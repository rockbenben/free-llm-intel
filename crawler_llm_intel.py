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
       不写入 README，改为单独输出到 llm-news-feeds.md，并尝试发现页面中的
       RSS / Atom 订阅源，汇总生成 llm-news-feeds.opml（可导入 RSS 阅读器）。
     - product 等产品页：仅用于确认产品线，默认不深度抓取。
  3. 巡检结果写入 README.md 的固定章节（标记注释之间，重跑自动重写，不累计）。

运行：
    python crawler_llm_intel.py                 # 完整巡检并刷新 README + 动态订阅文件
    python crawler_llm_intel.py --only deepseek # 只巡检指定 vendor_id（调试用，不覆盖全局文档）
    python crawler_llm_intel.py --no-news       # 跳过博客/RSS 发现，只刷新 README
    python crawler_llm_intel.py --no-browser    # 禁用浏览器兜底，纯 requests 抓取
    python crawler_llm_intel.py --ai-review     # 变化时调用 AI 自动核查并更新 profile_overrides.json

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

# SPA 单页外壳标记：静态 HTML 只有 JS 挂载点、正文靠客户端渲染
SPA_ROOT_MARKER = re.compile(
    r"""id\s*=\s*["'](?:root|__next|__nuxt|app|app-root|appRoot|react-root)["']""",
    re.I,
)

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
RSS_MERGED_LIMIT = 200  # 合并流最多收录条数（单厂商源不设上限，等于该厂商全量归档）

