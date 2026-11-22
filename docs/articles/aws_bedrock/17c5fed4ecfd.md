---
vendor: aws_bedrock
title: Introducing Amazon Bedrock cross-Region inference for Claude Sonnet 4.5 and Haiku 4.5 in Japan and Australia
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/introducing-amazon-bedrock-cross-region-inference-for-claude-sonnet-4-5-and-haiku-4-5-in-japan-and-australia
date: 2025-10-31
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 4fb1b2a8ebec
---

# 在日本和澳大利亚推出面向 Claude Sonnet 4.5 与 Haiku 4.5 的 Amazon Bedrock 跨区域推理

*本文由 Anthropic 的 Gareth Jones 共同撰写。*

こんにちは, G’day.

近期推出的 [Anthropic 的 Claude Sonnet 4.5](https://www.anthropic.com/news/claude-sonnet-4-5) 和 [Claude Haiku 4.5](https://aws.amazon.com/about-aws/whats-new/2025/10/claude-4-5-haiku-anthropic-amazon-bedrock/) 现已在 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 上线，标志着生成式 AI 模型的一次重大飞跃。这些先进的模型擅长复杂的 agentic 任务、编码和企业工作负载，为开发者提供更强的能力。伴随新模型，我们很高兴宣布，日本和澳大利亚的客户现在可以在 Amazon Bedrock 中访问 **Anthropic Claude Sonnet 4.5** 和 **Anthropic Claude Haiku 4.5**，同时通过跨区域推理（Cross-Region inference，CRIS）在其特定地域内处理数据。当客户需要满足本地数据处理要求时，这非常有用。

本文将探讨面向 Claude Sonnet 4.5 和 Claude Haiku 4.5、在日本和澳大利亚新推出的地域专用跨区域推理配置。我们将深入研究这些地域专用 CRIS 配置的细节，提供从旧模型迁移的指导，并展示如何开始使用这项新能力，为你的生成式 AI 应用释放这些模型的全部潜力。

## 日本和澳大利亚的跨区域推理

借助日本和澳大利亚的跨区域推理，你可以在本地地域内调用 Anthropic Claude Sonnet 4.5 或 Claude Haiku 4.5。通过使用 CRIS，Amazon Bedrock 会在整个推理请求生命周期中，在日本或澳大利亚的地域边界内处理推理请求。

**跨区域推理的工作原理**

[Amazon Bedrock 中的跨区域推理](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html)通过 [AWS Global Network](https://aws.amazon.com/about-aws/global-infrastructure/global-network/) 运行，对传输中和静态存储的数据进行端到端加密。当客户在源 AWS 区域提交推理请求时，Amazon Bedrock 会自动评估每个潜在目标区域的可用容量，并将请求路由到最佳目标区域。流量完全经由 AWS Global Network 传输，使用 AWS 内部的服务到服务通信模式，不会在源区域所列的目标区域之间穿越公共互联网。遵循同样的设计，日本和澳大利亚的 GEO CRIS 使用安全的 AWS Global Network，在其各自地域内的区域之间自动路由流量——日本的东京与大阪之间，以及澳大利亚的悉尼与墨尔本之间。CRIS 采用智能路由，在同一地域内的多个区域之间动态分配流量，无需用户手动配置或干预。

**跨区域推理配置**

日本和澳大利亚的 CRIS 配置如下表所述。

**日本 CRIS：**对于在日本运营的组织，CRIS 系统在东京和大阪区域之间提供路由。

| **源区域** | **目标区域** | **描述** |
| --- | --- | --- |
| ap-northeast-1 (Tokyo) | ap-northeast-1 (Tokyo)ap-northeast-3 (Osaka) | 来自东京区域的请求可自动路由到东京或大阪区域。 |
| ap-northeast-3 (Osaka) | ap-northeast-1 (Tokyo)ap-northeast-3 (Osaka) | 来自大阪区域的请求可自动路由到东京或大阪区域。 |

**澳大利亚 CRIS：**对于在澳大利亚运营的组织，CRIS 系统在悉尼和墨尔本区域之间提供路由。

| **源区域** | **目标区域** | **描述** |
| --- | --- | --- |
| ap-southeast-2 (Sydney) | ap-southeast-2 (Sydney)ap-southeast-4 (Melbourne) | 来自悉尼区域的请求可自动路由到悉尼或墨尔本区域。 |
| ap-southeast-4 (Melbourne) | ap-southeast-2 (Sydney)ap-southeast-4 (Melbourne) | 来自墨尔本区域的请求可自动路由到悉尼或墨尔本区域。 |

**注意：**在你的 [推理配置](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html) 中，每个源区域都会列出目标区域列表。

## 开始使用

要开始使用澳大利亚或日本 CRIS，请使用 Amazon Bedrock [推理配置](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-use.html) 按以下步骤操作。

- **配置 IAM 权限：**验证你的 IAM 角色或用户是否具备使用跨区域推理配置调用 Amazon Bedrock 模型的必要权限。要允许 IAM 用户或角色调用地域专用跨区域推理配置，你可以使用以下示例策略。策略中的第一条语句允许 Amazon Bedrock 的 `InvokeModel` API 对源自指定区域的请求访问 GEO 专用跨区域推理配置资源。GEO 专用推理配置以区域代码为前缀（日本为“**jp**”，澳大利亚为“**au**”）。在本例中，指定的请求区域是 **ap-northeast-1 (Tokyo)**，推理配置为 `jp.anthropic.claude-sonnet-4-5-20250929-v1:0`。第二条语句允许 GEO 专用跨区域推理配置访问并调用 GEO 专用推理配置将路由到的区域中的相应基础模型。在本例中，日本跨区域推理配置可以路由到 **ap-northeast-1**（东京）或 **ap-northeast-3**（大阪）。  `{ "Version":"2012-10-17", "Statement": [ { "Effect": "Allow", "Action": [ "bedrock:InvokeModel*" ], "Resource": [ "arn:aws:bedrock:ap-northeast-1:<your-account-id>:inference-profile/jp.anthropic.claude-sonnet-4-5-20250929-v1:0" ] }, { "Effect": "Allow", "Action": [ "bedrock:InvokeModel*" ], "Resource": [ "arn:aws:bedrock:ap-northeast-1::foundation-model/anthropic.claude-sonnet-4-5-20250929-v1:0", "arn:aws:bedrock:ap-northeast-3::foundation-model/anthropic.claude-sonnet-4-5-20250929-v1:0" ], "Condition": { "StringLike": { "bedrock:InferenceProfileArn": "arn:aws:bedrock:ap-northeast-1:<your-account-id>:inference-profile/jp.anthropic.claude-sonnet-4-5-20250929-v1:0" } } } ] }`
- **使用跨区域推理配置：**配置你的应用使用相应的推理配置 ID。这对 `InvokeModel` 和 `Converse` API 都适用。

**Anthropic Claude Sonnet 4.5 的推理配置**

| **区域** | **推理配置 ID** |
| --- | --- |
| Australia | **au**.anthropic.claude-sonnet-4-5-20250929-v1:0 |
| Japan | **jp**.anthropic.claude-sonnet-4-5-20250929-v1:0 |

**Anthropic Claude Haiku 4.5 的推理配置**

| **区域** | **推理配置 ID** |
| --- | --- |
| Australia | **au**.anthropic.claude-haiku-4-5-20251001-v1:0 |
| Japan | **jp**.anthropic.claude-haiku-4-5-20251001-v1:0 |

**示例代码**

使用 Converse API（Python）搭配日本 CRIS 推理配置。

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

## 配额管理

使用 CRIS 时，了解配额如何管理非常重要。对于地域专用 CRIS，配额管理在源区域层级执行。这意味着从源区域申请的配额提升仅适用于源自该区域的请求。例如，如果你从东京（ap-northeast-1）区域申请配额提升，**它将仅适用于源自**东京区域的请求。同样，从大阪提出的配额提升申请仅适用于源自大阪的请求。申请配额提升时，组织应考虑自身的区域使用模式，并通过 [AWS Service Quotas console](https://console.aws.amazon.com/servicequotas/home) 在相应的源区域提出提升申请。这种按区域划分的配额管理，能够在满足本地数据处理要求的同时，对资源分配进行更精细的控制。

### 申请配额提升

要为日本和澳大利亚的 CRIS 申请配额提升，组织应在各自的源区域（日本为东京/大阪，澳大利亚为悉尼/墨尔本）使用 [AWS Service Quotas console](https://console.aws.amazon.com/servicequotas/home)。组织和客户可以搜索与 Claude Sonnet 4.5 或 Claude Haiku 4.5 模型推理 token（按天和按分钟）相关的具体配额，并根据特定区域的工作负载需求提交提升申请。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/30/ML-19916-image-1.jpeg)

### 配额管理最佳实践

要管理你的配额，请遵循以下最佳实践：

- **主动申请提升**：每个组织都会根据其账户历史和使用模式获得默认配额。这些配额以每分钟 token 数（TPM）和每分钟请求数（RPM）衡量。对于 Claude Sonnet 4.5 和 Claude Haiku 4.5，配额通常以保守水平起步，并可根据已证明的需求和使用模式提升。如果你预计使用量较高，请在部署前通过 AWS Service Quotas 控制台申请配额提升。
- **监控利用率**：实施对配额使用情况的监控，尽量降低触及配额上限的可能性，以帮助防止服务中断并优化资源分配。AWS 提供 CloudWatch 指标来实时跟踪配额利用率，使组织能够在使用量接近设定阈值时设置告警。监控系统应同时跟踪当前使用情况和历史模式，以识别趋势并预测未来的配额需求。这些数据对于规划配额提升申请以及优化应用行为以在可用限额内运行至关重要。组织还应跨不同时间段监控配额使用情况，以识别峰值使用模式并据此规划。
- **大规模测试**：在生产部署之前，进行负载测试，以了解真实条件下的配额需求。大规模测试需要建立能够反映生产流量模式的真实场景，包括峰值使用时段和并发用户负载。实施渐进式负载测试，同时监控响应时间、错误率和配额利用率。

**重要提示**：在计算所需的配额提升量时，你需要考虑 [burndown rate](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-token-burndown.html)，其定义为输入和输出 token 被转换为限流系统的 token 配额用量的比率。以下模型的**输出 token 采用 5 倍消耗率（1 个输出 token 从你的配额中消耗 5 个 token）：**

- Anthropic Claude Opus 4
- Anthropic Claude Sonnet 4.5
- Anthropic Claude Sonnet 4
- Anthropic Claude 3.7 Sonnet

对于其他模型，消耗率为 **1:1**（1 个输出 token 从你的配额中消耗 1 个 token）。对于输入 token，token 与配额的比率为 1:1。每次请求的总 token 数计算如下：

`Input token count + Cache write input tokens + (Output token count x Burndown rate)`

## 从 Claude 3.5 迁移到 Claude 4.5

目前使用 Claude Sonnet 3.5（v1 和 v2）和 Claude Haiku 3.5 模型的组织，应分别规划向 Claude Sonnet 4.5 和 Claude Haiku 4.5 的迁移。Claude Sonnet 4.5 和 Haiku 4.5 是混合推理模型，相较前代有重大进步。它们在工具处理方面具备[高级能力](https://aws.amazon.com/blogs/aws/introducing-claude-sonnet-4-5-in-amazon-bedrock-anthropics-most-intelligent-model-best-for-coding-and-complex-agents/)，并在记忆管理和上下文处理上有所改进。这次迁移提供了一个机会：在通过 CRIS 保持符合本地数据处理要求的同时，使用增强的能力。

**关键迁移考量**

从 Claude 3.5 过渡到 4.5，除了简单的模型替换之外，还涉及若干关键因素。

- 性能基准测试应是你的首要任务，因为与前代相比，Claude 4.5 在 agentic 任务、编码能力和企业工作负载方面都有显著改进。组织应建立针对自身用例的标准化基准，以确保新模型达到或超过当前的性能要求。
- Claude 4.5 引入了多项高级技术能力。增强的上下文处理支持更复杂的 prompt 优化，这要求组织改进现有 prompt，以充分利用模型的能力。该模型支持更复杂的工具集成模式，并在多模态任务中展现出更好的性能。
- 成本优化是另一个关键考量。组织应进行全面的成本效益分析，包括潜在的配额提升和容量规划需求。

有关更多技术实现指导，组织应参考 AWS 博客文章[从 Anthropic 的 Claude 3.5 Sonnet 迁移到 Amazon Bedrock 上的 Claude 4 Sonnet](https://aws.amazon.com/blogs/machine-learning/migrate-from-anthropics-claude-3-5-sonnet-to-claude-4-sonnet-on-amazon-bedrock/)，其中提供的重要最佳实践同样适用于向新 Claude Sonnet 4.5 模型的迁移。此外，Anthropic 的[迁移文档](https://docs.claude.com/en/docs/about-claude/models/migrating-to-claude-4)提供了针对特定模型的优化策略，以及向 Claude 4.5 模型过渡时的注意事项。

鉴于生成式 AI 模型演进速度加快，组织应采用敏捷的迁移流程。如今行业标准预期每六到十二个月进行一次模型迁移，因此有必要建立系统化的方法，而不是针对特定模型版本过度优化。

## 在全球跨区域推理与 GEO 跨区域推理之间选择

Amazon Bedrock 提供两种跨区域推理配置，帮助你在高需求期间扩展 AI 工作流。虽然两者都会自动跨多个区域分配流量，但它们在地理范围和定价模式上有所不同。

**对于需要在特定地理边界内本地处理数据的客户**，推荐选择 GEO CRIS，因为它可确保推理处理始终停留在指定 GEO 的地域边界之内。

**对于没有数据驻留或跨 GEO 限制的客户**，与 GEO CRIS 相比，[Global CRIS](https://aws.amazon.com/blogs/machine-learning/unlock-global-ai-inference-scalability-using-new-global-cross-region-inference-on-amazon-bedrock-with-anthropics-claude-sonnet-4-5/) 可面向需要更高吞吐量、更低价格的 Claude 4.5 模型客户，扩展并路由到受支持的 AWS 商业区域。

## 结论

在本文中，我们介绍了 Anthropic 的 Claude Sonnet 4.5 和 Claude Haiku 4.5 在 Amazon Bedrock 上的可用性，以及面向日本和澳大利亚的跨区域推理能力。我们讨论了组织如何在遵守本地数据处理要求的同时利用先进的 AI 能力，确保推理请求始终停留在地理边界之内。对于处理敏感数据的金融机构、医疗保健提供方和政府机构等行业，推荐使用该新功能。我们还提供了上手指导、配额管理策略，以及从旧版 Claude 模型迁移到 Claude 4.5 模型的指引。要进一步了解 Bedrock 上 Claude Sonnet 4.5 和 Claude Haiku 4.5 的定价，请参阅 [Amazon Bedrock 定价](https://aws.amazon.com/bedrock/pricing)。

借助这项能力，组织现在可以放心地使用 Claude Sonnet 4.5 和 Claude Haiku 4.5 实施生产应用，既满足性能要求，也满足本地数据处理要求，标志着在这些国家负责任地部署 AI 技术取得了重大进展。

### 关于作者

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/03/derrchoo-100x133.jpg)Derrick Choo** 是 AWS 的高级解决方案架构师，通过云采用、AI/ML 和生成式 AI 解决方案加速企业数字化转型。他专攻全栈开发和 ML，设计端到端解决方案，涵盖前端界面、IoT 应用、数据集成和 ML 模型，尤其关注计算机视觉和多模态系统。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/03/mmelli-100x133.jpg)Melanie Li** 博士常驻澳大利亚悉尼，是 AWS 的高级生成式 AI 专家解决方案架构师，主要与客户合作，使用先进的 AI/ML 工具构建解决方案。她积极参与 APJ 地区的多个生成式 AI 项目，充分发挥 LLM 的能力。加入 AWS 之前，Li 博士曾在金融和零售行业担任数据科学职位。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/03/trikande-100x133.jpg)Saurabh Trikande** 是 Amazon Bedrock 和 Amazon SageMaker Inference 的高级产品经理。他热衷于与客户和合作伙伴合作，以推动 AI 普惠为目标。他专注于部署复杂 AI 应用、多租户模型推理、成本优化，以及让生成式 AI 模型的部署更加易用等核心挑战。业余时间，Saurabh 喜欢徒步、了解创新技术、关注 TechCrunch，以及陪伴家人。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/03/jldean-100x133.jpg)Jared Dean **是 AWS 的首席 AI/ML 解决方案架构师。Jared 与各行业的客户合作，开发能够提升效率的机器学习应用。他对一切与 AI、科技和烧烤有关的事物都感兴趣。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/30/chiaos.jpeg)**Stephanie Chiao **是 AWS 亚太及日本地区的生成式 AI GTM 与容量负责人。她倡导客户心声，推动 AWS 生成式 AI 服务（包括 Amazon Bedrock 和 Amazon EC2 GPU）在 APJ 各 AWS 区域的路线图。工作之外，她喜欢用生成式 AI 创作模型为她的柴犬和猫制作肖像。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/30/220720AWS2733_125x125.png)Kazuki Motohashi** 博士是 AWS Japan 的 AI/ML GTM 专家解决方案架构师。他在 AI/ML 领域工作已有 8 年以上，目前为在其业务中使用 AWS 生成式 AI/ML 服务的日本企业客户和合作伙伴提供支持。他一直在找时间玩《最终幻想战略版》，但至今还没开始。

**![Gareth](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/10/gareth_ml19602-100x88.png)Gareth Jones** 是 Anthropic 的产品经理，专注于 Claude API。他的工作包括与 AWS 在 Amazon Bedrock 上合作，让 Claude 能够被广大开发者使用。
