---
vendor: openai
title: Retro 竞赛
original_title: Retro Contest
url: https://openai.com/index/retro-contest
date: 2023-10-26
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 60d93e9e34fc
---

OpenAI

April 5, 2018

Milestone

# Retro 竞赛

我们发起一场迁移学习竞赛，用于衡量强化学习算法从以往经验中泛化的能力。

Contest

(opens in a new window)

Read paper

(opens in a new window)

Gym Retro

(opens in a new window)

Illustration: Timothy J. Reynolds

Loading…

## 为什么重要

在典型的 RL 研究中，算法在被训练的同一环境里测试，这会偏袒擅长记忆且拥有大量超参数的算法。而我们的竞赛则在一个算法从未见过的电子游戏关卡上测试它。竞赛使用 Gym Retro——一个把经典游戏整合进 Gym 的新平台，首发包含 30 款 SEGA Genesis 游戏。

*更新：[*结果*⁠](https://openai.com/index/retro-contest-results/) *已经出炉！*

Loading...

[OpenAI Retro Contest⁠(opens in a new window)](https://contest.openai.com/) 会提供一份来自 Sonic The Hedgehog™ 系列的关卡作为训练集，我们在一份专门为本次竞赛制作的自定义关卡测试集上评估你的算法。竞赛于 4 月 5 日至 6 月 5 日举行。为便于大家起步，我们发布了 [retro-baselines⁠(opens in a new window)](https://github.com/openai/retro-baselines)，演示如何在竞赛任务上运行多种 RL 算法。

Retro Contest（测试集）上的基线结果表明，即便使用迁移学习，RL 算法仍远远落后于人类表现。人类表现以水平虚线展示。人类只玩了 1 小时，而算法为 18 小时。

训练时你可以使用任何你希望的环境或数据集，但测试时每关只给你大约 18 小时（100 万个时间步）。18 小时听起来是打一通游戏关卡的很长时间，但在这种训练预算下，现有 RL 算法的表现远不如人类。

## Sonic 基准

为详细描述基准并给出一些基线结果，我们发布了一份技术报告：[Gotta Learn Fast: A New Benchmark for Generalization in RL⁠(opens in a new window)](https://arxiv.org/abs/1804.03720)。报告包含基准细节，以及运行 [Rainbow DQN⁠(opens in a new window)](https://arxiv.org/abs/1710.02298)、[PPO⁠](https://openai.com/index/openai-baselines-ppo/) 和一个简单随机猜测算法 JERK 的结果。JERK 针对 Sonic 优化地采样随机动作序列，随着训练进行，它会更加频繁地重放得分最高的动作序列。

我们发现，借助训练关卡上的经验，可以显著提升 PPO 在测试关卡上的表现。当网络先在训练关卡上预训练、再在测试关卡上微调时，其表现几乎翻倍，超过所有最强的替代基线。虽然这不是 RL 领域首次报告迁移学习成功的案例，但令人振奋的是，它显示迁移学习可以带来巨大而可靠的效果。

但我们的算法要追上人类表现，还有很长的路。如图所示，在训练关卡上练习 2 小时、在每个测试关卡上游玩 1 小时之后，人类获得的分数显著高于包括使用迁移学习在内的 RL 算法所得分数。

## Sonic 录像

我们制作了一个 [人类通关 Sonic 关卡的录像数据集⁠(opens in a new window)](https://github.com/openai/retro-movies)，用于 Retro Contest 中的 Sonic 关卡。这些录像可用来让智能体从每关过程内的随机采样点开始游玩，从而暴露于如果只从关卡起点开始就可能永远看不到的大量区域。研究者还可以使用这些录像，训练那些能从演示中学习的智能体。

## Gym Retro Beta

我们发布 Gym Retro，一套把经典电子游戏封装为 RL 环境的系统。这份初步版本包含 30 款来自 [SEGA Mega Drive and Genesis Classics Steam Bundle⁠(opens in a new window)](http://store.steampowered.com/app/34270/) 的 SEGA Genesis 游戏，以及 Arcade Learning Environment 中 62 款 Atari 2600 游戏。

[Atari 2600 游戏合集 Arcade Learning Environment⁠(opens in a new window)](https://github.com/mgbellemare/Arcade-Learning-Environment) 为强化学习提供了接口，是过去五年 RL 研究的重要推动力。这些 Atari 游戏比此前的 RL 基准更多样、更复杂——它们本来就是为了挑战玩家的反应能力和解题能力而设计。

[Gym Retro Beta⁠(opens in a new window)](https://github.com/openai/retro) 采用了比 Atari 更现代的主机——SEGA Genesis——扩展了可用于 RL 研究的游戏数量与复杂度。Genesis 上的游戏往往有很多关卡，某些维度相似（物理、物体外观），另一些维度不同（布局、道具），非常适合做迁移学习的实验田。它们也比 Atari 游戏更复杂，因为它们利用了 Genesis 更强的硬件（例如内存是 Atari 的 500 多倍，控制输入种类更多，图形支持也更好）。

Gym Retro 的灵感来自 [Retro Learning Environment⁠(opens in a new window)](https://arxiv.org/abs/1611.02205)，但编写上比 RLE 更灵活；例如，在 Gym Retro 中你可以通过 JSON 文件而非 C++ 代码来指定环境定义，更容易集成新游戏。

Loading...

Gym Retro 是我们构建大规模 RL 环境数据集的第二代尝试。它继承了 2016 年底 Universe 的一些想法，但我们未能在 Universe 实现上取得好结果，因为 Universe 环境是异步运行的、只能实时进行、并常常因基于屏幕检测游戏状态而不可靠。Gym Retro 把 Arcade Learning Environment 的模型扩展到了一个远为庞大的可选游戏集合上。

如需上手 Gym Retro，请查看 GitHub 上的 Getting Started 章节。

Loading...

有时，算法会在游戏里发现漏洞。这里，一个 PPO 训练的策略发现自己能穿墙向右移动以获得更高分数——又一个关于特定奖励函数如何导致 AI 智能体表现出 [怪异行为⁠](https://openai.com/index/faulty-reward-functions/) 的例子。

- [Exploration & Games](https://openai.com/research/index/?tags=exploration-game)
- [Community & Collaboration](https://openai.com/research/index/?tags=community-collaboration)
- [Simulated Environments](https://openai.com/research/index/?tags=simulated-environments)

## 作者

Christopher Hesse, John Schulman, Vicki Pfau, Alex Nichol, Oleg Klimov, Larissa Schiavo

## 其他贡献

感谢 Jonathan Gray 与 Tom Brown 对 gym-retro 早期版本的贡献。

感谢 Philipp Moritz、Robert Nishihara、Adam Stelmaszczyk、Aravind Srinivas、Qin Yongliang、Julian Togelius 与 Emilio Parisotto 提供的有益反馈。

## 封面艺术

Timothy J. Reynolds

## 相关文章

View all

Frontier risk and preparedness

SafetyOct 26, 2023

OpenAI Red Teaming Network

SafetySep 19, 2023

Confidence-Building Measures for Artificial Intelligence: Workshop proceedings

ConclusionAug 1, 2023
