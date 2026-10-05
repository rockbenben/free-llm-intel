---
vendor: huggingface
title: 探索 Diffusers 中的量化后端
original_title: Exploring Quantization Backends in Diffusers
url: https://huggingface.co/blog/diffusers-quantization
date: 2025-06-27
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 24068821da4c
translator: agent
---

返回文章列表

# 探索 Diffusers 中的量化后端

发布于
					2025 年 5 月 21 日

在 GitHub 上更新

点赞

45

- [![](https://huggingface.co/avatars/1604409b53f4cc409cbeac98d51b29e1.svg)](https://huggingface.co/lumiseven)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6340651b388c3fa40f9a5bc0/vM3rB17pUNT11MUhYqfFY.png)](https://huggingface.co/adamm-hf)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/654b3a5c8f78bd30275cc6a7/gJTYlz4rP9tqZ_2PKipVb.png)](https://huggingface.co/minpeter)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/638f308fc4444c6ca870b60a/Q11NK-8-JbiilJ-vk2LAR.png)](https://huggingface.co/linoyts)
- [![](https://huggingface.co/avatars/3bb8728057fa2ba0e24f5ceb1600068d.svg)](https://huggingface.co/Zmu)
- [![](https://huggingface.co/avatars/0d7d8635d2ae52c56876e97db09f8be7.svg)](https://huggingface.co/Deadbytes)

Derek Liu

derekl35

Marc Sun

marcsun13

Sayak Paul

sayakpaul

像 Flux（一种基于 flow 的文本生成图像模型）这样的大型扩散模型能生成令人惊艳的图像，但体量可能成为门槛——需要大量显存和算力。量化提供了一个有力的解法：把这些模型压缩，让它们在不过多牺牲性能的前提下更易使用。但灵魂拷问永远是：你真的能看出最终图像的差别吗？

在深入 Hugging Face Diffusers 中各种量化后端的技术细节之前，不如先测测你自己的眼力？

## 找出量化模型

我们搭了一个环境：你提供一条提示词，我们同时用原始高精度模型（如 BF16 的 Flux-dev）和若干量化版本（BnB 4-bit、BnB 8-bit）生成结果。生成的图像会展示给你，你的挑战是找出哪些来自量化模型。

在[这里](https://huggingface.co/spaces/diffusers/flux-quant)试试，或直接看下面的嵌入！

通常，尤其是 8-bit 量化时，差异很微妙，不仔细对比看不出来。更激进的量化（4-bit 或更低）可能更容易被察觉，但结果依然可以很好——考虑到巨量的显存节省，这相当划算。不过 NF4 往往能给出最佳的权衡。

好，接下来深入技术细节。

## Diffusers 中的量化后端

在此前的文章《[Memory-efficient Diffusion Transformers with Quanto and Diffusers](https://huggingface.co/blog/quanto-diffusers)》基础上，这篇博客探索直接集成进 Hugging Face Diffusers 的多种量化后端。我们会看看 bitsandbytes、GGUF、torchao、Quanto 以及原生 FP8 支持如何让大而强的模型更易用，并以 Flux 为例演示用法。

在深入各量化后端之前，先介绍 FluxPipeline（使用 [black-forest-labs/FLUX.1-dev](https://huggingface.co/black-forest-labs/FLUX.1-dev) checkpoint）及其各组件——它们正是我们要量化的对象。以 BF16 精度加载完整的 `FLUX.1-dev` 模型约需 31.447 GB 显存。主要组件如下：

- **文本编码器（CLIP 和 T5）：** **作用：** 处理输入的文本提示词。FLUX-dev 用 CLIP 做初步理解，用更大的 T5 做细致理解并改善文字渲染。 **显存：** T5 - 9.52 GB；CLIP - 246 MB（BF16 下）
- **Transformer（主模型 - MMDiT）：** **作用：** 核心生成部分（Multimodal Diffusion Transformer，多模态扩散 Transformer）。根据文本嵌入在潜空间生成图像。  **显存：** 23.8 GB（BF16 下）
- **变分自编码器（VAE）：** **作用：** 在像素空间与潜空间之间转换图像。把生成的潜表示解码为像素图像。 **显存：** 168 MB（BF16 下）
- **量化重点：** 示例将主要聚焦 `transformer` 和 `text_encoder_2`（T5），因为它们的显存节省最显著。

```
prompts = [
    "Baroque style, a lavish palace interior with ornate gilded ceilings, intricate tapestries, and dramatic lighting over a grand staircase.",
    "Futurist style, a dynamic spaceport with sleek silver starships docked at angular platforms, surrounded by distant planets and glowing energy lines.",
    "Noir style, a shadowy alleyway with flickering street lamps and a solitary trench-coated figure, framed by rain-soaked cobblestones and darkened storefronts.",
]
```

### bitsandbytes (BnB)

[`bitsandbytes`](https://github.com/bitsandbytes-foundation/bitsandbytes) 是一个流行且易用的 8-bit / 4-bit 量化库，被广泛用于 LLM 和 QLoRA 微调。它同样适用于基于 transformer 的扩散与 flow 模型。

| BF16 | BnB 4-bit | BnB 8-bit |
| --- | --- | --- |
| *Flux-dev 模型输出在 BF16（左）、BnB 4-bit（中）、BnB 8-bit（右）量化下的视觉对比。（点击图片放大）* |  |  |

| 精度 | 加载后显存 | 峰值显存 | 推理耗时 |
| --- | --- | --- | --- |
| BF16 | ~31.447 GB | 36.166 GB | 12 秒 |
| 4-bit | 12.584 GB | 17.281 GB | 12 秒 |
| 8-bit | 19.273 GB | 24.432 GB | 27 秒 |

所有基准测试在 1x NVIDIA H100 80GB GPU 上进行

示例（Flux-dev + BnB 4-bit）：

```
import torch
from diffusers import FluxPipeline
from diffusers import BitsAndBytesConfig as DiffusersBitsAndBytesConfig
from diffusers.quantizers import PipelineQuantizationConfig
from transformers import BitsAndBytesConfig as TransformersBitsAndBytesConfig

model_id = "black-forest-labs/FLUX.1-dev"

pipeline_quant_config = PipelineQuantizationConfig(
    quant_mapping={
        "transformer": DiffusersBitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16),
        "text_encoder_2": TransformersBitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16),
    }
)

pipe = FluxPipeline.from_pretrained(
    model_id,
    quantization_config=pipeline_quant_config,
    torch_dtype=torch.bfloat16
)
pipe.to("cuda")

prompt = "Baroque style, a lavish palace interior with ornate gilded ceilings, intricate tapestries, and dramatic lighting over a grand staircase."
pipe_kwargs = {
    "prompt": prompt,
    "height": 1024,
    "width": 1024,
    "guidance_scale": 3.5,
    "num_inference_steps": 50,
    "max_sequence_length": 512,
}


print(f"Pipeline memory usage: {torch.cuda.max_memory_reserved() / 1024**3:.3f} GB")

image = pipe(
    **pipe_kwargs, generator=torch.manual_seed(0),
).images[0]

print(f"Pipeline memory usage: {torch.cuda.max_memory_reserved() / 1024**3:.3f} GB")

image.save("flux-dev_bnb_4bit.png")
```

> 注意：使用 PipelineQuantizationConfig 配合 bitsandbytes 时，需要分别从 diffusers 导入 DiffusersBitsAndBytesConfig、从 transformers 导入 TransformersBitsAndBytesConfig，因为这些组件来自不同的库。如果你偏好更简单、不用管理这些不同导入的方式，可以采用流水线级量化的替代方案，Diffusers 文档中的 Pipeline-level quantization 页面有示例。

更多信息见 [bitsandbytes 文档](https://huggingface.co/docs/diffusers/quantization/bitsandbytes)。

### torchao

[`torchao`](https://github.com/pytorch/ao) 是 PyTorch 原生的架构优化库，提供量化、稀疏化和自定义数据类型，设计上兼容 `torch.compile` 和 FSDP。Diffusers 支持 `torchao` 的多种特殊数据类型，可以对模型优化做细粒度控制。

| int4_weight_only | int8_weight_only | float8_weight_only |
| --- | --- | --- |
| *Flux-dev 模型输出在 torchao int4_weight_only（左）、int8_weight_only（中）、float8_weight_only（右）量化下的视觉对比。（点击图片放大）* |  |  |

| torchao 精度 | 加载后显存 | 峰值显存 | 推理耗时 |
| --- | --- | --- | --- |
| int4_weight_only | 10.635 GB | 14.654 GB | 109 秒 |
| int8_weight_only | 17.020 GB | 21.482 GB | 15 秒 |
| float8_weight_only | 17.016 GB | 21.488 GB | 15 秒 |

示例（Flux-dev + torchao INT8 weight-only）：

```
@@
- from diffusers import BitsAndBytesConfig as DiffusersBitsAndBytesConfig
+ from diffusers import TorchAoConfig as DiffusersTorchAoConfig

- from transformers import BitsAndBytesConfig as TransformersBitsAndBytesConfig
+ from transformers import TorchAoConfig as TransformersTorchAoConfig
@@
pipeline_quant_config = PipelineQuantizationConfig(
    quant_mapping={
-         "transformer": DiffusersBitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16),
-         "text_encoder_2": TransformersBitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16),
+         "transformer": DiffusersTorchAoConfig("int8_weight_only"),
+         "text_encoder_2": TransformersTorchAoConfig("int8_weight_only"),
    }
)
```

示例（Flux-dev + torchao INT4 weight-only）：

```
@@
- from diffusers import BitsAndBytesConfig as DiffusersBitsAndBytesConfig
+ from diffusers import TorchAoConfig as DiffusersTorchAoConfig

- from transformers import BitsAndBytesConfig as TransformersBitsAndBytesConfig
+ from transformers import TorchAoConfig as TransformersTorchAoConfig
@@
pipeline_quant_config = PipelineQuantizationConfig(
    quant_mapping={
-         "transformer": DiffusersBitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16),
-         "text_encoder_2": TransformersBitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16),
+         "transformer": DiffusersTorchAoConfig("int4_weight_only"),
+         "text_encoder_2": TransformersTorchAoConfig("int4_weight_only"),
    }
)

pipe = FluxPipeline.from_pretrained(
    model_id,
    quantization_config=pipeline_quant_config,
    torch_dtype=torch.bfloat16,
+    device_map="balanced"
)
- pipe.to("cuda")
```

更多信息见 [torchao 文档](https://huggingface.co/docs/diffusers/quantization/torchao)。

### Quanto

[Quanto](https://github.com/huggingface/optimum-quanto) 是通过 [`optimum`](https://huggingface.co/docs/optimum/index) 库与 Hugging Face 生态集成的量化库。

| INT4 | INT8 | FP8 |
| --- | --- | --- |
| *Flux-dev 模型输出在 Quanto INT4（左）、INT8（中）、FP8（右）量化下的视觉对比。（点击图片放大）* |  |  |

| quanto 精度 | 加载后显存 | 峰值显存 | 推理耗时 |
| --- | --- | --- | --- |
| INT4 | 12.254 GB | 16.139 GB | 109 秒 |
| INT8 | 17.330 GB | 21.814 GB | 15 秒 |
| FP8 | 16.395 GB | 20.898 GB | 16 秒 |

示例（Flux-dev + quanto INT8 weight-only）：

```
@@
- from diffusers import BitsAndBytesConfig as DiffusersBitsAndBytesConfig
+ from diffusers import QuantoConfig as DiffusersQuantoConfig

- from transformers import BitsAndBytesConfig as TransformersBitsAndBytesConfig
+ from transformers import QuantoConfig as TransformersQuantoConfig
@@
pipeline_quant_config = PipelineQuantizationConfig(
    quant_mapping={
-         "transformer": DiffusersBitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16),
-         "text_encoder_2": TransformersBitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16),
+         "transformer": DiffusersQuantoConfig(weights_dtype="int8"),
+         "text_encoder_2": TransformersQuantoConfig(weights_dtype="int8"),
    }
)
```

> 注意：截至撰稿时，要在 Quanto 下获得 float8 支持，需要 optimum-quanto<0.2.5 并直接使用 quanto。我们正在着手修复这个问题。

示例（Flux-dev + quanto FP8 weight-only）

```
import torch
from diffusers import AutoModel, FluxPipeline
from transformers import T5EncoderModel
from optimum.quanto import freeze, qfloat8, quantize

model_id = "black-forest-labs/FLUX.1-dev"

text_encoder_2 = T5EncoderModel.from_pretrained(
    model_id,
    subfolder="text_encoder_2",
    torch_dtype=torch.bfloat16,
)

quantize(text_encoder_2, weights=qfloat8)
freeze(text_encoder_2)

transformer = AutoModel.from_pretrained(
      model_id,
      subfolder="transformer",
      torch_dtype=torch.bfloat16,
)

quantize(transformer, weights=qfloat8)
freeze(transformer)

pipe = FluxPipeline.from_pretrained(
    model_id,
    transformer=transformer,
    text_encoder_2=text_encoder_2,
    torch_dtype=torch.bfloat16
).to("cuda")
```

更多信息见 [Quanto 文档](https://huggingface.co/docs/diffusers/quantization/quanto)。

### GGUF

GGUF 是在 llama.cpp 社区中流行的一种用于存放量化模型的文件格式。

| Q2_k | Q4_1 | Q8_0 |
| --- | --- | --- |
| *Flux-dev 模型输出在 GGUF Q2_k（左）、Q4_1（中）、Q8_0（右）量化下的视觉对比。（点击图片放大）* |  |  |

| GGUF 精度 | 加载后显存 | 峰值显存 | 推理耗时 |
| --- | --- | --- | --- |
| Q2_k | 13.264 GB | 17.752 GB | 26 秒 |
| Q4_1 | 16.838 GB | 21.326 GB | 23 秒 |
| Q8_0 | 21.502 GB | 25.973 GB | 15 秒 |

示例（Flux-dev + GGUF Q4_1）

```
import torch
from diffusers import FluxPipeline, FluxTransformer2DModel, GGUFQuantizationConfig

model_id = "black-forest-labs/FLUX.1-dev"

# Path to a pre-quantized GGUF file
ckpt_path = "https://huggingface.co/city96/FLUX.1-dev-gguf/resolve/main/flux1-dev-Q4_1.gguf"

transformer = FluxTransformer2DModel.from_single_file(
    ckpt_path,
    quantization_config=GGUFQuantizationConfig(compute_dtype=torch.bfloat16),
    torch_dtype=torch.bfloat16,
)

pipe = FluxPipeline.from_pretrained(
    model_id,
    transformer=transformer,
    torch_dtype=torch.bfloat16,
)
pipe.to("cuda")
```

更多信息见 [GGUF 文档](https://huggingface.co/docs/diffusers/quantization/gguf)。

### FP8 逐层转换（`enable_layerwise_casting`）

FP8 Layerwise Casting（逐层精度转换）是一种显存优化技术。原理是把模型权重以紧凑的 FP8（8 位浮点）格式存放，占用大约只有标准 FP16/BF16 精度的一半。在某一层执行计算之前，其权重会被动态提升（cast up）到更高的计算精度（如 FP16/BF16），算完立即再降回 FP8 以节省存储。这套方法之所以可行，是因为核心计算保持了高精度，而对量化特别敏感的层（如归一化层）通常会被跳过。该技术还可以与[分组卸载（group offloading）](https://huggingface.co/docs/diffusers/en/optimization/memory#group-offloading)组合，获得进一步节省。

| FP8 (e4m3) |
| --- |
| *Flux-dev 模型使用 FP8 Layerwise Casting（e4m3）量化的视觉输出。* |

| 精度 | 加载后显存 | 峰值显存 | 推理耗时 |
| --- | --- | --- | --- |
| FP8 (e4m3) | 23.682 GB | 28.451 GB | 13 秒 |

```
import torch
from diffusers import AutoModel, FluxPipeline

model_id = "black-forest-labs/FLUX.1-dev"

transformer = AutoModel.from_pretrained(
    model_id,
    subfolder="transformer",
    torch_dtype=torch.bfloat16
)
transformer.enable_layerwise_casting(storage_dtype=torch.float8_e4m3fn, compute_dtype=torch.bfloat16)

pipe = FluxPipeline.from_pretrained(model_id, transformer=transformer, torch_dtype=torch.bfloat16)
pipe.to("cuda")
```

更多信息见 [Layerwise casting 文档](https://huggingface.co/docs/diffusers/main/en/optimization/memory#layerwise-casting)。

## 与更多显存优化技术及 torch.compile 组合

这些量化后端大多可以与 Diffusers 提供的显存优化技术组合使用。我们来探索 CPU 卸载、分组卸载和 `torch.compile`。这些技术的更多细节见 [Diffusers 文档](https://huggingface.co/docs/diffusers/main/en/optimization/memory)。

> 注意：截至撰稿时，bnb + torch.compile 也可以工作，前提是 bnb 从源码安装并搭配 pytorch nightly，或使用 fullgraph=False。

示例（Flux-dev + BnB 4-bit + enable_model_cpu_offload）：

```
import torch
from diffusers import FluxPipeline
from diffusers import BitsAndBytesConfig as DiffusersBitsAndBytesConfig
from diffusers.quantizers import PipelineQuantizationConfig
from transformers import BitsAndBytesConfig as TransformersBitsAndBytesConfig

model_id = "black-forest-labs/FLUX.1-dev"

pipeline_quant_config = PipelineQuantizationConfig(
    quant_mapping={
        "transformer": DiffusersBitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16),
        "text_encoder_2": TransformersBitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16),
    }
)

pipe = FluxPipeline.from_pretrained(
    model_id,
    quantization_config=pipeline_quant_config,
    torch_dtype=torch.bfloat16
)
- pipe.to("cuda")
+ pipe.enable_model_cpu_offload()
```

**模型 CPU 卸载（`enable_model_cpu_offload`）**：该方法在推理流程中把整个模型组件（如 UNet、文本编码器、VAE）在 CPU 和 GPU 之间来回搬运。它可带来可观的 VRAM 节省，而且通常比更细粒度的卸载更快，因为数据搬运次数更少、每次更大。

**bnb + `enable_model_cpu_offload`**：

| 精度 | 加载后显存 | 峰值显存 | 推理耗时 |
| --- | --- | --- | --- |
| 4-bit | 12.383 GB | 12.383 GB | 17 秒 |
| 8-bit | 19.182 GB | 23.428 GB | 27 秒 |

示例（Flux-dev + fp8 逐层转换 + 分组卸载）：

```
import torch
from diffusers import FluxPipeline, AutoModel

model_id = "black-forest-labs/FLUX.1-dev"

transformer = AutoModel.from_pretrained(
    model_id,
    subfolder="transformer",
    torch_dtype=torch.bfloat16,
    # device_map="cuda"
)
transformer.enable_layerwise_casting(storage_dtype=torch.float8_e4m3fn, compute_dtype=torch.bfloat16)
+ transformer.enable_group_offload(onload_device=torch.device("cuda"), offload_device=torch.device("cpu"), offload_type="leaf_level", use_stream=True)

pipe = FluxPipeline.from_pretrained(model_id, transformer=transformer, torch_dtype=torch.bfloat16)
- pipe.to("cuda")
```

**分组卸载（对 `diffusers` 组件用 `enable_group_offload`，对通用 `torch.nn.Module` 用 `apply_group_offloading`）**：它把模型内部成组的层（如 `torch.nn.ModuleList` 或 `torch.nn.Sequential` 实例）搬到 CPU。这种方式通常比整模型卸载更省显存，也比顺序卸载更快。

**FP8 逐层转换 + 分组卸载**：

| 精度 | 加载后显存 | 峰值显存 | 推理耗时 |
| --- | --- | --- | --- |
| FP8 (e4m3) | 9.264 GB | 14.232 GB | 58 秒 |

示例（Flux-dev + torchao 4-bit + torch.compile）：

```
import torch
from diffusers import FluxPipeline
from diffusers import TorchAoConfig as DiffusersTorchAoConfig
from diffusers.quantizers import PipelineQuantizationConfig
from transformers import TorchAoConfig as TransformersTorchAoConfig

from torchao.quantization import Float8WeightOnlyConfig

model_id = "black-forest-labs/FLUX.1-dev"
dtype = torch.bfloat16

pipeline_quant_config = PipelineQuantizationConfig(
    quant_mapping={
        "transformer":DiffusersTorchAoConfig("int4_weight_only"),
        "text_encoder_2": TransformersTorchAoConfig("int4_weight_only"),
    }
)

pipe = FluxPipeline.from_pretrained(
    model_id,
    quantization_config=pipeline_quant_config,
    torch_dtype=torch.bfloat16,
    device_map="balanced"
)

+ pipe.transformer = torch.compile(pipe.transformer, mode="max-autotune", fullgraph=True)
```

> 注意：torch.compile 会引入细微的数值差异，可能导致输出图像发生变化

**torch.compile**：另一个互补的加速手段是用 PyTorch 2.x 的 torch.compile() 加速模型执行。编译不会直接降低内存占用，但可以显著提升推理速度。PyTorch 2.0 的 compile（Torch Dynamo）通过提前（ahead-of-time）追踪并优化模型计算图来实现加速。

**torchao + `torch.compile`**：

| torchao 精度 | 加载后显存 | 峰值显存 | 推理耗时 | 编译耗时 |
| --- | --- | --- | --- | --- |
| int4_weight_only | 10.635 GB | 15.238 GB | 6 秒 | ~285 秒 |
| int8_weight_only | 17.020 GB | 22.473 GB | 8 秒 | ~851 秒 |
| float8_weight_only | 17.016 GB | 22.115 GB | 8 秒 | ~545 秒 |

部分基准测试结果可在这里查看：

## 开箱即用的量化 checkpoint

本博客中用到的 `bitsandbytes` 和 `torchao` 量化模型都在我们的 Hugging Face 集合里：[集合链接](https://huggingface.co/collections/diffusers/flux-quantized-checkpoints-682c951aebd378a2462984a0)。

## 结论

这里给一份量化后端选择速查指南：

- **最省事的显存节省（NVIDIA）：** 从 `bitsandbytes` 4/8-bit 开始。它还可以与 `torch.compile()` 组合以加速推理。
- **优先追求推理速度：** `torchao`、`GGUF`、`bitsandbytes` 都可以搭配 `torch.compile()`，有机会提升推理速度。
- **硬件灵活性（CPU/MPS）、FP8 精度：** `Quanto` 是个不错的选择。
- **图简单（Hopper/Ada）：** 试试 FP8 逐层转换（`enable_layerwise_casting`）。
- **要用现成的 GGUF 模型：** 用 GGUF 加载（`from_single_file`）。
- **好奇量化下的训练？** 敬请期待后续博客！更新（2025 年 6 月 19 日）：[它来了](https://huggingface.co/blog/flux-qlora)！

量化大大降低了使用大型扩散模型的门槛。多试试这些后端，找到最适合你需求的显存、速度与质量平衡点。

*致谢：感谢 [Chunte](https://huggingface.co/Chunte) 为本文提供缩略图。*

## 文中提到的模型 1

## 文中提到的 Spaces 1

## 文中提到的 Collections 1

我们博客的更多文章

guide

diffusers

quantization

## (LoRA) Fine-Tuning FLUX.1-dev on Consumer Hardware

- ![](https://huggingface.co/avatars/e5b8331c9a96cd96b679f38afd30422e.svg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/63ce875d199b36f7552d4f07/bpUrvhXDagzRqZ3vxTcSF.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1649681653581-5f7fbd813e94f16a85448745.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6141a88b3a0ec78603c9e784/DJsxSmWV39M33JFheLobC.jpeg)
- +1

107

2025 年 6 月 19 日

guide

diffusers

quantization

## Bringing Nunchaku 4-bit Diffusion Inference to Diffusers

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/655647bf2f76548766fce60f/mZhWuhJb-bzlzp-C3VoO_.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1649681653581-5f7fbd813e94f16a85448745.jpeg)

69

2026 年 7 月 23 日

### 社区

tolgacangoz

2025 年 10 月 25 日

·

此评论已被隐藏（标记为已解决）

将文件拖入文本输入框、粘贴，或

点击此处

，即可上传图像、音频和视频。

点击或粘贴此处上传图片

· [注册](https://huggingface.co/join?next=%2Fblog%2Fdiffusers-quantization)或[登录](https://huggingface.co/login?next=%2Fblog%2Fdiffusers-quantization)发表评论

点赞

45

- [![](https://huggingface.co/avatars/1604409b53f4cc409cbeac98d51b29e1.svg)](https://huggingface.co/lumiseven)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6340651b388c3fa40f9a5bc0/vM3rB17pUNT11MUhYqfFY.png)](https://huggingface.co/adamm-hf)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/654b3a5c8f78bd30275cc6a7/gJTYlz4rP9tqZ_2PKipVb.png)](https://huggingface.co/minpeter)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/638f308fc4444c6ca870b60a/Q11NK-8-JbiilJ-vk2LAR.png)](https://huggingface.co/linoyts)
- [![](https://huggingface.co/avatars/3bb8728057fa2ba0e24f5ceb1600068d.svg)](https://huggingface.co/Zmu)
- [![](https://huggingface.co/avatars/0d7d8635d2ae52c56876e97db09f8be7.svg)](https://huggingface.co/Deadbytes)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/650e5979c305ec67e6fc2c19/C9WMiNhR_QxxAecVl8b_o.png)](https://huggingface.co/jonahelisio)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/67e4716128d4a2a5c8c80c61/GX7eOFpBK0MBkJ51fqVZk.png)](https://huggingface.co/angel333)
- [![](https://huggingface.co/avatars/498080aecc4b5e0b828ea742daa41875.svg)](https://huggingface.co/mones2222)
- [![](https://huggingface.co/avatars/b7f43a4c70139aa2527f111cc42c8007.svg)](https://huggingface.co/KagdelwarSejal)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/67cfc23e88d980bafa621983/3uKqieo1ndzi8lxLDAjUJ.jpeg)](https://huggingface.co/key-life)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/65baa31607366d903890bcf4/6M9WaawnvJ-2h5wSUic1I.jpeg)](https://huggingface.co/badaoui)

## 文中提到的模型 1

## 文中提到的 Spaces 1

## 文中提到的 Collections 1
