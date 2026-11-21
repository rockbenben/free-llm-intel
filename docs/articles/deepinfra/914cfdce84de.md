---
vendor: deepinfra
title: DeepInfra 与 Opper AI 合作：Opper 网关接入 100+ 模型
original_title: 
url: https://deepinfra.com/blog/deepinfra-opper-partnership
date: 2026-11-17
lang: zh
captured: 2026-11-18
extractor: readability-v1
translator: llm
status: translated
body_sha: 1716080a87df
---

# DeepInfra 与 Opper AI 达成合作：Opper Gateway 上线 100+ 模型

发布于 2026.11.17，作者 DeepInfra

![DeepInfra 与 Opper AI 达成合作：Opper Gateway 上线 100+ 模型](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/11/deepinfra-opper-partnership-header.png)

*加利福尼亚州帕洛阿尔托，2026 年 11 月。* DeepInfra 与 [Opper AI](https://opper.ai/blog/deepinfra-partnership) 达成合作，让 DeepInfra 的开源模型推理能力通过 Opper 托管于欧盟的 AI gateway 对外提供。开发者现在可以通过 Opper API 调用 100 多个由 DeepInfra 托管的模型，从 Kimi K3、GLM-5.3、DeepSeek V4.1 Flash 到 MiniMax M3、Nemotron 3.5 Super VL 和 FLUX.2 Pro，并对每一次调用应用 Opper 的支出、数据保留和路由 Rules。

## 这对开发者意味着什么

如果你已经在 DeepInfra 上运行，现有集成不受任何影响。此次合作只是为同一批模型增加了第二条路径：通过 Opper 调用，与你可能已在该平台使用的其他 provider 并列。

**每个层级对应一个模型字符串。** Opper 上的每个 DeepInfra 对话模型都有 standard 层级，许多还提供 flex 和 priority：

| Opper 模型字符串 | 用途 |
| --- | --- |
| `deepinfra/…` | Standard 层级，用于日常调用 |
| `deepinfra:flex/…` | 便宜约五分之一，用于评测和后台任务 |
| `deepinfra:priority/…` | 必须优先响应的交互式流量 |

大规模任务可以通过 Opper 的 [Batch API](https://opper.ai/blog/batch-vs-flex-vs-standard) 以 flex 价格运行。每个模型各层级的价格，以及 DeepInfra 的图像、语音、视频和 embedding 模型，都列在 [Opper 的 DeepInfra provider 页面](https://opper.ai/provider/deepinfra)上。

**模型目录。** 通过 Opper，你可以访问当前 agent 所运行的开源模型：DeepSeek V4 和 V4.1、Moonshot 的 Kimi K3、Z.ai 的 GLM-5.3、Qwen3.5 至 Qwen3.8 系列、Google 的 Gemma 4、Meta 的 Llama 以及 Thinking Machines 的 Inkling。同一路径还覆盖 Black Forest Labs 的图像模型、字节跳动的 Seedance 2.0 视频模型、Qwen3 TTS 语音模型和用于搜索的 embedding，以及 NVIDIA 的 Nemotron 系列，从 Nemotron 3.5 Super VL 到 Nemotron 3 Ultra。

**价格。** 据 Opper 称，对于 MiniMax M3、NVIDIA Nemotron 3.5 Super VL、DeepSeek V3.2 和 Qwen3 235B Instruct 2507，DeepInfra 目前是 Opper gateway 上任何区域中最便宜的路径。

**数据处理。** Opper 上每条 DeepInfra 路径都在美国运行。在 standard、flex 和 priority 调用中，prompt 和 completion 不会被记录，也不会用于训练，并且可提供 DPA。Batch 任务会在运行前保留请求，这是任何 batch API 都必须的。DeepInfra 拥有并运营自己的 GPU 基础设施，并通过 SOC 2 和 ISO 27001 认证。Opper 的 provider 页面列出了每条路径的数据驻留和保留情况。

### 第一次调用

Opper 兼容 OpenAI，因此切换到 DeepInfra 模型只需更改 base URL 和模型字符串：

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

## 为什么选择 Opper：为每次调用设定 Rules

Opper 将自己描述为面向 agent 的欧洲 AI gateway。它总部位于斯德哥尔摩，通过一个托管于欧盟、符合 GDPR 的 API 为开发者提供 700 多个模型。路由只是它功能的一部分。通过 Opper 的每次调用都可以在你的 **[Rules](https://opper.ai/ai-control-plane)** 下运行：支出上限、数据保留、模型访问、内容检查和路由顺序，可按组织或按项目一次性设定。

对 DeepInfra 用户来说，这意味着你可以：

- 为评测运行锁定 DeepInfra 的 flex 层级，
- 将 DeepInfra 设为另一家 provider 之后的 fallback，或反过来，
- 限制支出并限定项目可调用的模型，而无需更改应用代码。

## 选择 Opper 还是直接使用 DeepInfra 的 API？

两条路径访问的都是同一批 DeepInfra 模型。如何选择取决于调用周边的需求。

**在以下情况使用 Opper：** 你通过一个 key 使用多家 provider 的模型，希望集中管理支出上限、模型白名单和保留规则，或希望由 gateway 处理 DeepInfra 与其他 provider 之间的路由和 fallback。

**在以下情况直接使用 DeepInfra 的 API：** 你的工作负载只运行 DeepInfra 模型，且不需要在请求路径中加入 gateway。你可以获得完整的 [DeepInfra 模型目录](https://deepinfra.com/models)、每个模型页面上列出的[价格](https://deepinfra.com/pricing)，以及适用于可等待任务的 [Flex 服务层级](https://deepinfra.com/blog/flex-service-tier)。

## 引言

“DeepInfra 运营着业界最深入的开源模型目录之一，其价格使其成为高吞吐任务的天然归宿。凭借同一批模型上的 standard、flex、priority 和 batch，Opper 上的构建者可以让每次调用匹配其所需的速率和价格。” — Göran Sandahl，Opper AI 联合创始人兼 CEO

“我们打造 DeepInfra，是为了在自己的 GPU 上以生产规模运行开源模型，并让每个 token 的价格都合理。Opper 通过一个 API 把这份目录呈现在广泛的构建者社区面前，与他们已在使用的其他模型并列。” — Nikola Borisov，DeepInfra 联合创始人兼 CEO

## 可用性

DeepInfra 模型现已在 Opper 上线。开始使用：

- 阅读 Opper 的公告：[Opper AI 与 DeepInfra 合作，将 100+ AI 模型引入 gateway](https://opper.ai/blog/deepinfra-partnership)
- 在 [Opper 的 DeepInfra provider 页面](https://opper.ai/provider/deepinfra)查看模型、层级和各路径价格
- 浏览 [DeepInfra 模型目录](https://deepinfra.com/models)和[价格](https://deepinfra.com/pricing)

## 关于 DeepInfra

DeepInfra 是一家推理云服务商，成立于 2022 年，总部位于加利福尼亚州帕洛阿尔托。它拥有并运营自己的 GPU 基础设施，通过兼容 OpenAI 的 API 提供文本、语音、图像、视频和 embedding 开源模型，承诺零数据保留，并通过 SOC 2 和 ISO 27001 认证。2026 年 5 月，它完成了由 500 Global 和 Georges Harik 共同领投的 1.07 亿美元 B 轮融资，NVIDIA、Samsung Next 和 Supermicro 参与投资。

## 关于 Opper AI

Opper AI 是面向 agent 的欧洲 AI gateway，总部位于斯德哥尔摩。它通过一个托管于欧盟、符合 GDPR 的 API，让开发者以按需付费方式访问 700 多个领先 AI 模型，并提供支出上限、模型白名单、零数据保留和完整的 OpenAI SDK 兼容性。

相关文章

[![GLM-5.3 现已在 DeepInfra 上线](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/09/glm-5.3-deepinfra.png)](https://deepinfra.com/blog/glm-5-3-deepinfra)[GLM-5.3 现已在 DeepInfra 上线](https://deepinfra.com/blog/glm-5-3-deepinfra)<p>GLM-5.3 与 GLM-5.2 共享基础模型，因此每一项性能提升都来自后训练。Z.ai 扩展了其已有的强化学习技术栈，并于 2026 年 8 月 14 日发布成果。GLM-5.3 是一个推理模型，专为复杂软件工程和长周期 agentic 任务而构建。在 Z.ai 内部的 Code Bench 上，它相比 GLM-5.2 提升了 50%，[&hellip;]</p>

[![推出 GPU Instances：面向 AI 工作负载的按需 GPU 算力](https://deepinfra.com/blog/gpu-instances.jpg)](https://deepinfra.com/blog/gpu-instances)[推出 GPU Instances：面向 AI 工作负载的按需 GPU 算力](https://deepinfra.com/blog/gpu-instances)借助我们全新的 GPU Instances 功能，几分钟内即可启动专用 GPU 容器，专为机器学习训练、推理和计算密集型工作负载而设计。

[![DeepInfra 推出对 NVIDIA Nemotron 模型的访问，覆盖视觉、检索和 AI 安全](https://deepinfra.com/blog/nvidia-deepinfra-logos.png)](https://deepinfra.com/blog/nvidia-nemotron-release)[DeepInfra 推出对 NVIDIA Nemotron 模型的访问，覆盖视觉、检索和 AI 安全](https://deepinfra.com/blog/nvidia-nemotron-release)DeepInfra 从发布首日即开始提供全新的开放 NVIDIA Nemotron 视觉语言和 OCR AI 模型。作为致力于性能与成本效率的领先推理 provider，我们以业界最优价格提供这些前沿模型，让开发者在不牺牲预算或性能的前提下构建专用 AI agent。

[查看全部](https://deepinfra.com/blog)
