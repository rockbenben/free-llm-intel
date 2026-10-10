---
vendor: openai
title: 事后经验回放
original_title: Hindsight Experience Replay
url: https://openai.com/index/hindsight-experience-replay
date: 2022-10-19
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 3472d98a1428
translator: agent
---


2017 年 7 月 5 日

论文

# 事后经验回放

阅读论文


加载中……

## 摘要

处理稀疏奖励是强化学习（RL）中最大的挑战之一。我们提出一种名为事后经验回放（Hindsight Experience Replay）的新技法，它支持从稀疏且二值的奖励中进行样本高效的采样，从而无需进行复杂的奖励工程。它可以与任意离策略（off-policy）RL 算法结合，也可视为一种隐式的课程学习（curriculum）。

我们在用机械臂操作物体的任务上验证了这一方法。具体而言，我们在三种不同任务上做了实验：推、滑、抓取放置（pick-and-place），每种情况都只使用指示任务是否完成的二值奖励。我们的消融实验表明，事后经验回放是让这些高难度环境中训练成为可能的关键要素。我们还证明，在物理仿真中训练出的策略可以部署到真实机器人上并成功完成任务。

- [学习范式](https://openai.com/research/index/?tags=learning-paradigms)

## 作者

Marcin Andrychowicz、Filip Wolski、Alex Ray、Jonas Schneider、Rachel Fong、Peter Welinder、Bob McGrew、Josh Tobin、Pieter Abbeel、Wojciech Zaremba
