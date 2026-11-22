---
vendor: aws_bedrock
title: Amazon Bedrock Flows is now generally available with enhanced safety and traceability
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-flows-is-now-generally-available-with-enhanced-safety-and-traceability
date: 2024-11-22
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: c9ad142b0423
---

# Amazon Bedrock Flows 正式可用，并带来增强的安全性与可追溯性

今天，我们很高兴宣布 [Amazon Bedrock Flows](https://aws.amazon.com/bedrock/prompt-flows/)（此前称为 Prompt Flows）正式可用。借助 Bedrock Flows，你无需编写代码即可快速构建和执行复杂的[生成式 AI](https://aws.amazon.com/ai/generative-ai/) 工作流。主要优势包括：

- 通过直观的可视化界面简化生成式 AI 工作流开发。
- 无缝集成最新的基础模型（FM）、Prompt、Agent、知识库、Guardrails 以及其他 AWS 服务。
- 可灵活地根据你的业务逻辑定义工作流。
- 借助 SDK API 和无服务器基础设施，减少测试和部署 AI 工作流的时间与精力。

Bedrock Flows 让开发者和企业更容易驾驭生成式 AI 的力量，使你能够为客户打造更精密、更高效的 AI 驱动解决方案。

[Thomson Reuters](https://www.thomsonreuters.com/en.html) 通过值得信赖的专业能力和行业领先的洞察，提供创新的技术与 GenAI，从而改变专业人士的工作方式。

> “Thomson Reuters 企业 AI 平台的使命，是让我们的领域专家、工程师和 AI 研究人员共同创建 Gen-AI 能力，把前沿且值得信赖的技术交到客户手中，并塑造专业人士的工作方式。Amazon Bedrock Flows 让我们能够创建复杂、灵活、多 prompt 的工作流，并可以轻松地评估、比较和版本化。我们还可以使用用于无服务器流程执行的 SDK API，快速把 flow 集成到我们的应用中——无需在部署和基础设施管理上浪费时间。我们很高兴 Bedrock Flows 能为生成式 AI 应用开发带来潜在的生产力提升与加速。” 
>         – Laura Skylaki，Thomson Reuters 人工智能、商业智能与数据平台副总裁。

[Dentsu Creative](https://www.dentsucreative.com/) 是一家全球创意代理网络，致力于在品牌与消费者之间建立有意义的连接。

> “我们已成功借助 Amazon Bedrock Flows 改造客户体验。使用 Bedrock Flows，我们加快了把书籍重塑为便于有学习障碍的读者阅读的格式这一进程。Bedrock Flows 还让我们能够轻松地把客服解决方案与 Claude Haiku 这样的基础模型连接起来，以应对常见咨询，节省了大量时间，使客服团队可以专注于更复杂的请求。借助直观的可视化界面让非技术用户理解 AI 和业务逻辑是如何应用的，Bedrock Flows 为我们组织中的生成式 AI 解决方案带来了透明度和可见性。无论是触达新的受众还是扩缩客户请求，Dentsu 都在借助由 Amazon Bedrock Flows 驱动的尖端生成式 AI 技术持续创新。” 
>         – Thiago Winkler，Dentsu Creative Brazil 运营执行总监

## **Amazon Bedrock Flows 的新能力**

采用生成式 AI 的组织需要强大的安全控制，以及对其 AI 工作流的清晰可见性。今天，我们宣布 Amazon Bedrock Flows 的两项新能力，帮助客户构建更安全、更可追溯的 AI 应用：

- **增强的安全性**：由 [Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/) 驱动，可为 Prompt 节点和知识库节点过滤有害内容和不受欢迎的话题。现在有两类节点支持 Guardrails：  **Prompt 节点**：定义并强制执行对 FM 交互的控制。**知识库节点**：对由知识库生成的响应应用防护栏。

- **增强的可追溯性**：通过输入与输出的可追溯性以及行内校验，快速验证和调试工作流。获得对工作流执行的全面可见性，并通过以下方式快速定位错误：  对输入和输出节点的详细可追溯性支持。完整的执行路径信息，展示每个节点的输入、输出、执行时间和错误。可视化构建器中节点的行内校验状态。

设想 ACME Corp 是一家虚构的电商公司，正在使用 Amazon Bedrock Flows 构建客服聊天机器人。他们在实施过程中面临几个挑战：

- 他们的聊天机器人有时会生成包含敏感客户信息的响应。
- 他们难以在不同客户交互中保持一致的回答质量和语气。
- 他们花费大量时间和精力排查应用中的问题。
- 他们无法确保响应符合公司政策和监管要求。
- 他们缺乏对影响客户体验的性能瓶颈的可见性。

下面我们来看 Amazon Bedrock Flows 的新能力如何应对这些挑战，并让 Acme Corp 构建更安全、高效且透明的客服解决方案。

## **先决条件**

在实施这些新能力之前，请确保你具备以下条件：

- 一个 AWS 账户
- 在 Amazon Bedrock 中：  在 Prompt Management 中[创建并测试你的基础 prompt](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-create.html)，用于客服交互。[设置你的知识库](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-create.html)，纳入相关的客服文档、FAQ 和产品信息。配置客服工作流所需的任何辅助 AWS 服务（例如用于订单历史的 Amazon DynamoDB）。

- 在 Amazon Bedrock Guardrails 中：  为客服交互[创建护栏配置](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-create.html)（例如 `CustomerServiceGuardrail-001`），其中包含：  针对不当语言和有害内容的内容过滤器 针对客户数据的个人可识别信息（PII）检测与掩码规则 针对公司专有术语的自定义词过滤器  上下文锚定检查以确保信息准确 测试并验证你的护栏配置。发布护栏的可用版本。

- 所需的 IAM 权限：  对 [Amazon Bedrock Flows 的访问权限](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-permissions.html) [使用已配置护栏的权限](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-permissions.html) 对任何集成 AWS 服务的适当访问权限

这些组件就位后，你就可以继续在客服工作流中实施这些新能力。

## **在 Flows 中启用增强的安全性**

对于 Acme Corp 的客服聊天机器人，实施护栏有助于确保安全、合规且一致的客户交互。

以下说明如何在 Prompt 节点和知识库节点中启用护栏：

- 在 Amazon Bedrock 的 AWS 管理控制台中，打开 `customer service flow` 中要添加护栏的 Prompt 节点或知识库节点。如需要，可创建新的 flow。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image001.png)
- 在节点配置面板中，找到 **Guardrail** 部分。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image003.png)
- 从下拉菜单中选择一个已有的护栏。例如 **CustomerServiceGuardrail-001**。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image005.png)
- 在本例中，`CustomerServiceGuardrail-001` 配置为：  掩码客户 PII 数据（姓名和电子邮箱） 阻止不当语言和有害内容 使响应符合公司政策 在响应中保持专业语气

