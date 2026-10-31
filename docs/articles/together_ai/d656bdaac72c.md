---
vendor: together_ai
title: DeepSeek-V4 Flash 0731 与 GPT-5.6 Luna 在 DeepSWE 上的成本与编码对比
original_title: 
url: https://www.together.ai/blog/deepseek-v4-flash-0731-vs-gpt-5-6-luna-on-deepswe-cost-and-coding
date: 2026-08-06
lang: zh
captured: 2026-10-31
extractor: readability-v1
translator: agent
status: translated
body_sha: a988e07c5ed8
---

# DeepSeek-V4 Flash 0731 与 GPT-5.6 Luna 在 DeepSWE 上的成本与编码对比

这款开放权重模型为「价格-智能比」立下了新的标杆

- 作者：Zain Hasan、Shobhit Dixit
- 目录[为生产环境选定的 40 多个模型……为生产环境选定的 40 多个模型……为生产环境选定的 40 多个模型……](https://www.together.ai/blog/deepseek-v4-flash-0731-vs-gpt-5-6-luna-on-deepswe-cost-and-coding)

核心要点

尽管 GPT-5.6 Luna 在每一项质量指标上都是更强的工程师，但 DeepSeek-V4 Flash 0731 足够便宜，以至于一条 DeepSeek 优先的级联（cascade）在准确率和成本上都胜过了单独使用 Luna。

- GPT-5.6 Luna 在 DeepSWE 的 pass@1 上以 67.2% 对 53.3% 决定性领先，差距 14 个百分点，并且在每一个相同的尝试次数上都保持领先。
- DeepSeek-V4 Flash 是 DeepSWE 榜单上最便宜的模型：每次 rollout $0.10 对 $0.61，每 100 美元产出 532 次解题，而 Luna 是 110 次。
- DeepSeek-V4 Flash 失败得更干净：在它的失败案例中只有 9% 弄坏了仓库原有的测试套件，而 Luna 是 15%。
- 先跑 DeepSeek-V4 Flash、只在失败时升级到 Luna，能以每任务 $0.385 解出 78.9% 的任务：比单独用 Luna 更准，还便宜 37%。

现已可用 · 开放权重

在 Together AI 上运行 DeepSeek-V4 Flash

DeepSWE 榜单上最便宜的模型，每任务约一美分。用廉价的第一阶段以生产规模提供服务，而不必付出前沿模型的 token 价格。

打开 playground

[DeepSeek-V4 Flash 0731](https://www.together.ai/models/deepseek-v4-flash-0731) 是整个 DeepSWE 榜单上最便宜的模型：每个任务大约一美分！GPT-5.6 Luna 是一台扎实的上层旗舰，每任务跑 $0.61，大约是 [DeepSeek](https://www.together.ai/models-providers/deepseek) 价格的六倍。所以问题不在于谁赢下榜单（Luna，赢得毫无悬念），而在于便宜六倍能给你买到什么、要你付出什么，以及两者一起用能不能胜过任何一个单干。

我们在全部 113 个 DeepSWE 任务上把 DeepSeek-V4 Flash 0731（max）对 GPT-5.6 Luna（max）跑了一遍：这些是真实运行中的开源仓库里长周期的功能请求，每个任务四次试验，由一套隐藏测试套件判 pass/fail。按公开的逐试验记录算下来一共是 900 次 rollout（DeepSeek 这边 452 次，Luna 那边 448 次）。下面每一个数字都来自这次运行，因此可能与其他公开记分卡不同。

## **一眼看全**

DeepSWE · 正面对决

### DeepSeek-V4 Flash 对 GPT-5.6 Luna：一眼看全

| 模型 | Pass@1 | 平均成本 | 输出 tok | 步数 |
| --- | --- | --- | --- | --- |
| gpt-5.6-luna [max] | **67% ± 4%** | $0.61 | 73k | 102 |
| deepseek-v4-flash [max] | 53% ± 4% | **$0.10** | 108k | 153 |

Luna 大约 6 倍的成本换来大约 14 个百分点的准确率；DeepSeek 用掉更多输出 token 和更多步数，却走得更浅，但按 $0.10 算，它是整组里最便宜的一次运行，而且便宜一大截。

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a755ae9f29796baf154f58d_08-accuracy-cost-effort.png)

## **DeepSWE 记分板：pass@1 与 pass@k**

单发这一项 Luna 赢得很清楚：按 DeepSWE 的官方评分口径，pass@1 为 67.2% 对 DeepSeek 的 53.3%，领先 14 个百分点，相对意义上约更准 26%。在相同的尝试次数下，Luna 在每个 k 上都保持领先（两次尝试 81.6 对 70.1，四次尝试 90.3 对 80.5）。就原始解题能力而言，这不是一场势均力敌的较量。

但 DeepSWE 恰恰是那种可以并行铺开多次尝试的工作负载，而在这一点上经济学重写了图景。DeepSeek 的 pass@2（70.1%）已经略微超过 Luna 的单发（67.2%），而两次 DeepSeek 尝试大约花 $0.20，Luna 则是 $0.61。如果有一个校验器能挑出成功的那次运行，那么这个廉价模型就以三分之一的价格追上了旗舰的首试质量——这还没动用下面任何路由技巧。

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a7537e9d60a38a5c400d7e0_01-solve-rate-by-attempts.png)

