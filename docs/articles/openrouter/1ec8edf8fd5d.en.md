---
vendor: openrouter
title: Image Benchmarks: See the Capabilities of Every Model
original_title: Image Benchmarks: See the Capabilities of Every Model
url: https://openrouter.ai/blog/announcements/image-benchmarks
date: 2026-08-21
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 462e70cf8af1
---

# Image Benchmarks: See the Capabilities of Every Model

Brian Thomas ·8/21/2026 · Updated 9/3/2026

Unlike choosing a text model, where we have a vast array of LLM benchmarks, picking an image model can feel arbitrary. Output samples tend to be curated eye candy and LLM-as-a-judge evals can’t yet capture the details a human would notice instantly. While arena scores help, they evaluate which outputs people prefer rather than what a model can actually do.

Today we’re launching [Visual Image Benchmarks](https://openrouter.ai/benchmarks/media/images) to help you quickly evaluate the capabilities of all the image models we offer (39 as of August ‘26). We’ve selected a set of challenging prompts designed to differentiate the capabilities of models, and show every result in a grid with sorting for both price and generation time.

## Prompts designed to test the boundaries of image model capabilities

Each challenge is designed to differentiate the capabilities of image models. We’ve initially grouped them into seven families:

- **Improbable scenes.** A wine glass filled level with the rim, umbrellas that are closed. Training data is full of the ordinary version of both.
- **Counting.** Three fingers, specific numbers of cards and dice.
- **Text.** One long exact string on a poster, and several languages in the same frame.
- **Spatial relations.** Occlusion and mirror reflections.
- **Negation.** A zebra with no stripes, a Times Square with no advertising.
- **Editing.** Minimal diffs, object removal, person removal, all from a reference image.
- **Consistency.** Holding a product or four reference subjects steady across a new scene.

The prompts are written so you can instantly evaluate them visually. For example, can a model follow the instruction to fully fill a wine glass?

![Full Wine Glass challenge sorted by cost, with the prompt above the grid and each wine glass output labeled with model name, price, and generation time](https://openrouter.ai/blog/images/image-benchmarks/wine-glass-grid.png)

## More visual evals and additional modalities coming soon

It’s similarly challenging to evaluate video and audio models to understand their quality and capabilities. We intend to expand this tool out across modalities as well as keep it up to date with all the new image models we add.

Check out our [image benchmarks](https://openrouter.ai/benchmarks/media/images) today! If you have any prompts that could challenge the next round of models, share it with us in [#feedback](https://discord.gg/fVyRaUDgxW) on our Discord.

## Generating images via the OpenRouter API and Chat

Once you’ve evaluated models via these benchmarks, try them on your own prompts through the [image generation API](https://openrouter.ai/docs/guides/overview/multimodal/image-generation) or [Chat](https://openrouter.ai/chat) to see how they perform on your own content.
