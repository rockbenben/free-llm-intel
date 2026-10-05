---
vendor: cerebras
title: GLM-4.7: Frontier intelligence at record speed — now available on Cerebras
original_title: GLM-4.7: Frontier intelligence at record speed — now available on Cerebras
url: https://www.cerebras.ai/blog/glm-4-7
date: 
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 5fc8192e7599
---

Jan 08 2026

# GLM-4.7: Frontier intelligence at record speed — now available on Cerebras

Eric Gardner

Today, we’re announcing GLM-4.7, the latest GLM family model released from Z.ai, now available on Cerebras Inference Cloud. This model combines speed with frontier intelligence, for coding, tool-driven agents, multi-turn reasoning, and more.

### Frontier Intelligence

GLM-4.7 is a clear step up from GLM-4.6. Against leading closed models, GLM-4.7 demonstrates comparable high-quality code generation and editing, reliable tool use, and consistent multi-turn reasoning. All at up to an order of magnitude higher speed and price-performance!

On benchmarks that reflect real developer workloads, GLM-4.7 now ranks as the top open-weight model, leading DeepSeek-V3.2 across a broad set of advanced developer benchmarks, including SWEbench, τ²bench, and LiveCodeBench.

Coding improvements in day-to-day development work are the most immediately visible advance from GLM-4.6 to 4.7. With more accurate solutions, cleaner structure, and stronger multilingual output, GLM-4.7 is noticeably more intelligent while stable over long, iterative coding sessions. It is also better at understanding project context, recovering from errors, and refining code across turns.

Tool-driven agent workflows also take a clear step forward in 4.7. The model is more reliable at planning, calling tools, and maintaining context across multi-step interactions — a direct result of how it handles reasoning internally.

GLM-4.7 further advances how reasoning works in practice. It builds on the idea of interleaved thinking, where the model reasons before each action, tool call, or response, rather than treating reasoning as a single upfront step. It also introduces preserved thinking, allowing reasoning context to persist across turns.

Together, these changes improve performance on complex math, logic, and tool-augmented tasks, reduce the need to rederive plans from scratch, and lead to more consistent behavior in multi-step workflows. The result is agents that reason more reliably over time and general interactions — including chat and role-play — that feel more natural and stable, with fewer abrupt shifts in tone or intent.

### Record Speed

What truly sets GLM-4.7 apart is that this level of intelligence now runs at real-time speeds on the Cerebras wafer-scale engine. When deployed on Cerebras hardware, GLM-4.7 code generation happens at approximately 1,000 tokens per second (and even up to [1,700 TPS](https://artificialanalysis.ai/models/glm-4-7-non-reasoning/providers) for some use cases). This speed requires Cerebras’ AI-specialized hardware and is not possible with comparable models that run on GPUs or other architectures.

When inference latency drops out of the critical path, teams can deploy models directly into user-facing products and time-sensitive workflows without compromising capability. GLM-4.7’s real-time performance on Cerebras makes frontier-level coding assistants, live agents, and latency-sensitive applications practical — while retaining flexibility through its open-weight design.

### Price-Performance

When teams evaluate model cost, it’s tempting to focus on price per token. In practice, what matters more is how quickly a model produces useful output.

GLM-4.7 runs up to an order of magnitude faster than leading closed models like Claude Sonnet 4.5 on real coding and agentic workloads. That speed directly reduces end-to-end cost by shortening sessions, lowering concurrency requirements, and reducing the infrastructure needed to deliver the same user experience.

Even when per-token pricing is similar across providers, the economics diverge quickly. Faster generation means developers spend less time waiting, agents complete tasks in fewer turns, and systems deliver more usable work per unit of time. This is the same dynamic that made GLM-4.6 compelling, and GLM-4.7 extends it further with even greater intelligence.

GLM-4.7 on Cerebras delivers ~10x higher price-performance than Claude Sonnet 4.5, and is on par with DeepSeek-V3.2 albeit with higher accuracy.

### Get Started Today

GLM-4.7 is a clear upgrade from GLM-4.6 and the strongest open model Cerebras has deployed to date. It outperforms other open-weight models like DeepSeek-V3.2 on key developer evaluations, and features comparable intelligence with leading closed models on the coding and agentic workloads that matter in production—while delivering an order of magnitude faster generation speed on Cerebras.

GLM-4.7 is fully compatible with existing GLM-4.6 chat completions workflows, using the same API surface with improved quality. For most teams, migrating is as simple as updating the model name. We recommend starting with the default settings and enabling preserved thinking for coding and agentic use cases.

Get started on Cerebras Cloud, including our pay-as-you-go developer tier starting at just $10, which includes generous rate limits that make it easy to prototype, build, and scale without big upfront costs.

If you’re on GLM-4.6, follow this [easy migration](https://inference-docs.cerebras.ai/resources/glm-47-migration) [checklist](https://inference-docs.cerebras.ai/resources/glm-47-migration). 
If not, [try GLM-4.7](https://cloud.cerebras.ai/) on the Cerebras Cloud today starting at just $10 on our dev tier.

Learn more about the model from Z.ai: https://z.ai/blog/glm-4.7
As always, we welcome your feedback on [Discord](https://discord.com/invite/q6bZcMWJVu) or [X](https://x.com/cerebras).
