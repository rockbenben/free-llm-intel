---
vendor: groq
title: GPT-OSS 20B 启用提示词缓存
original_title: Prompt Caching Enabled for GPT-OSS 20B
url: https://console.groq.com/docs/changelog.md
date: 2025-09-25
lang: en
captured: 2026-10-08
extractor: readability-v1
status: ok
body_sha: 0add8d4f9ae7
---

### Added[Prompt Caching Enabled for GPT-OSS 20B](#prompt-caching-enabled-for-gptoss-20b)

Automatic prompt caching is now live for [openai/gpt-oss-20b](https://console.groq.com/docs/model/openai/gpt-oss-20b). Cache hits automatically provide:

* **50% cost savings** on cached input tokens ($0.037/M vs $0.075/M)
* **Lower latency** through reused computation
* **Automatic prefix matching** for seamless cache utilization

Zero setup required - you automatically benefit from caching when your requests share common prefixes with recent requests. [Learn more about prompt caching](https://console.groq.com/docs/prompt-caching).
  
  
---