## **成本对比：DeepSeek-V4 Flash 与 GPT-5.6 Luna 的定价**

- 在每任务 $0.61 的价位上，Luna 每 100 美元换回 110 次解题，而 DeepSeek 是 532 次：廉价模型在性价比上有 4.8 倍的优势。每次 rollout 的成本差距约为 6 倍。
- 廉价模型唯一没给你买到的东西是速度，而这一点正是与通常的 "flash" 模型叙事相反的反转：这里 DeepSeek 是两者中更慢的那个，中位耗时 23 分钟、148 步，而 Luna 是 16 分钟、92 步。它磨得慢（也吐出更多内容，中位 104k 输出 token 对 Luna 的 70k）。DeepSeek 的优势是钱，不是时间。
- 这个墙上时钟（wall-clock）差距部分源于模型太新；随着推理引擎为它调优，预计会缩小。

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a7537fb7738b3678fd7a4eb_02-cost-value-speed.png)

## **失败模式：DeepSeek 比旗舰失败得更体面**

廉价模型悄悄赢下的另一件事是纪律性。DeepSeek 失败时，只有 9% 的失败会弄坏仓库已有的测试套件。Luna 是 15%：这就是 GPT 系的回归（regression）特征，与我们在 Sol 和其他 OpenAI 血统模型上看到的 15 到 20% 一致。两者主要都以"差一点"的方式失败（DeepSeek 69%，Luna 66%），但更贵的那个模型才是更可能动坏原本已经能工作的代码的那个。如果你部署 Luna，就把它挡在一次完整回归跑之后；DeepSeek 没那么需要这道护栏。

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a7538243beaa9328632f73d_03-failure-anatomy.png)

## **DeepSeek-V4 Flash 与 GPT-5.6 Luna 按任务领域对比**

按代码实际是什么来给这 113 个任务分类，Luna 在 8 个领域里赢下 7 个。它最大的优势恰恰在推理密集的那几块：程序分析（69 对 33）、并发与持久性（70 对 38）、语言与运行时内部机制（86 对 59），每一块都大约 30 个百分点的差距。这正是模型能力真正显形的地方，而 DeepSeek 在这里掉得很厉害。

DeepSeek 只守住了一个领域，而且是个耐人寻味的领域：查询与配置语言，78 对 70。SQL 构造器、窗口函数、keyset 分页、配置解析器。结构化的、按 schema 塑形的、遵循约定的一类活，正是廉价模型真正有竞争力、甚至领先的所在。而在任务要求把一条硬不变量贯穿整个系统保持住的地方，Luna 的能力就拉开了差距。

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a75382dae51b2becd28595c_04-solve-rate-by-task-domain.png)

## **DeepSeek-V4 Flash 与 GPT-5.6 Luna 按编程语言对比**

