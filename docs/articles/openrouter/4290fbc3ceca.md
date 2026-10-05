---
vendor: openrouter
title: Response Healing：将 JSON 缺陷减少 80% 以上
original_title: 'Response Healing: Reduce JSON Defects by 80%+'
url: https://openrouter.ai/blog/announcements/response-healing-reduce-json-defects-by-80percent
date: 2025-12-18
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

我们期望自己的 API 达到 99.999% 的可用性，也绝不会容忍一个 2% 时间会失败的支付处理器。那么，为什么我们能容忍 LLM 在结构化输出请求中动不动就破坏 JSON 语法？

今天我们推出 **[Response Healing](https://openrouter.ai/docs/guides/features/plugins/response-healing)**：OpenRouter 的一项新功能，会在畸形的 JSON 响应到达你的应用之前自动修复 LLM 产生的这类响应。

一周数据中两项最亮眼的改善：

- **Gemini 2.0 Flash**——我们最热门的结构化输出模型，过去一周超过 160 万次请求——缺陷率**下降了 80%**。
- **Qwen3 235B**——现有最强开源权重模型之一——缺陷率**下降了 99.8%**。

## 那笔该让你夜不能寐的数学

大多数开发者会忽略这一点：如果一个 LLM 的 JSON 缺陷率是 2%，Response Healing 把它降到 1%，你不是只做了 1% 的改进，而是把缺陷、bug 和支持工单**砍半**。

在 OpenRouter 的规模上，我们每天看到这种复利效应作用于数十亿 token。结构化输出可靠性上的一次“小”改进，意味着大幅更少的凌晨三点告警、更少的愤怒用户、更少花在调试“agent 为什么突然不干了”上的时间。

这就是为什么我们比任何网关都更痴迷于这个问题。边缘处的可靠性，正是真实生产系统成败的分界。

## 我们修什么

LLM 生成 JSON 时会犯出人意料的创造性错误。常见问题包括最后一个元素后的尾逗号、字符串里未转义的控制字符、缺失的右括号，以及各种让解析器崩溃的语法错误。

> Here’s the data you requested: {…}

这种东西**永远**不该把你打倒。

关于我们处理的失效模式的详细拆解，见 [Response Healing 文档](https://openrouter.ai/docs/guides/features/plugins/response-healing)：

![example healings](https://imagedelivery.net/Xq3eUzdKO2-MoBklzEEuMQ/04f0fde4-123b-42c8-c70f-4911d3fe5d00/public)

## 基准数据

我们分析了平台上数百万次结构化输出生成。这是实时完成的，在推理时进行，不记录任何补全、也不存储结果。

以下是最高流量模型的结果：

| Model | Requests | Success Before | Success After | Defects Resolved |
| --- | --- | --- | --- | --- |
| Gemini 2.0 Flash | 1.62M | 99.61% | 99.92% | 80.0% |
| Gemini 2.5 Flash | 772k | 98.97% | 99.65% | 66.3% |
| Gemini 2.5 Flash Lite | 703k | 99.64% | 99.89% | 68.7% |
| GPT-4o Mini | 494k | 99.98% | 100.00% | 80.7% |
| Grok 4 Fast | 488k | 92.89% | 94.87% | 27.8% |
| Grok 4.1 Fast | 284k | 98.70% | 99.17% | 36.4% |
| Gemini 2.0 Flash Lite | 282k | 99.94% | 100.00% | 98.9% |
| Deepseek Chat v3.1 | 196k | 82.54% | 97.39% | 85.0% |
| GPT-4.1 | 155k | 98.22% | 98.40% | 10.4% |
| Qwen3 235B | 113k | 88.02% | 99.98% | 99.8% |
| GPT-oss-120b | 112k | 99.53% | 99.82% | 62.2% |
| Devstral 2512 | 104k | 96.59% | 99.99% | 99.6% |
| Gemini 2.5 Flash Lite Preview | 93k | 99.14% | 99.86% | 83.7% |
| Llama 3.1 8B Instruct | 79k | 99.68% | 99.91% | 72.4% |
| GPT-oss-20b | 58k | 99.01% | 99.36% | 34.8% |
| Mistral Small 3.2 24B | 57k | 98.82% | 99.99% | 99.3% |
| GPT-5 Nano | 52k | 99.96% | 99.96% | 8.7% |
| Ministral 3B | 52k | 99.99% | 100.00% | 100.0% |

自我们一周前灰度上线以来，一些值得注意的亮点：

- `mistralai/devstral-2512`：开启插件的客户，有效 JSON 率从 97% 提升到 99.99%，即**缺陷减少 99.7%**
- `google/gemini-2.5-flash`：成功率从 97.5% 升到 99.88%，**减少 95.2%**
- `meta-llama/llama-3.1-8b-instruct`：成功率从 99.9% 升到 100%，**减少 100%**
- Qwen3-235B：有效率从 87.97% 到 99.98%，**减少 99.85%**
- Deepseek Chat V3.1：有效率从 83.16% 到 97.46%，**减少 84.89%**
- 多个模型——Ministral 3B、Devstral 2512、Mistral Small 3.2——达到 99% 以上的近乎完美修复率
- 连本来就表现不错的模型也有实质收益：Gemini 2.0 Flash Lite 的有效率从 99.94% 到 100%

## 如何启用

Response Healing 是选择性开启的。你可以在设置中新的 **Plugins** 区块配置：

[**openrouter.ai/settings/plugins**](https://openrouter.ai/settings/plugins)

![plugins screenshot](https://imagedelivery.net/Xq3eUzdKO2-MoBklzEEuMQ/e0c3c9db-c5da-4225-b447-a883ed8b3c00/public)

打开开关后，每一次结构化输出请求在返回你的应用之前都会自动经过我们的修复层。

### 成本

该插件免费使用。延迟方面，我们对全部生产数据做了新增 CPU 时间的分析：

| Category | Mean Time | Ops/Second |
| --- | --- | --- |
| Schema-less Repair | 0.018ms | 54,700 |
| Unified API | 0.019ms | 51,500 |
| Type Coercion | 0.041ms | 32,600 |
| Basic Parsing | 0.133ms | 16,900 |
| Large Payloads (10KB) | 2.3ms | 437 |

实际上，真实世界的延迟将由插件之外的因素主导。所以可以说：对典型响应，修复增加的延迟不到 1ms，与 LLM 推理时间相比可以忽略。

## 它不修什么

明确范围：Response Healing 修的是 **JSON 语法错误**，不是 schema 符合性。如果模型返回的是合法 JSON 但不匹配你期望的 schema（字段名错误、缺失必填属性、类型错误），修复层不会拦下。

另外，目前它只对非流式请求生效。如果你也需要修复流式请求，带着你的用例联系我们。

即便如此，你仍会看到整体错误率的实质性下降。语法错误是最常见的失效模式之一，消灭它们能让你的错误处理专注于真正需要应用逻辑解决的语义问题。

Tool calling 和 schema 符合性呢？Tool calling 的结构化 JSON 问题很少，但大多数模型在 schema 符合性上缺陷不少。我们很快会评估 schema 符合性。

XML 呢？该插件也能修复 XML 输出——需要可以联系我们开通。

## 放心交付

我们构建 OpenRouter，是想让它成为你不必操心的基础设施层。Response Healing 是朝这个目标迈进的又一步：每次都能用的结构化输出。

今天在 [openrouter.ai/settings/plugins](https://openrouter.ai/settings/plugins) 启用它，并告诉我们你在构建什么。
