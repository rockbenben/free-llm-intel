---
vendor: aws_bedrock
title: Discover tools at runtime with AWS Agent Registry
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/discover-tools-at-runtime-with-aws-agent-registry
date: 2026-10-20
lang: zh
captured: 2026-10-23
extractor: readability-v1
translator: mt
status: translated
body_sha: ddd32a563529
---

## [人工智能](https://aws.amazon.com/blogs/machine-learning/)

# 使用 AWS Agent Registry 在运行时发现工具

使用 AWS Agent Registry 进行运行时发现可以帮助解决代理演示可能隐藏的问题。硬编码工具对于少数人来说工作得很好，在几十人身上就开始退化，超过这个数量就变得难以管理。企业系统公开数百个内部 API，用于定价、支持、订单、库存和客户数据。在这些系统中，模型可以花费更多的令牌来消除工具名称的歧义，而不是推理用户的请求。每项新功能都需要在编排器中进行代码更改、重新部署以及跨团队协调发布，而团队更愿意按照自己的节奏进行发布。

这种模式可能出现在企业软件即服务 (SaaS) 活动中，团队将大型内部 API 界面暴露给代理消费者。随着目录的扩展，构建时布线可能会成为瓶颈。一种方法是改变协调器访问其工具的方式：代理可以在运行时发现相关工具，而不是将每个工具编译到代理中。

[AWS Agent Registry](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html) 是一项托管服务，用于编目和发现模型上下文协议 (MCP) 服务器、代理和代理技能。发布者注册特定于协议的描述符和可搜索的描述。在运行时，编排器可以搜索已批准的、可发现的记录，并使用返回的端点和描述符内容来构建客户端。注册表搜索结果不会返回功能的调用凭据或身份验证方案。

