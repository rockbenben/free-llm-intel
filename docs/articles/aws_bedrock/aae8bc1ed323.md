---
vendor: aws_bedrock
title: 在 AWS 上引入 Claude Sonnet 5.5
original_title: Introducing Claude Sonnet 5.5 on AWS
url: https://aws.amazon.com/blogs/machine-learning/introducing-claude-sonnet-5-5-on-aws
date: 2026-09-28
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

今天，我们很高兴地宣布 Claude Sonnet 5.5 在 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 和 [Claude Platform on AWS](https://staging.prod.website.marketing.aws.dev/blogs/machine-learning/introducing-claude-platform-on-aws-anthropics-native-platform-through-your-aws-account/) 上可用。Claude Sonnet 5.5 是一个更聪明、更高效的 Sonnet 模型，适用于聚焦的编码和知识工作——对多数工作以更快的速度带来更低每任务成本。

Amazon Bedrock 让你在把数据保持在 AWS 基础设施内、带区域数据驻留的同时，获得 Sonnet 5.5 的能力。它与你团队已经在使用的 AWS 控制协作，包括用于访问的 AWS Identity and Access Management (IAM)、用于审计的 AWS CloudTrail、用于监控的 Amazon CloudWatch，以及 Amazon Bedrock Guardrails。用量出现在你的 AWS 账单上。

本文涵盖 Claude Sonnet 5.5 的改进、关于何时选择 Sonnet 的实用指导，以及如何在 Amazon Bedrock 上开始上手。

## 是什么让 Claude Sonnet 5.5 与众不同

这些改进在范围明确的工作上尤为突出。无论开发者给它指派一个功能还是一个 bug 修复，Sonnet 5.5 都能完成工作并对照所述需求检查结果。它还产出比 Sonnet 5 更精致的文档和视觉作品，包括一页纸简介、架构图和摘要幻灯片。

结合对多数工作更低的每任务成本，这使 Sonnet 5.5 很适合那些持续或大规模运行的工作负载。在工程中，这包括对告警的首次响应、对智能体的全天候监控、SQL 生成、UI 和 UX 测试，以及在 IDE 中带固定支出上限的快速编码智能体。在整个企业中，它支持范围明确的小规模分析、对大型用户群来说有界的分析、短电子表格编辑和常规文档任务。

## 把 Sonnet 5.5 与 Opus 5.5 配对以完成工作

我们最近宣布了 [Opus 5.5 的可用](https://aws.amazon.com/blogs/machine-learning/claude-opus-5-5-is-now-available-on-aws/)。如今有了 Sonnet 5.5，你可以结合两类工作：需要审慎判断的决策，和范围明确的任务。你可以这样理解这些模型：

- **Claude Opus 5.5** 承担那些判断性的取舍。对编码而言，那是发布调试、多 PR 的功能栈、大型 pull request 的安全审查，以及有清晰目标的代码迁移。在代码之外，它处理那些以一个成品电子表格、演示或报告收尾的长分析，以及金融研究和合同红线修订。
- **Claude Sonnet 5.5** 承接那些方法已经明确、剩下的只是快速执行的工作，对多数工作以更快的速度带来更低每任务成本（相比 Opus 5.5）。

## 在 Amazon Bedrock 上开始使用 Claude Sonnet 5.5

要试用 Sonnet 5.5，打开 [Amazon Bedrock 控制台](https://console.aws.amazon.com/bedrock/)，进入 **Test > Playground**，并把 Sonnet 5.5 选为模型。从这里，你可以直接对它运行一个 prompt。

图 1：在 Amazon Bedrock 控制台 Playground 中选择一个 Anthropic Claude 模型

以编程方式，你可以通过 Anthropic SDK 针对 `bedrock-runtime` 用 [Anthropic Messages API](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages.html) 调用该模型。你也可以通过 [AWS Command Line Interface (AWS CLI)](https://staging.prod.website.marketing.aws.dev/cli/) 和 [AWS SDK](https://staging.prod.website.marketing.aws.dev/developer/tools/)，在 `bedrock-runtime` 上使用 [Invoke](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-api.html) 和 [Converse](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html) API。

### 前提条件

你必须具备以下前提条件：

- 拥有 Amazon Bedrock 访问权限的有效 AWS 账户。
- 已安装并配置 AWS CLI。
- Python 3.10+。
- 已安装 Boto3：`pip install boto3`。
- AWS Identity and Access Management (IAM) 权限：`bedrock:InvokeModel`、`bedrock:InvokeModelWithResponseStream`。

下面是使用 AWS SDK for Python (Boto3) 配合 InvokeModel API 的一个简短示例：

```
import boto3
import json

# Create a Bedrock Runtime client
bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

# Invoke Claude Sonnet 5.5
response = bedrock_runtime.invoke_model(
    modelId="global.anthropic.claude-sonnet-5-5",
    contentType="application/json",
    accept="application/json",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "messages": [
            {
                "role": "user",
                "content": " Write a Python function slugify(text) that lowercases a string, replaces spaces and underscores with hyphens, and strips any character that isn't a letter, digit, or hyphen. Code only."
            }
        ]
    })
)

result = json.loads(response["body"].read())
# Sonnet 5.5 may return a thinking block before the text block,
# so select the text block rather than a fixed index.
print(next(b["text"] for b in result["content"] if b["type"] == "text"))
```

你可以探索 [Getting Started notebook](https://github.com/aws-samples/anthropic-on-aws/blob/main/notebooks/claude_sonnet_5_5_getting_started/claude-sonnet-5-5-getting-started.ipynb) 获取更多示例。你可以通过 [Amazon CloudWatch](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring.html) 和 [AWS Cost Explorer](https://staging.prod.website.marketing.aws.dev/aws-cost-management/aws-cost-explorer/) 监控用量、性能和成本，随需求增长扩展应用。

## 可用性

Claude Sonnet 5.5 今天可通过 `bedrock-runtime` 上的 Global CRIS（global.）推理配置，在 Amazon Bedrock 上获取。

受支持的 AWS 区域完整列表见 [Amazon Bedrock 文档](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards-anthropic.html)。定价信息见 [Amazon Bedrock 定价](https://aws.amazon.com/bedrock/pricing/)。它在北美也可通过 [Claude Platform on AWS](https://aws.amazon.com/claude-platform/) 获取。
