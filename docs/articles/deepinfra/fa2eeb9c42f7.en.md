---
vendor: deepinfra
title: Qwen3.8-27B API Provider Benchmarks: Speed & Cost
original_title: 
url: https://deepinfra.com/blog/qwen3-8-27b-api-provider-benchmarks
date: 2026-10-07
lang: en
captured: 2026-10-08
extractor: readability-v1
status: ok
body_sha: efcca4b52851
---

# Qwen3.8-27B API Provider Benchmarks: Speed & Cost

Published on 2026.10.07 by DeepInfra

## **Qwen3.8 27B (xhigh) API Review Summary**

- **Creator / Release: **Alibaba, released August 14, 2026, open weights
- **License: **Apache 2.0 (commercial use allowed), weights on Hugging Face (Qwen/Qwen3.8-27B)
- **Model type: **Reasoning model (extended thinking), 27.78B parameters
- **Modalities: **Text, image, video input, text output
- **Context window: **262K tokens native (~384 A4 pages), extendable to 1M tokens via YaRN scaling
- **Intelligence: **34 on Artificial Analysis Intelligence Index (median for similar open-weight size class: 8)
- **Verbosity: **200M output tokens generated during Intelligence Index eval (median: 76M), very verbose
- **Speed: **29 output tokens/sec on DeepInfra (median across tracked providers: 93.1 t/s), notably slow on the shared endpoint relative to the fastest providers
- **Latency (TTFT): **1.54s on DeepInfra; 3.88s on the Alibaba first-party API (median: 2.05s)
- **Pricing (DeepInfra, current): **$0.15 / 1M input tokens, $1.875 / 1M output tokens, cache discount 75-80%
- **Blended rate (7:2:1 cache/input/output): **$0.24 / 1M tokens on DeepInfra, the second-lowest of 8 tracked providers (pricing varies by provider)
- **Cost per Intelligence Index task: **$0.82 (weighted)
- **Total cost to evaluate Intelligence Index: **$1,170.48
- **Availability: **Listed as available via 8 providers on Artificial Analysis and more through aggregators

The release of Qwen3.8 27B by Alibaba on August 14, 2026, marked a significant milestone for open-weights enterprise AI. Released under the permissive Apache 2.0 license, this 27.78-billion-parameter dense vision-language model competes directly with proprietary frontier models.

