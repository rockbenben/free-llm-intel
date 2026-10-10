---
vendor: deepinfra
title: DeepSeek V4.1 Flash API: Speed, Latency & Cost
original_title: 
url: https://deepinfra.com/blog/deepseek-v4-1-flash-api-benchmarks
date: 2026-09-30
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: c4e971084272
---

DeepSeek V4.1 Flash API: Speed, Latency & Cost

Published on 2026.09.30 by DeepInfra

## **DeepSeek V4.1 Flash (Reasoning, Max Effort) API Review Summary**

Metric

Value

Context

Intelligence

40 (Artificial Analysis Intelligence Index)

Well above median for comparable open-weight models (median: 18)

Speed

211.5-545.6 output tokens/sec

Notably fast; median: 68.9 t/s

Latency (TTFT)

1.19s-5.28s (varies by provider)

Competitive; median: 2.32s

Price (DeepSeek API)

$0.30/1M input, $1.20/1M output (peak)

Cache discount: 98%

Cost per Intelligence Index task

$0.27

Verbosity

250M output tokens during eval

High vs median: 140M

Context window

1M tokens

~1,500 A4 pages

Modalities

Text + image input; text output

Open weights / License

Open weights, MIT license

Commercial use allowed

Model size

552B total parameters, 8-16B active (MoE)

Release

September 10, 2026

Total cost to run Intelligence Index eval

$476.89

The open-weights AI landscape reached a new milestone on September 10, 2026, when DeepSeek released V4.1 Flash, a model that challenges the assumption that frontier-class intelligence requires proprietary infrastructure. The Chinese AI company that made waves at the start of 2025 with its low cost reasoning model has just released DeepSeek-V4.1 Flash, a model it calls smarter, faster, and more efficient.

Tests by multiple parties put V4.1-Flash ahead of V4-Pro on performance, cost, speed & total runtime. DeepSeek is phasing out V4-Pro. This comprehensive guide breaks down everything developers and enterprise architects need to know: from architecture and benchmark scores to API provider comparisons and deployment considerations.

## **Model Summary**

