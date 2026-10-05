---
vendor: openai
title: 面向代码合成大语言模型的危害分析框架
original_title: A hazard analysis framework for code synthesis large language models
url: https://openai.com/index/a-hazard-analysis-framework-for-code-synthesis-large-language-models
date: 2024-02-14
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# 面向代码合成大语言模型的危害分析框架

## 摘要

Codex 是一个在多种代码库上训练的大语言模型（LLM），在合成与生成代码的能力上超越了此前的最先进水平。尽管 Codex 带来诸多好处，但能够如此规模化生成代码的模型存在显著局限、对齐问题、被误用的可能，以及可能加快某些技术领域的进步速度——而这些领域本身可能带来 destabilizing（破坏稳定）的影响或误用风险。然而，此类安全影响目前尚不为人知，也有待探索。在本文中，我们概述了在 OpenAI 构建的一个危害分析框架，用以揭示部署 Codex 这类模型可能在技术、社会、政治和经济层面带来的危害或安全风险。该分析参考了一个新颖的评估框架：它衡量先进代码生成技术相对于规格提示词（specification prompts）的复杂度与表达力的能力，及其相对于人类能力对这些提示词的理解与执行水平。

**作者**：Heidy Khlaaf、Pamela Mishkin、Joshua Achiam、Gretchen Krueger、Miles Brundage
