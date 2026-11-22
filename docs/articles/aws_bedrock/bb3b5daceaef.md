---
vendor: aws_bedrock
title: How Myriad Genetics achieved fast, accurate, and cost-efficient document processing using the AWS open-source Generative AI Intelligent Document Processing Accelerator
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/how-myriad-genetics-achieved-fast-accurate-and-cost-efficient-document-processing-using-the-aws-open-source-generative-ai-intelligent-document-processing-accelerator
date: 2025-11-26
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 7dccb82ffcb4
---

# Myriad Genetics 如何借助 AWS 开源生成式 AI 智能文档处理加速器实现快速、准确且高性价比的文档处理

*本文与 Myriad Genetics 的 Martyna Shallenberg 和 Brode Mccrady 共同撰写。*

医疗机构在维护患者照护质量的同时，还要处理和管理大量复杂的医疗文档，面临诸多挑战。这些机构需要能够有效处理文档的解决方案来满足不断增长的需求。[Myriad Genetics](https://myriad.com/) 是一家为全球医疗提供方和患者提供基因检测与精准医疗解决方案的供应商，它正在应对这一挑战。

Myriad 的收入工程部门每天在妇女健康、肿瘤和精神健康等部门处理数千份医疗文档。公司把收到的文档分为检验申请单（Test Request Forms）、化验结果（Lab Results）、临床记录（Clinical Notes）和保险（Insurance）等类别，以实现事前授权（Prior Authorization）工作流的自动化。系统根据识别出的文档类别，把这些文档路由给合适的外部供应商处理。他们需要人工完成关键信息提取（KIE），包括保险详情、患者信息和化验结果，以判定 Medicare 资格并支撑下游流程。

随着文档量增长，Myriad 的现有系统开始出现问题。自动文档分类方案虽然有效，但成本高昂且耗时。由于复杂程度高，信息提取仍依赖人工。为应对高成本和慢处理，Myriad 需要一个更好的解决方案。

本文探讨 Myriad Genetics 如何与 AWS 生成式 AI 创新中心（GenAIIC）合作，利用 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 和 [Amazon Nova](https://aws.amazon.com/nova/) 基础模型改造其医疗文档处理 pipeline。我们详细说明其现有解决方案面临的挑战，以及生成式 AI 如何降低成本并提升处理速度。

我们考察基于 AWS [开源生成式 AI 智能文档处理（GenAI IDP）加速器解决方案](http://www.amazon.com/genai-idp-accelerator)的技术实现、用于文档分类和关键信息提取的优化策略，以及对 Myriad 事前授权工作流可量化的业务影响。我们还会介绍如何运用 prompt 工程技巧、模型选型策略和架构决策，构建一个能以高准确率处理复杂医疗文档同时降低运营成本的可扩展解决方案。

## 制约医疗运营的文档处理瓶颈

Myriad Genetics 的日常运营依赖于高效处理复杂的医疗文档，这些文档包含患者照护工作流和合规监管所需的关键信息。他们原有的解决方案把用于光学字符识别（OCR）的 [Amazon Textract](https://aws.amazon.com/textract/) 与用于文档分类的 [Amazon Comprehend](https://aws.amazon.com/comprehend/) 组合使用。

尽管分类准确率达到 94%，该方案在运营上仍存在挑战：

- **运营成本**：每页 3 美分，导致每个业务单元每月支出 $15,000
- **分类延迟**：每份文档 8.5 分钟，拖慢了下游的事前授权工作流

信息提取完全依靠人工，需要结合上下文理解才能区分关键的临床差异（比如“是转移性”还是“非转移性”），并在各种不同的文档格式中定位保险号码、患者信息等内容。这一处理负担相当沉重：仅妇女健康业务单元，其客户服务就需要最多 10 名全职员工，每天投入 78 小时。

Myriad 需要一个能够实现以下目标的解决方案：

- 在保持或提升准确率的同时降低文档分类成本
- 加快文档处理速度，消除工作流瓶颈
- 实现医疗文档信息提取的自动化
- 能够跨多个业务单元和文档类型扩展

## Amazon Bedrock 与生成式 AI

现代大语言模型（LLM）凭借在海量文本语料上的预训练，可以高准确率地处理复杂的医疗文档。这种预训练让 LLM 无需特征工程或大规模标注数据集，就能理解语言模式和文档结构。Amazon Bedrock 是一项完全托管的服务，提供来自领先 AI 公司的广泛的高性能 LLM。它提供医疗机构在处理敏感医疗信息时所需的安全性、隐私保护和负责任 AI 能力。在本方案中，我们使用了 Amazon 最新的基础模型：

- **Amazon Nova Pro**：一个高性价比、低延迟的模型，非常适合文档分类
- **Amazon Nova Premier**：一个具备推理能力的先进模型，用于信息提取

## 方案概述

我们与 Myriad 一起，基于 AWS 开源的 GenAI IDP 加速器实施了解决方案。该加速器提供可扩展的无服务器架构，把非结构化文档转换为结构化数据。加速器通过可配置的并发限制并行处理多份文档，而不会压垮下游服务。[其内置的评估框架](https://github.com/aws-solutions-library-samples/accelerated-intelligent-document-processing-on-aws/blob/main/docs/evaluation.md)让用户可以通过用户界面（UI）提供预期输出并评估生成结果，从而迭代地定制配置、提升准确率。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/11/26/ML-19156-1.png)

该加速器提供一键部署，并可选用来针对不同工作负载优化的预构建模式，这些工作负载在可配置性、成本和准确率要求上各不相同：

- [模式 1](https://github.com/aws-solutions-library-samples/accelerated-intelligent-document-processing-on-aws/blob/main/docs/pattern-1.md) —— 使用 Amazon Bedrock Data Automation，这是一项完全托管的服务，提供丰富的开箱即用功能、易用性以及直观的按页计价。该模式推荐用于大多数用例。
- [模式 2](https://github.com/aws-solutions-library-samples/accelerated-intelligent-document-processing-on-aws/blob/main/docs/pattern-2.md) —— 使用 Amazon Textract 与 Amazon Bedrock，搭配 Amazon Nova、Anthropic 的 Claude 或定制微调的 Amazon Nova 模型。该模式非常适合需要自定义逻辑的复杂文档。
- [模式 3](https://github.com/aws-solutions-library-samples/accelerated-intelligent-document-processing-on-aws/blob/main/docs/pattern-3.md) —— 使用 Amazon Textract、带微调分类模型的 [Amazon SageMaker](https://aws.amazon.com/sagemaker/)，以及用于提取的 Amazon Bedrock。该模式非常适合需要专门分类的文档。

模式 2 被证明最适合本项目：它既满足了低成本这一关键要求，又提供了通过 prompt 工程和 LLM 选型来优化准确率的灵活性。该模式提供**无代码配置** —— 通过[配置](https://github.com/aws-solutions-library-samples/accelerated-intelligent-document-processing-on-aws/blob/main/docs/configuration.md)来定制文档类型、提取字段和处理逻辑，并可在 Web UI 中编辑。

我们通过模式 2 的[配置文件](https://github.com/aws-solutions-library-samples/accelerated-intelligent-document-processing-on-aws/blob/main/config_library/pattern-2/README.md)定制了文档类别的定义、每个文档类别的关键属性及其定义、LLM 选择、LLM 超参数，以及分类和提取用的 LLM prompt。在生产环境中，Myriad 把该方案集成到其现有的事件驱动架构中。下图展示了生产 pipeline：

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/11/26/ML-19156-2.jpeg)

- **文档摄取**：收到的订单事件触发从源文档管理系统检索文档，并对先前处理过的文档做缓存优化。
- **并发管理**：[DynamoDB](https://aws.amazon.com/dynamodb/) 跟踪并发的 [AWS Step Function](https://aws.amazon.com/step-functions/) 作业，而 [Amazon Simple Queue Service（SQS）](https://aws.amazon.com/sqs/) 会把超出并发限制的文件排队等待文档处理。
- **文本提取：** Amazon Textract 从规范化后的文档中提取文本、版面信息、表格和表单。
- **分类**：配置好的 LLM 依据配置文件中提供的定制文档分类 prompt 分析提取出的内容，并把文档归入合适的类别。
- **关键** **信息提取**：配置好的 LLM 使用配置文件中提供的提取 prompt 提取医疗信息。
- **结构化输出**：pipeline 把结果格式化为结构化形式，并通过 RESTful 操作传递给 Myriad 的授权系统。

## 使用生成式 AI 进行文档分类

虽然 Myriad 的现有方案达到了 94% 的准确率，但由于不同文档类型之间存在结构相似、内容重叠和格式模式共用的问题，仍会出现误分类。这种语义上的歧义让相似文档难以区分。我们指导 Myriad 运用 prompt 优化技巧，利用 LLM 的上下文理解能力。这一方法超越了模式匹配，能够对文档的上下文和用途进行语义分析，找出人类专家能识别而以往自动化系统会漏掉的区分特征。

### AI 驱动的文档分类 prompt 工程

我们为相似的文档类型编制了带有区分特征的类别定义。为找出这些区分点，我们把每个类别的文档样本提供给 Amazon Bedrock 上启用了模型推理的 Anthropic Claude Sonnet 3.7（该功能让模型展示其逐步分析过程）。模型识别出相似文档类别之间的区分特征，再由 Myriad 的领域专家加以完善，并写入 GenAI IDP 加速器的[模式 2 配置文件](https://github.com/aws-solutions-library-samples/accelerated-intelligent-document-processing-on-aws/blob/main/config_library/pattern-2/README.md)中，用于文档分类 prompt。

### 基于格式的分类策略

我们把文档结构和格式作为关键区分点，用来区分内容相近但结构不同的相似文档类型。我们让分类模型能够识别版面结构、字段排布和视觉元素等格式特有的特征，使系统可以区分仅凭文本内容无法区分的文档。例如，化验报告和检验结果都包含患者信息和医疗数据，但化验报告以表格形式展示数值，而检验结果采用叙述式格式。我们指示 LLM：“*化验报告以表格形式组织数值结果，并附参考范围和单位。检验结果以段落形式呈现发现，并给出临床解读。*”

### 实施负向 prompt 以提升准确率

我们实施负向 prompt 技巧，通过明确告诉模型应避免哪些分类，来解决相似文档之间的混淆。这一方法在分类 prompt 中加入排除性表述，指明不应与各类文档关联的特征。起初，由于患者病史与化验测量值容易混淆，系统经常把检验申请单（TRF）误分类为检验结果。在 TRF 定义中加入诸如“*这些表单包含患者病史。不要把它们与包含当前或近期化验测量值的检验结果混淆*”的负向 prompt 后，分类准确率提升了 4%。通过对常见误分类模式提供明确指引，系统避免了典型错误以及相似文档类型之间的混淆。

### 面向成本与性能优化的模型选型

模型选型决定了规模化下的最优成本性能比，因此我们使用 [GenAI IDP 加速器的评估框架](https://github.com/aws-solutions-library-samples/accelerated-intelligent-document-processing-on-aws/blob/main/docs/evaluation.md)进行了全面的基准测试。我们用 1,200 份医疗文档、覆盖三个文档类别（检验申请单、化验结果和保险）测试了四个基础模型 —— Amazon Nova Lite、Amazon Nova Pro、Amazon Nova Premier 和 Anthropic Claude Sonnet 3.7。我们使用三个关键指标评估每个模型：分类准确率、处理延迟和单份文档成本。加速器的成本跟踪功能让我们可以直接比较不同模型配置的运营支出，确保性能提升在规模化下能转化为可衡量的业务价值。

评估结果表明，Amazon Nova Pro 在 Myriad 的用例上取得了最佳平衡。我们把 Myriad 原有的 Amazon Comprehend 实现迁移到使用优化 prompt 进行文档分类的 Amazon Nova Pro，取得了显著改善：分类准确率从 94% 提升到 98%，处理成本降低 77%，处理速度提升 80% —— 每份文档的分类时间从 8.5 分钟缩短到 1.5 分钟。

## 用生成式 AI 自动化关键信息提取

Myriad 的信息提取原本依靠人工：仅妇女健康部门就需要最多 10 名全职员工每天投入 78 小时，这造成了运营瓶颈和可扩展性约束。将医疗 KIE 自动化面临若干挑战：复选框字段需要区分不同的标记方式（对勾、X、手写标记）；文档中存在重叠标记或内容跨越多个字段等含糊的视觉元素；提取需要结合上下文理解来区分临床差异，并在各种不同的文档格式中定位信息。我们与 Myriad 合作开发了自动化 KIE 解决方案，并实施了以下优化技巧来应对提取的复杂性。

### 为复选框识别增强 OCR 配置

为应对复选框识别的挑战，我们在 GenAI IDP 加速器门户上启用了 Amazon Textract 专用的 TABLES 和 FORMS 功能（如下图所示），以提升 OCR 区分已选中与未选中复选框元素的能力。这些功能增强了系统检测和解读医疗表单中标记方式的能力。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/11/26/ML-19156-3.png)

我们通过在提取 prompt 中加入视觉线索来提升准确率。我们在 prompt 中更新了诸如“*查找小方框内或周围可见的标记（✓、x 或手写标记）*”这样的指示，引导语言模型识别复选框的选择状态。增强的 OCR 能力与有针对性的 prompt 相结合，改善了医疗表单中复选框的提取效果。

### 通过 few-shot 示例进行视觉上下文学习

仅靠配置 Textract 和改进 prompt，无法有效处理复杂的视觉元素。我们实施了多模态方法，把文档图像和 Textract 提取的文本一并发送给基础模型，从而能同时分析视觉版面与文本内容，做出准确的提取决策。我们实施了 [few-shot 学习](https://github.com/aws-solutions-library-samples/accelerated-intelligent-document-processing-on-aws/blob/main/docs/extraction.md#integration-with-few-shot-examples)，提供示例文档图像及其预期提取输出，引导模型理解各种表单版面和标记方式。多个带有正确提取模式的文档图像示例会使 LLM prompt 变得很长。我们利用 GenAI IDP 加速器[与 Amazon Bedrock prompt 缓存功能的内置集成](https://github.com/aws-solutions-library-samples/accelerated-intelligent-document-processing-on-aws/blob/main/docs/extraction.md#using-cachepoint-for-extraction)来降低成本和延迟。prompt 缓存会把冗长的 few-shot 示例在内存中保存 5 分钟 —— 在这段时间内处理多份相似文档时，Bedrock 会复用缓存的示例而不是重新处理，从而同时降低成本和处理时间。

### 用于复杂提取的思维链推理

虽然这种多模态方法提升了提取准确率，但在复杂表单版面中出现重叠和含糊的勾选标记时，我们仍面临挑战。为了在含糊和复杂的情况下也能表现良好，我们使用 Amazon Nova Premier 并实施了[思维链推理](https://arxiv.org/pdf/2201.11903)，让模型借助 thinking 标签逐步思考提取决策。例如：

```
Analyze the checkbox marks in this form:

<thinking>
1. What checkboxes are present? [List all visible options]
2. Where are the marks positioned? [Describe mark locations]
3. Which marks are clear vs ambiguous? [Assess mark quality]
4. For overlapping marks: Which checkbox contains most of the mark?
5. Are marks positioned in the center or touching edges? [Prioritize center positioning]
</thinking>
```

此外，我们在 few-shot 示例中加入了推理说明，展示我们如何在含糊情况下得出结论。这一方法让模型在做出最终判断之前先梳理复杂的视觉证据和上下文线索，从而改善了对含糊勾选标记的处理表现。

通过 GenAI IDP 加速器对 32 份复杂程度各异的文档样本进行测试后发现，启用 Layout、TABLES 和 FORMS 功能的 Amazon Textract，搭配 Amazon Nova Premier 先进的推理能力并加入 few-shot 示例，取得了最佳结果。该方案达到 90% 的准确率（与人工评估者的基线准确率相同），每份文档的处理时间约为 1.3 分钟。

## 结果与业务影响

通过我们的新方案，我们交付了可量化的改进，达到了项目初期设定的业务目标：

**文档分类性能：
**

- **我们把准确率从 94% 提升到 98%**，靠的是针对 Amazon Nova Pro 的 prompt 优化技巧，包括 AI 驱动的 prompt 工程、基于文档格式的分类策略和负向 prompt。
- **我们把分类成本降低了 77%（从每页 3.1 美分降到 0.7 美分）**，靠的是从 Amazon Comprehend 迁移到使用优化 prompt 的 Amazon Nova Pro。
- **我们把分类时间缩短了 80%（从每份文档 8.5 分钟降到 1.5 分钟）**，靠的是选用 Amazon Nova Pro 来提供低延迟、高性价比的解决方案。

**新增的自动化关键信息提取性能：**

- **我们实现了 90% 的提取准确率（与人工流程基线相同）**：这是通过结合 Amazon Textract 的文档分析能力、基于 few-shot 示例的视觉上下文学习，以及 Amazon Nova Premier 用于复杂数据解读的推理能力实现的。
- **我们实现了每页 9 美分的处理成本和每份文档 1.3 分钟的处理时间**，而人工基线需要每个业务单元最多 10 名全职员工每天工作 78 小时。

## 业务影响与推广计划

Myriad 已规划分阶段推广，从文档分类开始。他们计划先在妇女健康业务单元上线新的分类方案，随后推广到肿瘤和精神健康部门。得益于我们的工作，Myriad 在文档分类成本上每年最多可节省 $132K。该方案把每次事前授权提交的时间缩短了 2 分钟 —— 由于能更快访问已标记的文档，专员现在用 4 分钟就能完成订单，而不是 6 分钟。这一改进仅妇女健康部门每月就在 9,000 次事前授权中节省 300 小时，相当于每名事前授权专员节省 50 小时。

这些可量化的改进改变了 Myriad 的运营，其工程领导层如是确认：

> “与 GenAIIC 合作，把我们的智能文档处理解决方案从 AWS Comprehend 迁移到 Bedrock，是具有变革意义的一步。通过同时提升性能和准确率，该方案预计每月可节省超过 $10,000。团队与 Myriad 内部工程团队的紧密协作交付了高质量、可扩展的解决方案，而他们在先进语言模型方面的深厚专长提升了我们的能力。这是创新与伙伴关系如何驱动可量化业务影响的一个绝佳范例。”—— Martyna Shallenberg，Myriad Genetics 软件工程高级总监

## 结语

AWS GenAI IDP 加速器让 Myriad 得以快速实施，它提供灵活的框架，缩短了开发时间。医疗机构需要量身定制的解决方案 —— 加速器提供广泛的定制能力，让用户能够把方案适配到特定的文档类型和工作流，而无需大量改动代码，也无需在开发过程中频繁重新部署。我们的方法展示了战略性 prompt 工程与模型选型的力量。我们通过聚焦 prompt 设计（包括负向 prompt 和视觉线索），在专业领域实现了高准确率。我们为分类选择 Amazon Nova Pro、为复杂提取选择 Nova Premier，从而同时优化了成本与性能 —— 把合适的模型匹配到每项具体任务。

## 亲自体验该方案

希望改进文档处理工作流的机构可以亲身感受这些收益。为 Myriad 的转型提供支撑的[开源 GenAI IDP 加速器](https://aws.amazon.com/blogs/machine-learning/accelerate-intelligent-document-processing-with-generative-ai-on-aws/)可供你在自己的环境中部署和测试。该加速器简洁直接的安装流程让用户能够快速评估生成式 AI 如何改变文档处理难题。

在你体验过加速器并了解它对你工作流的潜在影响之后，欢迎联系 AWS GenAIIC 团队，探讨如何为你的具体用例定制和优化 GenAI IDP 加速器。这种亲身实践的方式能确保你在本机构实施智能文档处理时做出有依据的决策。

### 关于作者

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/11/26/ML-19156-4.jpeg)****Priyashree Roy** 是 AWS 生成式 AI 创新中心的二级数据科学家，她运用自己在机器学习和生成式 AI 方面的专长，为 AWS 战略客户开发创新解决方案。她以严谨的科学方法应对复杂的业务挑战，这得益于她在佛罗里达州立大学获得的实验粒子物理学博士学位以及在密歇根大学的博士后研究。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/11/26/ML-19156-5.jpeg)****Mofijul Islam** 是 AWS 生成式 AI 创新中心的二级应用科学家兼技术负责人，他帮助客户运用生成式 AI、大语言模型（LLM）、多 agent 学习、代码生成和多模态学习来应对以客户为中心的研究与业务挑战。他拥有弗吉尼亚大学机器学习博士学位，研究方向是多模态机器学习、多语言自然语言处理（NLP）和多任务学习。他的研究成果发表于 NeurIPS、国际学习表征会议（ICLR）、自然语言处理经验方法会议（EMNLP）、人工智能与统计学会（AISTATS）和美国人工智能促进会（AAAI）等顶级会议，以及电气与电子工程师协会（IEEE）和美国计算机协会（ACM）的期刊。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/11/26/ML-19156-6.jpeg)****Nivedha Balakrishnan** 是 AWS 生成式 AI 创新中心的二级深度学习架构师，她帮助客户设计和部署生成式 AI 应用以解决复杂的业务挑战。她的专长涵盖大语言模型（LLM）、多模态学习和 AI 驱动的自动化。她拥有圣何塞州立大学应用数据科学硕士学位和瑞典林雪平大学生物医学工程硕士学位。她此前的研究聚焦于药物发现与医疗健康领域的 AI 应用，把生命科学与机器学习连接起来。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/11/26/ML-19156-7.jpeg)****Martyna Shallenberg** 是 Myriad Genetics 的软件工程高级总监，她领导跨职能团队构建 AI 驱动的企业级解决方案，改变收入周期运营和医疗交付方式。凭借横跨基因组学、分子诊断和软件工程的独特背景，她扩展了从智能文档处理（IDP）到模块化 LIMS 解决方案等一系列创新平台。Martyna 还是 BioHive HealthTech Hub 的创始人兼总裁，推动跨领域协作以加速精准医疗和医疗创新。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/11/26/ML-19156-8.jpeg)****Brode Mccrady** 是 Myriad Genetics 的软件工程经理，他领导 AI、收入系统和智能文档处理方面的计划。凭借十多年在商业智能和战略分析领域的经验，Brode 在把复杂业务需求转化为可扩展技术解决方案方面拥有深厚专长。他拥有经济学学位，这塑造了他以数据驱动方式解决问题和制定业务战略的思路。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/11/26/ML-19156-9.jpeg)****Randheer Gehlot** 是 AWS 的首席客户解决方案经理，专精医疗健康与生命科学领域的转型。他深入关注 AI/ML 在医疗健康中的应用，帮助企业设计并实施高效云解决方案，以应对真实的业务挑战。他的工作包括与各类组织合作，实现基础设施现代化、推动创新并加快上云进程，同时确保成果务实且可持续。

### 致谢

*我们感谢 Bob Strahan、Kurt Mason、Akhil Nooney 和 Taylor Jensen 在整个过程中做出的重要贡献、战略决策与指导。*
