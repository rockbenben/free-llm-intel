---
vendor: anyscale
title: 用 Ray Serve 构建生产级 AI 应用
original_title: Building Production AI Applications with Ray Serve
url: https://anyscale.com/blog/building-production-ai-applications-with-ray-serve
date: 2023-10-24
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# 用 Ray Serve 构建生产级 AI 应用

作者：Anyscale Ray Team | 2023 年 10 月 24 日

2024 年 6 月更新：Anyscale Endpoints（Anyscale 的 LLM API 服务）与 Private Endpoints（自托管 LLM）现已作为 Anyscale Platform 的一部分提供。点击[这里](https://console.anyscale.com/?utm_source=anyscale&utm_medium=blog&utm_campaign=blog_callout&utm_content=june2024_product_update_subheading)在 Anyscale 平台上开始使用。

*本文是 Ray Summit 2023 精彩回顾系列的一部分，我们总结了近期这场 LLM 开发者大会中最激动人心的演讲。*

*免责声明：摘要由 AI 根据视频转录生成，并经过人工编辑。*

## 核心要点

Ray Serve 是面向在线推理的灵活高效计算系统，正在革新 AI 应用的构建与部署方式。在本文中，我们探讨 Ray Serve 如何应对 AI 应用部署中的常见挑战——模型微服务、大语言模型的兴起以及不断上涨的硬件成本。我们还将讨论 Ray Serve 的可观测性、spot 实例支持与自动扩缩容特性，这些让它成为构建生产 AI 应用的强大工具。

- Ray Serve 通过提供一个 Python 原生框架，帮助解决在线 AI 应用服务化中的常见问题：包含多个模型的复杂应用可以在单个 Python 程序中表达，从而便于快速迭代与部署。
- Ray Serve 正在回应的 2023 年趋势：

- 大语言模型（LLM）兴起——Ray Serve 增加了 [RayLLM](https://github.com/ray-project/ray-llm) 子项目等优化，以高效服务 LLM。
- 硬件成本上升——Ray Serve 增加了模型多路复用（model multiplexing）等优化，最大化硬件利用率。

- 迈向生产：Ray Serve 聚焦生产就绪性，包括稳定性、混沌测试、Ray dashboard 等可观测性功能，以及 Anyscale 等托管服务。
- 演示亮点：

- 用于可视化 Ray Serve 部署的 Anyscale 服务 UI
- 用于请求追踪的 CloudWatch 集成
- 用于指标与分析的 Grafana 仪表盘
- 支持 spot 实例以降低成本
- 根据负载动态伸缩资源的自动扩缩容

- 经过 2023 年生产环境的更多采用与锤炼，Ray Serve 已在 Ray 2.7 中正式 GA。

## 用 Ray Serve 构建生产级 AI 应用

人工智能（AI）与机器学习（ML）已成为各行各业的有机组成部分，驱动创新与效率。然而，为生产构建和部署 AI 应用可能是复杂且耗费资源的工作。强大的 AI 服务系统 Ray Serve 正为此而生。在本文中，我们将深入 Ray Serve 的世界，看它如何改变生产 AI 应用的格局。

## 构建生产级 AI 应用的挑战

要理解 Ray Serve 的意义，必须先认清 AI 开发者与组织在构建生产 AI 应用时面临的挑战：

- **模型微服务**：传统 AI 应用常采用模型微服务架构——每个模型作为独立服务运行，各有自己的 Docker 配置与 Kubernetes 部署。这种方式复杂且耗资源，让多个模型之间高效创新与共享资源变得困难。
- **大语言模型（LLM）的兴起**：GPT-3 及其变体等大语言模型的出现标志着 AI 的重大趋势。要释放 LLM 的潜力，AI 开发者需要灵活且可扩展的基础设施。
- **硬件成本上升**：随着 AI 模型复杂度增长，硬件尤其是 GPU 的成本大幅上涨。高效利用和管理这些资源是成本控制的重中之重。

## Ray Serve 介绍

Ray Serve 是 AI 应用部署领域的变革者，为构建生产 AI 应用提供灵活、可扩展且高效的方式。看它如何回应上述挑战：

- **化繁为简的模型微服务：** Ray Serve 让开发者把复杂应用表达为单个 Python 程序。这意味着你可以把业务逻辑与多个模型混合在一起，从本地测试到生产部署快速迭代。Ray Serve 的 Python 原生特性简化了应用架构，降低了为每个模型维护独立微服务的复杂度。
- **拥抱大语言模型：** 针对 LLM 的兴起，Ray Serve 引入了专门服务 LLM 的基础设施。这套优化后的基础设施可与 VLLM、NVIDIA TensorRT 等最先进方案集成，确保 AI 应用高效利用 LLM。
- **应对硬件成本：** Ray Serve 提供高级特性优化资源分配与伸缩。它支持模型多路复用，让大量模型在同一硬件上并发运行。在 GPU 日益紧俏、硬件成本攀升的环境下，这一能力尤为关键。此外，Ray Serve 支持 spot 实例，让你在不牺牲服务可用性的前提下利用高性价比的云资源。

## 节省与成功案例

真实案例彰显了 Ray Serve 应对这些挑战的成效。Ray Serve 用户 Samsara 将 AI 平台迁移到 Ray Serve 后，年度推理成本降低了 50%。多家金融机构正借助 Ray Serve 运行大规模 GPU 集群，以远低于竞品方案的成本提供最先进的模型。

## 紧跟趋势

AI 领域瞬息万变，新模型与新技术不断涌现。组织必须快速适应才能保持竞争力。Ray Serve 的灵活性与开发者效率使它跟得上这些趋势：它陆续推出了流式响应、连续批处理（continuous batching）和张量并行等特性，与领域最新进展保持同步，确保企业能迅速集成 AI 新发展的成果并从中获益。

## 生产就绪性

2023 年是 AI 的变革之年，许多公司正从构想阶段走向 ML 的生产应用。要完成这一转变，稳健的部署与可观测性系统不可或缺。Ray Serve 着力提升生产就绪性，引入了 Ray dashboard 上的 Serve 页签、改进的指标与日志等可观测性功能。持续的混沌与规模测试保障了稳定性，在问题影响用户之前就把它们揪出来。

## Ray Serve 实战——拍照计算器应用

演示以一个拍照计算器应用展示 Ray Serve：它体现了各 deployment 独立扩缩、应对流量突发，以及依据不同硬件需求优化资源使用的能力。

## 可观测性带来深入洞察

Ray Serve 的可观测性功能让你看清请求如何在应用中流转、每个 deployment 的延迟以及关键组件的健康状况。这种程度的可见性让管理者做出明智决策并高效排障。

## Spot 实例实现成本效率

Ray Serve 引入对 spot 实例的支持，让用户利用高性价比云资源。当 spot 实例被回收时，Ray Serve 会将流量平稳切换到按需节点，待 spot 实例可用时再自动切回。这一省钱策略确保 AI 应用保持成本高效。

## 自动扩缩容应对流量洪峰

流量模式会波动，应用必须随之适应。Ray Serve 的自动扩缩容能力可以根据用户需求动态调整副本数与节点数。正如演示所见，在流量洪峰期间，这带来了吞吐上升与延迟下降。

## 结语

构建生产级 AI 应用可能困难重重，但 Ray Serve 以灵活高效的基础设施简化了这一过程。它回应了模型微服务、大语言模型兴起和硬件成本上涨带来的挑战。凭借可观测性、spot 实例支持与自动扩缩容，Ray Serve 让组织既能交付成本高效的 AI 方案，也能跟上不断变化的 AI 趋势。随着 AI 版图持续演进，对于要在生产环境中释放 AI 潜力的组织，Ray Serve 始终是强大工具。

欢迎了解 [Ray Serve](https://ray.io/serve)，立即注册 [Anyscale endpoints](https://www.anyscale.com/endpoints?utm_source=anyscale&utm_campaign=ray-highlights-2023-blog)快速上手，或[联系销售](https://www.anyscale.com/signup?utm_source=anyscale&utm_campaign=ray-highlights-2023-blog)获取 Anyscale 平台的全面介绍。
