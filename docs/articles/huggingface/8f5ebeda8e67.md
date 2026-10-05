---
vendor: huggingface
title: 混合专家模型详解
original_title: Mixture of Experts Explained
url: https://huggingface.co/blog/moe
date: 2023-09-04
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: 23e491d09992
---

# 混合专家模型详解

本文另有中文版本可用：[简体中文](https://huggingface.co/blog/zh/moe)。

> 本文有第二版（2026 年 2 月），讲的是 transformers 库如何围绕 MoE 建设、让它们成为库和 Hub 的「一等公民」。帖子链接：Mixture of Experts (MoEs) in Transformers

随着 Mixtral 8x7B 的发布（[公告](https://mistral.ai/news/mixtral-of-experts/)、[model card](https://huggingface.co/mistralai/Mixtral-8x7B-v0.1)），一类 transformer 成了开放 AI 社区最热的话题：混合专家（Mixture of Experts），简称 MoE。这篇博客来看 MoE 的构件、它们如何训练，以及推理部署时的取舍。

开讲！

## 目录

- [什么是混合专家（MoE）？](https://huggingface.co/blog/moe#what-is-a-mixture-of-experts-moe)
- [MoE 简史](https://huggingface.co/blog/moe#a-brief-history-of-moes)
- [什么是稀疏性？](https://huggingface.co/blog/moe#what-is-sparsity)
- [MoE 的 token 负载均衡](https://huggingface.co/blog/moe#load-balancing-tokens-for-moes)
- [MoE 与 Transformers](https://huggingface.co/blog/moe#moes-and-transformers)
- [Switch Transformers](https://huggingface.co/blog/moe#switch-transformers)
- [用 router Z-loss 稳定训练](https://huggingface.co/blog/moe#stabilizing-training-with-router-z-loss)
- [专家学到了什么？](https://huggingface.co/blog/moe#what-does-an-expert-learn)
- [专家数量的扩展对预训练有什么影响？](https://huggingface.co/blog/moe#how-does-scaling-the-number-of-experts-impact-pretraining)
- [微调 MoE](https://huggingface.co/blog/moe#fine-tuning-moes)
- 什么时候该用稀疏 MoE，什么时候该用稠密模型？
- [让 MoE 跑起飞（brrr）](https://huggingface.co/blog/moe#making-moes-go-brrr) [专家并行](https://huggingface.co/blog/moe#parallelism) [容量因子与通信成本](https://huggingface.co/blog/moe#capacity-factor-and-communication-costs) [服务化技术](https://huggingface.co/blog/moe#serving-techniques) [高效训练](https://huggingface.co/blog/moe#more-on-efficient-training)
- [开源 MoE](https://huggingface.co/blog/moe#open-source-moes)
- [令人兴奋的方向](https://huggingface.co/blog/moe#exciting-directions-of-work)
- [一些资料](https://huggingface.co/blog/moe#some-resources)

## TL;DR

MoE：

- 相比稠密模型**预训练快得多**
- 与相同参数规模的模型相比**推理更快**
- 但需要**高显存**——所有专家都要加载进内存
- **微调**面临不少挑战，但 [近期工作](https://arxiv.org/pdf/2305.14705.pdf)显示 MoE 的**指令微调很有前景**

开讲！

## 什么是混合专家（MoE）？

模型规模是提升模型质量最重要的轴之一。在给定固定算力预算下，训一个更大的模型、跑更少的步，胜过训一个小模型跑更多步。

混合专家让模型预训练消耗的算力大幅降低——这意味着你可以用和稠密模型一样的算力预算，把模型或数据集规模拉高一大截。具体地说，MoE 模型在预训练期间应能以远更快的速度达到稠密模型同等的品质。

那么 MoE 究竟是什么？在 transformer 模型的语境下，MoE 由两个主要部分构成：

- **稀疏 MoE 层**取代稠密前馈网络（FFN）层。MoE 层有一定数量的「专家」（比如 8 个），每个专家是一个神经网络。实践中专家就是 FFN，但也可以是更复杂的网络，甚至本身又是一个 MoE——形成层级式 MoE！
- 一个**门控网络（gate network）或路由器（router）**，决定哪些 token 发给哪些专家。比如下图中，token "More" 被发给第二个专家，token "Parameters" 被发给第一个网络。正如后面会看到的，一个 token 也可以发给多个专家。如何把 token 路由给专家是 MoE 设计中的重大决策之一——路由器由可学习参数构成，与网络其余部分同时预训练。

来自 [Switch Transformers 论文](https://arxiv.org/abs/2101.03961)的 MoE 层

回顾一下：在 MoE 中，我们把 transformer 模型的每一层 FFN 换成一个 MoE 层，由门控网络加若干专家构成。

尽管 MoE 带来高效预训练、更快推理等好处，它也有难题：

- **训练**：MoE 能实现算力效率高得多的预训练，但历史上它们在微调阶段泛化不佳，容易过拟合。
- **推理**：虽然 MoE 可能有很多参数，推理时只用其中一部分。这使推理比同参数规模的稠密模型快得多。但所有参数都要载入 RAM，内存需求很高。例如一个 Mixtral 8x7B 这样的 MoE，我们需要装得下一个稠密 47B 参数模型的显存。为什么是 47B 而不是 8 x 7B = 56B？因为在 MoE 模型里只有 FFN 层被当作独立专家，其余参数是共享的。同时，假设每个 token 只用 2 个专家，推理速度（FLOPs）相当于用 12B 模型（而不是 14B），因为它做的是 2x7B 的矩阵乘法，但有些层是共享的（细节马上讲）。

有了 MoE 的大致概念后，来看看导致其发明的研究脉络。

## MoE 简史

MoE 的源头是 1991 年的论文 [Adaptive Mixture of Local Experts](https://www.cs.toronto.edu/~hinton/absps/jjnh91.pdf)。其思想类似集成（ensemble）方法：设计一个由多个独立网络组成的系统的监督学习流程，每个网络负责训练样本的不同子集。每个独立网络（即专家）专精输入空间的不同区域。专家如何选择？由一个门控网络决定各专家的权重。训练时，专家和门控一起训。

2010-2015 年间，两条研究方向为后来的 MoE 发展做了铺垫：

- **专家作为组件**：传统 MoE 设定中，整个系统 = 门控网络 + 多个专家。作为完整模型的 MoE 曾在 SVM、高斯过程等方法中被探索过。[Eigen、Ranzato 和 Ilya](https://arxiv.org/abs/1312.4314) 的工作探索了把 MoE 当作更深网络的组件：这样 MoE 可以作为多层网络中的一层，让模型同时做到又大又高效。
- **条件计算（Conditional Computation）**：传统网络把所有输入都过所有层。这一时期 Yoshua Bengio 研究了根据输入 token 动态激活或关闭组件的方法。

这些工作推动了在 NLP 语境下使用专家混合。具体来说，[Shazeer et al.](https://arxiv.org/abs/1701.06538)（2017，"et al." 里包括 Geoffrey Hinton 和 Jeff Dean——[谷歌的 Chuck Norris](https://www.informatika.bg/jeffdean)）把这个想法扩展到 137B 参数的 LSTM（当年 NLP 的事实标准架构，出自 Schmidhuber 之手），引入稀疏性，即使规模很大也能保持非常快的推理。该工作聚焦翻译任务，但也面临诸多挑战，比如高通信成本和训练不稳定。

来自 Outrageously Large Neural Network 论文的 MoE 层

MoE 使得训练数万亿参数的模型成为可能，比如开源的 1.6T 参数 Switch Transformers 等。MoE 在计算机视觉中也被探索过，但本博客聚焦 NLP 领域。

## 什么是稀疏性？

稀疏性践行的就是条件计算的思想。稠密模型对所有输入使用全部参数，稀疏性则允许我们只运行整个系统的一部分。

深入看 Shazeer 对 MoE 用于翻译的探索。这种设定下，条件计算（网络的部分组件按样本逐个激活）允许扩大模型规模而不增加计算量，这导致每个 MoE 层可以用成千上万个专家。

这种设定带来一些挑战。例如，虽然大 batch size 通常性能更好，但当数据流过被激活的专家时，MoE 的有效 batch size 会被削减。比如输入 batch 有 10 个 token，可能**5 个 token 进了同一个专家，另外 5 个各自进了 5 个不同专家，导致 batch 不均、利用率不足**。下文的「让 MoE 跑起飞」一节会讨论其他挑战和解决方案。

怎么解决？一个学出来的门控网络（G）决定把输入的某一部分送给哪些专家（E）：

y=∑i=1nG(x)iEi(x) y = \sum_{i=1}^{n} G(x)_i E_i(x) y=i=1∑n​G(x)i​Ei​(x)

这个式子里所有专家对所有输入都会跑——只是加权乘法。但 G 为 0 时会怎样？那样就不必计算对应专家的操作，算力就省下了。典型的门控函数长什么样？最传统的设定就是用一个小网络配 softmax 函数，网络会学着把输入送向哪个专家。

Gσ(x)=Softmax(x⋅Wg) G_\sigma(x) = \text{Softmax}(x \cdot W_g) Gσ​(x)=Softmax(x⋅Wg​)

Shazeer 的工作还探索了其他门控机制，例如 Noisy Top-k Gating（带噪 top-k 门控）。这种门控先引入一些（可调的）噪声，然后只保留 top k 个值：

- 加一些噪声

H(x)i=(x⋅Wg)i+StandardNormal()⋅Softplus((x⋅Wnoise)i) H(x)_i = (x \cdot W_{\text{g}})_i + \text{StandardNormal()} \cdot \text{Softplus}((x \cdot W_{\text{noise}})_i) H(x)i​=(x⋅Wg​)i​+StandardNormal()⋅Softplus((x⋅Wnoise​)i​)

- 只取 top k

KeepTopK(v,k)i={viif vi is in the top k elements of v,−∞otherwise. \text{KeepTopK}(v, k)_i = \begin{cases} v_i & \text{if } v_i \text{ is in the top } k \text{ elements of } v, \\ -\infty & \text{otherwise.} \end{cases} KeepTopK(v,k)i​={vi​−∞​if vi​ is in the top k elements of v,otherwise.​

- 再应用 softmax。

G(x)=Softmax(KeepTopK(H(x),k)) G(x) = \text{Softmax}(\text{KeepTopK}(H(x), k)) G(x)=Softmax(KeepTopK(H(x),k))

这种稀疏带来一些有趣的性质。只要 k 足够小（比如 1 或 2），训练和推理就能比激活许多专家时快得多。为什么不干脆只选 top-1 专家？最初的猜想是：必须路由到至少两个专家，门控才能学会如何路由到不同专家，所以至少选两个。[Switch Transformers](https://huggingface.co/blog/moe#switch-transformers) 一节会重新审视这个决定。

为什么要加噪声？为了负载均衡！

## MoE 的 token 负载均衡

前面说过，如果所有 token 都被送到少数热门专家，训练效率会很差。普通 MoE 训练中，门控网络往往收敛到反复激活同样那几个专家。这会自我强化：受优待的专家被练得更快，于是更常被选中。为缓解这一点，会加入一个**辅助损失（auxiliary loss）**鼓励所有专家同等重要。该损失确保每个专家拿到大致均等的训练样本。下面的章节还会介绍专家容量（expert capacity）概念——它规定一个专家能处理多少 token 的阈值。在 `transformers` 中，辅助损失通过 `aux_loss` 参数暴露。

## MoE 与 Transformers

Transformers 是「参数越多效果越好」的典型案例，所以 Google 在 [GShard](https://arxiv.org/abs/2006.16668) 中研究这条路线并不意外——它探索把 transformer 扩展到 6000 亿参数以上。

GShard 把编码器和解码器中每隔一层的 FFN 替换成使用 top-2 门控的 MoE 层。下一张图展示编码器部分的样子。这种设计对大规模计算非常有利：扩展到多设备时，MoE 层跨设备共享，其他层则复制。这在「让 MoE 跑起飞」一节还会展开。

GShard 论文中的 MoE Transformer 编码器

为了在扩展规模时保持负载均衡和效率，GShard 作者在类似上一节讲的辅助损失之外，还引入了几个改动：

- **随机路由**：在 top-2 设定里，top-1 专家总是被选，第二个专家则按权重成比例的概率被选中。
- **专家容量**：可以设定单个专家处理 token 数的阈值。如果两个专家都满了，该 token 就被视为溢出（overflowed），通过残差连接送到下一层（在其他项目中则直接丢弃）。这个概念将成为 MoE 最重要的概念之一。为什么需要专家容量？因为所有张量形状在编译期静态确定，而我们无法预先知道每个专家会收到多少 token，所以必须固定容量因子。

GShard 论文还用公式表达了适合 MoE 的并行计算模式，这超出了本博客的范围。

**注意：**推理时只有部分专家被触发。与此同时有些计算是共享的，比如 self-attention 会作用于所有 token。这就是为什么我们说 47B、8 专家的模型，其计算量可以用 12B 稠密模型来跑。如果用 top-2，本来应是 14B 参数，但由于注意力运算是共享的（还有其他共享部分），实际使用的参数量是 12B。

## Switch Transformers

虽然 MoE 前景光明，但它们在训练和微调的稳定性上挣扎。[Switch Transformers](https://arxiv.org/abs/2101.03961) 是一项对这些话题深入挖掘的精彩工作。作者甚至在 Hugging Face 上发布了 2048 专家、[1.6 万亿参数的 MoE](https://huggingface.co/google/switch-c-2048)，可以直接用 transformers 跑。Switch Transformers 相对 T5-XXL 实现了 4 倍预训练加速。

Switch Transformer 论文中的 Switch Transformer 层

与 GShard 一样，作者把 FFN 层换成 MoE 层。Switch Transformers 论文提出的 Switch Transformer 层接收两个输入（两个不同 token），并有四个专家。

与最初「至少用两个专家」的想法相反，Switch Transformers 采用简化的单专家策略。这一方法的效果：

- 路由器计算量降低
- 每个专家的 batch size 至少可以减半
- 通信成本降低
- 质量保持

Switch Transformers 还深入研究了专家容量的概念。

Expert Capacity=(tokens per batchnumber of experts)×capacity factor \text{Expert Capacity} = \left(\frac{\text{tokens per batch}}{\text{number of experts}}\right) \times \text{capacity factor} Expert Capacity=(number of expertstokens per batch​)×capacity factor

上面定义的容量相当于把 batch 里的 token 数均分给各专家。容量因子大于 1 时，就为 token 不完全均衡的情况留了缓冲。增大容量会导致更昂贵的跨设备通信，这是要权衡的。具体而言，Switch Transformers 在低容量因子（1-1.25）下就表现出色。

Switch Transformers 作者还重新审视并简化了前文提到的负载均衡损失。对每个 Switch 层，训练时把辅助损失加进模型总损失。该损失鼓励均匀路由，可通过一个超参数调权重。

作者还试验了选择性精度（selective precision），比如专家用 `bfloat16` 训练、其余计算用全精度。降低精度能减少处理器之间的通信成本、计算成本和张量存储内存。最初的实验里专家和门控网络都用 `bfloat16` 训练，结果更不稳定。原因特别在路由器计算上：路由里有指数运算，更高精度很重要。为了消除不稳定，路由也改用全精度。

使用选择性精度不损质量，还能让模型更快

这个 [notebook](https://colab.research.google.com/drive/1aGGVHZmtKmcNBbAwa9hbu58DDpIuB5O4?usp=sharing) 演示了用 Switch Transformers 微调做摘要，但建议先看[微调章节](https://huggingface.co/blog/moe#fine-tuning-moes)。

Switch Transformers 用的是 encoder-decoder 架构，相当于给 T5 做了个 MoE 版。[GLaM](https://arxiv.org/abs/2112.06905) 论文则探索进一步推大规模：用 1/3 的能量训练出达到 GPT-3 质量的模型（是的，因为 MoE 训练所需算力更低，碳足迹能降最多一个数量级）。该工作聚焦 decoder-only 模型和 few-shot/one-shot 评估而非微调。他们用了 Top-2 路由和大得多的容量因子，还研究了把容量因子当作训练和评估期间可变的指标——想用多少算力就调多少。

## 用 router Z-loss 稳定训练

前面讲的平衡损失可能导致不稳定。我们可以用很多方法稳定稀疏模型，但要以牺牲质量为代价。例如引入 dropout 能提升稳定性但损伤模型质量；反过来，多加乘法组件能提升质量却降低稳定性。

[ST-MoE](https://arxiv.org/abs/2202.08906) 提出的 router z-loss 在不损质量的情况下显著提升训练稳定性，它惩罚进入门控网络的大 logits。该损失鼓励数值的绝对幅度变小，从而减少舍入误差——对门控中的指数运算这类函数影响很大。推荐细读原论文。

## 专家学到了什么？

ST-MoE 作者观察到，编码器的专家会专精于某类 token 组或浅层概念。比如可能出现一个标点专家、一个专有名词专家等。而解码器的专家专精程度较低。作者还在多语言设定下训练。虽然可以设想每个专家专精一门语言，但事实相反：由于 token 路由和负载均衡，没有任何一个专家专精于某门语言。

ST-MoE 论文中展示哪些 token 组被送到哪个专家的表格。

## 专家数量的扩展对预训练有什么影响？

更多专家带来更好的样本效率和加速，但收益递减（尤其超过 256 或 512 之后），而且推理需要更多 VRAM。Switch Transformers 在大规模下研究的性质在小规模下同样成立——哪怕每层只有 2、4 或 8 个专家。

## 微调 MoE

> Mixtral 在 transformers 4.36.0 版本得到支持，可用 pip install transformers==4.36.0 --upgrade 安装

稠密模型与稀疏模型的过拟合动力学很不一样。稀疏模型更容易过拟合，所以可以探索在专家内部使用更强的正则（如 dropout）——比如稠密层一档 dropout 率、稀疏层用更高的一档。

一个问题是微调时要不要保留辅助损失。ST-MoE 作者试验过关掉辅助损失，质量没有显著影响——即使最多 11% 的 token 被丢弃。token 丢弃本身可能就是一种防过拟合的正则化。

Switch Transformers 观察到：在相同预训练 perplexity 下，稀疏模型在下游任务上不如稠密对应物，尤其是 SuperGLUE 这类重推理的任务。而在 TriviaQA 这类重知识的任务上，稀疏模型反而表现出色。作者还观察到更少的专家数量对微调更有利。另一个佐证泛化问题的观察是：模型在小任务上表现更差，在大任务上表现更好。

小任务（左）中能看到明显的过拟合——稀疏模型在验证集上差得多；较大的任务（右）中 MoE 表现出色。此图来自 ST-MoE 论文。

你还可以尝试冻结所有非专家权重，即只更新 MoE 层——这会导致性能大幅下降。反过来做倒是可行：只冻结 MoE 层的参数，效果几乎和更新全部参数一样好。这能帮助微调提速并降低内存消耗。这一点可能有点反直觉，因为（在 ST-MoE 项目中）80% 的参数在 MoE 层里。他们对该架构的解释是：专家层只占 1/4 的层数，且每个 token 每层最多经过两个专家，所以更新 MoE 参数影响的层数比更新其他参数少得多。

只冻结 MoE 层即可在保住质量的同时加速训练。此图来自 ST-MoE 论文。

微调稀疏 MoE 还有一个要留意的点：它们的微调超参设置不同——稀疏模型通常从更小的 batch size 和更高的学习率中获益更多。

更高的学习率加更小的 batch size 能提升稀疏模型的微调质量。此图来自 ST-MoE 论文。

读到这里，你可能有点沮丧：大家微调 MoE 一直磕磕绊绊。令人兴奋的是，近期论文 [MoEs Meets Instruction Tuning](https://arxiv.org/pdf/2305.14705.pdf)（2023 年 7 月）做了三类实验：

- 单任务微调
- 多任务指令微调
- 多任务指令微调后再单任务微调

作者把 MoE 与对应的 T5 一起微调时，T5 更好。但当他们对 Flan T5（T5 的 instruct 版）对应的 MoE 做指令微调时，MoE 的表现显著更好。不仅如此，Flan-MoE 相对 MoE 的提升幅度大于 Flan-T5 相对 T5 的提升——这表明 MoE 从指令微调中的获益可能比稠密模型更大。MoE 还从更多的任务数量中获益。与前文建议关掉辅助损失相反，在指令微调场景下该损失实际上能防过拟合。

稀疏模型从指令微调中的获益大于稠密模型。此图来自 MoEs Meets Instruction Tuning 论文。

## 什么时候用稀疏 MoE，什么时候用稠密模型？

在高吞吐、机器很多的场景，专家很有用。给定固定的预训练算力预算，稀疏模型更优。而在低吞吐、VRAM 有限的场景，稠密模型更好。

**注意：**不能直接拿稀疏模型和稠密模型的参数数量互相比较——两者代表的意义完全不同。

## 让 MoE 跑起飞（brrr）

最早的 MoE 工作把 MoE 层呈现成一种分支结构，导致计算缓慢（GPU 不是为它设计的），而且设备间要互相传信息，网络带宽成了瓶颈。这一节介绍已有的工作，让 MoE 的预训练和推理更可落地。MoE 起飞 brrrrr。

### 并行

先快速回顾并行方式：

- **数据并行**：同样的权重复制到所有核心，数据切分到各核心。
- **模型并行**：模型切分到各核心，数据在各核心复制。
- **模型并行 + 数据并行**：模型和数据都切分。注意不同核心处理的是不同的数据 batch。
- **专家并行（Expert Parallelism）**：专家放在不同 worker 上。若与数据并行结合，每个核心各有一个专家，数据切分到所有核心。

专家并行下，专家分布在不同 worker 上，每个 worker 拿不同的训练样本 batch。对非 MoE 层，专家并行与数据并行的行为相同；对 MoE 层，序列中的 token 被发往所需专家所在的 worker。

Switch Transformers 论文中展示数据与模型如何在各核心上按不同并行方式切分的示意图。

### 容量因子与通信成本

增大容量因子（CF）会提升质量，但会抬高通信成本和激活值的内存占用。如果 all-to-all 通信很慢，就用更小的容量因子。一个好的起点是：top-2 路由 + 容量因子 1.25 + 每核心一个专家。评估时可以调小容量因子以降低计算量。

### 服务化技术

> 你可以把 mistralai/Mixtral-8x7B-Instruct-v0.1 部署到 Inference Endpoints。

MoE 的一大缺点是参数量庞大。本地场景可能想用更小的模型。快速聊几个有助于部署的技术：

- Switch Transformers 作者做过早期蒸馏实验。把 MoE 蒸馏回稠密对应物后，仍能保住 30-40% 的稀疏收益。蒸馏因此同时带来「快速预训练」与「生产环境用小模型」两个好处。
- 近期一些方法修改路由，把完整句子或任务整体路由给某个专家，从而可以抽取子网络用于服务化。
- 专家聚合（Aggregation of Experts，MoE 的双关）：把专家的权重合并，减少推理时的参数量。

### 高效训练再谈

FasterMoE（2022 年 3 月）分析 MoE 在高效分布式系统上的性能，研究各种并行策略的理论极限，还提出让专家热门度倾斜的技术、降低延迟的细粒度通信调度，以及一个按最低延迟选专家、拓扑感知的改进门控——带来 17 倍加速。

Megablocks（2022 年 11 月）通过提供新的 GPU kernel 来处理 MoE 中的动态性，探索高效稀疏预训练。其方案从不丢弃 token，并能高效映射到现代硬件，带来显著加速。诀窍是什么？传统 MoE 用批量矩阵乘法（batched matmul），假设所有专家形状相同、token 数相同。Megablocks 则把 MoE 层表达为块稀疏（block-sparse）运算，能够容纳不均衡的分配。

不同大小专家、不同 token 数下的块稀疏矩阵乘法（来自 [MegaBlocks](https://arxiv.org/abs/2211.15841)）。

## 开源 MoE

现在有好几个可以训练 MoE 的开源项目：

- Megablocks：[https://github.com/stanford-futuredata/megablocks](https://github.com/stanford-futuredata/megablocks)
- Fairseq：[https://github.com/facebookresearch/fairseq/tree/main/examples/moe_lm](https://github.com/facebookresearch/fairseq/tree/main/examples/moe_lm)
- OpenMoE：[https://github.com/XueFuzhao/OpenMoE](https://github.com/XueFuzhao/OpenMoE)

已发布的开放获取 MoE 可以看：

- [Switch Transformers（Google）](https://huggingface.co/collections/google/switch-transformers-release-6548c35c6507968374b56d1f)：基于 T5 的 MoE 合集，从 8 到 2048 个专家，最大模型 1.6 万亿参数。
- [NLLB MoE（Meta）](https://huggingface.co/facebook/nllb-moe-54b)：NLLB 翻译模型的 MoE 版本。
- [OpenMoE](https://huggingface.co/fuzhao)：社区项目，发布了基于 Llama 的 MoE。
- [Mixtral 8x7B（Mistral）](https://huggingface.co/mistralai)：高质量 MoE，性能超过 Llama 2 70B 且推理快得多，同时发布了 instruct 微调版。详见[公告博客](https://mistral.ai/news/mixtral-of-experts/)。

## 令人兴奋的方向

对**蒸馏**的进一步实验：把稀疏 MoE 蒸馏成参数更少但质量相近的稠密模型。

另一个领域是 MoE 的量化。[QMoE](https://arxiv.org/abs/2310.16795)（2023 年 10 月）是该方向的好进展：把 MoE 量化到每参数不到 1 bit，将原本需要 3.2TB 加速器的 1.6T Switch Transformer 压缩到仅 160GB。

所以 TL;DR，值得探索的方向：

- 把 Mixtral 蒸馏成稠密模型
- 探索专家模型合并（model merging）技术及其对推理时的影响
- 对 Mixtral 做极端量化

## 一些资料

- [Adaptive Mixture of Local Experts (1991)](https://www.cs.toronto.edu/~hinton/absps/jjnh91.pdf)
- [Learning Factored Representations in a Deep Mixture of Experts (2013)](https://arxiv.org/abs/1312.4314)
- [Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer (2017)](https://arxiv.org/abs/1701.06538)
- [GShard: Scaling Giant Models with Conditional Computation and Automatic Sharding (Jun 2020)](https://arxiv.org/abs/2006.16668)
- [GLaM: Efficient Scaling of Language Models with Mixture-of-Experts (Dec 2021)](https://arxiv.org/abs/2112.06905)
- [Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity (Jan 2022)](https://arxiv.org/abs/2101.03961)
- [ST-MoE: Designing Stable and Transferable Sparse Expert Models (Feb 2022)](https://arxiv.org/abs/2202.08906)
- [FasterMoE: modeling and optimizing training of large-scale dynamic pre-trained models (April 2022)](https://dl.acm.org/doi/10.1145/3503221.3508418)
- [MegaBlocks: Efficient Sparse Training with Mixture-of-Experts (Nov 2022)](https://arxiv.org/abs/2211.15841)
- [Mixture-of-Experts Meets Instruction Tuning: A Winning Combination for Large Language Models (May 2023)](https://arxiv.org/abs/2305.14705)
- [Mixtral-8x7B-v0.1](https://huggingface.co/mistralai/Mixtral-8x7B-v0.1)、[Mixtral-8x7B-Instruct-v0.1](https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1)。

## 引用

```
@misc {sanseviero2023moe,
    author       = { Omar Sanseviero and
                     Lewis Tunstall and
                     Philipp Schmid and
                     Sourab Mangrulkar and
                     Younes Belkada and
                     Pedro Cuenca
                   },
    title        = { Mixture of Experts Explained },
    year         = 2023,
    url          = { https://huggingface.co/blog/moe },
    publisher    = { Hugging Face Blog }
}
```

```
Sanseviero, et al., "Mixture of Experts Explained", Hugging Face Blog, 2023.
```
