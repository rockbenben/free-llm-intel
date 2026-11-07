---
vendor: huggingface
title: 埃及英语与尼日利亚英语加入 Open ASR 排行榜
original_title: Egyptian and Nigerian English join the Open ASR Leaderboard
url: https://huggingface.co/blog/open-asr-leaderboard-liva
date: 2026-11-06
lang: zh
captured: 2026-11-07
extractor: readability-v1
translator: agent
status: translated
body_sha: cd65bd41c833
---

[ Back to Articles](https://huggingface.co/blog)

# 埃及英语与尼日利亚英语加入 Open ASR 排行榜

Published November 6, 2026

Update on GitHub


5

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6384db7fb2906edaf835a91d/MOTXxaOmjlTZ8wONYifnD.jpeg)](https://huggingface.co/bezzam)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/g0ECTo_lbbi8O4Wt_e37M.png)](https://huggingface.co/ausyeternal)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/OcluLHMjRNEC15-7X46GD.png)](https://huggingface.co/decypher01)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6824dfdc3df9a0dff0a59b6f/WizAqpnpoeY2_C1NUPQDT.jpeg)](https://huggingface.co/luckygall)
- [![](https://huggingface.co/avatars/d380b48d9b44431a5376b465daf057fb.svg)](https://huggingface.co/ashleymo2025)

[![Eric Bezzam's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/6384db7fb2906edaf835a91d/MOTXxaOmjlTZ8wONYifnD.jpeg)](https://huggingface.co/bezzam)

Eric Bezzam

bezzam

[![Ashley Mo's avatar](https://huggingface.co/avatars/d380b48d9b44431a5376b465daf057fb.svg)](https://huggingface.co/ashleymo2025)

Ashley Mo

ashleymo2025

[![Liva AI's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/64d5eff05900b6d111c9e1ad/upXC_tilVUY3zVD_7UqJu.png)](https://huggingface.co/liva-ai) [liva-ai](https://huggingface.co/liva-ai)

[![Aoi Otani's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/64d5eff05900b6d111c9e1ad/hGnt9yx6LyQP5a2MBpXGg.jpeg)](https://huggingface.co/aonorii)

Aoi Otani

aonorii

[![Liva AI's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/64d5eff05900b6d111c9e1ad/upXC_tilVUY3zVD_7UqJu.png)](https://huggingface.co/liva-ai) [liva-ai](https://huggingface.co/liva-ai)

几个月前，我们为 [Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard) 引入了私有测试集：来自 Appen 和 DataOceanAI 的 11 个子集，涵盖 5 种口音的朗读与自然会话语音（[博客](https://huggingface.co/blog/open-asr-leaderboard-private-data)）。社区反响非常热烈，许多人**特别强调了保留测试集对于构建可信评测的重要性**。此后，我们又通过 Voice Arena 补充了一个针对印度口音英语的私有子集（[博客](https://huggingface.co/blog/open-asr-leaderboard-global-south)）。

我们非常高兴宣布与 [Liva AI](https://huggingface.co/liva-ai) 达成全新合作，进一步扩充私有数据，并引入两种全新口音：**埃及英语** 🇪🇬 与 **尼日利亚英语** 🇳🇬。

| Dataset | Accent | Duration [h] | Style | Transcription |
| --- | --- | --- | --- | --- |
| Liva AI Conversational EG | Egyptian | 1.34 | Conversational, spontaneous | Punctuated, cased, with disfluencies. |
| Liva AI Conversational NG | Nigerian | 1.55 | Conversational, spontaneous | Punctuated, cased, with disfluencies. |

这是我们持续提升 ASR 评测代表性（覆盖更多口音与语种）与可信度（引入全新私有数据以遏制刷榜行为，并拓展更多数据供应商）工作的一部分。我们非常期待看到开源社区继续推动 ASR 技术造福全球用户 🤗

## Richer accent breakdown in the Private tab

随着这些全新口音的加入，我们现在可以基于 [Kachru 的英语三同心圆理论](https://en.wikipedia.org/wiki/World_Englishes#Kachru%27s_Three_Circles_of_English) 呈现更加丰富的口音细分（感谢 Hume AI 在其[排行榜](https://huggingface.co/spaces/HumeAI/asr-leaderboard)中提出的这一巧思）。Open ASR Leaderboard 现在将分别汇报：

- 美国英语 vs. 非美口音（*英国、澳大利亚、加拿大、印度、尼日利亚、埃及*）
- 内圈（*美国、英国、澳大利亚、加拿大*）vs. 外圈与扩展圈（*印度、尼日利亚、埃及*）

未来随着更多口音的加入，我们还会进一步拆分外圈与扩展圈。

![thumbnail](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/open_asr_leaderboard/private_data_accent_breakdown.png)

## About Liva AI

Liva AI 通过真实用户使用的消费级产品采集多模态交互数据。由于 Liva 同时拥有数据采集环境与分发渠道，它可以围绕模型在特定领域、行业、语言、模态及交互类型上的能力短板进行针对性产品设计。这使其能够捕获在真实产品使用中自然涌现的高语境、高质量交互行为，而非人工诱导或基于特定任务的机械互动。

## Spaces mentioned in this article 2

More Articles from our Blog

audiospeechleaderboard

## Open TTS Leaderboard: Scalable Evaluation for Multilingual Text-to-Speech and Voice Cloning

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6384db7fb2906edaf835a91d/MOTXxaOmjlTZ8wONYifnD.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/654bcb6fae75d15300d48205/T4L1RZUgCZgdik4ZhEWCq.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/660bc459d81d6112496f30f8/jMrpAckFyg-_iHMI7sn2h.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/62e54f0eae9d3f10acb95cb9/VAyk05hqB3OZWXEZW-B0q.png)

80

September 30, 2026

audiospeechleaderboard

## The Open ASR Leaderboard Adds Its First Global South Language

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6384db7fb2906edaf835a91d/MOTXxaOmjlTZ8wONYifnD.jpeg)
- ![](https://huggingface.co/avatars/56ce7e0fea0166a14997e7876fb23621.svg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/67bc3e2f4b9d3615a6e2c982/8x33LQ0fwbnUtIn9CAwv2.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6673251287330d7378e6b5e3/VVvuAsOUMiAPNgsdoRZjM.png)
- +6

61

August 28, 2026

### Community

![](https://huggingface.co/avatars/ab7fc92bae0354165d3f9890ac7f5b0b.svg)

wookute221

about 7 hours ago

hay

Upload images, audio, and videos by dragging in the text input, pasting, or clicking here.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fopen-asr-leaderboard-liva) or [log in](https://huggingface.co/login?next=%2Fblog%2Fopen-asr-leaderboard-liva) to comment


5

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6384db7fb2906edaf835a91d/MOTXxaOmjlTZ8wONYifnD.jpeg)](https://huggingface.co/bezzam)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/g0ECTo_lbbi8O4Wt_e37M.png)](https://huggingface.co/ausyeternal)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/OcluLHMjRNEC15-7X46GD.png)](https://huggingface.co/decypher01)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6824dfdc3df9a0dff0a59b6f/WizAqpnpoeY2_C1NUPQDT.jpeg)](https://huggingface.co/luckygall)
- [![](https://huggingface.co/avatars/d380b48d9b44431a5376b465daf057fb.svg)](https://huggingface.co/ashleymo2025)

## Spaces mentioned in this article 2
