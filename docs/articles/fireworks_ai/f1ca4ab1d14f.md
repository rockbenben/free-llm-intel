---
vendor: fireworks_ai
title: Should you switch your agents to Kimi K3.1 Pro?
original_title: 
url: https://fireworks.ai/blog/should-you-switch-your-agents-to-kimi-k3-1-pro
date: 
lang: zh
captured: 2026-11-21
extractor: readability-v1
translator: agent
status: translated
body_sha: 7bae0b793ec8
---

[Kimi K3.1 Pro](https://fireworks.ai/models/fireworks/kimi-k3p1-pro) 应该取代你 agent 背后的模型，还是与它并肩工作？我们用从业者构建的基准，在 [Specialized Intelligence Index](https://fireworks.ai/specialized-intelligence-index/)（SII）中把它与 [Kimi K3](https://fireworks.ai/models/fireworks/kimi-k3) 以及其他领先方案做了对比，考察任务表现、模型成本和执行时间。

在 17 个共有基准中，K3.1 Pro 有 14 个得分高于 K3，提升之处包括完成更多遗留代码任务，以及在银行客服场景中执行更精确的操作。与其他领先模型相比，机会各不相同：它以低得多的模型成本接近 Claude Opus 5.5 的网络研究得分，但在银行业更高的解决率背后，是更多的支出和更长的等待。

这些差异也带来了组合各家所长的机会。在我们的路由模拟中，把工作分配给 K3.1 Pro 与 GPT-6 Astra 或 GPT-6.1 Sol，综合得分高于任一模型单独使用。与 Opus 搭配时，模型支出减少了一半以上。这些发现有助于分辨：哪些场景可以考虑用 K3.1 Pro 替换，哪些场景保留另一个模型处理部分任务更有价值。

## 我们评估了什么

这项研究基于 21 个基准排行榜，在可得的数据上比较 K3.1 Pro 与其上一代以及其他模型的质量、模型成本和执行时间。我们更细致地考察了其中四项的任务结果与 agent 轨迹：[Sierra 的 τ³-Banking](https://fireworks.ai/specialized-intelligence-index/benchmarks/customer-support/tau3-banking) 对应银行业客户支持，[Epiq 的 CorporateBench](https://fireworks.ai/specialized-intelligence-index/benchmarks/legal/epiq-laer-corporatebench) 对应公司记录与邮件，[Rogo 的 Big Finance Benchmark](https://fireworks.ai/specialized-intelligence-index/benchmarks/finance/big-finance-benchmark) 对应金融研究，[Factory 的 Legacy-Bench](https://fireworks.ai/specialized-intelligence-index/benchmarks/code-generation/legacy-bench) 对应遗留代码维护。这些任务结果同样是路由模拟的基础。Letta 与 Surge AI 分别补充了关于记忆创建和软件工程行为的分析。评测细节见[方法与局限](https://fireworks.ai/blog/should-you-switch-your-agents-to-kimi-k3-1-pro#methodology-and-limitations)。

## K3.1 Pro 在多数基准上优于 K3，但也有重要例外

在 17 个共有基准中，K3.1 Pro 有 14 个得分高于 K3。任务级分析显示，它既完成了更多工作、操作也更精确，但在记忆创建和合同审查上出现了退步。

![Kimi K3.1 Pro 在 17 个基准中的 14 个上优于 K3](https://cdn.sanity.io/files/pv37i0yn/horizon/e6ed657dc2fe755de4133df959c85deb1158db6f.gif)

### K3.1 Pro 提升之处

**遗留代码维护。** Factory 的 Legacy-Bench 考察在较老的语言与环境中修 bug、加功能和做迁移，包括 COBOL、Fortran 和 Java 7。在同样的 97 项任务上，K3.1 Pro 比 K3 多完成 15% 的任务，完成率 62.5%，K3 则是 54.3%。模型成本比 K3 低 48%。

**银行业客户支持。** Sierra 的 τ³-Banking 考察 agent 能否使用银行政策与账户管理工具解决客户请求。检查日志显示，K3.1 Pro 更准确地遵循请求：带有未请求字段的账户变更类工具调用占比下降约 69%，从 K3 的 8.5% 降到 K3.1 Pro 的 2.6%。

另一个例子能把后果说得更具体。在一次涉及客户三张银行卡的对话中，K3 把三张卡全部关闭。K3.1 Pro 先冻结卡片、核查交易，只关闭了确实需要关闭的那一张，避免了另外两张被无谓关闭。

### 升级的短板

**记忆创建。** [Letta 的 FrontierMemory](https://fireworks.ai/specialized-intelligence-index/benchmarks/rsi/frontiermemory) 考察 agent 能否把此前的尝试记录转化为记忆，帮助另一个 agent 完成编码和知识工作任务。一个协调 agent 把这些记录分发给若干 worker，由 worker 抽取并保存有用信息。该基准以后续 agent 借助这些记忆完成任务的成功情况作为评分依据。

由 K3.1 Pro 来创建记忆时，基准得分比用 K3 低 22%。查看运行记录可以发现一个可能的成因：K3.1 Pro 留下许多源记录没有分配给 worker。

在这个协调角色上，K3.1 Pro 不如 K3 彻底。它只分配了约 50-65% 的可用记录，而 K3 在三次运行中有两次分配了全部记录。以某个包含 22 条记录的任务为例，K3.1 Pro 在一次运行中只分配了 1 条，另一次一条也没分配。这两次运行都没有为该项任务产出记忆，后续 agent 也就用不上这些记录。

**合同审查。** [Legal Agent Benchmark（LAB）](https://fireworks.ai/specialized-intelligence-index/benchmarks/legal/lab) 考察一名一年级法务助理可能接到的各执业领域任务。K3.1 Pro 得分比 K3 高 18%，从 13.1 升到 15.4。但在另一个专测合同审查、修订标注和问题识别的 [LAB: Contracts](https://fireworks.ai/specialized-intelligence-index/benchmarks/legal/lab-contracts) 基准上，它得分下降 64%，从 8.3 掉到 3.0。对用 K3 做合同审查的团队来说，LAB 总体的提升并不构成换模型的理由。

这些退步说明，即使在整体基准成绩更好的情况下，也不该把 K3.1 Pro 当作整个应用的自动替代品。

## K3.1 Pro 与领先方案相比如何

### 网络研究：模型成本低 72%，得分接近 Opus 5.5

[Parallel Search Capability Leaderboard](https://fireworks.ai/specialized-intelligence-index/benchmarks/web-search/parallel-search-capability-leaderboard) 用需要联网搜索的难题考察模型。K3.1 Pro 的成本比 Claude Opus 5.5 低 72%（每题 $0.27 对 $0.95），得分低 1.2 分（74.2 对 75.4）。对于在高并发网络研究上使用 Opus 的团队，这让 K3.1 Pro 成为降低模型支出的候选。

![Kimi K3.1 Pro 比 Claude Opus 5.5 低 1.2 分，模型成本低 72%](https://fireworks.ai/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2Fpv37i0yn%2Fhorizon%2F6a279665afa405867c32b580da23fbea84b66a33-1412x1158.png%3Fauto%3Dformat&w=3840&q=75)

### 金融研究：GPT-6.1 Sol 比 K3.1 Pro 得分更高、成本更低

Rogo 的 Big Finance Benchmark 衡量模型借助 Rogo 的研究工具回答金融分析师问题时有多准确。K3.1 Pro 以低 81% 的模型成本（每题 $0.17 对 $0.91）达到与 Claude Opus 5.5 相同的 48.2%。GPT-6.1 Sol 得分 52.0%，每题约 $0.05，得分更高，成本还比 K3.1 Pro 低约 69%。在这些模型里，Sol 为这项负载提供了更好的得分与成本组合。

![GPT-6.1 Sol 得分高于 Kimi K3.1 Pro，模型成本低 69%](https://fireworks.ai/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2Fpv37i0yn%2Fhorizon%2F5a9b93f6efc1809d71afe8d03b213fa6070965a6-1412x1080.png%3Fauto%3Dformat&w=3840&q=75)

### 企业研究：得分高于 Opus 5.5，模型成本低 83%

Epiq 的 CorporateBench 考察 agent 能否从四家合成公司的邮件档案中还原公司活动。任务包括判断员工的汇报关系、按主题给文档分类，以及回答需要跨多封邮件串联事实的问题。答案对照已知的公司记录核对，总榜得分中每家公司、每项能力等权。

![Kimi K3.1 Pro 在得分和成本上优于 Claude Opus 5.5；GPT-6.1 Sol 优于两者](https://fireworks.ai/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2Fpv37i0yn%2Fhorizon%2Fb73ca6a7e6b521cc246e740757c02fa4a2ae5270-1412x1118.png%3Fauto%3Dformat&w=3840&q=75)

K3.1 Pro 的平均分高于 Claude Opus 5.5，为 78.4 对 75.4，模型成本低 83%（每项任务 $0.47 对 $2.80）。GPT-6.1 Sol 得分更高，为 82.2，每项任务成本 $0.41。

**员工履历是明显短板。** 在 16 项要求模型还原员工汇报关系与入职日期的任务上，K3.1 Pro 平均 78 分（满分 100），GPT-6 Astra 为 96，Sol 为 93。查看日志可见，K3.1 Pro 有时因为没有文档明确写出上级，就断定该员工没有上级。Astra 则会从证据推断关系，比如这名员工向谁请示工作。

![Kimi K3.1 Pro 在还原员工履历上落后于 GPT-6 Astra 与 GPT-6.1 Sol](https://fireworks.ai/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2Fpv37i0yn%2Fhorizon%2F607200e06f697b303a654160520bf8e5d6d4dae8-1412x1104.png%3Fauto%3Dformat&w=3840&q=75)

### 银行业客户支持：K3.1 Pro 解决的请求多于 Opus 5.5，但成本更高、延迟更长

Sierra 的 τ³-Banking 考察 agent 能否借助银行政策与账户管理工具解决客户请求。K3.1 Pro 解决的请求比 Claude Opus 5.5 多 13%，完成率 63.3% 对 56.0%。

**难题上的完成率更高。** 该基准中有 12 段对话，是 20 个受评模型中至少有 15 个在任何一次运行里都没能解决的。在多次重复评测中，K3.1 Pro 平均解决了这 12 段中的 5 段，而其他模型平均都不超过 2 段。

![Kimi K3.1 Pro 解决的银行请求多于 Claude Opus 5.5，但每次成功解决的成本高 89%](https://fireworks.ai/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2Fpv37i0yn%2Fhorizon%2F45836c38fda3dc17e9b41e25933fd4a668e6c4b8-1412x1148.png%3Fauto%3Dformat&w=3840&q=75)

查看日志可见，K3.1 Pro 查阅银行政策的次数明显更多，平均每段对话查询知识库 22 次，而本次分析中的其他模型为 10-17 次。这或许能解释它在复杂请求上的表现，但日志并不能证明是额外的查询带来了完成率优势。

**支出更高、等待更久。** K3.1 Pro 每段对话处理的输入 token 约为 Opus 的三倍，抵消了它更低的 token 单价。即便完成率更高，它每次成功解决的成本是 $1.51，Opus 是 $0.80，高出约 89%。这里的算法是：包含失败尝试在内的模型总支出，除以成功解决的次数。每次尝试的平均执行时间也长了一倍以上。

对支持团队来说，如果多解决的请求能省下昂贵的人工转接，这笔溢价或许是值得的；但若响应时间要求严格，更长的客户等待时间可能就让 K3.1 Pro 出局。

### 软件工程：在被检查的尝试中，有 64% 的风险被发现却未处理、也未上报

编码 agent 可以完成要求的改动，同时让审查者不知道它其实已经注意到某个问题。Surge AI 在 256 项软件任务上发现了 K3.1 Pro 的这一模式，每项任务尝试三次：有 64% 的尝试中，模型在自己的推理里识别出了风险，但既没有处理，也没有在最终回复里提及。

Surge AI 能查看 K3.1 Pro 的完整推理过程，而用于对比的模型只暴露了书面的工作笔记。因此，未上报风险的频率在不同模型之间不能直接比较。

Surge AI 另一项 [sudo L7 benchmark](https://fireworks.ai/specialized-intelligence-index/benchmarks/code-generation/sudo-l7) 评测对生产代码库的改动，包括 agent 事后向用户交代了什么。K3.1 Pro 的通过率比 K3 高 37%，但仍明显落后于 Claude Opus 5.5 和 Claude Sonnet 5.5：16.7% 对 45.6% 和 50.6%。更宏观的行为分析并不能确定未上报的风险对这个结果贡献了多少。

对评估编码 agent 的团队来说，最终回复值得和代码一起审视。审查者需要 agent 报告它注意到但没有修的重要问题，才能判断这次改动是否可以上线。

### 故障诊断：K3.1 Pro 找准根因的比例低于 GPT-6 Astra

[Traversal 的 ORCA Benchmark](https://fireworks.ai/specialized-intelligence-index/benchmarks/site-reliability-engineering/traversal-orca-benchmark) 考察模型能否根据日志、trace 和指标诊断生产故障。K3.1 Pro 排名第三，但只有 32.9% 的情况找准了确切根因，Claude Opus 5 为 44.3%（ORCA 未评测 Opus 5.5），GPT-6 Astra 为 50.2%。它的榜单位次掩盖了一个不小的差距：Astra 大约一半的情况能定位根因，K3.1 Pro 只有大约三分之一。

## 把 K3.1 Pro 和现有模型搭配，会发生什么变化？

前面的负载对比既给出了使用 K3.1 Pro 的理由，也给出了保留另一个模型的理由。那么把 K3.1 Pro 与现有模型搭配，能否优于任一模型单独使用？我们在一次路由模拟中检验了这个问题。

![在我们的模拟中，Kimi K3.1 Pro 与 Claude Opus 5.5 或 GPT-6 Astra 搭配可让模型成本下降一半以上：各模型单独使用以及与 Kimi K3.1 Pro 搭配时的综合得分与模型总成本](https://cdn.sanity.io/files/pv37i0yn/horizon/c70aad061c0e6b1019da534b04fcbafd74485244.gif)

### 模拟是怎么做的

我们在同样的 461 项任务上模拟了三组双模型组合，让 K3.1 Pro 分别与 Claude Opus 5.5、GPT-6 Astra 和 GPT-6.1 Sol 搭配。由路由器为每项任务选择一个模型；两个模型之间不互相复核答案，也不为对方的失败重试。

这些基准共提供 24 个任务类别。对每项任务，路由器依据两个模型在同一类别其他任务上的历史得分与成本来择一。该任务自身的结果不参与这一决策。

路由器在基准表现与模型支出之间做权衡：它给每个得分点赋予 $20 的假定价值。这样当预期的得分提升足以抵过多花的钱时，它就会选择更贵的模型。$20 只是模拟中的一个假设，既不是支出上限，也不是实测的业务价值。

### 各组合带来的变化

对每一组搭配，我们比较了两种做法：461 项任务全部用原有模型，以及把每项任务分给该模型或 K3.1 Pro。

![路由表：Kimi K3.1 Pro 分别与 Claude Opus 5.5、GPT-6 Astra 或 GPT-6.1 Sol 搭配时的综合得分、模型成本，以及相对单模型的变化](https://fireworks.ai/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2Fpv37i0yn%2Fhorizon%2F43791d8101108bed863b0348bd0396b06a196275-1412x764.png%3Fauto%3Dformat&w=3840&q=75)

Astra 与 Sol 的搭配综合得分高于任一模型单独使用。我们对任务集重采样 2,000 次并重新计算路由决策，以检验这个结果在多大程度上依赖所选任务。Astra 的组合在 98% 的重采样中保持优势，Sol 为 89%，因此 Astra 搭配的提升有更强的支撑。Opus 的搭配在 99% 的重采样中优于 Opus 单独使用，而且在所有重采样里成本都更低，但只有 55% 的情况优于 K3.1 Pro 单独使用。

### 得分增益和节省来自哪里

**企业研究。** 在 Epiq 的 CorporateBench 上，K3.1 Pro-Opus 组合把七个任务类别交给 K3.1 Pro，而关于员工上级与入职日期的全部 16 个问题都留给 Opus——这正是 K3.1 Pro 的弱项。两个模型合计得分约 100（满分 128），比 Opus 单独使用高 11 分，同时把模型支出从 $358 降到 $100。Astra 的组合做了同样的切分，把员工履历类问题留给 Astra。

**银行业客户支持。** 三组搭配都把全部 97 段对话交给 K3.1 Pro。相比 Opus、Astra 或 Sol 单独使用，这解决了更多请求。它让银行业部分的支出相对 Opus 和 Sol 上升，但相对 Astra 下降。

**遗留代码维护。** Astra 的组合把 97 项任务中的 93 项交给 K3.1 Pro，剩下 4 项交给 Astra。它多完成了约 5 项任务，同时把模型支出削减约 82%：61 项任务花 $43，而 Astra 单独使用时 56 项任务要 $235。

这些结果来自基于历史结果和已知任务类别的模拟。生产环境的路由器需要获取或预测这些类别。重采样分析衡量的是任务样本的波动，而不是逐次运行之间的差异。本研究也没有检验 K3.1 Pro 能否为已经在多个模型间路由的更大组合带来增量价值。

## 该不该换到 K3.1 Pro？

当「采用」意味着给它分配有价值的工作，而不是在所有地方替换现有模型时，K3.1 Pro 的理由更充分。任务级发现揭示了总体排名看不到的机会：哪些场景高分伴随高成本，哪些短板值得保留另一个模型，哪些地方把双方长处结合起来效果更好。因此，采用的边界和模型的选择同样重要。

[**在 Fireworks 上试用 K3.1 Pro**](https://app.fireworks.ai/playground?model=accounts/fireworks/models/kimi-k3p1-pro) 在你的负载上评估它，或者[**了解 Fireworks Nexus**](https://fireworks.ai/product/nexus)，在现有的编码与协同工具里使用由开源和闭源模型组成的组合。

## 方法与局限

### 基准覆盖与评分

结果反映的是本研究在 2026 年 11 月 9 日对 Specialized Intelligence Index 的快照。基准覆盖范围、模型名单和评测日期各不相同。得分只在各基准内部比较，而各基准对成功的定义并不相同。

任务级分析覆盖 Sierra 的 τ³-Banking、Factory 的 Legacy-Bench、Epiq 的 CorporateBench 和 Rogo 的 Big Finance Benchmark。研究使用 97 段银行对话、97 项遗留代码任务（有 3 项任务在所有模型上都构建失败，因此未计入）、128 个 CorporateBench 问题和 139 个金融研究问题。在路由分析中，每项任务对综合得分的贡献最多为 1 分。CorporateBench 保留其部分给分的评分方式：得 0.75 分即贡献 0.75 分。综合得分是各任务得分在多次评测运行间取平均后求和。

### 评测运行与行为分析

[更新的 K3.1 Pro 结果](https://fireworks.ai/blog/kimi-k3-1-pro-fireworks) 在银行客户支持、Legacy-Bench 和 CorporateBench 上各含三次运行，Big Finance 上每题三次试验。来自 agent 日志的行为观察使用的是选定的较早运行记录；它们展示观察到的行为，并不构成对每一项得分差异的因果解释。

Letta 提供了记忆创建分析，用的是它自己的设置：由 orchestrator 把此前任务尝试的记录分发给 worker agent，后者抽取信息加以保留。这些观察针对的是 K3.1 Pro 在该流程中作为 orchestrator 的表现，而不是它一般意义上的记忆使用能力。

Surge AI 提供了软件工程分析，覆盖 256 项任务的三次运行，其中包括 60 项任务的 sudo L7 集合。这项更宏观的分析与 sudo L7 榜单得分是两回事。涉及可见推理与最终回复的对比，应当考虑各家厂商暴露内容的差异。

### 模型成本与执行时间

K3.1 Pro 运行在 Fireworks 上；对比模型在不同日期通过各自厂商的 API 运行。模型成本反映的是按各基准的定价与缓存假设记录下来的 token 用量，其中 K3.1 Pro 使用 [Fireworks 定价](https://fireworks.ai/pricing) 中的标价。成本不含评审模型的费用，适用时也不含模拟客户的开销。执行时间的差异既反映服务状态和评测设置，也反映模型行为本身。得分相近本身并不构成统计意义上的等价。

### 路由假设

对每项任务，路由器比较两个模型在同一类型其他任务上的平均得分与模型成本，并把每个得分点估值为 $20。该任务自身的结果不参与决策。当这个估值在 $10 到 $100 之间变动时，综合得分变化很小，但模型支出变化明显。报告中的 53% 和 65% 的节省采用的是 $20 设定。模拟使用的是历史结果，而不是实时流量。

### 不确定性与局限

路由分析假定基准定义的任务类别可以拿到。我们在每个基准内部对任务重采样，并在 2,000 次重采样中每次重新计算路由决策，同时把被路由任务的所有副本从它的路由决策中排除。

GPT-6 Astra 与 GPT-6.1 Sol 的搭配，分别在 98% 和 89% 的重采样中优于各自两个组成模型单独使用。对 Claude Opus 5.5 的搭配，90% 区间从比 K3.1 Pro 单独使用低 7 分到高 8 分。它相对 Opus 单独使用的成本节省则一直可靠。

每项任务的得分取其多次运行的均值，因此这项检查衡量的是任务样本的波动，而不是逐次运行的差异。综合得分四舍五入为整数。这项检查并不能验证生产流量上的请求分类或路由是否成立。

- [模型发布](https://fireworks.ai/blog?blogTypes=Model%20release)
- [路由](https://fireworks.ai/blog?topics=Routing)
- [基准](https://fireworks.ai/blog?topics=Benchmarks)
