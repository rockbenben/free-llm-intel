---
vendor: huggingface
title: Safetensors 加入 PyTorch Foundation
original_title: Safetensors is Joining the PyTorch Foundation
url: https://huggingface.co/blog/safetensors-joins-pytorch-foundation
date: 2026-05-12
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Safetensors 加入 PyTorch Foundation

今天我们要宣布：Safetensors 已加入 PyTorch Foundation，成为 Linux Foundation 旗下由基金会托管的项目，与 DeepSpeed、Helion、Ray、vLLM 以及 PyTorch 本身并肩。

## 我们如何走到这一步

Safetensors 诞生于 Hugging Face 的一个具体需求：一种不能执行任意代码的模型权重存储与分享方式。当时主导生态的基于 pickle 的格式意味着，你很可能在运行恶意代码，这是真实存在的风险。在机器学习尚处萌芽期时，这或许是可以接受的风险；但当开源模型分享成为 ML 社区运转的核心方式后，它就变得不可接受了。

我们构建的这个格式刻意保持简单：一个带 100MB 硬上限的 JSON header，描述 tensor 元数据，后面跟原始 tensor 数据。零拷贝（zero-copy）加载，让 tensor 直接从磁盘映射。惰性（lazy）加载，让你无需反序列化整个 checkpoint 就能读取单个权重。

我们没有完全预料到它会被如此广泛地采用。如今，Safetensors 是 Hugging Face Hub 及其他平台上模型分发的默认格式，被 ML 中所有模态的数万个模型使用。它已成为开源 ML 社区分享模型的首选方式。

## 为什么选择 PyTorch Foundation

我们希望 Safetensors 真正属于社区。这个项目一直是开源的，但代码贡献只是其演进的一部分。通过让更多公司和贡献者参与项目治理，我们确保项目的进步能反映在其之上构建的社区的广度。加入 PyTorch Foundation 意味着 Safetensors 现在有了一个厂商中立的家。商标、仓库和项目治理都归属于 Linux Foundation，而非任何单一公司。Hugging Face 的两位核心维护者 Luc 和 Daniel 仍留在技术指导委员会（Technical Steering Committee）中，继续负责项目的日常工作，但 Safetensors 现在正式属于依赖它的社区。

我们相信：当每位贡献者都能在已有的基础上构建时，安全性才能得到最好的保障——这一原则如今已写入项目自身的治理结构。

## 对用户和贡献者意味着什么

对绝大多数用户来说，什么都没变。格式相同、API 相同、Hub 集成相同：没有破坏性变更。今天以 Safetensors 格式存储的模型将继续像现在一样工作。

对贡献者来说，成为维护者的路径现在有了正式文档，并向社区中的任何人开放。项目的治理规则位于仓库中的 GOVERNANCE.md 和 MAINTAINERS.md。对于在 Safetensors 之上构建的组织，Linux Foundation 下的中立治理提供了一个稳定、长期、完全由社区驱动的底座。

## 未来会怎样

Safetensors 是一个已被整个生态采用的成熟项目，但我们仍然坚信项目正处于起点。

**我们正在与 PyTorch 团队合作，让 Safetensors 有望在 PyTorch 核心中作为 torch 模型的序列化系统使用。**

未来几个月将迎来显著增长，而没有什么比 PyTorch Foundation 更适合承载这一新篇章。接下来的路线图包括感知设备的加载与保存（device-aware loading and saving），让 tensor 可以直接加载到 CUDA、ROCm 和其他加速器上，无需不必要的 CPU 中转。

我们还在构建 Tensor Parallel 与 Pipeline Parallel 加载的一流 API，让每个 rank 或流水线阶段只加载自己需要的权重。随着生态中量化版图持续演化，我们将正式化对 FP8、GPTQ 和 AWQ 等块量化格式（block-quantized formats）以及亚字节整数类型（sub-byte integer types）的支持。

这些问题关乎整个生态的利益，而身处 PyTorch Foundation 内部，意味着我们可以与其他托管项目协作解决它们，而不是各自并行摸索。

## 参与进来

Safetensors 是开源项目，欢迎各个层面的贡献——从 bug 报告、文档，到新功能、参与治理。

- **GitHub：** [github.com/huggingface/safetensors](https://github.com/huggingface/safetensors)
- **文档：** [huggingface.co/docs/safetensors](https://huggingface.co/docs/safetensors)
- **PyTorch Foundation：** [pytorch.org/foundation](https://pytorch.org/foundation)

如果你是构建在 Safetensors 之上的开发者、研究者或组织，并希望更多地参与塑造它的方向，欢迎提 issue、发起讨论，或直接联系维护者。这个项目一直属于使用它的社区，如今治理结构也体现了这一点。
