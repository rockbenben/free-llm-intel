---
vendor: huggingface
title: Apriel-H1：蒸馏高效推理模型的那个出人意料的关键
original_title: Apriel-H1: The Surprising Key to Distilling Efficient Reasoning Models
url: https://huggingface.co/blog/ServiceNow-AI/apriel-h1
date: 2025-11-03
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Apriel-H1：蒸馏高效推理模型的那个出人意料的关键

我们把我们的 15B 推理模型转换成了 Mamba 混合架构，以最小的质量损失实现了 2.1 倍吞吐。关键是什么？是一个关于该用什么数据来蒸馏的非显而易见的洞见，以及直觉在这里为什么会失效。

当 MiniMax 在十月发布他们的 [M2 事后复盘](https://huggingface.co/blog/MiniMax-AI/why-did-m2-end-up-as-a-full-attention-model)、解释他们为什么在 230B 规模上放弃了高效注意力时，叙事一度变成"高效注意力已死"。几天之内，[Kimi Linear](https://github.com/MoonshotAI/Kimi-Linear) 就证明了不然。真正的教训是：这取决于你的约束。

我们的约束很简单：**我们有一个强大的 15B 推理模型，需要在不推倒重来的前提下让它变得高效。** 没有用于 20T-token 预训练的无限算力。没有从第一天起做架构协同设计的奢侈条件。只是一个实际问题：你能通过蒸馏把效率改造进一个现有模型吗？

剧透：能，但只有当你摒弃关于该用什么数据的直觉才行。

## 我们构建了什么

[Apriel-H1 系列](https://huggingface.co/collections/ServiceNow-AI/apriel-h1)：横跨 25-40 个 Mamba 层（总共 50 层）的七个检查点，展示了完整的效率-质量前沿。我们的旗舰 [Apriel-H1-15b-Thinker-SFT](https://huggingface.co/ServiceNow-AI/Apriel-H1-15b-Thinker-SFT) 以最小质量损失达到 **2.1 倍吞吐**：MATH500 和 MTBench 提升几个点（分别从 0.90 → 0.92 和 8.30 → 8.58），而 GSM8k（0.97 → 0.95）、GPQA（0.59 → 0.55）和 AIME24（0.70 → 0.65）略有退步。总训练量：76.8B token。

[![Apriel-H1 Evaluation Results](https://huggingface.co/ServiceNow-AI/Apriel-H1-15b-Thinker-SFT/resolve/main/images/apriel_h_vs_apriel_15b_eval_thrput_comparison.png)](https://huggingface.co/ServiceNow-AI/Apriel-H1-15b-Thinker-SFT/resolve/main/images/apriel_h_vs_apriel_15b_eval_thrput_comparison.png)

*Apriel-H1-15b-Thinker-SFT（绿色）对全注意力教师（蓝色）。推理质量在各基准上几乎持平，而吞吐随上下文长度不同提升 1.89-2.09 倍。*

完整细节在我们 [Apriel-H1 论文](https://arxiv.org/abs/2511.02651)中。这里，我们聚焦于让它奏效的那个关键洞见。

## 那个非显而易见的洞见

这是我们起初以为会奏效的做法：就在预训练数据上蒸馏，再补一些 SFT 收尾。

这个推理看起来站得住。我们要插入完全崭新的、从未见过数据的 Mamba 层。这些线性 SSM 需要从零学习通用的 token 混合。除非它们获得与原注意力层所见的相同宽分布的曝光，否则它们怎能成为有效的混合器？

于是我们试了。然后我们试了混合预训练和 SFT 数据。它没用。蒸馏出的混合模型丢失了推理质量，有时是大幅丢失。

**真正奏效的是：来自教师 SFT 数据集的高质量推理轨迹。**

蒸馏一个推理模型，不是关于迁移通用的下一 token 预测。基座模型已经有了那个，而我们是从一个强大的 15B 基础起步的。我们所保留的是具体而脆弱的东西：**教师的多步推理模式。**

这些模式从精巧的注意力机制中涌现。把上下文从数千 token 之前拉回来的检索头（retrieval heads）。识别并延续逻辑链的归纳头（induction heads）。把前提与许多步之后的结论连接起来的长程依赖。当你用 Mamba 的线性递推整体替换注意力时，这些计算机制被打断。混合模型必须发现通往同样推理结果的新路径。

那种发现需要有明确的、推理结构可见且正确的例子：

- 每一步想法都从上一步推出的多步数学证明
- 有清晰逻辑依赖的编码任务
- 有详尽解释链的科学分析

另一方面，预训练数据太嘈杂、太分散。推理信号被淹没了。你需要你所试图保留的那个特定能力的集中样本。

一旦我们理解了数据选择，我们的蒸馏方法也就清楚了。我们使用**反向 KL 散度**（温度 1）而非前向 KL。反向一致地胜出。为什么？我们在那些教师有高置信和清晰结构的问题上训练。反向 KL 的寻模（mode-seeking）行为鼓励学生去承诺那些高置信预测。当你的教师既自信又正确时，你也希望你的学生自信。

这一洞见是整个方法的关键：**把你的蒸馏数据匹配到你所保留的能力上，而不是你所构建的能力上。**

## 如何应用它：分阶段蒸馏

你不能只是把 40 层注意力换成 Mamba 然后寄望好运。我们吃了苦头才学会这点，并最终开发出一套分阶段蒸馏流程来可靠地达到目标。

**阶段 1：识别最不重要的层。** 我们在 MMLU 上使用了一种留一法（Leave-One-Out, LOO）分析：移除每一层，用恒等替换，然后测量下降幅度。按重要性排序，用 [Mamba-in-Llama](https://arxiv.org/abs/2408.15237)（MIL）初始化的混合器替换底部 25 层。端到端蒸馏。这对我们的 H-25 检查点奏效。

**阶段 2：超过 25 层的渐进转换。** 超过 25 层后 LOO 就失效了，因为单独看来不重要的层在组合中变得关键。为解决这点，我们开发了一种我们称之为 **MIL-Mamba-Replacement（MMR）** 的动态启发式。对每个剩余的注意力层，我们用 MIL 初始化一个 Mamba 混合器，运行 100 训练步，并记录蒸馏损失。收敛到更低损失的层"更易于"替换。这捕捉的是训练动态而非静态重要性。

我们渐进地推进：25 → 27 → 30 → 34 → 37 → 40 个 Mamba 层，按 MMR 分数分组成替换。每个检查点都从上一个蒸馏而来。

**阶段 3：在 SFT 数据上端到端训练。** 达到目标 Mamba 层数后，我们做最后一遍 SFT 直到推理性能稳定。经过 55.9B 蒸馏 token 和 20.9B SFT token，这产出了我们最终的 Apriel-H1-15b-Thinker-SFT 模型。

[![Apriel-H1 Family Performance](https://huggingface.co/ServiceNow-AI/Apriel-H1-15b-Thinker-SFT/resolve/main/images/throughput_eval_score_vs_throughput_1-16k_annotated.png)](https://huggingface.co/ServiceNow-AI/Apriel-H1-15b-Thinker-SFT/resolve/main/images/throughput_eval_score_vs_throughput_1-16k_annotated.png)

*完整效率前沿。每个检查点显示累积训练 token。我们的旗舰 H-30-SFT（以 Apriel-H1-15b-Thinker-SFT 名义发布）用了 76.8B 总量，在 0.76 平均分下达到 2.1 倍吞吐。激进转换的 H-40 变体用了 136.5B token 达到 3.4 倍吞吐。作为参考：NVIDIA 的 Nemotron-Nano-9B-v2 在 0.77 分下达到 4.6 倍，但需要用从头训练、多几个数量级的算力。*

## 让它可复现：Fast-LLM

我们把这一切构建在 [Fast-LLM](https://github.com/ServiceNow/Fast-LLM) 之上，我们的开源训练框架。核心架构原则是：**大语言模型的 transformer 应当是模块化的。** 注意力和 Mamba 是同一个"混合"接口的不同实现，可以随意互换。

这里是 Fast-LLM 配置格式中的一个混合架构：

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

`pattern` 字段指定层顺序。对 Apriel-H1-15b-Thinker-SFT：30 个 `mamba_block`、20 个 `attention_block`，按重要性排布。就这么简单。

蒸馏也是配置：

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

Fast-LLM 处理梯度累积、分布式训练、张量并行、检查点，以及大规模实验所需的一切。它是开源的，以 Apache 2.0 授权。**你可以复现这项工作**，因为我们设计基础设施时就是为了让它可复现。

## 常见问题

**为什么发布所有检查点？** 因为最优取决于你的约束。H-30 提供最佳平衡。H-40 为延迟敏感的工作负载最大化吞吐。中间检查点让你选择自己确切的权衡。

**为什么在不同上下文长度下你会得到不同的加速？** Mamba 的线性复杂度优势随序列长度增长，而注意力以二次方退化。

**为什么你只试了 Mamba？** 我们使用 **Mamba-1** 有三个原因：它有良好的蒸馏先例、展现出强劲的实证性能，并且在我们的框架中易于实现。它让我们先把注意力集中在数据问题上。

**Mamba 的超参数是什么？** State size 16，DT rank 16，内部维度 4096。对于我们在 Apriel 中的 GQA 设置，我们遵循 [M1](https://arxiv.org/abs/2504.10449) 扩展了 B（输入投影）和 x（状态）以匹配总注意力头数。

**为什么你们没有尝试更先进的转换方法？** 我们使用 [Mamba-in-Llama](https://arxiv.org/abs/2408.15237) 初始化和知识蒸馏，而非 [MOHAWK](https://arxiv.org/abs/2408.10189) 的多阶段流程，因为后者在初步实验中没有显示出显著优势。

**为什么你只对 H-30 模型做了 SFT？** 我们只对 H-30 施加 SFT，以验证蒸馏出的混合模型能通过标准后训练得到改善。其他检查点是纯蒸馏的，但可以类似地微调。

**为什么你没有探索 RL？** 这是一个界定范围的决策，用来隔离蒸馏问题：你能仅靠知识蒸馏迁移推理吗？答案：能。但 RL 应当能进一步弥合剩余的质量差距。我们正在为未来迭代探索 RL。

**你们真的证明了 Apriel-H1 在相似算力预算下匹敌全注意力的推理吗？** 我们没有做全注意力 Apriel 与一个从预训练起以完全相同方式训练的混合模型之间的同条件对比。那需要用 Apriel-H1 架构重复教师所有的中期训练和后训练，这超出了我们的算力预算。不过我们能主张的是：通过蒸馏改造效率是可行且有效的，而得到的混合模型可以被微调到匹敌甚至超过教师的推理质量。

## 生产现实

我们已经在 Hugging Face Transformers 和 vLLM 中实现了 Apriel-H1。Transformers 集成很直接。我们交付一个带可互换注意力和 Mamba 层的新模型类。vLLM 集成使用他们最近的 [Mamba 缓存操作](https://pytorch.org/blog/hybrid-models-as-first-class-citizens-in-vllm/)来实现连续批处理、前缀缓存和分块预填充。vLLM 插件已就绪。我们目前正在等待最终的法务批准以将其开源。

**坦率的评估：** 今天部署混合模型意味着磕磕绊绊。工具链正在快速成熟，但还不是开箱即用。你会写自定义代码、谨慎地验证数值行为，并绕过框架限制。对于能吸收这份成本的团队，吞吐增益值得。对于不能的，等待可能是正确的选择。

## 要点

大多数团队没有用于 20T-token 预训练的无限算力。如果你已经投入了一个强大的基座模型并需要效率增益，这项工作展示了一条实践路径：使用与你所保留的能力相匹配的高质量任务特定数据，蒸馏进混合模型。

那个出人意料的发现——**用推理数据来蒸馏推理**——事后看似乎显而易见，却与最初的直觉相悖。我们验证了它、解释了它为何奏效，并构建了让它可复现的基础设施。

## 试用

**模型：** [Apriel-H1 Collection on HuggingFace](https://huggingface.co/collections/ServiceNow-AI/apriel-h1)
**训练框架：** [Fast-LLM on GitHub](https://github.com/ServiceNow/Fast-LLM)
**教师模型：** [Apriel-Nemotron-15B-Thinker](https://huggingface.co/ServiceNow-AI/Apriel-Nemotron-15b-Thinker)
**论文：** [Apriel-H1: Towards Efficient Enterprise Reasoning Models](https://arxiv.org/abs/2511.02651)

发现了坏掉的东西？提一个 issue。发现了更好的层排布启发式？告诉我们。在 Apriel-H1 上构建了有趣的东西？我们很想看看。

**引用：**

```
@article{apriel-h1-2025,
  title={Apriel-H1: Towards Efficient Enterprise Reasoning Models},
  author={SLAM Lab, ServiceNow},
  journal={arXiv preprint arXiv:2511.02651},
  year={2025}
}
```

**核心贡献者：** Oleksiy Ostapenko, Luke Kumar, Raymond Li, Denis Kocetkov, Joel Lamy-Poirier, Torsten Scholak
**贡献者：** Shruthan Radhakrishna, Soham Parikh, Shambhavi Mishra
**技术共同负责人：** Torsten Scholak, Sathwik Tejaswi Madhusudhan
