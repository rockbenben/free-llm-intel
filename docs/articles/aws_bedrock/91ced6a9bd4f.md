---
vendor: aws_bedrock
title: 使用您的编码代理迁移到 Amazon Bedrock 托管知识库
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/migrate-to-amazon-bedrock-managed-knowledge-base-with-your-coding-agent
date: 2026-11-12
lang: zh
captured: 2026-11-13
extractor: readability-v1
translator: mt
status: translated
body_sha: 805946c63da4
---

## [人工智能](https://aws.amazon.com/blogs/machine-learning/)

# 使用您的编码代理迁移到 Amazon Bedrock 托管知识库

借助 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 上的客户管理知识库，您可以预置和扩展矢量存储、调整嵌入模型和索引设置，并规划每个新数据源的容量。 Agent Toolkit for AWS 中的迁移指南可帮助您迁移到 [Amazon Bedrock 托管知识库](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-build-management.html)。托管知识库接管这项工作并添加新的检索功能，您的团队可以控制内容和使用内容的应用程序。

移动生产知识库意味着您的团队在切换流量之前映射其配置、创建替换、提取内容、更新应用程序的检索调用并验证检索。为了提供帮助，我们在 [Agent Toolkit for AWS](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/skills.html) 中为“amazon-bedrock”技能添加了知识库迁移指南。该指南为您的编码代理提供了与您一起规划迁移的上下文，从只读发现和您逐行查看的计划开始。在您批准后，代理将在原始知识库及其数据源旁边创建新的知识库及其数据源，或者为您的管道编写迁移的基础设施即代码 (IaC) 模板。摄取和更新应用程序的“检索”调用始终由您负责，您的代理可以引导您完成这两个过程。

在这篇文章中，我们解释了为什么建议迁移以及迁移指南如何工作，查看先决条件，安装技能，计划迁移，更新应用程序的检索调用，以及在切换之前验证检索。

## 为什么迁移到托管知识库

我们推荐托管知识库，因为它平衡了易用性、检索准确性和成本。

### AWS 运营商店

借助托管知识库，Amazon Bedrock 可以处理摄取、存储、索引和检索，并且存储会随着内容的增长而自动扩展。混合搜索结合了关键字和语义匹配，始终处于开启状态，无需配置索引。该知识库包括托管嵌入模型、托管重排序器和用于多模式文件类型的内置解析器。

创建知识库时，您仍然可以使用自己的 Amazon Bedrock 嵌入模型。对于每个检索请求，您可以选择托管重排序器、Amazon Bedrock 重排序模型或不重排序。托管重排序器需要托管嵌入模型。

### 内置功能

托管知识库包括您自己构建的功能：