Luna 赢下全部五种语言，但差距的幅度告诉你 DeepSeek 该在哪些地方小心。它在 Rust（55 对 60）和 Go（62 对 79）上算体面，但它的 JavaScript 是崩盘：35 对 Luna 的 60，是整场对决里最弱的单个格子，而且是一个 25 个百分点的大坑。DeepSeek 的 Python 也偏软（49 对 65）。如果你的技术栈以 JS 为主，廉价模型就是省错了地方；如果是配置、查询或 Rust，DeepSeek 能补上大部分差距。

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a753839093e357145b4f8e6_05-solve-rate-by-language.png)

## **DeepSeek-V4 Flash 与 GPT-5.6 Luna 有多相似？**

相似程度不如廉价档位之间的那些配对。逐任务相关性是 0.50，而且多样性一边倒：两者都解出的任务有 87 个，只有 Luna 解出的有 15 个，而只有 DeepSeek 解出的只有 4 个。关键在于：不存在某个 DeepSeek 全对而 Luna 完全没拿下的任务（DeepSeek 占优的四对零角落是零个），而 Luna 全对、DeepSeek 一次都没拿下的有四个（go-critic-doc-link-checker、langchain-request-coalescing、meriyah-explicit-resource-declarations、superjson-error-stack-serialization）。两者的并集覆盖 113 个中的 106 个（93.8%），但其中几乎全部是 Luna 自己的射程。作为纯粹的多样性下注，DeepSeek 增添得很少。

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a753840433021ff99b04a3f_06-task-level-agreement.png)

## **组合打法：为什么级联依然有效**

所以这对配对本该毫无意义。它并不是，而原因就是价格。先跑 DeepSeek，只有当你的测试套件否掉答案时才升级到 Luna：解出 78.9%，每任务 $0.385。请仔细读这个数字。它比单独用 Luna 更准（67.2%，提升 11.7 个百分点），又比单独用 Luna 更便宜（$0.61），落在 Luna 每任务成本的大约 63%。

近乎免费的第一阶段就是全部诀窍：DeepSeek 以每个一美分的价钱清掉队列里大约 53%，于是 Luna 的计费只会落在剩下的难题上，而到达 Luna 的那些任务还在其上多了一次独立的尝试机会。这个级联甚至胜过一个完美的一次性预言机路由器（74.3%），因为两次挥棒好过一次完美的挑选。无论哪个模型打头，准确率都一样，但 DeepSeek 优先要便宜得多（$0.385 对 $0.64），所以永远用便宜的那个打头。

这对组合的上限是 93.8%；两者始终都解不出的那 7 个任务（其中包括 gql-incremental-graphql-delivery 和 bandit-structured-nosec-directives）需要的是更强的第三个模型，而不是更好的路由器。

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a75384f88064ca1d33a4adf_07-cascade.png)

## **这意味着什么**

单看自己，DeepSeek-V4 Flash 0731 是一个中游模型，只有一个真正拿手的领域（查询与配置）、一份干净的失败画像、一处灾难性的 JavaScript 短板，以及一个无人能敌的价格。GPT-5.6 Luna 在每一项质量指标上都是更好的工程师：pass@1 高 14 个百分点、8 个领域里赢 7 个、5 种语言全赢，速度也更快。你要为此付出大约 6 倍代价，外加一套需要护栏拦住的 GPT 系回归习惯。以每任务 $0.61 计，这台旗舰确实便宜，而当你在乎的是质量时，它就是那个省事的默认项。但 DeepSeek 最锋利的用法不是当作 Luna 的替代品，而是当作 Luna 的前置。一个只花一美分、却能清掉一半工作量的第一阶段，让你用低于旗舰自身价格的成本买到胜过旗舰的准确率。当廉价模型能便宜到这个地步，级联就不再是妥协，而成了整块榜单上最好的一行。

现已可用 · 开放权重

在 Together AI 上运行 DeepSeek-V4 Flash

DeepSWE 榜单上最便宜的模型，每任务约一美分。用廉价的第一阶段以生产规模提供服务，而不必付出前沿模型的 token 价格。

