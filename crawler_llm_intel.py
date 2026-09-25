#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
crawler_llm_intel.py — LLM 厂商免费额度 / 活动情报巡检脚本

功能：
  1. 读取并解析项目根目录下的 llm-intel.yaml（yaml.safe_load，只读不写）。
  2. 按 vendor_id 分组巡检 sources：
     - pricing / free_quota / token_plan / free_model / activities 等「情报页」：
       抓取页面文本，按关键词组提取「长期免费 / 注册赠送 / 包月订阅 / 限时活动 /
       限制条件」等证据片段（只摘录页面原文，不做主观推断、不编造使用建议）。
     - rate_limits / billing 等「条件页」：用于补充限制条件证据。
     - blog / engineering / news / updates / v4_news / research 等「动态页」：
       不写入 README，改为单独输出到 llm-news-feeds.md（每家最新若干篇），并把全量
       文章归档到 llm-news/<vendor>.md；同时尝试发现页面中的 RSS / Atom 订阅源，
       汇总生成 llm-news-feeds.opml（可导入 RSS 阅读器）。
     - product 等产品页：仅用于确认产品线，默认不深度抓取。
  3. 巡检结果写入 README.md 的固定章节（标记注释之间，重跑自动重写，不累计）。
     动态类产物由归档再生：docs/feeds/ 下的 RSS XML 与三个 JSON 索引
     （vendors / articles / model-releases，即模型发布雷达）；
     AI 核查采纳的事实变化追加进 llm-intel-changelog.md。

运行：
    python crawler_llm_intel.py                 # 完整巡检并刷新 README + 动态订阅文件
    python crawler_llm_intel.py --only deepseek # 只巡检指定 vendor_id（调试用，不覆盖全局文档）
    python crawler_llm_intel.py --no-news       # 跳过博客/RSS 发现，只刷新 README
    python crawler_llm_intel.py --no-browser    # 禁用浏览器兜底，纯 requests 抓取
    python crawler_llm_intel.py --ai-review     # 变化时调用 AI 自动核查并更新 profile_overrides.json
    python crawler_llm_intel.py --ai-titles     # 新收录文章的机翻标题交 LLM 润色一次（结果进归档即冻结）
    python crawler_llm_intel.py --rebuild-only  # 不触网，从 llm-news/ 归档等磁盘产物重建动态类产物
    python crawler_llm_intel.py --backfill-dates # 维护模式：逐篇文章页取元数据，回填归档缺失的发布日期

依赖：requests、PyYAML（HTML 解析使用标准库 html.parser，无需 bs4）。
可选：playwright（pip install playwright）。安装后对 403 反爬 / JS 动态渲染页面
自动用真实浏览器兜底渲染；Windows/macOS 直接复用系统 Edge/Chrome，无需额外下载。
"""

from __future__ import annotations

import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor
import html as html_mod
import re
import sys
import time
import xml.etree.ElementTree as ET
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from email.utils import format_datetime, parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import quote, unquote, urljoin, urlparse

import requests
import yaml

# Playwright 为可选依赖：安装后可对 403 / JS 动态渲染页面用真实浏览器兜底
#   pip install playwright
# Windows/macOS 可直接复用系统 Edge/Chrome（channel=msedge/chrome），无需下载 Chromium；
# 其他环境执行 `playwright install chromium` 即可。
try:
    from playwright.sync_api import sync_playwright  # type: ignore
    HAS_PLAYWRIGHT = True
except Exception:  # pragma: no cover - 未安装时降级为纯 requests
    sync_playwright = None  # type: ignore
    HAS_PLAYWRIGHT = False

# ---------------------------------------------------------------------------
# 常量配置
# ---------------------------------------------------------------------------

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
)

# 浏览器渲染后仍判定为「被反爬拦截」的页面特征
BLOCK_MARKERS = re.compile(
    r"(you have been blocked|enable cookies|checking your browser|"
    r"attention required|cf-error|access denied|please enable js|"
    r"verify you are human|未启用 ?javascript|请开启 ?javascript)",
    re.I,
)

# SPA 单页外壳标记：正文靠客户端渲染。两种形态——
#   ① 挂载点 div 为空（`<div id="root"></div>`，允许夹杂 noscript/script）；
#   ② 挂载 id 挂在 <html> 上（build.nvidia.com 的 `<html id="app">`）。
# 曾经只匹配 `id="root"` 字样就算外壳，把完全服务端渲染的 CJK 页面误伤
#（trae.cn 定价页正文齐全但中文密集，可见文本仅约 1.5k 字）。挂载点里有
# 服务端渲染内容的，不是外壳。
_SPA_ID = r"""id\s*=\s*["'](?:root|__next|__nuxt|app|app-root|appRoot|react-root)["']"""
SPA_EMPTY_MOUNT = re.compile(
    r"""<div[^>]*""" + _SPA_ID + r"""[^>]*>(?:\s|<noscript>[\s\S]*?</noscript>|<script[\s\S]*?</script>)*</div\s*>""",
    re.I,
)
SPA_HTML_MOUNT = re.compile(r"""<html[^>]*""" + _SPA_ID, re.I)

# 明确的登录认证跳转页（未登录时直接重定向至登录认证页）
LOGIN_PATTERNS = re.compile(
    r"(passport\.|/login\?|/signin\?|/auth/login|cloud\.tencent\.com/login|"
    r"i\.360\.cn/login|auth\.mistral\.ai|accounts\.google\.com)",
    re.I,
)

# 「免费额度 / 活动情报」页：深度抓取并提取证据
INTEL_TYPES = {
    "pricing", "free_quota", "token_plan", "activities", "free_model",
    "license", "free_tier", "trial", "price",
    # 邀请返利与学生扶持是独立情报维度（参考 FreeLLM-API-KeyHub 的
    # 「邀请/拉新奖励」「学生福利」两列）：必须给出官方活动页 URL，否则巡检无从复核
    "referral", "student_program",
}
# 「限制条件」页：速率 / 计费规则，作为条件证据补充
CONDITION_TYPES = {
    "rate_limits", "billing", "billing_rules", "billing_docs",
    "workers_pricing", "serverless_pricing", "tokenhub",
}
# 「博客 / 动态」页：不进 README，单独输出并发现 RSS
NEWS_TYPES = {
    "blog", "engineering", "news", "updates", "v4_news", "research", "changelog",
    "feed",
}
# 产品页及其他入口：不深度抓取
SKIP_TYPES = {"product"}

TYPE_LABELS = {
    "pricing": "定价页",
    "free_quota": "免费额度页",
    "token_plan": "Token Plan 页",
    "activities": "活动页",
    "free_model": "免费模型文档",
    "license": "开源/社区协议",
    "free_tier": "免费层/额度说明",
    "trial": "试用中心",
    "price": "价格详情",
    "referral": "邀请返利 / 拉新页",
    "student_program": "学生 / 高校计划页",
    "rate_limits": "速率限制文档",
    "billing": "计费说明",
    "billing_rules": "计费规则",
    "billing_docs": "计费文档",
    "workers_pricing": "Workers 定价",
    "serverless_pricing": "Serverless 定价",
    "tokenhub": "TokenHub 页",
    "blog": "官方博客",
    "engineering": "工程博客",
    "news": "新闻 / 更新",
    "updates": "更新日志",
    "v4_news": "版本动态",
    "research": "研究页",
    "changelog": "变更日志",
    "feed": "RSS/Atom 订阅源",
    "product": "产品页",
    "api_docs": "API 文档",
    "docs": "文档页",
    "console": "控制台",
    "discovered": "自动发现的定价/免费页",
    "homepage": "官网首页",
}

# 证据关键词组：(组键, 中文标题, 关键词列表)
# 注意：纯英文词按词边界匹配，避免 off 匹配到 office 之类误报
KEYWORD_GROUPS: list[tuple[str, str, list[str]]] = [
    ("free_tier", "长期免费 / 免费层", [
        "永久免费", "长期免费", "完全免费", "免费层", "免费额度", "免费调用", "免费使用",
        "免费模型", "免费套餐", "免费tokens", "免费 tokens", "免费体验", "免费开放",
        "公测期", "free tier", "free layer", "free of charge", "free plan",
        "free api", "free access", "free credits", "free allocation",
        "free allowance", "at no cost", "no cost", "at no charge", "no charge",
        "for free", "free to use", "free to prototype", "start free",
        "are free", "no per-token billing", "$0 per", "$0+",
        "¥0", "0元", "0 元", "不收费", "免收", "零成本", "免费额度累计",
        "royalty-free", "free for research", "free for commercial", "free to test",
        "open-weight", "open-weights",
    ]),
    ("signup_bonus", "注册赠送 / 新人试用", [
        "注册送", "注册即", "注册就送", "注册领", "新用户", "新人", "赠送", "送你",
        "免费试用", "试用额度", "体验金", "试用金", "首月免费", "新客", "新手福利",
        "开通即送", "登录即送", "免费账户", "免费账号", "迎新赠金", "免费体验额度",
        "sign up", "signup", "sign-up", "free trial", "trial key", "trial api key",
        "trial credit", "free credit", "free tokens", "free account",
        "get a free trial", "with a free trial", "free trial period",
        "starting credit", "credit when you", "get $", "welcome credit",
        "opening credit", "one-time credit", "come with credits",
        "new accounts",
    ]),
    ("subscription", "包月订阅 / Token Plan", [
        "token plan", "tokenplan", "包月", "套餐", "订阅计划", "订阅", "会员",
        "月付", "subscription", "subscribe", "pro plan", "coding plan",
        "monthly plan", "monthly credits", "credits per month",
        "plan includes", "every plan", "轻享包", "保障包", "tpm 保障包",
    ]),
    ("activity", "限时活动 / 优惠", [
        "限时免费", "限时五折", "限时优惠", "限时特惠", "限时两周", "限时抢",
        "活动期间", "促销", "优惠", "福利", "折扣", "打折", "特惠", "返利",
        "邀请有礼", "推荐有奖", "promo", "discount", "limited time",
        "limited-time", "coupon", "立减", "满减", "特惠专区",
        "退款", "余额退还", "降本", "服务调整", "打折版本",
    ]),
    ("referral", "邀请返利 / 拉新奖励", [
        "邀请", "推荐", "拉新", "返券", "返利", "邀请有礼", "推荐官", "老带新",
        "邀请奖励", "邀请好友", "邀请注册", "邀请得", "邀请人", "被邀请",
        "推荐注册", "好友注册", "推广", "返现", "叠加",
        "refer", "referral", "refer a friend", "invite friends",
        "inviting", "invitation", "invite reward", "referral bonus",
        "reward for inviting", "stackable", "unlimited stacking",
    ]),
    ("student", "学生 / 高校扶持", [
        "学生", "高校", "师生", "校园", "大学生", "在校学生", "教育优惠",
        "学生优惠", "学生计划", "学生认证", "学生福利", "学生包", "教育用户",
        "student", "students", "education", "campus", "edu plan",
        "student plan", "student pricing", "student discount", "github pack",
    ]),
    ("condition", "限制条件（绑卡 / 实名 / 速率）", [
        "绑卡", "信用卡", "credit card", "实名", "实名认证", "企业认证",
        "个人认证", "学生优惠", "学生计划", "学生认证", "师生", "高校",
        "student discount", "student plan", "student pricing",
        "仅限个人", "个人用户", "企业实名", "速率", "限流", "限速", "rate limit",
        "rate-limit", "rpm", "tpm", "并发限制", "并发数", "并发上限",
        "并发请求", "默认并发", "quota", "kyc", "备案制", "备案要求",
        "需备案", "完成备案", "需绑定",
        "requires a credit card", "verify your", "concurrent",
        "requests per minute", "req/min", "per minute",
        "monthly active users", "license agreement", "community license",
        "同一用户", "首次使用",
    ]),
]

README_BEGIN = "<!-- LLM-INTEL:BEGIN  本章节由 crawler_llm_intel.py 自动生成，请勿手工修改 -->"
README_END = "<!-- LLM-INTEL:END -->"

# 365 开源计划页脚：随生成区块一起输出（位于 END 标记之前），
# 若放在 END 之后会在下次 update_readme 时被当作历史人工附录丢弃。
PLAN_FOOTER = """---

## 关于 365 开源计划

[365 开源计划](https://github.com/rockbenben/365opensource) 的第 **#038** 个项目——一个人 + AI，一年 300+ 个开源项目。

[提交你的需求 →](https://365.aishort.top/) · [Discord](https://discord.gg/PZTQfJ4GjX) · [Telegram](https://t.me/aishort_top)"""
# 白嫖攻略独立生成块，位于项目介绍之后、快速开始之前（读者最关心，需置顶）
GUIDE_BEGIN = "<!-- LLM-GUIDE:BEGIN  本章节由 crawler_llm_intel.py 自动生成，请勿手工修改 -->"
GUIDE_END = "<!-- LLM-GUIDE:END -->"
NEWS_BEGIN = "<!-- LLM-NEWS:BEGIN  本章节由 crawler_llm_intel.py 自动生成，请勿手工修改 -->"
NEWS_END = "<!-- LLM-NEWS:END -->"

# 仓库主页：RSS 频道 <link> 指向它（订阅源本身没有对应的 HTML 页面）
REPO_URL = "https://github.com/rockbenben/free-llm-intel"

# 自建 RSS 订阅源（GitHub Pages 托管）
# 存在意义：llm-news-feeds.md 里相当一部分厂商官方**没有** RSS/Atom（只能靠页面
# 提取兜底）。本仓库既然已把这些页面归档成结构化文章，就顺手把它们变成真正可订阅
# 的源——否则「无官方源的厂商」永远只能靠人肉刷页面。
RSS_TITLE_MAX = 60      # 标题超过该长度则截断，完整文本移入 description
#: 合并流最多收录条数；**0 = 不限制**（收录全部有日期的条目）。
#: 曾经是 200，理由是「全量约 1.2 MB 的 feed 会让阅读器吃力」——**这个理由站不住**：
#: GitHub Pages 用 gzip 传输（线上实测 `Content-Encoding: gzip`），全量 2575 条
#: （XML 1124 KB）压缩后只有 **131 KB**，阅读器毫无压力。当时的判断看的是未压缩体积。
#: 单厂商源本来就不设上限（等于该厂商全量归档）。
RSS_MERGED_LIMIT = 0


def merged_scope_text(merged_limit: int) -> str:
    """合并流收录范围的文案。0 = 不限制。文案要跟着实际上限走，别写死。"""
    return "收录全部有日期的条目" if not merged_limit else f"最近 {merged_limit} 条"

BLOCK_TAGS = {
    "p", "div", "li", "tr", "td", "th", "h1", "h2", "h3", "h4", "h5", "h6",
    "br", "section", "article", "ul", "ol", "table", "header", "footer",
    "blockquote", "pre", "figure", "figcaption", "dt", "dd", "hr",
}
SKIP_TAGS = {"script", "style", "noscript", "svg", "iframe", "template"}
# 标题元素。卡片式列表页（通义更新日志、MiniMax 发布说明、x.ai/news 等）常把
# 整个卡片包进一个 <a>，锚文本因此是「标题 + 整段描述」拍平后的长串。
# 这些元素是拿回真正标题的结构线索 —— 比事后按标点猜可靠。
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}


# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------

@dataclass
class PageResult:
    """单个 URL 的抓取结果。"""
    url: str
    stype: str
    ok: bool = False
    status_code: int | None = None
    final_url: str = ""
    title: str = ""
    text: str = ""
    raw: str = ""  # 原始响应体（RSS/Atom 等 XML 源保留原文，供 feed 解析）
    feeds: list[str] = field(default_factory=list)
    links: list[tuple[str, str]] = field(default_factory=list)
    #: 与 `links` 逐项对齐：锚内标题元素（HEADING_TAGS）的文本，无则空串。
    #: 卡片式列表页里 `<a>` 会把标题和整段描述一起包住，拍平后粘成长串；
    #: 有了它才能取回真正的标题（见 extract_articles_from_page）。
    link_headings: list[str] = field(default_factory=list)
    error: str = ""
    sparse: bool = False  # 文本过少（可能是 JS 动态渲染 / 需登录）
    is_login: bool = False  # 页面重定向至登录认证页
    rendered_by: str = "requests"  # requests | browser
    discovered: bool = False  # 是否为脚本从首页自动发现的链接
    # 仅 requests 原文提取的文本，用于快照哈希：必须与 CI 的 --no-browser 运行
    # 结果一致，浏览器渲染出的额外内容（JS 页面/懒加载）不得进入快照，否则本地与
    # CI 哈希会来回打架、反复误触发 AI。为空表示该页在纯 requests 下不可快照。
    snapshot_text: str = ""
    snapshot_ok: bool = False  # requests 阶段即成功且非稀疏/登录：仅此类页面进入快照


@dataclass
class Snippet:
    text: str
    url: str
    stype: str


@dataclass
class Article:
    """博客 / 更新动态中的一篇文章（RSS item 或页面文章链接提取）。"""
    title: str
    url: str
    date: str = ""        # 归一化为 YYYY-MM-DD；无法解析则为空
    source: str = ""      # 来源标签：RSS / 页面提取
    stype: str = ""
    zh_title: str = ""    # 归档沿用的中文标题；空则现场走 translate_to_zh

    def __post_init__(self) -> None:
        # 统一在这里洗控制字符：RSS 原始 XML 与页面提取都可能带 \x00，
        # 有 6 处 Article(...) 构造点，收口在数据类比逐处修补更可靠
        self.title = sanitize_text(self.title)
        self.url = sanitize_text(self.url)
        self.date = sanitize_text(self.date)
        self.source = sanitize_text(self.source)
        self.stype = sanitize_text(self.stype)
        self.zh_title = sanitize_text(self.zh_title)


#: 归档标题「已是中文」的判据：含任一 CJK 字符即算（与 translate_to_zh 的整句跳过阈值无关，
#: 这里只需区分「人工/AI 汉化过」与「还是英文原标题」）。
_CJK_CHAR_RE = re.compile(r"[\u4e00-\u9fff]")


def article_title_zh(art: "Article") -> str:
    """输出用标题：优先归档沿用的中文译文，否则现场翻译（走磁盘缓存）。"""
    return art.zh_title or translate_to_zh(art.title)


#: 标题润色批量与单次巡检预算（新条目每天个位数；预算只防新收录厂商一次性几百条）
TITLE_POLISH_BATCH = 40
TITLE_POLISH_RUN_BUDGET = 300

_POLISH_LINE_RE = re.compile(r"^\s*(\d+)\s*(?:[.、）)]|[：:])?\s*[ \t]*\s*(.+?)\s*$")


def parse_polish_response(text: str, expected: list[str]) -> dict[str, str]:
    """解析「编号<TAB>中文标题」输出为 {英文原标题: 中文标题}。

    宽容排版（编号后可用制表/点/冒号），但内容从严：同一编号取第一个匹配、越界丢弃、
    既无中文又不同于原文的丢弃（= 没翻出来，回落机翻），过长疑似续写解释的丢弃。
    """
    mapping: dict[str, str] = {}
    for line in text.splitlines():
        m = _POLISH_LINE_RE.match(line)
        if not m or len(m.group(1)) > 6:
            continue
        idx = int(m.group(1))
        if not 1 <= idx <= len(expected):
            continue
        orig = expected[idx - 1]
        if orig in mapping:
            continue
        zh = m.group(2).strip().strip("\"'“”「」")
        if not zh or len(zh) > max(120, len(orig) * 2):
            continue
        if zh != orig.strip() and not _CJK_CHAR_RE.search(zh):
            continue
        mapping[orig] = zh
    return mapping


def make_llm_title_polisher(budget: int = TITLE_POLISH_RUN_BUDGET,
                            batch: int = TITLE_POLISH_BATCH):
    """返回 brand/titles -> {英文: 中文} 的润色回调（LLM 通道与 --ai-review 同源）。

    只应当次运行的**新增**机翻标题；结果写进 Article.zh_title 后随归档冻结，
    一篇只花一次调用。失败不抛异常（调用方回落 Google 机翻）。
    """
    import ai_review
    remaining = [budget]

    def polish(brand: str, titles: list[str]) -> dict[str, str]:
        out: dict[str, str] = {}
        for i in range(0, len(titles), batch):
            chunk = titles[i:i + batch]
            chunk = chunk[:max(remaining[0], 0)]
            remaining[0] -= len(chunk)
            if not chunk:
                break
            lines = "\n".join(f"{n}\t{t}" for n, t in enumerate(chunk, 1))
            prompt = (
                "你是科技资讯标题译者。下面每行是「编号<TAB>英文原标题」，请逐行译成中文标题。\n"
                "要求：品牌 / 模型 / 术语保留原文（如 Claude、GPT-6、LoRA、MCP）；忠实原意，"
                "不加原文没有的营销词与感叹号；原标题本身就是型号标识时原样返回该行。\n"
                "输出格式：一行一条「编号<TAB>中文标题」，不要解释、不要引号、不要 Markdown。\n\n"
                + lines)
            try:
                out.update(parse_polish_response(ai_review.call_llm(prompt), chunk))
            except Exception as exc:
                print(f"      [ai-titles] {brand}：润色失败，回落机翻"
                      f"（{type(exc).__name__}: {exc}）", file=sys.stderr)
        return out

    return polish


@dataclass
class VendorIntel:
    vendor_id: str
    brand: str
    homepage: str
    products: list[str]
    intel_pages: list[PageResult] = field(default_factory=list)   # 情报页 + 条件页
    news_pages: list[PageResult] = field(default_factory=list)    # 博客 / 动态页
    skipped_sources: list[dict] = field(default_factory=list)     # product 等未抓入口
    evidence: dict[str, list[Snippet]] = field(default_factory=dict)
    news_articles: list[Article] = field(default_factory=list)    # 主文档：最新 5 篇
    all_news_articles: list[Article] = field(default_factory=list)  # 子文档：全量文章归档
    news_filtered: int = 0    # 被「情报过滤」剔除的条目数（见 NEWS_INTEL_SIGNALS）


# ---------------------------------------------------------------------------
# HTML 解析（标准库，无 bs4 依赖）
# ---------------------------------------------------------------------------

class PageParser(HTMLParser):
    """从 HTML 中提取：可见文本（按块级标签换行）、title、RSS/Atom 订阅源链接。"""

    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self._chunks: list[str] = []
        self._skip_depth = 0
        self._in_title = False
        self._title_parts: list[str] = []
        self.feeds: list[str] = []
        self.links: list[tuple[str, str]] = []  # (绝对URL, 锚文本)
        # 与 links **逐项对齐**：锚内标题元素（HEADING_TAGS）的文本，无则空串。
        self.link_headings: list[str] = []
        self._a_heading: list[str] = []
        self._a_heading_depth: int = 0
        self.title = ""
        self._a_href: str | None = None
        self._a_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        tag = tag.lower()
        if tag in SKIP_TAGS:
            self._skip_depth += 1
            return
        attr = {k.lower(): (v or "") for k, v in attrs}
        if tag == "title":
            self._in_title = True
        if tag in BLOCK_TAGS:
            self._chunks.append("\n")
        if tag == "a":
            href = attr.get("href", "")
            self._a_href = urljoin(self.base_url, href) if href else None
            self._a_text = []
            self._a_heading = []
            self._a_heading_depth = 0
        if tag == "link":
            rel = attr.get("rel", "").lower()
            ltype = attr.get("type", "").lower()
            href = attr.get("href", "")
            if href and "alternate" in rel and ("rss" in ltype or "atom" in ltype or "xml" in ltype):
                feed = urljoin(self.base_url, href)
                # sitemap.xml 不是订阅源，不能当作 RSS/Atom（否则会被写进 OPML）
                if "sitemap" not in feed.lower() and feed not in self.feeds:
                    self.feeds.append(feed)
        if tag == "a" and self._a_href:
            # 仅匹配路径段明确为 rss/atom/feed 的链接，避免 anatomy 等词误报
            feed_pat = re.compile(
                r"((^|[/=.])(rss|atom|feeds?)([/?#]|$))|(\.(rss|xml)([?#]|$))", re.I)
            if (feed_pat.search(self._a_href)
                    and "sitemap" not in self._a_href.lower()
                    and not self._a_href.endswith(
                        (".png", ".jpg", ".jpeg", ".gif", ".css", ".js", ".html"))):
                if self._a_href not in self.feeds:
                    self.feeds.append(self._a_href)
        # 锚内的标题元素：记住进入深度，退出时取文本（见 link_headings）
        if tag in HEADING_TAGS and self._a_href is not None:
            self._a_heading_depth += 1

    def handle_endtag(self, tag: str):
        tag = tag.lower()
        if tag in SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
            return
        if tag == "title":
            self._in_title = False
        if tag in HEADING_TAGS and self._a_heading_depth > 0:
            self._a_heading_depth -= 1
        if tag == "a" and self._a_href is not None:
            text = re.sub(r"\s+", " ", "".join(self._a_text)).strip()
            heading = re.sub(r"\s+", " ", "".join(self._a_heading)).strip()
            self.links.append((self._a_href, text))
            self.link_headings.append(heading)
            self._a_href = None
            self._a_text = []
            self._a_heading = []
            self._a_heading_depth = 0
        if tag in BLOCK_TAGS:
            self._chunks.append("\n")

    def handle_data(self, data: str):
        if self._skip_depth:
            return
        if self._in_title:
            self._title_parts.append(data)
        if self._a_href is not None:
            self._a_text.append(data)
            if self._a_heading_depth > 0:
                self._a_heading.append(data)
        self._chunks.append(data)

    def get_text(self) -> str:
        text = "".join(self._chunks)
        text = html_mod.unescape(text)
        lines = []
        for line in text.split("\n"):
            line = re.sub(r"[ \t\r\f\v]+", " ", line).strip()
            if line:
                lines.append(line)
        return sanitize_text("\n".join(lines))

    def get_title(self) -> str:
        return sanitize_text(re.sub(r"\s+", " ", "".join(self._title_parts)).strip())


def parse_html(raw_html: str, base_url: str
               ) -> tuple[str, str, list[str], list[tuple[str, str]], list[str]]:
    """返回 (纯文本, 页面标题, RSS/Atom 链接列表, [(链接URL, 锚文本)], 锚内标题列表)。

    最后一个列表与链接列表**逐项对齐**（无标题元素处为空串），供
    `extract_articles_from_page` 取回卡片式列表页里被 `<a>` 包住的真标题。
    """
    parser = PageParser(base_url)
    try:
        parser.feed(raw_html)
        parser.close()
    except Exception as exc:  # 解析器容错：残缺 HTML 不应导致整体失败
        print(f"  [warn] HTML 解析异常 {base_url}: {type(exc).__name__}: {exc}",
              file=sys.stderr)
    return (parser.get_text(), parser.get_title(), parser.feeds,
            parser.links, parser.link_headings)


# ---------------------------------------------------------------------------
# YAML 解析与分组
# ---------------------------------------------------------------------------

def parse_yaml(path: Path) -> tuple[list[dict], list[dict]]:
    """使用 yaml.safe_load 解析 llm-intel.yaml，返回 (vendors, sources)。"""
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} 顶层结构不是 mapping")
    vendors = data.get("vendors") or []
    sources = data.get("sources") or []
    if not isinstance(vendors, list) or not isinstance(sources, list):
        raise ValueError(f"{path} 中 vendors / sources 应为列表")
    return vendors, sources


def group_sources_by_vendor(sources: list[dict]) -> dict[str, list[dict]]:
    """按 vendor_id 分组 sources，保持 YAML 中的出现顺序。"""
    grouped: OrderedDict[str, list[dict]] = OrderedDict()
    for item in sources:
        vid = (item or {}).get("vendor_id")
        if not vid:
            continue
        grouped.setdefault(vid, []).append(item)
    return grouped


# ---------------------------------------------------------------------------
# 网络抓取
# ---------------------------------------------------------------------------

def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    })
    return session


