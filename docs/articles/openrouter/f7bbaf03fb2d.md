---
vendor: openrouter
title: LangChain 对比 CrewAI：编排层与 OpenRouter 原生路由之争
original_title: "LangChain vs CrewAI: Orchestration Compared to OpenRouter-Native Routing"
url: https://openrouter.ai/blog/insights/langchain-vs-crewai-orchestration-compared-to-openrouter-native-routing
date: 2026-10-02
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# LangChain 对比 CrewAI：编排层与 OpenRouter 原生路由之争

OpenRouter · 2026-10-02

一个工作流里往往需要不止一个模型：一个低成本模型处理日常调用，一个更强的模型处理难题。LangChain、CrewAI 这类 agent 框架是实现方式之一。两者都提供编排（orchestration）层，但组织方式不同。LangChain 的运行时 LangGraph 给你显式的状态与控制流；CrewAI 把工作组织成基于角色的 agent 和事件驱动的 flow。

当你在构建一个会规划、保持状态、调用工具或委派工作的 agent 时，两个框架都有用。但如果你只需要为每一步选一个模型、失败时回退，一个完整的编排框架就引入了你用不到的零件。

本文按"各自干什么活"来对比 LangChain 与 LangGraph、CrewAI 以及 OpenRouter 原生路由：给出同一个两步流水线直接对接 OpenRouter 与经由 LangChain 的两种写法，说明我们的 Agent SDK 在两者之间的位置，并演示当你同时需要编排与路由时，如何把 OpenRouter 垫在任一框架之下。

## Tl;dr

- 多模型编排是三层。工作流编排是规划、状态、记忆与委派；模型路由是为一次调用选模型并在其报错时 fallback；provider 路由是选择由哪个 provider endpoint 来服务你选定的模型。
- LangGraph 和 CrewAI 做工作流编排，OpenRouter 做模型路由与 provider 路由，二者不能互相替代。
- OpenRouter 的 `models` 参数是一个有序 fallback 列表：第一个模型返回错误时我们试下一个。fallback 由错误驱动，不评判答案质量。
- 我们的 Agent SDK 覆盖的是中间地带：一个带校验、流式和停止条件的有界多轮工具循环，不需要持久化 graph 或角色制 crew。
- LangChain 有专门的 `ChatOpenRouter` 集成，CrewAI 文档将其 `LLM` 类对接 OpenRouter 作为 provider。你可以保留任一框架的编排，把 OpenRouter 用作底下的模型层。

## 被冠以同一个名字的三层

"多模型编排"这个说法覆盖了三种不同的决策。把它们拆开，框架对比就简短了。

**工作流编排**是规划、状态、记忆与委派：把任务拆成步骤、跨轮次跨运行保持状态、停下来等人工审核、把子任务交给其他 agent。LangGraph 和 CrewAI 为这一层而生。

**模型路由**是决定哪个模型处理某次调用，以及该模型返回错误时怎么办。OpenRouter 的 `models` 参数用一个请求字段解决这件事。

