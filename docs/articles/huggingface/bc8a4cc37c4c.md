---
vendor: huggingface
title: The Reformer - 突破语言建模的极限
original_title: The Reformer - Pushing the limits of language modeling
url: https://huggingface.co/blog/reformer
date: 2023-01-24
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 90f9640dbb0e
---

返回文章列表

# The Reformer - 突破语言建模的极限

发布于
					2020 年 7 月 3 日

在 GitHub 上更新



- [![](https://huggingface.co/avatars/ce9b99882a65fd2cb983ba71a5ac2473.svg)](https://huggingface.co/a-r-r-o-w)
- [![](https://huggingface.co/avatars/2211bd0a7d08bf1e078b0acee40894b5.svg)](https://huggingface.co/Vivek)
- [![](https://huggingface.co/avatars/6be635f7f258d1050cd4c6e2c2d92a62.svg)](https://huggingface.co/kamalelsaaid)

Patrick von Platen

patrickvonplaten

本文也有中文版本 [简体中文](https://huggingface.co/blog/zh/reformer)。

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/patrickvonplaten/blog/blob/main/notebooks/03_reformer.ipynb)

## Reformer 如何用不到 8GB 内存训练五十万 token 的序列

[Kitaev、Kaiser 等（2020）](https://arxiv.org/pdf/2001.04451.pdf) 提出的 Reformer 模型，是当今面向长序列建模最省内存的 transformer 模型之一。

近来，长序列建模掀起了一股热潮，仅今年一年的投稿就可见一斑——[Beltagy et al. (2020)](https://arxiv.org/abs/2004.05150)、[Roy et al. (2020)](https://arxiv.org/abs/2003.05997)、[Tay et al.](https://arxiv.org/abs/2002.11296)、[Wang et al.](https://arxiv.org/abs/2006.04768) 等等，这里就不一一列举。长序列建模背后的动机在于，NLP 里许多任务——*例如* 摘要、问答——要求模型处理的输入序列比 BERT 这类模型所能处理的更长。在那些要求模型处理大输入序列的任务里，长序列模型不必为了避免内存溢出而裁剪输入序列，因此已被证明优于标准的"BERT"式模型，参见 [Beltagy et al. (2020)](https://arxiv.org/abs/2004.05150)。

Reformer 把它能一次处理多达五十万 token 的能力推到了长序列建模的极限，如这个 [demo](https://github.com/patrickvonplaten/notebooks/blob/master/PyTorch_Reformer.ipynb) 所示。作为对比，一个常规的 `bert-base-uncased` 模型把输入长度限制在仅 512 token。在 Reformer 里，标准 transformer 架构的每一部分都被重新设计，以在性能没有显著下降的前提下优化到最小的内存需求。

内存上的改进可以归功于 Reformer 作者带给 transformer 世界的 **4** 个特性：

- **Reformer 自注意力层** —— *如何在不局限于局部上下文的前提下高效实现自注意力？*
- **分块前馈层** —— *如何让大型前馈层有更好的时间-内存权衡？*
- **可逆残差层** —— *如何通过巧妙的残差架构大幅降低训练时的内存消耗？*
- **轴向位置编码** —— *如何让位置编码可用于极长的输入序列？*

本博客的目标是让读者对上述四个 Reformer 特性中的每一个都有 **深入** 的理解。虽然讲解聚焦于 Reformer，读者也应当对这四个特性在什么情形下对其他 transformer 模型同样有效有一个更好的直觉。这四节之间的联系只是松散的，因此完全可以单独阅读。

Reformer 是 🤗Transformers 库的一部分。对于所有 Reformer 用户，建议通读这篇非常详尽的博客，以更好地理解模型如何工作、以及如何正确设置它的配置。所有公式都附带了它在 Reformer 配置里对应的名字，*例如* `config.<param_name>`，以便读者快速对应官方文档和配置文件。

**注意**：*轴向位置编码* 在官方 Reformer 论文里没有解释，但在官方代码库里被大量使用。本博客给出了对轴向位置编码的首个深入解释。

## 1. Reformer 自注意力层

Reformer 使用两种特殊的自注意力层：*局部* 自注意力层和敏感 locality 哈希（*LSH*，Locality Sensitive Hashing）自注意力层。

为了更好地引入这些新的自注意力层，我们先简要回顾 [Vaswani et al. 2017](https://arxiv.org/abs/1706.03762) 提出的常规自注意力。

本博客采用与那篇广受欢迎 [The illustrated transformer](http://jalammar.github.io/illustrated-transformer/) 博客相同的记号和配色，因此强烈建议读者先读那篇。

**重要**：虽然 Reformer 最初是为因果自注意力提出的，它同样可以很好地用于双向自注意力。在本文里，Reformer 的自注意力以 *双向* 自注意力的形式呈现。

### 回顾全局自注意力

每个 Transformer 模型的核心是 **自注意力** 层。为了回顾常规自注意力层——这里我们称之为 **全局自注意力** 层——假设我们把一个 transformer 层施加在嵌入向量序列 X=x1,…,xn\mathbf{X} = \mathbf{x}_1, \ldots, \mathbf{x}_nX=x1​,…,xn​ 上，其中每个向量 xi\mathbf{x}_{i}xi​ 大小为 `config.hidden_size`，*即* dhd_hdh​。

简而言之，全局自注意力层把 X\mathbf{X}X 投影到查询、键和值矩阵 Q,K,V\mathbf{Q}, \mathbf{K}, \mathbf{V}Q,K,V，并用 *softmax* 运算按如下方式计算输出 Z\mathbf{Z}Z：Z=SelfAttn(X)=softmax(QKT)V\mathbf{Z} = \text{SelfAttn}(\mathbf{X}) = \text{softmax}(\mathbf{Q}\mathbf{K}^T) \mathbf{V}Z=SelfAttn(X)=softmax(QKT)V，其中 Z\mathbf{Z}Z 的维度为 dh×nd_h \times ndh​×n（为简洁略去键归一化因子和自注意力权重 WO\mathbf{W}^{O}WO）。关于完整 transformer 操作的更多细节，见 [the illustrated transformer](http://jalammar.github.io/illustrated-transformer/)。

视觉上，对 n=16,dh=3n=16, d_h=3n=16,dh​=3 我们可以把该操作图示如下：

[![alt text](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/conventional_attention.png)](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/conventional_attention.png)

注意所有可视化中 `batch_size` 和 `config.num_attention_heads` 都假设为 1。有些向量，*例如* x3\mathbf{x_3}x3​ 和它对应的输出向量 z3\mathbf{z_3}z3​ 被特别标注，以便后面更好地解释 *LSH 自注意力*。所呈现的逻辑可以毫不费力地扩展到多头条自注意力（`config.num_attention_{h}eads` > 1）。建议读者阅读 [the illustrated transformer](http://jalammar.github.io/illustrated-transformer/) 作为多头条自注意力的参考。

需要记住的是，对每个输出向量 zi\mathbf{z}_{i}zi​，整个输入序列 X\mathbf{X}X 都会被处理。内部点积张量 QKT\mathbf{Q}\mathbf{K}^TQKT 的渐近内存复杂度为 O(n2)\mathcal{O}(n^2)O(n2)，这通常代表 transformer 模型的内存瓶颈。

这也是为什么 `bert-base-cased` 的 `config.max_position_embedding_size` 只有 512 的原因。

### 局部自注意力

**局部自注意力** 是降低 O(n2)\mathcal{O}(n^2)O(n2) 内存瓶颈、让我们能以更低计算成本建模更长序列的直观方案。在局部自注意力里，输入 X=X1:n=x1,…,xn \mathbf{X} = \mathbf{X}_{1:n} = \mathbf{x}_{1}, \ldots, \mathbf{x}_{n} X=X1:n​=x1​,…,xn​ 被切成 ncn_{c}nc​ 个块：X=[X1:lc,…,X(nc−1)∗lc:nc∗lc] \mathbf{X} = \left[\mathbf{X}_{1:l_{c}}, \ldots, \mathbf{X}_{(n_{c} - 1) * l_{c} : n_{c} * l_{c}}\right] X=[X1:lc​​,…,X(nc​−1)∗lc​:nc​∗lc​​]，每个长度 `config.local_chunk_length`，*即* lcl_{c}lc​，随后全局自注意力分别施加在每个块上。

让我们再次取 n=16,dh=3n=16, d_h=3n=16,dh​=3 的输入序列做可视化：

[![alt text](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/input.png)](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/input.png)

假设 lc=4,nc=4l_{c} = 4, n_{c} = 4lc​=4,nc​=4，分块注意力可以图示如下：

[![alt text](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/chunked_attention_1.png)](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/chunked_attention_1.png)

可以看到，注意力运算分别施加在每个块 X1:4,X5:8,X9:12,X13:16\mathbf{X}_{1:4}, \mathbf{X}_{5:8}, \mathbf{X}_{9:12}, \mathbf{X}_{13:16}X1:4​,X5:8​,X9:12​,X13:16​ 上。这个架构的第一个缺点显而易见：某些输入向量无法访问其紧邻上下文，*例如* 在我们的例子里 x9\mathbf{x}_9x9​ 无法访问 x8\mathbf{x}_{8}x8​，反之亦然。这成问题，因为这些 token 无法学到考虑其紧邻上下文的词表示。

一个简单的补救办法是给每个块附加 `config.local_num_chunks_before`，*即* npn_{p}np​ 个块和 `config.local_num_chunks_after`，*即* nan_{a}na​，从而让每个输入向量至少能访问前 npn_{p}np​ 个输入向量和后 nan_{a}na​ 个输入向量。这也可以理解为带重叠的分块，其中 npn_{p}np​ 和 nan_{a}na​ 定义了每个块与所有前块和后块的重叠量。我们把这种扩展的局部自注意力记为：

Zloc=[Z1:lcloc,…,Z(nc−1)∗lc:nc∗lcloc],\mathbf{Z}^{\text{loc}} = \left[\mathbf{Z}_{1:l_{c}}^{\text{loc}}, \ldots, \mathbf{Z}_{(n_{c} - 1) * l_{c} : n_{c} * l_{c}}^{\text{loc}}\right], Zloc=[Z1:lc​loc​,…,Z(nc​−1)∗lc​:nc​∗lc​loc​], 其中 Zlc∗(i−1)+1:lc∗iloc=SelfAttn(Xlc∗(i−1−np)+1:lc∗(i+na))[np∗lc:−na∗lc],∀i∈{1,…,nc}\mathbf{Z}_{l_{c} * (i - 1) + 1 : l_{c} * i}^{\text{loc}} = \text{SelfAttn}(\mathbf{X}_{l_{c} * (i - 1 - n_{p}) + 1: l_{c} * (i + n_{a})})\left[n_{p} * l_{c}: -n_{a} * l_{c}\right], \forall i \in \{1, \ldots, n_{c} \}Zlc​∗(i−1)+1:lc​∗iloc​=SelfAttn(Xlc​∗(i−1−np​)+1:lc​∗(i+na​)​)[np​∗lc​:−na​∗lc​],∀i∈{1,…,nc​}

好吧，这个公式看起来很复杂。我们把它简化一下。在 Reformer 的自注意力层里 nan_{a}na​ 通常设为 0，npn_{p}np​ 设为 1，那我们把公式对 i=1i = 1i=1 重写一遍：

Z1:lcloc=SelfAttn(X−lc+1:lc)[lc:]\mathbf{Z}_{1:l_{c}}^{\text{loc}} = \text{SelfAttn}(\mathbf{X}_{-l_{c} + 1: l_{c}})\left[l_{c}:\right]Z1:lc​loc​=SelfAttn(X−lc​+1:lc​​)[lc​:]

我们注意到这里存在循环关系，于是第一个段可以访问最后一个段。让我们再次图示这种略微增强的局部注意力。首先，我们在每个加窗段内施加自注意力，只保留中心的输出段。

[![alt text](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/local_attention_2.png)](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/local_attention_2.png)

最后，相关输出被拼接成 Zloc\mathbf{Z}^{\text{loc}}Zloc，看起来如下。

[![alt text](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/local_attention_3.png)](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/local_attention_3.png)

注意局部自注意力以高效方式实现，因此不会像这里为图示所画的那样先算出输出再"丢弃"（红叉）。

这里重要的是，为每个分块自注意力函数扩展输入向量，会让该自注意力函数 *每一个* 输出向量 zi \mathbf{z}_{i} zi​ 能学到更好的向量表示。例如输出向量 z5loc,z6loc,z7loc,z8loc \mathbf{z}_{5}^{\text{loc}}, \mathbf{z}_{6}^{\text{loc}}, \mathbf{z}_{7}^{\text{loc}}, \mathbf{z}_{8}^{\text{loc}} z5loc​,z6loc​,z7loc​,z8loc​ 中的每一个都能考虑所有输入向量 X1:8 \mathbf{X}_{1:8} X1:8​ 来学习更好的表示。

内存消耗上的收益相当直观：O(n2) \mathcal{O}(n^2) O(n2) 的内存复杂度被逐段分解，于是总渐近内存消耗降到 O(nc∗lc2)=O(n∗lc) \mathcal{O}(n_{c} * l_{c}^2) = \mathcal{O}(n * l_{c}) O(nc​∗lc2​)=O(n∗lc​)。

这种增强的局部自注意力优于原始的局部自注意力架构，但仍有主要缺点：每个输入向量只能访问一个预定义大小的局部上下文。对于不需要 transformer 模型学习输入向量间长程依赖的 NLP 任务——可以说 *例如* 语音识别、命名实体识别和短句子的因果语言建模——这未必是大问题。许多 NLP 任务确实要求模型学习长程依赖，于是局部自注意力可能导致显著的性能退化，*例如*

- *问答*：模型必须学习问题 token 与相关答案 token 之间的关系，而它们很可能不在同一局部范围内
- *多选*：模型必须把多个答案 token 段彼此比较，而它们通常被显著的长度隔开
- *摘要*：模型必须学习长上下文 token 序列与短摘要 token 序列之间的关系，而上下文与摘要之间的相关关系很可能无法被局部自注意力捕捉
- 等等……

局部自注意力单用很可能不足以让 transformer 模型学到输入向量（token）彼此之间的相关关系。

因此，Reformer 还额外采用了一个高效自注意力层来近似全局自注意力，称为 *LSH 自注意力*。

### LSH 自注意力

好，既然我们理解了局部自注意力如何工作，就可以来啃 Reformer 最具创新性的部分了：**敏感 locality 哈希（LSH）自注意力**。

LSH 自注意力的前提是：在近似全局自注意力的同时，效率大致与局部自注意力相当。

LSH 自注意力依赖 [Andoni et al (2015)](https://arxiv.org/abs/1509.02897) 提出的 LSH 算法，故得其名。

LSH 自注意力背后的想法基于一个洞察：如果 nnn 很大，施加在 QKT\mathbf{Q}\mathbf{K}^TQKT 注意力点积上的 softmax 对每个查询向量只会给很少几个值向量赋予显著大于 0 的权重。

让我们解释得更细一点。设 ki∈K=[k1,…,kn]T\mathbf{k}_{i} \in \mathbf{K} = \left[\mathbf{k}_1, \ldots, \mathbf{k}_n \right]^Tki​∈K=[k1​,…,kn​]T 和 qi∈Q=[q1,…,qn]T\mathbf{q}_{i} \in \mathbf{Q} = \left[\mathbf{q}_1, \ldots, \mathbf{q}_n\right]^Tqi​∈Q=[q1​,…,qn​]T 为键和查询向量。对每个 qi\mathbf{q}_{i}qi​，softmax(qiTKT)\text{softmax}(\mathbf{q}_{i}^T \mathbf{K}^T)softmax(qi​T​KT) 可以通过只使用那些与 qi\mathbf{q}_{i}qi​ 有高余弦相似度的键向量 kj\mathbf{k}_{j}kj​ 来近似。这归因于 softmax 函数对更大的输入值指数级地赋予更多权重。到目前为止挺好，下一个问题是如何高效地找到对每个 iii 都与 qi\mathbf{q}_{i}qi​ 具有高余弦相似度的向量。

首先，Reformer 作者发现共享查询和键投影 Q=K\mathbf{Q} = \mathbf{K}Q=K 不会影响 transformer 模型的性能 1{}^11。于是，不用为每个查询向量 qiq_iqi​ 去找高余弦相似度的键向量，只需要找查询向量彼此之间的余弦相似度。这很关键，因为查询-查询向量点积近似有一个传递性质：如果 qi\mathbf{q}_{i}qi​ 与查询向量 qj\mathbf{q}_{j}qj​ 和 qk\mathbf{q}_{k}qk​ 有高余弦相似度，那么 qj\mathbf{q}_{j}qj​ 也与 qk\mathbf{q}_{k}qk​ 有高余弦相似度。因此查询向量可以被聚成桶，使得属于同一桶的所有查询向量彼此都有高余弦相似度。我们把 CmC_{m}Cm​ 定义为第 *m* 个位置索引集合，使其对应的查询向量在同一个桶里：Cm={i∣ s.t. qi∈mth cluster}C_{m} = \{ i | \text{ s.t. } \mathbf{q}_{i} \in \text{mth cluster}\}Cm​={i∣ s.t. qi​∈mth cluster}，并把 `config.num_buckets`，*即* nbn_{b}nb​，定义为桶的数量。

对每个索引集合 CmC_{m}Cm​，softmax 函数在对应查询向量桶上 softmax(Qi∈CmQi∈CmT)\text{softmax}(\mathbf{Q}_{i \in C_{m}} \mathbf{Q}^T_{i \in C_{m}})softmax(Qi∈Cm​​Qi∈Cm​T​) 近似了共享查询和键投影的全局自注意力 softmax 函数 softmax(qiTQT)\text{softmax}(\mathbf{q}_{i}^T \mathbf{Q}^T)softmax(qi​T​QT)，对 CmC_{m}Cm​ 中的所有位置索引 iii。

其次，作者利用 **LSH** 算法把查询向量聚成预定义数量的桶 nbn_{b}nb​。LSH 算法在这里是理想选择，因为它非常高效，并且是余弦相似度最近邻算法的近似。解释 LSH 方案超出了本 notebook 的范围，所以我们只需记住：对每个向量 qi\mathbf{q}_{i}qi​，LSH 算法把它的位置索引 iii 归到 nbn_{b}nb​ 个预定义桶之一，*即* LSH(qi)=m\text{LSH}(\mathbf{q}_{i}) = mLSH(qi​)=m，其中 i∈{1,…,n}i \in \{1, \ldots, n\}i∈{1,…,n} 且 m∈{1,…,nb}m \in \{1, \ldots, n_{b}\}m∈{1,…,nb​}。

视觉上，对我们最初的示例可以这样图示：

[![alt text](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/lsh_hashing.png)](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/lsh_hashing.png)

第三，可以注意到，把所有查询向量聚进 nbn_{b}nb​ 个桶之后，可以用对应的索引集合 CmC_{m}Cm​ 来相应地置换输入向量 x1,…,xn\mathbf{x}_1, \ldots, \mathbf{x}_nx1​,…,xn​ 2{}^22，从而可以像局部注意力那样分段地施加共享查询-键自注意力。

用我们的示例输入向量 X=x1,...,x16\mathbf{X} = \mathbf{x}_1, ..., \mathbf{x}_{16}X=x1​,...,x16​ 来澄清，并假设 `config.num_buckets=4` 和 `config.lsh_chunk_length = 4`。看上面的图，可以看到我们把每个查询向量 q1,…,q16 \mathbf{q}_1, \ldots, \mathbf{q}_{16} q1​,…,q16​ 分配到了 C1,C2,C3,C4 \mathcal{C}_{1}, \mathcal{C}_{2}, \mathcal{C}_{3}, \mathcal{C}_{4} C1​,C2​,C3​,C4​ 四个簇之一。如果现在我们相应地对输入向量 x1,…,x16 \mathbf{x}_1, \ldots, \mathbf{x}_{16} x1​,…,x16​ 排序，就得到以下置换后的输入 X′ \mathbf{X'} X′：

[![alt text](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/lsh_perm.png)](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/lsh_perm.png)

自注意力机制应当对每个簇分别施加，于是对每个簇 Cm \mathcal{C}_m Cm​，对应输出按如下方式计算：Zi∈CmLSH=SelfAttnQ=K(Xi∈Cm) \mathbf{Z}^{\text{LSH}}_{i \in \mathcal{C}_m} = \text{SelfAttn}_{\mathbf{Q}=\mathbf{K}}(\mathbf{X}_{i \in \mathcal{C}_m}) Zi∈Cm​LSH​=SelfAttnQ=K​(Xi∈Cm​​)。

再次用我们的示例图示。

[![alt text](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/lsh_cluster_attn.png)](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/lsh_cluster_attn.png)

可以看到，自注意力函数在不同大小的矩阵上工作，这对 GPU 和 TPU 的高效批处理并不理想。

为了解决这个问题，可以用与局部注意力相同的方式对置换后的输入分块，使每个块的大小为 `config.lsh_chunk_length`。通过对置换后的输入分块，某个桶可能被拆到两个不同的块里。为了解决这个问题，在 LSH 自注意力里每个块除了自己之外还会关注它的前一个块 `config.lsh_num_chunks_before=1`，与局部自注意力相同（`config.lsh_num_chunks_after` 通常设为 0）。这样，我们可以确保桶内所有向量以高概率彼此关注 3{}^33。

总之对所有块 k∈{1,…,nc} k \in \{1, \ldots, n_{c}\} k∈{1,…,nc​}，LSH 自注意力可以记为：

Z′lc∗k+1:lc∗(k+1)LSH=SelfAttnQ=K(X′lc∗k+1):lc∗(k+1))[lc:] \mathbf{Z'}_{l_{c} * k + 1:l_{c} * (k + 1)}^{\text{LSH}} = \text{SelfAttn}_{\mathbf{Q} = \mathbf{K}}(\mathbf{X'}_{l_{c} * k + 1): l_{c} * (k + 1)})\left[l_{c}:\right] Z′lc​∗k+1:lc​∗(k+1)LSH​=SelfAttnQ=K​(X′lc​∗k+1):lc​∗(k+1)​)[lc​:]

其中 X′\mathbf{X'}X′ 和 Z′ \mathbf{Z'} Z′ 是按照 LSH 算法置换后的输入和输出向量。公式够复杂了，让我们图示 LSH 自注意力。

如上所示的置换向量 X′\mathbf{X'}X′ 被分块，共享查询键自注意力施加到每个块上。

[![alt text](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/lsh_attention_2.png)](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/lsh_attention_2.png)

最后，输出 Z′LSH\mathbf{Z'}^{\text{LSH}}Z′LSH 被重排回它原来的置换。

[![alt text](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/lsh_attention_3.png)](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/lsh_attention_3.png)

这里还需要提到的一个重要特性是，LSH 自注意力的准确性可以通过并行运行 `config.num_hashes` 次 LSH 自注意力来提升，比如 nhn_{h} nh​ 次，每次用不同的随机 LSH 哈希。通过设置 `config.num_hashes > 1`，对每个输出位置 i i i，会计算多个输出向量 ziLSH,1,…,ziLSH,nh \mathbf{z}^{\text{LSH}, 1}_{i}, \ldots, \mathbf{z}^{\text{LSH}, n_{h}}_{i} ziLSH,1​,…,ziLSH,nh​​ 并随后合并：ziLSH=∑knhZiLSH,k∗weightik \mathbf{z}^{\text{LSH}}_{i} = \sum_k^{n_{h}} \mathbf{Z}^{\text{LSH}, k}_{i} * \text{weight}^k_i ziLSH​=∑knh​​ZiLSH,k​∗weightik​。weightik \text{weight}^k_i weightik​ 表示哈希轮次 k k k 的输出向量 ziLSH,k \mathbf{z}^{\text{LSH}, k}_{i} ziLSH,k​ 相对于其他哈希轮次的重要性，与其 softmax 计算的归一化项成指数比例。背后的直觉是：如果对应的查询向量 qik \mathbf{q}_{i}^{k} qik​ 与所在块内所有其他查询向量具有高余弦相似度，那么该块的 softmax 归一化项往往较高，因此对应的输出向量 qik \mathbf{q}_{i}^{k} qik​ 应当是对全局注意力更好的近似，从而比 softmax 归一化项较低的哈希轮次的输出向量获得更多权重。更多细节见 [论文](https://arxiv.org/pdf/2001.04451.pdf) 附录 A。对我们的示例，多轮 LSH 自注意力可以图示如下。

[![alt text](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/lsh_attention_4.png)](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/lsh_attention_4.png)

很好，就这样。现在我们知道了 LSH 自注意力在 Reformer 里如何工作。

关于内存复杂度，现在有两个相互竞争的项来决定谁是内存瓶颈：点积 O(nh∗nc∗lc2)=O(n∗nh∗lc) \mathcal{O}(n_{h} * n_{c} * l_{c}^2) = \mathcal{O}(n * n_{h} * l_{c}) O(nh​∗nc​∗lc2​)=O(n∗nh​∗lc​) 以及 LSH 分桶所需内存 O(n∗nh∗nb2) \mathcal{O}(n * n_{h} * \frac{n_{b}}{2}) O(n∗nh​∗2nb​​)，其中 lc l_{c} lc​ 为块长度。因为对大 n n n，桶数 nb2 \frac{n_{b}}{2} 2nb​​ 比块长度 lc l_{c} lc​ 增长快得多，所以用户可以再次对桶数 `config.num_buckets` 做因式分解，如 [这里](https://huggingface.co/transformers/model_doc/reformer.html#lsh-self-attention) 所解释。

让我们快速回顾上面的内容：

- 我们想利用 softmax 运算只对很少几个键向量赋显著权重这一知识来近似全局注意力。
- 如果键向量等于查询向量，这意味着对 *每个* 查询向量 qi \mathbf{q}_{i} qi​，softmax 只对与它在余弦相似度上相似的其他查询向量赋显著权重。
- 这种关系是双向的，意味着如果 qj \mathbf{q}_{j} qj​ 与 qi \mathbf{q}_{i} qi​ 相似，那么 qj\mathbf{q}_{j} qj​ 也与 qi \mathbf{q}_{i} qi​ 相似，所以我们可以在把自注意力施加到置换输入之前先做全局聚类。
- 我们在置换后的输入上施加局部自注意力，并把输出重排回原来的置换。

1 {}^{1} 1 作者做了一些初步实验，确认共享查询键自注意力的表现与标准自注意力大致相当。

2 {}^{2} 2 更确切地说，桶内的查询向量按其原始顺序排序。这意味着，*例如* 如果向量 q1,q3,q7 \mathbf{q}_1, \mathbf{q}_3, \mathbf{q}_7 q1​,q3​,q7​ 都被哈希到桶 2，那么桶 2 里向量的顺序仍然是 q1 \mathbf{q}_1 q1​，然后是 q3 \mathbf{q}_3 q3​ 和 q7 \mathbf{q}_7 q7​。

3 {}^3 3 顺带一提，作者对查询向量 qi \mathbf{q}_{i} qi​ 施加了掩码，以防止该向量关注自己。因为一个向量对自身的余弦相似度总是与对其他向量的相似度一样高或更高，所以在共享查询键自注意力中强烈不鼓励查询向量关注自己。

### 基准

Transformers 最近加入了基准工具——见 [这里](https://github.com/huggingface/transformers/blob/master/notebooks/05-benchmark.ipynb) 获取更详细的说明。

要展示用 "局部" + "LSH" 自注意力能省多少内存，我们对 Reformer 模型 `google/reformer-enwik8` 在不同 `local_attn_chunk_length` 和 `lsh_attn_chunk_length` 下做了基准测试。`google/reformer-enwik8` 模型的默认配置和用法可在 [这里](https://huggingface.co/google/reformer-enwik8) 更详细地查看。

先做必要的导入和安装。

```
#@title Installs and Imports
# pip installs
!pip -qq install git+https://github.com/huggingface/transformers.git
!pip install -qq py3nvml

from transformers import ReformerConfig, PyTorchBenchmark, PyTorchBenchmarkArguments
```

首先，让我们用 *全局* 自注意力对 Reformer 模型的内存使用做基准测试。这可以通过把 `lsh_attn_chunk_length` = `local_attn_chunk_length` = 8192 来实现，于是对所有小于等于 8192 的输入序列，模型自动切换到全局自注意力。

```
config = ReformerConfig.from_pretrained("google/reformer-enwik8", lsh_attn_chunk_length=16386, local_attn_chunk_length=16386, lsh_num_chunks_before=0, local_num_chunks_before=0)
benchmark_args = PyTorchBenchmarkArguments(sequence_lengths=[2048, 4096, 8192, 16386], batch_sizes=[1], models=["Reformer"], no_speed=True, no_env_print=True)
benchmark = PyTorchBenchmark(configs=[config], args=benchmark_args)
result = benchmark.run()
```

```
HBox(children=(FloatProgress(value=0.0, description='Downloading', max=1279.0, style=ProgressStyle(description…



1 / 1
Doesn't fit on GPU. CUDA out of memory. Tried to allocate 2.00 GiB (GPU 0; 11.17 GiB total capacity; 8.87 GiB already allocated; 1.92 GiB free; 8.88 GiB reserved in total by PyTorch)

====================      INFERENCE - MEMORY - RESULT       ====================
--------------------------------------------------------------------------------
          Model Name             Batch Size     Seq Length    Memory in MB 
--------------------------------------------------------------------------------
           Reformer                  1              2048            1465     
           Reformer                  1              4096            2757     
           Reformer                  1              8192            7893     
           Reformer                  1             16386            N/A      
--------------------------------------------------------------------------------
```

输入序列越长，输入序列与峰值内存之间 O(n2) \mathcal{O}(n^2) O(n2) 的二次关系就越明显。可以看到，实践中需要长得多的输入序列才能清楚观察到把输入序列翻倍会使峰值内存变为四倍。

对一个使用全局注意力的 `google/reformer-enwik8` 模型，序列长度超过 16K 就会导致内存溢出。

现在，通过使用模型的默认参数来启用 *局部* 和 *LSH* 自注意力。

```
  config = ReformerConfig.from_pretrained("google/reformer-enwik8")
  benchmark_args = PyTorchBenchmarkArguments(sequence_lengths=[2048, 4096, 8192, 16384, 32768, 65436], batch_sizes=[1], models=["Reformer"], no_speed=True, no_env_print=True)
  benchmark = PyTorchBenchmark(configs=[config], args=benchmark_args)
  result = benchmark.run()
```

```
1 / 1
Doesn't fit on GPU. CUDA out of memory. Tried to allocate 2.00 GiB (GPU 0; 11.17 GiB total capacity; 7.85 GiB already allocated; 1.74 GiB free; 9.06 GiB reserved in total by PyTorch)
Doesn't fit on GPU. CUDA out of memory. Tried to allocate 4.00 GiB (GPU 0; 11.17 GiB total capacity; 6.56 GiB already allocated; 3.99 GiB free; 6.81 GiB reserved in total by PyTorch)

====================      INFERENCE - MEMORY - RESULT       ====================
--------------------------------------------------------------------------------
          Model Name             Batch Size     Seq Length    Memory in MB 
--------------------------------------------------------------------------------
           Reformer                  1              2048            1785     
           Reformer                  1              4096            2621     
           Reformer                  1              8192            4281     
           Reformer                  1             16384            7607     
           Reformer                  1             32768            N/A      
           Reformer                  1             65436            N/A      
--------------------------------------------------------------------------------
```

如预期的那样，对更长的输入序列使用局部和 LSH 自注意力内存效率高得多，以至于在本 notebook 里模型要到 16K token 才在一块 11GB 内存的 GPU 上出现内存溢出。

## 2. 分块前馈层

基于 transformer 的模型常常在自注意力层之后并行施加非常大的前馈层。这样，这一层可能占用相当一部分总体内存，有时甚至成为模型的内存瓶颈。分块前馈技术首次在 Reformer 论文中被提出，它允许用更多时间换取更好的内存消耗。

### Reformer 中的分块前馈层

在 Reformer 里，*LSH* 或 *局部* 自注意力层之后通常接一个残差连接，这构成 *transformer 块* 的第一部分。更多细节请参考这篇 [博客](http://jalammar.github.io/illustrated-transformer/)。

*transformer 块* 第一部分的输出，称为 *归一化自注意力* 输出，可以写作 Z‾=Z+X \mathbf{\overline{Z}} = \mathbf{Z} + \mathbf{X} Z=Z+X，其中 Z \mathbf{Z} Z 在 Reformer 中是 ZLSH \mathbf{Z}^{\text{LSH}} ZLSH 或 Zloc \mathbf{Z}^\text{loc} Zloc。

对我们的示例输入 x1,…,x16 \mathbf{x}_1, \ldots, \mathbf{x}_{16} x1​,…,x16​，我们把归一化自注意力输出图示如下。

[![alt text](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/layer_normed_output.png)](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/layer_normed_output.png)

现在，*transformer 块* 的第二部分通常由两个前馈层组成 1 ^{1} 1，定义为 Linearint(…) \text{Linear}_{\text{int}}(\ldots) Linearint​(…)，它把 Z‾ \mathbf{\overline{Z}} Z 处理为中间输出 Yint \mathbf{Y}_{\text{int}} Yint​，以及 Linearout(…) \text{Linear}_{\text{out}}(\ldots) Linearout​(…)，它把中间输出处理为输出 Yout \mathbf{Y}_{\text{out}} Yout​。这两个前馈层可以定义为

Yout=Linearout(Yint)=Linearout(Linearint(Z‾)).\mathbf{Y}_{\text{out}} = \text{Linear}_{\text{out}}(\mathbf{Y}_\text{int}) = \text{Linear}_{\text{out}}(\text{Linear}_{\text{int}}(\mathbf{\overline{Z}})).Yout​=Linearout​(Yint​)=Linearout​(Linearint​(Z))。

此刻需要记住重要的是，从数学上看，前馈层在位置 yout,i \mathbf{y}_{\text{out}, i} yout,i​ 的输出只依赖于该位置的输入 y‾i \mathbf{\overline{y}}_{i} y​i​。与自注意力层相反，每个输出 yout,i \mathbf{y}_{\text{out}, i} yout,i​ 因此完全独立于其他位置的不同输入 y‾j≠i \mathbf{\overline{y}}_{j \ne i} y​j​=i​。

让我们对 z‾1,…,z‾16 \mathbf{\overline{z}}_1, \ldots, \mathbf{\overline{z}}_{16} z1​,…,z16​ 图示前馈层。

[![alt text](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/feed_forward.png)](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/feed_forward.png)

如图中所示，所有输入向量 z‾i \mathbf{\overline{z}}_{i} zi​ 被同一个前馈层并行处理。

当查看前馈层的输出维度时就有意思了。在 Reformer 里，Linearint \text{Linear}_{\text{int}} Linearint​ 的输出维度定义为 `config.feed_forward_size`，*例如* df d_{f} df​，而 Linearout \text{Linear}_{\text{out}} Linearout​ 的输出维度定义为 `config.hidden_size`，*即* dh d_{h} dh​。

Reformer 作者观察到，在 transformer 模型里中间维度 df d_{f} df​ 通常远大于输出维度 2^{2}2 dh d_{h} dh​。这意味着维度为 df×n d_{f} \times n df​×n 的张量 Yint \mathbf{\mathbf{Y}}_\text{int} Yint​ 占据了总内存的相当一部分，甚至可能成为内存瓶颈。

为了对维度差异有更好的感觉，让我们画出示例中的矩阵 Yint \mathbf{Y}_\text{int} Yint​ 和 Yout \mathbf{Y}_\text{out} Yout​。

[![alt text](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/feed_forward_matrix.png)](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/feed_forward_matrix.png)

显然张量 Yint \mathbf{Y}_\text{int} Yint​ 占据比 Yout \mathbf{Y}_{\text{out}} Yout​ 多得多的内存（确切地说是 dfdh×n \frac{d_{f}}{d_{h}} \times n dh​df​​×n 倍）。但真的有必要计算完整的中间矩阵 Yint \mathbf{Y}_\text{int} Yint​ 吗？并不，因为相关的只是输出矩阵 Yout \mathbf{Y}_\text{out} Yout​。为了用内存换速度，可以把线性层的计算按块进行，每次只处理一个块。把 `config.chunk_size_feed_forward` 定义为 cf c_{f} cf​，分块线性层定义为 Yout=[Yout,1:cf,…,Yout,(n−cf):n] \mathbf{Y}_{\text{out}} = \left[\mathbf{Y}_{\text{out}, 1: c_{f}}, \ldots, \mathbf{Y}_{\text{out}, (n - c_{f}): n}\right] Yout​=[Yout,1:cf​​,…,Yout,(n−cf​):n​]，其中 Yout,(cf∗i):(i∗cf+i)=Linearout(Linearint(Z‾(cf∗i):(i∗cf+i))) \mathbf{Y}_{\text{out}, (c_{f} * i): (i * c_{f} + i)} = \text{Linear}_{\text{out}}(\text{Linear}_{\text{int}}(\mathbf{\overline{Z}}_{(c_{f} * i): (i * c_{f} + i)})) Yout,(cf​∗i):(i∗cf​+i)​=Linearout​(Linearint​(Z(cf​∗i):(i∗cf​+i)​))。实践中，它只是意味着输出被增量计算并拼接，以避免把整个中间张量 Yint \mathbf{Y}_{\text{int}} Yint​ 存进内存。

假设示例里 cf=1 c_{f}=1 cf​=1，我们可以把对位置 i=9 i=9 i=9 的增量输出计算图示如下。

[![alt text](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/chunked_feed_forward.png)](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/chunked_feed_forward.png)

通过以大小为 1 的块处理输入，唯一需要同时存进内存的张量是最大尺寸为 16×dh 16 \times d_{h} 16×dh​ 的 Yout \mathbf{Y}_\text{out} Yout​、大小为 df d_{f} df​ 的 yint,i \mathbf{y}_{\text{int}, i} yint,i​ 以及大小为 16×dh 16 \times d_{h} 16×dh​ 的输入 Z‾ \mathbf{\overline{Z}} Z，其中 dh d_{h} dh​ 为 `config.hidden_size` 3^{3}3。

最后需要记住的是，*分块线性层* 产生的输出在数学上等价于常规线性层，因此可以施加到所有 transformer 线性层上。利用 `config.chunk_size_feed_forward` 因而在某些用例中允许更好的内存与速度权衡。

1 {}^1 1 在前两节里，我们省略了施加在自注意力层和线性层之前的 layer norm 层。读者应当知道，X \mathbf{X} X 和 Z‾ \mathbf{\overline{Z}} Z 在被送入自注意力和线性层之前都先经过 layer normalization。 2 {}^2 2 在 `bert-base-uncased` 里，*例如* 中间维度 df d_{f} df​ 是 3072，是输出维度 dh d_{h} dh​ 的四倍。 3 {}^3 3 提醒一下，为清晰和图示起见，本 notebook 中 `config.num_attention_heads` 都假设为 1，因此自注意力层的输出可以认为大小为 `config.hidden_size`。

关于分块线性 / 前馈层的更多信息也可以在 🤗Transformers 文档 [这里](https://huggingface.co/transformers/glossary.html#feed-forward-chunking) 找到。

### 基准

让我们测试用分块前馈层能省多少内存。

```
#@title Installs and Imports
# pip installs
!pip -qq install git+https://github.com/huggingface/transformers.git
!pip install -qq py3nvml

from transformers import ReformerConfig, PyTorchBenchmark, PyTorchBenchmarkArguments
```

```
  Building wheel for transformers (setup.py) ... [?25l[?25hdone
```

首先，比较默认 `google/reformer-enwik8` 模型（不带分块前馈层）与带分块前馈层的版本。

```
config_no_chunk = ReformerConfig.from_pretrained("google/reformer-enwik8")  # no chunk
config_chunk = ReformerConfig.from_pretrained("google/reformer-enwik8", chunk_size_feed_forward=1)  # feed forward chunk
benchmark_args = PyTorchBenchmarkArguments(sequence_lengths=[1024, 2048, 4096], batch_sizes=[8], models=["Reformer-No-Chunk", "Reformer-Chunk"], no_speed=True, no_env_print=True)
benchmark = PyTorchBenchmark(configs=[config_no_chunk, config_chunk], args=benchmark_args)
result = benchmark.run()
```

```
1 / 2
Doesn't fit on GPU. CUDA out of memory. Tried to allocate 2.00 GiB (GPU 0; 11.17 GiB total capacity; 7.85 GiB already allocated; 1.74 GiB free; 9.06 GiB reserved in total by PyTorch)
2 / 2
Doesn't fit on GPU. CUDA out of memory. Tried to allocate 2.00 GiB (GPU 0; 11.17 GiB total capacity; 7.85 GiB already allocated; 1.24 GiB free; 9.56 GiB reserved in total by PyTorch)

====================      INFERENCE - MEMORY - RESULT       ====================
--------------------------------------------------------------------------------
          Model Name             Batch Size     Seq Length    Memory in MB 
--------------------------------------------------------------------------------
      Reformer-No-Chunk              8              1024            4281     
      Reformer-No-Chunk              8              2048            7607     
      Reformer-No-Chunk              8              4096            N/A      
        Reformer-Chunk               8              1024            4309     
        Reformer-Chunk               8              2048            7669     
        Reformer-Chunk               8              4096            N/A      
--------------------------------------------------------------------------------
```

有意思，分块前馈层看起来在这里完全没起作用。原因是 `config.feed_forward_size` 不够大，无法造成真正的差异。只有在 4096 这样更长的序列长度上才能看到内存占用略有下降。

让我们看看如果把前馈层尺寸增大 4 倍、同时把注意力头数也减小 4 倍，让前馈层成为内存瓶颈，内存峰值使用会发生什么。

```
config_no_chunk = ReformerConfig.from_pretrained("google/reformer-enwik8", chunk_size_feed_forward=0, num_attention_{h}eads=2, feed_forward_size=16384)  # no chuck
config_chunk = ReformerConfig.from_pretrained("google/reformer-enwik8", chunk_size_feed_forward=1, num_attention_{h}eads=2, feed_forward_size=16384)  # feed forward chunk
benchmark_args = PyTorchBenchmarkArguments(sequence_lengths=[1024, 2048, 4096], batch_sizes=[8], models=["Reformer-No-Chunk", "Reformer-Chunk"], no_speed=True, no_env_print=True)
benchmark = PyTorchBenchmark(configs=[config_no_chunk, config_chunk], args=benchmark_args)
result = benchmark.run()
```

```
1 / 2
2 / 2

====================      INFERENCE - MEMORY - RESULT       ====================
--------------------------------------------------------------------------------
          Model Name             Batch Size     Seq Length    Memory in MB 
--------------------------------------------------------------------------------
      Reformer-No-Chunk              8              1024            3743     
      Reformer-No-Chunk              8              2048            5539     
      Reformer-No-Chunk              8              4096            9087     
        Reformer-Chunk               8              1024            2973     
        Reformer-Chunk               8              2048            3999     
        Reformer-Chunk               8              4096            6011     
--------------------------------------------------------------------------------
```

现在可以看到对更长的输入序列内存峰值有明显下降。结论是，分块前馈层只对拥有少量注意力头和大型前馈层的模型有意义。

## 3. 可逆残差层

可逆残差层最早在 [N. Gomez et al](https://arxiv.org/abs/1707.04585) 中被提出，用于降低训练流行的 *ResNet* 模型时的内存消耗。从数学上看，可逆残差层与"真正的"残差层略有不同，但前向传播时不需要保存激活，因而可以大幅降低训练时的内存消耗。

### Reformer 中的可逆残差层

先来研究一下为什么训练一个模型比推理一个模型需要多得多的内存。

当以推理模式运行模型时，所需内存大致等于计算模型中 **单个** 最大张量所需的内存。另一方面，当训练一个模型时，所需内存大致等于所有可微张量的 **总和**。

考虑到深度学习框架里自动微分如何工作，这并不令人意外。Roger Grosse（多伦多大学）的这份 [讲义](https://www.cs.toronto.edu/~rgrosse/courses/csc321_2018/slides/lec10.pdf) 对更好地理解自动微分很有帮助。

简而言之，为计算一个可微函数（*例如* 一个层）的梯度，自动微分需要该函数输出的梯度以及函数的输入和输出张量。梯度是动态计算并随后丢弃的，而函数的输入和输出张量（*即* 激活）在前向传播期间会被保存。

好，让我们把它应用到 transformer 模型。transformer 模型包含多个所谓 transformer 层的堆叠。每一个额外的 transformer 层都会迫使模型在前向传播时保存更多激活，从而增加训练所需内存。让我们看更细一点。一个 transformer 层本质上由两个残差层组成。第一个残差层表示 *自注意力* 机制（见第 1 节），第二个残差层表示 *线性* 或前馈层（见第 2 节）。

使用与之前相同的记号，transformer 层的输入 *即* X \mathbf{X} X 先被归一化 1 ^{1} 1，随后由自注意力层处理得到输出 Z=SelfAttn(LayerNorm(X)) \mathbf{Z} = \text{SelfAttn}(\text{LayerNorm}(\mathbf{X})) Z=SelfAttn(LayerNorm(X))。我们把这两层简称为 G G G，于是 Z=G(X) \mathbf{Z} = G(\mathbf{X}) Z=G(X)。接着，残差 Z \mathbf{Z} Z 被加到输入 Z‾=Z+X \mathbf{\overline{Z}} = \mathbf{Z} + \mathbf{X} Z=Z+X，该和被送入第二个残差层——两个线性层。Z‾ \mathbf{\overline{Z}} Z 由第二个归一化层处理，随后经两个线性层得到 Y=Linear(LayerNorm(Z+X)) \mathbf{Y} = \text{Linear}(\text{LayerNorm}(\mathbf{Z} + \mathbf{X})) Y=Linear(LayerNorm(Z+X))。我们把第二个归一化层和两个线性层简称为 F F F，于是 Y=F(Z‾) \mathbf{Y} = F(\mathbf{\overline{Z}}) Y=F(Z)。最后，残差 Y \mathbf{Y} Y 被加到 Z‾ \mathbf{\overline{Z}} Z 上，得到 transformer 层的输出 Y‾=Y+Z‾ \mathbf{\overline{Y}} = \mathbf{Y} + \mathbf{\overline{Z}} Y=Y+Z。

让我们用 x1,…,x16 \mathbf{x}_1, \ldots, \mathbf{x}_{16} x1​,…,x16​ 图示一个完整的 transformer 层。

[![alt text](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/normal_trans_resnet.png)](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/normal_trans_resnet.png)

为计算 *例如* 自注意力块 G G G 的梯度，必须事先知道三个张量：梯度 ∂Z \partial \mathbf{Z} ∂Z、输出 Z \mathbf{Z} Z 和输入 X \mathbf{X} X。虽然 ∂Z \partial \mathbf{Z} ∂Z 可以即时计算并随后丢弃，Z \mathbf{Z} Z 和 X \mathbf{X} X 的值必须在前向传播期间计算并保存，因为在反向传播时无法轻易即时重新计算它们。因此在前向传播期间，像查询-键点积矩阵 QKT \mathbf{Q}\mathbf{K}^T QKT 或线性层的中间输出 Yint \mathbf{Y}^{\text{int}} Yint 这样的大张量输出必须存进内存 2 ^{2} 2。

这时，可逆残差层就派上用场了。想法相对直接。残差块被设计成：函数输入和输出张量不用保存，而可以在反向传播期间轻松重新计算，从而前向传播期间没有张量需要存进内存。这通过使用两路输入流 X(1),X(2) \mathbf{X}^{(1)}, \mathbf{X}^{(2)} X(1),X(2) 和两路输出流 Y‾(1),Y‾(2) \mathbf{\overline{Y}}^{(1)}, \mathbf{\overline{Y}}^{(2)} Y(1),Y(2) 来实现。第一个残差 Z \mathbf{Z} Z 由第一个输出流计算 Z=G(X(1)) \mathbf{Z} = G(\mathbf{X}^{(1)}) Z=G(X(1))，并随后加到第二个输入流的输入上，于是 Z‾=Z+X(2) \mathbf{\overline{Z}} = \mathbf{Z} + \mathbf{X}^{(2)} Z=Z+X(2)。类似地，残差 Y=F(Z‾) \mathbf{Y} = F(\mathbf{\overline{Z}}) Y=F(Z) 又被加到第一个输入流，于是两路输出流定义为 Y(1)=Y+X(1) \mathbf{Y}^{(1)} = \mathbf{Y} + \mathbf{X}^{(1)} Y(1)=Y+X(1) 和 Y(2)=X(2)+Z=Z‾ \mathbf{Y}^{(2)} = \mathbf{X}^{(2)} + \mathbf{Z} = \mathbf{\overline{Z}} Y(2)=X(2)+Z=Z。

可逆 transformer 层对 x1,…,x16 \mathbf{x}_1, \ldots, \mathbf{x}_{16} x1​,…,x16​ 可以图示如下。

[![alt text](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/rev_trans_resnet.png)](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/rev_trans_resnet.png)

可以看到，输出 Y‾(1),Y‾(2) \mathbf{\overline{Y}}^{(1)}, \mathbf{\overline{Y}}^{(2)} Y(1),Y(2) 的计算方式与不可逆层的 Y‾ \mathbf{\overline{Y}} Y 非常相似，但它们在数学上是不同的。Reformer 作者在一些初步实验中观察到，可逆 transformer 模型的表现与标准 transformer 模型相当。与标准 transformer 层第一个明显的不同是存在两路输入流和两路输出流 3 ^{3} 3，起初这会略微增加前向传播所需的内存。而两路结构的关键在于前向传播期间不用保存任何激活。来解释一下。对于反向传播，可逆 transformer 层必须计算梯度 ∂G \partial G ∂G 和 ∂F \partial F ∂F。除了可以即时计算的梯度 ∂Y \partial \mathbf{Y} ∂Y 和 ∂Z \partial \mathbf{Z} ∂Z 之外，为了使自动微分工作，对 ∂F \partial F ∂F 必须知道张量值 Y \mathbf{Y} Y、Z‾ \mathbf{\overline{Z}} Z，对 ∂G \partial G ∂G 必须知道张量值 Z \mathbf{Z} Z 和 X(1) \mathbf{X}^{(1)} X(1)。

如果我们假设已知 Y‾(1),Y‾(2) \mathbf{\overline{Y}}^{(1)}, \mathbf{\overline{Y}}^{(2)} Y(1),Y(2)，从图上很容易看出可以按如下方式计算 X(1),X(2) \mathbf{X}^{(1)}, \mathbf{X}^{(2)} X(1),X(2)。X(1)=F(Y‾(1))−Y‾(1) \mathbf{X}^{(1)} = F(\mathbf{\overline{Y}}^{(1)}) - \mathbf{\overline{Y}}^{(1)} X(1)=F(Y(1))−Y(1)。太好了，既然 X(1) \mathbf{X}^{(1)} X(1) 已知，X(2) \mathbf{X}^{(2)} X(2) 可以由 X(2)=Y‾(1)−G(X(1)) \mathbf{X}^{(2)} = \mathbf{\overline{Y}}^{(1)} - G(\mathbf{X}^{(1)}) X(2)=Y(1)−G(X(1)) 计算。好，现在 Z \mathbf{Z} Z 和 Y \mathbf{Y} Y 可以通过 Y=Y‾(1)−X(1) \mathbf{Y} = \mathbf{\overline{Y}}^{(1)} - \mathbf{X}^{(1)} Y=Y(1)−X(1) 和 Z=Y‾(2)−X(2) \mathbf{Z} = \mathbf{\overline{Y}}^{(2)} - \mathbf{X}^{(2)} Z=Y(2)−X(2) 简单计算。所以结论是，如果只在前向传播期间保存 **最后一个** 可逆 transformer 层的输出 Y‾(1),Y‾(2) \mathbf{\overline{Y}}^{(1)}, \mathbf{\overline{Y}}^{(2)} Y(1),Y(2)，所有其他相关激活都可以在反向传播期间利用 G G G 和 F F F 并通过传递 X(1) \mathbf{X}^{(1)} X(1) 和 X(2) \mathbf{X}^{(2)} X(2) 推导出来。每个可逆 transformer 层在反向传播时多出的两次 G G G 和 F F F 前向传播开销，被与前向传播期间不用保存任何激活的节省所抵消。这笔交易不亏！

**注意**：最近，主流深度学习框架发布了允许只保存某些激活、并在反向传播时重新计算较大激活的代码（Tensorflow 见 [这里](https://www.tensorflow.org/api_docs/python/tf/recompute_grad)，PyTorch 见 [这里](https://pytorch.org/docs/stable/checkpoint.html)）。对标准可逆层而言，这仍意味着每个 transformer 层至少要保存一个激活，但通过指定哪些激活可以被动态重新计算，可以节省大量内存。

1 ^{1} 1 在前两节里，我们省略了分别位于自注意力层和线性层之前的 layer norm 层。读者应当知道 X \mathbf{X} X 和 Z‾ \mathbf{\overline{Z}} Z 都在被送入自注意力和线性层之前先经过 layer normalization。 2 ^{2} 2 虽然在设计中 QK \mathbf{Q}\mathbf{K} QK 的维度写作 n×n n \times n n×n，但在 *LSH 自注意力* 或 *局部自注意力* 层里维度只会分别是 n×lc×nh n \times l_{c} \times n_{h} n×lc​×nh​ 或 n×lc n \times l_{c} n×lc​，其中 lc l_{c} lc​ 为块长度、nh n_{h} nh​ 为哈希数。 3 ^{3} 3 在第一个可逆 transformer 层里 X(2) \mathbf{X}^{(2)} X(2) 被设为等于 X(1) \mathbf{X}^{(1)} X(1)。

### 基准

为衡量可逆残差层的效果，我们将在训练时按层数递增比较 BERT 与 Reformer 的内存消耗。

```
#@title Installs and Imports
# pip installs
!pip -qq install git+https://github.com/huggingface/transformers.git
!pip install -qq py3nvml

from transformers import ReformerConfig, BertConfig, PyTorchBenchmark, PyTorchBenchmarkArguments
```

让我们测量标准 `bert-base-uncased` BERT 模型在层数从 4 增至 12 时训练所需的内存。

```
config_4_layers_bert = BertConfig.from_pretrained("bert-base-uncased", num_hidden_layers=4)
config_8_layers_bert = BertConfig.from_pretrained("bert-base-uncased", num_hidden_layers=8)
config_12_layers_bert = BertConfig.from_pretrained("bert-base-uncased", num_hidden_layers=12)
benchmark_args = PyTorchBenchmarkArguments(sequence_lengths=[512], batch_sizes=[8], models=["Bert-4-Layers", "Bert-8-Layers", "Bert-12-Layers"], training=True, no_inference=True, no_speed=True, no_env_print=True)
benchmark = PyTorchBenchmark(configs=[config_4_layers_bert, config_8_layers_bert, config_12_layers_bert], args=benchmark_args)
result = benchmark.run()
```

```
HBox(children=(FloatProgress(value=0.0, description='Downloading', max=433.0, style=ProgressStyle(description_…



1 / 3
2 / 3
3 / 3

====================        TRAIN - MEMORY - RESULTS        ====================
--------------------------------------------------------------------------------
          Model Name             Batch Size     Seq Length    Memory in MB 
--------------------------------------------------------------------------------
        Bert-4-Layers                8              512             4103     
        Bert-8-Layers                8              512             5759     
        Bert-12-Layers               8              512             7415     
--------------------------------------------------------------------------------
```

可以看到 BERT 每加一层，训练所需内存线性增加 400MB 以上。

```
config_4_layers_reformer = ReformerConfig.from_pretrained("google/reformer-enwik8", num_hidden_layers=4, num_hashes=1)
config_8_layers_reformer = ReformerConfig.from_pretrained("google/reformer-enwik8", num_hidden_layers=8, num_hashes=1)
config_12_layers_reformer = ReformerConfig.from_pretrained("google/reformer-enwik8", num_hidden_layers=12, num_hashes=1)
benchmark_args = PyTorchBenchmarkArguments(sequence_lengths=[512], batch_sizes=[8], models=["Reformer-4-Layers", "Reformer-8-Layers", "Reformer-12-Layers"], training=True, no_inference=True, no_speed=True, no_env_print=True)
benchmark = PyTorchBenchmark(configs=[config_4_layers_reformer, config_8_layers_reformer, config_12_layers_reformer], args=benchmark_args)
result = benchmark.run()
```

```
1 / 3
2 / 3
3 / 3

====================        TRAIN - MEMORY - RESULTS        ====================
--------------------------------------------------------------------------------
          Model Name             Batch Size     Seq Length    Memory in MB 
--------------------------------------------------------------------------------
      Reformer-4-Layers              8              512             4607     
      Reformer-8-Layers              8              512             4987     
      Reformer-12-Layers             8              512             5367     
--------------------------------------------------------------------------------
```

而对 Reformer，加一层在实践中增加的内存要少得多。加一层平均增加所需内存不到 100MB，因此一个大得多的 12 层 `reformer-enwik8` 模型所需内存反而比 12 层 `bert-base-uncased` 模型还少。

## 4. 轴向位置编码

Reformer 让它能够处理超长的输入序列。然而，对这样的长输入序列，仅标准位置编码的权重矩阵本身就需要 1GB 以上来存权重。为了防止这样巨大的位置编码矩阵，官方 Reformer 代码引入了 *轴向位置编码*。

**重要**：*轴向位置编码在官方论文里没有解释，但通过查看代码并与作者交流可以很好理解。*

### Reformer 中的轴向位置编码

transformer 需要位置编码来考虑输入中词的顺序，因为自注意力层 *没有顺序概念*。位置编码通常由一个简单的查表矩阵 E=[e1,…,enmax] \mathbf{E} = \left[\mathbf{e}_1, \ldots, \mathbf{e}_{n_\text{max}}\right] E=[e1​,…,enmax​​] 定义。位置编码向量 ei \mathbf{e}_{i} ei​ 随后简单地加到 *第 i 个* 输入向量 xi+ei \mathbf{x}_{i} + \mathbf{e}_{i} xi​+ei​ 上，这样模型就能区分一个输入向量（*即* token）在位置 i i i 还是 j j j。对每个输入位置，模型都必须能查到对应的位置编码向量，因此 E \mathbf{E} E 的维度由模型能处理的最大输入向量长度 `config.max_position_embeddings`，*即* nmax n_\text{max} nmax​，以及输入向量的 `config.hidden_size`，*即* dh d_{h} dh​ 决定。

假设 dh=4 d_{h}=4 dh​=4 且 nmax=49 n_\text{max}=49 nmax​=49，这样一个位置编码矩阵可以图示如下：

[![alt text](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/positional_encodings_default.png)](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/positional_encodings_default.png)

这里我们只展示位置编码 e1 \mathbf{e}_{1} e1​、e2 \mathbf{e}_{2} e2​ 和 e49 \mathbf{e}_{49} e49​，每个的维度（*即* 高度）为 4。

想象一下，我们想在一个长度可达 50 万 token、输入向量 `config.hidden_size` 为 1024 的序列上训练一个 Reformer 模型（见 [这里](https://github.com/patrickvonplaten/notebooks/blob/master/PyTorch_Reformer.ipynb) 的 notebook）。对应的位置嵌入大小为 0.5M×1024∼512M 0.5M \times 1024 \sim 512M 0.5M×1024∼512M 参数，相当于 2GB。

这样的位置编码无论在内存里加载模型还是把模型存到硬盘上，都会用掉不必要的大量内存。

Reformer 作者通过把 `config.hidden_size` 维度切成两半、并巧妙地因式分解 nmax n_\text{max} nmax​ 维度，大幅缩小了位置编码的尺寸。在 Transformer 里，用户可以通过把 `config.axial_pos_shape` 设为两个合适值 nmax1 n_\text{max}^1 nmax1​ 和 nmax2 n_\text{max}^2 nmax2​ 来决定 nmax n_\text{max} nmax​ 被因式分解成什么形状，使得 nmax1×nmax2=nmax n_\text{max}^1 \times n_\text{max}^2 = n_\text{max} nmax1​×nmax2​=nmax​。通过把 `config.axial_pos_embds_dim` 设为两个合适值 dh1 d_{h}^{1} dh1​ 和 dh2 d_{h}^2 dh2​ 使得 dh1+dh2=dh d_{h}^1 + d_{h}^2 = d_{h} dh1​+dh2​=dh​，用户可以决定隐藏尺寸维度该如何切。现在让我们用更直观的方式图示和解释。

可以把因式分解 nmax n_{\text{max}} nmax​ 想象成把该维度折到第三个轴上，下面对因式分解 `config.axial_pos_shape = [7, 7]` 展示了这一点：

[![alt text](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/3d_positional_encoding.png)](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/3d_positional_encoding.png)

三个立着的长方体各对应一个编码向量 e1,e2,e49 \mathbf{e}_{1}, \mathbf{e}_{2}, \mathbf{e}_{49} e1​,e2​,e49​，但我们可以看到 49 个编码向量被分成了 7 行、每行 7 个向量。现在的想法是只用 7 个编码向量中的一行，并把这些向量扩展到另外 6 行，本质上复用它们的值。因为不鼓励让不同编码向量取值相同，维度（*即* 高度）为 `config.hidden_size=4` 的每个向量被切成大小为 1 1 1 的下编码向量 edown \mathbf{e}_\text{down} edown​ 和大小为 3 3 3 的上编码向量 eup \mathbf{e}_\text{up} eup​，这样下半部分可以沿行维度扩展，上半部分可以沿列维度扩展。让我们图示得更清楚一点。

[![alt text](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/3d_positional_encoding_cut.png)](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/3d_positional_encoding_cut.png)

可以看到我们把嵌入向量切成了 edown \mathbf{e}_\text{down} edown​（*蓝色*）和 eup \mathbf{e}_\text{up} eup​（*黄色*）。现在对"子"向量 Edown=[edown,1,…,edown,49] \mathbf{E}_\text{down} = \left[\mathbf{e}_{\text{down},1}, \ldots, \mathbf{e}_{\text{down},49}\right] Edown​=[edown,1​,…,edown,49​]，只保留 7 7 7 中的第一行（*即* 图中的宽度），并沿列维度（*即* 图的深度）扩展；反之对"子"向量 Eup=[eup,1,…,eup,49] \mathbf{E}_\text{up} = \left[\mathbf{e}_{\text{up},1}, \ldots, \mathbf{e}_{\text{up},49}\right] Eup​=[eup,1​,…,eup,49​]，只保留 7 7 7 中的第一列，并沿行维度扩展。得到的嵌入向量 e′i \mathbf{e'}_{i} e′i​ 于是对应

e′i=[[edown, i%nmax1]T,[eup, ⌊inmax2⌋]T]T\mathbf{e'}_{i} = \left[ \left[\mathbf{e}_{\text{down, } i \% n_\text{max}^1}\right]^T, \left[\mathbf{e}_{\text{up, } \left \lfloor{\frac{i}{{n}^2_{\text{max}}}}\right \rfloor} \right]^T \right]^T e′i​=​[edown, i%nmax1​​]T,​eup, ⌊nmax2​i​⌋​​T​T

在我们示例里 nmax1=7 n_\text{max}^1 = 7 nmax1​=7 且 nmax2=7 n_\text{max}^2 = 7 nmax2​=7。这些新编码 E′=[e′1,…,e′nmax] \mathbf{E'} = \left[\mathbf{e'}_{1}, \ldots, \mathbf{e'}_{n_\text{max}}\right] E′=[e′1​,…,e′nmax​​] 称为 **轴向位置编码**。

接下来更详细地为我们的示例图示这些轴向位置编码。

[![alt text](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/axial_pos_encoding.png)](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/reformer_benchmark/axial_pos_encoding.png)

现在应该更容易理解最终的位置编码向量 E′ \mathbf{E'} E′ 如何仅由维度为 dh1×nmax1 d_{h}^1 \times n_{\text{max}^1} dh1​×nmax1​ 的 Edown \mathbf{E}_{\text{down}} Edown​ 和维度为 dh2×nmax2 d_{h}^2 \times n_{\text{max}}^2 dh2​×nmax2​ 的 Eup \mathbf{E}_{\text{up}} Eup​ 计算得到。

这里最关键的一点是，轴向位置编码在设计上确保 [e′1,…,e′nmax] \left[\mathbf{e'}_1, \ldots, \mathbf{e'}_{n_{\text{max}}}\right] [e′1​,…,e′nmax​​] 中没有向量彼此相同，并把编码矩阵的总尺寸从 nmax×dh n_{\text{max}} \times d_{h} nmax​×dh​ 缩小到 nmax1×dh1+nmax2×dh2 n_{\text{max}}^1 \times d_{h}^1 + n_\text{max}^2 \times d_{h}^2 nmax1​×dh1​+nmax2​×dh2​。通过让每个轴向位置编码向量在设计上都互不相同，当模型学习轴向位置编码时，它获得了更多灵活性来学习有效的位置表示。

为了展示尺寸上的大幅缩减，假设我们对一个可处理输入长度达 50 万 token 的 Reformer 模型设置 `config.axial_pos_shape = [1024, 512]` 和 `config.axial_pos_embds_dim = [512, 512]`。结果轴向位置编码矩阵将只有 1024×512+512×512∼800K 1024 \times 512 + 512 \times 512 \sim 800K 1024×512+512×512∼800K 参数，约等于 3MB。相比标准位置编码矩阵在此情形下需要 2GB，这是大幅缩减。

关于更浓缩、更偏数学的解释，请参考 🤗Transformers 文档 [这里](https://huggingface.co/transformers/model_doc/reformer.html#axial-positional-encodings)。

### 基准

最后，让我们也比较常规位置嵌入与 *轴向位置嵌入* 在推理时的内存峰值。

```
#@title Installs and Imports
# pip installs
!pip -qq install git+https://github.com/huggingface/transformers.git
!pip install -qq py3nvml

from transformers import ReformerConfig, PyTorchBenchmark, PyTorchBenchmarkArguments, ReformerModel
```

位置嵌入只依赖两个配置参数：允许输入序列的最大长度 `config.max_position_embeddings` 和 `config.hidden_size`。我们用一个把允许输入序列最大长度推到五十万 token 的模型 `google/reformer-crime-and-punishment` 来查看使用轴向位置嵌入的效果。

首先，比较轴向位置编码与标准位置编码的形状以及模型里的参数数量。

```
config_no_pos_axial_embeds = ReformerConfig.from_pretrained("google/reformer-crime-and-punishment", axial_pos_embds=False)  # disable axial positional embeddings
config_pos_axial_embeds = ReformerConfig.from_pretrained("google/reformer-crime-and-punishment", axial_pos_embds=True, axial_pos_embds_dim=(64, 192), axial_pos_shape=(512, 1024))  # enable axial positional embeddings

print("Default Positional Encodings")
print(20 * '-')
model = ReformerModel(config_no_pos_axial_embeds)
print(f"Positional embeddings shape: {model.embeddings.position_embeddings}")
print(f"Num parameters of model: {model.num_parameters()}")
print(20 * '-' + '\n\n')

print("Axial Positional Encodings")
print(20 * '-')
model = ReformerModel(config_pos_axial_embeds)
print(f"Positional embeddings shape: {model.embeddings.position_embeddings}")
print(f"Num parameters of model: {model.num_parameters()}")
print(20 * '-' + '\n\n')
```

```
HBox(children=(FloatProgress(value=0.0, description='Downloading', max=1151.0, style=ProgressStyle(description…



Default Positional Encodings
--------------------
Positional embeddings shape: PositionEmbeddings(
  (embedding): Embedding(524288, 256)
)
Num parameters of model: 136572416
--------------------


Axial Positional Encodings
--------------------
Positional embeddings shape: AxialPositionEmbeddings(
  (weights): ParameterList(
      (0): Parameter containing: [torch.FloatTensor of size 512x1x64]
      (1): Parameter containing: [torch.FloatTensor of size 1x1024x192]
  )
)
Num parameters of model: 2584064
--------------------
```

读过了理论，轴向位置编码权重的形状应当不会让读者惊讶。

关于结果，可以看到对于能处理如此长输入序列的模型，使用默认位置编码并不实用。在 `google/reformer-crime-and-punishment` 的情形下，仅标准位置编码就包含超过 1 亿参数。轴向位置编码把这个数字降到了 20 万多一点。

最后，也比较一下推理时所需的内存。

```
benchmark_args = PyTorchBenchmarkArguments(sequence_lengths=[512], batch_sizes=[8], models=["Reformer-No-Axial-Pos-Embeddings", "Reformer-Axial-Pos-Embeddings"], no_speed=True, no_env_print=True)
benchmark = PyTorchBenchmark(configs=[config_no_pos_axial_embeds, config_pos_axial_embeds], args=benchmark_args)
result = benchmark.run()
```

```
1 / 2
2 / 2

====================      INFERENCE - MEMORY - RESULT       ====================
--------------------------------------------------------------------------------
          Model Name             Batch Size     Seq Length    Memory in MB 
--------------------------------------------------------------------------------
Reformer-No-Axial-Pos-Embeddin       8              512             959      
Reformer-Axial-Pos-Embeddings        8              512             447      
--------------------------------------------------------------------------------
```

可以看到，在 `google/reformer-crime-and-punishment` 的情形下，使用轴向位置嵌入把内存需求降到了大约一半。

## 本文提到的模型 1

来自我们博客的更多文章

nlp

community

research

## 介绍 Ettin Reranker 家族

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6317233cc92fd6fee317e030/cJHSvvimr1kqgQfHOjO5n.png)

58

2026 年 5 月 19 日

nlp

evaluation

retrieval

## 介绍 RTEB：检索评估的新标准

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/61f33092a92c9a858b654991/jFRUSeZ6DnI27dlCAQRHq.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/5ff5943752c26e9bc240bada/Exyzf3C_gJ2KdsL4K5_cq.png)
- ![](https://huggingface.co/avatars/7a4067accdd1005f78c3c4adad3ee0a5.svg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/64cc0e80a257a3212c0c4b24/wqs6WZN8-3OQthcnQXgN7.png)
- +2

149

2025 年 10 月 1 日

### 社区

deleted

2025 年 10 月 31 日

•

此评论已被隐藏

allendorf

1 月 22 日

•

此评论已被隐藏（标记为垃圾）

通过拖拽到文本输入框、粘贴，或

点击这里

上传图像、音频和视频。

.

点击或粘贴到这里上传图像

· [注册](https://huggingface.co/join?next=%2Fblog%2Freformer) 或 [登录](https://huggingface.co/login?next=%2Fblog%2Freformer) 以评论



- [![](https://huggingface.co/avatars/ce9b99882a65fd2cb983ba71a5ac2473.svg)](https://huggingface.co/a-r-r-o-w)
- [![](https://huggingface.co/avatars/2211bd0a7d08bf1e078b0acee40894b5.svg)](https://huggingface.co/Vivek)
- [![](https://huggingface.co/avatars/6be635f7f258d1050cd4c6e2c2d92a62.svg)](https://huggingface.co/kamalelsaaid)
