---
vendor: together_ai
title: MiniMax Speech 2.6 Turbo now available natively on Together AI
original_title: 
url: https://www.together.ai/blog/minimax-speech-2-6
date: 2025-12-23
lang: zh
captured: 2026-10-31
extractor: readability-v1
translator: mt
status: translated
body_sha: 9a5f825f98c0
---

所有博客文章

模型库

发表于 12/23/2025

# MiniMax Speech 2.6 Turbo 现已在 Together AI 上原生提供

最先进的多语言 TTS，具有 40 多种语言的人类水平、情感感知语音，以及专用生产级基础设施上的实时延迟。

- 作者Arielle Fidel、Rajas Bansal、Sahil Yadav、Rishabh Bhargava、Sonny Khan
- 目录[40+ 选择用于生产的模型...40+ 选择用于生产的模型...40+ 选择用于生产的模型...](https://www.together.ai/blog/minimax-speech-2-6)
- 本文中的链接[MiniMax Speech 2.6 Turbo](https://www.together.ai/models/minimax-speech-2-6-turbo)[TTS 文档](https://docs.together.ai/docs/text-to-speech)[X](https://x.com/togethercompute)[Discord](https://discord.gg/9Rk6sSeWEG)[我们正在招聘！](https://www.together.ai/about#careers) [获取通知](https://www.together.ai/newsletter)‍

总结

- Together AI 上的 [**MiniMax Speech 2.6 Turbo**](https://www.together.ai/models/minimax-speech-2-6-turbo)**：**在人工分析竞技场上排名第一，仅在 Together AI 上的专用基础设施上可用
- 低于 250 毫秒的延迟、40 多种语言，具有流式内联切换、10 秒语音克隆、自动情绪感知
- 与 Cartesia 和 Rime 模型一起扩展 Together AI 上的精英专有 TTS 模型
- 专用 GPU 端点与 LLM 和 STT 工作负载位于同一位置

构建实时[语音](https://www.together.ai/solutions/voice)代理通常会迫使人们做出一个丑陋的选择：发布一个听起来令人信服的人类声音，或者发布一个立即响应并在生产中保持不变的声音。大多数团队通过拼凑的提供商来解决差异：一个用于展示体验，另一个用于低延迟转向，其他用于克隆或全球语言覆盖。随着时间的推移，这种拼凑而成的产品。行为因市场、延迟和质量漂移而有所不同，“升级语音”变成了跨供应商基础设施项目，而不是产品决策。

从今天开始，Together AI（AI 原生云）是唯一一个可以在专用基础设施上与 LLM 和 STT 工作负载一起运行 [MiniMax Speech 2.6 Turbo](https://www.together.ai/models/minimax-speech-2-6-turbo) 的平台，因此自然性和速度可以在一个平台上实现，而不是在各个供应商之间进行权衡。 MiniMax Speech 2.6 Turbo 在公共 TTS 排行榜上名列前茅，由 Talkie 背后的团队（1.5 亿用户，平均会话时间超过 90 分钟）构建，并经过训练以进行真正的对话交互，而不是朗读旁白。请求在 Together AI 基础设施上运行，具有零数据保留、SOC 2 Type II 和 HIPAA 支持以及数据驻留选项。您可以通过一个 API、一个身份验证和统一指标获得用于流传输、容量和调试的单一生产界面，因此会话延迟成为一种基础设施保证，而不是一种集成税。

MiniMax 多语言

英语到日语到西班牙语流媒体语言切换

2:54

“欢迎使用我们的服务。我们的人工智能实时无缝地弥合了文化之间的差距。日本语でもサポートできます。言葉の壁を越えて、世界中の人々と自然につながることができます。También ofrecemos soporte en español.全球通讯很简单。”

立即尝试

## **为什么自然会推动参与**

MiniMax Speech 2.6 Turbo 在人工盲评中名列人工分析竞技场榜首。该模型基于 Talkie 对话数据进行训练，其中 1.5 亿用户选择使用 AI 语音进行平均超过 90 分钟的会话。 MiniMax Speech 2.6 Turbo 不是从有声读物和播客旁白中学习，而是从真实对话中学习，从而产生不同的韵律、节奏和情感范围。

构建人工智能原生语音产品的团队选择语音质量直接驱动完成率的模型。客户服务代理可以拥有正确的意图识别和强大的 LLM 推理，但综合交付仍然会导致用户流失。 MiniMax Speech 2.6 Turbo 现已在 Together AI 上推出，其性能隔离和可靠性针对大规模生产工作负载进行了调整。

## **技术能力**

### **具有流内联切换功能的 40 多种语言**

通过流式内联语言切换，提供跨主要全球语言的本地质量语音。英语、日语、西班牙语、普通话、法语、德语中句，带有地道口音。该模型检测语言边界并实时切换为母语发音。

### **自动情绪感知**

该模型分析语义上下文并调整韵律。当你的LLM输出道歉语言时，MiniMax 会调整为同理心的表达方式。乐观的问候听起来很乐观。严重警告听起来很严重。这会在所有 40 多种语言中自动发生，无需立即进行工程或标记。

最小最大情绪意识

同一句话，语气富有同理心、乐观、严肃

2:54

” 善解人意：“我明白了。得知您遇到这个问题，我感到很遗憾。” 乐观：“我明白！很好的问题，让我帮忙解决一下。” 严肃地说：“我明白。这是一个至关重要的安全问题。”

立即尝试

### **10秒语音克隆**

从 10 秒音频样本中克隆声音。这个声音可以讲 40 多种语言，带有当地口音。该模型可以处理不完美的录音——背景噪音、口音、不流畅——并产生流畅的输出，同时保留独特的音色。为您的应用程序创建品牌声音，并通过 Together AI 在全球范围内部署。通过[销售](https://www.together.ai/contact-sales) 提供专业的语音克隆服务。

MiniMax原声

10秒原始样本

2:54

“你知道，一条特定的信息或某些事件或他们网站上的某些内容或他们知道的东西，嘿，当他们掌握这些信息时，他们更有可能需要我们的产品。”

MiniMax 语音克隆

使用样本生成的多语言输出

2:54

“现在，我用完全相同的声音说话，从短短十秒的音频中创建。甚至可以用这个声音说中文，音色和说话习惯都完美保留一次。Et maintenant，écoutez ma voix en français。Remarquez la flowité de la prononciation，qui Reste fidèle à mon timbre Original。”

立即尝试

### **Together AI 基础设施上的延迟低于 250 毫秒**

MiniMax 在 Together AI 专用端点上实现了低于 250 毫秒的延迟。当 TTS 在同一基础设施上与 LLM 和 STT 工作负载一起运行时，您可以消除跨供应商网络开销。从语音识别到推理再到合成的完整流程对于实时对话来说保持足够快。

### **自动格式处理**

URL、电子邮件地址、电话号码、日期和货币金额无需预处理即可转换。直接使用 LLM 输出，无需构建文本规范化管道。

## **用例**

### **客户服务代理**

在 Together AI 上部署语音代理，自然程度决定客户是否完成呼叫。 MiniMax Speech 2.6 Turbo 语音质量减少了合成检测造成的挂断。自动情绪意识意味着您的LLM专注于推理而不是语气管理。流式多语言支持意味着一次部署即可处理客户在英语、西班牙语和日语之间的切换。

### **大规模内容生成**

有声读物、电子学习课程和播客旁白，其中语音质量决定完成率。 Talkie 的平均会话时间超过 90 分钟，这表明 MiniMax Speech 2.6 Turbo 语音很受关注。 10 秒语音克隆意味着一位叙述者的声音可以跨越 40 多种语言并具有母语发音。在 Together AI 基础设施上部署内容生成工作负载，并具有与其他 AI 工作负载相同的可靠性和可观察性。

### **互动娱乐**

游戏、互动小说和虚拟同伴的角色声音。 MiniMax Speech 2.6 Turbo 所提供的表现力使 Talkie 取得了成功。自动情商意味着角色对对话环境做出自然反应。 10 秒克隆可快速制作角色声音原型。在 Together AI 专用端点上部署游戏语音基础设施，以保证流量高峰期间的性能。

MiniMax 游戏角色声音

情绪范围从愤怒到谨慎到温暖

2:54

“你敢挑战我？给我站住！再跨出一步，你就会后悔！等等……也许……这就是古老的护身符？我已经好几个世纪没有见过那个符号了……欢迎，我的朋友！哦，你是被选中的人之一！请进来，我们一起喝一杯！”

立即尝试

### **多语言应用程序**

服务全球用户群的应用程序需要跨语言一致的语音质量。 MiniMax Speech 2.6 Turbo 可通过 Together AI 基础设施上的流式内联切换处理 40 多种语言。构建一个可处理多语言用户的语音堆栈，无需单独部署或供应商分散。所有语言都具有相同的专用端点、可观察性和可靠性。

## **Together AI for TTS 模型的生产基础设施**

Together AI 提供跨不同性能和成本概况的 TTS 模型：

- 开源，例如 Orpheus 和 Kokoro：经济高效、大批量部署
- 企业专有软件，如 Rime Arcana v2：确定性发音、40 多种语音，经过 1B 以上对话训练
- MiniMax Speech 2.6 Turbo等精英自然性：人工分析竞技场排名第一，40多种语言，自动情绪控制，10秒语音克隆

MiniMax Speech 2.6 Turbo 仅在 Together AI 专用端点上运行 - 独立的 GPU 容量，具有 99.9% 的正常运行时间 SLA，支持超过 100 万开发人员的生产工作负载。

基础设施

- ✔ 具有隔离工作负载的专用 GPU 容量
- ✔ 99.9% 正常运行时间 SLA
- ✔ SOC 2 Type II、HIPAA 就绪、PCI 兼容
- ✔ 全球数据中心
- ✔ WebSocket 流支持
- ✔ 零数据保留和完全的数据所有权和控制

开发者经验

- ✔ 与 LLM 和 STT 端点相同的 SDK 和身份验证
- ✔ Arcana v2 和 Mist v2 的统一发音 API
- ✔ 整个语音管道的单一可观测性和日志记录表面
- ✔ 通过配置选择和更换型号
- ✔ 提供专业的语音克隆服务
- ✔ 大容量工作流程的批处理

## **开始使用**

→ [尝试模型](https://www.together.ai/models/minimax-speech-2-6-turbo)现在

→ 阅读 [TTS文档](https://docs.together.ai/docs/text-to-speech?_gl=1*151lwcn*_gcl_au*MjY2Mjg 2NjAwLjE3NjU1NjExMzIuMTgwNTIyNTk0OC4xNzY2MDg3MDg4LjE3NjYwODcxMDE.*_ga*NDQxNTg3OTU3LjE3NDg 1NDkxNjA.*_ga_BS43X21GZ2*czE3NjY0MzczNTckbzk4JGcxJHQxNzY2NDM5NTU2JGo1NCRsMCRoMTUxNTkyODM2 Mw..*_ga_BBHKJ5V8S0*czE3NjY0MzczNTckbzk4JGcxJHQxNzY2NDM5NTU2JGo1NCRsMCRoMTY1MDE2MjgzMg..)

→ [联系销售](https://www.together.ai/contact-sales)用于企业专用端点部署和批量定价

## 相关文章
