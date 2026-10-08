---
vendor: groq
title: Python SDK v1.2.0 and TypeScript SDK v1.1.2
original_title: 
url: https://console.groq.com/docs/changelog.md#python-sdk-v120-and-typescript-sdk-v112
date: 2026-04-18
lang: zh
captured: 2026-10-08
extractor: readability-v1
translator: agent
status: translated
body_sha: 2cac8555da6c
---

# Python SDK v1.2.0 and TypeScript SDK v1.1.2

### 变更[Python SDK v1.2.0 与 TypeScript SDK v1.1.2](#python-sdk-v120-and-typescript-sdk-v112)

继 [2025 年 12 月的 v1.0.0 正式版](https://github.com/groq/groq-python/releases/tag/v1.0.0)之后，两个 SDK 在第一季度都进行了一系列更新。

**Python SDK**（[v1.2.0](https://github.com/groq/groq-python/releases/tag/v1.2.0)）

* **v1.2.0** — 在与用户参数合并时保留硬编码的查询参数；确保文件数据作为单个参数发送；改进 multipart 请求的文件拷贝性能；查询与表单序列化采用 indices 数组格式。
* **v1.1.2** — 对端点路径参数做净化处理；除非显式设置，否则不向 Pydantic 传入 `by_alias`；提升了 `typing-extensions` 的最低版本要求。
* **v1.1.0** — 新增对二进制请求流式传输的支持，并提供自定义 JSON 编码器以支持更多类型；弃用 Python 3.9。

**TypeScript SDK**（[v1.1.2](https://github.com/groq/groq-typescript/releases/tag/v1.1.2)）

* **v1.1.1** — 恢复了 `defaultParseResponse` 中的流式支持；修复了 abort signal 内存泄漏，并避免过早移除 abort 监听器；保留已经嵌入到路径中的 URL 参数；锁定打过补丁的 `minimatch` 版本以处理 CVE-2026-27…。
* **v1.1.2** — GitHub Actions OIDC token 迁移；依赖更新。

---
