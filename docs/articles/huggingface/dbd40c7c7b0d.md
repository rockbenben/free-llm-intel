---
vendor: huggingface
title: Open LLM Leaderboard：DROP 深度剖析
original_title: 'Open LLM Leaderboard: DROP deep dive'
url: https://huggingface.co/blog/open-llm-leaderboard-drop
date: 2025-04-27
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Open LLM Leaderboard：DROP 深度剖析

本文另有[简体中文](https://huggingface.co/blog/zh/open-llm-leaderboard-drop)版本。

最近，[三个新基准](https://twitter.com/clefourrier/status/1722555555338956840)加入了 [Open LLM Leaderboard](https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard)：Winogrande、GSM8k 和 DROP，使用的是在 [EleutherAI Harness](https://github.com/EleutherAI/lm-evaluation-harness/) 中复现的原始实现。粗略一看 DROP 的分数就发现有些不对劲：绝大多数模型的 f1 分数在 100 分制下不到 10 分！我们做了深入研究以弄清缘由，一起来看看我们发现什么！

## 初步观察

DROP（Discrete Reasoning Over Paragraphs）是一项评估，要求模型先从英文段落中提取相关信息，再对其执行离散推理步骤（例如对条目排序或计数以得到正确答案，例子见下表）。使用的指标是自定义的 f1 与精确匹配分数。

Examples of reasoning and paragraph from the original article.

三周前我们把它加入 Open LLM Leaderboard，随即观察到预训练模型的 f1 分数呈现出一个意外趋势：把 DROP 分数与榜单原始平均分（ARC、HellaSwag、TruthfulQA 和 MMLU 的平均，是整体模型性能的合理代理）画在一起时，我们预期 DROP 分数会与它相关（更好的模型表现更好）。然而这只在少数模型上成立，其余所有模型的 DROP f1 分数都低得异常——不到 10。

DROP 分数中有两种趋势：一部分跟随平均分（对角线），另一部分卡在 5 左右（图右侧的竖线）。

## 归一化的疑点

在对这些意外行为的初步深入排查中，我们注意到归一化（normalization）步骤可能未按预期工作：某些情况下，当归一化时，如果正确的数字答案后面直接跟着除空格以外的空白字符（如换行符），它会被忽略。看一个例子：生成内容为 `10\n\nPassage: The 2011 census recorded a population of 1,001,360`，标准答案（gold）是 `10`。

归一化对生成和 gold 都分几步进行：

- **按分隔符切分** `|`、`-` 或   生成序列的开头 `10\n\nPassage:` 不含这些分隔符，因此在这一步被视为单个实体。
- **去标点** 第一个 token 变成 `10\n\nPassage`（`:` 被移除）
- **数字统一化** 每个可转换为 float 的字符串被视为数字，转成 float 再转回字符串。`10\n\nPassage` 保持不变，因为它无法转成 float；而 gold `10` 变成 `10.0`。
- **其他步骤** 随后还有很多其他归一化步骤（去冠词、去其他空白等），我们最初的示例变成 `10 passage 2011.0 census recorded population of 1001360.0`。

然而，总分不是按字符串计算，而是按从字符串提取的词袋（BOW），这里是 `{'recorded', 'population', 'passage', 'census', '2011.0', '1001360.0', '10'}`，再与同样按上述方式归一化的 gold BOW `{10.0}` 比较。可以看到，它们没有交集——尽管模型预测了正确的输出！

总结：如果一个数字后面跟着除普通空格以外的任何空白字符，它就不会通过数字归一化，因此当 gold 也是数字时永远无法匹配！这第一个问题很可能已经严重干扰分数，但它显然不是 DROP 分数如此之低的唯一因素。我们决定继续调查。

## 深入研究结果

我们把调查扩大，[Zeno](https://zenoml.com) 的朋友加入我们，并对结果[进行了远更彻底的探索](https://hub.zenoml.com/report/1255/DROP%20Benchmark%20Exploration)，研究了 5 个能代表我们在 DROP 分数中注意到问题的模型：falcon-180B 和 mistral-7B 表现低于预期；Yi-34B 和 tigerbot-70B 在 DROP 上表现很好且与其平均分相关；facebook/xglm-7.5B 介于两者之间。

如果你想自己尝试分析，可以在 [Zeno 项目](https://hub.zenoml.com/project/2f5dec90-df5e-4e3e-a4d1-37faf814c5ae/OpenLLM%20Leaderboard%20DROP%20Comparison/explore?params=eyJtb2RlbCI6ImZhY2Vib29rX194Z2xtLTcuNUIiLCJtZXRyaWMiOnsiaWQiOjk1NjUsIm5hbWUiOiJmMSIsInR5cGUiOiJtZWFuIiwiY29sdW1ucyI6WyJmMSJdfSwiY29tcGFyaXNvbk1vZGVsIjoiVGlnZXJSZXNlYXJjaF9fdGlnZXJib3QtNzBiLWNoYXQiLCJjb21wYXJpc29uQ29sdW1uIjp7ImlkIjoiYzJmNTY1Y2EtYjJjZC00MDkwLWIwYzctYTNiNTNkZmViM2RiIiwibmFtZSI6ImVtIiwiY29sdW1uVHlwZSI6IkZFQVRVUkUiLCJkYXRhVHlwZSI6IkNPTlRJTlVPVVMiLCJtb2RlbCI6ImZhY2Vib29rX194Z2xtLTcuNUIifSwiY29tcGFyZVNvcnQiOltudWxsLHRydWVdLCJtZXRyaWNSYW5nZSI6W251bGwsbnVsbF0sInNlbGVjdGlvbnMiOnsic2xpY2VzIjpbXSwibWV0YWRhdGEiOnt9LCJ0YWdzIjpbXX19) 试试！

Zeno 团队发现了两个更令人担忧的现象：

- 没有一个模型在浮点数答案上得到正确结果
- 生成长答案的高质量模型反而 f1 分数更低

此时我们相信这两个失败案例其实源于同一个根因：用 `.` 作为停止词 token 来结束生成（stop token）：

- 浮点数答案在生成完成前被系统性地截断
- 更高质量、试图贴合 few-shot prompt 格式的模型会生成 `Answer\n\nPlausible prompt for the next question.`，只在第一个 `.` 处、于真实答案之后的合理续写 prompt 中停止，因此生成了过多词，导致 f1 分数很差。

我们假设：把 `\n`（而非 `.`）用作生成结束停止词，可同时解决这两个问题。

## 更换生成结束 token

于是我们试一试！我们在现有结果上研究了用 `\n` 作为生成结束 token 的效果：把生成的答案按其中第一个 `\n` 切分（若存在），再重新计算分数。*注意这只是正确结果的近似，因为它无法修复那些在 `.` 上被过早截断的答案（例如浮点数答案）——但它也不会给任何模型不公平的优势，因为所有模型都受此问题影响。不过在不需要重跑模型的前提下（我们想尽快向社区通报），这已是我们能做的最好。*

我们得到的结果如下——按 `\n` 切分后与其他分数、进而与整体性能高度相关。

可以看到橙色（按新字符串计算的分数）与平均性能的相关性好得多。

## 接下来怎么办？

快速计算表明，重跑所有模型的完整评估成本相当高（完整更新花了 8 年 GPU 时间，其中很大一部分消耗在 DROP 上）。我们估算了只重跑失败示例的成本。

在 10% 的案例中，gold 答案是浮点数（例如 `12.25`），模型预测以正确开头开始（对我们这个例子是 `12`）但在 `.` 处被截断——如果生成继续下去，这些预测很可能本来就是对的。我们肯定需要重跑它们！我们的估算没有计入以数字结尾、可能被中断的生成句（其余生成的 40%），也没有计入被归一化弄乱的任何预测。

要得到正确结果，我们就需要重跑超过 50% 的示例——巨大的 GPU 时间！我们得确信这次要跑的实现是正确的。

与出色的 EleutherAI 团队讨论后（在 [GitHub](https://github.com/EleutherAI/lm-evaluation-harness/issues/978) 和私下都聊了，他们带我们梳理代码、帮助我们的调查），事情非常清楚：LM Eval Harness 的实现严格遵循"官方 DROP"代码：因此需要为该基准的评估开发一个新版本！**我们因此决定，把 DROP 从 Open LLM Leaderboard 移除，直到新版本出现。**

这次调查的一个收获，是社区众多眼睛协作调查一个基准的价值——它能发现此前被遗漏的错误。开源、社区与公开开发的力量再次彰显：它让我们能够透明地调查一个已存在数年的基准上某个问题的根本原因。

我们希望社区感兴趣成员与从事 DROP 评估研究的学者联手，同时修复它的评分与归一化。我们希望它重新可用，因为数据集本身确实非常有趣精彩。欢迎在[这个 issue](https://github.com/EleutherAI/lm-evaluation-harness/issues/1050) 上反馈我们应该如何评估 DROP。

感谢许多指出 DROP 分数问题的社区成员，也衷心感谢 EleutherAI Harness 与 Zeno 团队在此问题上的大力帮助。