class BrowserSession:
    """
    可选的 Playwright 真实浏览器后端：当 requests 被反爬拦截（403 等）或抓到
    JS 空壳页面时，用系统 Edge/Chrome（无头）重新渲染并取最终 HTML。
    整个巡检复用一个浏览器实例；未安装 playwright 时安全降级。
    """

    def __init__(self, enabled: bool = True, settle_ms: int = 3000,
                 goto_timeout_ms: int = 45000):
        self.enabled = enabled and HAS_PLAYWRIGHT
        self.settle_ms = settle_ms
        self.goto_timeout_ms = goto_timeout_ms
        self._pw = None
        self._browser = None
        self._page = None
        self._tried_launch = False

    def __enter__(self) -> "BrowserSession":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def _ensure(self) -> bool:
        if not self.enabled or self._page is not None:
            return self._page is not None
        if self._tried_launch:
            return False
        self._tried_launch = True
        try:
            self._pw = sync_playwright().start()
            launch_attempts = [
                ("系统 Edge", {"channel": "msedge"}),
                ("系统 Chrome", {"channel": "chrome"}),
                ("Playwright 内置 Chromium", {}),
            ]
            browser_kind = ""
            for label, kwargs in launch_attempts:
                try:
                    self._browser = self._pw.chromium.launch(
                        headless=True, **kwargs)
                    browser_kind = label
                    break
                except Exception:
                    self._browser = None
                    continue
            if self._browser is None:
                self.enabled = False
                print("  [warn] 浏览器后端启动失败（未找到 Edge/Chrome/Chromium），"
                      "JS 页面将仅标注；可执行 `playwright install chromium`",
                      file=sys.stderr)
                return False
            ctx = self._browser.new_context(
                user_agent=USER_AGENT, locale="zh-CN",
                ignore_https_errors=True,
                viewport={"width": 1440, "height": 900},
            )
            self._page = ctx.new_page()
            print(f"  [browser] 已启动真实浏览器后端（{browser_kind}，无头）")
            return True
        except Exception as exc:
            self.enabled = False
            print(f"  [warn] 浏览器后端不可用: {type(exc).__name__}: {str(exc)[:120]}",
                  file=sys.stderr)
            return False

    def _new_page(self):
        ctx = self._browser.new_context(
            user_agent=USER_AGENT, locale="zh-CN",
            ignore_https_errors=True,
            viewport={"width": 1440, "height": 900},
        )
        page = ctx.new_page()
        # 关闭旧页面，避免长时间运行后标签页堆积
        try:
            if self._page is not None:
                old_ctx = self._page.context
                self._page.close()
                old_ctx.close()
        except Exception:
            pass
        self._page = page
        return page

    def _render_once(self, url: str) -> tuple[str, str, int | None] | None:
        page = self._page or self._new_page()
        resp = page.goto(url, timeout=self.goto_timeout_ms,
                         wait_until="domcontentloaded")
        try:
            page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass
        page.wait_for_timeout(self.settle_ms)
        # 滚动以触发懒加载内容
        for y in (600, 1500, 3000):
            try:
                page.mouse.wheel(0, y)
                page.wait_for_timeout(250)
            except Exception:
                pass
        return page.content(), page.url, (resp.status if resp else None)

    def render(self, url: str) -> tuple[str, str, int | None] | None:
        """返回 (最终HTML, 最终URL, HTTP状态码)；失败时重建页面重试一次，再失败返回 None。"""
        if not self._ensure():
            return None
        for attempt in range(2):
            try:
                return self._render_once(url)
            except Exception as exc:
                if attempt == 0:
                    try:
                        self._new_page()  # 重建干净页面后重试
                    except Exception:
                        pass
                else:
                    print(f"  [warn] 浏览器渲染失败 {url}: {type(exc).__name__}: "
                          f"{str(exc)[:100]}", file=sys.stderr)
        return None

    def close(self) -> None:
        for obj, closer in ((self._browser, "close"),
                           (self._pw, "stop")):
            try:
                if obj is not None:
                    getattr(obj, closer)()
            except Exception:
                pass
        self._browser = None
        self._pw = None
        self._page = None


def _fetch_with_requests(session: requests.Session, url: str, stype: str,
                         timeout: tuple[float, float], retries: int) -> PageResult:
    """用 requests 抓取，任何异常都封装进 PageResult，不向上抛出。"""
    result = PageResult(url=url, stype=stype, final_url=url)
    last_err = ""
    for attempt in range(retries + 1):
        try:
            resp = session.get(url, timeout=timeout, allow_redirects=True)
            result.status_code = resp.status_code
            result.final_url = resp.url
            if resp.status_code >= 400:
                last_err = f"HTTP {resp.status_code}"
                if attempt < retries:
                    time.sleep(1.0)
                    continue
                result.error = last_err
                return result
            # 中文站点编码兜底：requests 猜测失败时改用 apparent_encoding
            if not resp.encoding or resp.encoding.lower() in ("iso-8859-1", "ascii"):
                resp.encoding = resp.apparent_encoding or resp.encoding
            ctype = resp.headers.get("Content-Type", "").lower()
            if stype == "feed":
                # RSS/Atom 源：保留原始 XML 正文（feed 解析器直接消费），
                # 不做 HTML 文本提取（标签会被剥掉导致 item 信息丢失）
                result.raw = resp.text[:2_000_000]
                result.ok = True
                result.sparse = len(result.raw) < 200
                return result
            if "html" not in ctype and "xml" not in ctype and len(resp.text) > 0:
                # 非 HTML（例如直接的 JSON 接口）——保留原始文本前若干字符
                result.text = resp.text[:20000]
                result.snapshot_text = result.text
                result.ok = True
                result.sparse = len(result.text) < 200
                result.snapshot_ok = not result.sparse
                return result
            result.raw = resp.text[:2_000_000]
            text, title, feeds, links, link_headings = parse_html(resp.text, resp.url)
            result.text = text
            result.snapshot_text = text  # 浏览器兜底不得覆盖此字段（见 PageResult）
            result.title = title
            result.feeds = feeds
            result.links = links
            result.link_headings = link_headings
            result.ok = True
            # 可见文本过少：通常是 SPA 动态渲染或需要登录（阈值放宽到 800，
            # 500~800 字多为导航外壳，正文仍靠浏览器兜底渲染）
            text_len = len(re.sub(r"\s", "", text))
            # 文本不算极少但页面确是 JS 渲染外壳（空挂载点 / <html id> 挂载）：
            # 正文全靠客户端渲染，同样走浏览器兜底
            spa_shell = text_len < 3000 and bool(
                SPA_EMPTY_MOUNT.search(resp.text or "")
                or SPA_HTML_MOUNT.search(resp.text or ""))
            result.sparse = text_len < 800 or spa_shell
            if LOGIN_PATTERNS.search(result.final_url):
                result.is_login = True
            # 仅 requests 阶段即成功且非稀疏/登录的页面可进快照；
            # 浏览器兜底把 sparse 翻转为 False 时不得改变此结论
            result.snapshot_ok = not result.sparse and not result.is_login
            return result
        except requests.RequestException as exc:
            last_err = f"{type(exc).__name__}: {str(exc)[:160]}"
            if attempt < retries:
                time.sleep(1.0)
        except Exception as exc:  # 兜底：单页失败不影响整体
            last_err = f"{type(exc).__name__}: {str(exc)[:160]}"
            break
    result.error = last_err or "未知抓取错误"
    return result


def fetch_url(session: requests.Session, url: str, stype: str,
              browser: "BrowserSession | None" = None,
              timeout: tuple[float, float] = (10.0, 30.0),
              retries: int = 1) -> PageResult:
    """
    抓取单个 URL：优先 requests；若被反爬拦截（401/403/429 等）或抓到 JS 空壳，
    且提供了 browser，则用真实浏览器重渲染兜底。任何异常都不向上抛出。
    """
    result = _fetch_with_requests(session, url, stype, timeout, retries)

    if LOGIN_PATTERNS.search(result.final_url):
        result.is_login = True

    # 429 速率限制短暂退避重试一次
    if result.status_code == 429:
        time.sleep(2.0)
        result = _fetch_with_requests(session, url, stype, timeout, retries=0)

    blocked_status = result.status_code in (400, 401, 403, 407, 429, 451)
    # requests 返回 200 但正文是反爬拦截 / 验证页（如 Cloudflare "Sorry, blocked"）
    req_blocked = bool(result.ok and BLOCK_MARKERS.search((result.text or "")[:3000]))
    needs_browser = browser is not None and browser.enabled and (
        not result.ok or blocked_status or result.sparse or req_blocked)
    if not needs_browser:
        return result

    rendered = browser.render(url)
    if not rendered:
        if req_blocked:  # requests 拿到的就是拦截页
            result.ok = False
            result.error = "疑似被反爬拦截（HTTP 200 但正文为拦截/验证页）"
        return result  # 浏览器也失败：保留 requests 的结果与标注
    html, final_url, code = rendered
    text, title, feeds, links, link_headings = parse_html(html, final_url or url)
    plain_len = len(re.sub(r"\s", "", text))
    is_block_page = bool(BLOCK_MARKERS.search(text[:3000]))

    if is_block_page:
        # 无头浏览器渲染出来的仍是反爬拦截 / 验证页（多为 IP 信誉级封锁）
        result.ok = False
        result.sparse = True
        result.rendered_by = "browser"
        result.error = ("被反爬拦截（Cloudflare/验证页）：requests 与无头浏览器均未取得正文，"
                        "建议人工访问或使用带住宅代理的有头浏览器")
        return result

    if LOGIN_PATTERNS.search(final_url or result.final_url or url):
        result.is_login = True

    if plain_len < 60 and not result.is_login:
        return result  # 浏览器内容也近乎为空：保留原结果

    result.text = text
    result.title = title or result.title
    result.feeds = sorted(set(result.feeds) | set(feeds))
    result.links = links or result.links
    result.link_headings = link_headings or result.link_headings
    result.final_url = final_url or result.final_url
    result.raw = html[:2_000_000]
    result.status_code = code or result.status_code or 200
    result.ok = True
    result.error = ""
    result.sparse = plain_len < 300 and not result.is_login
    result.rendered_by = "browser"
    # 注意：刻意不更新 snapshot_text / snapshot_ok —— 快照哈希必须保持
    # 与纯 requests（CI --no-browser）一致，避免本地/CI 哈希互相打架。
    return result


# ---------------------------------------------------------------------------
# 证据提取
# ---------------------------------------------------------------------------

def _kw_hit(keyword: str, line_lower: str) -> bool:
    """
    关键词命中判断：纯 ASCII 关键词按词边界匹配（避免 off 命中 office），
    词尾允许常见屈折变化（s/es/ed/ing/d/e，如 rate limit -> rate limited / limits）；
    中文按子串匹配。
    """
    kw = keyword.lower()
    if re.fullmatch(r"[\x20-\x7e]+", kw) and re.search(r"[a-z]", kw):
        return re.search(
            r"(?<![a-z0-9])" + re.escape(kw)
            + r"(?:ing|ies|ied|ered|ed|es|s|d|e)?(?![a-z0-9])",
            line_lower) is not None
    return kw in line_lower


# 图标字体 / 导航噪声行过滤
#: 控制字符清洗：除制表符(\x09) / 换行(\x0a) / 回车(\x0d) 外，C0 控制码与 \x7f 一律剔除。
#: 抓到的 HTML 与翻译接口偶发 \x00，若混进 README 会被 git / grep 判为二进制文件。
#: 注意分段写法——\x0d 夹在 \x0b-\x0c 与 \x0e 之间，写成 \x0b-\x1f 会把 \r 一起删掉。
_CTRL_RE = re.compile(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]")


def sanitize_text(text: str) -> str:
    """剔除页内文本中的控制字符（保留 \\t \\n \\r），供写入 Markdown 产物使用。"""
    return _CTRL_RE.sub("", text or "")


NOISE_LINE = re.compile(r"(check_circle|chevron_|arrow_forward|cancel_circle|^menu$)", re.I)

# 页面样板文字：Cookie / 隐私横幅，以及在线体验 / Playground 里的「示例提示词」
# （如“-上下文：我想推广公司的新产品。我的公司名为：智谱…”——曾因含“推广”被
# referral 关键词误选为邀请返利证据）。这些永远不会是免费额度事实。
BOILERPLATE_NOISE = re.compile(
    r"(?:this|these|our)\s+cookie|此 ?cookie|本(?:网站|站).{0,12}cookie|"
    r"我们使用.{0,6}cookie|stripe\.com|cookie 政策|__stripe|"
    r"-?上下文：|我想推广|我的公司名|新产品名[称为]|^你是一[个名]|请扮演|扮演一[个名]",
    re.I)

# 纯导航词拼接行（如“模型Token Plan文档控制台”），不是事实陈述
NAV_CONCAT = re.compile(
    r"^(模型|文档|控制台|首页|定价|价格|平台|官网|博客|新闻|登录|注册|资源|"
    r"产品|服务|中心|开放平台|token ?plan|docs?|console|pricing|home|blog|"
    r"sign|login|register|api|keys?|rate limits?|and|or|the|of|[\s/|·•])+$",
    re.I)

# 即使以 CTA 开头但包含这些词，仍是事实陈述（如 "Get started with a free trial..."）
FREEISH = re.compile(
    r"(free|免费|试用|赠送|额度|credits?|quota|trial|套餐|补贴|不收费|免收|¥0|\$0|0\s*元)",
    re.I,
)

# AI / 大模型相关性：云厂商超大定价页里与 LLM 无关的噪声（SQL Server、TensorBoard、
# SAP 认证、WebSocket 消息等）借此过滤掉；包含高信号免费/套餐词的行也算相关
AI_CONTEXT = re.compile(
    r"(model|token|inferenc|llm|generative|\bai\b|aigc|gpt|gemini|claude|grok|bedrock|"
    r"vertex|agent|neurons?|llama|deepseek|qwen|mistral|yi|glm|hunyuan|doubao|"
    r"sensenova|minimax|laguna|poolside|kimi|spark|tiangong|skywork|"
    r"royalty-free|open[- ]?weight|open[- ]?source|community license|"
    r"模型|大模型|智能|算力|推理|额度|tokens?|api|多模态|语言模型|"
    r"缓存|限流|限速|速率|并发|配额|quota|credits?|免费|套餐|订阅|试用|赠送|"
    r"free[- ]?(tier|plan|credits?|trial|allocation|allowance|quota|to use)|trial key|"
    r"token plan|coding plan|rate[- ]?limits?|concurrent|req/min|"
    r"requests per minute|\$0(?![0-9.])|¥0|0\s*元|不收费|退款|免收|成本|调用)",
    re.I,
)

# 纯导航 / 按钮 / CTA 行（不是事实陈述）
CTA_NAV = re.compile(
    r"^(sign up( for free)?|sign in|log ?in|log out|get started|contact( sales| us)?|"
    r"subscribe( to (emails|our newsletter))?|read more|learn more|view more|"
    r"try (it|for free|now)|buy now|skip to (main )?content|skip to navigation|"
    r"jump to (content|main|navigation)|back to top|立即订阅|立即购买|立即咨询|"
    r"免费试用|免费注册|联系(销售|我们)|了解更多|查看更多|查看详情|阅读更多|开始使用|"
    r"注册|登录|返回顶部|回到顶部|跳至主要内容|跳到主要内容|跳转到主要内容|→|›)",
    re.I,
)

_HAS_QUANTITY = re.compile(
    r"[0-9０-９$¥€元%％]|per month|per ?million|/月|每月|每次|"
    r"per ?1m tokens?|/ ?1m|/ ?m(?= ?tok)|/ ?1k")

# 短到会被长度门槛滤掉、但本身就是高信号免费事实的中文徽标文案
# （如定价页模型卡片上的“限时免费 / 永久免费”角标；“免费领取”是按钮，不在此列）
BADGE_FACTS = {"限时免费", "永久免费", "长期免费", "完全免费", "免费开放"}


def _is_fact_line(line: str) -> bool:
    """判断一行是否为有信息量的事实陈述（过滤问句、按钮、标题、导航）。"""
    s = line.strip()
    # 高信号中文徽标（“限时免费”等）虽短但本身就是事实，优先放行
    if s in BADGE_FACTS:
        return True
    if len(s) < 8 or NOISE_LINE.search(s) or NAV_CONCAT.match(s):
        return False
    if BOILERPLATE_NOISE.search(s):
        return False
    if s.endswith("?") or s.endswith("？"):  # FAQ 问句，答案通常在下一行
        return False
    if CTA_NAV.match(s):
        # “Get started with 25 free credits / a free trial” 这类虽以 CTA 开头，
        # 但含数字或免费关键词，保留；纯按钮文案才过滤
        if len(s) < 30 or (not _HAS_QUANTITY.search(s) and not FREEISH.search(s)):
            return False
    # 面包屑 / 页面标题，形如 “Token Plan - MiniMax API 平台”“免费额度 - 千问AI平台”，
    # 以及 “API Credit & Rate Limits - Handle 402 and 429 Errors” 这类标题
    # （HTTP 错误码也含数字，故标题过滤不再以“含数字”豁免）
    if (" - " in s and len(s) < 80
            and not re.search(r"[。，,！!：:?？]|[$¥€]\s?[0-9]|[0-9]\s?(元|美元|美金|折|%|％)",
                              s)):
        return False
    if " | " in s and len(s) < 80 and not _HAS_QUANTITY.search(s):
        return False
    # 短且无数字/金额的行多为导航词 / 小标题（如 “Coding Plan”“API Keys and Rate
    # Limits”）；中文短句信息量高（如“公测期完全免费开放”），长度门槛放宽
    has_cjk = bool(re.search(r"[一-鿿]", s))  # CJK 统一汉字区间
    if has_cjk:
        if len(s) < 12 and not (_HAS_QUANTITY.search(s) and FREEISH.search(s)) and s not in BADGE_FACTS:
            return False
    elif not _HAS_QUANTITY.search(s):
        # 英文表格 / 断行残句（小写开头且无句末标点，如 “govern capacity
        # globally. ... rate limits for”），不是完整事实陈述
        if (len(s) < 40
                or (re.match(r"^[a-z]", s)
                    and not re.search(r"[.!?…\"'’”)]$", s))):
            return False
        # 纯英文小标题 / 菜单项（多为 Title Case，如 “Different Types of API Keys
        # and Rate Limits”），不是事实陈述
        if len(s) < 60:
            words = re.findall(r"[A-Za-z][A-Za-z'-]*", s)
            cap = sum(1 for w in words if w[:1].isupper())
            if words and cap / len(words) >= 0.6:
                return False
    # 必须与 AI / 大模型主题相关，剔除云平台无关产品噪声
    if not AI_CONTEXT.search(s):
        return False
    return True


def extract_evidence(pages: Iterable[PageResult]) -> dict[str, list[Snippet]]:
    """
    从已抓取页面文本中按 KEYWORD_GROUPS 提取证据片段。
    只摘录页面原文行（事实陈述、与 AI 相关），不生成主观结论；
    同一条引文跨组不重复；含数字 / 金额的高信号行排在前面。
    """
    evidence: dict[str, list[Snippet]] = {key: [] for key, _, _ in KEYWORD_GROUPS}
    seen: dict[str, set[str]] = {key: set() for key, _, _ in KEYWORD_GROUPS}
    used_globally: set[str] = set()

    for page in pages:
        if not page.ok or not page.text:
            continue
        for raw_line in page.text.split("\n"):
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            if len(raw_line) <= 240:
                line_parts = [raw_line]
            else:
                # 文档站常把多个句子拼在一行：按句末标点切成 ≤240 字的片段，
                # 逐句判定，避免一整段事实因为超长被整体丢弃
                segments = re.split(r"(?<=[。！？!?；;])", raw_line)
                line_parts, buf = [], ""
                for seg in segments:
                    if not seg:
                        continue
                    if len(buf) + len(seg) <= 240:
                        buf += seg
                    else:
                        if buf:
                            line_parts.append(buf)
                        buf = seg[:240]
                if buf:
                    line_parts.append(buf)
            for line in line_parts:
                line = line.strip()
                if not line or not _is_fact_line(line):
                    continue
                low = line.lower()
                for key, _label, keywords in KEYWORD_GROUPS:
                    if len(evidence[key]) >= 6:  # 先多收集，排序后裁剪
                        continue
                    if any(_kw_hit(kw, low) for kw in keywords):
                        sig = re.sub(r"\s+", "", line)[:80]
                        if sig in seen[key] or sig in used_globally:
                            continue
                        seen[key].add(sig)
                        used_globally.add(sig)
                        snippet = line if len(line) <= 180 else line[:177] + "…"
                        evidence[key].append(Snippet(
                            text=snippet, url=page.final_url or page.url,
                            stype=page.stype))

    # 含数量/金额的行优先，每组最多保留 3 条
    for key in evidence:
        evidence[key].sort(
            key=lambda sn: (0 if _HAS_QUANTITY.search(sn.text) else 1, len(sn.text)))
        evidence[key] = evidence[key][:3]
    return evidence


# ---------------------------------------------------------------------------
# 博客 / 动态文章提取（RSS/Atom 解析 + HTML 文章链接启发式提取）
# ---------------------------------------------------------------------------

# 正文 / 锚文本中可能出现的日期写法（ISO、中文、英文月份）
# 日期分隔符片段：单位符号（年 / 月 / 日、-、/、.）**两侧都允许空白** ——
# 「2026 年 7 月 31 日」「2026年7月31日」「2026-07-31」都要认。
# 抽成共享片段是因为此前各处正则写法不一：只有 _PROMO_DATE_PAT 写成 `\s*[-/年.]\s*`，
# 其余写成 `[-/年.]\s?`（只容忍单位**后**的空格），于是带前导空格的写法在别处全部漏判 ——
# MiniMax 发布说明的目录锚点（`<a href="#2026-年-7-月-31-日">2026 年 7 月 31 日</a>`）
# 因此没被「标题就是日期」的守卫拦住，被当成文章收进归档。
_DATE_SEP_YM = r"\s*[-/年.]\s*"   # 年 与 月 之间
_DATE_SEP_MD = r"\s*[-/月.]\s*"   # 月 与 日 之间

_INLINE_DATE_RE = re.compile(
    r"(20\d{2}" + _DATE_SEP_YM + r"\d{1,2}" + _DATE_SEP_MD + r"\d{1,2}\s*日?|"
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2},?\s+20\d{2}|"
    r"\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?,?\s+20\d{2})",
    re.I)
_MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def _drop_future_date(day: str) -> str:
    """丢弃晚于今天的日期（返回空串）。

    页面卡片上的日期可能是错的：实测 cohere 一篇 **7 月 10 日**的文章，卡片上印的是
    "Dec 10, 2026"，于是它被当作未来日期排到归档 md 与 README 的最前面（一挂就是几个月，
    归档里已就地修正）。归档按 URL 增量合并、**不会自我纠正**，所以错误日期一旦写进去
    就永久留存 —— 必须在入口拦住。

    只丢日期、保留条目：没有日期只是排到末尾，条目本身不该因为卡片印错日期而消失
    （RSS 侧还有一层同样的兜底，两处都不能少：这里是防污染归档，那里是防污染订阅流）。
    """
    if not day:
        return ""
    if day > datetime.now().strftime("%Y-%m-%d"):
        print(f"      [warn] 丢弃未来日期 {day}（源页面日期有误，条目保留为无日期）",
              file=sys.stderr)
        return ""
    return day


def normalize_feed_date(raw: str) -> str:
    """把 RSS/Atom 或正文中的日期字符串归一化为 YYYY-MM-DD；失败返回空串。"""
    if not raw:
        return ""
    raw = raw.strip()
    # RSS pubDate（RFC822）："Tue, 08 Sep 2026 12:00:00 GMT"
    try:
        dt = parsedate_to_datetime(raw)
        if dt and dt.year >= 2000:
            return dt.strftime("%Y-%m-%d")
    except (TypeError, ValueError):
        pass
    # Atom updated/published（ISO 8601）："2026-09-08T12:00:00Z"
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if dt.year >= 2000:
            return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass
    m = re.search(r"(20\d{2})" + _DATE_SEP_YM + r"(\d{1,2})" + _DATE_SEP_MD + r"(\d{1,2})", raw)
    if m:
        try:
            return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
        except ValueError:
            pass
    m = re.search(
        r"(?i)(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+"
        r"(\d{1,2}),?\s+(20\d{2})", raw)
    if m:
        mon = _MONTHS.get(m.group(1)[:3].lower())
        if mon:
            try:
                return f"{int(m.group(3)):04d}-{mon:02d}-{int(m.group(2)):02d}"
            except ValueError:
                pass
    return ""


def parse_feed_xml(raw: str, base_url: str, stype: str = "feed") -> list[Article]:
    """解析 RSS 2.0 / Atom 订阅源，返回文章列表（保持源内顺序，通常最新在前）。"""
    articles: list[Article] = []
    if not raw or "<" not in raw[:500]:
        return articles
    # GitHub 提交式 feed：标题是 commit message，需要另行整理（见 _clean_commit_title）
    commit_feed = "github.com" in (base_url or "") and "/commits/" in (base_url or "")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return articles

    root_tag = root.tag.rsplit("}", 1)[-1].lower()
    if root_tag in ("rss", "rdf"):
        want = "item"
    elif root_tag == "feed":
        want = "entry"
    else:
        want = "item_or_entry"
    items = [e for e in root.iter()
             if e.tag.rsplit("}", 1)[-1].lower()
             in (("item", "entry") if want == "item_or_entry" else (want,))]

    seen: set[str] = set()
    for item in items:
        title = ""
        link = ""
        date_raw = ""
        desc_raw = ""
        for child in item:
            tag = child.tag.rsplit("}", 1)[-1].lower()
            if tag == "title" and not title and (child.text or "").strip():
                title = re.sub(r"\s+", " ", html_mod.unescape(child.text)).strip()
            elif tag in ("description", "summary", "content", "encoded") \
                    and not desc_raw:
                desc_raw = child.text or ""
            elif tag == "link":
                href = (child.get("href") or "").strip()
                rel = (child.get("rel") or "alternate").strip()
                if href and rel == "alternate" and not link:
                    link = href
                elif (child.text or "").strip() and not link:
                    link = child.text.strip()
            elif tag in ("pubdate", "published", "updated", "date") and not date_raw:
                date_raw = (child.text or "").strip()
        if not link:
            for child in item:
                if child.tag.rsplit("}", 1)[-1].lower() == "guid" \
                        and (child.text or "").strip().startswith("http"):
                    link = child.text.strip()
                    break
        link = urljoin(base_url, link) if link else ""
        # 标题写成「日期 + 栏目」时（DigitalOcean 发布记录），真标题在 description 里
        title = _feed_title_from_description(title, desc_raw)
        if commit_feed:
            title = _clean_commit_title(title)
        if not title or not link.startswith("http") or link in seen:
            continue
        # 拿不到真标题、只剩一个日期的条目直接丢弃 —— 产出纯日期条目等于什么都没说
        if _is_date_only_title(title):
            continue
        seen.add(link)
        articles.append(Article(
            title=title, url=link, date=normalize_feed_date(date_raw),
            source="RSS/Atom 订阅源", stype=stype))
    return articles


def fetch_feed_articles(session: requests.Session, url: str,
                        stype: str = "feed",
                        timeout: tuple[float, float] = (8.0, 20.0)
                        ) -> list[Article]:
    """抓取一个 RSS/Atom 订阅 URL 并解析文章；任何异常返回空列表。"""
    try:
        resp = session.get(url, timeout=timeout, allow_redirects=True)
        if resp.status_code >= 400:
            return []
        if not resp.encoding or resp.encoding.lower() in ("iso-8859-1", "ascii"):
            resp.encoding = resp.apparent_encoding or resp.encoding
        return parse_feed_xml(resp.text, resp.url, stype=stype)
    except requests.RequestException:
        return []


# HTML 博客页文章链接的路径特征：/blog/<slug>、/news/<slug>、/updates/... 等
_ARTICLE_PATH_HINTS = re.compile(
    r"/(blog|blogs|news|updates|changelog|announcements?|posts?|articles?|"
    r"engineering|research|release-notes)(/|$)|/news/news\d{6}", re.I)
_SECTION_ROOT = re.compile(
    r"^/(blog|blogs|news|updates|changelog|announcements?|posts?|articles?|"
    r"engineering|research|release-notes)/?$", re.I)
_BAD_ARTICLE_PATH = re.compile(
    r"/(tag|tags|category|categories|author|authors|page|archive|archives|"
    r"topic|topics|series|search|feed|rss|atom)(/|$)", re.I)
# 博客栏目分类页（非文章详情）：如 /blog/products/api-management
_CATEGORY_PAGE = re.compile(
    r"^/(blog|blogs|news|updates|changelog|announcements?|posts?|articles?|"
    r"engineering|research|release-notes)/(products?|topics?|categories?|"
    r"tags?|industries?)(/[a-z0-9-]+)?/?$", re.I)
# 栏目名与标题粘连时切开（"PartnershipGroq..." / "LearningThe new..."）：
# 信号为「小写/右括号紧跟大写+小写」的词中边界；但驼峰品牌名（GroqCloud/DeepSeek）
# 内部也有该边界，故仅当前缀是已知栏目词/栏目短语或含 & 等标签符号时才切。
_GLUED_LABEL = re.compile(r"[a-z)&][A-Z][a-z]")
# 标题尾部粘连的作者署名（"...this month By Andrea Moran" / "...monthBy Andrea Moran"）
_AUTHOR_SUFFIX = re.compile(r"(?<=[a-z0-9\s])By [A-Z][a-zA-Z.]+(?: [A-Z][a-zA-Z.]+)?$")
# 尾部阅读时长（"• 27-minute read"）与残缺 "By"
_READ_TIME_SUFFIX = re.compile(r"[\s•·|·\-–]*\d+\s*-?\s*min(?:ute)?s?\s*read\s*$", re.I)
_DANGLING_BY = re.compile(r"[\s•·|,\-–]*By\s*$")
# 单词式栏目名（粘连时整体作为前缀出现）
_LABEL_WORDS = {
    "newsroom", "partnership", "partnerships", "platform", "research",
    "blog", "news", "company", "product", "products", "customer", "customers",
    "event", "events", "technical", "engineering", "announcement",
    "announcements", "press", "insights", "technology", "solutions",
}
# 多词式栏目短语（GCP 等博客卡片的分类标签）
_LABEL_PHRASES = {
    "ai & machine learning", "security & identity", "data analytics",
    "smart analytics", "infrastructure modernization", "application development",
    "application modernization", "business application platform",
    "cloud migration", "devops & sre", "storage & data transfer",
    "containers & kubernetes", "management tools", "developers & practitioners",
    "startup ecosystem", "inside google cloud", "google cloud events",
    "training & certifications", "customer stories", "partners & customer stories",
    "global infrastructure", "hybrid & multicloud", "data management & databases",
    "api management & ecosystems", "productivity & collaboration",
    "industries", "networking", "databases", "compute", "serverless",
    "sustainability", "security", "infrastructure",
}


