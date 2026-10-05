---
vendor: xai_grok
title: Imagine Image 2.0
original_title: 
url: https://x.ai/news/grok-imagine-image-2
date: 2026-08-07
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 57c1e2772b3c
---

Back to news

Aug 7, 2026

# Imagine Image 2.0

Precise image generation and editing, built for real creative work.

Open Grok.com

Try on API

Imagine Image 2.0 is now generally available as the new **Quality Mode** on [grok.com/imagine](https://grok.com/imagine?referrer=website&campaign=imagine-image-2-blog), and our [iOS](https://apps.apple.com/app/grok-ai-chat-video/id6670324846) and [Android](https://play.google.com/store/apps/details?id=ai.x.grok) apps.

We built Image 2.0 around a simple goal: **make images you can use in real work**. 2.0 follows instructions closely, down to the details. It plans typography and layout the way a designer would, so dense, multi-part visuals hold together and small text comes out sharp. And it preserves what you put in across generations and edits.

## [Precise editing](https://x.ai/news/grok-imagine-image-2#precise-editing)

Real work is iterative. The first generation is rarely the final asset, so Image 2.0 adds tools for changing exactly what you mean and nothing else.

The magic wand edits the region you point at and leaves the rest untouched. Segmentation selects precise areas of the image to change. Background removal exports any subject with a transparent background, ready to drop into other work. Multi-ref editing accepts up to 5 input images in a single generation, removing the need for manual compositing.

### [Smart resize](https://x.ai/news/grok-imagine-image-2#smart-resize)

One image, any size: pick a ratio and the model fills in the frame.

1:2

## [Real-world performance](https://x.ai/news/grok-imagine-image-2#real-world-performance)

Image 2.0 was trained for fidelity across photography, design, and illustration, with editing treated as a first-class capability. It ranks second in the world in both text-to-image generation and image editing.

### Image Edit Arena

### Text-to-Image Arena

Overall Elo. Source: Arena Image Edit and Text-to-Image leaderboards (as of Aug 7, 2026). xAI models are listed on Arena under SpaceXAI.

## [Templates](https://x.ai/news/grok-imagine-image-2#templates)

We’re also introducing new templates, which package common image workflows into ready-made starting points. Each one covers a specific task — photo editing, product shots, headshots, icons, game assets, and more — with the workflow already configured, so you supply the inputs and get a finished result.

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

### [Build a world for video](https://x.ai/news/grok-imagine-image-2#build-a-world-for-video)

One world from a handful of prompts: a character, her locations, and the props she carries — generated separately, holding one style from image to image.

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

## [Try it today on our consumer products](https://x.ai/news/grok-imagine-image-2#try-it-today-on-our-consumer-products)

Open

Grok.com

Open

Grok on iOS

Open

Grok on Android

## [In the API](https://x.ai/news/grok-imagine-image-2#in-the-api)

Image 2.0 is available in the API as `grok-imagine-image-2.0`.

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

For full documentation, visit our [docs page](https://docs.x.ai/developers/model-capabilities/images/generation#quick-start), or start generating in the playground.

## Start generating

Open Playground
