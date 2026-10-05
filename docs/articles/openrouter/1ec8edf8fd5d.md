---
vendor: openrouter
title: 图像基准测试：看清每个模型的能力
original_title: Image Benchmarks: See the Capabilities of Every Model
url: https://openrouter.ai/blog/announcements/image-benchmarks
date: 2026-08-21
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

选择文本模型时我们有海量 LLM 基准可用，而选择图像模型却往往全凭感觉。展示的样张多是精心挑选的“眼缘货”，而 LLM-as-a-judge 评测目前也抓不住人类一眼就能注意到的细节。Arena 分数虽有参考价值，但它评的是人们更喜欢哪些输出，而不是模型实际能做什么。

今天我们推出 [Visual Image Benchmarks](https://openrouter.ai/benchmarks/media/images)，帮助你快速评估我们提供的所有图像模型的能力（截至 2026 年 8 月共 39 个）。我们挑选了一组有挑战性、能够区分模型能力的 prompt，并以网格形式展示所有结果，可按价格和生成时间排序。

## 为测试图像模型能力边界而设计的 prompt

每项挑战都旨在区分图像模型的能力。我们初步把它们分为七类：

- **不太可能的场景。** 倒满至杯口的酒杯、收拢状态的雨伞。训练数据里满是这两者的常见版本。
- **计数。** 三根手指、特定数量的纸牌和骰子。
- **文字。** 海报上一长串精确文本，以及同一画面中的多种语言。
- **空间关系。** 遮挡与镜面反射。
- **否定。** 没有条纹的斑马、没有广告牌的 Times Square。
- **编辑。** 最小改动、物体移除、人物移除，全部基于参考图。
- **一致性。** 在新场景中保持某个产品或四个参考主体稳定不变。

这些 prompt 的写法让你一眼就能目测评估。例如：模型能否遵循“把酒杯完全倒满”的指令？

![Full Wine Glass challenge sorted by cost, with the prompt above the grid and each wine glass output labeled with model name, price, and generation time](https://openrouter.ai/blog/images/image-benchmarks/wine-glass-grid.png)

## 更多视觉评测与新的模态即将推出

评估视频和音频模型的质量与能力同样困难。我们打算把这一工具扩展到更多模态，并随新增的图像模型持续更新。

现在就来看看我们的[图像基准](https://openrouter.ai/benchmarks/media/images)！如果你有能难住下一批模型的 prompt，欢迎在 Discord 的 [#feedback](https://discord.gg/fVyRaUDgxW) 频道分享给我们。

## 通过 OpenRouter API 和 Chat 生成图像

通过这些基准评估完模型后，用你自己的 prompt 在[图像生成 API](https://openrouter.ai/docs/guides/overview/multimodal/image-generation)或 [Chat](https://openrouter.ai/chat) 中试试，看看它们在你的内容上表现如何。
