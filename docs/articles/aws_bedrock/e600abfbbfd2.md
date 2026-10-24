---
vendor: aws_bedrock
title: 使用 AWS Agent Registry 在运行时发现工具
original_title: Discover tools at runtime with AWS Agent Registry
url: https://aws.amazon.com/blogs/machine-learning/discover-tools-at-runtime-with-aws-agent-registry
date: 2026-10-20
lang: zh
captured: 2026-10-24
extractor: readability-v1
translator: agent
status: translated
body_sha: 04180b5df6a4
---

## [Artificial Intelligence](https://aws.amazon.com/blogs/machine-learning/)

# 使用 AWS Agent Registry 在运行时发现工具

借助 AWS Agent Registry 的运行时发现，可以解决一个 agent 演示中容易被掩盖的问题。硬编码的工具在只有少数几个时运行良好，到几十个时开始退化，再往上就变得无法管理。企业系统会暴露数百个用于定价、支持、订单、库存和客户数据的内部 API。在这些系统中，模型花在消歧工具名称上的 token 可能比推理用户请求还要多。每增加一项新能力，都需要在编排器中改动代码、重新部署，并在那些更希望按自己节奏发版的团队之间进行协调发布。

在团队向 agentic 消费方暴露大量内部 API 表面的企业软件即服务（SaaS）项目中，这种模式可能反复出现。随着目录扩张，构建期的接线可能成为瓶颈。一种方法是改变编排器访问工具的方式：与其把每个工具都编译进 agent，不如让 agent 在运行时发现相关工具。

[AWS Agent Registry](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html) 是一项托管服务，用于对 Model Context Protocol（MCP）server、agent 和 agent skill 进行编目与发现。发布者注册协议特定的描述符和可搜索的描述。在运行时，编排器可以搜索已批准、可发现的记录，并使用返回的端点和描述符内容来构建客户端。Registry 的搜索结果不会返回该能力的调用凭证或身份验证方案。

