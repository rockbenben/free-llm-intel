---
vendor: huggingface
title: 🧨 Diffusers 迎来 Stable Diffusion 3
original_title: 🧨 Diffusers welcomes Stable Diffusion 3
url: https://huggingface.co/blog/sd3
date: 2023-01-24
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

本文另有 [简体中文](https://huggingface.co/blog/zh/sd3) 版本。

[Stable Diffusion 3](https://stability.ai/news/stable-diffusion-3-research-paper)（SD3）——Stability AI 的 Stable Diffusion 模型家族的最新迭代——现已上架 Hugging Face Hub，并可与 🧨 Diffusers 一起使用。

今天发布的模型是 Stable Diffusion 3 Medium，2B 参数。

作为本次发布的一部分，我们提供了：

- Hub 上的模型
- Diffusers 集成
- SD3 的 Dreambooth 与 LoRA 训练脚本

## 目录

- [What's new with SD3](https://huggingface.co/blog/sd3#whats-new-with-sd3)
- [Using SD3 with Diffusers](https://huggingface.co/blog/sd3#using-sd3-with-diffusers)
- [Memory optimizations to enable running SD3 on a variety of hardware](https://huggingface.co/blog/sd3#memory-optimizations-for-sd3)
- [Performance optimizations to speed things up](https://huggingface.co/blog/sd3#performance-optimizations-for-sd3)
- [Finetuning and creating LoRAs for SD3](https://huggingface.co/blog/sd3#dreambooth-and-lora-fine-tuning)

## SD3 有什么新东西？

### 模型

SD3 是一个潜在扩散模型，由三个不同的文本编码器（[CLIP L/14](https://huggingface.co/openai/clip-vit-large-patch14)、[OpenCLIP bigG/14](https://huggingface.co/laion/CLIP-ViT-bigG-14-laion2B-39B-b160k) 与 [T5-v1.1-XXL](https://huggingface.co/google/t5-v1_1-xxl)）、一个新颖的多模态扩散 Transformer（MMDiT）模型，以及一个与 [Stable Diffusion XL](https://arxiv.org/abs/2307.01952) 所用类似的 16 通道 AutoEncoder 模型组成。

SD3 以嵌入序列的形式处理文本输入与像素潜变量。位置编码被加到潜变量的 2x2 patch 上，随后展平为 patch 编码序列。这一序列与文本编码序列一起送入 MMDiT 块：在那里被嵌入到共同维度、拼接，再通过一系列带调制的注意力与 MLP。

为了照顾两种模态的差异，MMDiT 块使用两套独立的权重，把文本与图像序列嵌入到共同维度。这些序列在注意力运算前汇合，让两种表征各自在自己的空间中工作，同时在注意力运算中兼顾对方。这种文本与图像数据之间的双向信息流，不同于以往的文生图方法——后者通过交叉注意力把文本信息以固定的文本表征注入潜变量。

SD3 还把来自两个 CLIP 模型的池化文本嵌入用于时间步条件（timestep conditioning）。这些嵌入先被拼接、加到时间步嵌入中，然后传给每个 MMDiT 块。

### 用 Rectified Flow Matching 训练

除架构改动外，SD3 还采用[条件流匹配（conditional flow-matching）目标进行训练](https://arxiv.org/html/2403.03206v1#S2)。在这一方法中，前向加噪过程被定义为连接数据分布与噪声分布的[直线流（rectified flow）](https://arxiv.org/html/2403.03206v1#S3)。

rectified flow-matching 的采样过程更简单，在减少采样步数时表现也好。为支持 SD3 推理，我们引入了一个新调度器（`FlowMatchEulerDiscreteScheduler`），采用 rectified flow-matching 公式与 Euler 方法步。它还通过 `shift` 参数实现依赖分辨率的时间步调度偏移。提高 `shift` 值能更好地处理更高分辨率的噪声缩放。对 2B 模型建议使用 `shift=3.0`。

想快速体验 SD3，请参考下面的应用：

## 在 Diffusers 中使用 SD3

要在 Diffusers 中使用 SD3，请先升级到最新的 Diffusers 版本。

```
pip install --upgrade diffusers
```

由于该模型是受限（gated）的，在用 `diffusers` 使用它之前，你需要先到 [Stable Diffusion 3 Medium 的 Hugging Face 页面](https://huggingface.co/stabilityai/stable-diffusion-3-medium-diffusers)填写表格并接受许可。通过后需要登录，让系统知道你已获得访问权。用下面的命令登录：

```
huggingface-cli login
```

下面的代码片段会以 `fp16` 精度下载 SD3 的 2B 参数版本。这正是 Stability AI 发布的原始 checkpoint 的格式，也是推荐的推理方式。

### 文生图

```
import torch
from diffusers import StableDiffusion3Pipeline

pipe = StableDiffusion3Pipeline.from_pretrained(
    "stabilityai/stable-diffusion-3-medium-diffusers", torch_dtype=torch.float16
).to("cuda")

image = pipe(
    "A cat holding a sign that says hello world",
    negative_prompt="",
    num_inference_steps=28,
    guidance_scale=7.0,
).images[0]
image
```

[![hello_world_cat](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/sd3/hello_world_cat.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/sd3/hello_world_cat.png)

### 图生图

```
import torch
from diffusers import StableDiffusion3Img2ImgPipeline
from diffusers.utils import load_image

pipe = StableDiffusion3Img2ImgPipeline.from_pretrained(
    "stabilityai/stable-diffusion-3-medium-diffusers", torch_dtype=torch.float16
).to("cuda")

init_image = load_image("https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/cat.png")
prompt = "cat wizard, gandalf, lord of the rings, detailed, fantasy, cute, adorable, Pixar, Disney, 8k"
image = pipe(prompt, image=init_image).images[0]
image
```

[![wizard_cat](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/sd3/wizard_cat.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/sd3/wizard_cat.png)

SD3 文档见[这里](https://huggingface.co/docs/diffusers/main/en/api/pipelines/stable_diffusion/stable_diffusion_3)。

## SD3 的显存优化

SD3 使用三个文本编码器，其中一个是超大的 [T5-XXL 模型](https://huggingface.co/google/t5-v1_1-xxl)。即使使用 `fp16` 精度，在 VRAM 低于 24GB 的 GPU 上运行它也很吃力。

为应对这一点，Diffusers 集成自带了显存优化，让 SD3 能在更广的设备上运行。

### 用模型卸载做推理

Diffusers 中最基础的显存优化，允许你在推理期间把模型组件卸载到 CPU 以节省显存，代价是推理延迟略有增加。模型卸载只在需要执行某个组件时才把它搬上 GPU，其余组件留在 CPU。

```
import torch
from diffusers import StableDiffusion3Pipeline

pipe = StableDiffusion3Pipeline.from_pretrained(
    "stabilityai/stable-diffusion-3-medium-diffusers", torch_dtype=torch.float16
)
pipe.enable_model_cpu_offload()

prompt = "smiling cartoon dog sits at a table, coffee mug on hand, as a room goes up in flames. “This is fine,” the dog assures himself."
image = pipe(prompt).images[0]
```

### 推理时丢弃 T5 文本编码器

[在推理时移除内存密集的 4.7B 参数 T5-XXL 文本编码器](https://arxiv.org/html/2403.03206v1#S5.F9)，可以显著降低 SD3 的显存需求，而性能只有轻微损失。

```
import torch
from diffusers import StableDiffusion3Pipeline

pipe = StableDiffusion3Pipeline.from_pretrained(
    "stabilityai/stable-diffusion-3-medium-diffusers",
    text_encoder_3=None, 
    tokenizer_3=None, 
    torch_dtype=torch.float16
).to("cuda")

prompt = "smiling cartoon dog sits at a table, coffee mug on hand, as a room goes up in flames. “This is fine,” the dog assures himself."
image = pipe(prompt).images[0]
```

## 使用 T5-XXL 模型的量化版本

你可以用 `bitsandbytes` 库以 8-bit 加载 T5-XXL 模型，进一步降低显存需求。

```
import torch
from diffusers import StableDiffusion3Pipeline
from transformers import T5EncoderModel, BitsAndBytesConfig

# Make sure you have `bitsandbytes` installed.
quantization_config = BitsAndBytesConfig(load_in_8bit=True)

model_id = "stabilityai/stable-diffusion-3-medium-diffusers"
text_encoder = T5EncoderModel.from_pretrained(
    model_id,
    subfolder="text_encoder_3",
    quantization_config=quantization_config,
)
pipe = StableDiffusion3Pipeline.from_pretrained(
    model_id,
    text_encoder_3=text_encoder,
    device_map="balanced",
    torch_dtype=torch.float16
)
```

*完整代码片段见[这里](https://gist.github.com/sayakpaul/82acb5976509851f2db1a83456e504f1)。*

### 显存优化汇总

所有基准测试均在 80GB VRAM 的 A100 GPU 上用 SD3 的 2B 版本、`fp16` 精度与 PyTorch 2.3 进行。

显存基准使用 3 轮 pipeline 调用做预热，并报告 10 轮 pipeline 调用的平均推理时间。我们使用 [`StableDiffusion3Pipeline` `__call__()` 方法](https://github.com/huggingface/diffusers/blob/adc31940a9cedbbe2fca8142d09bb81db14a8a52/src/diffusers/pipelines/stable_diffusion_3/pipeline_stable_diffusion_3.py#L634)的默认参数。

| **Technique** | **Inference Time (secs)** | **Memory (GB)** |
| --- | --- | --- |
| Default | 4.762 | 18.765 |
| Offloading | 32.765 (~6.8x 🔼) | 12.0645 (~1.55x 🔽) |
| Offloading + no T5 | 19.110 (~4.013x 🔼) | 4.266 (~4.398x 🔽) |
| 8bit T5 | 4.932 (~1.036x 🔼) | 10.586 (~1.77x 🔽) |

## SD3 的性能优化

为提升推理延迟，可以用 `torch.compile()` 为 `vae` 与 `transformer` 组件获得优化的计算图。

```
import torch
from diffusers import StableDiffusion3Pipeline

torch.set_float32_matmul_precision("high")

torch._inductor.config.conv_1x1_as_mm = True
torch._inductor.config.coordinate_descent_tuning = True
torch._inductor.config.epilogue_fusion = False
torch._inductor.config.coordinate_descent_check_all_directions = True

pipe = StableDiffusion3Pipeline.from_pretrained(
    "stabilityai/stable-diffusion-3-medium-diffusers",
    torch_dtype=torch.float16
).to("cuda")
pipe.set_progress_bar_config(disable=True)

pipe.transformer.to(memory_format=torch.channels_last)
pipe.vae.to(memory_format=torch.channels_last)

pipe.transformer = torch.compile(pipe.transformer, mode="max-autotune", fullgraph=True)
pipe.vae.decode = torch.compile(pipe.vae.decode, mode="max-autotune", fullgraph=True)

# Warm Up
prompt = "a photo of a cat holding a sign that says hello world",
for _ in range(3):
    _ = pipe(prompt=prompt, generator=torch.manual_seed(1))

# Run Inference
image = pipe(prompt=prompt, generator=torch.manual_seed(1)).images[0]
image.save("sd3_hello_world.png")
```

*完整脚本见[这里](https://gist.github.com/sayakpaul/508d89d7aad4f454900813da5d42ca97)。*

我们在单台 80GB A100 上用 `fp16` 精度与 PyTorch 2.3 对 SD3 的 `torch.compile()` 做了性能基准。我们运行 10 轮 20 个扩散步的 pipeline 推理调用。发现编译后的模型平均推理时间为 **0.585 秒**，*比 eager 执行快 4 倍*。

## Dreambooth 与 LoRA 微调

此外，我们提供了一个基于 [LoRA](https://huggingface.co/blog/lora) 的 SD3 [DreamBooth](https://dreambooth.github.io/) 微调脚本。该脚本可高效微调 SD3，同时可作为实现 rectified flow 训练流水线的参考。rectified flow 的其他流行实现包括 [minRF](https://github.com/cloneofsimo/minRF/)。

要开始使用脚本，先确保环境正确并有 demo 数据集（例如[这个](https://huggingface.co/datasets/diffusers/dog-example)）。细节见[这里](https://github.com/huggingface/diffusers/blob/main/examples/dreambooth/README_sd3.md)。安装 `peft` 与 `bitsandbytes`，然后就可以出发：

```
export MODEL_NAME="stabilityai/stable-diffusion-3-medium-diffusers"
export INSTANCE_DIR="dog"
export OUTPUT_DIR="dreambooth-sd3-lora"

accelerate launch train_dreambooth_lora_sd3.py \
  --pretrained_model_name_or_path=${MODEL_NAME}  \
  --instance_data_dir=${INSTANCE_DIR} \
  --output_dir=/raid/.cache/${OUTPUT_DIR} \
  --mixed_precision="fp16" \
  --instance_prompt="a photo of sks dog" \
  --resolution=1024 \
  --train_batch_size=1 \
  --gradient_accumulation_steps=4 \
  --learning_rate=1e-5 \
  --report_to="wandb" \
  --lr_scheduler="constant" \
  --lr_warmup_steps=0 \
  --max_train_steps=500 \
  --weighting_scheme="logit_normal" \
  --validation_prompt="A photo of sks dog in a bucket" \
  --validation_epochs=25 \
  --seed="0" \
  --push_to_hub
```

## 致谢

感谢 Stability AI 团队造就了 Stable Diffusion 3 并给予我们早期访问权限。感谢 [Linoy](https://huggingface.co/linoyts) 帮助我们设计博文缩略图。
