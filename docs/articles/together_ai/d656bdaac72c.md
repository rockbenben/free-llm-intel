---
vendor: together_ai
title: DeepSeek-V4 Flash 0731 vs GPT-5.6 Luna on DeepSWE: Cost and Coding
original_title: 
url: https://www.together.ai/blog/deepseek-v4-flash-0731-vs-gpt-5-6-luna-on-deepswe-cost-and-coding
date: 2026-08-06
lang: zh
captured: 2026-10-31
extractor: readability-v1
translator: mt
status: translated
body_sha: 4a1850b2406e
---

所有博客文章

模型库

发布日期：2026 年 8 月 6 日

# DeepSWE 上的 DeepSeek-V4 Flash 0731 与 GPT-5.6 Luna：成本和编码

开放重量模型设定了新的价格情报标准

- 作者扎因·哈桑 (Zain Hasan)、肖比特·迪克西特 (Shobhit Dixit)
- 目录[40+ 型号选择用于生产...40+ 型号选择用于生产...40+ 型号选择用于生产...](https://www.together.ai/blog/deepseek-v4-flash-0731-vs-gpt-5-6-luna-on-deepswe-cost-and-coding)

要点

虽然 GPT-5.6 Luna 在每项质量指标上都是更强大的工程师，但 DeepSeek-V4 Flash 0731 足够便宜，以至于 DeepSeek-first 级联在准确性和成本上都击败了单独的 Luna。

- GPT-5.6 Luna 以 67.2% 和 53.3% 的准确率领先 DeepSWE pass@1，相差 14 分，并且在每次相同的尝试次数中保持领先。
- DeepSeek-V4 Flash 是 DeepSWE 板上最便宜的型号：每次部署 0.10 美元，每次部署 0.61 美元，每 100 美元可解决 532 个问题，而 Luna 为 110 个。
- DeepSeek-V4 Flash 的故障更加干净，在 9% 的故障中打破了存储库现有的测试套件，而 Luna 的故障率为 15%。
- 首先运行 DeepSeek-V4 Flash，仅在失败时升级到 Luna，以每项 0.385 美元的价格解决了 78.9% 的任务：比单独使用 Luna 更准确，并且便宜 37%。

现已上市·开放重量

在 Together AI 上运行 DeepSeek-V4 Flash

DeepSWE 板上最便宜的模型，大约十美分一个任务。以生产规模提供廉价的第一阶段服务，无需前沿代币价格。

打开游乐场

[DeepSeek-V4 Flash 0731](https://www.together.ai/models/deepseek-v4-flash-0731) 是整个 DeepSWE 板上最便宜的模型：大约十美分一个任务！ GPT-5.6 Luna 是一款可靠的高端旗舰产品，每项任务运行 0.61 美元，大约是 [DeepSeek](https://www.together.ai/models-providers/deepseek) 价格的六倍。因此，问题不在于哪一款赢得了排行榜（Luna，轻松地），而是用六倍便宜的价格买了什么，你花了多少钱，以及两者一起是否击败了其中任何一个。

我们在所有 113 个 DeepSWE 任务上运行 DeepSeek-V4 Flash 0731（最大）与 GPT-5.6 Luna（最大）：来自实时开源存储库的真实、长期功能请求，每个任务进行四次试验，通过隐藏测试套件对通过/失败进行分级。根据已发布的每次试验记录，总共推出了 900 次（DeepSeek 方面有 452 次，Luna 方面有 448 次）。下面的每个数字都来自本次运行，因此可能与其他公共记分卡有所不同。

## **概览**

DeepSWE · 头对头

### DeepSeek-V4 Flash 与 GPT-5.6 Luna 对比一览

|型号|通过@1 |平均成本|出托克 |步骤|
| ---| ---| ---| ---| ---|
| gpt-5.6-luna [最大] | **67% ± 4%** | 0.61 美元 | 73k | 102 | 102
| deepseek-v4-flash [最大] | 53% ± 4% | **0.10 美元** | 108k | 153 | 153

Luna 的成本约为 6 倍，准确度提高约 14 点； DeepSeek 使用更多的输出令牌和步骤来缩短距离，但价格为 0.10 美元，是该系列中最便宜的运行方式。

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a755ae9f29796baf154f58d_08-accuracy-cost-effort.png)

## **DeepSWE 记分板：pass@1 和 pass@k**

在 DeepSWE 的官方评分下，Luna 明显胜出单杆：67.2% pass@1 ，而 DeepSeek 则为 53.3%，领先 14 分，准确率相对而言高出约 26%。在相同的尝试计数下，Luna 在每 k 项上都保持领先（两次尝试时为 81.6 vs 70.1，四次尝试时为 90.3 vs 80.5）。就原始解决能力而言，这不是一场近距离的战斗。

但 DeepSWE 正是这样一种工作负载，您可以并行地进行多次尝试，并且经济性会改写情况。 DeepSeek 的 pass@2 (70.1%) 已经超过了 Luna 的单次射门 (67.2%)，两次 DeepSeek 尝试的成本约为 0.20 美元，而 Luna 的成本为 0.61 美元。如果验证者能够选出获胜者，那么在下面的任何路由技巧发挥作用之前，便宜的型号就可以以三分之一的价格与旗舰产品的首次尝试质量相媲美。

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a7537e9d60a38a5c400d7e0_01-solve-rate-by-attempts.png)

