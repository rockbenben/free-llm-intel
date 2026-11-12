---
vendor: openrouter
title: How to Stop an AI Agent Stuck in an Infinite Loop
original_title: 
url: https://openrouter.ai/blog/tutorials/ai-agent-infinite-loop
date: 2026-11-12
lang: en
captured: 2026-11-12
extractor: readability-v1
status: ok
body_sha: 6212345b57f0
---

# How to Stop an AI Agent Stuck in an Infinite Loop

OpenRouter ·11/12/2026

![How to Stop an AI Agent Stuck in an Infinite Loop](https://openrouter.ai/blog/images/ai-agent-infinite-loop.png)![How to Stop an AI Agent Stuck in an Infinite Loop](https://openrouter.ai/blog/images/ai-agent-infinite-loop-dark.png)

An AI agent gets stuck in an infinite loop when a model keeps calling a tool that fails, usually with the same arguments, because nothing in the agent loop tells it to stop. Each retry resends the whole conversation, so every turn costs more than the last, and a loop left running overnight can cost thousands of dollars.

This guide stops the loop with four guards, which we tested on six current models. Three run inside your agent through the [OpenRouter Agent SDK](https://openrouter.ai/blog/tutorials/agent-sdk-with-callmodel/) (@openrouter/agent 0.11.0): doom-loop detection, a rule for which calls count as repeats, and caps on steps and cost. The fourth is a credit limit on your API key. We enforce it on our side, so it holds even when your agent code has a bug.

## TL;DR

- With doom-loop detection on, all six models we tested were blocked on their third identical tool call. Without it, 4 of 18 runs retried until a 40-step cap. With it, 16 of 18 runs ended after two real tool calls.
- doomLoop: true in callModel blocks the third identical call and ends the run at the sixth.
- Some models get past detection by changing the argument slightly. A loopKey that normalizes the argument stops them.
- stopWhen: [stepCountIs(n), maxCost(x)] caps every run, whatever causes the loop.
- A credit limit on the key caps your total spend. A request that doesn’t fit fails with a 402 and limit_source: “openrouter_key_limit”.

## Why do AI agents get stuck in infinite loops?

An agent loop ends when the model answers without asking for a tool. A tool that keeps failing gives the model no reason to do that. The error goes back into the conversation, the instructions still say to finish the task, and another attempt looks like the right next step. Nothing in the loop counts attempts unless you add code that does.

The loop also gets more expensive as it goes, because every turn resends the whole conversation, including every earlier failure. In one run we logged turn by turn, input grew from 131 tokens to 3,262, and the cost per turn nearly quadrupled. With a pricier model and many sessions running at once, that growth is how one night adds up to thousands of dollars.

To watch it happen, we built a billing agent whose only tool fails the way a billing service that’s down would. To run it, save it as agent.ts, run bun add @openrouter/agent zod, set OPENROUTER_API_KEY, and run bun agent.ts:

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

All 41 calls were identical, and the run ended only because of stepCountIs(40). The extra call is one the model had already asked for when the cap fired, which the SDK still runs (Step 3 covers this). Without a stopWhen, the Agent SDK keeps looping until the model stops asking for tools, so this run wouldn’t have stopped on its own. The final answer says the service was timing out, so the model knew that on every turn and retried anyway.

![Line chart of the cumulative cost of the unguarded Mistral Large 4 run, rising from near $0 at turn 1 to $0.0309 after 41 turns.](https://openrouter.ai/blog/images/ai-agent-infinite-loop-1.png)

We ran the same agent three times on each of six models, with and without detection:

| **Model** | **Tool calls per run, no guard** | **Hit the 40-step cap** | **Tool calls per run, doomLoop: true** |
| --- | --- | --- | --- |
| anthropic/claude-haiku-5.5 | 6, 6, 6 | 0 of 3 | 2, 2, 2 |
| deepseek/deepseek-v4.1-flash | 6, 5, 7 | 0 of 3 | 2, 2, 2 |
| google/gemini-3.8-flash | 5, 6, 5 | 0 of 3 | 2, 2, 2 |
| mistralai/mistral-large-4-0 | 11, 41, 41 | 2 of 3 | 2, 12, 2 |
| openai/gpt-6-luna | 17, 37, 21 | 0 of 3 | 2, 2, 20 |
| x-ai/grok-4.7 | 41, 12, 41 | 2 of 3 | 2, 2, 2 |

Looping also changes from run to run. Grok 4.7 made 41, 12 and 41 calls on the same input, so one clean test doesn’t prove your agent won’t loop. Across all 18 runs, detection cut tool calls from 314 to 64 and spend from $0.29 to $0.05.

## Step 1: Turn on doom-loop detection

Add one option to the callModel call:

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

[Doom-loop detection](https://openrouter.ai/docs/agent-sdk/call-model/doom-loop-detection) fingerprints each tool call by its name and arguments. It canonicalizes the arguments first, so reordered JSON keys don’t hide a repeat. A repeat only counts when the model has seen the previous result and asks again, so five identical calls in one turn count as one. As the streak grows, it climbs the default ladder: observe at 2, block at 3 and stop at 6.

When a call is blocked, the SDK skips execute and returns a tool error telling the model it’s repeating itself. Unlike the timeout, this error says another try won’t help. In most runs, the model read it and wrote a final answer straight away, ending with SessionEnd: complete. In the run above it kept asking, so stop ended the run with reason: doom_loop. getDoomLoopVerdict() returns a message only when detection ended the run, which makes it the signal to alert on.

To stop sooner, lower the thresholds. With doomLoop: { ladder: { observe: 2, block: 3, stop: 4 } }, a GPT-6 Luna run ended at streak 4 for $0.0002. The ladder also has two rungs that are off by default. steer sends the model a note that it’s repeating itself, and escalate runs the next turn on a stronger model you pick.

## Step 2: Tell the detector what counts as the same call

By default, two calls count as the same only when their arguments match exactly. After a block, some models changed the argument slightly, which gives the call a new fingerprint and starts a new streak:

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

In nine more Mistral Large 4 runs with detection on, the model did this five times, and three of those reached the 40-step cap, mostly by alternating INV-2291 and inv-2291. GPT-6 Luna did the same with trailing spaces and newlines. The models are following the block message, which tells them to take a different approach. With only one tool, the only other approach they have is a different input.

A loopKey on the tool tells the detector which part of the input identifies the call. For an invoice ID, that’s the digits:

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

Every variant now maps to 2291, so the streak keeps growing and the repeats stay blocked. Five of six runs stopped after two real calls. In the sixth, the model tried a different invoice, INV-0000, which correctly reset the streak.

Normalize case, spacing, prefixes and anything else that doesn’t change which record the tool fetches. To ignore a field entirely, like a timeout the model raises on each retry, list only the fields that matter: loopKey: [‘invoice_id’]. A tool whose job is to repeat, like one that polls a job’s status, takes loopKey: false.

## Step 3: Cap steps and cost for every run

Detection only catches repeats. A model that tries something new every turn never repeats a fingerprint, and a model that keeps asking after a block isn’t stopped until stop fires. [Stop conditions](https://openrouter.ai/docs/agent-sdk/call-model/stop-conditions) end the run no matter why it ran long. Import maxCost alongside stepCountIs, replace stopWhen and add two [lifecycle hooks](https://openrouter.ai/docs/agent-sdk/call-model/lifecycle-hooks):

```
let failuresInARow = 0; // tool errors in a row, whatever the arguments

  stopWhen: [stepCountIs(15), maxCost(0.01), () => failuresInARow >= 5],
  hooks: {
    // ...the hooks from before, plus:
    PostToolUse: [{ handler: () => { failuresInARow = 0; } }],
    PostToolUseFailure: [{ handler: () => { failuresInARow++; } }],
  },
```

stopWhen is checked after every round, and the run stops when any condition is true. maxCost sums the usage.cost we return with each response, so it counts what you’re billed. The failure counter ignores arguments, so it catches the changed arguments from Step 2 even without a loopKey. On a Mistral Large 4 run that changed its arguments the same way, it ended the session after six calls for $0.0062, with SessionEnd: max_turns.

Every stopWhen condition ends the session with reason: max_turns, so log your own reason if you need to tell the caps apart. When a cap fires while the model still has tool calls pending, the SDK runs them and makes one last turn with tool calling disabled, so the run ends with a written answer. That’s why this run made six calls against a cap of five, and why the first demo made 41 against a cap of 40. Set allowFinalResponse: false to skip that turn.

Set both caps from your normal runs. Ours took four to six turns and cost $0.0018 to $0.0053 on Mistral Large 4, so 15 steps and $0.01 leave room without allowing a 40-turn run. Of the two, the cost cap matters more, since later turns cost more than early ones.

Without the Agent SDK, the same guards fit in any loop. Count calls per tool name and normalized arguments, return a tool result like “Blocked: tell the user what went wrong” instead of running the third repeat, and stop when steps or summed usage.cost pass your cap. Our Python version against the chat completions API stopped Mistral Large 4 after four steps, for under $0.002, in all three runs.

## Step 4: Put a credit limit on the API key

Every guard so far runs inside your agent’s process. If that code has a bug, ships without the caps, or runs a hundred sessions that each stay under maxCost, nothing limits the total. A credit limit on the key does, because we check it on our side before the request reaches a provider.

Set limit (in dollars) and limit_reset (daily, weekly, monthly or null) in the dashboard or with the create key API. If the key uses BYOK, also set include_byok_in_limit to true, because it defaults to false and BYOK spend doesn’t count toward the limit otherwise. Daily limits reset at midnight UTC, and weekly limits reset on Monday. Give each agent or customer its own key, so one loop can only spend that key’s share. If several agents have to share a key, follow [Capping Shared Agent Keys](https://openrouter.ai/docs/guides/best-practices/capping-shared-agent-keys).

Before we route a request, we price its worst case, which is the input plus max_tokens. If that doesn’t fit in what the key has left, the request fails, and you aren’t charged. We sent a chat completions request with max_tokens: 900000 to an expensive model on a key with $9.97 left, and got this back:

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

We replaced the workspace slug, key hash and organization ID.

Branch on error.metadata.limit_source, not on the message text or the status code. An exhausted key also reports openrouter_key_limit, and the [limits docs](https://openrouter.ai/docs/api_reference/limits) list that source under both 402 credit errors and 403 budget errors. If the message says the key can afford fewer tokens, as in the example above, retry with a lower max_tokens. If the key is exhausted, retrying can’t succeed until the limit resets, so treat it as a stop. The Agent SDK throws the 402 as PaymentRequiredResponseError. The one 402 worth retrying is openrouter_in_flight_budget, after its Retry-After header. Rate limits return 429 instead, which our [LLM API rate limits guide](https://openrouter.ai/blog/tutorials/llm-api-rate-limits/) covers.

[Workspace budgets](https://openrouter.ai/docs/guides/features/workspaces/workspace-budgets) pool the cap across every key in a workspace, per day, week, month or lifetime. Blocked requests get a 403 with a message like Workspace monthly budget of $500.00 exceeded. Contact your org admin. (We didn’t trigger this one, so the message comes from the docs.) Requests already in flight still finish, so spend can go slightly over, but a loop that runs all night stops close to the daily cap. The [spend controls guide](https://openrouter.ai/docs/guides/best-practices/spend-controls) shows how workspace budgets and per-member guardrails fit together.

## Which guard stops which loop?

Each guard catches a different kind of loop. The key limit catches all of them, but only once the key’s cap is spent, so it works best as the last layer.

| **Loop** | **doomLoop** | **loopKey** | **stopWhen caps** | **Key limit or workspace budget** |
| --- | --- | --- | --- | --- |
| Same call, same arguments | Stops it | Not needed | Stops it at the cap | Stops it at the limit |
| Same call, slightly different arguments | Misses it | Stops it | Stops it at the cap | Stops it at the limit |
| A new approach every turn | Misses it | Misses it | Stops it at the cap | Stops it at the limit |
| Many runs, each under its own cap | Per run only | Per run only | Per run only | Stops the total |
| A deploy with the guards missing | Misses it | Misses it | Misses it | Stops it at the limit |

## Frequently asked questions

### Why does my agent keep calling the same tool after an error?

The tool result says the call failed and the prompt says to finish the task, so another try looks like the right move to the model. Return errors that tell the model what to do next, like “The billing service is down. Tell the user and stop.” Don’t tell the model to retry until it succeeds.

### Does a max iterations limit stop runaway costs?

A max iterations limit stops a single run from going on forever, but it doesn’t cap what you spend, because later turns cost more and many runs under the limit still add up. Settings like max_iterations in LangChain’s AgentExecutor and max_iter in CrewAI do the same job as stepCountIs in the OpenRouter Agent SDK. Pair one with a cost cap per run and a credit limit on the API key.

## Next steps

- [Doom-loop detection](https://openrouter.ai/docs/agent-sdk/call-model/doom-loop-detection): the ladder, steering, escalation and per-tool overrides.
- [Stop conditions](https://openrouter.ai/docs/agent-sdk/call-model/stop-conditions): stepCountIs, maxCost, maxTokensUsed and custom conditions.
- [Set up team AI spend controls](https://openrouter.ai/blog/tutorials/team-spend-controls-setup/): workspace budgets and guardrails in the dashboard.
- [Agent SDK: Building Multi-turn Agent Workflows on OpenRouter](https://openrouter.ai/blog/tutorials/agent-sdk-with-callmodel/): how callModel runs the agent loop.
