---
vendor: aws_bedrock
title: New in Amazon Bedrock AgentCore: Build agents with broader knowledge and continuous learning
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/new-in-amazon-bedrock-agentcore-build-agents-with-broader-knowledge-and-continuous-learning
date: 2026-06-17
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 8a3feccbe604
---

# Amazon Bedrock AgentCore 新功能：构建拥有更广知识与持续学习能力的 agent

驱动今天这些 agent 的模型能力已经非常出色。它们能跨复杂问题进行推理、规划多步工作流，并生成有细腻差别的回答。但大多数 agent 的实际表现远低于这一潜力。缺的不是智能，而是对正确上下文与反馈的访问。

一个负责回答公司退款政策问题的客服 agent，如果够不到 SharePoint 里存放该政策的那份文档，就帮不上忙。一个撰写市场简报的研究 agent，如果拿不到训练数据之外的当前信息，就只能给出不完整的图景。一个理财顾问 agent，如果所需的实时市场数据位于它无法穿透的付费墙之后，就只能返回次优建议。而在这一切之上，大多数团队在 agent 上线之后，都没有任何系统化的方式知道它们是变好了还是变差了。

一个能力强的模型只是起点。让 agent 在生产环境中真正发挥作用的，是对完成整件事所需一切的访问：正确的知识、用于行动的资源，以及持续改进的反馈回路。

今天，我们在 [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) 上推出新能力——这个平台用于构建、连接与优化 agent。在本文中，我们介绍这些能力如何逐一弥合上述差距：把 agent 连接到组织内知识、web 知识与付费知识；帮助团队发现在生产环境中出错的地方并修复它；以及在 agent 能力增长的同时执行可扩展的控制。合在一起，它们帮助你更快地构建更有能力的 agent、用可扩展的控制治理它们，并持续改进它们。

# 知道更多、触达更广的 agent

我们让 AgentCore 上的 agent 原生访问三个层次的知识，每一层都在拓宽你的 agent 能触及与能完成的范围。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/06/16/knowledge-layers.png)

**组织知识层：Amazon Bedrock Managed Knowledge Base**

你最有价值的信息散落在 SharePoint、Google Drive、Confluence、S3 与内部 wiki 中。要让 agent 能用上这些信息，传统上需要构建自定义的数据接入 pipeline、调优检索，并长期维护数据的新鲜度。在你的 agent 能回答一个关于你自己业务的基本问题之前，这就是数月的工程投入。

