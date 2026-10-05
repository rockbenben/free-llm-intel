---
vendor: modular_cloud
title: Modverse #49：Modular 平台 25.4、Modular 🤝 AMD 与 Modular Hack Weekend
original_title: Modular: Modverse #49: Modular Platform 25.4, Modular 🤝 AMD, and Modular Hack Weekend
url: https://www.modular.com/blog/modverse-49
date: 2025-07-09
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Modverse #49：Modular 平台 25.4、Modular 🤝 AMD 与 Modular Hack Weekend

一场全球黑客松、一次重大发布、一批出色的社区项目——上个月 Modular 生态进展满满！

[Modular 平台 25.4 于 6 月 18 日发布](https://www.modular.com/blog/modular-25-4-one-container-amd-and-nvidia-gpus-no-lock-in?utm_source=modverse&utm_campaign=community)，同期宣布我们与 AMD 的正式合作，带来对 AMD Instinct™ MI300X 与 MI325X GPU 的完整支持。现在你可以在 AMD 与 NVIDIA 硬件上部署同一个容器——不改代码、没有厂商锁定、无需额外配置！

25.4 的亮点包括：在 Llama 3.1、Gemma 3、Mistral 等最先进语言模型的 prefill 密集型 BF16 负载上吞吐最高提升 53%。该版本还新增支持 AMD MI300/325、RDNA3/4 以及 NVIDIA RTX 2060–5090，并扩大了模型覆盖。

六月，来自世界各地的构建者还因 Modular Hack Weekend 汇聚一堂——开发者们做出的东西从快速傅里叶变换实现、GPU 加速量子模拟器，到高性能生物信息学库，五花八门。我们发布了 Mammoth——新的跨任意 GPU 扩展 GenAI 推理的系统，并推出把 Mojo kernel 直接嵌入 Python 工作流的新方式。社区推动了 kernel 设计的边界，探索了科学计算中的突破，并持续拓展 Mojo 与 MAX 的可能性。

来看看上个月 Modular 宇宙创造的一切。

# **博客、教程与视频**

- 来自 AI 与系统编程社区的开发者近期齐聚 **Modular Hack Weekend**：一场聚焦 GPU 编程与模型实现、使用 Mojo 与 MAX 的全球线上黑客松。为黑客松揭幕，我们举办了 [**GPU 编程工作坊**](https://www.youtube.com/watch?v=BBhZ9Ltpmdw)——在加州 Los Altos 办公室线下同步直播。查看全部演讲录像：[Chris Lattner 与 Tim Davis](https://www.youtube.com/watch?v=DqTBvi0DKgg)，Modular 联合创始人[Chuan Li](https://www.youtube.com/watch?v=F7jGCKHl7Wg)，Lambda 创始团队成员兼首席科学官[Bin Bao](https://www.youtube.com/watch?v=2LOPdVFoErs)，Meta 软件工程师、torch.compile 技术负责人[Jared Roesch](https://youtu.be/BBhZ9Ltpmdw?t=1717)，OctoAI 联合创始人、NVIDIA Distinguished Engineer[观看黑客松精彩集锦](https://www.modular.com/blog/modular-hack-weekend)并阅读[回顾博文](https://www.modular.com/blog/modular-hack-weekend?utm_source=modverse&utm_campaign=community)。探索[获奖项目](https://forum.modular.com/t/modular-hack-weekend-winners-announced/1848)与[全部提交作品](https://forum.modular.com/tags/c/community-showcase/8/modular-hack-weekend)。
- 我们在[视频首播](https://www.youtube.com/watch?v=TrBXHPGRlnQ)中发布了一系列重磅消息：Modular 平台正式在 AMD Instinct™ MI300X 与 MI325 GPU 上全面可用！基准显示 prefill 密集型 BF16 工作负载吞吐最高提升 53%。我们与 AMD 携手，把顶级算力与对开发者友好的软件结合在一起。详见[完整博文](https://www.modular.com/blog/modular-x-amd-unleashing-ai-performance-on-amd-gpus?utm_source=modverse&utm_campaign=community)。认识 Mammoth：我们新的 Kubernetes 原生系统，跨任意 GPU 扩展 GenAI 推理。用单一容器在 AMD 与 NVIDIA 上部署 Hugging Face 模型，无需手工配置。加入[公开预览](https://www.modular.com/blog/introducing-mammoth-enterprise-scale-genai-deployments-made-simple?utm_campaign=community&utm_source=modverse)。Python 中的 Mojo：现在可以把 Mojo kernel 直接放进 Python 工作流。nightly 版本即可体验，背后是 45 万行以上开源 Mojo kernel 代码。[从这里开始](https://docs.modular.com/mojo/manual/python/mojo-from-python/)。
- YouTube 上新：[Chris Lattner 在 AMD AdvancingAI 2025 的完整演讲](https://www.youtube.com/watch?v=liR2Pn5Zp9g)！了解 Mojo 如何融合 Python 的简洁与 C++ 的性能，驱动下一代 AI 软件栈。还有演讲后的 Chris Q&A。
- Chris Lattner 做客 [Latent Space 播客](https://www.youtube.com/watch?v=04_gN-C9IAo)，内幕式地讲述了 Modular 与 Mojo 的历史以及 GPU 编程的未来。
- [我们六月的社区会议](https://www.youtube.com/watch?v=1Q4RNVOSAH0)包含两场关于 Mojo 应用于科学计算的深度分享：[用 Mojo 做生物信息学](https://youtu.be/1Q4RNVOSAH0?t=32)：Seth 带我们了解 ish——一个用 Mojo 构建的高性能免索引比对工具，分享 SIMD 优化、GPU 加速以及与 Parasail 等 C++ 库的基准对比。[用 Mojo 做粒子物理](https://youtu.be/1Q4RNVOSAH0?t=1438)：Photon 分享 Mojo 如何简化复杂的粒子物理仿真，介绍了两个开源库 newmojo 与 hepjo，并讨论把 C++/Python 科研流水线移植到 Mojo 所带来的可观性能收益。
- Simon Veitner 发表了[关于为 NVIDIA Hopper 打造极速矩阵转置 kernel 的深度文章](https://veitner.bearblog.dev/highly-efficient-matrix-transpose-in-mojo/)。他讲解 TMA、swizzling、线程粗化，并展示用纯 Mojo 能把性能推到多远。想理解如何设置 descriptor 并高效搬运数据，先读 [Simon 的前一篇文章](https://veitner.bearblog.dev/use-tma-without-cuda/)。Mojo 新手？从头开始。[Simon 的入门文章](https://veitner.bearblog.dev/short-introduction-to-the-mojo-programming-language/)示范如何用 Mojo 的 Pythonic 语法通过向量加法写下第一个 GPU kernel。想把 Mojo 推向更深处，[Simon 还演示了在 Mojo 中使用自定义 PTX 指令获得高级 GPU 控制](https://veitner.bearblog.dev/use-ptx-instructions-in-mojo/)。
- 我们发布了[漫画系列 GPU Whisperers](https://comic.modular.com)，完美捕捉了身处 GenAI 革命洪流中的美妙混乱！🧑‍🚀
- Vincent Warmerdam 分享了一篇关于[从 Python 调用 Mojo](https://koaning.io/posts/giving-mojo-a-spin/)的出色文章。
- Modular [现已上架 Amazon Web Services（AWS）Marketplace](https://aws.amazon.com/marketplace/pp/prodview-t6oswipky4fhs)！500 多个预优化模型，带 OpenAI API 兼容端点，可在 NVIDIA B200、H200、H100、A100、A10、L40 和 L4 GPU 上运行，具备智能批处理与内存管理。
- Modular Tech Talks 是收录工程团队内部演讲的独家系列，讲解 Modular 技术栈的内在工作机制。[最新一期](https://www.youtube.com/watch?v=6hqMFXbugGo)中，Kyle Caverly 导览 MAX Pipelines 架构，涵盖主要接口及其如何使 Modular 团队快速拉起最先进模型，并带上 KV Cache 优化、投机解码等高性能特性。
- 要用 vibe coding 写出你的下一个 Mojo 杰作？机会来了：[查看指南](https://docs.modular.com/max/coding-assistants/)，学习如何用 Cursor、Copilot 等 AI 编码助手借助 Mojo 与 MAX 更快构建。
- Chris Lattner 近期的“AI 算力民主化”系列为塑造 AI 基础设施未来的挑战提供了清晰视角，现在你可以在一处读完全系列！🔖 [收藏或订阅 RSS](https://www.modular.com/democratizing-ai-compute?utm_source=modverse&utm_campaign=modverse)。[最新一篇](https://www.modular.com/blog/how-is-modular-democratizing-ai-compute?utm_source=modverse&utm_campaign=community)中，Chris Lattner 在 Modular 栈上绘制飞行图：Mojo 是炽热的内核世界，MAX 是巨大的气态行星，共同运行在 Mammoth 星团之中。
- 构建高性能 AI 基础设施不必花上数月。Inworld 用不到 8 周就在 Modular 上把最先进语音管线送进生产，证明了这一点。[他们的博客](https://inworld.ai/blog/how-we-made-state-of-the-art-speech-synthesis-scalable-with-modular)讲述如何用 MAX 与 Mojo 在 NVIDIA Blackwell GPU 上运行，实时延迟目标比使用最新 vLLM 快 70%。

# **Awesome MAX + Mojo**

- forfudan 创作了一本关于 Mojo 的在线书《Mojo Miji——从 Pythonista 视角看 Mojo 编程语言》（[论坛帖](https://forum.modular.com/t/mojo-miji-a-guide-to-mojo-programming-language-from-a-pythonistas-perspective/1594)）。
- TilliFe 开启了[在 Nabla 中训练 transformer 神经网络的 notebook 系列](https://forum.modular.com/t/training-a-transformer-with-max-acceleration/1695)——Nabla 是 Mojo 中的可微编程框架。
- HammadHAB 用 Mojo 写了一个[简单轻量的 INI 文件解析器](https://forum.modular.com/t/mojoini-minimal-ini-parser-in-mojo/1929)。
- [26 位社区成员分享了他们的 Modular Hack Weekend 项目！](https://forum.modular.com/tags/c/community-showcase/8/none/modular-hack-weekend)

# **开源贡献**

**‍**如果你最近第一次 PR 被合并，请在论坛私信 [**Caroline Frasca**](https://forum.modular.com/u/caroline) 领取你的 Modular 限定周边！看看我们出色社区成员[**最近合并的贡献**](https://github.com/modularml/mojo/pulls?page=1&q=is%3Apr+is%3Aclosed+label%3Amerged-internally+sort%3Aupdated-desc)：

- [Ivo-Balbaert](https://github.com/modular/modular/pulls?q=is%3Apr+author%3AIvo-Balbaert+) [[1](https://github.com/modular/modular/pull/4711)]
- [simveit](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Asimveit) [[1](https://github.com/modular/modular/pull/4715)][[2](https://github.com/modular/modular/pull/4725)][[3](https://github.com/modular/modular/pull/4706)]
- [soraros](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Asoraros+) [[1](https://github.com/modular/modular/pull/4707)][[2](https://github.com/modular/modular/pull/4608)][[3](https://github.com/modular/modular/pull/4607)][[4](https://github.com/modular/modular/pull/4734)][[5](https://github.com/modular/modular/pull/4339)][[6](https://github.com/modular/modular/pull/4557)][[7](https://github.com/modular/modular/pull/4778)][[8](https://github.com/modular/modular/pull/4764)][[9](https://github.com/modular/modular/pull/4733)][[10](https://github.com/modular/modular/pull/4733)][[11](https://github.com/modular/modular/pull/4753)][[12](https://github.com/modular/modular/pull/4786)][[13](https://github.com/modular/modular/pull/4526)][[14](https://github.com/modular/modular/pull/4775)][[15](https://github.com/modular/modular/pull/4760)][[16](https://github.com/modular/modular/pull/4747)][[17](https://github.com/modular/modular/pull/4744)][[18](https://github.com/modular/modular/pull/3083)][[19](https://github.com/modular/modular/pull/4693)][[20](https://github.com/modular/modular/pull/4770)][[21](https://github.com/modular/modular/pull/4799)][[22](https://github.com/modular/modular/pull/4821)][[23](https://github.com/modular/modular/pull/4825)][[24](https://github.com/modular/modular/pull/4204)][[25](https://github.com/modular/modular/pull/4876)][[26](https://github.com/modular/modular/pull/4816)][[27](https://github.com/modular/modular/pull/4903)][[28](https://github.com/modular/modular/pull/4901)][[29](https://github.com/modular/modular/pull/4900)][[30](https://github.com/modular/modular/pull/4880)][[31](https://github.com/modular/modular/pull/4898)][[32](https://github.com/modular/modular/pull/4895)][[33](https://github.com/modular/modular/pull/4890)][[34](https://github.com/modular/modular/pull/4772)][[35](https://github.com/modular/modular/pull/4875)][[36](https://github.com/modular/modular/pull/4935)][[37](https://github.com/modular/modular/pull/4933)][[38](https://github.com/modular/modular/pull/4814)][[39](https://github.com/modular/modular/pull/4757)][[40](https://github.com/modular/modular/pull/4812)][[41](https://github.com/modular/modular/pull/4800)]
- [martinvuyk](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Amartinvuyk) [[1](https://github.com/modular/modular/pull/4704)][[2](https://github.com/modular/modular/pull/4653)][[3](https://github.com/modular/modular/pull/4592)][[4](https://github.com/modular/modular/pull/4593)][[5](https://github.com/modular/modular/pull/4671)][[6](https://github.com/modular/modular/pull/3528)][[7](https://github.com/modular/modular/pull/3810)][[8](https://github.com/modular/modular/pull/4605)][[9](https://github.com/modular/modular/pull/4595)][[10](https://github.com/modular/modular/pull/4802)][[11](https://github.com/modular/modular/pull/4803)][[12](https://github.com/modular/modular/pull/4869)][[13](https://github.com/modular/modular/pull/4858)][[14](https://github.com/modular/modular/pull/4323)][[15](https://github.com/modular/modular/pull/4756)]
- [christoph-schlumpf](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Achristoph-schlumpf+) [[1](https://github.com/modular/modular/pull/4714)]
- [bgreni](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Abgreni) [[1](https://github.com/modular/modular/pull/4171)][[2](https://github.com/modular/modular/pull/4806)]
- [gabrieldemarmiesse](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Agabrieldemarmiesse+) [[1](https://github.com/modular/modular/pull/4661)]
- [sstadick](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Asstadick+) [[1](https://github.com/modular/modular/pull/4746)][[2](https://github.com/modular/modular/pull/4762)][[3](https://github.com/modular/modular/pull/4537)][[4](https://github.com/modular/modular/pull/4796)]
- [bgreni](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Abgreni+) [[1](https://github.com/modular/modular/pull/4635)][[2](https://github.com/modular/modular/pull/4781)][[3](https://github.com/modular/modular/pull/4785)]
- [hardikkgupta](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Ahardikkgupta+) [[1](https://github.com/modular/modular/pull/4782)][[2](https://github.com/modular/modular/pull/4832)][[3](https://github.com/modular/modular/pull/4897)]
- [sibarras](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Asibarras+) [[1](https://github.com/modular/modular/pull/4784)]
- [msaelices](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Amsaelices+) [[1](https://github.com/modular/modular/pull/4625)][[2](https://github.com/modular/modular/pull/4562)]
- [mzaks](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Amzaks+) [[1](https://github.com/modular/modular/pull/4841)][[2](https://github.com/modular/modular/pull/4863)]
- [zsiegel92](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Azsiegel92+) [[1](https://github.com/modular/modular/pull/4881)]
- [winding-lines](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Awinding-lines+) [[1](https://github.com/modular/modular/pull/4888)]
- [samufi](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Asamufi) [[1](https://github.com/modular/modular/pull/4928)]
