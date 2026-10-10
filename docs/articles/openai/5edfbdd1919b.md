---
vendor: openai
title: 用时间分段模型进行预测与控制
original_title: Prediction and control with temporal segment models
url: https://openai.com/index/prediction-and-control-with-temporal-segment-models
date: 2022-04-13
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# 用时间分段模型进行预测与控制

阅读论文

## 摘要

我们提出一种方法，基于对状态与动作的时间分段（temporal segment）进行建模的深度生成模型，来学习复杂非线性系统的动力学。与在单个离散时间步上运作的动力学模型不同，我们学习的是在未来状态轨迹上的分布——该分布以过去状态、过去动作和规划中的未来动作轨迹为条件，同时我们还学习动作轨迹上的潜变量先验。我们的方法以卷积自回归模型和变分自编码器为基础。它对复杂随机系统能够在长时间跨度上做出稳定而准确的预测，有效表达不确定性，并建模碰撞、感知噪声和动作延迟的影响。学得的动力学模型和动作先验可用于端到端、完全可微的轨迹优化以及基于模型（model-based）的策略优化，我们用它们评估了方法的性能与样本效率。

## 作者

Nikhil Mishra, Pieter Abbeel, Igor Mordatch
