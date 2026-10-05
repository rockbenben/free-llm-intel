---
vendor: aws_bedrock
title: Trane 如何用 Amazon Bedrock AgentCore 把楼宇洞察提速 60 倍
original_title: How Trane gets building insights 60x faster with Amazon Bedrock AgentCore
url: https://aws.amazon.com/blogs/machine-learning/how-trane-gets-building-insights-60x-faster-with-amazon-bedrock-agentcore
date: 2026-09-22
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

Trane Technologies 在全球管理着数以百万计的联网暖通空调（HVAC）资产，但要得到一个单一的运营答案，可能意味着交叉比对多个仪表盘、在菜单里钻取 20 分钟甚至更久。对在这样规模上运营的组织而言，这类摩擦会拖慢运营、推迟纠正措施，并在整个企业造成实质性的业务影响。

在 3–4 周内，Trane 的工程团队在 [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) 上构建了一个 AI 驱动的智能体式方案，把一个 20 分钟的多屏诊断工作流缩减为一次 20 秒的自然语言交互。这基于 Trane 与技师在数周内的内部基准测试。这代表在“到洞察的时间”上 60 倍的改进，帮助运营从被动响应转向更主动、数据驱动的优化。

在本文中，我们描述这一方案背后的架构方法和关键设计决策：

- 把智能体逻辑与工具执行分离。
- 通过一个集中式工具网关集成实时遥测。
- 为不同角色（persona）定制响应。

## Trane Technologies 与楼宇智能挑战

