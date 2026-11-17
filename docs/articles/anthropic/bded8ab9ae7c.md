---
vendor: anthropic
title: 使用 mods 自定义 Claude Code
original_title: 
url: https://claude.com/resources/articles/claude-code-mods
date: 2026-10-01
lang: zh
captured: 2026-11-17
extractor: readability-v1
translator: agent
status: translated
body_sha: 6bb44854e9c7
---

今天我们推出 mods：一些小巧的 TypeScript 函数，用来改变 Claude Code 的工作方式。一个 mod 可以重写 prompt、添加新的 UI、替换内置功能，或者加入全新的功能。你可以自己写一个 mod，也可以让 Claude Code 替你写。mods 打包在 plugin 中发布，因此你能像安装、分享任何 plugin 一样安装和分享它们。它们在 Claude Code CLI 和桌面应用中都能用。

mods 运行时对机器的访问权限与 Claude Code 本身相同。它们不受沙箱隔离，因此你只应从信任的来源安装 mods——就像在电脑上安装任何代码那样。

想了解 mods 能做什么，请[阅读我们关于构建第一个 mod 的指南](https://claude.dev/blog/getting-started-with-claude-code-mods/)。

### 我们为什么做 mods

开发者一直希望更多地掌控 Claude Code 的工作方式，而不用等我们发布某个功能。[Hooks](https://code.claude.com/docs/en/hooks) 让用户掌握了一部分控制权，但 hooks 无法重写事件、绘制新的 UI，也无法替换功能。mods 可以。

我们希望 Claude Code 感觉像是你自己的工具，让你能把它塑造成契合自己工作方式的样子。发布之前，我们[在 GitHub 上公开了 mods 的设计](https://github.com/anthropics/claude-code/issues/91870)，以收集开发者的反馈。感谢每一位提出意见的人。

### mods 如何工作

Claude Code 每做一件事，都会发出一个事件。例子包括调用工具、请求权限，以及绘制屏幕的某一部分。mod 就是一个挂接到这些事件之一上的函数。mod 可以在事件之前运行、在事件之后运行，也可以代替该事件运行。它还能包裹事件，在事件前后都执行代码。只用一个函数，mod 就能：

- 在 prompt 到达模型之前重写它。
- 拦截、重写或重试工具调用。
- 批准或拒绝权限请求。
- 在 Claude 读取之前，从工具输出中抹掉秘密信息。

mod 还能改变你看到的内容。它可以编辑或替换 Claude Code 绘制的界面的一部分，比如一条工具结果或 Claude 提出的问题。它可以添加按钮和输入框，而其他 mod 可以在你按下这些按钮时作出响应。目前，一个 mod 可以面向终端、桌面应用，或两者同时。

当多个 mod 挂接到同一个事件时，它们按加载顺序运行。最先加载的 mod 最先看到事件，最后看到结果。这样你就能把来自不同作者的 mods 叠加使用。

你也可以用 Claude Code 给 Claude Code 做 mod。让 Claude 创建一个 mod，它可以编写 TypeScript、安装它，并在你的会话中热重载它。

### 用你自己的实现替换内置功能

Claude Code 的一些内置功能现在以 mod 的形式发布。例如，内置的 `/diff` 功能现在就是一个 mod，你可以在 `/plugin` 中把它关掉，也可以用自己的版本替换它。我们计划逐步把更多内置功能迁移为 mods，这样你就能把 Claude Code 精简到一个小小的核心，只把想要的部分加回来。

### 面向团队与企业的 mods

mods 随 plugin 一起发布，因此你现有的 plugin 管控措施仍然适用。管理员可以允许或禁止 plugin 市场。在 Team 和 Enterprise 套餐中，由所有者（owner）在管理控制台中设置；在 Claude API 和第三方 API 套餐中，管理员把 managed settings 推送到用户的机器上。

在 Team 和 Enterprise 套餐上，以及任何配置了 managed settings 的机器上，一个名为 `sec-default`（“security default”，即安全默认值）的内置 mod 会最先加载。它会阻止用户安装的 mods 做出有风险的事情，比如覆盖你的权限拒绝规则。你可以[查看源代码](http://github.com/anthropics/claude-code/tree/main/mods)，了解它限制了哪些行为。管理员也可以改为先加载自己的 mods；如果这样做，请把 `sec-default` 加入你的列表，以保留它的限制。

团队还可以用 mods 构建自己的管控能力和功能。例如：

- **CI/CD 状态：**mod 可以在对话旁边的面板中显示流水线状态，并在构建通过或失败时更新它。
- **生产环境防护：**mod 可以要求任何触碰生产配置的命令都先经过确认。
- **审计日志：**最先加载的 mod 可以记录其他每个 mod 发起的每一次调用。

### 开始使用

mods 现在已在 Claude Code CLI 和桌面应用中可用。你可以从 [Claude directory](https://claude.ai/directory) 安装包含 mods 的 plugins，也可以在 CLI 中运行 `/plugin`。要分享一个 mod，把它打包进 plugin，然后[提交到 directory](https://claude.ai/directory/manage)。

要构建自己的 mods，请阅读我们的[入门指南](https://claude.dev/blog/getting-started-with-claude-code-mods/)，或查看[文档](https://code.claude.com/docs/en/plugins/mods/overview)。

文章

2026 年 11 月 12 日

### 在你的安全边界内运行 Claude Managed Agents

推出自托管的 Claude Managed Agents。现在你可以在自己的环境中运行 agents，无论环境是你自己的云还是在本地。agents、凭据和会话历史都由你托管，你还可以选择将发往 Claude 的请求送到哪里。

Claude PlatformClaude Managed Agents

文章

2026 年 11 月 12 日

### 推出 Claude for Manufacturing

一个包含 17 个 skills 和 4 个 connectors 的新 plugin，帮助制造商基于现有系统起草报价、质量报告和供应商请求。

文章

2026 年 11 月 12 日

### 推出 Claude Meetings

把 Claude 加入你的视频通话，边聊边把工作启动起来。

文章

2026 年 11 月 10 日

### 你的应用现在可以在 Claude 中打开，Claude 也能在其中工作

我们的合作伙伴现在可以把他们的应用直接嵌入 Claude，让你和 Claude 在同一个工具、同一个屏幕上协作，无需切换标签页。

Claude appsMCP

## 用 Claude 改变组织的运作方式

[查看定价](https://claude.com/pricing#api)[联系销售](https://claude.com/contact-sales)

### 获取开发者通讯

产品更新、操作指南、社区聚焦等内容，每月送达你的收件箱。

想接收我们的每月开发者通讯，请留下你的邮箱地址。你可以随时取消订阅。