def _strip_glued_label(title: str) -> str:
    """剥离粘在标题前/后的栏目名、作者名、阅读时长等卡片噪声。"""
    title = _READ_TIME_SUFFIX.sub("", title)
    title = _AUTHOR_SUFFIX.sub("", title)
    title = _DANGLING_BY.sub("", title)
    for _ in range(3):
        m = _GLUED_LABEL.search(title)
        if not m or not (4 <= m.start() + 1 <= 40):
            break
        prefix = title[:m.start() + 1].strip()
        if not re.fullmatch(r"[A-Za-z0-9&;,\s\-–|·•.]+", prefix):
            break
        low = prefix.lower()
        cut_ok = (
            "&" in prefix or ";" in prefix
            or low in _LABEL_PHRASES
            or low in _LABEL_WORDS
            or low.rstrip("s") in _LABEL_WORDS
        )
        if not cut_ok:
            break
        title = title[m.start() + 1:]
        title = _READ_TIME_SUFFIX.sub("", title)
        title = _AUTHOR_SUFFIX.sub("", title)
        title = _DANGLING_BY.sub("", title)
    return title.strip(" -–|·•\t")
# 锚文本为通用词（非文章标题）时，需要抓文章页补全标题
_GENERIC_ARTICLE_TITLE = re.compile(
    r"^(this documentation|documentation|docs|learn more|read more|view details|"
    r"see more|more|jump to (content|main|navigation)|查看详情|查看更多|了解更多|"
    r"阅读更多|详情|更多|文档(链接)?|点击查看|详见(文档|链接)?)$", re.I)
# 补全到的标题其实是文档指南页（说明该链接已失效/被站点回退到默认文档），丢弃
_DOCISH_TITLE = re.compile(
    r"^(your first |quick\s?start|getting started|introduction|overview|"
    r"api reference|documentation|docs?\b|readme|authentication|hello world|"
    r"make your first|frequently asked|faq\b|error codes?|rate limits?|"
    r"pricing|contact us|sign in|log in)", re.I)



# 单条变更日志标题上限：官方公告常用一整句话作标题（如 Kimi 模型下线公告达 118
# 字），故放宽到 200；超出时截尾补省略号，避免硬切在句中产生残句。
CHANGELOG_TITLE_MAX = 200


def _cap_changelog_title(title: str) -> str:
    """折叠空白并按 CHANGELOG_TITLE_MAX 截长，超长时以省略号收尾。"""
    title = re.sub(r"\s+", " ", title).strip()
    if len(title) > CHANGELOG_TITLE_MAX:
        return title[:CHANGELOG_TITLE_MAX - 1].rstrip() + "…"
    return title


def _is_date_only_title(title: str) -> bool:
    """整条标题就是日期 / 数字的（`2026 年 7 月 31 日`、`2026年9月`、`2026-07-31`）→ 不是标题。

    这类「标题」来自日期分节标题或目录锚点（MiniMax 发布说明的目录、Kimi 的月份分节），
    看着像动态、实际一条内容都没有。链接分支与 changelog 分支都要用，所以抽成一处 ——
    同一个判断分两处写迟早漂移（链接分支先加了这条守卫，changelog 分支漏了，
    于是 Kimi 的月份标题照旧进归档）。
    """
    return bool(re.fullmatch(r"[\d\s\-/.年月日]+", title or ""))


# 分节标题「**以日期开头、且日期之后还有条目名**」（小米 MiMo 更新日志：
# `<h2 id="2026-09-22-…">2026-09-22 MiMo-V2.6 系列发布</h2>`）。
# 与 `_is_date_only_title` 互补：那条判「整串只有日期」，这条判「日期 + 标题」。
# ⚠️ 必须要求**以日期开头**：否则 `时间-2026-09-10`（DeepSeek 中文页的锚点文本）
# 这类「前缀 + 日期」会被误当成条目名，把原本可用的正文首行标题顶掉。
_DATE_LEADING_HEADING = re.compile(
    r"^\s*20[2-3]\d\s*[-/年.]\s*\d{1,2}(?:\s*[-/月.]\s*\d{1,2})?\s*日?\s*\S")

# 表格表头 / 栏目名：本身是「标题」但零信息量。出现在把**表格表头当成正文首行**的
# 页面上（快手 StreamLake「产品更新公告」的正文就是一张表）。
# ⚠️ 表头是**一整行**，拍平后是「更新时间功能模块功能说明」这种拼接串，所以不能只做
# 整串精确匹配（那样一条都拦不住，实测就是这么漏的）—— 按词表逐词剥离，剥空即命中。
_TABLE_HEADER_WORDS = (
    "更新时间", "更新内容", "更新说明", "更新记录", "发布时间", "发布日期", "上线时间",
    "功能模块", "功能说明", "功能描述", "帮助文档", "文档链接",
    "模块", "说明", "备注", "序号", "类型", "名称", "详情", "链接",
)


def _is_table_header_title(title: str) -> bool:
    """标题是否只是**表格表头 / 栏目名**的拼接（`更新时间功能模块功能说明`）。"""
    t = re.sub(r"[\s\u200b]+", "", title or "")
    if not t:
        return False
    for word in _TABLE_HEADER_WORDS:
        t = t.replace(word, "")
    return not t


# RSS 标题实为「日期 + 栏目」的形式（DigitalOcean 发布记录：
# `17 September 2026 (postgresql, mysql)` / `2026 年 9 月 17 日（postgresql、mysql）`）。
_FEED_DATE_META_TITLE = re.compile(
    r"^\s*(?:"
    r"\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}"
    r"|\d{4}\s*[-/年.]\s*\d{1,2}\s*[-/月.]\s*\d{1,2}\s*日?"
    r"|\d{4}\s*[-/年.]\s*\d{1,2}\s*月?"
    r")\s*(?:[（(][^）)]*[）)])?\s*$",
    re.I)
# 纯 `vendor/model` 形态的模型 ID（PPIO 模型清单页的锚点：`qwen/qwen3-14b`）：
# 那是目录条目而不是动态，且标题本身没有任何可读信息。
_MODEL_ID_TITLE = re.compile(r"^[A-Za-z0-9][\w.\-]*(?:/[A-Za-z0-9][\w.\-]*)+$")


def _feed_title_from_description(title: str, desc: str,
                                 limit: int = 120) -> str:
    """RSS 标题是「日期 + 栏目」时，改用 <description> 的首句当标题。

    DigitalOcean 的发布记录 RSS 把标题写成 `17 September 2026 (postgresql, mysql)`，
    真正的变更说明在 description 里（「PostgreSQL Advanced Edition … are now
    generally available.」）。只取 <title> 会得到 100 条纯日期条目 ——
    看着像动态、实际一条内容都没有。取不到描述时原样返回，交给
    `_is_date_only_title()` 丢弃。
    """
    if not _FEED_DATE_META_TITLE.match(title or ""):
        return title
    text = html_mod.unescape(re.sub(r"<[^>]+>", " ", desc or ""))
    text = re.sub(r"[\u200b\s]+", " ", text).strip()
    if not text:
        return title
    m = re.search(r"^(.{12,}?[。.!?])(?:\s|$)", text)
    picked = (m.group(1) if m else text).strip(" -–|·•。.")
    if len(picked) > limit:
        picked = picked[:limit].rstrip() + "…"
    return picked if len(picked) >= 12 else title


# GitHub 提交式 feed 的标题就是 commit message（Groq 把 changelog 放在
# github.com/groq/groq-changelog，页面上的「RSS」指向 commits/main.atom）：
# `Add Kimi K2 0905 + Compound (#15)` / `chore: GitHub Terraform: …`。
_COMMIT_TITLE_SUFFIX = re.compile(r"\s*\(#\d+\)\s*$")
_COMMIT_PREFIX = re.compile(
    r"^(?:chore|fix|feat|docs|ci|refactor|test|style|build|perf|revert)"
    r"\s*[:：(]\s*", re.I)
# 剥掉前缀后仍然没有实质内容的维护性提交
_COMMIT_NOISE = re.compile(
    r"^(?:add|update|updates?)\s*(?:updates?|changelog)?$|^yay\b|^initial commit$|"
    r"^merge\b|^bump\b|^wip\b|^minor\b|^misc\b|^tweak", re.I)
# 仓库自身的维护提交（改 CI / 依赖 / 发布流程）：不是产品变更，不该进 changelog
_COMMIT_MAINT = re.compile(
    r"github terraform|\.github/|workflows?/|dependabot|renovate|stale\.ya?ml", re.I)


def _clean_commit_title(title: str) -> str:
    """整理 commit message 式标题；纯维护性提交返回空串（由调用方丢弃）。

    Groq 的变更日志托管在 GitHub 仓库，页面上那个「RSS」链接指向
    `github.com/groq/groq-changelog/commits/main.atom`，解析出来的「标题」是
    commit message（`add updates (#17)`、`yay first ever groq changelog entry (#1)`）。
    去掉 PR 编号与 conventional-commit 前缀后仍有内容的才留（如
    `Add prompt caching (#14)` → `Add prompt caching`）。
    """
    t = _COMMIT_TITLE_SUFFIX.sub("", title or "").strip()
    t = _COMMIT_PREFIX.sub("", t).strip()
    if not t or _COMMIT_NOISE.match(t) or _COMMIT_MAINT.search(t):
        return ""
    return t


def extract_changelog_sections(page: PageResult, max_items: int = 100) -> list[Article]:
    """从单页文档/变更日志（如 Mintlify、Docusaurus、GitBook 等）的日期标题或更新容器中提取文章列表。"""
    raw = page.raw or page.text
    if not raw:
        return []
    base_url = page.final_url or page.url
    articles: list[Article] = []
    seen: set[str] = set()

    def _clean_html_text(html_chunk: str) -> list[str]:
        s = re.sub(r"<(?:p|li|h[1-6]|div|br|tr)[^>]*>", "\n", html_chunk, flags=re.I)
        s = re.sub(r"<[^>]+>", "", s)
        lines = []
        for l in s.split("\n"):
            clean = re.sub(r"[\u200b\s]+", " ", l).strip(" \t\n-–|·•")
            if clean and len(clean) >= 3:
                lines.append(clean)
        return lines

    # 结构 1：Mintlify / BigModel 式 update-container（<div class="...update-container" id="2026-08-26">）
    if "update-container" in raw:
        matches = re.findall(
            r"<div[^>]+class=[\"'][^\"']*update-container[^\"']*[\"'][^>]+id=[\"']([^\"']+)[\"'][^>]*>(.*?)(?=<div[^>]+class=[\"'][^\"']*update-container|$)",
            raw, re.S
        )
        for hid, content in matches:
            dm = re.search(r"(\d{4})" + _DATE_SEP_YM + r"(\d{1,2})(?:" + _DATE_SEP_MD + r"(\d{1,2}))?", hid)
            norm_date = _drop_future_date(
                f"{dm.group(1)}-{int(dm.group(2)):02d}-{int(dm.group(3) or 1):02d}" if dm else "")
            lines = _clean_html_text(content)
            title = lines[0] if lines else hid
            # 第一行是日期分节标题（`2026年9月` 这类**只写年月**的也算 —— 原先的判据
            # `\d{4}年\d{1,2}(月\d{1,2})?` 匹配不上它，于是 Kimi 的标题就停在月份上，
            # 归档 26 条里 24 条是「2026年9月」这种没有内容的月份名）。真标题在下一行。
            if _is_date_only_title(title):
                title = lines[1] if len(lines) > 1 else title
            url = f"{base_url.split('#')[0]}#{quote(hid)}"
            if url not in seen and len(title) >= 3:
                seen.add(url)
                articles.append(Article(title=_cap_changelog_title(title), url=url, date=norm_date, source="官方更新日志", stype=page.stype))
        if articles:
            return articles[:max_items]

    # 结构 4：**日期分节 + 子标题条目**（Kimi 平台发布记录：`<h2 id="2026年9月">2026年9月</h2>`
    # 之下是一串 `<h3>`，每个 h3 才是一条真条目 —— 如「🤖 Kimi 托管智能体（Hosted Agents）Beta 上线」）。
    # 不认这层结构时抓到的是**月份标题**：实测归档 26 条里 24 条是「2026年9月」这种，
    # 看着像动态、实际一条内容都没有。
    # 放在结构 2 之前：它更具体（要求「日期分节 + 更深的子标题」同时成立），
    # 而 Gemini / MiniMax / PPIO 那些日期标题下面是正文而不是子标题，不会命中。
    if not articles:
        heads = list(re.finditer(
            r"<(h[2-4])[^>]*id=[\"']([^\"']+)[\"'][^>]*>(.*?)</\1>", raw, re.S | re.I))
        sec_date, sec_level = "", 9
        rows4: list[Article] = []
        seen4: set[str] = set()
        for hm in heads:
            level = int(hm.group(1)[1])
            lines4 = _clean_html_text(hm.group(3))
            text = lines4[0] if lines4 else ""
            if not text:
                continue
            # 日期分节标题：`2026年9月` / `2026 年 9 月 17 日` / `2026-09-17` 都算
            dm4 = re.search(
                r"(20[2-3]\d)\s*[-/年.]\s*(\d{1,2})(?:\s*[-/月.]\s*(\d{1,2}))?", text)
            if dm4 and _is_date_only_title(text):
                sec_date = _drop_future_date(
                    f"{dm4.group(1)}-{int(dm4.group(2)):02d}-{int(dm4.group(3) or 1):02d}")
                sec_level = level
                continue
            if not sec_date or level <= sec_level:
                continue  # 与分节同级或更浅的标题不是它的条目
            url4 = f"{base_url.split('#')[0]}#{quote(hm.group(2))}"
            if url4 in seen4:
                continue
            seen4.add(url4)
            rows4.append(Article(title=_cap_changelog_title(text), url=url4, date=sec_date,
                                 source="官方更新日志", stype=page.stype))
        if len(rows4) >= 3:
            return rows4[:max_items]

    # 结构 5：**日期分节 + 列表项条目**（PPIO 发版记录：日期区间标题之下是一组 `<li>`，
    # 每个 li 的**第一个 `<strong>`** 才是条目名 —— 如「部分多模态模型计划下线」。
    # 只取到分节标题旁的栏目名（「模型调整 🔧」）没有信息量，等于把内容丢了。
    # 同样放在结构 2 之前：结构 2 会把这种页面按「一节一条」处理，只留下栏目名。
    if not articles:
        heads5 = list(re.finditer(
            r"<(h[2-4])[^>]*id=[\"']([^\"']+)[\"'][^>]*>(.*?)</\1>", raw, re.S | re.I))
        sec_date5 = ""
        rows5: list[Article] = []
        seen5: set[str] = set()
        for idx5, hm5 in enumerate(heads5):
            lines5 = _clean_html_text(hm5.group(3))
            text5 = lines5[0] if lines5 else ""
            dm5 = re.search(
                r"(20[2-3]\d)\s*[-/年.]\s*(\d{1,2})(?:\s*[-/月.]\s*(\d{1,2}))?", text5)
            if not (dm5 and _is_date_only_title(text5)):
                continue
            sec_date5 = _drop_future_date(
                f"{dm5.group(1)}-{int(dm5.group(2)):02d}-{int(dm5.group(3) or 1):02d}")
            nxt = heads5[idx5 + 1].start() if idx5 + 1 < len(heads5) else len(raw)
            section = raw[hm5.end():nxt]
            for li_idx, li in enumerate(re.findall(r"<li[^>]*>(.*?)</li>", section, re.S | re.I)):
                strong5 = re.search(r"<strong[^>]*>(.*?)</strong>", li, re.S | re.I)
                title5 = re.sub(r"<[^>]+>", "", strong5.group(1)).strip() if strong5 else ""
                title5 = re.sub(r"[\u200b\s]+", " ", title5).strip(" \t\n-–|·•")
                if not title5 or _is_date_only_title(title5) or len(title5) < 4:
                    continue
                # 同一条公告的子要点也是 li：PPIO「Playground 支持 Function Call」
                # 之下还有「智能交互 ：在对话页面…」「三大优势 ： ⚡ 更强时效性」，
                # 特征是**纯中文短词 + <strong> 后紧跟分隔符**（真条目不会这样，
                # 它是「条目名 说明正文」）。不区分的话这些营销短语会各自变成一条。
                after5 = re.sub(r"<[^>]+>", "", li[strong5.end():]) if strong5 else ""
                after5 = re.sub(r"[\u200b\s]+", " ", after5).strip()
                if (len(title5) < 8 and not re.search(r"[A-Za-z0-9]", title5)
                        and re.match(r"^[：:—–\-|·]", after5)):
                    continue
                # li 没有自己的锚点，用「分节 id + 序号」合成一个稳定的 fragment，
                # 保证归档增量合并能认回同一条（改了就变成新增）。
                url5 = f"{base_url.split('#')[0]}#{quote(hm5.group(2))}-{li_idx + 1}"
                if url5 in seen5:
                    continue
                seen5.add(url5)
                rows5.append(Article(title=_cap_changelog_title(title5), url=url5,
                                     date=sec_date5, source="官方更新日志", stype=page.stype))
        if len(rows5) >= 3:
            return rows5[:max_items]

    # 结构 2：标题日期锚点式变更日志（<h2/h3 id="2026...">）。
    # id 允许日期前有短前缀（如 DeepSeek 中文页 h2 id="时间-2026-09-10"），
    # 故不要求 id 以年份开头；年-月、月-日间的非数字分隔限 3 字符以内，
    # 避免把 model-2025-rc1 之类的版本号误解析成日期。
    date_id_pat = r"[^\"']*20[2-3]\d[^\"']*"
    matches_h = list(re.finditer(
        r"<(h[23])[^>]*id=[\"'](" + date_id_pat + r")[\"'][^>]*>(.*?)</\1>"
        r"(.*?)(?=<(?:h[23])[^>]*id=[\"']" + date_id_pat + r"|$)",
        raw, re.S
    ))
    for m in matches_h:
        hid = m.group(2)
        head_html = m.group(3)
        body = m.group(4)
        # id 里的日期有两种写法，都要认：
        #   YYYY-MM-DD / `2026 年 7 月 31 日`（DeepSeek、MiniMax…）
        #   **MM-DD-YYYY**（Mintlify 系文档站：Gemini API changelog 的 `id="09-17-2026"`）
        # 后者原先解析不出日期 → 下面 `if not norm_date: continue` 把条目**全部丢弃**
        # （实测那一页 113 个日期标题一条都没进来）。月份/日做范围校验，避免把
        # `model-2025-rc1` 这类版本号当日期。
        dm = re.search(r"(20[2-3]\d)\D{1,3}(\d{1,2})(?:\D{0,3}(\d{1,2}))?", hid)
        norm_date = ""
        if dm:
            norm_date = _drop_future_date(
                f"{dm.group(1)}-{int(dm.group(2)):02d}-{int(dm.group(3) or 1):02d}")
        else:
            dm2 = re.search(r"(?<!\d)(\d{1,2})\D{1,3}(\d{1,2})\D{1,3}(20[2-3]\d)(?!\d)", hid)
            if dm2 and 1 <= int(dm2.group(1)) <= 12 and 1 <= int(dm2.group(2)) <= 31:
                norm_date = _drop_future_date(
                    f"{dm2.group(3)}-{int(dm2.group(1)):02d}-{int(dm2.group(2)):02d}")

        # 标题三选一：分节标题自带条目名 > 卡片标题 > 正文首行
        head_lines = _clean_html_text(head_html)
        head_text = head_lines[0] if head_lines else ""
        # 检查卡片标题（MiniMax 等卡片式组件）
        card_m = re.search(r"data-component-part=[\"']card-title[\"'][^>]*>(.*?)</h[23]>", body, re.S)
        if card_m:
            model_name = re.sub(r"<[^>]+>", "", card_m.group(1)).strip(" \u200b\t\n")
            # 标题**只取名称**，卡片正文（data-component-part="card-content"）不再并进来：
            # 拼成的中位标题有 145 字，订阅列表里根本没法扫读；正文点进链接就能看到。
            title = model_name
        elif _DATE_LEADING_HEADING.match(head_text):
            # 分节标题本身就写着条目名时**直接用它** —— 比正文首行准得多。
            # 不认这一层时，标题会变成正文整段（实测小米 MiMo 抓成
            # 「mimo-v2.6-pro： 最强大的旗舰推理模型，全模态、超高性能、万亿参数的旗舰推理模型…」，
            # 其余几条则是没有信息量的「模型简介：」）。
            title = head_text
        else:
            lines = _clean_html_text(body)
            title = lines[0] if lines else hid
            # 同上：首行是日期分节标题时，真标题在下一行
            if _is_date_only_title(title):
                title = lines[1] if len(lines) > 1 else title

        # 正文首行只是**表格表头 / 栏目名**时，它不是标题 —— 跳过这一条，
        # 交给后面的表格结构处理。快手 StreamLake 的「产品更新公告」正文是表格，
        # 不拦的话归档里全是「更新时间功能模块功能说明」这种零信息条目。
        if _is_table_header_title(title):
            continue

        title = re.sub(r"[\u200b\s]+", " ", title).strip(" \t\n-–|·•")
        url = f"{base_url.split('#')[0]}#{quote(hid)}"
        # id 中年份可能只是版本号片段（如 model-2025-rc1）：解析不出完整
        # 年月的标题不是日期锚点，跳过
        if not norm_date:
            continue
        if url not in seen and len(title) >= 3:
            seen.add(url)
            articles.append(Article(title=_cap_changelog_title(title), url=url, date=norm_date, source="官方更新日志", stype=page.stype))

    # 结构 3：帮助中心表格行式动态（如阿里云百炼「模型上下架与更新」：
    # 每行 = 类型 | 时间(YYYY-MM-DD) | <code>模型ID</code> | 功能说明）。
    # 严格守卫：同行必须同时含 ISO 日期格与 <code> 模型 ID，且全页 ≥3 行
    # 才采用，避免在普通表格页上误报。
    if not articles:
        base_no_frag = base_url.split("#")[0]
        table_rows: list[Article] = []
        row_seen: set[str] = set()
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", raw, re.S | re.I):
            cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S | re.I)
            if len(cells) < 3:
                continue
            date_m = re.search(r">((20[2-3]\d)-(\d{1,2})-(\d{1,2}))<", tr)
            code_m = re.search(r"<code[^>]*>(.*?)</code>", tr, re.S | re.I)
            if not date_m or not code_m:
                continue
            model_id = re.sub(r"<[^>]+>", "", code_m.group(1))
            model_id = re.sub(r"[​\s]+", "", model_id).strip("`")
            # 功能说明列既用于**校验这是一行真条目**（空说明的行多半是表头残留），
            # 也用来补全标题：整段拼进来太长（中位 145 字），只取**首句**。
            desc = re.sub(r"<[^>]+>", "", cells[-1])
            desc = re.sub(r"[​\s]+", " ", desc).strip()
            if not model_id or not desc:
                continue
            norm_date = _drop_future_date(
                f"{int(date_m.group(2)):04d}-"
                f"{int(date_m.group(3)):02d}-{int(date_m.group(4)):02d}")
            # 标题只写模型 ID（`qwen3.8-max-0902`）没有任何信息量：补上说明的首句，
            # 既保留可检索的 ID，又让订阅列表能看出这是什么模型。
            first = re.split(r"[。！？!?]", desc, maxsplit=1)[0].strip()
            title = f"{model_id}：{first}" if first else model_id
            url = f"{base_no_frag}#{quote(model_id)}"
            if url in row_seen:  # 同一模型在多地域表格中重复出现
                continue
            row_seen.add(url)
            table_rows.append(Article(
                title=_cap_changelog_title(title), url=url, date=norm_date,
                source="官方更新日志", stype=page.stype))
        if len(table_rows) >= 3:
            articles = table_rows

    # 结构 7：**表格行式发布记录**（日期列 + 说明列）。
    # 腾讯混元「产品动态」、快手 StreamLake「产品更新公告」都是这种：一行一条更新，
    # 日期与说明各占一列。结构 3 同样处理表格，但它硬性要求行内有 `<code>` 模型 ID
    # （阿里云百炼那种「模型 ID + 功能说明」），这两家没有，于是认不出来。
    # 日期可能只写「8月14日」（无年份）—— 年份从最近的**月份分节标题**
    # （`<h3>发布时间：2026年8月</h3>`）取；取不到年份就丢弃该行，**不猜**。
    if not articles:
        month_marks: list[tuple[int, int]] = []
        for hm in re.finditer(r"<(h[1-4])[^>]*>(.*?)</\1>", raw, re.S | re.I):
            ht = re.sub(r"<[^>]+>", "", hm.group(2))
            ym = re.search(r"(20[2-3]\d)\s*[-/年.]\s*(\d{1,2})", ht)
            # 只认「年 + 月」的分节标题；含完整日期的是条目本身，不是分节
            if ym and not re.search(r"\d{1,2}\s*[-/月.]\s*\d{1,2}", ht):
                month_marks.append((hm.start(), int(ym.group(1))))
        rows7: list[Article] = []
        seen7: set[str] = set()
        for trm in re.finditer(r"<tr[^>]*>(.*?)</tr>", raw, re.S | re.I):
            cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", trm.group(1), re.S | re.I)
            if len(cells) < 2:
                continue
            plain = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", c)).strip(" \u200b")
                     for c in cells]
            norm7 = ""
            for c in plain:
                full = re.search(
                    r"(20[2-3]\d)\s*[-/年.]\s*(\d{1,2})\s*[-/月.]\s*(\d{1,2})", c)
                if full:
                    norm7 = (f"{int(full.group(1)):04d}-{int(full.group(2)):02d}"
                             f"-{int(full.group(3)):02d}")
                    break
                md = re.fullmatch(r"(\d{1,2})\s*[-/月.]\s*(\d{1,2})\s*日?", c)
                if md and 1 <= int(md.group(1)) <= 12 and 1 <= int(md.group(2)) <= 31:
                    year7 = next((y for pos, y in reversed(month_marks)
                                  if pos < trm.start()), 0)
                    if year7:
                        norm7 = (f"{year7:04d}-{int(md.group(1)):02d}"
                                 f"-{int(md.group(2)):02d}")
                        break
            if not norm7:
                continue
            norm7 = _drop_future_date(norm7)
            if not norm7:
                continue
            # 说明列 = 最长的一列（日期列与「功能模块」这类短栏目名都被排除）
            body7 = [c for c in plain
                     if len(c) >= 10 and not re.fullmatch(r"[\d\s\-/月.日]+", c)]
            if not body7:
                continue
            first7 = re.split(r"[。！？!?]", max(body7, key=len), maxsplit=1)[0].strip()
            if len(first7) < 8:
                continue
            url7 = f"{base_url.split('#')[0]}#{quote('t' + norm7 + '-' + str(len(rows7)))}"
            if url7 in seen7:
                continue
            seen7.add(url7)
            rows7.append(Article(title=_cap_changelog_title(first7), url=url7,
                                 date=norm7, source="官方更新日志", stype=page.stype))
        # 同结构 6：规则较宽，至少 3 条才认，免得在普通表格页上误报
        if len(rows7) >= 3:
            articles = rows7

    # 结构 6：**日期 + 其后相邻的标题元素**构成的发布记录。
    # 商汤「发布动态」：`<p><code>2025.07.23</code></p>` 之后紧跟
    # `<h2 id="模型更新…">【模型更新】发布最新版本日日新-融合模态模型…</h2>`
    # （注意 h2 出现在 `<h3>release-202507</h3>` 分节**之后**，层级是倒的，所以
    # 「日期分节 + 更深子标题」的结构 4 认不出来）；
    # 这类页面前几个结构全部落空（结构 3 还要求表格里有 `<code>` 模型 ID）。
    if not articles:
        rows6: list[Article] = []
        seen6: set[str] = set()
        last_date_pos = -10_000
        for dm in _INLINE_DATE_RE.finditer(raw):
            # 同一处日期常被匹配**两次**（`<time datetime="2026-09-22">Sep 22, 2026</time>`
            # 里 ISO 与英文写法各命中一次），不去重就会产出两条一模一样的条目，
            # 而条数一旦够 3 条就会顶掉后面链接分支的正确结果。
            if dm.start() - last_date_pos < 60:
                continue
            last_date_pos = dm.start()
            norm6 = _drop_future_date(normalize_feed_date(dm.group(0)))
            if not norm6:
                continue
            # 日期之后 2000 字符内最近的标题元素 —— 再远就不是同一条了
            hm = re.search(r"<(h[1-4])([^>]*)>(.*?)</\1>", raw[dm.end():dm.end() + 2000],
                           re.S | re.I)
            if not hm:
                continue
            attrs6, inner6 = hm.group(2), hm.group(3)
            title6 = html_mod.unescape(re.sub(r"<[^>]+>", "", inner6))
            title6 = re.sub(r"[\u200b\s]+", " ", title6).strip(" \t\n-–|·•")
            # 标题必须像条目名：够长、且不是又一个日期（`2026年8月` 这类分节标题）
            if len(title6) < 8 or _is_date_only_title(title6):
                continue
            idm6 = re.search(r"id=[\"']([^\"']+)[\"']", attrs6)
            frag6 = idm6.group(1) if idm6 else f"d-{norm6}-{len(rows6)}"
            url6 = f"{base_url.split('#')[0]}#{quote(frag6)}"
            if url6 in seen6:
                continue
            seen6.add(url6)
            rows6.append(Article(title=_cap_changelog_title(title6), url=url6,
                                 date=norm6, source="官方更新日志", stype=page.stype))
        # 至少 3 条才认 —— 这条规则很宽（任何「日期 + 标题」都算），
        # 没有这个下限就会在普通文档页上误报出一两条假条目。
        if len(rows6) >= 3:
            articles = rows6

    return articles[:max_items]


