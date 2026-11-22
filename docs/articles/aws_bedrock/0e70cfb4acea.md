---
vendor: aws_bedrock
title: Introducing stateful MCP client capabilities on Amazon Bedrock AgentCore Runtime
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/introducing-stateful-mcp-client-capabilities-on-amazon-bedrock-agentcore-runtime
date: 2026-04-09
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 069cca73336e
---

# Amazon Bedrock AgentCore Runtime 上的有状态 MCP 客户端能力介绍

[Amazon Bedrock AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/mcp-stateful-features.html) 上的有状态 MCP 客户端能力，如今支持此前用无状态实现无法做到的交互式多轮 agent 工作流。构建 AI agent 的开发者常常遇到这样的困境：工作流需要在执行中途暂停，向用户询问澄清、请求大语言模型（LLM）生成的内容，或在长时间运行的操作中提供实时进度更新，而无状态 MCP 服务器无法处理这些场景。本方案通过引入 MCP 规范中的三项客户端能力解决了这些限制：

- Elicitation（在执行中途请求用户输入）
- Sampling（向客户端请求 LLM 生成的内容）
- Progress notification（流式传输实时更新）

这些能力将单向的工具执行转变为 MCP 服务器与客户端之间的双向对话。

[Model Context Protocol (MCP)](https://modelcontextprotocol.io/specification/2025-11-25) 是一个开放标准，定义 LLM 应用如何连接外部工具和数据源。该规范定义了 server capabilities（服务器暴露的 tools、prompts 和 resources）以及 client capabilities（客户端向服务器提供的特性）。我们此前的版本专注于在 AgentCore Runtime 上托管无状态 MCP 服务器，而这项新能力补全了双向协议的实现。连接到 AgentCore 托管 MCP 服务器的客户端现在可以响应服务器发起的请求。在本文中，你将学习如何构建有状态 MCP 服务器：在执行期间请求用户输入、调用 LLM sampling 生成动态内容，并为长时间运行的任务流式传输进度更新。你将看到每项能力的代码示例，并将一个可运行的有状态 MCP 服务器部署到 Amazon Bedrock AgentCore Runtime。

## **从无状态 MCP 到有状态 MCP**

AgentCore 最初对 MCP 服务器的支持采用无状态模式：每个传入的 HTTP 请求都是独立的，调用之间没有共享上下文。这种模式易于部署和理解，很适合接收输入并返回输出的工具服务器。但它有一个根本性的限制：服务器无法跨请求维护对话线程，无法在工具调用中途向用户询问澄清，也无法在工作进行时向客户端报告进度。

有状态模式消除了这一限制。当你以 stateless_http=False 运行 MCP 服务器时，AgentCore Runtime 会为每个用户会话配置一个专用的 microVM。该 microVM 在会话的整个生命周期内持续存在（最长 8 小时，或按 idleRuntimeSessionTimeout [设置](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-lifecycle-settings.html#configuration-attributes)计算的无活动状态 15 分钟），会话之间实现 CPU、内存和文件系统隔离。协议通过 `Mcp-Session-Id` 标头维持连续性：服务器在 initialize 握手中返回该标识符，客户端在后续每个请求中都携带它，以路由回同一会话。

下表总结了关键差异：

|  | **无状态模式** | **有状态模式** |
| --- | --- | --- |
| **stateless_httpsetting** | TRUE | FALSE |
| **会话隔离** | 每个会话专用 microVM | 每个会话专用 microVM |
| **会话生命周期** | 最长 8 小时；15 分钟空闲超时 | 最长 8 小时；15 分钟空闲超时 |
| **客户端能力** | 不支持 | Elicitation、sampling、progress notifications |
| **推荐场景** | 简单工具服务 | 交互式多轮工作流 |

当会话过期或服务器重启时，携带旧会话 ID 的后续请求会返回 404。此时，客户端必须重新初始化连接以获取新的会话 ID 并开启全新会话。启用有状态模式的配置改动，只是服务器启动时的一个标志位：

```
mcp.run( transport="streamable-http", host="0.0.0.0", port=8000, stateless_http=False # Enable stateful mode)
```

除了这个标志位之外，一旦 MCP 客户端在初始化握手中声明支持这三项客户端能力，它们就会自动可用。

## **三项新的客户端能力**

有状态模式带来了 MCP 规范中的三项客户端能力。每一项都对应 agent 在生产工作流中遇到的一种不同交互模式。

**Elicitation** 允许服务器暂停执行，并通过客户端向用户请求结构化输入。该工具可以在工作流中的恰当时机提出针对性问题：收集偏好、确认决策，或采集依赖先前结果的值。服务器发送一个 elicitation/create 请求，其中包含一条消息和一个可选的 JSON schema，用于描述预期的响应结构。客户端渲染相应的输入界面，用户可以接受（提供数据）、拒绝或取消。

**Sampling** 允许服务器通过 sampling/createMessage 向客户端请求 LLM 生成的补全内容。正是这一机制让服务器上的工具逻辑无需持有自己的模型凭证，也能使用语言模型能力。服务器提供一个 prompt 和可选的模型偏好；客户端将请求转发给它所连接的 LLM，并返回生成的响应。实际用途包括生成个性化摘要、为结构化数据创建自然语言解释，或基于先前对话上下文给出推荐。

**Progress notifications** 允许服务器在长时间运行的操作中报告增量进度。通过 `ctx.report_progress(progress, total)`，服务器发出更新，客户端可将其显示为进度条或状态指示器。对于跨多个步骤的操作（例如跨数据源搜索），这能让用户随时了解情况，而不是对着空白屏幕等待。

这三项能力在客户端层面都是选择启用的：客户端在初始化时声明自己支持哪些能力，服务器只能使用客户端已声明的能力。

### **Elicitation：服务器发起的用户输入**

Elicitation 是 MCP 服务器在执行中途暂停，并要求客户端从用户处收集特定信息的机制。服务器发送一个 elicitation/create JSON-RPC 请求，其中包含一条人类可读的消息和一个描述预期响应的 requestedSchema。客户端将其呈现为表单或 prompt，用户的响应（或明确的拒绝）会返回给服务器，以便继续执行。MCP 规范支持两种 elicitation 模式：

- **Form mode**：直接通过 MCP 客户端收集结构化数据。适合偏好设置、配置输入以及不涉及敏感数据的确认。
- **URL mode**：将用户引导至外部 URL，用于不应经过 MCP 客户端的交互，例如 OAuth 流程、支付处理或凭证输入。

响应采用三动作模型：`accept`（用户提供了数据）、`decline`（用户明确拒绝请求）或 `cancel`（用户未作选择就关闭）。服务器应妥善处理每种情况。以下示例实现了一个 `add_expense_interactive` tool，通过四个连续的 elicitation 步骤收集一笔新支出：金额、描述、类别，以及写入 DynamoDB 前的最终确认。每一步都将其预期输入定义为一个 Pydantic 模型，FastMCP 会将其转换为 `elicitation/create` 请求中发送的 JSON Schema。

**服务器**

`add_expense_interactive` tool 会引导用户依次回答四个问题，然后写入 Amazon DynamoDB。每一步都将预期输入定义为单独的 Pydantic 模型，因为 form mode 的 schema 必须是扁平对象。你可以在一个包含四个属性的模型中收集全部四个字段，但这里将它们拆分，让用户一次只面对一个聚焦的问题，这正是 elicitation 所设计的交互模式。

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

每次 `await ctx.elicit() `都会暂停工具，并通过当前会话发送一个 `elicitation/create` 请求。`isinstance(result, AcceptedElicitation) `检查在每一步统一处理 `decline` 和 `cancel`。

**客户端**

在 `fastmcp.Client` 上注册 `elicitation_handler`，既是接入处理程序的方式，也是客户端在初始化期间向服务器声明支持 elicitation 的方式。

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

对已部署的服务器运行此代码：

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

完整的可运行示例（包括 DynamoDB 设置和 AgentCore 部署）可在 [GitHub 示例仓库](https://github.com/awslabs/amazon-bedrock-agentcore-samples/tree/main/01-tutorials/01-AgentCore-runtime/08-mcp-e2e/02-client-e2e)中获取。

当工具需要的信息依赖先前结果、更适合交互式收集而非预先收集，或因用户而异且无法预先参数化时，就使用 elicitation。一个先搜索目的地、再让用户在其中选择的旅行预订工具就是典型场景；在提交前确认交易金额的金融工作流是另一个例子。elicitation 不适用于密码或 API key 等敏感输入，这类信息应使用 URL 模式或安全的带外通道。

### **Sampling：服务器发起的 LLM 生成**

Sampling 是 MCP 服务器向客户端请求 LLM 补全内容的机制。服务器发送一个 `sampling/createMessage` 请求，其中包含对话消息列表、一条 system prompt 以及可选的模型偏好。客户端将请求转发给它所连接的语言模型（需经用户批准），并返回生成的响应。服务器收到一个结构化结果，其中包含生成的文本、使用的模型和停止原因。

这一能力颠倒了典型流程：不再是客户端向服务器请求工具结果，而是服务器向客户端请求模型输出。好处在于服务器不需要 API key，也无需直接集成模型。客户端对使用哪个模型保有完全控制权，并且 MCP 规范要求设置一个 human-in-the-loop 环节，让用户可以在 sampling 请求被转发之前进行审查和批准。

服务器可以通过能力优先级（`costPriority, speedPriority, intelligencePriority`）和可选的模型提示来表达模型偏好。这些只是建议性的，客户端会根据自己可访问的模型做出最终选择。

**服务器**

`analyze_spending` tool 从 DynamoDB 获取交易记录，基于结构化数据构建一个 prompt，并通过 `ctx.sample()` 将分析工作交给客户端的 LLM。

**agents/mcp_client_features.py**（新增 tool，与 elicitation 位于同一文件）

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

该工具调用 `await ctx.sample()` 后暂停。服务器通过已建立的会话向客户端发送 `sampling/createMessage` 请求。当客户端返回 LLM 响应时，执行恢复。

**客户端**

`sampling_handler` 接收来自服务器的 prompt，并将其转发给语言模型。在本示例中，那就是 Amazon 上的 Claude Haiku。注册该处理程序也是客户端在初始化期间向服务器声明支持 sampling 的方式。

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

对一个已有四条预置支出记录的用户运行此代码：

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

当工具必须生成受益于语言模型能力的自然语言输出时，就使用 sampling。一个已经收集了用户旅行偏好、希望生成量身定制的行程叙述的工具就是很好的例子。sampling 不适用于数据库查询、计算或输出明确的 API 调用等确定性操作。我们建议对这些操作使用工具逻辑。

### **Progress notifications：实时操作反馈**

Progress notifications 是服务器在长时间运行的操作中发送的事件，用于让客户端和用户了解已完成的工作量。`await ctx.report_progress(progress, total)` 发出一条 `notifications/progress` 消息并立即返回。服务器不等待响应，这在两个方向上都是 fire-and-forget。客户端异步接收通知，可以渲染进度条、记录状态行，或用它来避免用户误以为连接已停滞。常见的做法是在多阶段操作的每个逻辑步骤调用 `report_progress`，使进度逐步递增至 total。

**服务器**

`generate_report` tool 分五个步骤生成月度财务报告，并在每一步开始时发出进度通知。

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

每次 await `ctx.report_progress()` 都是 fire-and-forget：通知发出后，执行立即进入下一步。

**客户端**

每当服务器发出通知时，`progress_handler` 都会接收 progress、total 和一条可选消息。注册该处理程序是客户端在初始化期间声明支持进度报告的方式。

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

随着服务器推进其五个阶段，客户端会在原地渲染进度条：

```
  Progress: [####----------------] 20% (1/5)
  Progress: [########------------] 40% (2/5)
  Progress: [############--------] 60% (3/5)
  Progress: [################----] 80% (4/5)
  Progress: [####################] 100% (5/5)  Done!
```

对于任何耗时超过几秒且包含离散、可度量步骤的工具调用，都应使用 progress notifications。搜索多个数据源、执行一系列 API 调用、处理一批记录，或运行多步骤预订工作流等操作都很适合。一秒内即可完成的工具通常不需要进度报告；对快速操作而言，发出事件的开销并不值得。

## **结论**

在本文中，我们向你介绍了 Amazon Bedrock AgentCore Runtime 上的有状态 MCP 客户端能力。我们解释了无状态与有状态 MCP 部署的区别，通过代码示例演示了 elicitation、sampling 和 progress notifications，并展示了如何将有状态 MCP 服务器部署到 AgentCore Runtime。借助这些能力，你可以构建这样的 MCP 服务器：让用户参与结构化对话、使用客户端的 LLM 生成内容，并为长时间运行的操作提供实时可见性——所有这些都托管在由 AgentCore Runtime 驱动的托管隔离基础设施上。我们鼓励你探索以下资源以开始使用：

- [GitHub 示例代码。](https://github.com/awslabs/amazon-bedrock-agentcore-samples/tree/main/01-tutorials/01-AgentCore-runtime/08-mcp-e2e)
- [Amazon Bedrock AgentCore Runtime 文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-how-it-works.html)
- [有状态 MCP 特性文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/mcp-stateful-features.html)
- [MCP 规范 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25)
- [前文：在 AgentCore Runtime 上托管 MCP 服务器](https://aws.amazon.com/blogs/machine-learning/accelerate-development-with-the-amazon-bedrock-agentcore-mcpserver/)

## **关于作者**
