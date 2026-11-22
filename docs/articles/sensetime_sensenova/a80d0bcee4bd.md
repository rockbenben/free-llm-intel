---
vendor: sensetime_sensenova
title: SenseNova-SI-1.3-InternVL3-8B
original_title: 
url: https://huggingface.co/sensenova/SenseNova-SI-1.3-InternVL3-8B
date: 2026-01-08
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: llm
status: translated
body_sha: 13a97c812e7c
---

**EN** | [中文](https://huggingface.co/sensenova/SenseNova-SI-1.3-InternVL3-8B/blob/main/README_CN.md)

# SenseNova-SI：以多模态基础模型扩展空间智能

![Code](https://img.shields.io/badge/SenseNova_SI-Code-100000?style=flat-square&logo=github&logoColor=white)

![arXiv](https://img.shields.io/badge/arXiv-SenseNova_SI-red?logo=arxiv)

![Code](https://img.shields.io/badge/EASI-Code-100000?style=flat-square&logo=github&logoColor=white)

![Leaderboard](https://img.shields.io/badge/%F0%9F%A4%97%20_EASI-Leaderboard-ffc107?color=ffc107&logoColor=white)

## 概述

尽管取得了显著进展，多模态基础模型在空间智能方面仍表现出令人意外的不足。在本工作中，我们探索通过扩展多模态基础模型，在 **SenseNova-SI 系列**中培养空间智能；该系列构建于现有多模态基础之上，包括视觉理解模型（即 Qwen3-VL 和 InternVL3）以及统一理解与生成模型（即 Bagel）。我们采用一套有原则的方法构建高性能且稳健的空间智能，即通过系统化整理 SenseNova-SI-8M：在严格的空间能力分类体系下包含八百万个多样化数据样本。SenseNova-SI 在广泛的空间智能基准上展现出前所未有的性能，同时保持强大的通用多模态理解能力。更重要的是，我们分析了数据扩展的影响，讨论了多样化数据训练所催生的涌现泛化能力的早期迹象，分析了过拟合与语言捷径的风险，给出了关于空间思维链推理的初步研究，并验证了潜在的下游应用。SenseNova-SI 是一个持续进行的项目，本报告将不断更新。所有新训练的多模态基础模型均已公开发布，以促进该方向的进一步研究。*未来，SenseNova-SI 将与更大规模的内部模型集成。*

## 发布信息

目前，我们在流行的开源基础模型之上构建 SenseNova-SI，以最大限度地兼容现有的研究流程。本次发布中，我们推出 [**SenseNova-SI-1.3-InternVL3-8B**](https://huggingface.co/sensenova/SenseNova-SI-1.3-InternVL3-8B)、[**SenseNova-SI-1.2-InternVL3-8B**](https://huggingface.co/sensenova/SenseNova-SI-1.2-InternVL3-8B)、[**SenseNova-SI-1.1-Qwen2.5-VL-3B**](https://huggingface.co/sensenova/SenseNova-SI-1.1-Qwen2.5-VL-3B)、[**SenseNova-SI-1.1-Qwen2.5-VL-7B**](https://huggingface.co/sensenova/SenseNova-SI-1.1-Qwen2.5-VL-7B) 和 [**SenseNova-SI-1.1-Qwen3-VL-8B**](https://huggingface.co/sensenova/SenseNova-SI-1.1-Qwen3-VL-8B)，其中 **SenseNova-SI-1.3-InternVL3-8B** 在八个近期空间智能基准——**VSI**、**MMSI**、**MindCube**、**ViewSpatial**、**SITE**、**BLINK**、**3DSRBench**、**EmbSpatial-Bench**——上，在同规模开源模型中达到最先进性能。与先前版本相比，它还提升了开放式空间问答能力。

| 模型 | VSI | MMSI | MindCube-Tiny | ViewSpatial | SITE | BLINK | 3DSRBench | EmbSpatial-Bench |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| *开源模型 (~2B)* |  |  |  |  |  |  |  |  |
| InternVL3-2B | 32.9 | 26.5 | 37.5 | 32.5 | 30.0 | 50.8 | 47.7 | 60.1 |
| Qwen3-VL-2B-Instruct | 50.3 | 28.9 | 34.5 | 36.9 | 35.6 | 53.2 | 47.5 | 70.1 |
| MindCube-3B-RawQA-SFT | 17.2 | 1.7 | 51.7 | 24.1 | 6.3 | 35.1 | 2.8 | 37.0 |
| SpatialLadder-3B | 44.8 | 27.4 | 43.4 | 39.8 | 27.9 | 43.0 | 42.8 | 58.2 |
| SpatialMLLM-4B | 46.3 | 26.1 | 33.4 | 34.6 | 18.0 | 40.5 | 36.2 | 50.0 |
| VST-3B-SFT | 57.9 | 30.2 | 35.9 | 52.8 | 35.8 | 58.8 | 54.1 | 69.0 |
| Cambrian-S-3B | 57.3 | 25.2 | 32.5 | 39.0 | 28.3 | 37.7 | 50.9 | 63.5 |
| *开源模型 (~8B)* |  |  |  |  |  |  |  |  |
| InternVL3-8B | 42.1 | 28.0 | 41.5 | 38.6 | 41.1 | 53.5 | 44.3 | 76.4 |
| Qwen3-VL-8B-Instruct | 57.9 | 31.1 | 29.4 | 42.2 | 45.8 | 66.7 | 53.9 | 77.7 |
| BAGEL-7B-MoT | 31.4 | 31.0 | 34.7 | 41.3 | 37.0 | 63.7 | 50.2 | 73.1 |
| SpaceR-7B | 41.5 | 27.4 | 37.9 | 35.8 | 34.2 | 49.6 | 40.5 | 66.9 |
| ViLaSR-7B | 44.6 | 30.2 | 35.1 | 35.7 | 38.7 | 51.4 | 46.6 | 67.3 |
| VST-7B-SFT | 60.6 | 32.0 | 39.7 | 50.5 | 39.6 | 61.9 | 54.6 | 73.7 |
| Cambrian-S-7B | 67.5 | 25.8 | 39.6 | 40.9 | 33.0 | 37.9 | 54.8 | 72.8 |
| **SenseNova-SI-1.3-InternVL3-8B** | **68.6** | **42.5** | **89.9** | **61.3** | **47.5** | **68.0** | **62.4** | **81.0** |
| *专有模型* |  |  |  |  |  |  |  |  |
| Gemini-2.5-pro-2025-06 | 53.5 | 38.0 | 57.6 | 46.0 | 57.0 | 73.5 | 59.3 | 78.9 |
| Grok-4-2025-07-09 | 47.9 | 37.8 | 63.5 | 43.2 | 47.0 | 56.4 | 54.9 | 75.7 |
| GPT-5-2025-08-07 | 55.0 | 41.8 | 56.3 | 45.5 | 61.8 | 68.0 | 60.3 | 81.6 |

## 🛠️ 快速开始

### 安装

我们推荐使用 [uv](https://docs.astral.sh/uv/) 管理环境。

> uv 安装指南：https://docs.astral.sh/uv/getting-started/installation/#installing-uv

```
git clone git@github.com:OpenSenseNova/SenseNova-SI.git
cd SenseNova-SI/
uv sync --extra cu124 # or one of [cu118|cu121|cu124|cu126|cu128|cu129], depending on your CUDA version
uv sync
source .venv/bin/activate
```

#### Hello World

一个简单的无图测试，用于验证环境设置并下载模型。

```
python example.py \
  --question "Hello" \
  --model_path sensenova/SenseNova-SI-1.3-InternVL3-8B
```

### 示例

#### 示例 1

本示例来自 [SITE-Bench](https://github.com/wenqi-wang20/SITE-Bench)：

```
python example.py \
  --image_paths examples/Q1_1.png \
  --question "Consider the real-world 3D locations of the objects. Which is closer to the sink, the toilet paper or the towel?\nOptions: \nA. toilet paper\nB. towel\nGive me the answer letter directly. The best answer is:" \
  --model_path sensenova/SenseNova-SI-1.3-InternVL3-8B
# --model_path sensenova/SenseNova-SI-1.1-Qwen3-VL-8B
```

**示例 1 详情**

**问：**考虑物体的真实世界 3D 位置。哪个离水槽更近，卫生纸还是毛巾？\n选项：\nA. 卫生纸\nB. 毛巾\n直接给出答案字母。最佳答案是：

| ![First image](https://huggingface.co/sensenova/SenseNova-SI-1.3-InternVL3-8B/resolve/main/examples/Q1_1.png) |
| --- |

**GT: A**

#### 示例 2

本示例来自 [MMSI-Bench](https://github.com/InternRobotics/MMSI-Bench)：

```
python example.py \
  --image_paths examples/Q2_1.png examples/Q2_2.png \
  --question "If the landscape painting is on the east side of the bedroom, where is the window located in the bedroom?\nOptions: A. North side, B. South side, C. West side, D. East side\nAnswer with the option's letter from the given choices directly. Enclose the option's letter within ``." \
  --model_path sensenova/SenseNova-SI-1.3-InternVL3-8B 
# --model_path sensenova/SenseNova-SI-1.1-Qwen3-VL-8B
```

**示例 2 详情**

**问：**如果风景画位于卧室东侧，那么窗户位于卧室的哪里？\n选项：A. 北侧，B. 南侧，C. 西侧，D. 东侧\n直接使用给定选项中的字母作答。将选项字母括在 `` 中。

| ![First image](https://huggingface.co/sensenova/SenseNova-SI-1.3-InternVL3-8B/resolve/main/examples/Q2_1.png) | ![Second image](https://huggingface.co/sensenova/SenseNova-SI-1.3-InternVL3-8B/resolve/main/examples/Q2_2.png) |
| --- | --- |

**GT: C**

#### 示例 3

本示例来自 [MMSI-Bench](https://github.com/InternRobotics/MMSI-Bench)，并测试模型在开放式简答题上的能力：

```
python example.py \
  --image_paths examples/Q3_1.png examples/Q3_2.png examples/Q3_3.png \
  --question "The robot is making tea. What is the order in which the pictures were taken?" \
  --model_path sensenova/SenseNova-SI-1.3-InternVL3-8B
```

**示例 3 详情**

**问：**机器人正在泡茶。这些照片拍摄的顺序是什么？

| ![First image](https://huggingface.co/sensenova/SenseNova-SI-1.3-InternVL3-8B/resolve/main/examples/Q3_1.png) | ![Second image](https://huggingface.co/sensenova/SenseNova-SI-1.3-InternVL3-8B/resolve/main/examples/Q3_2.png) | ![Third image](https://huggingface.co/sensenova/SenseNova-SI-1.3-InternVL3-8B/resolve/main/examples/Q3_3.png) |
| --- | --- | --- |

**GT: 第二、第一、第三**

#### 单次运行测试多个问题

准备一个类似 [examples/examples.jsonl](https://huggingface.co/sensenova/SenseNova-SI-1.3-InternVL3-8B/blob/main/examples/examples.jsonl) 的文件，其中每一行表示单个问题。

模型仅加载一次，并按顺序处理问题。各问题之间保持相互独立。

> 有关 jsonl 格式的更多细节，请参阅单图像数据和多图像数据的文档。

```
python example.py \
  --jsonl_path examples/examples.jsonl \
  --model_path sensenova/SenseNova-SI-1.3-InternVL3-8B 
# --model_path OpenGVLab/InternVL3-8B 
```

### 评估

如需复现上述基准结果，请参考 [EASI](https://github.com/EvolvingLMMs-Lab/EASI) 在主流空间智能基准上评估 SenseNova-SI。

## 🖊️ 引用

```
@InProceedings{sensenova-si,
  title = {Scaling Spatial Intelligence with Multimodal Foundation Models},
  author = {Cai, Zhongang and Wang, Ruisi and Gu, Chenyang and Pu, Fanyi and Xu, Junxiang and Wang, Yubo and Yin, Wanqi and Yang, Zhitao and Wei, Chen and Sun, Qingping and Zhou, Tongxi and Li, Jiaqi and Pang, Hui En and Qian, Oscar and Wei, Yukun and Lin, Zhiqian and Shi, Xuanke and Deng, Kewang and Han, Xiaoyang and Chen, Zukai and Fan, Xiangyu and Deng, Hanming and Lu, Lewei and Pan, Liang and Li, Bo and Liu, Ziwei and Wang, Quan and Lin, Dahua and Yang, Lei},
  booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
  year = {2026}
}
```

上月下载量

132

Safetensors

模型规模

8B 参数

张量类型

BF16


## sensenova/SenseNova-SI-1.3-InternVL3-8B 的模型树

基础模型

OpenGVLab/InternVL3-8B-Pretrained

微调

OpenGVLab/InternVL3-8B-Instruct

微调

OpenGVLab/InternVL3-8B

微调

([37](https://huggingface.co/models?other=base_model:finetune:OpenGVLab/InternVL3-8B))

本模型

适配器

1 个模型

## 包含 sensenova/SenseNova-SI-1.3-InternVL3-8B 的合集

以多模态基础模型扩展空间智能 • 16 个项目 • 更新于 2 天前 •  25

## sensenova/SenseNova-SI-1.3-InternVL3-8B 的论文

论文 • 2511.13719 • 发布于 Nov 17, 2025 •  50
