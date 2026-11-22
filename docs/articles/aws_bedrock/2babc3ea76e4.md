---
vendor: aws_bedrock
title: Make agents a reality with Amazon Bedrock AgentCore: Now generally available
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-is-now-generally-available
date: 2025-10-13
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 3dc633dae844
---

# 用 Amazon Bedrock AgentCore 让 agent 成为现实：现已正式可用

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/10/img3.png)

## 让 agent 走出原型困境，以安全性、可扩展性和可靠性进入生产环境

2006 年我们推出 AWS 时，我们相信云计算将改变组织构建和扩展技术的方式。如今，在 AI agent 领域我们正处在类似的拐点。我们设想这样一个世界：数十亿 agent 协同工作，改变从日常运营到复杂业务流程的一切。然而，要让这一设想成为现实，需要的不仅仅是框架或低代码构建工具。企业愿意把业务押注其上的 agent，需要一套企业级运营基础——它安全、可靠、可扩展，并且专为 agent 的非确定性特性而设计。凭借我们构建关键任务系统的经验，[Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) 是一个全面的 agentic 平台，帮助组织满怀信心地走向生产。

## AgentCore：让 agent 快速进入生产

AgentCore 现已正式可用，让每位开发者都能快速把 agent 从试点推进到全面生产。AgentCore 为你提供构建、部署和运营 agent 所需的完整基础。你可以轻松为 agent 配备工具、记忆和数据，以处理复杂工作流。你可以用几行代码把 agent 部署到当今最安全、最具可扩展性的运行时之一。你还可以用企业部署所需的控制能力和访问管理来运营这些 agent。你可以完成这一切而无需任何基础设施管理，并且可以轻松使用你选择的任意模型或 agent 框架上手。

AgentCore SDK 已被来自多个行业、各种规模的客户下载超过一百万次。早期客户包括 Clearwater Analytics（CWAN）、Cox Automotive、Druva、Ericsson、Experian、Heroku、National Australia Bank、Sony、Thomson Reuters 等。在 Accenture、Cisco、Deloitte 和 Salesforce 等 AWS 合作伙伴的支持下，AgentCore 已经在带来变革性成果。

## AgentCore：一个全面的 agentic 平台

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/13/image-20-2.png)

构建 agent 可能很难——你需要弄清楚如何与身份提供方集成、如何构建记忆和可观测性，以及如何与工具集成。我们的 agentic 平台提供覆盖 agent 开发生命周期（从构建到部署再到运营）的全托管服务。你可以自由组合、混用，使用任意模型或框架，在获得企业级基础设施和工具的同时拥有最大灵活性。让我们来看它的核心能力。

**按你想要的方式构建：** agent 领域正在快速演进，新的框架、模型和协议几乎每周都在出现。你可以借助可组合的 AgentCore 服务按自己的方式构建，这些服务既可以一起使用，也可以单独使用。你的组织可以决定团队需要哪些 AgentCore 服务，同时继续使用偏好的框架（包括 CrewAI、Google ADK、LangGraph、LlamaIndex、OpenAI Agents SDK 和 Strands Agents）和模型（包括 Amazon Bedrock 上可用的模型，以及 Bedrock 之外可用的模型，如 OpenAI 和 Gemini），从而保持按自己方式构建的自由。

**助力 agent 成功的基础工具：** agent 通过具体动作创造价值——编写和执行代码、连接企业系统、浏览网页。AgentCore 提供这些必需的服务：AgentCore Code Interpreter 让 agent 能在隔离环境中安全地生成并执行代码，AgentCore Browser 允许 agent 大规模与 Web 应用交互。同时，AgentCore Gateway 把你现有的 API 和 AWS Lambda 函数转换为 agent 可用的工具，连接到现有的 MCP 服务器，并与关键第三方业务工具和服务（如 Jira、Asana 和 Zendesk）实现无缝集成。这个统一的访问入口使跨企业系统的安全集成成为可能。借助 AgentCore Identity，agent 可以使用 OAuth 标准完成恰当的身份验证和授权，从而安全地访问并操作这些工具。

**具备智能记忆的上下文感知 agent：** 要让 agent 真正有效，它们需要保持上下文并从长期交互中学习。设想一个销售支持 agent 帮助客户了解企业软件选型——它应当在多次对话中记住客户的行业、预算约束和技术要求，避免重复提问，并给出越来越个性化的建议。同样，在协助复杂的技术故障排查时，agent 应当回想起此前的调试尝试及其结果，从而提供更有针对性的解决方案。AgentCore Memory 帮助开发者打造这类精细的上下文感知体验，而无需管理复杂的记忆基础设施，帮助 agent 建立并维持对用户偏好、历史交互和相关上下文的细致理解，从而丰富每一次对话。