[DeepSeek-V4.1-Flash](https://deepinfra.com/deepseek-ai/DeepSeek-V4.1-Flash) is a multimodal Mixture-of-Experts (MoE) model with 552B backbone parameters and support for contexts of up to one million tokens. The model natively processes images and text, and generates text autoregressively.

DeepSeek-V4.1-Flash adopts a Causal Encoder-Decoder (CED) architecture: a 40-layer Transformer organized as a 20-layer causal encoder followed by a 20-layer decoder. This architectural innovation enables the model to activate fewer parameters during input processing than during output generation, dramatically improving efficiency.

### **Highlights**

- **Frontier-class intelligence at Flash-tier pricing: **DeepSeek V4.1 Flash (Reasoning, Max Effort) is amongst the leading models in intelligence and reasonably priced when comparing to other open weight models of similar size.
- **Massive context window: **Same [1M-token context](https://getdeploying.com/llms/deepseek-v4.1-flash) as its predecessor, enabling processing of entire codebases or lengthy documents
- **Native multimodal support: **This model is the smallest in its new architecture family, which now [natively supports visual understanding](https://www.neowin.net/news/deepseek-launches-v41-flash-multimodal-reasoning-model/).
- **MIT-licensed open weights: **Full commercial use permitted
- **Exceptional efficiency: **DeepSeek-V4.1-Flash achieves approximately 4-fold and 437-fold reductions in KV cache size relative to DeepSeek-V4-Flash and DeepSeek-V1, respectively.

## **Technical Specifications**

### **Total Parameters**

It’s a [552B-parameter mixture-of-experts model](https://www.yottalabs.ai/post/deepseek-v4-1-flash-pricing-specs-v4-pro-routing-2026) with a new encoder-decoder architecture.

### **Active Parameters**

DeepSeek-V4.1 Flash boasts a 552 billion parameter Mixture of Experts design that delivers more intelligence at a low cost. It also uses a new Causal Encoder-Decoder architecture which means this model uses just eight billion active parameters for input and 16 billion for output.

### **Model Size**

DeepSeek V4.1 Flash is [510 GB on disk](https://www.yottalabs.ai/post/deepseek-v4-1-flash-hardware-requirements-gpu-memory-2026). The checkpoint is 510 GB across 48 shards.

DeepSeek V4 Flash was 166.9 GB and ran on two H200s; its replacement is three times the size.

### **Model Weights**

The weights are on [Hugging Face](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash) under MIT. The weights are publicly available for download, allowing developers to host, fine-tune, and deploy the model on their own hardware.

### **License**

The weights are MIT licensed. This permissive license allows for commercial use, modification, distribution, and private use without restrictions.

### **Input Modality**

The model natively processes images and text. This multimodal capability enables vision-language tasks without requiring separate vision encoders.

### **Output Modality**

The output modality is strictly Text. The model generates text autoregressively based on text and/or image inputs.

### **Context Window**

1M context, equivalent to approximately 1,500 A4 pages or 750,000 words. This enables processing of entire codebases, lengthy legal documents, or extensive research papers in a single prompt.

## **Reasoning Capabilities**

### **Reasoning**

DeepSeek-V4.1-Flash supports a continuously controllable reasoning effort from 1 to 100. All instruct results below use the maximum effort setting (reasoning_effort=100).

This continuous reasoning dial represents a significant advancement over previous discrete modes (Non-think, Think High, Think Max), allowing fine-grained control over the compute-accuracy tradeoff.

### **Intelligence**

DeepSeek V4.1 Flash (Reasoning, Max Effort) achieves a score of 40 on the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/deepseek-v4-1-flash). This composite benchmark evaluates models across reasoning, knowledge, mathematics, and coding.

### **Intelligence Index Comparisons**

DeepSeek V4.1 Flash (Reasoning, Max Effort) scores 40 on the Artificial Analysis Intelligence Index, placing it well above average among comparable models (median: 18).

DeepSeek also used new pre-training methods and larger-scale reinforcement learning post-training to deliver benchmark results that outdo flagship models such as Kimi-K3, GLM-5.3, Claude Opus 5, GPT 5.6-Sol, and DeepSeek-V4-Pro.

### **Capability Indices**

Benchmark

Score

MMLU

91%

MMLU-Pro

81.2%

HLE (High-Level Expertise)

36.8%

IFEval

89.5%

SimpleQA

49%

AIME 2025

87.5%

Deep SWE

74.2%

DeepSeek V4.1 Flash [scored 91% on MMLU](https://automatio.ai/models/deepseek-v4-1-flash). DeepSeek V4.1 Flash scored 81.2% on MMLU Pro.

### **Intelligence Breakdown**

- **Linguistic Intelligence: **Excellent command of English and multilingual tasks with 89.5% on instruction following
- **Mathematical Intelligence: **Strong performance with 87.5% on AIME 2025 competition-level problems
- **Coding Intelligence: **DeepSeek V4.1 Flash scores 74.2 on Deep SWE, putting it in the [same range as GPT-6 Astra, Gemini 3.8 Flash, and Opus 5](https://www.mindstudio.ai/blog/deepseek-v4-1-flash-benchmarks).
- **Visual Intelligence: **Native image understanding for vision-language tasks

## **Performance Metrics**

### **Speed**

At 214 tokens per second, DeepSeek V4.1 Flash (Reasoning, Max Effort) is notably fast. [Provider speeds vary significantly](https://artificialanalysis.ai/models/deepseek-v4-1-flash/providers): For output speed, the top providers are Inco (FAST) (545.6 t/s), LithosAI (402.5 t/s), and Databricks (338.2 t/s).

### **Latency**

Speed varies significantly across providers, with a 344% difference between the fastest and slowest. For latency, Inco (FAST) (5.28s), LithosAI (6.00s), and Databricks (7.17s) offer the lowest time to first answer token.

### **End-to-End Response Time**

For standard workloads, end-to-end response time typically ranges from 5-15 seconds depending on provider and reasoning effort setting. The model’s high output speed (200+ t/s on premium providers) means that even lengthy responses complete quickly once generation begins.

### **Token Use**

When evaluating the Intelligence Index, it generated 250M tokens, which is very verbose in comparison to the median of 140M.

This verbosity is an important consideration for cost planning: the model tends to generate comprehensive, detailed responses that consume more output tokens than average.

## **Cost**

### **Pricing Structure**

The model name is deepseek-flash, the price is $0.15 per million input tokens and $0.60 per million output off-peak, double that at peak, and cache hits are $0.003.

Pricing Tier

Input (per 1M tokens)

Output (per 1M tokens)

Cache Hits

Off-Peak

$0.15

$0.60

$0.003

Peak

$0.30

$1.20

$0.006

[Peak hours are 01:00 – 04:00 and 06:00 – 10:00 UTC](https://techjacksolutions.com/ai-tools/deepseek/deepseek-v4-1-flash/), Monday through Friday; all other hours are off-peak and billed at half the peak rate.

### **Cache Economics**

Cache hits carry a steep discount, about 98 percent off the cache-miss rate per token ($0.006 against $0.30 at peak).

A system prompt or tool schema reused across many requests costs a small fraction of a fresh prompt of the same length, which matters most for agentic workflows that resend the same scaffolding on every step.

### **Cost Comparison**

Pricing for DeepSeek V4.1 Flash (Reasoning, Max Effort) is $0.30 per 1M input tokens (moderately priced, median: $0.30) and $1.20 per 1M output tokens (somewhat expensive, median: $1.15).

In total, it cost $476.89 to evaluate DeepSeek V4.1 Flash (Reasoning, Max Effort) on the Intelligence Index.

### **Openness**

[Released open-source under MIT license](https://apxml.com/models/deepseek-v4-1-flash) on April 24, 2026.

DeepSeek V4.1 Flash represents a high-water mark for open-weights AI. The MIT license places no restrictions on commercial use, modification, or redistribution. Developers have full access to:

- Model weights (510 GB checkpoint)
- Architecture documentation
- Training methodology details
- Evaluation scripts and benchmarks

This openness enables enterprises to deploy on-premises, fine-tune for specific domains, and integrate without vendor lock-in concerns.

## **API Providers**

### **Available Providers**

DeepSeek V4.1 Flash is served by [19 providers on OpenRouter](https://openrouter.ai/deepseek/deepseek-v4.1-flash): Alibaba Cloud Int., Relace, DeepSeek, Morph, DeepInfra, Fireworks, GMICloud, AtlasCloud and 11 more.

DeepSeek V4.1 Flash (Reasoning, Max Effort) is available through 8 API providers: DeepSeek, Novita, Fireworks, Parasail, Baseten, Databricks, Inco (FAST), and LithosAI.

### **API Provider Benchmarks**

Provider

Output Speed

TTFT

Blended Price (per 1M)

Inco (FAST)

545.6 t/s

5.28s

N/A

LithosAI

402.5 t/s

6.00s

$0.09

Databricks

338.2 t/s

7.17s

$0.08

Fireworks

~250 t/s

N/A

$0.11

DeepSeek

211.5 t/s

1.19s

$0.06-0.30

Inco (FAST) offers the best performance with both the highest speed and lowest latency.

For pricing, Databricks (0.08), LithosAI (0.09), and Fireworks (0.11) offer the lowest blended prices per 1M tokens. Prices vary up to 4.9x across providers.

### **Provider Comparison Table**

Feature

DeepSeek (First-Party)

DeepInfra

Fireworks

Databricks

Output Speed

211.5 t/s

High

~250 t/s

338.2 t/s

TTFT

1.19s

~1.11s

N/A

7.17s

Input Cost

$0.30 (peak)

Competitive

$0.11 blended

$0.08 blended

Output Cost

$1.20 (peak)

Competitive

N/A

N/A

Cache Discount

98%

Varies

N/A

N/A

1M Context

✓

✓

✓

✓

Image Input

✓

✓

✓

✓

For most production-scale deployments, DeepInfra offers the strongest combination of low latency, [competitive pricing on both V4 variants](https://deepinfra.com/blog/best-api-providers-for-deepseek-v4), and a full-featured OpenAI-compatible API.

## **Self-Hosting Requirements**

### **Hardware Requirements**

DeepSeek V4.1 Flash needs about 614 GB of GPU memory.

DeepSeek V4.1 Flash is the first Flash model that needs a whole node.

The day-one serving recipes from vLLM, SGLang, and NVIDIA all start at four Blackwell-class GPUs or eight H200s.

### **Quantization Options**

DeepSeek V4.1 Flash needs about 306 GB of GPU memory at 4-bit with 32K context.

The cheapest rental that fits is 8× RTX A6000 at about $3,168 a month. That costs the same as roughly 7B tokens a month on DeepSeek’s API. Self-hosting is more expensive below that volume.

### **Software Support**

vLLM 0.30.0 or later, with the deepseekv41-flash-0909 tagged image on NVIDIA and the ROCm nightly on AMD. SGLang’s day-zero build supports it with attention and MoE backends auto-selected from the checkpoint.

## **Overall Recommendation**

DeepSeek V4.1 Flash represents an exceptional value proposition for teams seeking frontier-class intelligence without proprietary lock-in. DeepSeek’s claim is that V4.1 Flash beats V4 Pro on “performance, cost, speed, and task completion time.”

**Best for:**

- Long-context agent and coding workloads
- RAG pipelines requiring extensive document processing
- Multimodal applications mixing images with text
- Cost-sensitive deployments with high token volumes
- Agentic workflows leveraging cache discounts

**Consider alternatives if:**

- You need consumer-grade self-hosting options
- Your use case requires minimal verbosity
- You need guaranteed benchmark-to-production parity (some hands-on tests show gaps)

DeepSeek V4.1 Flash matches Opus 5 and GPT-5.6 on paper, but hands-on coding tests expose a gap between benchmark scores and real output. Evaluate thoroughly for your specific use case.

For API access, DeepInfra (deepinfra.com) offers an excellent balance of performance, pricing, and developer experience, particularly important given the model’s verbosity, where provider-level differences in throughput and caching economics materially impact total cost.

## **Conclusion**

DeepSeek V4.1 Flash marks a significant milestone in open-weights AI development. The firm said that this model is designed for greater capability, faster inference, higher throughput, and scaling to larger models.

With 552B total parameters, 8-16B active parameters, a 1M-token context window, native multimodal support, and MIT licensing, it delivers frontier-class capabilities at a fraction of proprietary model costs. The 98% cache discount makes it particularly compelling for agentic workflows.

V4.1-Flash lets DeepSeek serve more users at a lower cost. They’re [passing the savings on to users](https://deepseek.com/en/news/deepseek-v4-1-flash/).

Whether you’re building production AI applications, conducting research, or exploring the cutting edge of language model capabilities, DeepSeek V4.1 Flash deserves serious consideration, accessible via DeepInfra and numerous other providers, or self-hosted under the permissive MIT license.

## **Frequently Asked Questions**

### **Can I run DeepSeek V4.1 Flash on consumer hardware?**

No. DeepSeek V4.1 Flash is 510 GB on disk and needs about 614 GB of GPU memory. Even with quantization, you need enterprise-grade GPU infrastructure.

### **Does DeepSeek V4.1 Flash support image inputs?**

Yes. The model natively processes images and text.

### **Is it free for commercial use?**

Yes. The weights are MIT licensed.

### **What happened to DeepSeek V4 Pro?**

From 04:00 UTC on Sept 14, 2026, all deepseek-v4-pro requests will route to V4.1-Flash at V4.1-Flash rates.

### **How does the reasoning effort dial work?**

The model supports a continuously controllable reasoning effort setting (integer 1-100) that trades inference cost for accuracy.

### **Why is the model so verbose?**

It’s also notably fast, however very verbose. The model tends to provide comprehensive, detailed responses. Plan for higher output token consumption when budgeting.

Related articles

Introducing NVIDIA Nemotron 3 Nano Omni on DeepInfra

DeepInfra is an official launch partner for NVIDIA Nemotron 3 Nano Omni, the first multimodal model in the Nemotron 3 family — a single open model that understands images, video, audio, documents, and text in one unified inference pass.

Best SaaS Tools and API Providers for GLM-5.2

<p>GLM-5.2 represents a significant leap forward in open-weight models, particularly for complex reasoning, long-context processing, and agentic coding tasks. Deploying a model of this scale — especially with its massive 1-million token context window and Mixture-of-Experts (MoE) architecture — presents real infrastructure challenges. Managing memory bandwidth, optimizing time to first token (TTFT), and handling quantization [&hellip;]</p>

GLM 5.2 vs Claude Opus 4.8: Pricing the Task, Not the Token

<p>Every GLM 5.2 vs Claude Opus 4.8 comparison lands in the same place. Opus wins most coding benchmarks, GLM costs a fraction as much, pick according to your budget. That framing takes the price cards at face value, but it’s misleading. Price a finished unit of work instead of a million tokens and the gap [&hellip;]</p>
