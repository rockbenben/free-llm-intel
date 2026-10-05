---
vendor: openai
title: Spinning Up in Deep RL：工作坊回顾
original_title: Spinning Up in Deep RL: Workshop review
url: https://openai.com/index/spinning-up-in-deep-rl-workshop-review
date: 2020-06-20
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Spinning Up in Deep RL：工作坊回顾

2 月 2 日，我们举办了首届 Spinning Up 工作坊，这是 OpenAI 新教育计划的一部分。

我们在办公室接待了约 90 位参与者，并通过直播吸引了近 300 人加入。参与者背景多元，涵盖学术界、软件工程、数据科学、机器学习工程、医学和教育等领域。本次工作坊依托我们的 [Spinning Up in Deep RL⁠](https://openai.com/index/spinning-up-in-deep-rl/) 教育资源包，进一步深入探讨了 RL 算法设计、机器人以及构建安全 AI 系统。

## 打造教育工具

OpenAI 教育工作的目标之一，是帮助人们培养参与 AI 研究与开发所需的技能——尤其是深度强化学习，这是 OpenAI 的核心研究方向。基于我们与 [Scholars⁠（在新窗口中打开）](https://blog.openai.com/openai-scholars-2018-final-projects/) 和 [Fellows⁠（在新窗口中打开）](https://blog.openai.com/openai-summer-fellows-2018/) 共事的经验，我们发现技能培养的关键要素是：

- 一套灵活的课程体系，包含核心材料与研究前沿综述，
- 导师辅导和与专家的讨论，
- 让学生做难度恰当、能促进成长的项目。

OpenAI 教育工作的挑战在于如何规模化地提供这些要素。课程内容的规模化分享相对容易，但导师辅导和项目指导却难以放大。我们的工作假设是：工作坊也许正好能做到这一点。首届 Spinning Up 工作坊给了我们若干积极信号，表明这是一个有用的方向，我们很高兴分享所学。

## 人群

我们在办公室接待了约 90 人，并通过直播带动了近 300 人参与。来宾背景十分广泛，包括学术研究、软件工程、数据科学、ML 工程、医学和教育。群体的 ML 经验差异相当大，从“几乎没有”到“自己做过 Dota bot！”都有。

来自全球有超过 500 人申请参加本次工作坊。由于场地限制，很遗憾我们无法邀请所有人到场，但我们希望借未来的活动持续与社区互动。

## 演讲

工作坊以三小时的演讲开场。[Joshua Achiam⁠（在新窗口中打开）](https://twitter.com/jachiam0) 首先阐述了强化学习的概念基础，并概览了各类 RL 算法。想学习这部分材料，请查看 [Spinning Up in Deep RL⁠（在新窗口中打开）](https://blog.openai.com/spinning-up-in-deep-rl/)。

Matthias Plappert 介绍了 OpenAI [近期⁠（在新窗口中打开）](https://blog.openai.com/learning-dexterity/)的[工作⁠（在新窗口中打开）](https://arxiv.org/abs/1808.00177)：在仿真中训练灵巧的机械手，以在真实世界操纵物体。域随机化（domain randomization）、循环神经网络和大规模分布式训练，是弥合该任务“sim2real”差距的必要要素。

OpenAI 安全团队负责人 Dario Amodei 概述了 AI 安全领域的问题和该领域的[近期⁠（在新窗口中打开）](https://blog.openai.com/amplifying-ai-training/)[工作⁠（在新窗口中打开）](https://blog.openai.com/debate/)。他描述了核心安全难题：正确规定 agent 的行为非常困难！我们很容易在无意间给 agent 提供激励，使其做出并非我们期望的行为；而当 agent 非常强大时，这可能很危险。Dario 还介绍了 OpenAI 与 DeepMind 合作者为解决这一问题开展的[工作⁠（在新窗口中打开）](https://blog.openai.com/deep-reinforcement-learning-from-human-preferences/)——从人类偏好中学习奖励函数，而非人工设计。

## 下午

工作坊下午延续了半结构化的动手与分组环节。参与者可以向我们的志愿者团队请教项目构想和研究建议，志愿者包括 [Amanda Askell⁠（在新窗口中打开）](https://twitter.com/AmandaAskell)、[Alex Ray⁠（在新窗口中打开）](https://twitter.com/machinaut)、[Daniel Ziegler⁠（在新窗口中打开）](https://www.linkedin.com/in/daniel-ziegler-b4b61882)、[Dylan Hadfield-Menell⁠（在新窗口中打开）](https://twitter.com/dhadfieldmenell)、[Ethan Knight⁠（在新窗口中打开）](https://github.com/hyperdo?tab=repositories)、[Karl Cobbe⁠（在新窗口中打开）](https://twitter.com/karlcobbe)、[Matthias Plappert⁠（在新窗口中打开）](https://twitter.com/mplappert) 和 [Sam McCandlish⁠（在新窗口中打开）](https://www.linkedin.com/in/sam-mccandlish)。

分组环节成为下午的最大亮点。上午的演讲覆盖 RL 的概念基础，而分组环节旨在帮助参与者提升实现能力与研究技能。

第一节，Karl Cobbe 介绍了 [TensorFlow⁠（在新窗口中打开）](https://www.tensorflow.org/)——深度学习研究的关键库。第二节“一起写 DQN”，Daniel Ziegler 带领参与者一步步实现一个深度 RL 算法。第三节“高级 RL 问答”，Joshua Achiam 介绍了 RL 的最新研究前沿，并就如何做 RL 研究回答听众提问。

## 我们的收获

这是我们对工作坊形式的第一次实验，总体结果令我们满意。特别是，能与这样一群能力强、热情高的参与者直接共事，让我们很有成就感。这次体验加上群体反馈，让我们清楚知道未来的工作坊该保留什么、该改什么。

**奏效的地方**：我们请参与者说出各自的最大收获，以下回答颇具代表性：

> “在非常安全友好的环境里学到了海量东西，大家的学习水平基本一致。”

> “能得到一对一帮助、和真正懂行的人共度‘结对编程’般的时间，我认为这无比有益。志愿者们的热情也非常高，我深受鼓励，敢于开口求助。”

这类反馈让我们感到，工作坊形式在提供“导师辅导和与专家讨论”这一维度上大放异彩。

**可以改进的地方**：我们询问参与者觉得哪些地方本可以做得不同、以提升体验，收到的回答如：

> “我希望有一个环节介绍可供选择的项目，按经验水平分类。”

> “把工作坊延长到两天。”

许多参与者表示，黑客时段要么不确定该做什么，要么时间不足以在自己的项目上取得明显进展。

我们认为这类反馈表明：一天制工作坊不足以让学员在 RL 中“做难度恰当、能促进成长的项目”。未来我们会考虑举办更长的活动来实现该目标。这反馈还提示我们应更多打造“开箱即用”的 RL 项目，让参与者能立即上手。

**还有什么？** 除技术内容外，营造互助、包容的环境也是我们最挂心的事，参与者告诉我们这对其体验很重要。一条反馈写道：

> “这是我在硅谷参加的第一场非纯女性社交活动，现场约一半是女性。一开始震惊到我以为走错了房间。由于性别均衡，社交明显更轻松，为此感谢你们。”

## 下一步

OpenAI 的[章程⁠（在新窗口中打开）](https://blog.openai.com/openai-charter/)赋予我们“创建一个全球社区，共同应对 AGI 的全球挑战”的使命，我们将继续发展 OpenAI 的教育工作以服务这一目标。包括继续建设 [Spinning Up in Deep RL⁠（在新窗口中打开）](https://spinningup.openai.com/en/latest/) 这样的资源，以及举办更多本次 Spinning Up 工作坊这样的活动。我们正与伯克利的 [CHAI⁠（在新窗口中打开）](https://humancompatible.ai/) 筹划第二期工作坊，预计很快正式公布。

如果你愿意协助我们做 RL 研究或教授 AI，欢迎联系我们！[我们在招聘⁠](https://openai.com/careers/)。

*感谢 Maddie Hall 和 Loren Kwan 共同组织本次活动；感谢 Ian Atha 负责直播和录制课程，并帮助参与者解决 Python 和 TensorFlow 问题；感谢* [*Blake Tucker*⁠（在新窗口中打开）](https://www.blaketucker.com/) *的拍摄与摄影！*

## 作者

Joshua Achiam
