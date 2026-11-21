---
vendor: anthropic
title: We’ve launched Claude Opus 4.8 (claude-opus-4-8), our most capable model.
original_title: 
url: https://platform.claude.com/docs/en/release-notes/overview
date: 2026-05-28
lang: en
captured: 2026-11-22
extractor: rss-entry
status: ok
body_sha: 6b9b7464d5d3
---

- We’ve launched **Claude Opus 4.8** (`claude-opus-4-8`), our most capable model. Claude Opus 4.8 supports a [1M token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows) by default on the Claude API, Amazon Bedrock, Google Cloud, and Microsoft Foundry, 128k max output tokens, and the same set of tools and platform features as Claude Opus 4.7. See the [migration guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide) for baseline settings, features, and migration guidance.
- We’ve launched [mid-conversation system messages](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages). On Claude Opus 4.8, you can send `role: "system"` messages after a user turn (subject to [placement rules](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages#limitations)) in the `messages` array, preserving prompt cache hits when instructions change during a long-running session. No beta header is required.
- The [`stop_details`](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback#refusal-response) field on refusal responses is now publicly documented; it returns a `category` (`cyber`, `bio`, or `null`) and a human-readable `explanation`, so your application can route different classes of refusal to the right next step. No beta header is required.
- On Claude Opus 4.8, the [effort parameter](https://platform.claude.com/docs/en/build-with-claude/effort) defaults to `high` across all surfaces, including Claude Code and the Messages API.
- On Claude Opus 4.8, the minimum cacheable prompt length for [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) is 1,024 tokens, lower than on Claude Opus 4.7.
- With [adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/thinking) enabled, Claude Opus 4.8 triggers reasoning only when a turn needs it, reducing wasted thinking tokens compared to Claude Opus 4.7 at the same effort level.
- Claude Opus 4.8 supports [high-resolution image input](https://platform.claude.com/docs/en/build-with-claude/vision#high-resolution-image-support-on-claude-opus-4-7) (up to 2,576 pixels on the long edge), same as Claude Opus 4.7.
- [Task budgets](https://platform.claude.com/docs/en/build-with-claude/task-budgets) now support Claude Opus 4.8.
- The [advisor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool) now supports Claude Opus 4.8.
- [Computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool) now supports Claude Opus 4.8.
- [Fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode) for Claude Opus 4.8 is available as a research preview on the Claude API only.
- Setting the sampling parameters `temperature`, `top_p`, or `top_k` to a non-default value returns a 400 error on Claude Opus 4.8, same as on Claude Opus 4.7. See the [migration guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide) for details.
- In Claude Code, we’ve expanded Auto mode to more users for long-running tasks. See the [Claude Code documentation](https://code.claude.com/docs).
- In Claude Code, Max plan users now default to [fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode) on Claude Opus 4.8. See the [Claude Code documentation](https://code.claude.com/docs).
- In Claude Code, Workflows are available as a research preview, letting you define and run multistep agentic plans. See the [Claude Code documentation](https://code.claude.com/docs).
- We’ve deprecated [fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode) for Claude Opus 4.6, with removal approximately 30 days after launch. Migrate to fast mode for Claude Opus 4.8 or Claude Opus 4.7. Read more in [Fast mode model availability](https://platform.claude.com/docs/en/build-with-claude/fast-mode#supported-models).
- For updates to claude.ai, Cowork, Claude for Microsoft 365, and other Claude apps in this release, see the [release notes for Claude Apps](https://support.claude.com/en/articles/12138966-release-notes).
