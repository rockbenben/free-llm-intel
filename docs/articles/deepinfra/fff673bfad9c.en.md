---
vendor: deepinfra
title: Why Open Models Get Faster Weeks After Launch
original_title: 
url: https://deepinfra.com/blog/why-open-models-get-faster
date: 2026-10-31
lang: en
captured: 2026-11-01
extractor: readability-v1
status: ok
body_sha: 570cabed5996
---

# Why Open Models Get Faster Weeks After Launch

Published on 2026.10.31 by Niklas

![Why Open Models Get Faster Weeks After Launch](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/10/Why-New-Models-Get-Faster.png)

[Qwen3.8-Flash-Next](https://deepinfra.com/Qwen/Qwen3.8-Flash) was released on August 26, 2026. The same day, SGLang announced day-0 support, built with the Qwen, NVIDIA and AMD teams, and shipped a dedicated container image. vLLM served the model from its own dedicated image while the architecture-support work was still being merged. llama.cpp, the engine most people use to run models on their own hardware, picked up initial support in version 0.4.0 with a release note saying optimization improvements were still pending.

Three engines, three different answers to the question “can it run this model?”, all given within the first week. Every one of them said yes. None of them was saying the model would run fast, or cheaply, or at the context lengths the model was designed for. That second part took longer, and by early September community builds were already reporting double-digit gains from patches that touched nothing but the new attention indexer.

This pattern shows up with almost every new open model that introduces a new design, and it matters to anyone buying inference. The speed and price you see in week one are a starting point. This article explains why: what “supported at launch” really means, what custom engine work a new architecture demands (with Qwen3.8-Flash-Next as the worked example), which speed features switch on later, and how to plan around the curve if you are building on a model that just shipped.

## What “Supported at Launch” Means

When a provider says a model works on day one, it means the weights load, the architecture runs through a reference implementation, and the tokens that come out are correct. That is a real achievement for a design the engine has never seen, and it is what lets you start testing immediately.

It does not mean the model is running the way it eventually will. Day-one serving usually has some mix of the following:

- Operations running as generic kernels where hand-tuned, fused ones will later exist
- Speculative decoding or multi-token prediction switched off
- A higher-precision checkpoint in use because the lower-precision version has not been validated yet
- Cache management that works but wastes memory
- Scheduler settings tuned for the previous generation of models

Correctness comes first for good reason. A fast engine that returns subtly wrong answers is worse than a slow one, so teams run parity checks against the reference implementation before they enable anything aggressive. Speed arrives in layers, and each layer has to be proven safe.

## Why a New Architecture Needs New Engine Code

Inference engines are built around assumptions about what a transformer looks like. A model that changes those assumptions needs engine changes, not just a new config file. Qwen3.8-Flash-Next is a good illustration because its changes touch nearly every part of the serving stack.

The model has 125 billion parameters in its main body plus 51 billion in an n-gram embedding table, with only 6 billion parameters active per token. It uses 48 layers: 36 Gated DeltaNet layers that compress history into a fixed-size state, and 12 Qwen Sparse Attention layers that do precise retrieval over the full context. The [MoE layers](https://deepinfra.com/blog/mixture-of-experts-llm-economics-price-drop) route each token to 10 of 512 experts. Qwen describes it as an early preview of the architecture that will underpin Qwen4, much as Qwen3-Next previewed Qwen3.5.

### A Hybrid Layout the Engine Has Never Scheduled

Most engines manage memory around one assumption: every attention layer has a key-value cache that grows with the sequence. In this model, three out of four layers keep a fixed-size recurrent state instead, and only the remaining quarter keep a growing cache. The memory manager has to track both kinds of state per request, and it has to keep working with features like prefix caching (SGLang’s radix cache, for instance) that were designed before this layout existed. Getting that wrong does not crash anything. It quietly wastes memory and lowers the number of requests you can batch.

The same layout is also why the architecture is cheap at long context. Only 12 of the 48 layers store a growing cache, so the model’s memory savings come from the layout itself, as SGLang’s team points out, not from discarding anything inside the sparse attention layers. An engine that does not exploit this carefully gives the saving back.

### A Sparse Attention Indexer That Has to Be Written as Kernels

Qwen Sparse Attention works in two stages. A lightweight indexer scores compressed blocks of the context (every four tokens are averaged into one compressed key), keeps the best 512 blocks, and expands them to at most 2,051 token positions. Then ordinary sparse attention runs over just those positions, using the original uncompressed keys and values.

Neither stage exists as a stock kernel. SGLang wrote a custom GPU kernel for prefill scoring, a paged scorer for decode, and dispatches to different attention backends depending on the hardware (a TensorRT-LLM kernel path on Blackwell, packed FlashAttention elsewhere). It also stores one compressed index key per four tokens in a paged pool and keeps the raw keys for the unfinished block in a small per-request ring, which cut the index-cache overhead by 80%.

This is the kind of work that takes engine teams weeks, and it is why vLLM’s engine effort for this model centered on the sparse attention layers.

### Wider Residual Streams

The model replaces the single residual stream with four parallel branches, with a dynamic gate deciding how much to read from and write to each. Every block therefore needs a read operation (called Mix) and a write operation (called Combine) around it. These are tiny operations on a handful of tokens during decode, which makes them dominated by launch overhead rather than math.

SGLang and NVIDIA wrote shape-aware kernels for them, shipped through FlashInfer. At four tokens, the fused Mix kernel cut latency from 12.36 to 6.03 microseconds, and the split Combine kernel cut it from 4.17 to 2.13 microseconds. End to end, those two changes improved speculative-decode throughput by 7.6% and 5.5% respectively over earlier implementations. Neither number is dramatic alone, but a model has many such rough edges, and they add up.

### A 51-Billion-Parameter Table That Does Not Belong on the GPU

The n-gram embedding table is about 95 GiB in BF16, yet each token only looks up 16 rows from it. Holding the whole table in GPU memory would waste capacity that could hold cache. SGLang keeps the table in pinned host memory, gathers only the rows it needs on a separate CUDA stream, and overlaps that gather with the first decoder block.

On four H200 GPUs, this freed 23.46 GiB of weight memory per GPU and raised the allocated KV capacity from 1.84 million to 3.28 million tokens, a 78.5% increase, with a throughput change of just 0.07% across the concurrency levels they tested. More cache capacity means more concurrent requests per GPU, which feeds straight into cost per token.

## The Speed Features That Switch On Later

Alongside the architecture work, there is a set of general-purpose speed techniques that engines turn on once they are confident the output is unchanged. They tend to arrive in the first weeks, not on day one.

### Multi-Token Prediction and Speculative Decoding

A normal decode step produces one token per pass through the full model. Speculative decoding uses a cheap drafter to propose several tokens, then lets the full model verify them in a single pass. When the drafter guesses well, you get multiple tokens for the price of roughly one.

Qwen3.8-Flash-Next ships with its own draft module (about 4 billion MTP parameters), but using it well requires engine support. SGLang’s team added a feature called IndexShare MTP: because the sparse indexer is expensive at long context, and the draft steps only move a few positions, the indexer selection from the first step is reused by the later ones. On four B200 GPUs with the NVFP4 checkpoint, they report 540 tokens per second at batch size one, with an average accept length of 3.3 tokens per verification step.

The same story played out with [Google’s Gemma 4](https://deepinfra.com/blog/gemma-4-pricing-benchmarks-cost-scenarios). The family launched on April 2, 2026 with no speculative decoding assets, and Google released multi-token prediction drafters on May 5, reporting up to a 3x speedup with no change to outputs. That is a month, from the model’s own authors, for a technique the field already understood well.

### Lower-Precision Checkpoints

Lower precision means smaller weights, less memory traffic and more throughput, but each new format needs its own quantized checkpoint and its own quality check. For Qwen3.8-Flash-Next, SGLang’s documentation lists BF16, FP8 and NVFP4 builds as separate repositories, with NVFP4 limited to Blackwell GPUs. Providers rarely switch a production endpoint to a new precision until they have compared outputs on their own evaluation sets, so the cheapest format often shows up after the first one does.

### Kernel Fusion and Shape-Aware Dispatch

The Mix and Combine kernels above are examples of a broader habit: once the model is correct, engineers profile it, find the operations dominated by overhead, and fuse or reshape them. The gains are individually modest and collectively large, and they depend on the batch size and hardware, which is why they continue to land for weeks.

### Scheduling, Batching and Caching Tune-Ups

Every engine has settings for how many requests to batch, how to split prefill from decode, how long to keep prefixes cached, and how much memory to reserve. Defaults chosen for earlier models are often wrong for a new one. Hybrid models in particular change the trade-off, because their state does not grow the way a normal cache does, so tuning continues as providers see real traffic.

## What It Looked Like on the Local Side

llama.cpp makes the lifecycle easy to see in public, because its development happens in the open.

| **Stage** | **What was available** |
| --- | --- |
| Launch week | Tutorials told users to build an unmerged branch tied to Unsloth’s pull request, because mainline did not recognize the architecture |
| Early September | Support merged into mainline (PR #27742), described as initial, with optimizations pending |
| Release 0.4.0 | Adds a sparse flash attention path for DeepSeek-V4, GLM and the Qwen4 experimental architecture (PR #27970) |
| Community builds | One fork focused on the QSA indexer reported generation 8% faster at 8k context and 35% faster at 32k, with prompt processing 59% faster at 32k, and no change at zero context |

That last row is worth reading closely. The gains were largest at long context and absent at short context, which tells you exactly where the original implementation was slow: the indexer. The fork’s changes were five patches on the indexer, none of them touching a shader, such as scanning the cache table once per compression ratio instead of once per layer.

Early comparisons showed the gap in the other direction too. One user benchmarking on a single workstation GPU in early September reported that vLLM was around four times faster than llama.cpp at long context for this model, and that llama.cpp’s multi-token prediction support had not landed yet. That is a single report on one machine, so treat the ratio loosely, but the direction matches what the release notes say.

## Why Engine Speed Becomes Price

For a hosted API, the [cost of serving a token](https://deepinfra.com/blog/inference-economics-ai-costs-at-scale) is roughly the cost of a GPU hour divided by the tokens that GPU produces in that hour. When engine work raises throughput, the [cost per token](https://deepinfra.com/blog/pricing-101-token-math-cost-per-completion) falls even though the hardware bill does not change. If a node costs the same per hour and serves 1.5 times as many tokens, the cost per token drops by about a third.

Three of the improvements above act on that ratio directly:

- Cache memory savings (like the host-memory offload) let each GPU hold more concurrent requests
- Lower-precision weights move fewer bytes per token
- Fused kernels waste fewer cycles on overhead

Speculative decoding mostly improves latency for each individual request, and its effect on cost depends on load. It helps most when the GPU would otherwise be underused, which is typical at low batch sizes, and helps less when the hardware is already busy with large batches.

Providers do not all pass savings through at the same pace, and some never reprice. But the underlying cost curve moves, and competitive pressure among providers of an open model tends to pull prices toward it.

## How to Plan Around the Curve

If you are evaluating or building on a model that just launched, a few habits protect you from judging it too early.

- Treat week-one speed and price as a floor. Re-run your [latency and throughput tests](https://deepinfra.com/blog/llm-api-provider-performance-kpis-101) at 30 days.
- Test at your real context length. As the fork results show, the gains from new architectures are often concentrated at long context, so a short-prompt benchmark can miss them entirely.
- Ask which optimizations are active on the endpoint you are using, including the numeric precision of the checkpoint and whether speculative decoding is on. Precision changes can affect output quality, so keep a frozen evaluation set and re-run it when a provider changes the serving setup.
- Pin model versions where stability matters, and schedule a review when the provider announces a serving change.
- Keep your integration portable. A routing layer that can [move traffic between providers](https://deepinfra.com/blog/best-open-source-llm-api-providers) and models lets you take advantage of price drops without a rewrite.

For teams running their own inference, the same logic applies to engine versions. Expect to upgrade several times in the first month, and read release notes for the specific features your model needs.

## Caveats

Faster is not guaranteed for every model or every user. Speculative decoding gains depend on how predictable the output is, and the 3.3 accept length above is a single benchmark configuration on specific hardware. The NVFP4 numbers apply only to Blackwell GPUs. The community fork numbers come from one person’s setup, measured on consumer-class hardware.

Qwen3.8-Flash-Next is also an experimental preview. It is released under the Qwen Community License 1.0, not MIT, and Qwen’s own framing is that it previews the Qwen4 architecture. Previews can change, and engines sometimes deprioritize a design that does not become a mainstream family. The production Qwen3.8 Flash API, which carries the same family name, is the version most teams will actually build on.

Finally, some of the early performance data comes from the engine teams themselves, who have every reason to show their work in a good light. Independent measurements, as they appear, are worth more.

## The Bottom Line

A model’s launch day is the beginning of its serving story. New architectures arrive faster than inference engines can optimize for them, so the first version of support is built to be correct, and the fast version follows. Qwen3.8-Flash-Next shows how much sits in that gap: custom kernels for a sparse attention indexer, new memory management for a hybrid layout, fused operators for wider residual streams, an offload path for a table the size of a small language model, and a speculative decoding scheme that reuses index work across draft steps.

For buyers, the practical conclusion is simple. Judge a new model on what it can do, and judge its speed and price on a schedule rather than a single day. The teams that re-measure at 30 days, test at their own context lengths and keep their routing flexible will capture the improvements as they arrive, and will not write off a good model because week one looked slow.

Related articles

[![Best API Providers for Wan 3.0 Integration](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/10/integration.png)](https://deepinfra.com/blog/best-api-providers-wan-3-0-integration)[Best API Providers for Wan 3.0 Integration](https://deepinfra.com/blog/best-api-providers-wan-3-0-integration)<p>Wan3.0 is Alibaba&#8217;s all-in-one video generation model. It accepts text, images, video, audio, documents, and web pages, and it produces up to 30 seconds of 1080P video with synchronized audio. Production use raises practical questions. Video jobs run asynchronously, reference inputs can be large, and each provider exposes a different slice of the model&#8217;s features [&hellip;]</p>

[![Kimi K2.6 API Benchmarks: Latency, TPS & Cost Analysis (2026)](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/04/kimi-2.6-api-benchmark.webp)](https://deepinfra.com/blog/kimi-k2-6-api-benchmarks-latency-throughput-cost)[Kimi K2.6 API Benchmarks: Latency, TPS & Cost Analysis (2026)](https://deepinfra.com/blog/kimi-k2-6-api-benchmarks-latency-throughput-cost)<p>About Kimi K2.6 Kimi K2.6 is an open-source frontier model from Moonshot AI, released on April 20, 2026. It is a native multimodal agentic model built for long-horizon coding, autonomous execution, and swarm-based task orchestration. The model uses a Mixture-of-Experts (MoE) architecture with 1 trillion total parameters and 32 billion activated parameters per token, using [&hellip;]</p>

[![GLM-5.1 Pricing Guide: API Cost Comparison & Analysis](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/05/GLM-5.1-provider.png)](https://deepinfra.com/blog/glm-5-1-pricing-guide-provider-comparison)[GLM-5.1 Pricing Guide: API Cost Comparison & Analysis](https://deepinfra.com/blog/glm-5-1-pricing-guide-provider-comparison)<p>Provider choice for GLM-5.1 is a real economic decision. Across 10 benchmarked API providers, blended pricing runs from $0.74 to $1.70 per 1M tokens, output speed from 33.8 to 175.2 t/s, and the fastest provider is 5.2x quicker than the slowest. For teams deploying at scale, that spread determines whether this model fits a production [&hellip;]</p>

[View all](https://deepinfra.com/blog)
