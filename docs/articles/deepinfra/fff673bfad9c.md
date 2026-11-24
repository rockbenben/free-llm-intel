---
vendor: deepinfra
title: 开放模型为什么在发布数周后才提速
original_title: 
url: https://deepinfra.com/blog/why-open-models-get-faster
date: 2026-10-31
lang: zh
captured: 2026-11-01
extractor: readability-v1
translator: agent
status: translated
body_sha: 8eeed6874601
---

# 开放模型为什么在发布数周后才提速

发布于 2026.10.31，作者 Niklas

![开放模型为什么在发布数周后才提速](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/10/Why-New-Models-Get-Faster.png)

[Qwen3.8-Flash-Next](https://deepinfra.com/Qwen/Qwen3.8-Flash) 于 2026 年 8 月 26 日发布。同一天，SGLang 就宣布了 day-0 支持，这是与 Qwen、NVIDIA 和 AMD 团队一起完成的，并交付了一个专用容器镜像。vLLM 则用自己的专用镜像为该模型提供服务，那时架构支持的相关工作还在合并当中。llama.cpp 是大多数人用来在自有硬件上跑模型的引擎，它在 0.4.0 版本里加入了初步支持，release note 写明优化改进仍待完成。

三个引擎，对“它能跑这个模型吗？”这个问题给出三个不同的回答，而且都在第一周之内给出。每一个都说是。但它们谁都没有说这个模型会跑得快、跑得便宜，或者能跑到该模型设计所针对的上下文长度。后半件事花的时间更长：到 9 月初，社区构建版已经在报告两位数的性能提升，而那些补丁只动了新的 attention indexer，别的一处没碰。

这个规律几乎出现在每一个引入新设计的开放模型上，对任何采购推理的人来说都攸关成本。你在第一周看到的速度和价格只是一个起点。这篇文章解释原因：所谓“发布即支持”到底意味着什么，一个新架构要求引擎做哪些定制工作（以 Qwen3.8-Flash-Next 作为完整示例），哪些提速特性是后来才开启的，以及如果你正在一个刚上线的模型上做开发，该如何围绕这条曲线做规划。

## “发布即支持”意味着什么

当一个提供商说某个模型首日可用，它的意思是权重能加载、架构能跑通一份参考实现、输出的 token 是正确的。对一个引擎此前从未见过的设计来说，这本身就是实打实的成就，也正是它能让你立刻开始测试的原因。

但这并不意味着模型已经按它最终应有的方式在运行。首日的服务化通常会兼有下列情况中的若干种：

- 算子仍以通用 kernel 的形式运行，而后续会出现手工调优、融合过的版本
- speculative decoding 或 multi-token prediction 处于关闭状态
- 因为低精度版本尚未完成校验，仍在用更高精度的 checkpoint
- cache 管理能用，但浪费显存
- 调度器的设置还是为上一代模型调的

把正确性放在第一位有充分理由。一个会给出细微错误答案的快引擎，比慢引擎更糟，所以团队会先对着参考实现跑一致性校验，然后才敢开启任何激进的东西。速度是一层一层到来的，而每一层都必须先被证明是安全的。

## 为什么新架构需要新的引擎代码

推理引擎是围绕“一个 transformer 长什么样”的假设搭建起来的。改变了这些假设的模型，需要的是引擎改动，而不是只换一份配置文件。Qwen3.8-Flash-Next 是一个很好的例证，因为它的改动几乎牵动了服务化栈的每一个部分。

该模型主体有 1,250 亿参数，另外在一张 n-gram embedding 表上还有 510 亿参数，而每个 token 只激活 60 亿参数。它共 48 层：36 层 Gated DeltaNet，把历史压缩成固定大小的 state；12 层 Qwen Sparse Attention，在完整上下文上做精确检索。[MoE 层](https://deepinfra.com/blog/mixture-of-experts-llm-economics-price-drop)把每个 token 路由到 512 个 expert 中的 10 个。Qwen 把它描述为将来支撑 Qwen4 的那套架构的早期预览，就像 Qwen3-Next 预览了 Qwen3.5 一样。

### 引擎从未调度过的混合布局

大多数引擎的内存管理都建立在一条假设上：每个 attention 层都有一个随序列增长的 key-value cache。而在这个模型里，四分之三的层改为保存固定大小的循环 state，只有剩下的四分之一保存会增长的 cache。内存管理器必须按请求同时跟踪这两种 state，还得继续兼容 prefix caching 这类特性（比如 SGLang 的 radix cache）——这些特性是在这种布局出现之前就设计好的。把这件事做错不会让任何东西崩溃，它只会悄悄浪费显存，并降低你能攒进一个 batch 的请求数。

同样是这套布局，让该架构在长上下文下依然便宜。48 层里只有 12 层要保存会增长的 cache，所以正如 SGLang 团队指出的，模型的显存节省来自布局本身，而不是在 sparse attention 层内部丢弃了任何东西。引擎若不仔细利用这一点，就会把省下来的部分再吐回去。

### 必须写成 kernel 的 Sparse Attention indexer

Qwen Sparse Attention 分两个阶段工作。一个轻量级 indexer 给压缩后的上下文块打分（每 4 个 token 平均成 1 个压缩 key），保留最好的 512 个块，并把它们展开成至多 2,051 个 token 位置。随后普通的 sparse attention 只在这批位置上运行，用的是原始未压缩的 key 和 value。

这两个阶段都不存在现成的 kernel。SGLang 为 prefill 打分写了自定义 GPU kernel，为 decode 写了 paged scorer，并根据硬件分发到不同的 attention 后端（在 Blackwell 上走 TensorRT-LLM 的 kernel 路径，其余情况走 packed FlashAttention）。它还把每 4 个 token 的 1 个压缩 index key 存放在一个 paged pool 里，并把未写完那个块的原始 key 保存在一个按请求划分的小 ring 中，由此把 index-cache 开销降低了 80%。

这类工作会占用引擎团队数周时间，也正是因此，vLLM 在这个模型上投入的引擎工作都集中在 sparse attention 层。

### 更宽的残差流

该模型用四条并行分支取代了单条残差流，并由一个动态 gate 决定从每条分支读取多少、写回多少。于是每个 block 外面都需要一次读取操作（称为 Mix）和一次写入操作（称为 Combine）。这些操作在 decode 阶段只涉及少量 token，规模极小，因此主导其耗时的是 launch overhead，而不是计算量。

SGLang 和 NVIDIA 为它们写了 shape-aware 的 kernel，通过 FlashInfer 交付。在 4 个 token 的规模下，融合后的 Mix kernel 把延迟从 12.36 微秒降到 6.03 微秒，拆分式的 Combine kernel 把延迟从 4.17 微秒降到 2.13 微秒。端到端来看，这两处改动相比早先的实现分别把 speculative-decode 的吞吐提升了 7.6% 和 5.5%。单看哪个数字都不算惊人，但一个模型身上总有许多这样的毛刺，而它们会累积起来。

### 一张不属于 GPU 的 510 亿参数表

这张 n-gram embedding 表以 BF16 存放约为 95 GiB，但每个 token 只从里面查 16 行。把整张表都放进 GPU 显存，会浪费掉本可以用来放 cache 的容量。SGLang 把这张表放在 pinned host memory 里，只在一条独立的 CUDA stream 上 gather 需要的那几行，并让这次 gather 与第一个 decoder block 重叠执行。

在 4 张 H200 GPU 上，这让每张 GPU 释放出 23.46 GiB 的权重显存，并把分配到的 KV 容量从 184 万 token 提升到 328 万 token，增幅 78.5%，而它们在所测的各并发档位上观察到的吞吐变化只有 0.07%。更多的 cache 容量意味着每张 GPU 能承载更多并发请求，这直接体现在每个 token 的成本上。

## 后来才开启的提速特性

除了架构方面的工作，还有一批通用提速手段，引擎会在确信输出没有变化之后才把它们打开。它们往往出现在最初的几周里，而不是第一天。

### Multi-Token Prediction 与 speculative decoding

普通的 decode 步骤每完整走一遍模型只产出 1 个 token。speculative decoding 用一个廉价的 drafter 先提出若干个 token，再让完整模型用一趟把它们验证掉。当 drafter 猜得准的时候，你花大约一个 token 的代价就能拿到多个 token。

Qwen3.8-Flash-Next 自带自己的 draft 模块（约 40 亿 MTP 参数），但要把它用好仍然需要引擎支持。SGLang 团队加入了一个叫 IndexShare MTP 的特性：sparse indexer 在长上下文下开销很大，而 draft 步骤只前进几个位置，于是后续步骤复用第一步选出的 indexer 结果。在 4 张 B200 GPU 上配合 NVFP4 checkpoint，他们报告在 batch size 为 1 时达到每秒 540 tokens，平均每个验证步骤的接受长度为 3.3 个 token。

[Google 的 Gemma 4](https://deepinfra.com/blog/gemma-4-pricing-benchmarks-cost-scenarios) 也是同样的故事。该家族在 2026 年 4 月 2 日发布时并没有 speculative decoding 相关资产，Google 直到 5 月 5 日才放出 multi-token prediction drafter，报告最高 3x 提速且输出不变。对一个业界早已充分理解的技法来说，模型的作者自己就花了一个月。

### 更低精度的 checkpoint

更低的精度意味着更小的权重、更少的内存传输和更高的吞吐，但每种新格式都需要自己的量化 checkpoint 和各自的质量校验。就 Qwen3.8-Flash-Next 而言，SGLang 的文档把 BF16、FP8 和 NVFP4 构建列为各自独立的仓库，其中 NVFP4 仅限 Blackwell GPU。提供商很少会在自家评测集上比对过输出之前，就把生产 endpoint 切到新的精度上，所以最便宜的那种格式往往比第一种来得晚。

### Kernel 融合与 shape-aware 分发

上面的 Mix 和 Combine kernel 只是一个更普遍习惯的例子：一旦模型输出正确，工程师就会 profile 它，找出被开销主导的算子，把它们融合或重塑。单处的收益平平，合起来却很可观，而且它们取决于 batch size 和硬件，这就是为什么这些改动能连续落地好几周。

### 调度、批处理与缓存的调优

每个引擎都有一堆设置：一次攒多少请求、如何把 prefill 与 decode 拆开、prefix 缓存保留多久、预留多少内存。为更早的模型选定的默认值，对新模型往往是错的。混合模型尤其会改变这套权衡，因为它们的 state 不像普通 cache 那样增长；所以随着提供商看到真实流量，调优会一直持续下去。

## 本地这一侧的情形

llama.cpp 的开发本身是公开的，所以它让这条生命周期很容易被外界看到。

| **阶段** | **当时有什么** |
| --- | --- |
| 发布那周 | 教程让用户去构建一个挂在 Unsloth 的 pull request 上的未合并分支，因为主线还认不出这个架构 |
| 9 月初 | 支持合入主线（PR #27742），被描述为初步支持，优化仍待完成 |
| 0.4.0 版本 | 为 DeepSeek-V4、GLM 和 Qwen4 实验性架构加入 sparse flash attention 路径（PR #27970） |
| 社区构建版 | 一个专注于 QSA indexer 的 fork 报告生成在 8k 上下文下快 8%、在 32k 下快 35%，prompt 处理在 32k 下快 59%，而零上下文时没有变化 |

最后一行值得细读。增益在长上下文下最大、在短上下文下完全不存在，这就精确地告诉你原始实现慢在哪里：indexer。这个 fork 的改动是 indexer 上的 5 个补丁，没有一个碰过 shader，比如把 cache 表的扫描从“每层一次”改成“每个压缩比一次”。

早期的对比也显示出反方向的差距。一位用户在 9 月初用单张工作站 GPU 做 benchmark，报告在这个模型的长上下文场景下 vLLM 比 llama.cpp 快大约 4 倍，而 llama.cpp 的 multi-token prediction 支持当时还没落地。这只是同一台机器上的一份报告，所以这个比重要粗略看待，但方向与 release note 的说法一致。

## 引擎速度如何变成价格

对托管 API 而言，[服务一个 token 的成本](https://deepinfra.com/blog/inference-economics-ai-costs-at-scale)大致就是一张 GPU 每小时的成本，除以那张 GPU 在那一小时内产出的 token 数。当引擎工作把吞吐抬高，[每个 token 的成本](https://deepinfra.com/blog/pricing-101-token-math-cost-per-completion)就会下降，哪怕硬件账单分毫未变。如果一台节点每小时花费不变却多服务 1.5 倍的 token，每个 token 的成本就下降约三分之一。

上面这些改进里有三项直接作用在这个比值上：

- cache 显存的节省（比如放进 host 内存的下放）让每张 GPU 能容纳更多并发请求
- 更低精度的权重每个 token 搬运的字节更少
- 融合后的 kernel 在开销上浪费的周期更少

speculative decoding 主要改善的是单个请求自身的延迟，而它对成本的影响取决于负载。在 GPU 本来会被闲置的情况下它帮助最大——这正是低 batch size 时的常态；而当硬件已经被大批 batch 占满时，帮助就小得多。

各家提供商把节省传导给用户的节奏并不一致，有些甚至从不重新定价。但底层的成本曲线在移动，而同一款开放模型的提供商彼此之间的竞争压力，会把价格往这条曲线上拉。

## 如何围绕这条曲线做规划

如果你正在评估或基于一个刚发布的模型做开发，有几个习惯能保护你不过早下结论。

- 把第一周的速度和价格当作下限。在 30 天时重跑你的[延迟与吞吐测试](https://deepinfra.com/blog/llm-api-provider-performance-kpis-101)。
- 用你真实的上下文长度来测。正如那个 fork 的结果所示，新架构带来的增益往往集中在长上下文，所以短 prompt 的 benchmark 可能完全测不到它们。
- 问清楚你用的那个 endpoint 上开启了哪些优化，包括 checkpoint 的数值精度，以及 speculative decoding 是否开着。精度变化会影响输出质量，所以要留一份冻结的评测集，在提供商改动服务配置时重跑它。
- 在需要稳定性的地方锁定模型版本，并在提供商宣布服务变更时安排一次复核。
- 保持你的接入层可迁移。一层能在[各提供商之间调度流量](https://deepinfra.com/blog/best-open-source-llm-api-providers)、也能在各模型之间切换的路由层，能让你在不重写的前提下吃到降价。

对自建推理的团队来说，同样的逻辑适用于引擎版本。要做好在第一个月里升级好几次的预期，并且去读 release note，找你那个模型具体需要的特性。

## 注意事项

并不是每个模型、每个用户都能保证变快。speculative decoding 的增益取决于输出有多可预测，而上面那个 3.3 的接受长度只是特定硬件上的一组 benchmark 配置。NVFP4 的那些数字只对 Blackwell GPU 成立。社区 fork 的数字来自一个人的环境，测的是消费级硬件。

Qwen3.8-Flash-Next 本身也是一个实验性预览。它以 Qwen Community License 1.0 发布，而不是 MIT，而 Qwen 自己的说法就是它在预览 Qwen4 架构。预览版会变，而对于最终没有成为主流家族的设计，引擎有时会把它降低优先级。顶着同一家族名称的生产级 Qwen3.8 Flash API，才是多数团队真正会基于它构建的版本。

最后，早期性能数据有一部分来自引擎团队自己，而他们完全有理由把自己的工作展示得漂亮一些。独立测量结果一旦出现，价值更高。

## 结论

一个模型的发布日，只是它服务化故事的开端。新架构出现的速度，快过推理引擎为它做优化的速度，所以第一版支持是按“正确”做出来的，快的版本随后才到。Qwen3.8-Flash-Next 让人看到这中间的落差有多少：为一套 sparse attention indexer 写自定义 kernel，为混合布局做全新的内存管理，为更宽的残差流写融合算子，为一张相当于一整个小型语言模型那么大的表做 offload 路径，还要一套能在各 draft 步骤之间复用 index 成果的 speculative decoding 方案。

对采购方来说，实际结论很简单。按一个新模型能做什么来评判它，而它的速度和价格要按时间点来评判，而不是只看某一天。那些在 30 天时重新测量、按自己的上下文长度测试、并保持路由灵活性的团队，会在改进到来时把它们收下，也不会因为第一周看起来慢就否定一个好模型。

相关文章

[![Wan 3.0 集成的最佳 API 提供商](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/10/integration.png)](https://deepinfra.com/blog/best-api-providers-wan-3-0-integration)[Wan 3.0 集成的最佳 API 提供商](https://deepinfra.com/blog/best-api-providers-wan-3-0-integration)<p>Wan3.0 是阿里巴巴的一体化视频生成模型。它接受文本、图像、视频、音频、文档和网页，并能产出最长 30 秒、带同步音频的 1080P 视频。用于生产会带来现实问题。视频任务是异步运行的，参考输入可能很大，而每家提供商暴露的模型功能切片都 [&hellip;]</p>

[![Kimi K2.6 API 基准：延迟、TPS 与成本分析（2026）](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/04/kimi-2.6-api-benchmark.webp)](https://deepinfra.com/blog/kimi-k2-6-api-benchmarks-latency-throughput-cost)[Kimi K2.6 API 基准：延迟、TPS 与成本分析（2026）](https://deepinfra.com/blog/kimi-k2-6-api-benchmarks-latency-throughput-cost)<p>关于 Kimi K2.6 Kimi K2.6 是来自 Moonshot AI 的开源前沿模型，发布于 2026 年 4 月 20 日。它是一个原生多模态 agentic 模型，为长周期编码、自主执行和群体式任务编排而构建。该模型采用 Mixture-of-Experts (MoE) 架构，总参数 1 万亿，每个 token 激活 320 亿参数，使用 [&hellip;]</p>

[![GLM-5.1 定价指南：API 成本对比与分析](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/05/GLM-5.1-provider.png)](https://deepinfra.com/blog/glm-5-1-pricing-guide-provider-comparison)[GLM-5.1 定价指南：API 成本对比与分析](https://deepinfra.com/blog/glm-5-1-pricing-guide-provider-comparison)<p>为 GLM-5.1 选择提供商是一个实实在在的经济决策。在 10 家被 benchmark 的 API 提供商中，混合定价从 $0.74 到 $1.70 per 1M tokens，输出速度从 33.8 到 175.2 t/s，最快的提供商比最慢的快 5.2x。对大规模部署的团队来说，这个差距决定了该模型能否适配一个生产 [&hellip;]</p>

[查看全部](https://deepinfra.com/blog)