#: 对齐 `PageParser.links` 的收录口径：**带 href 的** `<a>` 才会被 parser 记录。
#: 旧写法 `<a\s` 会把脚本字符串里的 `<a ` 字面量也数进去（实测 claude.com/blog
#: 多 1 个 → 严格计数守卫整体放弃上下文日期，357 条链接的日期全丢）。
_ANCHOR_OPEN_RE = re.compile(r"<a(?=[\s/>])[^>]*\bhref\s*=", re.I)


def _link_context_dates(raw_html: str, links_count: int, window: int = 700) -> list[str]:
    """取每个链接「上下文里的日期」—— 该链接**之前**最近的日期（YYYY-MM-DD）。

    卡片式列表页常把日期放在独立元素里：`x.ai/news` 是
    `<time dateTime="2026-09-22">Sep 22, 2026</time>`、poolside 是
    `<time datetime="2026-05-11">`、cohere 是 `<p>Sep 10, 2026</p>` ——
    锚文本与锚内标题元素里**都没有**日期。只从标题找日期的旧逻辑在这些页面
    8 条里 0 条带日期，于是条目进不了合并流（无日期只进单厂商源，见 write_rss_feeds）。

    对齐方式：按 HTML 里 `<a>` 的出现顺序与 `page.links` 一一对应
    （HTMLParser 是流式的，两者顺序一致）。**数量对不上就整体返回空** ——
    宁可少修几条，也不要错位把上一条的日期安到这一条上。

    ⚠️ 每个日期**只能被一个链接消费**：卡片列表里「有日期的卡」与「没日期的卡」
    交替出现时，不做消费标记会让后者继承前者的日期（实测：一条没有日期的条目
    被安上了上一条的 2026-08-01）。宁可留空，也不要张冠李戴 —— 空日期只是不进
    合并流，错日期则是**静默的错误情报**。
    """
    if not raw_html or links_count <= 0:
        return [""] * max(links_count, 0)
    anchors = [m.start() for m in _ANCHOR_OPEN_RE.finditer(raw_html)]
    if len(anchors) != links_count:
        return [""] * links_count
    spans = [(m.start(), m.group(0)) for m in _INLINE_DATE_RE.finditer(raw_html)]
    used: set[int] = set()
    out: list[str] = []
    for pos in anchors:
        best_idx = -1
        best_text = ""
        for i, (dpos, dtext) in enumerate(spans):
            if dpos > pos:
                break
            if i in used or pos - dpos > window:
                continue
            best_idx, best_text = i, dtext
        if best_idx >= 0:
            # 同一处日期常被匹配**两次**：`<time datetime="2026-09-22">Sep 22, 2026</time>`
            # 里 ISO 与英文两种写法各命中一次。只标记命中的那一个，邻近的那份会被
            # 下一条没有日期的链接捡走（实测就是它让空日期条目拿到上一条的日期），
            # 所以把同一区域（60 字符内）的日期一并标记为已用。
            anchor_pos = spans[best_idx][0]
            for j, (dpos, _dt) in enumerate(spans):
                if abs(dpos - anchor_pos) <= 60:
                    used.add(j)
            out.append(normalize_feed_date(best_text))
        else:
            out.append("")
    return out


_MD_HEAD_RE = re.compile(r"^(#{2,6})\s+(.*?)\s*#*\s*$")
_MD_ENTRY_RE = re.compile(r"^[A-Za-z]*\[([^\]]{3,})\]\(#([^)]*)\)")
_MD_MONTH = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?"
_MD_DATE_DATED = re.compile(
    rf"^(?:20\d{{2}}[-/.年]\s*\d{{1,2}}[-/.月]\s*\d{{1,2}}日?"
    rf"|{_MD_MONTH}\s+\d{{1,2}},?\s+20\d{{2}}"
    rf"|\d{{1,2}}\s+(?:st|nd|rd|thin|th)?\s*{_MD_MONTH}\.?,?\s+20\d{{2}})\s*$", re.I)
_MD_DATE_YEARLESS = re.compile(rf"^({_MD_MONTH})\s+(\d{{1,2}})(?:st|nd|rd|th)?$|^\d{{1,2}}\s+{_MD_MONTH}$",
                               re.I)


def extract_md_changelog(raw: str, base_url: str, stype: str = "changelog",
                         max_items: int = 100, today: str | None = None) -> list[Article]:
    """纯 Markdown 变更日志（Mintlify 文档站 `.md` 端点，实测 groq console changelog.md）。

    页面形态：`---` 分隔 + 日期行 + 多条 `### 分类[标题](#锚点)`。最新分节的日期行
    **省略年份**（`Apr 18`）——变更日志按新→旧排列，未标年份的必是最近一段：按今年解、
    落在未来则回退一年。条目不足 3 条不认（规则宽，防普通 md 文档误报）。
    """
    today = today or datetime.now().strftime("%Y-%m-%d")
    rows: list[Article] = []
    seen: set[str] = set()
    cur = ""

    def _yearless_date(month_txt: str, day: int) -> str:
        mon = _MONTHS.get(month_txt[:3].lower())
        if not mon:
            return ""
        for year in (int(today[:4]), int(today[:4]) - 1):
            cand = f"{year:04d}-{mon:02d}-{day:02d}"
            if cand <= today:
                return cand
        return ""

    for line in raw.splitlines():
        s = line.strip()
        if not s:
            continue
        if _MD_DATE_DATED.match(s):
            cur = _drop_future_date(normalize_feed_date(s))
            continue
        if s.startswith("#"):
            hm = _MD_HEAD_RE.match(s)
            if not hm:
                continue
            text = hm.group(2).strip()
            if _is_date_only_title(text) or _MD_DATE_DATED.match(text):
                continue
            em = _MD_ENTRY_RE.match(text)
            if not em:
                continue
            title, anchor = em.group(1).strip(), em.group(2)
            if not cur or len(title) < 3:
                continue
            url = f"{base_url.split('#')[0]}#{quote(anchor or title)}"
            if url in seen:
                continue
            seen.add(url)
            rows.append(Article(title=_cap_changelog_title(title), url=url,
                                date=cur, source="官方更新日志", stype=stype))
            if len(rows) >= max_items:
                break
        else:
            ym = _MD_DATE_YEARLESS.match(s)
            if ym:
                month_txt, day = (ym.group(1), int(ym.group(2))) if ym.group(1) else (s.split()[1], int(s.split()[0]))
                cur = _yearless_date(month_txt, day)
    return rows if len(rows) >= 3 else []


def extract_articles_from_page(page: PageResult, max_items: int = 8) -> list[Article]:
    """
    从已抓取的博客 / 更新页 HTML 链接中启发式提取文章条目（无 RSS 时的兜底）：
    1) 先尝试从单页文档站的更新日志结构（Mintlify / Docusaurus 容器与日期标题块）中提取；
    2) 提取不到时，从 HTML 链接中启发式提取独立文章页面。
    """
    if not page.ok:
        return []
    raw = page.raw or page.text or ""
    # 纯 Markdown（docs 站 .md 端点，可能以 front-matter `---` 开头）：
    # HTML 结构全部依赖标签，这里走独立分支
    head = raw.lstrip()[:800].lower()
    if head.startswith(("#", "---")) and "<html" not in head \
            and re.search(r"(?m)^#{2,3} ", raw[:4000]):
        return extract_md_changelog(raw, page.final_url or page.url,
                                    stype=page.stype, max_items=100)[:max_items] \
            if (page.stype or "") in NEWS_TYPES else []
    # 1) 单页结构式变更日志解析（Kimi / MiniMax / BigModel 等）
    sections = extract_changelog_sections(page, max_items=max_items)
    if len(sections) >= 2:
        return sections

    if not page.links:
        return []
    base = page.final_url or page.url
    articles: list[Article] = []
    seen: set[str] = set()
    by_norm: dict[str, Article] = {}
    seen_titles: set[str] = set()
    # 长度不一致说明两个列表失配（未来若有人只改一处赋值就会这样）。此时**整体不用**
    # 标题列表、退回原来的锚文本逻辑 —— 宁可少修几条，也不要错位取到别人的标题。
    headings_aligned = page.link_headings if len(page.link_headings) == len(page.links) else []
    # 锚文本与标题元素里都没有日期时，退回「链接上下文里的日期」（<time datetime> 等）
    context_dates = _link_context_dates(page.raw or "", len(page.links))
    for link_idx, (url, anchor) in enumerate(page.links):
        if not url or not url.startswith("http") or not _same_site(url, base):
            continue
        try:
            path = urlparse(url).path or "/"
        except Exception:
            continue
        if _BAD_ARTICLE_PATH.search(path) or _SECTION_ROOT.fullmatch(path):
            continue
        if _CATEGORY_PAGE.fullmatch(path):
            continue
        if not _ARTICLE_PATH_HINTS.search(path):
            continue
        # 卡片式列表页（通义更新日志、MiniMax 发布说明、x.ai/news）把整张卡片包进一个
        # <a>，拍平后的锚文本 = 「标题 + 整段描述」粘成一串（实测通义 100%、xAI 37%、
        # MiniMax 30% 的条目如此）。解析时另存了锚内标题元素（h1-h6）的文本，有就优先用
        # —— 这是结构信息，比事后按标点猜标题可靠。
        # 但标题元素可能过短（如 "Grok 4.6"，会被下面的长度下限滤掉），此时仍退回锚文本，
        # 免得反而把条目丢掉。
        heading = headings_aligned[link_idx] if link_idx < len(headings_aligned) else ""
        source_text = heading if len(heading) >= 10 else (anchor or "")
        title = html_mod.unescape(re.sub(r"\s+", " ", source_text)).strip()
        date = ""
        # DeepSeek 更新日志：URL slug 即日期（/news/news260813 -> 2026-08-13）
        slug_m = re.search(r"/news/news(\d{2})(\d{2})(\d{2})", path, re.I)
        if slug_m:
            date = f"20{slug_m.group(1)}-{slug_m.group(2)}-{slug_m.group(3)}"
        dm = _INLINE_DATE_RE.search(title)
        if dm:
            date = date or normalize_feed_date(dm.group(1))
            title = (title[:dm.start()] + " " + title[dm.end():]).strip(" -–|·•\t")
        if not date:
            date = context_dates[link_idx]
        date = _drop_future_date(date)
        # 剥掉粘连的栏目名 / 作者名（"PartnershipGroq Among..." -> "Groq Among..."）
        title = _strip_glued_label(title)
        title = re.sub(r"\s+", " ", title).strip(" -–|·•")
        if len(title) < 10 or len(title) > 200:
            continue
        # 整条标题就是日期 / 数字的，不是标题 —— MiniMax 发布说明的目录锚点长这样
        # （`<a href="#2026-年-7-月-31-日">2026 年 7 月 31 日</a>`）。只写年月的
        # （`2026 年 4 月`）没有「日」，靠上面的 _INLINE_DATE_RE 剥不干净，这里兜住。
        if _is_date_only_title(title):
            continue
        # 纯模型 ID 形态的锚点（PPIO 模型清单页的 `qwen/qwen3-14b`）是目录条目，丢弃
        if _MODEL_ID_TITLE.match(title):
            continue
        if CTA_NAV.match(title) or NAV_CONCAT.match(title):
            continue
        if not re.search(r"[A-Za-z一-鿿]", title) or title.count("/") >= 3:
            continue
        # 无日期的英文标题需更像标题（首字母大写或含数字），过滤
        # "our latest models" / "jump to content" 这类小写导航残句
        if not date and not re.search(r"[一-鿿]", title):
            if len(title) < 15 or not (title[0].isupper() or re.search(r"[0-9]", title)):
                continue
        norm = _norm_url(url)
        # 单页文档站（如 PPIO 公告页）每条公告是同页 #锚点；_norm_url 会去掉
        # fragment，须把 fragment 纳入去重键，否则同页锚点全被折叠成一个 URL 丢弃
        frag = urlparse(url).fragment.strip().lower()
        if frag:
            norm = norm + "#" + frag
        if norm in seen:
            # 同一个 URL 常在一页里出现两次：首屏 hero 卡片（标题短、无日期）与下方
            # 列表卡片（标题带摘要、有日期）。保留先出现的（标题更干净），但把后来
            # 出现的日期补上 —— 日期决定归档与 RSS 的排序，丢了就再也拿不回来。
            # 实测 cohere 博客页因此有 9 条本可带日期的条目退化成无日期。
            kept = by_norm.get(norm)
            if kept is not None and not kept.date and date:
                kept.date = date
            continue
        # 同页锚点常带 -2/-3 后缀重复同一标题（PPIO 每条公告出现 5 次），按标题去重
        title_key = re.sub(r"\s+", "", title).lower()
        if title_key in seen_titles:
            continue
        seen.add(norm)
        seen_titles.add(title_key)
        art = Article(
            title=title, url=url, date=date,
            source="官方页面文章列表", stype=page.stype)
        articles.append(art)
        by_norm[norm] = art
        if len(articles) >= max_items:
            break
    return articles


# ---------------------------------------------------------------------------
# 动态条目的「情报过滤」
#
# 本仓库主题是**免费额度 / 模型 / 定价**，但不少厂商的 news 源其实是**公司博客**：
# `openai.com/index/*` 里客户案例、融资、政策、教程占绝大多数，`huggingface.co/blog`
# 是社区技术博客。2026-09-22 数据审计：线上 3376 条里 77% 来自这类源，
# 其中 228 条根本不是一篇文章。
#
# 判据按**信号组**组织 —— 同一个词在不同厂商的源里含义不同：
# `fine-tuning` / `embedding` 在 openai 的 news 里是 API 变更信号，
# 在 huggingface 的 blog 里却是技术教程的标题词，所以只有 openai 用 strong 组。
# **未列入 `NEWS_INTEL_SIGNALS` 的厂商不过滤**（变更日志型源结构上就对口）。
#
# 过滤在**翻译之前**执行，标题可能是原文（英文站）也可能是中文（页面本身是中文，
# 如 Anthropic 的若干条目标题）—— 两套词表都要有，否则中文标题会被整类剔除。
NEWS_SIGNAL_STRONG = re.compile(
    r"\b(api|apis|sdk|endpoint\w*|pricing|prices?|rate limits?|rate-limit|usage limits?|"
    r"spend controls?|free tiers?|free plans?|quota|billing|token plan|credits?|"
    r"deprecat\w*|retir\w*|sunset|discontinu\w*|no longer available|end of life|"
    r"system card|model card|changelog|release notes|"
    r"context window|context length|prompt caching|context caching|"
    r"function calling|tool calling|structured output|json mode|webhooks?|"
    r"batch api|parameters?)\b|"
    r"(免费额度|免费套餐|免费层|免费试用|限时免费|永久免费|降价|定价|计费|限速|限流|"
    r"配额|额度|弃用|下线|停止服务|涨价)", re.I)
NEWS_SIGNAL_RELEASE = re.compile(
    r"\b(introducing|announcing|announces|unveil\w*|launch\w*|releas\w*|ships?|"
    r"now available|available (in|on|now|for)|generally available|GA|"
    r"public preview|preview|beta|new models?|next[- ]generation|"
    r"welcome|is here|adds? support|now supports|product updates?)\b|"
    r"(上线|发布|推出|新增|产品介绍|正式发布|现已|产品更新|简介)", re.I)
# 窄口径：出现即说明「有东西上架 / 可用」，不必再要求产品名
# （`Qwen3.8-2.4T-A95B now available on Modal`、`Product updates: VM sandboxes…`）
NEWS_SIGNAL_RELEASE_ANY = re.compile(
    r"\b(now available|available (in|on|now|for)|generally available|GA|is here|"
    r"welcome|adds? support|now supports|public preview|product updates?)\b|"
    r"(现已|正式发布|上线|发布|推出|产品更新)", re.I)
# 标题以「模型名 + 版本号 + 冒号/破折号」开头：
# `GPT-6 Astra: A new generation of intelligence` / `GLM-5.2: Built for Long-Horizon Tasks`
NEWS_SIGNAL_HEADLINE = re.compile(
    r"^\s*(gpt|chatgpt|claude|gemini|gemma|qwen|llama|grok|mistral|codestral|magistral|"
    r"pixtral|deepseek|glm|kimi|minimax|command|nova|granite|phi|falcon|olmo|jamba|"
    r"code llama|stable diffusion|whisper|sora|dall)[- ]?[\d.]*[a-z]*\s*[:\-–—]",
    re.I)
NEWS_PRODUCT = re.compile(
    r"(?<![a-z])(gpt|chatgpt|codex|astra|o1|o3|o4|sora|dall|whisper|claude|gemini|gemma|"
    r"qwen|llama|grok|mistral|codestral|magistral|pixtral|deepseek|glm|kimi|minimax|"
    r"command|nova|granite|phi|falcon|olmo|jamba|realtime|responses api|agents sdk|"
    r"assistants?|agents?|models?|image|images|voice|audio|tts|asr|ocr|vision|embedding|"
    r"kernels?|translate|parse|studio|buckets?|storage|search|retrieval|rerank\w*|"
    r"transcrib\w*|speech|music|video|coder|code|chat|cli|platform|api)(?![a-z])", re.I)
NEWS_NOISE_CUSTOMER = re.compile(
    r"^how\s+\S+\s+(is|are|was|were)\s+\w+ing\b|"
    r"\b(trusts?|relies on|customer stor(y|ies)|case stud(y|ies)|success stor(y|ies))\b|"
    r"^(how\s+)?[\w'’.\- ]{2,40}\s(uses?|used|is using|are using|built|builds|cut|cuts|"
    r"scales?|scaled|accelerat\w+|improv\w+|transform\w+|deliver\w+|reduc\w+|turn\w+|sav\w+)\b|"
    r"^how\s+\S+\s+(uses?|builds?|scales?|cuts?|turns?|powers?|delivers?)\b|"
    r"^(inside|meet)\s+[\w'’.\- ]{2,30}('s)?\b|"
    r"\bwith (chatgpt|gpt-?\d|codex|claude|gemini|grok|copilot)\b", re.I)
NEWS_NOISE_COMPANY = re.compile(
    r"\b(joins?|joined|appoint\w*|hires?|hired|"
    r"acqui\w*|acquisition|merger|ipo|s-1|funding|fundrais\w*|series [a-e]|raises?|"
    r"invest\w*|grants?|donat\w*|stake|valuation|"
    r"partner\w*|collaborat\w*|teams? up|joins? forces|alliance|"
    r"expand\w*|presence in|headquarter\w*|campus|"
    r"polic(y|ies)|govern\w*|regulat\w*|legislat\w*|bill|senate|congress|lawmakers|"
    r"government|federal|white house|european union|blueprint|"
    r"awards?|recogni\w*|gartner|magic quadrant|forbes|"
    r"ukraine|russia|china|brazil|japan|india|thailand|africa|europe|singapore|malta|"
    r"greece|ireland|australia|korea|uae|saudi|emirates)\b", re.I)
NEWS_NOISE_MARKETING = re.compile(
    r"\b(reimagin\w*|future of|the future|why|what|how to|guide|best practices|"
    r"tips|trends?|outlook|opinion|perspective|essay|manifesto|vision|"
    r"state of|era of|age of|day in the life|lessons?|scorecard|"
    r"powering|unlocking|empowering|accelerating|transforming|demystif\w*|"
    r"fundamentals|getting started|101|explained|beginner)\b", re.I)
NEWS_NOISE_EDU_HEALTH = re.compile(
    r"\b(youth|teens?|students?|teachers?|classroom|k-?12|schools?|education|literacy|"
    r"academy|universit(y|ies)|college|"
    r"health|healthcare|clinicians?|patients?|medical|hospital|diagnos\w*|cancer|"
    r"nonprofits?|charit\w*|philanthrop\w*|social impact|workforce)\b", re.I)
NEWS_NOISE_SAFETY = re.compile(
    r"\b(disrupting|influence (operation|activity|campaign)|misuse|malicious|abuse|"
    r"threat actor\w*|scams?|phishing|malware|spam|covert|election|misinformation|"
    r"red team\w*|jailbreak|prompt injection|safeguards?|alignment|misalignment|"
    r"age prediction|parental control)\b", re.I)
NEWS_NOISE_RESEARCH = re.compile(
    r"\b(papers?|research|stud(y|ies)|benchmark\w*|evaluat\w*|"
    r"techniques?|methods?|algorithms?|architecture|datasets?|corpus|survey|"
    r"tutorial|deep dive|internals|attention|transformers?|quantiz\w*|distill\w*|"
    r"lora|grpo|rlhf|dpo|serving|kernels?|cuda|gpu|memory|"
    r"optimiz\w*|scaling|vector|profiling|part \d)\b", re.I)
NEWS_NOISE_TUTORIAL = re.compile(
    r"^(using|working with|building with|create|creating|build|learn|training)\b|"
    r"\b(workflows? (with|for)|for (marketing|sales|finance|research|operations|support|"
    r"customer success|managers|teams)|cheat sheet|playbook)\b", re.I)
NEWS_NOISE_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("customer_story", NEWS_NOISE_CUSTOMER), ("company_news", NEWS_NOISE_COMPANY),
    ("edu_health", NEWS_NOISE_EDU_HEALTH), ("safety", NEWS_NOISE_SAFETY),
    ("tutorial", NEWS_NOISE_TUTORIAL), ("marketing", NEWS_NOISE_MARKETING),
    ("research", NEWS_NOISE_RESEARCH),
]

# 按厂商选择信号组（未列出 = 不过滤）
#   strong          技术变更事实（API / 定价 / 限流 / 弃用）
#   release_product 发布用语 + 必须配产品名（滤掉 `Introducing the Intelligence Age`）
#   release_any     「已上架 / 可用」类用语，无需产品名
#   release_wide    全部发布用语，不要求产品名（huggingface 用：它的 `Introducing X`
#                   基本都是模型 / 平台发布）
#   headline        标题以「模型名 + 版本号 + 冒号」开头
NEWS_INTEL_SIGNALS: dict[str, tuple[str, ...]] = {
    "openai":        ("strong", "release_product", "release_any", "headline"),
    "huggingface":   ("release_wide", "headline"),
    "modal":         ("strong", "release_product", "release_any", "headline"),
    "modular_cloud": ("strong", "release_product", "release_any", "headline"),
    "mistral":       ("strong", "release_product", "release_any", "headline"),
    "anthropic":     ("strong", "release_product", "release_any", "headline"),
    "cohere":        ("strong", "release_product", "release_any", "headline"),
    "meta_llama":    ("strong", "release_product", "release_any", "headline"),
    "google_gemini": ("strong", "release_product", "release_any", "headline"),
}


def is_intel_news(vendor_id: str, title: str) -> bool:
    """判断一条动态的标题是否为「情报」（免费额度 / 模型 / 定价 / API 变更）。

    未列入 `NEWS_INTEL_SIGNALS` 的厂商一律返回 True（不过滤）。
    传进来的应当是**原文标题**（过滤发生在翻译之前）。
    """
    sig = NEWS_INTEL_SIGNALS.get(vendor_id)
    if not sig:
        return True
    text = title or ""
    if "strong" in sig and NEWS_SIGNAL_STRONG.search(text):
        return True
    if "headline" in sig and NEWS_SIGNAL_HEADLINE.search(text):
        return True
    # 客户案例优先于发布信号：`Stampli cuts launch hours by 68% using ChatGPT Work`
    # 里的 `launch` 是名词，会被发布词误命中，但它其实是客户案例。
    if NEWS_NOISE_CUSTOMER.search(text):
        return False
    if "release_wide" in sig and NEWS_SIGNAL_RELEASE.search(text):
        return True
    if "release_any" in sig and NEWS_SIGNAL_RELEASE_ANY.search(text):
        return True
    if "release_product" in sig and NEWS_SIGNAL_RELEASE.search(text) \
            and NEWS_PRODUCT.search(text):
        return True
    return False


# 已废弃的新闻源：这些 URL 前缀下的条目**不再保留**（含历史归档）。
# 归档是「增量合并、只增不减」的 —— 从 yaml 删掉一个源之后，它的历史条目会一直留在
# `llm-news/*.md` 与单厂商 feed 里，所以这里做一次收口。**新抓取的条目也一并挡掉。**
RETIRED_NEWS_URL_PREFIXES: tuple[str, ...] = (
    # Google Cloud 的通用 AI 博客（Gartner 魔力象限、印度板球转播、I/O 大会速览…）：
    # 不是 Gemini 的内容，且条目全无日期。该源已于 2026-09-18 从 yaml 移除，
    # 这里清理它的历史残留（实测 11 条）。
    "https://cloud.google.com/blog/products/",
    # 下面四家按「聚合第三方模型的平台不汇聚」的判据，已于 2026-09-22 从 yaml 删掉
    # News 源（baseten 35% 模型相关、modal 16%、ppio 纯聚合、digitalocean 100 条
    # 含模型名 0 条）。它们的归档已被 `write_news_archives` 的 `clean_removed` 清掉
    # （2026-09-23 巡检后 `articles.json` 里这四家均为 0 条）。这里再挡一道是**双保险**：
    # 厂商本体仍留在总表里，万一将来某个源被重新发现、或归档被手工恢复，
    # 条目也不会重新混进 News 端。
    "https://www.baseten.co/",
    "https://modal.com/",
    "https://ppio.com/",
    "https://docs.digitalocean.com/",
)


def _is_retired_news_url(url: str) -> bool:
    """URL 是否属于已废弃的新闻源（新抓取与历史归档都要挡）。"""
    return any((url or "").startswith(p) for p in RETIRED_NEWS_URL_PREFIXES)


