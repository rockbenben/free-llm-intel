---
vendor: groq
title: chore：GitHub Terraform——创建/更新 .github/workflows/stale.yaml（…）· groq/groq-changelog@b64680c · GitHub
original_title: chore: GitHub Terraform: Create/Update .github/workflows/stale.yaml [… · groq/groq-changelog@b64680c · GitHub
url: https://github.com/groq/groq-changelog/commit/b64680cebef49c1392ea94580fd5c99b0ff33271
date: 2025-05-15
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

### [.github/workflows/stale.yaml](https://github.com/groq/groq-changelog/commit/b64680cebef49c1392ea94580fd5c99b0ff33271#diff-8ed8226600411f044974fddc34a67113e5f1a72e726ffad86676cf8c05186bec)

行数变化：新增 1 行，删除 0 行

本次提交为 GitHub Actions 的 stale 工作流配置新增了一行参数（代码变更原样如下）：

```yaml
@@ -24,3 +24,4 @@ jobs:
 days-before-pr-stale: 30
 days-before-pr-close: 7
 exempt-pr-labels: "dependencies,security"
+ operations-per-run: 60 # Default is 30
```

即把每次运行的 API 操作次数上限从默认的 30 提高到 60。
