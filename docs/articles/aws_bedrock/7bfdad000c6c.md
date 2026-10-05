---
vendor: aws_bedrock
title: 用 Agentforce 和 AWS 扩展公共部门智能
original_title: Extending public sector intelligence with Agentforce and AWS
url: https://aws.amazon.com/blogs/machine-learning/extending-public-sector-intelligence-with-agentforce-and-aws
date: 2026-09-22
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

公共部门机构处理大量非结构化证据，如随身摄像机画面、监控视频和扫描文档，这些都需要先提取洞察，任何人才能对其采取行动。本文演示如何把 [Amazon Bedrock Data Automation](https://aws.amazon.com/bedrock/bda/) 与 Model Context Protocol (MCP) 结合，把非结构化数据转成结构化洞察。然后你可以在一个 AI 智能体（如 [Salesforce Agentforce](https://www.salesforce.com/agentforce/)）中通过自然语言查询暴露这些洞察。

在我们上一篇文章 [Modernizing evidence management in Salesforce Public Sector Solutions with Amazon S3](https://aws.amazon.com/blogs/publicsector/modernizing-evidence-management-in-salesforce-public-sector-solutions-with-amazon-s3/) 中，我们把 [Agentforce Public Sector](https://www.salesforce.com/government/solutions/)（前身为 Public Sector Solutions）借助 Amazon Simple Storage Service (Amazon S3) 的文件外部存储集合作为一个示例实现。有了那个基础，你现在拥有了为随身摄像机画面、监控视频、照片、音频录音和扫描文档做持久、经济的存储。

然而，存储只是挑战的一半。没有自动化，你会花大量时间人工审阅、分类并从这些文件中提取相关细节，然后才能对其采取行动。借助这一集成，Agentforce 用户可以搜索存储在 AWS 上的已处理数据、从非结构化数据中呈现关键洞察，并执行更高级的动作，全部无需离开 Salesforce 控制台。

## 方案概览

两条主要流程协同把原始证据转成可行动的调查洞察。第一条流程用 [External Storage of Files with Amazon S3 for Public Sector](https://help.salesforce.com/s/articleView?id=ind.psc_external_file_storage_amazons3.htm&language=en_US&type=5) 连接器把非结构化媒体文件和文档移入 Amazon S3。图 1 说明 Amazon S3 如何提供企业级规模的存储基础设施，用于存储大文档和媒体文件。

图 1：Agentforce Public Sector 与 Amazon S3 集成

其次，在数据进入 Amazon S3 后，一个事件驱动架构用 Amazon Bedrock Data Automation 异步处理多模态数据。图 2 展示你如何扩展这个存储方案以创建一个架构模式。该模式把非结构化数据转化为可行动的洞察，并通过 MCP 让它们对 Salesforce Agentforce 可用。

图 2：从非结构化数据生成洞察

如图 2 所示，当一个文件或文档落到 Amazon S3，一个 S3 事件通知会调用一个 AWS Lambda 函数。该 Lambda 函数生成一个文档 ID、把它连同文档元数据存进 Amazon DynamoDB，并启动一个 Amazon Bedrock Data Automation 作业来处理该文件。Amazon Bedrock Data Automation 基于媒体类型提取结构化洞察。当作业完成时，一个 Amazon EventBridge 规则触发第二个 Lambda 函数，把结果保存进 Amazon S3 中一个专用的输出桶。

在 Salesforce 侧，用户在 Agentforce 中的一次聊天触发一个已配置的动作，通过 MCP 调用 AWS。该调用经 Amazon Bedrock AgentCore Gateway（Amazon Bedrock AgentCore 的一项能力）路由，它认证请求并调用一个运行在 AWS Lambda 上的 MCP server。Amazon Bedrock AgentCore 是以任意框架或模型大规模构建、连接并优化智能体的平台。

Lambda 函数首先查询 DynamoDB 表以定位相关结果，然后从 Amazon S3 取回并返回它们。结果经 AgentCore Gateway 返回到 Agentforce，在那里数据被加载进智能体的上下文以做自然语言响应。

借助 Amazon Bedrock Data Automation，你可以基于媒体类型处理每个文件。对文档，它提取文本、识别关键字段并生成结构化摘要。对图像，它生成描述并识别画面中的物体或文字。对视频和音频文件，它生成转录和场景级摘要。Amazon Bedrock Data Automation 项目配置定义了对每种文件类型应用哪些提取能力，你可以在部署后在 Amazon Bedrock Data Automation 控制台中自定义这些设置。

这一处理在幕后进行。Salesforce 用户完全可以只在 Salesforce 控制台里上传文件、提问并收到 AI 驱动的洞察，无需在系统间切换或直接管理 AWS 资源。

该架构刻意做成模块化和可扩展的，被设计为一个你可以远超证据管理加以适配的模式。从处理流水线到查询路径，每个组件独立运作，都可以为你机构独特的需求定制。例如，你可以在 AWS Lambda MCP Serverless Runtime 中添加自定义处理逻辑，或在 Amazon DynamoDB 中存储额外元数据以做更丰富的文档查找。你也可以通过 MCP 连接不同的智能体前端而无需改动底层数据流水线。

## 技术实现指南

本节逐步讲解部署 AWS 基础设施并配置 Salesforce Agentforce 连接到 MCP 端点。

### 前提条件

开始前，完成上一篇文章 [Modernizing evidence management in Salesforce Public Sector Solutions with Amazon S3](https://aws.amazon.com/blogs/publicsector/modernizing-evidence-management-in-salesforce-public-sector-solutions-with-amazon-s3/) 中概述的步骤，因为本文直接在那个基础上构建。此外，确认你的 Salesforce org 支持通过 Agentforce Registry 注册并调用外部 MCP server。你可以通过导航到 **Setup > API Catalog > MCP Server** 并确认有注册 MCP server 的选项来验证这一点。注册外部 MCP server 在 Developer、Enterprise、Performance 和 Unlimited 版本中可用（见 [Manage External MCP Servers](https://help.salesforce.com/s/articleView?id=platform.api_catalog_manage_manual_external_mcp_servers.htm&type=5)）。

### 部署 AWS Cloud Development Kit (AWS CDK) 栈

这个 [GitHub 仓库](https://github.com/aws-samples/sample-extending-public-sector-intelligence-with-Agentforce-and-AWS) 提供了创建一个事件驱动架构所需 AWS 资源的部署。该方案部署一套无服务器基础设施，包括 Amazon EventBridge 规则、Amazon Bedrock Data Automation 配置、AWS Lambda 函数、Amazon DynamoDB 表和 Amazon Bedrock AgentCore Gateway。这段示例代码用于演示该模式，并非生产就绪，因此在用于生产前请审阅并加固它以满足你组织的要求。

部署 AWS CDK 栈后，配置 Salesforce Agentforce 连接到 Amazon Bedrock AgentCore Gateway MCP 端点。Agentforce 用 MCP Streamable HTTP 传输连接到 AgentCore Gateway。有了这个连接，Agentforce 可以发现并调用网关暴露的证据检索工具。AWS CDK 栈输出几个你配置 Salesforce 与 AWS 之间连接所需的值。在继续前从 AWS Management Console 取回它们。

可选地，在配置 Salesforce 连接之前，你可以用 [MCP Inspector](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-using-inspector.html) 验证你的网关端点——它是一个通过交互式界面测试和调试 MCP server 的开发者工具。这一步不是必需的，但可以在与 Agentforce 集成前帮助确认你的 AgentCore Gateway 正确响应。

#### 步骤 1：获取 AWS CloudFormation 输出

当 Intelligent Media Processing 方案完全部署后，设置 MCP 连接所需的输出在 AWS CloudFormation 的 `McpGatewayStack` 输出下可用。如图 3 所示，主要输出是 `CognitoClientId`、`CognitoTokenEndpoint` 和 `GatewayMcpEndpoint`。

图 3：AWS CloudFormation 输出

Agentforce 通过 Amazon Cognito 向 AWS 认证。你需要来自你 Cognito 应用客户端的 client secret，以在 Salesforce 中完成 MCP server 注册。

#### 步骤 2：获取 client secret

- 在 AWS Management Console 打开 Amazon Cognito。
- 在 **User Pools** 中，选择由 AWS CloudFormation 模板创建的 User pool 名称。
- 选择对应该用户池的应用客户端。

图 4 展示 Amazon Cognito 应用客户端页面，你可以在那里找到 Client secret。

图 4：Amazon Cognito client secret

### 把 Agentforce 连接到 MCP 端点

拿到 AWS 凭证后，你现在可以在 Salesforce 中注册 MCP server。这建立了一条经认证的链路，让 Agentforce 能调用 AWS 工具。

#### 步骤 3：创建 MCP 连接

- 在 Salesforce Setup 控制台，打开 Quick Find 并搜索 **API Catalog**，然后选择 **MCP Server**（见 [Manage External MCP Servers](https://help.salesforce.com/s/articleView?id=platform.api_catalog_manage_manual_external_mcp_servers.htm&type=5)）。
- 选择 **New**。然后选择 **Register MCP Server** 创建一个连接。
- 把 MCP server 命名为 `AwsBdaResultsMcp`，并把描述设为 `MCP server for accessing results from Amazon Bedrock Data Automation`。
- 取你在步骤 1 和 2 从 AWS 收集的各值，输入到对应字段，如图 5 所示，然后选择 **Create and Continue**。

图 5：MCP Server 创建连接

- 按提示操作。当你到达 MCP Server Allowlist 时，选择一个或多个你想用、且随 AWS CDK 一起部署的可用工具。在生产中，把允许清单限定到你的智能体仅需要的工具。见安全考量一节。
- 选择 **Save**。

你已成功把 Amazon Bedrock AgentCore MCP server 连接到 Salesforce Agentforce。

### 配置 Agentforce 使用 MCP

现在 MCP server 已注册，你可以把 MCP 工具加入一个现有 Agentforce 子智能体，或创建一个新子智能体。下面步骤演练创建一个专用的 Agentforce 子智能体，其主要任务是处理与证据检索相关的请求。该子智能体使用 MCP 工具查询存储在 AWS 中已处理的证据，并以自然语言把洞察返回给用户。

#### 步骤 4：把 MCP 工具动作加入你的 Agentforce 智能体

要集成一个外部 MCP server，请使用新的 Agentforce Builder。下面步骤使用 Employee Agent 模板。你可以把这一同样的 MCP 集成应用到其他智能体类型（如 Service Agent 或 Customer Agent），尽管确切的导航和配置选项可能不同。如果你有一个用旧版 Agentforce Builder 构建的智能体，请按此指南 [升级到新 Builder](https://help.salesforce.com/s/articleView?id=ai.agent_setup_create_upgrade.htm&type=5)。

- 从 App Launcher 打开 Agentforce Studio，然后选择 **New Agent**。从可用模板中选择 **Agentforce Employee Agent**，然后把它命名为 `Case Agent` 或一个与你用例相关的名称。
- 在 **Agentforce Builder** 中创建一个新子智能体。输入 `Media Processor` 作为名称，并把下面这段作为描述：
`Subagent that handles all questions related to files, documents, photos, images, videos, or audio attached to the current case. Retrieves AI-generated insights from processed media and responds in natural language.`

- 选择 **Save**。
- 在 **Media Processor** 子智能体中，在 **Actions Available for Reasoning** 部分下选择 **Add action**，然后选择 **Add from Asset Library**。搜索你注册的 MCP 工具（搜索 `AwsBdaResultsMcp` 会把结果缩小到相关工具）。图 6 展示在 **Actions Available for Reasoning** 部分下选中的已连接 MCP。

图 6：让 MCP 对智能体动作可用

- 在 **Reasoning Instructions** 下，给子智能体提供该做什么、如何回复的指令。使用以下推理指令模板：
`Handle all questions about files, documents, photos, images, videos, or audio attached to the current case. Run <MCP_PLACEHOLDER> to retrieve processed insights. If no insights are available, inform the user the attachment has not yet been processed. Don't fabricate content about unprocessed files.`

- 在 `<MCP_PLACEHOLDER>` 处，输入 `@` 以内联引用一个资源，然后选择与该子智能体关联的 MCP。图 7 展示在 Reasoning Instructions 中内联引用的 MCP。

图 7：把 MCP 加入子智能体

- 配置完成后，选择 **Save** 以预览智能体。

#### 步骤 5：测试并验证 MCP 集成

借助 Agentforce Builder，你可以预览智能体以及它在聊天中如何响应问题。要模拟一名员工在 Salesforce 控制台中提问的条件，你可以修改 **Context Variables**。这些变量代表当用户在 Salesforce 控制台工作时会被赋给智能体上下文的值。图 8 展示 Agentforce Builder 中 Preview 面板的 Context Variables。

要测试智能体，把 `currentRecordId` 上下文变量设为你想测试的案件的 Record ID（唯一的 18 字符 ID）。然后选择 **Apply and Restart Session**。本示例使用 **Agentforce Employee Agent**。其他智能体类型可能预配置了不同的上下文变量，因此相应调整。

图 8：预览上下文变量

要测试智能体的配置并验证它能否向 AWS 发出一次 MCP 调用，执行以下操作：

- 在把 Context Variables 设为模拟一个已上传媒体文件到 Amazon S3 并通过这一集成处理过的案件后，打开 Preview。输入一个能触发步骤 4 中配置的子智能体的 prompt，例如 `Summarize the files for this case`。
- 当智能体返回与案件记录关联每一项的摘要时，测试成功，如图 9 所示。

图 9：预览输出

- 要查看 Agentforce 智能体如何产生这一输出，审阅 **Summary** 输出。它们提供 trace 的一段自然语言摘要，解释智能体为处理请求所采取的步骤（见图 10）。

图 10：动作摘要

- 如果需要对 prompt 做任何改动以得到期望输出，请在 Agentforce Builder 中修改 prompt 并选择 **Save**，然后在 Preview 中再测试一次。
- 当你对输出满意后，你可以把这个智能体或子智能体部署到你组织使用的智能体界面中。

## 把这一模式扩展到你自己的用例

本文演示的架构不限于证据管理。你可以应用同样的模块化模式，为涉及处理非结构化数据的工作流（如许可证、福利理赔或合规审查）构建方案。关键组件有以下几个：

- 用于存储的 Amazon S3。
- 用于处理的 Amazon Bedrock Data Automation。
- 用于基于 MCP 的工具暴露的 Amazon Bedrock AgentCore Gateway。
- 用于自然语言交互的 Salesforce Agentforce。

这些中的每一个都可以为涉及非结构化数据的用例重新组合并扩展。因为每个组件独立运作，你可以替换处理引擎以匹配你机构的要求，同时保留同样的摄入和 MCP 查询层。对于许可证、福利理赔或税表这类文档密集型工作流，你可以替换 [GenAI Intelligent Document Processing (IDP) Accelerator](https://aws.amazon.com/blogs/machine-learning/accelerate-intelligent-document-processing-with-generative-ai-on-aws/) 作为另一种处理引擎。这保留同样的 Amazon S3 摄入和 MCP 查询路径。此外，因为 MCP server 建立在开放标准上，你只需构建一次。兼容 MCP 的智能体或系统可以连接到同一个端点，因此你可以在 Agentforce 之外多个应用间复用同一查询层。

无论你选择哪种处理方法，MCP 查询路径保持不变。AgentCore Gateway 把你处理过的数据作为兼容 MCP 的智能体可以发现并调用的工具暴露出来。这意味着，在多数情况下，该架构支持从一个用例起步并扩展到额外工作流，而无需重新设计 AWS 与 Salesforce 之间的集成。

## 安全考量

因为这一方案通过一个 MCP server 把 AI 智能体连接到你的数据，在你超越概念验证之前，请对照你组织的要求审视其安全态势。在 [AWS 责任共担模型](https://aws.amazon.com/compliance/shared-responsibility-model/) 下，AWS 保障底层基础设施安全，你保障自己的实现。作为一个起点，考虑哪些用户可以访问智能体，以及它能调用哪些工具和动作。还要记住，智能体处理的内容（如从证据中提取的文本）可能含有隐藏指令，诱使智能体采取非预期动作。这一风险称为间接 prompt 注入。要缓解这一风险，把所有从证据中提取的内容当作不可信数据处理，永远不要当作对智能体的指令。在取回的内容进入智能体上下文之前对其施加输入校验。用 MCP 允许清单把智能体可用的动作限定到最低必要的范围。用 Amazon Bedrock Guardrails 过滤或拒绝那些试图覆盖智能体行为的内容。要获取关于大语言模型（LLM）特有威胁的更广泛框架，参见 [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)。

这一方案处理公共部门证据，因此在生产前应用负责任的 AI 控制。Amazon Bedrock Guardrails 可以过滤有害内容并脱敏敏感信息，如可识别个人身份信息（PII）。它还能运行接地检查，确认响应接地位于取回的证据而非捏造。这些是例子，不是完整清单。关于保护智能体和 MCP 工具访问的权威指导，参见 [Security for agentic AI on AWS](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-security/introduction.html)、[Amazon Bedrock AgentCore 最佳实践](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/best-practices.html)，并以最小权限控制应用 [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)。

另需注意，随附的示例代码意在演示这一模式，并非生产就绪。请在部署到生产前审阅并加固它以满足你组织的要求。

## 清理

为避免持续产生费用，实验结束后清理你的资源。关于移除所有已部署资源的逐步命令，见 [GitHub 仓库](https://github.com/aws-samples/sample-extending-public-sector-intelligence-with-Agentforce-and-AWS#clean-up-the-cdk-stacks)。

你还必须手动删除 Salesforce 中的 Agentforce MCP 连接。

因为这是一个事件驱动的无服务器架构，你只为所使用的部分付费。处理成本只在证据被主动上传和分析时产生。Amazon S3 和 Amazon DynamoDB 存储成本基于所存储的数据量，没有最低承诺或预付费用。详情参见所用各服务的定价页面。

## 结论

本文演示了如何把 Amazon Bedrock Data Automation 与 Model Context Protocol 结合，处理非结构化证据并在 Salesforce Agentforce 中直接呈现结构化洞察。借助 Amazon Bedrock Data Automation，该架构自动从文档提取文本、从图像生成描述，并从视频和音频文件产出转录。

这一模式远超证据管理，延伸到涉及非结构化多模态数据的公共部门工作流。关于把这一架构适配到你机构特定需求的指导，参见本文前面的*把这一模式扩展到你自己的用例*一节。

完整示例代码可在 [GitHub 仓库](https://github.com/aws-samples/sample-extending-public-sector-intelligence-with-Agentforce-and-AWS)获取。你也可以探索用额外的 Amazon Bedrock Data Automation 输出类型来扩展该方案。另一个选项是集成 Amazon Bedrock Knowledge Bases——那个用于检索增强生成（RAG）的完全托管能力——以支持跨大型证据集合的基于 RAG 的问答。
