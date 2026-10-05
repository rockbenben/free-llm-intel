---
vendor: huggingface
title: 用 Unsloth 和 🤗 TRL 让 LLM 微调快 2 倍
original_title: Make LLM Fine-tuning 2x faster with Unsloth and 🤗 TRL
url: https://huggingface.co/blog/unsloth-trl
date: 2024-11-21
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

因为 LLM 微调慢得让人抓狂？本文介绍一个由社区开发的轻量工具，让 LLM 微调快到飞起！

在深入 Unsloth 之前，先读读我们的 [QLoRA 博客](https://huggingface.co/blog/4bit-transformers-bitsandbytes)，或熟悉一下用 🤗 PEFT 库做 LLM 微调，会更有帮助。

## Unsloth——快 2 倍、省 40% 内存、0 精度损失

[Unsloth](https://github.com/unslothai/unsloth) 是一个用于更快 LLM 微调的轻量库，与 Hugging Face 生态（Hub、transformers、PEFT、TRL）完全兼容。该库由 Unsloth 团队（[Daniel](https://huggingface.co/danielhanchen) 和 [Michael](https://github.com/shimmyshimmer)）与开源社区积极开发。它支持从 GTX 1070 一直到 H100 的绝大多数 NVIDIA GPU，并可搭配 TRL 库的全套 trainer（SFTTrainer、DPOTrainer、PPOTrainer）。写作本文时，Unsloth 支持 Llama（CodeLlama、Yi 等）与 Mistral 架构。

Unsloth 的工作方式是用优化后的算子覆写建模代码的某些部分。通过手工推导反向传播步骤、并把所有 PyTorch 模块重写为 Triton kernel，Unsloth 能同时降低内存占用并加速微调。关键是，相比普通 QLoRA 精度损失为 0%，因为优化后的代码没有做任何近似。

## 基准测试

| 1 A100 40GB | Dataset | 🤗 Hugging Face | 🤗 + Flash Attention 2 | 🦥 Unsloth | 🦥 VRAM reduction |
| --- | --- | --- | --- | --- | --- |
| Code Llama 34b | Slim Orca | 1x | 1.01x | **1.94x** | -22.7% |
| Llama-2 7b | Slim Orca | 1x | 0.96x | **1.87x** | -39.3% |
| Mistral 7b | Slim Orca | 1x | 1.17x | **1.88x** | -65.9% |
| Tiny Llama 1.1b | Alpaca | 1x | 1.55x | **2.74x** | -57.8% |
| DPO with Zephyr | Ultra Chat | 1x | 1.24x | **1.88x** | -11.6% |

| Free Colab T4 | Dataset | 🤗 Hugging Face | 🤗 + Pytorch 2.1.1 | 🦥 Unsloth | 🦥 VRAM reduction |
| --- | --- | --- | --- | --- | --- |
| Llama-2 7b | OASST | 1x | 1.19x | **1.95x** | -43.3% |
| Mistral 7b | Alpaca | 1x | 1.07x | **1.56x** | -13.7% |
| Tiny Llama 1.1b | Alpaca | 1x | 2.06x | **3.87x** | -73.8% |
| DPO with Zephyr | Ultra Chat | 1x | 1.09x | **1.55x** | -18.6% |

Unsloth 在 Tesla T4 与 A100 的 Google Colab 实例上，用 4 个数据集跑了 59 组基准。QLoRA 施加到所有线性层（attention 与 MLP），rank 为 16，并开启梯度检查点。对比最新版 Transformers（[4.36](https://github.com/huggingface/transformers/releases/tag/v4.36.0)，在 Pytorch 2.1.1 下原生集成 SDPA），Unsloth 最快可达 2.7 倍速、内存占用最多低 74%。我们还在免费 Google Colab 实例（低内存、1 块 T4 GPU、Pytorch 2.1.0 CUDA 12.1）上测试了 Unsloth。全部 59 个 notebook 都已提供以保证完全可复现，更多细节见 Unsloth 的基准说明[这里](https://unsloth.ai/blog/mistral-benchmark)。

## 我该怎么用 Unsloth？

用 `FastLanguageModel.from_pretrained` 加载你的模型就行！目前 Unsloth 支持 Llama 与 Mistral 类型架构（Yi、Deepseek、TinyLlama、Llamafied Qwen）。想要其他架构请[提 Github issue](https://github.com/unslothai/unsloth)！另外，在最新的 Transformers `main` 分支上，现在可以直接加载预量化 4bit 模型！这让模型下载快 4 倍，并把内存碎片减少约 500MB，从而能塞下更大的 batch！我们为你预备了几个预量化模型，包括 `unsloth/llama-2-7b-bnb-4bit`、`unsloth/llama-2-13b-bnb-4bit`、`unsloth/mistral-7b-bnb-4bit` 与 `unsloth/codellama-34b-bnb-4bit`。

你需要给 `from_pretrained` 提供期望的最大序列长度。Unsloth 内部会做 RoPE 缩放，因此自动支持更大的最大序列长度。除此之外，其 API 与 transformers 的 `from_pretrained` 几乎一样，只是 `FastLanguageModel.from_pretrained` 会顺便返回模型的 tokenizer。

```
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/mistral-7b-bnb-4bit", # Supports Llama, Mistral - replace this!
    max_seq_length = 2048, # Supports RoPE Scaling internally, so choose any!
    load_in_4bit = True,
)
```

模型加载后，用 `FastLanguageModel.get_peft_model` 挂上适配器以执行 QLoRA 微调。

```
# Do model patching and add fast LoRA weights
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 16,
    lora_dropout = 0, # Supports any, but = 0 is optimized
    bias = "none",    # Supports any, but = "none" is optimized
    use_gradient_checkpointing = True,
)
```

适配器挂好后，你就可以在 HF 生态的任何类中直接使用这个模型，比如 TRL 的 `SFTTrainer`！

## Unsloth + TRL 集成

要在 TRL 库中使用 Unsloth，只需把 Unsloth 模型传给 `SFTTrainer` 或 `DPOTrainer`！训练好的模型与 Hugging Face 生态完全兼容，你可以把最终模型推送到 Hub，并直接用 transformers 做推理，开箱即用！

```
import torch

from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset

from unsloth import FastLanguageModel

max_seq_length = 2048 # Supports RoPE Scaling interally, so choose any!
# Get dataset
dataset = load_dataset("imdb", split="train")

# Load Llama model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/mistral-7b-bnb-4bit", # Supports Llama, Mistral - replace this!
    max_seq_length = max_seq_length,
    dtype = None,
    load_in_4bit = True,
)

# Do model patching and add fast LoRA weights
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj",],
    lora_alpha = 16,
    lora_dropout = 0, # Supports any, but = 0 is optimized
    bias = "none",    # Supports any, but = "none" is optimized
    use_gradient_checkpointing = True,
    random_state = 3407,
    max_seq_length = max_seq_length,
)

trainer = SFTTrainer(
    model = model,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    tokenizer = tokenizer,
    args = TrainingArguments(
      per_device_train_batch_size = 2,
      gradient_accumulation_steps = 4,
      warmup_steps = 10,
      max_steps = 60,
      fp16 = not torch.cuda.is_bf16_supported(),
      bf16 = torch.cuda.is_bf16_supported(),
      logging_steps = 1,
      output_dir = "outputs",
      optim = "adamw_8bit",
      seed = 3407,
  ),
)
trainer.train()
```

## 可复现的 notebooks

下面分享完全可复现的 notebook，供想在免费 Google Colab 实例上用 Unsloth + SFTTrainer 试一试的人使用。

Llama 7b 免费 Tesla T4 colab 示例在[这里](https://huggingface.co/datasets/unsloth/notebooks/blob/main/Alpaca_%2B_Llama_7b_full_example.ipynb)

Mistral 7b 免费 Tesla T4 colab 示例在[这里](https://huggingface.co/datasets/unsloth/notebooks/blob/main/Alpaca_%2B_Mistral_7b_full_example.ipynb)

CodeLlama 34b A100 colab 示例在[这里](https://huggingface.co/datasets/unsloth/notebooks/blob/main/Alpaca_%2B_Codellama_34b_full_example.ipynb)

Zephyr DPO 复现 T4 colab 示例在[这里](https://huggingface.co/datasets/unsloth/notebooks/blob/main/DPO_Zephyr_Unsloth_Example.ipynb)
