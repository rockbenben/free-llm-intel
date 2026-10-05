---
vendor: openrouter
title: 在 OpenRouter 上构建可靠的工具调用智能体循环
original_title: Build a Reliable Tool-Calling Agent Loop on OpenRouter
url: https://openrouter.ai/blog/tutorials/build-tool-calling-agent-loop
date: 2026-09-17
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: a846e4b2d52a
translator: agent
---

# 在 OpenRouter 上构建可靠的工具调用智能体循环

OpenRouter ·9/17/2026 · 更新于 9/24/2026

工具调用 agent 循环做的事，是反复把对话和可用工具发给模型，执行模型请求的任何工具调用，把结果追加进去，再问模型下一步做什么。当模型不再返回工具调用、或应用自定义的停止条件被触发时，循环结束。

模型决定请求哪个工具，但解析参数、运行函数、判断循环何时必须停止，都是你应用的事。

本指南演示如何用 OpenRouter TypeScript SDK 搭这个循环。示例用本地天气数据，不接任何其他服务也能直接跑。

## 太长不看

- 模型请求工具。你的应用执行它们，并按工具调用 ID 每个调用返回一个结果。
- 每次请求都要带上工具定义，包括拿到工具结果后的后续请求。
- 停止条件：模型不再返回工具调用、同一调用重复超过限制、或到达迭代上限。
- `models` 参数给你有序模型回退；Auto Exacto 默认在工具调用请求上重排提供商。

## 工具调用 agent 循环如何工作

准备好任务、工具和消息历史，然后重复以下步骤：

- 带上完整历史和工具定义调用模型。
- 响应没有工具调用，就返回 assistant 文本并停止。
- 如果这已是最后一个被允许的迭代，在执行工具之前停。它们的结果永远到不了模型那里。
- 某个调用重复次数过多，就停止。
- 否则，执行每个工具调用，追加 assistant 消息和每调用一条结果。

循环还需要一个硬上限。模型可能反复重试一个失败的调用，或不断寻找更好的答案。没有迭代封顶，这个行为会一直持续，直到系统的其他部分把它掐掉。

搭建和理解这条控制流不需要 AI agent 框架。就算你日后把循环迁进某个库，一份小实现依然有用。

## 第 1 步：初始化客户端并定义工具

