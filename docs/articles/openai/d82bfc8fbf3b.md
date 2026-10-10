---
vendor: openai
title: 机器人研究的关键要素
original_title: Ingredients for robotics research
url: https://openai.com/index/ingredients-for-robotics-research
date: 2022-10-19
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
body_sha: 3a717ac7162a
---


2018 年 2 月 26 日

Release

# 机器人研究的关键要素

查看 Gym 环境


查看 Baselines


阅读论文


Ben Barry


我们发布 8 个仿真机器人环境，以及 Hindsight Experience Replay 在 Baselines 中的实现，这些都是过去一年里为我们自己的研究开发的。我们已经用这些环境训练出能在真实物理机器人上工作的模型。同时我们还发布了一批面向机器人研究的需求清单（requests for research）。

本次发布包含 4 个使用 [Fetch](http://fetchrobotics.com/platforms-research-development/) 科研平台的环境，以及 4 个使用 [ShadowHand](https://www.shadowrobot.com/products/dexterous-hand/) 机器人的环境。这些环境里的操作（manipulation）任务比 Gym 现有的 MuJoCo 连续控制环境难得多——后者如今用近期发布的算法（比如 [PPO⁠](https://openai.com/index/openai-baselines-ppo/)）都已经能轻松解决。此外，我们新发布的环境使用真实机器人的模型，要求 agent 解决贴近现实的任务。

## 环境

加载中...

本次发布附带 8 个用于 [Gym](https://github.com/openai/gym) 的机器人环境，均使用 [MuJoCo](https://www.mujoco.org/) 物理仿真器。这些环境是：

## 目标

所有新任务都有"目标（goal）"这一概念，例如滑物（slide）任务中期望冰球停下的位置，或手中方块操作任务中方块的期望朝向。所有环境默认使用稀疏奖励：尚未达成期望目标时给 -1，达成时给 0（在一定容差内）。这与旧那批 Gym 连续控制问题所用的塑形奖励（shaped reward）形成对比，比如 [Walker2d-v2](https://github.com/openai/gym/blob/master/gym/envs/mujoco/walker2d.py) 就带了[塑形奖励](https://github.com/openai/gym/blob/master/gym/envs/mujoco/walker2d.py#L16-L18)。

每个环境我们也提供了一个稠密奖励版本。但我们认为在机器人应用中稀疏奖励更贴近现实，鼓励大家使用稀疏奖励版本。

## Hindsight Experience Replay

除了这些新的机器人环境，我们还[发布代码](https://github.com/openai/baselines)实现 [Hindsight Experience Replay](https://arxiv.org/abs/1707.01495)（简称 HER），一种能够从失败中学习的强化学习算法。我们的结果显示，HER 只靠稀疏奖励就能在多数新机器人任务上学到成功的策略。下文我们还列出了一些未来研究的潜在方向，它们有望进一步提升 HER 在这些任务上的表现。

## 理解 HER

要理解 HER 做了什么，可以放在 [FetchSlide](https://gym.openai.com/envs/FetchSlide-v0) 的语境里看：这个任务要学着把冰球滑过桌面击中目标。我们的第一次尝试极不可能成功；除非运气极好，接下来几次大概也会失败。典型的强化学习算法从这种经验里学不到任何东西，因为它们只拿到一个恒定奖励（这里是 `-1`），不含任何学习信号。

HER 把人类凭直觉就会做的事形式化，这就是它的关键洞察：虽然我们没有达成某个特定目标，但至少达成了另一个目标。那何不假装我们从一开始想要的就是现在达成目标，而不是最初设定的那个？做了这个替换之后，强化学习算法就能拿到学习信号，因为它达成了*某个*目标——哪怕不是我们本来想达成的那个。重复这个过程，我们最终就学会如何达成任意目标，包括我们真正想达成的目标。

这种做法让我们即使奖励完全稀疏、即使早期可能从未真正击中期望目标，也能学会把冰球滑过桌面。我们称之为 Hindsight Experience Replay（事后经验回放），因为它回放经验（这是 [DQN⁠](https://openai.com/index/openai-baselines-dqn/) 和 [DDPG](https://arxiv.org/abs/1509.02971) 这类 off-policy RL 算法常用的技巧）时所用的目标是事后——即回合结束之后——选定的。因此 HER 可以与任何 off-policy RL 算法组合（比如 HER 可以和 DDPG 组合，我们写作 "DDPG + HER"）。

## 结果

我们发现，在带稀疏奖励的目标型环境里，HER 表现极好。在新任务上对比 DDPG + HER 和原始 DDPG，对比涵盖每个环境的稀疏奖励版和稠密奖励版。

HandManipulateBlockRotateXYZ-v0 上四种不同配置的中位测试成功率（折线）与四分位距（阴影区域）。数据按训练轮次（epoch）绘制，每种配置汇总 5 个不同随机种子的结果。

带稀疏奖励的 DDPG + HER 显著超过所有其他配置，仅凭稀疏奖励就在这个困难任务上学到了成功策略。有意思的是，带稠密奖励的 DDPG + HER 也能学，但最终表现更差。原始 DDPG 在这两种情况下基本都学不出来。我们发现这一趋势在多数环境中普遍成立，完整结果见随附的[技术报告](https://arxiv.org/abs/1802.09464)。

### 研究需求清单：HER 版

虽然 HER 是朝"用稀疏奖励学习复杂目标型任务"（比如我们这里提出的机器人环境）迈出的有希望的一步，但它仍有很大改进空间。和我们不久前发布的 [Requests for Research 2.0⁠](https://openai.com/index/requests-for-research-2/) 类似，关于如何专门改进 HER、以及改进强化学习本身，我们有几个想法。

- **自动构造事后目标**。目前我们选事后替换目标用的是一套硬编码策略。如果这个策略能改为学出来，会很有意思。
- **无偏 HER**。目标替换以一种缺乏原理依据的方式改变了经验的分布。理论上这种偏差会导致不稳定，尽管我们在实践中没遇到。但推导出 HER 的无偏版本仍然值得期待，例如利用[重要性采样](https://en.wikipedia.org/wiki/Importance_sampling)。
- **HER + HRL**。把 HER 与分层强化学习（HRL）中一个[近期想法](https://arxiv.org/abs/1712.00948) 进一步结合会很有意思。HER 不只用于目标，也可以用于高层策略产生的动作。例如，如果高层让低层去达成目标 A，实际却达成了目标 B，我们可以假设高层一开始要的就是目标 B。
- **更丰富的价值函数**。把[近期](http://proceedings.mlr.press/v37/schaul15.pdf) [研究](https://openreview.net/forum?id=Skw0n-W0Z) 延伸一下，让价值函数以额外输入为条件（如折扣因子、成功阈值），并（也许？）也在事后对它们做替换，会很有意思。
- **更快的信息传播**。多数 off-policy 的[深度](https://www.nature.com/articles/nature14236) [强化](https://arxiv.org/abs/1509.02971) [学习](https://arxiv.org/abs/1603.00748) [算法](https://arxiv.org/abs/1801.01290) 使用目标网络来稳定训练。但变化需要时间传播，这会限制训练速度；我们在实验中发现，这往往是决定 DDPG+HER 学习速度最重要的因素。研究不带来这种减速的其他训练稳定手段会很有意思。
- **HER + 多步回报**。HER 使用的经验因为做了目标替换而极度 off-policy，这让它很难与[多步回报](https://arxiv.org/pdf/1703.01327.pdf) 一起使用。但多步回报很理想，因为它能让关于回报的信息传播得快得多。
- **On-policy HER**。目前 HER 只能配合 off-policy 算法使用，因为我们对目标做了替换，使经验变得极度 off-policy。但 [PPO](https://arxiv.org/abs/1707.06347) 这类最新的业界领先算法表现出非常诱人的稳定性。研究 HER 能否与这类 on-policy 算法结合（例如通过[重要性采样](https://en.wikipedia.org/wiki/Importance_sampling)）会很有意思，这个方向已有一些[初步结果](https://arxiv.org/abs/1711.06006)。
- **动作频率极高的 RL**。当前 RL 算法对采取动作的频率非常敏感，这也是 Atari 上通常要用 frame skip 技巧的原因。在连续控制域里，随着动作频率趋于无穷，性能会趋于零，原因有两个：探索不一致，以及需要更多次 bootstrap 才能把关于回报的信息向时间前方传播。如何设计一个样本高效的 RL 算法，让它在动作频率趋于无穷时仍能保持性能？
- **把 HER 与 RL 的最新进展结合**。近期有大量研究分别改进 RL 的不同方面。作为一个起点，HER 可以和 [Prioritized Experience Replay](https://arxiv.org/abs/1511.05952)、[分布视角 RL](https://arxiv.org/abs/1707.06887)、[熵正则化 RL](https://arxiv.org/abs/1704.06440) 或[逆向课程生成](https://arxiv.org/abs/1707.05300) 结合。

关于这些设想以及新 Gym 环境的更多信息和参考文献，可以在随附的[技术报告](https://arxiv.org/abs/1802.09464) 中找到。

## 使用目标型环境

引入"目标"这一概念需要对[现有 Gym API](https://gym.openai.com/docs) 做几处向后兼容的改动：

- 所有目标型环境都使用 `gym.spaces.Dict` 观测空间。环境应当包含期望目标，即 agent 应尝试达成的目标（`desired_goal`）、它当前实际达成的目标（`achieved_goal`），以及真正的观测（`observation`），例如机器人状态。
- 我们暴露环境的奖励函数，因此可以在改变目标后重新计算奖励。这让 HER 这类要做目标替换的算法得以实现。

下面是一个简单示例，它与其中一个新的目标型环境交互并执行目标替换：

加载中...

新的目标型环境可以直接配合现有兼容 Gym 的强化学习算法（如 [Baselines](https://github.com/openai/baselines)）使用。用 `gym.wrappers.FlattenDictWrapper` 可以把基于 dict 的观测空间压平成数组：

加载中...


## 作者

Matthias Plappert, Marcin Andrychowicz, Alex Ray, Bob McGrew, Bowen Baker, Glenn Powell, Jonas Schneider, Josh Tobin, Maciek Chociej, Peter Welinder, Vikash Kumar, Wojciech Zaremba
