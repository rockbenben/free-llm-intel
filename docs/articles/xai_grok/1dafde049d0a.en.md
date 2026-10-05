---
vendor: xai_grok
title: Introducing the Voice Agent Builder
original_title: Introducing the Voice Agent Builder
url: https://x.ai/news/grok-voice-agent-builder
date: 2026-07-01
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: d98167c0bcd5
---

Back to news

Jul 1, 2026

# Introducing the Voice Agent Builder

Create a personalized voice agent in under 2 minutes without a single line of code.

Try It Free

Explore Voice Agents

Today, we’re announcing Voice Agent Builder in beta: a no-code platform to configure production voice agents on [Grok Voice](https://x.ai/news/grok-voice-think-fast-1).

It’s for operators and developers who want high-volume production voice agents without building the surrounding stack from scratch. Out of the box you get telephony, knowledge retrieval, tools, guardrails, MCPs, and observability in one place. You can also keep what you already have: bring existing phone numbers over SIP, wire tools to your APIs and MCP servers, or connect your own client over WebSocket.

Most voice stacks stitch together three APIs—speech-to-text, a language model, and text-to-speech—often with each stage hosted by a different provider. Every hop adds cost, latency, and new failure modes. Voice Agent Builder is one interface on a speech-to-speech path built for Grok Voice, tightly coupled to the model rather than assembled from three.

0:00

/

0:00

## [Trained on the hardest calls we could find](https://x.ai/news/grok-voice-agent-builder#trained-on-the-hardest-calls-we-could-find)

Real calls come with low-quality telephony audio, background noise, strong accents, interruptions, and callers who change their minds mid-sentence. The workflows behind them are ambiguous, run across dozens of tools, and happen in any of 25+ languages.

We trained [Grok Voice](https://x.ai/news/grok-voice-think-fast-1) on those calls. τ-voice Bench measures agents under the same conditions.

τ-voice Bench Leaderboard

Grok Voice Think Fast 1.0

67.3

%

Gemini 3.1 Flash Live

43.8

%

GPT Realtime 1.5

35.3

%

## [Two minutes to an agent](https://x.ai/news/grok-voice-agent-builder#two-minutes-to-an-agent)

Setup is simple: write a plain-language description of how calls should flow, then attach your documents, tools, and guardrails. You can go from zero to a working agent in about two minutes.

### [Teach it your business](https://x.ai/news/grok-voice-agent-builder#teach-it-your-business)

An agent starts with a prompt that describes how calls should go. The model reasons in real time, so it can follow long instructions and work through ambiguous requests.

What it *knows* comes from the **knowledge base**. You upload documents in common formats (plain text, Markdown, Word, PowerPoint, Excel, HTML, JSON, and others), and the agent retrieves from them during calls. Documents are organized into **collections**, which you can attach to one or more agents and share across agents so policies, product specs, and runbooks stay in one place instead of being pasted into every prompt.

### [Take action](https://x.ai/news/grok-voice-agent-builder#take-action)

Knowing the business is only half of a support or sales call. Agents also need to **act**. They look things up, change records, hand off, or close the loop after the conversation.

**Tools** and **connectors** are how that happens. On a booking line, the agent might schedule appointments in Google Calendar or Outlook Calendar, then send a confirmation through your email provider. On support, an API request can check order status or issue a refund in your own systems. When the answer isn't only in your documents, web search or X search can pull current public information. Tickets can be managed in Linear or Notion, and files come from Google Drive or OneDrive.

If the caller needs a human, the agent can transfer the call to your team. When the task is complete, it can end the call cleanly. Throughout the conversation, it sends real-time notifications so your team can see what the agent did and step in if needed.

search_help_center

transfer_to_human

### [Give it a voice and a number](https://x.ai/news/grok-voice-agent-builder#give-it-a-voice-and-a-number)

Agents can use any of the built-in voices, or a clone of your brand's voice made from about two minutes of audio. Each account includes a free phone number, ready for anything from a first test call to production traffic, and direct SIP connects an existing number from any major telephony provider. You can also test changes in the browser without a phone.

### [Review the calls](https://x.ai/news/grok-voice-agent-builder#review-the-calls)

Every call is recorded and transcribed. You can play back the audio, read the transcript, and see which tools the agent used. Guardrails set limits on what the agent shouldn't do, like reading back card numbers or discussing topics off script.

## [What it costs](https://x.ai/news/grok-voice-agent-builder#what-it-costs)

We believe that pricing should be simple and transparent. Agents are billed at our API rate (currently [$0.08 / min of audio](https://docs.x.ai/developers/pricing#voice-api-pricing)), with voices included and no separate platform fee. Telephony on a free provisioned number is an additional $0.01 / min.

Other voice stacks commonly bill for each individual component (recognition, reasoning, synthesis, and platform), each with its own meter and pricing. We wanted a small number of meters you can multiply by call volume and be done.

## [Try it](https://x.ai/news/grok-voice-agent-builder#try-it)

A voice agent is easier to judge by ear than by benchmark. Build one, give it your hardest workflow, and call it.

Try It Free

Explore Voice Agents
