# LLM 厂商博客 / 更新动态订阅源

<!-- LLM-NEWS:BEGIN  本章节由 crawler_llm_intel.py 自动生成，请勿手工修改 -->

## 厂商博客 / 更新动态订阅源

> 由 `crawler_llm_intel.py` 自动整理，最近更新：**2026-09-24 08:47:30**。
>
> 各厂商的官方博客、工程文章、更新日志**单独维护在此**，不混入 README 的免费额度情报；
> 每个厂商下方列出从官方 RSS / 博客页**实际抓取的最新文章**（标题自动汉化、附发布日期与原文链接）。
> 主文档每家仅展示**最新 5 篇**；**完整文章归档**按厂商拆分到 [`llm-news/`](llm-news/) 子目录（每厂商一个 `.md`，全量罗列该来源所有文章）。
> 可将同目录下的 `llm-news-feeds.opml` 导入任意 RSS 阅读器（如 Feedly / Inoreader / NetNewsWire / 本地阅读器）统一订阅（原生源 + 本仓库自建源，OPML 里分两组）。
>
> 📡 **本仓库自建 RSS**：把下方归档直接转成订阅源，**官方没有原生 RSS 的厂商也能订阅**（标题同样已汉化，每日随巡检刷新）：
> - 网页浏览 / 一键订阅：[https://free-llm-intel.aishort.top/](https://free-llm-intel.aishort.top/)（可按厂商筛选、搜索，页脚列出**全部有动态源的厂商**单源）
> - 合并流（聚合全部有动态源的厂商）：[`llm-news-all.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-all.xml)（收录全部有日期的条目，带厂商前缀，可按 `category` 过滤）
> - 单厂商源：`https://free-llm-intel.aishort.top/feeds/llm-news-{vendor_id}.xml`（把 `{vendor_id}` 换成下方括号里的厂商 id，如 `llm-news-openai.xml`）
> - ⚠️ 合并流与各厂商单源**内容重叠**，二选一订阅即可（都订会出现重复条目）；合并流只收有日期的条目，**要看全量请用浏览页或单厂商源**。

### OpenAI (openai)
- 页面：[官方博客](https://openai.com/blog)
  - 📡 RSS/Atom：https://openai.com/news/rss.xml
- 页面：[新闻 / 更新](https://openai.com/news/)
  - 📡 RSS/Atom：https://openai.com/news/rss.xml
- 📡 [RSS/Atom 订阅源](https://openai.com/news/rss.xml)：`https://openai.com/news/rss.xml`
- 📰 **最新文章**（官方源抓取于 2026-09-24，标题自动汉化）：
  1. [GPT-6 的提示缓存全面升级](https://openai.com/index/better-prompt-caching-for-gpt-6)（2026-09-22）
  2. [介绍 GPT-6 Sol 与 Luna](https://openai.com/index/introducing-gpt-6-sol-and-luna)（2026-09-22）
  3. [澳大利亚青少年安全蓝图简介](https://openai.com/index/australian-youth-safety-blueprint)（2026-09-18）
  4. [推出面向法律行业的 Astra](https://openai.com/index/astra-for-law)（2026-09-17）
  5. [Cooley 如何利用 ChatGPT 加速 IPO 工作](https://openai.com/index/cooley-gopublic)（2026-09-17）
  - 📄 完整文章归档（共 1213 篇）：[openai.md](llm-news/openai.md)

### Anthropic Claude (anthropic)
- 页面：[官方博客](https://claude.com/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 页面：[新闻 / 更新](https://www.anthropic.com/news)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-anthropic.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-anthropic.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-24，标题自动汉化）：
  1. [与埃森哲合作开展嵌入式评估的公告](https://www.anthropic.com/news/accenture-embedded-evaluation)（2026-09-18）
  2. [生命科学验证计划简介](https://www.anthropic.com/news/life-sciences-verification-program)（2026-09-17）
  3. [与客户共同打造企业级前沿保障](https://www.anthropic.com/news/enterprise-frontier-safeguards)（2026-09-01）
  4. [改进我们的对齐与安全工作](https://www.anthropic.com/news/improving-alignment-security-efforts)（2026-08-31）
  5. [预览 Model Hardware Standard](https://www.anthropic.com/news/model-hardware-standard-research-preview)（2026-08-27）
  - 📄 完整文章归档（共 69 篇）：[anthropic.md](llm-news/anthropic.md)

### Google Gemini (google_gemini)
- 页面：[变更日志](https://ai.google.dev/gemini-api/docs/changelog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-google_gemini.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-google_gemini.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-24，标题自动汉化）：
  1. [Gemini 3.8 Flash TTS 和 Gemini 3.8 Flash-Lite TTS 正式版 (GA)](https://ai.google.dev/gemini-api/docs/changelog?hl=zh-cn#09-22-2026-1)（2026-09-22）
  2. [反重力剂09-2026](https://ai.google.dev/gemini-api/docs/changelog?hl=zh-cn#09-17-2026-1)（2026-09-17）
  3. [Gemini 3.8 Live 和 Gemini 3.8 Live Extended Thinking 正式版 (GA)](https://ai.google.dev/gemini-api/docs/changelog?hl=zh-cn#09-15-2026-1)（2026-09-15）
  4. [双子座3.8 活生生的延伸思考](https://ai.google.dev/gemini-api/docs/changelog?hl=zh-cn#09-15-2026-2)（2026-09-15）
  5. [Lyria 3.5 正式版 (GA)](https://ai.google.dev/gemini-api/docs/changelog?hl=zh-cn#09-03-2026-1)（2026-09-03）
  - 📄 完整文章归档（共 43 篇）：[google_gemini.md](llm-news/google_gemini.md)

### xAI Grok (xai_grok)
- 页面：[新闻 / 更新](https://x.ai/news)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-xai_grok.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-xai_grok.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-24，标题自动汉化）：
  1. [Grok Build 中的记忆功能](https://x.ai/news/grok-build-memory)（2026-09-16）
  2. [让 Grok Bot 全面接管采购流程](https://x.ai/news/grok-bot-procurement)（2026-09-04）
  3. [为持久代理时代设计 Grok Bot](https://x.ai/news/designing-grok-bot)（2026-09-03）
  4. [前沿生物安全](https://x.ai/news/biosafety-at-the-frontier)（2026-09-01）
  5. [Grok Bot 现已支持 X](https://x.ai/news/grok-bot-and-x)（2026-08-29）
  - 📄 完整文章归档（共 82 篇）：[xai_grok.md](llm-news/xai_grok.md)

### Groq Cloud (groq)
- 页面：[变更日志](https://console.groq.com/docs/changelog)
  - 📡 RSS/Atom：https://github.com/groq/groq-changelog/commits/main.atom
- 📰 **最新文章**（官方源抓取于 2026-09-24，标题自动汉化）：
  1. [Q1 2026 更新日志条目](https://github.com/groq/groq-changelog/commit/abaa8395286b622a837adb5d6b44709845d1edba)（2026-05-06）
  2. [Groq 是首批将 NVIDIA Groq 3 LPX 和 Vera Rubin NVL72 推向市场的公司之一](https://groq.com/blog/groq-among-the-first-to-bring-nvidia-groq-3-lpx-and-vera-rubin-nvl72-to-market)（2026-03-24）
  3. [GroqCloud：扩展规模以满足需求](https://groq.com/blog/groqcloud-expanding-to-meet-demand)（2026-02-16）
  4. [12-01-25 更新日志](https://github.com/groq/groq-changelog/commit/1820d161308546dffffa80bf32485202ffb64459)（2025-12-02）
  5. [添加更新 (#17)](https://github.com/groq/groq-changelog/commit/844c61a2116a97e37e61736caacf9690182f6466)（2025-10-31）
  - 📄 完整文章归档（共 34 篇）：[groq.md](llm-news/groq.md)

### DeepSeek (deepseek)
- 页面：[更新日志](https://api-docs.deepseek.com/zh-cn/updates/)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 页面：[版本动态](https://api-docs.deepseek.com/zh-cn/news/news260424/)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-deepseek.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-deepseek.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-24，标题自动汉化）：
  1. [DeepSeek-V4.1-Flash 发布](https://api-docs.deepseek.com/zh-cn/news/news260910)（2026-09-10）
  2. [DeepSeek-V4-Flash-Vision-Exp 上线](https://api-docs.deepseek.com/zh-cn/news/news260821)（2026-08-21）
  3. [DeepSeek-V4-Pro 正式版上线](https://api-docs.deepseek.com/zh-cn/news/news260813)（2026-08-13）
  4. [DeepSeek-V4-Flash 更新](https://api-docs.deepseek.com/zh-cn/updates/#%E6%97%B6%E9%97%B4-2026-07-31)（2026-07-31）
  5. [DeepSeek-V4 预览版发布](https://api-docs.deepseek.com/zh-cn/news/news260424)（2026-04-24）
  - 📄 完整文章归档（共 34 篇）：[deepseek.md](llm-news/deepseek.md)

### 智谱 AI GLM (zhipu_glm)
- 页面：[更新日志](https://docs.bigmodel.cn/cn/update/new-releases)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-zhipu_glm.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-zhipu_glm.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-24，标题自动汉化）：
  1. [GLM-5.3-Flash 原生多模态模型上线](https://docs.bigmodel.cn/cn/update/new-releases#2026-08-26)（2026-08-26）
  2. [GLM-5.3 新一代旗舰模型上线](https://docs.bigmodel.cn/cn/update/new-releases#2026-8-19)（2026-08-19）
  3. [GLM-5.2 新一代旗舰模型上线](https://docs.bigmodel.cn/cn/update/new-releases#2026-06-16)（2026-06-16）
  4. [GLM Coding Plan 团队版上线](https://docs.bigmodel.cn/cn/update/new-releases#2026-05-29)（2026-05-29）
  5. [GLM-5.1 新一代旗舰模型上线](https://docs.bigmodel.cn/cn/update/new-releases#2026-04-07)（2026-04-07）
  - 📄 完整文章归档（共 26 篇）：[zhipu_glm.md](llm-news/zhipu_glm.md)

### 通义千问 Qwen (aliyun_qwen)
- 页面：[更新日志](https://help.aliyun.com/zh/model-studio/newly-released-models)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-aliyun_qwen.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-aliyun_qwen.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-24，标题自动汉化）：
  1. [stepfun/step-5-preview：Step 5 Preview 是面向真实世界 Agentic 任务的旗舰基座模型，在 AI 编程、软件工程、专业知识工作等任务上达到前沿水平，金融领域表现尤为突出](https://help.aliyun.com/zh/model-studio/newly-released-models#stepfun/step-5-preview)（2026-09-21）
  2. [qwen3.8-omni-flash-realtime：支持实时音视频交互及文本、音频输出，新增多通道音频、视频聚合和远程 MCP 工具调用，支持 WebSocket、WebRTC 和 AOQ 接入](https://help.aliyun.com/zh/model-studio/newly-released-models#qwen3.8-omni-flash-realtime)（2026-09-21）
  3. [ZHIPU/GLM-5.3-FlashX：GLM-5.3-FlashX 是 GLM-5 系列的高速模型，推理速度达 200 tokens/s，提供更快、更流畅的模型体验](https://help.aliyun.com/zh/model-studio/newly-released-models#ZHIPU/GLM-5.3-FlashX)（2026-09-21）
  4. [vanchin/deepseek-v4.1-flash：DeepSeek-V4.1-Flash 是 DeepSeek 全新模型结构系列中尺寸最小的模型，具备原生多模态视觉理解能力，支持 1M 上下文与 384K 输出](https://help.aliyun.com/zh/model-studio/newly-released-models#vanchin/deepseek-v4.1-flash)（2026-09-21）
  5. [qwen-audio-3.1-realtime-plus：支持实时双工语音对话，沿用 3.0 Plus 的接入协议，保留原有音色并新增 8 个系统音色](https://help.aliyun.com/zh/model-studio/newly-released-models#qwen-audio-3.1-realtime-plus)（2026-09-20）
  - 📄 完整文章归档（共 108 篇）：[aliyun_qwen.md](llm-news/aliyun_qwen.md)

### MiniMax (minimax)
- 页面：[更新日志](https://platform.minimax.cn/docs/release-notes/models)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 页面：[更新日志](https://platform.minimax.cn/docs/release-notes/apis)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-minimax.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-minimax.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-24，标题自动汉化）：
  1. [MiniMax H3 发布](https://platform.minimax.cn/docs/release-notes/models#2026-%E5%B9%B4-7-%E6%9C%88-31-%E6%97%A5)（2026-07-31）
  2. [全新 Music-3.0](https://platform.minimax.cn/docs/release-notes/models#2026-%E5%B9%B4-7-%E6%9C%88-16-%E6%97%A5)（2026-07-16）
  3. [MiniMax M3 模型](https://platform.minimax.cn/docs/release-notes/models#2026-%E5%B9%B4-6-%E6%9C%88-1-%E6%97%A5)（2026-06-01）
  4. [Music-2.6](https://platform.minimax.cn/docs/release-notes/models#2026-%E5%B9%B4-4-%E6%9C%88)（2026-04-01）
  5. [MiniMax M2.7](https://platform.minimax.cn/docs/release-notes/models#2026-%E5%B9%B4-3-%E6%9C%88-18-%E6%97%A5)（2026-03-18）
  - 📄 完整文章归档（共 36 篇）：[minimax.md](llm-news/minimax.md)

### 月之暗面 Kimi (moonshot_kimi)
- 页面：[变更日志](https://platform.kimi.com/docs/changelog/changelog/changelog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-moonshot_kimi.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-moonshot_kimi.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-24，标题自动汉化）：
  1. [🤖 Kimi 托管智能体（Hosted Agents）Beta 上线在模型推理 API 之上，我们封装了 Kimi Durable Harness，为企业提供 7x24 小时全托管的智能体运行环境——无需自建沙箱与会话基础设施，就能让 Agent 高质量、可持续地执行长程任务。](https://platform.kimi.com/docs/changelog#2026%E5%B9%B49%E6%9C%88)（2026-09-01）
  2. [kimi-k2.5 与 moonshot-v1 全系列模型（含 -vision-preview、moonshot-v1-auto）已于今日 16:00 在国内外全平台下线，调用将返回 404 错误（模型不存在），请迁移至 Kimi K3](https://platform.kimi.com/docs/changelog/changelog/changelog#2026%E5%B9%B48%E6%9C%8831%E6%97%A5)（2026-08-31）
  3. [kimi-k2.5 与 moonshot-v1 全系列模型（含 -vision-preview、moonshot-v1-auto）在国内外全平台下线，调用将返回 404 错误，请迁移至 Kimi K3](https://platform.kimi.com/docs/changelog#2026%E5%B9%B48%E6%9C%88)（2026-08-01）
  4. [🚀 Kimi K3 上线开放平台 APIKimi 面向长程编程与端到端知识工作的旗舰模型 K3 正式通过开放平台 API 提供，1M token 上下文，综合智能达到领先水平。详见 Kimi K3 快速开始。同期 kimi-k2.5 和 moonshot-v1 系列停止向新注册用户开放。账户概览新增当日实时消费金额展示，平台服务协议同步更新。](https://platform.kimi.com/docs/changelog#2026%E5%B9%B47%E6%9C%88)（2026-07-01）
  5. [支持组织级 API IP 白名单配置，企业安全管控更精细](https://platform.kimi.com/docs/changelog#2026%E5%B9%B46%E6%9C%88)（2026-06-01）
  - 📄 完整文章归档（共 26 篇）：[moonshot_kimi.md](llm-news/moonshot_kimi.md)

### Mistral AI (mistral)
- 页面：[新闻 / 更新](https://mistral.ai/news/)
  - 📡 RSS/Atom：https://mistral.ai/news/rss
- 📡 [RSS/Atom 订阅源](https://mistral.ai/news/rss)：`https://mistral.ai/news/rss`
- 📰 **最新文章**（官方源抓取于 2026-09-24，标题自动汉化）：
  1. [Mistral 和 Mozilla 正在为您的网络浏览器带来开放、私密和多语言的人工智能](https://mistral.ai/news/mistral-x-mozilla/)（2026-09-16）
  2. [Cloudera 与 Mistral 合作，为企业数据带来专业、主权化的智能](https://mistral.ai/news/mistral-x-cloudera/)（2026-09-10）
  3. [用 AI 代理现代化改造复杂的遗留代码。](https://mistral.ai/news/legacy-code-modernization/)（2026-09-09）
  4. [Mistral 融资 €3B，推动主权开放权重 AI 走向技术前沿](https://mistral.ai/news/mistral-makes-sovereign-open-weight-ai-to-frontier/)（2026-09-08）
  5. [Mistral 携手 HUMAIN](https://mistral.ai/news/mistral-x-humain/)（2026-08-24）
  - 📄 完整文章归档（共 87 篇）：[mistral.md](llm-news/mistral.md)

### Cohere (cohere)
- 页面：[官方博客](https://cohere.com/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-cohere.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-cohere.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-24，标题自动汉化）：
  1. [Cohere 和 OpenText 合作，为政府和受监管行业带来值得信赖的代理人工智能汇集企业数据、上下文和安全人工智能，以大规模支持代理人工智能](https://cohere.com/blog/cohere-and-open-text-partner-to-bring-trusted-ai)（2026-09-16）
  2. [谁来定义人工智能的规则？](https://cohere.com/blog/who-gets-to-define-the-rules-for-ai)（2026-09-13）
  3. [推出 North Small Translate：领先的主权开放权重机器翻译模型，性能出众、体积适中，为速度与成本效率而生。](https://cohere.com/blog/north-small-translate)（2026-09-10）
  4. [North Mini Code 的巨型内核服务引擎内部](https://cohere.com/blog/megakernels)（2026-09-08）
  5. [自动化的早期足迹](https://cohere.com/blog/automations-early-footprint)（2026-09-03）
  - 📄 完整文章归档（共 31 篇）：[cohere.md](llm-news/cohere.md)

### Meta Llama (meta_llama)
- 页面：[官方博客](https://ai.meta.com/blog/)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 [RSS/Atom 订阅源](https://about.fb.com/news/tag/ai/feed/)：`https://about.fb.com/news/tag/ai/feed/`
- 📰 **最新文章**（官方源抓取于 2026-09-24，标题自动汉化）：
  1. [介绍 Ray-Ban Meta Audio 及更多 AI 眼镜款式](https://about.fb.com/news/2026/09/introducing-ray-ban-meta-audio-glasses-new-styles-plus-muse/)（2026-09-23）
  2. [加拿大初创公司 smartARM 利用人工智能打造直观的仿生假肢](https://about.fb.com/news/2026/09/canadian-start-up-smartarm-uses-ai-to-create-intuitive-bionic-prosthetics/)（2026-09-16）
  3. [隆重推出 Meta One：一种具有更多功能和 AI 的订阅服务，可用于创建、连接和脱颖而出](https://about.fb.com/news/2026/09/introducing-meta-one-subscription-service-more-features-ai/)（2026-09-15）
  4. [推出 Muse：全球首个为每个人打造的个人 AI 代理](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/)（2026-09-08）
  5. [闭环冷却解释：Meta 人工智能背后的管道](https://about.fb.com/news/2026/08/closed-loop-cooling-explained-the-plumbing-behind-metas-ai/)（2026-08-27）
  - 📄 完整文章归档（共 16 篇）：[meta_llama.md](llm-news/meta_llama.md)

### Hugging Face (huggingface)
- 页面：[官方博客](https://huggingface.co/blog)
  - 📡 RSS/Atom：https://huggingface.co/blog/feed.xml
- 📡 [RSS/Atom 订阅源](https://huggingface.co/blog/feed.xml)：`https://huggingface.co/blog/feed.xml`
- 📰 **最新文章**（官方源抓取于 2026-09-24，标题自动汉化）：
  1. [您的代理人完成了任务。它会再次这样做吗？](https://huggingface.co/blog/ibm-research/altk-evolve-consistency)（2026-09-15）
  2. [跨 HF 作业使用 LoRA 的异步 GRPO：存储桶、代理，无 NCCL](https://huggingface.co/blog/asyncgrpo-lora-hfjobs)（2026-09-10）
  3. [用 Gradio 工作流重建 AUTOMATIC1111](https://huggingface.co/blog/gradio-workflow-1111)（2026-09-10）
  4. [IBM 发布采用商业友好许可证的 SOTA 模型 Granite Time Series PatchTST-FM-r2](https://huggingface.co/blog/ibm-research/ibm-releases-sota-granite-time-series)（2026-09-09）
  5. [安全为了谁？拒绝主题的正确子集，而非整个主题](https://huggingface.co/blog/MultiverseComputingCAI/safety-for-whom)（2026-09-08）
  - 📄 完整文章归档（共 863 篇）：[huggingface.md](llm-news/huggingface.md)

### Cloudflare Workers AI (cloudflare_workers_ai)
- 📡 [RSS/Atom 订阅源](https://developers.cloudflare.com/workers-ai/changelog/index.xml)：`https://developers.cloudflare.com/workers-ai/changelog/index.xml`
- 📰 **最新文章**（官方源抓取于 2026-09-24，标题自动汉化）：
  1. [Workers AI - GLM-5.2 现已登陆 Workers AI](https://developers.cloudflare.com/workers-ai/changelog/#glm-52-now-available-on-workers-ai)（2026-06-16）
  2. [Workers AI - Moonshot AI Kimi K2.7 Code 现已登陆 Workers AI](https://developers.cloudflare.com/workers-ai/changelog/#moonshot-ai-kimi-k27-code-now-available-on-workers-ai)（2026-06-12）
  3. [Workers AI - 计划中的模型弃用](https://developers.cloudflare.com/workers-ai/changelog/#planned-model-deprecations)（2026-05-08）
  4. [Workers AI - Moonshot AI Kimi K2.6 现已登陆 Workers AI](https://developers.cloudflare.com/workers-ai/changelog/#moonshot-ai-kimi-k26-now-available-on-workers-ai)（2026-04-20）
  5. [Workers AI - Google Gemma 4 26B A4B 现已登陆 Workers AI](https://developers.cloudflare.com/workers-ai/changelog/#google-gemma-4-26b-a4b-now-available-on-workers-ai)（2026-04-04）
  - 📄 完整文章归档（共 35 篇）：[cloudflare_workers_ai.md](llm-news/cloudflare_workers_ai.md)

### Modular (原 BentoCloud/BentoML) (modular_cloud)
- 📡 [RSS/Atom 订阅源](https://www.modular.com/blog/rss.xml)：`https://www.modular.com/blog/rss.xml`
- 📰 **最新文章**（官方源抓取于 2026-09-24，标题自动汉化）：
  1. [模块化：模块化 26.6：开放编译器贡献、音频生成和扩展模型支持](https://www.modular.com/blog/modular-26-6-open-compiler-contributions-audio-generation-and-expanded-model-support)（2026-09-17）
  2. [模块化：Mojo🔥 现已开源！](https://www.modular.com/blog/mojo-open-source)（2026-08-18）
  3. [模块化：模块化和高通：相同的代码，新的芯片](https://www.modular.com/blog/modcon-qualcomm)（2026-08-18）
  4. [模块化：ModCon 2026：开源、开放云、开放芯片](https://www.modular.com/blog/modcon-announcements)（2026-08-18）
  5. [Modular：Modular 26.5：Mojo 1.0 来了！](https://www.modular.com/blog/modular-26-5-mojo-1-0-is-here)（2026-08-11）
  - 📄 完整文章归档（共 100 篇）：[modular_cloud.md](llm-news/modular_cloud.md)

---
共整理 16 个厂商的动态入口（其中 16 个成功提取最新文章），RSS/Atom 源 11 个。

<!-- LLM-NEWS:END -->