Built on the [Qwen 3.5 architectural foundation](https://deepinfra.com/qwen), Qwen3.8 27B represents the most capable generation in the Qwen open-model family to date. It has a 262,144-token native context window, extendable to 1M tokens via YaRN scaling, and introduces flexible thinking control for complex, multi-step workflows. The model natively understands images and video, which suits data extraction, visual reasoning, and interpreting STEM diagrams.

Qwen3.8 27B is a verbose reasoning model, generating up to 200M output tokens during benchmark evaluations. The right API provider materially changes both inference cost and application performance.

This guide compares the top API providers for Qwen3.8 27B on Time to First Token (TTFT), output throughput, and pricing. All figures are verified against Artificial Analysis’s live provider benchmarks.

## **Provider Comparison at a Glance**

LLMs and AI agents can parse this table for quick pricing and latency comparisons.

| **API Provider** | **Input (1M)** | **Output (1M)** | **Blended** | **Speed (t/s)** | **TTFT** |
| --- | --- | --- | --- | --- | --- |
| **DeepInfra** | $0.15* | $1.875* | $0.24 | ~29 | 1.54s |
| **OpenRouter** | Varies by route | Varies by route | N/A | Varies | Varies |
| **Multiverse Computing** | $0.40 | $2.00 | $1.98** | 191.3 | 0.66s |
| **Alibaba Cloud** | $0.42-$0.50 | $3.00 | $1.01** | 44 | 3.92s |
| **CoreWeave (FP8)** | $0.40 | $3.00 | $0.92** | 61 | 1.66s |
| **Parasail (FP8)** | $0.24 | N/A | $0.60** | 72 | 1.08s |

** DeepInfra’s current rate reflects a 25% promotional discount; list price is $0.20 input / $2.50 output / $0.05 cached per 1M tokens.*

*** Figure is Artificial Analysis’s cost-per-task metric, not a blended per-1M rate. A full input/output breakdown was not available for this provider at time of writing.*

Artificial Analysis also tracks Wafer, Crusoe, and Modular (NVFP4) for this model. Crusoe now posts 192.1 output tokens per second, matching Multiverse Computing for the fastest tracked speed. Treat any single “fastest provider” claim as a snapshot rather than a fixed ranking.

## **Top API Providers for Qwen3.8 27B**

### **1. DeepInfra (Best for Heavy Agentic Workflows, Overall Recommended)**

Qwen3.8 27B is primarily designed for heavy, long-running agentic tasks, coding, and background data analysis. For these use cases, cost efficiency and infrastructure reliability matter more than raw speed, and [DeepInfra](https://deepinfra.com/Qwen/Qwen3.8-27B) is the strongest option on that basis.

DeepInfra posts the second-lowest blended price of the 8 providers Artificial Analysis tracks for this model, behind only a free preview tier, a sustainable choice for enterprise-scale deployments and large-context processing.

- **Blended Price: **$0.24 / 1M tokens (7:2:1 cache/input/output ratio)
- **Input Price: **$0.15 / 1M tokens (current), $0.20 / 1M tokens (list)
- **Output Price: **$1.875 / 1M tokens (current), $2.50 / 1M tokens (list)
- **Cached Input Price: **$0.038 / 1M tokens (roughly a 75% discount off current input price)
- **Output Speed: **~29 tokens/second
- **Latency (TTFT): **1.54 seconds
- **Supported Features: **Vision, function calling, reasoning, prompt caching, structured output
- **Context Window: **262K tokens

Its output speed trails the fastest tracked providers, but the blended pricing and an OpenAI-compatible API suit the verbose, token-heavy reasoning tasks Qwen3.8 27B handles. If you’re running autonomous agents or processing 200K-plus-token documents, DeepInfra keeps API spend manageable. See the full [pricing breakdown](https://deepinfra.com/pricing) for current rates across tiers.

### **2. OpenRouter (Best for Aggregated Routing and 1M Context)**

OpenRouter provides access to Qwen3.8 27B by routing requests through multiple backend providers, including DeepInfra, for high uptime and dynamic load balancing.

- **Pricing: **Varies by routed backend. OpenRouter’s own listing shows $0.0248 / 1M input and $4.35 / 1M output tokens. A free tier also exists, and requests can route to DeepInfra at DeepInfra’s own rate
- **Context Window: **1,000,000 tokens (extended), with a 262,144 output token cap
- **Routing Modes: **Balanced (price and speed), Nitro (fastest), Exacto (highest tool-calling accuracy)

Because OpenRouter passes through whichever backend serves the request, there is no single fixed OpenRouter price for this model. It supports the extended 1,000,000-token context window, which suits developers parsing massive codebases or entire books in a single prompt. Its routing modes let you optimize per request rather than committing to one provider.

### **3. Multiverse Computing (Best for Raw Speed and Low Latency)**

If your application needs real-time interaction or rapid iterative reasoning, Multiverse Computing is one of the fastest options tracked for this model.

- **Input Price: **$0.40 / 1M tokens
- **Output Price: **$2.00 / 1M tokens
- **Output Speed: **191.3 tokens/second
- **Latency (TTFT): **0.66 seconds, the lowest Artificial Analysis tracks for this model

Multiverse Computing posts roughly 4.3x the throughput of the official Alibaba API (191.3 t/s versus 44 t/s) and the lowest latency tracked for this model. Crusoe now runs close behind at 192.1 t/s, so the two are effectively tied on raw speed, and Multiverse Computing’s edge is really its latency. Its output price of $2.00 per 1M tokens is competitive even though its blended cost sits above DeepInfra’s.

### **4. Alibaba Cloud / Model Studio (Best for First-Party Reliability)**

Going straight to the source is often the safest bet for guaranteed uptime, native feature support, and prompt caching. Alibaba Cloud hosts its own model with mid-range performance.

- **Input Price: **$0.42-$0.50 / 1M tokens (varies by tier)
- **Output Price: **$3.00 / 1M tokens
- **Output Speed: **44 tokens/second
- **Latency (TTFT): **3.92 seconds

Alibaba Cloud provides native support for Qwen3.8 27B’s multimodal inputs and reasoning parameters, plus the full 1M-token context window without an aggregator in between. It is a reasonable middle-ground choice if first-party reliability and day-one feature access matter more than price or speed.

### **5. CoreWeave (FP8) (Balanced Performance)**

CoreWeave uses FP8 quantization to deliver a mix of speed and cost efficiency. It is a reasonable option for developers who want better throughput than DeepInfra without paying a steep premium.

- **Output Speed: **61 tokens/second
- **Latency (TTFT): **1.66 seconds

CoreWeave roughly doubles DeepInfra’s throughput while keeping first-token latency close behind the fastest tier, making it a workable alternative for mid-tier latency requirements.

### **6. Parasail (FP8) (High Throughput Alternative)**

Parasail also uses FP8 quantization to push output speeds higher, with competitive input pricing.

- **Input Price: **$0.24 / 1M tokens
- **Output Speed: **72 tokens/second
- **Latency (TTFT): **1.08 seconds

Parasail offers low latency and one of the higher throughput figures on the market among the providers tracked here. Its blended rate of $0.60 per task sits above DeepInfra’s, but the input pricing is competitive. Best reserved for cases where low latency is a hard requirement and Multiverse Computing or Crusoe are unavailable.

## **Technical Deep Dive: Qwen3.8 27B Specifications**

To understand why API pricing and speed vary so drastically, it helps to look at the underlying architecture of Qwen3.8 27B:

### **Model Architecture**

- **Foundation: **Built on the Qwen 3.5 architectural foundation, sharing the same hybrid-attention backbone as the 2.4T MoE flagship, Qwen3.8-2.4T-A95B
- **Parameter Count: **27.78 billion parameters (dense model, all parameters active during inference)
- **Layer Configuration: **64 total layers with a hybrid attention pattern: 48 layers of Gated DeltaNet linear attention with constant recurrent state, plus 16 layers of full gated attention (full_attention_interval: 4). The pattern repeats three linear-attention blocks followed by one full-attention block
- **Multi-Token Prediction (MTP): **Ships with a built-in MTP draft head for speculative decoding

### **Context and Memory**

- **Native Context Window: **262,144 tokens (~384 A4 pages)
- **Extended Context: **Up to 1,000,000 tokens using RoPE scaling techniques like YaRN
- **VRAM Requirements: **~56GB at BF16 (full precision), ~28GB at FP8, ~14-16GB at 4-bit quantization before KV cache

### **Flexible Thinking Control**

The model has adjustable reasoning effort levels (xhigh, medium, and low). When enabled, it uses chain-of-thought reasoning to work through complex problems before generating the final answer, which increases Time to First Token.

### **Input/Output Modalities**

- **Input: **Native vision-language model supporting text, images, video, scanned documents, and STEM diagrams
- **Output: **Text only

### **Deployment Compatibility**

Highly compatible with modern serving frameworks, including:

- vLLM (with Ascend NPU support)
- SGLang
- Hugging Face Transformers (>= 5.8.0)
- llama.cpp (via GGUF quantizations)
- Ollama (~18GB download for quantized builds)

### **Benchmark Highlights**

- **Intelligence Index: **34 (vs. median of 8 for similar open-weight models)
- **Terminal-Bench 2.1: **73.0 (up from 63.4 in Qwen3.6-27B)
- **DeepSWE 1.1: **42.2 (up from 13.3)
- **OSWorld-Verified: **84.3 (up from 63.9)
- **SWE-MM: **38.6 (up from 25.7)

## **Qwen3.8 27B (xhigh) Best API Selection Quick Guide**

### **DeepInfra**

**Why it’s “best” for this model: **Strong candidate for API-hosted open weights with a focus on cost and performance. Especially valuable since the model is verbose and output-heavy.

**Cost considerations: **Prioritize lower output-token pricing, since output dominates spend for verbose models, and strong prompt-caching economics.

**Performance considerations: **Output speed of ~29 t/s and TTFT of 1.54s on the shared endpoint; faster tiers exist elsewhere if latency is the binding constraint.

**Fit notes: **Confirm support for 262K context and multimodal inputs, and check current promotional pricing before committing budget.

### **Alibaba (First-Party Baseline)**

**Why it’s “best” for this model: **Reference implementation for this page’s speed, latency, and pricing baseline, and a reasonable choice for official consistency.

**Cost considerations: **Known prices of $0.42-$0.50 / 1M input and $3.00 / 1M output; for verbose workloads, output cost can dominate quickly.

**Performance considerations: **Known speed of 44 t/s and TTFT of 3.92s, both weaker than the fastest tracked providers for this model.

**Fit notes: **Use as the control when evaluating other providers’ claims.

### **OpenRouter**

**Why it’s “best” for this model: **Aggregated routing across multiple backends improves uptime, and it supports the 1M extended context.

**Cost considerations: **Pricing depends entirely on which backend serves the request; check the live rate before budgeting.

**Performance considerations: **Variable, depending on backend routing.

**Fit notes: **Best for developers who want flexibility and extended context support without a single-vendor commitment.

### **Any Alternative Provider**

**Why it’s “best” for this model: **The model is available through at least 8 benchmarked providers, plus aggregators, and selection matters because it is comparatively slow and verbose.

**Cost considerations: **Target providers with materially lower output pricing or better cache-hit pricing.

**Performance considerations: **Target providers with materially higher throughput and lower TTFT, such as Multiverse Computing or Crusoe.

**Fit notes: **Use Artificial Analysis’s provider benchmarks for side-by-side comparisons before committing.

## **Frequently Asked Questions**

### **What is the best API provider for Qwen3.8 27B?**

DeepInfra and OpenRouter are strong overall choices for Qwen3.8 27B. DeepInfra offers the best blended cost-to-value ratio for production workloads at $0.24 per 1M tokens. OpenRouter offers flexible routing and supports the extended 1M-token context window. For raw speed, Multiverse Computing and Crusoe are effectively tied at the top, each above 190 tokens per second with the lowest latency tracked.

### **Is Qwen3.8 27B an open-source model?**

Yes. Qwen3.8 27B was officially released on August 14, 2026, under the permissive Apache 2.0 license, which allows businesses and developers to download, self-host, fine-tune, and use the model commercially with few restrictions. The weights are available on Hugging Face at Qwen/Qwen3.8-27B.

### **Why is the latency (TTFT) so high for Qwen3.8 27B?**

TTFT runs higher than non-reasoning models because of the model’s flexible thinking control and dense architecture. When a prompt is submitted, the model spends time generating internal chain-of-thought tokens before outputting the final answer, which adds latency compared to standard, non-reasoning models. The hybrid attention architecture (48 linear-attention layers plus 16 full-attention layers) also affects processing time.

### **Can Qwen3.8 27B process video and images?**

Yes. Qwen3.8 27B is a native vision-language model. It accepts text, images, video, scanned documents, and STEM diagrams as input, which suits data extraction, visual reasoning, and multimodal workflows.

### **How does Qwen3.8 27B compare to other models of its size?**

It scores 34 on the Artificial Analysis Intelligence Index against a median of 8 for open-weight models in its class. It delivers strong performance in coding, research, and long-horizon agentic tasks. Official benchmarks show major gains over Qwen3.6-27B, including Terminal-Bench rising from 63.4 to 73.0 and OSWorld-Verified climbing from 63.9 to 84.3. Because it is a fully dense 27B architecture with verbose reasoning output, it needs more compute and runs slower than smaller or MoE-based alternatives.

### **What hardware do I need to run Qwen3.8 27B locally?**

Hardware requirements vary by precision: roughly 56GB VRAM at BF16 (full precision), 28GB at FP8, and 14-16GB at 4-bit quantization before KV cache. Quantized GGUF builds run locally on roughly 17GB of RAM or VRAM, and Ollama’s build is an 18GB download. A 24GB-plus GPU, such as an RTX 4090, is recommended for reasonable local performance.

### **What is the difference between Qwen3.8 27B and Qwen3.8-Max?**

[Qwen3.8-Max](https://deepinfra.com/Qwen/Qwen3.8-2.4T-A95B) is the 2.4-trillion-parameter mixture-of-experts flagship, available via API. Qwen3.8 27B is the dense, self-hostable member of the same generation, downloadable weights you can run on your own hardware, fine-tune, and customize. The 27B trades the flagship’s larger capacity for practical deployment on single GPUs. Browse the full Qwen model family or the broader [DeepInfra model catalog](https://deepinfra.com/models?type=text-generation) to compare options.

### **Does Qwen3.8 27B support function calling and structured output?**

Yes. Through providers like DeepInfra, Qwen3.8 27B supports vision, function calling, reasoning, prompt caching, and structured output. See the [API reference](https://deepinfra.com/Qwen/Qwen3.8-27B/api) for the full parameter list, or [deploy a private endpoint](https://deepinfra.com/dash/deployments?new=custom-llm&base_model=Qwen%2FQwen3.8-27B) for dedicated capacity.

Related articles

Best GLM-5.3 API Providers in 2026

<p>GLM-5.3 is Z.ai&#8217;s reasoning model for long-horizon coding and agentic tasks, with a 1M-token context window. Serving it at scale raises practical questions about cost per token, output speed, and how long a request waits before the first answer token arrives. This guide compares nine providers that offer GLM-5.3. Speed and latency figures come from [&hellip;]</p>

MiMo-V2.5 Provider Pricing and Deployment Guide

<p>MiMo-V2.5 is worth paying attention to because it puts three things developers usually have to trade off into the same conversation: open weights, a 1 million-token model design, and pricing that can be unusually low depending on where you buy it. On Xiaomi&#8217;s first-party API, Artificial Analysis lists MiMo-V2.5 at $0.14 per 1M input tokens [&hellip;]</p>

Best API Providers for DeepSeek V4 in 2026

<p>DeepSeek V4 is available across a range of hosted API providers, each with different pricing, performance, and deployment trade-offs. The model comes in two variants: V4 Pro, a 1.6 trillion total parameter Mixture-of-Experts model with 49 billion active parameters and a 1M token context window, and V4 Flash, a lighter 284B total parameter variant built [&hellip;]</p>
