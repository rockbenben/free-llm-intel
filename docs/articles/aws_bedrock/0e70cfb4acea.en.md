---
vendor: aws_bedrock
title: Introducing stateful MCP client capabilities on Amazon Bedrock AgentCore Runtime
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/introducing-stateful-mcp-client-capabilities-on-amazon-bedrock-agentcore-runtime
date: 2026-04-09
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 00533126ee2d
---

# Introducing stateful MCP client capabilities on Amazon Bedrock AgentCore Runtime

Stateful MCP client capabilities on [Amazon Bedrock AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/mcp-stateful-features.html) now enable interactive, multi-turn agent workflows that were previously impossible with stateless implementations. Developers building AI agents often struggle when their workflows must pause mid-execution to ask users for clarification, request large language model (LLM)-generated content, or provide real-time progress updates during long-running operations, stateless MCP servers can’t handle these scenarios. This solves these limitations by introducing three client capabilities from the MCP specification:

- Elicitation (request user input mid-execution)
- Sampling (request LLM-generated content from the client)
- Progress notification (stream real-time updates)

These capabilities transform one-way tool execution into bidirectional conversations between your MCP server and clients.

[Model Context Protocol (MCP)](https://modelcontextprotocol.io/specification/2025-11-25) is an open standard defining how LLM applications connect with external tools and data sources. The specification defines server capabilities (tools, prompts, and resources that servers expose) and client capabilities (features clients offer back to servers). While our previous release focused on hosting stateless MCP servers on AgentCore Runtime, this new capability completes the bidirectional protocol implementation. Clients connecting to AgentCore-hosted MCP servers can now respond to server-initiated requests. In this post, you will learn how to build stateful MCP servers that request user input during execution, invoke LLM sampling for dynamic content generation, and stream progress updates for long-running tasks. You will see code examples for each capability and deploy a working stateful MCP server to Amazon Bedrock AgentCore Runtime.

## **From stateless to stateful MCP**

The original MCP server support on AgentCore used stateless mode: each incoming HTTP request was independent, with no shared context between calls. This model is straightforward to deploy and reason about, and it works well for tool servers that receive inputs and return outputs. However, it has a fundamental constraint. The server can’t maintain a conversation thread across requests, ask the user for clarification in the middle of a tool call, or report progress back to the client as work happens.

Stateful mode removes that constraint. When you run your MCP server with stateless_http=False, AgentCore Runtime provisions a dedicated microVM for each user session. The microVM persists for the session’s lifetime (up to 8 hours, or 15 minutes of inactivity per idleRuntimeSessionTimeout [setting](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-lifecycle-settings.html#configuration-attributes)), with CPU, memory, and filesystem isolation between sessions. The protocol maintains continuity through a `Mcp-Session-Id` header: the server returns this identifier during the initialize handshake, and the client includes it in every subsequent request to route back to the same session.

The following table summarizes the key differences:

|  | **Stateless mode** | **Stateful mode** |
| --- | --- | --- |
| **stateless_httpsetting** | TRUE | FALSE |
| **Session isolation** | Dedicated microVM per session | Dedicated microVM per session |
| **Session lifetime** | Up to 8 hours; 15-min idle timeout | Up to 8 hours; 15-min idle timeout |
| **Client capabilities** | Not supported | Elicitation, sampling, progress notifications |
| **Recommended for** | Simple tool serving | Interactive, multi-turn workflows |

When a session expires or the server is restarted, subsequent requests with the early session ID return a 404. At that point, clients must re-initialize the connection to obtain a new session ID and start a fresh session.The configuration change to enable stateful mode is a single flag in your server startup:

```
mcp.run( transport="streamable-http", host="0.0.0.0", port=8000, stateless_http=False # Enable stateful mode)
```

Beyond this flag, the three client capabilities become available automatically once the MCP client declares support for them during the initialization handshake.

## **The three new client capabilities**

Stateful mode brings three client capabilities from the MCP specification. Each addresses a different interaction pattern that agents encounter in production workflows.

**Elicitation** allows a server to pause execution and request structured input from the user through the client. The tool can ask targeted questions at the right moment in its workflow, gathering a preference, confirming a decision, or collecting a value that depends on earlier results. The server sends an elicitation/create request with a message and an optional JSON schema describing the expected response structure. The client renders an appropriate input interface, and the user can accept (providing the data), decline, or cancel.

**Sampling** allows a server to request an LLM-generated completion from the client through sampling/createMessage. This is the mechanism that makes it possible for tool logic on the server to use language model capabilities without holding its own model credentials. The server provides a prompt and optional model preferences; the client forwards the request to its connected LLM and returns the generated response. Practical uses include generating personalized summaries, creating natural-language explanations of structured data, or producing recommendations based on earlier conversation context.

**Progress notifications** allow a server to report incremental progress during long-running operations. Using `ctx.report_progress(progress, total)`, the server emits updates that clients can display as a progress bar or status indicator. For operations that span multiple steps, for example, searching across data sources, this keeps users informed rather than watching a blank screen.

All three capabilities are opt-in at the client level: a client declares which capabilities it supports during initialization, and the server must only use capabilities the client has advertised.

### **Elicitation: server-initiated user input**

Elicitation is the mechanism by which an MCP server pauses mid-execution and asks the client to collect specific information from the user. The server sends an elicitation/create JSON-RPC request containing a human-readable message and a requestedSchema that describes the expected response. The client presents this as a form or prompt, and the user’s response (or explicit decline) is returned to the server so execution can continue.The MCP specification supports two elicitation modes:

- **Form mode**: structured data collection directly through the MCP client. Suitable for preferences, configuration inputs, and confirmations that don’t involve sensitive data.
- **URL mode**: directs the user to an external URL for interactions that must not pass through the MCP client, such as OAuth flows, payment processing, or credential entry.

The response uses a three-action model: `accept` (user provided data), `decline` (user explicitly rejected the request), or `cancel` (user dismissed without choosing). Servers should handle each case appropriately. The following example implements an `add_expense_interactive` tool that collects a new expense through four sequential elicitation steps: amount, description, category, and a final confirmation before writing to DynamoDB. Each step defines its expected input as a Pydantic model, which FastMCP converts to the JSON Schema sent in the `elicitation/create` request.

**Server**

The `add_expense_interactive` tool walks a user through four sequential questions before writing to Amazon DynamoDB. Each step defines its expected input as a separate Pydantic model, because the form mode schema must be a flat object. You can collect all four fields in a single model with four properties but splitting them here gives the user one focused question at a time, which is the interactive pattern elicitation is designed for.

`**agents/mcp_client_features.py**`

```
import os
from pydantic import BaseModel
from fastmcp import FastMCP, Context
from fastmcp.server.elicitation import AcceptedElicitation
from dynamo_utils import FinanceDB

mcp = FastMCP(name='ElicitationMCP')

_region = os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION') or 'us-east-1'
db = FinanceDB(region_name=_region)

class AmountInput(BaseModel):
    amount: float

class DescriptionInput(BaseModel):
    description: str

class CategoryInput(BaseModel):
    category: str  # one of: food, transport, bills, entertainment, other

class ConfirmInput(BaseModel):
    confirm: str  # Yes or No

@mcp.tool()
async def add_expense_interactive(user_alias: str, ctx: Context) -> str:
    """Interactively add a new expense using elicitation.

    Args:
        user_alias: User identifier
    """
    # Step 1: Ask for the amount
    result = await ctx.elicit('How much did you spend?', AmountInput)
    if not isinstance(result, AcceptedElicitation):
        return 'Expense entry cancelled.'
    amount = result.data.amount

    # Step 2: Ask for a description
    result = await ctx.elicit('What was it for?', DescriptionInput)
    if not isinstance(result, AcceptedElicitation):
        return 'Expense entry cancelled.'
    description = result.data.description

    # Step 3: Select a category
    result = await ctx.elicit(
        'Select a category (food, transport, bills, entertainment, other):',
        CategoryInput
    )
    if not isinstance(result, AcceptedElicitation):
        return 'Expense entry cancelled.'
    category = result.data.category

    # Step 4: Confirm before saving
    confirm_msg = (
        f'Confirm: add expense of ${amount:.2f} for {description}'
        f' (category: {category})? Reply Yes or No'
    )
    result = await ctx.elicit(confirm_msg, ConfirmInput)
    if not isinstance(result, AcceptedElicitation) or result.data.confirm != 'Yes':
        return 'Expense entry cancelled.'

    return db.add_transaction(user_alias, 'expense', -abs(amount), description, category)

if __name__ == '__main__':
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
        stateless_http=False
    )
```

Each `await ctx.elicit() `suspends the tool and sends an `elicitation/create` request over the active session. The `isinstance(result, AcceptedElicitation) `check handles `decline` and `cancel` uniformly at every step.

**Client**

Registering an `elicitation_handler` on `fastmcp.Client` is both how the handler is wired in and how the client advertises elicitation support to the server during initialization.

```
import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

# Pre-loaded responses simulate the user answering each question in sequence
_responses = iter([
    {'amount': 45.50},
    {'description': 'Lunch at the office'},
    {'category': 'food'},
    {'confirm': 'Yes'},
])

async def elicit_handler(message, response_type, params, context):
    # In production: render a form and return the user's input
    response = next(_responses)
    print(f'  Server asks: {message}')
    print(f'  Responding:  {response}\n')
    return response

transport = StreamableHttpTransport(url=mcp_url, headers=headers)

async with Client(transport, elicitation_handler=elicit_handler) as client:
    await asyncio.sleep(2)  # allow session initialization
    result = await client.call_tool('add_expense_interactive', {'user_alias': 'me'})

print(result.content[0].text)
```

Running this against the deployed server:

```
Server asks: How much did you spend?
Responding:  {'amount': 45.5}

Server asks: What was it for?
Responding:  {'description': 'Lunch at the office'}

Server asks: Select a category (food, transport, bills, entertainment, other):
Responding:  {'category': 'food'}

Server asks: Confirm: add expense of $45.50 for Lunch at the office (category: food)? Reply Yes or No
Responding:  {'confirm': 'Yes'}

Expense of $45.50 added for me
```

The complete working example, including DynamoDB setup and AgentCore deployment, is available in the [GitHub sample repository](https://github.com/awslabs/amazon-bedrock-agentcore-samples/tree/main/01-tutorials/01-AgentCore-runtime/08-mcp-e2e/02-client-e2e).

Use elicitation when your tool needs information that depends on earlier results, is better collected interactively than upfront, or varies across users in ways that cannot be parameterized in advance. A travel booking tool that first searches destinations and then asks the user to choose among them is a natural fit. A financial workflow that confirms a transaction amount before submitting is another. Elicitation isn’t appropriate for sensitive inputs like passwords or API keys, use URL mode or a secure out-of-band channel for those.

### **Sampling: server-initiated LLM generation**

Sampling is the mechanism by which an MCP server requests an LLM completion from the client. The server sends a `sampling/createMessage` request containing a list of conversation messages, a system prompt, and optional model preferences. The client forwards the request to its connected language model (subject to user approval) and returns the generated response. The server receives a structured result containing the generated text, the model used, and the stop reason.

This capability inverts the typical flow: instead of the client asking the server for tool results, the server asks the client for model output. The benefit is that the server doesn’t need API keys or a direct model integration. The client retains full control over which model is used, and the MCP specification calls for a human-in-the-loop step where users can review and approve sampling requests before they are forwarded.

Servers can express model preferences using capability priorities (`costPriority, speedPriority, intelligencePriority`) and optional model hints. These are advisory, the client makes the final selection based on what models it has access to.

**Server**

The `analyze_spending` tool fetches transactions from DynamoDB, builds a prompt from the structured data, and delegates the analysis to the client’s LLM via `ctx.sample()`.

**agents/mcp_client_features.py** (added tool, same file as elicitation)

```
@mcp.tool()
async def analyze_spending(user_alias: str, ctx: Context) -> str:
    """Fetch expenses from DynamoDB and ask the client's LLM to analyse them.

    Args:
        user_alias: User identifier
    """
    transactions = db.get_transactions(user_alias)
    if not transactions:
        return f'No transactions found for {user_alias}.'

    lines = '\n'.join(
        f"- {t['description']} (${abs(float(t['amount'])):.2f}, {t['category']})"
        for t in transactions
    )

    prompt = (
        f'Here are the recent expenses for a user:\n{lines}\n\n'
        f'Please analyse the spending patterns and give 3 concise, '
        f'actionable recommendations to improve their finances. '
        f'Keep the response under 120 words.'
    )

    ai_analysis = 'Analysis unavailable.'
    try:
        response = await ctx.sample(messages=prompt, max_tokens=300)
        if hasattr(response, 'text') and response.text:
            ai_analysis = response.text
    except Exception:
        pass

    return f'Spending Analysis for {user_alias}:\n\n{ai_analysis}'
```

The tool calls `await ctx.sample()` and suspends. The server sends a `sampling/createMessage` request to the client over the open session. When the client returns the LLM response, execution resumes.

**Client**

The `sampling_handler` receives the prompt from the server and forwards it to a language model. In this example, that’s Claude Haiku on Amazon. Registering the handler is also how the client declares sampling support to the server during initialization.

```
import json
import asyncio
import boto3
from mcp.types import CreateMessageResult, TextContent
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

MODEL_ID = 'us.anthropic.claude-haiku-4-5-20251001-v1:0'
bedrock = boto3.client('bedrock-runtime', region_name=region)

def _invoke_bedrock(prompt: str, max_tokens: int) -> str:
    body = json.dumps({
        'anthropic_version': 'bedrock-2023-05-31',
        'max_tokens': max_tokens,
        'messages': [{'role': 'user', 'content': prompt}]
    })
    resp = bedrock.invoke_model(modelId=MODEL_ID, body=body)
    return json.loads(resp['body'].read())['content'][0]['text']

async def sampling_handler(messages, params, ctx):
    """Called by fastmcp.Client when the server issues ctx.sample()."""
    prompt = messages if isinstance(messages, str) else ' '.join(
        m.content.text for m in messages if hasattr(m.content, 'text')
    )
    max_tokens = params.maxTokens if params and hasattr(params, 'maxTokens') and params.maxTokens else 300
    text = await asyncio.to_thread(_invoke_bedrock, prompt, max_tokens)
    return CreateMessageResult(
        role='assistant',
        content=TextContent(type='text', text=text),
        model=MODEL_ID,
        stopReason='endTurn'
    )

transport = StreamableHttpTransport(url=mcp_url, headers=headers)

async with Client(transport, sampling_handler=sampling_handler) as client:
    result = await client.call_tool('analyze_spending', {'user_alias': 'me'})

print(result.content[0].text)
```

Running this against a user with four seeded expenses:

```
Spending Analysis for me:

Total Spending: $266.79

Breakdown:
- Food: $130.80 (49%)
- Bills: $120.00 (45%)
- Entertainment: $15.99 (6%)

3 Actionable Recommendations:

1. Meal prep at home — cook groceries into multiple meals to reduce restaurant
   spending and lower food costs by 20-30%.

2. Review entertainment subscriptions — audit all subscriptions and cancel
   unused services or share family plans.

3. Reduce energy costs — use programmable thermostats, LED bulbs, and unplug
   devices to lower electricity bills by 10-15% monthly.
```

Use sampling when your tool must produce natural-language output that benefits from a language model’s capabilities. A tool that has collected a user’s travel preferences and wants to generate a tailored trip itinerary narrative is a good example. Sampling isn’t appropriate for deterministic operations like database queries, calculations, or API calls with well-defined outputs. We recommend that you use tool logic for those.

### **Progress notifications: real-time operation feedback**

Progress notifications are events that a server sends during long-running operations to keep the client and the user informed about how much work has been completed. `await ctx.report_progress(progress, total)` emits a `notifications/progress` message and returns immediately. The server doesn’t wait for a response, it’s fire-and-forget in both directions. The client receives the notification asynchronously and can render a progress bar, log a status line, or use it to prevent the user from assuming the connection has stalled. The pattern is to call `report_progress` at each logical step of a multi-stage operation, with progress incrementing toward total.

**Server**

The `generate_report` tool builds a monthly financial report in five steps, emitting a progress notification at the start of each one.

**agents/mcp_progress_server.py**

```
import os
from fastmcp import FastMCP, Context
from dynamo_utils import FinanceDB

mcp = FastMCP(name='Progress-MCP-Server')

_region = os.environ.get('AWS_REGION') or os.environ.get('AWS_DEFAULT_REGION') or 'us-east-1'
db = FinanceDB(region_name=_region)

@mcp.tool()
async def generate_report(user_alias: str, ctx: Context) -> str:
    """Generate a monthly financial report, streaming progress at each stage.

    Args:
        user_alias: User identifier
    """
    total = 5

    # Step 1: Fetch transactions
    await ctx.report_progress(progress=1, total=total)
    transactions = db.get_transactions(user_alias)

    # Step 2: Group by category
    await ctx.report_progress(progress=2, total=total)
    by_category = {}
    for t in transactions:
        cat = t['category']
        by_category[cat] = by_category.get(cat, 0) + abs(float(t['amount']))

    # Step 3: Fetch budgets
    await ctx.report_progress(progress=3, total=total)
    budgets = {b['category']: float(b['monthly_limit']) for b in db.get_budgets(user_alias)}

    # Step 4: Compare spending vs budgets
    await ctx.report_progress(progress=4, total=total)
    lines = []
    for cat, spent in sorted(by_category.items(), key=lambda x: -x[1]):
        limit = budgets.get(cat)
        if limit:
            pct = (spent / limit) * 100
            status = 'OVER' if spent > limit else 'OK'
            lines.append(f'  {cat:<15} ${spent:>8.2f} / ${limit:.2f}  [{pct:.0f}%] {status}')
        else:
            lines.append(f'  {cat:<15} ${spent:>8.2f}  (no budget set)')

    # Step 5: Format and return
    await ctx.report_progress(progress=5, total=total)
    total_spent = sum(by_category.values())
    return (
        f'Monthly Report for {user_alias}\n'
        f'{"=" * 50}\n'
        f'  {"Category":<15} {"Spent":>10}   {"Budget":>8}  Status\n'
        f'{"-" * 50}\n'
        + '\n'.join(lines)
        + f'\n{"-" * 50}\n'
        f'  {"TOTAL":<15} ${total_spent:>8.2f}\n'
    )

if __name__ == '__main__':
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
        stateless_http=False
    )
```

Each await `ctx.report_progress()` is fire-and-forget: the notification is sent and execution moves immediately to the next step.

**Client**

The `progress_handler` receives progress, total, and an optional message each time the server emits a notification. Registering the handler is how the client declares progress support during initialization.

```
import logging
logging.getLogger('mcp.client.streamable_http').setLevel(logging.ERROR)

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

async def progress_handler(progress: float, total: float | None, message: str | None):
    pct = int((progress / total) * 100) if total else 0
    filled = pct // 5
    bar = '#' * filled + '-' * (20 - filled)
    print(f'\r  Progress: [{bar}] {pct}% ({int(progress)}/{int(total or 0)})',
          end='', flush=True)
    if total and progress >= total:
        print('  Done!')

transport = StreamableHttpTransport(url=mcp_url, headers=headers)

async with Client(transport, progress_handler=progress_handler) as client:
    result = await client.call_tool('generate_report', {'user_alias': 'me'})

print(result.content[0].text)
```

As the server moves through its five stages, the client renders the bar in place:

```
  Progress: [####----------------] 20% (1/5)
  Progress: [########------------] 40% (2/5)
  Progress: [############--------] 60% (3/5)
  Progress: [################----] 80% (4/5)
  Progress: [####################] 100% (5/5)  Done!
```

Use progress notifications for any tool call that takes more than a few seconds and involves discrete, measurable steps. Operations like searching multiple data sources, running a sequence of API calls, processing a batch of records, or running a multi-step booking workflow are all good candidates. A tool that completes in under a second generally does not need progress reporting; the overhead of emitting events is not worthwhile for fast operations.

## **Conclusion**

In this post, you have been introduced to stateful MCP client capabilities on Amazon Bedrock AgentCore Runtime. We explained the difference between stateless and stateful MCP deployments, walked through elicitation, sampling, and progress notifications with code examples, and showed how to deploy a stateful MCP server into AgentCore Runtime. With these capabilities, you can build MCP servers that engage users in structured conversations, use the client’s LLM for content generation, and provide real-time visibility into long-running operations, all hosted on managed, isolated infrastructure powered by AgentCore Runtime.We encourage you to explore the following resources to get started:

- [GitHub sample code.](https://github.com/awslabs/amazon-bedrock-agentcore-samples/tree/main/01-tutorials/01-AgentCore-runtime/08-mcp-e2e)
- [Amazon Bedrock AgentCore Runtime documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-how-it-works.html)
- [Stateful MCP features documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/mcp-stateful-features.html)
- [MCP specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25)
- [Prior post: Hosting MCP servers on AgentCore Runtime](https://aws.amazon.com/blogs/machine-learning/accelerate-development-with-the-amazon-bedrock-agentcore-mcpserver/)

## **About the Authors**
