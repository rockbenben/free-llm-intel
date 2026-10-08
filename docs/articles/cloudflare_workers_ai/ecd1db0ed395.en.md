---
vendor: cloudflare_workers_ai
title: Workers AI - 对 llama-3.2-1b-instruct、whisper-large-v3-turbo、llama-guard 的模型 schema 小幅更新
original_title: 
url: https://developers.cloudflare.com/workers-ai/changelog
date: 2025-03-17
lang: en
captured: 2026-10-08
extractor: readability-v1
status: ok
body_sha: db9151e91970
---

Minor updates to the model schema for llama-3.2-1b-instruct, whisper-large-v3-turbo, llama-guard

- [llama-3.2-1b-instruct](https://developers.cloudflare.com/workers-ai/models/llama-3.2-1b-instruct/) - updated context window to the accurate 60,000
- [whisper-large-v3-turbo](https://developers.cloudflare.com/workers-ai/models/whisper-large-v3-turbo/) - new hyperparameters available
- [llama-guard-3-8b](https://developers.cloudflare.com/workers-ai/models/llama-guard-3-8b/) - the messages array must alternate between `user` and `assistant` to function correctly
