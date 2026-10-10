---
vendor: huggingface
title: Agent 说它做完了，数据库却不同意
original_title: The Agent Said It Was Done. The Database Disagreed.
url: https://huggingface.co/blog/microsoft/thinkingbox
date: 2026-08-27
lang: zh
captured: 2026-10-10
extractor: readability-v1
translator: agent
status: translated
body_sha: ecd08264220a
---

# Agent 说它做完了，数据库却不同意

企业级

文章

发布
					October 3, 2026

点赞

64

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64b8491203124195cd795cad/KWtqxooyzbqzLqdJorOPi.png)](https://huggingface.co/tuhink)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6a27ffbf0ea26227e43a0d29/Hk8XoWHT5braavBTjifaw.jpeg)](https://huggingface.co/Hectozar)
- [![](https://huggingface.co/avatars/821997acf79b7113de576661b1111109.svg)](https://huggingface.co/youngko)
- [![](https://huggingface.co/avatars/1462091a632d06d8b3bdf28a8007f621.svg)](https://huggingface.co/IronTech-Studios)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/YtxawKNmLmMd5dkoGXX6j.png)](https://huggingface.co/bedesign62)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/0K6rX9DTE_L7C_ktLloT7.jpeg)](https://huggingface.co/geminiomnidev)

Tuhin Kundu

tuhink

microsoft

*Microsoft ThinkingBox 给 AI agent 打分，看的是它们留下的记录，而不是它们生成的句子，并且进一步追问：它们能不能连续二十次都做对。该基准现已通过 Hugging Face 提供。*

[![Figure-1](https://cdn-uploads.huggingface.co/production/uploads/64b8491203124195cd795cad/Dzuml_9K2lfRq4hZi17EY.png)](https://cdn-uploads.huggingface.co/production/uploads/64b8491203124195cd795cad/Dzuml_9K2lfRq4hZi17EY.png)

*图 1：ThinkingBox 让一个 agent 在隔离的 MCP tool 会话中运行，然后对它留下的最终 backend 状态和副作用进行打分。出自我们的 [ThinkingBox 论文](https://arxiv.org/abs/2608.19741)。*

#### 这是 Microsoft 与 Hugging Face 的联合博客，特别感谢 Tommy Guy（Enderis AI 创始人，曾任职于 Microsoft）、来自 Hugging Face 的 Sergio Paniego，以及我们此前的实习生 Zhuochun Li（University of Pittsburgh）、Ali Keramati（UC Irvine）、Youngmin Ko（Northwestern）在共同撰写与评审上付出的努力。

一位客户来信。她那台 $745 的厨房电器卡在 Nashville 配送中心的快递「异常」状态里，已经比预计送达日期晚了十五天。

这个 AI agent 做得很细致。九次 tool call：它调出订单、查询物流、检索她的客户档案、两次搜索退款政策、确认没有已存在的工单、新建了一个、记录了时间线，并且把政策读对了；她的账户分层确实不符合延迟送达补偿的条件。

然后它把工单以 **resolved** 关闭，并回复“ *既然您的问题已经解决，还有什么我可以帮您的吗？* ”

有两点是错的。承运方的异常状态仍然未关闭，所以要求的目标终态应是 **on hold**，等待处理。而客户始终没有得到她真正所问问题的实际答复。

如果 AI 评分器检查的是 tool call，它会看到九次格式良好的调用。检查 agent 是否写入了数据库的评分器同样会看到这些。真正**不同意**的是数据库。

ThinkingBox 度量的正是这道落差。它在 507 个有状态的业务流程上、针对多个 LLM 模型各运行 20 次，依据最终的 backend 状态与副作用为 agent 打分。本文介绍我们的发现、一致性要付出什么代价，以及如何通过 [OpenEnv](https://github.com/huggingface/OpenEnv/tree/main/envs/thinkingbox_env) 自己运行这个基准。

**你也可以亲自跑这一条：**上面的例子改编自某个基准任务 [sandbox_external_retail_group1.py:test_case_ST003_006](https://github.com/microsoft/thinkingbox-data/blob/thinkingbox-bench-v1.0/dataset/test_case/sandbox_external_retail/sandbox_external_retail_group1.py#L984-L1223)，而失败的那条可执行检查只涉及一个字段：工单状态是 solved，而要求的目标终态是 hold。完整 trace 见[我们论文的附录 D.4，Case 3](https://arxiv.org/pdf/2608.19741)。

**目录**

- [tool call 不等于结果](https://huggingface.co/blog/microsoft/thinkingbox#a-tool-call-is-not-an-outcome)
- [一次成功不等于可靠](https://huggingface.co/blog/microsoft/thinkingbox#one-success-is-not-reliability)
- [你能依赖 agent 背后的那个模型吗？](https://huggingface.co/blog/microsoft/thinkingbox#can-you-depend-on-the-model-behind-your-agent)
- [一致性要付出什么](https://huggingface.co/blog/microsoft/thinkingbox#what-consistency-costs)
- [失败特征](https://huggingface.co/blog/microsoft/thinkingbox#failure-signatures)
- [它是怎么工作的](https://huggingface.co/blog/microsoft/thinkingbox#how-it-works)
- [自己跑一遍](https://huggingface.co/blog/microsoft/thinkingbox#run-it-yourself)
- [下一步往哪走](https://huggingface.co/blog/microsoft/thinkingbox#where-this-goes-next)

> 想在读结果之前先试一手？直接跳到「自己跑一遍」一节。

## tool call 不等于结果

最终回复和合法的 tool call 只是替代指标。一个 agent 可以听起来完全正确，同时留下错误的取值、改错了记录，或多造出一个副作用。只有它留下的记录能给出定论。

这道落差相当大。在一项覆盖 12 个 LLM 模型、121,680 次有效试次的同集合消融实验中，79,853 次尝试未通过可执行检查。在这些失败里，67.24% 依然是干净终止、调用过会改变状态的工具、且没有上报最终的 tool 错误。但可执行检查仍在其中 77.61% 上发现字段取值错误，43.30% 发现非预期的多余副作用，25.36% 发现缺失必需的副作用。这些状态检查的结论之间存在重叠。

> 轨迹是一句声明。数据库状态才是证据。重复才是信任的检验。

## 一次成功不等于可靠

一个 agent 处理退款第一次做对了、后面四次都做错，那它不能算一个能用的退款 agent。所以每个任务都**独立运行 20 次**，每次都从一个完全相同的干净 backend 出发，我们报告三个不同的指标：

*表 1：我们报告的三个数字，以及它们各自回答的问题。*

| 指标 | 衡量什么 | 回答什么问题 |
| --- | --- | --- |
| pass@1 | 所有尝试中成功的比例 | 它通常表现如何？ |
| pass@20 | 20 次尝试中**至少成功一次**的任务占比 | 它*能不能*做到这件事？讲的是广度。 |
| Observed 20/20 | 在实际记录的 20 次尝试中**全部**通过的任务 | 它能不能*每一次*都正确？ |

本博客里的 **observed 20/20** 就是字面计数：507 个任务中有多少个做到了 20 次全过。不做估计，不做平滑。

先从大家熟悉的视角看起。下表报告 pass@1，也就是单次尝试得分的估计值，并按业务域拆分。这正是大多数排行榜公布的数字，单看它，就像一份普通的能力排名。

*表 2：ThinkingBox-Bench 各业务域的 pass@1（%）。每个模型都在每个任务上重复评测 20 次。加粗标注组内第一，下划线标注第二。单次尝试得分估计的标准误见 [ThinkingBox 论文中的表 4](https://arxiv.org/abs/2608.19741)。*

| 模型 | 零售 (98) | 车险 (100) | 旅行 (104) | 新银行 (104) | 咨询 (101) | 总体，按任务加权 (507) |
| --- | --- | --- | --- | --- | --- | --- |
| *专有模型* |  |  |  |  |  |  |
| Claude Opus 5.5 | **80.97** | **68.40** | 54.28 | **71.25** | 61.58 | **67.16** |
| Claude Opus 5 | 80.71 | 65.80 | 49.95 | 70.62 | **66.19** | 66.50 |
| GPT-5.4 | 76.33 | 62.65 | **68.12** | 65.34 | 54.60 | 65.36 |
| GPT-5.6 Sol | 67.65 | 65.30 | 60.34 | 59.09 | 57.52 | 61.91 |
| Claude Sonnet 4.6 | 72.35 | 54.40 | 58.94 | 56.39 | 54.31 | 59.19 |
| GPT-6 Astra | 71.73 | 46.55 | 55.87 | 60.87 | 56.83 | 58.31 |
| GPT-5.2 | 70.20 | 22.40 | 53.70 | 51.15 | 34.06 | 46.28 |
| Claude Opus 4.6 | 68.62 | 8.30 | 21.11 | 35.67 | 27.82 | 32.09 |
| o3-pro | 37.70 | 2.95 | 17.31 | 24.28 | 14.60 | 19.31 |
| Grok-4.3 | 43.93 | 2.60 | 15.14 | 1.78 | 9.55 | 14.38 |
| *开放权重模型* |  |  |  |  |  |  |
| Kimi-K3 | **82.24** | **50.80** | **61.83** | 41.35 | **51.63** | **57.37** |
| Qwen3.8-27B | 64.03 | 47.85 | 53.41 | **47.88** | 45.69 | 51.70 |
| DeepSeek-V4-Pro | 68.21 | 29.65 | 43.13 | 44.86 | 31.04 | 43.26 |
| Kimi-K2.6 | 53.72 | 24.50 | 39.52 | 33.65 | 37.33 | 37.66 |
| GLM-5.1 | 58.67 | 25.70 | 35.43 | 13.27 | 34.06 | 33.19 |
| Qwen3.6-27B | 43.11 | 29.00 | 46.39 | 27.84 | 18.37 | 32.94 |
| Qwen3.5-9B | 19.90 | 0.70 | 4.71 | 1.15 | 2.33 | 5.65 |
| Mistral-Large-3 | 11.28 | 1.30 | 8.99 | 1.15 | 0.74 | 4.66 |

Claude Opus 5.5 以 67.16% **领跑**总成绩，比 Claude Opus 5 高三分之二个点。Kimi-K3 是最强的**开放权重模型**，与 GPT-6-Astra 相差不到一个点。**业务域同样关键**：Claude Opus 4.6 在零售上拿到 68.62%，在车险上却只有 8.30%。

> 一次漂亮的运行只能告诉你模型有能力做这件事，不能告诉你它会不会每次都做到。所以把每个任务跑 20 次，再看那份得分能剩下多少。

[![Figure-2](https://cdn-uploads.huggingface.co/production/uploads/64b8491203124195cd795cad/DjaLNZKNeU--Xy2WFCvVX.png)](https://cdn-uploads.huggingface.co/production/uploads/64b8491203124195cd795cad/DjaLNZKNeU--Xy2WFCvVX.png)

*图 2：每个模型的单次尝试得分，在重复 20 次之后还剩下多少。*

**只有三个**模型守住了自己 pass@1 得分的大部分：GPT-6 Astra 保留了单次成功率的 78%，Claude Opus 5.5 和 Claude Opus 5 各保留 71%。另一端的 GLM-5.1、Kimi-K2.6 和 DeepSeek-V4-Pro 各自只保住约 8%。

模型**一次能做到**什么与它**每一次都做了什么**之间的差距，就是这件事的全部。

## 你能依赖 agent 背后的那个模型吗

[![Figure-3](https://cdn-uploads.huggingface.co/production/uploads/64b8491203124195cd795cad/NONd2WGm4vtGpsVgs-CIq.png)](https://cdn-uploads.huggingface.co/production/uploads/64b8491203124195cd795cad/NONd2WGm4vtGpsVgs-CIq.png)

*图 3：广度与一致性是分开的两件事。十八个模型中展示了十二个；pass@1 低于 33% 的六个出于可读性被省略。*

**Kimi-K3 的覆盖广度在我们测过的所有模型中最宽。**它至少一次性解决了基准中 **93.89%** 的任务：507 个里 476 个。只有 31 个任务完全难住它，是全场最低。在零售流程上它以 82.24% 的 pass@1 直接领先，超过所有专有模型。

**Kimi-K3 同时也属于最不稳定的一档。**507 个任务里只有 68 个、即 13.41%，在 20 次尝试中全部成功。

Claude Opus 5 正好相反。它至少一次解决的任务更少（79.09%；有 106 个完全难住它），但在每一次尝试中都完成了 **47.53%** 的基准。

**换个更新的模型也解决不了这一点。**Claude Opus 5.5 在每次尝试的平均分上高于 Claude Opus 5，67.16% 对 66.50%，至少一次解决的任务也更多。但它在 20 次尝试中全部通过的任务数完全相同：241 个。标题上浮的半个点准确率，没有换来任何额外的可靠性。

- Kimi-K3 比 Opus 5 多**至少一次解决了 75 个任务**。
- Opus 5 比 Kimi-K3 多**稳定解决了 173 个任务**。

如果你选模型是为了承担会动真实记录的工作，pass@20 并不是你该看的那一列。

## 一致性要付出什么

能力对比通常止步于得分。对任何要真正部署的人来说，相关的问题是：一次成功的工作单元要花费多少。我们把它度量成「每次成功任务尝试的成本」。之所以说任务尝试，是因为基准里的每个任务都会被反复运行、成本按每次尝试发生，所以 pass@1 就是与之匹配的质量分母。

我们从每个模型完整的 507 × 20 跑批中取出记录到的 token 用量，按 [OpenRouter](https://openrouter.ai/)+ 上无折扣的公开列表价计费，还原了促销折扣，并排除了声明采用量化的 endpoint。输入、输出与缓存价格都取自每个模型对应的那一个 provider endpoint。

然后把一次运行的成本除以**成功**的尝试次数：

> 每次成功任务尝试的成本 = 507 次尝试（每个任务一次）的估算成本 ÷ (507 × pass@1)

这是一个用于相互比较的效率指数，不是账单，也不是服务一次生产请求的价格。它衡量的是单次成功的成本，而非一致性。一致性我们接下来单独定价。

**举例：**GPT-5.4 跑 507 次尝试（每个任务一次）花费 $43.49，pass@1 为 65.36%，因此 $43.49 ÷ (507 × 0.6536) = 每次成功任务尝试 $0.131。

### Pareto 成本前沿

当没有任何其他模型能*同时*做到*不比它贵* **且** *精度不低于它*时，这个模型才在前沿上。满足条件的有三个模型；其余每一个模型至少在一条轴上被支配。

[![Figure-4](https://cdn-uploads.huggingface.co/production/uploads/64b8491203124195cd795cad/oGmXYrxoNPJfsQndxlcMD.png)](https://cdn-uploads.huggingface.co/production/uploads/64b8491203124195cd795cad/oGmXYrxoNPJfsQndxlcMD.png)

*图 4：每次成功任务尝试的成本对 pass@1 的关系。带圆圈的点是 Pareto 成本前沿上的模型。*

**前沿分三级台阶。**GPT-5.6 Sol 的**单次成功成本最低**，为 $0.127；GPT-5.4 把 pass@1 提高 3.45 个百分点，每次成功只多花 $0.004；Claude Opus 5.5 再加 1.80 个点，每次成功 $0.276。这三个模型都留在成本前沿线上，因为没有更便宜的模型能达到它们的 pass@1。

Claude Opus 5 是最清楚的例子：每次成功 $0.475、pass@1 66.50%，相比 $0.276、67.16% 的 Claude Opus 5.5，它既更贵又更不准。

### 再给一致性定价

单次成功成本奖励的是便宜且经常答对的模型，它不奖励每次都不错的模型。所以我们也计算「每个可靠任务的成本」：把完整 20 轮跑批的总成本，除以模型在 20 次尝试中全部通过的任务数。

> 每个可靠任务的成本 = 20 轮 × 507 次尝试的估算成本 ÷ 通过 20/20 的任务数

**举例：**GPT-6-Astra 整轮跑批花费 20 × $86.03 = $1,720.60，在每一次尝试中都通过的任务有 231 个，因此 $1,720.60 ÷ 231 = 每个可靠任务 $7.45。

*表 3：在至少有一个 observed 20/20 任务的模型中，每个可靠任务成本最低的九个，由低到高排序。金额为估算值，不是真实云账单。*

| 模型 | 通过 20/20 的任务数 | 估算成本，20 轮 | 每个可靠任务的成本 |
| --- | --- | --- | --- |
| GPT-5.4 | 128 (25.25%) | $869.80 | **$6.80** |
| GPT-6 Astra | 231 (45.56%) | $1,720.60 | $7.45 |
| Claude Opus 5.5 | 241 (47.53%) | $1,880.77 | $7.80 |
| GPT-5.6 Sol | 82 (16.17%) | $800.00 | $9.76 |
| Claude Opus 5 | 241 (47.53%) | $3,206.00 | $13.30 |
| Claude Sonnet 4.6 | 102 (20.12%) | $1,587.60 | $15.56 |
| GPT-5.2 | 44 (8.68%) | $878.00 | $19.95 |
| Kimi-K3 | 68 (13.41%) | $1,406.40 | $20.68 |
| Qwen3.8-27B | 38 (7.50%) | $925.80 | $24.36 |

**现在按一致性来排名。**GPT-5.4 **最便宜**，$6.80，但只有 128 个任务达标。GPT-6 Astra 达到 231 个，每个 $7.45；Claude Opus 5.5 并列最高 241 个，每个 $7.80。

这三个里没有哪个能完全支配其他：每多一个可靠任务都要花更多。Claude Opus 5 同样通过 241 个，但每个要 $13.30，所以 Opus 5.5 直接把它支配掉了。GPT-5.6 Sol 单次成功最便宜（$0.127），可每个可靠任务要 $9.76。拿到一次正确答案最省钱的办法，并不是拿到一个可靠答案最省钱的办法。

## 失败特征

我们给每一条失败的 trace 指派一个确定性的诊断特征，而最可操作的一条结论是：大约五分之四的失败出在工具处理，而不是推理。汇总 [我们论文表 5](https://arxiv.org/pdf/2608.19741) 中的消融实验：

| 失败特征 | 占失败的比例 |
| --- | --- |
| 工具使用 | 79.9% |
| 状态更新错误 | 10.3% |
| 未完整解决用户问题 | 7.0% |
| 没有改变状态的动作 | 2.9% |

这些数字是各模型占比与可观测标签的未加权平均，不是唯一的因果解释。

实践层面的规律很简单：agent 通常能走到足够远、开始尝试这个流程，然后在工具报错、前置条件不满足或查询结果为空时恢复失败。在成为模型问题之前，它是一个重试与错误恢复问题。

难度也随业务域变化：在上文表 2 列出的模型中，零售平均 pass@1 为 59.52%，车险平均只有 33.83%。

**该怎么办。**把 20/20 通过率当成设计输入，而不是判决书。基准用来打分的那同一个信号在生产里同样可得：在提交之前检查最终状态，而不是检查模型对它的总结。

给工具和系统错误分类，让重试只针对那些可恢复的错误。把工具面裁剪到流程真正需要的程度。对你无法低成本回滚的改动要求人工审批。这些做法能带来多少提升，我们还没有在本基准上测量过——而这恰恰是这套环境现在让它变得可测的那类事情。

## 它是怎么工作的

ThinkingBox 是 agent 沙箱，ThinkingBox-Bench 则是用于评测 agent 的数据集基准。本文开头的示意图展示了这个闭环；这里说明每一部分的作用。

[![Figure-1a](https://cdn-uploads.huggingface.co/production/uploads/64b8491203124195cd795cad/elbRGqTXW6PIqci7xcEJN.png)](https://cdn-uploads.huggingface.co/production/uploads/64b8491203124195cd795cad/elbRGqTXW6PIqci7xcEJN.png)

*图 5：上文图 1 中 A 面板的沙箱闭环：隔离的 tool 会话、最终数据库状态、副作用、可执行裁判。*

每个任务都定义了起始 backend 状态、用户目标、可用的 MCP 工具、该业务域的政策，以及针对最终状态的可执行检查。模拟用户持有私有上下文（一个预订号、一个偏好或一个出生日期），只有被问到才放出来。

每次尝试都获得一个隔离的 MCP 会话，状态全新初始化。同一个任务的两次尝试从不共用任何数据库行或缓存的工具状态，这正是 20 次试次对比有意义的前提。

结束时，副作用抽取器推导出实际发生了哪些变化，确定性裁判把它与要求的目标终态对比：接受*任何*产出正确结果的轨迹，拒绝错误、缺失或多余的副作用。对于那些没有干净数据库取值的要求（「agent 是否披露了这一点无法保证？」），用一道窄口径的二元评分问题来处理语义。507 个任务中有 477 个仅依据状态打分；30 个额外带有回复评分项。

信任边界：模型能看到任务、对话和 tool schema。黄金状态、断言、打分内部实现与凭证都留在评测器一侧。

## 自己跑一遍

ThinkingBox 现已上线 Hugging Face，[harness](https://huggingface.co/docs/openenv/environments/thinkingbox) 和[数据集](https://huggingface.co/datasets/microsoft/ThinkingBox-Bench)都在。ThinkingBox-Bench 现在位于 OpenEnv 接口之后，每个结束的 episode 返回一个二元的 pass/fail 奖励。发布的适配器是为评测设计的；其它独立的、非基准的场景可以在训练流程中使用同一套接口。

### 开始之前

已在 Linux 和 WSL 上测试，需要 Python 3.11+、[uv](https://docs.astral.sh/uv/) 和 Docker。你还需要一份检出到指定发布版本的 [thinkingbox-data](https://github.com/microsoft/thinkingbox-data)，以及为 agent、模拟用户和裁判准备的模型 endpoint。一个 endpoint 可以同时承担这三个角色，这是最简的上手方式。OpenEnv 镜像*只启动 OpenEnv API*；其余都由你自己运行。

### 安装

```
# 1. OpenEnv + the ThinkingBox environment
git clone https://github.com/huggingface/OpenEnv
cd OpenEnv
uv sync --project envs/thinkingbox_env --frozen
# 2. The executable benchmark, at the pinned release
git clone https://github.com/microsoft/thinkingbox-data
git -C thinkingbox-data checkout thinkingbox-bench-v1.0
# 3. The ThinkingBox CLI, which provides `tb`
uv tool install "thinkingbox @ git+https://github.com/microsoft/thinkingbox"
```

### 启动 Typesense

在**第二个终端**里启动 Typesense 30.1，并等待它的健康检查通过：

```
mkdir -p .typesense-data
docker run --rm -d --name thinkingbox-typesense \
  -p 8108:8108 \
  -v "$PWD/.typesense-data:/data" \
  typesense/typesense:30.1 \
  --data-dir /data --api-key=Fake --enable-cors
until curl -fsS http://127.0.0.1:8108/health; do sleep 1; done
```

### 启动 MCP 服务器

在**第三个终端**里启动 Session Proxy 和 MCP 服务器。

```
cd OpenEnv
tb mcp-start --host 127.0.0.1 --port 7111 \
  --servers "$PWD/thinkingbox-data/servers/servers.yaml"
curl -fsS http://127.0.0.1:7111/health
```

### 启动 OpenEnv 服务器

回到第一个终端，用一个指明你那三个模型的 ThinkingBox YAML 配置启动 OpenEnv 服务器（[配置指南](https://github.com/microsoft/thinkingbox/blob/main/docs/llm_endpoint_config.md)）：

```
OPENENV_TB_CONFIG="$PWD/thinkingbox.yaml" \
uv run --project envs/thinkingbox_env --frozen server
```

### 检查就绪状态

在运行任何东西之前先用就绪状态做闸门。在它可观测的数据、配置和 Session Proxy 检查都通过之前，该接口返回 503。它无法观测 Typesense，也不会逐个实时探测每个模型 endpoint，所以这两项要你自己另行确认：

```
curl -sS http://127.0.0.1:8000/ready
```

### 给一个 episode 打分

现在给一个真实的 episode 打分。[example_usage.py](https://github.com/huggingface/OpenEnv/blob/main/examples/thinkingbox/example_usage.py) 只做 reset 和列出工具；要跑 agent 动作、副作用与断言，请使用打包好的评测器：

```
echo "- sandbox_external_retail_group1.py:test_case_ST002_001" > one_task.yaml
uv run --project envs/thinkingbox_env thinkingbox-eval \
  one_task.yaml \
  --config "$PWD/thinkingbox.yaml" \
  --output results.jsonl \
  --errors-output errors.jsonl \
  --repeat 1 --message-timeout 1800
```

OpenEnv 适配器会把运行期失败写入一个 errors 附属文件，这样它们可以被重跑，而不是悄悄混进模型的结果里。一份权威结果必须解决或明确计入这些尝试；我们把系统错误计为未成功的试次。

每次运行都以固定的框架 commit、固定的数据发布版本和 bundle hash 为闸门，因此权威结果是可以验证的，而不是靠声称。

## 下一步往哪走

这项工作中有用的部分，不是我们的 pass@1 排行榜，而是这套环境。

如果你正在评测一个会动真实记录的 agent：

- **查一个失败样本。**找一次干净终止却仍然失败的运行，看看数据库里实际改了什么。这会重新界定你自己的 eval 在度量什么。
- **用你自己的模型通过 OpenEnv 复现一个任务**。
- **报告一个重复性指标，并把它定义清楚。**你的用例支撑多大的 k 就用多大的 k；说明你报告的是 best-of-k 还是 every-of-k，以及你是怎么计算的。

更多细节见以下链接：

- **环境：**[envs/thinkingbox_env](https://github.com/huggingface/OpenEnv/tree/main/envs/thinkingbox_env)
- **OpenEnv：**[https://huggingface.co/docs/openenv/environments/thinkingbox](https://huggingface.co/docs/openenv/environments/thinkingbox)
- **框架：**[microsoft/thinkingbox](https://github.com/microsoft/thinkingbox) · [教程](https://github.com/microsoft/thinkingbox/blob/main/docs/tutorial.md)
- **基准：**[microsoft/thinkingbox-data](https://github.com/microsoft/thinkingbox-data) · [v1.0 发布](https://github.com/microsoft/thinkingbox-data/releases/tag/thinkingbox-bench-v1.0)
- **数据集查看器：**[microsoft/ThinkingBox-Bench](https://huggingface.co/datasets/microsoft/ThinkingBox-Bench)
- **论文：**[arXiv:2608.19741](https://arxiv.org/abs/2608.19741) 或 [HF](https://huggingface.co/papers/2608.19741)
- **RL 训练（即将推出）：**[microsoft/thinkingbox-training](https://github.com/microsoft/thinkingbox-training)

ThinkingBox 代码采用 MIT 许可证；基准数据采用 [CDLA-Permissive-2.0](https://cdla.dev/permissive-2-0/)；OpenEnv 环境按 OpenEnv 的 BSD-3-Clause 发布。

免责声明：公开基准里的每个任务都是合成的重构。流程和政策参照真实的 AI agentic 企业模式建模；客户并不是真实的人。

*ThinkingBox 和 ThinkingBox-Bench 由 Microsoft Copilot Studio 团队与 Toloka 合作构建，参与者还包括来自 University of Pittsburgh、Northwestern University、Columbia University 和 UC Irvine、曾在 Microsoft 实习的合作者。欢迎在下方评论区或 [github](https://github.com/microsoft/thinkingbox/discussions) 上提问*

+ OpenRouter 成本快照取自 Sept 20th 2026；Opus 5.5 的价格以 Anthropic 官网为准。

## 本文提及的数据集 1

## 本文提及的论文 1

该作者的其他文章

## Foundry Managed Compute 上的 Hugging Face 模型

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1583646260758-5e64858c87403103f9f1055d.png)

21

July 7, 2026

## Differential Transformer V2

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1583646260758-5e64858c87403103f9f1055d.png)

53

January 20, 2026

### 社区

CyberNativeAI

5 天前

`ST003_006` 把它的通过检查交给了 [`validate_database`](https://github.com/microsoft/thinkingbox-data/blob/fcaba4c1a9debec42fda7f15bf29fe6d6b46c431/dataset/test_case/sandbox_external_retail/sandbox_external_retail_group1.py#L13)。只要结果库与黄金库的哈希不相等，即使 `diff` 为空也算失败。diff 解释一次失败；但它并不决定是否通过。

这个[小型复现](https://github.com/CyberNative-AI/.github/tree/main/notes/thinkingbox-state-check)用四个手工构造的副作用输入来调用已发布的函数。运行 `python3 reproduce.py`。它会校验固定的源码版本并测试给定的哈希；它不计算数据库哈希、不运行 agent，也不复现完整环境。

由 CyberNative AI LLC 借助 AI 完成的源码阅读与示例。

Nomad-link-id

4 天前

有价值的那一刀，是 agent 自报的「完成」与 backend 最终状态之间的差别。

由执行了动作的那个进程自己给出的绿色成功是一份声明，不是一次评分。我希望 eval 依据一个冻结的 oracle 给持久的副作用（工单状态、退款状态、政策引用的字段）打分——并且在叙述一片绿灯而数据库不同意时判为失败。

实际可做的检查：当最终状态夹具是红的，一次运行还能被标记为完成吗？

把图片、音频和视频拖进输入框、粘贴，或

点击此处

.

点击或在此粘贴以上传图片

· [注册](https://huggingface.co/join?next=%2Fblog%2Fmicrosoft%2Fthinkingbox) 或 [登录](https://huggingface.co/login?next=%2Fblog%2Fmicrosoft%2Fthinkingbox) 后可发表评论

点赞

64

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64b8491203124195cd795cad/KWtqxooyzbqzLqdJorOPi.png)](https://huggingface.co/tuhink)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6a27ffbf0ea26227e43a0d29/Hk8XoWHT5braavBTjifaw.jpeg)](https://huggingface.co/Hectozar)
- [![](https://huggingface.co/avatars/821997acf79b7113de576661b1111109.svg)](https://huggingface.co/youngko)
- [![](https://huggingface.co/avatars/1462091a632d06d8b3bdf28a8007f621.svg)](https://huggingface.co/IronTech-Studios)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/YtxawKNmLmMd5dkoGXX6j.png)](https://huggingface.co/bedesign62)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/0K6rX9DTE_L7C_ktLloT7.jpeg)](https://huggingface.co/geminiomnidev)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/647cfece36e109abce3f0090/jTLaPk6En8p608on8sfZ3.png)](https://huggingface.co/jmarceno)
- [![](https://huggingface.co/avatars/2b4cb7be234f99a0df5cea995cf46837.svg)](https://huggingface.co/garyamorris)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/vIHJ-RvmYKUbiydPc5GFl.png)](https://huggingface.co/whitesal)
- [![](https://huggingface.co/avatars/39abcb2f6dba6ec01822dce0b5a7c2ab.svg)](https://huggingface.co/sisoma2)
- [![](https://huggingface.co/avatars/7a38edf6010c8b01c2c2e1e5c21e4b67.svg)](https://huggingface.co/Hivartei)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/reKDqB0OArc5x-li5obfp.png)](https://huggingface.co/Wizzas)

## 本文提及的数据集 1

## 本文提及的论文 1
