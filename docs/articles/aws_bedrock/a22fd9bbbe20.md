---
vendor: aws_bedrock
title: AWS Quick 中的 skills 和 agents 是如何工作的
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/how-skills-and-agents-work-in-aws-quick
date: 2026-11-10
lang: zh
captured: 2026-11-10
extractor: readability-v1
translator: agent
status: translated
body_sha: 1f36aaaf410c
---

## [人工智能](https://aws.amazon.com/blogs/machine-learning/)

# AWS Quick 中的 skills 和 agents 是如何工作的

如果你用过 AI agents，多半不止一次解释过同一个任务：怎样整理每周状态汇报、写版本说明、管理项目，或者创建工单。这些都是可重复的任务，可以借助 [AWS Quick](https://aws.amazon.com/quick/) 通过 agents 和 skills 固化下来。AWS Quick 是一项 AI 驱动的服务，用来自动化任务、分析数据、构建 Web 应用、开展调研。你用自然语言与它交互，Quick 则用 AI agents 对照你接入的数据源和应用来处理你的请求。

本文会讲清 agents、skills 和你的数据在 AWS Quick 里如何配合，以及如何构建并分享适合团队的 skills。我们还会展示官方目录和 custom agents 怎样帮你把这些 skills 用起来。

## 理解基础概念

这一节先解释几个基础概念，帮你理解 AWS Quick 与 agents、skills 以及你的数据之间的关系。

![中心辐射式示意图：Quick agent 位于中央，连接着它的指令、skills、connectors 和数据源](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/04/ML-22266-1.png)

图 1：Quick agent 如何遵循指令、加载任务所需的 skills、通过 connectors 执行操作，并以你的数据为依据给出回答

agent 位于图 1 的中央。它遵循指令、加载任务所需的 skills、通过 connectors 执行操作，并以你的数据为依据给出回答——这些数据包括 spaces、knowledge bases、datasets 和 dashboards。

### 使用 agents

AWS Quick 中的 [agent](https://docs.aws.amazon.com/quick/latest/userguide/agents-desktop.html) 是一个可配置的 AI，有自己的指令、知识来源（spaces）和 connectors，用来回答问题、为你完成工作。你可以在聊天里与 agent 协作，也可以借 [routine](https://docs.aws.amazon.com/quick/latest/userguide/agents-desktop.html) 让它自行运行。Agents 只能访问你本人能访问的资源和服务，每个 agent 可以做什么，由你决定。

**Quick** 是每个用户都能用的默认内置 agent。它没有固定范围，每轮对话里都能调用你有权访问的任何资源，比如你的 spaces、knowledge bases、dashboards、connectors 和 skills。你不必事先判断一个请求需要哪些数据或工具，所以多数工作都可以从 Quick 起步。

**custom agent** 是你或团队里某人为某项具体工作配置的 agent，例如一个人力资源（HR）入职助手，依据 HR 团队的 space 回答新员工的问题。你给它单独的指令，把它限定在用例所需的 spaces、connectors 和 skills 内。测试并发布之后，就能分享给 AWS Quick 账户里的其他用户和群组。构建过程的逐步演示，参见 [使用 AWS Quick 构建 AI 驱动的员工入职 agents](https://aws.amazon.com/blogs/machine-learning/build-ai-powered-employee-onboarding-agents-with-amazon-quick/)。

### 使用数据

Agents 的回答以你接入 Quick 的数据为依据。**space** 是经过整理的文档与 AWS Quick 资源集合，agent 把它当作信息来源。你可以为自己、团队或组织里其他小组创建一个 space，往里上传文件和文件夹，或加入 dashboards、knowledge bases、action connectors、datasets 这类资产。与 Quick 开始对话时，可以挂上一个 space，把 Quick 这轮对话用到的数据收窄。把 space 加进 agent 后，它就成了 agent 配置的一部分，请求需要时 agent 会从中取用。

**knowledge base** 是把数据源里的文档或内容组织好、建好索引的集合，专为检索和问答优化。Quick 会从 Google Drive、Microsoft OneDrive、Confluence、Microsoft SharePoint、Amazon Simple Storage Service (Amazon S3)、网页爬虫，以及 [Amazon Bedrock Managed Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) 等来源同步 knowledge bases，并按同步计划保持更新。

Datasets 和 dashboards 来自 [AWS Quick Sight](https://docs.aws.amazon.com/quick/latest/userguide/quick-bi.html)，也就是 Quick 里的商业智能功能；通过 AWS Management Console 开通的账户才能用它。**dataset** 是备好的一组数据，可直接用于分析和 dashboards。**dashboard** 是分析的发布版本，用来分享给其他 Quick 用户。借助 datasets，你可以在结构化数据（比如数据库表）之上建立语义丰富的元数据，从而用自然语言完成复杂的分析用例。

最后，**connector** 把 AWS Quick 连到外部应用或原生工具，让 agents 能读取数据、代你执行操作。**Cloud connectors** 把 Quick 接到 Microsoft Outlook、Slack、Jira、Asana、Salesforce 等服务，以及远程托管的 Model Context Protocol (MCP) 服务器；你使用 Quick 的每台设备上都能用。**Local connectors** 跑在你自己的机器上，比如你自己托管的 MCP 服务器，因此只有这台机器开机且联网时，它们的工具才可用。connector 类型的完整清单，参见 AWS Quick User Guide 中的 [Connectors](https://docs.aws.amazon.com/quick/latest/userguide/connections-desktop.html) 和 [Integration-specific guides](https://docs.aws.amazon.com/quick/latest/userguide/integration-guides.html)。

这些合在一起，让你的数据、文档和应用都能通过自然语言访问，于是你可以在已连接的来源里提问、执行操作。

### 使用 skills

[skill](https://docs.aws.amazon.com/quick/latest/userguide/skills-desktop.html) 是一组可复用的指令，教 agent 完成某项具体任务。Skills 也是 Quick 里的 agent 行为方式与完成工作的基础。和其他 agents 一样，Quick 中的 agent 运行在 harness（一个托管的 agent 循环）里，遵循推理与行动（ReAct）模式。你给 AWS Quick 一个 prompt 时，agent 会用可用的工具和指令达成目标，再给你回复。[Strands Agents SDK](https://strandsagents.com/) 这类 agent 框架，也是围绕同一个模型驱动的循环构建的。

Quick 默认能做的大部分事情，来自 **system skills**。比如你可以让 Quick 生成 Word 文档、PowerPoint 演示文稿、Excel 表格或 PDF，随后某个 system skill 便借助自带的脚本、用代码创建或编辑这份文档。另一些 system skills 负责浏览网页、运行代码、做深度调研、转录音频和视频、生成图像。还有一些管理 Quick 本身：构建 [AWS Quick Flows](https://docs.aws.amazon.com/quick/latest/userguide/using-amazon-quick-flows.html)、安排 routines、把工作交给 Kiro 这类 coding agent、管理你的记忆和知识图谱，或者跟踪待办事项。在 Quick 里，system skills 可以开关，但不能编辑、复制、导出、发布、分享或删除。

AWS Quick 提供的能力和工具，让 skills 能干很多种活。比如一个 skill 可以产出交付物，像按你的模板生成的每周状态汇报；另一个可以跨 connectors 自动化一条工作流，比如汇总本周的 Jira 动态、把摘要发到 Slack；skill 还能在 Python 脚本里做计算，再用 JavaScript 把结果画成图表。

## 什么是 skill？

Quick skills 遵循 [Agent Skills](https://agentskills.io/) 规范，它最早由 Anthropic 开发，并作为开放标准发布。桌面版 AWS Quick 用的就是这一规范：它于 [2026 年 4 月进入预览](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-quick-macos-windows-preview/)，并在 [2026 年 9 月正式可用](https://aws.amazon.com/blogs/machine-learning/amazon-quick-is-now-generally-available-on-desktop/)。

一个 skill 就是一个文件夹，根目录下放一个 Markdown 文件 `SKILL.md`，外加指令会用到的可选脚本或其他参考文件。这个文件的 frontmatter（两条 `---` 之间的属性）里写着 name、description，以及与这个 skill 相关的其他元数据。下面看一个删减过的示例，skill 名叫 `release-notes-generator`。

```
---
name: release-notes-generator
description: "Generates human-readable release notes from merged pull requests, commits, or changelogs ... Use when asked to 'generate release notes', 'write changelog', ..."
---
```

description 和 name 是触发一个 skill 最关键的两项。Quick 把 skills 加载进 agent 的 prompt 时，用的是 **progressive disclosure**：agent 只读每个 skill 的 name 和 description，直到某个请求需要这个 skill，才把它的完整指令加载进来，具体见 [How agents load skills](https://docs.aws.amazon.com/quick/latest/userguide/skills-desktop.html#desktop-how-quick-loads-skills)。这意味着某些说法能帮着触发 skill，比如「生成 2.3 版本的版本说明」。规范把 `name` 限制在 64 个字符以内、`description` 限制在 1,024 个字符以内，并建议 skill 里的指令不超过 5,000 tokens。

![名为 release-notes-generator 的 skill 文件夹，内含一个 SKILL.md 文件以及可选的 scripts 和 references 文件夹](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/04/ML-22266-2.png)

图 2：release-notes-generator skill 文件夹，含必需的 SKILL.md 文件以及可选的 scripts 和 references 文件夹

## 在 Quick 中构建并分享 skill

创建 skill 可以从聊天开始，也可以从文件（.md 或 .zip）或根目录下带 `SKILL.md` 的文件夹导入。本文只讲聊天这种方式。起步时，在聊天里把任务描述给 Quick。比如可以用下面这个模板（把 <> 里的内容换成你的要求）：

```
Every <specify your cadence e.g. every day, on monday, or none at all>, I have to grab data from the following sources:
- <List your sources and how you want to query them>
...

And do <describe how you want to transform the data and the exact sequence of steps>. 

Once I am finished, I have to create a report <describe your report format or provide an example> and send to the following stakeholders <describe your recipients> using the following connector <describe your connector>.

Create a skill from this requirement, and help me come up with testing scenarios to test the skill. 
```

有这些就够你动手做自己的 skills 了。另一种做法是：拿一段你此前为完成某任务而进行的多轮对话，让 Quick 据此生成一个 skill。对最终结果满意之后，发布并分享：

- 选择 **Customize**，再选择 **Skills**。
- 在草稿中找到你的 skill，打开其详情面板。
- 选择 **Publish**。
- 选择 **Share**，再选定要分享给的人员或群组。

发布和分享是两步，光发布并不会把 skill 开放给任何人。被分享的人从 **Shared with me** 下的 **Add to Quick** 添加它，此后你每次重新发布，他们那边的版本都会同步更新。当前步骤参见 AWS Quick User Guide 中的 [Draft and published versions](https://docs.aws.amazon.com/quick/latest/userguide/skills-desktop.html#desktop-skill-draft-published) 和 [Sharing your skills](https://docs.aws.amazon.com/quick/latest/userguide/skills-desktop.html#desktop-sharing-skills)。

### 用最佳实践打磨 skills

凭一段简短描述或一次对话搭出来的 skill，也许在你自己手上一直好用；但要做与团队共享的生产级 skills，就得把很多因素考虑进去。Skills 很像代码，不少工程上的最佳实践，能帮任何知识工作者把它们建好。

- 「在我机器上是好的」是软件工程师常说的一句话，说的是软件在作者那儿跑得通，换个人安装或使用就崩。做 skills 时，你必须考虑运行环境：skill 的指令可以让 agents 去查数据源、调 connectors 或工具。软件工程师通常靠写明使用前提来绕开这个限制。比如你要单独分享一个 skill，不妨随附一个 README，把这些要求写清楚。如果你分享的是用了这个 skill 的 agent，记得把它连接的来源一并分享，否则拿到的人只能从自己本来就能访问的来源里得到答案。
- 为失败做好预案。Agents 用的连接来源，依赖第三方和第一方服务。工程师写代码时得想清楚：软件某处挂了该怎么办。把这些情形写进 skill 的指令，agents 就能照着明确的指示应变。你不必是下游服务的专家——agent 会朝目标推进，某一步失败时它可以重试或换条路子。但你必须写清楚：一旦故障影响到任务或业务流程，该怎么做。看下面这段从某 skill 工作流里摘出来的片段，它一旦失败可能牵连不小。

```
[Agent] Send the report to {{recipient}} over email.
```

万一邮件发送失败，agent 该怎么做？你大概要把这种情形下的处理方式补进指令里。

```
[Agent] Send the report to {{recipient}} over email.
Validate: The report appears in your Sent folder.
If fails: Stop, and tell the user that the report wasn't sent and why, so they can send it themselves.
```

按计划定时运行 agents、又没有人在回路中时，处理失败情形就更要紧了。

- 每次改动都要测。软件工程师会写多种测试，比如单元测试、集成测试，用来检验软件；每改一次就跑一遍。对 skills 来说，同样要自己为各种场景生成测试用例，并随着改动不断补上新测试。做法不止一种，但最好在你预期下游用户会用的环境里测。

做生产级 skills 时，要考虑的还有很多：

- 每次改动都附上版本说明。
- 把会变的硬编码值（比如 `/Users/me/notes` 或 `#my-team`）从步骤里拿出去，改成由每个人自行提供的输入。
- 用易读的日期记下 skill 的改动时间。
- 记下每个参考文件的来源，这样来源一变，你也能同步更新 skill 的指令。
- 存一份 checksum——skill 文件的指纹，用来看出某个副本与当初校验过的版本是否不同。
- 每次改动后都检查结构，就像 linter 在代码送审之前先把错误挑出来。
- 用一致的方式构建 skills，团队就能更快地提交改动、完成评审。

对任何用户来说，要考虑的都不少。正因如此，[AWS Quick official catalog](https://amazon-quick.github.io/Amazon-Quick-official-catalog/) 才提供了预建好的资源，比如按这些最佳实践做出来的 skills。

### AWS Quick official catalog

这个 catalog 是一组 agent 资源，既可以原样安装使用，也可以拿它当起点、改成贴合自己工作的版本。目录称，其中每个资源在发布前都经过质量、安全等方面的测试和扫描。这些 skills 覆盖日常办公效率，也覆盖销售、市场、HR、法务、项目管理、客户成功、软件工程等团队的工作；还覆盖金融、医疗与生命科学、能源与公用事业、酒店业、供应链与物流等行业。

目录里有一个 **Skill Architect** skill，是替你把这些工程最佳实践用起来的预建 skill，具体见 [Build skills with software engineering practices in AWS Quick](https://amazon-quick.github.io/Amazon-Quick-official-catalog/build-skills/)。安装时依次选择 **Customize**、**Skills**、**Browse all**，再选 **Official**；在搜索框里输入 `skill architect`，然后选 **Install**。当前步骤参见 [Install skills in AWS Quick on desktop](https://amazon-quick.github.io/Amazon-Quick-official-catalog/install/)。

### 把 skills 连接到你的 agents

创建 agent 时，你要配置它的 name、description 和 instructions，选定它读取哪些 spaces、能用哪些 connectors、可以加载哪些 skills。详见 AWS Quick User Guide 里的 [Agent configuration](https://docs.aws.amazon.com/quick/latest/userguide/agents-desktop.html#desktop-agent-configuration)。让 agent 专注一个具体用例，比如回答新员工问题、准备每周状态报告，并把它的世界**限定**在该用例所需的 spaces、skills 和 connectors 内，效果最好。默认情况下，agent 能使用你全部的 skills；一旦你指定了具体的 skills，它就只能用这些。分享 agent 时这会出问题：它按使用者本人的权限运行，同一个请求在不同人那里可能触达不同的数据和 skills；要是需要某个只有你能访问的来源，回答就会不完整。

想把这几样（agents、skills 和 spaces）串起来，可以试试所链接 workshop 里的 [personal agent architect module](https://catalog.us-east-1.prod.workshops.aws/workshops/a8484e57-2e30-40ee-bd98-0122f0d05acc/en-US/2000-build-your-personal-setup/2100-run-personal-agent-architect)。

## 结语

本文讲了 agents 在 AWS Quick 里如何使用 skills 和你的数据，也讲了如何构建、分享适合团队的 skills。我们还展示了官方目录和 custom agents 怎样帮你把这些 skills 用起来。

想进一步了解、查找活动，或分享你用 AWS Quick 做出的成果，可以访问 [AWS Quick Community](https://community.amazonquick.com/)。AWS Quick Community 里有学习资料、功能公告、活动，以及其他用户的示例；你也可以在它的 Q&A 论坛提问。

本文相关主题有一场录播，可看 [Encode Your Enterprise with Agents & Skills on AWS Quick](https://www.youtube.com/watch?v=m9gN2GapOps)。这场分享讲了一个 skill 如何组织、如何加载，skills 如何与 agents、spaces、connectors 配合，以及构建要分享的 skills 的最佳实践。最后还演示了官方目录和 Skill Architect skill。

下面这些额外资源，出自每天与 AWS Quick 打交道的专家之手：

- [AWS Quick 完整指南：agentic AI 业务工作区](https://catalog.workshops.aws/amazon-quick-suite-workshop)。
- [AWS Quick：具备丰富集成的端到端业务用例](https://catalog.us-east-1.prod.workshops.aws/workshops/8724e6e3-1115-4f40-9770-8a24199ce308/en-US)。
- [AWS Quick 管理 Workshop](https://catalog.us-east-1.prod.workshops.aws/workshops/767bc5b8-1d33-40e2-8969-f8653db64756/en-US)。
- [深入了解 AWS Quick Sight](https://catalog.workshops.aws/quicksight/en-US)。
- [AWS Quick Knowledge Hub – 官方代码示例与解决方案](https://aws-samples.github.io/sample-amazon-quick-suite-knowledge-hub/)。
- [关于 AWS Quick 的 AWS 博客文章](https://aws.amazon.com/search/?searchQuery=Amazon%20Quick&filters=((id:provider,value:(blogs)))&sort=(id:relevance,direction:desc))。

## 关于作者
