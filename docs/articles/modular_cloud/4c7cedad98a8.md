---
vendor: modular_cloud
title: Modular 26.1：迈向更可编程、更可移植 AI 基础设施的一大步
original_title: "Modular: Modular 26.1: A Big Step Towards More Programmable and Portable AI Infrastructure"
url: https://www.modular.com/blog/modular-26-1-a-big-step-towards-more-programmable-and-portable-ai-infrastructure
date: 2026-01-29
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Modular 26.1：迈向更可编程、更可移植 AI 基础设施的一大步

今天我们发布 Modular 26.1——让高性能 AI 计算在异构硬件上更易构建、调试和部署的一大步。本次发布聚焦于开发速度和可编程性，帮助顶尖 AI 团队缩短其最重要创新面市的时间。

Modular 26.1 的核心是全新的 MAX Python API，它简化了跨异构硬件构建和部署高性能 GenAI 模型的过程。本次发布还增强了 Mojo 内 API 的强度与人体工学，包含错误报告的新开发者体验改进、能在编译期捕获更多 bug 的语言特性，以及扩展的 Apple 芯片 GPU 支持。

### **26.1 发布亮点包括：**

- **MAX Python API 走出实验期** – 类 PyTorch 建模，调试用 eager 模式，生产用 `model.compile()`
- **MAX LLM Book 现已稳定** – 在 [llm.modular.com](https://llm.modular.com/) 从零构建 transformer
- **不断增长的社区贡献** – 来自外部贡献者的 Qwen3 embeddings、BERT、Mamba、视觉生成流水线等
- **Mojo API 与人体工学改进** – 包括编译期反射、线性类型、带类型的错误、更好的错误消息

# **用 MAX 更快地从原型到生产**

我们通常把 MAX 描述为一个 AI 建模与服务框架，为生产推理提供业界领先性能与成本效率。但 MAX 最有特色的优势之一是其可编程性与可扩展性，Modular 26.1 让这一点更加凸显。

MAX Python API 让移植自定义 GenAI 模型——通常用 PyTorch 训练——到能在多样硬件上运行的、高性能格式变得简单。26.1 中，eager 执行 API 正式走出实验期，提供类 PyTorch 的建模接口，并有更坚实的文档和不断壮大的开发者社区支撑。

结果是：MAX 不再只是更快地服务模型的方式——它是一个端到端构建和服务 GenAI 模型的平台，不牺牲性能、可移植性或控制权。

## **更自然的 Python 建模体验**

在 26.1 中，MAX 向让来自 PyTorch 的用户感到直观迈出一大步：

- **类 PyTorch 建模 API**不再处于实验阶段，同时保留 MAX 的可移植性与性能特性。详见[模型开发者指南](https://docs.modular.com/max/develop/)。
- **Eager 模式支持**降低了实验和交互式开发中的摩擦。这显著改善了开发者体验，让 MAX 在调试、实验和模型 bring-up 期间感觉自然得多。虽然我们仍在改进编译时间，本次发布切实缩小了 PyTorch 的 eager 体验与 MAX 性能优先执行模型之间的差距。查看[张量基础指南](https://docs.modular.com/max/develop/tensors)，并在[nightly 构建](https://docs.modular.com/max/packages#install)中获取最新性能改进。
- **只需调用 [`model.compile()`](https://docs.modular.com/max/api/python/nn/module#max.nn.module.Module.compile)** 即可为你的 MAX 模型编译上生产。你会获得前置图编译的全部好处，带来你期待自 MAX 图编译器及其高性能 GPU kernel 的全部速度与内存效率。

这些改进一起把 MAX 拉近到用户期待的"即插即用"体验，同时保留了当性能与效率最关键时无缝扩展到完全编译、生产级执行的能力。

## 用 MAX 构建 LLM 的动手指南

我们[从零构建 LLM 的全面指南](https://llm.modular.com/)（MAX LLM book）现已稳定，并与 nightly 构建中的 API 变更同步维护。如果你看过实验版，再看一眼——我们彻底更新了顺序，让每一步写的代码都建立在上一步之上，直到你用 MAX 构建出一个完全可运行的 OpenAI LLM。

MAX LLM Book 走遍 transformer 的每个组件——从分词、embedding 到注意力与解码——同时教你如何用 MAX Python API 表达这些想法。它面向两类读者：

- 想深入、具体理解 transformer 究竟如何工作的开发者。
- 需要为真实生产用例定制或扩展模型的实践者。

每一章都包含可执行代码与详细解释，既是学习资源也是实用参考。[现在开始构建](https://llm.modular.com/)。

## **扩展的 Apple Silicon GPU 支持**

延续 25.7 中我们的 Apple 芯片 GPU 初步支持，26.1 大幅扩展了覆盖。简单 MAX 图可以在 Apple 芯片 GPU 上编译运行，所有 [Mojo GPU puzzles](https://puzzles.modular.com/)现在都能运行在 Apple GPU 上（NVIDIA 专属谜题除外）。未来的更新会把支持一路扩展到 Apple Silicon GPU 上的 LLM 推理。如果你想参与构建这一支持，欢迎加入我们的社区。

最新特性定期落地在我们的 nightly 发布中，所以请关注它们以获得最好的支持。你也可以通过为我们现有的许多[开源 Mojo kernels](https://github.com/modular/modular/tree/main/max/kernels)贡献新的 Apple 芯片 GPU 支持来帮忙。

## **不断壮大的 MAX 模型社区**

过去几个月标志着 MAX 演进的一个转折点——从一个内部框架变成一个**社区成长的建模平台**。来自整个生态的贡献者正用新模型架构、性能改进和惠及所有人的基础设施增强来扩展 MAX。以下是几处亮点：

- 社区成员 Sören Brunk 贡献了[生产就绪的 Qwen3 embedding 支持](https://github.com/modular/modular/pull/5782)，包括追平 vLLM 吞吐的性能优化，以及改进 MAX 架构注册表、惠及未来所有多任务模型的基础设施增强。
- Ryan Wayne 添加了 [BERT embedding 模型支持](https://github.com/modular/modular/pull/5752)，专门为替换他依赖 CUDA 的文本 embeddings 基础设施，展示了 MAX 在简化生产 ML 栈上的吸引力。
- Tolga Cangoz 正在开发一个雄心勃勃的 Z-Image 视觉生成流水线，将为 MAX 带来业界领先的、基于扩散的图像生成。

Qwerky AI 团队正通过 Mamba 架构在 MAX 中探索状态空间模型。状态空间模型为传统 Transformer 架构提供了一种诱人的替代，承诺可能更快的推理和对远更长上下文窗口的支持。Qwerky AI 一直在做自定义 Mojo kernel、新模型架构和服务流水线增强，以在 MAX 中支持这些新式模型。

我们已经开源了 MAX Python API、整个 GPU kernel 库（面向 NVIDIA、AMD 和 Apple 芯片）、所有模型架构、服务流水线等等。如果你有兴趣贡献模型架构、性能优化或扩展 MAX 的能力，请查看我们的[贡献指南](https://github.com/modular/modular/blob/main/max/CONTRIBUTING.md)，并加入我们在 [MAX 论坛](https://forum.modular.com/c/max)上的讨论。

# **Mojo：更强大、更顺手的 API**

Mojo 26.1 交付了一系列基础语言特性，让语言切实[更接近](https://www.modular.com/blog/the-path-to-mojo-1-0)[**Mojo 1.0**](https://www.modular.com/blog/the-path-to-mojo-1-0)。我们对 1.0 的目标是提供一门能为多样硬件做高性能计算、但用起来依然愉悦的语言。

本次发布通过纳入编译期安全方向的语言设计研究成果、改善你遇到错误时的体验、增强 Mojo 代码的整体人体工学，推动我们朝那个目标前进。具体来说，本次发布新增了：

- **编译期反射：**一个新的[编译期反射](https://docs.modular.com/mojo/manual/reflection)系统，进一步强化 Mojo 已然多才多艺的元编程系统。这个强大新能力可实现（除其他外）自动遵循库中定义的 trait，例如：自动可比较性、JSON 序列化或命令行参数解析。Mojo 社区的成员已经用 nightly 构建以此做出令人兴奋的东西。
- **显式析构类型：**Mojo 现在支持[显式析构类型](https://docs.modular.com/mojo/manual/lifecycle/death/#implicit-and-explicit-destruction)（即编程语言术语里的"线性类型"），在编译期保证某些值无法被遗忘。这是 Mojo 借鉴前沿研究语言的一个例子，其安全与能力超越了多数其他广泛使用的语言。
- **带类型的错误：**函数现在可以抛出 Error 以外的类型，使 GPU 和嵌入式系统上的错误处理零开销。Mojo 还支持"参数化可抛出性"，让通用算法得以强大而简洁地表达。
- **改进的错误消息：**我们修复了 Mojo 错误消息中最大的用户痛点——以前它会抱怨无法推断某个参数，而不是说类型不匹配。当两个类型几乎相同时，Mojo 现在还会对相似类型做 diff，告诉你是哪个子参数不一致！
- **Mojo LSP 服务器改进：**LSP 用户会看到打字时 CPU 占用大幅下降，编译器实验性地支持应用 fix-it 建议。

一如既往，Mojo 及其工具链中有趣且有用的新增远不止上面列的这些，所以请查看完整的 [Mojo changelog](https://docs.modular.com/mojo/changelog)。

# **今天就试试 26.1**

用 pip、uv、pixi 或 conda 安装 `modular` 包，获得用 MAX 构建 LLM、用 Mojo 编写高性能 GPU kernel 所需的一切。更多细节见[我们的快速入门指南](https://docs.modular.com/max/get-started)。

shell

```
uv pip install modular
```

配置好后，你可以探索 **Modular Platform 26.1** 的一切：

- 跟着 [MAX LLM Book 课程](https://llm.modular.com/)从第一性原理构建一个 transformer 模型
- 在你的 **Apple 芯片** Mac 上运行 [GPU puzzles](https://puzzles.modular.com/)并构建 [MAX 模型](https://docs.modular.com/max/develop/)
- [在 Mojo 中](https://docs.modular.com/mojo/manual/quickstart)探索**线性类型**与**编译期反射**

完整拆解见 [MAX](https://docs.modular.com/max/changelog) 和 [Mojo](https://docs.modular.com/mojo/changelog/) 26.1 changelog。

Modular 26.1 是让高性能 AI 开发人人可及的又一步。你的问题、反馈和贡献直接塑造这个平台——加入我们在[论坛](https://forum.modular.com/)上的讨论，并[报告任何 issue 或功能请求](https://github.com/modular/modular/issues)。

我们迫不及待想看到你构建的东西！
