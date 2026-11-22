---
vendor: aws_bedrock
title: Effectively use prompt caching on Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/effectively-use-prompt-caching-on-amazon-bedrock
date: 2025-04-07
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 3ac7c5a27487
---

# 在 Amazon Bedrock 上高效使用 prompt caching

prompt caching 现已在 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 上正式可用（generally available），支持 Anthropic 的 Claude 3.5 Haiku 和 Claude 3.7 Sonnet，以及 Nova Micro、Nova Lite 和 Nova Pro 模型；它通过在多次 API 调用之间缓存频繁使用的 prompt，可将响应延迟降低最多 85%、成本降低最多 90%。

借助 prompt caching，你可以标记 prompt 中需要缓存的具体连续片段（称为 *prompt 前缀*）。当带着指定 prompt 前缀发起请求时，模型会处理输入并缓存与该前缀关联的内部状态。后续请求若带有匹配的 prompt 前缀，模型就会从缓存读取，跳过处理输入 token 所需的计算步骤。这缩短了首 token 时延（TTFT），并更高效地利用硬件，使我们能把成本节省回馈给你。

本文详细介绍 Amazon Bedrock 上的 prompt caching 功能，并就如何有效使用该功能以改善延迟、节省成本提供指引。

## prompt caching 的工作原理

大型语言模型（LLM）的处理由两个主要阶段构成：输入 token 处理与输出 token 生成。Amazon Bedrock 上的 prompt caching 功能优化的是输入 token 处理阶段。

你可以先在 prompt 的相关位置标记 cache checkpoint。checkpoint 之前的整段 prompt 随即成为被缓存的 prompt 前缀。随着你发送更多带有相同 prompt 前缀（由 cache checkpoint 标记）的请求，LLM 会检查该 prompt 前缀是否已存于缓存中。如果找到匹配的前缀，LLM 就可以从缓存读取，让输入处理从上一个已缓存的前缀处继续。这省去了原本用于重新计算 prompt 前缀的时间与成本。

请注意，prompt caching 功能与模型相关。你应当查阅[支持的模型](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html#prompt-caching-models)，以及每个 cache checkpoint 最少 token 数和每个请求最多 cache checkpoint 数的详情。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-18188-image001.png)

只有前缀完全一致时才会命中缓存。要充分发挥 prompt caching 的效益，建议把指令、示例等静态内容放在 prompt 开头。动态内容（包括用户特定信息）应放在 prompt 末尾。这一原则同样适用于图像和工具，它们必须在各次请求之间保持完全一致才能启用缓存。

下图展示了缓存命中的工作方式。A、B、C、D 表示 prompt 的不同片段。A、B 和 C 被标记为 prompt 前缀。当后续请求包含相同的 A、B、C prompt 前缀时，就会发生缓存命中。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-18188-image003.png)

## 何时使用 prompt caching

对于涉及长上下文 prompt、且会在多次 API 调用中频繁复用的工作负载，推荐使用 Amazon Bedrock 上的 prompt caching。该能力可将响应延迟最多改善 85%、将推理成本最多降低 90%，因此非常适合使用重复的长输入上下文的场景。要判断 prompt caching 对你的用例是否有益，你需要估算计划缓存的 token 数量、复用频率以及请求之间的间隔时间。

以下用例非常适合使用 prompt caching：

- **与文档对话** – 在首次请求时把文档作为输入上下文缓存起来，之后每次用户查询都会更高效，从而实现更简单的架构，避免向量数据库这类更重的方案。
- **编码助手** – 在 prompt 中复用长代码文件，可实现近乎实时的行内建议，省去大量重新处理代码文件的时间。
- **Agentic 工作流** – 可以使用更长的 system prompt 来精细化 agent 行为，而不降低终端用户体验。通过缓存 system prompt 和复杂的工具定义，agentic 流程中每一步的处理时间都能减少。
- **Few-shot learning** – 需要包含大量高质量示例和复杂指令（例如客户服务或技术故障排查）的场景，可以从 prompt caching 中受益。

