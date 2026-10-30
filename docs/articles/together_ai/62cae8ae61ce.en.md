---
vendor: together_ai
title: Announcing the fastest inference for realtime voice AI agents
original_title: 
url: https://www.together.ai/blog/the-fastest-inference-for-realtime-voice-ai-agents
date: 2025-11-04
lang: en
captured: 2026-10-30
extractor: readability-v1
status: ok
body_sha: 66a80ba5d6b3
---

All blog posts

Model Library

Published 11/4/2025

# Announcing the fastest inference for realtime voice AI agents

- AuthorsRajas Bansal, Sahil Yadav, Garima Dhanania, Sri Yanamandra, Charles Zedlewski, Zain Hasan, Derek Petersen, Blaine Kasten, Sonny Khan, Rishabh Bhargava
- Table of contents[40+ Models Chosen for Production...40+ Models Chosen for Production...40+ Models Chosen for Production...](https://www.together.ai/blog/the-fastest-inference-for-realtime-voice-ai-agents)
- Links in this article[Playground](https://api.together.ai/playground/mistralai/Voxtral-Mini-3B-2507)[Speech-to-Text Documentation](https://docs.together.ai/docs/speech-to-text)[Text-to-Speech Documentation](https://docs.together.ai/docs/text-to-speech)[Model library](http://together.ai/models)‍

Summary

- **Streaming Whisper speech-to-text (STT):** Continuous transcription over WebSocket APIs optimized for voice agents
- **First serverless open-source text-to-speech (TTS):** Orpheus (high-fidelity) and Kokoro (ultra-low latency) available through REST and WebSocket APIs without dedicated infrastructure
- ‍**Voxtral transcription and speaker diarization:** Premium multilingual transcription model and automatic speaker identification for batch processing

[Voice](https://www.together.ai/solutions/voice) interfaces are one of the hallmarks of a truly AI native application. From transcription to speech-to-code to outbound calling to custom podcasts, voice makes applications engaging and productive. But developers often have to piece together a number of specialized voice services to ship a single voice application. This tends to slow development while adding complexity, latency and cost.

We're pleased to announce the addition of a greatly expanded set of high performance, low latency voice infrastructure to our cloud. We've worked hard to provide voice services that are frontier quality, developer friendly and very low latency.

With these additions, we've expanded our voice offering from transcription to a full set of building blocks that can power some or all of an application's voice pipeline. These services support real-time and batch patterns in developer-friendly serverless and dedicated form factors.

## ‍**Streaming speech-to-text for voice agents**

#### Streaming Whisper

Traditional batch transcription waits for complete audio files. Voice agents need to process speech as it arrives, and intelligently detect when users finish speaking.

We've built the industry's fastest speech-to-text API by combining optimized model [inference](https://www.together.ai/serverless-inference) with intelligent system design — WebSocket streaming to eliminate connection overhead, carefully tuned voice activity detection (VAD), and purpose-built infrastructure for realtime audio processing. The result: [Whisper](http://www.together.ai/models/whisper-large-v3-streaming) running in real time with minimal quality degradation, completing transcripts up to 35% faster than alternatives.

The key is optimizing for time-to-complete-transcript, not just time-to-first-token. Voice agents need to know precisely when a user stops speaking to begin formulating responses. Our VAD tuning ensures your agent responds at the right moment, not too early (cutting users off) or too late (creating dead air).

STREAMING WHISPER

Your browser does not support the video tag.

Real-time transcription with industry-leading latency. Carefully tuned voice activity detection for natural conversation flow.

$0.0035/min

Try now

## **Text-to-speech: Serverless open-source models**

Together AI is the first cloud to provide serverless open-source text-to-speech models. No more spinning up dedicated instances for sporadic TTS needs — both models are available through REST APIs for batch generation and WebSocket APIs for realtime streaming.

#### Orpheus TTS: Natural voice quality

[Orpheus](http://www.together.ai/models/orpheus-tts) delivers natural, expressive speech with multiple voice options suitable for customer-facing applications. At 187ms time-to-first-byte, it outpaces premium providers while approaching the speed of lighter models. The result: professional voice quality without sacrificing the responsiveness voice agents require.

ORPHEUS TTS

Your browser does not support the video tag.

High-fidelity voice generation with natural prosody. 187ms average time-to-first-byte—faster than premium proprietary providers.

$15/1M chars

Try now

#### Kokoro TTS

When every millisecond counts, [Kokoro](http://www.together.ai/models/kokoro-82m) delivers. With 97ms baseline TTFB, it's built for applications where response speed trumps all else. This predictable performance makes it ideal for high-volume voice agent deployments where cost and latency are critical.

KOKORO TTS

Your browser does not support the video tag.

Ultra-fast production-scale voice. 97ms time- to-first-byte—more than 2x faster than alternatives with consistent performance under load.

$4/1M chars

Try now

## **New audio transcriptions**

Two new capabilities expand our audio transcriptions API for batch processing workflows:

#### **Voxtral Mini**

[Voxtral Mini](http://www.together.ai/models/voxtral-mini-3b-2507) is a higher-accuracy transcription model from Mistral AI, optimized for European languages and challenging audio conditions. [Voxtral delivers measurably lower word error rates than standard Whisper](https://mistral.ai/news/voxtral/) — ideal for applications where transcription mistakes create liability or operational overhead.

VOXTRAL

Your browser does not support the video tag.

Premium multilingual transcription optimized for European languages and challenging audio conditions with measurably lower word error rates.

$0.0030/min

Try now

#### **Speaker Diarization**

Automatically identify and label different speakers in recorded audio. Transform raw transcripts into structured conversations showing who said what and when — essential for meeting transcription, call center quality assurance, and multi-party conversation review.

## **Built for production voice agents**

Three architectural decisions make Together AI's audio infrastructure uniquely suited for production voice agents:

#### **Latency: Response times that enable natural conversation**

Human conversation flows at a specific pace. Responses that take longer than 500ms feel unnatural. Beyond 2 seconds, users assume the system has failed. Every additional 100ms of latency measurably decreases user satisfaction and task completion rates.

Our infrastructure eliminates unnecessary latency at every layer. WebSocket connections stay alive, avoiding TCP handshake overhead. Models run on the same GPU clusters as your LLMs, eliminating cross-provider networking. Most critically, our optimized serving delivers consistent sub-200ms TTS and millisecond-accurate transcription even during traffic spikes.

Real-world impact: When a customer calls to change their flight, every second of delay increases the chance they'll hang up. The voice agent must capture their request, process it, and begin responding — all within the natural rhythm of human conversation.

#### **Quality: Accurate transcription and natural-sounding speech**

Voice agents fail when transcription errors cascade through the conversation. A misheard account number becomes a failed lookup. A garbled product name triggers the wrong workflow. Poor voice quality immediately signals "cheap automation" regardless of underlying intelligence.

That's why we offer multiple quality tiers. Streaming Whisper handles realtime transcription with enough accuracy for natural conversation. When precision matters — legal depositions, medical consultations, financial transactions — Voxtral's superior accuracy justifies its premium pricing. On the output side, Orpheus provides the natural, expressive voices users expect from professional services, while Kokoro offers clear, efficient speech for high-volume informational use cases.

Consider a healthcare scheduling bot: It must accurately capture medication names, understand accented speech, and respond with appropriate empathy. Quality failures at any layer break user trust and force expensive human escalation.

#### **Scale: Consistent performance under production load**

Voice infrastructure that performs well in demos but fails under production load creates a trust problem. Users who experience degraded service during peak hours learn to avoid the system entirely.

Our infrastructure maintains performance as load scales. A unique optimization in our WebSocket implementation allows multiplexing multiple conversations through single connections — critical for platforms like contact center software handling hundreds of simultaneous calls. Instead of managing thousands of individual WebSocket connections (with associated memory and networking overhead), you can efficiently route multiple isolated audio streams through shared connections.

This same approach to scale applies across our stack. Geographic distribution ensures low latency regardless of user location. Automatic scaling handles traffic spikes without manual intervention. The result: voice agents that perform identically whether handling 10 or 10,000 concurrent conversations.

## **Try it now**

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

**Get started:**

- [Playground](https://api.together.ai/playground/mistralai/Voxtral-Mini-3B-2507): Test audio models before building
- [Speech-to-Text Documentation](https://docs.together.ai/docs/speech-to-text): Complete API reference for transcription
- [Text-to-Speech Documentation](https://docs.together.ai/docs/text-to-speech): Complete API reference for voice generation
- [Model library](http://together.ai/models): Complete model specifications

**For production deployments:
**[Contact our sales](https://www.together.ai/contact-sales) team for enterprise options and dedicated infrastructure.

## Related articles

View All

View All
