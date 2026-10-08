---
vendor: cloudflare_workers_ai
title: Workers AI - 对 llama-3.2-1b-instruct、whisper-large-v3-turbo、llama-guard 的模型 schema 小幅更新
original_title: 
url: https://developers.cloudflare.com/workers-ai/changelog#minor-updates-to-the-model-schema-for-llama-32-1b-instruct-whisper-large-v3-turbo-llama-guard
date: 2025-03-17
lang: zh
captured: 2026-10-08
extractor: readability-v1
translator: agent
status: translated
body_sha: cb640763b53a
---

# Workers AI - 对 llama-3.2-1b-instruct、whisper-large-v3-turbo、llama-guard 的模型 schema 小幅更新

llama-3.2-1b-instruct、whisper-large-v3-turbo、llama-guard 的模型 schema 小幅更新

- [llama-3.2-1b-instruct](https://developers.cloudflare.com/workers-ai/models/llama-3.2-1b-instruct/) - 上下文窗口更新为准确的 60,000
- [whisper-large-v3-turbo](https://developers.cloudflare.com/workers-ai/models/whisper-large-v3-turbo/) - 新增了可用的超参数
- [llama-guard-3-8b](https://developers.cloudflare.com/workers-ai/models/llama-guard-3-8b/) - messages 数组必须在 `user` 和 `assistant` 之间交替，才能正常工作