- **本机连接器** 直接从 Amazon Simple Storage Service (Amazon S3)、Microsoft SharePoint 和 Atlassian Confluence 等来源获取内容。有关当前列表，请参阅[支持的连接器](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-management-create.html#kb-management-connectors)。第一次完全同步后，以后的同步仅根据需要或按计划获取更改。托管知识库包括删除保护措施，有助于防止意外批量删除索引内容。
- [**访问控制列表 (ACL) 感知**](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-management-acl.html) 将文档权限与内容一起提取，因此检索仅返回登录用户可以访问的内容。对于支持它的连接器（例如 Microsoft SharePoint 和 Atlassian Confluence），对源的实时检查还会捕获自上次同步以来的权限更改。 ACL 感知不会对用户进行身份验证，因此您的应用程序必须验证并传递用户的身份。
- [**代理检索**](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-agentic-retrieve.html) 通过处理多部分问题和迭代检索来回答单个搜索无法回答的问题。它可以在一次请求中搜索多个知识库。
- [**与 AgentCore Gateway 集成**](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-gateway-target.html) 是 Amazon Bedrock AgentCore 的一项功能，可将您的知识库公开为目标。任何支持模型上下文协议（MCP）的客户端都可以查询知识库，并且网关处理身份验证。
- [**基于资源的策略**](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-management-cross-account.html) 让其他 AWS 账户中的应用程序使用一个团队的知识库。将每个策略的范围限定为调用知识库的特定角色，并仅授予他们使用的操作，例如“bedrock:Retrieve”。

代理检索、AgentCore Gateway 集成和基于资源的策略在客户管理的知识库上不可用。有关提供托管知识库的 AWS 区域以及 AWS GovCloud（美国西部）不支持的功能，请参阅[支持的 AWS 区域](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-management-regions.html)。

### 更高的配额

截至撰写本文时，较高的默认配额会改变您组织内容的方式。每个知识库有 200 个数据源，您可以将相关内容分组到一个知识库中。每个账户、每个区域有 10,000 个知识库，每个团队或产品线都可以使用单独的知识库。

| **默认配额** | **客户管理** | **管理** |
| --- | --- | --- |
|每个帐户、每个区域的知识库 | 100 | 100 10,000 |
|每个知识库的数据源 | 5 | 200 | 200
|每个知识库的并发摄取作业 | 1 | 50 | 50
|查询输入字符| 1,000 | 10,000 |

有关当前值，请参阅 [Amazon Bedrock 终端节点和配额](https://docs.aws.amazon.com/general/latest/gr/bedrock.html#limits_bedrock) 和 [托管知识库的服务配额](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-management-quotas.html)。

### 为您存储和检索的内容付费

成本是团队在考虑这一举措时权衡的三件事之一，另外还有可定制性和对矢量存储的直接控制。在[客户管理的知识库](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-build-management.html)上，您可以选择、配置、扩展和更新矢量和文本存储，并为您选择的基础设施单独付费。在托管知识库上，这些阶段是服务的一部分，并且存储和检索是直接计量的。

定价模型也可能有所不同。对于客户管理的知识库，存储和检索费用取决于您选择的矢量存储。有些商店按预配置容量或最低容量收费，而其他商店（例如 Amazon S3 Vectors（Amazon S3 的一项功能））仅按您使用的容量收费。托管知识库根据您存储和检索的内容定价，因此成本取决于实际使用情况。基于使用情况的定价可以适应以低利用率运行的企业问答、策略和支持知识库。有关当前费率，请参阅 [Amazon Bedrock 定价](https://aws.amazon.com/bedrock/pricing/)。有关客户管理的知识库上可用的解析器以及每个解析器的计费方式，请参阅[数据源的解析选项](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-advanced-parsing.html)。

| **成本驱动因素** | **客户管理的知识库** | **托管知识库** |
| --- | --- | --- |
| **矢量存储** |由您选择的商店单独定价。即使在低容量的情况下，预配置的检索服务也可以具有最低的闲置成本 |包含在每月每 GB 5 美元的基本存储费率中 |
| **多模态文档解析** |需要 Amazon Bedrock Data Automation（按页面或图像计费）或基础模型（按令牌计费）。纯文本解析是免费的。 |包含 |
| **嵌入生成** |按照您的嵌入模型的费率单独计费 |包含在默认型号中。仅当您选择定制型号时才需付费 |
| **摄取、同步和重新同步计算** |每次同步时的重新嵌入、编排代码和索引计算峰值都会增加经常性成本包含增量同步，仅处理新的和更改的内容 |
| **连接器** |构建和运行自定义连接器会增加计算成本 |包含本机连接器 |
| **标准检索** |每次查询 Amazon Bedrock 不收取费用。您的矢量存储可以按查询收费，就像 Amazon S3 Vectors 一样。 |每 1,000 个检索请求 1 美元 |
| **重新排名** | Amazon Rerank 按每 1,000 个查询 1 美元收费。自定义重新排名模型按自己的费率计费 |包含在每 1,000 个检索请求 1 美元中 |
| **代理检索** |您在 Bedrock 模型上构建代理工作流程，在开发和维护之前，每 1,000 个查询的成本约为 18 至 24 美元。由于模型使用量按令牌计费，因此每次查询的价格各不相同。 |除了基础检索调用（包括多重检索、重新排名和答案生成）之外，代理检索还需要每 1,000 个查询额外花费 4 美元。根据底层检索调用的数量，每 1,000 个查询的总费用大约为 6 美元到 9 美元。 |

费率只是总拥有成本的一部分。在客户管理的知识库上，您的团队将每个阶段作为单独的资源进行配置、扩展和操作。托管知识库将它们整合为一种资源，具有默认的嵌入模型、基础模型和重新排序器，并且默认情况下具有每个知识库的速率限制。您管理内容和使用内容的应用程序，Amazon Bedrock 运行托管存储、嵌入模型、基础模型和重新排序器。

## 解决方案概述

客户管理的知识库使用“VECTOR”类型，以及您配置的矢量存储。托管知识库使用“MANAGED”类型。迁移指南指示您的代理在原始知识库旁边创建一个新的“托管”知识库，而无需在迁移过程中修改或删除原始知识库。使用指南的地图，您的代理可以编写一个计划，列出哪些设置保持不变、哪些托管处理方式不同，以及您需要进行哪些应用程序更改。如图 1 所示，当您的团队提取内容、验证和切换时，原始版本会继续满足每个请求。

![编码代理在原始 VECTOR 知识库旁边创建托管知识库的流程图，该知识库一直为应用程序提供服务，直到团队验证检索和剪切结束。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/03/ML-22176-1.png)

图 1：与原始模板一起创建托管知识库或迁移模板，然后在切换前进行验证

## 迁移指南的工作原理

该指南将规划与实施分开。在探索模式下，您的代理会回答有关托管知识库的问题，并可以通过只读调用检查您的配置，以便您可以估计工作量。在迁移模式下，指南将引导您的代理通过检查点：

- **介绍并选择。** 您的代理人会解释它会接触什么和不会接触什么。选择模式、实时知识库或 IaC 源以及简单（默认）或技术解释风格。
- **识别。** 确认账户和 AWS 区域。您的代理会标记过于宽泛的凭据，询问您是否需要成本分析，并创建一个输出目录。
- **发现。** 您的代理通过只读调用读取知识库和数据源，或读取您的模板文件。
- **计划。** 查看计划和应用程序更改。默认情况下，您的代理在此停止。
- **根据要求实施。** 对于实时构建，批准配置脚本的精确预览，并在发生更改时再次批准。对于 IaC，您的代理会编写迁移的模板并报告运行的架构检查。
- **交接。** 查看已生成的内容以及团队的剩余步骤。

如图 2 所示，资源创建与摄取和切换是分开的。

![迁移检查点流程图，经过介绍、识别、发现和计划，然后直接移交或通过可选的批准实施，探索模式为只读，团队处理摄取、验证、切换和退休。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/03/ML-22176-2.png)

图 2：迁移检查点。实施是可选的，您的团队负责进行摄取和切换

### 查看配置映射

该指南映射每个设置，以在托管类型使用不同的配置时保留数据源、筛选器和分块行为。该计划对每个设置进行分类：

- **1:1.** 新知识库使用相同的设置。
- **已调整。** 托管对相同结果使用不同的设置，并且计划应用替代。
- **已阻止。** 今天没有托管路径。您的代理会从构建中排除该知识库，解释原因，并引导您访问 AWS Support。同一运行中的其他知识库可以继续。

验证时比较您自己的内容的分块。

### 查看权限和生成的更改

发现、规划和整个 IaC 路径只需要只读凭据。对于实时构建，该指南指示您的代理提出一个范围策略，明确拒绝对原始知识库的更改，并且永远不会请求管理员或完全访问权限。它还指示您的代理仅更改其创建的资源，通过 Amazon 资源名称 (ARN) 引用机密，并忽略在其读取的数据中找到的指令。在批准运行之前，请查看生成的 AWS Identity and Access Management (IAM) 策略和预配置脚本。构建后，检查代理在 [AWS CloudTrail 事件历史记录](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html) 中执行的操作，该历史记录保留 90 天的管理事件。每个事件都会记录 API 调用（例如“CreateKnowledgeBase”）以及进行该调用的身份。

对于可选的成本分析，您的代理将使用当前 AWS 价格将当前支出与托管知识库估算进行比较。它使用只读输入，包括 Amazon CloudWatch 指标、Amazon S3 对象大小和 AWS Cost Explorer。每个数字都标记为测量值、由您提供或估计值。

## 先决条件

使用单独的凭据进行规划和任何批准的资源创建。

- 与 Agent Toolkit for AWS 兼容的开发环境。
- AWS 命令​​行界面 (AWS CLI)，配置了最低权限的只读配置文件。
- 访问原始知识库配置或其 IaC 文件。
- 对于可选的实时构建：范围化的构建配置文件，使用指南建议的策略。新知识库的 IAM 服务角色。该指南为您的代理提供信任策略和权限来帮助您创建它。 Python 3 和 boto3 用于生成的配置脚本。

Agent Toolkit for AWS 可与兼容的开发环境配合使用，其 [GitHub 上的存储库](https://github.com/aws/agent-toolkit-for-aws) 列出了可用的技能。本文中的示例使用 AWS CLI 2.37 和 boto3 1.43.32。

## 安装技能

请按照您的编码代理的 [Agent Toolkit for AWS 入门说明](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/quick-start.html) 操作。 “add-skill”命令将“amazon-bedrock”技能安装到它检测到的编码代理。将 `--agent` 添加到目标之一，例如 `--agent kiro`。
```
aws agent-toolkit add-skill \
    --skill-name amazon-bedrock
```
安装后，您的代理会在您描述迁移任务时加载迁移指南。以下提示是说明性输入，而不是文字记录。

## 规划迁移

选择与您维护源的方式相匹配的路径。

| **路径** | **您的代理人阅读的内容** | **它生产什么** | **AWS 变化** |
| --- | --- | --- | --- |
|探索 |文档，以及可选的知识库（只读）|对话中的答案 |无 |
|实时知识库 |您的知识库和数据源（只读）|一个计划，以及可选的新的托管知识库以及原始的 |仅在您批准确切的预览之后 |
|基础设施即代码 |您的 AWS CloudFormation 模板、AWS 云开发工具包 (AWS CDK) 合成模板或 Terraform 配置 |相同格式的迁移模板 |没有任何。您的管道部署它 |

要以探索模式开始，请提出一个问题：
```
What would change if I moved knowledge base <your-kb-name>
in <your-region> to a Managed Knowledge Base? Use Explore mode.
```
准备好后，选择实时或 IaC 路径。

### 迁移实时知识库

在授权资源创建之前询问计划：
```
Plan a migration of knowledge base <your-kb-name> in <your-region>
to a Managed Knowledge Base. Stop after the plan.
```
确认帐户和区域，然后查看计划的映射和应用程序更改。默认情况下，新知识库采用原始名称并带有“-management”后缀。要构建它，请确认服务角色存在，切换到构建配置文件，检查配置脚本及其预览，然后批准。您的代理运行脚本，该脚本创建知识库和数据源，并报告它们的状态。

### 将基础设施迁移为代码

将您的代理指向源模板或配置：
```
Review <path-to-source-template> and plan a migration to a
Managed Knowledge Base.
```
您的代理将迁移的文件写入输出目录，不部署任何内容，并向您显示差异。要保留差异，请要求您的代理保存它。在部署之前运行 `terraform init -backend=false` 和 `terraform validate`。您的代理可以引导您完成这两个命令，但指南将这些检查留给您，因为“terraform init”会下载大型 AWS 提供商。在应用部署计划之前，请检查它是否保留了回滚所需的原始资源。

### 对话示例

迁移作为对话运行。在阅读任何内容之前，您的代理人会说明其范围并询问如何继续：
```
It never changes or deletes <your-kb-id>, never starts ingestion,
and never cuts your application over; every AWS change is shown to
you and approved first. Nothing has run against your KB yet.

1. Mode: Explore (read-only Q&A about Managed KBs and your KB, no
   plan or build) or Migration (run the phases: identify, discover,
   plan, and optionally build)?
2. Target type, if Migration: migrate the live KB <your-kb-id> (kb
   path, which can build a new Managed KB on approval), or migrate
   the Terraform/CloudFormation that defines it (iac path, which
   only emits a migrated file and provisions nothing)?
3. Explanation style: plain or technical. I'll use plain unless
   you say otherwise.
```
计划摘要显示每个映射、调用者更改以及您需要做出的决策：
```
Phase 3, Plan: written (plan.md)
- Mapping:
  - Vector store becomes auto-provisioned (adjusted, Yes).
  - SEMANTIC chunking is dropped for the managed default
    (adjusted, Partly).
  - Parsing becomes SMART_PARSING (adjusted, Yes).
  - The S3 prefix and metadata sidecars carry over 1:1.
- Changes for callers:
  - New KB id.
  - managedSearchConfiguration replaces vectorSearchConfiguration.
  - overrideSearchType: SEMANTIC can't be sent; search is hybrid.
Your input needed before this can go further.
- D1 embeddingModelType: MANAGED (recommended): keeps the managed
  reranker. CUSTOM Titan v2 1024/FLOAT32: turns off the managed
  reranker.
- D2 aclEnabled: recommend false, since the source has no ACLs.
  On S3 this can't be changed after create.
- Next step: stop with this plan (the default), or opt into Phase 4?
```
对于实时构建，您的代理会在预览时停止，并且批准命令需要计划的哈希值：
```
If you approve, the command to run is the following. It is MUTATING:
  AWS_PROFILE=build-profile AWS_REGION=<your-region> \
    python3 provision_managed_kb.py --execute \
    --expect-plan-sha256 <plan-sha256>
--execute refuses to start unless it is given --expect-plan-sha256
and the hash matches.
What the preview would create:
- Knowledge base (CreateKnowledgeBase, MANAGED): support-docs-managed
- Data source (CreateDataSource, managed connector, deletion
  protection ENABLED/15): support-docs-s3-managed
The script never calls StartIngestionJob, Retrieve, Update*,
Delete*, or a standalone TagResource.
```
*示例交换经过轻微编辑，并替换了标识符。*

## 更新应用程序的检索调用

您的应用程序对这两种类型使用相同的“检索”操作。托管请求以新的知识库 ID 为目标，并将“vectorSearchConfiguration”替换为“drivenSearchConfiguration”。将“vectorSearchConfiguration”传递到托管知识库会返回验证错误。托管检索始终使用混合搜索，因此托管请求形状没有“overrideSearchType”字段。元数据过滤器保持相同的语法，只是托管知识库不支持“startsWith”和“stringContains”运算符。有关完整语法，请参阅[检索 API 参考](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_Retrieve.html)。

该示例假设两个知识库都包含过滤器使用的“区域设置”元数据。
```
# Illustrative: the managed request shape was checked with boto3 1.43.32; adapt the IDs and filter to your knowledge base.
import boto3

client = boto3.client("bedrock-agent-runtime")
query = {"text": "How do I return an online order?"}
locale_filter = {"equals": {"key": "locale", "value": "en-US"}}

# Customer-managed (VECTOR) knowledge base.
original_response = client.retrieve(
    knowledgeBaseId="<original-kb-id>",
    retrievalQuery=query,
    retrievalConfiguration={
        "vectorSearchConfiguration": {
            "numberOfResults": 5,
            "overrideSearchType": "SEMANTIC",
            "filter": locale_filter,
        }
    },
)

# Managed target: different ID and search configuration.
managed_response = client.retrieve(
    knowledgeBaseId="<managed-kb-id>",
    retrievalQuery=query,
    retrievalConfiguration={
        "managedSearchConfiguration": {
            "numberOfResults": 5,
            "filter": locale_filter,
        }
    },
)
```
## 验证检索并切换

在应用程序仍使用原始知识库的同时评估新知识库。

- 如果使用 IaC，请通过管道检查并部署目标配置。
- 同步每个数据源并检查任何失败。请参阅[同步您的数据](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-data-source-sync-ingest.html)。
- 在新知识库 ARN 上授予应用程序的运行时 IAM 角色“bedrock:Retrieve”，并保留其对原始知识库的访问权限，以便您可以回滚。
- 使用该角色通过“Retrieve”对两个知识库运行代表性查询。这两种类型使用不同的评分标准。托管分数还取决于“rerankingModelType”，托管嵌入模型默认为“MANAGED”，自定义模型默认为“NONE”。调整每个模式的阈值，并在比较时保持模式恒定。
- 测试使用的元数据过滤器和权限感知检索，包括登录用户不应接收的内容。在启用 ACL 的数据源上，没有“userContext.userId”（用户的电子邮件）的请求不会返回任何结果。
- 接受后，部署新的知识库 ID 和请求形状。在回滚期内保留原始知识库、当前内容和应用程序配置。

对于每个查询，检查两者是否返回相同的顶级文档以及结果重叠的程度。简短的脚本可以根据标准报告通过或失败，例如至少 90% 的查询匹配顶级文档，并且托管知识库上没有零结果查询。根据您的工作负载调整该阈值。有关其他检索质量衡量标准，例如上下文相关性和上下文覆盖率，请参阅[使用指标了解 RAG 系统性能](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-eval-retrieve.html)。

比较结果时请注意这些差异：

- **比较之前标准化源位置。** 客户管理的知识库可以在“location.s3Location.uri”中返回“s3://bucket/key”，托管知识库可以返回“https://”URL。按对象键进行比较。
- **比较顶部结果而不是假设结果计数相等。** 两种知识库类型可以返回不同数量的结果，并且“numberOfResults”设置最大值而不是保证。比较顶部文档，并查看每个查询中发生更改的地方。有关详细信息，请参阅[配置和自定义托管知识库的查询](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-management-test-config.html)。
- **映射重命名的系统元数据键。** 例如，将比较代码中的“x-amz-bedrock-kb-data-source-id”替换为“_data_source_id”。您自己的元数据属性保留其名称。有关详细信息，请参阅[配置和自定义托管知识库的查询](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-management-test-config.html)。

## 清理

如果完成迁移，则仅在回滚期和依赖性审查之后停用原始版本。保留托管知识库从中提取的源文档和存储桶，以及其他工作负载使用的存储。通过其拥有的模板清理 IaC 管理的资源。

如果您结束评估，请保留原始内容并按以下顺序删除您创建的内容：

- 删除每个托管数据源并等待它消失。
- 删除托管知识库并等待它消失。
- 如果您仅为本次评估创建了服务角色，请删除其内联策略，然后删除该角色。
- 使用客户管理的密钥，检查“aws kms list-grants”以获取 Amazon Bedrock 创建的授权，这些授权在删除知识库后可以保留。
- 保留另一个知识库仍在读取的任何 S3 存储桶。

托管数据源上的删除保护限制同步可以删除的数据量，而不是限制您是否可以删除数据源。删除原始知识库并不会删除其矢量存储，在您将其删除之前，矢量存储会继续产生费用。请参阅[删除 Amazon Bedrock 知识库](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-delete.html)。

## 结论

借助 Amazon Bedrock 托管知识库，您的团队不再运行矢量存储或管理底层检索基础设施。通过“亚马逊基础”技能中的迁移指南，您可以向您的代理询问计划，对其进行审查，然后仅批准您想要构建的资源。

首先，设置 [Agent Toolkit for AWS](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/quick-start.html) 并要求您的代理对您的知识库进行只读评估。迁移后，探索[代理检索](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-agentic-retrieve.html)以获取多部分问题。要了解更多信息，请参阅 AWS 机器学习博客上的[使用 Amazon Bedrock 托管知识库构建代理的企业搜索](https://aws.amazon.com/blogs/machine-learning/build-enterprise-search-for-agents-with-amazon-bedrock-management-knowledge-base/)。

## 关于作者