BLOCK_TAGS = {
    "p", "div", "li", "tr", "td", "th", "h1", "h2", "h3", "h4", "h5", "h6",
    "br", "section", "article", "ul", "ol", "table", "header", "footer",
    "blockquote", "pre", "figure", "figcaption", "dt", "dd", "hr",
}
SKIP_TAGS = {"script", "style", "noscript", "svg", "iframe", "template"}


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

    def __post_init__(self) -> None:
        # 统一在这里洗控制字符：RSS 原始 XML 与页面提取都可能带 \x00，
        # 有 6 处 Article(...) 构造点，收口在数据类比逐处修补更可靠
        self.title = sanitize_text(self.title)
        self.url = sanitize_text(self.url)
        self.date = sanitize_text(self.date)
        self.source = sanitize_text(self.source)
        self.stype = sanitize_text(self.stype)


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

    def handle_endtag(self, tag: str):
        tag = tag.lower()
        if tag in SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
            return
        if tag == "title":
            self._in_title = False
        if tag == "a" and self._a_href is not None:
            text = re.sub(r"\s+", " ", "".join(self._a_text)).strip()
            self.links.append((self._a_href, text))
            self._a_href = None
            self._a_text = []
        if tag in BLOCK_TAGS:
            self._chunks.append("\n")

    def handle_data(self, data: str):
        if self._skip_depth:
            return
        if self._in_title:
            self._title_parts.append(data)
        if self._a_href is not None:
            self._a_text.append(data)
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
               ) -> tuple[str, str, list[str], list[tuple[str, str]]]:
    """返回 (纯文本, 页面标题, RSS/Atom 链接列表, [(链接URL, 锚文本)])。"""
    parser = PageParser(base_url)
    try:
        parser.feed(raw_html)
        parser.close()
    except Exception as exc:  # 解析器容错：残缺 HTML 不应导致整体失败
        print(f"  [warn] HTML 解析异常 {base_url}: {type(exc).__name__}: {exc}",
              file=sys.stderr)
    return parser.get_text(), parser.get_title(), parser.feeds, parser.links


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
            text, title, feeds, links = parse_html(resp.text, resp.url)
            result.text = text
            result.snapshot_text = text  # 浏览器兜底不得覆盖此字段（见 PageResult）
            result.title = title
            result.feeds = feeds
            result.links = links
            result.ok = True
            # 可见文本过少：通常是 SPA 动态渲染或需要登录（阈值放宽到 800，
            # 500~800 字多为导航外壳，正文仍靠浏览器兜底渲染）
            text_len = len(re.sub(r"\s", "", text))
            spa_shell = (text_len < 3000
                         and SPA_ROOT_MARKER.search(resp.text or ""))
            # 文本不算极少但页面是 React/Vue 单页外壳（如 build.nvidia.com
            # 静态 HTML 只有 id="app" 挂载点）：正文全靠 JS 渲染，同样走浏览器
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
    text, title, feeds, links = parse_html(html, final_url or url)
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
_INLINE_DATE_RE = re.compile(
    r"(20\d{2}[-/年.]\s?\d{1,2}[-/月.]\s?\d{1,2}日?|"
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
    m = re.search(r"(20\d{2})[-/年.](\d{1,2})[-/月.](\d{1,2})", raw)
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
        for child in item:
            tag = child.tag.rsplit("}", 1)[-1].lower()
            if tag == "title" and not title and (child.text or "").strip():
                title = re.sub(r"\s+", " ", html_mod.unescape(child.text)).strip()
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
        if not title or not link.startswith("http") or link in seen:
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
            dm = re.search(r"(\d{4})[-/年.]\s?(\d{1,2})(?:[-/月.]\s?(\d{1,2}))?", hid)
            norm_date = _drop_future_date(
                f"{dm.group(1)}-{int(dm.group(2)):02d}-{int(dm.group(3) or 1):02d}" if dm else "")
            lines = _clean_html_text(content)
            title = lines[0] if lines else hid
            if re.fullmatch(r"\d{4}[-/年.]\d{1,2}(?:[-/月.]\d{1,2})?", title):
                title = lines[1] if len(lines) > 1 else title
            url = f"{base_url.split('#')[0]}#{quote(hid)}"
            if url not in seen and len(title) >= 3:
                seen.add(url)
                articles.append(Article(title=_cap_changelog_title(title), url=url, date=norm_date, source="官方更新日志", stype=page.stype))
        if articles:
            return articles[:max_items]

    # 结构 2：标题日期锚点式变更日志（<h2/h3 id="2026...">）。
    # id 允许日期前有短前缀（如 DeepSeek 中文页 h2 id="时间-2026-09-10"），
    # 故不要求 id 以年份开头；年-月、月-日间的非数字分隔限 3 字符以内，
    # 避免把 model-2025-rc1 之类的版本号误解析成日期。
    date_id_pat = r"[^\"']*20[2-3]\d[^\"']*"
    matches_h = list(re.finditer(
        r"<(h[23])[^>]*id=[\"'](" + date_id_pat + r")[\"'][^>]*>.*?</\1>"
        r"(.*?)(?=<(?:h[23])[^>]*id=[\"']" + date_id_pat + r"|$)",
        raw, re.S
    ))
    for m in matches_h:
        hid = m.group(2)
        body = m.group(3)
        dm = re.search(r"(20[2-3]\d)\D{1,3}(\d{1,2})(?:\D{0,3}(\d{1,2}))?", hid)
        norm_date = _drop_future_date(
            f"{dm.group(1)}-{int(dm.group(2)):02d}-{int(dm.group(3) or 1):02d}" if dm else "")

        # 检查卡片标题（MiniMax 等卡片式组件）
        card_m = re.search(r"data-component-part=[\"']card-title[\"'][^>]*>(.*?)</h[23]>", body, re.S)
        if card_m:
            model_name = re.sub(r"<[^>]+>", "", card_m.group(1)).strip(" \u200b\t\n")
            p_m = re.search(r"data-component-part=[\"']card-content[\"'][^>]*>(.*?)</div", body, re.S)
            desc = re.sub(r"<[^>]+>", "", p_m.group(1)).strip(" \u200b\t\n") if p_m else ""
            title = f"{model_name}：{desc}" if desc else model_name
        else:
            lines = _clean_html_text(body)
            title = lines[0] if lines else hid
            if re.search(r"^\d{4}\s*[-年]", title):
                title = lines[1] if len(lines) > 1 else title

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
            desc_raw = re.sub(r"<[^>]+>", "", cells[-1])
            desc = re.sub(r"[​\s]+", " ", desc_raw).strip()
            desc = re.sub(r"[，,]\s*了解详情$", "", desc)
            if not model_id or not desc:
                continue
            norm_date = _drop_future_date(
                f"{int(date_m.group(2)):04d}-"
                f"{int(date_m.group(3)):02d}-{int(date_m.group(4)):02d}")
            title = f"{model_id}：{desc}"
            url = f"{base_no_frag}#{quote(model_id)}"
            if url in row_seen:  # 同一模型在多地域表格中重复出现
                continue
            row_seen.add(url)
            table_rows.append(Article(
                title=_cap_changelog_title(title), url=url, date=norm_date,
                source="官方更新日志", stype=page.stype))
        if len(table_rows) >= 3:
            articles = table_rows

    return articles[:max_items]


def extract_articles_from_page(page: PageResult, max_items: int = 8) -> list[Article]:
    """
    从已抓取的博客 / 更新页 HTML 链接中启发式提取文章条目（无 RSS 时的兜底）：
    1) 先尝试从单页文档站的更新日志结构（Mintlify / Docusaurus 容器与日期标题块）中提取；
    2) 提取不到时，从 HTML 链接中启发式提取独立文章页面。
    """
    if not page.ok:
        return []
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
    for url, anchor in page.links:
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
        title = html_mod.unescape(re.sub(r"\s+", " ", anchor or "")).strip()
        date = ""
        # DeepSeek 更新日志：URL slug 即日期（/news/news260813 -> 2026-08-13）
        slug_m = re.search(r"/news/news(\d{2})(\d{2})(\d{2})", path, re.I)
        if slug_m:
            date = f"20{slug_m.group(1)}-{slug_m.group(2)}-{slug_m.group(3)}"
        dm = _INLINE_DATE_RE.search(title)
        if dm:
            date = date or normalize_feed_date(dm.group(1))
            title = (title[:dm.start()] + " " + title[dm.end():]).strip(" -–|·•\t")
        date = _drop_future_date(date)
        # 剥掉粘连的栏目名 / 作者名（"PartnershipGroq Among..." -> "Groq Among..."）
        title = _strip_glued_label(title)
        title = re.sub(r"\s+", " ", title).strip(" -–|·•")
        if len(title) < 10 or len(title) > 200:
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
            if not art.url:
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
    intel.all_news_articles = ordered       # 全量归档（llm-news/ 子文档）
    intel.news_articles = ordered[:5]       # 主文档仅展示最新 5 篇


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
            # api_docs / docs / console / hf_org 等入口：本轮不深度抓取
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
_PROMO_DATE_PAT = re.compile(r"(20\d{2})\s*[-/年.]\s*(\d{1,2})\s*[-/月.]\s*(\d{1,2})")


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
             "本仓库不转抄未经本轮官方页核实的价格数字——请从上方对应厂商表格的「官方直达」进入定价页查看现行档位。"
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
                 f"已借助 Google 公开翻译引擎将海外一手情报全面汉化；"
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
                     f"（最近 {merged_limit} 条，带厂商前缀，可按 `category` 过滤）")
        lines.append(f"> - 单厂商源：`{feeds_base}/llm-news-{{vendor_id}}.xml`"
                     "（把 `{vendor_id}` 换成下方括号里的厂商 id，如 `llm-news-openai.xml`）")
        lines.append("> - ⚠️ 合并流与各厂商单源**内容重叠**，二选一订阅即可（都订会出现重复条目）；"
                     "合并流只收有日期的条目且有上限，**要订阅全部有动态源的厂商请用单源或浏览页页脚**。")
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
                title_zh = translate_to_zh(art.title)
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
            "全部厂商 - 合并流（最近 %d 条，带厂商前缀）" % merged_limit,
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