**面向可信 agent 的全面可观测性：** 由于 agent 会实时推理并以非确定性方式执行动作，你需要对 agent 的推理和动作有完整的可见性。在 [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/) 的支持下，AgentCore Observability 通过实时仪表盘和详细审计轨迹提供全面监控。组织可以追踪 agent 的每一个动作、快速调试问题并持续优化性能。通过与 OpenTelemetry（OTEL）兼容，AgentCore Observability 可与现有监控工具集成，例如 CloudWatch、Dynatrace、Datadog、Arize Phoenix、LangSmith 和 Langfuse。

**任意规模下行业领先的可靠性：** 与传统应用不同，agent 工作负载的持续时间本质上可能难以预测。AgentCore Runtime 正是为这种波动性而设计，可按需从零自动扩展到数千个会话，并为长时间运行的任务提供行业领先的八小时运行时。

**企业级 agent 安全：** agent 需要代表用户行事，同时安全地访问多个系统并处理敏感数据，因此健壮的安全与法规合规不容妥协。AgentCore 在每项服务中内嵌安全能力，帮助 agent 安全运行。它支持虚拟私有云（VPC）环境和 AWS PrivateLink，使网络流量保持私密与安全。最重要的是，AgentCore Runtime 通过 microVM 技术提供行业领先的安全性，为每个 agent 会话提供各自隔离的计算环境，防止数据泄漏并维护每一次交互的完整性。

**借助 AgentCore，速度、规模和安全性可以兼得：** AgentCore 通过其 MCP server 让你轻松构建生产就绪的 agent，该 server 可与 Kiro 或 Cursor AI 等集成开发环境（IDE）配合使用。上手只需几分钟，但这些并非简化版工具——它们是功能完整、生产就绪的解决方案，可以立即从零扩展到数千个会话，同时保持健壮的安全性。这意味着你的团队可以从想法快速走向部署，并确信你的 agent 构建在经受过验证的基础上。

## 让 AI agent 的承诺成为现实：客户故事

从 Cohere Health 受监管的医疗健康环境，到 Ericsson 的复杂技术系统，再到 Sony 的全球转型，这些先行组织展示了 AgentCore 如何推动跨行业的下一波 AI 创新。在 AI 时代取得成功的组织，不会是最完美预测未来的那些，而是建立在经过验证的基础上、同时保持演进灵活性的那些。当你构建在 AgentCore 之上时，你得到的不只是用于部署和运营 agent 的专门服务，还得到一位拥有近二十年经验、帮助企业在全球规模上安全转型的伙伴。以下是一些展示客户成效的故事：

看看全球最大广告公司 Publicis Groupe 旗下的 Epsilon 如何使用 AgentCore 为大型品牌革新营销活动个性化。他们的 Intelligent Campaign Automation 解决方案可实现自动化营销活动设计、受众定向以及跨多个渠道的实时优化——在大规模下带来更快的执行速度和更高的客户定向精度。

### 用智能工作流自动化变革制造业

Amazon Devices Operations & Supply Chain 团队正在使用 AgentCore 开发一种 agentic 制造方法。作为这一新方法的一部分，AI agent 利用产品规格协同工作，自动化原本由人工完成的流程。一个 agent 读取产品需求并为质量控制创建详细的测试流程，另一个 agent 则训练制造线上机器人所需的视觉系统。结果是，过去需要数天工程时间的目标检测模型微调，现在不到一小时就能以高精度完成。这个概念验证只是他们更智能的制造愿景的开端——在这一愿景中，AI agent 将简化从最初产品需求到最终生产的整个流程。

### 用 agent 加速医疗健康决策

在医疗健康领域，每一分钟都很重要。Cohere Health® 是一家临床智能公司，专注于加强支付方与提供方之间的协作，并提升就医前后临床决策的速度和准确性。该公司经过临床训练的 AI 有助于加快患者获得医疗照护、改善患者预后、减轻提供方的行政负担，并改善整个照护连续过程中的医疗健康经济效益。

借助 AgentCore，Cohere Health 打造了 Cohere Review Resolve™，这是一款 AI 驱动的 copilot，可优化医保计划医疗必要性审核的准确性和效率。Cohere Review Resolve™ 会分析结构化和非结构化数据——例如临床记录、患者笔记和传真——快速识别并呈现证据，以验证所申请治疗方案的医疗必要性。该 copilot 将为医保计划的审核人员提供事先授权请求的完整临床上下文，并智能地回应审核人员的查询。

Cohere Health 选择 AgentCore，是因为他们需要在高度监管的医疗健康环境中首次生产部署 agentic AI，因而需要企业级基础设施。AgentCore 提供的全面审计轨迹、延长的会话支持，以及在复杂多小时的 workflow 中保持历史记录的能力，对他们的医疗健康用例至关重要。

