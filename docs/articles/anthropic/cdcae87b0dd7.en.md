---
vendor: anthropic
title: We’ve launched Claude Sonnet 5.5 (claude-sonnet-5-5).
original_title: 
url: https://platform.claude.com/docs/en/release-notes/overview
date: 2026-09-28
lang: en
captured: 2026-11-22
extractor: rss-entry
status: ok
body_sha: 81638e488bb6
---

- We’ve launched **Claude Sonnet 5.5** (`claude-sonnet-5-5`). It’s available on the Claude API, [Claude in Amazon Bedrock](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock), [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws), [Claude Models on Google Cloud (Google managed)](https://platform.claude.com/docs/en/build-with-claude/claude-models-on-google-cloud/google-managed), and [Claude in Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry). For its context window, output limits, and prices, see the [Claude Sonnet 5.5 model page](https://platform.claude.com/docs/en/models/sonnet-5-5/overview).
- Code written for Claude Sonnet 5 can break on Claude Sonnet 5.5 in five ways. To turn off up-front thinking, send `thinking: {"type": "between_tools"}` instead of `"disabled"`, at `high` effort or below. Forced tool use (`tool_choice` types `any` and `tool`) returns a 400 error. Thinking blocks are tied to the model and the conversation. On the Claude API and Google Cloud, the earlier `computer_20251124` computer use tool isn’t accepted. The advisor tool rejects Claude Opus 4.8, Claude Opus 4.7, and Claude Sonnet 5 as advisors. See [What’s new in Claude Sonnet 5.5](https://platform.claude.com/docs/en/models/sonnet-5-5/whats-new-sonnet-5-5) for each change and the [Claude Sonnet 5.5 migration guide](https://platform.claude.com/docs/en/models/sonnet-5-5/migration-guide) for before-and-after requests. For model-specific prompting patterns, see [Prompting Claude Sonnet 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5).
- Thinking blocks that Claude Sonnet 5.5 produces work only in the account that produced them, or in an account linked to it. When another account sends one of these blocks, the API drops the block before the model sees it, and the request succeeds. Blocks from earlier models aren’t affected. See [Thinking blocks stay with the account that produced them](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking#account-bound-thinking).
