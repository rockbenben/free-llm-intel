---
vendor: modular_cloud
title: Day Zero 首发：Gemma 4 在 NVIDIA 与 AMD 上的最快性能
original_title: "Modular: Day Zero Launch: Fastest Performance for Gemma 4 on NVIDIA and AMD"
url: https://www.modular.com/blog/day-zero-launch-fastest-performance-for-gemma-4-on-nvidia-and-amd
date: 2026-04-02
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Day Zero 首发：Gemma 4 在 NVIDIA 与 AMD 上的最快性能

今天，Google DeepMind 发布了 Gemma 4 系列模型——来自打造 Google Gemini 模型的同一支团队的最新业界领先开放模型。我们很高兴成为 day zero 首发合作伙伴，邀请开发者和企业在 [Modular Cloud](https://console.modular.com/signup?utm_campaign=day0&utm_source=blog) 上体验 Gemma 4 的多模态能力，在 NVIDIA 和 AMD 上均具备业界领先性能。

我们的基准测试显示，在 NVIDIA B200 上相比 vLLM 吞吐量高出 15%。

## 认识 Gemma 4 家族

Modular 托管 Google 新发布的 [Gemma 4 系列模型](https://huggingface.co/collections/google/gemma-4)的全部变体。所有变体原生多模态，支持文本、图像和视频，并具备动态分辨率与宽高比。

**Gemma 4 31B** 是一个 310 亿参数的稠密模型，采用重新设计的架构，同时提升了效率和长上下文质量。它拥有 256K 上下文窗口，专为需要在大规模输入上进行深度推理的高要求任务而生。

**Gemma 4 26B A4B** 是一个 Mixture-of-Experts (MoE) 模型，总参数 26B，但每次前向传播仅激活 4B，意味着你只需一小部分的算力成本就能获得更大模型的质量。它同样支持 256K 上下文窗口，并被设计为适配高端服务器的内存规格。

无论你运行的是 OCR、视频与图像理解，还是 256K 上下文工作流，处理你初始测试的那个由 MAX 驱动的引擎，同样运行你的生产级 Modular Cloud endpoint，因此扩展时不会有任何意外。

## 在 NVIDIA 与 AMD 上高性能运行 Gemma 4

Modular Cloud 运行在 [MAX](https://www.modular.com/open-source/max) 之上——我们的推理框架，将 GPU kernel、图编译和高性能服务统一在一个与硬件无关的平台上。Modular 让团队能够快速行动：我们把 Gemma 4 在 NVIDIA 和 AMD 上都优化到了业界领先水平，并在几天内就在 Modular Cloud 上上线了生产就绪的 endpoint。

高性能是 MAX 与生俱来的，在 NVIDIA B200 上，**Gemma 4 on MAX 比 vLLM 快 15%****，同时没有任何精度损失。**更多细节即将发布，敬请期待。

| **精度** | **MAX (B200)** | **vLLM* (B200)** | MAX (MI355) |
| --- | --- | --- | --- |
| MMLU Pro | 84.72% | （未测量） | **84.94%** |
| GSM8K Llama COT | **95.94%** | 94.69% | 94.37% |
| ChartQA | **84.69%** | 84.38% | 84.38% |

**使用官方提供的 vllm-0.18.2rc1.dev7*3 进行基准测试

## 今天就在 Modular Cloud 上试用 Gemma 4

Gemma 4 是最强大的开放模型之一——但能力只有落地才有意义。Modular Cloud 提供从第一次 API 调用到生产 endpoint 的直线路径，在 NVIDIA 和 AMD 硬件上均经过优化，无需做"基础设施考古"。

借助 Modular Cloud，你可以：

- **从 playground 平滑过渡到生产，无需切换技术栈**——运行你测试的 MAX 引擎同样驱动你的生产 endpoint。
- **为你的工作负载选择合适的 GPU**——在 NVIDIA 或 AMD 上运行，视成本与吞吐量需求而定。技术栈会自动选取正确的配置和批大小，让你不必靠猜。
- **更快地交付多模态与长上下文功能**——OCR、视频+图像理解和 256K 上下文工作流开箱即用。

[**开始在 Modular Cloud 上构建 →**](https://console.modular.com/signup?utm_campaign=day0blog)

或者，用 [MAX](https://docs.modular.com/max/get-started/) 自己免费体验。

*有兴趣在你自己的基础设施或自己的云上运行 MAX？*[预约演示](https://www.modular.com/request-demo)，我们将围绕你的模型、硬件和性能目标演示一套部署方案。*
