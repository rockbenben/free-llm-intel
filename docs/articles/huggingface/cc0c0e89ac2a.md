---
vendor: huggingface
title: Swift 🧨Diffusers：为 Mac 打造的快速 Stable Diffusion
original_title: Swift 🧨Diffusers
url: https://huggingface.co/blog/fast-mac-diffusers
date: 2023-02-24
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Swift 🧨Diffusers：为 Mac 打造的快速 Stable Diffusion

用 Diffusers for Mac 轻松把你的文字变成惊艳的图片——这是一款由最先进扩散模型驱动的原生应用。它利用了社区贡献到 Hugging Face Hub 上的一批 SoTA Text-to-Image 模型，并将它们转换为 Core ML 以获得极快的性能。最新的 1.1 版现已登陆 [Mac App Store](https://apps.apple.com/app/diffusers/id1666309574)，带来了显著的性能升级和更易用的界面调整，为后续功能更新打下了坚实基础。此外，该应用完全开源且采用宽松[许可证](https://github.com/huggingface/swift-coreml-diffusers/blob/main/LICENSE)，你也可以在它之上继续构建！更多信息请关注我们的 GitHub 仓库 [https://github.com/huggingface/swift-coreml-diffusers](https://github.com/huggingface/swift-coreml-diffusers)。

## 🧨Diffusers for Mac 到底是什么？

Diffusers 应用（[App Store](https://apps.apple.com/app/diffusers/id1666309574)，[源代码](https://github.com/huggingface/swift-coreml-diffusers)）是我们的 [🧨`diffusers` 库](https://github.com/huggingface/diffusers)的 Mac 对应版本。这个库用 Python 和 PyTorch 编写，采用模块化设计来训练和运行扩散模型。它支持许多不同的模型和任务，高度可配置且优化良好。它也能在 Mac 上运行，使用 PyTorch 的 [`mps` 加速器](https://huggingface.co/docs/diffusers/optimization/mps)——在 Apple Silicon 上它是 `cuda` 的替代方案。

那为什么要运行一个 Mac 原生应用呢？原因有很多：

- 它使用 Core ML 模型，而非原始的 PyTorch 模型。这很重要，因为 Core ML 允许针对 Apple 硬件特性做[额外优化](https://machinelearning.apple.com/research/stable-diffusion-coreml-apple-silicon)，而且 Core ML 模型可以在系统中的所有计算设备上运行：CPU、GPU 和神经引擎——*同时*——Core ML 框架会决定把模型的哪些部分放到哪个设备上以获得最快速度。PyTorch 的 `mps` 设备无法使用神经引擎。
- 它是一个 Mac 应用！我们遵循 Apple 的设计语言和指南，让它在你的 Mac 上浑然一体。无需使用命令行、创建虚拟环境或修复依赖。
- 它是本地且私密的。你不需要在线服务的额度，也不会排长队——想生成多少图就生成多少图，用于娱乐或工作。隐私有保证：你的 prompts 和图片归你所有，绝不会离开你的电脑（除非你主动分享）。
- [它是开源的](https://github.com/huggingface/swift-coreml-diffusers)，使用 Swift、Swift UI 以及 Mac 和 iOS 开发的最新语言与技术。如果你有技术背景，可以用 Xcode 按需扩展代码。我们也欢迎你的贡献！

## 性能基准

**TL;DR：** 取决于你的电脑，Diffusers 1.1 上的 Text-to-Image 生成最快可**提速一倍**。⚡️

我们在多台 Mac 上做了大量测试，以确定性能最优的计算设备组合。有些电脑用 GPU 最好，而另一些在启用神经引擎（ANE）时表现更好。

来看看我们的基准。所有组合都在 CPU 之外附加使用 GPU 或 ANE 之一。

| Model name | Benchmark | M1 8 GB | M1 16 GB | M2 24 GB | M1 Max 64 GB |
| --- | --- | --- | --- | --- | --- |
| Cores (performance/GPU/ANE) |  | 4/8/16 | 4/8/16 | 4/8/16 | 8/32/16 |
| Stable Diffusion 1.5 |  |  |  |  |  |
|  | GPU | 32.9 | 32.8 | 21.9 | 9 |
|  | ANE | 18.8 | 18.7 | 13.1 | 20.4 |
| Stable Diffusion 2 Base |  |  |  |  |  |
|  | GPU | 30.2 | 30.2 | 19.4 | 8.3 |
|  | ANE | 14.5 | 14.4 | 10.5 | 15.3 |
| Stable Diffusion 2.1 Base |  |  |  |  |  |
|  | GPU | 29.6 | 29.4 | 19.5 | 8.3 |
|  | ANE | 14.3 | 14.3 | 10.5 | 15.3 |
| OFA-Sys/small-stable-diffusion-v0 |  |  |  |  |  |
|  | GPU | 22.1 | 22.5 | 14.5 | 6.3 |
|  | ANE | 12.3 | 12.7 | 9.1 | 13.2 |

我们发现内存大小对性能影响似乎不大，但 CPU 与 GPU 核心数量影响显著。例如，在 M1 Max 笔记本上，GPU 生成比 ANE 快得多。这很可能是因为它拥有标准 M1 处理器 4 倍的 GPU 核心数（以及 2 倍的 CPU 性能核），而神经引擎核心数相同。反过来，Mac Mini 上搭载的标准 M1 处理器用 ANE 比 GPU **快一倍**。有趣的是，我们还测试了同时使用 GPU 和 ANE *两者*，发现相比只用其中较优者并不提升性能。分界点似乎大致在 M1 Pro 芯片的硬件特征（8 个性能核、14 或 16 个 GPU 核）附近，而我们目前没有该芯片可供测试。

🧨Diffusers 1.1 会根据应用运行的电脑自动选择最佳加速器。某些设备配置（如 "Pro" 变体）我们已知的云服务并不提供，因此针对它们的启发式规则仍有改进空间。如果你想帮助我们收集数据、持续改进应用的原生体验，请继续读下去！

## 社区基准数据征集

我们希望在 Mac 设备上开展更全面的性能基准。如果你想帮忙，我们创建了[这个 GitHub issue](https://github.com/huggingface/swift-coreml-diffusers/issues/31)，你可以在那里发布结果。我们将用它们优化应用下一个版本的性能。我们尤其关注 M1 Pro、M2 Pro 和 M2 Max 架构 🤗

## 1.1 版的其他改进

除性能优化和一些 bug 修复外，我们还专注于在保持 UI 尽可能简洁清爽的前提下新增功能。其中大部分显而易见（guidance scale、可选关闭安全检查器、允许取消生成）。我们最喜欢的是模型下载进度指示，以及一个快捷方式：复用上一次生成的 seed 来微调生成参数。

1.1 版还新增了关于各项生成设置作用的说明。我们希望 🧨Diffusers for Mac 让图像生成对所有 Mac 用户——而不仅是技术人员——都尽可能触手可及。

## 下一步

我们认为苹果生态在图像生成方面还有大量未被挖掘的潜力。在未来的更新中，我们想专注于：

- 便捷访问 Hub 上的更多模型。以 Mac 风格的方式，在应用里运行任意 Dreambooth 或微调模型。
- 发布 iOS 和 iPadOS 版本。

我们还在考虑更多想法。如果你有自己的建议，非常欢迎到 [GitHub 仓库](https://github.com/huggingface/swift-coreml-diffusers)提出。
