---
vendor: huggingface
title: 并发请求的 Prefill 与 Decode——LLM 性能优化
original_title: Prefill and Decode for Concurrent Requests
url: https://huggingface.co/blog/tngtech/llm-performance-prefill-decode-concurrent-requests
date: 2025-07-28
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# 并发请求的 Prefill 与 Decode——LLM 性能优化

并行处理多用户负载，对 LLM 应用的性能至关重要。在我们 LLM 性能系列的[上一部分](https://huggingface.co/blog/tngtech/llm-performance-request-queueing)中，我们讨论了用于区分不同用户优先级的排队策略。第二部分聚焦请求的并发处理，以及它如何影响延迟、吞吐等关键指标和 GPU 资源利用率。

在 TNG，我们在由 24 块 H100 GPU 组成的集群上自托管了大量大语言模型。它支撑着 50 个不同应用，每小时处理超过 5000 次推理，每天生成超过一千万个 token。

### Token 生成的两个阶段：Prefill 与 Decode

大多数 LLM 逐个 token 地生成文本，这保证每个新 token 都基于其前面所有 token 计算（这一模型属性称为*自回归*）。第一个输出 token 依赖全部 prompt token；第二个输出 token 已经依赖全部 prompt token *加上*第一个输出 token，依此类推。因此，在单个请求的层面，token 生成无法并行化。

在带注意力机制的 LLM 中，计算一个新 token 需要为每个先前的 token 计算 *key*、*value* 和 *query* 向量。幸运的是，某些特定计算的结果可以为后续 token 复用，这一概念就是 key-value（KV）缓存。每多一个输出 token，只需再多计算一组 *key* 和 *value* 向量并加入 KV 缓存。但对第一个输出 token，我们从最初为空的 KV 缓存开始，需要计算的 *key* 和 *value* 向量组数等于输入 prompt 的 token 数。幸好，与之后的任何 token 生成不同，所有输入 token 从一开始就已知，我们可以并行计算它们各自的 *key* 和 *value* 向量。这一差异催生了 **prefill（计算第一个输出 token）**与 **decode 阶段（计算之后的输出 token）**的划分。

在 prefill 阶段，所有输入 token 的计算可以并行执行；而在 decode 阶段，单请求层面无法并行。

prefill: 并行处理 prompt token，

decode: 串行处理单个输出 token。

#### 指标

prefill 与 decode 阶段的差异也体现在文本生成的两个关键指标上：*Time to first token* 和 *time per output token*。***time to first token*** 由 prefill 阶段的延迟决定，而 ***time per output token*** 是单个 decode 步骤的延迟。虽然 prefill 阶段同样只生成一个 token，但由于要处理所有输入 token，它比单个 decode 步骤耗时得多。另一方面，就每输入 token 而言，prefill 阶段比生成相同数量输出 token 的 decode 阶段快得多（这一差异正是商业 LLM API 对输入 token 定价远低于输出 token 的原因）。

通过在推理后端追踪请求到达时间、并在流式输出中追踪每个 token 的生成时间，我们可以测量 prefill 时间（即

time to first token

）以及每个 decode 步骤的耗时（即

time per output token

）。

这两种延迟对聊天机器人这类交互应用都很重要。如果用户要等待超过 5 秒才能看到回应，他们可能认为应用坏了而离开。同样，如果文本生成慢到每秒 1 个 token，他们也不会有耐心等到结束。交互应用典型的延迟目标是每输出 token 100-300ms（即每秒 3-10 个 token 的生成速度，至少和阅读速度一样快，理想情况下允许用户边生成边略读输出文本），且 *time to first token* 不超过 3 秒。根据模型规模、硬件、prompt 长度和并发负载，这两个延迟目标都可能相当难以达成。

其他非交互式用例可能不关心单个请求的延迟，而只关心总 ***token 吞吐***（每秒 token 数，跨所有并发请求求和）。当你想为书籍生成翻译、或总结大型仓库中的代码文件时，这就很重要。

正如后文一节将看到的，最大化总吞吐与最小化单个请求延迟之间通常存在权衡。

#### 资源利用率

由于对所有输入 token 的计算是并行的，prefill 阶段是 GPU 计算密集型的。相反，单个输出 token 的 decode 步骤使用很少算力；这里的速度通常受限于 GPU 显存带宽，即从 GPU 显存加载和访问模型权重与激活（包括 *key* 和 *value* 向量）有多快。

一般而言，token 吞吐可以持续提高，直到 GPU 利用率（按算力计）饱和。在 prefill 阶段，单个长 prompt 请求就可能达到 GPU 利用率上限。在 decode 阶段，可以通过多个请求的**批处理提高 GPU 利用率**。因此，当你把 token 吞吐画成并发请求数的函数时，会看到低并发区吞吐近乎线性增长，因为这种 memory-bound 机制受益于更大的批大小。一旦 GPU 利用率饱和、进入 compute-bound 机制，吞吐就不再随并发增加而变化。

总吞吐随并发增加而上升，直到 GPU 算力饱和。低并发时，吞吐受显存带宽限制。更短的 prompt 意味着 prefill 期间计算利用率更低，因而要在更高的请求速率下才会饱和。（数据为 vLLM 在单块 H100 GPU 上跑 Llama-3.1-8B、输入 3000/1500 token、输出 100 token 测得。）

### 并发处理

接下来我们考察推理引擎确切如何处理短时间内到达的多个请求。

prefill 和 decode 阶段都能利用批处理策略，把同一组操作应用于不同请求。但同时运行不同请求的 prefill 和 decode 会有什么后果？

#### Static Batching 与 Continuous Batching

最朴素的批处理形式叫 **static batching**。(1) 从空批次开始，(2) 用所有等待且能放入批次的条目填满批次，(3) 处理批次直到批内所有条目完成，(4) 用新的空批次重复该流程。

所有请求同时开始 prefill 阶段。由于 prefill 只是一个大规模并行的 GPU 操作（想象成一次非常大的矩阵乘法），所有并发请求的 prefill 阶段同时完成。随后所有 decode 阶段同时开始。输出 token 较少的请求本会更早结束，但由于 static batching，下一个等待的请求只有等批内最长的请求完成后才能开始。

使用 static batching 时，新请求必须等 batch 1 的所有请求结束后，才能被组装进 batch 2 处理。这可能造成大量时间和资源浪费。

**Static batching 优化 *time per output token***，因为 decode 阶段不被打断。缺点是资源利用率非常低。由于单个长 prompt 就能在 prefill 时饱和算力，并行处理多个 prefill 不会带来加速，且必然把 GPU 利用率打满。相反，decode 阶段 GPU 很可能利用不足，因为即便是大量并发 decode，也不如长 prompt 的 prefill 那样计算密集。

然而最大的缺点是可能很长的 *time to first token*。即使某些短请求提前完成，下一个排队请求也必须等批内最长的 decode 结束才能开始自己的 prefill。由于 static batching 这一缺陷，推理引擎通常实现 **continuous batching** 策略：任何完成的请求立即移出批次，批内空间由排队的下一个请求填补。因此，每种 continuous batching 策略都必须处理 prefill 与 decode 阶段的并发问题。

#### Prefill-First

为了减少请求等待时间，vLLM 和 TGI 等推理引擎在新请求到达且能放入当前批次时就调度其 prefill 阶段。新请求的 prefill 可以与每个先前请求各一个 decode 步骤并行运行，但由于一切在同一个 GPU 操作中执行，其时长由 prefill 主导，decode 阶段的每个请求在这段时间内只能生成单个输出 token。因此，这种**prefill 优先最小化 *time to first token***，但会打断已在运行请求的 decode 阶段。在聊天应用中，当其他用户提交长 prompt 时，用户会感到流式 token 生成被暂停。

在接下来的测量中你可以看到带 prefill-first 策略的 continuous batching 的效果。

由于新请求被立即处理，time to first token 被最小化。但在每次 prefill 期间，每个并发请求只能执行单个 decode 步骤，尽管其本身的执行时间本应短得多。因此该策略下 prefill 实际上打断了其他 decode。

#### Chunked Prefill

缓解打断式 prefill 对运行中 decode 影响的一种方法是 *chunked prefill*。不必在单个 prefill 步骤中处理整个 prompt，而是把它分摊到多个 chunk。这样 prefill 期间的并发 decode 步骤数等于 prefill chunk 数（而不是在整个 prefill 期间每个并发请求只有一个 decode 步骤）。一个 chunked prefill 步骤仍比孤立的 decode 步骤耗时长，但对小的 chunk 尺寸，用户现在感受到的是 token 生成变慢而非完全停止；这降低了平均 *time per output token*。从发起打断的请求视角看，chunked prefill 带来一些开销、比孤立的连续 prefill 稍长，所以 *time to first token* 有小幅增加。通过 chunk 尺寸，我们现在有**一个调节 *time to first token* 与 *time per output token* 优先级**的旋钮。典型 chunk 尺寸在 512 到 8192 个 token 之间（chunked prefill 刚实现时 vLLM 默认是 512，后来更新为更大值）。

当 prefill 被切成若干步骤时，其他请求的并发 decode 每处理一个 prefill chunk 就能产出一个输出 token，而不是整个 prefill 阶段只产出一个。虽然我们在客户端测量中无法解析单个 prefill chunk，但其影响可以从并发 decode 的形态看出——它们呈现为一个个孤立的点而非近乎连续的线。

不过该策略最大的优点是 **chunked prefill 最大化资源效率**。Prefill 是计算密集的，而 decode 受显存带宽限制。让两种操作并行运行，可以在不受 GPU 资源限制的情况下提高总吞吐。当然，只有在特定 chunk 尺寸下才能达到最高效率，而该尺寸又取决于具体的负载模式。

在标准 vLLM 部署、请求大小均匀的情况下，我们观察到 **chunked prefill 使总 token 吞吐提高 +50%**。现在 TNG 所有自托管 LLM 的 vLLM 部署都启用了它。总体而言，chunked prefill 是多数用例的好默认策略。然而，在负载模式不可预测的环境（如拥有众多多样应用的 TNG）中优化 chunk 尺寸相当困难；通常保持默认值即可。

无论 chunk 尺寸如何配置，chunked prefill 的并发处理都带来两个挑战，我们将在[下一篇文章](https://huggingface.co/blog/tngtech/llm-performance-blocked-by-long-prompts)中讨论。