def collect_news_articles(intel: VendorIntel, session: requests.Session) -> None:
    """
    汇总一个厂商的最新文章：
      1) YAML 中 type=feed 的源直接解析原始 XML；
      2) 博客 / 新闻 HTML 页自动发现的 RSS/Atom 链接，抓取并解析；
      3) 仍无文章时，从 HTML 链接中启发式提取文章卡片。
    去重后按日期倒序（无日期排后），每厂商保留最新 5 篇。
    """
    articles: list[Article] = []
    seen_urls: set[str] = set()
    feed_done: set[str] = set()

    def _add(arts: list[Article]) -> None:
        for art in arts:
            if not art.url or _is_retired_news_url(art.url):
                continue
            key = _norm_url(art.url)
            # 同页 #锚点 文章（单页文档站）须保留 fragment，否则被折叠成一条
            frag = urlparse(art.url).fragment.strip()
            if frag:
                key = key + "#" + frag.lower()
            if key in seen_urls:
                continue
            seen_urls.add(key)
            articles.append(art)

    # 1) 显式 RSS/Atom 源（raw 为抓取时保留的原始 XML）
    for page in intel.news_pages:
        if page.stype == "feed":
            feed_done.add(_norm_url(page.final_url or page.url))
            if page.ok and page.raw:
                _add(parse_feed_xml(page.raw, page.final_url or page.url,
                                    stype="feed"))

    # 2) HTML 动态页中发现的 RSS/Atom 链接
    for page in intel.news_pages:
        if not page.ok or page.stype == "feed":
            continue
        for feed_url in page.feeds:
            # sitemap.xml 形似 feed 但不是订阅源，跳过（发现端已拦，双保险）
            if "sitemap" in feed_url.lower():
                continue
            if _norm_url(feed_url) in feed_done:
                continue
            feed_done.add(_norm_url(feed_url))
            _add(fetch_feed_articles(session, feed_url, stype=page.stype))

    # 3) HTML 文章链接兜底（RSS 无产出时）
    if not articles:
        for page in intel.news_pages:
            if page.stype != "feed":
                # 子文档需要全量归档，HTML 兜底提取上限放宽到 100 条
                _add(extract_articles_from_page(page, max_items=100))
        # 锚文本是「this documentation / 查看详情」之类通用词时，
        # 抓文章页 <title> 补全标题（限前 5 篇，避免请求过多）；
        # 若补全到的是文档指南页标题，说明链接已失效（站点回退到默认文档），丢弃
        drop_urls: set[str] = set()
        for art in articles[:5]:
            if not _GENERIC_ARTICLE_TITLE.match(art.title.strip()):
                continue
            try:
                resp = session.get(art.url, timeout=(8.0, 20.0),
                                   allow_redirects=True)
                if resp.status_code < 400:
                    if not resp.encoding or resp.encoding.lower() in (
                            "iso-8859-1", "ascii"):
                        resp.encoding = resp.apparent_encoding or resp.encoding
                    page_title = parse_html(resp.text, resp.url)[1]
                    # 去掉站点名后缀（"标题 | 站点名" / "标题 - 站点名"）
                    page_title = re.split(r"\s[|\-–—_]\s", page_title)[0].strip()
                    if len(page_title) >= 8:
                        if _DOCISH_TITLE.match(page_title):
                            drop_urls.add(_norm_url(art.url))
                        else:
                            art.title = page_title
            except requests.RequestException:
                continue
        if drop_urls:
            articles = [a for a in articles if _norm_url(a.url) not in drop_urls]

    # 4) 同日去重：更新日志列表页里的日期锚点（如 DeepSeek /updates/#时间-2026-09-10）
    #    与对应新闻详情页（/news/<slug>）指向同一次发布时，保留详情页、丢弃锚点；
    #    当日没有详情页的历史条目（锚点是唯一记录）仍然保留。
    def _release_core(title: str) -> str:
        core = re.sub(r"[\s:：，,。.()（）\-]+", "", title).lower()
        for verb in ("正式版发布", "正式发布", "发布", "上线", "更新", "正式版"):
            if core.endswith(verb):
                return core[:-len(verb)]
        return core

    def _is_date_anchor(url: str) -> bool:
        p = urlparse(url)
        return ("/updates/" in p.path
                and unquote(p.fragment).startswith("时间-"))

    def _is_news_detail(url: str) -> bool:
        p = urlparse(url)
        return "/news/" in p.path

    drop_anchor_urls: set[str] = set()
    by_date: dict[str, list[Article]] = {}
    for art in articles:
        if art.date:
            by_date.setdefault(art.date, []).append(art)
    for day, items in by_date.items():
        anchors = [a for a in items if _is_date_anchor(a.url)]
        details = [a for a in items if _is_news_detail(a.url)]
        if not anchors or not details:
            continue
        for anc in anchors:
            core_anc = _release_core(anc.title)
            if not core_anc:
                continue
            for det in details:
                core_det = _release_core(det.title)
                if (core_anc == core_det
                        or core_anc in core_det or core_det in core_anc):
                    drop_anchor_urls.add(anc.url)
                    break
    if drop_anchor_urls:
        articles = [a for a in articles if a.url not in drop_anchor_urls]

    dated = sorted((a for a in articles if a.date),
                   key=lambda a: a.date, reverse=True)
    undated = [a for a in articles if not a.date]
    ordered = dated + undated

    # 情报过滤：剔除客户案例 / 公司新闻 / 营销 / 教程 / 研究论文（见 NEWS_INTEL_SIGNALS）。
    # 放在这里是因为此时 art.title 仍是**原文标题** —— 翻译之后再判会失真
    # （`Magistral` 译成「公路」、`Introducing X` 译成「X 简介」都会让判据失准）。
    kept = [a for a in ordered if is_intel_news(intel.vendor_id, a.title)]
    intel.news_filtered = len(ordered) - len(kept)
    intel.all_news_articles = kept          # 全量归档（llm-news/ 子文档）
    intel.news_articles = kept[:5]          # 主文档仅展示最新 5 篇


# ---------------------------------------------------------------------------
# 链接自动发现：为缺少 pricing/free_quota 入口（或入口指向营销首页）的厂商，
# 从官网首页 / 产品页上的链接中自动找出定价 / 免费额度页
# ---------------------------------------------------------------------------

# ASCII 部分加词边界守卫（避免 trial 命中 industrial 之类误报）；中文按子串匹配
PRICE_LINK_HINTS = re.compile(
    r"(?<![a-z])(pricing|prices?|price|costs?|billing)(?![a-z])"
    r"|计费|定价|价格|收费|资费|费用说明|套餐价格", re.I)
FREE_LINK_HINTS = re.compile(
    r"(?<![a-z])(free[-_ ]?(?:tier|plan|credits?|trial|quota|account|allowance|"
    r"allocation)|rate[-_ ]?limits?|credits?|quota|trial)(?![a-z])"
    r"|免费额度|免费|赠送|试用|权益|福利|资源包|额度|限速|限流|配额", re.I)
# 博客 / 文档 / 控制台 / 法务 / 聊天 App 等导航链接降权（发现目标是定价/免费页本身）
BAD_LINK_HINTS = re.compile(
    r"(blog|news|research|changelog|documentation|developers|api-reference|"
    r"github\.com|careers|/about|contact|legal|privacy|terms|/trust|security|"
    r"status\.|community|forum|discord|twitter|linkedin|youtube|facebook|"
    r"login|signin|sign[-_]?up|signup|console|dashboard|playground|招聘|博客|新闻|"
    r"动态|公告|开发者|法律|隐私|条款|登录|注册|"
    r"chat\.|/chat|sign[_-]?in|/auth|download|/docs?/)", re.I)
# 登录 / 注册 / 找回密码等 URL 直接排除（发现时偶尔会被“免费使用”锚文本带到登录页）
HARD_BAD_URL = re.compile(
    r"(login|log-in|signin|sign-in|signout|sign-out|sign-up|signup|register|"
    r"passport|reset[-_]?password|/auth|auth\.|/u/login|account/login)", re.I)

# 发现候选时按路径直接排除：博客 / 新闻 / 案例 / 招聘 / 社区等永远不会是定价页；
# 控制台内页（settings/account/dashboard 等）需登录，公开抓取只会跳到登录页。
# 仅匹配完整路径段（连字符扩展段如 billing-pricing 不排除，文档站常用）
HARD_BAD_PATH = re.compile(
    r"/(blog|blogs|news|press|press-releases|media|customers|customer-stories|"
    r"case-stud(?:y|ies)|stories|careers?|jobs|community|forums?|events?|webinars?|"
    r"podcasts?|research|changelog|settings|dashboard|admin|console|"
    r"whitepapers?|ebooks?|cookie[-_ ]?policy|privacy[-_ ]?policy)(?=/|$|\?)",
    re.I)


def _norm_url(url: str) -> str:
    """URL 规范化用于去重：小写 host、去末尾斜线、去掉 fragment。"""
    try:
        p = urlparse(url)
        return (p.scheme.lower() + "://" + p.netloc.lower()
                + p.path.rstrip("/")).lower()
    except Exception:
        return (url or "").rstrip("/").lower()


def _article_key(url: str) -> str:
    """文章的**身份**键：在 `_norm_url` 基础上**保留 fragment**。

    单页文档站的每条条目是「同页不同 `#锚点`」（阿里云百炼更新日志、MiniMax 发布说明、
    PPIO 公告页…），**fragment 才是它们的身份**。`_norm_url` 会去掉 fragment，于是同一页的
    N 条折叠成一个键：归档增量合并会把历史条目误判成「本次已抓到」而**丢弃**
    （实测：归档 3 条、本次只重抓到 1 条时，合并后只剩 1 条 —— 违反「归档只增不减」）；
    合并流去重也会把同页条目吃掉（通义 100 条在合并流里只剩 1 条）。

    `extract_articles_from_page` 与 `collect_news_articles` 早已按这个规则处理，这里统一 ——
    同一个判断不要在两处各写一遍。
    """
    key = _norm_url(url)
    frag = urlparse(url).fragment.strip().lower()
    return key + "#" + frag if frag else key


def _same_site(u1: str, u2: str) -> bool:
    """同站判断：同域或互为子域（www. 视为同域）。"""
    try:
        h1 = urlparse(u1).netloc.lower().split(":")[0]
        h2 = urlparse(u2).netloc.lower().split(":")[0]
        if h1.startswith("www."):
            h1 = h1[4:]
        if h2.startswith("www."):
            h2 = h2[4:]
        return h1 == h2 or h1.endswith("." + h2) or h2.endswith("." + h1)
    except Exception:
        return False


def score_links(links: list[tuple[str, str]], base_url: str
                ) -> list[tuple[int, str, str]]:
    """
    给页面上的锚链接打分，找出最可能是「定价 / 免费额度」的链接。
    锚文本命中比路径命中权重更高；同站链接才参与；返回降序 [(score, url, anchor)]。
    """
    scored: dict[str, tuple[int, str]] = {}
    for url, anchor in links:
        if not url or not url.startswith("http"):
            continue
        if not _same_site(url, base_url):
            continue
        p = urlparse(url)
        # 登录 / 注册 / SSO 跳转页不可能是定价页，直接排除
        if HARD_BAD_URL.search(p.netloc + p.path):
            continue
        # 博客 / 新闻 / 案例 / 控制台内页等路径，直接排除（避免博客评测文里的
        # cost/trial 词把候选带偏）
        if HARD_BAD_PATH.search(p.path or "/"):
            continue
        anchor_l = (anchor or "").lower()
        path_l = (p.path or "/").lower()
        score = 0
        if PRICE_LINK_HINTS.search(anchor_l):
            score += 6
        if FREE_LINK_HINTS.search(anchor_l):
            score += 5
        if PRICE_LINK_HINTS.search(path_l):
            score += 3
        if FREE_LINK_HINTS.search(path_l):
            score += 3
        if BAD_LINK_HINTS.search(anchor_l):
            score -= 8
        if BAD_LINK_HINTS.search(path_l):
            # 文档站里也常承载定价 / 速率限制页，路径降权不宜过重
            score -= 2
        if score <= 0:
            continue
        prev = scored.get(url)
        if prev is None or score > prev[0]:
            scored[url] = (score, anchor or "")
    return sorted(((s, u, a) for u, (s, a) in scored.items()),
                  key=lambda x: (-x[0], len(x[1])))


def discover_intel_links(seed_pages: list[PageResult], fetched: set[str],
                         max_candidates: int = 3) -> list[str]:
    """从种子页的链接中发现定价 / 免费页候选 URL（排除已抓取过的）。"""
    candidates: list[str] = []
    seen = set(fetched)
    for page in seed_pages:
        if not page.ok or not page.links:
            continue
        for _score, url, _anchor in score_links(page.links,
                                                page.final_url or page.url):
            norm = _norm_url(url)
            if norm in seen:
                continue
            seen.add(norm)
            candidates.append(url)
            if len(candidates) >= max_candidates:
                return candidates
    return candidates


# ---------------------------------------------------------------------------
# 巡检主流程
# ---------------------------------------------------------------------------

def crawl_vendor(vendor: dict, sources: list[dict], session: requests.Session,
                 delay: float, browser: "BrowserSession | None" = None) -> VendorIntel:
    """抓取单个厂商的全部相关入口并提取证据。"""
    vid = vendor.get("id", "unknown")
    intel = VendorIntel(
        vendor_id=vid,
        brand=vendor.get("brand", vid),
        homepage=vendor.get("homepage", ""),
        products=vendor.get("products") or [],
    )

    for src in sources:
        stype = src.get("type", "")
        url = src.get("url", "")
        if not url:
            continue
        if stype in SKIP_TYPES:
            intel.skipped_sources.append(src)
            continue
        if stype in NEWS_TYPES:
            target = intel.news_pages
        elif stype in INTEL_TYPES or stype in CONDITION_TYPES:
            target = intel.intel_pages
        else:
            # api_docs / docs / console / hf_org 等入口：不深度抓取
            intel.skipped_sources.append(src)
            continue
        page = fetch_url(session, url, stype, browser=browser)
        target.append(page)
        if page.ok:
            via = "🌐browser" if page.rendered_by == "browser" else "ok"
            extra = " (内容过少)" if page.sparse else ""
            status = f"{via}{extra}"
        else:
            status = f"FAIL {page.error}"
        print(f"    [{stype:<16}] {status:<24} {url}")
        if delay:
            time.sleep(delay)

    intel.evidence = extract_evidence(intel.intel_pages)

    # 博客 / 更新动态：解析 RSS/Atom 与页面文章链接，汇总最新文章
    try:
        collect_news_articles(intel, session)
    except Exception as exc:  # 文章提取失败不影响情报主流程
        print(f"    [warn] 动态文章提取异常: {type(exc).__name__}: {exc}",
              file=sys.stderr)

    # ---- 自动发现兜底：没有情报页，或抓了但没提取到任何免费 / 活动证据时，
    #      从官网首页 / 产品页等入口的链接里自动找出定价、免费额度页再抓 ----
    has_evidence = any(intel.evidence.get(k) for k, _, _ in KEYWORD_GROUPS)
    if not has_evidence:
        fetched: set[str] = set()
        for p in intel.intel_pages:
            fetched.add(_norm_url(p.url))
            if p.final_url:
                fetched.add(_norm_url(p.final_url))

        seeds: list[PageResult] = [p for p in intel.intel_pages
                                   if p.ok and p.links]

        def _log_page(page: PageResult) -> None:
            if page.ok:
                via = "🌐browser" if page.rendered_by == "browser" else "ok"
                extra = " (内容过少)" if page.sparse else ""
                status = f"{via}{extra}"
            else:
                status = f"FAIL {page.error}"
            print(f"    [{page.stype:<16}] {status:<26} {page.url}")

        def _fetch_seed(url: str, stype: str, into_list: bool):
            if not url or _norm_url(url) in fetched:
                return None
            # 第三方站点（如 HuggingFace 组织页）不作为发现种子，避免把别家的
            # 定价页误当作该厂商的页面
            if intel.homepage and not _same_site(url, intel.homepage):
                return None
            page = fetch_url(session, url, stype, browser=browser)
            fetched.add(_norm_url(url))
            if page.final_url:
                fetched.add(_norm_url(page.final_url))
            if into_list:
                intel.intel_pages.append(page)
            _log_page(page)
            if delay:
                time.sleep(delay)
            return page

        # 种子 1：官网首页（纳入巡检列表，首页正文本身也常含免费额度信息）
        home_page = _fetch_seed(intel.homepage, "homepage", True)
        if home_page is not None and home_page.ok:
            seeds.append(home_page)

        candidates = discover_intel_links(seeds, fetched)

        # 种子 2：product / 文档 / 控制台等未深度抓取的入口（首页没发现候选时）。
        # 这类页面不直接列入巡检结果，但正文若含免费/额度事实（常见于 api_docs），
        # 提取到证据后会作为来源补入巡检列表
        extra_seed_pages: list[PageResult] = []
        if not candidates:
            for src in intel.skipped_sources[:4]:
                seed_page = _fetch_seed(src.get("url", ""),
                                        src.get("type", "product"), False)
                if seed_page is not None and seed_page.ok:
                    seeds.append(seed_page)
                    extra_seed_pages.append(seed_page)
            candidates = discover_intel_links(seeds, fetched)

        if candidates:
            print(f"    [discovery] 自动发现 {len(candidates)} 个候选定价/免费页")
        for cu in candidates:
            page = fetch_url(session, cu, "discovered", browser=browser)
            _log_page(page)
            if delay:
                time.sleep(delay)
            if not page.ok:
                continue
            page.discovered = True
            fetched.add(_norm_url(cu))
            if page.final_url:
                fetched.add(_norm_url(page.final_url))
            intel.intel_pages.append(page)
        # 无论是否发现候选页，都基于全部已抓页面重新提取一次
        # （官网首页、api_docs 等种子页正文本身就可能含免费额度事实）
        new_evidence = extract_evidence(intel.intel_pages + extra_seed_pages)
        if any(new_evidence.get(k) for k, _, _ in KEYWORD_GROUPS):
            intel.evidence = new_evidence
            cited = {sn.url for k in new_evidence for sn in new_evidence[k]}
            for seed_page in extra_seed_pages:
                if (seed_page.final_url or seed_page.url) in cited:
                    intel.intel_pages.append(seed_page)

    for k in intel.evidence:
        for sn in intel.evidence[k]:
            try:
                sn.text = translate_to_zh(sn.text)
            except Exception:
                pass

    return intel


# ---------------------------------------------------------------------------
# README 生成（参考 FreeLLM-API-KeyHub 规格表风格，无状态噪点）
# ---------------------------------------------------------------------------

from provider_profiles import (
    get_provider_profile,
    render_freellm_table,
    translate_to_zh,
    CATEGORY_TITLES,
    CATEGORY_DESCRIPTIONS,
    get_guide_meta,
    reload_overrides,
    vendor_rank_index,
)


def type_label(stype: str) -> str:
    """类型中文名；未知类型退化为可读形式（api_docs -> API docs）。"""
    if stype in TYPE_LABELS:
        return TYPE_LABELS[stype]
    return stype.replace("_", " ")


#: 时间戳屏蔽正则：无内容变化的巡检不应因「最近更新」时间而产生 diff
_TS_RE = re.compile(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}")


def _mask_ts(text: str) -> str:
    return _TS_RE.sub("__TS__", text)


def order_vendor_records(intel_list: list[VendorIntel]) -> list[tuple[int, VendorIntel, dict]]:
    """按 README 展示顺序（国内 / 国际 / 云）返回 (序号, intel, profile)。"""
    categories = OrderedDict([("domestic", []), ("international", []), ("cloud", [])])
    for intel in intel_list:
        prof = get_provider_profile(intel.vendor_id, intel.brand, intel.homepage)
        cat = prof.get("category", "domestic")
        categories[cat if cat in categories else "domestic"].append((intel, prof))
    records: list[tuple[int, VendorIntel, dict]] = []
    idx = 1
    for items in categories.values():
        for intel, prof in items:
            records.append((idx, intel, prof))
            idx += 1
    return records


def _gh_slug(heading: str) -> str:
    """复刻 GitHub 锚点规则：小写、去标点、空白折叠为连字符（\\w 含中日韩文字）。"""
    s = re.sub(r"[^\w\s-]", "", heading.lower())
    return re.sub(r"\s+", "-", s.strip())


_PROMO_END_PAT = re.compile(r"截止|到期|结束|止至|until|end(?:s|ed)?\b", re.I)
_PROMO_DATE_PAT = re.compile(r"(20\d{2})" + _DATE_SEP_YM + r"(\d{1,2})" + _DATE_SEP_MD + r"(\d{1,2})")


def _promo_fragment_expired(frag: str, today: date) -> bool:
    """时效片段写明了截止/结束日期且最晚一个日期已过，则视为过期，不再收进攻略。

    无明确日期的片段（如「每日限量 100 名」「未公布截止日」）一律保留，交由人工复核。
    """
    if not _PROMO_END_PAT.search(frag):
        return False
    dates = []
    for m in _PROMO_DATE_PAT.finditer(frag):
        try:
            dates.append(date(int(m.group(1)), int(m.group(2)), int(m.group(3))))
        except ValueError:
            continue
    return bool(dates) and max(dates) < today


def render_guide_section(records: list[tuple[int, VendorIntel, dict]]) -> list[str]:
    """白嫖攻略：完全由 provider_profiles.get_guide_meta 与档案字段自动渲染（无时间戳）。"""
    L: list[str] = []
    L.append("---")
    L.append("")
    L.append('<a id="白嫖攻略"></a>')
    L.append("")
    L.append("## 🎯 白嫖攻略")
    L.append("")
    L.append("> 本章节与下方厂商总表同源，每次巡检自动重建；免费政策随时变化（活动到期、限速调整、模型下架），"
             "注册 / 充值前请点进对应厂商的官方链接复核。")
    L.append("")

    def link(idx: int, prof: dict) -> str:
        dname = prof.get("display_name", "")
        name = re.sub(r"[（(][^（）()]*[)）]\s*$", "", dname).strip()
        return f"[{name}](#{_gh_slug(f'{idx}. {dname}')})"

    def with_short(idx: int, intel: VendorIntel, prof: dict) -> str:
        short = get_guide_meta(intel.vendor_id).get("short")
        return f"{link(idx, prof)}（{short}）" if short else link(idx, prof)

    def tier_group(pred) -> tuple[list[str], list[str]]:
        """按「门槛 + 有效期」的价值排序分组（新用户视角），而非按额度机制归类。

        判定用到的三个信号：meta["signup"]（email=免卡 / card=需绑卡）、
        meta["tiers"]（permanent|recurring=不过期 / onetime=一次性 / selfhost=自托管）、
        prof["category"]（domestic=国内，一律需手机号+实名）。
        """
        dom, ovs = [], []
        for idx, intel, prof in records:
            meta = get_guide_meta(intel.vendor_id)
            if not meta or not pred(meta, prof):
                continue
            cell = with_short(idx, intel, prof)
            (dom if prof.get("category") == "domestic" else ovs).append(cell)
        return dom, ovs

    # 0. 懒人首选：GUIDE_META 中带 pick 推荐语的厂商（按总表序号）。
    #    五家都免绑卡；实名/邮箱只是常规注册，不构成门槛。
    picks = [(idx, intel, prof, get_guide_meta(intel.vendor_id).get("pick", ""))
             for idx, intel, prof in records
             if get_guide_meta(intel.vendor_id).get("pick")]
    picks.sort(key=lambda t: t[0])
    if picks:
        L.append(f"### 0. 懒人首选：不知道选谁，先注册这 {len(picks)} 个")
        L.append("")
        L.append("> 五家都**免绑信用卡**，注册即得（国内的需手机号实名，海外的邮箱即可——都属常规注册）；"
                 "覆盖日常对话、写代码、向量/重排、画图等绝大多数免费用法。")
        L.append("")
        for n, (idx, intel, prof, reason) in enumerate(picks, 1):
            L.append(f"{n}. {link(idx, prof)} —— {reason}")
        L.append("")

    # 1. 免费额度分级：唯一的真门槛是「要不要付款方式」，其次看额度过不过期。
    #    邮箱注册与手机号实名同属常规注册（人人有手机号），不算门槛。
    L.append("### 1. 先认清四类「免费」——按能否白嫖排序")
    L.append("")
    L.append("> 排序逻辑是**新用户视角**：先看要不要绑卡（实名 / 邮箱都只是常规注册，不算门槛），"
             "再看额度会不会过期。A 类注册即用且不会过期，C 类额度最大但要先冒绑卡的风险。")
    L.append("")
    L.append("| 类型 | 特点与正确用法 | 代表平台（点击跳上方档案） |")
    L.append("|---|---|---|")
    tier_defs = [
        ("A. 无条件 · 长期可用",
         "注册即得（邮箱 / GitHub / Google 或手机号实名均可，**无需付款方式**），"
         "不过期或按日/月滚动重置；可当长期主力，注意 RPM/RPD 限速与商用条款",
         lambda m, _p: m.get("signup") != "card"
                       and bool({"permanent", "recurring"} & set(m.get("tiers") or []))),
        ("B. 无条件 · 一次性限时",
         "注册即到账、**无需付款方式**，但有有效期、不可重置；先想好用量再开通，薅完即走",
         lambda m, _p: m.get("signup") != "card"
                       and "onetime" in (m.get("tiers") or [])
                       and not ({"permanent", "recurring"} & set(m.get("tiers") or []))),
        ("C. 需绑卡 · 大额云试用金",
         "需信用卡或身份验证（可能有验证扣款）；额度最大，但**注册后立刻设预算告警**，"
         "记下到期日并主动关停",
         lambda m, _p: m.get("signup") == "card"),
        ("D. 开源权重 / 自托管",
         "没有「额度」概念，自己出算力；也可走 A 类平台免费托管调用",
         lambda m, _p: "selfhost" in (m.get("tiers") or [])),
    ]
    for label, desc, pred in tier_defs:
        dom, ovs = tier_group(pred)
        cell = ""
        if dom:
            cell += "国内：" + "、".join(dom)
        if ovs:
            cell += ("<br>" if cell else "") + "海外：" + "、".join(ovs)
        L.append(f"| **{label}** | {desc} | {cell or '—'} |")
    L.append("")

    # 2. 注册门槛：实名/邮箱是常规注册，唯一需要单独列出的是绑卡
    L.append("### 2. 唯一的真门槛：要不要信用卡")
    L.append("")
    card, n_domestic = [], 0
    for idx, intel, prof in records:
        meta = get_guide_meta(intel.vendor_id)
        if prof.get("category") == "domestic":
            n_domestic += 1
        if meta.get("signup") == "card":
            card.append(link(idx, prof))
    L.append(f"- 除下列 **{len(card)} 家需验证付款方式**外，其余平台注册即发 Key，无任何付款门槛；"
             "国内平台用手机号 + 实名（常规注册，人人可办），海外平台用邮箱 / GitHub / Google 登录。")
    L.append("- ⚠️ **需绑卡**（可能有验证扣款或最低首付，赠金到账后也请立即设预算告警）："
             + "、".join(card) + "。")
    L.append("- 国内平台未完成实名时可能被限速（如 PPIO），但这是注册流程的一部分，不是额外门槛。")
    L.append("")

    # 3. 场景推荐
    L.append("### 3. 按场景选")
    L.append("")
    scenario_defs = [
        ("code", "写代码 / 编程 Agent"),
        ("flagship", "免费体验旗舰通用模型"),
        ("longctx", "超长上下文（约 1M tokens）"),
        ("image", "图像 / 视频生成"),
        ("embed", "Embedding / Rerank / OCR / 语音"),
        ("deploy", "自建私有端点 / 跑任意开源模型"),
        ("referral", "邀请返利 / 拉新奖励"),
        ("student", "学生 / 高校师生扶持"),
        ("credit", "大额云厂商体验金（海外需绑卡，国内需实名）"),
    ]
    for key, label in scenario_defs:
        hits = [with_short(idx, intel, prof) for idx, intel, prof in records
                if key in (get_guide_meta(intel.vendor_id).get("scenarios") or [])]
        if hits:
            L.append(f"- **{label}**：" + "、".join(hits) + "。")
    L.append("")

    # 4. 防扣费 / 防坑
    L.append("### 4. 防扣费清单（白嫖最容易翻车的地方）")
    L.append("")
    tip_no = 1
    for idx, intel, prof in records:
        tip = get_guide_meta(intel.vendor_id).get("tip")
        if tip:
            L.append(f"{tip_no}. {link(idx, prof)}：{tip}")
            tip_no += 1
    L.append(f"{tip_no}. 所有绑卡平台（见第 2 节名单）注册后立刻设置 **Budget 预算与用量告警**，"
             "记下赠金到期日，到期前关停资源、删除计费实例。")
    L.append(f"{tip_no + 1}. 永久免费层 RPM 普遍只有个位数到几十，批量任务请走大额试用金 / 月度重置额度或错峰。")
    L.append(f"{tip_no + 2}. 第三方聚合中转（DMXAPI、数眼智能等非官方平台）存在跑路风险，"
             "只放低敏测试流量，不要充大额余额。")
    L.append("")

    # 5. 限时 / 易变信息（自动扫描档案中的时效字段；写明截止日且已过期的片段直接剔除）
    limited: list[str] = []
    limit_pat = re.compile(r"(截止|限量|限时|爆满|limited time)", re.I)
    today = date.today()
    for idx, intel, prof in records:
        candidates: list[str] = []
        for key in ("promotions", "free_quota", "validity"):
            if isinstance(prof.get(key), str):
                candidates.append(prof[key])
        fm = prof.get("free_models")
        if isinstance(fm, (list, tuple)):
            candidates.extend(fm)
        alive: list[str] = []
        for text in candidates:
            if not limit_pat.search(text):
                continue
            clean = re.sub(r"[*`]", "", text)
            for frag in re.split(r"[。；;\n]", clean):
                frag = frag.strip()
                if limit_pat.search(frag) and not _promo_fragment_expired(frag, today):
                    alive.append(frag)
        if alive:
            frag = alive[0]
            limited.append(f"- {link(idx, prof)}：{frag[:90] + ('…' if len(frag) > 90 else '')}")
    if limited:
        L.append("### 5. 限时 / 易变信息（最容易过期，看到请先核对官方页）")
        L.append("")
        L.extend(limited[:10])
        L.append("")

    # 6. 免费用完之后（通用方法论，不含易过期价格数字）
    L.append("### 6. 免费额度用完之后")
    L.append("")
    L.append("国内厂商的包月「编程套餐」（火山方舟 Coding Plan、智谱 GLM 套餐等）价格与档位调整频繁，"
             "本仓库不转抄未经官方页面核实的价格数字——请从上方对应厂商表格的「官方直达」进入定价页查看现行档位。"
             "挑选时重点对比三点：")
    L.append("")
    L.append("1. **计费方式**：按请求次数（低频友好）还是按 token（长上下文 / 重度使用友好）；")
    L.append("2. **限速与并发**：套餐是否仍保留 RPM 上限，Batch / 夜间折扣是否可用；")
    L.append("3. **工具兼容**：是否支持你在用的 IDE / Agent 与 OpenAI 兼容端点。")
    L.append("")

    # 7. 常用免费 API · OpenAI 兼容端点速查表（开箱即用，避免用户到处搜索）
    L.append('<a id="一键接入"></a>')
    L.append("")
    L.append("### 7. 常见免费 API · OpenAI 兼容端点与申请直达（一键接入）")
    L.append("")
    L.append("> 适用于 NextChat、Cherry Studio、Chatbox、Dify、Cursor、Cline 等几乎所有支持自定义 OpenAI 格式的客户端：")
    L.append("")
    L.append("| 平台名称 | 免费额度简述 | API Key 申请直达 | OpenAI 兼容 Base URL | 推荐填写的免费模型名称 |")
    L.append("|---|---|---|---|---|")
    # 表体来自 provider_profiles 的 openai_compat 字段（国内 -> 国际 -> 云，与总表同序）
    for idx, intel, prof in records:
        oc = prof.get("openai_compat")
        if not isinstance(oc, dict) or not oc.get("base_url"):
            continue
        name = re.sub(r"[（(][^（）()]*[)）]\s*$", "", prof.get("display_name", intel.brand)).strip()
        key_label = oc.get("api_key_label") or "控制台申请"
        L.append(f"| **{name}** | {oc.get('summary') or '—'} | "
                 f"[{key_label}]({oc.get('api_key_url') or ''}) | `{oc['base_url']}` | "
                 f"{oc.get('models') or '—'} |")
    L.append("")
    return L


