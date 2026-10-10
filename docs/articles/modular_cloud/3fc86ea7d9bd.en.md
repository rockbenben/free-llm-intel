---
vendor: modular_cloud
title: Modular + AMD: Unleashing AI performance on AMD GPUs
original_title: Modular: Modular + AMD: Unleashing AI performance on AMD GPUs
url: https://www.modular.com/blog/modular-x-amd-unleashing-ai-performance-on-amd-gpus
date: 2025-06-10
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 1e4744e6ca33
---

June 10, 2025

# Modular + AMD: Unleashing AI performance on AMD GPUs

Modular Team

Company

[Modular is excited to announce a partnership](https://youtube.com/live/tBlNAIlMou8?feature=share) with [Advanced Micro Devices, Inc](https://www.amd.com/en.html). (AMD), one of the world’s leading AI semiconductor companies. Together, we’re bringing the benefits of the [Modular Platform](https://docs.modular.com/) to AMD GPUs, delivering infrastructure solutions optimized for today and tomorrow’s most demanding AI workloads.

> “We're truly in a golden age of AI, and at AMD we're proud to deliver world-class compute for the next generation of large-scale inference and training workloads… We also know that great hardware alone is not enough. We've invested deeply in open software with ROCm, empowering developers and researchers with the tools they need to build, optimize, and scale AI systems on AMD. This is why we are excited to partner with Modular… and we’re thrilled that we can empower developers and researchers to build the future of AI. “ – Vamsi Boppana, Senior Vice President, AI - AMD

This partnership marks the general availability of the Modular Platform across AMD's GPU portfolio, a significant milestone in heterogeneous AI computing infrastructure. Effective immediately, developers can deploy the Modular Platform on AMD's flagship datacenter accelerators, including the MI300 and MI325 series.

The Modular Platform, powered by the MAX inference server and the [Mojo programming language](https://www.modular.com/mojo), delivers unprecedented performance optimization for AMD hardware. In rigorous benchmarking against existing open source AI infrastructure stacks, we demonstrate superior inference efficiency, achieving up to 53% better throughput on prefill-heavy, `BF16` workloads on Llama 3.1, Gemma 3, Mistral, and other state-of-the-art language models—[all from a single container that scales across NVIDIA and AMD GPUs](https://hub.docker.com/r/modular/max-full).

For decode-heavy `BF16` workloads, we demonstrate up to 32% better throughput performance against existing AI infrastructure stacks.

These breakthroughs are made possible by Modular Platform, the industry’s first truly hardware-agnostic AI infrastructure stack—delivering a unified platform that enables seamless deployment across diverse hardware architectures without modifying a single line of code.


> Developers can now build portable, high-performance GenAI deployments that run on any platform.


Enterprises finally gain real freedom to choose the best hardware for their workloads—optimizing for both performance and total cost of ownership. Compared to vLLM on NVIDIA H200, MAX models on AMD MI325 match or exceed throughput parity for ShareGPT.

This optionality is made possible by Mojo 🔥, a Python family language designed from the ground up to easily unlock the best performance on a variety of hardware. Unlike most programming languages that are primarily targeted for CPUs, Mojo is built for the new era of heterogeneous computing across GPUs and other accelerators. Thanks to features like strong static typing, compile time meta programming, and seamless hardware dispatch, Mojo kernels are faster to write, easier to maintain, and portable across the latest hardware accelerators. For example, the Mojo kernel library implementation of `matmul` for `BF16` outperforms equivalent hand-tuned kernels on MI300X, while maintaining portability to other hardware.

Mojo Matmul GFLOPS performance on MI300X using BF16

Lastly, we’re taking hardware choice even further with today’s [preview launch of Mammoth](https://www.modular.com/blog/introducing-mammoth-enterprise-scale-genai-deployments-made-simple)—our Kubernetes-native orchestrator purpose-built for large-scale, architecture-agnostic inference. Mammoth delivers exceptional performance and operational simplicity across clusters of thousands of heterogeneous GPUs, [making AI infrastructure scalable, efficient, and future-proof](https://docs.modular.com/mammoth).

To harness the full power of the Modular Platform on AMD GPUs, [download our nightly](https://docs.modular.com/max/get-started) builds or pull our [Docker container](https://hub.docker.com/r/modular/max-amd). To help you get started today, Modular has partnered with [TensorWave](https://tensorwave.com) to offer complimentary access to high-performance AMD datacenter GPUs—just visit [modular.com/tensorwave](http://modular.com/tensorwave). We can’t wait to see what you build!

## Read more from Modular

View all blogs

Modular 26.6: Open compiler contributions, audio generation, and expanded model support

September 17, 2026

Mojo🔥 is now open source!

August 18, 2026

ModCon 2026: Open source, open cloud, open silicon

August 18, 2026

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
