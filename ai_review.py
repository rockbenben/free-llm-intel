# -*- coding: utf-8 -*-
"""
ai_review.py —— 变化触发式 AI 档案核查。

每日巡检发现某厂商的官方页面文本相对上次快照发生变化时，由 crawler 调用本模块：
把该厂商全部情报页正文 + 当前生效档案发给 LLM，要求只依据页面原文输出严格 JSON：
哪些事实字段变化、攻略元数据是否要调整、以及逐条「页面原文证据」。证据必须能在
页面正文中逐字定位（防幻觉闸门），校验通过后才允许写入 profile_overrides.json。

调用后端（AI_REVIEW_BACKEND=auto|gemini|anthropic，默认 auto）：
- gemini（默认）：Google AI Studio 的 Gemini API（generativelanguage.googleapis.com），
  用免费层 API Key（环境变量 GEMINI_API_KEY，兼容 GOOGLE_API_KEY），默认模型
  gemini-3.8-flash，可用 AI_REVIEW_MODEL 覆盖；
- anthropic（可选）：直连 Anthropic Messages API（ANTHROPIC_API_KEY）。

auto 规则：哪个 key 存在用哪个；都没有时按 gemini 报缺 key。

免费层回退（主要使用场景即 AI Studio 免费层，具体限额只在 AI Studio 控制台公布、
RPD 太平洋时间午夜重置）：
- 429 判定为当日额度（RPD，按项目共享）耗尽 → AiQuotaExhausted：不再调用任何厂商，
  全部保留旧快照等下次巡检；429 短期限流（RPM/TPM，按模型独立计量）→ 先尊重
  Retry-After 指数退避，退避仍不缓解则换下一个备选模型（其额度桶可能仍有余量），
  直到全部备选都限流才按额度耗尽整批终止；
- 首选模型 404 / 不可用 → 自动回退免费层备选链（均为
  https://ai.google.dev/pricing 标注免费 "Free of charge" 的模型，2026-09 核实）：
  gemini-3.8-flash → 3.7 → 3.6 → 3.5 → 2.5 → 3.5-flash-lite → 3.1-flash-lite
  → 2.5-flash-lite。完整 Flash 系按新到旧排列（能力优先），Lite 系垫底
  （更弱但免费层限额更宽松，最可能还余有额度）；不纳入 preview 模型
  （官方仅保证约两周弃用通知，不适合长期兜底）；AI_REVIEW_MODEL 可钉死首选；
- 单厂商核查受 MAX_REVIEW_WALL_SECONDS 墙钟预算约束：多备选 + 超时重试叠加时
  不会拖垮整轮巡检（CI 60 分钟作业），超预算即放弃该厂商、保留旧快照；
- Key 无效等 400/401/403 立即失败不浪费配额；crawler 对连续失败还有熔断（3 次）。

后端不可用 / 无网络时调用方应跳过核查并保留旧快照，下次巡检自动重试。
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

import requests

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
GEMINI_DEFAULT_MODEL = "gemini-3.8-flash"   # AI Studio 免费层可用，可用 AI_REVIEW_MODEL 覆盖
# 首选模型不可用 / 限流时的免费层备选链。每个模型都在
# https://ai.google.dev/pricing 免费层标注 "Free of charge"（2026-09-15 核实）。
# 排列原则：完整 Flash 系按新到旧（能力优先，兜底时才让位），Lite 系垫底
# （能力更弱但免费层限额更宽松，最可能还余有额度）；不纳入 preview 模型。
GEMINI_FALLBACK_MODELS = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
]
MAX_RATE_RETRIES = 4            # 429 短期限流（RPM/TPM）：5/10/20/40s 指数退避
RATE_RETRY_BASE_SECONDS = 5
MAX_TRANSIENT_RETRIES = 2       # 500/503/504 同模型重试次数
RETRY_WAIT_CAP_SECONDS = 90
TRANSIENT_STATUSES = {500, 503, 504}
# 单厂商核查的墙钟预算：备选链变长后，超时重试（单次请求 timeout=180s）与
# 限流退避叠加可能耗掉整轮巡检时间，超预算即放弃该厂商并保留旧快照。
MAX_REVIEW_WALL_SECONDS = 900
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_DEFAULT_MODEL = "claude-sonnet-5"
MAX_TOKENS = 4096
PAGE_CHAR_BUDGET = 18_000      # 单个来源页送给模型的最大字符数
TOTAL_CHAR_BUDGET = 60_000     # 单厂商总预算

BACKEND_GEMINI = "gemini"
BACKEND_ANTHROPIC = "anthropic"


def _gemini_key() -> str:
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""


def _anthropic_key() -> str:
    return os.environ.get("ANTHROPIC_API_KEY", "")


def backend_api_key(backend: str) -> str:
    if backend == BACKEND_GEMINI:
        return _gemini_key()
    if backend == BACKEND_ANTHROPIC:
        return _anthropic_key()
    return ""


def backend_config_error(backend: str) -> str:
    """返回该后端当前不可用的中文原因；可用时返回空串。"""
    if backend == BACKEND_GEMINI and not _gemini_key():
        return ("未设置 GEMINI_API_KEY（Google AI Studio 免费层 Key，"
                "申请：https://aistudio.google.com/apikey）：跳过 AI 核查，"
                "变化厂商保留旧快照，下次巡检重试。")
    if backend == BACKEND_ANTHROPIC and not _anthropic_key():
        return ("未设置 ANTHROPIC_API_KEY：跳过 AI 核查，变化厂商保留旧快照，"
                "下次巡检将继续标记为变化。")
    return ""


def resolve_backend(backend: str | None = None) -> str:
    """决定 LLM 后端：显式参数 > AI_REVIEW_BACKEND 环境变量 > auto（有哪个 key 用哪个）。"""
    name = (backend or os.environ.get("AI_REVIEW_BACKEND") or "auto").strip().lower()
    if name == "auto":
        if _gemini_key():
            return BACKEND_GEMINI
        if _anthropic_key():
            return BACKEND_ANTHROPIC
        return BACKEND_GEMINI  # 无 key 时仍按默认后端报缺 key（错误提示含申请地址）
    if name in (BACKEND_GEMINI, BACKEND_ANTHROPIC):
        return name
    raise AiReviewError(f"未知 AI_REVIEW_BACKEND：{name}（可选 auto/gemini/anthropic）")


def default_model(backend: str) -> str:
    return GEMINI_DEFAULT_MODEL if backend == BACKEND_GEMINI else ANTHROPIC_DEFAULT_MODEL


FIELD_TYPES = {
    "category": str,
    "display_name": str,
    "free_quota": str,
    "validity": str,
    "free_models": list,
    "tier_caveats": list,
    "preconditions": str,
    "promotions": str,
    "notes": str,
}
ALLOWED_TIERS = {"permanent", "onetime", "recurring", "selfhost"}
ALLOWED_SIGNUP = {"email", "card"}
ALLOWED_SCENARIOS = {"code", "flagship", "longctx", "image", "embed", "deploy", "credit",
                     "referral", "student"}

SYSTEM_PROMPT = """你是「免费 LLM API 情报」核查员，服务于一个只采信官方页面的开源项目。\
你的任务：对比「当前档案」与「官方页面原文」，判断免费模型、额度、限速、注册门槛、限时活动等\
事实是否发生变化，并输出严格 JSON。

