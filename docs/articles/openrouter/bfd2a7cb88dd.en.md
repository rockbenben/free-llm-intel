---
vendor: openrouter
title: Provider Variance: Introducing Exacto
original_title: Provider Variance: Introducing Exacto
url: https://openrouter.ai/blog/announcements/provider-variance-introducing-exacto
date: 2025-10-21
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 614c812ee91d
---

# Provider Variance: Introducing Exacto

Chris Clark ·10/21/2025 · Updated 6/24/2026

Today, we’re introducing a new set of endpoints – `exacto` – which are focused on providing higher tool-calling accuracy by routing to a sub-group of providers that have measurably better tool-use success rates ([docs](https://openrouter.ai/docs/features/exacto-variant)).

There’s been a lot of speculation about LLM provider accuracy; whether different providers, running the same model, perform the same. In theory, of course, the same model weights (with the same quantization) should yield the same results. But in practice, implementing models as production-grade inference is complex and nuanced, and differences emerge.

OpenRouter sees billions of requests per month, from all over the world, and thus has a unique vantage point from which to observe these differences, determine exactly what is going on, and give our users a high-quality and surprise-free experience.

## The Provider Ecosystem

At OpenRouter we have long-term, consistent partnerships with our providers. We speak to them regularly, we talk in Slack channels, we visit their offices, and share feedback regularly. These are active, hands-on, real-world relationships.

We don’t believe that any of our providers have ever intentionally compromised model quality. Do they work hard to reduce their costs? Absolutely. Are they deep in VLLM and SGLang to squeeze performance? Yes. And we have on rare occasions seen quality degradation as inference stacks are tweaked. But all of our providers take their quality very seriously. When we report issues, we get high levels of engagement, from smart, dedicated professionals. Our incentives are aligned: we are a neutral platform working to give inference consumers the best experience, as are our providers.

With that said, running inference at scale is hard, some models are more challenging to host than others, and mistakes happen. We see the reports from industry experts, we look at our own data, and we hear anecdotes from our own customers about qualitative differences in provider output quality: It’s clear we need to be doing more to ensure the best possible experience on OpenRouter.

## Benchmarking

Artificial Analysis [published](https://x.com/ArtificialAnlys/status/1955102409044398415) a terrific set of benchmarks against gpt-oss-120b shortly after it came out, which showed significant differences between providers on a particular benchmark:
 ![](https://imagedelivery.net/Xq3eUzdKO2-MoBklzEEuMQ/1552a4f1-5d60-4bfb-d2ce-1a8974a0d000/public) The performance differences are significant. But, importantly, this model was released on August 5, 2025, and this data from Artificial Analysis is from August 11th. We know firsthand that providers take some time to ‘burn in’ the model, and get it really humming on their hardware and inference stack. We’ve seen this many times; with models like R1, Kimi K2 – the performance improves as providers refine their inference engines. Our intuition was that this delta would shrink, and indeed as of September 2025 we have [this](https://artificialanalysis.ai/models/gpt-oss-120b/providers#evaluations):

![](https://imagedelivery.net/Xq3eUzdKO2-MoBklzEEuMQ/18a26677-6ede-49b0-ab3a-b57ad5433b00/public)

The spread has tightened considerably and the bulk of the providers available on OpenRouter have similar benchmark performance.

We worked with Artificial Analysis to run benchmarks on Deepseek 3.1 – a model that has been out for many months. Again we see a tight band of performance:

![](https://imagedelivery.net/Xq3eUzdKO2-MoBklzEEuMQ/f1acf24f-0b51-4893-32e9-a43167046300/public)

Of note, even Deepinfra, which is the only provider quantizing the model to fp4, is quite competitive.

Going forward, we will look to:

- Benchmark providers shortly after new open-weight models become available
- Share the results (privately) with providers
- Remove from rotation any providers that are outside of an acceptable range
- Add them back when the performance issues have been resolved

## Tool calling data

In August 2025, we began rolling out additional quality telemetry, focused on tool calling and structured outputs. Specifically, for *every* `tool_call` response across all of OpenRouter, we check for three possible failure modes:

- Was the `tool_call` returned by the LLM valid json?
- Was the tool name in the `tool_call` present in the original tools input?
- Does the schema of the `tool_call` match the schema of the provided tool?

This allows us to compare tool call accuracy, and tool call propensity, across providers for the same model. Because there could be skew in how certain providers are being used, we downsample large customers, compare accuracies for single apps across providers, and also check that schema complexities are comparable. In aggregate, we have measured the accuracy of billions of LLM tool calls.

For example, below are the tool calling accuracies of the top 5 DeepSeek Terminus providers (all quite good!).

![](https://imagedelivery.net/Xq3eUzdKO2-MoBklzEEuMQ/3b059e35-430c-4035-4342-13d2ce55a600/public)

In addition, we measure how frequently tools are requested by the models & providers, given that tools were provided in the input. We are not publishing the complete dataset at this time because we want to first work with providers to better understand the source of variance, but below is an example of variance in tool calling *propensity* among a sample of Kimi K2 providers This is similar to what [Moonshot published](https://x.com/kimi_moonshot/status/1976926483319763130?s=46) – but based on real world usage, not benchmarking.

![](https://imagedelivery.net/Xq3eUzdKO2-MoBklzEEuMQ/0ec36b6b-a920-4301-3b7e-648b45223f00/public)

While we have only shared a sample of data here, the full dataset shows clearly that the *propensity* of the LLM to use tools, and the *accuracy* of those tool calls, vary between providers significantly more than the standard benchmarking would suggest.

## Real-time user preferences

In addition to the measured tool call data, we also have access to another source of data: provider preferences.

OpenRouter supports ignoring providers, which we can interpret as a vote that the provider is not meeting the needs of that customer.

```
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{
    "model": "meta-llama/llama-3.3-70b-instruct",
    "messages": [
      {"role": "user", "content": "What is the capital of France?"}
    ],
    "provider": {
      "ignore": ["omega"]
    }
  }'
```

In aggregate, we have thousands of provider preferences for each model, that we can further restrict to LLM generations that provided tools. This is a powerful indicator of which providers are and aren’t performing well.

## Introducing Exacto

Using our tool calling data, customer provider preference data, and tool calling benchmarks run on [Groq OpenBench](https://github.com/groq/openbench), we have created new, curated endpoints specifically focused on tool calling accuracy. These are available today, and we are calling them exacto.

We are launching with exacto endpoints for the following models

- [Kimi K2](https://openrouter.ai/moonshotai/kimi-k2-0905:exacto) (`moonshotai/kimi-k2-0905:exacto`)
- [DeepSeek v3.1 Terminus](https://openrouter.ai/deepseek/deepseek-v3.1-terminus:exacto) (`deepseek/deepseek-v3.1-terminus:exacto`)
- [GLM 4.6](https://openrouter.ai/z-ai/glm-4.6:exacto) (`z-ai/glm-4.6:exacto`)
- [GPT-OSS 120b](https://openrouter.ai/openai/gpt-oss-120b:exacto) (`openai/gpt-oss-120b:exacto`)
- [Qwen3 Coder](https://openrouter.ai/qwen/qwen3-coder:exacto) (`qwen/qwen3-coder:exacto`)

You can use the new endpoints via `model_slug:exacto.` For example:

```
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{
    "model": "moonshotai/kimi-k2:exacto",
    "messages": [
      {"role": "user", "content": "What is the capital of France?"}
    ]
  }'
```

You will be routed to one of the providers that meet all of the following criteria:

- Are a top provider in terms of tool calling accuracy
- Are within normal range of tool calling propensity
- Are *not* frequently ignored or blacklisted by OpenRouter users when making tool calls

Running our internal tool-calling evals suites, as well as open-source benchmarks like [tau2-Bench](https://github.com/sierra-research/tau2-bench) and [LiveMCPBench](https://arxiv.org/html/2508.01780v1), we observe that tool calling failures happen measurably less often, and the model makes use of the tools given to it more reliably. Benchmarking (in this example, of Kimi K2 0905) shows material lift in tool calling success via `exacto`:

![](https://imagedelivery.net/Xq3eUzdKO2-MoBklzEEuMQ/5a1d1b5d-71e4-4918-38e1-f7dde6c8ab00/public)

We expect these endpoints to be popular for many agentic workflows, and anticipate that we will work with providers not currently included in the Exacto routing pool to help them improve and eventually meet the criteria to be included. Note that the exacto endpoints are *specifically focused on tool-calling*, and should not be viewed as a broader statement on endpoint or provider quality.

Lastly, we are working towards exposing more of our data publicly; expect to see some of the underlying data exposed before the end of the year to help our users make more informed decisions. As these are new findings, we would like to give certain providers opportunities to improve (or give feedback on our methodology) before we publish full datasets.

## In closing

While we hope some questions have been answered, we also suspect this analysis will raise more. We look forward to hearing the feedback and anticipate plenty of follow-ups. Please reach out to us on [X](https://x.com/openrouterai) or [Discord](https://discord.gg/openrouter) to engage in the discussion. If you have specific feedback on a provider under exacto, please fill out [this form](https://openrouter.notion.site/2932fd57c4dc8097ba74ffb6d27f39d1?pvs=105)

We hope our users find the Exacto endpoints helpful, and we’re excited to share more data (both benchmark and empirical), and build it into our products over the remainder of the year.
