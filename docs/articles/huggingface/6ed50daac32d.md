---
vendor: huggingface
title: OpenAI gpt-oss 的技巧：你 🫵 可以在 transformers 中使用
original_title: Tricks from OpenAI gpt-oss YOU 🫵 can use with transformers
url: https://huggingface.co/blog/faster-transformers
date: 2026-09-01
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: 7482cc908060
---

# OpenAI gpt-oss 的技巧：你 🫵 可以在 transformers 中使用

OpenAI 最近发布了 [GPT-OSS 系列模型](https://huggingface.co/collections/openai/gpt-oss-68911959590a1634ba11c7a4)。这批模型带来了一些新颖技术，例如 MXFP4 量化、高效 kernel、全新的聊天格式等等。为了让 gpt-oss 能通过 `transformers` 发布，我们对[这个库](https://github.com/huggingface/transformers/)做了大幅升级。这些更新让模型的**加载**、**运行**和**微调**都变得非常高效。

在这篇博文中，我们将深入讨论所有升级内容，以及它们如何成为 transformers 工具箱的一部分，让其他模型（现有的和未来的）也能从中受益。在 transformers 中提供新方法的清晰实现，也让社区能够快速理解和采用它们。[`MLX`](https://github.com/ml-explore/mlx-lm/pull/354)、[`llama.cpp`](https://github.com/ggml-org/llama.cpp/discussions/15396) 或 [`vLLM`](https://docs.vllm.ai/projects/recipes/en/latest/OpenAI/GPT-OSS.html) 等框架都可以把 transformers 代码作为参考，构建各自的实现。

这次发布，我们做了以下工作：

- [免编译 Kernel，可从 Hub 下载](https://huggingface.co/blog/faster-transformers#zero-build-kernels-downloadable-from-the-hub)
- [MXFP4 量化](https://huggingface.co/blog/faster-transformers#mxfp4-quantization)
- [张量并行](https://huggingface.co/blog/faster-transformers#tensor-parallelism)
- [专家并行](https://huggingface.co/blog/faster-transformers#expert-parallelism)
- [动态滑动窗口层与缓存](https://huggingface.co/blog/faster-transformers#dynamic-sliding-window-layer--cache)
- [连续批处理与分页注意力](https://huggingface.co/blog/faster-transformers#continuous-batching--paged-attention)
- [更快地加载更大的模型](https://huggingface.co/blog/faster-transformers#load-larger-models-faster)

> 最棒的是：这些功能中的大多数应该能跨 transformers 里所有主流模型使用！

## 免编译 Kernel，可从 Hub 下载

Kernel（算子内核）是在加速器上运行的***专用***小型程序，用于执行矩阵乘法、激活函数或归一化等任务。在 eager 模式的 PyTorch 中，各操作会依次触发独立的 kernel，这种做法简单直白，但会带来额外的内存搬运和启动开销。PyTorch 2.0 的 `torch.compile` 配合 `TorchInductor` 等后端通过自动融合与优化 kernel 来解决这个问题，可以带来 `2–10×` 的性能提升。

除此之外，社区还为常见的操作组合编写了自定义 kernel，*而不只是 matmul 这类单个 PyTorch 算子*。例如，Flash Attention 就是为优化定义 transformer 架构的关键注意力模块而创造的，许多模型（包括绝大多数 LLM）都用到了它。通过在一个 kernel 内精心合并所有注意力操作，内存搬运被降到最少、内存占用降低，还能获得加速。

问题在于，这些五花八门的 kernel 分散在各种独立库里，如果把它们全部加进 transformers 库，就会造成依赖膨胀。而且这些 kernel 不只是 Python 代码——它们由底层 CUDA 代码组成，用 C++ 粘合，再通过 Python 层暴露。这意味着它们必须在目标系统上编译，进而需要每个 kernel 库各自要求的构建系统。

[kernels 包](https://huggingface.co/blog/hello-hf-kernels)通过从 Hub 下载受支持 kernel 的预编译二进制文件解决了这个问题。你只需指明想用的 kernel，`kernels` 就会寻找与你系统兼容的版本并在首次使用时下载。

### GPT-OSS 的自定义 Kernel

[GPT-OSS](https://github.com/huggingface/transformers/blob/0f1b128d3359a26bd18be99c26d7f04fb3cba914/src/transformers/models/gpt_oss/modeling_gpt_oss.py) 是一个混合专家（MoE）模型，也是 Hub kernel 的大用户。它用到了多个自定义 kernel：

- Liger RMSNorm，通过 [`@use_kernel_forward_from_hub("RMSNorm")`](https://github.com/huggingface/transformers/blob/0f1b128d3359a26bd18be99c26d7f04fb3cba914/src/transformers/models/gpt_oss/modeling_gpt_oss.py#L46) 使用
- Megablocks MoE kernels：[`@use_kernel_forward_from_hub("MegaBlocksMoeMLP")`](https://github.com/huggingface/transformers/blob/0f1b128d3359a26bd18be99c26d7f04fb3cba914/src/transformers/models/gpt_oss/modular_gpt_oss.py#L160)
- Flash Attention 3，[支持 attention sinks](https://huggingface.co/kernels-community/vllm-flash-attn3)
- MXFP4 triton kernels（[后文](https://huggingface.co/blog/faster-transformers#mxfp4-in-transformers)详述）

来看看前两个。

在幕后，这两个装饰器只是指向社区贡献的 kernel。例如，`RMSNorm` 来自 [`liger_kernels`](https://huggingface.co/kernels-community/liger_kernels)，而 `MegaBlocksMoeMLP` kernel 来自 [`megablocks`](https://huggingface.co/kernels-community/megablocks)。根据你的设备（CUDA 或 ROCm）以及你在训练还是推理，正确的 kernel 会被自动引入。

这个设计既**具体又通用**：RMSNorm 的 liger kernels 已经在多个模型中被复用，而 MoE kernel 同样可以应用于未来的 MoE 模型。

由于 `kernels` 从 Hub 拉取代码，你必须显式启用这一功能——在模型实例化时传入 `use_kernels=True`，如下所示。我们在示例中开启了 `INFO` 日志，方便你验证可下载 kernel 确实生效了。

> 这些 kernel 与 mxfp4 不兼容，因此如果你使用它们，推理会以 bfloat16 进行。请针对你的项目基准测试内存与吞吐的最佳组合！

```
from transformers import AutoTokenizer, AutoModelForCausalLM

import logging
logging.basicConfig(level=logging.INFO)

model_id = "openai/gpt-oss-20b"
tokenizer = AutoTokenizer.from_pretrained(model_id)

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    dtype="auto",
    device_map="auto",
    use_kernels=True,
)
```

跑一次快速生成，就能看到类似这样的日志：

```
INFO:root:Using layer `LigerRMSNorm` from repo `kernels-community/liger_kernels`
INFO:root:Using layer `MegaBlocksMoeMLP` from repo `kernels-community/megablocks`
```

**图 1** 显示，在我们测试的系统上，这些 kernel 在较大批大小下效果最好。我们始终建议：任何与性能相关的改动，都要尽可能贴近你的生产条件做基准测试。

| [![benchmark with and without kernels](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/faster-transformers/benchmark-kernels-with-without.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/faster-transformers/benchmark-kernels-with-without.png) |
| --- |
| 图 1：自定义 kernel 的基准测试结果 |

> 你可以在这里探索和把玩基准测试脚本

### Flash Attention 3

OpenAI gpt-oss 模型使用了 *attention sinks*（注意力汇聚点），这能提升质量并便于使用更长的上下文。vLLM 团队把这个特性加进了最新版本的 Flash Attention（Flash Attention 3），生成的自定义 kernel 已[发布在 Hub 上](https://huggingface.co/kernels-community/vllm-flash-attn3)。目前该 kernel 兼容 Hopper 架构。如果你有 Hopper 显卡，启用方式如下：

```
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    dtype="auto",
    device_map="auto",
+    # Flash Attention with Sinks
+    attn_implementation="kernels-community/vllm-flash-attn3",
)
```

## MXFP4 量化

大语言模型非常吃内存。量化通过以更低精度格式存储权重（有时也包括激活值）来减小内存占用。作为参照，`FP32` 每个数占 32 位，`BF16` 占 16 位。降低位宽，就是用一部分精度换取更小的模型和更快的内存搬运。

想要量化取舍的直观图解，[Maarten Grootendorst](https://huggingface.co/MaartenGr) 的文章 [*A Visual Guide to Quantization*](https://newsletter.maartengrootendorst.com/p/a-visual-guide-to-quantization) 非常出色。

### 什么是 MXFP4

| [![explanation of mxfp4 format](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/faster-transformers/mxfp4.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/faster-transformers/mxfp4.png) |
| --- |
| 图 2：MXFP4 格式所用的 E2M1 格式 |

`MXFP4` 是一种 4 位浮点格式，采用 E2M1 布局：1 个符号位、2 个指数位、1 个尾数位，如 **图 2** 所示。单看 E2M1 非常粗糙，MXFP4 用**分块缩放（blockwise scaling）**来补救：

- 向量按每 32 个元素分为一块。
- 每块存储一个共享的缩放因子，在反量化时恢复动态范围。
- 块内的 4 位数值表示相对于该缩放因子的数。

这种分块方案让 `MXFP4` 能用极少的位数同时保住取值范围。实际效果是：启用 `MXFP4` 后，GPT-OSS 20B 大约只占 `16 GB` 显存，GPT-OSS 120B 大约 `80 GB`——这正是"加载不了"和"单卡能跑"的区别。代价是矩阵乘法现在必须考虑各块的缩放因子。要大规模高效地做到这一点，需要专门的 kernel。

### `transformers` 中的 MXFP4

`transformers` 现已原生支持 MXFP4，并利用优化过的 `triton`（MXFP4）kernel 提升性能。这建立在[前文讨论过的](https://huggingface.co/blog/faster-transformers#zero-build-kernels-downloadable-from-the-hub)社区驱动 kernel 分发机制之上，使用 Hub 上的预编译 kernel 简化部署。

关键实现细节：

- 量化器逻辑：位于 [MXFP4 quantizer 文件](https://github.com/huggingface/transformers/blob/0997c2f2ab08c32c8e2f90aaad06e29a7108535b/src/transformers/quantizers/quantizer_mxfp4.py)，负责 MXFP4 的核心量化流程。
- 集成钩子：[MXFP4 integration 文件](https://github.com/huggingface/transformers/blob/0997c2f2ab08c32c8e2f90aaad06e29a7108535b/src/transformers/integrations/mxfp4.py)让 MXFP4 能在 transformers 框架内无缝使用。

要检查某个模型是否支持 `MXFP4`，可以查看它的配置：

```
from transformers import GptOssConfig

model_id = "openai/gpt-oss-120b"
cfg = GptOssConfig.from_pretrained(model_id)
print(cfg.quantization_config)

# Example output:
# {
#   'modules_to_not_convert': [
#     'model.layers.*.self_attn',
#     'model.layers.*.mlp.router',
#     'model.embed_tokens',
#     'lm_head'
#   ],
#   'quant_method': 'mxfp4'
# }
```

如果输出中有 `'quant_method': 'mxfp4'`，那么只要条件支持，模型就会自动走 MXFP4 + Triton kernel 的路径。

> 得益于这个 pull request，你可以微调 gpt-oss 模型并以 MXFP4 格式直接保存到 Hub，让部署更顺畅、性能更优。

### 依赖要求与回退机制

要在 GPU 上运行 `MXFP4`，你需要：

- 安装 `accelerate`、`kernels` 和 `triton>=3.4`。注意 `PyTorch 2.8` 已自带 `triton 3.4`，因此只有使用 `PyTorch 2.7` 时才需要手动安装 triton。
- 计算能力 `≥ 7.5` 的 NVIDIA GPU。这可以一路回溯到 Tesla 架构，所以你可以在 Google Colab 和 Kaggle 的免费额度上跑 `gpt-oss-20b`，也能在很多消费级显卡上跑。

如果不满足这些约束，`transformers` 会回退到更高精度的路径（默认使用 `bfloat16`），其显存需求约为 MXFP4 的 4 倍。

这段[代码](https://huggingface.co/datasets/ariG23498/faster-transformers-scripts/blob/main/memory-requirements-quantized-vs-dequantized.py)在 CUDA 上把 GPT-OSS 加载了两次：一次用 `Mxfp4Config(dequantize=True)`（吃内存），一次走默认的量化路径（省内存）。**图 3** 展示了每次加载后的已用显存量，让你直观看到节省了多少。

| [![memory used with quantized vs dequantized models](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/faster-transformers/quantization.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/faster-transformers/quantization.png) |
| --- |
| 图 3：量化与非量化模型的内存需求 |

### MXFP4 的 Kernel

高效的 `MXFP4` 需要能在 GEMM 和融合算子中理解 32 元素块及其缩放因子的 kernel。这正是 **Hub 上的 Kernels** 再次派上用场的地方。当你加载需要 MXFP4 的模型时，`transformers` 会自动从社区仓库引入 `MXFP4` 感知的 Triton kernel。该仓库会出现在你的本地缓存中，并在前向传播时使用。对于 `MXFP4` kernels，不再需要像之前那样传 `use_kernels=True` 参数——它在 `transformers` 中默认启用。

在兼容 triton MXFP4 kernel 的 GPU 上运行 `gpt-oss-20b` 之后，用 Hugging Face 缓存 CLI 快速验证一下：

```
hf cache scan
```

示例输出：

```
REPO ID                          REPO TYPE SIZE ON DISK
-------------------------------- --------- ------------
kernels-community/triton_kernels model           536.2K
openai/gpt-oss-20b               model            13.8G
```

这说明 MXFP4 kernels 已被拉取并可供执行。

来跑些基准测试，看看 MXFP4 kernel 表现如何。在 **图 4** 中可以看到，对更大的批大小，`MXFP4` kernels 甚至比自定义的 MoE 和 RMSNorm kernels 更好。

| [![benchmark mxfp4 kernels](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/faster-transformers/benchmark-mxfp4.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/faster-transformers/benchmark-mxfp4.png) |
| --- |
| 图 4：MXFP4 kernel 基准测试 |

> 你可以在这里探索和把玩基准测试脚本

## 张量并行

| [![explaining tensor parallelism](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/tgi/TP.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/tgi/TP.png) |
| --- |
| 图 5：张量并行的解释。 |

张量并行（Tensor Parallelism，TP）把**层内部的张量**切分到多块 GPU 上（如 **图 5** 所示）。每块 GPU 并行地对自己的分片做乘法，然后用 all-gather 或 all-reduce 操作收集部分结果。这降低了单卡显存占用，并让所有 GPU 始终在**同一层**上工作，因此序列更长或批更大时吞吐更好。TP 通信密集，通常在**单机、节点内高速互联**的场景下效果最佳。

### 这在 `transformers` 中能做什么

`transformers` 直接在 `from_pretrained` 中实现了 TP。你可以从预设计划开始：

```
# run with: torchrun --nproc-per-node 4 tp_gpt_oss.py
import torch
from transformers import PreTrainedTokenizerFast, GptOssForCausalLM

model_id = "openai/gpt-oss-120b"
tokenizer = PreTrainedTokenizerFast.from_pretrained(model_id)
model = GptOssForCausalLM.from_pretrained(
    model_id,
    tp_plan="auto", # built in TP support
    dtype="auto",
).eval()

messages = [
    {"role": "system", "content": "Be concise."},
    {"role": "user", "content": "Explain KV caching briefly."},
]
inputs = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    return_tensors="pt",
    return_dict=True,
    reasoning_effort="low",
).to(model.device)

with torch.inference_mode():
    generations = model.generate(**inputs, max_new_tokens=128)

print(tokenizer.decode(generations[0][inputs["input_ids"].shape[-1]:]))
```

如果你没有基础设施跑上面的代码，可以直接用 [Hugging Face Jobs](https://huggingface.co/docs/huggingface_hub/en/guides/jobs) 在我们的 GPU 上起一个进程！

```
hf jobs run --detach --flavor l4x4 ghcr.io/astral-sh/uv:debian /bin/bash -c \
  "uv venv .venv --python 3.12 && \
  source .venv/bin/activate && \
  uv pip install --upgrade torch numpy transformers accelerate triton kernels && \
  wget https://huggingface.co/datasets/ariG23498/distributed/raw/main/tp_gpt_oss.py && \
  torchrun --nproc-per-node=4 tp_gpt_oss.py"
```

> hf jobs 对所有 Hugging Face PRO 和 Enterprise 用户可用。

幕后，`tp_plan="auto"` 会为每一层选择一个预定义的分片方案，并接好所需的 [collectives（集合通信）](https://huggingface.co/spaces/nanotron/ultrascale-playbook?section=a0:_parallel_programming_crash_course)。想确认哪些张量被分片了，可以用 `print(model._tp_plan)` 查看当前生效的计划。

### 什么时候该用 TP

当模型大到一块 GPU 装不下、而且你不仅要解决显存摆放、还想要**并行计算**时，就用 TP。TP 往往能随 GPU 数量扩展吞吐，对长序列或大批量尤其如此。

> 如果你好奇 TP 与 device_map="auto"（显存摆放）有何区别，这篇简短的 Stack Overflow 回答解释了两者的差异及各自适用场景。

想进一步了解 TP，这里有两份必读资料：

- [`transformers` 指南](https://huggingface.co/docs/transformers/en/perf_infer_gpu_multi)：张量并行、受支持模型、计划与扩展点。
- [Ultra-Scale Playbook](https://huggingface.co/spaces/nanotron/ultrascale-playbook?section=tensor_parallelism)：TP 的背景知识及其与其他并行模式的关系。

## 专家并行

专家并行（Expert Parallelism，EP）把 **MoE 层内部的专家**切分到多块 GPU 上。每个 token 只被路由到一到几个专家，因此只有那些专家会执行自己的前馈网络。由于专家是相互独立的 MLP，我们可以把不同的专家放到不同的 rank 上，只交换被路由 token 的隐藏状态。这让每张卡上的矩阵乘法保持完整，用路由和集合通信取代了张量切分。

使用 `torchrun` 以多进程方式运行。EP 通过分布式配置启用，在 transformers 中对 GPT-OSS 的 MoE 层开箱即用。

```
# run with: torchrun --nproc-per-node 4 ep_gpt_oss.py
import torch
from transformers import PreTrainedTokenizerFast, GptOssForCausalLM
from transformers.distributed import DistributedConfig

model_id = "openai/gpt-oss-120b"
tokenizer = PreTrainedTokenizerFast.from_pretrained(model_id)
model = GptOssForCausalLM.from_pretrained(
    model_id,
    distributed_config=DistributedConfig(enable_expert_parallel=True), # enabling EP
    dtype="auto",
).eval()

messages = [
    {"role": "system", "content": "Be concise."},
    {"role": "user", "content": "Explain KV caching briefly."},
]
inputs = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    return_tensors="pt",
    return_dict=True,
    reasoning_effort="low",
).to(model.device)

with torch.inference_mode():
    generations = model.generate(**inputs, max_new_tokens=128)

print(tokenizer.decode(generations[0][inputs["input_ids"].shape[-1]:]))
```

用 `hf jobs` 运行的方式如下

```
hf jobs run --detach --flavor l4x4 ghcr.io/astral-sh/uv:debian /bin/bash -c \
  "uv venv .venv --python 3.12 && \
  source .venv/bin/activate && \
  uv pip install --upgrade torch numpy transformers accelerate triton kernels && \
  wget https://huggingface.co/datasets/ariG23498/distributed/raw/main/ep_gpt_oss.py && \
  torchrun --nproc-per-node=4 ep_gpt_oss.py"
```

> 启用专家并行时，张量并行也会一并激活。这意味着你可以同时拥有两者的好处！

## 动态滑动窗口层与缓存

许多近期 LLM 使用*滑动窗口（sliding window）*注意力，或滑动与全局注意力层组合，以此节省内存、削减随序列长度增长的昂贵平方级矩阵乘法。不过，transformers 中的动态 KV cache 实现过去仍按序列长度继续分配空间，而不区分各个注意力层。你一直可以用编译（即固定形状）来优化内存，但那是完全不同的另一回事。

`transformers` 现在有了 [**`DynamicSlidingWindowLayer`**](https://github.com/huggingface/transformers/blob/64ae6e6b1de2c6822a53be46aba9db68f75ec595/src/transformers/cache_utils.py#L165) 和一个*感知配置*的 [`DynamicCache`](https://github.com/huggingface/transformers/blob/64ae6e6b1de2c6822a53be46aba9db68f75ec595/src/transformers/cache_utils.py#L959)。如果模型配置声明了滑动窗口或混合注意力（同时使用滑动与全局注意力层），缓存对滑动层**超过窗口后就不再增长**。如果你不传配置，行为就和以前一样（KV 随序列长度一路线性增长）。

对于只用滑动窗口层的模型，例如 Mistral 7B，当序列达到窗口大小（此处为 4096）时，缓存内存便不再增长。这很合理，因为滑动层本来就只能回看之前的 4K 个 token。

[![mistral cache behaviour comparison](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/faster-transformers/mistral-dynamic-cache-with-config.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/faster-transformers/mistral-dynamic-cache-with-config.png)

OpenAI gpt-oss 在滑动与全局注意力层之间交替，如我们稍后所见，随着序列变长，KV cache 总内存会*减半*。这带来了：

- **滑动或混合注意力模型（如 GPT-OSS）的 KV-cache 内存大幅降低**。缓存增长在达到窗口后便趋于平缓（例如 Mistral 是 4K，GPT-OSS 滑动层是 128），而不是随生成 token 总数线性增长。（[GitHub](https://github.com/huggingface/transformers/pull/40039)、[Transformers](https://huggingface.co/docs/transformers/en/model_doc/mistral)）
- **长提示/长生成场景下的速度与延迟优势**：更小的 KV 张量意味着更轻的注意力读写和更小的内存带宽压力，在越过窗口之后尤为明显（这正是滑动窗口/混合 LLM 的核心动机）。([AI21](https://www.ai21.com/blog/rise-of-hybrid-llms/)、[vLLM Blog](https://blog.vllm.ai/2025-08-05/gpt-oss.html))

### 如何使用

优化后的缓存默认启用，也就是说**你不需要对现有代码做任何改动**。如果你想显式创建 `DynamicCache`，方法如下：

```
from transformers import AutoModelForCausalLM, AutoTokenizer, DynamicCache

model_id = "openai/gpt-oss-20b"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    dtype="auto",
    device_map="auto",
).eval()

messages = [
    {"role": "system", "content": "Always respond in riddles"},
    {"role": "user", "content": "What is the weather like in Madrid?"},
]

inputs = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    return_tensors="pt",
    return_dict=True,
    reasoning_effort="low",
).to(model.device)

cache = DynamicCache(config=model.config) # create the cache with the model's config

generated = model.generate(
    **inputs,
    max_new_tokens=500,
    past_key_values=cache
)
print(tokenizer.decode(generated[0][inputs["input_ids"].shape[-1]:]))
```

**图 6** 展示了在滑动窗口注意力下使用动态 KV Cache 能带来多大差别。

| [![sliding window cache](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/faster-transformers/dynamic-cache.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/faster-transformers/dynamic-cache.png) |
| --- |
| 图 6：滑动窗口下动态缓存的内存分析 |

## 连续批处理与分页注意力

典型的自回归生成过程如 **图 7** 所示。你输入 prefill（预填充）token，模型逐一开始预测每个新 token，直到预测出 EOS（End of Sequence）token。

| [![prefilling](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/faster-transformers/prefill-tokens.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/faster-transformers/prefill-tokens.png) |
| --- |
| 图 7：自回归 token 生成 |

再来看传入一**批**输入时生成过程是什么样子。在 **图 8** 中你会注意到，有些生成比其他更早结束。这种长度不齐让 GPU 利用不充分。

| [![static batching](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/faster-transformers/static-batching.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/faster-transformers/static-batching.png) |
| --- |
| 图 8：序列的静态批处理 |

这种序列批处理方式称为*静态批处理（static batching）*。虽然简单好懂，但它天然带有低效：只有当每句话完全生成完毕，才能进入下一批。

为了绕过这个问题，我们使用**动态批处理**（也叫*连续批处理*，continuous batching）。与其等所有生成都结束，我们把新来的请求调度进已完成的生成腾出的位置。这样，批次里一旦有生成完成，立刻用下一个请求填充批次。整个过程如 **图 9** 所示。

| [![continuous batching](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/faster-transformers/dynamic-batching.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/faster-transformers/dynamic-batching.png) |
| --- |
| 图 9：序列的连续批处理 |

Transformers 通过 `generate_batch` API 支持连续批处理。这不是为生产级模型服务准备的——vLLM、SGLang 这类框架更擅长那件事——但对评测和实验非常有帮助。这里有一个端到端运行 CB 的[示例脚本](https://github.com/huggingface/transformers/blob/0f1b128d3359a26bd18be99c26d7f04fb3cba914/examples/pytorch/continuous_batching_simple.py)，跑在 `Qwen/Qwen3-4B-Instruct-2507` 上。

我们还用 100 个样本做了连续批处理与静态批处理的基准对比。在图 9 中可以看到，CB 比 SB 快不少。

| [![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/faster-transformers/cb-sb.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/faster-transformers/cb-sb.png) |
| --- |
| 图 9：连续批处理 vs 静态批处理的 Tokens/Second |

> 你可以在这里把玩基准测试：SB、CB

## 更快地加载更大的模型

当你把大模型加载进 GPU 时，PyTorch 需要**为每一层的权重预留 GPU 内存**。每次（每层的）分配请求都耗时，对数十亿参数的模型来说意味着**成千上万次微小内存分配**，模型就绪前的等待被越拖越长。与其每次都向 GPU 申请新内存，分配器可以**一次性握住一大块**，然后从中快速切分。

PyTorch 的分配器 exactly 能做到这点。问题在于，分配器只有在你先给它一大块内存之后才快起来。如果不先"把储藏室塞满"，你还是得反复慢慢跑"市场"。这个 PR（🎉 [#36380](https://github.com/huggingface/transformers/pull/36380)）教会了 `transformers` 在开始拷贝模型权重之前**预先备好储藏室**。

它做了这些：

- 查看 `device_map`（每层将位于哪块设备）。
- **在每块 GPU 上预先分配足够大的内存块**。
- 之后各层被拷入时，直接整齐地放进这段预留空间。

你不需要对现有代码做任何改动，这是 `transformers` 的默认行为。无论你使用 **`device_map="auto"`** 还是自备 device map，现在模型加载都会自动变快。如果你用 **张量并行（`tp_plan="auto"`）加 `torchrun`** 运行，配套的改动也让多 GPU 加载更聪明，同样受益。

## 结语

`transformers` 迭代很快，而且社区优先。库的演进紧跟领域步伐，因为贡献者们公开地塑造它。为新模型添加的组件会进入工具箱，在未来的集成中被复用。

这样的速度带来了 GPT-OSS 系列这样的 day-zero 集成。随着整个技术栈越来越 [PyTorch-first](https://x.com/LysandreJik/status/1933201171130593530)，它甩掉臃肿，加倍投入实际场景中重要的 PyTorch 路径。结果是更干净的核心：通过社区 kernel、量化和并行计划解锁新能力，同时[标准化模型定义](https://huggingface.co/blog/transformers-model-definition)，让 transformers 支持的架构成为参照，并扩展到更广的生态。

本文是我们反复朝同一方向推进的过程中的一个切片快照：服务社区的需求。要跟上 transformers 的最新 additions，请查看[文档](https://huggingface.co/docs/transformers/index)和[发布说明](https://github.com/huggingface/transformers/releases)。也请继续分享反馈、把模型发布到 transformers 里供社区享用 🤗

## 延伸阅读

想深入特定主题，这里有一份值得一看的链接清单：

- [Hugging Face GPT-OSS Recipes 仓库](https://github.com/huggingface/gpt-oss-recipes)
- [欢迎 OpenAI 全新开源模型家族 GPT OSS](https://huggingface.co/blog/welcome-openai-gpt-oss)
- [OpenAI Cookbook：GPT-OSS 专题](https://cookbook.openai.com/topic/gpt-oss)
- [Transformers 文档：多 GPU 分布式推理](https://huggingface.co/docs/transformers/en/perf_infer_gpu_multi)
- [Matthew Carrigan 关于 GPT OSS 技术创新的 X 线程](https://x.com/carrigmat/status/1952779877569978797)
- [YouTube 视频：OpenAI GPT OSS 发布会](https://www.youtube.com/watch?v=bbkcEiUjehk)
- [Transformers PR #36380：在加速器上更快加载模型](https://github.com/huggingface/transformers/pull/36380)
- [Transformers PR #36335：为张量并行更新 from_pretrained](https://github.com/huggingface/transformers/pull/36335)
- [Transformers PR #40039：新的动态滑动窗口层与缓存](https://github.com/huggingface/transformers/pull/40039)
- [HAN Lab 博客：Attention Sinks 如何让语言模型保持稳定](https://hanlab.mit.edu/blog/streamingllm)
