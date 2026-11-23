# LLM 厂商博客 / 更新动态订阅源

<!-- LLM-NEWS:BEGIN  本章节由 crawler_llm_intel.py 自动生成，请勿手工修改 -->

## 厂商博客 / 更新动态订阅源

> 由 `crawler_llm_intel.py` 自动整理，最近更新：**2026-11-23 10:59:17**。
>
> 各厂商的官方博客、工程文章、更新日志**单独维护在此**，不混入 README 的免费额度情报；
> 每个厂商下方列出从官方 RSS / 博客页**实际抓取的最新文章**（标题自动汉化、附发布日期与原文链接）。
> 主文档每家仅展示**最新 5 篇**；**完整文章归档**按厂商拆分到 [`llm-news/`](llm-news/) 子目录（每厂商一个 `.md`，全量罗列该来源所有文章）。
> 可将同目录下的 `llm-news-feeds.opml` 导入任意 RSS 阅读器（如 Feedly / Inoreader / NetNewsWire / 本地阅读器）统一订阅（原生源 + 本仓库自建源 + 英文镜像，OPML 里分组）。
>
> 📡 **本仓库自建 RSS**：把下方归档直接转成订阅源，**官方没有原生 RSS 的厂商也能订阅**（标题同样已汉化，每日随巡检刷新）：
> - 网页浏览 / 一键订阅：[https://free-llm-intel.aishort.top/](https://free-llm-intel.aishort.top/)（可按厂商筛选、搜索，页脚列出**全部有动态源的厂商**单源）
> - 全部厂商动态（聚合有动态源的全部厂商）：[`llm-news-all.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-all.xml)（最近 100 条，带厂商前缀，可按 `category` 过滤）
> - 英文镜像（全部厂商动态 · 英文）：[`llm-news-all.en.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-all.en.xml)（源语言标题，中文原生源的厂商不出现在这里）
> - 单厂商源：`https://free-llm-intel.aishort.top/feeds/llm-news-{vendor_id}.xml`（最近 50 条；把 `{vendor_id}` 换成下方括号里的厂商 id，如 `llm-news-openai.xml`；英文镜像同名加 `.en.xml`）
> - ⚠️ 全部厂商动态与各厂商单源**内容重叠**，二选一订阅即可（都订会出现重复条目）；中英两版**同时订**会看到同一份新闻各一条（guid 加了 `?li=1` 后缀区分，阅读器不会自动去重）。**建议按语言偏好二选一**。
> - 全部厂商动态只收有日期的条目；要看全量请用浏览页或单厂商源。

### Anthropic Claude (anthropic)
- 页面：[官方博客](https://claude.com/resources/articles)
  - 📡 RSS/Atom：https://claude.com/resources/articles/rss.xml
- 页面：[新闻 / 更新](https://www.anthropic.com/news)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [Anthropic 宣布完成 IPO：承销商全额行使超额配售选择权，同步私募配售亦告完成](https://www.anthropic.com/news/ipo-close)（2026-11-20）
  2. [Anthropic 公布 IPO 发行价](https://www.anthropic.com/news/anthropic-prices-initial-public-offering)（2026-11-18）
  3. [Claude Platform 上的关联计费](https://claude.com/resources/articles/linked-billing-on-claude-platform)（2026-11-17）
  4. [面向初创公司的 Claude Tag 指南](https://claude.com/resources/articles/claude-tag-guide-for-startups)（2026-11-13）
  5. [构建永远在线的 agent](https://claude.com/resources/articles/building-always-on-agents)（2026-11-13）
  - 📄 完整文章归档（共 167 篇）：[anthropic.md](llm-news/anthropic.md)

### OpenAI (openai)
- 页面：[官方博客](https://openai.com/news/)
  - 📡 RSS/Atom：https://openai.com/news/rss.xml
- 页面：[新闻 / 更新](https://openai.com/zh-Hans-CN/news/)
  - 📡 RSS/Atom：https://openai.com/news/rss.xml
- 📡 [官方 RSS](https://openai.com/news/rss.xml)：`https://openai.com/news/rss.xml`
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [Perplexity 与智能](https://openai.com/index/perplexity-and-intelligence)（2026-11-22）
  2. [应对对抗性蒸馏](https://openai.com/index/combatting-adversarial-distillation)（2026-11-20）
  3. [Hebbia 借助 GPT-6 Astra 提升金融研究能力](https://openai.com/business/customer-stories/hebbia)（2026-11-20）
  4. [AI 能否帮助科学家发现有前景的候选药物？](https://openai.com/index/introducing-medchembench)（2026-11-20）
  5. [OpenAI 的 Performance Factory 如何保持 ChatGPT 快速](https://openai.com/index/how-openai-performance-factory-keeps-chatgpt-fast)（2026-11-19）
  - 📄 完整文章归档（共 1419 篇）：[openai.md](llm-news/openai.md)

### Google Gemini (google_gemini)
- 页面：[变更日志](https://aistudio.google.com/docs/changelog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-google_gemini.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-google_gemini.xml)
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [Genie 4 (genie-4) generally available (GA): Released Genie 4 (genie-4) on the Interactions API (v1beta) for real-time interactive world generation, streaming steerable 24 fps 16:9 video with synchron…](https://aistudio.google.com/docs/changelog#11-19-2026)（2026-11-19）
  2. [Gemini 4 Neon (gemini-4-neon) 全面上市 (GA)：发布了 Gemini 4 Neon (gemini-4-neon)，带来前沿级智能，跨复杂的软件工程快速完成端到端任务……](https://aistudio.google.com/docs/changelog#11-18-2026)（2026-11-18）
  3. [Gemini 3.5 Transcribe 中的语音编辑：gemini-3.5-transcribe 和 gemini-3.5-transcribe-live 现在支持语音驱动的编辑、重写和格式化听写语音或预先存在的文本（来源...](https://aistudio.google.com/docs/changelog#11-17-2026)（2026-11-17）
  4. [Gemini 4 Hydrogen (gemini-4-Hydrogen) 全面上市 (GA)：发布了 Gemini 4 Hydrogen (gemini-4-Hydrogen)，为每个人带来尖端智能，为日常生活带来速度和效率……](https://aistudio.google.com/docs/changelog#11-12-2026)（2026-11-12）
  5. [Gemini Decision 1 and the Decisions API: Released Gemini Decision 1 (gemini-decision-1) and the Decisions API for fast, calibrated binary, categorical, and rubric decisions across text, images, audio…](https://aistudio.google.com/docs/changelog#11-11-2026)（2026-11-11）
  - 📄 完整文章归档（共 160 篇）：[google_gemini.md](llm-news/google_gemini.md)

### DeepSeek (deepseek)
- 页面：[更新日志](https://api-docs.deepseek.com/zh-cn/updates/)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 页面：[版本动态](https://api-docs.deepseek.com/zh-cn/news/news260424/)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-deepseek.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-deepseek.xml)
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [发布全家桶应用 API](https://api-docs.deepseek.com/zh-cn/updates/#%E6%97%B6%E9%97%B4-2026-11-13)（2026-11-13）
  2. [DeepSeek 全家桶应用 API 发布](https://api-docs.deepseek.com/zh-cn/news/news261113)（2026-11-13）
  3. [开放自研搜索 API](https://api-docs.deepseek.com/zh-cn/updates/#%E6%97%B6%E9%97%B4-2026-10-17)（2026-10-17）
  4. [DeepSeek-V4.1-Flash-1017 发布](https://api-docs.deepseek.com/zh-cn/news/news261017)（2026-10-17）
  5. [DeepSeek V4.1 Flash：更强、更快、更普惠](https://api-docs.deepseek.com/zh-cn/news/news260910)（2026-09-10）
  - 📄 完整文章归档（共 46 篇）：[deepseek.md](llm-news/deepseek.md)

### 通义千问 (aliyun_qwen)
- 页面：[研究页](https://qwen.ai/research)
  - 🔌 官方未提供 RSS/Atom 订阅源，条目取自官方数据接口
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-aliyun_qwen.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-aliyun_qwen.xml)
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [Qwen4-Max：新同事，已就位](https://qwen.ai/blog?id=qwen4-max)（2026-11-16）
  2. [Qwen-Image-2.1：小模强效，创改一体](https://qwen.ai/blog?id=qwen-image-2.1)（2026-09-20）
  3. [Qwen3.8-Omni-Flash：耳聪目明，办事得力](https://qwen.ai/blog?id=qwen3.8-omni-flash)（2026-09-18）
  4. [Qwen3.8-LiveTranslate：知其人，传其义](https://qwen.ai/blog?id=qwen3.8-livetranslate)（2026-09-18）
  5. [Qwen-Drive-1.0：迈向自动驾驶视觉-语言基础模型的初步探索](https://qwen.ai/blog?id=qwen-drive-1.0)（2026-09-03）
  - 📄 完整文章归档（共 41 篇）：[aliyun_qwen.md](llm-news/aliyun_qwen.md)

### 智谱 GLM (zhipu_glm)
- 页面：[更新日志](https://docs.bigmodel.cn/cn/update/new-releases)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-zhipu_glm.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-zhipu_glm.xml)
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [GLM-5.3-Flash 原生多模态模型上线](https://docs.bigmodel.cn/cn/update/new-releases#2026-08-26)（2026-08-26）
  2. [GLM-5.3 新一代旗舰模型上线](https://docs.bigmodel.cn/cn/update/new-releases#2026-8-19)（2026-08-19）
  3. [GLM-5.2 新一代旗舰模型上线](https://docs.bigmodel.cn/cn/update/new-releases#2026-06-16)（2026-06-16）
  4. [GLM Coding Plan 团队版上线](https://docs.bigmodel.cn/cn/update/new-releases#2026-05-29)（2026-05-29）
  5. [GLM-5.1 新一代旗舰模型上线](https://docs.bigmodel.cn/cn/update/new-releases#2026-04-07)（2026-04-07）
  - 📄 完整文章归档（共 26 篇）：[zhipu_glm.md](llm-news/zhipu_glm.md)

### Kimi (moonshot_kimi)
- 页面：[官方博客](https://www.kimi.com/blog/)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-moonshot_kimi.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-moonshot_kimi.xml)
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [Kimi K3.1 Pro](https://www.kimi.com/blog/kimi-k3-1-pro)（2026-10-24）
  2. [Kimi K3](https://www.kimi.com/blog/kimi-k3)（2026-07-16）
  3. [PerceptionBench](https://www.kimi.com/blog/perception-bench)（2026-07-16）
  4. [Kimi K2.6](https://www.kimi.com/blog/kimi-k2-6)（2026-04-20）
  5. [Agent Swarm](https://www.kimi.com/blog/agent-swarm)（2026-02-09）
  - 📄 完整文章归档（共 10 篇）：[moonshot_kimi.md](llm-news/moonshot_kimi.md)

### xAI Grok (xai_grok)
- 页面：[新闻 / 更新](https://x.ai/news)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-xai_grok.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-xai_grok.xml)
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [使用 Grok Bot 建立会计团队](https://x.ai/news/grok-bot-accounting)（2026-11-16）
  2. [Introducing Grok Bot 1.0](https://x.ai/news/grok-bot-1-0)（2026-11-11）
  3. [用 Grok Bot 给每个团队配一位数据科学家](https://x.ai/news/data-bot)（2026-11-02）
  4. [您的下一个销售团队成员应该是 Grok Bot](https://x.ai/news/grok-bot-sales)（2026-10-27）
  5. [SpaceX Super Intelligence 合作伙伴网络正式推出](https://x.ai/news/partnernetworkannouncement)（2026-10-22）
  - 📄 完整文章归档（共 119 篇）：[xai_grok.md](llm-news/xai_grok.md)

### MiniMax (minimax)
- 页面：[更新日志](https://platform.minimax.cn/docs/release-notes/models)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 页面：[更新日志](https://platform.minimax.cn/docs/release-notes/apis)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 页面：[官方博客](https://www.minimax.cn/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-minimax.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-minimax.xml)
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [MiniMax H3 Image](https://platform.minimax.cn/docs/release-notes/models#2026-%E5%B9%B4-11-%E6%9C%88-10-%E6%97%A5)（2026-11-10）
  2. [插件即应用：MiniMax Code Mini App 正式发布](https://www.minimax.cn/blog/minimax-code-mini-app-1792650729)（2026-10-22）
  3. [MiniMax M3.1 Flash](https://platform.minimax.cn/docs/release-notes/models#2026-%E5%B9%B4-10-%E6%9C%88-19-%E6%97%A5)（2026-10-19）
  4. [MiniMax M3.1 Flash：重新定义 Agent 的性能与成本](https://www.minimax.cn/blog/minimax-m31f)（2026-10-19）
  5. [MiniMax Music 3.0：新一代开放权重、生产级全能音乐模型](https://www.minimax.cn/blog/minimax-music-3-0-cn)（2026-08-13）
  - 📄 完整文章归档（共 52 篇）：[minimax.md](llm-news/minimax.md)

### Mistral AI (mistral)
- 页面：[新闻 / 更新](https://mistral.ai/news/)
  - 📡 RSS/Atom：https://mistral.ai/news/rss
- 📡 [官方 RSS](https://mistral.ai/news/rss)：`https://mistral.ai/news/rss`
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [Le Chonk 带来智能。Studio 让它派上用场。](https://mistral.ai/news/build-with-studio/)（2026-11-05）
  2. [Le Chonk：为程序员打造，受防御者信赖](https://mistral.ai/news/mistral-large-4-oss/)（2026-10-29）
  3. [Mistral 与 NVIDIA 合作推进工程领域的 AI](https://mistral.ai/news/mistral-nvidia-ai-for-industrial-engineering/)（2026-10-21）
  4. [Voxtral 3](https://mistral.ai/news/voxtral-3/)（2026-10-20）
  5. [推出 Timestral](https://mistral.ai/news/timestral/)（2026-10-15）
  - 📄 完整文章归档（共 94 篇）：[mistral.md](llm-news/mistral.md)

### Groq Cloud (groq)
- 页面：[变更日志](https://console.groq.com/docs/changelog.md)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-groq.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-groq.xml)
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [Qwen 3.6 27B](https://console.groq.com/docs/changelog.md#qwen-36-27b)（2026-09-21）
  2. [Compound 与 Compound Mini](https://console.groq.com/docs/changelog.md#compound-and-compound-mini)（2026-09-21）
  3. [Batch API 在验证时检查模型访问权限](https://console.groq.com/docs/changelog.md#batch-api-checks-model-access-at-validation)（2026-09-21）
  4. [Python SDK v1.7.0 与 TypeScript SDK v1.6.0](https://console.groq.com/docs/changelog.md#python-sdk-v170-and-typescript-sdk-v160)（2026-09-21）
  5. [MiniMax M2.7（企业版）](https://console.groq.com/docs/changelog.md#minimax-m27-enterprise)（2026-08-10）
  - 📄 完整文章归档（共 78 篇）：[groq.md](llm-news/groq.md)

### 小米 MiMo (xiaomi_mimo)
- 页面：[更新日志](https://mimo.mi.com/docs/zh-CN/updates/model)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 页面：[更新日志](https://mimo.mi.com/docs/zh-CN/updates/feature/platform)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 页面：[更新日志](https://mimo.mi.com/docs/zh-CN/news)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-xiaomi_mimo.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-xiaomi_mimo.xml)
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [TokenPlan 限时支持 UltraSpeed 超高速旗舰推理模型](https://mimo.mi.com/docs/zh-CN/updates/feature/platform#v2232026-11-19)（2026-11-19）
  2. [支持撤销退款](https://mimo.mi.com/docs/zh-CN/updates/feature/platform#v2222026-11-12)（2026-11-12）
  3. [批量推理（Batch API）结果文件下载提升优化](https://mimo.mi.com/docs/zh-CN/updates/feature/platform#v2212026-11-05)（2026-11-05）
  4. [账务查询 OpenAPI 上线](https://mimo.mi.com/docs/zh-CN/updates/feature/platform#v2202026-11-03)（2026-11-03）
  5. [2026-09-22 MiMo-V2.6 系列发布](https://mimo.mi.com/docs/zh-CN/updates/model#2026-09-22-mimo-v26-%E7%B3%BB%E5%88%97%E5%8F%91%E5%B8%83)（2026-09-22）
  - 📄 完整文章归档（共 44 篇）：[xiaomi_mimo.md](llm-news/xiaomi_mimo.md)

### 腾讯混元 (tencent_hunyuan)
- 页面：[研究页](https://hunyuan.tencent.com/research)
  - 🔌 官方未提供 RSS/Atom 订阅源，条目取自官方数据接口
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-tencent_hunyuan.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-tencent_hunyuan.xml)
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [Hy4 flash：日常工作的极致性价比模型](https://hunyuan.tencent.com/research/hy4-flash)（2026-11-16）
  2. [Hy4 正式发布](https://hunyuan.tencent.com/research/hy4)（2026-11-04）
  3. [Hyra 2.0：自动化科研的下一步](https://hunyuan.tencent.com/research/hyra2)（2026-11-02）
  4. [Hy Image3.5 preview 发布：为专业创作提供高性价比模型](https://hunyuan.tencent.com/research/hy-image35-preview)（2026-09-22）
  5. [当大模型强化学习走向规模化，Batch Size Scaling 有什么不一样？](https://hunyuan.tencent.com/research/100116)（2026-09-22）
  - 📄 完整文章归档（共 14 篇）：[tencent_hunyuan.md](llm-news/tencent_hunyuan.md)

### Hugging Face (huggingface)
- 页面：[官方博客](https://huggingface.co/blog)
  - 📡 RSS/Atom：https://huggingface.co/blog/feed.xml
- 📡 [官方 RSS](https://huggingface.co/blog/feed.xml)：`https://huggingface.co/blog/feed.xml`
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [欢迎 Inkling 2 Mini：为本地部署带来前沿性能](https://huggingface.co/blog/inkling2mini)（2026-11-20）
  2. [推出 harness adapters：把常用模型适配到你的 harness，提升性能并优化成本](https://huggingface.co/blog/harness-adapters-at-scale)（2026-11-20）
  3. [DaisyRose-27B: Pushing the Frontier of Post-Training Efficiency](https://huggingface.co/blog/RadixArk/daisyrose-27b-pushing-the-frontier-of-post-trainin)（2026-11-18）
  4. [为什么你的微调工作花费的时间比 FLOP 所说的要长](https://huggingface.co/blog/Dharma-AI/predicting-fine-tuning-time)（2026-11-18）
  5. [Streamhouse 中的时间序列模型：新领域和用例](https://huggingface.co/blog/ibm-research/time-series-powered-streamhouse)（2026-11-18）
  - 📄 完整文章归档（共 940 篇）：[huggingface.md](llm-news/huggingface.md)

### OpenRouter (openrouter)
- 📡 [官方 RSS](https://openrouter.ai/blog/feed.xml)：`https://openrouter.ai/blog/feed.xml`
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [推理服务提供商的数据处理事件](https://openrouter.ai/blog/announcements/data-processing-incidents-on-inference-providers/)（2026-11-22）
  2. [OpenRouter 现在为 Hugging Face 提供推理支持](https://openrouter.ai/blog/announcements/hugging-face-inference-providers/)（2026-11-16）
  3. [管理密钥访问控制收紧](https://openrouter.ai/blog/announcements/scoped-management-keys/)（2026-11-16）
  4. [RAG 中的 reranking：如何用 reranker 修复错误检索](https://openrouter.ai/blog/tutorials/reranking-rag/)（2026-11-13）
  5. [如何阻止 AI 代理陷入无限循环](https://openrouter.ai/blog/tutorials/ai-agent-infinite-loop/)（2026-11-12）
  - 📄 完整文章归档（共 186 篇）：[openrouter.md](llm-news/openrouter.md)

### Cloudflare Workers AI (cloudflare_workers_ai)
- 📡 [官方 RSS](https://developers.cloudflare.com/workers-ai/changelog/index.xml)：`https://developers.cloudflare.com/workers-ai/changelog/index.xml`
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
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
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [视频智能：让视频库中的每一刻都可搜索——推出面向企业搜索和 AI 智能体的精准、带时间戳视频检索](https://cohere.com/blog/video-intelligence-preview)（2026-11-16）
  2. [欢迎 Jaya Baloo 出任 Cohere 首位 CISO](https://cohere.com/blog/cohere-welcomes-jaya-baloo-as-first-ciso)（2026-11-12）
  3. [Embed 5 与 Rerank 5 现已上线 OpenRouter](https://cohere.com/blog/embed-rerank-5-openrouter)（2026-11-04）
  4. [全球领先的开放模型，完全由你掌控](https://cohere.com/blog/open-source-model-vault)（2026-11-03）
  5. [Cohere 推进 40 亿加元承诺，巩固加拿大 AI 领导地位并大幅扩充本土团队](https://cohere.com/blog/cohere-canada-commitment)（2026-10-30）
  - 📄 完整文章归档（共 59 篇）：[cohere.md](llm-news/cohere.md)

### 商汤 日日新 (sensetime_sensenova)
- 页面：[新闻 / 更新](https://www.sensetime.com/cn/news)
  - 🔌 官方未提供 RSS/Atom 订阅源，条目取自官方数据接口
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-sensetime_sensenova.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-sensetime_sensenova.xml)
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [SenseNova Loop-9B正式版：让更少的参数走更深的计算路径](https://www.sensetime.com/cn/news/sensenova-loop-9b-20261118-1059)（2026-11-17）
  2. [SenseNova 6.8 Flash 正式版发布：办公更稳，设计更美](https://www.sensetime.com/cn/news/sensenova-6-8-flash-release-20261103-1421)（2026-11-02）
  3. [商汤开源 SenseNova Loop-9B-Preview：探索以计算深度释放模型潜力](https://www.sensetime.com/cn/news/sensenova-loop-9b-preview-20261117-1750)（2026-10-30）
  4. [商汤实测 GPT-6-Astra 并开源 SenseNova-RoboRSI：具身智能下一步怎么走？](https://www.sensetime.com/cn/news/gpt-6-astra-sensenova-roborsi-20261019-1513)（2026-10-19）
  5. [“五彩斑斓的黑”也能直接出片，SenseNova U1 Pro正式版上线商汤小浣熊](https://www.sensetime.com/cn/news/sense-nova-u1-pro)（2026-09-21）
  - 📄 完整文章归档（共 36 篇）：[sensetime_sensenova.md](llm-news/sensetime_sensenova.md)

### Meta Llama (meta_llama)
- 页面：[官方博客](https://ai.meta.com/blog/)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 [官方 RSS](https://about.fb.com/news/tag/ai/feed/)：`https://about.fb.com/news/tag/ai/feed/`
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [共同推进科学：开源 AI for Science 峰会亮点](https://about.fb.com/news/2026/11/advancing-science-together-highlights-from-the-open-source-ai-for-science-summit/)（2026-11-20）
  2. [Meta 欢迎 Loblaw 成为 Muse 首家加拿大零售合作伙伴](https://about.fb.com/news/2026/11/meta-welcomes-loblaw-as-first-canadian-retail-partner-to-muse/)（2026-11-18）
  3. [Muse 在澳大利亚上线：全球首款面向所有人的个人 AI agent](https://about.fb.com/news/2026/11/muse-is-now-available-in-australia/)（2026-11-17）
  4. [Meta 的新协议将清洁制造引入数据中心供应链](https://about.fb.com/news/2026/11/meta-new-agreements-clean-manufacturing-data-center-supply-chains/)（2026-11-12）
  5. [为你专属定制 Muse 应用](https://about.fb.com/news/2026/11/introducing-spaces-customize-muse-app/)（2026-11-06）
  - 📄 完整文章归档（共 33 篇）：[meta_llama.md](llm-news/meta_llama.md)

### 美团 LongCat (longcat_meituan)
- 页面：[新闻 / 更新](https://longcat.ai/)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-longcat_meituan.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-longcat_meituan.xml)
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [LongCat-2.5：面向智能体任务的原生多模态模型](https://longcat.ai/blog/longcat-2.5)（2026-11-01）
  2. [LongCat-2.0：万亿参数 MoE 大语言模型](https://longcat.ai/blog/longcat-2.0)（2026-06-29）
  3. [在噪声中学习行动：用噪声环境增强 agent 鲁棒性](https://huggingface.co/papers/2605.27209)（2026-05-26）

### 硅基流动 (siliconflow)
- 页面：[更新日志](https://docs.siliconflow.cn/docs/release-notes/overview)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-siliconflow.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-siliconflow.xml)
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [【功能更新】动态限流上线：限流值随模型负载自动调整](https://docs.siliconflow.cn/docs/release-notes/overview#%E5%8A%9F%E8%83%BD%E6%9B%B4%E6%96%B0%E5%8A%A8%E6%80%81%E9%99%90%E6%B5%81%E4%B8%8A%E7%BA%BF%E9%99%90%E6%B5%81%E5%80%BC%E9%9A%8F%E6%A8%A1%E5%9E%8B%E8%B4%9F%E8%BD%BD%E8%87%AA%E5%8A%A8%E8%B0%83%E6%95%B4)（2026-11-16）
  2. [【模型服务调整】Wan2.2 系列、GLM-5.1 下线，MiniMax-H3 上线](https://docs.siliconflow.cn/docs/release-notes/overview#%E6%A8%A1%E5%9E%8B%E6%9C%8D%E5%8A%A1%E8%B0%83%E6%95%B4wan22-%E7%B3%BB%E5%88%97glm-51-%E4%B8%8B%E7%BA%BFminimax-h3-%E4%B8%8A%E7%BA%BF)（2026-11-03）
  3. [【模型服务调整】Qwen3-Coder-30B-A3B-Instruct、GLM-4.5V 等模型将下线](https://docs.siliconflow.cn/docs/release-notes/overview#%E6%A8%A1%E5%9E%8B%E6%9C%8D%E5%8A%A1%E8%B0%83%E6%95%B4qwen3-coder-30b-a3b-instructglm-45v-%E7%AD%89%E6%A8%A1%E5%9E%8B%E5%B0%86%E4%B8%8B%E7%BA%BF)（2026-11-03）
  4. [【新模型上线】OpenMOSS-Team/MOSS-Image 上线](https://docs.siliconflow.cn/docs/release-notes/overview#%E6%96%B0%E6%A8%A1%E5%9E%8B%E4%B8%8A%E7%BA%BFopenmoss-teammoss-image-%E4%B8%8A%E7%BA%BF)（2026-11-03）
  5. [【模型服务调整】Wan2.2 系列下线，MiniMax-H3 上线](https://docs.siliconflow.cn/docs/release-notes/overview#%E6%A8%A1%E5%9E%8B%E6%9C%8D%E5%8A%A1%E8%B0%83%E6%95%B4wan22-%E7%B3%BB%E5%88%97%E4%B8%8B%E7%BA%BFminimax-h3-%E4%B8%8A%E7%BA%BF)（2026-11-03）
  - 📄 完整文章归档（共 55 篇）：[siliconflow.md](llm-news/siliconflow.md)

### 快手万擎 (streamlake)
- 页面：[更新日志](https://www.streamlake.com/document/WANQING/mdptalisb06i7ai3zdd)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-streamlake.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-streamlake.xml)
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [【新增】数据分析任务完成后可将结果下载至本地，便于进一步处理与留存数据](https://www.streamlake.com/document/WANQING/mdptalisb06i7ai3zdd#t2026-08-14-0)（2026-08-14）
  2. [【新增】新增 Python 代码节点，支持灵活编写自定义处理逻辑，满足个性化数据加工需求](https://www.streamlake.com/document/WANQING/mdptalisb06i7ai3zdd#t2026-07-22-1)（2026-07-22）
  3. [【新增】新增 GLM-5.2-FP8 模型部署能力，支持预付费、后付费模式，丰富模型部署选择](https://www.streamlake.com/document/WANQING/mdptalisb06i7ai3zdd#t2026-07-03-2)（2026-07-03）
  4. [【优化】文本生成模型推理点监控新增缓存命中率曲线，支持 Cache命中率及 Cache token 数量等指标](https://www.streamlake.com/document/WANQING/mdptalisb06i7ai3zdd#t2026-07-03-3)（2026-07-03）
  5. [【优化】推理监控输入输出token卡片增加影响因子数据，用户可直接查看因子维度token消耗](https://www.streamlake.com/document/WANQING/mdptalisb06i7ai3zdd#t2026-06-30-4)（2026-06-30）
  - 📄 完整文章归档（共 23 篇）：[streamlake.md](llm-news/streamlake.md)

### Amazon Bedrock (aws_bedrock)
- 📡 [官方 RSS](https://aws.amazon.com/blogs/machine-learning/category/artificial-intelligence/amazon-machine-learning/amazon-bedrock/feed/)：`https://aws.amazon.com/cn/blogs/machine-learning/category/artificial-intelligence/amazon-machine-learning/amazon-bedrock/feed/`
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [将 Kimi Code CLI 与 Amazon Bedrock 上的模型结合使用](https://aws.amazon.com/blogs/machine-learning/use-kimi-code-cli-with-models-on-amazon-bedrock/)（2026-11-20）
  2. [让 AI agent 借助 Amazon Bedrock AgentCore payments 为 AWS Marketplace 的 x402 商品付款](https://aws.amazon.com/blogs/machine-learning/enable-ai-agents-to-pay-for-aws-marketplace-x402-products-with-amazon-bedrock-agentcore-payments/)（2026-11-19）
  3. [Amazon Bedrock AgentCore harness 新增 Strands harness 默认值、内置工具与生命周期钩子](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-harness-adds-strands-harness-defaults-built-in-tools-and-lifecycle-hooks/)（2026-11-19）
  4. [利用 Accenture 的排序方法优化 Amazon Bedrock 上的 AI 经济效益](https://aws.amazon.com/blogs/machine-learning/optimize-ai-economics-on-amazon-bedrock-with-accentures-sequenced-approach/)（2026-11-19）
  5. [从学习到上榜：思科如何用 AWS AI League 让 1,200 名工程师掌握 agentic AI](https://aws.amazon.com/blogs/machine-learning/from-learning-to-leaderboard-how-cisco-upskilled-1200-engineers-in-agentic-ai-with-aws-ai-league/)（2026-11-19）
  - 📄 完整文章归档（共 871 篇）：[aws_bedrock.md](llm-news/aws_bedrock.md)

### Cerebras Inference (cerebras)
- 页面：[官方博客](https://www.cerebras.ai/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-cerebras.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-cerebras.xml)
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [Cerebras 推出解耦式推理](https://www.cerebras.ai/blog/cerebras-launches-disaggregated-inference)
  2. [来自我们的 CEO：打造晶圆级需要什么，以及它为何能持续下去](https://www.cerebras.ai/blog/what-it-took-to-build-wafer-scale-and-why-it-lasts)
  3. [高级代码，晶圆级性能](https://www.cerebras.ai/blog/high-level-code-wafer-scale-performance)
  4. [如何实现晶圆级良率](https://www.cerebras.ai/blog/how-to-yield-at-wafer-scale)
  5. [MoE 规模化：让稀疏模型在真实硬件上跑得快](https://www.cerebras.ai/blog/moe-guide-scale)
  - 📄 完整文章归档（共 60 篇）：[cerebras.md](llm-news/cerebras.md)

### Together AI (together_ai)
- 📡 [官方 RSS](https://www.together.ai/blog/rss.xml)：`https://www.together.ai/blog/rss.xml`
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [安全事件：2026年6月和7月请求的 Prompt 泄露](https://www.together.ai/blog/security-event-prompt-leakage-for-requests-in-june-and-july-of-2026)（2026-11-21）
  2. [Qwen4 Max 已上线 Together AI](https://www.together.ai/blog/qwen4-max)（2026-11-21）
  3. [Qwen3 TTS is now available on Together AI](https://www.together.ai/blog/qwen3-tts)（2026-11-20）
  4. [Tencent Hy4 is live on Together AI](https://www.together.ai/blog/tencent-hy4)（2026-11-19）
  5. [推出 Together Storage Accelerator：为您的 GPU 集群提供快速、免费的数据缓存](https://www.together.ai/blog/introducing-together-storage-accelerator)（2026-11-19）
  - 📄 完整文章归档（共 104 篇）：[together_ai.md](llm-news/together_ai.md)

### Fireworks AI (fireworks_ai)
- 页面：[官方博客](https://fireworks.ai/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-fireworks_ai.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-fireworks_ai.xml)
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [Kimi K3.1 Pro 上线 Fireworks](https://fireworks.ai/blog/kimi-k3-1-pro-fireworks/)（2026-11-04）
  2. [免费训练 Muse Glimmer：我们如何押赢 Jev](https://fireworks.ai/blog/train-muse-glimmer-for-free)
  3. [Ember-1 发布](https://fireworks.ai/blog/ember-1)
  4. [专业智力指数简介](https://fireworks.ai/blog/specialized-intelligence-index-ai-benchmarks)
  5. [边界不是模型。这是一个路由器。](https://fireworks.ai/blog/llm-model-routing-deepswe)
  - 📄 完整文章归档（共 41 篇）：[fireworks_ai.md](llm-news/fireworks_ai.md)

### DeepInfra (deepinfra)
- 页面：[官方博客](https://deepinfra.com/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-deepinfra.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-deepinfra.xml)
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [Gemini 3.7 Flash：新增功能、基准测试和 API 指南](https://deepinfra.com/blog/gemini-3-7-flash-model-overview-integration-guide)（2026-11-17）
  2. [DeepInfra 与 Opper AI 合作：Opper 网关接入 100+ 模型](https://deepinfra.com/blog/deepinfra-opper-partnership)（2026-11-17）
  3. [Kimi K3.1 Pro：模型概览、基准测试与 API 指南](https://deepinfra.com/blog/kimi-k3-1-pro-model-overview)（2026-11-17）
  4. [最佳 Kimi K3.1 Pro API 提供商（2026）：价格、档位、速度](https://deepinfra.com/blog/best-kimi-k3-1-pro-api-providers)（2026-11-17）
  5. [Kimi K3.1 Pro API 基准测试：提供商、速度与成本](https://deepinfra.com/blog/kimi-k3-1-pro-api-benchmarks)（2026-11-17）
  - 📄 完整文章归档（共 64 篇）：[deepinfra.md](llm-news/deepinfra.md)

### Modular (modular_cloud)
- 📡 [官方 RSS](https://www.modular.com/blog/rss.xml)：`https://www.modular.com/blog/rss.xml`
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [Modular：重新引入 MAX 模块](https://www.modular.com/blog/reintroducing-max-module)（2026-11-19）
  2. [Modular：Modular 在 LLVM Developers' Meeting 2026 上](https://www.modular.com/blog/modular-llvm-dev-meeting-2026)（2026-11-16）
  3. [LLVM 开发者大会 2026：agentic 时代的持久基础设施](https://www.modular.com/blog/llvm-dev-meeting-2026-durable-infrastructure-in-the-agentic-era)（2026-11-04）
  4. [Modular：MAX 现在源码可用，向所有人开放](https://www.modular.com/blog/max-license)（2026-10-22）
  5. [Modular：Modular 26.7 开放 MAX](https://www.modular.com/blog/26-7)（2026-10-22）
  - 📄 完整文章归档（共 106 篇）：[modular_cloud.md](llm-news/modular_cloud.md)

### AI21 Labs (ai21_labs)
- 页面：[官方博客](https://www.ai21.com/blog)
  - 🔌 官方未提供 RSS/Atom 订阅源，条目取自官方数据接口
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-ai21_labs.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-ai21_labs.xml)
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [隆重推出 Teel – 面向 agent 的涡轮高效执行库（但不仅仅是）](https://www.ai21.com/blog/teel-turbo-efficient-execution-library/)（2026-11-05）
  2. [后训练案例研究：与 Deel 一起把全球薪资情报做到前沿级](https://www.ai21.com/blog/ai21-deel-case-study/)（2026-11-04）
  3. [后训练案例研究：与 Alice 一起达到前沿级攻击韧性](https://www.ai21.com/blog/ai21-alice-case-study/)（2026-11-02）
  4. [为什么我们在训练前先构建指令遵循基准](https://www.ai21.com/blog/lift-bench-blog/)（2026-10-25）
  5. [我们如何将 GitLab Duo Code Review 的成本降低 98%](https://www.ai21.com/blog/gitlab-case-study/)（2026-10-22）
  - 📄 完整文章归档（共 75 篇）：[ai21_labs.md](llm-news/ai21_labs.md)

### Jina AI (jina_ai)
- 页面：[官方博客](https://jina.ai/news/)
  - 📡 RSS/Atom：https://jina.ai/feed.rss
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [jina-embeddings-v5-omni：文本、图像、音频与视频嵌入：一个模型覆盖四种模态（文本、图像、音频、视频），1.6B 与 0.9B 均为同类最优的全模态嵌入](https://jina.ai/news/jina-embeddings-v5-omni-multimodal-embeddings-for-text-image-audio-and-video)（2026-05-12）
  2. [从多模态 LLM 自举音频嵌入：把任意多模态 LLM 变成小型音频嵌入模型，数据量少 25 倍即可超越 CLAP](https://jina.ai/news/bootstrapping-audio-embeddings-from-multimodal-llms)（2026-03-11）
  3. [从原始数值识别嵌入模型：读原始数字即可为嵌入模型留指纹的微型 transformer，无需特征工程](https://jina.ai/news/identifying-embedding-models-from-raw-numerical-values)（2026-03-06）
  4. [jina-embeddings-v5-text：新的 SOTA 小型多语言 embedding](https://jina.ai/news/jina-embeddings-v5-text-distilling-4b-quality-into-sub-1b-multilingual-embeddings)（2026-02-19）
  5. [Jina-VLM：小型多语言视觉语言模型：全新 2B 视觉语言模型在多语言 VQA 上达到 SOTA，纯文本任务不出现灾难性遗忘](https://jina.ai/news/jina-vlm-small-multilingual-vision-language-model)（2025-12-04）
  - 📄 完整文章归档（共 8 篇）：[jina_ai.md](llm-news/jina_ai.md)

### Poolside (poolside)
- 页面：[官方博客](https://poolside.ai/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-poolside.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-poolside.xml)
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [Poolside on Dell：在您的边界内实现前沿人工智能的有效途径](https://poolside.ai/blog/poolside-on-dell)（2026-07-28）
  2. [推出 Laguna XS 2.1](https://poolside.ai/blog/introducing-laguna-xs-2-1)（2026-07-21）
  3. [长上下文更新：Laguna XS.2 和 M.1](https://poolside.ai/blog/long-context-update-laguna-xs-2-and-m-1)（2026-07-02）
  4. [AI，你的方式：引入 Poolside 平台](https://poolside.ai/blog/introducing-the-poolside-platform)（2026-05-26）
  5. [Laguna XS.2 和 M.1：深入探讨](https://poolside.ai/blog/laguna-a-deeper-dive)（2026-05-11）
  - 📄 完整文章归档（共 19 篇）：[poolside.md](llm-news/poolside.md)

### Anyscale (anyscale)
- 📡 [官方 RSS](https://www.anyscale.com/rss.xml)：`https://www.anyscale.com/rss.xml`
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [Ray Train：通过数据摄取可观测性诊断模型训练中的 GPU 饥饿](https://anyscale.com/blog/diagnosing-gpu-starvation-with-ray-train)（2026-11-17）
  2. [用 Ray 实现 JEPA 世界模型架构的实时推理](https://anyscale.com/blog/real-time-inference-for-jepa-world-models-ray-anyscale)（2026-11-12）
  3. [向 CNCF 捐赠 KubeRay](https://anyscale.com/blog/donate-kuberay-cncf)（2026-11-09）
  4. [Lila Sciences 与 Anyscale 如何把 GLM-5.3-Flash 训练扩展到 100 万 token](https://anyscale.com/blog/lila-sciences-anyscale-glm-training-one-million-tokens)（2026-11-05）
  5. [KubeRay 生产实践：来自一线的最佳实践](https://anyscale.com/blog/kuberay-best-practices)（2026-10-26）
  - 📄 完整文章归档（共 104 篇）：[anyscale.md](llm-news/anyscale.md)

### InceptionLabs (inception_labs)
- 页面：[官方博客](https://www.inceptionlabs.ai/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-inception_labs.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-inception_labs.xml)
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [规模化扩散：Mercury 3 发布](https://www.inceptionlabs.ai/blog/introducing-mercury-3)（2026-10-29）
  2. [Mercury 2 入选 TIME 2026 年度最佳发明](https://www.inceptionlabs.ai/blog/mercury-2-named-to-time-s-best-inventions-of-2026)（2026-10-16）
  3. [Mercury Voice 发布](https://www.inceptionlabs.ai/blog/introducing-mercury-voice)（2026-10-01）
  4. [Mercury 2.5 简介](https://www.inceptionlabs.ai/blog/introducing-mercury-2-5)（2026-09-24）
  5. [Mercury 2 用于搜索：快到一次查询可以跑上百次](https://www.inceptionlabs.ai/blog/mercury-2-for-search)
  - 📄 完整文章归档（共 15 篇）：[inception_labs.md](llm-news/inception_labs.md)

### Inference.net (inference_net)
- 页面：[官方博客](https://inference.net/blog/)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-inference_net.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-inference_net.xml)
- 📰 **最新文章**（官方源抓取于 2026-11-23，标题自动汉化）：
  1. [我们用 Elixir 把 vLLM 分词提速 120 倍](https://inference.net/blog/vllm-tokenization-120x-faster-with-elixir/)（2026-11-20）
  2. [MiniMax M3.1 Flash 在 Inference 上线：Day 0](https://inference.net/blog/minimax-m3-1-flash-day-0/)（2026-10-23）
  3. [AutoEvals 简介：自动找到最适合您任务的模型](https://inference.net/blog/introducing-autoevals/)（2026-08-05）
  4. [Schematron V2：以极低成本实现前沿级 HTML 转 JSON 提取](https://inference.net/blog/schematron-v2/)（2026-04-16）
  5. [推理平台简介：监控、训练和部署自我改进的 AI 模型](https://inference.net/blog/introducing-inference-platform/)（2026-04-14）
  - 📄 完整文章归档（共 12 篇）：[inference_net.md](llm-news/inference_net.md)

---
共整理 34 个厂商的动态入口（其中 34 个成功提取最新文章），RSS/Atom 源 16 个。

<!-- LLM-NEWS:END -->
