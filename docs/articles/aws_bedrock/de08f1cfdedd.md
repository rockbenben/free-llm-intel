---
vendor: aws_bedrock
title: 使用 Amazon Bedrock AgentCore 构建自我改进的文档处理
original_title: Build self-improving document processing using Amazon Bedrock AgentCore
url: https://aws.amazon.com/blogs/machine-learning/build-self-improving-document-processing-using-amazon-bedrock-agentcore
date: 2026-10-14
lang: zh
captured: 2026-10-15
extractor: readability-v1
translator: agent
status: translated
body_sha: 65e1068d1fea
---

## [人工智能](https://aws.amazon.com/blogs/machine-learning/)

# 使用 Amazon Bedrock AgentCore 构建自我改进的文档处理

[IDC 的研究](https://warekennis.nl/wp-content/uploads/2013/11/bridging-the-information-worker-productivity-gap.pdf)显示，文档相关的难题每年给组织带来每名信息工作者（information worker）19,732 美元的成本，并让生产力下降 21.3%。要从数百家供应商接收发票的组织，常常面对因开票方而异、而且说变就变、事先不打招呼的版式。在这个规模上，基于模板的系统需要持续维护。员工可能把多达 30% 的时间花在文档相关任务上，而人工数据录入的错误率在 [1–4%](https://askelie.io/manual-document-processing-costs/) 之间。传统的智能文档处理（IDP）方案能减轻一部分负担，但它们对每一种文档格式都需要大量预先配置，并且在版式因供应商而异时会崩掉。

在这篇文章里，你会学到如何用 [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) 构建一个 agentic 的 IDP 系统，它在极少人工干预下对业务文档进行分类、抽取、校验并从中学习。Amazon Bedrock AgentCore 是一个可用任意框架或模型大规模构建、连接并优化 agent 的平台。你的 agent 会自动处理新的文档格式，例如供应商发票、采购订单、保险理赔和贷款申请。读完这篇文章，你可以：

- 部署一套多 agent 的 IDP 系统，通常在 20 分钟之内。
- 处理新的文档类型而无需人工配置模板。
- 让 agent 在每一种新的文档格式上自我训练并复用它们学到的东西，于是同类型的后续文档直接进入抽取、无需重新训练。

## 基于规则的文档处理带来的挑战

许多 IDP 管线要求你为每一种文档格式预先定义模板、抽取规则和校验逻辑。当一家新供应商发来版式不同的采购订单时，管线就断了。这带来三个核心挑战：

- **模板僵化：**每一种新的文档格式都需要人工配置，而哪怕细微的版式变化也会导致抽取失败。
- **没有学习：**同样的抽取错误会在相似文档上反复出现，因为系统不会从先前的纠正中保留知识。
- **扩展负担：**每新增一个供应商或文档变体都会让维护工作量成倍增长，处理来自数百个来源文档的组织要面对持续的运营成本。

agentic 的方法应对了这些挑战。AI agent 不再依赖静态模板，而是分析每一份文档、生成抽取指令、校验结果，并自动从纠正中学习。随着时间推移，你的系统会积累出一个文档格式知识库，于是你在处理相似文档时只需极少的额外配置。

## 方案总览

在这个方案里，八个专用 agent 协作跨两条运行于 Amazon Bedrock AgentCore 之上的基于图（graph-based）的工作流。

下图展示了使用 [Strands Agents](https://strandsagents.com)（一个用于构建 AI agent 的开源 SDK）构建的多 agent 工作流图。

图 1：多 agent 编排工作流图

- **识别工作流**：Analyzer agent 用 [Amazon Textract](https://aws.amazon.com/textract/) 抽取文本，并识别文档类型和发送方。Matcher agent 用 [Amazon S3 Vectors](https://aws.amazon.com/s3/features/vectors/)（Amazon Simple Storage Service（Amazon S3）的一项能力）中的向量相似度来搜索相似文档。
- **训练工作流**（新的文档类型）：当没有找到匹配项时，Instructions agent 生成抽取用的 prompt，Extractor agent 抽取结构化数据，Validator agent 依据 [Amazon Aurora DSQL](https://aws.amazon.com/rds/aurora/dsql/) 中的 schema 和业务规则校验结果。如果校验失败，Instructions Fixer agent 会改进 prompt 并重试。成功时，Save Instructions agent 把指令持久化以便复用。
- **自动化工作流**（已知的文档类型）：当找到匹配项时，Extractor agent 使用已有的指令。如果校验失败，Troubleshooter agent 直接修正抽取到的数据，而不改动指令。

### 它是如何工作的

下图展示了该方案的基础设施架构。

图 2：AWS 上的 agentic IDP 基础设施架构

- 业务文档通过 [Amazon Simple Email Service](https://aws.amazon.com/ses/)（Amazon SES）到达，或直接上传到 Amazon S3。
- [Amazon EventBridge](https://aws.amazon.com/eventbridge/) 触发一个 [AWS Lambda](https://aws.amazon.com/lambda/) 函数，该函数在 [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) 中创建一条跟踪作业，并调用 AgentCore runtime（Amazon Bedrock AgentCore 的一项能力）。
- AgentCore runtime 通过 Strands Agents 编排文档处理。
- 你的 agent 通过由 AgentCore Identity（Amazon Bedrock AgentCore 的一项能力）和 [Amazon Cognito](https://aws.amazon.com/cognito/) 管理的机器对机器凭证，安全地访问 AWS 资源。
- 你的 Lambda 函数通过 AgentCore Gateway（Amazon Bedrock AgentCore 的一项能力）的 Model Context Protocol（MCP）接口，成为与 agent 兼容的工具。
- Agent 用 Amazon Textract 抽取文本，用 S3 Vectors 中的向量 embedding 对文档做分类，并依据 Aurora DSQL 中的业务规则校验数据。
- Agent 通过 MCP server 访问企业数据，以对照业务规则校验抽取到的内容。
- 你通过托管在 [Amazon Elastic Container Service](https://aws.amazon.com/ecs/)（Amazon ECS）上的、带聊天能力的 dashboard 来监控状态和排查问题。
- 你通过 AgentCore Observability（Amazon Bedrock AgentCore 的一项能力）和 [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/) 遥测数据，获得对 agent 表现的可见性。

## 部署方案

按以下步骤把方案的基础设施和 Web UI 部署到你的 AWS 账户。

### 前提条件

要部署这个方案，你必须具备：

- 一个 [AWS 账户](https://portal.aws.amazon.com/gp/aws/developer/registration/index.html)。
- 对 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 的访问权限，并启用了 Amazon Nova 和 Anthropic (Claude) 模型。有关各 AWS Region 的模型可用性，参见 [Amazon Bedrock 按 AWS Region 划分的受支持模型](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html)。
- 对 Amazon Bedrock AgentCore（Runtime、Gateway、Identity）、S3 Vectors 和 Amazon Aurora DSQL 的访问权限，且需位于[受支持的 Region](https://docs.aws.amazon.com/bedrock/latest/userguide/bedrock-regions.html) 之内。
- 已安装 [AWS Cloud Development Kit](https://aws.amazon.com/cdk/)（AWS CDK）v2。
- 已安装并正在运行 [Docker](https://docs.docker.com/get-docker/)（构建和部署容器镜像所需）。
- Python 3.11+ 和 Node.js 18+。
- 用于创建 S3 桶、Lambda 函数、DynamoDB 表、Cognito 用户池、Amazon Elastic Container Registry（Amazon ECR）仓库和 Amazon ECS 服务的 [AWS Identity and Access Management](https://aws.amazon.com/iam/)（IAM）权限。

- 克隆 [仓库](https://github.com/aws-samples/aws-ai-intelligent-document-processing/tree/main/guidance/agentic-orchestration) 并搭建环境：  `git clone https://github.com/aws-samples/agenticidp-guidance.git cd agenticidp-guidance uv venv source .venv/bin/activate uv pip install -r requirements.txt cd ui/orchestrator npm install cd ../..`
- 部署各个 stack：  `uv run deploy.py --admin-email your-email@example.com`

这会部署六个 [AWS CloudFormation](https://aws.amazon.com/cloudformation/) stack：Core（S3、Cognito、DynamoDB）、Gateway（Lambda 工具、AgentCore Gateway）、Aurora（Amazon Aurora DSQL）、Agent（AgentCore runtime、容器）、UI Orchestrator（API 端点）以及 Modern UI（跑在 [Amazon CloudFront](https://aws.amazon.com/cloudfront/) 上的 React 应用）。部署大约需要 15–20 分钟。

- 验证部署：检查每个 stack 在 CloudFormation 控制台中都显示 `CREATE_COMPLETE`。

## 处理文件并查看结果

部署完成后，你会收到一封邮件，里面有 CloudFront URL、用户名和临时密码。

### 处理一份文档

- 登录 Web UI 并选择 **Process Document**。
- 从 `infrastructure/sample_data/purchase_orders/training/` 上传一份示例采购订单。
- 文档进入 agent 工作流：  Analyzer agent 抽取文本并识别发送方和文档类型。Matcher agent 在向量存储中搜索相似文档。对于新的文档类型，训练工作流会生成抽取指令、抽取数据、校验它，并保存指令供日后使用。对于已知的文档类型，自动化工作流使用已有的指令抽取数据并校验它。
- 在 **Review Jobs and Instructions** 标签页中查看结果，核对抽取到的数据、校验结果和生成的指令。

### 示例：一种新的文档类型（训练工作流）

假设你上传了来自一家新零售商 Two Wheel Store 的第一份采购订单。Matcher agent 在向量存储中搜索，找不到相似文档，于是把这个作业路由给训练工作流。

Analyzer agent 用 Amazon Textract 抽取原始文档文本：

```
# PURCHASE ORDER
FROM: Two Wheel Store
Order #: PO-2026-0102-2584
Date: 2026-01-02

## Items Ordered
AC-021  Advanced Computer     Qty: 1   $75.61
        Colors: cr4321        @ $75.61
...
SB-004  Folding Classic       Qty: 8   $9634.32
        Colors: cb8901 I Sizes: S     @ $1204.29

TOTAL: $14931.54
```

Instructions agent 依据 schema 生成抽取用的 prompt，Extractor agent 产出结构化的 JSON：

```
{
  "po_number": "PO-2026-0102-2584",
  "retailer_name": "Two Wheel Store",
  "order_date": "2026-01-02T00:00:00Z",
  "line_items": [
    { "sku": "AC-021", "product_name": "Advanced Computer", "quantity": 1, "unit_price": 75.61, "line_total": 75.61 },
    { "sku": "SB-004", "product_name": "Folding Classic",   "quantity": 8, "unit_price": 1204.29, "line_total": 9634.32 }
  ],
  "order_total": 14931.54
}
```

Validator agent 对照 schema 检查结果，并判定**失败**：

```
validation_status: INVALID
error: 'SB-004' does not match '^AB-[A-Z]{2}-\d{3}$'
```

供应商的 SKU 格式（`SB-004`）与 Acme Bikes 的内部格式（`AB-SB-004`）不匹配。Instructions Fixer agent 诊断出这个不匹配，并在抽取 prompt 里加了一条明确的 SKU 转换规则：给供应商的 SKU 加上 `AB-` 前缀。第二趟，七个行项目全部校验通过，Save Instructions agent 把改进后的 prompt 持久化到向量存储。这次首趟运行的端到端耗时：3 分 49 秒。

### 示例：一种已知的文档类型（自动化工作流）

当来自 Two Wheel Store 的第二份采购订单到达时，Matcher agent 找到了首趟运行存下的指令，置信度得分为 3.946（阈值：3.7），并把这个作业路由给自动化工作流：

- Extractor agent 直接应用存下的指令，因此编排器跳过了 prompt 生成。训练期间学到的那条 SKU 转换规则自动生效（`EL-002` → `AB-EL-002`、`HB-071` → `AB-HB-071`、`PD-002` → `AB-PD-002`）。
- 三个行项目在第一趟就校验通过，订单总额为 $5,979.19。
- 端到端处理在 1 分 30 秒内完成，低于首趟运行的 3 分 49 秒。

### 使用交互式聊天

dashboard 里包含一个用于排查问题的聊天界面：

- 问 `what tools do you have` 可以看到可用的 agent 能力。
- 问 `list instructions` 可查看存下的抽取指令。
- 问 `what is the status of job XXXX` 来检查处理进度。
- 问 `what went wrong with job XXXX, how can we update the instructions?` 来诊断失败。

### 理解准确率如何随时间提升

系统通过两条反馈闭环随时间改进：

- **训练闭环**：当 Instructions Fixer agent 在校验失败之后改进了抽取 prompt，改进后的指令会被保存并在相似文档上复用。
- **处理闭环**：当 Troubleshooter agent 修正抽取错误时，它会给出详尽的分析，帮助识别文档格式变化中的规律。

更换模型时，用 [AgentCore Evaluations](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations.html)（Amazon Bedrock AgentCore 的一项能力）来确认抽取质量仍然可以接受。这个方案已经用上了 AgentCore Observability，因此它具备所需的埋点。

## 预估成本

你只为实际使用的部分付费，因为这个方案跑在 serverless 与按需资源上，没有闲置成本。在 US East (N. Virginia)，一个每月 10 份训练文档、1,000 份处理文档的工作量，预估成本约为每月 $58。通过 Amazon Bedrock 的基础模型（FM）推理约占总成本的 85%，大约每份文档 $0.055。实际成本在很大程度上取决于分配给每个 agent 的模型。模型选择集中在 `agents/orchestratorgraph/utils/config.py` 里，因此你可以对更简单的任务用成本更低的模型，在需要的地方用更强的模型。详细定价参见 [Amazon Bedrock 定价](https://aws.amazon.com/bedrock/pricing/)页面。

## 为你的用例定制方案

你拿到的是一个采购订单处理用例，配一份合成自行车公司的数据集、一个预建的 JSON schema，以及一个校验用的 Lambda 函数——它把抽取到的数据与一个模拟 ERP 数据库里的产品和供应商记录做比对。要处理你自己的文档，你必须把随附的 schema 和校验逻辑换成你自己的。

### 定义你的文档 schema

创建一个 JSON schema，为每一种文档类型定义你想抽取的字段。`agents/orchestratorgraph/doc_schema/purchase_order_schema.json` 里的示例采购订单 schema 可以用作参考。你的 schema 应当指明字段名、数据类型，以及每个字段是在文档中被明确写出的、还是从上下文推断出来的。

### 构建你的校验流程

随附的 validator 会把采购订单数据与 Aurora DSQL 中合成的供应商表和产品表做比对。你的生产实现需要一个按你的业务规则定制的校验流程。例如：

- 发票 validator 可能对照你的应付账款系统核验供应商 ID，并验证行项目合计与发票总额相符。
- 合同 validator 可能验证文档包含必需的条款，并且日期与当事方名称和你的记录一致。
- 理赔 validator 可能对照你的保单管理系统检查保单号、承保限额和理赔人信息。

要新增一个 validator，创建一个接受抽取到的 JSON、并返回带详细错误信息的通过/失败结果的 Lambda 函数，然后把它注册为 AgentCore Gateway 中的一个工具。实现模式参见 `gateway/tools/po_validator_tool/`。

### 更新 agent 的 prompt

`agents/orchestratorgraph/prompts/` 里的 agent prompt 引用了采购订单的术语。请更新这些 prompt 以反映你的文档类型和抽取需求。Orchestrator agent、Validator agent 和 Instructions agent 各自都包含与特定文档类型相关的表述，你应当加以调整。

## 最佳实践

在训练和运营你的 agentic IDP 系统时，请记住这些建议。

- **从有代表性的样本开始**：训练期间每种类型上传 5–10 份文档，包括带格式变化的边缘用例，以建立可靠的抽取指令。
- **使用业务规则校验**：在 Aurora DSQL 中把 validator 连到你的参考数据（供应商列表、产品目录），以尽早发现抽取错误。
- **监控 agent 表现**：用 AgentCore Observability 和 CloudWatch 跟踪执行路径、识别瓶颈，并衡量抽取准确率随时间的变化。
- **增量地添加文档类型**：为每一种新的文档类型创建一个 JSON schema 和对应的校验 Lambda 函数。剩下的交给 agent。
- **为生产环境加护栏**：应用 Amazon Bedrock Guardrails，对 agent 的输出施加内容过滤和 grounding 检查。在处理保险理赔或贷款申请这类敏感的文档类型时，这一点尤其重要。
- **查看 OWASP Top 10 for LLMs**：在构建使用大语言模型（LLM）的应用时，查阅 [OWASP Top 10 for LLMs and Generative AI Apps](https://genai.owasp.org/llm-top-10/) 了解安全方面的考量。

## 清理

**重要：**在运行清理之前，先导出你想保留的数据。`destroy.py` 脚本会永久删除已处理的文档（S3）、作业历史（DynamoDB）、校验数据（Aurora DSQL）以及学到的抽取指令（向量存储）。

要避免持续产生费用，删除已部署的资源：

```
uv run destroy.py
```

在控制台确认这六个 CloudFormation stack 已被删除：AgenticIDP-Core-Dev、AgenticIDP-Gateway-Dev、AgenticIDP-Aurora-Dev、AgenticIDP-Agent-Dev、AgenticIDP-UIOrchestr-Dev 和 AgenticIDP-ModernUI-Dev。

## 结论

在这篇文章里，你学到了如何用 Amazon Bedrock AgentCore 构建一个自我改进的文档处理系统——在其中，专用的 AI agent 协作完成对业务文档的分类、抽取、校验和学习。这种 agentic 方法会自动适应新的文档格式，并通过反馈闭环随时间提升准确率，用自主学习取代人工模板配置。

作为下一步：

- 部署[示例方案](https://github.com/aws-samples/aws-ai-intelligent-document-processing/tree/main/guidance/agentic-orchestration)，并用随附的采购订单样本进行测试。
- 通过创建 JSON schema 和校验规则来添加你自己的文档类型。
- 探索如何把抽取到的数据与 ERP、CRM 或内容管理工具这类下游系统集成。

要了解更多关于本文所用服务与模式的信息，参见以下资源：

- 要深入了解本方案所用的 agent 框架，参见 [Strands Agents SDK：agent 架构与可观测性的技术详解](https://aws.amazon.com/blogs/machine-learning/strands-agents-sdk-a-technical-deep-dive-into-agent-architectures-and-observability/)。
- 要理解 AgentCore Gateway 如何把 API 变成与 agent 兼容的工具，参见 [介绍 Amazon Bedrock AgentCore Gateway：变革企业 AI agent 工具开发](https://aws.amazon.com/blogs/machine-learning/introducing-amazon-bedrock-agentcore-gateway-transforming-enterprise-ai-agent-tool-development/)。
- 关于 Model Context Protocol 以及它如何与 AWS 服务集成的背景，参见 [在 AWS 上释放 Model Context Protocol（MCP）的力量](https://aws.amazon.com/blogs/machine-learning/unlocking-the-power-of-model-context-protocol-mcp-on-aws/)。
- 要了解 agent 如何跨会话保留上下文，参见 [Amazon Bedrock AgentCore Memory：构建具备上下文感知能力的 agent](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-memory-building-context-aware-agents/)。
- 关于 Amazon Bedrock AgentCore 能力的细节，参见 [Amazon Bedrock AgentCore 文档](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore.html)。

要在构建文档处理方案上获得专家指导，[AWS Professional Services](https://aws.amazon.com/professional-services/) 和 [AWS Partners](https://aws.amazon.com/partners/) 可以提供帮助。

## 关于作者
