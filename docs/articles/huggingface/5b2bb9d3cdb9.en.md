---
vendor: huggingface
title: Make LLM Fine-tuning 2x faster with Unsloth and 🤗 TRL
original_title: Make LLM Fine-tuning 2x faster with Unsloth and 🤗 TRL
url: https://huggingface.co/blog/unsloth-trl
date: 2024-11-21
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 211810e8a565
---


# Make LLM Fine-tuning 2x faster with Unsloth and 🤗 TRL

					January 10, 2024

Update on GitHub


77

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63581bce0e4fef2198254575/yMzMAZCXYul2fRKHpbcvx.png)](https://huggingface.co/jucamohedano)
- [![](https://huggingface.co/avatars/084c2c1e9ff7cf474be8e6a4f39d297d.svg)](https://huggingface.co/lanj133)
- [![](https://huggingface.co/avatars/068505bec3b58e78e9c6d91a47fa3ac6.svg)](https://huggingface.co/realdanielbyrne)
- [![](https://huggingface.co/avatars/5b5eaf65f6260d81fce18c1ee5fdefd1.svg)](https://huggingface.co/mitjamartini)
- [![](https://huggingface.co/avatars/70d5e6c9ff08c99ca73bc28a8a30c407.svg)](https://huggingface.co/kartikmehta204)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63107b18e87051f3e3e0f598/R9onir4Y0MZuq1jEWCZ2-.jpeg)](https://huggingface.co/ucyang)

Daniel (Unsloth)

danielhanchen

guest

Pulling your hair out because LLM fine-tuning is taking forever? In this post, we introduce a lightweight tool developed by the community to make LLM fine-tuning go super fast!

Before diving into Unsloth, it may be helpful to read our [QLoRA blog post](https://huggingface.co/blog/4bit-transformers-bitsandbytes), or be familiar with LLM fine-tuning using the 🤗 PEFT library.

## Unsloth - 2x faster, -40% memory usage, 0% accuracy degradation

[Unsloth](https://github.com/unslothai/unsloth) is a lightweight library for faster LLM fine-tuning which is fully compatible with the Hugging Face ecosystem (Hub, transformers, PEFT, TRL). The library is actively developed by the Unsloth team ([Daniel](https://huggingface.co/danielhanchen) and [Michael](https://github.com/shimmyshimmer)) and the open source community. The library supports most NVIDIA GPUs –from GTX 1070 all the way up to H100s–, and can be used with the entire trainer suite from the TRL library (SFTTrainer, DPOTrainer, PPOTrainer). At the time of writing, Unsloth supports the Llama (CodeLlama, Yi, etc) and Mistral architectures.

Unsloth works by overwriting some parts of the modeling code with optimized operations. By manually deriving backpropagation steps and rewriting all Pytorch modules into Triton kernels, Unsloth can both reduce memory usage and make fine-tuning faster. Crucially, accuracy degradation is 0% with respect to normal QLoRA, because no approximations are made in the optimized code.

## Benchmarking

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

Unsloth was benchmarked across 59 runs using 4 datasets on Tesla T4 and A100 Google Colab instances. QLoRA was applied to all linear layers (attention and MLP) with a rank of 16, and gradient checkpointing was on. By testing against the latest Transformers version [(4.36)](https://github.com/huggingface/transformers/releases/tag/v4.36.0), which has SDPA natively integrated if you have Pytorch 2.1.1, Unsloth is up to 2.7x faster and uses up to 74% less memory. We also tested Unsloth on a free Google Colab instance (low RAM, 1 T4 GPU, Pytorch 2.1.0 CUDA 12.1). All 59 notebooks are provided for full reproducibility, and more details are in Unsloth’s benchmarking details [here](https://unsloth.ai/blog/mistral-benchmark)

## How do I use Unsloth?

Just load your model with `FastLanguageModel.from_pretrained`! Currently, Unsloth supports Llama and Mistral type architectures (Yi, Deepseek, TinyLlama, Llamafied Qwen). Please, [open a Github issue](https://github.com/unslothai/unsloth) if you want others! Also, on the latest Transformers `main` branch, you can now load pre-quantized 4bit models directly! This makes downloading models 4x faster, and reduces memory fragmentation by around 500MB, which allows you to fit larger batches! We have a few pre-quantized models for your convenience, including `unsloth/llama-2-7b-bnb-4bit`, `unsloth/llama-2-13b-bnb-4bit`, `unsloth/mistral-7b-bnb-4bit` and `unsloth/codellama-34b-bnb-4bit`.

You will need to provide your intended maximum sequence length to `from_pretrained`. Unsloth internally performs RoPE Scaling, so larger maximum sequence lengths are automatically supported. Otherwise the API is pretty much the same as transformers’ `from_pretrained`, except that `FastLanguageModel.from_pretrained` also returns the model tokenizer for convenience.

```
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/mistral-7b-bnb-4bit", # Supports Llama, Mistral - replace this!
    max_seq_length = 2048, # Supports RoPE Scaling internally, so choose any!
    load_in_4bit = True,
)
```

Once the model has been loaded, use `FastLanguageModel.get_peft_model` to attach adapters in order to perform QLoRA fine-tuning.

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

Once adapters are attached, you can use the model directly within any class from the HF ecosystem, such as the `SFTTrainer` from TRL!

## Unsloth + TRL integration

To use Unsloth with the TRL library, simply pass the Unsloth model into `SFTTrainer` or `DPOTrainer`! The trained model is fully compatible with the Hugging Face ecosystem, so you can push the final model to the Hub and use transformers for inference out of the box!

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

## Reproducible notebooks

We are sharing below fully reproducible notebooks for anyone that wants to try out Unsloth with SFTTrainer on a free-tier Google Colab instance.

Llama 7b Free Tesla T4 colab example [here](https://huggingface.co/datasets/unsloth/notebooks/blob/main/Alpaca_%2B_Llama_7b_full_example.ipynb)

Mistral 7b Free Tesla T4 colab example [here](https://huggingface.co/datasets/unsloth/notebooks/blob/main/Alpaca_%2B_Mistral_7b_full_example.ipynb)

CodeLlama 34b A100 colab example [here](https://huggingface.co/datasets/unsloth/notebooks/blob/main/Alpaca_%2B_Codellama_34b_full_example.ipynb)

Zephyr DPO replication T4 colab example [here](https://huggingface.co/datasets/unsloth/notebooks/blob/main/DPO_Zephyr_Unsloth_Example.ipynb)

## Datasets mentioned in this article 1

More Articles from our Blog

llm

optimization

quantization

## Overview of natively supported quantization schemes in 🤗 Transformers

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1648631057413-noauth.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/63ce875d199b36f7552d4f07/bpUrvhXDagzRqZ3vxTcSF.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1642598610696-noauth.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1644340617257-noauth.png)
- +1

13

September 12, 2023

llm

optimization

quantization

## Making LLMs lighter with AutoGPTQ and transformers

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/63ce875d199b36f7552d4f07/bpUrvhXDagzRqZ3vxTcSF.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1651743336129-624c60cba8ec93a7ac188b56.png)
- ![](https://huggingface.co/avatars/ad2b3f618031a1ea695728053a714fc2.svg)
- ![](https://huggingface.co/avatars/1bcbc93e7343b8dde06601abf6e32f4e.svg)
- +2

65

August 23, 2023

### Community

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Funsloth-trl) or [log in](https://huggingface.co/login?next=%2Fblog%2Funsloth-trl) to comment


77

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63581bce0e4fef2198254575/yMzMAZCXYul2fRKHpbcvx.png)](https://huggingface.co/jucamohedano)
- [![](https://huggingface.co/avatars/084c2c1e9ff7cf474be8e6a4f39d297d.svg)](https://huggingface.co/lanj133)
- [![](https://huggingface.co/avatars/068505bec3b58e78e9c6d91a47fa3ac6.svg)](https://huggingface.co/realdanielbyrne)
- [![](https://huggingface.co/avatars/5b5eaf65f6260d81fce18c1ee5fdefd1.svg)](https://huggingface.co/mitjamartini)
- [![](https://huggingface.co/avatars/70d5e6c9ff08c99ca73bc28a8a30c407.svg)](https://huggingface.co/kartikmehta204)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63107b18e87051f3e3e0f598/R9onir4Y0MZuq1jEWCZ2-.jpeg)](https://huggingface.co/ucyang)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64895f0b8c69af83c466eacf/Bhn8e3KzR80w3xe2FMvyE.png)](https://huggingface.co/Karamouche)
- [![](https://huggingface.co/avatars/09a6c67f3da6cfbcde6bf31e8a175f38.svg)](https://huggingface.co/YeungNLP)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6495db1662ae62cd134a52fc/L7UXMJE0_hUA7eVFm83wG.jpeg)](https://huggingface.co/santyzenith)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1659971187637-60d3b57ad7b174177faabd6e.jpeg)](https://huggingface.co/chansung)
- [![](https://huggingface.co/avatars/f6a4a8d04476f72ecda1c253736fa3d2.svg)](https://huggingface.co/YxBxRyXJx)
- [![](https://huggingface.co/avatars/9f4bdb373790586063d0800bfc179c2e.svg)](https://huggingface.co/enrsam)

## Datasets mentioned in this article 1
