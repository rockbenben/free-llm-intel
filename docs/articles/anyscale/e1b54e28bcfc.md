---
vendor: anyscale
title: Ray 加入 PyTorch 基金会
original_title: 
url: https://anyscale.com/blog/ray-by-anyscale-joins-pytorch-foundation
date: 2025-10-22
lang: zh
captured: 2026-11-05
extractor: readability-v1
translator: agent
status: translated
body_sha: 13b3d173980a
---

# Ray 加入 PyTorch 基金会

作者：[Robert Nishihara](https://www.anyscale.com/blog?author=robert-nishihara)、[Philipp Moritz](https://www.anyscale.com/blog?author=philipp-moritz) 和 [Ion Stoica](https://www.anyscale.com/blog?author=ion-stoica) | 2025 年 10 月 22 日

今天，[Ray](https://github.com/ray-project/ray/) 加入 PyTorch 基金会，该基金会是 Linux 基金会的一部分。Linux 基金会旗下汇聚了一批基础设施核心项目，包括 Kubernetes、PyTorch 和 vLLM。

过去一年里，Ray 的下载量增长了近 10 倍。

如今，Ray 每年驱动着数十亿美元的算力消耗，支撑着全球范围内的 AI 工作负载；在 [Ray Summit 2025](https://www.anyscale.com/ray-summit/2025) 上，来自各行各业公司的用例悉数登场，包括

- AI 初创公司：xAI、Thinking Machines、Perplexity
- 成熟的科技公司：Netflix、ByteDance、Apple、Tencent、Alibaba
- 大型企业：JPMorgan、BMW、Bridgewater、Workday

![Ray 每周下载量](https://images.ctfassets.net/xjan103pcp94/3taOf5VUlDYr6PMyZZcLj2/0f72b4839582e4ca757e9f9330c46f87/image_23.png)Ray 每周下载量

Ray 每周下载量

## **早期岁月**

我们在 UC Berkeley 创办 Ray，是因为作为研究 AI 的研究生，我们需要把算法扩展到 CPU 与 GPU 集群上运行，结果发现自己大部分时间都花在搭建基础设施上，用来解决规模化带来的分布式系统难题（可靠性、成本、性能）。

从一开始，我们就想做真正有用的开源软件，而我们的灵感来自实验室里上一代同学——他们做出了 [Apache Spark](https://github.com/apache/spark)。

我们在 2019 年创办 Anyscale，以开发并商业化 Ray。但在那个时候，只有最早一批采用者才有规模化的需求。Ant Group 是 Ray 的第一个主要生产用户，Uber 和 Pinterest 紧随其后。但现实是，当时绝大多数公司根本不需要为 AI 扩展算力。

随着生成式 AI、LLM 以及今天这些推理模型的出现，一切都变了。到了 2025 年，规模化的需求已经清清楚楚；而围绕扩展 AI 工作负载的软件工程挑战，也远比我们创办 Ray 时更大。

## **回到原点**

从某些方面看，我们绕了一圈又回到了原点。从一开始，我们就把 Ray 设想成一个通用框架（就内核而言，Ray 是一个 actor 框架），但我们最先攻克的用例却是强化学习。我们在[最初的 Ray 论文](https://arxiv.org/abs/1712.05889)里就是用 RL 来展示 Ray 的优势。我们之所以专注强化学习，是因为我们自己就在做 RL（[TRPO](https://arxiv.org/abs/1502.05477)、[RLlib](https://arxiv.org/abs/1712.09381)）。当时 AI 社区里有很大一部分人在打 Atari 游戏、在 Mujoco 这类物理仿真器里学习运动控制。不过那一波围绕强化学习的热潮相对封闭，并没有转化成广泛的实际应用。

今天，强化学习凭借它在构建推理模型、塑造 agent 行为方面的成功而强势回归。而现在，几乎每一个[用于 LLM 后训练的开源 RL 框架](https://www.anyscale.com/blog/open-source-rl-libraries-for-llms)都构建在 Ray 之上。

## **PyTorch 基金会**

说到基础设施软件，开源会赢。随着[面向 AI 的软件计算栈](https://www.anyscale.com/blog/ai-compute-open-source-stack-kubernetes-ray-pytorch-vllm)逐渐成形，栈上的每一层都会有一个开源标准。PyTorch 是占据主导地位的深度学习框架，Kubernetes 是占据主导地位的容器编排器，而我们构建 Ray，是要让它成为开源的分布式计算引擎。

过去一年 Ray 的采用呈爆发式增长。Ray 此时加入 PyTorch 基金会，是因为我们正在成长出一个全球贡献者社区。对规模的需求只会继续增长，而我们的打算是在 Ray 上大力投入，围绕它建好开源社区，以满足 AI 快速演进的需求。

## **加入 Ray 社区**

这一切才刚刚开始。

- 11 月 3 日至 5 日在旧金山，到 [Ray Summit 2025](https://www.anyscale.com/ray-summit/2025?utm_source=blog&utm_medium=web&utm_campaign=pytorch-donation&utm_content=ray-summit) 与社区见面
- 报名全新的 [Intro to Ray](https://courses.anyscale.com/bundles/introduction-to-ray?__hstc=143905642.0ab17989225ebf831fe500ef059ee2b8.1753208986630.1759787843262.1760983194684.22&__hssc=143905642.15.1760983194684&__hsfp=1062460436&_gl=1*rpuc7f*_gcl_au*MTQ1OTU4MDEwOS4xNzYwOTgzMTg5LjE5NDQyMjQ0NzguMTc2MDk4MzgyOS4xNzYwOTgzODI4?utm_source=blog&utm_medium=web&utm_campaign=pytorch-donation&utm_content=intro-to-ray-course) 课程
- 在 [GitHub](https://github.com/ray-project/ray) 上为 Ray 做贡献
- 加入 Ray 的 [Slack](https://www.ray.io/join-slack?utm_source=blog&utm_medium=web&utm_campaign=pytorch-donation&utm_content=slack)

我们将一起继续塑造 AI 基础设施的未来——开放、由社区驱动。