## 如何使用 prompt caching

在评估某个用例是否使用 prompt caching 时，关键是把给定 prompt 的组成部分划分为两类：静态且重复的部分，以及动态部分。prompt 模板应遵循下图所示的结构。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-18188-image005.png)

在一个请求内可以创建多个 cache checkpoint，但受模型特定限制约束。它应遵循同样的「静态部分、cache checkpoint、动态部分」结构，如下图所示。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-18188-image007.png)

### 用例示例

「与文档对话」这一用例（把文档放进 prompt）非常适合 prompt caching。在此示例中，prompt 的静态部分由响应格式指令和文档正文组成，动态部分是用户的查询，每次请求都会变化。

在这种场景下，prompt 的静态部分应标记为 prompt 前缀以启用 prompt caching。下面的代码片段演示如何使用 [Invoke Model API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModel.html) 实现这一做法。这里我们在请求中创建两个 cache checkpoint，一个用于指令，一个用于文档内容，如下图所示。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-18188-image008.png)

我们使用如下 prompt：

```
def chat_with_document(document, user_query):
    instructions = (
    "I will provide you with a document, followed by a question about its content. "
    "Your task is to analyze the document, extract relevant information, and provide "
    "a comprehensive answer to the question. Please follow these detailed instructions:"

    "\n\n1. Identifying Relevant Quotes:"
    "\n   - Carefully read through the entire document."
    "\n   - Identify sections of the text that are directly relevant to answering the question."
    "\n   - Select quotes that provide key information, context, or support for the answer."
    "\n   - Quotes should be concise and to the point, typically no more than 2-3 sentences each."
    "\n   - Choose a diverse range of quotes if multiple aspects of the question need to be addressed."
    "\n   - Aim to select between 2 to 5 quotes, depending on the complexity of the question."

    "\n\n2. Presenting the Quotes:"
    "\n   - List the selected quotes under the heading 'Relevant quotes:'"
    "\n   - Number each quote sequentially, starting from [1]."
    "\n   - Present each quote exactly as it appears in the original text, enclosed in quotation marks."
    "\n   - If no relevant quotes can be found, write 'No relevant quotes' instead."
    "\n   - Example format:"
    "\n     Relevant quotes:"
    "\n     [1] \"This is the first relevant quote from the document.\""
    "\n     [2] \"This is the second relevant quote from the document.\""

    "\n\n3. Formulating the Answer:"
    "\n   - Begin your answer with the heading 'Answer:' on a new line after the quotes."
    "\n   - Provide a clear, concise, and accurate answer to the question based on the information in the document."
    "\n   - Ensure your answer is comprehensive and addresses all aspects of the question."
    "\n   - Use information from the quotes to support your answer, but do not repeat them verbatim."
    "\n   - Maintain a logical flow and structure in your response."
    "\n   - Use clear and simple language, avoiding jargon unless it's necessary and explained."

    "\n\n4. Referencing Quotes in the Answer:"
    "\n   - Do not explicitly mention or introduce quotes in your answer (e.g., avoid phrases like 'According to quote [1]')."
    "\n   - Instead, add the bracketed number of the relevant quote at the end of each sentence or point that uses information from that quote."
    "\n   - If a sentence or point is supported by multiple quotes, include all relevant quote numbers."
    "\n   - Example: 'The company's revenue grew by 15% last year. [1] This growth was primarily driven by increased sales in the Asian market. [2][3]'"

    "\n\n5. Handling Uncertainty or Lack of Information:"
    "\n   - If the document does not contain enough information to fully answer the question, clearly state this in your answer."
    "\n   - Provide any partial information that is available, and explain what additional information would be needed to give a complete answer."
    "\n   - If there are multiple possible interpretations of the question or the document's content, explain this and provide answers for each interpretation if possible."

    "\n\n6. Maintaining Objectivity:"
    "\n   - Stick to the facts presented in the document. Do not include personal opinions or external information not found in the text."
    "\n   - If the document presents biased or controversial information, note this objectively in your answer without endorsing or refuting the claims."

    "\n\n7. Formatting and Style:"
    "\n   - Use clear paragraph breaks to separate different points or aspects of your answer."
    "\n   - Employ bullet points or numbered lists if it helps to organize information more clearly."
    "\n   - Ensure proper grammar, punctuation, and spelling throughout your response."
    "\n   - Maintain a professional and neutral tone throughout your answer."

    "\n\n8. Length and Depth:"
    "\n   - Provide an answer that is sufficiently detailed to address the question comprehensively."
    "\n   - However, avoid unnecessary verbosity. Aim for clarity and conciseness."
    "\n   - The length of your answer should be proportional to the complexity of the question and the amount of relevant information in the document."

    "\n\n9. Dealing with Complex or Multi-part Questions:"
    "\n   - For questions with multiple parts, address each part separately and clearly."
    "\n   - Use subheadings or numbered points to break down your answer if necessary."
    "\n   - Ensure that you've addressed all aspects of the question in your response."

    "\n\n10. Concluding the Answer:"
    "\n    - If appropriate, provide a brief conclusion that summarizes the key points of your answer."
    "\n    - If the question asks for recommendations or future implications, include these based strictly on the information provided in the document."

    "\n\nRemember, your goal is to provide a clear, accurate, and well-supported answer based solely on the content of the given document. "
    "Adhere to these instructions carefully to ensure a high-quality response that effectively addresses the user's query."
    )

    document_content =  f"Here is the document:  <document> {document} </document>"

    messages_API_body = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 4096,
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": instructions,
                    "cache_control": {
                        "type": "ephemeral"
                    }
                },
                {
                    "type": "text",
                    "text": document_content,
                    "cache_control": {
                        "type": "ephemeral"
                    }
                },
                {
                    "type": "text",
                    "text": user_query
                },
            ]
        }
    ]
    }

    response = bedrock_runtime.invoke_model(
        body=json.dumps(messages_API_body),
        modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        accept="application/json",
        contentType="application/json"
    )
    response_body = json.loads(response.get("body").read())
print(json.dumps(response_body, indent=2))    
 
 
response = requests.get("https://aws.amazon.com/blogs/aws/reduce-costs-and-latency-with-amazon-bedrock-intelligent-prompt-routing-and-prompt-caching-preview/")
blog = response.text
chat_with_document(blog, "What is the blog writing about?")
```

