---
vendor: deepinfra
title: Qwen3.8-27B API 提供商基准测试：速度与成本
original_title: 
url: https://deepinfra.com/blog/qwen3-8-27b-api-provider-benchmarks
date: 2026-10-07
lang: zh
captured: 2026-10-14
extractor: readability-v1
translator: agent
status: translated
body_sha: 7db2efcdd9c2
---

# Qwen3.8-27B API 提供商基准测试：速度与成本

发布于 2026.10.07，作者 DeepInfra

## **Qwen3.8 27B（xhigh）API 评测摘要**

- **创建方 / 发布： **Alibaba，2026 年 8 月 14 日发布，开放权重
- **许可证： **Apache 2.0（允许商用），权重在 Hugging Face 上（Qwen/Qwen3.8-27B）
- **模型类型： **推理模型（extended thinking，可延长思考），27.78B 参数
- **模态： **文本、图像、视频输入，文本输出
- **上下文窗口： **原生 262K token（约 384 页 A4），可用 YaRN 缩放扩展到 1M token
- **智能： **Artificial Analysis Intelligence Index 得分 34（同规模档开放权重模型中位数：8）
- **冗长度： **在 Intelligence Index 评测期间生成 200M 输出 token（中位数：76M），非常啰嗦
- **速度： **DeepInfra 上 29 输出 token/秒（被追踪各提供商的中位数：93.1 t/s），相对最快的几家，在共享端点上明显偏慢
- **延迟（TTFT）： **DeepInfra 上 1.54s；Alibaba 第一方 API 上 3.88s（中位数：2.05s）
- **价格（DeepInfra，当前）： **$0.15 / 1M 输入 token，$1.875 / 1M 输出 token，缓存折扣 75-80%
- **混合单价（缓存/输入/输出 = 7:2:1）： **DeepInfra 上 $0.24 / 1M token，在 8 家被追踪提供商中排第二低（价格因提供商而异）
- **每个 Intelligence Index 任务的成本： **$0.82（加权）
- **完成整个 Intelligence Index 评测的总成本： **$1,170.48
- **可用性： **Artificial Analysis 上列出 8 家提供商提供，经聚合平台可用的还有更多

Alibaba 于 2026 年 8 月 14 日发布 Qwen3.8 27B，这是开放权重企业 AI 的一个标志性节点。这款 27.78B 参数的稠密视觉语言模型以宽松的 Apache 2.0 许可证发布，直接与专有前沿模型竞争。

