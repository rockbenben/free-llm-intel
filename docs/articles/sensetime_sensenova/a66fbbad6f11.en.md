---
vendor: sensetime_sensenova
title: Vision as Unified Multimodal Generation
original_title: 
url: https://huggingface.co/sensenova/SenseNova-Vision-7B-MoT
date: 2026-11-19
lang: en
captured: 2026-11-21
extractor: readability-v1
status: ok
body_sha: be290b9275dd
---

# Vision as Unified Multimodal Generation

**English** | [简体中文](https://huggingface.co/sensenova/SenseNova-Vision-7B-MoT/blob/main/README_CN.md)

[![GitHub Stars](https://img.shields.io/github/stars/OpenSenseNova/SenseNova-Vision?style=social)](https://github.com/OpenSenseNova/SenseNova-Vision) [![arXiv](https://img.shields.io/badge/arXiv-2607.06560-b31b1b.svg)](https://arxiv.org/abs/2607.06560) [![](https://img.shields.io/static/v1?label=%F0%9F%A4%97%20Hugging%20Face&message=Model&color=green)](https://huggingface.co/sensenova/SenseNova-Vision-7B-MoT) [![](https://img.shields.io/static/v1?label=%F0%9F%A4%97%20Hugging%20Face&message=Dataset&color=yellow)](https://huggingface.co/datasets/sensenova/SenseNova-Vision-Corpus-50M) [![ModelScope Model](https://img.shields.io/badge/🤖%20ModelScope-Model-blue)](https://modelscope.cn/models/SenseNova/SenseNova-Vision-7B-MoT) [![License](https://img.shields.io/badge/License-CC%20BY--NC%204.0-blue.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

![SenseNova-Vision handles diverse vision tasks in a unified model](https://huggingface.co/sensenova/SenseNova-Vision-7B-MoT/resolve/main/assets/fig1_one_case_for_all.webp)

![SenseNova-Vision system overview](https://huggingface.co/sensenova/SenseNova-Vision-7B-MoT/resolve/main/assets/fig2_system_overview.webp)

## 🌟 Overview

SenseNova-Vision is a unified multimodal model for computer vision. It reformulates heterogeneous visual perception tasks as **text generation**, **image generation**, or **mixed text-image generation**, instead of relying on task-specific heads, decoders, or loss functions for each individual task. The model supports structured visual understanding, dense geometric prediction, segmentation, and multi-view visual geometry within a shared instruction-following interface.

## 🚀 Model Description

SenseNova-Vision rethinks computer vision as **unified multimodal generation**. Traditional computer-vision systems usually attach task-specific prediction heads for detection, segmentation, depth, surface normal, or 3D geometry. SenseNova-Vision instead expresses these heterogeneous tasks through the native input-output spaces of a unified multimodal model.

Natural-language instructions and optional visual prompts specify the target task, regions, views, output schema, and decoding convention. The model then generates different target formats depending on the task:

| Target type | Representative tasks | Output form |
| --- | --- | --- |
| Structured text | Detection, referring localization, OCR, GUI grounding, keypoints, camera parameters | Text records with normalized coordinates or structured fields |
| Dense image | Depth, surface normal, point maps, binary masks, color-coded masks | Image-like target maps |
| Mixed text-image | Multi-instance segmentation, grounded conversation segmentation, compositional perception | Text labels plus generated masks or visual maps |

This formulation allows a single model to cover structured visual understanding, dense geometric prediction, segmentation, and multi-view visual geometry while keeping outputs decodable for standard benchmarks.

## 🌐 Key Features

- **Unified vision-task formulation:** Heterogeneous computer-vision tasks are cast into the native text, image, and mixed generation spaces of a unified multimodal model.
- **No task-specific heads:** The model does not rely on separate detection, segmentation, depth, normal, or geometry heads.
- **Decodable outputs:** Generated text and images can be converted back into benchmark-compatible boxes, points, OCR strings, masks, depth maps, normal maps, point maps, and camera records.
- **Broad task coverage:** The same model handles structured visual understanding, segmentation, dense geometry, and multi-view visual geometry.
- **Instruction-defined task variants:** Natural-language instructions enable flexible task definitions beyond fixed benchmark schemas.

## 🛠️ How to Use

Please use the official inference code from the SenseNova-Vision GitHub repository:

```
git clone https://github.com/OpenSenseNova/SenseNova-Vision.git
cd SenseNova-Vision
```

### Environment Setup

Create the environment from the repository root:

```
bash setup.sh sensenova-vision
conda activate sensenova-vision
```

### Download the Model

You can download the model weights from Hugging Face with `huggingface_hub`:

```
from huggingface_hub import snapshot_download

model_path = snapshot_download("sensenova/SenseNova-Vision-7B-MoT")
print(model_path)
```

The printed `model_path` points to the local checkpoint directory and can be used as the model path for inference.

### Run the Curated Example

We provide a curated example to quickly verify the environment and model setup:

```
bash scripts/run_sensenova_vision.sh example
```

### Run One Inference Request

You can also run a single inference request with the official wrapper.
For example, the following command performs binary segmentation for the target category `"person"`:

```
bash scripts/run_sensenova_vision.sh inference \
  binary_seg \
  "person" \
  examples/images/2.jpg
```

### Launch the Web Demo

You can launch the Gradio web demo using the official wrapper provided in the repository.
The wrapper will print the local URL before starting Gradio. Open the printed URL in your browser to interact with the model.

For more details, supported tasks, and additional examples, please refer to the official GitHub repository:

```
https://github.com/OpenSenseNova/SenseNova-Vision
```

## 🏗️ Key Contributions

- 🔗 We introduce a unified multimodal generation formulation that casts heterogeneous computer vision tasks into the native input-output spaces of UMMs.
- 🧩 We construct the SenseNova-Vision Corpus, a large-scale computer-vision instruction-response corpus with decodable text, image, and mixed text-image targets.
- ✨ We train SenseNova-Vision and show strong results across structured visual understanding, dense geometric prediction, segmentation, and multi-view visual geometry, while supporting language-defined task variants beyond fixed benchmark schemas.

## 🏆 Benchmark Results

SenseNova-Vision is evaluated across structured visual understanding, dense geometric prediction, segmentation, and multi-view visual geometry. All tasks are formulated with natural-language instructions: textual outputs are parsed into benchmark-specific structures such as boxes, points, recognized text, keypoints, and camera parameters, while image outputs are decoded into masks, depth maps, normal maps, or 3D point maps.

### Structured Visual Understanding

Structured visual understanding evaluates tasks whose outputs can be represented as structured textual predictions, including box- and point-based localization, referring detection, OCR localization, GUI grounding, and keypoint localization.

| Method | Object Detection | OCR | GUI | Keypoint |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| COCO-Com. | HR/RefCOCOg V/T | LVIS | Dense200 | VisDrone | HierText | ICDAR15 | ScreenSpot-V2 | COCO-Kpt. |  |  |
| bbox | bbox | bbox | bbox | bbox | point | bbox | bbox | bbox | point |  |
| Grounding DINO-Swin-T | **56.6** | 25.2 / 45.9 / 46.8 | 38.8 | 33.1 | 38.5 | -- | -- | -- | -- | -- |
| Bagel | 50.2 | 74.6 / 76.4 / 77.8 | 46.8 | 42.4 | 23.0 | 36.9 | 7.1 | 15.8 | 81.1 | -- |
| Qwen3-VL-8B-Instruct | 46.6 | 70.4 / 72.3 / 72.6 | 43.2 | 13.5 | 28.7 | 35.7 | 22.4 | 25.4 | 90.5 | -- |
| Qwen3.5-9B | 49.3 | 71.7 / 72.1 / 72.6 | 43.2 | 27.5 | 26.8 | 41.7 | 19.6 | 11.4 | **92.2** | -- |
| LocateAnything | 54.7 | 78.7 / 76.7 / 77.6 | 50.7 | 58.7 | 39.9 | 60.4 | 29.1 | 26.4 | 85.5 | -- |
| Rex-Omni | 52.9 | 79.9 / 73.6 / 74.3 | 46.9 | 58.3 | 35.8 | 58.9 | 28.0 | 28.1 | 88.4 | 32.6 |
| SenseNova-Vision | **56.6** | **80.2** / **79.6** / **80.5** | **54.8** | **66.8** | **43.3** | **62.9** | **31.2** | **49.5** | 85.9 | **34.6** |

### Dense Geometric Prediction

Dense geometric prediction evaluates pixel-aligned geometric outputs, including monocular depth estimation and surface normal estimation.

| Method | Depth | Normal |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NYUv2 | KITTI | ETH3D | ScanNet | DIODE | ScanNet | iBims-1 | NYUv2 |  |
| AbsRel↓ / δ1↑ | Mean↓ / 11.25°↑ |  |  |  |  |  |  |  |
| DSINE | -- | -- | -- | -- | -- | 16.2 / 61.0 | 17.1 / 67.4 | 16.4 / 59.6 |
| DepthAnything | 4.3 / **98.1** | 7.6 / 94.7 | 12.7 / 88.2 | 4.3 / 98.1 | 26.0 / 75.9 | -- | -- | -- |
| DepthAnything V2 | 4.5 / 97.9 | 7.4 / 94.6 | 13.1 / 86.5 | 4.2 / 97.8 | 26.5 / 73.4 | -- | -- | -- |
| *MoGe-2 | **3.5** / 98.0 | **5.5** / **97.7** | **3.4** / **98.8** | **3.4** / **98.3** | **23.0** / **82.3** | **12.8** / **68.4** | **14.7** / **70.4** | **14.7** / **62.3** |
| Marigold | 5.5 / 96.4 | 9.9 / 91.6 | 6.5 / 95.9 | 6.4 / 95.2 | 30.8 / 77.3 | 21.3 / 45.6 | 18.5 / 64.7 | 20.9 / 50.5 |
| DICEPTION | 6.1 / 96.0 | 6.9 / 94.9 | 5.0 / 97.5 | 7.2 / 94.4 | 28.9 / 72.2 | 18.8 / 53.6 | -- | 18.3 / 52.9 |
| FE2E | 4.1 / 97.7 | 6.6 / **96.0** | **3.8** / **98.7** | 4.4 / 97.5 | 22.8 / **81.2** | 13.8 / 67.2 | **15.1** / **70.6** | 16.2 / 59.6 |
| Lotus-2 | 4.1 / 97.6 | 6.7 / 94.5 | 4.6 / 98.1 | 4.2 / 97.6 | 22.1 / 75.2 | 14.2 / 66.8 | 15.4 / 70.4 | 16.9 / 59.0 |
| SenseNova-Vision | **4.0** / **98.1** | **5.9** / 95.9 | 4.3 / 97.4 | **3.9** / **98.0** | **20.6** / 76.4 | **12.8** / **68.9** | 15.4 / 69.1 | **14.4** / **62.7** |

### Segmentation

Segmentation evaluates mask prediction under semantic, referring, reasoning, grounded, and interactive guidance.

| Method | Gen. Seg. | Ref. Seg. | Rea. Seg. | GCG Seg. | Inter. Seg. |
| --- | --- | --- | --- | --- | --- |
| Pan. / Sem. | RefCOCO / + / g | Val / Test | Val / Test | Point / Box |  |
| LISA-7B | -- | 74.9 / 65.1 / 67.9 | 52.9 / 47.3 | 62.0 / 61.7 | -- |
| PSALM | **55.9** / **66.6** | 83.6 / 72.9 / 73.8 | -- | -- | 64.3 / 67.3 |
| Text4Seg | -- | 79.2 / 72.8 / 74.0 | 59.1 / 57.1 | -- | -- |
| LENS | -- | 84.2 / **79.4** / 81.2 | 62.1 / 57.2 | -- | -- |
| ConverSeg | -- | 79.4 / 74.3 / 74.9 | 61.9 / 57.0 | -- | -- |
| X-SAM | 54.7 / 66.5 | **85.1** / 78.0 / **83.8** | 56.6 / 57.8 | **69.4** / **69.0** | **65.4** / 70.0 |
| SenseNova-Vision | 48.8 / 64.0 | 81.3 / 76.0 / 80.3 | **63.2** / **60.7** | 65.7 / 66.2 | 60.9 / **73.9** |

### Multi-View Visual Geometry

Multi-view visual geometry evaluates geometric prediction from multiple input images, including multi-view point map reconstruction and camera pose estimation.

| Method | Multi-View Reconstruction | Camera Pose |  |  |
| --- | --- | --- | --- | --- |
| Acc.↓ / Comp.↓ / F1↑ | RRA@30↑ / RTA@30↑ / AUC@30↑ |  |  |  |
| 7Scenes | ETH3D | Re10K | CO3Dv2 |  |
| DUSt3R | 0.026 / 0.034 / 87.1 | 0.359 / 0.531 / 66.6 | 99.8 / 84.9 / 67.6 | 97.7 / 93.4 / 78.3 |
| DepthAnything3 | **0.020** / **0.026** / **90.5** | 0.228 / 0.212 / 76.6 | **100.0** / **96.4** / **89.6** | **99.3** / **98.0** / **91.8** |
| VGGT | 0.023 / 0.032 / 88.4 | **0.177** / **0.155** / **80.9** | **100.0** / 93.5 / 79.3 | 98.3 / 96.6 / 89.2 |
| MoRe | 0.038 / 0.039 / 77.1 | 0.348 / 0.318 / 62.7 | **100.0** / 94.0 / 79.1 | 98.4 / 96.3 / 83.0 |
| MapAnything | **0.027** / 0.029 / 87.8 | 0.400 / 0.524 / 67.0 | **100.0** / 93.5 / **80.7** | 95.5 / 91.6 / 70.9 |
| G2VLM | 0.084 / 0.056 / 59.2 | 0.784 / 0.553 / 36.7 | 99.8 / 77.5 / 51.8 | 96.3 / 92.0 / 55.2 |
| SenseNova-Vision | 0.028 / **0.026** / **87.9** | **0.301** / **0.175** / **72.2** | 99.8 / **94.2** / 77.3 | **97.4** / **95.4** / **80.1** |

### Comparison with Generalist Vision Models

We further compare SenseNova-Vision with recent generalist visual models that span multiple visual capabilities.

| Method | Detection | Sem. Seg. | Ref. Seg. | Depth |
| --- | --- | --- | --- | --- |
| mAP | mIoU | cIoU | δ1 |  |
| COCO | Cityscapes | RefCOCO / + / g | NYUv2 |  |
| Youtu-VL | 47.1 | 70.4 | 80.7 / **76.2** / 76.5 | 90.4 |
| SenseNova-Vision | **53.7** | **71.2** | **81.3** / 76.0 / **80.3** | **98.1** |

| Method | Sem. Seg. | Ref. Seg. | Rea. Seg. | Depth | Normal |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mIoU | cIoU | gIoU | δ1 | Mean Error↓ |  |  |  |  |  |  |
| Cityscapes | RefCOCOg | ReasonSeg | KITTI | NYUv2 | DIODE | ETH3D | NYUv2 | ScanNet | DIODE |  |
| Vision Banana | 69.9 | 73.8 | 79.3 | 91.5 | 94.8 | 91.7 | 93.5 | 17.8 | 15.1 | **13.8** |
| SenseNova-Vision | **71.2** | **80.3** | 63.2 | 95.9 | 98.1 | 76.4 | 97.4 | **14.4** | **12.8** | 15.3 |

### General Multimodal Capability

SenseNova-Vision largely maintains general multimodal capability while being adapted to visual perception tasks.

| Method | Understanding | Generation |  |  |  |
| --- | --- | --- | --- | --- | --- |
| MMMU | MMVP | MathVista | GenEval | WISE |  |
| Bagel | 0.55 | 69.3 | 73.1 | 0.82 | 0.52 |
| SenseNova-Vision | 0.42 | 79.0 | 67.7 | 0.85 | 0.45 |

## 🖼️ Qualitative Examples

![SenseNova-Vision qualitative results across vision tasks](https://huggingface.co/sensenova/SenseNova-Vision-7B-MoT/resolve/main/assets/fig4_sensenova_vision_results.webp)

## 📚 Training Data

SenseNova-Vision is trained on the **SenseNova-Vision-Corpus-50M**, a large-scale computer-vision instruction-response corpus. The corpus converts heterogeneous annotations into a shared schema with visual inputs, natural-language instructions, and decodable targets represented as text, image, or mixed text-image responses.

The corpus covers four task families:

| Task family | Representative tasks | Target representation |
| --- | --- | --- |
| Structured visual understanding | Detection, referring localization, pointing, keypoints, OCR, layout, GUI grounding | Text records with normalized coordinates and lightweight structure markers |
| Dense geometric prediction | Monocular depth estimation and surface-normal prediction | Deterministically encoded image targets |
| Segmentation | Referring, reasoning, interactive, generic, and grounded-conversation segmentation | Binary masks, color-coded masks, or mixed text-image responses |
| Multi-view visual geometry | Point-map reconstruction and camera-pose estimation | Image-like point maps and structured camera records |

## ⚠️ Limitations

- **Not a specialist model for every task:** Although SenseNova-Vision covers many tasks, task-specific models may still outperform it on certain specialized benchmarks.
- **Output parsing is task-dependent:** Textual outputs require task-specific parsers, and image outputs require decoding rules consistent with the training protocol.
- **Metric accuracy is not guaranteed:** Dense depth, normal, point-map, and camera-pose predictions should be validated carefully before downstream use.
- **Prompt sensitivity:** As an instruction-following model, performance can vary with prompt wording, output schema, and visual prompt style.
- **Dataset and benchmark bias:** Model behavior reflects the distribution and annotation conventions of the training corpus.

## 🛡️ Ethical Considerations

SenseNova-Vision may generate incorrect localization, segmentation, depth, normal, or camera predictions. Users should avoid deploying the model in safety-critical settings without independent verification. When used for datasets involving people, faces, documents, medical scenes, surveillance imagery, or private environments, users are responsible for complying with applicable privacy, consent, and data-governance requirements.

## ✒️ Citation

If you find SenseNova-Vision useful, please cite the technical report:

```
@misc{han2026visionunifiedmultimodalgeneration,
      title={Vision as Unified Multimodal Generation}, 
      author={Xiaoyang Han and Jianhua Li and Kewang Deng and Zukai Chen and Xuanke Shi and Sihan Wang and Boxuan Li and Linyan Wang and Siyi Xie and Xin You and Jinsheng Quan and Zhongang Cai and Haiwen Diao and Ziwei Liu and Lei Yang and Dahua Lin and Quan Wang},
      year={2026},
      eprint={2607.06560},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2607.06560}, 
}
```

## 📜 License

The model weights are released under the CC BY-NC 4.0 license and are intended for non-commercial use only.

The source code in the official GitHub repository may follow a different license. Please refer to the repository license for code usage. Third-party datasets, tools, and assets are subject to their original licenses.

## 📮 Contact

For questions, issues, or collaboration requests, please use the official project repository or contact the authors through the release page once available.

Downloads last month

646

Inference Providers [NEW](https://huggingface.co/docs/inference-providers)

Any-to-Any

This model isn't deployed by any Inference Provider. [🙋  Ask for provider support](https://huggingface.co/spaces/huggingface/InferenceSupport/discussions/new?title=sensenova/SenseNova-Vision-7B-MoT&description=React%20to%20this%20comment%20with%20an%20emoji%20to%20vote%20for%20%5Bsensenova%2FSenseNova-Vision-7B-MoT%5D(%2Fsensenova%2FSenseNova-Vision-7B-MoT)%20to%20be%20supported%20by%20Inference%20Providers.%0A%0A(optional)%20Which%20providers%20are%20you%20interested%20in%3F%20(Novita%2C%20Hyperbolic%2C%20Together%E2%80%A6)%0A)

## Model tree for sensenova/SenseNova-Vision-7B-MoT

Finetunes

2 models

## Spaces using sensenova/SenseNova-Vision-7B-MoT 2

## Collection including sensenova/SenseNova-Vision-7B-MoT

Vision as Unified Multimodal Generation • 5 items • Updated 2 days ago •  36

## Paper for sensenova/SenseNova-Vision-7B-MoT

Paper • 2607.06560 • Published Jul 7 •  47
