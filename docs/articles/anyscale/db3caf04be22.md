---
vendor: anyscale
title: Anyscale 签署最终协议，加入 Nscale
original_title: Anyscale signs definitive agreement to join Nscale
url: https://anyscale.com/blog/anyscale-signs-definitive-agreement-to-join-nscale
date: 2026-07-30
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Anyscale 签署最终协议，加入 Nscale

作者：Robert Nishihara、Philipp Moritz、Ion Stoica、Richard Liaw 和 Edward Oakes | 2026 年 7 月 30 日

这意味着什么：

- **加倍投入 Ray。** 我们将扩大对 Ray 与开源社区的投入。双方携手，直接针对最先进加速器与数据中心架构优化 Ray。
- **开源战略。** 在 PyTorch Foundation 治理下，来自 Google、NVIDIA、Microsoft 与社区的贡献持续增长。Nscale 计划以白金会员身份加入该基金会。开源是 Nscale 战略的核心，也同样是我们的核心。
- **更多 GPU 容量。** Anyscale Platform 客户将获得 Nscale 的大量算力容量。
- **多云灵活性。** 交易完成后，Anyscale Platform 将继续在所有主流云服务商上运行。可移植性仍是 Ray 与 Anyscale Platform 路线图的核心。

## 瓶颈如今横跨整个技术栈

当我们在 UC Berkeley 创建 Ray 并创办 Anyscale 时，我们相信 AI 计算需求会爆发。第一个瓶颈是分布式计算的软件，我们构建了 Ray 来解决它。

这个赌注赢了。Ray 如今被用于所有主要 AI 负载——从数据准备到训练再到推理——并被用来构建多个前沿模型家族，包括 GLM、Nemotron、Composer 和 MAI。

但 AI 系统的规模与复杂度已增长了数量级。数据处理正变得多模态、重推理、[基于 GPU](https://www.anyscale.com/blog/data-processing-becoming-gpu-workload)。强化学习把训练、推理与仿真混在同一个负载里。推理需要分离式架构、面向超长上下文的 GPU 显存管理，以及 mixture-of-experts 架构的复杂路由与故障处理。

这些挑战与硬件不可分割。软件必须在每一层、每个组件上考虑机架与集群拓扑、容量、硬件异构性、计算分离以及故障。逐层独立优化已经不够了。未来需要在软硬件栈每一层之间做深度的联合优化。

## 为什么是 Nscale

在众多 neocloud 中，Nscale 以其执行速度和对完整垂直整合的愿景脱颖而出。

Nscale 深耕物理基础设施的更多环节，从土地与电力到数据中心和加速计算。其多吉瓦（multi-gigawatt）管线直击 AI 最大的约束之一，为我们提供算力可得性与密度，也为联合优化提供更紧的反馈回路。此外，Nscale 是最早规模化部署下一代 GB300 NVL72 系统的公司之一。在物理基础设施之外，Nscale 还为大规模推理构建了高性能平台软件，立即加速我们合并后的路线图。

与 Anyscale 相似，Nscale 也把开源作为战略押注，相信胜出的 AI 基础设施标准将是开放的。他们计划以白金会员身份加入 PyTorch Foundation，并大力投资开源生态。

Anyscale 与 Nscale 联手，可以共同设计软件层与其下的基础设施——这是任何一家公司只优化自己那一层都做不到的。

## 对开源与多云的承诺

Ray 从第一天起就是开放的、社区驱动的项目，与 PyTorch 和 vLLM 一起由 PyTorch Foundation 治理。它作为行业标准的价值，取决于它完全开放、中立且可移植。

正是这种开放性，让全行业公司都投资 Ray。过去一年，来自 Google、NVIDIA、Microsoft、Red Hat、Alibaba 以及更广泛 Ray 社区的工程师，改进了最新一代 GPU 与 TPU 支持、拓扑感知调度、GPU 原生数据处理、Kubernetes 集成与 Ray History Server。未来，Anyscale + Nscale 团队将大力投入 Ray 的维护与改进。我们会继续壮大社区、辅导贡献者，并寻求扩大项目治理。

Ray 一直与[开放 AI 基础设施栈](https://www.anyscale.com/blog/ai-compute-open-source-stack-kubernetes-ray-pytorch-vllm)的其他组件共同演化。现在我们正把这种协同设计延伸到更深的硬件层。

可移植性是硬性要求。Ray 被设计为支持任何硬件加速器、集成任何 ML 框架、运行在任何环境——包括你的笔记本、本地机房和任何云服务商。这一理念在 Ray 与 Anyscale Platform 上均保持不变。

## 展望未来

这是一个关键的增长期，刚过去的季度是我们迄今最强的季度，营收环比增长超过 70%。我们才刚开始。

我们将与 Nscale 一起，让分布式 AI 基础设施更简单、更可靠、更高效，同时加倍坚守成就了 Ray 的开放性与可移植性——它已是 AI 生态的基础组成部分。

今年 8 月，我们在旧金山的 [Ray Summit](https://www.anyscale.com/ray-summit/2026) 上会分享更多。交易完成后，合并团队也将开放[招聘](https://www.anyscale.com/careers)！
