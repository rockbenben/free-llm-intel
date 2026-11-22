---
vendor: aws_bedrock
title: How Loka Built a Natural, Low-Latency Voice Agent with Amazon Nova 2 Sonic
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/how-loka-built-a-natural-low-latency-voice-agent-with-amazon-nova-2-sonic
date: 2026-06-24
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: b87182f4641d
---

# Loka 如何用 Amazon Nova 2 Sonic 构建自然、低延迟的语音 agent

[Loka](https://www.loka.com/) 通过用 [Amazon Nova 2 Sonic](https://nova.amazon.com/sonic) 构建对话式 AI agent，改造了客户语音交互，让客户始终沉浸在自然、响应及时的体验中。他们基于 AWS 的解决方案在 [Big Bench Audio](https://huggingface.co/datasets/ArtificialAnalysis/big_bench_audio) 上取得很高的语音推理准确率，同时相比传统语音 AI pipeline 显著降低成本并加快响应速度。本文展示 Loka 为化解一个普遍困扰所采用的架构与方法：机械、迟缓的语音助手会让客户挂断电话，损害品牌声誉并推高支持成本。

## 传统语音助手为何不够用

传统语音助手遵循一个三步流程，根本问题正源于此。首先，它们用语音转文本（Speech-to-Text）系统把你的话转成文字。接着，它们用大语言模型（LLM）处理这段文字。最后，它们用文本转语音（Text-to-Speech）技术把文字回复再转回语音。这个 pipeline 在每一步都会引入累积的延迟。结果往往是你要等上 3 到 5 秒才能听到回复。这种延迟破坏了自然对话的感觉，也让打断助手或纠正助手显得笨拙而令人沮丧。

设想一个汽车经销店的真实场景。客户打来电话说：*“我在找你们广告里那辆 SUV，但不是混动那款。我只能下午 5 点之后过来。”* 助手需要同时解析多条信息。它必须理解意图、否定和日程约束。传统系统在这种复杂性面前力不从心，因为它们在转换过程中丢失了关键信息。当语音变成文本时，语调、犹豫和紧迫感都消失了。经销店这个场景让这些局限格外明显。客户打电话时期待得到即时、有用的回应。在销售对话中，五秒钟的停顿漫长得像永恒。更糟的是，如果助手理解错了还需要澄清，延迟就会叠加。对话变得冗长乏味，而不是有所帮助。

除了技术延迟，还有经济问题。服务数千个门店需要严格的成本控制。传统的实时语音系统在规模化时成本会高到难以承受，尤其是在处理持续音频流时。糟糕的体验加上高昂的成本限制了语音 AI 的采用。企业需要一个更好的方案。

## 原生语音到语音模型

AI 的近期进展开启了一种根本不同的方法。开发者现在可以把音频流直接发送给语音到语音（speech-to-speech）模型，由这些模型作为一个统一系统处理理解、推理与生成。通过端到端处理音频，这些模型能够捕捉传统纯文本 pipeline 所遗漏的语调、情绪和细微线索。

为验证这一方法，严格的测试必不可少。我们使用了 [Big Bench Audio](https://huggingface.co/datasets/ArtificialAnalysis/big_bench_audio)，这是一个衡量对语音输入进行推理能力的基准。[Amazon Nova 2 Sonic](https://nova.amazon.com/sonic) 取得 87.0 的语音推理得分，优于得分 71.0 的 [Gemini 2.5 Flash Native Audio (Live API)](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash-live-api)，也超过了 [GPT Realtime](https://developers.openai.com/api/docs/models/gpt-realtime) 的 83.0。这些得分证实，原生音频处理不会为了速度而牺牲智能。该模型能够处理真实经销店场景中复杂的多部分请求。

![Big Bench Audio 基准上各模型语音推理得分对比](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/06/02/ML-20376-1.png)

*图 1 – 语音推理得分对比 – Big Bench Audio*

对生产系统而言，仅有推理能力还不够。延迟决定了对话是自然还是机械。Nova 2 Sonic 的首字节音频时间（Time to First Audio）为 1.39 秒。这样的响应时间允许自然的“打断”（barge-in）行为。当用户打断对话时，语音 agent 能自然地回应。这种体验与人类对话模式相符。

![Big Bench Audio 基准上各模型首字节音频时间对比](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/06/02/ML-20376-2.png)

*图 2 – 首字节音频时间对比 – Big Bench Audio*

成本效率也有所提升。输入音频的 [Nova 2 Sonic 费用约为每小时 $0.27](https://aws.amazon.com/nova/pricing/)（基于发布时的定价）。这低于可比的实时模型和传统方法。

![Big Bench Audio 基准上各模型每小时音频成本对比](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/06/02/ML-20376-3.png)

*图 3 – 每小时音频成本对比 – Big Bench Audio*

为了在延迟与成本之外衡量质量，我们需要一套结构化评估。我们构建了使用 LLM 作为评判者（judge）的自动化 pipeline。每段对话都按五个维度以 1–5 分制打分。响应恰当性（Response Appropriateness）衡量回复是否相关且符合上下文。意图理解（Intent Understanding）评估 agent 是否把握了用户的真实目标。完整性（Completeness）追踪是否提供了必需的信息或操作。对话自然度（Conversational Naturalness）衡量流畅性、轮次衔接、语调以及拟人程度。

将 Amazon Nova Sonic 与 Amazon Nova 2 Sonic 对比，可以看到明显的进步。响应恰当性从 2.5 提升到 2.9。意图理解从 2.9 上升到 3.0。最显著的是完整性从 1.8 跃升到 2.5，这意味着 agent 完成复杂任务的可能性大大提高。对话自然度从 2.5 提升到 2.8。总体得分从 2.4 提升到 2.7。这些提升直接转化为经销店更好的客户结果。

| **指标（1–5 分制）** | **Nova Sonic（基线）** | **Nova 2 Sonic** | **变化** |
| --- | --- | --- | --- |
| **响应恰当性** | 2.5 | **2.9** | **+0.4** |
| **意图理解** | 2.9 | **3.0** | **+0.1** |
| **完整性** | 1.8 | **2.5** | **+0.7** |
| **对话自然度** | 2.5 | **2.8** | **+0.3** |
| **总体评判得分** | 2.4 | **2.7** | **+0.3** |

*表 1 – 语音到语音模型在五个维度上的指标对比*

## 对话式 AI agent 的工程实践

有了强大的基础模型，下一个挑战是优化。我们像对待代码一样对待 prompt，基于实测表现反复迭代。基线 Nova 2 Sonic 配置的总体得分为 2.7。第一次 prompt 优化后，得分上升到 3.1。第二轮迭代达到 5.0 分制下的 3.8。这一提升来自更好的轮次纪律和重复控制。agent 学会了何时说话、何时倾听，以及何时提出澄清性问题。

| **配置** | **响应恰当性** | **意图理解** | **完整性** | **错误恢复** | **对话自然度** | **总体评判得分** |
| --- | --- | --- | --- | --- | --- | --- |
| **Amazon Nova 2 Sonic（基线）** | 2.9 | 3.0 | 2.5 | 2.6 | 2.8 | 2.7 |
| **Amazon Nova 2 Sonic（Prompt v1）** | 3.2 | 3.3 | 3.0 | 2.8 | 3.9 | 3.1 |
| **Amazon Nova 2 Sonic（Prompt v2）** | **3.7** | **3.9** | **3.9** | **3.8** | **4.1** | **3.8** |

*表 2 – prompt 增强后语音到语音模型在五个维度上的指标对比*

团队从多个方面增强了基线 prompt，把它演进为两个 prompt 模板。他们用 `{assistant_name}` 和 `{dealership_address}` 这样的模板化变量替换了硬编码的经销店细节。这一改动让 prompt 可以复用于任何经销店。

团队把格式从编号列表改为在标注清晰的标题下使用要点列表。“Tool Usage Rules”、“Error Recovery”和“Conversation Endings”这样的标题为模型划出了更清晰的行为边界。这种结构减少了不同主题之间的指令串扰。

团队在整份 prompt 中加入了具体的行为示例。这些示例明确展示了如何在不复述来电者原话的情况下作出确认。他们还引入了一份回复前检查清单，提示模型在每次回复前自我审查。

[Amazon Bedrock Prompt Management](https://aws.amazon.com/bedrock/prompt-management/) 顺理成章地成为这整个生命周期的归属。它让团队可以用唯一的 Amazon Resource Name（ARN）存储每个模板版本。他们可以在不触碰应用代码的情况下把改动从草稿提升到生产。

当有新经销店接入时，其专属变量会在运行时通过 [Amazon Bedrock](https://aws.amazon.com/bedrock/) API 注入。这意味着同一份核心 prompt 服务于每个客户，同时保持完全可定制。

团队加入了 [AWS Identity and Access Management（AWS IAM）](https://aws.amazon.com/iam/) 访问控制，限制谁可以编写、批准或部署 prompt 改动。这为此前非正式的编辑流程带来了恰当的治理层。

这种方法把 prompt 工程从一次性任务转变为可重复、可审计的工作流。随着经销店数量和用例增长，该工作流也能随之扩展。

真实环境测试需要能对应实际经销店来电的边缘场景。我们测试了愤怒的客户、忙碌的家长、健谈的客户、困惑的客户以及年长来电者。

“忙碌的家长”场景在五个维度上都得到 5.0。agent 完美地处理了打断、背景噪声和时间压力。“愤怒的客户”用例总体得分 4.5。agent 保持冷静、共情，并聚焦于解决方案。“困惑的客户”场景同样得分 4.5。agent 耐心澄清，听起来并不居高临下。

| **对话示例** | **响应恰当性** | **意图理解** | **完整性** | **错误恢复** | **对话自然度** | **总体评判得分** |
| --- | --- | --- | --- | --- | --- | --- |
| **愤怒的客户** | 4.5 | 4.5 | 4.0 | 4.5 | 4.5 | 4.5 |
| **忙碌的家长客户** | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 | 5.0 |
| **健谈的客户** | 3.5 | 3.0 | 2.5 | 2.0 | 4.0 | 3.0 |
| **困惑的客户** | 4.5 | 4.5 | 4.5 | 5.0 | 4.5 | 4.5 |
| **年长的客户** | 3.5 | 3.0 | 2.5 | 2.0 | 4.0 | 3.0 |
| **平均** | **4.2** | **4.0** | **3.7** | **3.7** | **4.4** | **4.0** |

*表 3 – 基于客户画像的语音到语音模型评估*

有两个场景揭示了仍然存在的改进空间。“健谈的客户”和“年长的客户”两个用例总体得分都是 3.0。当用户给出冗长、漫无边际的输入时，语音 agent 在结构把握上显得吃力。在这些情况下，完整性得分降到 2.5，错误恢复降到 2.0。这些结果明确指出了未来 prompt 工程的方向。不过，边缘场景平均 4.0 的得分仍表明它已具备很强的真实环境就绪度。

构建合适的架构对生产部署很重要。我们设计了一个无服务器、事件驱动的系统，使用 [LiveKit](https://livekit.io/) 作为传输层。LiveKit 抽象掉了面向 Web 客户端的 [WebRTC](https://webrtc.org/) 和面向电话呼叫的 [Session Initiation Protocol（SIP）](https://www.sipforum.org/technology/sip-technology/) 的复杂性。这让工程团队可以完全专注于 agent 逻辑。

![对话式 AI 助手解决方案架构，展示 LiveKit、AWS Fargate、Amazon Bedrock 及配套服务](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/06/02/ML-20376-4.png)

*图 4 – 对话式 AI 助手 – 解决方案架构*

语音 agent 通过基于 Python 函数的工具与经销店业务系统集成，这些工具代表助手在对话过程中可以执行的操作。常见的工具有库存查询、预约登记和客户数据查询。这些工具充当 Amazon Nova 2 Sonic 与后端服务之间的集成层。模型决定何时应使用某个工具，Python 函数则执行对应的 GraphQL 查询或变更，并把结构化数据返回给 agent。

[AWS Fargate](https://aws.amazon.com/fargate/) 提供计算层。我们把 LiveKit Agents 容器化部署在 [Amazon Elastic Container Service（Amazon ECS）](https://aws.amazon.com/pm/ecs) 上。这样 agent worker 与媒体服务器可以独立伸缩。资源可以在经销店高峰时段动态优化。[Amazon Relational Database Service（Amazon RDS）](https://aws.amazon.com/rds/) 被用作结构化应用数据的持久化关系型存储，包括经销店配置、对话历史和客户记录。

实时语音 agent 无法容忍数据库延迟。[Amazon ElastiCache](https://aws.amazon.com/elasticache/) 用于处理房间管理以及跨分布式任务的临时会话协调。Amazon Bedrock 提供了对 Nova 2 Sonic 模型的直接访问。

浏览器客户端使用 [WebRTC](https://webrtc.org/)（Web Real-Time Communications）连接，这是一个用于点对点音频、视频与数据传输的开源框架。传统电话呼叫通过经由 Network Load Balancer 路由的 SIP Trunk 接入。这为媒体数据包提供了 TCP/UDP 吞吐能力。

可观测性来自在 AWS 上自托管的 [Langfuse](https://langfuse.com/)。它追踪每一个 agent 决策和工具调用。这些数据会被回馈到评估 pipeline 中，用于持续改进。

## 演示

下面的视频演示了该功能。

## 对话式 AI 的新标准

从基于文本的聊天机器人转向实时语音 agent，不只是界面层面的变化。它需要根本不同的基础设施与思维方式。Nova 2 Sonic 同时满足三项关键的工程要求。第一，它在没有中间文本转换的情况下提供很强的推理能力。第二，它提供低延迟，让自然的、类似人类的打断成为可能。第三，它对数千个门店而言具备成本效益，从而具备生产可行性。

对汽车经销店而言，这项技术已经在生产中创造营收。客户打来电话时能得到即时、有用的回应。复杂的请求可以在一次对话中顺畅处理完。预约能被正确安排，而不需要令人沮丧地来回确认。

其影响远远超出汽车销售领域。任何需要实时、智能语音交互的行业都能受益。想象一个旅行 agent，通过自然对话帮你规划整个假期。设想一位教育辅导老师，能适应你的说话风格和学习节奏。再想想处理复杂保险与排期问题的医疗健康预约系统。

语音到语音 AI 已经达到生产就绪。开始在你自己的 AWS 环境中试用 Nova 2 Sonic 吧。构建原型、测试边缘场景，探索你的业务可以实现什么。

本文是 AWS 与 Loka 合作的成果，后者专长于构建生产就绪的 AI 解决方案。Loka 的团队已经解决了架构、评估和优化方面的难题。他们在汽车经销店领域的经验可以直接迁移到其他行业。

语音到语音 AI 仍处于早期阶段。最好的应用还没有被发明出来。你的行业知识加上这项技术，可能创造出突破性的解决方案。今天就以 [Nova 2 Sonic](https://nova.amazon.com/sonic) 和 [Loka](https://partners.amazonaws.com/partners/0010h00001hfV65AAE/Loka) 开启你的旅程，改变客户与你的业务对话的体验。

## 关于作者