def render_guide_block(records: list[tuple[int, VendorIntel, dict]]) -> str:
    """白嫖攻略独立生成块（无时间戳；位置在项目介绍之后、快速开始之前）。"""
    body = "\n".join(render_guide_section(records))
    return f"{GUIDE_BEGIN}\n{body}\n{GUIDE_END}"


def render_intel_section(intel_list: list[VendorIntel], elapsed: float,
                         records: list[tuple[int, VendorIntel, dict]],
                         feeds_base: str = "") -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    news_vendors = sum(1 for v in intel_list if v.news_pages)
    # 页面数写进生成块而不是手写文档里：手写的那份（曾写「约 140 个」）已经漂到 175，
    # 且没人会记得回来改。这里由 intel_list 现算，永远与本次巡检一致。
    intel_pages = sum(len(v.intel_pages) for v in intel_list)
    news_pages = sum(len(v.news_pages) for v in intel_list)

    lines: list[str] = []
    lines.append(README_BEGIN)
    lines.append("")
    lines.append("> 实时追踪国内外大语言模型（LLM）厂商官方公开的**免费 API 额度**、**永久免费模型**与**限时活动调用**情报。")
    lines.append(f"> 本区块由 `crawler_llm_intel.py` 在**每次运行时**实时巡检官方页面生成（非人工编辑、非服务端持续监控），"
                 f"最近一次巡检：**{now}**；本地手动运行与 GitHub Actions 定时刷新的方法见文首「快速开始 / 更新机制」。")
    lines.append(">")
    lines.append(f"> 💡 **核心特性**：覆盖 **{len(intel_list)} 家厂商**"
                 f"（深度抓取 **{intel_pages} 个情报页 + {news_pages} 个动态页**）；"
                 f"海外一手情报自动汉化（品牌与型号名保留原文）；"
                 f"自动过滤页面抓取状态噪点，直接展示具体额度（Tokens/代金券/免费层）、"
                 f"可用模型、有效期与限制条件。")
    lines.append(f"> 📡 **博客动态订阅**：各厂商官方技术博客与更新日志单独维护至 [`llm-news-feeds.md`](llm-news-feeds.md)（共 {news_vendors} 个厂商），可导入 [`llm-news-feeds.opml`](llm-news-feeds.opml) 至 RSS 阅读器跟踪官方动态。")
    if feeds_base:
        site = _feeds_site_base(feeds_base)
        page_part = f"[网页浏览 / 一键订阅]({site}) ｜ " if site else ""
        lines.append(f"> 📡 **自建 RSS**（官方没有原生订阅源的厂商也能订）："
                     f"{page_part}"
                     f"[合并流]({feeds_base}/llm-news-all.xml) ｜ "
                     f"单厂商源 `{feeds_base}/llm-news-{{vendor_id}}.xml`。")
    lines.append("")

    # 白嫖攻略是独立生成块（GUIDE_BEGIN/END），已由 render_guide_block
    # 渲染到项目介绍之后，不在本情报区块内。
    last_cat = None
    for idx, intel, prof in records:
        cat = prof.get("category", "domestic")
        if cat != last_cat:
            title = CATEGORY_TITLES.get(cat, cat)
            desc = CATEGORY_DESCRIPTIONS.get(cat, "")
            lines.append("---")
            lines.append("")
            lines.append(title)
            lines.append("")
            if desc:
                lines.append(desc)
                lines.append("")
            lines.append("---")
            lines.append("")
            last_cat = cat
        lines.extend(render_freellm_table(intel, prof, idx))

    # 365 系列归属页脚必须留在生成标记内：标记之外的内容会被 update_readme 丢弃
    lines.extend(PLAN_FOOTER.split("\n"))
    lines.append("")
    lines.append(README_END)
    lines.append("")
    return "\n".join(lines)


def _replace_marker_block(text: str, begin: str, end: str, block: str) -> str:
    """替换一对 BEGIN/END 标记之间（含标记行）的内容；标记缺失时原样返回。"""
    i, j = text.find(begin), text.find(end)
    if i < 0 or j < i:
        return text
    return text[:i] + block + text[j + len(end):]


def update_readme(path: Path, section: str, guide_section: str = "") -> bool:
    """刷新 README 的两个自动生成区块：白嫖攻略（GUIDE）+ 情报总表（INTEL）。

    屏蔽时间戳后比对，内容无变化则不写文件。INTEL END 之后的历史人工附录
    在首次运行时会被自动移除。README 不存在则新建。返回是否发生写入。
    """
    if path.exists():
        old = path.read_text(encoding="utf-8")
    else:
        old = ("# Free LLM Intel · LLM 免费额度与活动情报\n\n"
               f"{GUIDE_BEGIN}\n{GUIDE_END}\n\n"
               "## 快速开始\n\n")
    if README_BEGIN not in old or README_END not in old:
        sep = "" if old.endswith("\n\n") else ("\n" if old.endswith("\n") else "\n\n")
        new = old.rstrip("\n") + sep + "\n" + section
    else:
        # 1) 先在静态前言区替换攻略块；旧 README 没有 GUIDE 标记时，
        #    退而求其次插到情报块之前（保证正确，位置可能不是最靠前）
        head = old[:old.find(README_BEGIN)]
        if GUIDE_BEGIN in head and GUIDE_END in head:
            head = _replace_marker_block(head, GUIDE_BEGIN, GUIDE_END, guide_section)
        elif guide_section:
            head = head.rstrip("\n") + "\n\n" + guide_section + "\n\n"
        # 2) 情报总表整块替换；END 之后内容丢弃
        new = head + section
    if _mask_ts(new) == _mask_ts(old):
        return False
    path.write_text(new, encoding="utf-8", newline="\n")
    return True


# ---------------------------------------------------------------------------
# 博客 / 动态（RSS）单独输出
# ---------------------------------------------------------------------------

def _native_feed_vendors(intel_list: list[VendorIntel]) -> set[str]:
    """返回**官网自带** RSS/Atom 的厂商 id 集合。

    OPML 与 `llm-news-feeds.md` 都要用它来区分「官方原生源」与「本仓库自建源」，
    两处各写一遍判断迟早会漂移，所以共用这一个。
    """
    out: set[str] = set()
    for intel in intel_list:
        for page in intel.news_pages:
            if not page.ok:
                continue
            if page.stype == "feed" or page.feeds:
                out.add(intel.vendor_id)
                break
    return out


def _rss_articles(intel: VendorIntel, today: str) -> list[Article]:
    """该厂商**会进订阅源**的文章：排除晚于今天的日期（源页面把日期写成未来的情形）。

    `write_rss_feeds` 只对有此类文章的厂商出源，所以 OPML 与 `llm-news-feeds.md` 里
    「本仓库自建源」的标注必须用**同一个判据** —— 否则当某厂商的文章日期全被误写成
    未来时，文档会给出一个并不存在的订阅地址（死链），而两边各自看都「对」。
    """
    return [a for a in intel.all_news_articles if a.date <= today]


def render_news_section(intel_list: list[VendorIntel], feeds_base: str = "",
                        merged_limit: int = RSS_MERGED_LIMIT) -> str:
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    today = now.strftime("%Y-%m-%d")
    lines: list[str] = []
    lines.append(NEWS_BEGIN)
    lines.append("")
    lines.append("## 厂商博客 / 更新动态订阅源")
    lines.append("")
    lines.append(f"> 由 `crawler_llm_intel.py` 自动整理，最近更新：**{now_str}**。")
    lines.append(">")
    lines.append("> 各厂商的官方博客、工程文章、更新日志**单独维护在此**，不混入 README 的免费额度情报；")
    lines.append("> 每个厂商下方列出从官方 RSS / 博客页**实际抓取的最新文章**（标题自动汉化、附发布日期与原文链接）。")
    lines.append("> 主文档每家仅展示**最新 5 篇**；**完整文章归档**按厂商拆分到 [`llm-news/`](llm-news/) 子目录"
                 "（每厂商一个 `.md`，全量罗列该来源所有文章）。")
    lines.append("> 可将同目录下的 `llm-news-feeds.opml` 导入任意 RSS 阅读器（如 Feedly / Inoreader / "
                 "NetNewsWire / 本地阅读器）"
                 + ("统一订阅（原生源 + 本仓库自建源，OPML 里分两组）。"
                    if feeds_base else "订阅**官方原生源**。"))
    if feeds_base:
        site = _feeds_site_base(feeds_base)
        lines.append(">")
        lines.append("> 📡 **本仓库自建 RSS**：把下方归档直接转成订阅源，"
                     "**官方没有原生 RSS 的厂商也能订阅**（标题同样已汉化，每日随巡检刷新）：")
        if site:
            lines.append(f"> - 网页浏览 / 一键订阅：[{site}]({site})"
                         "（可按厂商筛选、搜索，页脚列出**全部有动态源的厂商**单源）")
        lines.append(f"> - 合并流（聚合全部有动态源的厂商）：[`llm-news-all.xml`]({feeds_base}/llm-news-all.xml)"
                     f"（{merged_scope_text(merged_limit)}，带厂商前缀，可按 `category` 过滤）")
        lines.append(f"> - 单厂商源：`{feeds_base}/llm-news-{{vendor_id}}.xml`"
                     "（把 `{vendor_id}` 换成下方括号里的厂商 id，如 `llm-news-openai.xml`）")
        lines.append("> - ⚠️ 合并流与各厂商单源**内容重叠**，二选一订阅即可（都订会出现重复条目）；"
                     "合并流只收有日期的条目，**要看全量请用浏览页或单厂商源**。")
    lines.append("")

    vendors_with_news = [v for v in intel_list if v.news_pages]
    # 官网自带 RSS/Atom 的厂商：其余厂商才是自建源的真正用户，逐条标出来，
    # 否则读者看到「未发现 RSS/Atom 链接」会以为这家订不了 —— 而我们其实自建了一个。
    native_ids = _native_feed_vendors(vendors_with_news)
    feed_count = 0
    vendors_with_articles = 0
    for intel in vendors_with_news:
        lines.append(f"### {intel.brand} ({intel.vendor_id})")
        for page in intel.news_pages:
            label = type_label(page.stype)
            if page.stype == "feed":
                # 显式 RSS/Atom 源：直接列出订阅地址
                lines.append(f"- 📡 [{label}]({page.url})：`{page.final_url or page.url}`")
                feed_count += 1
                continue
            lines.append(f"- 页面：[{label}]({page.url})")
            if not page.ok:
                lines.append(f"  - ❌ 抓取失败：{page.error}（可直接访问页面查看）")
                continue
            if page.feeds:
                for feed in page.feeds:
                    feed_count += 1
                    lines.append(f"  - 📡 RSS/Atom：{feed}")
            else:
                hint = "页面可见文本过少，可能为动态渲染" if page.sparse else "页面 HTML 中未发现 RSS/Atom 链接"
                lines.append(f"  - ⚠️ {hint}，已尝试直接从页面提取文章条目")
        if feeds_base and intel.vendor_id not in native_ids and _rss_articles(intel, today):
            lines.append(f"- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）："
                         f"[`llm-news-{intel.vendor_id}.xml`]"
                         f"({feeds_base}/llm-news-{intel.vendor_id}.xml)")
        if intel.news_articles:
            vendors_with_articles += 1
            lines.append(f"- 📰 **最新文章**（官方源抓取于 {today}，标题自动汉化）：")
            for idx, art in enumerate(intel.news_articles, 1):
                title_zh = article_title_zh(art)
                date_part = f"（{art.date}）" if art.date else ""
                lines.append(f"  {idx}. [{title_zh}]({art.url}){date_part}")
            n_all = len(intel.all_news_articles)
            if n_all > len(intel.news_articles):
                lines.append(f"  - 📄 完整文章归档（共 {n_all} 篇）："
                             f"[{intel.vendor_id}.md](llm-news/{intel.vendor_id}.md)")
        else:
            lines.append("- ⚠️ 本次未提取到文章条目，请直接访问上方页面或官方 X / 公众号查看更新")
        lines.append("")

    lines.append(f"---")
    lines.append(f"共整理 {len(vendors_with_news)} 个厂商的动态入口（其中 {vendors_with_articles} 个"
                 f"成功提取最新文章），RSS/Atom 源 {feed_count} 个。")
    lines.append("")
    lines.append(NEWS_END)
    lines.append("")
    return "\n".join(lines)


def update_news_md(path: Path, section: str) -> bool:
    """刷新博客主文档；屏蔽时间戳/抓取日期后无变化则不写文件。返回是否写入。"""
    if path.exists():
        old = path.read_text(encoding="utf-8")
    else:
        old = "# LLM 厂商博客 / 更新动态订阅源\n\n"
    pattern = re.compile(
        re.escape(NEWS_BEGIN) + r".*?" + re.escape(NEWS_END) + r"\n?",
        re.DOTALL,
    )
    if pattern.search(old):
        new = pattern.sub(section, old)
    else:
        new = old.rstrip("\n") + "\n\n" + section

    def mask(s: str) -> str:
        s = _TS_RE.sub("__TS__", s)
        return re.sub(r"抓取于 \d{4}-\d{2}-\d{2}", "抓取于 __DATE__", s)

    if path.exists() and mask(new) == mask(old):
        return False
    path.write_text(new, encoding="utf-8", newline="\n")
    return True


def write_opml(path: Path, intel_list: list[VendorIntel], feeds_base: str = "",
               merged_limit: int = RSS_MERGED_LIMIT) -> int:
    """将发现的 RSS/Atom 源写成 OPML（可导入 RSS 阅读器）。返回订阅源总数。

    OPML 是读者真正会**导入**的那份清单，所以它必须覆盖"我能订到的全部"，而不只是
    "厂商官网自带的那些"：实测官网有原生 RSS 的只有 3/15，另外 12 家官方页面根本没有
    feed —— 而本仓库恰恰为它们自建了订阅源。只列原生源的清单会让人以为其余 12 家订不了。

    因此 feeds_base 非空（即线上 / CI）时再追加两组：
    - 「自建源」：**只收没有原生源的那几家**。有原生源的厂商不重复收录 —— 自建源内容
      与其原生源重叠，两组都订会在阅读器里出现重复条目。
    - 「聚合流」：合并流，单条订阅即可覆盖全部有动态源的厂商；与上面各组同样重叠，
      单独成组便于读者按需只勾一个。

    merged_limit 只用于条目文案里的「最近 N 条」——必须跟 `write_rss_feeds` 实际用的
    上限一致，否则 `--rss-limit` 一改，清单上的数字就是错的。
    """
    outlines: list[tuple[str, str, str, str]] = []  # (brand, title, xmlUrl, htmlUrl)
    seen_feeds: set[str] = set()
    for intel in intel_list:
        for page in intel.news_pages:
            if not page.ok:
                continue
            html_url = page.final_url or page.url
            # 显式 type=feed 的源本身就是订阅地址；其余页面取 HTML 中发现的 feed 链接
            page_feeds = [page.final_url or page.url] if page.stype == "feed" else list(page.feeds)
            for feed in page_feeds:
                if not feed or feed in seen_feeds:
                    continue
                seen_feeds.add(feed)
                label = TYPE_LABELS.get(page.stype, page.stype)
                title = f"{intel.brand} - {label}"
                outlines.append((intel.brand, title, feed, html_url))

    def esc(s: str) -> str:
        return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                .replace('"', "&quot;"))

    def group(title: str, rows: list[tuple[str, str, str]]) -> list[str]:
        """一组 outline；rows 为 (显示名, xmlUrl, htmlUrl)。"""
        out = [f'    <outline text="{esc(title)}" title="{esc(title)}">']
        for name, xml_url, html_url in rows:
            out.append(
                f'      <outline type="rss" text="{esc(name)}" title="{esc(name)}" '
                f'xmlUrl="{esc(xml_url)}" htmlUrl="{esc(html_url)}"/>'
            )
        out.append("    </outline>")
        return out

    # 自建源：只收官网没有原生 RSS 的厂商（有原生源的不重复收录，避免阅读器里出现重复条目）
    native_ids = _native_feed_vendors(intel_list)
    site = _feeds_site_base(feeds_base)
    today = datetime.now().strftime("%Y-%m-%d")
    self_hosted: list[tuple[str, str, str]] = []
    if feeds_base:
        for intel in intel_list:
            # 判据与 write_rss_feeds 出源的判据同源（_rss_articles）：否则文章日期全被
            # 误写成未来的厂商会在这里列出、却没有对应的源文件（死链）。
            if intel.vendor_id in native_ids or not _rss_articles(intel, today):
                continue
            self_hosted.append((
                f"{intel.brand} - 自建源（官方没有原生 RSS）",
                f"{feeds_base}/llm-news-{intel.vendor_id}.xml",
                site or feeds_base,
            ))

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<opml version="2.0">',
        "  <head>",
        "    <title>LLM 厂商博客 / 更新动态订阅源</title>",
        f"    <dateCreated>{esc(now)}</dateCreated>",
        "  </head>",
        "  <body>",
    ]
    lines += group("LLM Vendors · 官方原生源", [(t, x, h) for _b, t, x, h in outlines])
    if self_hosted:
        lines += group("LLM Vendors · 自建源（官方没有原生 RSS）", self_hosted)
        lines += group("LLM Vendors · 聚合流（订阅这一个 = 全部有动态源的厂商）", [(
            "全部厂商 - 合并流（%s，带厂商前缀）" % merged_scope_text(merged_limit),
            f"{feeds_base}/llm-news-all.xml",
            site or feeds_base,
        )])
    lines.append("  </body>")
    lines.append("</opml>")
    content = "\n".join(lines) + "\n"
    total = len(outlines) + len(self_hosted) + (1 if self_hosted else 0)
    if path.exists():
        old = path.read_text(encoding="utf-8")
        masked = re.sub(r"<dateCreated>[^<]*</dateCreated>",
                        "<dateCreated>__TS__</dateCreated>", old)
        if masked == re.sub(r"<dateCreated>[^<]*</dateCreated>",
                            "<dateCreated>__TS__</dateCreated>", content):
            return total
    path.write_text(content, encoding="utf-8", newline="\n")
    return total


# 标题用贪婪 `(.+)` 而不是 `[^\]]+`：标题里可能出现方括号（实测 huggingface 有 3 篇
# "Director of Machine Learning Insights [Part 4]"），`[^\]]+` 会停在第一个 `]` 上导致
# **整行失配** —— 这些条目既进不了 RSS，又因为增量合并靠这个正则读回旧归档而可能被静默
# 丢掉（归档"只增不减"的保证会被破坏）。贪婪匹配会一直回溯到最后一个 `](http…`，
# 尾部锚定保证不会多吞。
_ARCHIVE_ARTICLE_RE = re.compile(r"^\d+\.\s+\[(.+)\]\((https?://[^)]+)\)(?:（([^）]+)）)?$")


def parse_archived_articles(arch_path: Path) -> list[Article]:
    """从既有归档 .md 中恢复历史文章条目（供增量合并，保障历史旧文章只增不减、永久留存）。"""
    if not arch_path.exists():
        return []
    articles: list[Article] = []
    try:
        for line in arch_path.read_text(encoding="utf-8").splitlines():
            m = _ARCHIVE_ARTICLE_RE.match(line.strip())
            if m:
                title, url, date_val = m.group(1), m.group(2), m.group(3) or ""
                articles.append(Article(title=title, url=url,
                                        date=_drop_future_date(date_val)))
    except Exception:
        pass
    return articles


# ---------------------------------------------------------------------------
# 归档日期回填（维护模式 --backfill-dates，不参与日常巡检）
# ---------------------------------------------------------------------------

#: 单次回填最多访问的文章页数（礼貌抓取：0.5s 间隔；只补缺日期的历史条目）
DATE_BACKFETCH_LIMIT = 150


def resolve_article_date(html: str) -> str:
    """从文章页 HTML 里解发布日期：JSON-LD datePublished / OG 时间戳 / <time>。

    各家格式不同但都遵循其中一两个公开约定；解不出返回空串（维持无日期，
    绝不猜）。年份 <2000 视为噪声（部分页 datePublished 写成占位 0001-01-01）。
    """
    if not html:
        return ""
    cands: list[str] = []
    m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', html)
    if m:
        cands.append(m.group(1))
    m = re.search(r'property="article:published_time"\s+content="([^"]+)"', html)
    if m:
        cands.append(m.group(1))
    m = re.search(r"<time[^>]*datetime=\"([^\"]+)\"", html)
    if m:
        cands.append(m.group(1))
    for raw in cands:
        day = normalize_feed_date(raw)
        if day and day >= "2000-01-01":
            return day
    return ""


def backfill_archive_dates(news_dir: Path, fetch,
                           limit: int = DATE_BACKFETCH_LIMIT,
                           delay: float = 0.5) -> tuple[int, int]:
    """给归档里无日期的条目回填发布日期（visit 文章页取 meta）。

    fetch: url -> HTML 文本（注入以便测试；网络错误抛异常按「解不出」处理）。
    返回 (访问数, 回填数)。条目按原顺序处理，回填后重写日期括号。
    """
    import time as _time
    visited = fixed = 0
    for arch in sorted(news_dir.glob("*.md")):
        try:
            text = arch.read_text(encoding="utf-8")
        except OSError:
            continue
        lines = text.splitlines(keepends=True)
        dirty = False
        for i, line in enumerate(lines):
            m = re.match(r"^(\d+\.\s+\[.+\]\(https?://[^)]+\))(（[^）]*）)?\s*$", line)
            if not m or m.group(2):
                continue  # 非条目行 / 已有日期后缀
            if visited >= limit:
                break
            url = re.search(r"\]\((https?://[^)]+)\)", m.group(1)).group(1)
            try:
                html = fetch(url)
            except Exception:
                html = ""
            visited += 1
            day = resolve_article_date(html or "")
            if not day:
                continue
            lines[i] = m.group(1) + f"（{day}）\n"
            fixed += 1
            dirty = True
            _time.sleep(delay)
        if dirty:
            # 只写日期括号，不在此处重排 —— 顺序规范由 --rebuild-only / 下次巡检的
            # write_news_archives 统一完成（日期倒序 + 重编号），避免两处排序逻辑漂移。
            arch.write_text("".join(lines), encoding="utf-8", newline="\n")
    return visited, fixed


def _parse_news_md_page_states(news_md_text: str) -> dict[str, list[dict]]:
    """从上次渲染的 llm-news-feeds.md 里恢复每个厂商的动态页状态。

    原生 RSS 检测结果（page.feeds）、稀疏 / 失败标记只存在于抓取现场，产物是它们
    唯一的落盘记录；--rebuild-only 靠这份解析把 `intel.news_pages` 重建回渲染时的
    形状，使自建源标注与 OPML 分组不漂移。
    返回 {vendor_id: [{url, final_url, label, feeds, ok, sparse}, ...]}（保持文档顺序）。
    """
    blocks: dict[str, list[dict]] = {}
    rows: list[dict] | None = None
    pending: dict | None = None
    for line in news_md_text.splitlines():
        m = re.match(r"^### .+ \((\w+)\)\s*$", line)
        if m:
            rows = blocks.setdefault(m.group(1), [])
            pending = None
            continue
        if rows is None:
            continue
        m = re.match(r"^- 📡 \[([^\]]*)\]\((\S+)\)：`(\S+)`", line)
        if m:
            rows.append({"url": m.group(2), "final_url": m.group(3),
                         "label": m.group(1), "feeds": [], "ok": True,
                         "sparse": False})
            pending = None
            continue
        m = re.match(r"^- 页面：\[([^\]]*)\]\((\S+)\)", line)
        if m:
            pending = {"url": m.group(2), "final_url": "",
                       "label": m.group(1), "feeds": [], "ok": True,
                       "sparse": False}
            rows.append(pending)
            continue
        m = re.match(r"^\s+- 📡 RSS/Atom：(\S+)\s*$", line)
        if m and pending is not None:
            pending["feeds"].append(m.group(1))
            continue
        if re.match(r"^\s+- ⚠️ 页面可见文本过少", line) and pending is not None:
            pending["sparse"] = True
            continue
        if re.match(r"^\s+- ❌ 抓取失败", line) and pending is not None:
            pending["ok"] = False
    return blocks


def rebuild_intel_from_disk(vendors: list[dict], grouped: dict[str, list[dict]],
                            page_states: dict[str, list[dict]],
                            news_dir: Path,
                            orig_by_key: dict[tuple[str, str], str] | None = None,
                            ) -> list["VendorIntel"]:
    """不触网，从磁盘产物重建 `intel_list`（--rebuild-only 的入口）。

    三个数据源各司其职：yaml 供厂商元数据与 stype（决定 type_label 渲染）；
    llm-news-feeds.md 供各动态页的原生 feed / 失败状态；llm-news/*.md 供全量文章
    与中文标题（articles.json 供英文原文，见 orig_by_key）。
    不在任何产物里出现的厂商直接跳过：本模式只重建动态类产物，不生成情报页内容。
    """
    orig_by_key = orig_by_key or {}
    intel_list: list[VendorIntel] = []
    for vendor in vendors:
        vid = vendor.get("id", "unknown")
        news_urls = grouped.get(vid, [])
        states = page_states.get(vid, [])
        arch_path = news_dir / f"{vid}.md"
        arts = parse_archived_articles(arch_path)
        if not states and not arts:
            continue
        intel = VendorIntel(vendor_id=vid, brand=vendor.get("brand", vid),
                            homepage=vendor.get("homepage", ""),
                            products=vendor.get("products") or [])
        # 页清单以 yaml 为权威、产物状态只做富化：
        # ① 换源（如 groq `changelog` → `changelog.md`）时产物还记着旧 URL，按去 `.md`
        #    后缀归一匹配上，检测到的原生 feed 不丢；
        # ② yaml 新增的源（产物里从没有过）直接按声明建页，新厂商首轮即出总览条目，
        #    不必等下一次实抓把 feeds.md 补上（feed 发现留待实抓富化）。
        def _n(u: str) -> str:
            return u[:-3] if u.endswith(".md") else u
        state_by_url = {_n(st["url"]): st for st in states}
        for s in news_urls:
            u = s.get("url") or ""
            if (s.get("type") or "") not in NEWS_TYPES or not u:
                continue
            st = state_by_url.get(_n(u))
            page = PageResult(
                url=u, stype=s.get("type") or "",
                ok=bool(st["ok"]) if st else True,
                final_url=st["final_url"] if st else "",
                feeds=list(st["feeds"]) if st else [],
                sparse=bool(st["sparse"]) if st else False)
            intel.news_pages.append(page)
        intel.all_news_articles = arts
        for a in arts:
            # 归档 .md 里存的是**中文显示标题**（= 上次的 title_zh）；英文原文只在
            # articles.json 的 original_title 列里。重建时把中文落成 zh_title、原文回填
            # 到 art.title，与正常抓取路径的不变量一致（title=原文、zh_title=译文），
            # 于是 _rss_item 的「原文标题」与索引第 5 列都能逐字节复现。
            if _CJK_CHAR_RE.search(a.title):
                a.zh_title = a.title
                orig = orig_by_key.get((vid, a.url))
                if orig and orig != a.title:
                    a.title = orig
        intel.news_articles = arts[:5]
        intel_list.append(intel)
    return intel_list


def load_original_titles(articles_json_path: Path) -> dict[tuple[str, str], str]:
    """从既有 docs/feeds/articles.json 读回 {(vendor_id, url): 英文原文标题}。

    归档 .md 只保存中文显示标题，英文原文唯一的落盘处就是这份索引；--rebuild-only
    靠它把原文回填进 Article，否则重建的 RSS / 索引会丢失「原文标题」。
    """
    out: dict[tuple[str, str], str] = {}
    try:
        data = json.loads(articles_json_path.read_text(encoding="utf-8"))
    except Exception:
        return out
    fields = data.get("fields") or []
    if "original_title" not in fields or "url" not in fields or "vendor" not in fields:
        return out
    ti, ui, vi, oi = (fields.index(k) for k in ("title", "url", "vendor", "original_title"))
    for row in data.get("articles") or []:
        if len(row) <= oi:
            continue
        orig = (row[oi] or "").strip() or (row[ti] or "").strip()
        if orig:
            out[(row[vi], row[ui])] = orig
    return out