本文逐步讲解重构后的 Python 示例所演示的 Discover → Instantiate → Execute 循环。该代码通过 [Amazon Bedrock AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)（Amazon Bedrock AgentCore 的一项能力）部署一个订单管理 MCP server，在 [AgentCore runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime.html) 上部署两个 agent 到 agent（A2A）agent，以及一个 Registry 和一个编排器。[示例目录](https://github.com/ach1ntya/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastructure/03-registry/03-advanced/discovery-and-invocation-at-runtime)包含部署脚本、编排器、辅助模块和清理脚本。

## 解决方案概览：发现、实例化、执行

本示例中的编排器 agent 对工具或 agent 没有任何内置知识。

![Comparison of hardcoded tool endpoints versus runtime discovery with AWS Agent Registry](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21108-1-1.png)

图 1：没有 AWS Agent Registry 时（左侧），端点是硬编码的，新增一个 agent 意味着修改代码并重新部署。使用 AWS Agent Registry 时（右侧），编排器通过语义搜索发现能力，新的集成在注册并获得批准后即可使用

### 发现

编排器向 AWS Agent Registry 数据平面发送一个自然语言查询。搜索响应包含记录标识、名称、描述、记录类型、状态、版本，以及协议描述符（例如 MCP server 元数据或 A2A agent card）。它不包含调用凭证。应用必须通过另一条受信任的配置路径获取并应用合适的凭证。

### 实例化

对于每个返回的记录，编排器根据描述符类型构建客户端。在本示例中，注册的 MCP server 代表最初作为目标添加到 Amazon Bedrock AgentCore Gateway 的工具。因此 MCP 描述符指向 Gateway 端点。编排器另行获取一个 [Cognito OAuth](https://docs.aws.amazon.com/cognito/) 访问 token，并在创建 `MCPClient` 时使用它。A2A 记录包含一个 agent card，其 URL 标识一个 AgentCore runtime 端点。封装层通过 [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/agent-registry.html) 数据平面客户端调用该运行时，该客户端使用调用方的 AWS 凭证对请求签名。Registry 的发现只提供连接元数据，不提供身份验证材料。

### 执行

一个临时的内部 agent 仅用动态发现的工具构建。large language model（LLM）为请求挑选合适的工具，结果经过综合后返回给用户。这一轮结束后，内部 agent 及其客户端会被拆除。下一个请求会获得一次全新的搜索和一套全新的工具。

![End-to-end architecture: the orchestrator queries AWS Agent Registry, then invokes MCP servers through AgentCore Gateway and A2A agents on AgentCore runtime](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21108-2-1.png)

图 2：端到端架构。Amazon Bedrock AgentCore runtime 上的单个编排器查询 AWS Agent Registry。匹配的 MCP server 通过 Amazon Bedrock AgentCore Gateway 调用，匹配的 A2A agent 则在 Amazon Bedrock AgentCore runtime 上调用

示例中使用的参考架构包括 [AWS Agent Registry](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html)、[Amazon Bedrock AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)、[Amazon Bedrock AgentCore runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime.html)、Amazon Bedrock、Amazon Cognito、AWS Lambda 和 AWS Secrets Manager。

- [AWS Agent Registry](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html) 提供受治理、可搜索的目录，供编排器查询。只有完成所配置审批工作流的记录，才能通过可发现的数据平面提供。
- [Amazon Bedrock AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html) 把订单管理 Lambda 工具暴露为一个 MCP server。示例为入站 Gateway 调用配置了 [Cognito JWT](https://docs.aws.amazon.com/cognito/) 授权，并使用 Gateway 的 AWS Identity and Access Management（IAM）角色来调用 Lambda 目标。
- [Amazon Bedrock AgentCore runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime.html) 托管编排器以及 Pricing 和 Customer Support 两个 A2A agent。运行时调用使用[经 IAM 授权](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html)的 [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control.html) 调用。
- [Amazon Bedrock](https://aws.amazon.com/bedrock/) 提供编排器和 A2A agent 使用的基础模型（FM）。示例目前通过一个跨 Region 模型 ID 配置 Anthropic Claude Sonnet 模型。请参阅 [Amazon Bedrock 中各 AWS Region 支持的模型](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html)。

三个演示场景以不同的能力组合检验发现循环。第一个是仅 MCP 的调用（订单状态）。第二个串联 MCP + A2A（定价与折扣）。第三个针对模糊的用户意图测试纯粹的语义匹配：退货与退款，而这两个词并不出现在匹配到的 A2A agent 名称中。

## 技术实现

链接的运行时发现[示例](https://github.com/ach1ntya/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastructure/03-registry/03-advanced/discovery-and-invocation-at-runtime)会部署依赖项、创建并填充 Registry、验证发现、部署编排器，并运行三个演示。[orchestrator_agent.py](https://github.com/ach1ntya/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastructure/03-registry/03-advanced/discovery-and-invocation-at-runtime)包含逐请求的发现循环。[utils.py](https://github.com/ach1ntya/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastructure/03-registry/03-advanced/discovery-and-invocation-at-runtime)解析 Registry 描述符并创建 MCP 和 A2A 客户端。[cleanup.py](https://github.com/ach1ntya/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastructure/03-registry/03-advanced/discovery-and-invocation-at-runtime)删除资源。

### 1. 注册模型

一条 Registry 记录包含一个可搜索的描述和一个协议特定的描述符。示例使用 Agent Registry 控制平面客户端进行 Registry 和记录的生命周期操作，并使用 Agent Registry 数据平面客户端进行运行时发现。

创建一个采用手动审批和 IAM 授权的 Registry。

```
registry_client = session.client("agent-registry-control")
dp_client = session.client("agent-registry")
reg = registry_client.create_registry(
    name="OrderManagementRegistry",
    description=(
        "Registry for Order Management & Customer Service — "
        "agent discovers tools and agents via semantic search"
    ),
    approvalConfiguration={"autoApprovalRules": []},
)
REGISTRY_ARN = reg["registryArn"]
REGISTRY_ID = REGISTRY_ARN.split("/")[-1]
```

创建记录时 `recordType` 字段是必填的。在本示例中，MCP server 使用 `recordType="MCP"`，由 A2A 支持的 agent 使用 `recordType="AGENT"`。协议元数据存储在 `descriptors` 对象中的 `mcpServer` 或 `a2aAgentCard` 下。MCP 描述符包含 server 元数据和工具定义。A2A 描述符包含 agent card。描述符包含连接元数据，但不包含消费方在调用该能力时必须出示的凭证。

为 MCP 和 A2A 记录构建当前公共 SDK 的描述符结构。

```
# MCP descriptor
mcp_descriptors = {
    "mcpServer": {
        "data": json.dumps(server_metadata),
        "dataSchemaVersion": "2025-12-11",
        "additionalData": {
            "tools": {
                "data": json.dumps({"tools": tool_schemas}),
                "dataSchemaVersion": "2025-06-18",
            }
        },
    }
}

# A2A descriptor
a2a_descriptors = {
    "a2aAgentCard": {
        "data": json.dumps(agent_card),
        "dataSchemaVersion": "0.3",
    }
}
```

请用面向用户的语言撰写描述，使该能力能与相邻记录区分开。描述符内容提供协议特定的 server、工具或 agent card 数据。搜索质量应使用有代表性的查询来评估。本文并不假定目录增长会自动改善排序。

使用当前控制平面结构创建一条 Registry 记录。

```
descriptors = (
    mcp_descriptors
    if cfg["protocol"] == "MCP"
    else a2a_descriptors
)

response = registry_client.create_registry_record(
    registryId=REGISTRY_ID,
    name=name,
    description=cfg["description"],
    recordType=cfg["protocol"],
    descriptors=descriptors,
    recordVersion="1.0",
)
record_id = response["recordId"]
```

### 2. 审批工作流

在 `autoApproval` 设为 false 时，新记录必须从 `DRAFT` 转到 `PENDING_APPROVAL`，然后再转到 `APPROVED`。提交和状态更新操作都[经 IAM 授权](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html)，从而可以把发布者权限与审批者权限分开。只有已批准的记录才会由可发现的 Registry 数据平面返回。

*两步审批状态转换。*

```
record = registry_client.get_registry_record(
    registryId=REGISTRY_ID,
    recordId=record_id,
)
if record["status"] == "DRAFT":
    registry_client.submit_registry_record_for_approval(
        registryId=REGISTRY_ID,
        recordId=record_id,
    )
    registry_client.update_registry_record_status(
        registryId=REGISTRY_ID,
        recordId=record_id,
        status="APPROVED",
        statusReason="Approved",
    )
```

### 3. 发现层

数据平面客户端支持在可发现记录之间进行[混合关键词与语义搜索](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html)。最新的方法名是 [search_discoverable_registry_records](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/agent-registry.html)。结果会暴露规范化的记录字段和可发现的描述符。它们不会暴露该能力的调用凭证。

跨协议搜索已批准、可发现的记录。

```
response = dp_client.search_discoverable_registry_records(
    registryIds=[REGISTRY_ARN],
    searchQuery=query,
    maxResults=3,
)
records = response.get("registryRecords", [])
```

在示例场景中，一个退货退款查询会检索到 Customer Support Agent，因为其描述涵盖了该意图。请把这视为一个演示结果，而不是“目录越大排序就越好”的普遍论断。

### 4. 编排器

编排器是一个部署到 [Amazon Bedrock AgentCore runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime.html) 的 [Strands agent](https://strandsagents.com/latest/)。它暴露 `discover_and_execute`，该方法搜索 Registry、解析每个返回的描述符、创建相应的 [MCP](https://modelcontextprotocol.io/) 或 [A2A](https://a2a-protocol.org/latest/) 客户端，并仅用这些被发现的能力构建一个请求作用域的内部 agent。

![The orchestrator’s per-request flow, where an outer agent searches the Registry and assembles a request-scoped inner agent from the results](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21108-3-1.png)

图 3：编排器的逐请求流程。外层 agent 把用户请求转换为一次 Registry 搜索。内部 agent 由搜索结果组装而成，并在该轮结束时拆除

`discover_and_execute` 的核心可以放在一个代码块里：

*编排器的发现/实例化/执行循环。*

```
​​​@tool 
 def discover_and_execute(request: str) -> str: 
     records = dp_client.search_discoverable_registry_records( 
         registryIds=[REGISTRY_ARN], 
         searchQuery=request, 
         maxResults=5, 
     ).get("registryRecords", []) 
  
    # Registry returns descriptors, not invocation credentials. 
     oauth_token = fetch_oauth_token_from_config() 
     mcp_clients, a2a_tools = [], [] 
     for record in records: 
         metadata = parse_server_metadata(record) 
         if metadata["protocol"] == "MCP": 
             mcp_clients.append( 
                 create_mcp_client_from_metadata(metadata, oauth_token) 
             ) 
         elif metadata["protocol"] == "A2A": 
             a2a_tools.append( 
                 create_a2a_tool_from_metadata(metadata, session, REGION) 
             ) 
  
    return run_request_scoped_agent(request, mcp_clients, a2a_tools)​​ 

​​model = BedrockModel(model_id=MODEL_ID, region_name=REGION) 
​    started_clients = [] 
​    try: 
​        mcp_tools = [] 
​        for c in mcp_clients: 
​            c.start() 
​            started_clients.append(c) 
​            mcp_tools.extend(c.list_tools_sync()) 

​ 	    ##agent compiled in realtime within agent 
​        sub_agent = Agent( 
​            model=model, 
​            tools=mcp_tools + a2a_tools, 
​            system_prompt=( 
​                "You are an Order Management & Customer Service assistant. " 
​                "Use the RIGHT tool for each request:\\n" 
​                "- Order lookups, status, cancellations, address changes: use MCP tools\\n" 
​                "- Pricing, discounts, promo codes: use the pricing_agent tool\\n" 
​                "- Returns, refunds, complaints, escalations: use the customer_support_agent tool\\n" 
​                "Always use the most specific tool for the task." 
​            ), 
​        ) 
​        return str(sub_agent(request)) 
​    finally: 
​        for c in started_clients: 
​            try: 
​                c.stop() 
​            except Exception: 
​                pass​ 
```

示例会并行发起多个搜索查询，以提升其订单管理领域的召回率，对记录去重，并在请求结束后拆除 MCP 客户端。这种并行发起是示例特有的编排选择，并不是 Registry 的要求。身份验证仍留在发现之外：Gateway 的 OAuth token 从 [Cognito](https://docs.aws.amazon.com/cognito/) 配置和 [Secrets Manager](https://docs.aws.amazon.com/secretsmanager/) 获取，而 A2A 运行时调用则通过 [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control.html) 会话签名。

### 5. 运行三个演示

每个演示都检验发现循环的一种不同形态。

#### 演示 1：订单状态（仅 MCP）

*一个解析为单次 MCP 工具调用的请求。*

```
result = invoke_orchestrator(
    "What is the current status and tracking info for order 123?",
    agentcore_client, orchestrator_arn,
)
```

Registry 返回订单管理 MCP server。编排器通过 Gateway 调用 `get_order_status`，LLM 综合出人类可读的响应，内部 agent 随即终止。本轮不涉及 A2A。

#### 演示 2：定价与折扣（MCP + A2A）

*一个解析为多协议链路的请求。*

```
result = invoke_orchestrator(
    "Order 123 has 2x Widget Pro at $99.98. What discount tiers or "
    "promo codes can reduce the price?",
    agentcore_client, orchestrator_arn,
)
```

Registry 返回订单管理 MCP server 和定价 A2A agent：两个协议，一个自然语言查询。LLM 调用 `get_order_status` 获取订单行项目，然后在 runtime 上调用定价 agent 进行折扣分析，最后综合出一条建议。

#### 演示 3：退货与退款（语义匹配）

*一个意图并未字面出现在任何工具名称中的请求。*

```
result = invoke_orchestrator(
    "I want to return order 789 (Premium Headphones, delivered "
    "March 10). Am I eligible for a return and what is the refund "
    "amount?",
    agentcore_client, orchestrator_arn,
)
```

这个演示展示了语义发现的价值。“return refund”这一说法并没有出现在 Customer Support Agent 的注册名称中。混合搜索把它排在前面，是因为其描述涵盖了该意图。如果没有 Registry，编排器就需要硬编码“由哪个 agent 处理退货”的知识。

### 6. 可观测性

在适当的地方使用 Amazon Bedrock [AgentCore Observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html) 和 [Amazon CloudWatch](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html) 为发现和调用路径加上埋点。有用的信号包括 Registry 搜索的成功与失败、选中的记录标识符、客户端构建错误、下游调用结果、端到端 trace 关联以及应用错误。示例授予了 Amazon CloudWatch Logs 权限，但并未创建自定义指标或仪表板。生产团队应自行定义其运营模式所需的 trace、日志和告警。生产部署还应把 [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) 作为对 agent 响应的标准控制措施。

## 团队从受治理的运行时发现中获得什么

发现循环到位之后，若干此前与编排器发版耦合的能力变得彼此独立。

- 解耦发布。团队可以部署并注册自己的 MCP server、agent 和 skill。审批策略决定一条已发布的记录何时对消费方可用。
- 新批准的记录无需改动编排器代码。在这种模式下，添加一条兼容且已批准的 Registry 记录，不需要在编排器中添加工具特定的 import 或端点。对协议、身份验证设置或编排策略的更改仍可能需要更新代码或配置。
- 受治理的发现。采用手动审批时，只有经过审阅和批准的记录才可被发现。IAM 权限可以把记录发布者与审批者分开。
- 分离的身份验证。Registry 授权可以使用 IAM 或自定义 JWT。能力调用的身份验证是另一回事：示例对 Gateway 使用 Cognito OAuth，对 AgentCore runtime 使用 Boto3/IAM 签名。搜索结果不会返回这些凭证。
- 用目录搜索取代提示填充。借助混合 Registry 搜索，编排器只检索一小组候选项，而不是把整个目录放进模型上下文。搜索质量取决于描述、描述符质量、查询设计和评估。

## 何时不应使用运行时发现

运行时发现并非对每种工作负载都必要。有两种模式仍然更适合显式的构建期接线：

- 小型且稳定的目录。如果完整的能力集合很小且很少变动，显式的构建期接线可能更简单，也能避免额外的发现请求。
- 固定管道。当同样的能力总是以固定顺序运行时，把它们实现为确定性流程更直接，也能让追踪更聚焦。

## 结论

在运行时从 Registry 发现资产，使编排器对固定目录的依赖减弱。面对 AWS Agent Registry，它可以借助混合的语义与关键词搜索查找已批准的能力、解析 MCP 或 A2A 描述符，并实例化请求作用域的客户端。治理决定什么可被发现。身份验证仍然是 Registry 以及每个被调用能力各自要明确处理的问题。

AWS Agent Registry 已[正式可用](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-agent-registry-generally-available)，其能力超出这个单账户示例：

- [组织范围的发现](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html)和[跨账户共享](https://docs.aws.amazon.com/ram/latest/userguide/what-is.html)可以通过受支持的 [AWS Organizations](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html) 与共享机制，在账户边界之外暴露受治理的记录。
- [自动能力同步](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html)可以从 URL 填充受支持的描述符。该同步请求上的[凭证提供方配置](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity.html)用于获取描述符内容，它不会作为调用身份验证返回给运行时消费方。
- 审批工作流可以使用 Registry 状态 API 和 IAM 权限，把 CI 检查、安全审阅或人工审批接入 `DRAFT` → `PENDING_APPROVAL` → `APPROVED` 生命周期。
- 标签、[AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html) 支持和[基础设施即代码](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html)模式可以让 Registry 的部署和治理可重复。评估应针对组织自己的目录验证搜索相关性和调用行为。

运行[运行时发现示例](https://github.com/ach1ntya/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastructure/03-registry/03-advanced/discovery-and-invocation-at-runtime)，然后注册一个你自己的兼容 MCP server 或 agent。确认其描述符、审批状态、身份验证路径和搜索行为符合你的生产要求。

### 了解更多

- [AWS Agent Registry 正式可用公告](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-agent-registry-generally-available)
- [AWS Agent Registry 文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html)
- [Amazon Bedrock AgentCore 控制台（Registry）](https://console.aws.amazon.com/bedrock-agentcore/home)
- [AWS Agent Registry 正式可用技术博客文章](https://aws.amazon.com/blogs/machine-learning/manage-agents-tools-and-skills-at-scale-with-aws-agent-registry/)

## 关于作者
