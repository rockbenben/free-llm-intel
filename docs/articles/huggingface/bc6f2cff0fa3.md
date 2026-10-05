---
vendor: huggingface
title: BLOOM 训练背后的技术
original_title: The Technology Behind BLOOM Training
url: https://huggingface.co/blog/bloom-megatron-deepspeed
date: 2026-07-29
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: b3a2f9e28116
---

# BLOOM 训练背后的技术

近年来，训练越来越大的语言模型已成常态。人们时常讨论这些模型不开放研究的问题，但「怎么训练这种模型」的隐性知识却很少受到关注。本文想改变这一点：以 1760 亿参数语言模型 [BLOOM](https://huggingface.co/bigscience/bloom) 为例，讲讲训练这类模型在硬件和软件背后的技术与工程。

但在正文之前，我们要先感谢那些公司和关键人物与团队——是一个小而专注的团队训练出 1760 亿参数模型这一壮举得以可能的功臣。

随后我们会讨论硬件环境和主要技术组件。

[![BLOOM](https://huggingface.co/blog/assets/86_bloom_megatron_deepspeed/bloom-banner.png)](https://huggingface.co/blog/assets/86_bloom_megatron_deepspeed/bloom-banner.png)

项目速览：

|  |  |
| --- | --- |
| 硬件 | 384 块 80GB A100 GPU |
| 软件 | Megatron-DeepSpeed |
| 架构 | GPT3（含额外改进） |
| 数据集 | 59 种语言、3500 亿 token |
| 训练时长 | 3.5 个月 |

## 人物

这个项目由 Thomas Wolf（Hugging Face 联合创始人兼首席科学官）构想。他敢于与巨头公司竞争，不仅训练出最大的多语言模型之一，还让最终成果向所有人开放——把多数人眼中的梦想变成了现实。

本文聚焦在模型训练的工程侧。BLOOM 背后技术最重要的部分，是贡献专业知识、在编码和训练上帮助我们的那些人和公司。

要感谢的主要有 6 个群体：

- HuggingFace 的 BigScience 团队：投入超过六名全职员工从头到尾搞定并执行了整个训练，并提供和承担了 Jean Zay 算力之外的全部基础设施费用。
- Microsoft DeepSpeed 团队：开发了 DeepSpeed，后又将其与 Megatron-LM 整合。他们的开发者为项目需求投入数周，并在训练前后提供了大量实用的经验性建议。
- NVIDIA Megatron-LM 团队：开发了 Megatron-LM，非常耐心地回答我们的无数问题，给出一流的经验建议。
- 管理 Jean Zay 超级计算机的 IDRIS / GENCI 团队：为项目捐赠了海量算力，并提供了出色的系统管理员支持。
- PyTorch 团队：创造了这个强大的框架，其余软件都构建其上。在训练准备期他们对我们大力相助，修了多个 bug、改进我们在训练中依赖的 PyTorch 组件的可用性。
- BigScience 工程工作组（Engineering workgroup）的志愿者们

要给工程侧所有卓越贡献者点名实在太难，所以我只列出 Hugging Face 之外、过去 14 个月里成为本项目工程基石的几位关键人物：

Olatunji Ruwase、Deepak Narayanan、Jeff Rasley、Jared Casper、Samyam Rajbhandari 和 Rémi Lacroix

同样感谢允许员工参与本项目的每一家公司。

## 总览

BLOOM 的架构与 [GPT3](https://en.wikipedia.org/wiki/GPT-3) 非常相似，只加了一些改进，后文会讲。

模型在 [Jean Zay](http://www.idris.fr/eng/jean-zay/jean-zay-presentation-eng.html) 上训练——这是法国政府资助的超算，由 GENCI 管理、安装在 [IDRIS](http://www.idris.fr/)（法国国家科学研究中心 CNRS 的国家计算中心）。算力由 GENCI 慷慨捐赠（资助号 2021-A0101012475）。

训练使用的硬件如下：

- GPU：384 块 NVIDIA A100 80GB（48 节点）+ 32 块备用 GPU
- 每节点 8 块 GPU，NVLink 4 GPU 间互联，4 条 OmniPath 链路
- CPU：AMD EPYC 7543 32 核处理器
- CPU 内存：每节点 512GB
- GPU 内存：每节点 640GB
- 节点间互联：Omni-Path 架构（OPA），无阻塞胖树
- NCCL 通信网络：完全专用的子网
- 磁盘 IO 网络：与其他节点和用户共享的 GPFS

Checkpoint：

- [主要 checkpoints](https://huggingface.co/bigscience/bloom)
- 每个含 fp32 优化器状态和 bf16+fp32 权重的 checkpoint 为 2.3TB——仅 bf16 权重是 329GB。

数据集：

- 46 种语言、去重并大规模清洗后的 1.5TB 文本，转成 3500 亿唯一 token
- 模型词表大小：250,680 tokens
- 完整细节见 [The BigScience Corpus: A 1.6TB Composite Multilingual Dataset](https://openreview.net/forum?id=UoEw6KigkUn)

1760 亿参数的 BLOOM 训练发生在 2022 年 3 月至 7 月，耗时约 3.5 个月（约 100 万 GPU 计算小时）。

## Megatron-DeepSpeed

176B BLOOM 模型使用 [Megatron-DeepSpeed](https://github.com/bigscience-workshop/Megatron-DeepSpeed) 训练，它是 2 项主要技术的结合：

- [DeepSpeed](https://github.com/microsoft/DeepSpeed)：一个深度学习优化库，让分布式训练变得简单、高效、有效。
- [Megatron-LM](https://github.com/NVIDIA/Megatron-LM)：NVIDIA 应用深度学习研究团队开发的大型强大 transformer 模型框架。

DeepSpeed 团队把 DeepSpeed 库的 ZeRO 分片与流水线并行，同 Megatron-LM 的张量并行结合起来，实现了基于 3D 并行的方案。各组件细节见下表。

请注意，BigScience 的 [Megatron-DeepSpeed](https://github.com/bigscience-workshop/Megatron-DeepSpeed) 是原 [Megatron-DeepSpeed](https://github.com/microsoft/Megatron-DeepSpeed) 仓库的 fork，我们往里加了多个改动。

下表列出训练 BLOOM 时各组件由哪个框架提供：

| 组件 | DeepSpeed | Megatron-LM |
| --- | --- | --- |
| [ZeRO 数据并行](https://huggingface.co/blog/bloom-megatron-deepspeed#zero-data-parallelism) | V |  |
| [张量并行](https://huggingface.co/blog/bloom-megatron-deepspeed#tensor-parallelism) |  | V |
| [流水线并行](https://huggingface.co/blog/bloom-megatron-deepspeed#pipeline-parallelism) | V |  |
| [BF16Optimizer](https://huggingface.co/blog/bloom-megatron-deepspeed#bf16optimizer) | V |  |
| [融合 CUDA Kernels](https://huggingface.co/blog/bloom-megatron-deepspeed#fused-cuda-kernels) |  | V |
| [DataLoader](https://huggingface.co/blog/bloom-megatron-deepspeed#datasets) |  | V |

请注意，Megatron-LM 和 DeepSpeed 都有流水线并行和 BF16 优化器的实现，但我们用的是 DeepSpeed 的版本，因为它们与 ZeRO 是整合的。

Megatron-DeepSpeed 实现了 3D 并行，让超大模型能高效训练。下面简述 3D 的各个维度。

- **数据并行（DP）**——把同一套配置复制多份，每份喂一部分数据。各份并行处理，所有配置在每个训练步结束时相互同步。
- **张量并行（TP）**——把每个张量切成多块，整个张量不再驻留单块 GPU，每个分片放在各自的 GPU 上。处理期间每个分片在不同 GPU 上分开并行计算，步末再同步结果。这可以叫水平并行，因为切分发生在水平方向。
- **流水线并行（PP）**——模型沿纵向（层级）切到多块 GPU 上，单块 GPU 只放一个或几层。每块 GPU 并行处理流水线的不同阶段，各自处理批次的一小块。
- **Zero Redundancy Optimizer（ZeRO）**——也做张量分片，与 TP 有些像，但在前向或反向计算需要时会即时重建整个张量，因此模型无需修改。它还支持各种 offload 技术以弥补 GPU 显存不足。

## 数据并行

只有几块 GPU 的用户大概熟悉 `DistributedDataParallel`（DDP）（[PyTorch 文档](https://pytorch.org/docs/master/generated/torch.nn.parallel.DistributedDataParallel.html#torch.nn.parallel.DistributedDataParallel)）。这种方式把模型完整复制到每块 GPU，每次迭代后所有模型互相同步状态。这种方法靠堆资源提速，但只有当模型塞得进单块 GPU 时才可行。

### ZeRO 数据并行

ZeRO 驱动的数据并行（ZeRO-DP）如这张来自[博客](https://www.microsoft.com/en-us/research/blog/zero-deepspeed-new-system-optimizations-enable-training-models-with-over-100-billion-parameters/)的图所示 [![DeepSpeed-Image-1](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/parallelism-zero.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/parallelism-zero.png)

它可能不好理解，但其实概念很简单：就是普通的 DDP，只是不复制完整的模型参数、梯度和优化器状态——每块 GPU 只存其中一片。运行时，当某一层需要完整参数时，所有 GPU 同步、把彼此缺少的部分互传——就这样。

这个组件由 DeepSpeed 实现。

## 张量并行

在张量并行（TP）中，每块 GPU 只处理张量的一片，只有在需要完整张量的操作中才聚合出完整张量。

本节使用 Megatron-LM 论文 [Efficient Large-Scale Language Model Training on GPU Clusters](https://arxiv.org/abs/2104.04473) 的概念和图。

transformer 的主要构件是后接非线性激活 `GeLU` 的全连接 `nn.Linear`。

按 Megatron 论文的记法，可以把其中的点积部分写成 `Y = GeLU(XA)`，`X` 和 `Y` 是输入输出向量，`A` 是权重矩阵。

以矩阵形式看计算，就很容易理解矩阵乘法怎么切到多块 GPU 上：[![Parallel GEMM](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/parallelism-tp-parallel_gemm.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/parallelism-tp-parallel_gemm.png)

如果把权重矩阵 `A` 按列切到 `N` 块 GPU 上并并行做矩阵乘法 `XA_1` 到 `XA_n`，就得到 `N` 个输出向量 `Y_1, Y_2, ..., Y_n`，可以各自独立送进 `GeLU`：[![independent GeLU](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/parallelism-tp-independent-gelu.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/parallelism-tp-independent-gelu.png)。注意，Y 矩阵按列切分后，第二个 GEMM 可以按行切分，直接吃 GeLU 的输出，无需额外通信。

利用这个原则，可以并行化任意深度的 MLP，只需在每段行-列序列后同步各 GPU。Megatron-LM 论文作者给出了 helpful 的图示：[![parallel shard processing](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/parallelism-tp-parallel_shard_processing.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/parallelism-tp-parallel_shard_processing.png)

其中 `f` 在前向传播中是恒等算子、反向传播中是 all reduce；`g` 在前向传播中是 all reduce、反向传播中是恒等。

并行化多头注意力层更简单，因为它们多个 head 天然独立、本来就自带并行！[![parallel self-attention](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/parallelism-tp-parallel_self_attention.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/parallelism-tp-parallel_self_attention.png)

特别注意事项：由于前向和反向每层各有两次 all reduce，TP 需要设备间非常快的互联。因此除非网络很快，不建议跨超过一个节点做 TP。我们的场景里节点间链路远慢于 PCIe。实际来说，如果一台机器有 4 块 GPU，TP 度最高就是 4。若需要 TP 度 8，就得用至少 8 GPU 的节点。

这个组件由 Megatron-LM 实现。Megatron-LM 近期把张量并行扩展到了序列并行——沿序列维度切分那些无法按上面方式切分的操作（如 LayerNorm）。技术细节见论文 [Reducing Activation Recomputation in Large Transformer Models](https://arxiv.org/abs/2205.05198)。序列并行是在 BLOOM 训练完成后才发展的，因此 BLOOM 训练没有用到。

## 流水线并行

朴素流水线并行（naive PP）是把模型的一组层散布到多块 GPU，数据在 GPU 之间挪动，就好像它们是一整块大 GPU。机制相对简单——把目标层 `.to()` 到目标设备，数据进出这些层时把数据切到该层所在设备，其余不动。

这叫纵向模型并行，因为如果你记得多数模型的画法，我们是把层纵向切开。例如，下图是一个 8 层模型：

```
===================  ===================
|  0 | 1 | 2 | 3  |  |  4 | 5 | 6 | 7  |
===================  ===================
        GPU0                 GPU1
```

我们就是纵向切成两半，层 0-3 放 GPU0，4-7 放 GPU1。

数据从层 0 到 1、1 到 2、2 到 3 时，跟普通模型在单块 GPU 上的前向传播一样。但当数据需要从层 3 传到层 4 时，就必须从 GPU0 到 GPU1，引入通信开销。如果参与的 GPU 在同一计算节点（同一台物理机），这种拷贝很快；如果 GPU 在不同计算节点（多台机器），通信开销可能大得多。

之后层 4 到 5 到 6 到 7 又和普通模型一样；第 7 层完成后，通常要把数据送回层 0（标签在那里；或者反过来把标签送到最后一层）。这样就能计算损失，优化器干活。

问题：

- 最主要的缺陷——也是它被叫「朴素」PP 的原因——是任一时刻除一块 GPU 外其余全在闲着。用 4 块 GPU，几乎等于把单块 GPU 的内存扩大四倍、同时无视其他硬件。再加上设备间数据拷贝的开销。4 张 6GB 卡能容纳的模型规模和 1 张 24GB 卡用朴素 PP 相同——而且后者训练更快，因为没有数据拷贝开销。但如果你有 40GB 卡、需要塞进一个 45GB 的模型，4 张 40GB 卡可以做到（但很勉强，因为还有梯度和优化器状态）。
- 共享 embedding 可能需要在 GPU 之间来回拷贝。

流水线并行（PP）与上面朴素 PP 几乎相同，但通过把进来的批次切成 micro-batch、人为搭起流水线，解决了 GPU 闲置问题，让不同 GPU 能并发参与计算。

下面这张来自 [GPipe 论文](https://ai.googleblog.com/2019/03/introducing-gpipe-open-source-library.html)的图，上方是朴素 PP，下方是 PP：

[![mp-pp](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/parallelism-gpipe-bubble.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/parallelism-gpipe-bubble.png)

从下图很容易看到 PP 的死区更少——GPU 闲置的部分被称为「bubble（气泡）」。

图的两部分都是 4 度并行，即 4 块 GPU 参与流水线：有前向路径的 4 个流水级 F0、F1、F2、F3，然后逆序的反向路径 B3、B2、B1、B0。

PP 带来一个新的可调超参数 `chunks`。它定义同一个流水级连续发送多少块数据。例如下图中 `chunks=4`。GPU0 对 chunk 0、1、2、3 执行相同的前向路径（F0,0、F0,1、F0,2、F0,3），然后等其他 GPU 干活；只有当它们的工作快要完成时，GPU0 才开始对 chunk 3、2、1、0 做反向路径（B0,3、B0,2、B0,1、B0,0）。

注意，概念上这就是梯度累积步（GAS）。PyTorch 叫 `chunks`，DeepSpeed 对同一超参数叫 GAS。

由于 chunk 的存在，PP 引入了 micro-batch（MBS）的概念。DP 把全局批次大小拆成 mini-batch：如果 DP 度为 4，全局批次 1024 就被分成 4 个各 256 的 mini-batch（1024/4）。如果 `chunks`（或 GAS）为 32，最终 micro-batch 大小是 8（256/32）。每个流水线阶段一次只处理一个 micro-batch。

于是 DP + PP 配置的全局批次大小就是 `mbs*chunks*dp_degree`（`8*32*4=1024`）。

回到那张图。

`chunks=1` 时就是朴素 PP，非常低效。`chunks` 值太大则 micro-batch 太小，也可能低效。所以得实验找到让 GPU 高效利用率最高的取值。

图中可以看到有一段无法并行的「死」时间气泡——最后一个 `forward` 阶段要等 `backward` 完成流水线。寻找最佳 `chunks` 值的目的，就是让所有参与 GPU 保持高并发利用率，即把气泡最小化。

这个调度机制称为 `all forward all backward`。其他方案还有 [one forward one backward](https://www.microsoft.com/en-us/research/publication/pipedream-generalized-pipeline-parallelism-for-dnn-training/) 和 [interleaved one forward one backward](https://arxiv.org/abs/2104.04473)。

Megatron-LM 和 DeepSpeed 都各自实现了 PP 协议，但 Megatron-DeepSpeed 用 DeepSpeed 的实现，因为它与 DeepSpeed 的其他部分已集成。

这里还有一个重要问题是词嵌入矩阵的体积。通常词嵌入矩阵占的内存比 transformer 块小，但对我们 250k 的巨型词表，embedding 层在 bf16 下需要 7.2GB，而 transformer 块才 4.9GB。因此我们必须让 Megatron-DeepSpeed 把 embedding 层当作一个 transformer 块来处理，于是有了 72 层的流水线，其中 2 层专门给 embedding（第一和最后一层）。这样 GPU 显存消耗才均衡。否则首尾阶段会吃掉大部分显存，而 95% 的 GPU 用得很省，训练远谈不上高效。

## DP+PP

下面这张来自 DeepSpeed [流水线教程](https://www.deepspeed.ai/tutorials/pipeline/)的图，演示 DP 与 PP 如何组合。

[![dp-pp-2d](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/parallelism-zero-dp-pp.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/parallelism-zero-dp-pp.png)

这里重要的是看清 DP rank 0「看不见」GPU2、DP rank 1「看不见」GPU3。对 DP 来说只有 GPU 0 和 1，它把数据喂给这两块，仿佛系统只有 2 块 GPU。GPU0 通过 PP「悄悄」把自己的一部分负载 offload 给 GPU2，GPU1 拉上 GPU3 同样如此。

由于每个并行维度至少需要 2 块 GPU，这样至少要 4 块 GPU。

## DP+PP+TP

要更高效地训练，PP 会与 TP 和 DP 组合，这就是 3D 并行，如下图。

[![dp-pp-tp-3d](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/parallelism-deepspeed-3d.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/parallelism-deepspeed-3d.png)

这张图来自博客 [3D parallelism: Scaling to trillion-parameter models](https://www.microsoft.com/en-us/research/blog/deepspeed-extreme-scale-model-training-for-everyone/)，也值得一读。

由于每个维度至少 2 块 GPU，完整 3D 并行至少需要 8 块 GPU。

## ZeRO DP+PP+TP

DeepSpeed 的主要特色之一是 ZeRO——DP 的超可扩展增强版。前面在 [ZeRO 数据并行](https://huggingface.co/blog/bloom-megatron-deepspeed#zero-data-parallelism)已经讨论过。它通常是独立特性，不需要 PP 或 TP，但可以与 PP 和 TP 组合。

ZeRO-DP 与 PP（以及可选的 TP）组合时，通常只启用 ZeRO stage 1，即只分片优化器状态。Stage 2 还会额外分片梯度，stage 3 则连模型权重也分片。

理论上可以把 ZeRO stage 2 与流水线并行同用，但会有糟糕的性能影响：每个 micro-batch 需要额外的 reduce-scatter 集合操作来聚合梯度再分片，通信开销可能很可观。流水线并行的本性是使用小 micro-batch，重心放在平衡算术强度（micro-batch 大小）与最小化流水线气泡（micro-batch 数量）上，因此那些通信开销会很伤。

另外，PP 之下层数本来就更少，内存节省有限；PP 已经把梯度大小缩小到 `1/PP`，在此基础上再做梯度分片，收益远不如纯 DP。

ZeRO stage 3 在这个规模上也可用于训练，但它比 DeepSpeed 的 3D 并行实现需要更多通信。约一年前我们在自己环境里仔细评估后，认定 Megatron-DeepSpeed 3D 并行性能最佳。此后 ZeRO stage 3 性能大幅提升，今天重新评估的话，我们可能会选 stage 3。

## BF16Optimizer

用 FP16 训练超大 LLM 是大忌。

我们亲身验证过：花了好几个月[训练一个 104B 模型](https://github.com/bigscience-workshop/bigscience/tree/master/train/tr8-104B-wide)，从 [tensorboard](https://huggingface.co/bigscience/tr8-104B-logs/tensorboard) 就能看出那完全是场失败。在与不断发散的 lm-loss 斗争的过程中我们学到了很多东西：

[![104B-fail](https://huggingface.co/blog/assets/86_bloom_megatron_deepspeed/104b-lm-loss.png)](https://huggingface.co/blog/assets/86_bloom_megatron_deepspeed/104b-lm-loss.png)

Megatron-LM 和 DeepSpeed 团队在训练完 [530B 模型](https://arxiv.org/abs/2201.11990)之后也给了我们同样的建议。最近发布的 [OPT-175B](https://arxiv.org/abs/2205.01068) 同样报告 FP16 训练极其艰难。

所以早在 1 月，当我们知道将在支持 BF16 的 A100 上训练时，Olatunji Ruwase 开发了 `BF16Optimizer`，BLOOM 训练用的就是它。

如果不熟悉这个数据格式，可以看看 [位布局](https://en.wikipedia.org/wiki/Bfloat16_floating-point_format#bfloat16_floating-point_format)。BF16 格式的关键在于它的指数位与 FP32 相同，因此不会像 FP16 那样深受溢出困扰。FP16 最大数值范围只有 64k，只能乘小数字：`250*250=62500` 可以，但 `255*255=65025` 就溢出了——这正是训练出问题的主因。这意味着权重必须一直保持很小。loss scaling 技术可以缓解这个问题，但模型变得非常大时，FP16 的有限范围依然是个麻烦。

BF16 没有这个问题，`10_000*10_000=100_000_000` 轻而易举。

当然，由于 BF16 和 FP16 同为 2 字节，天下没有免费的午餐——用 BF16 代价是很差的精度。不过回想一下，用随机梯度下降及其变体的训练就是一种踉跄行走，一开始方向不完美没关系，后面几步会自己纠正。

无论用 BF16 还是 FP16，都存在一份始终为 FP32 的权重拷贝——优化器更新的就是它。所以 16-bit 格式只用于计算；优化器以全精度更新 FP32 权重，再把它转成 16-bit 格式供下一轮迭代使用。

PyTorch 所有组件都确保以 FP32 做累加，所以那里没有损失。

一个关键问题是梯度累积——它是流水线并行的主要特性之一，每个 microbatch 处理产生的梯度会被累积起来。梯度累积必须用 FP32 实现以保持训练精度，`BF16Optimizer` 就是这么做的。

除了其他改进，我们相信 BF16 混合精度训练把潜在的噩梦变成了相对平稳的过程——从下面的 lm-loss 图可以看出：

[![176B-fail](https://huggingface.co/blog/assets/86_bloom_megatron_deepspeed/176b-lm-loss.png)](https://huggingface.co/blog/assets/86_bloom_megatron_deepspeed/176b-lm-loss.png)

## 融合 CUDA Kernels

GPU 干两件事：从内存读写数据，以及对数据做计算。GPU 忙于拷贝时，计算单元就闲着。想高效利用 GPU，就要把闲置压到最低。

kernel 是一组指令的集合，实现某个具体的 PyTorch 操作。比如调用 `torch.add` 时，请求经过 [PyTorch dispatcher](http://blog.ezyang.com/2020/09/lets-talk-about-the-pytorch-dispatcher/)，它查看输入张量和 various 其他信息，决定该跑哪段代码然后跑掉。CUDA kernel 是使用 CUDA API 库的特定实现，只能在 NVIDIA GPU 上运行。

当我们让 GPU 计算 `c = torch.add(a, b); e = torch.max([c,d])`，朴素做法（也是 PyTorch 默认做法）是启动两个独立 kernel：一个算 `a` 加 `b`，一个求 `c` 与 `d` 的最大值。此时 GPU 先从内存取 `a` 和 `b`，算加法，把结果写回内存；然后再取 `c` 和 `d`，做 `max`，再把结果写回内存。

如果把这两个操作融合——合成单个「fused kernel」，只启动那一个 kernel——中间结果 `c` 就不必写回内存，而是留在 GPU 寄存器里，最后只需取 `d` 完成最后一步计算。这省下大量开销、避免 GPU 空转，让整体操作高效得多。

融合 kernel 就是这么回事。它们主要把多次离散计算和内存读写合并成内存移动极少的融合计算；一些融合 kernel 还会改写数学形式，让某些计算组跑得更快。

要快速高效地训练 BLOOM，必须使用 Megatron-LM 提供的数个定制融合 CUDA kernel。特别地，其中有做 LayerNorm 的优化 kernel，也有把缩放、掩码和 softmax 各种组合融合的 kernel。bias 项的加法也用 PyTorch 的 JIT 功能与 GeLU 融合。这些操作全是内存受限（memory bound）的，所以必须在从内存取出一个值之后把尽可能多的计算塞进去。例如，在本来就内存受限的 GeLU 操作里顺手加上 bias 项不花任何额外时间。这些 kernel 都在 [Megatron-LM 仓库](https://github.com/NVIDIA/Megatron-LM)里。

## 数据集

Megatron-LM 另一个重要特性是高效的数据加载器。首次启动训练时，每个数据集会被切成所请求序列长度（BLOOM 为 2048）的样本，并建立索引为每个样本编号。根据训练参数算出数据集需要的 epoch 数，生成对应 epoch 数的排序并洗牌。例如，某数据集有 10 个样本、需要过 2 遍，系统先按顺序铺开样本索引 `[0, ..., 9, 0, ..., 9]`，然后洗牌得到该数据集最终的全局顺序。注意这意味着训练不是简单跑完整个数据集再重复——有可能某个样本先见到两次而另一个样本还没见到过，但训练结束时每个样本都被看过两次。这有助于在整个训练过程中保持平滑的训练曲线。这些索引（含每个样本在基础数据集中的偏移）会存到文件里，免得每次启动训练都重算一遍。多个这样的数据集可以按不同权重混合成训练流程看到的最终数据。

## Embedding LayerNorm

在苦斗 104B 不发散的过程中，我们发现：在第一层词嵌入之后加一个 LayerNorm，训练稳定性大大提升。

这个洞见来自对 [bitsandbytes](https://github.com/facebookresearch/bitsandbytes) 的实验——其中有个 `StableEmbedding`，就是一个带 LayerNorm、使用均匀 xavier 初始化的普通 Embedding。

## 位置编码

我们还把通常的位置嵌入换成了 AliBi——依据论文 [Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation](https://arxiv.org/abs/2108.12409)，它可以外推到比训练序列更长的输入。所以我们虽然按 2048 长度训练，模型在推理时也能处理长得多的序列。

## 训练中的困难

架构、硬件和软件都就位后，我们于 2022 年 3 月初开始训练。但此后并不是一路顺风。本节讲讲我们遇到的主要坎。

训练开始前有大量问题要搞定。特别地，我们发现几个只在 48 节点规模训练时才暴露、小规模下不会出现的小问题。例如需要 `CUDA_LAUNCH_BLOCKING=1` 才能防止框架挂起；需要把优化器分组拆成更小组，否则框架同样会挂起。细节见[训练前传编年史](https://github.com/bigscience-workshop/bigscience/blob/master/train/tr11-176B-ml/chronicles-prequel.md)。

训练期间遇到的主要问题是硬件故障。这是一个约 400 块 GPU 的新集群，平均每周有 1-2 次 GPU 故障。我们每 3 小时（100 iterations）保存一次 checkpoint，所以硬件崩溃平均损失 1.5 小时训练。Jean Zay 的系统管理员会更换故障 GPU 并把节点重新拉起，期间我们用备份节点顶上。

我们还遇到过其他多种导致 5-10 小时宕机的问题，一些与 PyTorch 的死锁 bug 有关，另一些则是磁盘空间耗尽。想看具体细节请阅读[训练编年史](https://github.com/bigscience-workshop/bigscience/blob/master/train/tr11-176B-ml/chronicles.md)。

在决定这个模型的训练可行性时，我们就把这些宕机时间规划在内——我们选择的模型规模正是与可行性和想要让模型消化的数据量相匹配的。算上所有宕机，我们最终在预估时间内完成了训练。如前所述，共约 100 万 GPU 小时。

另一个问题是 SLURM 不是为人多团队设计的。一个 SLURM 作业属于单个用户，如果他不在，团队其他人对运行中的作业什么也做不了。我们开发了一个 kill-switch 变通方案，允许组内其他用户终止当前进程、而无要求作业发起人必须在场。90% 的问题下这招都好使。SLURM 的设计者们如果看到这篇文章——请加上 Unix 组的概念，让 SLURM 作业可以由一个组共同拥有。

训练是 7×24 小时进行的，需要有人随叫随到——好在我们的人分布在欧洲和加拿大西海岸，整体衔接得很好，不需要有人配呼机。当然，周末也得有人盯着训练。我们自动化了大部分环节（包括从硬件崩溃中恢复），但有时仍需人工介入。

## 结论

训练最艰难、压力最大的部分是开训前的那两个月。我们承受着尽快开训的巨大压力，因为资源分配是有时限的，而且直到最后一刻才有 A100 可用。那真是段艰难时光：`BF16Optimizer` 是压哨写出来的，我们还得调试并修各种 bug；而且如上一节所说，我们发现了若干只在 48 节点规模训练时才暴露、小规模下不会出现的新问题。

但把这些搞定之后，训练本身出奇地平稳，没有大问题。多数时间只有一个人盯训练，只有少数几次需要多人一起排查问题。我们得到 Jean Zay 管理团队的有力支持——训练期间冒出来的需求基本都很快被解决。

总的来说，这是一段超级紧张但收获满满的经历。

训练大语言模型仍然是个充满挑战的任务，但我们希望通过公开构建并分享这些技术，他人能在我们的经验之上继续前进。

## 资源

### 重要链接

- [主要训练文档](https://github.com/bigscience-workshop/bigscience/blob/master/train/tr11-176B-ml/README.md)
- [tensorboard](https://huggingface.co/bigscience/tr11-176B-ml-logs/tensorboard)
- [训练 slurm 脚本](https://github.com/bigscience-workshop/bigscience/blob/master/train/tr11-176B-ml/tr11-176B-ml.slurm)
- [训练编年史](https://github.com/bigscience-workshop/bigscience/blob/master/train/tr11-176B-ml/chronicles.md)

### 论文与文章

一篇文章不可能把所有细节讲完，如果这些技术勾起了你的好奇心、想深入了解，以下是推荐阅读的论文：

Megatron-LM：

- [Efficient Large-Scale Language Model Training on GPU Clusters](https://arxiv.org/abs/2104.04473)。
- [Reducing Activation Recomputation in Large Transformer Models](https://arxiv.org/abs/2205.05198)

DeepSpeed：

- [ZeRO: Memory Optimizations Toward Training Trillion Parameter Models](https://arxiv.org/abs/1910.02054)
- [ZeRO-Offload: Democratizing Billion-Scale Model Training](https://arxiv.org/abs/2101.06840)
- [ZeRO-Infinity: Breaking the GPU Memory Wall for Extreme Scale Deep Learning](https://arxiv.org/abs/2104.07857)
- [DeepSpeed: Extreme-scale model training for everyone](https://www.microsoft.com/en-us/research/blog/deepspeed-extreme-scale-model-training-for-everyone/)

Megatron-LM 与 DeepSpeed 联合：

- [Using DeepSpeed and Megatron to Train Megatron-Turing NLG 530B, A Large-Scale Generative Language Model](https://arxiv.org/abs/2201.11990)。

ALiBi：

- [Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation](https://arxiv.org/abs/2108.12409)
- [What Language Model to Train if You Have One Million GPU Hours?](https://openreview.net/forum?id=rI7BL3fHIZq)——里面有引导我们选择 ALiBi 的实验。

BitsNBytes：

- [8-bit Optimizers via Block-wise Quantization](https://arxiv.org/abs/2110.02861)（在 Embedding LayerNorm 的语境下提到；这篇论文和这项技术本身也非常出色——我们没用它的 8-bit 优化器的唯一原因，是 DeepSpeed-ZeRO 已经在优化器内存上做了节省）。

## 博客致谢

衷心感谢以下好心人提出了好问题并帮助改善文章可读性（按字母顺序）：Britney Muller、Douwe Kiela、Jared Casper、Jeff Rasley、Julien Launay、Leandro von Werra、Omar Sanseviero、Stefan Schweter 和 Thomas Wang。

主图由 Chunte Lee 制作。
