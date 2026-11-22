---
vendor: aws_bedrock
title: Migrate agentic workloads to Amazon Bedrock AgentCore
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/migrate-agentic-workloads-to-amazon-bedrock-agentcore
date: 2026-09-03
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 8cd1b203d52e
---

# Migrate agentic workloads to Amazon Bedrock AgentCore

An agent that works in a notebook isn’t an agent in production. After real users arrive, you own work that has nothing to do with your agent’s reasoning. Keep one user’s session out of another’s, and hold state across turns and days. Auth for every tool the agent calls sits in your code, and the operating system underneath needs patching. Those are four of the ten operational burdens this post maps.

When the agent reaches production, add Amazon Bedrock Guardrails to filter harmful content, validate grounding against your source documents, and block prompt injection attempts. Those controls apply to any agent regardless of which stage you stop at.

This post starts from an agent you already have. It’s a [LangGraph](https://langchain-ai.github.io/langgraph/) customer support agent that classifies each message, escalates an angry customer and answers everyone else with three tools, and its model calls already go to Amazon Bedrock. You own the container, the web server and the conversation state in the process. Inference is the one call a migration doesn’t touch, so being on Amazon Bedrock already isn’t the head start it sounds like. If your model calls go to OpenAI or Anthropic directly, one constructor changes, shown at stage 0.

In this post you move that agent in two stages. Stage 1 transitions it onto [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) Runtime, Gateway and Memory, graph unchanged. Stage 2 rebuilds the loop as model-driven planning on Strands Agents. Stop after stage 1 and you have a hosted agent with managed tools and durable state. Stage 3 hands the loop to an AgentCore harness, a capability of Amazon Bedrock AgentCore, documented here rather than built.

## Where you are

The agent in this post answers support questions. A customer asks where an order is, or how to return something, and the agent looks it up, answers what it can, and escalates what it can’t. It runs on compute you provision, patch and scale.

That last clause is what this post is about. None of it describes what the agent does.

In code the migration is bounded, and four constructs are all it touches. What you operate is the longer list, and the next section maps it.

| **LangGraph construct** | **Strands equivalent** | **AgentCore feature** |
| --- | --- | --- |
| `build_graph(...)`, plus the container and web server you run it in | `Agent(model=..., system_prompt=..., tools=...)`, callable | [Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime.html): `BedrockAgentCoreApp` and an `@app.entrypoint` function, on one microVM per session |
| `@tool` functions bound with `ToolNode(tools)` and `llm.bind_tools(tools)` | tools from `MCPClient.list_tools_sync()`, passed to `Agent(tools=...)` | [Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html): an AWS Lambda target, published as Model Context Protocol (MCP) tools named `supportTools___<name>` |
| `MemorySaver()` with `thread_id` in the invoke config | `AgentCoreMemorySessionManager(AgentCoreMemoryConfig(...))` | [Memory](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html): state keyed on `actor_id` and the session |
| `add_conditional_edges("classify_intent", route_intent)` | no equivalent: model-driven planning replaces the branch, or you keep the graph | Runtime hosts it unchanged. Nothing replaces it |

The last row answers the question “what does AgentCore take away from me”. Nothing. Runtime is where your agent runs, not what decides its next step. Losing the hand-written branch is a choice, made at stage 2.

## Solution overview

The point of moving is to shed the work that has nothing to do with your agent’s reasoning. Amazon Bedrock AgentCore is a platform to build, connect, and optimize agents at scale, with any framework or model. You attach its services one at a time, each attachment retiring specific burdens, and the following figure maps the ten onto them. Runtime takes the compute, so OS patching, auto scaling and session isolation stop being yours. By default it runs on AWS-managed infrastructure, and you can attach it to a virtual private cloud (VPC) you own. Either way you still design the network, place edge protection in front of your entry point, and decide authorization. Gateway takes tool auth and calls your function with its own execution role. Checkpoint storage goes to Memory, which holds conversation state across turns, processes and days.

AWS Identity and Access Management (IAM) policies, VPC configuration, web application firewall (WAF) rules, and secrets rotation stay yours at every stage. Dependency updates move at stage 3 and nowhere earlier.

Three more services attach without replacing anything. Identity brokers credentials and refreshes OAuth access tokens for APIs the agent calls on someone’s behalf. This walkthrough does not exercise it. The agent signs its Gateway calls with its own IAM credentials using Signature Version 4, and Gateway then invokes the AWS Lambda target under its own execution role. Nothing in that path needs a third-party token. Policy decides individual tool calls at the Gateway. Observability sends Runtime logs, metrics and traces to Amazon CloudWatch without you configuring it.

Take the stages in order. Stage 1 moves where the agent runs and changes nothing about how it thinks, which keeps one variable in play. Stage 2 moves how it plans, against a runtime you have already proved. A team rewriting the agent anyway can start at stage 2, because the gateway, target and Memory store built first serve either stage. Stage 3 is documented, not built.

![Comparison matrix titled “Migrating the sample LangGraph agent to AgentCore, stage by stage.” A subtitle states that each stage is measured for what we stopped operating and who plans the next step, and a note beneath it adds that one variable moved at a time: stage 1 moved where the agent ran, stage 2 moved how it planned. A band across the top, marked unchanged at every stage, holds the agent itself: classify, route, escalate, three tools. Four numbered stage columns are grouped under three headings. Where we started holds stage 0, self-hosted LangGraph on compute we ran and patched, marked baseline, reporting ten still ours. What this post builds, labeled with an Amazon Bedrock AgentCore icon, holds two highlighted columns: stage 1, replatform, adopting Runtime, Gateway and Memory, marked walked in this post, reporting five moved and five still ours. And stage 2, rebuild, where the loop becomes model-driven planning, also marked walked in this post, reporting the same five moved and five still ours. Beyond this post holds stage 3, hand the loop over, where AgentCore runs it, marked documented only, reporting six moved and four still ours. A row labeled who planned the next step reads our code at stage 0, our code at stage 1, the model at stage 2, and the model at stage 3. A row labeled what moves at this stage reads: nothing moved yet at stage 0, all ten ours, our router planned. Five moved to AWS at stage 1, the same five still ours, our router still planned. Nothing operational moved at stage 2, the same five still ours, the model took over planning, and stage 2 runs standalone. One more would move at stage 3, dependency updates, not built here. Ten operational burdens then run down the left as rows: VPC, WAF, IAM policies, secrets rotation, OS patching, dependency updates, auto-scaling rules, session isolation, checkpoint storage, and tool auth. Stage 0 shows a filled square on all ten. Stages 1 and 2 are identical to each other: filled circles on OS patching, auto-scaling rules, session isolation, checkpoint storage and tool auth, and filled squares on VPC, WAF, IAM policies, secrets rotation and dependency updates. Stage 3 shows filled circles on six, adding dependency updates, with VPC, WAF, IAM policies and secrets rotation the four squares left. A legend defines the two marks: a filled circle for moved to AgentCore, and a filled square for still ours to operate. A footer reads that the counts are measured from the committed sample, not asserted.](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/31/ML-20753-1.png)

Figure 1: What stops being yours to operate, and who plans the agent’s next step. Stage 1 moves the first, stage 2 moves the second

## Migration walkthrough

The [sample repository](https://github.com/aws-samples/sample-migrate-agents-to-amazon-bedrock-agentcore) is laid out as the following stages, so each stage can be compared against the one before it. The following figure is the shape of that comparison: what each stage started from, what moved, and why the next one follows. Where this post gives a count of what moved, that count is measured from the committed sample rather than estimated.

![Diagram titled “Sample migration flow, stage by stage.” A subtitle states that stages 1 and 2 are built and run in the sample. Three stacked cards read from top to bottom, joined by down arrows, and every card pairs a problem in grey with the result beneath it. The first card, stage 0, is headed the agent you already have. Its problem reads that a support agent is already answering customers, and that our team spent its week on the servers underneath it rather than on the answers it gave. Its result, in brick red, reads that we counted what we operate before touching anything: ten things, all ours, and every stage below has to beat that number. An arrow leads to the second card, stage 1, headed the same agent, replatformed, carrying an Amazon Bedrock AgentCore icon and a chip marked built and run. Its stage-level problem reads that three separate things were ours to run and none of them was the agent’s actual job, and its result, in teal, reads that we moved them one at a time and checked after each, so we could tell what each move actually bought. Four moments nest inside that card, each pairing a problem with a result the same way. Runtime: the operating system under the agent still needed patching, and that was our weekend rather than the model’s; AgentCore Runtime took over the patching and not a line of the agent changed. Gateway: only this agent could call its own tools, because the permissions lived in our code; Gateway holds those permissions now, which means the next agent gets the same tools for free. Memory: restarting the process lost the conversation and customers noticed, because they had to start over; AgentCore Memory keeps the thread now, and a different copy of the agent answered about an order it had never seen. Verify: three things had changed and nobody should take our word that it still behaved. We re-ran the same three conversations and compared, the behavior held, and five of the ten burdens are AWS’s now with five still ours. A second arrow leads to the third card, stage 2, headed rebuilding the loop because you chose to, carrying a Strands SDK icon and a chip marked built and run. Its problem reads that each new kind of question meant another branch in our router and we wrote every one of them. Its result, in teal, reads that Strands lets the model plan instead of our router, that nothing operational moved, and that we lost a branch we could audit, closing on the line that we would not call that a free upgrade. A footer reads that stage 3 hands the loop to an AgentCore harness, documented and not built.](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/31/ML-20753-2.png)

Figure 2: Where each stage started, what moved, and why the next one follows

### Prerequisites

You need an [AWS account](https://aws.amazon.com/free/) with [Amazon Bedrock](https://aws.amazon.com/bedrock/) model access enabled, [Python 3.12](https://www.python.org/), and the [AWS Command Line Interface (AWS CLI)](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) configured with credentials that can create AgentCore, Lambda, Amazon Simple Storage Service (Amazon S3) and IAM resources. Enable [CloudWatch Transaction Search](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-get-started.html) once for the account as well, or the traces this walkthrough produces cannot be viewed.

```
git clone https://github.com/aws-samples/sample-migrate-agents-to-amazon-bedrock-agentcore.git
cd sample-migrate-agents-to-amazon-bedrock-agentcore
./setup.sh
```

That creates a virtual environment and installs seven requirements. If you already run a LangGraph agent against Amazon Bedrock, the new ones are `strands-agents`, `bedrock-agentcore`, `mcp` and `langgraph-checkpoint-aws`. Two are pinned rather than floored, because an unpinned `langchain-aws` resolves higher and drags `boto3` forward with it.

Confirm the install with the test suite, which needs no credentials:

```
source .venv/bin/activate
python -m unittest discover -s tests -q
```

### Stage 0: The agent you already have

Read the agent before changing it, because its current behavior is the baseline every later stage must preserve. It’s a compiled `StateGraph`: `classify_intent` asks the model for one word, and a hand-written `route_intent` reads it. An angry customer goes to `escalate`, which returns a fixed handoff and makes no model call. Everyone else goes to `assist`, which calls the model with the tools bound:

```
builder.add_edge(START, "classify_intent")
builder.add_conditional_edges(
    "classify_intent",
    route_intent,
    {"escalate": "escalate", "assist": "assist"},
)
builder.add_edge("escalate", END)
builder.add_conditional_edges("assist", tools_condition)
builder.add_edge("tools", "assist")

return builder.compile(checkpointer=checkpointer)
```

Three tools hang off it as `@tool` functions over an HTTP backend: `lookup_order`, `process_return` and `search_faq`. They return an `{"error": ...}` payload instead of raising, because an exception inside the tool node kills the run while an error payload is something the model can act on.

State is a `MemorySaver` checkpointer keyed on a `thread_id` passed at invoke time, and it’s the one piece with a hard limit. A dictionary in the process dies with the process, and two replicas cannot see each other’s conversations. Everything else here is fine at production scale. That is not.

The model is `ChatBedrockConverse`, so inference already goes to Amazon Bedrock and stage 0 touches no AgentCore API. If you’re arriving from OpenAI or Anthropic instead, that constructor is your one change, with the model ID and AWS Region as arguments. For model availability by Region, refer to [Supported models by AWS Region in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html). Record the baseline before you move anything: which tools ran, and the final message from the graph state, not the model’s reply. That makes the next stage a comparison rather than a hope. This runs locally and creates nothing in AWS:

```
python -m examples.run_walkthrough --stage 0
```

### Stage 1: The same agent, migrated

Stage 0 left you a working agent and a recorded baseline. Stage 1 is where five of the ten burdens stop being yours, and the agent’s behavior is the thing that doesn’t change. Three things move: Runtime takes the process, two of the three tools go behind Gateway, and the conversation state lands in Memory. Inference does not move, because it was never the problem.

The migrated package doesn’t copy stage 0, it imports it:

```
from examples.stage0_langgraph.agent import build_graph
from examples.stage0_langgraph.tools import SUPPORT_TOOLS
```

Those two imports carry the graph topology, the router, the state schema, all three prompts and all three tool bodies, so none of it can drift. They also make the cost countable, measured from disk rather than asserted: **45 lines change inside the agent**, **22 lines are new supporting code the SDK doesn’t ship**, and **85 lines are imported untouched**. That 22 is small for one reason. The expensive piece used to be a hand-written LangGraph checkpointer over AgentCore Memory, and it now ships in a package, so a tool adapter is all the glue left.

#### Runtime: Hosting the loop

All ten operational burdens are still yours, and the baseline is now recorded over three turns. The machine underneath the loop moves first, because patching an operating system is not what your agent does. It is also the least code you will change for the most return: the operating system stops being yours to patch, and session isolation becomes one microVM per session. Wrap the loop you have in `BedrockAgentCoreApp` and give it an entrypoint:

```
from bedrock_agentcore import BedrockAgentCoreApp
from langchain_core.messages import HumanMessage

app = BedrockAgentCoreApp()

@app.entrypoint
def agent_invocation(payload, context):
    state = support_graph().invoke(
        {"messages": [HumanMessage(payload.get("prompt", ""))]},
        config={"configurable": {"thread_id": context.session_id or "local-session"}},
    )
    return {"result": state["messages"][-1].text}

if __name__ == "__main__":
    app.run()
```

The invoke call inside it is stage 0’s. What changed is where the `thread_id` comes from. Stage 0 chose one. Here it arrives as `context.session_id` on the `RequestContext` Runtime passes in. Build the graph once and hold it, because a per-request graph rebuilds the model client and can tear down the MCP session the tools need.

The same wrapper takes a [CrewAI](https://www.crewai.com/) or [LlamaIndex](https://www.llamaindex.ai/) loop, or one you wrote: accept a payload dict, invoke, return a dict.

#### Gateway: Publishing two of the three tools

The operating system and the compute underneath the loop have stopped being yours. Tool auth hasn’t. The reason to put a tool behind a gateway is what moves with it: auth stops being your code’s problem, and reach grows, because a published tool is [callable by your next agent](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html), where a function inside this process is only ever this agent’s. So `lookup_order` and `process_return` become MCP tools published by [AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html), a capability of Amazon Bedrock AgentCore, from a Lambda function. You register it and change no code inside it.

`search_faq` stays a local Python function through every stage, and that is the normal case rather than a compromise. A tool no other agent needs and no policy gates has nothing to gain from the trip.

Conversion is two calls on a `bedrock-agentcore-control` client. Create the gateway, choosing an `authorizerType`. `AWS_IAM` signs with credentials you have, `CUSTOM_JWT` wants a bearer token.

```
client = boto3.client("bedrock-agentcore-control", region_name=region)

gateway = client.create_gateway(
    name="MigratedAgentGateway",
    roleArn=role_arn,  # gateway execution role
    protocolType="MCP",
    authorizerType="AWS_IAM",
)
gateway_id = gateway["gatewayId"]
gateway_url = gateway["gatewayUrl"]
```

Both returned values matter later: `gateway_id` names the gateway when you register the target, and `gateway_url` is the MCP endpoint the agent connects to.

Then register a target, which is the conversion itself. Point Gateway at your function and declare its tools with a JSON schema.

```
response = client.create_gateway_target(
    gatewayIdentifier=gateway_id,
    name="supportTools",
    targetConfiguration={
        "mcp": {
            "lambda": {
                "lambdaArn": lambda_arn,
                "toolSchema": {"inlinePayload": TOOL_SCHEMA},
            }
        }
    },
    credentialProviderConfigurations=[
        {"credentialProviderType": "GATEWAY_IAM_ROLE"}
    ],
)
```

With `GATEWAY_IAM_ROLE`, Gateway calls your function as itself and passes tool arguments as the raw event, so an Amazon API Gateway handler needs adapting.

The agent discovers the tools, SigV4-signing every request:

```
import boto3
from mcp.client.streamable_http import streamablehttp_client
from strands.tools.mcp import MCPClient

from examples.tools.gateway_mcp_tools import SigV4HTTPXAuth

auth = SigV4HTTPXAuth(boto3.Session().get_credentials(),
                      "bedrock-agentcore", region)
mcp_client = MCPClient(lambda: streamablehttp_client(gateway_url, auth=auth))
mcp_client.start()  # not a `with` block: held for the process lifetime
tools = mcp_client.list_tools_sync()
```

Discovered tools arrive prefixed with the target name and three underscores. `lookup_order` becomes `supportTools___lookup_order`, and searching the list for the original name returns nothing.

`list_tools_sync()` returns Strands tool objects, the LangGraph tool node wants LangChain `BaseTool` objects, and the two share no interface. Those 22 lines convert between them. The same module merges both sources, matching on the part after the last `___`, so Gateway tools supersede same-named local functions and `search_faq` stays local.

#### Memory: State that used to die with the process

With compute and tool auth moved, conversation state is the remaining boundary in this stage. It still dies with the process, so two instances can’t read the same conversation. Memory retires that limit. Stage 0’s `MemorySaver` becomes a checkpointer backed by [AgentCore Memory](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html), keyed on `actor_id` and the session instead of a `thread_id` you chose. Create the store first, and set `event_expiry_days` deliberately, because checkpoints inherit it.

The checkpointer ships first party, a dependency rather than a file you own. It’s in the requirements you already installed, pinned:

```
langgraph-checkpoint-aws==1.2.1
```

Construct it with the memory id and nothing else. It takes no `actor_id`. It reads `actor_id` and `thread_id` off the `RunnableConfig` on each call instead of binding either at construction, so both travel with every invocation:

```
from langgraph_checkpoint_aws import AgentCoreMemorySaver

graph = build_graph(
    llm=llm,
    tools=tools,
    checkpointer=AgentCoreMemorySaver(memory_id, region_name=region),
)

state = graph.invoke(
    {"messages": [HumanMessage(prompt)]},
    config={"configurable": {"thread_id": session_id, "actor_id": actor_id}},
)
```

Test the durability, don’t assume it. A second process sharing only the memory, actor and session ids answered a question about an order it had never been told. Don’t assert on event counts, though. Two runs of identical code produced different totals.

You get durable conversation state shared across instances, sync and async. The saver also implements `list` and `delete_thread`. History and time travel work through the interface LangGraph already uses.

#### Deploying it, and verifying it ran

Prove the module locally first, because failures are legible there and inside Runtime they are not. `app.run()` serves the same `POST /invocations` contract Runtime invokes. Then call `CreateAgentRuntime` with a [codeConfiguration](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-code-deploy-python.html), which is a zip of your source in Amazon S3 with dependencies vendored beside it. No container, no Amazon Elastic Container Registry (Amazon ECR), no Docker. If you’re estimating this migration, that sentence is the estimate: pip is the only build tool the deploy needs.

Two traps cost real time, and neither error names its cause. First, `pip install -t` on a laptop installs laptop wheels, and Runtime is ARM64 (Advanced RISC Machine 64-bit) Linux. Vendor for the target application and the Python version the deploy names, so wheels and runtime agree:

```
pip install -r requirements.txt -t build/ \
    --platform manylinux2014_aarch64 --python-version 3.12 --only-binary=:all:
```

That 3.12 is the deploy target, not your local interpreter.

Second, a `requirements.txt` inside the zip is inert. The archive is the finished environment. Miss a dependency and the failure reads `Runtime initialization time exceeded ... 30s` rather than the `ModuleNotFoundError` that happened. Vendor the dependency, don’t tune the timeout.

The commands that follow create real AWS resources and start incurring charges. The Clean up section at the end removes everything the walkthrough makes.

Then validate against the baseline you recorded. Stage 1 needs two ARNs, and one script creates the Lambda behind the gateway target and prints both:

```
./examples/gateway/lambda_target/deploy.sh
python -m examples.run_walkthrough --stage 1 \
    --role-arn <gateway-role-arn> --lambda-arn <tools-function-arn>
```

Stage 1 prints the same per-turn output stage 0 did, so the check is a diff, not a judgement about reply text. The sample asserts that diff rather than leaving it to your eye: `test_stage1_replatform.py` requires the gateway call to arrive as `supportTools___lookup_order` carrying `{"order_id": "12345"}`, so a renamed tool or a dropped argument fails the run instead of passing a visual inspection.

When the agent does something you didn’t expect, you need to see what it actually did. Normally that means owning the instrumentation: a tracing package, environment variables, a collector to run. Runtime instruments the agent it hosts, and AgentCore Observability, a capability of Amazon Bedrock AgentCore, sends the result to CloudWatch. There’s no tracing package in the requirements and no `OTEL_*` variable to set. The log group appears after the first invocation without being asked for, and the spans show up in CloudWatch once Transaction Search is on.

![Architecture diagram titled “Stage 1: replatform the runtime.” Subtitle: direct invocation, unchanged orchestration, partial tool migration. A band across the top, marked deploy time and not request path, traces source plus vendored dependencies as a zip, into Amazon S3 as agent.zip, into a CreateAgentRuntime call whose codeConfiguration points back at S3, ending at Runtime deployed. There is no container and no Amazon ECR anywhere along it. Below that, a band marked request path starts at a client application card that calls InvokeAgentRuntime with a runtimeSessionId of at least 33 characters and is marked direct call. One arrow runs from it straight into the Amazon Bedrock AgentCore Runtime card, described as serverless with one microVM per session, with no load balancer and no API Gateway in between. Inside the Runtime card, three boxes stack down the page. First, agent_runtime.py, holding BedrockAgentCoreApp with an @app.entrypoint function and mapping RequestContext.session_id to thread_id. Second, the LangGraph graph, marked imported, not rewritten, built by build_graph from stage 0, and noted as the same graph calling all three tools. Third, the tools, split in two: a box outlined in the accent color and marked local Python holds search_faq and states it stays in Runtime, while a box marked gateway-served holds supportTools___lookup_order and supportTools___process_return, so two of the three tools are served by Gateway and one is not. Four service cards sit down the right side. Amazon Bedrock, using ChatBedrockConverse, is marked did not move and already Bedrock. AgentCore Memory, reached from Runtime, is annotated AgentCoreMemorySaver, a first-party saver from langgraph-checkpoint-aws. AgentCore Gateway speaks MCP over SigV4-signed calls with an AWS_IAM authorizer, and is reached from the gateway-served tool box. AWS Lambda is the Gateway target, receiving arguments as the raw event and the tool name in the client context. Along the bottom, an observability card carries the Amazon CloudWatch and AWS Distro for OpenTelemetry icons and reports Runtime logs, metrics, and traces. Beside it, an AgentCore Policy card marked attaches to this gateway is noted as demonstrated at stage 2 and describes Cedar on each tool call in the data plane, joined to Gateway by a dashed line. A line above the footer records that stage 1 was validated by re-running the stage 0 baseline over the same three turns and comparing the tools that ran and the final state, and states that VPC configuration, WAF, IAM policies, secrets rotation and dependency updates are still ours. A footer line reads: stage 1 replatformed runtime, no load balancer, no API Gateway, no container, no Amazon ECR.](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/31/ML-20753-3.png)

Figure 3: The client calls Runtime directly, the graph is imported and not rewritten, and two of the three tools move behind Gateway

That’s stage 1: the same agent giving the same answers, with five of the ten burdens now handled by AgentCore. Who plans the next step hasn’t changed, and that question is stage 2’s.

### Stage 2: Rebuilding the loop, because you chose to

Five of the ten operational burdens have moved, and five remain yours: VPC configuration, WAF, IAM policies, secrets rotation and dependency updates. Stage 2 moves none of them, because this stage changes who plans the next step. Take it when the hand-written branch is the ceiling: when `route_intent` is the file you keep editing, and a new intent means a new node rather than a new line in a prompt.

Model-driven orchestration replaces the branch. Stage 0’s `classify_intent` node and `route_intent` decided the next step in Python. A Strands agent hands that decision to the model, so `add_conditional_edges` has no counterpart. That is a loss as well as a gain. The branch was deterministic and auditable, and a model’s plan is neither.

The `bedrock-agentcore` SDK ships a session manager for Strands agents, so the wiring is a config object and a constructor argument:

```
config = AgentCoreMemoryConfig(
    memory_id=memory_id, session_id=session_id, actor_id=actor_id
)
kwargs["session_manager"] = AgentCoreMemorySessionManager(
    config, region_name=region_name
)

return Agent(**kwargs)
```

The session manager rides into `Agent(**kwargs)` beside the model, system prompt and tools, and it carries stage 1’s three ids, with `thread_id` now named `session_id`.

Stage 2 reuses stage 1’s gateway, target and Memory store. It does not reuse the stage-1 runtime, because the program inside it is a different loop. Amazon Bedrock didn’t move here either. Same model, every stage. Run it with the same two ARNs:

```
python -m examples.run_walkthrough --stage 2 \
    --role-arn <gateway-role-arn> --lambda-arn <tools-function-arn>
```

#### Authorization on the tool call itself

Stage 2 handed planning to the model and lost the auditable branch. [Policy in Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy.html) puts a deterministic decision back in front of every tool call: Cedar rules evaluate on each call through the gateway, in the data plane, on a path the application can’t bypass. A guardrail on model output is not on that path, and by the time it runs, the tool call has happened.

Policy attaches to the Gateway rather than the loop, so this works on the stage-1 agent unchanged. It appears here because the sample runs it here.

The sample ships two rules: a read-only identity may call `lookup_order`, a privileged identity might also call `process_return`. **There is no `forbid` rule anywhere.** Cedar is default-deny, so the read-only caller’s refusal is the absence of a matching permit. Coming from IAM, that is the habit to unlearn.

Both caller roles are created with identical IAM policies, which is why the enforcement is provably Cedar’s and not an IAM gap. Same permissions, same gateway, two callers against two tools, one refusal.

![Architecture diagram titled “Stage 2: rebuild the loop.” Subtitle: model-driven planning, SDK-shipped memory wiring, Cedar on every tool call. The upper half, headed what the rebuild changes, holds two cards. The first, marked the loop, rebuilt, shows a Strands Agent running strands_agent.py on AgentCore Runtime, with model-driven planning rather than a router, no route_intent and no add_conditional_edges, and a note that what is lost is a deterministic, auditable branch. The second, marked memory wiring, SDK-shipped, shows AgentCore Memory reusing stage 1’s store, with the SDK session manager named as AgentCoreMemorySessionManager. The lower half, headed the proof, Cedar in the data plane, holds AgentCore Policy described as two callers times two tools, evaluated at the Gateway in the data plane on every tool call, with a note that two by two is the smallest experiment that attributes a refusal because one refused call looks like missing IAM. A two by two table follows: a read-only role is allowed supportTools___lookup_order but denied supportTools___process_return for no matching permit, and a support-agent role is allowed both. Two lines state that no forbid rule exists anywhere because Cedar is default-deny, so the refusal is the absence of a permit, and that both roles’ IAM policies are identical, so the one refusal is provably Cedar’s. A dashed arrow leads down to a final band whose label lists what is reused, the Gateway, the target and Memory but not the stage 1 runtime, and notes that walkthrough steps 1 to 3 build them for either stage. The band shows AgentCore Gateway with its AWS_IAM authorizer, AWS Lambda as an unchanged target, and Amazon Bedrock as the same model in every stage, adding that the Memory store is also stage 1’s, the two Gateway tools supersede the same-named local stubs, search_faq stays local as in every stage, and deploy uses the same zip path as stage 1. One footer line states that ownership is unchanged, VPC configuration, WAF, IAM policies, secrets rotation and dependency updates, and that what changed is who plans. A second footer line notes that AWS_IAM principals carry an ARN and no tags, so the rules scope tools to callers and nothing finer.](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/31/ML-20753-4.png)

Figure 4: The loop becomes the model’s, memory wiring collapses into an SDK-shipped session manager, and Cedar decides every tool call at the Gateway

The loop is the model’s now, but it still ships as your code. Stage 3 is what removing that last piece looks like.

### Stage 3: Hand the loop over

One burden stays tied to owning the code, and this is the only stage that moves it. An [AgentCore harness](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-vs-runtime.html) runs the loop for you, powered by Strands Agents. You declare the agent as configuration (model, system prompt, tools, memory and limits) and AWS runs it, so switching a model is a configuration change rather than a redeploy. If you want the harness, what you run is stage 2’s agent. It hosts a single model-driven loop, not a graph, so a graph-shaped agent reaches it by becoming that loop first. That is the one place the recommended order is also the only order.

The figure marks that column documented rather than measured. Six of the ten burdens move there, against five at stage 2, and dependency updates is the only one that moves here, because the agent stops being your code. Secrets rotation isn’t among them. Identity refreshes tokens rather than rotating the secrets behind them, so that burden stays yours at stage 3 too.

## Common pitfalls

Migration changes more than infrastructure. These are the patterns that cost teams the most time after the move.

### 1. Assuming feature parity

Assuming parity sets up an argument nobody can close. Your agent won’t behave identically after migration, and without criteria agreed before the move, every difference in wording becomes that argument. Define acceptance criteria on outcomes, not implementation, then test them: 90 percent of order-status queries resolved without escalation, a response within 5 seconds. [AgentCore Evaluations](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations.html), a capability of Amazon Bedrock AgentCore, has built-in evaluators.

### 2. Holding state in the process

This one is paid for in production, by a user who stepped away, because no quick test idles long enough to catch it. A session isn’t an invocation: one session holds invocation after invocation, and Runtime ends an execution environment after 15 minutes of inactivity by default, provisioning a new one for the same session. That idle window is [idleRuntimeSessionTimeout](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-lifecycle-settings.html), settable from 60 seconds to 8 hours, so tuning it moves the deadline rather than removing it. The session survives, your in-memory state does not, and the symptom is state that disappears only after a quiet period. Hold the graph, as stage 1 does, but keep every fact the next turn needs in Memory.

### 3. Overlooking authentication architecture

Authentication gaps cost rework, not configuration: the tool that needs user-delegated access surfaces late and changes the invocation path. So map every flow first: how your agent authenticates to external APIs, how people authenticate to the agent, how you scope permissions. AgentCore Identity, a capability of Amazon Bedrock AgentCore, answers the first, referenced on your gateway target in place of `GATEWAY_IAM_ROLE`.

## Clean up

To avoid ongoing charges, remove what you created. The walkthrough tears down everything it made:

```
python -m examples.run_walkthrough --teardown
```

That is twelve resources in dependency order, and the Amazon CloudWatch log group is the one to notice. Nothing asked for it, the service created it on the runtime’s first log line, and deleting the runtime does not remove it. Delete the gateway target before the gateway, and poll `GetMemory` until the store is gone, because `DeleteMemory` returns first.

The Lambda function backing your tools, its execution role and the gateway’s are yours to delete.

## Conclusion

Stage 1 is a stopping point. You get the orchestration you already trust, on managed compute, with managed tools and durable state. So is stage 2, for agents where hand-written routing has become the constraint. Stage 3 takes the loop out of your code base.

None of this needs doing twice. AgentCore features attached in four shapes: a keyword argument for the gateway tools, a pinned dependency for the checkpointer, a config object for the session manager, a file of Cedar rules for Policy. Adding Identity or a second gateway target is that size of change, not this migration again.

The order is the same for most agents and the stopping stage is not. Stateful sessions and hard external dependencies are where you resequence it.

Leave a comment with questions or your own experience.

## Next steps

Clone the [sample repository](https://github.com/aws-samples/sample-migrate-agents-to-amazon-bedrock-agentcore), read its [security architecture comparison](https://github.com/aws-samples/sample-migrate-agents-to-amazon-bedrock-agentcore/blob/main/docs/security-comparison.md), then the [Amazon Bedrock AgentCore documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/).

## About the authors
