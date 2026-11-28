---
vendor: groq
title: chore: GitHub Terraform: Create/Update .github/workflows/stale.yaml [… · groq/groq-changelog@b64680c · GitHub
original_title: chore: GitHub Terraform: Create/Update .github/workflows/stale.yaml [… · groq/groq-changelog@b64680c · GitHub
url: https://github.com/groq/groq-changelog/commit/b64680cebef49c1392ea94580fd5c99b0ff33271
date: 2025-05-15
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 3992c11edf1c
---











- .github/workflows[stale.yaml](https://github.com/groq/groq-changelog/commit/b64680cebef49c1392ea94580fd5c99b0ff33271#diff-8ed8226600411f044974fddc34a67113e5f1a72e726ffad86676cf8c05186bec)





### [`‎.github/workflows/stale.yaml‎`](https://github.com/groq/groq-changelog/commit/b64680cebef49c1392ea94580fd5c99b0ff33271#diff-8ed8226600411f044974fddc34a67113e5f1a72e726ffad86676cf8c05186bec)

Copy file name to clipboard

Expand all lines: .github/workflows/stale.yaml

+

1

Lines changed: 1 addition & 0 deletions

| Original file line number | Diff line number | Diff line change |
| --- | --- | --- |
| `@@ -24,3 +24,4 @@ jobs:` |  |  |
| `24` | `24` | ` days-before-pr-stale: 30` |
| `25` | `25` | ` days-before-pr-close: 7` |
| `26` | `26` | ` exempt-pr-labels: "dependencies,security"` |
|  | `27` | `+ operations-per-run: 60 # Default is 30` |
