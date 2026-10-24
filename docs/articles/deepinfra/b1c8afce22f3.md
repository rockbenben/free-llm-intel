---
vendor: deepinfra
title: Wan 3.0 API 基准：速度、延迟与成本
original_title: Wan 3.0 API Benchmarks: Speed, Latency & Cost
url: https://deepinfra.com/blog/wan-3-0-api-benchmarks
date: 2026-10-21
lang: zh
captured: 2026-10-24
extractor: readability-v1
translator: agent
status: translated
body_sha: 45b8cdba5f7b
---

# Wan 3.0 API 基准：速度、延迟与成本

发布于 2026.10.21，作者 DeepInfra

![Wan 3.0 API 基准：速度、延迟与成本](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/10/api.png)

## **关键要点**

- Wan 3.0 在有声版的 Artificial Analysis text-to-video 排行榜上以 1,173 Elo 居首，因此供应商选择归结为价格、输入支持和可靠性。
- 每秒价格差异很大。Alibaba Cloud 和 fal 在 480P、720P 和 1080P 下标价 $0.05、$0.10 和 $0.20，OpenRouter 标出的费率则从 $0.0425 起。
- DeepInfra 只标一个费率：每秒 $0.20；它通过一个 API 服务从 Wan2.2 到 Wan3.0 的整个 Wan 家族，并执行零保留政策。
- OpenRouter 公布 Wan 3.0 的实测延迟与可用性，这让运营风险更容易被计入价格。

