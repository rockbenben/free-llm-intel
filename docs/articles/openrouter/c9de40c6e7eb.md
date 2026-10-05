---
vendor: openrouter
title: 使用 Agent SDK 构建您自己的 Harness
original_title: Build Your Own Harness with the Agent SDK
url: https://openrouter.ai/blog/tutorials/create-agent-harness-with-agent-sdk
date: 2026-04-24
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 1899a53e6477
translator: agent
---

# 使用 Agent SDK 构建您自己的 Harness

Brian Thomas ·4/24/2026 · 更新于 6/24/2026

我们为"构建你自己的 agent harness"做了两个 [skill](https://github.com/OpenRouterTeam/skills)。第一个 [`create-agent-tui`](https://github.com/OpenRouterTeam/skills/tree/main/skills/create-agent-tui) 脚手架出一个完整的终端 UI，外观可定制——banner、工具展示样式、输入框，可以配成 Codex 风格或 Claude Code 风格。第二个 [`create-headless-agent`](https://github.com/OpenRouterTeam/skills/tree/main/skills/create-headless-agent) 脚手架出一个无头 agent，用于 CLI 工具、API 服务器、队列 worker 和流水线——没有终端 UI，只有结构化输入输出。

把 Claude Code、Codex、Cursor 或任何兼容 skill 的 agent 指向其中一个，描述你要什么，它就生成一个完整可跑的 TypeScript 项目。两者都跑在[刚发布不久的 Agent SDK](https://openrouter.ai/announcements/agent-sdk-with-callmodel)上，兼容 OpenRouter 上的任何模型。

市面上成熟商业 harness 一大把，为什么还要自己搭？

- 你要对观感、工具或循环有精细控制
- 你要一个能作为产品一部分发布的极简 harness
- 你想搞懂 agent 怎么工作，从而更会用、更会调

![Agent TUI 输入样式](https://openrouter.ai/blog/images/agent-tui-input-style.png)

## 现在就试着自己搭一个

- 还没有的话，[拿一个 OpenRouter API key](https://openrouter.ai/settings/keys)
- 在你的编码 agent 里安装你要的 skill：**Agent TUI**：`gh skill install OpenRouterTeam/skills create-agent-tui`；**Headless agent**：`gh skill install OpenRouterTeam/skills create-headless-agent`
- 告诉你的 agent 给你搭一个编码助手，以及什么能让你的助手与众不同
- 运行生成的项目：**Agent TUI**：`bun install && bun run start`；**Headless agent**：`bun install && bun run src/cli.ts -m '~anthropic/claude-opus-latest' -p "What's in this repo?"`

Skill 被调用时会呈现一份交互清单。你挑需要的东西：服务器工具（网页搜索、日期时间、图像生成）、本地工具（文件读/写/编辑、grep、glob、shell 等）、harness 模块（会话持久化、上下文压缩、工具审批闸门）、斜杠命令（`/model` 随时换模型、`/new` 开新会话、`/export` 存成 Markdown）。选完之后，它生成整个项目并用 `tsc` 校验类型。

终端 UI 的每一部分开箱即可定制。三种工具展示样式（emoji 标记、分组动作文案、极简单行），三种输入样式（跟随终端主题的全宽块、带边框的行、朴素 readline），三种加载动画（渐变微光、spinner、尾点），外加自定义 ASCII banner。你也可以直接描述你要什么，skill 会生成一个定制样式。

生成的项目归你改。加领域专属工具、换一个入口点（skill 内置 HTTP API 服务器模板）、为长对话接上上下文压缩，或把它删到只剩骨架。

## 两个 skill 都依赖 Agent SDK 提供可靠的内循环

两个 skill 生成的代码分两层。**内层**是 [Agent SDK](https://openrouter.ai/docs/sdks/typescript/call-model/overview)：一次 `callModel` 调用处理整个 agentic 循环（模型调用、工具执行、多轮循环、停止条件、流式、成本追踪）。**外层**是 skill 在它周围生成的一切：配置、工具定义、会话管理、入口点——TUI skill 还包括终端界面。

这是生成的 `src/agent.ts`，只留主干：

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

这一次 `callModel` 调用就是整个 agent 循环。SDK 调用模型、在输出里检查工具请求、按你的 Zod schema 校验参数、执行工具、把结果喂回去、重复，直到某个停止条件触发。

Skill 在这个之上通过遍历 `result.getItemsStream()` 接好流式。每个 item 都有类型，携带完整的当前状态：`message` item 带至今的全部 assistant 文本，`function_call` item 带工具调用，`function_call_output` item 带结果，`reasoning` item 带模型思考。生成的 `src/renderer.ts` 把它们渲染成带 token 计数和工具调用摘要的干净终端显示。

工具住在 `src/tools/`，每个工具一个文件。每个工具用 SDK 的 `tool()` 函数：Zod schema 定义输入，`execute` 函数带类型。服务器工具（网页搜索、日期时间）更简单：`serverTool({ type: 'openrouter:web_search' })`，由 OpenRouter 在服务端执行，客户端零代码。

配置流过三层：硬编码默认值、可选的 `agent.config.json` 文件、环境变量。偏好的模型和成本限制可以写进配置文件，并在每次会话覆盖：`AGENT_MODEL=openai/gpt-5 npm start`。

会话持久化把每条消息写进 JSONL 文件。下次运行时，harness 能重载对话历史，作为 `Item[]` 数组传回 `callModel`，接着上次的地方继续。

## 这些模式来自头部 harness

Skill 的取材是三套生产 agent 架构：

- **[pi-mono 的编码 agent](https://github.com/badlogic/pi-mono)**：三层分离（配置、agent 循环、工具）、JSONL 会话、可插拔的工具操作
- **Claude Code**：带只读与破坏性标记的工具元数据、由静态与动态上下文组成的系统提示词
- **[Codex CLI](https://github.com/openai/codex)**：分层配置（默认值、配置文件、环境变量）、带会话缓存的审批流程

这些模式烙进了生成的代码里，而让整体保持紧凑的是 Agent SDK。没有 `callModel` 处理 agentic 循环、工具校验、流式和成本追踪，你得自己写几百行循环管理代码。Skill 全部精力都放在应用特定的部分，因为其余都归 SDK。

Headless skill 架构相同，只是整个剥掉 TUI 层。生成的 CLI 不通过 REPL，而是经 `--prompt`、位置参数或管道 stdin 接收提示词，输出纯文本、NDJSON 事件流，或只给一个退出码。

生产使用上有两个特性突出。**429/5xx 的安全重试**：生成的 `runAgentWithRetry` 包装器对瞬态 API 错误做指数退避重试——但仅在一次工具调用都没执行过时。`file_write` 或 `shell` 这类会改变状态的工具一旦跑过，从初始提示词重放 agent 会二次执行副作用，重试因此立即抛出。**`--output-schema` 结构化输出**：传入一个 JSON Schema 文件，CLI 会用 Ajv 把 agent 的最终响应对照校验，校验失败以退出码 2 结束。解析器能容忍 markdown 围栏，模型把 JSON 包在代码块里也能工作。

完整的 `callModel` API 参考在 [SDK 文档](https://openrouter.ai/docs/sdks/typescript/call-model/overview)。详细走查见 [Build Your Own Agent TUI](https://openrouter.ai/docs/cookbook/building-agents/create-agent-harness-tui) 和 [Build Your Own Headless Agent](https://openrouter.ai/docs/cookbook/building-agents/create-headless-agent) 指南。想在 Agent SDK 之上做你自己的 skill，从 [skills 仓库](https://github.com/OpenRouterTeam/skills)开始。
