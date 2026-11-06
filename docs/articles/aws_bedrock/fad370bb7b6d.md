---
vendor: aws_bedrock
title: Amazon Marketplace 如何使用 Amazon SageMaker AI 评估内容质量
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/how-amazon-marketplace-evaluates-content-quality-with-amazon-sagemaker-ai
date: 2026-11-05
lang: zh
captured: 2026-11-06
extractor: readability-v1
translator: agent
status: translated
body_sha: 9f7ae5962c4f
---

# Amazon Marketplace 如何使用 Amazon SageMaker AI 评估内容质量

A+ Content 是 Amazon 商品详情页上的富媒体组件。品牌借助视觉素材传达独特的产品价值与品牌价值，帮助顾客做出明智的购买决策。与没有使用 A+ Content 的同行相比，使用高质量 A+ Content 的销售合作伙伴销量能提升 8–20%。各类品牌都在使用 A+ Content——从拥有大规模内部设计团队的成熟品牌，到资源有限、白手起家的品牌——这带来内容质量上的参差不齐。一个典型的 A+ Content 项目会把文字、图片和视频组合成一个连贯的产品故事。孤立地评估每一项素材，就会错过这些素材协同工作时才体现出来的质量。当你的内容横跨多个异构模块、需要的是整体质量信号而不是逐项素材检查时，本文介绍的多模型融合方案可以帮上忙。在本文中，我们将在 A+ Content 的场景下审视这一问题。

A+ Content 为销售合作伙伴提供了创作自由，让他们可以在自己的商品详情页上表达真实自我，而没有图片比例、文字字数这类严格的内容规范约束。

这种灵活性固然能成就动人的品牌叙事，但也让内容的构成与质量产生了很大差异。

有了质量评估和改进建议，品牌就能把平庸的内容转变成更连贯、更相关、更有用的高质量内容。更好的内容能帮助顾客做出更明智的购买决策，并与品牌建立长久关系，从而为销售合作伙伴带来更好的营收。

要实现这个目标，一套评估系统必须能评判完整的内容体验、给出超越数字分数的可落地建议，并且能反映不同产品类目之间的细微差别。现有方法难以同时满足这些要求，所以在本文中，你会看到一种新的思路：用视觉语言模型（Vision-Language Models，VLMs）从整体上理解并评估内容，再用一个基于 diffusion 的生成组件，根据得到的质量信号生成改进后的视觉素材。

在本文中，你将了解到如何：

- 把完整的电商内容渲染为一张快照，并用 VLM 对其做整体评估。
- 把 VLM 的语义评分与 OCR 的可读性信号相结合，训练一个基于专家标注的轻量 CatBoost 分类器。
- 使用 SHAP 解释质量判定结果，为销售合作伙伴生成可落地的改进建议。
- 在 Amazon SageMaker AI 上实现端到端流水线，从数据摄取、标注，到模型托管、可解释性与生产监控。

## 基于 VLM 的评估：机遇与挑战

