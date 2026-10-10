---
vendor: poolside
title: Tools of the Trade: C2C Activation Offloading on Grace Blackwell
original_title: 
url: https://poolside.ai/blog/tools-of-the-trade-c2c-activation-offloading-on-grace-blackwell
date: 2026-04-28
lang: zh
captured: 2026-10-08
extractor: readability-v1
translator: agent
status: translated
body_sha: a19e92f57f05
---

# Tools of the Trade: C2C Activation Offloading on Grace Blackwell

**TL;DR: **我们证明，NVIDIA 的 Grace Blackwell NVLink C2C 链路可以在训练过程中把 MLP 激活值卸载到主机内存，从而用一个更快的替代方案换掉 activation checkpointing。在 Qwen3-30B-3A 上，这带来 6–13% 的端到端吞吐提升，代价只是约 0.5% 的额外峰值内存。对于 MLP 块特别庞大的模型，选择性卸载的变体可以挽回大部分收益。我们分享自己的消融实验、profile，以及这项技术背后的一般性原理。

## 引言

距离我们连载完第一篇关于 Model Factory 的博客系列已经过去六个多月了。社区的反响极其热烈，而有一件事也因此变得很清楚：人们对于「前沿实验室究竟是怎么把模型造出来的」有着永不满足的渴求。

对我们幸运的是，自我们写下那些帖子以来，Model Factory 以前所未有的速度在成长。正如我们当初的预判，Model Factory 之所以持续变大，恰恰是因为它的每一个子部件都在向一个更大的系统供料。举个例子，训练代码库稍微快一点，就能支撑更大规模的强化学习 pipeline，而这反过来又带来更好的模型，用来搭建代码执行环境。

然而，Model Factory 的成长过程中最有回报感的事情之一，是一路上我们攒下的各式各样的 tip、trick 和技术。这些技术通常只针对整体 Model Factory 里的一小块——比如我们的训练代码库——但它们带来的影响往往与其体量不成比例地大。事实上，这正是我们如此喜欢它们的原因。

正因为我们太喜欢这些技术，我们决定把它们讲给更广阔的世界听。每隔一阵子，我们会发布一篇新文章，讲一件我们发现根本不可或缺的吃饭家伙。我们希望通过记录这些技术，能把前沿模型构建背后那层工程的幕布再拉开一些。就先从我们最喜欢的一项开始吧：NVLink C2C Activation Offloading。

## 为什么要卸载？

每一次大规模训练最终都会撞上同一个问题：HBM 用完了。模型的前向传播一层层推进，沿途会留下一串中间激活值，它们通常会被保存下来，供反向传播时计算梯度使用。这些激活值一层接一层地堆积，直到在反向传播中被用到、并最终释放。而且，与权重和优化器状态不同（它们可以很好地跨设备分片），在单设备的口径下，你对激活值的大小其实没什么可做的。需要强调，尽管 Tensor Parallelism、Context Parallelism 这些众所周知的技术也能用在激活值上，但它们通常相当不灵活，并且天然会引入通信开销，因此绝非什么银弹。这意味着激活值所需的空间最终会占据设备内存的大头，成为一个真正的痛点。

为了对量级有个感觉，我们来看看 Qwen3-30B-3A 这类模型里的单个基于 SwiGLU 的 MoE 层。温习一下，SwiGLU 计算的是 y=Wdown (SiLU(Wgatex)∘Wupx)y = W_{down}\,(\text{SiLU}(W_{gate} x) \circ W_{up} x)y=Wdown​(SiLU(Wgate​x)∘Wup​x)，仅 MLP 块本身就会产生反向传播所需的三个大型激活张量：gate 投影的输出（WgatexW_{gate} xWgate​x，即 SiLU 的输入）、up 投影的输出（WupxW_{up} xWup​x），以及 SwiGLU 中间量（SiLU(Wgatex)∘Wupx\text{SiLU}(W_{gate} x) \circ W_{up} xSiLU(Wgate​x)∘Wup​x，即 WdownW_{down}Wdown​ 的输入）——它们每一个都随 batch size、序列长度以及中间维度缩放（对 MoE 模型来说，这个中间维度是激活专家数 kkk 乘以每个专家的中间维度，因为每个 token 的激活值会在全部 kkk 个被路由到的专家上实际生成出来）。作为参照，这已经是极其庞大的内存量：在一个合理的 microbatch 大小下，我们测得每层约 3.7GB 的 MLP 激活值（这个数字在「卸载 MLP 块」一节中推导）。48 层加起来就是接近 180 GB 的激活值内存，还要叠加在本来就挤在同一块 HBM 上的模型权重、优化器状态和梯度 buffer 之上。在前沿规模下，如何应对这一约束往往决定了你的并行策略、microbatch 大小，以及最终实现的训练吞吐。

