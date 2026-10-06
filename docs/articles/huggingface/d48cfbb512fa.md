---
vendor: huggingface
title: 用 LoRA 高效微调 Stable Diffusion
original_title: Using LoRA for Efficient Stable Diffusion Fine-Tuning
url: https://huggingface.co/blog/lora
date: 2023-01-26
lang: zh
captured: 2026-10-06
extractor: readability-v1
translator: agent
status: translated
---

# 用 LoRA 高效微调 Stable Diffusion

[LoRA: Low-Rank Adaptation of Large Language Models（大语言模型的低秩适配）](https://arxiv.org/abs/2106.09685) 是微软研究人员提出的一项新技术，用来解决大语言模型的微调问题。像 GPT-3 这样拥有数十亿参数的强力模型，为了让它们适配特定任务或领域而做微调，成本高得让人却步。LoRA 的做法是冻结预训练模型的权重，并在每个 transformer 层中注入可训练的新层（*秩分解矩阵*）。这大幅减少了可训练参数的数量和 GPU 显存需求，因为绝大多数模型权重都不需要计算梯度。研究者发现，把着力点放在大语言模型的 Transformer 注意力层上时，用 LoRA 微调出来的质量和全模型微调不相上下，但速度要快得多，所需算力也小得多。

## LoRA 用于 Diffusers 🧨

尽管 LoRA 最初是为大语言模型提出的，也是在 Transformer 层上做的验证，但这项技术同样可以用在别处。就 Stable Diffusion 的微调而言，LoRA 可以作用在把图像表征与描述它们的提示词对应起来的交叉注意力层（cross-attention layers）上。下面这张图（取自 [Stable Diffusion 论文](https://arxiv.org/abs/2112.10752)）的细节并不重要，你只要注意其中的黄色方块负责构建图像表征与文本表征之间的关系即可。

[![Latent Diffusion Architecture](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/lora-assets/latent-diffusion.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/lora-assets/latent-diffusion.png)

据我们所知，Simo Ryu（[`@cloneofsimo`](https://github.com/cloneofsimo)）是第一个为 Stable Diffusion 适配出 LoRA 实现的人。请一定去看看[他们的 GitHub 项目](https://github.com/cloneofsimo/lora)，里面有示例，还有大量颇有价值的讨论与见解。

要想把 LoRA 的可训练矩阵注入到模型足够深的地方——比如交叉注意力层——过去人们不得不用富有想象力（但也十分脆弱）的方式去改动 [diffusers](https://github.com/huggingface/diffusers) 的源码。如果说 Stable Diffusion 教会了我们一件事，那就是社区总会想出各种办法去改造和适配模型，用于创造性的目的，而我们很喜欢这一点！提供操纵交叉注意力层的灵活性，在很多其他方面同样有益，比如让 [xFormers](https://github.com/facebookresearch/xformers) 这类优化技术更容易被采用。另一个创意项目 [Prompt-to-Prompt](https://arxiv.org/abs/2208.01626) 也需要某种访问这些层的简便途径，所以我们决定[提供一种通用的方式让用户能够做到这一点](https://github.com/huggingface/diffusers/pull/1639)。自 12 月底以来我们一直在测试那个 *pull request*，它随着我们[昨天发布的 diffusers 版本](https://github.com/huggingface/diffusers/releases/tag/v0.12.0)正式对外推出。

我们和 [`@cloneofsimo`](https://github.com/cloneofsimo) 一起，为 diffusers 提供了 LoRA 训练支持，Dreambooth 和全模型微调两种方式都已覆盖！这些技术带来如下好处：

- 训练速度快得多，这一点前面已经讨论过。
- 算力需求更低。我们在一块 11 GB 显存的 2080 Ti 上就训练出了一个完整微调的模型！
- **训练出的权重体积要小得多、小得多**。由于原始模型被冻结，而我们注入的新层才是要训练的部分，因此可以把新层的权重存成单个文件，大小约 3 MB。相比 UNet 模型的原始体积，这大约*小了一千倍*！

我们对最后这一点尤其兴奋。过去用户想要分享自己出色的微调模型或 *dreambooth 版* 模型，不得不分享最终模型的完整副本。想试用这些模型的其他用户则要在自己常用的 UI 里下载微调后的权重，累积起来的存储与下载成本都非常可观。截至目前，[Dreambooth Concepts Library 中注册了约 1,000 个 Dreambooth 模型](https://huggingface.co/sd-dreambooth-library)，没有注册进这个库的想必还要多得多。

有了 LoRA，现在只需要发布[一个 3.29 MB 的文件](https://huggingface.co/sayakpaul/sd-model-finetuned-lora-t4/blob/main/pytorch_lora_weights.bin)，别人就能用上你微调出的模型。

*（感谢 [`@mishig25`](https://github.com/mishig25)，他是我听到的第一个在寻常对话里把 **dreamboothing** 当动词来用的人。）*

## LoRA 微调

Stable Diffusion 的全模型微调过去既慢又难，这也是 Dreambooth、Textual Inversion 这类更轻量方法如此流行的部分原因。有了 LoRA，针对自定义数据集微调模型变得容易多了。

Diffusers 现在提供了一个 [LoRA 微调脚本](https://github.com/huggingface/diffusers/blob/main/examples/text_to_image/train_text_to_image_lora.py)，最低只需要 11 GB 的 GPU 内存就能跑起来，不必动用 8-bit 优化器这类技巧。如果你想用 [Lambda Labs 的 Pokémon 数据集](https://huggingface.co/datasets/lambdalabs/pokemon-blip-captions) 来微调模型，可以这样使用它：

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

值得注意的是学习率是 `1e-4`，比常规微调常用的学习率（通常在 `~1e-6` 量级）大得多。这是上一次训练的 [W&B 面板](https://wandb.ai/pcuenq/text2image-fine-tune/runs/b4k1w0tn?workspace=user-pcuenq)，它在 2080 Ti GPU（11 GB 内存）上大约跑了 5 个小时。我并没有去优化超参数，欢迎你自己动手试试！[Sayak](https://huggingface.co/sayakpaul) 在 T4（16 GB 内存）上又跑了一次，这是[他最终的模型](https://huggingface.co/sayakpaul/sd-model-finetuned-lora-t4)，这是[用上了它的 demo Space](https://huggingface.co/spaces/pcuenq/lora-pokemon)。

[![Sample outputs from Sayak's LoRA model](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/lora-assets/sayak-pokemon-collage.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/lora-assets/sayak-pokemon-collage.png)

关于 diffusers 中 LoRA 支持的更多细节，请参阅[我们的文档](https://huggingface.co/docs/diffusers/main/en/training/lora)——它会始终与实现保持同步更新。

## 推理

正如前面所讨论的，LoRA 的一个主要优势在于：训练的参数比原模型规模少几个数量级，却能取得非常好的效果。我们据此设计了一套推理流程，允许把额外的权重叠加在未修改的 Stable Diffusion 模型权重之上加载。下面看看它是怎么工作的。

首先，我们用 Hub API 自动确定某个 LoRA 模型微调时用的是哪个基础模型。从 [Sayak 的模型](https://huggingface.co/sayakpaul/sd-model-finetuned-lora-t4) 出发，可以用这段代码：

```
from huggingface_hub import model_info

# LoRA weights ~3 MB
model_path = "sayakpaul/sd-model-finetuned-lora-t4"

info = model_info(model_path)
model_base = info.cardData["base_model"]
print(model_base)   # CompVis/stable-diffusion-v1-4
```

这段代码会打印出他用来做微调的模型，也就是 `CompVis/stable-diffusion-v1-4`。就我而言，我的模型是从 Stable Diffusion 1.5 版本开始训练的，所以如果你对[我的 LoRA 模型](https://huggingface.co/pcuenq/pokemon-lora) 运行同样的代码，会看到输出是 `runwayml/stable-diffusion-v1-5`。

如果你使用了 `--push_to_hub` 选项，基础模型的信息会由上一节介绍的那个微调脚本自动填好。它作为元数据标签记录在模型仓库的 `README` 文件里，如[这里](https://huggingface.co/pcuenq/pokemon-lora/blob/main/README.md) 所示。

在确定好用于 LoRA 微调的基础模型之后，我们加载一个普通的 Stable Diffusion pipeline。我们为它配置 `DPMSolverMultistepScheduler`，以实现非常快的推理：

```
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler

pipe = StableDiffusionPipeline.from_pretrained(model_base, torch_dtype=torch.float16)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
```

**奇迹就发生在下一步**。我们从 Hub 加载 LoRA 权重，*把它们叠加在常规模型权重之上*，把 pipeline 移到 cuda 设备上，然后运行推理：

```
pipe.unet.load_attn_procs(model_path)
pipe.to("cuda")

image = pipe("Green pokemon with menacing face", num_inference_steps=25).images[0]
image.save("green_pokemon.png")
```

## 用 LoRA 做 Dreambooth

Dreambooth 允许你让 Stable Diffusion 模型「学会」新的概念。LoRA 与 Dreambooth 兼容，流程和微调类似，但有几个优势：

- 训练更快。
- 我们只需要少量要训练的目标主体的图片（通常 5 到 10 张就够）。
- 如果需要，我们还可以调整文本编码器，让结果与目标更加贴合。

要用 LoRA 训练 Dreambooth，需要使用[这个 diffusers 脚本](https://github.com/huggingface/diffusers/blob/main/examples/dreambooth/train_dreambooth_lora.py)。有关细节，请查看 [README](https://github.com/huggingface/diffusers/tree/main/examples/dreambooth#training-with-low-rank-adaptation-of-large-language-models-lora)、[文档](https://huggingface.co/docs/diffusers/main/en/training/lora) 以及[我们的超参数探索博客文章](https://huggingface.co/blog/dreambooth)。

想要快速、便宜、轻松地用 LoRA 训练你的 Dreambooth 模型，请[看看这个 Space](https://huggingface.co/spaces/lora-library/LoRA-DreamBooth-Training-UI)，作者是 [`hysts`](https://twitter.com/hysts12321)。你需要把它复制一份并分配一块 GPU，这样才能跑得快。这一步替你省掉了自建训练环境的麻烦，几分钟内就能训练出自己的模型！

## 其他方法

对轻松微调的追求由来已久。除了 Dreambooth，[*textual inversion*](https://huggingface.co/docs/diffusers/main/en/training/text_inversion) 是另一种流行的方法，它同样试图向训练好的 Stable Diffusion 模型教授新概念。选用 Textual Inversion 的一个主要原因是训练出的权重也很小、便于分享。不过它只适用于单个主体（或少量几个主体），而 LoRA 可以用于通用目的的微调，也就是说它可以适配新的领域或数据集。

[Pivotal Tuning](https://arxiv.org/abs/2106.05744) 试图把 Textual Inversion 与 LoRA 结合起来。首先用 Textual Inversion 的技术教会模型一个新概念，得到一个表示它的新的 token embedding；然后用 LoRA 训练这个 token embedding，兼得两者之长。

我们还没有探索结合 LoRA 的 Pivotal Tuning。谁愿意来挑战一下？🤗
