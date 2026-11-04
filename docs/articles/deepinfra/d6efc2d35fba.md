---
vendor: deepinfra
title: MiMo-V2.6-Pro: Model Documentation & Integration Guide
original_title: 
url: https://deepinfra.com/blog/mimo-v2-6-pro-model-documentation-integration-guide
date: 2026-11-04
lang: zh
captured: 2026-11-05
extractor: readability-v1
translator: mt
status: translated
body_sha: 3f8303415da1
---

# MiMo-V2.6-Pro：模型文档和集成指南

DeepInfra 发布于 2026.11.04

![MiMo-V2.6-Pro：模型文档和集成指南](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/10/MiMo-V2.6-Pro-Integration-Guide.png)

[MiMo-V2.6-Pro](https://deepinfra.com/XiaomiMiMo/MiMo-V2.6-Pro) 是一款旗舰稀疏专家混合 (MoE) 模型，专为全模态智能和自主代理工作流程而构建。它拥有 1.02 万亿个参数，其中 420 亿个在推理过程中被激活，并且本身就是为了在单个统一架构中处理文本、图像、视频和音频而构建的。

MiMo-V2.6-Pro 具有 1,048,576 个令牌 (1M) 上下文窗口，并通过大规模混合强化学习进行优化，专为要求苛刻的技术任务而设计，包括长范围编码、复杂的多工具交互和企业级网络安全分析。

## 关键创新和最新更新

小米将MiMo-V2.6-Pro定位为V2.6系列旗舰，推出了多种针对AI自我提升和多模态推理的方法论。

### 混合强化学习：“你只能强化学习一次”

MiMo-V2.6-Pro 的核心是小米称之为“You Only RL Once”的训练方法。该模型不是针对不同领域运行单独的强化学习 (RL) 通道，而是使用跨编码、一般代理任务、视觉处理和网络安全的单一混合 RL 运行进行训练。这使得能力相互增强，目标是将策略转移到训练期间未直接覆盖的场景。

这与小米称为“Groupwise Agentic Grading”的自我改进循环相结合，该循环使用完全异步的组相对策略优化（GRPO）。该系统对模型自身的轨迹进行评估和排名，引导其走向更有效的问题解决路径，同时应用对抗性筛选进行对齐。

### 全模式功能

MiMo-V2.6-Pro 包括专用的 6.81 亿参数 MiMo Vision Transformer (ViT) 和独立的音频编码器，允许同时分析多种数据类型。与 1M 令牌上下文窗口相结合，该模型可以接受整个代码存储库、长工具跟踪和多会话代理运行，而不会丢失上下文。

### 生态系统整合

Hugging Face 和 ModelScope 上提供了权重。该模型集成到小米自己的AI Studio和MiMo Code中，并支持通过SGLang和vLLM服务框架进行部署。

## 性能基准

下表反映了小米自己发布的与 Claude Opus 5 和 GPT-5.6 Sol 的基准比较；这些是供应商报告的数字，而不是独立复制的第三方结果，应相应阅读。

| **基准（类别）** | **MiMo-V2.6-Pro** | **Claude Opus 5** | **GPT-5.6 Sol** |
| ---| ---| ---| ---|
| DeepSWE v1.1（编码）| 71.9 | 71.9 74.0 | 74.0 73.0 | 73.0
| AutomationBench v1.0.6（总代理）| 53.1 | 53.1 50.3 | 50.3 45.8 | 45.8
| OSWorld 验证（总代理）| 82.0 | 83.4 | 83.4 83.0 |
| GDPVal 2.1 — AA（推理、Elo）| 1673 | 1673 1708 | 1708 1588 | 1588
| Terminal Bench 2.1（终端/操作系统）| 89.9 | 89.9 89.1 | 89.1 88.8 |
| MiMo 视觉编码（视觉代理）| 72.3 | 72.3 70.0 | 70.0 73.4 | 73.4

### 专业优势

以下也是小米公布的数据：

- 网络安全：CyberGym 上为 94.0，MiMo Cyber Bench 上为 80.2，旨在利用验证和自主威胁缓解。
- 科学研究：在“联合科学家”用例中，小米报告称该模型已用于帮助设计用于环境吸附的金属有机框架，包括文献综述和假设生成。
- 创意工程：原生支持 MIDI 生成、管弦乐创作和端到端视频创作，包括节拍同步编辑。

## 技术架构

尽管规模庞大，但为了保持推理速度快，MiMo-V2.6-Pro 使用了多项架构优化：

- 稀疏 MoE：总共 70 层（60 个滑动窗口注意力/10 个全局注意力），平衡效率与远程依赖建模。
- 多令牌预测 (MTP)：5 层推测解码器每次前向传递最多预测 7 个令牌，从而提高吞吐量。
- 推测解码：EAGLE 风格的算法并行验证多个令牌以减少延迟。

## API 入门

MiMo-V2.6-Pro API 使用标准[OpenAI 兼容的 HTTP POST 端点](https://docs.deepinfra.com/quickstart)，因此它可以轻松集成到现有工作流程中。

### 身份验证

请求需要通过标准 HTTP 授权标头传递的 API 密钥。

|授权：承载<YOUR_API_KEY>内容类型：application/json |
| ---|

### API 端点

- 托管（DeepInfra）：https://api.deepinfra.com/v1/openai/chat/completions
- 自托管 (SGLang/vLLM)：http://<主机>:<端口>/v1/chat/completions
- 模型标识符：XiaomiMiMo/MiMo-V2.6-Pro 或XiaomiMiMo/MiMo-V2.6-Pro-RL，与 [DeepInfra 模型目录](https://docs.deepinfra.com/models) 中的所有其他托管模型一起列出

### 实现示例（Python）
```
import os
import requests
 
api_key = os.environ.get("DEEPINFRA_API_KEY")
url = "https://api.deepinfra.com/v1/openai/chat/completions"
 
payload = {
    "model": "XiaomiMiMo/MiMo-V2.6-Pro",
    "messages": [{"role": "user", "content": "Explain the role of sparse MoE in LLMs."}],
    "temperature": 1.0,
    "top_p": 0.95
}
 
response = requests.post(url, headers={"Authorization": f"Bearer {api_key}"}, json=payload)
print(response.json())copy
```
### 常用参数

| **参数** | **类型** | **描述** |
| ---| ---| ---|
|留言 |数组|必需的。支持文本、图像、视频和音频输入。 |
|温度|浮动|推荐：1.0。 |
|工具|数组|代理工作流程的可调用函数列表 - 请参阅 DeepInfra 的[函数调用指南](https://deepinfra.com/blog/deepinfra-function-calling-guide)。 |
|最大令牌数 |整数 | 1M 上下文窗口内的最大令牌数。 |

## 定价和使用

定价与消耗量成比例，并按每 100 万个代币计费，[缓存输入代币有大幅折扣](https://docs.deepinfra.com/chat/prompt-caching)。 MiMo-V2.6-Pro 和所有其他托管型号的完整当前费率位于 [DeepInfra 定价页面](https://deepinfra.com/pricing)。

| **型号变体** | **输入（缓存未命中）** | **输入（缓存命中）** | **输出** |
| ---| ---| ---| ---|
| MiMo-V2.6-Pro | 0.435 美元/100 万代币 | $0.0036 / 100 万代币 | 0.87 美元/100 万代币 |
|专业超高速 | 4.35 美元/100 万代币 | $0.036 / 100 万代币 | 8.70 美元/100 万代币 |

- 基于使用量的计费：定价直接与消耗量相关，按每 100 万个代币计费。
- UltraSpeed 模式：通过 MiMo Desktop 和 API 提供，为实时交互提供更快的输出速度。确认您的工作负载的当前吞吐量数据，因为服务模式性能可能因提供商而异。

＃＃ 结论

MiMo-V2.6-Pro 将万亿参数 MoE 架构与本机全模式支持和 1M 代币上下文窗口相结合，为开发人员提供了长期代理应用程序和安全工具的构建块。无论工作负载是复杂的软件工程还是高级科学研究，MiMo-V2.6-Pro 都是为生产规模的推理深度和吞吐量而构建的。

要更深入地了解它与其他最新版本在成本和基准方面的比较，请参阅我们对 [DeepSeek V4 Pro 的定价和提供商](https://deepinfra.com/blog/deepseek-v4-pro-pricing-guide-2026-providers-cost-analysis) 的报道。有关更多技术细节，请参阅 MiMo-V2.6 技术报告或 Discord 和 Telegram 上的开发者社区。

相关文章

[![GLM-5.3-Flash 文档和集成指南](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/09/glm-5.3-flash-docs.png)](https://deepinfra.com/blog/glm-5-3-flash-documentation-integration-guide)[GLM-5.3-Flash 文档和集成指南](https://deepinfra.com/blog/glm-5-3-flash-documentation-integration-guide)<p>GLM-5.3-Flash 是由 Z.ai 开发并托管在 DeepInfra 上的前沿级原生多模态模型。它采用混合专家 (MoE) 架构，总参数为 3200 亿个，其中只有 180 亿个参数在推理过程中处于活动状态。该模型是为复杂的长期任务而构建的——高级软件工程、代理工作流程和多模式推理——具有上下文[...]</p>

[![GLM-5.1 API 基准：延迟、吞吐量和成本](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/05/glm-5.1-cost.png)](https://deepinfra.com/blog/glm-5-1-api-benchmarks-latency-throughput-cost)[GLM-5.1 API 基准：延迟、吞吐量和成本](https://deepinfra.com/blog/glm-5-1-api-benchmarks-latency-throughput-cost)<p>Z.ai 的 GLM-5.1 是一个 2026 年 4 月为长期代理工程构建的开放权重推理模型 - 有效访问它意味着导航真正广泛的提供商选项。在 10 个基准 API 提供商中，混合定价范围为每 100 万个代币 0.74 至 1.70 美元，输出速度为 33.8 至 175.2 t/s，最快的提供商为 5.2 倍 [...]</p>

[！[免费比较 Llama2 与 OpenAI 模型。](https://deepinfra.com/blog/llama-boxer.webp)](https://deepinfra.com/blog/compare-models)[免费比较 Llama2 与 OpenAI 模型。](https://deepinfra.com/blog/compare-models)在 DeepInfra，我们托管最好的开源 LLM 模型。我们一直在努力让我们的 API 变得简单易用。今天，我们很高兴地宣布一种非常简单的方法来快速尝试我们的模型，如 Llama2 70b 和 [Mistral 7b](/mistralai/Mistral-7B-Instruct...

[查看全部](https://deepinfra.com/blog)
