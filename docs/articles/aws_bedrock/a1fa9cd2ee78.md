---
vendor: aws_bedrock
title: Built from the inside out: How AWS Professional Services became a frontier team first
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/built-from-the-inside-out-how-aws-professional-services-became-a-frontier-team-first
date: 2026-06-12
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 76dc429ad5e2
---

# 由内而外构建：AWS Professional Services 如何率先成为 frontier team

[AWS Professional Services](https://aws.amazon.com/professional-services/)（AWS ProServe）把项目周期从数月压缩到数天，靠的不是在既有流程上叠加人工智能（AI）工具，而是从根本上重建我们交付的方式，由内而外。这一转变与我的同事 Swami Sivasubramanian 在 [How Frontier Teams Are Reinventing AI-Native Development](https://aws.amazon.com/blogs/machine-learning/how-frontier-teams-are-reinventing-ai-native-development/) 中所描述的相符：真正的生产力提升来自重新构想软件如何被构建，而不是把 AI 层层叠加到既有工作流之上。

在本文中，我会分享 AWS ProServe 如何成为一支 frontier team、支撑这一转变的做法，以及你的工程组织可以从我们的经验中借鉴什么。

## 一个已经做过这件事的合作伙伴

建设一支 frontier team 是每个组织都能做到的事。对于希望加速的客户，AWS ProServe 是一个合作伙伴，其顾问已经把 AI 原生开发融入到每天的工作方式之中。

AI 原生开发的节奏，并不是传统咨询节奏所能承载的。过去要跨越数月的工作被压缩到数天，节奏也随之改变：更紧的循环、更快的反馈、更多决策在构建过程中就地做出。要帮助客户以这种节奏运转，顾问必须清楚哪些决策可以快速推进、哪些需要谨慎的人工判断，以及在执行提速时如何保持高质量。这种直觉只能从亲手做事中长出来。

我们的驱动力与 Swami 所描述的相同：把顾问从非编码的开销中解放出来——文档、协调、状态汇报、重复性的脚手架工作，这些占据了每一次项目的大部分时间。这让人的判断力得以集中在真正能改变结果的地方。于是我们做了 frontier team 会做的事：我们投入 agent context，围绕 agent 擅长的事重构工作，并不再把 AI 当作助手，而是开始把它当作底座。

## 我们的 pathfinder 团队：APEX

Swami 的博文描述了 Amazon 团队走向 AI 原生开发的三种路径：pathfinder 计划、结构化 sprint，以及就地实验。AWS ProServe 是从 pathfinder 起步的。

我们的 Agentic AI ProServe Experiences 团队（APEX）只有一项使命：重新设计 ProServe 的交付方式。[APEX 构建了 ProServe Delivery Agent](https://aws.amazon.com/blogs/machine-learning/accelerate-enterprise-solutions-with-agentic-ai-powered-consulting-introducing-aws-professional-service-agents/)，这是一个多 agent 系统，覆盖需求、架构验证、实现、安全评审、测试与部署。一个 supervisor agent 负责编排跨各生命周期阶段的专用 sub-agent。

ProServe 通过 Delivery Agent 落地 **AI-DLC**，即 **AI-Driven Development Lifecycle（AI 驱动的开发生命周期）**。AI-DLC 由 AWS 一线团队打造，并在数百场动手实践的客户工作坊中开发与打磨。AI 原生开发是地基，而 AI-DLC 则是 AWS 构建的流程，用来把 AI 原生开发贯穿到我们自己和客户的完整交付生命周期中。

APEX 在自己的生产负载上验证了这套模式。如今 Delivery Agent 在全球各地的项目中与人类顾问并肩工作，APEX 验证过的模式正在成为 ProServe 的默认交付动作。这不是试点，这就是我们大规模交付的方式。

## 我们如何重新设计交付动作

过去，一个典型的 ProServe 项目遵循人们熟悉的咨询节奏：用长篇文档做发现，在研讨会上辩论架构决策，按 sprint 节奏推进实现，测试与安全放在阶段边界。每一次交接都会引入延迟，每一份制品都只为给人阅读而写。

这次重新设计改变了每一步。需求从散文式描述转为结构化 spec，人和 agent 都能读，需求由此成为事实来源而不再是副产品。架构标准与过往项目的经验被固化成 steering 文件，供 agent 持续取用。实现方式从贡献者串行处理工单，转变为顾问把范围明确的任务并行喂给多个 agent。测试与安全评审被移入构建循环：agent 在本地验证输出，并在任何人工评审开始之前自行纠正。状态汇报与协调开销基本消失。

最终效果是连续流动，人的判断集中在优先级排序、验证与高风险决策上。

[![重新设计的 ProServe 交付动作示意图：从需求到部署的连续流动，agent 处理脚手架工作，人专注于优先级排序、验证与高风险决策](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/06/11/ML-21052-1.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/06/11/ML-21052-1.png)

## 用 Delivery Agent 构建 Delivery Agent

APEX 用与提供给客户相同的 AI 原生做法来构建 Delivery Agent。一个功能需求进入系统，agent 生成结构化工单、产出代码，并通过我们与 GitLab 集成的 DevOps pipeline 运行自动化测试。经人工评审与批准后，变更即可部署。

人负责判断：排优先级、验证质量、批准高风险决策。Agent 负责脚手架。低风险决策自动执行。人工卡点集中在真正需要判断的地方。

随着 ProServe 各交付团队在项目中采用 Delivery Agent，他们会把经验反馈回来，让它每做一个项目就更锋利。这就是 Amazon 构建的方式：我们运行自己的产品，看到哪里坏了，然后修好它。

## 让这一切奏效的五项实践

Swami 博文中的五项实践，如今定义了我们在 ProServe 内部如何运行 AI-DLC：

**慢下来，才能快起来。** Frontier team 在加速之前先投入：建立 agent context、把做法标准化，然后速度才会产生复利。APEX 做过这一次投入，因此我们直接把这身肌肉记忆传递出去，而不必让每个客户从零开始。

**在 agent context 上重投入。** 在每一个项目中，steering 文件与架构标准都是头等制品。上下文越丰富，agent 能安全行使的自主性就越大。

**喂给 agent，而不是盯着它。** 构建者维护一份稳定的、范围明确的任务 backlog，并行运行多个 agent，并异步评审输出。

**把 spec 作为事实来源。** Spec 驱动开发是默认工作流。Spec 不是文档，而是 agent 构建时要遵守的契约。

**把测试左移。** Agent 在本地验证，并在输出到达人工评审者之前自行纠正。

## 客户环境中的 AI 原生交付

在客户项目中，Delivery Agent 与人类顾问协同工作。双方一起走完从规划到部署的完整生命周期，对齐客户选定的业务成果。主导原则是：人提供意图，AI 创造，人来验证。

客户保留基础模型的选择权，并可以用自己的数据和工具扩展系统。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/06/22/AI-DLC_Architecture-blog.jpg)

## 先行一步的收获

校准不是可选项，但你不需要从零开始。团队需要时间来建立对“agent 擅长什么”的信任、把复杂工作拆解为可验证的任务，并为 AI 消费而重构制品。我们在项目过程中直接把这身肌肉记忆传递出去，缩短这条曲线。

工作流是常量，工具只是使能器。我们使用 Kiro、Amazon Bedrock AgentCore 与 Strands，但真正创造生产力增益的不是这套技术栈。只有当工作流围绕工具被重新设计时，工具才会产生复利。

对齐成果。传统咨询按时间和材料计费，这会激励拉长周期而非放大影响。我们转向与已上线交付的业务成果挂钩的固定价格项目。当商业模式与客户需求对齐时，其余的一切都会随之而来。

## 真实成果

*“我们采用了 Amazon Application Recovery Controller（ARC）新增的 Region Switch 功能，以简化我们的多区域容灾方案。Region Switch 用声明式计划取代了自定义的故障转移编排，这些计划并行协调了我们各项服务的扩缩容、数据库切换与 DNS 路由。Kiro 配合 AWS Professional Services Delivery Agent，把原本需要数周的 backlog 创建压缩到数小时，代码交付提速 60%，并在每个交付物上强制保持一致的质量。我们的 Region Switch 测试按计划执行，我们得以在备用区域运行。这让我们对这套做法为客户带来的速度与可靠性更有信心。”Matt McKeever，LexisNexis Legal & Professional 基础设施与运营 CTO。*

## 开始使用

**动手工作坊**：AWS Solutions Architects 会举办 AI-DLC 工作坊——为期两到五天的活动，在你的自有技术栈上演示 AI 原生开发。已有数百家客户参与。

**生产项目**：当你准备把业务用例推上生产时，AWS ProServe 会加入这段旅程。我们的顾问与 Delivery Agent 嵌入你的团队，一起交付生产成果，同时建立组织能力以维持并扩展这一做法。到结束时，你既有一套在生产中运行的系统，也有受过训练的内部推动者准备把它继续带下去。

*“我们的 Solutions Architects 一直站在这场转型的第一线，在 AI-DLC 工作坊中与客户动手协作，重新构想他们构建软件的方式。团队一旦亲身经历过 AI 原生开发，就不想再回到过去。AWS Professional Services 接住这股势头，并把它规模化地落到运营中。”Shaown Nandi，AWS 技术副总裁。*

许多组织都有等待被兑现的成果，也有准备换一种方式工作的工程团队。路径不是做更多实验，而是与一支已经在自己的生产负载上验证过这套方法的团队一起，坚定地执行。

联系你的 AWS 客户团队，或访问 [AWS Professional Services 网页](https://aws.amazon.com/professional-services/)，开始更快地交付生产成果。

## 关于作者
