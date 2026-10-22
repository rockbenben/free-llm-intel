---
vendor: deepinfra
title: Granite 4.2 8B: Model Overview & Integration Guide
original_title: 
url: https://deepinfra.com/blog/granite-4-2-8b-model-overview-integration-guide
date: 2026-10-21
lang: en
captured: 2026-10-22
extractor: readability-v1
status: ok
body_sha: bf1e7bc9134e
---

# Granite 4.2 8B: Model Overview & Integration Guide

Published on 2026.10.21 by DeepInfra

![Granite 4.2 8B: Model Overview & Integration Guide](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/10/Granite-4.2-Model-Integration-Guide.png)

[Granite 4.2 8B](https://deepinfra.com/ibm-granite/granite-4.2-8b) is an 8-billion-parameter dense transformer reasoning model developed by IBM. As the mid-size member of the Granite 4.2 family, it balances reasoning depth with operational efficiency.

Released under the Apache 2.0 license, the model is built for complex reasoning, code generation, tool calling, and structured data output.

Its defining feature is native chain-of-thought reasoning. Granite 4.2 8B performs step-by-step logical processing inside *<think>…</think>* tags before producing a final answer.

This supports applications that need deep logic, such as mathematical problem solving, agentic workflows, and software engineering tasks.

## **Capabilities and Performance**

### **Native Reasoning and Flexible Thinking Modes**

To give developers control over latency and computational depth, the model supports three thinking modes that can be toggled on a per-query basis:

- **Full Thinking (default):** maximizes reasoning depth for complex queries and generates comprehensive chain-of-thought tokens
- **Low-Effort Thinking:** provides brief reasoning for simpler queries, reducing time to first token
- **Non-Thinking:** disables the reasoning phase entirely for the lowest possible latency

### **Benchmarks**

The model has been tested across reasoning, knowledge, instruction following, and coding tasks:

| **Category** | **Benchmark** | **Score** | **Metric** |
| --- | --- | --- | --- |
| Reasoning | AIME 2025 | 86.67 | Accuracy |
| Reasoning | GPQA | 64.14 | Accuracy |
| Knowledge | MMLU-Pro | 74.04 | Accuracy |
| Instruction Following | Arena-Hard-V2 | 65.19 | Score |
| Coding | SWE-Bench Verified | 47.67 | Resolved Issues |

Compared to Granite 4.2 3B, the 8B variant offers greater reasoning depth. Compared to the 30B flagship, it remains more resource-efficient, making it a middle option for enterprise deployments.

### **Context Window and Multilingual Support**

Granite 4.2 8B natively supports a 128K token context window, extendable to 512K tokens for long-context tasks.

This makes it capable of analyzing long documents and large codebases.

The model officially supports 12 languages, including English, French, Japanese, Arabic, Spanish, and Chinese.

## **Getting Started With the API**

Granite 4.2 8B is hosted on DeepInfra, with an OpenAI-compatible interface for integration into existing workflows.

### **Authentication**

The API requires a DeepInfra API key. Include it in the HTTP Authorization header as a bearer token:

Authorization: Bearer <YOUR_DEEPINFRA_API_KEY>

Content-Type: application/json

### **API Endpoint Basics**

- **Base URL:** https://api.deepinfra.com/v1/openai
- **Path:** /chat/completions
- **Model Identifier:** ibm-granite/granite-4.2-8b

### **cURL Example**

```
curl -X POST "https://api.deepinfra.com/v1/openai/chat/completions" \

  -H "Authorization: Bearer $DEEPINFRA_API_KEY" \

  -H "Content-Type: application/json" \

  -d '{

    "model": "ibm-granite/granite-4.2-8b",

    "messages": [

      {"role": "user", "content": "Solve: If a store sells 12 pens for $18, how much do 30 pens cost?"}

    ],

    "temperature": 0.7

  }'copy
```

### **Python Example**

```
import os

import requests

api_key = os.environ.get("DEEPINFRA_API_KEY")

url = "https://api.deepinfra.com/v1/openai/chat/completions"

payload = {

    "model": "ibm-granite/granite-4.2-8b",

    "messages": [

        {"role": "system", "content": "Be a helpful assistant."},

        {"role": "user", "content": "Write a Python function to check if a string is a palindrome."}

    ],

    "temperature": 0.7,

    "max_tokens": 1024

}

response = requests.post(url, headers={"Authorization": f"Bearer {api_key}"}, json=payload)

print(response.json())copy
```

## **Configuration and Parameters**

The API supports the following parameters to fine-tune model behavior:

| **Parameter** | **Type** | **Default** | **Description** |
| --- | --- | --- | --- |
| max_tokens | integer | not set | Maximum new tokens to generate, capped by the model’s context length |
| temperature | float | 1 | Controls randomness (0 is deterministic, higher is more creative) |
| top_p | float | 1 | Nucleus sampling probability cutoff |
| repetition_penalty | float | 1 | Discourages repetitive text generation |
| stop | array | not set | Sequences that halt token generation |
| response_format | object | text | Set to json_object or json_schema for structured JSON output |
| tools / tool_choice | array / string | not set | Defines callable functions and controls tool invocation |
| prompt_cache_key | string | not set | Explicit key for reusing cached prompt state across requests |

The *tools / tool_choice* parameters are what make [tool calling](https://deepinfra.com/blog/deepinfra-function-calling-guide) work: the model decides which function to invoke and supplies arguments that match its schema.

The *response_format* parameter is how you request reliable [structured data output](https://deepinfra.com/blog/json-mode) instead of free-form text.

### **Response Format**

Because Granite 4.2 8B is a reasoning model, [the content field in the response](https://deepinfra.com/blog/deepinfra-json-only-responses) includes the reasoning steps followed by the final answer:

```
{

  "choices": [

    {

      "message": {

        "role": "assistant",

        "content": "<think>\n12 pens cost $18, so 1 pen is $1.50. 30 * $1.50 = $45.\n</think>\n30 pens will cost $45."

      }

    }

  ]

}copy
```

## **Pricing and Usage**

DeepInfra prices Granite 4.2 8B on a [per-token basis](https://deepinfra.com/blog/inference-economics-ai-costs-at-scale):

- **Input tokens:** $0.06 per 1 million tokens
- **Output tokens:** $0.25 per 1 million tokens
- [**Prompt caching:**](https://deepinfra.com/blog/pricing-101-token-math-cost-per-completion) $0.015 per 1 million cached tokens, which reduces costs for repeated system prompts or large context windows

Private endpoint deployments and dedicated hosting are available for high-volume enterprise needs.

## **Technical Background**

Granite 4.2 8B was post-trained from Granite 4.1 8B Base using a three-stage pipeline. The final stage used Group Relative Policy Optimization, a reinforcement learning technique, run on an NVIDIA GB200 NVL72 cluster.

This training supports what IBM calls [reasoning-augmented tool calling](https://deepinfra.com/blog/function-calling-feature), where the model reasons about which tool to use and why it fits the task.

## **Related Models on DeepInfra**

Granite 4.2 8B sits alongside other efficient models on DeepInfra that handle tool calling and agentic workloads:

- [**Gemma 4 26B A4B IT:**](https://deepinfra.com/google/gemma-4-26B-A4B-it) a mixture-of-experts model with 25.2B total and 3.8B active parameters. It offers a 262,144-token context window and supports JSON output, function calling, and multimodal input
- [**Qwen3.6-35B-A3B:**](https://deepinfra.com/Qwen/Qwen3.6-35B-A3B) a multimodal mixture-of-experts model with 35B total and 3B active parameters and a native 262,144-token context window
- [**GLM-5.3-Flash:**](https://deepinfra.com/zai-org/GLM-5.3-Flash) a natively multimodal model with a 1,048,576-token context window and support for JSON output and function calling
- [**DeepSeek-V4-Flash-0731:**](https://deepinfra.com/deepseek-ai/DeepSeek-V4-Flash-0731) a model with a 1,048,576-token context window and support for JSON output and function calling

## **Conclusion**

Granite 4.2 8B bridges lightweight efficiency and deep logical processing. Its native chain-of-thought, large context window, and flexible thinking modes make it a fit for [agentic workflows](https://deepinfra.com/blog/decision-models-ai-agent-infrastructure) and enterprise coding tasks.

Key takeaways:

- **Reasoning:** strong scores on AIME 2025 and SWE-Bench Verified
- **Flexibility:** toggle between full reasoning and low-latency modes
- **Cost:** usage-based pricing with prompt caching discounts

Get an API key and try [Granite 4.2 8B on DeepInfra](https://deepinfra.com/ibm-granite/granite-4.2-8b).

Related articles

[![DeepSeek V4 Pro: Model Overview, Features & Performance Guide](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/04/deepseek-v4-pro.png)](https://deepinfra.com/blog/deepseek-v4-pro-model-overview)[DeepSeek V4 Pro: Model Overview, Features & Performance Guide](https://deepinfra.com/blog/deepseek-v4-pro-model-overview)<p>DeepSeek V4 Pro is a 1.6-trillion parameter Mixture-of-Experts (MoE) model from DeepSeek, released on April 24, 2026 under the MIT license. It is designed for advanced reasoning, complex software engineering, and long-running agentic tasks, and arrives alongside DeepSeek-V4-Flash, a lighter 284B-parameter variant built for faster, lower-cost inference. The V4 series is DeepSeek&#8217;s first two-tier lineup [&hellip;]</p>

[![DeepSeek’s $10.29B Financing Round Explained](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/07/deepseek-1029-round-1024x725.png)](https://deepinfra.com/blog/deepseeks-upcoming-round)[DeepSeek’s $10.29B Financing Round Explained](https://deepinfra.com/blog/deepseeks-upcoming-round)<p>DeepSeek has not taken outside money since it was founded in 2023. For two years it turned down every venture capital firm and major tech company that came calling, funding its research entirely from the returns of its parent hedge fund, Zhejiang High-Flyer Asset Management, which reportedly posted a 56.6% return in 2025. That era [&hellip;]</p>

[![Wan 3.0 API Benchmarks: Speed, Latency & Cost](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/10/api.png)](https://deepinfra.com/blog/wan-3-0-api-benchmarks)[Wan 3.0 API Benchmarks: Speed, Latency & Cost](https://deepinfra.com/blog/wan-3-0-api-benchmarks)<p>Key Takeaways Wan is Alibaba&#8217;s family of video generation models. The earlier Wan2.2 models ship as open weights under Apache 2.0, while later releases such as Wan2.6, Wan2.7, and Wan3.0 are delivered through hosted APIs. Wan 3.0 is the first Wan model to accept documents and web pages as input. It also doubles the maximum [&hellip;]</p>

[View all](https://deepinfra.com/blog)
