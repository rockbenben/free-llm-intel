---
vendor: openai
title: 用过程监督改进数学推理
original_title: Improving mathematical reasoning with process supervision
url: https://openai.com/index/improving-mathematical-reasoning-with-process-supervision
date: 2023-10-19
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 29fe1936287e
---

OpenAI

May 31, 2023

Publication

# 用过程监督改进数学推理

Read paper

(opens in a new window)

Browse samples

Download dataset

(opens in a new window)


我们训练了一个模型，在数学解题上取得新的 SOTA：做法是给每一段正确的推理步骤打奖励（"过程监督"），而不只是给最终正确答案打奖励（"结果监督"）。除了相对结果监督提升表现之外，过程监督还有一个重要的对齐收益：它直接训练模型产出被人类认可的思维链（chain-of-thought）。

## 引言

近年来，大型语言模型在执行复杂多步推理上的能力有了大幅提升。然而，即使是当前最强的模型也仍然会犯逻辑错误——即所谓的*幻觉（hallucinations）*。缓解幻觉是迈向构建对齐 AGI 的关键一步。

我们可以训练奖励模型来检测幻觉，方式有两种：*结果监督*（依据最终结果提供反馈）或 *过程监督*（对思维链中的每一步单独提供反馈）。基于以往工作[1](https://openai.com/index/improving-mathematical-reasoning-with-process-supervision/#citation-bottom-1)，我们以 MATH 数据集[2](https://openai.com/index/improving-mathematical-reasoning-with-process-supervision/#citation-bottom-2) 为试验田对这两种方法进行了细致对比。我们发现，即便以结果作为评判口径，过程监督也能显著带来更好的表现。为了鼓励相关研究，我们公开了我们完整的过程监督数据集。

## 对齐意义

过程监督相比结果监督在对齐上有若干优势。它直接因模型遵循对齐的思维链而给予奖励，因为过程中每一步都获得精确的监督。过程监督也更可能产生可解释的推理，因为它鼓励模型沿着人类认可的流程走。相比之下，结果监督可能奖励一个并未对齐的过程，且通常更难审查。

在某些情况下，为 AI 系统采用更安全的方法会带来表现下降[3](https://openai.com/index/improving-mathematical-reasoning-with-process-supervision/#citation-bottom-3)，这一代价被称为 *对齐税（alignment tax）*。一般而言，任何对齐税都可能阻碍对齐方法的采纳，因为存在部署最强模型的压力。下文结果显示，至少在数学领域，过程监督实际上带来负的对齐税——不仅没有成本反而有增益。这可能提升过程监督的采纳率，我们相信这会带来正向的对齐副作用。

## 求解 MATH 问题


我们使用 MATH 测试集上的问题来评估过程监督和结果监督的奖励模型。我们对每道题生成大量解，然后按每个奖励模型挑出排序最高的那一个解。图中横轴为每题考虑多少解，纵轴为最终答对的比率。可以看到，过程监督奖励模型不仅在整体上都表现更好，而且随着每题考虑的解数量增多，性能差距还在进一步拉大。这显示过程监督奖励模型要可靠得多。

我们在下方展示 10 道题及其解，并附带关于奖励模型优点与不足的评论。


这些结果能在多大程度上泛化到数学之外仍未可知，我们认为未来的工作应当探索过程监督在其他领域的影响。如果这些结果能泛化，我们也许会发现过程监督兼得两全——一个比结果监督既更有效率也更对齐的方法。

- [GPT](https://openai.com/research/index/?tags=gpt)
- [Language](https://openai.com/research/index/?tags=language)
- [Learning Paradigms](https://openai.com/research/index/?tags=learning-paradigms)
- [Reasonings & Policy](https://openai.com/research/index/?tags=reasoning-policy)

## 参考文献

- 1Uesato, J., Kushman N., Kumar R., Song F., Siegel N., Wang L., Creswell A., Irving G. and Higgins, I., 2022. Solving math word problems with process- and outcome-based feedback. arXiv preprint arXiv:2211.14275.
- 2Hendrycks D., Burns C., Kadavath S., Arora A., Basart S., Tang E., Song D. and Steinhardt J., 2021. Measuring Mathematical Problem Solving With the MATH Dataset. arXiv preprint arXiv:2103.03874.
- 3Ouyang L., Wu J., Jiang X., Almedia D., Wainwright C.L., Mishkin P., Zhang C., Agarwal S., Slama K., Ray A., Schulman J., Hilton J., Kelton F., Miller L., Simens M., Askell A., Welinder P., Christiano P., Leike J. and Lowe R., 2022. Training language models to follow instructions with human feedback. arXiv preprint arXiv:2203.02155.

## 作者

Karl Cobbe, Hunter Lightman, Vineet Kosaraju, Yura Burda, Harri Edwards, Jan Leike, Ilya Sutskever

## 贡献者

Bowen Baker, Teddy Lee, John Schulman, Greg Brockman, Kendra Rimbach, Hannah Wong, Thomas Degry








