---
vendor: aws_bedrock
title: 借助 coding agent 迁移到 Amazon Bedrock 托管知识库
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/migrate-to-amazon-bedrock-managed-knowledge-base-with-your-coding-agent
date: 2026-11-12
lang: zh
captured: 2026-11-14
extractor: readability-v1
translator: agent
status: translated
body_sha: 520ed51d9dc2
---

## [人工智能](https://aws.amazon.com/blogs/machine-learning/)

# 借助 coding agent 迁移到 Amazon Bedrock 托管知识库

在 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 上使用客户管理的知识库时，你要自行预置和扩展向量存储、调优嵌入模型和索引设置，并为每个新数据源规划容量。Agent Toolkit for AWS 中的迁移指南可帮你迁移到 [Amazon Bedrock 托管知识库](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-build-managed.html)。托管知识库接管了这些工作，还增加了新的检索能力，而内容以及使用内容的应用程序仍由你的团队掌控。

迁移生产知识库意味着团队要先梳理现有配置、创建替代库、导入内容、更新应用程序的检索调用，并在切换流量前验证检索效果。为此，我们在 [Agent Toolkit for AWS](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/skills.html) 的 `amazon-bedrock` skill 里加入了一份知识库迁移指南。这份指南为你的 coding agent 提供上下文，让它和你一起规划迁移：从只读探查开始，给出一份你可以逐行审阅的计划。获得你批准后，agent 会在原有知识库旁创建新的知识库及其数据源，或为你的流水线写出迁移后的基础设施即代码 (IaC) 模板。导入内容和更新应用程序的 `Retrieve` 调用仍由你负责，agent 可以带你逐步完成这两件事。

本文将介绍我们为何建议迁移、迁移指南如何运作，并依次梳理前置条件、安装 skill、规划迁移、更新应用程序的检索调用，以及切换前的检索验证。

## 为什么迁移到托管知识库

我们推荐托管知识库，因为它在易用性、检索准确性和成本之间取得了平衡。

### AWS 负责运行存储

使用托管知识库后，Amazon Bedrock 会处理导入、存储、索引和检索，存储也会随内容增长自动扩展。混合搜索结合了关键词匹配与语义匹配，始终开启，无需配置索引。知识库内置托管嵌入模型、托管重排序器，以及面向多模态文件类型的解析器。

创建知识库时，你仍可自带 Amazon Bedrock 嵌入模型。每次检索请求都可以选择托管重排序器、某个 Amazon Bedrock 重排序模型，或者不重排序。托管重排序器要求使用托管嵌入模型。

### 内置能力

托管知识库内置了以下能力，否则你得自己实现：

