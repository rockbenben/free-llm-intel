---
vendor: groq
title: Groq Compound 与 Compound Mini 发布
original_title: 
url: https://console.groq.com/docs/changelog.md#groq-compound-and-compound-mini
date: 2025-09-04
lang: zh
captured: 2026-10-08
extractor: readability-v1
translator: agent
status: translated
body_sha: f754ef960d1d
---

# Groq Compound 与 Compound Mini 发布

### 新增[Groq Compound 与 Compound Mini](#groq-compound-and-compound-mini)

[Compound](https://console.groq.com/docs/compound/systems/compound)（`groq/compound`）和 [Compound Mini](https://console.groq.com/docs/compound/systems/compound-mini)（`groq/compound-mini`）是 Groq 生产可用的 agentic AI 系统，把网页搜索、代码执行和浏览器自动化整合进单次 API 调用。这两个系统从 beta 转为正式可用（general availability），为自主智能体应用带来前沿级表现，兼具领先的质量、低延迟和成本效率。

Compound 构建在 OpenAI 的 GPT-OSS-120B 与 Meta 的 Llama 模型之上，在各项基准上准确率高约 25%、错误少约 50%，超过了 OpenAI 的 Web Search Preview 和 Perplexity Sonar。[在这里了解更多关于 agentic tooling 的信息。](https://console.groq.com/docs/compound)

**主要特性：**

* **内置服务端工具** \- [网页搜索](https://console.groq.com/docs/web-search)、[代码执行](https://console.groq.com/docs/code-execution)、[Wolfram Alpha](https://console.groq.com/docs/wolfram-alpha) 和 [并行浏览器自动化](https://console.groq.com/docs/browser-automation)
* **生产级稳定性** \- 正式可用，速率上限更高、可靠性更强
* **前沿性能** \- 在 SimpleQA 和 RealtimeEval 基准上优于同类系统
* **单次 API 调用** \- 复杂的 agentic 工作流无需在客户端做编排

**增强的能力：**

* [并行浏览器自动化](https://console.groq.com/docs/browser-automation)（最多同时使用 10 个浏览器）
* 高级搜索，能从网页结果中抽取更丰富的上下文
* [Wolfram Alpha 集成](https://console.groq.com/docs/wolfram-alpha)，用于精确的数学与科学计算
* 改进的 markdown 渲染，便于结构化输出，也便于下游消费

**使用示例：**

curl

```
curl https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "groq/compound",
    "messages": [
      {
        "role": "user",
        "content": "Research the latest developments in AI inference optimization and summarize key findings"
      }
    ]
  }'
```
