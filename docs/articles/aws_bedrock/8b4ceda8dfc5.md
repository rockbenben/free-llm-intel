---
vendor: aws_bedrock
title: Reducing hallucinations in large language models with custom intervention using Amazon Bedrock Agents
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/reducing-hallucinations-in-large-language-models-with-custom-intervention-using-amazon-bedrock-agents
date: 2024-11-26
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 3ccba3b2e9a4
---

# 使用 Amazon Bedrock Agents 以自定义干预降低大语言模型的幻觉

[幻觉](https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence))在大语言模型（LLM）中指的是这样一种现象：LLM 生成的内容看似合理，但事实上不正确或是凭空捏造。当模型的训练数据缺少必要信息，或模型试图通过超出其实际知识的逻辑推断来生成连贯回答时，就可能出现这种情况。幻觉之所以产生，是因为[语言建模](https://h2o.ai/wiki/language-modeling/)方法本身存在固有局限：它以生成流畅且符合上下文的文本为目标，并不必然保证事实准确。

对于使用 LLM 的生产应用来说，缓解幻觉至关重要，尤其是在错误信息可能带来严重后果的领域，例如医疗健康、金融或法律应用。未被控制的幻觉会削弱系统的可靠性与可信度，可能导致伤害或法律责任。缓解幻觉的策略可以包括严格的事实核查机制、使用[检索增强生成（RAG），](https://aws.amazon.com/what-is/retrieval-augmented-generation/)整合外部知识源、应用置信度阈值，以及对关键输出实施人工监督或核验流程。

RAG 是这样一种方法：它通过引入检索外部知识的能力，并把检索到的内容作为 prompt 的一部分输入模型，来减少语言模型中的幻觉。retriever 模块负责根据输入查询或上下文，从大规模文本语料中检索相关段落或文档。检索到的信息随后提供给 LLM，LLM 将其与 prompt 结合，用于生成最终输出。通过让生成过程以来自可靠来源的事实信息为依据，RAG 可以降低生成错误或捏造内容的可能性，从而提升生成回答的事实准确性与可靠性。

[Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/) 通过上下文接地（contextual grounding）检查提供幻觉检测，可以使用 Amazon Bedrock API（例如 `Converse` 或 `InvokeModel`）无缝应用，也可以嵌入工作流。在 LLM 生成回答之后，这些工作流会执行检查，判断是否出现幻觉。这种设置可以通过 [Amazon Bedrock Prompt Flows](https://aws.amazon.com/bedrock/flows/) 实现，也可以使用 [AWS Lambda](https://aws.amazon.com/lambda) 函数编写自定义逻辑实现。客户还可以使用 Amazon Bedrock 模型评估中基于人工的评估功能，让人类评审者进行批量评估。然而这些都是静态工作流，更新幻觉检测逻辑需要修改整个工作流，限制了适应性。

为了满足这种灵活性需求，Amazon Bedrock Agents 支持动态工作流编排。借助 Amazon Bedrock Agents，组织可以实施可扩展、可定制的幻觉检测，根据具体需求进行调整；这样在把新的检测技术和额外的 API 调用纳入工作流时，无需重构整个工作流，所需工作量更小，并让 LLM 自行决定编排工作流的行动计划。

本文中，我们将使用 [Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/) 搭建自己的自定义 agentic AI 工作流，在检测到 LLM 幻觉时进行干预，并通过 human-in-the-loop 流程把用户查询转接给客服人员。可以把它理解为一种更简单的实现：当聊天机器人无法回答客户查询时，就转而呼叫客服人员。该聊天机器人基于 RAG 方法，能在很大程度上减少幻觉，而[agentic 工作流](https://promptengineering.org/exploring-agentic-wagentic-workflows-the-power-of-ai-agent-collaborationorkflows-the-power-of-ai-agent-collaboration/)则提供了一种可定制的机制，用来衡量、检测和缓解可能出现的幻觉。

Agentic 工作流为构建动态、复杂的业务用例工作流提供了全新视角，它借助 LLM 作为[推理引擎](https://cohere.com/blog/llm-reasoning-sets-new-benchmarks-for-ai)或大脑。这类 agentic 工作流把基于自然语言查询的任务分解为多个可执行步骤，并借助迭代反馈循环和[自我反思](https://blog.langchain.dev/reflection-agents/)，使用工具和 API 产出最终结果。

Amazon Bedrock Agents 通过编排多步骤任务，帮助加速生成式 AI 应用开发。Amazon Bedrock Agents 利用 LLM 的推理能力，把用户请求的任务拆解为多个步骤。它们依据给定的指令创建编排计划，然后通过调用公司 API 或使用 RAG 访问知识库来执行该计划，从而向用户给出最终回答。这带来了极大的用例灵活性，支持动态工作流，并降低了开发成本。Amazon Bedrock Agents 有助于定制应用以满足特定项目需求，同时保护私有数据并帮助保障应用安全。这些 agent 与 Lambda、[Amazon Bedrock](https://aws.amazon.com/bedrock) 等 AWS 托管基础设施能力配合工作，减少基础设施管理开销。此外，agent 还能简化工作流并自动执行重复性任务。借助 AI 自动化的力量，你可以提升生产力并降低成本。

Amazon Bedrock 是一项完全托管的服务，通过单一 API 提供来自 AI21 Labs、Anthropic、Cohere、Meta、Mistral AI、Stability AI 和 Amazon 等领先 AI 公司的高性能基础模型（FM）供你选择，并提供一整套能力，让你以安全性、隐私保护和负责任 AI 构建生成式 AI 应用。

## 用例概览

本文中，我们在 RAG 驱动的聊天机器人上加入自定义干预，用于在检测到幻觉时进行处理。我们将使用 Retrieval Augmented Generation Automatic Score（诸如 answer correctness 和 answer relevancy 等指标）**来制定自定义幻觉评分**，以衡量幻觉程度。如果某个 LLM 回答的幻觉评分低于自定义阈值，就说明生成的模型回答与标准答案不够一致。这种情况下，我们通过 [Amazon Simple Notification Service（Amazon SNS）通知](https://docs.aws.amazon.com/code-library/latest/ug/python_3_sns_code_examples.html)通知一组人工客服来协助处理该查询，而不是把带幻觉的 LLM 回答直接给客户。

我们使用的 RAG 聊天机器人会摄取 [Amazon Bedrock 用户指南](https://docs.aws.amazon.com/pdfs/bedrock/latest/userguide/bedrock-ug.pdf)，以帮助客户解答与 Amazon Bedrock 相关的问题。

## 数据集

[notebook](https://github.com/aws-samples/responsible_ai_reduce_hallucinations_for_genai_apps/blob/main/other-examples/bedrock-agent-self-reflection/bedrock-agent-self-reflection.ipynb) 中使用的数据集是最新的 [Amazon Bedrock 用户指南 PDF](https://docs.aws.amazon.com/pdfs/bedrock/latest/userguide/bedrock-ug.pdf) 文件，该文件可公开下载。你也可以使用自己选择的其他 PDF 从头创建知识库，并在该 notebook 中使用。

如果你使用自定义 PDF，就需要整理一个包含多个问题标准答案的监督数据集来测试这种方法。自定义幻觉检测器使用 RAGAS 指标，这些指标由包含问答对的 CSV 文件生成。对于自定义 PDF，需要替换该 CSV 文件，并针对不同的数据集重新运行 notebook。

除了 notebook 中的数据集，我们还会向 agent 提出多个问题，其中一些来自 PDF，一些不在 PDF 中。标准答案在相关时依据 PDF 内容人工整理。

## ![此图包含 4 个示例问题。我们向 agent 提出多个问题，其中一些来自 PDF，一些不在 PDF 中。标准答案在相关时依据 PDF 内容人工整理。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/24/ML-17639-Lab2-dataset-1024x260.png)

## 先决条件

要在你的 AWS 账户中运行此解决方案，请完成以下先决条件：

- 克隆 [GitHub 仓库](https://github.com/aws-samples/responsible_ai_reduce_hallucinations_for_genai_apps)并按照 README 中的步骤操作。
- 在 ml.t3.medium 的 [Amazon Elastic Compute Cloud（Amazon EC2）](https://aws.amazon.com/ec2) 上设置 [Amazon SageMaker](https://aws.amazon.com/sagemaker/) notebook
- 获取对 Amazon Bedrock 上托管模型的访问权限。在 Amazon Bedrock 控制台的导航窗格中选择 **Manage model access**，然后从可用选项列表中选择。本文我们使用 Amazon Bedrock 上的 [Anthropic 的 Claude v3（Sonnet）](https://www.anthropic.com/news/claude-3-family) 以及 Amazon Bedrock 上的 [Amazon Titan Embeddings](https://aws.amazon.com/bedrock/titan/) Text v2。

## 实施解决方案

下图展示了解决方案的架构：

自定义幻觉检测与缓解的架构图

整体工作流包含以下步骤：

- 数据摄取：把存储在 [Amazon Simple Storage Service（Amazon S3）](https://aws.amazon.com/s3) 存储桶中的原始 PDF 同步为 [Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/) 的数据源。
- 用户提出与 Amazon Bedrock 用户指南相关的问题，这些问题由设置为处理用户查询的 Amazon Bedrock agent 来处理。

`User query: What models are supported by bedrock agents?`

- agent 制定计划，并识别出需要使用知识库。随后它向知识库发送请求，知识库从底层向量数据库中检索相关数据。agent 通过 RAG 按以下步骤获取答案：  搜索查询被发往向量数据库（[Amazon OpenSearch Serverless](https://aws.amazon.com/opensearch-service/features/serverless/)）。检索到相关的答案分块。知识库根据检索到的答案分块生成回答，并回传给 agent。

`Generated Answer: Amazon Bedrock supports foundation models from various providers including Anthropic (Claude models), AI21 Labs (Jamba models), Cohere (Command models), Meta (Llama models), Mistral AI`

- 用户查询与知识库回答会一起用于调用正确的 action group。
- 用户问题和知识库回答作为输入传入一个 Lambda 函数，由它计算幻觉评分。

`The generated answer has some correct and some incorrect information as it picks up general Amazon Bedrock model support and not Amazon Bedrock Agents-specific model support. Therefore we have hallucination detected with a score of 0.4.`

- 如果答案评分低于自定义阈值，就发送 [SNS](https://aws.amazon.com/sns/) 通知。

`Because answer score is 0.4 < 0.9 (hallucination threshold), the SNS notification is triggered.`

- 如果答案评分高于自定义阈值，集成在 Lambda 中的幻觉检测器会返回最终的知识库回答。否则，它返回一个预定义回答，请用户稍等片刻，客服人员很快就会加入对话。

`Customer service human agent queue is notified and the next available agent joins or emails back if it is an offline response mechanism.`

- agent 的最终回答会显示在聊天机器人 UI（用户界面）中。

在 GitHub 仓库的 [notebook](https://github.com/aws-samples/responsible_ai_reduce_hallucinations_for_genai_apps/blob/main/other-examples/bedrock-agent-self-reflection/bedrock-agent-self-reflection.ipynb) 中，我们涵盖以下学习目标：

- 使用 agentic AI 工作流衡量并检测幻觉，该工作流在检测到幻觉时能够通知 human-in-the-loop 进行补救。
- 基于 RAGAS 中选定的评估指标、使用预定义阈值的自定义幻觉检测器。
- 为实现补救，我们会向客服队列发送 SNS 通知，等待人工协助解答问题。

### 步骤 1：使用 Amazon Bedrock Agents 设置 Amazon Bedrock Knowledge Bases

本节中，我们将把 [Amazon Bedrock Knowledge Bases ](https://aws.amazon.com/bedrock/knowledge-bases/)与 Amazon Bedrock Agents 集成，创建一个 RAG 工作流。RAG 系统使用外部知识源来增强 LLM 的输出，提升事实准确性并减少幻觉。我们创建 agent 时使用以下高层指令，鼓励它承担问答角色。

```
agent_instruction = """

You are a question answering agent that helps customers answer questions from the Amazon Bedrock User Guide inside the associated knowledge base.

Next you will always use the knowledge base search result to detect and measure any hallucination using the functions provided"

"""
```

### 步骤 2：用关于 Amazon Bedrock 文档的用户问题调用 Amazon Bedrock Agents

我们使用带有预定义问题和标准答案的监督数据集来调用 Amazon Bedrock Agents，它会基于 agent 从知识库得到的回答触发自定义幻觉检测器。在 notebook 中，我们演示了基于 RAGAS 指标的答案评分如何在低于预定义自定义阈值分数时通知人工客服代表。

我们使用 `answer correctness` 和 `answer relevancy` 等 RAGAS 指标来确定自定义阈值分数。视用例和数据集而定，适用的 RAGAS 指标列表可以相应定制。

要更改阈值分数，你可以修改 Lambda 函数 `measure_hallucination()` 中的 `lambda_hallucination_detection()` 方法。

agent 使用以下模板接收 prompt。模板中的 `user_question` 由包含问题与标准答案的监督数据集 CSV 文件逐条迭代得到。

```
USER_PROMPT_TEMPLATE = """Question: {user_question}

Given an input question, you will search the Knowledge Base on Amazon Bedrock User Guide to answer the user question. 
If the knowledge base search results do not return any answer, you can try answering it to the best of your ability, but do not answer anything you do not know. Do not hallucinate.
Using this knowledge base search result you will ALWAYS execute the appropriate action group API to measure and detect the hallucination on that knowledge base search result.

Remove any XML tags from the knowledge base search results and final user response.


Some samples for `user_question` parameter:

What models are supported by bedrock agents?
Which models can I use with Amazon Bedrock Agents?
Which are the dates for reinvent 2024?
What is Amazon Bedrock?

"""
```

### 步骤 3：在出现幻觉时触发 human-in-the-loop

如果 agent 的回答未达到自定义幻觉分数阈值，就使用 SNS 通知提醒 human-in-the-loop。这些通知可以发送到客服代表队列，或用于邮件和短信通知的 [Amazon Simple Queue Service（Amazon SQS）](https://aws.amazon.com/sqs) 队列。这些代表可以依据接受的培训和系统知识以及额外资源，通过回复邮件（离线）或正在进行的聊天（在线）来响应。这将取决于具体产品工作流的设计。

要查看实际发出的 SNS 消息，我们可以按照[查看 Lambda 函数的 CloudWatch 日志](https://docs.aws.amazon.com/lambda/latest/dg/monitoring-cloudwatchlogs-view.html)中的说明，查看最新的 Lambda [AWS CloudWatch](https://aws.amazon.com/cloudwatch) 日志。你可以在 Lambda 函数 `LambdaAgentsHallucinationDetection().` 的 [CloudWatch 日志](https://aws.amazon.com/cloudwatch/)中搜索字符串 `Received SNS message ::`。

## 成本考量

以下是一些重要的成本考量：

- 当前实现使用 Amazon Bedrock Knowledge Bases 或 Amazon Bedrock Agents 构建资源不会产生单独费用。
- 你将在 Amazon Bedrock 上产生 embedding 模型和文本模型调用的费用。更多详情请参阅 [Amazon Bedrock 定价](https://aws.amazon.com/bedrock/pricing/)。
- 你将产生 Amazon S3 和向量数据库的使用费用。更多详情请分别参阅 [Amazon S3 定价](https://aws.amazon.com/s3/pricing/)和 [Amazon OpenSearch Service 定价](https://aws.amazon.com/opensearch-service/pricing/)。

## 清理资源

为避免产生不必要的费用，该实现提供了在 notebook 完整运行一轮之后清理资源的选项。你可以查看 [`cleanup_infrastructure()`](https://github.com/aws-samples/responsible_ai_reduce_hallucinations_for_genai_apps/blob/main/reduce_llm_hallucinations_labs/lab2/lab2.ipynb) 方法中的说明，了解如何避免自动清理并用不同的 prompt 和数据集做实验。

资源清理的顺序如下：

- 禁用 action group。
- 删除 action group。
- 删除 alias。
- 删除 agent。
- 删除 Lambda 函数。
- 清空 S3 存储桶。
- 删除 S3 存储桶。
- 删除 [AWS Identity and Access Management（IAM）](https://aws.amazon.com/iam) 角色和策略。
- 删除向量数据库的 collection 策略。
- 删除知识库。

## 关键考量

与仅使用 Amazon Bedrock Guardrails 和 Amazon Bedrock Prompt Flows 相比，Amazon Bedrock Agents 会增加整体延迟。这是在 LLM 生成的工作流与静态或确定性工作流之间做的权衡。使用 agent 时，LLM 会利用可用的知识库、工具和 API 实时生成工作流编排。而使用 prompt flows 和 guardrails 时，工作流必须在离线阶段完成编排和设计。

在评估方面，虽然我们选择了基于 LLM 的评估框架 RAGAS，但也可以把幻觉检测 Lambda 函数中的组件替换为其他框架。

## 结论

本文演示了如何使用 Amazon Bedrock Agents、Amazon Knowledge Bases 和 RAGAS 评估指标构建自定义幻觉检测器，并通过 human-in-the-loop 进行补救。该 agentic 工作流可以通过不同的幻觉补救技术扩展到自定义用例，并提供使用自定义动作检测和缓解幻觉的灵活性。

有关创建 agent 以编排工作流的更多信息，请参阅 [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html) Agents。要了解用于 LLM 评估的多种 RAGAS 指标，请参阅 [RAGAS：入门](https://github.com/explodinggradients/ragas/blob/main/docs/getstarted/index.md)。

### 关于作者

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/09/20/shayan.png)**Shayan Ray** 是 Amazon Web Services 的应用科学家。他的研究领域涵盖自然语言相关的各个方面（例如 NLP、NLU 和 NLG）。他的工作聚焦于对话式 AI、任务导向的对话系统和基于 LLM 的 agent。他的研究成果发表在自然语言处理、个性化和强化学习方面。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/25/bharathiphoto-1.png)**Bharathi Srinivasan** 是 AWS WWSO 的生成式 AI 数据科学家，她在那里为负责任 AI 相关挑战构建解决方案。她热衷于通过解决负责任 AI 的广泛关切，从机器学习应用中创造业务价值。在为顾客构建新的 AI 体验之外，Bharathi 还喜欢写科幻小说，并用耐力运动挑战自己。
