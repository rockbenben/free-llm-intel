# -*- coding: utf-8 -*-
"""
provider_profiles.py — 54 家 LLM 厂商深度情报知识库与 Google 翻译服务
参考 FreeLLM-API-KeyHub 格式：免费模型与额度逐模型内联标注（免费 tokens /
限速 RPM / 免费层规则），账户级注册福利单独说明，附有效期、限制条件与官方直达入口。
"""

from __future__ import annotations

import atexit
import json
import re
from pathlib import Path
from threading import Lock

import requests

_TRANS_CACHE: dict[str, str] = {}
_TRANS_FAILED: set[str] = set()   # 本次运行内翻译失败的原文（不写磁盘，下次运行重试）
_TRANS_LOCK = Lock()
_TRANS_DIRTY = 0
_CACHE_PATH = Path(__file__).resolve().parent / ".translate_cache.json"


def _save_trans_cache() -> None:
    try:
        tmp = _CACHE_PATH.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(_TRANS_CACHE, ensure_ascii=False),
                       encoding="utf-8")
        tmp.replace(_CACHE_PATH)
    except Exception:
        pass


try:
    if _CACHE_PATH.exists():
        _TRANS_CACHE = json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
except Exception:
    pass
atexit.register(_save_trans_cache)


_CJK_CHAR = re.compile(r"[一-鿿㐀-䶿]")
_HALF_TO_FULL = {",": "，", ".": "。", ";": "；", ":": "：", "?": "？", "!": "！"}


def normalize_zh_punct(text: str) -> str:
    """把中文行里紧贴汉字的半角句读转为全角（口径同 repo-facade checker）。

    巡检证据是官方页原文 / 机翻文本，常混入半角标点（如「输入价格:¥0」）。
    行内代码与 URL 先占位保护；冒号后接数字 / 斜杠（16:9、端口）不动；
    逗号句号等仅当下一个字符是汉字或行尾时才转，语言列表式「, 空格 + 西文」放过。
    """
    if not text:
        return text
    saved: list[str] = []

    def _shield(m: re.Match) -> str:
        saved.append(m.group(0))
        return f"\x00{len(saved) - 1}\x00"

    protected = re.sub(r"`[^`]*`", _shield, text)
    protected = re.sub(r"https?://\S+", _shield, protected)
    chars = list(protected)
    for i, ch in enumerate(chars):
        full = _HALF_TO_FULL.get(ch)
        if not full or not _CJK_CHAR.match(chars[i - 1] if i > 0 else ""):
            continue
        if ch == "." and i + 1 < len(chars) and chars[i + 1] == ".":
            continue
        nxt = chars[i + 1] if i + 1 < len(chars) else ""
        if ch == ":":
            if nxt and nxt in "0123456789/":
                continue
        elif nxt and not _CJK_CHAR.match(nxt) and not re.match(r"[　-〿＀-￯*~“”「」]", nxt):
            continue
        chars[i] = full
    out = "".join(chars)
    out = re.sub(r"([，。、；：？！]) +(?=[一-鿿])", r"\1", out)
    while re.search(r"\x00\d+\x00", out):
        out = re.sub(r"\x00(\d+)\x00", lambda m: saved[int(m.group(1))], out)
    return out


# 纯专名短标题：1–2 个词、每词首字母大写（`Magistral` / `Pixtral Large` / `Le Chat`）。
# 这类标题**不翻译** —— 见 translate_to_zh 里的第三条守卫。
_PROPER_NOUN_TITLE = re.compile(r"^[A-Z][\w'’\-]*(?:\s+[A-Z][\w'’\-]*)?$")
# 首词是这些常见英文词时说明是句子而不是专名（`Introducing Mistral`、
# `Large Enough`），照常翻译。
_EN_STOPWORDS = {
    "a", "all", "an", "and", "announcing", "better", "beyond", "bringing",
    "building", "cheaper", "enough", "faster", "from", "getting", "how",
    "improved", "improving", "inside", "introducing", "launching", "large",
    "making", "more", "new", "now", "our", "releasing", "small", "stronger",
    "the", "update", "updates", "upgrading", "using", "we", "what", "when",
    "where", "why",
}


def _is_proper_noun_title(text: str) -> bool:
    """是否为「纯专名」短标题（品牌 / 产品名）—— 这类标题不该送去翻译。"""
    t = (text or "").strip()
    if not _PROPER_NOUN_TITLE.match(t):
        return False
    return t.split()[0].lower() not in _EN_STOPWORDS


