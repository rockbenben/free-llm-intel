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
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

# ---------------------------------------------------------------------------
# URL 规范化与稳定 slug
# ---------------------------------------------------------------------------

# 只剥明确的营销/追踪参数；`ref` / `source` 常是合法链接来源，保留。
_TRACKING_PREFIXES = ("utm_", "mc_cid", "mc_eid")
_TRACKING_EXACT = {"fbclid", "gclid", "igshid"}


def _is_tracking(name: str) -> bool:
    n = name.lower()
    return n in _TRACKING_EXACT or any(n.startswith(p) for p in _TRACKING_PREFIXES)


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


def url_hash(url: str) -> str:
    """规范化 URL 的 sha256 前 12 hex；用作文件名 slug（天然按 URL 去重）。"""
    return hashlib.sha256(normalize_url(url).encode("utf-8")).hexdigest()[:12]


def bodies_key(vendor_id: str, url: str) -> str:
    """`bodies.json` 的键：厂商 + 规范化 URL，tab 分隔。"""
    return f"{vendor_id}\t{normalize_url(url)}"


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
                 today: str, only_missing: bool = True,
                 save: Callable[[dict], None] | None = None, flush_every: int = 20) -> int:
    """逐行抓正文写 `.en.md` 并 upsert `bodies`。`fetch(url)->(html,ok,status,final)` 注入。

    返回本轮新写/更新的条数。幂等：`only_missing` 时已 `en_status=ok` 的行跳过。
    抓不到 → `fetch_failed`，正文留空，绝不编造。给定 `save` 时每 `flush_every` 篇
    增量落盘一次（长批被中断也不丢进度；末尾再落一次由调用方负责）。
    """
    written = 0
    for r in rows:
        url = r.get("url")
        vendor = r.get("vendor")
        if not url or not vendor:
            continue
        key = bodies_key(vendor, url)
        prev = bodies.get(key, {})
        if only_missing and (prev.get("en_status") in ("ok", "index_page")
                             or prev.get("zh_status") == "translated"):
            continue
        html, ok, _status, final = fetch(url)
        ex = extract_article_markdown(html or "", final or url)
        en_status = "ok" if ex["reason"] == "" and ok else status_for_reason(ex["reason"] or "empty")
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
