---
vendor: openrouter
title: 新功能：推理流、加密货币发票、终端用户 ID 等
original_title: New Features: Reasoning Streams, Crypto Invoices, End-User IDs & More
url: https://openrouter.ai/blog/announcements/new-features-reasoning-streams-crypto-invoices-end-user-ids-and-more
date: 2025-05-28
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

我们正在积极扩充 Claude 4 和 Gemini 2.5 的容量——与此同时，多项呼声很高的功能现已可用：

## 🧠 o3 推理摘要流式输出

OpenAI 的 o3 和 o4-mini 模型现已支持通过 OpenRouter Chat Completions API 流式输出推理摘要。
 实机演示：[https://x.com/OpenRouterAI/status/1927755349030793504](https://x.com/OpenRouterAI/status/1927755349030793504)

## 🧑‍🤝‍🧑 提交终端用户 ID

现在可以在每个请求中附带可选的用户字段，帮助防止滥用、改进内容审核，并实现按用户追踪用量。
 文档：[https://openrouter.ai/docs/api/reference/chat-completion#request.body.user](https://openrouter.ai/docs/api/reference/chat-completion#request.body.user)

## 📜 加密货币发票

现在可以在 /credits 页面一键生成发票，直接用加密货币支付。

## 🔑 强制使用你自己的第三方密钥

通过在模型配置中切换此设置，确保某个特定服务商只使用你的 API 密钥（例如你自己的 OpenAI 密钥）。

## 🛠️ 其他功能

- 2FA 支持——在账户设置中配置双因素认证和 Passkeys，安全更强。
- AI SDK 更新——新增用量统计和 PDF 解析支持。
