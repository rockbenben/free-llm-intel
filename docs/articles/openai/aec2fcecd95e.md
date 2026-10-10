---
vendor: openai
title: GPT-2：6 个月后的跟进
original_title: GPT-2: 6-month follow-up
url: https://openai.com/index/gpt-2-6-month-follow-up
date: 2024-01-16
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 1bde5603cb48
---

OpenAI

August 20, 2019

Publication

# GPT-2：6 个月后的跟进

Read paper

(opens in a new window)

View code

(opens in a new window)

Legal agreement

(opens in a new window)

Illustration: Ben Barry


继 2 月发布小的 [124M 模型⁠](https://openai.com/index/better-language-models/)、5 月以分阶段方式发布中等规模的 [355M 模型⁠](https://openai.com/index/better-language-models/#update)，并与合作伙伴及 AI 社区就模型的滥用风险与社会价值展开后续研究之后，我们现在发布 7.74 亿参数的 GPT-2 语言模型。我们同时发布一份开源的法律协议，让各组织更容易彼此建立模型共享合作，并公布一份技术报告，记录我们在与更广泛的 AI 研究社区协调发布规范方面的经验。

## 我们学到的关键点

**1. 协调很难，但可行**。到目前为止，还没有 1558M 参数语言模型的公开发布，尽管已有多个机构研发出了训练此类系统的条件，或公开讨论过如何训练更大的模型。例如，NLP 开发方 [Hugging Face⁠(opens in a new window)](https://medium.com/huggingface/ethical-analysis-of-the-open-sourcing-of-a-state-of-the-art-conversational-ai-852113c324b2) 的团队，以及 [Allen Institute for Artificial Intelligence⁠(opens in a new window)](https://allenai.org/)（AI2）与华盛顿大学的团队 [都明确采用了与我们类似的分阶段发布方式⁠(opens in a new window)](https://arxiv.org/abs/1905.12616)。自 2 月以来，我们已与五个以上复现了 GPT-2 的团队交流过。[A](https://openai.com/index/gpt-2-6-month-follow-up/#citation-bottom-A)

**2. 人类会被合成文本说服**。我们的研究合作伙伴、康奈尔大学的 Sarah Kreps 和 Miles McCain 的研究在 [*Foreign Affairs*⁠(opens in a new window)](https://www.foreignaffairs.com/articles/2019-08-02/not-your-fathers-bots) 上发表，指出人们认为 GPT-2 生成的合成文本样本几乎和《纽约时报》的真实文章一样可信（某个群体中 72% 的人判定这些文章可信，而真实文章为 83%）。[B](https://openai.com/index/gpt-2-6-month-follow-up/#citation-bottom-B) 此外，AI2/华盛顿大学的研究表明，一个名为"GROVER"的系统撰写的新闻可以 [比人类撰写的宣传更令人信服⁠(opens in a new window)](https://arxiv.org/abs/1905.12616)。这些研究结果让我们对发布语言模型总体更加谨慎。

**3. 检测并不简单**。实践中，我们预期检测器需要以极低的误报率检出相当比例的生成内容。恶意行为者可能采用多种采样技术（包括拒绝采样）或微调模型来规避检测方法。一个实际部署的系统很可能需要在各种生成内容上达到极高准确率（99.9%–99.99%）。我们的研究表明，当前基于机器学习的方法只能达到低到中等 90 多的准确率，而微调语言模型会进一步降低准确率。有一些有前景的可行路径（尤其见"[GROVER⁠(opens in a new window)](https://arxiv.org/abs/1905.12616)"开发者所倡导的那些），但这确实是一个困难的研究问题。我们认为，文本的统计检测需要辅以人类判断和与文本相关的元数据，才能有效对抗语言模型的滥用。

## 合作

我们与四家领先研究机构合作，同时分析新发布的 774M 参数 GPT-2 模型以及尚未发布的完整规模 GPT-2 模型。我们在技术报告中纳入了他们的一些初步结果，他们持续进行的分析将影响 1558M 模型的潜在发布。我们还制定了一份非商业性的法律协议，以促进组织之间的模型共享，并在此发布，帮助其他机构启动类似的共享机制。

- **康奈尔大学**正在研究人类对语言模型生成的数字虚假信息的易受影响程度。
- **蒙特雷国际研究学院**恐怖主义、极端主义与反恐研究中心（CTEC）正在探索恐怖主义者和极端分子如何在网线上滥用 GPT-2。
- **俄勒冈大学**正在开发一系列"偏差探针"来分析 GPT-2 内部的偏差。
- **得克萨斯大学奥斯汀分校**正在研究在领域特定数据集上微调 GPT-2 后其输出的统计可检测性，以及检测方法在不同语言模型之间的迁移程度。

## 未来的发布决策

这些合作伙伴的研究将影响我们未来的发布决策；同时我们也会观察 774M 模型的使用情况，并与研究者和政策制定者讨论语言模型，以理解更大模型相关的考量。作为分阶段发布策略的一部分，我们目前的计划是在几个月后发布 1558M 参数模型，但某合作伙伴的发现或我们 774M 模型被恶意使用，都可能改变这一计划。

我们认为，分阶段发布加基于合作关系的模型共享，很可能是 AI 领域负责任发表的基石，尤其是在强大学生式模型的语境下。大模型固有的问题会随时间增加而非减少。我们希望在 GPT-2 上的工作——我们在即将 [发布的⁠(opens in a new window)](https://cdn.openai.com/GPT_2_August_Report.pdf) 技术报告中有更多讨论——能为 AI 社区提供一些可借鉴的证据，用于思考 AI 研究某些领域固有的发表难题。

### 时间线

- **2019 年 1 月**OpenAI 发布了关于 GPT-2 的 [博客⁠](https://openai.com/index/better-language-models/) 和 [论文⁠(opens in a new window)](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)。发布了小参数（124M）GPT-2 模型。
- **2019 年 2 月**Partnership on AI 与 OpenAI 联合主办了一场晚餐会，[讨论发表规范⁠(opens in a new window)](https://www.partnershiponai.org/when-is-it-appropriate-to-publish-high-stakes-ai-research/)，随后发布了一篇总结讨论内容的博客。
- **2019 年 4 月**发布了中等参数（355M）模型。发布了大规模模型输出的数据集。发布了一个检测基线，帮助人们理解如何检测像 GPT-2 这样模型的输出。原始博客 [被更新⁠](https://openai.com/index/better-language-models/#update) 以反映这些变化。Adam King [上线⁠(opens in a new window)](https://twitter.com/adamdanielking/status/1125831730848571392?lang=en) "TalktoTransformer.com"，为人们提供可体验新发布模型的界面。Hugging Face 发布了一个基于 GPT-2 模型的对话式 AI 演示，讨论了发布决策中的一些伦理考量，并 [决定不发布大 GPT-2 模型⁠(opens in a new window)](https://medium.com/huggingface/ethical-analysis-of-the-open-sourcing-of-a-state-of-the-art-conversational-ai-852113c324b2)。华盛顿大学与 Allen Institute for AI Research 的研究者 [公布了 GROVER⁠(opens in a new window)](https://arxiv.org/abs/1905.12616)，一个 GPT-2 式语言模型；他们没有发布大版本模型，并对这类模型输出的检测开展了研究。
- **2019 年 5 月**[OpenAI 在国会作证⁠(opens in a new window)](https://www.youtube.com/watch?v=tdLS9MlIWOk)，谈合成媒体的影响，其中讨论了合成文本。DeepMind 在其近期关于无监督学习的 [讨论⁠(opens in a new window)](https://deepmind.com/blog/article/unsupervised-learning) 中谈及 GPT-2 以及为生成式模型制定恰当发表规范的重要性。OpenAI 与 [Partnership on AI⁠(opens in a new window)](https://www.partnershiponai.org/) 启动了一项关于 AI 研究发表规范的合作研究。我们正尝试与多元的 AI 研究机构合作，梳理科学家在发表前可能想问的问题，以及可用于做发表决策的潜在框架。
- **2019 年 6 月**[DeepTabNine 开发了一款⁠(opens in a new window)](https://tabnine.com/blog/deep) 基于 GPT-2 的代码自动补全工具。[Multi-turn Dialogue Response Generation with Autoregressive Transformer Models⁠(opens in a new window)](https://arxiv.org/abs/1908.01841)[GLTR: Statistical Detection and Visualization of Generated Text⁠(opens in a new window)](https://www.aclweb.org/anthology/P19-3019)
- **2019 年 7 月**Thoughtful Technology Project 和剑桥大学的研究者发表了一篇工作论文，题为"[Reducing malicious use of synthetic media research: Considerations and potential release practices for machine learning⁠(opens in a new window)](https://arxiv.org/abs/1907.11274)"。[Hello, It's GPT-2—How Can I Help You? Towards the Use of Pretrained Language Models for Task-Oriented Dialogue Systems⁠(opens in a new window)](https://arxiv.org/abs/1907.05774)AI 初创公司 AI21 Labs 发布了 [HAIM⁠(opens in a new window)](https://www.ai21.com/haim-post)，一个神经文本生成器；他们只发布了一个 345M 的模型变体，"规模上与公开发布版本的 Grover 和 GPT-2 相当"。NVIDIA Research [训练了⁠(opens in a new window)](https://nv-adlr.github.io/MegatronLM) 一个 83 亿参数的 GPT-2 模型。发布了更大参数（774M）的模型。

- [GPT](https://openai.com/research/index/?tags=gpt)
- [Community & Collaboration](https://openai.com/research/index/?tags=community-collaboration)
- [Reasonings & Policy](https://openai.com/research/index/?tags=reasoning-policy)
- [Ethics & Safety](https://openai.com/research/index/?tags=ethics-safety)

## 脚注

- A这类对话很困难，因为它涉及坦诚地讨论专有系统，而且不清楚在具体机构里应该联系谁来讨论此类模型，机构之间讨论未发表研究的恰当流程是什么。
- B这些样本是通过一种"人在回路"的流程生成的，用于模拟当代虚假信息行动：由人生成样本，并周期性地挑选一部分用于向人们展示。








