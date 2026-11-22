---
vendor: aws_bedrock
title: Run NVIDIA Nemotron and OpenAI GPT OSS models on Amazon Bedrock in AWS GovCloud (US)
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/run-nvidia-nemotron-and-openai-gpt-oss-models-on-amazon-bedrock-in-aws-govcloud-us
date: 2026-07-01
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 38a48ef58334
---

# Run NVIDIA Nemotron and OpenAI GPT OSS models on Amazon Bedrock in AWS GovCloud (US)

Government agencies running workloads in AWS GovCloud (US) need AI capabilities that keep pace with the commercial sector. At the same time, they can’t compromise the security and compliance controls their missions require. As open-weight foundation models (FMs) move from experimentation into mission systems, two requirements shape every model decision. First, the model must deliver the capability the mission demands. Second, the inference environment must satisfy the agency’s security, compliance, and data residency obligations. For U.S. government agencies, the defense and intelligence community and the contractors that serve them, these requirements are non-negotiable. Access to advanced open-weight models is essential for work such as intelligence analysis, mission planning, acquisition and contract document review, security log analysis, and compliance automation. This access must not require moving sensitive data outside the boundary that governs it.

We’re excited to introduce US-based frontier open-weight models in AWS GovCloud (US). With this release, Amazon Bedrock now supports OpenAI’s open-weight GPT OSS models (120B and 20B) and NVIDIA Nemotron (Nano 9B v2, Nano 12B v2, Nano 30B, Super 120B) models. With these new models, you can build and scale generative AI applications with diverse, high-performance FMs. This offers the flexibility to use OpenAI’s and NVIDIA’s latest models alongside other leading AI models through a single, unified API. You can use this unified API to select the right model for each specific use case without changing your application code.

AWS GovCloud (US) provides an isolated set of AWS Regions designed to host sensitive data and regulated workloads. Regions are physically located in the United States and administered exclusively by U.S. citizens. They help customers meet compliance frameworks including FedRAMP High (Provisional Authority to Operate) and DoD Cloud Computing Security Requirements Guide (SRG) Impact Levels 2, 4, and 5. Additional frameworks include International Traffic in Arms Regulations (ITAR) and Criminal Justice Information Services (CJIS).

