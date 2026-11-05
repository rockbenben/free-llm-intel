---
vendor: deepinfra
title: MiMo-V2.6-Pro：模型文档与集成指南
original_title: 
url: https://deepinfra.com/blog/mimo-v2-6-pro-model-documentation-integration-guide
date: 2026-11-04
lang: zh
captured: 2026-11-05
extractor: readability-v1
translator: agent
status: translated
body_sha: 3a70e4fa7f8b
---

# MiMo-V2.6-Pro：模型文档与集成指南

由 DeepInfra 发布于 2026.11.04

![MiMo-V2.6-Pro：模型文档与集成指南](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/10/MiMo-V2.6-Pro-Integration-Guide.png)

[MiMo-V2.6-Pro](https://deepinfra.com/XiaomiMiMo/MiMo-V2.6-Pro) 是一款为全模态智能与自主 agentic 工作流打造的旗舰稀疏 Mixture-of-Experts（MoE）模型。它的总参数为 1.02 万亿，推理时激活 420 亿参数，原生即为在单一、统一的架构内处理文本、图像、视频和音频而构建。

MiMo-V2.6-Pro 有 1,048,576 token（1M）的上下文窗口，并通过大规模混合强化学习做了优化，为高要求的技术任务而设计，包括长时程编码、复杂的多工具交互，以及企业级的网络安全分析。

## 关键创新与近期更新

Xiaomi 把 MiMo-V2.6-Pro 定位为 V2.6 系列的旗舰，并引入了几项面向 AI 自我改进与多模态推理的方法。

### 混合强化学习：「You Only RL Once」

MiMo-V2.6-Pro 的核心是 Xiaomi 称为「You Only RL Once」的训练思路。它不是为不同领域分别跑一遍强化学习（RL），而是在编码、通用 agent 任务、视觉处理与网络安全上，用一次混合的 RL 训练完成。这让各项能力彼此加强，目标是把策略迁移到训练中没有直接覆盖的场景里去。

与之配套的是一套 Xiaomi 称为 Groupwise Agentic Grading 的自我改进回路，它使用完全异步的 Group Relative Policy Optimization（GRPO）。这套系统评估并排序模型自己的 trajectory，把它引向更高效的解题路径，同时在对齐上施加对抗性筛查。

### 全模态能力

MiMo-V2.6-Pro 内置一个专门的 6.81 亿参数 MiMo Vision Transformer（ViT）以及独立的音频编码器，因而可以同时分析多种数据类型。配上 1M token 的上下文窗口，模型可以吃下整个代码仓库、超长的工具轨迹和多会话的 agent 运行而不丢上下文。

### 生态集成

权重在 Hugging Face 与 ModelScope 上可得。模型已集成进 Xiaomi 自家的 AI Studio 和 MiMo Code，并支持通过 SGLang 与 vLLM 服务框架部署。

## 性能基准

下表反映的是 Xiaomi 自己发布的、针对 Claude Opus 5 与 GPT-5.6 Sol 的 benchmark 对比；这些是厂商自报的数字，而不是第三方独立复现的结果，阅读时应当据此判断。

| **Benchmark（类别）** | **MiMo-V2.6-Pro** | **Claude Opus 5** | **GPT-5.6 Sol** |
| --- | --- | --- | --- |
| DeepSWE v1.1（编码） | 71.9 | 74.0 | 73.0 |
| AutomationBench v1.0.6（通用 agent） | 53.1 | 50.3 | 45.8 |
| OSWorld-Verified（通用 agent） | 82.0 | 83.4 | 83.0 |
| GDPVal 2.1 — AA（推理，Elo） | 1673 | 1708 | 1588 |
| Terminal Bench 2.1（终端/操作系统） | 89.9 | 89.1 | 88.8 |
| MiMo Visual Coding（视觉 agent） | 72.3 | 70.0 | 73.4 |

### 专门的强项

以下同样都是 Xiaomi 自报的数字：

- 网络安全：在 CyberGym 上 94.0，在 MiMo Cyber Bench 上 80.2，面向漏洞利用验证与自主威胁消解。
- 科学研究：在「co-scientist」类用例中，Xiaomi 报告该模型被用来协助设计面向环境吸附的金属有机框架，工作包括文献综述与假设生成。
- 创意工程：原生支持 MIDI 生成、管弦乐编曲与端到端的视频创作，包括按节拍对齐的剪辑。

## 技术架构

为了在这么大尺度上仍保持推理速度，MiMo-V2.6-Pro 用了几项架构上的优化：

- 稀疏 MoE：共 70 层（60 层滑动窗口注意力 / 10 层全局注意力），在效率与长程依赖建模之间取得平衡。
- Multi-Token Prediction（MTP）：一个 5 层的投机解码器每次前向传播最多预测 7 个 token，用以提升吞吐。
- 投机式解码：采用 EAGLE 风格的算法并行校验多个 token，以降低延迟。

## 开始使用 API

MiMo-V2.6-Pro 的 API 使用标准的 [OpenAI 兼容 HTTP POST 端点](https://docs.deepinfra.com/quickstart)，因此能轻松接入现有工作流。

### 身份验证

请求需要通过标准 HTTP Authorization 请求头传入一个 API key。

| Authorization: Bearer <YOUR_API_KEY>Content-Type: application/json |
| --- |

### API 端点

- 托管（DeepInfra）：https://api.deepinfra.com/v1/openai/chat/completions
- 自托管（SGLang/vLLM）：http://<host>:<port>/v1/chat/completions
- 模型标识符：XiaomiMiMo/MiMo-V2.6-Pro 或 XiaomiMiMo/MiMo-V2.6-Pro-RL，与其余所有托管模型一同列在 [DeepInfra 模型目录](https://docs.deepinfra.com/models) 中

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

| **参数** | **类型** | **说明** |
| --- | --- | --- |
| messages | array | 必填。支持文本、图像、视频和音频输入。 |
| temperature | float | 推荐：1.0。 |
| tools | array | 供 agentic 工作流调用的函数列表 — 见 DeepInfra 的 [function calling 指南](https://deepinfra.com/blog/deepinfra-function-calling-guide)。 |
| max_tokens | integer | 1M 上下文窗口内的最大 token 数。 |

## 定价与用量

价格随消耗递增并按每 100 万 token 计费，[缓存输入 token 还有大幅折扣](https://docs.deepinfra.com/chat/prompt-caching)。MiMo-V2.6-Pro 以及其余所有托管模型的完整当前费率都在 [DeepInfra 定价页](https://deepinfra.com/pricing) 上。

| **模型变体** | **输入（缓存未命中）** | **输入（缓存命中）** | **输出** |
| --- | --- | --- | --- |
| MiMo-V2.6-Pro | $0.435 / 1M tokens | $0.0036 / 1M tokens | $0.87 / 1M tokens |
| Pro-UltraSpeed | $4.35 / 1M tokens | $0.036 / 1M tokens | $8.70 / 1M tokens |

- 按用量计费：价格与消耗直接挂钩，按每 100 万 token 计费。
- UltraSpeed 模式：可通过 MiMo Desktop 和 API 使用，为实时交互提供显著更快的输出速度。请就自己的工作负载确认当前的吞吐数字，因为服务模式的表现会因提供商而异。

## 结论

MiMo-V2.6-Pro 把万亿参数级的 MoE 架构、原生全模态支持与 1M token 的上下文窗口结合在了一起，为开发者提供了构建长时程 agentic 应用与安全工具的基础构件。无论工作负载是复杂软件工程还是前沿科学研究，MiMo-V2.6-Pro 都是为生产规模下的推理深度与吞吐而打造的。

想看它与其他近期发布在成本与 benchmark 上的对比，可参考我们关于 [DeepSeek V4 Pro 定价与提供商](https://deepinfra.com/blog/deepseek-v4-pro-pricing-guide-2026-providers-cost-analysis) 的报道。需要更多技术细节，请查阅 MiMo-V2.6 技术报告，或 Discord 与 Telegram 上的开发者社区。

相关文章

[![GLM-5.3-Flash 文档与集成指南](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/09/glm-5.3-flash-docs.png)](https://deepinfra.com/blog/glm-5-3-flash-documentation-integration-guide)[GLM-5.3-Flash 文档与集成指南](https://deepinfra.com/blog/glm-5-3-flash-documentation-integration-guide)<p>GLM-5.3-Flash 是 Z.ai 开发的 frontier 级、原生多模态模型，托管在 DeepInfra 上。它采用 Mixture-of-Experts（MoE）架构，总参数 3,200 亿，其中推理时只有 180 亿处于激活状态。该模型为复杂、长时程任务而打造——高级软件工程、agentic 工作流与多模态推理——其上下文 [&hellip;]</p>

[![GLM-5.1 API 基准：延迟、吞吐与成本](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/05/glm-5.1-cost.png)](https://deepinfra.com/blog/glm-5-1-api-benchmarks-latency-throughput-cost)[GLM-5.1 API 基准：延迟、吞吐与成本](https://deepinfra.com/blog/glm-5-1-api-benchmarks-latency-throughput-cost)<p>Z.ai 的 GLM-5.1 是一款 2026 年 4 月的开放权重推理模型，为长时程 agentic 工程而打造——而要顺畅地用上它，意味着得在一堆真实存在的提供商选项之间做取舍。在 10 家被评测的 API 提供商中，混合价格区间为 $0.74 到 $1.70 每 1M tokens，输出速度从 33.8 到 175.2 t/s，最快的提供商是 5.2x [&hellip;]</p>

[![免费对比 Llama2 与 OpenAI 模型。](https://deepinfra.com/blog/llama-boxer.webp)](https://deepinfra.com/blog/compare-models)[免费对比 Llama2 与 OpenAI 模型。](https://deepinfra.com/blog/compare-models)在 DeepInfra，我们托管着最好的开源 LLM 模型。我们一直在努力把我们的 API 做得简单好用。今天要宣布的是一种非常便捷的方式，让你快速试用我们的模型，比如 Llama2 70b 和 [Mistral 7b](/mistralai/Mistral-7B-Instruc...

[查看全部](https://deepinfra.com/blog)
