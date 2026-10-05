---
vendor: modular_cloud
title: Modular 携手 AMD：在 AMD GPU 上释放 AI 性能
original_title: "Modular: Modular + AMD: Unleashing AI performance on AMD GPUs"
url: https://www.modular.com/blog/modular-x-amd-unleashing-ai-performance-on-amd-gpus
date: 2025-06-10
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Modular + AMD：在 AMD GPU 上释放 AI 性能

[Modular 很高兴宣布与](https://youtube.com/live/tBlNAIlMou8?feature=share)[Advanced Micro Devices, Inc](https://www.amd.com/en.html).（AMD）建立合作关系，AMD 是全球领先的 AI 半导体公司之一。我们将把 [Modular Platform](https://docs.modular.com/) 的优势带到 AMD GPU 上，为当今及未来最严苛的 AI 工作负载提供优化的基础设施方案。

> "我们身处真正的 AI 黄金时代，AMD 自豪地为下一代大规模推理与训练工作负载提供世界级的算力……我们也深知，仅有出色的硬件并不够。我们在开放软件 ROCm 上投入颇深，为开发者和研究人员提供在 AMD 上构建、优化和扩展 AI 系统所需的工具。这正是我们对与 Modular 的合作感到兴奋的原因……我们非常高兴能帮助开发者和研究人员构建 AI 的未来。" —— Vamsi Boppana，AMD AI 部门高级副总裁

这次合作标志着 Modular Platform 在 AMD 整个 GPU 产品线上正式可用（GA），这是异构 AI 计算基础设施的一座重要里程碑。即日起，开发者就可以在 AMD 旗舰数据中心加速器（包括 MI300 和 MI325 系列）上部署 Modular Platform。

由 MAX 推理服务器和 [Mojo 编程语言](https://www.modular.com/mojo)驱动的 Modular Platform，为 AMD 硬件带来了前所未有的性能优化。在与现有开源 AI 基础设施栈的严格基准对比中，我们展现出更优的推理效率：在 Llama 3.1、Gemma 3、Mistral 及其他业界领先语言模型的 prefill 密集型 `BF16` 工作负载上，吞吐量最多提升 53%——[全部来自一个可跨 NVIDIA 和 AMD GPU 扩展的容器](https://hub.docker.com/r/modular/max-full)。

对于 decode 密集型 `BF16` 工作负载，相比现有 AI 基础设施栈，我们展现出最多 32% 的吞吐量提升。

这些突破归功于 Modular Platform——业界第一个真正硬件无关的 AI 基础设施栈。它提供一个统一平台，无需修改一行代码即可在多样的硬件架构上无缝部署。

‍

> 开发者现在可以构建可在任何平台上运行的高性能、可移植 GenAI 部署。

‍

企业终于获得了真正的硬件选择自由——同时优化性能与总拥有成本（TCO）。与 NVIDIA H200 上的 vLLM 相比，AMD MI325 上的 MAX 模型在 ShareGPT 上的吞吐量持平或更优。

这种可选择性得益于 Mojo 🔥——一门 Python 家族语言，从底层设计起就能轻松在各种硬件上释放最佳性能。与主要面向 CPU 的大多数编程语言不同，Mojo 为 GPU 及其他加速器的异构计算新时代而生。凭借强静态类型、编译期元编程和无缝硬件调度等特性，Mojo kernel 写起来更快、维护更容易，并且可以在最新的硬件加速器之间移植。例如，Mojo kernel 库中 `BF16` 的 `matmul` 实现，在 MI300X 上性能超越等效的手工调优 kernel，同时保持了对其他硬件的可移植性。

Mojo Matmul 在 MI300X 上使用 BF16 的 GFLOPS 性能

最后，随着今天 [Mammoth 的预览版发布](https://www.modular.com/blog/introducing-mammoth-enterprise-scale-genai-deployments-made-simple)，我们把硬件选择权进一步扩展——Mammoth 是我们专为大规模、架构无关推理打造的 Kubernetes 原生编排器。Mammoth 在数千张异构 GPU 的集群上提供卓越的性能与运维简洁性，[让 AI 基础设施可扩展、高效且面向未来](https://docs.modular.com/mammoth)。

要在 AMD GPU 上充分发挥 Modular Platform 的全部威力，请[下载我们的 nightly](https://docs.modular.com/max/get-started)构建或拉取我们的 [Docker 容器](https://hub.docker.com/r/modular/max-amd)。为了帮你今天就能上手，Modular 已与 [TensorWave](https://tensorwave.com) 合作，提供免费的高性能 AMD 数据中心 GPU 使用权——访问 [modular.com/tensorwave](http://modular.com/tensorwave) 即可。我们迫不及待想看到你的构建！
