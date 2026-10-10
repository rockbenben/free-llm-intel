---
vendor: openai
title: WebGPT：通过网页浏览提升语言模型的事实准确性
original_title: WebGPT: Improving the factual accuracy of language models through web browsing
url: https://openai.com/index/webgpt
date: 2024-01-12
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: ec98289c703f
---


December 16, 2021

Publication

# WebGPT：通过网页浏览提升语言模型的事实准确性

我们微调了 GPT-3，让它能用一个基于文本的浏览器，更准确地回答开放式问题。




Browse samples


我们微调了 GPT-3，让它能用一个基于文本的浏览器，更准确地回答开放式问题。我们的原型模仿人类在网上研究问题的方式——提交搜索查询、跟随链接、上下滚动网页。它被训练为引用自己的信息来源，从而让反馈事实准确性的工作变得更容易。我们对开发更诚实的 AI 感到兴奋[1](https://openai.com/index/webgpt/#citation-bottom-1)，但挑战仍然存在，比如如何应对不熟悉的问题类型。

像 GPT-3 这样的语言模型对许多任务都有用，但在需要冷门现实世界知识的任务中，它们往往会"幻觉（hallucinate）"信息[2](https://openai.com/index/webgpt/#citation-bottom-2), [3](https://openai.com/index/webgpt/#citation-bottom-3)。为解决这一问题，我们教会 GPT-3 使用一个基于文本的浏览器。模型会拿到一个开放式问题以及浏览器状态的摘要，并必须发出诸如"搜索 ……"、"页面内查找：……"或"引用：……"之类的命令。通过这种方式，模型从网页上收集段落，再用这些段落组织回答。

模型基于 GPT-3 微调而来，用的是我们过去用过的 [同⁠](https://openai.com/index/deep-reinforcement-learning-from-human-preferences/)[样⁠](https://openai.com/index/fine-tuning-gpt-2/)[的⁠](https://openai.com/index/learning-to-summarize-with-human-feedback/)[方⁠](https://openai.com/index/summarizing-books/) 法。我们先训练模型模仿人类演示——这让它具备用文本浏览器回答问题的能力。然后我们通过训练一个奖励模型来预测人类偏好，并使用强化学习或拒绝采样来对其优化，从而提升模型回答的助益性与准确度。


## ELI5 结果

我们的系统被训练来回答 ELI5[4⁠](https://openai.com/index/webgpt/#rf4) 上的问题——这是一个从"Explain Like I'm Five"（像给五岁小孩解释）板块抓取的开放式问题数据集。我们训练了三个不同的模型，分别对应三档推理时算力预算。我们表现最好的模型给出的回答，与人类演示写的答案相比，56% 的情况下被人更喜欢，事实准确度接近。虽然用来训练模型的演示数据同样是这些数据，但我们能借助人类反馈改进模型回答，从而超过它们。


## TruthfulQA 结果

对于训练分布内的问题，我们最好的模型给出的答案在事实准确度上与人类所写的平均而言相当。然而，分布外的鲁棒性是一个挑战。为了探测这一点，我们在 TruthfulQA[5](https://openai.com/index/webgpt/#citation-bottom-5) 上评估模型——这是一个通过对抗方式构建的、由短问题组成的数据集，用来测试模型是否会掉入常见误解之类的陷阱。答案同时按"真实性"和"信息量"打分，两者之间会相互制约（例如，"我没有评论"被认为是真实但不信息丰富）。

我们的模型在 TruthfulQA 上超过 GPT-3，并展现出更优的缩放特性。然而我们的模型仍落后于人类表现，部分原因是它们有时会引用不太可靠的来源（如上面关于鬼魂的问题所示）。我们希望能用对抗训练之类的技术降低这类失败的频率。


## 评估事实准确度

为了给出反馈以改进事实准确度，人类必须能够评估模型所产生主张的事实准确性。这可能极其困难——因为主张可能是技术性的、主观的或含糊的。正因如此，我们要求模型引用自己的来源[6](https://openai.com/index/webgpt/#citation-bottom-6)。这让人类能通过检查一个主张是否*由一个可靠来源支持*来评估事实准确性。这不仅让任务更容易处理，也让判断更少歧义，这对降低标注噪声非常重要。

然而，这一做法也引发了若干问题。什么让一个来源显得可靠？什么样的主张足够显而易见、无需支持？在事实准确性的评估与连贯性等其他准则之间应该做什么权衡？这些都是困难的判断。我们不认为我们的模型已经学到了这些细微之处，因为它仍然会犯基础错误。但我们预期，随着 AI 系统变强，这类决策会变得更重要，需要跨学科研究，制定既实用又认识论上可靠的准则。我们也预期透明度等进一步的考量会很重要[1](https://openai.com/index/webgpt/#citation-bottom-1:2)。

最终，仅仅让模型引用来源不足以评估事实准确性。一个足够强的模型会挑拣它预计人类会觉得有说服力的来源，即使这些来源并不反映对证据的公允评估。已经有迹象显示这类事情在发生（见上面关于船的问题）。我们希望通过 [辩论（debate）⁠](https://openai.com/index/debate/) 之类的方法来缓解这一问题。

## 部署与训练风险

尽管我们的模型总体上比 GPT-3 更诚实（生成错误陈述的频率更低），但仍然存在风险。带引用的回答往往让人感觉到一种权威感，这可能掩盖我们的模型仍在犯基础错误的事实。模型也倾向于强化用户既有的信念。我们正在研究如何最好地应对这些及其他担忧。

除了这些部署风险，我们的做法在 *训练时* 也因让模型可访问网络而引入了新的风险。我们的浏览环境并不允许完全的网页访问，但允许模型向 [Microsoft Bing Web Search API](https://www.microsoft.com/en-us/bing/apis/bing-web-search-api) 发送查询，并跟随网上已存在的链接——这会有副作用。以我们使用 GPT-3 的经验看，模型看起来还远没有能力去危险地利用这些副作用。然而，这些风险会随模型能力上升，我们正在建立内部防护以应对它们。

## 结论

人类反馈以及像网页浏览器这样的工具，为走向稳健诚实、通用 AI 系统提供了一条有前景的路径。我们当前的系统在处理困难或不熟悉的情况时仍然吃力，但在这一方向上仍代表着显著进展。

*如果你想帮助我们构建更助益、更诚实的 AI 系统，*[*我们正在招人*](https://boards.greenhouse.io/openai/jobs/4247042004?gh_src=5600abde4us)*！*


## 参考文献

- 1O. Evans, O. Cotton-Barratt, L. Finnveden, A. Bales, A. Balwit, P. Wills, L. Righetti, and W. Saunders. Truthful AI: Developing and governing AI that does not lie. arXiv preprint [arXiv:2110.06674](https://arxiv.org/abs/2110.06674), 2021.
- 2J. Maynez, S. Narayan, B. Bohnet, and R. McDonald. On faithfulness and factuality in abstractive summarization. arXiv preprint [arXiv:2005.00661](https://arxiv.org/abs/2005.00661), 2020.
- 3K. Shuster, S. Poff, M. Chen, D. Kiela, and J. Weston. Retrieval augmentation reduces hallucination in conversation. arXiv preprint [arXiv:2104.07567](http://arxiv.org/abs/2104.07567), 2021.
- 4A. Fan, Y. Jernite, E. Perez, D. Grangier, J. Weston, and M. Auli. ELI5: Long form question answering. arXiv preprint [arXiv:1907.09190](https://arxiv.org/abs/1907.09190), 2019.
- 5S. Lin, J. Hilton, and O. Evans. TruthfulQA: Measuring how models mimic human falsehoods. arXiv preprint [arXiv:2109.07958](https://arxiv.org/abs/2109.07958), 2021.
- 6D. Metzler, Y. Tay, D. Bahri, and M. Najork. Rethinking search: Making experts out of dilettantes. arXiv preprint [arXiv:2105.02274](https://arxiv.org/abs/2105.02274), 2021.

## 作者

Jacob Hilton, Reiichiro Nakano, Suchir Balaji, John Schulman

## 致谢

感谢我们的论文共同作者：Jeff Wu, Long Ouyang, Christina Kim, Christopher Hesse, Shantanu Jain, Vineet Kosaraju, William Saunders, Roger Jiang, Karl Cobbe, Tyna Eloundou, Gretchen Krueger, Kevin Button, Matthew Knight 和 Benjamin Chess。

感谢参与本次发布并给予反馈的人：Steven Adler, Sam Altman, Beth Barnes, Miles Brundage, Kevin Button, Steve Dowling, Alper Ercetin, Matthew Knight, Gretchen Krueger, Ryan Lowe, Andrew Mayne, Bob McGrew, Mira Murati, Richard Ngo, Jared Salzano, Natalie Summers 和 Hannah Wong。

感谢 Surge AI 团队帮助我们收集数据，也感谢我们所有的合同工提供的演示与对比——没有他们，本项目无法完成。
