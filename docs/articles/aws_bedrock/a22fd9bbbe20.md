---
vendor: aws_bedrock
title: 技能和代理如何在 AWS Quick 中发挥作用
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/how-skills-and-agents-work-in-aws-quick
date: 2026-11-10
lang: zh
captured: 2026-11-10
extractor: readability-v1
translator: mt
status: translated
body_sha: 6af05db0a477
---

## [人工智能](https://aws.amazon.com/blogs/machine-learning/)

# 技能和代理如何在 AWS Quick 中发挥作用

如果您使用人工智能代理，您可能不止一次地解释过同一任务。您可能会描述如何构建每周状态更新、编写发行说明、管理项目或创建票证。这些都是可重复的任务，您可以通过代理和技能使用 [AWS Quick](https://aws.amazon.com/quick/) 进行编码。 AWS Quick 是一项人工智能驱动的服务，用于自动执行任务、分析数据、构建 Web 应用程序和进行研究。您可以使用自然语言来使用它，Quick 使用 AI 代理来处理您针对连接的数据源和应用程序的请求。

在这篇文章中，我们将介绍代理、技能和您的数据如何在 AWS Quick 中组合在一起，以及如何构建和分享适合您的团队的技能。我们还展示了官方目录和定制代理如何帮助您运用这些技能。

## 理解基本概念

在本部分中，我们将解释一些基本概念，帮助您了解与代理、技能和数据相关的 AWS Quick。

![中心辐射图，以 Quick 代理为中心，连接到其指令、技能、连接器和数据源](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/04/ML-22266-1.png)

图 1：Quick 代理如何遵循其指令、加载任务所需的技能、通过连接器执行操作并将其答案基于您的数据

代理位于图 1 的中心。它遵循指令，加载任务所需的技能，通过连接器采取行动，并将其答案基于您的数据：空间、知识库、数据集和仪表板。

### 与代理合作

AWS Quick 中的[代理](https://docs.aws.amazon.com/quick/latest/userguide/agents-desktop.html) 是一个可配置的 AI，具有自己的指令、知识源（空间）和连接器，用于回答问题并为您完成工作。您可以在聊天中使用代理，或者使用[例程](https://docs.aws.amazon.com/quick/latest/userguide/agents-desktop.html)让它自行运行。代理只能访问您可以访问的资源和服务，并且您可以决定允许每个代理执行哪些操作。

**Quick** 是每个用户都可以访问的默认内置代理。它没有固定的范围，因此在每次对话中，它都可以使用您有权访问的任何资源，例如您的空间、知识库、仪表板、连接器和技能。您无需提前决定请求需要哪些数据或工具，因此您可以使用 Quick 开始大部分工作。

**自定义代理**是您或您团队中的某人为特定作业配置的代理。一个例子是人力资源 (HR) 入职助理，他在人力资源团队的空间中回答新员工的问题。您可以为其提供自己的说明，并将其限制为您的用例所需的空间、连接器和技能。测试并发布后，您可以与 AWS Quick 账户中的其他用户和组共享。有关构建一个的演练，请参阅[使用 AWS Quick 构建由 AI 驱动的员工入职代理](https://aws.amazon.com/blogs/machine-learning/build-ai-powered-employee-onboarding-agents-with-amazon-quick/)。

### 处理数据

客服人员根据您连接到 Quick 的数据给出答案。 **空间** 是代理用作信息源的文档和 AWS Quick 资源的精选集合。您可以为自己、您的团队或组织中的其他小组创建一个。您可以将文件和文件夹上传到空间，或添加仪表板、知识库、操作连接器和数据集等资产。当您与 Quick 开始对话时，您可以附加一个空格来缩小 Quick 用于该对话的数据范围。当您向代理添加空间时，该空间将成为代理配置的一部分，并且代理会在请求需要时利用它。

**知识库**是来自数据源的文档或内容的有组织的、索引的集合，针对检索和问题回答进行了优化。快速同步来自 Google Drive、Microsoft OneDrive、Confluence、Microsoft SharePoint、Amazon Simple Storage Service (Amazon S3)、网络爬虫或 [Amazon Bedrock 托管知识库](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html) 等来源的知识库。快速让他们了解最新的同步时间表。

数据集和控制面板来自 [AWS Quick Sight](https://docs.aws.amazon.com/quick/latest/userguide/quick-bi.html)，这是 Quick 中的商业智能功能，可在通过 AWS 管理控制台配置的账户中使用。 **数据集**是准备好的数据集合，可用于分析和仪表板。 **仪表板**是您与其他 Quick 用户共享的分析的发布版本。借助数据集，您可以在结构化数据（例如数据库表）上构建语义丰富的元数据，这样您就可以使用自然语言完成复杂的分析用例。

最后，**连接器** 将 AWS Quick 连接到外部应用程序或本机工具，以便代理可以读取数据并代表您采取操作。 **云连接器** 将 Quick 连接到 Microsoft Outlook、Slack、Jira、Asana 和 Salesforce 等服务，以及远程托管的模型上下文协议 (MCP) 服务器。它们可在您使用 Quick 的每台设备上使用。 **本地连接器** 在您自己的计算机上运行，​​例如您自己托管的 MCP 服务器，因此它们的工具仅在该计算机打开并连接时才可用。有关连接器类型的完整列表，请参阅 AWS 快速用户指南中的[连接器](https://docs.aws.amazon.com/quick/latest/userguide/connections-desktop.html) 和[集成特定指南](https://docs.aws.amazon.com/quick/latest/userguide/integration-guides.html)。

这些共同使您的数据、文档和应用程序可以通过自然语言访问，因此您可以在连接的源中提出问题并采取行动。

### 运用技能工作

[技能](https://docs.aws.amazon.com/quick/latest/userguide/skills-desktop.html) 是一组可重复使用的指令，用于指导代理如何执行特定任务。技能也是客服人员在 Quick 中表现和完成工作的基础。与其他代理一样，Quick 中的代理在遵循推理和行动 (ReAct) 模式的线束（托管代理循环）中运行。当您向 AWS Quick 提供提示时，代理会使用其可用的工具和指令来实现其目标并向您提供响应。 [Strands Agents SDK](https://strandsagents.com/) 等代理框架是围绕相同的模型驱动循环构建的。

Quick 默认情况下所做的大部分工作都来自**系统技能**。例如，您可以要求 Quick 生成 Word 文档、PowerPoint 演示文稿、Excel 电子表格或 PDF。然后，系统技能可以使用带有技能包脚本的代码来创建或编辑文档。其他系统技能浏览网页、运行代码、执行深入研究、转录音频和视频以及生成图像。有些管理 Quick 本身，例如构建 [AWS Quick Flows](https://docs.aws.amazon.com/quick/latest/userguide/using-amazon-quick-flows.html)、安排例程、将工作交给 Kiro 等编码代理、管理您的记忆和知识图或跟踪您的待办事项。在 Quick 中，您可以打开或关闭系统技能，但无法编辑、复制、导出、发布、共享或删除它们。

由于 AWS Quick 提供的功能和工具，技能可以完成多种工作。例如，一项技能可以产生可交付成果，例如根据模板构建的每周状态更新。另一个可以自动化连接器之间的工作流程，例如收集本周的 Jira 更新并将摘要发布到 Slack。技能还可以在 Python 脚本中运行计算并使用 JavaScript 将结果绘制成图表。

## 什么是技能？

快速技能遵循 [Agent Skills](https://agentskills.io/) 规范，该规范最初由 Anthropic 开发并作为开放标准发布。桌面版 AWS Quick，于 [2026 年 4 月预览](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-quick-macos-windows-preview/) 推出，并[于 9 月全面推出2026](https://aws.amazon.com/blogs/machine-learning/amazon-quick-is-now-generally-available-on-desktop/)，使用此规范。

技能是一个文件夹，其根目录下有一个 Markdown 文件“SKILL.md”，以及其说明使用的任何可选脚本或其他参考文件。文件的 frontmatter（两个“---”行之间的属性）包含名称、描述以及与您的技能相关的任何其他元数据。请参阅以下名为“release-notes-generator”的技能的简短示例。
```
---
name: release-notes-generator
description: "Generates human-readable release notes from merged pull requests, commits, or changelogs ... Use when asked to 'generate release notes', 'write changelog', ..."
---
```
描述和名称是触发技能的两个最重要的方面。当快速将您的技能加载到代理的提示中时，它会使用**渐进式披露**。代理仅读取每个技能的名称和描述，直到请求调用该技能为止。然后，它会加载技能的完整说明，如[代理如何加载技能](https://docs.aws.amazon.com/quick/latest/userguide/skills-desktop.html#desktop-how-quick-loads-skills)所述。这意味着某些短语可以帮助触发该技能，例如“生成 2.3 版本的发行说明”。该规范将“名称”的上限限制为 64 个字符，将“描述”的上限限制为 1,024 个字符，并建议技能中的指令少于 5,000 个字符。

![名为release-notes-generator的技能文件夹，其中包含SKILL.md文件以及可选脚本和引用文件夹](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/04/ML-22266-2.png)

图 2：release-notes-generator 技能文件夹，其中包含必需的 SKILL.md 文件以及可选的脚本和引用文件夹

## 建立并分享 Quick 技能

您可以通过聊天、文件（.md 或 .zip 文件）或根目录下有“SKILL.md”文件的文件夹创建技能。这篇文章主要讨论聊天。首先，在聊天中快速描述您的任务。例如，您可以从此模板开始（将 <> 括号之间的内容替换为您的要求）：
```
Every <specify your cadence e.g. every day, on monday, or none at all>, I have to grab data from the following sources:
- <List your sources and how you want to query them>
...

And do <describe how you want to transform the data and the exact sequence of steps>. 

Once I am finished, I have to create a report <describe your report format or provide an example> and send to the following stakeholders <describe your recipients> using the following connector <describe your connector>.

Create a skill from this requirement, and help me come up with testing scenarios to test the skill. 
```
这就是您开始培养自己的技能所需的全部内容。或者，您也可以进行之前为完成任务而互动过的多轮对话，并要求 Quick 从中生成技能。当您对最终结果感到满意后，发布并分享您的技能：

- 选择**自定义**，然后选择**技能**。
- 在草稿中找到你的技能，然后打开其详细信息面板。
- 选择**发布**。
- 选择 **共享**，然后选择要共享的人员或群组。

发布和共享是独立的步骤，因此仅发布并不能让任何人获得该技能。您与之共享的人从 **添加到快速** 中的 **与我共享** 下添加它，并且每次您再次发布时，他们的版本都会保持同步。有关当前步骤，请参阅 AWS 快速用户指南中的[草稿和已发布版本](https://docs.aws.amazon.com/quick/latest/userguide/skills-desktop.html#desktop-skill-draft-published)和[分享您的技能](https://docs.aws.amazon.com/quick/latest/userguide/skills-desktop.html#desktop-sharing-skills)。

### 通过最佳实践提高您的技能

通过快速描述或对话构建的技能可能对您来说始终有效，但在构建与团队共享的生产技能时必须考虑许多注意事项。技能就像代码，许多工程最佳实践可以帮助任何知识工作者构建它们。

- “它可以在我的机器上运行”是软件工程师的常用短语。它描述了为构建它的人运行但在其他人安装或使用它时崩溃的软件。在培养技能时，您必须考虑您的环境。技能指令可以使用代理来查询数据源或调用连接器或工具。软件工程师通常通过记录使用软件的先决条件来解决此限制。例如，如果您要单独共享一项技能，您可能需要使用您的技能创建一个自述文件来记录这些要求。如果您共享使用您的技能的代理，还要共享它连接到的源，或者与您共享它的人只能从他们已经可以访问的源中获取答案。
- 为失败做好计划。代理使用依赖于第三方和第一方服务的连接源。当工程师编写代码时，他们需要了解如果某个软件出现故障该怎么办。如果您将这些场景纳入您的技能说明中，您的代理可以根据具体说明进行调整。您不需要成为下游服务的专家，因为代理会朝着目标努力，并且可以在步骤失败时重试或尝试其他方法。您确实需要列出当故障影响您的任务或业务流程时该怎么做。从技能中的工作流程中获取以下片段，如果失败可能会产生后果。
```
[Agent] Send the report to {{recipient}} over email.
```
如果发送邮件失败，代理应该怎么办？您可能想要添加有关在该场景中要做什么的说明。
```
[Agent] Send the report to {{recipient}} over email.
Validate: The report appears in your Sent folder.
If fails: Stop, and tell the user that the report wasn't sent and why, so they can send it themselves.
```
当按计划执行代理且无人参与循环时，处理故障场景甚至更为重要。

- 测试每一个变化。软件工程师编写多种形式的测试，例如单元测试和集成测试，以帮助他们测试软件。这些测试会在每次更改时运行。有了技能，为各种场景生成自己的测试用例并在做出更改时继续添加新测试也同样重要。有多种方法可以做到这一点，但最好使用您希望下游用户使用的环境进行测试。

培养生产技能时还有很多方面需要考虑：

- 为每个更改添加发行说明。
- 将发生变化的硬编码值（例如“/Users/me/notes”或“#my-team”）保留在步骤之外，并将它们声明为每个人提供的输入。
- 用人类可读的日期记录技能何时发生变化。
- 记录每个参考文件的来源，以便如果来源发生变化，您也可以更新您的技能说明。
- 存储校验和，即技能文件的指纹，当副本与检查的版本不同时显示。
- 每次更改后检查结构，就像检查代码之前 linter 捕获错误的方式一样。
- 以一致的方式培养技能，以便您的团队可以贡献更改并更快地审查它们。

对于任何用户来说，这是一个需要考虑的事情。这就是为什么 [AWS Quick 官方目录](https://amazon-quick.github.io/Amazon-Quick-official-catalog/) 提供了预先构建的资源，例如根据这些最佳实践构建的技能。

### AWS Quick 官方目录

该目录是代理资源的集合，您可以按原样安装和使用它们，也可以将其作为起点并适应您自己的工作。该目录指出，其中的每个资源在发布之前都经过质量、安全性和其他因素的测试和扫描。这些技能涵盖日常生产力和销售、营销、人力资源、法律、项目管理、客户成功和软件工程等团队的工作。它们还涵盖金融、医疗保健和生命科学、能源和公用事业、酒店、供应链和物流等行业。

该目录包括 **Skill Architect** 技能，这是一项为您应用这些工程最佳实践的预构建技能，如[使用 AWS Quick 中的软件工程实践构建技能](https://amazon-quick.github.io/Amazon-Quick-official-catalog/build-skills/) 所述。要安装它，请选择“**自定义**”、“**技能**”、“**浏览全部**”，然后选择“**官方**”。在搜索框中输入“技能架构师”，然后选择“**安装**”。有关当前步骤，请参阅[在桌面版 AWS Quick 中安装技能](https://amazon-quick.github.io/Amazon-Quick-official-catalog/install/)。

### 将技能与您的代理联系起来

创建代理时，您可以配置其名称、描述和说明，并选择其读取的空间、可以使用的连接器以及可以加载的技能。有关详细信息，请参阅 AWS 快速用户指南中的[代理配置](https://docs.aws.amazon.com/quick/latest/userguide/agents-desktop.html#desktop-agent-configuration)。代理在解决特定用例（例如回答新员工问题或准备每周状态报告）并将其世界限制在用例所需的空间、技能和连接器时效果最佳。默认情况下，代理可以使用您的所有技能，当您添加特定技能时，代理将仅限于这些技能。当您共享代理时，这会成为问题，因为它在使用它的人的访问权限下运行。同一请求可能会为每个人提供不同的数据和技能，并且当它需要只有您可以访问的来源时，可能会返回不完整的答案。

如果您想将它们全部（代理、技能和空间）联系在一起，请尝试[个人代理架构师模块](https://catalog.us-east-1.prod.workshops.aws/workshops/a8484e57-2e30-40ee-bd98-0122f0d05acc/en-US/2000-build-your-personal-setup/2100-run-personal-agent-architect)在链接的研讨会中。

## 结论

在这篇文章中，我们展示了代理如何在 AWS Quick 中使用技能和数据，以及如何构建和分享适合您的团队的技能。我们还展示了官方目录和定制代理如何帮助您运用这些技能。

要了解更多信息、查找活动或分享您使用 AWS Quick 取得的成功，请访问 [AWS Quick 社区](https://community.amazonquick.com/)。 AWS 快速社区提供学习材料、功能公告、活动和其他用户的示例。您还可以在其问答论坛中提问。

有关本文主题的录制会议，请观看 [在 AWS Quick 上使用代理和技能对您的企业进行编码](https://www.youtube.com/watch?v=m9gN2GapOps)。该会议涵盖了技能的结构和加载方式、技能如何与代理、空间和连接器配合使用，以及构建您共享的技能的最佳实践。最后是官方目录和技能架构师技能的演示。

以下是由每天使用 AWS Quick 的专家设计的一些额外资源：

- [AWS Quick 完整指南：代理 AI 业务工作区](https://catalog.workshops.aws/amazon-quick-suite-workshop)。
- [AWS Quick：具有丰富集成的端到端业务用例](https://catalog.us-east-1.prod.workshops.aws/workshops/8724e6e3-1115-4f40-9770-8a24199ce308/en-US)。
- [AWS 快速管理研讨会](https://catalog.us-east-1.prod.workshops.aws/workshops/767bc5b8-1d33-40e2-8969-f8653db64756/en-US)。
- [深入了解 AWS Quick Sight](https://catalog.workshops.aws/quicksight/en-US)。
- [AWS Quick Knowledge Hub – 官方代码示例和解决方案](https://aws-samples.github.io/sample-amazon-quick-suite-knowledge-hub/)。
- [关于 AWS Quick 的 AWS 博客文章](https://aws.amazon.com/search/?searchQuery=Amazon%20Quick&filters=((id:provider,value:(blogs)))&sort=(id:relevance,direction:desc))。

## 关于作者
