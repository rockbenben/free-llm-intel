---
vendor: groq
title: Add Kimi K2 (#10) · groq/groq-changelog@3e0d869 · GitHub
original_title: Add Kimi K2 (#10) · groq/groq-changelog@3e0d869 · GitHub
url: https://github.com/groq/groq-changelog/commit/3e0d86955b531ee3a8076d0f3a1bc63260daaf72
date: 2025-07-15
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 7edfedb1e532
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

- [CHANGELOG.md](https://github.com/groq/groq-changelog/commit/3e0d86955b531ee3a8076d0f3a1bc63260daaf72#diff-06572a96a58dc510037d5efa622f9bec8519bc1beab13c9f251e97e657a9d4ed)

Expand file tree

Collapse file tree

Open diff view settings

Collapse file

### [`‎CHANGELOG.md‎`](https://github.com/groq/groq-changelog/commit/3e0d86955b531ee3a8076d0f3a1bc63260daaf72#diff-06572a96a58dc510037d5efa622f9bec8519bc1beab13c9f251e97e657a9d4ed)

Copy file name to clipboard

Expand all lines: CHANGELOG.md

+

43

Lines changed: 43 additions & 0 deletions

- Display the source diff
- Display the rich diff

| Original file line number | Diff line number | Diff line change |
| --- | --- | --- |
| `@@ -1,5 +1,48 @@` |  |  |
| `1` | `1` | `# Groq Changelog` |
| `2` | `2` |  |
|  | `3` | `+## 2025-07-15 (Python SDK v0.30.0, TypeScript SDK v0.27.0)` |
|  | `4` | `+` |
|  | `5` | `+### [CHANGED] Python SDK v0.30.0, TypeScript SDK v0.27.0` |
|  | `6` | `+` |
|  | `7` | `+The Python SDK has been updated to v0.30.0 and the Typescript SDK has been updated to v0.27.0.` |
|  | `8` | `+` |
|  | `9` | `+**Key Changes:**` |
|  | `10` | `+ - Improved chat completion message type definitions for better compatibility with OpenAI. This fixes errors in certain cases with different message formats.` |
|  | `11` | `+` |
|  | `12` | `+### [ADDED] Moonshot AI Kimi 2 Instruct` |
|  | `13` | `+` |
|  | `14` | `+[Kimi K2 Instruct](https://console.groq.com/docs/model/moonshotai/kimi-k2-instruct) is Moonshot AI's state-of-the-art Mixture-of-Experts (MoE) language model with 1 trillion total parameters and 32 billion activated parameters. Designed for agentic intelligence, it excels at tool use, coding, and autonomous problem-solving across diverse domains.` |
|  | `15` | `+` |
|  | `16` | `+Kimi K2 Instruct is perfect for agentic use cases and coding. [Learn more about how to use tools here.](https://console.groq.com/docs/tool-use)` |
|  | `17` | `+` |
|  | `18` | `+**Key Features:**` |
|  | `19` | `+- 131K token context window` |
|  | `20` | `+- 16K max output tokens` |
|  | `21` | `+- MoE architecture with 384 experts (8 selected per token)` |
|  | `22` | `+- Surpasses GPT-4.1 on agentic and coding use cases` |
|  | `23` | `+` |
|  | `24` | `+**Performance Metrics:**` |
|  | `25` | `+- 53.7% Pass@1 on LiveCodeBench (coding performance)` |
|  | `26` | `+- 65.8% single-attempt accuracy on SWE-bench Verified` |
|  | `27` | `+- 89.5% exact match on MMLU` |
|  | `28` | `+- 70.6% Avg@4 on Tau2 retail tasks` |
|  | `29` | `+` |
|  | `30` | `+**Example Usage:**` |
|  | `31` | `+```curl` |
|  | `32` | `+curl https://api.groq.com/openai/v1/chat/completions \` |
|  | `33` | `+ -H "Authorization: Bearer $GROQ_API_KEY" \` |
|  | `34` | `+ -H "Content-Type: application/json" \` |
|  | `35` | `+ -d '{` |
|  | `36` | `+ "model": "moonshotai/kimi-k2-instruct",` |
|  | `37` | `+ "messages": [` |
|  | `38` | `+ {` |
|  | `39` | `+ "role": "user",` |
|  | `40` | `+ "content": "Explain why fast inference is critical for reasoning models"` |
|  | `41` | `+ }` |
|  | `42` | `+ ]` |
|  | `43` | `+ }'` |
|  | `44` | `+```` |
|  | `45` | `+` |
| `3` | `46` |  |
| `4` | `47` | `## 2025-06-25 (Python SDK v0.29.0, TypeScript SDK v0.26.0)` |
| `5` | `48` |  |
|  |  |  |

## 0 commit comments

Comments

0

(

0

)