[Bedrock Managed Knowledge Base](https://aws.amazon.com/blogs/aws/introducing-amazon-bedrock-managed-knowledge-base-for-faster-more-accurate-enterprise-ai-applications/) 现已在 AgentCore 上提供，替代了这些工作。你连接自己的非结构化数据源，其余由 AgentCore 处理。我们负责管理向量存储、检索时使用的 embedding 与重排序模型，以及限流这类可扩展性问题，好让你的团队专注于构建 agent，而不是运维 pipeline。它的核心是一个 agentic 检索器，远超传统的 RAG。它不是把查询匹配到最接近的若干片段，而是跨你的知识库规划查询、跨文档连接相关概念、评估中间结果，并在作答前重新排序。对于同时横跨多个主题的复杂多段查询，agentic 检索呈现出明显更广、更完整的覆盖，胜过基础检索。你的 agent 从「我无权访问那个」变成给出一个从你真实业务知识中提炼的答案，而且没有 pipeline 要建，也没有检索要调。

**世界知识层：Web Search on AgentCore**

内部知识存在空白。法规在变、市场在变、竞争对手不断推出新产品。要做好工作，你的 agent 需要理解组织之外的世界正在发生什么，用于研究、事实核查、客户服务与市场情报。

今天，我们为构建 AI agent 的开发者推出 [Web Search](https://aws.amazon.com/blogs/aws/announcing-web-search-on-amazon-bedrock-agentcore-ground-your-ai-agents-in-current-accurate-web-knowledge/)——一个新工具。它从 web 提供信息，同时让数据留在客户受保护的 AWS 环境中。Web Search 构建在支撑 Alexa+、AWS Quick 与 Kiro 的同一套 Amazon 搜索基础设施之上，针对 agentic 检索做了优化，返回高价值的摘录，让每个 token 都承载更高的智能。它还采用多来源接地的方式，把公开 web 信息与 Amazon 的专有知识图谱结合起来。该图谱补充了结构化实体数据、经核实的事实，以及股价、体育比分这类实时信息。AgentCore 上的 Web Search 让你的查询留在你的 AWS 安全与合规边界之内，无需引入额外供应商，也就没有随之而来的编排、认证与计费流程。无论你是在构建交叉比对公开来源的研究 agent、监控监管与政策更新的合规 agent，还是用当前信息为模型回答做接地，你的 agent 现在都能像查询内部知识一样，对实时 web 进行推理。

> “在 Sony，我们正在 AgentCore 上构建企业级 AI agent 平台，让各业务部门的团队能够开发、共享与复用 AI agent——从知识助手到工作流自动化 agent——每一个都针对自身需求定制。我们的企业知识分散在 SharePoint、Confluence 与 Amazon S3 等仓库中，并包含 PDF、演示文稿以及带图表和表格的电子表格这类复杂文档。现在 Bedrock Managed Knowledge Base 与 Web Search 已在 AgentCore 中可用，我们可以用一致的治理模型为 agent 配备高级检索与实时 web 接地，而无需从零构建这些能力。这加速了我们的愿景：以 AI 为催化剂，大规模改变人们的工作方式。”
>         Masahiro Oba，Sony Group Corporation 高级总经理

**付费知识层：AgentCore payments 与 AWS WAF AI 流量变现**

最好的信息并不总是免费的。金融市场行情源、授权研究、专有数据集、付费 API。如果你的 agent 无法访问付费资源，它就会返回次优答案，而用户永远不知道错过了什么。

访问付费内容包含两半：agent 需要有支付的方式，供应商需要有收款的方式。上个月以预览版发布的 AgentCore payments 负责 agent 这一侧，让 agent 发现付费服务与内容、访问它们，并在自己的执行循环内完成支付。现已正式可用的 [WAF AI 流量变现](https://aws.amazon.com/blogs/aws/aws-waf-adds-ai-traffic-monetization-capability-to-help-content-owners-charge-ai-bots-for-content-access/) 负责供应商这一侧，让内容所有者可以控制 agent 的访问：拦截它、允许它，或者从中获得付费。由于这两项能力运行在同一平台上，使用 WAF 的供应商会自动识别在 AgentCore 上验证过的 agent。结果是一条受信任的通道：对已验证的 agent 摩擦更低，对供应商则获得补偿。合在一起，这些能力为 agent 经济的两侧搭好了基础设施，使 agent 能够触及一切，而不只是碰巧免费的那些。

# 从每一次交互中学习的 agent

让 agent 更好地访问知识只是等式的一半。你还需要知道 agent 是否真的在达成目标，并在它没有达成时抓住它。

这比听起来更难。最危险的 agent 失败并不是抛出错误的那些，而是在仪表盘上看起来一切正常的那些：一个 agent 确认了一笔它从未执行的订单修改，另一个在 API 超时时编造了产品可用性，还有一个跳过了审批步骤，而仪表盘显示 99% 的成功率。这些失败不产生任何错误信号。它们通过几周后客户的投诉浮现，往往是在数千个会话已经受到影响之后。而且即便团队知道有问题，修复基本靠猜。你微调 prompt、改动工具描述、调整编排逻辑，然后指望它有用，却没有任何结构化的方式知道这次改动是真的改善了，还是悄悄弄坏了别的东西。

今天，我们宣布 AgentCore 中新的优化能力，把生产 trace 转化为持续改进。它们合在一起形成一个回路：理解你的 agent 实际在做什么、生成以数据为依据的修复、在发布前验证这些修复，并证明它们确实有效。

**理解你的 agent 在做什么：**该能力今天以预览版提供，AgentCore 能在数百个会话中给出丰富的失败、意图与轨迹洞察，浮现出任何仪表盘或逐条查看 trace 都无法揭示的模式。失败洞察会发现反复出现的失败模式，包括那些不产生错误信号的静默行为失败，详细解释每一种的根因，并按波及范围排序，让你一眼看出哪些问题正在伤害最多用户，从而优先修复它们。意图洞察按用户实际想做什么来聚类请求，让你看到 agent 被使用的真实形态。轨迹洞察把 agent 完成任务所走的路径分组，让你发现常见模式与离群值。你可以用每日或每周报告开启持续监控，也可以在部署之后或投诉激增之后运行一次针对性调查，几分钟内就有结果。

**有信心地修复：**一旦你知道该改什么，今天正式可用的 recommendations 与 A/B 测试会帮你行动。Recommendations 分析你的 trace 与评估输出，针对你的 system prompt 与工具描述提出具体改进建议，并且以你的 agent 实际行为为依据。批量评估会用你定义的测试数据集检验这些建议，并报告汇总分数，让你在改动到达生产之前抓住回归。A/B 测试通过切分实时生产流量，在 agent 版本之间做受控对比，在你最终采纳之前给出确凿证据，证明某项改动在生产条件下确实有效。这一切都不论你的 agent 运行在哪里：AgentCore 的 runtime、AWS Lambda、Amazon EKS，或非 AWS 环境。

当持续改进被内置进平台，而不是事后拼凑出来时，它就是这个样子。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/06/16/agentcore-optimization-loop.png)

> “在 FUJISOFT，我们正在构建 AI agent，以加速软件开发与运维。我们的框架 Character Capsule 把 agent 角色、skills 与流程打包成可复用的胶囊，它们可以运行在 Copilot 与 Kiro 这类本地编码工具上，也可以扩展到 AgentCore 上的多 agent 编排。随着我们部署的 agent 越来越多，最大的挑战是那些看起来正常、后来才浮现的静默失败，而修复它们基本靠猜。AgentCore 中的优化能力改变了这一点。它们分析我们的生产 trace，浮现失败模式、解释为什么会发生，并按影响排序。随后我们会得到改进 prompt 与工具描述的建议，并在采纳之前于实时流量上做 A/B 测试。agent 改进现在是一个以数据为依据的持续回路，而不是试错。”
>         Kazumi Matsuda，FUJISOFT AI 推进部高级经理

# agent 能力增长时更强的控制：新的策略增强

更有能力的 agent 意味着更大的暴露面。而 agent 带来了传统软件从未有过的安全挑战：它们是概率性的。agent 会做判断，而判断可能被上下文影响。新的暴露点不是你的网络，而是 agent 的上下文——在这里，prompt 注入与记忆投毒不需要闯入，只需要说服 agent 做出一个糟糕的判断。

保护概率性组件的方式，是用确定性的东西：不是把它当大脑，而是把它当外围护栏。AgentCore 中的策略能力已经提供实时的、确定性的控制，在网关处定义 agent 能对你的工具和数据做什么、不能做什么。今天我们通过 Bedrock Guardrails 集成来扩展它们——该集成现已正式可用，会对 agent 的每一个动作评估 prompt 注入尝试、有害内容与敏感数据泄露。这些检查运行在网关层，位于 agent 代码之外，agent 在上下文里看不到它们，无法绕过它们推理，也无法说服自己它们不适用。

Guardrails 是策略引擎可用来采取行动的第一种检测信号，而且不会只有我们自己的信号。即将推出的是，AgentCore 将允许你把来自领先安全供应商（包括 Check Point、Zscaler、Rubrik、Netskope 与 SentinelOne）的检测信号输入同一套策略。无论信号来自哪里，原则都保持不变：检测可以是概率性的，但策略执行始终是确定性的，基于既定阈值做出最终的允许或拒绝决定。

由于 AgentCore 上的每个工具与上下文来源都经由网关路由，你的 agent 新获得的能力会自动受到同一安全层的治理。更有能力的 agent 与更强的控制，一起扩展。

# 从想法到可用 agent 只需几分钟：AgentCore harness 正式可用

agent 不只是模型。如果模型是大脑，那么 harness 就是身体：大脑完成工作所需的一切。它运行编排循环、执行工具、管理上下文窗口、跨轮次持久化状态、从失败中恢复，并隔离每个会话。harness 对 agent 表现的影响与模型一样大。构建一个耐用的 harness，正是今天大多数团队花时间的地方。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/06/16/21242-3.png)

今天正式可用的 AgentCore harness 把这一层作为托管能力交给你。你不必编写循环代码，而是在配置中定义你的 agent：它使用的模型、它调用的工具、它能访问的 skills、它遵循的指令。AgentCore 为你组装并运行这个循环。从这一个定义出发，你在几分钟内就得到一个可用的 agent，运行在自己隔离的环境中。它自带文件系统与 shell、跨会话的 memory、skills（包括 AWS 精选目录）以及网页浏览。这不是一个你迟早会弃用的起步工具：你起初使用的配置，就是你在规模化时运行的配置；当你需要自定义编排时，可以把 harness 导出为代码，留在同一平台上而无需重建任何东西。

除了速度，它还解锁了市场尚未提供的一种真正选择。今天可用的 harness 方案都会把你绑在某样东西上。开源方案要你自己托管和运维 harness；托管服务把你锁在它们的环境里；来自模型实验室的 harness 只为它们自己的模型优化。我们把 harness 与模型解耦，因此你可以选择任何模型，并在会话中途切换，而不必改动 agent 逻辑。随着前沿推进、某个任务的最佳模型发生变化，你的 agent 的地基依然稳固。

选择只是其中一部分。由于 harness 是单一平台的一个部件，而不是包裹在框架外面的一层托管外壳，它通过同一个网关触达你的工具——这个网关同时执行你的安全策略，并把你的 agent 连接到组织知识、web 搜索与付费服务。身份、memory 与可观测性都来自同一个平台，因此 agent 的每一个动作从第一次调用起就受到治理与追踪，无需额外接线。你在第一天声明的 agent，就是你跑到第一千次时运行的 agent，一路都建立在同一套地基上。

> “Twilio 的客户正在构建跨语音、消息与数字渠道工作的 AI agent，借助实时智能与持久记忆，让每一次交互都像一场对话。通过把 AgentCore harness 与 Twilio Conversations 结合，开发者可以从想法走到上线 agent，而无需重新改造基础设施。最好的客户体验，发生在优秀的 AI 与优秀的通信基础设施一起构建的时候。”
>         Omar Paul，Twilio 产品副总裁

**开始使用**

这些能力今天已在 AgentCore 上正式可用：托管 harness、Bedrock Managed Knowledge Base、Web Search、Guardrail 集成、recommendations 与 A/B 测试。Insights 与 payments 以预览版提供。

在[控制台](https://us-west-2.console.aws.amazon.com/bedrock-agentcore/home?region=us-west-2)中开始，或使用 [AgentCore CLI](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-cli.html)。访问[文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)了解更多。

### 关于作者

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/21/MadhuProfile.jpg)Madhu Parthasarathy**

Madhu Parthasarathy 是 Amazon Bedrock AgentCore 的总经理，领导团队打造这个供企业构建、连接与优化生产级 AI agent 的平台。他拥有超过 20 年构建大规模分布式基础设施的经验，其中在 Amazon 超过 16 年，期间在 Amazon Retail、Elastic Block Store（EBS）以及如今的 AgentCore 领导了多项重要计划。在回到 Amazon 之前，Madhu 在 LinkedIn 担任高级领导职务，负责驱动 LinkedIn 全部企业业务线的企业平台；他还在一家新型云服务初创公司担任高级领导职务，负责 AI 基础设施并确立安全与开发者体验的愿景。他常驻加利福尼亚州圣克拉拉。
