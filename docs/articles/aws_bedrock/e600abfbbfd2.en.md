---
vendor: aws_bedrock
title: Discover tools at runtime with AWS Agent Registry
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/discover-tools-at-runtime-with-aws-agent-registry
date: 2026-10-20
lang: en
captured: 2026-10-21
extractor: readability-v1
status: ok
body_sha: 94dad0391ace
---

## [Artificial Intelligence](https://aws.amazon.com/blogs/machine-learning/)

# Discover tools at runtime with AWS Agent Registry

Runtime discovery with AWS Agent Registry can help address a problem that agent demos might hide. Hardcoded tools work fine for a handful, start to degrade at a few dozen, and become unmanageable beyond that. Enterprise systems expose hundreds of internal APIs for pricing, support, orders, inventory, and customer data. In these systems, the model can spend more tokens disambiguating tool names than reasoning about the user’s request. Each new capability requires a code change in the orchestrator, a redeploy, and a coordinated release across teams that would much rather ship on their own cadence.

This pattern can arise across enterprise software as a service (SaaS) engagements where teams expose large internal API surfaces to agentic consumers. Build-time wiring can become a bottleneck as the catalog expands. One approach is to change how the orchestrator accesses its tools: instead of compiling every tool into the agent, the agent can discover relevant tools at runtime.

[AWS Agent Registry](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html) is a managed service for cataloging and discovering Model Context Protocol (MCP) servers, agents, and agent skills. Publishers register protocol-specific descriptors and searchable descriptions. At runtime, an orchestrator can search approved, discoverable records and use the returned endpoint and descriptor content to construct a client. Registry search results do not return the capability’s invocation credentials or authentication scheme.

