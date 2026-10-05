---
vendor: huggingface
title: Open R1: Update #2
original_title: Open R1: Update #2
url: https://huggingface.co/blog/open-r1/update-2
date: 2025-02-06
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: da50c95401ef
---

Back to Articles

# Open R1: Update #2

Team

Article

Published
					February 10, 2025

Upvote

219

- [![](https://huggingface.co/avatars/fc53c381e1b66970cc70fc7a0466cd9d.svg)](https://huggingface.co/ArtinKim)
- [![](https://huggingface.co/avatars/ea98beefcece0fdccc6a3927b75b0e3f.svg)](https://huggingface.co/xdev1206)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/647f36a8454af0237bd49574/jshkqBUTY-GZL8As8y6Aq.jpeg)](https://huggingface.co/fdaudens)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/wFOODuqXJtAYPMa-qn_a1.png)](https://huggingface.co/jessepisel)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/62f1c8517cb1f6642f2fdb8c/fEuKPMj9-w3WYY2Lf5lp9.jpeg)](https://huggingface.co/tuanlda78202)
- [![](https://huggingface.co/avatars/283ddaa5329b6acdf69d965d565e7545.svg)](https://huggingface.co/sinnis)

Loubna Ben Allal

loubnabnl

open-r1

Lewis Tunstall

lewtun

open-r1

Anton Lozhkov

anton-l

open-r1

Elie Bakouch

eliebak

open-r1

Guilherme Penedo

guipenedo

open-r1

Hynek Kydlicek

hynky

open-r1

Gabriel Martín Blázquez

gabrielmbmb

open-r1

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/61c141342aac764ce1654e43/7QROrgiDUrccMrPCmlvwv.png)](https://cdn-uploads.huggingface.co/production/uploads/61c141342aac764ce1654e43/7QROrgiDUrccMrPCmlvwv.png)

We are now two weeks into the [Open R1 project](https://github.com/huggingface/open-r1) which aims to reconstruct the missing pieces of DeepSeek R1—specifically, the training pipeline and synthetic data.

In this post, we are happy to share the construction of [**OpenR1-Math-220k**](https://huggingface.co/datasets/open-r1/openr1-220k-math): our first large-scale dataset for mathematical reasoning!

We also take a look at some exciting developments from the community towards curating small, high-quality datasets for fine-tuning, along with insights into how to control the length of the chain-of-thought from reasoning models at both train-time and inference-time.

Let’s dive in!

## OpenR1-Math-220k dataset

One of the key advantages of DeepSeek R1 is its ability to transfer advanced reasoning capabilities to smaller models through distillation. The DeepSeek team demonstrated this by generating 600k reasoning traces and fine-tuning a series of Qwen and Llama models, showing that direct distillation from R1 can achieve competitive reasoning performance without reinforcement learning. Notably, DeepSeek-R1-Distill-Qwen-7B achieved 55.5% on AIME 2024, surpassing larger models like QwQ-32B-Preview.

However, the reasoning traces used for distillation have not been released publicly, prompting the community to independently recreate similar datasets. So far, multiple open datasets have been released by the community, including [OpenThoughts-114k](https://huggingface.co/datasets/open-thoughts/OpenThoughts-114k), [Bespoke-Stratos-17k](https://huggingface.co/datasets/HuggingFaceH4/Bespoke-Stratos-17k), [Dolphin-R1](https://huggingface.co/datasets/cognitivecomputations/dolphin-r1/viewer/reasoning-deepseek), and [LIMO](https://huggingface.co/datasets/GAIR/LIMO).

🐳 **Introducing OpenR1-Math-220k**, a large-scale **math reasoning dataset** generated locally on 512 H100s, with multiple answers per problem. To create OpenR1-Math-220k, we collaborated with [Numina](https://projectnumina.ai) who have developed a brand new version of their popular [NuminaMath-CoT](https://huggingface.co/datasets/AI-MO/NuminaMath-CoT) dataset.

What’s new in OpenR1 dataset compared to existing datasets:

- **800k R1 reasoning traces**: We generate two answers for 400k problems using [DeepSeek R1](https://huggingface.co/deepseek-ai/DeepSeek-R1). The filtered dataset contains **220k problems** with correct reasoning traces.
- **512 H100s running locally**: Instead of relying on an API, we leverage [vLLM](https://github.com/vllm-project/vllm/) and [SGLang](https://github.com/sgl-project/sglang?) to run generations locally on our science cluster, generating **180k reasoning traces per day**.
- **Based on [NuminaMath 1.5](https://huggingface.co/datasets/AI-MO/NuminaMath-1.5):** we focus on math reasoning traces and generate answers for problems in NuminaMath 1.5, an improved version of the [NuminaMath-CoT](https://huggingface.co/datasets/AI-MO/NuminaMath-CoT) dataset.
- **Automated filtering:** We apply [Math Verify](https://github.com/huggingface/Math-Verify) to only retain problems with at least one correct answer. We also leverage [Llama3.3-70B-Instruct](https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct) as a judge to retrieve more correct examples (e.g for cases with malformed answers that can’t be verified with a rules-based parser)
- **We match the performance of [DeepSeek-Distill-Qwen-7B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B)** by finetuning [Qwen-7B-Math-Instruct](https://huggingface.co/Qwen/Qwen2.5-Math-7B-Instruct) on our dataset.

By demonstrating scalable, high-quality reasoning data generation, we hope this pipeline can be extended beyond math to domains like code generation.

### Data generation

To build OpenR1-220k, we prompt [DeepSeek R1](https://huggingface.co/deepseek-ai/DeepSeek-R1) to generate solutions for 400k problems from NuminaMath 1.5. We follow the model card’s recommended parameters and prepend the following instruction to the user prompt:

"Please reason step by step, and put your final answer within \boxed{}."

We set a 16k token limit per generation, as our analysis showed that only 75% of problems could be solved in under 8k tokens, and most of the remaining problems required the full 16k tokens. Initially, we used vLLM for inference, achieving a throughput of 15 generations per hour per H100, and shared our generation scripts in previous updates and on the OpenR1 [repo](https://github.com/huggingface/open-r1). Recently, we started experimenting with **[SGLang](https://github.com/sgl-project/sglang) and we were able to generate 25 solutions per hour per H100 (almost 2x speedup!)**, enabling us to generate 300k problem solutions per day on 512 H100s. This allowed us to produce 800k reasoning traces in just a few days.

We generate two solutions per problem—and in some cases, four—to provide flexibility in filtering and training. This approach allows for rejection sampling, similar to DeepSeek R1’s methodology, and also makes the dataset suitable for preference optimisation methods like DPO.

The scripts for the data generation are available here: [https://github.com/huggingface/open-r1/tree/main/slurm](https://github.com/huggingface/open-r1/tree/main/slurm)

The unfiltered dataset is available here: [https://huggingface.co/datasets/open-r1/OpenR1-Math-Raw](https://huggingface.co/datasets/open-r1/OpenR1-Math-Raw)

### Data Filtering

To retain only high-quality, correct reasoning traces, we leverage [Math Verify,](https://github.com/huggingface/Math-Verify) a robust mathematical expression evaluation system designed to assess LLM-generated answers. We extract the final answers from model generations and compare them against ground truth answers in the dataset.

We find that 55% of problems have at least one correct answer. However, some ground truth answers in NuminaMath 1.5 were empty or not in a verifiable format, making automatic validation challenging. While we have improved Math-Verify to more accurately handle these more uncommon output formats (see Math-Verify improvements below), we also explored an alternative method to recover valid solutions from rejected samples: using Llama-3.3-70B-Instruct as a judge on a subset of rejected problems. Before running this verification step, we filter out samples that are incomplete or that contain an empty ground truth answer, ensuring that only well-formed responses with a clearly boxed final answer are considered. This process successfully retrieves 28,000 of previously rejected problems.

We prompt **Llama3.3-70B-Instruct** as follows:

```
You are a mathematical answer validator. You will be provided with a mathematical problem and you need to compare the answer in the reference solution, and the final answer in a model's solution to determine if they are equivalent, even if formatted differently.

PROBLEM:

{problem}

REFERENCE SOLUTION:

{answer}

MODEL'S SOLUTION:

{generation}

Focus ONLY on comparing the final mathematical answer provided by the model while ignoring differences in:

- Formatting (e.g., \\boxed{{}} vs plain text)
- Multiple choice formatting (e.g., "A" vs full solution)
- Order of coordinate pairs or solutions
- Equivalent mathematical expressions or notation variations
- If the model's answer is nonsense, return "Verdict: AMBIGUOUS"

Start with a brief explanation of your comparison (2-3 sentences). Then output your final answer in one of the following formats:

- "Verdict: EQUIVALENT"
- "Verdict: DIFFERENT"
- "Verdict: AMBIGUOUS"
```

By combining rule-based verification (Math Verify) with LLM-based evaluation, we improve dataset quality while maintaining scale. The final dataset consists of 220k problems with verified reasoning traces, making it a valuable resource for training reasoning models. Providing multiple solutions per problem gives the community flexibility to filter for better generations and apply more targeted refinements based on NuminaMath data sources and problem types.

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/61c141342aac764ce1654e43/8wY4H7-J_nBmfXDBMHwnJ.png)](https://cdn-uploads.huggingface.co/production/uploads/61c141342aac764ce1654e43/8wY4H7-J_nBmfXDBMHwnJ.png)

The dataset is available in two splits:

- `default` (94k problems), which achieves the best performance after SFT.
- `extended` (131k problems), which includes additional NuminaMath 1.5 sources like `cn_k12`, providing more reasoning traces. However, we observed that performance after SFT on this subset was lower than the default split, likely due to `cn_k12` containing simpler questions compared to other sources.

For rows with multiple correct answers, we also tried applying a Reward Model (RM) as a final filter to select the best response. For each row with multiple correct generations by R1, we extracted the final answer by removing the thinking tokens (`<think>…</think>`), and then pass the problem + the extracted answer to [Qwen/Qwen2.5-Math-RM-72B](https://huggingface.co/Qwen/Qwen2.5-Math-RM-72B) served using vLLM to get an score. Using these scores, we built a ranking for each row containing more than one correct response. The top-1 correct generations were selected and included in the training dataset, but sadly the training ablations showed that this approach doesn’t help to improve model performance with respect to selecting one random correct generation. A possible improvement could be to include the reasoning trace rather than just the final answer when scoring with the RM.

### Performance Comparison with DeepSeek-Distill-Qwen-7B

We fine-tune Qwen2.5-Math-Instruct for 3 epochs on the `default` split of the dataset using a learning rate of 5e-5. To extend the context length from 4k to 32k, we increase RoPE frequency to 300k. The training follows a linear learning rate schedule with a 10% warmup phase. The table below compares the performance of [OpenR1-Qwen-7B](https://huggingface.co/open-r1/OpenR1-Qwen-7B) to [DeepSeek-Distill-Qwen-7B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B) and [OpenThinker-7B](https://huggingface.co/open-thoughts/OpenThinker-7B) using [lighteval](https://github.com/huggingface/open-r1?tab=readme-ov-file#evaluating-models).

| Model | MATH-500 | AIME24 | AIME25 |
| --- | --- | --- | --- |
| DeepSeek-Distill-Qwen-7B | 91.6 | 43.3 | 40 |
| OpenR1-Qwen-7B | 90.6 | 36.7 | 40 |
| OpenThinker-7B | 89.6 | 30.0 | 33.3 |

This dataset represents an initial version, providing a foundation for further refinement. The community can explore additional filtering strategies to improve performance, such as rejection sampling, which was used in DeepSeek R1 to enhance quality.

### Math-Verify improvements

We identified several failure cases in Math-Verify during our inspection of the verification results. To address these issues, we implemented significant improvements and fixes. We strongly recommend updating to the latest version (0.5.2) to benefit from these enhancements:

```
pip install math-verify==0.5.2
```

The following is the summary of the most important improvements:

- Improved parsing and verification of text only answers (e.g $\text{E}$ == $E$)
- Improved parsing of list of answers (e.g $1$ and $2$ and $3$ == $1,2,3$)
- Fixed parsing of multiple boxed answers in single latex env (e.g $\boxed{1},\boxed{2}$ == {1,2})
- Introduction of ordered tuples. Inferring whether the list is a tuple of set is very hard, and we therefore use the gold answer to guide us: (1,2,3) ≠ {3,2,1}; 1,2,3 == {3,2,1}; {3,2,1} == {1,2,3}
- Support for relational (e.g. lower than) in gold and interval in prediction (e.g $1 < x < 2$ == $(1,2)$)

## Community highlights

This week saw the community explore GRPO from many different angles, while multiple research labs have shown that only ~1000 high quality training samples may be sufficient to elicit reasoning in existing open models.

### GRPO in the wild

- nrehiew [showed](https://x.com/nrehiew_/status/1887874867225063543) that applying GRPO directly to the Qwen2.5-0.5B base model yields ~51% accuracy on the GSM8k benchmark, which is a 10 point improvement over the Qwen2.5-0.5B-Instruct model. Impressive results like these have prompted many [discussions](https://x.com/abacaj/status/1888644577604563240) about the role of instruct data in pretraining, as people have not (yet) been able to obtain similar gains when applying GRPO to other base models like Llama 3. In particular, [researchers at Sea AI Lab (SAIL) showed](https://www.notion.so/Open-R1-Update-2-1961384ebcac80efb364e947cec44c91?pvs=21) that base models can be easily prompted to produce self-reflection and that the “aha” moment from the DeepSeek-R1 paper may be more a symptom of the base model than the RL optimisation process.
- Unsloth have applied their [optimisation magic](https://unsloth.ai/blog/r1-reasoning) to enable models up to 15B parameters to be trained with GRPO with just 15GB VRAM 🤯. This means you can now use GRPO in Google Colab for free!
- Wing Lian from [Axolotl](https://github.com/axolotl-ai-cloud/axolotl) has shown that [DoRA converges faster](https://x.com/winglian/status/1888951180606202028) than both LoRA and full-finetuning.
- Alexander Doria found a way to [craft reward functions for poetry](https://x.com/Dorialexander/status/1886176543593894387). This is exciting as it provides one of the first public examples of GRPO being applied to a domain that is not conventionally treated as “verifiable”.

### Evaluation

The first part of the [AIME 2025](https://artofproblemsolving.com/wiki/index.php/2025_AIME_I?srsltid=AfmBOoqknvf_6DwLAOY55UF1k21ilYYaSwo7QWzl9impFvE_XXMpfY7r) was released this week, which consists of 15 difficult math problems that are used to train high school students for the International Math Olympiad. In the past year, AIME 2024 has stood as the main benchmark to probe the mathematical capabilities of LLMs and the community was excited to see how well models performs on a new set of unseen problems:

- Researchers as [ETH Zurich](https://x.com/mbalunovic/status/1887962694659060204) evaluated a range of closed and open models, finding that the [performance drift](https://x.com/9hills/status/1888742869625905536) is far less than expected, typically in the range of 10-20 percentage points.
- However, [Dimitris Papailiopoulos](https://x.com/DimitrisPapail/status/1888325914603516214) found that several of the AIME 2025 problems already existed on internet forums! This may act as a form of accidental train-test leakage, which highlights [how difficult it is to create novel problems](https://x.com/hyhieu226/status/1888653916663132319) for LLMs to solve.

### Do LLMs need to reason in natural language?

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/61c141342aac764ce1654e43/I2Z27QYRjqmF7pbSdFJQc.png)](https://cdn-uploads.huggingface.co/production/uploads/61c141342aac764ce1654e43/I2Z27QYRjqmF7pbSdFJQc.png)

An interesting new [research paper](https://arxiv.org/abs/2502.05171) shows that by using a recurrent language model, it is possible to scale test-time compute by implicitly reasoning in latent space. This resembles [Meta’s Coconut work](https://arxiv.org/abs/2412.06769) to train language models in latent space, but now adapted to reasoning tasks. The advantage of these methods is that they are far more compute efficient: by exploring the latent, one does not need to generate huge amounts of “thinking” tokens to obtain high performance.

### A shift toward smaller, high-quality reasoning data?

While DeepSeek R1 leveraged 600k reasoning traces for distillation, recent work suggests that complex reasoning can emerge in language models not through massive-scale training, but through a small number of carefully curated samples.

One example of this approach is the [s1K](https://huggingface.co/datasets/simplescaling/s1K) dataset. It consists of 1,000 carefully selected math questions with distilled reasoning traces from [Gemini Flash](https://deepmind.google/technologies/gemini/flash-thinking/). The selection approach focuses on difficulty, diversity, and quality. The authors fine-tune Qwen2.5-32B-Instruct on s1K and manage to exceed OpenAI’s o1-preview on competition math benchmarks by up to 27%.

Another dataset, [LIMO](https://huggingface.co/GAIR/LIMO), pushes this idea further, achieving strong performance on AIME and MATH benchmarks using only 817 training samples. The authors hypothesize that when a model has already acquired extensive domain knowledge during pre-training, only a small number of well-structured examples may be needed to unlock advanced reasoning capabilities.

### CoT length: budget forcing & reward shaping

One important ingredient allowing the fine-tuned Qwen2.5-32B-Instruct model from [s1K](https://huggingface.co/datasets/simplescaling/s1K) to reach such strong performance is **budget forcing,** a test-time compute technique that either extends or truncates reasoning by appending “Wait” or an end-of-thinking token delimiter to the model’s generation, respectively. This tool allowed the authors to vary thinking time and conclude that their model exhibits test-time scaling: as thinking time increases, so does accuracy on different math benchmarks.

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/61c141342aac764ce1654e43/C_BAQUuhHUEoEYqQzRBKl.png)](https://cdn-uploads.huggingface.co/production/uploads/61c141342aac764ce1654e43/C_BAQUuhHUEoEYqQzRBKl.png)

Similarly, [Demystifying Long Chain-of-Thought Reasoning in LLMs](https://arxiv.org/abs/2502.03373) (Yeo et al.) also studies the effect of Chain-of-Thought (CoT) length on model performance. They introduce the **Cosine Reward** — a novel reward function that they use to incentivize shorter CoTs for correct generations and longer CoTs for wrong generations — which stabilizes RL training, particularly when the model has relatively limited max context size and average response length could explode. **Repetition penalty** is also employed when the model starts to show signs of reward hacking on hard questions, by artificially increasing CoT length through repetition instead of attempting to solve the problem.

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/61c141342aac764ce1654e43/ed4LVSonlqAxYOfahvtVi.png)](https://cdn-uploads.huggingface.co/production/uploads/61c141342aac764ce1654e43/ed4LVSonlqAxYOfahvtVi.png)

## What’s next?

Now that GRPO is humming in TRL, we are running an extensive set of experiments to understand which hyperparameters and reward functions have the greatest impact on training. You can follow our progress in the [community tab](https://huggingface.co/spaces/open-r1/README/discussions/15) and will write up our findings in the next update!

If you want to contribute check out the [**open-r1 repository on GitHub**](https://github.com/huggingface/open-r1) or follow the [**Hugging Face open-r1 org**](https://huggingface.co/open-r1).

## Models mentioned in this article 8

## Datasets mentioned in this article 7

More from this author

## Open R1: Update #4

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/651e96991b97c9f33d26bde6/QG_uzb2VV3OeKO0c61ynh.png)

50

March 26, 2025

Hot

## Open R1: Update #3

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/651e96991b97c9f33d26bde6/QG_uzb2VV3OeKO0c61ynh.png)

297

March 11, 2025

### Community

Ihor

Feb 10, 2025

Thanks for sharing your results and describing the background of what happened around GRPO research last week. Do you plan to test classical distillation, not just fine-tuning on reasoning traces?

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/651e96991b97c9f33d26bde6/-Bqs6qrmz0yCfwtB2e-6q.jpeg)](https://huggingface.co/eliebak)

·

eliebak

Article author

Feb 10, 2025

•

edited Feb 10, 2025

Yes that's something we might also try!

ryanmarten

Feb 11, 2025

This is awesome! Great work!

chansung

Feb 11, 2025

somewhat ambiguous point:

- with Math Verify, the size of filtered dataset is 220k (55% or 400k)
- with LLM based evaluation, the size of retrieved data from rejected sampling is 28k

But, this article claims as below:

> By combining rule-based verification (Math Verify) with LLM-based evaluation, we improve dataset quality while maintaining scale. The final dataset consists of 220k problems with verified reasoning traces, making it a valuable resource for training reasoning models

I think the size should be 248k? otherwise, it seems like the LLM based evaluation hasn't been included in the final dataset.

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/61c141342aac764ce1654e43/81AwoT5IQ_Xdw0OVw7TKu.jpeg)](https://huggingface.co/loubnabnl)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1613655355830-noauth.png)](https://huggingface.co/anton-l)

·

loubnabnl

Article author

Feb 11, 2025

We only applied Llama verification to the `default` subset, those rejected by Math Verify from the `extended` subset didn't go through a second verification step. We can release the unfiltered data with 400k problems if the community wants to do different filtering.

chansung

Feb 11, 2025

kind of wondering about the following statement

> achieving a throughput of 15 generations per hour per H100

Since DeepSeek-R1 can't fit into a single H100 (and based on [Update #2](https://huggingface.co/blog/open-r1/update-1), the model fits into 8xH100), how do you measure the throughput of H100? maybe 15*8 = 120 by 8xH100?

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/61c141342aac764ce1654e43/81AwoT5IQ_Xdw0OVw7TKu.jpeg)](https://huggingface.co/loubnabnl)

·

loubnabnl

Article author

Feb 11, 2025

•

edited Feb 11, 2025

The model actually fits on two 8xH100 [https://huggingface.co/blog/open-r1/update-1#synthetic-data-generation](https://huggingface.co/blog/open-r1/update-1#synthetic-data-generation)
And the 15 generations per hour per H100 is the throughput on four nodes divided by 32 GPUs (4 to avoid the cache filling up)

buildmine10

Feb 11, 2025

The discussions about SFT in pre training. If I understand correctly, the idea is that models that have pretraining data that contains some instruct data tend to learn to reason while those without any instruct data don't ever figure out how to reason.

zhaochenyang20

Feb 12, 2025

hello, we are the SGLang team from lmsys.org. I am Chenyang, the project manager. Together with a bunch of great people, we are working on integrating SGLang into OpenR1. We have been working on OpenR1 for over a week. And we have done work on distill label, GRPO, and lighteval.

We are planning to submit PRs to you but see that you are also using SGLang in this post:

[https://huggingface.co/blog/open-r1/update-2](https://huggingface.co/blog/open-r1/update-2)

We are reaching out to collaborate so that we both do not waste our time working on the same thing. Thanks!

If you feel interested, can be reached out by [chenyang.zhao@sglang.ai](mailto:chenyang.zhao@sglang.ai)

NickL77

Feb 12, 2025

Would also be nice to include the performance of Qwen2.5-Math-Instruct and Qwen2.5-7B-Instruct to quantify the improvement using reasoning trace SFT distillation.

esheep

Feb 13, 2025

How exactly is the Qwen/Qwen2.5-Math-RM-72B model used? Is it solely for ranking multiple answers? Can it also serve as a tool to validate whether the answers are correct?

phoebus27

Feb 17, 2025

Great work ！I have some questions about the values ​​in the performance comparison table. According to DeepSeek's paper, DeepSeek-Distill-Qwen-7B's performance in MATH-500 and AIME24 is 92.8 and 55.5 respectively, which seems to be very different from the values ​​in the table (especially AIME24). I don't know if there is any gap. Looking forward to your response, thanks

ngxson

Feb 17, 2025

📻 🎙️ Hey, I made a podcast about this blog post, check it out!

*This podcast is generated via [ngxson/kokoro-podcast-generator](https://huggingface.co/spaces/ngxson/kokoro-podcast-generator), using DeepSeek-R1 and Kokoro-TTS*

kaiwenw

Feb 19, 2025

Hi, thanks for the great work! I'm wondering if the data filtering code can be made public? I'm using Math-Verify to double check some of your labels and couldn't reproduce some labels -- it seems that some solutions are not parsed correctly with the default math_verify.parse function. Thank you! cc. [@loubnabnl](https://huggingface.co/loubnabnl)  [@lewtun](https://huggingface.co/lewtun)  [@eliebak](https://huggingface.co/eliebak)

Oasis-0927

Feb 21, 2025

Thanks for this great work. Would you please explain that OpenR1-Qwen-7B is trained through LORA or full-finetune?

tgehr

Feb 26, 2025

•

edited Feb 26, 2025

Thanks a lot for making this available! Note that [https://matharena.ai](https://matharena.ai) is joint work between ETH and INSAIT (not only ETH). Would be good to update this in the text.

chenth

May 30, 2025

Hi, thanks for the impressive work on Open R1!

I had a question about the data processing for SFT. From what I understand, the training uses the default dataset. Since this dataset contains multiple responses per question, I'm curious how the final SFT training data was constructed.

Were all the responses used during training, or was there a filtering step to select only the correct or high-quality answers? Any clarification on this would be greatly appreciated.

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fopen-r1%2Fupdate-2) or [log in](https://huggingface.co/login?next=%2Fblog%2Fopen-r1%2Fupdate-2) to comment

Upvote

219

- [![](https://huggingface.co/avatars/fc53c381e1b66970cc70fc7a0466cd9d.svg)](https://huggingface.co/ArtinKim)
- [![](https://huggingface.co/avatars/ea98beefcece0fdccc6a3927b75b0e3f.svg)](https://huggingface.co/xdev1206)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/647f36a8454af0237bd49574/jshkqBUTY-GZL8As8y6Aq.jpeg)](https://huggingface.co/fdaudens)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/wFOODuqXJtAYPMa-qn_a1.png)](https://huggingface.co/jessepisel)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/62f1c8517cb1f6642f2fdb8c/fEuKPMj9-w3WYY2Lf5lp9.jpeg)](https://huggingface.co/tuanlda78202)
- [![](https://huggingface.co/avatars/283ddaa5329b6acdf69d965d565e7545.svg)](https://huggingface.co/sinnis)
- [![](https://huggingface.co/avatars/d9b707e26f05d9edec708feb44d8c6c8.svg)](https://huggingface.co/why217)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1636035746738-noauth.png)](https://huggingface.co/prohor)
- [![](https://huggingface.co/avatars/efa262dc3d8d871c90b8c77fd09618b5.svg)](https://huggingface.co/rkukrej)
- [![](https://huggingface.co/avatars/3a6b3b952641e9a69992e9657d374231.svg)](https://huggingface.co/drproduck)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/642b7e754f379cdc3de9befc/dGYym9z5vYHRwZpu7ozkh.jpeg)](https://huggingface.co/aipoly)
- [![](https://huggingface.co/avatars/2a1785af3b1b02e495304d2b118accb0.svg)](https://huggingface.co/Shuaiii)

## Models mentioned in this article 8

## Datasets mentioned in this article 7