本文将介绍重构的 Python 示例演示的发现 → 实例化 → 执行循环。该代码通过 [Amazon Bedrock AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html) 部署订单管理 MCP 服务器、Amazon Bedrock AgentCore 的功能、[AgentCore 运行时](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime.html) 上的两个代理到代理 (A2A) 代理、一个注册表和一个协调者。 [示例目录](https://github.com/ach1ntya/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastruct/03-registry/03-advanced/discovery-and-inplication-at-runtime)包含部署脚本、orchestrator、帮助程序模块和清理脚本。

## 解决方案概述：发现、实例化、执行

此示例中的协调器代理没有内置的工具或代理知识。

![硬编码工具端点与使用 AWS Agent Registry 进行运行时发现的比较](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21108-1-1.png)

图 1：如果没有 AWS Agent Registry（左），端点将被硬编码，添加新代理意味着代码更改和重新部署。借助 AWS Agent Registry（右），编排器可以通过语义搜索发现功能，并且在注册和批准后即可使用新的集成

### 发现

编排器将自然语言查询发送到 AWS Agent Registry 数据平面。搜索响应包括记录标识、名称、描述、记录类型、状态、版本和协议描述符（例如 MCP 服务器元数据或 A2A 代理卡）。它不包括调用凭据。应用程序必须通过单独的可信配置路径获取并应用适当的凭据。

### 实例化

对于每个返回的记录，编排器根据描述符类型构造一个客户端。在此示例中，注册的 MCP 服务器代表首先作为目标添加到 Amazon Bedrock AgentCore Gateway 的工具。因此，MCP 描述符指向网关端点。协调器单独获取 [Cognito OAuth](https://docs.aws.amazon.com/cognito/) 访问令牌，并在创建“MCPClient”时使用它。 A2A 记录包含一个代理卡，其 URL 标识 AgentCore 运行时端点。包装器通过 [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/agent-registry.html) 数据平面客户端调用该运行时，该客户端使用调用者的 AWS 凭证对请求进行签名。注册表发现提供连接元数据，而不是身份验证材料。

### 执行

仅使用动态发现的工具构建临时内部代理。大语言模型 (LLM) 为请求选择正确的模型，并将结果合成回给用户。回合结束后，内部代理及其客户将被拆除。下一个请求将获得新的搜索和新的工具集。

![端到端架构：编排器查询AWS代理注册表，然后通过AgentCore网关和AgentCore上的A2A代理调用MCP服务器运行时](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21108-2-1.png)

图 2：端到端架构。 Amazon Bedrock AgentCore 运行时上的单个编排器查询 AWS 代理注册表。匹配的 MCP 服务器通过 Amazon Bedrock AgentCore Gateway 调用，匹配的 A2A 代理在 Amazon Bedrock AgentCore 运行时调用

示例中使用的参考架构包括 [AWS Agent Registry](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html)、[Amazon Bedrock AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)、[Amazon Bedrock AgentCore运行时](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime.html)、Amazon Bedrock、Amazon Cognito、AWS Lambda 和 AWS Secrets Manager。

- [AWS Agent Registry](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html) 提供编排器查询的受管控、可搜索目录。只有完成配置的审批工作流程的记录才可通过可发现的数据平面获得。
- [Amazon Bedrock AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html) 将订单管理 Lambda 工具公开为 MCP 服务器。该示例为入站网关调用配置 [Cognito JWT](https://docs.aws.amazon.com/cognito/) 授权，并使用网关 AWS Identity and Access Management (IAM) 角色来调用 Lambda 目标。
- [Amazon Bedrock AgentCore 运行时](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime.html) 托管协调器以及定价和客户支持 A2A 代理。运行时调用使用 [IAM 授权](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html) [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control.html) 调用。
- [Amazon Bedrock](https://aws.amazon.com/bedrock/) 提供编排器和 A2A 代理使用的基础模型 (FM)。该示例当前通过跨区域模型 ID 配置 Anthropic Claude Sonnet 模型。请参阅 [Amazon Bedrock 中 AWS 区域支持的模型](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html)。

三个演示场景使用不同的功能组合来练习发现循环。第一个是仅 MCP 调用（订单状态）。第二个连锁MCP + A2A（定价和折扣）。第三个测试针对模糊的用户意图测试纯语义匹配：退货和退款，其中这些词不会出现在匹配的 A2A 代理的名称中。

## 技术实现

链接的运行时发现[示例](https://github.com/ach1ntya/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastruct/03-registry/03-advanced/discovery-and-inspiration-at-runtime)部署依赖项、创建和填充注册表、验证发现、部署协调器并运行三个演示。 [orchestrator_agent.py](https://github.com/ach1ntya/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastruct/03-registry/03-advanced/discovery-and-inspiration-at-runtime)包含每个请求的发现循环。 [utils.py](https://github.com/ach1ntya/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastruct/03-registry/03-advanced/discovery-and-inplication-at-runtime) 解析注册表描述符并创建 MCP 和 A2A 客户端。 [cleanup.py](https://github.com/ach1ntya/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastruct/03-registry/03-advanced/discovery-and-inplication-at-runtime)删除资源。

### 1.注册模型

注册表记录包含可搜索的描述以及特定于协议的描述符。该示例使用 AgentRegistry 控制平面客户端进行注册表和记录生命周期操作，并使用 AgentRegistry 数据平面客户端进行运行时发现。

通过手动批准和 IAM 授权创建注册表。
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
创建记录时需要“recordType”字段。在此示例中，MCP 服务器使用 `recordType="MCP"`，A2A 支持的代理使用 `recordType="AGENT"`。协议元数据存储在“descriptors”对象中的“mcpServer”或“a2aAgentCard”下。 MCP 描述符包含服务器元数据和工具定义。 A2A 描述符包含座席卡。描述符包含连接元数据，但不包含使用者在调用该功能时必须提供的凭据。

为 MCP 和 A2A 记录构建当前的公共 SDK 描述符形状。
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
使用面向用户的语言编写描述，以区分该功能与相邻记录。描述符内容提供特定于协议的服务器、工具或代理卡数据。应使用代表性查询来评估搜索质量。这篇文章并不假设目录增长会自动提高排名。

使用当前控制平面形状创建注册表记录。
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
### 2. 审批流程

当“autoApproval”设置为 false 时，新记录必须从“DRAFT”移动到“PENDING_APPROVAL”，然后移动到“APPROVED”。提交和状态更新操作是 [IAM 授权](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html)，允许发布者和批准者权限分开。可发现的注册表数据平面仅返回批准的记录。

*两步审批过渡。*
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
### 3.发现层

数据平面客户端支持跨可发现记录的[混合关键字和语义搜索](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html)。最新的方法名称是 [search_discoverable_registry_records](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/agent-registry.html)。结果公开了标准化的记录字段和可发现的描述符。它们不会公开该功能的调用凭据。

跨协议搜索已批准的、可发现的记录。
```
response = dp_client.search_discoverable_registry_records(
    registryIds=[REGISTRY_ARN],
    searchQuery=query,
    maxResults=3,
)
records = response.get("registryRecords", [])
```
在示例场景中，退货和退款查询会检索客户支持代理，因为其描述捕获了该意图。将此视为演示结果，而不是仅仅因为目录更大而排名提高的一般说法。

### 4. 协调者

Orchestrator 是部署到 [Amazon Bedrock AgentCore 运行时](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime.html) 的 [Strands 代理](https://strandsagents.com/latest/)。它公开了“discover_and_execute”，它搜索注册表，解析每个返回的描述符，创建相应的[MCP]（https://modelcontextprotocol.io/）或[A2A]（https://a2a-protocol.org/latest/）客户端，并仅根据这些发现的功能构建请求范围的内部代理。

![编排器的每个请求流程，其中外部代理搜索注册表并从注册表组装请求范围的内部代理结果](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21108-3-1.png)

图 3：编排器的每个请求流程。外部代理将用户请求转换为注册表搜索。内部代理根据搜索结果组装并在回合结束时拆除

`discover_and_execute` 的核心适合单个代码块：

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
该示例分散出多个搜索查询，以提高其订单管理域的召回率、删除重复记录，并在请求后拆除 MCP 客户端。该扇出是特定于示例的编排选择，而不是注册表要求。身份验证保持在发现之外：网关 OAuth 令牌是从 [Cognito](https://docs.aws.amazon.com/cognito/) 配置和 [Secrets Manager](https://docs.aws.amazon.com/secretsmanager/) 获取的，而 A2A 运行时调用是通过[boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control.html) 会话。

### 5. 运行三个演示

每个演示都练习不同形状的发现循环。

#### 演示 1：订单状态（仅限 MCP）

*解析为单个 MCP 工具调用的请求。*
```
result = invoke_orchestrator(
    "What is the current status and tracking info for order 123?",
    agentcore_client, orchestrator_arn,
)
```
注册中心返回订单管理MCP服务器。协调器通过网关调用“get_order_status”，LLM 合成人类可读的响应，然后内部代理终止。本回合没有 A2A 参与。

#### 演示 2：定价和折扣（MCP + A2A）

*解析为多协议链的请求。*
```
result = invoke_orchestrator(
    "Order 123 has 2x Widget Pro at $99.98. What discount tiers or "
    "promo codes can reduce the price?",
    agentcore_client, orchestrator_arn,
)
```
注册中心返回订单管理 MCP 服务器和定价 A2A 代理：两种协议，一种自然语言查询。 LLM 调用“get_order_status”来获取行项目，然后在运行时调用定价代理进行折扣分析，然后综合单个建议。

#### 演示3：退货和退款（语义匹配）

*其意图实际上并不存在于任何工具名称中的请求。*
```
result = invoke_orchestrator(
    "I want to return order 789 (Premium Headphones, delivered "
    "March 10). Am I eligible for a return and what is the refund "
    "amount?",
    agentcore_client, orchestrator_arn,
)
```
该演示展示了语义发现的价值。 “退货退款”一词不会出现在客户支持代理的注册名称中。混合搜索对其排名很高，因为它的描述抓住了意图。如果没有注册表，编排器将需要硬编码了解哪个代理处理退货。

### 6.可观察性

在适当的情况下，使用 Amazon Bedrock [AgentCore Observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html) 和 [Amazon CloudWatch](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html) 检测发现和调用路径。有用的信号包括注册表搜索成功和失败、选定的记录标识符、客户端构造错误、下游调用结果、端到端跟踪关联和应用程序错误。该示例授予 Amazon CloudWatch Logs 权限，但不创建自定义指标或控制面板。生产团队应定义其操作模型所需的跟踪、日志和警报。生产部署还应应用 [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) 作为对代理响应的标准控制。

## 团队从受控运行时发现中获得什么

发现循环到位后，之前与 Orchestrator 版本耦合的多项功能将变得独立。

- 解耦的发布。团队可以部署和注册自己的 MCP 服务器、代理和技能。批准策略决定发布的记录何时可供消费者使用。
- 新批准的记录无需更改协调器代码。在此模式中，添加兼容的、经批准的注册表记录不需要向编排器添加特定于工具的导入或端点。协议、身份验证设置或编排策略的更改仍然可能需要代码或配置更新。
- 受控发现。通过手动批准，只有经过审核和批准的记录才能被发现。 IAM 权限可以将记录发布者与审批者分开。
- 单独的身份验证。注册中心授权可以使用IAM或自定义JWT。功能调用身份验证是单独的：示例使用 Cognito OAuth 作为网关，使用 Boto3/IAM 签名作为 AgentCore 运行时。搜索结果不会返回这些凭据。
- 目录搜索而不是提示填充。通过混合注册表搜索，协调器会检索一个小的候选集，而不是将完整的目录放入模型上下文中。搜索质量取决于描述、描述符质量、查询设计和评估。

## 何时不使用运行时发现

运行时发现并不是每个工作负载都必需的。有两种模式仍然有利于显式构建时连接：

- 小而稳定的目录。如果完整的功能集很小并且很少更改，则显式构建时连接可能会更简单，并且可以避免额外的发现请求。
- 固定管道。当相同的功能始终以固定的顺序运行时，将它们实现为确定性流程会更加简单，并且可以保持跟踪重点。

## 结论

在运行时从注册表中发现资产可以减少编排器对固定目录的依赖。针对 AWS 代理注册表，它可以通过混合语义和关键字搜索来搜索批准的功能，解析 MCP 或 A2A 描述符，并实例化请求范围内的客户端。治理决定什么是可发现的。身份验证仍然是注册表和每个调用的功能的明确关注点。

AWS Agent Registry 已[普遍可用](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-agent-registry-generally-available)，其功能超出了此单账户示例：

- [组织范围的发现](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html) 和[跨账户共享](https://docs.aws.amazon.com/ram/latest/userguide/what-is.html) 可以通过受支持的 [AWS] 跨账户边界公开受管记录组织](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html) 和共享机制。
- [自动功能同步](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html) 可以从 URL 填充支持的描述符。该同步请求上的[凭据提供程序配置](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity.html) 用于获取描述符内容。它不会作为调用身份验证返回给运行时使用者。
- 审批工作流程可以使用注册表状态 API 和 IAM 权限将 CI 检查、安全审查或人工审批连接到“DRAFT”→“PENDING_APPROVAL”→“APPROVED”生命周期。
- 标记、[AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html) 支持和[基础设施即代码](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html) 模式可以使注册表部署和治理可重复。评估应验证组织自己的目录的搜索相关性和调用行为。

运行 [runtime-discovery 示例](https://github.com/ach1ntya/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastruct/03-registry/03-advanced/discovery-and-inspiration-at-runtime)，然后注册您自己的一台兼容的 MCP 服务器或代理。确认其描述符、批准状态、身份验证路径和搜索行为符合您的生产要求。

### 了解更多

- [AWS Agent Registry 全面可用性公告](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-agent-registry-generally-available)
- [AWS 代理注册表文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html)
- [Amazon Bedrock AgentCore 控制台（注册表）](https://console.aws.amazon.com/bedrock-agentcore/home)
- [AWS Agent Registry 全面可用性技术博客文章](https://aws.amazon.com/blogs/machine-learning/manage-agents-tools-and-skills-at-scale-with-aws-agent-registry/)

## 关于作者
