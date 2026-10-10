---
vendor: huggingface
title: UK AISI 与 EvalEval 如何让基准测试结果可复现
original_title: How UK AISI and EvalEval Are Making Benchmark Results Reproducible
url: https://huggingface.co/blog/evaleval-aisi
date: 2026-09-28
lang: zh
captured: 2026-10-10
extractor: readability-v1
translator: agent
status: translated
body_sha: 720cf4d8bcec
---

# UK AISI 与 EvalEval 如何让基准测试结果可复现

发布于

2026 年 9 月 22 日

在 GitHub 上更新此内容

点赞

28

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6413251362e6057cbb6259bd/k8UMg_tnorG_uCXidybZ7.jpeg)](https://huggingface.co/evijit)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/vnmbzcTMfdqnuzbONym__.png)](https://huggingface.co/dariocava)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1583857146757-5e67bdd61009063689407479.jpeg)](https://huggingface.co/clem)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1594144055859-5ee3a7cd2a3eae3cbdad1305.jpeg)](https://huggingface.co/yjernite)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/66e691d778f2c37966d1d614/1MJg4zMGny3kmC5TPdjN3.png)](https://huggingface.co/DVRRK)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/69d94b034b0d592e906bc968/8HDc1xHMRnIlqJDI6CG_4.jpeg)](https://huggingface.co/vzn2auto)

Avijit Ghosh

evijit

evaleval

Jenny Chim

j-chim

evaleval

Deep Joshi

deeplumiere

evaleval

Srishti

srishtiy

evaleval

Matt Kennedy

wmmkennedy

evaleval

Irene Solaiman

irenesolaiman

evaleval

Jessica McFadyen

mcfadyen-aisi

ai-safety-institute

Lynn Tan

lynn-aisi

ai-safety-institute

Coz

coz-aisi

ai-safety-institute

[EvalEval Coalition](https://evalevalai.com/) 很高兴地分享，[UK AI Security Institute（AISI）](https://www.aisi.gov.uk/)正在使用 EvalEval 的基础设施来公开分享评测结果，支持更可复现、更可验证的评测科学。

AISI 与 EvalEval 此前已在一项研究的成果上合作，这项工作始于 [NeurIPS 2025 期间的一场联合 workshop](https://evalevalai.com/events/workshop-2025/)，来自该研究所的反馈也帮助塑造了 [Every Eval Ever（EEE）schema](https://evalevalai.com/projects/every-eval-ever/)。这次合作的下一阶段是把这套共享基础设施真正投入使用。

## 为什么可复现的评测报告很重要

随着 AI 部署加速，评测正越来越重要地成为关于模型与系统性能的证据来源。但结果分散在众多格式、平台和渠道上，而且常常缺少足以复现的信息。而重新跑一遍这些评测本身可能就贵得令人却步。

EvalEval 的使命是通过一套共享的报告 schema [Every Eval Ever](https://evalevalai.com/projects/every-eval-ever/)，以及一个开放平台 [Evaluation Cards](https://evalcards.evalevalai.com/) 来改善这个生态——后者把评测结果与解读它所需的信息收进一个共同的结构里。

这自然承接了 AISI 在评测效率方向上的工作 [OptStop](https://arxiv.org/abs/2608.14425)，在统计严谨性方向上的工作 [HiBayES](https://www.aisi.gov.uk/blog/hibayes-improving-llm-evaluation-with-hierarchical-bayesian-modelling)，以及在 transcript 分析与能力激发等方向上推动的标准化。AISI 与 EvalEval 正在一起诊断评测报告中的缺口，并构建共享基础设施来填补它们。

## AISI 分享了什么

transcript 级别的透明度不只对可复现性重要，对分析和诊断同样重要。在这次合作的这个阶段，AISI 在合适的情况下，通过 Evaluation Cards 公开其对外报告的评测方法与结论。这次发布包含论文主实验中五个基准的已验证结果、上下文与配置信息：

- HealthBench
- FrontierMath
- Humanity's Last Exam
- SWE-Bench Pro
- Terminal-Bench 2.0

这些结果覆盖六个前沿模型：Claude Opus 4、Claude Opus 4.5、Claude Opus 4.6、GPT-5、GPT-5.2 和 GPT-5.4。发布内容还包含两项相关 cyber 评测的结果——Cyber CTFs 与 The Last Ones——它们使用一组不同、部分重叠的模型。这些数据伴随 AISI 的论文[*How Inference Compute Shapes Frontier LLM Evaluation*](https://arxiv.org/abs/2606.17930)，该论文研究基准表现如何依赖 inference 阶段的算力与评测协议。

*Humanity's Last Exam 上的表现会随评测协议与 inference 算力而变化。每条曲线展示在给定 token 数之内已尝试任务中被解出部分的累计占比，每个任务取最早观测到的那次成功。当模型在每次尝试后收到来自 oracle 的正确性反馈时，随着 token 用量增加，它们仍会持续解出更多任务。*

当结果连同设置信息一起公开发布时，研究者和从业者就能更细致地检视单项研究，并在更大的生态范围内横向比较结论。当其他报告缺少这些细节时，像 AISI 这样的发布提供了已验证的参照点，用于在具体情境中解读评测——例如帮助研究者理解设置上的选择可能如何影响报告出来的性能。随着更多评测方采用 EEE，这类开放比较能够为更广泛、更可靠的元研究（meta-research）提供支撑。

*AISI 的 Terminal-Bench 2.0 结果，与同一批模型在其他评测设置下报告的其他评测结果并列。*

我们对这一采纳感到兴奋，也期待与 AISI 及其他 AI 评测机构进一步标准化并共享评测。

## 为共同使命出力

- **模型开发者：**[报告已验证的评测结果](https://evalcards.evalevalai.com/help/get-verified)。
- **评测开发者：**使用 [Every Eval Ever schema](https://github.com/evaleval/every_eval_ever) 报告基准与 run 数据。
- **评测、治理与政策研究者：**按基准或模型[浏览 Evaluation Cards](https://evalcards.evalevalai.com/)，或用它来考察评测报告的整体现状。

## 关于 EvalEval Coalition

EvalEval Coalition 是一个研究社区，为评测生态发展与科学立足的研究以及稳健的部署基础设施。其目标是改进评测科学、回应「在记录评测的适用性与效用方面缺乏共识」这一问题，并扩大对那些关乎科学研究与政策分析的影响的覆盖。

该联盟的旗舰项目包括 [Every Eval Ever](https://evalevalai.com/projects/every-eval-ever/)——一套用于评测结果的共享 schema 与仓库，以及 [Evaluation Cards](https://evalevalai.com/projects/eval-cards/)——它把基准元数据、评测 run 数据与模型元数据组合成可解读的记录。两者一起，让人更容易判断那些看起来相近的分数实际上是在有实质差异的条件下产生的。

## 关于 UK AI Security Institute

[UK AI Security Institute](https://www.aisi.gov.uk/) 是英国政府科学、创新与技术部（Department for Science, Innovation and Technology）旗下的一个研究组织。它的使命是为政府配备对先进 AI 所构成风险的科学理解。AISI 开展研究并建设基础设施，以理解先进 AI 的能力与影响、开发并测试缓解措施、为政策提供依据。

## 延伸阅读

- [*How Inference Compute Shapes Frontier LLM Evaluation*](https://arxiv.org/abs/2606.17930)
- [HiBayES: Improving LLM evaluation with hierarchical Bayesian modelling](https://www.aisi.gov.uk/blog/hibayes-improving-llm-evaluation-with-hierarchical-bayesian-modelling)
- [HiBayES 论文](https://arxiv.org/abs/2505.05602)
- [OptStop 论文](https://arxiv.org/abs/2608.14425)
- [Every Eval Ever](https://evalevalai.com/projects/every-eval-ever/)
- [Evaluation Cards](https://evalcards.evalevalai.com/)

我们博客的其他文章

evaluation

community

leaderboard

## 在 Hugging Face 的 Model Pages 上展示 Every Eval Ever 的结果

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6238f87f35384c2bcccb3889/vvQDZb934B36xPt_Gokjh.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6413251362e6057cbb6259bd/k8UMg_tnorG_uCXidybZ7.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1678663263366-63e0eea7af523c37e5a77966.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/67c7276e0c51bafa5ee8e033/yBl9QsWcQp4XtqUj4Ni_0.jpeg)
- +3

54

2026 年 6 月 30 日

nlp

evaluation

retrieval

## 推出 RTEB：检索评测的新标准

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/61f33092a92c9a858b654991/jFRUSeZ6DnI27dlCAQRHq.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/5ff5943752c26e9bc240bada/Exyzf3C_gJ2KdsL4K5_cq.png)
- ![](https://huggingface.co/avatars/7a4067accdd1005f78c3c4adad3ee0a5.svg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/64cc0e80a257a3212c0c4b24/wqs6WZN8-3OQthcnQXgN7.png)
- +2

149

2025 年 10 月 1 日

### 社区

Nomad-link-id

11 天前

对从业者真正要紧的那句话很平静：看起来相近的分数，可能是在有实质差异的条件下产生的。

一旦你亲眼看过一个基准仅仅因为改变 inference 阶段的算力或激发协议就发生移动，那么「模型 A 在 X 上胜过了模型 B」而没有一张 card，那就是营销，不是比较。随附已验证结果*以及*配置的 Evaluation Cards——在合适的时候还包括 transcript 级别的上下文——正是让评测从一张排行榜截图变成一份契约的方式。

我想问采用 EEE 的团队一个问题：在截止日期压力下，哪些字段最先是被动跳过（seed、工具访问、尝试预算、oracle 反馈），而当某个字段缺失时，你们是把它当作「不要引用这个差值」，还是「假定用的是默认值」？

可复现的报告不会消除分歧。它会让分歧落在正确的变量上。

把图片、音频和视频拖进文本输入框、粘贴，或者

点击这里

。

在此轻点或粘贴以上传图片

· [注册](https://huggingface.co/join?next=%2Fblog%2Fevaleval-aisi) 或 [登录](https://huggingface.co/login?next=%2Fblog%2Fevaleval-aisi) 即可评论

点赞

28

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6413251362e6057cbb6259bd/k8UMg_tnorG_uCXidybZ7.jpeg)](https://huggingface.co/evijit)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/vnmbzcTMfdqnuzbONym__.png)](https://huggingface.co/dariocava)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1583857146757-5e67bdd61009063689407479.jpeg)](https://huggingface.co/clem)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1594144055859-5ee3a7cd2a3eae3cbdad1305.jpeg)](https://huggingface.co/yjernite)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/66e691d778f2c37966d1d614/1MJg4zMGny3kmC5TPdjN3.png)](https://huggingface.co/DVRRK)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/69d94b034b0d592e906bc968/8HDc1xHMRnIlqJDI6CG_4.jpeg)](https://huggingface.co/vzn2auto)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/01iAmRqyak7mlJT6EDgxJ.png)](https://huggingface.co/MikeEliteLLM)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/62543749b777cd32720675c2/EF_KRZO4hTo8TWXOtvc-n.png)](https://huggingface.co/irenesolaiman)
- [![](https://huggingface.co/avatars/89ddd33671ed6f23c8b9c33f0674033b.svg)](https://huggingface.co/Jureko11)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/IWp7GmKqFXZxE8LB2nADg.png)](https://huggingface.co/birkanoge)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64a99fe3e831371424f583b9/dhKFIea8_zxhLnc2DVQuU.png)](https://huggingface.co/enixmeng)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/7sTK8Q_gZRoOz0uaKnVNJ.png)](https://huggingface.co/luke-loan-atlas)
