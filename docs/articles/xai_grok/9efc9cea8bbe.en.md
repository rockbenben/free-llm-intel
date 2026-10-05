---
vendor: xai_grok
title: Grok Build is Now Open Source
original_title: Grok Build is Now Open Source
url: https://x.ai/news/grok-build-open-source
date: 2026-07-15
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 15987f659d69
---

Back to news

Jul 15, 2026

# Grok Build is Now Open Source

Explore the harness behind our coding agent and TUI.

View on GitHub

Try Grok Build

We're open-sourcing Grok Build, SpaceXAI's coding agent and TUI. The source is now available on [GitHub](https://github.com/xai-org/grok-build).

Publishing the code is the most direct way to build toward a robust and reliable harness. You can read the source to see exactly how it works, from context assembly to tool-call dispatch.

Open-sourcing also makes the harness easier to explore and extend: if you're working with skills, plugins, hooks, MCP servers, or subagents, the source is the definitive reference for how each is loaded and invoked.

Finally, Grok Build can now run fully local-first: compile it yourself, point it at your own local inference, and drive everything from your `config.toml`.

## [About the codebase](https://x.ai/news/grok-build-open-source#about-the-codebase)

The published source includes:

- The agent loop: how context is assembled, how model responses are parsed, and how tool calls are dispatched
- The tools: how the agent reads, edits, and searches code, and how it runs commands
- The terminal UI: rendering, input handling, plan review, and the inline diff viewer
- The extension system: skills, plugins, hooks, MCP servers, and subagents

Explore the source on [GitHub](https://github.com/xai-org/grok-build).

## Get started

View on GitHub

Get Grok Build