def write_news_archives(out_dir: Path, intel_list: list[VendorIntel],
                       clean_removed: bool = True, title_polish=None) -> tuple[int, int, int]:
    """把每个厂商的全量文章写到 llm-news/<vendor_id>.md 子文档。

    返回 (归档文件数, 文章总数, 实际改写文件数)。自动将新抓取的文章与既有归档增量
    合并，保障旧文章永不丢失；标题汉化走 translate_to_zh（磁盘缓存 + 并发）。
    title_polish 非空时，对**新收录**（归档里没这个 URL）且仍是英文的标题调用一次润色（brand, titles)
    -> {英文: 中文}，结果写进 zh_title 随归档冻结（见 --ai-titles）。
    屏蔽「抓取于」日期后与旧文件比对，无内容变化则不重写（避免无变化日产生 diff）。
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    if clean_removed:
        current_ids = {v.vendor_id for v in intel_list if v.all_news_articles}
        # 清理已下线厂商的旧归档
        for old in out_dir.glob("*.md"):
            if old.stem not in current_ids:
                old.unlink()
    files = 0
    files_changed = 0
    total_articles = 0
    for intel in intel_list:
        arch_path = out_dir / f"{intel.vendor_id}.md"
        # 1) 增量合并既有归档：新抓取排前，历史已有且本次未抓到的条目追加在后，永不丢失
        existing = parse_archived_articles(arch_path)
        merged_arts: list[Article] = list(intel.all_news_articles)
        by_url = {_article_key(a.url): a for a in merged_arts}
        old_urls = {_article_key(o.url) for o in existing}
        for old_art in existing:
            # 已废弃源的历史条目不再保留（见 RETIRED_NEWS_URL_PREFIXES）
            if _is_retired_news_url(old_art.url):
                continue
            u_norm = _article_key(old_art.url)
            fresh = by_url.get(u_norm)
            if fresh is None:
                by_url[u_norm] = old_art
                merged_arts.append(old_art)
                continue
            if not fresh.date and old_art.date:
                # 本次抓取没拿到日期（页面卡片改版、标题被截断等），沿用归档里已有的：
                # 日期一旦丢失就永久丢失（归档排序、RSS pubDate、README 展示都依赖它），
                # 而且重抓也补不回来 —— 实测 cohere 博客页改版后 9 条会退化成无日期。
                fresh.date = old_art.date
            if (not fresh.zh_title and _CJK_CHAR_RE.search(old_art.title)
                    and old_art.title != fresh.title):
                # 归档里已有人工/AI 汉化过的中文标题 → 沿用，别让每日重抓把它退回
                # Google 机翻（CI 端 .translate_cache.json 不随仓库走，实测
                # 「GPT-6 的提示缓存全面升级」隔天变「更好的 GPT-6 提示缓存」）。
                # 代价：官方日后改标题会停在旧文案，但这种情况极少且可人工修。
                fresh.zh_title = old_art.title
        # 2) 新收录且尚无中文的标题 → 交给 LLM 润色一次（结果进归档即冻结，
        #    次日走上面的沿用分支不再重翻）。polisher 内部分批与预算，异常在此兜底。
        if title_polish is not None:
            new_en = [a.title for a in merged_arts
                      if not a.zh_title and _article_key(a.url) not in old_urls
                      and not _CJK_CHAR_RE.search(a.title)]
            if new_en:
                try:
                    polished = title_polish(intel.brand, new_en) or {}
                except Exception as exc:
                    print(f"      [ai-titles] {intel.brand}：润色整体失败，回落机翻"
                          f"（{type(exc).__name__}: {exc}）", file=sys.stderr)
                    polished = {}
                for a in merged_arts:
                    zh = polished.get(a.title)
                    if zh and not a.zh_title:
                        a.zh_title = zh
        dated = sorted((a for a in merged_arts if a.date),
                       key=lambda a: a.date, reverse=True)
        undated = [a for a in merged_arts if not a.date]
        arts = dated + undated
        intel.all_news_articles = arts
        intel.news_articles = arts[:5]
        if not arts:
            continue
        with ThreadPoolExecutor(max_workers=6) as pool:
            titles_zh = list(pool.map(article_title_zh, arts))
        lines: list[str] = []
        lines.append(f"# {intel.brand} 文章归档")
        lines.append("")
        lines.append(f"> 由 `crawler_llm_intel.py` 自动整理，抓取于 **{today}**"
                     "（标题自动汉化、附发布日期与原文链接）。")
        lines.append(f"> 厂商：{intel.brand}（`{intel.vendor_id}`） ｜ "
                     "[返回订阅源总览](../llm-news-feeds.md)")
        lines.append("")
        lines.append("## 订阅入口")
        lines.append("")
        for page in intel.news_pages:
            label = type_label(page.stype)
            if page.stype == "feed":
                lines.append(f"- 📡 RSS/Atom：[{label}]({page.final_url or page.url})")
            else:
                lines.append(f"- 页面：[{label}]({page.url})")
        lines.append("")
        lines.append(f"## 全部文章（共 {len(arts)} 篇，按日期倒序；无日期条目列于最后）")
        lines.append("")
        for art_idx, (art, title_zh) in enumerate(zip(arts, titles_zh), 1):
            date_part = f"（{art.date}）" if art.date else ""
            lines.append(f"{art_idx}. [{title_zh}]({art.url}){date_part}")
        lines.append("")
        content = "\n".join(lines)
        arch_path = out_dir / f"{intel.vendor_id}.md"
        # 仅屏蔽「抓取于」日期；文章自身的发布日期属于内容，变化必须写入
        mask = lambda s: re.sub(r"抓取于 \*\*\d{4}-\d{2}-\d{2}\*\*",
                                "抓取于 **__DATE__**", s)
        if arch_path.exists() and mask(arch_path.read_text(encoding="utf-8")) == mask(content):
            pass
        else:
            arch_path.write_text(content, encoding="utf-8", newline="\n")
            files_changed += 1
        files += 1
        total_articles += len(arts)
    return files, total_articles, files_changed


# ---------------------------------------------------------------------------
# 自建 RSS 订阅源（llm-news/ 归档 → RSS 2.0，托管在 GitHub Pages）
# ---------------------------------------------------------------------------

def default_feeds_base() -> str:
    """推导订阅源的对外前缀（GitHub Pages 地址）。

    Actions 会注入 GITHUB_REPOSITORY=owner/repo：项目页的 Pages 根是
    https://owner.github.io/repo/，而项目主页仓（owner.github.io）本身就是根。
    本地运行拿不到该变量时返回空串——此时省略 <atom:link rel="self">，
    对任何阅读器都没有影响。
    """
    slug = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if "/" not in slug:
        return ""
    owner, repo = slug.split("/", 1)
    if not owner or not repo:
        return ""
    if repo.lower() == f"{owner.lower()}.github.io":
        return f"https://{owner}.github.io/feeds"
    return f"https://{owner}.github.io/{repo}/feeds"


def _feeds_site_base(feeds_base: str) -> str:
    """由订阅源前缀反推**浏览页**地址（docs/index.html 的对外 URL）。

    feeds_base 形如 `https://owner.github.io/repo/feeds`，而浏览页在站点根：
    `https://owner.github.io/repo/`。空串（本地运行）时返回空串，调用方据此省略链接
    —— 与 feeds_base 一样，不猜域名。
    """
    if not feeds_base:
        return ""
    if feeds_base.endswith("/feeds"):
        return feeds_base[: -len("/feeds")] + "/"
    return feeds_base.rstrip("/") + "/"


def _rss_esc(text: str) -> str:
    """XML 文本 / 属性转义（与 write_opml 内的 esc 同源，独立出来供 item 复用）。"""
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&apos;"))


def _rss_pubdate(day: str) -> str:
    """YYYY-MM-DD → RFC 822（RSS pubDate 要求的格式），按当天 UTC 00:00 解释。"""
    try:
        dt = datetime.strptime(day, "%Y-%m-%d")
    except (TypeError, ValueError):
        return ""
    return format_datetime(dt.replace(tzinfo=timezone.utc))


def _rss_title(title: str) -> tuple[str, str]:
    """返回 (订阅源里的标题, 需要移入 description 的完整原文)。

    归档里有一批「标题其实是整段正文」的脏数据（页面锚文本提取所致，约占 5.8%），
    另有以 … 结尾的截断标题。原样塞进阅读器会撑爆列表，因此超长标题截断、
    完整文本改放 description——信息不丢，列表可读。
    """
    text = title.strip()
    if len(text) <= RSS_TITLE_MAX and not text.endswith("…"):
        return text, ""
    return text[:RSS_TITLE_MAX].rstrip() + "…", text


def _rss_item(art: Article, title_zh: str, brand: str = "",
              source_url: str = "") -> str:
    """单条 <item>；合并流传 brand 以加厂商前缀与 <category>，便于阅读器过滤。

    source_url 非空时额外写 <source url>：RSS 2.0 用它标注"这条来自哪个源"。
    这里指向该厂商的单厂商订阅源，于是合并流**自描述**了厂商→源的映射 ——
    docs/index.html 的浏览页据此生成「按厂商订阅」链接，无需硬编码厂商清单
    （硬编码会随厂商增删而漂移）。
    """
    short, truncated_from = _rss_title(title_zh)
    if brand:
        short = f"[{brand}] {short}"
    notes: list[str] = []
    if truncated_from:
        notes.append(f"完整标题：{truncated_from}")
    if art.title.strip() and art.title.strip() != title_zh.strip():
        notes.append(f"原文标题：{art.title.strip()}")
    lines = [
        "    <item>",
        f"      <title>{_rss_esc(short)}</title>",
        f"      <link>{_rss_esc(art.url)}</link>",
        f'      <guid isPermaLink="true">{_rss_esc(art.url)}</guid>',
    ]
    pub = _rss_pubdate(art.date)
    if pub:
        lines.append(f"      <pubDate>{pub}</pubDate>")
    if brand:
        lines.append(f"      <category>{_rss_esc(brand)}</category>")
    if brand and source_url:
        lines.append(f'      <source url="{_rss_esc(source_url)}">{_rss_esc(brand)}</source>')
    if notes:
        lines.append(f"      <description>{_rss_esc(' | '.join(notes))}</description>")
    lines.append("    </item>")
    return "\n".join(lines)


def _rss_channel(title: str, description: str, items: list[str], self_url: str,
                 build_date: str, site_url: str = REPO_URL) -> str:
    head = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "  <channel>",
        f"    <title>{_rss_esc(title)}</title>",
        f"    <link>{_rss_esc(site_url)}</link>",
        f"    <description>{_rss_esc(description)}</description>",
        "    <language>zh-cn</language>",
        "    <generator>crawler_llm_intel.py (free-llm-intel)</generator>",
    ]
    if self_url:
        head.append(f'    <atom:link href="{_rss_esc(self_url)}" rel="self"'
                    ' type="application/rss+xml"/>')
    # lastBuildDate 取最新文章日期而不是当前时间：产物因此是确定性的，
    # 内容没变时不会因为「又跑了一次」而改写文件（同 write_opml 的 dateCreated 屏蔽）。
    pub = _rss_pubdate(build_date)
    if pub:
        head.append(f"    <lastBuildDate>{pub}</lastBuildDate>")
    return "\n".join(head + items + ["  </channel>", "</rss>", ""])


def _rss_mask_builddate(text: str) -> str:
    return re.sub(r"<lastBuildDate>[^<]*</lastBuildDate>",
                  "<lastBuildDate>__T__</lastBuildDate>", text)


def _write_json(path: Path, payload: dict) -> bool:
    """确定性 JSON 落盘：键序固定、不含时间戳，内容无变化则不重写。

    与 `_rss_write` 同一套约定 —— 否则每天巡检都会因为「又跑了一次」刷出无意义 diff。
    换行显式写 `\n`：Windows 上 `write_text` 默认转 CRLF，会让整个文件看起来全改了。
    """
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if path.exists():
        try:
            if path.read_text(encoding="utf-8") == text:
                return False
        except Exception:
            pass
    path.write_text(text, encoding="utf-8", newline="\n")
    return True


def _rss_write(path: Path, content: str) -> bool:
    """内容无变化则不重写（屏蔽 lastBuildDate 后比对）。返回是否实际改写。"""
    if path.exists():
        try:
            old = _rss_mask_builddate(path.read_text(encoding="utf-8"))
            if old == _rss_mask_builddate(content):
                return False
        except Exception:
            pass
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def write_rss_feeds(out_dir: Path, intel_list: list[VendorIntel], base_url: str = "",
                    merged_limit: int = RSS_MERGED_LIMIT,
                    clean_removed: bool = True) -> tuple[int, int, int, int]:
    """把各厂商归档文章写成 RSS 2.0 订阅源（GitHub Pages 托管）。

    产出 `<out_dir>/llm-news-all.xml`（合并流，最近 merged_limit 条）与每厂商一个
    `<out_dir>/llm-news-<vendor_id>.xml`（等于该厂商全量归档，新订阅者可一次补齐历史）。

    日期规则：
      * **晚于今天**的日期必然是源页面写错了（真实案例：cohere 一篇 2026-07-10 的文章，
        博客卡片上印着 "Dec 10, 2026"，归档里已就地修正为 2026-07-10），一律排除——
        RSS 是按时间排序的流，一条未来日期会永远钉在列表顶端；
      * **无日期**的条目只进单厂商源（不写 pubDate、排在末尾），不进合并流：合并流是
        「最近更新」，没有日期的条目无法参与排序。归档 .md 里它们同样列在最后。
    若把无日期条目一并丢弃，Google Gemini / Meta Llama 这类整源都抓不到日期的厂商会直接
    没有订阅源——那还不如不做。被排除的条数会打印出来，让上游日期提取问题暴露在巡检日志里。

    返回 (源文件数, 收录条目数, 实际改写文件数, 因未来日期被排除的条目数)。
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    base = base_url.rstrip("/")
    today = datetime.now().strftime("%Y-%m-%d")

    # 标题汉化走 translate_to_zh 的磁盘缓存（.translate_cache.json）：归档过的标题
    # 全部命中缓存，不产生额外翻译请求。
    per_vendor: list[tuple[str, str, list[Article], list[str]]] = []
    skipped = 0
    for intel in intel_list:
        # 判据与 OPML / llm-news-feeds.md 的自建源标注共用 `_rss_articles`：
        # 三处必须一致，否则文档会标注出并不存在的源（或漏标真实存在的源）。
        arts = _rss_articles(intel, today)
        skipped += len(intel.all_news_articles) - len(arts)
        if not arts:
            continue
        with ThreadPoolExecutor(max_workers=6) as pool:
            titles_zh = list(pool.map(article_title_zh, arts))
        per_vendor.append((intel.brand, intel.vendor_id, arts, titles_zh))

    if clean_removed:
        current_ids = {row[1] for row in per_vendor}
        for old in out_dir.glob("llm-news-*.xml"):
            if old.name == "llm-news-all.xml":
                continue
            if old.stem.removeprefix("llm-news-") not in current_ids:
                old.unlink()

    files = items = changed = 0

    # 1) 合并流：只取有日期的条目，跨厂商按日期倒序，同一 URL 只留一条
    #    （不同厂商可能转发同一份公告）
    merged: list[tuple[str, str, Article, str]] = []
    for brand, vid, arts, titles_zh in per_vendor:
        merged.extend((brand, vid, art, t) for art, t in zip(arts, titles_zh) if art.date)
    merged.sort(key=lambda row: row[2].date, reverse=True)
    seen: set[str] = set()
    picked: list[tuple[str, str, Article, str]] = []
    for row in merged:
        key = _article_key(row[2].url)
        if key in seen:
            continue
        seen.add(key)
        picked.append(row)
        if merged_limit and len(picked) >= merged_limit:  # 0 = 不限制
            break
    if picked:
        # 每条带上「本厂商单源」地址，让合并流自描述厂商→源映射（见 _rss_item 注释）
        items_xml = [_rss_item(art, title_zh, brand,
                              f"{base}/llm-news-{vid}.xml" if base else "")
                     for brand, vid, art, title_zh in picked]
        files += 1
        items += len(items_xml)
        changed += _rss_write(
            out_dir / "llm-news-all.xml",
            _rss_channel(
                "LLM 厂商动态（合并流）",
                f"汇总 {len(per_vendor)} 家 LLM 厂商官方博客 / 更新日志的新文章，标题已汉化；"
                "官方没有 RSS 的厂商也在这里（由 free-llm-intel 定时巡检官方页面归档生成）。",
                items_xml, f"{base}/llm-news-all.xml" if base else "", picked[0][2].date))

    # 2) 每厂商单源：等于该厂商全量归档
    for brand, vendor_id, arts, titles_zh in per_vendor:
        items_xml = [_rss_item(art, t) for art, t in zip(arts, titles_zh)]
        files += 1
        items += len(items_xml)
        changed += _rss_write(
            out_dir / f"llm-news-{vendor_id}.xml",
            _rss_channel(
                f"{brand} 官方动态",
                f"{brand} 官方博客 / 更新日志归档（标题汉化，共 {len(items_xml)} 篇），"
                "由 free-llm-intel 定时巡检官方页面生成。",
                items_xml, f"{base}/llm-news-{vendor_id}.xml" if base else "",
                arts[0].date))

    # 3) 厂商索引：供浏览页 docs/index.html 列出**全部**厂商的订阅入口。
    #    光靠合并流是不够的 —— 合并流有 200 条上限、且只收有日期的条目，于是
    #    「文章全无日期」（google_gemini / meta_llama）或「文章都偏旧、排不进前 200」
    #    （groq）的厂商**根本不会出现**（实测漏 3/15，而这正是"官方没有原生 RSS"
    #    最需要被订到的那几家）。索引由这里顺手产出，与 feed 同源，不存在漂移。
    #    无时间戳：内容不变就不重写。
    #    数组顺序按「模型知名度」（provider_profiles.VENDOR_RANK）排：浏览页的厂商标签
    #    原先自己按**文章数**排，于是 openai / huggingface 永远在最前、baseten / ppio
    #    排在 claude / gemini 之前。排序依据放在这里（而不是页面里），是因为厂商清单
    #    不得硬编码进 docs/index.html —— 页面只读这个字段。
    #    ⚠️ `rank` 是**本索引内的连续序号**（0,1,2…），**不是**它在 VENDOR_RANK 里的
    #    全局位次。用全局位次会得到 0,1,2,…,10,12,15,17,18,49 这种跳号
    #    （VENDOR_RANK 覆盖全部 63 家，而本索引只列「有文章的厂商」），
    #    看上去像数据损坏。页面只需要相对顺序，连续编号即可。
    #    未登记的厂商排在最后，再按 id 保证顺序确定。
    _ordered = sorted(
        (
            {
                "id": vendor_id,
                "brand": brand,
                "feed": f"{base}/llm-news-{vendor_id}.xml" if base
                        else f"llm-news-{vendor_id}.xml",
                "articles": len(arts),
                # arts 已按日期倒序、无日期的排在最后，所以第一条有日期的就是最新日期
                "latest": next((a.date for a in arts if a.date), ""),
            }
            for brand, vendor_id, arts, _t in per_vendor
        ),
        key=lambda v: (vendor_rank_index(v["id"]), v["id"]),
    )
    changed += _write_json(out_dir / "vendors.json", {
        "vendors": [{**item, "rank": i} for i, item in enumerate(_ordered)]
    })

    # 4) 全量文章索引：供浏览页列出**全部**条目，不受合并流 200 条上限约束。
    #    合并流是给**订阅者**的：放开到全量约 1.2 MB（2561 条 × 504 字节），服务端无所谓，
    #    但阅读器每次轮询都要重下重解析，不少阅读器有体积上限 —— 所以「feed 限量、页面全量」。
    #    只放浏览必需的字段，不带描述，体积约为同条数 XML 的 1/3。
    #    第 5 列是**原文标题**（与汉化标题不同时才有值），页面用它做副标题 —— feed 里那
    #    一栏来自 `<description>`，索引不带 description，所以单独带上，免得页面功能倒退。
    #    标题用汉化后的 `titles_zh` 且**不截断**（feed 里截到 60 字是为了列表可读，
    #    页面上可以完整显示）。
    index_rows: list[list[str]] = []
    for _brand, vendor_id, arts, titles_zh in per_vendor:
        for art, t in zip(arts, titles_zh):
            orig = art.title.strip()
            index_rows.append([t, art.url, vendor_id, art.date,
                               orig if orig != t.strip() else ""])
    # 有日期的按日期倒序在前，无日期的排后（与页面/feed 的排序约定一致）。
    # sort 稳定 + 输入顺序确定 → 同样内容每次产出的字节一致，`_write_json` 才不会误判「变了」。
    dated_rows = sorted((r for r in index_rows if r[3]), key=lambda r: r[3], reverse=True)
    undated_rows = [r for r in index_rows if not r[3]]
    index_rows = dated_rows + undated_rows
    files += 1
    changed += _write_json(out_dir / "articles.json", {
        "fields": ["title", "url", "vendor", "date", "original_title"],
        "count": len(index_rows),
        "articles": index_rows,
    })
    return files, items, changed, skipped


# ---------------------------------------------------------------------------
# 情报变更日志：AI 核查采纳的「前值 → 后值」历史（最新在前，产物只追加）
# ---------------------------------------------------------------------------

CHANGELOG_MD = "llm-intel-changelog.md"
CHANGELOG_MAX_VENDORS = 150   # 厂商-天 记录条数上限，超出裁剪最旧日块
CHANGELOG_VALUE_LIMIT = 160   # 单值展示上限，防 free_models 长列表刷爆日志


def _changelog_fmt(value) -> str:
    """档案字段值 → 日志一行的紧凑字符串（列表顿号连接、超长截断）。"""
    if value is None:
        return "（原无此项）"
    if isinstance(value, (list, tuple)):
        text = "、".join(str(v) for v in value)
    elif isinstance(value, dict):
        text = json.dumps(value, ensure_ascii=False)
    else:
        text = str(value)
    text = " ".join(text.split())
    if len(text) > CHANGELOG_VALUE_LIMIT:
        text = text[:CHANGELOG_VALUE_LIMIT - 1] + "…"
    return text


def append_intel_changelog(path: Path, run_date: str, entries: list[dict]) -> int:
    """把本批采纳的变化写进变更日志：同日并入同一日块，新日块置顶。

    entries: [{vendor_id, brand, summary, diffs: [(field, 前值串, 后值串), ...]}]
    （前值由调用方在**应用补丁前**取生效档案格式化，后值取 patch.fields。）
    """
    header = ("# 情报变更日志\n\n"
              "> **产物**（只追加）：AI 核查每日采纳的免费额度事实变化，带前值 → 后值，最新在前。\n"
              f"> 保留最近约 {CHANGELOG_MAX_VENDORS} 条厂商-天记录；人工修订请直接改本文件。\n")
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    tail = existing[existing.find("\n## "):] if "\n## " in existing else ""
    day_blocks: list[list[str]] = []   # 每块 = [日期, *行]
    for b in re.split(r"(?m)^## ", tail)[1:]:
        lines = b.rstrip("\n").splitlines()
        day_blocks.append([lines[0].strip(), *lines[1:]])
    chunks: list[str] = []
    for e in entries:
        chunks.append(f"### {e['brand']}（`{e['vendor_id']}`）")
        chunks.append(f"- 摘要：{e['summary']}")
        for field, old, new in e["diffs"]:
            chunks.append(f"- `{field}`：{old} → {new}")
    idx = next((i for i, blk in enumerate(day_blocks)
                if blk[0] == run_date), None)
    if idx is None:
        day_blocks.insert(0, [run_date, *chunks])
    else:
        day_blocks[idx].extend(chunks)
    # 裁剪：从最新日块起累计厂商块数，超限后的旧日块整块丢弃
    kept: list[list[str]] = []
    count = 0
    for blk in day_blocks:
        n = sum(1 for l in blk[1:] if l.startswith("### "))
        if kept and count + n > CHANGELOG_MAX_VENDORS:
            break
        kept.append(blk)
        count += n
    body = "".join(f"\n## {blk[0]}\n" + "".join(l + "\n" for l in blk[1:])
                   for blk in kept)
    path.write_text(header + body, encoding="utf-8", newline="\n")
    return len(entries)


# ---------------------------------------------------------------------------
# 模型发布雷达：从动态归档标题抽 (厂商, 模型, 日期) 事件（宁可漏不可错）
# ---------------------------------------------------------------------------

#: A 类：`model-id：描述` 结构（更新日志页逐行「新模型上架」的形态）
_RADAR_STRUCT_RE = re.compile(r"^([A-Za-z][A-Za-z0-9+._/-]{1,48})[：:]")
#: B 类：含发布动词的标题里的「品牌词串 + 版本号」token
_RADAR_VERB_RE = re.compile(
    r"发布|上线|推出|新增|添加|登陆|正式版|预览版"
    r"|introducing|now available|released|launches|general availability|\(GA\)",
    re.I)
_RADAR_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9])([A-Z][A-Za-z0-9]*(?:[ \-][A-Z][A-Za-z0-9]*){0,2}"
    r"[ \-]?[Vv]?\d+(?:\.\d+){0,3}[A-Za-z]{0,3}(?:[-][A-Za-z0-9.]+)*)")
#: 公司 / 活动名前缀：型号常挂在它们后面（「Google Gemma 4」的型号是 Gemma 4）
_RADAR_STRIP_PREFIXES = ("Google ", "NVIDIA ", "Meta ", "Microsoft ", "Amazon ",
                         "OpenAI ", "IBM ", "Apple ")
#: 英文标题里的发布引导词，绝不能落在型号开头（「Introducing GPT-5.5」→ GPT-5.5）
_RADAR_INTRO_HEADS = {"Introducing", "Announcing", "Meet", "Launching",
                      "Releasing", "Adding", "Now", "Say"}


def _radar_clean(token: str) -> str:
    for p in _RADAR_STRIP_PREFIXES:
        if token.startswith(p):
            token = token[len(p):]
    words = token.split()
    while words and words[0] in _RADAR_INTRO_HEADS:
        words = words[1:]
    return " ".join(words).strip(" -_.+")


def _radar_bad_model(token: str) -> bool:
    """排除「品牌 + 裸年份」的会议/活动名（ModCon 2026），而非真版本号。

    判据：出现一个以空格或连字符引出、恰为 19xx/20xx 的四位数，且整个 token
    没有点分版本（如 5.3 / 25.08）→ 视为年份而非型号版本。GLM-ASR-2512、
    Hailuo-02 这类非 19/20 开头的数字仍当版本保留。
    """
    if not re.search(r"(?:^|[ \-])(?:19|20)\d\d(?:$|[ \-]|\b)", token):
        return False
    return "." not in token


def _radar_models_from_title(title: str) -> list[str]:
    """从单条标题抽候选型号；A 类命中即止（A 优先，避免同行 B 类重复）。"""
    m = _RADAR_STRUCT_RE.match(title)
    if m and any(c.isdigit() for c in m.group(1)):
        model = m.group(1).rstrip("-_.:")
        if not _radar_bad_model(model):
            return [model]
    if not _RADAR_VERB_RE.search(title):
        return []
    out: list[str] = []
    for tm in _RADAR_TOKEN_RE.finditer(title):
        tok = _radar_clean(tm.group(1))
        if len(tok) < 3 or not any(c.isdigit() for c in tok):
            continue
        if _radar_bad_model(tok):
            continue
        out.append(tok)
    return out


def extract_model_releases(intel_list: list["VendorIntel"]) -> list[dict]:
    """全量归档标题 → 按日期倒序的模型发布/上架事件（无日期条目跳过）。"""
    events: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for intel in intel_list:
        for art in intel.all_news_articles:
            if not art.date:
                continue
            for model in _radar_models_from_title(art.title):
                key = (intel.vendor_id, re.sub(r"[ \-]+", " ", model.lower()))
                if key in seen:
                    continue
                seen.add(key)
                events.append({"date": art.date, "vendor_id": intel.vendor_id,
                               "brand": intel.brand, "model": model,
                               "url": art.url, "title": article_title_zh(art)})
    events.sort(key=lambda e: (e["date"], e["vendor_id"]), reverse=True)
    return events


