---
vendor: groq
title: Python SDK v1.2.0 and TypeScript SDK v1.1.2
original_title: 
url: https://console.groq.com/docs/changelog.md
date: 2026-04-18
lang: en
captured: 2026-10-08
extractor: readability-v1
status: ok
body_sha: fd0f2c271468
---

### Changed[Python SDK v1.2.0 and TypeScript SDK v1.1.2](#python-sdk-v120-and-typescript-sdk-v112)

Following the [v1.0.0 GA in December 2025](https://github.com/groq/groq-python/releases/tag/v1.0.0), both SDKs received a series of updates over Q1.

**Python SDK** ([v1.2.0](https://github.com/groq/groq-python/releases/tag/v1.2.0))

* **v1.2.0** — Preserve hardcoded query params when merging with user params; ensure file data is sent as a single parameter; multipart request file-copy performance improvements; indices array format for query and form serialization.
* **v1.1.2** — Sanitize endpoint path params; do not pass `by_alias` to Pydantic unless explicitly set; bumped minimum `typing-extensions`.
* **v1.1.0** — Added support for binary request streaming and a custom JSON encoder for extended type support; deprecated Python 3.9.

**TypeScript SDK** ([v1.1.2](https://github.com/groq/groq-typescript/releases/tag/v1.1.2))

* **v1.1.1** — Restored streaming support in `defaultParseResponse`; fixed an abort-signal memory leak and avoided removing abort listeners too early; preserve URL params already embedded in path; pinned patched `minimatch` versions to address CVE-2026-27….
* **v1.1.2** — GitHub Actions OIDC token migration; dependency updates.
  
  
---
