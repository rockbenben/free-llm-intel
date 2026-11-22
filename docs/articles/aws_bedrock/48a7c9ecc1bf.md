---
vendor: aws_bedrock
title: Multi-tenant RAG implementation with Amazon Bedrock and Amazon OpenSearch Service for SaaS using JWT
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/multi-tenant-rag-implementation-with-amazon-bedrock-and-amazon-opensearch-service-for-saas-using-jwt
date: 2025-07-23
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 3ed4e68743dd
---

# 面向 SaaS 的、使用 JWT 与 Amazon Bedrock 和 Amazon OpenSearch Service 的多租户 RAG 实现

近年来，大语言模型（LLM）的出现加速了 AI 在各行各业的采用。然而，要进一步增强 LLM 的能力并有效利用最新信息和领域特定知识，与外部数据源的集成不可或缺。检索增强生成（RAG）作为一种应对这一挑战的有效方法，已获得广泛关注。

RAG 是一种根据用户输入从现有知识库或文档中搜索相关信息，并将这些信息纳入 LLM 输入以生成更准确、更贴合语境的响应的技术。该技术正被广泛应用于各类场景，从在产品开发中使用技术文档，到在客户支持中回答 FAQ，甚至支持基于最新数据的决策系统。

RAG 的实现为软件即服务（SaaS）提供商及其用户（租户）都带来了显著价值。

SaaS 提供商可以使用多租户架构，从单一代码库向多个租户提供服务。随着租户使用服务，其数据不断累积，同时受到适当的访问控制和数据隔离的保护。在此类环境中使用 LLM 实现 AI 能力时，RAG 使得利用每个租户的特定数据提供个性化 AI 服务成为可能。

以客户服务呼叫中心 SaaS 为例。每个租户的历史咨询记录、FAQ 和产品手册都会累积为租户特定的知识库。通过实施 RAG 系统，LLM 可以参考这些租户特定的数据源，生成与每个租户语境相关的恰当响应。这实现了融入租户特定业务知识的高准确度交互——这是通用 AI 助手无法达到的定制水平。RAG 是在 SaaS 中交付个性化 AI 体验的关键组件，有助于实现服务差异化和价值提升。

然而，通过 RAG 使用租户特定数据在安全和隐私方面带来了技术挑战。首要关注点是实施安全架构，以维持租户之间的数据隔离，并帮助防止意外的数据泄漏或跨租户访问。在多租户环境中，数据安全的实施会直接影响 SaaS 提供商的可信度和竞争优势。

[Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/) 使 RAG 的实现更为简便。使用 OpenSearch 作为向量数据库时，有两种选择：[Amazon OpenSearch Service](https://aws.amazon.com/opensearch-service/) 或 [Amazon OpenSearch Serverless](https://aws.amazon.com/opensearch-service/features/serverless/)。在构建多租户环境时，每种选择都有不同的特性和权限模型：

- Amazon OpenSearch Serverless：[元数据过滤](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-knowledge-bases-now-supports-metadata-filtering-to-improve-retrieval-accuracy/) 支持按租户从向量数据库筛选搜索结果（更多细节，请参阅 [Multi-tenant RAG with Amazon Bedrock Knowledge Bases](https://aws.amazon.com/blogs/machine-learning/multi-tenant-rag-with-amazon-bedrock-knowledge-bases/)）。其权限模型不会对数据创建和更新等写操作的权限进行隔离。
- Amazon OpenSearch Service：可使用[细粒度访问控制](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/fgac.html)（FGAC）。访问通过附加到知识库的单个 [AWS Identity and Access Management](https://aws.amazon.com/iam/)（IAM）角色进行，这有助于防止使用 FGAC 进行权限隔离。

本文将介绍结合使用 JSON Web Token（JWT）与 FGAC 的租户隔离模式，以及租户资源路由。如果上述权限模型限制了您实现 FGAC 目标，您可以使用本文中的解决方案。该解决方案使用 OpenSearch Service 作为向量数据库，并使用 [AWS Lambda](https://aws.amazon.com/lambda) 作为编排层。

在下一节中，我们将探讨在 OpenSearch Service 中使用 JWT 和 FGAC 实现租户隔离的具体做法，以及这如何构建安全的多租户 RAG 环境。

## JWT 在 OpenSearch Service 多租户数据隔离中的有效性

正如 [Storing Multi-Tenant SaaS Data with Amazon OpenSearch Service](https://aws.amazon.com/blogs/apn/storing-multi-tenant-saas-data-with-amazon-opensearch-service/) 中所介绍的，OpenSearch Service 提供多种管理多租户数据的方法：域级隔离、索引级隔离和文档级隔离。

要在索引和文档级别实现访问权限隔离，您可以使用由 OpenSearch Security 插件支持的 FGAC。

在 OpenSearch Service 中，您可以通过将 IAM 身份映射到 OpenSearch 角色来实现细粒度访问控制。这可以在 OpenSearch 中为每个 IAM 身份设置详细的权限。然而，这种方法带来了显著的可扩展性挑战。随着租户数量增加，所需的 IAM 用户或角色数量也会增加，可能触及 AWS 服务配额上限。此外，管理大量 IAM 实体会带来运维复杂性。尽管[动态生成的 IAM 策略](https://aws.amazon.com/blogs/apn/isolating-saas-tenants-with-dynamically-generated-iam-policies/)可以克服这一挑战，但每个动态生成的策略都附加到单个 IAM 角色。单个 IAM 角色可以映射到单个 OpenSearch 角色，但这仍然需要为每个租户提供一个 IAM 角色和动态策略以实现适当隔离，结果在管理大量实体方面带来类似的运维复杂性。

本文提供另一种方法，聚焦于 JWT 的有效性——JWT 是一种自包含 token，用于在多租户环境中实现数据隔离和访问控制。使用 JWT 带来以下优势：

- **动态租户识别** – JWT 载荷可以包含属性信息（租户上下文）以识别租户。这使系统能够为每个请求动态识别租户，并允许将该上下文传递给后续资源和服务。
- **与 OpenSearch 中 FGAC 的集成** – FGAC 可以直接使用 JWT 中的属性信息进行角色映射。这允许根据 JWT 中的租户 ID 等信息，将访问权限映射到特定索引或文档。

将 JWT 与 FGAC 结合，可在使用 OpenSearch Service 的多租户 RAG 环境中提供安全、灵活且可扩展的数据隔离和访问控制。在下一节中，我们将探讨在实际系统中应用这一概念的具体实现细节和技术考量。

## 解决方案概览

在 RAG 中，用于增强 LLM 输出的相关文档等数据会通过嵌入语言模型进行向量化，并索引到向量数据库中。用户的自然语言问题使用嵌入模型转换为向量，并在向量数据库中搜索。通过向量搜索检索到的数据作为上下文传递给 LLM，以增强输出。下图展示了该解决方案的架构。

[![架构图](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/07/ML-17909-1-architecture.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/07/ML-17909-1-architecture.png)

该解决方案使用 OpenSearch Service 作为向量数据存储，用于在 RAG 中存储知识来源。流程如下：

- 每个租户的 RAG 应用用户被创建为 [Amazon Cognito](https://aws.amazon.com/cognito/) [user pool](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools.html) 中的用户，登录前端时会收到一个加入了租户 ID 信息增强的 JWT。每个用户的租户信息存储在 [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) 中，并在用户认证期间由 [pre-token generation Lambda trigger](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-pre-token-generation.html) 添加到 JWT 中。
- 当用户在前端发起聊天时，用户查询会连同 JWT 一起通过 [Amazon API Gateway](https://aws.amazon.com/api-gateway/) 传递给 Lambda。
- 用户查询结合 Amazon Bedrock 中提供的文本嵌入模型进行向量化。
- 从 DynamoDB 获取用于检索的域和索引信息。
- 在 OpenSearch Service 上执行向量搜索，从索引中检索与查询相关的信息。
- 将检索到的信息作为上下文加入 prompt，并传递给 Amazon Bedrock 中可用的 LLM 以生成响应。

该解决方案的关键在于使用 JWT 在 OpenSearch Service 中实现租户数据隔离，并路由到每个租户的数据。它使用 OpenSearch Service 中提供的 FGAC 为每个数据集分离访问权限，并利用添加到 JWT 中的租户 ID 信息将应用用户映射到分离的权限集。该解决方案提供三种不同的数据隔离粒度模式以满足客户需求。通过定义 JWT 中的租户 ID 信息与 DynamoDB 中数据位置（域、索引）之间的映射，路由也得以实现。

当用户添加文档时，文件被上传到 [Amazon Simple Storage Service](https://aws.amazon.com/s3/)（Amazon S3），元数据写入 DynamoDB 管理表。在 OpenSearch Service 中存储数据时，由摄取 pipeline 调用文本嵌入模型（Amazon Bedrock）进行向量化。对于文档创建、更新和删除，请求会附带 JWT，从而实现租户识别。

该解决方案使用 [AWS Cloud Development Kit](https://aws.amazon.com/cdk/)（AWS CDK）实现。详细信息请参阅 [GitHub repository](https://github.com/aws-samples/sample-multi-tenant-saas-rag-using-bedrock-and-amazon-opensearch-service-with-jwt)。部署该解决方案的说明包含在仓库的 README 文件中。

## 先决条件

要试用该解决方案，您必须满足以下先决条件：

- 一个 AWS 账户。
- 运行 AWS CDK 所需的 IAM 访问权限。
- 前端执行环境：需要安装 node.js 和 npm。
- 必须配置 AWS CDK。详情请参阅 [Tutorial: Create your first AWS CDK app](https://docs.aws.amazon.com/cdk/v2/guide/hello-world.html)。
- 必须配置对 Amazon Bedrock 中所用模型的访问权限。该解决方案使用 Anthropic 的 Claude 3.5 Sonnet v2 和 Amazon Titan Text Embedding V2。详情请参阅 [Add or remove access to Amazon Bedrock foundation models](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access-modify.html)。

除架构图中展示的资源外，通过 AWS CDK 部署还会创建以下资源和配置，作为 [AWS CloudFormation](https://aws.amazon.com/cloudformation) 自定义资源：

- Amazon Cognito user pool：tenant-a、tenant-b、tenant-c 和 tenant-d 的用户
- DynamoDB 表：用户与租户之间的映射；租户与 OpenSearch 连接目标及索引之间的映射
- OpenSearch Service 域：JWT 认证设置；用于向量嵌入的摄取 pipeline；每个租户的 FGAC 角色和角色映射；k-NN 索引

## 使用 Amazon Cognito 进行用户认证和 JWT 生成

该解决方案使用 Amazon Cognito user pool 进行 RAG 应用用户认证。Amazon Cognito user pool 在认证期间签发 JWT。由于 OpenSearch Service 中的 FGAC 支持 JWT 认证，通过将 user pool 颁发的公钥注册到 OpenSearch Service 域，即可允许经 Amazon Cognito user pool 认证的用户访问。此外，还可以使用可添加到 JWT 载荷中的属性进行授权，以通过 FGAC 实现租户数据访问权限隔离，我们将在后续章节讨论这一点。为此，在 Amazon Cognito user pool 中配置了 pre-token generation Lambda trigger，用于检索 DynamoDB 中存储的每个用户的租户 ID 信息并将其添加到 token 中。获得的 JWT 由前端保留，并用于向后端发起请求。DynamoDB 按如下方式存储用户 ID（sub）与租户 ID 之间的映射：

```
{
  "pk": {
    "S": "membership#<Cognito user ID (sub)>"
  },
  "sk": {
    "S": "tenant#tenant-a"
  }
}
```

尽管使用 Amazon Cognito 实现多租户认证存在多种模式，但本实现使用单个 user pool，并在 DynamoDB 中保存用户与租户的映射。生产环境还需要额外的考量；请参阅 [Multi-tenant application best practices](https://docs.aws.amazon.com/cognito/latest/developerguide/multi-tenant-application-best-practices.html)。

## 使用 JWT 将请求路由到租户数据

在资源按租户分离的多租户架构中，将来自租户的请求路由到适当的资源至关重要。要了解有关租户路由策略的更多信息，请参阅 [Tenant routing strategies for SaaS applications on AWS](https://aws.amazon.com/jp/blogs/networking-and-content-delivery/tenant-routing-strategies-for-saas-applications-on-aws/)。本解决方案采用与该文章所述的数据驱动路由类似的方法来路由到 OpenSearch Service。

DynamoDB 表按如下方式存储租户 ID、目标 OpenSearch Service 域和索引的映射信息：

```
{
  "pk": {
    "S": "tenant#tenant-a"
  },
  "sk": {
    "S": "os_config"
  },
  "os_host": {
    "S": "<Amazon OpenSearch Service domain endpoint>"
  },
  "os_index": {
    "S": "tenant-a-index"
  },
  "rag_role": {
    "S": "tenant-a_role"
  }
}
```

JWT 从前端通过 API Gateway 发送到 Lambda 函数的 HTTP 请求的 Authorization 头中获取。通过解析 JWT 获得租户 ID，并使用该 ID 检索路由信息以确定路由目标。此外，如下一节所述，JWT 还用作向 OpenSearch 发出请求时的认证信息。

## OpenSearch Service 中数据位置和访问权限的多租户隔离

OpenSearch Service 中的多租户数据隔离策略包括三种隔离模式：域级、索引级和文档级隔离，以及它们的混合模型。本解决方案使用 FGAC 控制对租户数据的访问权限，为每个租户创建专用角色。

租户用户与 FGAC 租户角色之间的映射通过 backend roles 实现。在 OpenSearch Service 中提供的 [JWT 认证](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/JSON-Web-tokens.html) 中，可以指定 JWT 载荷中要与 backend roles 关联的属性作为 **Roles key**。以下截图展示了该域配置。

[![AOS 中的 JWT 配置](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/07/ML-17909-2-JWT-config-in-aos.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/07/ML-17909-2-JWT-config-in-aos.png)

JWT 载荷包含一个 `tenant_id` 属性，如下所示：`"tenant_id": "tenant-a"` 通过在 OpenSearch JWT 认证中将该属性设置为 roles key，并按如下方式映射角色，即可将租户用户与 FGAC 角色关联起来：

```
{
  "tenant-a_role": {
    "backend_roles": [
      "tenant-a"
    ]
  }
}
```

以下截图展示了 OpenSearch Dashboards 中 FGAC 租户角色映射的示例。

[![角色映射](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/07/ML-17909-3-role-mapping.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/07/ML-17909-3-role-mapping.png)

本解决方案的示例提供四个租户——tenant-a、tenant-b、tenant-c 和 tenant-d——以便您尝试全部三种隔离方法。下图展示了该架构。

[![三种隔离方法示意图](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/07/ML-17909-4-isolaton-map.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/07/ML-17909-4-isolaton-map.png)

每个角色都被授予仅访问相应租户数据的权限。在本节中，我们将介绍如何使用 JWT 和 FGAC 实现这三种隔离方法：

- **域级隔离** – 为每个租户分配独立的 OpenSearch Service 域。在这种隔离模式中，域是每个租户专用的，因此无需在域内做数据隔离。因此，FGAC 角色授予跨索引的访问权限。以下代码是 FGAC 角色定义中授予索引访问权限的 `index_permissions` 的一部分：

```
"index_permissions": [
    {
    "index_patterns": [
        "*"
    ],
```

- **索引级隔离** – 多个租户共享一个 OpenSearch Service 域，每个租户被分配单独的索引。每个租户应只能访问自己的索引，因此 FGAC 角色中的 `index_permissions` 配置如下（以 tenant-b 为例）：

```
"index_permissions": [
    {
    "index_patterns": [
        "tenant-b-index*"
    ]
```

- **文档级隔离** – 多个租户共享 OpenSearch Service 域和索引，使用 FGAC 的文档级安全对索引内租户数据的访问权限进行隔离。每个索引都包含一个用于存储租户 ID 信息的字段，并为该字段设置文档级安全查询。以下代码是 FGAC 角色中 `index_permissions` 的一部分，该角色允许 tenant-c 在 tenant-c 与 tenant-d 共享索引的配置中只访问自己的数据：

```
"index_permissions": [
    {
    "index_patterns": [
        "tenant-cd-shared-index*"
    ],
    "dls": """{"bool": {"must": {"match": {"tenant_id": "tenant-c"}}}}""",
```

以下截图展示了 FGAC 角色中文档级隔离的索引权限示例。

[![FGAC 角色权限设置](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/07/ML-17909-5-fgac-role-setting.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/07/ML-17909-5-fgac-role-setting.png)

## 注意事项

本文的实现采用 DynamoDB 表和 S3 存储桶在租户之间共享的模型。用于生产时，请考虑 [Partitioning Pooled Multi-Tenant SaaS Data with Amazon DynamoDB](https://aws.amazon.com/blogs/apn/partitioning-pooled-multi-tenant-saas-data-with-amazon-dynamodb/) 和 [Partitioning and Isolating Multi-Tenant SaaS Data with Amazon S3](https://aws.amazon.com/jp/blogs/apn/partitioning-and-isolating-multi-tenant-saas-data-with-amazon-s3/) 中介绍的分区模型，并根据您的需求确定最优模型。

此外，您可以使用[动态生成 IAM 策略](https://aws.amazon.com/blogs/apn/isolating-saas-tenants-with-dynamically-generated-iam-policies/)作为额外的一层，限制对每个资源的访问权限。

## 清理

为避免产生意外费用，我们建议在不再需要时删除资源。由于资源是使用 AWS CDK 创建的，请运行 `cdk destroy` 命令将其删除。此操作还会删除上传到 Amazon S3 的文档。

## 结论

本文介绍了一个在多租户 RAG 中使用 OpenSearch Service 作为向量数据存储的解决方案，利用 JWT 和 FGAC 实现数据隔离与路由。

该解决方案结合使用 JWT 和 FGAC 来实现严格的租户数据访问隔离与路由，这必须使用 OpenSearch Service。RAG 应用是独立实现的，因为在撰写本文时，Amazon Bedrock Knowledge Bases 无法使用基于 JWT 的方式访问 OpenSearch Service。多租户 RAG 的使用对 SaaS 公司很重要，而策略会因数据隔离严格程度、管理易用性和成本等需求而异。该解决方案实现了多种隔离模型，因此您可以根据自身需求进行选择。有关多租户 RAG 实现的其他解决方案和信息，请参阅以下资源：

- [Multi-tenant RAG with Amazon Bedrock Knowledge Bases](https://aws.amazon.com/jp/blogs/machine-learning/multi-tenant-rag-with-amazon-bedrock-knowledge-bases/)
- [Build a multi-tenant generative AI environment for your enterprise on AWS](https://aws.amazon.com/blogs/machine-learning/build-a-multi-tenant-generative-ai-environment-for-your-enterprise-on-aws/)
- [Self-managed multi-tenant vector search with Amazon Aurora PostgreSQL](https://aws.amazon.com/jp/blogs/database/self-managed-multi-tenant-vector-search-with-amazon-aurora-postgresql/)
- [Multi-tenant vector search with Amazon Aurora PostgreSQL and Amazon Bedrock Knowledge Bases](https://aws.amazon.com/jp/blogs/database/multi-tenant-vector-search-with-amazon-aurora-postgresql-and-amazon-bedrock-knowledge-bases/)

### 关于作者

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/07/ML-17909-6-naakazu-bio.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/07/ML-17909-6-naakazu-bio.png)**Kazuki Nagasawa** 是 Amazon Web Services 的云支持工程师。他专精于 Amazon OpenSearch Service，专注于解决客户的技术挑战。业余时间，他喜欢探索各类威士忌并发现新的拉面店。

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/07/ML-17909-7-kensukfu-bio-1.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/07/ML-17909-7-kensukfu-bio-1.png)**Kensuke Fukumoto** 是 Amazon Web Services 的资深解决方案架构师。他热衷于帮助 ISV 和 SaaS 提供商实现应用现代化并转型为 SaaS 模式。业余时间，他喜欢骑摩托车和泡桑拿。
