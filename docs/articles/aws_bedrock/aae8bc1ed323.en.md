---
vendor: aws_bedrock
title: Introducing Claude Sonnet 5.5 on AWS
original_title: Introducing Claude Sonnet 5.5 on AWS
url: https://aws.amazon.com/blogs/machine-learning/introducing-claude-sonnet-5-5-on-aws
date: 2026-09-28
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 7e66f63914aa
---

## [Artificial Intelligence](https://aws.amazon.com/blogs/machine-learning/)

# Introducing Claude Sonnet 5.5 on AWS

Today, we’re excited to announce the availability of Claude Sonnet 5.5 on [Amazon Bedrock](https://aws.amazon.com/bedrock/) and [Claude Platform on AWS](https://staging.prod.website.marketing.aws.dev/blogs/machine-learning/introducing-claude-platform-on-aws-anthropics-native-platform-through-your-aws-account/). Claude Sonnet 5.5 is a smarter, more efficient Sonnet model suited for focused coding and knowledge work with lower cost per task for most work at faster speed.

Amazon Bedrock gives you Sonnet 5.5 capabilities while keeping your data within AWS infrastructure with Regional data residency. It works with the AWS controls your team already uses, including AWS Identity and Access Management (IAM) for access, AWS CloudTrail for audit, Amazon CloudWatch for monitoring, and Amazon Bedrock Guardrails. Usage appears on your AWS bill.

This post covers Claude Sonnet 5.5’s improvements, practical guidance on when to choose Sonnet, and how to get started on Amazon Bedrock.

## What makes Claude Sonnet 5.5 different

The improvements stand out on well-scoped work. Whether a developer assigns it a feature or a bug fix, Sonnet 5.5 completes the work and checks the result against the stated requirements. It also produces more polished documents and visuals than Sonnet 5, including one-pagers, architecture diagrams, and summary slides.

Together with the lower cost per task for most work, this makes Sonnet 5.5 a strong fit for workloads that run continuously or at scale. In engineering, that includes first response to alerts, always-on monitoring of agents, SQL generation, UI and UX testing, and fast coding agents in the IDE with a fixed spend cap. Across the enterprise, it supports scoped analysis, short spreadsheet edits, and routine document tasks for large user populations.

## Pairing Sonnet 5.5 with Opus 5.5 to get the job done

We recently announced the [availability of Opus 5.5](https://aws.amazon.com/blogs/machine-learning/claude-opus-5-5-is-now-available-on-aws/). Now with Sonnet 5.5 you can combine two kinds of work: decisions that need careful judgment, and tasks that are well scoped. This is how you can think about these models:

- **Claude Opus 5.5** takes the judgment calls. For coding, that means release debugging, multi-PR feature stacks, security review of large pull requests, and code migrations with clear targets. Beyond code, it handles long analyses that end in a finished spreadsheet, deck, or report, along with financial research and contract redlining.
- **Claude Sonnet 5.5** takes the work where the approach is already clear and what’s left is to execute it quickly, with a lower cost per task (than Opus 5.5) for most work at faster speed.

## Getting started with Claude Sonnet 5.5 on Amazon Bedrock

To try Sonnet 5.5, open the [Amazon Bedrock console](https://console.aws.amazon.com/bedrock/), go to **Test > Playground**, and select Sonnet 5.5 as the model. From there, you can run a prompt directly against it.

Figure 1: Selecting an Anthropic Claude model in the Amazon Bedrock console Playground

Programmatically, you can call the model with the [Anthropic Messages API](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages.html) against `bedrock-runtime` through the Anthropic SDK. You can also use the [Invoke](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-api.html) and [Converse](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html) APIs on `bedrock-runtime` through the [AWS Command Line Interface (AWS CLI)](https://staging.prod.website.marketing.aws.dev/cli/) and [AWS SDK](https://staging.prod.website.marketing.aws.dev/developer/tools/).

### Prerequisites

You must have the following prerequisites:

- Active AWS account with Amazon Bedrock access.
- AWS CLI installed and configured.
- Python 3.10+.
- Boto3 installed: `pip install boto3`.
- AWS Identity and Access Management (IAM) permissions: `bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream`.

Here’s a quick example using the AWS SDK for Python (Boto3) with the InvokeModel API:

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

You can explore the [Getting Started notebook](https://github.com/aws-samples/anthropic-on-aws/blob/main/notebooks/claude_sonnet_5_5_getting_started/claude-sonnet-5-5-getting-started.ipynb) for more examples. You can monitor usage, performance, and costs through [Amazon CloudWatch](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring.html) and [AWS Cost Explorer](https://staging.prod.website.marketing.aws.dev/aws-cost-management/aws-cost-explorer/) to scale your applications as demand grows.

## Availability

Claude Sonnet 5.5 is available today on Amazon Bedrock through the Global CRIS (global.) inference profile on `bedrock-runtime`.

See the [Amazon Bedrock documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards-anthropic.html) for the full list of supported AWS Regions. For pricing information, see [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/). It is also available through [Claude Platform on AWS](https://aws.amazon.com/claude-platform/) in North America.

Give Claude Sonnet 5.5 a try in the [Amazon Bedrock console](https://console.aws.amazon.com/bedrock), in [Claude Platform on AWS](https://console.aws.amazon.com/claude-platform/), or explore the [Getting Started notebooks](https://github.com/aws-samples/anthropic-on-aws/tree/main/notebooks) on GitHub.

## About the authors
