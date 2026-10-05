---
vendor: openai
title: PaperBench：评估人工智能复制人工智能研究的能力
original_title: PaperBench: Evaluating AI’s Ability to Replicate AI Research
url: https://openai.com/index/paperbench
date: 2025-04-02
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: d2b30f718bfc
---

OpenAI

April 2, 2025

Publication

Release

# PaperBench

评估人工智能复制人工智能研究的能力。

Read paper

(opens in a new window)

View code

(opens in a new window)

我们推出 PaperBench，一个评估 AI 智能体复制最先进 AI 研究能力的基准。智能体必须从零开始复制 20 篇 ICML 2024 Spotlight 和 Oral 论文，包括理解论文贡献、开发代码库并成功执行实验。为了客观评估，我们制定了评分量规（rubrics），把每一项复制任务分层拆解为具有明确评分标准的更小子任务。PaperBench 总共包含 8,316 项可独立评分的任务。为确保准确与真实，量规与每篇 ICML 论文的作者共同制定。为了实现可扩展的评估，我们还开发了一个基于 LLM 的评审者，可根据量规自动为复制尝试打分，并通过单独构建一个针对评审者的基准来评估该评审者的表现。我们在 PaperBench 上评估了若干前沿模型，发现表现最好的测试智能体——搭配开源脚手架的 Claude 3.5 Sonnet (New)——平均复制得分为 21.0%。最后，我们邀请顶尖 ML 博士在 PaperBench 的一个子集上尝试，发现模型尚未超过人类基线。我们已 [开源⁠(opens in a new window)](https://github.com/openai/preparedness/tree/main/project/paperbench) 代码，以促进对未来研究 AI 智能体 AI 工程能力的理解。

- [Learning Paradigms](https://openai.com/research/index/?tags=learning-paradigms)
- [2025](https://openai.com/research/index/?tags=2025)

## 作者

Giulio Starace, Oliver Jaffe, Dane Sherburn, James Aung,  Chan Jun Shern, Leon Maksin, Rachel Dias, Evan Mays, Benjamin Kinsella, Wyatt Thompson, Johannes Heidecke, Mia Glaese, Tejal Patwardhan, OpenAI
