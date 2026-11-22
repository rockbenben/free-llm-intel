---
vendor: aws_bedrock
title: Use Amazon SageMaker Unified Studio to build complex AI workflows using Amazon Bedrock Flows
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/use-amazon-sagemaker-unified-studio-to-build-complex-ai-workflows-using-amazon-bedrock-flows
date: 2025-07-01
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 16c5ea09fde7
---

# 使用 Amazon SageMaker Unified Studio 借助 Amazon Bedrock Flows 构建复杂的 AI 工作流

组织面临的一大挑战是：要在不同环境中管理数据、多种人工智能与机器学习（AI/ML）工具以及工作流，这会影响生产力与治理。统一的开发环境把数据处理、模型开发与 AI 应用部署整合到单一系统中。这种集成精简了工作流、增强了协作，并加速 AI 方案从概念到生产的开发过程。

新一代 [Amazon SageMaker](https://aws.amazon.com/sagemaker/) 是你的数据、分析与 AI 的中心。SageMaker 汇聚了 AWS 的 AI/ML 与分析能力，提供统一的数据访问，并带来分析与 AI 的集成体验。[Amazon SageMaker Unified Studio](https://aws.amazon.com/sagemaker/unified-studio/) 是一个单一的数据与 AI 开发环境，你可以在其中查找并访问自己的数据，并用 AWS 的分析与 AI/ML 服务对其操作，涵盖 SQL 分析、数据处理、模型开发与生成式 AI 应用开发。

使用 SageMaker Unified Studio，你可以在可信且安全的环境中，借助 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 高效构建生成式 AI 应用。你可以从精选的高性能基础模型（FM）中选择，并使用先进的定制能力与工具，例如 [Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/)、[Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/)、[Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/) 与 [Amazon Bedrock Flows](https://aws.amazon.com/bedrock/flows/)。你可以快速定制并部署生成式 AI 应用，并通过内置目录进行分享以供发现。

本文演示如何使用 SageMaker Unified Studio 借助 Amazon Bedrock Flows 创建复杂的 AI 工作流。

## 方案概览

设想一家领先的金融机构 FinAssist Corp，正在开发一个由生成式 AI 驱动的 agent 支持应用。该方案提供以下关键特性：

- **投诉参考系统** – 一个由 AI 驱动的系统，提供对历史投诉数据的快速访问，使客服代表能够高效处理客户跟进、支持内部审计，并协助培训新员工。
- **智能知识库** – 一个覆盖已解决投诉的全面数据源，可快速检索相关投诉详情、处理动作与结果摘要。
- **精简的工作流管理** – 通过对过往案例信息的标准化访问，提升客户沟通的一致性，支持合规检查与流程改进举措。
- **灵活的查询能力** – 一个简洁的界面，支持多种查询场景，从客户询问过往的解决方案，到内部审查投诉处理流程。

我们来探讨 SageMaker Unified Studio 与 Amazon Bedrock Flows 如何结合 Amazon Bedrock Knowledge Bases 与 Amazon Bedrock Agents，通过构建一个 AI 驱动的投诉参考系统来应对这些挑战。下图展示了方案架构。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/1_Soultion_Architecture_image-1.png)

本方案使用以下关键组件：

- **SageMaker Unified Studio** – 提供开发环境
- **Flow 应用** – 编排工作流，包括：知识库查询、基于 prompt 的分类、条件路由、基于 agent 的响应生成

该工作流通过以下步骤处理用户查询：

- 用户提交一个与投诉相关的问题。
- 知识库提供相关的投诉信息。
- prompt 分类该查询是否与处理时限相关。
- 基于使用该条件所做的分类，应用采取以下动作：把查询路由到 AI agent 以给出具体的处理结果回答；返回一般性的投诉信息。
- 应用为用户生成相应的回答。

## 前提条件

本示例需要以下条件：

- [访问 SageMaker Unified Studio](https://docs.aws.amazon.com/sagemaker-unified-studio/latest/userguide/getting-started-access-the-portal.html)。（你需要从管理员处获取 SageMaker Unified Studio 门户 URL）。你可以使用以下任一方式完成身份验证：[AWS Identity and Access Management](https://aws.amazon.com/iam/)（IAM）用户凭证；或使用 [AWS IAM Identity Center](https://aws.amazon.com/iam/identity-center/) 的单点登录（SSO）凭证。
- IAM 用户或 IAM Identity Center 用户必须拥有以下方面的适当权限：SageMaker Unified Studio；Amazon Bedrock（包括 Amazon Bedrock Flows、Amazon Bedrock Agents、Amazon Bedrock Prompt Management 与 Amazon Bedrock Knowledge Bases）。更多信息请参阅[基于身份的策略示例](https://docs.aws.amazon.com/sagemaker-unified-studio/latest/adminguide/security_iam_id-based-policy-examples.html)。
- [访问 Amazon Bedrock FM](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)（请确保这些模型已为你的账户启用），例如：Anthropic 的 Claude 3 Haiku（用于 agent）。
- 为 SageMaker Unified Studio 项目中的 Amazon Bedrock [配置访问权限](https://docs.aws.amazon.com/sagemaker-unified-studio/latest/adminguide/amazon-bedrock.html#manage-models)，以使用你的 Amazon Bedrock 无服务器模型。
- Amazon Titan Embedding（用于知识库）。
- 以 CSV 格式准备好的示例投诉数据，用于创建知识库。

## 准备数据

我们创建了一个示例数据集，用于 Amazon Bedrock Knowledge Bases。该数据集包含客服代表收到的投诉信息以及处理结果信息。以下是该示例数据集中的一个示例：

```
complaint_id,product,sub_product,issue,sub_issue,complaint_summary,action_taken,next_steps,financial_institution,state,submitted_via,resolution_type,timely_response
FIN-2024-001,04/26/24,"Mortgage","Conventional mortgage","Payment issue","Escrow dispute","Customer disputes mortgage payment increase after recent escrow analysis","Reviewed escrow analysis, explained property tax increase impact, provided detailed payment breakdown","1. Send written explanation of escrow analysis 2. Schedule annual escrow review 3. Provide payment assistance options","Financial Institution-1","TX","Web","Closed with explanation","Yes"
FIN-2024-002,04/26/24,"Money transfer","Wire transfer","Processing delay","International transfer","Wire transfer of $10,000 delayed, customer concerned about international payment deadline","Located wire transfer in system, expedited processing, waived wire fee","1. Confirm receipt with receiving bank 2. Update customer on delivery 3. Document process improvement needs","Financial Institution-2","FL","Phone","Closed with monetary relief","No"
```

## 创建项目

在 SageMaker Unified Studio 中，用户可以使用项目就各类业务用例展开协作。在项目内，你可以管理 SageMaker Unified Studio 目录中的数据资产、执行数据分析、组织工作流、开发机器学习模型、构建生成式 AI 应用等等。

要创建项目，请完成以下步骤：

- 使用管理员提供的 URL 打开 SageMaker Unified Studio 落地页。
- 选择 **Create project**。
- 输入项目名称与可选描述。
- 在 **Project profile** 中，选择 **Generative AI application development**。
- 选择 **Continue**。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/2_Create_Project_image-2.png)

- 完成项目配置，然后选择 **Create project**。

## 创建 prompt

我们来创建一个可复用的 prompt 来承载给 FM 的指令，稍后创建 flow 应用时会用到它。更多信息请参阅[复用与共享 Amazon Bedrock prompt](https://docs.aws.amazon.com/sagemaker-unified-studio/latest/userguide/prompt-mgmt.html)。

- 在 SageMaker Unified Studio 中，在 **Build** 菜单下选择 **Machine Learning & Generative AI** 中的 **Prompt**。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/3_Prompt_image-3.png)

- 为 prompt 提供一个名称。
- 选择适当的 FM（本示例中选择 **Claude 3 Haiku**）。
- 在 **Prompt message** 中，输入以下内容：

```
You are a complaint analysis classifier. You will receive complaint data from a knowledge base. Analyze the {{input}} and respond with a single letter:
T: If the input contains information about complaint resolution timing, response time, or processing timeline (whether timely or delayed)
F: For all other types of complaint information
Return only 'T' or 'F' based on whether the knowledge base response is about resolution timing. Do not add any additional text or explanation - respond with just the single letter 'T' or 'F'.
```

- 选择 **Save**。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/4_Create_Version_image-4.png)

- 选择 **Create version**。

## 创建 chat agent

我们来创建一个 chat agent 来处理具体的处理结果回答。请完成以下步骤：

- 在 SageMaker Unified Studio 中，在 **Build** 菜单下选择 **Machine Learning & Generative AI** 中的 **Chat agent**。
- 为 prompt 提供一个名称。
- 选择适当的 FM（本示例中选择 **Claude 3 Haiku**）。
- 在 **Enter a system prompt** 中，输入以下内容：

```
You are a Financial Complaints Assistant AI. You will receive complaint information from a knowledge base and questions about resolution timing.
When responding to resolution timing queries:
1. Use the provided complaint information to confirm if it was resolved within timeline
2. For timely resolutions, provide:
   - Confirmation of timely completion
   - Specific actions taken (from the provided complaint data)
   - Next steps that were completed
2. For delayed resolutions, provide:
   - Acknowledgment of delay
   - Standard compensation package:
     • $75 service credit
     • Priority Status upgrade for 6 months
     • Service fees waived for current billing cycle
   - Actions taken (from the provided complaint data)
   - Contact information for follow-up: Priority Line: ************** 
Always reference the specific complaint details provided in your input when discussing actions taken and resolution process.
```

- 选择 **Save**。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/5_Chat_Agent_image-5.png)

- agent 保存后，选择 **Deploy**。
- 在 **Alias name** 中输入 `demoAlias`。
- 选择 **Deploy**。

## 创建 flow

现在 prompt 与 agent 都已就绪，我们来创建一个 flow 来编排投诉处理流程：

- 在 SageMaker Unified Studio 中，在 **Build** 菜单下选择 **Machine Learning & Generative AI** 中的 **Flow**。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/6_flow_image-6.jpeg)