[Trane Technologies](https://www.tranetechnologies.com/en/index.html) 是一家全球气候创新者，年收入超过 210 亿美元，在 100 多个国家有业务。通过其战略品牌 Trane，公司管理着数以百万计的联网 HVAC 资产，横跨数据中心、医院、制造设施和商业房地产组合。在这片辽阔格局的核心是 [Trane Cloud](https://www.trane.com/commercial/north-america/us/en/products-systems/smart-building-technology/digital-platform.html)——一个聚合来自数百万 HVAC 系统实时表现数据的数字枢纽。Trane Cloud 把原始设备遥测转化为可行动的、用于预测性维护、能源优化和运营卓越的情报。

虽然基于仪表盘的楼宇管理系统为监控和控制提供了基础，但提取跨系统洞察仍可能需要用户 navigating 多个屏幕、层层菜单和彼此割裂的仪表盘。通过把自然语言处理与对 Trane Cloud 的深度集成结合，用户可以通过单一对话式界面访问那份运营上下文。结果是对复杂楼宇管理问题更快的答案，以及一种更主动、更知情的设施运营方式。

## 业务挑战：为什么楼宇运营者需要一个 AI 智能体

楼宇运营者、现场技师和服务经理在他们触手可及之处有海量数据。设备遥测、表现分析、故障告警、能源消耗模式和优化机会从各种分散系统涌入，但提取可行动洞察仍然困难。根本问题是不同利益相关方对同一份数据需要截然不同的视图。

现场技师需要诊断精度。他们需要制冷剂压力、故障码和系统级排障工作流。客户经理需要战略情报。他们需要正常运行时间指标、成本节省机会和组合表现趋势。楼宇业主需要高管级的清晰。他们需要效率评分、可持续性指标和简化的运营摘要。现有工具对所有角色呈现单一界面，要求每个用户 navigating 他们工作流之外的功能。

现有的楼宇管理应用依赖逐屏导航，这让跨设备比较更具挑战，并要求用户记住菜单层级和技术术语。即便是基本的组合级问题，也可能需要跨多个屏幕的耗时人工工作流。

合起来，Trane 的智能体式 AI 方案和 Trane Cloud 交付四项能力：

- **基于角色的访问控制**，为每个用户的权限和需求定制响应。
- **实时 HVAC 分析**，即时访问当前和历史的性能数据。
- **智能搜索**，跨 Trane 的技术文档和最佳实践知识库。
- **可扩展架构**，随 AI 能力演进并扩展到额外的楼宇系统。

这些能力创造了一种跨角色、跨工作流、跨运营环境访问楼宇智能的更可扩展的方式。

## 方案概览：架构

扩展智能楼宇运营的挑战，在于把数以百万计联网资产生成的海量数据变成可行动的洞察。尽管 Trane Cloud 大规模摄入实时遥测，回答运营问题传统上要求用户 navigating 割裂的仪表盘并跨系统手动连接信息。为解决这一点，团队在 [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) 和 [Strands 框架](https://strandsagents.com/) 上构建了一个对话式智能体，并通过 [AWS Cloud Development Kit (AWS CDK)](https://aws.amazon.com/cdk/) 基础设施即代码部署。团队选择 Strands 作为智能体框架层，因为它提供构建智能体行为所需的开发者 SDK 和编排逻辑，而 AgentCore 在其下处理托管运行时、记忆、工具网关和生产基础设施。

为避免单体设计的局限，方案使用一个多智能体架构，其中每个专用助手由它自己的 system prompt 治理，让它紧紧聚焦于单一能力域：

- **Resources Assistant（资源助手）** – 检索并摘要参考材料。例如，用户可能问：“我该联系谁、该遵循哪本手册，或能与客户分享哪些文档？”
- **Knowledge Assistant（知识助手）** – 综合关于设备如何工作、其系统参数，或 Trane Cloud 基础设施是否经过 SOC 2 鉴证的技术答案。
- **Analytics Insights Assistant（分析洞察助手）** – 查询实时遥测以呈现效率机会、标记需要检查的项，并追溯故障根因。
- **Expert Advisor（专家顾问）** – 帮助用户决定哪个产品方案契合某个场景、如何最大化客户价值，或如何组装一个定制演示。
- **Navigation Assistant（导航助手）** – 返回用户所需的精确链接和工具，从技术支持升级表单到替换零件订购页。

这一架构为可扩展性而设计。团队可以通过 AgentCore Gateway（Amazon Bedrock AgentCore 的一项能力）和 Model Context Protocol (MCP) 这样的开放标准，连接额外的智能体或工具，如工单管理系统和企业客户关系管理（CRM）系统。

图 1：Trane 在 Amazon Bedrock AgentCore 上的对话式智能体高层架构

## 微服务架构：系统设计与实现挑战

在企业规模上支持这些截然不同的用户需求，需要一个能跨能力独立演进的系统。一个单体智能体会迫使每一次改动（新工具、更新的 prompt、额外的数据源）都经过单一部署流水线，随系统增长制造瓶颈。

把一个 20 分钟的人工诊断缩减为一次 20 秒的对话，浮现出四个架构挑战。第一个是集成。方案必须把实时遥测与跨一个庞大知识库的智能搜索结合，同时支持与 CRM 这类外部系统连接。第二个是分离。智能体逻辑必须与后端工具执行解开，使两者能独立部署，并有清晰的所有权边界。第三个是上下文。系统需要在排障会话间维持对话状态，而不搭建复杂的定制向量数据库基础设施。第四个是可观测性。当一个智能体跨一个多步推理链编排多个工具时，故障会变得难以定位。一个错误的答案可能源于缺失的 API 凭证、畸形的工具响应，或一次模型幻觉。没有端到端追踪，团队在生产规模上无从区分它们。

## Amazon Bedrock AgentCore 如何应对这些挑战

Amazon Bedrock AgentCore 是一个以任意框架或模型大规模构建、连接并优化智能体的智能体平台。Trane 团队用四项 AgentCore 能力应对了前面这些挑战。

在选择 AgentCore 之前，团队评估了在 Amazon Elastic Container Service (Amazon ECS) 和 AWS Lambda 上托管智能体。那种做法会在计算层之上需要构建会话隔离、自动伸缩逻辑和按会话计费。四个差异化因素推动了这一决定。第一，托管的智能体运行时缓解了基础设施运维。没有集群要配置或伸缩，会话之间没有空闲容量要付费。第二，内建的会话记忆消除了搭建和维护外部向量数据库、或构建定制上下文窗口管理代码的需要。第三，通过 AgentCore Gateway 的原生工具编排把现有内部 API 变成兼容智能体的工具，无需为每个编写定制集成逻辑。第四，AgentCore 框架无关的设计意味着团队可以使用 Strands SDK 而不被锁定到一个专有的编排层，随需求变化保留灵活性。

- **AgentCore runtime**：Trane 使用 AgentCore runtime（Amazon Bedrock AgentCore 的一项能力），把每个用户会话隔离在一个带自己 CPU、内存和文件系统的专用 microVM 中。AgentCore runtime 在会话完成时终止并清理每个 microVM。团队选择它是因为 microVM 模型把面向用户的智能体与后端 MCP Server 分开，让两者以清晰的所有权边界独立部署。AgentCore runtime 在物理上把一个现场技师的会话与一个楼宇业主的会话隔离，强化了基于角色的访问而无需定制基础设施。Trane 只为会话期间的活跃计算付费。工具调用之间那种（智能体工作流典型的）长时暂停不会累积成本。
- **AgentCore Gateway**：Trane 使用 AgentCore Gateway 把 Trane Cloud 的内部 API 暴露为兼容 MCP 的工具，团队按能力域组织这些工具并与 Amazon OpenSearch Service 集成。团队选择它是因为把这套助手连到实时分析、设备遥测和问题诊断，需要一个处理认证和 schema 转换的单一访问层。未来的集成（CRM、工单系统）经同一个 Gateway 连接而无需额外的管道。
- **AgentCore memory**：Trane 使用 AgentCore memory（Amazon Bedrock AgentCore 的一项能力）在排障会话间维持对话状态，使用户能问自然的追问（“现在把它和上个月比较一下”）而无需重新指定上下文。团队选择它是因为替代方案是搭建一个单独的向量数据库并编写定制上下文窗口管理代码。AgentCore memory 开箱提供短期会话记忆，带一个 90 天过期生命周期，在上下文感知与存储效率之间取得平衡，帮助 Trane 落实其数据保留政策。
- **AgentCore Observability**：Trane 使用 AgentCore Observability（Amazon Bedrock AgentCore 的一项能力）追踪智能体所做的工具调用，并跨多步推理链隔离故障。团队在开发期间遭遇了一致的、没有端到端可见性就无法识别的工具故障之后选择了它。通过在 Amazon CloudWatch 中的智能体 trace，工程师确认了跨多次调用的同一故障模式，并把它追溯到一个缺失在 AWS Secrets Manager 中的 secret。加上那个 secret 后，故障解决了。

实时数据流如下工作：

- 用户的查询带着一个 JSON Web Token (JWT) 打到 AgentCore runtime。Runtime 的入站授权器（AgentCore Identity，Amazon Bedrock AgentCore 的一项能力）针对 OpenID Connect (OIDC) 发现端点验证令牌。然后 AgentCore memory 在智能体处理请求前注入先前的对话上下文。
- 然后智能体通过 OAuth 2.0 机器到机器认证触发那个单独的 MCP Server，以安全访问后端工具。
- MCP Server 对 OpenSearch Service 和其他已连接系统执行并行工具调用，以快速做语义数据检索。
- 最后，Amazon Bedrock 上的 Anthropic Claude 模型综合遥测并通过 Server-Sent Events (SSE) 把响应流式返回给用户。这最小化了感知延迟，在数秒内交付答案。关于按 AWS 区域的模型可用性，参见 [Amazon Bedrock 中按 AWS 区域支持的模型](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html)。

## 结果与影响

使用 Amazon Bedrock AgentCore 和 Strands 框架，团队取得了前述 60 倍的到洞察时间改进。过去需要 navigating 多个屏幕的跨设备比较和诊断工作流，如今通过一次自然语言查询在数秒内完成。这帮助团队更快推进、减少分析步骤，并对设施运营采取更主动的方式。

除运行时性能外，该架构还交付了额外收益：

- **快速从原型到生产：** 团队在 3–4 周内搭起一个可用的原型并向利益相关方演示，然后先把智能体作为 beta 测试推给内部现场技师。现场技师执行最苛刻的诊断工作流，因此他们的反馈在真实条件下浮现出准确率和可用性缺口。团队在发布给外部客户之前基于那份反馈优化了智能体响应。
- **跨应用快速集成：** 有了解耦的微服务架构和集中的 AgentCore Gateway，把同一智能体后端集成进其他企业应用耗时不到一天。
- **有效的生产调试：** CloudWatch 中 AgentCore Observability 的完整调用 trace 让团队能快速定位一个反复出现的工具故障。

## 生产控制与负责任的 AI

部署一个从实时运营数据返回诊断建议的 AI 智能体，需要防范滥用和越界响应的控制。团队配置了 [Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/)，用内容过滤器阻止有害或不恰当的输出，并用限制智能体在其运营域内的主题拒绝策略，帮助阻止它回答超出其运营域之外的问题。敏感信息过滤器在响应到达用户之前检测并脱敏可识别个人身份信息（PII），而 prompt 攻击检测帮助防范那些可能绕过智能体 system prompt 的越狱尝试。

在基础设施层，Trane 基于角色的访问模型帮助把每个用户限制在其授权范围内的数据。AgentCore runtime 的每会话 microVM 隔离帮助在计算层防止跨租户数据泄漏风险。这些控制协同工作，让 Trane 能有信心地把智能体扩展到生产用户。响应保持在范围内，基于角色的访问和 PII 过滤器帮助保护敏感数据，而 Bedrock Guardrails 帮助强制执行智能体预期的运营边界。

## 结论

Trane 的落地展示了组织如何把 AI 智能体和其专有数据用作一种独特的竞争优势。通过基于 [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) 构建，该组织确立了一个稳健、安全的企业标准，可以跨不同业务部门扩展和复用。

这一从 3–4 周原型、经准确率调优和内部 beta、到外部发布和复用的分阶段上线，浮现出五条关于扩展企业 AI 的洞见：

- **数据是你的差异化：** 智能体成功的基础依赖现有企业数据，如 OpenSearch Service 索引和物联网（IoT）遥测。智能体的真正价值直接来自用这些专有数据驱动更高效的能源使用和运营卓越。
- **架构基础很重要：** Strands 框架帮助团队起步并快速迭代，而 Amazon Bedrock AgentCore 提供了大规模运行智能体所需的、专为其打造的基础设施和安全服务。承诺 MCP 这样的开放标准帮助为未来的增强提供了灵活性并加速了构建。
- **分阶段上线，先在内部加固：** 部署给内部现场技师（最苛刻的用户）捕获了关键的技术反馈，并让团队在向 Trane Cloud 客户外部发布之前优化准确率。
- **基于角色的访问和响应：** 不同角色需要不同工具和不同的响应格式。动态策略映射意味着一个现场技师收到逐步骤的诊断工作流，而一个楼宇业主收到简化的效率评分。这驱动了采纳，因为用户看到为其角色定制的响应。
- **可观测性是智能体系统的关键：** 当一个智能体在一个推理链中编排多个工具时，故障可能难以识别。通过 CloudWatch 的端到端调用追踪给了团队快速定位并解决问题的能力。

要了解更多关于构建智能体式方案的信息，访问 [Amazon Bedrock AgentCore 文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)，探索 [Strands Agents SDK](https://strandsagents.com/)，或关注 [AWS Artificial Intelligence Blog](https://aws.amazon.com/blogs/machine-learning/) 获取更多客户故事。

## 下一步

团队正在几个领域扩展该方案。

首先，AgentCore Evaluations（Amazon Bedrock AgentCore 的一项能力）会用自动化的准确率阈值来把关未来的上线阶段。为减轻质量保障（QA）团队的负担，团队会定义每次发布推进前必须通过的通过率基准。

其次，AgentCore 中的 Policy 会取代当前编码在 Runtime 里的定制授权逻辑。工具级的访问决定会转向声明式策略定义，使上线新角色和审计谁能调用哪些工具更容易。

第三，团队正在把他们的 AgentCore Gateway 开放给其他工程团队。因为 Gateway 通过 MCP 暴露工具，其他团队可以在同一集中数据层之上构建他们自己的智能体，而无需学习专有接口或搭建重复的集成。团队正在构建带用量跟踪的自助上线，以便他们衡量采纳并识别其他团队觉得最有价值的工具。

第四，团队正在快速添加新工具。一个已在进行的例子：现场办公室目前为每个客户站点手动做深度成本节省分析。团队正把它构建为一个智能体工具，使分析通过自然语言按需运行，去掉每次数百小时的人工工作。
