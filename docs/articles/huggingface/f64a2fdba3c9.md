---
vendor: huggingface
title: 日语 Stable Diffusion
original_title: Japanese Stable Diffusion
url: https://huggingface.co/blog/japanese-stable-diffusion
date: 2023-08-23
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# 日语 Stable Diffusion

[![Open In Hugging Face Spaces](https://img.shields.io/badge/🤗 Hugging Face-Spaces-blue)](https://huggingface.co/spaces/rinna/japanese-stable-diffusion)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rinnakk/japanese-stable-diffusion/blob/master/scripts/txt2img.ipynb)

由 [CompVis](https://github.com/CompVis)、[Stability AI](https://stability.ai/) 和 [LAION](https://laion.ai/) 开发的 Stable Diffusion，凭借只需输入文本 prompt 就能生成高准确度图像的能力，引发了广泛关注。Stable Diffusion 的训练数据主要使用 [LAION-5B](https://laion.ai/blog/laion-5b/) 数据集的英文子集 [LAION2B-en](https://huggingface.co/datasets/laion/laion2B-en)，因此需要输入英文文本 prompt，生成的图像也更偏向西方文化。

[rinna Co., Ltd](https://rinna.co.jp/). 通过在日语标注图像上微调 Stable Diffusion，开发了日语专属的文本生成图像模型 "Japanese Stable Diffusion"。Japanese Stable Diffusion 接受日语文本 prompt，能够生成反映日语世界文化、而难以通过翻译表达的图像。

本文将讨论 Japanese Stable Diffusion 的开发背景与训练方法。Japanese Stable Diffusion 已在 Hugging Face 和 GitHub 上发布，代码基于 [🧨 Diffusers](https://huggingface.co/docs/diffusers/index)。

- Hugging Face model card: [https://huggingface.co/rinna/japanese-stable-diffusion](https://huggingface.co/rinna/japanese-stable-diffusion)
- Hugging Face Spaces: [https://huggingface.co/spaces/rinna/japanese-stable-diffusion](https://huggingface.co/spaces/rinna/japanese-stable-diffusion)
- GitHub: [https://github.com/rinnakk/japanese-stable-diffusion](https://github.com/rinnakk/japanese-stable-diffusion)

## Stable Diffusion

近来已有报告指出，扩散模型在人工合成方面非常有效，图像上甚至胜过 GAN（生成对抗网络）。Hugging Face 在以下文章中解释了扩散模型的工作原理：

- [The Annotated Diffusion Model](https://huggingface.co/blog/annotated-diffusion)
- [Getting started with 🧨 Diffusers](https://colab.research.google.com/github/huggingface/notebooks/blob/main/diffusers/diffusers_intro.ipynb)

通常，一个文本生成图像模型由解读文本的文本编码器和根据编码输出图像的生成模型组成。

Stable Diffusion 使用 OpenAI 的语言-图像预训练模型 CLIP 作为文本编码器，用扩散模型的改进版——潜在扩散模型（latent diffusion model）——作为生成模型。Stable Diffusion 主要在 LAION-5B 的英文子集上训练，仅凭输入文本 prompt 就能生成高质量图像。除了高性能，Stable Diffusion 还很易用，推理只需约 10GB VRAM 的 GPU。

![sd-pipeline](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/stable_diffusion.png)

*from [Stable Diffusion with 🧨 Diffusers](https://huggingface.co/blog/stable_diffusion)*

## Japanese Stable Diffusion

### 为什么需要日语 Stable Diffusion？

Stable Diffusion 是极强的文本生成图像模型——不仅质量高，计算成本也低。由于它在英文数据集上训练，非英文 prompt 需先翻译成英文。令人惊讶的是，即使输入非英文 prompt，Stable Diffusion 有时也能生成合适的图像。

那么，为什么还需要一个语言专属的 Stable Diffusion？答案是我们想要一个能理解日本文化、身份认同和独特表达（包括俚语）的文本生成图像模型。例如，一个常见的由英文 businessman 重新演绎的日语词 "salary man"（サラリーマン），人们大多想象的是穿西装的上班族。Stable Diffusion 无法正确理解这类日语特有词汇，因为日语并不是它的目标语言。

![salary man of stable diffusion](https://huggingface.co/blog/assets/106_japanese_stable_diffusion/sd.jpeg)

*"salary man, oil painting" from the original Stable Diffusion*

这正是我们制作语言专属版 Stable Diffusion 的原因。与原版 Stable Diffusion 相比，Japanese Stable Diffusion 能做到以下几点：

- 生成日式风格图像
- 理解源自英语的日语外来词
- 理解日语独特的拟声拟态词
- 日语专有名词的理解

### 训练数据

我们使用了约 1 亿张带日语标注的图像，包括 [LAION-5B](https://laion.ai/blog/laion-5b/) 的日语子集。此外，为去除低质量样本，我们使用 rinna 公司发布的 [japanese-cloob-vit-b-16](https://huggingface.co/rinna/japanese-cloob-vit-b-16) 作为预处理步骤，删除得分低于某阈值的样本。

### 训练细节

构建日语专属文本生成图像模型的最大挑战是数据集规模。非英文数据集远比英文数据集小，这会导致深度学习模型性能下降。训练 Japanese Stable Diffusion 所用的数据集只有 Stable Diffusion 训练集的 1/20。为了用这么小的数据集做出好模型，我们没有从零训练文本生成图像模型，而是在英文数据集上训练的强大 [Stable Diffusion](https://huggingface.co/CompVis/stable-diffusion-v1-4) 基础上微调。

为做出优秀的语言专属文本生成图像模型，我们没有简单微调，而是按照 [PITI](https://arxiv.org/abs/2205.12952) 的思想应用了两个训练阶段。

#### 第一阶段：训练日语专属文本编码器

第一阶段固定潜在扩散模型，把英文文本编码器替换为日语专属文本编码器并对其进行训练。此时使用我们的日语 sentencepiece tokenizer 作为分词器。如果直接使用 CLIP tokenizer，日语文本会被按字节切分，token 依赖难以学习，且 token 数量会不必要地偏大。例如，对 "サラリーマン 油絵" 进行切分会得到 `['ãĤ', 'µ', 'ãĥ©', 'ãĥª', 'ãĥ¼ãĥ', 'ŀ', 'ãĥ³</w>', 'æ', '²', '¹', 'çµ', 'µ</w>']` 这些无法解读的 token。

```
from transformers import CLIPTokenizer
tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")
text = "サラリーマン 油絵"
tokens = tokenizer(text, add_special_tokens=False)['input_ids']
print("tokens:", tokenizer.convert_ids_to_tokens(tokens))
# tokens: ['ãĤ', 'µ', 'ãĥ©', 'ãĥª', 'ãĥ¼ãĥ', 'ŀ', 'ãĥ³</w>', 'æ', '²', '¹', 'çµ', 'µ</w>']
print("decoded text:", tokenizer.decode(tokens))
# decoded text: サラリーマン 油絵
```

另一方面，使用我们的日语 tokenizer 后，prompt 被切成可解读的 token，数量也减少了。例如 "サラリーマン 油絵" 可切分为 `['▁', 'サラリーマン', '▁', '油', '絵']`，是符合日语习惯的正确切分。

```
from transformers import T5Tokenizer
tokenizer = T5Tokenizer.from_pretrained("rinna/japanese-stable-diffusion", subfolder="tokenizer", use_auth_token=True)
tokenizer.do_lower_case = True
tokens = tokenizer(text, add_special_tokens=False)['input_ids']
print("tokens:", tokenizer.convert_ids_to_tokens(tokens))
# tokens: ['▁', 'サラリーマン', '▁', '油', '絵']
print("decoded text:", tokenizer.decode(tokens))
# decoded text: サラリーマン 油絵
```

这一阶段让模型能理解日语 prompt，但由于潜在扩散模型完全未变，仍无法输出日式风格的图像。换言之，日语词 "salary man" 可以被理解成英文词 "businessman"，但生成出来的仍是西方长相的上班族，如下图所示。

![salary man of japanese stable diffusion at stage 1](https://huggingface.co/blog/assets/106_japanese_stable_diffusion/jsd-stage1.jpeg)

*"サラリーマン 油絵", which means exactly "salary man, oil painting", from the 1st-stage Japanese Stable Diffusion*

因此，第二阶段我们训练模型输出更日式风格的图像。

#### 第二阶段：联合微调文本编码器与潜在扩散模型

第二阶段同时训练文本编码器和潜在扩散模型以生成日式图像。这一阶段对让模型变得更加语言专属至关重要。经过此阶段后，模型终于能生成下图所示的、日本面孔的上班族。

![salary man of japanese stable diffusion](https://huggingface.co/blog/assets/106_japanese_stable_diffusion/jsd-stage2.jpeg)

*"サラリーマン 油絵", which means exactly "salary man, oil painting", from the 2nd-stage Japanese Stable Diffusion*

## rinna 的开放策略

众多研究机构本着 AI 民主化的理念——让人人都能轻松使用 AI——发布自己的研究成果。特别是近来，基于大规模训练数据、参数量巨大的预训练模型成为主流，人们担心高性能 AI 会被拥有算力资源的研究机构垄断。好在幸运的是，已有许多预训练模型发布，为 AI 技术的发展做出了贡献。然而，文本类预训练模型往往面向世界上最通用的语言——英语。我们认为，对于人人都能轻松使用 AI 的世界，能在英语之外的语言中使用最先进 AI 是理想的。

因此，rinna 公司发布了日语专属的 [GPT](https://huggingface.co/rinna/japanese-gpt-1b)、[BERT](https://huggingface.co/rinna/japanese-roberta-base) 和 [CLIP](https://huggingface.co/rinna/japanese-clip-vit-b-16)，如今又发布了 [Japanese Stable Diffusion](https://huggingface.co/rinna/japanese-stable-diffusion)。通过发布日语专属预训练模型，我们希望让 AI 不偏向英语世界的文化，同时容纳日语世界的文化。让人人都能使用它，将有助于民主化一种保障日本文化认同的 AI。

## 未来方向

与 Stable Diffusion 相比，Japanese Stable Diffusion 通用性稍逊，仍存在一些精度问题。但通过开发和发布 Japanese Stable Diffusion，我们希望向研究社区传达语言专属模型开发的重要性和潜力。

rinna 公司已发布面向日语文本的 GPT 和 BERT 模型，以及面向日语文本与图像的 CLIP、CLOOB 和 Japanese Stable Diffusion 模型。我们将持续改进这些模型，下一步计划发布专门面向日语语音的自监督学习模型。