This post walks through the Discover → Instantiate → Execute loop demonstrated by the refactored Python sample. The code deploys an order-management MCP server through [Amazon Bedrock AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html), a capability of Amazon Bedrock AgentCore, two agent-to-agent (A2A) agents on [AgentCore runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime.html), a Registry, and an orchestrator. The [sample directory](https://github.com/ach1ntya/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastructure/03-registry/03-advanced/discovery-and-invocation-at-runtime) contains the deployment script, orchestrator, helper modules, and cleanup script.

## Solution overview: discover, instantiate, execute

The orchestrator agent in this sample has no built-in knowledge of tools or agents.

![Comparison of hardcoded tool endpoints versus runtime discovery with AWS Agent Registry](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21108-1-1.png)

Figure 1: Without AWS Agent Registry (left), endpoints are hardcoded and adding a new agent means code changes plus redeployment. With AWS Agent Registry (right), the orchestrator discovers capabilities through semantic search and new integrations are usable after registration and approval

### Discover

The orchestrator sends a natural-language query to the AWS Agent Registry data plane. The search response includes record identity, name, description, record type, status, version, and protocol descriptors such as MCP server metadata or an A2A agent card. It does not include invocation credentials. The application must obtain and apply the appropriate credentials through a separate, trusted configuration path.

### Instantiate

For each returned record, the orchestrator constructs a client from the descriptor type. In this sample, the registered MCP server represents tools that were first added as targets to Amazon Bedrock AgentCore Gateway. The MCP descriptor therefore points to the Gateway endpoint. The orchestrator fetches a [Cognito OAuth](https://docs.aws.amazon.com/cognito/) access token separately and uses it when creating the `MCPClient`. A2A records contain an agent card whose URL identifies an AgentCore runtime endpoint. The wrapper invokes that runtime through the [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/agent-registry.html) data-plane client, which signs the request with the caller’s AWS credentials. Registry discovery supplies connection metadata, not the authentication material.

### Execute

An ephemeral inner agent is built with only the dynamically-discovered tools. The large language model (LLM) picks the right one(s) for the request, and the result is synthesized back to the user. After the turn finishes, the inner agent and its clients are torn down. The next request gets a fresh search and a fresh tool set.

![End-to-end architecture: the orchestrator queries AWS Agent Registry, then invokes MCP servers through AgentCore Gateway and A2A agents on AgentCore runtime](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21108-2-1.png)

Figure 2: End-to-end architecture. A single orchestrator on Amazon Bedrock AgentCore runtime queries AWS Agent Registry. Matched MCP servers are invoked through Amazon Bedrock AgentCore Gateway, and matched A2A agents are invoked on Amazon Bedrock AgentCore runtime

The reference architecture used in the sample includes [AWS Agent Registry](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html), [Amazon Bedrock AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html), [Amazon Bedrock AgentCore runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime.html), Amazon Bedrock, Amazon Cognito, AWS Lambda, and AWS Secrets Manager.

- [AWS Agent Registry](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html) provides the governed, searchable catalog queried by the orchestrator. Only records that complete the configured approval workflow are available through the discoverable data plane.
- [Amazon Bedrock AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html) exposes the order-management Lambda tools as an MCP server. The sample configures [Cognito JWT](https://docs.aws.amazon.com/cognito/) authorization for inbound Gateway calls and uses the Gateway AWS Identity and Access Management (IAM) role to invoke the Lambda target.
- [Amazon Bedrock AgentCore runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime.html) hosts the orchestrator and the Pricing and Customer Support A2A agents. Runtime invocations use [IAM-authorized](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html) [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control.html) calls.
- [Amazon Bedrock](https://aws.amazon.com/bedrock/) provides the foundation model (FM) used by the orchestrator and A2A agents. The sample currently configures an Anthropic Claude Sonnet model through a cross-Region model ID. See [Supported models by AWS Region in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html).

Three demo scenarios exercise the discovery loop with different capability combinations. The first is an MCP-only call (order status). The second chains MCP + A2A (pricing and discounts). The third tests a pure semantic match against ambiguous user intent: return and refund, where those words don’t appear in the matched A2A agent’s name.

## Technical implementation

The linked runtime-discovery [sample](https://github.com/ach1ntya/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastructure/03-registry/03-advanced/discovery-and-invocation-at-runtime) deploys the dependencies, creates and populates the Registry, verifies discovery, deploys the orchestrator, and runs three demos. [orchestrator_agent.py](https://github.com/ach1ntya/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastructure/03-registry/03-advanced/discovery-and-invocation-at-runtime) contains the per-request discovery loop. [utils.py](https://github.com/ach1ntya/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastructure/03-registry/03-advanced/discovery-and-invocation-at-runtime) parses Registry descriptors and creates MCP and A2A clients. [cleanup.py](https://github.com/ach1ntya/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastructure/03-registry/03-advanced/discovery-and-invocation-at-runtime) removes resources.

### 1. The registration model

A Registry record contains a searchable description plus a protocol-specific descriptor. The sample uses the Agent Registry control-plane client for Registry and record lifecycle operations and the Agent Registry data-plane client for runtime discovery.

Creating a Registry with manual approval and IAM authorization.

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

The `recordType` field is required when creating a record. In this sample, MCP servers use `recordType="MCP"` and A2A-backed agents use `recordType="AGENT"`. Protocol metadata is stored under `mcpServer` or `a2aAgentCard` in the `descriptors` object. An MCP descriptor contains server metadata and tool definitions. An A2A descriptor contains the agent card. The descriptors contain connection metadata but not the credentials that a consumer must present when invoking the capability.

Building current public-SDK descriptor shapes for MCP and A2A records.

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

Write descriptions in user-facing language that distinguishes the capability from neighboring records. Descriptor content supplies the protocol-specific server, tool, or agent-card data. Search quality should be evaluated with representative queries. This post does not assume that catalog growth automatically improves ranking.

Creating a Registry record with the current control-plane shape.

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

### 2. Approval workflow

With `autoApproval` set to false, a new record must move from `DRAFT` to `PENDING_APPROVAL` and then `APPROVED`. The submit and status-update actions are [IAM-authorized](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html), allowing publisher and approver permissions to be separated. Only approved records are returned by the discoverable Registry data plane.

*The two-step approval transition.*

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

### 3. The discovery layer

The data-plane client supports [hybrid keyword and semantic search](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html) across discoverable records. The latest method name is [search_discoverable_registry_records](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/agent-registry.html). Results expose normalized record fields and discoverable descriptors. They don’t expose the capability’s invocation credentials.

Searching approved, discoverable records across protocols.

```
response = dp_client.search_discoverable_registry_records(
    registryIds=[REGISTRY_ARN],
    searchQuery=query,
    maxResults=3,
)
records = response.get("registryRecords", [])
```

In the sample scenario, a return-and-refund query retrieves the Customer Support Agent because its description captures that intent. Treat this as a demo result, not a general claim that ranking improves merely because the catalog is larger.

### 4. The orchestrator

The orchestrator is a [Strands agent](https://strandsagents.com/latest/) deployed to [Amazon Bedrock AgentCore runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime.html). It exposes `discover_and_execute`, which searches the Registry, parses each returned descriptor, creates the corresponding [MCP](https://modelcontextprotocol.io/) or [A2A](https://a2a-protocol.org/latest/) client, and builds a request-scoped inner agent from only those discovered capabilities.

![The orchestrator’s per-request flow, where an outer agent searches the Registry and assembles a request-scoped inner agent from the results](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21108-3-1.png)

Figure 3: The orchestrator’s per-request flow. The outer agent translates the user request into a Registry search. The inner agent is assembled from the search results and torn down at the end of the turn

The core of `discover_and_execute` fits in a single code block:

*The orchestrator’s discover/instantiate/execute loop.*

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

The sample fans out several search queries to improve recall for its order-management domain, deduplicates records, and tears down MCP clients after the request. That fan-out is a sample-specific orchestration choice, not a Registry requirement. Authentication remains outside discovery: the Gateway OAuth token is obtained from [Cognito](https://docs.aws.amazon.com/cognito/) configuration and [Secrets Manager](https://docs.aws.amazon.com/secretsmanager/), whereas A2A runtime calls are signed through the [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control.html) session.

### 5. Running the three demos

Each demo exercises a different shape of the discovery loop.

#### Demo 1: Order status (MCP only)

*A request that resolves to a single MCP tool call.*

```
result = invoke_orchestrator(
    "What is the current status and tracking info for order 123?",
    agentcore_client, orchestrator_arn,
)
```

The Registry returns the order management MCP server. The orchestrator calls `get_order_status` through Gateway, the LLM synthesizes a human-readable response, and the inner agent terminates. No A2A involvement on this turn.

#### Demo 2: Pricing and discounts (MCP + A2A)

*A request that resolves to a multi-protocol chain.*

```
result = invoke_orchestrator(
    "Order 123 has 2x Widget Pro at $99.98. What discount tiers or "
    "promo codes can reduce the price?",
    agentcore_client, orchestrator_arn,
)
```

The Registry returns the order management MCP server and the pricing A2A agent: two protocols, one natural-language query. The LLM calls `get_order_status` to fetch line items, then calls the pricing agent on runtime for discount analysis, then synthesizes a single recommendation.

#### Demo 3: Return and refund (semantic match)

*A request whose intent is not literally present in any tool name.*

```
result = invoke_orchestrator(
    "I want to return order 789 (Premium Headphones, delivered "
    "March 10). Am I eligible for a return and what is the refund "
    "amount?",
    agentcore_client, orchestrator_arn,
)
```

This demo shows the value of semantic discovery. The phrase ‘return refund’ doesn’t appear in the Customer Support Agent’s registered name. The hybrid search ranks it highly because its description captures the intent. Without Registry, the orchestrator would need hardcoded knowledge of which agent handles returns.

### 6. Observability

Instrument the discovery and invocation path using Amazon Bedrock [AgentCore Observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html) and [Amazon CloudWatch](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html) where appropriate. Useful signals include Registry search success and failure, selected record identifiers, client-construction errors, downstream invocation outcomes, end-to-end trace correlation, and application errors. The sample grants Amazon CloudWatch Logs permissions, but it doesn’t create custom metrics or dashboards. Production teams should define the traces, logs, and alerts required for their operating model. Production deployments should also apply [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) as a standard control on agent responses.

## What teams gain from governed runtime discovery

After the discovery loop is in place, several capabilities that were previously coupled to orchestrator releases become independent.

- Decoupled publishing. Teams can deploy and register their own MCP servers, agents, and skills. Approval policy determines when a published record becomes available to consumers.
- No orchestrator code change for newly approved records. In this pattern, adding a compatible, approved Registry record doesn’t require adding a tool-specific import or endpoint to the orchestrator. Changes to protocols, authentication setup, or orchestration policy can still require code or configuration updates.
- Governed discovery. With manual approval, only reviewed and approved records become discoverable. IAM permissions can separate record publishers from approvers.
- Separated authentication. Registry authorization can use IAM or custom JWT. Capability invocation authentication is separate: the sample uses Cognito OAuth for Gateway and Boto3/IAM signing for AgentCore runtime. Search results don’t return those credentials.
- Catalog search instead of prompt stuffing. With hybrid Registry search, the orchestrator retrieves a small candidate set instead of placing the full catalog in the model context. Search quality depends on descriptions, descriptor quality, query design, and evaluation.

## When not to use runtime discovery

Runtime discovery is not necessary for every workload. Two patterns can still favor explicit build-time wiring:

- Small, stable catalogs. If the complete capability set is small and changes rarely, explicit build-time wiring might be simpler and avoid an additional discovery request.
- Fixed pipelines. When the same capabilities always run in a fixed order, implementing them as a deterministic flow is more straightforward and keeps tracing focused.

## Conclusion

Discovery of assets from Registry at runtime makes the orchestrator less dependent on a fixed catalog. Against an AWS Agent Registry, it can search approved capabilities with hybrid semantic and keyword search, parse MCP or A2A descriptors, and instantiate request-scoped clients. Governance determines what is discoverable. Authentication remains an explicit concern for the Registry and each invoked capability.

AWS Agent Registry is [generally available](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-agent-registry-generally-available) with capabilities that extend beyond this single-account sample:

- [Organization-wide discovery](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html) and [cross-account sharing](https://docs.aws.amazon.com/ram/latest/userguide/what-is.html) can expose governed records across account boundaries through supported [AWS Organizations](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html) and sharing mechanisms.
- [Automatic capability synchronization](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html) can populate supported descriptors from a URL. [Credential-provider configuration](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity.html) on that synchronization request is used to fetch descriptor content. It isn’t returned to runtime consumers as invocation authentication.
- Approval workflows can use Registry status APIs and IAM permissions to connect CI checks, security review, or human approval to the `DRAFT` → `PENDING_APPROVAL` → `APPROVED` lifecycle.
- Tagging, [AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html) support, and [infrastructure-as-code](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html) patterns can make Registry deployment and governance repeatable. Evaluation should verify search relevance and invocation behavior for the organization’s own catalog.

Run the [runtime-discovery sample](https://github.com/ach1ntya/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastructure/03-registry/03-advanced/discovery-and-invocation-at-runtime), then register one compatible MCP server or agent of your own. Confirm that its descriptor, approval state, authentication path, and search behavior match your production requirements.

### Learn more

- [AWS Agent Registry general availability announcement](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-agent-registry-generally-available)
- [AWS Agent Registry documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/registry.html)
- [Amazon Bedrock AgentCore console (Registry)](https://console.aws.amazon.com/bedrock-agentcore/home)
- [AWS Agent Registry general availability technical blog post](https://aws.amazon.com/blogs/machine-learning/manage-agents-tools-and-skills-at-scale-with-aws-agent-registry/)

## About the authors
