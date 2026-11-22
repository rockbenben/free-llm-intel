---
vendor: aws_bedrock
title: Choosing the right approach for generative AI-powered structured data retrieval
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/choosing-the-right-approach-for-generative-ai-powered-structured-data-retrieval
date: 2025-07-01
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 51c3aab920f6
---

# 为生成式 AI 驱动的结构化数据检索选择合适的方案

组织希望直接获得业务问题的答案，而不必编写 SQL 查询，也不必在商业智能（BI）仪表板中穿梭以从结构化数据存储中提取数据。结构化数据的示例包括符合预定义 schema 的表、数据库和数据仓库。由大语言模型（LLM）驱动的自然语言查询系统改变了我们与数据交互的方式，因此你可以问“哪个区域的收入最高？”，并立即得到有见地的回答。实现这些能力需要仔细考量你的具体需求——无论你是需要整合来自其他系统（例如文档这类非结构化来源）的知识、服务内部还是外部用户、处理问题的分析复杂度，还是为业务适宜性定制回答，等等。

在本文中，我们讨论 AWS 中由 LLM 驱动的结构化数据查询模式。我们提供一个决策框架，帮助你针对具体用例选出最佳模式。

## 业务挑战：让结构化数据易于访问

组织拥有海量的结构化数据，但出于几个原因，难以让非技术用户有效访问这些数据：

- 业务用户缺乏查询数据所需的技术知识（例如 SQL）
- 员工依赖 BI 团队或数据科学家进行分析，限制了自助服务能力
- 获取洞察往往伴随时间延迟，影响决策
- 预定义仪表板限制了对数据的自发性探索
- 用户可能不知道能问哪些问题，也不知道相关数据存放在哪里

## 解决方案概览

有效的解决方案应提供以下能力：

- 对话式界面，让员工无需技术专长即可查询结构化数据源
- 能够用日常语言提问，并获得准确、可信的答案
- 自动生成可视化与解释，以清晰传达洞察。
- 整合来自不同数据源（结构化和非结构化）的信息，并以统一方式呈现
- 易于与既有投资集成，并具备快速部署能力
- 基于身份、角色和权限的访问限制

在以下各节中，我们探讨五种可以满足这些需求的模式，并分别说明每种方案的架构、理想用例、优势、注意事项和实施资源。

## 模式 1：使用企业助手的直接对话式界面

