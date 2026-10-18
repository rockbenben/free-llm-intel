# LLM 厂商博客 / 更新动态订阅源

<!-- LLM-NEWS:BEGIN  本章节由 crawler_llm_intel.py 自动生成，请勿手工修改 -->

## 厂商博客 / 更新动态订阅源

> 由 `crawler_llm_intel.py` 自动整理，最近更新：**2026-10-18 08:26:02**。
>
> 各厂商的官方博客、工程文章、更新日志**单独维护在此**，不混入 README 的免费额度情报；
> 每个厂商下方列出从官方 RSS / 博客页**实际抓取的最新文章**（标题自动汉化、附发布日期与原文链接）。
> 主文档每家仅展示**最新 5 篇**；**完整文章归档**按厂商拆分到 [`llm-news/`](llm-news/) 子目录（每厂商一个 `.md`，全量罗列该来源所有文章）。
> 可将同目录下的 `llm-news-feeds.opml` 导入任意 RSS 阅读器（如 Feedly / Inoreader / NetNewsWire / 本地阅读器）统一订阅（原生源 + 本仓库自建源 + 英文镜像，OPML 里分组）。
>
> 📡 **本仓库自建 RSS**：把下方归档直接转成订阅源，**官方没有原生 RSS 的厂商也能订阅**（标题同样已汉化，每日随巡检刷新）：
> - 网页浏览 / 一键订阅：[https://free-llm-intel.aishort.top/](https://free-llm-intel.aishort.top/)（可按厂商筛选、搜索，页脚列出**全部有动态源的厂商**单源）
> - 合并流（聚合全部有动态源的厂商）：[`llm-news-all.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-all.xml)（最近 100 条，带厂商前缀，可按 `category` 过滤）
> - 英文镜像合并流：[`llm-news-all.en.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-all.en.xml)（源语言标题，中文原生源的厂商不出现在这里）
> - 单厂商源：`https://free-llm-intel.aishort.top/feeds/llm-news-{vendor_id}.xml`（最近 50 条；把 `{vendor_id}` 换成下方括号里的厂商 id，如 `llm-news-openai.xml`；英文镜像同名加 `.en.xml`）
> - ⚠️ 合并流与各厂商单源**内容重叠**，二选一订阅即可（都订会出现重复条目）；中英两版**同时订**会看到同一份新闻各一条（guid 加了 `?li=1` 后缀区分，阅读器不会自动去重）。**建议按语言偏好二选一**。
> - 合并流只收有日期的条目；要看全量请用浏览页或单厂商源。

### Anthropic Claude (anthropic)
- 页面：[官方博客](https://claude.com/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 页面：[新闻 / 更新](https://www.anthropic.com/news)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-anthropic.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-anthropic.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [Anthropic 日本的一位 BDR，如何带着一队 Claude 智能体过一天](https://claude.com/resources/articles/how-an-anthropic-japan-business-development-representative-runs-his-day)（2026-10-16）
  2. [Claude Code 团队如何进行代码审查](https://claude.com/resources/articles#d-2026-10-16-2)（2026-10-16）
  3. [Code Review 现已正式可用](https://claude.com/resources/articles/code-review-is-now-generally-available)（2026-10-15）
  4. [在 Claude Platform 上用 OpenTelemetry 追踪 agent](https://claude.com/resources/articles/agent-observability-on-the-claude-platform)（2026-10-14）
  5. [Uber 的 CISO 谈如何为 AI 搭建内部威胁防控体系](https://claude.com/resources/articles/uber-s-ciso-on-building-an-insider-threat-program-for-ai)（2026-10-13）
  - 📄 完整文章归档（共 97 篇）：[anthropic.md](llm-news/anthropic.md)

### OpenAI (openai)
- 页面：[官方博客](https://openai.com/blog)
  - 📡 RSS/Atom：https://openai.com/news/rss.xml
- 页面：[新闻 / 更新](https://openai.com/zh-Hans-CN/news/)
  - 📡 RSS/Atom：https://openai.com/news/rss.xml
- 📡 [RSS/Atom 订阅源](https://openai.com/news/rss.xml)：`https://openai.com/news/rss.xml`
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [Itaú 如何为全部客户打造生成式 AI](https://openai.com/index/itau-generative-ai)（2026-10-16）
  2. [Benefit Street Partners 通过 Codex 更快地回答问题](https://openai.com/index/benefit-street-partners)（2026-10-16）
  3. [Stack Overflow for Agents 靠 ChatGPT plugin 让注册量增至三倍](https://openai.com/index/stack-overflow-chatgpt-plugin)（2026-10-16）
  4. [把 GPT‑Rosalind 带进学术研究实验室](https://openai.com/index/introducing-the-rosalind-academic-plan)（2026-10-15）
  5. [通过提问教学生思考与学习](https://openai.com/index/teaching-students-to-think-and-learn-through-questions)（2026-10-15）
  - 📄 完整文章归档（共 1298 篇）：[openai.md](llm-news/openai.md)

### Google Gemini (Google AI Studio) (google_gemini)
- 页面：[变更日志](https://ai.google.dev/gemini-api/docs/changelog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-google_gemini.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-google_gemini.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [Gemini 4 Argon (gemini-4-argon) 正式版 (GA)](https://ai.google.dev/gemini-api/docs/changelog?hl=zh-cn#10-13-2026)（2026-10-13）
  2. [Gemini 3.7 Flash 弃用](https://ai.google.dev/gemini-api/docs/changelog?hl=zh-cn#10-08-2026)（2026-10-08）
  3. [Gemini 3.5 Flash 弃用](https://ai.google.dev/gemini-api/docs/changelog?hl=zh-cn#10-08-2026)（2026-10-08）
  4. [Deep Research 智能体 deep-research-pro-preview-12-2025 弃用](https://ai.google.dev/gemini-api/docs/changelog?hl=zh-cn#10-08-2026)（2026-10-08）
  5. [Gemini Nano Banana 2.1 正式版 (GA)](https://ai.google.dev/gemini-api/docs/changelog?hl=zh-cn#10-06-2026)（2026-10-06）
  - 📄 完整文章归档（共 48 篇）：[google_gemini.md](llm-news/google_gemini.md)

### DeepSeek (深度求索) (deepseek)
- 页面：[更新日志](https://api-docs.deepseek.com/zh-cn/updates/)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 页面：[版本动态](https://api-docs.deepseek.com/zh-cn/news/news260424/)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-deepseek.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-deepseek.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [开放自研搜索 API](https://api-docs.deepseek.com/zh-cn/updates/#%E6%97%B6%E9%97%B4-2026-10-17)（2026-10-17）
  2. [DeepSeek-V4.1-Flash 发布](https://api-docs.deepseek.com/zh-cn/updates/#%E6%97%B6%E9%97%B4-2026-09-10)（2026-09-10）
  3. [DeepSeek V4.1 Flash：更强、更快、更普惠](https://api-docs.deepseek.com/zh-cn/news/news260910)（2026-09-10）
  4. [DeepSeek-V4-Flash-Vision-Exp 发布](https://api-docs.deepseek.com/zh-cn/updates/#%E6%97%B6%E9%97%B4-2026-08-21)（2026-08-21）
  5. [V4-Flash-Vision-Exp 上线，开启多模态 API 服务](https://api-docs.deepseek.com/zh-cn/news/news260821)（2026-08-21）
  - 📄 完整文章归档（共 47 篇）：[deepseek.md](llm-news/deepseek.md)

### 通义千问 (阿里云) (aliyun_qwen)
- 页面：[研究页](https://qwen.ai/research)
  - 🔌 官方未提供 RSS/Atom 订阅源，条目取自官方数据接口
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-aliyun_qwen.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-aliyun_qwen.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [Qwen-Image-2.1：小模强效，创改一体](https://qwen.ai/blog?id=qwen-image-2.1)（2026-09-20）
  2. [Qwen3.8-Omni-Flash：耳聪目明，办事得力](https://qwen.ai/blog?id=qwen3.8-omni-flash)（2026-09-18）
  3. [Qwen3.8-LiveTranslate：知其人，传其义](https://qwen.ai/blog?id=qwen3.8-livetranslate)（2026-09-18）
  4. [Qwen-Drive-1.0：迈向自动驾驶视觉-语言基础模型的初步探索](https://qwen.ai/blog?id=qwen-drive-1.0)（2026-09-03）
  5. [E-Commerce Bench：长程经营，多维评估](https://qwen.ai/blog?id=e-commerce-bench)（2026-09-03）
  - 📄 完整文章归档（共 40 篇）：[aliyun_qwen.md](llm-news/aliyun_qwen.md)

### 智谱 GLM (zhipu_glm)
- 页面：[更新日志](https://docs.bigmodel.cn/cn/update/new-releases)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-zhipu_glm.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-zhipu_glm.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [GLM-5.3-Flash 原生多模态模型上线](https://docs.bigmodel.cn/cn/update/new-releases#2026-08-26)（2026-08-26）
  2. [GLM-5.3 新一代旗舰模型上线](https://docs.bigmodel.cn/cn/update/new-releases#2026-8-19)（2026-08-19）
  3. [GLM-5.2 新一代旗舰模型上线](https://docs.bigmodel.cn/cn/update/new-releases#2026-06-16)（2026-06-16）
  4. [GLM Coding Plan 团队版上线](https://docs.bigmodel.cn/cn/update/new-releases#2026-05-29)（2026-05-29）
  5. [GLM-5.1 新一代旗舰模型上线](https://docs.bigmodel.cn/cn/update/new-releases#2026-04-07)（2026-04-07）
  - 📄 完整文章归档（共 26 篇）：[zhipu_glm.md](llm-news/zhipu_glm.md)

### Kimi (月之暗面) (moonshot_kimi)
- 页面：[变更日志](https://platform.kimi.com/docs/changelog/changelog/changelog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-moonshot_kimi.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-moonshot_kimi.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [🤖 Kimi 托管智能体（Hosted Agents）Beta 上线在模型推理 API 之上，我们封装了 Kimi Durable Harness，为企业提供 7x24 小时全托管的智能体运行环境——无需自建沙箱与会话基础设施，就能让 Agent 高质量、可持续地执行长程任务。](https://platform.kimi.com/docs/changelog#2026%E5%B9%B49%E6%9C%88)（2026-09-01）
  2. [kimi-k2.5 与 moonshot-v1 全系列模型（含 -vision-preview、moonshot-v1-auto）已于今日 16:00 在国内外全平台下线，调用将返回 404 错误（模型不存在），请迁移至 Kimi K3](https://platform.kimi.com/docs/changelog/changelog/changelog#2026%E5%B9%B48%E6%9C%8831%E6%97%A5)（2026-08-31）
  3. [kimi-k2.5 与 moonshot-v1 全系列模型（含 -vision-preview、moonshot-v1-auto）在国内外全平台下线，调用将返回 404 错误，请迁移至 Kimi K3](https://platform.kimi.com/docs/changelog#2026%E5%B9%B48%E6%9C%88)（2026-08-01）
  4. [🚀 Kimi K3 上线开放平台 APIKimi 面向长程编程与端到端知识工作的旗舰模型 K3 正式通过开放平台 API 提供，1M token 上下文，综合智能达到领先水平。详见 Kimi K3 快速开始。同期 kimi-k2.5 和 moonshot-v1 系列停止向新注册用户开放。账户概览新增当日实时消费金额展示，平台服务协议同步更新。](https://platform.kimi.com/docs/changelog#2026%E5%B9%B47%E6%9C%88)（2026-07-01）
  5. [支持组织级 API IP 白名单配置，企业安全管控更精细](https://platform.kimi.com/docs/changelog#2026%E5%B9%B46%E6%9C%88)（2026-06-01）
  - 📄 完整文章归档（共 26 篇）：[moonshot_kimi.md](llm-news/moonshot_kimi.md)

### xAI Grok (xai_grok)
- 页面：[新闻 / 更新](https://x.ai/news)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-xai_grok.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-xai_grok.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [推出 Grok Voice 3.0](https://x.ai/news/grok-voice-3)（2026-10-14）
  2. [X 订阅简介](https://x.ai/news/x-subscription)（2026-10-12）
  3. [团队机器人：共享人工智能队友，边工作边学习](https://x.ai/news/team-bots)（2026-09-28）
  4. [SpaceXAI 如何用 Grok Bot 扩展客户支持](https://x.ai/news/grok-bot-customer-support)（2026-09-22）
  5. [介绍 Grok 4.7](https://x.ai/news/grok-4-7)（2026-09-21）
  - 📄 完整文章归档（共 113 篇）：[xai_grok.md](llm-news/xai_grok.md)

### MiniMax (稀宇科技) (minimax)
- 页面：[更新日志](https://platform.minimax.cn/docs/release-notes/models)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 页面：[更新日志](https://platform.minimax.cn/docs/release-notes/apis)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 页面：[官方博客](https://www.minimax.cn/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-minimax.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-minimax.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [MiniMax Music 3.0：新一代开放权重、生产级全能音乐模型](https://www.minimax.cn/blog/minimax-music-3-0-cn)（2026-08-13）
  2. [MiniMax H3](https://platform.minimax.cn/docs/release-notes/models#2026-%E5%B9%B4-7-%E6%9C%88-31-%E6%97%A5)（2026-07-31）
  3. [MiniMax H3：打破任务和模态的边界](https://www.minimax.cn/blog/minimax-h3)（2026-07-31）
  4. [Music-3.0](https://platform.minimax.cn/docs/release-notes/models#2026-%E5%B9%B4-7-%E6%9C%88-16-%E6%97%A5)（2026-07-16）
  5. [MaxProof: 生成式验证强化学习驱动的数学证明进化系统](https://www.minimax.cn/blog/minimax-maxproof-math-proof-evolution)（2026-06-09）
  - 📄 完整文章归档（共 48 篇）：[minimax.md](llm-news/minimax.md)

### Mistral AI (mistral)
- 页面：[新闻 / 更新](https://mistral.ai/news/)
  - 📡 RSS/Atom：https://mistral.ai/news/rss
- 📡 [RSS/Atom 订阅源](https://mistral.ai/news/rss)：`https://mistral.ai/news/rss`
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [推出 Timestral](https://mistral.ai/news/timestral/)（2026-10-15）
  2. [推出 Mistral Large 4](https://mistral.ai/news/mistral-large-4/)（2026-10-06）
  3. [你好，德国！](https://mistral.ai/news/hallo-deutschland/)（2026-09-28）
  4. [Mistral 与 Mozilla 把开放、私密、多语言的 AI 带进你的浏览器](https://mistral.ai/news/mistral-x-mozilla/)（2026-09-16）
  5. [Cloudera 与 Mistral 合作，为企业数据带来专业化、主权的智能](https://mistral.ai/news/mistral-x-cloudera/)（2026-09-10）
  - 📄 完整文章归档（共 90 篇）：[mistral.md](llm-news/mistral.md)

### Groq Cloud (LPU 推理) (groq)
- 页面：[变更日志](https://console.groq.com/docs/changelog.md)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-groq.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-groq.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [2026 年第一季度变更日志条目](https://github.com/groq/groq-changelog/commit/abaa8395286b622a837adb5d6b44709845d1edba)（2026-05-06）
  2. [MiniMax M2.5 与 Qwen3-VL 32B Instruct（企业版）](https://console.groq.com/docs/changelog.md#minimax-m25-and-qwen3vl-32b-instruct-enterprise)（2026-04-18）
  3. [Orpheus Arabic Saudi 新增语音](https://console.groq.com/docs/changelog.md#new-voices-for-orpheus-arabic-saudi)（2026-04-18）
  4. [Python SDK v1.2.0 与 TypeScript SDK v1.1.2](https://console.groq.com/docs/changelog.md#python-sdk-v120-and-typescript-sdk-v112)（2026-04-18）
  5. [Groq 率先将 NVIDIA Groq 3 LPX 与 Vera Rubin NVL72 推向市场](https://groq.com/blog/groq-among-the-first-to-bring-nvidia-groq-3-lpx-and-vera-rubin-nvl72-to-market)（2026-03-24）
  - 📄 完整文章归档（共 68 篇）：[groq.md](llm-news/groq.md)

### 小米 MiMo (xiaomi_mimo)
- 页面：[更新日志](https://mimo.mi.com/docs/zh-CN/updates/model)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 页面：[更新日志](https://mimo.mi.com/docs/zh-CN/updates/feature/platform)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 页面：[更新日志](https://mimo.mi.com/docs/zh-CN/news)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-xiaomi_mimo.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-xiaomi_mimo.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [2026-09-22 MiMo-V2.6 系列发布](https://mimo.mi.com/docs/zh-CN/updates/model#2026-09-22-mimo-v26-%E7%B3%BB%E5%88%97%E5%8F%91%E5%B8%83)（2026-09-22）
  2. [2026-9-22 批量推理（Batch API） & 团队版 TokenPlan 功能上线](https://mimo.mi.com/docs/zh-CN/updates/feature/platform#2026-9-22--%E6%89%B9%E9%87%8F%E6%8E%A8%E7%90%86batch-api--%E5%9B%A2%E9%98%9F%E7%89%88-tokenplan-%E5%8A%9F%E8%83%BD%E4%B8%8A%E7%BA%BF)（2026-09-22）
  3. [2026-9-22 批量推理（Batch API）功能上线](https://mimo.mi.com/docs/zh-CN/updates/feature/platform#2026-9-22--%E6%89%B9%E9%87%8F%E6%8E%A8%E7%90%86batch-api%E5%8A%9F%E8%83%BD%E4%B8%8A%E7%BA%BF)（2026-09-22）
  4. [2026-9-15 新增站内信功能](https://mimo.mi.com/docs/zh-CN/updates/feature/platform#2026-9-15--%E6%96%B0%E5%A2%9E%E7%AB%99%E5%86%85%E4%BF%A1%E5%8A%9F%E8%83%BD)（2026-09-15）
  5. [2026-6-23 支持 OpenAI Responses API](https://mimo.mi.com/docs/zh-CN/updates/feature/platform#2026-6-23-%E6%94%AF%E6%8C%81-openai-responses-api)（2026-06-23）
  - 📄 完整文章归档（共 39 篇）：[xiaomi_mimo.md](llm-news/xiaomi_mimo.md)

### 腾讯云混元 (TokenHub) (tencent_hunyuan)
- 页面：[更新日志](https://cloud.tencent.com/document/product/1729/97765)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-tencent_hunyuan.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-tencent_hunyuan.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [混元旧版本模型正式下线，下线模型不再提供服务，建议迁移至 TokenHub 使用最新版本模型](https://cloud.tencent.com/document/product/1729/97765#t2026-06-22-0)（2026-06-22）
  2. [基于文本 TurboS 基座生成图生文快思考模型，相比上一版本在图像基础识别、图像分析推理等维度都有明显的效果提升](https://cloud.tencent.com/document/product/1729/97765#t2025-12-17-1)（2025-12-17）
  3. [发布特性：1. 模型底座从 TurboS 升级为混元2.0，模型能力全面提升](https://cloud.tencent.com/document/product/1729/97765#t2025-11-11-3)（2025-11-11）
  4. [发布特性：1. 模型底座从 TurboS 升级为混元2.0，模型能力全面提升](https://cloud.tencent.com/document/product/1729/97765#t2025-11-09-2)（2025-11-09）
  5. [支持语种齐全，33种语种互译和5种民族语言互译](https://cloud.tencent.com/document/product/1729/97765#t2025-10-14-4)（2025-10-14）
  - 📄 完整文章归档（共 95 篇）：[tencent_hunyuan.md](llm-news/tencent_hunyuan.md)

### Hugging Face (Inference Providers) (huggingface)
- 页面：[官方博客](https://huggingface.co/blog)
  - 📡 RSS/Atom：https://huggingface.co/blog/feed.xml
- 📡 [RSS/Atom 订阅源](https://huggingface.co/blog/feed.xml)：`https://huggingface.co/blog/feed.xml`
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [Indic 预训练规模化：2.8 万亿 token 与开放的数据生成流水线](https://huggingface.co/blog/nvidia/scaling-indic-pretraining)（2026-10-16）
  2. [欢迎 Beam：一个你可以拥有、定制并规模化的 501B 开放模型](https://huggingface.co/blog/reflection-beam)（2026-10-16）
  3. [Granite Switch 4.1：一个 endpoint 同时提供聊天、决策与语音](https://huggingface.co/blog/ibm-granite/granite-switch-4-1)（2026-10-15）
  4. [欢迎 Muse Spark Open：来自 Meta 的开放权重前沿多模态混合专家模型](https://huggingface.co/blog/meta-muse-spark-open)（2026-10-15）
  5. [Diffusers 迎来 FLUX.3 Image Klein：来自 Black Forest Labs 的最新开源图像生成模型](https://huggingface.co/blog/flux-3)（2026-10-15）
  - 📄 完整文章归档（共 887 篇）：[huggingface.md](llm-news/huggingface.md)

### OpenRouter (模型统一网关) (openrouter)
- 📡 [RSS/Atom 订阅源](https://openrouter.ai/blog/feed.xml)：`https://openrouter.ai/blog/feed.xml`
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [Private Endpoints：把你的微调模型与算力接入 OpenRouter](https://openrouter.ai/blog/announcements/private-endpoints/)（2026-10-14）
  2. [ElevenLabs 现已上线 OpenRouter](https://openrouter.ai/blog/announcements/elevenlabs-on-openrouter/)（2026-10-07）
  3. [AI 销售智能体如何帮我们的销售团队每月省下 600 小时](https://openrouter.ai/blog/case-studies/how-an-ai-sales-agent-saved-our-sales-team-600-hours-a-month/)（2026-10-07）
  4. [AI 代理的服务器端代码执行工具比较](https://openrouter.ai/blog/insights/server-side-code-execution-tools-for-ai-agents-compared/)（2026-10-05）
  5. [Agent 框架对比：Tool-Calling Schema 的处理](https://openrouter.ai/blog/insights/agent-frameworks-compared-tool-calling-schema-handling/)（2026-10-02）
  - 📄 完整文章归档（共 157 篇）：[openrouter.md](llm-news/openrouter.md)

### Cloudflare Workers AI (cloudflare_workers_ai)
- 📡 [RSS/Atom 订阅源](https://developers.cloudflare.com/workers-ai/changelog/index.xml)：`https://developers.cloudflare.com/workers-ai/changelog/index.xml`
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [Workers AI - GLM-5.2 现已登陆 Workers AI](https://developers.cloudflare.com/workers-ai/changelog/#glm-52-now-available-on-workers-ai)（2026-06-16）
  2. [Workers AI - Moonshot AI Kimi K2.7 Code 现已登陆 Workers AI](https://developers.cloudflare.com/workers-ai/changelog/#moonshot-ai-kimi-k27-code-now-available-on-workers-ai)（2026-06-12）
  3. [Workers AI - 计划中的模型弃用](https://developers.cloudflare.com/workers-ai/changelog/#planned-model-deprecations)（2026-05-08）
  4. [Workers AI - Moonshot AI Kimi K2.6 现已登陆 Workers AI](https://developers.cloudflare.com/workers-ai/changelog/#moonshot-ai-kimi-k26-now-available-on-workers-ai)（2026-04-20）
  5. [Workers AI - Google Gemma 4 26B A4B 现已登陆 Workers AI](https://developers.cloudflare.com/workers-ai/changelog/#google-gemma-4-26b-a4b-now-available-on-workers-ai)（2026-04-04）
  - 📄 完整文章归档（共 35 篇）：[cloudflare_workers_ai.md](llm-news/cloudflare_workers_ai.md)

### Cohere (cohere)
- 页面：[官方博客](https://cohere.com/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-cohere.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-cohere.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [Cohere 将收购 AISLE 以推进抗网络攻击的主权 AI](https://cohere.com/blog/cohere-and-aisle-sign-letter-of-intent-to-advance-cyber-resilient-sovereign-ai)（2026-10-15）
  2. [公用事业的 AI 需要能力，也需要控制](https://cohere.com/blog/ai-for-utilities-requires-capability-and-control)（2026-10-15）
  3. [Agent 蔓延：如何在企业里管理 agent 的激增](https://cohere.com/blog/agent-sprawl)（2026-10-15）
  4. [AI ROI：企业如何衡量 AI 投资的回报](https://cohere.com/blog/ai-roi)（2026-10-15）
  5. [扩展 coding agent 团队的经验教训：用 30% 的成本触达前沿水平](https://cohere.com/blog/lessons-from-scaling-teams-of-frontier-coding-agents)（2026-10-14）
  - 📄 完整文章归档（共 44 篇）：[cohere.md](llm-news/cohere.md)

### 商汤 日日新 (SenseNova) (sensetime_sensenova)
- 页面：[更新日志](https://www.sensecore.cn/help/docs/model-as-a-service/nova/release)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-sensetime_sensenova.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-sensetime_sensenova.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [【模型更新】发布最新版本日日新-融合模态模型SenseNova-V6.5-Pro、SenseNova-V6.5-Turbo](https://www.sensecore.cn/help/docs/model-as-a-service/nova/release#%E6%A8%A1%E5%9E%8B%E6%9B%B4%E6%96%B0%E5%8F%91%E5%B8%83%E6%9C%80%E6%96%B0%E7%89%88%E6%9C%AC%E6%97%A5%E6%97%A5%E6%96%B0-%E8%9E%8D%E5%90%88%E6%A8%A1%E6%80%81%E6%A8%A1%E5%9E%8Bsensenova-v65-prosensenova-v65-turbo)（2025-07-23）
  2. [【模型更新】发布最新版本日日新-语音大模型-语音合成（音色融合）](https://www.sensecore.cn/help/docs/model-as-a-service/nova/release#%E6%A8%A1%E5%9E%8B%E6%9B%B4%E6%96%B0%E5%8F%91%E5%B8%83%E6%9C%80%E6%96%B0%E7%89%88%E6%9C%AC%E6%97%A5%E6%97%A5%E6%96%B0-%E8%AF%AD%E9%9F%B3%E5%A4%A7%E6%A8%A1%E5%9E%8B-%E8%AF%AD%E9%9F%B3%E5%90%88%E6%88%90%E9%9F%B3%E8%89%B2%E8%9E%8D%E5%90%88)（2025-06-03）
  3. [【模型更新】发布最新版本日日新-融合模态模型SenseNova-V6-Pro、SenseNova-V6-Reasoner、SenseNova-V6-Turbo](https://www.sensecore.cn/help/docs/model-as-a-service/nova/release#%E6%A8%A1%E5%9E%8B%E6%9B%B4%E6%96%B0%E5%8F%91%E5%B8%83%E6%9C%80%E6%96%B0%E7%89%88%E6%9C%AC%E6%97%A5%E6%97%A5%E6%96%B0-%E8%9E%8D%E5%90%88%E6%A8%A1%E6%80%81%E6%A8%A1%E5%9E%8Bsensenova-v6-prosensenova-v6-reasonersensenova-v6-turbo)（2025-04-09）
  4. [【模型更新】发布最新版本日日新-大语言模型SenseChat-5-1202、SenseChat-Turbo-1202](https://www.sensecore.cn/help/docs/model-as-a-service/nova/release#%E6%A8%A1%E5%9E%8B%E6%9B%B4%E6%96%B0%E5%8F%91%E5%B8%83%E6%9C%80%E6%96%B0%E7%89%88%E6%9C%AC%E6%97%A5%E6%97%A5%E6%96%B0-%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8Bsensechat-5-1202sensechat-turbo-1202)（2024-12-30）
  5. [【功能更新】OpenAPI全面支持通过API Key调用](https://www.sensecore.cn/help/docs/model-as-a-service/nova/release#%E5%8A%9F%E8%83%BD%E6%9B%B4%E6%96%B0openapi%E5%85%A8%E9%9D%A2%E6%94%AF%E6%8C%81%E9%80%9A%E8%BF%87api-key%E8%B0%83%E7%94%A8)（2024-10-30）
  - 📄 完整文章归档（共 18 篇）：[sensetime_sensenova.md](llm-news/sensetime_sensenova.md)

### Meta Llama (开源权重) (meta_llama)
- 页面：[官方博客](https://ai.meta.com/blog/)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 [RSS/Atom 订阅源](https://about.fb.com/news/tag/ai/feed/)：`https://about.fb.com/news/tag/ai/feed/`
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [隆重推出 Muse Wonder 和 Muse Wonder Full：面向智能体的前沿模型](https://about.fb.com/news/2026/10/introducing-muse-wonder-models/)（2026-10-12）
  2. [辟谣：关于数据中心的最大迷思](https://about.fb.com/news/2026/10/debunking-the-biggest-data-center-myths/)（2026-10-08）
  3. [为什么数据中心是 Meta AI 战略的重要一环](https://about.fb.com/news/2026/10/meta-data-centers-ai-approach/)（2026-10-07）
  4. [未来属于每个人：面向小企业的 Muse](https://about.fb.com/news/2026/09/introducing-muse-small-business/)（2026-09-29）
  5. [推出 Meta Enterprise Platform（Meta 企业平台）](https://about.fb.com/news/2026/09/launching-meta-enterprise-platform/)（2026-09-28）
  - 📄 完整文章归档（共 24 篇）：[meta_llama.md](llm-news/meta_llama.md)

### 美团 LongCat (longcat_meituan)
- 页面：[更新日志](https://longcat.chat/platform/docs/zh/ChangeLog.html)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-longcat_meituan.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-longcat_meituan.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [LongCat-2.5-Preview 上线](https://longcat.chat/platform/docs/zh/ChangeLog.html#%E7%89%88%E6%9C%AC-2026-09-25)（2026-09-25）
  2. [全新推出企业服务](https://longcat.chat/platform/docs/zh/ChangeLog.html#%E7%89%88%E6%9C%AC-2026-09-10)（2026-09-10）
  3. [全新推出企业服务](https://longcat.chat/platform/docs/zh/ChangeLog.html#%E7%89%88%E6%9C%AC-2026-09-02)（2026-09-02）
  4. [LongCat-2.0 发布 & 全新推出计费服务](https://longcat.chat/platform/docs/zh/ChangeLog.html#%E7%89%88%E6%9C%AC-2026-06-30)（2026-06-30）
  5. [LongCat 部分模型服务下线](https://longcat.chat/platform/docs/zh/ChangeLog.html#%E7%89%88%E6%9C%AC-2026-05-29)（2026-05-29）
  - 📄 完整文章归档（共 14 篇）：[longcat_meituan.md](llm-news/longcat_meituan.md)

### 硅基流动 (SiliconFlow) (siliconflow)
- 页面：[更新日志](https://docs.siliconflow.cn/cn/release-notes/overview)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-siliconflow.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-siliconflow.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [【模型服务调整】ERNIE-Image-Turbo 模型将下线](https://docs.siliconflow.cn/docs/release-notes/overview#%E6%A8%A1%E5%9E%8B%E6%9C%8D%E5%8A%A1%E8%B0%83%E6%95%B4ernie-image-turbo-%E6%A8%A1%E5%9E%8B%E5%B0%86%E4%B8%8B%E7%BA%BF)（2026-10-17）
  2. [【模型服务调整】systemone 接口 diffusiongemma 模型将停止服务](https://docs.siliconflow.cn/docs/release-notes/overview#%E6%A8%A1%E5%9E%8B%E6%9C%8D%E5%8A%A1%E8%B0%83%E6%95%B4systemone-%E6%8E%A5%E5%8F%A3-diffusiongemma-%E6%A8%A1%E5%9E%8B%E5%B0%86%E5%81%9C%E6%AD%A2%E6%9C%8D%E5%8A%A1)（2026-10-16）
  3. [【接口服务调整】对话模型将忽略 repetition_penalty 参数](https://docs.siliconflow.cn/docs/release-notes/overview#%E6%8E%A5%E5%8F%A3%E6%9C%8D%E5%8A%A1%E8%B0%83%E6%95%B4%E5%AF%B9%E8%AF%9D%E6%A8%A1%E5%9E%8B%E5%B0%86%E5%BF%BD%E7%95%A5-repetition_penalty-%E5%8F%82%E6%95%B0)（2026-09-30）
  4. [【模型服务调整】Nex-N2-Pro、Qwen3.5-397B-A17B、MiniMax-M2.5 等模型将下线](https://docs.siliconflow.cn/docs/release-notes/overview#%E6%A8%A1%E5%9E%8B%E6%9C%8D%E5%8A%A1%E8%B0%83%E6%95%B4nex-n2-proqwen35-397b-a17bminimax-m25-%E7%AD%89%E6%A8%A1%E5%9E%8B%E5%B0%86%E4%B8%8B%E7%BA%BF)（2026-09-30）
  5. [【接口服务调整】生图 API 下线 batch_size 字段、水印默认添加](https://docs.siliconflow.cn/docs/release-notes/overview#%E6%8E%A5%E5%8F%A3%E6%9C%8D%E5%8A%A1%E8%B0%83%E6%95%B4%E7%94%9F%E5%9B%BE-api-%E4%B8%8B%E7%BA%BF-batch_size-%E5%AD%97%E6%AE%B5%E6%B0%B4%E5%8D%B0%E9%BB%98%E8%AE%A4%E6%B7%BB%E5%8A%A0)（2026-09-15）
  - 📄 完整文章归档（共 49 篇）：[siliconflow.md](llm-news/siliconflow.md)

### StreamLake (快手万擎) (streamlake)
- 页面：[更新日志](https://www.streamlake.com/document/WANQING/mdptalisb06i7ai3zdd)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-streamlake.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-streamlake.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [【新增】数据分析任务完成后可将结果下载至本地，便于进一步处理与留存数据](https://www.streamlake.com/document/WANQING/mdptalisb06i7ai3zdd#t2026-08-14-0)（2026-08-14）
  2. [【新增】新增 Python 代码节点，支持灵活编写自定义处理逻辑，满足个性化数据加工需求](https://www.streamlake.com/document/WANQING/mdptalisb06i7ai3zdd#t2026-07-22-1)（2026-07-22）
  3. [【新增】新增 GLM-5.2-FP8 模型部署能力，支持预付费、后付费模式，丰富模型部署选择](https://www.streamlake.com/document/WANQING/mdptalisb06i7ai3zdd#t2026-07-03-2)（2026-07-03）
  4. [【优化】文本生成模型推理点监控新增缓存命中率曲线，支持 Cache命中率及 Cache token 数量等指标](https://www.streamlake.com/document/WANQING/mdptalisb06i7ai3zdd#t2026-07-03-3)（2026-07-03）
  5. [【优化】推理监控输入输出token卡片增加影响因子数据，用户可直接查看因子维度token消耗](https://www.streamlake.com/document/WANQING/mdptalisb06i7ai3zdd#t2026-06-30-4)（2026-06-30）
  - 📄 完整文章归档（共 23 篇）：[streamlake.md](llm-news/streamlake.md)

### 数眼智能 (数言 AI / ShuyanAI) (dataeye)
- 页面：[官方博客](https://www.shuyanai.com/blogs)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-dataeye.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-dataeye.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [从开发验证到核心生产：数眼智能如何以 ≧99.95% 可用率与多级 SLA 通道护航企业 AI 业务？](https://www.shuyanai.com/blogs/32)（2026-10-15）
  2. [数眼智能完成数千万元天使轮融资，加速企业级大模型部署能力建设](https://www.shuyanai.com/blogs/31)（2026-09-21）
  3. [数眼智能AI漫剧教程：从脚本、AI生图到Seedance 2.5生视频](https://www.shuyanai.com/blogs/30)（2026-09-17）
  4. [数眼智能 AI 视频生成教程：如何用智能体生成第一条视频？](https://www.shuyanai.com/blogs/29)（2026-09-16）
  5. [数眼智能在海南数据谷OPC社区揭牌现场｜把 Token 级算力，送到每一个 AI 超级个体手里](https://www.shuyanai.com/blogs/28)（2026-09-16）
  - 📄 完整文章归档（共 17 篇）：[dataeye.md](llm-news/dataeye.md)

### Amazon Bedrock (AWS Free Tier) (aws_bedrock)
- 📡 [RSS/Atom 订阅源](https://aws.amazon.com/blogs/machine-learning/feed/)：`https://aws.amazon.com/cn/blogs/machine-learning/feed/`
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [建立对 AI 智能体的信任：基于 Amazon Bedrock AgentCore 的生产级评测框架](https://aws.amazon.com/blogs/machine-learning/building-trust-in-ai-agents-a-production-ready-evaluation-framework-with-amazon-bedrock-agentcore/)（2026-10-16）
  2. [Reflection Beam 发布：面向 AWS 上智能体编码的开放权重模型](https://aws.amazon.com/blogs/machine-learning/introducing-reflection-beam-an-open-weight-model-for-agentic-coding-on-aws/)（2026-10-16）
  3. [Meta 的 Muse Spark Open 现已在 Amazon SageMaker JumpStart 上线](https://aws.amazon.com/blogs/machine-learning/metas-muse-spark-open-now-available-in-amazon-sagemaker-jumpstart/)（2026-10-15）
  4. [纵深信任：给 agent 更多自主权，同时不失去控制](https://aws.amazon.com/blogs/machine-learning/trust-in-depth-giving-agents-more-autonomy-without-losing-control/)（2026-10-15）
  5. [使用 Amazon Bedrock AgentCore 构建自我改进的文档处理](https://aws.amazon.com/blogs/machine-learning/build-self-improving-document-processing-using-amazon-bedrock-agentcore/)（2026-10-14）
  - 📄 完整文章归档（共 86 篇）：[aws_bedrock.md](llm-news/aws_bedrock.md)

### Cerebras Inference (晶圆级推理) (cerebras)
- 页面：[官方博客](https://www.cerebras.ai/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-cerebras.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-cerebras.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [发布 Cerebras CS-4：最快的 AI 再次提速](https://www.cerebras.ai/blog/introducing-cerebras-cs-4)
  2. [MoE 规模化：让稀疏模型在真实硬件上跑得快](https://www.cerebras.ai/blog/moe-guide-scale)
  3. [MoE 数学揭秘：8x7B 到底是什么意思？](https://www.cerebras.ai/blog/moe-guide-calculator)
  4. [从头开始的分类推理](https://www.cerebras.ai/blog/disaggregated-inference-from-the-ground-up)
  5. [AlphaSense 如何用快速推理让 Agentic 研究变得可交互](https://www.cerebras.ai/blog/how-alphasense-uses-fast-inference-to-make-agentic-research-interactive)
  - 📄 完整文章归档（共 54 篇）：[cerebras.md](llm-news/cerebras.md)

### Together AI (together_ai)
- 📡 [RSS/Atom 订阅源](https://www.together.ai/blog/rss.xml)：`https://www.together.ai/blog/rss.xml`
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [Meta Muse Spark Open 已在 Together AI 上线](https://www.together.ai/blog/meta-muse-spark-open)（2026-10-15）
  2. [与 IBM Cloud 和 NVIDIA 合作，扩展我们的企业推理容量](https://www.together.ai/blog/expanding-our-enterprise-inference-capacity-with-ibm-cloud-and-nvidia)（2026-10-06）
  3. [Together Link：在你已在用的 harness 中用上前沿品质的开放模型](https://www.together.ai/blog/together-link-frontier-quality-open-models-in-the-harness-you-already-use)（2026-10-05）
  4. [花 17 美元训练你自己的 Jev](https://www.together.ai/blog/how-to-train-your-own-jev)（2026-09-23）
  5. [金丝雀发布：在生产环境中零停机升级模型](https://www.together.ai/blog/canary-rollouts-upgrade-models-in-production-without-downtime)（2026-09-22）
  - 📄 完整文章归档（共 84 篇）：[together_ai.md](llm-news/together_ai.md)

### Fireworks AI (fireworks_ai)
- 页面：[官方博客](https://fireworks.ai/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-fireworks_ai.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-fireworks_ai.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [强化学习：为什么数值与 MoE 路由的对齐如此重要](https://fireworks.ai/blog/reinforcement-learning-why-alignment-of-numerics-and-MoE-routing-matter)
  2. [深入 Fireworks 多区域部署：一个部署，全球规模](https://fireworks.ai/blog/multi-region-deployment)
  3. [每个字节都算数：ARCv3 与跨区域 RL 的必要性](https://fireworks.ai/blog/arcv3-and-the-case-for-cross-region-rl)
  4. [Ember-1 发布](https://fireworks.ai/blog/ember-1)
  5. [Specialized Intelligence Index 正式发布](https://fireworks.ai/blog/introducing-the-specialized-intelligence-index)
  - 📄 完整文章归档（共 24 篇）：[fireworks_ai.md](llm-news/fireworks_ai.md)

### DeepInfra (deepinfra)
- 页面：[官方博客](https://deepinfra.com/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-deepinfra.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-deepinfra.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [IBM Granite 4.2 8B Now Available on DeepInfra](https://deepinfra.com/blog/imb-granite-4-2)（2026-10-17）
  2. [开放权重模型的许可证：上线前该查哪些条款](https://deepinfra.com/blog/open-weight-model-licenses)（2026-10-16）
  3. [TypeSafe Jev 评测：在一个非聊天模型上测试 5 项任务](https://deepinfra.com/blog/typesafe-jev-review)（2026-10-15）
  4. [AI 支出审计：如何用开放模型削减成本](https://deepinfra.com/blog/ai-spend-audit-open-models)（2026-10-15）
  5. [从截图到 tool call：DeepInfra 上的 NVIDIA Nemotron 3.5 Super VL](https://deepinfra.com/blog/nvidia-nemotron-3-5-super-vl-release)（2026-10-15）
  - 📄 完整文章归档（共 36 篇）：[deepinfra.md](llm-news/deepinfra.md)

### Modular (原 BentoCloud/BentoML) (modular_cloud)
- 📡 [RSS/Atom 订阅源](https://www.modular.com/blog/rss.xml)：`https://www.modular.com/blog/rss.xml`
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [培育 Modular 生态：Modular 社区资助计划](https://www.modular.com/blog/nurturing-the-modular-ecosystem-the-modular-community-grant-program)（2026-10-09）
  2. [Modular 26.6：开放编译器贡献、音频生成与扩展模型支持](https://www.modular.com/blog/modular-26-6-open-compiler-contributions-audio-generation-and-expanded-model-support)（2026-09-17）
  3. [Mojo🔥 现已开源！](https://www.modular.com/blog/mojo-open-source)（2026-08-18）
  4. [Modular 与高通：相同的代码，新的芯片](https://www.modular.com/blog/modcon-qualcomm)（2026-08-18）
  5. [ModCon 2026：开源、开放云、开放硅](https://www.modular.com/blog/modcon-announcements)（2026-08-18）
  - 📄 完整文章归档（共 101 篇）：[modular_cloud.md](llm-news/modular_cloud.md)

### AI21 Labs (ai21_labs)
- 页面：[官方博客](https://www.ai21.com/blog)
  - 🔌 官方未提供 RSS/Atom 订阅源，条目取自官方数据接口
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-ai21_labs.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-ai21_labs.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [与 NVIDIA、Gong、Deel 和 Alice 合作，后训练 Nemotron 3.5 Super](https://www.ai21.com/blog/ai21-post-trains-nvidia-nemotron-35-super-vl/)（2026-10-15）
  2. [隐藏的错配：在开发者真正做的工作上评估 coding agent](https://www.ai21.com/blog/evaluating-coding-agents-on-the-work-developers-actually-do/)（2026-10-14）
  3. [智能体设计的可验证性试金石](https://www.ai21.com/blog/the-verifiability-litmus-test-for-agent-design/)（2026-10-06）
  4. [从人工协商到自动调度：AI21 如何用 Kueue 管理其 GPU 集群](https://www.ai21.com/blog/how-ai21-manages-its-gpu-fleet-with-kueue/)（2026-10-04）
  5. [你不需要前沿模型，你需要一个校验器](https://www.ai21.com/blog/you-need-a-verifier/)（2026-08-19）
  - 📄 完整文章归档（共 70 篇）：[ai21_labs.md](llm-news/ai21_labs.md)

### Jina AI (Reader / Embeddings / Reranker) (jina_ai)
- 页面：[官方博客](https://jina.ai/news/)
  - 📡 RSS/Atom：https://jina.ai/feed.rss
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [jina-embeddings-v5-omni：文本、图像、音频与视频嵌入：一个模型覆盖四种模态（文本、图像、音频、视频），1.6B 与 0.9B 均为同类最优的全模态嵌入](https://jina.ai/news/jina-embeddings-v5-omni-multimodal-embeddings-for-text-image-audio-and-video)（2026-05-12）
  2. [从多模态 LLM 自举音频嵌入：把任意多模态 LLM 变成小型音频嵌入模型，数据量少 25 倍即可超越 CLAP](https://jina.ai/news/bootstrapping-audio-embeddings-from-multimodal-llms)（2026-03-11）
  3. [从原始数值识别嵌入模型：读原始数字即可为嵌入模型留指纹的微型 transformer，无需特征工程](https://jina.ai/news/identifying-embedding-models-from-raw-numerical-values)（2026-03-06）
  4. [Jina-VLM：小型多语言视觉语言模型：全新 2B 视觉语言模型在多语言 VQA 上达到 SOTA，纯文本任务不出现灾难性遗忘](https://jina.ai/news/jina-vlm-small-multilingual-vision-language-model)（2025-12-04）
  5. [在 Llama.cpp 与 GGUF 中实现多模态 embedding](https://jina.ai/news/multimodal-embeddings-in-llama-cpp-and-gguf)（2025-09-09）
  - 📄 完整文章归档（共 6 篇）：[jina_ai.md](llm-news/jina_ai.md)

### Poolside (poolside)
- 页面：[官方博客](https://poolside.ai/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-poolside.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-poolside.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [Poolside on Dell：在您的边界内实现前沿人工智能的有效途径](https://poolside.ai/blog/poolside-on-dell)（2026-07-28）
  2. [推出 Laguna XS 2.1](https://poolside.ai/blog/introducing-laguna-xs-2-1)（2026-07-21）
  3. [长上下文更新：Laguna XS.2 和 M.1](https://poolside.ai/blog/long-context-update-laguna-xs-2-and-m-1)（2026-07-02）
  4. [AI，你的方式：引入 Poolside 平台](https://poolside.ai/blog/introducing-the-poolside-platform)（2026-05-26）
  5. [Laguna XS.2 和 M.1：深入探讨](https://poolside.ai/blog/laguna-a-deeper-dive)（2026-05-11）
  - 📄 完整文章归档（共 19 篇）：[poolside.md](llm-news/poolside.md)

### Anyscale (anyscale)
- 📡 [RSS/Atom 订阅源](https://www.anyscale.com/rss.xml)：`https://www.anyscale.com/rss.xml`
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [用 KubeRay 在 Kubernetes 上大规模运行 Ray](https://anyscale.com/blog/kuberay)（2026-10-15）
  2. [在 Anyscale 上用 Ray 扩展机器人决策研究的规模](https://anyscale.com/blog/science-of-robot-decisions-ray-anyscale)（2026-10-09）
  3. [编码智能体成本降低 90%：在 Anyscale 上用 Ray + vLLM 安全地提供 LLM 服务](https://anyscale.com/blog/run-coding-agents-on-your-own-gpus)（2026-10-08）
  4. [Anyscale on Azure 正式可用：让企业掌握完整的 AI 闭环，而不只是推理](https://anyscale.com/blog/anyscale-on-azure-general-availability-enterprise-ai)（2026-10-07）
  5. [Ray Summit 2026：物理 AI、RL，以及承载它们的一切基础设施](https://anyscale.com/blog/ray-summit-2026-recap)（2026-09-08）
  - 📄 完整文章归档（共 80 篇）：[anyscale.md](llm-news/anyscale.md)

### InceptionLabs (inception_labs)
- 页面：[官方博客](https://www.inceptionlabs.ai/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-inception_labs.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-inception_labs.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [Mercury 2 入选 TIME 2026 年度最佳发明](https://www.inceptionlabs.ai/blog/mercury-2-named-to-time-s-best-inventions-of-2026)（2026-10-16）
  2. [Mercury Voice 发布](https://www.inceptionlabs.ai/blog/introducing-mercury-voice)（2026-10-01）
  3. [Mercury 2.5 简介](https://www.inceptionlabs.ai/blog/introducing-mercury-2-5)（2026-09-24）
  4. [Mercury 2 用于搜索：快到一次查询可以跑上百次](https://www.inceptionlabs.ai/blog/mercury-2-for-search)
  5. [更多开发者。更高吞吐。更好的 Mercury 2。](https://www.inceptionlabs.ai/blog/mercury-2-10x-free-tokens)
  - 📄 完整文章归档（共 14 篇）：[inception_labs.md](llm-news/inception_labs.md)

### Inference.net (inference_net)
- 页面：[官方博客](https://inference.net/blog/)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-inference_net.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-inference_net.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-18，标题自动汉化）：
  1. [Schematron V2：以极低成本实现前沿级 HTML 转 JSON 提取](https://inference.net/blog/schematron-v2/)（2026-08-05）
  2. [推理平台简介：监控、训练和部署自我改进的 AI 模型](https://inference.net/blog/introducing-inference-platform/)（2026-04-16）
  3. [Inference.net 如何训练专用语言模型，把 AI 成本最多降低 50 倍](https://inference.net/blog/nemotron-finetuning/)（2026-04-14）
  4. [专业LLM：您需要的模型尚不存在](https://inference.net/blog/the-model-you-need-doesnt-exist-yet/)（2026-03-11）
  5. [OSSAS 项目：定制LLM可处理 1 亿篇研究论文](https://inference.net/blog/project-aella/)（2026-02-05）
  - 📄 完整文章归档（共 9 篇）：[inference_net.md](llm-news/inference_net.md)

---
共整理 35 个厂商的动态入口（其中 35 个成功提取最新文章），RSS/Atom 源 15 个。

<!-- LLM-NEWS:END -->
