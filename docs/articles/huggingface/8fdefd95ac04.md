---
vendor: huggingface
title: 开放阿拉伯语 LLM 排行榜 2
original_title: The Open Arabic LLM Leaderboard 2
url: https://huggingface.co/blog/leaderboard-arabic-v2
date: 2024-08-27
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: 6fe239ff1236
---

# 开放阿拉伯语 LLM 排行榜 2

## 阿拉伯语 LLM 排行榜的现状

支持阿拉伯语的 LLM（无论是单语还是多语言模型）越来越多，社区因此创建了专门的阿拉伯语排行榜。此前，面向阿拉伯语的排行榜通常只是特定作者引入的窄基准，往往是其工作的演示：作者搭个排行榜展示模型在某个特定任务或数据集上的表现。另一些排行榜则要求用户用自己的算力跑评估，然后把结果封装成 JSON 文件提交展示。

这些做法虽然点燃了社区对阿拉伯语基准测试的初步兴趣，但也带来几个难题：

- **资源限制**：许多社区成员没有足够的算力去评估所有可用的开源模型，从而为自己的下游项目或应用挑选最合适的模型，只能依赖模型制作者在文档里给出的结果——而这些结果很多时候无法直接比较。时间和算力的双重高成本会成为参与阿拉伯语 LLM 进一步开发的重大门槛，这也让排行榜成为一种宝贵的共享资源。
- **上报结果的可信度**：由于一些平台要求用户自行评估模型然后单纯提交分数文件，没有可靠机制保证这些结果准确、甚至保证它们真的来自一次真实的评估。缺少集中校验可能损害排行榜的可信度与公平性。