铁律：
1. 只能依据本次给出的官方页面文本，禁止使用你的记忆或外部知识；页面没写的内容一律视为未知。
2. 只有当页面原文能证明事实相对当前档案发生变化时才输出 changed=true；措辞重排、营销内容、\
新闻文章、导航噪音不构成事实变化 → changed=false。
3. changed=true 时：fields 只放发生变化的字段，且列表/多句字段（如 free_models）必须给出\
该字段的完整新内容（不是只给差异行）；每条 free_models 字符串格式为「模型名 —— 内联额度/限速」，\
可使用 Markdown 加粗与反引号，中文撰写。
4. evidence 给出 1-6 条页面原文逐字摘录（不要翻译、不要改写、不要省略号拼接），\
每条必须能在给定页面文本中连续找到；所有数字、模型名必须与原文一致。
5. 攻略归类 guide_meta 仅在归类确实需要变化时给出：tiers 取值 permanent/onetime/recurring/\
selfhost，signup 取值 email/card，scenarios 取值 code/flagship/longctx/image/embed/deploy/credit，\
short 是一句话额度摘要，tip 是一句话防扣费提示。
6. 输出只能是一个 JSON 对象，不要输出解释、Markdown 代码块或多余文字。"""


class AiReviewError(RuntimeError):
    """AI 核查失败（网络、格式或证据校验不过）；调用方应保留旧快照以便下次重试。"""


class AiReviewAbort(AiReviewError):
    """整批终止信号：调用方应立即停止调用其余厂商、整体保留旧快照（不计入单厂商失败次数）。"""


class AiQuotaExhausted(AiReviewAbort):
    """免费层当日额度耗尽（RPD）或持续限流。"""


class AiServiceOutage(AiReviewAbort):
    """多个模型连续 5xx：Google 侧整体故障，换厂商标重试无意义。"""


# 429 错误体中识别「当日额度」（太平洋时间午夜重置，重试无意义）
_DAILY_QUOTA_RE = re.compile(
    r"per[_\s-]*day|\bRPD\b|RequestsPer\w*PerDay|每天|每日|日配额|日额度", re.I)
# 400/404 错误体中识别「模型在当前项目不可用 / 已下线」→ 回退备选模型
_MODEL_MISSING_RE = re.compile(
    r"not found|not supported|no version|deprecated|not a valid model|no.*found for model",
    re.I)


def gemini_candidate_models(preferred: str = "") -> list[str]:
    """首选模型 + 免费层备选链（去重保序）。"""
    out: list[str] = []
    for cand in [preferred or GEMINI_DEFAULT_MODEL, GEMINI_DEFAULT_MODEL,
                 *GEMINI_FALLBACK_MODELS]:
        if cand and cand not in out:
            out.append(cand)
    return out


def _retry_after_seconds(resp, default: float) -> float:
    """尊重 Retry-After（秒数形式），其余回退到给定退避值，统一封顶。"""
    raw = resp.headers.get("retry-after") if getattr(resp, "headers", None) else None
    if raw and raw.strip().isdigit():
        return min(int(raw.strip()), RETRY_WAIT_CAP_SECONDS)
    return min(default, RETRY_WAIT_CAP_SECONDS)


def _gemini_error(resp) -> tuple[dict, str]:
    try:
        err = resp.json().get("error", {}) or {}
    except ValueError:
        return {}, resp.text[:300]
    return err, str(err.get("message") or resp.text[:300])


def _is_daily_quota(err: dict, msg: str) -> bool:
    details = json.dumps(err.get("details", []), ensure_ascii=False)
    return bool(_DAILY_QUOTA_RE.search(f"{details} {msg}"))


def _norm(s: str) -> str:
    return re.sub(r"\s+", "", s or "").lower()


def build_user_prompt(
        vendor_id: str, brand: str, profile: dict, guide_meta: dict,
        pages: list[dict], char_budget: int = TOTAL_CHAR_BUDGET) -> str:
    """pages: [{"url","stype","title","text"}]，按 char_budget 截断。"""
    profile_view = {k: profile.get(k) for k in FIELD_TYPES if k in profile}
    parts = [
        f"厂商：{brand}（id: {vendor_id}）",
        "",
        "【当前生效档案】",
        json.dumps(profile_view, ensure_ascii=False, indent=2),
        "",
        "【当前攻略元数据】",
        json.dumps(guide_meta or {}, ensure_ascii=False),
        "",
        "【官方页面原文】",
    ]
    total = 0
    page_budget = min(PAGE_CHAR_BUDGET, char_budget)
    for page in pages:
        header = f"\n===== 来源类型 {page['stype']}｜{page['url']}｜{page.get('title','')} ====="
        body = page["text"][:page_budget]
        if total + len(header) + len(body) > char_budget:
            body = body[:max(0, char_budget - total - len(header))]
        parts.append(header)
        parts.append(body)
        total += len(header) + len(body)
        if total >= char_budget:
            break
    parts.append("")
    parts.append("【输出格式】")
    parts.append(json.dumps({
        "changed": True,
        "summary": "一句话说明变化（中文）",
        "fields": {"free_quota": "…", "free_models": ["模型 —— 额度"]},
        "guide_meta": {"tiers": ["permanent"], "signup": "email",
                       "scenarios": ["code"], "short": "…", "tip": "…"},
        "evidence": [{"url": "https://…", "quote": "页面原文逐字片段"}],
    }, ensure_ascii=False, indent=2))
    parts.append("无事实变化时输出：" + json.dumps({"changed": False}, ensure_ascii=False))
    return "\n".join(parts)


def call_llm(prompt: str, api_key: str = "", model: str = "",
             timeout: float = 180.0, backend: str | None = None) -> str:
    """按后端分发。prompt 为用户消息（系统提示由各 API 的 system 字段承载）。"""
    backend = resolve_backend(backend)
    if not model:
        model = default_model(backend)
    if not api_key:
        api_key = backend_api_key(backend)
    if backend == BACKEND_GEMINI:
        return call_llm_gemini(prompt, api_key=api_key, model=model, timeout=timeout)
    return call_llm_anthropic(prompt, api_key=api_key, model=model, timeout=timeout)


def _parse_gemini_response(resp) -> str:
    try:
        data = resp.json()
        candidates = data.get("candidates") or []
        parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
        text = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
        if not text.strip():
            block = (data.get("promptFeedback") or {}).get("blockReason")
            finish = candidates[0].get("finishReason") if candidates else None
            raise AiReviewError(
                f"Gemini 返回空内容（finishReason={finish}, blockReason={block}）")
        return text
    except AiReviewError:
        raise
    except (KeyError, IndexError, ValueError) as exc:
        raise AiReviewError(f"Gemini 响应结构异常：{resp.text[:300]}") from exc


def call_llm_gemini(prompt: str, api_key: str, model: str = GEMINI_DEFAULT_MODEL,
                    timeout: float = 180.0) -> str:
    """Gemini API（AI Studio 免费层 Key）：generateContent，强制 JSON 输出。

    免费层回退策略：
    - 429 且判定为当日额度（RPD，按项目共享，太平洋时间午夜重置）→ AiQuotaExhausted，
      不浪费调用、不再尝试其他模型；
    - 429 短期限流（RPM/TPM，按模型独立计量）→ 先尊重 Retry-After 指数退避，
      退避仍不缓解则换下一个备选模型；备选链全部限流才按额度耗尽整批终止；
    - 404 / 400 模型不可用（下线、免费层未开放）→ 按 GEMINI_FALLBACK_MODELS 顺序回退；
    - 400/401/403 配置错误（Key 无效等）→ 立即报错，换模型无意义；
    - 5xx / 网络抖动 → 同模型短重试后再回退备选模型；
    - 单厂商墙钟预算 MAX_REVIEW_WALL_SECONDS 兜住最坏情况（备选 × 超时重试叠加）。
    """
    if not api_key:
        raise AiReviewError("gemini 后端需要 GEMINI_API_KEY（https://aistudio.google.com/apikey）")
    body = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": MAX_TOKENS,
            "responseMimeType": "application/json",
        },
    }
    candidates = gemini_candidate_models(model)
    last_detail = ""
    server_outage = False   # 上一个模型已因 5xx 退出；新模型首次再遇 5xx 即判定整体故障
    rate_limited = 0        # 退避仍不缓解而放弃的备选模型数
    deadline = time.monotonic() + MAX_REVIEW_WALL_SECONDS
    for mi, cand in enumerate(candidates):
        url = f"{GEMINI_BASE_URL}/models/{cand}:generateContent"
        rate_try = transient_try = net_try = 0
        while True:
            if time.monotonic() >= deadline:
                raise AiReviewError(
                    f"AI 核查单厂商耗时超过 {MAX_REVIEW_WALL_SECONDS}s 墙钟预算，"
                    "本次保留该厂商旧快照，下次巡检重试。")
            try:
                resp = requests.post(
                    url,
                    headers={"x-goog-api-key": api_key, "content-type": "application/json"},
                    json=body,
                    timeout=timeout,
                )
            except requests.RequestException as exc:
                if net_try < 1:
                    net_try += 1
                    time.sleep(3)
                    continue
                raise AiReviewError(f"Gemini 请求连续失败：{exc}") from exc
            if resp.status_code == 200:
                if mi > 0:
                    print(f"      [warn] 首选模型不可用，Gemini 已回退到 {cand}",
                          file=sys.stderr)
                return _parse_gemini_response(resp)
            err, msg = _gemini_error(resp)
            last_detail = f"{cand} HTTP {resp.status_code}：{msg[:200]}"
            if resp.status_code == 429:
                if _is_daily_quota(err, msg):
                    raise AiQuotaExhausted(
                        "Gemini 免费层当日调用额度（RPD）已用尽（太平洋时间午夜重置），"
                        f"本次跳过 AI 核查、保留旧快照。接口信息：{msg[:160]}")
                if rate_try < MAX_RATE_RETRIES:
                    wait = _retry_after_seconds(
                        resp, RATE_RETRY_BASE_SECONDS * 2 ** rate_try)
                    print(f"      [warn] Gemini 触发短期限流（429），{wait:.0f}s 后重试"
                          f"（{rate_try + 1}/{MAX_RATE_RETRIES}）",
                          file=sys.stderr)
                    time.sleep(wait)
                    rate_try += 1
                    continue
                # RPM/TPM 按模型独立计量，退避不缓解即换下一个备选；仅当整条链都限流
                # 才按额度耗尽整批终止（循环末尾统一抛出 AiQuotaExhausted）。
                rate_limited += 1
                left = len(candidates) - 1 - mi
                print(f"      [warn] Gemini 模型 {cand} 短期限流未缓解"
                      f"（{msg[:100]}），"
                      + (f"尝试剩余 {left} 个备选模型…" if left > 0
                         else "备选模型已用尽，本次跳过其余厂商…"),
                      file=sys.stderr)
                break
            if resp.status_code in TRANSIENT_STATUSES:
                if server_outage:
                    # 上一个模型也在 5xx：不是单模型问题，换厂商也会失败 → 整批终止
                    raise AiServiceOutage(
                        f"Gemini 多个模型连续返回 HTTP {resp.status_code}，"
                        "疑似 Google 侧整体故障，本次跳过 AI 核查、保留旧快照。")
                if transient_try < MAX_TRANSIENT_RETRIES:
                    wait = _retry_after_seconds(resp, 3 * 2 ** transient_try)
                    time.sleep(wait)
                    transient_try += 1
                    continue
                print(f"      [warn] Gemini 模型 {cand} 服务暂不可用"
                      f"（HTTP {resp.status_code}），尝试备选模型…",
                      file=sys.stderr)
                server_outage = True
                break
            if resp.status_code == 404 or (
                    resp.status_code == 400 and _MODEL_MISSING_RE.search(msg)):
                print(f"      [warn] Gemini 模型 {cand} 在当前项目不可用"
                      f"（{msg[:100]}），回退备选模型…",
                      file=sys.stderr)
                break
            # 400/401/403 等配置类错误：重试与换模型都无意义
            raise AiReviewError(f"Gemini 返回 HTTP {resp.status_code}：{msg[:300]}")
    if rate_limited:
        # 至少有一个备选是因持续限流放弃的：额度信号优先于「模型不可用」表述
        raise AiQuotaExhausted(
            f"Gemini 免费层备选链中有 {rate_limited}/{len(candidates)} 个模型"
            "在多次退避后仍持续限流，本次跳过其余厂商、保留旧快照，下次巡检重试。"
            f"接口信息：{last_detail[:160]}")
    raise AiReviewError(f"Gemini 全部备选模型均不可用：{last_detail}")


def call_llm_anthropic(prompt: str, api_key: str, model: str = ANTHROPIC_DEFAULT_MODEL,
                       timeout: float = 180.0) -> str:
    """Anthropic Messages API（可选后端）。"""
    if not api_key:
        raise AiReviewError("anthropic 后端需要 ANTHROPIC_API_KEY")
    try:
        resp = requests.post(
            ANTHROPIC_API_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": MAX_TOKENS,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise AiReviewError(f"LLM 请求失败：{exc}") from exc
    if resp.status_code != 200:
        raise AiReviewError(f"LLM 返回 HTTP {resp.status_code}：{resp.text[:300]}")
    try:
        blocks = resp.json()["content"]
        return "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
    except (KeyError, ValueError) as exc:
        raise AiReviewError(f"LLM 响应结构异常：{resp.text[:300]}") from exc


def parse_json_loose(text: str) -> dict:
    """容忍模型偶发的 ```json 包裹或前后缀文字。"""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fence:
        text = fence.group(1)
    else:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            text = text[start:end + 1]
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AiReviewError(f"模型输出不是合法 JSON：{exc}") from exc
    if not isinstance(data, dict):
        raise AiReviewError("模型输出的 JSON 不是对象")
    return data


def validate_patch(data: dict, corpus_norm: str) -> dict:
    """校验并归一化 AI 补丁；证据必须逐字命中页面正文，否则拒绝整个补丁。

    corpus_norm 可传原始页面拼接文本（内部会再做一次空白归一化）。
    """
    corpus_norm = _norm(corpus_norm)
    if not data.get("changed"):
        return {"changed": False}

    fields = data.get("fields") or {}
    if not isinstance(fields, dict) or not fields:
        raise AiReviewError("changed=true 但 fields 为空")
    clean_fields: dict = {}
    for key, val in fields.items():
        if key not in FIELD_TYPES:
            raise AiReviewError(f"fields 含非法字段：{key}")
        if not isinstance(val, FIELD_TYPES[key]):
            raise AiReviewError(f"字段 {key} 类型错误")
        if isinstance(val, list):
            if not val or not all(isinstance(x, str) and x.strip() for x in val):
                raise AiReviewError(f"字段 {key} 必须是非空字符串列表")
            if len(val) > 12:
                raise AiReviewError(f"字段 {key} 条目过多（>12），疑似异常输出")
        elif not val.strip():
            raise AiReviewError(f"字段 {key} 为空字符串")
        clean_fields[key] = val

    guide_meta = None
    gm = data.get("guide_meta")
    if gm is not None:
        if not isinstance(gm, dict):
            raise AiReviewError("guide_meta 不是对象")
        guide_meta = {}
        if "tiers" in gm:
            tiers = gm["tiers"]
            if not isinstance(tiers, list) or not set(tiers) <= ALLOWED_TIERS:
                raise AiReviewError("guide_meta.tiers 非法")
            guide_meta["tiers"] = tiers
        if "signup" in gm:
            if gm["signup"] not in ALLOWED_SIGNUP:
                raise AiReviewError("guide_meta.signup 非法")
            guide_meta["signup"] = gm["signup"]
        if "scenarios" in gm:
            sc = gm["scenarios"]
            if not isinstance(sc, list) or not set(sc) <= ALLOWED_SCENARIOS:
                raise AiReviewError("guide_meta.scenarios 非法")
            guide_meta["scenarios"] = sc
        for key in ("short", "tip"):
            if key in gm:
                if not isinstance(gm[key], str) or not gm[key].strip():
                    raise AiReviewError(f"guide_meta.{key} 必须是非空字符串")
                guide_meta[key] = gm[key].strip()
        if not guide_meta:
            guide_meta = None

    evidence = data.get("evidence") or []
    if not isinstance(evidence, list) or not evidence:
        raise AiReviewError("changed=true 但缺少 evidence")
    clean_evidence = []
    for item in evidence[:6]:
        if not isinstance(item, dict):
            raise AiReviewError("evidence 条目不是对象")
        quote, url = str(item.get("quote", "")), str(item.get("url", ""))
        if len(quote) < 6:
            raise AiReviewError("证据过短（<6 字符），拒绝采信")
        if _norm(quote) not in corpus_norm:
            raise AiReviewError(f"证据无法在页面原文中逐字定位，疑似臆造：{quote[:60]}")
        clean_evidence.append({"url": url, "quote": quote})
    if not clean_evidence:
        raise AiReviewError("没有有效证据")

    summary = str(data.get("summary", "")).strip() or "官方页面事实变化"
    return {
        "changed": True,
        "summary": summary[:200],
        "fields": clean_fields,
        "guide_meta": guide_meta,
        "evidence": clean_evidence,
    }


def review_vendor(vendor_id: str, brand: str, profile: dict, guide_meta: dict,
                  pages: list[dict], api_key: str = "", model: str | None = None,
                  backend: str | None = None) -> dict:
    """完整流程：组 prompt → 调模型 → 解析 → 校验。返回归一化补丁 dict。"""
    backend = resolve_backend(backend)
    if not model:
        model = default_model(backend)
    prompt = build_user_prompt(vendor_id, brand, profile, guide_meta, pages,
                               char_budget=TOTAL_CHAR_BUDGET)
    raw = call_llm(prompt, api_key=api_key, model=model, backend=backend)
    data = parse_json_loose(raw)
    # 证据只要求命中模型实际看到的文本（prompt 内含预算截断后的页面原文）
    corpus_norm = _norm(prompt)
    return validate_patch(data, corpus_norm)


def apply_patches(overlay_path: Path, patches: dict[str, dict]) -> None:
    """把通过校验的补丁合并写入 profile_overrides.json（整体字段覆盖）。"""
    try:
        overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
        if not isinstance(overlay, dict):
            overlay = {}
    except (FileNotFoundError, json.JSONDecodeError):
        overlay = {}

    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for vendor_id, patch in patches.items():
        if not patch.get("changed"):
            continue
        entry = overlay.setdefault(vendor_id, {})
        entry.update(patch["fields"])
        if patch.get("guide_meta"):
            entry["guide_meta"] = patch["guide_meta"]
        entry["_updated"] = now
        entry["_summary"] = patch["summary"]
        # 证据累积保留最近 20 条，便于 PR 审阅与事后追溯
        old_ev = entry.get("_evidence", [])
        if not isinstance(old_ev, list):
            old_ev = []
        entry["_evidence"] = (old_ev + patch["evidence"])[-20:]
    overlay_path.write_text(
        json.dumps(overlay, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
