---
vendor: huggingface
title: Up to 3.2x Faster Inference with LFM2.5-DSpark
original_title: Up to 3.2x Faster Inference with LFM2.5-DSpark
url: https://huggingface.co/blog/LiquidAI/lfm25-dspark
date: 2026-08-20
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: e0914bd48c0f
---

Back to Articles

# Up to 3.2x Faster Inference with LFM2.5-DSpark

Team

Article

Published
					August 20, 2026

Upvote

56

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/646e57a5cb6ea6e6b6df1ad4/PlGhM2SUynFBUdYAylaZK.jpeg)](https://huggingface.co/fernandofernandes)
- [![](https://huggingface.co/avatars/33d508f28166e6a6b449d742fa1f60e0.svg)](https://huggingface.co/mayankagarwal)
- [![](https://huggingface.co/avatars/ee4a89ebc7a0716e21deaebc86e062e6.svg)](https://huggingface.co/nathanrchn)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6317233cc92fd6fee317e030/cJHSvvimr1kqgQfHOjO5n.png)](https://huggingface.co/tomaarsen)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/67379ceb30d6ac7169c5dc99/hQZ-atHUbYkcfjsgQ0ywE.png)](https://huggingface.co/mmd-k)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6615494716917dfdc645c44e/M_aMgH5QzSl_hm-srhJwW.webp)](https://huggingface.co/FlameF0X)

xx

tugot17

LiquidAI

Leonie Monigatti

iamleonie

LiquidAI

Fernando Fernandes Neto

fernandofernandes

LiquidAI

Tarek Dakhran

tdakhran

LiquidAI

nathan ranchin

nathanrchn

LiquidAI

Today, we release **DSpark draft model checkpoints** for three models from our LFM2.5 family: LFM2.5-1.2B-Instruct, LFM2.5-2.6B, and LFM2.5-8B-A1B. These add a speculative decoding path that trades a minimal memory increase for a large decoding speedup without changing output quality:

- **Faster inference**: up to 3.18 throughput improvement on a GPU and up to 2.87x on-device.
- **Toward on-device agentic inference**: cuts function-calling latency by 57% on average for LFM2.5-2.6B
- **Day-one support for llama.cpp and SGLang**: LFM-compatible DSpark integration is open-sourced upstream

## How does DSpark work

The decode phase in LLM inference is traditionally memory-bound. Most latency comes from streaming weights from DRAM into SRAM, not from intense computation. Speculative decoding addresses this by using a lightweight draft model to produce candidate tokens, then having the target model verify them all in a single forward pass, sharing the cost of loading the weights across all tokens we verify.

Over the years, multiple approaches of speculation have been proposed, with the most prominent being [EAGLE-3](https://huggingface.co/papers/2503.01840), [DFlash](https://huggingface.co/papers/2602.06036), and, most recently, [DSpark](https://huggingface.co/papers/2607.05147), which combines three components:

- **DFlash-style parallel backbone** conditioned on the target model’s context features, producing hidden states for all draft tokens in a single forward pass.
- **A lightweight sequential head**, modeled as a Markov chain between neighboring tokens, that adds inter-token dependency, raising the acceptance rate at later positions.
- **A confidence-scheduled verifier** that predicts each token’s survival probability and prunes low-confidence suffixes when verification would cost more than it saves.

[![DSpark](https://cdn-uploads.huggingface.co/production/uploads/644249b08443bce4c9890a0f/QSig7XupRwDH70cDopwv2.png)](https://cdn-uploads.huggingface.co/production/uploads/644249b08443bce4c9890a0f/QSig7XupRwDH70cDopwv2.png)

## Training and Architecture

We follow the DSpark recipe with a larger and more diverse data mix covering SFT, chat, code, and function-calling data. Based on our ablations, the first versions of the draft models are simplified attention-only draft models, with 5 layers and a block of 9. For each draft model, we ran 15 epochs on the entire dataset and selected the epoch with the highest acceptance rate rather than the lowest loss.

The resulting draft models are relatively small, with each around ~300M parameters.

| Component | LFM2.5-1.2B-Instruct | LFM2.5-8B-A1B | LFM2.5-2.6B |
| --- | --- | --- | --- |
| Decoder stack (5 layers) | 241.2M | 241.2M | 241.2M |
| Hidden-state projection | 21.0M | 21.0M | 21.0M |
| Markov head | 33.6M | 65.5M | 65.5M |
| Norms + confidence head | 27.5k | 27.5k | 27.5k |
| **Total** | **295.7M** | **327.7M** | **327.7M** |

## Quality parity

Under greedy decoding, a draft token is only accepted if it matches the target model’s distribution. On rejection, the target model's own token takes its place. The emitted sequence is therefore **identical to baseline greedy** by construction, so benchmark accuracy (pass@1 or exact match) is unchanged.

## Inference Speed Up on CPU and GPU

Our DSpark draft models for LFM2.5 ship with day-one support for **llama.cpp** (implementation [builds on top of the official codebase](https://github.com/ggml-org/llama.cpp/pull/27383), which we run with [experimental metal kernels](https://github.com/ggml-org/llama.cpp/pull/27441)) and **SGLang (**implementation [builds on the official SGLang implementation of DSpark](https://github.com/sgl-project/sglang/pull/31041)).

We measure on-device throughput with llama.cpp and Metal on an M4 Max MacBook Pro using FP16 GGUF weights and up to 256 output tokens. We measure GPU throughput with SGLang on a single H100 80 GB in BF16. Both configurations use a DSpark block size of 9, a batch size of 1, and a temperature of 0. We evaluate them on five benchmark datasets.

All three drafter models deliver noticeable throughput improvements on both the large-scale accelerator (H100) and the edge deployment (M4 Max MacBook).

For **LFM2.5-2.6B,** speedup on the MacBook is especially noticeable, as it pushes the interactivity level a user can enjoy far beyond the throughput offered by most proprietary cloud models (around ~140 tok/s, depending on the dataset).

| Dataset | Acceptance (of 10) | Speedup on H100 | Speedup on M4 Max |
| --- | --- | --- | --- |
| MATH500 | 5.42 | **3.06x** 326 → 1000 tok/s | **2.25x** 61 → 137 tok/s |
| HumanEval | 4.54 | **2.56x** 326 → 835 tok/s | **2.63x** 61 → 161 tok/s |
| MBPP | 4.71 | **2.64x** 326 → 861 tok/s | **2.11x** 62 → 132 tok/s |
| GSM8K | 4.32 | **2.22x** 312 → 693 tok/s | **2.36x** 60 → 143 tok/s |
| MT-Bench | 5.07 | **2.87x** 325 → 933 tok/s | **1.99x** 62 → 123 tok/s |
| Mean | 4.81 | **2.67x** 323 → 864 tok/s | **2.27x** 61 → 139 tok/s |

Across various multi-tool scenarios, DSpark reduces the latency by 57% on average for LFM2.5-2.6B.

[![bfcl_latency_mac](https://cdn-uploads.huggingface.co/production/uploads/644249b08443bce4c9890a0f/RTL-W6OBn97nMW7gkkT-e.png)](https://cdn-uploads.huggingface.co/production/uploads/644249b08443bce4c9890a0f/RTL-W6OBn97nMW7gkkT-e.png)

For **LFM2.5-1.2B-Instruct**, we see much more variance in dataset acceptance rates, so speedup varies by as much as 52% depending on the underlying text distribution.

| Dataset | Acceptance (of 10) | Speedup on H100 | Speedup on M4 Max |
| --- | --- | --- | --- |
| MATH500 | 6.02 | **2.56x** 668 → 1712 tok/s | **2.62x** 140 → 366 tok/s |
| HumanEval | 5.31 | **2.26x** 664 → 1499 tok/s | **2.87x** 136 → 389 tok/s |
| MBPP | 5.52 | **2.37x** 667 → 1578 tok/s | **2.74x** 137 → 375 tok/s |
| GSM8K | 4.34 | **1.67x** 624 → 1041 tok/s | **2.73x** 140 → 381 tok/s |
| MT-Bench | 3.90 | **1.66x** 657 → 1091 tok/s | **1.72x** 137 → 237 tok/s |
| Mean | 5.02 | **2.10x** 656 → 1384 tok/s | **2.54x** 138 → 350 tok/s |

For **LFM2.5-8B-A1B**, the acceptance rate increases compared to two dense models, yet on-device we get only an 18% improvement on average. This gap is due to the current MoE implementation in llama.cpp's Metal backend, and to the fact that verifying k tokens activates more experts and thus more weight traffic than a single decode step.

| Dataset | Acceptance (of 10) | Speedup on H100 | Speedup on M4 Max |
| --- | --- | --- | --- |
| MATH500 | 8.27 | **3.18x** 428 → 1362 tok/s | **1.21x** 93 → 112 tok/s |
| HumanEval | 7.02 | **2.58x** 426 → 1100 tok/s | **1.12x** 91 → 101 tok/s |
| MBPP | 6.93 | **2.64x** 426 → 1122 tok/s | **1.09x** 89 → 97 tok/s |
| GSM8K | 4.02 | **1.29x** 385 → 496 tok/s | **1.44x** 90 → 129 tok/s |
| MT-Bench | 8.52 | **3.02x** 426 → 1288 tok/s | **1.04x** 87 → 90 tok/s |
| Mean | 6.95 | **2.54x** 418 → 1074 tok/s | **1.18x** 90 → 106 tok/s |

## How to use LFM2.5-DSpark

Running the DSpark draft models with **SGLang** requires an SGLang build with DSpark support for LFM2 targets ([PR #31041](https://github.com/sgl-project/sglang/pull/31041)). Launch the target with the draft attached:

```
python -m sglang.launch_server \
  --model-path LiquidAI/LFM2.5-2.6B \
  --speculative-algorithm DSPARK \
  --speculative-draft-model-path LiquidAI/LFM2.5-2.6B-DSpark \
  --speculative-draft-attention-backend flashinfer \
  --disable-radix-cache --mem-fraction-static 0.75 --port 30000
```

Then query the OpenAI-compatible endpoint at `http://localhost:30000/v1`. The block size is read from the draft's `config.json`; the baseline is the same command without the three `--speculative-*` flags.

Running them with **llama.cpp** requires the respective llama.cpp build ([PR#27383](https://github.com/ggml-org/llama.cpp/pull/27383)).

```
llama-server -m LFM2.5-2.6B-F16.gguf \
  -md LFM2.5-2.6B-DSpark-F16.gguf \
  --spec-type draft-dspark --spec-draft-n-max 10 --spec-draft-n-min 0 \
  -fa on -ngl 99
```

The block size is read from the sidecar metadata (n-max is clamped to it). Speculative decoding is **exact**: the target verifies every proposed token, so greedy output equals the target alone; per-response `timings` report `draft_n` / `draft_n_accepted`.

## Get Started

The DSpark draft model checkpoints are available on Hugging Face as Safetensors and in GGUF format:

- **Safetensors**: [LFM2.5-2.6B-DSpark](https://huggingface.co/LiquidAI/LFM2.5-2.6B-DSpark), [LFM2.5-1.2B-Instruct-DSpark](https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-DSpark), and [LFM2.5-8B-A1B-DSpark](https://huggingface.co/LiquidAI/LFM2.5-8B-A1B-DSpark)
- **GGUF**: [LFM2.5-2.6B-DSpark-GGUF](https://huggingface.co/LiquidAI/LFM2.5-2.6B-DSpark-GGUF), [LFM2.5-1.2B-Instruct-DSpark-GGUF](https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-DSpark-GGUF), [LFM2.5-8B-A1B-DSpark-GGUF](https://huggingface.co/LiquidAI/LFM2.5-8B-A1B-DSpark-GGUF)

We can’t wait to see what you build.

## Citation

For citations, please use the following reference or BibTeX:

Liquid AI, "LFM2.5-DSpark: Up to 3.2x Faster Inference from H100 to MacBook", Liquid AI Blog, Aug 2026.

```
@article{liquidAI2026dspark,
  author = {Liquid AI},
  title = {LFM2.5-DSpark: Up to 3.2x Faster Inference from H100 to MacBook},
  journal = {Liquid AI Blog},
  year = {2026},
  note = {www.liquid.ai/blog/lfm2.5-dspark},
}
```

## Models mentioned in this article 6

## Papers mentioned in this article 3

More from this author

## Accelerating vision-language models with LFM2.5-VL-DSpark

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/61b8e2ba285851687028d395/EsTgVtnM2IqVRKgPdfqcB.png)

49

September 24, 2026

## LFM2.5 Q4\_0 Checkpoints from Quantization-Aware Distillation

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/61b8e2ba285851687028d395/EsTgVtnM2IqVRKgPdfqcB.png)

37

August 19, 2026

### Community

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2FLiquidAI%2Flfm25-dspark) or [log in](https://huggingface.co/login?next=%2Fblog%2FLiquidAI%2Flfm25-dspark) to comment

Upvote

56

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/646e57a5cb6ea6e6b6df1ad4/PlGhM2SUynFBUdYAylaZK.jpeg)](https://huggingface.co/fernandofernandes)
- [![](https://huggingface.co/avatars/33d508f28166e6a6b449d742fa1f60e0.svg)](https://huggingface.co/mayankagarwal)
- [![](https://huggingface.co/avatars/ee4a89ebc7a0716e21deaebc86e062e6.svg)](https://huggingface.co/nathanrchn)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6317233cc92fd6fee317e030/cJHSvvimr1kqgQfHOjO5n.png)](https://huggingface.co/tomaarsen)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/67379ceb30d6ac7169c5dc99/hQZ-atHUbYkcfjsgQ0ywE.png)](https://huggingface.co/mmd-k)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6615494716917dfdc645c44e/M_aMgH5QzSl_hm-srhJwW.webp)](https://huggingface.co/FlameF0X)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/b3-Xov8BZ4gmTUDOe1wz7.png)](https://huggingface.co/ODanchi-1)
- [![](https://huggingface.co/avatars/5da6b01d9377592f8cd3170d0b700f3e.svg)](https://huggingface.co/ludsvick)
- [![](https://huggingface.co/avatars/473432078df13239e9a48a23ef36d3f4.svg)](https://huggingface.co/mohsendev1)
- [![](https://huggingface.co/avatars/d78a1504df949d46e6e98156cc336e93.svg)](https://huggingface.co/ironwill2000)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/65cc6e71df78d51bb8bd237c/mqHWbwAVTravT8yi0OuOY.png)](https://huggingface.co/tahamajs)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6925170b7498c53accb82dcf/sw8GFcd3_z3oPhqVSi8xq.jpeg)](https://huggingface.co/patraparnab25)

## Models mentioned in this article 6

## Papers mentioned in this article 3
