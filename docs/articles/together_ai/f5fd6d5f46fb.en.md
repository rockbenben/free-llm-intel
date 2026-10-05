---
vendor: together_ai
title: How a global fintech scaled coding agent traffic with Dedicated Model Inference
original_title: How a global fintech scaled coding agent traffic with Dedicated Model Inference
url: https://www.together.ai/blog/global-fintech-scales-coding-agent-traffic-with-dedicated-model-inference
date: 2026-09-18
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 05fe3972dff6
---

All blog posts

Inference

Published 9/18/2026

# How a global fintech scaled coding agent traffic with Dedicated Model Inference

- AuthorsAnkit Goyal
- Table of contents[40+ Models Chosen for Production...40+ Models Chosen for Production...40+ Models Chosen for Production...](https://www.together.ai/blog/global-fintech-scales-coding-agent-traffic-with-dedicated-model-inference#)

Summary

A global fintech runs its coding assistant on GLM 5.2 through Together's Dedicated Model Inference, handling spiky, engineering-hours traffic that static capacity planning couldn't keep up with. 

With DMI, the customer's engineers scale endpoints, roll out models, and test changes themselves, no tickets, no waiting on Together. The result: infrastructure that moves as fast as the teams adopting it.

## The workload

This customer ships financial products to millions of users across dozens of markets, and growth shows no sign of slowing. Sustaining that pace is an engineering problem before anything else, and the company's engineers lean on AI coding agents to do it.

That puts inference on the critical path of how fast the company ships, rather than inside any single customer-facing feature. The workload runs on GLM-5.2, the mixture-of-experts model built for long-horizon coding and agentic work, served on Together. Traffic follows the working day: spiky, concentrated in engineering hours, and it climbs every time another team adopts agents into its workflow.

## The constraint: capacity planning couldn't keep up with adoption

### Operational control

The customer came to Together after running coding workloads with other inference providers, and first consolidated onto our earlier dedicated offering. That offering worked, but wasn't built for how this workload actually behaves. The coding-assistant traffic isn't steady; it's peak-load and relatively low-TPS, concentrated in engineering hours, with sharp bursts in concurrency and prompt size as more teams put agents into their daily workflow. That shape is precisely why concurrency, not raw throughput, was the design priority when the workload moved to GLM-5.2.

Under the earlier model, absorbing that kind of burst meant someone had to see it coming. Teams ready to move agents into their daily workflow often waited on capacity rather than provisioning it, and the customer's platform team absorbed the coordination for every one of them, filing requests and sizing clusters. The team worked to plan ahead, but planning stopped working once adoption became unpredictable in both timing and size. You can't forecast a burst that's driven by a hundred different engineering teams independently deciding to lean on their coding agent harder this week.

When capacity is provisioned to yesterday's forecast and traffic is genuinely spiky, prefill capacity and KV cache headroom get exhausted exactly during the burst, which is when it matters most, producing exactly the kind of multi-minute request queuing that agentic coding workflows can't tolerate. Fixing that after the fact, versus giving the customer's own teams the ability to see load and scale ahead of it, is the difference between a coordination problem and an infrastructure one.

## What the customer required: self-service, observability, concurrency

The customer set requirements for the Together team around autonomy, in addition to raw performance, and the workload's own shape makes clear why. The coding-assistant traffic runs at ISL p50/p90/p95 of roughly 81K/163K/178K tokens and RPS p50/p90/p95 of 3/6/7, a peak-load, relatively-low-TPS pattern where bursts in concurrency matter far more than raw tokens-per-second. That's the backdrop for what the customer asked of Together:

- **Self-service provisioning**: An engineering team should be able to stand up its own endpoint and put traffic on it without filing a request or waiting on the platform group, a shift from the earlier model, where every new team's capacity request went through Together and the customer's platform team in turn.
- **Observability its own teams could act on**: Usage and performance data available programmatically, so capacity decisions could sit with the teams making them, not get routed through a support queue when something like cache hit rate degrades.
- **Throughput and fast scaling under concentrated load**: Sustained performance during working-hours peaks, not benchmark conditions, running dozens of B200s across a multi-replica configuration at 256K context, sized specifically to hold concurrency headroom.
- **Model fluidity**: Room to swap models as the frontier advances, without renegotiation, demonstrated in practice by the move from GLM 5.1 to GLM 5.2 on the same account, plus a live tuning pass on cache and load-balancing parameters done as a config update, not a redeployment.

## **What shipped: full endpoint control, a metrics API, and model fluidity**

### Endpoint configuration through the API, UI, or CLI

Dedicated Model Inference exposes the full endpoint lifecycle: creation, sizing, scaling policy, and configuration changes. The customer's infrastructure team used exactly this when a migration reshaped their GLM 5.2 endpoint, shifting toward fewer, larger replicas, same total footprint, different ratio of replica count to chips per replica. When that re-shape hit near-100% prefill capacity a few days later, with requests queuing one to three minutes and decode throughput collapsing to roughly 5 tokens per second, the fix wasn't a new deployment or a ticket back to Together. It was a live configuration change: restoring the tuned cache-session-aware routing policy in place of DMI's default cache-aware-by-hash policy, and widening the max-inflight-per-worker threshold. All of it was pushed same day with zero downtime.

### Metrics API

Programmatic access to endpoint usage and performance data is how the root cause was found. Together API Support traced a single 192-second slow request end-to-end through the metrics data and found it wasn't compute-bound, and had spent almost the entire span queued behind a 2.3M-token pending-prefill backlog from other requests, not its own 250K-token prompt. That's the specific value of self-serve observability: the customer's own team diagnosed a queuing problem, not a capacity problem, without waiting on Together to pull logs.

### Fast access to a rich library of models

Dedicated Model Inference gives users self-serve access to frontier open-source models, as well as performance-aware configurations to help customers opt for any combination of TTFT, TPS, TPM, and other metrics. The customer's team works closely with Together's forward-deployed engineers to continuously optimize these configurations as its coding agent use evolves.

This showed up as the GLM 5.1 to GLM 5.2 and context-length iterations transitioning on the same account and endpoint pattern, with no renegotiation involved. It also showed up as a deliberate configuration trade-off the customer's team made themselves: given their traffic profile, they evaluated a 1M-context configuration and turned it down, because doubling context to 1M would have cut the concurrency headroom their peak-load, low-TPS workload actually depends on. The team chose to stay at 256K/512K instead.

## Timeline: from early load tests to a production endpoint at scale

The coding-assistant relationship predates the GLM 5.2 production endpoint by several months. Together's Solutions Architecture team had already built dedicated load-testing infrastructure modeling the customer's actual usage pattern, initially validated against an earlier GLM release.

That groundwork carried straight into GLM 5.1. Early on, the customer's project lead asked over a weekend for a checkbox-style concurrency test of GLM 5.1 across 8 to 16 B200s, explicitly for the coding use case and distinct from earlier tests that had been consumer-facing and latency-focused. Together turned the test endpoint around the same day, and GLM 5.1 passed the bar and moved to production: two dedicated endpoints, split by accessibility, running as the customer's internal developer-facing coding assistant.

- **The pivot to GLM 5.2:** The customer moved the coding workload to GLM 5.2, and the production endpoint began running it at 256K context on 56 B200s (14 replicas by 4 B200s), prioritizing concurrency over raw throughput to match the customer's peak-load, relatively-low-TPS traffic shape.
- **Self-serve migration to DMI:** Together's CX team migrated the customer's GLM 5.2 endpoint onto the DMI self-serve platform, handing the customer control over scaling, custom-weight rollouts, and blue/green testing, with Together's SA/FDE team standing by for any performance tuning.

## Results

### Time to change a config or ship a model update

Before DMI, changing a config or adding capacity meant routing through Together: filing a request, sizing a cluster, waiting for a redeploy. Every engineering team that wanted to adopt agents added to that same queue, so the customer's platform team ended up coordinating on behalf of the whole organization.

On DMI, that entire flow moved in-house:

- **Scaling: **the customer adjusts capacity directly, no ticket to Together.
- **Custom-weight rollouts: **new model versions go live without a redeployment cycle.
- **Blue/green testing: **the customer validates changes against production traffic on its own timeline.

## What's next: a second workload and region

The deployment stopped being a single endpoint and started being a surface for innovation. That pattern is now repeating as a pipeline, not a one-off. The customer's team is already scoping a dedicated GLM 5.1 node in a new region, sized against a real production workload. It's a different shape of workload than the original coding assistant: a chat-style customer-support NLP workload rather than long-horizon agentic coding, landing on the same infrastructure and provisioning pattern.

‍

‍

‍

## Related articles

View All

View All
