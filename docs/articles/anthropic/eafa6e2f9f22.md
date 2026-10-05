---
vendor: anthropic
title: Claude 开发者平台推出高级工具使用功能
original_title: Introducing advanced tool use on the Claude Developer Platform \ Anthropic
url: https://www.anthropic.com/engineering/advanced-tool-use
date: 2025-11-24
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: bd92895dac14
translator: agent
---

Anthropic 工程实践

# Claude 开发者平台推出高级工具使用功能

发布于 2025 年 11 月 24 日

我们新增了三项 beta 功能，让 Claude 可以动态地发现、学习并执行工具。下面介绍它们的工作方式。

AI agent 的未来，是模型能在成百上千个工具之间自如协作。一个 IDE 助手，整合 git 操作、文件处理、包管理器、测试框架和部署流水线；一个运营协调者，同时连接 Slack、GitHub、Google Drive、Jira 和公司数据库，外加几十个 MCP server。

要[构建高效的 agent](https://www.anthropic.com/research/building-effective-agents)，它们需要能使用规模不设上限的工具库，而不是把所有工具定义预先塞进上下文。我们关于[结合代码执行与 MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)的博客文章讨论过：工具结果和定义有时在 agent 读到请求之前就消耗了 50,000 多个 token。Agent 应当按需发现和加载工具，只保留与当前任务相关的内容。

Agent 还需要能从代码里调用工具。使用自然语言的工具调用时，每次调用都需要一轮完整的推理，中间结果无论有用与否都会不断堆积在上下文里。代码天生适合编排逻辑，比如循环、条件判断和数据转换。Agent 需要能在代码执行与推理之间，根据手头任务灵活选择。

Agent 还需要能从示例中学习正确的工具用法，而不只是看 schema 定义。JSON schema 能说明什么在结构上是合法的，但表达不了使用模式：何时该带上可选参数、哪些参数组合有意义、你的 API 遵循什么约定。

今天发布的三项功能让这一切成为可能：

- **Tool Search Tool**（工具搜索工具），让 Claude 能通过搜索工具访问上千个工具，而不占用其上下文窗口
- **Programmatic Tool Calling**（程序化工具调用），让 Claude 在代码执行环境里调用工具，降低对模型上下文窗口的影响
- **Tool Use Examples**（工具使用示例），提供展示某个工具正确用法的通用标准

在内部测试中，我们发现这些功能帮助我们做出了一些用传统工具使用模式根本做不出来的东西。例如，**[Claude for Excel](https://www.claude.com/claude-for-excel)** 就使用 Programmatic Tool Calling 来读写包含数千行的电子表格，而不会挤爆模型的上下文窗口。

基于我们的经验，我们认为这些功能为"你能用 Claude 构建什么"打开了新的可能。

## Tool Search Tool

### 挑战

MCP 的工具定义提供了重要上下文，但随着接入的 server 越来越多，这些 token 会不断累积。设想一个五个 server 的配置：

- GitHub：35 个工具（约 26K token）
- Slack：11 个工具（约 21K token）
- Sentry：5 个工具（约 3K token）
- Grafana：5 个工具（约 3K token）
- Splunk：2 个工具（约 2K token）

对话还没开始，58 个工具就已消耗约 55K token。再加上 Jira（仅它就约 17K token）这类 server，很快就要面对 100K+ token 的开销。在 Anthropic 内部，我们见过工具定义在优化前消耗 134K token 的情况。

但 token 成本并不是唯一的问题。最常见的失败是选错工具和参数错误，尤其是在工具名字相似的时候，比如 `notification-send-user` 和 `notification-send-channel`。

### 我们的方案

Tool Search Tool 按需发现工具，而不是把所有工具定义预先加载。Claude 只看到当前任务真正需要的工具。

Tool Search Tool 保留了 191,300 token 的上下文，而 Claude 传统方式只剩 122,800。

传统方式：

- 所有工具定义预先加载（50 多个 MCP 工具约 72K token）
- 对话历史和 system prompt 争抢剩余空间
- 总上下文消耗：还没干活就约 77K token

使用 Tool Search Tool：

- 预先加载的只有 Tool Search Tool 本身（约 500 token）
- 工具按需发现（3-5 个相关工具，约 3K token）
- 总上下文消耗：约 8.7K token，保留了 95% 的上下文窗口

这相当于节省 85% 的 token 用量，同时保留对完整工具库的访问。内部测试显示，在处理大型工具库时，MCP 评测的准确率有显著提升：启用 Tool Search Tool 后，Opus 4 从 49% 提升到 74%，Opus 4.5 从 79.5% 提升到 88.1%。

### Tool Search Tool 如何工作

Tool Search Tool 让 Claude 动态发现工具，而不是预先加载所有定义。你把全部工具定义提供给 API，但用 `defer_loading: true` 标记某些工具，让它们可被按需发现。被延迟的工具初始不会加载进 Claude 的上下文。Claude 只看到 Tool Search Tool 本身，加上标记为 `defer_loading: false` 的工具（你最关键、最常用的那几个）。

当 Claude 需要某种能力时，它会搜索相关工具。Tool Search Tool 返回匹配工具的引用，这些引用随后被展开成完整定义进入 Claude 的上下文。

比如，Claude 需要与 GitHub 交互时，它会搜索 "github"，于是只有 `github.createPullRequest` 和 `github.listIssues` 被加载——而不是你从 Slack、Jira 和 Google Drive 来的另外 50 多个工具。

这样一来，Claude 能访问你的完整工具库，却只为真正要用的工具支付 token 成本。

**Prompt 缓存说明：**Tool Search Tool 不会破坏 prompt 缓存，因为被延迟的工具完全不进初始 prompt。它们只在 Claude 搜索之后才加入上下文，所以你的 system prompt 和核心工具定义仍然可缓存。

**实现：**

```
{
  "tools": [
    // Include a tool search tool (regex, BM25, or custom)
    {"type": "tool_search_tool_regex_20251119", "name": "tool_search_tool_regex"},

    // Mark tools for on-demand discovery
    {
      "name": "github.createPullRequest",
      "description": "Create a pull request",
      "input_schema": {...},
      "defer_loading": true
    }
    // ... hundreds more deferred tools with defer_loading: true
  ]
}
```

对于 MCP server，你可以把整个 server 延迟加载，只让高频工具保持加载：

```
{
  "type": "mcp_toolset",
  "mcp_server_name": "google-drive",
  "default_config": {"defer_loading": true}, # defer loading the entire server
  "configs": {
    "search_files": {
"defer_loading": false
    }  // Keep most used tool loaded
  }
}
```

Claude 开发者平台开箱提供基于正则和 BM25 的搜索工具，你也可以实现自定义搜索工具，比如基于嵌入向量或其他策略。

### 何时使用 Tool Search Tool

和所有架构决策一样，启用 Tool Search Tool 有得有失。该功能在工具调用前增加了一个搜索步骤，所以只有当上下文节省和准确率提升超过额外延迟时，投入产出比才最高。

**适合使用的场景：**

- 工具定义消耗超过 10K token
- 遇到工具选择准确率问题
- 构建使用多个 server 的 MCP 系统
- 可用工具超过 10 个

**收益较小的场景：**

- 工具库很小（少于 10 个工具）
- 每次会话所有工具都会用到
- 工具定义本身很紧凑

## Programmatic Tool Calling

### 挑战

随着工作流越来越复杂，传统工具调用会产生两个根本问题：

- **中间结果污染上下文**：当 Claude 分析一个 10MB 的日志文件找错误模式时，整个文件都会进入它的上下文窗口，哪怕它只需要一份错误频率摘要。当跨多张表拉取客户数据时，无论相关与否，每条记录都会堆在上下文里。这些中间结果吞噬大量 token，甚至可能把重要信息直接挤出上下文窗口。
- **推理开销与人工拼接**：每次工具调用都需要一轮完整的模型推理。拿到结果后，Claude 必须"肉眼"扫描数据、提取相关信息、推理各部分如何关联，再决定下一步——一切都要通过自然语言处理完成。一个五工具的工作流意味着五轮推理，外加 Claude 逐一解析每个结果、比对数值、综合结论。既慢又容易出错。

### 我们的方案

Programmatic Tool Calling 让 Claude 通过代码而不是逐个 API 往返来编排工具。Claude 不再一次请求一个工具、每个结果都返回到它的上下文，而是编写代码：代码调用多个工具、处理它们的输出，并决定哪些信息真正进入上下文窗口。

Claude 擅长写代码，让它用 Python 表达编排逻辑，而不是通过自然语言逐次调用工具，你会得到更可靠、更精确的控制流。循环、条件、数据转换和错误处理都明确写在代码里，而不是隐含在 Claude 的推理中。

#### 示例：预算合规检查

设想一个常见的业务任务："哪些团队成员超出了第三季度的差旅预算？"

你有三个可用工具：

- `get_team_members(department)` - 返回含 ID 和职级的团队成员列表
- `get_expenses(user_id, quarter)` - 返回某个用户的费用明细
- `get_budget_by_level(level)` - 返回某个职级的预算上限

**传统做法**：

- 拉取团队成员 → 20 人
- 为每个人拉取其 Q3 费用 → 20 次工具调用，每次返回 50-100 条明细（机票、酒店、餐费、票据）
- 按职级拉取预算上限
- 以上全部进入 Claude 的上下文：2,000 多条费用明细（50 KB 以上）
- Claude 要手动逐个加总每个人的费用、查其预算、把费用与预算上限逐条比对
- 更多的模型往返，巨大的上下文消耗

**使用 Programmatic Tool Calling**：

不再让每个工具结果都返回给 Claude，而是由 Claude 写一个 Python 脚本来编排整个工作流。脚本在 Code Execution 工具（一个沙箱环境）中运行，需要工具结果时暂停。当你通过 API 返回工具结果时，结果由脚本处理，而不是被模型消化。脚本继续执行，Claude 只看到最终输出。

Programmatic Tool Calling 让 Claude 通过代码而非逐个 API 往返来编排工具，从而支持工具并行执行。

针对预算合规任务，Claude 的编排代码是这样的：

```
team = await get_team_members("engineering")

# Fetch budgets for each unique level
levels = list(set(m["level"] for m in team))
budget_results = await asyncio.gather(*[
    get_budget_by_level(level) for level in levels
])

# Create a lookup dictionary: {"junior": budget1, "senior": budget2, ...}
budgets = {level: budget for level, budget in zip(levels, budget_results)}

# Fetch all expenses in parallel
expenses = await asyncio.gather(*[
    get_expenses(m["id"], "Q3") for m in team
])

# Find employees who exceeded their travel budget
exceeded = []
for member, exp in zip(team, expenses):
    budget = budgets[member["level"]]
    total = sum(e["amount"] for e in exp)
    if total > budget["travel_limit"]:
        exceeded.append({
            "name": member["name"],
            "spent": total,
            "limit": budget["travel_limit"]
        })

print(json.dumps(exceeded))
```

Claude 的上下文只收到最终结果：超预算的那两三个人。2,000 多条明细、中间加总、预算查询都不影响 Claude 的上下文，消耗从 200KB 的原始费用数据降到仅 1KB 的结果。

效率收益非常可观：

- **Token 节省**：把中间结果挡在 Claude 上下文之外，PTC 大幅降低 token 消耗。在复杂研究任务上，平均用量从 43,588 降到 27,297 token，减少 37%。
- **降低延迟**：每次 API 往返都需要模型推理（几百毫秒到几秒）。当 Claude 在单个代码块里编排 20 多次工具调用时，你就省掉了其中 19 轮以上的推理。API 直接处理工具执行，无需每次都返回给模型。
- **提升准确率**：通过编写显式的编排逻辑，Claude 比在自然语言里同时摆弄多个工具结果犯错更少。内部知识检索从 25.6% 提升到 28.5%；[GIA 基准](https://arxiv.org/abs/2311.12983)从 46.5% 提升到 51.2%。

生产环境的工作流总有脏数据、条件逻辑和需要扩展的操作。Programmatic Tool Calling 让 Claude 以编程方式处理这些复杂性，同时把注意力放在可行动的结果上，而不是原始数据的加工上。

### Programmatic Tool Calling 如何工作

#### 1. 标记可从代码调用的工具

在 tools 中加入 code_execution，并设置 allowed_callers 来选择性开启工具的程序化执行：

```
{
  "tools": [
    {
      "type": "code_execution_20250825",
      "name": "code_execution"
    },
    {
      "name": "get_team_members",
      "description": "Get all members of a department...",
      "input_schema": {...},
      "allowed_callers": ["code_execution_20250825"] # opt-in to programmatic tool calling
    },
    {
      "name": "get_expenses",
 	...
    },
    {
      "name": "get_budget_by_level",
	...
    }
  ]
}
```

API 会把这些工具定义转换为 Claude 可以调用的 Python 函数。

#### 2. Claude 编写编排代码

Claude 不逐个请求工具，而是生成 Python 代码：

```
{
  "type": "server_tool_use",
  "id": "srvtoolu_abc",
  "name": "code_execution",
  "input": {
    "code": "team = get_team_members('engineering')\n..." # the code example above
  }
}
```

#### 3. 工具执行不触碰 Claude 的上下文

当代码调用 get_expenses() 时，你会收到一个带 caller 字段的工具请求：

```
{
  "type": "tool_use",
  "id": "toolu_xyz",
  "name": "get_expenses",
  "input": {"user_id": "emp_123", "quarter": "Q3"},
  "caller": {
    "type": "code_execution_20250825",
    "tool_id": "srvtoolu_abc"
  }
}
```

你提供结果，结果在 Code Execution 环境中处理，而不是进入 Claude 的上下文。这个请求-响应循环对代码中的每个工具调用重复执行。

#### 4. 只有最终输出进入上下文

代码运行结束后，只有代码的结果返回给 Claude：

```
{
  "type": "code_execution_tool_result",
  "tool_use_id": "srvtoolu_abc",
  "content": {
    "stdout": "[{\"name\": \"Alice\", \"spent\": 12500, \"limit\": 10000}...]"
  }
}
```

这就是 Claude 看到的全部内容，而不是中途处理的 2,000 多条费用明细。

### 何时使用 Programmatic Tool Calling

Programmatic Tool Calling 在工作流中加入了一个代码执行步骤。只有当 token 节省、延迟改善和准确率提升都相当可观时，这一步的额外开销才划得来。

**收益最大的场景：**

- 处理大数据集，而你只需要聚合值或摘要
- 运行包含三个以上相互依赖的工具调用的多步工作流
- 在 Claude 看到工具结果之前先过滤、排序或转换
- 处理中间数据不应影响 Claude 推理的任务
- 对大量条目做并行操作（例如检查 50 个 endpoint）

**收益较小的场景：**

- 简单的单工具调用
- Claude 应该看到并对所有中间结果进行推理的任务
- 响应很小的快速查询

## Tool Use Examples

### 挑战

JSON Schema 擅长定义结构——类型、必填字段、允许的枚举值——但它表达不了使用模式：何时该带上可选参数、哪些组合有意义、你的 API 遵循什么约定。

看一个工单 API：

```
{
  "name": "create_ticket",
  "input_schema": {
    "properties": {
      "title": {"type": "string"},
      "priority": {"enum": ["low", "medium", "high", "critical"]},
      "labels": {"type": "array", "items": {"type": "string"}},
      "reporter": {
        "type": "object",
        "properties": {
          "id": {"type": "string"},
          "name": {"type": "string"},
          "contact": {
            "type": "object",
            "properties": {
              "email": {"type": "string"},
              "phone": {"type": "string"}
            }
          }
        }
      },
      "due_date": {"type": "string"},
      "escalation": {
        "type": "object",
        "properties": {
          "level": {"type": "integer"},
          "notify_manager": {"type": "boolean"},
          "sla_hours": {"type": "integer"}
        }
      }
    },
    "required": ["title"]
  }
}
```

schema 定义了什么是合法的，却留下了一堆关键问题没有答案：

- **格式歧义**：`due_date` 该用 "2024-11-06"、"Nov 6, 2024"，还是 "2024-11-06T00:00:00Z"？
- **ID 约定**：`reporter.id` 是 UUID、"USR-12345"，还是就 "12345"？
- **嵌套结构用法**：什么时候该填 `reporter.contact`？
- **参数关联**：`escalation.level` 和 `escalation.sla_hours` 与 priority 是什么关系？

这些歧义会导致工具调用不合法、参数使用不一致。

### 我们的方案

Tool Use Examples 让你直接在工具定义里提供示例调用。不是只依赖 schema，而是向 Claude 展示具体的使用模式：

```
{
    "name": "create_ticket",
    "input_schema": { /* same schema as above */ },
    "input_examples": [
      {
        "title": "Login page returns 500 error",
        "priority": "critical",
        "labels": ["bug", "authentication", "production"],
        "reporter": {
          "id": "USR-12345",
          "name": "Jane Smith",
          "contact": {
            "email": "jane@acme.com",
            "phone": "+1-555-0123"
          }
        },
        "due_date": "2024-11-06",
        "escalation": {
          "level": 2,
          "notify_manager": true,
          "sla_hours": 4
        }
      },
      {
        "title": "Add dark mode support",
        "labels": ["feature-request", "ui"],
        "reporter": {
          "id": "USR-67890",
          "name": "Alex Chen"
        }
      },
      {
        "title": "Update API documentation"
      }
    ]
  }
```

从这三个示例中，Claude 学到：

- **格式约定**：日期用 YYYY-MM-DD，用户 ID 遵循 USR-XXXXX，标签用 kebab-case
- **嵌套结构模式**：如何构造带嵌套 contact 对象的 reporter 对象
- **可选参数的关联规律**：紧急 bug 会带完整联系方式 + 严格 SLA 的升级信息；功能请求有 reporter 但没有 contact/escalation；内部任务只有 title

在我们自己的内部测试中，工具使用示例把复杂参数处理的准确率从 72% 提升到 90%。

### 何时使用 Tool Use Examples

Tool Use Examples 会给工具定义增加 token，所以只有当准确率提升大于额外成本时，它才最有价值。

**收益最大的场景：**

- 复杂的嵌套结构——合法的 JSON 并不暗示正确的用法
- 可选参数很多、何时包含哪些参数很要紧的工具
- 有 schema 表达不了的领域特定约定的 API
- 相似的工具——示例能说明该用哪个（如 `create_ticket` 与 `create_incident`）

**收益较小的场景：**

- 用法显而易见的单参数简单工具
- Claude 本来就懂的标准格式，如 URL 或邮箱
- 更适合用 JSON Schema 约束解决的校验问题

## 最佳实践

构建在真实世界采取行动的 agent，意味着同时应对规模、复杂度和精确性。这三项功能协同解决工具使用工作流中不同的瓶颈。下面是如何有效地组合它们。

### 按策略分层使用功能

不是每个 agent 在每个任务上都需要三项全用。从你最大的瓶颈入手：

- 工具定义撑爆上下文 → Tool Search Tool
- 大量中间结果污染上下文 → Programmatic Tool Calling
- 参数错误和调用不合法 → Tool Use Examples

这种抓重点的做法让你针对制约 agent 性能的具体瓶颈下手，而不是一上来就堆复杂度。

然后再按需叠加其他功能。它们是互补的：Tool Search Tool 保证找对工具，Programmatic Tool Calling 保证高效执行，Tool Use Examples 保证正确调用。

### 为更好的发现而配置 Tool Search Tool

工具搜索靠匹配名称和描述，所以清晰、有描述性的定义能提升发现准确率。

```
// Good
{
    "name": "search_customer_orders",
    "description": "Search for customer orders by date range, status, or total amount. Returns order details including items, shipping, and payment info."
}

// Bad
{
    "name": "query_db_orders",
    "description": "Execute order query"
}
```

在 system prompt 里加引导，让 Claude 知道都有哪些工具可用：

```
You have access to tools for Slack messaging, Google Drive file management, 
Jira ticket tracking, and GitHub repository operations. Use the tool search 
to find specific capabilities.
```

让你最常用的三到五个工具始终保持加载，其余全部延迟。这样常见操作可以立即访问，其他一切则按需发现。

### 为正确执行而配置 Programmatic Tool Calling

由于 Claude 要写代码解析工具输出，请清楚地为返回格式写文档，这能帮助 Claude 写出正确的解析逻辑：

```
{
    "name": "get_orders",
    "description": "Retrieve orders for a customer.
Returns:
    List of order objects, each containing:
    - id (str): Order identifier
    - total (float): Order total in USD
    - status (str): One of 'pending', 'shipped', 'delivered'
    - items (list): Array of {sku, quantity, price}
    - created_at (str): ISO 8601 timestamp"
}
```

下面这些特征的工具适合开启程序化编排：

- 可以并行运行的工具（相互独立的操作）
- 可安全重试的操作（幂等）

### 为参数准确而配置 Tool Use Examples

为行为清晰度而打磨示例：

- 使用真实感的数据（真实的城市名、合理的价格，而不是 "string" 或 "value"）
- 展示多样性：最小化、部分、完整三种填写模式
- 保持精炼：每个工具 1-5 个示例
- 聚焦歧义（只在正确用法无法从 schema 一眼看出的地方加示例）

## 开始使用

这些功能以 beta 形式提供。要启用它们，请添加 beta header 并带上你需要的工具：

```
client.beta.messages.create(
    betas=["advanced-tool-use-2025-11-20"],
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    tools=[
        {"type": "tool_search_tool_regex_20251119", "name": "tool_search_tool_regex"},
        {"type": "code_execution_20250825", "name": "code_execution"},
        # Your tools with defer_loading, allowed_callers, and input_examples
    ]
)
```

详细的 API 文档和 SDK 示例见我们的：

- Tool Search Tool 的[文档](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)和 [cookbook](https://github.com/anthropics/claude-cookbooks/blob/main/tool_use/tool_search_with_embeddings.ipynb)
- Programmatic Tool Calling 的[文档](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling)和 [cookbook](https://github.com/anthropics/claude-cookbooks/blob/main/tool_use/programmatic_tool_calling_ptc.ipynb)
- Tool Use Examples 的[文档](https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use#providing-tool-use-examples)

这些功能把工具使用从简单的函数调用推向智能编排。当 agent 开始处理横跨几十个工具、大量数据的更复杂工作流时，动态发现、高效执行和可靠调用将成为基石。

我们很期待看到你做出的东西。

## 致谢

本文由 Bin Wu 撰写，Adam Jones、Artur Renault、Henry Tay、Jake Noble、Noah Picard、Sam Jiang 以及 Claude 开发者平台团队均有贡献。这项工作建立在 Chris Gorgolewski、Daniel Jiang、Jeremy Fox 和 Mike Lambert 的基础研究之上。我们还从整个 AI 生态中汲取灵感，包括 [Joel Pobar 的 LLMVM](https://github.com/9600dev/llmvm)、[Cloudflare 的 Code Mode](https://blog.cloudflare.com/code-mode/) 和 [Code Execution as MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)。特别感谢 Andy Schumeister、Hamish Kerr、Keir Bradwell、Matt Bleifer 和 Molly Vorwerck 的支持。

## 订阅开发者通讯

产品更新、实操指南、社区风采等，每月送达你的邮箱。
