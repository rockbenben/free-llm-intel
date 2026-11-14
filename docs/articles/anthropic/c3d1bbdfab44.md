---
vendor: anthropic
title: 在自己的安全边界内运行 Claude Managed Agents
original_title: 
url: https://claude.com/resources/articles/self-hosted-claude-managed-agents
date: 2026-11-12
lang: zh
captured: 2026-11-14
extractor: readability-v1
translator: agent
status: translated
body_sha: 058ea27bb580
---

[自托管 Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/self-hosted) 现已开放私有测试。开发者可以构建直接作用于公司代码和内部系统的 agents，并在自己的环境中运行它们。

自托管是运行 [Managed Agents](https://claude.com/platform/claude-managed-agents) 的一种新方式——它是一套可组合的 API，用来构建和部署自主 agents。Managed Agents 提供 agent harness、沙箱、凭据处理和会话历史，让长时间运行的 agents 得以进入生产环境。

## 在自己的环境中运行 agent 控制平面

我们最初把 Managed Agents 作为 Claude Platform 上的托管服务推出，由 Anthropic 替你运行基础设施。对于需要把代码留在自己环境里的团队，我们后来加入了[自托管沙箱](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes)。

此后，agents 能力更强，承担起更要紧的活儿：修复坏掉的构建、测试发布版本、分诊告警、清理 bug backlog。它们在你的代码上无人值守地运行，也需要访问你的内部系统。对拥有这种访问级别的 agents，有些团队希望整套服务都放在自己的环境里，而不只是沙箱。在此之前，这意味着得自己把平台搭出来。

有了自托管 Managed Agents，服务的每个部分都跑在你自己的云或本地，包括 harness、沙箱、凭据和会话历史。你负责运维 Managed Agents 服务器、它的数据库，以及 agents 运行 shell 和文件工具的 worker。模型请求发往哪里由你定：可以直接发给 Anthropic，也可以走你的云厂商（Amazon Bedrock、Google 的 Agent Platform 或 Microsoft Foundry），或者你自己的网关。你的开发者仍用与托管版 Managed Agents 服务相同的核心 API 来构建 agents。

会话历史存在你自己的数据库里。如果你的组织与 Anthropic 之间启用了[零数据保留（ZDR）](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#zero-data-retention-zdr-scope)，它对发送给 Claude 的请求同样适用，与任何其他 Messages API 调用一致。

![图 1：自托管 Claude Managed Agents](https://assets.claude.com/7607c90e3d3d6e3bf9f7d1af0d39afb006be1413.svg)

## 为 agent 安全而设计

当 agent 在你的代码和系统里无人值守地运行，你没法指望有人逐步盯着，所以限制必须做进系统本身。这就是为什么 agent 安全要从架构抓起，也是我们围绕四条原则设计 Managed Agents 的原因。无论由 Anthropic 托管全部、你只托管沙箱，还是你托管整套服务，这些原则都适用。

**大脑与双手分开**

harness（大脑）负责调用 Claude，沙箱（双手）是 agent 代码运行的地方，两者在设计上刻意分开。agent 的代码跑在沙箱里，而 agent loop、会话历史和 vault 机密都留在它之外。[把两者分开](https://www.anthropic.com/engineering/managed-agents)还意味着 agent 不必依赖某一个沙箱撑完整轮运行：沙箱只在工具需要时才启动，会话历史则以事件日志的形式存在于沙箱之外。

**凭据不进沙箱**

Vault 的设计目的就是把凭据挡在沙箱之外。对 MCP 工具和受支持的 API 调用，[由沙箱外的代理把凭据加进请求](https://platform.claude.com/docs/en/managed-agents/vaults)。用自托管 Managed Agents 时，你也可以把凭据存进自己的 secrets manager。

**网络访问可以收紧**

你可以把每个环境限制在[一份允许访问的主机列表](https://platform.claude.com/docs/en/managed-agents/secure-deployment)内，发往其他主机的请求一律拦截。对修复坏掉构建的 agent 来说，这份名单可能只有你的 git 主机和包仓库。沙箱由你自己托管时，同样的限制就设在自己的防火墙里。

**每次会话都留下完整记录**

Managed Agents 会记下 agent 走过的每一步，包括它发起的工具调用和返回的结果。记录通过 [OpenTelemetry](https://platform.claude.com/docs/en/manage-claude/opentelemetry) 导出，你可以送进已在用的监控工具，和其他系统一起查看 agent 的活动。

## 开始使用

自托管 Claude Managed Agents 现已开放私有测试。可联系你的 Anthropic 客户团队申请开通，或阅读[文档](https://platform.claude.com/docs/en/managed-agents/self-hosted)了解更多。

文章

2026 年 11 月 12 日

### 推出 Claude for Manufacturing

一款含 17 个 skills 和 4 个 connectors 的新插件，帮制造商从已在运行的系统里起草报价、质量报告和供应商询价。

文章

2026 年 11 月 12 日

### 推出 Claude Meetings

把 Claude 加进视频通话，边聊边把活儿开起来

文章

2026 年 11 月 10 日

### 你的应用现在能在 Claude 里打开，Claude 也能在其中工作

我们的合作伙伴现在可以把应用直接嵌进 Claude，让你和 Claude 在同一个工具、同一块屏幕上协作，无需切换标签页。

Claude appsMCP

文章

2026 年 11 月 10 日

### 与 Claude 协作的更多方式：Sheets、Whiteboards 和 Interactive Connectors

以思考的速度工作

Claude apps

## 用 Claude 改变组织的运作方式

[查看定价](https://claude.com/pricing#api)[联系销售](https://claude.com/contact-sales)

### 订阅开发者通讯

产品更新、操作指南、社区聚焦，以及更多内容。每月送达你的收件箱。

如需接收我们的每月开发者通讯，请留下你的邮箱地址。你可以随时取消订阅。
