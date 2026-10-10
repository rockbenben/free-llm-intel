---
vendor: huggingface
title: 用 Hugging Face Accelerate 在 DeepSpeed 与 FSDP 间自如切换
original_title: From DeepSpeed to FSDP and Back Again with Hugging Face Accelerate
url: https://huggingface.co/blog/deepspeed-to-fsdp-and-back
date: 2024-12-19
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 84c008643cd0
translator: agent
---

返回文章列表

# Hugging Face Accelerate 的多后端故事：FSDP 与 DeepSpeed

发布于
					2024 年 6 月 13 日

在 GitHub 上更新



- [![](https://huggingface.co/avatars/611a96669ddcd187c298a67ec24a509a.svg)](https://huggingface.co/HammerW)
- [![](https://huggingface.co/avatars/c2b45478a6cd0e614191ab8f73c0173e.svg)](https://huggingface.co/geshijoker)
- [![](https://huggingface.co/avatars/47f09e5d4236a1281b904fcae220ca43.svg)](https://huggingface.co/RobotSail)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6459fa0f5b3111fbe83286e1/E6Buqu8Wd9WmIHKOCZXCc.jpeg)](https://huggingface.co/louisbrulenaudet)
- [![](https://huggingface.co/avatars/5353fa05db1e2f5f4b209f6216dde553.svg)](https://huggingface.co/llm2big)
- [![](https://huggingface.co/avatars/0a6dbfe8a09dc050d4acbd01c2dbd663.svg)](https://huggingface.co/gogo8232)

Yu Chin Fabian Lim

mirinflim

guest

aldo pareja

aldopareja

guest

Zachary Mueller

muellerzr

Stas Bekman

stas

ContextualAI

本文也有中文版本 [简体中文](https://huggingface.co/blog/zh/deepspeed-to-fsdp-and-back)。

社区里有两种流行的 [ZeRO Redundancy Optimizer（Zero）](https://arxiv.org/abs/1910.02054)算法实现：一种来自 [DeepSpeed](https://github.com/microsoft/DeepSpeed)，另一种来自 [PyTorch](https://pytorch.org/docs/stable/fsdp.html)。Hugging Face [Accelerate](https://huggingface.co/docs/accelerate/en/index) 把这两个框架都暴露给最终用户，用来训练/调优模型。本博客重点说明 Accelerate 暴露这两个后端的方式有何差异。为了让用户能够无缝切换后端，我们[向上游提交了一个与精度相关的改动](https://github.com/huggingface/accelerate/issues/2624)，并写了一份[概念指南](https://huggingface.co/docs/accelerate/concept_guides/fsdp_and_deepspeed)。

## FSDP 和 DeepSpeed 可以互换吗？

最近，我们尝试分别用 DeepSpeed 和 PyTorch FSDP 跑同一条训练流水线，发现得到的结果不同。具体模型是 Mistral-7B base，以半精度（`bfloat16`）加载。DeepSpeed（蓝色）的 loss 收敛得很好，而 FSDP（橙色）的 loss 却迟迟不降，如图 1 所示。

[![Figure 1](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/deepspeed-to-fsdp-and-back/figure_1.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/deepspeed-to-fsdp-and-back/figure_1.png)

我们猜测学习率可能需要按 GPU 数量缩放，于是把学习率提高了 4 倍（因为我们用了 4 块 GPU）。之后得到了图 2 所示的 loss 表现。

[![Figure 2](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/deepspeed-to-fsdp-and-back/figure_2.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/deepspeed-to-fsdp-and-back/figure_2.png)

看起来，把 FSDP 的学习率按 GPU 数量缩放就达到了想要的效果！不过，当我们换用另一个未缩放的学习率（`1e-5`）时，观察到两个框架的 loss 和梯度范数特性都差不多，如图 3 所示。

[![Figure 3](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/deepspeed-to-fsdp-and-back/figure_3.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/deepspeed-to-fsdp-and-back/figure_3.png)

## 精度很重要

在 `DeepSpeed` 代码库内部，具体是实现 `DeepSpeedZeroOptimizer_Stage3` 的地方（顾名思义，它负责 Stage 3 的优化器分片），我们发现 `trainable_param_groups`（被训练的参数组）会经过一个内部的 `_setup_for_real_optimizer` 函数调用，该函数又会调用一个叫 `_create_fp32_partitions` 的函数。从名字里的 `fp32` 就能看出，`DeepSpeed` 在内部做了上转换（upcast），按设计始终把主权重（master weights）保持在 `fp32`。上转到全精度意味着优化器能在一些低精度下无法收敛的学习率上正常收敛。前面的那些观察其实是这个精度差异造成的假象。

在 FSDP 中，模型和优化器参数在分发到各 GPU 之前，会先被“展平”（flatten）成一维张量。FSDP 和 DeepSpeed 对这些“展平”参数使用的 `dtype` 不同，而这会影响 PyTorch 优化器的行为。表 1 列出了两个框架的流程；“Local”列表示该过程在每个 GPU 上独立发生，因此上转换带来的内存开销会被 GPU 数量摊薄。

| **过程** | **是否 Local？** | **框架** | **细节** |
| --- | --- | --- | --- |
| 加载模型（如 `AutoModel.from_pretrained(..., torch_dtype=torch_dtype)`） | ❌ |  |  |
| 准备工作，如创建“展平参数” | ✅ | FSDP DeepSpeed | 使用 `torch_dtype` 忽略 `torch_dtype`，以 `float32` 创建 |
| 优化器初始化 | ✅ | FSDP DeepSpeed | 以 `torch_dtype` 创建参数 以 `float32` 创建参数 |
| 训练步（前向、反向、归约） | ❌ | FSDP DeepSpeed | 遵循 [fsdp.MixedPrecision](https://pytorch.org/docs/stable/fsdp.html#torch.distributed.fsdp.MixedPrecision) 遵循 `deepspeed_config_file` 的混合精度设置 |
| 优化器（步前） | ✅ | FSDP DeepSpeed | 上转换（如有）到 `torch_dtype` 全部上转换到 `float32` |
| 优化器（实际执行步） | ✅ | FSDP DeepSpeed | 以 `torch_dtype` 执行 以 `float32` 执行 |

> 表 1：FSDP 与 DeepSpeed 处理混合精度的方式总结

几个要点：

- 正如一个 [🤗 Accelerate issue](https://github.com/huggingface/accelerate/issues/2624#issuecomment-2058402753) 指出的，做混合精度时有一条经验法则：可训练参数保持在 `float32`。
- 像 `DeepSpeed` 那样做上转换，在大量 GPU 上分片时对内存占用影响不大。但在少量 GPU 上使用 `DeepSpeed` 时，内存占用翻倍就可能很可观。
- FSDP 的 torch 原生实现不强制上转换，允许用户以低精度运行 PyTorch 优化器。这比 `DeepSpeed` 的原生上转换更灵活。

## 在 🤗 Accelerate 中统一 DeepSpeed 与 FSDP

为了让 DeepSpeed 和 FSDP 在 🤗 Accelerate 中更好对齐，我们可以在启用混合精度时自动为 FSDP 做上转换。我们提交了一个包含该改动的 pull request，已随 [0.30.0 版本](https://github.com/huggingface/accelerate/releases/tag/v0.30.0)发布。

[![Figure 4](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/deepspeed-to-fsdp-and-back/figure_4.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/deepspeed-to-fsdp-and-back/figure_4.png)

这个 PR 的效果是让 FSDP 支持两种模式：

- 与 DeepSpeed 对应的“混合精度”模式
- 面向内存受限场景的低精度模式，如图 4 所示。

FSDP 的这两种新模式总结在表 2 中，并与 DeepSpeed 做了对比。

| **框架** | **模型加载（`torch_dtype`）** | **混合精度** | **准备工作（Local）** | **训练** | **优化器（Local）** |
| --- | --- | --- | --- | --- | --- |
| FSDP（内存受限） | `bf16` | 默认（无） | `bf16` | `bf16` | `bf16` |
| FSDP（混合精度模式） | `bf16` | `bf16` | `fp32` | `bf16` | `fp32` |
| DeepSpeed | `bf16` | `bf16` | `fp32` | `bf16` | `fp32` |

> 表 2：FSDP 两种新模式总结及与 DeepSpeed 的对比

## 吞吐量结果

我们用 [IBM Granite 7B](https://huggingface.co/ibm-granite/granite-7b-base) 模型（架构与 Meta Llama2 相同）做吞吐量对比，比较 Model Flops Utilization（MFU，模型算力利用率）和 tokens/sec/GPU 两个指标，分别展示 FSDP（完全分片）和 DeepSpeed（Zero3）的结果。

和之前一样使用 4 块 A100 GPU，超参数如下：

- Batch size 为 8
- 模型以 `torch.bfloat16` 加载
- 混合精度使用相同 dtype。

表 3 显示 FSDP 与 DeepSpeed 的预期表现相近。

> 我们后续打算做一次更全面的吞吐量对比，并介绍提升吞吐量的方法（如带 packing 的 4D mask、torch.compile、选择性激活检查点），因为 InstructLab、GLAN 这类大规模对齐技术正变得流行。

| **框架** | **每秒每设备 tokens** | **步长耗时（秒）** | **Model Flops Utilization（MFU）** |
| --- | --- | --- | --- |
| FSDP（对齐模式） | 3158.7 | 10.4 | 0.41 |
| DeepSpeed | 3094.5 | 10.6 | 0.40 |

> 表 3：FSDP 与 DeepSpeed 在 4 块 A100 GPU 上的吞吐量概算对比

## 写在最后

我们提供了一份[新概念指南](https://huggingface.co/docs/accelerate/v0.31.0/en/concept_guides/fsdp_and_deepspeed)，帮助用户在两个框架之间迁移。这份指南可以回答这些问题：

- 如何配置出等效的分片策略？
- 如何高效地加载模型？
- FSDP 和 DeepSpeed 的权重预取是如何管理的？
- DeepSpeed 中什么相当于 FSDP 的 wrapping？

在 🤗 Accelerate 中，我们可以通过多种方式配置这两个框架：

- 在命令行 `accelerate launch` 时配置
- 使用 🤗 Accelerate 提供的各种 `Plugin` 类，分别针对 (`DeepSpeed`)[[https://huggingface.co/docs/accelerate/main/en/package_reference/deepspeed]](https://huggingface.co/docs/accelerate/main/en/package_reference/deepspeed%5D) 和 (`FSDP`)[[https://huggingface.co/docs/accelerate/main/en/package_reference/fsdp]](https://huggingface.co/docs/accelerate/main/en/package_reference/fsdp%5D)

🤗 Accelerate 让 FSDP 与 DeepSpeed 之间的切换几乎**毫不费力**，大部分工作只是改一下 Accelerate 配置文件（具体操作见新概念指南）。

除了改配置，还有一些其他注意事项（指南中也有说明），比如 checkpoint 处理方式的差异等。

本博客中的所有实验都可以用[原始 🤗 Accelerate issue](https://github.com/huggingface/accelerate/issues/2624) 中的代码复现。

我们后续打算跟进更大规模的吞吐量对比，以及在不损失模型质量的前提下，更好地利用 GPU 做微调和任务的技术。

## 致谢

这项工作是跨多个组织的几个团队协作的成果。它始于 IBM Research，具体是 Aldo Pareja 发现了这个问题，Fabian Lim 找到了精度差异并修复了它。Zach Mueller 和 [Stas Bekman](https://github.com/stas00) 为 accelerate 提供了出色的反馈和修复。Meta PyTorch 团队的 Less Wright 在 FSDP 参数方面给予了很大帮助。最后，也要感谢 [DeepSpeed](https://www.deepspeed.ai/) 团队对本博客提出的反馈。

## 本文提到的 Models 1

我们博客的更多文章

research

nlp

open-source

## 用 Self-Speculative Decoding 加速文本生成

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/608aabf24955d2bfc3cd99c6/-YxmtpzEmf3NKOTktODRP.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/63c9725ebedad7e2bf160bdc/wzPuyhOXCYBNGwZDshbnL.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1655385361868-61b85ce86eb1f2c5e6233736.jpeg)

67

2024 年 11 月 20 日

research

nlp

open-source

## Universal Assisted Generation：用任意助手模型加速解码

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6055ae5d25cd24537dd59dc5/eswozkCirLrnyhufN8_-f.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1664643955283-60570320cbe9c7542f3501e3.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/63e0c8875c6964861ebb0c49/yzkhPSxgXtJCM62iMBOOK.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/606d6349f1259f30578520ad/72_XrFfgQ6p9tgJj5Bc5U.png)
- +4

62

2024 年 10 月 29 日

### 社区

将图片、音频和视频拖到输入框、粘贴，或

点击这里

上传。

点击或粘贴到这里上传图片

· [注册](https://huggingface.co/join?next=%2Fblog%2Fdeepspeed-to-fsdp-and-back)或[登录](https://huggingface.co/login?next=%2Fblog%2Fdeepspeed-to-fsdp-and-back)即可评论



- [![](https://huggingface.co/avatars/611a96669ddcd187c298a67ec24a509a.svg)](https://huggingface.co/HammerW)
- [![](https://huggingface.co/avatars/c2b45478a6cd0e614191ab8f73c0173e.svg)](https://huggingface.co/geshijoker)
- [![](https://huggingface.co/avatars/47f09e5d4236a1281b904fcae220ca43.svg)](https://huggingface.co/RobotSail)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6459fa0f5b3111fbe83286e1/E6Buqu8Wd9WmIHKOCZXCc.jpeg)](https://huggingface.co/louisbrulenaudet)
- [![](https://huggingface.co/avatars/5353fa05db1e2f5f4b209f6216dde553.svg)](https://huggingface.co/llm2big)
- [![](https://huggingface.co/avatars/0a6dbfe8a09dc050d4acbd01c2dbd663.svg)](https://huggingface.co/gogo8232)
- [![](https://huggingface.co/avatars/4faff084ae3495a28dd1ae26b7608386.svg)](https://huggingface.co/aldopareja)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1594311341799-5f07383b19cb630495b812cd.jpeg)](https://huggingface.co/stas)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/62f47c093561a52aa5a67c90/d4sFnllrLH5BWbZDRNvMn.jpeg)](https://huggingface.co/rootacess)
- [![](https://huggingface.co/avatars/c32741e7fc57c9a08722fab3877a7b81.svg)](https://huggingface.co/tjruwase)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1639773384591-5f353bb37e58354338621655.jpeg)](https://huggingface.co/nbroad)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/651e93137b2a2e027f9e55df/5oXWJeEDCrMJLA4s_0I93.png)](https://huggingface.co/Aurelien-Morgan)

## 本文提到的 Models 1
