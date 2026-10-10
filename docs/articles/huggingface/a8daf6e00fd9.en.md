---
vendor: huggingface
title: Kimina-Prover-RL
original_title: Kimina-Prover-RL
url: https://huggingface.co/blog/AI-MO/kimina-prover-rl
date: 2025-07-10
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: a2f6477ab329
---


# Kimina-Prover-RL

Team

Article

					August 14, 2025


17

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/655e4c26d5c0d3db535cdd66/IjYjuy2goiaHG08mFiFmU.jpeg)](https://huggingface.co/Presidentlin)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64146fc68ebec947b8c2fddc/tTTdYhcg5cp2U8LGZustC.png)](https://huggingface.co/dsantosmarco)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/62a3bb1cd0d8c2c2169f0b88/eT2TS0IlQbZtz-F_zHLz9.jpeg)](https://huggingface.co/Tonic)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64b79b422f5a966b9735fa46/3zUZRdWzPnYiZE-Sw567D.png)](https://huggingface.co/ricdomolm)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/641aef7b1911d3be67425338/CmCbWWB6NxkAaus59q31w.jpeg)](https://huggingface.co/purewhite42)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/mnSJ7cP3UfzyA9qkqaRx-.jpeg)](https://huggingface.co/UnluckyOrangutan)

Thibaut Barroyer

thibautbar

AI-MO

Jonas Bayer

TBUGTB

AI-MO

Marina Vinyes

mavi88

AI-MO

Mert Unsal

mertunsal

AI-MO

Haiming Wang

HaimingW

AI-MO

Xiaohan Lin

XiaoHLim

AI-MO

MantasBaksys

MantasBaksys

AI-MO

Junqi Liu

ahhwuhu

AI-MO

Marco Dos Santos

dsantosmarco

AI-MO

Flood Sung

floodsung

AI-MO

Ying

zhenzhe

AI-MO

Zhu Zekai

hehepig166

AI-MO

lujianqiao

rookiemango

AI-MO

Hugues de Saxcé

desaxce

AI-MO

Ebony Zhang

ebony59

AI-MO

Bolton Bailey

BoltonBailey

AI-MO

Frederick Pu

UnluckyOrangutan

AI-MO

Zhengying Liu

evariste-liu

AI-MO

LI Jia

liyongsea

AI-MO

**A slimmed-down training pipeline from Kimina Prover, with core features and full compatibility with verl.**

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/67c7666cd51b75fc80596316/uUzRaw1J4qgQ8wAqPmnQq.png)](https://cdn-uploads.huggingface.co/production/uploads/67c7666cd51b75fc80596316/uUzRaw1J4qgQ8wAqPmnQq.png)

We are happy to introduce kimina-prover-rl, an open-source training pipeline for formal theorem proving in Lean 4, based on a structured reasoning-then-generation paradigm inspired by DeepSeek-R1.

This training pipelinee is a simplified version of the system we used to train [Kimina Prover](https://huggingface.co/blog/AI-MO/kimina-prover), preserving the key components of the system and offering full compatibility with the open-source Verl framework.

It is released as part of a [fork of Verl](https://github.com/project-numina/kimina-prover-rl/tree/main/recipe/kimina_prover_rl) containing the complete training recipe in `recipe/kimina-prover-rl`, allowing anyone to reproduce our experiments or adapt the setup to their own models and datasets. All information to setup and launch the pipeline can be found in the [README](https://github.com/project-numina/kimina-prover-rl/blob/main/recipe/kimina_prover_rl/README.md) of the recipe.

As a result of this training pipeline, we are releasing two models:

- **[AI-MO/Kimina-Prover-RL-1.7B](https://huggingface.co/AI-MO/Kimina-Prover-RL-1.7B)**, a 1.7B-parameter model that achieves **76.63% Pass@32** on the MiniF2F benchmark — setting a new state of the art for open-source models in this size category
- **[AI-MO/Kimina-Prover-RL-0.6B](https://huggingface.co/AI-MO/Kimina-Prover-RL-0.6B)**, a 0.6B-parameter model that achieves **71.30% Pass@32** on the MiniF2F benchmark — also setting a new state of the art for open-source models in this size category.

## Introduction

kimina-prover-rl is a training pipeline designed to teach large language models to solve formal proof goals in Lean 4, using a two-stage output structure: a natural language reasoning trace followed by corresponding Lean code.

This paradigm, inspired by DeepSeek-R1, enables the model to separate planning from execution, promoting explainability, error recovery, and stronger generalization.

To train models under this reasoning framework, we apply GRPO — a reinforcement learning approach tailored for LLMs. This open-source version of the training pipeline of Kimina-prover is implemented using the RL library [Verl](https://github.com/volcengine/verl).

During the rollout phase of GRPO, the model generates N outputs for each prompt. A reward of 1 is assigned to any output whose Lean code is successfully verified by Lean using our [kimina-lean-server](https://github.com/project-numina/kimina-lean-server).

Two main features are added to this framework:

- A format checking reward to teach the model to structure its outputs
- An error correction turn to encourage the model to learn from failure signals

## Kimina-Client

During training, a large number of Lean 4 proof candidates must be verified simultaneously. To handle this efficiently, we require a high-throughput verification system.

To meet this need, Numina and Kimi have developed an open-source server called [kimina-lean-server](https://github.com/project-numina/kimina-lean-server), which supports parallel proof checking at scale using Lean 4.

To simplify integration, we also provide [kimina-client](https://www.piwheels.org/project/kimina-client/), a lightweight Python package (available on PyPI) that offers a clean interface for interacting with the server’s API.

## Dataset

We train using [Kimina-Prover-Promptset](https://huggingface.co/datasets/AI-MO/Kimina-Prover-Promptset), a curated subset of the [NuminaMath-LEAN](https://huggingface.co/datasets/AI-MO/NuminaMath-LEAN) dataset.

For this training setup, we filter and preprocess the dataset as follows:

- **Remove easy problems** with a historical win rate above **0.5** to only keep challenging statements in the dataset.
- **Generate variants** of existing problems to increase diversity using Gemini
- **Duplicate hard problems** to give them more weight during training

The resulting dataset contains challenging, high-value problems for improving Lean 4 theorem proving models.

NuminaMath-LEAN-RL is also the dataset used to train [AI-MO/Kimina-Prover-RL-1.7B](https://huggingface.co/AI-MO/Kimina-Prover-RL-1.7B) and [AI-MO/Kimina-Prover-RL-0.6B](https://huggingface.co/AI-MO/Kimina-Prover-RL-0.6B).

Example input format:

```
Think about and solve the following problems step by step in Lean 4.

# Problem:
Find all primes that are the difference of the fourth powers of two integers.

# Formal Statement:
'''lean4
import Mathlib

theorem number_theory_4487 : {p : ℕ | p.Prime ∧ ∃ a b, p = a ^ 4 - b ^ 4} = ∅ := by
'''
```

## Format reward

The core idea of our reasoning training pipeline is to structure the LLM output into two stages. One thinking block followed by one lean4 block:

- A reasoning block ( ... )
- A Lean 4 code block

```
<think>
To prove the statement, we use induction on n.
The base case is trivial, and the inductive step follows by applying the hypothesis.
</think>

'''lean4
theorem my_thm : ∀ n, f n = g n := by
  induction n with
  | zero => simp
  | succ n ih => simp [ih]
'''
```

Each rollout is **verified** to ensure that this format is respected. If the output is malformed — e.g., missing the `<think>` block or misplacing the code — the model receives a **zero reward**, regardless of whether the proof is actually valid.

This enforces consistency and teaches the model to structure its outputs reliably.

In kimina-prover, these checks go beyond simply verifying the presence of `<think>` and lean4 blocks:

- Ensuring there is exactly one `<think>...</think>` block and one lean4 code block per output.
- Rejecting outputs with repetitive reasoning lines, which often indicate hallucinated or degenerate generations.
- Checking that tactic blocks inside the thinking section are present in sufficient number and contain enough non-comment lines.
- Applying thresholds on comment density (in both reasoning and Lean code), to penalize overly verbose or boilerplate outputs.
- Comparing the semantic alignment between tactics described in blocks and the final Lean code using a matching score (e.g., Intersection-over-Union or subcode coverage).
- Penalize unnecessarily long responses, encouraging the model to use tokens more efficiently while still giving complete replies

Only generations that pass all these checks are considered well-formatted and can receive a reward. This structured filtering improves training stability and encourages clean reasoning.

## Error correction

To make training more informative, we have added an **error correction mechanism** that gives the model a chance to fix its own failed proofs.

When a rollout fails (e.g., due to a Lean error or incorrect proof), we:

- Store the full prompt, response, and Lean feedback.
- Create a **new training sample** where the model is explicitly prompted to revise its previous reasoning/code.

This encourages the model to learn from failure signals as lean feedback is provided during the training.

It also enables multi-turn interaction chains, where feedback from Lean is injected as part of the prompt, and the model is rewarded for successfully debugging its own output.

Because multi-turn responses can get long, we allow only one error-fix turn and cap the error message at a set number of tokens.

## Overview of the pipeline

The work **Understanding R1-Zero-Like Training: A Critical Perspective** claims there's optimization bias in GRPO, that leads to artificially longer responses, especially for incorrect outputs.

We also noticed this behaviour during our experimentations and we used DrGPO for our optimization. DrGRPO aggregates token-level losses by normalizing with a global constant to eliminate length bias.

The configuration file provided in the repository is for a 8 GPUs setup.

The model that we are finetunning is the **[AI-MO/Kimina-Prover-Distill-1.7B](https://huggingface.co/AI-MO/Kimina-Prover-Distill-1.7B)**. This model is a finetuned version of **[Qwen/Qwen3-1.7B](https://huggingface.co/Qwen/Qwen3-1.7B)** with cold start data generated from our **[AI-MO/Kimina-Prover-72B](https://huggingface.co/AI-MO/Kimina-Prover-72B)** model.

At every step, 256 samples are fetched in the training dataset. One out of two is an error correction sample. We generate 8 rollout per samples so 2048 generations. You can increase to 16 or 32 rollouts if you are using more than one node.

We evaluate the model every 5 training steps, using the best@8 metric from verl to have fast validation steps. You can increase to best@16 or 32 if you are using more than one node. We are evaluating the performance before and the after the error correction turn. For each failed reponse we allow the model to do one more tentative to fix its proof.

## Results

After a few training steps, we observe a consistent improvement in performance. In this section we will discuss the training metrics after 48 hours of training on 8 H100 GPUs.

By step 85, the pipeline improves the model's accuracy by 4 points, reaching 70% for the best@8 metric and 74% after the error correction turn:

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/67c7666cd51b75fc80596316/pCXpFDfuoS87AN2iJJ4k7.png)](https://cdn-uploads.huggingface.co/production/uploads/67c7666cd51b75fc80596316/pCXpFDfuoS87AN2iJJ4k7.png)

In parallel, we observe that the number of format errors steadily decreases over the course of training, indicating that the model is learning to produce structurally valid outputs.

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/67c7666cd51b75fc80596316/SfhtLJ7VjGswmc6JRG8w4.png)](https://cdn-uploads.huggingface.co/production/uploads/67c7666cd51b75fc80596316/SfhtLJ7VjGswmc6JRG8w4.png)

Finally, and as expected under the DeepSeek-R1-style training setup, the average token length of the model’s outputs increases with training — a signal that the model is learning to reason in longer, more structured traces.

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/67c7666cd51b75fc80596316/AEavg6sbiAyQzpdYLpqiR.png)](https://cdn-uploads.huggingface.co/production/uploads/67c7666cd51b75fc80596316/AEavg6sbiAyQzpdYLpqiR.png)

After the training, we evaluated the model using pass@32 with and without error fixing. We were able to improve the performances of our 1.7B model by more than 3% at pass@32 on MiniF2F:

| Model | Pass@32 | Pass@32 with error fixing |
| --- | --- | --- |
| AI-MO/Kimina-Prover-Distill-1.7B | 72.95% | 75.41% |
| AI-MO/Kimina-Prover-RL-1.7B | 76.23% | 77.87% |

Using this training pipeline we also finetuned a 0.6B model, improving its performances by more than 2%.

| Model | Pass@32 |
| --- | --- |
| AI-MO/Kimina-Prover-Distill-0.6B | 68.85% |
| AI-MO/Kimina-Prover-RL-0.6B | 71.30% |

## Conclusion

With [Kimina-Prover-RL](https://github.com/project-numina/kimina-prover-rl/tree/main/recipe/kimina_prover_rl), we provide a lightweight yet powerful reinforcement learning pipeline for training Lean 4 theorem provers.

By combining structured reasoning, format rewards, and error correction, we achieve state-of-the-art results for open-source models in the 0.6B–1.7B parameter range.

Alongside the models, we are also releasing a [fork of Verl](https://github.com/project-numina/kimina-prover-rl/blob/main/recipe/kimina_prover_rl) containing the full training recipe in `recipe/kimina-prover-rl`, so the community can reproduce our results or adapt the pipeline to their own datasets and models.

We hope this release will serve as a solid foundation for the community to experiment with RL training in formal reasoning, and to push the limits of open-source automated theorem proving in Lean 4.

## Models mentioned in this article 5

## Datasets mentioned in this article 2

More from this author

## Kimina-Prover: Applying Test-time RL Search on Large Formal Reasoning Models

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/661d3f3e85f70e208d6f20db/kaXbnZDekN1gPzmRG_aFV.png)

56

July 10, 2025

### Community

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2FAI-MO%2Fkimina-prover-rl) or [log in](https://huggingface.co/login?next=%2Fblog%2FAI-MO%2Fkimina-prover-rl) to comment


17

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/655e4c26d5c0d3db535cdd66/IjYjuy2goiaHG08mFiFmU.jpeg)](https://huggingface.co/Presidentlin)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64146fc68ebec947b8c2fddc/tTTdYhcg5cp2U8LGZustC.png)](https://huggingface.co/dsantosmarco)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/62a3bb1cd0d8c2c2169f0b88/eT2TS0IlQbZtz-F_zHLz9.jpeg)](https://huggingface.co/Tonic)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64b79b422f5a966b9735fa46/3zUZRdWzPnYiZE-Sw567D.png)](https://huggingface.co/ricdomolm)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/641aef7b1911d3be67425338/CmCbWWB6NxkAaus59q31w.jpeg)](https://huggingface.co/purewhite42)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/mnSJ7cP3UfzyA9qkqaRx-.jpeg)](https://huggingface.co/UnluckyOrangutan)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/62928e6556fedc76e3971e19/Ye0xR859GTCs3ZTZSvlM3.jpeg)](https://huggingface.co/sorokin)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1669189789447-629f3b18ee05727ce328ccbe.jpeg)](https://huggingface.co/kashif)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/67c7666cd51b75fc80596316/5l5x9PRzLuPwuauN-ZXDW.jpeg)](https://huggingface.co/thibautbar)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/650c5818fb7a51088736587b/u8FIlFoylRB3iSwQaBQQv.jpeg)](https://huggingface.co/desaxce)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/PdtmLEqIkalWWw0tYND6o.jpeg)](https://huggingface.co/TBUGTB)
- [![](https://huggingface.co/avatars/9469599b176034548042922c0afa7051.svg)](https://huggingface.co/dark-pen)

## Models mentioned in this article 5

## Datasets mentioned in this article 2
