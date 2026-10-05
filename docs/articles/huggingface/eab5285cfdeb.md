---
vendor: huggingface
title: LFM2.5-DSpark：推理最快提速 3.2 倍
original_title: Up to 3.2x Faster Inference with LFM2.5-DSpark
url: https://huggingface.co/blog/LiquidAI/lfm25-dspark
date: 2026-08-20
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

今天，我们为 LFM2.5 家族的三个模型发布 **DSpark 草稿模型（draft model）checkpoints**：LFM2.5-1.2B-Instruct、LFM2.5-2.6B 和 LFM2.5-8B-A1B。它们新增了一条 speculative decoding（投机解码）路径，用极小的内存增加换取大幅的解码加速，且不改变输出质量：

- **推理更快**：在 GPU 上吞吐最高提升 3.18 倍，在设备端最高 2.87 倍。
- **迈向设备端 agentic 推理**：LFM2.5-2.6B 的 function-calling 延迟平均降低 57%。
- **llama.cpp 与 SGLang 首日支持**：兼容 LFM 的 DSpark 集成已在上游开源。

## DSpark 如何工作

LLM 推理中的 decode 阶段传统上是内存受限的。大部分延迟来自把权重从 DRAM 流式读入 SRAM，而不是密集计算。投机解码通过以下方式应对：用一个轻量草稿模型产出候选 token，然后让目标模型在单次前向传播中全部验证，把加载权重的成本摊到所有被验证的 token 上。