这些局限说明我们需要一个更统一、更易参与、更透明的基准测试平台——不仅能让整个阿拉伯语 NLP 社区做真实的、可复现的实验，还要鼓励这样做。为了解决这些问题，2A2I、TII 和 HuggingFace 于 2024 年 5 月推出了第一版 [Open Arabic LLM Leaderboard - OALL](https://huggingface.co/blog/leaderboard-arabic) [1]，包含 14 个基准，覆盖阅读理解、情感分析、问答等一系列任务。

2024 年 9 月，SDAIA 与萨勒曼国王阿拉伯语全球学院合作推出 [Balsam Index](https://benchmarks.ksaa.gov.sa/b/balsam)，包含约 1,400 个数据集、50,000 个问题、覆盖 67 类任务，例如语法纠错、改写、因果分类、文本理解等。

同年 12 月 5 日，Inception 和 MBZUAI 发布了 [AraGen Leaderboard](https://huggingface.co/blog/leaderboard-3c3h-aragen)——首个面向阿拉伯语生成式任务的排行榜，引入 3C3H 评估指标：采用带私有测试集的动态评估周期，并提供原生阿拉伯语、文化自觉的生成任务数据集 AraGen Bench，从四大任务评估 LLM。

年底收尾也很强劲：2024 年 12 月 19 日，Scale 的安全、评估与对齐实验室（SEAL）在其多语言排行榜家族中发布了[阿拉伯语排行榜](https://scale.com/leaderboard/arabic)。支撑该排行榜的基准与其家族中所有语言一样始终私有，依赖人类偏好评估，使用一个含 1,000 个阿拉伯语提示的数据集，旨在提升聊天机器人在复杂、文化细腻对话中的交互能力。

## 上一版排行榜的影响

第一版 OALL 上线不到 7 个月，就迅速成为阿拉伯语 AI 社区的重要平台：累计访问超过 46,000 人次，过去一个月（2025 年 1 月）就有超过 2,000 次访问。这个 HuggingFace space 获得超过 100 个赞、在 Google Scholar 上被引用超过 8 次。社区提交了 700 多个模型，规模从 1B 到 70B 以上参数，提交者来自 180 多个不同组织，使其成为最活跃的 LLM 评估排行榜之一。自上线以来，排行榜在社交媒体、HuggingFace、Reddit 上引发了大量讨论，是目前最受关注的阿拉伯语排行榜。

如图 1 所示，在提交给初版排行榜的约 700 个模型中，chat 和微调（finetuned）模型占大多数，超过 70%，而预训练模型只占 11%。按模型规模看，超过 50% 的模型小于 7B 参数。

![](https://raw.githubusercontent.com/alielfilali01/OALL-assets/refs/heads/main/v2-blog-plots/piechart_requests.png)

图 1：模型类型与规模分布。

我们省略了模型类型未知（'?'）的计数，它只占总请求的 0.12%。

与其他语言的排行榜相比（见图 2），开放阿拉伯语 LLM 排行榜是最活跃的之一，紧随[韩语](https://huggingface.co/spaces/upstage/open-ko-llm-Leaderboard)、[波兰语](https://huggingface.co/spaces/speakleash/open_pl_llm_Leaderboard)和[葡萄牙语](https://huggingface.co/spaces/eduagarcia/open_pt_llm_Leaderboard)排行榜之后——而这些都上线不到一年。考虑到阿拉伯语是全球使用人数最多的语言之一、而互联网上的阿拉伯语内容却相对有限，这些数字相比其他语言的分量更重。

![](https://raw.githubusercontent.com/alielfilali01/OALL-assets/refs/heads/main/v2-blog-plots/leaderboard_comparison_sort_uptime.png)

图 2：托管在 huggingface 上的各 MCQ 排行榜，已评估模型数量对上线月数。

数据截至 2025 年 1 月 13 日。覆盖语言：阿拉伯语、简体中文、中国台湾中文、捷克语、荷兰语、法语、希伯来语、冰岛语、意大利语、日语、韩语（v2）、马来语、波斯语、波兰语、葡萄牙语、西班牙语、土耳其语。

## 为什么需要一版新排行榜？

社区近期的讨论——包括对 OALL 及类似项目的批评——[指出了当前基准测试实践的关键短板](https://arxiv.org/abs/2409.12623v2) [2]。许多研究者、开发者和语言爱好者强调：需要更直接地评估阿拉伯语特有任务、提高基准创建过程的透明度、纳入更多样化的数据集以反映阿拉伯语方言、领域和真实应用的广度。这些意见在塑造新版排行榜中起了核心作用。

阿拉伯语有其独特的挑战与特征，需要超出通用 NLP 任务的专门评估：精密的语法、丰富复杂的形态、口语方言的多样性、以及带有文化细腻度的安全相关考量。一个照顾到这些因素的排行榜，才能更清楚地呈现模型在真实阿拉伯语语境中的表现。

OALL 的第一版中，相当一部分数据集和任务源自非阿拉伯语语境。把这些任务改写成阿拉伯语后，往往无法反映真实使用场景、也满足不了阿拉伯语社区的实际需求。很多任务是从英语直译而来，经常引入语言与语境上的错位。这种方式忽略了阿拉伯语独特的形态和句法复杂性，使任务难以有效衡量真正的语言理解与建模能力。

另外，OALL 第一版的部分基准随着模型拿到接近满分的分数而逐渐失效，无法再区分小幅改进。为此，新排行榜替换了这些饱和基准，换上一套更相关、更新的评估任务。

为弥补这些缺口，新排行榜纳入了原生以阿拉伯语开发的任务。这些任务的设计旨在捕捉该语言的特征——丰富的形态、微妙的句法、特定语境中的用法——这些正是基于翻译的基准常常丢失的东西。这一转向保证了评估更真实，更贴合阿拉伯语使用的现实。

此外，我们发现在主要任务之一的 AlGhafa 中有一个静默 bug，无意间影响了模型排名。问题出在答案校验的方式上——该任务不是校验选项索引，而是拿模型回答与选项文本本身比对。这不算完全错误，但对小/弱模型的影响不成比例。有些模型因此掉了多达 20 分，而更强的模型基本不受影响。这损害了评估的一致性、公平性与统一性。

## 这一版有什么新东西？

在改革排行榜时，我们遵循两条原则：删除饱和任务和机器翻译任务（后者固有质量较低、可能带文化偏差）；新增近期发布的高质量原生或人工筛选基准，扩大评估覆盖面。

从第一版 OALL 中，我们保留了以下基准数据集：

- [AlGhafa benchmark](https://gitlab.com/tiiuae/alghafa) [3]：TII 发布的原始基准中，我们只保留原生阿拉伯语数据集，即人工筛选版的 Facts-Balanced、SOCAL、XGLUE、Sentiment、Sentiment-Rating、Sentiment-Rating-No-Neutral，[Meta's Belebele](https://huggingface.co/datasets/facebook/belebele) [4] 中的两个阿拉伯语任务（Arabic-MSA 和 Arabic-Dialects），最后是 [Arabic EXAMS benchmarks]() [5]。

我们加入过去一年发布的以下数据集来丰富排行榜：

- [Native Arabic MMLU](https://huggingface.co/datasets/MBZUAI/ArabicMMLU) [6]：MBZUAI 发布的原生阿拉伯语基准，受英文原版 MMLU 启发；由 40 个任务、近 15,000 道现代标准阿拉伯语（MSA）选择题构成，题目源自学校考试。
- Human Translated MMLU（MMLU-HT）[7]：英文原版 MMLU 的人工翻译版，含 57 个任务，由 Inception 在 JAIS 项目中整理，发布于 MBZUAI 的 HF 组织下。
- [MedinaQA](https://huggingface.co/datasets/MBZUAI/MadinahQA)：MBZUAI 发布，旨在推动更多原生阿拉伯语基准的采用，聚焦阿拉伯语语言与语法通识。
- [AraTrust](https://huggingface.co/datasets/asas-ai/AraTrust) [8]：包含 522 道人工撰写选择题的数据集，覆盖安全与真实性的多个侧面。

最后，我们推出 **ALRAGE** 基准：Arabic Language Retrieval Augmented Generation Evaluation（阿拉伯语检索增强生成评估）。它为一组 LLM 在阿拉伯语中的检索增强生成能力提供完整评估框架。其[数据集](https://huggingface.co/datasets/OALL/ALRAGE)经过精细整理，取自 40 本阿拉伯语书籍，主题从艺术文学到技术创新无所不包；使用 meta-llama/Meta-Llama-3.1-70B 合成生成，并通过与 Argilla 合作的[社区冲刺](https://huggingface.co/spaces/OALL/alrage-sprint-progress)由阿拉伯语母语者校验。数据集结构包括问题、标准答案、经 BAAI/bge-m3 嵌入模型检索的候选上下文、以及目标候选索引，全部设计用于真实模拟阿拉伯语场景下的 RAG。

ALRAGE 的创新之处在于评估方法：在 lighteval 框架内实现了 LLM-as-judge 指标。以 Qwen2.5-72B-Instruct 为裁判模型，通过一个结构化的阿拉伯语提示，把模型输出与标准答案对照评分。评估采用细化的 0-10 打分规则，衡量答案的准确性、相关性与质量，再归一化到 0-1 区间以便标准化。这套技术实现（体现为自定义的 JudgeMetricWrapper 类）为阿拉伯语生成提供了严格、可复现的评估方法，同时保持对阿拉伯语语言细腻之处的敏感，正好回应了阿拉伯语 NLP 对高级评估指标的迫切需求。

表 1 汇总了从第一版保留的数据集和本版新增的数据集。

| **从 OALL v1 保留的数据集** | **OALL v2 新增的数据集** |
| --- | --- |
| AlGhafa（6 个任务） | Native Arabic MMLU（40 个任务） |
| EXAMS | Human Translated MMLU（57 个任务） |
| Belebele（2 个任务） | MedinaQA |
|  | AraTrust |
|  | ALRAGE |

除了增删数据集，我们还修复了 UI 及其筛选器的多个问题，并引入了聊天模板。用户提交方面，现在每个组织每周最多提交 5 个模型。这个限制是为了控制排行榜的使用强度，让 diverse 的组织都有机会让自己的模型被评估。注意：OALL 团队提交给 v2 的模型，若 config 中存在聊天模板，评估时会使用它；否则禁用聊天模板。

## v1 与 v2 的结果

为了评估 OALL 第二版的影响，我们对两个版本做了一系列统计比较。

图 3 展示了两个版本在六个基准上的表现分数。值得注意的是，ACVA 和 Toxigen 在不同模型规模上都呈现饱和效应。第一版的 Alghafa 饱和程度较低，我们猜测是因为它同时纳入了原生和翻译的阿拉伯语基准。相比之下，模型在 v2 的 AraTrust、ALRAGE 和 Alghafa 上的表现随模型规模更分散。

![](https://raw.githubusercontent.com/alielfilali01/OALL-assets/refs/heads/main/v2-blog-plots/task_comparison_pretrained_only.png)

图 3：比较开放阿拉伯语 LLM 排行榜两个版本间被移除/保留/新增任务的行为。

为考察 OALL 与其他阿拉伯语 LLM 排行榜的相关性，我们在三个排行榜（OALL v2、SEAL Arabic 和 AraGen）上比较了五个开放阿拉伯语 LLM 的相对排名：[google/gemma-2-27b-it](https://huggingface.co/google/gemma-2-27b-it)、[CohereForAI/aya-23-35B](https://huggingface.co/CohereForAI/aya-23-35B)、[CohereForAI/aya-expanse-32b](https://huggingface.co/CohereForAI/aya-expanse-32b)、[inceptionai/jais-adapted-70b-chat](https://huggingface.co/inceptionai/jais-adapted-70b-chat) 和 [meta-llama/Llama-3.3-70B-Instruct](https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct)。如图 4 所示，各排行榜之间存在明显相关性：Llama3.3-70-instruct 在 OALL v2 和 AraGen 上都排名第一，在 SEAL 上排名第三。*需要说明：AraGen 目前只有 [inceptionai/jais-adapted-70b-chat](https://huggingface.co/inceptionai/jais-adapted-70b-chat) 的分数，Arabic SEAL 排行榜也只收录了 Jais Adapted 70B，推测是预训练模型。由于我们无法完全解决这一出入，本次比较决定在 OALL v2 上评估 [inceptionai/jais-adapted-70b-chat](https://huggingface.co/inceptionai/jais-adapted-70b-chat)。

![](https://raw.githubusercontent.com/alielfilali01/OALL-assets/refs/heads/main/v2-blog-plots/different_leaderboards_comparison_public_models_by_rank.png)

图 4：五个开放模型在开放阿拉伯语 LLM 排行榜第二版上与 AraGen、SEAL-Arabic 排行榜的相对排名比较。数据取自 2025 年 1 月 29 日。

为了进一步探究 OALL 两版之间的差异，我们在图 5 中给出两个类别（预训练和 chat）的头部模型。对提交到 OALL v1 的模型，Qwen2.5 在所有类别中都确立了阿拉伯语的强力基线，预训练模型尤其如此。在 OALL v2 中，Qwen 系列仍统治预训练类别，不过 Qwen/Qwen2-72B 超过 Qwen/Qwen2.5-72B 成为最佳预训练/继续预训练模型；而 Llama3.3-70B-instruct 在所有类别中登顶，超过 calme-2.1-qwen2.5-72b。总的来说，v2 中一些模型排名发生了移动，另一些保持稳定。我们把变化归因于两个关键因素：其一，模型在阿拉伯语原生基准、安全与可信度上的稳健性；其二，OALL v1 评估了 700 多个模型，v2 目前只有 80 个，其中包含一些 v1 里没有的新模型。我们预计社区会在发布后继续充实排行榜。

![](https://raw.githubusercontent.com/alielfilali01/OALL-assets/refs/heads/main/v2-blog-plots/best_pretrained_by_range.png) ![](https://raw.githubusercontent.com/alielfilali01/OALL-assets/refs/heads/main/v2-blog-plots/best_chat_by_range.png)

图 5：各模型规模区间内最佳预训练/继续预训练模型的比较。

最后，我们分析了两类模型家族——AceGPT 和 Jais——在 OALL v1 与 v2 上的平均分。如图 6 所示，两个版本趋势一致：模型越大平均分越高，唯一例外是 inceptionai/jais-family-30b-8k，它在 OALL v2 上超过了更大的 inceptionai/jais-adapted-70b。整体上，v2 的平均分高于 v1，除了两个家族中的 7B 模型。我们猜测这一出入源于小模型在 ALRAGE 上的较弱表现——它是生成式任务，通常更利好大模型。

![](https://raw.githubusercontent.com/alielfilali01/OALL-assets/refs/heads/main/v2-blog-plots/reference_models_pretrained_by_range.png)

图 6：AceGPT 与 Jais 模型家族比较。

## 结论与未来工作

在这篇博客中，我们介绍了开放阿拉伯语 LLM 排行榜的第二版。我们分析了现有阿拉伯语排行榜以及 OALL 第一版，指出诸如部分基准饱和的问题——这些基准在第二版中被移除。我们还移除了机器翻译基准，只保留阿拉伯语原生和人工翻译的基准。最后新增了 Aratrust、MadinaQA、原生 MMLU、人工翻译 MMLU（MMLU-HT）和 ALRAGE 等基准。我们的目标是给社区一个客观的阿拉伯语 LLM 评估，帮助理解每个提交模型的长处与短板。

展望未来，我们希望看到更多阿拉伯语基准发布，特别是在数学、推理、幻觉，以及通用与领域特定基准等领域。

## 致谢

作者感谢 Mohamed bin Zayed 人工智能大学（MBZUAI）提供了本版使用的一部分新原生基准，包括新的 MMLU-HT 数据集。也感谢 TII 慷慨赞助评估后端所需的推理硬件。感谢 Hugging Face 的朋友们持续的支持，在需要的时候始终 🤗。感谢所有专注于各自语言和任务评估与排行榜的人们。最后，感谢社区对 OALL 第一版的参与和宝贵反馈。期待在排行榜上看到更多模型 🚀。

## 引用

```
@misc{OALL2,
  author = {El Filali, Ali and ALOUI, Manel and Husaain, Tarique and Alzubaidi, Ahmed and Boussaha, Basma El Amel and Cojocaru, Ruxandra and Fourrier, Clémentine and Habib, Nathan and Hacid, Hakim},
  title = {The Open Arabic LLM Leaderboard 2},
  year = {2025},
  publisher = {OALL},
  howpublished = {https://huggingface.co/spaces/OALL/Open-Arabic-LLM-Leaderboard}
}
```

## 参考文献

- [1] [Introducing the Open Arabic LLM Leaderboard](https://huggingface.co/blog/leaderboard-arabic)（El Filali 等，2024）
- [2] [CamelEval: Advancing Culturally Aligned Arabic Language Models and Benchmarks](https://arxiv.org/abs/2409.12623v2)（Qian 等，2024）
- [3] [AlGhafa Evaluation Benchmark for Arabic Language Models](https://aclanthology.org/2023.arabicnlp-1.21/)（Almazrouei 等，ArabicNLP 2023）
- [4] [The Belebele Benchmark: a Parallel Reading Comprehension Dataset in 122 Language Variants](https://aclanthology.org/2024.acl-long.44/)（Bandarkar 等，ACL 2023）
- [5] [{EXAMS}: A Multi-subject High School Examinations Dataset for Cross-lingual and Multilingual Question Answering"](https://aclanthology.org/2020.emnlp-main.438/)（Hardalov 等，EMNLP 2023）
- [6] [ArabicMMLU: Assessing Massive Multitask Language Understanding in Arabic](https://aclanthology.org/2024.findings-acl.334/)（Koto 等，ACL 2024）
- [7] [Jais and jais-chat: Arabic-centric foundation and instruction-tuned open generative large language models](https://arxiv.org/abs/2308.16149)（Sengupta 等，2023）
- [8] [AraTrust: An Evaluation of Trustworthiness for LLMs in Arabic](https://arxiv.org/abs/2403.09017)（Alghamdi 等，2024）
- [9] [LightEval: A lightweight framework for LLM evaluation](https://github.com/huggingface/lighteval)（Fourrier 等，2023）
