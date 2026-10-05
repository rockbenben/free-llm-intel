---
vendor: together_ai
title: DeepSeek V4 Pro 0813 对阵 Claude Fable 5：DeepSWE 上的成本、编码能力与路由
original_title: "DeepSeek V4 Pro 0813 vs Claude Fable 5 on DeepSWE: Cost, Coding, and Routing"
url: https://www.together.ai/blog/deepseek-v4-pro-0813-vs-claude-fable-5-on-deepswe-cost-coding-and-routing
date: 2026-08-17
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# DeepSeek V4 Pro 0813 对阵 Claude Fable 5：DeepSWE 上的成本、编码能力与路由

Fable 赢在首次尝试，Pro 赢在其后的每一次尝试，而最便宜的路径是两个都用。

## 关键结论

先跑 DeepSeek V4 Pro 0813，失败时才升级到 Claude Fable 5。这个级联以每个任务 \$8.28 的成本解决 DeepSWE 82.7% 的任务。Fable 单独跑是 69.7%、每个 \$21.63。高 13 个百分点，便宜 62%。

- Fable 首次即胜：pass@1 69.7% 对 62.8%，领先 7 个百分点。
- Pro 赢下之后的每一次：pass@2 打平（78.5% vs 77.1%），pass@4 领先（88.5% vs 84.1%）。
- 价差达 90 倍。每次 rollout \$0.24 对 \$21.63。每 100 美元，Pro 解决 260 个任务，Fable 只有 3 个。
- 它们在任务上错开的方向不同。逐任务相关系数仅 0.39，是我们测过的最分歧的一对。两者合计覆盖 113 个任务中的 107 个。正是这种分歧让路由奏效。

现已可用 · 美国托管

在 Together AI 上运行 DeepSeek-V4 Pro 0813

1.05M 上下文，function calling 与 JSON mode，OpenAI 兼容 API，由美国基础设施提供服务。

查看模型

