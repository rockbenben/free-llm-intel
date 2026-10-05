---
vendor: groq
title: 新增 Qwen3 与 SDK 更新（#8）· groq/groq-changelog@edee777 · GitHub
original_title: Add Qwen3 + SDK updates (#8) · groq/groq-changelog@edee777 · GitHub
url: https://github.com/groq/groq-changelog/commit/edee777a205934fcd2ddef6cc045099ddf4c129a
date: 2025-06-13
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

### [CHANGELOG.md](https://github.com/groq/groq-changelog/commit/edee777a205934fcd2ddef6cc045099ddf4c129a#diff-06572a96a58dc510037d5efa622f9bec8519bc1beab13c9f251e97e657a9d4ed)

行数变化：新增 61 行，删除 0 行

# Groq Changelog

## 2025-06-12 (Python SDK v0.28.0, TypeScript SDK v0.25.0)

### [UPDATED] Python SDK v0.28.0, TypeScript SDK v0.25.0

Python SDK 已更新至 v0.28.0，TypeScript SDK 已更新至 v0.25.0。

**主要变更：**

 - 为 chat completion 的 assistant 消息新增 `reasoning` 字段。当 [`reasoning_format`](https://console.groq.com/docs/reasoning#options-for-reasoning-format) 设置为 `"parsed"` 时，该字段是 assistant 输出的推理内容。此字段仅可与 Qwen 3 模型配合使用。
 - 为 Qwen 3 模型（目前仅 [`qwen/qwen3-32b`](https://console.groq.com/docs/model/qwen3-32b)）新增 [`reasoning_effort`](https://console.groq.com/docs/reasoning#options-for-reasoning-effort) 参数。设置为 `"none"` 可禁用推理。

## 2025-06-11 (Python SDK v0.27.0, TypeScript SDK v0.24.0)

### [ADDED] Qwen 3 32B

[Qwen 3 32B](https://console.groq.com/docs/model/qwen3-32b) 是 Qwen 系列最新一代大语言模型，在推理、指令遵循、智能体能力和多语言支持方面带来突破性进展。该模型独有的特性是可以在[思考模式](https://console.groq.com/docs/reasoning)（面向复杂逻辑推理、数学和编程）与[非思考模式](https://console.groq.com/docs/reasoning#options-for-reasoning-effort)之间无缝切换。

**核心特性：**

- 128K token 上下文窗口
- 支持 100 多种语言和方言
- 支持工具调用与 JSON 模式
- token 生成速度约 491 TPS
- 输入 token 价格：$0.29/1M tokens
- 输出 token 价格：$0.59/1M tokens

**性能指标：**

- ArenaHard 得分 93.8%
- AIME 2024 通过率 81.4%
- LiveCodeBench 65.7%
- BFCL 30.3%
- MultiIF 73.0%
- AIME 2025 72.9%
- LiveBench 71.6%

**使用示例：**

```sh
curl "https://api.groq.com/openai/v1/chat/completions" \
 -X POST \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer ${GROQ_API_KEY}" \
 -d '{
 "messages": [
 {
 "role": "user",
 "content": "Explain why fast inference is critical for reasoning models"
 }
 ],
 "model": "qwen/qwen3-32b",
 "reasoning_effort": "none"
 }'
```

### [CHANGED] Python SDK v0.27.0, TypeScript SDK v0.24.0

Python SDK 已更新至 v0.26.0，TypeScript SDK 已更新至 v0.23.0。

**主要变更：**

 - 使用[智能体工具体系](https://console.groq.com/docs/agentic-tooling)时，`search_settings` 参数新增字段：`include_images`。设为 `true` 则搜索结果包含图片，设为 `false` 则排除图片。
 - 使用[智能体工具体系](https://console.groq.com/docs/agentic-tooling)时，为每个已执行的工具输出新增 `code_results`。该字段可包含 `png`（当代码执行产生图片时，以 Base64 格式编码）和 `text`（代码执行的文本输出）。

## 2025-05-29 (Python SDK v0.26.0, TypeScript SDK v0.23.0)

### [CHANGED] Python SDK v0.26.0, TypeScript SDK v0.23.0