## **成本比较：DeepSeek-V4 Flash 与 GPT-5.6 Luna 定价**

- 每项任务的价格为 0.61 美元，Luna 每 100 美元返回 110 个解决方案，而 DeepSeek 的解决方案为 532 个：廉价模型的价值优势为 4.8 倍。每个推出间隙的成本约为 6 倍。
- 廉价模型买不到的一件事是速度，这是与通常的“flash”模型故事相比的扭曲：DeepSeek 是这两者中较慢的一个，中位数为 23 分钟和 148 步，而 Luna 为 16 分钟和 92 步。它会研磨（并发出更多输出，中位数为 104k 代币，而 Luna 为 70k）。 DeepSeek的优势是金钱，而不是时间。
- 挂钟间隙部分是模型新旧程度造成的；随着推理引擎对其进行调整，预计它会缩小。

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a7537fb7738b3678fd7a4eb_02-cost-value-speed.png)

## **故障模式：DeepSeek 比旗舰产品更优雅地失败**

廉价模式悄然赢得的另一件事是纪律。当 DeepSeek 失败时，只有 9% 的失败会破坏存储库的现有测试套件。 Luna 的比例为 15%：GPT 系列回归特征，与我们在 Sol 和其他 OpenAI 谱系模型中看到的相同，为 15% 到 20%。两者的失败大多是因未遂事件而失败（DeepSeek 69%，Luna 66%），但更昂贵的模型更有可能干扰已经工作的代码。如果您部署 Luna，请将其置于完整回归运行之后； DeepSeek 较少需要护栏。

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a7538243beaa9328632f73d_03-failure-anatomy.png)

## **DeepSeek-V4 Flash 与 GPT-5.6 Luna（按任务域）对比**

根据代码的实际内容对 113 个任务进行分类，Luna 赢得了 8 个域中的 7 个。它最大的优势正是推理繁重的工作：程序分析（69 vs 33）、并发性和持久性（70 vs 38）、语言和运行时内部（86 vs 59），每项大约有 30 分的差距。这就是模型能力真正体现出来的地方，而 DeepSeek 的表现却严重下降。

DeepSeek 只拥有一个领域，而且这一领域很能说明问题：查询和配置语言，78 与 70。SQL 构建器、窗口函数、键集分页、配置解析器。结构化、模式化、遵循惯例的工作是廉价模型真正具有竞争力的地方，甚至是领先的。每当任务需要在整个系统中保持硬不变量时，Luna 的能力就会有所不同。

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a75382dae51b2becd28595c_04-solve-rate-by-task-domain.png)

## **DeepSeek-V4 Flash 与 GPT-5.6 Luna（按编程语言）对比**

