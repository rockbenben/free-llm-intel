---
vendor: huggingface
title: Open R1：第二次更新
original_title: "Open R1: Update #2"
url: https://huggingface.co/blog/open-r1/update-2
date: 2025-02-06
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: da50c95401ef
---

# Open R1：第二次更新

作者：Loubna Ben Allal、Lewis Tunstall、Anton Lozhkov、Elie Bakouch、Guilherme Penedo、Hynek Kydlicek、Gabriel Martín Blázquez（open-r1 团队）

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/61c141342aac764ce1654e43/7QROrgiDUrccMrPCmlvwv.png)](https://cdn-uploads.huggingface.co/production/uploads/61c141342aac764ce1654e43/7QROrgiDUrccMrPCmlvwv.png)

[Open R1 项目](https://github.com/huggingface/open-r1)——旨在补齐 DeepSeek R1 缺失的部分（主要是训练流水线与合成数据）——到现在已经推进两周了。

在这篇更新里，很高兴分享 [**OpenR1-Math-220k**](https://huggingface.co/datasets/open-r1/openr1-220k-math) 的构建过程——这是我们第一个大规模数学推理数据集！

我们还会看看社区在"为微调整理小而高质量数据集"方面的一系列振奋人心的进展，以及如何在训练时和推理时控制推理模型思维链长度的洞见。

开始吧！

## OpenR1-Math-220k 数据集

DeepSeek R1 的关键优势之一，是能把高级推理能力通过蒸馏迁移到更小的模型上。DeepSeek 团队通过生成 60 万条推理轨迹、微调一系列 Qwen 和 Llama 模型证明了这一点：直接从 R1 蒸馏无需强化学习也能达到有竞争力的推理水平。值得一提的是，DeepSeek-R1-Distill-Qwen-7B 在 AIME 2024 上拿到 55.5%，超过了 QwQ-32B-Preview 这样更大的模型。

但用于蒸馏的推理轨迹并未公开发布，社区于是着手独立复现类似数据集。目前社区已发布了多个开放数据集，包括 [OpenThoughts-114k](https://huggingface.co/datasets/open-thoughts/OpenThoughts-114k)、[Bespoke-Stratos-17k](https://huggingface.co/datasets/HuggingFaceH4/Bespoke-Stratos-17k)、[Dolphin-R1](https://huggingface.co/datasets/cognitivecomputations/dolphin-r1/viewer/reasoning-deepseek) 和 [LIMO](https://huggingface.co/datasets/GAIR/LIMO)。

🐳 **隆重介绍 OpenR1-Math-220k**：一个大规模**数学推理数据集**，在 512 块 H100 上本地生成，每道题有多个答案。为构建 OpenR1-Math-220k，我们与 [Numina](https://projectnumina.ai) 合作——他们为广受欢迎的 [NuminaMath-CoT](https://huggingface.co/datasets/AI-MO/NuminaMath-CoT) 数据集开发了全新版本。

与现有数据集相比，OpenR1 数据集的新意在于：

- **80 万条 R1 推理轨迹**：我们用 [DeepSeek R1](https://huggingface.co/deepseek-ai/DeepSeek-R1) 对 40 万道题各生成两个答案。过滤后的数据集包含 **22 万道**带正确推理轨迹的题目。
- **512 块 H100 本地运行**：不依赖 API，我们用 [vLLM](https://github.com/vllm-project/vllm/) 和 [SGLang](https://github.com/sgl-project/sglang?) 在科研集群上本地跑生成，**每天生成 18 万条推理轨迹**。
- **基于 [NuminaMath 1.5](https://huggingface.co/datasets/AI-MO/NuminaMath-1.5)**：聚焦数学推理轨迹，对 NuminaMath 1.5（[NuminaMath-CoT](https://huggingface.co/datasets/AI-MO/NuminaMath-CoT) 的改进版）中的题目生成答案。
- **自动化过滤**：应用 [Math Verify](https://github.com/huggingface/Math-Verify) 只保留至少有一个正确答案的题目。我们还让 [Llama3.3-70B-Instruct](https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct) 当裁判，找回更多正确样本（例如答案格式有瑕疵、无法用基于规则的解析器验证的情况）
- **性能与 [DeepSeek-Distill-Qwen-7B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B) 持平**：方法是在我们的数据集上微调 [Qwen-7B-Math-Instruct](https://huggingface.co/Qwen/Qwen2.5-Math-7B-Instruct)。

通过展示可扩展的高质量推理数据生成，我们希望这条流水线未来能从数学扩展到代码生成等领域。

### 数据生成

构建 OpenR1-220k 时，我们提示 [DeepSeek R1](https://huggingface.co/deepseek-ai/DeepSeek-R1) 对 NuminaMath 1.5 的 40 万道题生成解答。参数遵循模型卡的推荐值，并在用户提示前加上这条指令：

"Please reason step by step, and put your final answer within \boxed{}."

每次生成设 16k token 上限。我们的分析显示，只有 75% 的题目能在 8k token 内解决，其余大部分题目需要完整的 16k token。最初我们用 vLLM 推理，吞吐为每块 H100 每小时 15 条生成；生成脚本已在此前的更新和 OpenR1 [仓库](https://github.com/huggingface/open-r1)中分享。最近我们开始试用 **[SGLang](https://github.com/sgl-project/sglang)，每块 H100 每小时能生成 25 条（接近 2 倍加速！）**，使我们在 512 块 H100 上每天能生成 30 万条题目解答。几天之内就产出了 80 万条推理轨迹。

每题生成两个解答（部分情况四个），为过滤和训练提供灵活性。这种做法支持拒绝采样（rejection sampling），与 DeepSeek R1 的方法一致；同时数据集也适合 DPO 这类偏好优化方法。

数据生成脚本在这里：[https://github.com/huggingface/open-r1/tree/main/slurm](https://github.com/huggingface/open-r1/tree/main/slurm)

未过滤数据集在这里：[https://huggingface.co/datasets/open-r1/OpenR1-Math-Raw](https://huggingface.co/datasets/open-r1/OpenR1-Math-Raw)

### 数据过滤

为只保留高质量的正确推理轨迹，我们使用 [Math Verify](https://github.com/huggingface/Math-Verify)——一套稳健的数学表达式求值系统，用于评估 LLM 生成的答案。我们从模型生成中提取最终答案，与数据集中的标准答案比对。

我们发现 55% 的题目至少有一个正确答案。不过 NuminaMath 1.5 中部分标准答案为空或格式不可验证，给自动验证带来困难。我们已经改进 Math-Verify 以更准确地处理这些少见输出格式（见下文 Math-Verify 改进），同时探索了另一种从被拒样本中找回有效解答的方法：用 Llama-3.3-70B-Instruct 对被拒问题的一个子集做裁判。运行这一步验证前，我们先剔除不完整或标准答案为空的样本，只考虑格式规范、有清晰 boxed 最终答案的回答。这一步成功找回了此前被拒的 28,000 道题。

我们按如下方式提示 **Llama3.3-70B-Instruct**：

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

把基于规则的验证（Math Verify）与基于 LLM 的评估结合，我们在保持规模的同时提升了数据集质量。最终数据集由 22 万道具有已验证推理轨迹的题目组成，是训练推理模型的宝贵资源。每题提供多个解答，让社区可以灵活地过滤出更好的生成，并根据 NuminaMath 的数据来源和题型做更有针对性的精炼。

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/61c141342aac764ce1654e43/8wY4H7-J_nBmfXDBMHwnJ.png)](https://cdn-uploads.huggingface.co/production/uploads/61c141342aac764ce1654e43/8wY4H7-J_nBmfXDBMHwnJ.png)

数据集有两个 split：

- `default`（9.4 万题），SFT 后效果最好。
- `extended`（13.1 万题），纳入了更多 NuminaMath 1.5 来源（如 `cn_k12`），提供更多推理轨迹。但我们观察到在该子集上 SFT 后的性能低于 default split，很可能因为 `cn_k12` 的问题相对其他来源更简单。

对于有多个正确答案的行，我们还尝试把奖励模型（RM）作为最终过滤器来挑选最佳回答。对 R1 生成多个正确答案的每一行，我们先去掉思考 token（`<think>…</think>`）提取最终答案，再把题目 + 提取的答案输入用 vLLM 服务的 [Qwen/Qwen2.5-Math-RM-72B](https://huggingface.co/Qwen/Qwen2.5-Math-RM-72B) 取分数。基于这些分数，我们对含多个正确响应的行做排名，把 top-1 正确生成选入训练集。可惜训练消融显示，相比随机选一个正确生成，这种做法并没有提升模型表现。一个可能的改进是：用 RM 打分时纳入整条推理轨迹而不仅是最终答案。

### 与 DeepSeek-Distill-Qwen-7B 的性能对比

我们在数据集的 `default` split 上以 5e-5 学习率微调 Qwen2.5-Math-Instruct 三个 epoch。为把上下文长度从 4k 扩到 32k，将 RoPE 频率调到 300k。训练采用线性学习率调度，含 10% 的 warmup 阶段。下表用 [lighteval](https://github.com/huggingface/open-r1?tab=readme-ov-file#evaluating-models) 比较 [OpenR1-Qwen-7B](https://huggingface.co/open-r1/OpenR1-Qwen-7B) 与 [DeepSeek-Distill-Qwen-7B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B)、[OpenThinker-7B](https://huggingface.co/open-thoughts/OpenThinker-7B) 的表现。

| 模型 | MATH-500 | AIME24 | AIME25 |
| --- | --- | --- | --- |
| DeepSeek-Distill-Qwen-7B | 91.6 | 43.3 | 40 |
| OpenR1-Qwen-7B | 90.6 | 36.7 | 40 |
| OpenThinker-7B | 89.6 | 30.0 | 33.3 |

这个数据集是初始版本，为后续精炼打基础。社区可以探索更多过滤策略来提升表现，例如 DeepSeek R1 用过的拒绝采样。

### Math-Verify 改进

在检查验证结果时，我们发现 Math-Verify 存在若干失败案例。为解决这些问题，我们做了大量改进和修复。强烈建议升级到最新版（0.5.2）以享受这些增强：

```
pip install math-verify==0.5.2
```

以下是最重要的改进摘要：

- 改进纯文本答案的解析与验证（如 $\text{E}$ == $E$）
- 改进答案列表的解析（如 $1$ and $2$ and $3$ == $1,2,3$）
- 修复单个 latex 环境中多个 boxed 答案的解析（如 $\boxed{1},\boxed{2}$ == {1,2}）
- 引入有序元组。判断一个列表是 tuple 还是 set 非常困难，因此我们借用标准答案来指导：(1,2,3) ≠ {3,2,1}；1,2,3 == {3,2,1}；{3,2,1} == {1,2,3}
- 支持标准答案中的关系式（如"小于"）与预测中的区间（如 $1 < x < 2$ == $(1,2)$）

## 社区亮点

这一周，社区从多个角度探索 GRPO；同时多个研究实验室表明：也许只需约 1,000 条高质量训练样本，就能在现有开放模型上激发推理能力。

### GRPO 的实战应用

- nrehiew [展示](https://x.com/nrehiew_/status/1887874867225063543)：直接对 Qwen2.5-0.5B 基座模型应用 GRPO，在 GSM8k 基准上达到约 51% 准确率，比 Qwen2.5-0.5B-Instruct 高 10 个点。这样亮眼的结果引发了关于[预训练中指令数据作用](https://x.com/abacaj/status/1888644577604563240)的许多讨论——人们（暂时）没能在 Llama 3 等其他基座模型上复现同样的收益。特别是，[Sea AI Lab (SAIL) 的研究者表明](https://www.notion.so/Open-R1-Update-2-1961384ebcac80efb364e947cec44c91?pvs=21)：基座模型很容易就能被提示做自我反思，DeepSeek-R1 论文中那个 "aha" 时刻可能更多是基座模型本身的属性，而非 RL 优化过程的功劳。
- Unsloth 把他们的[优化魔法](https://unsloth.ai/blog/r1-reasoning)应用到 GRPO，让多达 15B 参数的模型只需 15GB 显存就能训练 🤯。这意味着你现在可以在 Google Colab 上免费用 GRPO！
- 来自 [Axolotl](https://github.com/axolotl-ai-cloud/axolotl) 的 Wing Lian 展示了 [DoRA 比 LoRA 和全量微调收敛更快](https://x.com/winglian/status/1888951180606202028)。
- Alexander Doria 找到了[为诗歌构造奖励函数](https://x.com/Dorialexander/status/1886176543593894387)的方法。这很令人兴奋——它是最早公开展示 GRPO 用于传统意义上"不可验证"领域的例子之一。

### 评估

[AIME 2025](https://artofproblemsolving.com/wiki/index.php/2025_AIME_I?srsltid=AfmBOoqknvf_6DwLAOY55UF1k21ilYYaSwo7QWzl9impFvE_XXMpfY7r) 第一部分本周发布，包含 15 道高难度数学题——这些题用于训练参加国际数学奥赛的高中生。过去一年，AIME 2024 一直是探测 LLM 数学能力的主要基准，社区也很兴奋想看看模型在一批没见过的题上表现如何：

- [ETH Zurich](https://x.com/mbalunovic/status/1887962694659060204) 的研究者评估了一批闭源和开源模型，发现[性能漂移](https://x.com/9hills/status/1888742869625905536)远小于预期，通常在 10-20 个百分点以内。
- 不过 [Dimitris Papailiopoulos](https://x.com/DimitrisPapail/status/1888325914603516214) 发现 AIME 2025 有多道题早已存在于互联网论坛上！这可能构成一种意外的训练-测试泄漏，也凸显了[为 LLM 出原创题目有多难](https://x.com/hyhieu226/status/1888653916663132319)。

### LLM 必须用自然语言推理吗？

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/61c141342aac764ce1654e43/I2Z27QYRjqmF7pbSdFJQc.png)](https://cdn-uploads.huggingface.co/production/uploads/61c141342aac764ce1654e43/I2Z27QYRjqmF7pbSdFJQc.png)

一篇有趣的新[研究论文](https://arxiv.org/abs/2502.05171)表明：借助循环语言模型，可以在潜在空间（latent space）中隐式推理来扩展测试时算力。这让人联想到 [Meta 的 Coconut 工作](https://arxiv.org/abs/2412.06769)——在潜在空间中训练语言模型——只是现在被改造用于推理任务。这类方法的优势是计算效率高得多：在潜在空间中探索，不需要生成大量"思考"token 就能拿到高性能。

### 转向更小、更高质量的推理数据？

DeepSeek R1 用 60 万条推理轨迹做蒸馏，而近期工作表明：复杂推理未必靠大规模训练涌现，少量精心挑选的样本就可能做到。

[s1K](https://huggingface.co/datasets/simplescaling/s1K) 数据集是这种方法的一个例子。它由 1,000 道精挑细选的数学题组成，推理轨迹蒸馏自 [Gemini Flash](https://deepmind.google/technologies/gemini/flash-thinking/)。选题策略聚焦难度、多样性和质量。作者在 s1K 上微调 Qwen2.5-32B-Instruct，在竞赛数学基准上最多超过 OpenAI 的 o1-preview 27%。

另一个数据集 [LIMO](https://huggingface.co/GAIR/LIMO) 把这一思路推得更远：只用 817 条训练样本就在 AIME 和 MATH 基准上取得强劲表现。作者假设：当模型已在预训练中积累了大量领域知识后，可能只需要少量结构良好的样例就能解锁高级推理能力。

### CoT 长度：预算强制与奖励塑形

让 [s1K](https://huggingface.co/datasets/simplescaling/s1K) 微调的 Qwen2.5-32B-Instruct 达到强劲表现的一个重要成分，是**预算强制（budget forcing）**——一种测试时算力技术：分别通过在模型生成后追加 "Wait" 或思维结束分隔符来延长或截断推理。借助这个工具，作者可以改变思考时长，并得出结论：他们的模型展现了测试时缩放——思考时间越长，各数学基准上的准确率越高。

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/61c141342aac764ce1654e43/C_BAQUuhHUEoEYqQzRBKl.png)](https://cdn-uploads.huggingface.co/production/uploads/61c141342aac764ce1654e43/C_BAQUuhHUEoEYqQzRBKl.png)

类似地，[Demystifying Long Chain-of-Thought Reasoning in LLMs](https://arxiv.org/abs/2502.03373)（Yeo 等）也研究了思维链（CoT）长度对模型性能的影响。他们提出了 **Cosine Reward**——一种新颖的奖励函数：对正确的生成激励更短的 CoT，对错误的生成激励更长的 CoT——从而稳定 RL 训练，尤其当模型的最大上下文长度有限、平均响应长度可能爆炸时。当模型在难题上开始出现 reward hacking 迹象（靠重复来人为拉长 CoT 而不是解题）时，他们还会启用**重复惩罚（repetition penalty）**。

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/61c141342aac764ce1654e43/ed4LVSonlqAxYOfahvtVi.png)](https://cdn-uploads.huggingface.co/production/uploads/61c141342aac764ce1654e43/ed4LVSonlqAxYOfahvtVi.png)

## 接下来？

现在 GRPO 已在 TRL 顺畅运转，我们正在跑一系列大规模实验，弄清哪些超参数和奖励函数对训练影响最大。你可以在[社区 tab](https://huggingface.co/spaces/open-r1/README/discussions/15)跟踪进展，我们将在下次更新中写下发现！

想参与贡献，请看 [**open-r1 的 GitHub 仓库**](https://github.com/huggingface/open-r1)，或关注 [**Hugging Face open-r1 组织**](https://huggingface.co/open-r1)。
