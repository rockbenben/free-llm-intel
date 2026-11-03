---
vendor: anthropic
title: 通过消息线程使长时间运行的代理更快
original_title: 
url: https://claude.com/resources/articles/message-threads
date: 2026-11-02
lang: zh
captured: 2026-11-03
extractor: readability-v1
translator: mt
status: translated
body_sha: efa257331639
---

消息线程现已在 Claude 平台上提供公共测试版。通过消息线程，代理不再需要每次都重新发送完整的对话历史记录，从而减少了长时间运行会话的延迟。

### 消息线程如何工作

编码代理可能在一个会话中发出数百个请求，每个请求都会重新发送每条较早的消息和工具结果。一旦对话达到数十万个令牌，重新发送所有令牌会增加Claude开始响应之前的时间。通过消息线程，代理仅发送自上一轮以来的新内容，这减少了第一个令牌 (TTFT) 的时间。

对于大多数 Claude Code 用户来说，默认情况下消息线程处于打开状态，具有 500k 到 1M 令牌的请求的 TTFT 中值下降了约 35%。

要使用消息线程，请将“thread”参数添加到消息 API 请求中。第一个请求包括完整的对话并启动一个线程。此后的每个请求仅包含新消息和先前响应的 ID。在轮流之间，我们将每个线程保存在内存中，它被加密并且不会写入磁盘。线程在最后一次请求后 5 分钟后过期，然后您的客户端重新发送完整对话以开始新的对话。虽然消息线程的每个请求都较小，但 Claude 仍然每次都会读取完整的对话，因此令牌使用量保持不变。

消息线程最适合延迟很重要的活动会话，包括：

- **长期运行的编码代理**，其中每个工具结果或文件编辑都会添加到对话中。
- **计算机使用代理**，其中屏幕截图保留在线程中，而不是每次都重新上传。
- **文档和图像密集的工作流程**，其中请求较小。

代理携带的上下文越多，可以减少第一个令牌的时间的消息线程就越多。

### 开始使用

消息线程现已在本机 Claude 平台、AWS 上的 Claude 平台、Microsoft Foundry 中的 Claude 以及 Google Cloud 上的 Claude 模型（人工管理）上提供公开测试版。标准 Claude 代币利率和现有利率限制适用。请参阅[文档](http://platform.claude.com/docs/en/build-with-claude/message-threads)开始。

文章

2026 年 10 月 28 日

### Claude Enterprise 的智能报告、调查和汇总集团预算

在许多组织中，成员已经确定了Claude可以解锁的独特工作。下一步是将这项工作扩展到每个团队。

Claude·恩企业

文章

2026 年 10 月 28 日

### IDC 将 Quanta 引入 Claude，并在整个公司采用 Claude

IDC 将 Claude 整合为其 Quanta 平台的一部分，并将 Claude 推广到自己的业务中

Claude·科沃克

Claude·科德

还有 1 个

：Claude·企业

Claude·恩企业

文章

2026 年 10 月 28 日

### 为法律工作引入工件

Claude for Legal 现在包含用于法律工作的即用型工件，团队可以使用自己的数据和连接器进行调整，并在整个企业中共享。

Claude·恩企业

文章

2026 年 10 月 27 日

### 财务顾问Claude

财务顾问现在可以将 Claude 连接到他们所依赖的托管人、投资组合平台、CRM 和规划工具，以及针对财务顾问日常工作量身定制的新技能。

## 与 Claude 一起改变您的组织的运作方式

[查看定价](https://claude.com/pricing#api)[联系销售人员](https://claude.com/contact-sales)

### 获取开发者通讯

产品更新、操作方法、社区焦点等等。每月发送到您的收件箱。

如果您想接收我们的每月开发者通讯，请提供您的电子邮件地址。您可以随时取消订阅。