Luna 赢得了全部五场比赛，但利润率告诉您在使用 DeepSeek 时需要小心的地方。它在 Rust（55 vs 60）和 Go（62 vs 79）上值得尊敬，但它的 JavaScript 却是崩溃的：35 vs Luna 的 60，整个对决中最弱的单格，还有 25 分的差距。 DeepSeek 的 Python 也很软（49 vs 65）。如果你的堆栈是 JS 密集型的，那么便宜的模型就是错误的经济；如果是配置、查询或 Rust，DeepSeek 可以弥补大部分差距。

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a753839093e357145b4f8e6_05-solve-rate-by-language.png)

## **DeepSeek-V4 Flash 和 GPT-5.6 Luna 有多相似？**

少于廉价线对。每个任务的相关性为 0.50，并且多样性是不平衡的：它们都解决了 87 个任务，Luna 独自完成了 15 个任务，而 DeepSeek 独自完成了 4 个任务。至关重要的是，没有一个 DeepSeek 扫过的任务是 Luna 完全错过的（零四对零角点对 DeepSeek 有利），而 Luna 扫除了 DeepSeek 从未完成的四个任务（go-critic-doc-link-checker， langchain-request-coalescing、meriyah-explicit-resource-declarations、superjson-error-stack-serialization）。他们的工会涵盖了 113 个中的 106 个（93.8%），但几乎所有这些都是卢娜自己的范围。作为一种原始的多样性游戏，DeepSeek 几乎没有增加任何东西。

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a753840433021ff99b04a3f_06-task-level-agreement.png)

## **投资组合游戏：为什么级联仍然有效**

所以配对应该是没有意义的。事实并非如此，原因是价格。首先运行 DeepSeek，仅当您的测试套件拒绝答案时才升级到 Luna：78.9% 的问题得到解决，每个任务 0.385 美元。请仔细阅读。它比单独的 Luna 更准确（67.2%，上升 11.7 个点），并且比单独的 Luna 更便宜（0.61 美元），约为 Luna 每任务成本的 63%。

几乎免费的第一阶段就是整个技巧：DeepSeek 以每个一毛钱的价格清除了大约 53% 的队列，因此 Luna 的充电只会触及硬剩余部分，而到达 Luna 的任务将在顶部进行第二次独立尝试。级联甚至击败了完美的一次性预言机路由器（74.3％），因为两次挥杆击败了一次完美的选择。无论哪个模型领先，精度都是相同的，但 DeepSeek-first 便宜得多（0.385 美元 vs 0.64 美元），因此始终以便宜的模型领先。

该对的上限为93.8%；从未解决的 7 个任务（包括 gql-incremental-graphql-delivery 和 bandit-structed-nosec-directives）需要更强大的第三个模型，而不是更好的路由器。

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a75384f88064ca1d33a4adf_07-cascade.png)

## **这意味着什么**

就其本身而言，DeepSeek-V4 Flash 0731 是一款中型模型，具有一个真实域（查询和配置）、干净的故障配置文件、灾难性的 JavaScript 弱点以及无与伦比的价格。 GPT-5.6 Luna 在每一个质量指标上都是更好的工程师：14 分 pass@1、8 个域中的 7 个、所有 5 种语言，速度也更快。你需要支付大约 6 倍的费用，再加上 GPT 系列回归习惯来护栏。这款旗舰产品每项售价 0.61 美元，确实很便宜，当您关心质量时，它是您的默认选择。但 DeepSeek 最明显的用途并不是作为 Luna 的替代品；而是作为 Luna 的替代品。它是一个 Luna 前端。第一阶段花费一毛钱并完成一半的工作，让您以低于旗舰产品本身的价格购买超越旗舰产品的精度。当廉价型号如此便宜时，级联不再是妥协，而是成为板上最好的排。

现已上市·开放重量

在 Together AI 上运行 DeepSeek-V4 Flash

DeepSWE 板上最便宜的模型，大约十美分一个任务。以生产规模提供廉价的第一阶段服务，无需前沿代币价格。

打开游乐场

## **附录：数据表**

DeepSWE·附录

