---
vendor: huggingface
title: IBM 与 UC Berkeley 用 IT-Bench 与 MAST 诊断企业 agent 为何失败
original_title: IBM and UC Berkeley Diagnose Why Enterprise Agents Fail Using IT-Bench and MAST
url: https://huggingface.co/blog/ibm-research/itbenchandmast
date: 2026-04-21
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

[Ayhan Sebin](https://huggingface.co/ayhansebin) [Saurabh Jha](https://saurabhjha.one/) [Rohan Arora](https://rohanarora.name/) [Daby Sow](https://scholar.google.com/citations?user=son-DloAAAAJ&hl=en) [Mert Cemri](https://people.eecs.berkeley.edu/~mert_cemri/) [Melissa Pan](https://melissa-pan.github.io/) [Ion Stoica](https://people.eecs.berkeley.edu/~istoica/)

[ITBench HF Space](https://huggingface.co/spaces/ibm-research/ITBench-Lite) [ITBench HF Dataset](https://huggingface.co/datasets/ibm-research/ITBench-Lite) [MAST HF Dataset](https://huggingface.co/datasets/mcemri/MAST-Data) [ITBench Github](https://github.com/itbench-hub/ITBench) [MAST Github](https://github.com/multi-agent-systems-failure-taxonomy/MAST)

IBM Research 与 UC Berkeley 合作研究了 agentic LLM 系统在真实 IT 自动化中如何崩溃——涉及事件分诊、日志/指标查询，以及长程工具循环中的 Kubernetes 操作。

基准测试通常把性能压缩成一个数字，告诉你 agent 失败了，却从不告诉你为什么。为了解决这个黑盒问题，我们应用了 MAST（Multi-Agent System Failure Taxonomy，多智能体系统失效分类法）——一种诊断 agentic 可靠性的新兴实践。用 MAST 分析 ITBench——面向 SRE、安全与 FinOps 自动化的行业基准——我们把原始执行轨迹转化为结构化的失效签名，精确揭示坏在哪、怎么修。我们对 310 条 ITBench SRE 轨迹做了标注，覆盖三类不同的模型：Gemini-3-Flash、Kimi-K2 与 GPT-OSS-120B。

关键发现：

- Gemini-3-Flash 这类前沿模型失败得很干净（每条轨迹 2.6 个失效模式），通常只撞上孤立的瓶颈，如验证环节。GPT-OSS-120B 这样的大开源模型则深受级联失效模式之苦（每条轨迹 5.3 个失效模式）——运行早期一个微小的推理不一致就会污染上下文，导致幻觉不断叠加。
- 在所有模型中，失败最有力的预测因子是 FM-3.3（Incorrect Verification，错误验证）。agent 总是「宣布胜利」而不核对事实真相。
- Kimi-K2 难以识别任务何时完成。它在 Premature Termination（提前终止，+46%）与 Unaware of Termination Conditions（不知终止条件，+43%）上出现巨增，经常在即将解决问题前放弃，或无限循环。

我们从构建 agent 的分析中提炼的要点：

- 对 Gemini 这类前沿模型：把验证外置。绝不让 LLM 给自己的作业打分。退出前要求硬性工具证据。
- 把终止与循环控制放在模型之外：终止问题是最常见的杀手（FM-1.5）。增加显式停止条件 + 对重复工具调用/动作的循环检测器，或实现有限状态机。
- 输入有歧义时强制「先澄清或只读」：澄清失败（FM-2.2）是小模型的主要失败动因。把歧义作为 agent 图中一等公民的分支。

如果你为企业 IT 工作流构建 agent，这就是你想要的那类评估：不只是「过了吗？」，而是「坏在哪、哪里坏、哪种干预的杠杆最大？」

## Agent 基准的「黑盒」问题

**ITBench** 这类基准正成为衡量高风险 IT 自动化任务中 agentic 性能的标准。在 ITBench 中，agent 扮演站点可靠性工程师（SRE）或安全分析师，负责诊断 Kubernetes 故障、修补漏洞，或在生产环境中管理云成本。

这类基准用成功率作为评估 agent 的主要指标。但对构建稳健系统来说，这个指标不够：知道某 agentic 系统在 ITBench 上只有 14% 成功率，告诉我们*它失败了*，却不告诉我们为什么：**是因为忘了上下文？幻觉出一条命令？还是干脆没有终止？**

缺乏系统性的失效诊断手段，开发者只能瞎猜，往往退而求其次地做盲目的 prompt 调整——解决一个问题又制造另一个。

作为分析复杂 agentic 系统失效模式的新标准，我们开发了 **MAST（多智能体系统失效分类法）**。MAST 带来更多洞见，让这类基准不透明的评估变得公开可读。MAST 源自对 7 种不同框架下 1,600 多条轨迹的严格分析，为 agent 失效提供了标准化的分类。

MAST 把非结构化的执行日志转化为结构化「失效向量」，基于三大类别下 14 种不同模式：

- **FC1：系统设计问题**（「骨架」）失效源自 agent 的架构与角色定义。*例：***FM-1.3 Step Repetition**（循环）、**FM-1.4 Loss of Conversation History**（内存泄漏）、**FM-1.5 Unaware of Termination**（该停不停）。
- **FC2：智能体间失调**（「通信」）失效发生在运行时，源于 agent 之间或 agent 与环境之间的对话方式。*例：***FM-2.2 Fail to Ask for Clarification**（擅自假设而不提问）、**FM-2.3 Task Derailment**（跑题）。
- **FC3：任务验证**（「质检」）失效在于对 agent 输出的质量保证。*例：***FM-3.1 Premature Termination**（过早放弃）、**FM-3.3 Incorrect Verification**（幻觉出成功）。

[![MAST ANALYSIS](https://cdn-uploads.huggingface.co/production/uploads/64e8143f6de557454220921e/e4z2uA2pkASgWJdqdGJZl.webp)](https://cdn-uploads.huggingface.co/production/uploads/64e8143f6de557454220921e/e4z2uA2pkASgWJdqdGJZl.webp)

## 实验：诊断 ITBench agent

我们用 MAST 压力测试「让 agent 评估可操作」这一理念，在 ITBench——覆盖 **SRE**、**安全/合规** 与 **FinOps** IT 自动化任务的流行评估套件——上应用它，获得失效模式的洞见。

我们标注了 310 条 ITBench SRE 执行轨迹，由一个用 Codex 构建的 SRE agent 在贴近现实的环境中产生。这些轨迹记录了 agent 与其工具之间的自然语言交互，来自代表不同能力档位的三个模型：Gemini-3-Flash、Kimi-K2 与 GPT-OSS-120B。这让我们越过简单的成功指标，探究驱动结果的独特失效签名。我们使用召回（recall）分数，因为模型按设计最多只输出 3-5 个结果，而 SRE 更偏好召回分数而非 F-1 分数。

- **Gemini-3-Flash：** 100 条轨迹（平均召回 75.5%）
- **Kimi-K2：** 105 条轨迹（平均召回 28.6%）
- **GPT-OSS-120B：** 105 条轨迹（平均召回 12.4%）

下面详述这次诊断分析的发现。

## 发现 1：Gemini-3-Flash 这样的强模型每条轨迹呈现外科手术式的（孤立）失效模式，而开源的 Kimi-K2 与 GPT-oss-120b 呈现叠乘式失效模式

审视失败的轨迹时，三个模型之间呈现出清晰的复杂度层级——以每次失败运行中观察到的不同失效模式数量来度量。

- **Gemini-3-Flash：** 每条失败轨迹 2.6 个失效模式
- **Kimi-K2：** 每条失败轨迹 4.7 个失效模式
- **GPT-OSS-120B：** 每条失败轨迹 5.3 个失效模式

失效模式密度上的差异揭示了这些系统崩溃方式的根本不同。Gemini-3-Flash 表现出外科手术式的失效画像：即便运行失败，它仍保持很高的内部一致性，通常只因一个孤立的失效点而失败，比如一步错误的验证。这些失败精确、远易于诊断。

光谱另一端，GPT-OSS-120B 饱受级联坍塌之苦。在这些轨迹中，我们观察到错误会随时间叠加。过程中早期一个小的推理不一致常常导致偏离任务规格，继而引发 agent 彻底跑偏。Kimi-K2 居于中间：失败比前沿模型更频繁、更复杂，但未达到 120B 开源权重模型那种系统性不稳定。

这一发现的意义在于：更高的成功率往往伴随着孤立的失败。以更少并发问题失败的系统更可预测，也更容易通过有针对性的工程干预来改进。

[![failure mode](https://cdn-uploads.huggingface.co/production/uploads/64e8143f6de557454220921e/7OtWv_RJ1BZj8n3ChhgUz.webp)](https://cdn-uploads.huggingface.co/production/uploads/64e8143f6de557454220921e/7OtWv_RJ1BZj8n3ChhgUz.webp)

## 发现 2：「非致命」与「致命」失效

也许 MAST 最关键的洞见，是区分系统能*容忍*的失效与对下游任务成功致命的失效。通过比较**成功轨迹**与**失败轨迹**中失效模式的分布，我们可以把它们分成三类。

### 「非致命」（良性）缺陷

在三个模型中，某些失效模式即使在最终成功的运行里也频繁出现。这些多是结构性的摩擦，而非终局性 bug。

- **FM-1.3 Step Repetition（步骤重复）：** 在成功的 Kimi-K2 运行中，90% 以上都有这个模式。在 SRE 领域，迭代往往是必需的。agent 可能多次查询同一指标，以确认服务在趋稳或修复已生效。Gemini-3-Flash 在失败轨迹中的重复反而更少，说明它有时失败是因为迭代不够。
- **FM-1.1 Disobey Task Specification（违背任务规格）：** agent 经常偏离严格的工具格式或顺序指令，但依然能找对根因。

这种区分正是 MAST 价值所在：它让我们忽略排障中常见的重复类良性失效，聚焦于杀死一次运行的致命失效。

### 「致命」缺陷

某些行为能强区分成败。这些模式一出现，成功概率便断崖下跌。最突出的是 **FM-3.3（Incorrect Verification）**：该模式在 Gemini-3-Flash 失败轨迹中的占比比成功轨迹高 52%。其他显著的模式是 1.5（不知终止条件）与 2.6（推理-动作不一致）。

它们一旦发生，这次运行基本就废了——这指导实践者为系统中的各 agent、跨多轮交互，制定健壮的上下文管理策略。

### **案例研究：Gemini-3-Flash（果断但过度自信）**

Gemini-3-Flash 高效，但其首要瓶颈是不加严格验证就假定成功。它的失效签名被验证误差的巨大差值主导：它常能识别正确信号，却在对照事实核验之前就终止。修复方法是实现外置验证门：在允许 agent 退出前，要求诸如告警已清除或指标恢复健康的工具证据，以此缓解这个模型固有的过度自信。

- **修复：** 要在 ITBench 上提升 Gemini-3-Flash，prompt 工程帮助不大。具体地，我们在 [NeurIPS 2025 论文](https://arxiv.org/abs/2503.13657)中展示的实验表明，对内存类失效做 prompt 工程这类人工干预，性能提升最多约 15.6%；而在[上一篇 MAST 博文](https://mast-ucb.notion.site/improve-agents-with-mast)中我们展示：引入新的 agent——例如 **Summarizer Agent** 向其他 agent 提醒当前状况并持续增补其状态（修复 FM-1.4），或引入上下文管理机制（如更严格的**状态机**强制终止以修复 FM-1.5），性能提升可达 53%，因为这些直击系统的根本问题。

[![gemini 3](https://cdn-uploads.huggingface.co/production/uploads/64e8143f6de557454220921e/TIC3M-6ZyIJhRuWdv-Zvr.webp)](https://cdn-uploads.huggingface.co/production/uploads/64e8143f6de557454220921e/TIC3M-6ZyIJhRuWdv-Zvr.webp)

- **案例研究：Kimi-K2（终止危机）**

虽然终止混乱（FM-3.1 与 FM-1.5）是 Kimi-K2 的主要失效模式，但它的失败轨迹由一个无处不在的 **Action-Reasoning Mismatch（动作-推理不一致，FM-2.6）** 定义——出现在其失败中惊人的 **92%**。

- **执行鸿沟：** 尽管其部分内部推理常常正确，但它受 FM-2.6 高达 92% 失败占比的困扰。它频繁识别出正确的下一步，随后却执行冗余或无关的命令。
- **元循环陷阱：** 约 25% 的失败轨迹涉及 **FM-2.3（Task Derailment）**。当工具调用返回小错误，agent 常常放弃主事件调查，转陷入调试自己调查脚本的循环。

Kimi-K2 是一个「想太多」模型的好例子：推理链往往过长，却在执行上失手。

[![kimi2](https://cdn-uploads.huggingface.co/production/uploads/64e8143f6de557454220921e/oiqI0JpzhJIzT8WU8YPRM.webp)](https://cdn-uploads.huggingface.co/production/uploads/64e8143f6de557454220921e/oiqI0JpzhJIzT8WU8YPRM.webp)

### 案例研究：**GPT-OSS-120B**

GPT-OSS-120B 表现出这批模型中最不稳定的失效签名。每条失败轨迹平均 5.3 个不同失效模式，说明其维护内部状态存在根本性缺陷。

- **Loss of Conversation History（FM-1.4）：** 这是 120B 模型独有的致命缺陷。它在 **24%** 的轨迹中丢失对话历史，而 Gemini-3-Flash 内存零丢失、Kimi-K2 仅 7%。随着 SRE 轨迹变长，GPT-OSS-120B 实际上「忘记」了自己最初在分诊的告警，导致任务彻底跑偏。
- **Reasoning Disconnect（FM-2.6）：** 多达 **94%** 的轨迹存在推理与动作脱钩。它说出正确计划却执行完全无关或冗余工具调用的可能性几乎是 Gemini（31%）的 3 倍。

[![OSS](https://cdn-uploads.huggingface.co/production/uploads/64e8143f6de557454220921e/i179ZOT-r6et7kC23J0oy.webp)](https://cdn-uploads.huggingface.co/production/uploads/64e8143f6de557454220921e/i179ZOT-r6et7kC23J0oy.webp)

## 读图的另一（更有用的）方式：「致命」vs「非致命」

总而言之，MAST 把失效模式分成两桶：

### 可恢复/结构性（在成功轨迹中同样出现）

这些失效并非致命，系统可以从中恢复并成功完成任务。

- **FM-1.3 步骤重复**
- **FM-3.3 错误验证**（一个重要细微处：系统*确实*在验证，只是验证得差）
- **FM-2.6 推理-动作不一致**（常出现，但并非总是决定性）

### 致命/决定性（与失败轨迹强相关）

这些失效系统通常无法恢复。

- **FM-1.5 不知终止条件**
- **FM-3.1 提前终止**
- **FM-1.4 丢失对话历史**
- **FM-2.3 任务偏航**（少见，但一旦出现极有诊断价值）
- **FM-2.2 不请求澄清**（尤其对 Granite/Llama 这类档位）

这就是「更丰富的理解」所在：**两个模型在同一小子集上可以有相同成功率，却因完全不同的原因失败——需要完全不同的修复。**

## 结论

MAST 是一种检查 agentic 系统轨迹、识别细粒度失效类型以支撑系统开发与调试的工具。在这篇博客中，我们展示了把 MAST 应用于 ITBench 后，我们从笼统观察（「开源模型不行」）走向了具体的工程路线图，帮助改进依赖这些模型的 agentic 系统的性能，例如：

- **对 Gemini-3-Flash：** 验证失败（**FM-3.3**）是外科式模型最常见的致命失效。绝不允许 agent 自我终止；在一次运行被判定成功前，要求硬性的、经工具中介的证据（如 AlertManager 告警清除或 K8s 状态变更）。
- **对 Kimi-K2：** 用确定性状态机修复模型频繁无法识别任务完成的问题。这个模型的推理链可能过长、难以终止，因此从「更严格控制何时结束」中获益会很大。
- **对 GPT-oss-120b：** 当微小的推理不一致（**FM-2.6**）污染任务历史时，会发生系统性坍塌。实施积极的上下文卫生与早期错误检测，确保小的偏差不再复合成彻底跑偏。

- **IT-Bench 论文：** [https://arxiv.org/pdf/2502.05352](https://arxiv.org/pdf/2502.05352)
- **IT-Bench 代码：** [https://github.com/itbench-hub/ITBench](https://github.com/itbench-hub/ITBench)
- **MAST 论文：** [https://arxiv.org/abs/2503.13657](https://arxiv.org/abs/2503.13657)
- **MAST 代码：** [https://github.com/multi-agent-systems-failure-taxonomy/MAST](https://github.com/multi-agent-systems-failure-taxonomy/MAST)
- **MAST-Data**：[🤗 MAST-Data（1600+ 轨迹）](https://huggingface.co/datasets/mcemri/MAST-Data)
