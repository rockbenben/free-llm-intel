---
vendor: groq
title: Add prompt caching (#14) · groq/groq-changelog@fc1e7dc · GitHub
original_title: Add prompt caching (#14) · groq/groq-changelog@fc1e7dc · GitHub
url: https://github.com/groq/groq-changelog/commit/fc1e7dc66859b831b42594389098d756e06fcd0c
date: 2025-08-20
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 31e385a795a5
---

groq


groq-changelog

Public

- [ Notifications ](https://github.com/login?return_to=%2Fgroq%2Fgroq-changelog) You must be signed in to change notification settings
- [ Fork 0 ](https://github.com/login?return_to=%2Fgroq%2Fgroq-changelog)
- [  Star  17 ](https://github.com/login?return_to=%2Fgroq%2Fgroq-changelog)

## File tree

Expand file tree

Collapse file tree

Open diff view settings

Filter options

- [CHANGELOG.md](https://github.com/groq/groq-changelog/commit/fc1e7dc66859b831b42594389098d756e06fcd0c#diff-06572a96a58dc510037d5efa622f9bec8519bc1beab13c9f251e97e657a9d4ed)

Expand file tree

Collapse file tree

Open diff view settings

Collapse file

### [`‎CHANGELOG.md‎`](https://github.com/groq/groq-changelog/commit/fc1e7dc66859b831b42594389098d756e06fcd0c#diff-06572a96a58dc510037d5efa622f9bec8519bc1beab13c9f251e97e657a9d4ed)

Copy file name to clipboard

Expand all lines: CHANGELOG.md

+

16

Lines changed: 16 additions & 0 deletions

- Display the source diff
- Display the rich diff

| Original file line number | Diff line number | Diff line change |
| --- | --- | --- |
| `@@ -1,5 +1,21 @@` |  |  |
| `1` | `1` | `# Groq Changelog` |
| `2` | `2` |  |
|  | `3` | `+## 2025-08-20 (Python SDK v0.31.0, TypeScript SDK v0.30.0)` |
|  | `4` | `+` |
|  | `5` | `+### [ADDED] Prompt Caching` |
|  | `6` | `+` |
|  | `7` | `+Prompt caching automatically reuses computation from recent requests when they share a common prefix, delivering significant cost savings and improved response times while maintaining data privacy through volatile-only storage that expires automatically. ` |
|  | `8` | `+` |
|  | `9` | `+**How It Works**` |
|  | `10` | `+- Prefix Matching: When you send a request, the system examines and identifies matching prefixes from recently processed requests stored temporarily in volatile memory. Prefixes can include system prompts, tool definitions, few-shot examples, and more.` |
|  | `11` | `+- Cache Hit: If a matching prefix is found, cached computation is reused, dramatically reducing latency and token costs by 50% for cached portions.` |
|  | `12` | `+- Cache Miss: If no match exists, your prompt is processed normally, with the prefix temporarily cached for potential future matches.` |
|  | `13` | `+- Automatic Expiration: All cached data automatically expires within a few hours, which helps ensure privacy while maintaining the benefits.` |
|  | `14` | `+` |
|  | `15` | `+Prompt caching is rolling out to [Kimi K2](https://console.groq.com/docs/model/moonshotai/kimi-k2-instruct) starting today with support for additional models coming soon. This feature works automatically on all your API requests with no code changes required and no additional fees.` |
|  | `16` | `+` |
|  | `17` | `+[Learn more about prompt caching in our docs.](https://console.groq.com/docs/prompt-caching)` |
|  | `18` | `+` |
| `3` | `19` | `## 2025-08-05 (Python SDK v0.31.0, TypeScript SDK v0.30.0)` |
| `4` | `20` |  |
| `5` | `21` | `### [ADDED] OpenAI GPT-OSS 20B & OpenAI GPT-OSS 120B` |
|  |  |  |

## 0 commit comments

Comments

0

(

0

)
