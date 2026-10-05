---
vendor: modular_cloud
title: Modverse #49: Modular Platform 25.4, Modular 🤝 AMD, and Modular Hack Weekend
original_title: Modular: Modverse #49: Modular Platform 25.4, Modular 🤝 AMD, and Modular Hack Weekend
url: https://www.modular.com/blog/modverse-49
date: 2025-07-09
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 268d6566e138
---

July 9, 2025

# Modverse #49: Modular Platform 25.4, Modular 🤝 AMD, and Modular Hack Weekend

Caroline Frasca

Community

Between a global hackathon, a major release, and standout community projects, last month was full of progress across the Modular ecosystem!

[Modular Platform 25.4 launched on June 18th](https://www.modular.com/blog/modular-25-4-one-container-amd-and-nvidia-gpus-no-lock-in?utm_source=modverse&utm_campaign=community), alongside the announcement of our official partnership with AMD, bringing full support for AMD Instinct™ MI300X and MI325X GPUs. You can now deploy the same container across both AMD and NVIDIA hardware with no code changes, no vendor lock-in, and no additional configuration!

Highlights from 25.4 include up to 53% better throughput on prefill-heavy BF16 workloads across Llama 3.1, Gemma 3, Mistral, and other state-of-the-art language models. The release also added support for AMD MI300/325, RDNA3/4, and NVIDIA RTX 2060–5090, along with expanded model coverage.

June also united builders from around the world for Modular Hack Weekend, where developers created everything from Fast Fourier Transform implementations and GPU-accelerated quantum simulators to high-performance bioinformatics libraries. We introduced Mammoth, our new system for scaling GenAI inference across any GPU, and rolled out new ways to integrate Mojo kernels directly into Python workflows. The community pushed the boundaries of kernel design, explored breakthroughs in scientific computing, and continued expanding what’s possible with Mojo and MAX.

Let’s take a look at everything the Modular universe made possible last month.

# **Blogs, Tutorials, and Videos**

- Developers from across the AI and systems programming communities recently came together for **Modular Hack Weekend**: a global, virtual hackathon focused on GPU programming and model implementation with Mojo and MAX.To kick off the hackathon, we hosted a [**GPU Programming Workshop**](https://www.youtube.com/watch?v=BBhZ9Ltpmdw), both in-person at our office in Los Altos, California, and virtually via livestream. Check out all the talk recordings:[Chris Lattner and Tim Davis](https://www.youtube.com/watch?v=DqTBvi0DKgg), co-founders of Modular[Chuan Li](https://www.youtube.com/watch?v=F7jGCKHl7Wg), founding team member and Chief Scientific Officer at Lambda[Bin Bao](https://www.youtube.com/watch?v=2LOPdVFoErs), Software Engineer and torch.compile Tech Lead at Meta[Jared Roesch](https://youtu.be/BBhZ9Ltpmdw?t=1717), cofounder of OctoAI and Distinguished Engineer at NVIDIA[Watch the hackathon highlight reel](https://www.modular.com/blog/modular-hack-weekend) and check out [the recap blog post](https://www.modular.com/blog/modular-hack-weekend?utm_source=modverse&utm_campaign=community).Explore [the winning projects](https://forum.modular.com/t/modular-hack-weekend-winners-announced/1848) and [all the submitted projects](https://forum.modular.com/tags/c/community-showcase/8/modular-hack-weekend).
- We dropped a series of exciting announcements in [our video premiere](https://www.youtube.com/watch?v=TrBXHPGRlnQ):Modular Platform is now generally available on AMD Instinct™ MI300X and MI325 GPUs! Benchmarks show up to 53% better throughput on prefill-heavy BF16 workflows. Together with AMD, we’re combining best-in-class compute with developer-friendly software. Check out [the full blog post](https://www.modular.com/blog/modular-x-amd-unleashing-ai-performance-on-amd-gpus?utm_source=modverse&utm_campaign=community).Meet Mammoth: our new Kubernetes-native system for scaling GenAI inference across any GPU. Deploy Hugging Face models across AMD and NVIDIA from a single container, with no manual configuration. Join [the public preview](https://www.modular.com/blog/introducing-mammoth-enterprise-scale-genai-deployments-made-simple?utm_campaign=community&utm_source=modverse).Mojo in Python: you can now drop Mojo kernels directly into your Python workflows. Available today in nightly builds, and backed by 450k+ lines of open source Mojo kernel code. [Start here](https://docs.modular.com/mojo/manual/python/mojo-from-python/).
- Now on YouTube: [Chris Lattner's full talk from AMD AdvancingAI 2025](https://www.youtube.com/watch?v=liR2Pn5Zp9g)! Learn how Mojo brings together Python’s simplicity and C++ performance to power a next-gen AI software stack. Plus, catch the post-talk Q&A with Chris.
- Chris Lattner joined [the Latent Space podcast](https://www.youtube.com/watch?v=04_gN-C9IAo) to share an inside look at the history of Modular and Mojo, and the future of GPU programming.
- [Our June community meeting](https://www.youtube.com/watch?v=1Q4RNVOSAH0) featured two in-depth presentations on how Mojo is being applied in scientific computing:[Bioinformatics with Mojo](https://youtu.be/1Q4RNVOSAH0?t=32): Seth walked us through ish, a high-performance, index-free alignment tool built in Mojo. He shared insights on SIMD optimizations, GPU acceleration, and benchmarking against C++ libraries like Parasail.[Particle Physics with Mojo](https://youtu.be/1Q4RNVOSAH0?t=1438): Photon shared how Mojo is helping streamline complex particle physics simulations. He introduced two open-source libraries, newmojo and hepjo, and discussed porting a C++/Python research pipeline to Mojo with promising performance gains.
- Simon Veitner published [a deep dive on crafting a blazing-fast matrix transpose kernel for NVIDIA Hopper](https://veitner.bearblog.dev/highly-efficient-matrix-transpose-in-mojo/). He covers TMA, swizzling, thread coarsening, and shows how far you can push performance using pure Mojo.If you want to understand how to set up descriptors and move data efficiently, start with [Simon's previous post](https://veitner.bearblog.dev/use-tma-without-cuda/).New to Mojo? Start from the beginning. [Simon’s intro post](https://veitner.bearblog.dev/short-introduction-to-the-mojo-programming-language/) shows how to write your first GPU kernel using vector addition in Mojo’s Pythonic syntax.If you're looking to push Mojo even further, [Simon also walked through using custom PTX instructions in Mojo for advanced GPU control](https://veitner.bearblog.dev/use-ptx-instructions-in-mojo/).
- We released [our comic series, GPU Whisperers](https://comic.modular.com), that perfectly captures the beautiful chaos of living through the GenAI revolution! 🧑‍🚀
- Vincent Warmerdam shared an excellent [writeup on calling Mojo from Python](https://koaning.io/posts/giving-mojo-a-spin/).
- Modular is [now available on the Amazon Web Services (AWS) Marketplace](https://aws.amazon.com/marketplace/pp/prodview-t6oswipky4fhs)! 500+ Pre-Optimized Models, with an OpenAI API Compatible endpoint, ready for you to run across NVIDIA B200, H200, H100, A100, A10, L40 and L4 GPUs, with intelligent batching and memory management.
- Modular Tech Talks is an exclusive series featuring internal presentations from our engineering team, explaining the inner workings of the Modular technology stack. [In our most recent edition](https://www.youtube.com/watch?v=6hqMFXbugGo), Kyle Caverly gives a tour of the MAX Pipelines architecture, covering its major interfaces and how they enable the Modular team to rapidly bring up state of the art models with high-performance features like KV Cache optimization and speculative decoding.
- Vibe coding your next Mojo masterpiece? You’re in luck: [check out our guide](https://docs.modular.com/max/coding-assistants/) on using AI coding assistants like Cursor and Copilot to build faster with Mojo and MAX.
- Our recent Democratizing AI Compute series by Chris Lattner offers a clear perspective on the challenges shaping the future of AI infra, and you can now explore the full series in one convenient place! 🔖 [Bookmark for later or subscribe to the RSS feed](https://www.modular.com/democratizing-ai-compute?utm_source=modverse&utm_campaign=modverse).[In the latest installment](https://www.modular.com/blog/how-is-modular-democratizing-ai-compute?utm_source=modverse&utm_campaign=community), Chris Lattner plots a flight plan across the Modular stack: Mojo the molten inner world, MAX the mighty gas giant, all orbiting in the Mammoth cluster.
- Building high-performance AI infrastructure doesn’t have to take months. Inworld proved that by launching a state-of-the-art speech pipeline into production in under 8 weeks with Modular. [Their blog post](https://inworld.ai/blog/how-we-made-state-of-the-art-speech-synthesis-scalable-with-modular) explains how they used MAX and Mojo to run on NVIDIA Blackwell GPUs, meet real-time latency targets that were 70% faster than using the latest vLLM.

# **Awesome MAX + Mojo**

- forfudan created [an online book on Mojo called “Mojo Miji - A Guide to Mojo Programming Language from A Pythonista’s Perspective”](https://forum.modular.com/t/mojo-miji-a-guide-to-mojo-programming-language-from-a-pythonistas-perspective/1594).
- TilliFe started [a notebook series on training transformer neural networks in Nabla](https://forum.modular.com/t/training-a-transformer-with-max-acceleration/1695), a framework for differentiable programming in Mojo.
- HammadHAB built a [simple, lightweight INI file parser in Mojo](https://forum.modular.com/t/mojoini-minimal-ini-parser-in-mojo/1929).
- [26 community members shared their Modular Hack Weekend projects!](https://forum.modular.com/tags/c/community-showcase/8/none/modular-hack-weekend)

# **Open-Source Contributions**

**‍**If you’ve recently had your first PR merged, message [**Caroline Frasca**](https://forum.modular.com/u/caroline) in the forum to claim your epic Modular swag! Check out the [**recently merged contributions**](https://github.com/modularml/mojo/pulls?page=1&q=is%3Apr+is%3Aclosed+label%3Amerged-internally+sort%3Aupdated-desc) from our amazing community members:

- [Ivo-Balbaert](https://github.com/modular/modular/pulls?q=is%3Apr+author%3AIvo-Balbaert+) [[1](https://github.com/modular/modular/pull/4711)]
- [simveit](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Asimveit) [[1](https://github.com/modular/modular/pull/4715)][[2](https://github.com/modular/modular/pull/4725)][[3](https://github.com/modular/modular/pull/4706)]
- [soraros](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Asoraros+) [[1](https://github.com/modular/modular/pull/4707)][[2](https://github.com/modular/modular/pull/4608)][[3](https://github.com/modular/modular/pull/4607)][[4](https://github.com/modular/modular/pull/4734)][[5](https://github.com/modular/modular/pull/4339)][[6](https://github.com/modular/modular/pull/4557)][[7](https://github.com/modular/modular/pull/4778)][[8](https://github.com/modular/modular/pull/4764)][[9](https://github.com/modular/modular/pull/4733)][[10](https://github.com/modular/modular/pull/4733)][[11](https://github.com/modular/modular/pull/4753)][[12](https://github.com/modular/modular/pull/4786)][[13](https://github.com/modular/modular/pull/4526)][[14](https://github.com/modular/modular/pull/4775)][[15](https://github.com/modular/modular/pull/4760)][[16](https://github.com/modular/modular/pull/4747)][[17](https://github.com/modular/modular/pull/4744)][[18](https://github.com/modular/modular/pull/3083)][[19](https://github.com/modular/modular/pull/4693)][[20](https://github.com/modular/modular/pull/4770)][[21](https://github.com/modular/modular/pull/4799)][[22](https://github.com/modular/modular/pull/4821)][[23](https://github.com/modular/modular/pull/4825)][[24](https://github.com/modular/modular/pull/4204)][[25](https://github.com/modular/modular/pull/4876)][[26](https://github.com/modular/modular/pull/4816)][[27](https://github.com/modular/modular/pull/4903)][[28](https://github.com/modular/modular/pull/4901)][[29](https://github.com/modular/modular/pull/4900)][[30](https://github.com/modular/modular/pull/4880)][[31](https://github.com/modular/modular/pull/4898)][[32](https://github.com/modular/modular/pull/4895)][[33](https://github.com/modular/modular/pull/4890)][[34](https://github.com/modular/modular/pull/4772)][[35](https://github.com/modular/modular/pull/4875)][[36](https://github.com/modular/modular/pull/4935)][[37](https://github.com/modular/modular/pull/4933)][[38](https://github.com/modular/modular/pull/4814)][[39](https://github.com/modular/modular/pull/4757)][[40](https://github.com/modular/modular/pull/4812)][[41](https://github.com/modular/modular/pull/4800)]
- [martinvuyk](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Amartinvuyk) [[1](https://github.com/modular/modular/pull/4704)][[2](https://github.com/modular/modular/pull/4653)][[3](https://github.com/modular/modular/pull/4592)][[4](https://github.com/modular/modular/pull/4593)][[5](https://github.com/modular/modular/pull/4671)][[6](https://github.com/modular/modular/pull/3528)][[7](https://github.com/modular/modular/pull/3810)][[8](https://github.com/modular/modular/pull/4605)][[9](https://github.com/modular/modular/pull/4595)][[10](https://github.com/modular/modular/pull/4802)][[11](https://github.com/modular/modular/pull/4803)][[12](https://github.com/modular/modular/pull/4869)][[13](https://github.com/modular/modular/pull/4858)][[14](https://github.com/modular/modular/pull/4323)][[15](https://github.com/modular/modular/pull/4756)]
- [christoph-schlumpf](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Achristoph-schlumpf+) [[1](https://github.com/modular/modular/pull/4714)]
- [bgreni](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Abgreni) [[1](https://github.com/modular/modular/pull/4171)][[2](https://github.com/modular/modular/pull/4806)]
- [gabrieldemarmiesse](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Agabrieldemarmiesse+) [[1](https://github.com/modular/modular/pull/4661)]
- [sstadick](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Asstadick+) [[1](https://github.com/modular/modular/pull/4746)][[2](https://github.com/modular/modular/pull/4762)][[3](https://github.com/modular/modular/pull/4537)][[4](https://github.com/modular/modular/pull/4796)]
- [bgreni](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Abgreni+) [[1](https://github.com/modular/modular/pull/4635)][[2](https://github.com/modular/modular/pull/4781)][[3](https://github.com/modular/modular/pull/4785)]
- [hardikkgupta](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Ahardikkgupta+) [[1](https://github.com/modular/modular/pull/4782)][[2](https://github.com/modular/modular/pull/4832)][[3](https://github.com/modular/modular/pull/4897)]
- [sibarras](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Asibarras+) [[1](https://github.com/modular/modular/pull/4784)]
- [msaelices](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Amsaelices+) [[1](https://github.com/modular/modular/pull/4625)][[2](https://github.com/modular/modular/pull/4562)]
- [mzaks](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Amzaks+) [[1](https://github.com/modular/modular/pull/4841)][[2](https://github.com/modular/modular/pull/4863)]
- [zsiegel92](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Azsiegel92+) [[1](https://github.com/modular/modular/pull/4881)]
- [winding-lines](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Awinding-lines+) [[1](https://github.com/modular/modular/pull/4888)]
- [samufi](https://github.com/modular/modular/pulls?q=is%3Apr+author%3Asamufi) [[1](https://github.com/modular/modular/pull/4928)]

## Read more from Modular

View all blogs

Modverse #55: Mojo 1.0 Beta, Community Mojo Libraries, and Real-Time Patient Conversations Powered by MAX

June 10, 2026

How I built a pure Mojo app (and 10 libraries) with AI agents

May 19, 2026

Modverse #54: AMD AI DevDay, New Modular Offices, and a Community That Keeps Shipping

May 4, 2026

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