### DeepSeek-V4 Flash 与 GPT-5.6 Luna：完整数据表

|公制| DeepSeek-V4 闪存 0731（最大）| GPT-5.6 Luna（最大）|
| ---| ---| ---|
| pass@1（官方评分）| 53.3% | **67.2%** |
| pass@1（错误视为失败）| 53.3% | **67.2%** |
|通过@2 / 通过@4 | 70.1 / 80.5% | **81.6 / 90.3%** |
|覆盖范围/可靠性| 80.5 / 66.2% | **90.3 / 74.8%** |
|实心 (4/4) / 墙壁 (0/4) | 23 / 22 | 23 / 22 **43 / 11** |
|每次部署成本/总计 | **0.10 美元/45 美元** | 0.61 美元/273 美元 |
|每 100 美元解决一个问题 | **532** | 110 | 110
|中位分钟/步数 | 23 / 148 | **16 / 92** |
|中值峰值上下文/输出标记 | 202k / 104k | 202k / 70k |
|故障剖析| **69% 接近，9% 回归** | 66% 接近，15% 回归 |
|赢得域名（共 8 个）| 1（查询和配置）| **7** |
|语言获胜 |无 | **全部 5** |
|每任务关联/联合 | 0.50 / 106 / 113 (93.8%) |  |
| Cascade DeepSeek > Luna（精度/成本）| **78.9% / 0.385 美元** |与单独的 Luna 相比 67.2% / 0.61 美元 |
| Oracle 1-shot 路由器 | 74.3% |  |
|排行榜排名（52 个配置）| 30 日 | **13日** |
|基础设施错误 | 0 | 0 |

## **常见问题解答**

### **GPT-5.6 Luna 比 DeepSeek-V4 Flash 更好吗？**

论质量，是的。 GPT-5.6 Luna 以 67.2% 比 53.3% 赢得 DeepSWE pass@1，在每次相同的尝试次数中领先，赢得 8 个任务域中的 7 个和所有 5 种语言，并且速度更快。 DeepSeek-V4 Flash 每次推出时在价格上获胜约 6 倍，并且在失败时失败得更干净。

### **DeepSeek-V4 Flash 比 GPT-5.6 Luna 便宜多少？**

在我们的运行中，DeepSeek-V4 Flash 每次推出的成本约为 0.10 美元，而 GPT-5.6 Luna 的每次推出成本为 0.61 美元，大约是其价格的六分之一。按照已解决的任务进行衡量，DeepSeek 每 100 美元返回 532 个解决方案，而 Luna 为 110 个，大约是每美元工作量的 4.8 倍。

### **您应该同时使用 DeepSeek-V4 Flash 和 GPT-5.6 Luna 吗？**

是的，在级联中。首先运行 DeepSeek，仅当测试套件拒绝答案时才升级到 Luna，在我们的运行中，以每个 0.385 美元的价格解决了 78.9% 的任务：比单独的 Luna (67.2%) 更准确，并且比单独的 Luna (0.61 美元) 更便宜。始终以廉价型号为主导；两种方式的准确性都是相同的，但 DeepSeek-first 的成本更低。

### **DeepSeek-V4 Flash 和 GPT-5.6 Luna 哪个更适合编码？**

在我们的细分中，Luna 赢得了所有语言，但差距有所不同。 DeepSeek 在 Rust 上受到尊重，并且在查询和配置工作方面具有竞争力，这实际上是它领先的地方。它的 JavaScript 是这场比赛中最弱的单元（35 vs 60），因此 JS 密集型堆栈不应仅依赖于廉价模型。

### **DeepSWE 上的 pass@k 是什么？**

pass@k 衡量一项任务的 k 次尝试中至少有一次是否通过了隐藏的测试套件。 pass@1 奖励第一次尝试就正确；较高的 k 奖励能够通过多次尝试最终找到解决方案的模型。 DeepSeek 的 pass@2 (70.1%) 已经领先 Luna 的 pass@1 (67.2%)，这就是并行尝试和级联经济学发挥作用的原因。

## 相关文章
