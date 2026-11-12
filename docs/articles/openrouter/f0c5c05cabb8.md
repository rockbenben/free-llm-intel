---
vendor: openrouter
title: How to Stop an AI Agent Stuck in an Infinite Loop
original_title: 
url: https://openrouter.ai/blog/tutorials/ai-agent-infinite-loop
date: 2026-11-12
lang: zh
captured: 2026-11-12
extractor: readability-v1
translator: agent
status: translated
body_sha: 2f66cc9cbd85
---

# 如何阻止 AI agent 陷入无限循环

OpenRouter ·11/12/2026

![如何阻止 AI agent 陷入无限循环](https://openrouter.ai/blog/images/ai-agent-infinite-loop.png)![如何阻止 AI agent 陷入无限循环](https://openrouter.ai/blog/images/ai-agent-infinite-loop-dark.png)

当模型不断调用一个失败的工具（通常还带着同样的参数），而 agent 循环里没有任何东西叫它停下，AI agent 就卡进了无限循环。每次重试都会把整段对话重发一遍，于是每一轮都比上一轮更贵，一个放任跑上一整夜的循环能烧掉几千美元。

本指南用四道闸拦住循环，我们在六个当下主流模型上做过测试。其中三道跑在你的 agent 内部，通过 [OpenRouter Agent SDK](https://openrouter.ai/blog/tutorials/agent-sdk-with-callmodel/)（@openrouter/agent 0.11.0）实现：doom-loop 检测、判定「哪些调用算重复」的规则，以及对步数和成本的封顶。第四道是给 API key 设额度上限，由我们在服务端强制执行，因此即便你的 agent 代码有 bug 也照样兜得住。

## TL;DR

- 开启 doom-loop 检测后，我们测试的六个模型全都在第三次相同的工具调用时被拦下。不开检测时，18 次运行里有 4 次一直重试到 40 步上限才停。开了之后，18 次里有 16 次在两次真实工具调用后就结束了。
- callModel 里的 `doomLoop: true` 会拦下第三次相同调用，并在第六次时结束本次运行。
- 有些模型靠把参数稍作改动绕开检测。一个能对参数做归一化的 `loopKey` 就能拦住它们。
- `stopWhen: [stepCountIs(n), maxCost(x)]` 给每次运行都封顶，不管循环因何而起。
- API key 上的额度上限封住你的总支出。装不下的请求会以 402 失败，并带 `limit_source: “openrouter_key_limit”`。

## AI agent 为什么会卡进无限循环？

agent 循环在模型不再请求工具、直接作答时结束。一个持续失败的工具，让模型没有理由这么做。错误被塞回对话，指令仍写着「完成任务」，于是再试一次看起来就是正确的下一步。除非你加上计数的代码，循环里没有任何东西在数尝试次数。

循环越跑也越贵，因为每一轮都会重发整段对话，连之前每次失败都带上。在我们逐轮记录的一次运行里，输入从 131 token 涨到 3,262，单轮成本几乎翻了两番。若用更贵的模型、又有多个会话同时跑，这种增长就是「一晚上烧掉几千美元」的来由。

为了亲眼看到它发生，我们搭了一个 billing agent，它唯一的工具会以「计费服务宕机」的方式失败。要跑它，把代码存成 agent.ts，执行 `bun add @openrouter/agent zod`，设置 `OPENROUTER_API_KEY`，再运行 `bun agent.ts`：

```
import { OpenRouter, tool, stepCountIs } from '@openrouter/agent';
import { z } from 'zod';

const openrouter = new OpenRouter({ apiKey: process.env.OPENROUTER_API_KEY });

let attempts = 0;

const fetchInvoice = tool({
  name: 'fetch_invoice',
  description: 'Fetch an invoice from the billing service by ID.',
  inputSchema: z.object({ invoice_id: z.string() }),
  execute: async ({ invoice_id }) => {
    attempts++;
    console.log(`  fetch_invoice("${invoice_id}")`);
    throw new Error(`billing-service timeout after 30s fetching ${invoice_id}`);
  },
});

let cost = 0;

const result = openrouter.callModel({
  model: 'mistralai/mistral-large-4-0',
  instructions:
    'You are a billing agent. Complete the task. If a tool call fails, retry it. ' +
    'Do not stop until you have the invoice total.',
  input: 'Get the total of invoice INV-2291.',
  tools: [fetchInvoice] as const,
  stopWhen: stepCountIs(40), // so the demo ends
  hooks: {
    PostModelCall: [{ handler: ({ usage }) => { cost += usage?.cost ?? 0; } }],
    DoomLoopDetected: [{ handler: ({ action, streak }) =>
      console.log(`DoomLoopDetected: ${action} (streak ${streak})`) }],
    SessionEnd: [{ handler: ({ reason }) => console.log(`SessionEnd: ${reason}`) }],
  },
});

const text = await result.getText();
const verdict = await result.getDoomLoopVerdict(); // set only when detection stopped the run

console.log(`attempts: ${attempts}, cost: $${cost.toFixed(4)}`);
console.log(verdict ? `stopped: ${verdict.message}` : text.slice(0, 160));
```

```
  fetch_invoice("INV-2291")
  fetch_invoice("INV-2291")
  fetch_invoice("INV-2291")
  ...
SessionEnd: max_turns
attempts: 41, cost: $0.0309
I was unable to retrieve the total for invoice INV-2291. The billing service
consistently timed out after 30 seconds on all 41 attempts to fetch this invoice, r
```

41 次调用一模一样，运行之所以停下，仅仅是因为 `stepCountIs(40)`。多出来的那次，是上限触发时模型已经请求、SDK 仍照跑的一次（第 3 步会讲）。没有 `stopWhen`，Agent SDK 会一直循环到模型不再请求工具为止，所以这次运行本不会自己停。最终回答里说服务在超时——可见模型每一轮都知道这一点，却仍然重试。

![折线图：未加防护的 Mistral Large 4 运行的累计成本，从第 1 轮接近 $0 一路涨到第 41 轮后的 $0.0309。](https://openrouter.ai/blog/images/ai-agent-infinite-loop-1.png)

我们在六个模型上各跑三次同样的 agent，分别开、关检测：

| **模型** | **每次运行工具调用数，无防护** | **撞到 40 步上限** | **每次运行工具调用数，doomLoop: true** |
| --- | --- | --- | --- |
| anthropic/claude-haiku-5.5 | 6, 6, 6 | 0 of 3 | 2, 2, 2 |
| deepseek/deepseek-v4.1-flash | 6, 5, 7 | 0 of 3 | 2, 2, 2 |
| google/gemini-3.8-flash | 5, 6, 5 | 0 of 3 | 2, 2, 2 |
| mistralai/mistral-large-4-0 | 11, 41, 41 | 2 of 3 | 2, 12, 2 |
| openai/gpt-6-luna | 17, 37, 21 | 0 of 3 | 2, 2, 20 |
| x-ai/grok-4.7 | 41, 12, 41 | 2 of 3 | 2, 2, 2 |

循环还会一次一个样。Grok 4.7 在同一输入上分别调了 41、12、41 次，所以一次干净利落的测试并不能证明你的 agent 不会循环。全部 18 次运行加起来，检测把工具调用从 314 次砍到 64 次，花费从 $0.29 降到 $0.05。

## 第 1 步：打开 doom-loop 检测

给 callModel 调用加一个选项：

```
  doomLoop: true,
```

```
  fetch_invoice("INV-2291")
DoomLoopDetected: observe (streak 2)
  fetch_invoice("INV-2291")
DoomLoopDetected: block (streak 3)
DoomLoopDetected: block (streak 4)
DoomLoopDetected: block (streak 5)
DoomLoopDetected: stop (streak 6)
SessionEnd: doom_loop
attempts: 2, cost: $0.0034
stopped: Doom loop suspected: tool "fetch_invoice" was invoked in 6 consecutive rounds
with identical arguments (fingerprint 64be4614c5ea3e26…). Repeating the call will not
change the result. Take a different approach, or explain why repetition is required.
```

[Doom-loop detection](https://openrouter.ai/docs/agent-sdk/call-model/doom-loop-detection) 按工具名和参数给每次工具调用算指纹。它先把参数规范化，因此 JSON 键换个顺序也藏不住重复。只有当模型看过上一次结果、又再次请求时，才算一次重复——所以同一轮里五次相同的调用只算一次。随着连续次数增长，它沿默认阶梯往上爬：第 2 次 observe、第 3 次 block、第 6 次 stop。

某次调用被 block 时，SDK 跳过 `execute`，返回一个工具错误，告诉模型它在重复自己。和超时不同，这个错误明说再试也没用。多数运行里，模型读到它就直接写了最终回答，以 `SessionEnd: complete` 结束。上面那次它还在继续请求，于是 stop 以 `reason: doom_loop` 结束了运行。`getDoomLoopVerdict()` 仅在检测结束运行时才返回消息，这正好是值得告警的信号。

想更早停，就调低阈值。用 `doomLoop: { ladder: { observe: 2, block: 3, stop: 4 } }` 时，一次 GPT-6 Luna 运行在连续第 4 次就停了，只花 $0.0002。阶梯还有默认关闭的两级：`steer` 给模型发一条「你在重复自己」的提示，`escalate` 让下一轮跑在你指定的更强模型上。

## 第 2 步：告诉检测器什么算「同一次调用」

默认只有参数完全一致，两次调用才算相同。被 block 之后，有些模型会把参数稍作改动，于是这次调用有了新指纹，连续计数重新从零开始：

```
 fetch_invoice("INV-2291")
DoomLoopDetected: observe (streak 2)
  fetch_invoice("INV-2291")
DoomLoopDetected: block (streak 3)
  fetch_invoice("2291")
  fetch_invoice("inv-2291")
  fetch_invoice("INV-2291")
DoomLoopDetected: observe (streak 2)
  fetch_invoice("INV-2291")
  fetch_invoice("INV2291")
  ...
SessionEnd: complete
attempts: 13, cost: $0.0125
```

在另外九次开了检测的 Mistral Large 4 运行里，模型有五次这么干，其中三次撞到 40 步上限，多半是在 `INV-2291` 和 `inv-2291` 之间来回换。GPT-6 Luna 则用尾部空格和换行做同样的事。模型其实在照 block 消息做——那条消息让它们换个思路。可只有一个工具时，它们能换的「另一种做法」就只剩换个输入。

工具上的 `loopKey` 告诉检测器：输入的哪一部分标识了这次调用。对发票 ID 来说，就是那串数字：

```
 loopKey: ({ invoice_id }) => invoice_id.replace(/\D/g, ''), // "inv-2291 " and "INV-2291" are one call
```

```
 fetch_invoice("INV-2291")
DoomLoopDetected: observe (streak 2)
  fetch_invoice("INV-2291")
DoomLoopDetected: block (streak 3)
DoomLoopDetected: block (streak 4)
DoomLoopDetected: block (streak 5)
SessionEnd: complete
attempts: 2, cost: $0.0039
```

现在每种变体都映射到 2291，连续次数持续增长，重复也就一直被拦。六次里有五次在两次真实调用后就停了。第六次里，模型试了另一张发票 `INV-0000`，连续计数被正确地重置了。

把大小写、空格、前缀，以及一切「不改变工具所取记录」的差异都归一化。要完全忽略某个字段（比如模型每次重试都调大的 timeout），就只列出要紧的字段：`loopKey: [‘invoice_id’]`。而本职就是重复的工具，比如轮询任务状态的那个，用 `loopKey: false`。

## 第 3 步：给每次运行的步数和成本封顶

检测只抓重复。每轮都换花样的模型永远不会重复指纹；被 block 后还继续请求的模型，也要等 stop 触发才停。[Stop conditions](https://openrouter.ai/docs/agent-sdk/call-model/stop-conditions) 则不管运行为何拖长，都会把它结束。把 `maxCost` 和 `stepCountIs` 一起 import，替换 `stopWhen`，再加两个 [lifecycle hooks](https://openrouter.ai/docs/agent-sdk/call-model/lifecycle-hooks)：

```
let failuresInARow = 0; // tool errors in a row, whatever the arguments

  stopWhen: [stepCountIs(15), maxCost(0.01), () => failuresInARow >= 5],
  hooks: {
    // ...the hooks from before, plus:
    PostToolUse: [{ handler: () => { failuresInARow = 0; } }],
    PostToolUseFailure: [{ handler: () => { failuresInARow++; } }],
  },
```

`stopWhen` 每轮之后都会检查，任一条件为真即停止运行。`maxCost` 累加我们随每次响应返回的 `usage.cost`，算的正是你被计费的金额。失败计数器不看参数，因此即便没有 `loopKey`，它也能抓住第 2 步里改过参数的调用。在一次同样改参数的 Mistral Large 4 运行里，它在六次调用后结束了会话，花费 $0.0062，`SessionEnd: max_turns`。

每个 `stopWhen` 条件都以 `reason: max_turns` 结束会话，所以若需要区分是哪道封顶，就自己记一条原因。当封顶触发、而模型还有待处理的工具调用时，SDK 会先跑完它们，再在禁用工具调用的情况下多走一轮，好让运行以一段写好的回答收尾。这就是为什么这次在 5 次的上限下跑了 6 次调用，也是第一个 demo 在 40 的上限下跑了 41 次。设 `allowFinalResponse: false` 可跳过这一轮。

两道封顶都按你正常运行的水位来设。我们那几次在 Mistral Large 4 上用 4 到 6 轮、花 $0.0018 到 $0.0053，所以 15 步和 $0.01 既留了余量，又不至于放进一次 40 轮的运行。两者里成本上限更要紧，因为越到后面每轮越贵。

不用 Agent SDK 时，同样这几道闸也能塞进任意循环里：按工具名和归一化后的参数计数，第三次重复时不去执行、而是返回一条像「Blocked: tell the user what went wrong」的工具结果，并在步数或累加的 `usage.cost` 越过上限时停下。我们针对 chat completions API 写的 Python 版本，三次运行里都在四步之后、不到 $0.002 就拦住了 Mistral Large 4。

## 第 4 步：给 API key 设额度上限

前面每道闸都跑在 agent 自己的进程里。可一旦那段代码有 bug、上线时漏了封顶，或跑了一百个各自都压在 `maxCost` 之下的会话，就没有任何东西限制总额了。key 上的额度上限能限制，因为我们在请求到达供应商之前就于服务端做了检查。

在 dashboard 里、或用 create key API，设置 `limit`（以美元计）和 `limit_reset`（daily、weekly、monthly 或 null）。若 key 用了 BYOK，还要把 `include_byok_in_limit` 设为 true——它默认 false，否则 BYOK 的花费不计入上限。每日额度在 UTC 午夜重置，每周额度在周一重置。给每个 agent 或每个客户单独一把 key，这样一个循环最多只能花掉那把 key 的份额。若多个 agent 不得不共用一把 key，参见 [Capping Shared Agent Keys](https://openrouter.ai/docs/guides/best-practices/capping-shared-agent-keys)。

在路由请求之前，我们先按最坏情况给它估价，即输入加 `max_tokens`。若这装不进 key 剩下的额度，请求就失败，且不会向你收费。我们往一个还剩 $9.97 的 key 上、对一个贵模型发了一个 `max_tokens: 900000` 的 chat completions 请求，拿回的是：

```
402
{
  "error": {
    "message": "This request requires more credits, or fewer max_tokens. You requested up to 900000 tokens, but can only afford 664657. To increase, visit https://openrouter.ai/workspaces/<workspace-slug>/keys/<key-hash> and adjust the key's total limit",
    "code": 402,
    "metadata": {
      "limit_source": "openrouter_key_limit",
      "remedy_hint": "Raise or remove this API key's usage limit at https://openrouter.ai/settings/keys, or use a key without a limit.",
      "provider_name": null
    }
  },
  "user_id": "<org-id>"
}
```

我们把 workspace slug、key hash 和 organization ID 都替换掉了。

请按 `error.metadata.limit_source` 分支，别按消息文本或状态码。额度耗尽的 key 同样报 `openrouter_key_limit`，[limits docs](https://openrouter.ai/docs/api_reference/limits) 在 402 额度错误和 403 预算错误下都列了这个来源。若像上面例子那样，消息说这把 key 只能负担更少的 token，就调低 `max_tokens` 重试。若 key 已耗尽，在额度重置前重试都不可能成功，应当当作「停止」处理。Agent SDK 会把这个 402 抛成 `PaymentRequiredResponseError`。唯一值得重试的 402 是 `openrouter_in_flight_budget`，且要按它的 `Retry-After` 头来。限流返回的则是 429，见我们的 [LLM API rate limits guide](https://openrouter.ai/blog/tutorials/llm-api-rate-limits/)。

[Workspace budgets](https://openrouter.ai/docs/guides/features/workspaces/workspace-budgets) 把一个 workspace 里所有 key 的上限按每天、每周、每月或整个生命周期合并计算。被拦的请求拿到 403，消息形如 `Workspace monthly budget of $500.00 exceeded. Contact your org admin.`（我们没触发这一种，消息出自文档）。已在途的请求仍会跑完，因此花费可能略微超出，但一个跑通宵的循环会停在接近每日上限的地方。[spend controls guide](https://openrouter.ai/docs/guides/best-practices/spend-controls) 讲了 workspace budgets 与按成员护栏如何配合。

## 哪道闸拦哪种循环？

每道闸抓的是不同种类的循环。key 上限全都能抓，但要等 key 的额度花完才生效，所以最适合当最后一层。

| **循环** | **doomLoop** | **loopKey** | **stopWhen 封顶** | **Key 上限或 workspace budget** |
| --- | --- | --- | --- | --- |
| 同一调用、同一参数 | 拦住 | 不需要 | 到上限拦住 | 到额度拦住 |
| 同一调用、参数略有不同 | 漏掉 | 拦住 | 到上限拦住 | 到额度拦住 |
| 每轮换一种新做法 | 漏掉 | 漏掉 | 到上限拦住 | 到额度拦住 |
| 很多次运行，各自都低于上限 | 仅单次运行 | 仅单次运行 | 仅单次运行 | 拦住总额 |
| 上线时漏了防护 | 漏掉 | 漏掉 | 漏掉 | 到额度拦住 |

## 常见问题

### 出错后我的 agent 为什么还一直调同一个工具？

工具结果说调用失败，prompt 又说要完成任务，于是「再试一次」在模型看来就是正确的动作。返回能告诉模型下一步该怎么做的错误，比如「计费服务已宕机。告知用户并停止。」别跟模型说「一直重试到成功为止」。

### max iterations 上限能拦住失控的成本吗？

max iterations 上限能拦住单次运行无限跑下去，却封不住花费——因为越到后面每轮越贵，而且许多压在上限之下的运行加起来仍很可观。LangChain 的 `AgentExecutor` 里的 `max_iterations`、CrewAI 里的 `max_iter`，和 OpenRouter Agent SDK 的 `stepCountIs` 是同一类东西。请给它配上每次运行的成本上限，以及 API key 上的额度上限。

## 下一步

- [Doom-loop detection](https://openrouter.ai/docs/agent-sdk/call-model/doom-loop-detection)：阶梯、steering、escalation 与按工具覆盖。
- [Stop conditions](https://openrouter.ai/docs/agent-sdk/call-model/stop-conditions)：`stepCountIs`、`maxCost`、`maxTokensUsed` 与自定义条件。
- [Set up team AI spend controls](https://openrouter.ai/blog/tutorials/team-spend-controls-setup/)：dashboard 里的 workspace budgets 与护栏。
- [Agent SDK: Building Multi-turn Agent Workflows on OpenRouter](https://openrouter.ai/blog/tutorials/agent-sdk-with-callmodel/)：`callModel` 如何跑 agent 循环。
