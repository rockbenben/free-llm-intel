---
vendor: anthropic
title: Cache diagnostics is out of beta on the Claude API and no longer requires the cache-diagnosis-2026-04-07 beta header.
original_title: 
url: https://platform.claude.com/docs/en/release-notes/overview
date: 2026-09-23
lang: en
captured: 2026-11-22
extractor: rss-entry
status: ok
body_sha: 51791aee9937
---

- [Cache diagnostics](https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics) is out of beta on the Claude API and no longer requires the `cache-diagnosis-2026-04-07` beta header. Include the `diagnostics` object on a Messages request to opt in; requests that still send the header work as before. Responses from `POST /v1/messages` now always include the `diagnostics` field, which is `null` when the request did not include the `diagnostics` object.
