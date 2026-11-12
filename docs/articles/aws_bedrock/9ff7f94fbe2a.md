---
vendor: aws_bedrock
title: Accelerating product development with AI-driven lifecycle management (AI-PDLC) in AWS Quick
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/accelerating-product-development-with-ai-driven-lifecycle-management-ai-pdlc-in-aws-quick
date: 2026-11-11
lang: zh
captured: 2026-11-12
extractor: readability-v1
translator: agent
status: translated
body_sha: 703b1b8322f5
---

## [人工智能](https://aws.amazon.com/blogs/machine-learning/)

# 用 AWS Quick 中的 AI 驱动生命周期管理（AI-PDLC）加速产品开发

本文聚焦 AI 如何借助构建在 AWS Quick 之上、且流程内嵌人工审批的 agent，改善并加快产品开发生命周期。

AI 驱动的软件开发，正帮助团队以前所未有的速度交付产品。随着实现环节提速，上游的产品开发流程反而更加重要。编码 agent 能把清晰的需求比以前更快地变成可运行的软件，却弥补不了「做错了产品」。当实现变容易，你的竞争优势便向上游转移到四项关键活动：发现对的客户问题、决定追哪一个机会、设计对的体验，以及用原型去验证它。

做这些决策所需的信号却散落各处：客户在 Slack 里留反馈，销售团队把洞察记进 Salesforce，系统在 ServiceNow 里记录事故，干系人在 Microsoft SharePoint 里写需求，工程师在 Jira 里跟踪工作项，团队在 Outlook 会议和邮件串里做决定。团队在这些工具之间来回切换时，本该支撑决策的上下文与决策本身被割裂，每次交接都会再丢一些。

