---
vendor: together_ai
title: Announcing the fastest inference for realtime voice AI agents
original_title: 
url: https://www.together.ai/blog/the-fastest-inference-for-realtime-voice-ai-agents
date: 2025-11-04
lang: zh
captured: 2026-10-31
extractor: readability-v1
translator: mt
status: translated
body_sha: 6d02e5f54fe1
---

所有博客文章

模型库

发布日期：2025 年 11 月 4 日

# 宣布实时语音 AI 代理最快的推理

- 作者Rajas Bansal、Sahil Yadav、Garima Dhanania、Sri Yanamandra、Charles Zedlewski、Zain Hasan、Derek Petersen、Blaine Kasten、Sonny Khan、Rishabh Bhargava
- 目录[40+ 选择用于生产的模型...40+ 选择用于生产的模型...40+ 选择用于生产的模型...](https://www.together.ai/blog/the-fastest-inference-for-realtime-voice-ai-agents)
- 本文中的链接[Playground](https://api.together.ai/playground/mistralai/Voxtral-Mini-3B-2507)[语音转文本文档](https://docs.together.ai/docs/speech-to-text)[文本转语音文档](https://docs.together.ai/docs/text-to-speech)[模型库](http://together.ai/models)‍

总结

- **流式 Whisper 语音转文本 (STT)：** 通过针对语音代理优化的 WebSocket API 进行连续转录
- **第一个无服务器开源文本转语音 (TTS)：** Orpheus（高保真）和 Kokoro（超低延迟）可通过 REST 和 WebSocket API 获得，无需专用基础设施
- ‍**Voxtral 转录和说话人分类：** 高级多语言转录模型和用于批量处理的自动说话人识别

[语音](https://www.together.ai/solutions/voice) 接口是真正的 AI 原生应用程序的标志之一。从转录到语音到代码，再到出站呼叫，再到自定义播客，语音使应用程序更具吸引力和生产力。但开发人员通常必须将许多专门的语音服务组合在一起才能发布单个语音应用程序。这往往会减慢开发速度，同时增加复杂性、延迟和成本。

我们很高兴地宣布在我们的云中添加了一组大幅扩展的高性能、低延迟语音基础设施。我们一直致力于提供前沿质量、开发人员友好且延迟极低的语音服务。

通过这些新增功能，我们将语音产品从转录扩展到了一整套构建块，可以为应用程序的部分或全部语音管道提供支持。这些服务支持开发人员友好的无服务器和专用外形的实时和批处理模式。

## ‍**语音代理的流式语音转文本**

#### 流媒体耳语

传统的批量转录需要等待完整的音频文件。语音代理需要在语音到达时进行处理，并智能检测用户何时结束讲话。

我们通过将优化模型[推理](https://www.together.ai/serverless-inference)与智能系统设计相结合，构建了业界最快的语音到文本 API - WebSocket 流式传输以消除连接开销、精心调整的语音活动检测 (VAD) 以及用于实时音频处理的专用基础设施。结果：[Whisper](http://www.together.ai/models/whisper-large-v3-streaming) 实时运行，质量下降最小，完成转录的速度比替代方案快 35%。

关键是优化完成转录的时间，而不仅仅是首次标记的时间。语音代理需要准确地知道用户何时停止说话才能开始制定响应。我们的 VAD 调整可确保您的代理在正确的时刻做出响应，不会太早（切断用户）或太晚（造成死气沉沉）。

流媒体耳语

您的浏览器不支持视频标签。

具有行业领先延迟的实时转录。仔细调整语音活动检测以实现自然的对话流程。

$0.0035/分钟

立即尝试

## **文本转语音：无服务器开源模型**

Together AI 是第一个提供无服务器开源文本转语音模型的云。不再需要为零星的 TTS 需求而旋转专用实例——这两种模型都可以通过用于批量生成的 REST API 和用于实时流传输的 WebSocket API 来使用。

#### Orpheus TTS：自然的语音质量

[Orpheus](http://www.together.ai/models/orpheus-tts) 提供自然、富有表现力的语音，具有适合面向客户的应用程序的多种语音选项。它的首字节时间为 187 毫秒，超过了优质提供商，同时接近较轻型号的速度。结果：专业的语音质量，同时又不牺牲语音代理所需的响应能力。

奥菲斯 TTS

您的浏览器不支持视频标签。

具有自然韵律的高保真语音生成。平均首字节时间为 187 毫秒，比优质专有提供商更快。

$15/100 万个字符

立即尝试

#### 心 TTS

当每一毫秒都很重要时，[Kokoro](http://www.together.ai/models/kokoro-82m) 交付。它具有 97 毫秒基线 TTFB，专为响应速度高于一切的应用而设计。这种可预测的性能使其成为成本和延迟至关重要的大容量语音代理部署的理想选择。

KOKORO TTS

您的浏览器不支持视频标签。

超快的生产规模语音。第一个字节的时间为 97 毫秒——比替代方案快 2 倍以上，并且在负载下具有一致的性能。

$4/100 万个字符

立即尝试

## **新的音频转录**

两项新功能扩展了我们用于批处理工作流程的音频转录 API：

#### **Voxtral 迷你**

[Voxtral Mini](http://www.together.ai/models/voxtral-mini-3b-2507) 是 Mistral AI 的高精度转录模型，针对欧洲语言和具有挑战性的音频条件进行了优化。 [Voxtral 的字错误率明显低于标准 Whisper](https://mistral.ai/news/voxtral/) — 非常适合转录错误造成责任或运营开销的应用。

沃斯特拉尔

您的浏览器不支持视频标签。

优质多语言转录针对欧洲语言和具有挑战性的音频条件进行了优化，单词错误率显着降低。

$0.0030/分钟

立即尝试

#### **说话人分类**

自动识别并标记录制音频中的不同说话者。将原始记录转换为结构化对话，显示谁在何时说什么——对于会议转录、呼叫中心质量保证和多方对话审核至关重要。

## **专为生产语音代理而构建**

三个架构决策使 Together AI 的音频基础设施特别适合生产语音代理：

#### **延迟：实现自然对话的响应时间**

人类的对话以特定的速度进行。花费超过 500 毫秒的响应会让人感觉不自然。超过 2 秒，用户认为系统出现故障。每增加 100 毫秒的延迟就会显着降低用户满意度和任务完成率。

我们的基础设施消除了每一层不必要的延迟。 WebSocket 连接保持活动状态，避免 TCP 握手开销。模型与LLM在相同的 GPU 集群上运行，从而消除了跨提供商网络。最重要的是，即使在流量高峰期间，我们的优化服务也能提供一致的低于 200 毫秒的 TTS 和毫秒级准确的转录。

现实世界的影响：当客户致电更改航班时，每一秒的延误都会增加他们挂断电话的可能性。语音代理必须捕获他们的请求、处理它并开始响应——所有这些都在人类对话的自然节奏内。

#### **质量：准确的转录和自然的语音**

当转录错误在对话中级联时，语音代理会失败。听错帐号就会导致查找失败。乱码的产品名称会触发错误的工作流程。无论潜在的智能如何，语音质量差都会立即发出“廉价自动化”的信号。

这就是我们提供多个质量等级的原因。 Streaming Whisper 可以足够准确地处理实时转录，以实现自然对话。当精确性至关重要时——法律证词、医疗咨询、金融交易——Voxtral 卓越的精确性证明了其高定价的合理性。在输出方面，Orpheus 提供用户期望从专业服务中获得的自然、富有表现力的声音，而 Kokoro 则为大容量信息用例提供清晰、高效的语音。

考虑一个医疗保健调度机器人：它必须准确捕获药物名称，理解口音语音，并以适当的同理心做出回应。任何一层的质量故障都会破坏用户的信任，并迫使成本高昂的人工升级。

#### **规模：生产负载下的一致性能**

在演示中表现良好但在生产负载下失败的语音基础设施会产生信任问题。在高峰时段遇到服务质量下降的用户学会完全避开该系统。

我们的基础设施随着负载的扩展而保持性能。我们的 WebSocket 实现中的独特优化允许通过单个连接复用多个对话，这对于处理数百个同时呼叫的联络中心软件等平台至关重要。您可以通过共享连接有效地路由多个独立的音频流，而不是管理数千个单独的 WebSocket 连接（具有相关的内存和网络开销）。

同样的扩展方法也适用于我们的整个堆栈。无论用户位于何处，地理分布都可确保低延迟。自动扩展无需人工干预即可处理流量峰值。结果是：无论处理 10 个还是 10,000 个并发对话，语音代理的性能都相同。

## **立即尝试**
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
**开始：**

- [Playground](https://api.together.ai/playground/mistralai/Voxtral-Mini-3B-2507)：构建前测试音频模型
- [Speech-to-Text 文档](https://docs.together.ai/docs/speech-to-text)：用于转录的完整 API 参考
- [文本转语音文档](https://docs.together.ai/docs/text-to-speech)：用于语音生成的完整 API 参考
- [模型库](http://together.ai/models)：完整的模型规格

**对于生产部署：
**[联系我们的销售人员](https://www.together.ai/contact-sales) 团队以获取企业选项和专用基础设施。

## 相关文章