当然了，这么大的问题不可能长期没人解，AI 领域有一个标准答案，形式就是 activation checkpointing。activation checkpointing 不在前向传播中保存这些庞大的中间量，而是在反向传播时即时把它们重新计算出来，从而让我们用算力换取内存节省。到今天，activation checkpointing 已经是一项标准技术，我们预计几乎每一次大规模训练都会以某种形式使用它。但 activation checkpointing 并不免费；每重算一次激活值都要花掉 FLOPs，而 FLOPs 无论在时间还是能耗上都很昂贵。在大 MoE 模型的语境下情况更糟；我们本质上等于把每一层的 MLP 投影 GEMM（所有激活专家上的 gate、up、down 投影）重跑了两遍。

到了这一步，我们也许会去看不允许我们在训练中卸载激活值的其它技术。幸运的是，这条路早已被充分研究；毕竟 FSDP 和 ZeRO 都存在。但这些方法只针对权重和优化器状态，并不针对中间激活值。于是一个很自然的问题出现了：我们能卸载激活值吗？

如果我们能在前向传播时把它们寄存在一个次级内存池里，再在反向传播时把它们取回来——并且不干扰计算——我们就能拿到 activation checkpointing 的内存节省，而不用付出重算这道税。在以往的硬件上这事从来行不通；但 NVIDIA 的 Grace superchip 改变了这道等式。

那么卸载与 activation checkpointing（AC）相比究竟如何？两者节省的稳态内存是相同的——区别在于你付出什么。AC 用算力来付（重跑 MLP 前向）；卸载用瞬时内存和 NVLink C2C 带宽来付。下文我们要说明，在 Grace Blackwell 硬件上这笔交易是压倒性地划算的。

## 为什么卸载以前行不通

在继续之前，值得先说清楚为什么激活值卸载过去一直不可行。毕竟，把权重和优化器状态通过 PCIe 卸载到主机内存是一项很成熟的技术。激活值有什么特别的？

主要问题在于，激活值是在单个训练 step 之内产生并被消耗的。这意味着我们必须以极快的速度卸载中间激活值：某一层的 D2H 传输必须在下下一层需要那块 buffer 空间之前完成。实际做法中，卸载会与下一层的前向计算重叠，所以链路必须跟得上逐层的计算速度，而 PCIe Gen5 根本做不到这一点。举个例子，考虑一个典型的 H200 配置。这类设置中通往主机内存的通路是 PCIe Gen5 16x，提供大约 64GB/s 的单向带宽。而每层有好几 GB 的激活数据，传输时间就和前向计算时间相当了。根本没有余量。

