---
vendor: aws_bedrock
title: 用 AgentCore Gateway 和 MCP 构建多账户 AI 智能体
original_title: Build a multi-account AI agent with AgentCore Gateway and MCP
url: https://aws.amazon.com/blogs/machine-learning/build-a-multi-account-ai-agent-with-agentcore-gateway-and-mcp
date: 2026-09-24
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

企业越来越希望 AI 智能体能对分散在多个 AWS 账户中的数据推理，而无需复制或集中它。每个团队把数据留在自己的账户里自有其充分理由：清晰的归属、范围隔离和独立的部署生命周期。但一个只看到一个账户数据的智能体价值有限，而把它连接到分散的数据源通常意味着复制数据或理清跨账户的 [AWS Identity and Access Management (IAM)](https://aws.amazon.com/iam/)。目标是让数据留在它原本所在的地方——在每个业务线（LOB）账户里。只有在查询时才流出某个请求所需的特定数据，因此底层数据集不会离开它们所属的账户。

在本文中，你要构建一个多账户架构：把每个团队的数据留在自己的账户中，同时用 [Amazon Bedrock AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html) 和 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 给智能体一个跨这些账户查询的统一方式。[Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) 是一个智能体服务，用于安全、大规模地构建、部署和运营高效的智能体。一个中心的平台账户承载智能体层以及通过 Amazon Bedrock 的大语言模型（LLM）推理。LOB 团队把他们的数据和工具以 MCP server 的形式暴露出来，而平台账户的 AgentCore Gateway 为智能体提供一个单一端点，用于跨已注册 LOB 的工具发现与调用。在此过程中，你会设置跨账户的 MCP 集成、用 Amazon Bedrock AgentCore 的一项能力 [AgentCore Identity](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity.html) 以及 [Okta](https://www.okta.com/) 进行认证、用 AgentCore 中的 Policy 做细粒度授权，以及支撑生产就绪的治理控制。

## 方案概览

该架构遵循一个多账户模型，含三层：一个中心的平台账户、分散的 LOB 账户，以及作为连接它们的集成层的 AgentCore Gateway。

### 平台账户——智能体控制面

平台团队拥有平台账户，它在 [AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html)（Amazon Bedrock AgentCore 的一项能力）上运行智能体。AgentCore Runtime 是一个无服务器、框架无关的环境，在专用 microVM 中做会话隔离，按消费计价并内建认证。为了讲得清楚，本文使用单个智能体，但同一模式支持在平台账户中运行多个智能体。智能体连接到平台账户的 Gateway，而不是各个 LOB 的 MCP server。

LLM 推理在平台账户中通过 Amazon Bedrock 运行。平台团队控制可用的基础模型（FM），应用 [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)，并通过单一计费边界跟踪成本，从而避免在数十个 LOB 账户间管理模型配额的开销。随着需求增长，有些组织会把推理分布到几个专用的推理账户，并把 AgentCore Gateway 置于其前作为 [Inference Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-targets-inference.html)，在多个模型提供方之间路由流量，根据请求选择提供方并施加每团队限流。

平台账户中的 AgentCore Gateway 充当该智能体的唯一 MCP 端点。它把每个 LOB 账户的 MCP server 注册为一个 target，并从那一个端点提供带语义搜索的统一工具发现、通过 AgentCore Identity 的集中认证、用 [AgentCore 中的 Policy](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy.html) 的细粒度授权，以及[可观测性](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html)。

除了聚合 MCP server 并充当 Inference Gateway，AgentCore Gateway 还支持额外的[目标类型](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-supported-targets.html)，使它成为一个中心集成点。[HTTP 目标](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-targets-http.html)把 AgentCore Runtime 智能体、智能体到智能体（A2A）服务以及其他 HTTP 端点纳入同一个受治理的端点，各自通过自己的子路径寻址。平台团队还可以应用 Amazon Bedrock Guardrails 做内容安全，并配置 AgentCore 中的 Policy（[Cedar](https://www.cedarpolicy.com/)）做细粒度访问控制——两者都在 Gateway 层、在智能体代码之外强制执行。

### LOB 账户——数据与工具

各 LOB 团队不是直接暴露原始 AWS 资源（[Amazon Simple Storage Service (Amazon S3)](https://aws.amazon.com/s3/) 桶、数据库、[Amazon Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)），而是把其数据和工具封装成一个 MCP server。零售银行团队暴露 `get_balance` 和 `get_profile` 这样的工具。信贷团队提供 `get_credit_score` 和 `search_lending_policies`，其中后者通过 Amazon Bedrock Knowledge Bases 里完全托管的[检索增强生成（RAG）](https://aws.amazon.com/what-is/retrieval-augmented-generation/)能力，对银行政策 PDF 做查询。这一参考架构把一个独立的 Amazon Bedrock Knowledge Base 包在 MCP server 内，以对检索流水线做细粒度控制。对于新实现，你可以改为把一个 [Amazon Bedrock Managed Knowledge Base](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-target-connector-managed-kb.html) 作为原生连接器直接附加到 Gateway，这样智能体用标准 MCP 调用查询它，而你无需运营任何检索基础设施。

MCP server 运行在 LOB 账户的 AgentCore Runtime 上——一个无服务器、框架无关的环境，在专用 microVM 中做会话隔离、按消费计价、通过 AgentCore Identity 内建认证，并具备智能体专属的可观测性。这给了 LOB 团队对其工具面的完全所有权：他们决定暴露什么、每个工具背后运行什么业务逻辑，并能在不影响平台智能体的情况下更改实现，只要 MCP 工具接口保持一致。

### 跨账户集成：Gateway 和 Identity 连接各层

该架构遵循 hub-and-spoke 模式：每个 LOB 使用基于 Streamable HTTP 的 MCP 部署一个独立的 MCP server（spoke），而 AgentCore Gateway（hub）在单一端点后把它们聚合起来。智能体把一个 Gateway 当作一个 MCP server 连接，Gateway 在已注册的 LOB 目标之间联邦化地分发工具调用。当智能体调用某个工具时，Gateway 从 AgentCore Identity 获取 OAuth 2.0 机器到机器（M2M）凭证、把它们附加到出站请求，并把它路由到正确的 LOB MCP server；后者在处理请求前，先针对 Okta 的 OpenID Connect（OIDC）端点验证该令牌。

LOB 的数据留在自己的账户中：MCP server 只返回该工具产出的特定结果，而非原始数据集，而该结果作为上下文流入平台账户用于推理。源数据不被复制或搬迁。

图 1：带 AgentCore Gateway 和 MCP 的多账户 AI 智能体架构

下面的演练追踪用户的一个问题如何跨越账户边界、调用分散的工具并返回一个统一的答案：

- 用户通过 React webapp 登录，该应用重定向到 Okta 进行认证。
- Okta 验证用户凭证并返回一个包含身份声明（sub、groups、audience）的 JSON Web Token（JWT）。
- 用户通过 webapp 提交一个 prompt，它经由 HTTPS 到达 [Amazon CloudFront](https://aws.amazon.com/cloudfront/)。
- CloudFront 把请求转发到运行在 [Amazon Elastic Container Service (Amazon ECS)](https://aws.amazon.com/ecs/)（配合 [AWS Fargate](https://aws.amazon.com/fargate/)）上的 FastAPI 后端。
- 后端在用户输入到达智能体之前，应用 Amazon Bedrock Guardrails 对可识别个人身份信息（PII）做脱敏；并在智能体输出到达用户之前再次应用。
- 后端调用 AgentCore Runtime 上的 [Strands Agent](https://github.com/strands-agents)，在 Authorization 头中转发用户的 JWT 以传播身份。
- 智能体把 prompt 发送给 Amazon Bedrock 进行推理。基于模型的响应，智能体决定调用哪些工具。
- 智能体把用户的 JWT 转发给 AgentCore Gateway，后者用跨 LOB 目标的语义搜索做工具发现。AgentCore 中的 Policy（当某个策略引擎与 Gateway 关联时）针对 Cedar 规则评估 JWT 声明，并按用户身份、角色或动作允许或拒绝每次工具调用。因为出站调用使用 M2M，用户级的授权在 Gateway 这里执行。
- 对于被允许的调用，Gateway 从 AgentCore Identity 获取 OAuth 2.0 M2M 凭证，把它们附加到出站请求并转发到正确的 LOB MCP server。每个 LOB MCP server 在处理前先验证入站 OAuth 令牌。
- LOB MCP server 运行其工具逻辑：(a) 针对本地 [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) 表做结构化数据查询；(b) 对于 Lending & Wealth LOB，还通过 Amazon OpenSearch Serverless 索引，针对存放在 Amazon S3 中的银行政策 PDF，在 Amazon Bedrock Knowledge Bases 上执行 RAG 检索。

结果沿同一条链回流（LOB → Gateway → 智能体 → 后端），示例应用中的一个 trace 面板显示访问了哪些 LOB 以及 AgentCore 中 Policy 的拒绝。每个 LOB 运行时都验证入站 OAuth 令牌。在生产中，LOB 团队配置 `allowedWorkloadConfiguration`，把运行时调用限制为那些身份链中包含 Gateway 的请求，从而降低绕过 Gateway policy 和 Cedar 授权的直接访问风险。

Strands Agent 通过 Gateway 的 `tools/list` 方法发现 LOB 工具，并在启动时查询 [AWS Agent Registry](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html)（预览版）以发现已注册的 LOB MCP server。让一个新 LOB 上线只需添加一个 Gateway target。智能体在下一次 `tools/list` 调用时就会发现新工具。

## 技术实现

下面的小节逐层讲解架构：LOB 团队如何构建并部署 MCP server、平台团队如何配置带 OAuth 出站认证和 AgentCore 中 Policy 授权的 AgentCore Gateway，以及持续评估如何帮助智能体在工具和模型演进时保持可靠。完整实现请克隆[配套仓库](https://github.com/aws-samples/sample-amazon-bedrock-agentcore-banking-mcp-multi-account)并运行部署脚本，它在四个账户间引导 [AWS Cloud Development Kit (AWS CDK)](https://aws.amazon.com/cdk/)、配置平台和 LOB 资源、部署 MCP server 和 Gateway target，并在 CloudFront 后的 [Amazon ECS](https://aws.amazon.com/ecs/) 上启动一个 React Web 应用。

### 前提条件

配套仓库假设以下条件：

- 一个通过 [AWS Organizations](https://aws.amazon.com/organizations/) 管理的 AWS 多账户设置，平台账户和 LOB 账户在同一组织内。
- 平台账户中的 Amazon Bedrock [模型访问权限](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)。
- 在平台账户（用于智能体、Gateway 和 Registry）以及每个 LOB 账户（用于 Runtime 上的 MCP server 托管）中都配置了 AgentCore。
- 一个兼容 OIDC 的身份提供方（如 Okta、[Amazon Cognito](https://aws.amazon.com/cognito/) 或 Microsoft Entra ID），带有用于 OAuth 2.0 客户端凭证授权的 M2M 应用客户端。仓库使用 Okta。
- MCP server 将封装的 LOB 数据源（Amazon Bedrock Knowledge Bases、Amazon DynamoDB 表、Amazon S3 桶或 API 端点）。

### 在 LOB 账户中设置 MCP server

每个 LOB 团队用 [FastMCP](https://github.com/jlowin/fastmcp) 构建一个 MCP server，并使用 [AgentCore CLI](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-cli.html) 把它部署到 AgentCore Runtime，把该团队的数据以带类型化输入输出的结构化工具暴露出来。每个 LOB 团队用 `customJWTAuthorizer` 配置其服务器，针对 Okta 的 OIDC discovery 端点认证入站 OAuth 令牌，因此请求必须先出示有效令牌才能调用该 LOB 的工具。为生产加固，请在 Runtime 上把 `allowedWorkloadConfiguration` 设为 Gateway 的 Amazon Resource Name (ARN)，这会把 Gateway 配置为仅当身份链中包含该 Gateway 时才接受请求。该示例主要依赖 OAuth audience 校验作为其访问控制。添加 `allowedWorkloadConfiguration` 有助于把调用限制为经由 Gateway 到达的那些，降低绕过 Gateway policy 的直接访问风险。

这段代码展示了 Lending & Wealth LOB 的 MCP server，它把 Amazon DynamoDB 查询与 Amazon Bedrock Knowledge Bases 检索结合在一起。

```
REGION = os.environ.get("AWS_REGION", "us-east-1")
dynamodb = boto3.resource("dynamodb", region_name=REGION)
bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name=REGION)
KNOWLEDGE_BASE_ID = os.environ.get("KNOWLEDGE_BASE_ID", "")

mcp = FastMCP("lending-wealth", host="0.0.0.0", stateless_http=True)


@mcp.tool()
def get_credit_score(customer_id: str) -> dict:
    """Get credit score and contributing factors for a customer."""
    table = dynamodb.Table("CreditScores")
    resp = table.get_item(Key={"customer_id": customer_id})
    item = resp.get("Item")
    if not item:
        return {"error": f"No credit score found for customer {customer_id}"}
    return item


@mcp.tool()
def search_lending_policies(query: str) -> str:
    """Search the bank's lending policy documents for guidelines,
    eligibility criteria, and regulatory requirements."""
    if not KNOWLEDGE_BASE_ID:
        return json.dumps({"error": "KNOWLEDGE_BASE_ID not configured"})
    resp = bedrock_agent_runtime.retrieve(
        knowledgeBaseId=KNOWLEDGE_BASE_ID,
        retrievalQuery={"text": query},
        retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 5}},
    )
    chunks = []
    for r in resp.get("retrievalResults", []):
        text = r.get("content", {}).get("text", "")
        source = r.get("location", {}).get("s3Location", {}).get("uri", "")
        if text:
            chunks.append({"text": text, "source": os.path.basename(source)})
    return json.dumps({"results": chunks}, default=str)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

用 AgentCore CLI 把 MCP server 部署到 AgentCore Runtime。configure 步设置入口点和协议。deploy 步把它打包并推送：

```
# Configure the MCP server
agentcore configure \
    --entrypoint server.py \
    --name lending_wealth_mcp \
    --protocol MCP \
    --disable-memory \
    --non-interactive \
    --authorizer-config '{
      "customJWTAuthorizer": {
        "discoveryUrl": "<OKTA_DISCOVERY_URL>",
        "allowedAudience": ["lobfederation"]
      }
    }'

# Deploy to AgentCore Runtime
agentcore deploy --auto-update-on-conflict \
    --env KNOWLEDGE_BASE_ID=<your-knowledge-base-id>
```

部署后，CLI 返回一个运行时 ARN，平台团队用它把该 MCP server 注册为一个 Gateway target。

### 配置 AgentCore Gateway

在平台账户中，创建一个带 Custom JWT 授权器的 Gateway，它指向 Okta 的 OIDC discovery URL 并验证 audience（aud）声明，以限制哪些应用可以连接：

```
ctrl.update_gateway(
    gatewayIdentifier=gateway_id,
    name="lobfederation-gateway",
    protocolType="MCP",
    protocolConfiguration={
        "mcp": {
            "searchType": "SEMANTIC",
            "supportedVersions": ["2025-03-26"],
        }
    },
    authorizerType="CUSTOM_JWT",
    authorizerConfiguration={
        "customJWTAuthorizer": {
            "discoveryUrl": "https://<your-okta-domain>/oauth2/<auth-server-id>/.well-known/openid-configuration",
            "allowedAudience": ["lobfederation"],
        }
    },
)
```

对于到 LOB MCP server 的出站认证，Gateway 使用 OAuth 2.0 客户端凭证授权（M2M）。平台团队在 AgentCore Identity 中注册一个存储 Okta M2M 客户端凭证的 OAuth 凭证提供方。当 Gateway 调用某个 LOB MCP server 时，AgentCore Identity 从 Okta 获取一个新的访问令牌并把它放进 Authorization 头。注册凭证提供方并把它附加到每个 Gateway target：

```
# Register an OAuth credential provider (M2M / client_credentials)
resp = ctrl.create_oauth2_credential_provider(
    name="lobfederation-okta-m2m",
    credentialProviderVendor="CustomOauth2",
    oauth2ProviderConfigInput={
        "customOauth2ProviderConfig": {
            "oauthDiscovery": {
                "discoveryUrl": "https://<your-okta-domain>/oauth2/<auth-server-id>/.well-known/openid-configuration"
            },
            "clientId": "<M2M_CLIENT_ID>",
            "clientSecret": "<M2M_CLIENT_SECRET>",
            "clientAuthenticationMethod": "CLIENT_SECRET_BASIC",
        }
    },
)
cred_arn = resp["credentialProviderArn"]

# Create a Gateway target for the LOB MCP server with OAuth outbound auth
ctrl.create_gateway_target(
    gatewayIdentifier=gateway_id,
    name="lending-wealth",
    description="Lending & Wealth --- loans, credit scores, eligibility, policy search",
    targetConfiguration={
        "mcp": {
            "mcpServer": {
                "endpoint": f"https://bedrock-agentcore.{REGION}.amazonaws.com/runtimes/{encoded_runtime_arn}/invocations",
            }
        }
    },
    credentialProviderConfigurations=[
        {
            "credentialProviderType": "OAUTH",
            "credentialProvider": {
                "oauthCredentialProvider": {
                    "providerArn": cred_arn,
                    "scopes": ["lobfederation.invoke"],
                    "grantType": "CLIENT_CREDENTIALS",
                }
            },
        }
    ],
)
```

当某个 LOB 工具必须自行强制每用户访问（例如行级安全）时，AgentCore Identity 还提供[代表用户（OBO）令牌交换](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/on-behalf-of-token-exchange.html)，其中 Gateway 把入站的用户令牌交换成一个携带智能体和用户双方身份、下游作用域的令牌。这一实现使用 M2M，因为该示例所用的 Okta 开发者账户不支持 OBO 流程。AgentCore Gateway 也支持授权码模式和 API key。示例参见 [AgentCore Gateway 出站认证示例](https://github.com/awslabs/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastructure/01-gateway/01-attach-targets/mcp/mcp-servers/01-configure-auth)。

### 部署智能体

把 Strands 智能体部署到 AgentCore Runtime，用 Custom JWT 授权器做入站认证。部署脚本在初始部署后，通过 AgentCore 控制平面 API 应用授权器配置。在请求时，智能体把用户的 JWT 转发给 Gateway，以便 AgentCore 中的 Policy 能在路由每次工具调用前评估用户的声明：

```
{
  "agents": [
    {
      "name": "lobfederation-agent",
      "authorizerType": "CUSTOM_JWT",
      "authorizerConfiguration": {
        "customJwtAuthorizer": {
          "discoveryUrl": "https://<your-okta-domain>/oauth2/<auth-server-id>/.well-known/openid-configuration",
          "allowedAudience": ["lobfederation"]
        }
      },
      "requestHeaderAllowlist": ["Authorization"]
    }
  ]
}
```

部署后，智能体从入站请求头读取用户的 JWT 并把它传给 AgentCore Gateway。这样终端用户身份就被一路传播到 Cedar 策略引擎，而智能体无需解析或修改该令牌：

```
@app.entrypoint
def invoke(payload, context=None):
    prompt = payload.get("prompt", "Hello")

    # Read the user's JWT from inbound request headers (passed through by Runtime)
    request_headers = context.request_headers if context else {}
    user_jwt = request_headers.get("Authorization", "")

    # Connect to Gateway with the user's JWT --- Cedar evaluates per-user policies
    mcp_client = MCPClient(
        lambda: streamablehttp_client(
            url=GATEWAY_URL,
            headers={"Authorization": user_jwt},
        )
    )

    with mcp_client:
        tools = mcp_client.list_tools_sync()
        agent = Agent(model=MODEL_ID, system_prompt=SYSTEM_PROMPT, tools=tools)
        result = agent(prompt)
```

### 运营智能体

智能体部署后，平台团队通过持续评估、安全的版本上线和可观测性来保持其可靠。

#### 持续评估

在一个智能体跨许多 LOB 编排工具的多账户架构中，平台团队需要有信心：随着工具、模型和 prompt 演进，它持续正确运行。[AgentCore Evaluations](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations.html) 提供了一个托管框架，帮助在回归到达客户之前捕获它们。

在线评估用内置评估器（如 Tool Selection Accuracy、Correctness 和 Goal Success Rate）持续为实时的生产流量样本（例如 10% 的会话）打分。分数呈现在 Amazon Bedrock AgentCore 的一项能力、由 [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/) 驱动的 AgentCore Observability 仪表盘上，在质量下降时告警；若智能体已经发出 [OpenTelemetry](https://opentelemetry.io/) trace，则无需改动任何代码。这能暴露出延迟和错误率监控所漏掉的、不易察觉的退化，比如智能体把信贷查询路由到了错误的 LOB。

按需评估是面向开发和持续集成与持续交付（CI/CD）的实时 API。团队一次性定义一个评估数据集（场景配上期望响应、工具轨迹和目标断言），AgentCore Evaluations 会在每次改动时用数据集评估重放它。因为两种模式共享同样的评估器，团队在部署前把关的内容，正是它在生产中监控的内容。为了闭环，[AgentCore Optimization](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/optimization.html) 分析生产 trace 并推荐 prompt 和工具描述的改进，在其上线前经过验证。

#### 安全地做版本与上线

你在 AgentCore Runtime 上部署智能体，带有指向特定版本的端点（prod、staging、dev）。当平台团队更新智能体的 prompt 或模型时，它发布一个新版本并更新端点，而 LOB MCP server 不受影响，因为工具接口没变。在晋级某个改动前，团队可以通过 AgentCore Gateway 运行 [A/B 测试](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/ab-testing.html)，把实时流量在当前版本和候选版本之间分流。随后当结果达到统计显著性时，平台团队再晋级胜出的配置。

#### 监控与观测

AgentCore 通过 Amazon CloudWatch 和 OpenTelemetry 提供内建可观测性。平台团队监控调用延迟、错误率和 token 用量，并通过 CloudWatch 跨账户可观测性查看 LOB MCP server 的指标和日志，而无需切换账户。

## 安全、治理与成本管理

在集中智能体的同时分散数据，会产生特定的治理要求：控制谁能调用哪些工具、审计跨账户调用、强制执行负责任的 AI 政策，以及把成本归因回触发它们的 LOB。

### 最小权限访问与数据所有方批准

LOB 团队通过其 AgentCore Runtime 部署上的 JWT 授权器配置来控制谁能调用他们的 MCP server。来自平台账户 Gateway 的请求，只有在 LOB 团队已把其 MCP server 配置为接受来自平台身份提供方的令牌之后，才能到达该 LOB 的工具。这份批准独立于平台团队。即使 Gateway 添加了一个新 target，LOB MCP server 也会拒绝未认证的请求。

### AgentCore 中的 Policy 授权

Gateway 以 ENFORCE 模式运行 AgentCore 中的 Policy，在路由每次工具调用前针对用户的 JWT 声明（来自智能体转发的令牌）评估规则。AgentCore 中的 Policy 使用 Cedar 策略语言，因此规则是显式的 permit（允许）和 forbid（禁止）语句。例如，一条策略可以为所有已认证用户允许 `get_balance` 这样的只读工具，同时把 `transfer_funds` 这样的写操作限制到某个特定角色，或完全阻止 `delete_customer` 这样的破坏性操作：

```
// Permit all authenticated users to invoke read-only tools
permit(
    principal is AgentCore::OAuthUser,
    action in [
        AgentCore::Action::"retail-banking___get_customer",
        AgentCore::Action::"retail-banking___get_accounts",
        AgentCore::Action::"retail-banking___get_balance",
        AgentCore::Action::"tools/list",
        AgentCore::Action::"initialize"
    ],
    resource
);

// Block destructive operations regardless of user
forbid(
    principal,
    action == AgentCore::Action::"retail-banking___delete_customer",
    resource
);
```

因为 AgentCore 中的 Policy 使用默认拒绝（default-deny）模型，只有被显式允许的动作才会成功。这给了平台团队对智能体跨已注册 LOB 所能做之事的集中控制，同时各个 LOB 团队在 MCP server 层保留自己的授权。

### 网络连通性与 VPC 考量

这一参考实现对 AgentCore Runtime 使用默认的公有网络模式，流量通过 HTTPS 经 OAuth 走公共互联网。这适合开发但不适合生产。对于生产，AgentCore Runtime 支持通过弹性网络接口 (ENI) 做专有网络（VPC）连通以访问私有资源、通过 [AWS PrivateLink](https://aws.amazon.com/privatelink/) 上的接口 VPC 端点为到 Gateway 的私有入站，以及用 `allowedWorkloadConfiguration` 把运行时调用限制到你的 Gateway。配置步骤参见 [AgentCore Runtime 的网络连通模式](https://aws.amazon.com/blogs/networking-and-content-delivery/network-connectivity-patterns-for-agents-deployed-on-amazon-bedrock-agentcore-runtime/)和[使用接口 VPC 端点为 AgentCore Gateway 建立安全入站连通](https://aws.amazon.com/blogs/machine-learning/secure-ingress-connectivity-to-amazon-bedrock-agentcore-gateway-using-interface-vpc-endpoints/)。

### Guardrails

在平台账户中应用 Amazon Bedrock Guardrails 做内容过滤、PII 脱敏和主题限制。因为推理是集中的，一份 guardrail 配置适用于跨 LOB 工具的智能体交互。作为一种较新的选项，你可以把 Guardrails 作为策略直接应用到 AgentCore Gateway 上，这样检查在 Gateway 层、在智能体代码之外运行，覆盖经 Gateway 路由的工具和上下文源。

### 审计与合规

要启用数据平面日志，在 Gateway 上配置把日志投递到 Amazon CloudWatch Logs，它捕获工具调用和请求元数据。[AWS CloudTrail](https://aws.amazon.com/cloudtrail/) 默认捕获控制平面操作（创建和更新 gateway、runtime、target 和 policy）。要在 CloudTrail 中同时捕获单个工具调用，请使用高级事件选择器为 AgentCore Gateway 资源启用数据事件日志。要集中审计，配置一个组织级的 CloudTrail trail，把平台和 LOB 账户的日志聚合到一个专用日志账户。

### 成本归因

这一架构天然提供了成本边界。每个 LOB 的数据平面成本（Amazon DynamoDB、Amazon Bedrock Knowledge Bases、MCP server 计算）留在其自己的账户中，并直接呈现在 [AWS Cost Explorer](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-what-is.html) 里。LLM 推理和 Gateway 调用累积在平台账户。要把这些归因回发起的 LOB，智能体的执行角色带有标签（例如一个 lob 或 costCenter 标签）。在 AWS Billing 控制台激活成本分配标签后，这些标签会流入 [AWS Cost and Usage Report](https://docs.aws.amazon.com/cur/latest/userguide/what-is-cur.html) 以做按 LOB 的费用分摊。智能体的工具 trace 记录了每个 LOB 调用了哪些工具，以做按比例分配。更深入的方法参见 [Amazon Bedrock 的细粒度成本归因](https://aws.amazon.com/blogs/machine-learning/introducing-granular-cost-attribution-for-amazon-bedrock/)。

## 清理

要在部署配套仓库后避免持续产生费用，运行附带的清理脚本。它会移除跨四个账户部署的资源，包括 AgentCore 组件（智能体、Gateway、Registry、凭证提供方）、Okta 配置（授权服务器、M2M 应用客户端）、MCP server 部署、CDK 栈（Amazon DynamoDB 表、Amazon S3 桶、Amazon Elastic Container Registry 仓库、Amazon ECS 集群），以及示例数据源。

从仓库根目录运行它：

```
./cleanup.sh
```

该脚本按部署的反向顺序运行，先移除智能体和 MCP server，然后是 Gateway target 和 AgentCore 中的 Policy 配置，最后是跨全部四个账户的 CDK 基础设施栈。

## 结论

本文展示了如何构建一个多账户架构：通过 Amazon Bedrock 和 AgentCore 集中运行智能体，同时把数据分散保留在各 LOB 账户。LOB 团队把其数据以 MCP server 暴露，平台账户的 Gateway 提供一个经过认证的单一端点用于工具发现与调用，而 AgentCore 中的 Policy 在 Gateway 层强制每用户授权。这一模式自然扩展：要让一个新业务线上线，平台团队添加一个 Gateway target，智能体就在下一次调用时发现新工具。

要亲自尝试这一模式，克隆[配套仓库](https://github.com/aws-samples/sample-amazon-bedrock-agentcore-banking-mcp-multi-account)并部署这个四账户参考实现。

## 相关资源

[Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)

[将 Amazon Bedrock AgentCore 连接到跨账户知识库](https://aws.amazon.com/blogs/machine-learning/connect-amazon-bedrock-agentcore-to-cross-account-knowledge-bases/)

[革新你的 MCP 架构：通过 AgentCore Gateway 统一 MCP server](https://aws.amazon.com/blogs/machine-learning/transform-your-mcp-architecture-unite-mcp-servers-through-agentcore-gateway/)
