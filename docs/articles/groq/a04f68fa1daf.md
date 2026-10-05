---
vendor: groq
title: 新增提示缓存（#14）· groq/groq-changelog@fc1e7dc · GitHub
original_title: Add prompt caching (#14) · groq/groq-changelog@fc1e7dc · GitHub
url: https://github.com/groq/groq-changelog/commit/fc1e7dc66859b831b42594389098d756e06fcd0c
date: 2025-08-20
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

### [CHANGELOG.md](https://github.com/groq/groq-changelog/commit/fc1e7dc66859b831b42594389098d756e06fcd0c#diff-06572a96a58dc510037d5efa622f9bec8519bc1beab13c9f251e97e657a9d4ed)

行数变化：新增 16 行，删除 0 行

# Groq Changelog

## 2025-08-20 (Python SDK v0.31.0, TypeScript SDK v0.30.0)

### [ADDED] Prompt Caching（提示缓存）

提示缓存会在近期请求共享公共前缀时自动复用其计算结果，从而大幅节省成本并改善响应时间；同时数据只存储在会自动过期的易失性存储中，保障了隐私。

**工作原理**

- 前缀匹配：发送请求时，系统会检查并识别来自临时存储在易失性内存中的近期已处理请求的匹配前缀。前缀可以包含系统提示、工具定义、few-shot 示例等。
- 缓存命中：若找到匹配前缀，则复用已缓存的计算，显著降低延迟，缓存部分的 token 成本降低 50%。
- 缓存未命中：若不存在匹配，你的提示会正常处理，同时其前缀会被临时缓存以供未来匹配。
- 自动过期：所有缓存数据会在数小时内自动过期，在保留收益的同时保障隐私。

提示缓存自今日起在 [Kimi K2](https://console.groq.com/docs/model/moonshotai/kimi-k2-instruct) 上推出，后续将支持更多模型。该功能在你的所有 API 请求上自动生效，无需改动代码，也不产生额外费用。

[在我们的文档中了解更多关于提示缓存的信息。](https://console.groq.com/docs/prompt-caching)

## 2025-08-05 (Python SDK v0.31.0, TypeScript SDK v0.30.0)

### [ADDED] OpenAI GPT-OSS 20B & OpenAI GPT-OSS 120B
