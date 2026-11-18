---
vendor: deepinfra
title: DeepInfra Partners with Opper AI: 100+ Models on the Opper Gateway
original_title: DeepInfra Partners with Opper AI: 100+ Models on the Opper Gateway
url: https://deepinfra.com/blog/deepinfra-opper-partnership
date: 2026-11-17
lang: en
captured: 2026-11-18
extractor: readability-v1
status: ok
body_sha: fb101359f42d
---

# DeepInfra Partners with Opper AI: 100+ Models on the Opper Gateway

Published on 2026.11.17 by DeepInfra

![DeepInfra Partners with Opper AI: 100+ Models on the Opper Gateway](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/11/deepinfra-opper-partnership-header.png)

*Palo Alto, California, November 2026.* DeepInfra and [Opper AI](https://opper.ai/blog/deepinfra-partnership) are partnering to make DeepInfra’s open-model inference available through Opper’s EU-hosted AI gateway. Developers can now call more than 100 DeepInfra-hosted models through the Opper API, from Kimi K3, GLM-5.3 and DeepSeek V4.1 Flash to MiniMax M3, Nemotron 3.5 Super VL and FLUX.2 Pro, and apply Opper’s spend, retention and routing Rules to every call.

## What this means for developers

If you already run on DeepInfra, nothing changes on your existing integration. The partnership adds a second route to the same models: through Opper, alongside the other providers you may already use there.

**One model string per tier.** Every DeepInfra chat model on Opper has a standard tier, and many also come as flex and priority:

| Opper model string | What it’s for |
| --- | --- |
| `deepinfra/…` | Standard tier, for everyday calls |
| `deepinfra:flex/…` | About a fifth cheaper, for evaluations and background work |
| `deepinfra:priority/…` | Interactive traffic that must answer first |

Large jobs can go through Opper’s [Batch API](https://opper.ai/blog/batch-vs-flex-vs-standard) at the flex price. Per-tier prices for each model, plus DeepInfra’s image, speech, video and embedding models, are listed on [Opper’s DeepInfra provider page](https://opper.ai/provider/deepinfra).

**The catalog.** Through Opper you can reach the open models agents run today: DeepSeek V4 and V4.1, Moonshot’s Kimi K3, Z.ai’s GLM-5.3, the Qwen3.5 to Qwen3.8 lineup, Google’s Gemma 4, Meta’s Llama and Thinking Machines’ Inkling. The same route covers image models from Black Forest Labs, ByteDance’s Seedance 2.0 for video, Qwen3 TTS for speech and embeddings for search, as well as NVIDIA’s Nemotron family, from Nemotron 3.5 Super VL to Nemotron 3 Ultra.

**Price.** According to Opper, DeepInfra is currently the cheapest route on the Opper gateway, in any region, for MiniMax M3, NVIDIA Nemotron 3.5 Super VL, DeepSeek V3.2 and Qwen3 235B Instruct 2507.

**Data handling.** Every DeepInfra route on Opper runs in the United States. On standard, flex and priority calls, prompts and completions are not logged or used for training, and a DPA is available. Batch jobs hold requests until they run, as any batch API must. DeepInfra owns and operates its GPU infrastructure and is SOC 2 and ISO 27001 certified. Opper’s provider page lists residency and retention for each route.

### A first call

Opper is OpenAI-compatible, so switching to a DeepInfra model is a change of base URL and model string:

```
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPPER_API_KEY"],
    base_url="https://api.opper.ai/v3/compat",
)

completion = client.chat.completions.create(
    model="deepinfra/MiniMaxAI/MiniMax-M3",  # or "deepinfra:flex/MiniMaxAI/MiniMax-M3" for background work
    messages=[{"role": "user", "content": "Hello"}],
)
print(completion.choices[0].message.content)copy
```

## Why Opper: Rules for every call

Opper describes itself as the European AI gateway for agents. Based in Stockholm, it gives developers more than 700 models through one EU-hosted, GDPR-compliant API. Routing is only part of what it does. Every call through Opper can run under your **[Rules](https://opper.ai/ai-control-plane)**: spend limits, data retention, model access, content checks and routing order, set once for the organization or per project.

For DeepInfra users, that means you can:

- pin DeepInfra’s flex tier for evaluation runs,
- set DeepInfra as a fallback behind another provider, or the other way round,
- cap spend and limit which models a project can call, without changing application code.

## Opper or DeepInfra’s API directly?

Both routes reach the same DeepInfra models. The choice depends on what sits around the call.

**Use Opper when** you use models from several providers through one key, want spend caps, model allowlists and retention rules managed centrally, or want routing and fallback between DeepInfra and other providers handled by the gateway.

**Use DeepInfra’s API directly when** your workload runs only on DeepInfra models and you don’t need a gateway in the request path. You get the full [DeepInfra model catalog](https://deepinfra.com/models), the [pricing](https://deepinfra.com/pricing) listed on each model page, and the [Flex service tier](https://deepinfra.com/blog/flex-service-tier) for work that can wait.

## Quotes

“DeepInfra runs one of the deepest open-model catalogues anywhere, at prices that make it a natural home for high-volume work. With standard, flex, priority and batch on the same models, builders on Opper can match every call to the speed and price it needs.” — Göran Sandahl, Co-founder and CEO, Opper AI

“We built DeepInfra to run open models at production scale on our own GPUs, at a price that works for every token. Opper puts that catalogue in front of a wide community of builders through one API, next to every other model they already use.” — Nikola Borisov, Co-founder and CEO, DeepInfra

## Availability

DeepInfra models are live on Opper today. To get started:

- Read Opper’s announcement: [Opper AI partners with DeepInfra to bring 100+ AI models to the gateway](https://opper.ai/blog/deepinfra-partnership)
- See models, tiers and per-route prices on [Opper’s DeepInfra provider page](https://opper.ai/provider/deepinfra)
- Browse the [DeepInfra model catalog](https://deepinfra.com/models) and [pricing](https://deepinfra.com/pricing)

## About DeepInfra

DeepInfra is an inference cloud founded in 2022 and based in Palo Alto, California. It owns and operates its GPU infrastructure and serves open models for text, speech, image, video and embeddings through OpenAI-compatible APIs, with zero data retention and SOC 2 and ISO 27001 certification. In May 2026 it raised a $107M Series B co-led by 500 Global and Georges Harik, with NVIDIA, Samsung Next and Supermicro participating.

## About Opper AI

Opper AI is the European AI gateway for agents, based in Stockholm. It gives developers access to 700+ leading AI models through one EU-hosted, GDPR-compliant API, pay-as-you-go, with spend caps, model allowlists, zero data retention and full OpenAI SDK compatibility.

Related articles

[![GLM-5.3 Is Now Available on DeepInfra](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/09/glm-5.3-deepinfra.png)](https://deepinfra.com/blog/glm-5-3-deepinfra)[GLM-5.3 Is Now Available on DeepInfra](https://deepinfra.com/blog/glm-5-3-deepinfra)<p>GLM-5.3 shares its base model with GLM-5.2, so every performance gain comes from post-training. Z.ai scaled the reinforcement learning stack it already had and released the result on August 14, 2026. GLM-5.3 is a reasoning model built for complex software engineering and long-horizon agentic tasks. On Z.ai&#8217;s internal Code Bench, it improves 50% over GLM-5.2, [&hellip;]</p>

[![Introducing GPU Instances: On-Demand GPU Compute for AI Workloads](https://deepinfra.com/blog/gpu-instances.jpg)](https://deepinfra.com/blog/gpu-instances)[Introducing GPU Instances: On-Demand GPU Compute for AI Workloads](https://deepinfra.com/blog/gpu-instances)Launch dedicated GPU containers in minutes with our new GPU Instances feature, designed for machine learning training, inference, and compute-intensive workloads.

[![DeepInfra Launches Access to NVIDIA Nemotron Models for Vision, Retrieval, and AI Safety](https://deepinfra.com/blog/nvidia-deepinfra-logos.png)](https://deepinfra.com/blog/nvidia-nemotron-release)[DeepInfra Launches Access to NVIDIA Nemotron Models for Vision, Retrieval, and AI Safety](https://deepinfra.com/blog/nvidia-nemotron-release)DeepInfra is serving the new, open NVIDIA Nemotron vision language and OCR AI models from day zero of their release. As a leading inference provider committed to performance and cost-efficiency, we're making these cutting-edge models available at the industry's best prices, empowering developers to build specialized AI agents without compromising on budget or performance.

[View all](https://deepinfra.com/blog)