- 选择护栏的适当版本。例如 **Working draft**。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image007.png)
- 输入用于客服场景的 prompt 消息。例如 `Respond to customer queries`。
- 把 Prompt 节点连接到 flow 的输入和输出节点。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image009.png)
- 在 Test Flow 中输入一个 prompt 来测试应用了护栏的 Flows。例如 `Hi, my name is John Smith, email – [john.smith@email.com](mailto:john.smith@email.com). How do I get started with setting up an ACME Corp account?`
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image011.png)
- 在界面右侧窗格显示的 **Test flow** 中，可以看到模型响应如何处理敏感信息。例如：  原始响应：“Dear Mr. *John Smith*…” 护栏响应：“Dear Mr. *{NAME}*…”  ![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image013.png)

## **通过 Flows Trace View 增强可追溯性**

新的 Flows Tracing 能力现在可以详细地展现 flow 的执行过程，并通过 Trace view 和行内校验增强调试能力。这套全面的监控方案帮助开发者更有效地监控、调试和优化其 AI 工作流。

增强可追溯性的主要优势包括：

- 通过 Trace view 获得完整执行路径的可见性
- 对每个节点进行详细的输入/输出追踪
- 每个节点的错误、警告和执行耗时
- 快速识别瓶颈和问题
- 更快的错误根因分析

