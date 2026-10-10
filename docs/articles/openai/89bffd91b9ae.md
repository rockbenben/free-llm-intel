---
vendor: openai
title: OpenAI o3 和 o4-mini 系统卡补遗：OpenAI o3 Operator
original_title: Addendum to OpenAI o3 and o4-mini system card: OpenAI o3 Operator
url: https://openai.com/index/o3-o4-mini-system-card-addendum-operator-o3
date: 2025-05-23
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
translator: agent
body_sha: e3d667ccd610
---


May 23, 2025

Safety

Publication

# OpenAI o3 和 o4-mini 系统卡补遗：OpenAI o3 Operator

Read the System Card



2025 年 1 月，我们推出了 Operator，作为研究预览版来服务我们的 Computer Using Agent（CUA，计算机使用智能体）模型。CUA 是一个智能体模型，可以使用网络替用户执行任务。它用自己的浏览器查看网页，并像人一样通过输入、点击、滚动等方式与网页交互。

我们将把 Operator 现有的基于 GPT‑4o 的模型替换为基于 OpenAI o3 的版本。API 版本将继续基于 4o。

o3 Operator 使用与 4o 版 Operator 相同的多层安全方法，我们在最初的 [Operator 系统卡](https://cdn.openai.com/operator_system_card.pdf) 中描述过这套方法。与 o3 系列的其他模型相比，o3 Operator 针对计算机使用场景用额外的安全数据做了微调，包括专门设计用来让模型学习我们在确认与拒绝上决策边界的的安全数据集。

虽然 o3 Operator 继承了 o3 的编程能力，但它没有原生访问编程环境或终端（Terminal）的权限。


## 作者

OpenAI
