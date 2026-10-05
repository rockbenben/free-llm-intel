---
vendor: inception_labs
title: Mercury 2: the first reasoning model fast enough to pick up the phone
original_title: Mercury 2: the first reasoning model fast enough to pick up the phone
url: https://www.inceptionlabs.ai/blog/mercury-2-the-first-reasoning-model-fast-enough-to-pick-up-the-phone
date: 2026-09-29
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 7440f0d150f4
---

For the past two years, every frontier lab has hillclimbed intelligence in the same way: **letting models think for longer**. Reasoning models now burn thousands of thinking (pontificating, cerebrating, lollygagging) tokens before saying a word. Under the dominant autoregressive decoding paradigm, every one of those tokens is generated sequentially, each requiring a full forward pass. On the phone with a voice agent, this generation (decode) time stacks up to the point where you’d rather just hang up.

The result is a strange split in the industry. The reasoning intelligence frontier has sprinted ahead, while **realtime intelligence has stood still**. Voice is one of the only verticals where GPT 5.x, Claude Sonnet, and Gemini Pro simply fail to meet the bar because nobody wants to wait 3 seconds every time they answer a question about their dentist appointment.

**Mercury 2 is the world’s first reasoning diffusion language model**, decoding 1000+ tokens per second on standard NVIDIA GPUs. That’s fast enough to run a full reasoning pass *and* start speaking within the latency budget of a natural conversation. We reduce the cost of reasoning from 3 seconds of dead air to only 300 milliseconds.

## Voice agents are stuck in April 2025

Voice customers tell us that end-to-end LLM latency must land under ~500ms, or the conversation stops feeling human.

A reasoning model that emits 500 chain-of-thought tokens at a typical autoregressive 60–100 tokens/sec blows through that budget by *five to eight seconds*. So voice builders have to choose between a smart model that sounds broken or a fast model that can't follow instructions.

Most of them have resolved it the same way: **GPT 4.1, OpenAI's smartest non-reasoning model — from April 2025(!)** — remains the default brain of most production voice agents. It's one of the only models that combines strong instruction-following and tool-calling with realtime latency at a price that scales to thousands of calls a day. But GPT 4.1 is scheduled to sunset on many providers later this year, meaning the voice agent industry is about to lose its default model, and none of the frontier reasoning models can take its seat.

One escape hatch is exotic hardware: serving on Cerebras or Groq gets you autoregressive decoding at impressive speeds. But capacity on custom silicon is scarce and frequently booked out with 12+ month wait times; Cerebras’ massive multiyear deal with OpenAI has locked up most of its resources, squeezing out smaller contracts. So the real question is: what if you could get **custom-silicon decode speeds** on the NVIDIA GPUs everyone already has?

## Why diffusion doesn't need to go one token at a time

The bottleneck in every autoregressive LLM is structural. Sequential decoding means that each output token requires a full forward pass, and each forward pass means streaming the entire model's weights from GPU HBM into on-chip SRAM. At the low batch sizes that latency-sensitive serving demands, this leaves most of the GPU's arithmetic bandwidth idle.

Mercury models are diffusion large language models (dLLMs), using **an architecture that generates tokens in parallel.**

As we detail in our[ technical report](https://arxiv.org/abs/2506.17298), generation works through a pair of processes. A *forward* process takes clean text and progressively corrupts it into noise over a series of steps. The model — a standard Transformer — is trained to run this in *reverse*: given a noisy latent sequence, it predicts the clean text, and it is trained with a denoising objective to do so for **all positions in the sequence simultaneously**.

Each denoising pass touches many tokens, so the arithmetic intensity of generation is far higher than one-token-at-a-time decoding, i.e., the same weights loaded from memory do many tokens' worth of useful math. The result, is **over 1,000 tokens/second on NVIDIA H100s — throughput previously possible only on custom chips** — at a quality comparable to smaller frontier models such as GPT Mini and Claude Haiku.

## Doing the math on realtime reasoning

At 1000+ tokens/second, a 300-token reasoning trace completes in under 300ms. That means the deliberation that makes reasoning models good at tool selection, policy compliance, and multi-step workflows now **fit inside a single turn**, inaudibly for the caller.

Mercury 2 utilizes a `reasoning_effort` knob with four settings — instant, low, medium, and high — so builders can , according to the intelligence needed for their application.

We benchmarked `instant`, `low` and `medium` on** IFBench** (instruction following) and **Tau3Bench Telecom** (realistic multi-turn tool-calling for customer-service agents), with latency measured on real production prompts from OpenCall.

“At OpenCall, we have been using Mercury 2 to power our production voice agents handling complex patient calls. In our testing, Mercury 2 outperformed GPT OSS 120B on Cerebras on instruction-following, tool-use and reasoning through multi-step workflows. It gives us the reasoning quality we need without sacrificing the latency required for a natural phone call experience.”

Oliver Silverstein, OpenCall CEO

**Instant** trades intelligence for reflex speed, making it suitable for acknowledgments, backchannels, and turns that don’t require tool calls. **Low** already beats GPT 4.1 on instruction following at a fraction of the latency. And **medium** is the headline, beating out GPT 4.1 by 27 points on IFBench and 24 points on Tau3Bench Telecom while *still* being faster than GPT 4.1's non-reasoning decode:

## Why cascaded pipelines still win over speech-to-speech

You might be thinking: why optimize the LLM in a cascaded pipeline at all, when speech-to-speech models exist? Despite the naturalness of full duplex voice models, almost all production voice agents in 2026 still run **ASR → LLM → TTS** for at least four reasons:

**Flexibility. **When operating voice agents across multiple regions and accents, you can swap transcription models and voices per market.

**Observability.** Cascaded pipelines produce text transcripts rather than thousands of hours of opaque audio, enabling scalable QA and auditing.

**Intelligence.** Today's speech-to-speech models still lag on long-context performance, multi-turn coherence and tool-calling accuracy.

**Cost.** At $32/$64 per million tokens, GPT Realtime 2 pricing doesn’t survive contact with call-center volume. Mercury 2 is priced at **$0.25/M input, $0.75/M output**, which works out to roughly **half a cent per minute of conversation**.

> Assuming a production voice-agent profile: ~4 conversational turns per minute; ~2,000-token system prompt plus growing conversational history re-sent on each turn (~20,000 input tokens per conversation-minute); ~600 output tokens per minute including reasoning tokens (~50 spoken-response tokens and ~100 reasoning tokens per turn). Mercury 2 list pricing of $0.25/M input and $0.75/M output. Model-layer cost only; excludes STT, TTS, and telephony.

Cascaded pipelines are still hip, but what's been missing is a brain for them that can reason in realtime. As an OpenAI-API compatible endpoint, Mercury drops into the LLM slot of whatever orchestration stack you already run — LiveKit, Pipecat, Vapi, Retell, or your own.

## What's next

Realtime reasoning changes what a voice agent can do. We've been working with voice platforms and enterprises on longer contexts, frontier tool-calling performance, and a latency-aware reasoning mode.

**Want to see how Mercury 2 handles your prompts?** The API is live at[ platform.inceptionlabs.ai 

](https://platform.inceptionlabs.ai/)**Benchmarking production voice latency?** We'll provision higher throughput capacity so you can measure real-world performance on your workload. [Get in touch with our team](https://www.inceptionlabs.ai/enterprise#contact-sales).
