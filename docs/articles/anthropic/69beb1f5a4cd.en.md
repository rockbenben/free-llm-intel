---
vendor: anthropic
title: We’ve released API version 2026-10-21.
original_title: 
url: https://platform.claude.com/docs/en/release-notes/overview
date: 2026-10-21
lang: en
captured: 2026-11-22
extractor: rss-entry
status: ok
body_sha: 2d1110b548f9
---

- We’ve released API version `2026-10-21`. [Migrating to API version 2026-10-21](https://platform.claude.com/docs/en/api/migration-2026-10-21) shows how to upgrade.
- We’ve released new versions of the [client SDKs](https://platform.claude.com/docs/en/cli-sdks-libraries/overview) and the [`ant` CLI](https://platform.claude.com/docs/en/cli-sdks-libraries/cli/quickstart) that send API version `2026-10-21` by default: Python SDK 2.0.0, TypeScript SDK 1.0.0, C# SDK 13.0.0, Go SDK 2.0.0, Java SDK 3.0.0, PHP SDK 1.0.0, Ruby SDK 2.0.0, and `ant` CLI 2.0.0. See [Switch to 2026-10-21](https://platform.claude.com/docs/en/api/migration-2026-10-21#upgrade).
- The new SDK and CLI versions also have breaking changes that don’t depend on the API version, and they are licensed under Apache 2.0 instead of the MIT License. See [SDK and CLI changes](https://platform.claude.com/docs/en/api/migration-2026-10-21#sdk-changes).
- We’ve added the `enforcement_status` and `enforcement_actions` fields to [user profiles](https://platform.claude.com/docs/en/manage-claude/user-profiles), so you can see whether Anthropic has restricted or banned one of your end customers. To find the profiles that have an open restriction or ban, [list your profiles](https://platform.claude.com/docs/en/api/user_profiles/list) with the new `enforcement_status[]` filter. See [Check whether Anthropic has restricted or banned a profile](https://platform.claude.com/docs/en/manage-claude/user-profiles#check-whether-anthropic-has-restricted-or-banned-a-profile).