在我们的 [DeepSeek V4 Pro 0813](https://www.together.ai/models/deepseek-v4-pro-0813) vs Claude Fable 5 DeepSWE 对比中——DeepSWE 是一个跨多种任务类型和编程语言测试模型软件工程能力的基准——两个模型位于价格表的两端。Claude Fable 5 是 DeepSWE 榜单上最贵的 rollout，DeepSeek V4 Pro 0813 则是最便宜的之一。Fable 首次尝试准确率高 7 个百分点，但每次 rollout 贵 90 倍。所以真正的问题不是哪个模型更好，而是这 90 倍溢价到底买到了什么、什么时候值得付。

DeepSWE · 直接对决

### DeepSeek V4 Pro 0813 vs Claude Fable 5 速览

| 模型 | Pass@1 | 平均成本 | 每 \$100 解决数 | 输出 token | 步数 |
| --- | --- | --- | --- | --- | --- |
| claude-fable-5 [max] | **69.7% ± 2.3%** | $21.63 | 3 | 115k | **79** |
| deepseek-v4-pro-0813 [max] | 62.8% ± 3.1% | **$0.24** | **260** | **101k** | 146 |

我们在全 113 个 DeepSWE 任务上用四个 trial 跑了 DeepSeek V4 Pro 0813 (max) 对 Claude Fable 5 (max)，数据来自公布的逐 trial 记录：共 904 次 rollout（各 452 次）。Fable 是昂贵的匠人；Pro 是性价比异类。两者在这个集合中的分歧也超过任何其他配对——事后证明这是它们最有意思的地方。下文每个数字都来自这次运行，因此可能与其他公开的 DeepSeek V4 Pro 0813 vs Claude Fable 5 计分卡不同。

## **DeepSWE 计分板：pass@1 与 pass@k**

单次尝试，Fable 领先：pass@1 69.7% 对 Pro 的 62.8%（官方评分）。但这个领先很脆弱。两次尝试时 Pro 追平（78.5 vs 77.1），四次尝试时 Pro 的 88.5% pass@4 甩开 Fable 的 84.1% 超过四个百分点。对一个贵 90 倍的模型来说，Fable 既不占据上限，也在重试下保不住首枪优势。低成本的模型同时拥有更广的触达和更高的 best-of-k。

## **成本对比：DeepSeek V4 Pro 0813 与 Claude Fable 5 定价**

每次 rollout \$0.24，DeepSeek V4 Pro 0813 比 Fable（\$21.63）便宜 90 倍：每 100 美元解决 260 个任务对 Fable 的 3 个。这是我们测过的所有配对中最宽的价差，而且 Fable 是榜单上单价最高的配置。不寻常的是，低价格并没有伴随你预期的速度惩罚：Fable 的 rollout 中位耗时 31 分钟对 Pro 的 35 分钟，大致持平——因为 Fable 是榜单上话最多的模型（115k 输出 token），尽管它步数更少（79 vs 146）。Pro 步数更多；Fable 每步写更多。两个模型都不算明显更快。

## **失败模式：两个模型各自怎么犯错**

两者都很有分寸地不破坏既有功能：**DeepSeek V4 Pro 0813 和 Fable 各自只在 11% 的失败案例中让现有测试套件回归**，远低于 GPT 家族的 20%。差别在另一个方向：Fable 的"离谱错"占比在这里最大（18% vs Pro 的 10%），意思是 Fable 错的时候更常错得离谱——解法离靶心很远，而不是差一个边缘情况。Pro 更常在接近正确的地方失败（近失 66% vs Fable 的 57%）。所以两者都可以放心接受而无需重型回归门禁，但 Fable 的失误是更贵的那种，更难 debug。

## **各自在哪里赢：按任务类型**

Fable 的匠心体现在重推理、精确契约的领域：8 个领域中赢 6 个，以数据建模与序列化 88%（超 Pro 24 个百分点）和语言内部机制（78）领跑。但 DeepSeek V4 Pro 0813 拿下两个，且都很重要：有状态响应式（66 vs 64），以及耐人寻味的并发与持久化（58 vs 45）：恰好在 Fable 最差的领域领先 13 个百分点。Fable 在并发上的 45% 是它最弱的一格，也是唯一一个低成本模型就是更好的工程师——而不只是更便宜——的领域。

## **DeepSeek V4 Pro 0813 vs Claude Fable 5 按编程语言**

Fable 在五种语言中赢四种，但让它价格站得住的数字是 Rust：85% 对 Pro 的 65，20 个百分点的差距，是对决中最宽的单点差距。Fable 明显是序列化与 Rust 专家。其他地方比价格暗示的要接近（Python 70 vs 60，Go 71 vs 67，JavaScript 75 vs 65），而 DeepSeek V4 Pro 0813 实际拿下了 TypeScript（61 vs 57）。在 Rust 和序列化之外，付 90 倍的理由很难成立。

## **两个模型有多大差异？**

以下是 Fable 挽回颜面的特性。逐任务相关系数只有 0.39，是所有 DeepSeek-Pro 配对中最低的，这两个模型是真分歧。它们各解出 88 个任务；Pro 独立解出 12 个，Fable 独立解出 7 个，只有 6 个同时难住两者。两者的并集覆盖 113 个中的 107 个（94.7%），且分歧是双向的：DeepSeek V4 Pro 0813 把 awilix-async-container-initialization 四次全收，Fable 一次都没拿下；Fable 则四次全收 Pro 挂零的四个任务（包括 koota-query-predicates 和 testem-bail-on-test-failure）。这是真正的互补，不是冗余。

## **在两者之间路由：投资组合打法**

这种多样性加上价差，让级联极具吸引力。先跑 DeepSeek V4 Pro 0813，只有当你的测试套件拒绝答案时才升级到 Fable：82.7% 解决率、每任务 \$8.28。这比 Fable 单独跑（69.7%）高 13 个百分点，而成本还不到 Fable 单价（\$21.63）的一半。低成本的第一级消化了队列的大部分，Fable 的高价只施加在困难的剩余部分上，而且那些任务还额外获得一次独立的第二尝试。这个级联甚至打败了完美的一次命中 oracle 路由器（78.8%）。顺序不可颠倒：Pro 优先成本 \$8.28，Fable 优先成本 \$21.71，准确率却相同。

## **这意味着什么**

Fable 5 是这张榜单上最难被论证为"默认选择"的单体模型：最贵的 rollout，会被重试抹平的首枪领先，也没有四枪上限优势。为且仅为两件事买它：Rust（85%）和序列化密集的工作（88%），它的质量在那儿确实配得上价格。

DeepSeek V4 Pro 0813 是相反的画像：首次尝试接近 Fable 的准确率、更高的上限、持平或更好的失败画像、便宜 90 倍——尽管它在 Rust 和精确契约领域认输。而由于两者是我们测过最多样的配对，Fable 的最佳用法不是当默认，而是作为低成本 Pro 第一级之后的选择性升级，只为那几个真需要 Rust 或序列化专家的任务付费。

现已可用 · 美国托管

在 Together AI 上运行 DeepSeek-V4 Pro 0813

1.05M 上下文，function calling 与 JSON mode，OpenAI 兼容 API，由美国基础设施提供服务。

查看模型

## **数据表：DeepSeek V4 Pro 0813 vs Claude Fable 5 完整结果**

DeepSWE · 完整结果

| 指标 | deepseek-v4-pro-0813 [max] | claude-fable-5 [max] |
| --- | --- | --- |
| Pass@1（官方评分） | 62.8% | **69.7%** |
| Pass@1（错误计为失败） | 62.8% | **67.3%** |
| Pass@2 / pass@4 | **78.5 / 88.5%** | 77.1 / 84.1% |
| 覆盖 / 可靠性 | 88.5 / 71.0% | 84.1 / 82.0% |
| 稳定（4/4）/ 死磕（0/4） | 35 / 13 | 56 / 18 |
| 每次 rollout / 总成本 | **$0.24 / $109** | $21.63 / $9,346 |
| 每 \$100 解决数 | **261** | 3 |
| 中位分钟数 / 步数 | 35 / 146 | 31 / 79 |
| 中位峰值上下文 / 输出 token | 232k / 101k | 202k / 115k |
| 失败解剖（近失 / 离谱错 / 回归） | 66% / 10% / 11% | 57% / 18% / 11% |
| 赢得的领域（共 8） | 2（stateful、concurrency） | **6** |
| 赢得的语言 | 1（TypeScript） | **4（Rust 是碾压）** |
| 逐任务相关系数 / 并集 | 0.39 / 113 中 107（94.7%） |  |
| 级联 Pro → Fable（准确率 / 成本） | **82.7% / $8.28**（Fable 单独 69.7% / $21.63） |  |
| Oracle 一次命中路由器 | 78.8% |  |
| 基础设施错误 | 0 | 16 |

## **FAQ**

### **DeepSeek V4 Pro 0813 比 Claude Fable 5 好吗？**

看指标。Claude Fable 5 赢在单次尝试质量（pass@1 69.7% vs 62.8%），四枪全中（56 vs 35）也更多。DeepSeek V4 Pro 0813 在 pass@2 追平、赢下 pass@4（88.5% vs 84.1%），每次 rollout 成本低 90 倍，因此对高吞吐或可容忍重试的 agent 工作，它是更强的价值之选。

### **DeepSeek V4 Pro 0813 比 Claude Fable 5 便宜多少？**

在我们的运行中，DeepSeek V4 Pro 0813 每次 rollout 成本 \$0.24，Claude Fable 5 max effort 为 \$21.63，约便宜 90 倍。按每解决任务计，Pro 每 \$100 返回 260 个解决，Fable 只有 3 个，每美元解决量约为其 80 倍。

### **编码选 DeepSeek V4 Pro 0813 还是 Claude Fable 5？**

多数编码工作上，两者比价格暗示的更接近。Claude Fable 5 领先 Rust（85 vs 65）、Python、Go 和 JavaScript，8 个任务领域赢 6 个，以数据建模和序列化领衔。DeepSeek V4 Pro 0813 拿下 TypeScript（61 vs 57）、有状态响应式，以及并发与持久化（58 vs 45）——后者是 Fable 最弱的领域。

### **我该在 DeepSeek V4 Pro 0813 和 Claude Fable 5 之间做路由吗？**

可以验证结果的话，应该。两个模型拥有我们测过所有配对中最低的逐任务相关系数（0.39），合计覆盖 113 个任务中的 107 个。先跑 DeepSeek V4 Pro 0813，测试套件拒绝输出时升级到 Claude Fable 5，达到 82.7%、每任务 \$8.28——超过 Fable 单独运行，也超过完美的一次命中 oracle 路由器。

### **DeepSWE 上的 pass@k 是什么？**

pass@k 度量对某任务的 k 次尝试中是否至少有一次通过隐藏测试套件。pass@1 奖励一次做对；更高的 k 奖励能在多次尝试中最终抵达解法的模型。DeepSeek V4 Pro 0813 的优势随 k 增大而扩大。
