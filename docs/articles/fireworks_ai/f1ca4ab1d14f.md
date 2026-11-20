---
vendor: fireworks_ai
title: Should you switch your agents to Kimi K3.1 Pro?
original_title: 
url: https://fireworks.ai/blog/should-you-switch-your-agents-to-kimi-k3-1-pro
date: 
lang: zh
captured: 2026-11-20
extractor: readability-v1
translator: mt
status: translated
body_sha: db36d06f62e6
---

[Kimi K3.1 Pro](https://fireworks.ai/models/fireworks/kimi-k3p1-pro) 应该替换为您的代理提供支持的模型，还是与它一起工作？我们使用 [专业智能指数](https://fireworks.ai/specialized-intelligence-index/) (SII) 中从业者构建的基准将其与 [Kimi K3](https://fireworks.ai/models/fireworks/kimi-k3) 和领先替代方案进行比较，检查任务性能、模型成本和执行时间。

K3.1 Pro 在 17 个共享基准测试中的 14 个上得分高于 K3，其进步包括完成更多遗留代码任务以及银行客户支持中更精确的操作。与其他领先模型相比，机会有所不同：它以低得多的模型成本接近 Claude Opus 5.5 的网络研究分数，但其在银行业的更高解析率伴随着更大的支出和更长的等待。

这些差异也创造了结合模型优势的机会。在我们的路由模拟中，在 K3.1 Pro 和 GPT-6 Astra 或 GPT-6.1 Sol 之间分配工作所产生的综合得分比单独使用任一模型更高。与 Opus 搭配使用，模特支出减少了一半以上。这些发现有助于区分在哪些情况下考虑将 K3.1 Pro 作为替代品，以及在哪些情况下为某些任务保留其他型号可能会提供更多价值。

## 我们评估了什么

该研究借鉴了 21 个基准排行榜，将 K3.1 Pro 与其前身和其他模型在质量、模型成本和执行时间（如果有）方面进行了比较。我们在四个方面更仔细地检查了任务结果和代理跟踪：[Sierra 的 τ³-Banking](https://fireworks.ai/specialized-intelligence-index/benchmarks/customer-support/tau3-banking) 用于银行业客户支持，[Epiq 的 CorporateBench](https://fireworks.ai/specialized-intelligence-index/benchmarks/legal/epiq-laer-corporatebench) 用于公司记录和电子邮件，[Rogo 的 Big Finance Benchmark](https://fireworks.ai/specialized-intelligence-index/benchmarks/finance/big-finance-benchmark) 用于金融研究，以及 [Factory’s Legacy-Bench](https://fireworks.ai/specialized-intelligence-index/benchmarks/code-generation/legacy-bench) 用于遗留代码维护。这些任务结果也支持路由模拟。 Letta 和 Surge AI 分别提供了对内存创建和软件工程行为的额外分析。有关评估详细信息，请参阅[方法和限制](https://fireworks.ai/blog/should-you-switch-your-agents-to-kimi-k3-1-pro#methodology-and-limitations)。

## K3.1 Pro 在大多数基准测试中都比 K3 有所改进，但有一些重要的例外

K3.1 Pro 在 17 个共享基准测试中的 14 个上得分高于 K3。任务级分析不仅显示了更多完成的工作和更精确的操作，而且还显示了内存创建和合同审查方面的回归。

![Kimi K3.1 Pro 在 17 个基准测试中的 14 个中比 K3 有所改进](https://cdn.sanity.io/files/pv37i0yn/horizon/e6ed657dc2fe755de4133df959c85deb1158db6f.gif)

### K3.1 Pro 改进的地方

**遗留代码维护。** Factory 的 Legacy-Bench 测试旧语言和环境（包括 COBOL、Fortran 和 Java 7）中的错误修复、功能添加和迁移。K3.1 Pro 完成的任务比 K3 多 15%，在相同的 97 项任务中，完成率为 62.5%，而完成率为 54.3%。模型成本比K3低48%。

**银行业的客户支持。** Sierra 的 τ³-Banking 使用银行政策和账户管理工具来测试代理来解决客户请求。检查的日志显示，K3.1 Pro 更准确地跟踪请求：包含未请求字段的帐户更改工具调用的比例下降了约 69%，从 K3 的 8.5% 下降到 K3.1 Pro 的 2.6%。

一个单独的例子使结果更加具体。在一次涉及客户三张银行卡的对话中，K3 关闭了所有三张银行卡。 K3.1 Pro冻结了卡，检查了交易，只关闭了需要关闭的一张，避免了其他两张不必要的关闭。

### 升级不足的地方

**记忆创建。** [Letta 的 FrontierMemory](https://fireworks.ai/specialized-intelligence-index/benchmarks/rsi/frontiermemory) 测试代理是否可以将先前尝试的记录转化为记忆，以帮助另一个代理解决编码和知识工作任务。协调代理将这些记录分发给工作人员，工作人员提取并保存有用的信息。该基准使用这些记忆来衡量后来的智能体的任务成功率。

使用 K3.1 Pro 创建记忆，基准分数比 K3 低 22%。检查的运行揭示了一个潜在的问题：K3.1 Pro 留下许多未分配给工作人员的源记录。

K3.1 Pro在这个协调作用上不如K3彻底。它仅分配了大约 50-65% 的可用记录，而 K3 在三轮运行中的两次分配了全套记录。对于一项有 22 条记录的任务，K3.1 Pro 在一次运行中仅分配一条记录，而在另一次运行中则不分配任何记录。两次运行都没有产生该任务的记忆，使得后来的特工无法获得这些记录的好处。

**合同审查。** [法律代理基准 (LAB)](https://fireworks.ai/specialized-intelligence-index/benchmarks/legal/lab) 测试第一年法律助理可能在各个执业领域收到的作业。 K3.1 Pro的得分比K3高出18%，从13.1上升到15.4。但在单独的 [LAB：合同](https://fireworks.ai/specialized-intelligence-index/benchmarks/legal/lab-contracts) 基准测试中，该基准测试了合同审查、红线和问题发现，其得分下降了 64%，从 8.3 降至 3.0。对于使用 K3 进行合同审查的团队来说，更广泛的 LAB 改进并不表明他们应该更换。

这些回归反对在整个应用程序中将 K3.1 Pro 视为 K3 的自动替代品，即使其整体基准测试记录更强。

## K3.1 Pro 与领先替代品的比较

### 网络研究：接近 Opus 5.5 的分数，模型成本降低 72%

[并行搜索能力排行榜](https://fireworks.ai/specialized-intelligence-index/benchmarks/web-search/parallel-search-capability-leaderboard) 测试需要网络搜索的难题的模型。 K3.1 Pro 的成本比 Claude Opus 5.5 低 72%（每题 0.27 美元对 0.95 美元），得分低 1.2 分（74.2 比 75.4）。对于使用 Opus 进行大量网络研究的团队来说，这使得 K3.1 Pro 成为减少模型支出的候选者。

![Kimi K3.1 Pro 得分比 Claude Opus 5.5 低 1.2 分，模型成本降低 72%](https://fireworks.ai/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2Fpv37i0yn%2Fhorizon%2F6a279665afa405867c32b580da23fbea84b66a33-1412x1158.png%3Fauto%3Dformat&w=3840&q=75)

### 金融研究：GPT-6.1 Sol 比 K3.1 Pro 得分更高且成本更低

Rogo 的大金融基准衡量模型使用 Rogo 研究工具回答金融分析师问题的准确程度。 K3.1 Pro 与 Claude Opus 5.5 的 48.2% 得分相匹配，模型成本低 81%（每个问题 0.17 美元，而每个问题 0.91 美元）。 GPT-6.1 Sol 得分为 52.0%，每个问题约 0.05 美元，得分更高，而成本比 K3.1 Pro 低约 69%。在这些模型中，Sol 为该工作负载提供了更强的分数和成本组合。

![GPT-6.1 Sol 得分高于 Kimi K3.1 Pro，模型成本降低 69%](https://fireworks.ai/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2Fpv37i0yn%2Fhorizon%2F5a9b93f6efc1809d71afe8d03b213fa6070965a6-1412x1080.png%3Fauto%3Dformat&w=3840&q=75)

### 企业研究：比 Opus 5.5 得分更高，模型成本降低 83%

Epiq 的 CorporateBench 测试代理是否可以从四家综合公司的电子邮件档案中重建公司活动。任务包括识别员工的报告关系、按主题对文档进行分类以及回答需要跨消息连接事实的问题。答案会根据已知的公司记录进行检查，每个公司和能力在标题得分中的权重相同。

![Kimi K3.1 Pro 在得分和成本上优于 Claude Opus 5.5； GPT-6.1 Sol 的性能优于两者](https://fireworks.ai/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2Fpv37i0yn%2Fhorizon%2Fb73ca6a7e6b521cc246e740757c02fa4a2ae5270-1412x1118.png%3Fauto%3Dformat&w=3840&q=75)

K3.1 Pro 的平均得分高于 Claude Opus 5.5，分别为 78.4 和 75.4，而模型成本却低了 83%（每个任务分别为 0.47 美元和 2.80 美元）。 GPT-6.1 Sol 的得分高于两者，为 82.2，每个任务的成本为 0.41 美元。

**员工历史是一个特别的弱点。** 在要求模型重建员工报告关系和角色开始日期的 16 项任务中，K3.1 Pro 的平均分是 78 分（满分 100 分），而 GPT-6 Astra 的得分是 96 分，Sol 的得分是 93 分。在检查的日志中，K3.1 Pro 有时会得出结论，某个员工没有经理，因为没有文件明确指定经理。相反，Astra 根据员工向谁寻求指导等证据来推断关系。

![Kimi K3.1 Pro 在重建员工历史方面落后于 GPT-6 Astra 和 GPT-6.1 Sol](https://fireworks.ai/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2Fpv37i0yn%2Fhorizon%2F607200e06f697b303a654160520bf8e5d6d4dae8-1412x1104.png%3Fauto%3Dformat&w=3840&q=75)

### 银行业客户支持：K3.1 Pro 比 Opus 5.5 解决更多请求，但成本和延迟更高

Sierra 的 τ³-Banking 测试代理是否可以使用银行政策和账户管理工具解决客户请求。 K3.1 Pro 解决的请求比 Claude Opus 5.5 多了 13%，完成了 63.3% 的尝试，而 Claude Opus 5.5 则为 56.0%。

**对困难请求的完成率更高。** 该基准测试包括 12 个对话，20 个评估模型中至少有 15 个在任何运行中都未能解决。在重复的评估运行中，K3.1 Pro 平均解决了 12 个对话中的 5 个对话，而没有其他型号的平均解决次数超过 2 个。

![Kimi K3.1 Pro 比 Claude Opus 5.5 解决了更多的银行请求，每个解决方案的成本高出 89%](https://fireworks.ai/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2Fpv37i0yn%2Fhorizon%2F45836c38fda3dc17e9b41e25933fd4a668e6c4b8-1412x1148.png%3Fauto%3Dformat&w=3840&q=75)

检查的日志显示 K3.1 Pro 更广泛地咨询银行政策，平均每次对话进行 22 次知识库查找，而分析中的其他模型为 10-17 次。这可能有助于解释其在复杂请求上的性能，但日志并不能证明额外的查找导致了完成优势。

**更高的支出和更长的等待时间。** K3.1 Pro 每次对话处理的输入令牌数量大约是 Opus 的三倍，超过了其较低的令牌价格。即使完成率较高，每次成功解决问题的成本为 1.51 美元，而 Opus 的成本为 0.80 美元，高出约 89%。这将模型总支出（包括失败的尝试）除以成功的解决方案。每次尝试的平均执行时间也长两倍多。

对于支持团队来说，如果可以避免成本高昂的人工交接，额外的解决方案可能会证明溢价是合理的，但较长的客户等待可能会排除 K3.1 Pro，因为响应时间要求很严格。

### 软件工程：在 64% 的检查尝试中，已识别的风险未得到解决和报告

编码代理可以完成所请求的更改，同时使其审阅者不知道其已经注意到的问题。 Surge AI 在 K3.1 Pro 的 256 个软件任务中发现了这种模式，每个任务都尝试了三次：在 64% 的尝试中，该模型在其推理中发现了风险，但既没有解决它，也没有在最终响应中提及它。

Surge AI可以检查K3.1 Pro的完整推理，而对比模型仅暴露其书面工作笔记。因此，未报告风险的频率在不同模型之间不能直接比较。

Surge AI 的独立 [sudo L7 基准测试](https://fireworks.ai/specialized-intelligence-index/benchmarks/code-generation/sudo-l7) 评估生产代码库的更改，包括代理随后告诉用户的内容。 K3.1 Pro 的通过率比 K3 高 37%，但仍远远落后于 Claude Opus 5.5 和 Claude Sonnet 5.5：分别为 16.7%、45.6% 和 50.6%。更广泛的行为分析并不能确定未报告的风险对这一结果的影响有多大。

对于评估编码代理的团队来说，最终的响应值得与代码一起仔细审查。审核者需要代理报告其注意到但未修复的后续问题，以便他们可以决定更改是否已准备好交付。

### 事件诊断：K3.1 Pro 找到确切原因的频率低于 GPT-6 Astra

[Traversal 的 ORCA 基准](https://fireworks.ai/specialized-intelligence-index/benchmarks/site-reliability-engineering/traversal-orca-benchmark) 根据日志、跟踪和指标测试生产事件的诊断。 K3.1 Pro 排名第三，但仅在 32.9% 的情况下识别出确切的根本原因，而 Claude Opus 5 为 44.3%（Opus 5.5 未在 ORCA 上进行评估），GPT-6 Astra 为 50.2%。它在排行榜上的位置掩盖了巨大的差距：Astra 在大约一半的情况下找到了根本原因，而 K3.1 Pro 在大约三分之一的情况下找到了根本原因。

## 当您将 K3.1 Pro 与您当前的型号配对时，会发生什么变化？

工作负载比较显示了使用 K3.1 Pro 的原因和保留其他型号的原因。将 K3.1 Pro 与您当前的型号配对是否会比单独使用任一型号有所改善？我们在路由模拟中测试了这个问题。

![在我们的模拟中，将 Kimi K3.1 Pro 与 Claude Opus 5.5 或 GPT-6 Astra 配对可将模型成本降低一半以上：每个模型单独以及与 Kimi K3.1 Pro 配对的综合分数和总模型成本](https://cdn.sanity.io/files/pv37i0yn/horizon/c70aad061c0e6b1019da534b04fcbafd74485244.gif)

### 模拟是如何进行的

我们在相同的 461 项任务中模拟了三个双模型集成，将 K3.1 Pro 分别与 Claude Opus 5.5、GPT-6 Astra 和 GPT-6.1 Sol 配对。路由器选择一个模型来处理每项任务；这些模型没有审查彼此的答案或重试彼此的失败。

基准测试提供了 24 个任务类别。对于每项任务，路由器都会使用其记录的分数和同一类别中其他任务的成本来选择模型。任务本身的结果被排除在该决定之外。

路由器通过为每个得分点分配 20 美元的假设值，平衡基准性能与模型支出。当预期分数提高证明额外成本合理时，它可以选择更昂贵的模型。 20 美元是一个模拟假设，而不是支出限制或衡量的商业价值。

### 每组配对有何变化

对于每个配对，我们将在所有 461 个任务上使用现有模型与将每个任务路由到该模型或 K3.1 Pro 进行比较。

![路由表：Kimi K3.1 Pro 与 Claude Opus 5.5、GPT-6 Astra 或 GPT-6.1 Sol 配对时与单独每个模型的综合得分、模型成本和变化](https://fireworks.ai/_next/image?url=https%3A%2F%2Fcdn.sanity.io%2Fimages%2Fpv37i0yn%2Fhorizon%2F43791d8101108bed863b0348bd0396b06a196275-1412x764.png%3Fauto%3Dformat&w=3840&q=75)

Astra 和 Sol 配对的得分高于任一模型单独的得分。我们对任务集重新采样 2,000 次，并重新计算路由决策，以测试结果在多大程度上取决于所评估的任务。 Astra 的重采样率为 98%，Sol 的重采样率为 89%，这一优势为 Astra 配对的改进提供了更有力的支持。 Opus 配对在 99% 的重新采样中击败了单独的 Opus，并且在所有重新采样中都击败了单独的 Opus，但它仅在 55% 的重新采样中击败了单独的 K3.1 Pro。

### 分数增长和节省从何而来

**企业研究。** 在 Epiq 的 CorporateBench 上，K3.1 Pro-Opus 配对为 K3.1 Pro 分配了 7 个任务类别，并让 Opus 回答有关员工经理和角色开始日期的所有 16 个问题，而 K3.1 Pro 在这方面表现不佳。这些模特的综合得分约为 100 分（满分 128 分），比 Opus 单独得分高出 11 分，同时模特支出从 358 美元减少到 100 美元。阿斯特拉（Astra）配对也出现了同样的分歧，让阿斯特拉（Astra）继续关注员工历史问题。

**银行业的客户支持。** 所有三个配对都将所有 97 个对话分配给 K3.1 Pro。这比单独使用 Opus、Astra 或 Sol 完成了更多的请求。相对于 Opus 和 Sol，它增加了银行业支出，但相对于 Astra 减少了银行支出。

**旧代码维护。** Astra 配对将 97 项任务中的 93 项分配给 K3.1 Pro，其余 4 项任务分配给 Astra。它完成了大约 5 项额外任务，同时削减了约 82% 的模型支出：61 项任务花费 43 美元，而仅使用 Astra 就完成 56 项任务花费 235 美元。

这些结果来自使用记录结果和已知任务类别的模拟。生产路由器需要获取或预测这些类别。重采样分析测量任务样本中的变化，而不是运行之间的变化。该研究也没有测试 K3.1 Pro 是否能为已经在多个模型之间路由的更大整体增加价值。

## 您应该切换到 K3.1 Pro 吗？

当采用 K3.1 Pro 意味着分配有用的工作，而不是到处替换现有模型时，K3.1 Pro 的理由就更充分了。任务级别的研究结果揭示了总体排名所错过的机会：更高的分数伴随着更高的成本，弱点需要保留另一个模型，以及结合它们的优势可以改善结果。这使得采用范围与模型选择同样重要。

[**在 Fireworks 上尝试 K3.1 Pro**](https://app.fireworks.ai/playground?model=accounts/fireworks/models/kimi-k3p1-pro) 根据您的工作负载对其进行评估，或者 [**探索 Fireworks Nexus**](https://fireworks.ai/product/nexus) 在现有编码和协作工具中使用开放式和封闭式模型的集合。

## 方法论和局限性

### 基准覆盖率和评分

结果反映了该研究 2026 年 11 月 9 日的专业智力指数快照。基准覆盖范围、模型名册和评估日期各不相同。分数是在基准内进行比较的，其成功的定义不同。

任务级分析涵盖 Sierra 的 τ³-Banking、Factory 的 Legacy-Bench、Epiq 的 CorporateBench 和 Rogo 的 Big Finance Benchmark。该研究使用了 97 个银行对话、97 个遗留代码任务（3 个任务未能跨所有模型构建，因此未包括在内）、128 个 CorporateBench 问题和 139 个金融研究问题。对于路由分析，每项任务最多为综合得分贡献一分。 CorporateBench 保留其部分信用评级：0.75 分贡献 0.75 分。综合分数是评估运行期间平均任务分数的总和。

### 评估运行和行为分析

[更新的 K3.1 Pro 结果](https://fireworks.ai/blog/kimi-k3-1-pro-fireworks) 包括银行业、Legacy-Bench 和 CorporateBench 客户支持的 3 次运行，以及 Big Finance 上每个问题的 3 次试验。来自代理日志的行为观察使用选定的早期运行；它们说明了观察到的行为，但并未确定每个分数差异的原因。

Letta 从其设置中提供了内存创建分析，其中协调器将早期任务尝试的记录分发给工作代理，以提取要保存的信息。这些观察结果涉及 K3.1 Pro 作为该工作流程中的协调器的行为，而不是其一般使用内存的能力。

Surge AI 提供了软件工程分析，涵盖了 256 个任务的三轮运行，其中包括 60 任务 sudo L7 集。这种更广泛的分析与 sudo L7 排行榜分数不同。涉及可见推理和最终响应的比较应考虑提供者所公开内容的差异。

### 模型成本和执行时间

K3.1 Pro在Fireworks上运行；比较模型在不同日期运行了其提供商的 API。模型成本反映了每个基准定价和缓存假设下记录的令牌使用情况，包括 K3.1 Pro 的 [Fireworks 标价](https://fireworks.ai/pricing)。它们不包括法官成本以及（如果适用）模拟客户成本。执行时间差异反映了服务条件和评估设置以及模型行为。相似的分数本身并不能建立统计等价性。

### 路由假设

对于每项任务，路由器都会比较模型在其他同类任务中的平均得分和模型成本，将每个得分点的价值定为 20 美元。任务本身的结果被排除在决策之外。当该值从 10 美元变化到 100 美元时，综合分数变化不大，但模型支出发生了重大变化。据报道，使用 20 美元设置可节省 53% 和 65%。模拟使用记录的结果而不是实时流量。

### 不确定性和局限性

路由分析假设基准定义的任务类别可用。我们在每个基准测试中对任务进行了重新采样，并在 2,000 个重新采样中的每个重新采样中重新计算了路由决策，从其路由决策中排除了正在路由的任务的每个副本。

在 98% 和 89% 的重采样中，GPT-6 Astra 和 GPT-6.1 Sol 配对的得分分别高于单独的两个组成模型。对于 Claude Opus 5.5 配对，90% 区间比单独的 K3.1 Pro 低 7 个点到高 8 个点。相对于单独的 Opus 而言，其成本节省仍然可靠。

每个任务的得分都保持在运行期间的平均值，因此此检查测量任务样本中的变化，而不是运行之间的变化。综合分数四舍五入为整数。此检查不会验证生产流量上的请求分类或路由。

- [模型发布](https://fireworks.ai/blog?blogTypes=Model%20release)
- [路由](https://fireworks.ai/blog?topics=Routing)
- [基准测试](https://fireworks.ai/blog?topics=Benchmarks)