此模式使用 [Amazon Q Business](https://aws.amazon.com/q/business/)——一个由生成式 AI 驱动的助手——在具有原生连接器的数据源之上提供聊天界面。当用户用自然语言提问时，Amazon Q Business 会连接数据源、解释问题并检索相关信息，无需中间服务。下图展示了此工作流。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/01/ML_18613_pattern-1.png)

这种方法非常适合需要在统一体验中回答业务用户关于结构化和非结构化数据源问题的内部企业助手。例如，HR 人员可以问“我们的育儿假政策是什么，上季度有多少员工使用了它？”，并在一次交互中同时从休假政策文档和员工数据库获得答案。采用此模式，你可以获得以下好处：

- 通过 Amazon Q Business 丰富的内置连接器库简化连接
- 只需配置和管理一个服务，实施流程精简
- 统一的搜索体验，可同时访问结构化和非结构化信息
- 内置理解并遵循既有身份、角色和权限

你可以通过 SQL 查询的形式定义要拉取的数据范围。Amazon Q Business 根据定义的 SQL 查询预先索引数据库内容，并在回答用户问题时使用该索引。同样，你可以定义同步模式和计划，以决定希望多久更新一次索引。Amazon Q Business 承担了繁重的工作：使用检索增强生成（RAG）方法为数据建立索引，并使用 LLM 生成文笔良好的答案。有关如何为 [Amazon Aurora PostgreSQL-Compatible Edition](https://aws.amazon.com/rds/aurora/postgresql-features/) 连接器设置 Amazon Q Business 的更多详细信息，请参阅 [Discover insights from your Amazon Aurora PostgreSQL database using the Amazon Q Business connector](https://aws.amazon.com/blogs/machine-learning/discover-insights-from-your-amazon-aurora-postgresql-database-using-the-amazon-q-business-connector/)。你也可以查阅[受支持数据源连接器](https://docs.aws.amazon.com/amazonq/latest/qbusiness-ug/connectors-list.html)的完整列表。

## 模式 2：为 BI 工具增强自然语言查询能力

此模式使用 [AWS Quick Sight](https://aws.amazon.com/quicksight/q/) 对先前已在 [AWS Quick Sight](https://aws.amazon.com/quicksight) 中配置好的数据集处理自然语言查询。用户可以在 Quick Sight 界面内用日常语言提问，无需编写 SQL 即可获得可视化答案。此方法适用于 Quick Sight（Enterprise 或 Q 版），并支持多种数据源，包括 [Amazon Relational Database Service](https://aws.amazon.com/rds/)（Amazon RDS）、[Amazon Redshift](https://aws.amazon.com/redshift)、[Amazon Athena](https://aws.amazon.com/athena) 等。下图描绘了该架构。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/01/ML_18613_pattern-2.png)

此模式非常适合内部 BI 和分析用例。业务分析师、高管和其他员工可以提出临时问题，以仪表板形式即时获得可视化洞察。例如，高管可以问“上季度按收入排名前 5 的区域是哪些？”，并立即看到响应式图表，从而减少对分析团队的依赖。此模式的优势如下：

- 它支持生成丰富可视化与图表的自然语言查询
- 无需编码或机器学习（ML）经验——自然语言解释和 SQL 生成等繁重工作由 AWS Quick Sight 负责
- 它可无缝集成到熟悉的 Quick Sight 仪表板环境中

现有 Quick Sight 用户可能会发现，这是利用生成式 AI 优势最直接的方式。你可以通过配置主题（例如精选字段、同义词和预期提问措辞）来优化此模式，以获得更高质量的结果。此模式只会从 Quick Sight 中特定配置的数据源拉取数据，并以仪表板作为输出。更多详细信息，请查看 [Quick Sight DemoCentral](https://democentral.learnquicksight.online/)，在 Quick Sight 中观看演示、查看生成式 BI 学习仪表板，并查看使用 Amazon Q 创建仪表板的引导式说明。另请参阅[受支持数据源](https://docs.aws.amazon.com/quicksight/latest/user/supported-data-sources.html)列表。

## 模式 3：将 BI 可视化与对话式 AI 结合，打造无缝体验

此模式将 BI 可视化能力与对话式 AI 融合，创造无缝的知识体验。通过将 [AWS Quick Sight](https://docs.aws.amazon.com/quicksight/latest/user/generative-bi-q-business.html) 与 [Amazon Q Business](https://aws.amazon.com/q/business/)（启用 Quick Sight 插件）集成，组织可以为用户提供统一的对话式界面，同时利用非结构化和结构化数据。下图展示了该架构。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/01/ML_18613_pattern-3a.png)

这非常适合希望内部 AI 助手回答各种问题的企业——无论是数据库中的指标，还是文档中的知识。例如，高管可以问“我们第四季度的收入增长如何？”，并通过 Quick Sight 看到来自 Amazon Redshift 数据仓库的可视化结果，然后紧接着问“我们公司的休假政策是什么？”以查阅 HR 文档——全部在同一对话流中完成。此模式具有以下优势：

- 它在单一应用中统一来自结构化数据（数据库和数据仓库）和非结构化数据（文档、wiki、电子邮件）的答案
- 它在对话式回答之外提供丰富的可视化，在聊天中实现实时分析的无缝体验
- 没有重复劳动——如果你的 BI 团队已在 Quick Sight 中为分析构建了数据集和主题，你可以直接在 Amazon Q Business 中使用它们
- 在数据类与文档类询问之间切换时，它能保持对话上下文

更多详细信息，请参阅 [Query structured data from Amazon Q Business using AWS Quick Sight integration](https://aws.amazon.com/blogs/machine-learning/query-structured-data-from-amazon-q-business-using-amazon-quicksight-integration/) 和 [Amazon Q Business now provides insights from your databases and data warehouses (preview)](https://aws.amazon.com/about-aws/whats-new/2024/12/amazon-q-business-insights-databases-data-warehouses-preview/)。

此模式的另一种变体推荐给希望在 Quick Sight 中通过丰富可视化呈现统一数据的 BI 用户，如下图所示。

![使用混合方案选项 2 的结构化数据检索](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/01/ML_18613_pattern3b-1.png)

更多详细信息，请参阅 [Integrate unstructured data into AWS Quick Sight using Amazon Q Business](https://aws.amazon.com/blogs/business-intelligence/integrate-unstructured-data-into-amazon-quicksight-using-amazon-q-business/)。

## 模式 4：使用托管 text-to-SQL 从结构化数据构建知识库

此模式使用 [Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/) 实现[结构化数据检索](https://aws.amazon.com/about-aws/whats-new/2024/12/amazon-bedrock-knowledge-bases-structured-data-retrieval/)。该服务提供一个全托管的 text-to-SQL 模块，可缓解为结构化数据开发自然语言查询应用时的常见挑战。此实现使用 [Amazon Bedrock](https://aws.amazon.com/bedrock/)（[Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/) 和 Amazon Bedrock Knowledge Bases）以及你选择的数据仓库，例如 Amazon Redshift 或 [Amazon SageMaker Lakehouse](https://aws.amazon.com/sagemaker/lakehouse/)。下图展示了该工作流。

![使用 Amazon Bedrock Knowledge Bases 进行结构化数据检索](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/01/ML_18613_pattern4.png)

例如，卖家可以将此能力嵌入电子商务应用，提出诸如“给我去年销售额相比前一年增长 50% 的前 5 个产品？另外按产品类别对结果分组。”的复杂查询。系统会自动生成相应的 SQL，对数据源执行该查询，并返回结果或一段摘要叙述。此模式具有以下优势：

- 它提供全托管的 text-to-SQL 能力，无需模型训练
- 它支持无需数据移动即可直接查询源中的数据
- 它支持对仓库数据的复杂分析查询
- 它通过 Amazon Bedrock 灵活选择 foundation model（FM）
- API 连接、个性化选项和上下文感知的聊天功能，使其更适合面向客户的应用

当你需要灵活、面向开发者的解决方案时，请选择此模式。这种方法适合你能够控制 UI 设计的应用（内部或外部）。默认输出主要是文本或结构化数据。然而，对 text-to-SQL 应用而言，执行任意 SQL 查询可能带来安全风险。建议你按需采取预防措施，例如使用受限角色、只读数据库和沙箱。有关如何构建此模式的更多信息，请参阅 [Empower financial analytics by creating structured knowledge bases using Amazon Bedrock and Amazon Redshift](https://aws.amazon.com/blogs/big-data/empower-financial-analytics-by-creating-structured-knowledge-bases-using-amazon-bedrock-and-amazon-redshift/)。有关受支持的结构化数据存储列表，请参阅 [Create a knowledge base by connecting to a structured data store](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-structured-create.html)。

## 模式 5：可灵活选择模型的自定义 text-to-SQL 实现

此模式代表一种自建方案：使用 FM 将自然语言转换为 SQL，对数据仓库执行查询并返回结果。当你希望在没有深厚 ML 专业知识的情况下快速集成此能力时，请选择 Amazon Bedrock——它通过统一 API 提供开箱即用 FM 的全托管服务，并以按需付费定价处理基础设施需求。或者，当你需要大量模型定制来构建特定需求时，请选择 [Amazon SageMaker AI](https://aws.amazon.com/sagemaker-ai/)——它为数据科学家和 ML 工程师提供完整的 ML 生命周期工具，以便以更高的控制度构建、训练和部署自定义模型。更多信息，请参阅我们的 [Amazon Bedrock 或 Amazon SageMaker AI 决策指南](https://docs.aws.amazon.com/decision-guides/latest/bedrock-or-sagemaker/bedrock-or-sagemaker.html)。下图展示了该架构。

![使用 Amazon Bedrock 或 Amazon SageMaker AI 进行结构化数据检索](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/01/ML_18613_pattern-5.png)

如果你的用例需要特定的开放权重模型，或者你希望在自己的领域数据上微调模型，请使用此模式。例如，如果你需要查询结果高度准确，可以使用此模式在特定的 schema 结构上微调模型，同时保持与现有工作流和多云环境集成的灵活性。此模式具有以下优势：

- 它在模型选择、微调和系统设计方面提供最大程度的定制
- 它支持跨多个数据源的复杂逻辑
- 它在你的虚拟私有云（VPC）中提供对安全与部署的完全控制
- 它支持灵活的接口实现（Slack bot、自定义 Web UI、notebook 插件）
- 你可以将其用于面向外部用户的解决方案

有关构建此模式步骤的更多信息，请参阅 [Build a robust text-to-SQL solution generating complex queries, self-correcting, and querying diverse data sources](https://aws.amazon.com/blogs/machine-learning/build-a-robust-text-to-sql-solution-generating-complex-queries-self-correcting-and-querying-diverse-data-sources/)。

## 模式对比：做出正确选择

为了做出有效决策，我们来按关键标准比较这些模式。

### 数据工作负载适用性

不同的开箱即用模式在处理事务型（运营）和分析型（历史或聚合）数据时，有效性各不相同。使用 Amazon Q Business 的模式 1 和模式 3 处理已索引的数据，针对的是对先前已索引内容进行查找式查询，而非实时事务型数据库查询。使用 AWS Quick Sight 的模式 2 针对事务型信息获取可视化输出，用于临时分析。使用 Amazon Bedrock 结构化数据检索的模式 4 专为分析系统和数据仓库设计，擅长对大型数据集执行复杂查询。模式 5 是一种自管理的 text-to-SQL 选项，可构建为同时支持用户的事务型或分析型需求。

### 目标受众

模式 1、2 和 3（使用 Amazon Q Business、AWS Quick Sight 或两者组合）中强调的架构最适合内部企业使用。不过，你可以使用 [AWS Quick Sight Embedded](https://aws.amazon.com/quicksight/embedded-analytics/) 将数据可视化、仪表板和自然语言查询嵌入内部应用或面向客户的应用。Amazon Q Business 作为面向组织知识的企业 AI 助手，采用基于订阅的定价层级，专为内部员工设计。模式 4（使用 Amazon Bedrock）既可用于构建内部应用，也可用于构建面向客户的应用。这是因为，与 Amazon Q Business 的订阅模式不同，Amazon Bedrock 提供 API 驱动的服务，可减轻外部客户场景下的按用户成本与身份管理开销。这使其非常适合需要服务潜在大批外部用户的面向客户体验。模式 5 中的自定义 LLM 解决方案同样可以针对外部应用需求进行定制。

### 接口与输出格式

不同模式通过不同的交互模型交付答案：

- **对话式体验** —— 模式 1 和 3（使用 Amazon Q Business）提供基于聊天的界面。模式 4（使用 Amazon Bedrock Knowledge Bases 进行结构化数据检索）天然支持 AI 助手集成，模式 5（自定义 text-to-SQL 解决方案）可针对多种交互模型进行设计。
- **以可视化为重点的输出** —— 模式 2（使用 AWS Quick Sight）擅长针对用户问题即时生成图表和表格等可视化。
- **API 集成** —— 若要把能力嵌入现有应用，模式 4 和 5 提供最灵活的基于 API 的集成选项。

下图是 AWS 结构化数据查询模式的对比矩阵。

![图示表格](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/03/Diagram-Table-modified-title-2.png)

## 结论

在这些模式之间，你的最佳选择取决于以下关键因素：

- **数据位置与特征** —— 你的数据是在运营数据库中、已经在数据仓库中，还是分散在多个来源？
- **用户画像与交互模型** —— 你服务的是内部用户还是外部用户？他们更偏好对话式界面还是以可视化为重点的界面？
- **可用资源与专业知识** —— 你是否有可用的 ML 专家，或者需要全托管解决方案？
- **准确性与治理要求** —— 你需要严格受控的语义与人工整理，还是可接受更宽的查询灵活性并配合监控？

通过理解这些模式及其权衡，你可以设计出与业务目标一致的架构。

### 关于作者

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/20/akshara2.png)**Akshara Shah** 是 Amazon Web Services 的高级解决方案架构师。她帮助商业客户构建基于云的生成式 AI 服务以满足其业务需求。十多年来，她一直在设计、开发和实施利用 AI 与 ML 技术的解决方案。工作之外，她喜欢绘画、锻炼，以及与家人共度时光。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/20/Sanghwa-Profilenew.png)Sanghwa Na** 是 Amazon Web Services 的生成式 AI 专家解决方案架构师。他常驻旧金山，与客户合作在 AWS 上使用大语言模型和 foundation model 设计和构建生成式 AI 解决方案。他专注于帮助组织采用能带来真实业务价值的 AI 技术
