---
vendor: aws_bedrock
title: 降低人工智能生成成本：规则代码、判断模型
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/cut-generative-ai-costs-code-for-rules-models-for-judgment
date: 2026-11-17
lang: zh
captured: 2026-11-18
extractor: readability-v1
translator: mt
status: translated
body_sha: 950d453d8cc0
---

## [人工智能](https://aws.amazon.com/blogs/machine-learning/)

# 降低人工智能生成成本：规则代码、判断模型

生成式人工智能系统中最大的成本杠杆是你是否调用模型。我们经常看到团队通过大型语言模型 (LLM) 路由每项任务，包括输入验证、格式化和路由。每个调用单独来看都很便宜，但在生产规模上，这些小成本成为架构中最大的项目之一。只要确定性规则可以完成工作，跳过模型就可以节省资金、减少延迟并消除非确定性来源。在这篇文章中，您将了解如何确定工作流中的每个步骤是否都需要模型。然后，您可以将每个选项映射到 AWS：确定性代码、受限决策调用或 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 上的适当大小的模型。

## 为什么不需要的模型调用会增加

该模式通常从原型开始。模型调用适用于一个步骤，因此它成为下一步的默认调用。这些步骤包括验证输入、重新格式化请求正文以及选择路线。在原型数量上，没有人注意到成本。

在生产量中，不需要的模型调用会在三个方面给您带来成本：

- 支出随着请求数量的增加而增长，即使对于低价值的步骤也是如此。
- 延迟叠加，因为链中的每个模型调用都会增加数百毫秒。
- 输出可能会有所不同，因为相同的输入可能会返回不同的答案。这使得测试变得更加困难，审核也变得更加缓慢。

每次新型号的推出都会重新引发关于使用哪种型号的争论。之前的问题，即该步骤是否需要模型，没有被问到。

成本指导，包括 [AWS Well-Architected Generative AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genperf02-bp03.html)，通常从模型选择开始。这篇文章提前一步开始​​：该步骤是否需要模型？

## 如何判断一个步骤是否需要模型

图 1 以流程图的形式显示了整个决策，其中包含三个标记通道：作为代码运行、问题和在模型上运行。按顺序完成每个工作流程步骤中的三个问题，并停在满足该步骤要求的第一个选项上：

- 规则是否可以检查成功，例如格式、模式、关键字或范围？如果规则仅解决步骤的一部分，则快速路径首先运行该规则。
- 模型是否可以编写一次规则，例如正则表达式或 JSON 模式？
- 该步骤是否从固定列表中选择一个答案，例如路线、类别，或者是或否？

如果这三个问题的答案都是“否”，则该步骤是开放式的，并且在适当大小的模型上运行。

![将工作流程步骤分类为代码、受限决策调用或大小合适的 Amazon Bedrock 模型的流程图](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/17/ML-22259-1.png)

图 1：确定工作流程步骤是否需要模型以及需要哪个模型

考虑聘请客户支持助理。下表显示了其五个步骤如何通过图表。