Cohere Health 预计 Review Resolve™ 将把审核时间缩短 30-40%，帮助他们满足关键且被强制要求的周转时限。对患者而言，更快的决策将加快获得照护、提高治疗依从性、改善预后并降低成本。Review Resolve™ 还在其现有 90% 自动化率的基础上进一步提升，同时帮助医保计划进一步提高临床判定的准确性，从而改善医疗费用节省和患者预后。

### 电信行业的 agent：简化复杂系统

全球电信技术领导者 Ericsson 使用 AgentCore 解决了其在部署 agent 时的主要挑战。Ericsson 业务领域网络部 AI 与新兴技术负责人 Dag Lindbo 表示：“在 Ericsson，我们的 3G/4G/5G/6G 系统横跨数千个互连子系统、数百万行代码，代表着在全国级关键基础设施规模上数十年的工程创新。AgentCore 支撑着我们对数据与信息的关键融合，在真实研发中交付能力空前的 AI agent，让数万名员工实现两位数的效率提升。AgentCore 还让我们能够使用任意 agent 框架，这对我们在众多团队和用例之间扩展至关重要。”

### 娱乐行业的 agent：实现安全性、可观测性和可扩展性

在全球领先的技术与娱乐公司 Sony Group，AgentCore 已经在产生影响。Sony Group Corporation 数字与技术平台 AI 加速部高级总经理 Masahiro Oba 表示：“Agentic AI 能带来更高水平的先进运营效率和精细化程度，是我们 AI 转型旅程中不可或缺的技术。不过，它也确实带来了许多技术挑战。借助 Amazon Bedrock AgentCore，我们构建了集团级的 Agentic AI 平台，实现了企业级的安全性、可观测性和可扩展性，以及与 AI 资源的无缝跨平台连接——这对我们来说是一项关键能力。把 Amazon Bedrock AgentCore 放在我们 agentic AI 生态系统的核心，我们获得了治理和共享海量 AI 资源的能力，使我们能够以信心和安全性加速 AI 转型。”

## 在 AWS 为 AI agent 时代奠定基础

AgentCore 现已在九个 AWS 区域正式可用，以支持全球部署需求，包括亚太地区（孟买）、亚太地区（新加坡）、亚太地区（悉尼）、亚太地区（东京）、欧洲地区（都柏林）、欧洲地区（法兰克福）、美国东部（弗吉尼亚北部）、美国东部（俄亥俄）和美国西部（俄勒冈）。组织可以通过 [AWS Marketplace](https://aws.amazon.com/marketplace/solutions/ai-agents-and-tools?trk=70405219-a2f8-4816-a915-9932f523f1bd&sc_channel=el) 提供的、专为在 AgentCore 上运行而设计的预构建 agent 和工具，加快实现价值的时间。

立即开始使用 AgentCore——访问 [aws.amazon.com/bedrock/agentcore/](https://aws.amazon.com/bedrock/agentcore/) 开启你的 agentic 未来！

**了解更多：**

- [使用 Amazon Bedrock AgentCore MCP server 加速开发](https://aws.amazon.com/blogs/machine-learning/accelerate-development-with-the-amazon-bedrock-agentcore-mcpserver/)（Shreyas Subramanian 和 Primo Mu，AWS ML Blog，10/02/2025）
- [推出 Amazon Bedrock AgentCore：安全地部署和运营任意规模的 AI agent（预览）](https://aws.amazon.com/blogs/aws/introducing-amazon-bedrock-agentcore-securely-deploy-and-operate-ai-agents-at-any-scale/)（Danilo Poccia，AWS News Blog，7/16/2025）
- [AWS 在 2025 年纽约 AWS Summit 上发布用于构建 AI agent 的新创新](https://www.aboutamazon.com/news/aws/aws-summit-agentic-ai-innovations-2025)（Amazon 新闻摘要，7/16/2025）

### 关于作者

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2022/10/31/swami.png)Swami Sivasubramanian** 是 Amazon Web Services（AWS）负责 Agentic AI 的副总裁。在 AWS，Swami 主导了 Amazon DynamoDB、Amazon SageMaker、Amazon Bedrock 和 Amazon Q 等领先 AI 服务的开发与成长。他团队的使命是提供客户和合作伙伴所需的大规模、灵活性和价值，使其能够满怀信心地使用 agentic AI 进行创新，并构建不仅强大高效、而且可信负责的 agent。Swami 还在 2022 年 5 月至 2025 年 5 月期间担任美国国家人工智能咨询委员会（National Artificial Intelligence Advisory Committee）成员，该委员会负责就国家 AI 计划相关议题向美国总统和国家 AI 计划办公室提供建议。