[Amazon Bedrock](https://aws.amazon.com/bedrock/) is a fully managed service for accessing FMs from independent model providers, with inference running entirely on AWS-operated infrastructure.

With Amazon Bedrock, inference runs inside the AWS GovCloud (US) isolation boundary, on infrastructure operated by U.S. citizens on U.S. soil. For details on how Amazon Bedrock handles your data, refer to [Data protection in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/data-protection.html).

OpenAI’s open-weight GPT OSS models and NVIDIA Nemotron open-weight models are now available on Amazon Bedrock in AWS GovCloud (US). This launch delivers two open-weight model families into the AWS GovCloud (US) Regions: OpenAI gpt-oss-120b and gpt-oss-20b, and the NVIDIA Nemotron 3 family, including Nemotron 3 Super 120B alongside the Nemotron 3 Nano models. With these models, you can build agentic applications and mission workflows such as automated security control assessments, multi-document intelligence synthesis, contract and acquisition analysis, and policy compliance checking. All of this runs within the AWS GovCloud (US) compliance boundary.

In this post, we cover the models currently available in AWS GovCloud (US) and their capabilities, the inference options for data residency, the available service tiers and how to get started.

## About the models

This section introduces the two open-weight model families now available in AWS GovCloud (US) and the capabilities that set each apart.

### NVIDIA Nemotron

The NVIDIA Nemotron family delivers both small language model (SLM) and large language model (LLM) capabilities, built for compute efficiency and accuracy in specialized agentic AI systems. NVIDIA describes the two models as follows:

- **NVIDIA Nemotron 3 Super** is a 120B open hybrid mixture-of-experts (MoE) model for complex multi-agent workloads with 120 billion total parameters that activates only 12 billion parameters per token. This MoE design delivers up to 5 times higher throughput than the previous generation for cost-efficient inference, and its 1-million-token context window gives agents the long-term memory to stay focused across long, multi-step tasks.
- **NVIDIA Nemotron 3 Nano** is a 30-billion-parameter open model that activates approximately 3 billion parameters per token, delivering 4 times higher throughput than the previous generation and reducing reasoning-token generation by up to 60 percent. Its 1-million-token context window supports long-running, multi-step agent workflows.

For the full list of NVIDIA Nemotron models available in AWS GovCloud (US), refer to [NVIDIA models on Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards-nvidia.html).

### OpenAI GPT OSS

OpenAI’s GPT OSS models are open-weight, text-to-text models designed for reasoning, agentic, and developer tasks, with adjustable reasoning effort and support for external tool integration. This post focuses on two variants:

**gpt-oss-120b** is OpenAI’s 120-billion parameter open-weight model, designed for production, general-purpose, and high-reasoning use cases.

**gpt-oss-20b** is the 20-billion parameter model, designed for lower latency and local or specialized use cases.

Both models provide a 128K-token context window and up to 16K output tokens, and both accept text input and generate text output. Because the weights are open, organizations can independently evaluate the model architecture, review the published model card, and run their own benchmarks on representative workloads. For government teams, this transparency supports organizational risk assessments, enables customer security teams to evaluate model behavior before deployment, and aligns with the zero-trust principles many U.S. government agencies are adopting.

For the full list of OpenAI models available in AWS GovCloud (US), refer to [OpenAI models on Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards-openai.html).

## Serverless inference inside your compliance boundary

NVIDIA Nemotron and GPT OSS models on Amazon Bedrock are served by the next-generation inference engine in Amazon Bedrock. To understand the architecture, it helps to distinguish between the engine and the endpoint: the engine is the underlying serving infrastructure, designed with Model Deployment Account isolation and zero operator access, while the `bedrock-mantle` endpoint is the OpenAI-compatible HTTPS API that applications call to send requests to the engine. For agencies, there’s no infrastructure to provision, no GPUs to manage, and no model-deployment expertise required.

The next-generation inference engine is built on a zero operator access design. No operator, whether from AWS, the customer, or a model provider, can access customer data, such as inference prompts or completions. Combined with the AWS GovCloud (US) isolation boundary, this gives government teams a strong data-protection foundation. For the technical details, refer to [Exploring the zero operator access design of Mantle](https://aws.amazon.com/blogs/machine-learning/exploring-the-zero-operator-access-design-of-mantle/).

Amazon Bedrock provides two endpoints for invoking these models. The `bedrock-mantle` endpoint is the OpenAI-compatible API for the next-generation inference engine, so you can call it with the OpenAI Python and TypeScript SDKs. It uses the Chat Completions and Responses APIs. The `bedrock-runtime` endpoint uses the Converse and InvokeModel APIs through the AWS SDK, with access to native Amazon Bedrock features such as Guardrails. Code samples for both are in the Getting started section.

## Regional availability and data residency

Amazon Bedrock offers multiple options for where your inference requests are processed. *In-Region* keeps every request within a single Region, and *Geographic Cross-Region inference* routes requests across Regions within a geography for higher throughput, so your data stays within that geographic boundary. For NVIDIA Nemotron and GPT OSS models in AWS GovCloud (US), the options are as follows:

- *In-Region inference* is available in `us-gov-west-1` (AWS GovCloud (US-West)).
- *Geo cross-Region inference *is available through a dedicated AWS GovCloud (US) cross-Region inference ID that routes requests across `us-gov-west-1` and `us-gov-east-1`. Traffic stays within the AWS GovCloud (US) boundary, while you gain resilience across both Regions.

All inference for these models stays within the AWS GovCloud (US) boundary. Global cross-Region inference, which routes requests across commercial AWS Regions worldwide, isn’t available in AWS GovCloud (US). You can choose between single-Region and Geo cross-Region based on your requirements.

## Service tiers

Amazon Bedrock offers multiple [service tiers](https://docs.aws.amazon.com/bedrock/latest/userguide/service-tiers-inference.html) to match different workload requirements. For all three models, the Standard, Priority, and Flex tiers are supported.

| **Service tier** | **Description** | **Supported** |
| --- | --- | --- |
| Standard | Pay-per-token access with no commitment | Yes |
| Priority | Higher throughput for latency-sensitive traffic | Yes |
| Flex | Lower-cost access for flexible, non-time-sensitive workloads | Yes |
| Reserved | Dedicated throughput with a term commitment | Not currently available |

By default, requests use on-demand inference on the Standard tier, where you pay per token without reserving capacity in advance. For latency-sensitive, customer-facing workloads, you can route individual requests to the Priority tier. For non-time-sensitive work such as model evaluations or batch summarization, the Flex tier offers a lower-cost option. For scaling guidance and how to handle throttling at production volume, refer to [Scaling and throughput best practices](https://docs.aws.amazon.com/bedrock/latest/userguide/scaling-throughput-best-practices.html) and the Getting started section.

## Getting started in AWS GovCloud (US)

This section walks through invoking the models, starting with the recommended `bedrock-mantle` endpoint. The examples use the `us-gov-west-1` Region, where in-Region inference is available.

### Console playground

- Navigate to the [Amazon Bedrock console](https://console.amazonaws-us-gov.com/bedrock/) in your AWS GovCloud (US) account.
- Choose **Playground** from the left menu under the **Test** section.
- Choose **Select model**.
- Choose the provider (**NVIDIA** or **OpenAI**) from the category list, then select the model (for example, **NVIDIA Nemotron 3 Super** or **120B gpt-oss-120b**).
- Choose **Apply** to load the model.
- Enter a prompt to test the model.

### Using the bedrock-mantle endpoint (recommended)

To use these models, you need an AWS account in AWS GovCloud (US) with permissions to invoke Amazon Bedrock models. For the `bedrock-mantle` endpoint, you need an [Amazon Bedrock API key](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html) or standard AWS credentials. The following is a sample policy:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "BedrockMantleInference",
            "Effect": "Allow",
            "Action": [
                "bedrock-mantle:CreateInference",
                "bedrock-mantle:Get*",
                "bedrock-mantle:List*"
            ],
            "Resource": "arn:aws-us-gov:bedrock-mantle:us-gov-west-1:111122223333:project/*"
        },
        {
            "Sid": "BedrockMantleCallWithBearerToken",
            "Effect": "Allow",
            "Action": "bedrock-mantle:CallWithBearerToken",
            "Resource": "*"
        }
    ]
}
```

Replace `111122223333` with your AWS account ID and scope the Region to the AWS GovCloud (US) Regions you use. The code examples in this post authenticate with a Bedrock API key, which requires `bedrock-mantle:CallWithBearerToken`. This action must be scoped to `"Resource": "*"`, as shown in the second statement. To control which identities can generate or use Amazon Bedrock API keys, refer to [Control permissions for generating and using Amazon Bedrock API keys](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html). To restrict your organization to approved models only, use a [service control policy (SCP)](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html).

The following example uses the [OpenAI Python SDK](https://github.com/openai/openai-python) to call the `bedrock-mantle` endpoint. For production workloads, use short-term API keys, which expire automatically (maximum 12 hours) and inherit the permissions of the IAM role that generated them.

```
import boto3
from openai import OpenAI

# Retrieve the Bedrock API key from AWS Secrets Manager
secrets_client = boto3.client("secretsmanager", region_name="us-gov-west-1")
api_key = secrets_client.get_secret_value(SecretId="bedrock-api-key")["SecretString"]

client = OpenAI(
    # Use the AWS GovCloud (US) Region in the base URL, e.g. us-gov-west-1
    base_url="https://bedrock-mantle.us-gov-west-1.api.aws/v1",
    api_key=api_key,
)

response = client.chat.completions.create(
    model="openai.gpt-oss-120b",
    messages=[
        {"role": "user", "content": "Explain the benefits of open-weight models for regulated workloads."}
    ],
    reasoning_effort="medium",  # low | medium | high
    max_completion_tokens=512,
)

print(response.choices[0].message.content)
```

**Note:** These examples retrieve the Bedrock API key from [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/). For local development, you can instead read the key from an environment variable, but avoid that pattern in production. Use AWS Secrets Manager or another secrets store.

To call NVIDIA Nemotron 3 Super 120B instead, change the model parameter to `nvidia.nemotron-super-3-120b` and remove the `reasoning_effort` parameter (reasoning effort control is specific to GPT OSS). No other code changes are required.

#### Controlling reasoning effort

GPT OSS models are reasoning models that expose an adjustable reasoning effort. Set the `reasoning_effort` parameter on the Chat Completions call to `low`, `medium`, or `high` to trade response latency against reasoning depth. Use `low` for high-volume, latency-sensitive traffic, and `high` for complex, multi-step reasoning or agentic planning. For reasoning models, prefer `max_completion_tokens` to bound the response length (the older `max_tokens` field is still accepted).

#### Using the Responses API

In addition to Chat Completions, GPT OSS models support the Responses API, OpenAI’s interface for reasoning-style interactions. It takes a single `input` rather than a `messages` array. NVIDIA Nemotron 3 Super 120B doesn’t support the Responses API. Use Chat Completions, Converse, or Invoke for that model.

```
import boto3
from openai import OpenAI

# Retrieve the Bedrock API key from AWS Secrets Manager
secrets_client = boto3.client("secretsmanager", region_name="us-gov-west-1")
api_key = secrets_client.get_secret_value(SecretId="bedrock-api-key")["SecretString"]

client = OpenAI(
    base_url="https://bedrock-mantle.us-gov-west-1.api.aws/v1",
    api_key=api_key,
)

response = client.responses.create(
    model="openai.gpt-oss-120b",
    input="Explain the benefits of open-weight models for regulated workloads.",
)

print(response)
```

#### Streaming responses

For chat and agent use cases where you want to surface tokens to the user as they are generated, set `stream=True`. The response becomes an iterator of incremental delta events:

```
stream = client.chat.completions.create(
    model="openai.gpt-oss-120b",
    messages=[
        {"role": "user", "content": "Write a short summary of mixture-of-experts architectures."}
    ],
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
print()
```

On the `bedrock-runtime` endpoint, the equivalent capability requires the `bedrock:InvokeModelWithResponseStream` permission, which the minimum policy shown later already grants.

#### Tool calling

NVIDIA Nemotron and GPT OSS open-weight models are designed for agentic workflows, making them actionable for tool-calling scenarios. In a tool-calling workflow, you define functions (tools) that the model can invoke, the model decides when to call them based on the user’s request, and your application runs the function and returns the result for the model to incorporate into its final response.

The following example demonstrates this pattern end to end. We define a `get_weather` tool, send a user message, let the model request the tool call, run the function with mock data, and pass the result back so the model can generate a natural-language answer.

```
import json
import boto3
from openai import OpenAI

# Retrieve the Bedrock API key from AWS Secrets Manager
secrets_client = boto3.client("secretsmanager", region_name="us-gov-west-1")
api_key = secrets_client.get_secret_value(SecretId="bedrock-api-key")["SecretString"]

client = OpenAI(
    base_url="https://bedrock-mantle.us-gov-west-1.api.aws/v1",
    api_key=api_key,
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and country (e.g., Seattle, US)"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

# Step 1: Send the user request with tool definitions
messages = [
    {"role": "user", "content": "What's the weather like in Seattle?"}
]

response = client.chat.completions.create(
    model="openai.gpt-oss-120b",
    messages=messages,
    tools=tools,
    tool_choice="auto",
)

assistant_message = response.choices[0].message

# Step 2: Check if the model wants to call a tool
if assistant_message.tool_calls:
    messages.append(assistant_message)

    for tool_call in assistant_message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        # Step 3: Validate function name and run it
        if function_name == "get_weather":
            location = arguments.get("location", "Unknown")
            unit = arguments.get("unit", "fahrenheit")
            result = {
                "location": location,
                "temperature": 18 if unit == "celsius" else 64,
                "unit": unit,
                "condition": "Partly cloudy",
                "humidity": 72,
            }
        else:
            result = {"error": f"Unknown function: {function_name}"}

        # Step 4: Return the function result to the model
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result),
        })

    # Step 5: Get the final response incorporating tool results
    final_response = client.chat.completions.create(
        model="openai.gpt-oss-120b",
        messages=messages,
        tools=tools,
    )

    print(final_response.choices[0].message.content)
else:
    print(assistant_message.content)
```

The example shown here demonstrates client-side tool calling: the model returns a tool call, your application runs the function, and you pass the result back. On `bedrock-mantle`, GPT OSS models support both client-side and server-side tool calling, while NVIDIA Nemotron 3 Super 120B supports client-side tool calling only. Both model families also support tool calling on the `bedrock-runtime` endpoint through the Converse API (using `toolConfig`). Refer to each model’s [model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards.html) for the full feature matrix.

### Using the bedrock-runtime endpoint (boto3)

For the `bedrock-runtime` endpoint, you need AWS credentials configured (AWS Identity and Access Management (IAM) user or role) with permission to invoke the model. The following is a sample policy:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": "arn:aws-us-gov:bedrock:us-gov-west-1::foundation-model/openai.gpt-oss-120b-1:0"
        }
    ]
}
```

For production deployments, scope the `Resource` to the specific AWS GovCloud (US) Regions and model IDs that you use.

The following example sends a single-turn request using the [AWS SDK for Python (boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) with the Converse API. On the `bedrock-runtime` endpoint, the GPT OSS model IDs include a version suffix (for example, `openai.gpt-oss-120b-1:0`). Use the exact model ID from each model’s model card. The response contains a reasoning block followed by a text block, so the example selects the text block when printing the answer.

```
import boto3

client = boto3.client("bedrock-runtime", region_name="us-gov-west-1")

response = client.converse(
    modelId="openai.gpt-oss-120b-1:0",
    messages=[{
        "role": "user",
        "content": [{"text": "What is a mixture-of-experts architecture?"}]
    }],
    inferenceConfig={"maxTokens": 2048, "temperature": 1.0, "topP": 0.95},
)

content_blocks = response["output"]["message"]["content"]
response_text = next(
    (block["text"] for block in content_blocks if "text" in block),
    None
)

if response_text:
    print(response_text)
else:
    print("No text response.")
```

To call NVIDIA Nemotron 3 Super 120B through `bedrock-runtime`, use the model ID `nvidia.nemotron-super-3-120b` (this model ID doesn’t carry a version suffix).

You can also access these models from your terminal using the [AWS Command Line Interface (AWS CLI)](https://docs.aws.amazon.com/cli/latest/reference/bedrock-runtime/):

```
aws bedrock-runtime converse \
--model-id openai.gpt-oss-120b-1:0 \
--messages '[{"role":"user","content":[{"text":"Type_Your_Prompt_Here"}]}]' \
--inference-config '{"maxTokens":512}' \
--region us-gov-west-1
```

### Scaling on-demand inference

On-demand capacity on the Standard tier is shared and allocated per AWS Region, so during periods of high regional demand a request can be briefly queued or throttled. On the `bedrock-mantle` endpoint, there is no requests-per-minute quota. Throughput is governed by token-based limits. These open-weight models don’t currently have per-account token quotas published in the Service Quotas console, so use retry logic with exponential backoff to handle transient throttling. Amazon Bedrock surfaces two HTTP error codes that indicate when a request can’t be served:

| **Error code** | **Meaning** | **Recommended action** |
| --- | --- | --- |
| 429 | The request was denied because it exceeded the account quotas for Amazon Bedrock. | Request a quota increase through the Service Quotas console, and apply client-side throttling. |
| 503 | The service is experiencing high demand or temporary capacity constraints. | Retry with exponential backoff and jitter. If throttling is sustained, reduce the request rate and ramp back up gradually. |

For transient 503 responses, configure automatic retries in your SDK:

```
import boto3
from botocore.config import Config

config = Config(retries={"total_max_attempts": 6, "mode": "standard"})
client = boto3.client("bedrock-runtime", config=config)
```

When ramping back up after sustained throttling, hold at a steady state for about 15 minutes between increases rather than stepping straight to the target volume. For more detailed ramp-up procedure and additional best practices, see [Scaling and throughput best practices](https://docs.aws.amazon.com/bedrock/latest/userguide/scaling-throughput-best-practices.html) in the Amazon Bedrock User Guide.

### Clean up

These models use on-demand inference, which incurs charges only when you invoke a model, so there’s no endpoint or infrastructure to tear down. To avoid unintended charges after testing:

If you generate short-term Bedrock API keys, they expire automatically (maximum 12 hours). To revoke one sooner, delete it in the Amazon Bedrock console.

If you opted in to the Priority tier for testing, return to Standard pricing for non-latency-sensitive traffic by removing the `service_tier` parameter from your invocations.

If you stored a Bedrock API key in AWS Secrets Manager for testing, delete the secret to avoid storage charges.

For pricing details by model and tier, refer to [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/).

## Pricing and availability

OpenAI GPT OSS and NVIDIA Nemotron models are available today on Amazon Bedrock in AWS GovCloud (US). In-Region inference is available in AWS GovCloud (US-West) (`us-gov-west-1`), and Geo cross-Region inference routes requests across AWS GovCloud (US-West) and AWS GovCloud (US-East) (`us-gov-east-1`) while keeping traffic within the AWS GovCloud (US) boundary.

Pricing is per token and varies by model and service tier. On-demand inference on the Standard tier incurs charges when you invoke a model, with no capacity to reserve and no infrastructure to tear down. For current rates, refer to [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/).

## Conclusion

OpenAI GPT OSS and NVIDIA Nemotron models are now available on Amazon Bedrock in AWS GovCloud (US), giving government customers access to advanced open-weight models inside their compliance boundary. In this post, we covered the available models and their capabilities, the two endpoints for invoking them, the available service tiers, and scaling guidance. Government teams can run these open-weight models for mission workloads while keeping inference inside the AWS GovCloud (US) boundary, on AWS-operated infrastructure.

**To get started:**

- Open the [Amazon Bedrock console](https://console.amazonaws-us-gov.com/bedrock/) in your AWS GovCloud (US) account and try the models in the **Playground**.
- Run the `bedrock-mantle` Python sample from this post against your own data.
- Evaluate gpt-oss-120b, gpt-oss-20b, and NVIDIA Nemotron 3 Super 120B on your workloads to choose the model that fits your cost and latency profile.
- For production deployment, review [Scaling and throughput best practices](https://docs.aws.amazon.com/bedrock/latest/userguide/scaling-throughput-best-practices.html) and consider the Priority tier for latency-sensitive traffic.

## Resources

For more information, refer to the following resources:

- [AWS GovCloud (US)](https://aws.amazon.com/govcloud-us/)
- [Amazon Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)
- [OpenAI models on Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-openai.html)
- [NVIDIA Nemotron 3 Super 120B model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-nvidia-nemotron-super-3-120b.html)
- [Exploring the zero operator access design of Mantle](https://aws.amazon.com/blogs/machine-learning/exploring-the-zero-operator-access-design-of-mantle/)
- [Amazon Bedrock service tiers](https://docs.aws.amazon.com/bedrock/latest/userguide/service-tiers-inference.html)
- [Amazon Bedrock API keys](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html)

## About the authors
