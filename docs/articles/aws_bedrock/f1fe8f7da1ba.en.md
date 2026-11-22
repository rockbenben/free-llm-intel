---
vendor: aws_bedrock
title: Effectively use prompt caching on Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/effectively-use-prompt-caching-on-amazon-bedrock
date: 2025-04-07
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 90b14684e863
---

# Effectively use prompt caching on Amazon Bedrock

Prompt caching, now generally available on [Amazon Bedrock](https://aws.amazon.com/bedrock/) with Anthropic’s Claude 3.5 Haiku and Claude 3.7 Sonnet, along with Nova Micro, Nova Lite, and Nova Pro models, lowers response latency by up to 85% and reduces costs up to 90% by caching frequently used prompts across multiple API calls.

With prompt caching, you can mark the specific contiguous portions of your prompts to be cached (known as a *prompt prefix*). When a request is made with the specified prompt prefix, the model processes the input and caches the internal state associated with the prefix. On subsequent requests with a matching prompt prefix, the model reads from the cache and skips the computation steps required to process the input tokens. This reduces the time to first token (TTFT) and makes more efficient use of hardware such that we can share the cost savings with you.

This post provides a detailed overview of the prompt caching feature on Amazon Bedrock and offers guidance on how to effectively use this feature to achieve improved latency and cost savings.

## How prompt caching works

Large language model (LLM) processing is made up of two primary stages: input token processing and output token generation. The prompt caching feature on Amazon Bedrock optimizes the input token processing stage.

You can begin by marking the relevant portions of your prompt with cache checkpoints. The entire section of the prompt preceding the checkpoint then becomes the cached prompt prefix. As you send more requests with the same prompt prefix, marked by the cache checkpoint, the LLM will check if the prompt prefix is already stored in the cache. If a matching prefix is found, the LLM can read from the cache, allowing the input processing to resume from the last cached prefix. This saves the time and cost that would otherwise be spent recomputing the prompt prefix.

Be advised that the prompt caching feature is model-specific. You should review the [supported models](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html#prompt-caching-models) and details on the minimum number of tokens per cache checkpoint and maximum number of cache checkpoints per request.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-18188-image001.png)

Cache hits only occur when the exact prefix matches. To fully realize the benefits of prompt caching, it’s recommended to position static content such as instructions and examples at the beginning of the prompt. Dynamic content, including user-specific information, should be placed at the end of the prompt. This principle also extends to images and tools, which must remain identical across requests in order to enable caching.

The following diagram illustrates how cache hits work. A, B, C, D represent distinct portions of the prompt. A, B and C are marked as the prompt prefix. Cache hits occur when subsequent requests contain the same A, B, C prompt prefix.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-18188-image003.png)

## When to use prompt caching

Prompt caching on Amazon Bedrock is recommended for workloads that involve long context prompts that are frequently reused across multiple API calls. This capability can significantly improve response latency by up to 85% and reduce inference costs by up to 90%, making it well-suited for applications that use repetitive, long input context. To determine if prompt caching is beneficial for your use case, you will need to estimate the number of tokens you plan to cache, the frequency of reuse, and the time between requests.

The following use cases are well-suited for prompt caching:

- **Chat with document** – By caching the document as input context on the first request, each user query becomes more efficient, enabling simpler architectures that avoid heavier solutions like vector databases.
- **Coding assistants** – Reusing long code files in prompts enables near real-time inline suggestions, eliminating much of the time spent reprocessing code files.
- **Agentic workflows** – Longer system prompts can be used to refine agent behavior without degrading the end-user experience. By caching the system prompts and complex tool definitions, the time to process each step in the agentic flow can be reduced.
- **Few-shot learning** – Including numerous high-quality examples and complex instructions, such as for customer service or technical troubleshooting, can benefit from prompt caching.

## How to use prompt caching

When evaluating a use case to use prompt caching, it’s crucial to categorize the components of a given prompt into two distinct groups: the static and repetitive portion, and the dynamic portion. The prompt template should adhere to the structure illustrated in the following figure.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-18188-image005.png)

