---
vendor: tencent_hunyuan
title: 当大模型强化学习走向规模化，Batch Size Scaling 有什么不一样？
original_title: 
url: https://hunyuan.tencent.com/research/100116
date: 2026-09-22
lang: zh
captured: 2026-11-21
extractor: readability-v1
translator: native
status: translated
body_sha: 8b8106e806c4
---

2026-09-22RL Team

# 当大模型强化学习走向规模化，Batch Size Scaling 有什么不一样？

• 摘要更大的 batch 让每次更新能够处理更多序列，从而利用更多并行计算资源；但在样本预算固定时，模型可更新的次数也会减少。在强化学习中，什么时候增大 batch 才能缩短达到目标性能所需的实际时间？对于大语言模型，还必须考虑训练轨迹需要在线生成，以及生成与训练对计算资源的需求并不相同。我们建立了一个将达标所需样本数与端到端吞吐量联系起来的分析框架：只有吞吐增益超过额外的样本代价，更大的 batch 才能加速训练。这也给出了一个实用的调参顺序：先找到 batch size 变化后学习效果仍近似不变的范围，再在这个范围内优化吞吐量。GRPO 和 PPO 实验表明，重新调整学习率后，不同 batch 的学习曲线在一定范围内按累计样本数比较时大致对齐。在固定硬件上，增大 batch 使生成吞吐量最高提升 2.29 倍；我们测得的最佳 GRPO 配置在不增加 GPU 的情况下，将达到同一验证目标所需的时间缩短了 29%。

![封面：Batch Size Scaling 需要同时权衡学习效率与系统效率](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/71e4f885/2026090811213134_d0d291b9138b4878d3c3ddb2d3c7e34d.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1788837694;2104197694&q-key-time=1788837694;2104197694&q-header-list=&q-url-param-list=&q-signature=262651f0542e41c3dfd99a3063f076a01ea47f04)

*图 1｜把训练比作登山：山顶代表达到同一目标性能，四条路线代表不同的 Batch Size，每个路标代表一次优化更新。配套调整学习率后，B、2B 和 4B 在累计样本维度上保持近似相同的学习进度；其中更大的 Batch 因吞吐更高而更快“登顶”。但扩大到 16B 后，样本效率损失超过吞吐收益，登顶反而比 B 更慢。图例给出了归一化 time-to-target。*

# 引言