- 创建一个名为 demo-flow 的新 flow。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/7_new_flow_image-7.png)

### 为 flow 应用添加知识库

请完成以下步骤，为 flow 添加一个知识库节点：

- 在导航窗格中，在 **Nodes** 标签页上选择 **Knowledge Base**。
- 在 **Configure** 标签页上，提供以下信息：在 **Node name** 中输入名称（例如 `complaints_kb`）。选择 **Create new Knowledge Base**。
- 在 **Create Knowledge Base** 窗格中，输入以下信息：在 **Name** 中输入名称（例如 `complaints`）。在 **Description** 中输入描述（例如 `user complaints information`）。在 **Add data sources** 中选择 **Local file** 并上传 complaints.txt 文件。在 **Embeddings model** 中选择 **Titan Text Embeddings V2**。在 **Vector store** 中选择 **OpenSearch Serverless**。选择 **Create**。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/8_Knowledge_base_image-8.png)

- 创建知识库后，在 flow 中选择它。
- 在详细信息名称中，提供以下信息：
- 在 **Response generation model** 中，选择 **Claude 3 Haiku**。
- 把 flow 输入节点的输出连接到知识库节点的输入。
- 把知识库节点的输出连接到 flow 输出节点的输入。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/9_first_connection_image-9.png)

