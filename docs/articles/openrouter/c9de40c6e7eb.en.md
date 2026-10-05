---
vendor: openrouter
title: Build Your Own Harness with the Agent SDK
original_title: Build Your Own Harness with the Agent SDK
url: https://openrouter.ai/blog/tutorials/create-agent-harness-with-agent-sdk
date: 2026-04-24
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 1899a53e6477
---

# Build Your Own Harness with the Agent SDK

Brian Thomas ·4/24/2026 · Updated 6/24/2026

We built two [skills](https://github.com/OpenRouterTeam/skills) for building your own agent harness. The first, [`create-agent-tui`](https://github.com/OpenRouterTeam/skills/tree/main/skills/create-agent-tui), scaffolds a full terminal UI with customizable looks — banners, tool display styles, and input fields you can match to Codex’s style or Claude Code’s style. The second, [`create-headless-agent`](https://github.com/OpenRouterTeam/skills/tree/main/skills/create-headless-agent), scaffolds a headless agent for CLI tools, API servers, queue workers, and pipelines — no terminal UI, just structured input/output.

Point Claude Code, Codex, Cursor, or any skill-compatible agent at either skill, describe what you want, and it generates a complete, runnable TypeScript project. Both run on the [recently launched Agent SDK](https://openrouter.ai/announcements/agent-sdk-with-callmodel) and work with any model on OpenRouter.

Why do this when there are many great commercial harnesses out there?

- You want fine-grained control over the look, tools, or the loop
- You want a minimal harness you can ship as part of a product
- You want to learn how agents work to get better at using and debugging them

![Agent TUI input style](https://openrouter.ai/blog/images/agent-tui-input-style.png)

## Try building your own now

- [Get an OpenRouter API key](https://openrouter.ai/settings/keys) if you don’t have one
- Install the skill you want in your coding agent:  **Agent TUI**: `gh skill install OpenRouterTeam/skills create-agent-tui` **Headless agent**: `gh skill install OpenRouterTeam/skills create-headless-agent`
- Tell your agent to build you a coding assistant and what will make your assistant unique
- Run the generated project:  **Agent TUI**: `bun install && bun run start` **Headless agent**: `bun install && bun run src/cli.ts -m '~anthropic/claude-opus-latest' -p "What's in this repo?"`

The skill presents an interactive checklist when invoked. You pick what you need: server tools (web search, datetime, image generation), local tools (file read/write/edit, grep, glob, shell, and more), harness modules (session persistence, context compaction, tool approval gates), and slash commands (`/model` to switch models on the fly, `/new` for fresh conversations, `/export` to save as Markdown). After you make your selections, it generates the full project and verifies types with `tsc`.

Every part of the terminal UI is customizable out of the box. Three tool display styles (emoji markers, grouped action labels, or minimal one-liners), three input styles (full-width block that adapts to your terminal theme, bordered lines, or plain readline), three loader animations (gradient shimmer, spinner, or trailing dots), and custom ASCII banners. You can also describe what you want directly and the skill will generate a custom style.

The generated project is yours to modify. Add domain-specific tools, wire up a different entry point (the skill includes templates for HTTP API servers), bolt on context compaction for long conversations, or strip it down to the bare minimum.

## Both skills rely on the Agent SDK for a trustworthy inner loop

Both skills generate two layers of code. The **inner layer** is the [Agent SDK](https://openrouter.ai/docs/sdks/typescript/call-model/overview): one `callModel` call that handles the entire agentic loop (model calls, tool execution, multi-turn cycling, stop conditions, streaming, cost tracking). The **outer layer** is everything the skill generates around it: configuration, tool definitions, session management, the entry point, and — in the TUI skill’s case — the terminal interface.

Here’s the generated `src/agent.ts`, stripped to the essentials:

```
import { OpenRouter } from '@openrouter/agent';
import type { Item } from '@openrouter/agent';
import { stepCountIs, maxCost } from '@openrouter/agent';
import { tools } from './tools/index.js';

const client = new OpenRouter({ apiKey: config.apiKey });

const result = client.callModel({
  model: config.model,
  instructions: config.systemPrompt,
  input: userMessage,
  tools,
  stopWhen: [stepCountIs(config.maxSteps), maxCost(config.maxCost)],
});
```

That single `callModel` call is the entire agent loop. The SDK calls the model, inspects the output for tool requests, validates arguments against your Zod schemas, executes the tools, feeds results back, and repeats until a stop condition fires.

The skill wires up streaming on top of this by iterating over `result.getItemsStream()`. Each item is typed and carries the complete current state: `message` items carry the full assistant text so far, `function_call` items carry tool invocations, `function_call_output` items carry results, and `reasoning` items carry model thinking. The generated `src/renderer.ts` turns these into a clean terminal display with token counts and tool call summaries.

Tools live in `src/tools/`, one file per tool. Each tool uses the SDK’s `tool()` function with a Zod schema for input and a typed `execute` function. Server tools (web search, datetime) are even simpler: `serverTool({ type: 'openrouter:web_search' })` and OpenRouter executes them server-side with zero client code.

Configuration flows through three layers: hardcoded defaults, an optional `agent.config.json` file, and environment variables. You can set your preferred model and cost limits in a config file and override them per-session with `AGENT_MODEL=openai/gpt-5 npm start`.

Session persistence writes every message to a JSONL file. On the next run, the harness can reload conversation history and pass it back into `callModel` as an `Item[]` array, picking up where you left off.

## These patterns come from the top harnesses

The skill draws from three production agent architectures:

- **[pi-mono’s coding agent](https://github.com/badlogic/pi-mono)**: three-layer separation (config, agent loop, tools), JSONL sessions, pluggable tool operations
- **Claude Code**: tool metadata with read-only and destructive flags, system prompt composition from static and dynamic context
- **[Codex CLI](https://github.com/openai/codex)**: layered configuration (defaults, config file, environment variables), approval flows with session caching

These patterns are baked into the generated code, but the Agent SDK is what makes the whole thing compact. Without `callModel` handling the agentic loop, tool validation, streaming, and cost tracking, you’d be writing hundreds of lines of loop management code yourself. The skill focuses entirely on the app-specific parts because the SDK handles everything else.

The headless skill follows the same architecture but strips away the TUI layer entirely. Instead of a REPL, the generated CLI accepts prompts via `--prompt`, positional arguments, or piped stdin, and outputs plain text, NDJSON event streams, or just an exit code.

Two features stand out for production use. **Safe retry on 429/5xx**: the generated `runAgentWithRetry` wrapper retries transient API errors with exponential backoff — but only if no tool calls have executed yet. Once a mutating tool like `file_write` or `shell` has run, replaying the agent from the initial prompt would double-execute side effects, so retries throw immediately instead. **Structured output with `--output-schema`**: pass a JSON Schema file and the CLI validates the agent’s final response against it with Ajv, exiting with code 2 on validation failure. The parser is tolerant of markdown fences, so it works even when models wrap JSON in code blocks.

For the full `callModel` API reference, check the [SDK docs](https://openrouter.ai/docs/sdks/typescript/call-model/overview). For detailed walkthroughs, see the [Build Your Own Agent TUI](https://openrouter.ai/docs/cookbook/building-agents/create-agent-harness-tui) and [Build Your Own Headless Agent](https://openrouter.ai/docs/cookbook/building-agents/create-headless-agent) guides. To build your own skills on top of the Agent SDK, start with the [skills repo](https://github.com/OpenRouterTeam/skills).
