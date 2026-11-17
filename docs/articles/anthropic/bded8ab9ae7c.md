---
vendor: anthropic
title: 使用 mods 自定义 Claude Code
original_title: 
url: https://claude.com/resources/articles/claude-code-mods
date: 2026-10-01
lang: zh
captured: 2026-11-17
extractor: readability-v1
translator: llm
status: translated
body_sha: 58e65609469a
---

今天我们推出 mods——一些小型的 TypeScript 函数，用来改变 Claude Code 的工作方式。一个 mod 可以重写提示词、添加新的 UI、替换内置功能，或者添加全新的功能。你可以自己编写 mod，也可以让 Claude Code 为你编写。Mods 以插件的形式发布，因此你可以像安装和分享任何插件一样安装和分享它们。它们可在 Claude Code CLI 和桌面应用中使用。

Mods 运行时对你机器的访问权限与 Claude Code 本身相同。它们没有沙箱隔离，因此你只应从你信任的来源安装 mods，就像你在计算机上安装任何代码一样。

要了解 mods 能做什么，请[阅读我们关于构建第一个 mod 的指南](https://claude.dev/blog/getting-started-with-claude-code-mods/)。

### 我们为什么构建 mods

开发者们希望获得更多对 Claude Code 工作方式的控制，而不必等待我们发布某个功能。[Hooks](https://code.claude.com/docs/en/hooks) 曾帮助用户获得部分此类控制，但 hooks 无法重写事件、绘制新的 UI 或替换功能。Mods 可以做到。

我们希望 Claude Code 让你感觉它是属于你的，从而可以按照你的工作方式塑造它。在发布之前，我们[在 GitHub 上分享了 mods 的设计](https://github.com/anthropics/claude-code/issues/91870)，以征求开发者的反馈。感谢所有提出意见的人。

### Mods 如何工作

每当 Claude Code 执行某项操作时，它都会发出一个事件。例如调用工具、请求权限，以及绘制屏幕的一部分。一个 mod 就是挂接到这些事件之一上的函数。Mod 可以在事件之前、之后或代替事件运行。它还可以包装事件，在事件前后都运行代码。借助一个函数，一个 mod 可以：

- 在提示词到达模型之前重写它。
- 阻止、重写或重试工具调用。
- 批准或拒绝权限请求。
- 在 Claude 读取工具输出之前，将其中的机密信息遮盖掉。

Mod 还可以改变你所看到的内容。它可以编辑或替换 Claude Code 绘制的部分界面，例如工具结果或 Claude 提出的问题。它可以添加按钮和输入框，其他 mod 可以在你按下按钮时做出响应。目前，一个 mod 可以针对终端、桌面应用或两者。

当多个 mods 挂接到同一个事件时，它们会按加载顺序运行。最先加载的 mod 最先看到事件，最后看到结果。这让你可以叠加来自不同作者的各种 mods。

你也可以用 Claude Code 来为 Claude Code 写 mod。让 Claude 创建一个 mod，它可以编写 TypeScript、安装它，并在你的会话中热重载它。

### 用你自己的功能替换内置功能

Claude Code 的一些内置功能现在以 mods 形式发布。例如，内置的 `/diff` 功能现在就是一个 mod，因此你可以（在 `/plugin` 中）关掉它，或用自己的版本替换它。我们计划逐步将更多内置功能迁移为 mods，这样你就能把 Claude Code 精简到一个小型内核，只把想要的功能加回来。

### 面向团队和企业的 mods

Mods 以插件形式发布，因此你现有的插件管控措施同样适用。管理员可以允许或阻止插件市场。在 Team 和 Enterprise 方案中，由所有者在管理控制台中设置这一点。在 Claude API 和第三方 API 方案中，管理员会将受管设置推送到用户的机器上。

在 Team 和 Enterprise 方案中，以及在任何配置了受管设置的机器上，会首先加载一个名为 `sec-default`（“security default”，安全默认）的内置 mod。它会阻止用户安装的 mods 做出有风险的操作，例如覆盖你的权限拒绝规则。你可以[查看源代码](http://github.com/anthropics/claude-code/tree/main/mods)，了解它限制了哪些操作。管理员也可以改为先加载自己的 mods。如果这样做，请把 `sec-default` 加入你的列表，以保留其限制。

团队还可以用 mods 构建自己的管控措施和功能。例如：

- **CI/CD 状态：**mod 可以在对话旁边的窗格中显示你的流水线状态，并在构建通过或失败时更新。
- **生产防护：**mod 可以要求在执行任何涉及生产配置的命令前进行确认。
- **审计日志：**最先加载的 mod 可以记录其他每个 mod 发起的每一次调用。

### 开始使用

Mods 现已在 Claude Code CLI 和桌面应用中可用。你可以从 [Claude 目录](https://claude.ai/directory) 安装包含 mods 的插件，或在 CLI 中运行 `/plugin`。要分享一个 mod，请将其打包进插件并[提交到目录](https://claude.ai/directory/manage)。

要构建你自己的 mods，请阅读我们的[入门指南](https://claude.dev/blog/getting-started-with-claude-code-mods/)，或查阅[文档](https://code.claude.com/docs/en/plugins/mods/overview)。

文章

2026年11月12日

### 在你的安全边界内运行 Claude Managed Agents

推出自托管的 Claude Managed Agents。现在你可以在自己的环境中运行 agents，无论是自有云还是本地部署。你托管 agents、凭证和会话历史，并选择向 Claude 发送请求的位置。

Claude PlatformClaude Managed Agents

文章

2026年11月12日

### 推出面向制造业的 Claude

一个包含 17 项 skills 和四个 connectors 的新插件，帮助制造商基于其现有运行的系统起草报价单、质量报告和供应商请求。

文章

2026年11月12日

### 推出 Claude Meetings

将 Claude 加入你的视频通话，在你们交谈的同时就开始推进工作

文章

2026年11月10日

### 你的应用现在可以在 Claude 中打开，Claude 也能在其中工作

我们的合作伙伴现在可以将其应用直接嵌入 Claude，这样你和 Claude 就能在同一个工具、同一个屏幕上工作，无需切换标签页。

Claude appsMCP

## 借助 Claude 转变你的组织运作方式

[查看定价](https://claude.com/pricing#api)[联系销售](https://claude.com/contact-sales)

### 订阅开发者简报

产品更新、操作指南、社区亮点等，每月发送到你的收件箱。

如果你希望收到我们每月的开发者简报，请提供你的电子邮箱地址。你可以随时退订。
