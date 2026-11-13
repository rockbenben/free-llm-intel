---
vendor: anthropic
title: Operate Claude Managed Agents inside your security perimeter | Claude by Anthropic
original_title: Operate Claude Managed Agents inside your security perimeter
url: https://claude.com/resources/articles/self-hosted-claude-managed-agents
date: 2026-11-12
lang: en
captured: 2026-11-13
extractor: readability-v1
status: ok
body_sha: 04a567c24d08
---

[Self-hosted Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/self-hosted) is now available in private beta. Developers can build agents that work directly in their company's code and internal systems, and run those agents in their own environment.

Self-hosting is a new way to run [Managed Agents](https://claude.com/platform/claude-managed-agents), a suite of composable APIs for building and deploying autonomous agents. Managed Agents provides the agent harness, sandboxes, credential handling, and session history to get long-running agents into production.

## Run your agent control plane in your own environment

We first launched Managed Agents as a hosted service on the Claude Platform, where Anthropic runs the infrastructure for you. For teams who needed their code to stay in their own environment, we added [self-hosted sandboxes](https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes).

Since then, agents have become more capable and are taking on more critical work, like fixing broken builds, testing releases, triaging alerts, and working through your bug backlog. They run unattended on your code and need access to your internal systems. For agents with that level of access, some teams want the whole service in their own environment, not just the sandbox. Until now, that meant building the platform themselves.

With self-hosted Managed Agents, every part of the service runs in your own cloud or on-premise, including the harness, sandboxes, credentials, and session history. You operate the Managed Agents server, its database, and the workers where agents run their shell and file tools. Model requests go where you choose, whether that's Anthropic directly, your cloud provider (Amazon Bedrock, Google's Agent Platform, or Microsoft Foundry), or your own gateway. Your developers still build agents with the same core APIs as the hosted Managed Agents service.

Session history is stored in your own database. If your organization has [zero data retention (ZDR)](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention#zero-data-retention-zdr-scope) in place with Anthropic, it applies to the requests sent to Claude in the same way as any other Messages API call.

![Diagram 1: self-hosted Claude Managed Agents](https://assets.claude.com/7607c90e3d3d6e3bf9f7d1af0d39afb006be1413.svg)

## Designed for agent security

When an agent runs unattended inside your code and systems, you can't rely on a person checking every step, so the limits have to be built into the system itself. That's why agent security starts with architecture, and why we designed Managed Agents around four principles. These principles apply whether Anthropic hosts everything, you host just the sandbox, or you host the whole service.

**The brain and the hands are split**

The harness (the brain) calls Claude, and the sandbox (the hands) is where the agent's code runs. They are kept separate by design. The agent's code runs in the sandbox, while the agent loop, session history, and vault secrets stay outside it. [Separating them](https://www.anthropic.com/engineering/managed-agents) also means an agent doesn't depend on one sandbox surviving its whole run, sandboxes start only when a tool needs them, and session history lives outside the sandbox as an event log.

**Credentials stay out of the sandbox**

Vaults are designed to keep credentials out of the sandbox. For MCP tools and supported API calls, [a proxy outside the sandbox adds the credential to the request](https://platform.claude.com/docs/en/managed-agents/vaults). With self-hosted Managed Agents, you can also store credentials in your own secrets manager.

**Network access can be limited**

You can limit each environment to [a list of allowed hosts](https://platform.claude.com/docs/en/managed-agents/secure-deployment), and requests to any other host are blocked. For an agent that fixes broken builds, that list might be just your git host and your package registry. When you host the sandbox yourself, you set the same limits in your own firewall.

**Every session leaves a full record**

Managed Agents keeps a record of every step an agent took, including the tool calls it made and what came back. The record exports over [OpenTelemetry](https://platform.claude.com/docs/en/manage-claude/opentelemetry), so you can send it to the monitoring tools you already use and review agent activity alongside the rest of your systems.

## Get started

Self-hosted Claude Managed Agents is now available in private beta. Contact your Anthropic account team to request access, or read the [docs](https://platform.claude.com/docs/en/managed-agents/self-hosted) to learn more.

Article

Nov 12, 2026

### Introducing Claude for Manufacturing

A new plugin with 17 skills and four connectors helps manufacturers draft quotes, quality reports, and supplier requests from the systems they already run.

Article

Nov 12, 2026

### Introducing Claude Meetings

Add Claude to your video call and get the work started while you talk

Article

Nov 10, 2026

### Your apps can now open in Claude, and Claude can work in them

Our partners can now embed their apps directly in Claude, so you and Claude can work in the same tool, on the same screen, without switching tabs.

Claude appsMCP

Article

Nov 10, 2026

### More ways to work with Claude: Sheets, Whiteboards, and Interactive Connectors

Work at the speed of thought

Claude apps

## Transform how your organization operates with Claude

[See pricing](https://claude.com/pricing#api)[Contact sales](https://claude.com/contact-sales)

### Get the developer newsletter

Product updates, how-tos, community spotlights, and more. Delivered monthly to your inbox.

Please provide your email address if you'd like to receive our monthly developer newsletter. You can unsubscribe at any time.
