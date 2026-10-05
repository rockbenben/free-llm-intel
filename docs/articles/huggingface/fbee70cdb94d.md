---
vendor: huggingface
title: 用 3C3H 重新思考 LLM 评估：AraGen 基准与排行榜
original_title: Rethinking LLM Evaluation with 3C3H: AraGen Benchmark and Leaderboard
url: https://huggingface.co/blog/leaderboard-3c3h-aragen
date: 2024-12-04
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 16962d013e36
---

返回文章列表

# 用 3C3H 重新思考 LLM 评估：AraGen 基准与排行榜

发布于
					2024 年 12 月 4 日

在 GitHub 上更新

点赞

39

- [![](https://huggingface.co/avatars/dd41593a55d1bec4f1a3a54fca35e646.svg)](https://huggingface.co/SamujjwalIIAI)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/628e39f4b1596566033b8d7b/-Y807up1cgMmAQsczdOPn.jpeg)](https://huggingface.co/cchristophe)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63d7acf73130cadcaf827e84/5dbueSbBbcN1NvAYznMq0.jpeg)](https://huggingface.co/karimouda)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/638eb5f949de7ae552dd6211/mJkQJGpn9tXV37N2VLFCh.jpeg)](https://huggingface.co/derek-thomas)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/jJMt0ulikjBDFPtLFUdUq.png)](https://huggingface.co/chYassine)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1628885133347-6116d0584ef9fdfbf45dc4d9.jpeg)](https://huggingface.co/MohamedRashad)

Ali El Filali

alielfilali01

inceptionai

Neha Sengupta

neha1710

inceptionai

Abouelseoud

Arwa88

inceptionai

Preslav Nakov

preslavnakov

MBZUAI

Clémentine Fourrier

clefourrier

在大语言模型（LLM）快速演进的版图中，全面而稳健的评估方法始终是一个关键挑战，对低资源语言尤其如此。在这篇博客中，我们推出 AraGen——一个面向阿拉伯语 LLM 的生成任务基准与排行榜，它基于 3C3H（一种新的自然语言生成评估度量），我们希望对其他语言的同类工作也能有所启发。

AraGen 排行榜做出三项关键贡献：

- **3C3H 度量**：3C3H 度量给模型的回答打分，是这个框架的核心。它是一种整体性方法，基于 LLM-as-judge（用大模型当裁判）从多个维度评估模型回答——**正确性（Correctness）、完整性（Completeness）、简洁性（Conciseness）、有用性（Helpfulness）、诚实性（Honesty）和无害性（Harmlessness）**。
- **动态评估**：AraGen 排行榜采用动态评估策略，包含三个月的盲测周期，数据集和评估代码在周期内保持私有，在周期结束时公开发布，并替换为一个新的私有基准。
- **阿拉伯语评估数据集**：AraGen 基准提供了一份精心构建的阿拉伯语 LLM 评估数据集，结合多轮和单轮场景，在多个领域和任务上检验模型能力。

我们相信 AraGen 凭借其动态评估方法解决了数据污染这一长期问题，保住了基准的完整性。它还是一个可扩展、语言无关框架的首个应用，用于细致而公平的模型评估，这代表着理解不同语言语境下 LLM 性能的一项重要努力，为全面的模型基准测试树立了新标准。

## 概述

评估大语言模型（LLM）是 AI 研究的一个关键挑战。虽然现有方法增进了我们对 LLM 能力的理解，但它们往往无法全面兼顾 **真实性（factuality）**——评估模型的核心知识——和 **可用性（usability）**——即与人类（终端用户）预期的对齐。当前的评估方法大体可分为基于知识或真实性的基准，以及基于偏好的基准。

**自动基准** 聚焦于评估基础知识和事实正确性。例如，Hugging Face 的 [Open LLM Leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard) 等计划评估给定提示（问题）各选项的可能性，并把最可能的输出与一个金标准参考选项做比较。这些基准在测试核心知识方面很有效，但对模型在面向用户的实际场景中表现如何提供的洞见有限，把可用性的关键方面留在了盲区。

相比之下，**基于偏好的基准** 旨在捕捉与用户偏好的对齐。例如 LMSYS 的 [Chatbot Arena](https://arena.lmsys.org/) 和 AtlaAI 的 [Judge Arena](https://huggingface.co/spaces/AtlaAI/judge-arena)，它们主要依赖对输出的主观评估，基于风格、语气和整体效用。然而这些方法有把风格对齐置于事实准确之上的风险，可能把评估偏向风格讨喜却不够准确的回答。此外，众包竞技场会反映其标注者的偏见，而标注者可能缺乏强有力的投票指引，进一步影响评估的一致性和可靠性。

为解决这些局限，我们提出一种新的评估度量，目标是 **把两种方法结合起来**，为评估语言模型提供一套全面的机制。它评估模型输出的两个关键方面：

- **真实性**：模型输出的准确度与正确性，反映其核心知识。
- **可用性**：模型输出与人类偏好的对齐程度，确保以用户为中心的评估。

这通过引入一种基于 LLM-as-a-Judge 方法的新评估度量来实现（[关于此方法的更多信息见这里](https://github.com/huggingface/evaluation-guidebook/blob/main/contents/model-as-a-judge/basics.md)），它用建模真实性与可用性的六个维度来评估模型表现。通过采取平衡的视角，我们确保可用性不以牺牲事实准确为代价，反之亦然。

## AraGen：面向阿拉伯语 LLM 的生成式基准与排行榜

**AraGen 排行榜** 对开源和专有模型一同排名，使用我们下面引入的新 **3C3H** 度量在 **AraGen 基准** 上做评估。3C3H 为评估大语言模型的事实准确性和可用性提供了一个全面框架。我们选择阿拉伯语作为该框架的首个应用，契合 Inception 为阿拉伯语及更广泛的全球南方普及 AI 的使命，同时应对这些语言和地区缺乏稳健生成基准的问题，也希望看到这项工作扩展到许多其他语言。

排行榜是动态的，评估数据集保持私有（盲测）三个月以确保公平无偏的评估。此后，数据集和对应的评估代码会公开发布，同时引入下一个评估周期的新数据集，而新数据集同样保持私有三个月。这种迭代过程确保评估保持前沿，模型持续在全新的、未见过的数据上被测试。

我们相信这种动态方法既有益又稳健，因为它缓解数据泄漏、鼓励持续的模型改进，并在快速演进的 LLM 开发版图中维持基准的相关性。

## AraGen 排行榜

### 评估流水线

AraGen 评估流水线旨在确保稳健、可复现、可扩展的评估。流程包括以下步骤：

- **模型提交**：用户提交一个模型用于评估。
- **响应生成**：我们用模型对一组固定的、经人工验证的问题（AraGen 基准）生成回答。
- **LLM 当裁判**：一个选定的 LLM（见第 2 节）对生成的答案与预先验证的真值答案做评估。裁判的评估以 **3C3H** 为指引，并在其推理部分之后、回复末尾以 `json` 格式返回分数。
- **打分与归一化**：先确定二值分数（正确性与完整性），只有正确的答案才被进一步评估其他维度。缩放分数（如有用性、诚实性）最初在 [1, 5] 区间打分，后被归一化到 [0, 1] 区间。
- **排行榜报告**：结果展示在两个排行榜上：**3C3H 排行榜**：给出一个整体分数，基于 **3C3H** 分数的六个维度（**正确性、完整性、简洁性、有用性、诚实性和无害性**）对所有答案做整体评估，并分别报告每一项的分数。**任务排行榜**：报告我们聚焦的四项独立任务的 3C3H 分数：问答、推理、正字法与语法分析、安全。

### 3C3H：我们面向 LLM 的新评估度量

我们的主要贡献是 **3C3H** 度量，它用一个 LLM 裁判在六个维度上评估模型表现。

- **正确性（0 或 1）**：回答相对于真值是否在事实上准确？
- **完整性（0 或 1）**：回答是否顾及了问题的所有部分？
- **简洁性（1 到 5）**：回答是否在保留所有必要信息和细节的同时恰当地简短？
- **有用性（1 到 5）**：回答是否有效地帮助或告知了用户？
- **诚实性（1 到 5）**：回答中的所有信息是否准确且没有幻觉？这个度量与上面第一个维度（正确性）类似，但它在更细的尺度上评估回答中附带包含的额外信息的准确性。
- **无害性（1 到 5）**：回答是否不含冒犯性或偏见内容？

评估过程包含以下要素：

- **系统提示**：一个详细的系统提示定义了裁判 LLM 的评估规则和打分标准，包括如何为每个维度打分、以及如何以 JSON 格式生成结构化评分的输出。
- **用户提示**：用户提示由数据集中一个问题及其 **真值答案**（正确答案，经人工验证）、**模型生成的答案**（待评估）配对组成。
- **单次评估**：对每个问题，裁判评估模型的回答一次，在单次评估中给出六个分数（每个标准一个）。**归零规则** 确保如果回答在事实上不正确（`Correct = 0`），其他所有维度都被评为 `0`。
- **输出格式**：裁判先给出其分数的详细解释，然后给出可解析的 JSON 格式结果，确保清晰。

#### 打分与归一化

- 二值分数（正确性与完整性）先计算。如果回答是 **不正确（0）**，其他所有维度自动置零，以免给有缺陷的输出加分。
- 缩放分数（如简洁性、有用性……）。其余四个维度是 1 到 5 的分数，随后为了一致性归一化到 [0, 1]。例如，**诚实性** 得分为 3 会被归一化为 3−14=0.5 \frac{3 - 1}{4} = 0.5 43−1​=0.5。

#### 计算 3C3H 分数

给定每个维度的单独分数，3C3H 度量按如下方式计算：

3C3H=16n∑i=1nc1i(1+c2i+c3i−14+h1i−14+h2i−14+h3i−14) 3C3H = \frac{1}{6n} \sum_{i=1}^{n} c_{1i} \left(1 + c_{2i} + \frac{c_{3i} - 1}{4} + \frac{h_{1i} - 1}{4} + \frac{h_{2i} - 1}{4} + \frac{h_{3i} - 1}{4}\right) 3C3H=6n1​i=1∑n​c1i​(1+c2i​+4c3i​−1​+4h1i​−1​+4h2i​−1​+4h3i​−1​)

其中 n n n 是数据集样本数，c1i c_{1i} c1i​ 是样本 i i i 的正确性分数，c2i c_{2i} c2i​ 是样本 i i i 的完整性分数，c3i c_{3i} c3i​、h1i h_{1i} h1i​、h2i h_{2i} h2i​、h3i h_{3i} h3i​ 分别是样本 i i i 的简洁性、有用性、诚实性和无害性分数。

### 为稳健性而设的动态排行榜

为了确保可靠而公平的评估过程，**AraGen 排行榜** 引入 **动态** 评估策略，旨在应对数据污染风险，同时把透明度、可复现性和持续相关性放在首位。具体保证方式如下：

- **盲测集**：
每个测试集保持私有 **3 个月的评估期**。在这一阶段，测试集用于评估提交的模型，而不存在泄漏进训练数据集的风险，从而确保无偏结果。
- **周期性更新**：
三个月后，盲测集被替换为新一组 **经人工验证的问答对**。这确保评估保持稳健、自适应并与演进中的模型能力对齐。新测试集的设计要维持在 **结构** 上的一致：保留交互的类型和格式；**复杂度**：确保批次间至少可比或递增的难度；**分布**：平衡领域、任务和场景的表示。
- **为可复现而开源**：
在盲测评估期之后，基准数据集将连同评估所用代码一同公开发布。这使得 **独立验证**：研究人员可复现结果并验证基准完整性。**开源**：开放获取促进研究社区内的讨论与改进。

### 数据集设计

AraGen 基准包含 279 道定制的、主要经人工验证的问题，旨在严格测试模型在四类多样任务上的能力：

- **问答**：测试与阿拉伯及阿拉伯世界相关的不同主题的事实准确性和核心知识。
- **正字法与语法分析**：在结构层面评估阿拉伯语理解和语法错误的检测/纠正。
- **推理**：挑战模型进行推断、演绎和逻辑推理。
- **安全**：评估产生不含有害或偏见内容的回答的能力，或避免服从用户的有害请求的能力。

图 1：任务百分比分布

图 2：问答（QA）的类别分布

图 3：推理的类别分布

对于"正字法与语法分析"任务，数据在两个子类别之间均匀分布："阿拉伯语语法"和"阿拉伯语听写语法"，各占 50% 的样本。在"安全"任务中，所有数据都仅属于"安全"类别/子类别。

#### 交互类别

数据集样本被组织为三种交互类型：

- **单次交互**：简单的问答格式，模型必须给出一个单一、完整的回答。
- **对话式交互**：多轮交流，模型必须维持对话的流畅与连贯。模型基于它对交流中最后一个问题的回答被评估，展示其参与自然对话的能力。例如：**用户**："法国首都是哪里？" **助手**："巴黎。" **用户**："它还有哪个别称？" **助手**："巴黎常被称为光之城，这得益于它在启蒙运动时期的角色以及它较早采用街道照明。"
这里，模型基于它对最后一个问题的回答被评估，同时考虑交流的流畅性。
- **跟进式交互**：一段要求两个相关回答之间连续性和事实性的序列。模型的第二个回答依赖于它的第一个答案，打分强调初始回答的重要性。例如：**用户**："德国的首都是哪里？" **助手**："柏林。" **用户**："那里人口多少？" **助手**："柏林人口约 370 万。"
如果第一个回答错了（例如"慕尼黑"），第二个回答就会级联出错，除非它自我纠正，而这很少见。这种交互测试模型维持事实连续性并逻辑地在其先前回答之上构建的能力。

#### 跟进式交互的加权系统

在给涉及跟进式交互的模型表现打分时，对话中第一个回答的分数被赋予更高权重，因为它更有潜力左右对话走向。错误的初始答案会导致级联错误。

- **第一个答案** 被赋予系数 2。
- **第二个答案** 被赋予系数 1。

例如，即使第一个回答错误而第二个回答正确（这出乎意料，考虑到我们问题的设计以及这些系统通常的工作方式），该交互的平均分也会是 0×2+1×13=0.333 \frac{0 \times 2 + 1 \times 1}{3} = 0.333 30×2+1×1​=0.333，反映初始答案的关键性。

## 裁判评估与选择

为 **AraGen 排行榜** 选择最优裁判是确保可靠、无偏、一致评估的关键步骤。本节详述为评估潜在裁判而做的实验，包括单模型和陪审团系统，并基于严谨的实证分析论证最终选择。

#### 所考虑的裁判：

评估了以下裁判候选：

- **GPT-4o**：一个稳健的专有模型，具有良好的对齐潜力；
- **GPT-4o-mini**：GPT-4o 的低成本变体，要求轻量；
- **Claude-3.5-sonnet**：根据多个基准和排行榜的最先进专有模型；
- **Claude-3-haiku**：Claude-3.5-sonnet 的较弱但低成本的变体；
- **Llama 3.1-405b**：提供最完整透明度和控制的最先进开放模型。

我们还尝试采用一个 **[陪审团](https://arxiv.org/abs/2404.18796)**，它聚合多个 LLM 裁判的评估，以检验集体打分是否提升可靠性。

注意，在我们做实验的时候，Claude-3.5-haiku 尚未通过 Anthropic API 提供。

#### 评估目标

为了评估并选择最佳裁判，我们从四个维度考察候选：

- **与人类裁判的一致度**：测量 **Cohen's Kappa 分数** 以评估与人类评估的一致度。
- **分数一致性分析**：裁判分数在多次评估运行中的稳定程度。
- **自我偏见分析**：衡量裁判表现出的自我偏好打分程度。
- **幻觉分析**：验证裁判是否倾向于产生幻觉、不遵循评估指引。

### 与人类裁判的一致度

我们用 **Cohen's Kappa（κ）系数** 测量裁判之间的评估（分数）一致度。结果在下面的热力图中可视化：

图 4：表示裁判之间在 3C3H 分数上一致度的 Cohen's Kappa 热力图

#### 关键观察

- **GPT-4o-mini** 与人类裁判取得最高一致度，κ 分数为 **0.46**，**Claude-3.5-sonnet** 紧随其后；
- **GPT-4o** 表现出合理的对齐，一致度略低于 GPT-4o-mini 和 Claude-3.5-sonnet；
- **Claude-3-haiku** 与人类评估表现出极少的一致度（kappa 分数：**0.06**），使其不适合作为裁判。因此我们决定把它从剩余实验中剔除；
- **Llama 3.1-405b** 表现出中等一致度，但落后于专有模型。

### 分数一致性分析

为评估分数的一致性，我们对每个裁判在相同模型回答上的三次评估运行计算 **分数的标准差**。标准差越低表示越稳定。

#### 结果

| 裁判 | 平均标准差 |
| --- | --- |
| 陪审团 | **0.0049** |
| Claude-3.5-sonnet | **0.0063** |
| Llama 3.1-405b | 0.0092 |
| GPT-4o | 0.0287 |
| GPT-4o-mini | 0.0436 |

#### 关键观察

- **陪审团系统** 整体最稳定，分数的平均标准差为（**0.0049**）。
- **Claude-3.5-sonnet** 是单裁判中最一致的，标准差为 **0.0063**。
- **GPT-4o-mini** 虽然低成本，但表现出更高的波动（**0.0436**），相比 Claude-3.5-sonnet 限制了它在需要极强一致性场景下的适用性。

更详细的分数

#### 裁判：gpt-4o-mini

| 模型名 | Run_1 | Run_2 | Run_3 | 平均分 | 标准差 |
| --- | --- | --- | --- | --- | --- |
| CohereForAI/aya-expanse-8b | 0.8750 | 0.8438 | 0.8542 | 0.857667 | 0.012971 |
| FreedomIntelligence/AceGPT-v2-8B-Chat | 0.6932 | 0.5521 | 0.4917 | 0.579000 | 0.084432 |
| inceptionai/jais-family-30b-8k-chat | 0.6562 | 0.6208 | 0.5746 | 0.617200 | 0.033410 |

## **裁判 gpt-4o-mini 的平均标准差**：0.043604

#### 裁判：gpt-4o

| 模型名 | Run_1 | Run_2 | Run_3 | 平均分 | 标准差 |
| --- | --- | --- | --- | --- | --- |
| CohereForAI/aya-expanse-8b | 0.8681 | 0.8229 | 0.8104 | 0.833800 | 0.024785 |
| FreedomIntelligence/AceGPT-v2-8B-Chat | 0.7917 | 0.7354 | 0.7313 | 0.752800 | 0.027557 |
| inceptionai/jais-family-30b-8k-chat | 0.8042 | 0.7604 | 0.7215 | 0.762033 | 0.033782 |

## **裁判 gpt-4o 的平均标准差**：0.02870

#### 裁判：claude-3.5-sonnet

| 模型名 | Run_1 | Run_2 | Run_3 | 平均分 | 标准差 |
| --- | --- | --- | --- | --- | --- |
| CohereForAI/aya-expanse-8b | 0.8333 | 0.8354 | 0.8354 | 0.834700 | 0.000990 |
| FreedomIntelligence/AceGPT-v2-8B-Chat | 0.7879 | 0.7833 | 0.7812 | 0.784133 | 0.002798 |
| inceptionai/jais-family-30b-8k-chat | 0.7750 | 0.7750 | 0.8070 | 0.785667 | 0.015085 |

## **裁判 claude-3.5-sonnet 的平均标准差**：0.00629

#### 裁判：llama3.1-405b

| 模型名 | Run_1 | Run_2 | Run_3 | 平均分 | 标准差 |
| --- | --- | --- | --- | --- | --- |
| CohereForAI/aya-expanse-8b | 0.9167 | 0.9167 | 0.9188 | 0.917400 | 0.000990 |
| FreedomIntelligence/AceGPT-v2-8B-Chat | 0.6477 | 0.6188 | 0.6021 | 0.622867 | 0.018837 |
| inceptionai/jais-family-30b-8k-chat | 0.7563 | 0.7750 | 0.7654 | 0.765567 | 0.007635 |

## **裁判 llama3.1-405b 的平均标准差**：0.00915

#### 裁判：陪审团

| 模型名 | Run_1 | Run_2 | Run_3 | 平均分 | 标准差 |
| --- | --- | --- | --- | --- | --- |
| CohereForAI/aya-expanse-8b | 0.8819 | 0.8832 | 0.8832 | 0.882767 | 0.000613 |
| FreedomIntelligence/AceGPT-v2-8B-Chat | 0.7953 | 0.7697 | 0.7789 | 0.781300 | 0.010588 |
| inceptionai/jais-family-30b-8k-chat | 0.7907 | 0.7830 | 0.7837 | 0.785800 | 0.003477 |

## **裁判 陪审团 的平均标准差**：0.00489

### 自我偏见分析

正如 [这项研究](https://arxiv.org/pdf/2404.13076) 以及其他若干研究报道的那样，通常当一个大型语言模型同时充当评估者和被评估者时，会引入某些偏见。为分析自我偏见，我们比较了裁判如何给自己的回答与他人的回答打分。下表总结了结果：

| 模型名 | GPT-4o-mini | Claude-3.5-sonnet | Llama 3.1-405b | GPT-4o |
| --- | --- | --- | --- | --- |
| Claude-3.5-sonnet-20241022 | 0.8532 | 0.8432 | 0.8244 | 0.8442 |
| Meta-Llama 3.1-405B-Instruct-8bit[^1] | 0.7856 | 0.7943 | 0.8100 | 0.7928 |
| GPT-4o | 0.7810 | 0.7995 | 0.7921 | 0.8025 |
| GPT-4o-mini | 0.7093 | 0.6290 | 0.6403 | 0.7222 |

[^1]: Inception 内部部署的"meta-llama/Llama-3.1-405B-Instruct"的 bnb 8bit 量化版本。

#### 关键观察

行对应被评估的模型，列显示不同裁判给出的分数，包括模型给自己的分数。例如：

- **GPT-4o 给自己打 0.8025**，是它在所有模型上的最高分，表明明显的自我偏见。
- 模型给自己的回答打更高分的趋势在所有裁判中都一致，**除了 Claude-3.5-sonnet**，它给自己的回答打分略低于他人。
- **GPT-4o-mini** 以及延伸的 GPT-4o 表现出最高的自我偏见，因为它们的自评分超过了其他裁判给出的分数。
- **Claude-3.5-sonnet** 看起来自我偏见较少，它的自评分与其他裁判给的分数高度一致。
- **Meta-Llama 3.1-405B-Instruct** 的自评分与外部分数之间表现出中等程度的一致，暗示打分较为均衡。

通过观察自评分相对于外部评分的差异，我们量化了自我偏见的程度，而它会影响一个模型作为裁判的可靠性。

### 幻觉分析

为评估裁判遵循评估指引的可靠性，我们做了幻觉分析。这一实验聚焦于判断裁判是否提供了准确的、符合指引的评论，并避免生成幻觉或无意义的反馈，而不论其与人工标注者的一致与否。分析在两个裁判上进行：

- **Claude-3.5-sonnet**：根据前三个实验被选为表现最佳的裁判；
- **GPT-4o-mini**：因其在成本与性能之间良好的平衡而被选中。

#### 质量校验

我们从评估池中每个被评估模型的回答里随机抽取 10%。人工标注者负责审查裁判的评论，以判断：

- 评论是否遵循了评估指引。
- 评论与模型回答和真值是否在逻辑上一致，或是否显示出任何幻觉迹象。

#### 结果

| 裁判 | 一致度百分比 |
| --- | --- |
| GPT-4o-mini | **100.0%** |
| Claude-3.5-sonnet | **96.3%** |

#### 关键观察

结果表明裁判评论与人类评估之间一致度很高，鉴于任务之简单这符合预期。任务要求裁判评估事实正确性以及与直白指引的对齐程度，把产生幻觉的可能性降到最低。

然而，在 **Claude-3.5-sonnet** 上观察到一个出乎意料的差异，它的一致率（**96.3%**）略低于 **GPT-4o-mini**（**100.0%**）。经进一步调查，我们确认该差异是由于 Claude-3.5-sonnet 在部分样本上遇到了 **529 和 500 错误码**。这些错误导致裁判评论字段为空，标注者把它们标记为不一致。

当只分析 Claude-3.5-sonnet 的有效回答（即排除受错误影响的）时，一致率上升到 **100.0%**，与 GPT-4o-mini 持平。这印证了我们的假设：任务设计受限得足够充分，几乎不给幻觉留空间，确保两个裁判都高可靠。

### 陪审团：局限与洞见

**陪审团** 按"先投票再平均"的策略聚合多个裁判的分数，理论上利用"群体智慧"。然而这一方法受限于

- **排名没有差异**：比较陪审团系统与单裁判的模型排名，发现根本没有差异，削弱了使用多裁判的意义。
- **偏见放大**：如果部分裁判共享偏向某些模型的偏见，尤其是当裁判来自同一家大型通用模型家族时，整体分数会被抬高。
- **高资源成本**：雇佣多个裁判的计算开销使该方法在大规模基准上不切实际。

**潜在改进**：如果陪审团纳入更小的、在反映不同视角和文化的多样数据集上微调过的模型，可能更有效。我们打算探索的另一种潜在方法是用语言、文化和视角的变化来改写系统提示，以描述同一任务。这会引入更大的判断多样性，缓解在专有、英语优先的通用模型中观察到的偏见一致性。

### 裁判选择

以上所有实验都倾向于选择 **Claude-3.5-sonnet** 作为 AraGen 排行榜的 **主裁判**，因为它的

- 高一致性（最低标准差）；
- 自我偏见极少，确保公平；
- 与人工标注者相对较高的一致度，可与 GPT-4o-mini 相比。

注意 Cohen Kappa 系数相对较低，不足以据此做决定。然而，与单个人类裁判对齐本身就很困难，因为人有不同的偏见。尽管如此，我们认为它是与更大、更多样的人类裁判群体潜在对齐的一个有意义信号。我们计划在即将到来的版本（三月和六月）中就此做进一步实验。

**GPT-4o-mini** 尽管与人类评估相对一致，我们决定降低它的优先级，因为其较高的分数波动与我们追求的结果可复现性目标相悖。**陪审团系统** 虽然可能是更好的方法，但在本版中因可扩展性挑战、分数抬高以及与单裁判排名缺乏显著差异而被排除。

根据我们迄今所做的实验，Claude-3.5-sonnet 是本版 AraGen 最可靠的选择，平衡了一致性与公平性。

## 结论

我们相信 **AraGen 排行榜** 代表了 LLM 评估的重要一步，通过 **3C3H** 评估度量结合了严格的事实与对齐评估。AraGen 旨在应对数据泄漏、可复现性和可扩展性等挑战，提供了一个稳健框架，我们相信它对许多其他语言都同样有用。

展望未来，我们计划在未来三个月内通过引入新任务来扩展 AraGen 排行榜，同时半自动化数据集创建，以在不通过人工验证牺牲质量的情况下提升可扩展性。此外，我们正在探索更复杂的问题和任务，以持续挑战和打磨模型表现，确保排行榜保持动态和自适应。最后，我们旨在把这一框架扩展到该领域资源不足或代表性不够的其他语言。我们致力于这些倡议的成功，并欢迎社区协作。

## 本文提到的 Space 2

来自我们博客的更多文章

leaderboard

evaluation

nlp

## 阿拉伯语排行榜：引入阿拉伯语指令遵循、更新 AraGen 等

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/626237d9bbcbd1c34f1bb231/EJrOjvAL-68qMCYdnvOrq.png)
- ![](https://huggingface.co/avatars/c71a54d7c9824d17ab4ad3deaf33afd1.svg)
- ![](https://huggingface.co/avatars/c12168cdda7085eb8d649e63115a82b5.svg)
- ![](https://huggingface.co/avatars/9b3b2d12ad3e1959aacfefbb931986dd.svg)
- +2

20

2025 年 4 月 8 日

nlp

research

leaderboard

## 开放阿拉伯语 LLM 排行榜 2

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/626237d9bbcbd1c34f1bb231/EJrOjvAL-68qMCYdnvOrq.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1658510827196-5fc52718fa6eef7667a4d68e.jpeg)
- ![](https://huggingface.co/avatars/66b0d4461fe6ae8b24494e1461231e02.svg)
- ![](https://huggingface.co/avatars/874c3eac1d738f805fa9b42d19bf4472.svg)
- +4

39

2025 年 2 月 10 日

### 社区

通过拖拽到文本输入框、粘贴，或

点击这里

上传图像、音频和视频。

.

点击或粘贴到这里上传图像

· [注册](https://huggingface.co/join?next=%2Fblog%2Fleaderboard-3c3h-aragen) 或 [登录](https://huggingface.co/login?next=%2Fblog%2Fleaderboard-3c3h-aragen) 以评论

点赞

39

- [![](https://huggingface.co/avatars/dd41593a55d1bec4f1a3a54fca35e646.svg)](https://huggingface.co/SamujjwalIIAI)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/628e39f4b1596566033b8d7b/-Y807up1cgMmAQsczdOPn.jpeg)](https://huggingface.co/cchristophe)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63d7acf73130cadcaf827e84/5dbueSbBbcN1NvAYznMq0.jpeg)](https://huggingface.co/karimouda)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/638eb5f949de7ae552dd6211/mJkQJGpn9tXV37N2VLFCh.jpeg)](https://huggingface.co/derek-thomas)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/jJMt0ulikjBDFPtLFUdUq.png)](https://huggingface.co/chYassine)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1628885133347-6116d0584ef9fdfbf45dc4d9.jpeg)](https://huggingface.co/MohamedRashad)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/659028cbbec7ad2647547c26/_zwBYlcwPg6gqjvF9N6k3.jpeg)](https://huggingface.co/Amr-khaled)
- [![](https://huggingface.co/avatars/0c9722d674704a88394af2dd65ef522f.svg)](https://huggingface.co/shawkyebrahim2514)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6400916cf4ff62c2616ddc2f/K96MViOF0Vg4hzPq2XJ25.png)](https://huggingface.co/Manel)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/626237d9bbcbd1c34f1bb231/EJrOjvAL-68qMCYdnvOrq.png)](https://huggingface.co/alielfilali01)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6640bbd0220cfa8cbfdce080/wiAHUu5ewawyipNs0YFBR.png)](https://huggingface.co/John6666)
- [![](https://huggingface.co/avatars/7b5d41178833ebd7aeb2b3232d56f11c.svg)](https://huggingface.co/younos)

## 本文提到的 Space 2
