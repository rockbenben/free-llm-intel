---
vendor: huggingface
title: Fetch 借助 Hugging Face on AWS 整合 AI 工具并节省 30% 开发时间
original_title: Fetch Consolidates AI Tools and Saves 30% Development Time with Hugging Face on AWS
url: https://huggingface.co/blog/fetch-eap-case-study
date: 2023-02-23
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Fetch 借助 Hugging Face on AWS 整合 AI 工具并节省 30% 开发时间

*如果你在使用 Hugging Face 和 AWS 时需要支持，请通过[这里](https://huggingface.co/contact/sales?from=support)联系我们——我们的团队会与你联系，讨论你的需求！*

## 摘要

消费者奖励公司 Fetch 开发了约 15 种不同的 AI 工具，用于接收、路由、读取、处理、分析和存储用户上传的收据。该公司的购物奖励应用拥有超过 1800 万月活跃用户。Fetch 希望重构其 AI 驱动的平台，在 AWS 及 AWS 合作伙伴 Hugging Face 的支持下，从使用第三方应用转向自研工具，以获得更好的客户洞察。消费者扫描收据——或转发电子收据——即可为其购买获得奖励积分。企业可以向用户提供特别奖励，例如购买特定产品可获得额外积分。如今公司每天可更快地处理超过 1100 万张收据，并获得更好的数据。

## Fetch 需要可扩展的方式来更快地训练 AI

[Fetch](https://fetch.com/)（前身为 Fetch Rewards）自创立以来不断成长，每月服务 1800 万活跃用户，这些用户每天扫描 1100 万张收据以赚取奖励积分。用户只需拍摄收据照片并通过公司应用上传，也可以上传电子收据。收据可以赚取积分；如果收据来自 Fetch 的品牌合作伙伴，还可能符合获得额外积分的促销活动。积分可兑换多家合作伙伴的礼品卡。但扫描只是开始。Fetch 收到收据后，必须对其进行处理：提取数据和分析结果，并归档数据与收据。公司此前一直使用运行在 AWS 上的人工智能（AI）工具完成这些工作。

公司原本使用某第三方 AI 方案处理收据，却发现得不到所需的数据洞察。Fetch 的商业伙伴想了解客户如何参与其促销活动，而 Fetch 缺乏从每天数百万张收据中提取和处理数据所需的颗粒度。"Fetch 把扫描收据这个'大脑'外包给了第三方，但只扫描是不够的，"Fetch 的计算机视觉科学家 Boris Kogan 说。"那个方案是个黑盒，我们无法控制也无法了解它做了什么，只能被动接受结果。我们无法把商业伙伴想要的信息提供给他们。"

Kogan 加入 Fetch 时肩负的使命是在公司内部建立扎实的机器学习（ML）和 AI 专业能力，并让公司完全掌握其接收的所有数据的方方面面。为此，他组建了一支工程团队来实现这一愿景。"我们的全部基础设施都运行在 AWS 上，模型训练也依赖 AWS 的产品，"Kogan 说。"团队开始打造我们自己的'大脑'时，当然首先要训练模型，我们就是在 AWS 上完成的。我们为项目预留了 12 个月，结果 8 个月就完成了，因为我们始终拥有所需的资源。"

## Hugging Face 打开黑盒

Fetch 团队通过 AWS Marketplace 上的 [Hugging Face 专家加速计划](https://aws.amazon.com/marketplace/pp/prodview-z6gp22wkcvdt2/)与 [AWS 合作伙伴](https://partners.amazonaws.com/partners/0010h00001jBrjVAAS/Hugging%20Face%20Inc) [Hugging Face](https://huggingface.co/)合作，帮助 Fetch 在扫描件上传后的流程环节解锁新工具。Hugging Face 是开源 AI 的领导者，为企业提供 AI 使用指导。包括 Fetch 在内的许多企业都在使用 Hugging Face 的 transformers，让用户可以在几分钟内训练和部署开源 ML 模型。"轻松获取 [Transformers](https://huggingface.co/docs/transformers/index) 模型正是 Hugging Face 开创的，他们在这方面非常出色，"Kogan 说。Fetch 与 Hugging Face 团队共同确定并训练了最先进的文档 AI 模型，改进了实体解析和语义搜索。

在这段合作关系中，Hugging Face 扮演顾问角色，通过知识转移帮助 Fetch 工程师更高效地使用其资源。"Fetch 已经有一支很棒的团队，"Hugging Face 机器学习工程师 Yifeng Yin 说。"他们不需要我们进来主导或搭建项目，而是想学习如何用 Hugging Face 训练他们正在构建的模型。我们教会他们使用这些资源，之后他们就自己跑通了。"在 Yifeng 的指导下，Fetch 的开发时间缩短了 30%。

由于要构建自己的 AI 和 ML 模型来替代第三方的"大脑"，Fetch 需要在切换之前确保新系统能稳定产出良好结果，且不能中断每天数百万张收据的处理流。"在上线任何东西之前，我们先搭建了一条影子管道（shadow pipeline），"Fetch 首席机器学习工程师 Sam Corzine 说。"我们把所有数据在新 ML 管道里重新处理一遍，可以对一切做审计。它以全量运行，重新处理全部 1100 万张收据并对其进行相当长时间的分析，之后数据才进入主数据字段。那时黑盒仍在主导，我们把自己的结果与它对比校验。"该方案使用 [Amazon SageMaker](https://aws.amazon.com/sagemaker/)——让企业能为任意用例构建、训练和部署 ML 模型，并配备全托管的基础设施、工具与工作流；同时使用 [AWS Inferentia](https://aws.amazon.com/machine-learning/inferentia/) 加速器，以最低成本为深度学习（DL）推理应用提供高性能。

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/llama2-non-engineers/fetch3.jpg)

## Fetch 壮大 AI 实力，延迟降低 50%，并节省成本

Fetch 对自研 ML 和 AI 能力的投入带来了多项收益，包括一定的成本节约，但更重要的是打造了更能满足客户需求的服务。"对任何应用来说，你都必须给客户一个持续回访的理由，"Corzine 说。"我们通过更快的上传处理提升了客户体验的响应速度，处理延迟降低了 50%。如果让客户等太久，他们就会流失。而客户越是用 Fetch，我们和合作伙伴就越了解什么对他们重要。通过自建模型，我们获得了前所未有的细节。"

公司现在训练一个模型只需几个小时，而过去要几天甚至几周。开发时间也缩短了约 30%。另一个重大收益是为 Fetch 建立了更稳固的基础，虽然难以量化。"依赖第三方黑盒给我们带来了相当大的业务风险，"Corzine 说。"因为有 Hugging Face 及其社区的存在，我们能够使用那些工具并与社区协作。归根结底，现在我们掌握了自己的命运。"

如今 Fetch 已从一家使用第三方 AI"大脑"的公司转变为 AI 优先的公司，正在持续提升客户服务、加深对客户行为的理解。"Hugging Face 和 AWS 提供了完成所需工作的基础设施和资源，"Kogan 说。"Hugging Face 让 transformer 模型民主化了——那些过去几乎不可能训练的模型如今人人可用。没有他们，我们做不到这一切。"

*本文转自 2024 年 2 月发表于 [AWS 官网](https://aws.amazon.com/fr/partners/success/fetch-hugging-face/)的原始文章。*
