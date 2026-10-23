---
vendor: deepinfra
title: Wan 3.0 API Benchmarks: Speed, Latency & Cost
original_title: 
url: https://deepinfra.com/blog/wan-3-0-api-benchmarks
date: 2026-10-21
lang: zh
captured: 2026-10-23
extractor: readability-v1
translator: mt
status: translated
body_sha: c45f1661a864
---

# Wan 3.0 API 基准：速度、延迟和成本

DeepInfra 发布于 2026.10.21

![Wan 3.0 API 基准：速度、延迟和成本](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/10/api.png)

## **要点**

- Wan 3.0 以 1,173 Elo 的音频领先人工分析文本到视频排行榜，因此提供商的选择取决于价格、输入支持和可靠性。
- 每秒价格差异很大。阿里云和 fal 列出了 480P、720P 和 1080P 的 0.05 美元、0.10 美元和 0.20 美元，OpenRouter 列出了 0.0425 美元起的费率。
- DeepInfra 列出了每秒 0.20 美元的费率，通过一个 API 为从 Wan2.2 到 Wan3.0 的整个 Wan 系列提供服务，并应用零保留政策。
- OpenRouter 发布了 Wan 3.0 的测量延迟和可用性，这使得操作风险更容易定价。

万是阿里巴巴的视频生成模型家族。早期的 [Wan2.2](https://deepinfra.com/Wan-AI/Wan2.2-T2V-A14B) 模型在 Apache 2.0 下作为开放权重发布，而后来的版本，例如 [Wan2.6](https://deepinfra.com/Wan-AI/Wan2.6-T2V)， [Wan2.7](https://deepinfra.com/Wan-AI/Wan2.7-R2V)和[Wan3.0](https://deepinfra.com/Wan-AI/Wan3.0-Video)通过托管API交付。

Wan 3.0是第一个接受文档和网页作为输入的Wan模型。它还将最大剪辑长度加倍至 30 秒。

| **型号** | **关键能力** | **访问** |
| --- | --- | --- |
|万3.0 |剪辑长达 30 秒，480P 至 1080P，原生音频、文档和网页输入 |托管 API |
|万2.7 |剪辑长达 15 秒、图像转视频、参考视频、视频编辑 |托管 API |
|万2.6 |多镜头讲故事，主题一致，剪辑长达 15 秒 |托管 API |
|万2.2 |开放式文本到视频和图像到视频模型 |开放式重量（Apache 2.0）|

在人工分析文本转视频音频排行榜上，Wan 3.0 以 1,173 Elo 排名第一。 Utopai X 紧随其后，得分为 1,166，然后是 Dreamina Seedance 2.5，得分为 1,159，MiniMax H3 得分为 1,158。 Wan 3.0 的 95% 区间从 1,157 到 1,189，因此顶级模型坐在一起。

## **提供商比较表**

下表列出了标准 Wan 3.0 层。价格是每秒生成的视频。

| **提供商** | **480P** | **720P** | **1080P** | **注释** |
| --- | --- | --- | --- | --- |
|深基础设施 | 0.20 美元 | 0.20 美元 | 0.20 美元 |单挂率|
|阿里云（新加坡）| 0.05 美元 | 0.10 美元 | 0.20 美元 |美国和欧洲地区列出 0.041256 美元、0.082513 美元和 0.165025 美元 |
|开放路由器 | 0.0425 美元 | 0.085 美元 | 0.17 美元 |包括 15% 的折扣，端点背后有一个提供商 |
|福尔| 0.05 美元 | 0.10 美元 | 0.20 美元 |还提供 Prime 级别 |
|阿特拉斯云 | 0.04 美元 |未列出 | 0.16 美元 |包括页面上显示的 20% 折扣 |

## **如何比较提供商**

- **每秒价格：** 每个分辨率层列出的速率，因为视频模型按生成的持续时间计费。
- **输入支持：** 终端是否接受参考图像、视频、音频、文档和网页。
- **操作数据：** 提供商发布的延迟和可用性。
- **数据处理：** 保留政策和合规性认证。
- **质量：** 人工分析以Wan 3.0为模型进行评分，重点关注上述四个因素。

## **Wan 模型的顶级 API 提供商**

### **深度基础设施**

DeepInfra 通过一个 API 为 Wan2.2 到 Wan3.0 的 Wan 系列提供服务，因此团队可以在不同代之间移动，而无需更换供应商。 [Wan3.0-Video](https://deepinfra.com/Wan-AI/Wan3.0-Video) 按每秒输出 0.20 美元计费。

DeepInfra 上可用的 Wan 模型有：

| **型号** | **价格** | **能力** |
| --- | --- | --- |
| Wan3.0-视频|每秒 0.20 美元 |剪辑长达 30 秒、全模式参考、音频 |
| [Wan2.7-R2V](https://deepinfra.com/Wan-AI/Wan2.7-R2V) |每秒 0.10 美元 |参考保留人或物体的外观和声音的视频 |
| [Wan2.6-T2V](https://deepinfra.com/Wan-AI/Wan2.6-T2V) |每秒 0.10 美元 |文本转视频，多镜头叙事，最长 15 秒 |
| [Wan2.2-T2V-A14B](https://deepinfra.com/Wan-AI/Wan2.2-T2V-A14B) |每秒 0.075 美元 | 480p 的开放式文本转视频模型 |

DeepInfra 还以每秒 0.10 美元的价格列出了 Wan2.7-I2V 和 Wan2.6-I2V。 Artificial Analysis 在其生成时间跟踪中包括 DeepInfra 上的 Wan 2.2 A14B 端点。

数据处理是强项。 DeepInfra 对输入、输出和用户数据运行[零保留政策](https://deepinfra.com/blog/data-sovereignty-ai-open-weight-adoption)，并且该平台经过 SOC 2 和 ISO 27001 认证。

代价是低分辨率下的价格。单次 0.20 美元的费率与阿里云的 1080P 价格相当，但高于其他地方的 480P 和 720P 费率。

结论：DeepInfra 适合以 1080P 渲染最终剪辑、需要跨多个 Wan 代的 API 并需要明确的数据处理条款的团队。

### **阿里云**

阿里云通过 Model Studio 提供直接访问，具有完整的 Wan 3.0 功能集和区域定价。新加坡地区每秒列出 0.05 美元、0.10 美元和 0.20 美元。美国、德国、日本和中国的地区售价为 0.041256 美元、0.082513 美元和 0.165025 美元。

- 每个列出的区域的速率限制为每分钟 300 个请求
- 在新加坡，Prime 级别的价格为每秒 0.068 美元、0.14 美元和 0.28 美元，旨在加快生成速度
- 从第一方 API 进行编辑、扩展和参考指导生成
- 不支持批量推理或微调

阿里巴巴指出，音频纹理和屏幕文本渲染仍处于成熟阶段。结论：阿里云适合需要第一方访问和区域定价选项的企业团队。

### **开放路由器**

OpenRouter 在 alibaba/wan-3.0 下列出了 Wan 3.0，发布日期为 2026 年 8 月 24 日。它路由到单一提供商阿里云，并显示 480P 每秒 0.0425 美元起的费率，并应用 15% 的折扣。

OpenRouter 发布端点的操作数据。截至撰写本文时，最佳提供商的端到端延迟中值约为 149 秒，三天内可用性接近 85%。这些数字会移动，因此请检查实时页面。

结论：OpenRouter 适合需要一种计费关系和可见可靠性数据的成本敏感型团队。

### **失败**

fal 通过 alibaba/wan-3.0 端点为 Wan 3.0 提供服务，并以 480p、720p 和 1080p 每秒列出 0.05 美元、0.10 美元和 0.20 美元。 Prime 版本售价为 0.068 美元、0.14 美元和 0.28 美元。

- 持续时间从 2 到 30 秒，智能持续时间为空值
- 自适应宽高比、16:9、4:3、1:1、3:4 和 9:16
- 一个 JavaScript 客户端发布为 @fal-ai/client
- 默认情况下打开的安全检查器

据 fal 称，关闭即时扩展可以节省大约 20 到 60 秒的延迟。结论：fal 适合需要类型化客户端和基于队列的请求的 Web 团队。

### **阿特拉斯云**

Atlas Cloud 以每秒 0.05 美元的价格列出 Wan 3.0，20% 折扣后显示为 0.04 美元。 Prime 级别的价格为 0.068 美元，10% 折扣后显示为 0.061 美元。该页面列出了 SOC 2 Type II 认证和 HIPAA 一致性。

视频参考最多可接受 20 个混合参考：10 个图像、5 个视频和 5 个音频剪辑。结论：Atlas Cloud 适合具有合规性要求且希望每秒速率较低的团队。

## **为什么 DeepInfra 适合生产广域网工作负载**

每秒价格只是一个输入。生产团队还会权衡数据处理、供应商数量以及以后添加其他模型的容易程度。

- 一个 API 涵盖从 Wan2.2 到 Wan3.0 的每一代 Wan，以及其他视频模型，例如 Google Veo 3.1 Fast（每秒 0.15 美元）。
- 零保留以及 SOC 2 和 ISO 27001 认证涵盖受监管的审查流程。
- 单一列出的费率使固定分辨率管道的预算变得简单。

该表显示了每个分辨率下 10 秒剪辑的成本。 DeepInfra 的单一速率使其适合 1080P 工作。

| **提供商** | **480P** | **720P** | **1080P** |
| --- | --- | --- | --- |
|深基础设施 | 2.00 美元 | 2.00 美元 | 2.00 美元 |
|阿里云（新加坡）| 0.50 美元 | 1.00 美元 | 2.00 美元 |
|开放路由器 | 0.425 美元 | 0.85 美元 | 1.70 美元 |
|福尔| 0.50 美元 | 1.00 美元 | 2.00 美元 |

还运行其他实验室视频模型的团队可以通过相同的 API 添加 [Google Veo 3.1 Fast](https://deepinfra.com/google/veo-3.1-fast)。

## **常见问题**

### **哪家提供商的 Wan 3.0 最便宜？**

这取决于分辨率。 480P 下，Atlas Cloud 折扣后显示为 0.04 美元，阿里巴巴美国地区显示为 0.041256 美元，OpenRouter 显示为 0.0425 美元。在 1080P 下，Atlas Cloud 显示为 0.16 美元，OpenRouter 列出为 0.17 美元。

### **通过 API 播放一个 Wan 3.0 视频需要多少钱？**

一个 5 秒的 720P 片段在 OpenRouter 上的价格约为 0.425 美元，在阿里云的新加坡区域和 fal 上为 0.50 美元，在 DeepInfra 上为 1.00 美元。一个 5 秒的 1080P 剪辑在 DeepInfra、阿里云和 fal 上的价格为 1.00 美元。

### **Wan 2.x 和 Wan 3.0 有什么区别？**

Wan 3.0 将单代时间从 Wan 2.7 中的 15 秒延长至 30 秒。它添加了文档和网页输入，继承了 Wan 2.7 的编辑功能，并作为托管服务提供。

### **Wan 3.0开源吗？**

阿里巴巴通过托管 API 提供 Wan 3.0。 Wan2.2 权重在 Apache 2.0 许可证下发布在 Hugging Face 上。

### **我可以在本地运行 Wan 吗？**

是的，使用 Wan2.2。 Wan2.2 T2V A14B 和 TI2V 5B 权重位于 Apache 2.0 下的 Hugging Face 上。如果您更喜欢 API，DeepInfra 还托管 A14B 模型。

## **结论**

选择 Wan API 提供商意味着根据您的工作分辨率、您需要的输入以及提供商发布的操作数据量来比较价格。质量是由模型设定的，因此决策取决于这些实际因素。

- 选择 DeepInfra 实现跨 Wan 代的一个 API、1080P 最终渲染和零保留数据处理。
- 选择阿里云进行第一方访问、区域定价和 Prime 套餐。
- 选择 OpenRouter 以获得较低的 1080P 速率和公布的可靠性数据。
- 为类型化客户或合规列表选择 fal 或 Atlas Cloud。

语言模型的类似比较涵盖了 [GLM-5.3 API 提供程序](https://deepinfra.com/blog/best-glm-5-3-api-providers)。

相关文章

[![MCP 服务器解释：开发人员实用指南](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/09/MCP-servers.png)](https://deepinfra.com/blog/mcp-servers-explained)[MCP 服务器解释：开发人员实用指南开发人员](https://deepinfra.com/blog/mcp-servers-explained)<p>为 AI 应用程序提供对数据库、API、文件系统或内部服务的访问权限听起来很简单，但您必须维护集成。您需要定义模型可以访问的内容、描述操作、安全地执行请求、返回结构化结果并处理身份验证。当另一个 AI [...]</p> 时，您可能需要重复大部分工作

[![Kimi K3 vs Claude Opus 4.8 vs GPT-5.6 Sol：实用的 AI 模型比较](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/07/kimi-close-source.png)](https://deepinfra.com/blog/kimi-k3-vs-claude-opus-4-8-vs-gpt-5-6-sol)[Kimi K3 vs Claude Opus 4.8 vs GPT-5.6 Sol：实用的人工智能模型比较](https://deepinfra.com/blog/kimi-k3-vs-claude-opus-4-8-vs-gpt-5-6-sol)<p>自该比较首次运行以来发生了什么变化这里比较的三个模型中的两个已经成功，并且 GPT-5.6 Sol 的定价发生了重大变化。目前 DeepInfra 上可用的三个最强大的模型并不能按功能层完全分开。 Kimi K3（通过 DeepInfra 提供）、Claude Opus 4.8 和 GPT-5.6 Sol 的得分均在 [...]</p>

[![最佳 Qwen3.8-27B 推理提供程序 (2026)](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/10/qwen3.8-27b-best-providers.png)](https://deepinfra.com/blog/best-qwen3-8-27b-inference-providers)[最佳Qwen3.8-27B 推理提供程序 (2026)](https://deepinfra.com/blog/best-qwen3-8-27b-inference-providers)<p>Qwen3.8-27B 改变了开放权重模型的格局。它在参数数量和推理能力之间取得了特殊的平衡：一个拥有 270 亿个参数的模型，功能强大但结构紧凑。它可以在单张 24GB 卡上以 4 位量化运行，也可以在单张 80GB 卡上以全精度运行。寻找合适的基础设施来托管、扩展或[...]</p>

[查看全部](https://deepinfra.com/blog)
