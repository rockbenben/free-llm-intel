---
vendor: aws_bedrock
title: Extending MCP support for Amazon Bedrock AgentCore Gateway
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/extending-mcp-support-for-amazon-bedrock-agentcore-gateway-2
date: 2026-06-01
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 7d835c3c3c33
---

# 扩展 Amazon Bedrock AgentCore Gateway 的 MCP 支持

在生产环境部署 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/specification/2025-11-25) 服务器时，企业需要跨服务器的细粒度访问控制、能看清哪些团队在使用哪些工具的可观测性、防止数据外泄的安全保证，以及集中化的凭证管理，并且所有这些都要能在规模化场景下实现。[Amazon Bedrock AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html) 位于 MCP 服务器与使用它们的客户端之间，把凭证管理、可观测性和安全连接集中到一个可信的单一入口点。

今天，我们为 AgentCore Gateway 增加新能力，进一步加强对企业级 MCP 部署的支持。本文涵盖扩展的 [MCP 工具 schema](https://modelcontextprotocol.io/specification/2025-11-25/server/tools#data-types) 支持、作为一等原语的 [MCP prompts](https://modelcontextprotocol.io/specification/2025-11-25/server/prompts) 与 [MCP resources](https://modelcontextprotocol.io/specification/2025-11-25/server/resources)、用于在运行时发现 MCP 服务器的[动态列举](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-target-MCPservers.html#gateway-target-MCPservers-considerations)、支持有状态实时交互的流式传输与会话管理、用于在执行中途请求输入的 [elicitation](https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation)，以及用于委托式认证的 [OAuth 2.0 on-behalf-of token 交换](https://oauth.net/2/token-exchange/)。实践示例请访问 [GitHub 示例仓库](https://github.com/awslabs/agentcore-samples/tree/main/01-tutorials)。

## 通过 AgentCore Gateway 为企业统一 MCP 服务器

没有集中式网关时，组织构建的每个 MCP 服务器都必须自行处理凭证、策略执行、私有连接和日志记录。这意味着法务团队的合同审阅 MCP 服务器、财务团队的数据检索 MCP 服务器和运维团队的事件响应 MCP 服务器，各自都要承担相同的基础设施负担。安全团队逐个审核每台服务器，开发人员排队等待审批，而没有谁能统一看到 MCP 基础设施在整个组织中的使用情况。

[AgentCore Gateway](https://aws.amazon.com/blogs/machine-learning/transform-your-mcp-architecture-unite-mcp-servers-through-agentcore-gateway/) 通过建立一个所有 MCP 流量都会流经的单一入口点，帮助避免这种重复建设。下图展示了 AgentCore Gateway 支持集中治理与控制的主要特性。

![AgentCore Gateway 架构图，展示集中治理、可观测性、安全与连接性特性如何把 MCP 客户端连接到多个 MCP 服务器、REST API 和 AWS Lambda 函数。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/05/19/ML-20987-1.png)

每个团队只需为其 MCP 服务器编写业务逻辑。其余一切由 AgentCore Gateway 处理。它跨不同目标类型聚合能力，包括 [MCP 服务器](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-target-MCPservers.html)、[REST API](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-schema-openapi.html)、[AWS Lambda](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-add-target-lambda.html) 函数以及[更多类型](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-supported-targets.html)。[基于资源的策略（RBP）](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/resource-based-policies.html) 控制谁可以调用 AgentCore Gateway，例如把调用限制在某个 [Amazon Virtual Private Cloud (Amazon VPC)](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html) 内。[服务控制策略（SCP）](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html) 则管理 AgentCore Gateway 在你的 AWS 组织内如何被维护。

在网络隔离方面，[AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/vpc-interface-endpoints.html) 同时支持控制面与数据面操作的 [AWS PrivateLink](https://aws.amazon.com/privatelink/)，让流量始终留在你的 Amazon VPC 边界内。你也可以通过[托管 VPC 资源模式](https://aws.amazon.com/blogs/machine-learning/configuring-amazon-bedrock-agentcore-gateway-for-secure-access-to-private-resources/)连接到私有 API 端点或 MCP 服务器。集中化的[应用](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-gateway-metrics.html)日志与[身份](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-identity-metrics.html)日志帮助你满足审计与合规要求。

借助[拦截器](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-interceptors.html)能力，AWS Lambda 函数可以自定义请求与响应，从而实现细粒度访问控制、数据清洗、自定义授权逻辑以及[更多能力](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-interceptors-examples.html)。与 [AgentCore Policy（预览版）](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy.html) 的集成提供围绕你的工具所定义的 agentic 护栏，在集中式平面上实现确定性的策略执行。AgentCore Gateway 还帮助打通 [OAuth 2.0 授权码流程](https://aws.amazon.com/blogs/machine-learning/connecting-mcp-servers-to-amazon-bedrock-agentcore-gateway-using-authorization-code-flow/)：agent 在调用工具之前先代表用户完成认证。

接下来，我们逐一介绍新增到 AgentCore Gateway 的能力，以进一步加强企业级 MCP 支持。

## 通过单一网关暴露你的 MCP 服务器原语

AgentCore Gateway 成为一个单一的 MCP 端点，聚合组织中每台 MCP 服务器的能力。客户端只需面对一个统一的工具目录、一个 prompt 库和一个资源命名空间，而不是 20 条各自独立的连接。在底层，AgentCore Gateway 支持全部三种 MCP 原语：tools、prompts 和 resources。MCP 中的工具定义除了标准的 `name`、`icons`、`description` 和 `inputSchema`，还包含可选的 `outputSchema`（用于定义期望的输出结构）和 `annotations`（描述行为属性，例如某个工具是只读的还是破坏性的）。网关还通过完整的 MCP 方法集支持 prompts、resources 和 resource templates：`tools/list`、`tools/call`、`prompts/list`、`prompts/get`、`resources/list`、`resources/read` 和 `resources/templates/list`。下面的架构图展示了 AgentCore Gateway 如何支撑 list 与 invoke 调用。

![架构图，展示 AgentCore Gateway 把来自 MCP 客户端的 list 与 invoke 调用路由到后端 MCP 服务器目标，网关为默认模式的目标缓存 tools、prompts 和 resources。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/05/19/ML-20987-2.png)

在默认列举模式下，AgentCore Gateway 从已连接的 MCP 服务器目标发现并缓存 tools、prompts 和 resources。每次调用 [CreateGatewayTarget](https://docs.aws.amazon.com/bedrock-agentcore-control/latest/APIReference/API_CreateGatewayTarget.html) 或 [UpdateGatewayTarget](https://docs.aws.amazon.com/bedrock-agentcore-control/latest/APIReference/API_UpdateGatewayTarget.html) 时，该缓存都会被隐式刷新；你也可以用 [SynchronizeGatewayTargets](https://docs.aws.amazon.com/bedrock-agentcore-control/latest/APIReference/API_SynchronizeGatewayTargets.html) API 显式刷新。当客户端发起 `tools/list`、`prompts/list` 或 `resources/list` 等 list 调用时，AgentCore Gateway 直接从该缓存返回响应，不会调用 MCP 服务器目标。与 MCP 服务器目标的实际交互只发生在 invoke 操作期间：`tools/call`、`prompts/get` 和 `resources/read`。此时 AgentCore Gateway 才把请求路由到正确的目标。

AgentCore Gateway 返回的 tools 和 prompts 会以目标名作为前缀，格式为 `targetName___`。与 tools 和 prompts 不同，资源 URI 返回时不带目标名前缀；来自下游 MCP 服务器的原始 URI 会原样透传。创建暴露资源的 MCP 服务器目标时，你可以选择指定 `resourcePriority` 值（1–1000），以控制当多个目标暴露同一资源 URI 时 AgentCore Gateway 如何解决冲突。如果未定义优先级，则应用默认值 1000。发生冲突时，AgentCore Gateway 返回 `resourcePriority` 值最低的目标所提供的资源。如果两个冲突资源的优先级相同，则返回先同步的那个目标所提供的资源。

由于资源 URI 由下游 MCP 服务器目标提供，而 AgentCore Gateway 不会对其做校验或清洗，因此处理不受信任的目标时要格外小心。恶意或被攻陷的 MCP 服务器可能返回指向内部端点或本地文件系统路径的 URI。在跟随这些 URI 之前请先校验和清洗，不要自动抓取或渲染来自不受信任的 MCP 服务器目标的 URI。

## 动态列举带来运行时灵活性

有些 MCP 服务器会按用户个性化其能力。一个感知权限的服务器可能只向管理者暴露 `approve_expense`，而一个多租户服务器可能只向医疗行业客户提供符合 HIPAA 的工具。动态列举让你在仍经由 AgentCore Gateway 路由的同时，保留这种服务器端访问控制。

创建目标时，你可以在两种列举模式之间选择：*默认*与*动态*。在默认列举模式下，AgentCore Gateway 会在 `CreateGatewayTarget` 或 `UpdateGatewayTarget` 操作期间调用 MCP 服务器，以发现并缓存 tools、prompts 和 resources。该缓存可以用 `SynchronizeGatewayTargets` API 显式刷新。当客户端发起 list 调用时，AgentCore Gateway 直接从该缓存返回响应，不联系后端服务器。在动态列举模式下，AgentCore Gateway 不会在 `CreateGatewayTarget` 或 `UpdateGatewayTarget` 操作期间调用 MCP 服务器。相反，list 调用会在请求时实时转发给 MCP 服务器，并使用调用用户的身份。在两种模式下，`tools/call`、`prompts/get` 和 `resources/read` 等 invoke 操作都直接路由到 MCP 服务器目标。下面的架构图说明两种模式如何协同工作。

![架构图，对比 AgentCore Gateway 的默认列举模式与动态列举模式：MCP Server 1 处于动态模式，list 调用实时转发；MCP Server 2 和 3 处于默认模式，由网关缓存提供响应。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/05/19/ML-20987-3.png)

MCP Server 1 配置为动态列举模式，而 MCP Server 2 和 3 使用默认列举模式。AgentCore Gateway 的缓存中只包含默认模式服务器的能力。在 list 调用期间，响应是分页的；来自缓存的原语与 MCP Server 1 的原语会出现在不同分页上。由于动态列举目标的原语没有在 AgentCore Gateway 建立索引，因此无法使用[语义工具搜索](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-using-mcp-semantic-search.html)能力。

这种双模式架构还为多租户和细粒度访问控制（FGAC）提供了灵活性。对两种列举模式，你都可以用 AgentCore Policy 或 AWS Lambda 响应拦截器集中执行策略，按租户身份过滤能力。例如，你可以限制某个租户只看到只读工具。对于动态列举模式，你可以直接在 MCP 服务器本身管理访问控制，因为 list 操作以最终用户的身份执行，而 MCP 服务器目标只返回该用户有权访问的能力。

## 流式传输、会话管理与 elicitation

许多企业 MCP 工作流并不止于简单的请求—响应式工具调用。一台 MCP 服务器可能需要在生成报告时流式推送进度更新，在执行中途暂停以在执行敏感操作前征求用户批准，或在一段跨越多次工具调用的多步对话中保持上下文。AgentCore Gateway 支持 Streamable HTTP 传输、MCP 会话管理和 elicitation，从而支撑有状态、实时、human-in-the-loop 的交互。

### Streamable HTTP

没有流式传输时，一次耗时 45 秒的工具调用在完成前不会返回任何内容，用户只能对着转圈的加载指示器干等。有了流式传输，用户能实时看到进度事件。当客户端发送带 `Accept: application/json, text/event-stream` 的 `tools/call` 请求时，AgentCore Gateway 会打开一个 SSE 流，实时转发来自 MCP 服务器目标的事件，包括进度通知、日志消息和最终的工具结果。只发送 `Accept: application/json` 的客户端仍然会收到单个 JSON 响应，完整的向后兼容性得以保留。

![架构图，展示在一次流式工具调用期间，AgentCore Gateway 把 Server-Sent Events (SSE) 从 MCP 服务器目标转发给 MCP 客户端。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/05/19/ML-20987-4.png)

在 AgentCore Gateway 上启用响应流式传输后，响应拦截器的行为会改变，必须检查 `gatewayResponse` 中的 `isStreamingResponse` 字段，以区分流式响应和非流式响应。响应拦截器只会对包含 JSON-RPC `id` 字段的事件被调用，不会对 `notifications/progress`、`notifications/message` 和 `pings` 被调用。要启用流式传输，请在 `CreateGateway` 或 `UpdateGateway` API 调用中设置 `enableResponseStreaming` 块。

```
"protocolConfiguration": {
  "mcp": {
    "streamingConfiguration": {
      "enableResponseStreaming": true
    }
  }
}
```

在考虑 AgentCore Gateway 的流式传输用例时，请记住以下几点。AgentCore Gateway 根据流中的第一个事件来确定 HTTP 状态码。如果流中途发生错误，它会以 SSE 帧内的 JSON-RPC 错误对象形式传递，而不是作为 HTTP 状态码传递，因为状态码已经发送出去了。流开始前的错误，例如认证失败、限流或校验错误，会作为标准 JSON-RPC 错误响应返回，不带 SSE 分帧。

### 会话管理

会话管理为 AgentCore Gateway 引入有状态的多轮工作流。启用会话后，AgentCore Gateway 会在第一次 initialize 请求时生成 `Mcp-Session-Id`，并把它作为响应头返回。客户端在后续请求中携带该头，AgentCore Gateway 便能跟踪客户端交互、维护到下游 MCP 服务器会话的映射，并在多次工具调用之间关联 elicitation 请求。

要启用会话，请在 `CreateGateway` 或 `UpdateGateway` API 调用中添加 `sessionConfiguration` 块。会话超时可以配置为最短 15 分钟、最长 8 小时，默认 1 小时。

```
"protocolConfiguration": {
  "mcp": {
    "sessionConfiguration": {
      "sessionTimeoutInSeconds": 3600
    }
  }
}
```

会话的作用域限定为已认证用户。AgentCore Gateway 从授权上下文中推导用户身份——OAuth 入站使用 JWT bearer token，AWS_IAM 入站使用 IAM 凭证——并校验会话内的每个请求都来自同一用户。这有助于防止会话劫持，即某个客户端试图使用另一个客户端的会话标识符。如果启用了会话的网关收到不带 `Mcp-Session-Id` 头的请求，AgentCore Gateway 返回 HTTP 400；对于已过期或不存在的会话，返回 HTTP 404。

![架构图，展示 AgentCore Gateway 如何把客户端的 Mcp-Session-Id 映射到下游 MCP 服务器会话，并在后续工具调用中复用该映射。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/05/19/ML-20987-5.png)

在幕后，AgentCore Gateway 把会话 ID 持久化到全托管的持久存储中，以跨请求管理会话。当 AgentCore Gateway 在一个会话内首次收到针对某个 MCP 服务器目标的工具调用时，它会初始化到该目标的连接、代表客户端协商能力，并保存目标会话标识符。该会话内对同一目标的后续工具调用会复用这个映射，避免重复的初始化开销。由于这一行为，AgentCore Runtime 无需在每次请求时冷启动新的 micro-VM，从而带来更快的响应时间。

为你的 AgentCore Gateway 规划会话时，请注意以下几点。启用会话是使用 elicitation 的前提条件。如果你目前使用头部传播把 `Mcp-Session-Id` 转发给目标，就无法同时启用会话管理，因为网关需要自己掌控会话生命周期。如果下游 MCP 服务器会话在网关会话超时之前过期，网关会透明地重新初始化该目标，并继续为客户端提供服务。

### Elicitation

Elicitation 让 AgentCore Gateway 背后的 MCP 服务器能够暂停执行，并向最终用户请求输入。对于高风险操作尤其有价值：服务器在执行前需要用户明确确认、需要收集结构化数据，或需要带外认证。

AgentCore Gateway 支持以下 elicitation 模式。在*表单模式*下，MCP 服务器发送一个扁平 JSON Schema，描述它需要的字段，客户端则渲染表单供用户填写。在 *URL 模式*下，服务器发送一个 URL，由客户端为用户打开，通常是 OAuth 同意屏幕或外部审批工作流。在 *URL 异常模式*下，服务器返回包含 URL 的 `URLElicitationRequiredError`，提示客户端重定向用户，并在用户完成外部流程后重试该工具调用。

![架构图，展示经由 AgentCore Gateway 的表单模式 elicitation，包括会话初始化、tools/call 请求、MCP 服务器与客户端之间的 elicitation/create 交换，以及最终响应。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/05/19/ML-20987-6.png)

以下是经由 AgentCore Gateway 的表单模式 elicitation 的工作方式。步骤 1–6 涵盖会话初始化与工具发现。之后，客户端发送带 `Mcp-Session-Id` 头的 `tools/call` 请求。AgentCore Gateway 把该工具调用转发给 MCP 服务器目标。目标打开一个 SSE 流，并发送 `elicitation/create` 请求。AgentCore Gateway 在 SSE 流上把 `elicitation/create` 请求转发给客户端。客户端向用户呈现表单并收集响应。随后客户端使用同一个 `Mcp-Session-Id` 发送 elicitation 响应（action 为 accept 或 decline）。AgentCore Gateway 把该响应转发给 MCP 服务器目标，目标以 HTTP 202 Accepted 确认。目标带着新信息继续处理请求。

Elicitation 要求在你的网关上同时启用流式传输与会话。AgentCore Gateway 尊重能力协商：只有当连接的客户端在初始化时声明支持 elicitation，它才会向下游 MCP 服务器声明 elicitation 支持。这意味着如果客户端不支持 elicitation，MCP 服务器就不会尝试发送 elicitation 请求，从而避免意外行为。AgentCore Gateway 还支持每个会话中存在多个活跃的 elicitation，因此一个客户端可以同时有多个工具调用，各自带有待处理的 elicitation。

为你的 AgentCore Gateway 规划 elicitation 时，请注意以下几点。elicitation 超时由 AgentCore Gateway 的连接超时决定。如果用户响应表单或完成 URL 流程的时间超过连接超时，请求就会超时。对于涉及人机交互的工作流，请据此规划连接超时。如果在 elicitation 期间客户端与 AgentCore Gateway 之间的连接中断，AgentCore Gateway 不支持恢复该特定工具调用，客户端应重试最初的 `tools/call` 请求。网关仅对 MCP 服务器目标支持 elicitation 透传。对于 REST API 或 AWS Lambda 函数等非 MCP 目标类型，elicitation 不适用，因为这些目标不会发起 elicitation 请求。

## OAuth 2.0 on-behalf-of token 交换

当你的 agent 需要代表已认证用户访问下游资源时，AgentCore Gateway 通过 AgentCore Identity 支持 OAuth 2.0 on-behalf-of（OBO）token 交换。这实现了零信任认证模型：原始用户身份被保留，并在请求链的每一跳中传播，同时每一层都收到一个精确限定到其目标受众的 token。

![架构图，展示跨 MCP 客户端、AgentCore Gateway、AgentCore Identity、MCP 服务器与下游 API 的 OAuth 2.0 on-behalf-of token 交换，每一跳都会收到限定到其目标受众的 JWT。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/05/19/ML-20987-7.png)

MCP 客户端通过 `/mcp` streamable HTTP 连接，用作用域限定为网关受众（`aud: gw`）的 JWT A 向 AgentCore Gateway 认证。当 AgentCore Gateway 需要调用下游 MCP 服务器目标时，它会调用 AgentCore Identity，把 JWT A 换成现在限定为 MCP 服务器受众（`aud: mcp`）的 JWT B。如果该 MCP 服务器又需要调用更下游的 API，它可以用 `GetResourceOAuth2Token` 获得限定为下游 API 受众（`aud: api`）的 JWT C。在每一跳，原始用户身份（`sub: X`）都会向前携带，因此下游服务可以执行细粒度的按用户授权，而无需触发额外的同意流程。本流程中使用的 claims 仅用于示例目的，只应用于理解这张图。

AgentCore Identity 是整个流程的中央 token 代理。它提供安全的 token 保管库来存储 OAuth 凭证和客户端密钥，使 AgentCore Gateway 和 MCP 服务器都无需直接管理凭证；它还提供工作负载身份，用 AWS 工作负载身份而非长期有效的密钥完成服务间认证。它支持标准 token 交换（[RFC 8693](https://www.rfc-editor.org/rfc/rfc8693.html)）或 JWT 授权授予（[RFC 7523](https://www.rfc-editor.org/rfc/rfc7523.html)），具体取决于身份提供方。

## 结论

借助本次发布，你可以通过单一托管端点构建有状态的多轮 agent 工作流，具备实时进度流式推送、可暂停与恢复执行的人工审批关卡，以及零信任身份传播。无需自定义会话存储，无需自己拼凑流式基础设施，也无需共享的服务账户凭证。你的 MCP 服务器继续专注于业务逻辑。其余的事交给 AgentCore Gateway：发现、流式传输、状态、身份和策略，集中治理，且可增量采用。

要开始使用，请查阅 [Amazon Bedrock AgentCore Gateway 文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)，了解本文所涉各项功能的配置细节。实践示例请访问 [GitHub 示例仓库](https://github.com/awslabs/agentcore-samples/tree/main/01-tutorials)。如果你已经在 AgentCore Gateway 背后运行 MCP 服务器，可以增量采用这些能力，无需改动现有的 AgentCore Gateway 或目标配置。

## 关于作者
