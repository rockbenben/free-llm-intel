---
vendor: aws_bedrock
title: Building health care agents using Amazon Bedrock AgentCore
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/building-health-care-agents-using-amazon-bedrock-agentcore
date: 2025-09-26
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 59d7011c2864
---

# 使用 Amazon Bedrock AgentCore 构建医疗保健 agent

*本文与 Innovaccer 的 AI 平台负责人 Kuldeep Singh 共同撰写。*

agentic AI 的引入正在医疗保健领域开启一个变革性的时代，标志着与传统 AI 系统的显著分野。agentic AI 在复杂的医疗环境中展现出自主决策能力与自适应学习能力，使其能够监测患者进展、协调照护团队，并实时调整治疗策略。这些智能系统正日益深入地嵌入医疗保健运营之中：从借助高级模式识别提升诊断精度，到优化临床工作流、加速药物发现进程。agentic AI 将主动的问题解决能力与实时适应能力结合起来，使医疗保健专业人员可以专注于高价值、以患者为中心的工作，而由 AI 处理常规任务与复杂的数据分析。

Innovaccer 是一家开创性的医疗保健 AI 公司，最近推出了 [Innovaccer Gravity™](https://innovaccer.com/resources/news/innovaccer-launches-gravity-healthcare-intelligence-platform-accelerate-ai-driven-transformation)，该平台使用 [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore) 构建，是一个全新的医疗保健智能平台，旨在彻底变革数据集成与 AI 驱动的医疗保健转型。凭借其令人瞩目的过往业绩——其现有解决方案服务于 1,600 多个美国照护场所、管理超过 8,000 万份统一的健康记录，并已创造 15 亿美元的成本节约——这充分体现了 AWS 客户如何通过打造变革医疗保健服务、同时带来显著投资回报（ROI）的智能解决方案，引领 agentic AI 的演进。

医疗保健要求精准与可问责。在这一领域运行的 AI agent 必须安全地处理敏感的患者数据、遵守严格的合规法规（如 [HIPAA](https://www.cdc.gov/phlp/php/resources/health-insurance-portability-and-accountability-act-of-1996-hipaa.html)），并在多样的临床工作流之间保持一致的可互操作性。面对复杂的医疗保健系统与患者数据保护要求，标准的通用协议显得不足。医疗保健机构需要一个健壮的服务，把现有 API 转换为与 [Model Context Protocol (MCP) ](https://modelcontextprotocol.io/docs/getting-started/intro)兼容的工具，这些工具能够有效扩展规模，同时提供内置的身份认证、授权、加密与全面的审计跟踪。[Amazon Bedrock AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html) 为医疗保健服务提供方与数字健康公司提供了一种简单而安全的方式，用于大规模构建、部署、发现和连接工具，从而在维持最高安全与合规标准的同时创建 AI 驱动的医疗保健解决方案。

## 问题

医疗保健机构面临着严重的数据孤岛挑战，原因是不同系统间的电子健康记录（EHR）格式各异，而且往往要维护多个系统来满足特定科室需求和遗留系统。FHIR（Fast Healthcare Interoperability Resources）通过将医疗保健数据标准化为可交换的*资源*（resource，如患者记录和化验结果）来解决这些互操作性挑战，在不同系统之间实现无缝通信，同时保持安全性并改善照护协调。然而，实施 FHIR 也带来其自身的挑战，包括与遗留系统集成的技术复杂性，以及在医疗信息学和 API 开发方面需要专门的专业知识。

AI agent 的实施引入了新的复杂性层次，需要谨慎设计和维护与现有系统的接口。AI agent 需要以安全的方式访问 FHIR 数据和其他医疗保健工具，并具备（入站与出站的）身份认证和端到端加密。MCP 是一个标准化的通信框架，使 AI 系统能够通过统一接口与外部工具、数据源和服务无缝交互。然而，MCP server 的开发与扩展需要大量资源和专业知识。托管这些服务需要持续的开发投入和关注，以维持最佳性能与可靠性。当医疗保健机构穿行于这片复杂地形时，解决这些挑战对于实现真正的互操作性、释放现代医疗保健技术的全部潜力至关重要。

## 使用 Amazon Bedrock AgentCore 大规模部署、增强和监控 AI agent

通过使用 Amazon Bedrock AgentCore，你可以安全地大规模部署和运维能力出众的 AI agent。它提供专为动态 agent 工作负载打造的基础设施、用于增强 agent 的强大工具，以及面向真实世界部署的必要控制能力。Bedrock AgentCore 提供一组可组合的服务，本文方案中最相关的服务列于下方。更多信息请参阅 [Bedrock AgentCore 文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)。

- [AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html) 提供一个安全的无服务器运行时，专为使用任意开源框架、协议和模型来部署和扩展动态 AI agent 与工具而打造。Runtime 为 agentic 工作负载而构建，具备行业领先的扩展运行时间支持、快速冷启动、真正的会话隔离、内置身份，以及对多模态负载的支持。
- [AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html) 为 agent 发现和使用工具提供安全途径，并能将 API、[AWS Lambda](https://aws.amazon.com/lambda) 函数和现有服务直接转换为 agent 兼容的工具。Gateway 加速定制代码开发、基础设施预置和安全实现，让开发者可以专注于构建创新的 agent 应用。
- [AgentCore Identity](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity.html) 提供安全、可扩展的 agent 身份与访问管理能力，加速 AI agent 开发。它与现有身份提供程序兼容，无需迁移用途或重建认证流程。
- [AgentCore Observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html) 通过统一的可运营仪表板，帮助开发者追踪、调试和监控生产环境中的 agent 性能。它支持与 OpenTelemetry 兼容的遥测，并对 agent 工作流的每一步提供详细的可视化。

在本方案中，我们演示了用户（一位家长）如何以对话方式与 Strands 或 LangGraph agent 交互，获取孩子免疫接种历史与接种计划的信息、查询可用时段并预约。稍作改动后，AI agent 可以变为事件驱动，从而自动发送提醒、预约等。这减轻了医疗保健机构和家长的行政负担——家长不再需要追踪纸质材料，也不必多次致电预约。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/18/ML-19648-Arch.png)

如上图所示，使用 Amazon Bedrock AgentCore 构建的医疗保健预约工作流如下：

- **用户与 Strands 或 LangGraph agent 交互：**该方案同时包含 [Strands](https://strandsagents.com/) 和 [LangGraph](https://www.langchain.com/langgraph) 两种 agent。你也可以使用 AutoGen 和 CrewAI 等其他框架。
- **来自 Amazon Bedrock 的推理 LLM：**使用 Amazon Bedrock 中的 Claude 3.5 Sonnet 大语言模型（LLM）。该模型通过把握细微差别和复杂指令展现出高级推理能力，并具备强大的工具调用能力，使其能够有效集成外部应用与服务，自动完成网页浏览、计算或数据交互等各类任务。
- **通过 AgentCore Gateway 暴露工具：**AgentCore Gateway 使用标准 MCP client 为 Strands 或 LangGraph agent 提供对所需工具的安全访问。在本方案中，REST API 托管在 [Amazon API Gateway](https://aws.amazon.com/gateway) 上，并通过 AgentCore Gateway 以 MCP 工具形式暴露。
- **AgentCore Gateway 的入口认证：**AgentCore Gateway 使用 oAuth 2.0 加以保护，以 [Amazon Cognito](https://aws.amazon.com/cognito) 作为身份提供程序。你可以按需使用 Auth0、Keycloak 等其他兼容 oAuth 2.0 的身份提供程序来适配你的用例。
- **使用 AgentCore Gateway 将 OpenAPI 规范转换为工具：**Amazon API Gateway 被用作后端来暴露 API。通过导入 OpenAPI 规范，AgentCore Gateway 无需额外的工具元数据配置即可提供兼容 MCP 的 server。以下是本方案中使用的工具。`get_patient_emr()`：获取家长与孩子的人口统计信息。`search_immunization_emr()` – 获取孩子的免疫接种历史与计划。`get_available_slots()` – 获取家长首选日期附近儿科医生的排班。`book_appointment()` – 预约并返回确认编号。
- **以 AWS HealthLake 作为 FHIR server：**[HealthLake](https://aws.amazon.com/healthlake/) 用于管理人口统计信息、免疫接种历史、排班与预约等患者数据。HealthLake 是一项符合 HIPAA 资格的服务，通过基于 FHIR API 的事务，为医疗保健公司提供个人与患者群体健康数据的完整视图，以 PB 级规模安全地存储数据并转换为可查询的格式，并进一步使用机器学习（ML）模型分析这些数据。
- **从 AgentCore Gateway 到工具的出口认证：**使用 oAuth 2.0 并以 Amazon Cognito 作为身份提供程序，来完成 AgentCore Gateway 与本方案所用工具之间的认证。

## 解决方案搭建

| **重要：**以下代码示例仅用于学习和演示目的。在生产环境实现时，建议补充必需的错误处理、输入校验、日志记录和安全控制。 |
| --- |

搭建和清理此示例方案的代码与说明可在 [GitHub](https://github.com/awslabs/amazon-bedrock-agentcore-samples/tree/main/02-use-cases/healthcare-appointment-agent) 上获取。搭建完成后，该方案如下所示，面向家长用于与免疫接种相关的预约。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/18/ML-19648-Demo.gif)

## 定制解决方案

该方案可以通过以下机制进行定制，以扩展相同或不同的用例：

- **OpenAPI 规范：**该方案使用一份示例 OpenAPI 规范（名为 `fhir-openapi-spec.yaml`），其中的 API 托管在 API Gateway 上。可以通过编辑 YAML 文件来定制 OpenAPI 规范，以增加更多工具或改用完全不同的工具。对 OpenAPI 规范做出更改后，必须重新创建 AgentCore gateway。
- **Agent 指令与 LLM：**可以修改 `strands_agent.py` 或 `langgraph_agent.py`，以更改 Agent 的目标或指令，或改用其他 LLM。

## 未来增强

我们已经在展望并规划该方案的未来增强。

- **AgentCore Runtime：**在 AgentCore Runtime 上托管 strands 或 LangGraph agent。
- **AgentCore Memory：**使用 AgentCore Memory 在短期（会话内）和长期（跨会话）保留会话信息，为 agent 用户提供更个性化的体验。

## Innovaccer 对 Bedrock AgentCore 的使用场景

Innovaccer 的 gravity 平台包含 400 多个连接器，用于统一来自 Epic、Oracle Cerner 和 MEDITECH 等来源的 EHR 数据，还包含 20 多个预训练模型、15 个预构建 AI agent、100 个 FHIR resource，以及 60 个开箱即用的解决方案，具备基于角色的访问控制、全面的审计跟踪、端到端加密和安全的个人健康信息（PHI）处理能力。他们还提供低代码或无代码界面，用于借助通过 Healthcare Model Context Protocol（HMCP）server 暴露的工具构建更多 AI agent。

Innovaccer 将 Bedrock AgentCore 用于以下目的：

- 使用 AgentCore Gateway 将他们的 OpenAPI 规范转换为兼容 HMCP 的工具，而无需承担构建、保护或扩展 MCP server 所需的繁重工作。
- 使用 AgentCore Identity 处理入站和出站认证，并与 Innovaccer 或客户提供的 OAuth server 集成。
- 使用 AgentCore Runtime 部署和扩展 AI agent，支持多 agent 协作，并具备日志记录、可追溯性以及接入自定义 guardrail 的能力。

Bedrock AgentCore 支持企业级安全，提供传输中和静态加密、完整的会话隔离、使用 [AWS CloudTrail](https://aws.amazon.com/cloudtrail) 的审计跟踪，以及帮助 Innovaccer 的 agent 大规模可靠、安全运行的全面控制能力。

## Bedrock AgentCore Gateway 的定价：

AgentCore Gateway 采用基于消费的定价模式，计费依据 API 调用（如 `ListTools`、`InvokeTool` 和 `Search API`）以及工具索引。更多信息请参阅[定价页面](https://aws.amazon.com/bedrock/agentcore/pricing/)。

## 结论

Amazon Bedrock AgentCore 与医疗保健系统的集成，代表着 AI 在改善患者照护和简化医疗保健运营方面应用的重大飞跃。借助 Bedrock AgentCore 提供的一整套服务，医疗保健机构可以部署复杂的 AI agent，安全地与现有系统交互、遵守严格的合规标准并高效扩展。

本文介绍的解决方案架构展示了这些技术的实际应用，说明 AI agent 如何简化免疫接种排程和预约等复杂流程。这可以减轻医疗保健服务提供方的行政负担，并通过提供对关键健康信息和服务的直接访问来提升患者体验。

展望未来，AI agent 在医疗保健行业的潜力是巨大的。从提升诊断准确性到个性化治疗方案、简化临床工作流，各种可能性无穷无尽。像 Amazon Bedrock AgentCore 这样的工具可以帮助医疗保健机构自信地应对实施 AI 的复杂性，同时维持最高的安全、合规和患者照护标准。

医疗保健行业正站在一个变革时代的门槛上，AI agent 将在提供高效、个性化、高质量照护方面扮演日益核心的角色。通过拥抱这些技术并持续创新，我们可以打造一个比以往任何时候都更敏捷、更智能、更以患者为中心的医疗保健网络。

### 关于作者

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/18/ML-19648-AuthorHeadshot-100x133.jpeg)**Kamal Manchanda** 是 AWS 的高级解决方案架构师，在云、数据和 AI 技术领域拥有 17 年经验。他与 AWS 客户的 C 级高管和技术团队紧密合作，推动云采用和数字化转型计划。在加入 AWS 之前，他领导全球团队，在咨询和产品组织中交付以云为中心的系统、数据驱动应用和 AI/ML 解决方案。Kamal 擅长将复杂的业务挑战转化为可扩展、安全的解决方案，带来可衡量的业务价值。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/19/ML-19648-KuldeepHeadshot-100x101.jpeg)**Kuldeep Singh** 是 Innovaccer 的 AVP 兼 AI 平台负责人。他领导 Innovaccer 旗下医疗保健智能平台 Gravity 的 AI agentic 工作流层的工作，该平台旨在统一数据、agent 和合规工作流，使医疗系统能够大规模部署 AI。Kuldeep 在数据工程、AI 和产品领导方面拥有深厚经验，专注于让医疗保健更高效、更安全、更以患者为中心。他在构建使照护团队无需繁重工程即可自动化复杂多步任务（如集成支付方或 EHR 数据、编排临床 agent）的工具方面发挥关键作用。他热衷于减少临床医生倦怠、改善患者结局，并将试点项目转化为企业级 AI 解决方案。
