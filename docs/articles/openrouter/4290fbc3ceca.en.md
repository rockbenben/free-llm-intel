---
vendor: openrouter
title: Response Healing: Reduce JSON Defects by 80%+
original_title: Response Healing: Reduce JSON Defects by 80%+
url: https://openrouter.ai/blog/announcements/response-healing-reduce-json-defects-by-80percent
date: 2025-12-18
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 4a3a280f82dd
---

# Response Healing: Reduce JSON Defects by 80%+

Alex Atallah ·12/18/2025 · Updated 6/24/2026

We expect our APIs to have 99.999% uptime. We’d never tolerate a payment processor that failed 2% of the time. So why do we accept LLMs that routinely break JSON syntax in structured output requests?

Today we’re launching **[Response Healing](https://openrouter.ai/docs/guides/features/plugins/response-healing)**: a new feature on OpenRouter that automatically fixes malformed JSON responses from LLMs before they reach your application.

Two standout improvements from a week of data:

- **Gemini 2.0 Flash**, our most popular model for structured output with over 1.6 million requests in the past week, saw its defect rate **decline by 80%**.
- **Qwen3 235B**, one of the most capable open-weight models available, saw its defect rate **decline by 99.8%**.

## The Math That Should Keep You Up at Night

Here’s something most developers overlook: if an LLM has a 2% JSON defect rate, and Response Healing drops that to 1%, you haven’t just made a 1% improvement. You’ve cut your defects, bugs, and support tickets **in half**.

At OpenRouter’s scale, we see this compounding effect across billions of tokens daily. A “small” improvement in structured output reliability translates to dramatically fewer 3am pages, fewer angry users, and fewer hours debugging why your agent suddenly stopped working.

This is why we obsess over this problem more than any other gateway. Reliability at the margins is where real production systems succeed or fail.

## What We’re Fixing

LLMs make surprisingly creative mistakes when generating JSON. Common issues include trailing commas after the last element, unescaped control characters in strings, missing closing brackets, and various syntax errors that break parsers.

> Here’s the data you requested: {…}

That’s not something that should **ever** take you down.

For a detailed breakdown of the failure modes we handle, check out our [Response Healing documentation](https://openrouter.ai/docs/guides/features/plugins/response-healing):

![example healings](https://imagedelivery.net/Xq3eUzdKO2-MoBklzEEuMQ/04f0fde4-123b-42c8-c70f-4911d3fe5d00/public)

## The Benchmarks

We analyzed millions of structured output generations across our platform. We did this on the fly, at inference time, without logging any completions or storing results.

Here are the results for the highest-volume models:

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

Some highlights worth noting since we soft-rolled this out a week ago:

- `mistralai/devstral-2512`: customers who turned on the plugin had valid json rate taken from 97% to 99.99%, which is a **99.7% defect reduction**
- `google/gemini-2.5-flash`: success rate increased from 97.5% to 99.88%. **95.2% reduction**
- `meta-llama/llama-3.1-8b-instruct`: success rate increased from 99.9% to 100%. **100% reduction**
- Qwen3-235B: 87.97% valid to 99.98% valid, a **99.85% reduction**
- Deepseek Chat V3.1: 83.16% valid to 97.46% valid, a **84.89% reduction**
- Several models—Ministral 3B, Devstral 2512, Mistral Small 3.2—achieve near-perfect healing rates above 99%
- Even models that already perform well see meaningful gains: Gemini 2.0 Flash Lite went from 99.94% to 100% validity

## How to Enable It

Response Healing is opt-in. You can configure it through the new **Plugins** section in your settings:

[**openrouter.ai/settings/plugins**](https://openrouter.ai/settings/plugins)

![plugins screenshot](https://imagedelivery.net/Xq3eUzdKO2-MoBklzEEuMQ/e0c3c9db-c5da-4225-b447-a883ed8b3c00/public)

Toggle it on, and every structured output request will automatically pass through our healing layer before returning to your application.

### Cost

The plugin is free to use. In terms of latency, we ran an analysis of added CPU time across all production data:

| Category | Mean Time | Ops/Second |
| --- | --- | --- |
| Schema-less Repair | 0.018ms | 54,700 |
| Unified API | 0.019ms | 51,500 |
| Type Coercion | 0.041ms | 32,600 |
| Basic Parsing | 0.133ms | 16,900 |
| Large Payloads (10KB) | 2.3ms | 437 |

In reality, factors outside the plugin are going to dominate any real world latency. So we can say that, for typical responses, healing adds less than 1ms of latency, negligible compared to LLM inference time.

## What This Doesn’t Fix

To be clear about scope: Response Healing fixes **JSON syntax errors**, not schema adherence. If a model returns valid JSON that doesn’t match your expected schema (wrong field names, missing required properties, wrong types), healing won’t catch that.

It also only works for non-streaming requests today. Contact us with your use case if you have a need for fixing streaming requests as well.

That said, you should still see a meaningful drop in your overall error rate. Syntax errors are one of the most common failure modes, and eliminating them lets you focus your error handling on the semantic issues that actually require application logic to resolve.

What about tool calling and schema adherence? Tool calling has very few structural JSON issues, but schema adherence has many defects across most models. We’ll evaluate schema adherence soon.

What about XML? The plugin can heal XML output as well - contact us if you’d like access.

## Ship with Confidence

We built OpenRouter to be the infrastructure layer you don’t have to think about. Response Healing is another step toward that goal: structured outputs that just work, every time.

Enable it today at [openrouter.ai/settings/plugins](https://openrouter.ai/settings/plugins), and let us know what you’re building.
