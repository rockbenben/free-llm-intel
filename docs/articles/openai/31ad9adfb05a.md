---
vendor: openai
title: Gym Retro
original_title: Gym Retro
url: https://openai.com/index/gym-retro
date: 2022-10-19
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Gym Retro

我们发布 [Gym Retro](https://github.com/openai/retro) 的完整版本——一个用于游戏强化学习研究的平台。这把公开游戏数量从约 70 款 Atari 游戏和 30 款世嘉游戏，扩展到依托多种模拟器、超过 1000 款游戏。我们还发布了用于向平台添加新游戏的工具。

我们用 Gym Retro 开展 RL 算法研究并研究泛化能力。此前 RL 研究大多聚焦于优化智能体以解决单一任务。有了 Gym Retro，我们可以研究在概念相似、外观不同的游戏之间进行泛化的能力。

本次发布包含世嘉 Genesis、世嘉 Master System，以及任天堂 NES、SNES 和 Game Boy 主机的游戏。同时还初步支持世嘉 Game Gear、任天堂 Game Boy Color、任天堂 Game Boy Advance 和 NEC TurboGrafx。部分已集成的游戏——包括 Gym Retro `data/experimental` 目录下的游戏——仍处于 beta 状态，欢迎试用，如遇 bug 请告知。由于涉及的改动规模巨大，代码暂时只在[分支](https://github.com/openai/retro)上提供。为避免破坏参赛者的代码，我们要等比赛结束后才会合并该分支。

正在进行中的 [Retro Contest](https://contest.openai.com/)（还有几周就结束！）和我们最近的[技术报告](https://arxiv.org/abs/1804.03720)聚焦于较容易的问题：在同一款游戏（《Sonic The Hedgehog™》）的不同关卡之间泛化。完整的 Gym Retro 数据集把这一想法推得更远，使研究更难的问题——不同游戏之间的泛化——成为可能。数据集的规模和单款游戏的难度使其成为一项艰巨挑战，我们期待在未来一年分享研究进展。我们也希望 Retro Contest 参赛者开发的一些方案能被放大并应用于完整的 Gym Retro 数据集。

## 集成工具

我们还发布了用于集成新游戏的工具。只要你有游戏的 ROM，这个工具就能让你轻松创建存档状态、定位内存地址、设计供强化学习智能体解决的场景。我们为希望添加新游戏支持的人写了[集成者指南](https://retro.readthedocs.io/en/latest/integration.html)。

集成工具还支持录制和播放记录了所有按键输入的 movie 文件。这些文件很小，因为只需保存初始状态和按键序列，而不必存储输出的每一帧。这类 movie 文件既可用于可视化你的强化学习智能体在做什么，也可存储人类输入用作训练数据。

## 刷分现象

在开发 Gym Retro 的过程中，我们发现了大量例子：智能体学会了"刷"奖励（定义为游戏分数的增长），而不是完成隐含任务。在上面的片段中，《Cheese Cat-Astrophe（左）》和《Blades of Vengeance（右）》中的角色陷入了无限循环，因为那样能快速积累奖励。这凸显了我们此前讨论过的一个[现象](https://blog.openai.com/faulty-reward-functions/)：我们给当代强化学习算法的相对简单的奖励函数——比如最大化游戏分数——可能导致不良行为。

对于奖励密集（频繁且渐进）、且难度主要来自需要快速反应的游戏，PPO 这类强化学习算法表现出色。

在《Gradius》（右图）这样的游戏中，击落每个敌人都能得分，因此很容易获得奖励并开始学习。在这类游戏中存活取决于躲避敌人的能力，而这对强化学习算法不成问题——它们逐帧地进行游戏。

对于奖励稀疏或需要向前规划数秒以上的游戏，现有算法就举步维艰。Gym Retro 数据集中的许多游戏要么奖励稀疏、要么需要规划，因此要攻克完整数据集，很可能需要尚未发展的新技术。

如果你热衷于在一个空前庞大的数据集上开展迁移学习和元学习研究，欢迎考虑[加入 OpenAI⁠](https://openai.com/careers/)。

## 作者

Vicki Pfau, Alex Nichol, Christopher Hesse, Larissa Schiavo, John Schulman, Oleg Klimov