def write_news_archives(out_dir: Path, intel_list: list[VendorIntel],
                       clean_removed: bool = True) -> tuple[int, int, int]:
    """把每个厂商的全量文章写到 llm-news/<vendor_id>.md 子文档。

    返回 (归档文件数, 文章总数, 实际改写文件数)。自动将新抓取的文章与既有归档增量
    合并，保障旧文章永不丢失；标题汉化走 translate_to_zh（磁盘缓存 + 并发）。
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
        by_url = {_norm_url(a.url): a for a in merged_arts}
        for old_art in existing:
            u_norm = _norm_url(old_art.url)
            fresh = by_url.get(u_norm)
            if fresh is None:
                by_url[u_norm] = old_art
                merged_arts.append(old_art)
            elif not fresh.date and old_art.date:
                # 本次抓取没拿到日期（页面卡片改版、标题被截断等），沿用归档里已有的：
                # 日期一旦丢失就永久丢失（归档排序、RSS pubDate、README 展示都依赖它），
                # 而且重抓也补不回来 —— 实测 cohere 博客页改版后 9 条会退化成无日期。
                fresh.date = old_art.date
        dated = sorted((a for a in merged_arts if a.date),
                       key=lambda a: a.date, reverse=True)
        undated = [a for a in merged_arts if not a.date]
        arts = dated + undated
        intel.all_news_articles = arts
        intel.news_articles = arts[:5]
        if not arts:
            continue
        with ThreadPoolExecutor(max_workers=6) as pool:
            titles_zh = list(pool.map(translate_to_zh, (a.title for a in arts)))
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
            titles_zh = list(pool.map(translate_to_zh, (a.title for a in arts)))
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
        key = _norm_url(row[2].url)
        if key in seen:
            continue
        seen.add(key)
        picked.append(row)
        if len(picked) >= merged_limit:
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
    changed += _write_json(out_dir / "vendors.json", {
        "vendors": [
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
        ]
    })
    return files, items, changed, skipped


# ---------------------------------------------------------------------------
# 页面快照变化检测（仅快照、不理解语义；语义判断由 ai_review 的 LLM 完成）
# ---------------------------------------------------------------------------

SNAPSHOT_STATE = "llm-intel-state.json"
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
            self.entries: dict[str, dict] = (
                json.loads(self.path.read_text(encoding="utf-8"))
                .get("sources", {})) if self.path.exists() else {}
        except (ValueError, OSError):
            self.entries = {}
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

    def save(self, crawled_ids: set[str], full_run: bool) -> bool:
        # AI 未处理 / 失败的厂商保持旧哈希（未 stage 即自然保留）
        for staged in self._staged.values():
            self.entries.update(staged)
        self._staged.clear()
        if full_run:
            prefixes = tuple(f"{vid}|" for vid in crawled_ids)
            self.entries = {k: v for k, v in self.entries.items()
                            if k.startswith(prefixes)}
        payload = json.dumps({"sources": self.entries},
                             ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        old = self.path.read_text(encoding="utf-8") if self.path.exists() else ""
        if payload == old:
            return False
        self.path.write_text(payload, encoding="utf-8", newline="\n")
        return True


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

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
                        help=f"合并流最多收录条数（默认 {RSS_MERGED_LIMIT}；单厂商源不设上限）")
    parser.add_argument("--delay", type=float, default=0.3, help="每次请求间隔秒数（默认 0.3）")
    parser.add_argument("--timeout", type=float, default=20.0, help="读取超时秒数（默认 20）")
    parser.add_argument("--only", action="append", default=[],
                        help="只巡检指定 vendor_id（可多次使用，调试用；不覆盖全局 README 与新闻总表）")
    parser.add_argument("--no-news", action="store_true", help="跳过博客 / RSS 发现")
    parser.add_argument("--no-browser", action="store_true",
                        help="禁用 Playwright 浏览器兜底（默认启用，需 pip install playwright）")
    parser.add_argument("--ai-review", action="store_true",
                        help="检测到官方页面变化时调用 LLM 核查并更新 profile_overrides.json"
                             "（后端 AI_REVIEW_BACKEND=auto|gemini|anthropic，默认 auto："
                             "有 GEMINI_API_KEY 走 Google AI Studio，否则 ANTHROPIC_API_KEY；"
                             "可用 AI_REVIEW_MODEL 覆盖模型）")
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parent
    (root / ".ai-changed").unlink(missing_ok=True)
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

    session = build_session()
    timeout = (8.0, args.timeout)
    use_browser = not args.no_browser
    if use_browser and not HAS_PLAYWRIGHT:
        print("[info] 未安装 playwright，禁用浏览器兜底（JS/403 页面将仅标注）。"
              "安装后可自动用真实浏览器渲染：pip install playwright")
    intel_list: list[VendorIntel] = []
    snapshots = SnapshotState(root)
    if snapshots.baseline:
        print("[info] 快照状态文件不存在：本次为基线建档，只记录页面哈希，不触发 AI 核查。")
    started = time.time()

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
    ai_patches: dict[str, dict] = {}
    if changed_map:
        print(f"      {len(changed_map)} 个厂商的官方页面发生变化。")
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
                    if patch.get("changed"):
                        ai_patches[vid] = patch
                        print(f"      [ai-update] {intel.brand}：{patch['summary']}")
                    else:
                        print(f"      [ai-ok] {intel.brand}：页面变化不构成事实更新")
                if ai_aborted:
                    print("      本次 AI 核查提前终止：README / 博客照常生成，事实档案未被改写。")
                if ai_patches:
                    overlay_path = root / "profile_overrides.json"
                    ai_review.apply_patches(overlay_path, ai_patches)
                    reload_overrides()
                    report = [f"{vid}: {p['summary']}" for vid, p in ai_patches.items()]
                    (root / ".ai-changed").write_text("\n".join(report) + "\n",
                                                      encoding="utf-8", newline="\n")
                    print(f"      已写入 profile_overrides.json（{len(ai_patches)} 个厂商），"
                          "README 将按新档案重渲染。")
        # 无变化厂商的 stage 也一并落盘（哈希相同，不产生内容差异）
        for intel in intel_list:
            snapshots.commit_vendor(intel.vendor_id)
    state_changed = snapshots.save({v.vendor_id for v in intel_list},
                                   full_run=not args.only)
    if state_changed:
        print(f"      快照状态已更新：{SNAPSHOT_STATE}")

    print("      开始渲染 README ...")
    # 自建 RSS 的对外前缀与输出目录：README 与博客总表都要引用订阅地址，
    # 因此必须在渲染之前解析（CI 里由 GITHUB_REPOSITORY 推导 Pages 地址）。
    feeds_base = args.feeds_base.strip() or default_feeds_base()
    feeds_dir = (root / args.feeds_dir) if not Path(args.feeds_dir).is_absolute() else Path(args.feeds_dir)
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
    news_md_path = (root / args.news_md) if not Path(args.news_md).is_absolute() else Path(args.news_md)
    opml_path = (root / args.news_opml) if not Path(args.news_opml).is_absolute() else Path(args.news_opml)
    if args.no_news:
        print("      已跳过（--no-news）")
    elif args.only and news_md_path.resolve() == (root / "llm-news-feeds.md").resolve():
        news_dir = news_md_path.parent / "llm-news"
        n_arch, n_arch_arts, n_arch_changed = write_news_archives(
            news_dir, intel_list, clean_removed=False)
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
            news_dir, intel_list, clean_removed=True)
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