AWS Quick 为这些碎片化知识提供连接层。它把自定义 chat agent 建立在互联的企业数据之上，并把产物存进共享的 [Spaces](https://aws.amazon.com/quick/spaces/)，帮助团队用组织已有的知识来构建，而不是每个项目都从一张白纸开始。

AI-Driven Product Development Lifecycle（AI-PDLC）是一个框架，通过一套六个各有所长的 AWS Quick agent 来运用这些能力，在每个阶段产出可追溯的一组产物。agent 负责收集、结构化上下文，暴露缺口，起草产物；你和团队贡献判断，并批准每一个决策。目标不是更快地产出文档，而是帮团队想得更清楚、留住每个决策背后的「为什么」，并给工程和编码 agent 一份以客户证据为依据的规格说明。我们会展示如何在 AWS Quick 里配置这套六 agent 的 AI-PDLC 套件，并用它从分散的客户信号走到经过验证的原型。全程从最初洞察到工程交接，上下文都得以保留。

## 架构

下图展示了 AI-PDLC 框架的端到端流程。

![端到端 AI-PDLC 流程：从企业信号经 Amazon Quick agent 到编码 agent](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/05/ML-21390-1.png)

图 1：端到端 AI-PDLC 流程，从分散的企业信号经 AWS Quick agent 到编码 agent 交接

它从多数团队最容易跟丢的信号起步——那些 Slack 讨论串、Jira 工单、文档和通话转写，里面藏着某个决策背后的「为什么」，以及客户实际说了什么。Enterprise connectors 从 Slack、Outlook、Jira、Salesforce、SharePoint、ServiceNow 等众多企业来源拉取这些上下文。

![Amazon Quick 个人知识图谱，跨互联工具把人、项目与决策连起来](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/05/ML-21390-2.png)

图 2：AWS Quick 构建个人知识图谱，跨互联应用与文件夹把人、项目和决策连起来

AWS Quick 能从你互联的应用与文件夹构建个人知识图谱，把散在各工具里的人、项目和决策关联起来。

这些信号喂给「大脑」：AWS Quick 上的那组 agent，由一个 Orchestrator 统领，运行 Discovery、Prioritize、Working Backwards、Spec Generator 和 Designer。它们产出的一切都落到同一种通用语言里：一份 `prototype_spec.md`，装着验收标准、personas、界面和数据模型。每个决策都能追溯回一处来源。

AWS Quick 可以用 **Agent Client Protocol（ACP）** 把开发任务委派给 AI 编码 agent。ACP 是一个开放的 JSON-RPC 2.0 标准，无供应商锁定。客户可以用自己偏好的编码 agent，比如 Kiro 或 Claude Code，照 AI-PDLC 生成的规格说明来构建。

在这之下，每个阶段都设有一道人工审批闸。你确认痛点、批准优先级、签收 spec、给构建放行、接受评审。随后生产数据回流到 Discovery，闭环合拢。agent 干活，你拍板，而且谁都不必离开自己的工具。

## 方案概览

AI-PDLC 生命周期横跨八个阶段：Discover、Decide、Design、Prototype、Engineer、Ship、Operate 和 Learn。本文聚焦前四个，那是产品团队工作的阶段；后四个由 Kiro 这类编码 agent 承担，基于上游阶段产出的规格说明来构建。上游阶段在 AWS Quick 里实现为六个 agent。

![实现上游四个 AI-PDLC 阶段的六个 Amazon Quick agent](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/05/ML-21390-3.png)

图 3：上游 AI-PDLC 阶段，在 AWS Quick 里实现为六个 agent

用户只与一个 Orchestrator 交互：它在运行时读取每位专家的提问框架，针对当前阶段提出有的放矢的问题，再把产物生成分派给合适的专家。一场对话就能走完全程，而流水线只有在工作流里每一步都经人工批准后才推进。

![由 Orchestrator 驱动的 AI-PDLC 流水线，在每道闸经人工批准后推进各阶段](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/05/ML-21390-4.png)

图 4：一场 Orchestrator 对话驱动流水线，每道闸经人工批准后才推进

### 阶段 1：Discover

*Discovery agent* 通过交互式问答、URL 摄取，以及从 Slack、Jira、支持工单、Salesforce、研究资料库等互联企业来源直接拉取，引导结构化的痛点分析。它按严重度和频率给每个痛点打分，产出一份 *Pain Point Board*，让团队用一个以证据为依据的视角看清客户究竟卡在哪里。

![Pain Point Board 按严重度和频率给客户痛点打分](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/05/ML-21390-5.png)

图 5：Discovery agent 产出一份按严重度和频率打分的 Pain Point Board

### 阶段 2：Decide

*Prioritize agent* 用两套透明的 0–10 框架，按加权标准给每个用例打分：一套专为 agentic 用例设计（large language model（LLM）能力匹配、工具可用性、用户接受度），一套面向传统应用（可行性、业务影响、工作量）。团队可以打开 *Scoring Matrix*，逐条追溯某个用例为何压过另一个。

![Scoring Matrix 按加权优先级标准给用例排名](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/05/ML-21390-6.png)

图 6：Prioritize agent 的 Scoring Matrix 显示某个用例为何压过另一个

选出头号用例后，*Working Backwards agent* 用 Amazon Working Backwards 方法生成一份完整的 PR/FAQ，含客户 FAQ 与内部 FAQ，覆盖单位经济模型、失效模式、监管风险和竞争格局。如果一个概念经不起这番拷问，团队在投入工程资源之前就能在纸面上看出来。

![Working Backwards agent 生成的 PR/FAQ，含客户与内部 FAQ](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/05/ML-21390-7.png)

图 7：Working Backwards agent 为头号用例生成完整 PR/FAQ

### 阶段 3：Design

*Spec Generator agent* 把经过验证的用例与 PR/FAQ 变成一份可直接构建的规格说明，为 agentic 与应用两类用例分别准备了模板，另有一份给 UX 团队的 *Design Handoff Brief*。每份 spec 都含验收标准、用户流程、约束，以及把每条需求追溯回其来源痛点、优先级得分和验证过它的 PR/FAQ 的元数据。这些验收标准有双重用途：既是编码 agent 遵循的构建契约，也是 review agent 据此审计的评审量规。过去要花好几个 sprint 起草和评审的事，如今变成一次集中会话，细到工程可以立刻照设计 spec 开工，几乎不必再开澄清会。

![可直接构建的规格说明，验收标准可追溯回来源痛点](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/05/ML-21390-8.png)

图 8：Spec Generator agent 把经过验证的用例变成可直接构建的规格说明

### 阶段 4：Prototype

*Designer agent* 直接在 AWS Quick 里生成 *journey maps*、*wireframes* 和*可点击的 HTML 原型*。它依据 Design Handoff Brief、来自 Discovery 的 personas、来自 PR/FAQ 的用户流程、待设计界面、品牌语境，以及从客户原话里提炼的情绪目标来工作，让团队在投入 Figma 或其它设计工具之前就能与干系人验证概念。spec 获批后，便分派给工程团队开发。

![Designer agent 在 Amazon Quick 里生成的可点击原型与 wireframe](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/05/ML-21390-9.png)

图 9：Designer agent 在 AWS Quick 里生成 journey maps、wireframes 和可点击原型

整个循环是迭代式的，每道闸都有人评审与批准，没有明确签收就不放行。按问题复杂度不同，传统上要花数周做原型和迭代的事，可能变成几天、甚至几小时的引导式 agent 协作。

每个决策都记在两层。每位专家在自己产出的 artifact 里记录本层的决策、打分与理由，Orchestrator 则独立核查这些条目确实存在，并维护一条贯穿整条流水线的共享日志。就算一层漏了，另一层仍握着完整记录，因此任何一道闸的批准都不会无人追踪。

AI-PDLC 可以按两种节奏执行。Deep Discovery 每阶段问 8–12 个问题，追查歧义与边界情况，适合团队希望充分探索的新问题域。Fast Track 把每阶段压缩到 3–5 个关键问题，并从已有的上下文里给出默认值，让你逐条确认或覆盖，适合团队熟悉该领域、需要快速推进的限时会话。

## agent 实现细节：逐步拆解

我们走一遍 agent 的创建与实现过程。

### 前置条件

- 一个装好 Desktop client 的 AWS Quick workspace。
- 有在 AWS Quick 里创建自定义 agent 的权限，且已为 Slack、Jira、SharePoint 或团队使用的其它工具配置好 Enterprise connectors。

![Amazon Quick workspace，已为 Slack、Jira、SharePoint 配置企业连接器](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/05/ML-21390-10.png)

图 10：一个已配置企业连接器的 AWS Quick workspace

### 第 1 步：克隆 AI-PDLC repository

完整的 agent 套件、参考架构、prompt 模板和搭建说明都在 [AI-PDLC GitHub repository](https://github.com/aws-samples/sample-AI-PDLC-using-AmazonQuick) 里。

repository 包含：

- 全部六个 agent 的 instruction 文件。
- 每位专家 agent 的提问框架样例。
- 配置文件与搭建指南。

### 第 2 步：创建专家 agent

在 AWS Quick 里，用 repository 中的 instructions 创建专家 agent：

第 2.1 步：从 [GitHub repository for agent building](https://github.com/aws-samples/sample-AI-PDLC-using-AmazonQuick/blob/main/agents/ai_pdlc_agents_full.json) 下载 JSON 文件。

第 2.2 步：进入 **Quick Desktop** → **Customize** → **Agents** → **Create**，然后选择 **Create from File**。

![Quick Desktop Customize 菜单里用文件创建 agent](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/10/ml-21390-fig11.png)

图 11：在 Quick Desktop 里用 Create from File 创建专家 agent

第 2.3 步：chat 窗口随即打开。

![创建 agent 后打开的 Amazon Quick chat 窗口](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/05/ML-21390-12.png)

图 12：创建 agent 时打开的 chat 窗口

第 2.4 步：以下六个带 instructions 的 agent 创建完成：

![在 Amazon Quick 里创建的六个 AI-PDLC agent 及其 instructions](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/05/ML-21390-13.png)

图 13：创建的六个 AI-PDLC agent 及其 instructions

Orchestrator 是架构的核心组件。它在运行时动态读取每位专家的 instructions：

![Orchestrator agent 在运行时读取每位专家 agent 的 instructions](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/05/ML-21390-14.png)

图 14：Orchestrator 在运行时动态读取每位专家的 instructions

### 第 3 步：配置 Quick Spaces（产物仓库）

创建一个共享的 Quick Space 来存放流水线产物：

- 打开 **Quick Spaces**，选择 **Create New Space**。
- 名称：AI-PDLC Artifacts。
- 给相关团队成员授权。   [![在 Quick Spaces 里创建 AI-PDLC Artifacts Space 并给团队授权](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/05/ML-21390-15.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/05/ML-21390-15.png) 图 15：创建 AI-PDLC Artifacts Space 并给团队成员授权

### 第 4 步：运行流水线

- 打开 AWS Quick Desktop。
- 在 agent 选择器里选 **AI-PDLC Orchestrator**。
- 输入：「Run the full pipeline」（或输入「Fast Track」跑精简会话）。
- 按 Orchestrator 引导，回答它贯穿各阶段的结构化问题。
- 在每道闸，随着产物生成逐一评审。   [![运行 AI-PDLC Orchestrator 流水线并在每道闸评审产物](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/05/ML-21390-16.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/05/ML-21390-16.png) 图 16：运行流水线，并在每道闸评审随生成随出的产物

![AI-PDLC Orchestrator 启动一次流水线运行](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/05/ML-21390-17.png)

图 17：用 AI-PDLC Orchestrator 启动一次流水线运行

你可以按需选择节奏：Deep Discovery 或 Fast Track。

![在 Deep Discovery 与 Fast Track 两种节奏模式间选择](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/05/ML-21390-18.png)

图 18：按需要在 Deep Discovery 与 Fast Track 之间选择节奏

## 看它实际跑起来

想看 AI-PDLC 的现场演示——从客户洞察穿过全部四个阶段直到可运行的原型——可看我们的 YouTube 视频讲解：

- [YouTube Part 1: End-to-end product lifecycle with AWS Quick and AI coding agents (51:49)](https://www.youtube.com/watch?v=uGkf1NpzzEA)
- [YouTube Part 2: Creating AI-PDLC agents](http://youtube.com/watch?v=lwYwAgdklYw)

视频涵盖：

- 搭建 agent 套件。
- 用一个真实用例跑完整条 Orchestrator 流水线。
- 实时产物生成实录。
- 到编码 agent 的 ACP 交接。
- 在 Deep Discovery 与 Fast Track 模式之间做选择的提示。

## AI-PDLC 适用场景

我们走一遍可以套用 AI-PDLC 框架的几类常见场景：

### 场景 1：从零开始做新产品

当团队发现新的市场机会或未被满足的客户需求时，会碰到经典的冷启动难题：信号分散、点子互相竞争、没有结构化的办法把洞察变成行动。AI-PDLC 引导团队走完整个上游旅程，从真实客户数据里浮出痛点，用透明标准给互相竞争的点子打分。它还通过严格的 PR/FAQ 验证概念，并产出可直接构建的 spec，让第一行代码是照着经过验证的计划写的，而不是凭直觉。

### 场景 2：给已有产品加功能，路线图驱动或客户驱动

产品团队不断收到决定「接下来做什么」的信号：支持渠道里的客户反馈、销售转来的功能请求、显示流失点的用量数据，或领导层的战略优先级。AI-PDLC 从互联工具（Slack、Jira、Salesforce、AWS Quick Sight）里把这些信号拉出来，加速这一过程。框架把它们结构化为一份带证据打分的优先级 backlog，并产出一份保留每个功能背后「为什么」的 spec，让工程拿到的是上下文丰富的工作项，而不是被抽掉意图、只剩一行的 Jira 工单。

### 场景 3：bug 修复与事故驱动的改进

当生产问题经由客户投诉、监控告警或支持升级浮出水面时，响应常常跳过结构化分析，直奔代码修复。AI-PDLC 给这种被动工作流带来章法：把根因记为有文档可查的痛点，评估这次修复值得做更广的设计改动还是一处定向补丁。它产出一份带可测验收标准的、划定范围的 spec，让修复针对底层问题而非只是症状，并把决策轨迹留下来供日后查考。

每个场景都走同一条流水线（Discover → Decide → Design → Prototype），只是进入的深度不同。新产品跑完整旅程，功能增补可跳过深度发现，bug 修复可压缩成一次聚焦的循环。方法随之调整，而审计轨迹与治理始终一致。

## 清理

本实操创建的资源闲置时不产生费用，所以若你打算再跑流水线，可以放心把整套 AI-PDLC 套件留着。

要移除不再需要的东西，在 Quick Desktop 的 **Customize → Agents** 下删掉那六个 agent，删除 **AI-PDLC Artifacts** Space（或只删其中的测试产物）并撤销你授予的团队访问权，再断开任何仅为本次练习添加的 Enterprise connectors 或编码 agent 链接。你也可以把克隆下来的 GitHub repository 从本地机器移除。

## 结语

产品开发的瓶颈已经转移。编码 agent 让实现变快了，可上游工作仍在掣肘团队：发现客户问题、决定做什么、验证概念、产出清晰规格。能压缩这段上游循环的团队，可以获得复利式优势：做对的产品、做得更快、少走代价高昂的弯路。

AI-PDLC 正面回应这一点。它提供一套结构化、AI 原生的框架，以 AWS Quick 里的一组 agent 实现，引导产品团队走过 Discover、Decide、Design 和 Prototype，每道闸都内建治理。AI-PDLC 给每个决策归属，每件产物都能追溯回客户证据。等 spec 到了工程手里，它带着完整的上下文：为何存在、谁验证过、以及「做完」长什么样。

产品团队的角色不是写代码，而是就「做什么、为什么做」快速且可追溯地做出对的决策。AI-PDLC 让这成为可能。

## 今天就上手

- 克隆 [repository](https://github.com/aws-samples/sample-AI-PDLC-using-AmazonQuick)。
- 按 repository 里的搭建指南创建五个专家 agent 和一个 Orchestrator。
- 在 agent 选择器里选「AI-PDLC Orchestrator」，然后说：「Run the full pipeline」。

## 关于作者
