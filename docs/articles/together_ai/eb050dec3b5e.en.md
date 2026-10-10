---
vendor: together_ai
title: Cache-aware prefill–decode disaggregation (CPD) for up to 40% faster long-context LLM serving
original_title: Cache-aware prefill–decode disaggregation (CPD) for up to 40% faster long-context LLM serving
url: https://www.together.ai/blog/cache-aware-disaggregated-inference
date: 2026-03-04
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 07eb701fdcd7
---

All blog posts


Published 3/4/2026

# Cache-aware prefill–decode disaggregation (CPD) for up to 40% faster long-context LLM serving

- AuthorsJiejing Zhang, Yubo Wang, Yinghui Liu, Mourya Vangala Srinivasa, Chenxi Li, Jue Wang, Yineng Zhang, Shuaiwen Leon Song, Ce Zhang
- Table of contents[40+ Models Chosen for Production...40+ Models Chosen for Production...40+ Models Chosen for Production...](https://www.together.ai/blog/cache-aware-disaggregated-inference#)

Summary

Serving long prompts doesn’t have to mean slow responses. At Together AI, we built cache-aware prefill–decode disaggregation (CPD), a serving architecture that purposely separates cold and warm workloads by cache hit rate, resulting in fast context reuse. By isolating heavy prefills and leveraging distributed KV cache, CPD delivers up to 40% higher sustainable throughput and significantly lower time-to-first-token (TTFT) for long-context inference — especially under mixed, real-world traffic.

Today's AI native applications are pushing context lengths to new limits. From multi-turn conversations and coding copilots to agent memory and retrieval-augmented systems, long prompts are becoming the norm. But serving these large contexts efficiently remains a challenge: **TTFT rises and becomes more variable**. Inference performance is increasingly shaped not just by model compute, but by how efficiently systems handle shared context. In real-world workloads, many requests are not entirely new. Some contain large portions of context that have been seen before — e.g., shared system prompts, conversation history, or common documents. We refer to these as **warm requests**. Others introduce mostly new context and require full computation — these are **cold requests**.

Recent advances like prefix caching and prefill–decode disaggregation (PD) have already improved long-context serving. Prefix caching reduces redundant work by reusing previously computed KV cache of the prompt prefixes, while PD separates the compute-heavy prefill stage from latency-sensitive decoding to reduce interference between them. Together with other associated techniques such as chunk prefill, sequence/context parallelism, etc., they collectively help lower overhead and improve hardware utilization.

However, real-world workloads under very high load poses new challenges beyond the common serving scenarios. Consider a system where some concurrent users submit large, entirely new prompts over 100K tokens while others continue with multi-turn conversations that mostly reuse earlier context. PD ensures decoding is not blocked by prefill, but all prefills — both cold and warm — still share the same prefill capacity. The large cold prompts occupy those resources for seconds at a time, and warm requests that could have been served quickly through cache reuse end up waiting in the same queue. As a result, TTFT increases not because these requests need heavy computation, but because they are stuck behind the requests that do.

To address this gap, we built a cache-aware disaggregation serving architecture, which handles warm and cold requests with separate compute resources. By identifying how much reusable context a request contains, the system can make smarter scheduling decisions — reducing unnecessary waiting and routing work more effectively across compute resources. Instead of letting expensive cold prefills dominate shared capacity, the system paves fast paths for warm requests while still processing new context efficiently.

As a result, the cache-aware disaggregation design enables the system to scale more gracefully under load. As shown in Figure 1, under a tail-sensitive SLA, it consistently sustains higher achievable throughput than conventional baselines. In our evaluation, CPD improves sustainable QPS by up to **35–40%** over existing disaggregated designs, while maintaining tighter tail latency bounds even in the presence of large cold prompts.

Figure 1.

Maximum achievable QPS under latency SLOs.

## How CPD works

We propose cache-aware prefill–decode disaggregation (CPD), which extends standard prefill–decode disaggregated serving with **cache-aware routing** and a **shared KV-cache hierarchy**. The key idea is simple: *don't let expensive "cold" prefills block the fast path for reusable context*.

The system separates inference into three roles:

- **Pre-Prefill nodes**: handle low-reuse (cold) prompts, compute new context, and write KV cache into a distributed cache.
- **Prefill nodes**: prioritize high-reuse (warm) requests, reading KV blocks from cache instead of recomputing prefixes.
- **Decode nodes**: remain latency-focused and isolated from prefill interference.

Prefill and decode are already disaggregated, but CPD adds a dedicated **pre-prefill tier** that handles requests with little or no cache reuse. These nodes compute large new contexts and write their KV cache into a distributed cache. Meanwhile, normal prefill nodes focus on requests that can reuse existing state, reading KV blocks from the cache instead of recomputing them. Decode nodes remain isolated and latency-focused.

Under the hood, CPD relies on a **three-level KV-cache hierarchy**, as depicted in Figure 2. The fastest layer lives in GPU memory, followed by host DRAM, and a cluster-wide distributed cache connected via RDMA. When a cold request is processed by a pre-prefill node, its KV state is written to the distributed cache. Subsequent similar requests can fetch this state in bulk at high bandwidth, turning what would have been seconds of compute into hundreds of milliseconds of transfer and light recomputation. Over time, frequently accessed contexts naturally move closer to the GPU, further shrinking latency.

Figure 2. System overview

The router ties this together. For each request, it estimates how much of the prompt can be served from cache. Requests with low reuse are steered to pre-prefill nodes, while high-reuse requests go directly to normal prefill nodes. This **workload separation** prevents large cold prefills from saturating shared compute, while still allowing the system to ingest new context and continuously warm the cache. The result is a serving stack that keeps fast paths fast, even under mixed and bursty long-context workloads.

## What happens across repeated requests

CPD's benefits become clear when the same or similar long context appears multiple times — which is common in copilots, agents, and multi-turn chat scenarios. Each request moves the workload further away from heavy compute bound and to prefix cache reuse.

Figure 3. The 3 request pattern.

#### **Request 1 — Cold (bootstrap)**

The first time a large context appears, it is classified as **cold**. The router sends it to a **pre-prefill node**, which performs the full prefill computation. At the same time, the generated KV cache is written into the distributed cache.

This request pays the full compute cost, but it *primes the system* by turning the new context into a reusable state.

#### **Request 2 — Warm (distributed cache reuse)**

When the same context appears again, the router now identifies it as **warm**. Instead of recomputing the prefix, a normal prefill node fetches KV blocks from the distributed cache via RDMA and loads them into GPU memory.

Now seconds of compute are replaced by high-bandwidth transfer and light processing. Latency drops dramatically while GPU compute pressure also decreases.

#### **Request 3 — Warm (local reuse)**

If the context remains active on the same node, its KV state may already reside in GPU or host memory. No distributed cache transfer is needed — the system reuses local cache directly.

At this point, prefill becomes minimal overhead, and latency shrinks even further. The same 100K-token context that originally required seconds of compute can now be served in a few hundred milliseconds. Moreover, CPD does more than reuse prefixes — it isolates heavy compute from reuse-driven traffic, allowing the system to scale long-context inference without letting cold workloads dominate shared resources.

## Evaluation

We evaluate CPD along two complementary dimensions that are critical for long-context serving systems under real-world load:

- **Latency and throughput scaling under increasing load** — how TTFT (p50 and p90) and per-GPU throughput evolve as target QPS increases.
- **Effective serving capacity under contention** — how much sustainable QPS per GPU the system can maintain before prefill-side saturation leads to rapid latency inflation.

We compare a conventional PD-based deployment against CPD, focusing on how cache-aware disaggregation reshapes saturation behavior and latency under mixed warm and cold workloads:

- **2P1D/2P2D (baseline)**: Two prefill nodes and one or two decode node, using standard PD routing where all requests share the same prefill capacity.
- **CPD-1D/2D**: A cache-aware pipeline consisting of a dedicated pre-prefill tier, one normal prefill tier, and one or two decode nodes, coordinated by a CPD-aware router that distinguishes warm and cold requests.

All experiments are conducted on NVIDIA **B200 GPUs**. Each prefill stage uses tensor parallelism across 4 B200 GPUs per node, while decode stages use data parallelism with attention sharding across 4 B200 GPUs. We cap the maximum number of inflight requests at 24 to reflect realistic admission control and to avoid unbounded tail amplification.

For each target QPS, the system ramps up traffic over 30 seconds and then sustains steady-state load for 600 seconds. QPS is swept from 0.4 to 1.6 in increments of 0.2 to capture system behavior from light load through saturation.

### Workload configuration

To reflect realistic long-context inference workloads, we design a benchmark based on a coding agent scenario with large shared context and multi-turn interactions. This workload mirrors AI-assisted software development settings where an agent maintains substantial codebase context across multiple turns — reading files, analyzing dependencies, implementing changes, and iterating on fixes. Using synthetic data with a realistic mix of warm and cold prefill requests that stress CPD's scheduling decisions.

### Results

Together, Figure 4 illustrates how CPD reshapes both latency scaling behavior and serving capacity as system load increases.

Figure 4.

Performance comparison between 2P1D/2P2D and CPD under increasing target QPS.

#### Saturation behavior

As target QPS increases, the two systems begin to diverge once prefill capacity becomes the dominant bottleneck. The 2P1D baseline reaches saturation earlier, with achieved QPS flattening around **0.75–0.8 QPS per GPU**, after which queueing delays grow rapidly. In contrast, CPD continues to scale to approximately **1.1–1.15 QPS per GPU** under the same workload, representing a **~40% increase in sustainable throughput** before entering saturation.

This rightward shift of the saturation point is consistent with the throughput curves in Figure 4 (bottom-left), where CPD maintains higher effective prefill throughput as load increases. By separating cold prefills from cache-backed warm requests, CPD prevents long-running cold prompts from monopolizing shared prefill capacity, allowing the system to operate efficiently at higher offered load.

#### Latency under load

At light load, median TTFT (p50) is comparable between 2P1D and CPD, indicating that CPD does not introduce additional overhead in the uncongested regime. As QPS increases toward the baseline's saturation point, however, the behavior diverges sharply.

For 2P1D, TTFT p50 rises steeply beyond 1 second and quickly enters multi-second territory, reflecting queueing behind large cold prefills. CPD exhibits a significantly more gradual increase: even at target QPS levels where the baseline is already saturated, CPD maintains **sub-second to low-second median TTFT**, as shown in Figure 4 (top-left). This improvement directly follows from workload isolation — warm requests that reuse cached context are no longer forced to wait behind expensive cold-prefill execution.

Tail latency (TTFT p90) shows a more nuanced pattern. Under moderate load, both systems exhibit similar p90 behavior. As load increases further, p90 TTFT rises for both designs, but CPD consistently remains below or comparable to the baseline across the evaluated range (Figure 4, top-right). Importantly, CPD achieves substantial gains in median latency without introducing disproportionate tail amplification. While bursts of cold traffic can still increase queueing within the pre-prefill tier, their impact remains largely contained, preserving predictable tail behavior.

#### Throughput efficiency

The throughput breakdown in Figure 4 highlights the underlying cause of these improvements. CPD sustains higher prefill throughput per GPU at elevated QPS, whereas the baseline's prefill throughput plateaus and then degrades as queueing intensifies. Generation throughput remains broadly comparable between the two systems, indicating that the observed performance differences are primarily driven by more efficient prefill scheduling rather than decode-side optimizations.

#### Key result and discussion

Figure 4 shows that CPD shifts the operating point of long-context serving under mixed warm and cold workloads. Increasing decode capacity from 1D to 2D improves overall throughput and delays saturation for both baseline and CPD configurations, confirming that decode-side parallelism contributes to higher serving capacity.

Importantly, CPD continues to deliver consistent improvements even when decode capacity is scaled. Under both 1D and 2D settings, CPD sustains higher effective QPS per GPU and exhibits a more gradual increase in median TTFT compared to the corresponding baseline. In addition, CPD maintains comparable or higher decode throughput, indicating that its benefits are not limited to prefill isolation but extend to more efficient end-to-end pipeline utilization.

These improvements are driven not by raw model execution speed, but by cache-aware isolation on the prefill path. By preventing long-running cold prefills from blocking cache-backed warm requests, CPD preserves a fast path for reuse even under high load. This highlights that as context windows grow, system-level scheduling and reuse-aware design become first-order factors in inference performance, alongside model and hardware efficiency.

## Related articles

View All

View All
