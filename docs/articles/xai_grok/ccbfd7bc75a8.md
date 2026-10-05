---
vendor: xai_grok
title: Imagine Image 2.0
original_title: Imagine Image 2.0
url: https://x.ai/news/grok-imagine-image-2
date: 2026-08-07
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Imagine Image 2.0

精准的图片生成与编辑，为真实创作工作而生。

Open Grok.com

Try on API

Imagine Image 2.0 现已正式全面可用，作为 [grok.com/imagine](https://grok.com/imagine?referrer=website&campaign=imagine-image-2-blog) 以及我们的 [iOS](https://apps.apple.com/app/grok-ai-chat-video/id6670324846) 和 [Android](https://play.google.com/store/apps/details?id=ai.x.grok) 应用上全新的 **Quality Mode**。

我们围绕一个简单的目标打造 Image 2.0：**生成你能用在真实工作里的图**。2.0 对指令的遵循细致入微。它像设计师一样规划字体排印与版式，让信息密集、多部件的画面保持整体协调，小字号也清晰锐利。而且在你的输入跨多次生成与编辑时被完整保留。

## [精准编辑](https://x.ai/news/grok-imagine-image-2#precise-editing)

真实工作是迭代式的。第一次生成很少就是最终素材，所以 Image 2.0 增添了只改你所指、其余不动的工具。

魔法棒只编辑你指向的区域，其他部分保持原样。分割（Segmentation）可选中画面中精确的区域进行修改。背景移除能以透明背景导出任何主体，可直接放入其他作品。多参考编辑支持单次生成最多 5 张输入图，免去手动合成。

### [智能改尺寸](https://x.ai/news/grok-imagine-image-2#smart-resize)

一张图，任意尺寸：选择一个比例，模型自动补足画面。

1:2

## [真实世界性能](https://x.ai/news/grok-imagine-image-2#real-world-performance)

Image 2.0 为摄影、设计、插画上的高保真而训练，并把编辑当作一等公民能力。它在文生图与图像编辑两项均排名全球第二。

### Image Edit Arena

### Text-to-Image Arena

Overall Elo. Source: Arena Image Edit and Text-to-Image leaderboards (as of Aug 7, 2026). xAI models are listed on Arena under SpaceXAI.

## [模板](https://x.ai/news/grok-imagine-image-2#templates)

我们还引入新模板，把常见图像工作流打包成现成的起点。每个模板覆盖一项具体任务——照片编辑、产品图、头像、图标、游戏资产等——工作流已预先配置好，你只需提供输入，即得成品。

Photo Tools

Photo Edit

Product

Product Color Change

Marketing

Editorial Product Poster

Photo Tools

Reimagine

Photo Tools

Photo Collage

Design Tools

Mascot Maker

Photo Tools

BG Removal & Change

Marketing

E-Commerce Photos

Marketing

UGC Photos

Photo Tools

Professional Headshot

Design Tools

Icon Maker

Design Tools

Character Sprite

Game Assets

Props & UI Kit

Streaming

Emoji Creator

Marketing

Merch Maker

### [为视频构建一个世界](https://x.ai/news/grok-imagine-image-2#build-a-world-for-video)

用几条提示构建一个世界：一个角色、她的场景、她携带的道具——分别生成，从一张图到另一张图保持同一种风格。

One world

### Built image by image

A character, her locations, and the props she carries — generated separately, holding one look.

Character

Location

Location

Prop

Prop

Character

Location

## [今天就在消费级产品中体验](https://x.ai/news/grok-imagine-image-2#try-it-today-on-our-consumer-products)

Open

Grok.com

Open

Grok on iOS

Open

Grok on Android

## [API 中可用](https://x.ai/news/grok-imagine-image-2#in-the-api)

Image 2.0 以 `grok-imagine-image-2.0` 在 API 中提供。

```
import xai_sdk

client = xai_sdk.Client()

response = client.image.sample(
    prompt="A concert poster for a synthwave band, bold retro typography, sharp small print",
    model="grok-imagine-image-2.0",
)

print(response.url)
```

python

完整文档请访问我们的[文档页](https://docs.x.ai/developers/model-capabilities/images/generation#quick-start)，或在 playground 中直接开始生成。

## 开始生成

Open Playground