You can create multiple cache checkpoints within a request, subject to model-specific limitations. It should follow the same static portion, cache checkpoint, dynamic portion structure, as illustrated in the following figure.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-18188-image007.png)

### Use case example

The “chat with document” use case, where the document is included in the prompt, is well-suited for prompt caching. In this example, the static portion of the prompt would comprise instructions on response formatting and the body of the document. The dynamic portion would be the user’s query, which changes with each request.

In this scenario, the static portions of the prompt should be marked as the prompt prefixes to enable prompt caching. The following code snippet demonstrates how to implement this approach using the [Invoke Model API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModel.html). Here we create two cache checkpoints in the request, one for the instructions and one for the document content, as illustrated in the following figure.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-18188-image008.png)

We use the following prompt:

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

In the response to the preceding code snippet, there is a usage section that provides metrics on the cache reads and writes. The following is the example response from the first model invocation:

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

The cache checkpoint has been successfully created with 37,209 tokens cached, as indicated by the `cache_creation_input_tokens` value, as illustrated in the following figure.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-18188-image010.png)

For the subsequent request, we can ask a different question:

```
chat_with_document(blog, "what are the use cases?")
```

The dynamic portion of the prompt has been changed, but the static portion and prompt prefixes remain the same. We can expect cache hits from the subsequent invocations. See the following code:

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

37,209 tokens are for the document and instructions read from the cache, and 10 input tokens are for the user query, as illustrated in the following figure.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-18188-image012.png)

Let’s change the document to a different blog post, but our instructions remain the same. We can expect cache hits for the instructions prompt prefix because it was positioned before the document body in our requests. See the following code:

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

In the response, we can see 1,038 cache read tokens for the instructions and 37,888 cache write tokens for the new document content, as illustrated in the following figure.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-18188-image014.png)

## Cost savings

When a cache hit happens, Amazon Bedrock passes along the compute savings to customers by giving a per-token discount on cached context. To calculate the potential cost savings, you should first understand your prompt caching usage pattern with cache write/read metrics in the Amazon Bedrock response. Then you can calculate your potential cost savings with price per 1,000 input tokens (cache write) and price per 1,000 input tokens (cache read). For more price details, see [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/).

## Latency benchmark

Prompt caching is optimized to improve the TTFT performance on repetitive prompts. Prompt caching is well-suited for conversational applications that involve multi-turn interactions, similar to chat playground experiences. It can also benefit use cases that require repeatedly referencing a large document.

However, prompt caching might be less effective for workloads that involve a lengthy 2,000-token system prompt with a long set of dynamically changing text afterwards. In such cases, the benefits of prompt caching might be limited.

