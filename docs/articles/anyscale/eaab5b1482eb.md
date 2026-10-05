---
vendor: anyscale
title: Spotify 如何打造稳健且开发者体验无阻的 Ray 平台
original_title: How Spotify Built a Robust Ray Platform with a Frictionless Developer Experience
url: https://anyscale.com/blog/how-spotify-built-a-robust-ray-platform-with-a-frictionless-developer
date: 2023-11-09
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Spotify 如何打造稳健且开发者体验无阻的 Ray 平台

作者：Anyscale Ray Team | 2023 年 11 月 9 日

2024 年 6 月更新：Anyscale Endpoints（Anyscale 的 LLM API 服务）与 Private Endpoints（自托管 LLM）现已作为 Anyscale Platform 的一部分提供。点击[这里](https://console.anyscale.com/?utm_source=anyscale&utm_medium=blog&utm_campaign=blog_callout&utm_content=june2024_product_update_subheading)在 Anyscale 平台上开始使用。

*本文是 Ray Summit 2023 精彩回顾系列的一部分，我们总结了近期这场 LLM 开发者大会中最激动人心的演讲。*

*免责声明：摘要由 AI 根据视频转录生成，并经过人工编辑。*

## 核心要点

Spotify 打造稳健 Ray 平台、实现无摩擦开发者体验的历程，是一个关于创新与精简机器学习开发流程的励志故事。本文深入介绍他们的做法：面临的挑战、实施的解法，以及经验教训。了解 Spotify 如何利用 Kubernetes、Ray 与自定义 SDK，打造友好的云端开发环境（CDE），为 ML 工程师、研究员与数据科学家简化开发工作流。

- Spotify 用 Ray 驱动机器学习应用：个性化内容推荐、搜索排序、内容发现等。
- Spotify 在 Ray 之上构建了名为 Hendrix 的内部 ML 平台，部署在 Google Kubernetes Engine 上，为工程师提供把 ML 应用快速产品化的工具与环境。
- 新平台 Hendrix 的 SDK 内置 Ray 与 PyTorch 库，把常见 ML 任务标准化；同时利用 Hydra、DeepSpeed 等开源库。
- Spotify 构建了云端开发环境（CDE）方案，统一开发环境、规避本地配置的种种问题。它提供配备 GPU、工具自动配置好的远程云环境。
- CDE 通过消除环境问题提升生产力，提供更充裕的算力，并让背景各异的用户都能无摩擦上手。
- 关键经验：保障可用性、性能与安全；允许定制与扩展；使用 Kubernetes 并发挥其特性。
- Spotify 把 PyTorch 与 Ray 集成，用于可扩展训练、超参数调优等。Ray 生态在 Spotify 持续催生更多 ML 创新。

## Spotify 如何打造稳健且开发者体验无阻的 Ray 平台

全球音频流媒体领军者 Spotify 长期与前沿技术相伴。公司横跨 184 个市场、拥有超过 5.15 亿用户与 2.1 亿订阅者，依靠先进的机器学习应用提升用户体验、驱动创新。为此，他们踏上了一条构建稳健 Ray 平台、并使其与无摩擦开发者体验无缝融合的旅程。

本文深入剖析 Spotify 如何达成这一成就，拆解其策略的关键要素与一路积累的洞见。读完你会全面理解 Spotify 如何改造其 ML 开发流程，并可以借鉴到自己的项目里。

## 背景

Spotify 的机器学习平台在公司运营中扮演枢纽角色，支撑个性化内容推荐、搜索结果优化、内容发现等诸多应用。为支持这些 ML 计划，Spotify 的 ML 平台团队打造了名为 Hendrix 的集中式机器学习平台。

Hendrix 的关键组件之一是强大的分布式计算框架 Ray。要高效利用 Ray，Spotify 需要创建一个用户友好的云端开发环境（CDE）。挑战在于：为从 ML 工程师到数据科学家等不同背景的用户，提供统一而直白的界面。

## 愿景

Spotify 的目标很明确：简化机器学习开发流程。为此，他们构想了能为不同用户理顺工作流的 CDE。无论用户角色或背景如何，CDE 都以灵活高效的方式访问被托管的 Ray 基础设施。

本质上，愿景是创造无摩擦的开发者体验，让用户专注于自己的 ML 任务，不被搭建与配置的复杂事务拖住。

## 技术方案

Spotify 为这种无摩擦开发者体验给出的技术方案，是深思熟虑的技术组合加自研开发。关键组件如下：

### Kubernetes 上的 Ray 集群

Spotify 的机器学习平台基于 Kubernetes，GPU 节点通过 Google Kubernetes Engine（GKE）接入。他们用名为 Kubeflow 的开源 Kubernetes operator 做编排。把 Ray 集群部署在 Kubernetes 上，获得了可扩展、可维护的基础设施。

### 集成 Ray 与 PyTorch 的 Python SDK

为用户提供无缝体验，Spotify 构建了包含 Ray 与 PyTorch 库的自定义 Python SDK。该 SDK 简化了访问 Ray 基础设施的流程，加速 ML 应用开发，满足不同背景与需求的用户。

### 云端开发环境

Spotify 创建了云端开发环境（CDE），让用户在云上无缝工作。CDE 基于 Kubernetes，具备快速启动、低延迟、任意设备可用的特点。用户可以瞬间搭好配置完备的开发环境，不必再排查本地机器上的坏配置。

### 定制的 VS Code 扩展

Spotify 认识到用户对开发环境的偏好各不相同。为此他们开发了定制的 VS Code 扩展，与 Spotify 生态的其他部分集成：用户可以查询内部数据端点、运行自定义 SQL 引擎等。

### 生态支持

Spotify 也充分利用 Ray 更大的生态，集成 Hugging Face、DeepSpeed、PyG 等流行 ML 库，确保用户能获取大量工具与方案来应对各种 ML 问题。

## 经验教训

Spotify 构建无摩擦开发者体验的历程揭示了若干关键经验：

### 可用性与性能

对任何开发环境而言，高可用与快速启动时间至关重要。Spotify 强调需要一个快速、高可用的反向代理来优化用户体验。

### 定制与扩展

在个人级与仓库级配置上提供高度可定制能力很重要。用户应当能按自己的偏好个性化其环境。

### 安全与遥测

设计时必须考虑安全。实现访问控制、授权与遥测等功能，提供安全且可观察的平台。

### 效率与成本节约

精简平台以最大化效率、降低成本。实现空闲自动关停（idle shutdown）等功能，节约资源、减少开销。

### 与现有工具集成

考虑新平台如何与组织内现有工具和工作流集成。无缝集成能显著改善用户体验。

## 未来

Spotify 的无摩擦开发者体验之旅没有止步于此。他们对未来有雄心计划，包括完成在 Ray 上的 PyTorch 开发、优化 ML 计算加速器的分配、进一步把开发环境平台化，以提供更好的可访问性、可靠性与可观察性。

## 结语

Spotify 成功改造其 ML 开发流程，证明了创新与深思熟虑规划的力量。通过组合 Ray、Kubernetes 与自定义 SDK 等技术，他们打造了满足 ML 工程师、研究员与数据科学家需求的友好云端开发环境。

他们的历程得出的要点，适用于任何想精简开发工作流的人：

**简化开发流程**：尽力消除开发流程中的复杂度，让用户专注于自己的任务。

**选对技术**：选择与你的愿景和需求契合的技术与工具。

**定制与扩展**：提供选项，让用户按偏好定制环境。

**安全与遥测**：优先保障安全与监控，营造安全、可观察的环境。

**集成与扩展性**：确保平台与现有工具无缝集成，并能随组织成长而扩展。

Spotify 的历程展示了组织精简机器学习开发的潜力，途中积累的洞见对任何踏上类似转型的人都很宝贵。

从 Spotify 的故事中汲取灵感，你也能让自己的开发者体验更少摩擦、更高效、更友好，最终为你的项目与产品注入创新动力。

立即注册 [Anyscale endpoints](https://www.anyscale.com/endpoints?utm_source=anyscale&utm_campaign=ray-highlights-2023-blog)快速上手，或[联系销售](https://www.anyscale.com/signup?utm_source=anyscale&utm_campaign=ray-highlights-2023-blog)获取 Anyscale 平台的全面介绍。
