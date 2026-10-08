---
vendor: poolside
title: Long context update: Laguna XS.2 and M.1 — Poolside
original_title: Long context update: Laguna XS.2 and M.1
url: https://poolside.ai/blog/long-context-update-laguna-xs-2-and-m-1
date: 2026-05-26
lang: en
captured: 2026-10-08
extractor: readability-v1
status: ok
body_sha: e4edbfd692ef
---

We have been thrilled to see the community start to build with our Laguna XS.2 and Laguna M.1 foundation models.

In the 4 weeks since making both models available we have seen over 1 trillion tokens processed and Laguna XS.2's weights have been downloaded from Hugging Face over 50,000 times.

In response to community feedback, both models now support 256K context.

Laguna M.1 is now being served with a 256K context window on our API and on OpenRouter. Laguna XS.2 will be updated to 256K later today — the updated configuration is already [  available on Hugging Face](https://huggingface.co/poolside/Laguna-XS.2).

Both models remain free to use.

Laguna M.1 remains our most capable model. With this update, it reaches 45.8% on Terminal-Bench 2.0, improving long-horizon performance.

- Laguna M.1 225B-A23B
- Laguna XS.2 33B-A3B
- Qwen3.6 35B-A3B
- DeepSeek-V4-Flash 284B-A13B
- Claude Sonnet 4.6 -

### SWE-bench Verified

SWE-bench Verified

Resolved tasks on SWE-bench Verified.

### SWE-bench Multilingual

SWE-bench Multilingual

Resolved tasks on SWE-bench Multilingual.

### SWE-Bench Pro

SWE-Bench Pro

Resolved tasks on SWE-Bench Pro.

### Terminal-Bench 2.0

Terminal-Bench 2.0

Resolved tasks on Terminal-Bench 2.0.

Benchmarks as of 26 May 2026.

Both models remain free to use via our [  API](https://platform.poolside.ai/) and on [  OpenRouter](https://openrouter.ai/provider/poolside). Get started immediately:

- Install [  pool](https://poolside.ai/get-started), our terminal-based coding agent, and
- Build with [  Shimmer](https://shimmer.run/), a cloud dev experience for iterating on web apps, APIs, and CLIs with our models.

Footnotes: All benchmarking for Laguna M.1 and Laguna XS.2 was completed using the Laude Institute’s Harbor Framework with our [  agent harness](https://github.com/poolsideai/pool), using a maximum of 500 steps and sandboxed execution using 8 GB RAM/2 CPUs (with the exception of Terminal-Bench 2.0; see below). The same sampling parameters were used across both models and for all benchmarking: temperature=1.0 and top_k=20. Some base task images and verifiers were patched to fix infrastructure reliability issues inherent in task setup, such as rate limits on third-party dependencies in external registries used by the verifier. More details outlining these updates and other findings will follow in a future technical blog post.

- SWE-Bench Pro: mean pass@1 averaged over 3 runs.
- SWE-bench Verified: mean pass@1 averaged over 4 runs.
- SWE-bench Multilingual: mean pass@1 averaged over 7 runs.
- Terminal-Bench 2.0: mean pass@1 averaged over 5 runs. 48GB RAM/32 CPUs.

We used the highest publicly-referenced scores for all comparison models across each benchmark. In all cases these were official scores published in release blog posts or equivalent.