在上述代码片段的响应中，有一个 usage 部分，提供缓存读写方面的指标。下面是首次调用模型时的示例响应：

```
{
  "id": "msg_bdrk_01BwzJX6DBVVjUDeRqo3Z6GL",
  "type": "message",
  "role": "assistant",
  "model": "claude-3-7-sonnet-20250219”,
  "content": [
    {
      "type": "text",
      "text": "Relevant quotes:\n[1] \"Today, Amazon Bedrock has introduced in preview two capabilities that help reduce costs and latency for generative AI applications\"\n\n[2] \"Amazon Bedrock Intelligent Prompt Routing \u2013 When invoking a model, you can now use a combination of foundation models (FMs) from the same model family to help optimize for quality and cost... Intelligent Prompt Routing can reduce costs by up to 30 percent without compromising on accuracy.\"\n\n[3] \"Amazon Bedrock now supports prompt caching \u2013 You can now cache frequently used context in prompts across multiple model invocations... Prompt caching in Amazon Bedrock can reduce costs by up to 90% and latency by up to 85% for supported models.\"\n\nAnswer:\nThe article announces two new preview features for Amazon Bedrock that aim to improve cost efficiency and reduce latency in generative AI applications [1]:\n\n1. Intelligent Prompt Routing: This feature automatically routes requests between different models within the same model family based on the complexity of the prompt, choosing more cost-effective models for simpler queries while maintaining quality. This can reduce costs by up to 30% [2].\n\n2. Prompt Caching: This capability allows frequent reuse of cached context across multiple model invocations, which is particularly useful for applications that repeatedly use the same context (like document Q&A systems). This feature can reduce costs by up to 90% and improve latency by up to 85% [3].\n\nThese features are designed to help developers build more efficient and cost-effective generative AI applications while maintaining performance and quality standards."
    }
  ],
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "usage": {
    "input_tokens": 9,
    "cache_creation_input_tokens": 37209,
    "cache_read_input_tokens": 0,
    "output_tokens": 357
  }
}
```