- **原生 connector** 直接从 Amazon Simple Storage Service (Amazon S3)、Microsoft SharePoint、Atlassian Confluence 等来源导入内容。最新列表见[支持的 connector](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-create.html#kb-managed-connectors)。首次全量同步之后，后续同步只拉取变更，可按需触发或按计划执行。托管知识库还带有删除防护，帮助避免误删大量已索引内容。
- [**访问控制列表 (ACL) 感知**](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-acl.html) 会随内容一同导入文档权限，因此检索只返回已登录用户有权访问的内容。对于支持该能力的 connector（如 Microsoft SharePoint 和 Atlassian Confluence），还会对来源做实时检查，捕获自上次同步以来的权限变更。ACL 感知不负责用户身份认证，因此你的应用程序必须自行验证并传入用户身份。
- [**agentic 检索**](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-agentic-retrieve.html) 通过处理多部分问题、反复迭代检索，回答单次搜索无法解决的问题。它可以在一次请求中搜索多个知识库。
- [**与 AgentCore Gateway 集成**](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-gateway-target.html) 是 Amazon Bedrock AgentCore 的一项能力，可把你的知识库公开为一个 target。任何支持 Model Context Protocol (MCP) 的客户端都能查询该知识库，身份认证由网关处理。
- [**基于资源的策略**](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-cross-account.html) 让其他 AWS 账户中的应用程序也能使用某个团队的知识库。把每条策略限定到调用该知识库的具体角色，只授予它们实际用到的操作，例如 `bedrock:Retrieve`。

agentic 检索、AgentCore Gateway 集成和基于资源的策略在客户管理的知识库上不可用。关于提供托管知识库的 AWS 区域，以及 AWS GovCloud (US-West) 不支持的功能，参见[支持的 AWS 区域](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-regions.html)。

### 更高的配额

截至本文撰写时，更高的默认配额改变了你组织内容的方式。每个知识库可有 200 个数据源，你可以把相关内容归到同一个知识库里。每个账户、每个区域可有 10,000 个知识库，每个团队或产品线都能用独立的知识库。

| **默认配额** | **客户管理** | **托管** |
| --- | --- | --- |
| 每个账户、每个区域的知识库数 | 100 | 10,000 |
| 每个知识库的数据源数 | 5 | 200 |
| 每个知识库的并发导入作业数 | 1 | 50 |
| 查询输入字符数 | 1,000 | 10,000 |

最新数值参见 [Amazon Bedrock endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/bedrock.html#limits_bedrock) 和 [Service quotas for managed knowledge bases](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-quotas.html)。

### 按存储和检索的内容付费

团队在考虑这次迁移时要权衡三点，成本是其中之一，另外两点是可定制性和对向量存储的直接掌控。在[客户管理的知识库](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-build-managed.html)上，向量存储和文本存储都由你选择、预置、扩展和更新，并按所选基础设施单独付费。而在托管知识库上，这些环节都是服务的一部分，存储和检索直接计量收费。

定价模型也可能不同。客户管理的知识库，其存储和检索费用取决于你选择的向量存储。有些存储按预置容量或最低容量收费，另一些（如 Amazon S3 Vectors，Amazon S3 的一项能力）只按实际用量收费。托管知识库按你存储和检索的内容定价，因此成本随真实用量走。按用量计费适合低利用率运行的企业问答、政策和支持类知识库。最新费率参见 [Amazon Bedrock 定价](https://aws.amazon.com/bedrock/pricing/)。关于客户管理的知识库可用的解析器及其计费方式，参见[数据源的解析选项](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-advanced-parsing.html)。

| **成本项** | **客户管理的知识库** | **托管知识库** |
| --- | --- | --- |
| **向量存储** | 由所选存储单独计价。预置型检索服务即便用量低，也可能有最低闲置成本 | 已含在每 GB 每月 $5 的基础存储费率中 |
| **多模态文档解析** | 需要 Amazon Bedrock Data Automation（按页或按图片计费），或基础模型（按 token 计费）。纯文本解析免费 | 已包含 |
| **嵌入生成** | 按你所用嵌入模型的费率单独计费 | 默认模型已包含。仅当选择自定义模型时才收费 |
| **导入、同步与重新同步的计算** | 每次同步时的重新嵌入、编排代码和索引计算峰值都会带来周期性成本 | 已包含，增量同步只处理新增和变更的内容 |
| **connector** | 构建和运行自定义 connector 会增加计算成本 | 已包含原生 connector |
| **标准检索** | 每次查询 Amazon Bedrock 不收费。你的向量存储可能按查询收费，Amazon S3 Vectors 就是如此 | 每 1,000 次检索请求 $1 |
| **重排序** | Amazon Rerank 按每 1,000 次查询 $1 计费。自定义重排序模型按其自身费率计费 | 已含在每 1,000 次检索请求 $1 中 |
| **agentic 检索** | 你要在 Bedrock 模型上自行搭建 agentic 工作流，在开发和维护成本之外，每 1,000 次查询约需 $18 到 $24。由于模型用量按 token 计费，每次查询的价格并不固定 | agentic 检索在底层检索调用之外，每 1,000 次查询额外收取 $4，其中已包含多轮检索、重排序和答案生成。视底层检索调用次数，每 1,000 次查询总费用约在 $6 到 $9 之间 |

费率只是总拥有成本的一部分。在客户管理的知识库上，团队要把每个环节当作独立资源分别预置、扩展和运维。托管知识库把它们整合为一项资源，默认带嵌入模型、基础模型和重排序器，并默认按知识库设置速率限制。你管理内容和使用内容的应用程序，Amazon Bedrock 则运维托管存储、嵌入模型、基础模型和重排序器。

## 解决方案概述

客户管理的知识库使用 `VECTOR` 类型，向量存储由你配置。托管知识库使用 `MANAGED` 类型。迁移指南会引导你的 agent 在原有知识库旁新建一个 `MANAGED` 知识库，迁移期间不修改也不删除原有知识库。借助指南给出的映射，agent 会写出一份计划，列明哪些设置保持不变、哪些由托管方式以不同方式处理、以及你需要对应用程序做哪些改动。如图 1 所示，团队导入内容、验证并完成切换的同时，原有知识库持续响应每一个请求。

![coding agent 在原有 VECTOR 知识库旁新建 MANAGED 知识库的流程图；原有知识库持续为应用程序提供服务，直到团队验证检索并完成切换。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/03/ML-22176-1.png)

图 1：在原有知识库旁创建托管知识库或迁移后的模板，然后在切换前验证

## 迁移指南如何运作

这份指南把规划与实施分开。在 Explore 模式下，你的 agent 会回答关于托管知识库的问题，并能通过只读调用检查你的配置，方便你评估工作量。在 Migration 模式下，指南会带 agent 逐一经过以下检查点：

- **介绍与选择。** agent 说明它会动什么、不会动什么。你来选模式、实时知识库或 IaC 源，以及通俗（默认）还是技术化的讲解风格。
- **识别。** 确认账户和 AWS 区域。agent 会标出权限过宽的凭证，询问你是否需要成本分析，并创建输出目录。
- **探查。** agent 通过只读调用读取知识库和数据源，或读取你的模板文件。
- **规划。** 审阅计划和应用程序改动。默认情况下，agent 到此为止。
- **按需实施。** 实时构建时，你要批准配置脚本的精确预览，脚本有变动时还要再批一次。走 IaC 时，agent 写出迁移后的模板，并报告跑了哪些 schema 检查。
- **交接。** 审阅产出的内容，以及团队剩下的步骤。

如图 2 所示，资源创建与导入和切换始终分开。

![迁移检查点的流程图：依次经过介绍、识别、探查、规划，然后直接交接，或经过可选且需批准的实施环节；Explore 模式为只读，导入、验证、切换和退役由团队负责。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/03/ML-22176-2.png)

图 2：迁移检查点。实施是可选的，导入和切换由团队完成

### 查看配置映射

当托管类型采用不同配置时，指南会映射每一项设置，以保留你的数据源、过滤条件和分块行为。计划把每项设置归为三类：

- **1:1。** 新知识库沿用相同设置。
- **需调整。** 托管方式用不同的设置达成同样效果，计划会做相应替换。
- **受阻。** 目前没有对应的托管路径。agent 会把该知识库排除在构建之外、说明原因，并指引你联系 AWS Support。同一批次里的其他知识库仍可继续。

验证时，用你自己的内容对比一下分块效果。

### 查看权限与生成的改动

探查、规划以及整条 IaC 路径都只需要只读凭证。实时构建时，指南会要求 agent 提出一份限定范围的策略，明确拒绝对原有知识库的任何改动，且绝不索取管理员或完全访问权限。它还要求 agent 只改动自己创建的资源、用 Amazon Resource Name (ARN) 引用密钥、并忽略所读数据里出现的指令。批准运行前，先审阅生成的 AWS Identity and Access Management (IAM) 策略和预置脚本。构建完成后，到 [AWS CloudTrail 事件历史](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html) 核对 agent 的操作，其中保留 90 天的管理事件。每条事件都记录下 API 调用（例如 `CreateKnowledgeBase`）和发起调用的身份。

可选的成本分析里，agent 会按当前 AWS 价格，把你现在的花费与托管知识库的估算做对比。它只用只读输入，包括 Amazon CloudWatch 指标、Amazon S3 对象大小和 AWS Cost Explorer。每个数字都会标明是实测值、由你提供，还是估算值。

## 前置条件

规划与任何获批的资源创建请使用不同的凭证。

- 装有 Agent Toolkit for AWS 的兼容开发环境。
- 配置好最小权限只读 profile 的 AWS Command Line Interface (AWS CLI)。
- 能访问原有知识库的配置或其 IaC 文件。
- 可选的实时构建需要：按指南建议的策略配置、限定范围的 build profile；供新知识库使用的 IAM service role，指南会给 agent 信任策略和权限来帮你创建；以及运行生成的预置脚本所需的 Python 3 和 boto3。

Agent Toolkit for AWS 可用于兼容的开发环境，其 [GitHub 上的仓库](https://github.com/aws/agent-toolkit-for-aws) 列出了可用的 skill。本文示例使用 AWS CLI 2.37 和 boto3 1.43.32。

## 安装 skill

按你的 coding agent 对应的 [Agent Toolkit for AWS 入门说明](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/quick-start.html) 操作。`add-skill` 命令会把 `amazon-bedrock` skill 安装到它检测到的 coding agent 上。加 `--agent` 可指定某一个，例如 `--agent kiro`。

```
aws agent-toolkit add-skill \
    --skill-name amazon-bedrock
```

安装完成后，你描述迁移任务时 agent 就会加载迁移指南。下面的提示词只是示意输入，并非真实对话记录。

## 规划迁移

选择与你维护源的方式相符的路径。

| **路径** | **agent 读取什么** | **产出什么** | **AWS 改动** |
| --- | --- | --- | --- |
| Explore | 文档，以及（可选）你的知识库（只读） | 对话中的回答 | 无 |
| 实时知识库 | 你的知识库和数据源（只读） | 一份计划，以及（可选）在原有知识库旁新建一个托管知识库 | 仅在你批准确切预览之后 |
| 基础设施即代码 | 你的 AWS CloudFormation 模板、AWS Cloud Development Kit (AWS CDK) 合成模板，或 Terraform 配置 | 同格式的迁移后模板 | 无。由你的流水线部署 |

想从 Explore 模式开始，先问一个问题：

```
What would change if I moved knowledge base <your-kb-name>
in <your-region> to a Managed Knowledge Base? Use Explore mode.
```

准备好后，再选实时路径或 IaC 路径。

### 迁移实时知识库

授权创建资源之前，先要一份计划：

```
Plan a migration of knowledge base <your-kb-name> in <your-region>
to a Managed Knowledge Base. Stop after the plan.
```

确认账户和区域，再审阅计划里的映射和应用程序改动。默认情况下，新知识库沿用原名并加上 `-managed` 后缀。要构建它，先确认 service role 已存在，切到 build profile，检查预置脚本及其预览，然后批准。agent 会运行脚本，创建知识库和数据源，并报告状态。

### 迁移基础设施即代码

把 agent 指向源模板或配置：

```
Review <path-to-source-template> and plan a migration to a
Managed Knowledge Base.
```

agent 会把迁移后的文件写入输出目录，不部署任何东西，并把 diff 展示给你。想保留 diff，就让 agent 存下来。部署前先跑 `terraform init -backend=false` 和 `terraform validate`。这两个命令 agent 都能带你走一遍，但指南把检查留给你自己做，因为 `terraform init` 会下载体积很大的 AWS provider。应用部署计划前，确认它保留了回滚所需的原有资源。

### 对话示例

迁移以对话方式进行。读取任何内容之前，agent 会先声明自己的范围，并问你如何继续：

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

计划摘要会列出每一项映射、调用方要做的改动，以及你需要拍板的决策：

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

实时构建时，agent 会停在预览这一步，批准命令还需要带上计划的哈希值：

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

*示例对话经过少量编辑，标识符已替换。*

## 更新应用程序的检索调用

两种类型的知识库，应用程序都用同一个 `Retrieve` 操作。托管请求指向新的知识库 ID，并把 `vectorSearchConfiguration` 换成 `managedSearchConfiguration`。向托管知识库传 `vectorSearchConfiguration` 会返回校验错误。托管检索始终使用混合搜索，因此托管请求的结构里没有 `overrideSearchType` 字段。元数据过滤器的语法不变，只是托管知识库不支持 `startsWith` 和 `stringContains` 运算符。完整语法参见 [Retrieve API 参考](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_Retrieve.html)。

下面的示例假设两个知识库都含有过滤器用到的 `locale` 元数据。

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

在应用程序仍使用原有知识库期间，评估新知识库。

- 如果走 IaC，通过流水线审阅并部署目标配置。
- 同步每个数据源，检查有没有失败。参见[同步数据](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-data-source-sync-ingest.html)。
- 给应用程序的运行时 IAM role 授予新知识库 ARN 上的 `bedrock:Retrieve`，同时保留它对原有知识库的访问权限，以便回滚。
- 用该 role 通过 `Retrieve` 对两个知识库跑有代表性的查询。两种类型使用不同的评分标度。托管分数还取决于 `rerankingModelType`：搭配托管嵌入模型时默认为 `MANAGED`，搭配自定义模型时默认为 `NONE`。按模式分别调阈值，比较时保持模式不变。
- 测试用到的元数据过滤器和权限感知检索，包括已登录用户不该看到的内容。在启用 ACL 的数据源上，不带 `userContext.userId`（用户邮箱）的请求不会返回任何结果。
- 验收通过后，部署新的知识库 ID 和请求结构。在整个回滚期内，保留原有知识库、其当前内容以及应用程序配置。

对每条查询，检查两者是否返回相同的首位文档，以及结果重叠多少。可以写个简短脚本，按标准给出通过或失败，比如至少 90% 的查询首位文档一致、且托管知识库没有零结果查询。这个阈值要按你的工作负载调。其他检索质量指标（如上下文相关性、上下文覆盖率）参见[用指标衡量 RAG 系统性能](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-eval-retrieve.html)。

比较结果时留意这些差异：

- **比较前先规范化来源位置。** 客户管理的知识库可能在 `location.s3Location.uri` 里返回 `s3://bucket/key`，托管知识库则可能返回 `https://` URL。按对象键来比较。
- **比较首位结果，别假定结果条数相等。** 两种知识库返回的结果条数可能不同，而 `numberOfResults` 设的是上限而非保证值。比较首位文档，并逐条查看它发生变化的查询。详见[配置与自定义托管知识库的查询](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-test-config.html)。
- **映射被改名的系统元数据键。** 例如，在比较代码里把 `x-amz-bedrock-kb-data-source-id` 换成 `_data_source_id`。你自己的元数据属性名称不变。详见[配置与自定义托管知识库的查询](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-test-config.html)。

## 清理

如果完成了迁移，只在回滚期结束并做完依赖审查之后，才让原有知识库退役。保留托管知识库所导入的源文档和存储桶，以及其他工作负载仍在用的存储。IaC 管理的资源，通过各自所属的模板清理。

如果是终止评估，则保留原有知识库，并按以下顺序删除你创建的东西：

- 删除每个托管数据源，等它彻底消失。
- 删除托管知识库，等它彻底消失。
- 如果 service role 只是为这次评估创建的，先删它的内联策略，再删角色。
- 使用客户管理的密钥时，用 `aws kms list-grants` 查一下 Amazon Bedrock 创建的授权，它们在知识库删除后可能仍然保留。
- 保留任何仍被其他知识库读取的 S3 存储桶。

托管数据源上的删除保护限制的是一次同步能删掉多少内容，而不是你能不能删除这个数据源。删除原有知识库并不会删除它的向量存储，后者会继续产生费用，直到你把它移除。参见[删除 Amazon Bedrock 知识库](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-delete.html)。

## 结语

有了 Amazon Bedrock 托管知识库，你的团队不必再运行向量存储，也不必管理底层的检索基础设施。借助 `amazon-bedrock` skill 里的迁移指南，你向 agent 要一份计划、审阅它，只批准你想构建的资源。

想上手，先配置好 [Agent Toolkit for AWS](https://docs.aws.amazon.com/agent-toolkit/latest/userguide/quick-start.html)，让 agent 对你的知识库做一次只读评估。迁移之后，可以试试用 [agentic 检索](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-agentic-retrieve.html) 处理多部分问题。更多内容参见 AWS Machine Learning Blog 上的[用 Amazon Bedrock 托管知识库为 agent 构建企业搜索](https://aws.amazon.com/blogs/machine-learning/build-enterprise-search-for-agents-with-amazon-bedrock-managed-knowledge-base/)。

## 关于作者
