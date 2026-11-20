---
vendor: openai
title: 面向法律事务的 Astra 引领法律智能
original_title: 
url: https://openai.com/index/astra-law-6-2
date: 2026-11-18
lang: zh
captured: 2026-11-20
extractor: readability-v1
translator: native
status: translated
body_sha: e0617eecd5aa
---

2026年11月17日

公司

# 面向法律事务的 Astra 引领法律智能

我们的最新模型配置在涵盖 24 个法律领域的首发评测中排名第一，其诉讼书状获得的评分也高于 GPT‑6 Astra。现在，所有 ChatGPT Enterprise 客户均可申请访问

今天，我们发布新版面向法律事务的 Astra (Astra for Law)。它在 Harvey LAB-AA 上达到业界最先进水平，并在 [Harvey](https://www.harvey.ai/) 与 [Grubel](https://grubel.ai/) 共同开发的 LAB: USCL，以及 Vals AI 法律研究基准测试中名列前茅。我们也向所有 ChatGPT Enterprise 客户开放了通过可信访问计划申请访问的渠道，包括通过 API 访问。

面向法律事务的 Astra 是基于 GPT‑6.2 Astra 的一种模型配置，后者是我们最新、最强大的前沿模型。它将 GPT‑6.2 Astra 与专门的法律搜索索引相结合，并配备指令，指导模型研究问题、权衡法律依据和撰写答案。该配置在 LAB-AA 评测中的满分率比单独使用 GPT‑6.2 Astra 高出近 40%。

自我们[于 9 月向少数律所推出面向法律事务的 Astra⁠](https://openai.com/index/astra-for-law/) 以来，研究团队迅速推进创新，提升了其法律推理能力，并将法律资料来源扩充至约两倍。这些律所包括 [Cooley⁠](https://openai.com/index/cooley-gopublic/)、[Ropes & Gray⁠](https://openai.com/index/ropes-gray-ai-diligence/) 和 [Sullivan & Cromwell⁠](https://openai.com/index/sullivan-cromwell/)。在 [Vals AI 法律研究基准测试](https://www.vals.ai/benchmarks/legal_research)中，通过全部核查的研究答案占比从约 46% 上升至近 55%。我们持续投入法律领域，让最优秀的律师能够运用我们最强的前沿智能，在日益复杂的世界中解决推动进步的关键问题。

## 面向法律事务的 Astra 在涵盖 24 个法律领域的 Harvey LAB-AA 首发对比中排名第一

Harvey 的法律智能体基准测试 (LAB) 用于检验模型能否从头到尾完成一项法律任务。[LAB-AA](https://artificialanalysis.ai/evaluations/harvey-lab-aa) 是 Artificial Analysis 版本的这项测试。它通过 Harvey 开发的 120 项任务对模型进行严格考验，涵盖起草证言录取提纲、审查商业租赁合同，以及制定收购中的所有权变更策略等工作。要获得满分，答案必须满足任务的每一项要求，且不能产生幻觉，即不能提出缺乏源文件支持的实质性主张。

面向法律事务的 Astra 在 **20.8%** 的任务中获得满分，排名第一，领先于 GPT‑6.2 Astra 的 15.0% 和 Muse Wonder Full 的 13.1%。

![条形图对比 LAB-AA 任务的满分率。](https://images.ctfassets.net/kftzwdyauwt9/7elvsIiYJS1aSNbqPreAcY/55c27a90181e7ac9e5acecbda4057cd0/astra-for-law-labaa-ranking.png?w=3840&q=90&fm=webp)

面向法律事务的 Astra 在 20.8% 的任务中获得满分，排名第一。

面向法律事务的 Astra 以不到首发对比中得分最高的非 OpenAI 模型一半的输出量，取得了这一最高分。它每项任务平均输出约 64,000 个 Token，而 Muse Wonder Full 为 139,000 个；同时，它的满分率更高，达到 20.8%，后者为 13.1%。对于按用量付费的法律团队而言，这意味着面向法律事务的 Astra 获得满分的比例高于 Muse Wonder Full，且**每项任务的输出量减少了 54%。**这可能决定了费用是控制在预算之内，还是大幅超支。

![散点图展示平均输出 Token 数与 LAB-AA 满分率的关系，其中 Token 数采用对数刻度。](https://images.ctfassets.net/kftzwdyauwt9/6Nh3rzJD9qBELDLc4elOlF/56576a8bdc979857681eb7c834bb7a83/astra-for-law-labaa-output-tokens.png?w=3840&q=90&fm=webp)

每个圆点代表一种模型配置。位置越高，表示获得满分的任务越多；越靠左，表示输出 Token 数越少，其中包括模型在推理和写作过程中生成的文本。面向法律事务的 Astra 每项任务平均输出约 64,000 个 Token，满分率为 20.8%；相比之下，Muse Wonder Full 分别为 139,000 个和 13.1%。图中没有任何配置能以更少的输出 Token，在得分上追平面向法律事务的 Astra。

### 面向法律事务的 Astra 每项任务的平均实质性幻觉数比 Claude Opus 5.5 少 95%

法律工作不能接受幻觉。哪怕只有一处虚构的引用，也可能让律师失去客户的信任、法庭上的公信力，以及多年积累的声誉。因此，面向法律事务的 Astra 始终以减少幻觉为优先目标。在 Artificial Analysis 最新的 LAB-AA 对比中，面向法律事务的 Astra 与 GPT‑6 并列，拥有**最低的实质性幻觉率：**每项任务 0.03 次；相比之下，排名其后的非 OpenAI 模型中表现最好的 Claude Opus 5.5 为每项任务 0.59 次。

![分组条形图对比每项 LAB-AA 任务的实质性幻觉数和轻微幻觉数。](https://images.ctfassets.net/kftzwdyauwt9/7lXN8zH60iSckZoa3uUJ1g/458f711e3dd648cb213c56fdd9216956/astra-for-law-labaa-hallucinations.png?w=3840&q=90&fm=webp)

面向法律事务的 Astra 每项任务平均产生 0.03 次实质性幻觉和 0.06 次轻微幻觉。Claude Opus 5.5 每项任务平均产生 0.59 次实质性幻觉和 0.51 次轻微幻觉，分别约为前者的 20 倍和 8.5 倍。

在同样的 120 项任务中，Artificial Analysis 统计了可能在实质性问题上误导读者的幻觉陈述。面向法律事务的 Astra 每项任务平均出现 0.03 次此类错误，在对比中并列最低，约为常规 GPT‑6.2 Astra（0.06 次）的一半。所有受测的 OpenAI 配置产生的幻觉都少于 Claude Opus 5.5，后者是非 OpenAI 模型中在这一指标上表现最好的模型。与面向法律事务的 Astra 相比，Opus 每项任务平均产生约 20 倍的实质性幻觉，达到 0.59 次。值得注意的是，在这项评测中，面向法律事务的 Astra 在满足全部通过标准的任务中没有产生任何幻觉，因此，即使施加幻觉扣分，其评测得分也没有下降。

## 面向法律事务的 Astra 在美国判例法基准测试中名列前茅

> “在我们的各项基准测试中，面向法律事务的 Astra 6.2 相比此前的 Astra 模型都有显著提升。它撰写的诉讼书状更全面，论证更充分。在我们的两两比较评判中，其书状在近 90% 的情况下优于 GPT‑6 Astra 的书状。值得注意的是，深度的提升并未以牺牲此前模型的准确性为代价。我们持续观察到，Astra 系列模型在 LAB 及其美国判例法扩展测试中的幻觉率仍处于最低水平之列。”

Julio Pereyra，Harvey 法律研究负责人

诉讼书状撰写是法律工作中最复杂的长周期流程之一，需要将清晰的推理、研究和写作结合起来，形成出色的论证。

Harvey 与 [Grubel](https://grubel.ai/) 共同开发了 [LAB: USCL](https://www.harvey.ai/blog/legal-agent-bench-us-case-law)，用于测试模型能否针对真实的美国联邦案件开展研究并撰写诉讼书状。每个模型都以原诉讼书状提交前的时间点为起点，就同一争议问题为同一方当事人撰写书状。在一个测试版本中，模型必须自行查找相关判例。在另一个版本中，模型会获得案卷材料和原律师引用的判例。AI 评分系统依据经律师审核和校准的标准，对书状进行两两比较。面向法律事务的 Astra 在两个版本中的得分均名列前茅。

![Harvey 美国判例法评测：在自行研究的测试中，面向法律事务的 Astra 得分为 1,844，Opus 5.5 为 1,817；在提供判例的测试中，两者分别为 1,883 和 1,882。两项测试中的不确定性区间均有重叠。](https://images.ctfassets.net/kftzwdyauwt9/1HVz2qpUp9oskSsvcNmscc/eef9bc9e554b03d83bf1a8a26f898544/astra-law-legal-intelligence-brief-ratings.png?w=3840&q=90&fm=webp)

Farther right means the briefs earned higher ratings. When the models researched the law themselves, Astra for Law scored 1,844 to Opus 5.5’s 1,817. Given the precedents, they were effectively even at 1,883 and 1,882.

*位置越靠右，表示书状获得的评分越高。在模型自行开展法律研究的测试中，面向法律事务的 Astra 得分为 1,844，Opus 5.5 为 1,817。在提供判例的测试中，两者基本持平，分别为 1,883 和 1,882。两项测试中的不确定性区间均有重叠。*

第一项结果（左侧的“研究与起草”）意义重大，因为提升法律研究能力是此次发布的核心改进之一。我们重点提升了这项表现，因为诉讼律师很少能在工作之初就拿到一份恰好包含所需判例的清单。在这项测试中，每个模型都必须判断哪些判决与案件相关，并据此撰写出法院能够理解的论证。在这项任务中，与 Opus 5.5、Gemini 4 Argon 等其他领先前沿模型相比，Harvey 评分系统更青睐新版面向法律事务的 Astra 撰写的书状。在接下来介绍的 Vals AI 评测中，我们可以看到法律研究能力更为显著的提升。

## 面向法律事务的 Astra 在 Vals AI 法律研究基准测试中名列前茅，不到两个月提升了 9 个百分点

OpenAI 已将法律列为重点研究领域，并组建专门的研究团队，加速前沿法律智能的创新。[Vals AI 法律研究基准测试](https://www.vals.ai/benchmarks/legal_research)是衡量该团队早期进展的一项指标，其中的问题由执业律师围绕美国联邦法和州法设定。答案必须涵盖所有要求的要点，并通过来源核查。9 月，面向法律事务的 Astra 答题通过率约为 **46%**。本次发布版本的通过率达到 **54.81%**，与已公布的最高分相差不到 1 个百分点。

以模型配置的形式构建面向法律事务的 Astra，让我们既能改进其推理方式，也能扩充其可查阅的资料。自 9 月以来，我们已将 GPT‑6.2 Astra 引入该配置，并优化了指导其法律分析的指令。我们还向其搜索索引中新增了超过 **539,000 份美国法律资料**，并开始收录英国、澳大利亚和加拿大的一手法律资料，新增了来自**这三个国家的超过 98,000 份资料**。这些新增内容进一步扩充了法律搜索索引。该索引[在推出时就已涵盖超过 2.3 亿个 URL⁠](https://openai.com/index/astra-for-law/)，其资料集覆盖了[美国已公布且具有先例效力的判例法的 99.9% 以上](https://wiki.free.law/c/courtlistener/help/data-coverage/case-law)。

在 Harvey 自有的法律智能体基准测试中，GPT‑6 Astra 在 **4.6%** 的任务中满足了全部要求。在相同条件下，GPT‑6.2 Astra 完全达标的任务比例为 **14.6%**。采用法律专用配置后，这一比例上升至 **16.2%**。

![在 Harvey 法律智能体基准测试中满足全部要求的任务占比：GPT-6 Astra 为 4.6%；GPT-6.2 Astra 为 14.6%；面向法律事务的 Astra 6.2 为 16.2%。](https://images.ctfassets.net/kftzwdyauwt9/38EGkb4OZvdEeyQ0u6J8hb/949faf5ace6376bf617549e8395e35bc/astra-for-law-harvey-lab-all-pass.png?w=3840&q=90&fm=webp)

This chart shows both the rate of development in frontier intelligence, as well as the impact of the model configuration. The full-credit rate more than tripled from GPT‑6 Astra to GPT‑6.2 Astra, then rose another 11% with the legal configuration. This test comes from Harvey’s own LAB (separate from the previously discussed LAB-AA).

*条形越长，表示满足 Harvey 全部要求的任务越多。Harvey 单独开展了这项测试，与 Artificial Analysis 的 LAB-AA 评测相互独立。*

## 律师正利用面向法律事务的 Astra 检验论证，帮助同事做出更艰难的判断

> “我们很高兴有机会提前试用面向法律事务的 Astra 早期版本，这些版本从构建之初就考虑了法律应用场景。无论在诉讼还是交易事务中，这些模型都展现出令人印象深刻的研究深度，以及对法律依据效力的敏锐判断。即使仍处于早期阶段，它们也让我们感到，面向法律领域、以最新且全面的研究为严谨依据的 AI，已经向前迈出了重要一步。”

—John Savva，Sullivan & Cromwell 合伙人

将面向法律事务的 Astra 用于日常工作的律师，正在探索它最值得期待的应用可能。在律所客户和 OpenAI 自身的法律团队中，早期用户正围绕执业领域构建参考资料，让自己的论证接受更严格的质疑，并探索分析法律的新方法。

例如，OpenAI 内部的早期用户正在利用面向法律事务的 Astra 开展以下工作：

- **为你的论证找到最强的对手。**面向法律事务的 Astra 常被用作辩论陪练。一位竞争法律师向它提供自己对某项法律的解读，请它结合立法沿革、法院判决和该法律的其他语言版本，从反方角度展开论证。当反对意见足以促使律师调整法律建议时，它的价值就显现出来了。
- **厘清建议与强制要求之间的界限。**一位研究 AI 监管法案草案的政策律师，想弄清独立审查员究竟有多大权限。如果审查员要求整改，开发者是否必须执行？针对这类问题，这位律师将各项义务的通俗英文解释与法案原文并列呈现，让同事看清文本支持哪种解读。
- **与外部法律顾问首次沟通，就直奔难题。**当公司考虑进入一个陌生行业时，一位产品律师会利用面向法律事务的 Astra，梳理拟开展的业务活动适用哪些规则。这样，律师不必在首次沟通时花时间了解行业概况，而是可以直接就公司计划开展的业务，向专业顾问提出具体问题。
- **把一摞政策文件转化为工作流程。**一位法律项目经理利用面向法律事务的 Astra，将监管程序和公司政策转化为供同事处理新收案件的工作流程，让他们清楚何时需要补充信息、何时可以结案，以及何时应移交律师处理。
- **为法律编写一份你一直想要的配套指南。**一位竞争法律师将面向法律事务的 Astra 与 ChatGPT 的网站构建工具结合使用，为团队经常查阅的法律添加注释。同事在阅读条款时，只需将鼠标悬停在术语上即可查看定义，也可以通过链接查阅解释材料，并查看上次涉及该条款时团队给出的建议。

## 将面向法律事务的 Astra 融入你的法律实践

即日起，所有 ChatGPT Enterprise 客户都可以通过管理控制台中的可信访问计划，申请使用面向法律事务的 Astra。如果你的团队已获得访问权限，请在 ChatGPT 中选择 **GPT‑6.2 Astra Law**。如需通过 API 将面向法律事务的 Astra 集成到自己的工具中，请联系你的客户总监，单独申请审批。

法律行业正处于转折点。技术正在改变企业的能力边界，世界也日益复杂、彼此紧密相连。在这样的背景下，律师迎来了前所未有的机会，帮助我们理解当下、把握变化。这不仅关乎他们服务的企业，也关乎我们每一个人，因为我们都生活在他们参与制定的规则之下。我们相信，最优秀的律师借助最强大的智能，能够回应这个时代的挑战。

这仅仅是开始。我们期待看到你们将法律行业带向怎样的未来。


## 作者