如 `cache_creation_input_tokens` 的值所示，cache checkpoint 已成功创建，共缓存 37,209 个 token，如下图所示。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-18188-image010.png)

在后续请求中，我们可以问一个不同的问题：

```
chat_with_document(blog, "what are the use cases?")
```

prompt 的动态部分已改变，但静态部分与 prompt 前缀保持不变。可以预期后续调用会命中缓存。参见以下代码：

```
{
  "id": "msg_bdrk_01HKoDMs4Bmm9mhzCdKoQ8bQ",
  "type": "message",
  "role": "assistant",
  "model": "claude-3-7-sonnet-20250219",
  "content": [
    {
      "type": "text",
      "text": "Relevant quotes:\n[1] \"This is particularly useful for applications such as customer service assistants, where uncomplicated queries can be handled by smaller, faster, and more cost-effective models, and complex queries are routed to more capable models.\"\n\n[2] \"This is especially valuable for applications that repeatedly use the same context, such as document Q&A systems where users ask multiple questions about the same document or coding assistants that need to maintain context about code files.\"\n\n[3] \"During the preview, you can use the default prompt routers for Anthropic's Claude and Meta Llama model families.\"\n\nAnswer:\nThe document describes two main features with different use cases:\n\n1. Intelligent Prompt Routing:\n- Customer service applications where query complexity varies\n- Applications needing to balance between cost and performance\n- Systems that can benefit from using different models from the same family (Claude or Llama) based on query complexity [1][3]\n\n2. Prompt Caching:\n- Document Q&A systems where users ask multiple questions about the same document\n- Coding assistants that need to maintain context about code files\n- Applications that frequently reuse the same context in prompts [2]\n\nBoth features are designed to optimize costs and reduce latency while maintaining response quality. Prompt routing can reduce costs by up to 30% without compromising accuracy, while prompt caching can reduce costs by up to 90% and latency by up to 85% for supported models."
    }
  ],
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "usage": {
    "input_tokens": 10,
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 37209,
    "output_tokens": 324
  }
}
```

37,209 个 token 是从缓存读取的文档与指令，10 个输入 token 是用户查询，如下图所示。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-18188-image012.png)

我们把文档换成为另一篇博客文章，但指令保持不变。由于指令在请求中位于文档正文之前，可以预期指令的 prompt 前缀会命中缓存。参见以下代码：

```
response = requests.get(https://aws.amazon.com/blogs/machine-learning/enhance-conversational-ai-with-advanced-routing-techniques-with-amazon-bedrock/)
blog = response.text
chat_with_document(blog, "What is the blog writing about?")
{
  "id": "msg_bdrk_011S8zqMXzoGHABHnXX9qSjq",
  "type": "message",
  "role": "assistant",
  "model": "claude-3-7-sonnet-20250219",
  "content": [
    {
      "type": "text",
      "text": "Let me analyze this document and provide a comprehensive answer about its main topic and purpose.\n\nRelevant quotes:\n[1] \"When you're designing a security strategy for your organization, firewalls provide the first line of defense against threats. Amazon Web Services (AWS) offers AWS Network Firewall, a stateful, managed network firewall that includes intrusion detection and prevention (IDP) for your Amazon Virtual Private Cloud (VPC).\"\n\n[2] \"This blog post walks you through logging configuration best practices, discusses three common architectural patterns for Network Firewall logging, and provides guidelines for optimizing the cost of your logging solution.\"\n\n[3] \"Determining the optimal logging approach for your organization should be approached on a case-by-case basis. It involves striking a balance between your security and compliance requirements and the costs associated with implementing solutions to meet those requirements.\"\n\nAnswer:\nThis document is a technical blog post that focuses on cost considerations and logging options for AWS Network Firewall. The article aims to help organizations make informed decisions about implementing and managing their firewall logging solutions on AWS. Specifically, it:\n\n1. Explains different logging configuration practices for AWS Network Firewall [1]\n2. Discusses three main architectural patterns for handling firewall logs:\n   - Amazon S3-based solution\n   - Amazon CloudWatch-based solution\n   - Amazon Kinesis Data Firehose with OpenSearch solution\n3. Provides detailed cost analysis and comparisons of different logging approaches [3]\n4. Offers guidance on balancing security requirements with cost considerations\n\nThe primary purpose is to help AWS users understand and optimize their firewall logging strategies while managing associated costs effectively. The article serves as a practical guide for organizations looking to implement or improve their network security logging while maintaining cost efficiency [2]."
    }
  ],
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "usage": {
    "input_tokens": 9,
    "cache_creation_input_tokens": 37888,
    "cache_read_input_tokens": 1038,
    "output_tokens": 385
  }
}
```

