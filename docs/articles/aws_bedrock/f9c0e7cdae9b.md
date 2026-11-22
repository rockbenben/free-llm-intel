---
vendor: aws_bedrock
title: Build an intelligent contract management solution with Amazon Quick Suite and Bedrock AgentCore
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-an-intelligent-contract-management-solution-with-amazon-quick-suite-and-bedrock-agentcore
date: 2026-01-27
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 9ed0e8a0b7e9
---

# 使用 AWS Quick 与 Bedrock AgentCore 构建智能合同管理解决方案

每年管理数百份合同的组织面临明显的效率问题：系统彼此割裂、流程复杂，团队不得不把大量时间花在合同审阅周期上。本方案通过 multi-agent 协作来应对这些挑战——多个专门化的 AI agent 可以同时处理合同分析的不同方面，在缩短周期时间的同时保持准确性与可管控性。

本指南演示如何构建智能合同管理解决方案：以 [AWS Quick](https://aws.amazon.com/quicksuite/) 作为主要的合同管理方案，并用 [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/)增强其高级 multi-agent 能力。

## 为何要用 Amazon Bedrock AgentCore 增强 Quick

Quick 充当你的 agentic 工作空间，为聊天、调研、商业智能和自动化提供统一界面。Quick 帮助你从获取答案顺畅过渡到采取行动，同时还能把从日常例行事务到合同处理与分析这类复杂业务流程的任务自动化。

将 Amazon Bedrock AgentCore 与 Quick 结合使用，你可以更安全、更大规模地把业务逻辑封装进能力强大的 AI agent。AgentCore 的各项服务可与多种框架配合，包括 [Strands Agents](https://strandsagents.com/)，也支持 Amazon Bedrock 内外的各种基础模型。

## 方案概览

本方案演示了一个智能合同管理系统：由 Quick 充当用户界面与知识库，Amazon Bedrock AgentCore 提供 multi-agent 协作功能。系统借助专门化的 agent 分析合同、评估风险、检查合规性，并通过精简的架构提供结构化洞察，如下图所示。

![解决方案概览](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/16/ML-19870-image-1.png)

### 架构组件

方案架构包含以下组件：

- **Quick 组件：**  **Spaces** 用于合同管理工作流 **Chat agents** 用于对话式合同交互 **Knowledge bases** 用于集成存储在 Amazon S3 中的法律文档 **Topics** 用于集成结构化合同数据 **Actions** 用于连接用 Amazon Bedrock AgentCore 开发的自定义 agent **Flows** 用于周期性的半人工文档审阅流程 **Automate** 用于每日和每月的合同自动化任务
- **由 AgentCore 驱动的 multi-agent 系统：**  **Contract collaboration agent**：负责协调工作流的中心编排者 **Legal agent**：分析法律条款并提取关键义务 **Risk agent**：评估财务与运营风险 **Compliance agent**：评估监管合规性
- **支撑基础设施：**  [Amazon API Gateway](https://aws.amazon.com/api-gateway) 与 [AWS Lambda](https://aws.amazon.com/lambda) 用于管理 API 请求 [Amazon Simple Storage Service（Amazon S3）](https://aws.amazon.com/s3/) 用于文档存储 [Amazon Redshift](https://aws.amazon.com/redshift) 用于结构化数据

## 合同管理工作流

本方案实现了一套精简的合同管理工作流，在提升准确性的同时显著缩短处理时间。系统通过协同工作的 AI agent 处理合同，通常在几分钟内完成分析，而人工审阅往往需要数天。

| **Agent 类型** | **主要功能** | **关键输出** |
| --- | --- | --- |
| Contract collaboration agent | 中心编排者与工作流管理 | 文档路由决策与汇总结果 |
| Legal agent | 法律条款分析与义务提取 | 当事方详情、关键条款、义务与风险标记 |
| Risk agent | 财务与运营风险评估 | 风险评分、敞口指标与谈判建议 |
| Compliance agent | 监管合规性评估 | 合规状态、监管标记与整改建议 |

下面我们看一个处理示例服务协议合同的例子。该工作流包含以下步骤：

- **contract collaboration agent** 判断该文档需要法律、风险和合规三方面分析。
- **legal agent** 提取当事方、付款条款和义务。
- **risk agent** 识别财务敞口与谈判筹码。
- **compliance agent** 评估监管要求并标记潜在问题。
- **contract collaboration agent** 把各项发现汇总为一份完整报告。

## 前提条件

在设置 Quick 之前，请确认你已具备：

- 具有管理员权限的 AWS 账户
- 对 Quick 可用的受支持 AWS 区域的访问权限
- 用于 Quick 服务访问的相应 [AWS Identity and Access Management（IAM）](https://aws.amazon.com/iam) 角色与策略

## 设置第一部分：配置 Quick

下面的步骤将配置 Quick 的各项组件。

### 启用 Quick

你的 AWS 管理员可以通过以下方式启用 Quick：

- 登录 AWS Management Console
- 在控制台中导航到 Quick
- 为你的组织订阅 Quick 服务
- 按需配置身份与访问管理

Quick 启用后，请访问 [AWS Quick Web 界面](https://quicksight.aws.amazon.com/)并使用你的凭据登录。

### 创建合同管理空间

在 Quick 中新建一个名为 **Contract Management** 的空间，用于组织与合同相关的工作流和资源。之后你可以使用右侧的助手，就该空间中的资源提问。下图展示了初始空间。

![Contract Management 空间](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/16/ML-19870-image-2.jpg)

### 为非结构化数据（Amazon S3）配置知识库

请按以下步骤操作：

- 导航到 **Knowledge bases**：在 Integrations 区域中选择 **Knowledge bases**。
- 添加 Amazon S3 集成：  选择 **Amazon S3** 作为数据源。配置将用于存放合同文档的 S3 bucket。知识库创建完成后，把它添加到 **Contract Management** 空间。

![知识库与 S3 集成](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/26/ML-19870-image-3-1.jpeg)

### 为结构化数据（Amazon Redshift）配置知识库

请按以下步骤操作：

- **Add dataset**：在 **Datasets** 区域中，为结构化合同数据配置你的合同数据仓库（Amazon Redshift）。按 [Creating a dataset from a database](https://docs.aws.amazon.com/quicksuite/latest/userguide/create-a-database-data-set.html) 中的说明操作，并等待数据集配置完成。
- **Add data topics**：在 **Topics** 区域中，集成结构化合同数据源，例如：  合同数据库 供应商信息系统 合规跟踪系统

关于在 Quick 中添加 Topics，请参阅 [Adding datasets to a topic in AWS Quick Sight](https://docs.aws.amazon.com/quicksuite/latest/userguide/topics-data-add.html)。

- 把 Topics 添加到你的空间：将相关的 Topics 添加到你的 **Contract Management** 空间。

## 设置第二部分：部署 Amazon Bedrock AgentCore

Amazon Bedrock AgentCore 提供企业级基础设施来部署 AI agent，并具备会话隔离：每个会话运行时拥有隔离的 CPU、内存和文件系统资源。这在用户会话之间形成隔离，有助于保护有状态的 agent 推理过程。

- 所需代码可在该 [GitHub 仓库](https://github.com/aws-samples/sample-industry-genai/tree/main/Intelligent-Contract-Management-with-QuickSuite-and-AgentCore)中找到。请进入子目录 `legal-contract-solution/deployment`。
- 该方案包含一个功能完备的 `deploy_agents.py` 脚本，通过云端构建完成把 AI agent 部署到 AWS 的全过程。这些步骤要求 **Python>=3.10**。

```
pip3 install -r requirements.txt
python3 deploy_agents.py
```

### 部署脚本做了什么

部署过程完全自动化，负责处理：

- **依赖管理**：  按需自动安装 `bedrock-agentcore-starter-toolkit` 校验所需的 Python 包是否可用
- **AWS 基础设施搭建**：  创建具有 agent 执行所需权限的 IAM 角色 为容器镜像设置 [Amazon Elastic Container Registry（Amazon ECR）](https://aws.amazon.com/ecr) 仓库 配置 [Amazon CloudWatch](https://aws.amazon.com/cloudwatch) 日志用于监控
- **Agent 部署**：  部署四个专门化的 agent 使用 [AWS CodeBuild](https://aws.amazon.com/codebuild) 进行云端 ARM64 容器构建 无需本地 Docker——构建在 AWS 基础设施中完成
- **配置管理**：  自动配置 agent 通信协议 在 agent 之间设置安全边界 建立监控与可观测性

agent 部署完成后，你可以在 Amazon Bedrock AgentCore 控制台中看到它们，如下图所示。

![Bedrock AgentCore Agent](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/16/ML-19870-image-4.jpg)

## 设置第三部分：把 Amazon Bedrock AgentCore 与 Quick 集成

Quick 可以通过 actions 集成连接企业解决方案与 agent，让工具可供 chat agents 和自动化工作流使用。

**部署 API Gateway 与 Lambda**

进入子目录 `legal-contract-solution/deployment` 并运行以下命令：`python3 deploy_quicksuite_integration.py`

这会创建一个带 user pool 的 [Amazon Cognito](https://aws.amazon.com/cognito)，用于授权访问 API Gateway 端点。Quick 配置会引用该 user pool 的 OAuth 详细信息。部署成功后，会为你的 Quick 集成生成两个文件：

- `quicksuite_integration_config.json` – 完整配置
- `quicksuite_openapi_schema.json` – 供 Quick 导入的 OpenAPI schema

**在 Quick 中设置 actions 集成**

在 **Actions** 区域中，准备好用于连接由 AgentCore 部署的 agent 的集成点：

- 从工作目录中获取 OpenAPI 规范文件 `quicksuite_openapi_schema.json`。
- 在 **Integrations/Actions** 区域中进入 **OpenAPI Specification**。通过上传 `api_gateway_openapi_schema.json` 文件创建新的 OpenAPI 集成，并为提供的 agent 填写下面的 **Name** 与 **Description**。使用 `quicksuite_integration_config.json` 文件中的信息填写端点 URL。  **Name**：Legal Contract Analyzer **Description**：利用 AI agent 对法律合同进行条款提取、风险评估与合规检查

**设置 chat agent 定义细节**

在 **Chat agents** 区域中，按下面的设置创建 agent 并填写以下详情：

- **Name**：`Legal Contract AI Analyzer`
- **Description**：  `一套由 AI 驱动的系统，使用先进的机器学习能力分析法律合同并做全面风险评估，识别潜在问题、合规缺口与合同风险。`
- **Agent 身份：**  `你是一套由先进 GenAI 能力驱动的专业法律合同分析 AI 系统。你的职责是提供全面的合同审阅与风险评估服务。`
- **Persona 指令：**  `尽可能使用法律合同分析器。始终按严重程度（High、Medium、Low）对风险分类。突出非标准条款、缺失条款和潜在合规问题。为合同改进提供具体建议。分析责任条款时，特别关注赔偿、责任限制和不可抗力条款。标记任何异常的终止条件或知识产权问题。`
- **沟通风格：** `专业、精确、分析性强，使用清晰的法律术语。`
- **响应格式：**  `提供结构化分析，包含清晰的风险分类、严重程度等级和可执行的建议。关键发现用项目符号列表，优先建议用编号列表。`
- **长度：**  `覆盖所有关键方面的全面分析，同时保持清晰并聚焦于可执行的洞察。`
- **欢迎消息：**  `欢迎使用 Legal Contract AI Analyzer。上传合同即可进行智能分析与风险评估。`
- **推荐 prompt：**  `分析这份合同中的潜在法律风险与合规问题` `审阅本协议中的责任条款，找出需警惕的危险信号` `评估本合同中的终止条件与通知要求`

## 测试你的合同管理方案

基础设施已部署、Quick 已配置完成，现在你可以选择 **Contract Management** 空间来测试合同管理方案。你可以通过 agent 界面就知识库提问，并指示 agent 审阅文档。你的空间会如下图所示：

## 清理资源

部署的方案会产生相应的基础设施费用。当你在 AWS 账户中不再需要它时，可以进入子目录 `legal-contract-solution/deployment` 并运行以下命令进行清理：`python3 cleanup.py`

## 结论

AWS Quick 与 Amazon Bedrock AgentCore 的结合，为采购和法律团队带来即时的运营收益，同时让他们为未来的 AI 进展做好准备。你可以使用 Amazon Bedrock multi-agent 协作来构建和管理多个专门化 agent，让它们协同应对日益复杂的业务流程。通过落地这套智能合同管理方案，你可以改造组织的采购流程、缩短合同周期，并让团队专注于战略决策而不是事务性工作。得益于方案可扩展的架构，你可以从核心合同管理功能起步，随着组织需求演进逐步扩展到更复杂的用例。无论你是想简化日常合同审阅，还是推进全面的采购转型，这套智能合同管理方案都为实现业务目标提供了强大基础。要了解更多关于 AWS Quick 与 Amazon Bedrock AgentCore 的信息，请参阅：

- [AWS Quick](https://aws.amazon.com/quicksuite/)
- [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/)

### 关于作者

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/14/Oliver-Steffmann_bio-2-100x100.png)Oliver Steffmann** 是 AWS 的 Principal Solutions Architect，常驻纽约，热衷于 GenAI 与公共区块链用例。他有超过 20 年与金融机构合作的经验，帮助客户把云转型真正启动起来。工作之外，他喜欢与家人相处，并为下一场 Ironman 训练。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/16/David-Dai.jpeg)David Dai** 是 AWS 的 Enterprise Solutions Architect，常驻纽约。他与不同行业的客户合作，帮助他们设计并实施能创造业务价值的云解决方案。David 热衷于云架构，乐于引导组织走完数字化转型之旅。工作之外，他重视与家人共度优质时光，也喜欢探索最新技术。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/08/09/krishna.jpg)Krishna Pramod** 是 AWS 的 Senior Solutions Architect。他作为客户信赖的顾问，引导客户用现代技术创新，并在 AWS 云上开发架构良好的应用。工作之外，Krishna 喜欢阅读、音乐和探索新的目的地。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/16/manemalh1-1.jpg)Malhar Mane** 是 AWS 的 Enterprise Solutions Architect，常驻西雅图，为不同行业的企业客户担任可信赖的顾问。他对生成式 AI 与存储解决方案怀有深厚热情，专长是引导组织完成云转型，并帮助他们借助生成式 AI 优化业务运营、推动创新。Malhar 拥有加州大学欧文分校的计算机科学学士学位。业余时间，他喜欢徒步和探索国家公园。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/16/Praveen-Panati.jpg)Praveen Panati** 是 Amazon Web Services 的 Senior Solutions Architect。他热衷于云计算，与 AWS 企业客户合作架构、构建并扩展基于云的应用，以实现其业务目标。Praveen 的专长包括云计算、大数据、流式分析和软件工程。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/16/sesan_komaiya-100x133.png)Sesan Komaiya** 是 Amazon Web Services 的 Solutions Architect。他与各类客户合作，帮助其推进云采用、成本优化和新兴技术。Sesan 在企业 IT 领域有超过 15 年经验，在 AWS 已任职 5 年。业余时间，他喜欢观看各种体育赛事，如足球、网球和摩托车运动。他还有两个孩子，在家里也让他十分忙碌。