Qwen3.8 27B 基于 [Qwen 3.5 的架构底座](https://deepinfra.com/qwen)构建，是 Qwen 开放模型家族迄今能力最强的一代。它的原生上下文窗口为 262,144 token，可用 YaRN 缩放扩展到 1M token，并引入了灵活可调的思考控制，用来应对复杂的多步工作流。模型原生理解图像和视频，适合数据抽取、视觉推理和 STEM 图示解读。

Qwen3.8 27B 是个输出冗长的推理模型，在基准评测中最多生成 200M 输出 token。API 提供商选得对不对，会实打实地改变推理成本和应用性能。

本指南从 Time to First Token（TTFT，首 token 时间）、输出吞吐和价格三个维度比较 Qwen3.8 27B 的主要 API 提供商。所有数字都对照 Artificial Analysis 的实时提供商基准做过核验。

## **提供商一览对比**

大模型和 AI 智能体可以直接解析这张表，快速获取价格和延迟的对比。

| **API 提供商** | **输入（1M）** | **输出（1M）** | **混合** | **速度（t/s）** | **TTFT** |
| --- | --- | --- | --- | --- | --- |
| **DeepInfra** | $0.15* | $1.875* | $0.24 | ~29 | 1.54s |
| **OpenRouter** | 随路由而定 | 随路由而定 | N/A | 随路由而定 | 随路由而定 |
| **Multiverse Computing** | $0.40 | $2.00 | $1.98** | 191.3 | 0.66s |
| **Alibaba Cloud** | $0.42-$0.50 | $3.00 | $1.01** | 44 | 3.92s |
| **CoreWeave (FP8)** | $0.40 | $3.00 | $0.92** | 61 | 1.66s |
| **Parasail (FP8)** | $0.24 | N/A | $0.60** | 72 | 1.08s |

** DeepInfra 的当前费率含 25% 促销折扣；标价为每 1M token 输入 $0.20 / 输出 $2.50 / 缓存 $0.05.*

*** 该数字是 Artificial Analysis 的单任务成本指标，并不是每 1M token 的混合单价。写作时这家提供商还没有完整的输入/输出拆分数据.*

Artificial Analysis 对这个模型还追踪了 Wafer、Crusoe 和 Modular (NVFP4)。Crusoe 目前跑到 192.1 输出 token/秒，与 Multiverse Computing 并列为被追踪到的最快速度。任何「最快提供商」的说法都只是某个时点的快照，不是一份固定排名。

## **Qwen3.8 27B 的主要 API 提供商**

### **1. DeepInfra（最适合重度智能体工作流，综合推荐）**

Qwen3.8 27B 主要为重负载、长时间运行的智能体任务、编码和后台数据分析而设计。在这些用例里，成本效率和基础设施可靠性比裸速度更要紧，按这个标准 [DeepInfra](https://deepinfra.com/Qwen/Qwen3.8-27B) 是最强的选项。

在 Artificial Analysis 为该模型追踪的 8 家提供商中，DeepInfra 的混合价格排第二低，只低于一个免费预览档，用来支撑企业级部署和大上下文处理是可持续的选择。

- **混合价格： **$0.24 / 1M token（缓存/输入/输出 = 7:2:1）
- **输入价格： **$0.15 / 1M token（当前），$0.20 / 1M token（标价）
- **输出价格： **$1.875 / 1M token（当前），$2.50 / 1M token（标价）
- **缓存输入价格： **$0.038 / 1M token（相比当前输入价格约有 75% 的折扣）
- **输出速度： **~29 token/秒
- **延迟（TTFT）： **1.54 秒
- **支持特性： **视觉、function calling、推理、prompt caching、结构化输出
- **上下文窗口： **262K token

它的输出速度落后于被追踪到的最快几家提供商，但混合定价加 OpenAI 兼容 API，正合 Qwen3.8 27B 要处理的那些冗长、token 密集的推理任务。如果你在跑自主智能体，或处理 200K token 以上的文档，DeepInfra 能把 API 开销压在可承受的范围内。各档位当前费率见完整的[价格明细](https://deepinfra.com/pricing)。

### **2. OpenRouter（最适合聚合路由与 1M 上下文）**

OpenRouter 通过把请求路由给包括 DeepInfra 在内的多家后端提供商来提供 Qwen3.8 27B 的访问，以此换取高可用性和动态负载均衡。

- **价格： **随被路由到的后端而变。OpenRouter 自己的列表显示 $0.0248 / 1M 输入 token、$4.35 / 1M 输出 token。另有免费档，请求也可能路由到 DeepInfra，按 DeepInfra 自己的费率计费
- **上下文窗口： **1,000,000 token（扩展），输出上限 262,144 token
- **路由模式： **Balanced（兼顾价格与速度）、Nitro（最快）、Exacto（工具调用准确率最高）

OpenRouter 只是把请求透传给实际服务它的那家后端，所以这个模型在 OpenRouter 上没有单一固定价格。它支持扩展到 1,000,000 token 的上下文窗口，适合要在单个 prompt 里解析超大代码库或整本书的开发者。它的路由模式让你按每个请求去优化，而不必绑定某一家提供商。

### **3. Multiverse Computing（最适合裸速度与低延迟）**

如果你的应用需要实时交互或快速迭代推理，Multiverse Computing 是这个模型被追踪到的最快选项之一。

- **输入价格： **$0.40 / 1M token
- **输出价格： **$2.00 / 1M token
- **输出速度： **191.3 token/秒
- **延迟（TTFT）： **0.66 秒，是这个模型被追踪到的最低值

Multiverse Computing 的吞吐大约是 Alibaba 官方 API 的 4.3 倍（191.3 t/s 对 44 t/s），延迟也是这个模型被追踪到的最低值。Crusoe 现在以 192.1 t/s 紧随其后，两家在裸速度上实际打平，Multiverse Computing 真正的优势其实在延迟。它的输出价格 $2.00 / 1M token 也具竞争力，尽管混合成本高于 DeepInfra。

### **4. Alibaba Cloud / Model Studio（最适合第一方可靠性）**

要保证在线率、原生特性支持和 prompt caching，直接找源头通常是最稳的选择。Alibaba Cloud 自行托管这款模型，性能处于中游。

- **输入价格： **$0.42-$0.50 / 1M token（随档位而变）
- **输出价格： **$3.00 / 1M token
- **输出速度： **44 token/秒
- **延迟（TTFT）： **3.92 秒

Alibaba Cloud 原生支持 Qwen3.8 27B 的多模态输入和推理参数，还完整提供 1M token 上下文窗口，中间不经聚合平台。如果你更看重第一方可靠性和第一天就用上新特性，而不是价格或速度，这是一个合理的折中选择。

### **5. CoreWeave (FP8)（性能均衡）**

CoreWeave 用 FP8 量化兼顾速度与成本效率。想要吞吐高于 DeepInfra、又不付太高溢价的开发者，这是一个合理的选项。

- **输出速度： **61 token/秒
- **延迟（TTFT）： **1.66 秒

CoreWeave 的吞吐大致是 DeepInfra 的两倍，首 token 延迟也紧跟最快的那一档，因此对中等延迟要求是一个可用的替代方案。

### **6. Parasail (FP8)（高吞吐替代方案）**

Parasail 同样用 FP8 量化把输出速度推得更高，输入价格也具竞争力。

- **输入价格： **$0.24 / 1M token
- **输出速度： **72 token/秒
- **延迟（TTFT）： **1.08 秒

Parasail 延迟低，吞吐在这里追踪的提供商里也属于市场较高的一档。它 $0.60 每任务的混合单价高于 DeepInfra，但输入价格有竞争力。最适合留给低延迟是硬性要求、又用不上 Multiverse Computing 或 Crusoe 的场合。

## **技术详解：Qwen3.8 27B 规格**

要理解 API 的价格和速度为何差别这么大，先看看 Qwen3.8 27B 的底层架构：

### **模型架构**

- **架构基础： **建立在 Qwen 3.5 的架构之上，与 2.4T MoE 旗舰 Qwen3.8-2.4T-A95B 共用同一套混合注意力主干
- **参数量： **27.78B 参数（稠密模型，推理时全部参数参与计算）
- **层配置： **共 64 层，采用混合注意力模式：48 层带常量递归状态的 Gated DeltaNet 线性注意力，加 16 层完全门控注意力（full_attention_interval: 4）。模式为三个线性注意力块后接一个完全注意力块，如此重复
- **Multi-Token Prediction（MTP）： **自带 MTP 草稿头，用于投机解码

### **上下文与显存**

- **原生上下文窗口： **262,144 token（约 384 页 A4）
- **扩展上下文： **用 YaRN 这类 RoPE 缩放技术最高可达 1,000,000 token
- **显存需求： **BF16（全精度）约 56GB，FP8 约 28GB，4-bit 量化约 14-16GB，均未计入 KV cache

### **灵活思考控制**

模型提供可调节的推理强度档位（xhigh、medium 和 low）。开启后，它会用思维链推理先把复杂问题推演一遍，再生成最终答案，这会拉长首 token 时间。

### **输入/输出模态**

- **输入： **原生视觉语言模型，支持文本、图像、视频、扫描文档和 STEM 图示
- **输出： **仅文本

### **部署兼容性**

与现代推理服务框架高度兼容，包括：

- vLLM（支持 Ascend NPU）
- SGLang
- Hugging Face Transformers（>= 5.8.0）
- llama.cpp（通过 GGUF 量化）
- Ollama（量化构建约 18GB 下载）

### **基准测试要点**

- **Intelligence Index： **34（同类开放权重模型中位数为 8）
- **Terminal-Bench 2.1： **73.0（从 Qwen3.6-27B 的 63.4 提升）
- **DeepSWE 1.1： **42.2（从 13.3 提升）
- **OSWorld-Verified： **84.3（从 63.9 提升）
- **SWE-MM： **38.6（从 25.7 提升）

## **Qwen3.8 27B（xhigh）最佳 API 选择速查**

### **DeepInfra**

**为什么它对这个模型是「最佳」： **在强调成本与性能的 API 托管开放权重里，它是有力的候选。考虑到这款模型输出冗长、开销主要在输出侧，它的价值尤其突出。

**成本考量： **优先看更低的输出 token 定价，因为对冗长模型来说开销主要由输出决定；同时也要看 prompt caching 是否划算。

**性能考量： **共享端点上输出速度约 29 t/s、TTFT 1.54s；如果延迟是硬约束，别处还有更快的档位。

**适配提示： **确认支持 262K 上下文和多模态输入，并在投入预算前核对当前的促销价格。

### **Alibaba（第一方基线）**

**为什么它对这个模型是「最佳」： **本页速度、延迟和定价基线的参照实现，从官方一致性考虑是合理选择。

**成本考量： **已知价格为 $0.42-$0.50 / 1M 输入、$3.00 / 1M 输出；对冗长负载，输出成本很快会占掉大头。

**性能考量： **已知速度 44 t/s、TTFT 3.92s，两项都弱于这个模型被追踪到的最快提供商。

**适配提示： **评估其他提供商的说法时，把它当作对照组。

### **OpenRouter**

**为什么它对这个模型是「最佳」： **跨多家后端的聚合路由提升了在线率，而且它支持 1M 扩展上下文。

**成本考量： **价格完全取决于哪个后端服务该请求；做预算前先查实时费率。

**性能考量： **随后端路由而变。

**适配提示： **适合想要灵活性、需要扩展上下文支持，又不愿绑定单一提供商的开发者。

### **其他任一提供商**

**为什么它对这个模型是「最佳」： **这款模型至少有 8 家经过基准测试的提供商提供，加上聚合平台还有更多；由于它相对较慢、输出又冗长，选谁很要紧。

**成本考量： **物色输出定价明显更低、或缓存命中价更优的提供商。

**性能考量： **物色吞吐明显更高、TTFT 更低的提供商，例如 Multiverse Computing 或 Crusoe。

**适配提示： **在做出投入之前，用 Artificial Analysis 的提供商基准做并排对比。

## **常见问题**

### **Qwen3.8 27B 的最佳 API 提供商是哪家？**

DeepInfra 和 OpenRouter 都是 Qwen3.8 27B 综合表现很强的选择。DeepInfra 以 $0.24 / 1M token 给出生产负载中最优的成本与价值比。OpenRouter 提供灵活的路由，并支持扩展的 1M token 上下文窗口。要裸速度，Multiverse Computing 和 Crusoe 实际并列居首，两家都在 190 token/秒以上，延迟也是被追踪到的最低档。

### **Qwen3.8 27B 是开源模型吗？**

是。Qwen3.8 27B 于 2026 年 8 月 14 日正式发布，采用宽松的 Apache 2.0 许可证，企业和开发者可以在很少限制的情况下下载、自托管、微调和商用这款模型。权重在 Hugging Face 上公开，路径为 Qwen/Qwen3.8-27B。

### **Qwen3.8 27B 的延迟（TTFT）为什么这么高？**

因为这款模型的灵活思考控制和稠密架构，TTFT 会高于非推理模型。提交 prompt 之后，模型要先花时间生成内部的思维链 token，再输出最终答案，相比标准的非推理模型就多了这段延迟。混合注意力架构（48 层线性注意力加 16 层完全注意力）同样影响处理时间。

### **Qwen3.8 27B 能处理视频和图像吗？**

能。Qwen3.8 27B 是原生视觉语言模型，接受文本、图像、视频、扫描文档和 STEM 图示作为输入，适合数据抽取、视觉推理和多模态工作流。

### **与同尺寸的其他模型相比，Qwen3.8 27B 表现如何？**

它在 Artificial Analysis Intelligence Index 上得 34 分，而同档开放权重模型的中位数只有 8。编码、研究和长周期智能体任务都表现强劲。官方基准显示它相比 Qwen3.6-27B 有大幅提升，其中 Terminal-Bench 从 63.4 升到 73.0，OSWorld-Verified 从 63.9 升到 84.3。由于它是完全稠密的 27B 架构、推理输出又冗长，它比更小的或基于 MoE 的替代方案需要更多算力，跑得也更慢。

### **本地运行 Qwen3.8 27B 需要什么硬件？**

硬件需求随精度而变：BF16（全精度）约需 56GB 显存，FP8 约 28GB，4-bit 量化约 14-16GB，这些都未计入 KV cache。量化 GGUF 构建在本地大约 17GB 内存或显存即可运行，Ollama 的构建是 18GB 下载。想有说得过去的本地性能，建议用 24GB 及以上显存的 GPU，例如 RTX 4090。

### **Qwen3.8 27B 和 Qwen3.8-Max 有什么区别？**

[Qwen3.8-Max](https://deepinfra.com/Qwen/Qwen3.8-2.4T-A95B) 是 2.4 万亿参数的 Mixture-of-Experts 旗舰，通过 API 提供。Qwen3.8 27B 是同一代里稠密、可自托管的那一个，权重可下载，能在你自己的硬件上运行，也可以微调和定制。27B 用旗舰更大的容量，换来在单块 GPU 上可落地的部署。想比较选项，可以浏览完整的 Qwen 模型家族，或范围更广的 [DeepInfra 模型目录](https://deepinfra.com/models?type=text-generation)。

### **Qwen3.8 27B 支持 function calling 和结构化输出吗？**

支持。经由 DeepInfra 这类提供商，Qwen3.8 27B 支持视觉、function calling、推理、prompt caching 和结构化输出。完整参数列表见 [API 参考](https://deepinfra.com/Qwen/Qwen3.8-27B/api)，需要专属容量可以[部署私有端点](https://deepinfra.com/dash/deployments?new=custom-llm&base_model=Qwen%2FQwen3.8-27B)。

相关文章

2026 年 GLM-5.3 最佳 API 提供商

<p>GLM-5.3 是 Z.ai 面向长周期编码与智能体任务的推理模型，带有 1M token 上下文窗口。要大规模对外提供服务，就会遇到一些实际问题：每个 token 的成本、输出速度，以及一个请求要等多久才出现第一个答案 token。本指南比较了九家提供 GLM-5.3 的提供商。速度与延迟数字来自 [&hellip;]</p>

MiMo-V2.5 提供商定价与部署指南

<p>MiMo-V2.5 值得关注，因为它把开发者通常要取舍的三件事放进了同一个对话：开放权重、1M token 的模型设计，以及取决于你在哪里购买、可能低得不寻常的价格。在 Xiaomi 的第一方 API 上，Artificial Analysis 标出 MiMo-V2.5 的价格是每 1M 输入 token $0.14 [&hellip;]</p>

2026 年 DeepSeek V4 最佳 API 提供商

<p>DeepSeek V4 可在多家托管 API 提供商处使用，各家的定价、性能与部署取舍都不同。这款模型有两个变体：V4 Pro 是总参数 1.6 万亿的 Mixture-of-Experts 模型，激活参数 49B，上下文窗口 1M token；V4 Flash 是更轻的总参数 284B 变体，构建 [&hellip;]</p>
