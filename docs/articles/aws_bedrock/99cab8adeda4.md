---
vendor: aws_bedrock
title: Going beyond AI assistants: Examples from Amazon.com reinventing industries with generative AI
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/going-beyond-ai-assistants-examples-from-amazon-com-reinventing-industries-with-generative-ai
date: 2025-05-30
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: cd18353a8e88
---

# 超越 AI 助手：Amazon.com 用生成式 AI 重塑各行业的实例

[生成式 AI](https://aws.amazon.com/generative-ai/) 通过各类应用革新着业务运营，其中就包括 Amazon 的 [Rufus](https://www.aboutamazon.com/news/retail/amazon-rufus) 和 [Amazon Seller Assistant](https://www.aboutamazon.com/news/innovation-at-amazon/amazon-project-amelia) 这类对话式助手。此外，一些影响最大的生成式 AI 应用在幕后自主运行，这一关键能力让企业能够大规模地改造其运营、数据处理与内容创作。这些非对话式实现通常表现为由[大语言模型（LLM）](https://aws.amazon.com/what-is/large-language-model/)驱动的 agentic 工作流，它们无需用户直接交互，就能跨行业执行特定的业务目标。

非对话式应用具有更高的延迟容忍度、批处理和缓存等独特优势，但其自主运行的性质要求比对话式应用更强的防护栏（guardrails）和更彻底的质量保证——后者可以受益于实时的用户反馈与监督。

本文考察四个不同的 Amazon.com 案例，它们都属于这类生成式 AI 应用：

- [Amazon.com 商品详情页创建与目录数据质量改进](https://www.aboutamazon.com/news/innovation-at-amazon/amazon-generative-ai-powered-product-listings) —— 展示 LLM 如何帮助销售伙伴和 Amazon.com 大规模创建更高质量的详情页
- [Amazon Pharmacy 的处方处理](https://www.aboutamazon.com/news/retail/how-amazon-pharmacy-uses-generative-ai) —— 展示在高度受监管的环境中的实现，以及 agentic 工作流的任务分解
- [评论摘要](https://www.aboutamazon.com/news/amazon-ai/amazon-improves-customer-reviews-with-generative-ai) —— 说明大规模批处理、与传统[机器学习](https://aws.amazon.com/ai/machine-learning/)（ML）的集成、更小 LLM 的使用，以及规模化下的高性价比方案
- [Amazon Ads 创意图像与视频生成](https://advertising.amazon.com/library/guides/how-to-use-ai-image-generators) —— 突出多模态生成式 AI 与创意工作中的负责任 AI 实践

每个案例都揭示了实现非对话式生成式 AI 应用的不同侧面，从技术架构到运营考量。通读这些例子，你将了解包括 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 和 [Amazon SageMaker](https://aws.amazon.com/sagemaker/) 在内的全套 AWS 服务如何成为成功的关键。最后，我们列出这些用例共同分享的关键经验。

## 在 Amazon.com 上创建高质量的商品详情页

创建带有完整细节的高质量商品详情页，有助于顾客做出明智的购买决策。传统上，销售伙伴需要为每件商品手动录入数十个属性。这项于 2024 年推出的新生成式 AI 方案改变了这一流程：它主动从品牌网站及其他来源获取商品信息，从而在众多商品品类中改善顾客体验。

生成式 AI 简化了销售伙伴的体验：他们可以用 URL、商品图片或电子表格等多种格式输入信息，系统会自动将这些信息转换为所需的结构与格式。已有超过 90 万名销售伙伴使用该功能，近 80% 生成的详情页草稿在仅做极少修改的情况下被接受。AI 生成的内容提供了完整的产品细节，有助于提升清晰度与准确性，进而帮助商品在顾客搜索中被发现。

对于新上架的商品，工作流从销售伙伴提供初始信息开始。系统随后利用多个信息来源生成完整的详情页，包括标题、描述和详细属性。生成的详情页会交给销售伙伴审批或编辑。

对于已有的详情页，系统会识别出可以通过补充数据来丰富内容的商品。

### 面向多种输出的数据集成与处理

Amazon 团队使用 Amazon Bedrock 及其他 AWS 服务，为内部和外部来源构建了兼容 LLM 的 API 连接器，以便无缝接入 Amazon.com 的后端系统。

一个关键挑战是把多样化的数据综合成统一的详情页，覆盖 50 多个文本与数值属性。LLM 需要特定的控制机制和指令才能准确理解电商概念，因为面对如此复杂多样的数据，它们未必能表现最优。例如，LLM 可能把刀座上的“capacity”误解为尺寸而非刀槽数量，或把“Fit Wear”当成款式描述而不是品牌名。团队大量使用 prompt 工程和微调来应对这些情况。

### 用 LLM 进行生成与验证

生成的商品详情页应当完整且正确。为此，该方案实现了一个多步骤工作流，用 LLM 同时负责属性的生成与验证。这种双 LLM 方法有助于防止幻觉，在处理安全隐患或技术规格时尤为关键。团队开发了先进的自反思（self-reflection）技术，确保生成与验证过程能够有效互补。

下图展示了由 LLM 执行的生成与验证过程。

图 1. 商品详情页创建工作流

### 结合人工反馈的多层质量保证

人工反馈是该方案质量保证的核心。流程包括由 Amazon.com 专家进行初步评估，以及由销售伙伴提供接受或修改意见。这既保证了高质量的输出，也让 AI 模型得以持续改进。

质量保证流程包含自动化测试方法，结合基于 ML、算法或 LLM 的评估。未通过的详情页会重新生成，通过的则进入进一步测试。我们使用[因果推断模型](https://en.wikipedia.org/wiki/Causal_inference)识别影响详情页表现的潜在特征与可丰富内容的机会。最终，通过质量检查并获得销售伙伴接受的详情页会发布上线，确保顾客获得准确、完整的商品信息。

下图展示了商品详情页生成在投入生产时进行测试、评估与监控的工作流。

图 2. 商品详情页测试与人在环（human-in-the-loop）工作流

### 兼顾准确性与成本的应用级系统优化

鉴于对准确性和完整性的高标准，团队采用了全面的实验方法，并配套一套自动优化系统。该系统探索 LLM、prompt、playbook、工作流和 AI 工具的各种组合，以迭代提升包括成本在内的业务指标。通过持续评估和自动化测试，商品详情页生成器在保持对新 AI 进展的适应性的同时，有效地平衡了性能、成本与效率。这意味着顾客能受益于高质量的商品信息，销售伙伴也能获得高效创建详情页的前沿工具。

## Amazon Pharmacy 中由生成式 AI 驱动的处方处理

在延续前面卖家详情页示例中讨论的“人机混合”工作流的基础上，Amazon Pharmacy 展示了这些原则如何应用于受 [Health Insurance Portability and Accountability Act](https://aws.amazon.com/compliance/hipaa-compliance/)（HIPAA）监管的行业。此前我们在博文[了解 Amazon Pharmacy 如何使用 Amazon SageMaker 构建基于 LLM 的聊天机器人](https://aws.amazon.com/blogs/machine-learning/learn-how-amazon-pharmacy-created-their-llm-based-chat-bot-using-amazon-sagemaker/)中分享了面向患者护理专家的对话式助手，现在我们聚焦于自动化的处方处理，你可以在 [Amazon Pharmacy 中一张处方的生命周期](https://www.amazon.science/blog/the-life-of-a-prescription-at-amazon-pharmacy)以及下面这篇[发表于 Nature Magazine 的研究论文](https://www.nature.com/articles/s41591-024-02933-8)中了解相关内容。

在 Amazon Pharmacy，我们构建了一套基于 Amazon Bedrock 和 SageMaker 的 AI 系统，帮助药房技术员更准确、更高效地处理用药说明。该方案让人类专家与 LLM 在生成与验证两个角色上协同，以提升患者用药说明的精确度。

### 面向医疗准确性的 agentic 工作流设计

处方处理系统将人类专业知识（数据录入技术员和药师）与 AI 支持结合起来，用于提出用药指征建议并提供反馈。如下图所示，工作流首先由基于药房知识库的预处理器在 [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) 中规范化原始处方文本，随后由 SageMaker 上经过微调的小语言模型（SLM）识别关键要素（剂量、频次）。

| ![数据录入技术员与药师配合两个 GenAI 模块的工作流](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/16/Picture3-blog17678-1.jpg)  (a) |  |
| --- | --- |
| ![数据录入技术员与药师配合两个 GenAI 模块的工作流](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/16/Picture4-blog17678-1-645x1024.png)  (b) | ![标记模块工作流](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/16/Picture5-blog17678-1-548x1024.png)  (c) |
| *图 3. (a) 数据录入技术员与药师配合两个 GenAI 模块的工作流，(b) 建议模块工作流，(c) 标记模块工作流* |  |

该系统无缝地整合了数据录入技术员和药师等专家，生成式 AI 在其中补强整个工作流，朝着敏捷与准确的方向更好地服务患者。随后，一套带安全防护栏的用药指征装配系统会通过建议模块为数据录入技术员生成指令，帮助他们创建录入的指征。标记模块则标记或纠正错误，并把反馈提供给数据录入技术员，从而落实更多安全措施。技术员最终敲定高度准确、安全录入的指征，交由药师反馈或执行，传至下游服务。

该方案的一个亮点是任务分解，它让工程师和科学家能够把整体流程拆成众多步骤，每个模块由子步骤构成。团队大量使用了经过微调的 SLM。此外，流程还采用传统 ML 方法，例如[命名实体识别（NER）](https://docs.aws.amazon.com/sagemaker/latest/dg/sms-named-entity-recg.html)，或用[回归模型](https://en.wikipedia.org/wiki/Regression_analysis)估计最终置信度。在这样受控、定义明确的过程中使用 SLM 和传统 ML，显著提升了处理速度，同时由于在特定步骤上加入了恰当的防护栏，仍维持了严格的安全标准。

该系统由多个定义明确的子步骤组成，每个子流程都作为一个专门组件运行，在工作流中半自主又相互协作地服务于整体目标。这种带分阶段具体校验的分解式方法，比端到端方案更有效，同时还能使用经过微调的 SLM。考虑到其与现有后端系统的集成情况，团队使用 [AWS Fargate](https://aws.amazon.com/fargate/) 来编排工作流。

在产品开发过程中，团队转向 Amazon Bedrock，它提供了高性能的 LLM，并带有为生成式 AI 应用量身定制的易用特性。SageMaker 则支持更多的 LLM 选择、更深的可定制性以及传统 ML 方法。想进一步了解这项技术，请参阅[任务分解与更小的 LLM 如何让 AI 更可负担](https://www.amazon.science/blog/how-task-decomposition-and-smaller-llms-can-make-ai-more-affordable)，并阅读 [Amazon Pharmacy 业务案例研究](https://aws.amazon.com/solutions/case-studies/amazon-pharmacy-improves-customer-care-case-study/)。

### 用防护栏与 HITL 构建可靠的应用程序

为符合 HIPAA 标准并保护患者隐私，我们在采用混合方法的同时落实了严格的数据治理实践：混合方法将使用 Amazon Bedrock API 的微调 LLM 与基于 [Amazon OpenSearch Service](https://aws.amazon.com/opensearch-service/) 的[检索增强生成（RAG）](https://aws.amazon.com/what-is/retrieval-augmented-generation/)相结合。这一组合在高效检索知识的同时，为特定子任务保持了高准确度。

管理 LLM 幻觉在医疗场景中至关重要，而这需要的不仅仅是在大规模数据集上微调。我们的方案构建了基于 [Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/) 的领域特定防护栏，并辅以人在环（HITL）监督，以提升系统可靠性。

Amazon Pharmacy 团队正通过药师实时反馈和扩展处方格式支持来持续增强该系统。这种在创新、领域专长、先进 AI 服务与人工监督之间取得平衡的做法，不仅提升了运营效率，也意味着 AI 系统恰当地赋能医疗专业人员提供最佳的患者护理。

## 由生成式 AI 驱动的顾客评论摘要

前面的示例展示了 Amazon Pharmacy 如何将 LLM 集成到处方处理的实时工作流中，而接下来的用例则说明类似的技术——SLM、传统 ML 与周到的流程设计——如何应用于[离线批量推理](https://docs.aws.amazon.com/sagemaker/latest/dg/deploy-model.html)，且规模巨大。

Amazon 推出了 [AI 生成的顾客评论摘要](https://www.aboutamazon.com/news/retail/amazon-ai-generated-review-highlights)，用于处理每年超过 2 亿条商品评论与评分。该功能把顾客的共同意见提炼成简洁段落，突出关于商品及其特性的正面、中性和负面反馈。购物者可以快速掌握共识，同时通过提供相关顾客评论的入口并保留原始评论来保持透明。

该系统通过一个界面改善购物决策：顾客可以选择具体特性（例如画质、遥控功能，或 Fire TV 的安装便捷性）来查看评论摘要。特性以视觉方式编码——绿色对勾表示正面情绪，橙色减号表示负面，灰色表示中性——购物者因此可以基于已验证购买的评论快速识别商品的优缺点。下面的截图展示了某商品在噪音水平方面的评论摘要。

图 4. 某商品评论摘要的示例。

### 离线用例中高性价比使用 LLM 的配方

团队开发了一套高性价比的混合架构，把传统 ML 方法与专用 SLM 结合起来。该方案把情感分析和关键词抽取交给传统 ML，而把复杂的文本生成任务交给经过优化的 SLM，从而同时提升准确性和处理效率。下图展示了传统 ML 与 LLM 协同完成整体工作流的方式。

图 5. 工作流中传统 ML 与 LLM 的使用。

该功能采用 [SageMaker 批量转换](https://docs.aws.amazon.com/sagemaker/latest/dg/batch-transform.html)进行异步处理，相比实时端点显著降低成本。为提供近乎零延迟的体验，该方案把抽取出的洞察与现有评论一起[缓存](https://aws.amazon.com/caching/aws-caching/)，缩短等待时间，并让多位顾客无需额外计算即可同时访问。系统增量处理新评论，在不重新处理整个数据集的情况下更新洞察。为获得最佳性能与成本效益，该功能使用 [Amazon Elastic Compute Cloud](https://aws.amazon.com/ec2)（Amazon EC2）[Inf2 实例](https://aws.amazon.com/ec2/instance-types/inf2/)运行批量转换作业，[相较替代方案可提供最高 40% 更好的性价比](https://aws.amazon.com/ec2/instance-types/inf2/)。

通过采用这一全面的方法，团队在处理海量评论与商品的同时有效地管理了成本，使方案既高效又可扩展。

## Amazon Ads 由 AI 驱动的创意图像与视频生成

前面的示例探讨的主要是以文本为中心的生成式 AI 应用，现在我们转向多模态生成式 AI：[Amazon Ads 为赞助广告生成创意内容](https://advertising.amazon.com/lp/grow-your-business-with-sponsored-ads)。该方案具备[图像](https://advertising.amazon.com/blog/ai-image-generation)与[视频](https://www.aboutamazon.com/news/innovation-at-amazon/amazon-ads-generative-ai-video-generator-advertisers)生成能力，我们将在本节分享其中的细节。共同之处在于，该方案以 [Amazon Nova](https://aws.amazon.com/ai/generative-ai/nova/creative/) 创意内容生成模型为核心。

从客户需求倒推，2023 年 3 月 Amazon 的一项调研显示，近 75% 在为广告活动成效苦恼的广告主都把创意内容生成列为首要挑战。许多广告主——尤其是那些没有内部能力或代理机构支持的——因制作高质量视觉素材所需的专业知识和成本而面临巨大障碍。Amazon Ads 的这套方案让视觉内容创作大众化，使不同规模的广告主都能以可及且高效的方式使用它。影响相当可观：在 [Sponsored Brands](https://advertising.amazon.com/solutions/products/sponsored-brands) 广告活动中使用 AI 生成图像的广告主，[点击率（CTR）](https://en.wikipedia.org/wiki/Click-through_rate)提升了近 8%，提交的广告活动数量比未使用者多 88%。

去年，AWS Machine Learning Blog 发表了一篇[详细介绍该图像生成方案](https://aws.amazon.com/blogs/machine-learning/learn-how-amazon-ads-created-a-generative-ai-powered-image-generation-capability-using-amazon-sagemaker/)的博文。此后，Amazon 采用 [Amazon Nova Canvas](https://aws.amazon.com/ai/generative-ai/nova/creative/) 作为创意图像生成的基础，从文本或图像 prompt 生成专业级图像，并具备基于文本的编辑功能以及色彩方案与版式调整控制。

2024 年 9 月，Amazon Ads 团队把从商品图片生成[短视频广告](https://www.aboutamazon.com/news/innovation-at-amazon/amazon-ads-generative-ai-video-generator-advertisers)的能力纳入其中。该功能使用 [Amazon Bedrock 上可用的基础模型](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)，让客户通过自然语言控制视觉风格、节奏、镜头运动、旋转和缩放，并借助 agentic 工作流先描述视频分镜，再为故事生成内容。下面的截图展示了 Amazon Ads 中为商品背景生成创意图像的示例。

图 6. 某商品的广告图像生成示例。

正如原博文所述，[负责任 AI](https://aws.amazon.com/ai/responsible-ai/) 是该方案的核心，Amazon Nova 创意模型自带控制能力以支持安全与负责任的 AI 使用，包括水印和内容审核。

该方案使用 [AWS Step Functions](https://aws.amazon.com/step-functions/) 搭配 [AWS Lambda](https://aws.amazon.com/lambda/) 函数，以无服务器方式编排图像与视频生成流程。生成的内容存储在 [Amazon Simple Storage Service](https://aws.amazon.com/s3/)（Amazon S3）中，元数据存放在 DynamoDB，[Amazon API Gateway](https://aws.amazon.com/api-gateway) 则为客户提供对生成能力的访问。该方案现在除在多个步骤中维持 [Amazon Rekognition](https://aws.amazon.com/rekognition/) 与 [Amazon Comprehend](https://aws.amazon.com/comprehend/) 集成以进行额外的安全检查外，还采用了 Amazon Bedrock Guardrails。下面的截图展示了 Amazon Ads 广告活动构建器中 AI 生成的创意视频。

图 7. 某商品的广告视频生成

大规模创建高质量广告创意带来了复杂的挑战。生成式 AI 模型需要在多样化的商品品类和广告场景中产出有吸引力、符合品牌调性的图像，同时还要让无论技术水平高低的广告主都能使用。质量保证与持续改进是图像和视频生成能力的基础。系统通过由 [Amazon SageMaker Ground Truth](https://aws.amazon.com/sagemaker-ai/groundtruth/) 支撑的广泛 HITL 流程不断改进。这一实现交付了一款强大的工具，重塑了广告主的创意流程，让高质量视觉内容创作在多样化的商品品类和场景中更易获得。

这只是 Amazon Ads 借助生成式 AI 赋能广告客户、帮他们创建推动广告目标所需内容的开始。该方案表明，降低创意门槛直接提升了广告活动活跃度，同时仍保持了负责任 AI 使用的高标准。

## 关键技术经验与讨论

非对话式应用受益于更高的延迟容忍度，从而支持批处理和缓存，但由于其自主运行的性质，需要健壮的校验机制和更强的防护栏。以下洞见同样适用于非对话式和对话式 AI 实现：

- **任务分解与 agentic 工作流 ——** 把复杂问题拆成更小的组件，在各实现中都体现出价值。这种由领域专家主导的刻意分解，使针对特定子任务的专用模型成为可能，正如 Amazon Pharmacy 的处方处理所示——经过微调的 SLM 处理剂量识别等离散任务。该策略允许使用具备清晰校验步骤的专用 agent，提升可靠性并简化维护。Amazon 卖家详情页用例通过其包含独立生成与验证过程的多步骤工作流印证了这一点。此外，评论摘要用例展示了如何通过用传统 ML 做预处理、并承担那些本可归为 LLM 任务的部分，实现对 LLM 高性价比且可控的使用。
- **混合架构与模型选择 ——** 将传统 ML 与 LLM 结合，比纯 LLM 方案提供更好的控制力和成本效益。传统 ML 擅长定义明确的任务，正如评论摘要系统在情感分析和信息抽取中的表现。Amazon 各团队根据需求有策略地部署大模型和小模型，并把 RAG 与微调结合，用于 Amazon Pharmacy 这类有效的领域特定应用。
- **成本优化策略 ——** Amazon 各团队通过批处理、面向高流量操作的缓存机制、[AWS Inferentia](https://aws.amazon.com/machine-learning/inferentia/) 和 [AWS Trainium](https://aws.amazon.com/ai/machine-learning/trainium/) 等专用实例类型以及经过优化的模型选择来实现效率。评论摘要展示了增量处理如何降低算力需求，Amazon Ads 则使用 Amazon Nova [基础模型](https://aws.amazon.com/what-is/foundation-models/)（FM）以高性价比的方式创建创意内容。
- **质量保证与控制机制 ——** 质量控制依赖通过 Amazon Bedrock Guardrails 实现的领域特定防护栏，以及把自动化测试与人工评估相结合的多层校验。在 Amazon 卖家详情页中，用于生成与验证的双 LLM 方法有助于防止幻觉，自反思技术则提升了准确性。Amazon Nova 创意 FM 自带负责任的 AI 控制，并辅以持续的 A/B 测试和性能度量。
- **HITL 实施 ——** HITL 方法跨越多个层次，从药师的专业评估到销售伙伴的终端用户反馈。Amazon 各团队建立了结构化的改进工作流，根据具体领域需求和风险状况在自动化与人工监督之间取得平衡。
- **负责任 AI 与合规 ——** 负责任 AI 实践包括面向受监管环境的内容摄取防护栏，以及遵守 HIPAA 等法规。Amazon 各团队为用户侧应用集成了内容审核，通过提供来源信息的访问入口在评论摘要中保持透明，并落实带监控的数据治理以提升质量与合规性。

这些模式让生成式 AI 方案在保持质量与责任标准的同时实现可扩展、可靠且高性价比。这些实现表明，有效的方案不仅需要精密的模型，还需要在 AWS 服务和既有实践的支持下，审慎关注架构、运营与治理。

## 后续步骤

本文分享的 Amazon.com 示例说明了生成式 AI 如何在传统对话式助手之外创造价值。我们邀请你借鉴这些示例或创建自己的方案，去发现生成式 AI 如何重塑你的业务乃至行业。你可以访问 [AWS 生成式 AI 用例](https://aws.amazon.com/ai/generative-ai/use-cases/)页面开始构思。

这些示例表明，有效的生成式 AI 实现往往受益于把不同类型的模型与工作流组合起来。要了解 AWS 服务支持哪些 FM，请参阅 [Amazon Bedrock 中支持的基础模型](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)和 [Amazon SageMaker JumpStart 基础模型](https://docs.aws.amazon.com/sagemaker/latest/dg/jumpstart-foundation-models.html)。我们还建议你探索 [Amazon Bedrock Flows](https://aws.amazon.com/bedrock/flows/)，它可以简化构建工作流的路径。此外提醒你，Trainium 和 Inferentia 加速器能在这些应用中带来可观的成本节省。

如我们的示例所示，agentic 工作流已被证明特别有价值。我们建议探索 [Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/)，以快速构建 agentic 工作流。

成功的生成式 AI 实现不止于模型选择——它代表着从实验到应用监控的完整软件开发过程。要开始在这些关键服务上打下基础，我们邀请你探索 [Amazon QuickStart](https://aws.amazon.com/events/quickstart/)。

## 结论

这些示例展示了生成式 AI 如何超越对话式助手，推动各行业的创新与效率。成功来自把 AWS 服务与扎实的工程实践和对业务的理解结合起来。归根结底，有效的生成式 AI 方案专注于解决真实的业务问题，同时保持高质量与责任标准。

想进一步了解 Amazon 如何使用 AI，请参阅 Amazon News 中的[人工智能](https://www.aboutamazon.com/news/tag/artificial-intelligence)栏目。

### 关于作者

![Burak](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2023/09/12/Burak.jpeg)**Burak Gozluklu** 是 AWS 上 Amazon.com 的首席 AI/ML 专业解决方案架构师兼 GenAI 科学家首席架构师，常驻马萨诸塞州波士顿。他帮助战略客户采用 AWS 技术，尤其是生成式 AI 方案，以实现其业务目标。Burak 拥有 METU 的航空航天工程博士学位、系统工程硕士学位，并在马萨诸塞州剑桥市的 MIT 完成系统动力学的博士后研究。他通过担任 MIT 的研究附属成员保持与学术界的联系。工作之外，Burak 是一位瑜伽爱好者。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/21/emilio-1.jpg) **Emilio Maldonado** 是 Amazon 的高级负责人，负责产品知识，致力于构建系统以扩展电商目录元数据、组织所有商品属性，并利用 GenAI 推断精准信息，引导卖家和购物者与商品互动。他热衷于打造充满活力的团队并建立合作关系。他拥有 Tecnologico de Monterrey（ITESM）的计算机科学理学学士学位和宾夕法尼亚大学沃顿商学院的 MBA 学位。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/21/wenchao.jpg)**Wenchao Tong** 是位于加州帕洛阿尔托的 Amazon Ads 的高级首席技术专家，负责牵头面向创意构建与效果优化的 GenAI 应用开发。他的工作让客户能够通过创新的 AI 技术提升创意表现与质量，从而增强商品与品牌认知并推动销售。Wenchao 拥有同济大学计算机科学硕士学位。工作之外，他喜欢徒步、桌游和与家人共度时光。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/21/Alexander.png)**Alexandre Alves** 是 Amazon Health Services 的高级首席工程师，专长于 ML、优化和分布式系统。他帮助交付以健康为本的体验。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/21/Puneet-1.jpg) **Puneet Sahni** 是 Amazon 的高级首席工程师。他致力于提升 Amazon 目录中所有商品的数据质量。他热衷于利用商品数据改善顾客体验。他拥有印度理工学院（IIT）孟买分校的电气工程硕士学位。工作之外，他喜欢与年幼的孩子共度时光和旅行。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/21/Vaughn-1.jpg) **Vaughn Schermerhorn** 是 Amazon 的总监，负责 Shopping Discovery and Evaluation，涵盖顾客评论、内容审核以及 Amazon 全球各站点的站内导航。他管理一个由应用科学家、工程师和产品负责人组成的多学科组织，专注于通过可扩展的 ML 模型、多模态信息检索和实时系统架构呈现可信的顾客洞察。他的团队开发并运营支撑每日数十亿次购物决策的大规模分布式系统。Vaughn 拥有乔治城大学和圣迭戈州立大学的学位，曾在美国、德国和阿根廷生活和工作。工作之外，他喜欢阅读、旅行和与家人共度时光。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/21/Tarik-1.png) **Tarik Arici** 是 Amazon Selection and Catalog Systems（ASCS）的首席应用科学家，负责使用 GenAI 工作流提升目录质量。他拥有佐治亚理工学院的电气与计算机工程博士学位。工作之外，Tarik 喜欢游泳和骑行。
