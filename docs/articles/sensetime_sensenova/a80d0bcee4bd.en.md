---
vendor: sensetime_sensenova
title: SenseNova-SI: Scaling Spatial Intelligence with Multimodal Foundation Models
original_title: 
url: https://huggingface.co/sensenova/SenseNova-SI-1.3-InternVL3-8B
date: 2026-11-19
lang: en
captured: 2026-11-21
extractor: readability-v1
status: ok
body_sha: 70fa67afe450
---

**EN** | [中文](https://huggingface.co/sensenova/SenseNova-SI-1.3-InternVL3-8B/blob/main/README_CN.md)

# SenseNova-SI: Scaling Spatial Intelligence with Multimodal Foundation Models

![Code](https://img.shields.io/badge/SenseNova_SI-Code-100000?style=flat-square&logo=github&logoColor=white)

![arXiv](https://img.shields.io/badge/arXiv-SenseNova_SI-red?logo=arxiv)

![Code](https://img.shields.io/badge/EASI-Code-100000?style=flat-square&logo=github&logoColor=white)

![Leaderboard](https://img.shields.io/badge/%F0%9F%A4%97%20_EASI-Leaderboard-ffc107?color=ffc107&logoColor=white)

## Overview

Despite remarkable progress, multimodal foundation models still exhibit surprising deficiencies in spatial intelligence. In this work, we explore scaling up multimodal foundation models to cultivate spatial intelligence within the **SenseNova-SI family**, built upon established multimodal foundations including visual understanding models (i.e., Qwen3-VL and InternVL3) and unified understanding and generation models (i.e., Bagel). We take a principled approach to constructing high-performing and robust spatial intelligence by systematically curating SenseNova-SI-8M: eight million diverse data samples under a rigorous taxonomy of spatial capabilities. SenseNova-SI demonstrates unprecedented performance across a broad range of spatial intelligence benchmarks, while maintaining strong general multimodal understanding. More importantly, we analyze the impact of data scaling, discuss early signs of emergent generalization capabilities enabled by diverse data training, analyze the risk of overfitting and language shortcuts, present a preliminary study on spatial chain-of-thought reasoning, and validate the potential downstream application. SenseNova-SI is an ongoing project, and this report will be updated continuously. All newly trained multimodal foundation models are publicly released to facilitate further research in this direction. *In the future, SenseNova-SI will be integrated with larger-scale in-house models.*

## Release Information

Currently, we build SenseNova-SI upon popular open-source foundation models to maximize compatibility with existing research pipelines. In this release, we present [**SenseNova-SI-1.3-InternVL3-8B**](https://huggingface.co/sensenova/SenseNova-SI-1.3-InternVL3-8B), [**SenseNova-SI-1.2-InternVL3-8B**](https://huggingface.co/sensenova/SenseNova-SI-1.2-InternVL3-8B), [**SenseNova-SI-1.1-Qwen2.5-VL-3B**](https://huggingface.co/sensenova/SenseNova-SI-1.1-Qwen2.5-VL-3B), [**SenseNova-SI-1.1-Qwen2.5-VL-7B**](https://huggingface.co/sensenova/SenseNova-SI-1.1-Qwen2.5-VL-7B), and [**SenseNova-SI-1.1-Qwen3-VL-8B**](https://huggingface.co/sensenova/SenseNova-SI-1.1-Qwen3-VL-8B), of which **SenseNova-SI-1.3-InternVL3-8B** achieve state-of-the-art performance among open-source models of comparable size across eight recent spatial intelligence benchmarks: **VSI**, **MMSI**, **MindCube**, **ViewSpatial**, **SITE**, **BLINK**, **3DSRBench**, **EmbSpatial-Bench**. It also improves open-ended spatial question-answering capabilities compared to previous versions.

| Model | VSI | MMSI | MindCube-Tiny | ViewSpatial | SITE | BLINK | 3DSRBench | EmbSpatial-Bench |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| *Open-source Models (~2B)* |  |  |  |  |  |  |  |  |
| InternVL3-2B | 32.9 | 26.5 | 37.5 | 32.5 | 30.0 | 50.8 | 47.7 | 60.1 |
| Qwen3-VL-2B-Instruct | 50.3 | 28.9 | 34.5 | 36.9 | 35.6 | 53.2 | 47.5 | 70.1 |
| MindCube-3B-RawQA-SFT | 17.2 | 1.7 | 51.7 | 24.1 | 6.3 | 35.1 | 2.8 | 37.0 |
| SpatialLadder-3B | 44.8 | 27.4 | 43.4 | 39.8 | 27.9 | 43.0 | 42.8 | 58.2 |
| SpatialMLLM-4B | 46.3 | 26.1 | 33.4 | 34.6 | 18.0 | 40.5 | 36.2 | 50.0 |
| VST-3B-SFT | 57.9 | 30.2 | 35.9 | 52.8 | 35.8 | 58.8 | 54.1 | 69.0 |
| Cambrian-S-3B | 57.3 | 25.2 | 32.5 | 39.0 | 28.3 | 37.7 | 50.9 | 63.5 |
| *Open-source Models (~8B)* |  |  |  |  |  |  |  |  |
| InternVL3-8B | 42.1 | 28.0 | 41.5 | 38.6 | 41.1 | 53.5 | 44.3 | 76.4 |
| Qwen3-VL-8B-Instruct | 57.9 | 31.1 | 29.4 | 42.2 | 45.8 | 66.7 | 53.9 | 77.7 |
| BAGEL-7B-MoT | 31.4 | 31.0 | 34.7 | 41.3 | 37.0 | 63.7 | 50.2 | 73.1 |
| SpaceR-7B | 41.5 | 27.4 | 37.9 | 35.8 | 34.2 | 49.6 | 40.5 | 66.9 |
| ViLaSR-7B | 44.6 | 30.2 | 35.1 | 35.7 | 38.7 | 51.4 | 46.6 | 67.3 |
| VST-7B-SFT | 60.6 | 32.0 | 39.7 | 50.5 | 39.6 | 61.9 | 54.6 | 73.7 |
| Cambrian-S-7B | 67.5 | 25.8 | 39.6 | 40.9 | 33.0 | 37.9 | 54.8 | 72.8 |
| **SenseNova-SI-1.3-InternVL3-8B** | **68.6** | **42.5** | **89.9** | **61.3** | **47.5** | **68.0** | **62.4** | **81.0** |
| *Proprietary Models* |  |  |  |  |  |  |  |  |
| Gemini-2.5-pro-2025-06 | 53.5 | 38.0 | 57.6 | 46.0 | 57.0 | 73.5 | 59.3 | 78.9 |
| Grok-4-2025-07-09 | 47.9 | 37.8 | 63.5 | 43.2 | 47.0 | 56.4 | 54.9 | 75.7 |
| GPT-5-2025-08-07 | 55.0 | 41.8 | 56.3 | 45.5 | 61.8 | 68.0 | 60.3 | 81.6 |

## 🛠️ QuickStart

### Installation

We recommend using [uv](https://docs.astral.sh/uv/) to manage the environment.

> uv installation guide: https://docs.astral.sh/uv/getting-started/installation/#installing-uv

```
git clone git@github.com:OpenSenseNova/SenseNova-SI.git
cd SenseNova-SI/
uv sync --extra cu124 # or one of [cu118|cu121|cu124|cu126|cu128|cu129], depending on your CUDA version
uv sync
source .venv/bin/activate
```

#### Hello World

A simple image-free test to verify environment setup and download the model.

```
python example.py \
  --question "Hello" \
  --model_path sensenova/SenseNova-SI-1.3-InternVL3-8B
```

### Examples

#### Example 1

This example is from [SITE-Bench](https://github.com/wenqi-wang20/SITE-Bench):

```
python example.py \
  --image_paths examples/Q1_1.png \
  --question "Consider the real-world 3D locations of the objects. Which is closer to the sink, the toilet paper or the towel?\nOptions: \nA. toilet paper\nB. towel\nGive me the answer letter directly. The best answer is:" \
  --model_path sensenova/SenseNova-SI-1.3-InternVL3-8B
# --model_path sensenova/SenseNova-SI-1.1-Qwen3-VL-8B
```

**Details of Example 1**

**Q:**Consider the real-world 3D locations of the objects. Which is closer to the sink, the toilet paper or the towel?\nOptions: \nA. toilet paper\nB. towel\nGive me the answer letter directly. The best answer is:

| ![First image](https://huggingface.co/sensenova/SenseNova-SI-1.3-InternVL3-8B/resolve/main/examples/Q1_1.png) |
| --- |

**GT: A**

#### Example 2

This example is from [MMSI-Bench](https://github.com/InternRobotics/MMSI-Bench):

```
python example.py \
  --image_paths examples/Q2_1.png examples/Q2_2.png \
  --question "If the landscape painting is on the east side of the bedroom, where is the window located in the bedroom?\nOptions: A. North side, B. South side, C. West side, D. East side\nAnswer with the option's letter from the given choices directly. Enclose the option's letter within ``." \
  --model_path sensenova/SenseNova-SI-1.3-InternVL3-8B 
# --model_path sensenova/SenseNova-SI-1.1-Qwen3-VL-8B
```

**Details of Example 2**

**Q:**If the landscape painting is on the east side of the bedroom, where is the window located in the bedroom?\nOptions: A. North side, B. South side, C. West side, D. East side\nAnswer with the option's letter from the given choices directly. Enclose the option's letter within ``.

| ![First image](https://huggingface.co/sensenova/SenseNova-SI-1.3-InternVL3-8B/resolve/main/examples/Q2_1.png) | ![Second image](https://huggingface.co/sensenova/SenseNova-SI-1.3-InternVL3-8B/resolve/main/examples/Q2_2.png) |
| --- | --- |

**GT: C**

#### Example 3

This example is from [MMSI-Bench](https://github.com/InternRobotics/MMSI-Bench) and test the model's capability in open-ended short-answer questions:

```
python example.py \
  --image_paths examples/Q3_1.png examples/Q3_2.png examples/Q3_3.png \
  --question "The robot is making tea. What is the order in which the pictures were taken?" \
  --model_path sensenova/SenseNova-SI-1.3-InternVL3-8B
```

**Details of Example 3**

**Q:**The robot is making tea. What is the order in which the pictures were taken?

| ![First image](https://huggingface.co/sensenova/SenseNova-SI-1.3-InternVL3-8B/resolve/main/examples/Q3_1.png) | ![Second image](https://huggingface.co/sensenova/SenseNova-SI-1.3-InternVL3-8B/resolve/main/examples/Q3_2.png) | ![Third image](https://huggingface.co/sensenova/SenseNova-SI-1.3-InternVL3-8B/resolve/main/examples/Q3_3.png) |
| --- | --- | --- |

**GT: Second, first, third**

#### Test Multiple Questions in a Single Run

Prepare a file similar to [examples/examples.jsonl](https://huggingface.co/sensenova/SenseNova-SI-1.3-InternVL3-8B/blob/main/examples/examples.jsonl), where each line represents a single question.

The model is loaded once and processes questions sequentially. The questions remain independent of each other.

> For more details on the jsonl format, refer to the documentation for Single-Image Data and Multi-Image Data.

```
python example.py \
  --jsonl_path examples/examples.jsonl \
  --model_path sensenova/SenseNova-SI-1.3-InternVL3-8B 
# --model_path OpenGVLab/InternVL3-8B 
```

### Evaluation

To reproduce the benchmark results above, please refer to [EASI](https://github.com/EvolvingLMMs-Lab/EASI) to evaluate SenseNova-SI on mainstream spatial intelligence benchmarks.

## 🖊️ Citation

```
@InProceedings{sensenova-si,
  title = {Scaling Spatial Intelligence with Multimodal Foundation Models},
  author = {Cai, Zhongang and Wang, Ruisi and Gu, Chenyang and Pu, Fanyi and Xu, Junxiang and Wang, Yubo and Yin, Wanqi and Yang, Zhitao and Wei, Chen and Sun, Qingping and Zhou, Tongxi and Li, Jiaqi and Pang, Hui En and Qian, Oscar and Wei, Yukun and Lin, Zhiqian and Shi, Xuanke and Deng, Kewang and Han, Xiaoyang and Chen, Zukai and Fan, Xiangyu and Deng, Hanming and Lu, Lewei and Pan, Liang and Li, Bo and Liu, Ziwei and Wang, Quan and Lin, Dahua and Yang, Lei},
  booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
  year = {2026}
}
```

Downloads last month

132

Safetensors

Model size

8B params

Tensor type

BF16


## Model tree for sensenova/SenseNova-SI-1.3-InternVL3-8B

Base model

OpenGVLab/InternVL3-8B-Pretrained

Finetuned

OpenGVLab/InternVL3-8B-Instruct

Finetuned

OpenGVLab/InternVL3-8B

Finetuned

([37](https://huggingface.co/models?other=base_model:finetune:OpenGVLab/InternVL3-8B))

this model

Adapters

1 model

## Collection including sensenova/SenseNova-SI-1.3-InternVL3-8B

Scaling Spatial Intelligence with Multimodal Foundation Models • 16 items • Updated 2 days ago •  25

## Paper for sensenova/SenseNova-SI-1.3-InternVL3-8B

Paper • 2511.13719 • Published Nov 17, 2025 •  50
