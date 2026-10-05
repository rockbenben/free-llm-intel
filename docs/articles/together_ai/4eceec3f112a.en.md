---
vendor: together_ai
title: What does 99.9% uptime mean for inference?
original_title: What does 99.9% uptime mean for inference?
url: https://www.together.ai/blog/99-9-uptime-for-inference
date: 2026-07-16
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 94539e7b318a
---

All blog posts

Inference

Published 7/16/2026

# What does 99.9% uptime mean for inference?

- AuthorsRyan Lucchese, Sarung Tripathi
- Table of contents[40+ Models Chosen for Production...40+ Models Chosen for Production...40+ Models Chosen for Production...](https://www.together.ai/blog/99-9-uptime-for-inference#)

**TL;DR**

- The short version: Each reliability tier maps to a specific failure domain, and each one requires its own architecture to survive it. Roughly speaking:
- 99% means your architecture can survive node-level failures: GPU hardware faults, driver crashes, thermal events. Getting there generally takes automated health checking, node draining, and fast replica replacement within a single DC.
- 99.9% means your architecture can survive a full data center failure. That usually means model weights deployed across two facilities, enough capacity on each side to absorb the full load, and live traffic routing to both, not a cold standby.
- 99.99% means your architecture can survive a regional outage. That typically calls for multi-region deployment with AZ redundancy and reserved failover capacity.

Reliability numbers are easy to publish. What’s hard is explaining what they mean: which failure domains the architecture actually covers, whether the provider controls the infrastructure at those layers, and what happens when something breaks at 3 a.m.

Together runs inference for teams like Cursor, Decagon, Cartesia, and Yutori. We’ve been paged for most of what follows; here’s what we’ve learned.

## The problem with reliability numbers

When inference goes down, someone’s product goes down with it. GPU inference fails differently from conventional services. The hardware has failure modes; CPU infrastructure doesn't, and the systems are tuned hard for performance. Hitting 1M tokens per minute per GPU at 200 TPS, or sub-50ms TTFT on voice models with custom kernels, leaves limited slack. Adding reliability to a system like that is exponentially harder with each nine.

The useful mental model is layers, and the failure modes in each one are distinct:

- **Compute:** ECC errors in VRAM (the most common thing we see; they corrupt weights silently, so requests return but outputs aren't trustworthy), thermal throttling, driver crashes, NVLink faults, NIC or CPU failures that kill the machine regardless of GPU state.
- **Network:** Switch failures, transceiver issues that degrade performance before causing full unavailability, edge device failures that take out an entire site.
- **Storage:** Outages that block weight fetching, stall rescheduling, and cascade into capacity problems.
- **Software: **Routing bugs, scheduler edge cases, deployment failures that can propagate if you're not careful.

None of these fail in isolation. A storage hiccup surfaces as a capacity problem, a thermal event shows up as degraded output quality long before any health alert fires. Getting good at this means learning to read the real signal from the misleading symptom.

## What each nine actually requires

Each tier is a different engineering problem, not just a harder version of the same one. Here’s what each one actually takes, and what we’ve built around it.

### 99%: Survive node failures

The goal is to catch a degrading node before a request reaches it. Detect fast, drain, replace. The interesting engineering problem is observability.

Passive health checks (hardware telemetry, metrics) give you visibility without capacity overhead, but miss a class of failure that only shows up under real GPU load. Active health checks catch those, but they require capacity to run. You can’t exercise a GPU that’s already serving traffic, since this creates obvious tension. Everyone wants to run near 100% utilization, and maintaining excess capacity for health checks just trades reliability for inefficiency. That path we’ve taken is getting fast at rescheduling: integrating checks with the scheduler so they run in the gaps between workloads, and making the checks themselves as quick as possible. It’s still something we tune.

The ceiling at this tier is the building itself. A thermal issue, a substation event, an edge router failure. Any of these takes a single-DC deployment down regardless of in-DC redundancy. Most providers have backup systems for this, but a redundant system that isn’t regularly tested under real conditions is like calling a player off the bench who hasn’t practiced in six weeks. The failover might be there on paper, whether it works is a different question.

### 99.9%: Survive a full DC failure

The whole facility is the failure domain here: Power, cooling, network ingress, edge networking. What surviving it requires: Weights deployed across two facilities, enough capacity on each side to absorb the full load, and routing traffic that shifts cleanly.

The architectural decision that defines whether a provider actually delivers this tier is whether they run live traffic to both facilities continuously, or maintain a cold standby. We chose continuous. Most 99.9% SLA claims implicitly promise this tier. The question is whether the architecture behind the claim is actually built for it.

This is also where infrastructure ownership matters concretely. A provider renting capacity from a hyperscaler or neocloud doesn’t own their failure domains. When something breaks at the power or cooling layer, they’re filing a ticket with whoever does. They can’t tell you what their SLA physically survives at that layer because they don’t control it. When you’re with Together AI, one ticket covers the hardware, network, storage, and software because we have chip-to-token visibility across our entire global footprint. The alternative: ticket to the provider, ticket from the provider to hyperscaler/neocloud, queue. We’ve seen what that looks like at 3 a.m.

### 99.99%: Survive a regional outage

The underlying challenge at this tier is that we’re building reliable infrastructure on inherently unreliable hardware. GPU failure rates are meaningfully higher than CPU failure rates, and every failure mode has to be accounted for. What four nines requires: multi-region deployment with AZ redundancy, and reserved capacity in the failover region sized to absorb a full regional outage. The key word here is reserved. Not “we can route traffic there” but “we have room sitting idle there right now.”

## What to ask before you commit to a provider

SLAs are a starting point. These questions get to the architecture underneath it, who owns what when things break, and how fast recovery happens. We’d expect you to ask them of us too:**‍**

- **On infrastructure ownership:**
Where are models hosted, and is it single or multi-region?Do you own your infrastructure, or are you renting capacity from a hyperscaler or third party?Who’s responsible for the data center: power, cooling, transit? Do you have physical access, or do you go through a ticket queue?If there’s an outage in one DC, how fast can you move that deployment somewhere else? Do you maintain reserve capacity for exactly this, or are you running lean?
- **On full-stack expertise:**
Do you have chip-to-token visibility across the stack, or are there gaps in observability between inference and hardware?When something breaks, does your team have direct hardware access or are dependent on a third party to diagnose and respond?How deep does your GPU hardware expertise go beyond inference software?
- **On capacity and failover:**
How is failover tested: live traffic continuously, or periodic drills?What’s your realistic RTO when a failover actually needs to execute?
- **On SLA measurement:**
Which failure domain does each SLA tier actually cover: a node, a DC, or a region?Is your SLA measured at the load balancer or at successful inference completion?Do client-side retries count against your uptime measurement?

## Our numbers defined

Vague SLA definitions are where the gap between what’s promised and what’s delivered lives. Here’s exactly what we measure and how we define each term.

| What we measure | How we define it | Our number |
| --- | --- | --- |
| Delivered uptime | % of time the inference endpoint successfully serves requests (measured at inference completion, not load balancer) | 99.9% (consistently delivered) |
| Guaranteed SLA: Single DC | Contractual SLA for a single data center deployment | 99% |
| Guaranteed SLA: Multi DC | Contractual SLA for a multi-data center deployment | 99.9% |
| Failover time | Time to shift traffic to healthy capacity after a facility fault | Seconds |
| Request volume | Inference requests served over the measurement window | 2B TPM+ |

‍

We measure at inference completion, not at the gateway. A request that reaches the load balancer but fails at the GPU is downtime in our accounting. One more thing: availability and performance are different contracts. In Provisioned Throughput, you’re paying for a GPU allocation to deliver specific TPS, not just for the endpoint to respond. A service that’s up but delivering 30% of contracted throughput isn’t meeting the deal.

## Come see the architecture

Every provider will give you a number. What matters is whether the architecture behind it is built to back it up, and whether they own the infrastructure where the guarantee has to hold.

Those are answerable questions. Ask any provider to walk through the architecture behind each SLA tier. Ask whether they own the infrastructure or sit above someone else’s. Ask whether the failover paths run under live traffic. A provider that knows their infrastructure can answer these quickly.

We can walk you through ours anytime. If you want to dig in, we’re here.

## Related articles

View All

View All