对于 Acme Corp 的客服团队，新的 Flows Tracing 能力为其聊天机器人的性能和行为提供了关键洞察。这帮助他们：

- 监控客户交互的响应时间
- 识别导致延迟的客户查询模式
- 调试对话流中的问题
- 优化客户体验

要使用 Trace view：

- 在 Amazon Bedrock 控制台中，打开你的 flow 并用示例查询进行测试。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image015.png)
- 运行 flow 后，选择 **Show trace** 来分析这次交互。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image017.png)
- 查看 Flow Trace 窗口，其中显示：  客户交互每一步的响应时间 客户输入如何被处理 护栏在哪里应用 性能瓶颈  ![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image019.png)
- 分析执行详情，包括：  客户查询的处理步骤 响应的生成与验证 每一步的耗时 错误详情与原因分析  ![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image021.png)

## **行内校验状态**

Flows 可视化构建器和 SDK 现在包含直观的节点校验能力：

可视化构建器：

- 绿色背景表示节点配置有效。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image023.png)
- 红色背景表示节点配置无效，需要处理。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image025.png)
- 黄色背景表示节点配置存在警告。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image027-new.png)

这些校验能力在可视化开发和程序化开发过程中提供实时校验反馈，帮助开发者快速识别并解决 flow 中的潜在问题。

## **结论**

Bedrock Flows 中 Bedrock Guardrails 的集成与增强的可追溯性，代表了生成式 AI 开发的一次重大进步。这些能力使开发者能够打造更安全、透明且高效的 AI 驱动解决方案，应对快速演进的 AI 应用开发领域中的关键挑战。

带有这些新能力的 Bedrock Flows 现已在 Amazon Bedrock 可用的所有区域正式可用（GovCloud 除外）。自 2025 年 2 月 1 日起，Bedrock Flows 还将按运行工作流所需的节点转换次数收费，价格为每 1000 次节点转换 0.035 美元。我们邀请你探索这些新能力，亲身体验它们如何改进你的生成式 AI 开发流程。要开始使用，请打开 Amazon Bedrock 控制台，今天就借助 Flows 构建具备更强安全性和可见性的 flow。了解更多信息，请参阅 AWS 用户指南中的 [Guardrails 集成](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-guardrails.html) 和[可追溯性](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-trace.html)。定价信息请访问 [Amazon Bedrock 定价页面](https://aws.amazon.com/bedrock/pricing/)。

我们非常期待看到你们用这些新能力构建的创新应用。一如既往，欢迎通过 [AWS re:Post](https://repost.aws/) 的 Amazon Bedrock 版块或你常用的 AWS 联系人提供反馈。加入 [community.aws](https://community.aws/) 的生成式 AI 构建者社区，分享你的经验并向他人学习。

### 关于作者

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/Amit-lulla.jpg) Amit Lulla** 是 AWS 的首席解决方案架构师，为软件公司设计企业级生成式 AI 和机器学习解决方案。他拥有超过 15 年的软件开发与架构经验，热衷于把复杂的 AI 挑战转化为能带来真实商业价值的定制解决方案。在不设计前沿系统或指导其他架构师的时候，你会在壁球场、瑜伽垫上找到 Amit，或者看到他在规划下一次旅行冒险。他还坚持每日冥想练习，他认为这让他在快节奏的 AI 创新世界中保持专注。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/Huuong.jpg)**Huong Nguyen** 是 AWS 的首席产品经理。她负责领导 Amazon Bedrock Flows，拥有 18 年构建以客户为中心、数据驱动产品的经验。她热衷于让负责任的机器学习和生成式 AI 走向大众，以推动客户体验和业务创新。工作之外，她喜欢与家人朋友共度时光、听有声书、旅行和园艺。
