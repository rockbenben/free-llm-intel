---
vendor: poolside
title: 长上下文更新：Laguna XS.2 和 M.1
original_title: 
url: https://poolside.ai/blog/long-context-update-laguna-xs-2-and-m-1
date: 2026-07-02
lang: zh
captured: 2026-10-08
extractor: readability-v1
translator: agent
status: translated
body_sha: d2dd9d7abfcb
---

# 长上下文更新：Laguna XS.2 和 M.1

我们非常高兴看到社区开始用我们的 Laguna XS.2 和 Laguna M.1 基础模型做构建。

在两个模型开放后的 4 周里，我们已经看到超过 1 万亿 token 被处理，Laguna XS.2 的权重从 Hugging Face 下载超过 50,000 次。

回应社区的反馈，现在两个模型都支持 256K 上下文。

Laguna M.1 目前在我们的 API 和 OpenRouter 上都以 256K 上下文窗口提供服务。Laguna XS.2 今天晚些时候也会更新到 256K——更新后的配置已经[  在 Hugging Face 上可用](https://huggingface.co/poolside/Laguna-XS.2)。

两个模型仍然可以免费使用。

Laguna M.1 依然是我们能力最强的模型。经过这次更新，它在 Terminal-Bench 2.0 上达到 45.8%，长程任务的表现有所提升。

- Laguna M.1 225B-A23B
- Laguna XS.2 33B-A3B
- Qwen3.6 35B-A3B
- DeepSeek-V4-Flash 284B-A13B
- Claude Sonnet 4.6 -

### SWE-bench Verified

SWE-bench Verified

在 SWE-bench Verified 上解决的任务。

### SWE-bench Multilingual

SWE-bench Multilingual

在 SWE-bench Multilingual 上解决的任务。

### SWE-Bench Pro

SWE-Bench Pro

在 SWE-Bench Pro 上解决的任务。

### Terminal-Bench 2.0

Terminal-Bench 2.0

在 Terminal-Bench 2.0 上解决的任务。

基准数据截至 2026 年 5 月 26 日。

两个模型仍然可以免费使用，可通过我们的 [  API](https://platform.poolside.ai/)，也可在 [  OpenRouter](https://openrouter.ai/provider/poolside) 上调用。马上开始：

- 安装 [  pool](https://poolside.ai/get-started)，我们基于终端的编程智能体，以及
- 用 [  Shimmer](https://shimmer.run/) 来构建，这是一套云端开发体验，用我们的模型反复迭代 web 应用、API 和 CLI。

脚注：Laguna M.1 与 Laguna XS.2 的全部评测都是使用 Laude Institute 的 Harbor Framework 完成的，配合我们的 [  agent harness](https://github.com/poolsideai/pool)，最多使用 500 个 step，在沙箱执行环境中运行，配置为 8 GB 内存 / 2 个 CPU（Terminal-Bench 2.0 除外，见下文）。两个模型、所有评测都使用同一套采样参数：temperature=1.0、top_k=20。部分基础任务镜像和 verifier 被打过补丁，以修复任务编排本身固有的基础设施可靠性问题，比如 verifier 所使用的外部仓库里第三方依赖的限流。关于这些改动及其他发现的更多细节，将在此后的技术博客文章中给出。

- SWE-Bench Pro：pass@1 均值，取 3 次运行的平均。
- SWE-bench Verified：pass@1 均值，取 4 次运行的平均。
- SWE-bench Multilingual：pass@1 均值，取 7 次运行的平均。
- Terminal-Bench 2.0：pass@1 均值，取 5 次运行的平均。48GB 内存 / 32 个 CPU。

在每个基准上，对所有对比模型我们采用的都是其公开引用过的最高分。所有情况下，这些都是发布博客文章或同等渠道公布的官方分数。
