---
vendor: huggingface
title: 介绍 SynthID Text
original_title: Introducing SynthID Text
url: https://huggingface.co/blog/synthid-text
date: 2025-02-17
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 7b4d5bb29a64
translator: agent
---

返回文章列表

# 介绍 SynthID Text

发布于
					2024 年 10 月 23 日

在 GitHub 上更新



- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63ce875d199b36f7552d4f07/bpUrvhXDagzRqZ3vxTcSF.jpeg)](https://huggingface.co/marcsun13)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/61868ce808aae0b5499a2a95/F6BA0anbsoY_Z7M1JrwOe.jpeg)](https://huggingface.co/fffiloni)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6527e89a8808d80ccff88b7a/CuGNmF1Et8KMQ0mCd1NEJ.jpeg)](https://huggingface.co/not-lain)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64a0784d7b57fab3a5d63868/iqA0qF0nYAstSWsSS94RH.png)](https://huggingface.co/Erfan-Shayegani)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1677134945205-62f32eab52ad88c930bb3f3b.png)](https://huggingface.co/codelion)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1613511937628-5fb15d1e84389b139cf3b508.jpeg)](https://huggingface.co/MoritzLaurer)

Sumedh Ghaisas

sumedhghaisas

客座作者

Sumanth Dathathri

sdathath

客座作者

Ryan Mullins

RyanMullins

客座作者

Joao Gante

joaogante

Marc Sun

marcsun13

Raushan Turganbay

RaushanTurganbay

本文另有中文版本 [简体中文](https://huggingface.co/blog/zh/synthid-text)。

你觉得难以分辨一段文字是人写的还是 AI 生成的吗？能够识别 AI 生成内容，对促进信息可信度至关重要，也有助于应对错误归属（misattribution）和虚假信息等问题。今天，[Google DeepMind](https://deepmind.google/) 和 Hugging Face 很高兴在 Transformers v4.46.0 中推出 [SynthID Text](https://deepmind.google/technologies/synthid/)（该版本今天稍晚发布）。这项技术可以通过一个用于生成任务的[logits 处理器](https://huggingface.co/docs/transformers/v4.46.0/en/internal/generation_utils#transformers.SynthIDTextWatermarkLogitsProcessor)给 AI 生成的文本加水印，并用一个[分类器](https://huggingface.co/docs/transformers/v4.46.0/en/internal/generation_utils#transformers.SynthIDTextWatermarkDetector)检测这些水印。

关于该算法的完整技术细节，请阅读发表于 *Nature* 的 SynthID Text [论文](https://www.nature.com/articles/s41586-024-08025-4)；关于如何在你的产品中应用 SynthID Text，可参阅 Google 的 [Responsible GenAI Toolkit](https://ai.google.dev/responsible/docs/safeguards/synthid)。

## 工作原理

SynthID Text 的首要目标，是把水印编码进 AI 生成的文本，帮助你判断文本是否出自你的 LLM——同时不影响底层 LLM 的运作、不损害生成质量。Google DeepMind 研发的水印技术使用一个伪随机函数（称为 g-function）来增强任意 LLM 的生成过程，使水印对人眼不可察觉，但对训练过的模型可见。它已实现为一个[生成工具](https://huggingface.co/docs/transformers/v4.46.0/en/internal/generation_utils#transformers.SynthIDTextWatermarkLogitsProcessor)：任何 LLM 无需修改、照常用 `model.generate()` API 即可兼容；同时附有如何训练检测器识别水印文本的[端到端示例](https://github.com/huggingface/transformers/tree/v4.46.0/examples/research_projects/synthid_text/detector_training.py)。关于 SynthID Text 算法更完整的细节，请看[研究论文](https://www.nature.com/articles/s41586-024-08025-4)。

## 配置水印

水印通过一个 [dataclass 配置](https://huggingface.co/docs/transformers/v4.46.0/en/internal/generation_utils#transformers.SynthIDTextWatermarkingConfig)，它参数化了 *g*-function 及其在锦标赛采样（tournament sampling）过程中的应用方式。你使用的每个模型都应有自己的水印配置，并且**该配置必须安全、私密地保存**，否则你的水印可能被他人复制。

每份水印配置必须定义两个参数：

- `keys` 参数：一个整数列表，用于在模型的整个词表上计算 *g*-function 分数。推荐使用 20 到 30 个唯一的随机生成数字，以在可检测性与生成质量之间取得平衡。
- `ngram_len` 参数：用于平衡鲁棒性与可检测性。值越大水印越容易被检测，代价是对修改更脆弱。一个好的默认值是 5，但至少要为 2。

你还可以根据性能需求进一步配置水印。更多信息见 [`SynthIDTextWatermarkingConfig` 类](https://huggingface.co/docs/transformers/v4.46.0/en/internal/generation_utils#transformers.SynthIDTextWatermarkingConfig)。

[研究论文](https://www.nature.com/articles/s41586-024-08025-4)里还有关于具体配置取值如何影响水印性能的额外分析。

## 应用水印

给水印上，只是对现有生成调用做一个简单改动。定义好配置后，把 `SynthIDTextWatermarkingConfig` 对象以 `watermarking_config=` 参数传给 `model.generate()`，所有生成的文本就会带上水印。可以看看 [SynthID Text Space](https://huggingface.co/spaces/google/synthid-text) 里的交互式加水印示例，试试你能不能看出来。

```
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    SynthIDTextWatermarkingConfig,
)

# Standard model and tokenizer initialization
tokenizer = AutoTokenizer.from_pretrained('repo/id')
model = AutoModelForCausalLM.from_pretrained('repo/id')

# SynthID Text configuration
watermarking_config = SynthIDTextWatermarkingConfig(
    keys=[654, 400, 836, 123, 340, 443, 597, 160, 57, ...],
    ngram_len=5,
)

# Generation with watermarking
tokenized_prompts = tokenizer(["your prompts here"])
output_sequences = model.generate(
    **tokenized_prompts,
    watermarking_config=watermarking_config,
    do_sample=True,
)
watermarked_text = tokenizer.batch_decode(output_sequences)
```

## 检测水印

水印的设计目标是：可被训练过的分类器检测，但对人类不可感知。你在模型上使用的每份水印配置，都需要一个专门训练来识别该水印的检测器。

检测器训练的基本流程是：

- 确定一份水印配置。
- 收集检测器训练集，按"有水印/无水印"和"训练/测试"划分，建议至少 1 万个样本。
- 用你的模型生成无水印输出。
- 用你的模型生成有水印输出。
- 训练你的水印检测分类器。
- 把模型连同水印配置和对应检测器一起投入生产。

Transformers 提供了[贝叶斯检测器类](https://huggingface.co/docs/transformers/v4.46.0/en/internal/generation_utils#transformers.BayesianDetectorModel)，并附带如何针对特定水印配置训练检测器识别水印文本的[端到端示例](https://github.com/huggingface/transformers/tree/v4.46.0/examples/research_projects/synthid_text/detector_training.py)。使用同一分词器的模型还可以共享水印配置与检测器，即共享同一个水印——前提是检测器的训练集包含所有共享该水印的模型的样本。

训练好的检测器可以上传到私有 HF Hub，供整个组织使用。如何把 SynthID Text 生产化到你的产品里，可参阅 Google 的 [Responsible GenAI Toolkit](https://ai.google.dev/responsible/docs/safeguards/synthid)。

## 局限

SynthID Text 水印对某些变换具有鲁棒性，比如裁剪文本片段、替换少量词语或轻度改写，但这个方法仍有局限。

- 在事实性回答上水印效果较弱，因为没有多少增强生成的空间而不损害准确性。
- 当 AI 生成文本被彻底重写或翻译成另一种语言时，检测器的置信度分数会大幅下降。

SynthID Text 并不是为直接阻止蓄意作恶者而设计的。但它能让把 AI 生成内容用于恶意目的变得更困难，也可以与其他方法结合，在不同内容类型和平台上获得更好的覆盖。

## 致谢

作者们感谢 Robert Stanforth 和 Tatiana Matejovicova 对这项工作的贡献。

## 文中提到的 Spaces 1

我们博客的更多文章

announcement

mlx

llm

## The PR you would have opened yourself

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/623c830997ddced06d78699b/ucB8joTPONCnc_Gj0mssR.jpeg)

74

2026 年 4 月 16 日

announcement

cohere

llm

## A Deepdive into Aya Expanse: Advancing the Frontier of Multilinguality

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/65c581dfc3fa039f843991f6/O4ywGgQQrzps5JYeR3o0y.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1677753847837-62c2175d756039dd0dd20509.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6658011eaba105a066e37e1b/VPwyTv1bnVMQbVMoMQzcf.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/661b21f8ea926e8f86729e61/gM59piqaqjEu2IPbDvCbZ.jpeg)

66

2024 年 10 月 24 日

### 社区

kirudang

2025 年 2 月 17 日


2025 年 2 月 17 日编辑

Hello,

I applied the WM to LLama2 and used the availably trained detector named "joaogante/dummy_synthid_detector".
The output is return probability, not 1 (watermarked) or 0 (unwatermarked).
Could you help me with threshold and how to train the detector?

```
from transformers import (
    AutoTokenizer, BayesianDetectorModel, SynthIDTextWatermarkLogitsProcessor, SynthIDTextWatermarkDetector
)

# Load the detector. See examples/research_projects/synthid_text for training a detector.
detector_model = BayesianDetectorModel.from_pretrained("joaogante/dummy_synthid_detector")
logits_processor = SynthIDTextWatermarkLogitsProcessor(
    **detector_model.config.watermarking_config, device="cpu"
)
tokenizer = AutoTokenizer.from_pretrained(detector_model.config.model_name)
detector = SynthIDTextWatermarkDetector(detector_model, logits_processor, tokenizer)

# Test whether a certain string is watermarked
test_input = tokenizer(["This is a test input"], return_tensors="pt")
is_watermarked = detector(test_input.input_ids)
```

macshsgshedd

2025 年 7 月 22 日

How can i get API access

将文件拖入文本输入框、粘贴，或

点击此处

，即可上传图像、音频和视频。

点击或粘贴此处上传图片

· [注册](https://huggingface.co/join?next=%2Fblog%2Fsynthid-text)或[登录](https://huggingface.co/login?next=%2Fblog%2Fsynthid-text)发表评论



- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63ce875d199b36f7552d4f07/bpUrvhXDagzRqZ3vxTcSF.jpeg)](https://huggingface.co/marcsun13)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/61868ce808aae0b5499a2a95/F6BA0anbsoY_Z7M1JrwOe.jpeg)](https://huggingface.co/fffiloni)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6527e89a8808d80ccff88b7a/CuGNmF1Et8KMQ0mCd1NEJ.jpeg)](https://huggingface.co/not-lain)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64a0784d7b57fab3a5d63868/iqA0qF0nYAstSWsSS94RH.png)](https://huggingface.co/Erfan-Shayegani)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1677134945205-62f32eab52ad88c930bb3f3b.png)](https://huggingface.co/codelion)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1613511937628-5fb15d1e84389b139cf3b508.jpeg)](https://huggingface.co/MoritzLaurer)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/651ea296c887c687e09158af/ju9Zx2xDBVhDLnLL1e1Mq.jpeg)](https://huggingface.co/brunatrevelin)
- [![](https://huggingface.co/avatars/b36027822d6b00831eb9c232031194f0.svg)](https://huggingface.co/Jarrodbarnes)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/65a402a53522df7a27125823/tVR6lZlKmjPqi7dTZBGoS.jpeg)](https://huggingface.co/RyanMullins)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1657623563546-noauth.png)](https://huggingface.co/toxcik)
- [![](https://huggingface.co/avatars/31f8d5a88a8469da13478a9379f597f5.svg)](https://huggingface.co/nikilpatel94)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/61d375fd733d3a83ecd1bba9/oIXwvvs1-HaCnJXMCZgkc.jpeg)](https://huggingface.co/andrewrreed)

## 文中提到的 Spaces 1
