---
vendor: huggingface
title: 推出面向文档图像的 TextImage 增强
original_title: Introducing TextImage Augmentation for Document Images
url: https://huggingface.co/blog/doc_aug_hf_alb
date: 2024-03-29
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: cf671378ce86
translator: agent
---

返回文章列表

# 面向文档图像的多模态 TextImage 增强登场

发布于
					2024 年 8 月 6 日

在 GitHub 上更新

点赞

33

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63e3f98a9db5da2dc1efab76/7DEh2SkVDHt5VMGmdLLsP.jpeg)](https://huggingface.co/alkibijad)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63ee535a190ddd6214f30dc2/f4pNRFs9XVLToponWndWJ.jpeg)](https://huggingface.co/de-Rodrigo)
- [![](https://huggingface.co/avatars/af4083af77a109281b129215012e5429.svg)](https://huggingface.co/babaswananda)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/OqiF10RKo-bytyIkmX8HJ.png)](https://huggingface.co/privategeek24)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/638eb5f949de7ae552dd6211/mJkQJGpn9tXV37N2VLFCh.jpeg)](https://huggingface.co/derek-thomas)
- [![](https://huggingface.co/avatars/3c8e246a1ee0a8bbad66c4ffb46cfc7e.svg)](https://huggingface.co/drdn)

Dana Aubakirova

danaaubakirova

Pablo Montalvo

Molbap

Vladimir Iglovikov

Ternaus

guest

在这篇博文中，我们提供一份教程，讲解如何使用一种与 Albumentations AI 合作开发的、面向文档图像的新数据增强技术。

## 动机

视觉语言模型（VLM，Vision Language Models）有极其广泛的应用，但它们往往需要针对具体用例做微调，尤其是包含文档图像（即文字内容很多的图片）的数据集。在这些场景下，文本和图像在模型训练的所有阶段都需要相互作用，而对两个模态同时做增强正是为了保证这种交互。说白了，我们想让模型学会正确“阅读”，而在数据最常見的缺失情况下，这非常有挑战性。

因此，在面对小数据集微调模型的挑战时，对文档图像进行**有效数据增强**的需求就变得很明确。一个常见的顾虑是：缩放、模糊、改背景色这类常规图像变换会 negatively 影响文字提取的准确率。

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/640e21ef3c82bd463ee5a76d/po85g2Nu4-d2eHqJ0PMt4.png)](https://cdn-uploads.huggingface.co/production/uploads/640e21ef3c82bd463ee5a76d/po85g2Nu4-d2eHqJ0PMt4.png)

我们意识到需要一种既能扩充数据集、又保持文本完整性的数据增强技术。这样的增强可以促进新文档的生成或现有文档的修改，同时保住文本质量。

## 简介

为满足这一需求，我们推出了一条**新的数据增强流水线**，它与 [Albumentations AI](https://albumentations.ai) 合作开发。这条流水线同时处理图像及其中的文本，为文档图像提供成套的解决方案。这类数据增强是*多模态*的，因为它会同时修改图像内容和文本标注。

正如我们在之前的[博文](https://huggingface.co/blog/danaaubakirova/doc-augmentation)中讨论的，我们的目标是验证这个假设：在 VLM 预训练中对文本和图像同时做增强是有效的。详细的参数说明和使用场景示例见 [Albumentations AI 文档](https://albumentations.ai/docs/examples/example_textimage/?h=textimage)。Albumentations AI 支持动态设计这些增强，并把它们与其他类型的增强组合起来。

## 方法

对文档图像做增强时，我们先在文档中随机选行。超参数 `fraction_range` 控制被修改的 bounding box（边界框）所占的比例。

接下来，对相应的文本行应用若干种文本增强方法之一——这些方法常用于文本生成任务，包括 Random Insertion（随机插入）、Deletion（删除）、Swap（交换）和 Stopword Replacement（停用词替换）。

修改文本之后，我们把图像中插入文字的位置涂黑，再做修补（inpaint），并沿用原始 bounding box 的尺寸作为新文字字号的近似。字号可以通过参数 `font_size_fraction_range` 指定，它决定按 bounding box 高度的比例来选择字号的范围。注意，被修改的文本及其对应的 bounding box 都可以取出来用于训练。这一流程产出的数据集，文本内容语义相近，图像则被视觉上扭曲。

## TextImage 增强的主要特性

这个库主要有两种用法：

- **在图像上插入任意文本**：这个功能允许你把文字叠加到文档图像上， effectively 生成合成数据。用任意随机图像做背景、渲染全新的文本，就能构造多样的训练样本。类似的技术 SynthDOG 出自 [OCR-free document understanding transformer](https://arxiv.org/pdf/2111.15664) 一文。
- **在图像上插入增强后的文本**：包括以下几种文本增强：  **Random deletion（随机删除）**：从文本中随机删词。**Random swapping（随机交换）**：交换文本中的词。**Stop words insertion（停用词插入）**：把常见停用词插入文本。

把这些增强与 Albumentations 的其他图像变换组合起来，就能同时修改图像和文本。你同样可以取到增强后的文本。

*注*：在 [这个 repo](https://github.com/danaaubakirova/doc-augmentation) 里展示的数据增强流水线初版包含同义词替换。这一版把它去掉了，因为它带来很大的时间开销。

## 安装

```
!pip install -U pillow
!pip install albumentations
!pip install nltk
```

```
import albumentations as A
import cv2
from matplotlib import pyplot as plt
import json
import nltk

nltk.download('stopwords')
from nltk.corpus import stopwords
```

## 可视化

```
def visualize(image):
    plt.figure(figsize=(20, 15))
    plt.axis('off')
    plt.imshow(image)
```

## 加载数据

注意，这类增强可以使用 [IDL](https://huggingface.co/datasets/pixparse/idl-wds) 和 [PDFA](https://huggingface.co/datasets/pixparse/pdfa-eng-wds) 数据集，它们提供了你想修改的文本行的 bounding box。本教程以 IDL 数据集的一条样本为例。

```
bgr_image = cv2.imread("examples/original/fkhy0236.tif")
image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

with open("examples/original/fkhy0236.json") as f:
    labels = json.load(f)

font_path = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"

visualize(image)
```

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/640e21ef3c82bd463ee5a76d/g3lYRSdMBazALttw7wDJ2.png)](https://cdn-uploads.huggingface.co/production/uploads/640e21ef3c82bd463ee5a76d/g3lYRSdMBazALttw7wDJ2.png)

我们需要正确地预处理数据，因为 bounding box 的输入格式是归一化的 Pascal VOC。因此元数据按如下方式构造：

```
page = labels['pages'][0]

def prepare_metadata(page: dict, image_height: int, image_width: int) -> list:
    metadata = []

    for text, box in zip(page['text'], page['bbox']):
        left, top, width_norm, height_norm = box

        metadata.append({
            "bbox": [left, top, left + width_norm, top + height_norm],
            "text": text
        })
    
    return metadata

image_height, image_width = image.shape[:2]
metadata = prepare_metadata(page, image_height, image_width)
```

## 随机交换

```
transform = A.Compose([A.TextImage(font_path=font_path, p=1, augmentations=["swap"], clear_bg=True, font_color = 'red', fraction_range = (0.5,0.8), font_size_fraction_range=(0.8, 0.9))])
transformed = transform(image=image, textimage_metadata=metadata)
visualize(transformed["image"])
```

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/640e21ef3c82bd463ee5a76d/k06LJuPRSRHGeGnpCj3XP.png)](https://cdn-uploads.huggingface.co/production/uploads/640e21ef3c82bd463ee5a76d/k06LJuPRSRHGeGnpCj3XP.png)

## 随机删除

```
transform = A.Compose([A.TextImage(font_path=font_path, p=1, augmentations=["deletion"], clear_bg=True, font_color = 'red', fraction_range = (0.5,0.8), font_size_fraction_range=(0.8, 0.9))])
transformed = transform(image=image, textimage_metadata=metadata)
visualize(transformed['image'])
```

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/640e21ef3c82bd463ee5a76d/3Z_L4GTZMT5tvBYJSMOha.png)](https://cdn-uploads.huggingface.co/production/uploads/640e21ef3c82bd463ee5a76d/3Z_L4GTZMT5tvBYJSMOha.png)

## 随机插入

随机插入会把随机的词或短语插入文本。这里我们使用停用词（stop words）——语言中常见、在自然语言处理（NLP）任务中常被忽略或过滤掉的词，因为它们携带的信息比其他词少。停用词的例子包括 "is"、"the"、"in"、"and"、"of" 等。

```
stops = stopwords.words('english')
transform = A.Compose([A.TextImage(font_path=font_path, p=1, augmentations=["insertion"], stopwords = stops, clear_bg=True, font_color = 'red', fraction_range = (0.5,0.8), font_size_fraction_range=(0.8, 0.9))])
transformed = transform(image=image, textimage_metadata=metadata)
visualize(transformed['image'])
```

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/640e21ef3c82bd463ee5a76d/QZKZP_VEzFhEV5GhykRlP.png)](https://cdn-uploads.huggingface.co/production/uploads/640e21ef3c82bd463ee5a76d/QZKZP_VEzFhEV5GhykRlP.png)

## 能和其他变换组合吗？

我们用 `A.Compose` 定义一条复杂的变换流水线，包括带指定字体属性和停用词的文本插入、Planckian jitter（普朗克抖动）和仿射变换。首先，用 `A.TextImage` 以指定字体属性向图像插入文本，背景透明、字体为红色，并指定插入文本的比例和大小。然后用 `A.PlanckianJitter` 改变图像的色彩平衡。最后用 `A.Affine` 做仿射变换，可以包括缩放、旋转和平移图像。

```
transform_complex = A.Compose([A.TextImage(font_path=font_path, p=1, augmentations=["insertion"], stopwords = stops, clear_bg=True, font_color = 'red', fraction_range = (0.5,0.8), font_size_fraction_range=(0.8, 0.9)),
                               A.PlanckianJitter(p=1),
                               A.Affine(p=1)
                              ])
transformed = transform_complex(image=image, textimage_metadata=metadata)
visualize(transformed["image"])
```

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/640e21ef3c82bd463ee5a76d/-mDto1DdKHJXmzG2j9RzR.png)](https://cdn-uploads.huggingface.co/production/uploads/640e21ef3c82bd463ee5a76d/-mDto1DdKHJXmzG2j9RzR.png)

# 如何获取被改动的文本？

要提取文本被改动的 bounding box 索引以及对应的变换后文本数据，运行下面这个 cell。这些数据可以很好地用于训练模型识别和处理图像中的文字变化。

```
transformed['overlay_data']
```

```
[{'bbox_coords': (375, 1149, 2174, 1196),
  'text': "Lionberger, Ph.D., (Title: if Introduction to won i FDA's yourselves Draft Guidance once of the wasn't General Principles",
  'original_text': "Lionberger, Ph.D., (Title: Introduction to FDA's Draft Guidance of the General Principles",
  'bbox_index': 12,
  'font_color': 'red'},
 {'bbox_coords': (373, 1677, 2174, 1724),
  'text': "After off needn't were a brief break, ADC member mustn Jeffrey that Dayno, MD, Chief Medical Officer for at their Egalet",
  'original_text': 'After a brief break, ADC member Jeffrey Dayno, MD, Chief Medical Officer at Egalet',
  'bbox_index': 19,
  'font_color': 'red'},
 {'bbox_coords': (525, 2109, 2172, 2156),
  'text': 'll Brands recognize the has importance and of a generics ADF guidance to ensure which after',
  'original_text': 'Brands recognize the importance of a generics ADF guidance to ensure',
  'bbox_index': 23,
  'font_color': 'red'}]
  
```

## 合成数据生成

这种增强方法可以扩展到合成数据生成，因为它能在任意背景或模板上渲染文本。

```
template = cv2.imread('template.png')
image_template = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
transform = A.Compose([A.TextImage(font_path=font_path, p=1, clear_bg=True, font_color = 'red', font_size_fraction_range=(0.5, 0.7))])

metadata = [{
    "bbox": [0.1, 0.4, 0.5, 0.48],
    "text": "Some smart text goes here.",
}, {
    "bbox": [0.1, 0.5, 0.5, 0.58],
    "text": "Hope you find it helpful.",
}]

transformed = transform(image=image_template, textimage_metadata=metadata)
visualize(transformed['image'])
```

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/640e21ef3c82bd463ee5a76d/guKKPs5P0-g8nX4XSGcLe.png)](https://cdn-uploads.huggingface.co/production/uploads/640e21ef3c82bd463ee5a76d/guKKPs5P0-g8nX4XSGcLe.png)

## 结语

我们与 Albumentations AI 合作推出了 TextImage Augmentation——一种同时修改文档图像和其中文本的多模态技术。把 Random Insertion、Deletion、Swap、Stopword Replacement 等文本增强与图像修改结合起来，这条流水线可以生成多样的训练样本。

详细参数和使用场景示例请参阅 [Albumentations AI 文档](https://albumentations.ai/docs/examples/example_textimage/?h=textimage)。希望这些增强能帮助你提升文档图像处理的 Workflow。

## 参考文献

```
@inproceedings{kim2022ocr,
  title={Ocr-free document understanding transformer},
  author={Kim, Geewook and Hong, Teakgyu and Yim, Moonbin and Nam, JeongYeon and Park, Jinyoung and Yim, Jinyeong and Hwang, Wonseok and Yun, Sangdoo and Han, Dongyoon and Park, Seunghyun},
  booktitle={European Conference on Computer Vision},
  pages={498--517},
  year={2022},
  organization={Springer}
}
```

## 本文提到的 Datasets 2

我们博客的更多文章

community

evaluation

synthetic-data

## LAVE：用 LLM 在 Docmatix 上做零样本 VQA 评估——还需要微调吗？

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/640e21ef3c82bd463ee5a76d/nVR1DFPAsiLw6Boys28Rb.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/65d66b494bbd0d92b641cdbb/6-7dm7B-JxcoS1QlCPdMN.jpeg)

17

2024 年 7 月 25 日

community

datasets

synthetic-data

## Docmatix——一个用于文档视觉问答的大型数据集

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/65d66b494bbd0d92b641cdbb/6-7dm7B-JxcoS1QlCPdMN.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1635201569275-noauth.jpeg)

80

2024 年 7 月 18 日

### 社区

将图片、音频和视频拖到输入框、粘贴，或

点击这里

上传。

点击或粘贴到这里上传图片

· [注册](https://huggingface.co/join?next=%2Fblog%2Fdoc_aug_hf_alb)或[登录](https://huggingface.co/login?next=%2Fblog%2Fdoc_aug_hf_alb)即可评论

点赞

33

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63e3f98a9db5da2dc1efab76/7DEh2SkVDHt5VMGmdLLsP.jpeg)](https://huggingface.co/alkibijad)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63ee535a190ddd6214f30dc2/f4pNRFs9XVLToponWndWJ.jpeg)](https://huggingface.co/de-Rodrigo)
- [![](https://huggingface.co/avatars/af4083af77a109281b129215012e5429.svg)](https://huggingface.co/babaswananda)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/OqiF10RKo-bytyIkmX8HJ.png)](https://huggingface.co/privategeek24)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/638eb5f949de7ae552dd6211/mJkQJGpn9tXV37N2VLFCh.jpeg)](https://huggingface.co/derek-thomas)
- [![](https://huggingface.co/avatars/3c8e246a1ee0a8bbad66c4ffb46cfc7e.svg)](https://huggingface.co/drdn)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/Y5Lr9MsfuTrUNOig29z62.jpeg)](https://huggingface.co/BeefOven)
- [![](https://huggingface.co/avatars/fe3107c60414d2241fa21a451c78f71f.svg)](https://huggingface.co/nightwatch)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/BNZWfvArvA_5BEi8Ta_c2.png)](https://huggingface.co/psyche414)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1670594087059-630412d57373aacccd88af95.jpeg)](https://huggingface.co/alfredplpl)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/660c2d134ba2fcc848b03e21/oIxOALwKoNaNw3nh0bmrS.png)](https://huggingface.co/qubvel-hf)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64789feb79f2d49511ed7db4/IzaIwiVgnkTZHrcLDQk0C.jpeg)](https://huggingface.co/Molbap)

## 本文提到的 Datasets 2
