---
vendor: aws_bedrock
title: Run NVIDIA Nemotron and OpenAI GPT OSS models on Amazon Bedrock in AWS GovCloud (US)
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/run-nvidia-nemotron-and-openai-gpt-oss-models-on-amazon-bedrock-in-aws-govcloud-us
date: 2026-07-01
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: d33f5d757131
---

# 在 AWS GovCloud (US) 的 Amazon Bedrock 上运行 NVIDIA Nemotron 与 OpenAI GPT OSS 模型

在 AWS GovCloud (US) 中运行工作负载的政府机构，需要能够跟上商业领域步伐的 AI 能力。与此同时，它们又不能牺牲任务所要求的安全与合规控制。随着开放权重基础模型（foundation model，FM）从实验阶段进入任务系统，每一项模型决策都受两个条件约束。第一，模型必须提供任务所需的能力。第二，推理环境必须满足机构在安全、合规与数据驻留方面的义务。对美国政府机构、国防与情报界以及为它们提供服务的承包商而言，这些要求没有商量余地。获取先进的开放权重模型，对情报分析、任务规划、采购与合同文档审查、安全日志分析以及合规自动化等工作至关重要。而这种获取不能要求把敏感数据移出管辖它的边界。

我们很高兴在 AWS GovCloud (US) 中引入部署在美国境内的前沿开放权重模型。通过本次发布，Amazon Bedrock 现已支持 OpenAI 的开放权重 GPT OSS 模型（120B 与 20B）以及 NVIDIA Nemotron 模型（Nano 9B v2、Nano 12B v2、Nano 30B、Super 120B）。借助这些新模型，你可以用多样化、高性能的 FM 构建并扩展生成式 AI 应用。这带来了灵活性：通过单一的统一 API，即可把 OpenAI 与 NVIDIA 的最新模型与其他领先 AI 模型一起使用。你可以用这个统一 API 为每个具体用例挑选合适的模型，而无需改动应用代码。

AWS GovCloud (US) 提供一组隔离的 AWS 区域，专为承载敏感数据与受监管工作负载而设计。这些区域物理上位于美国境内，并且仅由美国公民管理。它们帮助客户满足各类合规框架，包括 FedRAMP High（临时运营授权，Provisional Authority to Operate）以及 DoD Cloud Computing Security Requirements Guide（SRG）的 Impact Level 2、4 和 5。其他框架还包括 International Traffic in Arms Regulations（ITAR）与 Criminal Justice Information Services（CJIS）。

