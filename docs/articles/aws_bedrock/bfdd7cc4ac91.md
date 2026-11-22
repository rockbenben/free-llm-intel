---
vendor: aws_bedrock
title: How GoDaddy built a category generation system at scale with batch inference for Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/how-godaddy-built-a-category-generation-system-at-scale-with-batch-inference-for-amazon-bedrock
date: 2025-03-13
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 7c1edd05d1ce
---

# GoDaddy 如何在 Amazon Bedrock 上用批量推理构建规模化的类别生成系统

*本文与 GoDaddy 数据与分析团队数据工程负责人 Vishal Singh 合写*

[生成式 AI](https://aws.amazon.com/generative-ai/) 解决方案有潜力通过提升生产力、改善客户体验来改变企业，而在这些方案中使用[大语言模型（LLM）](https://aws.amazon.com/what-is/large-language-model/)也变得越来越普遍。然而，当生产环境中承载大量应用时，把 LLM 推理当成单次模型调用或 API 调用，扩展性并不好。

借助批量推理，你可以异步运行多个推理请求，从而高效处理海量请求。你还可以用批量推理来提升大数据集上模型推理的性能。

本文概述一套为 GoDaddy 定制开发的解决方案。GoDaddy 是一家提供域名注册、注册局、网站托管和电商服务的公司，它希望通过生成式 AI 为超过 2,100 万名客户提供个性化的商业洞察——这些洞察此前只有大企业才能获得——从而让创业变得更容易。在这次合作中，生成式 AI 创新中心（Generative AI Innovation Center）团队利用 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 中的批量推理，打造了一套准确且成本高效的生成式 AI 解决方案，帮助 GoDaddy 改进现有的产品分类系统。

## 解决方案概览

GoDaddy 希望增强其产品分类系统，该系统根据产品名称给产品分配类别。例如：

```
Input: Fruit by the Foot Starburst

Output: color -> multi-colored, material -> candy, category -> snacks, product_line -> Fruit by the Foot,…
```

GoDaddy 曾使用开箱即用的 Meta Llama 2 模型，为 600 万个产品生成产品类别，其中每个产品由一个 SKU 标识。生成的类别常常不完整或标注错误。此外，用 LLM 逐个产品做分类被证明是一件成本高昂的事。认识到需要一个更精确、更具成本效益的方案，GoDaddy 转而寻找另一种方法，用更准确、更省钱的方式完成产品分类，以改善客户体验。

该方案使用以下组件来更准确、更高效地对产品进行分类：

- 在 Amazon Bedrock 中使用 [Meta Llama 2](https://aws.amazon.com/bedrock/llama-2/) 和 [Anthropic 的 Claude](https://aws.amazon.com/bedrock/claude/) 模型进行批处理
- [Amazon Simple Storage Service](https://aws.amazon.com/s3/)（Amazon S3）用于存储产品和输出数据
- [AWS Lambda](https://aws.amazon.com/lambda/) 用于编排 Amazon Bedrock 模型

下图展示了关键步骤：

- 包含产品数据的 JSONL 文件被上传到 S3 存储桶，触发第一个 Lambda 函数。Amazon Bedrock 对这单个 JSONL 文件进行批处理，其中每一行都包含输入参数和 prompt。它会生成一个输出 JSONL 文件，在每一行上追加一个新的 `model_output` 值，与输入数据相对应。
- 该 Lambda 函数启动一个 Amazon Bedrock 批处理端点，并传入 S3 文件位置。
- Amazon Bedrock 端点执行以下任务：读取产品名称数据并生成分类输出，包括类别、子类别、季节、价格区间、材质、颜色、产品线、性别和首次销售年份。它把输出写入另一个 S3 位置。
- 第二个 Lambda 函数执行以下任务：监控 Amazon Bedrock 上的批处理作业。处理完成后关闭该端点。

安全措施已经天然集成到该架构所用的 AWS 服务中。详细信息请参阅本文的[安全最佳实践](https://aws.amazon.com/blogs/machine-learning/how-godaddy-built-a-category-generation-system-at-scale-with-batch-inference-for-amazon-bedrock/#_Security_Best_Practices)一节。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/01/29/Picture1_godaddy.png)

我们使用的数据集由 30 个有标注数据点和 100,000 个无标注测试数据点组成。有标注的数据点由 llama2-7b 生成，并由人工领域专家（SME）核验。如下面的样本 ground truth 截图所示，有些字段是 N/A 或缺失值，这并不理想，因为 GoDaddy 希望方案在下游预测建模中具有高覆盖率。每个可能字段的覆盖率越高，就能为客户提供越多的商业洞察。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/01/29/Screenshot-2025-01-29-at-9.28.11 AM.png)

每个 SKU 的词数或 token 数分布显示出轻微的离群值隐患，这适合在 prompt 中捆绑多个待分类产品，从而可能获得更高效的模型响应。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/01/29/Picture2-bp-chart.jpg)

该方案提供了一个完整的框架，用于在 GoDaddy 的产品分类系统中生成洞察。它被设计为兼容 Amazon Bedrock 上的一系列 LLM，具备可定制的 prompt 模板，并支持批量推理与实时（在线）推理。此外，该框架还包含可扩展的评估指标，以适应准确率需求的变化。

在接下来的几节中，我们会更详细地介绍该方案的关键组件。

## 批量推理

我们使用 Amazon Bedrock 进行批量推理处理。Amazon Bedrock 提供 `CreateModelInvocationJob` API，用于创建一个带唯一作业名称的批处理作业。该 API 返回的响应中包含 `jobArn`。请参考以下代码：

```
Request: POST /model-invocation-job HTTP/1.1

Content-type: application/json
{
  "clientRequestToken": "string",
  "inputDataConfig": {
    "s3InputDataConfig": {
      "s3Uri": "string",
      "s3InputFormat": "JSONL"
    }
   },
  "jobName": "string",
  "modelId": "string",
  "outputDataConfig": {
    "s3OutputDataConfig": {
      "s3Uri": "string"
    }
  },
  "roleArn": "string",
  "tags": [{
  "key": "string",
  "value": "string"
  }]
}

Response
HTTP/1.1 200 Content-type: application/json
{
  "jobArn": "string"
}
```

我们可以用作业创建时返回的 `jobArn`，通过 `GetModelInvocationJob` 监控作业状态。以下是作业生命周期中的有效状态：

- **Submitted** – 当 JSON 文件已就绪、可以由 Amazon Bedrock 进行推理处理时，作业被标记为 **Submitted**。
- **InProgress** – 当 Amazon Bedrock 开始处理该 JSON 文件时，作业被标记为 **InProgress**。
- **Failed** – 如果处理过程中出现错误，作业被标记为 **Failed**。错误可以作为 `modelOutput` 的一部分写入 JSON 文件。如果是 4xx 错误，则写入作业的元数据中。
- **Completed** – 当针对输入 JSON 文件生成了输出 JSON 文件，并且该文件已上传到在 `CreateModelInvocationJob` 中通过 `outputDataConfig` 提交的 S3 输出路径时，作业被标记为 **Completed **。
- **Stopped** – 当对一个处于 **InProgress** 的作业调用 `StopModelInvocationJob` API 时，作业被标记为 **Stopped**。处于终态的作业（**Succeeded** 或 **Failed**）无法用 `StopModelInvocationJob` 停止。

以下是 `GetModelInvocationJob` API 的示例代码：

```
GET /model-invocation-job/jobIdentifier HTTP/1.1

Response:
{
  'ResponseMetadata': {
    'RequestId': '081afa52-189f-4e83-a3f9-aa0918d902f4',
    'HTTPStatusCode': 200,
    'HTTPHeaders': {
       'date': 'Tue, 09 Jan 2024 17:00:16 GMT',
       'content-type': 'application/json',
       'content-length': '690',
       'connection': 'keep-alive',
       'x-amzn-requestid': '081afa52-189f-4e83-a3f9-aa0918d902f4'
      },
     'RetryAttempts': 0
   },
  'jobArn': 'arn:aws:bedrock:<region>:<account-id>:model-invocation-job/<id>',
  'jobName': 'job47',
  'modelId': 'arn:aws:bedrock:<region>::foundation-model/anthropic.claude-instant-v1:2',
  'status': 'Submitted',
  'submitTime': datetime.datetime(2024, 1, 8, 21, 44, 38, 611000, tzinfo=tzlocal()),
  'lastModifiedTime': datetime.datetime(2024, 1, 8, 23, 5, 47, 169000, tzinfo=tzlocal()),
  'inputDataConfig': {'s3InputDataConfig': {'s3Uri': <path to input jsonl file>}},
  'outputDataConfig': {'s3OutputDataConfig': {'s3Uri': <path to output jsonl.out file>}}
}
```

作业完成后，s3OutputDataConfig 中指定的 S3 路径下会出现一个以字母和数字命名的新文件夹。该文件夹包含两个文件：

- **json.out** – 以下代码展示了该格式的示例：

```
{
   "processedRecordCount":<number>,
   "successRecordCount":<number>,
   "errorRecordCount":<number>,
   "inputTokenCount":<number>,
   "outputTokenCount":<number>
}
```

- **<file_name>.jsonl.out** – 以下截图展示了代码示例，其中包含成功处理的记录，`modelOutput` 以 JSON 格式给出给定产品名称的类别列表。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/07/Picture2-10.png)

随后我们在 Amazon S3 中处理 `jsonl.out` 文件。该文件通过 LangChain 的 `PydanticOutputParser` 解析，生成一个 .csv 文件。`PydanticOutputParser` 需要一个 schema 才能解析 LLM 生成的 JSON。我们创建了一个 CCData 类，其中包含要为每个产品生成的类别列表，如下面的代码示例所示。由于我们启用了 n-packing，还用 List 包裹了该 schema，定义在 `List_of_CCData` 中。

```
class CCData(BaseModel):
   product_name: Optional[str] = Field(default=None, description="product name, which will be given as input")
   brand: Optional[str] = Field(default=None, description="Brand of the product inferred from the product name")
   color: Optional[str] = Field(default=None, description="Color of the product inferred from the product name")
   material: Optional[str] = Field(default=None, description="Material of the product inferred from the product name")
   price: Optional[str] = Field(default=None, description="Price of the product inferred from the product name")
   category: Optional[str] = Field(default=None, description="Category of the product inferred from the product name")
   sub_category: Optional[str] = Field(default=None, description="Sub-category of the product inferred from the product name")
   product_line: Optional[str] = Field(default=None, description="Product Line of the product inferred from the product name")
   gender: Optional[str] = Field(default=None, description="Gender of the product inferred from the product name")
   year_of_first_sale: Optional[str] = Field(default=None, description="Year of first sale of the product inferred from the product name")
   season: Optional[str] = Field(default=None, description="Season of the product inferred from the product name")

class List_of_CCData(BaseModel): 
   list_of_dict: List[CCData]
```

我们还使用 `OutputFixingParser` 来处理初次解析尝试失败的情况。以下截图展示了一个生成的 .csv 文件样例。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/05/Picture3-5.png)

## Prompt 工程

Prompt 工程指的是巧妙地设计和打磨输入 prompt。这一过程包括挑选合适的词、短语、句子、标点和分隔字符，以便在多样化的应用中高效使用 LLM。本质上，prompt 工程就是与 LLM 有效交互。最有效的 prompt 工程策略需要根据具体任务和数据而变化，具体到本例就是数据卡片（data card）生成和 GoDaddy 的 SKU。

Prompt 由来自用户的特定输入组成，这些输入引导 LLM 根据指定的任务或指令给出合适的响应或输出。这些 prompt 包含若干要素，例如任务或指令本身、周围的上下文、完整示例，以及引导 LLM 组织响应的输入文本。prompt 的构成会随具体用例、数据可得性和手头任务的性质等因素而变化。例如，在[检索增强生成](https://aws.amazon.com/what-is/retrieval-augmented-generation/)（RAG）用例中，我们会提供额外的上下文，并在 prompt 中加入用户提供的查询，要求 LLM 聚焦于能够回答该查询的上下文。在元数据生成的用例中，我们可以提供图片，并要求 LLM 以特定格式生成描述该图片的说明和关键词。

在本文中，我们粗略地把 prompt 工程方案分为两步：输出生成和格式解析。

### 输出生成

以下是输出生成的最佳实践和注意事项：

- **提供简单、清晰且完整的指令** – 这是 prompt 工程工作的通用准则。
- **一致地使用分隔字符** – 在这个用例中，我们使用换行符 \n
- **处理 missing 之类的默认输出值** – 在这个用例中，我们不想要 N/A 或 missing 这类特殊值，因此把多条指令串在一起，力求排除默认值或缺失值。
- **使用 few-shot prompting** – 也称*上下文学习（in-context learning）*，few-shot prompting 就是提供少量示例，这有助于 LLM 更有效地理解输出要求。在这个用例中，我们针对 Llama 2 和 Anthropic 的 Claude 模型分别测试了 0–10 个上下文示例。
- **使用 packing 技巧** – 我们把多个 SKU 和产品名称合并到一次 LLM 查询中，这样一些 prompt 指令就能在不同 SKU 之间共享，以优化成本和延迟。在这个用例中，我们针对 Llama 2 和 Anthropic 的 Claude 模型分别测试了 1–10 的 packing 数。
- **测试良好的泛化能力** – 你应当保留一个留出测试集和正确的响应，用来检验对 prompt 的修改是否能泛化。
- **为 Anthropic 的 Claude 模型系列使用额外技巧** – 我们采用了以下技巧：把示例包在 XML 标签中：

```
<example>
H: <question> The list of product names is:
{few_shot_product_name} </question>
A: <response> The category information generated with absolutely no missing value, in JSON format is:
{few_shot_field} </response>
</example>
```

- 使用 Human 和 Assistant 标注：

```
\n\nHuman:
...
...
\n\nAssistant:
```

- 引导 assistant 的 prompt：

```
\n\nAssistant: Here are the answer with NO missing, unknown, null, or N/A values (in JSON format):
```

- **为 Llama 模型系列使用额外技巧** – 对于 Llama 2 模型系列，你可以把示例包在 [INST] 标签中：

```
[INST]
If the list of product names is:
{few_shot_product_name}
[/INST]

Then the answer with NO missing, unknown, null, or N/A values is (in JSON format):

{few_shot_field}

[INST]
If the list of product names is:
{product_name}
[/INST]

Then the answer with NO missing, unknown, null, or N/A values is (in JSON format):
```

### 格式解析

以下是格式解析的最佳实践和注意事项：

- **用修饰词细化 prompt** – 对任务说明的细化，通常涉及改动 prompt 中的指令、任务或问题部分。这些技巧的效果因任务和数据而异。这个用例中一些有效的策略包括：**角色设定** – 让模型假定自己正在扮演某个角色。例如：

你是一名产品信息经理、分类学家和分类专家，善于遵循指令。

- **Prompt 的具体性**：非常具体并向模型提供详细指令，有助于为所需任务生成更好的响应。

每一条类别信息都需要同时依据产品名称和你最好的判断来填写。如果你忘记生成任何类别信息、把它留成 missing 或 N/A，就会有无辜的人丧命。

- **描述输出格式** – 我们既通过一个 JSON 字符串直接给出 JSON 格式的指令，也通过 few-shot 示例间接给出。

- **注意 few-shot 示例的格式** – LLM（Anthropic 的 Claude 和 Llama）对细微的格式差异很敏感。在对 few-shot 示例的格式做了几次迭代之后，解析时间显著改善。最终的方案如下：

```
few_shot_field='{\"list_of_dict\"' +
':[' +
', \n'.join([true_df.iloc[i].to_json() for i in range(num_few_shot)]) +
']}'
```

- **为 Anthropic 的 Claude 模型系列使用额外技巧 **– 对于 Anthropic 的 Claude 模型，我们指示它按 JSON 格式输出：

```
{
    "list_of_dict": [{
        "some_category": "your_generated_answer",
        "another_category": "your_generated_answer",
    },
    {
        <category information for the 2st product name, in json format>
    },
    {
        <category information for the 3st product name, in json format>
    },
// ... {additional product information, in json format} ...
    }]
}
```

- **为 Llama 2 模型系列使用额外技巧 **– 对于 Llama 2 模型，我们指示它按如下 JSON 格式输出：

按 JSON 格式输出你的结果（务必对特殊字符做转义）：
 输出应当被格式化为符合以下 JSON schema 的 JSON 实例。
 举例来说，对于 schema `{"properties": {"foo": {"title": "Foo", "description": "a list of strings", "type": "array", "items": {"type": "string"}}}, "required": ["foo"]}`
 对象 `{"foo": ["bar", "baz"]}` 是该 schema 的一个格式良好的实例。对象 `{"properties": {"foo": ["bar", "baz"]}}` 则不是格式良好的。

以下是输出 schema：

`{“properties”: {“list_of_dict”: {“title”: “List Of Dict”, “type”: “array”, “items”: {“$ref”: “#/definitions/CCData”}}}, “required”: [“list_of_dict”], “definitions”: {“CCData”: {“title”: “CCData”, “type”: “object”, “properties”: {“product_name”: {“title”: “Product Name”, “description”: “product name, which will be given as input”, “type”: “string”}, “brand”: {“title”: “Brand”, “description”: “Brand of the product inferred from the product name”, “type”: “string”}, “color”: {“title”: “Color”, “description”: “Color of the product inferred from the product name”, “type”: “string”}, “material”: {“title”: “Material”, “description”: “Material of the product inferred from the product name”, “type”: “string”}, “price”: {“title”: “Price”, “description”: “Price of the product inferred from the product name”, “type”: “string”}, “category”: {“title”: “Category”, “description”: “Category of the product inferred from the product name”, “type”: “string”}, “sub_category”: {“title”: “Sub Category”, “description”: “Sub-category of the product inferred from the product name”, “type”: “string”}, “product_line”: {“title”: “Product Line”, “description”: “Product Line of the product inferred from the product name”, “type”: “string”}, “gender”: {“title”: “Gender”, “description”: “Gender of the product inferred from the product name”, “type”: “string”}, “year_of_first_sale”: {“title”: “Year Of First Sale”, “description”: “Year of first sale of the product inferred from the product name”, “type”: “string”}, “season”: {“title”: “Season”, “description”: “Season of the product inferred from the product name”, “type”: “string”}}}}}`

## 模型与参数

我们使用了以下 prompt 参数：

- **packing 数量** – 1、5、10
- **上下文示例数量** – 0、2、5、10
- **格式指令** – JSON 格式伪示例（长度较短）、JSON 格式完整示例（长度较长）

对于 Llama 2，模型选择为 meta.llama2-13b-chat-v1 或 meta.llama2-70b-chat-v1。我们使用了以下 LLM 参数：

```
{
    "temperature": 0.1,
    "top_p": 0.9,
    "max_gen_len": 2048,
}
```

对于 Anthropic 的 Claude，模型选择为 anthropic.claude-instant-v1 和 anthropic.claude-v2。我们使用了以下 LLM 参数：

```
{
   "temperature": 0.1,
   "top_k": 250,
   "top_p": 1,
   "max_tokens_to_sample": 4096,
   "stop_sequences": ["\n\nHuman:"],
   "anthropic_version": "bedrock-2023-05-31"
}
```

该方案可以很直接地扩展到 Amazon Bedrock 上托管的其他 LLM，例如 [Amazon Titan](https://aws.amazon.com/bedrock/titan/)（比如把模型 ID 换成 amazon.titan-tg1-large）、[Jurassic](https://aws.amazon.com/bedrock/jurassic/)（模型 ID 为 ai21.j2-ultra）等等。

## 评估

该框架包含可进一步扩展的评估指标，以适应准确率需求的变化。目前它涉及五项不同的指标：

- **内容覆盖率 **– 衡量输出生成步骤中缺失值的占比。
- **解析覆盖率 **– 衡量格式解析步骤中缺失样本的占比：**产品名称上的解析召回率** – 精确匹配可以作为解析完整度的下界（解析覆盖率则是解析完整度的上界），因为有些情况下两个几乎相同的产品名称需要经过归一化和变换才能精确匹配（例如 “Nike Air Jordan” 和 “nike. air Jordon”）。**产品名称上的解析精确率** – 对于精确匹配，我们使用与解析召回率类似的指标，但用精确率而不是召回率。
- **最终覆盖率 **– 衡量输出生成和格式解析两个步骤中缺失值的占比。
- **人工评估 **– 侧重于整体质量评估，例如文本生成的准确性、相关性和全面性（丰富度）。

## 结果

以下是在一些表现最佳的设置下，近似的样本输入与输出长度：

- **Llama 2 模型系列的输入长度** – 10-shot 为 2,068 tokens，5-shot 为 1,585 tokens，2-shot 为 1,319 tokens
- **Anthropic 的 Claude 模型系列的输入长度** – 10-shot 为 1,314 tokens，5-shot 为 831 tokens，2-shot 为 566 tokens，zero-shot 为 359 tokens
- **5-packing 时的输出长度** – 约 500 tokens

### 定量结果

下表汇总了我们整合后的定量结果。

- 为简洁起见，表中只包含我们对每种模型类型的部分最终建议。
- 所用指标是延迟和准确率。
- 最佳模型和结果以绿色和粗体高亮显示。

| **配置** | **延迟** | **准确率** |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **批处理服务** | **模型** | **Prompt** | **批处理延迟（5 packing）** | **近实时处理延迟（1 packing）** | **程序化评估（覆盖率）** |  |  |  |
| 测试集 = 20 | 测试集 = 5k | GoDaddy 需求 @ 5k | 解析精确匹配的召回率 | 最终内容覆盖率 |  |  |  |  |
| Amazon Bedrock 批量推理 | Llama2-13b | zero-shot | n/a | n/a | 3600s | n/a | n/a | n/a |
| 5-shot (template12) | 65.4s | 1704s | 3600s | 72/20=3.6s | 92.60% | 53.90% |  |  |
| Llama2-70b | zero-shot | n/a | n/a | 3600s | n/a | n/a | n/a |  |
| 5-shot (template13) | 139.6s | 5299s | 3600s | 156/20=7.8s | 98.30% | 61.50% |  |  |
| **Claude-v1 (instant)** | **zero-shot (template6)** | **29s** | 723s | 3600s | **44.8/20=2.24s** | 98.50% | **96.80%** |  |
| 5-shot (template12) | 30.3s | **644s** | 3600s | 51/20=2.6s | 99% | 84.40% |  |  |
| Claude-v2 | zero-shot (template6) | 82.2s | 1706s | 3600s | 104/20=5.2s | 99% | 84.40% |  |
| 5-shot (template14) | 49.1s | 1323s | 3600s | 104/20=5.2s | **99.40%** | 90.10% |  |  |

以下表格汇总了批量推理中的扩展效果。

- 当从 5,000 个样本扩展到 100,000 个样本时，只多需要八倍的计算时间。
- 如果对每个产品都用单独的 LLM 调用完成分类，那么 100,000 个产品的推理时间会比批处理方法多大约 40 倍。
- 覆盖率上的准确率保持稳定，成本则大致线性扩展。

| **批处理服务** | **模型** | **Prompt** | **批处理延迟（5 packing）** | **近实时处理延迟（1 packing）** |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 测试集 = 20 | 测试集 = 5k | GoDaddy 需求 @ 5k | 测试集 = 100k |  |  |  |  |
| Amazon Bedrock 批量 | Claude-v1 (instant) | zero-shot (template6) | 29s | 723s | 3600s | 5733s | 44.8/20=2.24s |
| Amazon Bedrock 批量 | Anthropic 的 Claude-v2 | zero-shot (template6) | 82.2s | 1706s | 3600s | 7689s | 104/20=5.2s |

| **批处理服务** | **近实时处理延迟（1 packing）** | **程序化评估（覆盖率）** |  |  |  |
| --- | --- | --- | --- | --- | --- |
| 产品名称上的解析召回率（测试集 = 5k） | 产品名称上的解析召回率（测试集 = 100k） | 最终内容覆盖率（测试集 = 5k） | 最终内容覆盖率（测试集 = 100k） |  |  |
| Amazon Bedrock 批量 | 44.8/20=2.24s | 98.50% | 98.40% | 96.80% | 96.50% |
| Amazon Bedrock 批量 | 104/20=5.2s | 99% | 98.80% | 84.40% | 97% |

下表汇总了 n-packing 的效果。Llama 2 的输出长度上限为 2,048，最多大约能容纳 20 个 packing。Anthropic 的 Claude 上限更高。我们在 20 个 ground truth 样本上测试了 1、5 和 10 个 packing，并从所有模型和 prompt 模板中挑选结果。在 Anthropic 的 Claude 模型系列上，延迟的扩展效果比 Llama 2 更明显。在输出中增加 packing 数时，Anthropic 的 Claude 的泛化能力比 Llama 2 更好。

我们只对 Llama 2 模型试了少量 shot，与 zero-shot 相比准确率有所提升。

| **批处理服务** | **模型** | **Prompt** | **延迟 **（测试集 = 20） |  |  | **准确率 **（最终覆盖率） |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  | npack = 1 | npack= 5 | npack = 10 | npack = 1 | npack= 5 | npack = 10 |
| Amazon Bedrock 批量推理 | Llama2-13b | 5-shot (template12) | 72s | 65.4s | 65s | 95.90% | 93.20% | 88.90% |
|  | Llama2-70b | 5-shot (template13) | 156s | 139.6s | 150s | 85% | 97.70% | 100% |
|  | Claude-v1 (instant) | zero-shot (template6) | 45s | 29s | 27s | 99.50% | 99.50% | 99.30% |
|  |  | 5-shot (template12) | 51.3s | 30.3s | 27.4s | 99.50% | 99.50% | 100% |
|  | Claude-v2 | zero-shot (template6) | 104s | 82.2s | 67s | 85% | 97.70% | 94.50% |
|  |  | 5-shot (template14) | 104s | 49.1s | 43.5s | 97.70% | 100% | 99.80% |

### 定性结果

我们注意到以下定性结果：

- **人工评估 **– 生成的类别由 GoDaddy 的 SME 做了定性评估。结果发现类别质量良好。
- **经验教训 **– 我们把 LLM 用在两次独立的调用中：输出生成和格式解析。我们观察到以下情况：在这个用例中，我们发现 Llama 2 在格式解析上表现不佳，但在输出生成上相对有能力。为了保持一致并做公平比较，我们要求两次调用所用的 LLM 相同——两步中的 API 调用要么都调用 `llama2-13b-chat-v1`，要么都调用 `anthropic.claude-instant-v1`。不过，GoDaddy 选择 Llama 2 作为类别生成的 LLM。在这个用例中，我们发现只在输出生成中使用 Llama 2、在格式解析中使用 Anthropic 的 Claude 是合适的，因为 Llama 2 的模型能力相对较低。格式解析可以通过 prompt 工程（JSON 格式指令至关重要）来改善，从而降低延迟。例如，在 20 个测试集上使用 Anthropic 的 Claude-Instant 并对多个 prompt 模板取平均，延迟可以降低约 77%（从 90 秒降到 20 秒）。这直接免除了使用 JSON 微调版 LLM 的必要性。
- **Llama2 **– 我们观察到以下情况：Llama2-13b 和 Llama2-70b 模型在 zero-shot prompt 中都需要完整指令，即 `format_instruction()`。Llama2-13b 在内容覆盖率和格式上似乎更差（例如，它无法正确转义字符 `\\`“），这会带来可观的解析时间和成本，也会降低准确率。当 packing 数在 1、5 和 10 之间变化时，Llama 2 表现出明显的性能下降和不稳定，说明与 Anthropic 的 Claude 模型系列相比泛化能力更差。
- **Anthropic 的 Claude **– 我们观察到以下情况：Anthropic 的 Claude-Instant 和 Claude-v2 无论使用 zero-shot 还是 few-shot prompting，都只需要部分格式指令，而不是完整指令 `format_instruction()`。这缩短了输入长度，因此更具成本效益。这也说明 Anthropic 的 Claude 在遵循指令方面的能力更强。当 packing 数在 1、5 和 10 之间变化时，Anthropic 的 Claude 泛化良好。

## 业务层面的收获

我们得到以下关键的业务收获：

- **延迟改善** – 我们的方案能在 12 分钟内完成 5,000 个产品的推理，比 GoDaddy 的需求（1 小时内完成 5,000 个产品）快 80%。在 Amazon Bedrock 中使用批量推理展现了高效的批处理能力，并且预计还有进一步的扩展空间，因为 AWS 计划部署更多的云实例。这种扩展将带来更多的时间和成本节省。
- **更具成本效益** – 生成式 AI 创新中心使用 Anthropic 的 Claude-Instant 构建的方案，比使用 Llama2-13b 的现有方案便宜 8%，同时覆盖率还高出 79%。
- **更高的准确率** – 交付成果在 5,000 和 100,000 个留出测试集上都达到了 97% 的类别覆盖率，超过 GoDaddy 90% 的需求。这个完整的框架能够推动未来对当前模型参数和 prompt 模板的迭代改进。
- **定性评估** – 经 GoDaddy 的 SME 人工评估，类别生成的质量令人满意。

## 技术层面的收获

我们得到以下关键的技术收获：

- 该方案同时具备批量推理和近实时推理（每个产品 2 秒）的能力，并支持多种后端 LLM 选择。
- Anthropic 的 Claude-Instant 配合 zero-shot 明显是最优解：在 5,000 个留出测试集上，它在延迟、成本和准确率上都是最好的。它对更高的 packing 数（一次查询中的 SKU 数量）表现出更好的泛化能力，还可能带来更多的成本和延迟改善。
- 对 prompt 模板做迭代，在所有测试模型中都能看到改善，这说明良好的 prompt 工程是类别生成任务的一种实用方法。
- 在输入方面，增加到 10-shot 可能进一步提升表现（这一点在小规模科学实验中观察到），但也会让成本增加约 30%。因此，我们在大规模批处理实验中最多只测到 5-shot。
- 在输出方面，增加到 10-packing 甚至 20-packing（仅限 Anthropic 的 Claude；Llama 2 的输出长度上限为 2,048）可能进一步改善延迟和成本（因为更多 SKU 可以共享相同的输入指令）。
- 在这个用例中，我们发现 Anthropic 的 Claude 模型系列具有更好的准确率和泛化能力，例如：使用 Anthropic 的 Claude-Instant 时最终类别覆盖率表现更好。当 packing 数从 1、5 增加到 10 时，与 Llama 2 相比，Anthropic 的 Claude-Instant 在延迟上有改善、准确率保持稳定。为实现该用例的最终类别，我们注意到 Anthropic 的 Claude 需要更短的 prompt 输入就能遵循指令，并且对更高的 packing 数有更长的输出长度上限。

## GoDaddy 的后续步骤

以下是 GoDaddy 团队作为后续步骤正在考虑的建议：

- **数据集增强 **– 汇总更大规模的 ground truth 示例，并扩展程序化评估，以更好地监控和改进模型表现。与此相关，如果产品名称能借助领域知识做归一化，更干净的输入也有助于让 LLM 给出更好的响应。例如，产品名称 ”<product_name> Power t-shirt, ladyfit vest or hoodie” 会让 LLM 针对多个 SKU 而不是一个 SKU 作答（类似地，“<product_name> – $5 or $10 or $20 or $50 or $100”）。
- **人工评估 **– 增加人工评估，以提供更高的生成质量并与期望结果对齐。
- **微调 **– 当有更丰富的训练数据集时，考虑把微调作为增强类别生成的潜在策略。
- **Prompt 工程 **– 探索自动化的 prompt 工程技术来增强类别生成，尤其是在有更多训练数据可用时。
- **Few-shot 学习 **– 研究动态 few-shot 选择等技巧，并基于模型的参数知识设计上下文示例，以增强 LLM 的 few-shot 学习能力。
- **知识集成 **– 通过把 LLM 连接到知识库（内部或外部数据库）并让它纳入更多相关信息，来改善模型输出。这有助于减少 LLM 幻觉并提升响应的相关性。

## 结论

在本文中，我们分享了生成式 AI 创新中心团队如何与 GoDaddy 合作，利用 Amazon Bedrock 中的批量推理打造一套更准确、更具成本效益的生成式 AI 解决方案，帮助 GoDaddy 改进现有的产品分类系统。我们实现了 n-packing 技巧，并使用 Anthropic 的 Claude 和 Meta Llama 2 模型来改善延迟。我们尝试了不同的 prompt 来改进 LLM 的分类效果，发现 Anthropic 的 Claude 模型系列比 Llama 2 模型系列具有更好的准确率和泛化能力。GoDaddy 团队将在一个更大的数据集上测试该方案，并评估推荐方法生成的类别。

如果你有兴趣与 AWS 生成式 AI 创新中心合作，请[联系我们](https://aws.amazon.com/generative-ai/innovation-center/)。

## 安全最佳实践

- [Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)
- [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/security.html)
- [StepFunctions](https://docs.aws.amazon.com/step-functions/latest/dg/security.html)
- [AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/lambda-security.html)

## 参考资料

- [SnapLogic 如何借助 Amazon Bedrock 构建把业务意图转化为行动的 text-to-pipeline 应用](https://aws.amazon.com/blogs/machine-learning/how-snaplogic-built-a-text-to-pipeline-application-with-amazon-bedrock-to-translate-business-intent-into-action/)

- [Q4 Inc. 如何借助 Amazon Bedrock、RAG 和 SQLDatabaseChain 解决构建问答 chatbot 时的数值与结构化数据集难题](https://aws.amazon.com/blogs/machine-learning/how-q4-inc-used-amazon-bedrock-rag-and-sqldatabasechain-to-address-numerical-and-structured-dataset-challenges-building-their-qa-chatbot/)

### 关于作者

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/05/Vishal-K-Singh-100x121.png) Vishal Singh **是 GoDaddy 数据与分析团队的数据工程负责人。他的重点方向是借助数据工程工具结合生成式 AI 构建数据产品，并从中提炼洞察。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2023/06/16/yun.png) Yun Zhou **是 AWS 的应用科学家，他致力于研究与开发，以确保 AWS 客户取得成功。他运用统计建模和机器学习技术，为多个行业打造前沿解决方案。他的兴趣包括生成式模型和序列数据建模。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/04/25/Meghana.png) Meghana Ashok** 是生成式 AI 创新中心的机器学习工程师。她与客户紧密协作，指导他们针对自己的生成式 AI 需求构建安全、成本高效且有韧性的解决方案与基础设施。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2021/05/07/Karan-Sindwani.jpg) Karan Sindwani** 是 AWS 的应用科学家，他与不同垂直行业的 AWS 客户合作，加速他们使用生成式 AI 和 AWS 云服务来解决业务挑战。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2021/04/22/Vidya-Sagar-Ravipati.jpg) Vidya Sagar Ravipati** 是生成式 AI 创新中心的科学经理，他凭借在大规模分布式系统方面的丰富经验和对机器学习的热忱，帮助不同垂直行业的 AWS 客户加速采用 AI 与云。
