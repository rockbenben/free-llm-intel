---
vendor: anthropic
title: 在您的安全范围内操作 Claude Managed Agents
original_title: 
url: https://claude.com/resources/articles/self-hosted-claude-managed-agents
date: 2026-11-12
lang: zh
captured: 2026-11-13
extractor: readability-v1
translator: mt
status: translated
body_sha: c2acb2471283
---

[自托管 Claude Managed Agents](https://platform.claude.com/docs/en/management-agents/self-hosted) 现已推出内测版。开发人员可以构建直接在公司代码和内部系统中工作的代理，并在自己的环境中运行这些代理。

自托管是运行[托管代理](https://claude.com/platform/claude-management-agents)的一种新方式，这是一套用于构建和部署自主代理的可组合 API。托管代理提供代理工具、沙箱、凭证处理和会话历史记录，以使长期运行的代理投入生产。

## 在您自己的环境中运行代理控制平面

我们首先在 Claude 平台上推出托管代理作为托管服务，Anthropic 在该平台上为您运行基础设施。对于需要将代码保留在自己的环境中的团队，我们添加了[自托管沙箱](https://platform.claude.com/docs/en/management-agents/self-hosted-sandboxes)。

从那时起，代理变得更加有能力，并承担更重要的工作，例如修复损坏的构建、测试版本、对警报进行分类以及处理错误积压。它们在您的代码上无人值守地运行，并且需要访问您的内部系统。对于具有该级别访问权限的代理，一些团队希望在自己的环境中获得整个服务，而不仅仅是沙箱。到目前为止，这意味着自己构建平台。

通过自托管托管代理，服务的每个部分都在您自己的云或本地运行，包括工具、沙箱、凭据和会话历史记录。您可以操作托管代理服务器、其数据库以及代理运行 shell 和文件工具的工作线程。模型请求将发送至您选择的位置，无论是直接由 Anthropic、您的云提供商（Amazon Bedrock、Google 的代理平台或 Microsoft Foundry）还是您自己的网关。您的开发人员仍然使用与托管托管代理服务相同的核心 API 来构建代理。

会话历史记录存储在您自己的数据库中。如果您的组织使用 Anthropic 实现了[零数据保留 (ZDR)](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#zero-data-retention-zdr-scope)，则它适用于发送给 Claude 的请求，方式与任何其他消息 API 调用相同。

![图 1：自托管 Claude 托管代理](https://assets.claude.com/7607c90e3d3d6e3bf9f7d1af0d39afb006be1413.svg)

## 专为代理安全而设计

当代理在代码和系统中无人值守地运行时，您不能依赖人员检查每个步骤，因此必须将限制内置到系统本身中。这就是代理安全性从架构开始的原因，也是我们围绕四个原则设计托管代理的原因。无论 Anthropic 托管所有内容、仅托管沙箱还是托管整个服务，这些原则都适用。

**大脑和手分开**

线束（大脑）调用Claude，沙箱（手）是代理代码运行的地方。它们在设计上是分开的。代理的代码在沙箱中运行，而代理循环、会话历史记录和保管库机密则保留在沙箱之外。 [将它们分开](https://www.anthropic.com/engineering/managed-agents)还意味着代理不依赖于一个沙箱在整个运行过程中幸存，沙箱仅在工具需要它们时启动，并且会话历史记录作为事件日志存在于沙箱之外。

**凭证远离沙箱**

保险库旨在将凭证排除在沙箱之外。对于 MCP 工具和支持的 API 调用，[沙箱外部的代理将凭证添加到请求中](https://platform.claude.com/docs/en/management-agents/vaults)。通过自托管托管代理，您还可以将凭据存储在您自己的机密管理器中。

**网络访问可能受到限制**

您可以将每个环境限制为[允许的主机列表](https://platform.claude.com/docs/en/management-agents/secure-deployment)，并阻止对任何其他主机的请求。对于修复损坏的构建的代理，该列表可能只是您的 git 主机和包注册表。当您自己托管沙箱时，您可以在自己的防火墙中设置相同的限制。

**每一次会话都会留下完整的记录**

托管代理会记录代理所采取的每一步，包括其发出的工具调用以及返回的内容。该记录通过 [OpenTelemetry](https://platform.claude.com/docs/en/manage-claude/opentelemetry) 导出，因此您可以将其发送到您已使用的监控工具，并与其他系统一起查看代理活动。

## 开始吧

自托管的 Claude Managed Agents 现已推出内测版。请联系您的 Anthropic 帐户团队请求访问权限，或阅读[文档](https://platform.claude.com/docs/en/management-agents/self-hosted)以了解更多信息。

文章

2026 年 11 月 12 日

### 介绍制造领域的Claude

具有 17 项技能和 4 个连接器的新插件可帮助制造商从他们已运行的系统起草报价、质量报告和供应商请求。

文章

2026 年 11 月 12 日

### 介绍Claude会议

将 Claude 添加到您的视频通话中，并在通话时开始工作

文章

2026 年 11 月 10 日

### 您的应用程序现在可以在 Claude 中打开，并且 Claude 可以在其中工作

我们的合作伙伴现在可以将他们的应用程序直接嵌入到 Claude 中，这样您和 Claude 就可以在同一屏幕上使用同一个工具，而无需切换选项卡。

Claude·应用MCP

文章

2026 年 11 月 10 日

### 与 Claude 合作的更多方式：表格、白板和交互式连接器

以思考的速度工作

Claude应用程序

## 与 Claude 一起改变您的组织的运作方式

[查看定价](https://claude.com/pricing#api)[联系销售人员](https://claude.com/contact-sales)

### 获取开发者通讯

产品更新、操作方法、社区焦点等等。每月发送到您的收件箱。

如果您想接收我们的每月开发者通讯，请提供您的电子邮件地址。您可以随时取消订阅。