在响应中可以看到，指令命中了 1,038 个缓存读取 token，新文档内容产生了 37,888 个缓存写入 token，如下图所示。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-18188-image014.png)

## 成本节省

发生缓存命中时，Amazon Bedrock 通过对已缓存上下文给予按 token 的折扣，把计算节省回馈给客户。要计算潜在的成本节省，你应首先通过 Amazon Bedrock 响应中的缓存写入/读取指标了解自己的 prompt caching 使用模式。然后可以用每 1,000 个输入 token 的价格（cache write）和每 1,000 个输入 token 的价格（cache read）计算潜在的成本节省。更多价格详情，请参阅 [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/)。

## 延迟基准测试

prompt caching 针对提升重复 prompt 的 TTFT 表现做了优化。prompt caching 非常适合涉及多轮交互的对话类应用，类似 chat playground 的体验。它也能让需要反复引用大文档的用例受益。

不过，对于「先是长达 2,000 token 的 system prompt，后面跟着一长串动态变化的文本」这样的工作负载，prompt caching 的效果可能较差。在这些场景下，prompt caching 的收益可能有限。

我们已在 [GitHub repo](https://github.com/aws-samples/amazon-bedrock-samples/tree/main/introduction-to-bedrock/prompt-caching) 上发布了一个 notebook，介绍如何使用 prompt caching 以及如何对它做基准测试。基准测试结果取决于用例：输入 token 数、已缓存 token 数或输出 token 数。

## Amazon Bedrock 跨区域推理

prompt caching 可以与[跨区域推理（CRIS）](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html)配合使用。跨区域推理会自动在你的地理范围内选择最优的 AWS 区域来服务推理请求，从而最大化可用资源与模型可用性。在需求高峰期，这些优化可能导致缓存写入增多。

## 指标与可观测性

对于使用 Amazon Bedrock 的应用，prompt caching 的可观测性对优化成本节省、改善延迟至关重要。通过监控关键性能指标，开发者可以获得显著的效率提升——例如把长 prompt 的 TTFT 最多降低 85%、成本最多削减 90%。这些指标至关重要，因为它们让开发者能够准确评估缓存表现，并就缓存管理做出策略性决策。

### 使用 Amazon Bedrock 监控

Amazon Bedrock 通过 API 响应的 `usage` 部分暴露缓存性能数据，让开发者可以跟踪缓存命中率、token 消耗（读与写）以及延迟改善等关键指标。利用这些洞察，团队可以有效地管理缓存策略，以提升应用响应能力并降低运营成本。

### 使用 Amazon CloudWatch 监控

[Amazon CloudWatch](https://aws.amazon.com/cloudwatch) 提供了一个健壮的平台，用于监控 AWS 服务的健康状况与性能，其中包括专为 Amazon Bedrock 模型新增的自动仪表盘。这些仪表盘可快速访问关键指标，并有助于更深入地洞察模型性能。

要创建自定义的可观测性仪表盘，请完成以下步骤：

- 在 CloudWatch 控制台中新建一个仪表盘。完整示例请参阅 [Improve visibility into Amazon Bedrock usage and performance with Amazon CloudWatch](https://aws.amazon.com/blogs/machine-learning/improve-visibility-into-amazon-bedrock-usage-and-performance-with-amazon-cloudwatch/)。
- 选择 **CloudWatch** 作为数据源，并为初始小组件类型选择 **Pie**（之后可以调整）。
- 更新指标的时间范围（例如 1 小时、3 小时或 1 天）以适配你的监控需求。
- 在 **AWS namespaces** 下选择 **Bedrock**。
- 在搜索框中输入「cache」以筛选与缓存相关的指标。
- 对于模型，找到 `anthropic.claude-3-7-sonnet-20250219-v1:0`，并同时选择 `CacheWriteInputTokenCount` 和 `CacheReadInputTokenCount`。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-18188-image016.png)

- 选择 **Create widget**，然后选择 **Save** 保存仪表盘。

以下是创建该小组件的示例 JSON 配置：

```
{
    "view": "pie",
    "metrics": [
        [ "AWS/Bedrock", "CacheReadInputTokenCount" ],
        [ ".", "CacheWriteInputTokenCount" ]
    ],
    "region": "us-west-2",
    "setPeriodToTimeRange": true
}
```

### 理解缓存命中率

分析缓存命中率需要同时观察 `CacheReadInputTokens` 和 `CacheWriteInputTokens`。在确定的时间段内对这两个指标求和，开发者就能洞悉缓存策略的效率。借助 [Amazon Bedrock pricing page](https://aws.amazon.com/bedrock/pricing/) 上公布的、随模型而异的每 1,000 个输入 token 价格（cache write）和每 1,000 个输入 token 价格（cache read），你可以估算自己用例的潜在成本节省。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-18188-image018.jpg)

## 结论

本文探讨了 Amazon Bedrock 中的 prompt caching 功能，演示了它的工作方式、何时使用以及如何有效使用。重要的是要仔细评估你的用例是否能从该功能中受益。这取决于是否周到地组织 prompt 结构、是否理解静态内容与动态内容的区别，以及是否为你的具体需求选择合适的缓存策略。通过使用 CloudWatch 指标监控缓存表现，并遵循本文概述的实现模式，你可以构建更高效、更具成本效益的 AI 应用，同时保持高性能。

有关在 Amazon Bedrock 上使用 prompt caching 的更多信息，请参阅 [Prompt caching for faster model inference](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html)。

### 关于作者

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2022/11/29/ML11626-author-sharon-227x300-1.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2022/11/29/ML11626-author-sharon-227x300-1.png)**Sharon Li** 是 Amazon Web Services（AWS）的 AI/ML 专业解决方案架构师，常驻马萨诸塞州波士顿。Sharon 热衷于利用前沿技术，处于在 AWS 云平台上开发与部署创新生成式 AI 方案的前沿。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/20/image7-1-100x100.jpeg)**Shreyas Subramanian** 是一名首席数据科学家，借助 AWS 服务使用生成式 AI 和深度学习帮助客户解决业务挑战。Shreyas 在大规模优化与机器学习方面有深厚背景，并擅长用机器学习和强化学习加速优化任务。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/06/Satveer-1.jpg)Satveer Khurpa** 是 Amazon Web Services 的 Amazon Bedrock 高级 WW 专业解决方案架构师，专注于 Amazon Bedrock 安全。在此职位上，他运用自己在云架构方面的专长，为不同行业的客户开发创新的生成式 AI 方案。Satveer 对生成式 AI 技术和安全原则的深刻理解，使他能够设计可扩展、安全且负责任的应用程序，在保持强健安全态势的同时释放新的业务机会并创造切实价值。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/09/13/ml_16764_kosta_headshot-1.png)**Kosta Belz** 是 AWS 生成式 AI 创新中心的高级应用科学家，帮助客户设计和构建生成式 AI 方案以解决关键业务问题。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/seaneich.jpeg)**Sean Eichenberger** 是 AWS 的高级产品经理。
