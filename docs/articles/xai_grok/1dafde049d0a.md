---
vendor: xai_grok
title: 介绍 Voice Agent Builder
original_title: Introducing the Voice Agent Builder
url: https://x.ai/news/grok-voice-agent-builder
date: 2026-07-01
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# 介绍 Voice Agent Builder

不写一行代码，两分钟内创建个性化的语音智能体。

Try It Free

Explore Voice Agents

今天，我们宣布 Voice Agent Builder 进入 beta：一个无代码平台，用于在 [Grok Voice](https://x.ai/news/grok-voice-think-fast-1) 上配置生产级语音智能体。

它面向需要高并发生产语音智能体、又不想从零搭建周边技术栈的运营者与开发者。开箱即得电话接入、知识检索、工具、护栏、MCP 和可观测性，全在一个地方。你也可以保留已有的东西：通过 SIP 带入现有号码，把工具接到你的 APIs 和 MCP 服务器，或通过 WebSocket 连接你自己的客户端。

多数语音技术栈是把三个 API 缝合起来的——speech-to-text、语言模型、text-to-speech——而且每一段常常由不同供应商托管。每一次跳转都增加成本、延迟和新的故障模式。Voice Agent Builder 是一个统一界面，背后是为 Grok Voice 专门构建的 speech-to-speech 通路——与模型紧耦合，而不是三段拼装。

0:00

/

0:00

## [用我们能找到的最难的通话来训练](https://x.ai/news/grok-voice-agent-builder#trained-on-the-hardest-calls-we-could-find)

真实通话伴随着低质量电话音频、背景噪音、重口音、插话，以及说话说到一半改主意的来电者。其背后的工作流含糊不清、横跨数十个工具，并可能发生在 25+ 种语言中的任一种里。

我们就是在这些真实通话上训练 [Grok Voice](https://x.ai/news/grok-voice-think-fast-1) 的。τ-voice Bench 在同样条件下衡量智能体。

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

## [两分钟，一个智能体](https://x.ai/news/grok-voice-agent-builder#two-minutes-to-an-agent)

设置很简单：用平实语言描述通话应如何流转，然后附上你的文档、工具和护栏。大约两分钟，从零到一个可工作的智能体。

### [教会它你的业务](https://x.ai/news/grok-voice-agent-builder#teach-it-your-business)

智能体始于一条描述通话应该如何进行的提示词。模型实时推理，因此能遵循冗长的指令、处理含糊的请求。

它*知道*的内容来自**知识库**。你上传常见格式的文档（纯文本、Markdown、Word、PowerPoint、Excel、HTML、JSON 等），智能体在通话中从中检索。文档按 **collections** 组织，你可以把它们挂到一个或多个智能体上并跨智能体共享——让政策、产品规格和 runbook 集中在一处，而不是贴进每一条提示词。

### [付诸行动](https://x.ai/news/grok-voice-agent-builder#take-action)

懂业务只是客服或销售通话的一半。智能体还需要**行动**：查询、改记录、转接，或在对话结束后闭环。

**Tools** 和 **connectors** 就是实现方式。在预约线路上，智能体可以在 Google Calendar 或 Outlook Calendar 里排预约，然后通过你的邮件服务商发送确认。在客服场景，API 请求可以查询订单状态，或在你的系统里发起退款。当答案不只在你的文档里时，网页搜索或 X 搜索可以拉取最新的公开信息。工单可以在 Linear 或 Notion 中管理，文件可以来自 Google Drive 或 OneDrive。

如果来电者需要真人，智能体可以把通话转给你的团队。任务完成后，它能利落地结束通话。全程它还会发送实时通知，让你的团队看到智能体做了什么、必要时随时介入。

search_help_center

transfer_to_human

### [给它一个声音和一个号码](https://x.ai/news/grok-voice-agent-builder#give-it-a-voice-and-a-number)

智能体可以使用任意内建声音，或用约两分钟音频制作的你品牌声音的克隆。每个账户包含一个免费号码——从第一次测试通话到生产流量皆可用的号码——直接 SIP 则可从任何主流 telephony 服务商接入现有号码。你也可以不用电话，直接在浏览器里测试改动。

### [复盘通话](https://x.ai/news/grok-voice-agent-builder#review-the-calls)

每通电话都会录制并转录。你可以回放音频、阅读转录文本、查看智能体用了哪些工具。护栏为智能体不该做的事设定限制，比如复述卡号或谈论剧本之外的话题。

## [成本几何](https://x.ai/news/grok-voice-agent-builder#what-it-costs)

我们相信定价应当简单透明。智能体按我们的 API 费率计费（目前为[$0.08/分钟音频](https://docs.x.ai/developers/pricing#voice-api-pricing)），声音包含在内，不收单独的平台费。用免费分配的号码打电话，另加 $0.01/分钟。

其他语音技术栈通常对每个组件单独计费（识别、推理、合成、平台），各有各的计量与价格。我们想要的，是少数几个可以乘上通话量的计量表，就这么简单。

## [试一试](https://x.ai/news/grok-voice-agent-builder#try-it)

语音智能体用耳朵判断比看基准更靠谱。搭一个，把你最难的工作流交给它，然后打个电话。

Try It Free

Explore Voice Agents
