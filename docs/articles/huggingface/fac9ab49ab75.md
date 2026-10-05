---
vendor: huggingface
title: PyTorch 实现策略梯度
original_title: Policy Gradient with PyTorch
url: https://huggingface.co/blog/deep-rl-pg
date: 2022-06-30
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# PyTorch 实现策略梯度

## [Hugging Face 深度强化学习课程 🤗](https://github.com/huggingface/deep-rl-class) 第 5 单元

⚠️ 本文有**新的更新版本**，在这里 👉 [https://huggingface.co/deep-rl-course/unit1/introduction](https://huggingface.co/deep-rl-course/unit4/introduction)

*本文是深度强化学习课程的一部分。这是一门从入门到专家的免费课程。课程大纲见[这里](https://huggingface.co/deep-rl-course/unit0/introduction)* ![Thumbnail](https://huggingface.co/blog/assets/85_policy_gradient/thumbnail.gif)

⚠️ 本文有**新的更新版本**，在这里 👉 [https://huggingface.co/deep-rl-course/unit1/introduction](https://huggingface.co/deep-rl-course/unit4/introduction)

*本文是深度强化学习课程的一部分。这是一门从入门到专家的免费课程。课程大纲见[这里](https://huggingface.co/deep-rl-course/unit0/introduction)*

[在上一单元](https://huggingface.co/blog/deep-rl-dqn)中，我们学习了 Deep Q-Learning。在这个基于价值的深度强化学习算法中，我们**用深度神经网络来近似每个状态下各个可能动作的 Q 值。**

事实上，从课程开始到现在，我们只研究了基于价值的方法——**先估计一个价值函数，作为寻找最优策略的中间步骤。**

因为在基于价值的方法中，**π 只是因为动作价值估计而存在——策略不过是一个给定状态选择价值最高动作的函数**（例如贪心策略）。

而在基于策略的方法中，我们要直接优化策略，**不需要学习价值函数这个中间步骤。**

所以今天，**我们将学习第一个基于策略的方法**：Reinforce，并用 PyTorch 从零实现它。之后会在 CartPole-v1、PixelCopter 和 Pong 上检验它的鲁棒性。

开始吧！

- [什么是策略梯度方法？](https://huggingface.co/blog/deep-rl-pg#what-are-policy-gradient-methods) [策略梯度概览](https://huggingface.co/blog/deep-rl-pg#an-overview-of-policy-gradients) [策略梯度方法的优点](https://huggingface.co/blog/deep-rl-pg#the-advantages-of-policy-gradient-methods) [策略梯度方法的缺点](https://huggingface.co/blog/deep-rl-pg#the-disadvantages-of-policy-gradient-methods)
- [Reinforce（蒙特卡洛策略梯度）](https://huggingface.co/blog/deep-rl-pg#reinforce-monte-carlo-policy-gradient)

## 什么是策略梯度方法？

策略梯度（Policy-Gradient）是基于策略方法（Policy-Based Methods）的一个子类。后者是一类算法，**目标是用多种技术直接优化策略而不使用价值函数**。策略梯度方法与一般基于策略方法的区别在于：它旨在**用梯度上升估计最优策略的权重**，从而直接优化策略。

### 策略梯度概览

为什么在策略梯度方法中，我们要用梯度上升估计最优策略的权重来直接优化策略？

记住，强化学习的目标是**找到最优行为策略，最大化期望累计奖励。**

我们还需要记住，策略是一个**给定状态、输出动作概率分布**的函数（在我们的例子中是随机策略）。

策略梯度的目标是通过调优策略来控制动作的概率分布，让**好的动作（能最大化回报的动作）在未来被更频繁地采样。**

看一个简单例子：

- 让策略与其环境交互，收集一个 episode。
- 然后看这个 episode 的奖励总和（期望回报）。如果总和为正，我们**认为 episode 中采取的动作是好的**：因此，我们想对每个（状态，动作）对提高 P(a|s)（在该状态下采取该动作的概率）。

策略梯度算法（简化版）看起来是这样：

但 Deep Q-Learning 已经很棒了！为什么还要用策略梯度方法？

### 策略梯度方法的优点

相比 Deep Q-Learning 方法有多重优势，我们来看几个：

- 集成简单：**我们可以直接估计策略，无需存储额外数据（动作价值）。**
- 策略梯度方法可以**学习随机策略，而价值函数做不到**。

这带来两个结果：

a. 我们**不需要手动实现探索/利用的权衡**。由于输出的是动作概率分布，智能体会**在不总走同一条轨迹的情况下探索状态空间**。

b. 我们还摆脱了**感知别名（perceptual aliasing）**问题。感知别名指两个状态看起来（或实际上）相同，却需要不同的动作。

举个例子：我们有一个智能吸尘器，目标是吸走灰尘、避免伤害仓鼠。

我们的吸尘器只能感知墙在哪里。

问题在于，两个红色格子是别名状态，因为智能体在其中都感知到上墙和下墙。

在确定性策略下，策略要么在红色状态时向右、要么向左。无论哪种都会**让智能体卡住，永远吸不到灰尘**。

在基于价值的 RL 算法中，我们学到的是准确定性策略（"epsilon 贪心策略"）。结果是我们的智能体可能花很长时间才能找到灰尘。

另一方面，最优随机策略会在灰色状态随机向左或向右。因此，**它不会卡住，并以高概率到达目标状态**。

- 策略梯度在**高维动作空间和连续动作空间**中更有效

Deep Q-learning 的问题在于，它们的**预测在每个时间步、给定当前状态下，为每个可能动作打分（最大期望未来奖励）**。

但如果有无限种可能的动作呢？

例如，自动驾驶汽车在每个状态下都有（近乎）无限的动作选择（方向盘转 15°、17.2°、19.4°、按喇叭等）。我们需要为每个可能动作输出一个 Q 值！而对连续输出取最大动作本身就是一个优化难题！

而策略梯度直接输出**动作的概率分布**。

### 策略梯度方法的缺点

当然，策略梯度方法也有缺点：

- **策略梯度常常收敛到局部极大值而非全局最优。**
- 策略梯度是一步一步前进的，**训练时间可能更长（效率低）。**
- 策略梯度可能方差较大（可用 baseline 解决）。

👉 想深入了解策略梯度方法的优缺点，[可以看这个视频](https://youtu.be/y3oqOjHilio)。

了解了策略梯度的全貌及其优缺点后，**我们来学习并实现其中一个算法**：Reinforce。

## Reinforce（蒙特卡洛策略梯度）

Reinforce，也叫蒙特卡洛策略梯度，**使用整个 episode 的估计回报来更新策略参数** θ。

我们有带参数 θ 的策略 π。这个 π 给定状态，**输出动作的概率分布**。

其中 πθ(at∣st) 表示在策略下，智能体从状态 st 选择动作 at 的概率。

**但我们如何知道策略好不好？**我们需要一种衡量方式，为此定义一个分数/目标函数 J(θ)。

分数函数 J 就是期望回报：

记住，策略梯度可以看作一个优化问题。所以我们必须找到最佳参数 θ 来最大化分数函数 J(θ)。

为此我们使用[策略梯度定理](https://www.youtube.com/watch?v=AKbX1Zvo7r8)。这里不展开数学细节，感兴趣请看[这个视频](https://www.youtube.com/watch?v=AKbX1Zvo7r8)。

Reinforce 算法如下运行：循环：

- 使用策略 πθ 收集一个 episode τ
- 用该 episode 估计梯度 ĝ = ∇θJ(θ)

- 更新策略权重：θ ← θ + αĝ

我们可以这样解读：

- ∇θlogπθ(at∣st) 是从状态 st 选择动作 at 的（对数）概率**增长最快的方向**。=> 它告诉我们：若想增加/减小在状态 st 选择动作 at 的对数概率，**应该如何改变策略的权重**。
- R(τ)：评分函数。如果回报高，就抬升各（状态，动作）组合的概率；如果回报低，就压低它们的概率。

## 学完 Reinforce 背后的理论，**你已经准备好用 PyTorch 编写你的 Reinforce 智能体了**。并将在 CartPole-v1、PixelCopter 和 Pong 上检验其鲁棒性。

从这里开始教程 👉 [https://colab.research.google.com/github/huggingface/deep-rl-class/blob/main/unit5/unit5.ipynb](https://colab.research.google.com/github/huggingface/deep-rl-class/blob/main/unit5/unit5.ipynb)

比较你和同学结果的排行榜 🏆 👉 [https://huggingface.co/spaces/chrisjay/Deep-Reinforcement-Learning-Leaderboard](https://huggingface.co/spaces/chrisjay/Deep-Reinforcement-Learning-Leaderboard)

 ![Environments](https://huggingface.co/blog/assets/85_policy_gradient/envs.gif)

祝贺你完成这一章！信息量很大。也祝贺你完成教程——你用 PyTorch 从零写出了第一个深度强化学习智能体，并分享到了 Hub 🥳。

**如果你对这一切仍感困惑，这很正常**。对我以及所有学过 RL 的人来说都是一样。

请花时间真正消化这些材料再继续。

不妨在其他环境中训练你的智能体。**最好的学习方法就是自己动手尝试！**

如果想深入，我们在课程大纲中公布了延伸阅读 👉 **[https://github.com/huggingface/deep-rl-class/blob/main/unit5/README.md](https://github.com/huggingface/deep-rl-class/blob/main/unit5/README.md)**

下一单元，我们将学习基于策略与基于价值方法的结合——Actor-Critic 方法。

别忘了分享给想学习的朋友 🤗！

最后，我们希望**根据你的反馈持续改进和更新课程**。如有建议，请填写这个表单 👉 **[https://forms.gle/3HgA7bEHwAmmLfwh9](https://forms.gle/3HgA7bEHwAmmLfwh9)**

### **继续学习，保持精彩 🤗，**
