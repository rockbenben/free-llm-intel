---
vendor: deepinfra
title: DeepInfra 与 Opper AI 合作：Opper 网关接入 100+ 模型
original_title: 
url: https://deepinfra.com/blog/deepinfra-opper-partnership
date: 2026-11-17
lang: zh
captured: 2026-11-21
extractor: readability-v1
translator: agent
status: translated
body_sha: 1a902f3fb555
---

# DeepInfra 与 Opper AI 合作：Opper 网关接入 100+ 模型

发布于 2026.11.17，作者 DeepInfra

![DeepInfra 与 Opper AI 合作：Opper 网关接入 100+ 模型](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/11/deepinfra-opper-partnership-header.png)

*加利福尼亚州帕洛阿尔托，2026 年 11 月。* DeepInfra 与 [Opper AI](https://opper.ai/blog/deepinfra-partnership) 达成合作，让 DeepInfra 的开源模型推理通过 Opper 托管于欧盟的 AI 网关对外提供。开发者现在可以通过 Opper API 调用 100 多个由 DeepInfra 托管的模型，从 Kimi K3、GLM-5.3、DeepSeek V4.1 Flash 到 MiniMax M3、Nemotron 3.5 Super VL 和 FLUX.2 Pro，并对每一次调用套用 Opper 的支出、数据保留和路由 Rules。

## 这对开发者意味着什么

如果你已经在 DeepInfra 上运行，现有集成不受影响。这次合作只是给同一批模型加了第二条路径：走 Opper，和你可能已经在该平台上使用的其他提供商并列。

**每个层级一个模型字符串。** Opper 上的每个 DeepInfra 对话模型都有 standard 层级，许多还提供 flex 和 priority：

| Opper 模型字符串 | 用途 |
| --- | --- |
| `deepinfra/…` | standard 层级，日常调用 |
| `deepinfra:flex/…` | 便宜约五分之一，适合评测和后台任务 |
| `deepinfra:priority/…` | 必须最先响应的交互式流量 |

大规模任务可以走 Opper 的 [Batch API](https://opper.ai/blog/batch-vs-flex-vs-standard)，按 flex 价格计费。每个模型各层级的价格，以及 DeepInfra 的图像、语音、视频和 embedding 模型，都列在 [Opper 的 DeepInfra 提供商页面](https://opper.ai/provider/deepinfra)上。

**模型目录。** 通过 Opper，你可以触达今天 agent 实际在用的开源模型：DeepSeek V4 和 V4.1、Moonshot 的 Kimi K3、Z.ai 的 GLM-5.3、Qwen3.5 到 Qwen3.8 系列、Google 的 Gemma 4、Meta 的 Llama，以及 Thinking Machines 的 Inkling。同一条路径还覆盖 Black Forest Labs 的图像模型、字节跳动的 Seedance 2.0 视频模型、Qwen3 TTS 语音模型、用于搜索的 embedding，以及 NVIDIA 的 Nemotron 系列，从 Nemotron 3.5 Super VL 到 Nemotron 3 Ultra。

**价格。** 据 Opper 称，对于 MiniMax M3、NVIDIA Nemotron 3.5 Super VL、DeepSeek V3.2 和 Qwen3 235B Instruct 2507，DeepInfra 目前是 Opper 网关上任何区域里最便宜的路径。

**数据处理。** Opper 上的每条 DeepInfra 路径都在美国运行。standard、flex 和 priority 调用中，prompt 和 completion 不会被记录，也不会用于训练，并可提供 DPA。Batch 任务会先把请求存住，等轮到再跑，任何 batch API 都必须如此。DeepInfra 拥有并自营 GPU 基础设施，通过了 SOC 2 和 ISO 27001 认证。Opper 的提供商页面逐一列出了每条路径的驻留地和保留策略。

### 第一次调用

Opper 兼容 OpenAI，所以要换成 DeepInfra 的模型，只需改 base URL 和模型字符串：

```
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPPER_API_KEY"],
    base_url="https://api.opper.ai/v3/compat",
)

completion = client.chat.completions.create(
    model="deepinfra/MiniMaxAI/MiniMax-M3",  # or "deepinfra:flex/MiniMaxAI/MiniMax-M3" for background work
    messages=[{"role": "user", "content": "Hello"}],
)
print(completion.choices[0].message.content)copy
```

## 为什么选 Opper：每次调用都有 Rules

Opper 把自己定位为面向 agent 的欧洲 AI 网关。它总部在斯德哥尔摩，通过一个托管于欧盟、符合 GDPR 的 API 为开发者提供 700 多个模型。路由只是它做的事里的一部分。通过 Opper 的每次调用都可以跑在你的 **[Rules](https://opper.ai/ai-control-plane)** 之下：支出上限、数据保留、模型访问、内容检查和路由顺序，按组织或按项目设定一次即可。

对 DeepInfra 用户来说，这意味着你可以：

- 把 DeepInfra 的 flex 层级固定用于评测任务，
- 把 DeepInfra 设为另一家提供商后面的 fallback，或者反过来，
- 给支出设上限、限定项目能调用哪些模型，而不用改应用代码。

## 选 Opper 还是直接用 DeepInfra 的 API？

两条路径到达的是同一批 DeepInfra 模型。怎么选取决于调用之外还想要什么。

**适合用 Opper 的情况：** 你通过一个 key 使用多家提供商的模型，希望集中管理支出上限、模型白名单和保留规则，或者希望由网关来处理 DeepInfra 与其他提供商之间的路由和 fallback。

**适合直接用 DeepInfra API 的情况：** 你的工作负载只跑 DeepInfra 的模型，不需要在请求路径上多一个网关。你能拿到完整的 [DeepInfra 模型目录](https://deepinfra.com/models)、每个模型页面上列出的[价格](https://deepinfra.com/pricing)，以及面向可以等一等的任务的 [Flex 服务层级](https://deepinfra.com/blog/flex-service-tier)。

## 引言

“DeepInfra 运营着业内最深的一份开源模型目录，价格让它天然适合承载高并发的活儿。同一批模型上有 standard、flex、priority 和 batch，Opper 上的构建者可以让每次调用都匹配它需要的速度和价格。”—— Opper AI 联合创始人兼 CEO Göran Sandahl

“我们做 DeepInfra，是为了在自己的 GPU 上以生产规模跑开源模型，并且让每个 token 的价格都说得过去。Opper 用一个 API 把这本目录摆到广大的构建者社区面前，与他们已经在用的其他模型并列。”—— DeepInfra 联合创始人兼 CEO Nikola Borisov

## 可用性

DeepInfra 的模型今天已经在 Opper 上线。开始使用：

- 阅读 Opper 的公告：[Opper AI 与 DeepInfra 合作，把 100+ AI 模型接入网关](https://opper.ai/blog/deepinfra-partnership)
- 在 [Opper 的 DeepInfra 提供商页面](https://opper.ai/provider/deepinfra)查看模型、层级和每条路径的价格
- 浏览 [DeepInfra 模型目录](https://deepinfra.com/models)和[价格](https://deepinfra.com/pricing)

## 关于 DeepInfra

DeepInfra 是一家推理云，2022 年成立，总部位于加利福尼亚州帕洛阿尔托。它拥有并自营 GPU 基础设施，通过兼容 OpenAI 的 API 提供文本、语音、图像、视频和 embedding 开源模型，零数据保留，并通过 SOC 2 和 ISO 27001 认证。2026 年 5 月，它完成 1.07 亿美元 B 轮融资，由 500 Global 和 Georges Harik 共同领投，NVIDIA、Samsung Next 和 Supermicro 参投。

## 关于 Opper AI

Opper AI 是面向 agent 的欧洲 AI 网关，总部在斯德哥尔摩。它通过一个托管于欧盟、符合 GDPR 的 API 让开发者访问 700 多个领先 AI 模型，按用量付费，并提供支出上限、模型白名单、零数据保留和完整的 OpenAI SDK 兼容。

相关文章

[![GLM-5.3 现已在 DeepInfra 上线](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/09/glm-5.3-deepinfra.png)](https://deepinfra.com/blog/glm-5-3-deepinfra)[GLM-5.3 现已在 DeepInfra 上线](https://deepinfra.com/blog/glm-5-3-deepinfra)<p>GLM-5.3 与 GLM-5.2 共享基础模型，因此每一项性能提升都来自后训练。Z.ai 扩展了已有的强化学习栈，并于 2026 年 8 月 14 日发布成果。GLM-5.3 是一款推理模型，面向复杂软件工程和长周期 agentic 任务。在 Z.ai 内部的 Code Bench 上，它比 GLM-5.2 提升 50%，[&hellip;]</p>

[![推出 GPU Instances：面向 AI 工作负载的按需 GPU 算力](https://deepinfra.com/blog/gpu-instances.jpg)](https://deepinfra.com/blog/gpu-instances)[推出 GPU Instances：面向 AI 工作负载的按需 GPU 算力](https://deepinfra.com/blog/gpu-instances)用我们全新的 GPU Instances 功能，几分钟内就能启动专用 GPU 容器，为机器学习训练、推理和计算密集型工作负载而设计。

[![DeepInfra 上线 NVIDIA Nemotron 模型，覆盖视觉、检索和 AI 安全](https://deepinfra.com/blog/nvidia-deepinfra-logos.png)](https://deepinfra.com/blog/nvidia-nemotron-release)[DeepInfra 上线 NVIDIA Nemotron 模型，覆盖视觉、检索和 AI 安全](https://deepinfra.com/blog/nvidia-nemotron-release)DeepInfra 从发布首日就提供全新的开放 NVIDIA Nemotron 视觉语言与 OCR AI 模型。作为专注于性能与成本效率的领先推理提供商，我们以业界最优价格提供这些前沿模型，让开发者在不牺牲预算或性能的前提下构建专用 AI agent。

[查看全部](https://deepinfra.com/blog)
