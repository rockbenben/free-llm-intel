---
vendor: modular_cloud
title: Paged Attention & Prefix Caching Now Available in MAX Serve
original_title: Modular: Paged Attention & Prefix Caching Now Available in MAX Serve
url: https://www.modular.com/blog/paged-attention-prefix-caching-now-available-in-max-serve
date: 2025-02-06
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 80d058475250
---

February 6, 2025

# Paged Attention & Prefix Caching Now Available in MAX Serve

Ehsan M. Kermani

Product

We're excited to announce the availability of **Paged Attention** and **Prefix Caching** in [MAX Serve](https://docs.modular.com/max/serve), bringing state-of-the-art LLM inference optimizations. These features are available in [MAX nightly](https://github.com/modular/max/commit/b1b540c6d699cbecab0b50b47c17bf40cdbdd8fd) and the [MAX Serve nightly Docker image](https://hub.docker.com/layers/modular/max-openai-api/25.1.0.dev2025020205/images/sha256-ca59f45568b326c5aa175b8d94b8e77aa81f0604c3d07e2c6b21245fa25176a4).

## **Try them now**

To proceed, please make sure to install the `magic` CLI

Bash

curl -ssL https://magic.modular.com/ | bash

Or update it via

Bash

magic self-update

Now install the `max-pipelines` package with a single command

Bash

magic global install max-pipelines

Serve with optimizations enabled

Bash

max-pipelines serve \
    --huggingface-repo-id modularai/llama-3.1 \
    --cache-strategy paged \ 
    --enable-prefix-caching

`‍
`Check out what’s available with

Bash

max-pipelines serve --help

These features are available in [Modular's officially supported models](https://github.com/modular/max/tree/main/pipelines/python), leveraging the highly optimized [MAX Graph APIs](https://docs.modular.com/max/api/python/graph/).

## **Why do Paged Attention and Prefix Caching matter?**

[Multi-Head Attention](https://arxiv.org/pdf/1706.03762) (MHA) is a core building block of modern LLMs, but it can be computationally intensive during inference. MHA's computational complexity scales quadratically with sequence length **O(n²)** and linearly with batch size, making it particularly demanding for long sequences or large batches. [KV Cache ](https://huggingface.co/blog/not-lain/kv-caching)optimizes this by storing previously computed **Key** and **Value** projections, avoiding redundant computations during autoregressive generation. However, traditional KV caching faces memory management challenges with long sequences.

PagedAttention and Prefix Caching address these challenges.

### **Paged Attention: Memory-efficient KV Cache management**

Paged attention, introduced by vLLM, revolutionizes how we handle attention computation in LLMs with:

- **Block-based memory management**:Organizes KV cache into fixed-size memory blocks (pages)Each block typically contains 16 or 32 tokensEnables efficient memory allocation and deallocation
- **Key benefits**:**Continuous memory guarantee**: No memory fragmentation**Dynamic sequence management**: Efficiently handles variable-length sequences**Memory pooling**: Shares memory across multiple requests**GPU memory savings**: Up to 40% reduction in memory usage

Learn more about paged attention [vLLM: Easy, Fast, and Cheap LLM Serving with PagedAttention](https://arxiv.org/pdf/2309.06180)**‍**

### **Prefix Caching: Optimizing similar prompts **

**‍**Prefix caching, introduced by SGLang, provides powerful optimization for structured LLM programs:

- **Core concept**:Identifies and caches common prefix patterns in text promptsLeverages program structure for optimal cache reuseImplements intelligent cache management in the prefix trees
- **Key advantages**:**Smart prefix detection**: Automatically identifies reusable prompt segments**Program-aware caching**: Optimizes for common patterns in LLM applications**Throughput improvement**: Up to 3x speedup for structured workflows**Resource optimization**: Efficient memory usage through structured sharing

Learn more prefix caching [SGLang: Efficient Execution of Structured Language Model Programs](https://arxiv.org/pdf/2312.07104)

## What’s next?

These improvements optimize GPU memory by up to 40% and throughput up to 3x. Here are a few resources to get you started:

- ‍[**Get started with MAX**](https://docs.modular.com/max/get-started)
- Explore [**MAX Serve**](https://docs.modular.com/max/serve) and [**MAX Container**](https://docs.modular.com/max/container/)
- Check out the tutorial on how to [**deploy Llama 3 on GPU with MAX Serve**](https://docs.modular.com/max/tutorials/max-serve-local-to-cloud)
- Check out the [**relevant concept page**](https://docs.modular.com/max/serve/prefix-caching)
- Join our [**Discord**](https://discord.gg/modular) and our [**Modular forum**](https://forum.modular.com/)

We're excited to see what you'll build with MAX! Share your projects and experiences with us using **#ModularAI** on social media.

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
