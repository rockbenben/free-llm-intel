---
vendor: aws_bedrock
title: How PayU built a secure enterprise AI assistant using Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/how-payu-built-a-secure-enterprise-ai-assistant-using-amazon-bedrock
date: 2025-07-15
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 9a3fb749f1a1
---

# PayU 如何用 Amazon Bedrock 构建安全的企业级 AI 助手

*这是一篇客座文章，由 PayU 的 Rahul Ghosh、Sandeep Kumar Veerlapati、Rahmat Khan 与 Mudit Chopra 共同撰写。*

[PayU](https://payu.in/) 提供全栈数字金融服务系统，通过技术满足商户、银行与消费者的金融需求。

作为印度一家受中央银行监管的金融机构，我们近来观察到员工对使用公共[生成式 AI](https://aws.amazon.com/generative-ai/)助手的兴趣激增。团队发现这些 AI 助手在各种任务上都有帮助，包括通过分享错误或异常详情来排查技术问题、撰写邮件回复，以及为内部与对外沟通润色英文内容。然而，这种对公共生成式 AI 工具日益增长的依赖，很快就为我们的信息安全（Infosec）团队敲响了警钟。我们越来越担心敏感数据——例如专有系统信息、机密的客户详情与受监管的文档——被传输给外部第三方 AI 提供方并由其处理的风险。鉴于严格的合规要求以及金融行业数据隐私的极端重要性，我们决定限制对这些公共生成式 AI 系统的访问。此举对于保护组织免遭潜在数据泄露与监管违规是必要的，但它也凸显出我们需要一个安全、符合合规要求的替代方案，让我们既能利用生成式 AI 的种种好处，又不必在安全策略上妥协。

在本文中，我们说明如何在不违背数据驻留要求的前提下，借助 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 为 PayU 团队提供企业级 AI 方案，并让 AI 访问实现民主化。

## 方案概述

作为受监管实体，我们必须把所有数据保留在印度境内，并安全地限制在 PayU 的虚拟私有云（VPC）之内。因此，我们寻找的方案需要既能借助生成式 AI 的力量促进创新、提升运营效率，同时又能实现稳健的数据安全措施与所用数据的地理围栏。除技术排障、邮件起草与内容润色等基础用例之外，我们还希望为团队提供一个自然语言界面，用以跨领域查询企业数据。这包括以直观的对话式交互，自助获取业务关键洞察——例如贷款放款趋势、还款模式、客户人口统计与交易分析——以及 HR 政策解读。我们的愿景是让员工从内部系统获得即时、由 AI 驱动的答案，而不把敏感数据暴露给外部系统，从而与印度的金融监管规定和我们的内部治理框架保持一致。

我们选择 Amazon Bedrock，因为它是一项全托管服务，可访问来自 AI21 Labs、Anthropic、Cohere、DeepSeek、Luma、Meta、Mistral AI、poolside（即将推出）、Stability AI、TwelveLabs（即将推出）、Writer 与 Amazon 等行业领导者的多种高性能基础模型（FM）。这些模型可通过单一的统一 API 访问。Amazon Bedrock 还提供了一整套契合我们需求的功能，包括用于工作流自动化的 [Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/) 与用于企业数据集成的 [Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/)。此外，[Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/) 在模型、prompt 与应用层面提供必要的防护，用于拦截不受欢迎的有害多模态内容，并帮助过滤掉我们检索增强生成（RAG）与 agentic 工作流中的幻觉回复。

在前端方面，我们选择了 [Open WebUI](https://openwebui.com/)，这是一个以可扩展性、丰富功能集与直观易用界面著称的开源方案，让我们的团队可以与我们集成的 AI 能力无缝交互。

下图展示了该方案的架构。

[![PayU AI 助手方案架构](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/08/ml-19011-solution_architecture.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/08/ml-19011-solution_architecture.png)

在以下章节中，我们将更详细地讨论该方案的关键组成部分。

## Open WebUI

我们使用 Open WebUI 作为基于浏览器的前端应用。Open WebUI 是一个开源、自托管的应用程序，旨在提供一个用户友好、功能丰富的界面，用于与大语言模型（LLM）交互。它支持与广泛的模型集成，并可部署在私有环境中，以帮助保护数据隐私与安全。Open WebUI 支持单点登录（SSO）等企业功能，用户可以用组织的身份提供方无缝完成身份验证，从而简化访问并降低与密码相关的风险。该服务还提供基于角色的访问控制（RBAC），管理员可以定义细粒度的用户角色——例如 admin 与 user——从而按组织需求定制权限、模型访问与数据可见性。这有助于保护敏感信息。

我们把 Open WebUI 与身份提供方连接起来以启用 SSO。RBAC 则通过定义与用户岗位职能直接绑定的功能角色来实现——例如贷款运营或 HR 支持。这些角色决定了访问特定 agent、知识库与 FM 的权限，使团队只能访问与其职责相关的工具。配置、用户对话历史与使用指标都安全地存储在持久化的 [Amazon Relational Database Service（Amazon RDS）for PostgreSQL](https://aws.amazon.com/rds/postgresql/) 数据库中，从而具备审计就绪能力并支持合规。在部署方面，我们把 Open WebUI 容器化，并在 [Amazon Elastic Kubernetes Service](https://aws.amazon.com/eks/)（Amazon EKS）集群上编排运行，利用自动伸缩根据需求动态调整资源，同时保持高可用性。

## Access Gateway

Access Gateway 充当 Open WebUI 与 Amazon Bedrock 之间的中介，把 Amazon Bedrock 的 API 转换为 Open WebUI 可兼容的 schema。该组件让前端可以访问 FM、Amazon Bedrock Agents 与 Amazon Bedrock Knowledge Bases。

## Amazon Bedrock

Amazon Bedrock 提供多种多样的 FM，我们已把它们集成到 Web UI 中，使 PayU 的员工能够高效完成文本摘要、邮件起草与技术排障等任务。此外，我们使用 Amazon Bedrock Agents 与 Amazon Bedrock Knowledge Bases，基于我们的组织数据开发了自定义 AI agent。这些量身定制的 agent 同样可以通过前端应用访问。

为实现安全、基于角色的组织洞察访问，我们针对具体业务职能部署了专门的 agent——包括 `hr-policy-agent`、`credit-disbursal-agent`、`collections-agent` 与 `payments-demographics-agent`。对这些 agent 的访问由用户角色与岗位职能管控。这些 agent 结合使用 RAG 与 text-to-SQL 两种方式。例如，`hr-policy-agent` 使用 RAG，查询 [Amazon OpenSearch Service](https://aws.amazon.com/opensearch-service/) 中的向量化知识库；而 `credit-disbursal-agent` 使用 text-to-SQL pipeline，把自然语言查询转换为结构化 SQL 命令，从基于 [Amazon Simple Storage Service](https://aws.amazon.com/s3/)（Amazon S3）的数据湖中提取洞察。这些方式在维持数据治理的同时提供精确、上下文感知的回复。text-to-SQL 工作流的实施细节如下图所示。

[![PayU 使用 Bedrock Agents 与 Knowledge Bases 的 text-to-SQL](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/08/ml-19011-text_to_sql.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/08/ml-19011-text_to_sql.png)

该工作流包含以下步骤：

- 我们在 Amazon S3 的数据湖仓中维护面向具体业务的数据集市（datamart），为其充实丰富的元数据，并以高度反规范化的形式呈现。这个内部称为 Luna 的数据湖仓使用 [Apache Spark](https://spark.apache.org/) 与 [Apache Hudi](https://hudi.apache.org/) 构建。数据集市对于在我们的系统中获得更高准确率与更优性能至关重要。这些数据以 [AWS Glue](https://aws.amazon.com/glue/) 表的形式暴露，充当 Hive Metastore，并可用 [Amazon Athena](https://aws.amazon.com/athena/) 查询，从而为我们的业务需求提供高效的访问与分析能力。
- HR 政策文档存放在另一个 S3 桶中。使用 Amazon Bedrock Knowledge Bases，这些文档被向量化并存入 OpenSearch Service。
- 员工可以依据自己的角色，通过 Open WebUI 界面访问 FM 与 agent。他们可以在下拉菜单中选择 FM 或 agent。当用户选择 FM 时，问题直接使用该模型的预训练知识来回答，不涉及 agent。若选择了 agent，则调用对应的 agent 来处理请求。
- 为便于编排，会向 Amazon Bedrock agent 提供一段指令 prompt。该 agent 解读这一 prompt，并通过把具体动作委派给底层 LLM 来管理工作流。在此过程中，Amazon Bedrock agent 协调任务的执行，使每一步都根据收到的输入与为工作流定义的编排逻辑得到恰当处理。编排步骤可以从知识库中提取上下文，或调用某个动作组。会向 Amazon Bedrock agent 提供一段指令 prompt 来引导编排过程。该 agent 解读这一 prompt，并通过把具体任务分配给 LLM 来协调工作流。例如，在调用 text-to-SQL agent 的动作时，它被指示先检查语法，通过读取错误来修复查询，然后才执行最终查询。
- 会向 Amazon Bedrock agent 提供一段指令 prompt，以引导编排过程。该 agent 解读这一 prompt，并通过把具体任务分配给 LLM 来协调工作流。
- Amazon Bedrock agent 中动作组（action group）的主要功能，是针对用户的输入或请求组织并执行多个动作。这使 agent 能够执行一系列协同的步骤来有效满足用户需求，而不局限于单个动作。每个动作组都包含一个 schema，用于定义所需的格式与参数。该 schema 让 agent 能够通过提供所需的通信结构，与计算层（例如 [AWS Lambda](https://aws.amazon.com/lambda) 函数）进行准确交互。
- Lambda 函数充当执行引擎，运行 SQL 查询并与 Athena 连接以处理数据。为实现安全高效的运行，正确配置资源策略与权限至关重要，这有助于维持无服务器计算环境的完整性。
- Athena 是一项无服务器查询服务，它使用标准 SQL 分析 Amazon S3 中的数据，并由 AWS Glue 管理数据目录。AWS Glue 从 Amazon S3 读取数据、为 Athena 创建可查询的表，并把查询结果存回 Amazon S3。这一由 crawler 与 AWS Glue Data Catalog 支持的集成，简化了数据管理与分析。
- 对于与 HR 政策及其他企业文档相关的问题，系统使用 Amazon Bedrock Knowledge Bases。这些知识库基于存放在 Amazon S3 中的 HR 政策文档构建，语义搜索能力由 OpenSearch Service 中的向量嵌入驱动。

## 对基础模型的私有访问

由于我们的组织数据会作为上下文被包含在发往 Amazon Bedrock 的 prompt 中，且生成的回复可能含有敏感信息，我们需要一套稳健的方案来帮助防止这些数据暴露到公网。我们的目标是建立一道安全的数据边界，以帮助降低与面向互联网的通信相关的潜在风险。为此，我们实施了 [AWS PrivateLink](https://aws.amazon.com/privatelink/)，在我们的 VPC 与 Amazon Bedrock 之间建立私有的专用连接。采用这一配置后，Amazon Bedrock 就像位于我们自己 VPC 内一样可被访问，不再需要互联网网关或 NAT 网关。通过在 PrivateLink 上设置接口端点，我们直接在 VPC 子网中配置了网络接口，使数据安全地留在 AWS 网络内。这一架构不仅通过最小化外部暴露强化了我们的安全态势，也简化了内部应用的连接。

下图展示了这一架构。

[![PayU 通过 AWS PrivateLink 实现 Bedrock 安全访问](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/08/ml-19011-bedrock_private_connection.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/08/ml-19011-bedrock_private_connection.png)

## 结语

该应用的引入在 PayU 内部激发了对生成式 AI 的浓厚兴趣。员工如今更清楚地认识到 AI 在应对复杂业务挑战方面的潜力。这股热情促使多个业务工作流被加入该应用。业务部门与技术团队之间的协作加快了数字化转型的步伐。上线之后，内部估算显示业务分析师团队的生产力提升了 30%。这一效率提升让分析师得以专注于更具战略性的任务，并缩短了交付周期。总体而言，该应用在全组织范围内培养了创新与持续学习的文化。

准备好把你所在组织的 AI 能力提升到新水平了吗？在 [Amazon Bedrock 用户指南](https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html)中深入了解 Amazon Bedrock、Amazon Bedrock Agents 与 Amazon Bedrock Guardrails 的技术细节，并在 [Amazon Bedrock Agent GitHub 仓库](https://github.com/awslabs/amazon-bedrock-agent-samples)中探索动手示例，快速启动你的实施。

### 关于作者

**[![Deepesh Dhapola](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/02/25/dhapola.jpeg)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/02/25/dhapola.jpeg) Deepesh Dhapola** 是 AWS 印度的高级解决方案架构师，为金融服务与金融科技组织设计高性能、有韧性的云解决方案。他专长于运用先进 AI 技术——包括生成式 AI、智能 agent 与 Model Context Protocol（MCP）——设计安全、可扩展、上下文感知的应用。Deepesh 在机器学习方面具备深厚专长，并密切关注新兴趋势，通过整合前沿 AI 能力推动数字化转型，为 AWS 客户提升运营效率、促进创新。技术之外，他喜欢与家人共度美好时光，并探索富有创意的烹饪技法。

**[![Rahul Ghosh](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/08/rahul.jpeg)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/08/rahul.jpeg) Rahul Ghosh** 是一位资深的数据与 AI 工程师，在基于云的数据架构、大规模数据处理以及包括生成式 AI、LLM、检索增强生成（RAG）与基于 agent 的系统在内的现代 AI 技术方面拥有深厚专长。他的技术工具箱横跨 Python、SQL、Spark、Hudi、Airflow、Kubeflow 及其他现代编排框架，并在 AWS、Azure 与开源系统上具备实践经验。Rahul 热衷于在数据与智能的交汇处构建可靠、可扩展且合乎伦理的解决方案。工作之外，他喜欢指导初入行的技术人，并从事扎根于其家乡孟加拉农村的社会工作。

**[![Sandeep Kumar Veerlapati](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/08/ML-19011-Sandeep.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/08/ML-19011-Sandeep.png) Sandeep Kumar Veerlapati** 是 PayU Finance 的数据工程副总监，专注于打造强大、高绩效的团队并制定有效的数据策略。他在云数据系统、数据架构与生成式 AI 方面具备专长，在打造可扩展且有影响力的解决方案上经验丰富。他的技术背景扎实，熟悉 Spark、Airflow、Hudi 与 AWS Cloud 等工具。他热衷于通过数据交付价值，乐于带领团队解决现实世界的挑战。工作之外，Sandeep 喜欢指导他人、协作，以及寻找用技术创新的新方式。

**[![Mudit Chopra](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/08/ML-19011-mudit-chopra.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/08/ML-19011-mudit-chopra.png) Mudit Chopra** 是一位熟练的 DevOps 工程师与生成式 AI 爱好者，专长于自动化工作流、构建稳健的 CI/CD pipeline，以及跨系统管理基于云的基础设施。他热衷于简化交付 pipeline、促进跨团队协作，帮助实现顺畅的产品部署。他致力于持续学习与创新，乐于使用 AI 驱动的工具提升运营效率、打造更智能更敏捷的系统。他始终紧跟技术趋势，致力于推动数字化转型并交付有影响力的解决方案。

**[![Rahmat Khan](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/08/ML-19011-Rahmat-Khan.jpeg)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/08/ML-19011-Rahmat-Khan.jpeg) Rahmat Khan** 是一位进取的 AI 与机器学习工程师兼创业者，深度专注于构建智能的真实世界系统。他的工作横跨完整的 ML 生命周期——数据工程、模型开发与规模化部署——并在实际的 AI 应用上有扎实根基。多年来，他从生成模型到多模态系统都有探索，并着眼于创造无缝的用户体验。在好奇心与对实验的热爱的驱动下，他乐于解决开放式问题、快速交付，并从可能性的边界中学习。技术之外，他对培育想法、指导同伴同样充满热情，并始终把握我们为何而构建的更大图景。

** [![Saikat Dey](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/08/saikat.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/08/saikat.png)Saikat Dey** 是 AWS 印度的技术客户经理（TAM），为战略金融科技客户提供支持，帮助他们借助云的力量推动创新与业务转型。作为可信赖的顾问，他连接技术团队与业务团队，提供架构最佳实践、主动指引与战略洞察，帮助客户在 AWS 上取得长期成功。凭借对生成式 AI 的强烈热情，Saikat 与客户合作识别高影响力用例，并借助 Amazon Bedrock 与 Amazon Q 等服务加速他们对生成式 AI 方案的采用。工作之外，他积极探索新兴技术、关注创新趋势，并喜欢通过旅行体验多元文化与视角。
