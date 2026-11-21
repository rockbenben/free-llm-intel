---
vendor: anthropic
title: Uber 的 CISO 谈如何为 AI 搭建内部威胁防控体系
original_title: 
url: https://claude.com/resources/articles/uber-s-ciso-on-building-an-insider-threat-program-for-ai
date: 2026-10-13
lang: zh
captured: 2026-10-15
extractor: readability-v1
translator: agent
status: translated
body_sha: c90802ec39ce
---

Uber 运营着全球最大的实时交易市场之一，每天产生超过 4000 万次出行和配送订单。Philip Martin 是 Uber 的首席信息安全官（CISO），他带领的团队守护着 Uber 的数据，以及现实世界中使用这一平台的乘客、司机和骑手。早在 Claude Code 出现之前，他的团队就开始与 Claude 一起做威胁建模，当时要靠手工拼装上下文。如今有了 Claude Fable，Claude 能自己从代码、设计文档和工单历史中收集这些上下文。

Martin 认为，AI 智能体也需要企业如今已经在为员工运行的那类内部威胁防控体系。我们就这一思路与他聊了聊：他为什么如此在意无意的误用，以及 Uber 的开源监控工具如何与 Enterprise Frontier Safeguards 协同工作。

**前沿模型正在如何改变你们安全团队的工作？**

此前的模型与今天的前沿模型之间真正重大的差别，在于它们能在很长的时间跨度内纳入额外上下文，并由此生成非常具体的输出。当我们针对某个服务应用做安全评审或威胁建模时，可以让模型消化更多关于该服务的上下文——无论是代码本身、设计文档、Jira 里的 issue，还是关于这个服务应该做什么、与哪些东西交互的历史背景。

同样的趋势我也在智能体团队身上看到。可以想象，在不远的将来，每个服务都会关联一个对它了解得非常透彻的智能体，而这些智能体之间也能对话——就像这些服务在生产环境中彼此交互一样——交流威胁模型：这是我的威胁模型，我的数据来自这里。这种智能体团队的协同效应，会把我们的效能带到下一个层级。

**Uber 与我们这边的 Enterprise Frontier Safeguards 团队有过合作。这对 Uber 为什么重要？**

Anthropic 和 Uber 有一个共同点：对安全的专注刻在骨子里，尽管两者的语境完全不同。Uber 谈安全，想的是乘客安全、保护个人数据。Anthropic 要防止其前沿模型被滥用，而 Uber 需要保护我们的客户数据、商业机密，以及其他一切专有信息。Enterprise Frontier Safeguards 让我们得以拿捏这个平衡：防护措施到位，但未经我们许可，Anthropic 无法访问我们的数据。

它让我们掌握对自己数据的控制权，也掌握风险缓释的主动权——安全防护措施触发之后，采取什么行动由我们决定。我认为我们共同负有一份责任：确保这些模型在现实世界中被安全、有效地使用。

你们团队讲解设计方案的时候，我们能明显感觉到他们听进去了我们的反馈。你们把主导权交到了我们手上。这让我们既能保护自己的数据，又能负起责任，善用这些模型的能力。

**Enterprise Frontier Safeguards 如何与你们已经在 Uber 的 AI 部署上运行的安全监控相配合？**

从最开始起，我们就围绕如何在 Uber 内部安全地部署 AI 做了大量工作。我们最近开源了一个名为 [AI Detection and Response（ADR）](https://github.com/uber/ADR)的产品，设计目标是在我们部署的智能体 harness 中采集实时遥测并执行实时响应。

它与 Anthropic 的防护措施形成互补，因为我们现在能拿到增强后的数据，检测智能体是否越界行动并实时响应。我们对正在发生什么有自己的视角，再加上 Anthropic 分类器的输出，两路信息可以整合进我们整体的检测环境，就像传统网络安全环境那样。核心在于有效拼装上下文，尽可能快、尽可能有把握地做出决策。

我想我们会看到 Enterprise Frontier Safeguards 作为一个数据源接入 ADR。再加上我们的 LLM 网关——它负责搭建边界、管控 Uber 内部如何使用 AI——这些共同构成了我们整体的 AI 安全架构。

**在保护 AI 系统这件事上，你认为防守方接下来应该优先把重心放在哪里？**

第一位是实时检测与干预：尽可能贴近那个在 harness 里输入 prompt 的人，能够提醒他「你大概率不想这么做」，或者「这个模型接下来要调用的工具、要连接的地方，恐怕不是你希望发生的」。

第二位是更好地理解新出现的模式。我们观察模型行为的趋势，检出那些我们此前不知道还可能发生的新行为。这会形成一个循环：我们看数据——很多时候有 LLM 辅助——在这些行为一出现时就发现它们，再把针对它们的防护措施建回实时平台。然后新的行为又会出现，因为约束本身会催生新行为，我们同样会把它们找出来。

**对那些在前沿模型所要求的监控上犹豫不决的其他领导者，你会对他们说什么？**

采用 AI 是业务的当务之急。不管我们愿不愿意，它都会到来，而且会给世界各地的企业和人们带来实实在在的好处。但它同样存在真实的危害可能，而且随着模型能力更强、承担更复杂、更自主的工作，风险敞口也在上升。

每家公司都已经在为自己的员工运行内部威胁防控体系，这一点没人有异议。我们接受有时相当繁重的数据留存要求，监控一些本来不想监控的东西，因为我们知道人偶尔会越出自身角色的边界，原因多种多样。

前沿模型带来了同样的风险。这些模型可能被人指使，越出我们期望它们运作的约束范围。所以我们需要面向 AI 的对等能力。那套针对模型的内部威胁防控体系，将是我们把这些系统安全、稳妥地铺开的关键。

*进一步了解 [Enterprise Frontier Safeguards](https://www.anthropic.com/news/enterprise-frontier-safeguards)。*

文章

2026 年 10 月 8 日

### Block 如何让 Claude Fable 在上千个 pull request 中协同调度

Block 的 AI 能力负责人 Bradley Axen，谈他的团队如何评测新的大语言模型、Claude Fable 5 如何统筹公司范围内的代码迁移，以及为什么安全防护措施是负责任地大规模部署前沿智能的关键一环。

Claude Enterprise

文章

2026 年 10 月 6 日

### Comcast 和 Booz Allen 如何用 Claude Mythos 挖掘漏洞利用链、加固代码库

Comcast 和 Booz Allen 的安全团队通过 Project Glasswing 使用 Claude Mythos 级模型，找到了现有扫描器漏掉的漏洞，并完成验证和修复。

文章

2026 年 9 月 29 日

### 可以被带教的智能体：Asana 如何用 Claude 组建人机混合团队

Asana 首席产品官 Arnab Bose，谈 Asana 如何把 AI 智能体当作团队成员来运作：限定范围的角色、共享的记忆，以及人人都看得见的工作。

Claude Platform

文章

2026 年 9 月 28 日

### 用 Claude 自动化评测设计与 hillclimbing

如何在不自欺的前提下设计评测并对其 hillclimbing，以及 claude-api skill 的 build-eval 与 hillclimb 命令如何把它们付诸实践。

Claude Platform


## 用 Claude 变革组织的运作方式

[查看 pricing](https://claude.com/pricing#api)[联系销售](https://claude.com/contact-sales)

### 订阅开发者通讯

产品更新、操作指南、社区聚焦等内容，每月送达你的邮箱。

如果你希望接收我们每月的开发者通讯，请提供你的邮箱地址。你可以随时退订。
