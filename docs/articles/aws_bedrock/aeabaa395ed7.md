---
vendor: aws_bedrock
title: Introducing structured output for Custom Model Import in Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/introducing-structured-output-for-custom-model-import-in-amazon-bedrock
date: 2025-11-07
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 04124d9e19eb
---

# Amazon Bedrock 的 Custom Model Import 推出结构化输出

借助 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 的 [Custom Model Import](https://aws.amazon.com/bedrock/custom-model-import/)，你可以在全托管、无服务器的环境中部署并扩展微调过的或专有的基础模型。你可以把自己的模型带入 Amazon Bedrock，在无需管理基础设施的前提下安全地扩展它们，并与其他 Amazon Bedrock 能力集成。

今天，我们很高兴宣布 Custom Model Import 新增了结构化输出能力。结构化输出会实时约束模型的生成过程，使它产生的每一个 token 都符合你定义的 schema。你不再需要依赖 prompt 工程技巧或脆弱的后处理脚本，现在可以在推理时直接生成结构化输出。

对某些生产应用来说，模型输出的可预测性比它的创作灵活性更重要。客服聊天机器人或许受益于多样、自然的回答，但订单处理系统需要符合预定义 schema 的精确结构化数据。结构化输出弥合了这一差距：它保留基础模型的智能，同时校验其输出满足严格的格式要求。

这标志着从自由文本生成转向一致、机器可读、并为与企业系统无缝集成而设计的输出。自由文本很适合人阅读，而生产应用需要更高的精确度。当企业的系统依赖结构化输出来可靠地与 API、数据库和自动化工作流对接时，它们无法承受自然语言变体带来的歧义。

本文中，你将学习如何在 Amazon Bedrock 的 Custom Model Import 中实现结构化输出。我们会介绍结构化输出是什么、如何在 API 调用中启用它，以及如何把它应用到需要结构化、可预测输出的真实场景中。

## 理解结构化输出

结构化输出也称为受约束解码（constrained decoding），是一种引导 LLM 输出符合预定义 schema（例如合法 JSON）的方法。它不让模型基于概率分布自由选择 token，而是在生成过程中引入约束，把可选项限制在那些能保持结构合法性的 token 上。如果某个 token 会因产生非法 JSON、插入多余字符或使用意料之外的字段名而违反 schema，结构化输出就会拒绝它，并要求模型改选另一个允许的选项。这种实时校验有助于让最终输出保持一致、机器可读，并可直接被下游应用使用，无需额外后处理。

在没有结构化输出时，开发者常常通过类似“*仅以 JSON 回答*”这样的 prompt 指令来强制结构。这种做法有时有效，但由于 LLM 固有的概率性，它并不可靠。这些模型通过对概率分布采样来生成文本，由此带来的自然变化让回答更有人味，却给自动化系统造成了很大挑战。

设想一个对工单进行分类的客户支持应用：如果回答在“*这看起来像计费问题*”，“*我会把它归类为：计费*”和“*类别 = BILLING*”之间变化，下游代码就无法可靠地解释这些结果。生产系统真正需要的是可预测的结构化输出。例如：

```
{
  "category": "billing",
  "priority": "high",
  "sentiment": "negative"
}
```

有了这样的响应，你的应用可以自动路由工单、触发工作流或更新数据库，而无需人工介入。通过提供可预测、与 schema 对齐的响应，结构化输出把 LLM 从对话工具转变为可集成到数据库、API 和业务逻辑中的可靠系统组件。这项能力为自动化开辟了新的可能，同时保留了构成这些模型价值的智能推理。

除了提升可靠性并简化后处理之外，结构化输出还带来其他好处，可增强生产环境中的性能、安全性与防护能力。

- **更低的 token 用量与更快的响应：** 通过把生成约束在已定义的 schema 上，结构化输出去掉了不必要的冗长自由文本，从而减少 token 数量。由于 token 生成是串行的，更短的输出直接意味着更快的响应和更低的延迟，整体性能与成本效益都得到改善。
- **更强的 prompt 注入防护：** 结构化输出收窄了模型的表达空间，有助于阻止它产生任意或不安全的内容。恶意行为者无法在既定结构之外注入指令、代码或意外文本。每个字段都必须匹配预期的类型与格式，从而确保输出始终处于安全边界之内。
- **安全与策略控制：** 结构化输出让你可以设计本身就有助于防止有害、有毒或违反策略内容的 schema。通过把字段限定为获批取值、强制使用既定模式并限制自由文本，schema 能确保输出符合监管要求。

下一节中，我们将探讨结构化输出如何在 Amazon Bedrock 的 Custom Model Import 中工作，并逐步演示一个在你的 API 调用中启用它的示例。

## 在 Amazon Bedrock 的 Custom Model Import 中使用结构化输出

我们首先假设你已经使用 Custom Model Import 功能把一个 Hugging Face 模型导入到 Amazon Bedrock 中。

### 前提条件

在继续之前，请确保你具备：

- 一个有效、可访问 Amazon Bedrock 的 AWS 账户
- 一个使用 Custom Model Import 功能在 Amazon Bedrock 中创建的自定义模型
- 通过 Amazon Bedrock Runtime 调用模型所需的适当 [AWS Identity and Access Management (IAM)](https://aws.amazon.com/iam/) 权限

具备这些前提条件之后，我们来探讨如何在你导入的模型上实现结构化输出。

要开始在 Amazon Bedrock 的 Custom Model Import 中使用结构化输出，首先配置你的环境。在 Python 中，这包括创建一个 Bedrock Runtime 客户端，并从你导入的 Hugging Face 模型初始化一个 tokenizer。

Bedrock Runtime 客户端通过 Bedrock 的 `InvokeModel` API 提供对你所导入模型的访问。tokenizer 会套用与所导入模型相匹配的正确 chat template，它定义了 user、system 和 assistant 消息如何合并成一个 prompt、角色标记（例如 `<|user|>`、`<|assistant|>`）如何插入，以及模型的响应应该从哪里开始。

通过调用 `tokenizer.apply_chat_template(messages, tokenize=False)`，你可以生成与模型所期望的精确输入格式相匹配的 prompt，这对保持一致而可靠的推理至关重要，尤其在启用结构化编码时。

```
import boto3
from transformers import AutoTokenizer
from botocore.config import Config

# HF model identifier imported into Bedrock
hf_model_id = "<<huggingface_model_id>>" # Example: "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B
model_arn = "arn:aws:bedrock:<<aws-region>>:<<account-id>>:imported-model/your-model-id"
region      = "<<aws-region>>"

# Initialize tokenizer aligned with your imported model 
tokenizer = AutoTokenizer.from_pretrained(hf_model_id)

# Initialize Bedrock client
bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name=region)
```

## 实现结构化输出

当你在 Amazon Bedrock 上调用自定义模型时，可以选择在请求 payload 中加入 `response_format` 块来启用结构化输出。该块接受一个 JSON schema，用来定义模型响应的结构。在推理过程中，模型会实时强制执行这个 schema，确保生成的每个 token 都符合既定结构。下面通过一个简单的地址抽取任务，逐步演示如何实现结构化输出。

### 第 1 步：定义数据结构

你可以用 Pydantic model 定义期望的输出，它充当你要抽取的数据的类型化契约。

```
from pydantic import BaseModel, Field

class Address(BaseModel):
    street_number: str = Field(description="Street number")
    street_name: str = Field(description="Street name including type (Ave, St, Rd, etc.)")
    city: str = Field(description="City name")
    state: str = Field(description="Two-letter state abbreviation")
    zip_code: str = Field(description="5-digit ZIP code")
```

### 第 2 步：生成 JSON schema

Pydantic 可以自动把你的数据模型转换成 JSON schema：

```
schema = Address.model_json_schema()
address_schema = {
    "name": "Address",
    "schema": schema
}
```

这个 schema 定义了每个字段的类型、描述和必填要求，形成一份模型在生成过程中会遵循的蓝图。

### 第 3 步：准备输入消息

使用模型期望的 chat 格式来组织你的输入：

```
messages = [{
    "role": "user",
    "content": "Extract the address: 456 Tech Boulevard, San Francisco, CA 94105"
}]
```

### 第 4 步：套用 chat template

使用模型的 tokenizer 生成格式化后的 prompt：

```
prompt = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)
```

### 第 5 步：构建请求 payload

创建请求体，其中包含引用你的 schema 的 `response_format`：

```
request_body = {
    'prompt': prompt,
    'temperature': 0.1,
    'max_gen_len': 1000,
    'top_p': 0.9,
    'response_format': {
        "type": "json_schema",
        "json_schema": address_schema
    }
}
```

### 第 6 步：调用模型

使用 `InvokeModel` API 发送请求：

```
response = bedrock_runtime.invoke_model(
    modelId=model_arn,
    body=json.dumps(request_body),
    accept="application/json",
    contentType="application/json"
)
```

### 第 7 步：解析响应

从响应中提取生成的文本：

```
result = json.loads(response['body'].read().decode('utf-8'))
raw_output = result['choices'][0]['text']
print(raw_output)
```

由于 schema 定义了必填字段，模型的响应中会包含它们：

```
{
"street_number": "456",
"street_name": "Tech Boulevard",
"city": "San Francisco",
"state": "CA",
"zip_code": "94105"
}
```

输出是干净、合法的 JSON，你的应用可以直接消费，无需额外的解析、过滤或清理。

## 结论

Amazon Bedrock 中配合 Custom Model Import 的结构化输出，提供了一种从你的模型生成结构化、与 schema 对齐输出的有效方式。通过把校验前移到模型推理本身，结构化输出降低了对复杂后处理工作流和错误处理代码的需求。

结构化输出生成的结果可预测、易于集成到你的系统中，并支持多种用例，例如构建需要精确数据抽取的金融应用、需要结构化临床文书的医疗系统，或要求一致工单分类的客户服务系统。

今天就开始在你的 [Custom Model Import](https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-import-model.html) 中试用结构化输出，改变你的 AI 应用交付一致、可用于生产的结果的方式。

### 关于作者

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/07/manoj.png)Manoj Selvakumar** 是 AWS 的生成式 AI 专家解决方案架构师，帮助各类组织在云上设计、原型验证并扩展 AI 驱动的解决方案。他在深度学习、可扩展云原生系统和多 agent 编排方面具备专长，专注于把新兴创新转化为能带来可衡量业务价值的生产级架构。他热衷于让复杂的 AI 概念变得实用，帮助客户在规模化场景下负责任地创新——从早期实验一直到企业级部署。加入 AWS 之前，Manoj 从事咨询工作，为企业客户交付数据科学与 AI 解决方案，构建由完善 MLOps 实践支撑的端到端机器学习系统，覆盖训练、部署和生产监控。

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/06/16/yanyan.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/06/16/yanyan.png)**Yanyan Zhang** 是 Amazon Web Services 的高级生成式 AI 数据科学家，作为生成式 AI 专家从事前沿 AI/ML 技术工作，帮助客户用生成式 AI 达成他们期望的结果。Yanyan 毕业于 Texas A&M University，获得电气工程博士学位。工作之外，她喜欢旅行、健身和探索新事物。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/13/ravi.png)**Lokeshwaran Ravi** 是 AWS 的高级深度学习编译器工程师，专长于 ML 优化、模型加速和 AI 安全。他专注于提升效率、降低成本并构建安全的技术生态，以推动 AI 技术普及，让前沿 ML 在各行各业都易于获得并能产生实际影响。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/11/image-8-4-100x133.png)Revendra Kumar** 是 Amazon Web Services 的高级软件开发工程师。在目前的岗位上，他专注于 Amazon Bedrock 上的模型托管与推理 MLOps。在此之前，他曾担任工程师，负责在云上托管 Quantum 计算机，并为本地云环境开发基础设施解决方案。工作之外，Revendra 喜欢通过打网球和徒步保持活力。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/11/06/image-23-100x100.png)**Muzart Tuman** 是一名软件工程师，运用他在深度学习、机器学习优化和 AI 驱动应用等领域的经验，以可扩展、高效且易于使用的方式帮助解决现实问题。他的目标是打造有影响力的工具，既推进技术能力，也促进行业与社区的实质性改变。
