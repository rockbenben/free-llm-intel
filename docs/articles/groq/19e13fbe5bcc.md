---
vendor: groq
title: GPT-OSS 20B 启用提示词缓存
original_title: 
url: https://console.groq.com/docs/changelog.md#prompt-caching-enabled-for-gptoss-20b
date: 2025-09-25
lang: zh
captured: 2026-10-08
extractor: readability-v1
translator: agent
status: translated
body_sha: abc18f80c46e
---

# GPT-OSS 20B 启用提示词缓存

### 新增[为 GPT-OSS 20B 启用 prompt caching](#prompt-caching-enabled-for-gptoss-20b)

[openai/gpt-oss-20b](https://console.groq.com/docs/model/openai/gpt-oss-20b) 现已启用自动 prompt caching。缓存命中会自动带来：

* 缓存的输入 token **节省 50% 成本**（$0.037/M 对比 $0.075/M）
* 通过复用计算带来**更低的延迟**
* **自动前缀匹配**，让缓存利用无缝衔接

无需任何配置 —— 当你的请求与近期请求共享相同前缀时，你会自动从缓存中受益。[了解更多关于 prompt caching 的信息](https://console.groq.com/docs/prompt-caching)。

---
