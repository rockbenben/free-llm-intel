---
vendor: tencent_hunyuan
title: From LR to ELR: A Better Heuristic for Pretraining Dynamics
original_title: 
url: https://hunyuan.tencent.com/research/elr
date: 2026-08-11
lang: zh
captured: 2026-11-21
extractor: readability-v1
translator: native
status: translated
body_sha: 3c02109bd241
---

2026-08-11Pretrain Team

# From LR to ELR: A Better Heuristic for Pretraining Dynamics

• 摘要在大模型（Large Language Models，LLM）预训练中，超参数是影响效果好坏、控制模型训练动态的关键因素。而学习率（Learning Rate, LR）作为预训练中最重要的超参数之一，却无法精确控制模型参数的演化速率，其最优取值又往往随模型和数据规模的扩大而改变。本文引入了有效学习率（Effective Learning Rate, ELR）来控制模型权重的方向变化。作为可调超参数，ELR 比 LR 更贴近训练的内在动态，因此是更合适的调参依据：在多幂律（Multi-Power Law, MPL）模型中，以 ELR 为依据可以更准确地预测损失，最优 ELR 也能更可靠地迁移到不同规模的模型。进一步地，ELR 这一视角还能指导我们设计更合适的 LR 调度策略，并在实验中优于常规 LR 调度策略基线。

![Clipboard_Screenshot_1785920196.png](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/b729e183/2026080516563630_28c59be2fc21524ca77ae6700c813cc6.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1785920200;2101280200&q-key-time=1785920200;2101280200&q-header-list=&q-url-param-list=&q-signature=b50863f4b82fb3771891afadc797f6f9cbb216c7)

*图 1：Modded-nanoGPT Track 3 优化基准上的结果。* ** MuonH + 负平方根调度策略（minus-square-root schedule）** *仅用 3175 步即达到验证损失值的目标值 3.28，刷新了 MuonH 的最佳性能。*

# 引言

在训练大语言模型（Large Language Model, LLM）时，学习率（Learning Rate, LR）通常被视为控制优化速度最重要的超参数。以迭代 t 时权重 wt 的标准更新为例：

(1)wt+1=(1−ηtλ)⏟权重衰减(Weight Decay)wt−ηtOpt(∇f(wt)⏟梯度(Gradient)).

