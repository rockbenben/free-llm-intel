---
vendor: aws_bedrock
title: Building intelligent AI voice agents with Pipecat and Amazon Bedrock – Part 1
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/building-intelligent-ai-voice-agents-with-pipecat-and-amazon-bedrock-part-1
date: 2025-06-09
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 3b2f2270cc9a
---

# 使用 Pipecat 与 Amazon Bedrock 构建智能 AI 语音 agent – 第 1 部分

Voice AI 正在改变我们与技术交互的方式，让对话式交互比以往任何时候都更自然、更直观。与此同时，AI agent 也日益成熟，能够理解复杂查询并代表我们自主采取行动。随着这两股趋势汇聚，智能 AI 语音 agent 应运而生——它们可以像人一样对话，同时执行各种各样的任务。

在本系列文章中，你将学习如何使用 [Pipecat](https://github.com/pipecat-ai/pipecat)（一个用于语音和多模态对话式 AI agent 的开源框架）配合 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 上的基础模型，构建智能 AI 语音 agent。文章包含高层参考架构、最佳实践和[代码示例](https://github.com/aws-samples/building-intelligent-voice-ai-agents-with-pipecat-and-amazon-bedrock)，为你的实现提供指导。

## 构建 AI 语音 agent 的方法

构建对话式 AI agent 有两种常见方法：

- **使用级联模型：** 本文（第 1 部分）将介绍级联模型方法，并深入剖析对话式 AI agent 的各个组件。采用该方法时，语音输入会依次经过一系列架构组件，然后才把语音回复发送给用户。这种方法有时也被称为 pipeline 或组件模型语音架构。
- **在单一架构中使用语音到语音基础模型：** 在[第 2 部分](https://aws.amazon.com/blogs/machine-learning/building-intelligent-ai-voice-agents-with-pipecat-and-amazon-bedrock-part-2/)中，你将了解 [Amazon Nova Sonic](https://aws.amazon.com/blogs/aws/introducing-amazon-nova-sonic-human-like-voice-conversations-for-generative-ai-applications/) 这一先进的统一语音到语音基础模型，如何通过在单一架构中结合语音理解与生成，实现实时、拟人的语音对话。

## 常见用例

AI 语音 agent 可以处理多种用例，包括但不限于：

- **客户支持：** AI 语音 agent 可以 7×24 小时处理客户咨询，即时给出回复，并在必要时把复杂问题转交人工客服。
- **外呼：** AI agent 可以开展个性化外联活动，通过自然对话安排预约或跟进潜在客户。
- **虚拟助手：** Voice AI 可以驱动个人助手，帮助用户管理任务、回答问题。

## 架构：使用级联模型构建 AI 语音 agent

要用级联模型方法构建 agentic 语音 AI 应用，你需要编排多个架构组件，其中涉及多个机器学习和基础模型。

![参考架构 - Pipecat](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/09/Reference-Architecture-Pipecat.png)

*图 1：使用 Pipecat 的 Voice AI Agent 架构总览*

这些组件包括：

**WebRTC Transport：** 在客户端设备与应用服务器之间实现实时音频流传输。

**Voice Activity Detection (VAD)：** 使用 [Silero VAD](https://github.com/snakers4/silero-vad) 检测语音，支持配置语音开始和结束时间，并具备噪声抑制能力，可去除背景噪声、提升音频质量。

**Automatic Speech Recognition (ASR)：** 使用 [Amazon Transcribe](https://aws.amazon.com/transcribe/) 进行准确、实时的语音转文本。

**Natural Language Understanding (NLU)：** 借助 [latency-optimized inference](https://aws.amazon.com/blogs/machine-learning/optimizing-ai-responsiveness-a-practical-guide-to-amazon-bedrock-latency-optimized-inference/) 在 Bedrock 上结合 [Amazon Nova Pro](http://Amazon Nova Pro) 等模型解读用户意图，并可选择启用 [prompt caching](https://aws.amazon.com/bedrock/prompt-caching/)，以优化检索增强生成（RAG）用例中的速度与成本效率。

**Tools Execution and API Integration：** 通过 Pipecat Flows 集成后端服务与数据源，并利用基础模型的 [tool use](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html) 能力，为 RAG 执行操作或检索信息。

**Natural Language Generation (NLG)：** 使用 Bedrock 上的 [Amazon Nova Pro](https://aws.amazon.com/ai/generative-ai/nova/) 生成连贯回复，在质量与延迟之间取得恰当平衡。

**Text-to-Speech (TTS)：** 使用 [Amazon Polly](https://aws.amazon.com/polly/) 的[生成式语音](https://docs.aws.amazon.com/polly/latest/dg/generative-voices.html)把文本回复转换为逼真的语音。

**Orchestration Framework：** Pipecat 负责编排这些组件，为实时、多模态 AI agent 应用提供模块化的 Python 框架。

## 构建高效 AI 语音 agent 的最佳实践

开发响应灵敏的 AI 语音 agent 需要关注延迟与效率。尽管最佳实践仍在不断演进，仍可考虑以下实现策略，以获得自然、拟人的交互体验：

**尽量缩短对话延迟：** 为 [Amazon Nova Pro](https://aws.amazon.com/ai/generative-ai/nova/) 等基础模型（FM）使用 [latency-optimized inference](https://docs.aws.amazon.com/bedrock/latest/userguide/latency-optimized-inference.html)，以保持自然的对话节奏。

**选择高效的基础模型：** 优先选用更小、更快的基础模型（FM），在保持质量的同时快速给出响应。

**实施 prompt caching：** 利用 [prompt caching](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html) 同时优化速度与成本效率，尤其是在需要知识检索的复杂场景中。

**部署 text-to-speech（TTS）填充语：** 在耗时操作前使用自然的填充语（例如“我帮你查一下”），在系统发起工具调用或向基础模型发起长时间调用时维持用户的参与感。

**构建稳健的音频输入 pipeline：** 集成降噪等组件，保证音频质量清晰，从而获得更好的语音识别结果。

**从简单开始并迭代：** 先实现基础对话流程，再逐步演进到能处理多种用例的复杂 agentic 系统。

**区域可用性：** 低延迟和 prompt caching 特性可能仅在部分区域提供。请权衡这些高级能力与选择地理上更接近最终用户的区域之间的取舍。

## 示例实现：几分钟内构建你自己的 AI 语音 agent

本文提供了一个 [Github 上的示例应用](https://github.com/aws-samples/building-intelligent-voice-ai-agents-with-pipecat-and-amazon-bedrock)，用于演示文中讨论的概念。它使用 [Pipecat](https://github.com/pipecat-ai/pipecat) 及其配套的状态管理框架 [Pipecat Flows](https://github.com/pipecat-ai/pipecat-flows)，结合 Amazon Bedrock，并借助 [Daily](https://daily.co/) 提供的 Web Real-time Communication（WebRTC）能力，构建出一个几分钟内就能试用的可用语音 agent。

### 先决条件

要搭建示例应用，你应具备以下先决条件：

- Python 3.10+
- 一个具备 Amazon Bedrock、Amazon Transcribe 和 Amazon Polly 相应 Identity and Access Management（IAM）权限的 AWS 账户
- [访问](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html#:~:text=To%20request%20access%20to%20a,want%20to%20add%20access%20to.) Amazon Bedrock 上的基础模型
- [访问](https://docs.daily.co/reference/rest-api) Daily 的 API key
- 支持 WebRTC 的现代浏览器（例如 Google Chrome 或 Mozilla Firefox）

## 实现步骤

完成先决条件后，就可以开始搭建你的示例语音 agent：

- 克隆仓库：`git clone https://github.com/aws-samples/build-intelligent-ai-voice-agents-with-pipecat-and-amazon-bedrock cd build-intelligent-ai-voice-agents-with-pipecat-and-amazon-bedrock/part-1 `
- 搭建环境：`cd server python3 -m venv venv source venv/bin/activate # Windows: venv\Scripts\activate pip install -r requirements.txt`
- 在`.env`中配置 API key：`DAILY_API_KEY=your_daily_api_key AWS_ACCESS_KEY_ID=your_aws_access_key_id AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key AWS_REGION=your_aws_region`
- 启动服务器：`python server.py`
- 在浏览器中访问 `http://localhost:7860` 并授予麦克风权限
- 开始与你的 AI 语音 agent 对话

### 定制你的语音 AI agent

要定制，可以从以下方面入手：

- 修改 `flow.py` 以更改对话逻辑
- 在` bot.py`中调整模型选择，以满足你对延迟和质量的要求

如需了解更多，请参阅 Pipecat Flows 的[文档](https://docs.pipecat.ai/guides/features/pipecat-flows)，并查看我们在 Github 上代码示例的 [README](https://github.com/aws-samples/building-intelligent-voice-ai-agents-with-pipecat-and-amazon-bedrock)。

### 清理

上述说明用于在本地环境搭建应用。本地应用会通过 AWS IAM 和 API 凭证使用 AWS 服务与 Daily。出于安全考虑并避免意外费用，完成后请删除这些凭证，确保它们不再能被访问。

## 加速语音 AI 落地

为加速 AI 语音 agent 的落地，[AWS Generative AI Innovation Center（GAIIC）](https://aws.amazon.com/ai/generative-ai/innovation-center/)与客户合作，识别高价值用例并开发可快速投入生产的概念验证（PoC）方案。

### 客户证言：InDebted

[InDebted](https://www.indebted.co/)是一家正在改造消费债务行业的全球金融科技公司，它与 AWS 合作开发其语音 AI 原型。

> “我们相信，AI 驱动的语音 agent 是增强金融服务客户互动中人情味的关键机遇。通过将 AI 语音技术融入我们的运营，我们的目标是让客户更快速、更直观地获得适应其需求的客服支持，同时提升客户体验质量与联系我们中心（contact centre）的运营表现” 
>         InDebted 首席数据官 Mike Zhou 表示。

通过与 AWS 合作并利用 Amazon Bedrock，InDebted 这样的组织可以打造安全、自适应的语音 AI 体验，既满足监管标准，又能在最棘手的金融对话中带来真实、以人为本的效果。

## 结语

借助 [Pipecat](https://github.com/pipecat-ai/pipecat) 等开源框架，以及 Amazon Bedrock 上支持[延迟优化推理](https://aws.amazon.com/blogs/machine-learning/optimizing-ai-responsiveness-a-practical-guide-to-amazon-bedrock-latency-optimized-inference/)和 [prompt caching](https://aws.amazon.com/bedrock/prompt-caching/) 的强大基础模型，如今构建智能 AI 语音 agent 比以往任何时候都更容易。

本文中，你了解了构建 AI 语音 agent 的两种常见方法，并深入探讨了级联模型方法及其关键组件。这些核心组件协同工作，构成一个能够自然理解、处理并回应人类语音的智能系统。借助生成式 AI 的这些快速进展，你可以打造成熟、响应灵敏的语音 agent，为你的用户和客户带来真正的价值。

要开始你自己的语音 AI 项目，可以试用我们在 [Github 上的代码示例](https://github.com/aws-samples/building-intelligent-voice-ai-agents-with-pipecat-and-amazon-bedrock)，或联系你的 AWS 客户团队，探讨与 [AWS Generative AI Innovation Center（GAIIC）](https://aws.amazon.com/ai/generative-ai/innovation-center/)合作。

你也可以在[第 2 部分](https://aws.amazon.com/blogs/machine-learning/building-intelligent-ai-voice-agents-with-pipecat-and-amazon-bedrock-part-2/)中了解如何使用统一的语音到语音基础模型 [Amazon Nova Sonic](https://aws.amazon.com/blogs/aws/introducing-amazon-nova-sonic-human-like-voice-conversations-for-generative-ai-applications/) 构建 AI 语音 agent。

### 关于作者

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/09/adxthya.jpeg)**[Adithya Suresh](https://www.linkedin.com/in/adithyaxx/)** 是 AWS Generative AI Innovation Center 的 Deep Learning Architect，他与技术和业务团队合作，构建创新型生成式 AI 方案以应对现实挑战。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/02/05/wirjo.jpeg)**[Daniel Wirjo](https://www.linkedin.com/in/wirjo/)** 是 AWS 的 Solutions Architect，专注于金融科技和 SaaS 初创公司。作为前初创公司 CTO，他喜欢与创始人和工程负责人协作，在 AWS 上推动增长与创新。工作之外，Daniel 喜欢端着一杯咖啡散步、亲近自然，并学习新想法。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/28/karan.jpg)**[Karan Singh](https://www.linkedin.com/in/karan-singh-a8aa7518/)** 是 AWS 的 Generative AI Specialist，他与顶级第三方基础模型和 agentic 框架提供商合作，制定并执行联合上市策略，帮助客户有效部署和扩展方案，以解决企业生成式 AI 挑战。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2023/10/07/liuxuefeng.jpg)**[Xuefeng Liu](https://www.linkedin.com/in/xuefeng-liu-aa915362/)** 领导 AWS Generative AI Innovation Center 在亚太地区的科学团队。他的团队与 AWS 客户合作开展生成式 AI 项目，目标是加速客户对生成式 AI 的采用。
