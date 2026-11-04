---
vendor: anyscale
title: Ray is Joining The PyTorch Foundation
original_title: Ray is Joining The PyTorch Foundation
url: https://anyscale.com/blog/ray-by-anyscale-joins-pytorch-foundation
date: 2025-10-22
lang: en
captured: 2026-11-05
extractor: readability-v1
status: ok
body_sha: 854a2211f4b0
---

[Home](https://www.anyscale.com/)[Blog](https://www.anyscale.com/blog)Blog Detail

# Ray is Joining The PyTorch Foundation

By [Robert Nishihara](https://www.anyscale.com/blog?author=robert-nishihara), [Philipp Moritz](https://www.anyscale.com/blog?author=philipp-moritz) and [Ion Stoica](https://www.anyscale.com/blog?author=ion-stoica) | October 22, 2025

Today, [Ray](https://github.com/ray-project/ray/) is joining the PyTorch Foundation, which is part of the Linux Foundation. The Linux Foundation is home to foundational infrastructure projects including Kubernetes, PyTorch, and vLLM.

Downloads of Ray have grown nearly 10x over the past year.

Today, Ray drives billions of dollars of annual compute consumption and powers AI workloads across the globe, with [Ray Summit 2025](https://www.anyscale.com/ray-summit/2025) featuring use cases from companies across the board including

- AI startups: xAI, Thinking Machines, Perplexity
- Established tech companies: Netflix, ByteDance, Apple, Tencent, Alibaba
- Major enterprises: JPMorgan, BMW, Bridgewater, Workday

![Ray weekly downloads](https://images.ctfassets.net/xjan103pcp94/3taOf5VUlDYr6PMyZZcLj2/0f72b4839582e4ca757e9f9330c46f87/image_23.png)Ray weekly downloads

Ray weekly downloads

## Link**Early Days**

We started Ray at UC Berkeley because, as graduate students working on AI, we needed to scale our algorithms across CPU and GPU clusters, and we found ourselves spending most of our time building infrastructure to solve the distributed systems challenges of scaling (reliability, cost, performance).

From the start, we were interested in producing useful open-source software. And we were inspired by the previous generation of students in our lab who had created [Apache Spark](https://github.com/apache/spark).

We started Anyscale in 2019 to develop and commercialize Ray. However, at the time, the need for scale existed only among the earliest of adopters. Ant Group was the first major production user of Ray. Uber and Pinterest were among the next. But the reality was that, at the time, the vast majority of companies didn’t need to scale compute for AI.

All of that changed with the advent of generative AI, LLMs, and today’s reasoning models. Now in 2025, the need for scale is clear. And the software engineering challenges around scaling AI workloads are far greater today than they were when we started Ray.

## Link**Full Circle**

In some ways, we have come full circle. From the start, we envisioned Ray as a general purpose framework (at its core, Ray is an actor framework), but the very first use case we pursued was reinforcement learning. We used RL to showcase Ray’s advantages in the [original Ray paper](https://arxiv.org/abs/1712.05889). We focused on reinforcement learning because we ourselves were working on RL ([TRPO](https://arxiv.org/abs/1502.05477), [RLlib](https://arxiv.org/abs/1712.09381)). A huge fraction of the AI community was working on playing Atari games and learning motor control in physics simulators like Mujoco. However, that wave of excitement around reinforcement learning was relatively siloed and didn’t translate into widespread practical application.

Today, reinforcement learning has made a major comeback through its success in building reasoning models and shaping agentic behavior. And today, nearly every [open-source RL framework for post-training LLMs](https://www.anyscale.com/blog/open-source-rl-libraries-for-llms) is built on top of Ray.

## Link**PyTorch Foundation**

When it comes to infrastructure software, open source wins. As the [software compute stack for AI](https://www.anyscale.com/blog/ai-compute-open-source-stack-kubernetes-ray-pytorch-vllm) emerges, every layer of the stack will have an open-source standard. PyTorch is the dominant deep learning framework. Kubernetes is the dominant container orchestrator. We are building Ray to serve as the open-source distributed compute engine.

Ray adoption has exploded over the last year. Ray is joining the PyTorch Foundation now because we are growing a global community of contributors. The need for scale is only growing, and our intention is to invest heavily and to build the open-source community around Ray to meet the rapidly evolving needs of AI.

## Link**Join the Ray Community**

This is just the beginning.

- Meet the community at[ Ray Summit 2025](https://www.anyscale.com/ray-summit/2025?utm_source=blog&utm_medium=web&utm_campaign=pytorch-donation&utm_content=ray-summit), November 3–5 in San Francisco
- Sign up for the new[ Intro to Ray](https://courses.anyscale.com/bundles/introduction-to-ray?__hstc=143905642.0ab17989225ebf831fe500ef059ee2b8.1753208986630.1759787843262.1760983194684.22&__hssc=143905642.15.1760983194684&__hsfp=1062460436&_gl=1*rpuc7f*_gcl_au*MTQ1OTU4MDEwOS4xNzYwOTgzMTg5LjE5NDQyMjQ0NzguMTc2MDk4MzgyOS4xNzYwOTgzODI4?utm_source=blog&utm_medium=web&utm_campaign=pytorch-donation&utm_content=intro-to-ray-course) course
- Contribute to Ray on[ GitHub](https://github.com/ray-project/ray)
- Join the Ray[ Slack](https://www.ray.io/join-slack?utm_source=blog&utm_medium=web&utm_campaign=pytorch-donation&utm_content=slack)

Together, we’ll continue shaping the future of AI infrastructure — open and community-driven.

#### Table of contents

- [Early Days](https://www.anyscale.com/blog/ray-by-anyscale-joins-pytorch-foundation#early-days)
- [Full Circle](https://www.anyscale.com/blog/ray-by-anyscale-joins-pytorch-foundation#full-circle)
- [PyTorch Foundation](https://www.anyscale.com/blog/ray-by-anyscale-joins-pytorch-foundation#pytorch-foundation)
- [Join the Ray Community](https://www.anyscale.com/blog/ray-by-anyscale-joins-pytorch-foundation#join-the-ray-community)

#### Sharing

#### Tags

#### Sign up for product updates

#### Recommended content

![kuberay-production-best-practices-field](https://images.ctfassets.net/xjan103pcp94/3uRWLXRJv2sisfuH1UpkBg/7ffa981a092ba41c591b03ef933976bf/kuberay-production-best-practices-field.png?w=140)

#### KubeRay in production: best practices from the field


![Announcing Ray support for PyTorch on Google TPUs](https://images.ctfassets.net/xjan103pcp94/5odqs3bDXHHrUGye7EReO6/12a5fb11fc7d119b1ce905d420821160/ExternalRayTorchTPUblog.png?w=140)

#### Announcing Ray support for PyTorch on Google TPUs


![Running Ray at scale on Kubernetes with KubeRay](https://images.ctfassets.net/xjan103pcp94/6rF9ECqCFk5OjE7RftoynJ/e003a1df2ce07a3177dbdd4d1fe76473/Running_Ray_at_scale_on_Kubernetes_with_KubeRay.png?w=140)

#### Running Ray at scale on Kubernetes with KubeRay


## Explore Anyscale today

Build, run, and scale any AI workload on Ray with a multi-cloud platform built for production AI.

[Start for Free](https://authkit.anyscale.com/?utm_source=anyscale&utm_content=exploreblock&utm_medium=website&utm_campaign=cta)[Talk to an expert](https://www.anyscale.com/book/demo?utm_source=anyscale&utm_content=exploreblock&utm_medium=website&utm_campaign=cta)