def translate_to_zh(text: str, timeout: float = 4.0) -> str:
    """非中文内容借助 Google 公开 translate 接口自动翻译为中文。

    成功结果持久化到 .translate_cache.json（跨运行复用，线程安全）；
    翻译失败的条目只在本次运行内回退原文、不落盘，以便下次运行重试。
    """
    global _TRANS_DIRTY
    if not text or not text.strip():
        return text
    clean_text = text.strip()
    # 标识符形态（模型 id 等）**在查缓存之前**就返回：整串没有空格、且含 - / . _ 之一。
    # 实测 Google 会把 "qwen/qwen3-coder-30b-a3b-instruct：—" 译成
    # "qwen/qwen3-coder-30b-a3b-指令：—" —— 模型名被改掉，比不翻更糟。
    # 正常标题都带空格，所以这条不会误伤。
    # 必须放在缓存查询前：错误的译文可能**已经落进 .translate_cache.json**（本地就撞到了），
    # 放后面等于对历史缓存不生效。
    if " " not in clean_text and re.search(r"[-/._]", clean_text):
        return clean_text
    # 含**型号**的标题也不翻：字母紧邻数字（`H3` / `4.6` / `v2`）就是型号信号。
    # 实测 Google 把 `MiniMax H3` 译成 `迷你最大H3`（品牌名被改写），
    # `qwen3.8-omni-flash` 译成 `qwen3.8-全向闪存`。带空格的品牌名上面那条拦不住。
    # 宁可留英文，也不翻坏品牌名；纯散文标题（无型号）照常翻译。
    # 同样放在缓存查询前 —— 已翻坏的译文可能已在缓存里，放后面就治不了历史数据。
    if re.search(r"[A-Za-z]\d|\d[A-Za-z]", clean_text):
        return clean_text
    # 纯专名短标题同样不翻：实测 Google 把 `Magistral` 译成「公路」、`Pixtral Large`
    # → 「像素大号」、`Le Chat` → 「猫」、`Codestral` → 「共纹」—— 品牌名一旦被汉化，
    # 标题彻底失去可检索性，读者也不知道那是什么。上面两条都拦不住它
    # （`Le Chat` 有空格，`Magistral` 既无符号也无数字）。
    # 同样放在缓存查询前：坏译文可能已落进 .translate_cache.json，放后面治不了历史数据。
    if _is_proper_noun_title(clean_text):
        return clean_text
    with _TRANS_LOCK:
        if clean_text in _TRANS_CACHE:
            return _TRANS_CACHE[clean_text]
        if clean_text in _TRANS_FAILED:
            return clean_text
    # 中文字符占比 > 35% 则视为已是中文，无需翻译
    cjk_count = len(re.findall(r"[\u4e00-\u9fff]", clean_text))
    if cjk_count / max(len(clean_text), 1) > 0.35:
        with _TRANS_LOCK:
            if clean_text not in _TRANS_CACHE:
                _TRANS_CACHE[clean_text] = clean_text
                _TRANS_DIRTY += 1
        return clean_text
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": "zh-CN",
            "dt": "t",
            "q": clean_text,
        }
        resp = requests.get(url, params=params, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            translated = "".join(part[0] for part in data[0] if part and part[0])
            if translated:
                with _TRANS_LOCK:
                    if clean_text not in _TRANS_CACHE:
                        _TRANS_CACHE[clean_text] = translated
                        _TRANS_DIRTY += 1
                        if _TRANS_DIRTY >= 100:
                            _TRANS_DIRTY = 0
                            _save_trans_cache()
                return translated
    except Exception:
        pass
    with _TRANS_LOCK:
        _TRANS_FAILED.add(clean_text)
    return clean_text


CATEGORY_TITLES = {
    "domestic": "## Part 1：国内主流大语言模型（免费额度与接入指南）",
    "international": "## Part 2：国际主流大模型与极速推理服务（免费层与调用配额）",
    "cloud": "## Part 3：云原生算力与 Serverless 部署平台（免费体验与算力额度）",
}

CATEGORY_DESCRIPTIONS = {
    "domestic": "> 以下平台面向开发者与个人用户，注册/认证后可获得**实实在在的免费额度**或**永久免费调用模型**。",
    "international": "> 以下平台包含官方提供的**永久免费层（Free Tier）**、**试用密钥（Trial Key）**或**注册赠送体验金**，部分海外模型支持免绑卡直接调用。",
    "cloud": "> 以下平台提供**每月循环赠送的 GPU 免费算力**、**大额公有云试用抵扣金**或**大模型 Serverless 托管额度**。",
}

# ---------------------------------------------------------------------------
# 厂商展示顺序（按模型知名度从高到低）
#
# 浏览页（`docs/index.html`）的厂商标签原先按**文章数**排序，于是
# openai / huggingface（归档文章最多）永远钉在最前，而 baseten / ppio /
# digitalocean 这类「平台功能记录」反而排在 claude / gemini 前面 ——
# 与读者对「谁更重要」的直觉正好相反。
#
# 改成按这张表排序：表内的厂商按此顺序，**表外的排在最后**（按 YAML 录入顺序），
# 所以新增厂商不会因为忘记登记而消失。调整顺序只需改这个元组。
#
# ⚠️ 顺序是主观判断，不是任何官方排名 —— 想调整直接改这个元组即可。
# 守卫 `test_vendor_rank_covers_all_vendors` 会检查 id 拼写与漏项。
# ---------------------------------------------------------------------------
VENDOR_RANK: tuple[str, ...] = (
    # 第一梯队：自有旗舰模型、全球知名度最高
    "anthropic", "openai", "deepseek", "google_gemini", "xai_grok", "zhipu_glm",
    "aliyun_qwen", "moonshot_kimi", "mistral", "meta_llama",
    # 第二梯队：常用推理平台与国内主力
    "groq", "volcengine_doubao", "minimax", "tencent_hunyuan", "baidu_qianfan",
    "huggingface", "openrouter", "cloudflare_workers_ai", "cohere", "siliconflow",
    "nvidia_nim", "xiaomi_mimo", "sensetime_sensenova", "iflytek_spark",
    # 第三梯队：国内其他厂商
    "longcat_meituan", "streamlake", "unisound_shanhai", "mthreads_coding",
    "infini_ai", "ppio", "china_telecom_tianyi", "china_mobile_moma",
    "zhinao_360", "dataeye", "dmxapi", "lingyiwanwu_01ai", "kunlun_tiangong",
    # 第四梯队：海外云厂商的托管服务
    "aws_bedrock", "azure_openai", "gcp_vertex_ai", "oracle_oci_ai", "ibm_watsonx",
    # 第五梯队：海外推理 / 部署平台与长尾
    "cerebras", "together_ai", "fireworks_ai", "deepinfra", "nebius", "baseten",
    "modal", "modular_cloud", "stability_ai", "ai21_labs", "jina_ai",
    "morph_labs", "relace", "poolside", "mancer", "anyscale",
    "digitalocean_genai", "inception_labs", "inference_net", "ncompass", "mara",
)


def vendor_rank_index(vendor_id: str) -> int:
    """返回厂商在 `VENDOR_RANK` 中的位次；未登记的厂商排在所有已登记厂商之后。"""
    try:
        return VENDOR_RANK.index(vendor_id)
    except ValueError:
        return len(VENDOR_RANK)

# ---------------------------------------------------------------------------
# 白嫖攻略元数据（README 项目介绍后的「白嫖攻略」独立生成块由 crawler 依据本表渲染）
#
# tiers:      permanent=永久免费层滚动重置 / onetime=注册一次性赠送 /
#             recurring=每日/每月重置额度 / selfhost=开源权重/自托管
# signup:     email=邮箱或 OAuth 免信用卡 / card=需验证付款方式/绑卡
# scenarios:  code/flagship/longctx/image/embed/deploy/credit
# short:      一句话额度摘要，用于攻略表格（带括号补充）
# tip:        防扣费 / 防坑提示（没有则省略）
# ---------------------------------------------------------------------------
GUIDE_META: dict[str, dict] = {
    # ---- 国内 ----
    "zhipu_glm": {"tiers": ["permanent"], "scenarios": ["code", "image", "referral", "student"],
                  "short": "4.x 代 Flash 0 元（新旗舰 5.3 付费）+ 2000 万 tokens 新用户包",
                  "pick": "**4.x 代 Flash 长期 0 元**（4.7/4-Flash/4V + 画图/视频），国内中文场景首选；但新旗舰 5.3-Flash 已收费，免费模型有独立并发限速",
                  "tip": "0 元只限 4.x 代，GLM-5.3/5.3-Flash 要付费（2000 万资源包可抵）；免费模型会换代（旧版下线自动路由新版）；限速数值只在控制台显示。"},
    "aliyun_qwen": {"tiers": ["onetime"], "scenarios": ["flagship"],
                    "short": "每模型 100 万 tokens / 90 天",
                    "tip": "开通模型时勾选「免费额度用完即停」；免费额度仅限北京区域，跨区域调用不扣免费额度。"},
    "baidu_qianfan": {"tiers": ["onetime"], "scenarios": ["flagship"],
                      "short": "17 个模型各 100 万 / 3 个月 + 20 元券"},
    "tencent_hunyuan": {"tiers": ["onetime"], "scenarios": ["embed"],
                        "short": "Hunyuan-a13b 与 embedding 各 100 万"},
    "sensetime_sensenova": {"tiers": ["permanent", "recurring"],
                            "short": "Token Plan 公测：每 5 小时 6 万积分"},
    "siliconflow": {"tiers": ["permanent", "onetime"], "scenarios": ["embed"],
                    "short": "bge/OCR/画图等 0 元模型 + 注册送 14 元券",
                    "pick": "0 元模型矩阵最适合工具链：bge 向量/重排、OCR、Kolors 画图长期免费，注册再送 14 元券试旗舰"},
    "moonshot_kimi": {"tiers": ["onetime"], "scenarios": ["longctx"],
                      "short": "实名送 15 元代金券（可抵 kimi-k3，上下文 1,048,576）"},
    "longcat_meituan": {"tiers": ["onetime"], "scenarios": ["longctx", "referral"],
                        "short": "LongCat-2.0 资源包（1M 上下文，30 天有效）"},
    "dataeye": {"tiers": ["onetime"],
                "short": "注册即领 50 万 tokens（第三方中转，注意风险）"},
    "unisound_shanhai": {"tiers": ["onetime"], "scenarios": ["embed"],
                         "short": "OCR/U2 各 500 万、ASR 5 小时、TTS 5 万字"},
    "china_telecom_tianyi": {"tiers": ["onetime"], "scenarios": ["credit"],
                             "short": "实名最高 2,000 元试用体验金"},
    "iflytek_spark": {"tiers": ["permanent"],
                      "short": "星火 Lite 支持免费使用（需产品页领取）"},
    "volcengine_doubao": {"short": "无统一免费 token 额度；Managed Agents 送 30 小时",
                          "tip": "在控制台开启「安心体验模式」，超限即停，避免自动扣费。"},
    "ppio": {"short": "无公开注册赠金，按量计费",
             "tip": "未实名认证用户有请求频率限制；历史“注册送 5 元”说法官方页无据。"},
    "mthreads_coding": {"short": "MUSA Coding Plan 免费试用 30 天，每日限量 100 名"},
    "xiaomi_mimo": {"tiers": ["onetime", "selfhost"], "signup": "email",
                    "scenarios": ["embed", "referral"],
                    "short": "TTS 系列限时免费 + 新用户注册赠金（40 天）",
                    "tip": "语言模型按量计费（v2.6-pro ¥3/¥6 每百万 tokens），免费只覆盖 TTS 与缓存写入且官方标注「限时」；"
                           "注册赠金 40 天过期、不可抵 Token Plan 订阅。"},
    "anyscale": {"tiers": ["onetime"], "signup": "card",
                 "short": "$100 注册额度（需工作邮箱；无独立免费层，抵扣 Ray 算力）"},
    "inception_labs": {"tiers": ["onetime"], "signup": "email",
                       "short": "新号 1 亿 free tokens，免信用卡"},
    "inference_net": {"tiers": [], "signup": "email",
                      "short": "$0 档 100 万请求是**观测额度**非推理额度；推理需付费部署"},
    "digitalocean_genai": {"tiers": ["onetime"], "signup": "card", "scenarios": ["credit"],
                           "short": "$5 / 90 天通用试用金（非 LLM 免费层，需绑卡）"},
    "streamlake": {"tiers": ["onetime"], "signup": "email", "scenarios": ["code"],
                   "short": "注册开通后分批送免费调用次数（仅基础模型推理）",
                   "tip": "免费额度**分批发放**（初识/探索/首金礼包）、**仅限基础模型推理**、**不可抵扣 Batch 批量推理**，"
                          "具体额度以活动说明为准 ——「Air 永久免费」与「Pro 送 2000 万 tokens/30 天」均无官方依据，不予采信。"},
    # ---- 国际 ----
    "google_gemini": {"tiers": ["permanent"], "signup": "email", "scenarios": ["flagship"],
                      "short": "AI Studio：Gemini 3.x Flash 全系免费层",
                      "pick": "**邮箱注册免信用卡**，免费额度每日滚动重置；Gemini Flash 旗舰能力，海外平台首选"},
    "groq": {"tiers": ["permanent"], "signup": "email", "scenarios": ["code"],
             "short": "gpt-oss 免费层 30 RPM / 1,000 RPD",
             "pick": "极速推理 + **无需付款方式的永久免费层**：30 RPM / 1,000 RPD，写代码与 Agent 调用的海外主力",
             "tip": "旧 Llama-3.1-8b / 3.3-70b 已转 Enterprise 付费，勿按旧清单调用。"},
    "cloudflare_workers_ai": {"tiers": ["permanent", "recurring"], "signup": "email",
                              "scenarios": ["code"],
                              "short": "86 个模型共享每日 1 万 Neurons",
                              "tip": "超量按 $0.011 / 1,000 Neurons 计费，注意每日用量。"},
    "openrouter": {"tiers": ["permanent"], "signup": "email", "scenarios": ["code"],
                   "short": ":free 模型 20 RPM / 50 RPD（充值 $10 升至 1,000 RPD）",
                   "pick": "**一个账号免费用 25+ 模型**：带 `:free` 后缀即免费、无需付款方式，最适合懒得逐家注册",
                   "tip": "只有带 :free 后缀的模型免费；同名付费模型会按量扣费。"},
    "nvidia_nim": {"tiers": ["permanent"], "signup": "email",
                   "short": "免费推理约 40 RPM，不按 token 计费",
                   "tip": "免费接口面向开发评估，不可用于生产环境。"},
    "cohere": {"tiers": ["permanent"], "signup": "email",
               "short": "Trial Key 免费（每月 1,000 次，限非商用）",
               "tip": "Trial Key 明确仅限非商业用途，商用需升级付费套餐。"},
    "jina_ai": {"tiers": ["permanent"], "signup": "email", "scenarios": ["embed"],
                "short": "每 Key 1,000 万 tokens，GitHub 登录免卡"},
    "morph_labs": {"tiers": ["permanent", "recurring"], "signup": "email",
                   "short": "每月 200 次请求 + 工具附带 $10/月算力"},
    "relace": {"tiers": ["permanent"], "signup": "email", "scenarios": ["code"],
               "short": "编程 Agent 专用模型免费套餐"},
    "mancer": {"tiers": ["permanent"], "signup": "email",
               "short": "页面标 FREE 的角色扮演向模型 0 元调用"},
    "cerebras": {"tiers": ["onetime"], "signup": "card",
                 "short": "$5 赠金 / 30 天（需添加付款方式后发放）"},
    "nebius": {"tiers": [], "signup": "card",
               "short": "无自动赠送；绑卡扣 $25 且转为余额，并非赠金"},
    "ai21_labs": {"tiers": ["onetime"], "signup": "email",
                  "short": "$10 credits，邮箱注册免卡"},
    "fireworks_ai": {"tiers": ["onetime"], "signup": "email",
                     "short": "新号 $1 免费额度"},
    "stability_ai": {"tiers": ["onetime", "selfhost"], "signup": "email", "scenarios": ["image"],
                     "short": "新号 25 积分；开源权重年营收 < $100 万免费"},
    "poolside": {"tiers": ["permanent"], "signup": "email", "scenarios": ["code"],
                 "short": "代码模型限时免费（官方未公布截止日）"},
    "huggingface": {"tiers": ["recurring"], "signup": "email",
                    "short": "Inference Providers 每月 $0.10"},
    "mistral": {"tiers": ["permanent"], "signup": "email",
                "short": "免费**端点**：Mistral Moderation 2（Free）+ Labs 实验模型（无新用户赠金）",
                "tip": "免费的是**端点**而非额度：无新用户赠金 / 免费实验层；`Leanstral` 属 Labs 限时收集反馈期，随时可能下线；"
                       "商业模型（Medium 3.5 / Large 3 / Small 4 等）均按量付费；旧「€5 赠金 / 1 RPS 免费层」在现行定价页无据。"},
    # ---- 云 / 算力 ----
    "modal": {"tiers": ["recurring"], "signup": "email", "scenarios": ["deploy"],
              "short": "$30 / 月免费算力，按月重置"},
    "modular_cloud": {"tiers": ["permanent", "selfhost"], "scenarios": ["deploy"],
                      "short": "共享端点免费测试 + 开源自托管永久免费"},
    "meta_llama": {"tiers": ["selfhost"],
                   "short": "Llama 4 Scout/Maverick 免版税权重（可经 Groq/Cloudflare 免费托管调用）"},
    "aws_bedrock": {"tiers": ["onetime"], "signup": "card", "scenarios": ["credit"],
                    "short": "$100 起，6 个月内最高 $300（需信用卡）"},
    "azure_openai": {"tiers": ["onetime"], "signup": "card", "scenarios": ["credit"],
                     "short": "$200 / 30 天（需信用卡或身份验证）"},
    "gcp_vertex_ai": {"tiers": ["onetime"], "signup": "card", "scenarios": ["credit"],
                      "short": "$300 / 90 天 + Always Free（需绑卡）"},
    "oracle_oci_ai": {"tiers": ["onetime"], "signup": "card", "scenarios": ["credit"],
                      "short": "$300 / 30 天 + Always Free（需信用卡验证）"},
    "ibm_watsonx": {"tiers": ["permanent"], "signup": "email",
                    "short": "Free Toolbox/Lite 免卡：30 万 tokens + 20 CUH/月"},
    "infini_ai": {"tiers": ["permanent"], "signup": "email", "scenarios": ["embed"],
                  "short": "嵌入 / 重排接口长期免费 + 网页 Playground 全模型免费体验",
                  "tip": "免费的是**嵌入 / 重排接口**与**网页体验**；GenStudio **API 推理不设试用额度**、按量付费（官方计费文档已明确），"
                         "「注册送 200 万 token」是旧说法，不予采信。"},
    "baseten": {"tiers": ["onetime"], "signup": "email", "scenarios": ["deploy"],
                "short": "新账户试用额度（官方未公开金额，以控制台为准）",
                "tip": "试用额度**金额未公开**，以注册后控制台显示为准；Startup Program（最高 $25,000 算力 + $2,500 Model APIs）"
                       "需申请审核，非注册即得。"},
}

PROVIDER_PROFILES: dict[str, dict] = {
    # ------------------ Part 1: 国内主流大模型平台 (23) ------------------
    "siliconflow": {
        "category": "domestic",
        "display_name": "硅基流动 (SiliconFlow)",
        "openai_compat": {
            "summary": "众多 0 元模型 + 注册送 14 元券",
            "api_key_label": "控制台申请",
            "api_key_url": "https://cloud.siliconflow.cn/account/ak",
            "base_url": "https://api.siliconflow.cn/v1",
            "models": "`PaddleOCR-VL-1.5`, `bge-m3`, `Kolors`",
        },
        "free_quota": "注册即送 **14 元** 通用代金券（官方计费 FAQ 原文：“注册即送 14 元额度”），可抵扣付费模型 token 费用；有效期以账户内券面标注为准",
        "validity": "0 元模型长期免费；代金券有效期以账户标注为准",
        "free_models": [
            "文本 `PaddleOCR-VL-1.5`、`Hunyuan-MT-7B` —— 定价页标注「免费」，**0 元调用**（限速以官方文档为准）",
            "向量 `bge-m3`、重排 `bge-reranker-v2-m3` —— **0 元免费**",
            "图像 `Kolors`、语音 ASR/TTS 系列 —— **0 元免费**",
            "付费旗舰（可用 14 元代金券抵扣）：DeepSeek-V4-Pro/Flash、GLM-5.3/5.2、MiniMax-M2.5、Kimi-K2.7-Code、LongCat-2.0、Qwen3.6-35B 等",
        ],
        "tier_caveats": [
            "**0 元只覆盖小模型 / 向量 / 重排 / 画图 / 语音**（PaddleOCR-VL、Hunyuan-MT、bge、Kolors 等）；DeepSeek-V4、GLM-5.x、Kimi-K2.7 等旗舰全部按量计费，只能用 14 元代金券抵扣",
            "免费模型清单随定价页「免费」标签调整，接入前以 pricing 页实时标注为准；免费模型有平台统一限速",
        ],
        "preconditions": "手机号注册（免费模型无需付费即可调用）",
        "promotions": "官方有邀请返利活动，但具体奖励金额以控制台活动页公示为准（历史页面金额无法在当前官方页复核，不予采信）。",
        "invite_reward": "**未找到官方邀请活动页**：第三方情报库指向的 `siliconflow.cn/about/reward` 已 307 跳转回官网首页（该路径不存在）；所称「注册 + 推荐各得 16 元、可无限叠加」无法复核，**不予采信**。实际奖励以控制台活动页公示为准。",
        "notes": "免费模型清单随平台调整，以定价页「免费」标签为准；旗舰模型按 token 计费，可用代金券抵扣。",
        "links": [
            ("官方主页", "https://siliconflow.cn/"),
            ("定价 / 免费模型清单", "https://siliconflow.cn/pricing"),
            ("API Key 申请直达", "https://cloud.siliconflow.cn/account/ak"),
            ("计费 FAQ（额度说明）", "https://docs.siliconflow.com/cn/faqs/billing-rules"),
        ],
    },
    "volcengine_doubao": {
        "category": "domestic",
        "display_name": "火山引擎 (火山方舟 / 豆包)",
        "free_quota": "**无新用户注册赠金 / 文本 token 免费额度表**（官方免费额度文档现行版本）；唯一可确认的免费项为下方 Managed Agents 时长包",
        "validity": "Agent 免费额度有效期 **2 年**；文本模型以开通页展示为准",
        "free_models": [
            "**Managed Agents（Agent 编排）** —— 赠送 **30 小时运行时长 + 500 次 web_search 工具调用，有效期 2 年**（官方免费额度文档）",
            "文本/多模态大模型**无统一免费 token 额度**：当前在线旗舰 `doubao-seed-evolving`（持续进化版）、Seed-2.1-Pro/Turbo、Seed-2.0 系列，以及托管 DeepSeek-V4-Pro/Flash 正式版、GLM-5.2/4.7 等，开通后按量付费",
        ],
        "preconditions": "注册火山引擎账号并完成实名认证",
        "promotions": "Coding Plan 邀请活动、高校师生扶持等传闻额度无法在当前官方页复核，不予采信，以控制台活动页为准。",
        "student_benefit": "**高校师生扶持未找到官方活动页**：第三方情报库所指 `volcengine.com/docs/82379/1340426` 已 404；现行免费额度文档为 `docs/82379/1522733`（原 1263512 亦 301 重定向至此），其中未见师生专属额度。所称「最高 1 亿 tokens」不予采信。",
        "invite_reward": "**Coding Plan 邀请有礼未找到官方活动页**：第三方情报库所指 `volcengine.com/docs/82379/1455310` 已 404；所称「邀请返 10% 代金券」不予采信。",
        "notes": "方舟（Ark）为模型接入平台，豆包为自研模型系列；支持「安心体验模式」防止超额扣费。",
        "links": [
            ("火山方舟产品页", "https://www.volcengine.com/product/ark"),
            ("火山方舟控制台直达", "https://console.volcengine.com/ark/"),
            ("免费额度官方文档", "https://docs.volcengine.com/docs/82379/1263512?lang=zh"),
            ("计费说明文档", "https://docs.volcengine.com/docs/82379/1099455?lang=zh"),
        ],
    },
    "zhipu_glm": {
        "category": "domestic",
        "display_name": "智谱AI GLM (大模型开放平台)",
        "openai_compat": {
            "summary": "4.x 代 Flash 0 元（新旗舰 5.3-Flash 付费）+ 2000万券",
            "api_key_label": "控制台申请",
            "api_key_url": "https://bigmodel.cn/usercenter/apikeys",
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "models": "`glm-4.7-flash`, `glm-4-flash-250414`, `glm-4v-flash`",
        },
        "free_quota": "新用户注册专享 **2000 万免费 Tokens 资源包 + 120 次图像/视频资源包**（官方定价页首页原文：“新用户注册得 2000 万 Tokens，新模型免费”）——资源包只能抵扣**付费模型**，免费模型另算；有效期以券面标注为准",
        "validity": "免费模型长期 0 元但**会换代**：旧版下线后请求自动路由到新版（如 GLM-4.5-Flash 2026-01-30 下线后自动路由至 GLM-4.7-Flash），旧 model id 可能失效",
        "free_models": [
            "**免费的是 4.x 代 Flash，不含 5.x 新旗舰**：`glm-4.7-flash`（30B 级、200K 上下文、Agentic Coding 强化；GLM-4.5-Flash 下线后自动路由至此）、`glm-4-flash-250414`（智谱首个免费大模型 API）、`glm-z1-flash`（推理）—— 0 元",
            "视觉（4.x 代）：`glm-4v-flash`（首个免费图像理解模型）、`glm-4.6v-flash`、`glm-4.1v-thinking-flash` —— 0 元",
            "多模态生成：`CogView-3-Flash`（图像）、`CogVideoX-Flash`（视频）—— 0 元",
            "**当前旗舰 `glm-5.3-flash`（1M 上下文、原生多模态）是付费模型**，定价为 GLM-5.3 的 1/10，免费层不覆盖；`glm-5.3` / `glm-5.2` 同为付费（可用 2000 万资源包抵扣）",
        ],
        "tier_caveats": [
            "**版本代差**：0 元只覆盖 4.x 代，最新一代 5.x（GLM-5.3 / GLM-5.3-Flash）全部收费；想要最新模型只能用 2000 万资源包抵扣或付费",
            "**限速按模型独立设置且数值不公开**：官方速率限制文档未给统一 RPM/TPM 数值，需登录控制台「速率限制」页查看本账户额度；触发限流返回错误码 1302、平台过载返回 1305；可申请提并发（10 个工作日审核）",
            "**旧模型会下线**：GLM-4.5-Flash 已于 2026-01-30 下线（自动路由至 4.7-Flash）；调用方不应把免费 model id 写死，需关注官方下线公告",
            "2000 万资源包与图像/视频 120 次包为一次性新用户福利，**有效期以券面为准**，不是永久额度",
        ],
        "preconditions": "注册并完成实名认证",
        "promotions": "官方定价页原文：邀好友实名注册得 Tokens，**最高可领取总计 2 亿 Tokens 资源包**（活动规则与奖励以活动页公示为准）。",
        "invite_reward": "**官方邀请活动（已复核）**：成功邀请 1 名新用户完成**实名注册**，**邀请双方各得 2000 万 Tokens** 资源包；**每月可邀请 10 人，上限 2 亿 Tokens**；无需付费/充值，页面无截止日期，按月滚动。文案取自官方前端 bundle 的 i18n 原文（`inviteNewUser` / `placard`）—— 注意 bundle 自身不一致：`tips` 写 GLM-4-Air，其余字段写 GLM-4.5-Air。入口：`bigmodel.cn/special_area`（未登录可读）、`bigmodel.cn/invite`（完整规则在登录墙后）。",
        "student_benefit": "**原「智谱 AI 校园计划」官方页已下线**：`bigmodel.cn/university` 前端路由 redirect 至「活动已下线」页；`zhipu.ai/activity/campus` 经 302 跳转后目标 404。第三方情报库所称「学生认证送 200 万 tokens / 1 个月」无在架官方页，**不予采信**。**现存两处官方入口**：① 清言「开学季送会员卡」`chatglm.cn/activity/giftVip` —— 免费赠送价值 **399 元**智谱清言会员卡年卡，**在校学生与教职工**，每账号限领 1 次，需完成认证（消费端会员，非 API 额度）；② `bigmodel.cn/special_area` 教育专区 —— 高校师生专享低至 6 折**付费**资源包（页面文案未见「学生认证」字样，认证校验规则未公示）。",
        "notes": "免费模型清单与付费档位以 bigmodel.cn/pricing 实时标注为准。",
        "links": [
            ("官方主页", "https://bigmodel.cn/"),
            ("定价中心（新用户资源包与免费模型标注）", "https://bigmodel.cn/pricing"),
            ("API Key 申请直达", "https://bigmodel.cn/usercenter/apikeys"),
            ("免费模型 GLM-4.7-Flash 文档", "https://docs.bigmodel.cn/cn/guide/models/free/glm-4.7-flash"),
            ("免费模型 GLM-4V-Flash 文档", "https://docs.bigmodel.cn/cn/guide/models/free/glm-4v-flash"),
            ("速率限制说明（1302/1305 错误码）", "https://docs.bigmodel.cn/cn/api/rate-limit"),
        ],
    },
    "longcat_meituan": {
        "category": "domestic",
        "display_name": "美团 LongCat (长猫开放平台)",
        "free_quota": "新用户注册赠送 token 资源包，具体数额**公开页未公示**，以注册后账户实际发放为准（“1000 万/5000 万”等历史说法无法复核，不予采信）",
        "validity": "官方定价页标注 token 资源包有效期 **30 天**",
        "free_models": [
            "`LongCat-2.0`（2026-06-30 发布，1M 上下文）—— 调用消耗 token 资源包（新用户包数额以账户到账为准，**资源包有效期 30 天**）",
            "旧 LongCat-Flash 系列已于 2026-05-29 下线",
        ],
        "tier_caveats": [
            "新用户资源包**具体数额官方公开页不公示**（历史「1000 万 / 5000 万」说法无法复核），以注册后账户实际到账为准",
            "资源包**30 天有效**，到期清零；定价与资源包页需登录才能查看；旧 LongCat-Flash 系列已下线",
        ],
        "preconditions": "注册并登录开放平台（定价与资源包页需登录查看）",
        "promotions": "平台有“老带新”邀请活动入口，但奖励规则未在公开页面公示，以控制台内活动页为准。",
        "invite_reward": "官方邀请返佣页：`longcat.chat/platform/referral` 与活动说明页 `longcat.chat/about`（均为前端渲染，巡检需浏览器抓取）；所称「邀请双方各 20% / 10%、被邀者额外 20%」等比例未能在静态页面复核，以页面公示为准。",
        "notes": "兼容 OpenAI 接口格式；缓存命中（Cache Hit）部分按更低费率计费。",
        "links": [
            ("开放平台", "https://longcat.chat/platform/"),
            ("定价页", "https://longcat.chat/platform/pricing"),
        ],
    },
    "aliyun_qwen": {
        "category": "domestic",
        "display_name": "阿里云百炼 (Model Studio / 通义千问)",
        "openai_compat": {
            "summary": "每模型 100 万 / 90 天（北京区）",
            "api_key_label": "控制台申请",
            "api_key_url": "https://bailian.console.aliyun.com/?apiKey=1",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "models": "`qwen3.8-max`, `qwen-plus`",
        },
        "free_quota": "**无独立注册赠金 / 代金券**；免费额度即按模型发放的 tokens（见左栏，官方免费额度文档 help.aliyun.com/zh/model-studio/new-free-quota）",
        "validity": "**90 天**（自额度发放起）",
        "free_models": [
            "自研旗舰 `qwen3.8-max` 及 Qwen3 系列、Qwen-Coder 系列 —— 新用户**每个模型 100 万 tokens** 免费额度，**有效期 90 天**，**仅限北京区域**（开通模型后自动生效，无需领取）",
            "托管第三方模型（DeepSeek-V4、GLM 等）—— 同样按**每模型 100 万 tokens / 90 天 / 北京区域**规则享受，各模型额度独立计算",
        ],
        "tier_caveats": [
            "**额度按模型独立发放，不是账号总额**：每个模型各 100 万 tokens / 90 天，几十个模型各领各的；过期或用完即止，不可结转",
            "**仅限北京区域**：跨区域调用不扣免费额度、会直接按后付费计费",
            "开通模型时务必勾选「免费额度用完即停」，否则超额自动转付费；无独立注册代金券",
        ],
        "preconditions": "注册阿里云账号；免费额度按官方文档规则在百炼平台开通模型后即可使用",
        "promotions": "“云大使”返利、知识库 720 小时试用等说法无法在当前官方免费额度页复核，不予采信。",
        "invite_reward": "**阿里云“云大使”官方页不可达**：第三方情报库所指 `k.aliyun.com/smarter/ai-distributor` 本轮无法访问；所称「推广返利 30%–45%」不予采信。",
        "notes": "建议在控制台开启“免费额度用完即停”避免超额扣费；跨区域调用不扣免费额度。",
        "links": [
            ("百炼免费额度官方文档", "https://help.aliyun.com/zh/model-studio/new-free-quota"),
            ("API Key 申请直达", "https://bailian.console.aliyun.com/?apiKey=1"),
            ("百炼控制台", "https://bailian.console.aliyun.com/"),
            ("通义千问官网", "https://tongyi.aliyun.com/"),
        ],
    },
    "baidu_qianfan": {
        "category": "domestic",
        "display_name": "百度智能云千帆大模型平台",
        "openai_compat": {
            "summary": "17 个模型各 100 万 / 3 个月",
            "api_key_label": "控制台申请",
            "api_key_url": "https://console.bce.baidu.com/qianfan/overview",
            "base_url": "https://qianfan.baidubce.com/v2",
            "models": "`ernie-5.0`, `ernie-4.5-turbo`, `ernie-x1.1`",
        },
        "free_quota": "完成实名认证另送 **20 元代金券**（有效期 1 个月）；模型免费 tokens 见左栏（官方免费额度文档 cloud.baidu.com/doc/qianfan/s/Imi2rpirg）",
        "validity": "模型免费额度 **3 个月**；代金券 **1 个月**",
        "free_models": [
            "**17 个模型**（含 `ERNIE 5.1`、`ERNIE 5.0`、`ERNIE X1.1`、`ERNIE 4.5-Turbo` 等）—— 新用户**每个模型赠送 100 万 tokens，有效期 3 个月**",
            "旧 ERNIE-Speed/Lite/Tiny 永久免费模型**已下架**，平台当前无永久免费模型",
        ],
        "tier_caveats": [
            "**17 个模型各 100 万 tokens / 3 个月**，额度按模型独立计算；另送的 20 元代金券只有 **1 个月**有效期",
            "旧 ERNIE-Speed / Lite / Tiny **永久免费模型已下架**，平台当前无永久免费层，额度用尽需开通付费",
        ],
        "preconditions": "百度智能云注册并完成实名认证",
        "promotions": "不定期发放算力代金券，以控制台活动页为准。",
        "notes": "免费额度直接扣减，剩余量可在控制台计费中心查看；额度用尽后需开通付费。",
        "links": [
            ("千帆免费额度官方文档", "https://cloud.baidu.com/doc/qianfan/s/Imi2rpirg"),
            ("API Key / 控制台直达", "https://console.bce.baidu.com/qianfan/overview"),
            ("千帆产品页", "https://cloud.baidu.com/product/qianfan.html"),
            ("千帆控制台", "https://console.bce.baidu.com/qianfan/"),
        ],
    },
    "tencent_hunyuan": {
        "category": "domestic",
        "display_name": "腾讯云混元 (TokenHub)",
        "free_quota": "**无额外注册赠金**；免费资源即左栏两款模型的 tokens（官方免费额度文档 /document/product/1729/97731）",
        "validity": "免费资源包有效期 **1 年**（官方文档原文）",
        "free_models": [
            "`Hunyuan-a13b`（共享版）—— 首次开通赠送 **100 万 tokens，有效期 1 年**",
            "文本嵌入模型 —— 赠送 **100 万 tokens，有效期 1 年**",
            "付费旗舰：混元 `Hy4` 预览版（2026-08-28 发布）、`Hy-MT2-Pro`（翻译）、`Hy-Role-Latest`（角色扮演）、`Hy-Image-3.0`（图像）等按 token 后付费；旧 Hunyuan-Lite/Standard 已下线",
        ],
        "tier_caveats": [
            "**只有两款模型免费**：Hunyuan-a13b 共享版、文本嵌入模型各 100 万 tokens、有效期 1 年；旗舰 Hy4、Hy-Image、角色扮演等按 token 后付费",
            "旧 Hunyuan-Lite / Standard 已下线——流传的「Hunyuan-lite 完全免费」已失效",
        ],
        "preconditions": "腾讯云注册并完成实名认证",
        "promotions": "兼容 OpenAI 格式 API；模型接入统一在 TokenHub 调度台管理。",
        "notes": "免费额度限 a13b 共享版与嵌入模型；旗舰 Hy4 等按 token 后付费。",
        "links": [
            ("免费额度官方文档", "https://cloud.tencent.com/document/product/1729/97731"),
            ("混元产品页", "https://cloud.tencent.com/product/tclm"),
            ("TokenHub 说明", "https://cloud.tencent.com/document/product/1729/111007"),
        ],
    },
    "minimax": {
        "category": "domestic",
        "display_name": "MiniMax (稀宇科技)",
        "openai_compat": {
            "summary": "新用户 Token Plan 订阅/体验",
            "api_key_label": "控制台申请",
            "api_key_url": "https://platform.minimax.cn/console/access?tab=api-keys",
            "base_url": "https://api.minimax.chat/v1",
            "models": "`MiniMax-M3`, `MiniMax-M2.7`",
        },
        "free_quota": "**无公开注册赠金**：现行官方文档目录中无注册赠送代金券页面（历史“注册送券/90 天”说法无法复核，不予采信），以控制台实际到账为准",
        "validity": "以账户内券面标注为准",
        "free_models": [
            "**无免费模型层**：当前旗舰 `MiniMax-M3`（官方原文：全新 MSA 注意力架构、1M 上下文、原生多模态 Coding/Agentic 模型）、`MiniMax-M2.7`/M2.7-highspeed，以及视频 `H3`、`speech-2.8`、`music-3.0` 均为付费（Token Plan 订阅或积分包）",
            "M2.5/M2.1/M2 已归入 Legacy，MiniMax-Text-01 与 abab6.5s 已下架",
        ],
        "preconditions": "账号注册并完成实名认证",
        "promotions": "**Token Plan 订阅**（官方定价文档）：Plus ¥49/月、Max ¥119/月、Ultra ¥469/月，覆盖 M3/M2.7/图像/语音（H3 视频、音色克隆等特殊模型除外）；预付积分包 1,000 积分 = ¥7，有效期 365 天。",
        "notes": "“Builder 共建者邀请返券”在现行官方文档中无入口记载；开放平台文档站已统一至 platform.minimax.cn/docs（旧域名 platform.minimaxi.com 全站 301 跳转至此）。",
        "links": [
            ("API Key 申请直达", "https://platform.minimax.cn/console/access?tab=api-keys"),
            ("模型介绍文档", "https://platform.minimax.cn/docs/guides/models-intro"),
            ("Token Plan 定价", "https://platform.minimax.cn/docs/guides/pricing-token-plan"),
            ("官方网站", "https://www.minimax.cn/"),
        ],
    },
    "moonshot_kimi": {
        "category": "domestic",
        "display_name": "Kimi 开放平台 (月之暗面)",
        "openai_compat": {
            "summary": "实名送 15 元券（1M 长上下文）",
            "api_key_label": "控制台申请",
            "api_key_url": "https://platform.kimi.com/console/api-keys",
            "base_url": "https://api.moonshot.cn/v1",
            "models": "`kimi-k2.7-code`, `kimi-k2.6`",
        },
        "free_quota": "实名认证赠送 **15 元代金券**（官方账号与支付文档原文：“认证成功后会为您赠送 15 元代金券，可用于支持该代金券的模型”）；有效期官方未载明，以券面标注为准",
        "validity": "以券面标注为准（官方文档未载明有效期）",
        "free_models": [
            "`kimi-k2.7-code`（含 highspeed 版）、`kimi-k2.6`（256K）—— 付费模型，**可用 15 元代金券抵扣**",
            "`kimi-k3`（2.8 万亿参数、原生视觉理解、上下文 1,048,576 tokens；输入 ¥20/输出 ¥100 每百万、缓存命中 ¥2）—— 付费，且官方原文**“Kimi K3 不支持使用新用户代金券”**，需充值解锁",
            "旧 `moonshot-v1` 全系列与 `kimi-k2.5` 已于 **2026-08-31 下线**（调用返回 404）",
        ],
        "tier_caveats": [
            "送的是 **15 元代金券而非免费模型**；`kimi-k3` 官方明确**不支持新用户代金券**，必须充值才能用",
            "代金券有效期官方文档未载明，以券面标注为准；旧 moonshot-v1 全系列、kimi-k2.5 已下线",
        ],
        "preconditions": "国内注册并完成实名认证",
        "promotions": "官方原文：**“Kimi K3 不支持使用新用户代金券”**，需充值后解锁；充值返券活动在官方财务文档中无记载。",
        "invite_reward": "**邀请活动官方页不存在**：第三方情报库所指 `platform.kimi.com/docs/guide/invite-rewards` 已 308 重定向到 `/docs/get-api-key`；所称「邀请双方各得 240 元」不予采信。",
        "notes": "开放平台已统一至新域名 platform.kimi.com（moonshot.cn 入口均跳转至此）。",
        "links": [
            ("API Key 管理直达", "https://platform.kimi.com/console/api-keys"),
            ("API Key 获取指南", "https://platform.kimi.com/docs/get-api-key"),
            ("账号与支付（15 元代金券说明）", "https://platform.kimi.com/docs/guide/account-and-payments"),
            ("模型列表", "https://platform.kimi.com/docs/models"),
            ("K3 定价", "https://platform.kimi.com/docs/pricing/chat-k3"),
        ],
    },
    "ppio": {
        "category": "domestic",
        "display_name": "PPIO 派欧云 (分布式大模型算力)",
        "free_quota": "**无公开注册赠金**：现行官方产品页、快速开始、计费文档与公告索引均无新用户赠金记载（历史“注册送约 5 元/500 万 tokens”无法复核）；官方公告原文：“邀请奖励”活动已于 **2025-11-30 结束**",
        "validity": "不适用（无公开赠送政策）",
        "free_models": [
            "**无免费模型层**，全部按量付费：DeepSeek V4 Pro/Flash/Vision Exp、V3.2、DeepSeek OCR 2；Qwen3.8 Max/Flash、Qwen3.7 Max、Qwen3 Coder Next；GLM 5.3/5.2/5.1；Kimi K3/K2.7 Code/K2.6；MiniMax-M3/M2.7；小米 MiMo V2.5/Pro；Fusion 融合模型（Beta）。**清单中已无 Llama**",
        ],
        "preconditions": "注册账号并绑定手机号；按量付费",
        "promotions": "提供 Token Plan 订阅套餐（ppio.com/token-plan）；“初创扶持最高 10 万元”在官方页面无记载，不予采信。",
        "notes": "分布式 GPU 云，OpenAI 兼容接口，国内多节点加速。",
        "links": [
            ("大模型 API 定价与模型清单", "https://ppio.com/ai-computing/llm-api"),
            ("官方公告（活动记录）", "https://ppio.com/docs/announcement/announcement"),
            ("Token Plan", "https://ppio.com/token-plan"),
        ],
    },
    "deepseek": {
        "category": "domestic",
        "display_name": "DeepSeek (深度求索)",
        "free_quota": "**无公开赠送政策**：现行官方定价页与更新日志均无新用户赠送 token 政策（历史“500 万 tokens/30 天”无法复核，不予采信）；账户扣费顺序中存在“赠送余额”项，实际以注册后账户到账为准",
        "validity": "以账户内余额标注为准",
        "free_models": [
            "**无免费模型层**，当前在架仅 V4 系列且按量计费：`deepseek-v4-flash`（DeepSeek-V4-Flash-0731）、`deepseek-v4-pro`（DeepSeek-V4-Pro-0813，2026-08-13 GA）、`deepseek-v4-flash-vision-exp`；上下文 1M（最大输出 384K）",
            "峰谷定价（元/百万 tokens，高峰=北京时间工作日 9:00–12:00、14:00–18:00）：v4-flash 输出 9.0 高峰/4.5 空闲、缓存命中输入低至 0.05；v4-pro 输出 27.0/13.5",
            "旧 `deepseek-chat`/`deepseek-reasoner` 已于 **2026-07-24 停用**（过渡期分别指向 v4-flash 的非思考/思考模式）",
        ],
        "preconditions": "注册平台账号；按量计费，并发限制随账户充值等级（Tier）提升",
        "promotions": "实行**峰谷定价**（元/百万 tokens，高峰为北京时间工作日 9:00–12:00、14:00–18:00）：v4-flash 输出 9.0（高峰）/4.5（空闲），缓存命中输入低至 0.05；v4-pro 输出 27.0/13.5。",
        "notes": "V3/R1 时代价格（缓存 0.5 元、输出 8 元）已作废；官方无 RSS，更新见 updates 页。",
        "links": [
            ("定价文档（人民币峰谷价）", "https://api-docs.deepseek.com/zh-cn/quick_start/pricing"),
            ("API Key 管理", "https://platform.deepseek.com/api_keys"),
            ("更新日志", "https://api-docs.deepseek.com/zh-cn/updates/"),
            ("API 平台", "https://platform.deepseek.com/"),
        ],
    },
    "iflytek_spark": {
        "category": "domestic",
        "display_name": "科大讯飞星火 (Spark API)",
        "free_quota": "**无独立注册赠金**；唯一免费项为星火 Lite（额度需在星火产品页领取，规则以领取页为准）；进阶版本无公开赠送额度记载",
        "validity": "Lite 免费额度以产品页领取规则为准（官方文档无“永久”字样）",
        "free_models": [
            "**星火 Lite** —— 官方 HTTP 调用文档原文“具有更高的响应速度，**支持免费使用**”，免费额度在星火产品页领取（QPS/限速以领取页规则为准）",
            "付费版本：Pro、Pro-128K、Max、Max-32K、**4.0 Ultra**（已升级至 X1.5 快思考模式），另有深度推理 **X2** 产品线；Max 套餐将于 **2026-03-10 下线**并合并至 Ultra",
        ],
        "tier_caveats": [
            "免费的只有**星火 Lite 一个模型**，且额度**必须先到星火产品页手动领取**（不是注册自动到账）；QPS / 限速以领取页规则为准",
            "进阶版本（Pro/Max/4.0 Ultra 等）无公开免费额度",
        ],
        "preconditions": "讯飞开放平台注册并实名认证",
        "promotions": "面向教育、政企与开发者提供专项适配；支持语音/多模态混合调用。",
        "notes": "旧档案“Lite 1–3 QPS”“X2-VL”“V2.0/V3.5”等名称/数字在现行文档中无记载（V3.5 即 Max 的 model 参数 generalv3.5）。",
        "links": [
            ("星火 API 产品页（免费额度领取）", "https://xinghuo.xfyun.cn/sparkapi"),
            ("HTTP 调用文档（模型版本说明）", "https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html"),
            ("控制台", "https://console.xfyun.cn/"),
        ],
    },
    "streamlake": {
        "category": "domestic",
        "display_name": "StreamLake (快手万擎)",
        "free_quota": "免费资源包**分批发放**（初识礼包/探索礼包/首金礼包）：官方免费资源包文档原文“注册并开通服务，即可分批获得一定额度的免费调用模型推理服务的次数”“免费额度仅限基础模型推理使用”“具体发放额度以活动说明为准”",
        "validity": "各资源包有效期以活动说明为准（官方文档无“永久免费”表述）",
        "free_models": [
            "**基础模型推理** —— 注册开通后分批获得免费调用次数（不可抵扣 Batch 批量推理；具体次数以活动说明为准）",
            "在架模型：自研 `KAT-Coder-Pro-V2.5`/`KAT-Coder-Air-V2.5`（均为 256K 上下文/80K 输出）及托管 DeepSeek-V4-Flash/Pro、GLM-5.x、MiniMax-M2.x、Kimi-K2.x、MiMo-V2-Pro、Qwen3、Keye-VL 等；KAT-Coder V1 已下线，“快意 KwaiYii”已不在模型列表",
        ],
        "tier_caveats": [
            "免费额度**分批发放**（初识礼包 / 探索礼包 / 首金礼包），各资源包有效期以活动说明为准 —— 官方文档**无「永久免费」表述**",
            "免费额度**仅限基础模型推理**，且**不可抵扣 Batch 批量推理**调用",
            "具体发放额度官方文档未写明（原文「以活动说明为准」）；「Air 永久免费」「Pro 送 2000 万 tokens / 30 天」无官方依据，不予采信",
        ],
        "preconditions": "注册 StreamLake 账号并开通服务",
        "promotions": "免费额度不可抵扣批量推理（Batch）调用；快手旗下代码与推理模型平台。",
        "notes": "“Air 永久免费”“Pro 送 2000 万 tokens/30 天”无官方依据（原活动说明页已 404），不予采信。",
        "links": [
            ("官方主页", "https://www.streamlake.com/"),
            ("免费资源包说明", "https://www.streamlake.com/document/WANQING/mdsor5767ob7s796sp6"),
            ("模型列表文档", "https://www.streamlake.com/document/WANQING/mdrax1ixkgpgh1ms1na"),
        ],
    },
    "china_telecom_tianyi": {
        "category": "domestic",
        "display_name": "中国电信 (天翼云 / 息壤智算)",
        "free_quota": "注册并完成实名认证，**最高可得 2000 元试用体验金**（天翼云试用中心官方原文）；有效期以试用中心规则为准",
        "validity": "试用体验金与 tokens 有效期以试用中心规则为准",
        "free_models": [
            "星辰大模型专区托管 GLM、DeepSeek V4/V3.2、Qwen 系列 —— 专区设有 **50 万免费 tokens** 领取入口（以体验中心实际到账为准）",
            "电信自研 `TeleChat3`（TeleChat3-36B-Thinking、TeleChat3-Coder-36B 等）由 Tele-AI 发布并开源在 Hugging Face，**非息壤在售清单**（可自行下载部署）",
            "注意：**2500 万 tokens 对应的是 29.9 元/月付费套餐（畅享版），不是免费额度**；Token Plan 轻享版 9.9 元/月含 1000 万 tokens（限 DeepSeek V3.2）",
        ],
        "tier_caveats": [
            "「最高 2000 元」是试用中心**多档活动的上限、不是注册即得全额**，实际到账金额与有效期以试用中心规则为准",
            "星辰大模型专区另有 50 万 tokens 领取入口；注意 2500 万 tokens 对应的是 **29.9 元/月付费套餐**，不是免费额度",
        ],
        "preconditions": "实名认证天翼云账号",
        "promotions": "Token Plan 订阅：轻享版 **9.9 元/月含 1000 万 tokens**（限 DeepSeek V3.2）、畅享版 29.9 元/4000 万、尊享版 49.9 元/8000 万。",
        "notes": "旧档案“2500 万 tokens 免费包”有误：2500 万对应的是 29 元/月付费套餐，非免费额度。",
        "links": [
            ("试用中心（2000 元体验金）", "https://www.ctyun.cn/act/trial/central"),
            ("星辰大模型专区", "https://www.ctyun.cn/act/AI/zhuanxiang"),
            ("Tele-AI 官方文档站", "https://www.teleai.com.cn/docOverview"),
        ],
    },
    "sensetime_sensenova": {
        "category": "domestic",
        "display_name": "商汤日日新 (SenseNova / 大装置)",
        "free_quota": "**Token Plan 公测版免费**即左栏额度（无独立注册赠金）；正式商用定价以官方后续公告为准",
        "validity": "公测期间滚动有效（每 5 小时自动刷新）",
        "free_models": [
            "`SenseNova 6.8 Flash Lite`（轻量文本）、`SenseNova U1 Fast`（多模态）等 —— **Token Plan 公测免费：每 5 小时 60,000 积分**（滚动刷新），单账号可创建 **20 个 API Key**；各模型按积分计量",
        ],
        "tier_caveats": [
            "免费仅限 **Token Plan 公测期**：每 5 小时 60,000 积分滚动刷新，**正式商用定价待官方公告**——公测结束后现有免费额度可能取消或改规则",
            "按积分而非 token 计量，不同模型积分单价不同；单账号最多 20 个 API Key",
        ],
        "preconditions": "注册商汤大装置（SenseCore）开放平台账号",
        "promotions": "公测阶段 Token Plan 免费；正式商用定价以官方后续公告为准。",
        "notes": "按积分而非直接 token 计费，不同模型积分单价不同。",
        "links": [
            ("Token Plan 官方页", "https://www.sensenova.cn/token-plan"),
            ("官方主页", "https://www.sensenova.cn/"),
            ("大装置控制台", "https://console.sensecore.cn/"),
        ],
    },
    "dmxapi": {
        "category": "domestic",
        "display_name": "DMXAPI (大模型聚合转发)",
        "free_quota": "新用户注册后可能发放测试额度，**数额未公开**，以账户内实际到账为准（历史“$1/8 元”说法无法在当前官方页复核，不予采信）；为非官方第三方中转，额度不属模型厂商承诺",
        "validity": "测试额度用完即止",
        "free_models": [
            "**无公开免费模型层**：第三方聚合转发，模型清单随上游更新，当前文档列出 GPT-5.x、Claude 4.5、Gemini 3、DeepSeek 等系列（以文档站模型列表为准）",
        ],
        "preconditions": "邮箱或手机号注册",
        "promotions": "支持人民币结算，多节点故障转移；为非官方第三方中转，额度与稳定性不属官方承诺。",
        "notes": "聚合中转服务，适合统一接口调试；生产用途请评估上游合规性。",
        "links": [
            ("官方文档站（模型列表）", "https://doc.dmxapi.cn/"),
            ("人民币价格表", "https://www.dmxapi.cn/rmb"),
            ("官方主页", "https://www.dmxapi.cn/"),
        ],
    },
    "zhinao_360": {
        "category": "domestic",
        "display_name": "360 智脑开放平台",
        "free_quota": "新用户注册赠送测试资源，**具体数额/有效期未在公开页公示**，以账户实际发放为准（“1000 万 tokens/30 天”说法无法复核，不予采信）",
        "validity": "以资源包标注为准",
        "free_models": [
            "**无公开免费模型层**：平台转为聚合模式，模型列表约 86 款（含第三方模型）；自研模型 `360zhinao-pro` 定价输入 ¥2/百万 tokens、输出 ¥5/百万 tokens（以定价页为准）",
        ],
        "preconditions": "360 账号注册并完成实名认证",
        "promotions": "集成 360 搜索增强能力；模型与价格以 /open/models 页面实时列表为准。",
        "notes": "自研模型与第三方托管模型同页计费，注意区分。",
        "links": [
            ("模型与定价页", "https://ai.360.com/open/models"),
            ("开发者文档", "https://ai.360.com/docs"),
        ],
    },
    "china_mobile_moma": {
        "category": "domestic",
        "display_name": "中国移动九天人工智能平台",
        "free_quota": "免费体验包政策**无法从官方公开页面核实**（九天门户为纯动态渲染页面），需登录九天平台控制台查看实际权益——宁缺毋假",
        "validity": "需登录控制台核实",
        "free_models": [
            "**需登录控制台核实**：平台在架模型清单无法从官方公开页确认（旧档案“九天·海云/九天·客服/MoMA”等名称无法从现行官方页证实；移动云 MoMA 产品页已 404 下线）",
        ],
        "preconditions": "注册中国移动/移动云账号并完成实名认证",
        "promotions": "面向行业开发者的赋能计划以官方公告为准。",
        "notes": "本条官方公开证据不足，宁缺毋假：额度与模型信息请以登录九天门户后的控制台内容为准。",
        "links": [
            ("九天人工智能平台门户", "https://jiutian.10086.cn/portal/"),
            ("九天帮助中心", "https://jiutian.10086.cn/portal/common-helpcenter"),
            ("移动云", "https://ecloud.10086.cn/"),
        ],
    },
    "unisound_shanhai": {
        "category": "domestic",
        "display_name": "云知声 Token Hub (MaaS)",
        "free_quota": "新人礼包即左栏按模型/服务发放的额度（官方快速入门文档），实名认证后自动到账、**无需审核**；有效期官方未标注，以账户内资源包为准",
        "validity": "以账户内资源包标注为准（官方文档未标注有效期）",
        "free_models": [
            "`Unisound U2`（通用）、`U2-Med`（医疗）、`U1-OCR` —— 实名认证即送**各 500 万 tokens**",
            "`U2-ASR`（语音识别）—— 赠送 **5 小时**；`U2-TTS`（语音合成）—— 赠送 **5 万字**",
            "另有 `U2-RadiMed`（放射医疗）等在架模型",
        ],
        "tier_caveats": [
            "额度**按模型/服务分散发放**，不是统一 token 池：U2 / U2-Med / U1-OCR 各 500 万、ASR 5 小时、TTS 5 万字，互不通兑",
            "有效期官方文档未标注，以账户内资源包为准",
        ],
        "preconditions": "注册并完成实名认证（无需企业审核）",
        "promotions": "平台聚焦语音与医疗场景，提供语音识别/合成与 OCR 全栈接口。",
        "notes": "开放平台已统一为 maas.unisound.com（Token Hub）。",
        "links": [
            ("快速入门（新人礼包说明）", "https://maas.unisound.com/docs/guide/quickstart"),
            ("平台文档总览", "https://maas.unisound.com/docs/guide/overview"),
            ("Token Hub 主页", "https://maas.unisound.com/"),
        ],
    },
    "dataeye": {
        "category": "domestic",
        "display_name": "数眼智能 (数言 AI / ShuyanAI)",
        "free_quota": "**注册即领 50 万免费 Tokens**（官方价格页 shuyanai.com/price 原文），用完即止；为非官方第三方中转，额度不属模型厂商承诺",
        "validity": "免费 tokens 用完即止（有效期以账户标注为准）",
        "free_models": [
            "聚合转发模型（价格页列出 `kimi-k3`、`deepseek-v4-pro`、`qwen3.8-max`、`glm-5.3-flash` 等，以站点实时列表为准）—— 共享新用户 **50 万免费 tokens**",
        ],
        "tier_caveats": [
            "**第三方聚合中转，不是模型厂商官方平台**：50 万 tokens 的额度与稳定性都不属厂商承诺，存在跑路 / 改版风险",
            "只建议放低敏测试流量，不要充大额余额；模型清单随上游调整",
        ],
        "preconditions": "手机号或微信注册",
        "promotions": "聚合 API 转发与按量计费；为非官方第三方中转，额度不属模型厂商承诺。",
        "notes": "与 dataeye.com（营销数据分析公司）无关，官方域名为 shuyanai.com。",
        "links": [
            ("价格页（50 万 tokens 说明）", "https://www.shuyanai.com/price"),
            ("官方主页", "https://www.shuyanai.com/"),
        ],
    },
    "mthreads_coding": {
        "category": "domestic",
        "display_name": "摩尔线程 MUSA Coding Plan",
        "free_quota": "Free Trial 即左栏 30 天免费试用（每日限量 100 名），无独立注册赠金",
        "validity": "试用期 **30 天**",
        "free_models": [
            "`GLM-4.7`（代码场景，运行于摩尔线程 MUSA GPU 集群）—— 官网 Free Trial 标注 **¥0 免费试用、有效期 30 天**，每日限量 **100 名**开发者；核对时页面按钮显示“体验爆满，扩容中”（可能暂时无法开通）",
        ],
        "preconditions": "手机号注册开发者账号，每日名额有限",
        "promotions": "基于摩尔线程夸娥（KUAE）集群与 MUSA 软件栈的国产 GPU 推理服务。",
        "notes": "能否开通以 code.mthreads.com 页面实时状态为准。",
        "links": [
            ("Coding Plan 官网", "https://code.mthreads.com/"),
        ],
    },
    "xiaomi_mimo": {
        "category": "domestic",
        "display_name": "小米 MiMo (Xiaomi MiMo 开放平台)",
        "openai_compat": {
            "summary": "TTS 系列限时免费；语言模型按量计费",
            "api_key_label": "控制台申请",
            "api_key_url": "https://platform.xiaomimimo.com/#/console/api-keys",
            "base_url": "https://api.xiaomimimo.com/v1",
            "models": "`mimo-v2.6-pro`, `mimo-v2.6-flash`, `mimo-v2.5-tts`",
        },
        "free_quota": "新用户注册可获**赠金（bonus credit）**（官方促销 FAQ 原文：“You can receive bonus credit through Refer & Earn or new user registration”），**有效期 40 天**、到期自动作废；只能抵扣按量计费 API 调用费、**不可抵扣 Token Plan 订阅**。具体金额随活动变动，以控制台账户页实际到账为准",
        "validity": "注册赠金 **40 天**有效（自到账日起、先到期先扣）；TTS 系列与缓存写入为「**限时免费**」，官方未公布截止日",
        "free_models": [
            "**语音合成 TTS 系列 —— 限时免费**：`mimo-v2.5-tts`、`mimo-v2.5-tts-voiceclone`（音色克隆）、`mimo-v2.5-tts-voicedesign`（音色设计）—— 官方定价页原文「限时免费」，且不消耗 Token Plan 套餐额度",
            "**缓存写入（Cache Write）—— 限时免费**（官方定价页原文）",
            "**语言模型与 ASR 均按量计费、无免费层**：`mimo-v2.6-pro` ¥0.025（缓存命中）/ ¥3.00 / ¥6.00 每百万 tokens；`mimo-v2.6-flash` ¥0.02 / ¥1.00 / ¥2.00；`mimo-v2.6-pro-ultraspeed` ¥0.25 / ¥30 / ¥60；`mimo-v2.5-asr` ¥0.5 / 小时",
            "**开源权重可自托管**：`MiMo-V2-Flash` 以 MIT 许可开源（GitHub / HuggingFace），支持 sglang 本地部署，不受 API 额度限制",
            "网页体验：Xiaomi MiMo Studio（`aistudio.xiaomimimo.com`）可直接对话体验，无需 API Key",
        ],
        "tier_caveats": [
            "**平台按量计费，语言模型没有免费层**：免费只覆盖 TTS 系列与缓存写入（均标注「限时」）；`mimo-v2.6-pro` 等主力模型按 token 计费，或改走 Token Plan 订阅（个人版 ¥39 / ¥99 / ¥329 / ¥659 每月）",
            "**「限时免费」官方未公布截止日**，随时可能转正式计费 —— 接入前先看定价页「TTS 系列」那行是否仍写「限时免费」",
            "**注册赠金 40 天过期**（先到期先扣、赠金优先于现金），只能抵按量计费 API 费用，**不能抵 Token Plan 订阅**，不可提现 / 转让 / 找零",
            "**限速**：`mimo-v2.6-pro` / `mimo-v2.6-flash` 均为 **100 RPM / 10M TPM**（单账号所有 API Key 合计）；`mimo-v2.6-pro-ultraspeed` 的限速需联系商务定制",
            "国内账号充值 / 购买套餐需**实名认证**；海外与国内按区域返回不同 Base URL 与 Key、**额度不互通**；`mimo-v2.5-pro` / `mimo-v2.5` 将于 **2026-10-21 10:00（北京时间）下线**",
        ],
        "preconditions": "小米账号登录（国内手机号或微信 / 微博 / QQ / 支付宝 / Apple ID 授权；海外邮箱或 Google / Facebook）；充值 / 购买套餐需实名认证",
        "promotions": "Refer & Earn 长期活动（官方 2026-08-13 更新）：好友经邀请码注册并完成首笔 **Token Plan** 付费订阅后，邀请人得实付金额 **10%** 返利（Standard / Pro 年付与 Max 订阅为 **20%**，无 30 单上限），好友首单 **9 折**；另有 MiMo Claw 限时特惠 ¥14.9 / 月。",
        "invite_reward": "官方 6 位邀请码：**填码双方各得 API 体验金**（国内 ¥10 / 海外 $2，注册后自动填入，40 天有效）+ 首单 **9 折**；邀请人在好友首笔付费订阅后额外得 **10% 返利**（年付 / Max 为 20%，上限 30 单，订单完成 3 天后到账）。返利只能抵 API 调用费、**不可抵 Token Plan**。",
        "notes": "API 兼容 OpenAI（`https://api.xiaomimimo.com/v1`）与 Anthropic（`https://api.xiaomimimo.com/anthropic`）两种协议；Token Plan 使用独立 Base URL 与 `tp-` 前缀 Key。",
        "links": [
            ("官方主页", "https://mimo.xiaomi.com/"),
            ("开放平台 / 控制台", "https://platform.xiaomimimo.com/"),
            ("模型与定价总览", "https://mimo.mi.com/"),
            ("按量计费定价（中文）", "https://mimo.mi.com/docs/zh-CN/price/pay-as-you-go"),
            ("Token Plan 订阅定价", "https://mimo.mi.com/docs/zh-CN/price/token-plan"),
            ("API 文档中心", "https://mimo.mi.com/docs/welcome"),
            ("开源权重 GitHub", "https://github.com/XiaomiMiMo"),
        ],
    },

    # ------------------ Part 2: 国际主流大模型与高速推理平台 (25) ------------------
    "google_gemini": {
        "category": "international",
        "display_name": "Google Gemini (Google AI Studio)",
        "openai_compat": {
            "summary": "免费层每日滚动重置（免绑卡）",
            "api_key_label": "AI Studio 申请",
            "api_key_url": "https://aistudio.google.com/apikey",
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
            "models": "`gemini-2.5-flash`, `gemini-3.8-flash`",
        },
        "free_quota": "**AI Studio 免费层（Free Tier）长期存在**（官方计费文档原文 “New accounts begin on the Free Tier”），仅需 Google 账号、免绑信用卡；注意：**2026 年 3 月起 $300 Google Cloud 试用金不能用于支付 Gemini API / AI Studio 费用**；付费层需关联结算账户并预付最低 **$5**",
        "validity": "免费层按速率限额滚动（RPD 太平洋时间午夜重置）",
        "free_models": [
            "`Gemini 3.8 / 3.7 / 3.6 Flash`、Gemini 3.5 Flash/Flash-Lite、Gemini 3.1 Flash-Lite、Gemini 3 Flash Preview、`Gemini 2.5 Pro/Flash/Flash-Lite`、`Gemma 4`、Gemini Embedding 系列 —— **免费层可用**，按速率限额滚动（RPD 太平洋时间午夜重置；官方文档已不再公开各模型具体免费层数字，以 AI Studio 内 Rate Limit 页为准）",
            "`Gemini 3.1 Pro Preview` 与 Nano Banana 图像系列 —— **无免费层**",
        ],
        "tier_caveats": [
            "**不是所有模型都有免费层**：3.x Flash / Gemma 4 / Embedding 系列可用；`Gemini 3.1 Pro Preview`、Nano Banana 图像系列**无免费层**，调错模型会直接付费",
            "**隐私代价**：免费层输入/输出数据可能被用于改进 Google 产品；敏感数据不要走免费层",
            "免费层限速官方已不再公开固定数值，以 AI Studio 内 Rate Limit 页为准；RPD 按太平洋时间午夜重置",
            "$300 Google Cloud 试用金**不能**用于 Gemini API / AI Studio（2026 年 3 月起）；付费层需关联结算账户并预付最低 $5",
        ],
        "preconditions": "仅需 Google 账号即可生成 API Key，免绑信用卡；免费层数据可能用于产品改进",
        "promotions": "付费层预付 $5 起；与 Google Cloud Vertex AI 深度集成。",
        "notes": "注意：**2026 年 3 月起，$300 Google Cloud 试用金不能用于支付 Gemini API / AI Studio 费用**（官方 billing 文档原文）；旧“Gemini 1.5 Flash/Pro、Gemma 2、15 RPM/1500 RPD”等型号与数字均已换代或下架。",
        "links": [
            ("API Key 申请直达 (AI Studio)", "https://aistudio.google.com/apikey"),
            ("OpenAI 兼容端点快速入门", "https://ai.google.dev/gemini-api/docs/openai"),
            ("AI Studio 官网", "https://ai.google.dev/"),
            ("API 定价文档", "https://ai.google.dev/gemini-api/docs/pricing"),
            ("计费与免费层说明", "https://ai.google.dev/gemini-api/docs/billing"),
            ("速率限制说明", "https://ai.google.dev/gemini-api/docs/rate-limits"),
        ],
    },
    "groq": {
        "category": "international",
        "display_name": "Groq Cloud (LPU 推理)",
        "openai_compat": {
            "summary": "30 RPM / 1,000 RPD 高速推理（免绑卡）",
            "api_key_label": "控制台申请",
            "api_key_url": "https://console.groq.com/keys",
            "base_url": "https://api.groq.com/openai/v1",
            "models": "`openai/gpt-oss-120b`, `qwen/qwen3.6-27b`",
        },
        "free_quota": "**Free Plan 免费层长期存在**（官方速率文档），邮箱注册即得 API Key、免信用卡；更高限额 / Batch / Flex 需升级付费 Developer plan",
        "validity": "限额按分钟与按天滚动重置",
        "free_models": [
            "`openai/gpt-oss-120b`、`gpt-oss-20b` —— 免费层 **30 RPM / 1,000 RPD / 8K TPM**",
            "`qwen/qwen3.6-27b`、`qwen3.8-27b`（Preview）、`meta-llama/llama-prompt-guard-2`、`groq/compound`(-mini)、`whisper-large-v3`(-turbo)、Orpheus TTS —— 免费层可用（各模型限额见官方速率文档，按组织级计量，缓存命中 token 不计入限速）",
            "旧 Llama-3.1-8b / Llama-3.3-70b 已转 Enterprise 付费（旧“30 RPM / 14,400 RPD / 6,000 TPM 统一限额”说法已过时）",
        ],
        "tier_caveats": [
            "免费层只覆盖 gpt-oss / Qwen / 部分工具模型（gpt-oss 为 30 RPM / 1,000 RPD / 8K TPM，组织级计量）；**旧 Llama-3.1-8b、Llama-3.3-70b 已转 Enterprise 付费**，按旧清单调用会扣费",
            "Batch、Flex、更高限额需付费 Developer plan；缓存命中的 token 不计入限速",
        ],
        "preconditions": "邮箱注册即可获取 API Key，免信用卡",
        "promotions": "Developer plan 按 token 计费（gpt-oss-120b $0.15/$0.60 每百万）；自研 LPU 硬件推理速度快。",
        "notes": "旧“30 RPM / 14,400 RPD / 6,000 TPM 统一限额”及 Mixtral-8x7B、Gemma-2-9B 模型均已过时/下架。",
        "links": [
            ("API Key 控制台直达", "https://console.groq.com/keys"),
            ("快速开始文档", "https://console.groq.com/docs/quickstart"),
            ("官方主页", "https://groq.com/"),
            ("速率限制文档", "https://console.groq.com/docs/rate-limits"),
            ("模型清单", "https://console.groq.com/docs/models"),
            ("定价说明", "https://groq.com/pricing/"),
        ],
    },
    "cloudflare_workers_ai": {
        "category": "international",
        "display_name": "Cloudflare Workers AI",
        "free_quota": "注册 Cloudflare 账号即可使用、免绑卡；超额后开通 Workers Paid 按 **$0.011 / 1,000 Neurons** 计费（官方定价页原文）",
        "validity": "**每日 UTC 0 点重置**",
        "free_models": [
            "全目录 **86 个模型**共享免费额度：代表 `@cf/meta/llama-4-scout-17b`、`llama-3.3-70b-fp8`、`@cf/openai/gpt-oss-120b/20b`、`deepseek-v4-flash-0731/v4-pro-0813`、`gemma-4-26b`、`glm-5.3(-flash)`、`kimi-k2.6`、`nemotron-3-120b`、`qwen3-30b`、`bge-m3` —— **每日 10,000 Neurons 免费**（官方定价页原文 “10,000 Neurons per day at no charge”），UTC 0 点刷新；旧 llama-3.1-8b、mistral-7b 已弃用",
        ],
        "tier_caveats": [
            "86 个模型**共享每日 10,000 Neurons** 总额度（不是每模型各 1 万），按太平洋时间午夜重置；超额按 $0.011 / 1,000 Neurons 计费，需开 Workers Paid",
            "免费层主要面向 Workers 平台内调用；Neurons 换算随模型不同",
        ],
        "preconditions": "注册 Cloudflare 账号即可使用，免绑卡",
        "promotions": "与 Cloudflare Workers、Vectorize 向量库、AI Gateway 边缘集成。",
        "notes": "超额后开通 Workers Paid 按 **$0.011 / 1,000 Neurons** 计费（官方定价页原文）。",
        "links": [
            ("Workers AI 文档", "https://developers.cloudflare.com/workers-ai/"),
            ("模型目录", "https://developers.cloudflare.com/workers-ai/models/"),
            ("定价说明", "https://developers.cloudflare.com/workers-ai/platform/pricing/"),
            ("配额与限制", "https://developers.cloudflare.com/workers-ai/platform/limits/"),
        ],
    },
    "openrouter": {
        "category": "international",
        "display_name": "OpenRouter (模型统一网关)",
        "openai_compat": {
            "summary": "20 RPM 免费层（免绑卡）",
            "api_key_label": "控制台申请",
            "api_key_url": "https://openrouter.ai/keys",
            "base_url": "https://openrouter.ai/api/v1",
            "models": "选带 `:free` 后缀模型（如 `google/gemma-4-31b-it:free`、`nvidia/nemotron-3-super-120b:free`）",
        },
        "free_quota": "免费模型**无需充值**即可调用，邮箱或 GitHub 登录创建 API Key、免信用卡；购满 10 credits 可将免费模型日限从 50 次提升至 1,000 次",
        "validity": "免费政策长期有效",
        "free_models": [
            "**`:free` 后缀模型**（实时目录约 16 个）—— **限速 20 RPM**；每日请求上限 **50 次**（累计购买不足 10 credits）或 **1,000 次**（购满 10 credits），官方 limits 文档常量 FREE_MODEL_RATE_LIMIT_RPM=20 / FREE_MODEL_NO_CREDITS_RPD=50 / FREE_MODEL_HAS_CREDITS_RPD=1000",
            "当前 :free 实例：`google/gemma-4-31b-it:free`、`gemma-4-26b-a4b-it:free`、`nvidia/nemotron-3-super-120b:free`、`nemotron-3-ultra-550b:free`、`thinkingmachines/inkling:free`(-small)、`cohere/north-mini-code:free`、`poolside/laguna-s-2.1:free`、`liquid/lfm-2.5-2.6b:free` 等；旧 llama-3.3-70b / gemini-2.0-flash-exp / deepseek-r1 / qwen-2.5-72b :free ID 均已下架",
        ],
        "tier_caveats": [
            "**只有带 `:free` 后缀的模型免费**，同名付费模型照常扣费；免费实例约 16 个且随上游厂商变动（旧 llama-3.3-70b / gemma-2 / deepseek-r1 等 :free ID 已下架）",
            "限速 20 RPM；每日 50 次（累计充值不足 $10）或 1,000 次（购满 $10 credits 后）",
        ],
        "preconditions": "邮箱或 GitHub 登录创建 API Key，免信用卡",
        "promotions": "一个 API Key 统一切换全球多家模型厂商；购满 10 credits 可将免费模型日限提升至 1,000 次。",
        "notes": "旧举的 llama-3.3-70b / gemini-2.0-flash-exp / deepseek-r1 / qwen-2.5-72b :free ID 均已下架。",
        "links": [
            ("API Key 申请直达", "https://openrouter.ai/keys"),
            ("官方主页", "https://openrouter.ai/"),
            ("速率限制文档", "https://openrouter.ai/docs/api_reference/limits"),
            ("免费模型列表", "https://openrouter.ai/models?max_price=0"),
        ],
    },
    "cerebras": {
        "category": "international",
        "display_name": "Cerebras Inference (晶圆级推理)",
        "free_quota": "**Free Trial 赠金制**：注册后得 **$5 免费额度**（添加验证付款方式后发放），**30 天有效**（官方定价页 “Get started with $5 in free credits”）",
        "validity": "**30 天**",
        "free_models": [
            "公共端点当前仅 **`gpt-oss-120b`**（约 3000 tok/s）与 **`qwen-3.8-27b`** —— 免费层限额 **5 RPM / 30K uncached TPM（90K total）/ 1M Tokens 每天**",
            "Llama 模型已不在公共目录（旧“永久免费 Developer Tier / 30 RPM / 60K TPM”说法均已过时）；Developer (PAYG) 层 gpt-oss-120b 1K RPM / 1M TPM",
        ],
        "preconditions": "注册账号；$5 赠金需添加验证付款方式",
        "promotions": "Developer (PAYG) 层 gpt-oss-120b 1K RPM / 1M TPM，无小时与每日限制。",
        "notes": "旧“永久免费 Developer Tier / 30 RPM / 60K TPM / Llama 3.1/3.3”均已过时；Llama 模型已不在公共目录。",
        "links": [
            ("官方主页", "https://www.cerebras.ai/"),
            ("速率限制文档", "https://inference-docs.cerebras.ai/support/rate-limits"),
            ("模型清单", "https://inference-docs.cerebras.ai/models/overview"),
            ("定价中心", "https://www.cerebras.ai/pricing"),
        ],
    },
    "cohere": {
        "category": "international",
        "display_name": "Cohere",
        "free_quota": "**Trial Key 免费**：官方定价页原文 “API calls made from a Trial API key are free”，邮箱注册、免信用卡；但**禁止用于生产或商业用途**（“not permitted to be used for production or commercial purposes”），生产 key 按量计费",
        "validity": "每月 1 日重置 1,000 次",
        "free_models": [
            "`Command A+`、Command A Reasoning/Translate/Vision、Command A、Command R/R+、Command R7B、North Mini Code —— Trial Key **每月 1,000 次调用免费**，Trial 速率 Chat **20 RPM**",
            "`Embed 4` Small/Medium —— Trial 速率 **2,000 inputs/min**；`Rerank 3.5`/`Rerank 4` Fast/Pro —— Trial 速率 **10 RPM**（旧“40 RPM”说法有误，裸 Embed/Rerank 已换代）",
        ],
        "tier_caveats": [
            "**Trial Key 明令禁止生产 / 商业用途**（官方原文 “not permitted to be used for production or commercial purposes”）；商用必须升级按量付费 key",
            "每月 1,000 次调用；Chat 限速 20 RPM、Embed 2,000 inputs/min、Rerank 10 RPM",
        ],
        "preconditions": "邮箱注册即可，免信用卡；Trial Key 仅限非商用开发测试",
        "promotions": "Trial 速率：Chat **20 RPM**、Embed 2,000 inputs/min、Rerank 10 RPM；生产 key 按量计费。",
        "notes": "旧“40 RPM”说法有误（Chat 实为 20 RPM）；裸 “Embed/Rerank” 已换代为 Embed 4 / Rerank 3.5–4。",
        "links": [
            ("API Key 控制台直达", "https://dashboard.cohere.com/api-keys"),
            ("官方主页", "https://cohere.com/"),
            ("定价页", "https://cohere.com/pricing"),
            ("速率限制文档", "https://docs.cohere.com/docs/rate-limits"),
        ],
    },
    "mistral": {
        "category": "international",
        "display_name": "Mistral AI",
        "free_quota": "**无新用户赠金 / 免费实验层**（现行 API 定价页未提及；旧“€5 赠金 / 1 RPS 免费层”无据）；Le Chat 套餐含 $10/月 API credits 属订阅权益",
        "validity": "以官方定价页为准",
        "free_models": [
            "**`Leanstral`**（Labs，`labs-leanstral-2603`，限时开放收集反馈）—— 免费端点",
            "**Mistral Moderation 2（Free）** —— 免费端点",
            "商业模型均付费：Mistral Medium 3.5、`Large 3`（$0.50/$1.50 每百万）、`Small 4`（$0.15/$0.60）、Ministral 3（3B/8B/14B）、Codestral v25.08、Voxtral 语音、OCR 4.1、Mistral Embed、Shieldstral 1.0、第三方 GLM 5.2；旧 open-mistral-7b / Mixtral / Pixtral-12B 已列入 deprecated/retired",
        ],
        "tier_caveats": [
            "免费的是**端点**而非额度：官方定价页未提供新用户赠金或免费实验层（旧“€5 赠金 / 1 RPS 免费层”无据）",
            "`Leanstral` 属 Labs「限时开放收集反馈」，**随时可能下线**；`Mistral Moderation 2（Free）` 是常设免费端点",
            "商业模型（Mistral Medium 3.5、Large 3、Small 4、Ministral 3、Codestral、Voxtral、OCR、Mistral Embed、Shieldstral）均按量付费",
            "免费端点限速数值官方未公开，以控制台为准",
        ],
        "preconditions": "邮箱注册并验证手机号",
        "promotions": "开放权重模型可下载；提供企业私有化部署；2026-09 宣布完成 €3B 融资。",
        "notes": "旧“€5 赠金 / 1 RPS 免费层 / open-mistral-7b / Mixtral / Pixtral-12B”在现行官方页面无据或已列入 deprecated/retired 表。",
        "links": [
            ("API Key 控制台直达", "https://console.mistral.ai/api-keys/"),
            ("官方主页", "https://mistral.ai/"),
            ("API 定价", "https://mistral.ai/pricing/api/"),
            ("模型文档", "https://docs.mistral.ai/getting-started/models/"),
            ("新闻动态", "https://mistral.ai/news/"),
        ],
    },
    "meta_llama": {
        "category": "international",
        "display_name": "Meta Llama (开源权重)",
        "free_quota": "权重本身**免费免版税**（自托管零授权费）；许可限制：上自然月活跃用户超过 **7 亿（700 million MAU）** 的实体需另行向 Meta 申请授权",
        "validity": "永久有效（遵守许可条款）",
        "free_models": [
            "**`Llama 4 Scout`**（17B 激活/109B 总参，10M 上下文）与 **`Llama 4 Maverick`**（17B 激活/400B 总参，原生多模态，2025-04-05 发布）—— **开源权重免版税授权**（Llama 4 Community License 原文 “royalty-free”），可自行部署或经 Groq/Cerebras/Cloudflare/Together/DeepInfra 等托管平台免费/低价调用；Llama 3.x 系列仍可用",
        ],
        "preconditions": "遵守 Llama 4 社区许可；上自然月活跃用户超过 **7 亿（700 million MAU）** 的实体需另行向 Meta 申请授权",
        "promotions": "主流推理平台（Groq、Cerebras、Cloudflare、Together、DeepInfra 等）均托管 Llama 4。",
        "notes": "官方主站已迁至 developer.meta.com/ai；llama.com 301 跳转至此；Llama 4 许可页为 /ai/llama4/license/。",
        "links": [
            ("Meta AI 开发者站", "https://developer.meta.com/ai/"),
            ("Llama 4 许可协议", "https://developer.meta.com/ai/llama4/license/"),
            ("Hugging Face 组织", "https://huggingface.co/meta-llama"),
        ],
    },
    "together_ai": {
        "category": "international",
        "display_name": "Together AI",
        "free_quota": "**无免费试用 / 无赠送**：官方计费文档原文 “Together AI does not currently offer free trials. Access to the Together platform requires a minimum $5 credit purchase.”——$5 是最低充值额而非赠送；预付余额无过期时间（官方原文 “credits … do not currently have an expiration date”）",
        "validity": "预付余额不过期；无免费额度",
        "free_models": [
            "**无免费模型层**，serverless 代表模型 Kimi K3、DeepSeek V4 Pro 0813 / V4 Flash 0731、GLM-5.2、MiniMax M3、Qwen3.8 2.4T A95B、GPT OSS 120B，图像 GPT Image 2、Nano Banana 2、FLUX.2 均需充值后按量调用",
        ],
        "preconditions": "注册账号并至少充值 $5",
        "promotions": "Serverless 按量计费 + 专用 GPU 集群；支持 OpenAI SDK 兼容调用。",
        "notes": "旧“注册送 $5（3 个月）”说法与官方计费文档矛盾。",
        "links": [
            ("API Key 设置直达", "https://api.together.ai/settings/api-keys"),
            ("官方主页", "https://www.together.ai/"),
            ("计费文档", "https://docs.together.ai/docs/billing-credits"),
            ("定价页面", "https://www.together.ai/pricing"),
        ],
    },
    "fireworks_ai": {
        "category": "international",
        "display_name": "Fireworks AI",
        "free_quota": "新账号送 **$1 免费额度**（官方定价页原文 “Get started with $1 in free credits.”），邮箱注册自助开通，用完即止",
        "validity": "用完即止",
        "free_models": [
            "serverless 模型可用 $1 赠金抵扣：`Kimi K3`（$3/$15）、Kimi K2.7 Code、`DeepSeek V4 Pro 0813`（$1.32/$3.96）、`DeepSeek V4 Flash 0731`（$0.22/$0.66）、Qwen 3.8 Max / 3.7 Plus 等",
        ],
        "tier_caveats": [
            "**$1 额度极小**，只够几十次测试调用，用完即止、不重置",
            "现行 serverless 价目已无 Llama 聊天模型单列（未列名模型按尺寸档位计费）",
        ],
        "preconditions": "邮箱注册即可自助开通（self-serve）",
        "promotions": "Batch 5 折；支持 Function Calling 与 JSON Schema 结构化输出。",
        "notes": "现行 serverless 价目表中已无 Llama 聊天模型单列（未列名模型按尺寸档位计费）。",
        "links": [
            ("API Key 控制台直达", "https://fireworks.ai/api-keys"),
            ("官方主页", "https://fireworks.ai/"),
            ("定价说明", "https://fireworks.ai/pricing"),
            ("Serverless 计费文档", "https://docs.fireworks.ai/serverless/pricing"),
        ],
    },
    "deepinfra": {
        "category": "international",
        "display_name": "DeepInfra",
        "free_quota": "**无注册赠送额度**：官方定价页与文档均未标注（官方原文 “You have to add a card or pre-pay or you won't be able to use our services.”）；DeepStart 初创扶持为申请制、金额未公开",
        "validity": "以官方定价页为准",
        "free_models": [
            "**无免费模型层**，代表模型 DeepSeek-V4-Pro（$1.30/$2.60）、DeepSeek-V4-Flash（$0.06/$0.18）、DeepSeek-R1-0528、Qwen3-Max、Qwen3-Coder-480B、Llama-4-Maverick/Scout、Llama-3.3-70B-Turbo、语音 Voxtral 系列均需绑卡或预付后调用",
        ],
        "preconditions": "支持 GitHub/Google/邮箱/SSO 登录（登录免卡，实际调用需加卡或预付）",
        "promotions": "Batch 8 折；DeepStart 初创项目需提交公司/融资信息申请，金额未公开。",
        "notes": "旧“注册送 $1.80”说法在现行官方页面无据；接口兼容 OpenAI。",
        "links": [
            ("API Key 控制台直达", "https://deepinfra.com/dash/api_keys"),
            ("官方主页", "https://deepinfra.com/"),
            ("模型价格表", "https://deepinfra.com/pricing"),
            ("开发者文档", "https://docs.deepinfra.com/"),
        ],
    },
    "huggingface": {
        "category": "international",
        "display_name": "Hugging Face (Inference Providers)",
        "free_quota": "Inference Providers 免费用户**每月 $0.10** 额度（官方定价文档原文，标注 “subject to change”），注册生成 Access Token 即可、免信用卡；PRO 会员 **$9/月**含每月 **$2** 通用推理额度",
        "validity": "免费额度**按月发放**",
        "free_models": [
            "经 18 家 provider（Cerebras/Together/Fireworks/Groq/Novita 等）路由的开源模型：`openai/gpt-oss-120b`、`deepseek-ai/DeepSeek-V3/R1`、`FLUX.1-dev` 等 —— 共享免费用户 **$0.10/月** 额度（原 Serverless 社区集群免费层已调整为 hf-inference provider，2025 年 7 月起主要提供 CPU 推理）",
        ],
        "tier_caveats": [
            "免费用户每月仅 **$0.10** 推理额度（官方标注 “subject to change”），只够极低频测试，不是长期主力额度",
            "原 Serverless 社区免费集群 2025 年 7 月起已改为 hf-inference provider 且主要提供 CPU 推理；PRO $9/月也只含 $2 额度",
        ],
        "preconditions": "注册 Hugging Face 账号并生成 Access Token，免信用卡",
        "promotions": "PRO 会员 **$9/月**，含每月 **$2** 通用推理额度（免费额度的 20 倍）。",
        "notes": "高并发生产场景建议使用 Dedicated Endpoints。",
        "links": [
            ("官方主页", "https://huggingface.co/"),
            ("Inference Providers 定价", "https://huggingface.co/docs/inference-providers/pricing"),
            ("会员定价", "https://huggingface.co/pricing"),
        ],
    },
    "nvidia_nim": {
        "category": "international",
        "display_name": "NVIDIA NIM (API Catalog)",
        "free_quota": "免费层长期有效（官网宣传 **“Free inference with leading models”**），注册 NVIDIA 开发者账号即可；受 NVIDIA API Trial Terms 约束，超出促销条款后按标准价计费",
        "validity": "免费层长期有效（以官方试用条款为准）",
        "free_models": [
            "API 目录代表模型 `nvidia/nemotron-3-ultra-550b-a55b`、`nemotron-3.5-lightning-30b`、`nemotron-3-super-120b`、`deepseek-v4-pro/flash`、`kimi-k3`、`gpt-oss-120b/20b`、`glm-5.2`、`llama-3.3-70b` —— 免费层官方页面原文**“多数模型限速 40 RPM、不按 token 计费”**",
            "旧 nemotron-4-340b、llama-3.1-405b 已不在现行目录；“1,000 credits / 90 天”等旧数字查不到",
        ],
        "tier_caveats": [
            "多数模型限速约 **40 RPM、不按 token 计费**；仅供**开发评估**，官方 Trial Terms 不允许生产环境使用",
            "模型目录变动频繁（旧 nemotron-4-340b、llama-3.1-405b 已撤出）；生产用量需走各模型厂商或 NIM 自建",
        ],
        "preconditions": "注册 NVIDIA 开发者账号",
        "promotions": "支持一键导出 NIM Docker 容器镜像本地部署；企业试用另见官方条款。",
        "notes": "“1,000 credits / 90 天”等旧数字在现行公开页面查不到；免费层 40 RPM 为官网当前公示；旧 nemotron-4-340b、llama-3.1-405b 已不在现行目录。",
        "links": [
            ("体验中心", "https://build.nvidia.com/"),
            ("API 模型目录", "https://docs.api.nvidia.com/nim/reference/llm-apis"),
            ("开发者条款", "https://developer.nvidia.com/legal/terms"),
        ],
    },
    "openai": {
        "category": "international",
        "display_name": "OpenAI",
        "free_quota": "**API 无公开固定赠送额度**：官方快速开始文档仅提供一次免费测试请求（原文 “Congrats on running a free test API request!”），随后引导充值（“Add credits to keep building”）；旧“$5 测试积分”在现行文档已不再出现。网页端 ChatGPT 提供免费版（可用模型以官方说明为准）",
        "validity": "免费测试请求为注册后一次性体验；额度政策以官方定价页为准",
        "free_models": [
            "**API 无免费模型层**，当前代际均按量付费：旗舰 `GPT-6 Astra`（$10/$50 每百万 token）、`GPT-5.6 Sol/Terra/Luna`；最低价 `gpt-5-nano`（$0.05/$0.40）；`text-embedding-3-small` 仍在售",
        ],
        "preconditions": "注册 OpenAI 账号并绑定海外付款方式；按组织层级划分 RPM / TPM 配额",
        "promotions": "Batch 批量推理约 5 折；提示缓存输入约 1–2.5 折；网页端 ChatGPT 提供免费版（可用模型以官方说明为准）。",
        "notes": "旧“$5 测试积分”说法在现行官方文档中已不再出现；“数据共享折扣”亦未见公开表述。",
        "links": [
            ("官方主页", "https://openai.com/"),
            ("API 定价", "https://developers.openai.com/api/docs/pricing"),
            ("模型列表", "https://developers.openai.com/api/docs/models"),
            ("快速开始", "https://developers.openai.com/api/docs/quickstart"),
        ],
    },
    "anthropic": {
        "category": "international",
        "display_name": "Anthropic Claude",
        "free_quota": "API 新用户有**少量免费测试额度**（官方定价 FAQ 原文：“New users receive a small amount of free credits to test the API”，未公开金额，以账户到账为准）；网页端 Claude 免费版注册即可用，Pro 订阅 $20/月（年付 $17）含 Claude Code",
        "validity": "网页免费版额度每 5 小时滚动重置；API 测试额度以账户到账为准",
        "free_models": [
            "**API 无免费模型层**：当前代际 `Claude Fable 5.1`（`claude-fable-5-1`）、`Claude Opus 5`（`claude-opus-5`）、`Claude Sonnet 5`（`claude-sonnet-5`）、`Claude Haiku 4.5`（`claude-haiku-4-5`，上下文 200K–1M）均按量付费，新用户少量测试 credits 可抵扣",
            "网页端 Claude 免费版（Free plan）—— 额度按 **5 小时滚动窗口**重置，但**不含 Claude Code**（官方原文 “Claude Code is included in all paid plans”）",
        ],
        "preconditions": "网页端注册账号即可；API 需绑定付款方式；**免费版不含 Claude Code**（官方原文 “Claude Code is included in all paid plans”）",
        "promotions": "Pro 订阅 $20/月（年付 $17/月）含 Claude Code；Max 从 $100/月起；Batch 5 折、提示缓存读低至 0.1x。",
        "notes": "官方建议多数工作负载从 Opus 5 起步，Fable 5.1 面向复杂推理与长程智能体任务。",
        "links": [
            ("官方主页", "https://claude.com/"),
            ("定价中心", "https://claude.com/pricing"),
            ("模型文档", "https://platform.claude.com/docs/en/models/overview"),
            ("API 定价 FAQ", "https://platform.claude.com/docs/en/about-claude/pricing"),
        ],
    },
    "xai_grok": {
        "category": "international",
        "display_name": "xAI Grok",
        "free_quota": "**API 无免费额度**：官方文档与定价页均未标注，快速开始要求注册后自行充值（原文 “load it with credits to start using the API”）；旧“$25 免费额度/30 天”说法无据。X Premium+ 订阅含网页端 Grok 对话",
        "validity": "以官方控制台活动为准",
        "free_models": [
            "**API 无免费模型层**：`grok-4.6`（编码模型 Grok Build）、grok-4.5、grok-4.3、grok-4.20 系列（reasoning / non-reasoning / multi-agent，上下文最高 1M）均需充值；旧 `grok-2`/`grok-beta` 已退役",
        ],
        "preconditions": "注册 xAI 控制台并充值；X Premium+ 订阅含网页端 Grok 对话",
        "promotions": "部分模型 Batch 8 折；Priority Processing 2x；Grok Build 提供 API 与 CLI 智能体编码。",
        "notes": "旧“$25 免费额度/30 天”说法在现行官方页面无据。",
        "links": [
            ("官方主页", "https://x.ai/"),
            ("API 定价", "https://docs.x.ai/developers/pricing"),
            ("快速开始", "https://docs.x.ai/developers/quickstart"),
            ("开发者控制台", "https://console.x.ai/"),
        ],
    },
    "nebius": {
        "category": "international",
        "display_name": "Nebius (Token Factory / AI Cloud)",
        "free_quota": "**无自动赠送额度**：绑卡时扣款 **$25 并转为账户余额**（最低首付，**非赠送**；官方注册文档原文）；免费额度仅通过不定期 **promo code** 活动发放（官方原文 “You can receive a promo code from Nebius as part of a special offer”）",
        "validity": "promo code 有效期以活动规则为准",
        "free_models": [
            "**无免费模型层**：Nebius Token Factory（原 AI Studio，studio.nebius.ai 已 301 跳转 tokenfactory.nebius.com）模型目录以后台为准，需账户余额；GPU 云 B300 $7.85/h、B200 $7.15/h、H200 $4.55/h 等",
        ],
        "preconditions": "注册 Nebius 账户并绑卡（$25 扣款转余额）",
        "promotions": "Startup program / Research grants 可申请（无公开金额）。",
        "notes": "旧“注册送 $25 启动金”系对绑卡扣款转余额的误读。",
        "links": [
            ("官方主页", "https://nebius.com/"),
            ("价格说明", "https://nebius.com/prices"),
            ("Promo code 文档", "https://docs.nebius.com/signup-billing/payments/promo-codes"),
            ("Token Factory", "https://tokenfactory.nebius.com/"),
        ],
    },
    "ai21_labs": {
        "category": "international",
        "display_name": "AI21 Labs",
        "free_quota": "免费试用 **$10 credits**，邮箱注册即得 API Key、**免信用卡**（官方定价页）",
        "validity": "**7 天**",
        "free_models": [
            "`Jamba Large 1.7`（`jamba-large-1.7-2025-07`）、`Jamba Mini 2`（`jamba-mini-2-2026-01`）—— 试用 **$10 credits、7 天有效**；Jamba 1.5/1.6 已弃用（旧“$10 / 3 个月”说法过时）",
        ],
        "tier_caveats": [
            "**$10 credits 仅 7 天有效**（旧「3 个月」说法已过时），到期清零",
            "Jamba 1.5 / 1.6 已弃用，免费试用对应现行 Jamba Large 1.7 / Mini 2",
        ],
        "preconditions": "邮箱注册即可获取 API Key，免信用卡",
        "promotions": "企业产品为 Maestro（原 Contextual Answers 已下线）；Jamba SSM-Transformer 混合架构长上下文显存开销较低。",
        "notes": "旧“$10 / 3 个月”及 Jamba 1.5、Contextual Answers 说法均已过时。",
        "links": [
            ("官方主页", "https://www.ai21.com/"),
            ("定价页面", "https://www.ai21.com/pricing/"),
            ("模型文档", "https://docs.ai21.com/docs/jamba-foundation-models"),
        ],
    },
    "jina_ai": {
        "category": "international",
        "display_name": "Jina AI (Reader / Embeddings / Reranker)",
        "free_quota": "每个新 API Key 含 **10M tokens 免费额度**（官方产品页），GitHub 账号登录获取、免信用卡；免费速率限制长期有效",
        "validity": "免费速率限制长期有效",
        "free_models": [
            "**Reader API**（r.jina.ai 网页转 Markdown）—— 免 key **20 RPM**、免费 key **500 RPM**",
            "`jina-embeddings-v5`（v4 免费但限非商用）、`jina-reranker-v3.5` —— 免费层 **100 RPM / 100K TPM**，共享新 Key **10M tokens** 免费额度",
        ],
        "tier_caveats": [
            "Embeddings / Reranker 免费层 100 RPM / 100K TPM，共享每 Key **10M tokens** 总额度；Reader 免 key 仅 20 RPM、免费 key 500 RPM",
            "部分模型（如 v4 embeddings）免费层**仅限非商用**；超限按量计费",
        ],
        "preconditions": "GitHub 账号登录获取 API Key，免绑定信用卡",
        "promotions": "Reader 加 r.jina.ai 前缀即可提取任意网页清洁文本/Markdown。",
        "notes": "旧“100 万 tokens”说法已过时（现为 10M）；v3/v2 模型已被 v5/v3.5 取代。",
        "links": [
            ("官方主页", "https://jina.ai/"),
            ("Reader", "https://jina.ai/reader/"),
            ("Embeddings", "https://jina.ai/embeddings/"),
            ("Reranker", "https://jina.ai/reranker/"),
        ],
    },
    "stability_ai": {
        "category": "international",
        "display_name": "Stability AI",
        "free_quota": "新账号赠送 **25 积分**（官方 API 定价页原文：**“Get started with 25 free credits”**，可在账户页查看余额，用完即止）；开源权重自托管为零成本长期路径",
        "validity": "赠送积分用完即止（以账户页显示为准）",
        "free_models": [
            "`Stable Diffusion 3.5 Large/Turbo/Medium` 及 Stable Image 系列（API）—— 调用可使用新账号 **25 免费积分**抵扣",
            "**开源模型权重免费下载**：Community License 下年营收低于 **100 万美元** 的组织/个人可免费使用（含商用），超过需申请企业授权",
        ],
        "tier_caveats": [
            "25 积分按图像生成次数消耗，通常只够少量出图，用完即止、不重置",
            "真正长期免费的路径是**开源权重自托管**：Community License 仅限年营收 < 100 万美元的组织/个人（含商用），超过需企业授权",
        ],
        "preconditions": "API 需注册平台账号；开源权重自行下载部署",
        "promotions": "**Stability AI Community License**：年营收低于 **100 万美元** 的组织/个人可免费使用（含商用），超过需申请企业授权。",
        "notes": "图像/视频生成模型厂商；25 积分为注册赠送，开源部署为零成本长期路径。",
        "links": [
            ("API 定价（25 free credits 说明）", "https://platform.stability.ai/pricing"),
            ("社区许可协议", "https://stability.ai/license"),
            ("Stable Image 模型页", "https://stability.ai/stable-image"),
        ],
    },
    "morph_labs": {
        "category": "international",
        "display_name": "Morph Labs",
        "free_quota": "免费层 **每月 200 次请求** + WarpGrep/Glance 等工具附带 **每月 $10 算力额度**（官方定价页），邮箱注册取 Key，按月重置",
        "validity": "免费层**按月重置**",
        "free_models": [
            "OpenAI 兼容端点（api.morphllm.com/v1）：`morph-v3-fast`、`morph-v3-large` 及托管 Qwen 3.5 397B、MiniMax M2.7、DeepSeek V4 Flash 等 —— 免费层 **每月 200 次请求**",
            "WarpGrep/Glance 等工具 —— 附带 **每月 $10 算力额度**",
        ],
        "tier_caveats": [
            "免费层 **每月仅 200 次请求**（按月重置），批量 / 高频使用不够；另有随 WarpGrep / Glance 等工具附带的 $10/月算力额度，不开工具拿不到",
        ],
        "preconditions": "邮箱注册获取 API Key",
        "promotions": "面向 AI 编程与智能体场景优化推理延迟；兼容 OpenAI SDK。",
        "notes": "免费额度适合个人开发与轻量调用。",
        "links": [
            ("定价页（免费层说明）", "https://morphllm.com/pricing"),
            ("官方主页", "https://morphllm.com/"),
        ],
    },
    "mancer": {
        "category": "international",
        "display_name": "Mancer",
        "free_quota": "注册赠金数额未在官方页公示（历史“$1”说法无法复核，不予采信）；免费模型长期可用，付费额度以账户标注为准",
        "validity": "免费模型长期可用；付费额度以账户标注为准",
        "free_models": [
            "官方模型页标注 **FREE** 的模型（如 `MythoLite`，及 MythoMax、Magnum 72B v4 等角色扮演向模型）—— **0 元免费调用**（清单以 mancer.tech/models 页面 FREE 标签为准）",
            "付费另有 DeepSeek V4 Flash 284B、GLM 4.7 353B、GPT OSS 120B 等",
        ],
        "tier_caveats": [
            "只有模型页标 **FREE** 的角色扮演向模型 0 元（如 MythoLite 等），其余模型按 token 计费；FREE 清单随页面调整",
            "免费模型同样限速，具体 RPM 以模型页标注为准",
        ],
        "preconditions": "邮箱注册；按 token 消耗计费",
        "promotions": "OpenAI 兼容接口，主打角色扮演/创意写作（RP）场景的无审查模型托管。",
        "notes": "免费模型清单以 mancer.tech/models 页面 FREE 标签为准。",
        "links": [
            ("模型页（FREE 标注）", "https://mancer.tech/models"),
            ("API 开发者文档", "https://mancer.tech/docs-api/"),
            ("定价页", "https://mancer.tech/pricing"),
            ("官方主页", "https://mancer.tech/"),
        ],
    },
    "poolside": {
        "category": "international",
        "display_name": "Poolside",
        "free_quota": "已从申请制转为**开放注册**，官方标注 **“Free to use for a limited time”**（限时免费，截止时间未公布，以官方后续公告为准）",
        "validity": "限时免费期内有效（以官方后续公告为准）",
        "free_models": [
            "代码模型 **`Laguna S 2.1`**（118B 总参/8B 激活，1M 上下文）、**`Laguna XS 2.1`**（33B/3B 激活，256K）—— **限时免费调用**；端点 inference.poolside.ai/v1（OpenAI 兼容），权重在 Hugging Face 发布",
        ],
        "tier_caveats": [
            "**限时免费且官方未公布截止日**（原文 “Free to use for a limited time”）——随时可能转收费，接入前先看官方公告",
            "免费的是 Laguna S 2.1 / XS 2.1 两款代码模型；也可经 OpenRouter 的 :free 实例调用",
        ],
        "preconditions": "官网注册获取 API Key",
        "promotions": "面向软件工程的代码生成/改写模型，支持长上下文仓库级理解。",
        "notes": "限时免费结束后的定价以 poolside.ai/models 页面公告为准。",
        "links": [
            ("模型页", "https://poolside.ai/models"),
            ("官方主页", "https://poolside.ai/"),
        ],
    },
    "relace": {
        "category": "international",
        "display_name": "Relace",
        "free_quota": "官方定价页原文：提供在线 Playground 并可**“从免费套餐（free tier）开始在您的应用中测试 Relace 模型”**（Sign Up for Free）；具体免费额度未公开数字，以注册后控制台为准",
        "validity": "以注册后控制台显示为准",
        "free_models": [
            "面向编程智能体的推理模型 `relace-compact`、`relace-apply-3`、`relace-rank`、`relace-search`（代码改写/检索/排序）—— **免费套餐（free tier）可用**，具体配额注册后查看",
        ],
        "tier_caveats": [
            "**免费套餐配额不公开数字**，官方定价页只写可从 free tier 开始测试，具体限额要注册后在控制台查看",
            "免费模型是编程 Agent 专用模型（compact/apply/rank/search），不是通用对话模型",
        ],
        "preconditions": "官网注册（免费套餐入口）；企业部署可预约 guided onboarding",
        "promotions": "为编码 Agent 提供低延迟代码变换与检索基础设施，OpenAI 兼容接口。",
        "notes": "免费套餐具体配额需注册后查看；定价页主打 token 计费的基础设施套餐。",
        "links": [
            ("定价页（含 free tier 说明）", "https://relace.ai/pricing"),
            ("官方主页", "https://relace.ai/"),
        ],
    },

    # ------------------ Part 3: 云厂商与 Serverless 算力平台 (9) ------------------
    "modal": {
        "category": "cloud",
        "display_name": "Modal (Serverless AI 云平台)",
        "free_quota": "**每月 $30 免费算力额度**，按月刷新、无需预付（官方定价页），支持 GitHub/Google/SSO 注册",
        "validity": "**每月重置**",
        "free_models": [
            "通用 Serverless GPU/CPU 平台，可自行部署 vLLM、LLM 推理、Whisper、FLUX 等任意模型/函数 —— 调用消耗 **每月 $30 免费额度**，可抵扣 GPU/CPU 使用，超出后按量计费",
        ],
        "tier_caveats": [
            "$30 是**算力额度而非现成模型 API**：要自己写函数 / 部署 vLLM，模型权重、镜像与代码都要自备；对只想拿 key 调模型的新手门槛高",
            "额度**按月刷新**，当月用不完不累积；GPU 单价高，A100 类机型 $30 只够很少的时长",
        ],
        "preconditions": "支持 GitHub/Google/SSO 注册（官方页面未见手机验证要求）",
        "promotions": "按秒计费、可缩容到零，适合个人开发者托管私有推理端点。",
        "notes": "免费额度可抵扣 GPU/CPU 使用；超出后按量计费。",
        "links": [
            ("开发文档直达", "https://modal.com/docs"),
            ("定价页（$30/月免费额度）", "https://modal.com/pricing"),
            ("官方主页", "https://modal.com/"),
        ],
    },
    "baseten": {
        "category": "cloud",
        "display_name": "Baseten",
        "free_quota": "新账户有试用额度但**官方未公开具体金额**（以注册后控制台为准）；**Startup Program**：入选可获最高 **$25,000** 专用算力 + **$2,500** Model APIs 额度（需申请审核）",
        "validity": "以账户/项目协议为准",
        "free_models": [
            "模型部署平台（Truss 框架）：模型库开源模型一键部署与付费专有模型端点 —— 新账户试用额度可抵扣，**金额未公开**",
        ],
        "tier_caveats": [
            "新账户试用额度**金额未公开**（官方定价页无数字），以注册后控制台为准，可能随时调整",
            "额度用于抵扣 GPU 部署与 Model APIs 调用，属**算力型额度**而非 LLM token 免费层",
            "Startup Program（最高 $25,000 专用算力 + $2,500 Model APIs）**需申请审核**，非注册即得",
        ],
        "preconditions": "注册账号；Startup Program 需申请审核",
        "promotions": "面向生产级 GPU 推理部署，支持自动扩缩容。",
        "notes": "普通试用额度以注册后控制台显示为准，无公开数字。",
        "links": [
            ("Startup Program", "https://www.baseten.co/startup-program/"),
            ("定价页", "https://www.baseten.co/pricing/"),
            ("官方主页", "https://baseten.co/"),
        ],
    },
    "modular_cloud": {
        "category": "cloud",
        "display_name": "Modular (原 BentoCloud/BentoML)",
        "free_quota": "**无公开注册赠金**（历史“$10 注册赠金”无法在当前官方页复核，BentoML 已被 Modular 收购）；免费项见左栏",
        "validity": "共享端点免费测试长期有效；自托管永久免费",
        "free_models": [
            "**共享推理端点（shared endpoints）** —— **可免费测试**（基于 MAX 引擎，可体验 Llama、DeepSeek 等开源模型）",
            "**自托管（self-hosted）** —— **永久免费**、不限模型，开源自托管无需账号",
        ],
        "tier_caveats": [
            "云端免费项仅限**共享端点（shared endpoints）测试**，不保证 SLA 与容量；稳定生产用途要么付费要么**自托管开源版**（MAX 引擎免费但要自备算力）",
        ],
        "preconditions": "官网注册（云托管）；开源自托管无需账号",
        "promotions": "BentoML/MAX 开源生态，Python 代码一键打包为生产推理服务。",
        "notes": "品牌与平台已迁移至 modular.com；bentoml.com 保留开源框架文档。",
        "links": [
            ("Modular 定价页", "https://www.modular.com/pricing"),
            ("Modular 官网", "https://www.modular.com/"),
            ("BentoML（开源框架）", "https://www.bentoml.com/"),
        ],
    },
    "infini_ai": {
        "category": "cloud",
        "display_name": "无问芯穹 Infini AI (GenStudio)",
        "free_quota": "官方计费文档明确 **GenStudio 不设试用额度**（无注册赠送 token）；免费项见左栏，API 推理按量付费",
        "validity": "网页体验长期免费；API 调用按量付费",
        "free_models": [
            "**嵌入/重排（embedding/rerank）模型接口 —— 免费**",
            "**网页 Playground —— 全模型免费体验**（DeepSeek V4、Qwen 3.6、GLM、Kimi、MiniMax、MiMo 等；当前模型列表无 Llama）",
            "GenStudio API 推理（上述模型）—— **不设试用额度**，调用按量付费",
        ],
        "tier_caveats": [
            "免费项仅限**嵌入 / 重排接口**与**网页 Playground**；GenStudio API 推理**不设试用额度**、按量付费，免费额度不可抵扣",
            "网页 Playground 免费体验的当前模型列表不含 Llama（DeepSeek V4、Qwen 3.6、GLM、Kimi、MiniMax、MiMo 等），清单随在架模型变动",
            "API 推理需充值后才能调用，官方计费文档已明确无注册赠送 token",
        ],
        "preconditions": "手机号注册；API 推理需充值",
        "promotions": "跨国产 GPU（昇腾、沐曦、天数智芯、摩尔线程等）统一调度的推理云。",
        "notes": "不要轻信“注册送 200 万 token”等旧说法，官方文档已明确无试用额度。",
        "links": [
            ("计费说明文档", "https://docs.infini-ai.com/gen-studio/api/usage-and-billing/billing.html"),
            ("模型列表文档", "https://docs.infini-ai.com/gen-studio/models/"),
            ("GenStudio 定价页", "https://cloud.infini-ai.com/pricing"),
        ],
    },
    "aws_bedrock": {
        "category": "cloud",
        "display_name": "Amazon Bedrock (AWS Free Tier)",
        "free_quota": "注册即得 **$100** 额度 + 最高 **$200**（6 个月内分期）探索额度（官方免费套餐页，需绑信用卡）；**AWS Activate** 初创计划最高可申请 **$200,000** 抵扣",
        "validity": "探索额度 **6 个月**；Always Free 永久",
        "free_models": [
            "Bedrock 托管 GPT-5.6 系列、Anthropic Claude 最新代、Llama 4、Amazon Nova、Qwen3 等 —— 调用可使用账户额度抵扣，**各模型具体免费额度以 Bedrock 定价页标注为准**；另含 **90 款服务 6 个月免费 + 30+ 款永久免费（Always Free）**",
        ],
        "preconditions": "注册 AWS 账号并绑定信用卡；控制台开通 Model Access",
        "promotions": "**AWS Activate** 初创计划最高可申请 **$200,000** 抵扣。",
        "notes": "与 AWS 生态（IAM、Lambda、S3）集成；免费套餐政策以 aws.amazon.com/free 实时页面为准。",
        "links": [
            ("AWS Free Tier 官方页", "https://aws.amazon.com/free/"),
            ("Bedrock 定价", "https://aws.amazon.com/bedrock/pricing/"),
            ("Bedrock 文档", "https://docs.aws.amazon.com/bedrock/"),
        ],
    },
    "azure_openai": {
        "category": "cloud",
        "display_name": "Azure OpenAI / Azure AI Foundry",
        "free_quota": "注册送 **$200 额度（30 天有效）**（官方免费账号页，需信用卡/身份验证）；**Microsoft for Startups Founders Hub** 最高 **$150,000** Azure 额度",
        "validity": "$200 赠金 **30 天**；12 个月免费层按服务规则",
        "free_models": [
            "AI Foundry 托管 GPT-5.6 Sol/Terra/Luna 等 OpenAI 最新模型及开源模型 —— 可用 **$200 赠金**抵扣调用（模型清单以 Foundry 模型页为准）；另含 **20+ 款服务 12 个月免费 + 65+ 款永久免费**服务",
        ],
        "preconditions": "注册 Azure 账号（需信用卡/身份验证）；OpenAI 服务需在 Foundry 中申请接入",
        "promotions": "**Microsoft for Startups Founders Hub** 最高 **$150,000** Azure 额度。",
        "notes": "企业级合规与数据隔离；可用 $200 赠金抵扣 Foundry 模型调用。",
        "links": [
            ("Azure 免费账号页", "https://azure.microsoft.com/en-us/free/"),
            ("Azure AI 产品页", "https://azure.microsoft.com/en-us/products/ai/"),
            ("Foundry 模型文档", "https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/models"),
        ],
    },
    "gcp_vertex_ai": {
        "category": "cloud",
        "display_name": "Google Cloud Vertex AI",
        "free_quota": "新账号 **$300 赠金（90 天）** + **Always Free** 永久免费资源（官方免费页，需开通 Cloud Billing、信用卡验证）；**Google for Startups Cloud Program** 标准 $200,000、AI 赛道最高 **$350,000**",
        "validity": "$300 赠金 **90 天**；Always Free 永久",
        "free_models": [
            "Vertex 托管 Gemini 3.x 系列、Anthropic Claude Opus/Sonnet 5、Llama 4 等 —— 可用 **$300 赠金**抵扣调用（模型可用性以区域与 Vertex 模型页为准）",
        ],
        "preconditions": "Google 账号 + 开通 Cloud Billing（需信用卡验证）",
        "promotions": "**Google for Startups Cloud Program**：标准 **$200,000**，AI 赛道最高 **$350,000**。",
        "notes": "$300 赠金可抵扣 Vertex AI 调用；整合 GCP 全栈 MLOps 与 Grounding 检索。",
        "links": [
            ("GCP 免费套餐页", "https://cloud.google.com/free"),
            ("Vertex AI 文档", "https://cloud.google.com/vertex-ai/docs"),
            ("Vertex AI 定价", "https://cloud.google.com/vertex-ai/pricing"),
        ],
    },
    "ibm_watsonx": {
        "category": "cloud",
        "display_name": "IBM watsonx.ai (Free Toolbox)",
        "free_quota": "免费层（Free Toolbox/Lite）**无需信用卡**，注册 IBM Cloud 账号即可；生产用途需升级 Standard/Premium",
        "validity": "免费额度**每月重置**",
        "free_models": [
            "**Granite 4.1** 系列（30b/8b/3b）及 Granite Speech/Vision 4.1 等 IBM 自研模型（部分开源可商用）—— 免费层**每月 300,000 tokens 生成额度 + 20 CUH（Capacity Unit-Hours）+ 100 个文档解析额度**，按月重置",
        ],
        "tier_caveats": [
            "Lite 免费层每月 **300,000 tokens 生成 + 20 CUH + 100 个文档解析**，按月重置；生产用途需升级 Standard/Premium",
            "免费层主要是 Granite 自研系列；第三方模型通常不包含在 Lite 额度内",
        ],
        "preconditions": "注册 IBM Cloud 账号（Lite 免费层免信用卡）",
        "promotions": "Granite 开源模型免许可费，面向受监管行业提供治理与版权保障。",
        "notes": "免费层适合原型验证；生产用途需升级 Standard/Premium。",
        "links": [
            ("watsonx.ai 产品页", "https://www.ibm.com/watsonx"),
            ("watsonx.ai 定价", "https://www.ibm.com/products/watsonx-ai/pricing"),
        ],
    },
    "oracle_oci_ai": {
        "category": "cloud",
        "display_name": "Oracle OCI Generative AI",
        "free_quota": "**$300 云额度（30 天有效）** + **Always Free** 永久免费资源（官方免费层文档，需信用卡做身份验证）",
        "validity": "$300 额度 **30 天**；Always Free 永久",
        "free_models": [
            "OCI 托管 Cohere Command A 系列、Gemini 2.5、Llama 4 Maverick/Scout、gpt-oss、Grok 4.3/4.20 等 —— 可用 **$300 云额度**抵扣（以预训练模型文档页清单为准）",
        ],
        "preconditions": "注册 Oracle Cloud 账号（需信用卡做身份验证）",
        "promotions": "提供专用 AI 集群（Dedicated AI Clusters）与 RDMA 网络。",
        "notes": "$300 额度可抵扣 OCI 生成式 AI 服务用量。",
        "links": [
            ("OCI 预训练模型文档", "https://docs.oracle.com/en-us/iaas/Content/generative-ai/pretrained-models.htm"),
            ("Always Free 资源说明", "https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm"),
            ("OCI 定价", "https://www.oracle.com/cloud/pricing/"),
        ],
    },

    # ------------------ 第三方情报库线索复核后收录（8） ------------------
    # 这批厂商来自 FreeLLM-API-KeyHub 的免费额度清单；收录前逐个访问官方页复核，
    # 复核结论（含"查不到"）如实写入下方字段，不搬运无法复核的数字。
    "lingyiwanwu_01ai": {
        "category": "domestic",
        "display_name": "零一万物 01.AI (开放平台)",
        "free_quota": "**平台疑似已关停**：据 CDP 读取官方开放平台首页公告，2026-08-03 发布下线公告、API 服务 **2026-09-03 停止**；本轮静态复核未能确认（站点为前端渲染 SPA，仅取到页面标题；Web 搜索亦无结果），故**标注为待核实而非确认事实**",
        "validity": "不适用（若公告属实则服务已停）",
        "free_models": [
            "Yi 系列模型与「万策」「万智」多智能体平台的模型清单需登录平台查看，公开页面无免费模型标注",
        ],
        "preconditions": "不适用",
        "promotions": "官方开放平台公开页面无邀请 / 拉新活动记载。",
        "notes": "第三方情报库所称「注册送体验金 / 1 个月」**不予采信**。条目保留作为历史记录与跟踪；若确已关停，应从免费额度名单移除。",
        "links": [
            ("开放平台", "https://platform.lingyiwanwu.com/"),
        ],
    },
    "kunlun_tiangong": {
        "category": "domestic",
        "display_name": "昆仑万维 天工 (开放平台)",
        "free_quota": "**开发者 API 已无响应**：`model-platform.tiangong.cn` 302 跳转至天工主站（消费端产品页），`api.tiangong.cn` 返回 **503 Service Unavailable**；无免费额度可查",
        "validity": "不适用",
        "free_models": [
            "天工系列模型目前仅见消费端（App / 网页）入口，开发者开放平台与免费 API 额度公开页均未找到",
        ],
        "preconditions": "未提供可用的公开开发者注册入口",
        "promotions": "第三方情报库亦标注「当前可能已无标准化公开免费额度」「API 开放平台个人免费额度待确认」，与本轮复核一致。",
        "notes": "产品重心已转向天工 App 消费端；条目保留跟踪 API 是否恢复，暂不应进免费额度主力名单。",
        "links": [
            ("天工主站（开放平台入口跳转目标）", "https://www.tiangong.cn/"),
            ("原开放平台入口", "https://model-platform.tiangong.cn/"),
            ("开发者 API（当前 503）", "https://api.tiangong.cn/"),
        ],
    },
    "anyscale": {
        "category": "international",
        "display_name": "Anyscale",
        "free_quota": "注册即送 **$100 Anyscale Credits**（官方 pricing 页原文：\"Get started with $100 credit\"）；项目模板一键启动另含 **$5** 额度（原文：\"Launch project with $5\"）",
        "validity": "官方 pricing 页**未载明** $100 额度的有效期",
        "free_models": [
            "**无独立免费模型层**：额度用于抵扣 Ray on Anyscale 的 GPU / CPU 算力消耗（VM / K8s 部署），按量计费",
        ],
        "preconditions": "注册 Anyscale 账号，**需工作邮箱（work email）**；pricing 页未公示绑卡要求",
        "promotions": "另有初创企业扶持计划；Committed contracts 提供批量折扣（需商务接触）。",
        "notes": "本质是托管 Ray 算力平台而非 LLM 免费层，$100 属于算力试用金；无永久免费层。**注意稳定性风险**：官方 2026-07-30 公告已签署被 **Nscale** 收购的最终协议，额度与产品后续政策可能变动。",
        "links": [
            ("Pricing（$100 额度说明）", "https://www.anyscale.com/pricing"),
            ("官方主页", "https://www.anyscale.com/"),
        ],
    },
    "digitalocean_genai": {
        "category": "cloud",
        "display_name": "DigitalOcean Inference Engine",
        "free_quota": "新账号 **$5 试用金 / 90 天有效**（官方文档原文：$5 credit，\"expire 90 days after signup\"）——**全站通用额度，非 LLM 专属**",
        "validity": "**90 天**（自注册起）",
        "free_models": [
            "**无 LLM 免费层**：$5 为通用云试用金，可抵扣 Droplets / GPU / Inference Engine 等任意服务",
            "产品名已由 **GenAI Inference 改为 Inference Engine**（旧路径 `/products/genai-inference` 全线 404）",
        ],
        "preconditions": "注册账号并**必须添加有效付款方式**后才能创建 Droplets 等资源（官方文档原文：\"must add a valid payment method\"）",
        "promotions": "面向初创企业另有扶持计划（额度区间未在本轮官方页复核）。",
        "notes": "第三方情报库所称「$200 / 60 天」**已过期，不予采信**；现行官方口径为 **$5 / 90 天且需绑卡**。**不属于 LLM 免费层**，收录意义在于给需要 GPU 的实验留一个低门槛入口。",
        "links": [
            ("Signup Credit 文档（$5 / 90 天）", "https://docs.digitalocean.com/platform/billing/signup-credit/"),
            ("Pricing", "https://www.digitalocean.com/pricing"),
            ("Inference Engine 产品页", "https://www.digitalocean.com/products/inference-engine"),
        ],
    },
    "ncompass": {
        "category": "international",
        "display_name": "NCompass",
        "free_quota": "**业务已转型，不再是 LLM 推理平台**：官方站现定位为 \"GPU performance engineering for opencode\"（面向 opencode 工具的 GPU 性能优化），无 LLM API 与免费额度",
        "validity": "不适用",
        "free_models": [
            "无 LLM 模型服务；第三方情报库所称「$100 免费额度 / 低延迟推理平台」**不予采信**",
        ],
        "preconditions": "不适用",
        "promotions": "无。",
        "notes": "本轮复核判定为已转型（非停服），与免费额度无关；条目保留以便下次巡检复核。",
        "links": [
            ("官方站", "https://ncompass.tech/"),
        ],
    },
    "inception_labs": {
        "category": "international",
        "display_name": "InceptionLabs",
        "free_quota": "新账号送 **1 亿 free tokens**（官方文档原文：\"Every new account includes **100 million free tokens** — **no payment details required**\"），超出后再到 Billing 添加付款方式",
        "validity": "官方文档未载明免费额度的有效期",
        "free_models": [
            "`mercury-2.5`（diffusion-based LLM，官方文档唯一具名的免费可用模型）；模型列表另含 Mercury 2 / Mercury Edit",
            "付费定价：输入 $0.25 / 百万 tokens、输出 $0.75 / 百万 tokens（免费额度用完后适用）",
        ],
        "tier_caveats": [
            "1 亿 tokens 的**有效期官方文档未载明**，也未说明是否按月重置，按一次性到账规划用量",
            "免费额度对应 mercury 系列模型；超出后输入 $0.25 / 输出 $0.75 每百万 tokens，需到 Billing 加付款方式",
        ],
        "preconditions": "注册 Inception Platform 账号；**免费额度阶段无需信用卡**",
        "promotions": "无其他活动记载。",
        "notes": "第三方情报库所称「1000 万 tokens」少了一个数量级，实际为 **1 亿**。**免费额度写在文档站**（`docs.inceptionlabs.ai/get-started`），根站 `/pricing` 路径 404——只查官网首页会误判为「无免费层」。",
        "openai_compat": {
            "summary": "新号 1 亿 free tokens，免信用卡",
            "api_key_label": "Dashboard 申请",
            "api_key_url": "https://platform.inceptionlabs.ai/dashboard/api-keys",
            "base_url": "https://api.inceptionlabs.ai/v1",
            "models": "`mercury-2.5`, `mercury-2`",
        },
        "links": [
            ("文档 Quick Start（免费额度说明）", "https://docs.inceptionlabs.ai/get-started"),
            ("官方主页", "https://www.inceptionlabs.ai/"),
        ],
    },
    "inference_net": {
        "category": "international",
        "display_name": "Inference.net",
        "free_quota": "**$0 免费档给的是观测额度，不是推理额度**：含 **100 万 Gateway 请求**（指 LLM 流量的 tracing/trace 上报）、**30 req/min**、**1 seat**、**14 天数据留存**；官方 ToS 原文「To use non-free aspects of the Service, you must provide ... at least one (1) current, valid payment card」——免费档不需信用卡",
        "validity": "100 万请求为档内包含额度（是否按月重置官方页未载明）",
        "free_models": [
            "**无免费推理模型**：100 万请求是 Gateway 的观测/追踪请求配额（Tracing spans），不是模型调用次数",
            "要跑推理需先付费购买 **Deploy**（专用 GPU 部署自己的模型），再通过 `api.inference.net/v1` 调用；官方示例的 model 字段是 `acme-corp/my-model` 这类**自部署模型路径**",
            "付费档 Growth 为 $250/月，含 **$50 one-time opening credit**（一次性，**不属于免费档**）",
        ],
        "preconditions": "注册账号，**仅支持 GitHub / Google OAuth**（`inference.net/register`）",
        "promotions": "Growth 档含 $50 一次性开户赠金；免费档本身无额外活动。",
        "notes": "第三方情报库所称「$1/月重置额度」无官方页支撑，**不予采信**。**重要：这是可观测性平台而非免费推理平台**——`api.inference.net/v1/models` 无鉴权即返回完整模型目录（含 claude 系列，标注 upstream 单价），说明模型目录公开可读，但推理本身仍需付费部署。**OpenAI 兼容 base URL 为 `https://api.inference.net/v1`**（官方 docs 示例确认）。",
        "links": [
            ("Pricing（免费档额度）", "https://inference.net/pricing/"),
            ("文档：Call Your Deployment", "https://docs.inference.net/platform/deploy/call-your-deployment"),
            ("注册", "https://inference.net/register/"),
            ("官方主页", "https://inference.net/"),
        ],
    },
    "mara": {
        "category": "international",
        "display_name": "Mara",
        "free_quota": "**未找到任何 LLM 平台的一手证据，疑为虚构条目**：`www.mara.com` 是比特币矿企 **MARA Holdings Inc.**（无 LLM API）；`mara.ai` 为 GoDaddy 停放域名（标价 $1,420,000）；`getmara.ai` 是 HR 招聘 ATS；`maralabs.ai` 显示 COMING SOON；`docs.mara.ai` SSL 失败；Wayback Machine 从未归档过 `mara.ai` 的 LLM 内容",
        "validity": "不适用",
        "free_models": [
            "无。第三方情报库所称「$5 / 30 天免费额度」**不予采信**——查遍候选域名、Wayback 与新闻检索均无一手来源",
        ],
        "preconditions": "不适用",
        "promotions": "无。",
        "notes": "该条目来源存疑，可能是名字混淆或上游情报库的幻觉条目；建议回溯源数据核对。保留条目作为反例留痕，**不应作为可用免费额度来源**。",
        "links": [
            ("MARA Holdings（比特币矿企，非 LLM）", "https://www.mara.com/"),
        ],
    },
}


# ---------------------------------------------------------------------------
# AI 巡检补丁（profile_overrides.json）
#
# 每日巡检检测到官方页面变化时，AI 只向 profile_overrides.json 写结构化补丁，
# 不修改本文件。补丁按字段整体覆盖（free_models 等列表给出完整新内容）；
# 下划线开头的键（_updated / _evidence / _summary）为元信息，不参与渲染。
# 白嫖攻略元数据通过补丁中的 guide_meta 覆盖 GUIDE_META。
# ---------------------------------------------------------------------------
_OVERLAY_PATH = Path(__file__).resolve().parent / "profile_overrides.json"
_OVERLAY_FIELDS = {
    "category", "display_name", "free_quota", "validity", "free_models",
    "preconditions", "promotions", "notes",
    "invite_reward", "student_benefit", "openai_compat", "tier_caveats",
}

#: 巡检证据的展示顺序（键名即 crawler_llm_intel.KEYWORD_GROUPS 的分组名）。
#: 免费层 > 注册赠送 > 邀请返利 > 学生扶持 > 限时活动 > 套餐 > 限制条件。
EVIDENCE_DISPLAY_ORDER = (
    "free_tier", "signup_bonus", "referral", "student",
    "activity", "subscription", "condition",
)


def _load_overrides() -> dict:
    try:
        data = json.loads(_OVERLAY_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


_PROFILE_OVERRIDES: dict = _load_overrides()


def reload_overrides() -> dict:
    """AI 写入新补丁后在同一进程内调用，重新加载 JSON。"""
    global _PROFILE_OVERRIDES
    _PROFILE_OVERRIDES = _load_overrides()
    return _PROFILE_OVERRIDES


def _apply_overlay(profile: dict, vendor_id: str) -> dict:
    patch = _PROFILE_OVERRIDES.get(vendor_id)
    if not isinstance(patch, dict):
        return profile
    merged = dict(profile)
    for key, val in patch.items():
        if key in _OVERLAY_FIELDS:
            merged[key] = val
    return merged


def get_guide_meta(vendor_id: str) -> dict:
    """攻略元数据：GUIDE_META 为基线，AI 补丁中的 guide_meta 整体覆盖。"""
    meta = dict(GUIDE_META.get(vendor_id, {}))
    patch = _PROFILE_OVERRIDES.get(vendor_id)
    if isinstance(patch, dict) and isinstance(patch.get("guide_meta"), dict):
        meta.update(patch["guide_meta"])
    return meta


def get_provider_profile(vendor_id: str, brand: str = "", homepage: str = "") -> dict:
    if vendor_id in PROVIDER_PROFILES:
        return _apply_overlay(PROVIDER_PROFILES[vendor_id], vendor_id)
    base = {
        "category": "domestic",
        "display_name": brand or vendor_id,
        "free_quota": "详见官方最新控制台活动公告",
        "validity": "以官方控制台说明为准",
        "free_models": ["免费模型与额度以官方控制台实时信息为准"],
        "preconditions": "注册官方账号",
        "promotions": "提供标准开发者支持",
        "notes": "以官方页面实时信息为准",
        "links": [("官方主页", homepage or "")],
    }
    return _apply_overlay(base, vendor_id)


def render_freellm_table(intel, profile: dict, index: int) -> list[str]:
    """参考 FreeLLM-API-KeyHub 生成美观、详尽且无状态噪点的 Markdown 规格表。"""
    out: list[str] = []
    dname = profile.get("display_name", intel.brand)
    hp = intel.homepage or (profile["links"][0][1] if profile.get("links") else "")

    out.append(f"### {index}. {dname}")
    out.append("")
    out.append("| 字段 | 详情 |")
    out.append("|------|------|")
    out.append(f"| **平台名称** | [{dname}]({hp}) |")
    # 免费模型与额度合并展示：每个模型内联其免费额度 / 限速，不再分两栏
    fm = profile.get('free_models', '—')
    if isinstance(fm, (list, tuple)):
        fm_cell = "<br>".join(f"• {item}" for item in fm)
    else:
        fm_cell = str(fm)
    out.append(f"| **免费模型与额度** | {fm_cell} |")
    out.append(f"| **注册福利 / 账户赠送** | {profile.get('free_quota', '—')} |")
    out.append(f"| **额度有效期** | {profile.get('validity', '—')} |")
    out.append(f"| **前置条件 / 限制** | {profile.get('preconditions', '—')} |")
    # 免费层的真实边界：只免旧版？限速多少？能否商用？各平台差异极大，
    # 用独立字段强制写清，避免「全家桶永久免费」这类覆盖关键限制的笼统说法
    if profile.get("tier_caveats"):
        caveats = profile["tier_caveats"]
        cell = "<br>".join(f"• {item}" for item in caveats) if isinstance(caveats, (list, tuple)) else str(caveats)
        out.append(f"| **免费层限制 / 注意事项** | {cell} |")
    out.append(f"| **邀请 / 特惠活动** | {profile.get('promotions', '—')} |")
    # 邀请返利与学生扶持是独立维度：只有存在可核实的官方记载时才出这两行
    if profile.get("invite_reward"):
        out.append(f"| **邀请 / 拉新奖励** | {profile['invite_reward']} |")
    if profile.get("student_benefit"):
        out.append(f"| **学生 / 高校扶持** | {profile['student_benefit']} |")

    # 提取实时巡检证据（如果页面抓取到了真实事实，翻译为中文后嵌入表格）
    # 证据分组键必须与 crawler_llm_intel.KEYWORD_GROUPS 的分组名一致；
    # 按「与免费额度相关性」从高到低取前 3 条。历史上这里写的是 trial_bonus /
    # monthly_sub / promotions / constraints 等不存在的分组名，导致只有 free_tier 生效。
    live_items = []
    if intel.evidence:
        for key in EVIDENCE_DISPLAY_ORDER:
            snips = intel.evidence.get(key) or []
            for sn in snips[:1]:  # 每类精选 1 条高价值动态
                # 自动翻译非中文
                trans = normalize_zh_punct(translate_to_zh(sn.text))
                # 截断过长文本
                if len(trans) > 120:
                    trans = trans[:117] + "…"
                live_items.append(f"• {trans}")
    if live_items:
        live_str = "<br>".join(live_items[:3])
        out.append(f"| **实时巡检证据** | {live_str} |")

    # 官方直达链接
    link_parts = []
    for label, url in profile.get("links", []):
        if url:
            link_parts.append(f"[{label}]({url})")
    if not link_parts and hp:
        link_parts.append(f"[官方主页]({hp})")
    out.append(f"| **官方直达** | {' ｜ '.join(link_parts)} |")

    if profile.get("notes"):
        out.append(f"| **特别说明** | {profile['notes']} |")

    out.append("")
    return out
