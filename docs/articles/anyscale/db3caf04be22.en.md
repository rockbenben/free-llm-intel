---
vendor: anyscale
title: Anyscale signs definitive agreement to join Nscale
original_title: Anyscale signs definitive agreement to join Nscale
url: https://anyscale.com/blog/anyscale-signs-definitive-agreement-to-join-nscale
date: 2026-07-30
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: d2936f3961fd
---



Blog Detail

# Anyscale signs definitive agreement to join Nscale

By

Robert Nishihara

,

Philipp Moritz

,

Ion Stoica

,

Richard Liaw

and

Edward Oakes

|

July 30, 2026

What this means:

- **Doubling down on Ray.** We are expanding our investment in Ray and the open-source community. Together, we will directly optimize Ray for cutting-edge accelerator and data center architectures.
- **An open source strategy. **Under PyTorch Foundation governance, contributions from Google, NVIDIA, Microsoft, and the community are growing. Nscale plans to join the Foundation as a platinum member. Open-source is at the heart of Nscale’s strategy, as it is ours.
- **More GPU capacity. **Anyscale Platform customers will gain access to significant compute capacity from Nscale.
- **Multi-cloud flexibility. **Post-closing, the Anyscale Platform will continue to run across all major cloud providers. Portability remains core to our roadmap for both Ray and the Anyscale Platform.

## LinkThe bottleneck now spans the stack

When we created Ray at UC Berkeley and launched Anyscale, we believed AI compute needs would explode. The first bottleneck was the software for distributed computing, and we built Ray to address it.

That bet played out. Ray is now used across every major AI workload, from data preparation to training to inference, and is used to build many frontier model families, including GLM, Nemotron, Composer, and MAI.

But AI systems have grown orders of magnitude in scale and complexity. Data processing is becoming multimodal, inference-heavy, and [GPU-based](https://www.anyscale.com/blog/data-processing-becoming-gpu-workload). Reinforcement learning mixes training, inference, and simulation together in a single workload. Inference requires disaggregation, GPU memory management for extremely long context, and complex routing and failure handling for mixture-of-experts architectures.

These challenges are inseparable from the hardware. Software must account for rack and cluster topology, capacity, hardware heterogeneity, compute disaggregation, and failures at every level and in every component. Optimizing one layer at a time is no longer enough. The future requires deep, joint optimization across every layer of the software and hardware stack.

## LinkWhy Nscale

Among the neoclouds, Nscale stands out for its execution speed and vision of complete vertical integration.

Nscale focuses on more of the physical infrastructure, from land and power to data centers and accelerated compute. Its multi-gigawatt pipeline addresses one of AI’s biggest constraints and gives us compute availability and density as well as a tighter feedback loop for joint optimization. In addition, Nscale was among the first to deploy next-generation GB300 NVL72 systems at scale. Beyond physical infrastructure, Nscale has built performant platform software for large-scale inference, immediately accelerating our combined roadmap.

Similar to Anyscale, Nscale is betting on open source as a strategy and believes that the winning AI infrastructure standards will be open. They plan to join the PyTorch Foundation as a Platinum member and to invest heavily in the open source ecosystem.

Together, Anyscale and Nscale can co-design the software layer and infrastructure beneath it, something that neither company could do as effectively by optimizing its layer alone.

## LinkCommitment to open source & multi-cloud

Ray was built from day one as an open, community-driven project, and it is governed by the PyTorch Foundation alongside PyTorch and vLLM. Its value as an industry standard depends on it being fully open, neutral, and portable.

That openness is why companies across the industry invest in Ray. Over the past year, engineers from Google, NVIDIA, Microsoft, Red Hat, Alibaba, along with the broader Ray community, have improved latest-generation GPU and TPU support, topology-aware scheduling, GPU-native data processing, Kubernetes integration, and the Ray History Server. Going forward, the Anyscale + Nscale team will invest heavily in maintaining and improving Ray. We will continue to bolster the community, mentor contributors, and seek to expand project governance.

Ray has a history of co-evolution with other components of the [open AI infrastructure stack](https://www.anyscale.com/blog/ai-compute-open-source-stack-kubernetes-ray-pytorch-vllm). We are now extending that co-design deeper into the hardware layer.

Portability is a requirement. Ray was designed to support any hardware accelerator, integrate with any ML framework, and run in any environment, including your laptop, on premises, and any cloud provider. That philosophy remains unchanged across Ray and the Anyscale Platform.

## LinkLooking ahead

This is a critical period of growth, and this past quarter was our strongest yet, with over 70% quarter-over-quarter revenue growth. We are just getting started.

Together with Nscale, we will make distributed AI infrastructure simpler, more reliable, and more efficient, all while doubling down on the openness and portability that have made Ray a foundational part of the AI ecosystem.

We will share more at [Ray Summit](https://www.anyscale.com/ray-summit/2026) in San Francisco this August. Post-closing, we will also be [hiring](https://www.anyscale.com/careers) across the combined team!

#### Table of contents

- [The bottleneck now spans the stack](https://www.anyscale.com/blog/anyscale-signs-definitive-agreement-to-join-nscale#the-bottleneck-now-spans-the-stack)
- [Why Nscale](https://www.anyscale.com/blog/anyscale-signs-definitive-agreement-to-join-nscale#why-nscale)
- [Commitment to open source & multi-cloud](https://www.anyscale.com/blog/anyscale-signs-definitive-agreement-to-join-nscale#commitment-to-open-source-&-multi-cloud)
- [Looking ahead](https://www.anyscale.com/blog/anyscale-signs-definitive-agreement-to-join-nscale#looking-ahead)

#### Sharing

#### Tags

#### Sign up for product updates

#### Recommended content

#### Ray is Joining The PyTorch Foundation


#### An Open Source Stack for AI Compute: Kubernetes + Ray + PyTorch + vLLM


#### Architecting Data Pipelines for Multimodal Datasets at Scale


## Explore Anyscale today

Build, run, and scale any AI workload on Ray with a multi-cloud platform built for production AI.

Start for Free

Talk to an expert
