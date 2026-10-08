---
vendor: groq
title: Groq Compound 与 Compound Mini 发布
original_title: Groq Compound and Compound Mini
url: https://console.groq.com/docs/changelog.md
date: 2025-09-04
lang: en
captured: 2026-10-08
extractor: readability-v1
status: ok
body_sha: 71a40dc4b03b
---

### Added[Groq Compound and Compound Mini](#groq-compound-and-compound-mini)

[Compound](https://console.groq.com/docs/compound/systems/compound) (`groq/compound`) and [Compound Mini](https://console.groq.com/docs/compound/systems/compound-mini) (`groq/compound-mini`) are Groq's production-ready agentic AI systems that integrate web search, code execution, and browser automation into a single API call. Moving from beta to general availability, these systems deliver frontier-level performance with leading quality, low latency, and cost efficiency for autonomous agent applications.

Built on OpenAI's GPT-OSS-120B and Meta's Llama models, Compound delivers \~25% higher accuracy and \~50% fewer mistakes across benchmarks, surpassing OpenAI's Web Search Preview and Perplexity Sonar. [Learn more about agentic tooling here.](https://console.groq.com/docs/compound)

**Key Features:**

* **Built-in server-side tools** \- [Web search](https://console.groq.com/docs/web-search), [code execution](https://console.groq.com/docs/code-execution), [Wolfram Alpha](https://console.groq.com/docs/wolfram-alpha), and [parallel browser automation](https://console.groq.com/docs/browser-automation)
* **Production-grade stability** \- General availability with increased rate limits and reliability
* **Frontier performance** \- Outperforms competing systems on SimpleQA and RealtimeEval benchmarks
* **Single API call** \- No client-side orchestration required for complex agentic workflows

**Enhanced Capabilities:**

* [Parallel browser automation](https://console.groq.com/docs/browser-automation) (up to 10 browsers simultaneously)
* Advanced search with richer context extraction from web results
* [Wolfram Alpha integration](https://console.groq.com/docs/wolfram-alpha) for precise mathematical and scientific computations
* Enhanced markdown rendering for structured outputs and better downstream consumption

**Example Usage:**

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
