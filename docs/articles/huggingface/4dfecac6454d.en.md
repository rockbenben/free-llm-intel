---
vendor: huggingface
title: 🧨 Diffusers welcomes Stable Diffusion 3
original_title: Diffusers welcomes Stable Diffusion 3
url: https://huggingface.co/blog/sd3
date: 2023-01-24
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: a1497d212bdd
---


# 🧨 Diffusers welcomes Stable Diffusion 3

					June 12, 2024

Update on GitHub


99

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6640bbd0220cfa8cbfdce080/wiAHUu5ewawyipNs0YFBR.png)](https://huggingface.co/John6666)
- [![](https://huggingface.co/avatars/0e9c6507b999f7eedb86463482b967a7.svg)](https://huggingface.co/moeinshariatnia)
- [![](https://huggingface.co/avatars/42edbf9018f41a07a3bd1dcf0e5c1e49.svg)](https://huggingface.co/zheyishine)
- [![](https://huggingface.co/avatars/a3565133c0e9e4c09f646ec38f1690cd.svg)](https://huggingface.co/Zer0Nin3r)
- [![](https://huggingface.co/avatars/a607674492c0aedd4096df680c4d1883.svg)](https://huggingface.co/xiaolong01)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6032802e1f993496bc14d9e3/w6hr-DEQot4VVkoyRIBiy.png)](https://huggingface.co/osanseviero)

Dhruv Nair

dn6

YiYi Xu

YiYiXu

Sayak Paul

sayakpaul

Alvaro Somoza

OzzyGT

Kashif Rasul

kashif

Apolinário from multimodal AI art

multimodalart

This article is also available in Chinese [简体中文](https://huggingface.co/blog/zh/sd3).

[Stable Diffusion 3](https://stability.ai/news/stable-diffusion-3-research-paper) (SD3), Stability AI’s latest iteration of the Stable Diffusion family of models, is now available on the Hugging Face Hub and can be used with 🧨 Diffusers.

The model released today is Stable Diffusion 3 Medium, with 2B parameters.

As part of this release, we have provided:

- Models on the Hub
- Diffusers Integration
- SD3 Dreambooth and LoRA training scripts

## Table Of Contents

- [What’s new with SD3](https://huggingface.co/blog/sd3#whats-new-with-sd3)
- [Using SD3 with Diffusers](https://huggingface.co/blog/sd3#using-sd3-with-diffusers)
- [Memory optimizations to enable running SD3 on a variety of hardware](https://huggingface.co/blog/sd3#memory-optimizations-for-sd3)
- [Performance optimizations to speed things up](https://huggingface.co/blog/sd3#performance-optimizations-for-sd3)
- [Finetuning and creating LoRAs for SD3](https://huggingface.co/blog/sd3#dreambooth-and-lora-fine-tuning)

## What’s New With SD3?

### Model

SD3 is a latent diffusion model that consists of three different text encoders ([CLIP L/14](https://huggingface.co/openai/clip-vit-large-patch14), [OpenCLIP bigG/14](https://huggingface.co/laion/CLIP-ViT-bigG-14-laion2B-39B-b160k), and [T5-v1.1-XXL](https://huggingface.co/google/t5-v1_1-xxl)), a novel Multimodal Diffusion Transformer (MMDiT) model, and a 16 channel AutoEncoder model that is similar to the one used in [Stable Diffusion XL](https://arxiv.org/abs/2307.01952).

SD3 processes text inputs and pixel latents as a sequence of embeddings. Positional encodings are added to 2x2 patches of the latents which are then flattened into a patch encoding sequence. This sequence, along with the text encoding sequence are fed into the MMDiT blocks, where they are embedded to a common dimensionality, concatenated, and passed through a sequence of modulated attentions and MLPs.

In order to account for the differences between the two modalities, the MMDiT blocks use two separate sets of weights to embed the text and image sequences to a common dimensionality. These sequences are joined before the attention operation, which allows both representations to work in their own space while taking the other one into account during the attention operation. This two-way flow of information between text and image data differs from previous approaches for text-to-image synthesis, where text information is incorporated into the latent via cross-attention with a fixed text representation.

SD3 also makes use of the pooled text embeddings from both its CLIP models as part of its timestep conditioning. These embeddings are first concatenated and added to the timestep embedding before being passed to each of the MMDiT blocks.

### Training with Rectified Flow Matching

In addition to architectural changes, SD3 applies a [conditional flow-matching objective to train the model](https://arxiv.org/html/2403.03206v1#S2). In this approach, the forward noising process is defined as a [rectified flow](https://arxiv.org/html/2403.03206v1#S3) that connects the data and noise distributions on a straight line.

The rectified flow-matching sampling process is simpler and performs well when reducing the number of sampling steps. To support inference with SD3, we have introduced a new scheduler (`FlowMatchEulerDiscreteScheduler`) with a rectified flow-matching formulation and Euler method steps. It also implements resolution-dependent shifting of the timestep schedule via a `shift` parameter. Increasing the `shift` value handles noise scaling better for higher resolutions. It is recommended to use `shift=3.0` for the 2B model.

To quickly try out SD3, refer to the application below:

## Using SD3 with Diffusers

To use SD3 with Diffusers, make sure to upgrade to the latest Diffusers release.

```
pip install --upgrade diffusers
```

As the model is gated, before using it with `diffusers` you first need to go to the [Stable Diffusion 3 Medium Hugging Face page](https://huggingface.co/stabilityai/stable-diffusion-3-medium-diffusers), fill in the form and accept the gate. Once you are in, you need to log in so that your system knows you’ve accepted the gate. Use the command below to log in:

```
huggingface-cli login
```

The following snippet will download the 2B parameter version of SD3 in `fp16` precision. This is the format used in the original checkpoint published by Stability AI, and is the recommended way to run inference.

### Text-To-Image

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

### Image-To-Image

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

You can check out the SD3 documentation [here](https://huggingface.co/docs/diffusers/main/en/api/pipelines/stable_diffusion/stable_diffusion_3).

## Memory Optimizations for SD3

SD3 uses three text encoders, one of which is the very large [T5-XXL model](https://huggingface.co/google/t5-v1_1-xxl). This makes running the model on GPUs with less than 24GB of VRAM challenging, even when using `fp16` precision.

To account for this, the Diffusers integration ships with memory optimizations that allow SD3 to be run on a wider range of devices.

### Running Inference with Model Offloading

The most basic memory optimization available in Diffusers allows you to offload the components of the model to the CPU during inference in order to save memory while seeing a slight increase in inference latency. Model offloading will only move a model component onto the GPU when it needs to be executed while keeping the remaining components on the CPU.

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

### Dropping the T5 Text Encoder during Inference

[Removing the memory-intensive 4.7B parameter T5-XXL text encoder during inference](https://arxiv.org/html/2403.03206v1#S5.F9) can significantly decrease the memory requirements for SD3 with only a slight loss in performance.

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

## Using A Quantized Version of the T5-XXL Model

You can load the T5-XXL model in 8 bits using the `bitsandbytes` library to reduce the memory requirements further.

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

*You can find the full code snippet [here](https://gist.github.com/sayakpaul/82acb5976509851f2db1a83456e504f1).*

### Summary of Memory Optimizations

All benchmarking runs were conducted using the 2B version of the SD3 model on an A100 GPU with 80GB of VRAM using `fp16` precision and PyTorch 2.3.

For our memory benchmarks, we use 3 iterations of pipeline calls for warming up and report an average inference time of 10 iterations of pipeline calls. We use the default arguments of the [`StableDiffusion3Pipeline` `__call__()` method](https://github.com/huggingface/diffusers/blob/adc31940a9cedbbe2fca8142d09bb81db14a8a52/src/diffusers/pipelines/stable_diffusion_3/pipeline_stable_diffusion_3.py#L634).

| **Technique** | **Inference Time (secs)** | **Memory (GB)** |
| --- | --- | --- |
| Default | 4.762 | 18.765 |
| Offloading | 32.765 (~6.8x 🔼) | 12.0645 (~1.55x 🔽) |
| Offloading + no T5 | 19.110 (~4.013x 🔼) | 4.266 (~4.398x 🔽) |
| 8bit T5 | 4.932 (~1.036x 🔼) | 10.586 (~1.77x 🔽) |

## Performance Optimizations for SD3

To boost inference latency, we can use `torch.compile()` to obtain an optimized compute graph of the `vae` and the `transformer` components.

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

*Refer [here](https://gist.github.com/sayakpaul/508d89d7aad4f454900813da5d42ca97) for the full script.*

We benchmarked the performance of `torch.compile()`on SD3 on a single 80GB A100 machine using `fp16` precision and PyTorch 2.3. We ran 10 iterations of a pipeline inference call with 20 diffusion steps. We found that the average inference time with the compiled versions of the models was **0.585 seconds,** *a 4X speed up over eager execution*.

## Dreambooth and LoRA fine-tuning

Additionally, we’re providing a [DreamBooth](https://dreambooth.github.io/) fine-tuning script for SD3 leveraging [LoRA](https://huggingface.co/blog/lora). The script can be used to efficiently fine-tune SD3 and serves as a reference for implementing rectified flow-based training pipelines. Other popular implementations of rectified flow include [minRF](https://github.com/cloneofsimo/minRF/).

To get started with the script, first, ensure you have the right setup and a demo dataset available (such as [this one](https://huggingface.co/datasets/diffusers/dog-example)). Refer [here](https://github.com/huggingface/diffusers/blob/main/examples/dreambooth/README_sd3.md) for details. Install `peft` and `bitsandbytes` and then we’re good to go:

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

## Acknowledgements

Thanks to the Stability AI team for making Stable Diffusion 3 happen and providing us with its early access. Thanks to [Linoy](https://huggingface.co/linoyts) for helping us with the blogpost thumbnail.

## Models mentioned in this article 4

## Datasets mentioned in this article 1

More Articles from our Blog

guide

diffusers

quantization

## Bringing Nunchaku 4-bit Diffusion Inference to Diffusers

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/655647bf2f76548766fce60f/mZhWuhJb-bzlzp-C3VoO_.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1649681653581-5f7fbd813e94f16a85448745.jpeg)

69

July 23, 2026

peft

lora

guide

## Beyond LoRA: Can you beat the most popular fine-tuning technique?

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1656685953025-62bf03d1e80cec527083cd66.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1649681653581-5f7fbd813e94f16a85448745.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/upIyVlEpqWqoeFTvNzTf5.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1669189789447-629f3b18ee05727ce328ccbe.jpeg)

103

June 18, 2026

### Community

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fsd3) or [log in](https://huggingface.co/login?next=%2Fblog%2Fsd3) to comment


99

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6640bbd0220cfa8cbfdce080/wiAHUu5ewawyipNs0YFBR.png)](https://huggingface.co/John6666)
- [![](https://huggingface.co/avatars/0e9c6507b999f7eedb86463482b967a7.svg)](https://huggingface.co/moeinshariatnia)
- [![](https://huggingface.co/avatars/42edbf9018f41a07a3bd1dcf0e5c1e49.svg)](https://huggingface.co/zheyishine)
- [![](https://huggingface.co/avatars/a3565133c0e9e4c09f646ec38f1690cd.svg)](https://huggingface.co/Zer0Nin3r)
- [![](https://huggingface.co/avatars/a607674492c0aedd4096df680c4d1883.svg)](https://huggingface.co/xiaolong01)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6032802e1f993496bc14d9e3/w6hr-DEQot4VVkoyRIBiy.png)](https://huggingface.co/osanseviero)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1648966381588-6064e095abd8d3692e3e2ed6.jpeg)](https://huggingface.co/radames)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1605114051380-noauth.jpeg)](https://huggingface.co/jeffboudier)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64b695dcd3df8086e5ed7c89/ZULwnPE8Q5q7bxKJsJ7v5.jpeg)](https://huggingface.co/0xFieldsy)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64371b564aacf7bf786fb530/HZl_fPo7YclFEuuLSme3K.png)](https://huggingface.co/Nymbo)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/651e93137b2a2e027f9e55df/5oXWJeEDCrMJLA4s_0I93.png)](https://huggingface.co/Aurelien-Morgan)
- [![](https://huggingface.co/avatars/8011cc6e4a919cb30f30d1be783de6d4.svg)](https://huggingface.co/Rohit311)

## Models mentioned in this article 4

## Datasets mentioned in this article 1