多年来人们提出过多种投机方案，最著名的是 [EAGLE-3](https://huggingface.co/papers/2503.01840)、[DFlash](https://huggingface.co/papers/2602.06036)，以及最近的 [DSpark](https://huggingface.co/papers/2607.05147)。DSpark 结合了三个组件：

- **DFlash 风格的并行主干**，以目标模型的上下文特征为条件，在一次前向传播中产出所有草稿 token 的 hidden states。
- **一个轻量级顺序头**，建模为相邻 token 之间的马尔可夫链，加入 token 间依赖，提高靠后位置的接受率。
- **一个置信度调度的验证器**，预测每个 token 的存活概率，并在验证的开销超过收益时剪掉低置信度的后缀。

[![DSpark](https://cdn-uploads.huggingface.co/production/uploads/644249b08443bce4c9890a0f/QSig7XupRwDH70cDopwv2.png)](https://cdn-uploads.huggingface.co/production/uploads/644249b08443bce4c9890a0f/QSig7XupRwDH70cDopwv2.png)

## 训练与架构

我们遵循 DSpark 配方，用了更大、更多样的数据配比，覆盖 SFT、聊天、代码和 function-calling 数据。基于我们的 ablation，草稿模型的初版是简化的纯注意力草稿模型，5 层、block 为 9。每个草稿模型在整个数据集上跑 15 个 epoch，选择接受率最高的 epoch，而不是 loss 最低的。

得到的草稿模型相对小巧，每个约 3 亿参数。

| 组件 | LFM2.5-1.2B-Instruct | LFM2.5-8B-A1B | LFM2.5-2.6B |
| --- | --- | --- | --- |
| Decoder stack (5 layers) | 241.2M | 241.2M | 241.2M |
| Hidden-state projection | 21.0M | 21.0M | 21.0M |
| Markov head | 33.6M | 65.5M | 65.5M |
| Norms + confidence head | 27.5k | 27.5k | 27.5k |
| **合计** | **295.7M** | **327.7M** | **327.7M** |

## 质量持平

在贪心解码下，草稿 token 只有匹配目标模型的分布才会被接受。一旦被拒绝，目标模型自己的 token 就取而代之。因此产出的序列**与基线贪心解码在构造上完全一致**，基准准确率（pass@1 或 exact match）不变。

## CPU 与 GPU 上的推理加速

我们为 LFM2.5 的 DSpark 草稿模型在首日即支持 **llama.cpp**（实现[构建在官方代码库之上](https://github.com/ggml-org/llama.cpp/pull/27383)，我们配合[实验性 metal kernels](https://github.com/ggml-org/llama.cpp/pull/27441)运行）和 **SGLang**（实现[基于 DSpark 的官方 SGLang 实现](https://github.com/sgl-project/sglang/pull/31041)）。

设备端吞吐用 llama.cpp 加 Metal 在 M4 Max MacBook Pro 上测量，使用 FP16 GGUF 权重、最多 256 个输出 token。GPU 吞吐用 SGLang 在单块 H100 80GB、BF16 下测量。两种配置都用 DSpark block size 9、batch size 1、temperature 0。我们在五个基准数据集上评估。

三个草稿模型在大规模加速器（H100）与边缘部署（M4 Max MacBook）上都带来了明显的吞吐提升。

对 **LFM2.5-2.6B**，MacBook 上的加速尤其显著：它把用户可享有的交互流畅度推得远高于多数专有云模型提供的吞吐（约 140 tok/s，视数据集而定）。

| 数据集 | Acceptance (of 10) | H100 加速 | M4 Max 加速 |
| --- | --- | --- | --- |
| MATH500 | 5.42 | **3.06x** 326 → 1000 tok/s | **2.25x** 61 → 137 tok/s |
| HumanEval | 4.54 | **2.56x** 326 → 835 tok/s | **2.63x** 61 → 161 tok/s |
| MBPP | 4.71 | **2.64x** 326 → 861 tok/s | **2.11x** 62 → 132 tok/s |
| GSM8K | 4.32 | **2.22x** 312 → 693 tok/s | **2.36x** 60 → 143 tok/s |
| MT-Bench | 5.07 | **2.87x** 325 → 933 tok/s | **1.99x** 62 → 123 tok/s |
| 平均 | 4.81 | **2.67x** 323 → 864 tok/s | **2.27x** 61 → 139 tok/s |

在各种多工具场景中，DSpark 把 LFM2.5-2.6B 的延迟平均降低了 57%。

[![bfcl_latency_mac](https://cdn-uploads.huggingface.co/production/uploads/644249b08443bce4c9890a0f/RTL-W6OBn97nMW7gkkT-e.png)](https://cdn-uploads.huggingface.co/production/uploads/644249b08443bce4c9890a0f/RTL-W6OBn97nMW7gkkT-e.png)

对 **LFM2.5-1.2B-Instruct**，各数据集的接受率差异大得多，加速随底层文本分布的不同最多相差 52%。

| 数据集 | Acceptance (of 10) | H100 加速 | M4 Max 加速 |
| --- | --- | --- | --- |
| MATH500 | 6.02 | **2.56x** 668 → 1712 tok/s | **2.62x** 140 → 366 tok/s |
| HumanEval | 5.31 | **2.26x** 664 → 1499 tok/s | **2.87x** 136 → 389 tok/s |
| MBPP | 5.52 | **2.37x** 667 → 1578 tok/s | **2.74x** 137 → 375 tok/s |
| GSM8K | 4.34 | **1.67x** 624 → 1041 tok/s | **2.73x** 140 → 381 tok/s |
| MT-Bench | 3.90 | **1.66x** 657 → 1091 tok/s | **1.72x** 137 → 237 tok/s |
| 平均 | 5.02 | **2.10x** 656 → 1384 tok/s | **2.54x** 138 → 350 tok/s |

对 **LFM2.5-8B-A1B**，接受率相比两个稠密模型有所提高，但设备端平均只提升 18%。这一差距源于 llama.cpp Metal 后端当前的 MoE 实现，也源于验证 k 个 token 会激活更多专家、带来比单个 decode 步更多的权重搬运这一事实。

| 数据集 | Acceptance (of 10) | H100 加速 | M4 Max 加速 |
| --- | --- | --- | --- |
| MATH500 | 8.27 | **3.18x** 428 → 1362 tok/s | **1.21x** 93 → 112 tok/s |
| HumanEval | 7.02 | **2.58x** 426 → 1100 tok/s | **1.12x** 91 → 101 tok/s |
| MBPP | 6.93 | **2.64x** 426 → 1122 tok/s | **1.09x** 89 → 97 tok/s |
| GSM8K | 4.02 | **1.29x** 385 → 496 tok/s | **1.44x** 90 → 129 tok/s |
| MT-Bench | 8.52 | **3.02x** 426 → 1288 tok/s | **1.04x** 87 → 90 tok/s |
| 平均 | 6.95 | **2.54x** 418 → 1074 tok/s | **1.18x** 90 → 106 tok/s |

## 如何使用 LFM2.5-DSpark

用 **SGLang** 运行 DSpark 草稿模型需要一个对 LFM2 目标支持 DSpark 的 SGLang 构建（[PR #31041](https://github.com/sgl-project/sglang/pull/31041)）。启动目标模型并挂上草稿模型：

```
python -m sglang.launch_server \
  --model-path LiquidAI/LFM2.5-2.6B \
  --speculative-algorithm DSPARK \
  --speculative-draft-model-path LiquidAI/LFM2.5-2.6B-DSpark \
  --speculative-draft-attention-backend flashinfer \
  --disable-radix-cache --mem-fraction-static 0.75 --port 30000
```

然后查询 `http://localhost:30000/v1` 的 OpenAI 兼容端点。block size 从草稿模型的 `config.json` 读取；基线是同一条去掉三个 `--speculative-*` 标志的命令。

用 **llama.cpp** 运行则需要对应的 llama.cpp 构建（[PR#27383](https://github.com/ggml-org/llama.cpp/pull/27383)）。

```
llama-server -m LFM2.5-2.6B-F16.gguf \
  -md LFM2.5-2.6B-DSpark-F16.gguf \
  --spec-type draft-dspark --spec-draft-n-max 10 --spec-draft-n-min 0 \
  -fa on -ngl 99
```

block size 从 sidecar 元数据读取（n-max 会被夹到它）。投机解码是**精确的**：目标模型验证每个提议的 token，所以贪心输出与单独用目标模型一致；每条响应的 `timings` 会报告 `draft_n` / `draft_n_accepted`。

## 开始使用

DSpark 草稿模型 checkpoints 已在 Hugging Face 上以 Safetensors 和 GGUF 两种格式提供：

- **Safetensors**：[LFM2.5-2.6B-DSpark](https://huggingface.co/LiquidAI/LFM2.5-2.6B-DSpark)、[LFM2.5-1.2B-Instruct-DSpark](https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-DSpark) 和 [LFM2.5-8B-A1B-DSpark](https://huggingface.co/LiquidAI/LFM2.5-8B-A1B-DSpark)
- **GGUF**：[LFM2.5-2.6B-DSpark-GGUF](https://huggingface.co/LiquidAI/LFM2.5-2.6B-DSpark-GGUF)、[LFM2.5-1.2B-Instruct-DSpark-GGUF](https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-DSpark-GGUF)、[LFM2.5-8B-A1B-DSpark-GGUF](https://huggingface.co/LiquidAI/LFM2.5-8B-A1B-DSpark-GGUF)

我们迫不及待想看到你的创造。

## 引用

引用请使用以下参考文献或 BibTeX：

Liquid AI, "LFM2.5-DSpark: Up to 3.2x Faster Inference from H100 to MacBook", Liquid AI Blog, Aug 2026.

```
@article{liquidAI2026dspark,
  author = {Liquid AI},
  title = {LFM2.5-DSpark: Up to 3.2x Faster Inference from H100 to MacBook},
  journal = {Liquid AI Blog},
  year = {2026},
  note = {www.liquid.ai/blog/lfm2.5-dspark},
}
```
