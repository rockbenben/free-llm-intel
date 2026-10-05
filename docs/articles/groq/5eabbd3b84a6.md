---
vendor: groq
title: 新增 Kimi K2（#10）· groq/groq-changelog@3e0d869 · GitHub
original_title: Add Kimi K2 (#10) · groq/groq-changelog@3e0d869 · GitHub
url: https://github.com/groq/groq-changelog/commit/3e0d86955b531ee3a8076d0f3a1bc63260daaf72
date: 2025-07-15
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

### [CHANGELOG.md](https://github.com/groq/groq-changelog/commit/3e0d86955b531ee3a8076d0f3a1bc63260daaf72#diff-06572a96a58dc510037d5efa622f9bec8519bc1beab13c9f251e97e657a9d4ed)

行数变化：新增 43 行，删除 0 行

# Groq Changelog

## 2025-07-15 (Python SDK v0.30.0, TypeScript SDK v0.27.0)

### [CHANGED] Python SDK v0.30.0, TypeScript SDK v0.27.0

Python SDK 已更新至 v0.30.0，TypeScript SDK 已更新至 v0.27.0。

**主要变更：**

- 改进了 chat completion 消息类型定义，以更好地兼容 OpenAI。这修复了在某些不同消息格式下出现的错误。

### [ADDED] Moonshot AI Kimi 2 Instruct

[Kimi K2 Instruct](https://console.groq.com/docs/model/moonshotai/kimi-k2-instruct) 是 Moonshot AI 的尖端混合专家（MoE）语言模型，总参数量达 1 万亿，每 token 激活参数为 320 亿。该模型专为智能体智能（agentic intelligence）设计，在工具使用、编程以及跨领域的自主问题解决方面表现出色。

Kimi K2 Instruct 非常适合智能体场景和编程任务。[了解更多关于如何使用工具的信息](https://console.groq.com/docs/tool-use)。

**核心特性：**

- 131K token 上下文窗口
- 最大输出 16K token
- 采用 384 个专家的 MoE 架构（每个 token 激活 8 个专家）
- 在智能体和编程场景上超越 GPT-4.1

**性能指标：**

- LiveCodeBench Pass@1 达 53.7%（编程能力）
- SWE-bench Verified 单次尝试准确率 65.8%
- MMLU 精确匹配 89.5%
- Tau2 零售任务 Avg@4 达 70.6%

**使用示例：**

```curl
curl https://api.groq.com/openai/v1/chat/completions \
 -H "Authorization: Bearer $GROQ_API_KEY" \
 -H "Content-Type: application/json" \
 -d '{
 "model": "moonshotai/kimi-k2-instruct",
 "messages": [
 {
 "role": "user",
 "content": "Explain why fast inference is critical for reasoning models"
 }
 ]
 }'
```

## 2025-06-25 (Python SDK v0.29.0, TypeScript SDK v0.26.0)
