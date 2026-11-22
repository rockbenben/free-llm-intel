---
vendor: aws_bedrock
title: Rede Mater Dei de Saúde: Monitoring AI agents in the revenue cycle with Amazon Bedrock AgentCore
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/rede-mater-dei-de-saude-monitoring-ai-agents-in-the-revenue-cycle-with-amazon-bedrock-agentcore
date: 2026-04-15
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 711ee972f2e6
---

# Rede Mater Dei de Saúde：使用 Amazon Bedrock AgentCore 监控收入周期中的 AI agent

*本文由 Rede Mater Dei de Saúde 的 Renata Salvador Grande、Gabriel Bueno 与 Paulo Laurentys 共同撰写。*

多 agent AI 系统的日益普及正在重新定义医疗健康领域的关键运营环节。在大型医院网络中，数千项决策直接影响现金流、服务交付时间和理赔拒付风险，因此能否对 AI agent 进行监控、追踪和治理，已成为运营可持续性的必要条件。这就是 Rede Mater Dei de Saúde 的实践历程：该机构正使用 [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) 落地其由 12 个 AI agent 组成的套件，这一综合性服务为生产环境中的 AI agent 提供 agent 运行时、工具集成、记忆管理以及内置的可观测能力。

## **关于 Rede Mater Dei de Saúde**

拥有 45 年历史的 Rede Mater Dei 是巴西最受尊敬的医疗健康机构之一，在 Belo Horizonte、Betim-Contagem、Nova Lima、Salvador、Uberlândia、Goiânia、Feira de Santana 设有机构，并在 São Paulo 有一个在建的新项目。该机构将技术、先进的分析智能与高复杂度诊疗相结合，交付以患者为中心的成果与卓越运营。

## **应对巴西医疗健康领域的结构性挑战**

根据巴西私立医院协会（[Anahp](https://www.anahp.com.br/noticias/hospitais-reduzem-mortalidade-e-tempo-de-internacao-mas-enfrentam-alta-de-glosas-e-de-rotatividade/)）的数据，2024 年巴西的理赔拒付达到令人警惕的水平：行业平均值从 11.89% 跃升至 15.89%，相当于高达 R$ 10 billion 的未收回收入。与许多机构一样，Rede Mater Dei 也面临运营层面的挑战：

- **手工流程**通常由数百名运营人员处理。
- **流程碎片化**，其特征是数据非结构化且分散。
- **团队流动率高**，因为任务的重复性会使员工流失，这些流程只能由不断更换的人员来承担。
- **复杂的核验**需要持续而高强度的关注，在流程的脆弱环节造成不一致与返工。

这些弱点直接影响了从资质审核到计费的整个收入周期，也使该机构暴露在整个行业共同面临、并推高拒付率的同类风险之下。在 A3Data 与 AWS 的支持下，Rede Mater Dei 启动了一项转型计划，旨在减少拒付的成因、加快分析速度，并通过 AI agent 构建一套可治理、可观测、可扩展且高质量的运营体系。

### **部署在 Amazon Bedrock AgentCore Runtime 上的 12 个 AI agent 套件**

Rede Mater Dei 与 A3Data 以及 AWS 生成式 AI（GenAI）创新中心一起，规划了一个包含 12 个 AI agent 完整套件的项目，覆盖整个医院收入周期。该套件构建出一支“数字力量”，让 AI agent 以编排化、持续且可审计的方式，尽可能自主地感知、决策与行动。

在计划中的 12 个 agent 里，首批落地的包括：

- **合同 Agent（Contracts Agent）**：集中管理并结构化此前分散在各类文档中的复杂合同规则。
- **参数化 Agent（Parameterization Agent）**：自动将规则转换为医院的企业资源计划（ERP）系统配置，有助于减少人为错误并加快更新速度。
- **授权 Agent（Authorization Agent）**：自动化向健康保险机构发起的请求、校验与交互。

这些 agent 运行在 Amazon Bedrock **AgentCore Runtime** 上，后者为部署、运行和扩展 AI agent 与工具提供安全、无服务器的托管环境。

团队将架构组织为三个互补的层次：

- **DEL（Data Execution Layer，数据执行层）**：将来自多个数据源的数据组织为结构化的数据湖。
- **AEL（Agent Execution Layer，agent 执行层）**：以集成方式编排并执行各个 agent。
- **TCL（Trust and Compliance Layer，信任与合规层）**：实施治理、安全与合规对齐，便于实现可追溯性。

为了治理 AI agent，Rede Mater Dei 与 A3Data 和 AWS GenAI 创新中心建立合作。双方共同在 **Amazon Bedrock AgentCore** 上构建了完整的 agent 关键执行与治理层，后者成为整套 agent 的运营核心。该项目是拉丁美洲的先驱性实践，在一个高影响力的医疗健康业务应用中，对 [AgentCore Evaluations](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations.html) 进行大规模、全面的验证。

## **为什么选择 Amazon Bedrock AgentCore？**

作为 Amazon Bedrock 的一部分，AgentCore 是一套综合性服务，为 agentic 场景提供基础能力。它提供工具、部署与可观测能力，以及按需组合的模块化组件，用于在规模化且安全的前提下部署、运行和改进 AI agent。其组件包括：

- **安全的无服务器**[AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html)。
- [AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)，用于将 agent 连接到现有的工具与服务。
- [AgentCore Memory](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html)，提供短期与长期的持久记忆，以便在多个会话之间保持上下文。
- **可观测资源**，用于监控。

初始实施的重点，是通过 [AgentCore Observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html) 与 **AgentCore Evaluations**，为已有的多 agent AI 方案增加一层监控与改进能力。

使用 AgentCore Evaluations，Rede Mater Dei 为该方案增加了**监控与评估层。这一层支撑**多 agent AI 系统的持续改进，使其性能可度量、可控制且准确率高。

通过该服务，可以评估被视为全球最佳实践的指标与指标项，例如正确性、实用性、精确性、安全性、目标成功率以及上下文相关性。

这套评估结构为 AI agent 提供了**度量与可追溯性**。这些能力有助于在医疗健康环境中维持稳定性、韧性、可预测性以及对监管要求的遵从。

## **采用 AgentCore Evaluations 的架构**

该方案的设计与实施如下图所示，其中已纳入 AgentCore Evaluations：

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/01/ML-20233-image-1.png)

