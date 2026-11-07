---
vendor: huggingface
title: 埃及语和尼日利亚英语加入 Open ASR 排行榜
original_title: 
url: https://huggingface.co/blog/open-asr-leaderboard-liva
date: 2026-11-06
lang: zh
captured: 2026-11-07
extractor: readability-v1
translator: mt
status: translated
body_sha: 28baccfaa362
---

[返回文章](https://huggingface.co/blog)

# 埃及和尼日利亚英语加入 Open ASR 排行榜

发表于 2026 年 11 月 6 日

GitHub 上更新

5

- [![](https://cdn-avatars.huggingface.co/v1/product/uploads/6384db7fb2906edaf835a91d/MOTXxaOmjlTZ8wONYifnD.jpeg)](https://huggingface.co/bezzam)
- [![](https://cdn-avatars.huggingface.co/v1/product/uploads/no-auth/g0ECTo_lbbi8O4Wt_e37M.png)](https://huggingface.co/ausyeternal)
- [![](https://cdn-avatars.huggingface.co/v1/product/uploads/no-auth/OcluLHMjRNEC15-7X46GD.png)](https://huggingface.co/decypher01)
- [![](https://cdn-avatars.huggingface.co/v1/product/uploads/6824dfdc3df9a0dff0a59b6f/WizAqpnpoeY2_C1NUPQDT.jpeg)](https://huggingface.co/luckygall)
- [![](https://huggingface.co/avatars/d380b48d9b44431a5376b465daf057fb.svg)](https://huggingface.co/ashleymo2025)

[![Eric Bezzam 的头像](https://cdn-avatars.huggingface.co/v1/product/uploads/6384db7fb2906edaf835a91d/MOTXxaOmjlTZ8wONYifnD.jpeg)](https://huggingface.co/bezzam)

埃里克·贝扎姆

贝扎姆

[![Ashley Mo 的头像](https://huggingface.co/avatars/d380b48d9b44431a5376b465daf057fb.svg)](https://huggingface.co/ashleymo2025)

莫施礼

阿什利莫2025

[![Liva AI 头像](https://cdn-avatars.huggingface.co/v1/product/uploads/64d5eff05900b6d111c9e1ad/upXC_tilVUY3zVD_7UqJu.png)](https://huggingface.co/liva-ai) [liva-ai](https://huggingface.co/liva-ai)

[![大谷葵的头像](https://cdn-avatars.huggingface.co/v1/product/uploads/64d5eff05900b6d111c9e1ad/hGnt9yx6LyQP5a2MBpXGg.jpeg)](https://huggingface.co/aonorii)

大谷葵

青苔

[![Liva AI 头像](https://cdn-avatars.huggingface.co/v1/product/uploads/64d5eff05900b6d111c9e1ad/upXC_tilVUY3zVD_7UqJu.png)](https://huggingface.co/liva-ai) [liva-ai](https://huggingface.co/liva-ai)

几个月前，我们将私有数据添加到 [开放 ASR 排行榜](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard)：来自 Appen 和 DataOceanAI 的 11 个分割，涵盖五种口音的脚本和会话语音 ([博客](https://huggingface.co/blog/open-asr-leaderboard-private-data))。社区反响热烈，许多人**强调了保留集对于可信评估的重要性**。从那时起，我们又通过 Voice Arena 添加了一项针对印度口音英语的私人拆分（[博客](https://huggingface.co/blog/open-asr-leaderboard-global-south)）。

我们很高兴宣布与 [Liva AI](https://huggingface.co/liva-ai) 开展新合作，以两种新口音添加更多​​私人数据：**埃及语** 🇪🇬 和 **尼日利亚语** 🇳🇬。

|数据集 |口音|持续时间 [h] |风格|转录|
| --- | --- | --- | --- | --- |
| Liva AI 对话 EG |埃及 | 1.34 | 1.34对话式、自发式 |断断续续、格格不入、不连贯。 |
| Liva AI 对话式NG |尼日利亚 | 1.55 | 1.55对话式、自发式 |断断续续、格格不入、不连贯。 |

这是我们持续努力的一部分，旨在提高 ASR 评估的代表性（更多口音和更多语言）并提高信任度（新的私有数据以最大限度地减少基准优化，以及新的数据提供者）。我们很高兴看到社区继续为世界推动 ASR 性能 🤗

## 私人选项卡中更丰富的口音细分

有了这些新的口音，我们现在可以基于 [Kachru 的三个圆圈](https://en.wikipedia.org/wiki/World_Englishes#Kachru%27s_Three_Circles_of_English) 呈现更丰富的口音细分（在 [排行榜](https://huggingface.co/spaces/HumeAI/asr-leaderboard) 中向 Hume AI 致敬）。 Open ASR 排行榜现在将报告：

- 美国与非美国（*英国、澳大利亚、加拿大、印度、尼日利亚、埃及*）
- 内圈（*美国、英国、澳大利亚、加拿大*）与外圈和扩展圈（*印度、尼日利亚、埃及*）

随着更多口音的加入，我们将拆分外圈和扩展圈。

![缩略图](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/open_asr_leaderboard/private_data_accent_breakdown.png)

## 关于 Liva AI

Liva AI 通过真人使用的消费产品收集多模态交互数据。由于 Liva 拥有收集环境和分发，因此它可以围绕跨领域、行业、语言、模式和交互类型的特定模型差距来设计产品。这使它能够访问通过实际产品使用而出现的自然的、高情境的行为，而不是人为引发的或基于任务的交互。

## 本文提到的空格2

我们博客的更多文章

音频语音排行榜

## 开放 TTS 排行榜：多语言文本转语音和语音克隆的可扩展评估

- ![](https://cdn-avatars.huggingface.co/v1/product/uploads/6384db7fb2906edaf835a91d/MOTXxaOmjlTZ8wONYifnD.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/product/uploads/654bcb6fae75d15300d48205/T4L1RZUgCZgdik4ZhEWCq.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/product/uploads/660bc459d81d6112496f30f8/jMrpAckFyg-_iHMI7sn2h.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/product/uploads/62e54f0eae9d3f10acb95cb9/VAyk05hqB3OZWXEZW-B0q.png)

80

2026 年 9 月 30 日

音频语音排行榜

## 开放 ASR 排行榜添加了第一个全球南方语言

- ![](https://cdn-avatars.huggingface.co/v1/product/uploads/6384db7fb2906edaf835a91d/MOTXxaOmjlTZ8wONYifnD.jpeg)
- ![](https://huggingface.co/avatars/56ce7e0fea0166a14997e7876fb23621.svg)
- ![](https://cdn-avatars.huggingface.co/v1/product/uploads/67bc3e2f4b9d3615a6e2c982/8x33LQ0fwbnUtIn9CAwv2.png)
- ![](https://cdn-avatars.huggingface.co/v1/product/uploads/6673251287330d7378e6b5e3/VVvuAsOUMiAPNgsdoRZjM.png)
- +6

61

2026 年 8 月 28 日

### 社区

![](https://huggingface.co/avatars/ab7fc92bae0354165d3f9890ac7f5b0b.svg)

乌库特221

大约 7 小时前

干草

通过拖入文本输入、粘贴或单击此处来上传图像、音频和视频。

点击或粘贴此处上传图像

· [注册](https://huggingface.co/join?next=%2Fblog%2Fopen-asr-leaderboard-liva) 或 [登录](https://huggingface.co/login?next=%2Fblog%2Fopen-asr-leaderboard-liva) 发表评论

5

- [![](https://cdn-avatars.huggingface.co/v1/product/uploads/6384db7fb2906edaf835a91d/MOTXxaOmjlTZ8wONYifnD.jpeg)](https://huggingface.co/bezzam)
- [![](https://cdn-avatars.huggingface.co/v1/product/uploads/no-auth/g0ECTo_lbbi8O4Wt_e37M.png)](https://huggingface.co/ausyeternal)
- [![](https://cdn-avatars.huggingface.co/v1/product/uploads/no-auth/OcluLHMjRNEC15-7X46GD.png)](https://huggingface.co/decypher01)
- [![](https://cdn-avatars.huggingface.co/v1/product/uploads/6824dfdc3df9a0dff0a59b6f/WizAqpnpoeY2_C1NUPQDT.jpeg)](https://huggingface.co/luckygall)
- [![](https://huggingface.co/avatars/d380b48d9b44431a5376b465daf057fb.svg)](https://huggingface.co/ashleymo2025)

## 本文提到的空格2
