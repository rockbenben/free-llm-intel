---
vendor: openai
title: OpenAI Gym 公测版
original_title: OpenAI Gym Beta
url: https://openai.com/index/openai-gym-beta
date: 2022-10-19
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 87c456b2cd94
translator: agent
---

OpenAI

2016 年 4 月 27 日


# OpenAI Gym 公测版

阅读论文


加载中……

我们发布 OpenAI Gym 的公开测试版，这是一个用于开发和比较强化学习（RL）算法的工具包。它由一套不断扩充的环境（从仿真机器人到雅达利游戏）以及一个用于比较和复现结果的网站组成。

OpenAI Gym 兼容用任何框架编写的算法，比如 [Tensorflow](https://www.tensorflow.org/) 和 [Theano](https://github.com/Theano/Theano)。环境是用 Python 写的，但我们很快会让它们能从任何语言方便地调用。我们最初打造 OpenAI Gym 是为了加速我们自己的 RL 研究。我们希望它对更广泛的社区同样有用。

## 上手

如果你想立刻上手，可以跟着我们的[教程](https://gym.openai.com/docs)走一遍。你也可以边学边帮忙，[复现一个结果](https://gym.openai.com/evaluations/eval_lEi8I8v2QLqEgzBxcvRIaA)。

## 为什么是 RL？

强化学习（RL）是机器学习中关注决策与运动控制的分支。它研究一个智能体如何学会在复杂、不确定的环境中达成目标。它之所以令人兴奋，有两个原因：

- **RL 非常通用，涵盖一切需要做一连串决策的问题**：比如控制机器人的电机让它能[跑](https://gym.openai.com/envs/Humanoid-v0)和[跳](https://gym.openai.com/envs/Hopper-v0)、做定价和库存管理这类商业决策，或者玩[电子游戏](https://gym.openai.com/envs#atari)和[棋盘游戏](https://gym.openai.com/envs#board_game)。RL 甚至能应用于带有[序列](http://arxiv.org/abs/1511.06732)[或](http://arxiv.org/abs/0907.0786)[结构化](http://arxiv.org/abs/1601.01705)输出的监督学习问题。
- **RL 算法已经在许多高难度环境里取得了不错的成绩**。RL 历史悠久，但在深度学习近期进展之前，它需要大量针对具体问题的工程。DeepMind 的[雅达利成果](https://deepmind.com/dqn.html)、来自 [Pieter Abbeel⁠](https://openai.com/index/welcome-pieter-and-shivon/) 团队的 [BRETT](http://news.berkeley.edu/2015/05/21/deep-learning-robot-masters-skills-via-trial-and-error/)，以及 [AlphaGo](https://googleblog.blogspot.com/2016/01/alphago-machine-learning-game-go.html) 都用到了深度 RL 算法，这些算法对环境做了很少的假设，因此可以迁移到其他场景。

不过，RL 研究也被两个因素拖慢了：

- **需要更好的基准**。在监督学习里，进展是由像 [ImageNet](http://www.image-net.org/) 这样的大规模标注数据集驱动的。在 RL 里，最接近的等价物会是一大批多样化的环境。然而现有的开源 RL 环境集合种类不够丰富，而且常常连搭建和使用都很费劲。
- **论文中所用环境缺乏标准化**。问题定义上细微的差别，比如奖励函数或动作集合，都可能大幅改变任务的难度。这个问题让复现已发表研究、比较不同论文的结果变得困难。

OpenAI Gym 就是同时解决这两个问题的一次尝试。

## 环境

OpenAI Gym 提供一套多样化的环境，从简单到困难，涉及许多不同类型的数据。我们一开始包含以下这些集合：

- [经典控制](https://gym.openai.com/envs#classic_control)和 [玩具文字](https://gym.openai.com/envs#toy_text)：完成小规模任务，大多来自 RL 文献。它们在这里是为了帮你入门。
- [算法](https://gym.openai.com/envs#algorithmic)：执行计算，比如多位数相加、反转序列。也许有人会说这些任务对计算机来说很简单。难点在于纯粹从样例中学出这些算法。这些任务有个好性质：通过改变序列长度就能方便地调节难度。
- [雅达利](https://gym.openai.com/envs#atari)：玩经典雅达利游戏。我们集成了 [Arcade Learning Environment](http://www.arcadelearningenvironment.org/)（它对强化学习研究影响很大），并以[易于安装](https://github.com/openai/gym#atari)的形式提供。
- [棋盘游戏](https://gym.openai.com/envs#board_games)：在 9x9 和 19x19 棋盘上玩围棋。双人对弈与我们收录的其他设定有本质不同，因为有一个对手在和你博弈。在我们的首个版本里，提供了一个由 [Pachi](http://pachi.or.cz/) 提供的固定对手，我们之后可能加入其他对手（欢迎提交补丁！）。我们也很可能扩展 OpenAI Gym，让多玩家游戏获得一等公民支持。
- [2D 和 3D 机器人](https://gym.openai.com/envs#mujoco)：在仿真中控制机器人。这些任务使用 [MuJoCo](https://www.mujoco.org/) 物理引擎，它就是为快速而精确的机器人仿真设计的。其中收录了 UC Berkeley 研究者近期一个[基准](http://arxiv.org/abs/1604.06778)里的一些环境（他们正好今年夏天[加入我们⁠](https://openai.com/index/team-plus-plus/)）。MuJoCo 是专有软件，但提供[免费试用](https://www.roboti.us/trybuy.html)许可。

随着时间推移，我们计划大幅扩充这套环境集合，非常欢迎社区贡献。

每个环境都有版本号（比如 [**Hopper-v0**](https://gym.openai.com/envs/Hopper-v0)）。如果我们需要改动某个环境，就会提升版本号，定义一个全新的任务。这保证了在某个特定环境上的结果始终可比。

## 评测

我们让[上传结果](https://gym.openai.com/docs#uploading)到 OpenAI Gym 变得很简单。不过我们选择不做传统的排行榜。对研究而言重要的不是你的分数（针对特定任务过拟合或手工拼凑解法是可能的），而是你方法的通用性。

我们一开始会维护一份[精选清单](https://gym.openai.com/docs#review)，收录那些对算法能力说明了有趣内容的贡献。长期来看，我们希望这种筛选是一项社区协作，而不是由我们独占的东西。具体的细节我们必然要在实践中逐步摸索，也非常欢迎你的[帮助](https://gym.openai.com/docs#help)。

我们希望 OpenAI Gym 从一开始就是一项社区事业。我们已经和一些伙伴合作，围绕 OpenAI Gym 整理资源：

- [NVIDIA](http://www.nvidia.com/)：与 John 的技术[问答](https://devblogs.nvidia.com/parallelforall/train-reinforcement-learning-agents-openai-gym)。
- [Nervana](http://www.nervanasys.com/)：一个 [DQN OpenAI Gym 智能体](http://www.nervanasys.com/openai)的实现。
- [亚马逊云服务（AWS）](https://aws.amazon.com/)：为部分 OpenAI Gym 用户提供 250 美元的抵扣券。如果你有一个能证明算法潜力的评测、却受资源限制无法放大规模，[给我们发邮件⁠](mailto:gym@openai.com)领一张抵扣券。（先到先得！）

在公测期间，我们在收集反馈，看怎样把它做成一个对研究更好的工具。如果你想帮忙，可以在每个环境上试着推进业界最先进水平、复现别人的结果，甚至实现你自己的环境。也欢迎加入我们的[社区聊天](https://gym.openai.com/chat)！

- [仿真环境](https://openai.com/research/index/?tags=simulated-environments)
- [探索与游戏](https://openai.com/research/index/?tags=exploration-game)
- [软件与工程](https://openai.com/research/index/?tags=software-engineering)
- [机器人](https://openai.com/research/index/?tags=robotics)
- [学习范式](https://openai.com/research/index/?tags=learning-paradigms)
- [社区与协作](https://openai.com/research/index/?tags=community-collaboration)

## 作者

Greg Brockman
