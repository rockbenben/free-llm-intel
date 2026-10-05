---
vendor: huggingface
title: HuggingFace 与 IISc 合作，为印度多元语言的模型构建加速
original_title: HuggingFace, IISc partner to supercharge model building on India's diverse languages
url: https://huggingface.co/blog/iisc-huggingface-collab
date: 2026-09-17
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# HuggingFace 与 IISc 合作，为印度多元语言的模型构建加速

印度科学理工学院 [IISc](https://iisc.ac.in/) 与 [ARTPARK](https://artpark.in/) 同 Hugging Face 达成合作，让全球开发者都能访问 [Vaani](https://vaani.iisc.ac.in/)——印度语言多样性最丰富的开源多模态多语言数据集。双方共同致力于构建包容、可及、最先进的 AI 技术，尊重语言与文化多样性。

## 合作

Hugging Face 与 IISc/ARTPARK 的合作旨在提升 Vaani 数据集的可访问性并改善易用性，鼓励开发更好地理解印度多元语言、满足其人民数字需求的 AI 系统。

## 关于 Vaani 数据集

Project Vaani 由 IISc/ARTPARK 和 Google 于 2022 年发起，是一项开创性计划，目标是创建真正代表印度语言多样性的开源多模态数据集。该数据集以地理为中心的采集方式独树一帜，能够收集偏远地区使用的方言和语言，而非只关注主流语言。

Vaani 的目标是从全部 773 个地区（district）的 100 万人处收集超过 15 万小时语音和 1.5 万小时转写文本数据，确保语言、方言和人口的多样性。

数据集分阶段构建：第一阶段覆盖 80 个地区，已经开源；第二阶段正在进行，把数据集扩展到另外 100 个地区，进一步增强 Vaani 在印度多元语言版图中的覆盖面与影响力。

[![Key Highlights](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/iisc-huggingface-collab/Vaani_Dataset_summary.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/iisc-huggingface-collab/Vaani_Dataset_summary.png) *Key Highlights of the Vaani data set, open sourced so far: (as of 15-02-2025)*

### 分地区的语言分布

Vaani 数据集展现了印度各地区丰富的语言分布，凸显地方层面的语言多样性。这些信息对想为特定地区和方言定制语音模型的研究者、AI 开发者和语言技术创新者非常有价值。要查看详细的分地区语言分布，请访问：[Vaani Dataset on HuggingFace](https://huggingface.co/datasets/ARTPARK-IISc/Vaani)

### 转写子集

如果你只需要访问转写数据、希望跳过未转写的纯音频数据，可以从这里获取大数据集的一个开源子集。该数据集包含 790 小时转写音频，来自约 70 万说话人、覆盖 7 万张图像。这个资源包含与精确转写匹配的更小的分段语音单元，可用于多种任务，包括：

- 语音识别：训练精确转写口语的模型。
- 语言建模：构建更精细的语言模型。
- 分段任务：识别不同的语音单元以提高转写准确率。

这份附加数据集与主 Vaani 数据集互补，使构建端到端语音识别系统和更有针对性的 AI 解决方案成为可能。

## LLM 时代中 Vaani 的用途

Vaani 数据集有多项关键优势，包括广泛的语言覆盖（54 种语言）、多元地理区域的代表性、多样的教育与社会经济背景、庞大的说话人覆盖、自发语音数据，以及真实环境的采集场景。这些特性可以支撑包容性 AI 模型用于：

- 语音转文本与文本转语音：面向 LLM 及非 LLM 应用微调这些模型。此外，转写标注支持开发代码转换（印度语言与英语混用）ASR 模型。
- 面向印度语言的基础语音模型：数据集显著的语言与地理覆盖，支撑健壮的印度语言基础模型开发。
- 说话人识别/验证模型：拥有超过 8 万说话人的数据，该数据集非常适合开发健壮的说话人识别与验证模型。
- 语言识别模型：支持面向各种真实应用的语向识别模型。
- 语音增强系统：数据集的标注体系支持先进语音增强技术的开发。
- 增强多模态 LLM：独特的数据采集方式使其在与其他多模态数据集结合时，对构建和提升 LLM 的多模态能力很有价值。
- 性能基准：得益于其多样的语言、地理和真实世界数据属性，该数据集是语音模型基准测试的理想选择。

这些 AI 模型可以驱动广泛的对话式 AI 应用。从教育工具到远程医疗平台、医疗解决方案、选民热线、媒体本地化和多语言智能设备，Vaani 数据集可能在真实场景中带来变革。

## 下一步

IISc/ARTPARK 与 Google 已把合作扩展到第二阶段（新增 100 个地区）。由此，Vaani 覆盖了印度所有邦！我们很高兴把这份数据集带给大家。

[![Map of districts where data has been collected](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/iisc-huggingface-collab/district_map.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/iisc-huggingface-collab/district_map.png) *The map highlights the districts across India where data has been collected as of Feb 5,2025*

## 你可以如何贡献

最有意义的贡献就是使用 Vaani 数据集。无论你是在构建新的 AI 应用、开展研究还是探索创新用例，你的参与都会帮助项目改进和扩张。

如果你有使用数据集后的反馈或洞见，我们非常乐意聆听。请联系 [vaanicontact@gmail.com](mailto:vaanicontact@gmail.com) 分享你的体验/咨询合作机会，或填写这份[反馈表](https://docs.google.com/forms/d/e/1FAIpQLSdJ_oMoafkVabj0vgfbTsmECyFFQmbVy3b18NOsxUhYVJKeDQ/viewform)。

为印度的语言多样性用 ❤️ 打造
