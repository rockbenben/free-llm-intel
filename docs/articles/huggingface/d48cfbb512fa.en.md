---
vendor: huggingface
title: Using LoRA for Efficient Stable Diffusion Fine-Tuning
original_title: Using LoRA for Efficient Stable Diffusion Fine-Tuning
url: https://huggingface.co/blog/lora
date: 2023-04-24
lang: en
captured: 2026-10-06
extractor: readability-v1
status: ok
body_sha: 98ebdcdc34b7
---

Back to Articles

# Using LoRA for Efficient Stable Diffusion Fine-Tuning

Published
					January 26, 2023

Update on GitHub

Upvote

84

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/615b8a9c23f3c5e91441a387/b7wAb09b-doTD5zf4gZOc.jpeg)](https://huggingface.co/Broomva)
- [![](https://huggingface.co/avatars/7d47ce449a26a2b2f44e99369d28c5b2.svg)](https://huggingface.co/arslanali900)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/62e54f0eae9d3f10acb95cb9/VAyk05hqB3OZWXEZW-B0q.png)](https://huggingface.co/mrfakename)
- [![](https://huggingface.co/avatars/5ef1e6ed4d77275727e7be8297ac36e2.svg)](https://huggingface.co/eurekaylj)
- [![](https://huggingface.co/avatars/cb500c762af93de33f8b2bd154a71410.svg)](https://huggingface.co/Mahendran)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/OqiF10RKo-bytyIkmX8HJ.png)](https://huggingface.co/privategeek24)

Pedro Cuenca

pcuenq

Sayak Paul

sayakpaul

This article is also available in Chinese [简体中文](https://huggingface.co/blog/zh/lora).

[LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685) is a novel technique introduced by Microsoft researchers to deal with the problem of fine-tuning large-language models. Powerful models with billions of parameters, such as GPT-3, are prohibitively expensive to fine-tune in order to adapt them to particular tasks or domains. LoRA proposes to freeze pre-trained model weights and inject trainable layers (*rank-decomposition matrices*) in each transformer block. This greatly reduces the number of trainable parameters and GPU memory requirements since gradients don't need to be computed for most model weights. The researchers found that by focusing on the Transformer attention blocks of large-language models, fine-tuning quality with LoRA was on par with full model fine-tuning while being much faster and requiring less compute.

## LoRA for Diffusers 🧨

Even though LoRA was initially proposed for large-language models and demonstrated on transformer blocks, the technique can also be applied elsewhere. In the case of Stable Diffusion fine-tuning, LoRA can be applied to the cross-attention layers that relate the image representations with the prompts that describe them. The details of the following figure (taken from the [Stable Diffusion paper](https://arxiv.org/abs/2112.10752)) are not important, just note that the yellow blocks are the ones in charge of building the relationship between image and text representations.

[![Latent Diffusion Architecture](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/lora-assets/latent-diffusion.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/lora-assets/latent-diffusion.png)

To the best of our knowledge, Simo Ryu ([`@cloneofsimo`](https://github.com/cloneofsimo)) was the first one to come up with a LoRA implementation adapted to Stable Diffusion. Please, do take a look at [their GitHub project](https://github.com/cloneofsimo/lora) to see examples and lots of interesting discussions and insights.

In order to inject LoRA trainable matrices as deep in the model as in the cross-attention layers, people used to need to hack the source code of [diffusers](https://github.com/huggingface/diffusers) in imaginative (but fragile) ways. If Stable Diffusion has shown us one thing, it is that the community always comes up with ways to bend and adapt the models for creative purposes, and we love that! Providing the flexibility to manipulate the cross-attention layers could be beneficial for many other reasons, such as making it easier to adopt optimization techniques such as [xFormers](https://github.com/facebookresearch/xformers). Other creative projects such as [Prompt-to-Prompt](https://arxiv.org/abs/2208.01626) could do with some easy way to access those layers, so we decided to [provide a general way for users to do it](https://github.com/huggingface/diffusers/pull/1639). We've been testing that *pull request* since late December, and it officially launched with our [diffusers release yesterday](https://github.com/huggingface/diffusers/releases/tag/v0.12.0).

We've been working with [`@cloneofsimo`](https://github.com/cloneofsimo) to provide LoRA training support in diffusers, for both Dreambooth and full fine-tuning methods! These techniques provide the following benefits:

- Training is much faster, as already discussed.
- Compute requirements are lower. We could create a full fine-tuned model in a 2080 Ti with 11 GB of VRAM!
- **Trained weights are much, much smaller**. Because the original model is frozen and we inject new layers to be trained, we can save the weights for the new layers as a single file that weighs in at ~3 MB in size. This is about *one thousand times smaller* than the original size of the UNet model!

We are particularly excited about the last point. In order for users to share their awesome fine-tuned or *dreamboothed* models, they had to share a full copy of the final model. Other users that want to try them out have to download the fine-tuned weights in their favorite UI, adding up to combined massive storage and download costs. As of today, there are about [1,000 Dreambooth models registered in the Dreambooth Concepts Library](https://huggingface.co/sd-dreambooth-library), and probably many more not registered in the library.

With LoRA, it is now possible to publish [a single 3.29 MB file](https://huggingface.co/sayakpaul/sd-model-finetuned-lora-t4/blob/main/pytorch_lora_weights.bin) to allow others to use your fine-tuned model.

*(h/t to [`@mishig25`](https://github.com/mishig25), the first person I heard use **dreamboothing** as a verb in a normal conversation).*

## LoRA fine-tuning

Full model fine-tuning of Stable Diffusion used to be slow and difficult, and that's part of the reason why lighter-weight methods such as Dreambooth or Textual Inversion have become so popular. With LoRA, it is much easier to fine-tune a model on a custom dataset.

Diffusers now provides a [LoRA fine-tuning script](https://github.com/huggingface/diffusers/blob/main/examples/text_to_image/train_text_to_image_lora.py) that can run in as low as 11 GB of GPU RAM without resorting to tricks such as 8-bit optimizers. This is how you'd use it to fine-tune a model using [Lambda Labs Pokémon dataset](https://huggingface.co/datasets/lambdalabs/pokemon-blip-captions):

```
export MODEL_NAME="runwayml/stable-diffusion-v1-5"
export OUTPUT_DIR="/sddata/finetune/lora/pokemon"
export HUB_MODEL_ID="pokemon-lora"
export DATASET_NAME="lambdalabs/pokemon-blip-captions"

accelerate launch --mixed_precision="fp16"  train_text_to_image_lora.py \
  --pretrained_model_name_or_path=$MODEL_NAME \
  --dataset_name=$DATASET_NAME \
  --dataloader_num_workers=8 \
  --resolution=512 --center_crop --random_flip \
  --train_batch_size=1 \
  --gradient_accumulation_steps=4 \
  --max_train_steps=15000 \
  --learning_rate=1e-04 \
  --max_grad_norm=1 \
  --lr_scheduler="cosine" --lr_warmup_steps=0 \
  --output_dir=${OUTPUT_DIR} \
  --push_to_hub \
  --hub_model_id=${HUB_MODEL_ID} \
  --report_to=wandb \
  --checkpointing_steps=500 \
  --validation_prompt="Totoro" \
  --seed=1337
```

One thing of notice is that the learning rate is `1e-4`, much larger than the usual learning rates for regular fine-tuning (in the order of `~1e-6`, typically). This is a [W&B dashboard](https://wandb.ai/pcuenq/text2image-fine-tune/runs/b4k1w0tn?workspace=user-pcuenq) of the previous run, which took about 5 hours in a 2080 Ti GPU (11 GB of RAM). I did not attempt to optimize the hyperparameters, so feel free to try it out yourself! [Sayak](https://huggingface.co/sayakpaul) did another run on a T4 (16 GB of RAM), here's [his final model](https://huggingface.co/sayakpaul/sd-model-finetuned-lora-t4), and here's [a demo Space that uses it](https://huggingface.co/spaces/pcuenq/lora-pokemon).

[![Sample outputs from Sayak's LoRA model](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/lora-assets/sayak-pokemon-collage.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/lora-assets/sayak-pokemon-collage.png)

For additional details on LoRA support in diffusers, please refer to [our documentation](https://huggingface.co/docs/diffusers/main/en/training/lora) – it will be always kept up to date with the implementation.

## Inference

As we've discussed, one of the major advantages of LoRA is that you get excellent results by training orders of magnitude less weights than the original model size. We designed an inference process that allows loading the additional weights on top of the unmodified Stable Diffusion model weights. Let's see how it works.

First, we'll use the Hub API to automatically determine what was the base model that was used to fine-tune a LoRA model. Starting from [Sayak's model](https://huggingface.co/sayakpaul/sd-model-finetuned-lora-t4), we can use this code:

```
from huggingface_hub import model_info

# LoRA weights ~3 MB
model_path = "sayakpaul/sd-model-finetuned-lora-t4"

info = model_info(model_path)
model_base = info.cardData["base_model"]
print(model_base)   # CompVis/stable-diffusion-v1-4
```

This snippet will print the model he used for fine-tuning, which is `CompVis/stable-diffusion-v1-4`. In my case, I trained my model starting from version 1.5 of Stable Diffusion, so if you run the same code with [my LoRA model](https://huggingface.co/pcuenq/pokemon-lora) you'll see that the output is `runwayml/stable-diffusion-v1-5`.

The information about the base model is automatically populated by the fine-tuning script we saw in the previous section, if you use the `--push_to_hub` option. This is recorded as a metadata tag in the `README` file of the model's repo, as you can see [here](https://huggingface.co/pcuenq/pokemon-lora/blob/main/README.md).

After we determine the base model we used to fine-tune with LoRA, we load a normal Stable Diffusion pipeline. We'll customize it with the `DPMSolverMultistepScheduler` for very fast inference:

```
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler

pipe = StableDiffusionPipeline.from_pretrained(model_base, torch_dtype=torch.float16)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
```

**And here's where the magic comes**. We load the LoRA weights from the Hub *on top of the regular model weights*, move the pipeline to the cuda device and run inference:

```
pipe.unet.load_attn_procs(model_path)
pipe.to("cuda")

image = pipe("Green pokemon with menacing face", num_inference_steps=25).images[0]
image.save("green_pokemon.png")
```

## Dreamboothing with LoRA

Dreambooth allows you to "teach" new concepts to a Stable Diffusion model. LoRA is compatible with Dreambooth and the process is similar to fine-tuning, with a couple of advantages:

- Training is faster.
- We only need a few images of the subject we want to train (5 or 10 are usually enough).
- We can tweak the text encoder, if we want, for additional fidelity to the subject.

To train Dreambooth with LoRA you need to use [this diffusers script](https://github.com/huggingface/diffusers/blob/main/examples/dreambooth/train_dreambooth_lora.py). Please, take a look at [the README](https://github.com/huggingface/diffusers/tree/main/examples/dreambooth#training-with-low-rank-adaptation-of-large-language-models-lora), [the documentation](https://huggingface.co/docs/diffusers/main/en/training/lora) and [our hyperparameter exploration blog post](https://huggingface.co/blog/dreambooth) for details.

For a quick, cheap and easy way to train your Dreambooth models with LoRA, please [check this Space](https://huggingface.co/spaces/lora-library/LoRA-DreamBooth-Training-UI) by [`hysts`](https://twitter.com/hysts12321). You need to duplicate it and assign a GPU so it runs fast. This process will save you from having to set up your own training environment and you'll be able to train your models in minutes!

## Other Methods

The quest for easy fine-tuning is not new. In addition to Dreambooth, [*textual inversion*](https://huggingface.co/docs/diffusers/main/en/training/text_inversion) is another popular method that attempts to teach new concepts to a trained Stable Diffusion Model. One of the main reasons for using Textual Inversion is that trained weights are also small and easy to share. However, they only work for a single subject (or a small handful of them), whereas LoRA can be used for general-purpose fine-tuning, meaning that it can be adapted to new domains or datasets.

[Pivotal Tuning](https://arxiv.org/abs/2106.05744) is a method that tries to combine Textual Inversion with LoRA. First, you teach the model a new concept using Textual Inversion techniques, obtaining a new token embedding to represent it. Then, you train that token embedding using LoRA to get the best of both worlds.

We haven't explored Pivotal Tuning with LoRA yet. Who's up for the challenge? 🤗

## Models mentioned in this article 1

## Spaces mentioned in this article 2

More Articles from our Blog

guide

collaboration

diffusers

## LoRA training scripts of the world, unite!

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/638f308fc4444c6ca870b60a/Q11NK-8-JbiilJ-vk2LAR.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1649143001781-624bebf604abc7ebb01789af.jpeg)

80

January 2, 2024

diffusers

stable-diffusion

dreambooth

## Training Stable Diffusion with Dreambooth using Diffusers

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1600014820272-5ec0135ded25d76864d553f1.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1675508716308-noauth.jpeg)

32

November 7, 2022

### Community

thomascarrolljr

Dec 24, 2025

I'm particularly excited about the lower VRAM requirements. Being able to fine-tune on an 11 GB card opens this up to so many more people who don't have access to high-end hardware. The Pokemon example is perfect for demonstrating real-world results too. [https://playvio.io/](https://playvio.io/)

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Flora) or [log in](https://huggingface.co/login?next=%2Fblog%2Flora) to comment

Upvote

84

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/615b8a9c23f3c5e91441a387/b7wAb09b-doTD5zf4gZOc.jpeg)](https://huggingface.co/Broomva)
- [![](https://huggingface.co/avatars/7d47ce449a26a2b2f44e99369d28c5b2.svg)](https://huggingface.co/arslanali900)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/62e54f0eae9d3f10acb95cb9/VAyk05hqB3OZWXEZW-B0q.png)](https://huggingface.co/mrfakename)
- [![](https://huggingface.co/avatars/5ef1e6ed4d77275727e7be8297ac36e2.svg)](https://huggingface.co/eurekaylj)
- [![](https://huggingface.co/avatars/cb500c762af93de33f8b2bd154a71410.svg)](https://huggingface.co/Mahendran)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/OqiF10RKo-bytyIkmX8HJ.png)](https://huggingface.co/privategeek24)
- [![](https://huggingface.co/avatars/25a7099518dbd446f7385cf858272d4e.svg)](https://huggingface.co/ttaox)
- [![](https://huggingface.co/avatars/3d84982fbd33d2ea16a4cbf5f4c5659e.svg)](https://huggingface.co/hollowsense)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/645917af8aa54fb020f83351/g-g9TvDM42P2-YWwgcWuW.jpeg)](https://huggingface.co/nglebm19)
- [![](https://huggingface.co/avatars/54a2342bf21ea1efbbcc0f7b9c6d996c.svg)](https://huggingface.co/Greencow2000)
- [![](https://huggingface.co/avatars/3d73fd4d964c0e047cbc255fb60b29e8.svg)](https://huggingface.co/UGVly)
- [![](https://huggingface.co/avatars/b50148b860164be46a00a2991c9fad15.svg)](https://huggingface.co/Gezhiwa)

## Models mentioned in this article 1

## Spaces mentioned in this article 2
