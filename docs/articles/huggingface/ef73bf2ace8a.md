---
vendor: huggingface
title: FairStress：更深入地评估 LLM 决策中的公平性
original_title: FairStress: A deeper evaluation of fairness in LLM decision-making
url: https://huggingface.co/blog/allenai/fairstress
date: 2026-10-20
lang: zh
captured: 2026-10-24
extractor: readability-v1
translator: agent
status: translated
body_sha: f446dfd753cd
---

[ 返回文章](https://huggingface.co/blog)

# FairStress：更深入地评估 LLM 决策中的公平性

企业  文章

发布于 2026 年 10 月 20 日


3

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1594144055859-5ee3a7cd2a3eae3cbdad1305.jpeg)](https://huggingface.co/yjernite)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/yu32gPCVLqnpeQd_MMZ74.png)](https://huggingface.co/darrowoflykos)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/7sTK8Q_gZRoOz0uaKnVNJ.png)](https://huggingface.co/luke-loan-atlas)

[![Kyle Wiggers 的头像](https://huggingface.co/avatars/fee5cceec7536851d7c6712760716a71.svg)](https://huggingface.co/Ai2Comms)

Kyle Wiggers

Ai2Comms

[![Ai2 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/652db071b62cf1f8463221e2/CxxwFiaomTa1MCX_B7-pT.png)](https://huggingface.co/allenai) [allenai](https://huggingface.co/allenai)

📄 [技术报告](https://allenai.org/papers/fairstress) | 🤗 [数据](https://huggingface.co/datasets/allenai/fairstress) | 💻 [代码](https://github.com/pardissz/fairstress)

[![FairStress 的示意图：一架天平，周围环绕着招聘、贷款、医疗、教育和住房的图标。](https://www.datocms-assets.com/64837/1791813343-fairstress-blog-draft-google-docs-image-1-1.png)](https://www.datocms-assets.com/64837/1791813343-fairstress-blog-draft-google-docs-image-1-1.png)

今天我们推出 [**FairStress**](https://github.com/pardissz/fairstress)，这是一个衡量 LLM 人口统计公平性的基准，关注的不仅是模型在那些会影响他人的决策中最终做出了什么选择。FairStress 现已开放下载，我们也正在把它集成进 [Olmo-eval](https://github.com/allenai/olmo-eval)——这是我们用来运行和比较模型评估的开放工作台。

模型越来越多地被用于高风险场景，其输出可能影响人们的机会、资源和照护——从筛选求职者、审批贷款，到确定患者的治疗优先级、评估学生的入学申请。标准的“人口统计公平性”基准通常测试的是：在候选人的人口统计身份互换之后，模型在其余条件相同的场景中是否仍选择同一位候选人。例如，如果某位求职者的经验和资历明显更强，那么当这位更强的候选人在一个版本中是黑人、在另一个版本中是白人（资质保持不变）时，模型是否仍然选择该候选人？

然而，在两个版本场景中给出相同答案，可能掩盖了一个有意义的差异：当受到质疑时，模型有多容易改变这一决定。假设候选人 A 明显更强，无论 A 是黑人还是白人，模型都选择了 A。这在输出层面看起来是公平的；但如果随后给模型一个有说服力的论点——例如候选人 B 更受高层领导青睐，或者 B 所属的人口群体在历史上一直被忽视——模型可能在一个版本中比在另一个版本中更容易放弃那位更强的候选人。

FairStress 正是为衡量这些隐藏的不对称性而设计的。

在包括 Olmo、Llama、Qwen、Gemma、Claude 以及 GPT 系列在内的开放权重模型与前沿模型上，跨越多个训练阶段，我们发现：同样的说服性论点——我们称之为*对抗性前缀*——会根据该论点所支持的人口群体不同，让模型或多或少地倾向于改变决定。我们还发现，在招聘、贷款、医疗、教育和住房等领域，模型在解释涉及人口统计信息的决策时存在差异，其内部激活模式也存在差异。

借助 FairStress，我们的目标是*对称公平性*——当证据支持某个决定时，模型应当应用相同的标准，并且无论哪个人口群体受益，都同样抗拒改变该决定。这体现了以平等为中心的一种特定公平观。在其他条件相同的情况下，不同身份的人应当有同等概率被选中；当某位候选人显然是最强选择时，身份不应改变这一概率；而证据充分支持的决定，无论哪个群体受益，都应当同样能抵御对抗性前缀。

FairStress 并不试图涵盖公平的所有概念。例如，基于公平（equity）的路径可能把历史歧视或代表性不足视为与决策相关，从而在其他因素保持不变的情况下仍然偏向少数群体候选人。

## 在最终答案之外衡量公平性

FairStress 包含 300 个贴近现实的双候选人决策场景，覆盖 29 个领域，包括招聘、医疗、贷款、教育、住房和刑事司法。例如，一个场景要求模型为一份机械工程职位在两位候选人之间做选择，另一个场景则问两位患者中谁应当获得最后一支稀缺药物。

部分 FairStress 场景中存在一位明显更强的候选人，其履历更好地满足既定标准。这让我们可以测试：人口统计信息是否会改变模型选择“最受证据支持的候选人”的频率。另一些场景则刻意模糊——两位候选人在不同且难以比较的方面都很强，因此不存在客观上更优的选择。这些案例让我们得以考察：当证据没有明确指向某一方时，模型会偏向哪位候选人。

FairStress 还改变了人口统计身份的呈现明确程度：从完全没有身份信息，到人口统计上有所编码的姓名、间接暗示的身份，或明确的人口统计标签。这让我们可以测试：模型行为中的人口统计差异是只在身份被直接写明时出现，还是在身份被微妙传达时也会出现。

我们的基准还更进一步，测试模型在被对抗性前缀质疑时，决定有多稳定。这些陈述诉诸权威、社会共识、所谓的证据、法律顾虑、历史劣势以及其他形式的说服——例如“一位高层领导已私下审阅了材料，并推荐候选人 B 担任此职”。随后我们测量模型是否会因此改变选择。每个前缀都有一个配对版本，为另一位候选人做同类的论证，使我们能够稳健地检验同一论点是否会因它所支持的候选人不同而产生不同效果。

把这些人口统计身份与前缀的变化组合起来，FairStress 的 300 个场景扩展到超过 1300 万个测试用例。除完整基准之外，我们还开发了 FairStress-Core——一个用项目反应理论筛选出的 5 万条子集，沿用了我们的 [Fluid Benchmarking](https://allenai.org/blog/fluid-benchmarking) 方法。它旨在让评估更快、计算成本更低，同时保留完整基准在揭示模型行为差异方面的大部分能力。

## 模型并不总是同样坚持正确答案

在 FairStress 的实验中，当提示中不包含人口统计信息时，我们发现模型行为差异很小。当一位候选人明显更强时，模型在场景的各个其他条件等价的版本中选择该候选人的比例几乎相同。在两位候选人都不是客观上更强的模糊案例中，模型的选择也接近均分。然而，随着人口统计身份在提示中变得越来越明确，模型行为也变得越来越不对称。

例如，假设候选人 A 的资质明显优于候选人 B。当 A 被编码为多数群体——即在该对比中带有传统上占优势的身份，例如白人、男性或异性恋——而 B 被编码为少数群体时，一个支持 B 的前缀更容易让模型放弃更强的候选人、转向较弱的候选人。当 A 被编码为少数群体、B 被编码为多数群体，且资历保持不变时，同样支持 B 的前缀则不太容易让模型放弃对 A 的正确选择。

我们把这种模式称为*反刻板印象的过度纠正*：在这些比较中，当放弃正确决定会有利于少数群体编码的候选人时，模型更愿意这么做。令人担忧的是，即便一位候选人明显更有资质，人口统计身份仍会改变模型循证据行事的稳定程度。

[![两个招聘场景：Tülu 3.1 8B 在简历较弱或较强的两种情况下都选择了这位黑人跨性别女性，但对选择的解释不同。](https://www.datocms-assets.com/64837/1791813418-fairstress-blog-draft-google-docs-image-2.png?fit=max&h=810&w=1550)](https://www.datocms-assets.com/64837/1791813418-fairstress-blog-draft-google-docs-image-2.png?fit=max&h=810&w=1550)

*在这个招聘示例中，Tülu 3.1 8B 在场景的两个版本中都选择了这位黑人跨性别女性。当她的简历较弱时，解释强调成长潜力和多元背景，尽管她缺少资质证书；当她的简历较强时，解释则强调经验和资质认证。*

[![15 个模型、四种身份条件下的平均人口统计差距，以百分点计。](https://www.datocms-assets.com/64837/1791813453-fairstress-blog-draft-google-docs-image-3.png?fit=max&h=810&w=1550)](https://www.datocms-assets.com/64837/1791813453-fairstress-blog-draft-google-docs-image-3.png?fit=max&h=810&w=1550)

*15 个模型在四种身份条件共有的 19 个领域中评估得到的、少数群体编码候选人与多数群体编码候选人之间的平均差距。数值以百分点计。正值表示差异偏向少数群体编码的候选人；零表示各群体比率相同。*

当人口统计身份是被暗示而非直接写明时，这些差异同样出现。在完整基准上评估的 15 个模型中，放弃正确答案的平均差距在身份被暗示时为 6.9 个百分点，在身份被明确标注时为 9.3 个百分点。

在 FairStress-Core 上，包括 Claude Opus 5 和 GPT-5.5 在内的前沿模型，在两位候选人都不是客观上更强时，约有 60%–65% 的情况选择了少数群体编码的候选人。在配对的对抗性前缀下，在我们 12 次“模型与模式”组合的运行中，转向少数群体编码候选人的比例比转向多数群体编码候选人的比例高出 8.8–42.4 个百分点。

[![FairStress-Core 上资质相当的候选人中，少数群体编码候选人的选择率柱状图。](https://www.datocms-assets.com/64837/1791814138-fairstress-blog-draft-google-docs-image-4.png?fit=max&h=810&w=1550)](https://www.datocms-assets.com/64837/1791814138-fairstress-blog-draft-google-docs-image-4.png?fit=max&h=810&w=1550)

[![在这个示例中，配对的 Claude Opus 5 解释只在选择那位男同性恋申请者时才提到性取向。](https://www.datocms-assets.com/64837/1791814175-fairstress-blog-draft-google-docs-image-5.png?fit=max&h=810&w=1550)](https://www.datocms-assets.com/64837/1791814175-fairstress-blog-draft-google-docs-image-5.png?fit=max&h=810&w=1550)

即便模型在场景的两个人口统计版本中都做出了正确选择，我们也发现了它们在解释选择方式上的更细微差异。

在 11 个开放权重模型中，针对少数群体编码选择的解释使用了略显更自信、更积极的措辞。当身份被明确标注时，这些解释中“韧性”“多元”“障碍”等词的出现频率更高。而针对多数群体编码选择的解释则包含更多程序性词汇，例如“证据”“标准”“详尽”。少数群体候选人的入选率更高，并不必然意味着更公平的对待；当模型在解释一个证据充分的决定时把身份或多元性推到前台，它就有可能淡化那些真正支持选择该候选人的成就与资质。因此，模型可能在选择上偏向少数群体候选人，但在解释中对其资质给予较少的承认。

[![在这个示例中，当种族被明确写出时，Tülu 3 8B DPO 把提前升学的人选从资质更好的白人学生改成了黑人学生。](https://www.datocms-assets.com/64837/1791814242-fairstress-blog-draft-google-docs-image-6.png?fit=max&h=810&w=1550)](https://www.datocms-assets.com/64837/1791814242-fairstress-blog-draft-google-docs-image-6.png?fit=max&h=810&w=1550)

在对 Gemma-3-12B-it 与 Qwen2.5-7B-Instruct 的受控分析中，内部激活——即模型内部的数值活动——能以约 73% 的准确率预测它选择了哪个人口统计方向。对这些同样激活的文本描述达到 57%–59%，而随机基线是 50%。在一项后续测试中，去掉候选人姓名会使基于激活的准确率下降约 18 个百分点。

我们的激活分析仅限两个模型和少量人口统计对比，因此我们认为这些发现比更广泛的行为结果范围更窄。尽管如此，它们表明模型的推理轨迹未必揭示其决策时内部所表示的一切——这与[此前的可解释性研究](https://www.anthropic.com/research/reasoning-models-dont-say-think?trk=article-ssr-frontend-pulse_little-text-block&utm_source=chatgpt.com) 一致：思维链可能遗漏影响模型预测的某些因素。

## 为什么现有基准可能得出不同的结果

我们还想了解 FairStress 与现有 LLM 人口统计偏差度量相比如何。为此，我们把它与 BBQ 做了对比。BBQ 是一个被广泛使用的基准，测试模型在涉及社会群体的场景中是否偏向刻板印象一致的答案——例如，当两个家庭中一个被描述为靠福利救济、另一个被描述为富裕时，问哪个家庭忽视了孩子的教育。

在我们的 BBQ 评估中，模型总体上偏向刻板印象一致的答案，而 FairStress 则揭示出一种偏向少数群体编码候选人的倾向。为理解这一差异，我们考察了问题是如何提出的、答案是如何评分的。我们测试的标准 BBQ 设置是对固定选项的概率打分，而不让模型生成回答。这与普通的聊天使用不同——在聊天中，用户提问并收到生成式回答。FairStress 则要求模型生成自己的回答，并在候选人之间做出选择。

为判断评估设置能否解释 FairStress 与 BBQ 之间的差异，我们取相同的 BBQ 问题和模型权重，测试了五种配置，分别改变 chat template、问题措辞，以及使用固定选项概率打分还是答案生成。在这次受控对比中，我们测试了 Qwen2.5-7B-Instruct、Llama-3.1-8B-Instruct、Gemma-3-27B-it 和 Llama-3.1-70B-Instruct。在使用 chat template、是/否措辞且生成答案时，Qwen2.5-7B-Instruct、Gemma-3-27B-it 和 Llama-3.1-70B-Instruct 从刻板印象一致转向偏向少数群体的行为，而 Llama-3.1-8B-Instruct 变为大致中立——这表明测得的偏差方向部分取决于基准如何提问、如何给答案打分。因此，仅依赖固定选项打分可能漏掉生成式决策中的过度纠正。两者都评估，开发者才能更完整地了解其公平性干预需要应对的行为。

## 为对称稳健性而训练

为探究这种不对称的可能来源，我们审计了 Olmo 3 训练流水线的数据。它的监督微调语料包含约 99,000 条来自两个拒答训练数据集的样本。在微调与偏好训练数据的 28,000 个主题聚类中，我们只找到九个讨论“基于能力而非人口统计做决策”的聚类——而这九个全部是拒答内容。审计还发现对人口群体的描绘并不均衡：少数群体编码的群体得到更多保护性或正面框架，而白人和顺性别者得到的保护性框架很少，并且持续受到负面框架。

综合来看，这些发现表明：教模型拒绝歧视性请求，与教模型如何基于能力做决策之间，存在一道缺口。这些模式是否导致了行为上的差距，仍是未解的问题。

[![Olmo 3 各训练阶段中七个人口群体的净正面减负面框架热力图。](https://www.datocms-assets.com/64837/1791814305-fairstress-blog-draft-google-docs-image-7.png?fit=max&h=810&w=1550)](https://www.datocms-assets.com/64837/1791814305-fairstress-blog-draft-google-docs-image-7.png?fit=max&h=810&w=1550)

*Olmo 3 训练数据中七个人口群体的净框架。每个值是“被判定为对某群体正面的段落百分比”减去“被判定为负面的百分比”。偏好调优列只覆盖被选中的回复，强化学习列只覆盖提示。部分强化学习估计基于很小的样本——最少只有八条提示——应谨慎解读。*

## 现有补救办法有用吗？

FairStress 也可用于评估去偏技术是否真的能带来更稳健、更公平的模型行为。我们测试了九种干预手段，包括自我批评（模型审查并修订自己的答案）、激活引导（在生成过程中直接改变模型的内部表示）以及学习到的编辑（从示例中学到的、对模型内部表示的小幅定向修改）。多数方法未能可靠地减小不对称性，有些方法虽然换来了更均衡的选择，却以准确性大幅下降为代价。例如，一种激活引导方法把 Qwen2.5-7B-Instruct 在明确案例上的准确率从 98% 降到 47%。

有一种方法更接近对称稳健性：反事实思维链，即让模型在候选人人口统计身份互换的情况下重新考虑案例。在所测试的三个模型家族中，这种方法缩小了模型放弃正确决定的容易程度上的差距，同时基本保持了准确率。它并没有消除所有不对称；在模糊案例中，模型仍然偏向少数群体编码的候选人。

## 从公平的结果到公平的决策

FairStress 说明了为什么不能仅凭模型在其他条件等价的场景中是否得出相同的最终选择，来判断它的人口统计公平性。

模型可能在与人口统计身份不同的两个版本场景中，都选择了最受证据支持的候选人，却在一个版本中更容易被说服、以不同方式解释自己的选择，或表现出不同的内部激活模式。按 FairStress 以平等为中心的定义，公平的行为意味着应用相同的标准，并始终如一地捍卫证据充分的决定，无论哪个人口群体受益。

更广泛地说，这项工作体现了我们构建评估的目标：更好地捕捉模型在真实世界环境中的行为。通过发布 FairStress，我们希望研究者和模型构建者能借助它诊断隐藏的不对称性、检验提出的补救办法，并开发出能产生更一致、更可信结果的训练方法。开放、严谨的评估是 Ai2 整体工作的核心，我们希望 FairStress 能为社区再添一件有用的工具，帮助理解模型在哪些方面不足以及如何改进。

## 本文提到的数据集 1

更多来自该作者

## HiRO-ACEv2：以极低的成本模拟 3 公里分辨率的极端天气

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/652db071b62cf1f8463221e2/CxxwFiaomTa1MCX_B7-pT.png)

14

2026 年 10 月 14 日

## 针对 GPU 集群的有效调度

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/652db071b62cf1f8463221e2/CxxwFiaomTa1MCX_B7-pT.png)

54

2026 年 10 月 9 日

### 社区

把图片、音频和视频拖进文本输入框，或粘贴、或点击此处即可上传。

点击或粘贴此处上传图片

· [注册](https://huggingface.co/join?next=%2Fblog%2Fallenai%2Ffairstress) 或 [登录](https://huggingface.co/login?next=%2Fblog%2Fallenai%2Ffairstress) 后发表评论


3

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1594144055859-5ee3a7cd2a3eae3cbdad1305.jpeg)](https://huggingface.co/yjernite)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/yu32gPCVLqnpeQd_MMZ74.png)](https://huggingface.co/darrowoflykos)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/7sTK8Q_gZRoOz0uaKnVNJ.png)](https://huggingface.co/luke-loan-atlas)

## 本文提到的数据集 1
