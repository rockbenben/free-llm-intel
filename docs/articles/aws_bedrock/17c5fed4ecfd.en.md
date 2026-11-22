---
vendor: aws_bedrock
title: Introducing Amazon Bedrock cross-Region inference for Claude Sonnet 4.5 and Haiku 4.5 in Japan and Australia
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/introducing-amazon-bedrock-cross-region-inference-for-claude-sonnet-4-5-and-haiku-4-5-in-japan-and-australia
date: 2025-10-31
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: fc3a91451f24
---

# Introducing Amazon Bedrock cross-Region inference for Claude Sonnet 4.5 and Haiku 4.5 in Japan and Australia

*This post is co-written with Gareth Jones from Anthropic.*

こんにちは, G’day.

The recent launch of [Anthropic’s Claude Sonnet 4.5](https://www.anthropic.com/news/claude-sonnet-4-5) and [Claude Haiku 4.5](https://aws.amazon.com/about-aws/whats-new/2025/10/claude-4-5-haiku-anthropic-amazon-bedrock/), now available on [Amazon Bedrock](https://aws.amazon.com/bedrock/), marks a significant leap forward in generative AI models. These state-of-the-art models excel at complex agentic tasks, coding, and enterprise workloads, offering enhanced capabilities to developers. Along with the new models, we are thrilled to announce that customers in Japan and Australia can now access **Anthropic Claude Sonnet 4.5** and **Anthropic Claude Haiku 4.5** in Amazon Bedrock while processing the data in their specific geography by using Cross-Region inference (CRIS). This can be useful when customers need to meet the requirements to process data locally.

This post will explore the new geographic-specific cross-Region inference profile in Japan and Australia for Claude Sonnet 4.5 and Claude Haiku 4.5. We will delve into the details of these geographic-specific CRIS profiles, provide guidance for migrating from older models, and show you how to get started with this new capability to unlock the full potential of these models for your generative AI applications.

## Japan and Australia Cross-Region inference

With Japan and Australia cross-Region inference you can make calls to Anthropic Claude Sonnet 4.5 or Claude Haiku 4.5 within your local geography. By using CRIS Amazon Bedrock processes the inference requests within the geographic boundaries, either Japan or Australia, through the entire inference request lifecycle.

**How Cross-Region inference works**

[Cross-Region inference in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html) operates through the [AWS Global Network](https://aws.amazon.com/about-aws/global-infrastructure/global-network/) with end-to-end encryption for data in transit and at rest. When a customer submits an inference request in the source AWS Region, Amazon Bedrock automatically evaluates available capacity in each potential destination Region and routes their request to the optimal destination Region. The traffic flows exclusively over the AWS Global Network without traversing the public internet between Regions listed as destination for your source Region, using the AWS internal service-to-service communication patterns. Following the same design, the Japan and Australia GEO CRIS use the secure AWS Global Network to automatically route traffic between Regions within their respective geographies – between Tokyo and Osaka in Japan, and between Sydney and Melbourne in Australia. CRIS uses intelligent routing that distributes traffic dynamically across multiple Regions within the same geography, without requiring manual user configuration or intervention.

**Cross-Region inference configuration**

The CRIS configurations for Japan and Australia are described in the following tables.

**Japan CRIS: **For organizations operating within Japan, the CRIS system provides routing between Tokyo and Osaka Regions.

| **Source Region** | **Destination Region** | **Description** |
| --- | --- | --- |
| ap-northeast-1 (Tokyo) | ap-northeast-1 (Tokyo)ap-northeast-3 (Osaka) | Requests from the Tokyo Region can be automatically routed to either Tokyo or Osaka Regions. |
| ap-northeast-3 (Osaka) | ap-northeast-1 (Tokyo)ap-northeast-3 (Osaka) | Requests from the Osaka Region can be automatically routed to either Tokyo or Osaka Regions. |

**Australia CRIS: **For organizations operating within Australia, the CRIS system provides routing between Sydney and Melbourne Regions.

| **Source Region** | **Destination Region** | **Description** |
| --- | --- | --- |
| ap-southeast-2 (Sydney) | ap-southeast-2 (Sydney)ap-southeast-4 (Melbourne) | Requests from the Sydney Region can be automatically routed to either Sydney or Melbourne Regions. |
| ap-southeast-4 (Melbourne) | ap-southeast-2 (Sydney)ap-southeast-4 (Melbourne) | Requests from the Melbourne Region can be automatically routed to either Sydney or Melbourne Regions. |

**Note:** A list of destination Regions is listed for each source Region within your [inference profile](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html).

## Getting started

To get started with Australia or Japan CRIS, follow these steps using Amazon Bedrock [inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-use.html).

- **Configure IAM Permission: **Verify your IAM role or user has the necessary permissions to invoke Amazon Bedrock models using a cross-Region inference profile. To allow an IAM user or role to invoke a geographic-specific cross-Region inference profile, you can use the following example policy.The first statement in the policy allows Amazon Bedrock `InvokeModel` API access to the GEO specific cross-Region inference profile resource for requests originating from the nominated Region. GEO specific inference profiles are prefix by the Region code (“**jp**” for Japan and “**au**” for Australia). In this example, the nominated requesting Region is **ap-northeast-1 (Tokyo)** and the inference profile is `jp.anthropic.claude-sonnet-4-5-20250929-v1:0`.The second statement allows the GEO specific cross-Region inference profile to access and invoke the matching foundation models in the Region where the GEO specific inference profile will route to. In this example, the Japan cross-Region inference profiles can route to either **ap-northeast-1** (Tokyo) or **ap-northeast-3** (Osaka).  `{ "Version":"2012-10-17", "Statement": [ { "Effect": "Allow", "Action": [ "bedrock:InvokeModel*" ], "Resource": [ "arn:aws:bedrock:ap-northeast-1:<your-account-id>:inference-profile/jp.anthropic.claude-sonnet-4-5-20250929-v1:0" ] }, { "Effect": "Allow", "Action": [ "bedrock:InvokeModel*" ], "Resource": [ "arn:aws:bedrock:ap-northeast-1::foundation-model/anthropic.claude-sonnet-4-5-20250929-v1:0", "arn:aws:bedrock:ap-northeast-3::foundation-model/anthropic.claude-sonnet-4-5-20250929-v1:0" ], "Condition": { "StringLike": { "bedrock:InferenceProfileArn": "arn:aws:bedrock:ap-northeast-1:<your-account-id>:inference-profile/jp.anthropic.claude-sonnet-4-5-20250929-v1:0" } } } ] }`
- **Use cross-Region inference profile: **Configure your application to use the relevant inference profile ID. This works for both the `InvokeModel` and `Converse` APIs.

**Inference Profiles for Anthropic Claude Sonnet 4.5**

| **Region** | **Inference Profile ID** |
| --- | --- |
| Australia | **au**.anthropic.claude-sonnet-4-5-20250929-v1:0 |
| Japan | **jp**.anthropic.claude-sonnet-4-5-20250929-v1:0 |

**Inference Profiles for Anthropic Claude Haiku 4.5**

| **Region** | **Inference Profile ID** |
| --- | --- |
| Australia | **au**.anthropic.claude-haiku-4-5-20251001-v1:0 |
| Japan | **jp**.anthropic.claude-haiku-4-5-20251001-v1:0 |

**Example Code**

Using the Converse API (Python) with Japan CRIS inference profile.

```
import boto3

# Initialize Bedrock Runtime client
bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="ap-northeast-1"  # Your originating Region
)

# Define the inference profile ID
inference_profile_id = "jp.anthropic.claude-sonnet-4-5-20250929-v1:0"

# Prepare the conversation
response = bedrock_runtime.converse(
    modelId=inference_profile_id,
    messages=[
        {
            "role": "user",
            "content": [{"text": "What is Amazon Bedrock?"}]
        }
    ],
    inferenceConfig={
        "maxTokens": 512,
        "temperature": 0.7
    }
)

# Print the response
print(f"Response: {response['output']['message']['content'][0]['text']}")
```

## Quota management

When using CRIS, it is important to understand how quotas are managed. For geographic-specific CRIS, quota management is performed at the source Region level. This means that quota increases requested from the source Region will only apply to requests originating from that Region. For example, if you request a quota increase from the Tokyo (ap-northeast-1) Region, **it will only apply to requests that originate** from the Tokyo Region. Similarly, quota increase requests from Osaka only apply to requests originating from Osaka. When requesting a quota increase, organizations should consider their regional usage patterns and request increases in the appropriate source Regions through the [AWS Service Quotas console](https://console.aws.amazon.com/servicequotas/home). This Region-specific quota management allows for more granular control over resource allocation while maintaining data local processing requirements.

### Requesting a quota increase

For requesting quota increases for CRIS in Japan and Australia, organizations should use the [AWS Service Quotas console](https://console.aws.amazon.com/servicequotas/home) in their respective source Regions (Tokyo/Osaka for Japan, and Sydney/Melbourne for Australia). Organizations and customers can search for specific quotas related to Claude Sonnet 4.5 or Claude Haiku 4.5 model inference tokens (per day and per minute) and submit increase requests based on their workload requirements in the specific Region.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/30/ML-19916-image-1.jpeg)

### Quota management best practices

To manage your quotas, follow these best practices:

- **Request increase proactively**: Each organization receives default quota allocations based on their account history and usage patterns. These quotas are measured in tokens per minute (TPM) and requests per minute (RPM). For Claude Sonnet 4.5 and Claude Haiku 4.5, quotas typically start at conservative levels and can be increased based on demonstrated need and usage patterns. If you anticipate high usage, request quota increase through the AWS Service Quotas console before your deployment.
- **Monitor utilization**: Implement monitoring of your quota usage to minimize the chances of reaching quota limits to help prevent service interruptions and optimize resource allocation. AWS provides CloudWatch metrics that track quota utilization in real-time, allowing organizations to set up alerts when usage approaches defined thresholds. The monitoring system should track both current usage and historical patterns to identify trends and predict future quota needs. This data is essential for planning quota increase requests and optimizing application behavior to work within available limits. Organizations should also monitor quota usage across different time periods to identify peak usage patterns and plan accordingly.
- **Test at scale**: Before production deployment, conduct load testing to understand your quota requirements under realistic conditions. Testing at scale requires establishing realistic scenarios that mirror production traffic patterns, including peak usage periods and concurrent user loads. Implement progressive load testing while monitoring response times, error rates, and quota utilization.

**Important**: When calculating your required quota increase, you need to take into account for the [burndown rate](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-token-burndown.html), defined as the rate at which input and output tokens are converted into token quota usage for the throttling system. The following models have a **5x burn down rate for output tokens (1 output token consumes 5 tokens from your quotas):**

- Anthropic Claude Opus 4
- Anthropic Claude Sonnet 4.5
- Anthropic Claude Sonnet 4
- Anthropic Claude 3.7 Sonnet

For other models, the burndown rate is **1:1** (1 output token consumes 1 token from your quota). For input tokens, the token to quota ratio is 1:1. The calculation for the total number of tokens per request is as follows:

`Input token count + Cache write input tokens + (Output token count x Burndown rate)`

## Migrating from Claude 3.5 to Claude 4.5

Organizations currently using Claude Sonnet 3.5 (v1 and v2) and Claude Haiku 3.5 models should plan their migration to Claude Sonnet 4.5 and Claude Haiku 4.5 respectively. Claude Sonnet 4.5 and Haiku 4.5 are hybrid reasoning models that represents a substantial advancement over its predecessors. They feature [advanced capabilities](https://aws.amazon.com/blogs/aws/introducing-claude-sonnet-4-5-in-amazon-bedrock-anthropics-most-intelligent-model-best-for-coding-and-complex-agents/) in tool handling with improvements in memory management and context processing. This migration presents an opportunity to use enhanced capabilities while maintaining compliance with data local processing requirements through CRIS.

**Key Migration Considerations**

The transition from Claude 3.5 to 4.5 involves several critical factors beyond simple model replacement.

- Performance benchmarking should be your first priority, as Claude 4.5 demonstrates significant improvements in agentic tasks, coding capabilities, and enterprise workloads compared to its predecessors. Organizations should establish standardized benchmarks specific to their use cases to make sure the new model meets or exceeds current performance requirements.
- Claude 4.5 introduces several advanced technical capabilities. The enhanced context processing enables more sophisticated prompt optimization, requiring organizations to refine their existing prompts to fully leverage the model’s capabilities. The model supports more complex tool integration patterns and demonstrates improved performance in multi-modal tasks.
- Cost optimization represents another crucial consideration. Organizations should conduct thorough cost-benefit analysis including potential quota increases and capacity planning requirements.

For more technical implementation guidance, organizations should reference the AWS blog post, [Migrate from Anthropic’s Claude 3.5 Sonnet to Claude 4 Sonnet on Amazon Bedrock](https://aws.amazon.com/blogs/machine-learning/migrate-from-anthropics-claude-3-5-sonnet-to-claude-4-sonnet-on-amazon-bedrock/), which provides essential best practices that are also valid for the migration to the new Claude Sonnet 4.5 model. Additionally, Anthropic’s[ migration documentation](https://docs.claude.com/en/docs/about-claude/models/migrating-to-claude-4) offers model-specific optimization strategies and considerations for transitioning to Claude 4.5 models.

Given the accelerated pace of generative AI model evolution, organizations should adopt agile migration processes. Industry standards now expect model migrations every six to twelve months, making it essential to develop systematic approaches rather than over-optimizing for specific model versions.

## Choosing between Global Cross-Region inference or GEO Cross-Region inference

Amazon Bedrock offers two types of cross-Region inference profile to help you scale AI workflows during high demand. While both automatically distribute traffic across multiple Regions, they differ in their geographical scope and pricing models.

**For customers who need to process data locally within specific geographical boundaries**, GEO CRIS is the recommended option, as it makes sure inference processing stays within the geography boundaries of the specified GEO.

**For customers without data residency or cross-GEO constraints**, [Global CRIS](https://aws.amazon.com/blogs/machine-learning/unlock-global-ai-inference-scalability-using-new-global-cross-region-inference-on-amazon-bedrock-with-anthropics-claude-sonnet-4-5/) scales and routes to supported AWS commercial Regions for customers who need higher throughput at a lower price for Claude 4.5 models compared to GEO CRIS.

## Conclusion

In this post, we introduced the availability of Anthropic’s Claude Sonnet 4.5 and Claude Haiku 4.5 on Amazon Bedrock with cross-Region inference capabilities for Japan and Australia. We discussed how organizations can harness advanced AI capabilities while adhering to local data processing requirements, making sure the inference requests remain within geographical boundaries. This new feature is recommended for sectors such as financial institutions, healthcare providers, and government agencies handling sensitive data. We also provided guidance on how to get started and covered quota management strategies, as well as migration guidance from older Claude models to Claude 4.5 models. To understand more of the pricing for Claude Sonnet 4.5 and Claude Haiku 4.5 on Bedrock, please refer to [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing).

Through this capability, organizations can now confidently implement production applications with Claude Sonnet 4.5 and Claude Haiku 4.5 that not only meet their performance requirements but also the local data processing requirements, marking a significant advancement in the responsible deployment of AI technology in these countries.

### About the authors

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/03/derrchoo-100x133.jpg)Derrick Choo** is a Senior Solutions Architect at AWS who accelerates enterprise digital transformation through cloud adoption, AI/ML, and generative AI solutions. He specializes in full-stack development and ML, designing end-to-end solutions spanning frontend interfaces, IoT applications, data integrations, and ML models, with a particular focus on computer vision and multi-modal systems.

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/03/mmelli-100x133.jpg)Melanie Li**, PhD, is a Senior Generative AI Specialist Solutions Architect at AWS based in Sydney, Australia, where her focus is on working with customers to build solutions using state-of-the-art AI/ML tools. She has been actively involved in multiple generative AI initiatives across APJ, harnessing the power of LLMs. Prior to joining AWS, Dr. Li held data science roles in the financial and retail industries.

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/03/trikande-100x133.jpg)Saurabh Trikande** is a Senior Product Manager for Amazon Bedrock and Amazon SageMaker Inference. He is passionate about working with customers and partners, motivated by the goal of democratizing AI. He focuses on core challenges related to deploying complex AI applications, inference with multi-tenant models, cost optimizations, and making the deployment of generative AI models more accessible. In his spare time, Saurabh enjoys hiking, learning about innovative technologies, following TechCrunch, and spending time with his family.

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/03/jldean-100x133.jpg)Jared Dean **is a Principal AI/ML Solutions Architect at AWS. Jared works with customers across industries to develop machine learning applications that improve efficiency. He is interested in all things AI, technology, and BBQ.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/30/chiaos.jpeg)**Stephanie Chiao **is a Generative AI GTM & Capacity Lead for AWS in Asia Pacific and Japan. She champions the voice of the customer to drive the roadmap for AWS Generative AI services including Amazon Bedrock and Amazon EC2 GPUs across AWS Regions in APJ. Outside of work, she enjoys using Generative AI creative models to make portraits of her shiba inu and cat.

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/30/220720AWS2733_125x125.png)Kazuki Motohashi**, Ph.D. is an AI/ML GTM Specialist Solutions Architect at AWS Japan. He has been working in the AI/ML field for more than 8 years and currently supports Japanese enterprise customers and partners who utilize AWS generative AI/ML services in their businesses. He’s seeking time to play Final Fantasy Tactics, but hasn’t even started it yet.

**![Gareth](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/10/gareth_ml19602-100x88.png)Gareth Jones** is a Product Manager at Anthropic focused on the Claude API. His work includes collaboration with AWS on Amazon Bedrock to make Claude widely accessible to developers.