打开 playground

## **附录：数据表**

DeepSWE · 附录

### DeepSeek-V4 Flash 对 GPT-5.6 Luna：完整数据表

| 指标 | DeepSeek-V4 Flash 0731 (max) | GPT-5.6 Luna (max) |
| --- | --- | --- |
| pass@1（官方评分） | 53.3% | **67.2%** |
| pass@1（把错误算作失败） | 53.3% | **67.2%** |
| pass@2 / pass@4 | 70.1 / 80.5% | **81.6 / 90.3%** |
| 覆盖率 / 可靠性 | 80.5 / 66.2% | **90.3 / 74.8%** |
| 稳定（4/4）/ 全败（0/4） | 23 / 22 | **43 / 11** |
| 每次 rollout 成本 / 总计 | **$0.10 / $45** | $0.61 / $273 |
| 每 100 美元解题数 | **532** | 110 |
| 中位分钟数 / 步数 | 23 / 148 | **16 / 92** |
| 中位峰值上下文 / 输出 token | 202k / 104k | 202k / 70k |
| 失败解剖 | **69% 接近成功，9% 回归** | 66% 接近成功，15% 回归 |
| 赢下的领域（共 8 个） | 1（查询与配置） | **7** |
| 赢下的语言 | 无 | **全部 5 种** |
| 逐任务相关性 / 并集 | 0.50 / 113 中的 106（93.8%） |  |
| 级联 DeepSeek > Luna（准确率 / 成本） | **78.9% / $0.385** | 对比单独 Luna 67.2% / $0.61 |
| 预言机单发路由器 | 74.3% |  |
| 榜单排名（共 52 个配置） | 第 30 | **第 13** |
| 基础设施错误 | 0 | 0 |

## **常见问题**

### **GPT-5.6 Luna 比 DeepSeek-V4 Flash 更好吗？**

就质量而言，是的。GPT-5.6 Luna 在 DeepSWE 的 pass@1 上以 67.2% 对 53.3% 取胜，在每一个相同的尝试次数上都领先，赢下 8 个任务领域中的 7 个和全部 5 种语言，而且更快。DeepSeek-V4 Flash 赢在价格上，每次 rollout 大约 6 倍，并且失败时失败得更干净。

### **DeepSeek-V4 Flash 比 GPT-5.6 Luna 便宜多少？**

在我们的这次运行中，DeepSeek-V4 Flash 每次 rollout 约 $0.10，而 GPT-5.6 Luna 是 $0.61，大约是六分之一的价格。按每解出一个任务来衡量，DeepSeek 每 100 美元产出 532 次解题，而 Luna 是 110 次，即每美元大约多干 4.8 倍的活。

### **DeepSeek-V4 Flash 和 GPT-5.6 Luna 该一起用吗？**

该，用级联的方式。先跑 DeepSeek、只在测试套件否掉答案时才升级到 Luna，在我们这次运行里以每任务 $0.385 解出 78.9% 的任务：比单独用 Luna 更准（67.2%），也比单独用 Luna 更便宜（$0.61）。永远让便宜的模型打头；准确率无论如何都一样，但 DeepSeek 优先花得更少。

### **写代码哪个更好，DeepSeek-V4 Flash 还是 GPT-5.6 Luna？**

在我们的分语言拆解里 Luna 赢下每一种语言，但差距不一。DeepSeek 在 Rust 上算体面，在查询与配置类的工作上也有竞争力——那里它确实领先。它的 JavaScript 是整场对决里最弱的格子（35 对 60），所以以 JS 为主的技术栈不该只指望这个廉价模型。

### **DeepSWE 上的 pass@k 是什么？**

pass@k 衡量的是对某个任务的 k 次尝试里是否至少有一次通过隐藏测试套件。pass@1 奖励一次就做对；k 越高，越奖励那些经过几次尝试最终能抵达解的模型。DeepSeek 的 pass@2（70.1%）已经略微超过 Luna 的 pass@1（67.2%），这正是并行尝试与级联的经济学能够成立的原因。

## 相关文章
