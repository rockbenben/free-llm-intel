---
vendor: huggingface
title: Granite 4.1 LLM：它们是如何构建的
original_title: "Granite 4.1 LLMs: How They’re Built"
url: https://huggingface.co/blog/ibm-granite/granite-4-1
date: 2026-03-17
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Granite 4.1 LLM：它们是如何构建的

*关于 Granite 4.1 LLM 背后的数据工程、预训练、监督微调与强化学习的深入技术解读。*

**作者：** Granite Team, IBM

**太长不看** — Granite 4.1 是一个稠密、仅解码器（decoder-only）的 LLM 家族（3B、8B 和 30B），在约 15T token 上用多阶段预训练流水线训练，包括最长 512K token 的长上下文扩展。模型进一步经过约 410 万条高质量精选样本的监督微调，以及采用 DAPO 损失（[Yu et al., 2025](https://arxiv.org/abs/2503.14476)）的 on-policy GRPO 强化学习打磨。值得注意的是，8B instruct 模型追平甚至超过了上一代 Granite 4.0-H-Small（32B-A9B MoE），尽管它用的是更简单的稠密架构、参数更少。所有 Granite 4.1 模型均以 Apache 2.0 许可证发布。

**链接：**

- [Granite 4.1 HF Collection](https://huggingface.co/collections/ibm-granite/granite-41-language-models)
- [GitHub 仓库](https://github.com/ibm-granite/granite-4.1-language-models)
- [Granite 文档](https://www.ibm.com/granite/docs/)

## 总览

构建高质量的小语言模型，光靠堆算力不够——需要在整个训练过程中严格做数据筛选。对 Granite 4.1，我们把数据质量置于数量之上，在五个预训练阶段中逐步精炼数据配比。我们还用 LLM-as-Judge（大模型当评审）框架进一步精选监督微调数据，并应用多阶段强化学习流水线，系统性地强化模型在数学、代码、指令跟随和通用对话上的表现。

## 模型架构

Granite 4.1 模型采用仅解码器的稠密 transformer 架构。核心设计选择包括 **分组查询注意力（GQA）**、**旋转位置编码（RoPE）**、**SwiGLU 激活**、**RMSNorm** 和**共享输入/输出 embedding**。

| 组件 | 3B Dense | 8B Dense | 30B Dense |
| --- | --- | --- | --- |
| Embedding 维度 | 2560 | 4096 | 4096 |
| 层数 | 40 | 40 | 64 |
| 注意力头维度 | 64 | 128 | 128 |
| 注意力头数 | 40 | 32 | 32 |
| KV 头数 | 8 | 8 | 8 |
| MLP 隐藏层维度 | 8192 | 12800 | 32768 |
| MLP 激活 | SwiGLU | SwiGLU | SwiGLU |
| 位置编码 | RoPE | RoPE | RoPE |

三种规格共享同一套训练流水线和数据策略，只在架构维度上有所不同。

## 预训练

Granite 4.1 在约 15 万亿 token 上从零开始训练，采用五阶段训练策略。阶段 1–2 聚焦基础预训练，阶段 3–4 进行中间训练（mid-training），对越来越高质量的数据做退火，阶段 5 引入长上下文训练，把上下文窗口扩展到 512K token。每个阶段使用不同的数据配比和学习率调度，逐步从宽泛的网络级数据转向更精选、更领域相关的内容。

[![Five-phase pre-training pipeline](https://cdn-uploads.huggingface.co/production/uploads/6658c911e238275ea9efc339/G9mYhWq9PunNVyKzszCUL.png)](https://cdn-uploads.huggingface.co/production/uploads/6658c911e238275ea9efc339/G9mYhWq9PunNVyKzszCUL.png)

***图 2：** 五阶段预训练流水线。阶段 1–2 是预训练，阶段 3–4 是中间训练（高质量数据退火），阶段 5 是长上下文训练（LCE）。*

### 阶段 1：通用预训练（10T token）

第一阶段用通用的训练数据配比，配合幂函数学习率调度和 warmup，建立宽泛的语言理解。

**数据构成：**

- **CommonCrawl** 约 59% — 通用网络数据
- **代码** 约 20% — 编程语言与代码仓库
- **数学** 约 7% — 数学推理数据
- **技术文献** 约 10.5% — 科学论文、技术文档和手册
- **多语言** 约 2% — 非英语语言数据
- **领域特定** 约 1.5% — 特定领域内容

### 阶段 2：数学/代码预训练（2T token）

第二阶段大幅提高代码和数学数据的比例，转向更强的推理能力，同时保持通用语言覆盖。

**数据构成：**

- **数学** 约 35% — 比阶段 1 增加 5 倍
- **代码** 约 30% — 增加 1.5 倍
- **CommonCrawl-HQ** 约 12% — 高质量 Common Crawl 子集
- **合成数据** 约 9% — 合成的高质量数据
- **技术文献** 约 10%
- **多语言** 约 3%
- **领域** 约 1%

### 阶段 3：高质量数据退火（2T token）

第三阶段进入**中间训练**，使用更均衡、更高质量的配比和指数衰减学习率调度。我们从这里开始混入思维链和合成指令数据。

**数据构成：**

- **CommonCrawl-HQ** 约 16.67%
- **数学** 约 16.67%
- **代码** 约 16.67%
- **合成数据** 约 8.5%
- **技术文献** 约 12.5%
- **多语言** 约 4.5%
- **长思维链** 约 12.5% — 推理轨迹
- **语言指令** 约 7.5% — 指令微调数据
- **代码指令** 约 4.5% — 指令微调数据

### 阶段 4：高质量数据退火——精炼（0.5T token）

第四阶段继续中间训练，学习率线性衰减到零，让模型聚焦于可用的最高质量数据。

**数据构成：**

- **CommonCrawl-HQ** 约 40%
- **代码** 约 20%
- **数学** 约 20%
- **长思维链** 约 6%
- **代码指令** 约 5%
- **语言指令** 约 9%

[![Data mix evolution across pre-training phases](https://cdn-uploads.huggingface.co/production/uploads/6658c911e238275ea9efc339/Rrc_DSHSiJs7iNc8Nv8yI.png)](https://cdn-uploads.huggingface.co/production/uploads/6658c911e238275ea9efc339/Rrc_DSHSiJs7iNc8Nv8yI.png)

***图 3：** 数据配比在预训练各阶段中的演变。注意从网络数据为主（阶段 1）逐步转向指令与推理数据为主的质量优先配比（阶段 3–4）。*

### 阶段 5：长上下文训练（LCE）

第五也是最后一个阶段（同样属于中间训练）通过分阶段的长上下文扩展流程，把上下文窗口从 **4K** 扩展到 **512K**：

- **32K 扩展** — 使用与阶段 4 相同的数据配比
- **128K 扩展** — 与阶段 4 相同的数据配比
- **512K 扩展** — 80% 书籍 + 20% 代码仓库数据（仅 8B 和 30B）

LCE 阶段使用从 `1e-4` 起衰减到 `0` 的指数学习率调度。为确保模型原生处理长序列而不劣化短上下文性能，我们在每个 LCE 阶段后做一次模型合并。base 模型的 RULER 基准：

| 模型名 | 32K | 64K | 128K |
| --- | --- | --- | --- |
| **granite-4.1-3b-base** | 75.0 | 66.6 | 58.0 |
| **granite-4.1-8b-base** | 83.6 | 79.1 | 73.0 |
| **granite-4.1-30b-base** | 85.2 | 84.6 | 76.7 |

## SFT：数据准备与质量控制

监督微调（SFT）把 base 模型变成可靠的指令跟随助手，因此数据质量至关重要——哪怕少量错误或幻觉样本也可能灌输不良行为。为此，我们应用严格的 LLM-as-Judge 框架，配合基于规则的过滤来精选高质量样本。整条流水线自动按结构、语义和行为标准评估每条样本，能修的问题就地修复，达不到质量标准的样本则被过滤掉。

[![SFT Data Quality Pipeline](https://cdn-uploads.huggingface.co/production/uploads/6658c911e238275ea9efc339/_-jA1WScOVuIFl20cLEPU.png)](https://cdn-uploads.huggingface.co/production/uploads/6658c911e238275ea9efc339/_-jA1WScOVuIFl20cLEPU.png)

***图 4：** SFT 数据质量流水线。原始对话数据经过带多维度评分标准的 LLM-as-Judge，产出接受/边缘/拒绝的裁定。硬性拒绝类缺陷（幻觉、虚假前提、计算错误）无论得分如何都会触发自动拒绝。*

我们严格的 LLM-as-Judge 框架只评估助手的回答，把系统提示词、用户输入、检索文档和工具输出严格当作上下文信息。这确保评审评估的是模型说了什么，而不是它被要求做什么。在 RAG（检索增强生成）场景中，不以检索上下文为依据的回答会被标记为幻觉；工具调用的输出则对照允许工具集合及其参数 schema 来校验。

我们针对不同 SFT 数据类型使用专门的评审提示词，包括多轮对话、RAG 增强回答、工具调用交互和多语言对话。每条回答在六个加权维度上打分——指令跟随、正确性、完整性、简洁性、自然度和校准（外加可选的批判性思维检查）。样本依据确定性分数阈值被接受、标记为边缘或拒绝；对幻觉、虚假前提、计算错误等严重缺陷，硬性拒绝规则优先于分数。

为补充语义评估，我们应用一条确定性的规则流水线，通过文本规范化、截断与长度过滤、schema 校验和泄漏检测来保证结构完整性。最后一步全局去重确保数据集内唯一。所有过滤和修正动作都可完整审计。

### SFT 训练细节

通过 LLM-as-Judge、规则过滤和全局去重流水线之后，我们在约 **410 万**条高质量样本上微调 base 模型。以下细节适用于全部三种模型规格：

**训练配置：**

| 参数 | 值 |
| --- | --- |
| 算力 | 16 个节点，每节点 4x GB200 |
| Epochs | 3 |
| 学习率 | 5e-6（线性 warmup 3%，约 25K 步线性衰减） |
| 序列长度 | 16,384 token |
| 样本总数 | 约 410 万 |
| 等效 batch size | 每轮 256 条样本（约 420 万 token/轮） |

## 强化学习：多阶段 RL 流水线

SFT 之后，我们应用多阶段强化学习流水线，进一步提升模型在特定领域的能力。我们不做单次 RL，而是运行**多个有针对性的 RL 阶段**，每个阶段优化不同的能力。

### 训练方法

我们使用 **on-policy GRPO（Group Relative Policy Optimization，组相对策略优化）**（[Shao et al., 2024](https://arxiv.org/abs/2402.03300)），配合 **DAPO（解耦裁剪与动态采样策略优化）损失**（[Yu et al., 2025](https://arxiv.org/abs/2503.14476)），相比标准 GRPO 提供更稳定的训练信号。不过由于动态采样的计算开销很大，我们在训练运行中把它关掉了。

#### RL 训练配置

| 参数 | 值 |
| --- | --- |
| 算法 | on-policy GRPO + DAPO 损失 |
| 训练框架 | SkyRL（[NovaSky-AI, 2025](https://github.com/NovaSky-AI/SkyRL)） |
| 每个提示词样本数 | 16 |
| 训练 batch size | 1024 |
| 上下文长度 | 8,192 |

### RL 流水线

[图 10](https://huggingface.co/blog/ibm-granite/granite-4-1#fig-rl-pipeline) 展示我们训练 Granite 4.1 模型的强化学习流水线。经过对各种强化学习配方的大量实验，我们发现这套步骤顺序能在最大限度提升多领域性能的同时，最小化灾难性遗忘。

[![Granite 4.1 Reinforcement Learning Pipeline](https://cdn-uploads.huggingface.co/production/uploads/6658c911e238275ea9efc339/MAieYrC4jTq4xiFUYcqHJ.png)](https://cdn-uploads.huggingface.co/production/uploads/6658c911e238275ea9efc339/MAieYrC4jTq4xiFUYcqHJ.png)

***图 10：** Granite 4.1 强化学习流水线，由四个顺序阶段组成：多领域 RL、RLHF、身份与知识校准 RL、数学 RL。*

#### 多领域 RL

在这个阶段，模型在来自多个领域的统一混合数据上联合训练。因此每次梯度更新都反映全部任务的多样性，从而防止灾难性遗忘、提升整体基准表现，并把任何单一任务上的退化降到最低。

该阶段覆盖的领域包括：

| 领域 | 说明 |
| --- | --- |
| **数学** | 数学推理与计算 |
| **科学** | 科学知识与推理 |
| **逻辑推理** | 演绎与归纳逻辑 |
| **指令跟随（IF）** | 对复杂指令的遵守 |
| **结构化输出** | 结构化数据输出 |
| **Text2SQL** | 数据库查询生成 |
| **时序推理** | 基于时间的逻辑与排序 |
| **通用对话** | 一般对话质量 |
| **上下文内学习** | 从上下文示例中学习 |

在该阶段，我们用 45,504 条唯一提示词训练模型（按全部 Granite 4.1 模型平均），发现学习率 `5e-7`、KL 损失系数 ($\beta$) `0.05` 对多领域强化学习效果最好。

#### RLHF

为了进一步提升模型的助益性和对话能力，我们用多语言标量奖励模型在通用对话提示词上训练模型。与 SFT checkpoint 相比，在 Alpaca-Eval 上观察到平均约 **18.9 分**的提升（三个 Granite 4.1 模型平均）。

为了缓减策略相对已学知识的漂移，本阶段使用保守的学习率 `3e-7` 和更高的 KL 损失系数 $\beta$ `0.09`。RLHF 阶段平均使用 17,920 条唯一提示词。

#### 身份与知识校准 RL

在这个阶段，我们用身份和知识校准提示词对模型训练少量步（约 40 个训练步）。我们观察到这个很小的训练阶段显著改善了模型的自我识别能力。

与 RLHF 阶段类似，学习率用 `3e-7`、KL 损失系数 $\beta$ 用 `0.09`，本阶段使用 1,728 条唯一提示词。

#### 数学 RL

在 RL 训练过程中，我们发现 RLHF 阶段会导致数学基准分数下降（如 GSM8K、DeepMind-Math）。数学 RL 阶段让模型从这次下降中恢复，并在数学基准上超过原始 SFT 表现：GSM8K 平均提升 **约 3.8 分**，DeepMind-Math 平均提升 **约 23.48 分**。本阶段平均使用 13,504 条唯一提示词，并与多领域 RL 阶段一样采用学习率 `5e-7`、KL 损失系数 $\beta$ `0.05`。

<!-- PART2 -->