视觉语言模型（VLM）把一个图像编码器与一个大语言模型（LLM）配对起来。编码器通常是 [vision transformer（ViT）](https://arxiv.org/abs/2010.11929)，它把图像切成分块并转成 embedding，再由一个小型连接层把这些 embedding 映射进语言模型的输入空间（[Flamingo](https://arxiv.org/abs/2204.14198)、[LLaVA](https://arxiv.org/abs/2304.08485)）。许多 VLM 复用了 [CLIP](https://arxiv.org/abs/2103.00020) 的图像编码器，CLIP 学到的能力是把图像与它的描述文字对应起来。因为 VLM 是按遵循指令的方式训练的，你可以把一张图像连同一份评估标准的评分细则（rubric）一起交给它，无需针对任务训练就能拿到一段书面评估。当你需要与人工评审有更高的一致性时，可以在带标注的样本上对这个模型做 fine-tuning。这使得 VLM 成为一个务实的起点，能够大规模地按你的内容规范检查商品图片。

常规的计算机视觉模型已经能为单项素材打分，比如标记一张模糊的图片，或指出要点列表里的语法错误。用 VLM 逐项给素材打分，在这种能力之上并没有增加太多东西。而一个商品详情页会把图片、文字和布局模块组合成一个完整的故事，它的质量取决于这些部分如何协同。我们的做法是把整个页面渲染成一张快照，让 VLM 按照顾客看到的样子来评估它。

设想一个搅拌机的页面：一张主图、一份突出刀片转速和容量的要点式功能列表，以及一张现代厨房里正在使用搅拌机的生活方式照片。逐项检查时，每个素材都合格：图片清晰，要点没有语法问题，照片光线也不错。合在一起看，问题就出现了。要点列表可能宣传 64 盎司容量的搅拌杯，生活方式照片里展示的却是单人份机型；也可能生活方式照片排在主图之上，让顾客先看到厨房再看到产品。因为一个素材的含义取决于它出现在哪里、周围是什么，这类问题只有在把页面当作整体评估时才会显现。快照给了 VLM 这样完整的视角。要在生产环境中使用它，还需要满足三个要求：评分必须与专家的质量标准一致，评估必须在大规模下既准确又高效，而且每个结果都要说明该修什么。

如图 1 所示，我们通过一套围绕自适应性、性能与可解释性设计的基于 VLM 的多模型融合架构来应对这些考量。下文将分别介绍各个组件。

![基于 VLM 的多模型融合方案模块图，包含 VLM、OCR 与分类器组件](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/30/ML-20598-1.png)

图 1：基于 VLM 的多模型融合方案的模块图，包含 VLM、OCR 与分类器模型

## 用专家标注实现自适应的 VLM 内容评估

用一个预训练 VLM 配合评分细则提示词，它会依据自身通用知识给内容打分，而这些分数并不总能对上电商的质量标准。要靠 fine-tuning VLM 来消除这个差距，就需要 GPU 训练基础设施，而且只有几千个带标注样本的情况下，过拟合的风险是实实在在的。我们的做法是：VLM 和评分细则提示词都固定不动，把 VLM 的结构化输出当作特征，在其上训练一个 CatBoost 分类器来预测专家的质量标签。CatBoost 是一个梯度提升决策树库，在这类小规模表格数据集上表现很好。因为只重新训练分类器，随着标注积累或评判标准变化而更新系统时，只需要一个短暂的纯 CPU 任务，而不是一次基础模型 fine-tuning。

VLM 接收页面快照，以及一份覆盖 4 个质量维度的评分细则提示词：Visual Storytelling、Feature Presentation、A+ Layout 和 Conversion Optimization。每个维度都有明确的评判标准和扣分规则。对每个维度，VLM 返回一个 0 到 10 的分数、一个置信度值，以及一段自然语言的判断依据。例如，当页面缺少多样的模块或缺少生活方式照片、或者信息重复时，它会下调分数并说明原因。这些分数和置信度值成为分类器的特征，而那些判断依据则帮助销售合作伙伴理解结果。

为了构造训练标签，1 名电商营销专家和 4 名专业标注人员按照同一套标准，独立地把来自 10 个产品类目的 5,478 个商品详情页评为高质量或低质量。我们审核了他们的评分，并用多数投票得出共识标签。两类样本大致均衡（49.6% 为高质量），因此分类器不能靠一味预测多数类来拿到高分。为了衡量标签的可靠性，我们使用了 Cohen's kappa，它衡量的是两名评审在扣除偶然因素后实际一致的程度。0 表示一致程度不比随机好，1 表示完全一致，高于 0.8 通常被认为是很强的一致。每位标注人员与共识标签相比，得分都在 0.845 到 0.915 之间。

![标注人员表现与内容难度在各评审间的分布](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/30/ML-20598-2.png)

图 2：标注人员表现与内容难度分布。近乎均衡的类别划分排除了多数类偏置（左），而难度分布解释了残留的分歧（右）

我们在 20% 的留出集（约 1,100 个页面）上把分类器与一个基线做了对比。基线是对 4 个 VLM 分数取平均再施加一个固定阈值，因此每个维度权重相同。基线达到 0.80 的准确率和 0.84 的 F1 分数（高质量类）。在同一批分数上训练的 CatBoost 分类器达到 0.89 的准确率和 0.90 的 F1 分数。因为分类器能学到每个维度有多重要、维度之间如何相互作用，它的预测与专家的判断贴合得更紧。

## 用 OCR 实现高性能的 VLM 内容评估

VLM 能很好地把握页面的整体语义与视觉构成，但在细粒度的可读性问题上不太可靠，比如文字有多密集、行与行之间留白有多少。由于以语言模型为基础，它们还可能偏爱冗长细致的描述，即使顾客更喜欢能快速扫读的精炼文字。在一个文字密集的页面上，VLM 可能把密集的产品信息评为有用，而顾客却在为挤在小块区域里的长句发愁。为了捕捉这类问题，我们使用一个托管在 [SageMaker AI Inference](https://docs.aws.amazon.com/sagemaker/latest/dg/deploy-model.html) 上的光学字符识别（OCR）模型，抽取每一块文字及其位置，然后计算 4 个量化信号：Text Density、Character Density、Spacing 和 Overall Readability。把这些 OCR 分数与 VLM 的语义和视觉评估结合，能补充互补信息，从而提升质量分类效果。

从这份输出中，我们计算出 4 项可读性分数：

- **Text Density：** 页面面积中被文字覆盖的比例。
- **Character Density：** 单位页面面积上的字符数。
- **Spacing：** 词、行、段落之间留白的一致程度与充足程度。
- **Overall Readability：** 由前面 3 项分数合成的一个综合信号。

因为这些分数取决于布局而不是措辞，两个文字内容完全相同的页面也可能得到不同的分数。

融合模型把 4 个 VLM 评分细则分数与 4 个 OCR 分数组合成 8 个特征，并在同一批专家标签上训练一个 CatBoost 分类器。表 1 把它和只用单一特征集训练的模型做对比，用的是同一个 20% 留出集。

在同一个 20% 留出集上，只用 OCR 特征的 CatBoost 模型达到 0.82 的准确率和 0.83 的 F1 分数，只用 VLM 特征的模型为 0.89 和 0.90。融合后的 `OCR-VLM-CatBoost` 模型优于两个单独模型，达到 0.94 的准确率和 0.95 的 F1 分数。相比只用 VLM 的模型，两项指标都有 0.05 的提升，这说明 OCR 并不是一种替代信号，它用细粒度的文字可读性信息补充了 VLM 的整体判断。

| **配置** | **准确率** | **F1 分数** |
| --- | --- | --- |
| 基线（VLM 分数取平均 + 阈值） | 0.80 | 0.84 |
| 只用 OCR 的 CatBoost | 0.82 | 0.83 |
| 只用 VLM 的 CatBoost | 0.89 | 0.90 |
| 融合 OCR-VLM CatBoost | **0.94** | **0.95** |

## 用 SHAP 实现可解释的 VLM 内容评估

只有一个质量标签，并不能告诉销售合作伙伴该先修什么。为了找出是哪些维度主导了每一次判定，我们使用 SHapley Additive exPlanations（SHAP），它给每个特征赋一个值，表示这个特征把预测推向高质量或低质量多远。因为 VLM 分数和 OCR 分数喂给同一个分类器，SHAP 可以在同一把标尺上衡量两者。原始分数做不到这一点：Visual Storytelling 得 6 分、Character Density 很高，并不能告诉你哪一个对判定的影响更大。

在整个留出集上，影响力最大的特征是 OCR 的 Character Density（SHAP 绝对值均值 1.1）、OCR 的 Overall Readability（1.0）和 VLM 的 Visual Storytelling（1.0）。紧随其后的是 A+ Layout（0.8）、Feature Presentation（0.6）和 Conversion Optimization（0.4）。OCR 和 VLM 的特征都排在靠前位置，说明分类器同时依赖这两个信息源。

![所有 VLM 与 OCR 特征的全局 SHAP 值分布](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/30/ML-20598-3.png)

图 3：所有 VLM 与 OCR 特征的全局 SHAP 值分布

对单个页面，SHAP 能显示是哪些特征拉低了判定。对每个被判为低质量的页面，我们按 SHAP 值把 8 个特征排序，然后把最负的几个特征、产品类目以及电商最佳实践，连同 VLM 给出的判断依据一起交给一个 LLM，由它把这些转成有优先级、具体可执行的行动。

图 4 展示了两张局部 SHAP 图，以及基于这些 SHAP 结果得出的 LLM 推理，分别对应一个低质量和一个高质量的 A+ Content 样例。例如，如果 A+ Layout 的 SHAP 值为 -1.2、Visual Storytelling 为 -0.3，系统就会优先建议重排布局、重新平衡文字与图片，其次才是改进图像本身。

| [![低质量 A+ Content 样例的局部 SHAP 分布，多数特征贡献为负](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/30/ML-20598-4.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/30/ML-20598-4.png) | [![高质量 A+ Content 样例的局部 SHAP 分布，多数特征贡献为正](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/30/ML-20598-5.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/30/ML-20598-5.png) |
| --- | --- |

*图 4：所有 VLM 与 OCR 特征的两个局部 SHAP 值分布：(a) 低质量案例，多数特征贡献为负，从而给出请求改进的建议；(b) 高质量案例，多数特征贡献为正*

我们通过测量销售合作伙伴修改内容之后的质量分数，验证了这些基于解释的建议确实有效。在一个具有统计显著性的样本上，修改后的平均质量分数在 10 分制下提升了 1.4 分。因此 SHAP 贡献可以从对判定的解释，转化为可落地的改进优先级与方法。可解释性因而不只是理解模型的一项辅助能力，它还是一个反馈机制，能实打实地提升内容质量。

## 结果

完整系统会用 VLM 和 OCR 给每个页面快照打分，把 4 个 VLM 分数与 4 个 OCR 分数合成一个特征向量，再交给在专家标签上训练的 CatBoost 分类器。随后 SHAP 识别是哪些特征主导了每次判定。为了衡量每个组件带来多少增益，我们在同一个 20% 留出集上对比了 4 种配置。留出集来自 10 个产品类目的 5,478 个商品详情页，包括家具、鞋类、食品杂货、美妆和服饰。

基线对 4 个 VLM 分数取平均并施加一个固定阈值，因此每个维度权重相同。它的准确率为 0.80，F1 分数为 0.84。在同一批分数上训练 CatBoost 分类器，模型就能学到哪些维度最重要、它们如何相互作用，准确率因此升到 0.89、F1 升到 0.90。只用 OCR 分数训练的分类器达到 0.82 的准确率和 0.83 的 F1 分数。把 VLM 分数与 OCR 分数结合取得了最好的结果：0.94 的准确率和 0.95 的 F1 分数，比基线的准确率高 14 个百分点、F1 高 11 个百分点。

![对比各 VLM 与 OCR 评估配置的准确率与 F1 的柱状图](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/30/ML-20598-6.png)

图 5：各 VLM 与 OCR 评估配置的准确率与 F1 对比

把每一项性能增益单独来看，能更清楚地看出整合方案的价值。CatBoost 的校准先缓解了固定阈值的局限，它学到的是各维度各自的权重和非线性的判定边界。随后加入 OCR 特征，补上了 VLM 可能漏掉的文字可读性信号。总的来说，最终的融合模型相比基线把准确率提升了 0.14、F1 提升了 0.11。

我们还在一个额外的实验中更换了 VLM 主干模型，用的是只含单个类目、包含 499 个内容项目的数据集。使用更轻量的 VLM 变体时，基线的准确率为 0.74、F1 为 0.72，而 `OCR-VLM-CatBoost` 模型两项指标都达到 0.90。使用能力更强的 VLM 变体时，基线的准确率为 0.79、F1 为 0.84，而融合模型达到 0.94 和 0.95。对这两个 VLM，融合方案分别把准确率提升了 0.16 和 0.15，说明互补的 OCR 特征带来的增益是稳定的，并不依赖某一个特定的基础模型。

为了在保留对高性能基础模型访问的同时降低开发成本，系统冻结 VLM，只训练开销很低的分类器。在生产环境中，一项全球范围的 A/B 实验根据模型的质量判定调整低质量 A+ Content 的可见性，带来了下单商品数（Ordered Product Sales，OPS）上具有统计意义的提升。这套整合系统除了与专家判断高度贴合，还提供了一种质量信号，能够大规模支撑顾客体验与业务决策。

## 在 Amazon SageMaker AI 上的实现

本节说明这套架构如何在 Amazon SageMaker AI 上端到端落地。从内容渲染、专家标注，到 VLM 评分、OCR 抽取、特征聚合、分类器训练、基于 SHAP 的可解释性和生产监控，流水线的每个阶段都对应一项 SageMaker AI 托管能力。这种设计让运维开销保持很低。下面逐步说明每个组件在生产中如何部署、连接和维护。

![内容质量系统在 Amazon SageMaker AI 上的端到端架构](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/30/ML-20598-7.png)

图 6：内容质量系统在 Amazon SageMaker AI 上的架构

**1. 内容快照渲染与数据摄取：** 渲染完整的 A+ Content 体验，捕捉顾客实际看到页面时的样子。

[SageMaker Processing](https://docs.aws.amazon.com/sagemaker/latest/dg/processing-job.html) 作业以容器化方式大规模运行渲染任务，把数据准备与训练、推理的算力解耦。

**2. VLM 评分与模型托管：** 标注人员按照质量评分细则独立地为内容打标，他们汇总后的共识标签成为训练目标。冻结的 VLM 接收每个快照加一段评分细则提示词，输出 4 个 0 到 10 的分数（Visual Storytelling、Feature Presentation、A+ Layout、Conversion Optimization），每个分数都带一个置信度值和一段判断依据。SageMaker AI Inference 按工作负载选择合适的部署方式来托管 VLM：

- Real-Time Endpoints，用于对单个商品做同步、低延迟的评分。
- Asynchronous Endpoints，用于高分辨率快照这类大载荷，此时轻微的延迟是可以接受的。
- Batch Transform，用于目录规模下的离线批量打分。

这些选项都支持自动扩缩、托管基础设施和 GPU 实例选型。

如果团队想要一个更专用、延迟更低的变体，可以可选地用 [SageMaker Training Jobs](https://docs.aws.amazon.com/sagemaker/latest/dg/how-it-works-training.html) 进一步调优或蒸馏 VLM（例如 Low-Rank Adaptation（LoRA）适配器、把知识蒸馏进一个更小的模型）。要避免这种做法，以保持重新校准的成本可控、并与具体 VLM 无关。

**3. OCR 可读性抽取：** 并行地，OCR 从每个快照抽取文字和边界框位置，并计算 4 个可读性信号：Text Density、Character Density、Spacing 和 Overall Readability。

[SageMaker JumpStart](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-jumpstart.html) 的模型库提供预训练、可单步部署的模型，省去了从零开始寻找、打包和评测模型的麻烦。团队选择一个模型，可以在电商内容上用 [SageMaker Serverless Model Customization](https://docs.aws.amazon.com/sagemaker/latest/dg/customize-model.html) 在不管理基础设施的前提下可选地做 fine-tuning，然后直接部署。之后由 [SageMaker AI Inference](https://docs.aws.amazon.com/sagemaker/latest/dg/deploy-model.html) 把选定的 OCR 模型托管为 endpoint。

**4. 特征聚合与存储：**

[SageMaker Feature Store](https://docs.aws.amazon.com/sagemaker/latest/dg/feature-store.html) 为同一批特征同时提供在线（低延迟推理）与离线（批量训练）访问，避免训练-服务偏斜。团队可以在组织内共享特征，下游使用方因此能复用同一批精心整理的特征。

**5. 分类器训练：** 在这个 8 维特征向量上训练 CatBoost 分类器，以专家标注为目标，学习非均匀的维度权重和非线性的判定边界。这里可以再次使用 [SageMaker Training Jobs](https://docs.aws.amazon.com/sagemaker/latest/dg/how-it-works-training.html)。训练好的模型可以直接注册到 SageMaker Model Registry，用于版本管理、审批流程和生产部署。

**6. SHAP 可解释性与建议：** [SageMaker Processing](https://docs.aws.amazon.com/sagemaker/latest/dg/processing-job.html) 作业支持 [自带（BYO）处理代码](https://docs.aws.amazon.com/sagemaker/latest/dg/processing-container-run-scripts.html)，可以用它来算出 SHAP 值和模型可解释性指标。

**7. 生产监控与重新训练：** 在生产环境中，机器学习模型会随时间自然退化。顾客的审美在变，新的 A+ 模块类型在上线，产品类目在演化，卖家行为也在变化。分类器从历史标注中学到的评分模式会逐渐与当下“质量”的含义脱节，如果不加管控就会造成悄无声息的准确率侵蚀。持续监控能补上这个缺口：它检测线上数据分布或模型预测偏离训练基线的程度，一旦偏离足够大就触发重新校准。

SageMaker AI ModelOps 提供[一组示例](https://github.com/aws-samples/sample-aiops-on-amazon-sagemakerai/tree/main)和资源，帮助你在 SageMaker AI 上把生成式 AI 与机器学习工作负载落地到生产。

[SageMaker AIOps](https://github.com/aws-samples/sample-aiops-on-amazon-sagemakerai/tree/main) 提供了追踪数据质量、模型质量和特征归因漂移的工具。[SageMaker Pipelines](https://docs.aws.amazon.com/sagemaker/latest/dg/pipelines.html) 还能在漂移阈值被突破时，端到端地自动化重新训练流程。

**8. 基于 diffusion 的内容生成：** 为了形成闭环，质量分数与由 SHAP 得出的建议会作为条件输入，驱动一个 diffusion 模型生成改进后的 A+ 图片素材。系统不是让卖家自己去理解建议、从零创作新内容，而是直接产出可立即使用的视觉素材（升级后的生活方式照片、重新平衡的布局、或增强后的产品图），针对性地解决 SHAP 标为负向贡献最大的那些维度。这些生成的素材和自然语言的改进建议会推送给卖家，让他们能在 amazon.com 上升级自己的商品 listing。

## 结论

在本文中，我们展示了如何按顾客看到的样子来评估商品详情页：把每个页面渲染成一张快照，再用 VLM 打分。我们也走了一遍在 Amazon SageMaker AI 上实现这套系统的路径。系统围绕三个目标构建。在自适应性上，我们固定 VLM 不动，只在其评分细则分数上训练一个 CatBoost 分类器，因此系统能与专家判断对齐，并且可以用一个短暂的纯 CPU 任务来更新。在性能上，我们加入 OCR 可读性分数，用来捕捉 VLM 漏掉的文字过密、间距不当的问题。在可解释性上，SHAP 指出是哪些特征主导了每次判定，再由一个 LLM 把这些结果转成给销售合作伙伴的、有优先级的建议。

在来自 10 个产品类目的 5,478 个商品详情页上，融合模型达到 0.94 的准确率和 0.95 的 F1 分数，比分数取平均的基线分别高 14 和 11 个百分点。按建议修改过的页面，其质量分数在 10 分制下平均提升 1.4 分。

内容质量标准会因产品类目、语言和市场而异，我们的专家标注无法完整覆盖所有场景。接下来，我们计划评估更高效的 VLM 主干模型与推理方法，以便在全球商品目录上运行这套系统。

## 关于作者