Wan 是阿里巴巴的视频生成模型家族。较早的 [Wan2.2](https://deepinfra.com/Wan-AI/Wan2.2-T2V-A14B) 模型以 Apache 2.0 下的开放权重形式发布，而较新的版本如 [Wan2.6](https://deepinfra.com/Wan-AI/Wan2.6-T2V)、[Wan2.7](https://deepinfra.com/Wan-AI/Wan2.7-R2V) 和 [Wan3.0](https://deepinfra.com/Wan-AI/Wan3.0-Video) 则通过托管 API 交付。

Wan 3.0 是首个接受文档和网页作为输入的 Wan 模型。它还把最大片段时长翻倍到 30 秒。

| **模型** | **关键能力** | **访问方式** |
| --- | --- | --- |
| Wan 3.0 | 片段最长 30 秒，480P 至 1080P，原生音频，支持文档与网页输入 | 托管 API |
| Wan 2.7 | 片段最长 15 秒，image-to-video、reference-to-video、视频编辑 | 托管 API |
| Wan 2.6 | 多镜头叙事，主体一致，片段最长 15 秒 | 托管 API |
| Wan 2.2 | 开放权重的 text-to-video 与 image-to-video 模型 | 开放权重（Apache 2.0） |

在有声版的 Artificial Analysis text-to-video 排行榜上，Wan 3.0 以 1,173 Elo 排名第一。Utopai X 以 1,166 紧随其后，接着是 Dreamina Seedance 2.5 的 1,159 和 MiniMax H3 的 1,158。Wan 3.0 的 95% 区间为 1,157 至 1,189，因此头部模型之间的差距很小。

## **供应商对比表**

该表列出 Wan 3.0 标准档。价格按每生成一秒视频计。

| **供应商** | **480P** | **720P** | **1080P** | **备注** |
| --- | --- | --- | --- | --- |
| DeepInfra | $0.20 | $0.20 | $0.20 | 单一标价 |
| Alibaba Cloud（新加坡） | $0.05 | $0.10 | $0.20 | 美国与欧洲区域标价为 $0.041256、$0.082513 和 $0.165025 |
| OpenRouter | $0.0425 | $0.085 | $0.17 | 含 15% 折扣，端点背后只有一家供应商 |
| fal | $0.05 | $0.10 | $0.20 | 另提供 Prime 档 |
| Atlas Cloud | $0.04 | 未标价 | $0.16 | 含页面上显示的 20% 折扣 |

## **供应商是如何对比的**

- **每秒价格：** 各分辨率档位的标价，因为视频模型按生成时长计费。
- **输入支持：** 端点是否接受参考图像、视频、音频、文档和网页。
- **运营数据：** 供应商公布延迟与可用性的，就纳入比较。
- **数据处理：** 保留政策与合规认证。
- **质量：** Artificial Analysis 对 Wan 3.0 作为模型给出评分，从而把比较焦点留在这四个因素上。

## **Wan 模型的首选 API 供应商**

### **DeepInfra**

DeepInfra 通过一个 API 服务从 Wan2.2 到 Wan3.0 的整个 Wan 家族，因此团队可以在不同代之间切换而不必换供应商。[Wan3.0-Video](https://deepinfra.com/Wan-AI/Wan3.0-Video) 按每秒输出 $0.20 计费。

在 DeepInfra 上可用的 Wan 模型有：

| **模型** | **价格** | **能力** |
| --- | --- | --- |
| Wan3.0-Video | 每秒 $0.20 | 片段最长 30 秒，omni-modal 参考，音频 |
| [Wan2.7-R2V](https://deepinfra.com/Wan-AI/Wan2.7-R2V) | 每秒 $0.10 | reference-to-video，能保持人物或物体的外观与声音 |
| [Wan2.6-T2V](https://deepinfra.com/Wan-AI/Wan2.6-T2V) | 每秒 $0.10 | 支持多镜头叙事的 text-to-video，最长 15 秒 |
| [Wan2.2-T2V-A14B](https://deepinfra.com/Wan-AI/Wan2.2-T2V-A14B) | 每秒 $0.075 | 480p 的开放权重 text-to-video 模型 |

DeepInfra 还以每秒 $0.10 标出 Wan2.7-I2V 和 Wan2.6-I2V。Artificial Analysis 在其生成时间跟踪中纳入了 DeepInfra 上的 Wan 2.2 A14B 端点。

数据处理是它的一项优势。DeepInfra 对输入、输出和用户数据执行[零保留政策](https://deepinfra.com/blog/data-sovereignty-ai-open-weight-adoption)，平台通过了 SOC 2 和 ISO 27001 认证。

代价在于低分辨率下的价格。单一的 $0.20 费率与 Alibaba Cloud 的 1080P 价格持平，但高于别处的 480P 和 720P 价格。

结论：DeepInfra 适合以 1080P 渲染最终片段、希望在多个 Wan 代际上统一用一个 API、并且需要明确数据处理条款的团队。

### **Alibaba Cloud**

Alibaba Cloud 通过 Model Studio 提供直接访问，具备完整的 Wan 3.0 功能集和区域化定价。新加坡区域标价为每秒 $0.05、$0.10 和 $0.20。美国、德国、日本和中国的区域标价为 $0.041256、$0.082513 和 $0.165025。

- 在所有已标价的区域，速率限制为每分钟 300 次请求
- 新加坡提供每秒 $0.068、$0.14 和 $0.28 的 Prime 档，面向更快的生成
- 第一方 API 支持编辑、延长和参考引导式生成
- 不支持批量推理或微调

Alibaba 指出音频质感与画面文字渲染仍在成熟中。结论：Alibaba Cloud 适合需要第一方访问和区域化定价选项的企业团队。

### **OpenRouter**

OpenRouter 以 alibaba/wan-3.0 的名称列出 Wan 3.0，发布日期为 2026 年 8 月 24 日。它只路由到一家供应商 Alibaba Cloud，并显示 480P 下每秒 $0.0425 起的费率（已应用 15% 折扣）。

OpenRouter 公布该端点的运营数据。撰稿时，最佳供应商显示端到端延迟中位数约 149 秒，三天内可用性接近 85%。这些数字会变动，请查看实时页面。

结论：OpenRouter 适合对成本敏感、希望只有一个计费关系并看到可靠性数据的团队。

### **fal**

fal 通过 alibaba/wan-3.0 端点提供 Wan 3.0，标价为 480p、720p 和 1080p 下每秒 $0.05、$0.10 和 $0.20。Prime 变体标价为 $0.068、$0.14 和 $0.28。

- 时长从 2 到 30 秒，传 null 表示由系统智能决定时长
- 宽高比支持 adaptive、16:9、4:3、1:1、3:4 和 9:16
- 发布为 @fal-ai/client 的 JavaScript 客户端
- 默认开启的安全检查器

据 fal 称，关闭 prompt expansion 可节省大约 20 至 60 秒延迟。结论：fal 适合需要带类型定义的客户端和基于队列的请求的 web 团队。

### **Atlas Cloud**

Atlas Cloud 将 Wan 3.0 标为每秒 $0.05，折后 20% 显示为 $0.04。Prime 档标价 $0.068，折后 10% 显示为 $0.061。页面上列出 SOC 2 Type II 认证和 HIPAA 合规。

reference-to-video 最多接受 20 个混合参考：10 张图像、5 段视频和 5 段音频。结论：Atlas Cloud 适合有合规要求、同时也想要低每秒费率的团队。

## **为什么 DeepInfra 适合生产环境的 Wan 工作负载**

每秒价格只是其中一项输入。生产团队还会权衡数据处理、供应商数量，以及日后接入其他模型的难易程度。

- 一个 API 覆盖从 Wan2.2 到 Wan3.0 的每一代 Wan，外加其他视频模型，例如每秒 $0.15 的 Google Veo 3.1 Fast。
- 零保留以及 SOC 2 和 ISO 27001 认证可覆盖受监管的审核流程。
- 单一标价让固定分辨率管线的预算编制变得简单。

下表展示各分辨率下一条 10 秒片段的成本。DeepInfra 的单一费率使它适合 1080P 工作。

| **供应商** | **480P** | **720P** | **1080P** |
| --- | --- | --- | --- |
| DeepInfra | $2.00 | $2.00 | $2.00 |
| Alibaba Cloud（新加坡） | $0.50 | $1.00 | $2.00 |
| OpenRouter | $0.425 | $0.85 | $1.70 |
| fal | $0.50 | $1.00 | $2.00 |

同时还在跑其他实验室视频模型的团队，可以通过同一个 API 接入 [Google Veo 3.1 Fast](https://deepinfra.com/google/veo-3.1-fast)。

## **常见问题**

### **Wan 3.0 用哪家供应商最便宜？**

取决于分辨率。在 480P，Atlas Cloud 折后显示 $0.04，Alibaba 美国区域标价 $0.041256，OpenRouter 标价 $0.0425。在 1080P，Atlas Cloud 显示 $0.16，OpenRouter 标价 $0.17。

### **通过 API 生成一条 Wan 3.0 视频要多少钱？**

一条 5 秒 720P 片段在 OpenRouter 上约 $0.425，在 Alibaba Cloud 新加坡区域和 fal 上为 $0.50，在 DeepInfra 上为 $1.00。一条 5 秒 1080P 片段在 DeepInfra、Alibaba Cloud 和 fal 上都是 $1.00。

### **Wan 2.x 与 Wan 3.0 有什么区别？**

Wan 3.0 把单次生成长度延长到 30 秒，而 Wan 2.7 是 15 秒。它新增了文档和网页输入，沿用了 Wan 2.7 的编辑功能，并以托管服务的形式交付。

### **Wan 3.0 是开源的吗？**

阿里巴巴通过托管 API 提供 Wan 3.0。Wan2.2 的权重以 Apache 2.0 许可证发布在 Hugging Face 上。

### **我可以在本地运行 Wan 吗？**

可以，用 Wan2.2。Wan2.2 T2V A14B 和 TI2V 5B 的权重以 Apache 2.0 发布在 Hugging Face 上。如果你更想用 API，DeepInfra 也托管 A14B 模型。

## **结论**

选择 Wan API 供应商，意味着要比较你工作分辨率下的价格、你需要的输入，以及供应商公布了多少运营数据。质量由模型本身决定，因此决策落在这些实际因素上。

- 需要在多个 Wan 代际上统一一个 API、以 1080P 出最终成品、并要零保留的数据处理，选 DeepInfra。
- 需要第一方访问、区域化定价和 Prime 档，选 Alibaba Cloud。
- 需要低 1080P 费率和公开的可靠性数字，选 OpenRouter。
- 需要带类型定义的客户端或合规资质清单，选 fal 或 Atlas Cloud。

语言模型的类似对比涵盖 [GLM-5.3 API 供应商](https://deepinfra.com/blog/best-glm-5-3-api-providers)。

相关文章

[![MCP 服务器详解：面向开发者的实用指南](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/09/MCP-servers.png)](https://deepinfra.com/blog/mcp-servers-explained)[MCP 服务器详解：面向开发者的实用指南](https://deepinfra.com/blog/mcp-servers-explained)<p>让一个 AI 应用访问数据库、API、文件系统或内部服务，听起来很简单，直到你要维护这套集成。你需要定义模型能访问什么、描述各项操作、安全地执行请求、返回结构化结果，还要处理认证。当另一个 AI [&hellip;]</p>

[![Kimi K3 vs Claude Opus 4.8 vs GPT-5.6 Sol：实用 AI 模型对比](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/07/kimi-closed-source.png)](https://deepinfra.com/blog/kimi-k3-vs-claude-opus-4-8-vs-gpt-5-6-sol)[Kimi K3 vs Claude Opus 4.8 vs GPT-5.6 Sol：实用 AI 模型对比](https://deepinfra.com/blog/kimi-k3-vs-claude-opus-4-8-vs-gpt-5-6-sol)<p>这篇对比首次发布后有哪些变化 这里比较的三个模型中有两个已经被后继版本取代，GPT-5.6 Sol 的定价也发生了实质变化。目前 DeepInfra 上可用的三个最强模型，并不能按能力档次干净地分开。Kimi K3（可通过 DeepInfra 使用）、Claude Opus 4.8 和 GPT-5.6 Sol 的得分都在 [&hellip;]</p>

[![最佳 Qwen3.8-27B 推理供应商（2026）](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/10/qwen3.8-27b-best-providers.png)](https://deepinfra.com/blog/best-qwen3-8-27b-inference-providers)[最佳 Qwen3.8-27B 推理供应商（2026）](https://deepinfra.com/blog/best-qwen3-8-27b-inference-providers)<p>Qwen3.8-27B 改变了开放权重模型的格局。它在参数量与推理能力之间取得了出色平衡：一个 270 亿参数的模型，能力极强却又足够紧凑。它能在单张 24GB 显卡上以 4-bit 量化运行，或在单张 80GB 显卡上以全精度运行。要找到合适的基础设施来托管、扩展或 [&hellip;]</p>

[查看全部](https://deepinfra.com/blog)
