---
vendor: tencent_hunyuan
title: Hyra 2.0：自动化科研的下一步
original_title: 
url: https://hunyuan.tencent.com/research/hyra2
date: 2026-11-02
lang: zh
captured: 2026-11-21
extractor: readability-v1
translator: native
status: translated
body_sha: 70311c3ff68a
---

2026-11-02Hyra Team

# Hyra 2.0：自动化科研的下一步

• 摘要AutoResearch的下半场，从「抽卡刷题」转向「工具升级」。

三个月前，我们发布了 Hyra 1.0[[1]](https://hunyuan.tencent.com/research/hyra2#fn:1)[[1]](https://hunyuan.tencent.com/research/hyra2#fnref:1)腾讯混元，**Hyra 1.0**，面向通用科研问题的自动化研究框架介绍：[https://hy.tencent.com/research/hyra](https://hy.tencent.com/research/hyra)：一套面向通用科研问题的、极简的 agent 循环。发布一周后，在开源模型 Hy3 的驱动下，Hyra 解决了加法组合学中一个悬而未决五十多年的问题：和集与差集的最优指数[[2]](https://hunyuan.tencent.com/research/hyra2#fn:2)[[2]](https://hunyuan.tencent.com/research/hyra2#fnref:2)Haowei Lin 与 Shanda Li，**“Settling the Optimal Exponent Relating Sumsets and Difference Sets”**，关于和集与差集最优指数的论文：[https://arxiv.org/abs/2607.27199](https://arxiv.org/abs/2607.27199)。这是国产开源模型首次全自动解决数学开放问题。

Hyra 1.0 发布 11 天后，OpenAI 公布了下一代模型 Astra 的内部版本在 10 个长期开放问题[[3]](https://hunyuan.tencent.com/research/hyra2#fn:3)[[3]](https://hunyuan.tencent.com/research/hyra2#fnref:3)OpenAI，**“Ten advances in mathematics and theoretical computer science”**，介绍模型在数学与理论计算机科学开放问题上的研究进展：[https://openai.com/index/ten-advances-in-mathematics/](https://openai.com/index/ten-advances-in-mathematics/)上取得的新结果。随后的两个多月里，OpenAI 又宣布给出了 Navier–Stokes 千禧年问题的解答[[4]](https://hunyuan.tencent.com/research/hyra2#fn:4)[[4]](https://hunyuan.tencent.com/research/hyra2#fnref:4)OpenAI，**“On the Navier–Stokes Millennium Prize Problem”**，关于 Navier–Stokes 千禧年问题的研究文章：[https://openai.com/index/navier-stokes-solution/](https://openai.com/index/navier-stokes-solution/)，并公开了 722 篇由内部模型产出的数学手稿[[5]](https://hunyuan.tencent.com/research/hyra2#fn:5)[[5]](https://hunyuan.tencent.com/research/hyra2#fnref:5)OpenAI，**openai/math**，公开数学研究手稿与相关材料的代码仓库：[https://github.com/openai/math](https://github.com/openai/math)。AI自动化科研一路疾驰。

Hyra 1.0 说明：给 AI 一道有明确评判标准的难题，让它循环尝试，就有机会超过已有的最好成绩。过去三个月，社区继续沿着这条路线探索，投入大量 token，在更多难题上取得了新进展。

既然路已走通，我们更想抬头看看前方：自动化科研的下一步是什么？

- 当 AI 已经能攻克许多人类未解的难题，科研的范式将走向何处？
- 怎样让 AI 更经济、更可持续地解决科研问题？
- 目前仍然很多难题无法被 AI 解决，瓶颈在哪里？

三个问题看似各有所指，我们的回答却是同一个：**工具升级**。

近年来，AI4Science经历过几次范式上的革新：以AlphaFold[[6]](https://hunyuan.tencent.com/research/hyra2#fn:6)[[6]](https://hunyuan.tencent.com/research/hyra2#fnref:6)John Jumper 等，**“Highly accurate protein structure prediction with AlphaFold”**，发表于 Nature（2021）的 AlphaFold 论文：[https://www.nature.com/articles/s41586-021-03819-2](https://www.nature.com/articles/s41586-021-03819-2)，AlphaEarth[[7]](https://hunyuan.tencent.com/research/hyra2#fn:7)[[7]](https://hunyuan.tencent.com/research/hyra2#fnref:7)Google DeepMind，**“AlphaEarth Foundations helps map our planet in unprecedented detail”**，AlphaEarth Foundations 的官方介绍：[https://deepmind.google/blog/alphaearth-foundations-helps-map-our-planet-in-unprecedented-detail/](https://deepmind.google/blog/alphaearth-foundations-helps-map-our-planet-in-unprecedented-detail/)，AlphaGeometry[[8]](https://hunyuan.tencent.com/research/hyra2#fn:8)[[8]](https://hunyuan.tencent.com/research/hyra2#fnref:8)Trieu H. Trinh 等，**“Solving olympiad geometry without human demonstrations”**，发表于 Nature（2024）的 AlphaGeometry 论文：[https://www.nature.com/articles/s41586-023-06747-5](https://www.nature.com/articles/s41586-023-06747-5)为代表的面相特定问题的模型或系统；到以AlphaEvolve[[9]](https://hunyuan.tencent.com/research/hyra2#fn:9)[[9]](https://hunyuan.tencent.com/research/hyra2#fnref:9)Google DeepMind，**“AlphaEvolve: A Gemini-powered Coding Agent for Designing Advanced Algorithms”**，官方技术博客：[https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/)，Hyra1.0[[1]](https://hunyuan.tencent.com/research/hyra2#fn:1)等为代表的基于通用模型驱动agent，直接解决科学问题的范式。Hyra2.0希望再向前一步，让通用 agent 参与科学工具与模型的研发和升级，让一次研发的成果在后续研究中被反复使用。

![01-research-paradigm.png#S#R #center](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/210b8ba1/2026110122491024_819c896eb854e0890a93b27b99e198d1.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793544553;2108904553&q-key-time=1793544553;2108904553&q-header-list=&q-url-param-list=&q-signature=465fbb2472e8268c3783263f4d41a7d58c8c510b)

*图 1：从解题到造工具。上方展示研究者研发专用科学模型、通用 agent 直接解决科研问题两种方式；下方展示 Hyra 2.0 的目标：由 agent 研发和升级科学模型、研究工作流与软件工具，让成果被后续研究反复使用。*

## 从答案到工具

风靡社区的刷题抽卡的突破固然可贵，但它的成果，并不会自动提升下一次研究的能力，形成智能复利。

工具则不同。升级一件工具，所有用到它的下游任务都会随之受益。

荀子说：“君子生非异也，善假于物也。”

这里的「物」，即为工具，是能被人类或 agent 反复使用、帮助完成一类任务的方法与系统。按能力的载体，工具大致分为两类：

- 符号化工具将方法显式地表达为代码、规则或流程，例如搜索算法、验证程序、数据处理管线和研究工作流。它们把“如何完成任务”写成可执行的操作或可遵循的步骤，改进这些方法，就能改变工具的能力与效率；
- 参数化工具则通过训练，将从数据与反馈中学到的规律保存在模型参数中，例如用于理解、生成和推理的通用语言模型以及用于蛋白质设计的科学模型。

工具的最大价值在于可复用，agent 调用的工具更好了，动作空间和效率也随之提升，在各种基准测试里的表现和效率也会提升（例如用更好的工具解决一个 Terminal Bench[[10]](https://hunyuan.tencent.com/research/hyra2#fn:10)[[10]](https://hunyuan.tencent.com/research/hyra2#fnref:10)Mike A. Merrill 等，**“Terminal-Bench: Benchmarking Agents on Hard, Realistic Tasks in Command Line Interfaces”**，面向终端环境中真实复杂任务的智能体评测基准：[https://arxiv.org/abs/2601.11868；基准主页：https://www.tbench.ai/](https://arxiv.org/abs/2601.11868%EF%BC%9B%E5%9F%BA%E5%87%86%E4%B8%BB%E9%A1%B5%EF%BC%9Ahttps://www.tbench.ai/) 的任务）。

工具也有高阶与低阶之分。以数学为例：解出一道题，收获的是一个答案；做一套适合解这类题的工作流，或训练一个数学推理更强的模型，就有机会裨益无数题的解决；再往上，是一个能自动训练出这种模型的系统；最高处，则是一个能自动做任何任务的系统（AGI）。

越往上，工具越通用，惠及的任务越多，工具的研发周期更长，研发环境更复杂，研发难度更大。

工具升级已经在逐渐发生。8 月底发布混元 Hy4 preview 时，我们在博客[[11]](https://hunyuan.tencent.com/research/hyra2#fn:11)[[11]](https://hunyuan.tencent.com/research/hyra2#fnref:11)腾讯混元，**Hy4 preview**，正文所引的模型发布博客：[https://hunyuan.tencent.com/research/hy4-preview](https://hunyuan.tencent.com/research/hy4-preview)里展示了 Hyra 与它一同加速分子动力学力场模型；三周后，Anthropic 披露 Claude 在不到四周的时间里加速了 30 多个开源生物分子模型[[12]](https://hunyuan.tencent.com/research/hyra2#fn:12)[[12]](https://hunyuan.tencent.com/research/hyra2#fnref:12)Anthropic，**“How Claude is uplifting biomolecular modeling”**，介绍 Claude 参与生物分子模型加速的官方研究文章：[https://www.anthropic.com/research/claude-uplifts-biomolecular-modeling](https://www.anthropic.com/research/claude-uplifts-biomolecular-modeling)。不过，由于反馈速度快，加速一个现成的模型相对容易。更难的是端到端地做出一个新模型，从设计、实现到部署。Hyra 2.0 想攀登的，正是这级更难的台阶：**成为最会创造工具的系统**。

在递归自我改进（RSI）的语境里，研发大模型，本身就要用到许多工具：训练基础设施、数据合成管线、推理系统。我们希望 Hyra 2.0 参与升级这些工具，帮助训练出更好的下一代 Hy 模型；而下一代 Hy 模型，又可以成为 Hyra 2.0 手里的工具。倘若如此，工具造得越好，造工具的系统就越强；系统越强，下一件工具又能造得更好。

## 为升级工具而生的 Harness

研发工具，对 Harness 提出了不同于解题的要求。训练一个模型，要经历方案设计、代码实现、训练、评估和反复修改，整个过程可能持续数天甚至数周。几个项目同时推进时，还要处理实验等待、资源分配和研究方向的调整。这些工作很难靠一个不断延长的 agent session 来管理。

我们先把 Hyra 2.0 接入团队的实际研发环境：在企业微信里和研究者对齐需求，在计算平台上提交和管理实验，在代码仓库里实现、验证改动，并保存实验过程和产物。涉及较大算力开销和共享知识同步的操作，需要经过相应的人工审批；已经获准的工作则由系统继续推进。

研究工作由 **Overall**、**Mission** 和 **Worker** 三层分工。Overall 与人类研究者沟通，管理项目优先级，协调资源和关键决策。每个 Mission 长期负责一个研究问题，决定研究路线、设计实验、组织 Worker，并对结论负责。哪些假设值得继续投入，哪些结果需要复核，什么时候应该换方向，都需要 Mission 判断。Worker 可以独立读代码、做实验、分析失败原因、提出新想法，也可以质疑 Mission。不同 Worker 可以使用不同模型，提供不同的分析和复核意见。

Mission 可以同时安排方向探索、实验执行和独立复核。任务进入持久化队列后，调度系统根据优先级、依赖关系和资源上限启动 Worker。某项任务在等待训练结果或人工审批时，其他任务仍可继续。agent 也可以设置下一次唤醒时间，在实验完成或到达检查节点后接着工作。

并行研究的进展记录在 Research Board 上，包括想法、实验发现、证据和关键决策。普通进展由其他 agent 异步阅读；必须处理的问题通过消息通知，接收方需要明确回应。这样，Worker 可以连续工作较长时间，Mission 也能查到各条研究路线的进展，不必频繁打断正在进行的工作。

![02-harness.png#S#R #center](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/210b8ba1/2026110122493216_d526226be878245ca7a67551fd81ebcc.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793544575;2108904575&q-key-time=1793544575;2108904575&q-header-list=&q-url-param-list=&q-signature=736fc08a74b40be8904c4545b919851573495dd1)

*图 2：Hyra 2.0 的 Harness。Overall 协调目标与资源，Mission 负责研究路线，Worker 开展探索与实验；持久化队列、协作记录和独立复核支持长期研究。底部分别保存项目状态、agent 记忆与共享知识，并将可复用方法整理为 skill，供后续任务使用。*

Worker 报告完成时，需要附上代码版本、实验结果、日志或原始运行轨迹等证据。Mission 可以查看实际操作记录，检查实验是否支持报告中的结论。需要独立验证时，系统会启动新的 Review Worker，让它先接触原始问题和证据，减少执行者结论带来的影响。复核可能发现错误，也可能发现现有证据只支持一个范围更窄的结论，这些都需要如实保留。

工具研发的周期虽然长，却有不少经验可以复用。一次训练失败中有效的排查方法，可以用于后续训练；数值对齐时建立的验证流程，可以复用于其他模型；复核中发现的缺陷，也可以变成工具链里的自动化检查。单次尝试越昂贵，就越有必要留下这些经验，避免后续项目重复摸索。

为此，Hyra 2.0 将项目状态、agent 的工作记忆和可复用经验分开保存。任务队列和 Research Board 记录项目的协作状态；每个 agent 维护自己的分层记忆，保存当前认识、关键假设、已排除的路线和下一步计划；跨任务可复用的经验则进入共享知识库 Books。

Books 中的记录需要说明做法、理由和适用条件，并附上原始证据。这些经验分为「观察」「已验证」和「约定」：单次实验发现的现象可以作为观察，供后续研究参考；经过独立复现的发现才能成为可靠依据；影响团队行为的约定需要人类确认。新证据出现后，已有记录也会随之修正。

项目复盘时，可迁移的方法还会被整理成 skill。例如，训练模型时积累的经验，已经形成了一套 skill，供后续任务使用。这些 skill 本身也是 Hyra 2.0 造出的工具，会在使用中继续修改和完善。我们所说的持续学习，就包括把研究中摸索出的有效方法保存下来，让后续项目能够直接用上，并继续改进。

## 初步成果

Hyra 2.0 已经完成了一批工具的研发与升级。我们会将相关成果持续公开在 [GitHub 仓库](https://github.com/Tencent-Hunyuan/hyra-results/)，供社区检验和复用。

### HyInv：50 毫秒设计 128 条蛋白质序列

HyInv 和下面介绍的 HyPLM，均由 Hyra 2.0 从头训练。它们对应着前文所说的那级台阶：从加速现有模型，走向完整的新模型研发。

HyInv 处理蛋白质设计中的逆折叠问题：给定一个目标骨架，寻找能够折叠成这一结构的蛋白质序列。这是药物设计、酶工程和文库构建中的基础工具。

HyInv 是一个仅有 196 万参数的图神经网络。它的预训练、监督微调、强化学习和推理优化均由 Hyra 2.0 完成。Hyra 2.0 还为它设计了“先起草、再改写”的两步采样方法。

与制药行业常用的 ProteinMPNN[[13]](https://hunyuan.tencent.com/research/hyra2#fn:13)[[13]](https://hunyuan.tencent.com/research/hyra2#fnref:13)Justas Dauparas 等，**“Robust deep learning–based protein sequence design using ProteinMPNN”**，发表于 Science（2022）的 ProteinMPNN 论文：[https://www.science.org/doi/10.1126/science.add2187](https://www.science.org/doi/10.1126/science.add2187) 相比，HyInv 生成的序列与目标结构的吻合程度更好，**生成速度快了 57 倍**。

![03-hyinv-hyplm.png#S#R #center](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/210b8ba1/2026110122495522_7762b0a2f28f902bcdac5742b7dab3d1.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793544598;2108904598&q-key-time=1793544598;2108904598&q-header-list=&q-url-param-list=&q-signature=c43cd91bf4938482c77edb2729e26eb825b6abf0)

*图 3：HyInv 与 HyPLM-Flash 的表现和速度对比。左：横轴为每秒生成的序列数，纵轴为设计质量（scTM）；右：横轴为推理吞吐量（千残基/秒），纵轴为平均归一化评测得分。两图均越靠右上越好；圆点大小表示参数量，分别按对数尺度（左）和线性尺度（右）绘制。*

### HyPLM：从头训练高效的蛋白质语言模型

蛋白质语言模型从序列中学习规律，是判断突变影响、注释蛋白功能和辅助蛋白设计的常用工具。这类模型会被反复调用，训练和推理效率的改进，也就能惠及许多下游任务。

Hyra 2.0 训练的 HyPLM-Flash 有 6.5 亿参数，累计使用 7260 亿训练 token。这一用量是 ESM-2 650M[[14]](https://hunyuan.tencent.com/research/hyra2#fn:14)[[14]](https://hunyuan.tencent.com/research/hyra2#fnref:14)Zeming Lin 等，**“Evolutionary-scale prediction of atomic-level protein structure with a language model”**，发表于 Science（2023）、介绍 ESM-2 的论文：[https://www.science.org/doi/10.1126/science.ade2574](https://www.science.org/doi/10.1126/science.ade2574) 的 0.73 倍，是 E1-600M[[15]](https://hunyuan.tencent.com/research/hyra2#fn:15)[[15]](https://hunyuan.tencent.com/research/hyra2#fnref:15)Profluent，**“E1: Retrieval-Augmented Protein Encoder Models”**，E1 蛋白质编码模型的研究论文：[https://www.biorxiv.org/content/10.1101/2025.11.12.688125v1；包含](https://www.biorxiv.org/content/10.1101/2025.11.12.688125v1%EF%BC%9B%E5%8C%85%E5%90%AB) E1-600M 的官方介绍：[https://www.profluent.bio/showcase/e1](https://www.profluent.bio/showcase/e1) 和 ESM C 600M[[16]](https://hunyuan.tencent.com/research/hyra2#fn:16)[[16]](https://hunyuan.tencent.com/research/hyra2#fnref:16)EvolutionaryScale，**“ESM Cambrian: Revealing the mysteries of proteins with unsupervised learning”**，包含 ESM C 600M 的官方模型介绍：[https://www.evolutionaryscale.ai/blog/esm-cambrian](https://www.evolutionaryscale.ai/blog/esm-cambrian) 的五分之一到八分之一。在比较的 12 个蛋白质语言模型中，HyPLM-Flash 的推理速度最快，**在35个评测任务中平均排名第3**。

HyInv 和 HyPLM 的研发细节将通过技术报告公开，供社区参考和复用。两个模型也可以由 agent 调用，参与药物设计等任务。我们还会继续研发这样的科学模型，全面升级工业制药的现有工具。

### HyFF：面向大规模分子模拟的原子级基础模型

HyFF 是面向分子模拟的原子级基础模型，输入原子的种类和坐标，预测体系的能量与每个原子受到的力，可作为机器学习力场驱动分子动力学模拟。这让研究者能够在原子尺度上追踪分子的运动与反应，为药物设计、酶工程和材料研发提供基础工具。

HyFF 提供五种规模，参数量从 230 万到 12 亿，均在大规模量子化学计算数据上训练，覆盖 83 种元素，支持带电和开壳层体系。每个原子只调用与自身元素对应的子网络，在扩大模型容量的同时控制计算开销。我们将 HyFF 与 16 个公开模型进行了比较。**五个 HyFF 模型全部位于评测的精度–速度帕累托前沿**。HyFF 已用于实际模拟：近 6 万原子的水通道蛋白膜体系模拟了 100 纳秒，可以观察到水分子排成单列、逐个穿过通道；在 4.6 万原子的酶体系中，从选定起点出发，观察到了一次完整的断键、成键反应过程。

![04-hyff.png#S#R #center](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/210b8ba1/2026110122501259_d5b56b48282ba86fc587b0f2a00cdc37.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793544614;2108904614&q-key-time=1793544614;2108904614&q-header-list=&q-url-param-list=&q-signature=5fef04be03a1d6a227efa869e2636991ad699c69)

*图 4：HyFF 与公开模型的精度–速度对比。左为能量预测误差，右为力预测误差；横轴为单步分子动力学模拟耗时，纵轴为平均绝对误差（MAE），越靠左下越好。绿色圆点为五种规模的 HyFF，其他标记为公开对比模型。*

### HyProver：把数学探索组织成可复用的工作流

HyProver 是一套面向纯数学证明的 agent 工作流，保持高 token efficiency 和强探索能力。系统在运行过程中，持续搜索资料、寻找线索、转化问题、提出猜想并产出事实，像真实人类数学家一样，有组织地尝试攻克难题。在尝试潜在路线的过程中，系统并非盲目“摊大饼”，而是会高效地利用 token，通过转化问题来联系不同的数学分支或自主提出中间猜想，沿着 promising 的方向前进。

Hyprover已经完整解决了许多开放数学问题。其中，我们协同数学家已核验并整理好了 **丘成桐先生的圆周作用猜想** 与 **五维 Petty 等距点猜想**[[17]](https://hunyuan.tencent.com/research/hyra2#fn:17)[[17]](https://hunyuan.tencent.com/research/hyra2#fnref:17)C. M. Petty，**“Equilateral Sets in Minkowski Spaces”**，关于 Minkowski 空间等距点集的原始研究，发表于 Proceedings of the American Mathematical Society，29(2): 369–374（1971）：[https://doi.org/10.1090/S0002-9939-1971-0275294-8](https://doi.org/10.1090/S0002-9939-1971-0275294-8) 的证明。

![05-hyprover.png#S #R #center](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/210b8ba1/2026110122502614_d49705067f79e17fadad40358ec1ac1c.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793544629;2108904629&q-key-time=1793544629;2108904629&q-header-list=&q-url-param-list=&q-signature=a142989df957f157405a99b743b6f62e056ffc2c)

*图 5：HyProver 的数学研究工作流。研究 agent 提出中间猜想，证明 Worker 尝试构造证明，再由独立 LLM 在新上下文中复核。待解猜想和通过复核的引理保存在共享研究笔记中，后者可作为后续探索的前提。*

### HyQEC：构造新量子码，严格验证码距

量子纠错需要用多个物理量子比特保护逻辑量子比特。如何降低这笔开销，是量子码研究的核心问题之一。Hyra 2.0 为此研发了 HyQEC：一套面向量子低密度奇偶校验码（qLDPC）的构造与验证系统，支持新码构造、码距搜索和精确码距证明。

在新码构造上， Hyra 2.0 设计了 Split Pauli-CPM 算法，构造并严格验证了量子码 [488,123,22]。其编码效率指标 kd2/n 达到 122.0，在非 CSS、校验权重不超过 8 的条件下，比 qLDPC Challenge[[18]](https://hunyuan.tencent.com/research/hyra2#fn:18)[[18]](https://hunyuan.tencent.com/research/hyra2#fnref:18)Unitary Foundation，**QEC Challenge / qLDPC Challenge**，量子纠错码挑战、排行榜及码距验证的官方项目：[https://github.com/unitaryfoundation/qldpc-challenge](https://github.com/unitaryfoundation/qldpc-challenge) 原榜首**提升约 48%**。系统还构造出多种低开销量子码，刷新了相应参数条件下的已知编码开销纪录。

在码距验证上， HyQEC 配备了 GPU 加速的搜索算法和两套独立的精确证明工具。搜索吞吐量达到原有 8 线程 CPU 工具的 **8–55 倍**。在复核已有结果时，它将原榜首码的码距上界从 95 收紧至 86，并为排行榜 187 个条目中的 178 个完成了精确码距认证。

这套工具既能帮助研究者寻找新码，也能为比较和筛选量子码提供可靠依据。我们后续将发布 HyQEC，供社区使用。

### 灵巧手：自主设计更高效的机器人结构

灵巧手是机器人操作物体的重要工具。传统方法通常先确定机械结构，再训练控制策略；但不同的手指布局和长度，也会影响机器人的操作能力。Hyra 2.0 尝试将探索延伸到机器人本体设计，自主寻找更好的机械结构。

在一项手内物体旋转任务中，Hyra 2.0 自主发现了一种特别的五指设计：五根手指绕着掌心排列，长度从短到长依次递增，像一段旋转楼梯。我们称它为**「旋梯手」**。有趣的是，这只手在初始测试中表现并不突出，旋转速度比论文中的最优设计[[19]](https://hunyuan.tencent.com/research/hyra2#fn:19)[[19]](https://hunyuan.tencent.com/research/hyra2#fnref:19)Kehlani Fay 等，**“House of Dextra: Cross-embodied Co-design for Dexterous Hands”**，发表于 ICLR 2026 的灵巧手结构与控制策略协同设计研究：[https://arxiv.org/abs/2512.03743](https://arxiv.org/abs/2512.03743)慢约 11%。但经过同等预算的策略微调后，它反而实现了反超。

在更严格的 DR5 仿真评测中，旋梯手的旋转速度达到 3.277 rad/s，比同样经过微调的论文最优设计**快 28.6%**，目标完成数提升 21%，失稳率也更低。

这一结果提示我们，初始表现最好的机械结构，不一定拥有最好的训练后性能。尽管目前的结果还局限于仿真环境，尚未经过真机验证，但它展示了让 AI 自主探索机器人结构与控制策略的潜力。我们希望将 Hyra 2.0 的工具研发能力，从软件和模型进一步延伸到物理世界。

![灵巧手结构对比#100%#auto](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/210b8ba1/2026102811035438_af34c413269ee378f8775399526b4526.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793156637;2108516637&q-key-time=1793156637;2108516637&q-header-list=&q-url-param-list=&q-signature=7de04e5d8f516fafde6cf65ea5923366633a91d9)

main_hyra_vs_dextra_v5.mp4

*图 6：Hyra 2.0 自主设计的「旋梯手」与 Dextra 的结构及仿真表现对比。左：与 House of Dextra[[19]](https://hunyuan.tencent.com/research/hyra2#fn:19) 最优五指设计的结构对比；右：与 Dextra Baseline 的物体旋转对比。在 DR5 仿真评测中，经相同预算的策略微调后，Hyra Hand 的平均旋转速度提升 28.6%（3.28 vs. 2.55 rad/s）。*

### 香山：提升处理器性能，补强正确性验证

香山[[20]](https://hunyuan.tencent.com/research/hyra2#fn:20)[[20]](https://hunyuan.tencent.com/research/hyra2#fnref:20)OpenXiangShan，**XiangShan（香山）**，开源高性能 RISC-V 处理器项目：[https://github.com/OpenXiangShan/XiangShan](https://github.com/OpenXiangShan/XiangShan)是一个全流程开源的 RISC-V 处理器项目。Hyra 2.0 围绕它开展了两项工作：性能优化与正确性验证，从而升级该芯片设计工具。

Hyra 2.0 修复了 SPEC CPU2006[[21]](https://hunyuan.tencent.com/research/hyra2#fn:21)[[21]](https://hunyuan.tencent.com/research/hyra2#fnref:21)Standard Performance Evaluation Corporation（SPEC），**SPEC CPU2006**，处理器、内存子系统与编译器性能评测基准的官方说明：[https://www.spec.org/cpu2006/](https://www.spec.org/cpu2006/) 基准测试中暴露的多项问题。结合其他调优，香山每 GHz 得分的几何平均值提升了 **5.79%**，单核频率保持不变，面积增加 0.3%。按照官方性能看板[[22]](https://hunyuan.tencent.com/research/hyra2#fn:22)[[22]](https://hunyuan.tencent.com/research/hyra2#fnref:22)OpenXiangShan，**XiangShan Dashboard**，香山项目的官方性能看板：[https://dashboard.xiangshan.cc/](https://dashboard.xiangshan.cc/)记录的历史迭代速度估算，这一提升大致相当于官方团队 2–3 个月的迭代成果。

Hyra 2.0 新设计的 fuzz 测试发现了 7 个 bug，加上另外 3 个独立发现，**共计 10 个**，均未出现在官方 issue 列表中。它还使用 TLA+[[23]](https://hunyuan.tencent.com/research/hyra2#fn:23)[[23]](https://hunyuan.tencent.com/research/hyra2#fnref:23)Leslie Lamport，**TLA+**，用于描述和验证并发及分布式系统的形式化规约语言；作者主页与工具资料：[https://lamport.azurewebsites.net/tla/tla.html](https://lamport.azurewebsites.net/tla/tla.html) 进行形式化验证，找到了一个多核缓存一致性的反例，相关修复已贡献给开源末级缓存 OpenLLC[[24]](https://hunyuan.tencent.com/research/hyra2#fn:24)[[24]](https://hunyuan.tencent.com/research/hyra2#fnref:24)OpenXiangShan，**OpenLLC**，开源末级缓存项目：[https://github.com/OpenXiangShan/OpenLLC](https://github.com/OpenXiangShan/OpenLLC)。

![07-hyqec-xiangshan.png#S#R #center](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/210b8ba1/2026110122510083_8c6aa28d5a71d07cc8d1e816af49f5c6.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793544663;2108904663&q-key-time=1793544663;2108904663&q-header-list=&q-url-param-list=&q-signature=79f82403baa2903ccc9b9c980d0cf8c7c11c3c55)

*图 7：Hyra 2.0 在量子纠错与处理器研发中的工具升级。左：HyQEC 构造量子低密度奇偶校验码，并通过上下界一致来认证精确码距；右：围绕香山处理器开展性能调优与正确性验证，将发现的问题用于改进设计。*

### 下一代 Hy 模型：走进大模型研发的现场

在混元内部，Hyra 2.0 也正在参与下一代 Hy 模型的升级，例如：

- **预训练：** 优化训练基础设施，参与新训练技术的实验验证，缩短从提出方案到获得实验结果的时间。
- **后训练：** 搭建自动化数据合成管线，让 Hyra 参与高质量训练数据的生成和处理；
- **推理：** 优化实际使用的推理镜像和系统，以降低部署成本，以及训练、评测和大规模实验中的开销。

我们希望让 Hyra 通过改进研发工具，帮助训练出更好的 Hy 模型，再借助更强的模型和更好的工具，完成下一轮工具研发与模型迭代。

## 回到开头的三个问题

**科研会怎样变化？** 我们认为，AI 的贡献会从解出具体问题，延伸到提高一类问题的研究能力。衡量一次研究的成果，除了看它得到了什么答案，也要看它为后续研究留下了什么：一套证明工作流、一个科学模型，或一种可靠的验证方法。工具越通用，能够支持的研究就越多。

**怎样让 AI 做科研更经济、更可持续？** 研发工具本身可能昂贵，但这笔投入可以由后续的许多任务共同分摊。更快的模型减少每次调用的开销，更好的工作流减少重复探索，积累成 skill 的经验则让后续任务少走已经走过的弯路。一次改进的价值，可以在反复使用中不断累积。

**暂时解决不了的问题怎么办？** 先找出限制来自哪里：模型能力不足、搜索效率不够，还是验证和实验反馈太慢？这些具体的限制，可以成为下一轮工具研发的目标。原问题未必立刻有解，但这次探索应尽可能留下可复用的方法和工具，让下一次尝试有更好的起点。

我们希望，**今天的研究成果，能成为明天的研究工具**，加速拓展科学的边界。

脚注

[[1]](https://hunyuan.tencent.com/research/hyra2#fnref:1)腾讯混元，**Hyra 1.0**，面向通用科研问题的自动化研究框架介绍：[https://hy.tencent.com/research/hyra](https://hy.tencent.com/research/hyra)

[[2]](https://hunyuan.tencent.com/research/hyra2#fnref:2)Haowei Lin 与 Shanda Li，**“Settling the Optimal Exponent Relating Sumsets and Difference Sets”**，关于和集与差集最优指数的论文：[https://arxiv.org/abs/2607.27199](https://arxiv.org/abs/2607.27199)

[[3]](https://hunyuan.tencent.com/research/hyra2#fnref:3)OpenAI，**“Ten advances in mathematics and theoretical computer science”**，介绍模型在数学与理论计算机科学开放问题上的研究进展：[https://openai.com/index/ten-advances-in-mathematics/](https://openai.com/index/ten-advances-in-mathematics/)

[[4]](https://hunyuan.tencent.com/research/hyra2#fnref:4)OpenAI，**“On the Navier–Stokes Millennium Prize Problem”**，关于 Navier–Stokes 千禧年问题的研究文章：[https://openai.com/index/navier-stokes-solution/](https://openai.com/index/navier-stokes-solution/)

[[5]](https://hunyuan.tencent.com/research/hyra2#fnref:5)OpenAI，**openai/math**，公开数学研究手稿与相关材料的代码仓库：[https://github.com/openai/math](https://github.com/openai/math)

[[6]](https://hunyuan.tencent.com/research/hyra2#fnref:6)John Jumper 等，**“Highly accurate protein structure prediction with AlphaFold”**，发表于 Nature（2021）的 AlphaFold 论文：[https://www.nature.com/articles/s41586-021-03819-2](https://www.nature.com/articles/s41586-021-03819-2)

[[7]](https://hunyuan.tencent.com/research/hyra2#fnref:7)Google DeepMind，**“AlphaEarth Foundations helps map our planet in unprecedented detail”**，AlphaEarth Foundations 的官方介绍：[https://deepmind.google/blog/alphaearth-foundations-helps-map-our-planet-in-unprecedented-detail/](https://deepmind.google/blog/alphaearth-foundations-helps-map-our-planet-in-unprecedented-detail/)

[[8]](https://hunyuan.tencent.com/research/hyra2#fnref:8)Trieu H. Trinh 等，**“Solving olympiad geometry without human demonstrations”**，发表于 Nature（2024）的 AlphaGeometry 论文：[https://www.nature.com/articles/s41586-023-06747-5](https://www.nature.com/articles/s41586-023-06747-5)

[[9]](https://hunyuan.tencent.com/research/hyra2#fnref:9)Google DeepMind，**“AlphaEvolve: A Gemini-powered Coding Agent for Designing Advanced Algorithms”**，官方技术博客：[https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/)

[[10]](https://hunyuan.tencent.com/research/hyra2#fnref:10)Mike A. Merrill 等，**“Terminal-Bench: Benchmarking Agents on Hard, Realistic Tasks in Command Line Interfaces”**，面向终端环境中真实复杂任务的智能体评测基准：[https://arxiv.org/abs/2601.11868；基准主页：https://www.tbench.ai/](https://arxiv.org/abs/2601.11868%EF%BC%9B%E5%9F%BA%E5%87%86%E4%B8%BB%E9%A1%B5%EF%BC%9Ahttps://www.tbench.ai/)

[[11]](https://hunyuan.tencent.com/research/hyra2#fnref:11)腾讯混元，**Hy4 preview**，正文所引的模型发布博客：[https://hunyuan.tencent.com/research/hy4-preview](https://hunyuan.tencent.com/research/hy4-preview)

[[12]](https://hunyuan.tencent.com/research/hyra2#fnref:12)Anthropic，**“How Claude is uplifting biomolecular modeling”**，介绍 Claude 参与生物分子模型加速的官方研究文章：[https://www.anthropic.com/research/claude-uplifts-biomolecular-modeling](https://www.anthropic.com/research/claude-uplifts-biomolecular-modeling)

[[13]](https://hunyuan.tencent.com/research/hyra2#fnref:13)Justas Dauparas 等，**“Robust deep learning–based protein sequence design using ProteinMPNN”**，发表于 Science（2022）的 ProteinMPNN 论文：[https://www.science.org/doi/10.1126/science.add2187](https://www.science.org/doi/10.1126/science.add2187)

[[14]](https://hunyuan.tencent.com/research/hyra2#fnref:14)Zeming Lin 等，**“Evolutionary-scale prediction of atomic-level protein structure with a language model”**，发表于 Science（2023）、介绍 ESM-2 的论文：[https://www.science.org/doi/10.1126/science.ade2574](https://www.science.org/doi/10.1126/science.ade2574)

[[15]](https://hunyuan.tencent.com/research/hyra2#fnref:15)Profluent，**“E1: Retrieval-Augmented Protein Encoder Models”**，E1 蛋白质编码模型的研究论文：[https://www.biorxiv.org/content/10.1101/2025.11.12.688125v1；包含](https://www.biorxiv.org/content/10.1101/2025.11.12.688125v1%EF%BC%9B%E5%8C%85%E5%90%AB) E1-600M 的官方介绍：[https://www.profluent.bio/showcase/e1](https://www.profluent.bio/showcase/e1)

[[16]](https://hunyuan.tencent.com/research/hyra2#fnref:16)EvolutionaryScale，**“ESM Cambrian: Revealing the mysteries of proteins with unsupervised learning”**，包含 ESM C 600M 的官方模型介绍：[https://www.evolutionaryscale.ai/blog/esm-cambrian](https://www.evolutionaryscale.ai/blog/esm-cambrian)

[[17]](https://hunyuan.tencent.com/research/hyra2#fnref:17)C. M. Petty，**“Equilateral Sets in Minkowski Spaces”**，关于 Minkowski 空间等距点集的原始研究，发表于 Proceedings of the American Mathematical Society，29(2): 369–374（1971）：[https://doi.org/10.1090/S0002-9939-1971-0275294-8](https://doi.org/10.1090/S0002-9939-1971-0275294-8)

[[18]](https://hunyuan.tencent.com/research/hyra2#fnref:18)Unitary Foundation，**QEC Challenge / qLDPC Challenge**，量子纠错码挑战、排行榜及码距验证的官方项目：[https://github.com/unitaryfoundation/qldpc-challenge](https://github.com/unitaryfoundation/qldpc-challenge)

[[19]](https://hunyuan.tencent.com/research/hyra2#fnref:19)Kehlani Fay 等，**“House of Dextra: Cross-embodied Co-design for Dexterous Hands”**，发表于 ICLR 2026 的灵巧手结构与控制策略协同设计研究：[https://arxiv.org/abs/2512.03743](https://arxiv.org/abs/2512.03743)

[[20]](https://hunyuan.tencent.com/research/hyra2#fnref:20)OpenXiangShan，**XiangShan（香山）**，开源高性能 RISC-V 处理器项目：[https://github.com/OpenXiangShan/XiangShan](https://github.com/OpenXiangShan/XiangShan)

[[21]](https://hunyuan.tencent.com/research/hyra2#fnref:21)Standard Performance Evaluation Corporation（SPEC），**SPEC CPU2006**，处理器、内存子系统与编译器性能评测基准的官方说明：[https://www.spec.org/cpu2006/](https://www.spec.org/cpu2006/)

[[22]](https://hunyuan.tencent.com/research/hyra2#fnref:22)OpenXiangShan，**XiangShan Dashboard**，香山项目的官方性能看板：[https://dashboard.xiangshan.cc/](https://dashboard.xiangshan.cc/)

[[23]](https://hunyuan.tencent.com/research/hyra2#fnref:23)Leslie Lamport，**TLA+**，用于描述和验证并发及分布式系统的形式化规约语言；作者主页与工具资料：[https://lamport.azurewebsites.net/tla/tla.html](https://lamport.azurewebsites.net/tla/tla.html)

[[24]](https://hunyuan.tencent.com/research/hyra2#fnref:24)OpenXiangShan，**OpenLLC**，开源末级缓存项目：[https://github.com/OpenXiangShan/OpenLLC](https://github.com/OpenXiangShan/OpenLLC)

目录

[ 从答案到工具]()[ 为升级工具而生的 Harness]()[ 初步成果]()[ HyInv：50 毫秒设计 128 条蛋白质序列]()[ HyPLM：从头训练高效的蛋白质语言模型]()[ HyFF：面向大规模分子模拟的原子级基础模型]()[ HyProver：把数学探索组织成可复用的工作流]()[ HyQEC：构造新量子码，严格验证码距]()[ 灵巧手：自主设计更高效的机器人结构]()[ 香山：提升处理器性能，补强正确性验证]()[ 下一代 Hy 模型：走进大模型研发的现场]()[ 回到开头的三个问题]()

评论（0）

0/2000

### 继续阅读

![Hy4 正式发布](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9a5ea02f/2026110614314011_cb6bad8aa277cf9d40dc98cfa2d4ad3a.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1793946700;2109306700&q-key-time=1793946700;2109306700&q-header-list=&q-url-param-list=&q-signature=f65ce2d45d0e76c67548e865da16f64577b8aefd)

Hy4 正式发布

2026-11-04Hy LLM

![Hy Image3.5 preview 发布：为专业创作提供高性价比模型](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/9c5ca906/2026092121293058_779bc5a05fcb7733e4780de216614118.png?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1789997370;2105357370&q-key-time=1789997370;2105357370&q-header-list=&q-url-param-list=&q-signature=b7bd8e7f50f9549d6ec0470c38ebabbd090eee02)

Hy Image3.5 preview 发布：为专业创作提供高性价比模型

2026-09-22caesarqin

![当大模型强化学习走向规模化，Batch Size Scaling 有什么不一样？](https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/71e4f885/2026091900431240_478a0e952aed78993dfd31c8a980a9b6.jpg?q-sign-algorithm=sha1&q-ak=AKIDRl074nOsGdJ9zjMsCRWP3ShmgS3VtX4S&q-sign-time=1789749793;2105109793&q-key-time=1789749793;2105109793&q-header-list=&q-url-param-list=&q-signature=e080af780914377ed06ad71ebcb5e42c028f0ae8)

当大模型强化学习走向规模化，Batch Size Scaling 有什么不一样？

2026-09-22RL Team
