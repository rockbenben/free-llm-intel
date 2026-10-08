"""全文语料库（article bodies + bilingual storage）的独立模块。

与 `crawler_llm_intel` 解耦：本模块**不 import** 主爬取器（避免循环），
所有外部依赖（HTTP 抓取 `fetch(url) -> (html, ok, status, final_url)`、
LLM 翻译 `call_llm(prompt) -> str`）由调用方注入。CI 只走「增量、requests-only」，
本地回充可用 `--allow-browser` 兜底 SPA/反爬。

设计参见 docs/superpowers/specs/2026-10-05-fulltext-corpus-design.md。
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable, Iterable, Tuple
from urllib.parse import parse_qsl, unquote, urlencode, urljoin, urlsplit, urlunsplit

# ---------------------------------------------------------------------------
# URL 规范化与稳定 slug
# ---------------------------------------------------------------------------

# 只剥明确的营销/追踪参数；`ref` / `source` 常是合法链接来源，保留。
_TRACKING_PREFIXES = ("utm_", "mc_cid", "mc_eid")
_TRACKING_EXACT = {"fbclid", "gclid", "igshid"}


def _is_tracking(name: str) -> bool:
    n = name.lower()
    return n in _TRACKING_EXACT or any(n.startswith(p) for p in _TRACKING_PREFIXES)


def anchor_fragment(url: str) -> str:
    """URL 的 fragment（percent-decoded，空则空串）。

    单页变更日志的每条条目都是「同页不同 #锚点」（MiniMax 发布说明、Kimi 发布记录、
    poolside / inference.net 的博客卡片）。这类页面**抓回来的 HTML 永远是整页**，
    条目之间的区别只存在于 fragment 里 —— 所以 fragment 是条目身份的一部分。
    """
    return unquote(urlsplit(url.strip()).fragment).strip()


def normalize_url(url: str) -> str:
    """去 fragment、去已知跟踪参数、host 小写、剥路径尾斜杠（除根路径）。

    确定性：同一 URL 多次运行得同一形态，即便 fragment / utm 变。
    """
    parts = urlsplit(url.strip())
    host = parts.netloc.lower()
    path = parts.path
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/") or "/"
    pairs = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
             if not _is_tracking(k)]
    query = urlencode(pairs)
    return urlunsplit((parts.scheme.lower(), host, path or "/", query, ""))


def _identity_url(url: str) -> str:
    """条目的**身份** URL = `normalize_url` 的结果 + 原 fragment（小写）。

    与 `normalize_url` 的差别只体现在带 fragment 的 URL 上：无 fragment 的条目两者
    完全一致，slug 与既有语料文件一一对应，不会有任何迁移。
    """
    base = normalize_url(url)
    frag = anchor_fragment(url).lower()
    return base + "#" + frag if frag else base


def url_hash(url: str) -> str:
    """身份 URL 的 sha256 前 12 hex；用作文件名 slug（天然按 URL 去重）。

    **认 fragment**：否则单页变更日志上的 N 条条目会塌成同一个 slug、共用一份
    「整页」正文 —— 实测 MiniMax 发布说明 21 条条目 → 1 个文件，点开任一条看到的都是
    整页目录。
    """
    return hashlib.sha256(_identity_url(url).encode("utf-8")).hexdigest()[:12]


def bodies_key(vendor_id: str, url: str) -> str:
    """`bodies.json` 的键：厂商 + 身份 URL，tab 分隔。

    同样认 fragment —— 否则同页 N 条锚点条目共用一行 ledger，第二条会被判成
    「已有正文」直接跳过，正文也就永远只有整页那一份。
    """
    return f"{vendor_id}\t{_identity_url(url)}"


# ---------------------------------------------------------------------------
# frontmatter：扁平 key: value + 原子落盘（不引 PyYAML）
# ---------------------------------------------------------------------------

def write_body_doc(path: Path, fm: dict, body: str) -> None:
    """原子写「--- frontmatter --- 正文」。值原样存（允许含冒号），键顺序即传入顺序。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["---"]
    for k, v in fm.items():
        lines.append(f"{k}: {v}")
    lines += ["---", "", (body or "").rstrip("\n"), ""]
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def read_body_doc(path: Path) -> Tuple[dict, str]:
    """读回 (frontmatter dict, 正文)。缺 frontmatter 抛 ValueError。"""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: 缺 frontmatter")
    _open, fm_block, rest = text.split("---\n", 2)
    fm: dict = {}
    for ln in fm_block.splitlines():
        if ":" in ln:
            k, v = ln.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, rest.strip("\n")


# ---------------------------------------------------------------------------
# 正文抽取：标准库 HTMLParser → 密度选主块 → Markdown（readability-v1）
# ---------------------------------------------------------------------------

# 自身不 import crawler，自带一份反爬/SPA 判定正则（判据同源、耦合为零）。
_BLOCKED_RE = re.compile(
    r"(you have been blocked|enable cookies|checking your browser|access denied|are you a robot)", re.I)
_PAYWALL_RE = re.compile(
    r"(subscribe to (read|continue)|members[\s-]?only|paywall|sign in to read|log in to read)", re.I)
_SPA_SHELL_RE = re.compile(r"<div[^>]*id=[\"']?(?:root|app|__next|main)[\"'][^>]*>\s*</div>", re.I)

_DROP_TAGS = {"script", "style", "nav", "header", "footer", "aside", "form",
              "noscript", "svg", "iframe", "button", "head", "title", "template"}
_BLOCK_TAGS = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "pre", "blockquote"}
_INLINE_MARK = {"strong", "b", "em", "i", "code", "a", "img", "br"}
_MIN_BODY_CHARS = 200
_HEADINGS = {"h1": "#", "h2": "##", "h3": "###", "h4": "####", "h5": "#####", "h6": "######"}


class _Node:
    __slots__ = ("tag", "attrs", "children", "skip")

    def __init__(self, tag, attrs=None, skip=False):
        self.tag = tag
        self.attrs = dict(attrs or {})
        self.children = []          # _Node | str
        self.skip = skip