| **#** | **步骤** | **图表路径** | **它在哪里运行** |
| --- | --- | --- | --- |
| 1 |检查订单号的格式 |规则可以检查是否成功。 | [Amazon API Gateway](https://aws.amazon.com/api-gateway/) REST API 请求验证或 [AWS Lambda](https://aws.amazon.com/lambda/) 函数 |
| 2 |按意图路由消息 |规则解决了其中的一部分。快速路径上的关键字匹配会解析“退款”等消息，剩余部分转到第三个问题。 |使用 JSONata 的 [AWS Step Functions](https://aws.amazon.com/step-functions/) 选择状态。残差进入约束决策调用。 |
| 3 |从运营商电子邮件中提取跟踪号码 |模型可以编写一次规则。它起草一个正则表达式，然后您检查并提交它。 |代码，作为 AWS Lambda 中的承诺模式 |
| 4 |选择四个支持队列之一获取票证 |答案来自一个固定的列表。 |受限决策调用。不确定的答案升级为合适尺寸的模型。 |
| 5 |起草给客户的回复 |该任务是开放式的。 |尺寸合适的模型，满足要求的最小的 Amazon Bedrock 模型 |

当任务是开放式的、不明确的或生成性的时，您可以使用模型：总结文档、起草回复、从散文中提取含义。当任务具有可检查规则时使用确定性代码：电子邮件格式、模式、确切的关键字、数字范围。下表显示了当您向模型发送规则型任务时您要付出的代价。

| **财产** | **确定性代码** | **模特来电** |
| --- | --- | --- |
|每次调用成本|通常要低几个数量级 |每个代币，在规模上并不平凡 |
|延迟|单位数毫秒或更短 |数百毫秒|
|明确规则的正确性|完全符合所写规则 |高，但错误率非零 |
|可审计性|该规则位于源代码管理中 |向审计师解释更困难 |
|随着时间的推移行为 |稳定，直到你改变它 |当您迁移到新模型版本或某个版本停用时发生变化 |

模型还可以产生幻觉并对同一输入返回不同的答案。温度为 0 会降低不同答案的可能性，但不能保证相同的输出。 [Amazon Bedrock 模型评估](https://aws.amazon.com/bedrock/evaluations/) 和 [Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/) 可帮助您衡量和控制这些风险。规则没有任何问题，这是受监管的工作负载青睐规则的原因之一。有用的测试：如果您可以将验收测试编写为规则，则通常可以将步骤编写为规则。有关更多信息，请参阅 AWS 规范指南中的[编排模型：从基于规则到 AI 原生](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-serverless/orchestration-models.html)。

## 决定，不生成

大多数路由和分类步骤位于规则和开放式生成之间。规则无法决定所有情况，但这些步骤也不需要生成文本。他们需要从您预先定义的固定选项列表中找到一个答案，例如上例中的支持队列。使用一个组件，将其输出限制为允许的答案，并为您提供何时升级的信号。自信的答案继续出现，不确定的答案不断升级。 AWS Well-Architected Agentic AI Lens 描述了这种[分层、基于置信度的升级](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentcost02-bp01.html)。在 AWS 上，您可以通过四种方式构建它：

- **具有结构化输出的小型 Amazon Bedrock 模型 –** 答案仅限于 `enum` 选项，以及触发升级的“不确定”选项。这是模型自己的判断，而不是校准分数，因此在使用它来决定升级之前，请先对照标记数据进行检查。
- **嵌入相似性 –** 使用 Amazon Bedrock 嵌入模型嵌入输入并选择最近的标记示例。使用相似度分数作为升级信号，并在标记数据上设置其阈值。
- **[Strands Decider](https://github.com/strands-labs/strands-decider)，Apache License 2.0 下的一个实验性开源决策模型 –** 它根据评分标准从选项或分数中进行选择，并返回每个答案的校准置信度。其 README 报告称，在短分类任务中，置信度为 0.9 或更高的答案在大约 95% 的情况下是正确的。由于该模型是实验性的，因此在生产中使用之前请先根据自己的数据验证该结果。您可以自行托管它，例如在 [Amazon SageMaker AI](https://aws.amazon.com/sagemaker/ai/) 终端节点上，按照其存储库中的[部署指南](https://github.com/strands-labs/strands-decider/tree/main/deploy) 进行操作。
- **Amazon SageMaker AI 上训练有素的分类器 –** 一旦您标记了训练数据，它就会以低延迟和低成本返回类别概率。

以下 JSON 模式将结构化输出答案限制为四个队列加上“不确定”。 Amazon Bedrock 要求架构中的每个对象将 `additionalProperties` 设置为 `false`。
```
{
  "type": "object",
  "properties": {
    "queue": {
      "type": "string",
      "enum": ["billing", "technical", "account", "other", "unsure"]
    }
  },
  "required": ["queue"],
  "additionalProperties": false
}
```
无论您选择哪个选项，请根据您自己的标记数据检查其升级信号，并在那里设置任何阈值。将您的授权决定（例如退款限额）保留在规则中。

## 确定性快速路径模式

许多成本模式侧重于模型之间的路由。快速路径提前一级：首先运行确定性检查，然后仅将规则无法解决的内容发送到模型。意图路由就是一个例子。许多消息都带有明确的信号，例如“退款”或“重置我的密码”，关键字匹配可以在个位数毫秒或更短的时间内解析这些信号。如果规则解决了 95% 的请求，则在模型选择带来的任何节省之前，只有二十分之一的请求会到达模型。 （说明性算术，不是基准。）

在 AWS 上，您可以使用现有的构建块来构建它：

- AWS Step Functions Choice 在工作流调用任何模型之前声明分支。
- AWS Lambda 托管需要的不仅仅是选择状态的规则，例如验证和架构检查。
- Amazon API Gateway (REST API) 请求验证在任何计算运行之前拒绝格式错误的输入。
- 受限决策调用或 Amazon Bedrock 模型仅处理残差。

下面的Choice状态是关键字快速路径。它使用 JSONata 将退款和密码重置消息直接发送到代码，并将其他所有内容发送到受限决策调用。
```
"KeywordFastPath": {
  "Type": "Choice",
  "QueryLanguage": "JSONata",
  "Choices": [
    {
      "Condition": "{% $contains($states.input.message, /refund/i) %}",
      "Next": "RefundFlow"
    },
    {
      "Condition": "{% $contains($states.input.message, /reset (my )?password/i) %}",
      "Next": "PasswordResetFlow"
    }
  ],
  "Default": "ConstrainedDecisionCall"
}
```
您还可以让模型编写一次规则，而不是每次都运行它。让它起草正则表达式或 JSON 模式，对其进行审查并提交。在运行时，规则以规则速度和成本运行。检查模型编写的正则表达式，并根据已知的好输入和坏输入对其进行测试。避免使用 `(a+)+` 等嵌套量词，这可能会使某些输入的匹配速度非常慢（正则表达式拒绝服务或 ReDoS）。

当您生成时，Amazon Bedrock 结构化输出会限制对您定义的 JSON 架构的响应。然后，响应与架构相匹配，因此您的代码可以在没有自定义解析逻辑的情况下解析它（检查内容的正确性）。在代码中保留范围检查，例如数字边界和长度限制。有关支持的模型和架​​构功能，请参阅[从模型获取经过验证的 JSON 结果](https://docs.aws.amazon.com/bedrock/latest/userguide/structured-output.html)。

如果您的规则存在于配置中，则仅允许已知的原语，例如正则表达式、架构检查、关键字列表和范围检查。切勿从配置文件运行任意代码。

## 当您确实需要模型时，调整它的大小

选择符合您的地板质量的最便宜、最快的型号。这通常不是最新或最大的型号。生成式 AI Lens 在[正确调整模型选择](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost01-bp01.html) 的最佳实践中涵盖了这一点。 [Amazon Bedrock 的有效成本优化策略](https://aws.amazon.com/blogs/machine-learning/effective-cost-optimization-strategies-for-amazon-bedrock/) 对此进行了深入介绍。在比较模型之前定义要求：

- **质量下限：** 可接受的最低输出质量，在黄金评估集上测量（带有已知正确答案的任务标记示例）。
- **成本上限：** 您为每个请求或每个成功结果支付的最高费用。
- **延迟目标：** 体验可以容忍的 p95 或 p99 响应时间。
- **合规性限制：** 可能排除候选者的数据驻留等要求。

Amazon Bedrock 在一个 API 背后提供多种模型系列和大小，因此您可以在不更改集成的情况下调整每项任务的大小。 [Amazon Bedrock 智能提示路由](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html) 将每个请求路由到支持的模型系列中的合适模型。 [Amazon Bedrock 模型蒸馏](https://docs.aws.amazon.com/bedrock/latest/userguide/model-distillation.html) 将知识从较大的模型转移到适合您的用例的较小、更便宜的模型。模型提供商在广泛的基准上评估新的前沿模型，但您的工作量是具有单一质量底线的一项任务。较大的模型可能会增加成本和延迟，但不会改善该任务。在切换之前，请根据您的要求评估每次启动，例如黄金评估集的质量和延迟目标。

## 将模型选择视为经过测试的配置

生成式 AI 镜头建议根据地面实况数据测试候选模型，并提供快速更新模型的方法。更进一步，将决策视为经过测试的配置：

- 为每个任务保留一个黄金评估集，并带有标记的基本事实，并以持续集成的方式运行它。
- 满足您的要求。将低于质量底线的较便宜的模型视为回归。
- 将模型放在配置标志后面，以便您可以反转交换。
- 使用正确的预言机进行验证。根据基本事实检查规则。为开放式输出保留模型作为法官的评估。
- 注意漂移。通过影子模式下的模型对一些规则解析的请求进行采样，并在它们不同意时重新分类步骤。

## 付诸实践

将模型能力用在需要判断的地方，而不是其他地方。您可以通过四个步骤到达那里：

- **仪器 –** 将每个调用标记为确定性代码、约束决策调用或模型调用。跟踪每个成功结果的成本。
- **将规则移至代码 –** 在 AWS Lambda 或 AWS Step Functions 上运行可检查规则的步骤。这通常是最大且最安全的胜利。
- **添加受限决策调用 –** 通过在不确定时升级的调用来路由固定选择步骤。
- **切换模型之前进行测试 –** 在每个新模型成为默认模型之前，通过您的黄金评估集运行它。

＃＃ 结论

在这篇文章中，您学习了如何确定工作流程步骤是否需要模型。规则属于确定性代码，固定选择属于受限决策调用。开放式工作采用尺寸合适的 Amazon Bedrock 模型。旨在以您的优质地板允许的最低成本和最低延迟来满足每项要求。在询问哪个步骤之前先询问某个步骤是否需要模型。

有关更多信息，请参阅 AWS 人工智能博客上的以下帖子：

- [将决策模型与 Amazon Bedrock AgentCore 评估结合使用](https://aws.amazon.com/blogs/machine-learning/use-decision-models-with-amazon-bedrock-agentcore-evaluations/)。
- [使用 Amazon Bedrock 智能提示路由以获得成本和延迟优势](https://aws.amazon.com/blogs/machine-learning/use-amazon-bedrock-intelligent-prompt-routing-for-cost-and-latency-benefits/)。
- [Amazon Bedrock 上的结构化输出：符合架构的 AI 响应](https://aws.amazon.com/blogs/machine-learning/structured-outputs-on-amazon-bedrock-schema-compliant-ai-responses/)。
- [修复评估偏差以在 Amazon Bedrock 上解锁更好的模型](https://aws.amazon.com/blogs/machine-learning/fix-evaluation-bias-to-unlock-better-models-on-amazon-bedrock/)。

要尝试约束决策调用，请打开 [Amazon Bedrock 控制台](https://console.aws.amazon.com/bedrock/)，或从其 [GitHub 存储库](https://github.com/strands-labs/strands-decider) 部署 Strands Decider。

从一个大容量工作流程开始，衡量其中有多少不需要模型。

## 关于作者