- 选择 **Save**。

### 为 flow 应用添加 prompt

现在我们把你先前创建的 prompt 添加到 flow 中：

- 在 **Flow app builder** 窗格的 **Nodes** 标签页上，添加一个 prompt 节点。
- 在 prompt 节点的 **Configure** 标签页上，提供以下信息：
- 在 **Node name** 中输入名称（例如 `demo_prompt`）。
- 在 **Prompt** 中选择 `financeAssistantPrompt`。
- 在 **Version** 中选择 **1**。
- 把知识库节点的输出连接到 prompt 节点的输入。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/10_KB_Prompt_connection_image-10.png)
- 选择 **Save**。

### 为 flow 应用添加条件

条件节点决定 flow 如何处理不同类型的查询。它会评估查询是关于处理时限，还是关于一般性投诉信息，使 flow 能够把查询适当地路由。当查询与处理时限相关时，它会被导向 chat agent 做专门处理；否则它会直接从知识库得到回答。请完成以下步骤添加条件：

- 在 **Flow app builder** 窗格的 **Nodes** 标签页上，添加一个条件节点。
- 在条件节点的 **Configure** 标签页上，提供以下信息：在 **Node name** 中输入名称（例如 `demo_condition`）。在 **Conditions** 下的 **Condition** 中输入 `conditionInput == "T"`。把 prompt 节点的输出连接到条件节点的输入。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/11_condition_connection_image-11.png)
- 选择 **Save**。

