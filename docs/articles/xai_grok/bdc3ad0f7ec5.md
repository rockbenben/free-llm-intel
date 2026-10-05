---
vendor: xai_grok
title: 自定义声音（Custom Voices）
original_title: Custom Voices
url: https://x.ai/news/grok-custom-voices
date: 2026-04-30
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# 自定义声音（Custom Voices）

你的声音，你的品牌。用一小段录音克隆声音，并在 Grok Text to Speech 与 Voice Agent API 中随处使用。

Clone your voice

Read Docs

Clone your voice

Read Docs

今天，我们介绍 **Custom Voices（自定义声音）**。用几秒钟音频克隆你的声音，即刻在 [Grok Text to Speech](https://docs.x.ai/developers/model-capabilities/audio/text-to-speech?campaign=custom-voices-blog) 和 [Voice Agent API](https://docs.x.ai/developers/model-capabilities/audio/speech-to-speech?campaign=custom-voices-blog) 中随处使用。

Tyler

SpaceX Broadcast Host

ORIGINAL

CLONED

## [用例](https://x.ai/news/grok-custom-voices#use-cases)

Custom Voices 打开了一整类新应用。

Live Support

I need help with my recent order.

Of course! Let me pull up your order details.

### 品牌声音智能体

给你的客服智能体一个与你品牌识别一致的、可辨识的声音，而不是通用预设。

Rec

00:

42

In today's episode we dive deep into the future of AI and what it means for creators everywhere

### 内容创作者

用你自己的声音规模化地为视频、播客和社交帖配音，不必每次重新录制。

Original

Preserved

### 无障碍

为失去说话能力的人创造个性化声音，保留他们的声音身份。

🇺🇸

🇪🇸

🇫🇷

🇩🇪

🇨🇳

🇯🇵

🇺🇸

English

🇪🇸

Spanish

🇫🇷

French

🇩🇪

German

🇨🇳

Chinese

🇯🇵

Japanese

### 多语言团队

让你的 CEO 主题演讲以每一种主要语言自然呈现——英语、西班牙语、法语、德语、中文、日语等。

Narrator

The ancient door creaked open...

Kira

We need to move. Now.

Thane

I have a bad feeling about this.

### 游戏与娱乐

用独特声音让角色鲜活起来，不必为每一句台词安排录音室时间。

Chapter 3

The Discovery

She opened the notebook and found the handwriting unmistakably her own though she had no memory of writing it

4:12

12:34

### 播客与有声书朗读

让你的叙事引人入胜。把脚本变成用你自己的声音逐章朗读的完整有声书，不必走进录音室。

Live Support

I need help with my recent order.

Of course! Let me pull up your order details.

Rec

00:

42

In today's episode we dive deep into the future of AI and what it means for creators everywhere

Original

Preserved

🇺🇸

🇪🇸

🇫🇷

🇩🇪

🇨🇳

🇯🇵

🇺🇸

English

🇪🇸

Spanish

🇫🇷

French

🇩🇪

German

🇨🇳

Chinese

🇯🇵

Japanese

Narrator

The ancient door creaked open...

Kira

We need to move. Now.

Thane

I have a bad feeling about this.

Chapter 3

The Discovery

She opened the notebook and found the handwriting unmistakably her own though she had no memory of writing it

4:12

12:34

### 品牌声音智能体

给你的客服智能体一个与你品牌识别一致的、可辨识的声音，而不是通用预设。

## [Custom Voices](https://x.ai/news/grok-custom-voices#custom-voices)

**两分钟内克隆你的声音，随处使用。**

在 [xAI console](https://console.x.ai/team/default/voice/voice-library?campaign=custom-voices-blog&utm_source=website&utm_medium=referral&utm_campaign=custom-voices-blog) 中录制约一分钟自然说话。我们的管线会验证你是声音的所有者、处理你的录音，并交付一个生产就绪的声音模型——全程两分钟以内。你的自定义声音继承 TTS 的全部能力：[语音标签（speech tags）](https://docs.x.ai/developers/model-capabilities/audio/text-to-speech?campaign=custom-voices-blog)、多语言输出，以及 REST 和 WebSocket 流式传输。

PASSPHRASE CHECK

RECORDING

My

voice

is

my

key

Step

1

Read a passphrase aloud to confirm your identity

自定义声音适用于所有内置声音能去的地方。把 `voice_id` 传给任意 [TTS 端点](https://docs.x.ai/developers/model-capabilities/audio/text-to-speech?campaign=custom-voices-blog)，或在 [Voice Agent API](https://docs.x.ai/developers/model-capabilities/audio/speech-to-speech?campaign=custom-voices-blog) 中用它构建实时对话智能体。

使用自定义声音调用 Text to Speech 或 Voice Agent API 不收取额外费用。

## [声音安全](https://x.ai/news/grok-custom-voices#voice-safety)

每个自定义声音在创建前都必须通过两阶段验证流程。首先，说话者朗读一句验证短语，我们的 STT 引擎实时转录并比对，确认意愿与本人在场。然后，我们分别从验证片段和完整录音计算说话人嵌入（speaker embeddings），确认两者属于同一个人。

你不能用既有录音克隆声音，也不能克隆别人的声音。

PASSPHRASE CHECK

RECORDING

My

voice

is

my

key

### 口令验证

朗读一句验证短语。我们的 STT 引擎实时转录并比对，验证你的同意与本人在场。

SPEAKER SIMILARITY

IDLE

PASSPHRASE

–

RECORDING

### 说话人相似度

比较来自口令和完整录音的说话人嵌入，确认它们属于同一个人。

Clone your voice
