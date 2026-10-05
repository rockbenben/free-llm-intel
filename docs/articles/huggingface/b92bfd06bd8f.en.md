---
vendor: huggingface
title: Safetensors is Joining the PyTorch Foundation
original_title: Safetensors is Joining the PyTorch Foundation
url: https://huggingface.co/blog/safetensors-joins-pytorch-foundation
date: 2026-05-12
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 157308aea8f0
---

Back to Articles

# Safetensors is Joining the PyTorch Foundation

Published
					April 8, 2026

Update on GitHub

Upvote

42

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)](https://huggingface.co/pcuenq)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1666977434736-617bc8d1000dbbbf7c225eed.png)](https://huggingface.co/mcpotato)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/5dd96eb166059660ed1ee413/NQtzmrDdbG0H8qkZvRyGk.jpeg)](https://huggingface.co/julien-c)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/69c4c97bea5bffda021d4e4e/45XGDj29b7YgXb4I9DKZk.jpeg)](https://huggingface.co/LOYOLABIZ)
- [![](https://huggingface.co/avatars/cdeb6e415b4bfa6667029efd347088f6.svg)](https://huggingface.co/stgrue)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6258561f4d4291e8e63d8ae6/EYjinEYAcbtm_dL5QmmRi.png)](https://huggingface.co/Sylvestre)

Luc Georges

mcpotato

Lysandre

lysandre

Today, we're announcing that Safetensors has joined the PyTorch Foundation as a foundation-hosted project under the Linux Foundation, alongside DeepSpeed, Helion, Ray, vLLM, and PyTorch itself.

## How we got here

Safetensors started as a Hugging Face project born out of a concrete need: a way to store and share model weights that couldn't execute arbitrary code. The pickle-based formats that dominated the ecosystem at the time meant that there was a very real risk you’d be running malicious code. While this was an acceptable risk when ML was still budding, it would become unacceptable as open model sharing became central to how the ML community works.

The format we built is intentionally simple: a JSON header with a hard limit of 100MB, describing tensor metadata, followed by raw tensor data. Zero-copy loading that maps tensors directly from disk. Lazy loading so you can read individual weights without deserializing an entire checkpoint.

What we didn't fully anticipate was how broadly it would be adopted. Today, Safetensors is the default format for model distribution across the Hugging Face Hub and others, used by tens of thousands of models across all modalities in ML. It has become the preferred way for the open source ML community to share models.

## Why the PyTorch Foundation

We want Safetensors to truly belong to the community. The project has always been open source, but code contributions are just one part of its evolution. By bringing more companies and contributors into the governance of the project, we make sure that progress reflects the breadth of the community building on top of it. Joining the PyTorch Foundation means Safetensors now has a vendor-neutral home. The trademark, the repository, and the governance of the project sit with the Linux Foundation rather than any single company. Hugging Face's two core maintainers, Luc and Daniel, remain on the Technical Steering Committee and continue to lead the project day-to-day, but Safetensors now formally belongs to the community that depends on it.

We believe safety is best guaranteed when every contributor can build on what already exists; a principle now embedded in the project's governance itself.

## What this means for users and contributors

For the vast majority of users, nothing changes. The format is the same, the APIs are the same, the Hub integration is the same: no breaking changes. Models stored in Safetensors format today will continue to work exactly as they do now.

For contributors, the path to becoming a maintainer is now formally documented and open to anyone in the community. The project's governance lives in GOVERNANCE.md and MAINTAINERS.md in the repository. For organizations building on top of Safetensors, neutral governance under the Linux Foundation provides a stable, long-term foundation, entirely community-driven.

## What comes next

Safetensors is a well-established project, adopted by the ecosystem at large, but we're still convinced we're at the very beginning of the project.

**We're working with the PyTorch team so that Safetensors may be used within PyTorch core as a serialization system for torch models.**

The coming months will see significant growth, and we couldn't think of a better home for that next chapter than the PyTorch Foundation. The roadmap ahead includes device-aware loading and saving, so tensors can load directly onto CUDA, ROCm, and other accelerators without unnecessary CPU staging.

We're also building first-class APIs for Tensor Parallel and Pipeline Parallel loading, so each rank or pipeline stage loads only the weights it needs. And as the ecosystem's quantization landscape continues to evolve, we'll be formalizing support for FP8, block-quantized formats like GPTQ and AWQ, and sub-byte integer types.

These are problems the whole ecosystem has a stake in solving, and being inside the PyTorch Foundation means we can work on them in collaboration with the other hosted projects rather than in parallel.

## Get involved

Safetensors is open source and contributions are welcome at every level, from bug reports and documentation to new features and participation in governance.

- **GitHub:** [github.com/huggingface/safetensors](https://github.com/huggingface/safetensors)
- **Documentation:** [huggingface.co/docs/safetensors](https://huggingface.co/docs/safetensors)
- **PyTorch Foundation:** [pytorch.org/foundation](https://pytorch.org/foundation)

If you're a developer, researcher, or organization that builds on Safetensors and want to be more involved in shaping its direction, open an issue, start a discussion, or reach out to the maintainers directly. The project has always belonged to the community that uses it. The governance now reflects that too.

More Articles from our Blog

guide

partnerships

open-source-collab

## Run AI workloads on any cloud, store on Hugging Face: zero-egress storage with SkyPilot

- ![](https://huggingface.co/avatars/50200d00263e5e8a9aeb265a204dc085.svg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6429b84e8852afdf89beeae5/K5TdNld69Z8bgqFghYyBx.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6a468f8e9a0f24346593df15/w2XYo_Hv7xJ5Cs-5XX9ra.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/61a5dcedf14aa6d7c74925f7/ZbVN8MsvjWwanqOwUdIeC.png)
- +1

35

July 7, 2026

partnerships

audio

open-source-collab

## Hugging Face and Cerebras bring Gemma 4 to real-time voice AI

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/67f2f500e329a81a62a05d44/DOlzc8GFQzrnfVrsOdtbN.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/65d66b494bbd0d92b641cdbb/6-7dm7B-JxcoS1QlCPdMN.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/5e48005437cb5b49818287a5/4uCXGGui-9QifAT4qelxU.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/qbWPAosFCnSgPJ-SRNZeG.png)

107

July 1, 2026

### Community

nigeldouglas

May 12

Will there be a concerted effort now to get newer (and older) LLM models to adopt the more secure safetensors format rather than allowing AI developers to continue with pickle files as they did in the past? And what would some of the objections be, if any, for a developer to not transition to safetensors format?

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fsafetensors-joins-pytorch-foundation) or [log in](https://huggingface.co/login?next=%2Fblog%2Fsafetensors-joins-pytorch-foundation) to comment

Upvote

42

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)](https://huggingface.co/pcuenq)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1666977434736-617bc8d1000dbbbf7c225eed.png)](https://huggingface.co/mcpotato)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/5dd96eb166059660ed1ee413/NQtzmrDdbG0H8qkZvRyGk.jpeg)](https://huggingface.co/julien-c)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/69c4c97bea5bffda021d4e4e/45XGDj29b7YgXb4I9DKZk.jpeg)](https://huggingface.co/LOYOLABIZ)
- [![](https://huggingface.co/avatars/cdeb6e415b4bfa6667029efd347088f6.svg)](https://huggingface.co/stgrue)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6258561f4d4291e8e63d8ae6/EYjinEYAcbtm_dL5QmmRi.png)](https://huggingface.co/Sylvestre)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/5e3aec01f55e2b62848a5217/PMKS0NNB4MJQlTSFzh918.jpeg)](https://huggingface.co/lysandre)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/67d7dea1786ddcb3af5a44b3/gEgXTH4oO91GIzjHR-yrb.png)](https://huggingface.co/CarolinePascal)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6317233cc92fd6fee317e030/cJHSvvimr1kqgQfHOjO5n.png)](https://huggingface.co/tomaarsen)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/68750699d365b5bf3756c71c/j39Nlb_MXxhT10E9yfsVm.png)](https://huggingface.co/ILer33)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1643012094339-61914f536d34e827404ceb99.jpeg)](https://huggingface.co/hysts)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1594144055859-5ee3a7cd2a3eae3cbdad1305.jpeg)](https://huggingface.co/yjernite)