[Amazon Bedrock](https://aws.amazon.com/bedrock/) 是一项完全托管的服务，用于访问来自独立模型提供商的 FM，其推理完全运行在 AWS 运营的基础设施上。

使用 Amazon Bedrock 时，推理运行在 AWS GovCloud (US) 隔离边界之内，运行在美国本土、由美国公民运营的基础设施上。有关 Amazon Bedrock 如何处理你的数据的详细信息，请参阅 [Data protection in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/data-protection.html)。

OpenAI 的开放权重 GPT OSS 模型与 NVIDIA Nemotron 开放权重模型现已在 AWS GovCloud (US) 的 Amazon Bedrock 上可用。本次发布将两个开放权重模型家族引入 AWS GovCloud (US) 区域：OpenAI 的 gpt-oss-120b 与 gpt-oss-20b，以及 NVIDIA Nemotron 3 家族，其中包括 Nemotron 3 Super 120B 与 Nemotron 3 Nano 系列模型。借助这些模型，你可以构建 agentic 应用与任务工作流，例如自动化安全控制评估、多文档情报综合、合同与采购分析，以及政策合规检查。所有这些都运行在 AWS GovCloud (US) 的合规边界之内。

在本文中，我们介绍 AWS GovCloud (US) 中当前可用的模型及其能力、面向数据驻留的推理选项、可用的服务层级，以及如何开始使用。

## 关于这些模型

本节介绍现已在 AWS GovCloud (US) 中可用的两个开放权重模型家族，以及让它们各自脱颖而出的能力。

### NVIDIA Nemotron

NVIDIA Nemotron 家族同时提供小语言模型（SLM）与大语言模型（LLM）能力，专为专业化 agentic AI 系统中的计算效率与准确性而打造。NVIDIA 对这两个模型的描述如下：

- **NVIDIA Nemotron 3 Super** 是一个 120B 的开放混合专家（mixture-of-experts，MoE）模型，面向复杂的多 agent 工作负载，总参数达 1200 亿，而每个 token 仅激活 120 亿参数。这种 MoE 设计带来比上一代最高 5 倍的吞吐量，实现高性价比推理；其 100 万 token 的上下文窗口为 agent 提供长期记忆，使其在漫长的多步任务中保持专注。
- **NVIDIA Nemotron 3 Nano** 是一个 300 亿参数的开放模型，每个 token 大约激活 30 亿参数，吞吐量比上一代高 4 倍，并将推理 token 的生成量减少最多 60%。其 100 万 token 的上下文窗口可支撑长时间运行的多步 agent 工作流。

关于 AWS GovCloud (US) 中可用的 NVIDIA Nemotron 模型完整清单，请参阅 [NVIDIA models on Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards-nvidia.html)。

### OpenAI GPT OSS

OpenAI 的 GPT OSS 模型是开放权重的文本到文本模型，为推理、agentic 与开发者任务而设计，具备可调的推理强度，并支持外部工具集成。本文聚焦于两个变体：

**gpt-oss-120b** 是 OpenAI 的 1200 亿参数开放权重模型，面向生产环境、通用以及高推理强度的用例。

**gpt-oss-20b** 是 200 亿参数的模型，面向更低延迟以及本地或专用用例。

两个模型都提供 128K token 的上下文窗口和最多 16K 的输出 token，并且都接受文本输入、生成文本输出。由于权重是开放的，组织可以独立评估模型架构、查阅已发布的模型卡，并针对有代表性的工作负载运行自己的基准测试。对政府团队而言，这种透明度支撑组织的风险评估，使客户的安全团队能够在部署前评估模型行为，也与许多美国政府机构正在采用的零信任原则相一致。

关于 AWS GovCloud (US) 中可用的 OpenAI 模型完整清单，请参阅 [OpenAI models on Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards-openai.html)。

## 在你的合规边界内实现无服务器推理

Amazon Bedrock 上的 NVIDIA Nemotron 与 GPT OSS 模型由 Amazon Bedrock 的下一代推理引擎提供服务。要理解这套架构，区分引擎与端点会有所帮助：引擎是底层的服务基础设施，采用 Model Deployment Account 隔离与零操作员访问设计；而 `bedrock-mantle` 端点是应用程序用来向引擎发送请求的、兼容 OpenAI 的 HTTPS API。对机构而言，无需预置任何基础设施，无需管理 GPU，也无需具备模型部署方面的专业知识。

下一代推理引擎建立在零操作员访问的设计之上。任何操作员——无论是来自 AWS、客户还是模型提供商——都无法访问客户数据，例如推理的 prompt 或补全结果。结合 AWS GovCloud (US) 隔离边界，这为政府团队奠定了坚实的数据保护基础。技术细节请参阅 [Exploring the zero operator access design of Mantle](https://aws.amazon.com/blogs/machine-learning/exploring-the-zero-operator-access-design-of-mantle/)。

Amazon Bedrock 提供两个端点来调用这些模型。`bedrock-mantle` 端点是面向下一代推理引擎的、兼容 OpenAI 的 API，因此你可以用 OpenAI Python 与 TypeScript SDK 调用它；它使用 Chat Completions 与 Responses API。`bedrock-runtime` 端点通过 AWS SDK 使用 Converse 与 InvokeModel API，并可访问 Guardrails 等 Amazon Bedrock 原生功能。两者的代码示例都在「开始使用」一节中。

## 区域可用性与数据驻留

Amazon Bedrock 在你推理请求的处理位置上提供多种选择。*In-Region* 将每个请求保持在单个区域内，而 *Geographic Cross-Region inference* 在一个地理范围内的多个区域之间路由请求以获得更高吞吐量，因此你的数据始终留在该地理边界之内。对于 AWS GovCloud (US) 中的 NVIDIA Nemotron 与 GPT OSS 模型，选项如下：

- *In-Region inference* 在 `us-gov-west-1`（AWS GovCloud (US-West)）中可用。
- *Geo cross-Region inference* 通过一个专用的 AWS GovCloud (US) 跨区域推理 ID 提供，该 ID 在 `us-gov-west-1` 与 `us-gov-east-1` 之间路由请求。流量保持在 AWS GovCloud (US) 边界内，同时你在两个区域之间获得容错能力。

这些模型的所有推理都留在 AWS GovCloud (US) 边界内。全球跨区域推理（即在世界各地的商业 AWS 区域之间路由请求）在 AWS GovCloud (US) 中不可用。你可以根据自身需求在单区域与 Geo 跨区域之间选择。

## 服务层级

Amazon Bedrock 提供多种[服务层级](https://docs.aws.amazon.com/bedrock/latest/userguide/service-tiers-inference.html)以匹配不同的工作负载需求。对于全部三个模型，均支持 Standard、Priority 与 Flex 层级。

| **服务层级** | **描述** | **是否支持** |
| --- | --- | --- |
| Standard | 按 token 付费、无承诺的访问方式 | 是 |
| Priority | 面向延迟敏感流量的更高吞吐量 | 是 |
| Flex | 面向灵活、对时间不敏感工作负载的低成本访问方式 | 是 |
| Reserved | 带期限承诺的专用吞吐量 | 当前不可用 |

默认情况下，请求使用 Standard 层级上的按需推理，你按 token 付费，无需预先预留容量。对于延迟敏感、面向客户的工作负载，你可以把单个请求路由到 Priority 层级。对于模型评估或批量摘要等对时间不敏感的工作，Flex 层级提供成本更低的选项。有关扩展指导以及如何应对生产规模下的限流，请参阅 [Scaling and throughput best practices](https://docs.aws.amazon.com/bedrock/latest/userguide/scaling-throughput-best-practices.html) 以及「开始使用」一节。

## 在 AWS GovCloud (US) 中开始使用

本节逐步介绍如何调用这些模型，先从推荐的 `bedrock-mantle` 端点开始。示例使用 `us-gov-west-1` 区域，该区域提供 in-Region 推理。

### 控制台 Playground

- 在你的 AWS GovCloud (US) 账户中，打开 [Amazon Bedrock 控制台](https://console.amazonaws-us-gov.com/bedrock/)。
- 在左侧菜单的 **Test** 分组下选择 **Playground**。
- 选择 **Select model**。
- 在类别列表中选择提供商（**NVIDIA** 或 **OpenAI**），然后选择模型（例如 **NVIDIA Nemotron 3 Super** 或 **120B gpt-oss-120b**）。
- 选择 **Apply** 以加载模型。
- 输入一个 prompt 来测试模型。

### 使用 bedrock-mantle 端点（推荐）

要使用这些模型，你需要一个位于 AWS GovCloud (US) 的 AWS 账户，并具备调用 Amazon Bedrock 模型的权限。对于 `bedrock-mantle` 端点，你需要一个 [Amazon Bedrock API key](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html) 或标准 AWS 凭证。以下是一份示例策略：

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

将 `111122223333` 替换为你的 AWS 账户 ID，并把 Region 限定为你所使用的 AWS GovCloud (US) 区域。本文中的代码示例使用 Bedrock API key 进行身份验证，这需要 `bedrock-mantle:CallWithBearerToken` 权限。该操作必须按第二条语句所示，把范围限定为 `"Resource": "*"`。要控制哪些身份可以生成或使用 Amazon Bedrock API key，请参阅 [Control permissions for generating and using Amazon Bedrock API keys](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html)。若要把你的组织限制为仅可使用已批准的模型，请使用[服务控制策略（SCP）](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html)。

以下示例使用 [OpenAI Python SDK](https://github.com/openai/openai-python) 调用 `bedrock-mantle` 端点。对于生产工作负载，请使用短期 API key：它们会自动过期（最长 12 小时），并继承生成它们的 IAM 角色的权限。

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

**注意：**这些示例从 [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/) 获取 Bedrock API key。在本地开发时，你也可以改为从环境变量读取该 key，但请避免在生产环境中使用这种模式。请使用 AWS Secrets Manager 或其他密钥存储。

若要改为调用 NVIDIA Nemotron 3 Super 120B，请把 model 参数改为 `nvidia.nemotron-super-3-120b` 并移除 `reasoning_effort` 参数（推理强度控制是 GPT OSS 特有的）。无需其他代码改动。

#### 控制推理强度

GPT OSS 模型是推理模型，暴露了可调的推理强度。在 Chat Completions 调用上把 `reasoning_effort` 参数设为 `low`、`medium` 或 `high`，即可在响应延迟与推理深度之间做权衡。高并发、延迟敏感的流量请使用 `low`，复杂多步推理或 agentic 规划请使用 `high`。对于推理模型，建议用 `max_completion_tokens` 来限制响应长度（较旧的 `max_tokens` 字段仍被接受）。

#### 使用 Responses API

除 Chat Completions 之外，GPT OSS 模型还支持 Responses API，即 OpenAI 面向推理式交互的接口。它接收单个 `input`，而不是 `messages` 数组。NVIDIA Nemotron 3 Super 120B 不支持 Responses API，对该模型请使用 Chat Completions、Converse 或 Invoke。

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

#### 流式响应

对于希望把 token 在生成过程中即时呈现给用户的聊天与 agent 用例，请设置 `stream=True`。响应会变成一个增量 delta 事件的迭代器：

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

在 `bedrock-runtime` 端点上，实现同等能力需要 `bedrock:InvokeModelWithResponseStream` 权限，后文展示的最小策略已授予该权限。

#### 工具调用

NVIDIA Nemotron 与 GPT OSS 开放权重模型为 agentic 工作流而设计，因此在工具调用场景中颇具实用性。在工具调用工作流中，你定义模型可以调用的函数（工具），模型根据用户的请求决定何时调用它们，你的应用执行该函数并把结果返回给模型，让模型将其纳入最终响应。

以下示例端到端地演示了这种模式。我们定义一个 `get_weather` 工具，发送一条用户消息，让模型发起工具调用请求，用模拟数据运行该函数，再把结果传回，使模型能够生成自然语言的回答。

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

此处展示的示例演示的是客户端工具调用：模型返回一个工具调用，你的应用执行该函数，然后你把结果传回。在 `bedrock-mantle` 上，GPT OSS 模型同时支持客户端与服务端工具调用，而 NVIDIA Nemotron 3 Super 120B 仅支持客户端工具调用。两个模型家族也都可以通过 Converse API（使用 `toolConfig`）在 `bedrock-runtime` 端点上进行工具调用。完整的功能矩阵请参阅各模型的[模型卡](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards.html)。

### 使用 bedrock-runtime 端点（boto3）

对于 `bedrock-runtime` 端点，你需要配置好具备调用该模型权限的 AWS 凭证（AWS Identity and Access Management（IAM）用户或角色）。以下是一份示例策略：

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

对于生产部署，请把 `Resource` 限定为你所使用的具体 AWS GovCloud (US) 区域与模型 ID。

以下示例使用 [AWS SDK for Python (boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) 通过 Converse API 发送单轮请求。在 `bedrock-runtime` 端点上，GPT OSS 的模型 ID 带有版本后缀（例如 `openai.gpt-oss-120b-1:0`）。请使用各模型卡中的确切模型 ID。响应包含一个推理块，其后是一个文本块，因此该示例在打印答案时会选择文本块。

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

若要通过 `bedrock-runtime` 调用 NVIDIA Nemotron 3 Super 120B，请使用模型 ID `nvidia.nemotron-super-3-120b`（该模型 ID 不带版本后缀）。

你也可以使用 [AWS Command Line Interface（AWS CLI）](https://docs.aws.amazon.com/cli/latest/reference/bedrock-runtime/) 从终端访问这些模型：

```
aws bedrock-runtime converse \
--model-id openai.gpt-oss-120b-1:0 \
--messages '[{"role":"user","content":[{"text":"Type_Your_Prompt_Here"}]}]' \
--inference-config '{"maxTokens":512}' \
--region us-gov-west-1
```

### 扩展按需推理

Standard 层级上的按需容量是共享的，并按 AWS 区域分配，因此在区域需求高峰时段，请求可能会被短暂排队或限流。在 `bedrock-mantle` 端点上没有每分钟请求数配额，吞吐量由基于 token 的限制来管控。这些开放权重模型目前在 Service Quotas 控制台中尚未发布按账户的 token 配额，因此请使用带指数退避的重试逻辑来处理暂时性限流。Amazon Bedrock 会返回两个 HTTP 错误码，用来指示请求无法被处理：

| **错误码** | **含义** | **建议操作** |
| --- | --- | --- |
| 429 | 请求被拒绝，因为它超出了该账户的 Amazon Bedrock 配额。 | 通过 Service Quotas 控制台申请提高配额，并在客户端实施限流。 |
| 503 | 服务正经历高需求或临时的容量限制。 | 使用指数退避加抖动重试。如果限流持续，请降低请求速率并逐步恢复。 |

对于暂时性的 503 响应，请在 SDK 中配置自动重试：

```
import boto3
from botocore.config import Config

config = Config(retries={"total_max_attempts": 6, "mode": "standard"})
client = boto3.client("bedrock-runtime", config=config)
```

在持续限流之后恢复时，请在每次提升之间以稳定状态保持约 15 分钟，而不是直接跳到目标吞吐量。有关更详细的爬坡流程与更多最佳实践，请参阅 Amazon Bedrock User Guide 中的 [Scaling and throughput best practices](https://docs.aws.amazon.com/bedrock/latest/userguide/scaling-throughput-best-practices.html)。

### 清理资源

这些模型使用按需推理，仅在你调用模型时产生费用，因此没有需要拆除的端点或基础设施。为避免测试后产生意外费用：

如果你生成了短期 Bedrock API key，它们会自动过期（最长 12 小时）。若要更早撤销，请在 Amazon Bedrock 控制台中将其删除。

如果你在测试时选择了 Priority 层级，请从调用中移除 `service_tier` 参数，让非延迟敏感的流量回到 Standard 定价。

如果你为测试把 Bedrock API key 存放在 AWS Secrets Manager 中，请删除该密钥以避免存储费用。

有关按模型与层级划分的定价详情，请参阅 [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/)。

## 定价与可用性

OpenAI GPT OSS 与 NVIDIA Nemotron 模型自今日起在 AWS GovCloud (US) 的 Amazon Bedrock 上可用。In-Region 推理在 AWS GovCloud (US-West)（`us-gov-west-1`）中可用；Geo 跨区域推理在 AWS GovCloud (US-West) 与 AWS GovCloud (US-East)（`us-gov-east-1`）之间路由请求，同时让流量保持在 AWS GovCloud (US) 边界内。

定价按 token 计，并因模型与服务层级而异。Standard 层级上的按需推理在你调用模型时产生费用，无需预留容量，也没有需要拆除的基础设施。当前费率请参阅 [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/)。

## 结语

OpenAI GPT OSS 与 NVIDIA Nemotron 模型现已在 AWS GovCloud (US) 的 Amazon Bedrock 上可用，让政府客户能够在其合规边界内使用先进的开放权重模型。本文介绍了可用的模型及其能力、调用这些模型的两个端点、可用的服务层级以及扩展指导。政府团队可以为任务工作负载运行这些开放权重模型，同时把推理保持在 AWS GovCloud (US) 边界内由 AWS 运营的基础设施上。

**开始使用：**

- 在你的 AWS GovCloud (US) 账户中打开 [Amazon Bedrock 控制台](https://console.amazonaws-us-gov.com/bedrock/)，并在 **Playground** 中试用这些模型。
- 用你自己的数据运行本文中的 `bedrock-mantle` Python 示例。
- 在你的工作负载上评估 gpt-oss-120b、gpt-oss-20b 与 NVIDIA Nemotron 3 Super 120B，以选择符合你成本与延迟特征的模型。
- 对于生产部署，请查阅 [Scaling and throughput best practices](https://docs.aws.amazon.com/bedrock/latest/userguide/scaling-throughput-best-practices.html)，并为延迟敏感的流量考虑使用 Priority 层级。

## 资源

更多信息请参阅以下资源：

- [AWS GovCloud (US)](https://aws.amazon.com/govcloud-us/)
- [Amazon Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)
- [OpenAI models on Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-openai.html)
- [NVIDIA Nemotron 3 Super 120B model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-nvidia-nemotron-super-3-120b.html)
- [Exploring the zero operator access design of Mantle](https://aws.amazon.com/blogs/machine-learning/exploring-the-zero-operator-access-design-of-mantle/)
- [Amazon Bedrock service tiers](https://docs.aws.amazon.com/bedrock/latest/userguide/service-tiers-inference.html)
- [Amazon Bedrock API keys](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html)

## 关于作者
