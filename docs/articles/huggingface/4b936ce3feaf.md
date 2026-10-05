---
vendor: huggingface
title: 开源 SD-Small 与 SD-Tiny 的知识蒸馏代码与权重
original_title: Open-sourcing Knowledge Distillation Code and Weights of SD-Small and SD-Tiny
url: https://huggingface.co/blog/sd_distillation
date: 2024-10-08
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

本文另有 [简体中文](https://huggingface.co/blog/zh/sd_distillation) 版本。

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/distill_sd/Picture1.png)

近来，AI 社区见证了一波模型发展的狂潮：更大更高性能的模型不断涌现，语言模型方面有 Falcon 40B、LLaMa-2 70B、MPT 30B，图像领域有 SD2.1、SDXL 等。这些进展无疑拓展了 AI 能力的边界，带来高度多面、最先进的图像生成与语言理解能力。然而，在赞叹这些模型威力与复杂度的同时，我们必须认识到：让 AI 模型更小、更高效、更易获取的需求正日益增长——尤其要通过开源来实现。

在 [Segmind](https://www.segmind.com/models)，我们一直在研究如何让生成式 AI 模型更快、更便宜。去年我们开源了加速版 SD-WebUI 库 [voltaML](https://github.com/VoltaML/voltaML-fast-stable-diffusion)——一个基于 AITemplate/TensorRT 的推理加速库，推理速度提升了 4-6 倍。沿着「让生成模型更快、更小、更便宜」的目标，我们现在开源压缩版 **SD 模型的权重与训练代码：SD-Small 和 SD-Tiny**。预训练 checkpoint 已在 [Huggingface 🤗](https://huggingface.co/segmind) 提供。

## 知识蒸馏

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/distill_sd/Picture2.png)

我们的新压缩模型基于知识蒸馏（KD）技术训练，主体工作以[这篇论文](https://openreview.net/forum?id=bOVydU0XKC)为基础。作者提出了一种块移除（Block-removal）知识蒸馏方法：去掉部分 UNet 层，然后训练学生模型的权重。使用论文中描述的 KD 方法，我们借助 [🧨 diffusers](https://github.com/huggingface/diffusers) 库训练出两个压缩模型——**Small** 与 **Tiny**——参数量分别比基座模型少 35% 和 55%，同时实现了与基座模型相当的图像保真度。我们的蒸馏代码已在该 [仓库](https://github.com/segmind/distill-sd)开源，预训练 checkpoint 在 [Huggingface 🤗](https://huggingface.co/segmind)。

用知识蒸馏训练神经网络，类似老师一步步指导学生。先用海量数据预训练一个大教师模型，然后让一个小模型在较小的数据集上训练，既按经典方式学习数据集，又模仿大模型的输出。

在这种特定的知识蒸馏中，学生模型接受的训练是完成常规的扩散任务——从纯噪声中还原图像，同时让输出匹配更大的教师模型。输出的匹配在 U-Net 的每个块上进行，因此模型质量基本得以保留。沿用之前的比喻，可以说在这种蒸馏中，学生不仅从问答中学习，还从老师的答案以及一步步得到答案的方法中学习。我们的损失函数为此包含 3 个部分：首先是传统损失——目标图像的 latents 与生成图像 latents 之间；其次是教师生成图像 latents 与学生生成图像 latents 之间的损失；最后也是最重要的部分是特征级损失——教师与学生每个块输出之间的损失。

把这一切组合起来，就构成了知识蒸馏训练。下面是论文中所述 KD 使用的块移除 UNet 架构。

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/distill_sd/Picture3.png)

图片取自 Shinkook 等人的论文 ["On Architectural Compression of Text-to-Image Diffusion Models"](https://arxiv.org/abs/2305.15798)

我们选取 [Realistic-Vision 4.0](https://huggingface.co/SG161222/Realistic_Vision_V4.0_noVAE) 作为基座教师模型，在 [LAION Art Aesthetic 数据集](https://huggingface.co/datasets/recastai/LAION-art-EN-improved-captions)中图像评分高于 7.5 的子集上训练——因为它们有高质量的图像描述。与论文不同，我们选择两个模型各用 100 万张图训练：Small 训练 10 万步，Tiny 训练 12.5 万步。蒸馏训练的代码见[这里](https://github.com/segmind/distill-sd)。

## 模型使用

该模型可以通过 [🧨 diffusers](https://github.com/huggingface/diffusers) 的 DiffusionPipeline 使用：

```
from diffusers import DiffusionPipeline
import torch

pipeline = DiffusionPipeline.from_pretrained("segmind/small-sd", torch_dtype=torch.float16)
prompt = "Portrait of a pretty girl"
negative_prompt = "(deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime:1.4), text, close up, cropped, out of frame, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck"
image = pipeline(prompt, negative_prompt = negative_prompt).images[0]
image.save("my_image.png")
```

## 推理延迟意义上的速度

我们观察到，蒸馏后的模型比原始基座模型快最多 100%。基准测试代码见[这里](https://github.com/segmind/distill-sd/blob/master/inference.py)。

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/distill_sd/Picture4.jpeg)

## 潜在局限

蒸馏模型尚处早期阶段，输出质量可能还未达生产水平。这些模型也许不是最佳的通用模型，更适合在特定概念/风格上做微调或 LoRA 训练后再用。蒸馏模型目前在组合性（composibility）或多概念方面表现还不理想。

## 在肖像数据集上微调 SD-tiny 模型

我们在用 Realistic Vision v4.0 生成的肖像图片上微调了 sd-tiny 模型。所用微调参数如下。

- Steps: 131000
- Learning rate: 1e-4
- Batch size: 32
- Gradient accumulation steps: 4
- Image resolution: 768
- Dataset size - 7k images
- Mixed-precision: fp16

我们以几乎少 40% 的参数实现了接近原模型产出图像的质量，下面的样例结果不言自明：

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/distill_sd/Picture5.png)

微调基座模型的代码见[这里](https://github.com/segmind/distill-sd/blob/master/checkpoint_training.py)。

## LoRA 训练

在蒸馏模型上做 LoRA 训练的一个优势是训练更快。下面是我们在蒸馏模型上针对某些抽象概念训练的第一个 LoRA 的部分图像。LoRA 训练代码见[这里](https://github.com/segmind/distill-sd/blob/master/lora_training.py)。

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/distill_sd/Picture6.png)

## 结论

我们邀请开源社区帮助我们改进这些蒸馏 SD 模型、推动更广泛的采用。欢迎加入我们的 [Discord](https://discord.gg/s6E6eHJk) 服务器，我们将在上面发布这些模型的最新更新、更多 checkpoint 以及一些令人兴奋的新 LoRA。如果你喜欢我们的工作，请在我们的 [Github](https://github.com/segmind/distill-sd) 上点个 star。