AgentCore Evaluations 架构

### **517% 投资回报率与多个流程中的结构性效率提升**

以 AgentCore Observability 与 AgentCore Evaluations 为抓手的初始阶段，让 Rede Mater Dei 取得了可量化的收益，并为更安全、更可预测、更数据驱动的 AI 运营奠定了基础。该初始阶段带来了强劲的财务与临床成果：**前四个月实现 517% 的投资回报率（ROI）**、**授权时间缩短 66%**、**手术开始时间缩短 33%**。除这些收益之外，AgentCore 治理层还扩展了该机构在有控制、可透明的条件下运营和演进其 agent 的能力。

### **治理与合规**

结构化的可观测能力为收入周期的关键决策提供了完整的可追溯性，为 agent 的每一次交互、所应用的每条规则以及所采取的每个动作留下不可篡改的审计轨迹。这有助于降低监管风险、强化运营安全，并简化内部与外部的核查——在合同、授权和计费等敏感流程中尤为如此。

### **运营效率**

借助统一的遥测数据，团队减少了识别和解决故障所耗的时间，复制了在其他用例中观察到的效果，目标是**事件解决时间缩短最多 50%**。团队可以立即发现 agent 的异常行为、性能下降或数据不一致，从而加快持续改进循环，并提升直接影响拒付风险的工作流的可靠性。

### **战略决策**

对关键绩效指标（KPI）的实时可见性，覆盖自动化分析量、预计财务影响、处理速度、预估拒付风险、校验成功率以及按保险机构划分的各项指标。这些洞察把运营数据转化为更快、更精确的高管决策，用于指导规则调整、积压事项的优先级排序、团队扩容，以及针对最影响收入与效率的工作流的精准干预。综合来看，这些成果表明：Mater Dei 的 agent 套件与 AgentCore 的结合，不仅带来了立竿见影的收益，也有助于为更稳健、可审计、可扩展的医院运营奠定基础，从而支撑该网络的扩张，并应对巴西在理赔拒付方面的结构性挑战。

除已取得的成果之外，该项目还成为全球性的参考案例：在拉斯维加斯举行的 AWS re:Invent 2025 上，它出现在 [Ruba Borno 的主题演讲](https://youtu.be/JVj-r7B0gOU?t=991)（AWS 专家与合作伙伴副总裁）之中，展示了收入周期的转型不仅可行：它可度量、可快速推进，并能带来可观的回报。

## **客户证言**

> “与 A3Data 一起，我们用更具分析性、结构化和创新驱动的方式，正在化解一个长期存在的行业难题。我们的重点是提升收入周期关键环节的准确性、可预测性和敏捷性，减少波动，并强化该网络的运营与财务效率。这种一致性提升自然转化为更顺畅的患者体验，其背后是更有条理、技术上更稳健的流程。”
>         – Renata Salvador Grande，Rede Mater Dei de Saúde 商务与市场营销副总裁

### **关于作者**