def write_model_releases(path: Path, events: list[dict]) -> bool:
    """模型发布雷达索引（无时间戳：输入不变产物字节不变）。"""
    payload = json.dumps({
        "fields": ["date", "vendor", "brand", "model", "title", "url"],
        "count": len(events),
        "releases": [[e["date"], e["vendor_id"], e["brand"], e["model"],
                      e["title"], e["url"]] for e in events],
    }, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    if payload == old:
        return False
    path.write_text(payload, encoding="utf-8", newline="\n")
    return True


# ---------------------------------------------------------------------------
# 页面快照变化检测（仅快照、不理解语义；语义判断由 ai_review 的 LLM 完成）
# ---------------------------------------------------------------------------

SNAPSHOT_STATE = "llm-intel-state.json"

#: 例行复查：每次巡检最多顺带核查几家长期未变的厂商（分批轮完存量，控免费层 RPD）
STALE_REVIEW_PER_RUN = 4
#: 默认例行复查周期（天）：一个厂商最久每这么久会被 AI 重新核查一次
STALE_REVIEW_DAYS = 45
SNAPSHOT_TEXT_LIMIT = 60_000

# 只对「含事实信号的行」做快照：整页文本会混入 A/B 版位、CSRF token、时间等噪音，
# 导致 10% 左右的页面每天假性变化。额度政策变动一定落在含下列关键词的行上。
_SNAPSHOT_LINE_RE = re.compile(
    r"免费|额度|限速|速率|频率|配额|计费|收费|价格|定价|赠送|试用|体验金|代金券|实名|信用卡|"
    r"有效期|每月|每日|每周|每 ?\d+ ?小时|滚动重置|永久|限时|积分|"
    r"\d[\d, .]*\s*(万?\s*tokens?|次|积分|小时|元|美元|美金|RPM|RPD|TPM|QPS|CUH|credits?|neurons?|"
    r"requests?(?:\s*/\s*(?:min(?:ute)?|hour|day|month))?|"
    r"requests?\s+per\s+(?:minute|hour|day|month))|"
    r"free|freemium|no credit card|rate ?limit|per month|per day|per minute|per hour|"
    r"\$\s?\d|trial|quota|allowance|monthly|daily|forever|royalty-?free",
    re.I,
)

# 看似含数字信号、实为实时性能/状态计数器的行（如 mancer 的 "10439.1 tokens/sec"），
# 每次抓取都变，必须排除以免假性触发 AI 核查。
_SNAPSHOT_NOISE_RE = re.compile(
    r"tokens?\s*/\s*s(?:ec)?\b|token/s|req(?:uest)?s?\s*/\s*s(?:ec)?\b|"
    r"\d[\d.,]*\s*ms\b|throughput|实时吞吐|当前在线|在线用户",
    re.I,
)


def _snapshot_key(vendor_id: str, page: PageResult) -> str:
    return f"{vendor_id}|{page.stype}|{page.final_url or page.url}"


def _snapshot_fact_text(text: str) -> str:
    kept = []
    for line in (text or "").splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if 4 <= len(line) <= 2000 and _SNAPSHOT_LINE_RE.search(line) \
                and not _SNAPSHOT_NOISE_RE.search(line):
            kept.append(line)
    return "\n".join(kept)[:SNAPSHOT_TEXT_LIMIT]


def _snapshot_hash(text: str) -> str:
    import hashlib
    norm = _snapshot_fact_text(text)
    return hashlib.sha256(norm.encode("utf-8", "ignore")).hexdigest()


class SnapshotState:
    """来源页文本哈希快照。基线运行（状态文件不存在）只建档、不报变化。"""

    def __init__(self, root: Path):
        self.path = root / SNAPSHOT_STATE
        self.baseline = not self.path.exists()
        try:
            data = (json.loads(self.path.read_text(encoding="utf-8"))
                    if self.path.exists() else {})
            self.entries: dict[str, dict] = data.get("sources", {}) or {}
            self.reviews: dict[str, str] = data.get("reviews", {}) or {}
        except (ValueError, OSError):
            self.entries = {}
            self.reviews = {}
        self._staged: dict[str, dict[str, dict]] = {}
        self.changed_pages: dict[str, list[PageResult]] = {}
        # 冷却中的厂商：vid -> (可重试日期, 已失败次数, 最近错误)
        self.cooldown: dict[str, tuple[str, int, str]] = {}

    def stage_vendor(self, vendor_id: str, intel: VendorIntel,
                     ai_enabled: bool = False) -> list[PageResult]:
        # 快照资格只认 requests 阶段的结论（snapshot_ok/snapshot_text），
        # 保证本地带浏览器与 CI --no-browser 两种运行产生完全一致的哈希。
        pages = [p for p in intel.intel_pages
                 if p.ok and p.snapshot_ok and not p.is_login and not p.discovered
                 and p.stype not in NEWS_TYPES and (p.snapshot_text or "").strip()]
        staged: dict[str, dict] = {}
        changed: list[PageResult] = []
        for page in pages:
            key = _snapshot_key(vendor_id, page)
            entry = {"sha256": _snapshot_hash(page.snapshot_text)}
            staged[key] = entry
            old = self.entries.get(key)
            if not self.baseline and (old is None or old.get("sha256") != entry["sha256"]):
                changed.append(page)
        # AI 失败退避：变化条目全部仍在冷却期内时，本次不触发 AI（旧哈希保留），
        # 避免同一批顽固变化每天都消耗免费层 RPD。
        if changed and ai_enabled and not self.baseline:
            today = date.today().isoformat()
            waiting = []
            attempts_seen = 0
            last_err = ""
            for page in changed:
                old = self.entries.get(_snapshot_key(vendor_id, page)) or {}
                retry_after = old.get("ai_retry_after", "")
                if retry_after and retry_after > today:
                    waiting.append(retry_after)
                    attempts_seen = max(attempts_seen, int(old.get("ai_attempts", 0)))
                    last_err = old.get("ai_last_error", "") or last_err
            if len(waiting) == len(changed):
                self._staged.pop(vendor_id, None)
                self.cooldown[vendor_id] = (max(waiting), attempts_seen, last_err[:120])
                return []
        self._staged[vendor_id] = staged
        if changed:
            self.changed_pages[vendor_id] = changed
        return changed

    def commit_vendor(self, vendor_id: str) -> None:
        # 新条目只含 sha256，整体覆盖即同时清除旧的 ai_attempts / ai_retry_after
        self.entries.update(self._staged.pop(vendor_id, {}))

    def rollback_vendor(self, vendor_id: str, bump: bool = False,
                        error: str = "") -> None:
        """AI 核查未通过：保留旧哈希，使下次巡检继续把该厂商标记为变化。

        bump=True 时给变化条目累加失败次数并设置指数退避（1/2/4/7 天），
        防止同一批变化在 AI 持续失败时每天消耗免费层额度。
        """
        staged = self._staged.pop(vendor_id, None)
        self.changed_pages.pop(vendor_id, None)
        if bump and staged:
            today = date.today()
            for key, new_entry in staged.items():
                old = self.entries.get(key)
                if old and old.get("sha256") == new_entry.get("sha256"):
                    continue  # 未变化条目不计数
                if old is None:
                    # 新增来源页首次核查即失败：造占位条目承载冷却状态
                    old = {"sha256": ""}
                    self.entries[key] = old
                n = int(old.get("ai_attempts", 0)) + 1
                wait_days = (1, 2, 4, 7)[min(n - 1, 3)]
                old["ai_attempts"] = n
                old["ai_retry_after"] = (today + timedelta(days=wait_days)).isoformat()
                if error:
                    old["ai_last_error"] = error[:160]

    def mark_reviewed(self, vendor_id: str, when: str | None = None) -> None:
        """记一次 AI 实际核查（页面变了也好、没变也好）——例行复查的时钟从这里走。"""
        self.reviews[vendor_id] = when or date.today().isoformat()

    def stale_vendors(self, vendor_ids: list[str], days: int, today: str) -> list[str]:
        """距上次核查超过 days 天的厂商，最久未查的在前（从未核查视为最久）。"""
        cutoff = (date.fromisoformat(today) - timedelta(days=days)).isoformat()
        stale = [v for v in vendor_ids if self.reviews.get(v, "") <= cutoff]
        stale.sort(key=lambda v: self.reviews.get(v, ""))
        return stale

    def save(self, crawled_ids: set[str], full_run: bool) -> bool:
        # AI 未处理 / 失败的厂商保持旧哈希（未 stage 即自然保留）
        for staged in self._staged.values():
            self.entries.update(staged)
        self._staged.clear()
        if full_run:
            prefixes = tuple(f"{vid}|" for vid in crawled_ids)
            self.entries = {k: v for k, v in self.entries.items()
                            if k.startswith(prefixes)}
        payload = json.dumps({"sources": self.entries, "reviews": self.reviews},
                             ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        old = self.path.read_text(encoding="utf-8") if self.path.exists() else ""
        if payload == old:
            return False
        self.path.write_text(payload, encoding="utf-8", newline="\n")
        return True


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def _repo_root() -> Path:
    """仓库根目录（所有产物的落点）。

    独立成函数是为了**可注入**：`.ai-changed` 与 README 等都写在仓库根，而
    `TestCrawlerCleanup` 要验证「启动时清理历史残留的 `.ai-changed`」——若它只能对着真实
    仓库根跑，就会删掉 workflow「Decide commit path」的判据，CI 里不能跑（此前只能把它
    排除在 CI 之外）。测试改为把本函数 patch 到临时目录，就能在 CI 里跑同一个代码路径。
    """
    return Path(__file__).resolve().parent


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # Windows 控制台中文输出
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="LLM 厂商免费额度 / 活动情报巡检脚本")
    parser.add_argument("--yaml", default="llm-intel.yaml", help="情报 YAML 路径（默认 ./llm-intel.yaml）")
    parser.add_argument("--readme", default="README.md", help="输出 README 路径（默认 ./README.md）")
    parser.add_argument("--news-md", default="llm-news-feeds.md", help="博客/动态清单输出路径")
    parser.add_argument("--news-opml", default="llm-news-feeds.opml", help="RSS OPML 输出路径")
    parser.add_argument("--feeds-dir", default="docs/feeds",
                        help="自建 RSS 输出目录（默认 ./docs/feeds，即 GitHub Pages 的发布目录）")
    parser.add_argument("--feeds-base", default="",
                        help="自建 RSS 的对外前缀；默认按 GITHUB_REPOSITORY 推导 GitHub Pages 地址")
    parser.add_argument("--rss-limit", type=int, default=RSS_MERGED_LIMIT,
                        help=f"合并流最多收录条数（默认 {RSS_MERGED_LIMIT} = **不限制**；"
                             "单厂商源本来就不设上限）")
    parser.add_argument("--delay", type=float, default=0.3, help="每次请求间隔秒数（默认 0.3）")
    parser.add_argument("--timeout", type=float, default=20.0, help="读取超时秒数（默认 20）")
    parser.add_argument("--only", action="append", default=[],
                        help="只巡检指定 vendor_id（可多次使用，调试用；不覆盖全局 README 与新闻总表）")
    parser.add_argument("--no-news", action="store_true", help="跳过博客 / RSS 发现")
    parser.add_argument("--rebuild-only", action="store_true",
                        help="不抓取网络，从磁盘产物（llm-news/*.md 归档 + llm-news-feeds.md）"
                             "重建动态类产物：归档、llm-news-feeds.md、OPML、docs/feeds/*.xml 与索引 JSON。"
                             "改了归档标题后本地刷新产物用这个；README 情报区需要实抓，不会被触碰。"
                             "与 --only / --no-news 互斥")
    parser.add_argument("--no-browser", action="store_true",
                        help="禁用 Playwright 浏览器兜底（默认启用，需 pip install playwright）")
    parser.add_argument("--ai-review", action="store_true",
                        help="检测到官方页面变化时调用 LLM 核查并更新 profile_overrides.json"
                             "（后端 AI_REVIEW_BACKEND=auto|gemini|anthropic，默认 auto："
                             "有 GEMINI_API_KEY 走 Google AI Studio，否则 ANTHROPIC_API_KEY；"
                             "可用 AI_REVIEW_MODEL 覆盖模型）")
    parser.add_argument("--ai-titles", action="store_true",
                        help="新收录文章的机翻标题交给 LLM 润色一次（与 --ai-review 同后端同免费层；"
                             "润色结果写进 llm-news/ 归档后随 zh_title 机制冻结，不逐日重翻）。"
                             "缺 key 时自动跳过并回落 Google 机翻")
    parser.add_argument("--stale-review-days", type=int, default=STALE_REVIEW_DAYS,
                        help=f"页面长期不变时的例行复查周期：距上次 AI 核查超过 N 天的厂商"
                             f"即使哈希未变也进核查队列（每次最多 {STALE_REVIEW_PER_RUN} 家，"
                             f"配合免费层 RPD）。0 = 关闭，只按页面变化核查。默认 {STALE_REVIEW_DAYS}")
    parser.add_argument("--backfill-dates", action="store_true",
                        help="维护模式（不巡检）：逐篇访问归档中**缺发布日期**的文章页，"
                             "从 JSON-LD datePublished / OG / <time> 元数据回填日期；"
                             f"单次上限 {DATE_BACKFETCH_LIMIT} 页礼貌抓取。回填后跑 --rebuild-only 刷新产物")
    args = parser.parse_args(argv)

    root = _repo_root()
    if not args.rebuild_only:
        (root / ".ai-changed").unlink(missing_ok=True)
    if args.backfill_dates:
        session = build_session()

        def _fetch_article(u: str) -> str:
            rr = session.get(u, timeout=(8.0, args.timeout))
            rr.raise_for_status()
            return rr.text
        news_md = (root / args.news_md) if not Path(args.news_md).is_absolute() else Path(args.news_md)
        print(f"[维护] 归档日期回填（只访问缺日期条目的文章页，≤{DATE_BACKFETCH_LIMIT} 页）...")
        visited, filled = backfill_archive_dates(news_md.parent / "llm-news", _fetch_article)
        print(f"      访问 {visited} 页，回填 {filled} 条；"
              "请随后运行 --rebuild-only 重排归档并刷新产物。")
        return 0
    yaml_path = (root / args.yaml).resolve() if not Path(args.yaml).is_absolute() else Path(args.yaml)
    if not yaml_path.exists():
        print(f"[fatal] 找不到 {yaml_path}", file=sys.stderr)
        return 1

    print(f"[1/4] 解析 {yaml_path.name} ...")
    vendors, sources = parse_yaml(yaml_path)
    grouped = group_sources_by_vendor(sources)
    print(f"      vendors={len(vendors)}  sources={len(sources)}  "
          f"覆盖厂商={len(grouped)}")

    if args.only:
        wanted = set(args.only)
        vendors = [v for v in vendors if v.get("id") in wanted]
        missing = wanted - {v.get("id") for v in vendors}
        if missing:
            print(f"[warn] --only 指定的 vendor_id 不存在: {sorted(missing)}", file=sys.stderr)

    if args.rebuild_only and (args.only or args.no_news):
        print("[fatal] --rebuild-only 与 --only / --no-news 互斥（重建本身就是全局动态产物）",
              file=sys.stderr)
        return 2

    session = build_session()
    timeout = (8.0, args.timeout)
    use_browser = not args.no_browser
    if use_browser and not HAS_PLAYWRIGHT and not args.rebuild_only:
        print("[info] 未安装 playwright，禁用浏览器兜底（JS/403 页面将仅标注）。"
              "安装后可自动用真实浏览器渲染：pip install playwright")
    intel_list: list[VendorIntel] = []
    snapshots = SnapshotState(root)
    if snapshots.baseline and not args.rebuild_only:
        print("[info] 快照状态文件不存在：本次为基线建档，只记录页面哈希，不触发 AI 核查。")
    started = time.time()

    news_md_path = (root / args.news_md) if not Path(args.news_md).is_absolute() else Path(args.news_md)
    feeds_dir = (root / args.feeds_dir) if not Path(args.feeds_dir).is_absolute() else Path(args.feeds_dir)
    if args.rebuild_only:
        print("[2/4] --rebuild-only：跳过抓取，从磁盘产物重建 ...")
        news_text = news_md_path.read_text(encoding="utf-8") if news_md_path.exists() else ""
        intel_list = rebuild_intel_from_disk(
            vendors, grouped, _parse_news_md_page_states(news_text),
            news_md_path.parent / "llm-news",
            load_original_titles(feeds_dir / "articles.json"))
        n_arts = sum(len(v.all_news_articles) for v in intel_list)
        print(f"      重建 {len(intel_list)} 个厂商、{n_arts} 篇归档文章（未发起网络请求）。")
    else:
        print(f"[2/4] 开始巡检（{'含博客/RSS 发现' if not args.no_news else '跳过博客/RSS'}；"
              f"浏览器兜底 {'开' if use_browser and HAS_PLAYWRIGHT else '关'}）...")
        with BrowserSession(enabled=use_browser) as browser:
            for idx, vendor in enumerate(vendors, 1):
                vid = vendor.get("id", "unknown")
                brand = vendor.get("brand", vid)
                v_sources = grouped.get(vid, [])
                if args.no_news:
                    v_sources = [s for s in v_sources if s.get("type") not in NEWS_TYPES]
                print(f"  [{idx}/{len(vendors)}] {brand} ({vid}) — {len(v_sources)} 个入口")
                try:
                    intel = crawl_vendor(vendor, v_sources, session, args.delay,
                                         browser=browser)
                except Exception as exc:  # 单厂商失败不终止整体
                    print(f"    [error] 厂商巡检异常，已跳过: {type(exc).__name__}: {exc}",
                          file=sys.stderr)
                    intel = VendorIntel(vendor_id=vid, brand=brand,
                                        homepage=vendor.get("homepage", ""),
                                        products=vendor.get("products") or [])
                intel_list.append(intel)
                changed_pages = snapshots.stage_vendor(vid, intel, ai_enabled=args.ai_review)
                if changed_pages:
                    labels = ", ".join(sorted({p.stype for p in changed_pages}))
                    print(f"    [change] {len(changed_pages)} 个官方页面文本变化（{labels}）")

    if snapshots.cooldown:
        for cid, (retry_after, n, last_err) in sorted(snapshots.cooldown.items()):
            print(f"    [ai-cooldown] {cid}：AI 已连续失败 {n} 次，{retry_after} 前不再重试"
                  f"（免费层额度保护；最近原因：{last_err or '未知'}）", file=sys.stderr)

    elapsed = time.time() - started
    print(f"[3/4] 巡检完成，耗时 {elapsed:.0f} 秒。")

    # ---- 变化触发式 AI 核查 ----
    changed_map = snapshots.changed_pages
    # 例行复查：页面文本长期不变 ≠ 事实不变（限时活动到期、赠金过期都不改版面）。
    # 超过 N 天没被 AI 真正核查过的厂商也进队列；每次巡检限量，让存量厂商分批轮完。
    forced_review: set[str] = set()
    if (args.ai_review and not args.rebuild_only and not snapshots.baseline
            and args.stale_review_days > 0):
        candidates = [v.vendor_id for v in intel_list
                      if v.vendor_id not in changed_map
                      and any(p.ok and p.text.strip() and p.stype not in NEWS_TYPES
                              for p in v.intel_pages)]
        batch = snapshots.stale_vendors(candidates, args.stale_review_days,
                                        date.today().isoformat())
        for vid in batch[:STALE_REVIEW_PER_RUN]:
            changed_map[vid] = []
            forced_review.add(vid)
    ai_patches: dict[str, dict] = {}
    if changed_map:
        n_change = len(changed_map) - len(forced_review)
        bits = []
        if n_change:
            bits.append(f"{n_change} 家页面变化")
        if forced_review:
            bits.append(f"{len(forced_review)} 家例行复查（超 {args.stale_review_days} 天）")
        print(f"      待 AI 核查：{'；'.join(bits)}。")
        if not args.ai_review:
            print("      未启用 --ai-review：仅更新快照（AI 核查需在 CI 或本地带该参数运行）。")
            for intel in intel_list:
                snapshots.commit_vendor(intel.vendor_id)
        else:
            import os
            import ai_review
            try:
                backend = ai_review.resolve_backend()
                backend_err = ""
            except ai_review.AiReviewError as exc:
                backend, backend_err = "", str(exc)
            model = os.environ.get("AI_REVIEW_MODEL") or (
                ai_review.default_model(backend) if backend else "")
            not_ready = backend_err or (ai_review.backend_config_error(backend)
                                        if backend else "")
            if not_ready:
                print(f"      [warn] {not_ready}", file=sys.stderr)
                for vid in list(changed_map):
                    snapshots.rollback_vendor(vid)
            else:
                api_key = ai_review.backend_api_key(backend)
                print(f"      AI 核查后端：{backend}（模型 {model}）")
                intel_by_id = {v.vendor_id: v for v in intel_list}
                pending = list(changed_map.items())
                ai_aborted = False
                consecutive_errors = 0
                ai_max_consecutive_errors = 3
                for pos, (vid, changed_pages) in enumerate(pending):
                    intel = intel_by_id[vid]
                    prof = get_provider_profile(vid, intel.brand, intel.homepage)
                    payload = [
                        {"url": p.final_url or p.url, "stype": p.stype,
                         "title": p.title, "text": p.text}
                        for p in intel.intel_pages
                        if p.ok and p.text.strip() and p.stype not in NEWS_TYPES
                    ]
                    if not payload:
                        snapshots.rollback_vendor(vid)
                        continue

                    def _abort_ai(reason: str) -> None:
                        """停止本次剩余 AI 调用：当前 + 未处理厂商一律保留旧快照。"""
                        nonlocal ai_aborted
                        print(reason, file=sys.stderr)
                        snapshots.rollback_vendor(vid)
                        for rest_vid, _pages in pending[pos + 1:]:
                            snapshots.rollback_vendor(rest_vid)
                        ai_aborted = True

                    try:
                        patch = ai_review.review_vendor(
                            vid, intel.brand, prof, get_guide_meta(vid),
                            payload, api_key=api_key, model=model, backend=backend)
                    except ai_review.AiReviewAbort as exc:
                        # 当日额度耗尽 / 持续限流 / 服务整体故障：不再调用任何厂商
                        tag = ("[ai-outage]" if isinstance(exc, ai_review.AiServiceOutage)
                               else "[ai-quota]")
                        _abort_ai(f"      {tag} {exc}")
                        break
                    except Exception as exc:  # 单厂商失败不阻断；退避后再试，保留旧快照
                        consecutive_errors += 1
                        print(f"      [ai-error] {vid}: {type(exc).__name__}: {exc}",
                              file=sys.stderr)
                        snapshots.rollback_vendor(
                            vid, bump=True, error=f"{type(exc).__name__}: {exc}")
                        if consecutive_errors >= ai_max_consecutive_errors:
                            _abort_ai(
                                "      [ai-abort] AI 连续失败已达 "
                                f"{ai_max_consecutive_errors} 次（Key 无效 / 网络或服务异常？），"
                                "停止本次 AI 核查，其余变化厂商保留旧快照下次重试。")
                            break
                        continue
                    consecutive_errors = 0
                    snapshots.commit_vendor(vid)
                    snapshots.mark_reviewed(vid)
                    if patch.get("changed"):
                        ai_patches[vid] = patch
                        print(f"      [ai-update] {intel.brand}：{patch['summary']}")
                    else:
                        print(f"      [ai-ok] {intel.brand}：页面变化不构成事实更新")
                if ai_aborted:
                    print("      本次 AI 核查提前终止：README / 博客照常生成，事实档案未被改写。")
                if ai_patches:
                    overlay_path = root / "profile_overrides.json"
                    # 变更日志的「前值」必须在**应用前**取生效档案（含既有覆写）
                    changelog_entries = []
                    for vid, p in ai_patches.items():
                        intel = intel_by_id[vid]
                        base = get_provider_profile(vid, intel.brand, intel.homepage)
                        changelog_entries.append({
                            "vendor_id": vid, "brand": intel.brand,
                            "summary": p.get("summary") or "官方页面事实变化",
                            "diffs": [(f, _changelog_fmt(base.get(f)),
                                       _changelog_fmt(v))
                                      for f, v in (p.get("fields") or {}).items()],
                        })
                    ai_review.apply_patches(overlay_path, ai_patches)
                    reload_overrides()
                    report = [f"{vid}: {p['summary']}" for vid, p in ai_patches.items()]
                    (root / ".ai-changed").write_text("\n".join(report) + "\n",
                                                      encoding="utf-8", newline="\n")
                    n_cl = append_intel_changelog(
                        root / CHANGELOG_MD, datetime.now().strftime("%Y-%m-%d"),
                        changelog_entries)
                    print(f"      已写入 profile_overrides.json（{len(ai_patches)} 个厂商），"
                          f"变更日志追加 {n_cl} 条（{CHANGELOG_MD}），README 将按新档案重渲染。")
        # 无变化厂商的 stage 也一并落盘（哈希相同，不产生内容差异）
        for intel in intel_list:
            snapshots.commit_vendor(intel.vendor_id)
    if not args.rebuild_only:
        state_changed = snapshots.save({v.vendor_id for v in intel_list},
                                       full_run=not args.only)
        if state_changed:
            print(f"      快照状态已更新：{SNAPSHOT_STATE}")

    # 自建 RSS 的对外前缀：README 与博客总表都要引用订阅地址，必须在渲染之前解析
    # （CI 里由 GITHUB_REPOSITORY 推导 Pages 地址）。feeds_dir 已在 [2/4] 前算好。
    feeds_base = args.feeds_base.strip() or default_feeds_base()
    if args.rebuild_only:
        print("      [info] --rebuild-only：跳过 README 渲染与快照落盘（情报区需要实抓页面）。")
    else:
        print("      开始渲染 README ...")
        records = order_vendor_records(intel_list)
        guide_section = render_guide_block(records)
        section = render_intel_section(intel_list, elapsed, records, feeds_base)
        readme_path = (root / args.readme) if not Path(args.readme).is_absolute() else Path(args.readme)
        if args.only and readme_path.resolve() == (root / "README.md").resolve():
            print("      [info] 当前为 --only 局部调试运行：跳过全局 README.md 覆盖重写（防止清除其他厂商档案）。"
                  "提交前请运行完整巡检以全量生成文档。")
        else:
            readme_changed = update_readme(readme_path, section, guide_section)
            print(f"      {'已刷新' if readme_changed else '无内容变化，未改写'} {readme_path.name}")

    print(f"[4/4] 整理博客 / 动态订阅源 ...")
    opml_path = (root / args.news_opml) if not Path(args.news_opml).is_absolute() else Path(args.news_opml)
    title_polish = None
    if args.ai_titles:
        import ai_review
        try:
            polish_backend = ai_review.resolve_backend()
            polish_err = ai_review.backend_config_error(polish_backend)
        except ai_review.AiReviewError as exc:
            polish_backend, polish_err = "", str(exc)
        if polish_err:
            print(f"      [ai-titles] 已禁用：{polish_err}", file=sys.stderr)
        else:
            title_polish = make_llm_title_polisher()
            print(f"      [ai-titles] 新收录标题将经 {polish_backend} 润色一次（结果进归档即冻结）")
    if args.no_news:
        print("      已跳过（--no-news）")
    elif args.only and news_md_path.resolve() == (root / "llm-news-feeds.md").resolve():
        news_dir = news_md_path.parent / "llm-news"
        n_arch, n_arch_arts, n_arch_changed = write_news_archives(
            news_dir, intel_list, clean_removed=False, title_polish=title_polish)
        print("      [info] 当前为 --only 局部调试运行：跳过全局 llm-news-feeds.md、opml 与自建 RSS "
              "覆盖重写；"
              f"llm-news/ 已更新 {n_arch} 个对应厂商归档文件（共 {n_arch_arts} 篇文章，改写 {n_arch_changed} 个）。")
    else:
        # write_news_archives 会把「新抓取 + 历史归档」的合并结果写回 intel.all_news_articles
        # 与 intel.news_articles，而总表的「共 N 篇」和「最新 5 篇」都取自这两个字段 ——
        # 因此它必须排在 update_news_md 之前：否则总表用的是合并前计数，会比归档文件少
        # （归档保留了页面已不再链接的历史文章，实测差 1~4 篇）。
        news_dir = news_md_path.parent / "llm-news"
        n_arch, n_arch_arts, n_arch_changed = write_news_archives(
            news_dir, intel_list, clean_removed=True, title_polish=title_polish)
        news_changed = update_news_md(
            news_md_path,
            render_news_section(intel_list, feeds_base, merged_limit=args.rss_limit))
        n_feeds = write_opml(opml_path, intel_list, feeds_base,
                             merged_limit=args.rss_limit)
        print(f"      {news_md_path.name} {'已刷新' if news_changed else '无内容变化，未改写'}；"
              f"{opml_path.name}（{n_feeds} 个订阅源"
              f"{'：官方原生 + 自建源 + 聚合流' if feeds_base else '（仅官方原生源，未推导出 Pages 前缀）'}）")
        print(f"      llm-news/ 归档 {n_arch} 个厂商文件、共 {n_arch_arts} 篇文章"
              f"（本次实际改写 {n_arch_changed} 个文件）")
        # 同样必须在 write_news_archives 之后：RSS 要用的正是这份全量、已排序的列表。
        n_rss, n_rss_items, n_rss_changed, n_rss_skipped = write_rss_feeds(
            feeds_dir, intel_list, feeds_base, merged_limit=args.rss_limit)
        print(f"      {args.feeds_dir} 自建 RSS {n_rss} 个源、{n_rss_items} 条"
              f"（本次实际改写 {n_rss_changed} 个文件）")
        if n_rss_skipped:
            print(f"      [warn] {n_rss_skipped} 条因发布日期缺失或晚于今天未进订阅流"
                  "（归档 .md 中仍保留）——多为源页面日期提取有误，建议核查。")
        # 模型发布雷达：同一份「归档合并后」全量列表的免费衍生（确定性、无时间戳）
        releases = extract_model_releases(intel_list)
        wrote_rel = write_model_releases(feeds_dir / "model-releases.json", releases)
        print(f"      模型发布雷达 {len(releases)} 个事件"
              f"（{('已刷新 ' + 'model-releases.json') if wrote_rel else '无内容变化，未改写'}）")

    # 控制台汇总
    total = sum(len(v.intel_pages) for v in intel_list)
    ok = sum(1 for v in intel_list for p in v.intel_pages if p.ok)
    fail = total - ok
    news_total = sum(len(v.news_pages) for v in intel_list)
    print("-" * 60)
    print(f"完成：厂商 {len(intel_list)} 个；情报页 {total}（成功 {ok} / 失败 {fail}）；"
          f"动态页 {news_total}。")
    if fail:
        print("失败页面已在 README 中标注「解析失败」，可重跑或人工核查。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
