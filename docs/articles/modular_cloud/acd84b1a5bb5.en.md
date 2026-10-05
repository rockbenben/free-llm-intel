---
vendor: modular_cloud
title: Day Zero Launch: Fastest Performance for Gemma 4 on NVIDIA and AMD
original_title: Modular: Day Zero Launch: Fastest Performance for Gemma 4 on NVIDIA and AMD
url: https://www.modular.com/blog/day-zero-launch-fastest-performance-for-gemma-4-on-nvidia-and-amd
date: 2026-04-02
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: eb7329714a1b
---

April 2, 2026

# Day Zero Launch: Fastest Performance for Gemma 4 on NVIDIA and AMD

Modular Team

Product

Today, Google DeepMind released the Gemma 4 family of models, the latest state-of-the-art open models from the same team behind Google Gemini models. We’re thrilled to be day zero launch partners and invite developers and enterprises to try out Gemma 4’s multimodal capabilities on [Modular Cloud](https://console.modular.com/signup?utm_campaign=day0&utm_source=blog) with state of the art performance on both NVIDIA and AMD.

Our benchmarks show 15% higher throughput when compared to vLLM on NVIDIA B200.

## Meet the Gemma 4 family

Modular is hosting all variants of Google’s new [Gemma 4 family of models](https://huggingface.co/collections/google/gemma-4). All are natively multimodal, supporting text, images, and video with dynamic resolution and aspect ratio.

**Gemma 4 31B** is a 31-billion-parameter dense model featuring a redesigned architecture that improves both efficiency and long-context quality. With a 256K context window, it's built for demanding tasks that require deep reasoning across large inputs.

**Gemma 4 26B A4B** is a Mixture-of-Experts (MoE)model with 26B total parameters but only 4B activated per forward pass, meaning you get the quality of a much larger model at a fraction of the compute cost. It also supports a 256K context window and is designed to fit the memory footprint of high-end servers.

Whether you're running OCR, video and image understanding, or 256K-context workflows, the same MAX-powered engine that handles your initial tests runs your production Modular Cloud endpoint, so there are no surprises when you scale.

## High performance Gemma 4 on NVIDIA and AMD

Modular Cloud runs on [MAX](https://www.modular.com/open-source/max), our inference framework that unifies GPU kernels, graph compilation, and high-performance serving in a single hardware-agnostic platform. Modular allows teams to move fast: we optimized Gemma 4 to state-of-the-art across NVIDIA and AMD and brought up a production-ready endpoint on Modular Cloud within a few days.

Performance is a given in MAX, and on NVIDIA B200, **Gemma 4 on MAX is 15% faster than vLLM ****while experiencing no accuracy degradation. ** Stay tuned for more details coming soon.

| **Accuracy ** | **MAX (B200)** | **vLLM* (B200)** | MAX (MI355) |
| --- | --- | --- | --- |
| MMLU Pro | 84.72% | (not measured) | **84.94%** |
| GSM8K Llama COT | **95.94%** | 94.69% | 94.37% |
| ChartQA | **84.69%** | 84.38% | 84.38% |

**Benchmarked using the officially provided vllm-0.18.2rc1.dev7*3

## Try Gemma 4 on Modular Cloud Today

Gemma 4 is one of the most capable open models available - but capability only matters if you can ship it. Modular Cloud gives you a straight line from first API call to production endpoint, optimized across NVIDIA and AMD hardware, with no infrastructure archaeology required.

With Modular Cloud, you can:

- **Transition from playground to production without switching stacks** - The same MAX-powered engine that runs your tests runs your production endpoint.
- **Choose the right GPU for your workload - **Run on NVIDIA or AMD, whichever fits your cost and throughput requirements. The stack picks the right configuration and batch sizing so you're not guessing.
- **Ship multimodal and long-context features faster - **OCR, video + image understanding, and 256K-context workflows are supported out of the box.

[**Start building on Modular Cloud →**](https://console.modular.com/signup?utm_campaign=day0blog)

Or, try it for free yourself[ with MAX.](https://docs.modular.com/max/get-started/)

*Interested in running MAX on your own infrastructure or in your own cloud? *[*Book a demo*](https://www.modular.com/request-demo)* and we'll walk through a deployment built around your models, hardware, and performance goals.*

Discover what Modular can do for you

Request a demo

## Read more from Modular

View all blogs

Modular 26.5: Mojo 1.0 is here!

August 11, 2026

Modular 26.4: SOTA MoE Serving, Model Bringup via Agent Skills, Mojo 1.0 Beta 2 and More

June 18, 2026

Translating to Mojo via AI Agents

May 13, 2026

Build the future of AI with Modular

Get started - FREE

View Editions

- ![Person with blonde hair using a laptop with an Apple logo.](https://cdn.prod.website-files.com/68c9c3107effc2ea46e1a81f/68cc733ff9050921bab7782c_emoji-dev.png)Sign up todaySignup to our Cloud Platform today to get started easily.[Sign Up](https://docs.modular.com/max/get-started)
- ![Magnifying glass emoji with black handle and round clear lens.](https://cdn.prod.website-files.com/68c9c3107effc2ea46e1a81f/68cc733fb111718bbd49ca31_emoji-zoom.png)Browse open modelsBrowse our model catalog, or deploy your own custom model[Browse models](https://www.modular.com/models)

## Sign up for our newsletter

Get all our latest news, announcements and updates delivered directly to your inbox. Unsubscribe at anytime.

Thanks for signing up to our newsletter! 🚀

Thank you,

Modular Sales Team

Oops! Something went wrong while submitting the form.