预训练为大语言模型建立了新的能力基线；强化学习则通过在新环境和新任务中的探索与反馈，决定模型还能继续进步多远。DeepSeek-R1 展示了大规模强化学习如何仅使用少量标注数据发展出强大的推理能力。[[1]](https://hunyuan.tencent.com/research/100116#fn:1)[[1]](https://hunyuan.tencent.com/research/100116#fnref:1)DeepSeek, [DeepSeek-R1 Release](https://deepseek.com/en/news/deepseek-r1/), January 20, 2025.  随着 Grok 4 的发布，xAI 进一步扩大了计算规模：据其介绍，Grok 4 使用拥有 200,000 张 GPU 的 Colossus 集群，以预训练规模运行强化学习，所使用的计算量超过此前 RL 工作的一个数量级。[[2]](https://hunyuan.tencent.com/research/100116#fn:2)[[2]](https://hunyuan.tencent.com/research/100116#fnref:2)xAI, [Grok 4: Scaling Up Reinforcement Learning](https://x.ai/news/grok-4), July 9, 2025.  随着强化学习在模型开发中的占比不断提升，其**效率**也会对训练预算产生越来越大的影响。

考虑一个示例预算：假设 10,000 张 GPU 连续运行 30 天，每张 GPU 每小时的成本为 3 美元，那么总成本将达到 **2,160 万美元**。如果在达到相同模型质量的情况下，训练时间缩短 10%，那么按照这一假设，可以节省 **720,000 个 GPU 小时，即 216 万美元**。对于运行自有集群的团队来说，这些节省下来的 GPU 小时也意味着可以用于下一次实验的计算资源。

那么，我们应该从哪里寻找这种收益？一个切入点是每个训练方案都已有的参数：**batch size**。在实践中，batch size 主要涉及两个反复出现的决策：

- **Batch-size tuning：调整训练方案。** 更大的模型或不同类型的加速器，可能会使原有的 batch size 和学习率不再合适。较小的 batch 可能无法充分利用硬件，而不匹配的学习率则可能减慢训练，甚至导致训练不稳定。目标是找到一个合适的 batch size 及其匹配的超参数，使模型能够稳定学习，同时高效利用现有硬件。
- **Batch-size scaling：将并行性转化为更快的学习。** 当同一个模型获得更多 GPU 时，batch 能否随之增大，并更快达到目标？即使不增加 GPU，增大生成 batch 是否也能利用原本闲置的计算容量？

这两个决策最终都指向同一个实际问题：**如何找到一个 batch size，使模型以最短的实际训练时间达到目标性能？**

更大的 batch 既可能成为加速器，也可能成为减速带。在我们的实验中，适度增大的 batch 配合学习率重新调整，可以在提升吞吐量的同时保持学习效率。但当 batch 过大时，额外的样本代价可能超过吞吐增益。图 1 将这种对比描绘成通往同一个山顶的不同路线：更大的 batch 往往有帮助，但并不总能让模型更快达到目标。

**什么科学原理决定了这种从加速到减速的转变？**并且，**能否将其转化为一个可衡量的标准，用于选择使 time-to-target 最短的 batch size？** 为回答这一问题，我们在训练动态与硬件执行的共同约束下分析 batch scaling，从第一性原理重新审视 LLM 强化学习的规模化规律。这需要训练算法与基础设施的协同设计。我们的[论文](https://arxiv.org/abs/2608.29296)构建了由此得到的分析框架。

# 从经典 Batch Scaling 到 LLM 强化学习

> Batch size 可以有效扩大到什么程度？

现代大 Batch 训练最初以工程突破的形式进入人们的视野。2017 年，Goyal 等人使用 256 张 GPU 和 8,192 的 Batch，在一小时内完成了 ResNet-50 在 ImageNet 上的训练，并通过线性放大学习率和渐进式 warmup 保持了小 Batch 的精度。[[3]](https://hunyuan.tencent.com/research/100116#fn:3)[[3]](https://hunyuan.tencent.com/research/100116#fnref:3)Goyal et al. (2017), [Accurate, Large Minibatch SGD: Training ImageNet in 1 Hour](https://arxiv.org/abs/1706.02677). 这一结果表明，配合合适的训练配方，更大的 Batch 可以将硬件并行转化为实际训练时间的大幅缩短。它也让下一个问题变得更加明确：

> 这种 Scaling 在多大范围内仍然有效？

McCandlish 等人（2018）将收益开始递减的转折点与梯度噪声尺度联系起来。[[4]](https://hunyuan.tencent.com/research/100116#fn:4)[[4]](https://hunyuan.tencent.com/research/100116#fnref:4)McCandlish et al. (2018), [An Empirical Model of Large-Batch Training](https://arxiv.org/abs/1812.06162). Shallue 等人（2019）指出，有效的数据并行取决于具体工作负载，而公平比较不同 Batch Size 需要调整超参数。[[5]](https://hunyuan.tencent.com/research/100116#fn:5)[[5]](https://hunyuan.tencent.com/research/100116#fnref:5)Shallue et al. (2019), [Measuring the Effects of Data Parallelism on Neural Network Training](https://arxiv.org/abs/1811.03600). JMLR. 其实际含义很简单：每次更新的样本数翻倍，并不一定能让达到同一目标所需的更新次数减半。

一个密切相关的问题是：改变 batch size 后，能否保持从固定数量样本中获得的学习效果？Hilton、Cobbe 和 Schulman（2022）将这一问题作为**策略优化中的 Batch Size Invariance** 进行研究：调整相关超参数后，不同 Batch Size 应在相同样本数下呈现相近的学习行为。[[6]](https://hunyuan.tencent.com/research/100116#fn:6)[[6]](https://hunyuan.tencent.com/research/100116#fnref:6)Hilton, Cobbe, and Schulman (2022), [Batch Size-Invariance for Policy Optimization](https://arxiv.org/abs/2110.00641). NeurIPS. 这既是有用的 Scaling 直觉，也是公平比较的原则：更多样本通常应带来更强的能力；而在相同累计样本预算下，经过充分调参的不同 Batch Size 应达到近似相同的能力。

> LLM 强化学习带来了什么变化？

在监督学习中，样本已经存在于一个*固定的*数据集中。扩大 Batch 主要改变梯度估计、优化器更新频率和训练并行度；模型不需要自己生成训练样本。LLM 强化学习增加了一个在线闭环。Transformer 模型 首先使用当前策略采样回答或与环境交互，产生轨迹和奖励。这些新生成的数据随后用于前向传播、反向传播和优化器更新；更新后的策略再生成下一批数据。**因此，模型既是生产训练数据的推理系统，也是消费这些数据的学习系统。**

![LLM 采样与训练共享 GPU 计算资源#60%#auto#center](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/71e4f885/2026091516122958_72013eea4c7db8e6a838345f642a499e.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1789459950;2104819950&q-key-time=1789459950;2104819950&q-header-list=&q-url-param-list=&q-signature=2fd9991431691c535c5753f36aaad19c90463bb0)

*图 2. LLM 强化学习将两个 GPU 密集型过程联系起来。采样通过自回归推理生成回答和轨迹；训练则使用这些数据更新模型。Batch Size 同时影响两侧：生成 Batch 决定有多少推理工作可以并发执行，训练 Batch 则决定每次优化器更新使用多少数据。*

两个过程都需要大量 GPU 计算，但使用硬件的方式不同。采样每次生成一个 token，需要反复读取模型权重、维护 KV Cache，并调度并发序列。训练则同时处理多个 token 位置，但需要保存激活、计算梯度并更新优化器状态。正如后文将展示的，这种计算不对称使 Batch Size 对两个阶段产生不同的影响。

# 两种效率，一个分析框架

更快达到目标模型质量，取决于两种效率：

- **样本效率**：衡量模型从每条训练响应中学到了多少。Batch size 及其相关超参数决定了给定样本预算下模型能够取得的进展。
- **系统效率**：衡量完整训练流水线每秒能够处理多少条训练响应，同时考虑生成、模型更新，以及等待或同步所带来的开销。

设 J 表示验证集性能，N 表示累计训练响应数，t 表示经过的时间。沿着学习轨迹的平滑近似，有：

dJdt⏟每秒学习进展=dJdN⏟样本效率×dNdt⏟系统效率.

如果吞吐量翻倍，但每条训练响应带来的学习进展减半，那么两种效果会相互抵消。Batch size 可能同时改变这两个因素，因此我们需要对它们进行联合评估。这个分解为固定硬件条件下的分析提供了概念起点。由于实际学习曲线存在噪声，并且只能在离散检查点上进行评估，我们使用达到目标所需的时间（time-to-target）进行实证比较。

为所有配置设定一个共同的验证目标。令 N⋆ 表示达到该目标所需的训练响应数，令 q 表示在这一时间区间内的平均端到端吞吐量，则：

T=N⋆q.

相对于某个参考配置，定义样本成本比率 rN=N⋆/N0⋆，以及吞吐量比率 rq=q/q0。其中，rN>1 表示新配置需要更多训练响应才能达到目标，即产生了样本代价；rq>1 表示新配置每秒能够处理更多训练响应，即获得了吞吐增益。

### 判据：吞吐增益必须超过样本代价

显然，更大的 batch 只有在 rq>rN 时才能更快完成训练。

举例

假设参考配置需要 100,000 条训练响应，处理速度为每分钟 1,000 条，因此需要 100 分钟才能达到目标。另一种更大的 batch 配置需要 120,000 条训练响应，但处理速度为每分钟 1,500 条。那么：

rN=1.2,rq=1.5,

并且：

TT0=rNrq=1.21.5=0.8.

尽管更大的 batch 样本效率更低，但由于吞吐量提升了 50%，超过了 20% 的样本代价，因此达到目标所需的时间缩短了 20%。如果吞吐量只提升 10%，则有：

1.21.1≈1.09,

这意味着训练时间反而增加约 9%。

这个关系可以从两个互补的角度理解：

- **理论上，要比较吞吐增益与样本代价。** 只有当 rq>rN 时，更大的 batch 才能缩短达到目标所需的时间。
- **实践中，应先建立近似不变性，再优化吞吐量。** 遵循 batch-size invariance 原则，先重新调整依赖 batch size 的超参数，并找出一个范围，使不同配置的学习曲线在相同累计响应数下大致对齐。在这个范围内，rN≈1，因此更高的端到端吞吐量会更直接地转化为更短的 time-to-target。

Takeaway
Batch size 同时影响每条训练响应带来的学习效果和端到端吞吐量。当吞吐增益超过达到相同质量所需额外响应数带来的样本代价时，更大的 batch 才能缩短训练时间。一个更简单的实践准则是：先建立近似的 batch-size invariance，再在这一范围内优化吞吐量。

# 第一步：先保住每条样本的学习效果

第一步的目标是建立（近似的）batch-size invariance。其含义很直接： 将 batch size 翻倍，应该大致将达到相同模型质量所需的优化器更新次数减半，同时使总样本需求基本保持不变。

在分别重新调整依赖 batch size 的超参数之后，一个公平且直观的 scaling 比较应满足以下两个预期：

- 更多样本通常应带来更好的性能。
- 在累计样本数相同的情况下，经过良好调参的不同 batch size 配置应达到大致相同的性能。

遗憾的是，这种性质**不会自动出现**。更大的 batch 会对更多响应的梯度进行平均，但在固定样本预算下，也会减少模型更新的机会。因此，要保持每条响应带来的学习效果，就需要重新调整每次更新推动策略变化的幅度。

**重新调整学习率。** 对于 Adam，我们以平方根规则作为起点：

η(B)=η0BB0.

其中，B0 和 η0 分别表示参考 batch size 和参考学习率。该规则受此前关于自适应优化器 scaling 的分析启发。[[7]](https://hunyuan.tencent.com/research/100116#fn:7)[[7]](https://hunyuan.tencent.com/research/100116#fnref:7)Malladi, Lyu, Panigrahi, and Arora (2022), [On the SDEs and Scaling Rules for Adaptive Gradient Algorithms](https://arxiv.org/abs/2205.10287). NeurIPS. 在实验中，我们固定其他优化器超参数，对这一规则进行实证检验；如果进一步联合调整更多依赖 batch size 的超参数，可能还可以扩大近似不变性的适用范围。

为了保持比较的清晰性，我们使用自研训练基础设施评估 GRPO 和 PPO。两种 workload 都在每个 rollout batch 上执行一次全局优化器更新，不进行 minibatch 切分，也不复用 rollout，从而避免引入 minibatch size 和优化 epoch 等额外调参维度。由于训练过程具有随机性，评估结果也存在噪声，我们预期 batch-size invariance 在实际学习曲线上表现为近似对齐，而不是完全重合。

### 发现一：近似不变性在相当大的范围内成立，但最终会失效

**GRPO：** 这些实验使用 Qwen3-30B-A3B-Instruct-2507，数据来自经过筛选的 DAPO-MATH-17K 子集，每个 prompt 对应 G=8 条响应。我们使用 AIME 2024 和 2025 的 mean@32 平均结果进行评估。一条训练样本指的是经过过滤、并被用于一次优化器更新的响应；每次更新包含 P 个保留的 prompt group，因此：Btrain=PG。

在重新调整学习率之后，随着 prompt batch size 扩大 16 倍，GRPO 仍能保持大致对齐的、以样本数为横轴的学习曲线。图 3 左图展示了在测量窗口内从 P=64 到 P=1024 的对齐情况。当 P=2048 和 P=4096 时，在相同样本数下，曲线开始落后于这一曲线族。

![figure2-batch-invariance.png](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/71e4f885/2026090823563361_f3819c4dc54707dc7200e0c9fbafecd3.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1788882995;2104242995&q-key-time=1788882995;2104242995&q-header-list=&q-url-param-list=&q-signature=5cebf9aa20bc3b3a65c9c80916fe9b5ac4fcd6a8)

*图 3：在 group size 固定时，经过重新调参的 GRPO 在一定范围的 prompt batch size 上保持对齐。最大的 batch 开始偏离这一曲线族，同时 actor gradient norm 的下降趋于平缓。灰色的 ±1 个百分点区域仅用于视觉参考。*

图 3 右图从另一个角度展示了这种偏离。在近似不变的范围内，actor gradient norm 大致按照 P−1/2 的规律下降。当 P=2048 和 P=4096 时，这种下降变得更加平缓，并且与左图中学习曲线失去对齐的现象同时出现。这一模式与梯度平均收益递减的解释一致：超过这一范围后，在每次更新中加入更多响应，已经无法有效补偿更新次数减少所带来的影响。

**PPO：** 我们使用内部的混元 policy model 和 value model，每个模型都有 3B active parameters，并在混合数学、科学和逻辑任务的内部数据集上进行训练。评估性能取对应 benchmark 的平均值。在这里，每个 prompt 保留一条响应，因此：G=1,Btrain=P。

![figure5-ppo-invariance.png](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/71e4f885/2026090823570254_72679251353a7e9d1653749f891d862b.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1788883024;2104243024&q-key-time=1788883024;2104243024&q-header-list=&q-url-param-list=&q-signature=80aea6fb3bf747c81413c0c89adc588c455d5070)

*图 4：PPO 中的 batch scaling。左图：验证集性能随累计训练响应数的变化。右图：不同 batch size 下的 actor 和 critic gradient norm。*

图 4 左图显示，当 batch size 从 256 增加到 2048 时，以样本数为横轴的学习曲线大致保持对齐，而 batch size 为 4096 时则落后于这一曲线族。这为以下结论提供了补充证据：在 PPO 中，重新调整学习率可以在一个有界范围内近似保持每条响应带来的学习效果。

右图揭示了 actor 和 critic 之间的差异。随着 batch size 增大，actor gradient norm 逐渐下降，并且在最大 batch size 处下降趋于平缓。相比之下，critic gradient norm 整体上较为平坦，同时具有较大噪声。这些观察表明，actor 和 critic 可能对应不同的有效 batch scale。由于二者的训练目标不同，理解这种差异，以及探究分别调参能否提升效率，是未来值得研究的方向。

### 发现二：以总响应数作为 batch size 的度量单位

在 GRPO 中，我们可以沿两个维度扩大 batch：采样更多 prompt，或为每个 prompt 采样更多响应。由于同一 group 内的响应共享相同的 prompt，并共同参与 group-relative advantage 的计算，这两种方式未必以相同的方式降低方差。那么，当总 response batch 保持不变时，它们是否仍会产生相似的学习行为？

我们比较两组配置。第一组为 (P,G)=(128,8) 和 (64,16)，两者每次更新都包含 1,024 条响应；第二组为 (P,G)=(256,8) 和 (128,16)，两者每次更新都包含 2,048 条响应。图中使用 n 表示 group size，在我们的记号中对应 G。

左图显示，这些配置的学习轨迹总体相似，但曲线并不会在每个 checkpoint 上完全重合。右图展示了更加清晰的对应关系：总 response batch 相同的配置具有相似的 actor gradient norm，而总 batch 更大的配置则持续表现出更小的 gradient norm。综合来看，对于所测试的配置，使用总保留响应数 PG 作为 batch 的度量单位是合理的。

![Clipboard_Screenshot_1789012202.png](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/71e4f885/2026091011534977_8e66a4bd347c404da4e3f880491d113b.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1789012429;2104372429&q-key-time=1789012429;2104372429&q-header-list=&q-url-param-list=&q-signature=609efae6058ac830cff64182399ad38c63dba9ec)

*图 5：GRPO 中的 group size 对比。左图：验证集性能随累计训练响应数的变化。右图：同一训练窗口内的 actor gradient norm。实线对应每次更新 1,024 条响应，虚线对应每次更新 2,048 条响应。蓝色和橙色分别表示 group size 为 8 和 16。*

### 发现三：固定学习率会破坏 batch size 的近似不变性

在实践中，增加 GPU 通常会同时提高数据并行度和 global batch。如果学习率及其他超参数仍按照较小 batch 进行设置，训练过程可能看起来依然稳定，甚至由于梯度噪声更低而显得更加平滑。但在累计响应数相同的情况下，更大的 batch 实际执行的优化器更新次数更少，因此可能无法达到相同的质量。由此可见，训练稳定**并不意味着** batch-size invariance；更大的 batch 可能需要明显更多的响应才能追赶上来。

我们将一个参考配置与两个 P=256 的配置进行比较。参考配置为：P=128,η=10−6。 两个对比配置的 batch size 都为 P=256：其中一个保持学习率不变，另一个按照平方根规则将学习率提高为：2×10−6。 Group size 保持不变。

![Clipboard_Screenshot_1789012475.png](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/71e4f885/2026091011543675_19e6072bf0695bf76cb71eed4cd8bcc4.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1789012479;2104372479&q-key-time=1789012479;2104372479&q-header-list=&q-url-param-list=&q-signature=cdec201de2913526930a518ceae39f1c44d7306d)

*图 6：GRPO 中的学习率控制。左图：参考 batch、采用平方根学习率 scaling 的两倍 batch，以及固定学习率的两倍 batch 的验证集性能随累计训练响应数的变化。右图：以参考配置首次达到目标时的更新次数为基准进行归一化后的优化器更新次数，展示重新调参如何使两倍 batch 更接近理想的更新次数减半。*

左图说明了重新调整学习率的重要性。使用 scaling 后的学习率时，更大的 batch 在相同样本数下总体上能够跟随参考配置的学习曲线。相比之下，保持学习率不变会使训练在大部分过程中明显落后。例如，在约 120K 条响应处，固定学习率配置的得分约为 74%，而参考配置和重新调参后的配置都约为 77%。

右图量化了优化器更新次数的差异。严格的 batch-size invariance 预测：将 batch size 翻倍后，达到相同目标所需的更新次数应减半。采用 scaling 后学习率的配置，其达到目标所需的更新次数约为参考配置首次达到目标时更新次数的 **0.50–0.67 倍**；考虑到当前 checkpoint 的分辨率，这与理想的 **0.50 倍**基本一致。相比之下，固定学习率的配置需要 **0.75–0.83 倍**的更新次数，明显高于理想值。

Takeaway

在我们的 GRPO 和 PPO 实验中，重新调整学习率可以在一个有界的 batch 范围内近似保持每条响应带来的学习效果。在 GRPO 的 group-size 对比中，总 response batch 相同的配置也表现出总体相似的学习轨迹和高度接近的 gradient norm。PPO 同样在一个有界范围内表现出近似不变性，但随着 batch size 增大，actor 和 critic 呈现出明显不同的 gradient-norm scaling。

# 第二步：在固定硬件上提升吞吐量

当每条样本带来的学习效果得到近似保持后，下一个问题就是如何更快地处理这些样本。一个常见方法是增加 GPU，并提高数据并行度。但如果不增加硬件，更大的 batch 能否加速训练？在相同设备上，每次更新处理更多响应，看起来似乎只会使处理时间按比例增加。然而，在 LLM 强化学习中，**生成与训练之间的计算不对称性**提供了一个机会。

- 在自回归解码过程中，每个序列一次生成一个新 token。在并发度较低时，GPU 会反复读取模型权重，只处理相对较少的 token 向量。增加活跃序列数后，更多 token 可以共享这些权重读取，因此响应数的增长速度可能快于生成它们所需时间的增长速度。
- 训练具有不同的执行模式。当响应已经生成后，前向和反向传播会同时处理大量 token 位置，本身已经暴露出较高的并行度。在这种情况下，增大 batch 主要意味着增加工作量。

一个简单的局部模型可以概括这种差异：

tgen(Bgen)≈d0+d1Bgen,ttrain(Btrain)≈γBtrain.

其中，Bgen 表示逻辑 rollout batch 中的响应数，Btrain 表示一次优化器更新实际消耗的保留响应数。我们的实验采用异步的部分 rollout，并满足：

Bgen=2Btrain.

因此，增大 training batch 也会同时增大 generation batch。截距 d0 表示可以在多个响应之间摊销的生成成本：增大 batch 会降低每条响应分摊到的这部分成本，而训练时间则大致与 training batch size 成正比。我们的[论文](https://arxiv.org/abs/2608.29296)通过 roofline 视角进一步解释了这一现象，说明 batching 如何改变 arithmetic intensity，以及执行过程何时受限于内存带宽或计算能力。上面的简化模型概括了生成成本与训练成本之间由此产生的差异。

吞吐增益取决于执行系统如何将更大的 generation batch 转化为更高的活跃解码并发度，同时还受到调度和显存约束的影响。因此，我们使用每秒保留训练响应数来衡量端到端吞吐量，其中包括处理被丢弃响应、执行模型更新以及流水线开销所花费的时间。

### 发现四：在测量范围内，响应收集时间呈次线性增长

图 7 对比了保留训练响应数的增长和响应收集时间的增长，并将二者都归一化到最小 batch。在两种 workload 中，蓝色的响应数柱状条增长得都快于橙色的时间柱状条。二者的比值就是生成阶段的吞吐增益。

![figure6-generation-throughput.png](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/71e4f885/2026090823591270_60acf35352b316010a5c1b457540fc93.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1788883154;2104243154&q-key-time=1788883154;2104243154&q-header-list=&q-url-param-list=&q-signature=c4af122b30ea8a98a786517038ef727d7b8ccdc2) 
*图 7：响应数增加并不一定需要成比例增加收集时间。在固定硬件上，将 batch 增大 4 倍后，PPO 和 GRPO 的生成阶段吞吐量分别提升 2.29 倍和 1.36 倍。*

在 PPO 中，将 training batch 从 256 增大到 1024 后，每次优化器更新收集的响应数增加到原来的 4 倍，而收集时间从 39 秒增加到 68 秒。因此，响应收集吞吐量提升为：468/39=2.29×.

在 GRPO 中，将 P 从 128 增大到 256 后，生成阶段吞吐量提升 1.31 倍；继续增大到 512 后，吞吐量提升 1.36 倍。增量收益较小，说明在这一范围内，可获得的收益已经开始趋于平缓。

Takeaway

生成和训练随 batch size 的 scaling 方式不同：生成过程可以让更多并发序列摊销模型权重读取的成本，而训练时间则大致与 batch size 成正比。当解码过程尚未使硬件达到饱和时，将 generation batch 翻倍通常只会使收集时间增加不到 2 倍，从而即使不增加 GPU，也能提升生成吞吐量。

# 第三步：结合两个 Critical Batch，最小化 Time-to-target

前面的结果揭示了 LLM 强化学习中 batch scaling 的两个不同上限：

- **Critical Generation Batch** 关注系统效率。它表示在模型、解码引擎、响应长度分布和硬件资源分配固定的情况下，生成吞吐量开始接近平台的位置。在这一规模以下，增大 batch 可以提升硬件利用率；超过这一规模后，继续增大 batch 对生成吞吐量的提升就会非常有限。
- **Critical Training Batch** 关注样本效率。它表示在重新调整学习率后，近似 batch-size invariance 所能达到的上限。在这一范围内，更大的 batch 达到给定目标所需的响应数大致不变；超过这一范围后，每次更新中加入更多响应所带来的收益，已经无法完全弥补更新次数减少的影响，因此达到目标所需的样本数会增加。

这两个临界 batch 不一定重合。图 8 展示了它们各自不同的作用，同时显存容量还会对可行的 generation batch 施加独立约束。二者之间的相互作用决定了增大 batch 到什么程度才能缩短训练时间。

![Clipboard_Screenshot_1789019582.png](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/71e4f885/2026091013530224_dda9df2d9372a59a936f2bf8f8536add.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1789019585;2104379585&q-key-time=1789019585;2104379585&q-header-list=&q-url-param-list=&q-signature=1d29eeb9d67a3f026e6a5d7bf7a928d94625162f)

*图 8：两个 Critical Batch。左图：生成吞吐量逐渐接近平台。右图：在较大 batch 导致学习效率下降之前，通过重新调整学习率，每条响应带来的学习效果大致保持不变。两条曲线均为示意图。*

### 从 Critical Batch 到训练时间

这两个上限如何共同决定训练时间？考虑一种 generation batch 和 training batch 同步增大的配置。图 9 展示了生成吞吐量先于学习效率发生下降的情况。在这一示意中，生成吞吐量的平台也会限制端到端吞吐量的进一步提升，从而形成一个接近最优的 training batch 范围。

![Coupled batch scaling#650px#center](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/71e4f885/2026091013191098_eee2e3aee8f67952d5a27f93a44c88b1.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1789017553;2104377553&q-key-time=1789017553;2104377553&q-header-list=&q-url-param-list=&q-signature=678a100caf9733bf8fab5ebbadc0e33ec2d37a27)

*图 9：生成吞吐量先于样本效率发生饱和时的 time-to-target 示意图。星号标记了接近最优平台上最小的 batch。*

这种情况下会出现三种阶段：

- **学习效果保持不变，吞吐量不断提升。** 增大 batch 可以缩短训练时间，因为模型达到目标所需的响应数大致不变，而系统能够更快地处理这些响应。
- **学习效果保持不变，但吞吐量达到平台。** 继续增大 batch 几乎不会带来额外的加速。因此，一系列不同的 batch size 可能实现相近的训练时间。
- **样本代价占据主导。** 当更大的 batch 需要更多响应才能达到目标时，有限的吞吐增益将无法弥补额外的样本代价，训练时间因此增加。

上述顺序也可能相反。如果学习效率先于生成吞吐量达到平台而开始下降，那么只要吞吐增益能够超过额外的样本代价，更大的 batch 仍然可能更快完成训练。

### 实测结果

图 10 将上述分析与我们在固定硬件上的 GRPO 实验联系起来，其中参考配置为 G=8、P=128。

![Clipboard_Screenshot_1789017161.png](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/71e4f885/2026091013124253_737a0bd9bd493c769cf101400160fbe6.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1789017165;2104377165&q-key-time=1789017165;2104377165&q-header-list=&q-url-param-list=&q-signature=81e009c3fbd643046d3603bd4482937431c679b2)

*图 10：不同 prompt batch size 下归一化后的 GRPO 训练时间。蓝色点使用平方根学习率 scaling，橙色对照组保持学习率不变。所有时间均以 P=128 的配置为基准进行归一化。星号标记了测量到的最佳配置。*

重新调整学习率后，将 P 从 128 增大到 512 和 1024，可以将归一化的 time-to-target 降低到 **0.74 倍和 0.71 倍**。当 P=1024 时，所需样本数保持不变，而吞吐量提升了 41%，训练时间从 11.90 小时缩短到 8.42 小时，即在不增加 GPU 的情况下，训练时间减少了 **29%**。

更大的 batch 并不总是有帮助。当 P=2048 和 P=4096 时，所需响应数增加 **60%**，超过了 30% 和 36% 的吞吐增益，使训练时间上升到 **1.23 倍和 1.18 倍**。决定性因素在于：吞吐增益是否足以抵消额外的样本代价。

# 结论

我们的研究成果可以转化为两个实践阶段：

- **对齐每条响应带来的学习效果。** 对每个候选 training batch 重新调整学习率（以及其他超参数），在相同累计响应数下比较学习曲线，并在共同的验证目标处估计样本成本比率 rN。
- **测量系统收益。** 在显存限制内，调整 generation batching 或解码并发度，测量端到端吞吐量 q，并选择能够最大化 q/rN 的可行配置。当系统变化影响学习行为时，重新检查 rN。

![algorithm-two-stage-v2.png]()

# 未来工作

一个有趣的问题是：能否预测有效的 batch 范围，而不是每遇到一种新设置，就通过昂贵的 sweep 重新寻找。要回答这一问题，需要从机制上理解近似 batch-size invariance 为什么会出现、其边界由什么决定，以及它为什么最终会失效。重新调整学习率只是第一步。更完整的 scaling 理论还应解释：相关的、依赖 batch size 的超参数，如何在不同模型、目标函数、任务分布和训练阶段之间迁移。

PPO 的结果进一步表明，即使在同一个训练算法内部，batch size 也可能不具有单一且普适的含义。Actor 和 critic 优化不同的目标，并表现出不同的 gradient-norm scaling 行为，因此它们可能对应不同的 critical training batch。理解这些不同的动态特征，可能会促使我们为两个组件分别设置 batch size、更新计划或调参规则。

在系统层面，我们的观察针对的是自回归 Transformer：逐 token 生成和并行训练对硬件提出了不同的要求。其他架构——包括 state-space、recurrent 或 hybrid 模型——可能会改变这种生成与训练之间的计算不对称性，因此对应不同的 critical batch scale。面向模型和系统进行设计的 RL stack 应该考虑这些差异，并将生成并发度与 optimizer batch 解耦，同时不能忽略由此带来的排队、策略陈旧性和数据新鲜度之间的权衡。

因此，更广泛的目标并不只是调节 batch size，而是建立一种具有预测能力、面向架构的 RL scaling 理解框架，联合解释训练动态、硬件执行，以及二者如何共同决定 time-to-target。

# Citation

bibtex

```
@misc{li2026largerbatches,
  title={When Do Larger Batches Help Scale LLM Reinforcement Learning?},
  author={Ziniu Li and Jinbo Wang and Guanhua Huang and Feiyuan Zhang and Pengbo Li and Alex Chen},
  year={2026},
  eprint={2608.29296},
  archivePrefix={arXiv},
  primaryClass={cs.LG},
  url={https://arxiv.org/abs/2608.29296}
}
```

脚注

[[1]](https://hunyuan.tencent.com/research/100116#fnref:1)DeepSeek, [DeepSeek-R1 Release](https://deepseek.com/en/news/deepseek-r1/), January 20, 2025.

[[2]](https://hunyuan.tencent.com/research/100116#fnref:2)xAI, [Grok 4: Scaling Up Reinforcement Learning](https://x.ai/news/grok-4), July 9, 2025.

[[3]](https://hunyuan.tencent.com/research/100116#fnref:3)Goyal et al. (2017), [Accurate, Large Minibatch SGD: Training ImageNet in 1 Hour](https://arxiv.org/abs/1706.02677).

[[4]](https://hunyuan.tencent.com/research/100116#fnref:4)McCandlish et al. (2018), [An Empirical Model of Large-Batch Training](https://arxiv.org/abs/1812.06162).

[[5]](https://hunyuan.tencent.com/research/100116#fnref:5)Shallue et al. (2019), [Measuring the Effects of Data Parallelism on Neural Network Training](https://arxiv.org/abs/1811.03600). JMLR.

[[6]](https://hunyuan.tencent.com/research/100116#fnref:6)Hilton, Cobbe, and Schulman (2022), [Batch Size-Invariance for Policy Optimization](https://arxiv.org/abs/2110.00641). NeurIPS.

[[7]](https://hunyuan.tencent.com/research/100116#fnref:7)Malladi, Lyu, Panigrahi, and Arora (2022), [On the SDEs and Scaling Rules for Adaptive Gradient Algorithms](https://arxiv.org/abs/2205.10287). NeurIPS.

目录

[ 引言]()[ 从经典 Batch Scaling 到 LLM 强化学习]()[ 两种效率，一个分析框架]()[ 判据：吞吐增益必须超过样本代价]()[ 第一步：先保住每条样本的学习效果]()[ 发现一：近似不变性在相当大的范围内成立，但最终会失效]()[ 发现二：以总响应数作为 batch size 的度量单位]()[ 发现三：固定学习率会破坏 batch size 的近似不变性]()[ 第二步：在固定硬件上提升吞吐量]()[ 发现四：在测量范围内，响应收集时间呈次线性增长]()[ 第三步：结合两个 Critical Batch，最小化 Time-to-target]()[ 从 Critical Batch 到训练时间]()[ 实测结果]()[ 结论]()[ 未来工作]()[ Citation]()

评论（0）

0/2000

### 继续阅读

![Hy Image3.5 preview 发布：为专业创作提供高性价比模型](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9c5ca906/2026092121293058_779bc5a05fcb7733e4780de216614118.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1789997370;2105357370&q-key-time=1789997370;2105357370&q-header-list=&q-url-param-list=&q-signature=b7bd8e7f50f9549d6ec0470c38ebabbd090eee02)

Hy Image3.5 preview 发布：为专业创作提供高性价比模型

2026-09-22caesarqin

![Hy4 preview 发布](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026082914161695_a99d8e4fdac07d233f015c0206772b08.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1787984177;2103344177&q-key-time=1787984177;2103344177&q-header-list=&q-url-param-list=&q-signature=7b9c494dad35e6b11e0b8655c60f51ecf6fde2f3)

Hy4 preview 发布

2026-08-28Hy LLM

![From LR to ELR: A Better Heuristic for Pretraining Dynamics](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/b729e183/2026081311413226_9f51552b11f9d48d1aa47638aceefcfb.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1786592493;2101952493&q-key-time=1786592493;2101952493&q-header-list=&q-url-param-list=&q-signature=d9997db259c95748285b2cf84bb5d1073c27c5b4)

From LR to ELR: A Better Heuristic for Pretraining Dynamics

2026-08-11Pretrain Team
