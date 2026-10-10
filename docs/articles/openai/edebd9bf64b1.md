---
vendor: openai
title: 变分选项发现算法
original_title: Variational option discovery algorithms
url: https://openai.com/index/variational-option-discovery-algorithms
date: 2022-10-19
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: f8e1b64ccf3b
translator: agent
---


2018 年 7 月 26 日

论文

# 变分选项发现算法（Variational option discovery algorithms）

阅读论文

## 摘要

我们探索基于变分推断的选项（option）发现方法，并做出两项算法贡献。第一：我们揭示了变分选项发现方法与变分自编码器（VAE）之间的紧密联系，并提出 VALOR——Variational Autoencoding Learning of Options by Reinforcement——一种源自这一联系的新方法。在 VALOR 中，策略把来自噪声分布的上下文编码进轨迹，而解码器则从完整的轨迹中恢复这些上下文。第二：我们提出一种课程学习方法——每当智能体在当前上下文集合上的表现足够强（由解码器来衡量）时，智能体所见的上下文数量就会增加。我们证明，这个简单的技巧能稳定 VALOR 以及先前变分选项发现方法的训练，使单个智能体能够学到比固定上下文分布下多得多的行为模式。最后，我们研究了与变分选项发现相关的其他主题，包括这一通用方法的根本局限，以及学到的选项在下游任务上的适用性。

- [学习范式](https://openai.com/research/index/?tags=learning-paradigms)

## 作者

Joshua Achiam, Harri Edwards, Dario Amodei, Pieter Abbeel