结果就是滚雪球效应：每一层都在上一层的传输尚未结束之前把激活值加进传输队列。积压随着每一层不断增长，训练吞吐随之崩塌。我们在 2024 年用自己的 [  Monster 代码库](https://poolside.ai/blog/titan-the-model-factory-s-furnace)亲眼见识过这一幕，当时我们用 NVIDIA 的 Unified Memory，通过页迁移把激活值自动卸载到主机内存，并在反向传播时预先取回。原理上它是可行的，但 profile 道出了真相：里面塞满了 device-to-host 的 memcpy、页迁移，以及各种各样的其它问题。我们的 step 时间大幅膨胀，很快就意识到这根本不可行。

事实证明，这一个洞察就足以判断卸载激活值什么时候可行：我们只需要 host-to-device 带宽相对于平台所提供计算量的一个良好比值。具体地说，让 VℓV_\ellVℓ​ 表示第 ℓ\ellℓ 层的激活量，BWBWBW 表示主机链路带宽，tfwd(ℓ)t_{fwd}^{(\ell)}tfwd(ℓ)​ 表示下一层的前向计算时间。当且仅当下面这条成立时，卸载方案不会滚雪球：

V

ℓ

B

W

<

t

f

w

d

(

ℓ

+

1

)

\frac{V_\ell}{BW} < t_{fwd}^{(\ell+1)}

B

W

V

ℓ



<

t

f

w

d

(

ℓ

+

1

)


在 PCIe Gen5 上 BW≈64BW \approx 64BW≈64 GB/s，这条不等式对我们关心的任何模型都不成立。值得指出的是，我们确实可以做某些事情来缓解这种滚雪球；比如我们可以阻塞直到每次传输完成，但这最终牺牲的正是卸载的主要收益。

## Grace Blackwell 带来了什么

到目前为止，我们的分析都局限在 H200 上。但 AI 行业并没有原地踏步，NVIDIA 的 GB200 Super Chip 就是当今最顶级的加速器之一。给不熟悉的人解释一下，Grace Blackwell 是一种 system-on-a-chip 架构，把两颗 Blackwell GPU 与一颗 Grace CPU 配对起来。这些芯片之间通过 chip-to-chip（C2C）的 NVLink 连接。我们指出，更早的 Grace Hopper（GH）系列芯片共享同样的 NVLink C2C 互连，所以这里的原则对两个系列都适用。不过就本文而言，我们只关注 Grace Blackwell。事实证明，有三个特性让这类架构对激活值卸载变得有意思。

第一，GB 系列提供了极其庞大的 C2C 带宽。C2C 链路的标称值是 ~900 GB/s 双向，但这里有个细节：NVIDIA 给出的这个数是按每颗 Blackwell GPU package 计的，而每个 package 内含两颗共享一个 HBM stack 的 GPU die。所以理论上每颗 die 的有效单向带宽是 ∼225\sim 225∼225 GB/s。实践中我们稳定量到 ∼185\sim 185∼185 GB/s——按当前的优化，我们测得的是理论峰值的 82%，其余被开销吃掉。这仍然约是 PCIe Gen5 的 3 倍，而且在一系列张量大小上都是稳定值。（跑一次快速的 `nvbandwidth` 或 STREAM 风格的 memcpy 测试，是集群团队在部署卸载前确认 C2C 吞吐健康的好办法。）顺带一提，尽管 NVLink-C2C 名义上是对称的，但我们在实践中观察到 H2D 传输始终比 D2H 更快——这大概源于 Grace 与 Blackwell 内存控制器在 write-combining 与 prefetch 行为上的差异。做可行性分析时我们采用较低的 D2H 数字。

第二，C2C 传输不消耗任何 SM 资源。Blackwell die 上有一个专用的 copy engine 负责这条链路，因此数据传输可以与计算 kernel 并发运行而不抢占 SM cycle。这意味着我们可以把卸载与 GEMM 重叠，而不会明显拉低计算吞吐，不过正如后文将要看到的，在 memory-bound 操作期间存在一个关于 HBM 争用的微妙之处。

第三，Grace 每颗 CPU 配备 480 GB 的 LPDDR5x 系统内存，而每块板上有 1 颗 Grace CPU 和 2 颗 Blackwell GPU，每颗 GPU 有 186 GB 的 HBM3e 内存。即便是每层卸载三个 MLP 激活值的 48 层模型（总共 ∼150–200\sim 150–200∼150–200 GB），也有充足的余量。当然，CPU 内存还有其它竞争者（数据流水线与 prefetch 等等），但实践中这算不上值得担心的约束。

把这三点放在一起看，就会发现我们实际上凑齐了某种以前根本不可能成立的东西的雏形：以足够的带宽把激活值卸载与逐层前向计算重叠，同时不撞上滚雪球效应。

## 卸载 MLP 块

如前所述，这种卸载的天然目标是 MLP 块。原则上，把一层里所有激活值都卸载能带来最大的内存节省。我们试过，但对我们测试的那些模型来说这超出了 NVLink C2C 的带宽预算，而且它还需要多得不切实际的 host 内存。于是我们把注意力只放在 MLP 上：当我们说「full offload」时，指的是卸载该层中每一个 MLP 激活张量。在某种程度上，full MLP offloading 正是做这类优化的自然起点。毕竟，MLP 激活值是每层最大的内存消耗者——它们随 dffnd_{ffn}dffn​ 缩放，即 FFN 中间维度（也就是每个 MLP 块的 hidden 宽度）——而且重算它们最贵。对 dense 模型，dffnd_{ffn}dffn​ 就是 MLP 的 hidden 宽度；对 MoE 模型，它是 k⋅dmoek \cdot d_{moe}k⋅dmoe​，其中 kkk 是激活专家的数量。这里要指出，存在一些模型架构，full MLP offloading 会直接超出我们的带宽预算，但正如后文分析 Grok2 时会看到的，选择性卸载的变体同样好用。

我们先从卸载完整的 MLP 层开始。对一个基于 SwiGLU 的 MoE 层，反向传播需要的正是上面引入的那三个张量：gate 投影输出、up 投影输出，以及 SwiGLU 中间量。它们加在一起，每层的 MLP 激活内存为：

M

MLP

(

ℓ

)

=

3


B


S


d

f

f

n


β

bytes

M_{\text{MLP}}^{(\ell)} = 3 \cdot B \cdot S \cdot d_{ffn} \cdot \beta \text{ bytes}

M

MLP

(

ℓ

)


=

3


B


S


d

f

f

n



β

bytes

其中 β\betaβ 是每个元素的字节数（BF16 为 2）。对 Qwen3-30B-3A，dffn=3×2048=6144d_{ffn} = 3 \times 2048 = 6144dffn​=3×2048=6144。这里要指出，一个融合的 SwiGLU kernel 实际上可以把它缩减到只有两个张量，因为我们只需保存 WgatexW_{gate} xWgate​x 和 WupxW_{up} xWup​x，剩下的即时重算就够了。这能把卸载量降下大约三分之一。融合与卸载的这种组合实际上让我们两边的好处都拿到，因为我们传输的数据更少了，同时也获得了各项内存节省。不过就本文而言，我们聚焦于简单情形，使用未融合的、三张量的做法。

相比之下，checkpointing 所要付出的重算代价是：

F

recomp

=

2


k


3


d


d

m

o

e

FLOPs per token

F_{\text{recomp}} = 2 \cdot k \cdot 3 \cdot d \cdot d_{moe} \text{ FLOPs per token}

F

recomp


=

2


k


3


d


d

m

oe


FLOPs per token

其中 kkk 是每个 token 的激活专家数，d 是模型的 hidden 维度，dmoed_{moe}dmoe​ 是每个专家的中间维度（3 个 SwiGLU 投影 × 每参数 2 FLOPs）。这就是卸载所消掉的计算量。对我们更好的是，那些冗余的 FLOPs 要消耗真实的能量，所以卸载也是更环保的选择。

反向传播比前向重 ∼2×\sim 2\times∼2×（既要对激活值求梯度，也要对权重求梯度），这对我们有利：它给 H2D 重新加载留出了额外的完成时间。作为一项额外的优化，我们还可以跳过对最后一层的卸载；毕竟反向传播就是从最后一层开始的，卸载与重新加载激活值之间的重叠窗口为零。

### 实验

为了证明这些想法在实践中站得住，我们在 4 颗 GB200 GPU 上对 Qwen3-30B-3A 的 8 层（共 48 层）跑了一些实验，microbatch 大小为 24，序列长度 4096。事实证明 Qwen3-30B-3A 是这类工作的一个恰当选择：MoE 架构相对简单直接，使它适合用来快速实验。我们的配置在单个 node 内使用 4 颗 GB200 Grace Blackwell superchip——也正是生产部署中组成 GB200 NVL72 机架的那些 superchip。我们决定只用 48 层中的 8 层，因为卸载的模式是逐层的：如果它在 8 层上能不积累传输欠账地工作，那么在 48 层上也一样能。这个 microbatch 大小让 GEMM 保持在 compute-bound 区间，而那正是在大规模下真正要紧的区间——也是 C2C copy engine 可以不必争抢 HBM 带宽就能工作的区间。

我们的实验实现挂在 PyTorch 的 saved-tensor 机制上：前向传播期间在一条专用的 CUDA stream 上发起 D2H 拷贝，反向期间在同一条 stream 上做 H2D 重新加载。我们确保 host 侧 buffer 是 pin 住的（`cudaHostAlloc`），因为尽管带 ATS 的 Grace Blackwell C2C 链路能让 GPU 直接访问 pageable 的 CPU 内存，`cudaMemcpyAsync` 仍然需要 pinned memory 才能真正做到非阻塞。这是 CUDA runtime 的约束而不是硬件的约束，但它对我们的重叠实验很要紧。

由于 copy stream 独立于 compute stream，传输可以与 GEMM 无争用地重叠——前提是那些 GEMM 是 compute-bound 的。当某个 GEMM 是 memory-bound 时，它的 HBM 流量会与 C2C copy engine 争用同一条 HBM 总线，蚕食掉重叠效果。这正是我们瞄准重计算阶段的原因：让 copy engine 在后台把激活值排空的同时，用大型 matmul 把 SM 保持忙碌。该方法与 FSDP 兼容（标准的 `all_gather` / `reduce_scatter` collective 照常与卸载 stream 并行运行），也与 `torch.compile` 兼容（编译出的 `FxGraph` 区域在 trace 里可见，与异步拷贝干净地交错）。

*流水线时序图。上方的 SM 计算轨道运行逐层前向与逐层反向 kernel；下方的 C2C copy engine 把 D2H 卸载与下一层的前向重叠、把 H2D 重新加载与当前层的反向重叠。峰值 HBM 中最多保留两层的激活值。*

在每层三个 SwiGLU 激活值全部卸载的情况下，D2H 传输会在后一层的前向计算时间内完成。每层的卸载量为：

V

offload

=

3


B


S


d

f

f

n


β

V_{\text{offload}} = 3 \cdot B \cdot S \cdot d_{ffn} \cdot \beta

V

offload


=

3


B


S


d

f

f

n



β

我们测得 D2H 传输在 ∼20\sim 20∼20 ms 内完成，这意味着每层 Voffload≈0.020×185=3.7V_{\text{offload}} \approx 0.020 \times 185 = 3.7Voffload​≈0.020×185=3.7 GB。该层的前向时间是 ~22.5 ms，所以 tD2H<tfwdt_{D2H} < t_{fwd}tD2H​<tfwd​ 成立——余量很紧，但可行。

返程受到的约束更小：H2D 重新加载传输的同样是 3.7 GB，以 ∼185\sim 185∼185 GB/s（∼20\sim 20∼20 ms）跑完，而反向传播提供了更宽的重叠窗口。在我们的 trace 里，H2D 早在被重新加载的激活值投入使用之前就已结束。真正的硬约束是前向期间的 D2H。假如某次 H2D 传输跑得太久，反向传播会卡在一个 `cudaStreamSynchronize` 上直到重新加载完成——正确性保住了，但那一层的重叠收益就没了。

下面的 profile 证实了这一点。D2H 传输（红色方框）在下一层前向结束之前很早便已完成。峰值 HBM 最多保留两层的激活值：正在计算的那一层，以及正在排空的那一层。

*Qwen3-30B-3A 的 MLP 卸载 profile。D2H 传输（红色方框）在每层前向计算窗口之内从容完成。峰值 HBM 最多保留两层的激活值。*

对于 dffnd_{ffn}dffn​ 非常大的架构，full MLP offload 可能超过该层的前向时间；我们在下文的 Grok2 分析中详细说明退路（卸载更少的张量）。

## 正面对决：卸载 vs activation checkpointing

引言里提到过，卸载和 activation checkpointing（AC）节省的稳态内存是相同的——区别在于你付出什么。现在我们来把这个差别量化。

### 内存

先从内存说起。对我们的 8 层配置，我们测得如下结果：

- 峰值已分配内存：124.01 GB（卸载）vs 120.38 GB（activation checkpointing）——相差 +3.63 GB，约 +3%。
- 稳态最小值：两种方法都是 17.03 GB——完全一致，与预期相同。
- 「三角形」高度（峰值减最小值）：106.97 GB vs 103.35 GB——同样是 +3.63 GB（+3.5%）。

结果看来，这 +3% 的差额来自 in-flight 的 D2H buffer；有一层的激活值在传输过程中仍然留在 HBM 里。按 20 ms × 185 GB/s = 3.7 GB 计算，这与观察到的差额完全吻合。

关键在于，这份开销是恒定的（也就是说无论我们用多少层做卸载都成立）。这意味着相对开销与层数成反比：

Δ

M

M

total

=

M

MLP

(

ℓ

)

L


M

MLP

(

ℓ

)

+

M

other

≤

1

L

\frac{\Delta M}{M_{\text{total}}} = \frac{M_{\text{MLP}}^{(\ell)}}{L \cdot M_{\text{MLP}}^{(\ell)} + M_{\text{other}}} \leq \frac{1}{L}

M

total


Δ

M


=

L


M

MLP

(

ℓ

)


+

M

other


M

MLP

(

ℓ

)



≤

L

1


其中 MotherM_{\text{other}}Mother​ 涵盖权重、优化器状态、梯度以及非 MLP 激活值。在我们的 8 层实验里 1/L=12.5%1/L = 12.5\%1/L=12.5%，但实际开销只有 3%，因为 MotherM_{\text{other}}Mother​ 很大。对完整的 48 层模型，1/L=2.1%1/L = 2.1\%1/L=2.1%，实际开销降到约 0.5%。若是 96 层模型还会更低。换句话说，模型越深，这笔交易越划算。

*单个训练 step 内的内存时间线。两种方法共享同一个稳态下界；卸载额外带来一个恒定的 +3.7 GB in-flight buffer（一层的激活值正在通过 C2C 排空）。*

有一点要注意：*实测*峰值内存与*已分配*峰值内存之间可能存在相当大的差异。这一差异主要来自 allocator 的碎片化，尽管 PyTorch 的 CachingAllocator 通常能把这个差距压得很好。在我们的实验里，实际内存是 160.86 GB，而 AC 是 131.45 GB——22% 的差距。这可以通过为 in-flight 数据预分配固定 buffer 来解决，而在带 FSDP 的分布式设置里，每个 rank 的状态更小，allocator 也就更轻松。在大规模下这似乎不构成问题。这一差异主要来自 allocator 的碎片化，尽管 PyTorch 的 CachingAllocator 通常能把这个差距压得很好。在我们的实验里，实际内存是 160.86 GB，而 AC 是 131.45 GB——22% 的差距。这可以通过为 in-flight 数据预分配固定 buffer 来解决，而在带 FSDP 的分布式设置里，每个 rank 的状态更小，allocator 也就更轻松。在大规模下这似乎不构成问题。

### 速度

前向传播是完全一样的，因为 D2H 传输不消耗 SM。收益体现在反向传播：AC 必须先重算 MLP 激活值才能计算梯度，而卸载只是通过 copy engine 用 H2D 把它们从 Grace 内存重新加载回来。没有任何 SM cycle 被偷走。

我们在 48 层中取 8 层做测试，好让实验能装进单个 4 GPU 的 node；卸载的模式是逐层的，所以只要它在 8 层上能不积累传输欠账地工作，在 48 层上也就一样。对所有层取平均，与 AC 相比卸载把反向时间降低了约 7-8%，而前向时间完全相同。有代表性的中间层显示出更大的收益，约 13%，但这种加速并不均匀：靠近模型两端的层由于 warm-up 和 cool-down 效应改善较小，于是跨层平均被拉到约 7-8%。

对我们的 8 层模型，端到端的 step 时间改善约 4.3%。约 7-8% 的逐层收益与 4.3% 的端到端数字之间的落差，是因为 8 层模型的固定开销（embedding、unembedding、loss 计算）占比很大，稀释了逐层收益。对更深的模型，这部分固定开销变得可以忽略，端到端加速会向逐层收益收敛，从而带来预期的 6–13% 改善。缩放性质我们在下文推导。

*有代表性的中间层的正面对决计时对比。左：逐层前向（完全相同）与反向的相对改善。右：8 层上端到端 step 时间的相对改善。*

下面的 profile 详细展示了逐层计时。可以看到每一层的 D2H 传输都在计算窗口之内从容完成，SM 时间线上没有空闲间隙。

*逐层计时细节，显示 D2H 传输与计算 kernel 重叠。SM 时间线上没有出现空闲间隙。*

底线是：对完整深度（48 层）的 Qwen3-30B-3A，卸载用约 0.5% 的峰值内存换来预估的 6–13% 吞吐提升。在一次 90 天的预训练里，这个区间的中点（约 7%）折合约 6 天墙钟时间的节省。

### 在真实的 Grace Blackwell 系统上部署

我们已经在 GB200 Grace Blackwell 硬件上验证了这项技术。对于打算在生产环境部署 C2C offloading 的团队，关键的基础设施前提是：(1) 必须在系统 firmware 中启用 C2C（在 GB200 NVL 配置上这是默认行为），(2) host buffer 必须通过 `cudaHostAlloc` 钉住，以确保 `cudaMemcpyAsync` 传输真正非阻塞，(3) 在开始一次训练之前，应当用一次基本的 C2C 带宽健康检查（例如运行 `nvbandwidth` 或 STREAM 风格的 memcpy 测试）确认每颗 superchip 都达到预期的 ~185 GB/s D2H 吞吐。

## 一般性原理

这套方案的生死取决于一个约束：D2H 传输必须在一层的前向时间内结束，否则滚雪球就会卷土重来。而预算不只是 MLP 前向——是整个层，包括 attention 和通信。那些非 MLP 的计算是白得的余量，而你能拿到多少余量取决于架构。三个 SwiGLU 激活值全部的 D2H 传输时间是：

t

D

2

H

=

3


B


S


d

f

f

n


β

B

W

C

2

C

t_{D2H} = \frac{3 \cdot B \cdot S \cdot d_{ffn} \cdot \beta}{BW_{C2C}}

t

D

2

H


=

B

W

C

2

C


3


B


S


d

f

f

n



β


该层的前向时间是 MLP GEMM（对 kkk 个激活专家的 SwiGLU 而言是 6k⋅d⋅dmoe6k \cdot d \cdot d_{moe}6k⋅d⋅dmoe​ FLOPs/token）、attention（Fattn(S)F_{\text{attn}}(S)Fattn​(S) FLOPs/token，取决于序列长度 SSS）以及通信开销的总和。由于 B⋅SB \cdot SB⋅S 同时出现在传输量和计算时间里，它会从不等式中约掉，条件因而主要取决于模型架构和硬件。把 tD2H<tfwdt_{D2H} < t_{fwd}tD2H​<tfwd​ 重新整理，就得到 dffnd_{ffn}dffn​ 的一个阈值：

d

f

f

n

<

(

6


k


d


d

m

o

e

+

F

attn

)


B

W

C

2

C

3


β


P

p

e

a

k

d_{ffn} < \frac{(6 \cdot k \cdot d \cdot d_{moe} + F_{\text{attn}}) \cdot BW_{C2C}}{3 \cdot \beta \cdot P_{peak}}

d

f

f

n


<

3


β


P

p

e

ak


(

6


k


d


d

m

oe


+

F

attn


)


B

W

C

2

C



其中 PpeakP_{peak}Ppeak​ 是该设备的峰值计算吞吐。注意这个公式假设了 compute-bound 区间；一般而言，GEMM 的前向时间是 tgemm=max⁡(tcompute,thbm)t_{gemm} = \max(t_{compute}, t_{hbm})tgemm​=max(tcompute​,thbm​)，其中 thbmt_{hbm}thbm​ 是 GEMM 的内存流量时间，并在 GEMM roofline 的 memory-bandwidth-bound 区间里占主导。我们还注意到，attention 的贡献 Fattn(S)F_{\text{attn}}(S)Fattn​(S) FLOPs 随序列长度二次增长，而 MLP 的 FLOPs 与卸载量都只是线性增长；这潜在地给了我们更多空间去吸收 D2H 传输。

然而，并非所有模型都适合做 MLP 卸载。有一个 MLP 不成比例地庞大的模型，就是 Grok2。

*C2C 卸载的可行域。对角线上方的模型（D2H 时间 < 层前向时间）可以卸载而不引发滚雪球。Qwen3-30B-3A 恰好位于边界之上——可行，但缺少 attention 余量时就很紧；Grok2 需要选择性卸载才能降到边界之下。*

### 完全卸载失效之时：Grok2

Grok-2 是一个打破 full MLP offloading 的典型模型。它的 MLP 明显更大，每个激活张量大约 1.5 GB；每层三个，总量达到约 4.5 GB。在 180 GB/s 的传输速度下，Device-to-Host（D2H）传输要 ~25 ms，超过了该层的前向时间。这个「滚雪球效应」在 profile 里一眼就能看见：

*Grok2 的 full MLP 卸载，展示滚雪球效应。每一层的 D2H 传输都溢出到下一层的前向窗口中，形成不断增长的积压。*

为了解决这个问题，我们可以采用另一种选择性卸载策略。我们不再卸载 MLP 内部的每一个中间张量，而是在整层范围内只卸载一部分激活值。通过把这些更小的传输与正在进行的计算重叠，我们阻止了积压的形成。

一个有效的解法是从 attention 块中卸载特定的激活值。可供卸载的候选有好几个，所以最优选择取决于具体的硬件配置。在我们的情况下，我们选择卸载：

- transformer 层的输入。
- attention 输出投影层的激活值。
- 只从 MLP 中卸载一个激活值（取 WupW_{up}Wup​，以便与计算更多地重叠）。

通过把这些 D2H 传输入分散到整个前向传播中，我们消除了主要的 MLP 瓶颈。

*选择性卸载确保 D2H 传输留在该层的前向时间之内。*

如图所示，卸载阶段现在所花的时间比前向传播略少一点，于是整个过程变得可行。在这个配置下，我们每层成功卸载了约 2 GB。此外，这种做法在 attention 与 MLP 两个阶段之间留出了一个窗口，可以用来卸载补充数据。

归根结底，这说明卸载是一种取舍。根据具体约束的不同，可以设计出不同的策略，在内存节省与计算吞吐之间取得平衡。而且，卸载和 activation checkpointing 可以结合起来使用，允许从重新加载的激活值出发做重算，从而避免一整轮完整重算。

### 这笔取舍如何随规模变化

现在可以来看我们的完整结果了。

|  | Qwen3-30B-3A | Grok2（完全） | Grok2（部分） |
| --- | --- | --- | --- |
| 每层卸载量 | 3.7 GB | 4.84 GB | 2.15 GB |
| D2H 时间（占层前向的 %） | ~89% | ~119% | ~62% |
| 能放进该层的前向时间里吗？ | 是 | 否 | 是 |
| 内存开销（48 层） | ~1/L | — | ~1/L |

**注：**我们没有为 Grok2 profile 一条 AC 基线，所以 Grok2 的两列是拿完全卸载与选择性卸载相比，而不是与 AC 相比。那 12% 的改善是完全 vs 部分；部分 vs AC 的对比仍属未来工作，因为它需要更细粒度的 AC 实现。

从这张表里可以做出几个观察。首先，我们看到 in-flight buffer 确实增加了一层的激活值，由此带来的相对开销至多是 1/L1/L1/L（48 层约 2%，96 层约 1%）。

同样地，我们看到这项技术在 step 时间上有很强的改善。具体地说，让 δ\deltaδ 表示被消掉的逐层重算时间。重算节省给出了相对加速的下界：

speedup

≥

1

1

−

δ

t

f

+

t

b

A

C

\text{speedup} \geq \frac{1}{1 - \frac{\delta}{t_f + t_b^{AC}}}

speedup

≥

1

−

t

f


+

t

b

A

C


δ


1


对所有层取平均，反向的收益是约 7–8%。对足够深的模型，随着固定开销（embedding、loss）被摊薄，端到端的改善会向这个逐层平均值收敛。这就是为什么我们的 8 层实验尽管逐层收益更大、端到端却只有 4.3%。

最后我们还注意到，对足够深的模型，LLL 会被约掉；加速与深度无关，而内存代价按 1/L1/L1/L 缩放。模型越深，节省越好。对 48 层的 Qwen3-30B-3A，每个 step 节省 ΔT≈48×δˉ\Delta T \approx 48 \times \bar{\delta}ΔT≈48×δˉ ms（其中 δˉ\bar{\delta}δˉ 是逐层平均节省），而内存代价恒定为 3.7 GB。这让 C2C offloading 对当今前沿开源模型中流行的那种又深又窄的 MoE 架构（DeepSeek-V3、Qwen3-MoE、GLM-5）格外有吸引力。此外我们注意到，C2C offloading 同样适用于 dense 模型，那里通常更小的 dffnd_{ffn}dffn​ 让可行性条件更容易满足。

### 可组合性

一项无法与生产并行方式组合的技术没什么用处。好消息是 C2C offloading 可以干净地落进现有的分布式分片策略里。在我们的 trace 中，FSDP 的 `all_gather` / `reduce_scatter` 跑在 NIC 上，与 C2C copy engine 并行且互不干扰。Tensor parallelism 不受影响（卸载作用在 TP 之后的 per-rank 激活值上），expert parallelism 同样正交（卸载针对 dispatch 之后的激活值）。纸面上看，Pipeline parallelism 似乎也能与 C2C offloading 配合得很好：卸载可以帮助填补 pipeline bubble，因为我们可以用原本空闲的时间把存下来的激活值在主机内存与设备内存之间来回传输。不过这一点纯属我们的假设，因为我们还没有在实验上验证这个组合。

梯度累积也天然可以组合：每个 microbatch 的前向/反向各自独立地卸载与重新加载，而 in-flight buffer 的代价仍然是每个 microbatch 一层的量（前一个 microbatch 的激活值在下一次开始之前已经完全排空）。事实上，activation checkpointing 和卸载彼此相当正交，完全可以把两种做法合成一个混合策略。简而言之，C2C offloading 是叠加式的：我们可以把它放进现有的 FSDP + TP + EP + PP 栈里，而不需要重新架构任何东西。

## 感谢

感谢阅读！如果你有兴趣解决这一类问题，Poolside 的许多团队都在[招聘](https://poolside.ai/careers)——我们很乐意收到你的消息。

## 致谢

我们要感谢 Poolside Architecture 团队，围绕 NVLink C2C offloading 的对话富有成果。也要感谢我们在 NVIDIA 的伙伴们，包括 NVIDIA Inception 项目在这篇博客文章上给予的支持与技术专长。
