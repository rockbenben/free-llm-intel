---
vendor: huggingface
title: A Hugging Face Accelerate Story of Multiple Backends: FSDP and DeepSpeed
original_title: From DeepSpeed to FSDP and Back Again with Hugging Face Accelerate
url: https://huggingface.co/blog/deepspeed-to-fsdp-and-back
date: 2024-12-19
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 579a82a3c5bf
---


# A Hugging Face Accelerate Story of Multiple Backends: FSDP and DeepSpeed

					June 13, 2024

Update on GitHub


63

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

This article is also available in Chinese [简体中文](https://huggingface.co/blog/zh/deepspeed-to-fsdp-and-back).

There are two popular implementations of the [ZeRO Redundancy Optimizer (Zero)](https://arxiv.org/abs/1910.02054) algorithm in the community, one from [DeepSpeed](https://github.com/microsoft/DeepSpeed) and the other from [PyTorch](https://pytorch.org/docs/stable/fsdp.html). Hugging Face [Accelerate](https://huggingface.co/docs/accelerate/en/index) exposes both these frameworks for the end users to train/tune their models. This blog highlights the differences between how these backends are exposed through Accelerate. To enable users to seamlessly switch between these backends, we [upstreamed a precision-related change](https://github.com/huggingface/accelerate/issues/2624) and a [concept guide](https://huggingface.co/docs/accelerate/concept_guides/fsdp_and_deepspeed).

## Are FSDP and DeepSpeed Interchangeable?

Recently, we tried running a training pipeline with DeepSpeed and PyTorch FSDP. We noticed that the results obtained differed. The specific model was Mistral-7B base and it was loaded in half-precision (`bfloat16`). While the DeepSpeed (blue) loss had converged well, the FSDP (orange) loss was not decreasing, as can be seen in Figure 1.

[![Figure 1](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/deepspeed-to-fsdp-and-back/figure_1.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/deepspeed-to-fsdp-and-back/figure_1.png)

We hypothesized that the learning rate may need scaling by the number of GPUs and bumped up the learning rate by 4x since we were using 4 GPUs. Then, we saw the following loss behavior, shown in Figure 2.

[![Figure 2](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/deepspeed-to-fsdp-and-back/figure_2.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/deepspeed-to-fsdp-and-back/figure_2.png)

It looked like the desired behavior had been achieved by scaling the FSDP learning rate by the number of GPUs! However, when we tried a different learning rate (`1e-5`) without scaling, we observed similar loss and gradient norm characteristics for both frameworks, shown in Figure 3.

[![Figure 3](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/deepspeed-to-fsdp-and-back/figure_3.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/deepspeed-to-fsdp-and-back/figure_3.png)

## Precision Matters

Inside the `DeepSpeed` codebase, specifically in the implementation of `DeepSpeedZeroOptimizer_Stage3` (as the name implies, what handles doing Stage 3 optimizer sharding), we noticed that the `trainable_param_groups`, the parameter groups being trained on, pass through an internal `_setup_for_real_optimizer` function call, which calls another function called `_create_fp32_partitions`. As the `fp32` in the name suggests, `DeepSpeed` was performing upcasting internally, and it always keeps its master weights in `fp32` by design. This upcasting to full precision meant that the optimizer could converge at learning rates that it would not converge in lower precision. The earlier observations were artifacts of this precision difference.

In FSDP, before the model and optimizer parameters are distributed across GPUs, they are first "flattened" to a one-dimensional tensor. FSDP and DeepSpeed use different `dtype`s for these "flattened" parameters which has ramifications for PyTorch optimizers. Table 1 outlines the processes for both frameworks; the "Local" column indicates the process occurring per-GPU, therefore the memory overhead from upcasting is amortized by the number of GPUs.

| **Process** | **Local?** | **Framework** | **Details** |
| --- | --- | --- | --- |
| Loading the model in (such as `AutoModel.from_pretrained(..., torch_dtype=torch_dtype)`) | ❌ |  |  |
| Preparation, such as creation of the "flattened parameters" | ✅ | FSDP DeepSpeed | utilizes `torch_dtype` disregards `torch_dtype` and is created in `float32` |
| Optimizer initialization | ✅ | FSDP DeepSpeed | creates parameters in `torch_dtype` creates parameters in `float32` |
| Training Step (forward, backward, reduction) | ❌ | FSDP DeepSpeed | follows [fsdp.MixedPrecision](https://pytorch.org/docs/stable/fsdp.html#torch.distributed.fsdp.MixedPrecision) follows `deepspeed_config_file` mixed precision settings |
| Optimizer (pre-step) | ✅ | FSDP DeepSpeed | upcasting (if any) to `torch_dtype` upcasting everything to `float32` |
| Optimizer (actual step) | ✅ | FSDP DeepSpeed | occurs in `torch_dtype` occurs in `float32` |

> Table 1: Summary of how FSDP and DeepSpeed handle mixed precision

A few takeaway points:

- As noted an [🤗 Accelerate issue](https://github.com/huggingface/accelerate/issues/2624#issuecomment-2058402753), a rule of thumb when performing mixed precision is to keep trainable parameters in `float32`.
- Upcasting, as is done in `DeepSpeed`, may have a negligible effect on memory consumption when sharding over a large number of GPUs. However, when using `DeepSpeed` on a small number of GPUs, the 2x increase in memory consumption can be significant.
- The torch-native implementation of FSDP does not force upcasting, allowing a user to operate PyTorch optimizers in low precision. This offers more flexibility than the native upcasting of `DeepSpeed`.

## Harmonizing DeepSpeed and FSDP in 🤗 Accelerate

To better align DeepSpeed and FSDP in 🤗 Accelerate, we can perform upcasting automatically for FSDP when mixed precision is enabled. We created a pull request with this change that was included in the [0.30.0 release](https://github.com/huggingface/accelerate/releases/tag/v0.30.0).

[![Figure 4](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/deepspeed-to-fsdp-and-back/figure_4.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/deepspeed-to-fsdp-and-back/figure_4.png)

The result of this PR is to allow FSDP to operate in two modes:

- A “mixed-precision” mode like the DeepSpeed counterpart
- A low precision mode for memory constrained scenarios, as shown in Figure 4.

The two new FSDP modes are summarized in Table 2 and compared with DeepSpeed.

| **Framework** | **Model Loading (`torch_dtype`)** | **Mixed Precision** | **Preparation (Local)** | **Training** | **Optimizer (Local)** |
| --- | --- | --- | --- | --- | --- |
| FSDP (memory-constrained) | `bf16` | default (none) | `bf16` | `bf16` | `bf16` |
| FSDP (mixed precision mode) | `bf16` | `bf16` | `fp32` | `bf16` | `fp32` |
| DeepSpeed | `bf16` | `bf16` | `fp32` | `bf16` | `fp32` |

> Table 2: Summary of the two new FSDP modes and comparisons with DeepSpeed

## Throughput results

We use the [IBM Granite 7B](https://huggingface.co/ibm-granite/granite-7b-base) model (which follows the Meta Llama2 architecture) for throughput comparisons. We compare Model Flops Utilization (MFU) and tokens/sec/GPU metrics and show them for FSDP (full sharding) and DeepSpeed (Zero3).

We used four A100 GPUs as before with the following hyperparameters:

- Batch size of 8
- Model loaded in `torch.bfloat16`
- Mixed precision is the same dtype.

Table 3 shows that FSDP and DeepSpeed are expected to perform similarly.

> We intend to follow up with a comprehensive throughput comparison and approaches to improve throughput (e.g., 4D masks with packing, torch.compile, selective activation checkpointing) as large scale alignment techniques like InstructLab and GLAN become popular.

| **Framework** | **Tokens / sec / device** | **Step time (s)** | **Model Flops Utilization (MFU)** |
| --- | --- | --- | --- |
| FSDP (aligned mode) | 3158.7 | 10.4 | 0.41 |
| DeepSpeed | 3094.5 | 10.6 | 0.40 |

> Table 3: Ballpark throughput comparisons between FSDP and DeepSpeed on four A100 GPUs.

## Closing thoughts

We provided a [new concept guide](https://huggingface.co/docs/accelerate/v0.31.0/en/concept_guides/fsdp_and_deepspeed) to help users migrate between the two frameworks. The guide helps users answer questions such as:

- How do we achieve equivalent sharding strategies?
- How do we perform efficient model loading?
- How is weight prefetching managed in FSDP and DeepSpeed?
- What is the equivalent of FSDP wrapping in DeepSpeed?

We consider various modes of configuring these frameworks in 🤗 Accelerate,

- From the command line during `accelerate launch`
- From the various `Plugin` classes 🤗 Accelerate provides for (`DeepSpeed`)[[https://huggingface.co/docs/accelerate/main/en/package_reference/deepspeed]](https://huggingface.co/docs/accelerate/main/en/package_reference/deepspeed%5D) and (`FSDP`)[[https://huggingface.co/docs/accelerate/main/en/package_reference/fsdp]](https://huggingface.co/docs/accelerate/main/en/package_reference/fsdp%5D)

🤗 Accelerate makes it almost **trivial** to switch between FSDP and DeepSpeed, with the majority of it being an Accelerate config file change (see the new concept guide for instructions on this).

Besides the config change, some of the other considerations (also outlined in the guide) are differences in how checkpoints are handled, etc.

All experiments in this blog can be reproduced with the code from the [original 🤗 Accelerate issue](https://github.com/huggingface/accelerate/issues/2624).

We intend to follow up with throughput comparisons at scale and techniques to better utilize those GPUs for tuning and alignment jobs while maintaining model quality.

## Acknowledgements

This is an effort that involved several teams across multiple organizations to come together. It started at IBM Research, specifically Aldo Pareja, who found the issue, and Fabian Lim, who identified the precision gaps and fixed this issue. Zach Mueller and [Stas Bekman](https://github.com/stas00) have been phenomenal in providing feedback and the fixes to accelerate. Less Wright from the PyTorch Team at Meta was very helpful with questions on FSDP parameters. Finally, we would also like to thank the [DeepSpeed](https://www.deepspeed.ai/) team for providing feedback on this blog.

## Models mentioned in this article 1

More Articles from our Blog

research

nlp

open-source

## Faster Text Generation with Self-Speculative Decoding

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/608aabf24955d2bfc3cd99c6/-YxmtpzEmf3NKOTktODRP.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/63c9725ebedad7e2bf160bdc/wzPuyhOXCYBNGwZDshbnL.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1655385361868-61b85ce86eb1f2c5e6233736.jpeg)

67

November 20, 2024

research

nlp

open-source

## Universal Assisted Generation: Faster Decoding with Any Assistant Model

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6055ae5d25cd24537dd59dc5/eswozkCirLrnyhufN8_-f.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1664643955283-60570320cbe9c7542f3501e3.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/63e0c8875c6964861ebb0c49/yzkhPSxgXtJCM62iMBOOK.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/606d6349f1259f30578520ad/72_XrFfgQ6p9tgJj5Bc5U.png)
- +4

62

October 29, 2024

### Community

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fdeepspeed-to-fsdp-and-back) or [log in](https://huggingface.co/login?next=%2Fblog%2Fdeepspeed-to-fsdp-and-back) to comment


63

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

## Models mentioned in this article 1
