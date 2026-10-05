---
vendor: huggingface
title: Kimina-Prover-RL
original_title: Kimina-Prover-RL
url: https://huggingface.co/blog/AI-MO/kimina-prover-rl
date: 2025-07-10
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Kimina-Prover-RL

**从 Kimina Prover 精简而来的训练管线，保留核心功能并完全兼容 verl。**

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/67c7666cd51b75fc80596316/uUzRaw1J4qgQ8wAqPmnQq.png)](https://cdn-uploads.huggingface.co/production/uploads/67c7666cd51b75fc80596316/uUzRaw1J4qgQ8wAqPmnQq.png)

我们很高兴地推出 kimina-prover-rl，一个面向 Lean 4 形式化定理证明的开源训练管线，其核心是受 DeepSeek-R1 启发的「先推理、后生成」结构化范式。

该训练管线是我们用于训练 [Kimina Prover](https://huggingface.co/blog/AI-MO/kimina-prover) 系统的简化版本，保留了系统的关键组件，并与开源 Verl 框架完全兼容。

它作为 [Verl 的一个 fork](https://github.com/project-numina/kimina-prover-rl/tree/main/recipe/kimina_prover_rl) 的一部分发布，完整训练配方位于 `recipe/kimina-prover-rl`，任何人都可以复现我们的实验，或将该配置适配到自己的模型和数据集。搭建与启动管线的所有信息都可以在该配方的 [README](https://github.com/project-numina/kimina-prover-rl/blob/main/recipe/kimina_prover_rl/README.md) 中找到。

基于这条训练管线，我们发布两个模型：

- **[AI-MO/Kimina-Prover-RL-1.7B](https://huggingface.co/AI-MO/Kimina-Prover-RL-1.7B)**：一个 1.7B 参数模型，在 MiniF2F 基准上取得 **76.63% Pass@32**——创下该尺寸区间开源模型的最新纪录
- **[AI-MO/Kimina-Prover-RL-0.6B](https://huggingface.co/AI-MO/Kimina-Prover-RL-0.6B)**：一个 0.6B 参数模型，在 MiniF2F 基准上取得 **71.30% Pass@32**——同样创下该尺寸区间开源模型的最新纪录。

## 引言

kimina-prover-rl 是一条旨在教会大语言模型求解 Lean 4 形式化证明目标的训练管线，采用两阶段输出结构：先给出自然语言推理过程，再给出对应的 Lean 代码。

这种受 DeepSeek-R1 启发的范式使模型能够将规划与执行分离，从而提升可解释性、错误恢复能力和更强的泛化能力。

为了在该推理框架下训练模型，我们采用 GRPO——一种专为 LLM 定制的强化学习方法。Kimina-prover 训练管线的这个开源版本基于 RL 库 [Verl](https://github.com/volcengine/verl) 实现。

在 GRPO 的 rollout 阶段，模型对每个 prompt 生成 N 个输出。只要某个输出中的 Lean 代码能被我们的 [kimina-lean-server](https://github.com/project-numina/kimina-lean-server) 成功验证，该输出就会被赋予 1 的奖励。

在该框架上我们加入了两个主要特性：

- 格式检查奖励，教会模型结构化其输出
- error correction 回合，鼓励模型从失败信号中学习

## Kimina-Client

训练期间需要同时验证大量 Lean 4 证明候选。为了高效处理这一需求，我们需要一个高吞吐量的验证系统。

为满足这一需求，Numina 与 Kimi 联合开发了一个名为 [kimina-lean-server](https://github.com/project-numina/kimina-lean-server) 的开源服务器，支持使用 Lean 4 进行大规模并行证明检查。

为简化集成，我们还提供了 [kimina-client](https://www.piwheels.org/project/kimina-client/)——一个轻量级 Python 包（可在 PyPI 获取），为与服务器 API 交互提供了简洁的接口。

## 数据集

我们使用 [Kimina-Prover-Promptset](https://huggingface.co/datasets/AI-MO/Kimina-Prover-Promptset) 进行训练，它是 [NuminaMath-LEAN](https://huggingface.co/datasets/AI-MO/NuminaMath-LEAN) 数据集的一个精选子集。

在本次训练配置中，我们按如下方式过滤和预处理数据集：

- **移除简单问题**：历史胜率高于 **0.5** 的题目被剔除，只在数据集中保留有挑战性的命题。
- **生成变体**：使用 Gemini 对已有问题生成变体以增加多样性
- **复制困难问题**：让它们在训练中拥有更高权重

由此得到的数据集包含对提升 Lean 4 定理证明模型有价值的高难度问题。

NuminaMath-LEAN-RL 也是训练 [AI-MO/Kimina-Prover-RL-1.7B](https://huggingface.co/AI-MO/Kimina-Prover-RL-1.7B) 和 [AI-MO/Kimina-Prover-RL-0.6B](https://huggingface.co/AI-MO/Kimina-Prover-RL-0.6B) 所使用的数据集。

输入格式示例：

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

## 格式奖励

我们推理训练管线的核心思想是将 LLM 输出组织为两个阶段：一个思考块后跟一个 lean4 块：

- 一个推理块（ ... ）
- 一个 Lean 4 代码块

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

每次 rollout 都会被**校验**，以确保遵循该格式。如果输出格式不合法——例如缺少 `<think>` 块或代码位置错误——无论证明是否真的有效，模型都会获得**零奖励**。

这强制了输出的一致性，教会模型可靠地组织其输出结构。

在 kimina-prover 中，这些检查不止于简单验证 `<think>` 和 lean4 块的存在：

- 确保每个输出中恰好有一个 `<think>...</think>` 块和一个 lean4 代码块。
- 拒绝推理行重复的输出，这类输出往往表明幻觉或退化的生成。
- 检查思考部分中的 tactic 块数量是否足够、是否包含足够的非注释行。
- 对注释密度（推理部分和 Lean 代码均适用）设置阈值，以惩罚过度冗长或模板化的输出。
- 使用匹配分数（例如 Intersection-over-Union 或子代码覆盖率）比较块中描述的 tactic 与最终 Lean 代码之间的语义一致性。
- 惩罚不必要的超长回复，鼓励模型在给出完整回复的同时更高效地使用 token

只有通过全部检查的生成才会被视为格式合格，才可能获得奖励。这种结构化过滤提升了训练稳定性，并促进清晰的推理。

## 错误修正

为了让训练提供更多信息，我们加入了一个**错误修正机制**，让模型有机会修复自己失败的证明。

当一次 rollout 失败时（例如由于 Lean 错误或证明不正确），我们会：

- 存储完整的 prompt、回复以及 Lean 反馈。
- **创建一条新的训练样本**，在其中明确提示模型修订其先前的推理/代码。

由于训练过程中会提供 Lean 反馈，这鼓励模型从失败信号中学习。

它还支持多轮交互链：Lean 的反馈被注入到 prompt 中，模型因成功调试自己的输出而获得奖励。

由于多轮回复可能很长，我们只允许一次错误修复回合，并将错误消息限制在设定的 token 数以内。

## 管线总览

论文 **Understanding R1-Zero-Like Training: A Critical Perspective** 指出 GRPO 存在优化偏差，会导致回复被人为拉长，尤其是对于不正确的输出。

我们在实验中同样观察到了这一行为，并使用 DrGRPO 进行优化。DrGRPO 通过用一个全局常数做归一化来聚合 token 级损失，从而消除长度偏差。

仓库中提供的配置文件针对 8 GPU 配置。

我们微调的模型是 **[AI-MO/Kimina-Prover-Distill-1.7B](https://huggingface.co/AI-MO/Kimina-Prover-Distill-1.7B)**。该模型是 **[Qwen/Qwen3-1.7B](https://huggingface.co/Qwen/Qwen3-1.7B)** 的微调版本，其冷启动数据由我们的 **[AI-MO/Kimina-Prover-72B](https://huggingface.co/AI-MO/Kimina-Prover-72B)** 模型生成。

每一步从训练数据集中取 256 条样本，其中一半是错误修正样本。我们对每条样本生成 8 个 rollout，即 2048 个生成。如果使用多于一台节点，可以将 rollout 数提高到 16 或 32。

我们每 5 个训练步骤评估一次模型，使用 verl 的 best@8 指标以便快速验证。如果使用多于一台节点，可以提高到 best@16 或 32。我们分别在错误修正回合之前和之后评估性能。对于每个失败回复，我们允许模型再做一次尝试来修复其证明。

## 结果

经过若干训练步骤后，我们观察到性能持续提升。本节讨论在 8 块 H100 GPU 上训练 48 小时后的训练指标。

到第 85 步，管线将模型的准确率提升了 4 个点：best@8 指标达到 70%，错误修正回合后达到 74%：

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/67c7666cd51b75fc80596316/pCXpFDfuoS87AN2iJJ4k7.png)](https://cdn-uploads.huggingface.co/production/uploads/67c7666cd51b75fc80596316/pCXpFDfuoS87AN2iJJ4k7.png)

与此同时，我们观察到格式错误的数量在整个训练过程中稳步下降，表明模型正在学习产出结构合法的输出。

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/67c7666cd51b75fc80596316/SfhtLJ7VjGswmc6JRG8w4.png)](https://cdn-uploads.huggingface.co/production/uploads/67c7666cd51b75fc80596316/SfhtLJ7VjGswmc6JRG8w4.png)

最后，正如 DeepSeek-R1 风格训练配置下的预期那样，模型输出的平均 token 长度随训练增加——这是模型学会用更长、更结构化的推理链进行推理的信号。

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/67c7666cd51b75fc80596316/AEavg6sbiAyQzpdYLpqiR.png)](https://cdn-uploads.huggingface.co/production/uploads/67c7666cd51b75fc80596316/AEavg6sbiAyQzpdYLpqiR.png)

训练结束后，我们在有无错误修正两种情况下用 pass@32 评估模型。在 MiniF2F 上，我们成功将 1.7B 模型在 pass@32 上的表现提升了 3% 以上：

| Model | Pass@32 | Pass@32 with error fixing |
| --- | --- | --- |
| AI-MO/Kimina-Prover-Distill-1.7B | 72.95% | 75.41% |
| AI-MO/Kimina-Prover-RL-1.7B | 76.23% | 77.87% |

利用这条训练管线，我们还微调了一个 0.6B 模型，将其表现提升了 2% 以上。

| Model | Pass@32 |
| --- | --- |
| AI-MO/Kimina-Prover-Distill-0.6B | 68.85% |
| AI-MO/Kimina-Prover-RL-0.6B | 71.30% |

## 结论

通过 [Kimina-Prover-RL](https://github.com/project-numina/kimina-prover-rl/tree/main/recipe/kimina_prover_rl)，我们提供了一条轻量而强大的强化学习管线，用于训练 Lean 4 定理证明器。

通过结合结构化推理、格式奖励与错误修正，我们在 0.6B–1.7B 参数区间取得了开源模型的最先进结果。

除了模型之外，我们还发布了 [Verl 的一个 fork](https://github.com/project-numina/kimina-prover-rl/blob/main/recipe/kimina_prover_rl)，其完整训练配方位于 `recipe/kimina-prover-rl`，社区既可以复现我们的结果，也可以将该管线适配到自己的数据集和模型。

我们希望这次发布能成为社区的坚实基础，帮助大家尝试形式化推理中的 RL 训练， 推动开源 Lean 4 自动定理证明的边界。