**Provider 路由**是决定由哪个 provider endpoint 来服务你已经选好的模型。OpenRouter 上很多模型由不止一家 provider 服务，我们在每次请求时从合格的 provider 中选择；对包含工具的请求，[Auto Exacto](https://openrouter.ai/docs/guides/routing/auto-exacto) 会按工具调用表现重排这些 provider 的顺序。Provider 路由从不改变你要的是哪个模型。

[![三层示意图。顶层的工作流编排覆盖规划、状态、记忆、人工审核与委派，由 LangGraph、CrewAI 或用于有界工具循环的 OpenRouter Agent SDK 提供；中间的模型路由覆盖按调用选模型与经由 OpenRouter models 列表的错误驱动 fallback；底层的 provider 路由覆盖为选定模型挑选 provider endpoint，带工具的请求由 Auto Exacto 重排 provider。](https://openrouter.ai/blog/images/orchestration-model-routing-provider-routing-layers.png)](https://openrouter.ai/blog/images/orchestration-model-routing-provider-routing-layers.png)

一个工作流可能三层都需要：规划逻辑决定下一步做什么，模型路由决定由哪个模型做，provider 路由决定由哪个 endpoint 服务该模型。但你不一定需要第一层才能得到后两层——一个 `models` 列表加几个 `if` 语句，不需要 agent 框架也能在模型之间路由。

## LangChain 与 LangGraph

LangChain 当前的文档描述两个角色不同的产品。LangChain 是 agent 框架，提供面向模型、工具和 agent 循环的抽象与集成；LangGraph 是其下的低层编排运行时，聚焦持久执行、流式、human-in-the-loop 和状态持久化。你可以不用 LangChain 而单用 LangGraph，而 LangChain 的预构建 agent 就跑在 LangGraph 上。

LangGraph 把工作流建模为节点图。同一张图里可以混合确定性的手写步骤与模型驱动的步骤。持久化来自两个组件：checkpointer 保存某个 thread 的图状态，带来会话连续性、容错、时间旅行，以及人工审核的基础；store 在图状态之外保存应用数据，用于长期、跨 thread 的记忆。`interrupt()` 函数可以在节点内任意位置暂停运行、经由 checkpointer 保存状态、等待你用 `Command` 恢复它，从而让人在运行继续之前批准、修改或拒绝某个步骤。

这种控制的代价是控制流要你自己描述。每个节点、边、状态字段、checkpointer 和 interrupt 都是你要写和维护的代码。如果你需要一个每个节点都可检视、可恢复的多步流水线，LangGraph 给你这套结构；如果你只是一个带 fallback 的模型调用，它超出了这份工作所需。

## CrewAI

CrewAI 的文档描述两种积木。Crews 是 agent 团队：每个 agent 由角色、目标（goal）和背景故事（backstory）定义，完成分派的任务。crew 可以按顺序流程运行任务——每个任务的输出成为下一个任务的上下文；也可以按层级流程运行——由 manager 模型或 manager agent 分派并协调任务。启用 `allow_delegation` 后 agents 可以互相委派；每个 agent 有默认为 20 的 `max_iter` 上限，以及可选的 `max_execution_time`。

Flows 是围绕 crews 的、结构化的事件驱动层。一个 flow 定义步骤、在步骤间流转的状态和控制流，包括条件逻辑、循环和分支。每个 flow 实例带一个拥有唯一 ID、在该次运行内持久保存的状态对象。CrewAI 的介绍把 flows 定位为应用的骨架、crews 为 flow 内部的工作单元。

CrewAI 的模型更接近"任务描述"而非"图定义"：你把更多精力花在角色、目标和任务字符串上，更少花在连线上。这与 LangGraph 是另一种取舍，而不是它的缩水版。Crews 留给 agent 自行决定如何完成任务的空间，而 flows 是你把控制权收回来的地方。

## 对比

维度

LangChain 与 LangGraph

CrewAI

OpenRouter 直接调用

为谁而生

基于图的编排，显式状态、持久化与人工审核

事件驱动 flow 中的角色制 agent 团队

按调用选模型、错误驱动 fallback 与 provider 路由

多模型支持

是，每个节点或 agent 一个模型对象

是，每个 agent、crew 或 manager 一个

LLM

是，每个请求一个

models

列表

规划、记忆与委派

是，在 graph、checkpointer 与 store 中显式实现

是，经由 agents、processes 与 flow 状态

否，仅路由

流式

是

是，crew 级别

是，按请求

人工审核

带 checkpointer 的

interrupt()

你自己写的 flow 逻辑

不提供

你要写的东西

节点、边、状态 schema、持久化配置

agent、task、crew 与 flow 定义

一个请求体

## OpenRouter 原生路由

这里的"原生"指不用框架。你向 `https://openrouter.ai/api/v1/chat/completions` 发请求，在 [`models`](https://openrouter.ai/docs/guides/routing/model-fallbacks) 参数里按优先级列出模型，剩下的交给我们。第一个模型返回错误时，我们尝试列表中的下一个。默认任何错误都可能触发 fallback，包括上下文长度校验错误、被过滤模型上的审核标记、限流和宕机。如果 fallback 模型也报错，我们就返回那个错误。请求按最终服务的模型计费，响应中的 `model` 字段告诉你它是哪个。

Fallback 响应的是错误，它不评估第一个模型的答案好不好。如果想让更强的模型审阅更弱模型的输出，那是你代码里的第二步，不是 `models` 列表会替你做的事。

来看一个两步流水线：先用一个模型起草，再用另一个模型审查草稿，且每一步在首个模型报错时 fallback。直接对接 OpenRouter 写，就是一个函数加两份 `models` 列表。

```
import os

import requests


def route(models: list[str], prompt: str) -> tuple[str, str]:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
        json={"models": models, "messages": [{"role": "user", "content": prompt}]},
        timeout=120,
    )
    response.raise_for_status()
    body = response.json()
    return body["choices"][0]["message"]["content"], body["model"]


draft, draft_model = route(
    ["anthropic/claude-sonnet-5", "openai/gpt-5.6-sol"],
    "Draft a one-paragraph summary of what a model fallback list does.",
)
review, review_model = route(
    ["openai/gpt-5.6-sol", "anthropic/claude-sonnet-5"],
    f"Review this draft for accuracy and suggest one improvement:\n\n{draft}",
)
print(f"draft by {draft_model}, review by {review_model}")
print(review)
```

要把某一步发给不同的模型，就改那个列表。因为我们的 API 兼容 OpenAI，同一个 chat completions 请求形态适用于目录中的所有 chat 模型，换模型就是换一个字符串。提供其他 endpoint 的模型——如 embeddings、video、text to speech 或 speech to text——使用各自的请求形态。

同样的流水线经由 LangChain 时，使用专门的 `ChatOpenRouter` 模型类。为每一步创建一个模型对象，用 LangChain 的 `with_fallbacks` 包装以便调用失败时重试下一个模型对象，再通过 `invoke` 调用结果。

```
from langchain_openrouter import ChatOpenRouter

drafter = ChatOpenRouter(model="anthropic/claude-sonnet-5").with_fallbacks(
    [ChatOpenRouter(model="openai/gpt-5.6-sol")]
)
reviewer = ChatOpenRouter(model="openai/gpt-5.6-sol").with_fallbacks(
    [ChatOpenRouter(model="anthropic/claude-sonnet-5")]
)

draft = drafter.invoke("Draft a one-paragraph summary of what a model fallback list does.")
review = reviewer.invoke(
    f"Review this draft for accuracy and suggest one improvement:\n\n{draft.content}"
)
print(review.content)
```

两个版本都在同样的两个模型上以同样的 fallback 顺序路由同样的两步。区别在于 fallback 在哪里执行。直接版本里，我们在单个请求内服务端执行；LangChain 版本里，框架在你的进程内捕获失败的调用并发送第二个请求。对用 LangChain 的 `create_agent` 构建的 agent，框架还提供 `ModelFallbackMiddleware`，在主模型失败时尝试备选模型。框架版本给你模型对象和共享的 `invoke` 接口——当已经存在一张图、一个 checkpointer 或一组工具要管理时，这正是你想要的结构；当这些都不存在时，它就是开销。

无论哪个版本，经由我们路由都附带三样东西。每个响应都包含带 token 数与 credit 成本的 `usage` 对象，无需额外参数——在决定分级方案值不值之前，你能先看到每次调用花了多少。在受支持模型上的 [Prompt caching](https://openrouter.ai/docs/guides/best-practices/prompt-caching) 能降低重复上下文的成本。当请求包含工具时，[Auto Exacto](https://openrouter.ai/docs/guides/routing/auto-exacto) 默认启用：它用吞吐量、工具调用成功率和基准数据为你选定模型的 provider 重排序，让工具调用落在工具调用记录良好的 provider 上，无需你做任何配置。Auto Exacto 改的是 provider 顺序，不是模型。

直接路由不会做规划、不会跨轮次保持状态、也不会决定哪个子任务给哪个 agent。那是工作流编排层的事，`models` 列表不提供。而下一档也不总是完整框架。

## OpenRouter Agent SDK

在直接路由与完整框架之间，是我们的 [Agent SDK](https://openrouter.ai/docs/agent-sdk/overview)——`@openrouter/agent` 包。chat completion 是无状态的：你发 messages，得到一个响应。把它变成 agent 意味着运行一个循环：模型请求一次工具调用，你的代码校验参数并执行工具，结果回给模型，循环往复直到工作完成。Agent SDK 把这个循环封装进一个 `callModel` 函数。

你用 `tool()` 辅助函数加 Zod schema 定义工具，SDK 负责校验、执行和跨轮次的会话状态。`stepCountIs`、`maxCost` 之类的停止条件为循环设界。每个条件在某步完成后检查，所以 `maxCost` 是在达到阈值的那一步之后停止循环，而不是阻止那一步；默认 SDK 随后会再多做一轮模型调用以产出最终答案。请把 `maxCost` 当作停止规则，而不是支出上限。流式是内置的，你还可以把远程 MCP server 接为工具源。

```
import { OpenRouter, tool, stepCountIs, maxCost } from "@openrouter/agent";
import { z } from "zod";

const client = new OpenRouter({ apiKey: process.env.OPENROUTER_API_KEY });

const result = client.callModel({
  model: "anthropic/claude-sonnet-5",
  input: "What time is it in Tokyo?",
  tools: [
    tool({
      name: "get_time",
      description: "Get the current time in a timezone",
      inputSchema: z.object({ timezone: z.string() }),
      execute: async ({ timezone }) => ({
        time: new Date().toLocaleString("en-US", { timeZone: timezone }),
      }),
    }),
  ],
  stopWhen: [stepCountIs(5), maxCost(0.5)],
});

const text = await result.getText();
console.log(text);
```

该 SDK 以 TypeScript 编写，Python 和 Go 移植版保持同步。它给你一个带校验、流式和停止条件的有界工具循环，但不给你持久化 graph、checkpointer 或角色制 crew。

在单次请求内的委派方面，`openrouter:subagent` server tool 允许模型在生成过程中把一个自包含任务交给一个 worker 模型。worker 可以是 OpenRouter 上的任意模型；每个任务相互独立，worker 只能看到任务描述且任务之间不留记忆。Server tools 处于 beta，API 与行为可能变化。

SDK 在这个循环内也支持人工批准和持久化的会话状态。工具可以设置 `requireApproval`，在执行前暂停；`StateAccessor` 可以在多次 `callModel` 调用之间持久化 messages、审批和工具结果。它不给你的是带显式转移与检查点的持久化 graph，或多 agent 团队间的协调。当你需要这些时，就是升级到 LangGraph 或 CrewAI 的时机。

## 在 LangChain 或 CrewAI 之下使用 OpenRouter

你不必在框架和网关之间二选一。你可以保留框架的规划、状态与委派，把 OpenRouter 用作其下的模型层。

在 LangChain 一侧，我们维护一个专门的[集成](https://openrouter.ai/docs/guides/community/langchain)。Python 的 `langchain-openrouter` 包和 JavaScript 的 `@langchain/openrouter` 包都提供 `ChatOpenRouter` 模型，供你的 agents 和 graphs 指向。LangChain 文档目前把 Python 集成标为 beta。

```
from langchain_openrouter import ChatOpenRouter

model = ChatOpenRouter(
    model="anthropic/claude-sonnet-5",
    temperature=0,
    model_kwargs={"models": ["anthropic/claude-sonnet-5", "openai/gpt-5.6-sol"]},
)
```

一个 `ChatOpenRouter` 对象只发送一个 `model` 值。要在 LangChain 下使用我们的服务端 fallback，通过 `model_kwargs` 传入 `models` 列表——该包会把它展开进请求体。不传的话，fallback 就是框架的职责，如上文 `with_fallbacks` 的例子。

在 CrewAI 一侧，你用我们的 endpoint 配置它的 `LLM` 类。CrewAI 的 [LLM 文档](https://docs.crewai.com/en/concepts/llms)把 OpenRouter 列为一个使用 LiteLLM 的 provider：安装 `crewai[litellm]` extra，在模型 slug 前加 `openrouter/`，传入我们的 base URL 和你的 key。

```
import os

from crewai import LLM

llm = LLM(
    model="openrouter/anthropic/claude-sonnet-5",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)
```

这个 CrewAI 示例配置了一个模型。Provider 路由适用于每个请求，更换处理某一步的模型就是改 slug。服务端模型 fallback 只在请求携带 `models` 列表时生效，而 CrewAI 的文档没有覆盖如何传该字段。两种情况下，你的 graphs 或 crews 都按设计继续工作，而触达不同模型的改动只是一个配置变更——不需要新的 provider 集成，也不需要每个模型一把 API key。

## 选择层次

如果你的直接实现开始积累状态机、可恢复检查点、审批步骤和委派规则，那你就是在手工搭建一个工作流编排层——框架能替代你本来要自己设计和维护的那些代码。以下是我们的编辑性建议而非产品保证，它从"你的应用必须自己拥有的行为"出发。

- 当工作流已经清晰、你只需要按调用选模型、加一个 fallback 列表或控制 provider 路由时，用 OpenRouter 原生路由。
- 当你需要一个带校验、流式和停止条件的有界多轮工具循环，而不需要持久化 graph 或角色制 crew 时，用 OpenRouter Agent SDK。
- 当你需要显式状态转移、持久化、故障恢复、人工审核，或确定性步骤与模型驱动步骤混合时，用 LangGraph。
- 当工作可以映射到专家 agent、任务委派和顺序或层级协作，且外围应用需要结构化状态与控制时用 flows——这是 CrewAI 的场景。
- 当你想让框架掌握编排、OpenRouter 掌握模型访问与 provider 路由时，把 OpenRouter 垫在 LangGraph 或 CrewAI 之下；在框架转发 `models` 列表的地方获得服务端模型 fallback。

## 结论

多模型编排是三层。工作流编排是规划、状态、记忆与委派，LangGraph 和 CrewAI 各以不同的取舍为此而生：LangGraph 给你显式的图控制，代价是控制流要你自己写；CrewAI 给你角色制 agents 和 flows，代价是把更多执行路径留给 agent。模型路由与 provider 路由是 OpenRouter 做的事——无论上面有没有框架，我们做它们的方式都一样。

如果你不确定自己的项目落在界线哪一边，先试承诺更小的那个。先用一个 `models` 列表把两步工作流路由到两个模型上，再决定是否需要上面架一个框架。无论哪种方式，在选择模型时，[models 目录](https://openrouter.ai/models)支持按受支持参数（包括 `tools`）过滤。

## 常见问题

### 使用多个模型需要 LangChain 或 CrewAI 吗？

不需要。如果你的全部需求只是为一次调用选模型、并在第一个模型报错时回退到另一个模型，OpenRouter 的 `models` 参数在一个请求里就能做到。当工作流还需要规划、持久状态、记忆、人工审核或 agent 间委派时，才选 LangGraph 或 CrewAI。

### 如何在一个 agent 工作流里编排多个 LLM？

把层次拆开。跨步骤的规划、状态与委派，用 LangGraph 或 CrewAI 这样的编排框架。决定每次调用由哪个模型处理，就向 OpenRouter 发送一个有序 `models` 列表，让第一个模型报错时我们回退到下一个。我们还会为实际服务的模型选择 provider endpoint。一个工作流可以两者兼用：框架在上，OpenRouter 在下作为模型层。

### 我可以把 OpenRouter 和 LangChain 或 CrewAI 一起用，而不是二选一吗？

可以。LangChain 有专门的 `ChatOpenRouter` 集成（Python 的 `langchain-openrouter` 包和 JavaScript 的 `@langchain/openrouter` 包）；CrewAI 文档通过其基于 LiteLLM 的 `LLM` 类把 OpenRouter 列为 provider。两种情况下框架保留编排，OpenRouter 提供模型访问与 provider 路由。我们的服务端模型 fallback 只在请求携带 `models` 列表时运行，`ChatOpenRouter` 会通过其 `model_kwargs` 参数转发该列表。

### 采用 LangChain 或 CrewAI 会把我锁死在某一家模型 provider 上吗？

只要把框架指向 OpenRouter 而不是某一家 provider 的 SDK，就不会。两个框架都接受 OpenRouter 作为模型 provider，更换处理某一步的模型只是改框架配置里的模型字符串，而不是重写 provider 集成。你始终保有 OpenRouter 上所有模型的访问。

### OpenRouter 的模型 fallback 会评判答案质量吗？

不会。Fallback 由错误驱动。当 `models` 列表中的第一个模型返回错误——上下文长度校验错误、审核标记、限流或宕机——我们尝试列表中的下一个。成功返回的响应原样给出，响应的 `model` 字段告诉你它是哪个模型产出的。

## 参考

- [Model Fallbacks](https://openrouter.ai/docs/guides/routing/model-fallbacks)，OpenRouter
- [Provider Routing](https://openrouter.ai/docs/guides/routing/provider-selection)，OpenRouter
- [Auto Exacto](https://openrouter.ai/docs/guides/routing/auto-exacto)，OpenRouter
- [Prompt Caching](https://openrouter.ai/docs/guides/best-practices/prompt-caching)，OpenRouter
- [Tool Calling](https://openrouter.ai/docs/guides/features/tool-calling)，OpenRouter
- [Agent SDK](https://openrouter.ai/docs/agent-sdk/overview) 与 [Stop Conditions](https://openrouter.ai/docs/agent-sdk/call-model/stop-conditions)，OpenRouter
- [Subagent server tool](https://openrouter.ai/docs/guides/features/server-tools/subagent)，OpenRouter
- [LangChain 集成](https://openrouter.ai/docs/guides/community/langchain)，OpenRouter
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)、[Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) 与 [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)，LangChain
- [ChatOpenRouter](https://docs.langchain.com/oss/python/integrations/chat/openrouter) 与 [Built-in middleware](https://docs.langchain.com/oss/python/langchain/middleware/built-in)，LangChain
- [Introduction](https://docs.crewai.com/en/introduction)、[Flows](https://docs.crewai.com/en/concepts/flows)、[Processes](https://docs.crewai.com/en/concepts/processes)、[Agents](https://docs.crewai.com/en/concepts/agents) 与 [LLMs](https://docs.crewai.com/en/concepts/llms)，CrewAI
