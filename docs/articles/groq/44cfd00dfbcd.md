---
vendor: groq
title: Python SDK v1.6.0 与 TypeScript SDK v1.5.0
original_title: 
url: https://console.groq.com/docs/changelog.md#python-sdk-v160-and-typescript-sdk-v150
date: 2026-08-10
lang: zh
captured: 2026-11-17
extractor: readability-v1
translator: agent
status: translated
body_sha: ba8d339962b3
---

### 变更[Python SDK v1.6.0 与 TypeScript SDK v1.5.0](#python-sdk-v160-and-typescript-sdk-v150)

两个 SDK 在第二季度都迎来了一系列更新。

**Python SDK** ([v1.6.0](https://github.com/groq/groq-python/releases/tag/v1.6.0))

* **v1.3.0** — 支持通过环境变量设置请求头；修复了 multipart 文件数组的字段名格式。
* **v1.4.0** — 支持对 pydantic 迭代器进行提前校验（eager validation）。
* **v1.5.0** — API 规范更新。
* **v1.6.0** — CI 与工作流模板更新。

**TypeScript SDK** ([v1.5.0](https://github.com/groq/groq-typescript/releases/tag/v1.5.0))

* **v1.2.0** — 支持通过环境变量设置请求头。
* **v1.2.1** — 升级 `tsc-multi` 以兼容 Node 26。
* **v1.3.0** — API 规范更新；对省略了可选请求体的请求，发送 content-type 请求头。
* **v1.4.0 / v1.4.1** — CI 工作流在 Node 24 上运行；依赖更新。
* **v1.5.0** — API 规范更新。

---
