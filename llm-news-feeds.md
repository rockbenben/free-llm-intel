# LLM 厂商博客 / 更新动态订阅源

<!-- LLM-NEWS:BEGIN  本章节由 crawler_llm_intel.py 自动生成，请勿手工修改 -->

## 厂商博客 / 更新动态订阅源

> 由 `crawler_llm_intel.py` 自动整理，最近更新：**2026-09-26 13:46:54**。
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
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
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
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [Claude Tag 现在支持通道中的个人连接器](https://claude.com/blog#d-2026-09-25-19)（2026-09-25）
  2. [Claude Tag 现已支持频道中的个人连接器](https://claude.com/blog/claude-tag-now-supports-personal-connectors-in-channels)（2026-09-24）
  3. [Claude Marketplace：一站式发现合作伙伴的插件、代理和服务](https://claude.com/blog#d-2026-09-23-21)（2026-09-23）
  4. [Claude Marketplace：一站式发现合作伙伴的插件、代理和服务](https://claude.com/blog/claude-marketplace)（2026-09-23）
  5. [与埃森哲合作开展嵌入式评估的公告](https://www.anthropic.com/news/accenture-embedded-evaluation)（2026-09-18）
  - 📄 完整文章归档（共 80 篇）：[anthropic.md](llm-news/anthropic.md)

### Google Gemini (google_gemini)
- 页面：[变更日志](https://ai.google.dev/gemini-api/docs/changelog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-google_gemini.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-google_gemini.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
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
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [SpaceXAI 如何使用 Grok Bot 扩大客户支持](https://x.ai/news#d-2026-09-22-1)（2026-09-22）
  2. [SpaceXAI 如何使用 Grok Bot 扩展客户支持](https://x.ai/news/grok-bot-customer-support)（2026-09-22）
  3. [介绍 Grok 4.7](https://x.ai/news#d-2026-09-21-0)（2026-09-21）
  4. [介绍 Grok 4.7](https://x.ai/news/grok-4-7)（2026-09-21）
  5. [Grok 语音转录 2.0 简介](https://x.ai/news#d-2026-09-18-2)（2026-09-18）
  - 📄 完整文章归档（共 164 篇）：[xai_grok.md](llm-news/xai_grok.md)

### Groq Cloud (groq)
- 页面：[变更日志](https://console.groq.com/docs/changelog.md)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-groq.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-groq.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [Q1 2026 更新日志条目](https://github.com/groq/groq-changelog/commit/abaa8395286b622a837adb5d6b44709845d1edba)（2026-05-06）
  2. [MiniMax M2.5 与 Qwen3-VL 32B Instruct 上线（企业版）](https://console.groq.com/docs/changelog.md#minimax-m25-and-qwen3vl-32b-instruct-enterprise)（2026-04-18）
  3. [Orpheus Arabic Saudi 新增语音](https://console.groq.com/docs/changelog.md#new-voices-for-orpheus-arabic-saudi)（2026-04-18）
  4. [Python SDK v1.2.0 and TypeScript SDK v1.1.2](https://console.groq.com/docs/changelog.md#python-sdk-v120-and-typescript-sdk-v112)（2026-04-18）
  5. [Groq 是首批将 NVIDIA Groq 3 LPX 和 Vera Rubin NVL72 推向市场的公司之一](https://groq.com/blog/groq-among-the-first-to-bring-nvidia-groq-3-lpx-and-vera-rubin-nvl72-to-market)（2026-03-24）
  - 📄 完整文章归档（共 49 篇）：[groq.md](llm-news/groq.md)

### DeepSeek (deepseek)
- 页面：[更新日志](https://api-docs.deepseek.com/zh-cn/updates/)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 页面：[版本动态](https://api-docs.deepseek.com/zh-cn/news/news260424/)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-deepseek.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-deepseek.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [DeepSeek-V4.1-Flash 发布](https://api-docs.deepseek.com/zh-cn/updates/#%E6%97%B6%E9%97%B4-2026-09-10)（2026-09-10）
  2. [DeepSeek-V4.1-Flash 发布](https://api-docs.deepseek.com/zh-cn/news/news260910)（2026-09-10）
  3. [DeepSeek-V4-Flash-Vision-Exp 发布](https://api-docs.deepseek.com/zh-cn/updates/#%E6%97%B6%E9%97%B4-2026-08-21)（2026-08-21）
  4. [DeepSeek-V4-Flash-Vision-Exp 上线](https://api-docs.deepseek.com/zh-cn/news/news260821)（2026-08-21）
  5. [DeepSeek-V4-Pro 更新](https://api-docs.deepseek.com/zh-cn/updates/#%E6%97%B6%E9%97%B4-2026-08-13)（2026-08-13）
  - 📄 完整文章归档（共 47 篇）：[deepseek.md](llm-news/deepseek.md)

### 智谱 AI GLM (zhipu_glm)
- 页面：[更新日志](https://docs.bigmodel.cn/cn/update/new-releases)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-zhipu_glm.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-zhipu_glm.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
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
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [decision-model-preview：面向高频业务判断的结构化决策模型，可根据文本或业务状态并行完成分类、是非判断与评分，并返回概率分布和置信度，适用于工单分流、内容审核、智能体路由与结果校验等场景](https://help.aliyun.com/zh/model-studio/newly-released-models#decision-model-preview)（2026-09-24）
  2. [stepfun/step-5-preview：Step 5 Preview 是面向真实世界 Agentic 任务的旗舰基座模型，在 AI 编程、软件工程、专业知识工作等任务上达到前沿水平，金融领域表现尤为突出](https://help.aliyun.com/zh/model-studio/newly-released-models#stepfun/step-5-preview)（2026-09-21）
  3. [qwen3.8-omni-flash-realtime：支持实时音视频交互及文本、音频输出，新增多通道音频、视频聚合和远程 MCP 工具调用，支持 WebSocket、WebRTC 和 AOQ 接入](https://help.aliyun.com/zh/model-studio/newly-released-models#qwen3.8-omni-flash-realtime)（2026-09-21）
  4. [ZHIPU/GLM-5.3-FlashX：GLM-5.3-FlashX 是 GLM-5 系列的高速模型，推理速度达 200 tokens/s，提供更快、更流畅的模型体验](https://help.aliyun.com/zh/model-studio/newly-released-models#ZHIPU/GLM-5.3-FlashX)（2026-09-21）
  5. [vanchin/deepseek-v4.1-flash：DeepSeek-V4.1-Flash 是 DeepSeek 全新模型结构系列中尺寸最小的模型，具备原生多模态视觉理解能力，支持 1M 上下文与 384K 输出](https://help.aliyun.com/zh/model-studio/newly-released-models#vanchin/deepseek-v4.1-flash)（2026-09-21）
  - 📄 完整文章归档（共 109 篇）：[aliyun_qwen.md](llm-news/aliyun_qwen.md)

### 腾讯混元 (tencent_hunyuan)
- 页面：[更新日志](https://cloud.tencent.com/document/product/1729/97765)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-tencent_hunyuan.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-tencent_hunyuan.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [混元旧版本模型正式下线，下线模型不再提供服务，建议迁移至 TokenHub 使用最新版本模型](https://cloud.tencent.com/document/product/1729/97765#t2026-06-22-0)（2026-06-22）
  2. [基于文本 TurboS 基座生成图生文快思考模型，相比上一版本在图像基础识别、图像分析推理等维度都有明显的效果提升](https://cloud.tencent.com/document/product/1729/97765#t2025-12-17-1)（2025-12-17）
  3. [发布特性：1. 模型底座从 TurboS 升级为混元2.0，模型能力全面提升](https://cloud.tencent.com/document/product/1729/97765#t2025-11-11-3)（2025-11-11）
  4. [发布特性：1. 模型底座从 TurboS 升级为混元2.0，模型能力全面提升](https://cloud.tencent.com/document/product/1729/97765#t2025-11-09-2)（2025-11-09）
  5. [支持语种齐全，33种语种互译和5种民族语言互译](https://cloud.tencent.com/document/product/1729/97765#t2025-10-14-4)（2025-10-14）
  - 📄 完整文章归档（共 95 篇）：[tencent_hunyuan.md](llm-news/tencent_hunyuan.md)

### 商汤 SenseNova 日日新 (sensetime_sensenova)
- 页面：[更新日志](https://www.sensecore.cn/help/docs/model-as-a-service/nova/release)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-sensetime_sensenova.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-sensetime_sensenova.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [【模型更新】发布最新版本日日新-融合模态模型SenseNova-V6.5-Pro、SenseNova-V6.5-Turbo](https://www.sensecore.cn/help/docs/model-as-a-service/nova/release#%E6%A8%A1%E5%9E%8B%E6%9B%B4%E6%96%B0%E5%8F%91%E5%B8%83%E6%9C%80%E6%96%B0%E7%89%88%E6%9C%AC%E6%97%A5%E6%97%A5%E6%96%B0-%E8%9E%8D%E5%90%88%E6%A8%A1%E6%80%81%E6%A8%A1%E5%9E%8Bsensenova-v65-prosensenova-v65-turbo)（2025-07-23）
  2. [【模型更新】发布最新版本日日新-语音大模型-语音合成（音色融合）](https://www.sensecore.cn/help/docs/model-as-a-service/nova/release#%E6%A8%A1%E5%9E%8B%E6%9B%B4%E6%96%B0%E5%8F%91%E5%B8%83%E6%9C%80%E6%96%B0%E7%89%88%E6%9C%AC%E6%97%A5%E6%97%A5%E6%96%B0-%E8%AF%AD%E9%9F%B3%E5%A4%A7%E6%A8%A1%E5%9E%8B-%E8%AF%AD%E9%9F%B3%E5%90%88%E6%88%90%E9%9F%B3%E8%89%B2%E8%9E%8D%E5%90%88)（2025-06-03）
  3. [【模型更新】发布最新版本日日新-融合模态模型SenseNova-V6-Pro、SenseNova-V6-Reasoner、SenseNova-V6-Turbo](https://www.sensecore.cn/help/docs/model-as-a-service/nova/release#%E6%A8%A1%E5%9E%8B%E6%9B%B4%E6%96%B0%E5%8F%91%E5%B8%83%E6%9C%80%E6%96%B0%E7%89%88%E6%9C%AC%E6%97%A5%E6%97%A5%E6%96%B0-%E8%9E%8D%E5%90%88%E6%A8%A1%E6%80%81%E6%A8%A1%E5%9E%8Bsensenova-v6-prosensenova-v6-reasonersensenova-v6-turbo)（2025-04-09）
  4. [【模型更新】发布最新版本日日新-大语言模型SenseChat-5-1202、SenseChat-Turbo-1202](https://www.sensecore.cn/help/docs/model-as-a-service/nova/release#%E6%A8%A1%E5%9E%8B%E6%9B%B4%E6%96%B0%E5%8F%91%E5%B8%83%E6%9C%80%E6%96%B0%E7%89%88%E6%9C%AC%E6%97%A5%E6%97%A5%E6%96%B0-%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8Bsensechat-5-1202sensechat-turbo-1202)（2024-12-30）
  5. [【功能更新】OpenAPI全面支持通过API Key调用](https://www.sensecore.cn/help/docs/model-as-a-service/nova/release#%E5%8A%9F%E8%83%BD%E6%9B%B4%E6%96%B0openapi%E5%85%A8%E9%9D%A2%E6%94%AF%E6%8C%81%E9%80%9A%E8%BF%87api-key%E8%B0%83%E7%94%A8)（2024-10-30）
  - 📄 完整文章归档（共 18 篇）：[sensetime_sensenova.md](llm-news/sensetime_sensenova.md)

### SiliconFlow 硅基流动 (siliconflow)
- 页面：[更新日志](https://docs.siliconflow.cn/cn/release-notes/overview)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-siliconflow.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-siliconflow.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [【接口服务调整】生图 API 下线 batch_size 字段、水印默认添加](https://docs.siliconflow.cn/docs/release-notes/overview#%E6%8E%A5%E5%8F%A3%E6%9C%8D%E5%8A%A1%E8%B0%83%E6%95%B4%E7%94%9F%E5%9B%BE-api-%E4%B8%8B%E7%BA%BF-batch_size-%E5%AD%97%E6%AE%B5%E6%B0%B4%E5%8D%B0%E9%BB%98%E8%AE%A4%E6%B7%BB%E5%8A%A0)（2026-09-15）
  2. [【模型价格调整】DeepSeek-V4-Flash 模型分时段定价调整](https://docs.siliconflow.cn/docs/release-notes/overview#%E6%A8%A1%E5%9E%8B%E4%BB%B7%E6%A0%BC%E8%B0%83%E6%95%B4deepseek-v4-flash-%E6%A8%A1%E5%9E%8B%E5%88%86%E6%97%B6%E6%AE%B5%E5%AE%9A%E4%BB%B7%E8%B0%83%E6%95%B4)（2026-09-11）
  3. [【接口服务调整】对话模型将忽略 repetition_penalty 参数](https://docs.siliconflow.cn/docs/release-notes/overview#%E6%8E%A5%E5%8F%A3%E6%9C%8D%E5%8A%A1%E8%B0%83%E6%95%B4%E5%AF%B9%E8%AF%9D%E6%A8%A1%E5%9E%8B%E5%B0%86%E5%BF%BD%E7%95%A5-repetition_penalty-%E5%8F%82%E6%95%B0)（2026-09-09）
  4. [【模型服务调整】Nex-N2-Pro、Qwen3.5-397B-A17B、MiniMax-M2.5 等模型将下线](https://docs.siliconflow.cn/docs/release-notes/overview#%E6%A8%A1%E5%9E%8B%E6%9C%8D%E5%8A%A1%E8%B0%83%E6%95%B4nex-n2-proqwen35-397b-a17bminimax-m25-%E7%AD%89%E6%A8%A1%E5%9E%8B%E5%B0%86%E4%B8%8B%E7%BA%BF)（2026-09-03）
  5. [【接口服务调整】/user/info 接口将停止服务](https://docs.siliconflow.cn/docs/release-notes/overview#%E6%8E%A5%E5%8F%A3%E6%9C%8D%E5%8A%A1%E8%B0%83%E6%95%B4userinfo-%E6%8E%A5%E5%8F%A3%E5%B0%86%E5%81%9C%E6%AD%A2%E6%9C%8D%E5%8A%A1)（2026-09-01）
  - 📄 完整文章归档（共 47 篇）：[siliconflow.md](llm-news/siliconflow.md)

### MiniMax (minimax)
- 页面：[更新日志](https://platform.minimax.cn/docs/release-notes/models)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 页面：[更新日志](https://platform.minimax.cn/docs/release-notes/apis)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-minimax.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-minimax.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
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
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
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
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
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
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [Cohere 和 OpenText 合作，为政府和受监管行业带来值得信赖的代理人工智能汇集企业数据、上下文和安全人工智能，以大规模支持代理人工智能](https://cohere.com/blog/cohere-and-open-text-partner-to-bring-trusted-ai)（2026-09-16）
  2. [Cohere 与 Aleph Alpha 签署协议，成为首个跨大西洋主权人工智能解决方案](https://cohere.com/blog/cohere-and-aleph-alpha-sign-agreement)（2026-09-16）
  3. [谁来定义人工智能的规则？](https://cohere.com/blog/who-gets-to-define-the-rules-for-ai)（2026-09-13）
  4. [推出 North Small Translate：领先的主权开放权重机器翻译模型，性能出众、体积适中，为速度与成本效率而生。](https://cohere.com/blog/north-small-translate)（2026-09-10）
  5. [North Mini Code 的巨型内核服务引擎内部](https://cohere.com/blog/megakernels)（2026-09-08）
  - 📄 完整文章归档（共 31 篇）：[cohere.md](llm-news/cohere.md)

### Meta Llama (meta_llama)
- 页面：[官方博客](https://ai.meta.com/blog/)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 [RSS/Atom 订阅源](https://about.fb.com/news/tag/ai/feed/)：`https://about.fb.com/news/tag/ai/feed/`
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
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
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [您的代理人完成了任务。它会再次这样做吗？](https://huggingface.co/blog/ibm-research/altk-evolve-consistency)（2026-09-15）
  2. [跨 HF 作业使用 LoRA 的异步 GRPO：存储桶、代理，无 NCCL](https://huggingface.co/blog/asyncgrpo-lora-hfjobs)（2026-09-10）
  3. [用 Gradio 工作流重建 AUTOMATIC1111](https://huggingface.co/blog/gradio-workflow-1111)（2026-09-10）
  4. [IBM 发布采用商业友好许可证的 SOTA 模型 Granite Time Series PatchTST-FM-r2](https://huggingface.co/blog/ibm-research/ibm-releases-sota-granite-time-series)（2026-09-09）
  5. [安全为了谁？拒绝主题的正确子集，而非整个主题](https://huggingface.co/blog/MultiverseComputingCAI/safety-for-whom)（2026-09-08）
  - 📄 完整文章归档（共 863 篇）：[huggingface.md](llm-news/huggingface.md)

### Cloudflare Workers AI (cloudflare_workers_ai)
- 📡 [RSS/Atom 订阅源](https://developers.cloudflare.com/workers-ai/changelog/index.xml)：`https://developers.cloudflare.com/workers-ai/changelog/index.xml`
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [Workers AI - GLM-5.2 现已登陆 Workers AI](https://developers.cloudflare.com/workers-ai/changelog/#glm-52-now-available-on-workers-ai)（2026-06-16）
  2. [Workers AI - Moonshot AI Kimi K2.7 Code 现已登陆 Workers AI](https://developers.cloudflare.com/workers-ai/changelog/#moonshot-ai-kimi-k27-code-now-available-on-workers-ai)（2026-06-12）
  3. [Workers AI - 计划中的模型弃用](https://developers.cloudflare.com/workers-ai/changelog/#planned-model-deprecations)（2026-05-08）
  4. [Workers AI - Moonshot AI Kimi K2.6 现已登陆 Workers AI](https://developers.cloudflare.com/workers-ai/changelog/#moonshot-ai-kimi-k26-now-available-on-workers-ai)（2026-04-20）
  5. [Workers AI - Google Gemma 4 26B A4B 现已登陆 Workers AI](https://developers.cloudflare.com/workers-ai/changelog/#google-gemma-4-26b-a4b-now-available-on-workers-ai)（2026-04-04）
  - 📄 完整文章归档（共 35 篇）：[cloudflare_workers_ai.md](llm-news/cloudflare_workers_ai.md)

### OpenRouter (openrouter)
- 📡 [RSS/Atom 订阅源](https://openrouter.ai/blog/feed.xml)：`https://openrouter.ai/blog/feed.xml`
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [Is Seedance Open Source?](https://openrouter.ai/blog/insights/seedance-2-5-open-source/)（2026-09-25）
  2. [Is Kimi K3 Open Source? Weights, License, and How to Call It](https://openrouter.ai/blog/insights/kimi-k3-open-source/)（2026-09-24）
  3. [Best Embedding Models in 2026](https://openrouter.ai/blog/insights/best-embedding-models-2026/)（2026-09-23）
  4. [How to Use Jev: Moderation with the Jev API in TypeScript](https://openrouter.ai/blog/tutorials/how-to-use-jev/)（2026-09-23）
  5. [Batch API: half-price inference by bundling requests](https://openrouter.ai/blog/announcements/batch-api/)（2026-09-22）
  - 📄 完整文章归档（共 140 篇）：[openrouter.md](llm-news/openrouter.md)

### Cerebras (cerebras)
- 页面：[官方博客](https://www.cerebras.ai/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-cerebras.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-cerebras.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [Introducing CS-4: The Fastest AI Accelerator in the Industry Learn more >>](https://www.cerebras.ai/blog/introducing-cerebras-cs-4)
  2. [Why Cyber Defense Needs Faster Inference](https://www.cerebras.ai/blog/why-cyber-defense-needs-faster-inference)
  3. [The rise of slow personal assistants](https://www.cerebras.ai/blog/the-rise-of-slow-personal-assistants)
  4. [We Taught an AI Agent to QA Our Cloud Console — in Plain English](https://www.cerebras.ai/blog/we-taught-an-ai-agent-to-qa-our-cloud-console-in-plain-english)
  5. [How Cerebras serves GPT-5.6 Sol at up to 750 tokens per second](https://www.cerebras.ai/blog/how-cerebras-serves-gpt-5-6-sol-at-up-to-750-tokens-per-second)
  - 📄 完整文章归档（共 49 篇）：[cerebras.md](llm-news/cerebras.md)

### Amazon Bedrock (aws_bedrock)
- 📡 [RSS/Atom 订阅源](https://aws.amazon.com/blogs/machine-learning/feed/)：`https://aws.amazon.com/cn/blogs/machine-learning/feed/`
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [Scaling MoE reinforcement learning on Amazon EKS with EFA and DeepEP with 40% more throughput](https://aws.amazon.com/blogs/machine-learning/scaling-moe-reinforcement-learning-on-amazon-eks-with-efa-and-deepep-with-40-more-throughput/)（2026-09-25）
  2. [Accelerate multimodal RL training with SkyRL on Amazon SageMaker HyperPod](https://aws.amazon.com/blogs/machine-learning/accelerate-multimodal-rl-training-with-skyrl-on-amazon-sagemaker-hyperpod/)（2026-09-25）
  3. [NarrateAI: production-ready LLM quality assurance on Amazon Bedrock](https://aws.amazon.com/blogs/machine-learning/narrateai-production-ready-llm-quality-assurance-on-amazon-bedrock/)（2026-09-25）
  4. [Deploying real-time personalized speech with Qwen3-TTS on Amazon SageMaker AI](https://aws.amazon.com/blogs/machine-learning/deploying-real-time-personalized-speech-with-qwen3-tts-on-amazon-sagemaker-ai/)（2026-09-25）
  5. [How Datacor built self-service rental analytics with Amazon Quick Sight](https://aws.amazon.com/blogs/machine-learning/how-datacor-built-self-service-rental-analytics-with-amazon-quick-sight/)（2026-09-25）
  - 📄 完整文章归档（共 20 篇）：[aws_bedrock.md](llm-news/aws_bedrock.md)

### Fireworks AI (fireworks_ai)
- 页面：[官方博客](https://fireworks.ai/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-fireworks_ai.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-fireworks_ai.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [Every byte counts: ARCv3 and the case for cross-region RL](https://fireworks.ai/blog/arcv3-and-the-case-for-cross-region-rl)
  2. [Introducing The Specialized Intelligence Index](https://fireworks.ai/blog/introducing-the-specialized-intelligence-index)
  3. [The frontier isn’t a model. It’s a router.](https://fireworks.ai/blog/the-frontier-isnt-a-model-its-a-router)
  4. [Phylo brings frontier AI to more scientists with open models on Fireworks](https://fireworks.ai/blog/phylo-brings-frontier-ai-to-more-scientists-with-open-models-on-fireworks)
  5. [DeepSeek-V4.1-Flash on Fireworks: Astra-level DeepSWE at 1/15th the cost](https://fireworks.ai/blog/DeepSeek-V4.1-Flash-Astra)
  - 📄 完整文章归档（共 21 篇）：[fireworks_ai.md](llm-news/fireworks_ai.md)

### Together AI (together_ai)
- 📡 [RSS/Atom 订阅源](https://www.together.ai/blog/rss.xml)：`https://www.together.ai/blog/rss.xml`
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [How to train your own Jev for $17](https://www.together.ai/blog/how-to-train-your-own-jev)（2026-09-23）
  2. [Canary rollouts: upgrade models in production without downtime](https://www.together.ai/blog/canary-rollouts-upgrade-models-in-production-without-downtime)（2026-09-22）
  3. [How a global fintech scaled coding agent traffic with Dedicated Model Inference](https://www.together.ai/blog/global-fintech-scales-coding-agent-traffic-with-dedicated-model-inference)（2026-09-18）
  4. [Migrating from closed to open source models, Together](https://www.together.ai/blog/migrating-from-closed-to-open-source-models)（2026-09-16）
  5. [Together AI expands fine-tuning service with more models, live metrics, and finer controls](https://www.together.ai/blog/together-ai-expands-fine-tuning-service-with-more-models-live-metrics-and-finer-controls)（2026-09-11）
  - 📄 完整文章归档（共 81 篇）：[together_ai.md](llm-news/together_ai.md)

### DeepInfra (deepinfra)
- 页面：[官方博客](https://deepinfra.com/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-deepinfra.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-deepinfra.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [AI Model Calibration: The Benchmark Nobody Optimizes](https://deepinfra.com/blog/ai-model-calibration-benchmark)（2026-09-25）
  2. [Token Verbosity Is the New Pricing War](https://deepinfra.com/blog/token-verbosity)（2026-09-25）
  3. [Model Deprecation: Build LLM Apps That Last](https://deepinfra.com/blog/model-deprecation-llm-apps)（2026-09-24）
  4. [Design Your Next Website With AI: A Prompting Guide for Ming-Image](https://deepinfra.com/blog/ming-design-with-ai)（2026-09-23）
  5. [Two-Tier AI Agents: Why You Need Two Models](https://deepinfra.com/blog/two-tier-agent-two-models)（2026-09-22）
  - 📄 完整文章归档（共 7 篇）：[deepinfra.md](llm-news/deepinfra.md)

### 美团 LongCat (longcat_meituan)
- 页面：[更新日志](https://longcat.chat/platform/docs/zh/ChangeLog.html)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-longcat_meituan.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-longcat_meituan.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [LongCat-2.5-Preview 上线](https://longcat.chat/platform/docs/zh/ChangeLog.html#%E7%89%88%E6%9C%AC-2026-09-25)（2026-09-25）
  2. [LongCat-2.5-Preview 上线](https://longcat.chat/platform/docs/zh/ChangeLog.html#%E7%89%88%E6%9C%AC-2026-09-25-1)（2026-09-25）
  3. [全新推出企业服务](https://longcat.chat/platform/docs/zh/ChangeLog.html#%E7%89%88%E6%9C%AC-2026-09-10)（2026-09-10）
  4. [全新推出企业服务](https://longcat.chat/platform/docs/zh/ChangeLog.html#%E7%89%88%E6%9C%AC-2026-09-02)（2026-09-02）
  5. [LongCat-2.0 发布 &amp; 全新推出计费服务](https://longcat.chat/platform/docs/zh/ChangeLog.html#%E7%89%88%E6%9C%AC-2026-06-30)（2026-06-30）
  - 📄 完整文章归档（共 15 篇）：[longcat_meituan.md](llm-news/longcat_meituan.md)

### StreamLake (streamlake)
- 页面：[更新日志](https://www.streamlake.com/document/WANQING/mdptalisb06i7ai3zdd)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-streamlake.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-streamlake.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [【新增】数据分析任务完成后可将结果下载至本地，便于进一步处理与留存数据](https://www.streamlake.com/document/WANQING/mdptalisb06i7ai3zdd#t2026-08-14-0)（2026-08-14）
  2. [【新增】新增 Python 代码节点，支持灵活编写自定义处理逻辑，满足个性化数据加工需求](https://www.streamlake.com/document/WANQING/mdptalisb06i7ai3zdd#t2026-07-22-1)（2026-07-22）
  3. [【新增】新增 GLM-5.2-FP8 模型部署能力，支持预付费、后付费模式，丰富模型部署选择](https://www.streamlake.com/document/WANQING/mdptalisb06i7ai3zdd#t2026-07-03-2)（2026-07-03）
  4. [【优化】文本生成模型推理点监控新增缓存命中率曲线，支持 Cache命中率及 Cache token 数量等指标](https://www.streamlake.com/document/WANQING/mdptalisb06i7ai3zdd#t2026-07-03-3)（2026-07-03）
  5. [【优化】推理监控输入输出token卡片增加影响因子数据，用户可直接查看因子维度token消耗](https://www.streamlake.com/document/WANQING/mdptalisb06i7ai3zdd#t2026-06-30-4)（2026-06-30）
  - 📄 完整文章归档（共 23 篇）：[streamlake.md](llm-news/streamlake.md)

### 数眼智能 (dataeye)
- 页面：[官方博客](https://www.shuyanai.com/blogs)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-dataeye.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-dataeye.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [数眼智能完成数千万元天使轮融资，加速企业级大模型部署能力建设](https://www.shuyanai.com/blogs#d-2026-09-21-3)（2026-09-21）
  2. [数眼智能完成数千万元天使轮融资，加速企业级大模型部署能力建设](https://www.shuyanai.com/blogs#d-2026-09-21-4)（2026-09-21）
  3. [数眼智能AI漫剧教程：从脚本、AI生图到Seedance 2.5生视频](https://www.shuyanai.com/blogs#d-2026-09-17-5)（2026-09-17）
  4. [数眼智能 AI 视频生成教程：如何用智能体生成第一条视频？](https://www.shuyanai.com/blogs#d-2026-09-16-6)（2026-09-16）
  5. [数眼智能在海南数据谷OPC社区揭牌现场｜把 Token 级算力，送到每一个 AI 超级个体手里](https://www.shuyanai.com/blogs#d-2026-09-16-7)（2026-09-16）
  - 📄 完整文章归档（共 20 篇）：[dataeye.md](llm-news/dataeye.md)

### AI21 Labs (ai21_labs)
- 页面：[官方博客](https://www.ai21.com/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-ai21_labs.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-ai21_labs.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [You don’t need a frontier model. You need a verifier.](https://www.ai21.com/blog/#d-2026-08-19-0)（2026-08-19）
  2. [Better and cheaper together: Open models explore, frontier models patch](https://www.ai21.com/blog/#d-2026-07-15-1)（2026-07-15）
  3. [Improving Best-of-N with Budget-Aware Execution for SWE Agents](https://www.ai21.com/blog/#d-2026-07-07-2)（2026-07-07）
  4. [Token spend isn’t going down. You need more than naive routing to manage it](https://www.ai21.com/blog/#d-2026-06-25-3)（2026-06-25）
  5. [Tipping the scales: Merging weak agents into a state-of-the-art deep researcher](https://www.ai21.com/blog/#d-2026-06-24-4)（2026-06-24）
  - 📄 完整文章归档（共 13 篇）：[ai21_labs.md](llm-news/ai21_labs.md)

### Jina AI (jina_ai)
- 页面：[官方博客](https://jina.ai/news/)
  - 📡 RSS/Atom：https://jina.ai/feed.rss
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [jina-embeddings-v5-omni: Embeddings for Text, Image, Audio and VideoOne model, four modalities: text, image, audio, video. Best-in-class omni embeddings in 1.6B and 0.9B.](https://jina.ai/news/jina-embeddings-v5-omni-multimodal-embeddings-for-text-image-audio-and-video)（2026-05-12）
  2. [7 minutes readBootstrapping Audio Embeddings from Multimodal LLMsTurn any multimodal LLM into a small audio embedding model that beats CLAP with 25x less data.](https://jina.ai/news/bootstrapping-audio-embeddings-from-multimodal-llms)（2026-03-11）
  3. [6 minutes readIdentifying Embedding Models from Raw Numerical ValuesA tiny transformer that fingerprints embedding models by reading raw numerical digits. No feature engineering.](https://jina.ai/news/identifying-embedding-models-from-raw-numerical-values)（2026-03-06）
  4. [7 minutes readJina-VLM: Small Multilingual Vision Language ModelNew 2B vision language model achieves SOTA on multilingual VQA, no catastrophic forgetting on text-only tasks.](https://jina.ai/news/jina-vlm-small-multilingual-vision-language-model)（2025-12-04）
  5. [11 minutes readMultimodal Embeddings in Llama.cpp and GGUFWe brought multimodal embeddings to llama.cpp and GGUF, and uncovered a few surprising issues along the way.](https://jina.ai/news/multimodal-embeddings-in-llama-cpp-and-gguf)（2025-09-09）
  - 📄 完整文章归档（共 6 篇）：[jina_ai.md](llm-news/jina_ai.md)

### Poolside (poolside)
- 页面：[官方博客](https://poolside.ai/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-poolside.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-poolside.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [Poolside on Dell: an efficient path for frontier AI inside your boundary](https://poolside.ai/blog#d-2026-07-28-34)（2026-07-28）
  2. [Poolside on Dell: an efficient path for frontier AI inside your boundary](https://poolside.ai/blog#d-2026-07-28-35)（2026-07-28）
  3. [Introducing Laguna XS 2.1](https://poolside.ai/blog#d-2026-07-21-18)（2026-07-21）
  4. [Introducing Laguna XS 2.1](https://poolside.ai/blog#d-2026-07-21-19)（2026-07-21）
  5. [Long context update: Laguna XS.2 and M.1](https://poolside.ai/blog#d-2026-07-02-20)（2026-07-02）
  - 📄 完整文章归档（共 38 篇）：[poolside.md](llm-news/poolside.md)

### Modular (原 BentoCloud/BentoML) (modular_cloud)
- 📡 [RSS/Atom 订阅源](https://www.modular.com/blog/rss.xml)：`https://www.modular.com/blog/rss.xml`
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [模块化：模块化 26.6：开放编译器贡献、音频生成和扩展模型支持](https://www.modular.com/blog/modular-26-6-open-compiler-contributions-audio-generation-and-expanded-model-support)（2026-09-17）
  2. [模块化：Mojo🔥 现已开源！](https://www.modular.com/blog/mojo-open-source)（2026-08-18）
  3. [模块化：模块化和高通：相同的代码，新的芯片](https://www.modular.com/blog/modcon-qualcomm)（2026-08-18）
  4. [模块化：ModCon 2026：开源、开放云、开放芯片](https://www.modular.com/blog/modcon-announcements)（2026-08-18）
  5. [Modular：Modular 26.5：Mojo 1.0 来了！](https://www.modular.com/blog/modular-26-5-mojo-1-0-is-here)（2026-08-11）
  - 📄 完整文章归档（共 100 篇）：[modular_cloud.md](llm-news/modular_cloud.md)

### 小米 MiMo (xiaomi_mimo)
- 页面：[更新日志](https://mimo.mi.com/docs/zh-CN/updates/model)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 页面：[更新日志](https://mimo.mi.com/docs/zh-CN/updates/feature/platform)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 页面：[更新日志](https://mimo.mi.com/docs/zh-CN/news)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-xiaomi_mimo.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-xiaomi_mimo.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [2026-09-22 MiMo-V2.6 系列发布](https://mimo.mi.com/docs/zh-CN/updates/model#2026-09-22-mimo-v26-%E7%B3%BB%E5%88%97%E5%8F%91%E5%B8%83)（2026-09-22）
  2. [2026-9-22 批量推理（Batch API）功能上线](https://mimo.mi.com/docs/zh-CN/updates/feature/platform#2026-9-22--%E6%89%B9%E9%87%8F%E6%8E%A8%E7%90%86batch-api%E5%8A%9F%E8%83%BD%E4%B8%8A%E7%BA%BF)（2026-09-22）
  3. [2026-9-15 新增站内信功能](https://mimo.mi.com/docs/zh-CN/updates/feature/platform#2026-9-15--%E6%96%B0%E5%A2%9E%E7%AB%99%E5%86%85%E4%BF%A1%E5%8A%9F%E8%83%BD)（2026-09-15）
  4. [2026-6-23 支持 OpenAI Responses API](https://mimo.mi.com/docs/zh-CN/updates/feature/platform#2026-6-23-%E6%94%AF%E6%8C%81-openai-responses-api)（2026-06-23）
  5. [2026-6-11 邀请有礼活动升级](https://mimo.mi.com/docs/zh-CN/updates/feature/platform#2026-6-11-%E9%82%80%E8%AF%B7%E6%9C%89%E7%A4%BC%E6%B4%BB%E5%8A%A8%E5%8D%87%E7%BA%A7)（2026-06-11）
  - 📄 完整文章归档（共 38 篇）：[xiaomi_mimo.md](llm-news/xiaomi_mimo.md)

### Anyscale (anyscale)
- 📡 [RSS/Atom 订阅源](https://www.anyscale.com/rss.xml)：`https://www.anyscale.com/rss.xml`
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [Ray Summit 2026: Physical AI, RL, and the infrastructure that runs them all](https://anyscale.com/blog/ray-summit-2026-recap)（2026-09-08）
  2. [Scaling Ray for AI workloads to 10k node clusters](https://anyscale.com/blog/how-we-scaled-ray-from-batch-inference-to-10000-node-training-clusters)（2026-08-25）
  3. [Optimizing LLM Serving Efficiency: Moving Beyond KV Cache Reuse to Token-Load Awareness with Ray Serve LLM](https://anyscale.com/blog/llm-kv-token-aware-routing)（2026-08-25）
  4. [Introducing Ray History Server: Post-Mortem Observability for Ray on Kubernetes](https://anyscale.com/blog/ray-history-server)（2026-08-25）
  5. [Learning Loops: The Path to Owning Your Intelligence](https://anyscale.com/blog/learning-loops)（2026-08-25）
  - 📄 完整文章归档（共 19 篇）：[anyscale.md](llm-news/anyscale.md)

### InceptionLabs (inception_labs)
- 页面：[官方博客](https://www.inceptionlabs.ai/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-inception_labs.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-inception_labs.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [Introducing Mercury 2.5|Read the blog](https://www.inceptionlabs.ai/blog/introducing-mercury-2-5)（2026-09-24）
  2. [Mercury 2 for Search: Fast enough to run a hundred times per queryRead story](https://www.inceptionlabs.ai/blog/mercury-2-for-search)
  3. [More builders. More throughput. Better Mercury 2.Read story](https://www.inceptionlabs.ai/blog/mercury-2-10x-free-tokens)
  4. [Mercury 2: the first reasoning model fast enough to pick up the phoneRead story](https://www.inceptionlabs.ai/blog/mercury-2-the-first-reasoning-model-fast-enough-to-pick-up-the-phone)
  5. [Mercury 2 on Azure Foundry](https://www.inceptionlabs.ai/blog/mercury-2-on-azure-foundry)
  - 📄 完整文章归档（共 12 篇）：[inception_labs.md](llm-news/inception_labs.md)

### Inference.net (inference_net)
- 页面：[官方博客](https://inference.net/blog/)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-inference_net.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-inference_net.xml)
- 📰 **最新文章**（官方源抓取于 2026-09-26，标题自动汉化）：
  1. [Schematron V2: Frontier HTML-to-JSON extraction at a fraction of the cost](https://inference.net/blog/#d-2026-08-05-0)（2026-08-05）
  2. [Introducing Inference platform: Monitor, train, and deploy self-improving AI models](https://inference.net/blog/#d-2026-04-16-1)（2026-04-16）
  3. [How Inference.net trains Specialized Language Models that cut AI costs by up to 50x](https://inference.net/blog/#d-2026-04-14-2)（2026-04-14）
  4. [Specialized LLMs: The model you need doesn't exist yet](https://inference.net/blog/#d-2026-03-11-3)（2026-03-11）
  5. [Project OSSAS: Custom LLMs to process 100 Million Research Papers](https://inference.net/blog/#d-2026-02-05-4)（2026-02-05）
  - 📄 完整文章归档（共 9 篇）：[inference_net.md](llm-news/inference_net.md)

---
共整理 35 个厂商的动态入口（其中 35 个成功提取最新文章），RSS/Atom 源 15 个。

<!-- LLM-NEWS:END -->