We have published a notebook on how to use prompt caching and how to benchmark it in our [GitHub repo](https://github.com/aws-samples/amazon-bedrock-samples/tree/main/introduction-to-bedrock/prompt-caching) . The benchmark results depend on the use case: input token count, cached token count, or output token count.

## Amazon Bedrock cross-Region inference

Prompt caching can be used in conjunction with [cross-region inference (CRIS).](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html) Cross-region inference automatically selects the optimal AWS Region within your geography to serve your inference request, thereby maximizing available resources and model availability. At times of high demand, these optimizations may lead to increased cache writes.

## Metrics and observability

Prompt caching observability is essential for optimizing cost savings and improving latency in applications using Amazon Bedrock. By monitoring key performance metrics, developers can achieve significant efficiency improvements—such as reducing TTFT by up to 85% and cutting costs by up to 90% for lengthy prompts. These metrics are pivotal because they enable developers to assess cache performance accurately and make strategic decisions regarding cache management.

### Monitoring with Amazon Bedrock

Amazon Bedrock exposes cache performance data through the API response’s `usage` section, allowing developers to track essential metrics such as cache hit rates, token consumption (both read and write), and latency improvements. By using these insights, teams can effectively manage caching strategies to enhance application responsiveness and reduce operational costs.

### Monitoring with Amazon CloudWatch

[Amazon CloudWatch](https://aws.amazon.com/cloudwatch) provides a robust platform for monitoring the health and performance of AWS services, including new automatic dashboards tailored specifically for Amazon Bedrock models. These dashboards offer quick access to key metrics and facilitate deeper insights into model performance.

To create custom observability dashboards, complete the following steps:

- On the CloudWatch console, create a new dashboard. For a full example, see [Improve visibility into Amazon Bedrock usage and performance with Amazon CloudWatch](https://aws.amazon.com/blogs/machine-learning/improve-visibility-into-amazon-bedrock-usage-and-performance-with-amazon-cloudwatch/).
- Choose **CloudWatch** as your data source and select **Pie** for the initial widget type (this can be adjusted later).
- Update the time range for metrics (such as 1 hour, 3 hours, or 1 day) to suit your monitoring needs.
- Select **Bedrock** under **AWS namespaces**.
- Enter “cache” in the search box to filter cache-related metrics.
- For the model, locate `anthropic.claude-3-7-sonnet-20250219-v1:0`, and select both `CacheWriteInputTokenCount` and `CacheReadInputTokenCount`.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-18188-image016.png)

- Choose **Create widget** and then **Save** to save your dashboard.

The following is a sample JSON configuration for creating this widget:

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

### Understanding cache hit rates

Analyzing cache hit rates involves observing both `CacheReadInputTokens` and `CacheWriteInputTokens`. By summing these metrics over a defined period, developers can gain insights into the efficiency of the caching strategies. With the published pricing for the model-specific price per 1,000 input tokens (cache write) and price per 1,000 input tokens (cache read) on the [Amazon Bedrock pricing page](https://aws.amazon.com/bedrock/pricing/), you can estimate the potential cost savings for your specific use case.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/ML-18188-image018.jpg)

## Conclusion

This post explored the prompt caching feature in Amazon Bedrock, demonstrating how it works, when to use it, and how to use it effectively. It’s important to carefully evaluate whether your use case will benefit from this feature. It depends on thoughtful prompt structuring, understanding the distinction between static and dynamic content, and selecting appropriate caching strategies for your specific needs. By using CloudWatch metrics to monitor cache performance and following the implementation patterns outlined in this post, you can build more efficient and cost-effective AI applications while maintaining high performance.

For more information about working with prompt caching on Amazon Bedrock, see [Prompt caching for faster model inference](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html).

### About the authors

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2022/11/29/ML11626-author-sharon-227x300-1.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2022/11/29/ML11626-author-sharon-227x300-1.png)**Sharon Li** is an AI/ML Specialist Solutions Architect at Amazon Web Services (AWS) based in Boston, Massachusetts. With a passion for leveraging cutting-edge technology, Sharon is at the forefront of developing and deploying innovative generative AI solutions on the AWS cloud platform.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/20/image7-1-100x100.jpeg)**Shreyas Subramanian** is a Principal Data Scientist and helps customers by using generative AI and deep learning to solve their business challenges using AWS services. Shreyas has a background in large-scale optimization and ML and in the use of ML and reinforcement learning for accelerating optimization tasks.

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/06/Satveer-1.jpg)Satveer Khurpa** is a Sr. WW Specialist Solutions Architect, Amazon Bedrock at Amazon Web Services, specializing in Amazon Bedrock security. In this role, he uses his expertise in cloud-based architectures to develop innovative generative AI solutions for clients across diverse industries. Satveer’s deep understanding of generative AI technologies and security principles allows him to design scalable, secure, and responsible applications that unlock new business opportunities and drive tangible value while maintaining robust security postures.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/09/13/ml_16764_kosta_headshot-1.png)**Kosta Belz** is a Senior Applied Scientist in the AWS Generative AI Innovation Center, where he helps customers design and build generative AI solutions to solve key business problems.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/04/04/seaneich.jpeg)**Sean Eichenberger** is a Sr Product Manager at AWS.
