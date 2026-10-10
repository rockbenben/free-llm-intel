---
vendor: openai
title: Procgen 与 MineRL 竞赛
original_title: Procgen and MineRL Competitions
url: https://openai.com/index/procgen-minerl-competitions
date: 2024-03-13
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Procgen 与 MineRL 竞赛

我们兴奋地宣布，OpenAI 将与 AIcrowd、卡内基梅隆大学和 DeepMind 共同组织两场 NeurIPS 2020 竞赛，分别使用 Procgen Benchmark 和 MineRL。我们在内部高度依赖这些环境开展强化学习研究，期待看到社区在这些高难度竞赛中取得的进步。

## Procgen 竞赛

[Procgen 竞赛](https://www.aicrowd.com/challenges/neurips-2020-procgen-competition)聚焦于提升强化学习的样本效率与泛化能力。参赛者将在固定的环境交互次数预算内，最大化 agent 的表现。Agent 将在 [Procgen Benchmark](https://arxiv.org/abs/1912.01588) 已公开的 16 个环境，以及专为本次竞赛创建的 4 个保密测试环境中分别接受评估。通过在如此多多样环境上聚合表现，我们能得到高质量的指标来评判底层算法。各轮赛的详情见[此处](https://www.aicrowd.com/challenges/neurips-2020-procgen-competition)。

- [报名 Procgen](https://www.aicrowd.com/challenges/neurips-2020-procgen-competition)

由于所有内容均为程序化生成，每个 Procgen 环境从本质上就要求 agent 泛化到从未见过的情况。因此，这些环境为 agent 在众多多样情境中学习的能力提供了稳健的检验。此外，我们把 Procgen 环境设计得快速、易用。算力有限的参赛者也能轻松复现我们的基线结果并运行新实验。希望这能让参赛者快速迭代新方法，改进 RL 的样本效率与泛化。

## MineRL 竞赛

近年来人工智能的诸多标志性成功——如 AlphaStar、AlphaGo 和我们自己的 [OpenAI Five⁠](https://openai.com/projects/five/)——都利用深度强化学习在序列决策任务上达到人类甚至超人类水平。而这些最先进进展迄今需要[指数级增长⁠](https://openai.com/index/ai-and-compute/)的算力和模拟器样本，因此许多系统难以[A](https://openai.com/index/procgen-minerl-competitions/#citation-bottom-A)直接应用于环境采样昂贵的现实问题。降低环境样本复杂度的一种著名途径，是利用人类先验和期望行为的示范。

为进一步催化这一方向的研究，我们共同组织了 [MineRL 2020 竞赛](https://www.aicrowd.com/challenges/neurips-2020-minerl-challenge)，旨在促进能够高效利用人类示范、大幅降低解决复杂、层级化、稀疏环境所需样本数的算法发展。为此，参赛者将竞相开发这样的系统：仅用 [MineRL 模拟器](http://minerl.io/docs) 的 8,000,000 个样本、在单 GPU 机器上训练 4 天，就能在 [Minecraft](http://minercraft.net/) 中从原始像素获得钻石。参与者将获得 MineRL-v0 数据集（[网站](http://minerl.io/dataset/)、[论文](https://arxiv.org/abs/1907.13440)）——一个包含超过 6000 万帧人类示范的大规模集合——使他们能利用专家轨迹，最小化算法与 Minecraft 模拟器的交互。

本次竞赛是 [MineRL 2019 竞赛](https://www.aicrowd.com/challenges/neurips-2019-minerl-competition) 的延续。在那届比赛中，[冠军队伍的 agent](https://arxiv.org/pdf/1912.08664v2.pdf)在如此有限的算力与模拟器交互预算下成功[获得了铁镐](https://www.youtube.com/watch?v=GHo8B4JMC38&feature=youtu.be)（该竞赛倒数第二高的目标）。对比之下，最先进的标准强化学习系统需要在大规模多 GPU 系统上进行数亿次环境交互才能达到同样目标。今年，我们预期参赛者会把最先进水平再推高。

为确保参赛者开发出真正样本高效的算法，MineRL 竞赛组织者会在严格的硬件、算力与模拟器交互约束下，从零训练冠军队伍的最后一轮模型。MineRL 2020 竞赛还引入一项新机制，以防止手工设计特征和针对该领域的过拟合方案。赛制详情见[此处](https://www.aicrowd.com/challenges/neurips-2020-minerl-challenge)。

- [报名 MineRL](https://www.aicrowd.com/challenges/neurips-2020-minerl-competition)

## 脚注

- A 虽然由于所需样本数量庞大而无法直接应用，但 Sim2Real 与数据增强技术可以缓解对直接采样现实世界动态的需求。
