---
vendor: cerebras
title: MoE 规模化：让稀疏模型在真实硬件上跑得快
original_title: 
url: https://www.cerebras.ai/blog/moe-guide-scale
date: 
lang: zh
captured: 2026-10-15
extractor: readability-v1
translator: agent
status: translated
body_sha: a2fa8e500b0c
---

Oct 06 2026

# MoE 规模化：让稀疏模型在真实硬件上跑得快

[Daria Soboleva](https://www.cerebras.ai/author/dariasoboleva)[Quentin Anthony](https://www.cerebras.ai/author/quentin-anthony)

[MoE 基础](https://www.cerebras.ai/blog/moe-guide-why-moe) | [Router 之争](https://www.cerebras.ai/blog/moe-guide-router) | [调试死掉的 MoE 模型](https://www.cerebras.ai/blog/moe-guide-debug) | [MoE 大规模化 ](https://www.cerebras.ai/blog/moe-guide-scale)| [MoE 数学解密](https://www.cerebras.ai/blog/moe-guide-calculator)

在本视频中，我们讨论如何在现代硬件上扩展 MoE 模型的规模，并应对几个关键的优化难题。如果打不开上面显示的视频，请用这个链接到 YouTube 上观看：[https://youtu.be/MXo9LEYzwkg](https://youtu.be/MXo9LEYzwkg)

Mixture-of-Experts（MoE）模型让你在计算量不成比例增长的前提下提高总参数量，从而高效地训练更大、更好的模型（Soboleva, 2025a）。你也许会问，要把 MoE 模型的理论收益真正榨出来，是否需要大量工程工作。毕竟，你在第 3 篇里的那个实现（Soboleva and Tiwari, 2025）在一个小规模加速节点上（甚至在你自己的笔记本上）训练得毫无问题。这里的要点是，你只用了 4 个 expert 和 124M 的 backbone 参数，而 DeepSeek-V3、Qwen3-30B-A3B 这类生产系统用的是数百个 expert 和体量巨大的 backbone。试着用我们之前那版实现在 GPU 上扩展到它们的规模，你很快就会撞上设备的内存上限。

我们来弄清这是为什么。还记得第 3 篇里我们在图 1 展示的那段代码吗？当时我们就提醒过，那段代码并不高效，只是用于教学。为什么？从图 1 可以看到，那里对所有 expert 做了串行循环，而我们其实只需要给定 token 被选中的那些 expert。你可能会问，为什么这么浪费？你已经知道，业界通行的 routing 并不是确定性的（Soboleva, 2025b），因此无法提前预测给定 token 会激活哪个 expert。这就意味着我们不得不把所有 expert 都载入内存，以防后面要用到它们（在内存带宽与延迟的限制下，为每个 token 实时把 expert 权重搬进 GPU 内存会太慢）。因此，随着你增加 expert 数量，内存需求线性增长，很快就无法在单张 GPU 上训练（用我们之前那版实现，十几个 expert 都装不下）。

本指南余下的部分介绍应对这一规模化难题的方案。首先我们讨论 GPU 方案及其局限，其次介绍 Cerebras Wafer Scale Engine（WSE）如何解决这个问题，最后说明如何把两者结合以最大化收益。

图 1：面向批处理的 expert 混合（见 train [train_gpt moe.pyL208-L225](https://github.com/cat-state/modded-nanogpt-moe/blob/blogpost-version/train_gpt_moe.py##L208-L225)）。

### GPU 方案及其问题

当你的 MoE 模型超出单张 GPU 的内存容量时，最流行的解法是采用某种模型并行，expert parallelism 就是其中一个例子，简称 EP（Lepikhin et al., 2020; DeepSeek-AI et al., 2024）。用 EP 时，我们通常给每张 GPU 分配数量相同的 expert，而其余所有层（attention、router 等）在每台设备上都存一份副本。在这个流程里，router 先预测哪些 token 该被路由到哪些 expert，随后一次 all-to-all 通信操作按 router 的分配把 token 交换到正确的设备上，并行执行每个 expert，再把结果交换回 token 原来的设备，完成 expert 混合。

要让 EP 高效，网络中所有层的 expert 都必须做到负载均衡。这在模型质量与基础设施效率之间制造了张力。追求最佳模型质量的 ML 研究者往往更偏爱能让 expert 高度专业化的 routing 策略（Soboleva, 2025b），即使这会造成负载失衡。与此同时，基础设施团队需要可预测、均衡的负载，才能达到最优的硬件利用率并把训练成本压到最低。两个目标都至关重要，方向却彼此拉扯。激进的负载均衡会把 token 推给并不合适的 expert，从而损害模型质量（我们在 hash routing 上就见过这种情况）。而负载失衡的 expert 又会造成昂贵的基础设施瓶颈：一些 GPU 空转，另一些被压满，整体硬件利用率大幅下降。

此外，EP 还会引入通信开销，并且随着 expert 数量增加而恶化。为了更高的计算效率，现代 MoE 架构会为每个 token 激活许多较小的 expert，而不是数量少但体积大的 expert（Krajewski et al., 2024）。可在这套配置下，要用 EP 做并行就必须依赖强力的负载均衡，而这会影响模型质量。如果你无法用质量换速度（即激进的负载均衡），EP 的通信/计算比就会恶化：大部分时间都花在搬运 token 上，而不是 expert 在它们上面执行有用的运算。总的来说，在 GPU 上训练 MoE 模型依然棘手，因为单靠 EP 通常不足以产生足够的并行度。

### Cerebras WSE 与 GPU（架构差异）

在 GPU 上跑大型 MoE 模型，除了 expert parallelism 通常还需要叠加多种并行策略。例如 DeepSeek-V3 就组合使用了流水线并行、expert parallelism 与数据并行（DeepSeek-AI et al., 2024）。这带来一套复杂的 3D 并行实现，你必须仔细调优，而且模型或集群任一发生变化时都得重新调。用 Cerebras WSE 则不需要分布式计算。我们只用数据并行来训练和扩展模型。是什么让这成为可能？我们的片上内存（SRAM）比最新的单张 GPU 多约 900 倍，因此可以把大得多的模型直接存放在芯片上。向更大模型扩展时，我们采用一种叫 weight streaming 的技术（Hall et al., 2023），把 WSE 上的内存与计算解耦。用 weight streaming 时，我们把模型参数（那些沉重的张量）彻底移出晶圆，它们改存放在外部内存单元里，训练时再流式送入晶圆来计算梯度；晶圆又把梯度流式送回内存单元去更新权重。这项技术让我们仅用一台设备就能训练如今的万亿参数 MoE 模型（Kimi Team, 2025）。

### 内存问题解决了，接着是计算

我们已经说明，Cerebras WSE 凭借 weight streaming 可以把大型 MoE 模型直接放进芯片，无需任何模型并行。但你能训练万亿参数的 MoE，并不意味着它高效。随着模型变得更稀疏（expert 更多、*top_k* 更低），我们撞上的是另一个问题：计算利用率。还记得本系列第 1 篇里承诺的、用 32 个 expert 带来的 62% FLOPs（Floating Point Operations，浮点运算次数）下降吗？当时我们指出，这会让 MoE 模型达到同样 loss 的训练速度比 dense 基线快 3 倍。可实践中看到的并不是这样。实际情况是，我们没能把这些 FLOP 的节省转化为真实的 wall-clock 加速，大规模训练 MoE 模型变得低效。

这为什么会发生？在稀疏的 MoE 模型里，routing 会把 batch size 切分到许多 expert 上，结果是大多数 expert 只看到原始 batch 的一小部分。batch 一小，就意味着多数 expert 在空转，没有执行有用的运算。你加载了大型 expert 网络的矩阵，却几乎没用上它们（在这些层里你会变成 I/O bound）。与此同时，attention 层又处理不了更大的 batch，因为它们受激活内存（activation memory）限制（Anthony et al., 2023; Korthikanti et al., 2022）。这意味着它们必须存放庞大的中间张量，例如 attention scores，其规模随序列长度呈二次增长 [1]。于是 expert 层与 attention 层之间存在一道持续的利用率鸿沟：expert 网络在挨饿，等着更多数据进来供它们处理；而 attention 层又难以高效处理更大批量的 token，使我们没办法把数据更快地送进 expert 网络。

### Batch Tiling on Attention

为解决这个问题，在 Cerebras WSE 上我们把 attention 与 expert 网络对 batch size 的需求解耦。这项技术我们称为 Batch Tiling on Attention（BTA）。用 BTA 时，我们把 attention 的输入 batch size 切成 G 个大小为 B 的 tile，每个 tile 独立处理，再把结果拼接回去，得到 G × B 的大 batch 送进 expert 网络（图 2）。

图 2：Batch Tiling on Attention（BTA）架构。输入 batch 被切成 G 个 tile，每个 tile 以小 batch size B 通过 attention；输出被拼接成 G × B 的大 batch 供 expert 处理，从而解耦 attention 层与 expert 层对 batch size 的约束。

与 FlashAttention（Dao et al., 2022）沿序列维度切 tile 以降低内存占用的思路类似，BTA 沿 batch 维度切 tile，用来改善 expert 网络与 attention 网络之间失衡的利用率。BTA 的双 batch 策略直接对准 MoE 的计算需求：我们在 attention 层使用更小的 batch 以减少其激活内存，在 expert 网络使用更大的 batch 以提升其计算利用率。

我们来给 BTA 做一次压力测试：在单台 CS-3 机器上运行近期一个名为 Qwen3-30B-A3B、含 3B 激活参数的 MoE 模型（Yang et al., 2025）。该模型原本使用 learned routing，共 128 个 expert，每个 token 激活 *top_k* = 8 个。我们将改变 *top_k* 和 expert 数量，从而改变模型的稀疏度，并观察在有无 BTA 两种情况下稀疏度对吞吐量的影响。

首先，我们把 *top_k* 固定在 8，让 expert 数量从 16 变到 128，测量相比激活参数量相同的 dense 模型，吞吐量退化到什么程度。图 3a 显示，「red」线（不用 BTA 的传统 batching）退化严重，在 128 个 expert 时最高达到 53%（相当于慢 2 倍）。「blue」线（使用 BTA，并把 G 值调到能取得最快速度）显示吞吐量始终保持高位、接近 dense 模型，在所有 expert 数量下都是如此。第二个实验里，我们把 expert 数量固定为 128，让被激活的 expert 数量 *top_k* 从 1 变到 8。这个实验中，我们还通过相应调整 expert 网络的规模来维持固定的激活参数量。图 3b 显示，随着我们提高网络的稀疏程度（更低的 *top_k*），传统 batching 的吞吐量退化甚至更大，最坏时比我们的 dense 模型慢 86%（相当于慢 7 倍）。而 BTA 无论我们取哪个 *top_k*，都维持高吞吐量。

图 3：BTA 阻止吞吐量随 MoE 模型变得更稀疏而退化。传统 batching（「red」线）出现严重的吞吐量下降（expert 增多时最高 53%，*top_k* 变小时最高 86%），而 BTA（「blue」线）在所有配置下都保持稳定且高位的吞吐量，与 dense 模型相当。

### 把数学摆出来

在上面的章节里，我们主张 GPU 上的 EP 会造成通信瓶颈，而在 Cerebras WSE 上我们面对的是计算利用率挑战。随后我们看到 BTA 如何解决 WSE 上的利用率问题。

现在我们再深入一层：建立一套数学模型，用模型把这些主张形式化，并从中推导出效率预测。我们的工作建立在（Anthony et al.; Korthikanti et al., 2022）所确立的计算框架之上，把它们的分析扩展到我们的 MoE 场景。若无特别说明，我们假设使用混合精度训练（低精度参数副本用 fp16/bf16，高精度参数副本与优化器状态用 fp32）。以下公式中我们略去 bias 项，因为它们可以忽略。下面是本次分析需要的符号记法：

- : 序列长度
- : batch size
- : hidden size
- : attention 中 query head 的数量
- : tile 的数量（在 BTA 中指对 batch 切 tile）
- : 每个 token 被激活的 expert 数量
- : FFN multiplier（在 MoE 层中为 filter size / hidden size）
- : 层数
- : expert 数量
- : 每个模型参数的存储需求（以字节计）

### GPU

我们在上面实验部分用到的 Qwen3-30B-A3B 模型（, , , , ,  带 SwiGLU 非线性）上做分析。首先要弄清楚的是，这个模型能不能装进单张 GPU。假设我们有一张 80GB 内存的 H100 GPU。我们来算一算，仅单个 MoE 层的权重需要多少存储：

在混合精度下，每个参数需要  字节存储。把模型权重及其梯度计入所有  层，就需要大约 116GB 的内存，这还只是最低限度。因此我们无法把这个模型装进单张 H100 GPU，必须启用某种形式的模型并行。虽然存在好几种并行方案，我们的分析聚焦在 EP 上。

在 GPU 上训练 MoE 模型时，某一层所需的内存包括权重、梯度、优化器状态和激活值。权重、梯度与优化器状态合计，每个权重需要  字节存储。把网络里所有 MoE 层都算上，得到需要 464GB 存储。按 Korthikanti et al. (2022)，每个 MoE 层的激活内存量可以这样计算：

对我们这个 batch size 为  、使用  字节存储的 Qwen3-30B-A3B 配置，所有层  加总得到约 8GB 激活内存，于是内存需求升到约 472GB。现在可以看出，训练这个模型我们至少需要 8 张 H100 GPU，并且用 EP 可以在每张 GPU 上放  个 expert。其余所有层，例如 attention 层（K、Q、V 矩阵）、router 以及其他非 MoE 组件，都在每张 GPU 上各存一份副本。

在上面的章节里我们主张 EP 受通信开销拖累。我们来量化一下，在我们这套配置下它到底有多糟。为此，我们计算 MoE 层中计算时间与通信时间之比，看谁占主导。

8 张 H100 GPU，每张提供约 800 peak TFLOPs/s（Bekman, 2023-2024）。假设在 expert MLP 的 GEMM 期间每张 GPU 达到约 500 TFLOPs/s（我们认为这能代表当下常见 MoE 模型中真实的 GEMM 形态），expert 网络会在 **0.08 ms** 内处理完数据。通信成本方面，我们计入 2 个阶段的 all-to-all 操作调用：

按 NVLink 的 350GB/s 带宽（测量细节见附录），并假设每个 token 占用 2 字节存储，这些数据搬运约耗时 **0.77 ms**。换个说法，通信吃掉了 MoE 层总处理时间的 91%。随着我们增加被激活的 expert 数量（带来额外的通信开销）、同时把每个 expert 做得更小（削弱有用的计算并行度），情况还会更糟。

### Cerebras WSE

在 Cerebras WSE 上，我们从不把模型权重直接存放在芯片上。因此，增加 expert 总数并不需要动用 EP 或任何其他形式的模型并行。

但我们撞上的是另一个问题。前面已经表明，随着网络引入更多稀疏性，MoE 模型的吞吐量会退化。这是因为稀疏 MoE 模型把 batch size 切分，使每个 expert 上的有效计算变少，而权重仍要全部载入内存。为了量化这一效应，我们来计算 Qwen3-30B-A3B 模型在不同稀疏度下的算术强度（arithmetic intensity，AI）：

算术强度衡量我们每搬运一字节内存能换来多少次浮点运算。算术强度越低，计算单元就有越多时间在空等内存传输。

把 Qwen3-30B-A3B 的模型配置代入并化简，我们得到 。每个 expert 都会切分 batch size，平均处理  条序列。当引入最低程度的稀疏性（ ，相当于 dense 网络的计算）时，每个 expert 处理的 batch size 同样是 ，其中  是网络其余部分使用的 batch size。然而，当使用最高程度的稀疏性（ ，即每个给定 token 只激活 1 个 expert）时，每个 expert 平均只处理  条序列，仅是原始 batch 的一小部分。在以  条序列这样一个合理的 batch size 下，最高稀疏度相比最低稀疏度会让算术强度几乎低 **88%**。这意味着更稀疏的 MoE 网络变得更受 I/O 制约，严重浪费分配给它们的资源。这就解释了为什么在 Cerebras 硬件上训练时，MoE 模型相比 dense 网络会出现如此大的吞吐量退化（图 3 中的「red」曲线）。BTA 修好了这个问题。我们只需把 expert 的 batch size 做成 expert 数量的函数： 。考虑我们最稀疏的情形 ，在那里观察到算术强度退化最严重。原先每个 expert 只处理  条序列，现在每个 expert 处理  条序列。在  且  的情况下，每个 expert 会处理整个 batch ，这就把 MoE 层的算术强度完全恢复到与最低稀疏度相当的水平。

对不同稀疏度，我们都能找到最合适的  ，确保稀疏性对算术强度、进而对 MoE 层与整个网络的吞吐量影响最小。不过还有一项考量值得讨论。如果我们为了让稀疏 MoE 层受益就持续把 batch size 乘以 G，会给那些受激活内存限制的 attention 层带来麻烦 [2]。按 Korthikanti et al. (2022)，每个 attention 层的激活内存可以这样计算：

其中的二次项  [3] 意味着，把 batch size 乘以  会很快耗尽可用内存。用 BTA，这一点我们也一并处理了。当我们扩大 expert 网络的 batch size 以提升其算术强度时，同时也把 attention 网络的 batch size 按  个分组切 tile。attention 在这  个分组上从不同时产生激活内存，因此降低了它们的存储需求，让它们不那么受激活内存约束。

总结一下，我们的分析正好印证了前面的主张。GPU 上的 EP 造成严重的通信开销，把实际计算比了下去。在 Cerebras WSE 上我们完全绕开了模型并行，但面对另一类挑战：随着稀疏度上升，expert 拿到的 batch size 被切分，导致资源严重利用不足，变成 I/O bound。用 BTA，我们在 Cerebras WSE 上通过解耦 expert 层与 attention 层各自的 batch size 需求解决了这个问题，命中它们各自独特的计算瓶颈。正如图 3（「blue」曲线）所示，BTA 让我们能在 Cerebras 硬件上以 dense 网络的速度训练 MoE 模型。

### 把一切串起来

MoE 模型很难高效训练，尤其当我们走向更高的稀疏度时。高度稀疏的 MoE 模型参数量比 dense 模型多得多。只要几十个 expert，它们就能撞上 GPU 的内存上限（考虑到如今生产级 MoE 模型用的都是数百个 expert，这其实是个很小的数字）。expert 数量更大时，GPU 就需要实现某些模型并行技术才能把所有 expert 载入内存。你必须动用 expert parallelism，把 expert 网络分布到多台设备上，并确保各个 expert 保持负载均衡。

鉴于内存约束在 Cerebras 硬件上不那么致命，我们转而审视更稀疏网络所遇到的计算低效。我们讨论了 BTA 这类技术如何被采用，显著提升 MoE 模型在晶圆上的计算利用率。需要说明的是，BTA 并非银弹，它只是更大优化工具箱里的一项优化技术。我们为 GPU 集群讨论的 expert parallelism，同样可以很好地用在 Cerebras 硬件上：你可以把 expert 分布到多台 WSE 设备上，同时在每台设备上使用 BTA 来维持高计算利用率。

讲到这里就结束了。你现在已经掌握大规模 MoE 训练的完整图景。你理解第 1 篇的基础概念，知道如何从第 2 篇里挑对 routing 方法，能用第 3 篇排查 MoE 训练问题，也看到了如何在现代硬件上解决内存管理与计算利用率问题（无论是在 GPU 上用 EP，还是在 Cerebras WSE 上用 BTA）。在下一篇 [MoE 数学解密：8x7B 到底意味着什么？](https://www.cerebras.ai/blog/moe-guide-calculator) 里，我们把重心从训练转向部署，为你提供实用工具，帮你依据自身约束判断该部署一个 MoE 模型还是继续用 dense 架构。

### 引用

有问题？可以在这里找到我：[https://soboleva-daria.github.io/](https://soboleva-daria.github.io/)

### 脚注

[1] 在 Cerebras 硬件上，我们不使用 FlashAttention，而是在激活张量不再被用到时把它们卸载到内存单元。

[2] 通常网络中所有层都使用  的 batch size，只有 MoE 层会把它切分。

[3] Qwen3-30B-A3B 使用 grouped-query attention（GQA），在多组 query head 之间共享 key 与 value 投影。为简便起见，公式 (6) 保留 multi-head 形式，因为 GQA 并不改变我们在分析中所用的、对  的二次依赖。

### 参考文献

Anthony, Q., Biderman, S., & Schoelkopf, H. (2023). Transformer Math 101. *Eleuther AI Blog*. [https://blog.eleuther.ai/transformer-math/](https://blog.eleuther.ai/transformer-math/)

Bekman, S. (2023-2024). Machine Learning Engineering Open Book. GitHub repository. [https://github.com/stas00/ml-engineering](https://github.com/stas00/ml-engineering)

Cerebras Systems (2023). Training giant neural networks using weight streaming. *White Paper*. [https://www.cerebras.ai](https://www.cerebras.ai/)

Dao, T., Fu, D. Y., Ermon, S., Rudra, A., & Ré, C. (2022). FlashAttention: Fast and memory-efficient exact attention with IO-awareness. *arXiv preprint arXiv:2205.14135*. [https://doi.org/10.48550/arXiv.2205.14135](https://doi.org/10.48550/arXiv.2205.14135)

DeepSeek-AI (2024). DeepSeek-V3 technical report. *arXiv preprint arXiv:2412.19437*. [https://doi.org/10.48550/arXiv.2412.19437](https://doi.org/10.48550/arXiv.2412.19437)

Kimi Team (2025). Kimi K2: Open agentic intelligence. *arXiv preprint arXiv:2507.20534*. [https://doi.org/10.48550/arXiv.2507.20534](https://doi.org/10.48550/arXiv.2507.20534)

Korthikanti, V., Casper, J., Lym, S., McAfee, L., Andersch, M., Shoeybi, M., & Catanzaro, B. (2022). Reducing activation recomputation in large transformer models. *arXiv preprint arXiv:2205.05198*. [https://doi.org/10.48550/arXiv.2205.05198](https://doi.org/10.48550/arXiv.2205.05198)

Krajewski, J., Ludziejewski, J., Adamczewski, K., et al. (2024). Scaling laws for fine-grained mixture of experts. *arXiv preprint arXiv:2402.07871*. [https://doi.org/10.48550/arXiv.2402.07871](https://doi.org/10.48550/arXiv.2402.07871)

Lepikhin, D., Lee, H., Xu, Y., Chen, D., Firat, O., Huang, Y., Krikun, M., Shazeer, N., & Chen, Z. (2020). GShard: Scaling giant models with conditional computation and automatic sharding. *arXiv preprint arXiv:2006.16668*. [https://doi.org/10.48550/arXiv.2006.16668](https://doi.org/10.48550/arXiv.2006.16668)

Qwen Team (2025). Qwen3-30B-A3B technical report. *arXiv preprint arXiv:2505.09388*. [https://doi.org/10.48550/arXiv.2505.09388](https://doi.org/10.48550/arXiv.2505.09388)

Soboleva, D. (2025). Debugging dead MoE models: A step-by-step guide. *Cerebras Blog*. [https://www.cerebras.ai/blog/moe-guide-debug](https://www.cerebras.ai/blog/moe-guide-debug)

Soboleva, D. (2025). MoE fundamentals: Sparse models are the future. *Cerebras Blog*. [https://www.cerebras.ai/blog/moe-guide-why-moe](https://www.cerebras.ai/blog/moe-guide-why-moe)

Soboleva, D. (2025). Router wars: Which MoE routing strategy actually works. *Cerebras Blog*. [https://www.cerebras.ai/blog/moe-guide-router](https://www.cerebras.ai/blog/moe-guide-router)

### 附录

表 1：8×H100 SXM5 节点上的 NCCL all-to-all 总线带宽结果。结果显示带宽在较大消息尺寸下收敛到 350 GB/s。软件环境使用 [nvcr.io/nvidia/pytorch:24.10-py3](https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-24-10.html) docker 容器，被测基准是 nccl-tests 的 all-to-all 带宽。

### MoE 101 指南

页面

### MoE 基础：稀疏模型才是未来

博客

### Router 之争：哪种 MoE routing 策略真正管用

博客

### 调试死掉的 MoE 模型：分步指南

博客

### MoE 数学解密：8x7B 到底意味着什么？

博客