### 为 flow 应用添加 chat agent

现在把你先前创建的 chat agent 添加到 flow 中：

- 在 **Flow app builder** 窗格的 **Nodes** 标签页上，添加 agent 节点。
- 在 agent 节点的 **Configure** 标签页上，提供以下信息：在 **Node name** 中输入名称（例如 `demo_agent`）。在 **Chat agent** 中选择 `DemoAgent`。在 **Alias** 中选择 `demoAlias`。
- 创建以下节点连接：把条件节点（`demo_condition`）的输入连接到 prompt 节点（`demo_prompt`）的输出。连接条件节点的输出：把 **If condition is true** 设置为 agent 节点（`demo_agent`）。把 **If condition is false** 设置为已有的 flow 输出节点（`FlowOutputNode`）。把知识库节点（`complaints_kb`）的输出连接到以下节点的输入：agent 节点（`demo_agent`）；flow 输出节点（`FlowOutputNode`）。把 agent 节点（`demo_agent`）的输出连接到一个新的名为 `FlowOutputNode_2` 的 flow 输出节点。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/12_agent_connection_image-12.png)
- 选择 **Save**。

## 测试 flow 应用

flow 应用已就绪，我们来测试它。在页面右侧选择展开图标以打开 **Test** 窗格。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/13_fina_connection_image-13.png)

在 **Enter prompt** 文本框中，我们可以提出几个与先前创建的数据集相关的问题。以下截图展示了一些示例。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/14_question_image-14.png)

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/15_answer_image-15.png)

## 清理

要清理资源，请删除 flow、agent、prompt、知识库，以及相关的 OpenSearch Serverless 资源。

## 结论

本文演示了如何在 SageMaker Unified Studio 中使用 flow 应用构建一个 AI 驱动的投诉参考系统。借助 SageMaker Unified Studio 的集成能力，以及 Amazon Bedrock Knowledge Bases、Amazon Bedrock Agents 与 Amazon Bedrock Flows 等 Amazon Bedrock 特性，你无需大量编码即可快速开发和部署精密的 AI 应用。

在使用 SageMaker Unified Studio 构建 AI 工作流时，请记得在安全方面遵循 AWS 的[共享责任模型](https://aws.amazon.com/compliance/shared-responsibility-model/)。落实 SageMaker Unified Studio 的[安全](https://docs.aws.amazon.com/sagemaker-unified-studio/latest/adminguide/security.html)最佳实践，包括恰当的 IAM 配置与数据加密。你还可以参阅[用 OWASP Top 10 缓解措施保护生成式 AI 助手](https://aws.amazon.com/blogs/machine-learning/secure-a-generative-ai-assistant-with-owasp-top-10-mitigation/)，了解如何使用针对常见威胁的 OWASP TOP 10 缓解措施来评估生成式 AI 助手的安全态势。遵循这些指引有助于建立健壮的 AI 应用，保持数据完整性与系统防护。

想了解更多，请参阅 [SageMaker Unified Studio 中的 Amazon Bedrock](https://docs.aws.amazon.com/sagemaker-unified-studio/latest/userguide/bedrock.html)，并加入 [AWS Generative AI Community](https://community.aws/generative-ai?trk=4a84f0b4-a654-4729-9e51-6d6dc54134f2&sc_channel=el) 参与讨论、分享你的经验。

我们期待看到你用这些强大的新特性创造出创新的方案。

### 关于作者

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/sumeettr-100x133.jpg)**Sumeet Tripathi** 是 AWS 位于北卡罗来纳州的企业支持负责人（TAM）。他在技术领域拥有 17 年以上、跨越多种角色的经验。他热衷于帮助客户减少运营挑战与摩擦。他的重点领域是 AI/ML 以及能源与公用事业行业。工作之余，他喜欢与家人旅行、看板球比赛和电影。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/Vsnak-100x133.jpg)**Vishal Naik** 是 Amazon Web Services（AWS）的高级解决方案架构师。他是一名构建者，乐于帮助客户实现业务需求，并用 AWS 方案与最佳实践解决复杂挑战。他的核心关注领域包括生成式 AI 与机器学习。闲暇时，Vishal 喜欢拍摄以时间旅行和平行宇宙为主题的短片。
