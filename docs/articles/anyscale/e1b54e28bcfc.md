---
vendor: anyscale
title: Ray 加入 PyTorch 基金会
original_title: 
url: https://anyscale.com/blog/ray-by-anyscale-joins-pytorch-foundation
date: 2025-10-22
lang: zh
captured: 2026-11-05
extractor: readability-v1
translator: mt
status: translated
body_sha: f7cd470c5a8d
---

[主页](https://www.anyscale.com/)[博客](https://www.anyscale.com/blog)博客详细信息

# Ray 加入 PyTorch 基金会

作者：[Robert Nishihara](https://www.anyscale.com/blog?author=robert-nishihara)、[Philipp Moritz](https://www.anyscale.com/blog?author=philipp-moritz) 和 [Ion Stoica](https://www.anyscale.com/blog?author=ion-stoica) | 2025 年 10 月 22 日

今天，[Ray](https://github.com/ray-project/ray/) 加入了 PyTorch 基金会，该基金会是 Linux 基金会的一部分。 Linux 基金会是基础设施项目的所在地，包括 Kubernetes、PyTorch 和 vLLM。

去年，Ray 的下载量增长了近 10 倍。

如今，Ray 每年推动数十亿美元的计算消耗，并为全球范围内的 AI 工作负载提供动力，[Ray Summit 2025](https://www.anyscale.com/ray-summit/2025) 展示了来自各公司的用例，包括

- 人工智能初创公司：xAI、Thinking Machines、Perplexity
- 老牌科技公司：Netflix、字节跳动、苹果、腾讯、阿里巴巴
- 主要企业：摩根大通、宝马、桥水、Workday

![Ray 每周下载量](https://images.ctfassets.net/xjan103pcp94/3taOf5VUlDYr6PMyZZcLj2/0f72b4839582e4ca757e9f9330c46f87/image_23.png)Ray 每周下载量

雷每周下载量

## 链接**早期**

我们在加州大学伯克利分校创办 Ray 是因为，作为研究 AI 的研究生，我们需要跨 CPU 和 GPU 集群扩展我们的算法，并且我们发现自己花费了大部分时间构建基础设施来解决分布式系统的扩展挑战（可靠性、成本、性能）。

从一开始，我们就对生产有用的开源软件感兴趣。我们受到实验室上一代学生的启发，他们创建了 [Apache Spark](https://github.com/apache/spark)。

我们于 2019 年成立 Anyscale 来开发 Ray 并将其商业化。然而，当时，只有最早的采用者才需要扩大规模。蚂蚁集团是Ray的第一个主要生产用户。 Uber 和 Pinterest 是紧随其后的。但现实是，当时绝大多数公司不需要扩展人工智能的计算规模。

随着生成式人工智能、LLM和当今推理模型的出现，所有这一切都发生了变化。到了 2025 年，规模化的需求已经很明显了。如今，围绕扩展 AI 工作负载的软件工程挑战比我们创立 Ray 时要大得多。

## 链接**全圆**

在某些方面，我们已经回到了原点。从一开始，我们就将 Ray 设想为一个通用框架（Ray 的核心是一个参与者框架），但我们追求的第一个用例是强化学习。我们在[原始 Ray 论文](https://arxiv.org/abs/1712.05889) 中使用 RL 来展示 Ray 的优势。我们专注于强化学习，因为我们自己也在研究 RL（[TRPO](https://arxiv.org/abs/1502.05477)、[RLlib](https://arxiv.org/abs/1712.09381)）。 AI 社区的很大一部分人致力于玩 Atari 游戏并学习 Mujoco 等物理模拟器中的运动控制。然而，围绕强化学习的那股兴奋浪潮相对孤立，并没有转化为广泛的实际应用。

如今，强化学习因其在构建推理模型和塑造代理行为方面的成功而卷土重来。如今，几乎每个[用于训练后 LLM 的开源 RL 框架](https://www.anyscale.com/blog/open-source-rl-libraries-for-llms) 都是构建在 Ray 之上的。

## 链接**PyTorch 基金会**

当谈到基础设施软件时，开源获胜。随着[AI软件计算堆栈](https://www.anyscale.com/blog/ai-compute-open-source-stack-kubernetes-ray-pytorch-vllm)的出现，堆栈的每一层都将有一个开源标准。 PyTorch 是占主导地位的深度学习框架。 Kubernetes 是占主导地位的容器编排器。我们正在构建 Ray 作为开源分布式计算引擎。

去年，Ray 的采用呈爆炸式增长。 Ray 现在加入 PyTorch 基金会是因为我们正在发展一个全球贡献者社区。对规模的需求只会不断增长，我们的目的是大力投资并围绕 Ray 建立开源社区，以满足人工智能快速发展的需求。

## 链接**加入 Ray 社区**

这只是开始。

- 11 月 3 日至 5 日在旧金山参加 [ Ray Summit 2025](https://www.anyscale.com/ray-summit/2025?utm_source=blog&utm_medium=web&utm_campaign=pytorch-donation&utm_content=ray-summit) 与社区见面
- 注册新的[简介雷](https://courses.anyscale.com/bundles/introduction-to-ray?__hstc=143905642.0ab17989225ebf831fe5 00ef059ee2b8.1753208986630.1759787843262.1760983194684.22&__hssc=143905642.15.1760983194684&__hsfp= 1062460436&_gl=1*rpuc7f*_gcl_au*MTQ1OTU4MDEwOS4xNzYwOTgzMTg5LjE5NDQyMjQ0NzguMTc2MDk4MzgyOS4xNzYwOTg zODI4?utm_source=blog&utm_medium=web&utm_campaign=pytorch-donation&utm_content=intro-to-ray-course)课程
- 在 [ GitHub](https://github.com/ray-project/ray) 上为 Ray 做出贡献
- 加入 Ray[Slack](https://www.ray.io/join-slack?utm_source=blog&utm_medium=web&utm_campaign=pytorch-donation&utm_content=slack)

我们将共同继续塑造人工智能基础设施的未来——开放和社区驱动。

#### 目录

- [早期](https://www.anyscale.com/blog/ray-by-anyscale-joins-pytorch-foundation#early-days)
- [全圆](https://www.anyscale.com/blog/ray-by-anyscale-joins-pytorch-foundation#full-circle)
- [PyTorch 基金会](https://www.anyscale.com/blog/ray-by-anyscale-joins-pytorch-foundation#pytorch-foundation)
- [加入 Ray 社区](https://www.anyscale.com/blog/ray-by-anyscale-joins-pytorch-foundation#join-the-ray-community)

####分享

####标签

#### 注册产品更新

####推荐内容

![kuberay-products-best-practices-field](https://images.ctfassets.net/xjan103pcp94/3uRWLXRJv2sisfuH1UpkBg/7ffa981a092ba41c591b03ef933976bf/kuberay-products-best-practices-field.png?w=140)

#### 生产中的 KubeRay：现场最佳实践

![宣布 Ray 在 Google TPU 上支持 PyTorch](https://images.ctfassets.net/xjan103pcp94/5odqs3bDXHHrUGye7EReO6/12a5fb11fc7d119b1ce905d420821160/ExternalRayTorchTPUblog.png?w=140)

#### 宣布 Ray 在 Google TPU 上支持 PyTorch

![使用 KubeRay 在 Kubernetes 上大规模运行 Ray](https://images.ctfassets.net/xjan103pcp94/6rF9ECqCFk5OjE7RftoynJ/e003a1df2ce07a3177dbdd4d1fe76473/Running_Ray_at_scale_on_Kubernetes_with_KubeRay.png?w=140)

#### 使用 KubeRay 在 Kubernetes 上大规模运行 Ray

## 立即探索 Anyscale

使用专为生产 AI 构建的多云平台，在 Ray 上构建、运行和扩展任何 AI 工作负载。

[免费开始](https://authkit.anyscale.com/?utm_source=anyscale&utm_content=exploreblock&utm_medium=website&utm_campaign=cta)[与专家交谈](https://www.anyscale.com/book/demo?utm_source=anyscale&utm_content=exploreblock&utm_medium=website&utm_campaign=cta)
