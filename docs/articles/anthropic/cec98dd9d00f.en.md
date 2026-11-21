---
vendor: anthropic
title: You can now let a Claude Managed Agents agent use dynamic workflows, in beta with the managed-agents-2026-04-01 beta header.
original_title: 
url: https://platform.claude.com/docs/en/release-notes/overview
date: 2026-10-09
lang: en
captured: 2026-11-22
extractor: rss-entry
status: ok
body_sha: 39907ef05055
---

- You can now let a Claude Managed Agents agent use [dynamic workflows](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration#dynamic-workflows), in beta with the `managed-agents-2026-04-01` beta header. For work with many pieces, such as reviewing hundreds of documents, the agent can write a workflow. A workflow is a program that runs many agents in phases and combines their results. The server runs it in the background as a workflow run. To [turn dynamic workflows on](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration#turn-on-dynamic-workflows), set the agent’s `multiagent` field to `{"type": "multiagent_20261001", "workflows": {"type": "enabled"}}`. To guide the agent, tell it in its system prompt when to start a run. Follow each run through `workflow_run.*` events on the session’s event stream. See [Workflow runs](https://platform.claude.com/docs/en/managed-agents/workflow-runs).
