---
vendor: anyscale
title: Accelerating AI: Harnessing Intel(R) Gaudi(R) 3 with Ray 2.10
original_title: 
url: https://anyscale.com/blog/accelerating-ai-harnessing-intel-gaudi-3-with-ray-2-10
date: 2024-04-09
lang: en
captured: 2026-11-08
extractor: readability-v1
status: ok
body_sha: 5303f3fd9da4
---

[Home](https://www.anyscale.com/)[Blog](https://www.anyscale.com/blog)Blog Detail

# Accelerating AI: Harnessing Intel(R) Gaudi(R) 3 with Ray 2.10

By [Ramit Hora](https://www.anyscale.com/blog?author=ramit-hora) | April 9, 2024

## Link**Are Hardware and Energy Shortages Constraining AI Growth?**

If you follow AI news, you’ve noticed a new phantom on the horizon that some believe will overwhelm power grids around the world and materially slow down AI adoption. As more companies become interested in AI, [AI workloads are growing fast and consuming too much power](https://www.morningbrew.com/daily/stories/2024/03/24/the-power-grid-has-an-ai-problem). Experts worry that this power shortage could manifest into much larger fallout– including higher energy prices, brownouts, and accelerated climate change.

As the producer of many of the most popular and widely-adopted computer chips in history, it came as no surprise when [Intel announced plans last year](https://www.cnbc.com/2023/12/14/intel-unveils-gaudi3-ai-chip-to-compete-with-nvidia-and-amd.html) to deliver the next generation of its specialized “Gaudi” family of AI Accelerators, Intel Gaudi 3, in 2024. The company continues to push forward, expanding and evolving its product line to address AI workloads from the desktop to the datacenter.

It’s worth noting that this compute resource problem didn’t appear out of nowhere. We’ve known for some time that while all of our compute-intensive workloads of the last 50 years were significant energy-consumers, the story is different with AI. Unlike other major technology waves of the last few decades like CRM, Web3, or Big Data, AI has actually *changed the requirements for underlying hardware* in a unique way. Specifically, some AI workloads like training have been shown to run better on Graphics Processing Unit (GPU) chipsets vs. traditional CPU chipsets, driving an explosion of interest in specialized AI hardware and accelerators.

## Link**Intel(R) and Anyscale - Optimizing for AI Efficiency**

At Anyscale, we’re thankful for our longstanding partnership with Intel. The core of that partnership is collaborative development, with Anyscale and Intel engineers teaming to optimize Ray and the Anyscale Platform for Intel accelerators. We’re also thankful to have Intel Capital as an investor, helping us to grow Ray adoption as well as fund AI innovation and integration.

**Today, at the **[**Intel Vision conference**](https://www.intel.com/content/www/us/en/events/on-event-series/vision.html)**, we are pleased to announce Anyscale’s latest release of Ray, Ray 2.10, adds support for Intel Gaudi 3.**

“At Intel, we’ve long believed that open source will play a critical role, not just in democratizing AI, but in driving innovation,” said said Eitan Medina, COO Intel Habana Labs. “Together, Ray 2.10 and Intel Gaudi 3 accelerator offer practitioners an optimized, open-sourced based solution for AI to address the scale, performance, cost and energy-efficiency needs of today’s growing and evolving AI workloads.”

We encourage users to [try it out for themselves](https://docs.ray.io/en/latest/serve/tutorials/intel-habana-gaudi-inference.html). Gaudi and Ray are integrated throughout the entire Ray Stack. You can:

- Spin up and manage your own Ray Clusters provisioning **Ray Core** [Task and Actors](https://docs.ray.io/en/master/ray-core/scheduling/accelerators.html#using-accelerators-in-tasks-and-actors) on a Gaudi fleet directly through Ray Core APIs.
- Tap into** Ray Serve** on Gaudi through Ray Serve APIs for a higher level experience.See an example [here](https://docs.ray.io/en/master/serve/tutorials/intel-habana-gaudi-inference.html) for how to set up single and distributed inference of Llama2 7B and 70B running on one or multiple Gaudi chips.
- Configure Gaudi infrastructure for use at the **Ray Train** layer. See [here](https://docs.ray.io/en/master/train/examples/hpu/resnet.html) for an example including setup.

Our team is attending the Intel Vision conference this week, meeting with users, friends from Intel, and industry luminaries. Co-Founder and Executive Chairman Ion Stoica will be featured on a panel, *Future of Distributed Compute: How AI will tranform systems Architecture in Next 5 years* and will present a talk named *Scaling Systems for Gen AI*. Additionally, you can see our Head of Product Marketing Subrata Charkrabarti discussing trends in open source AI at the *Infrastructure AI ISV Session*.

Stay tuned for more information on Anyscale-Intel integration in the coming months. You’ll hear more about benchmarks and other research to provide ongoing optimizations for maximum performance, scale, and efficiency for your AI workloads using Intel and Anyscale.

#### Table of contents

- [Are Hardware and Energy Shortages Constraining AI Growth?](https://www.anyscale.com/blog/accelerating-ai-harnessing-intel-gaudi-3-with-ray-2-10#are-hardware-and-energy-shortages-constraining-ai-growth?)
- [Intel(R) and Anyscale - Optimizing for AI Efficiency](https://www.anyscale.com/blog/accelerating-ai-harnessing-intel-gaudi-3-with-ray-2-10#intel(r)-and-anyscale---optimizing-for-ai-efficiency)

#### Sharing

#### Tags

#### Sign up for product updates

#### Recommended content

![Lila x SkyRL](https://images.ctfassets.net/xjan103pcp94/4UnfGrZlZyKRBMsd2jSreK/05b0b3cd8d2c9ad962448365782fb980/Lila_x_SkyRL.png?w=140)

#### How Lila Sciences and Anyscale Scaled GLM-5.3-Flash Training to 1M tokens


![kuberay-production-best-practices-field](https://images.ctfassets.net/xjan103pcp94/3uRWLXRJv2sisfuH1UpkBg/7ffa981a092ba41c591b03ef933976bf/kuberay-production-best-practices-field.png?w=140)

#### KubeRay in production: best practices from the field


![Announcing Ray support for PyTorch on Google TPUs](https://images.ctfassets.net/xjan103pcp94/5odqs3bDXHHrUGye7EReO6/12a5fb11fc7d119b1ce905d420821160/ExternalRayTorchTPUblog.png?w=140)

#### Announcing Ray support for PyTorch on Google TPUs


## Explore Anyscale today

Build, run, and scale any AI workload on Ray with a multi-cloud platform built for production AI.

[Start for Free](https://authkit.anyscale.com/?utm_source=anyscale&utm_content=exploreblock&utm_medium=website&utm_campaign=cta)[Talk to an expert](https://www.anyscale.com/book/demo?utm_source=anyscale&utm_content=exploreblock&utm_medium=website&utm_campaign=cta)
