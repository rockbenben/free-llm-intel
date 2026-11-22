---
vendor: aws_bedrock
title: Build a multi-account AI agent with AgentCore Gateway and MCP
original_title: Build a multi-account AI agent with AgentCore Gateway and MCP
url: https://aws.amazon.com/blogs/machine-learning/build-a-multi-account-ai-agent-with-agentcore-gateway-and-mcp
date: 2026-09-24
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 4b2ef793aefe
---

## [Artificial Intelligence](https://aws.amazon.com/blogs/machine-learning/)

# Build a multi-account AI agent with AgentCore Gateway and MCP

Enterprises increasingly want AI agents that can reason over data spread across many AWS accounts without copying or centralizing it. Each team keeps its data in its own account for good reasons: clear ownership, scope isolation, and independent deployment lifecycles. But an agent that sees only one account’s data delivers limited value, and connecting it to distributed sources usually means replicating data or untangling cross-account [AWS Identity and Access Management (IAM)](https://aws.amazon.com/iam). The goal is to let data stay where it already lives, in each line-of-business (LOB) account. Only the specific data a request needs flows out at query time, so the underlying datasets do not leave their owning account.

In this post, you build a multi-account architecture that keeps each team’s data in its own account while giving agents a unified way to query across them, using [Amazon Bedrock AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html) and [Model Context Protocol (MCP)](https://modelcontextprotocol.io/). [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) is an agentic service for building, deploying, and operating highly effective agents securely at scale. A central platform account hosts the agent tier and large language model (LLM) inference through Amazon Bedrock. LOB teams expose their data and tools as MCP servers, and the platform account’s AgentCore Gateway gives agents a single endpoint for tool discovery and invocation across registered LOBs. Along the way, you set up cross-account MCP integration, authentication with [AgentCore Identity](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity.html), a capability of Amazon Bedrock AgentCore, and [Okta](https://www.okta.com/), fine-grained authorization with Policy in Amazon Bedrock AgentCore, and the governance controls that support production readiness.

## Solution overview

The architecture follows a multi-account model with three layers: a central platform account, distributed LOB accounts, and AgentCore Gateway as the integration layer that connects them.

### Platform account — the agent control plane

The platform team owns the platform account, which runs the agent on [AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html), a capability of Amazon Bedrock AgentCore. AgentCore Runtime is a serverless, framework-agnostic environment with session isolation in dedicated microVMs, consumption-based pricing, and built-in authentication. To keep the walkthrough clear, this post uses a single agent, but the same pattern supports multiple agents in the platform account. The agent connects to the platform account’s Gateway rather than to individual LOB MCP servers.

LLM inference runs in the platform account through Amazon Bedrock. The platform team controls available foundation models (FMs), applies [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html), and tracks costs through a single billing boundary, avoiding the overhead of managing model quotas across dozens of LOB accounts. As demand grows, some organizations distribute inference across several dedicated inference accounts, placing AgentCore Gateway in front as an [Inference Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-targets-inference.html) that routes traffic across model providers, selecting the provider based on the request and applying per-team rate limits.

AgentCore Gateway in the platform account acts as the single MCP endpoint for the agent. It registers each LOB account’s MCP server as a target and, from that one endpoint, provides unified tool discovery with semantic search, centralized authentication through AgentCore Identity, fine-grained authorization with [Policy in AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy.html), and [observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html).

Beyond aggregating MCP servers and acting as an Inference Gateway, AgentCore Gateway supports additional [target types](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-supported-targets.html) that make it a central integration point. [HTTP targets](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-targets-http.html) bring AgentCore Runtime agents, agent-to-agent (A2A) services, and other HTTP endpoints into the same governed endpoint, each addressable through its own sub-path. The platform team can also apply Amazon Bedrock Guardrails for content safety and configure Policy in AgentCore ([Cedar](https://www.cedarpolicy.com/)) for fine-grained access control, both enforced at the Gateway layer outside the agent’s code.

### LOB accounts — data and tools

Rather than exposing raw AWS resources ([Amazon Simple Storage Service (Amazon S3)](https://aws.amazon.com/s3/) buckets, databases, [Amazon Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)) directly, each LOB team packages its data and tools as an MCP server. The retail banking team exposes tools like `get_balance` and `get_profile`. The lending team offers `get_credit_score` and `search_lending_policies`, where the latter queries the fully managed [Retrieval Augmented Generation (RAG)](https://aws.amazon.com/what-is/retrieval-augmented-generation/) capability in Amazon Bedrock Knowledge Bases over bank policy PDFs. This reference architecture wraps a standalone Amazon Bedrock Knowledge Base inside the MCP server for fine-grained control over the retrieval pipeline. For new implementations, you can instead attach an [Amazon Bedrock Managed Knowledge Base](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-target-connector-managed-kb.html) directly to the Gateway as a native connector, so agents query it with standard MCP calls and you operate no retrieval infrastructure.

The MCP server runs on AgentCore Runtime in the LOB account, a serverless, framework-agnostic environment with session isolation in dedicated microVMs, consumption-based pricing, built-in authentication through AgentCore Identity, and agent-specific observability. This gives LOB teams full ownership of their tool surface: they decide what to expose and what business logic runs behind each tool, and can change the implementation without affecting the platform agent, as long as the MCP tool interface stays consistent.

### Cross-account integration: Gateway and Identity connect the layers

This architecture follows a hub-and-spoke pattern: each LOB deploys a standalone MCP server (the spoke) using MCP over Streamable HTTP, while AgentCore Gateway (the hub) aggregates them behind a single endpoint. The agent connects to the Gateway as one MCP server, and the Gateway federates tool invocation across registered LOB targets. When the agent invokes a tool, the Gateway retrieves OAuth 2.0 machine-to-machine (M2M) credentials from AgentCore Identity, attaches them to the outbound request, and routes it to the right LOB MCP server, which authenticates the token against Okta’s OpenID Connect (OIDC) endpoint before processing the request locally.

The LOB’s data stays in its own account: the MCP server returns only the specific result the tool produced, not the raw dataset, and that result flows to the platform account as context for inference. The source data isn’t copied or relocated.

Figure 1: Multi-account AI agent architecture with AgentCore Gateway and MCP

The following walkthrough traces a user’s question as it crosses account boundaries, invokes distributed tools, and returns a unified answer:

- The user logs in through the React webapp, which redirects to Okta for authentication.
- Okta validates the user’s credentials and returns a JSON Web Token (JWT) containing identity claims (sub, groups, audience).
- The user submits a prompt through the webapp, which reaches [Amazon CloudFront](https://aws.amazon.com/cloudfront/) over HTTPS.
- CloudFront forwards the request to the FastAPI backend running on [Amazon Elastic Container Service (Amazon ECS)](https://aws.amazon.com/ecs/) with [AWS Fargate](https://aws.amazon.com/fargate/).
- The backend applies Amazon Bedrock Guardrails for personally identifiable information (PII) redaction on the user’s input before it reaches the agent, and again on the agent’s output before it reaches the user.
- The backend invokes the [Strands Agent](https://github.com/strands-agents) on AgentCore Runtime, forwarding the user’s JWT in the Authorization header for identity propagation.
- The agent sends the prompt to Amazon Bedrock for reasoning. Based on the model’s response, the agent determines which tools to invoke.
- The agent forwards the user’s JWT to AgentCore Gateway, which uses semantic search for tool discovery across LOB targets. Policy in AgentCore (when a policy engine is associated with the Gateway) evaluates the JWT claims against Cedar rules and permits or denies each tool call by user identity, role, or action. Because the outbound call uses M2M, user-level authorization is enforced here at the Gateway.
- For permitted calls, the Gateway retrieves OAuth 2.0 M2M credentials from AgentCore Identity, attaches them to the outbound request, and forwards it to the correct LOB MCP server. Each LOB MCP server validates the inbound OAuth token before processing.
- The LOB MCP server runs its tool logic: (a) against local [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) tables for structured data lookups, and (b) for the Lending & Wealth LOB, also performs RAG retrieval against Amazon Bedrock Knowledge Bases over bank policy PDFs stored in Amazon S3 with Amazon OpenSearch Serverless indexing.

Results flow back through the same chain (LOB to Gateway to Agent to backend), with a trace panel in the sample application showing which LOBs were accessed and Policy in AgentCore denials. Each LOB runtime validates the inbound OAuth token. In production, the LOB team configures `allowedWorkloadConfiguration` to restrict runtime invocation to requests whose identity chain includes the Gateway, reducing the risk of direct access that bypasses Gateway policy and Cedar authorization.

The Strands Agent discovers LOB tools through the Gateway’s `tools/list` method, and queries [AWS Agent Registry](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html) (Preview) at startup to discover registered LOB MCP servers. Onboarding a new LOB involves adding a Gateway target. The agent discovers the new tools on its next `tools/list` call.

## Technical implementation

The following sections walk through each layer of the architecture: how LOB teams build and deploy MCP servers, how the platform team configures AgentCore Gateway with OAuth outbound authentication and Policy in AgentCore authorization, and how continuous evaluation helps keep the agent reliable as tools and models evolve. For the complete implementation, clone the [accompanying repository](https://github.com/aws-samples/sample-amazon-bedrock-agentcore-banking-mcp-multi-account) and run the deployment script, which bootstraps [AWS Cloud Development Kit (AWS CDK)](https://aws.amazon.com/cdk/) across the four accounts, provisions the platform and LOB resources, deploys the MCP servers and Gateway targets, and launches a React web application on [Amazon ECS](https://aws.amazon.com/ecs/) behind CloudFront.

### Prerequisites

The accompanying repository assumes the following:

- An AWS multi-account setup managed through [AWS Organizations](https://aws.amazon.com/organizations/), with the platform and LOB accounts in the same organization.
- Amazon Bedrock [model access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html) in the platform account.
- AgentCore configured in both the platform account (for the agent, Gateway, and Registry) and each LOB account (for MCP server hosting on Runtime).
- An OIDC-compatible identity provider (such as Okta, [Amazon Cognito](https://aws.amazon.com/cognito/), or Microsoft Entra ID) with M2M app clients for the OAuth 2.0 client credentials grant. The repository uses Okta.
- LOB data sources (Amazon Bedrock Knowledge Bases, Amazon DynamoDB tables, Amazon S3 buckets, or API endpoints) that the MCP servers will wrap.

### Set up MCP servers in the LOB accounts

Each LOB team builds an MCP server with [FastMCP](https://github.com/jlowin/fastmcp) and deploys it to AgentCore Runtime using the [AgentCore CLI](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-cli.html), exposing the team’s data as structured tools with typed inputs and outputs. Each LOB team configures its server with a `customJWTAuthorizer` that authenticates inbound OAuth tokens against Okta’s OIDC discovery endpoint, so requests must present a valid token before they can invoke the LOB’s tools. For production hardening, set `allowedWorkloadConfiguration` on the Runtime to the Gateway’s Amazon Resource Name (ARN), which configures it to accept requests only when the identity chain includes that Gateway. This sample relies on OAuth audience validation as its primary access control. Adding `allowedWorkloadConfiguration` helps restrict invocations to those arriving through the Gateway, reducing the risk of direct access that bypasses Gateway policy.

This snippet shows the Lending & Wealth LOB’s MCP server, combining Amazon DynamoDB lookups with Amazon Bedrock Knowledge Bases retrieval.

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

Deploy the MCP server to AgentCore Runtime with the AgentCore CLI. The configure step sets the entrypoint and protocol. The deploy step packages and pushes it:

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

After deployment, the CLI returns a runtime ARN that the platform team uses to register the MCP server as a Gateway target.

### Configure AgentCore Gateway

In the platform account, create the Gateway with a Custom JWT authorizer that points to Okta’s OIDC discovery URL and validates the audience (aud) claim to restrict which applications can connect:

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

For outbound authentication to LOB MCP servers, the Gateway uses the OAuth 2.0 client credentials grant (M2M). The platform team registers an OAuth credential provider in AgentCore Identity that stores the Okta M2M client credentials. When the Gateway invokes a LOB MCP server, AgentCore Identity obtains a fresh access token from Okta and passes it in the Authorization header. Register the credential provider and attach it to each Gateway target:

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

When a LOB tool must enforce per-user access itself (for example, row-level security), AgentCore Identity also provides [on-behalf-of (OBO) token exchange](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/on-behalf-of-token-exchange.html), where the Gateway exchanges the inbound user token for a downstream-scoped token carrying both the agent’s and the user’s identity. This implementation uses M2M because the Okta developer account used for the sample doesn’t support the OBO flow. AgentCore Gateway also supports the authorization code grant and API keys. For examples, see the [AgentCore Gateway outbound authentication samples](https://github.com/awslabs/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastructure/01-gateway/01-attach-targets/mcp/mcp-servers/01-configure-auth).

### Deploy the agent

Deploy the Strands agent to AgentCore Runtime with a Custom JWT authorizer for inbound auth. The deployment script applies the authorizer configuration through the AgentCore control-plane API after the initial deploy. At request time, the agent forwards the user’s JWT to the Gateway so Policy in AgentCore can evaluate the user’s claims before routing each tool call:

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

After deployed, the agent reads the user’s JWT from the inbound request headers and passes it to AgentCore Gateway. This propagates the end-user identity through to the Cedar policy engine without the agent needing to parse or modify the token:

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

### Operate the agent

After the agent is deployed, the platform team keeps it reliable through continuous evaluation, safe version rollouts, and observability.

#### Evaluate continuously

In a multi-account architecture where the agent orchestrates tools across many LOBs, the platform team needs confidence that it keeps performing correctly as tools, models, and prompts evolve. [AgentCore Evaluations](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations.html) provides a managed framework that helps catch regressions before they reach customers.

Online evaluation continuously scores a sample of live production traffic (for example, 10 percent of sessions) using built-in evaluators such as Tool Selection Accuracy, Correctness, and Goal Success Rate. Scores surface in the AgentCore Observability dashboard, a capability of Amazon Bedrock AgentCore powered by [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/), with alerts when quality drops and no code changes required if the agent already emits [OpenTelemetry](https://opentelemetry.io/) traces. This can surface quiet degradations that latency and error-rate monitoring miss, such as an agent routing lending queries to the wrong LOB.

On-demand evaluation is a real-time API for development and continuous integration and continuous delivery (CI/CD). The team defines an evaluation dataset once (scenarios paired with expected responses, tool trajectories, and goal assertions), and AgentCore Evaluations replays it on every change using dataset evaluation. Because both modes share the same evaluators, what the team gates on before deployment is exactly what it monitors in production. To close the loop, [AgentCore Optimization](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/optimization.html) analyzes production traces and recommends prompt and tool-description improvements, validated before they ship.

#### Version and roll out safely

You deploy the agent on AgentCore Runtime with endpoints (prod, staging, dev) that point to specific versions. When the platform team updates the agent’s prompt or model, it publishes a new version and updates the endpoint, and LOB MCP servers are unaffected because the tool interface doesn’t change. Before promoting a change, the team can run [A/B testing](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/ab-testing.html) through AgentCore Gateway, splitting live traffic between the current and candidate versions. The platform team then promotes the winning configuration once results reach statistical significance.

#### Monitor and observe

AgentCore provides built-in observability through Amazon CloudWatch and OpenTelemetry. The platform team monitors invocation latency, error rates, and token usage, and views metrics and logs from LOB MCP servers through CloudWatch cross-account observability without switching accounts.

## Security, governance, and cost management

Centralizing the agent while distributing data creates specific governance requirements: controlling who can invoke which tools, auditing cross-account calls, enforcing responsible AI policies, and attributing costs back to the LOB that triggered them.

### Least-privilege access and data owner approval

LOB teams control who can invoke their MCP server through the JWT authorizer configuration on their AgentCore Runtime deployment. A request from the platform account’s Gateway reaches a LOB’s tools only after the LOB team has configured their MCP server to accept tokens from the platform’s identity provider. This approval is independent of the platform team. Even if the Gateway adds a new target, the LOB MCP server rejects unauthenticated requests.

### Policy in AgentCore authorization

The Gateway runs Policy in AgentCore in ENFORCE mode, evaluating rules before routing each tool call against the user’s JWT claims (from the token the agent forwards). Policy in AgentCore uses the Cedar policy language, so rules are explicit permit and forbid statements. For example, a policy can permit read-only tools like `get_balance` for all authenticated users while restricting writes like `transfer_funds` to a specific role, or block destructive operations like `delete_customer` entirely:

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

Because Policy in AgentCore uses a default-deny model, only actions with an explicit permit succeed. This gives the platform team centralized control over what the agent can do across registered LOBs, while individual LOB teams retain their own authorization at the MCP server level.

### Network connectivity and VPC considerations

This reference implementation uses the default public network mode for AgentCore Runtime, where traffic traverses the public internet over HTTPS with OAuth. This suits development but not production. For production, AgentCore Runtime supports virtual private cloud (VPC) connectivity through elastic network interfaces (ENIs) for private resource access, an interface VPC endpoint over [AWS PrivateLink](https://aws.amazon.com/privatelink/) for private ingress to the Gateway, and `allowedWorkloadConfiguration` to restrict runtime invocation to your Gateway. For configuration steps, see [network connectivity patterns for AgentCore Runtime](https://aws.amazon.com/blogs/networking-and-content-delivery/network-connectivity-patterns-for-agents-deployed-on-amazon-bedrock-agentcore-runtime/) and [secure ingress to AgentCore Gateway using interface VPC endpoints](https://aws.amazon.com/blogs/machine-learning/secure-ingress-connectivity-to-amazon-bedrock-agentcore-gateway-using-interface-vpc-endpoints/).

### Guardrails

Apply Amazon Bedrock Guardrails in the platform account for content filtering, PII redaction, and topic restrictions. Because inference is centralized, one guardrail configuration applies to agent interactions across LOB tools. As a newer option, you can apply Guardrails as policies directly on AgentCore Gateway, so checks run at the Gateway layer, outside the agent’s code, covering the tools and context sources routed through the Gateway.

### Audit and compliance

To enable data-plane logging, configure log delivery on the Gateway to Amazon CloudWatch Logs, which captures tool invocations and request metadata. [AWS CloudTrail](https://aws.amazon.com/cloudtrail/) captures control-plane operations (creating and updating gateways, runtimes, targets, and policies) by default. To also capture individual tool calls in CloudTrail, enable data event logging for AgentCore Gateway resources using an advanced event selector. For centralized audit, configure an organization-level CloudTrail trail that aggregates logs from platform and LOB accounts into a dedicated logging account.

### Cost attribution

This architecture provides natural cost boundaries. Each LOB’s data-plane costs (Amazon DynamoDB, Amazon Bedrock Knowledge Bases, MCP server compute) stay in its own account and appear directly in [AWS Cost Explorer](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-what-is.html). LLM inference and Gateway invocations accrue in the platform account. To attribute these back to the originating LOB, the agent’s execution role carries tags (for example, a lob or costCenter tag). After you activate the cost allocation tag in the AWS Billing console, these tags flow to the [AWS Cost and Usage Report](https://docs.aws.amazon.com/cur/latest/userguide/what-is-cur.html) for per-LOB chargeback. The agent’s tool trace records which tools each LOB called for proportional allocation. For a deeper approach, see [granular cost attribution for Amazon Bedrock](https://aws.amazon.com/blogs/machine-learning/introducing-granular-cost-attribution-for-amazon-bedrock/).

## Cleaning up

To avoid ongoing charges after deploying the accompanying repository, run the included cleanup script. It removes deployed resources across the four accounts, including AgentCore components (agent, Gateway, Registry, credential providers), Okta configuration (authorization server, M2M app clients), MCP server deployments, CDK stacks (Amazon DynamoDB tables, Amazon S3 buckets, Amazon Elastic Container Registry repositories, Amazon ECS clusters), and sample data sources.

Run it from the repository root:

```
./cleanup.sh
```

The script runs in reverse order of deployment, removing agent and MCP servers first, then Gateway targets and Policy in AgentCore configuration, then CDK infrastructure stacks across all four accounts.

## Conclusion

This post showed how to build a multi-account architecture that runs the agent centrally through Amazon Bedrock and AgentCore while keeping data distributed across LOB accounts. LOB teams expose their data as MCP servers, the platform account’s Gateway provides a single authenticated endpoint for tool discovery and invocation, and Policy in AgentCore enforces per-user authorization at the Gateway layer. The pattern scales naturally: to onboard a new line of business, the platform team adds a Gateway target and the agent discovers the new tools on its next invocation.

To try this pattern yourself, clone the [accompanying repository](https://github.com/aws-samples/sample-amazon-bedrock-agentcore-banking-mcp-multi-account) and deploy the four-account reference implementation.

## Related resources

[Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)

[Connect Amazon Bedrock AgentCore to cross-account knowledge bases](https://aws.amazon.com/blogs/machine-learning/connect-amazon-bedrock-agentcore-to-cross-account-knowledge-bases/)

[Transform your MCP architecture: Unite MCP servers through AgentCore Gateway](https://aws.amazon.com/blogs/machine-learning/transform-your-mcp-architecture-unite-mcp-servers-through-agentcore-gateway/)

## About the authors