class _TreeBuilder(HTMLParser):
    """宽松建树：void 标签不入栈；endtag 弹到最近同名；drop/嵌套子树标 skip。"""

    _VOID = {"img", "br", "hr", "meta", "link", "input", "area", "base", "col", "source"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = _Node("root")
        self.stack = [self.root]
        self.title_parts = []
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        skip = self.stack[-1].skip or tag in _DROP_TAGS
        node = _Node(tag, attrs, skip)
        if tag == "title":
            self._in_title = True
        if tag in self._VOID:
            self.stack[-1].children.append(node)
            return
        self.stack[-1].children.append(node)
        self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        node = _Node(tag, attrs, self.stack[-1].skip or tag in _DROP_TAGS)
        self.stack[-1].children.append(node)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in self._VOID:
            return
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if self._in_title:
            self.title_parts.append(data)
        if not self.stack[-1].skip and data:
            self.stack[-1].children.append(data)


def _text_of(node, include_skip=False) -> str:
    out = []
    for ch in node.children:
        if isinstance(ch, str):
            out.append(ch)
        elif include_skip or not ch.skip:
            out.append(_text_of(ch, include_skip))
    return "".join(out)


def _link_text_len(node) -> int:
    if node.tag == "a":
        return len(_text_of(node).strip())
    return sum(_link_text_len(c) for c in node.children if isinstance(c, _Node))


def _subtree_text_len(node) -> int:
    if node.skip:
        return 0
    if node.tag in _DROP_TAGS:
        return 0
    total = 0
    for ch in node.children:
        if isinstance(ch, str):
            total += len(ch.strip())
        elif not ch.skip and ch.tag not in _DROP_TAGS:
            total += _subtree_text_len(ch)
    return total


def _find_main(root) -> _Node:
    """优先最大的 <article>/<main>（不设字数门槛——空判定交给调用方）；否则取正文密度
    最高、非链接密集的块容器。"""
    articles = []

    def walk(n):
        for c in n.children:
            if isinstance(c, _Node) and not c.skip:
                if c.tag in ("article", "main"):
                    articles.append((_subtree_text_len(c), c))
                walk(c)
    walk(root)
    if articles:
        articles.sort(key=lambda x: x[0], reverse=True)
        return articles[0][1]
    # 退化：挑正文最长、非链接密集的 div/section（排除 body/root：整站文本必然最长，
    # 会连导航页脚一起吞掉；真正文块总在某个子 div 里）。
    best, best_score = root, 0
    pool = []

    def collect(n):
        for c in n.children:
            if isinstance(c, _Node) and not c.skip:
                if c.tag in ("div", "section"):
                    pool.append(c)
                collect(c)
    collect(root)
    for n in pool:
        t = _subtree_text_len(n)
        score = t - 2 * _link_text_len(n)      # 链接多 = 导航/列表页，降权
        if score > best_score:
            best, best_score = n, score
    return best


def _inline(node) -> str:
    parts = []
    for ch in node.children:
        if isinstance(ch, str):
            parts.append(re.sub(r"\s+", " ", ch))
            continue
        if ch.skip:
            continue
        inner = _inline(ch)
        if ch.tag in ("strong", "b"):
            parts.append(f"**{inner}**" if inner.strip() else inner)
        elif ch.tag in ("em", "i"):
            parts.append(f"*{inner}*" if inner.strip() else inner)
        elif ch.tag == "code":
            parts.append(f"`{inner}`" if inner.strip() else inner)
        elif ch.tag == "a":
            href = ch.attrs.get("href", "")
            parts.append(f"[{inner}]({href})" if inner.strip() else inner)
        elif ch.tag == "img":
            src = ch.attrs.get("src", "")
            alt = ch.attrs.get("alt", "")
            parts.append(f"![{alt}]({src})")
        elif ch.tag == "br":
            parts.append("\n")
        else:
            parts.append(inner)
    return "".join(parts)


def _table_to_md(tbl) -> str:
    """把 <table> 渲染为 Markdown 管道表（首行作表头；忽略 rowspan/colspan）。"""
    rows = []
    for tr in _iter_nodes(tbl):
        if tr.tag != "tr":
            continue
        cells = [_inline(td).strip().replace("\n", " ")
                 for td in tr.children
                 if isinstance(td, _Node) and td.tag in ("td", "th") and not td.skip]
        if cells:
            rows.append(cells)
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    esc = lambda c: c.replace("|", "\\|")
    lines = ["| " + " | ".join(esc(c) for c in rows[0]) + " |",
             "| " + " | ".join("---" for _ in rows[0]) + " |"]
    lines += ["| " + " | ".join(esc(c) for c in r) + " |" for r in rows[1:]]
    return "\n".join(lines)


def _blocks(node, out: list) -> None:
    for ch in node.children:
        if isinstance(ch, str):
            stripped = ch.strip()
            if stripped:
                out.append(stripped)
            continue
        if ch.skip or ch.tag in _DROP_TAGS:
            continue
        if ch.tag in _HEADINGS:
            txt = _inline(ch).strip()
            if txt:
                out.append(f"{_HEADINGS[ch.tag]} {txt}")
        elif ch.tag == "p":
            txt = _inline(ch).strip()
            if txt:
                out.append(txt)
        elif ch.tag == "table":
            tmd = _table_to_md(ch)
            if tmd:
                out.append(tmd)
        elif ch.tag in ("ul", "ol"):
            items = []
            for li in ch.children:
                if isinstance(li, _Node) and li.tag == "li":
                    t = _inline(li).strip()
                    if t:
                        items.append(f"- {t}")
            if items:
                out.append("\n".join(items))
        elif ch.tag == "blockquote":
            t = _text_of(ch).strip()
            if t:
                out.append("\n".join(f"> {ln}" for ln in t.splitlines()))
        elif ch.tag == "pre":
            t = _text_of(ch).strip("\n")
            if t.strip():
                out.append(f"```\n{t}\n```")
        elif ch.tag in ("div", "section", "article", "main", "figure", "span"):
            _blocks(ch, out)
        else:
            _blocks(ch, out)


def _extract_meta(root, tree) -> Tuple[str, str, str]:
    title = ""
    for n in _iter_nodes(root):
        if n.tag == "h1" and not n.skip:
            title = _text_of(n).strip()
            break
    if not title:
        title = "".join(tree.title_parts).strip()
    date = ""
    for n in _iter_nodes(root):
        if n.tag == "time" and n.attrs.get("datetime"):
            date = n.attrs["datetime"][:10]
            break
    byline = ""
    return title, byline, date


def _iter_nodes(node):
    for ch in node.children:
        if isinstance(ch, _Node):
            yield ch
            yield from _iter_nodes(ch)


def _absolutize(root, base_url: str) -> None:
    """把 a[href]/img[src] 按 base_url 绝对化（图片保留远程 URL，不下载）。"""
    for n in _iter_nodes(root):
        if n.tag == "a" and n.attrs.get("href"):
            n.attrs["href"] = urljoin(base_url, n.attrs["href"])
        elif n.tag == "img" and n.attrs.get("src"):
            n.attrs["src"] = urljoin(base_url, n.attrs["src"])


def extract_article_markdown(html: str, base_url: str) -> dict:
    """返回 {title, byline, date, markdown, reason}。reason="" 表示成功。"""
    html = html or ""
    tree = _TreeBuilder()
    try:
        tree.feed(html)
    except Exception:
        pass
    root = tree.root
    _absolutize(root, base_url)
    title, byline, date = _extract_meta(root, tree)

    def _fail(reason):
        return {"title": title, "byline": byline, "date": date, "markdown": "", "reason": reason}

    main = _find_main(root)
    blocks: list = []
    _blocks(main, blocks)
    markdown = "\n\n".join(blocks).strip()

    # 硬失败判定（抓不到不猜）：反爬 > 付费墙 > SPA 壳 > 正文过短
    if _BLOCKED_RE.search(html):
        return _fail("blocked")
    if _PAYWALL_RE.search(html) and len(markdown) < 400:
        return _fail("paywall")
    if len(markdown) < _MIN_BODY_CHARS:
        if _SPA_SHELL_RE.search(html):
            return _fail("scaffold")
        return _fail("empty")
    return {"title": title, "byline": byline, "date": date, "markdown": markdown, "reason": ""}


def status_for_reason(reason: str) -> str:
    if reason == "":
        return "ok"
    if reason == "paywall":
        return "paywall"
    return "fetch_failed"


# ---------------------------------------------------------------------------
# 源语言判定：中文原生页不该塞进 `.en.md` 等翻译（对齐 --backfill-orig 的中文原生跳过）
# ---------------------------------------------------------------------------

_CJK = re.compile(r"[\u4e00-\u9fff]")
_LATIN = re.compile(r"[A-Za-z]")
ZH_SOURCE_RATIO = 0.4   # 正文里 CJK 占比阈值（代码块/URL 已剔，模型名等拉丁词不致误判）


def _body_text_for_lang(md: str) -> str:
    """剔掉代码块与 URL，只留自然语言文本，再量 CJK/拉丁占比。"""
    t = re.sub(r"```.*?```", " ", md, flags=re.S)
    t = re.sub(r"https?://\S+", " ", t)
    return t


def detect_source_lang(md: str) -> str:
    """返回 'zh' 或 'en'：CJK/(CJK+拉丁) ≥ ZH_SOURCE_RATIO 判中文原生。"""
    t = _body_text_for_lang(md or "")
    cjk = len(_CJK.findall(t))
    latin = len(_LATIN.findall(t))
    if cjk + latin == 0:
        return "en"
    return "zh" if cjk / (cjk + latin) >= ZH_SOURCE_RATIO else "en"


# ---------------------------------------------------------------------------
# 链接目录页判定：poolside 那种「整页都是 - [标题+描述](url)」的 blog index
# 是厂商列表页不是文章；不应进语料，也不应占待译队列（用户 2026-10-05 定）。
# ---------------------------------------------------------------------------

_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_INDEX_LINK_RATIO = 0.7   # 链接文字的字符量 / 正文非空白字符量 ≥ 此值 = 目录页
_INDEX_MIN_BODY = 200


def detect_index_page(md: str) -> bool:
    """正文的「散文」几乎全在链接显示文字里、括号外没什么独立文字 → 判为目录页。

    度量：link 显示文字字符 / (link 显示文字 + 链接外剩余文字)。URL 不计入分母
    （整段 `[text](url)` 被剥掉，只剩 text 计为链接内）。阈值 0.7 取自 poolside
    首页（全是 `- [长描述](url)`，链接外≈空）与正常文章（散文在链接外）的实测余量。
    """
    body = (md or "").strip()
    if len(body) < _INDEX_MIN_BODY:
        return False
    link_chars = sum(len(re.sub(r"[\s\W]+", "", t, flags=re.UNICODE))
                     for t in _LINK_RE.findall(body))
    outside = _LINK_RE.sub("", body)
    outside_chars = len(re.sub(r"[\s\W]+", "", outside, flags=re.UNICODE))
    denom = link_chars + outside_chars
    if denom == 0:
        return False
    return link_chars / denom >= _INDEX_LINK_RATIO

# ---------------------------------------------------------------------------
# 单页变更日志：按 fragment 把「整页正文」切成「这一条的正文」
# ---------------------------------------------------------------------------

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
#: 标题里带**指向锚点的链接**的，视为「一条条目的开头」。
#: 注意目标可能是相对锚点（`[↩](#2026-年7-31-日)`），也可能是带锚点的**完整 URL**
#: （`[](https://x.cn/docs#2026-年-7-月-31-日)`，MiniMax 发布说明实测就是这种，
#: 因为它的回链用的是页面自身的绝对地址）—— 只认 `](#` 会漏掉后一种。
_BACKLINK_RE = re.compile(r"\]\([^)]*#")


#: 变更日志里「一条条目的开头」长这样：`## 2026 年 7 月 31 日`（MiniMax 发布说明）
#: 或 `## 2026年9月`（Kimi 发布记录），通常还带一个指回自身的回链。
#: **判据是日期型标题，不是「同级标题」** —— MiniMax 每条下面紧跟的 `## MiniMax H3`
#: 与日期标题同级，按同级切会把条目正文整段丢掉（实测切出 92 字符、只剩日期行）。
_DATE_HEADING_RE = re.compile(r"20\d{2}\s*[-/.年]\s*\d{1,2}(?:\s*[-/.月]\s*\d{1,2})?")


def _is_entry_heading(line: str) -> bool:
    """该标题是不是「下一条条目的开头」—— 日期型，或带回链。"""
    m = _HEADING_RE.match(line)
    if not m:
        return False
    text = m.group(2)
    return bool(_DATE_HEADING_RE.search(text) or _BACKLINK_RE.search(text))


def _anchor_key(s: str) -> str:
    """锚点的日期形态键：只留数字与 CJK 汉字。

    同一个锚点在 URL 与标题里是**两种写法**：MiniMax 发布说明的条目 URL 形如
    `#2026-年7-月31-日`（slug 规则多插了几个短横），而页面标题里的回链是
    `#2026-年7-31-日`。原样比对永远匹配不上，切片会静默退回整页 —— 实测就是
    「21 条条目共用一份整页正文」。归一到「数字 + 汉字」后两者收敛成同一个键。

    只对**日期型**锚点成立。英文 slug 过这里会退化成纯数字
    （`#python-sdk-v1.2.0-and-typescript-sdk-v1.1.2` → `120112`），互不相干的条目
    会撞成同一个键 —— 实测 groq 有 4 条因此共用同一段错切片。所以它只作兜底档。
    """
    return "".join(ch for ch in unquote(s or "")
                   if ch.isdigit() or "\u4e00" <= ch <= "\u9fff")


#: 锚点归一：空白与下划线变短横，其余非「字母数字 / 汉字」字符一律丢掉。
#: 厂商页面的条目锚点就是这么从标题生成的，比对两侧都先过这一步。
_SLUG_DROP_RE = re.compile(r"[^0-9a-z\u4e00-\u9fff-]")
_SLUG_DASH_RE = re.compile(r"-{2,}")


def _slug(s: str) -> str:
    """标题 → 锚点 slug：`GLM-5.2 now available on Workers AI` → `glm-52-now-available-on-workers-ai`。"""
    t = unquote(s or "").strip().lower()
    t = re.sub(r"[\s_]+", "-", t)
    t = _SLUG_DROP_RE.sub("", t)
    return _SLUG_DASH_RE.sub("-", t).strip("-")


#: 行内链接指向的锚点：相对形式 `](#frag)`，也含绝对地址 `](https://site/page#frag)`
#: （groq 的条目标题用前者，MiniMax / siliconflow 的自链接用后者）。
_ANCHOR_LINK_RE = re.compile(r"\]\((?:[^)#\s]*)#([^)\s]+)\)")
_LINK_TEXT_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
#: 代码栅栏的**标记行**（不含内容）。别名与下方剥译文包裹的 `_FENCE_RE` 区分开：
#: 两处同名会在 import 时静默互相覆盖，实测让「栅栏内不参与定位」从未生效。
_FENCE_MARK_RE = re.compile(r"^\s*(```|~~~)")


def _line_anchor_keys(line: str) -> tuple[set, set]:
    """这一行可匹配的锚点形态：(行内链接的 slug 集合, 行文本的 slug 集合)。"""
    frags = {_slug(f) for f in _ANCHOR_LINK_RE.findall(line)} - {""}
    text = _LINK_TEXT_RE.sub(r"\1", line)
    text = re.sub(r"^#{1,6}\s*", "", text).strip()
    return frags, ({_slug(text)} - {""})


def _visible_lines(lines: list[str]) -> list[bool]:
    """每行是否可见标记（代码栅栏内部不算）。

    groq 页面正文里有 ``` 代码块，块内的 `curl` 之类短行会被「独立短行」误认成
    条目标题，把收尾边界提前。
    """
    flags: list[bool] = []
    in_fence = False
    for line in lines:
        if _FENCE_MARK_RE.match(line):
            in_fence = not in_fence
            flags.append(False)
            continue
        flags.append(not in_fence)
    return flags


def _heading_level(line: str) -> int:
    m = _HEADING_RE.match(line)
    return len(m.group(1)) if m else 0


def _is_entry_start(lines: list[str], i: int, visible: list[bool] | None = None) -> bool:
    """这一行是不是一条条目的开头。两种形状都算：

    1. 标题行且是条目开头（判据见 `_is_entry_heading`）；
    2. **独立成行的短标题，且紧跟 bullet 清单** —— Cloudflare Workers AI changelog
       的条目没有自己的标题：`## 2026-06-16` 下面直接是
       `GLM-5.2 now available on Workers AI`，再跟该条改动清单。只认标题行时这类
       页面定位不到起点，21818 字符的整页被 14 条条目共用（实测）。

    第 2 条的三个附加约束都是被实测逼出来的，缺一个就会把**正文**认成条目标题，
    于是切片在第一条句子处提前收尾（实测 groq `Python SDK v0.30.0` 那条只剩 95
    字符的标题行，正文整段丢了）：
      * `visible`（代码栅栏外）—— 块内的 `curl` 之类短行不是标题；
      * 下一非空行必须是真正的 bullet（`- ` / `* ` 后带空格）——
        `**Key Changes:**` 这类粗体行不算；
      * 本行不能以句末标点收尾 —— 那是句子，不是标题。

    标题行（第 1 条）**不受 `visible` 约束**：栅栏的奇偶配对在真实页面上并不可靠
    （groq changelog 实测有位错的示例块），拿它屏蔽标题会让 20 条条目全部定位不到
    起点、集体退回整页。
    """
    line = lines[i]
    if _HEADING_RE.match(line):
        return _is_entry_heading(line)
    if visible is not None and not visible[i]:
        return False
    if not line.strip() or len(line) > 120:
        return False
    if line.lstrip()[:1] in "-*>|`#":
        return False
    if line.rstrip()[-1:] in (".", "。", "!", "！", "?", "？", ":", "：", ";", "；"):
        return False
    if i > 0 and lines[i - 1].strip():
        return False          # 紧贴上一行 → 是上一段的续行，不是新条目
    j = i + 1
    while j < len(lines) and not lines[j].strip():
        j += 1
    if j >= len(lines):
        return False
    return bool(re.match(r"^\s*[-*]\s+\S", lines[j]))


def _find_entry_start(lines: list[str], frag: str) -> int:
    """按「行内链接锚点精确 → 行文本精确 → 日期键相等」三档定位条目起点；无则 -1。

    分档而不混合打分：高优先档命中过的行不再参与低档，且低档要求**相等**而非
    包含 —— 否则 groq 那种 `v1.2.0 / v1.1.2` 的数字键会把不相干条目吸到一起
    （实测 4 条不同条目错共用 1283 字符）。同档多行命中取第一行：变更日志自上
    而下，页面顶部的目录链接会重复出现同一锚点，正文里那次才是条目本身。
    """
    tslug, tdate = _slug(frag), _anchor_key(frag)
    visible = _visible_lines(lines)
    for tier in ("link", "text", "date"):
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            if tier == "date":
                if tdate and tdate == _anchor_key(_LINK_TEXT_RE.sub(r"\1", line)):
                    if _is_entry_start(lines, i, visible):
                        return i
                continue
            frags, texts = _line_anchor_keys(line)
            if tslug in (frags if tier == "link" else texts) and _is_entry_start(lines, i, visible):
                return i
    return -1


#: 「同页第 N 条」的**合成锚点**：抽取时页面给不出可用链接，锚点按
#: `t<ISO日期>-<序号>`（腾讯混元）或 `d-<ISO日期>-<序号>`（siliconflow）生成。
#:
#: 不解析 `04-09-2025-2` 这类**月日顺序有歧义**的写法：Gemini 版本说明实测是美式
#: MM-DD-YYYY（该行 date 列是 2025-04-09，页面里的标题是「2025 年 4 月 9 日」），
#: 按 DD-MM 读会指到另一天。猜错日期就是切错正文，所以宁可不认。
_SYN_ISO_ORD = re.compile(r"^(?:t|d-)?(\d{4})-(\d{1,2})-(\d{1,2})-(\d+)$")
_TABLE_ONLY = set("|-: ")


def _syn_date_ordinal(frag: str):
    """合成锚点拆成 (ISO 日期, 序号)；不是 ISO 合成锚点返回 None。"""
    s = unquote(frag or "").strip()
    m = _SYN_ISO_ORD.match(s)
    if not m:
        return None
    y, mo, d, n = m.groups()
    return "%04d-%02d-%02d" % (int(y), int(mo), int(d)), int(n)


def _date_variants(iso: str) -> set:
    """同一日期在页面里可能的写法（ISO / 去零 / 中文年月日 / 点分）。"""
    y, mo, d = (int(x) for x in iso.split("-"))
    return {iso, f"{y}-{mo}-{d}", f"{y}年{mo}月{d}日", f"{y}年{mo:02d}月{d:02d}日",
            f"{y}.{mo:02d}.{d:02d}", f"{y}.{mo}.{d}"}


def _norm_text(s: str) -> str:
    return re.sub(r"[\W_]+", "", s or "", flags=re.UNICODE).lower()


def _plain_line_text(line: str) -> str:
    """一行的「纯字面」：脱掉链接壳、去标题井号（比对用，不用于输出）。"""
    text = _LINK_TEXT_RE.sub(r"\1", line)
    return re.sub(r"^#{1,6}\s*", "", text).strip()


def _slice_by_sibling_titles(md: str, title: str, siblings) -> str:
    """起点和终点都只认「这一页自己的那些条目标题」，切出 `title` 那一条。

    整页变更日志里，条目行常常**不是标题语法**：智谱更新日志实测条目名就是一行普通
    文本，下面紧跟 emoji 与型号行，`_is_entry_start` 认不出开头，三种判据全落空，
    于是 21 条条目共用一份整页正文。这里不再猜「哪行像标题」，改用索引里同一页的
    其余条目标题当分界 —— 分界由页面自己认领（那行确实是另一条的标题）。

    命中 0 行或 >1 行、切完只剩标题本身，一律返回空串交给调用方维持现状。
    """
    t = _norm_text(title)
    if len(t) < 4:
        return ""
    lines = md.splitlines()
    starts = [i for i, l in enumerate(lines) if _norm_text(_plain_line_text(l)) == t]
    if len(starts) != 1:
        return ""
    i0 = starts[0]
    others = {_norm_text(s) for s in (siblings or ()) if s} - {t, ""}
    end = len(lines)
    for j in range(i0 + 1, len(lines)):
        key = _norm_text(_plain_line_text(lines[j]))
        if key and key in others:
            end = j
            break
    section = "\n".join(lines[i0:end]).strip()
    if _norm_text(section) == t or len(section) <= len(_plain_line_text(lines[i0])):
        return ""             # 只有标题一行 = 切不出「这一条」
    return section


def _slice_dated_table(md: str, frag: str, title: str):
    """条目是**表格里的一行**时的定位：日期筛出候选行，标题必须选中唯一一行。

    腾讯混元更新日志实测：`## 2025年12月` 小节下面是一张四列表（动态名称 / 动态描述 /
    发布时间 / 相关文档），一条更新就是其中一行 —— 页面上没有任何标题与锚点对得上，
    前三种判据（行内锚点、行文本 slug、汉字日期键）全部落空，80 行因此只有整页可读。

    标题当闸门而不是当线索：选不中、或同日期几行都含该标题（实测 4 行近义重复）时
    **一律不切**，宁缺不错。返回 None 表示交给调用方维持现状。
    """
    got = _syn_date_ordinal(frag)
    if not got:
        return None
    iso, _ordinal = got
    lines = md.splitlines()
    variants = _date_variants(iso)
    cand = [i for i, l in enumerate(lines)
            if l.strip().startswith("|") and not set(l.strip()) <= _TABLE_ONLY
            and any(v in l for v in variants)]
    if not cand:
        return None
    nt = _norm_text(title)
    sel = []
    if nt:
        for i in cand:
            for cell in [c.strip() for c in lines[i].strip().strip("|").split("|")][:2]:
                nc = _norm_text(cell)
                if nc and (nc in nt or nt in nc):
                    sel.append(i)
                    break
        if len(sel) != 1:
            return None            # 0 个或仍多选中：不给错正文
    elif len(cand) != 1:
        return None
    row = sel[0] if sel else cand[0]
    # 所属表格的表头（列名 + 分隔行）：从该行往上走到表格块的开头
    top = row
    while top - 1 >= 0 and lines[top - 1].strip().startswith("|"):
        top -= 1
    header = lines[top:top + 2] if row - top >= 2 else []
    # 所属小节标题：往上第一个标题行
    sec = ""
    for k in range(top - 1, -1, -1):
        if _HEADING_RE.match(lines[k]):
            sec = lines[k]
            break
    parts = [p for p in (sec, "\n".join(header), lines[row]) if p]
    out = "\n\n".join(parts).strip()
    return out if len(out) >= 80 else None


#: 条目之间的收尾噪声：分隔线，以及**下一条**头顶的裸日期标签
#: （groq changelog 实测 13 条切片结尾挂着 `---` + `Oct 29, 2025`，读者会以为
#: 这条自己就是那个日期）。日期标签只在它后面紧跟边界时才削，正文一律不动。
_TAIL_SEP_RE = re.compile(r"^\s*(?:---+|\*\*\*+|___+)\s*$")
_TAIL_DATE_RE = re.compile(r"^\s*(?:[A-Z][a-z]{2} \d{1,2}(?:, \d{4})?"
                           r"|\d{4}[-/.]\d{1,2}(?:[-/.]\d{1,2})?)\s*$")


def _trim_entry_tail(lines: list[str], end: int) -> int:
    """回退 `end`，剥掉切片尾部的分隔线与紧随其前的裸日期标签。"""
    i = end
    while i - 1 > 0 and (not lines[i - 1].strip() or _TAIL_SEP_RE.match(lines[i - 1])):
        i -= 1
    if i - 1 > 0 and _TAIL_DATE_RE.match(lines[i - 1]):
        j = i - 1
        while j - 1 > 0 and not lines[j - 1].strip():
            j -= 1
        # 日期标签上面就是本条正文（不是另一条标题）→ 它是下一条的抬头，削掉
        if j - 1 > 0 and not _HEADING_RE.match(lines[j - 1]):
            i = j
    return i


def _slice_anchor_section(md: str, frag: str, title: str = "", siblings=()) -> str:
    """从整页 markdown 里切出 `frag` 锚点那一条的段落；找不到就原样返回整页。

    起点 = `_find_entry_start`（标题行，或 Cloudflare 那种独立成行的条目标题）。
    三种形状都定位不到时，再试 `_slice_dated_table`：条目其实是**表格里的一行**
    （腾讯混元更新日志），靠合成锚点里的日期筛行、用 `title` 选中唯一一行。
    表格也选不中时最后试 `_slice_by_sibling_titles`：分界用 `siblings`（同一页其余
    条目的标题）认，不猜「哪行像标题」。
    终点 = 其后第一个**同级或更浅的条目起点**；起点是非标题行时，任意条目起点都能收尾。
    标题型起点还要求那个标题是「条目开头」，判据见 `_is_entry_heading`（日期型标题或带锚点链接），
    **不是单纯「下一个同级标题」**：MiniMax 每条下面紧跟的 `## MiniMax H3` 与日期标题同级，
    按同级切会把条目正文整段丢掉（实测只剩 92 字符的日期行）。

    切不到 / 切出来太短都退回整页：宁可给多也不给空 —— 空正文会被 `detect_index_page`
    判掉、正文直接留空，读者那边就变成「点开什么都没有」。
    """
    if not frag and not title:
        return md
    lines = md.splitlines()
    start = _find_entry_start(lines, frag)
    if start < 0:
        table_slice = _slice_dated_table(md, frag, title)
        if table_slice:
            return table_slice
        # 表格也选不中：最后用「同页其他条目标题」当分界试一次（智谱那种条目行不是标题语法）
        return _slice_by_sibling_titles(md, title, siblings) or md
    level = _heading_level(lines[start]) or 99   # 非标题起点：任何条目起点都算边界
    end = len(lines)
    visible = _visible_lines(lines)
    for j in range(start + 1, len(lines)):
        if _heading_level(lines[j]) > level:
            continue     # 更深的标题是本条内部结构
        if _is_entry_start(lines, j, visible):
            end = _trim_entry_tail(lines, j)
            break
    section = "\n".join(lines[start:end]).strip()
    # 切片后太短说明锚点只定位到一个空标题，退回整页（宁可给多也不给空）
    return section if len(section) >= 80 else md.strip()

_ENTRY_FIELDS = ("slug", "en_path", "zh_path", "en_status", "zh_status",
                 "translator", "title", "date", "captured", "body_sha", "src_lang")


def iter_article_rows(articles_json_path: Path) -> list:
    """读 `docs/feeds/articles.json` 的行数组 → [{vendor,url,title,date,original_title}]。"""
    if not articles_json_path.exists():
        return []
    d = json.loads(articles_json_path.read_text(encoding="utf-8"))
    fields = d.get("fields", [])
    if "url" not in fields or "vendor" not in fields:
        return []
    idx = {name: fields.index(name) for name in fields}

    def get(row, name, default=""):
        i = idx.get(name)
        return row[i] if i is not None and i < len(row) else default
    return [{"vendor": get(r, "vendor"), "url": get(r, "url"), "title": get(r, "title"),
             "date": get(r, "date"), "original_title": get(r, "original_title")}
            for r in d.get("articles", [])]


def load_bodies(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8")).get("bodies", {})


def save_bodies(path: Path, bodies: dict) -> None:
    """确定性序列化：不含构建时间戳，key 排序，缩进 2，LF，原子写。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"count": len(bodies),
               "bodies": {k: {f: bodies[k].get(f, "") for f in _ENTRY_FIELDS} for k in sorted(bodies)}}
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def validate_bodies(root: Path, bodies: dict) -> list:
    """§3.4 不变量：违规描述列表（空=合规）。"""
    errs = []
    for key, e in bodies.items():
        en, zh = e.get("en_status"), e.get("zh_status")
        enp = root / e.get("en_path", "")
        if en == "ok":
            if not e.get("en_path") or not enp.exists():
                errs.append(f"{key}: en_status=ok 但缺正文文件 {e.get('en_path')!r}")
            else:
                _fm, body = read_body_doc(enp)
                if not body.strip():
                    errs.append(f"{key}: en_status=ok 但正文为空")
        elif en in ("fetch_failed", "paywall", "index_page"):
            if e.get("en_path") and enp.exists():
                _fm, body = read_body_doc(enp)
                if body.strip():
                    errs.append(f"{key}: {en} 条目正文非空（疑似编造）")
        if zh == "translated":
            if not e.get("zh_path") or not (root / e.get("zh_path", "")).exists():
                errs.append(f"{key}: zh=translated 但缺 {e.get('zh_path')!r}")
    return errs


def fetch_bodies(root: Path, rows: list, bodies: dict, *, fetch: Callable,
                 today: str, only_missing: bool = True, retry_unreadable: bool = False,
                 save: Callable[[dict], None] | None = None, flush_every: int = 20) -> int:
    """逐行抓正文写 `.en.md` 并 upsert `bodies`。`fetch(url)->(html,ok,status,final)` 注入。

    返回本轮新写/更新的条数。幂等：`only_missing` 时已 `en_status=ok` 的行跳过。
    `retry_unreadable=True` 时连已标 `index_page` 的行也重抓（判定可能被源站改版
    推翻）；已有真实中文译文（`zh_status=translated`）的行**始终**跳过，重抓不许
    把精译冲掉。`fetch_failed` / `paywall` 本来就每天重试，与本旗标无关。
    抓不到 → `fetch_failed`，正文留空，绝不编造。给定 `save` 时每 `flush_every` 篇
    增量落盘一次（长批被中断也不丢进度；末尾再落一次由调用方负责）。
    """
    # 同一基页（去掉 fragment）的其他条目标题：单页变更日志切片时的分界素材。
    siblings_by_base: dict = {}
    for r in rows:
        u, v = r.get("url"), r.get("vendor")
        t = (r.get("title") or "").strip()
        if not u or not v or not t:
            continue
        siblings_by_base.setdefault((v, u.split("#", 1)[0]), []).append(t)
    written = 0
    for r in rows:
        url = r.get("url")
        vendor = r.get("vendor")
        if not url or not vendor:
            continue
        key = bodies_key(vendor, url)
        prev = bodies.get(key, {})
        if only_missing:
            done = (prev.get("en_status") == "ok"
                    or prev.get("zh_status") == "translated")
            # `index_page` 是**判定**而不是事实：标了就没人再看一眼，源站改版或
            # 当初判错都翻不回来。`fetch_failed` / `paywall` 一向每天重试，不变。
            if not retry_unreadable:
                done = done or prev.get("en_status") == "index_page"
            if done:
                continue
        html, ok, _status, final = fetch(url)
        ex = extract_article_markdown(html or "", final or url)
        en_status = "ok" if ex["reason"] == "" and ok else status_for_reason(ex["reason"] or "empty")
        # 单页变更日志（MiniMax 发布说明、Kimi 发布记录）：抓回来的永远是**整页**，
        # 按 fragment 切成「这一条」的段落。顺序不能换 —— 必须先切片再判目录页：
        # 整页本身就是个目录，先判会把其中 N 条真条目统统判成 index_page、正文留空
        # （实测 MiniMax 发布说明 21 条条目因此共用一份整页正文）。
        frag = anchor_fragment(url)
        if en_status == "ok" and frag:
            sliced = _slice_anchor_section(
                ex["markdown"], frag, r.get("title") or "",
                siblings_by_base.get((vendor, url.split("#", 1)[0]), ()))
            if len(sliced) < len(ex["markdown"]):
                ex["markdown"] = sliced
                # 整页的 <title> 是页面级的（「模型发布 - MiniMax 开放平台文档中心」），
                # 切片后用它会让每篇正文都顶着同一个标题；条目自己的标题在索引里。
                ex["title"] = r.get("title") or ex["title"]
        # 链接目录页（blog index / 聚合列表）不是文章：置 index_page、正文留空、不入待译
        if en_status == "ok" and detect_index_page(ex["markdown"]):
            en_status = "index_page"
        slug = url_hash(url)
        date = today
        norm = normalize_url(url)
        if en_status == "ok" and detect_source_lang(ex["markdown"]) == "zh":
            # 中文原生：正文即译文，直接落 `.md`，不留英文侧
            zh_rel = f"docs/articles/{vendor}/{slug}.md"
            fm = {"vendor": vendor, "title": ex["title"] or r.get("title", ""),
                  "original_title": "", "url": norm, "date": ex["date"] or r.get("date", ""),
                  "lang": "zh", "captured": date, "extractor": "readability-v1",
                  "translator": "native", "status": "translated",
                  "body_sha": hashlib.sha256(ex["markdown"].encode("utf-8")).hexdigest()[:12]}
            write_body_doc(root / zh_rel, fm, ex["markdown"])
            stale_en = f"docs/articles/{vendor}/{slug}.en.md"
            if prev.get("en_path") and (root / prev["en_path"]).exists():
                (root / prev["en_path"]).unlink()
            bodies[key] = {"slug": slug, "en_path": "", "en_status": "", "zh_path": zh_rel,
                           "zh_status": "translated", "translator": "native",
                           "title": r.get("title", ""), "date": r.get("date", ""),
                           "captured": date, "body_sha": fm["body_sha"], "src_lang": "zh"}
            written += 1
            if save is not None and written % flush_every == 0:
                save(bodies)
            continue
        # 英文原文 / 抓取失败：写英文侧，保留已有的真实中文译文
        en_rel = f"docs/articles/{vendor}/{slug}.en.md"
        body = ex["markdown"] if en_status == "ok" else ""
        fm = {"vendor": vendor, "title": ex["title"] or r.get("original_title") or r.get("title", ""),
              "original_title": r.get("original_title", ""), "url": norm,
              "date": ex["date"] or r.get("date", ""), "lang": "en", "captured": date,
              "extractor": "readability-v1", "status": en_status,
              "body_sha": hashlib.sha256(body.encode("utf-8")).hexdigest()[:12]}
        write_body_doc(root / en_rel, fm, body)
        bodies[key] = {"slug": slug, "en_path": en_rel, "en_status": en_status,
                       "zh_path": prev.get("zh_path", ""), "zh_status": prev.get("zh_status", ""),
                       "translator": prev.get("translator", ""),
                       "title": r.get("title", ""), "date": r.get("date", ""),
                       "captured": date, "body_sha": fm["body_sha"], "src_lang": "en"}
        written += 1
        if save is not None and written % flush_every == 0:
            save(bodies)
    return written


def reclassify_bodies(root: Path, bodies: dict) -> int:
    """一次性、幂等地把已缓存的 `.en.md` 按真实语言重判：中文原生的移到 `.md`（native）
    并删掉误存的 `.en.md`；英文的补 `src_lang=en`。复用磁盘正文，不重新抓取。返回改动数。"""
    changed = 0
    for key, e in list(bodies.items()):
        if e.get("en_status") != "ok" or not e.get("en_path"):
            continue
        enp = root / e["en_path"]
        if not enp.exists():
            continue
        fm, body = read_body_doc(enp)
        if detect_index_page(body):
            # 链接目录页：清空正文、标 index_page、退出待译
            nfm = dict(fm); nfm["status"] = "index_page"
            nfm["body_sha"] = hashlib.sha256(b"").hexdigest()[:12]
            write_body_doc(enp, nfm, "")
            e.update({"en_status": "index_page", "src_lang": ""})
            changed += 1
            continue
        if detect_source_lang(body) != "zh":
            if e.get("src_lang") != "en":
                e["src_lang"] = "en"
                changed += 1
            continue
        slug = e["slug"]
        vendor = key.split("\t", 1)[0]
        zh_rel = f"docs/articles/{vendor}/{slug}.md"
        nfm = {"vendor": vendor, "title": fm.get("title", ""), "original_title": "",
               "url": fm.get("url", ""), "date": fm.get("date", ""), "lang": "zh",
               "captured": fm.get("captured", ""), "extractor": fm.get("extractor", "readability-v1"),
               "translator": "native", "status": "translated",
               "body_sha": hashlib.sha256(body.encode("utf-8")).hexdigest()[:12]}
        write_body_doc(root / zh_rel, nfm, body)
        enp.unlink()
        e.update({"en_path": "", "en_status": "", "zh_path": zh_rel,
                  "zh_status": "translated", "translator": "native", "src_lang": "zh"})
        changed += 1
    return changed


def pending_translation_keys(bodies: dict) -> list:
    """需翻译的 ledger 键：英文 ok 且尚未 translated。"""
    return [k for k, e in bodies.items()
            if e.get("en_status") == "ok" and e.get("zh_status") != "translated"]


def reconcile_translations(root: Path, bodies: dict) -> int:
    """从磁盘吸收译文：某英文源若已有非空 `<slug>.md`，就把 ledger 标 translated。

    用于「子代理只写 .md、控制者单点写 ledger」的并发安全收口（避免多进程抢
    bodies.json）。translator 取该 .md frontmatter 里的值（缺省 agent）。
    """
    n = 0
    for key, e in bodies.items():
        if e.get("en_status") != "ok" or e.get("zh_status") == "translated":
            continue
        rel = f"docs/articles/{key.split(chr(9))[0]}/{e['slug']}.md"
        p = root / rel
        if not p.exists():
            continue
        try:
            fm, body = read_body_doc(p)
        except (ValueError, OSError):
            continue
        if body.strip():
            e["zh_path"] = rel
            e["zh_status"] = "translated"
            e["translator"] = fm.get("translator", "agent")
            n += 1
    return n


def mark_translated(root: Path, bodies: dict, *, key: str, zh_body_md: str,
                    translator: str, today: str) -> None:
    """把已译好的中文正文落 `.md` 并更新 ledger（不含任何翻译逻辑）。"""
    e = bodies[key]
    vendor = key.split("\t", 1)[0]
    rel = f"docs/articles/{vendor}/{e['slug']}.md"
    fm = {"vendor": vendor, "title": e.get("title", ""), "original_title": e.get("original_title", ""),
          "url": key.split("\t", 1)[1], "date": e.get("date", ""), "lang": "zh", "captured": today,
          "extractor": "readability-v1", "translator": translator, "status": "translated",
          "body_sha": hashlib.sha256(zh_body_md.encode("utf-8")).hexdigest()[:12]}
    write_body_doc(root / rel, fm, zh_body_md)
    e["zh_path"] = rel
    e["zh_status"] = "translated"
    e["translator"] = translator


# ---------------------------------------------------------------------------
# CI 增量翻译（--ai-bodies）：pending 英文正文 → LLM 中文 → .md（translator=llm）
# ---------------------------------------------------------------------------

#: 单篇英文正文送进翻译的最大字符数。超了直接留 pending、不译半篇（spec §10：
#: 「设单篇字数上限+截断留 pending，不产半成品」）。取值让中文输出稳落在
#: ai_review.BODY_MAX_TOKENS 之内——宁可漏译长文（本地 agent 补），不可产残篇。
BODY_TRANSLATE_CHAR_CAP = 12_000

_FENCE_RE = re.compile(r"^\s*```(?:markdown|md|text)?\s*\n([\s\S]*?)\n```\s*$")
_LABEL_RE = re.compile(r"^\s*(译文|翻译|中文翻译|正文)\s*[:：]\s*")


def _clean_llm_translation(text: str) -> str:
    """剥掉模型偶发的整体 ``` 包裹与「译文：」前缀标签，拿到纯 markdown 正文。"""
    t = (text or "").strip()
    m = _FENCE_RE.match(t)
    if m:
        t = m.group(1).strip()
    t = _LABEL_RE.sub("", t, count=1).strip()
    return t


def _translation_acceptable(en_body: str, zh: str) -> bool:
    """内容从严：非空、确为中文、不是原样照抄、长度不像拒答/截断。

    长度下限取「绝对 8 字」与「输入 15%」的较大者：8 字挡掉「无法翻译」这类
    一词拒答；15% 比例挡掉被 max_tokens 截断的残篇（中文比英文紧凑，正常译文
    远在 15% 之上）。宁可留 pending 让本地 agent 补，也不写进半篇。
    """
    if not zh:
        return False
    if zh.strip() == en_body.strip():
        return False                      # 没翻，原样吐回来
    if not _CJK.search(zh):
        return False
    if detect_source_lang(zh) != "zh":    # CJK 占比不足 = 多半是失败/夹生输出
        return False
    if len(zh) < max(8, int(len(en_body) * 0.15)):
        return False
    return True


def translate_bodies_llm(root: Path, bodies: dict, translate: Callable, *,
                         today: str, limit: int = 0, save: Callable = None,
                         flush_every: int = 10,
                         char_cap: int = BODY_TRANSLATE_CHAR_CAP,
                         translator: str = "llm",
                         stats: dict = None) -> int:
    """把待译英文正文逐篇交 `translate(title, en_body)->中文markdown`，落 `.md`。

    幂等：只动 `pending_translation_keys`（英文 ok 且未 translated）；已译的绝不重译。
    有界：`limit`（>0）封顶本次最多译几篇，控 CI 成本；`char_cap` 挡超长篇（留 pending）。
    不产半成品：正文取不到 / 超长 / 调用抛错 / 输出校验不过，一律留 pending，绝不写残篇。
    给定 `save` 时每 `flush_every` 篇落一次 ledger（中断也保住已完成项）。返回本轮新译篇数。

    `stats`（传入一个 dict 即被填充）记录每篇的归类，专治「批量译了 0 篇却看不出为什么」：
    translated / over_cap / no_en / errored 计数 + errors 前几条异常样本（含类型名）。
    """
    keys = pending_translation_keys(bodies)
    done = 0
    attempted = 0
    st = stats
    if st is not None:
        st.update({"considered": len(keys), "translated": 0, "over_cap": 0,
                   "no_en": 0, "rejected": 0, "errored": 0, "deferred": 0, "errors": []})
    for key in keys:
        e = bodies[key]
        en_path = root / e.get("en_path", "")
        if not e.get("en_path") or not en_path.exists():
            if st is not None:
                st["no_en"] += 1
            continue
        try:
            en_fm, en_body = read_body_doc(en_path)
        except (ValueError, OSError):
            if st is not None:
                st["no_en"] += 1
            continue
        if not en_body.strip():
            if st is not None:
                st["no_en"] += 1
            continue
        if len(en_body) > char_cap:       # 超长：留 pending，交本地 agent，不译半篇
            if st is not None:
                st["over_cap"] += 1
            continue                      # 不占调用预算（没真发一次翻译）
        if limit and limit > 0 and attempted >= limit:
            if st is not None:
                st["deferred"] += 1        # 够短但本轮预算已用尽，下次再译
            continue
        attempted += 1                     # limit 封顶的是「实际调用次数」，不是扫描条数
        title = en_fm.get("title") or e.get("title", "")
        try:
            zh = _clean_llm_translation(translate(title, en_body))
        except Exception as exc:           # 网络/额度/异常：留 pending，下次再试
            if st is not None:
                st["errored"] += 1
                if len(st["errors"]) < 3:
                    st["errors"].append(f"{type(exc).__name__}: {str(exc)[:180]}")
            continue
        if not _translation_acceptable(en_body, zh):
            if st is not None:
                st["rejected"] += 1
            continue                       # 校验不过：宁缺毋残
        mark_translated(root, bodies, key=key, zh_body_md=zh, translator=translator,
                        today=today)
        done += 1
        if st is not None:
            st["translated"] += 1
        if save is not None and done % flush_every == 0:
            save(bodies)
    return done
