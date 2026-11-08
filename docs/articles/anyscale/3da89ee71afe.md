---
vendor: anyscale
title: 加速 AI：在 Ray 2.10 中释放 Intel(R) Gaudi(R) 3 算力
original_title: Accelerating AI: Harnessing Intel(R) Gaudi(R) 3 with Ray 2.10
url: https://anyscale.com/blog/accelerating-ai-harnessing-intel-gaudi-3-with-ray-2-10
date: 2024-04-09
lang: zh
captured: 2026-11-08
extractor: readability-v1
translator: agent
status: translated
body_sha: 550964272f03
---

# 加速 AI：在 Ray 2.10 中释放 Intel(R) Gaudi(R) 3 算力

作者：[Ramit Hora](https://www.anyscale.com/blog?author=ramit-hora) | 2024 年 4 月 9 日

## 硬件与能源短缺是否正在制约 AI 的发展？

如果你关注 AI 领域的新闻，就会注意到地平线上浮现出了一个新的隐忧——有人认为它将压垮全球电网，并实质性地延缓 AI 的落地普及。随着越来越多的企业对 AI 产生兴趣，[AI 工作负载正在飞速增长，并消耗过多电力](https://www.morningbrew.com/daily/stories/2024/03/24/the-power-grid-has-an-ai-problem)。专家们担心，这种电力短缺可能会演化为更大范围的负面连锁反应——包括能源价格上涨、局部停电以及气候变化加速。

作为历史上众多最流行、应用最广泛的计算机芯片的制造者，[Intel 去年宣布计划](https://www.cnbc.com/2023/12/14/intel-unveils-gaudi3-ai-chip-to-compete-with-nvidia-and-amd.html)于 2024 年推出其专用“Gaudi”系列 AI 加速器的下一代产品——Intel Gaudi 3，这并不令人意外。该公司正持续向前推进，不断扩展和演进其产品线，以应对从桌面端到数据中心的各种 AI 工作负载。

值得注意的是，这种算力资源问题并非凭空出现。我们早就明白，尽管过去 50 年间的所有计算密集型工作负载都是巨大的能源消耗源，但 AI 的情况却截然不同。与过去几十年中的 CRM、Web3 或大数据等其他重大技术浪潮不同，AI 实际上以一种独特的方式*改变了对底层硬件的需求*。具体来说，诸如模型训练等部分 AI 工作负载已被证明在图形处理单元（GPU）芯片组上的运行效果显著优于传统 CPU 芯片组，从而引发了业界对专用 AI 硬件与加速器的极大关注。

## Intel(R) 与 Anyscale：为 AI 效率持续优化

在 Anyscale，我们非常感谢与 Intel 之间保持的长期合作伙伴关系。这种合作的核心是联合研发——Anyscale 与 Intel 的工程师通力协作，针对 Intel 加速器对 Ray 和 Anyscale Platform 进行深度优化。我们也很荣幸有 Intel Capital 作为投资方，帮助我们推动 Ray 的普及，并为 AI 创新与集成提供资金支持。

**今天，在 **[**Intel Vision 大会**](https://www.intel.com/content/www/us/en/events/on-event-series/vision.html)** 上，我们很高兴地宣布，Anyscale 发布的最新版 Ray（Ray 2.10）正式新增了对 Intel Gaudi 3 的支持。**

“在 Intel，我们长期以来坚信开源将发挥关键作用，它不仅能促进 AI 的民主化，更是推动创新的重要力量，”Intel Habana Labs 首席运营官 Eitan Medina 表示，“Ray 2.10 与 Intel Gaudi 3 加速器携手，为从业者提供了一套优化的、基于开源的 AI 解决方案，以满足当今不断增长和演进的 AI 工作负载在规模、性能、成本及能效方面的需求。”

我们鼓励用户[亲自上手体验](https://docs.ray.io/en/latest/serve/tutorials/intel-habana-gaudi-inference.html)。Gaudi 与 Ray 在整个 Ray Stack 中都实现了深度集成。你可以：

- 直接通过 Ray Core API 启动并管理你自己的 Ray 集群，在 Gaudi 节点集群上调度 **Ray Core** 的 [Task 与 Actor](https://docs.ray.io/en/master/ray-core/scheduling/accelerators.html#using-accelerators-in-tasks-and-actors)。
- 通过 Ray Serve API 在 Gaudi 上使用 **Ray Serve**，获得更高层次的开发体验。参见[此处示例](https://docs.ray.io/en/master/serve/tutorials/intel-habana-gaudi-inference.html)，了解如何在单张或多张 Gaudi 芯片上设置运行 Llama2 7B 和 70B 的单机及分布式推理。
- 配置 Gaudi 基础设施以便在 **Ray Train** 层使用。参见[此处示例](https://docs.ray.io/en/master/train/examples/hpu/resnet.html)（含环境配置）。

我们的团队本周正在参加 Intel Vision 大会，与用户、Intel 的伙伴以及行业先锋交流。联合创始人兼执行董事长 Ion Stoica 将出席以“分布式计算的未来：AI 如何在未来 5 年内改变系统架构”（*Future of Distributed Compute: How AI will tranform systems Architecture in Next 5 years*）为主题的圆桌讨论，并将带来名为“面向生成式 AI 扩展系统”（*Scaling Systems for Gen AI*）的主题演讲。此外，我们的产品营销主管 Subrata Charkrabarti 还将在“基础设施 AI ISV 专题会议”（*Infrastructure AI ISV Session*）上探讨开源 AI 的发展趋势。

请持续关注未来几个月有关 Anyscale 与 Intel 集成的更多资讯。我们将发布更多基准测试与研究成果，帮助你结合使用 Intel 与 Anyscale，为 AI 工作负载持续带来极致的性能、扩展性与能效优化。
