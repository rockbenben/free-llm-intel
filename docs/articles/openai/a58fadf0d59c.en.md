---
vendor: openai
title: PaperBench
original_title: PaperBench: Evaluating AI’s Ability to Replicate AI Research
url: https://openai.com/index/paperbench
date: 2025-04-02
lang: en
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

Evaluating AI’s Ability to Replicate AI Research.

Read paper

(opens in a new window)

View code

(opens in a new window)

We introduce PaperBench, a benchmark evaluating the ability of AI agents to replicate state-of-the-art AI research. Agents must replicate 20 ICML 2024 Spotlight and Oral papers from scratch, including understanding paper contributions, developing a codebase, and successfully executing experiments. For objective evaluation, we develop rubrics that hierarchically decompose each replication task into smaller sub-tasks with clear grading criteria. In total, PaperBench contains 8,316 individually gradable tasks. Rubrics are co-developed with the author(s) of each ICML paper for accuracy and realism. To enable scalable evaluation, we also develop an LLM-based judge to automatically grade replication attempts against rubrics, and assess our judge’s performance by creating a separate benchmark for judges. We evaluate several frontier models on PaperBench, finding that the best-performing tested agent, Claude 3.5 Sonnet (New) with open-source scaffolding, achieves an average replication score of 21.0%. Finally, we recruit top ML PhDs to attempt a subset of PaperBench, finding that models do not yet outperform the human baseline. We [open-source⁠(opens in a new window)](https://github.com/openai/preparedness/tree/main/project/paperbench) our code to facilitate future research in understanding the AI engineering capabilities of AI agents.

- [Learning Paradigms](https://openai.com/research/index/?tags=learning-paradigms)
- [2025](https://openai.com/research/index/?tags=2025)

## Authors

Giulio Starace, Oliver Jaffe, Dane Sherburn, James Aung,  Chan Jun Shern, Leon Maksin, Rachel Dias, Evan Mays, Benjamin Kinsella, Wyatt Thompson, Johannes Heidecke, Mia Glaese, Tejal Patwardhan, OpenAI
