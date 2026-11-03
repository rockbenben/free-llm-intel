---
vendor: anthropic
title: 用 message threads 让长时间运行的 agent 更快
original_title: 
url: https://claude.com/resources/articles/message-threads
date: 2026-11-02
lang: zh
captured: 2026-11-03
extractor: readability-v1
translator: agent
status: translated
body_sha: 36f3f7adb78b
---

Message threads 现已在 Claude Platform 上开放 public beta。有了 message threads，agents 不再需要在每一轮重新发送完整的对话历史，从而降低了长时间运行会话的延迟。

### message threads 如何工作

一个 coding agent 在一次会话里可能发出数百个请求，而每个请求都会把此前所有消息和工具结果重发一遍。一旦对话累积到数十万个 tokens，这样整份重发就会在 Claude 开始响应之前额外加上时间。有了 message threads，agents 只需要发送上一轮之后的新增内容，从而缩短 time to first token（TTFT）。

在 message threads 对多数 Claude Code 用户默认开启之后，token 量在 500k 到 1M 之间的请求，其中位 TTFT 下降了约 35%。

要使用 message threads，请在 Messages API 请求里加上 `thread` 参数。第一个请求包含完整对话，并开启一个 thread。之后的每个请求只包含新增消息和上一个响应的 ID。在两轮之间，我们把每个 thread 保存在内存中，在那里它是加密的且不会写入磁盘。一个 thread 在其最后一次请求 5 分钟后过期，届时你的客户端会重发完整对话来开启一个新的。虽然用上 message threads 后每个请求都更小，但 Claude 每一轮仍然读取完整对话，所以 token 用量保持不变。

message threads 最适合那些在意延迟的活跃会话，包括：

- **长时间运行的 coding agents**，每个工具结果或文件编辑都会往对话里累加。
- **Computer use agents**，截图留在 thread 里，而不必每一轮都重新上传。
- **文档和图片量大的工作流**，请求因此变得更小。

一个 agent 携带的上下文越多，message threads 能在 time to first token 上省下的就越多。

### 开始使用

message threads 现已在原生 Claude Platform 上开放 public beta，同时也支持 Claude Platform on AWS、Claude in Microsoft Foundry，以及 Claude Models on Google Cloud（Anthropic 托管）。适用标准的 Claude token 费率和现有的限流。请查阅[文档](http://platform.claude.com/docs/en/build-with-claude/message-threads)开始使用。

文章

2026 年 10 月 28 日

### Claude Enterprise 的智能报告、调研与群组预算池化

在许多组织里，成员们已经找到了 Claude 能够释放出来的独特工作。下一步是把这种工作扩展到每一个团队。

Claude Enterprise

文章

2026 年 10 月 28 日

### IDC 把 Quanta 接入 Claude，并在全公司采用 Claude

IDC 已把 Claude 集成进自己的 Quanta 平台，并在自身业务中全面铺开了 Claude

Claude Cowork

Claude Code

还有 1 个

：Claude Enterprise

Claude Enterprise

文章

2026 年 10 月 28 日

### 推出面向法律工作的 artifacts

Claude for Legal 如今加入了开箱即用的法律工作 artifacts，团队可以结合自己的数据和连接器加以调整，并在整个业务中共享。

Claude Enterprise

文章

2026 年 10 月 27 日

### Claude for Financial Advisors

理财顾问如今可以把 Claude 连到他们依赖的托管机构、投资组合平台、CRM 和规划工具上，此外还有针对理财顾问日常工作定制的新 skills。

## 用 Claude 变革你的组织运作方式

[查看定价](https://claude.com/pricing#api)[联系销售](https://claude.com/contact-sales)

### 订阅开发者通讯

产品更新、操作指南、社区亮点，以及更多内容。每月送达你的收件箱。

如果你希望接收我们每月的开发者通讯，请提供你的电子邮箱地址。你可以随时退订。
