---
vendor: aws_bedrock
title: Long-running execution flows now supported in Amazon Bedrock Flows in public preview
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/long-running-execution-flows-now-supported-in-amazon-bedrock-flows-in-public-preview
date: 2025-07-11
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: d4b3f712de6a
---

# Amazon Bedrock Flows 现已在公开预览中支持长时间运行执行流

今天，我们宣布 [Amazon Bedrock Flows](https://aws.amazon.com/bedrock/prompt-flows/) 中的[长时间运行执行（异步）](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-create-async.html) flow 支持进入公开预览。借助 Amazon Bedrock Flows，你可以把基础模型（FM）、[Amazon Bedrock Prompt Management](https://aws.amazon.com/es/bedrock/prompt-management/)、[Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/)、[Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/)、[Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/) 以及其他 AWS 服务连接起来，以构建并扩展预定义的生成式 AI workflow。

随着各行各业客户构建日益复杂的应用，他们反馈需要处理更大的数据集，并运行需要超过几分钟才能完成的复杂 workflow。许多客户告诉我们，他们希望转换整本书、处理海量文档，并在编排多步 AI workflow 时不必担心运行时限制，这凸显了对能够处理长时间运行后台任务的解决方案的需求。为回应这些关切，Amazon Bedrock Flows 推出了一项公开预览的新功能，把 workflow 执行时间从 5 分钟（同步）延长到 24 小时（异步）。

借助 Amazon Bedrock 长时间运行执行流（异步），你可以把多个 prompt、AI 服务和 Amazon Bedrock 组件串联成复杂的长时间运行 workflow（异步最长 24 小时）。新能力包括可直接使用 [AWS Management Console](https://aws.amazon.com/console) 和 [Amazon Bedrock Flow API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_StartFlowExecution.html) 获取内置的执行追踪，以实现可观测性。这些增强大幅简化了 Amazon Bedrock Flows 中的 workflow 开发与管理，帮助你专注于构建和部署生成式 AI 应用。

通过把 workflow 执行（以可运行最长 24 小时的长时间运行流异步进行）与用户的即时交互解耦，你现在可以构建这样的应用：能够处理需要超过 5 分钟处理的大负载、执行资源密集型任务、应用多条规则进行决策，甚至在与多个系统集成的同时在后台运行 flow——同时为用户提供无缝、响应及时的体验。

## 解决方案概览

使用 Amazon Bedrock Flows 的组织现在可以利用长时间运行执行流能力来设计和部署长时间运行的 workflow，从而构建更具可扩展性和更高效率的生成式 AI 应用。该功能带来以下好处：

- **长时间运行的 workflow** – 你可以把长时间运行的 workflow（最长 24 小时）作为后台任务运行，并使 workflow 执行与用户的即时交互解耦。
- **大负载** – 该功能支持大负载处理和资源密集型任务，可持续 24 小时，而不是当前的 5 分钟限制。
- **复杂用例** – 它可以管理集成多个外部系统的复杂、多步决策生成式 AI workflow 的执行。
- **对构建者友好** – 你可以通过 [Amazon Bedrock API](https://docs.aws.amazon.com/bedrock/latest/APIReference/welcome.html) 和 Amazon Bedrock 控制台来创建和管理长时间运行执行流。
- **可观测性** – 你可以获得无缝的用户体验，能够查看 flow 执行状态并相应地获取结果。该功能还提供追踪，让你可以查看每个节点的输入和输出。

电通（Dentsu）是一家领先的广告代理公司和创意机构，它需要处理执行时间更长的复杂、多步生成式 AI 用例。其中一个用例是其 [Easy Reading](https://www.dentsucreative.com/en-gb/cases/easy-reading) 应用，它把包含许多章节和插图的书籍转换为易于阅读的格式，使有智力障碍的人也能接触文学作品。借助 Amazon Bedrock 长时间运行执行流，电通现在可以：

- 在 workflow 内处理大输入并执行复杂的资源密集型任务。在长时间运行执行流之前，由于 flow 的 5 分钟执行限制，输入大小受到限制。
- 把多个外部系统和服务集成到生成式 AI workflow 中。
- 同时支持快速、近实时的 workflow，以及运行时间更长、更复杂的 workflow。

“与 Amazon Bedrock 合作并向客户展示价值的过程非常棒，”电通创意巴西（Dentsu Creative Brazil）创新总监 Victoria Aiello 表示。“借助追踪和 flow，我们能够展示 AI 所做工作背后的处理过程，让我们对将要产出的内容有更好的可见性和准确性。对于 Easy Reading 用例，长时间运行执行流可以一次性处理整本书，利用 24 小时的 flow 执行时间，而不必编写自定义代码来分别管理书中多个部分。这为我们在制作新书、甚至集成不同模型时节省了时间；我们可以根据每本书的需求或内容测试不同的结果。”

下面我们来探讨 Amazon Bedrock Flows 中新的长时间运行执行流能力如何让电通构建一个更高效、可长时间运行的书籍处理生成式 AI 应用。下图展示了电通书籍处理应用的端到端 flow。流程始于客户把一本书上传到 [Amazon Simple Storage Service](https://aws.amazon.com/s3)（Amazon S3），触发一个处理多个章节的 flow，其中每一章都会根据用户的具体要求进行无障碍转换和格式化。转换后的章节随后被收集、与目录合并，并作为最终的无障碍文档存回 Amazon S3。这一长时间运行执行（异步）flow 可以高效处理大部头书籍，在 24 小时执行窗口内完成处理，并在整个转换过程中提供状态更新和可追溯性。

![Detailed AWS workflow diagram showing three-step book conversion process: upload, asynchronous processing, and status monitoring](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/09/ml-18820-1.png)

在以下各节中，我们以电通真实的书籍转换用例来演示如何在 Amazon Bedrock Flows 中创建长时间运行执行流。

## 先决条件

在实现这些新能力之前，请确保你具备以下条件：

- 一个 AWS 账户
- 已启用的其他 Amazon Bedrock 功能，例如：  [在 Amazon Bedrock Prompt Management 中为客户服务交互创建并测试你的基础 prompt](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-create.html) 使用相关规则设置 Amazon Bedrock Guardrails
- 按 workflow 需要配置的辅助 AWS 服务，例如 [Amazon DynamoDB](https://aws.amazon.com/dynamodb)、Amazon S3 和 [Amazon Simple Notification Service](https://aws.amazon.com/sns/)（Amazon SNS）
- 所需的 [AWS Identity and Access Management](https://aws.amazon.com/iam/)（IAM）权限：  [访问 Amazon Bedrock Flows 的权限](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-permissions.html) [对 Amazon Bedrock 中大语言模型（LLM）的适当访问权限](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access-permissions.html)

这些组件就绪后，你就可以在生成式 AI 用例中实现 Amazon Bedrock 长时间运行执行流能力。

## 创建长时间运行执行流

请完成以下步骤来创建长时间运行执行流：

- 在 Amazon Bedrock 控制台的导航窗格中，在 **Builder tools** 下选择 **Flows**。
- 选择 **Create a flow**。
- 为新的 flow 提供名称，例如 easy-read-long-running-flow。

有关创建 flow 的详细说明，请参阅 [Amazon Bedrock Flows 现已正式可用，并增强了安全性与可追溯性](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-flows-is-now-generally-available-with-enhanced-safety-and-traceability/)。Amazon Bedrock 提供不同的[节点类型](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-nodes.html) 来构建你的 prompt flow。

以下截图展示了电通书籍转换生成式 AI 应用的高层 flow。该 workflow 演示了从输入处理到内容转换，再到最终存储和交付的顺序流程。

![AWS Bedrock Flow Builder interface displaying easy-read-long-running-flow with connected components for document processing and storage](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/09/ml-18820-2.png)

下表列出了前面 workflow 中为文档处理和无障碍转换而设计的核心组件和节点。

| **节点** | **用途** |
| --- | --- |
| Flow Input | 入口点，接受 S3 前缀（章节）数组和无障碍配置文件 |
| Iterator | 逐个处理每个章节（前缀） |
| S3 Retrieval | 从指定的 Amazon S3 位置下载章节内容 |
| Easifier | 对章节内容应用无障碍转换规则 |
| HTML Formatter | 用适当的 HTML 结构格式化转换后的内容 |
| Collector | 在保持顺序的同时汇集转换后的章节 |
| Lambda Function | 把各章节合并为带目录的单一文档 |
| S3 Storage | 把最终转换后的文档存储到 Amazon S3 |
| Flow Output | 返回转换后书籍的 Amazon S3 位置及元数据 |

## 测试书籍处理 flow

现在我们准备通过 Amazon Bedrock 控制台或 API 来测试该 flow。我们使用一本名为“Beyond Earth: Humanity’s Journey to the Stars”的虚构书籍。这本书讲述了人类在地球之外最伟大的冒险，追溯我们从最早的卫星和月球漫步，到空间站，再到不断揭开太阳系奥秘的机器人探索者的历程。

- 在 Amazon Bedrock 控制台的导航窗格中选择 **Flows**。
- 选择该 flow（easy-read-long-running-flow），然后选择 **Create execution**。

创建执行之前，该 flow 必须处于 **Prepared** 状态。

**Execution** 选项卡显示所选 flow 之前的执行记录。

![AWS Bedrock Flow details page showing flow configuration and execution status](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/09/ml-18820-3.png)

- 提供以下输入：

阅读障碍测试输入

```
{
  "chapterPrefixes": [
    "books/beyond-earth/chapter_1.txt",
    "books/beyond-earth/chapter_2.txt",
    "books/beyond-earth/chapter_3.txt"
  ],
  "metadata": {
    "accessibilityProfile": "dyslexia",
    "bookId": "beyond-earth-002",
    "bookTitle": "Beyond Earth: Humanity's Journey to the Stars"
  }
}
```

这些是我们书中需要转换的不同章节。

- 选择 **Create**。

![AWS Bedrock Flow execution setup modal with name, alias selection, and JSON configuration for book processing](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/09/ml-18820-4.png)

Amazon Bedrock Flows 会启动我们 workflow 的长时间运行执行（异步）flow。仪表板会显示我们 flow 的各次执行及其对应状态（**Running**、**Succeeded**、**Failed**、**TimedOut**、**Aborted**）。当某次执行被标记为 **Completed** 时，结果就会出现在我们指定的 S3 存储桶中。

![AWS Bedrock Flow dashboard displaying flow details and active execution status for easy-read implementation](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/09/ml-18820-5.png)

选择某次执行会进入包含其详细信息的摘要页面。Overview 部分显示开始和结束时间，以及执行的 Amazon Resource Name（ARN）——这是后续排查特定执行问题时必不可少的唯一标识符。

![AWS execution interface with status, summary details, and workflow diagram of connected services](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/09/ml-18820-6.png)

当你在 flow 构建器中选择某个节点时，它的配置详情就会出现。例如，选择 Easifier 节点会显示所使用的 prompt、选定的模型（这里为 [Amazon Nova Lite](https://aws.amazon.com/ai/generative-ai/nova/)）以及额外的配置参数。这些是理解该特定组件如何配置的关键信息。

![AWS Bedrock interface with LLM settings, prompt configuration, and service workflow visualization](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/09/ml-18820-7.png)

系统还提供对执行追踪的访问，给出每个处理步骤的详细信息、跟踪实时性能指标，并突出显示 flow 执行期间发生的问题。可以使用 [API](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-trace.html) 启用追踪，并把追踪发送到 [Amazon CloudWatch](https://aws.amazon.com/cloudwatch) 日志。在 API 中，把 [InvokeFlow](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_InvokeFlow.html) 请求中的 enableTrace 字段设为 true。响应中的每个 flowOutputEvent 都会伴随一个 flowTraceEvent 返回。

![AWS flow execution trace showing processing steps for book chapter conversion](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/09/ml-18820-8.png)

我们现在已成功创建并执行了一个长时间运行执行流。你还可以使用 [Amazon Bedrock API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_StartFlowExecution.html) 以编程方式启动、停止、列出和获取 flow 执行。有关如何配置 flow 以获得增强的安全性和可追溯性的更多细节，请参阅 [Amazon Bedrock Flows 现已正式可用，并增强了安全性与可追溯性](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-flows-is-now-generally-available-with-enhanced-safety-and-traceability/)。

## 结论

在 Amazon Bedrock Flows 中集成长时间运行执行流，代表了生成式 AI 开发领域的一项重要进步。借助这些能力，你可以创建更高效的 AI 驱动解决方案来自动化长时间运行的操作，应对快速演进的 AI 应用开发领域中的关键挑战。

Amazon Bedrock Flows 中的长时间运行执行流支持现已在[提供 Amazon Bedrock Flows 的 AWS 区域](https://docs.aws.amazon.com/bedrock/latest/userguide/features-regions.html) 以公开预览形式可用，AWS GovCloud (US) 区域除外。要开始使用，请打开 Amazon Bedrock 控制台或 API，开始使用 Amazon Bedrock Flows 构建带长时间运行执行流的 flow。要了解更多信息，请参阅[在 Amazon Bedrock 中创建你的第一个 flow](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-get-started.html) 和[通过查看 Amazon Bedrock 中 flow 的追踪来跟踪每一步](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-trace.html)。

我们非常期待看到你利用这些新能力构建的创新应用。一如既往，欢迎你通过 [AWS re:Post](https://repost.aws/) 上关于 Amazon Bedrock 的渠道或你常用的 AWS 联系人提供反馈。加入 [community.aws](https://community.aws/) 的生成式 AI 构建者社区，分享你的经验并向他人学习。

### 关于作者

![Shubhankar Sumar](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/02/sssumar-1.jpg)**Shubhankar Sumar** 是 AWS 的高级解决方案架构师，专长为英国各地的企业软件和 SaaS 公司设计生成式 AI 驱动的解决方案架构。凭借深厚的软件工程背景，Shubhankar 擅长在云上设计安全、可扩展且具成本效益的多租户系统。他的专长在于把前沿的生成式 AI 能力无缝集成到现有 SaaS 应用中，帮助客户保持技术创新的前沿地位。

![Amit Lulla](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/Amit-lulla.jpg)**Amit Lulla** 是 AWS 的首席解决方案架构师，为软件公司设计企业级生成式 AI 和机器学习解决方案的架构。他拥有 15 年以上的软件开发与架构经验，热衷于把复杂的 AI 挑战转化为能带来真实业务价值的定制解决方案。在不设计前沿系统或指导同行架构师的时候，你会发现 Amit 在壁球场上、在练瑜伽，或是在规划下一次旅行冒险。他还保持着每日冥想的习惯，他认为这能让他在节奏飞快的 AI 创新世界中保持专注。

![Huong Nguyen](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/Huuong.jpg)**Huong Nguyen** 是 AWS 的首席产品经理。她负责领导 Amazon Bedrock Flows，拥有 18 年构建以客户为中心、数据驱动产品的经验。她热衷于让负责任的机器学习和生成式 AI 走向大众，以赋能客户体验和业务创新。工作之外，她喜欢与家人和朋友共度时光、听有声书、旅行和园艺。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/09/kamwang-1-100x107.png)Christian Kamwangala** 是 AWS 的 AI/ML 与生成式 AI 专家解决方案架构师，常驻法国巴黎。他与企业客户合作，利用 AWS 全面的机器学习技术栈来设计、优化和部署生产级 AI 解决方案。Christian 专长于推理优化技术，为大规模部署平衡性能、成本和延迟要求。业余时间，Christian 喜欢探索大自然，并与家人和朋友共度时光。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/09/jbart-1-100x113.png)Jeremy Bartosiewicz** 是 AWS 的高级解决方案架构师，在技术领域有 15 年以上、担任多种角色的经验。Jeremy 出身咨询背景，喜欢参与各式各样的项目，帮助组织借助云解决方案实现增长。他在 AWS 负责支持大型企业客户，并且是广告与机器学习 TFC 的成员。
