---
vendor: deepinfra
title: Wan 3.0 API Benchmarks: Speed, Latency & Cost
original_title: 
url: https://deepinfra.com/blog/wan-3-0-api-benchmarks
date: 2026-10-21
lang: en
captured: 2026-10-22
extractor: readability-v1
status: ok
body_sha: f9958bdb047d
---

# Wan 3.0 API Benchmarks: Speed, Latency & Cost

Published on 2026.10.21 by DeepInfra

![Wan 3.0 API Benchmarks: Speed, Latency & Cost](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/10/api.png)

## **Key Takeaways**

- Wan 3.0 leads the Artificial Analysis text-to-video leaderboard with audio at 1,173 Elo, so provider choice comes down to price, input support, and reliability.
- Per-second prices vary widely. Alibaba Cloud and fal list $0.05, $0.10, and $0.20 at 480P, 720P, and 1080P, and OpenRouter lists a rate from $0.0425.
- DeepInfra lists one rate of $0.20 per second, serves the whole Wan family from Wan2.2 to Wan3.0 through one API, and applies a zero-retention policy.
- OpenRouter publishes measured latency and availability for Wan 3.0, which makes operational risk easier to price in.

Wan is Alibaba’s family of video generation models. The earlier [Wan2.2](https://deepinfra.com/Wan-AI/Wan2.2-T2V-A14B) models ship as open weights under Apache 2.0, while later releases such as [Wan2.6](https://deepinfra.com/Wan-AI/Wan2.6-T2V), [Wan2.7](https://deepinfra.com/Wan-AI/Wan2.7-R2V), and [Wan3.0](https://deepinfra.com/Wan-AI/Wan3.0-Video) are delivered through hosted APIs.

Wan 3.0 is the first Wan model to accept documents and web pages as input. It also doubles the maximum clip length to 30 seconds.

| **Model** | **Key capabilities** | **Access** |
| --- | --- | --- |
| Wan 3.0 | Clips up to 30 seconds, 480P to 1080P, native audio, document and web page input | Hosted API |
| Wan 2.7 | Clips up to 15 seconds, image-to-video, reference-to-video, video editing | Hosted API |
| Wan 2.6 | Multi-shot storytelling, consistent subjects, clips up to 15 seconds | Hosted API |
| Wan 2.2 | Open-weight text-to-video and image-to-video models | Open weights (Apache 2.0) |

On the Artificial Analysis text-to-video leaderboard with audio, Wan 3.0 ranks first at 1,173 Elo. Utopai X follows at 1,166, then Dreamina Seedance 2.5 at 1,159 and MiniMax H3 at 1,158. The 95% interval for Wan 3.0 runs from 1,157 to 1,189, so the top models sit close together.

## **Provider Comparison Table**

The table lists the standard Wan 3.0 tier. Prices are per second of generated video.

| **Provider** | **480P** | **720P** | **1080P** | **Notes** |
| --- | --- | --- | --- | --- |
| DeepInfra | $0.20 | $0.20 | $0.20 | Single listed rate |
| Alibaba Cloud (Singapore) | $0.05 | $0.10 | $0.20 | US and Europe regions list $0.041256, $0.082513, and $0.165025 |
| OpenRouter | $0.0425 | $0.085 | $0.17 | Includes a 15% discount, one provider behind the endpoint |
| fal | $0.05 | $0.10 | $0.20 | Prime tier also available |
| Atlas Cloud | $0.04 | Not listed | $0.16 | Includes a 20% discount shown on the page |

## **How the Providers Are Compared**

- **Price per second:** The listed rate at each resolution tier, since video models bill by generated duration.
- **Input support:** Whether the endpoint accepts reference images, video, audio, documents, and web pages.
- **Operational data:** Latency and availability where a provider publishes them.
- **Data handling:** Retention policy and compliance certifications.
- **Quality:** Artificial Analysis scores Wan 3.0 as a model, which keeps the focus on the four factors above.

## **Top API Providers for Wan Models**

### **DeepInfra**

DeepInfra serves the Wan family from Wan2.2 through Wan3.0 behind one API, so teams can move between generations without changing vendors. [Wan3.0-Video](https://deepinfra.com/Wan-AI/Wan3.0-Video) is billed at $0.20 per second of output.

The Wan models available on DeepInfra are:

| **Model** | **Price** | **Capabilities** |
| --- | --- | --- |
| Wan3.0-Video | $0.20 per second | Clips up to 30 seconds, omni-modal reference, audio |
| [Wan2.7-R2V](https://deepinfra.com/Wan-AI/Wan2.7-R2V) | $0.10 per second | Reference-to-video that keeps the look and voice of people or objects |
| [Wan2.6-T2V](https://deepinfra.com/Wan-AI/Wan2.6-T2V) | $0.10 per second | Text-to-video with multi-shot storytelling, up to 15 seconds |
| [Wan2.2-T2V-A14B](https://deepinfra.com/Wan-AI/Wan2.2-T2V-A14B) | $0.075 per second | Open-weight text-to-video model at 480p |

DeepInfra also lists Wan2.7-I2V and Wan2.6-I2V at $0.10 per second. Artificial Analysis includes the Wan 2.2 A14B endpoint on DeepInfra in its generation-time tracking.

Data handling is a strength. DeepInfra runs a [zero-retention policy](https://deepinfra.com/blog/data-sovereignty-ai-open-weight-adoption) for inputs, outputs, and user data, and the platform is SOC 2 and ISO 27001 certified.

The trade-off is price at low resolutions. The single $0.20 rate matches Alibaba Cloud’s 1080P price but sits above the 480P and 720P rates elsewhere.

Verdict: DeepInfra fits teams that render final clips at 1080P, want one API across several Wan generations, and need clear data handling terms.

### **Alibaba Cloud**

Alibaba Cloud offers direct access through Model Studio, with the full Wan 3.0 feature set and regional pricing. The Singapore region lists $0.05, $0.10, and $0.20 per second. Regions in the US, Germany, Japan, and China list $0.041256, $0.082513, and $0.165025.

- Rate limit of 300 requests per minute in every listed region
- A Prime tier at $0.068, $0.14, and $0.28 per second in Singapore, aimed at faster generation
- Editing, extension, and reference-guided generation from the first-party API
- No support for batch inference or fine-tuning

Alibaba notes that audio texture and on-screen text rendering are still maturing. Verdict: Alibaba Cloud suits enterprise teams that want first-party access and regional pricing options.

### **OpenRouter**

OpenRouter lists Wan 3.0 under alibaba/wan-3.0 with a release date of August 24, 2026. It routes to a single provider, Alibaba Cloud, and shows rates from $0.0425 per second at 480P with a 15% discount applied.

OpenRouter publishes operational data for the endpoint. At the time of writing, the best provider shows a median end-to-end latency of about 149 seconds and availability near 85% over three days. These figures move, so check the live page.

Verdict: OpenRouter fits cost-sensitive teams that want one billing relationship and visible reliability data.

### **fal**

fal serves Wan 3.0 through the alibaba/wan-3.0 endpoints and lists $0.05, $0.10, and $0.20 per second at 480p, 720p, and 1080p. A Prime variant lists $0.068, $0.14, and $0.28.

- Duration from 2 to 30 seconds, with a null value for smart duration
- Aspect ratios of adaptive, 16:9, 4:3, 1:1, 3:4, and 9:16
- A JavaScript client published as @fal-ai/client
- A safety checker that is on by default

Turning off prompt expansion can save roughly 20 to 60 seconds of latency, according to fal. Verdict: fal fits web teams that want a typed client and queue-based requests.

### **Atlas Cloud**

Atlas Cloud lists Wan 3.0 at $0.05 per second, shown as $0.04 after a 20% discount. A Prime tier lists $0.068, shown as $0.061 after 10% off. The page lists SOC 2 Type II certification and HIPAA alignment.

Reference-to-video accepts up to 20 mixed references: 10 images, 5 videos, and 5 audio clips. Verdict: Atlas Cloud suits teams with compliance requirements that also want low per-second rates.

## **Why DeepInfra Fits Production Wan Workloads**

Price per second is only one input. Production teams also weigh data handling, vendor count, and how easily they can add other models later.

- One API covers every Wan generation from Wan2.2 to Wan3.0, plus other video models such as Google Veo 3.1 Fast at $0.15 per second.
- Zero retention and SOC 2 and ISO 27001 certification cover regulated review processes.
- A single listed rate makes budgeting simple for fixed-resolution pipelines.

The table shows what a 10-second clip costs at each resolution. DeepInfra’s single rate makes it a fit for 1080P work.

| **Provider** | **480P** | **720P** | **1080P** |
| --- | --- | --- | --- |
| DeepInfra | $2.00 | $2.00 | $2.00 |
| Alibaba Cloud (Singapore) | $0.50 | $1.00 | $2.00 |
| OpenRouter | $0.425 | $0.85 | $1.70 |
| fal | $0.50 | $1.00 | $2.00 |

Teams that also run video models from other labs can add [Google Veo 3.1 Fast](https://deepinfra.com/google/veo-3.1-fast) through the same API.

## **Frequently Asked Questions**

### **Which provider is cheapest for Wan 3.0?**

It depends on resolution. At 480P, Atlas Cloud shows $0.04 after its discount, Alibaba’s US region lists $0.041256, and OpenRouter lists $0.0425. At 1080P, Atlas Cloud shows $0.16 and OpenRouter lists $0.17.

### **How much does a Wan 3.0 video cost through an API?**

A 5-second 720P clip costs about $0.425 on OpenRouter, $0.50 on Alibaba Cloud’s Singapore region and fal, and $1.00 on DeepInfra. A 5-second 1080P clip costs $1.00 on DeepInfra, Alibaba Cloud, and fal.

### **What is the difference between Wan 2.x and Wan 3.0?**

Wan 3.0 extends a single generation to 30 seconds, up from 15 seconds in Wan 2.7. It adds document and web page input, carries forward the editing features from Wan 2.7, and ships as a managed service.

### **Is Wan 3.0 open source?**

Alibaba offers Wan 3.0 through managed APIs. The Wan2.2 weights are published on Hugging Face under the Apache 2.0 license.

### **Can I run Wan locally?**

Yes, with Wan2.2. The Wan2.2 T2V A14B and TI2V 5B weights are on Hugging Face under Apache 2.0. DeepInfra also hosts the A14B model if you prefer an API.

## **Conclusion**

Choosing a Wan API provider means comparing price at your working resolution, the inputs you need, and how much operational data the provider publishes. Quality is set by the model, so the decision rests on those practical factors.

- Choose DeepInfra for one API across Wan generations, 1080P final renders, and zero-retention data handling.
- Choose Alibaba Cloud for first-party access, regional pricing, and a Prime tier.
- Choose OpenRouter for a low 1080P rate and published reliability figures.
- Choose fal or Atlas Cloud for a typed client or compliance listings.

A similar comparison for language models covers [GLM-5.3 API providers](https://deepinfra.com/blog/best-glm-5-3-api-providers).

Related articles

[![MCP Servers Explained: A Practical Guide for Developers](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/09/MCP-servers.png)](https://deepinfra.com/blog/mcp-servers-explained)[MCP Servers Explained: A Practical Guide for Developers](https://deepinfra.com/blog/mcp-servers-explained)<p>Giving an AI application access to a database, API, file system, or internal service sounds simple until you have to maintain the integration. You need to define what the model can access, describe operations, execute requests safely, return structured results, and handle authentication. You may need to repeat much of that work when another AI [&hellip;]</p>

[![Kimi K3 vs Claude Opus 4.8 vs GPT-5.6 Sol: Practical AI Model Comparison](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/07/kimi-closed-source.png)](https://deepinfra.com/blog/kimi-k3-vs-claude-opus-4-8-vs-gpt-5-6-sol)[Kimi K3 vs Claude Opus 4.8 vs GPT-5.6 Sol: Practical AI Model Comparison](https://deepinfra.com/blog/kimi-k3-vs-claude-opus-4-8-vs-gpt-5-6-sol)<p>What&#8217;s changed since this comparison first ran Two of the three models compared here have since been succeeded, and GPT-5.6 Sol&#8217;s pricing has changed materially. Three of the strongest models available on DeepInfra right now don’t separate cleanly by capability tier. Kimi K3 (available via DeepInfra), Claude Opus 4.8, and GPT-5.6 Sol all score within [&hellip;]</p>

[![Best Qwen3.8-27B Inference Providers (2026)](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/10/qwen3.8-27b-best-providers.png)](https://deepinfra.com/blog/best-qwen3-8-27b-inference-providers)[Best Qwen3.8-27B Inference Providers (2026)](https://deepinfra.com/blog/best-qwen3-8-27b-inference-providers)<p>Qwen3.8-27B has shifted the landscape of open-weight models. It strikes an exceptional balance between parameter count and reasoning capability: a 27-billion parameter model that is highly capable yet compact. It runs on a single 24GB card at 4-bit quantization, or a single 80GB card at full precision. Finding the right infrastructure to host, scale, or [&hellip;]</p>

[View all](https://deepinfra.com/blog)
