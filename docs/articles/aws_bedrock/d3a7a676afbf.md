---
vendor: aws_bedrock
title: Vxceed builds the perfect sales pitch for sales teams at scale using Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/vxceed-builds-the-perfect-sales-pitch-for-sales-teams-at-scale-using-amazon-bedrock
date: 2025-10-08
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: e3ee354599eb
---

# Vxceed 借助 Amazon Bedrock 为销售团队大规模打造完美销售话术

*本文与 Vxceed 的 Cyril Ovely 合写。*

快消品（CPG）公司在新兴经济体面临一个关键挑战：如何有效地留存收入并大规模提升客户忠诚度。尽管这些公司把收入的 15–20% 投入贸易促销和零售商忠诚度计划，但由于计划本身复杂、且难以照顾到单个零售商的需求，这些计划的参与率历来低于 30%。

[Vxceed](https://vxceed.com/) 的 Lighthouse 平台以其创新的忠诚度模块应对这一挑战。Lighthouse 获得东南亚、非洲和中东新兴经济体的领先全球快消品牌信赖，为一线销售团队提供前沿的、AI 驱动的工具集。该方案使用生成式 AI，基于单个零售商的数据和趋势生成个性化的销售话术，帮助一线代表有效触达零售商、回应常见异议并提升计划采用率。

在本文中，我们展示 Vxceed 如何借助 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 开发这套 AI 驱动的多 agent 方案，为一线销售团队大规模生成个性化的销售话术。

### 挑战：为品牌解决收入留存问题

Vxceed 的业务主要集中在新兴经济体。快消行业正面临持续变化、客户期望走高、进入门槛低等挑战。这些挑战在新兴经济体更为突出。为应对这些挑战，全球的快消公司每年把收入的 15–20% 投入贸易促销，形式往往是面向零售商的忠诚度计划。

然而，这类忠诚度计划历来参与率低于 30%，原因在于其复杂性，以及需要照顾到每个独立门店的需求。让这一挑战更复杂的是，在新兴经济体，这些忠诚度计划主要通过一线销售团队销售，而该团队同时承担订单采集与履约的角色，其业务规模常常覆盖数百万家门店。要提升忠诚度计划的参与率——进而提升品牌的收入留存——就需要在个性化层面量身定制计划，并向每一家门店恰当地推介。

Vxceed 需要一个能规模化解决该问题的方案，为一线销售团队可以推销的每一家门店量身定制独特、个性化的忠诚度计划销售故事。

这一挑战促使 Vxceed 采用 Amazon Bedrock——一项全托管服务，可通过单一 API 选用来自领先 AI 公司的高性能基础模型（FM）。

## 解决方案概述

为应对个性化、规模化以及把方案交到数万名一线销售团队手中的挑战，Vxceed 开发了 Lighthouse Loyalty Selling Story 这一 AI 驱动的解决方案。Lighthouse Loyalty Selling Story 的架构使用 Amazon Bedrock、Amazon API Gateway、Amazon DynamoDB 和 AWS Lambda，构建了一个安全、可扩展、AI 驱动的销售故事生成系统。该方案实现了多 agent 架构（如下图所示），其中每个组件都在客户私有的 AWS 环境中运行，从而保持数据安全、可扩展性和直观的用户交互。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/19/vxceed-cpg-arch-1-1024x503.png)
 该解决方案架构围绕若干关键组件构建，这些组件协同工作，为每个零售商客户提供独一无二的、精心编排的销售赋能体验：

