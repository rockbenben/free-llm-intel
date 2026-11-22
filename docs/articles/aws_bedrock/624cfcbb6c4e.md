---
vendor: aws_bedrock
title: How Untold Studios empowers artists with an AI assistant built on Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/how-untold-studios-empowers-artists-with-an-ai-assistant-built-on-amazon-bedrock
date: 2025-02-07
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: f58cb2e57e97
---

# Untold Studios 如何借助基于 Amazon Bedrock 构建的 AI 助手为艺术家赋能

[Untold Studios](https://untoldstudios.tv/) 是一家技术驱动、行业领先的创意工作室，专精高端视觉特效与动画。我们对创新的执着把我们引向一个关键挑战：如何利用机器学习（ML）的能力进一步增强竞争优势，同时在技术进步与严格的数据安全要求、以及简化对现有内部资源访问的需求之间取得平衡。

要让艺术家用上技术，我们需要打造好用的用户界面。这是一大挑战，尤其是当最终用户群体在需求和技术经验上差异很大时。我们看到一个机会：用大语言模型（LLM）构建自然语言界面，这既让该挑战变得更容易，也承担了大量繁重的工作。

本文详述我们如何用 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 创建一个 AI 助手（Untold Assistant），让艺术家可以通过自然语言界面直接访问内部资源，并集成到他们现有的 Slack 工作流中。

## 解决方案概览

Untold Assistant 是艺术家的中枢。除了文本生成和图像生成这类常见 AI 功能外，它还让艺术家能通过自然语言查询与内部数据、工具和工作流交互。

在 UI 方面，我们使用 Slack 的内置功能而不是自建前端。Slack 已经为工作站和手机提供应用、为复杂查询提供消息线程、为反馈提供 emoji 反应，以及文件共享能力。实现上，我们用 Slack 的事件订阅 API 处理传入消息，用 Slack 的 Web API 发送回复。用户通过私聊直接消息与 Untold Assistant 交互，或在频道中 @ 提及它，让所有人看到。由于我们的团队本来就整天在用 Slack，这消除了上下文切换和采用新软件的需要。每条新消息都会先收到一个齿轮 emoji 作为即时反馈，查询成功后变为对勾，出错则变为 X。下面的截图展示了一个示例。

![AI 助手截图](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/02/04/ML-17799-screenshot-1.png)

借助 [Amazon Bedrock 上的 Anthropic Claude 3.5 Sonnet 模型](https://aws.amazon.com/bedrock/claude/)，系统处理复杂请求并生成贴合上下文的回复。无服务器架构提供可扩展性与响应能力，安全存储则承载工作室庞大的资产库和知识库。使用的主要 AWS 服务包括：

- [Amazon Bedrock](https://aws.amazon.com/bedrock/) – 包括 Anthropic 的 Claude 3.5 Sonnet LLM、Stability AI 的 Stable Diffusion 3 图像生成，以及知识库连接器
- [AWS Lambda](https://aws.amazon.com/lambda) – 用于工作流执行
- [Amazon API Gateway](https://aws.amazon.com/api-gateway) – 用于 Slack 事件处理器
- [Amazon Simple Storage Service (Amazon S3)](https://aws.amazon.com/s3) – 用于任意非结构化数据
- [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) – 用于持久化存储

下图展示了解决方案架构。

![架构图](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/02/04/ML-17799-arch-diagram-1.png)

该应用的主要组件包括 Slack 集成、Amazon Bedrock 集成、Retrieval Augmented Generation（RAG）实现、用户管理和日志记录。

### Slack 集成

我们采用双函数方案来满足 Slack 的 3 秒确认要求。来自 Slack 的传入事件被发送到 API Gateway 中的一个端点，Slack 期望在 3 秒内收到响应，否则请求失败。第一个 Lambda 函数（具有预留容量）快速确认事件，并把请求转发给第二个函数，在后者那里可以不受时间限制地处理。该设置既满足了对时间敏感的响应，又允许充分的请求处理。我们直接从第一个函数调用第二个函数，中间不使用 [Amazon Simple Notification Service](https://aws.amazon.com/sns)（Amazon SNS）事件或 [Amazon Simple Queue Service](https://aws.amazon.com/sqs/)（Amazon SQS）队列，以尽可能降低延迟。

### Amazon Bedrock 集成

我们的 Untold Assistant 使用 Amazon Bedrock 和 Anthropic 的 Claude 3.5 Sonnet 模型进行自然语言处理。我们使用该模型的函数调用能力，让应用可以按需触发特定的工具或动作。这使助手既能处理一般查询，也能处理复杂的专业查询，或在我们各内部系统中执行任务。

### RAG 实现

我们的 RAG 设置使用 Amazon Bedrock 连接器与 Confluence 和 Salesforce 集成，接入我们现有的知识库。对于没有现成连接器可用的其他数据源，我们把内容导出到 Amazon S3 并使用 Amazon S3 连接器。例如，我们把资产库中已分块的资产元数据导出到 Amazon S3，让 Amazon Bedrock 负责 embeddings、向量存储和搜索。这种方式显著减少了开发时间和复杂度，让我们可以专注于改善用户体验。

### 用户管理

我们把 Slack 用户 ID 映射到内部用户池，该用户池目前位于 DynamoDB（但设计上可与 [Amazon Cognito](https://aws.amazon.com/cognito/) 配合使用）。该系统按每位用户的角色和权限级别裁剪助手能力，确保它在每个用户的权限范围内运作，同时保持功能。对数据源的访问通过工具控制。每个工具封装一个数据源，而 LLM 对工具的访问受用户及其角色限制。

此外，如果用户告诉助手某件应当被记住的事，我们会把这条信息存入库中，并在用户每次发起请求时把它加入上下文。例如，“Keep all your replies as short as possible”（所有回复尽量简短）或“If I ask for code it’s always Python”（要代码时一律用 Python）。

### 日志与监控

我们使用 Lambda 中与 [Amazon CloudWatch](https://aws.amazon.com/cloudwatch) 的内置集成来跟踪系统性能和错误状态。为了监控关键错误，我们设置了向专用 Slack 频道的直接通知，以便即时知晓并响应。每次查询和工具调用都会记录到 DynamoDB，形成丰富的数据集，我们用它分析使用模式并优化系统的性能与功能。

## 使用 Amazon Bedrock 进行函数调用

与 Anthropic 的 Claude 一样，大多数现代 LLM 都支持函数调用，这让我们能把 LLM 的能力扩展到单纯的文本生成之外。我们可以提供一组函数规范，其中包含函数将要做什么的描述，以及函数参数的名称和描述。基于这些信息，LLM 判断传入的请求能否直接解决，还是解决该查询的最佳下一步是调用某个函数。如果是后者，模型会返回要调用的函数名称以及参数和值。接下来由我们运行该函数并发起下一步。Agent 会循环使用这套机制来调用函数并处理其输出，直到达到成功标准。在我们的场景中，我们只实现单次函数调用以保持简单和健壮。不过在某些情况下，函数本身会借助 LLM 处理数据，并为最终用户整理成漂亮的格式。

函数调用是一项非常有用的特性，它帮助我们把非结构化的用户输入转换为结构化的、可自动化的指令。我们预计在未来几个月里会添加更多函数，以扩展 AI 助手的能力并提升其实用性。尽管像 LangChain 这样的框架为实现函数调用系统提供了全面的解决方案，我们还是选择了一个针对自身需求量身定制的轻量自研方案。这一决定让我们保持更小的占用，并专注于用例必需的功能。

下面是一个使用 AiTool 基类实现可扩展性的代码示例。

![AI 助手代码片段](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/02/04/ML-17799-code-snippet-1.png)

添加新函数只需要创建像示例中那样的类。该类会被自动发现，如果用户有权访问该函数，相应的规范就会被添加到发给 LLM 的请求中。创建函数规范所需的全部信息都从代码和 docstring 中提取：

- **NAME** – 函数的 ID
- **PROGRESS_MESSAGE** – 在函数运行前通过 Slack 发给用户以提供即时反馈的消息
- **EXCLUSIVE_ACCESS_DEPARTMENTS** – 如果设置，只有指定部门的用户才能访问该工具

这个示例中的工具会更新用户记忆。例如，查询“Remember to always use Python as a programming language”会触发该工具的执行。LLM 会从请求中提取 info 字符串，例如“code should always be Python”。如果始终被加入上下文的现有用户记忆中已经包含关于同一主题的记忆（例如“code should always be Java”），LLM 还会提供记忆 ID，现有记忆将被覆盖。否则，会创建一条带新 ID 的新记忆。

## 关键特性与收益

Slack 作为单一入口，让艺术家无需离开熟悉的工作流就能查询各种内部系统。以下功能由使用 Anthropic 的 Claude 的函数调用驱动：

- 面向不同用户角色的多种知识库（Confluence、Salesforce）
- 内部资产库（Amazon S3）
- 由 Stable Diffusion 驱动的图像生成
- 用户专属的记忆与偏好（例如默认编程语言、图像生成的默认尺寸、回复的详细程度）

通过消除额外软件和上下文切换的需要，我们大幅降低了访问关键资源的阻力。系统全天候为艺术家的查询和任务提供服务，而我们基于 Anthropic 的 Claude 的函数调用框架也为未来扩展功能留出了空间。

LLM 的自然语言界面对用户交互来说是一场变革。相比传统界面，它天生更灵活、更宽容，能够解读非结构化输入、主动询问缺失信息，并完成日期格式化、单位换算、从自然语言描述中提取数值等任务。系统能娴熟处理含糊的查询，提取相关信息与意图。这意味着艺术家可以专注于创作过程，而不必担心措辞是否精确，或去穿梭于复杂的菜单结构。

安全与可控是我们采用 AI 战略中的重中之重。通过把所有数据留在 AWS 生态内，我们消除了对第三方 AI 工具的依赖并缓解了相关风险。这种方式让我们对数据访问和使用保持严密控制。此外，我们实施了全面的使用分析，提供关于采用模式和可改进之处的洞察。这种数据驱动的方式确保我们持续打磨工具，以满足艺术家不断变化的需求。

## 影响与未来计划

Untold Assistant 目前每天处理多达 120 次查询，其中约 10–20% 会调用其他工具，例如图像生成或知识库搜索。尤其对那些还不熟悉内部工作流和应用的新用户来说，它可以节省大量时间。他们不必再到多个 Confluence 空间和 Slack 频道里翻找，或联系技术团队，只需询问 Untold Assistant，它就像支持团队的一名虚拟成员。这可以把耗时从几分钟缩短到几秒钟。

总体而言，Untold Assistant 使用 AWS 服务快速开发并部署，已经带来多项收益：

- 提升了此前未被充分利用的内部资源的可发现性和使用率
- 显著减少了搜索信息的时间
- 通过统一入口和授权系统，简化了对多个内部系统的访问
- 减轻了支持团队和技术团队的负担
- 通过提供用户交互框架，加快了新技术的采用速度

在这一成功的基础上，我们正通过更多函数调用来扩展功能。一项重要的计划功能是面向艺术家的渲染作业错误分析。该工具会自动获取最近渲染的日志，利用 Anthropic 的 Claude 的能力分析潜在错误，并结合互联网资源和内部已知错误知识库，为用户提供解释与解决方案。

此外，我们计划使用 [Amazon Titan Text Embeddings](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html) 和凝聚层次聚类来分析已保存的查询，以识别语义相近的问题。当某个簇的出现频率超过我们设定的阈值时（例如一周内有超过 10 个来自不同用户的相似问题），我们就会完善知识库或更新入门材料，主动回应这些常见查询，减少重复提问并提升助手的效率。

这些初期使用指标和计划中的技术改进，体现了系统对我们工作流的积极影响。通过自动化常见的支持任务，并通过数据驱动分析持续完善知识库，我们在保持高质量协助的同时减轻了技术团队的支持负担。模块化架构让我们能在需求出现时快速集成新工具，跟上 AI 与 ML 领域惊人的进展步伐。

## 结论

Untold Assistant 展示了 Amazon Bedrock 如何在不牺牲安全与可控性的前提下快速开发复杂的 AI 应用。使用 Amazon Bedrock 中的函数调用和预制连接器，省去了复杂的向量存储集成和自定义 embedding pipeline，把我们的开发时间从数月缩短到数周。使用 Python 类作为工具的模块化架构，让系统高度可维护、可扩展。

通过自动化日常技术任务和信息检索，我们让艺术家腾出精力专注于创造业务价值的创意工作。该方案在 LLM 接口与业务逻辑之间做了清晰的分离，且完全构建在 AWS 生态内，因此能在保持严格数据安全的同时快速集成新能力。相比传统的菜单驱动系统，LLM 解读非结构化输入和处理含糊查询的能力创造了更自然、更宽容的界面。这种技术稳健性与艺术家生产力提升的基础，让我们能够快速采用新兴 AI 能力，同时继续聚焦创意创新。

想了解如何用 Amazon Bedrock 简化贵公司的工作流，请参阅 [Amazon Bedrock 入门](https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html)。如有问题或建议，欢迎留言评论。

### 关于作者

**![Olivier Vigneresse](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/02/04/olivigne.jpg) Olivier Vigneresse** 是 AWS 的解决方案架构师。他常驻英国，主要服务媒体与娱乐行业的中小企业客户。凭借安全与网络方面的背景，Olivier 通过提供架构指导和最佳实践帮助客户在云之旅中取得成功；他也热衷于帮助客户利用机器学习与生成式 AI 用例创造价值。

**![Daniel Goller](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/02/04/daniel_goller.png) Daniel Goller** 是 Untold Studios 的研发负责人，专注于云基础设施和新兴技术。他在德国取得博士学位，期间与 BMW、Audi 等行业领导者合作；此后十年间他一直从事软件解决方案的实施，近年尤其侧重云技术。在 Untold Studios，他领导基础设施优化和 AI/ML 计划，凭借技术专长和研究背景推动媒体与娱乐领域的创新。

**![Max Barnett](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/02/04/bamax.jpg) Max Barnett** 是 AWS 的客户经理，专长于加速媒体与娱乐客户的云之旅。过去 4.5 年他一直在 AWS 帮助客户。Max 尤其深入参与视觉特效领域的客户，引导他们探索生成式 AI。