创建 TypeScript 项目，安装 [OpenRouter TypeScript SDK](https://openrouter.ai/docs/client-sdks/typescript/overview) 和 tsx：

```
mkdir openrouter-agent-loop
cd openrouter-agent-loop
npm init -y
npm pkg set type=module
npm install @openrouter/sdk
npm install --save-dev tsx
```

创建一个 [OpenRouter API key](https://openrouter.ai/settings/keys)，让进程能读到它：

```
export OPENROUTER_API_KEY="your-api-key"
```

创建 `agent.ts`，加入客户端、一个有序模型列表和一个本地工具：

```
import { OpenRouter } from "@openrouter/sdk";
import type { ChatMessages, ChatToolCall } from "@openrouter/sdk/models";

if (!process.env.OPENROUTER_API_KEY) {
  throw new Error("Set OPENROUTER_API_KEY before running this example");
}

const openRouter = new OpenRouter({
  apiKey: process.env.OPENROUTER_API_KEY,
});

const models = [
  "google/gemini-3-flash-preview",
  "nvidia/nemotron-3.5-lightning",
];

const tools = [
  {
    type: "function" as const,
    function: {
      name: "get_weather",
      description: "Get local sample weather data for Lagos or London",
      parameters: {
        type: "object",
        properties: {
          city: { type: "string", enum: ["Lagos", "London"] },
        },
        required: ["city"],
        additionalProperties: false,
      },
    },
  },
];

const weatherByCity: Record<
  string,
  { temperatureC: number; conditions: string }
> = {
  lagos: { temperatureC: 29, conditions: "partly cloudy" },
  london: { temperatureC: 18, conditions: "overcast" },
};
```

工具定义告诉模型何时该用这个函数、接受哪些参数。函数本体留在你的应用里，因为只有你的代码能运行它。

描述要具体，把模型正确使用该工具所需的信息写进去。这里的做法是点名两个支持的城市，帮模型生成合法参数。

列表里的两个模型都支持工具调用。模型的可用性会随时间变化，选定自己的列表之前，先到[模型目录](https://openrouter.ai/models?supported_parameters=tools)查当前支持 `tools` 参数的模型。

## 第 2 步：调用模型并读取响应

接着加一个 helper，发一次模型请求，返回 assistant 消息和全部工具调用：

```
async function sendTurn(
  messages: ChatMessages[],
  toolChoice: "required" | "auto",
) {
  const result = await openRouter.chat.send({
    chatRequest: {
      models,
      messages,
      tools,
      toolChoice,
      maxCompletionTokens: 1024,
      stream: false,
    },
  });

  if (!("choices" in result)) {
    throw new Error("Expected a non-streaming response");
  }

  const message = result.choices[0]?.message;

  if (!message) throw new Error("The model returned no message");

  return {
    result,
    message,
    calls: message.toolCalls ?? [],
  };
}
```

SDK 把请求体嵌在 `chatRequest` 下，字段用驼峰：`toolChoice`、`maxCompletionTokens`、`toolCalls`。它转换成 API 的 snake_case 线格式发送，所以 `toolChoice` 出门时是 `tool_choice`。

每次调用都保留 `tools`，包括后续调用。我们用这些定义校验模型返回的工具调用，模型也需要它们来判断还有没有别的工具能帮忙。

第一轮用 `toolChoice: "required"`，让示例必定走一遍工具路径。之后的轮次用 `"auto"`，让模型在拿到工具结果后可以返回最终答案。如果每轮都强制调工具，模型就没有办法用文本收尾。这是示例的选择，不是 API 默认值——有 tools 时 `tool_choice` 的 API 默认就是 `"auto"`。

## 第 3 步：执行工具调用并返回结果

加一个 helper，执行一个工具调用，生成将发回模型的工具消息：

```
async function executeToolCall(call: ChatToolCall): Promise<ChatMessages> {
  let content: string;

  try {
    if (call.function.name !== "get_weather") {
      throw new Error(`Unknown tool: ${call.function.name}`);
    }

    const args = JSON.parse(call.function.arguments) as { city?: unknown };

    if (typeof args.city !== "string") {
      throw new Error("city must be a string");
    }

    const weather = weatherByCity[args.city.toLowerCase()];

    if (!weather) {
      throw new Error(`No weather data for ${args.city}`);
    }

    content = JSON.stringify({ city: args.city, ...weather });
  } catch (error) {
    content = JSON.stringify({
      error: error instanceof Error ? error.message : String(error),
    });
  }

  return {
    role: "tool",
    toolCallId: call.id,
    content,
  };
}
```

工具参数以 JSON 字符串到达，所以 `JSON.parse()` 要放在 `try` 块里。非法 JSON、未知函数名或失败的处理函数，都会变成一个工具结果而不是让循环崩溃。模型随后可以改参数、换工具，或解释这次失败。

结果还携带原调用 ID 作为 `toolCallId`，模型就靠它把每条结果对上发起它的调用。一个响应可以包含多个调用，每个都需要自己的结果。

本示例把预期的解析和执行失败返回给模型。认证、网络等请求级错误仍应抛出循环之外，让外围应用处理。

## 第 4 步：把调用包进带上限的循环

第 2、3 步各处理一轮模型交互。加一个 `runAgent()` 把它们连起来：

```
async function runAgent(task: string, maxIterations = 10) {
  if (!Number.isSafeInteger(maxIterations) || maxIterations < 1) {
    throw new Error("maxIterations must be a positive safe integer");
  }

  const messages: ChatMessages[] = [{ role: "user", content: task }];
  const callCounts = new Map<string, number>();

  for (let iteration = 1; ; iteration++) {
    const startedAt = performance.now();
    const { result, message, calls } = await sendTurn(
      messages,
      iteration === 1 ? "required" : "auto",
    );

    console.info({
      iteration,
      model: result.model,
      tools: calls.map((call) => call.function.name),
      latencyMs: Math.round(performance.now() - startedAt),
    });

    if (calls.length === 0) {
      return typeof message.content === "string" ? message.content : null;
    }

    if (iteration === maxIterations) {
      throw new Error(`Stopped after ${maxIterations} iterations`);
    }

    for (const call of calls) {
      const fingerprint = `${call.function.name}:${call.function.arguments}`;
      const count = (callCounts.get(fingerprint) ?? 0) + 1;

      callCounts.set(fingerprint, count);

      if (count >= 3) {
        throw new Error(
          `Stopped after three identical calls to ${call.function.name}`,
        );
      }
    }

    messages.push(message);
    messages.push(...(await Promise.all(calls.map(executeToolCall))));
  }
}
```

每一趟先调模型、判断是否已经完成，然后追加 assistant 消息和工具结果。下一趟把扩充后的历史经由 `sendTurn()` 再发一遍。assistant 消息要在工具结果之前压入，完整轮次才得以保留。

迭代上限的检查发生在模型响应之后、任何工具执行之前。工具结果只有在下一次模型请求时才有用，所以当模型在最后一个被允许的迭代上仍然请求工具时，循环直接停止、不执行它们——那种执行只会留下模型永远看不到也报不出的副作用。

这个上限是循环里唯一的硬限制，检查用的是 `iteration` 与 `maxIterations` 相等。`runAgent()` 在首个请求之前就拒绝任何不是正安全整数的上限，因为 `0`、`1.5`、`NaN` 之类的值永远无法命中，循环会跑到模型自己停止请求工具为止。`Number.isSafeInteger()` 还会拒绝大于 `Number.MAX_SAFE_INTEGER` 的值——在那里 `iteration++` 不再产生不同的值，上限永远达不到。

指纹计数器在同一个工具名加参数串出现三次后终止运行。设成二会拦掉"空结果或瞬时失败后重试一次"的模型；设成三放行那次重试，同时仍能很快拦卡死的模型。这个阈值和 `maxIterations` 默认值都是应用的选择，不是 OpenRouter 的默认。

生产应用里，比较之前先规范化解析后的参数，让换了格式但内容相同的调用仍被算作重复。你也可以给每个工具设不同的限制。

## 测试循环

用一个小 `main()` 收尾 `agent.ts`：

```
async function main() {
  const answer = await runAgent(
    "Compare the weather in Lagos and London. Which city is warmer?",
  );

  console.log(answer);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```

在终端运行：

```
npx tsx agent.ts
```

你会看到一次或多次调用 `get_weather` 的迭代，然后是一份最终对比。数值来自第 1 步的本地 map，所以可以在接真实服务之前把整个循环测通。这是一次真实 API 运行的输出：

```
{
  iteration: 1,
  model: 'google/gemini-3-flash-preview',
  tools: [ 'get_weather', 'get_weather' ],
  latencyMs: 3930
}
{
  iteration: 2,
  model: 'google/gemini-3-flash-preview',
  tools: [],
  latencyMs: 1417
}
Lagos is currently warmer than London.
```

第一轮在一个响应里返回了两个 `get_weather` 调用，循环并行执行了它们。第二轮没有工具调用，循环于是返回文本。你的运行可能在迭代数、措辞和延迟上不同。

## 加上回退与并发控制

这里的每个控制各管一种失败模式。迭代上限和重复计数管你应用内的无效行为；并发的选择管并行工具互相写坏；模型回退管所选模型的报错；Auto Exacto 管工具调用请求上的提供商排序。

从循环里已有的停止条件开始：模型不发工具调用就返回，同一调用出现三次就失败，在迭代 `maxIterations` 上模型还在请求工具就失败。即使日后加时间、token 或按工具的限制，也要保留这个硬上限。

下一个选择是并发。示例用 `Promise.all()` 跑工具调用，因为两个查询互相独立。除非确认工具之间不共享状态，否则请按顺序跑：对同一条记录"先写后读"绝不能并行。

再下一层是模型回退。[`models` 参数](https://openrouter.ai/docs/guides/routing/model-fallbacks)接收有序列表。第一个模型是首选；第一个返回错误——包括限流、提供商宕机和内容审核拒绝——就依次试列表里的下一个。你的循环读 `result.model` 看是哪个模型答的。

[Auto Exacto](https://openrouter.ai/docs/guides/routing/auto-exacto) 默认在每个包含 `tools` 的请求上运行。对有多家提供商的模型，我们按吞吐、工具调用成功率和基准测试成绩来重排提供商，而不是按价格。你的循环不用为此改任何代码。只有一家提供商的模型没有可重排的东西——请查看模型页面的提供商列表，确认重排是否适用于你选的模型。如果你的循环每轮都发送大体量工具定义、且提示词缓存命中率比提供商质量更要紧，可以通过设 `provider.sort` 为 `"price"` 或使用 `:floor` 模型变体来退出。

## 限制历史增长，并给每次迭代留日志

每次迭代都追加一条 assistant 消息和每个工具调用一条结果。这些消息会在后续请求里再发一遍，大的工具结果能让历史迅速膨胀。

工具返回大响应而模型只需要几个字段时，先挑选字段再追加结果。也可以截断内容，或把完整载荷存到别处、返回一个引用。截断后的结果要保持合法：比如返回一个带预览、原始大小和 truncated 标记的 JSON 对象，而不是从中间劈开一个 JSON 字符串。

循环已经记录了迭代序号、实际服务的模型、工具名和延迟。在应用里，再加上参数的安全哈希和停止原因。别记录密钥或原始敏感参数。一段简短、格式一致的轨迹，能告诉你一次运行是从哪里开始重复、在哪里撞上上限的。

## 在循环里使用 MCP 工具

MCP server（Model Context Protocol，模型上下文协议服务器）把另一个服务或进程里的工具暴露出来。你的循环照旧向模型发送工具定义、接收调用、执行、追加结果——不同之处是工具发现和执行由一个 MCP 客户端接管，而不是你的本地函数表。

工具是你自己的少数几个函数、想要最小实现时，用本地 handler。工具已经存在于远端服务器之后——GitHub、Linear 或内部服务——时，用 MCP。

边界一条没变：每个工具调用 ID 返回一条结果、后续请求保持工具可用、检测重复、强制执行上限。MCP 改变的只是工具在哪里运行，不是这些控制是否可以不做。

## 什么时候迁到 Agent SDK

当你想让库来管多轮循环、工具执行、对话状态和停止条件时，迁到我们的 [Agent SDK](https://openrouter.ai/docs/agent-sdk/overview)。它还支持 MCP 工具、流式、[工具审批与状态持久化](https://openrouter.ai/docs/agent-sdk/call-model/tool-approval-state)，以及对重复工具调用的[死循环检测](https://openrouter.ai/docs/agent-sdk/call-model/doom-loop-detection)（默认关闭）。

如果你的工具已经在远端 MCP server 后面，[`@openrouter/mcp`](https://openrouter.ai/docs/agent-sdk/call-model/mcp-tools) 能发现它们，并和你在本地工具一起暴露给 Agent SDK 的 `callModel` 函数。

想直接掌控消息、工具分发和停止条件时，自己搭循环依然有价值。它也给你一个具体的途径，理解 agent 框架替你管理了什么。

当你的应用需要持久工作流或对话之外的持久状态时，更大的编排系统才说得通。

## 下一步

模型请求、有序模型回退和提供商路由归我们。工具执行和围着它的限制归你的应用。

完整的请求与响应形态见[工具调用指南](https://openrouter.ai/docs/guides/features/tool-calling)。本指南用到的 SDK 请求字段见 [TypeScript SDK 概览](https://openrouter.ai/docs/client-sdks/typescript/overview)。想用第二个模型给循环的产出打分，读 [LLM 裁判：自动为 AI 智能体的输出打分](https://openrouter.ai/blog/tutorials/llm-as-a-judge-evaluate-ai-agents/)。想在分发器执行前逐条对照用户请求检查工具调用，看 [Gate Agent Tool Calls with Jev](https://openrouter.ai/docs/cookbook/building-agents/gate-tool-calls-with-jev)。

## 常见问题

### 怎么决定 agent 循环何时停止？

模型不再返回工具调用时、重复了不允许的调用时、到达固定迭代上限时，循环就该停。生产循环还可以加耗时、token 或成本的限制。它们至少应当永远有一条硬边界，并记录是哪条边界终结了这次运行。

### 工具调用失败时应该发生什么？

把失败作为对应的那条工具结果返回，让模型能对它做出反应。用 TypeScript SDK 时，结果应为 `role: "tool"`、带上原 `toolCallId`、内容是清晰的错误信息。参数解析和工具执行的错误要在循环内部捕获，别让一个失败的工具终结整个进程。

### 怎么阻止 agent 重复同一个动作？

用工具名加参数生成指纹，统计它在整次运行中出现的次数，越过你的阈值就停止或按工具施加重试限制。生产环境在比较之前先规范化解析后的参数，让等价的 JSON 对象产生同一个指纹。只有当循环另有变化条件且有硬上限时，才为轮询类工具放行有意的重复。

### 搭一个工具调用 agent 需要 LangChain 或其他 AI agent 框架吗？

不需要。一个小 agent 靠消息、工具定义、本地 handler 和一个有界循环就能跑。当你需要框架来管理执行状态、审批、持久运行或更大的工具生态时，再上 AI agent 框架。
