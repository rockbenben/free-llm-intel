---
vendor: together_ai
title: 宣布面向实时语音 AI agent 的最快推理
original_title: 
url: https://www.together.ai/blog/the-fastest-inference-for-realtime-voice-ai-agents
date: 2025-11-04
lang: zh
captured: 2026-10-31
extractor: readability-v1
translator: agent
status: translated
body_sha: 74a6ae716236
---

# 宣布面向实时语音 AI agent 的最快推理

- 作者：Rajas Bansal、Sahil Yadav、Garima Dhanania、Sri Yanamandra、Charles Zedlewski、Zain Hasan、Derek Petersen、Blaine Kasten、Sonny Khan、Rishabh Bhargava
- 目录[为生产环境选定的 40+ 款模型…为生产环境选定的 40+ 款模型…为生产环境选定的 40+ 款模型…](https://www.together.ai/blog/the-fastest-inference-for-realtime-voice-ai-agents)
- 本文中的链接[Playground](https://api.together.ai/playground/mistralai/Voxtral-Mini-3B-2507)[语音转文本（Speech-to-Text）文档](https://docs.together.ai/docs/speech-to-text)[文本转语音（Text-to-Speech）文档](https://docs.together.ai/docs/text-to-speech)[Model library](http://together.ai/models)‍

摘要

- **流式 Whisper 语音转文本（STT）：** 基于 WebSocket API 的持续转写，为语音 agent 做过优化
- **首个 serverless 开源 text-to-speech（TTS）：** Orpheus（高保真）与 Kokoro（超低延迟），通过 REST 与 WebSocket API 提供，无需 dedicated 基础设施
- ‍**Voxtral 转写与 speaker diarization：** 面向批处理的高端多语种转写模型与自动说话人识别

[语音](https://www.together.ai/solutions/voice)交互是真正 AI 原生应用的标志之一。从转写、语音转代码，到外呼电话、定制播客，语音让应用既有吸引力又高效。但开发者往往要把一堆专项语音服务拼起来，才能交付一个语音应用。这通常会拖慢开发，同时增加复杂度、延迟和成本。

我们很高兴地宣布，云上新增了一整套高性能、低延迟的语音基础设施。我们下了很大功夫，让语音服务同时做到前沿品质、对开发者友好，以及极低的延迟。

有了这些新增能力，我们把语音产品线从转写扩展为一整套构件，足以支撑应用语音 pipeline 的部分或全部。这些服务同时支持实时与批量两种模式，并以开发者友好的 serverless 与 dedicated 两种形态交付。

## ‍**面向语音 agent 的流式语音转文本**

#### Streaming Whisper

传统批量转写要等完整的音频文件。语音 agent 需要在语音到达时就实时处理，并聪明地判断用户什么时候说完了。

我们把优化的模型[推理](https://www.together.ai/serverless-inference)与聪明的系统设计结合起来，做出了业内最快的语音转文本 API——用 WebSocket 流式传输消除连接开销、精心调校 voice activity detection（VAD）、以及为实时音频处理专门构建的基础设施。结果是：[Whisper](http://www.together.ai/models/whisper-large-v3-streaming) 以实时方式运行，质量损失极小，完成转写比同类方案快最多 35%。

关键在于优化 time-to-complete-transcript，而不只是 time-to-first-token。语音 agent 需要精确知道用户何时停止说话，才能开始组织回应。我们的 VAD 调校保证你的 agent 在恰当时机开口：既不太早（打断用户），也不太晚（留下冷场）。

STREAMING WHISPER

你的浏览器不支持 video 标签。

实时转写，延迟业内领先。为自然对话节奏精心调校的 voice activity detection。

$0.0035/min

立即试用

## **Text-to-speech：Serverless 开源模型**

Together AI 是首个提供 serverless 开源 text-to-speech 模型的云。不必再为间歇性的 TTS 需求单独拉起 dedicated 实例——两款模型都通过 REST API 提供批量生成、通过 WebSocket API 提供实时流式。

#### Orpheus TTS：自然的音色

[Orpheus](http://www.together.ai/models/orpheus-tts) 输出自然、富有表现力的语音，提供多种适合面向客户应用的音色。187ms 的 time-to-first-byte 让它快过高端供应商，同时逼近更轻量模型的速度。结果是：专业的音色，又不牺牲语音 agent 所需的响应性。

ORPHEUS TTS

你的浏览器不支持 video 标签。

高保真语音生成，韵律自然。平均 187ms 的 time-to-first-byte——比高端专有供应商更快。

$15/1M chars

立即试用

#### Kokoro TTS

当每一毫秒都要争，[Kokoro](http://www.together.ai/models/kokoro-82m) 就派上用场。97ms 的基线 TTFB，让它专为响应速度压倒一切的应用而生。这种可预期的性能，使它特别适合成本与延迟都至关重要的大批量语音 agent 部署。

KOKORO TTS

你的浏览器不支持 video 标签。

极快的生产规模语音。97ms 的 time-to-first-byte——比同类方案快 2 倍以上，且在负载下性能一致。

$4/1M chars

立即试用

## **全新音频转写能力**

两项新能力扩展了我们面向批处理工作流的音频转写 API：

#### **Voxtral Mini**

[Voxtral Mini](http://www.together.ai/models/voxtral-mini-3b-2507) 是 Mistral AI 出品的更高准确度转写模型，针对欧洲语言和复杂音频条件做过优化。[与标准 Whisper 相比，Voxtral 带来可测量的更低 word error rate](https://mistral.ai/news/voxtral/)——特别适合转写错误会造成责任风险或运维开销的应用。

VOXTRAL

你的浏览器不支持 video 标签。

面向欧洲语言与复杂音频条件优化的多语种高端转写，word error rate 更低且可测量。

$0.0030/min

立即试用

#### **Speaker Diarization（说话人分离）**

自动识别并标注录制音频中的不同说话人。把原始转写变成结构化对话，呈现谁在什么时候说了什么——这对会议转写、呼叫中心质检以及多方会话复盘都必不可少。

## **为生产级语音 agent 而生**

三个架构决策，让 Together AI 的音频基础设施格外适合生产环境的语音 agent：

#### **延迟：让自然对话成为可能的响应时间**

人类对话有自己的节奏。回应超过 500ms 就显得不自然；越过 2 秒，用户就认为系统坏了。每多 100ms 延迟，用户满意度与任务完成率都能测量到下降。

我们的基础设施在每一层消除不必要的延迟。WebSocket 连接保持存活，避开 TCP 握手开销。模型与你的 LLM 跑在同一批 GPU 集群上，消除跨供应商的网络传输。最关键的是，我们优化过的服务层即使在流量峰值期间也能交付稳定的 200ms 以内 TTS 和毫秒级精度的转写。

真实影响：当客户打电话来改签机票，每一秒延迟都会提高他们挂断的可能。语音 agent 必须接住请求、处理它并开始回应——全部落在人类对话的自然节奏之内。

#### **质量：准确的转写与自然的声音**

转写错误会在对话中层层传导，语音 agent 因此失效。听错一个账号会导致查询失败；一个含糊的产品名会触发错误的 workflow。而糟糕的音色会立刻透出“廉价自动化”的味道，无论底层智能有多强。

这正是我们提供多个质量档位的原因。Streaming Whisper 负责实时转写，准确度足以支撑自然对话。当精度至关重要——法律取证、医疗问诊、金融交易——Voxtral 更高的准确度对得起它的溢价。输出侧，Orpheus 提供用户在专业服务中期待的自然、富有表现力的声音，Kokoro 则为大批量信息类场景提供清晰高效的语音。

设想一个医疗排期 bot：它必须准确捕获药品名、听懂带口音的语音，并以恰当的同理心回应。任何一层的质量失守都会击穿用户信任，逼出昂贵的人工升级。

#### **规模：生产负载下的稳定性能**

演示里表现良好、生产负载下失效的语音基础设施会带来信任问题。在高峰时段体验到服务劣化的用户，会彻底绕开这个系统。

我们的基础设施在负载增长时保持性能。我们 WebSocket 实现中一项独特的优化，允许把多路对话 multiplexing 到单条连接上——这对呼叫中心软件这类要处理数百路并发通话的平台至关重要。你不必管理上千条独立的 WebSocket 连接（以及随之而来的内存与网络开销），而是可以把多条彼此隔离的音频流高效地复用共享连接。

同样的扩展思路贯穿我们整个技术栈。地理分布保证无论用户身处何地都保持低延迟。自动扩缩容应对流量峰值，无需人工介入。结果是：无论承载 10 路还是 10,000 路并发对话，语音 agent 的表现都完全一致。

## **立即体验**

```
	  
    from together import Together
    import asyncio

    client = Together()

    async def handle_conversation():
        # Listen to user input
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=audio_stream,
            language="en"
        )
        
        # Generate response while monitoring for interruptions
        async with client.audio.speech.create(
            model="canopylabs/orpheus-3b-0.1-ft",
            input="I can help with that-",
            voice="tara"
        ) as tts:
            
            audio_playback = asyncio.create_task(play_audio(tts))
            
            # Simultaneously monitor for user interruptions
            async for chunk in transcription:
                if "wait" in chunk.text.lower() or "actually" in chunk.text.lower():
                    audio_playback.cancel()
                    # Adapt to new user input
                    break
    
```

**开始上手：**

- [Playground](https://api.together.ai/playground/mistralai/Voxtral-Mini-3B-2507)：动手构建前先测试音频模型
- [语音转文本（Speech-to-Text）文档](https://docs.together.ai/docs/speech-to-text)：转写的完整 API 参考
- [文本转语音（Text-to-Speech）文档](https://docs.together.ai/docs/text-to-speech)：语音生成的完整 API 参考
- [Model library](http://together.ai/models)：完整的模型规格

**面向生产部署：
**[联系我们销售](https://www.together.ai/contact-sales)团队，获取企业级选项与 dedicated 基础设施。

## 相关文章