- **销售员应用（Salesperson app）** – 一线销售团队使用一款移动应用获取有吸引力的计划销售话术，并通过聊天界面与系统交互。这是销售代表的主要触点。
- **API Gateway 与安全** – 该方案使用以下安全服务：API Gateway 作为应用交互的入口。安全通过以下方式强制实施：使用 [AWS Key Management Service](https://aws.amazon.com/kms/)（AWS KMS）做加密，使用 [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/) 做安全的凭证管理。[Amazon Simple Storage Service](https://aws.amazon.com/s3/)（Amazon S3）用于图片的存储与管理。
- **智能 agent** – 该方案使用以下基于 Lambda 的 agent：Orchestration Agent 协调组件之间的整体流程与交互。Story Framework Agent 建立叙事结构。Story Generator Agent 生成个性化内容。Story Review Agent 维护质量以及与品牌规范的合规性。Brand Guidelines Agent 保持品牌一致性。Business Rules Agent 执行业务逻辑与约束。
- **数据服务层** – 数据服务层由以下组件构成：Data API 服务提供对关键业务信息的访问，包括：门店画像数据 忠诚度计划详情 历史数据 采购画像信息 与 Lighthouse 的人工智能与机器学习（AI/ML）模型及数据湖集成，用于高级分析。[Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/) 用于增强上下文与信息。
- **高级能力** – 该方案还提供以下额外能力：Q&A Service 支持针对销售查询的自然语言交互。CTA（Call-to-Action，行动号召）服务简化零售门店的注册流程。Amazon Bedrock 大语言模型（LLM）为智能回复提供动力。[Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/) 促成恰当且符合合规要求的交互。

该架构实现了安全、可扩展的无服务器设计，使用 AWS 托管服务交付一套成熟的销售赋能方案。

## 面向安全编排的多 agent AI 架构

Vxceed 在 Lambda 上构建了一个多 agent AI 系统来管理个性化的销售故事讲述。该架构由多个专用 agent 组成，它们协同创建、校验并交付有吸引力的销售话术，同时与业务规则和品牌规范保持一致。

以下是该多 agent AI 架构的详细拆解：

- **Orchestration Agent** – 协调各 agent 之间的工作流，管理整体的故事创建过程，并与 Amazon Bedrock LLM 对接以完成智能处理。
- **Story Framework Agent** – 基于经过验证的故事讲述模式和销售方法论，建立销售话术的叙事结构与流程。
- **Story Generator Agent** – 通过整合多个来源的数据（包括门店画像、忠诚度计划详情和历史数据）生成个性化内容。
- **Story Review Agent** – 在交付给销售人员之前，校验生成内容在准确性、完整性和有效性方面的表现。
- **Brand Guidelines Agent** – 确保生成内容符合品牌语调、语气和视觉标准。
- **Business Rules Agent** – 在生成内容中执行业务逻辑、客户品牌合规要求和运营约束。

每个 agent 都实现为一个无服务器 Lambda 函数，从而实现可扩展且高性价比的处理，同时通过与 AWS KMS 和 Secrets Manager 集成来维持严格的安全控制。这些 agent 与 Amazon Bedrock LLM 和 guardrails 交互，以提供恰当且负责任的 AI 生成内容。

## Guardrails 防护机制

Lighthouse 使用 Amazon Bedrock Guardrails 来维持专业、聚焦的交互。系统使用拒绝话题（denied topics）和词过滤器，帮助阻止无关讨论和不专业用语，确保对话始终围绕客户需求。这些 guardrails 会筛除不当内容、围绕敏感话题划定清晰边界，并在与组织价值观保持一致的前提下得体地回应竞争性询问。

## Vxceed 为何选择 Amazon Bedrock

Vxceed 选择 Amazon Bedrock 而非其他 AI 方案，是因为四项关键优势：

- **企业级安全与隐私** – 借助 Amazon Bedrock，你可以配置 AI 工作负载和数据，使信息安全地留在你自己的虚拟私有云（VPC）内。这种方式为 AI 操作维持私密、加密的环境，有助于让数据在你的 VPC 内受到保护并保持隔离。更多细节请参阅 Security in Amazon Bedrock。
- **AWS 上的托管服务** – Lighthouse Loyalty Selling Story 运行在 Vxceed 既有的 AWS 基础设施上，把集成工作量降到最低，并使用 Amazon Bedrock 等托管服务实现端到端的数据与运营控制。
- **可访问多种 AI 模型** – Amazon Bedrock 支持多种基础模型，因此 Vxceed 可以针对不同用例进行试验并优化性能。Vxceed 使用 Anthropic 的 Claude 3.5 Sonnet，因为它在处理复杂的对话式交互和复杂语言处理任务上表现出色。
- **强大的 AI 开发工具** – Vxceed 通过使用 Amazon Bedrock Knowledge Bases、prompt 工程库和 agent 框架实现高效的 AI 编排，从而加快了开发速度。

## 业务成效与未来展望

该实施在三个关键领域带来了显著且可衡量的改进。

## 增强的客户服务

该方案达到 95% 的回复准确率，同时把 90% 的忠诚度计划相关查询实现自动化。这种自动化有助于对客户异议和查询给出连贯、准确的回复，帮到销售人员，也显著改善了零售商体验。

### 加速的收入增长

早期客户反馈和行业分析表明，计划注册量增长了 5–15%。这一增长说明，消除注册流程中的摩擦会直接影响业务结果。

### 提升的运营效率

该方案带来了可观的运营收益：

- 注册处理时间缩短 20%
- 支持所需时间减少 10%
- 每个地理区域每年在行政开销上节省 2 个人月

这些效率提升帮助 Vxceed 的客户专注于更高价值的活动，同时降低运营成本。更快的处理与更低的支持需求相结合，为计划增长打下了可扩展的基础。

## 结语

AWS 与 Vxceed 合作支持其 AI 战略，最终开发出 Lighthouse Loyalty Selling Story 这一创新的个性化销售话术方案。借助 Amazon Bedrock 和 Lambda 等 AWS 服务，Vxceed 成功构建了一个安全的、AI 驱动的方案，为快消行业的一线销售团队大规模生成个性化销售故事。展望未来，Vxceed 计划通过以下方式进一步完善 Lighthouse Loyalty Selling Story：

- 优化 AI 推理成本，以提升可扩展性和成本效益
- 新增 Language Agent，以用户所选母语呈现生成的销售故事
- 引入 RAG 和 GraphRAG，进一步增强故事生成效果

通过这一合作，Vxceed 旨在显著改善快消行业的一线销售管理，为快消公司和品牌交付安全、高效、AI 驱动的方案。

如果你有兴趣实施类似的 AI 驱动方案，可以先了解如何使用 Amazon Bedrock 实现异步 AI agent。参见[使用 Amazon Bedrock 创建异步 AI agent](https://aws.amazon.com/blogs/machine-learning/creating-asynchronous-ai-agents-with-amazon-bedrock/)，了解多 agent 系统的实现模式，并为你的组织开发安全、AI 驱动的方案。

### 关于作者

| ![Roger Wang](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/19/yibowang.jpg) | Roger Wang 是 AWS 的高级解决方案架构师。他是一位资深架构师，在软件行业拥有 20 多年经验。他帮助新西兰及全球的软件与 SaaS 公司利用 AWS 的前沿技术解决复杂的业务挑战。Roger 热衷于弥合业务驱动因素与技术能力之间的差距，并乐于推动能带来实际影响的对话。 |
| --- | --- |
| ![Deepika Kumar](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/19/awsdeep.jpg) | Deepika Kumar 是 AWS 的解决方案架构师。她在技术行业拥有 13 年以上经验，帮助企业和 SaaS 组织在云上构建并安全部署其工作负载。她热衷于以负责任的方式使用生成式 AI，无论是推动产品创新、提升生产力，还是改善客户体验。 |
| ![Jhalak Modi](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/19/jhalaknz.jpg) | Jhalak Modi 是 AWS 的解决方案架构师，专长于云架构、安全和 AI 驱动的解决方案。她帮助企业在 AWS 上构建安全、可扩展且创新的解决方案。Jhalak 对新兴技术充满热情，积极分享自己在云计算、自动化和负责任 AI 采用方面的专业知识，帮助组织加速数字化转型，并在快速演进的技术格局中保持领先。 |
| ![Cyril Ovely](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/19/cyril-vxceed.jpg) | Cyril Ovely 是 Vxceed Software Solutions 的 CTO 兼联合创始人，负责公司面向快消品牌的 SaaS 物流解决方案。他拥有 33 年经验，其中 22 年在 Vxceed，此前从事分析与过程控制仪表相关工作。Cyril 是工程师出身，负责设计 Vxceed 的 SaaS 产品，并以新西兰奥克兰为基地推动创新。 |