这里学习率 ηt 对优化器的更新量 Opt(∇f(wt)) 进行缩放后加到权重上，通常会同时改变权重的大小和方向[[1]](https://hunyuan.tencent.com/research/elr#fn:1)[[1]](https://hunyuan.tencent.com/research/elr#fnref:1)[Decoupled Weight Decay Regularization](https://arxiv.org/abs/1711.05101)。然而，由于归一化层（Normalization Layers）在LLM架构中被广泛引入，许多模型权重都具备如下所示的尺度不变性 (scale-invariant)[[2]](https://hunyuan.tencent.com/research/elr#fn:2)[[2]](https://hunyuan.tencent.com/research/elr#fnref:2)[Theoretical Analysis of Auto Rate-Tuning by Batch Normalization](https://arxiv.org/abs/1812.03981)[[3]](https://hunyuan.tencent.com/research/elr#fn:3)[[3]](https://hunyuan.tencent.com/research/elr#fnref:3)[An Exponential Learning Rate Schedule for Deep Learning](https://arxiv.org/abs/1910.07454)：

如果f(cw)=f(w)∀c>0则称w具备尺度不变性.

对于具备尺度不变性的权重而言，方向比大小更重要，但常规的学习率并不能准确刻画权重方向的变化幅度。在实际的 LLM 预训练中，学习率调优也往往颇具挑战：最优学习率会随架构、模型规模和数据规模而变化，因而常常要为每一种新配置重新拟合超参数的缩放律。

为了刻画权重方向的变化幅度，我们可以引入角更新幅度（Angular Update Size, AUS）[[4]](https://hunyuan.tencent.com/research/elr#fn:4)[[4]](https://hunyuan.tencent.com/research/elr#fnref:4)[Rotational Equilibrium: How Weight Decay Balances Learning Across Neural Networks](https://arxiv.org/abs/2305.17212) 的概念，其度量的是相邻训练步间的权重矩阵在归一化到单位球面上之后的距离：

AUS:=‖wt+1‖wt+1‖−wt‖wt‖‖.

注意这里的 AUS 并不是一个新概念。这一概念源于此前对权重衰减（Weight Decay, WD）的一系列动力学分析[[1]](https://hunyuan.tencent.com/research/elr#fn:1) [[5]](https://hunyuan.tencent.com/research/elr#fn:5)[[5]](https://hunyuan.tencent.com/research/elr#fnref:5)[L2 regularization versus batch and weight normalization](https://arxiv.org/abs/1706.05350) [[6]](https://hunyuan.tencent.com/research/elr#fn:6)[[6]](https://hunyuan.tencent.com/research/elr#fnref:6)[Spherical Motion Dynamics: Learning Dynamics of Neural Network with Normalization, Weight Decay, and SGD](https://arxiv.org/abs/2006.08419) [[7]](https://hunyuan.tencent.com/research/elr#fn:7)[[7]](https://hunyuan.tencent.com/research/elr#fnref:7)[Reconciling Modern Deep Learning with Traditional Optimization Analyses: The Intrinsic Learning Rate](https://proceedings.neurips.cc/paper/2020/hash/a7453a5f026fb6831d68bdc9cb0edcae-Abstract.html)。这些研究发现，WD会通过减少权重的模长的方式，间接提升权重方向的变化幅度。感兴趣的读者可以进行拓展阅读。

本文重点关注在 LLM 训练过程中，如何去主动控制模型的 AUS。具体来说，我们将式（1）中的更新规则改写成如下形式，并通过控制其中的有效学习率（Effective Learning Rate, ELR）ηt⋆ 来显式控制 AUS：

wt+1=(1−ηλ)wt−ηt⋆‖wt‖Optt‖Optt‖, 其中 ηt⋆:=η‖Optt‖‖wt‖

我们的研究发现，相比于直接调整普通学习率 LR，以有效学习率 ELR 为依据进行调参往往更加有效。我们的主要发现如下：

- 通过直接控制 AUS，可以**自然导出近期的 Hyperball 优化方法**[[8]](https://hunyuan.tencent.com/research/elr#fn:8)[[8]](https://hunyuan.tencent.com/research/elr#fnref:8)[Fantastic Pretraining Optimizers and Where to Find Them II: Hyperball Optimization](https://arxiv.org/abs/2606.16899)，且 Hyperball 优化器的学习率 LR 实质上就是 ELR。更进一步，只要让标准优化器与其 Hyperball 变体具有相同的 AUS 变化轨迹，就能得到几乎完全一致的损失曲线。
- 借助多重幂律（Multi-Power Law, MPL）模型[[9]](https://hunyuan.tencent.com/research/elr#fn:9)[[9]](https://hunyuan.tencent.com/research/elr#fnref:9)[A Multi-Power Law for Loss Curve Prediction Across Learning Rate Schedules](https://arxiv.org/abs/2503.12811)，**ELR 能够对损失曲线实现比 LR 更准确的预测**，且**最优 ELR 可以更可靠地**跨模型宽度和深度进行迁移。
- 受实际训练中 AUS 的变化规律启发，我们提出了负平方根调度策略（minus-square-root schedule），并将 Modded-nanoGPT Track 3 上 MuonH 的 SOTA 收敛步数**提前了 75 步**，在 3,175 步时即达到了 3.28 的目标损失值。同时，该调度策略在我们的一个最大模型大小为 6B 的混合专家（Mixture of Experts, MoE）模型训练的缩放阶梯（scaling ladder）上，稳定优于基于 linear 及 WSD （Warmup-Stable-Decay）的基线策略。

# AUS、ELR 与 Hyperball 优化

**AUS 的定义：** 令 w^t:=wt‖wt‖，我们定义 AUS 为 w^t 的变化大小：

AUS:=‖w^t+1−w^t‖≈ηt‖Optt⊥‖‖wt+1‖, 其中 Optt⊥=(I−w^tw^t⊤)Optt.

**证明概要**

考虑如下更新规则，可得：

wt+1=(1−ηtλ)wt−ηtOptt=((1−ηtλ)‖wt‖−ηt⟨w^t,Optt⟩)w^t−ηtOptt⊥

定义 C=(1−ηtλ)‖wt‖−ηt⟨w^t,Optt⟩，可得：

‖wt+1‖=‖Cw^t−ηtOptt⊥‖=C2+ηt2‖Optt⊥‖2

因此：

‖wt+1‖2−C2=ηt2‖Optt⊥‖2(‖wt+1‖−C)(‖wt+1‖+C)=ηt2‖Optt⊥‖2‖wt+1‖−C=ηt2‖Optt⊥‖2‖wt+1‖+C

将其代回更新规则，并对权重进行归一化，可得：

w^t+1=C‖wt+1‖w^t−ηt‖wt+1‖Optt⊥w^t+1−w^t=C−‖wt+1‖‖wt+1‖w^t−ηt‖wt+1‖Optt⊥w^t+1−w^t=−ηt2‖Optt⊥‖2‖wt+1‖(‖wt+1‖+C)w^t−ηt‖wt+1‖Optt⊥

对于充分小的 ηt，我们有：

‖wt+1‖+C≥2C≥‖wt‖.

从而：

‖wt+1‖(‖wt+1‖+C)≥‖wt‖2‖wt‖=‖wt‖22.

因此：

‖ηt2‖Optt⊥‖2‖wt+1‖(‖wt+1‖+C)w^t‖≤2ηt2‖Optt⊥‖2‖wt‖2

最终：

w^t+1−w^t=−ηt‖wt+1‖Optt⊥+O(ηt2).

![Clipboard_Screenshot_1785398566.png#320px #146px  #float-right](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/b729e183/2026073016030443_0a853c68dc97c175ab80e690c1baef6a.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1785398587;2100758587&q-key-time=1785398587;2100758587&q-header-list=&q-url-param-list=&q-signature=f21054b4649aeb79bebe49655f492a85fa939017)

令 θ 表示 wt+1 与 wt 之间的夹角，则 AUS 近似为 sin⁡θ：

sin⁡θ=‖(I−w^tw^t⊤)(wt+1−wt)‖‖wt+1‖=ηt‖Optt⊥‖‖wt+1‖.

也就是说，AUS 衡量的是模型权重的角度变化。因此在具备尺度不变性的模型中，AUS 可以很好地作为间接衡量更新步长的代理指标。

那么，我们是否可以直接控制 AUS 呢？如果直接控制 AUS，会发生什么？

**通过 ELR 控制 AUS：** 我们可以从标准的更新规则中分解出 ELR ηt′:=ηt‖Optt⊥‖‖wt+1‖ 的形式：

wt+1=(1−ηλ)wt−ηt′‖wt+1‖Optt‖Optt⊥‖满足‖w^t+1−w^t‖≈ηt′

在该规则下，我们直接调节 ηt′ 来控制 AUS。然而，‖wt+1‖ 无法预先获得，且显式计算正交分量 Optt⊥ 还会引入额外的计算开销。

为解决这些问题，我们引入 ELR ηt⋆:=ηt‖Optt‖‖wt‖ 来近似 ηt′，其对应的更新规则变为：

(2)wt+1=(1−ηλ)wt−ηt⋆‖wt‖N(Optt), 其中 N(x)=x‖x‖.

该近似依赖于两个假设：

- ‖wt+1‖≈‖wt‖：权重衰减（WD）会减小权重范数，而优化器更新通常会增大权重范数。随着训练推进，这两种效应逐渐达到平衡，权重范数进入稳态。
- ⟨Optt,wt⟩≈0：对于具备尺度不变性的目标函数，梯度与权重严格正交，即 ⟨∇f(wt),wt⟩=0。因此，基于梯度的更新与参数近似正交，在高维空间中尤其如此。

> 近期，流形优化在优化器设计中受到越来越多的关注[10][10]Modular Manifolds [11][11]流形上的最速下降：3. Muon + Stiefel [12][12]Controlled LLM Training on Spectral Sphere [13][13]Mano: Restriking Manifold Optimization for LLM Training，这类方法会将每一步的更新向目标流形的切空间进行投影。以嵌入欧氏空间的超球面为例，当前点的切空间恰好由所有与当前权重向量正交的向量构成。在这种设计下，第二个假设自然成立。

**与 Hyperball 优化的关联：** 第一个假设 ‖wt+1‖≈‖wt‖ 并非总是成立，尤其是训练初期。最直接的修正，是在算法中强制权重范数保持为初始值，即 ‖wt‖=‖w0‖，同时去除 WD：

wt+1=‖w0‖⋅N(wt−ηt⋆‖w0‖N(Optt)).

值得注意的是，将上式中的 ‖w0‖ 替换为可配置的超参数 R，即可得到近期提出的 *Hyperball 优化器*[[8]](https://hunyuan.tencent.com/research/elr#fn:8)：

wt+1=R⋅N(wt−ηt⋆R⋅N(Optt)),

与式（1）中不固定权重范数、同时采用WD的标准优化器相比，Hyperball 可以带来 20%–30% 的加速。类似的思想可追溯至 *Van Laarhoven（2017）*[[5]](https://hunyuan.tencent.com/research/elr#fn:5)，该工作提出固定权重范数，从而不再使用 WD。

以上推导与 Hyperball 优化器本身的出发点是一致的：Hyperball 中的 LR 实际上充当 ELR，因此可以直接控制 AUS。为了验证这一点，我们设计了如下实验：

- **基线：** 使用 Adam/Muon 训练一个满足尺度不变性的 GPT-2 模型（124M），并记录每个更新步的 AUS。
- **将 AUS 用作 LR：** 将 Adam/Muon 替换为各自的 Hyperball 变体，并把记录的基线 AUS 轨迹直接设置为 LR 调度所遵循的曲线。

如图 2 所示，在这种设定下，Hyperball 优化器几乎复现了基线的 AUS 曲线。这说明 Hyperball 中的 LR 扮演了 ELR 的角色，并能直接控制 AUS。更关键的是，只要 AUS 轨迹对齐，Hyperball 与基线的损失曲线也会非常接近，也就是说，AUS 是影响训练动态的主要因素之一。

![Clipboard_Screenshot_1785917868.png#center](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/e3076a8f/2026080516182574_c4618616b5a1dd20230e651b39b8205b.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1785917908;2101277908&q-key-time=1785917908;2101277908&q-header-list=&q-url-param-list=&q-signature=9da4a8afd6d5134c966ffc4f573182f51d5336a0)

*图 2. 将基础优化器的 AUS 轨迹作为 LR 调度策略进行重放，会使 Hyperball 优化器产生几乎完全一致的损失曲线和 AUS 曲线。第一行展示 AUS 曲线，第二行展示损失轨迹，第三行展示损失差值。*

**朴素模型上的现象**

对于不具备尺度不变性的朴素 GPT-2 模型，Hyperball 优化器与基线的损失曲线仍大体重合，但在训练初期偏离得更为明显。我们将这一差异归因于 Hyperball 将权重范数固定在相对较小的初始化值上。实验发现，通过仔细调节初始化尺度，可以消除这里的损失差异。

**使用切向动量增强对 AUS 的控制：** 让我们考虑第二个假设：⟨Optt,wt⟩≈0。对具备尺度不变性的模型，梯度本身满足 ⟨∇f(wt),wt⟩=0，但在带动量 mt 的现代优化器中，动量会不断累积历史梯度，因此它与当前权重一般不再满足近似正交假设。因此，我们将动量投影到当前权重处的切空间：

mt=(1−β)mt−1+β∇f(wt)切向动量： mt⊥=(I−w^tw^t⊤)mt

图 3 比较了原始 MuonH 与采用切向动量的 MuonH（即 MuonH-T）。可以看到，后者的 AUS 轨迹与 LR 调度策略更吻合，最终验证损失值也略低。但两者间的差别非常微弱，说明在原始MuonH中，ELR 已经能够很好地控制模型的 AUS。

![Clipboard_Screenshot_1785920515.png](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/b729e183/2026080517020359_57796dfbc185aeb1018af6ba0c28b9bf.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1785920526;2101280526&q-key-time=1785920526;2101280526&q-header-list=&q-url-param-list=&q-signature=32e150f82fc1b01bf00499daa0577157751da75e)

*图 3. 切向动量改善了 Hyperball 优化器对 AUS 的控制。图中分别展示了 MuonH 和 MuonH-T 的 LR 调度策略与 AUS 轨迹。*

本节先定义 AUS，再引入通过 ELR 控制 AUS 的训练视角。沿着这一视角继续推导，就会自然得到广受关注的 Hyperball 优化器。在下文中，我们将以 Hyperball 优化器作为实验对象，研究 ELR 的性质。

**核心结论：** AUS 可以通过 ELR 被显式控制，而 Hyperball 优化器中的 LR 扮演了 ELR 的角色。

# ELR 有何优势？

本节将深入分析 ELR 的两个重要性质。

**性质 I - ELR 能够更准确地预测损失轨迹：** 预训练中有一个常见现象：如果两次训练的累积 LR（ ∑i=1tηi）相近，它们往往会达到相近的最终损失值。受此启发，*Luo 等人（2025）*[[9]](https://hunyuan.tencent.com/research/elr#fn:9) 提出了多重幂律（Multi-Power Law, MPL）模型，根据 LR 调度策略对验证损失值进行预测。*Tissue 等人（2024）*[[14]](https://hunyuan.tencent.com/research/elr#fn:14)[[14]](https://hunyuan.tencent.com/research/elr#fnref:14)[Scaling law with Learning Rate Annealing](https://arxiv.org/abs/2408.11029) 和 *Li 等人（2025）*[[15]](https://hunyuan.tencent.com/research/elr#fn:15)[[15]](https://hunyuan.tencent.com/research/elr#fnref:15)[ Functional Scaling Laws in Kernel Regression: Loss
Dynamics and Learning Rate Schedules](https://proceedings.neurips.cc/paper_files/paper/2025/hash/92abec9d3f278c648dfe99c8b8f35954-Abstract-Conference.html)也提出过类似的模型。

先简要回顾 MPL 模型。模型包含两项：第一项刻画累积 LR 的作用，第二项刻画 LR 衰减的作用。原始模型的衰减项含有较复杂的非线性表达式。这里我们采用一个简化版本：去掉这部分非线性表达式，同时保留了模型较强的预测能力。其形式如下：

L(t)=L0+A(∑i=1tηi+Sw)−α⏟累积 LR 的贡献−B∑i=1t(ηi−1−ηi)⏟LR 衰减的贡献=L0+A(∑i=1tηi+Sw)−α−Bηt

该模型包含 4 个拟合参数：L0,A,α 和 B。其中，Sw 表示预热阶段的累积 LR，i=1 对应预热结束后的第一个训练步。

为了比较 LR 和 ELR 的预测能力，我们把 MPL 模型中的 LR η 换成 ELR η⋆，再分别拟合两种模型。拟合数据来自 65 组 Muon 实验，这些实验来自对线性和 WSD 调度策略的扫描。图 4 从两个角度评估 MPL 模型：

- **样本内拟合性能：** 将观测到的验证损失轨迹与 MPL 模型拟合后给出的预测结果进行比较，我们发现基于 ELR 的模型比基于 LR 的模型预测更准确。
- **泛化性能：** 依次将六个指定实验中的一个作为测试样本，用其余实验重新拟合 MPL 模型，再预测该测试样本的验证损失值。在六轮测试中，基于 ELR 的模型预测都更准确。

![mpl_linear_wsd.png#790px #438px #center](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/b729e183/2026072715031010_6eb18db04f97290dc5483c61bf364d97.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1785135792;2100495792&q-key-time=1785135792;2100495792&q-header-list=&q-url-param-list=&q-signature=0d68de462deddd85f493f479f724ec1bbc249568)

*图 4. 基于 ELR 和基于 LR 的 MPL 模型对比。第一行展示样本内拟合，第二行展示泛化。在两种设置下，基于 ELR 的模型都能更准确地预测验证损失值。*

> 需要说明的是，我们只考察在相同调度策略下进行预测的情况。相比之下，Luo 等人（2025）[9] 在多种调度策略上拟合模型，并验证了模型对没有见过的调度策略的泛化能力。

在两种设置下，ELR 对验证损失值的预测都比 LR 更准确，表明它能够更好地刻画训练动态。

**性质 II - ELR 可以更可靠地跨模型规模迁移：** LR 迁移是大规模预训练中的核心挑战，目标是在较小模型上调好 LR，再直接迁移到更大规模的训练任务。*Wen 等人（2026）*[[8]](https://hunyuan.tencent.com/research/elr#fn:8) 发现，Hyperball 优化器的 LR 在不同模型规模之间有很强的迁移能力，并把这一能力归因于 Hyperball 对 AUS 的直接控制。由此产生一个自然的问题：这种迁移能力是否必须依赖超球面约束，还是仅靠 ELR 就能获得？

为验证这一点，我们考虑式（2）中的更新规则，并分别考察 ELR 与超球面约束各自的作用：

wt+1=(1−ηλ)wt−ηt⋆‖wt‖N(Optt).

基于这一更新规则，我们在满足尺度不变性的 GPT-2 模型上做宽度缩放扫描：只改变模型宽度，其他训练设置保持不变。图 5 表明，只改变模型宽度时，最优常规 LR 会明显偏移，而最优 ELR 始终落在更窄的范围内。只改变层数做深度缩放扫描时，最优 ELR 同样在不同深度下保持稳定。Yang 等人（2026）[[16]](https://hunyuan.tencent.com/research/elr#fn:16)[[16]](https://hunyuan.tencent.com/research/elr#fnref:16)[On the Nonlinearity of Learning Rate Scaling for LLM Training](https://arxiv.org/abs/2606.29158) 也表明，ELR 的超参数缩放律比 LR 的缩放律更加线性。

![width_depth_scaling_val_loss_vs_lr.png#center](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/b729e183/2026072715011567_1a6f01d58f4e63e121f65df5c222903e.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1785135676;2100495676&q-key-time=1785135676;2100495676&q-header-list=&q-url-param-list=&q-signature=4956af2bbc17add0c560f2cb07bdcbedc92e5fd7)

*图 5. LR 与 ELR 跨模型规模迁移能力的对比。使用式（2）的更新规则直接调节 ELR，而 LR 则通过标准更新规则调节。在两种设置下均使用 Muon 作为基础优化器。*

需要指出的是，最优的 ELR 调度策略**不能**直接跨不同训练总步数之间迁移。另外，ELR 调度策略与常规 LR 调度策略也大不相同。在下一节中，我们将进一步分析 AUS 的变化规律和 ELR 调度策略。

**核心结论：** 相比常规 LR，ELR 是一种预测能力更强、迁移能力更好的启发式指标。

# AUS 的变化规律

我们已经看到了控制 ELR 可以带来诸多优势，但训练过程中的 ELR 最优调度策略如何，尚需进一步研究。对此，我们提出了两个问题：

*什么样的 ELR 调度策略最优？它随训练规模的迁移规律是怎样的？*

ELR 调度策略的选择空间是非常大的。为寻找有效的调度策略，我们首先以标准 Muon（非 Hyperball）训练为基准，记录了三类常见 LR 调度策略（WSD、余弦、线性）在不同预热步数和峰值 LR 下的 AUS 轨迹，结果见图 6。

![Clipboard_Screenshot_1785920236.png](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/b729e183/2026080516572188_50dad8b08346113b62955091db10948e.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1785920244;2101280244&q-key-time=1785920244;2101280244&q-header-list=&q-url-param-list=&q-signature=736a36fa53ed93bbf414cf0a50063eaf5f59a469)

*图 6. 在 WSD、余弦和线性调度策略下对预热步数与峰值 LR 进行扫描。图中展示了 LR 调度策略以及最后一层各权重矩阵对应的 AUS 轨迹。*

- **规律 I - 角度坍缩：** 尽管不同 LR 调度策略彼此差异很大，但对应的 AUS 轨迹却非常接近，尤其是在训练初期。我们把这种现象称为 *角度坍缩（angular collapse）*。这意味着效果较好的 ELR 调度策略可能集中在比 LR 调度策略更窄的范围内。
- **规律 II - 两阶段动态：** AUS 轨迹还呈现出清晰的两个阶段：*训练初期*。AUS 快速上升，随后急剧下降。与 LR 调度策略相比，该阶段的预热更短、峰值显著更高。*训练后期*。AUS 轨迹基本遵循 LR 调度策略的形状。

这两条 AUS 的变化规律表明，常见的 LR 调度策略可能无法直接迁移到 ELR。

图 7 进一步展示了每组 LR 调度策略中验证损失值最低的实验。在联合调优预热步数和峰值 LR 后，线性调度策略取得了最低的验证损失值，也显著优于 WSD。因此，最佳线性调度策略对应的 AUS 轨迹可以作为设计更优 ELR 调度策略的起点。

![Clipboard_Screenshot_1785920349.png #570px #445px #center](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/b729e183/2026080516591195_1824c9a71c0979aa22333e00132c719c.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1785920354;2101280354&q-key-time=1785920354;2101280354&q-header-list=&q-url-param-list=&q-signature=9f19799a1e1a83544f2f1be1a84c6f5a0ae32900)

*图 7. 各组 LR 调度策略中表现最好的实验。采用线性调度策略的实验取得了最低的验证损失值。*

**权重范数的动态解释了 AUS 的变化规律：** 回顾 AUS≈ηt‖Optt⊥‖‖wt+1‖。当 ‖Optt⊥‖ 近似恒定时，AUS 主要由 ηt 和 ‖wt+1‖ 决定。ηt 遵循 LR 调度策略，而近期研究[[6]](https://hunyuan.tencent.com/research/elr#fn:6) [[7]](https://hunyuan.tencent.com/research/elr#fn:7) 表明，权重范数通常会先快速变化，随后进入稳态。

以梯度下降为例：wt+1=(1−ηλ)wt−η∇f(wt)，对于具备尺度不变性的目标函数，只要满足

‖∇wt⊥f(w^t)‖≥2λη‖wt‖2.

权重范数就会增大。在初始化阶段，相比梯度范数，‖w0‖2 通常更小，因此该条件很容易满足，权重范数也会快速增长。当训练进行到足够大的步数 T 时，权重范数进入稳态，并近似满足：

‖wT‖2≈η2λ‖∇wT⊥f(w^T)‖.

**证明概要**

回顾尺度不变性 f(cw)=f(w)，可得：

∇f(w)=I−w^w^⊤‖w‖∇f(w^)=1‖w‖∇w⊥f(w^)

权重范数按如下方式更新：

‖wt+1‖2=‖(1−ηλ)wt−η∇f(wt)‖2=(1−ηλ)2‖wt‖2+η2‖wt‖2‖∇wt⊥f(w^t)‖2

因此可将其改写为：

‖wt+1‖2−‖wt‖2=(−2ηλ+η2λ2)‖wt‖2+η2‖wt‖2‖∇wt⊥f(w^t)‖2≥−2ηλ‖wt‖2+η2‖wt‖2‖∇wt⊥f(w^t)‖2

因此，权重范数增大的一个充分条件是：

η2‖wt‖2‖∇wt⊥f(w^t)‖2≥2ηλ‖wt‖2⟺‖∇wt⊥f(w^t)‖≥2λη‖wt‖2

对于充分大的训练步 T，还可以求解稳态权重范数：

‖wT‖2=(1−ηλ)2‖wT‖2+η2‖wT‖2‖∇wT⊥f(w^T)‖2=η2ηλ−η2λ2‖∇wT⊥f(w^T)‖≈η2λ‖∇wT⊥f(w^T)‖

- 稳态权重范数可以解释 *AUS 轨迹坍缩*。将 ‖wT‖2 代入 ELR 的定义，可得AUS≈η‖∇wT⊥f(w^T)‖‖wT‖2=2ηλ.对于固定的 λ，稳态 AUS 仅按 AUS∝η 缩放。这种平方根缩放使 AUS 的变化幅度远小于常规 LR，从而导致轨迹坍缩。
- 权重范数的演化也解释了两阶段动态。在训练初期，‖wt‖ 的快速增长使 AUS 比常规 LR 更早开始下降，从而有效缩短预热阶段。进入训练后期，随着权重范数趋于稳定，AUS 更多地由 LR 决定，并紧密地遵循其调度策略形状。

**AUS 的预热步数和峰值对训练时长并不敏感。** 我们在不同的训练总步数下，扫描线性调度策略的预热步数和峰值 LR，并将验证损失值较低的实验展示在图 8 中。随着训练时长增加，效果较好的 LR 调度策略往往需要更长的预热步数和更低的峰值；但对应的 AUS 轨迹变化并不大，预热步数只略微增加，峰值也只小幅变化。因此我们推测，在不同训练步数上搜索最优 ELR 调度策略时，预热步数和峰值的调优空间会比常规 LR 调度策略更窄。

![Clipboard_Screenshot_1785920394.png](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/b729e183/2026080516595629_47b60035ab31ad89e3aa18caa4439c72.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1785920400;2101280400&q-key-time=1785920400;2101280400&q-header-list=&q-url-param-list=&q-signature=99c3fb14b1d9cb6a0d38e1dfd02093353a0123d7)

*图 8. 在线性调度策略下，跨不同训练时长扫描预热步数与峰值 LR。图中展示了 LR 调度策略以及最后一层各权重矩阵对应的 AUS 轨迹。*

**核心结论：**AUS 在训练初期变化迅速，随后逐渐平滑，并在不同模型组件间呈现一致的两阶段模式。

# 设计更优的ELR调度策略

下面我们转向调度策略设计：以前一节总结的 AUS 模式为线索，我们在 Hyperball 优化器上构造更有效的 ELR 调度策略。前文已经提到，在 Hyperball 优化器中，LR 调度策略等同于 ELR 调度策略。

**负平方根调度策略（minus-square-root schedule）:** AUS 的两阶段动态启发我们设计一种 ELR 调度策略：它的预热更短，早期峰值更高，随后先快速衰减，再逐渐转为平缓。为此，我们考虑指数 p=0.5 的幂衰减调度策略，并将其称为*负平方根调度策略*。经过 tw 步的线性预热后，调度策略为

ηt⋆=ηpeak⋆(1−(t−TwT−Tw)p)=ηpeak⋆(1−t−TwT−Tw),tw≤t≤T.

我们在 modded-nanoGPT Track 3 基准上评估该调度策略。如图 9 所示，采用精心调优的负平方根调度策略后，MuonH（MuonH-msqrt）[[17]](https://hunyuan.tencent.com/research/elr#fn:17)[[17]](https://hunyuan.tencent.com/research/elr#fnref:17)[Track 3: MuonH minus-square-root schedule reaches 3.28 at 3175 steps](https://github.com/KellerJordan/modded-nanogpt/pull/343) 在 3,175 步时达到 3.28 的目标验证损失值，比此前 MuonH-linear 的 SOTA 提前了 75 步。

![Clipboard_Screenshot_1785920475.png](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/b729e183/2026080517011799_122a2fb51e4fd15748986645552f2b55.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1785920480;2101280480&q-key-time=1785920480;2101280480&q-header-list=&q-url-param-list=&q-signature=cf002339debccf8b0c732c65c4fb201b9474a9f8)

*图 9. modded-nanoGPT Track 3 优化基准结果。MuonH-msqrt[[17]](https://hunyuan.tencent.com/research/elr#fn:17) 在 3,175 步时达到 3.28 的目标验证损失值，将此前的 MuonH-linear 结果提前了 75 步。PR #345[[18]](https://hunyuan.tencent.com/research/elr#fn:18)[[18]](https://hunyuan.tencent.com/research/elr#fnref:18)[Track 3: MuonH power-0.4 schedule reaches 3.28 at 3150 steps](https://github.com/KellerJordan/modded-nanogpt/pull/345)[[19]](https://hunyuan.tencent.com/research/elr#fn:19)[[19]](https://hunyuan.tencent.com/research/elr#fnref:19)[Hyperball May Not Be a Free Lunch](https://arxiv.org/abs/2607.22444) 中的 MuonH-power 在 3,150 步时达到目标。*

更重要的是，这一调度策略正好对应了上一节总结出的两条变化规律：

- **短预热与高峰值：** 该调度策略采用 100 步预热，峰值为 0.0300。相比线性基线，峰值提高至 1.67 倍。
- **快速衰减与更平滑的尾部：** 预热结束后，ELR 会先快速下降，临近训练结束时再逐渐贴近线性调度策略；这一形状与图 7 中最佳线性调度策略的 AUS 轨迹相似。

> PR #345[18][19] 独立提出了一种类似的调度策略，在 3,150 步时达到 3.28 的目标验证损失值。该调度策略采用相同的峰值 0.0300，随后以指数 0.4 进行幂衰减。这一结果印证了我们此前对 ELR 调度策略的理解。

随后，我们在覆盖多种计算预算的缩放阶梯实验中评估了 MuonH-msqrt。最大设置是在 6B MoE 模型上训练 32.7B token。在这一设定下，MuonH-msqrt 的验证损失值低于 MuonH-linear、Muon-WSD 和 Muon-linear。图 10 进一步表明，它在各个计算预算下都取得了最优性能。不过，MuonH-msqrt 拟合出的缩放曲线更平缓，斜率绝对值也略小。按这一拟合趋势外推，它在更大计算量下的优势可能会消失。

![Clipboard_Screenshot_1786085280.png#center](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/e3076a8f/2026080714510838_e0b82c0920759548101b7720085c0c13.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1786085469;2101445469&q-key-time=1786085469;2101445469&q-header-list=&q-url-param-list=&q-signature=e3e46047d75656860361f27439c3253aadc42a5c)

*图 10：在约 32.7B token 上训练的 6B MoE 模型的训练损失值曲线与验证损失值曲线（左图和中图），以及覆盖多种计算预算的缩放阶梯结果（右图）。MuonH-msqrt 在每个测量到的计算预算下都取得了最低的损失值。*

**分段线性调度策略（piecewise linear schedule）:** 负平方根调度策略已经体现了我们观测到的两阶段动态，但其早期下降和后期衰减都由同一个指数 ρ 控制，因此调优时不够灵活。基于这一点，我们进一步考虑更灵活的分段线性调度策略。如图 11 所示，该调度策略包含两个阶段：

- **早期阶段 - 高峰值与快速衰减：** 相比负平方根调度策略，分段线性调度策略达到更高峰值，随后更加快速地下降到一个中间点。
- **后期阶段 - 严格线性衰减：** 从中间点开始，ELR 线性衰减至零，与前文观测到的后期模式直接匹配。

在 nanoGPT 实验中，分段线性调度策略取得了比负平方根调度策略和线性调度策略更低的训练损失值与验证损失值。

![Clipboard_Screenshot_1785918377.png #center](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/b729e183/2026080516262025_1f6fa6eb5784f4dd44afd7b0ddd29690.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1785918383;2101278383&q-key-time=1785918383;2101278383&q-header-list=&q-url-param-list=&q-signature=9ee0835c36811d054f1f32e0c922a7a9f18bece4)

*图 11. 在 nanoGPT 上比较 MuonH 配合线性调度策略、负平方根调度策略和分段线性调度策略时的表现。分段线性调度策略取得了最低的验证损失值。*

**如何调节分段线性调度策略的中间点**

分段线性调度策略引入了两个额外超参数：中间点的位置和取值。图 12 展示了对中间点位置和取值进行的网格搜索，最优中间点似乎位于训练较早阶段，且取值较低。不过，该调度策略的迁移能力仍是一个有待研究的问题。

![Clipboard_Screenshot_1785918334.png #center]()

*图 12. 对中间点的位置和值进行网格搜索。在评估的网格范围内，当中间点位于训练较早阶段且取值较低时，能够得到最低的验证损失值。*

*总结而言*，我们提出了两种适配 AUS 两阶段模式的 ELR 调度策略。由于 Hyperball 优化器可以直接控制 AUS，只要调整 LR 调度策略，就能直接从这些 ELR 调度策略中获益，并取得更优性能。

**核心建议：** 下次跑实验，试试负平方根调度策略和分段线性调度策略！

# 未来工作

我们认为，ELR 更直接地刻画了 LLM 预训练中的优化动态。ELR 直接控制了 AUS，这对于具备尺度不变性的 LLM 权重来说尤为重要。我们已将从 ELR 中获得的若干洞见应用于前沿模型的实际生产。

我们的探索只是 ELR 调度策略研究的一个起点。一个关键的开放问题是：为什么训练初期可以容忍更高的峰值 ELR，甚至常常能从中受益，而训练后期却更适合缓慢、近似线性的衰减？除了理解这一现象，我们还希望为 ELR 的超参数建立缩放律，例如峰值和预热时长，使其能够在不同数据量和模型规模之间可靠迁移。展望未来，我们希望把常规 LR 调度策略转向 ELR 调度策略，从而更直接地控制训练动态、实现更好的超参数迁移，并提高 LLM 预训练的可预测性。

> 贡献者：Zhanpeng Zhou∗, Wenjie Zhou∗, Yufei Gu∗, Juqiu Wang, Guanwei Zhang†, Ruobing Xie, Xianbiao Qi, Yushi Bai†, Kaifeng Lyu, Shunyu Yao （∗：同等贡献；†：通讯作者。）

# 引用

bibtex

```
@misc{zhou-zhou-gu-2026-elr,
  title = {From LR to ELR: A Better Heuristic for Pretraining Dynamics},
  author = {Zhou, Zhanpeng and Zhou, Wenjie and Gu, Yufei and Wang, Juqiu and Zhang, Guanwei and Xie, Ruobing and Qi, Xianbiao and Bai, Yushi and Lyu, Kaifeng and Yao, Shunyu},
  year = {2026},
  url = {https://hy.tencent.ai/research/elr}
}
```

# 致谢

感谢 ProdEng 团队提供的技术支持。也感谢 Jiacheng You、Kairong Luo、Yifeng Liu、Zeke Xie 和 Lambert Wong 围绕优化理论及 ELR 理论细节展开的宝贵讨论。

脚注

[[1]](https://hunyuan.tencent.com/research/elr#fnref:1)[Decoupled Weight Decay Regularization](https://arxiv.org/abs/1711.05101)

[[2]](https://hunyuan.tencent.com/research/elr#fnref:2)[Theoretical Analysis of Auto Rate-Tuning by Batch Normalization](https://arxiv.org/abs/1812.03981)

[[3]](https://hunyuan.tencent.com/research/elr#fnref:3)[An Exponential Learning Rate Schedule for Deep Learning](https://arxiv.org/abs/1910.07454)

[[4]](https://hunyuan.tencent.com/research/elr#fnref:4)[Rotational Equilibrium: How Weight Decay Balances Learning Across Neural Networks](https://arxiv.org/abs/2305.17212)

[[5]](https://hunyuan.tencent.com/research/elr#fnref:5)[L2 regularization versus batch and weight normalization](https://arxiv.org/abs/1706.05350)

[[6]](https://hunyuan.tencent.com/research/elr#fnref:6)[Spherical Motion Dynamics: Learning Dynamics of Neural Network with Normalization, Weight Decay, and SGD](https://arxiv.org/abs/2006.08419)

[[7]](https://hunyuan.tencent.com/research/elr#fnref:7)[Reconciling Modern Deep Learning with Traditional Optimization Analyses: The Intrinsic Learning Rate](https://proceedings.neurips.cc/paper/2020/hash/a7453a5f026fb6831d68bdc9cb0edcae-Abstract.html)

[[8]](https://hunyuan.tencent.com/research/elr#fnref:8)[Fantastic Pretraining Optimizers and Where to Find Them II: Hyperball Optimization](https://arxiv.org/abs/2606.16899)

[[9]](https://hunyuan.tencent.com/research/elr#fnref:9)[A Multi-Power Law for Loss Curve Prediction Across Learning Rate Schedules](https://arxiv.org/abs/2503.12811)

[[10]](https://hunyuan.tencent.com/research/elr#fnref:10)[Modular Manifolds](https://thinkingmachines.ai/blog/modular-manifolds/)

[[11]](https://hunyuan.tencent.com/research/elr#fnref:11)[流形上的最速下降：3. Muon + Stiefel](https://spaces.ac.cn/archives/11221)

[[12]](https://hunyuan.tencent.com/research/elr#fnref:12)[Controlled LLM Training on Spectral Sphere](https://arxiv.org/abs/2601.08393)

[[13]](https://hunyuan.tencent.com/research/elr#fnref:13)[Mano: Restriking Manifold Optimization for LLM Training](https://arxiv.org/abs/2601.23000)

[[14]](https://hunyuan.tencent.com/research/elr#fnref:14)[Scaling law with Learning Rate Annealing](https://arxiv.org/abs/2408.11029)

[[15]](https://hunyuan.tencent.com/research/elr#fnref:15)[ Functional Scaling Laws in Kernel Regression: Loss
Dynamics and Learning Rate Schedules](https://proceedings.neurips.cc/paper_files/paper/2025/hash/92abec9d3f278c648dfe99c8b8f35954-Abstract-Conference.html)

[[16]](https://hunyuan.tencent.com/research/elr#fnref:16)[On the Nonlinearity of Learning Rate Scaling for LLM Training](https://arxiv.org/abs/2606.29158)

[[17]](https://hunyuan.tencent.com/research/elr#fnref:17)[Track 3: MuonH minus-square-root schedule reaches 3.28 at 3175 steps](https://github.com/KellerJordan/modded-nanogpt/pull/343)

[[18]](https://hunyuan.tencent.com/research/elr#fnref:18)[Track 3: MuonH power-0.4 schedule reaches 3.28 at 3150 steps](https://github.com/KellerJordan/modded-nanogpt/pull/345)

[[19]](https://hunyuan.tencent.com/research/elr#fnref:19)[Hyperball May Not Be a Free Lunch](https://arxiv.org/abs/2607.22444)

目录

[ 引言]()[ AUS、ELR 与 Hyperball 优化]()[ ELR 有何优势？]()[ AUS 的变化规律]()[ 设计更优的ELR调度策略]()[ 未来工作]()[ 引用]()[ 致谢]()

评论（0）

0/2000

### 继续阅读

![Hy4 preview 发布](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026082914161695_a99d8e4fdac07d233f015c0206772b08.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1787984177;2103344177&q-key-time=1787984177;2103344177&q-header-list=&q-url-param-list=&q-signature=7b9c494dad35e6b11e0b8655c60f51ecf6fde2f3)

Hy4 preview 发布

2026-08-28Hy LLM

![Hyra: 简单有效的科学发现智能体](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/210b8ba1/2026072023004586_f2fa05a3a80068a295e536f8935f0546.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1784559645;2099919645&q-key-time=1784559645;2099919645&q-header-list=&q-url-param-list=&q-signature=90729bdaf96831ef0565215012a0b323088c3258)

Hyra: 简单有效的科学发现智能体

2026-07-21Hyra Team

![Hy3 正式发布](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026070613543257_0151de0813ddc1ed78746a88c07c1b9d.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1783317273;2098677273&q-key-time=1783317273;2098677273&q-header-list=&q-url-param-list=&q-signature=bb734fb07aaabe1bb009d463e0f9006e03ea0382)

Hy3 正式发布

2026-07-06Hy LLM
