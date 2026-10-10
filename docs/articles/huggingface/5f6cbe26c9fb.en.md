---
vendor: huggingface
title: Apriel-H1: The Surprising Key to Distilling Efficient Reasoning Models
original_title: Apriel-H1: The Surprising Key to Distilling Efficient Reasoning Models
url: https://huggingface.co/blog/ServiceNow-AI/apriel-h1
date: 2025-11-03
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: f8729dd6336c
---


# Apriel-H1: The Surprising Key to Distilling Efficient Reasoning Models

Enterprise

Article

					November 19, 2025


35

- [![](https://huggingface.co/avatars/62d031d7fdb0d0747476d52c78dcdb18.svg)](https://huggingface.co/ostapeno)
- [![](https://huggingface.co/avatars/ed617ef804a5f3863cc496a5284c88a9.svg)](https://huggingface.co/nitsanluke)
- [![](https://huggingface.co/avatars/59cc1a52f69cfeb832ea3b90ce852ae9.svg)](https://huggingface.co/harithoppil)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/654bcb6fae75d15300d48205/T4L1RZUgCZgdik4ZhEWCq.jpeg)](https://huggingface.co/Steveeeeeeen)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1627505688463-60107b385ac3e86b3ea4fc34.jpeg)](https://huggingface.co/davanstrien)
- [![](https://huggingface.co/avatars/ea41ddd50d96a0cd45acd9dc0a362072.svg)](https://huggingface.co/shruthan-r)

Torsten Scholak

tscholak

ServiceNow-AI

Oleksiy Ostapenko

ostapeno

ServiceNow-AI

Raymond Li

RaymondLi

ServiceNow-AI

Luke Kumar

nitsanluke

ServiceNow-AI

Joel Lamy-Poirier

jlamypoirier

ServiceNow-AI

We converted our 15B reasoning model to a Mamba hybrid achieving 2.1x throughput with minimal quality loss. The key? A non-obvious insight about what data to distill on, and why intuition fails here.

When MiniMax published their [M2 post-mortem](https://huggingface.co/blog/MiniMax-AI/why-did-m2-end-up-as-a-full-attention-model) in October explaining why they abandoned efficient attention at 230B scale, the narrative briefly became "efficient attention is dead." Within days, [Kimi Linear](https://github.com/MoonshotAI/Kimi-Linear) proved otherwise. The real lesson: it depends on your constraints.

Our constraint was simple: **we had a strong 15B reasoning model and needed to make it efficient without starting over.** No infinite compute for 20T-token pretraining. No luxury of architectural co-design from day one. Just a practical question: can you retrofit efficiency into an existing model through distillation?

Spoilers: yes, but only if you ignore your intuition about what data to use.

## What We Built

The [Apriel-H1 family](https://huggingface.co/collections/ServiceNow-AI/apriel-h1): seven checkpoints spanning 25-40 Mamba layers (out of 50 total), showing the complete efficiency-quality frontier. Our flagship [Apriel-H1-15b-Thinker-SFT](https://huggingface.co/ServiceNow-AI/Apriel-H1-15b-Thinker-SFT) achieves **2.1x throughput with minimal quality loss**: MATH500 and MTBench improve a few points (0.90 → 0.92 and 8.30 → 8.58, respectively), while GSM8k (0.97 → 0.95), GPQA (0.59 → 0.55), and AIME24 (0.70 → 0.65) regress slightly. Total training: 76.8B tokens.

[![Apriel-H1 Evaluation Results](https://huggingface.co/ServiceNow-AI/Apriel-H1-15b-Thinker-SFT/resolve/main/images/apriel_h_vs_apriel_15b_eval_thrput_comparison.png)](https://huggingface.co/ServiceNow-AI/Apriel-H1-15b-Thinker-SFT/resolve/main/images/apriel_h_vs_apriel_15b_eval_thrput_comparison.png)

*Apriel-H1-15b-Thinker-SFT (green) vs full-attention teacher (blue). Reasoning quality stays nearly flat across benchmarks while throughput increases 1.89-2.09x depending on context length.*

The full details are in our [Apriel-H1 paper](https://arxiv.org/abs/2511.02651). Here, we focus on the key insight that made it work.

## The Non-Obvious Insight

Here's what we initially thought would work: just distill on pretraining data and round it out with some SFT.

The reasoning seemed solid. We're inserting completely new Mamba layers that have never seen data. These linear SSMs need to learn general-purpose token mixing from scratch. How can they become effective mixers unless they get exposure to the same broad distribution the original attention layers saw?

So we tried it. Then we tried mixing pretraining and SFT data. It didn't work. The distilled hybrids lost reasoning quality, sometimes dramatically.

**What actually worked: high-quality reasoning traces from the teacher's SFT dataset.**

Distilling a reasoning model isn't about transferring general next-token prediction. The base model already has that, and we started from a strong 15B foundation. What we're preserving is specific and fragile: **the teacher's multi-step reasoning patterns.**

Those patterns emerge from intricate attention mechanisms. Retrieval heads pulling context from thousands of tokens back. Induction heads recognizing and continuing logical chains. Long-range dependencies connecting premises to conclusions many steps later. When you replace attention wholesale with Mamba's linear recurrence, these computational mechanisms are disrupted. The hybrid must discover new paths to the same reasoning outcomes.

That discovery requires explicit examples where reasoning structure is visible and correct:

- Multi-step math proofs where each thought follows from the previous
- Coding tasks with clear logical dependencies
- Scientific analysis with detailed explanatory chains

Pretraining data, on the other hand, is too noisy and too diffuse. The reasoning signal gets lost. You need concentrated examples of the specific capability you're trying to preserve.

Once we understood the data choice, our distillation method became clear too. We used **reverse KL divergence** (temperature 1) rather than forward KL. Reverse won consistently. Why? We're training on problems where the teacher has high confidence and clear structure. Reverse KL's mode-seeking behavior encourages the student to commit to those high-confidence predictions. When your teacher is confident and correct, you want your student to be confident too.

This insight is the key to the whole approach: **match your distillation data to the capability you're preserving, not the capability you're building.**

## How to Apply It: Staged Distillation

You can't just swap 40 attention layers for Mamba and hope. We learned this the hard way, and eventually developed a staged distillation procedure to get there reliably.

**Stage 1: Identify least-important layers.** We used a Leave-One-Out (LOO) analysis on MMLU: remove each layer, replace with identity, then measure the drop. Sort by importance, replace the bottom 25 with [Mamba-in-Llama](https://arxiv.org/abs/2408.15237) (MIL) initialized mixers. Distill end-to-end. This worked for our H-25 checkpoint.

**Stage 2: Progressive conversion beyond 25 layers.** LOO broke down past 25 layers because layers unimportant in isolation became critical in combination. To address this, we developed a dynamic heuristic we call **MIL-Mamba-Replacement (MMR).** For each remaining attention layer, we initialize a Mamba mixer with MIL, run 100 training steps, and record the distillation loss. Layers converging to lower loss are "easier" to replace. This captures training dynamics rather than static importance.

We progressed incrementally: 25 → 27 → 30 → 34 → 37 → 40 Mamba layers, grouping replacements by MMR scores. Each checkpoint distills from the previous.

**Stage 3: End-to-end training on SFT data.** After reaching the target Mamba layer count, we did a final SFT pass until reasoning performance stabilized. After 55.9B distillation tokens and 20.9B SFT tokens, this produced our final Apriel-H1-15b-Thinker-SFT model.

[![Apriel-H1 Family Performance](https://huggingface.co/ServiceNow-AI/Apriel-H1-15b-Thinker-SFT/resolve/main/images/throughput_eval_score_vs_throughput_1-16k_annotated.png)](https://huggingface.co/ServiceNow-AI/Apriel-H1-15b-Thinker-SFT/resolve/main/images/throughput_eval_score_vs_throughput_1-16k_annotated.png)

*The complete efficiency frontier. Each checkpoint shows cumulative training tokens. Our flagship H-30-SFT (released as Apriel-H1-15b-Thinker-SFT) used 76.8B total for 2.1x throughput at 0.76 average score. The aggressively converted H-40 variant used 136.5B tokens for 3.4x throughput. For reference: NVIDIA's Nemotron-Nano-9B-v2 achieves 4.6x at 0.77 score but required training from scratch with orders of magnitude more compute.*

## Making It Reproducible: Fast-LLM

We built all this on [Fast-LLM](https://github.com/ServiceNow/Fast-LLM), our open-source training framework. The core architectural principle: **large language model transformers should be modular.** Attention and Mamba are different implementations of the same "mixing" interface, and can be swapped freely.

Here's a hybrid architecture in Fast-LLM's config format:

```
decoder:
  type: "pattern"
  blocks:
    attention_block:
      mixer:
        type: "attention"
        heads: 32
        head_groups: 8
        head_size: 128
      mlp:
        type: "gated"
        activation: "silu"
    mamba_block:
      mixer:
        type: "mamba"
        d_inner: 4096
        state_size: 16
        dt_rank: 16
      mlp:
        type: "gated"
        activation: "silu"
  num_blocks: 50
  pattern: ["attention_block", "attention_block", "mamba_block", ...]
```

The `pattern` field specifies layer order. For Apriel-H1-15b-Thinker-SFT: 30 `mamba_block`, 20 `attention_block`, placed by importance. That's it.

Distillation is configuration too:

```
model:
  base_model:
    head:
      distillation_model: teacher
      distillation_loss_implementation: reverse_kl
reference_models:
  teacher:
    pretrained:
      format: mistral
      path: path/to/Apriel-Nemotron-15b-Thinker
```

Fast-LLM handles gradient accumulation, distributed training, tensor parallelism, checkpointing, everything you need for large-scale experimentation. It's open source, and licensed under Apache 2.0. **You can reproduce this work** because we designed the infrastructure to make it reproducible.

## FAQs

**Why release all checkpoints?** Because optimal depends on your constraints. H-30 offers the best balance. H-40 maximizes throughput for latency-critical workloads. The intermediate checkpoints let you choose your exact trade-off.

**Why do you get different speedups at different context lengths?** Mamba's linear complexity advantage grows with sequence length, and attention degrades quadratically.

**Why did you only try Mamba?** We used **Mamba-1** for three reasons: it has a proven distillation track record, has shown strong empirical performance, and was simple to implement in our framework. It let us focus on the data question first.

**What were the Mamba hyperparameters?** State size 16, DT rank 16, inner dimension 4096. For our GQA setup in Apriel we expanded B (input projection) and x (state) to match total attention heads following [M1](https://arxiv.org/abs/2504.10449).

**Why didn't you try more advanced conversion methods?** We used [Mamba-in-Llama](https://arxiv.org/abs/2408.15237) initialization and knowledge distillation rather than [MOHAWK's](https://arxiv.org/abs/2408.10189) multi-stage procedure because the latter didn't show significant advantages in preliminary experiments.

**Why did you only SFT the H-30 model?** We only applied SFT to H-30 to validate that distilled hybrids can be improved through standard post-training. The other checkpoints are pure distillation but can be fine-tuned similarly.

**Why didn't you explore RL?** This was a scoping decision to isolate the distillation question: can you transfer reasoning via knowledge distillation alone? Answer: yes. But RL should close remaining quality gaps further. We are exploring RL for future iterations.

**Did you really show that Apriel-H1 matches full-attention reasoning at similar compute budgets?** We didn't do an apples-to-apples comparison between full-attention Apriel and a hybrid trained identically from pretraining forward. That would require repeating all mid-training and post-training of the teacher with the Apriel-H1 architecture, which was beyond our compute budget. What we can claim though is that retrofitting efficiency via distillation is practical and effective, and that the resulting hybrids can be fine-tuned to match or exceed the teacher's reasoning quality.

## The Production Reality

We've implemented Apriel-H1 in Hugging Face Transformers and vLLM. Transformers integration is straightforward. We ship a new model class with interchangeable attention and Mamba layers. vLLM integration uses their recent [Mamba cache operations](https://pytorch.org/blog/hybrid-models-as-first-class-citizens-in-vllm/) for continuous batching, prefix caching, and chunked prefill. The vLLM plugin is ready. We are currently waiting for final legal approval to open-source it.

**Honest assessment:** Deploying hybrids today means rough edges. The tooling is maturing fast but isn't turnkey. You will write custom code, validate numerical behavior carefully, and work around framework limitations. For teams that can absorb that cost, throughput gains are worth it. For those that can't, waiting might be the right call.

## Takeaway

Most teams don't have infinite compute for 20T-token pretraining. If you've invested in a strong base model and need efficiency gains, this work shows a practical path: distill into hybrids using high-quality task-specific data that matches the capability you're preserving.

The surprising finding, **use reasoning data to distill reasoning**, seems obvious in retrospect but contradicts initial intuition. We validated it, explained why it works, and built the infrastructure to make it reproducible.

## Try It

**Models:** [Apriel-H1 Collection on HuggingFace](https://huggingface.co/collections/ServiceNow-AI/apriel-h1)
**Training framework:** [Fast-LLM on GitHub](https://github.com/ServiceNow/Fast-LLM)
**Teacher model:** [Apriel-Nemotron-15B-Thinker](https://huggingface.co/ServiceNow-AI/Apriel-Nemotron-15b-Thinker)
**Paper:** [Apriel-H1: Towards Efficient Enterprise Reasoning Models](https://arxiv.org/abs/2511.02651)

Found something broken? File an issue. Discovered a better layer placement heuristic? Tell us. Built something interesting on Apriel-H1? We'd love to see it.

**Citation:**

```
@article{apriel-h1-2025,
  title={Apriel-H1: Towards Efficient Enterprise Reasoning Models},
  author={SLAM Lab, ServiceNow},
  journal={arXiv preprint arXiv:2511.02651},
  year={2025}
}
```

**Core contributors:** Oleksiy Ostapenko, Luke Kumar, Raymond Li, Denis Kocetkov, Joel Lamy-Poirier, Torsten Scholak
**Contributors:** Shruthan Radhakrishna, Soham Parikh, Shambhavi Mishra
**Technical co-leads:** Torsten Scholak, Sathwik Tejaswi Madhusudhan

## Models mentioned in this article 2

## Collections mentioned in this article 1

More from this author

## AutoSynthData: Generating Training Data for Enterprise Agents

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/63d3095c2727d7888cbb54e2/Uv-Lx8PVGviqokfOyYlCN.png)

37

October 2, 2026

## Can Voice Agents Handle Bilingual Customers? Benchmarking Frontier ASR on Code-Switched Speech

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/63d3095c2727d7888cbb54e2/Uv-Lx8PVGviqokfOyYlCN.png)

46

June 9, 2026

### Community

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2FServiceNow-AI%2Fapriel-h1) or [log in](https://huggingface.co/login?next=%2Fblog%2FServiceNow-AI%2Fapriel-h1) to comment


35

- [![](https://huggingface.co/avatars/62d031d7fdb0d0747476d52c78dcdb18.svg)](https://huggingface.co/ostapeno)
- [![](https://huggingface.co/avatars/ed617ef804a5f3863cc496a5284c88a9.svg)](https://huggingface.co/nitsanluke)
- [![](https://huggingface.co/avatars/59cc1a52f69cfeb832ea3b90ce852ae9.svg)](https://huggingface.co/harithoppil)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/654bcb6fae75d15300d48205/T4L1RZUgCZgdik4ZhEWCq.jpeg)](https://huggingface.co/Steveeeeeeen)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1627505688463-60107b385ac3e86b3ea4fc34.jpeg)](https://huggingface.co/davanstrien)
- [![](https://huggingface.co/avatars/ea41ddd50d96a0cd45acd9dc0a362072.svg)](https://huggingface.co/shruthan-r)
- [![](https://huggingface.co/avatars/84e286313264af1461389fedef8b030d.svg)](https://huggingface.co/PlayAI)
- [![](https://huggingface.co/avatars/c80cf773f436748c992d76ca042dd5fb.svg)](https://huggingface.co/RaymondLi)
- [![](https://huggingface.co/avatars/226f57ea23b9dd861e71b7ba7821adce.svg)](https://huggingface.co/optimass)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/iAhWDdlCKRDYln-dCN73H.png)](https://huggingface.co/nicogontier)
- [![](https://huggingface.co/avatars/0f911fee8c173543a6e0cbd78a940676.svg)](https://huggingface.co/dotvignesh)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/651e96991b97c9f33d26bde6/-Bqs6qrmz0yCfwtB2e-6q.jpeg)](https://huggingface.co/eliebak)

## Models mentioned in this article 2

## Collections mentioned in this article 1
