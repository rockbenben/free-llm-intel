# LLM 厂商博客 / 更新动态订阅源

<!-- LLM-NEWS:BEGIN  本章节由 crawler_llm_intel.py 自动生成，请勿手工修改 -->

## 厂商博客 / 更新动态订阅源

> 由 `crawler_llm_intel.py` 自动整理，最近更新：**2026-10-05 01:06:34**。
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
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [GPT-6.1 Sol 发布](https://openai.com/index/introducing-gpt-6-1-sol)（2026-09-29）
  2. [为 GPT-6 提供更好的提示缓存](https://openai.com/index/better-prompt-caching-for-gpt-6)（2026-09-22）
  3. [介绍 GPT-6 Sol 与 Luna](https://openai.com/index/introducing-gpt-6-sol-and-luna)（2026-09-22）
  4. [澳大利亚青少年安全蓝图简介](https://openai.com/index/australian-youth-safety-blueprint)（2026-09-18）
  5. [推出面向法律行业的 Astra](https://openai.com/index/astra-for-law)（2026-09-17）
  - 📄 完整文章归档（共 1213 篇）：[openai.md](llm-news/openai.md)

### Anthropic Claude (anthropic)
- 页面：[官方博客](https://claude.com/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 页面：[新闻 / 更新](https://www.anthropic.com/news)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-anthropic.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-anthropic.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [Claude政府现已普遍可用](https://claude.com/blog#d-2026-10-01-19)（2026-10-01）
  2. [Introducing Claude Opus 5.5](https://www.anthropic.com/news#d-2026-09-28-0)（2026-09-28）
  3. [Claude Tag 现已支持频道中的个人连接器](https://claude.com/blog/claude-tag-now-supports-personal-connectors-in-channels)（2026-09-24）
  4. [Claude Marketplace：发现合作伙伴插件、智能体与服务的一站式入口](https://claude.com/blog#d-2026-09-23-23)（2026-09-23）
  5. [Claude Marketplace：从我们的合作伙伴那里发现插件、智能体和服务的地方](https://claude.com/blog#d-2026-09-23-21)（2026-09-23）
  - 📄 完整文章归档（共 78 篇）：[anthropic.md](llm-news/anthropic.md)

### Google Gemini (google_gemini)
- 页面：[变更日志](https://ai.google.dev/gemini-api/docs/changelog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-google_gemini.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-google_gemini.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [Gemini 3.8 Flash TTS 和 Gemini 3.8 Flash-Lite TTS 正式版 (GA)](https://ai.google.dev/gemini-api/docs/changelog?hl=zh-cn#09-22-2026-1)（2026-09-22）
  2. [Antigravity 09-2026](https://ai.google.dev/gemini-api/docs/changelog?hl=zh-cn#09-17-2026-1)（2026-09-17）
  3. [Gemini 3.8 Live 和 Gemini 3.8 Live Extended Thinking 正式版 (GA)](https://ai.google.dev/gemini-api/docs/changelog?hl=zh-cn#09-15-2026-1)（2026-09-15）
  4. [Gemini 3.8 Live 扩展思考](https://ai.google.dev/gemini-api/docs/changelog?hl=zh-cn#09-15-2026-2)（2026-09-15）
  5. [Lyria 3.5 正式版 (GA)](https://ai.google.dev/gemini-api/docs/changelog?hl=zh-cn#09-03-2026-1)（2026-09-03）
  - 📄 完整文章归档（共 41 篇）：[google_gemini.md](llm-news/google_gemini.md)

### xAI Grok (xai_grok)
- 页面：[新闻 / 更新](https://x.ai/news)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-xai_grok.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-xai_grok.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [Team Bots：向你的团队学习的 AI 同事](https://x.ai/news#d-2026-09-28-1)（2026-09-28）
  2. [SpaceXAI 如何使用 Grok Bot 扩展客户支持](https://x.ai/news/grok-bot-customer-support)（2026-09-22）
  3. [IntroducingGrok 4.7](https://x.ai/news#d-2026-09-21-0)（2026-09-21）
  4. [推出 Grok 4.7](https://x.ai/news/grok-4-7)（2026-09-21）
  5. [推出 Grok Voice Transcribe 2.0](https://x.ai/news/grok-voice-transcribe-2)（2026-09-18）
  - 📄 完整文章归档（共 113 篇）：[xai_grok.md](llm-news/xai_grok.md)

### Groq Cloud (groq)
- 页面：[变更日志](https://console.groq.com/docs/changelog.md)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-groq.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-groq.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [2026 年第一季度变更日志条目](https://github.com/groq/groq-changelog/commit/abaa8395286b622a837adb5d6b44709845d1edba)（2026-05-06）
  2. [MiniMax M2.5 与 Qwen3-VL 32B Instruct 上线（企业版）](https://console.groq.com/docs/changelog.md#minimax-m25-and-qwen3vl-32b-instruct-enterprise)（2026-04-18）
  3. [Orpheus Arabic Saudi 新增语音](https://console.groq.com/docs/changelog.md#new-voices-for-orpheus-arabic-saudi)（2026-04-18）
  4. [Python SDK v1.2.0 and TypeScript SDK v1.1.2](https://console.groq.com/docs/changelog.md#python-sdk-v120-and-typescript-sdk-v112)（2026-04-18）
  5. [Groq 是首批将 NVIDIA Groq 3 LPX 和 Vera Rubin NVL72 推向市场的公司之一](https://groq.com/blog/groq-among-the-first-to-bring-nvidia-groq-3-lpx-and-vera-rubin-nvl72-to-market)（2026-03-24）
  - 📄 完整文章归档（共 68 篇）：[groq.md](llm-news/groq.md)

### DeepSeek (deepseek)
- 页面：[更新日志](https://api-docs.deepseek.com/zh-cn/updates/)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 页面：[版本动态](https://api-docs.deepseek.com/zh-cn/news/news260424/)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-deepseek.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-deepseek.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [DeepSeek-V4.1-Flash 发布](https://api-docs.deepseek.com/zh-cn/updates/#%E6%97%B6%E9%97%B4-2026-09-10)（2026-09-10）
  2. [DeepSeek V4.1 Flash：更强、更快、更普惠](https://api-docs.deepseek.com/zh-cn/news/news260910)（2026-09-10）
  3. [DeepSeek-V4-Flash-Vision-Exp 发布](https://api-docs.deepseek.com/zh-cn/updates/#%E6%97%B6%E9%97%B4-2026-08-21)（2026-08-21）
  4. [V4-Flash-Vision-Exp 上线，开启多模态 API 服务](https://api-docs.deepseek.com/zh-cn/news/news260821)（2026-08-21）
  5. [DeepSeek-V4-Pro 更新](https://api-docs.deepseek.com/zh-cn/updates/#%E6%97%B6%E9%97%B4-2026-08-13)（2026-08-13）
  - 📄 完整文章归档（共 46 篇）：[deepseek.md](llm-news/deepseek.md)

### 智谱 AI GLM (zhipu_glm)
- 页面：[更新日志](https://docs.bigmodel.cn/cn/update/new-releases)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-zhipu_glm.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-zhipu_glm.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [GLM-5.3-Flash 原生多模态模型上线](https://docs.bigmodel.cn/cn/update/new-releases#2026-08-26)（2026-08-26）
  2. [GLM-5.3 新一代旗舰模型上线](https://docs.bigmodel.cn/cn/update/new-releases#2026-8-19)（2026-08-19）
  3. [GLM-5.2 新一代旗舰模型上线](https://docs.bigmodel.cn/cn/update/new-releases#2026-06-16)（2026-06-16）
  4. [GLM Coding Plan 团队版上线](https://docs.bigmodel.cn/cn/update/new-releases#2026-05-29)（2026-05-29）
  5. [GLM-5.1 新一代旗舰模型上线](https://docs.bigmodel.cn/cn/update/new-releases#2026-04-07)（2026-04-07）
  - 📄 完整文章归档（共 26 篇）：[zhipu_glm.md](llm-news/zhipu_glm.md)

### 通义千问 Qwen (aliyun_qwen)
- 页面：[研究页](https://qwen.ai/research)
  - 🔌 官方未提供 RSS/Atom 订阅源，条目取自官方数据接口
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-aliyun_qwen.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-aliyun_qwen.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [Qwen-Image-2.1：小模强效，创改一体](https://qwen.ai/blog?id=qwen-image-2.1)（2026-09-20）
  2. [Qwen3.8-Omni-Flash：耳聪目明，办事得力](https://qwen.ai/blog?id=qwen3.8-omni-flash)（2026-09-18）
  3. [Qwen3.8-LiveTranslate：知其人，传其义](https://qwen.ai/blog?id=qwen3.8-livetranslate)（2026-09-18）
  4. [Qwen-Drive-1.0：迈向自动驾驶视觉-语言基础模型的初步探索](https://qwen.ai/blog?id=qwen-drive-1.0)（2026-09-03）
  5. [E-Commerce Bench：长程经营，多维评估](https://qwen.ai/blog?id=e-commerce-bench)（2026-09-03）
  - 📄 完整文章归档（共 40 篇）：[aliyun_qwen.md](llm-news/aliyun_qwen.md)

### 腾讯混元 (tencent_hunyuan)
- 页面：[更新日志](https://cloud.tencent.com/document/product/1729/97765)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-tencent_hunyuan.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-tencent_hunyuan.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
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
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
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
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [【接口服务调整】对话模型将忽略 repetition_penalty 参数](https://docs.siliconflow.cn/docs/release-notes/overview#%E6%8E%A5%E5%8F%A3%E6%9C%8D%E5%8A%A1%E8%B0%83%E6%95%B4%E5%AF%B9%E8%AF%9D%E6%A8%A1%E5%9E%8B%E5%B0%86%E5%BF%BD%E7%95%A5-repetition_penalty-%E5%8F%82%E6%95%B0)（2026-09-30）
  2. [【模型服务调整】Nex-N2-Pro、Qwen3.5-397B-A17B、MiniMax-M2.5 等模型将下线](https://docs.siliconflow.cn/docs/release-notes/overview#%E6%A8%A1%E5%9E%8B%E6%9C%8D%E5%8A%A1%E8%B0%83%E6%95%B4nex-n2-proqwen35-397b-a17bminimax-m25-%E7%AD%89%E6%A8%A1%E5%9E%8B%E5%B0%86%E4%B8%8B%E7%BA%BF)（2026-09-30）
  3. [【模型服务调整】ERNIE-Image-Turbo 模型将下线](https://docs.siliconflow.cn/docs/release-notes/overview#%E6%A8%A1%E5%9E%8B%E6%9C%8D%E5%8A%A1%E8%B0%83%E6%95%B4ernie-image-turbo-%E6%A8%A1%E5%9E%8B%E5%B0%86%E4%B8%8B%E7%BA%BF)（2026-09-28）
  4. [【接口服务调整】生图 API 下线 batch_size 字段、水印默认添加](https://docs.siliconflow.cn/docs/release-notes/overview#%E6%8E%A5%E5%8F%A3%E6%9C%8D%E5%8A%A1%E8%B0%83%E6%95%B4%E7%94%9F%E5%9B%BE-api-%E4%B8%8B%E7%BA%BF-batch_size-%E5%AD%97%E6%AE%B5%E6%B0%B4%E5%8D%B0%E9%BB%98%E8%AE%A4%E6%B7%BB%E5%8A%A0)（2026-09-15）
  5. [【模型价格调整】DeepSeek-V4-Flash 模型分时段定价调整](https://docs.siliconflow.cn/docs/release-notes/overview#%E6%A8%A1%E5%9E%8B%E4%BB%B7%E6%A0%BC%E8%B0%83%E6%95%B4deepseek-v4-flash-%E6%A8%A1%E5%9E%8B%E5%88%86%E6%97%B6%E6%AE%B5%E5%AE%9A%E4%BB%B7%E8%B0%83%E6%95%B4)（2026-09-11）
  - 📄 完整文章归档（共 50 篇）：[siliconflow.md](llm-news/siliconflow.md)

### MiniMax (minimax)
- 页面：[更新日志](https://platform.minimax.cn/docs/release-notes/models)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 页面：[更新日志](https://platform.minimax.cn/docs/release-notes/apis)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-minimax.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-minimax.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [MiniMax H3 发布](https://platform.minimax.cn/docs/release-notes/models#2026-%E5%B9%B4-7-%E6%9C%88-31-%E6%97%A5)（2026-07-31）
  2. [介绍 Music-3.0](https://platform.minimax.cn/docs/release-notes/models#2026-%E5%B9%B4-7-%E6%9C%88-16-%E6%97%A5)（2026-07-16）
  3. [MiniMax M3 模型](https://platform.minimax.cn/docs/release-notes/models#2026-%E5%B9%B4-6-%E6%9C%88-1-%E6%97%A5)（2026-06-01）
  4. [Music-2.6](https://platform.minimax.cn/docs/release-notes/models#2026-%E5%B9%B4-4-%E6%9C%88)（2026-04-01）
  5. [MiniMax M2.7](https://platform.minimax.cn/docs/release-notes/models#2026-%E5%B9%B4-3-%E6%9C%88-18-%E6%97%A5)（2026-03-18）
  - 📄 完整文章归档（共 35 篇）：[minimax.md](llm-news/minimax.md)

### 月之暗面 Kimi (moonshot_kimi)
- 页面：[变更日志](https://platform.kimi.com/docs/changelog/changelog/changelog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-moonshot_kimi.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-moonshot_kimi.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
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
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [Mistral x Mozilla：私密、多语言的 AI 浏览](https://mistral.ai/news/mistral-x-mozilla/)（2026-09-16）
  2. [Cloudera 与 Mistral 合作打造主权企业 AI](https://mistral.ai/news/mistral-x-cloudera/)（2026-09-10）
  3. [用 AI 智能体现代化改造复杂的遗留代码。](https://mistral.ai/news/legacy-code-modernization/)（2026-09-09）
  4. [让主权、开放权重的 AI 成为技术前沿](https://mistral.ai/news/mistral-makes-sovereign-open-weight-ai-to-frontier/)（2026-09-08）
  5. [Mistral 携手 HUMAIN](https://mistral.ai/news/mistral-x-humain/)（2026-08-24）
  - 📄 完整文章归档（共 87 篇）：[mistral.md](llm-news/mistral.md)

### Cohere (cohere)
- 页面：[官方博客](https://cohere.com/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-cohere.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-cohere.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [Embed 5 简介——前沿嵌入模型的新系列](https://cohere.com/blog/embed-5)（2026-09-30）
  2. [Cohere 与 OpenText 合作，为政府和受监管行业带来可信赖的智能体 AI](https://cohere.com/blog/cohere-and-open-text-partner-to-bring-trusted-ai)（2026-09-16）
  3. [Cohere 与 Aleph Alpha：跨大西洋主权 AI](https://cohere.com/blog/cohere-and-aleph-alpha-sign-agreement)（2026-09-16）
  4. [谁来定义人工智能的规则？](https://cohere.com/blog/who-gets-to-define-the-rules-for-ai)（2026-09-13）
  5. [推出 North Small Translate：领先的主权开放权重机器翻译模型，性能出众、体积适中，为速度与成本效率而生。](https://cohere.com/blog/north-small-translate)（2026-09-10）
  - 📄 完整文章归档（共 32 篇）：[cohere.md](llm-news/cohere.md)

### Meta Llama (meta_llama)
- 页面：[官方博客](https://ai.meta.com/blog/)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 [RSS/Atom 订阅源](https://about.fb.com/news/tag/ai/feed/)：`https://about.fb.com/news/tag/ai/feed/`
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [推出 Meta 企业平台](https://about.fb.com/news/2026/09/launching-meta-enterprise-platform/)（2026-09-28）
  2. [介绍 Ray-Ban Meta Audio 及更多 AI 眼镜款式](https://about.fb.com/news/2026/09/introducing-ray-ban-meta-audio-glasses-new-styles-plus-muse/)（2026-09-23）
  3. [加拿大初创公司 smartARM 利用人工智能打造直观的仿生假肢](https://about.fb.com/news/2026/09/canadian-start-up-smartarm-uses-ai-to-create-intuitive-bionic-prosthetics/)（2026-09-16）
  4. [推出 Meta One：用更多功能与 AI 创作、连接、脱颖而出的订阅服务](https://about.fb.com/news/2026/09/introducing-meta-one-subscription-service-more-features-ai/)（2026-09-15）
  5. [推出 Muse：全球首个为人人打造的个人 AI 智能体](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/)（2026-09-08）
  - 📄 完整文章归档（共 17 篇）：[meta_llama.md](llm-news/meta_llama.md)

### Hugging Face (huggingface)
- 页面：[官方博客](https://huggingface.co/blog)
  - 📡 RSS/Atom：https://huggingface.co/blog/feed.xml
- 📡 [RSS/Atom 订阅源](https://huggingface.co/blog/feed.xml)：`https://huggingface.co/blog/feed.xml`
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [Olmo-core 3 简介：面向大型 MoE 的开放、可扩展的培训基础设施](https://huggingface.co/blog/allenai/olmocore3)（2026-10-01）
  2. [你的智能体出色完成了任务，还能再现吗？](https://huggingface.co/blog/ibm-research/altk-evolve-consistency)（2026-09-15）
  3. [跨 HF Jobs 用 LoRA 的异步 GRPO：一个存储桶、一个代理、没有 NCCL](https://huggingface.co/blog/asyncgrpo-lora-hfjobs)（2026-09-10）
  4. [用 Gradio 工作流重建 AUTOMATIC1111](https://huggingface.co/blog/gradio-workflow-1111)（2026-09-10）
  5. [IBM 发布采用商业友好许可证的 SOTA 模型 Granite Time Series PatchTST-FM-r2](https://huggingface.co/blog/ibm-research/ibm-releases-sota-granite-time-series)（2026-09-09）
  - 📄 完整文章归档（共 864 篇）：[huggingface.md](llm-news/huggingface.md)

### Cloudflare Workers AI (cloudflare_workers_ai)
- 📡 [RSS/Atom 订阅源](https://developers.cloudflare.com/workers-ai/changelog/index.xml)：`https://developers.cloudflare.com/workers-ai/changelog/index.xml`
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [Workers AI - GLM-5.2 现已登陆 Workers AI](https://developers.cloudflare.com/workers-ai/changelog/#glm-52-now-available-on-workers-ai)（2026-06-16）
  2. [Workers AI - Moonshot AI Kimi K2.7 Code 现已登陆 Workers AI](https://developers.cloudflare.com/workers-ai/changelog/#moonshot-ai-kimi-k27-code-now-available-on-workers-ai)（2026-06-12）
  3. [Workers AI - 计划中的模型弃用](https://developers.cloudflare.com/workers-ai/changelog/#planned-model-deprecations)（2026-05-08）
  4. [Workers AI - Moonshot AI Kimi K2.6 现已登陆 Workers AI](https://developers.cloudflare.com/workers-ai/changelog/#moonshot-ai-kimi-k26-now-available-on-workers-ai)（2026-04-20）
  5. [Workers AI - Google Gemma 4 26B A4B 现已登陆 Workers AI](https://developers.cloudflare.com/workers-ai/changelog/#google-gemma-4-26b-a4b-now-available-on-workers-ai)（2026-04-04）
  - 📄 完整文章归档（共 35 篇）：[cloudflare_workers_ai.md](llm-news/cloudflare_workers_ai.md)

### OpenRouter (openrouter)
- 📡 [RSS/Atom 订阅源](https://openrouter.ai/blog/feed.xml)：`https://openrouter.ai/blog/feed.xml`
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [Server-Side Code Execution Tools for AI Agents, Compared](https://openrouter.ai/blog/insights/server-side-code-execution-tools-for-ai-agents-compared/)（2026-10-05）
  2. [代理框架比较：工具调用架构处理](https://openrouter.ai/blog/insights/agent-frameworks-compared-tool-calling-schema-handling/)（2026-10-02）
  3. [LangChain vs CrewAI：编排与 OpenRouter-原生路由的比较](https://openrouter.ai/blog/insights/langchain-vs-crewai-orchestration-compared-to-openrouter-native-routing/)（2026-10-02）
  4. [模型路由器基准](https://openrouter.ai/blog/announcements/model-router-benchmarks/)（2026-10-02）
  5. [支持机器人的模型路由：廉价优先的常见问题解答处理](https://openrouter.ai/blog/tutorials/model-routing-for-support-bots-cheap-first-faq-handling/)（2026-10-02）
  - 📄 完整文章归档（共 154 篇）：[openrouter.md](llm-news/openrouter.md)

### Cerebras (cerebras)
- 页面：[官方博客](https://www.cerebras.ai/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-cerebras.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-cerebras.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [推出 Cerebras CS-4：最快的 AI 又更快了](https://www.cerebras.ai/blog/introducing-cerebras-cs-4)
  2. [从头开始的分类推理](https://www.cerebras.ai/blog/disaggregated-inference-from-the-ground-up)
  3. [AlphaSense 如何使用快速推理使代理研究互动](https://www.cerebras.ai/blog/how-alphasense-uses-fast-inference-to-make-agentic-research-interactive)
  4. [为什么网络防御需要更快的推理](https://www.cerebras.ai/blog/why-cyber-defense-needs-faster-inference)
  5. [慢速私人助理的兴起](https://www.cerebras.ai/blog/the-rise-of-slow-personal-assistants)
  - 📄 完整文章归档（共 51 篇）：[cerebras.md](llm-news/cerebras.md)

### Amazon Bedrock (aws_bedrock)
- 📡 [RSS/Atom 订阅源](https://aws.amazon.com/blogs/machine-learning/feed/)：`https://aws.amazon.com/cn/blogs/machine-learning/feed/`
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [使用 Amazon Quick 和裁决查询模式扫描数千个租赁的合规性](https://aws.amazon.com/blogs/machine-learning/sweep-thousands-of-leases-for-compliance-using-amazon-quick-and-the-adjudicated-query-pattern/)（2026-10-02）
  2. [使用 Amazon Bedrock AgentCore 将安全 Web 搜索添加到 Claude Desktop](https://aws.amazon.com/blogs/machine-learning/add-secure-web-search-to-claude-desktop-with-amazon-bedrock-agentcore/)（2026-10-02）
  3. [在 Amazon SageMaker AI 上使用多轮 RL 微调搜索代理](https://aws.amazon.com/blogs/machine-learning/fine-tune-a-search-agent-with-multi-turn-rl-on-amazon-sagemaker-ai/)（2026-10-02）
  4. [在 Amazon Bedrock AgentCore 上使用代理 AI 扩展云迁移](https://aws.amazon.com/blogs/machine-learning/scaling-cloud-migrations-with-agentic-ai-on-amazon-bedrock-agentcore/)（2026-10-01）
  5. [使用 Amazon Quick 在 AI 构建的应用程序中提供实时、受管控的数据](https://aws.amazon.com/blogs/machine-learning/serve-live-governed-data-in-ai-built-apps-with-amazon-quick/)（2026-10-01）
  - 📄 完整文章归档（共 46 篇）：[aws_bedrock.md](llm-news/aws_bedrock.md)

### Fireworks AI (fireworks_ai)
- 页面：[官方博客](https://fireworks.ai/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-fireworks_ai.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-fireworks_ai.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [强化学习：为什么数字和 MoE 路由的对齐很重要](https://fireworks.ai/blog/reinforcement-learning-why-alignment-of-numerics-and-MoE-routing-matter)
  2. [走进 Fireworks 多区域部署：一套部署，全球扩展](https://fireworks.ai/blog/multi-region-deployment)
  3. [Every byte counts: ARCv3 and the case for cross-region RL](https://fireworks.ai/blog/arcv3-and-the-case-for-cross-region-rl)
  4. [Ember-1 简介](https://fireworks.ai/blog/ember-1)
  5. [推出专业智能指数](https://fireworks.ai/blog/introducing-the-specialized-intelligence-index)
  - 📄 完整文章归档（共 24 篇）：[fireworks_ai.md](llm-news/fireworks_ai.md)

### Together AI (together_ai)
- 📡 [RSS/Atom 订阅源](https://www.together.ai/blog/rss.xml)：`https://www.together.ai/blog/rss.xml`
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [如何用 17 美元训练你自己的 Jev](https://www.together.ai/blog/how-to-train-your-own-jev)（2026-09-23）
  2. [金丝雀部署：无需停机即可升级生产中的模型](https://www.together.ai/blog/canary-rollouts-upgrade-models-in-production-without-downtime)（2026-09-22）
  3. [一家全球金融科技公司如何用专用模型推理扩展编码智能体流量](https://www.together.ai/blog/global-fintech-scales-coding-agent-traffic-with-dedicated-model-inference)（2026-09-18）
  4. [与 Together 一起从闭源模型迁移到开源模型](https://www.together.ai/blog/migrating-from-closed-to-open-source-models)（2026-09-16）
  5. [Together AI 通过更多模型、实时指标和更精细的控制来扩展微调服务](https://www.together.ai/blog/together-ai-expands-fine-tuning-service-with-more-models-live-metrics-and-finer-controls)（2026-09-11）
  - 📄 完整文章归档（共 81 篇）：[together_ai.md](llm-news/together_ai.md)

### DeepInfra (deepinfra)
- 页面：[官方博客](https://deepinfra.com/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-deepinfra.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-deepinfra.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [GLM-5.3 提供商定价指南：成本比较](https://deepinfra.com/blog/glm-5-3-provider-pricing-guide)（2026-10-03）
  2. [GLM-5.3 现已在 DeepInfra 上提供](https://deepinfra.com/blog/glm-5-3-deepinfra)（2026-10-03）
  3. [GLM-5.3 API 提供商：速度、延迟和成本](https://deepinfra.com/blog/glm-5-3-api-provider-benchmarks)（2026-10-02）
  4. [Best DeepSeek-V4.1-Flash API Providers in 2026](https://deepinfra.com/blog/best-deepseek-v4-1-flash-api-providers)（2026-10-02）
  5. [DeepSeek-V4.1-Flash: Model Overview & Integration](https://deepinfra.com/blog/deepseek-v4-1-flash-model-overview-integration)（2026-10-01）
  - 📄 完整文章归档（共 22 篇）：[deepinfra.md](llm-news/deepinfra.md)

### 美团 LongCat (longcat_meituan)
- 页面：[更新日志](https://longcat.chat/platform/docs/zh/ChangeLog.html)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-longcat_meituan.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-longcat_meituan.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [LongCat-2.5-Preview 上线](https://longcat.chat/platform/docs/zh/ChangeLog.html#%E7%89%88%E6%9C%AC-2026-09-25)（2026-09-25）
  2. [全新推出企业服务](https://longcat.chat/platform/docs/zh/ChangeLog.html#%E7%89%88%E6%9C%AC-2026-09-10)（2026-09-10）
  3. [全新推出企业服务](https://longcat.chat/platform/docs/zh/ChangeLog.html#%E7%89%88%E6%9C%AC-2026-09-02)（2026-09-02）
  4. [LongCat-2.0 发布 & 全新推出计费服务](https://longcat.chat/platform/docs/zh/ChangeLog.html#%E7%89%88%E6%9C%AC-2026-06-30)（2026-06-30）
  5. [LongCat 部分模型服务下线](https://longcat.chat/platform/docs/zh/ChangeLog.html#%E7%89%88%E6%9C%AC-2026-05-29)（2026-05-29）
  - 📄 完整文章归档（共 14 篇）：[longcat_meituan.md](llm-news/longcat_meituan.md)

### StreamLake (streamlake)
- 页面：[更新日志](https://www.streamlake.com/document/WANQING/mdptalisb06i7ai3zdd)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-streamlake.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-streamlake.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
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
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [数眼智能完成数千万元天使轮融资，加速企业级大模型部署能力建设](https://www.shuyanai.com/blogs#d-2026-09-21-4)（2026-09-21）
  2. [数眼智能AI漫剧教程：从脚本、AI生图到Seedance 2.5生视频](https://www.shuyanai.com/blogs#d-2026-09-17-5)（2026-09-17）
  3. [数眼智能 AI 视频生成教程：如何用智能体生成第一条视频？](https://www.shuyanai.com/blogs#d-2026-09-16-6)（2026-09-16）
  4. [数眼智能在海南数据谷OPC社区揭牌现场｜把 Token 级算力，送到每一个 AI 超级个体手里](https://www.shuyanai.com/blogs#d-2026-09-16-7)（2026-09-16）
  5. [数眼智能与海南大学达成专利技术合作](https://www.shuyanai.com/blogs#d-2026-09-15-9)（2026-09-15）
  - 📄 完整文章归档（共 16 篇）：[dataeye.md](llm-news/dataeye.md)

### AI21 Labs (ai21_labs)
- 页面：[官方博客](https://www.ai21.com/blog)
  - 🔌 官方未提供 RSS/Atom 订阅源，条目取自官方数据接口
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-ai21_labs.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-ai21_labs.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [From manual negotiation to automated scheduling: How AI21 manages its GPU fleet with Kueue](https://www.ai21.com/blog/how-ai21-manages-its-gpu-fleet-with-kueue/)（2026-10-04）
  2. [你要的不是前沿模型，而是一个验证器](https://www.ai21.com/blog/you-need-a-verifier/)（2026-08-19）
  3. [又好又省：开放模型探路，前沿模型收尾](https://www.ai21.com/blog/better-and-cheaper-together-open-models-explore-frontier-models-patch/)（2026-07-15）
  4. [面向 SWE 智能体的预算感知执行，把 Best-of-N 做得更好](https://www.ai21.com/blog/improving-best-of-n-with-budget-aware-execution-for-swe-agents/)（2026-07-07）
  5. [token 开销降不下来？光靠简单路由管不住它](https://www.ai21.com/lp/blog/token-spend-isnt-going-down-you-need-more-than-naive-routing-to-manage-it-gated/)（2026-06-30）
  - 📄 完整文章归档（共 67 篇）：[ai21_labs.md](llm-news/ai21_labs.md)

### Jina AI (jina_ai)
- 页面：[官方博客](https://jina.ai/news/)
  - 📡 RSS/Atom：https://jina.ai/feed.rss
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [jina-embeddings-v5-omni: Embeddings for Text, Image, Audio and VideoOne model, four modalities: text, image, audio, video. Best-in-class omni embeddings in 1.6B and 0.9B.](https://jina.ai/news/jina-embeddings-v5-omni-multimodal-embeddings-for-text-image-audio-and-video)（2026-05-12）
  2. [7 minutes readBootstrapping Audio Embeddings from Multimodal LLMsTurn any multimodal LLM into a small audio embedding model that beats CLAP with 25x less data.](https://jina.ai/news/bootstrapping-audio-embeddings-from-multimodal-llms)（2026-03-11）
  3. [从原始数值识别嵌入模型：读原始数字即可为嵌入模型留指纹的微型 transformer，无需特征工程](https://jina.ai/news/identifying-embedding-models-from-raw-numerical-values)（2026-03-06）
  4. [7 minutes readJina-VLM: Small Multilingual Vision Language ModelNew 2B vision language model achieves SOTA on multilingual VQA, no catastrophic forgetting on text-only tasks.](https://jina.ai/news/jina-vlm-small-multilingual-vision-language-model)（2025-12-04）
  5. [Llama.cpp 与 GGUF 中的多模态嵌入：落地途中发现的几个意外问题](https://jina.ai/news/multimodal-embeddings-in-llama-cpp-and-gguf)（2025-09-09）
  - 📄 完整文章归档（共 6 篇）：[jina_ai.md](llm-news/jina_ai.md)

### Poolside (poolside)
- 页面：[官方博客](https://poolside.ai/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-poolside.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-poolside.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [Poolside on Dell：在自身边界内落地前沿 AI 的高效路径](https://poolside.ai/blog#d-2026-07-28-35)（2026-07-28）
  2. [Laguna XS 2.1 简介](https://poolside.ai/blog#d-2026-07-21-19)（2026-07-21）
  3. [长上下文更新：Laguna XS.2 和 M.1](https://poolside.ai/blog#d-2026-07-02-21)（2026-07-02）
  4. [按你的方式使用 AI：Poolside 平台介绍](https://poolside.ai/blog#d-2026-05-26-23)（2026-05-26）
  5. [Laguna XS.2 和 M.1：深入探讨](https://poolside.ai/blog#d-2026-05-11-1)（2026-05-11）
  - 📄 完整文章归档（共 19 篇）：[poolside.md](llm-news/poolside.md)

### Modular (原 BentoCloud/BentoML) (modular_cloud)
- 📡 [RSS/Atom 订阅源](https://www.modular.com/blog/rss.xml)：`https://www.modular.com/blog/rss.xml`
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [Modular：Modular 26.6：开放编译器贡献、音频生成和扩展模型支持](https://www.modular.com/blog/modular-26-6-open-compiler-contributions-audio-generation-and-expanded-model-support)（2026-09-17）
  2. [Modular：Mojo 现已开源！](https://www.modular.com/blog/mojo-open-source)（2026-08-18）
  3. [Modular：Modular 和高通：相同的代码，新的芯片](https://www.modular.com/blog/modcon-qualcomm)（2026-08-18）
  4. [Modular：ModCon 2026：开源、开放云、开放芯片](https://www.modular.com/blog/modcon-announcements)（2026-08-18）
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
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [2026-09-22 MiMo-V2.6 系列发布](https://mimo.mi.com/docs/zh-CN/updates/model#2026-09-22-mimo-v26-%E7%B3%BB%E5%88%97%E5%8F%91%E5%B8%83)（2026-09-22）
  2. [2026-9-22 批量推理（Batch API）功能上线](https://mimo.mi.com/docs/zh-CN/updates/feature/platform#2026-9-22--%E6%89%B9%E9%87%8F%E6%8E%A8%E7%90%86batch-api%E5%8A%9F%E8%83%BD%E4%B8%8A%E7%BA%BF)（2026-09-22）
  3. [2026-9-15 新增站内信功能](https://mimo.mi.com/docs/zh-CN/updates/feature/platform#2026-9-15--%E6%96%B0%E5%A2%9E%E7%AB%99%E5%86%85%E4%BF%A1%E5%8A%9F%E8%83%BD)（2026-09-15）
  4. [2026-6-23 支持 OpenAI Responses API](https://mimo.mi.com/docs/zh-CN/updates/feature/platform#2026-6-23-%E6%94%AF%E6%8C%81-openai-responses-api)（2026-06-23）
  5. [2026-6-11 邀请有礼活动升级](https://mimo.mi.com/docs/zh-CN/updates/feature/platform#2026-6-11-%E9%82%80%E8%AF%B7%E6%9C%89%E7%A4%BC%E6%B4%BB%E5%8A%A8%E5%8D%87%E7%BA%A7)（2026-06-11）
  - 📄 完整文章归档（共 38 篇）：[xiaomi_mimo.md](llm-news/xiaomi_mimo.md)

### Anyscale (anyscale)
- 📡 [RSS/Atom 订阅源](https://www.anyscale.com/rss.xml)：`https://www.anyscale.com/rss.xml`
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [Ray Summit 2026：物理 AI、RL 与支撑这一切的基础设施](https://anyscale.com/blog/ray-summit-2026-recap)（2026-09-08）
  2. [推出 Ray History Server：Kubernetes 上 Ray 的事后可观测性](https://anyscale.com/blog/ray-history-server)（2026-08-25）
  3. [Scaling Ray for AI workloads to 10k node clusters](https://anyscale.com/blog/how-we-scaled-ray-from-batch-inference-to-10000-node-training-clusters)（2026-08-25）
  4. [优化 LLM 服务效率：用 Ray Serve LLM 从 KV 缓存复用走向 token 负载感知](https://anyscale.com/blog/llm-kv-token-aware-routing)（2026-08-25）
  5. [学习循环：把智能掌握在自己手中](https://anyscale.com/blog/learning-loops)（2026-08-25）
  - 📄 完整文章归档（共 66 篇）：[anyscale.md](llm-news/anyscale.md)

### InceptionLabs (inception_labs)
- 页面：[官方博客](https://www.inceptionlabs.ai/blog)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-inception_labs.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-inception_labs.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [Mercury Voice 发布](https://www.inceptionlabs.ai/blog/introducing-mercury-voice)（2026-10-01）
  2. [Mercury 2.5 简介](https://www.inceptionlabs.ai/blog/introducing-mercury-2-5)（2026-09-24）
  3. [Mercury 2 for Search：快到每次查询能跑上一百次](https://www.inceptionlabs.ai/blog/mercury-2-for-search)
  4. [更多构建者。更高吞吐量。更好的 Mercury 2](https://www.inceptionlabs.ai/blog/mercury-2-10x-free-tokens)
  5. [Mercury 2：首个快到能接起电话的推理模型](https://www.inceptionlabs.ai/blog/mercury-2-the-first-reasoning-model-fast-enough-to-pick-up-the-phone)
  - 📄 完整文章归档（共 13 篇）：[inception_labs.md](llm-news/inception_labs.md)

### Inference.net (inference_net)
- 页面：[官方博客](https://inference.net/blog/)
  - ⚠️ 页面 HTML 中未发现 RSS/Atom 链接，已尝试直接从页面提取文章条目
- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）：[`llm-news-inference_net.xml`](https://free-llm-intel.aishort.top/feeds/llm-news-inference_net.xml)
- 📰 **最新文章**（官方源抓取于 2026-10-05，标题自动汉化）：
  1. [Schematron V2: Frontier HTML-to-JSON extraction at a fraction of the cost](https://inference.net/blog/#d-2026-08-05-0)（2026-08-05）
  2. [Inference 平台简介：监控、训练并部署自我改进的 AI 模型](https://inference.net/blog/#d-2026-04-16-1)（2026-04-16）
  3. [How Inference.net trains Specialized Language Models that cut AI costs by up to 50x](https://inference.net/blog/#d-2026-04-14-2)（2026-04-14）
  4. [专业 LLM：您需要的模型尚不存在](https://inference.net/blog/#d-2026-03-11-3)（2026-03-11）
  5. [OSSAS 项目：定制 LLM 可处理 1 亿篇研究论文](https://inference.net/blog/#d-2026-02-05-4)（2026-02-05）
  - 📄 完整文章归档（共 9 篇）：[inference_net.md](llm-news/inference_net.md)

---
共整理 35 个厂商的动态入口（其中 35 个成功提取最新文章），RSS/Atom 源 15 个。

<!-- LLM-NEWS:END -->
