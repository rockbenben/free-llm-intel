---
vendor: modular_cloud
title: CUDA 是如何成功的？（AI 算力普惠化，第 3 部分）
original_title: "Modular: How did CUDA succeed? (Democratizing AI Compute, Part 3)"
url: https://www.modular.com/blog/democratizing-ai-compute-part-3-how-did-cuda-succeed
date: 2025-02-12
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# CUDA 是如何成功的？（AI 算力普惠化，第 3 部分）

如果我们这个生态希望取得进展，就必须理解**CUDA 软件帝国**是如何变得如此主导的。纸面上看，替代方案是存在的——AMD 的 ROCm、Intel 的 oneAPI、基于 SYCL 的框架——但在实践中，CUDA 依然是**GPU 计算无可争议的王者**。

**这是怎么发生的？**

答案不仅仅是**技术卓越**——虽然那确实起作用。CUDA 是一个开发者平台，它建立在**卓越的执行、深层的战略投入、连续性、生态锁定**之上，当然，还有那么一点**运气**。

本文拆解**为什么 CUDA 如此成功**，逐层审视 NVIDIA 的战略——从早期对通用并行计算的押注，到与 [PyTorch](https://pytorch.org/) 和 [TensorFlow](http://tensorflow.org/) 等 AI 框架的紧密耦合。归根结底，CUDA 的统治地位不只是软件的胜利，更是一堂**长期平台思维的典范课**。

我们开始吧。🚀

## CUDA 的早期增长

构建一个计算平台的关键挑战，是吸引开发者去学习并投入它，而如果你只能瞄准小众硬件，**就很难获得势能**。在[一期很棒的 "Acquired" 播客](https://www.acquired.fm/episodes/jensen-huang)里，Jensen Huang 分享说，NVIDIA 早期一个关键战略是保持 GPU 跨代兼容。这让 NVIDIA 能够利用它已有的、极其普及的**游戏 GPU** 装机量——这些 GPU 原本是为运行基于 DirectX 的 PC 游戏而卖出的。此外，它还让开发者能在低价的桌面 PC 上学习 CUDA，再扩展到更昂贵、更强的高端硬件。

这现在看起来也许显而易见，但在当时是个大胆的赌注：NVIDIA 没有为不同用例（笔记本、桌面、物联网、数据中心等）创建各自优化的独立产品线，而是构建了**单一连续的 GPU 产品线**。这意味着接受一些取舍——比如功耗或成本上的低效——但作为回报，它创造了一个**统一生态**，每个开发者对 CUDA 的投入都能从游戏 GPU 无缝扩展到高性能数据中心加速器。这个战略与 Apple 维护并推进其 iPhone 产品线的方式颇为类似。

这种做法的好处有两层：

- **降低进入门槛**——开发者可以用他们已有的 GPU 学习 CUDA，让实验和采纳变得容易。
- **创造网络效应**——随着更多开发者开始使用 CUDA，更多软件和库被创造出来，使这个平台更有价值。

这批早期的装机量让 CUDA 从游戏增长到**科学计算、金融、AI 和高性能计算（HPC）**。一旦 CUDA 在这些领域获得牵引，它相对替代方案的优势就显而易见了：**NVIDIA 的持续投入确保 CUDA 始终站在 GPU 性能的最前沿**，而竞争对手则苦于无法建立可比的生态。

## 抓住并骑上 AI 软件的浪潮

CUDA 的统治地位因**深度学习的爆发**而彻底稳固。2012 年，**AlexNet**——那张**点燃现代 AI 革命的神经网络**——是用两块 NVIDIA GeForce GTX 580 GPU 训练出来的。这一突破不仅证明了**GPU 在深度学习上更快**——它证明了 GPU 对 AI 进步不可或缺，并导致 **CUDA 被迅速采纳为深度学习的默认计算后端**。

随着深度学习框架涌现——最著名的是 **TensorFlow**（Google，2015）和 **PyTorch**（Meta，2016）——NVIDIA **抓住了机会**，大力投入优化其**高层 CUDA 库**，以确保这些框架在它的硬件上尽可能高效地运行。NVIDIA 没有把**底层 CUDA 性能调优**留给 **AI 框架团队**自己去处理，而是像我们在[第 2 部分](https://www.modular.com/blog/democratizing-compute-part-2-what-exactly-is-cuda)讨论的那样，积极打磨 **cuDNN** 和 **TensorRT**，把这份负担揽到自己身上。

这一举措不仅让 **PyTorch 和 TensorFlow 在 NVIDIA GPU 上显著更快**——它还让 NVIDIA 得以**紧密整合自己的硬件与软件**（一个被称为"[硬件/软件协同设计](https://towardsdatascience.com/how-to-co-design-software-hardware-architecture-for-ai-ml-in-a-new-era-b296f2842fe2/)"的过程），因为它减少了与 Google 和 Meta 的协调。硬件的每一次大更新，都会带来一版**新的 CUDA**，**利用硬件的新能力**。渴望速度与效率的 AI 社区非常乐意**把这份责任委托给 NVIDIA**——这直接导致这些框架被**绑定到 NVIDIA 硬件上**。

但为什么 Google 和 Meta 放任这一切发生？现实是，**Google 和 Meta** 并非一心要构建一个广泛的 AI 硬件生态——他们专注于用 AI 来**驱动收入、改进产品、解锁新研究**。他们的顶尖工程师优先考虑**高影响力的内部项目**以推动公司内部指标。例如，这些公司[**决定**自己造](https://thechipletter.substack.com/p/googles-first-tensor-processing-unit)[**专有 TPU 芯片**](https://cloud.google.com/transform/ai-specialized-chips-tpu-history-gen-ai)——把精力倾注在优化自己的[第一方硬件](https://ai.meta.com/blog/next-generation-meta-training-inference-accelerator-AI-MTIA/)上。对 GPU，**把缰绳交给 NVIDIA** 是合理的。

替代硬件的厂商面对的是**一场苦战**——在没有同等程度硬件聚焦的情况下，试图**复刻庞大、不断扩张的 NVIDIA CUDA 库生态**。竞争的硬件厂商不只是艰难——他们**被困在一个无尽的循环里**，永远在 NVIDIA 硬件上追赶下一个 AI 进展。这也影响了 Google 和 Meta 的**自研芯片项目**，催生了包括 XLA 和 PyTorch 2 在内的众多项目。我们可以在后续文章里深挖这些，但[尽管曾有一些期望](https://semianalysis.com/2023-01-16/nvidiaopenaitritonpytorch/)，今天我们可以看到，没有什么能让硬件创新者匹敌 CUDA 平台的能力。

随着硬件每一代的更替，**NVIDIA 拉大了差距**。然后突然地，2022 年末，ChatGPT 横空出世，随之，**GenAI 和 GPU 计算走向主流**。

## 借助生成式 AI 的激增获利

几乎一夜之间，**对 AI 算力的需求**飙升——它成为**千亿美元产业**、消费级应用和企业竞争战略的基础。**大型科技公司**和风险投资机构向 AI 研究初创公司[注入了数十亿美元](https://techcrunch.com/2025-01-03/generative-ai-funding-reached-new-heights-in-2024/)和[资本开支扩建](https://www.thestreet.com/investing/nvidia-first-in-line-to-reap-gains-from-massive-big-tech-spending-surge)——这些钱最终径直流向 NVIDIA，唯一能满足**爆炸式算力需求**的玩家。

随着 AI 算力需求激增，企业面临一个残酷现实：**训练和部署 GenAI 模型[极其昂贵](https://epoch.ai/blog/how-much-does-it-cost-to-train-frontier-ai-models)**。每一个效率提升——无论多小——在规模下都转化为巨大的节省。由于 **NVIDIA 的硬件早已扎根数据中心**，AI 公司面临一个严肃选择：**为 CUDA 优化，或者落后**。几乎一夜之间，业界转向编写 **CUDA 专用代码**。结果呢？AI 突破不再纯粹由模型和算法驱动——它们如今**取决于从 CUDA 优化代码中榨取最后一滴效率的能力**。

以 [**FlashAttention-3**](https://pytorch.org/blog/flashattention-3/) 为例：这种前沿优化大幅削减了**运行 transformer 模型的成本**——但它专为 **Hopper GPU** 构建，通过确保**最佳性能**只在其最新硬件上可用，强化了 **NVIDIA 的锁定**。**持续的研究创新**沿袭了同样的轨迹，例如当 [**DeepSeek 直接转向 PTX 汇编**](https://www.tomshardware.com/tech-industry/artificial-intelligence/deepseeks-ai-breakthrough-bypasses-industry-standard-cuda-uses-assembly-like-ptx-programming-instead)，在**尽可能低的层面**获得了[对硬件的完全掌控](https://medium.com/@amin32846/unlock-warp-level-performance-deepseeks-practical-techniques-for-specialized-gpu-tasks-a6cf0c68a178)。随着新的 [NVIDIA Blackwell](https://nvidianews.nvidia.com/news/nvidia-blackwell-platform-arrives-to-power-a-new-era-of-computing) 架构即将到来，我们可以预期业界会**再次从零重写一切**。

## 强化 CUDA 掌控力的自增强循环

这套系统在加速，并且**自我强化**。**生成式 AI 已成一股失控的力量**，驱动着对算力的贪求，而 **NVIDIA 握着所有的牌**。最大的**装机量**确保**大多数 AI 研究**在 **CUDA** 上进行，而这反过来**驱动了优化 NVIDIA 平台的投入**。

NVIDIA 硬件的每一代都带来**新特性和新效率**，但它也要求**新的软件重写、新的优化，以及对 NVIDIA 技术栈更深的依赖**。未来看似不可避免：一个 CUDA 对 AI 算力的掌控只会更紧的世界。

#### 只是 CUDA 并不完美。

那些**巩固** CUDA 统治地位的力量，也在变成一个瓶颈——技术挑战、低效，以及**更广泛创新的障碍**。这种统治真的服务于 **AI 研究社区**吗？CUDA 是**对开发者好**，还是只是**对 NVIDIA 好**？

让我们退后一步：我们审视了 [**CUDA 是什么**](https://www.modular.com/blog/democratizing-compute-part-2-what-exactly-is-cuda)，以及它为何如此成功，但**它到底好不好用？**我们会在第 4 部分探讨这个——敬请期待，也告诉我们你觉得这个系列有没有用，或者有什么建议/请求！🚀

-Chris
