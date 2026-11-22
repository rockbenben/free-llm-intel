---
vendor: aws_bedrock
title: How LendingTree built a multi-agent mortgage assistant on Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/how-lendingtree-built-a-multi-agent-mortgage-assistant-on-amazon-bedrock
date: 2026-08-05
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 64199987ca7e
---

# LendingTree 如何在 Amazon Bedrock 上构建多 agent 房贷助手

买房是大多数人面对的最大财务决策之一，[LendingTree](https://www.lendingtree.com/) 在 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 上构建了一个多 agent 房贷助手，让这个过程更直白易懂。该助手为借款人做科普、理解他们的处境，并在自然对话中给出量身定制的选项。借款人必须权衡购房还是再融资、常规贷款还是政府担保贷款、15 年还是 30 年期限，以及固定利率还是浮动利率。此外还有一堆行话，比如“discount points”（折扣点）、“origination fees”（放款手续费）和“debt-to-income ratio”（债务收入比）。难怪很多人在还没开始时就已感到迷茫。

25 年多来，LendingTree 一直在帮助消费者梳理这些选择，为数以百万计的人对接贷款机构，以找到有竞争力的房贷报价。这家公司建立在这样一个信念之上：每个人都应当拥有做出自信财务决策所需的工具与知识。[AI 驱动的房贷助手](https://agent.lendingtree.com/chat)就是下一步。

这套方案必须满足 LendingTree 从第一天起就遵循的同一套标准：准确的信息、透明的引导，以及对用户数据的严格保护。要在房贷行业的监管要求下运作，意味着内容过滤、个人可识别信息（personally identifiable information，PII）保护和合规监督都不是可选功能。它们没有商量余地。这让 Amazon Bedrock 及其内置 guardrails 成为正确的基础。

> “我们的目标是成为购房旅程中值得信赖的伙伴——一位引导者，为消费者做科普、理解他们的处境，并为他们匹配正确的报价。Amazon Bedrock 中的基础模型和内置 guardrails 让我们从一开始就能以安全与合规的方式交付这一点。”

— Srinivas Madabushi，LendingTree 技术高级副总裁

业内许多公司都为基础问题加了 chatbot。LendingTree 想走得更远：回答那些难的问题，并为借款人匹配有竞争力的报价。这需要不止一个 agent。

## 方案概览

为应对这些挑战，LendingTree 部署了三个独立的 AI agent：一个 supervisor 和两个专职 worker（教育与匹配），并用 [LangGraph](https://www.langchain.com/langgraph)、[Model Context Protocol（MCP）](https://modelcontextprotocol.io/) 以及由 Amazon Bedrock 提供的基础模型来协同。所有 agent 都以容器化服务的形式运行在 [Amazon Elastic Container Service（Amazon ECS）](https://aws.amazon.com/ecs/) 上，配合 [AWS Fargate](https://aws.amazon.com/fargate/)。

LendingTree 选择 Amazon Bedrock，是看中它的多模型灵活性以及继承来的 AWS 治理控制——这是其合规团队的要求。方案部署在 Amazon ECS 上而非 [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) 上，因为当 AgentCore 正式可用时，它已经在生产环境中了。AgentCore 是一个用于大规模构建、连接和优化 agent 的平台，支持任何框架、任何模型。

下图展示了高层架构。

LendingTree 用于房贷咨询的多 agent 架构

**（1）** 面向消费者的聊天界面是一个 React 应用，以容器化服务的形式运行在 Amazon ECS 与 Fargate 上，通过公共端点服务网页端与移动浏览器的消费者。

**（2）** 用户输入与模型输出都会经过 [Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/) 做内容过滤（例如仇恨与脏话检测）和 PII 脱敏。收到的消息还会接受 prompt 威胁筛查。

与 Guardrails 并行，一个基于大语言模型（LLM）的安全分类器执行 LendingTree 的对话策略。两项安全检查并发运行，因此这份额外的保障不会增加延迟。

一个业务逻辑层处理 LendingTree 的运营规则：把复杂问题转给人工支持，并把跑题的对话引导回来。

**（3）** Supervisor agent 是编排者，基于 LangGraph 构建为一个遵循 plan-and-execute 模式的状态机。它的运作方式像一个组织良好的团队：Supervisor 理解全局并决定需要做什么，而各个 worker 负责各自最擅长的事。

Supervisor 是一张由节点和边构成的图。节点负责干活（意图分析、执行规划、响应组装），边则根据结果决定接下来发生什么（路由到 Education、路由到 Matching，或直接回答）。这让流程变得显式：穿过系统的每一条路径都是定义好的、可审计的、可追踪的。

Supervisor 用 [Amazon Nova Pro](https://aws.amazon.com/ai/generative-ai/nova/) 分析用户意图并产出执行计划。随后它通过 MCP 路由到合适的 worker，并使用连接池以实现低延迟调用。关于各区域可用的模型，请参阅 [Amazon Bedrock 中按 AWS 区域划分的受支持模型](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html)。

并非每个任务都需要最强的模型。Supervisor 实现了多模型架构，根据任务需求在 Amazon Nova Pro（用于复杂推理与关键分类）和 Amazon Nova Lite（用于对话式响应与轻量分类）之间自动选择。这在可靠性与成本之间取得平衡。

规划与执行在设计上就是分离的。当一次对话出了问题，团队可以精确追踪到是哪个节点做了哪个决策。

**（4）** Education worker 是耐心的科普者。它帮助用户理解房贷概念、解释产品差异，并通过交互式对话提供引导。它运行自己的 LangGraph workflow，并维护针对其领域定制的 [Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/)——即完全托管的检索增强生成（RAG）能力——以 [Amazon OpenSearch Service](https://aws.amazon.com/opensearch-service/) 作为向量存储。每一个回答都扎根于真实文档，而不是仅依赖模型自身知识。

**（5）** Matching worker 是连接者。它收集用户偏好，并调用 LendingTree 内部的报价、资格与利率 API。在此基础上，它根据用户的实际处境交付个性化的贷款选项。它会解读资格标准，并帮助用户并排比较选项。

**（6）** 共享服务通过 [Amazon Relational Database Service（Amazon RDS）](https://aws.amazon.com/rds/) 上的 LangGraph PostgreSQL checkpointer 处理对话记忆与会话状态。这让对话能跨轮次、跨 agent 交接、跨服务重启保持。用户可以暂停、稍后回来，或提出后续问题，都不会丢失上下文。

**（7）** Amazon Bedrock 提供广泛的基础模型，适用于各种用例。从复杂推理与关键分类（Amazon Nova Pro）到成本高效的对话式响应与轻量分类（Amazon Nova Lite），全部可通过一个 API 访问。内置的 [Guardrails](https://aws.amazon.com/bedrock/guardrails/) 提供可配置的安全控制，而 Amazon Bedrock Knowledge Bases 通过 Amazon OpenSearch Service 等向量存储把 agent 连接到权威内容，实现混合检索。

**（8）** LendingTree 内部的 service 与 API 提供贷款机构搜索、利率与产品数据、资格与预先核准检查、报价比较，以及用户画像信息。

**（9）** 所有 service 都运行在 Amazon ECS 与 AWS Fargate 上，每个 agent 依据自身需求信号独立扩缩容。基础设施通过 Terraform 管理，并通过 GitLab 持续集成与持续交付（CI/CD）pipeline 部署，带有自动化测试与健康检查。

### 端到端跟踪一次对话

假设用户问：*“FHA 和常规贷款有什么区别，哪一种适合我？”*

消息先流经 Amazon Bedrock Guardrails（2）做安全筛查。随后 Supervisor agent（3）从对话记忆（6）加载对话历史并分析意图，识别出两个需求：一段解释和一次个性化比较。它通过 MCP 把科普类问题路由到 Education worker（4），把匹配类问题路由到 Matching worker（5）。每个 worker 独立运作并返回结果。Supervisor 把两者聚合成一段连贯回复，在交付前再把输出过一遍 Guardrails。整段交互都会被 checkpoint 到 PostgreSQL（6），因此下一轮能从完整上下文接着进行。

对用户来说，这是一次连续的对话。在幕后，它是一套协同的 workflow，其中每个决策点都可追踪。

## 部署与运维

由于 agent 之间通过 MCP 通信，每一个都可以独立更新、扩缩容和回滚。Education worker 可以发布新的 knowledge base，而不必改动 Supervisor 或 Matching worker。在运维层面，多 agent 系统特有的挑战是追踪单次跨越多个服务的对话。[Amazon CloudWatch](https://aws.amazon.com/cloudwatch/) 日志与 [AWS X-Ray](https://aws.amazon.com/xray/) 分布式追踪让团队能跟随一次对话在全部三个 agent 之间的旅程，并获得按 agent 划分的指标与详细耗时。

## 结果

该助手自 2025 年底起就在生产环境中处理真实的房贷对话。本节指标基于 LendingTree 内部从上线到 2026 年第一季度的生产分析，由 LendingTree 工程团队提供。在此期间，它服务了大约 1,960 次对话、12,100 条消息，平均每次交互 6.2 条消息。这些不是一次性的查询：活跃用户会维持多轮会话，平均在 9 分钟内超过 10 条消息，不断提出后续问题、细化自身处境，并以对话方式探索选项。

**从科普到行动。** 对话数据揭示了消费者实际如何使用 AI 房贷助手。在上线初期，75% 的对话属于科普性质。用户会问“什么是 FHA 贷款？”“HELOC 是怎么运作的？”“申请常规贷款需要多少信用分？”随着系统成熟并口口相传，交易意图随之增长：最近超过 50% 的对话涉及利率比较、贷款机构匹配或预先核准——这些都是直接与转化挂钩的动作。

**对话深度体现信任。** 平均 6.2 条消息的会话长度说明了一件事。活跃用户平均 9 分钟内 10 条以上消息则说明了另一件事。用户不会对一个自己觉得没用的系统维持这样的参与度。Education worker 建立起理解，当用户准备行动时，他们自然而然地走向 Matching worker。没有强制交接，也没有“从头再来”的时刻。

**这些问题揭示了真实的复杂度。** 最常见的话题包括贷款类型比较（FHA、常规贷款和 VA）、针对特定信用画像的资格标准、利率谈判策略、放款时间线，以及首付权衡。这些恰恰是静态 FAQ 页面无法答好的、依赖具体处境的问题。它们需要上下文：用户三轮之前说过什么、他们符合什么资格、他们在优化什么。这正是对话记忆与 Supervisor 的意图分析之所以值得其复杂度的地方，而系统会维持这条线索，让每个回答都建立在上一段之上。

**承接率（containment）。** 超过 97% 的对话被端到端处理，没有升级到人工；只有约 3% 的用户明确要求真人 agent。对于一个受监管的金融产品——问题确实难，答错会有真实后果——这样的承接率意义重大。它表明系统有能力作为一个自包含的咨询类服务运作，而不只是呼叫中心前面的一层分诊。

**数据确认了什么。** 参与深度才是最重要的信号。信息更充分的用户会做出更好的决策。对话式界面能挖掘出静态表单永远无法组合捕获的偏好与约束。像“我是一名退伍军人，信用分 650，想在 30 天内于 Colorado Springs 买房”这样的细节，会让下游的贷款机构匹配更有相关性。这最终才是真正服务消费者的方式。

## LendingTree 学到了什么，以及下一步

把一个多 agent 系统推到生产环境，让团队在架构上学到的东西不亚于任何单一功能。

在发布房贷助手之后，LendingTree 意识到：构建一个 agent 很直接，但扩展到多个 agent 需要共享的地基。LendingTree 不是把每个新功能都做成一次性实现，而是在投资可复用的组件。这些包括用于数据访问的共享上下文层、用于工具集成的 MCP 契约，以及标准化的部署流程。一个 registry 让团队能发现已有能力，而不是重复造轮子。这让团队可以构建更小、聚焦于领域的能力，再组合成更宽泛的消费者体验。安全、可观测性、评估和复用方面的一致标准把这一切串在一起。

**Agent 设计上的经验：**

- **Knowledge Bases 的语义分块。** 把文档切成语义上连贯的块，而不是固定大小的块，显著提升了检索质量，因为分块边界与自然的话题切分对齐。
- **Knowledge Base 的冲突消解。** 有多个 KB 时，有时会浮现互相矛盾的信息。基于领域的过滤与来源优先级解决了这个问题：对产品相关的问题，LendingTree 内部内容优先；外部资源则服务于通用的房贷科普。
- **agent 之间的上下文传递。** worker agent 起初对更宽泛的对话缺乏认知。在每次 MCP 请求中传入完整对话历史和意图摘要，让 worker 获得了提供相关回答所需的上下文。
- **query 改写。** 像“not sure”或“yes”这样的简短用户回复，会在检索之前借助对话历史改写成有意义、可检索的 query。这显著提升了检索质量。
- **Guardrail 调优是持续性的工作。** 早期配置会拦下合法问题，因为房贷术语触发了内容过滤器。用真实对话数据做调优解决了这个问题。
- **基于任务的模型路由** 让成本可控：只在推理确实需要的场景用 Nova Pro，其余一律用 Nova Lite。

这些是 agent 设计层面的问题，而不是基础设施问题。无论选择哪种运行时，它们都同样重要，也构成了这次实现留下的持久知识。

**基础设施上的经验：**

- **对话状态管理。** 早期版本在 agent 交接时会丢失上下文。一个统一的、由 PostgreSQL 支撑并显式序列化状态的 checkpointer 解决了这个问题，让对话能跨 agent 切换与系统重启保持。
- **并行执行安全检查** 在不削弱保护的前提下保住了延迟。
- **agent 的独立扩缩容** 需要为每个 agent 手工接线 ECS 容器、健康检查和部署 pipeline。

团队现在正在评估把架构迁移到 AgentCore，以把无差异的基础设施工作卸载出去。这样可以避免手工接线 PostgreSQL checkpointer、ECS 容器和 agent 扩缩容，让工程投入从“维持运行时活着”转向“持续优化 agent 逻辑与领域知识”。

## 结语

LendingTree 的生产级多 agent 系统表明，AI agent 能够在高度受监管的行业中服务消费者——不只是作为原型，而是作为 7×24 运行的生产系统。Amazon Bedrock（Nova Pro 与 Nova Lite、Knowledge Bases 和 Guardrails）提供了模型与安全基础。LangGraph 负责 agent 编排，MCP 负责 agent 之间的通信。它们合在一起，在维持严格合规标准的同时，大规模交付个性化的房贷指导。

对于正在构建多 agent 系统的组织：把规划与执行分离，让系统可调试。把安全做成结构性支柱，而不是一个可以跳过的步骤。从第一天起就为可复用的能力做设计，那将让你把这一模式推广到整个组织。

要在 AWS 上开始构建多 agent 系统，请查阅 [Amazon Bedrock 文档](https://docs.aws.amazon.com/bedrock/) 以及 [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) 的托管运行时能力。

## 相关资源

- [使用 Amazon Bedrock AgentCore 在 AWS 上构建高度可扩展的无服务器 LangGraph 多 agent 系统](https://aws.amazon.com/blogs/machine-learning/build-highly-scalable-serverless-langgraph-multi-agent-systems-in-aws-with-amazon-bedrock-agentcore/) — 了解如何使用 Amazon Bedrock AgentCore 构建并部署基于 LangGraph 的多 agent workflow。
- [GitHub 上的 AgentCore 示例](https://github.com/awslabs/agentcore-samples) — 探索示例多 agent 架构与模式。

## 关于作者
