---
vendor: groq
title: Add Qwen3 + SDK updates (#8) · groq/groq-changelog@edee777 · GitHub
original_title: Add Qwen3 + SDK updates (#8) · groq/groq-changelog@edee777 · GitHub
url: https://github.com/groq/groq-changelog/commit/edee777a205934fcd2ddef6cc045099ddf4c129a
date: 2025-06-13
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 66fd9258887a
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

- [CHANGELOG.md](https://github.com/groq/groq-changelog/commit/edee777a205934fcd2ddef6cc045099ddf4c129a#diff-06572a96a58dc510037d5efa622f9bec8519bc1beab13c9f251e97e657a9d4ed)

Expand file tree

Collapse file tree

Open diff view settings

Collapse file

### [`‎CHANGELOG.md‎`](https://github.com/groq/groq-changelog/commit/edee777a205934fcd2ddef6cc045099ddf4c129a#diff-06572a96a58dc510037d5efa622f9bec8519bc1beab13c9f251e97e657a9d4ed)

Copy file name to clipboard

Expand all lines: CHANGELOG.md

+

61

Lines changed: 61 additions & 0 deletions

- Display the source diff
- Display the rich diff

| Original file line number | Diff line number | Diff line change |
| --- | --- | --- |
| `@@ -1,5 +1,66 @@` |  |  |
| `1` | `1` | `# Groq Changelog` |
| `2` | `2` |  |
|  | `3` | `+` |
|  | `4` | `+## 2025-06-12 (Python SDK v0.28.0, TypeScript SDK v0.25.0)` |
|  | `5` | `+` |
|  | `6` | `+### [UPDATED] Python SDK v0.28.0, TypeScript SDK v0.25.0` |
|  | `7` | `+` |
|  | `8` | `+The Python SDK has been updated to v0.28.0 and the Typescript SDK has been updated to v0.25.0.` |
|  | `9` | `+` |
|  | `10` | `+**Key Changes:**` |
|  | `11` | `+ - Added `reasoning` field for chat completion assistant messages. This is the reasoning output by the assistant if [`reasoning_format`](https://console.groq.com/docs/reasoning#options-for-reasoning-format) was set to `"parsed"`. This field is only usable with Qwen 3 models.` |
|  | `12` | `+ - Added [`reasoning_effort`](https://console.groq.com/docs/reasoning#options-for-reasoning-effort) parameter for Qwen 3 models (currently only [`qwen/qwen3-32b`](https://console.groq.com/docs/model/qwen3-32b)). Set to `"none"` to disable reasoning.` |
|  | `13` | `+` |
|  | `14` | `+## 2025-06-11 (Python SDK v0.27.0, TypeScript SDK v0.24.0)` |
|  | `15` | `+` |
|  | `16` | `+### [ADDED] Qwen 3 32B` |
|  | `17` | `+` |
|  | `18` | `+[Qwen 3 32B](https://console.groq.com/docs/model/qwen3-32b) is the latest generation of large language models in the Qwen series, offering groundbreaking advancements in reasoning, instruction-following, agent capabilities, and multilingual support. The model uniquely supports seamless switching between [thinking mode](https://console.groq.com/docs/reasoning) (for complex logical reasoning, math, and coding) and [non-thinking mode](https://console.groq.com/docs/reasoning#options-for-reasoning-effort).` |
|  | `19` | `+` |
|  | `20` | `+**Key Features:**` |
|  | `21` | `+- 128K token context window` |
|  | `22` | `+- Support for 100+ languages and dialects` |
|  | `23` | `+- Tool use and JSON mode support` |
|  | `24` | `+- Token generation speed of ~491 TPS` |
|  | `25` | `+- Input token price: $0.29/1M tokens` |
|  | `26` | `+- Output token price: $0.59/1M tokens` |
|  | `27` | `+` |
|  | `28` | `+**Performance Metrics:**` |
|  | `29` | `+- 93.8% score on ArenaHard` |
|  | `30` | `+- 81.4% pass rate on AIME 2024` |
|  | `31` | `+- 65.7% on LiveCodeBench` |
|  | `32` | `+- 30.3% on BFCL` |
|  | `33` | `+- 73.0% on MultiIF` |
|  | `34` | `+- 72.9% on AIME 2025` |
|  | `35` | `+- 71.6% on LiveBench` |
|  | `36` | `+` |
|  | `37` | `+**Example Usage:**` |
|  | `38` | `+```sh` |
|  | `39` | `+curl "https://api.groq.com/openai/v1/chat/completions" \` |
|  | `40` | `+ -X POST \` |
|  | `41` | `+ -H "Content-Type: application/json" \` |
|  | `42` | `+ -H "Authorization: Bearer ${GROQ_API_KEY}" \` |
|  | `43` | `+ -d '{` |
|  | `44` | `+ "messages": [` |
|  | `45` | `+ {` |
|  | `46` | `+ "role": "user",` |
|  | `47` | `+ "content": "Explain why fast inference is critical for reasoning models"` |
|  | `48` | `+ }` |
|  | `49` | `+ ],` |
|  | `50` | `+ "model": "qwen/qwen3-32b",` |
|  | `51` | `+ "reasoning_effort": "none"` |
|  | `52` | `+ }'` |
|  | `53` | `+```` |
|  | `54` | `+` |
|  | `55` | `+### [CHANGED] Python SDK v0.27.0, TypeScript SDK v0.24.0` |
|  | `56` | `+` |
|  | `57` | `+The Python SDK has been updated to v0.26.0 and the Typescript SDK has been updated to v0.23.0.` |
|  | `58` | `+` |
|  | `59` | `+**Key Changes:**` |
|  | `60` | `+ - The `search_settings` parameter when using [agentic tooling systems](https://console.groq.com/docs/agentic-tooling) now includes a new field: `include_images`. Set this to `true` to include images in the search results, and `false` to exclude images from the search results.` |
|  | `61` | `+ - Added `code_results` to each executed tool output when using [agentic tooling systems](https://console.groq.com/docs/agentic-tooling). This field can include `png` (when code execution produces an image, encoded in Base64 format) and `text` (text output of the code execution).` |
|  | `62` | `+` |
|  | `63` | `+` |
| `3` | `64` | `## 2025-05-29 (Python SDK v0.26.0, TypeScript SDK v0.23.0)` |
| `4` | `65` |  |
| `5` | `66` | `### [CHANGED] Python SDK v0.26.0, TypeScript SDK v0.23.0` |
|  |  |  |

## 0 commit comments

Comments

0

(

0

)
