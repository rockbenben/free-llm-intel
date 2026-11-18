---
vendor: aws_bedrock
title: 降低人工智能生成成本：规则代码、判断模型
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/cut-generative-ai-costs-code-for-rules-models-for-judgment
date: 2026-11-17
lang: zh
captured: 2026-11-18
extractor: readability-v1
translator: agent
status: translated
body_sha: 32beb7b6c659
---

## [Artificial Intelligence](https://aws.amazon.com/blogs/machine-learning/)

# 降低人工智能生成成本：规则代码、判断模型

生成式 AI 系统里最大的成本杠杆，是你到底要不要调用模型。我们经常看到团队把每一项任务都交给大型语言模型（LLM），包括输入校验、格式化和路由。单次调用看起来便宜，但在生产规模下，这些零散的小成本会变成架构中最大的一笔开销。只要确定性规则能完成工作，跳过模型就能省钱、降低延迟，并去掉一个非确定性的来源。在本文中，你将学会如何判断工作流中的每个步骤到底需不需要模型。然后，你可以把每种选项对应到 AWS 上：确定性代码、受约束的决策调用，或 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 上规模合适的模型。

## 为什么不需要的模型调用会累积成本

这种模式通常从原型阶段开始。一次模型调用在某个步骤上奏效了，于是它就成了下一个步骤的默认做法。这些步骤包括校验输入、重新格式化请求体，以及选择路由。在原型规模下，没人会注意到成本。

到了生产规模，不需要的模型调用会从三个方面让你付出代价：

- 开销随请求数增长，即便是低价值步骤也一样。
- 延迟会叠加，因为链路上的每一次模型调用都会增加数百毫秒。
- 输出可能不稳定，因为同样的输入可能返回不同的答案。这让测试更难、审计更慢。

而每有新模型发布，关于「该用哪个模型」的争论又会被重新点燃。更早的那个问题——这个步骤到底需不需要模型——却始终没人问。

包括 [AWS Well-Architected Generative AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genperf02-bp03.html) 在内的成本指南，往往从选择模型讲起。本文则再往前推一步：这个步骤到底需不需要模型？

## 如何判断一个步骤是否需要模型

图 1 把整个决策过程画成一张流程图，分为三条带标签的泳道：以代码运行、问题、以模型运行。让工作流的每个步骤依次经过三个问题，并在第一个满足该步骤要求的选项处停下：

- 规则能否检查是否成功，例如格式、schema、关键字或范围？如果规则只能解决该步骤的一部分，就先走一条快路径来运行规则。
- 模型能否一次性写出这条规则，例如一个正则表达式或一个 JSON schema？
- 该步骤是否要从固定列表里选出一个答案，例如一条路由、一个类别，或是/否？

如果三个问题的答案都是否，那么这个步骤就是开放式的，交由规模合适的模型来运行。

![将工作流步骤归入代码、受约束的决策调用或规模合适的 Amazon Bedrock 模型的流程图](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/17/ML-22259-1.png)

图 1：判断一个工作流步骤是否需要模型，以及需要哪一个模型

以客户支持助手为例。下表展示了它的五个步骤如何走完这张流程图。

| **#** | **步骤** | **在流程图中的路径** | **在哪里运行** |
| --- | --- | --- | --- |
| 1 | 检查订单号格式 | 规则可以检查是否成功。 | [Amazon API Gateway](https://aws.amazon.com/api-gateway/) REST API 请求校验，或 [AWS Lambda](https://aws.amazon.com/lambda/) 函数 |
| 2 | 按意图路由消息 | 规则能解决其中一部分。在快路径上做关键字匹配即可处理 “refund” 这类消息，剩余部分进入第三个问题。 | 使用 JSONata 的 [AWS Step Functions](https://aws.amazon.com/step-functions/) Choice 状态。剩余部分交给受约束的决策调用。 |
| 3 | 从承运商邮件中提取跟踪号 | 模型可以一次性写出规则。它起草一个正则表达式，由你审核并提交。 | 代码，作为 AWS Lambda 中已提交的模式 |
| 4 | 为工单挑选四个支持队列之一 | 答案来自固定列表。 | 一次受约束的决策调用。不确定的答案升级到规模合适的模型。 |
| 5 | 起草给客户的回复 | 任务属于开放式。 | 规模合适的模型，即满足要求的最小 Amazon Bedrock 模型 |

当任务开放式、有歧义或属于生成式时，可以使用模型：总结文档、起草回复、从散文里提取含义。当任务存在可检查的规则时，就使用确定性代码：邮箱格式、schema、精确关键字、数值范围。下表展示了把规则型的任务交给模型会牺牲什么。

| **属性** | **确定性代码** | **模型调用** |
| --- | --- | --- |
| 单次调用成本 | 通常低几个数量级 | 按 token 计费，规模化后并不便宜 |
| 延迟 | 个位数毫秒或更低 | 数百毫秒 |
| 对明确规则的准确性 | 按所写规则精确执行 | 高，但存在非零错误率 |
| 可审计性 | 规则存放在源码管理中 | 更难向审计人员解释 |
| 长期行为 | 在你修改之前保持稳定 | 会随切换到新模型版本或版本退役而变化 |

模型还可能产生幻觉，对同样的输入返回不同的答案。temperature 设为 0 可以降低答案多样的可能性，但并不能保证输出完全一致。[Amazon Bedrock model evaluation](https://aws.amazon.com/bedrock/evaluations/) 和 [Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/) 可以帮助你度量和遏制这些风险。规则则没有这两个问题，这也是受监管的工作负载偏好规则的原因之一。一个有用的测试是：如果你能把验收测试写成一条规则，通常就能把这个步骤写成规则。更多信息请参阅 AWS Prescriptive Guidance 中的 [Orchestration models: From rule-based to AI-native](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-serverless/orchestration-models.html)。

## 做决策，而非生成

大多数路由与分类步骤介于规则和开放式生成之间。规则无法决定所有情况，但这些步骤也不需要生成的文本。它们需要的是从你预先定义的固定选项列表中选出一个答案，就像前面示例里的支持队列。使用这样一个组件：把输出限制在允许的答案内，并给出何时需要升级的信号。有把握的答案继续往下走，不确定的则升级处理。AWS Well-Architected Agentic AI Lens 把这种做法称为[分层、基于置信度的升级](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentcost02-bp01.html)。在 AWS 上，有四种构建方式：

- **带结构化输出的小型 Amazon Bedrock 模型 –** 答案被限制为选项的 `enum`，外加一个会触发升级的 ‘unsure’ 选项。这是模型自己的判断，而不是校准过的分数，所以在用它决定是否升级之前，要先拿标注数据做校验。
- **Embedding 相似度 –** 用 Amazon Bedrock 的 embedding 模型把输入向量化，选出最接近的已标注示例。把相似度分数用作升级信号，并在标注数据上设定阈值。
- **[Strands Decider](https://github.com/strands-labs/strands-decider)，一个以 Apache License 2.0 发布的实验性开源决策模型 –** 它从选项中选择，或按评分标准（rubric）打分，并为每个答案返回一个校准过的置信度。其 README 报告称，在短分类任务上，置信度为 0.9 及以上的答案约有 95% 是正确的。由于该模型仍属实验性质，在生产环境使用前请先在自己的数据上验证这一结果。你需要自行托管它，例如部署到 [Amazon SageMaker AI](https://aws.amazon.com/sagemaker/ai/) endpoint 上，按照其仓库中的[部署指南](https://github.com/strands-labs/strands-decider/tree/main/deploy)操作。
- **Amazon SageMaker AI 上训练好的分类器 –** 一旦有了标注好的训练数据，它就能以低延迟、低成本返回类别概率。

下面的 JSON schema 把结构化输出的答案限制为四个队列加 ‘unsure’。Amazon Bedrock 要求 schema 中的每个对象都把 `additionalProperties` 设为 `false`。

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

无论选择哪种方案，都要用自己的标注数据检验它的升级信号，并在标注数据上设定阈值。授权类的决策，例如退款上限，要留在规则里。

## 确定性快路径模式

许多成本模式关注的是在模型之间做路由。快路径则再往前一层：先运行确定性检查，只把规则无法解决的部分交给模型。意图路由就是一个例子。很多消息带有明确的信号，例如 “refund” 或 “reset my password”，用关键字匹配就能在个位数毫秒或更短时间内处理掉。如果规则能解决 95% 的请求，那么每 20 个请求里只有 1 个会到达模型，这还没有算上选择模型带来的节省。（仅为说明性算术，不是 benchmark。）

在 AWS 上，你可以用现成的积木拼出这套方案：

- AWS Step Functions 的 Choice 状态在工作流调用任何模型之前就完成分支。
- AWS Lambda 承载超出 Choice 状态能力的规则，例如校验和 schema 检查。
- Amazon API Gateway（REST API）的请求校验会在任何计算运行之前拒绝格式错误的输入。
- 受约束的决策调用或 Amazon Bedrock 模型只处理剩余部分。

下面的 Choice 状态就是一个关键字快路径。它用 JSONata 把退款和密码重置类消息直接送到代码，其余全部送到受约束的决策调用。

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

你也可以让模型只写一次规则，而不是每次都运行模型。让它起草一个正则表达式或 JSON schema，由你审核并提交。运行时，规则以规则的速度和成本执行。要审查模型写出的正则表达式，并用已知的正常输入和异常输入测试它。避免 `(a+)+` 这类嵌套量词，它们会让某些输入下的匹配变得极慢（正则表达式拒绝服务，即 ReDoS）。

当你确实需要生成时，Amazon Bedrock 的结构化输出会把响应约束到你定义的 JSON schema。这样响应就符合 schema，你的代码无需自定义解析逻辑就能解析它（但仍要检查内容是否正确）。范围检查，例如数值边界和长度限制，要留在代码里。受支持的模型与 schema 特性请参阅 [Get validated JSON results from models](https://docs.aws.amazon.com/bedrock/latest/userguide/structured-output.html)。

如果你的规则存放在配置里，只允许已知的原语，例如正则表达式、schema 检查、关键字列表和范围检查。绝不要执行来自配置文件的任意代码。

## 确实需要模型时，选对规模

选择满足你质量下限的最便宜、最快的模型。它往往不是最新或最大的模型。Generative AI Lens 在[为模型选择确定合适规模](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/gencost01-bp01.html)的最佳实践中涵盖了这一点。[Effective cost optimization strategies for Amazon Bedrock](https://aws.amazon.com/blogs/machine-learning/effective-cost-optimization-strategies-for-amazon-bedrock/) 对此有深入讨论。在比较模型之前，先定义需求：

- **质量下限：** 可接受的最低输出质量，在 golden 评估集（带已知正确答案的任务标注样本）上度量。
- **成本上限：** 每个请求或每个成功结果最多愿意付多少。
- **延迟目标：** 体验可以容忍的 p95 或 p99 响应时间。
- **合规约束：** 例如数据驻留之类的要求，可能直接排除掉一些候选。

Amazon Bedrock 在一个 API 背后提供众多模型家族与规模，因此你可以为每项任务选对规模，而无需改动集成方式。[Amazon Bedrock Intelligent Prompt Routing](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html) 会在受支持的模型家族内把每个请求路由到合适的模型。[Amazon Bedrock Model Distillation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-distillation.html) 会把知识从更大的模型迁移到更小、更便宜的模型，以适配你的用例。模型提供商会用宽泛的 benchmark 评估新的前沿模型，但你的工作负载只是带着一个质量下限的单一任务。更大的模型可能增加成本与延迟，却对这个任务毫无改善。在切换之前，请按照你的需求评估每一次发布，例如在 golden 评估集上的质量和延迟目标。

## 把模型选择当作经过测试的配置

Generative AI Lens 建议用你的 ground truth 数据测试候选模型，并保留一种快速更新模型的方式。可以再进一步，把这个决策当作一份经过测试的配置来对待：

- 为每项任务维护一个带标注 ground truth 的 golden 评估集，并在持续集成中运行它。
- 以你的需求作为门禁。把跌破质量下限的更便宜模型视为回归。
- 把模型放在配置开关后面，以便随时回滚切换。
- 用合适的判据验证。用 ground truth 检验规则。model-as-judge 评估只留给开放式输出。
- 关注漂移。用影子模式让模型抽样处理一部分由规则解决的请求，当两者不一致时，就重新判定该步骤的归属。

## 付诸实践

把模型算力花在需要判断的地方，其余地方一律不花。你可以通过四个步骤实现：

- **埋点 –** 给每次调用打标签：确定性代码、受约束的决策调用，还是模型调用。跟踪每个成功结果的成本。
- **把规则搬到代码里 –** 在 AWS Lambda 或 AWS Step Functions 上运行可用规则检查的步骤。这通常是收益最大、也最稳妥的一项。
- **加入受约束的决策调用 –** 把固定选项的步骤交给一种调用，它在不确定时升级。
- **切换模型前先测试 –** 每个新模型在成为默认之前，都要跑一遍你的 golden 评估集。

## 结论

在本文中，你学会了如何判断一个工作流步骤到底需不需要模型。规则应该放进确定性代码，固定选项应该交给受约束的决策调用，开放式的工作则交给规模合适的 Amazon Bedrock 模型。目标是在质量下限允许的前提下，用最低的成本和延迟满足每一项需求。先问这个步骤需不需要模型，再问该用哪个模型。

更多信息，请参阅 AWS Artificial Intelligence Blog 上的这些文章：

- [在 Amazon Bedrock AgentCore Evaluations 中使用决策模型](https://aws.amazon.com/blogs/machine-learning/use-decision-models-with-amazon-bedrock-agentcore-evaluations/)。
- [使用 Amazon Bedrock Intelligent Prompt Routing 获得成本与延迟收益](https://aws.amazon.com/blogs/machine-learning/use-amazon-bedrock-intelligent-prompt-routing-for-cost-and-latency-benefits/)。
- [Amazon Bedrock 上的结构化输出：符合 schema 的 AI 响应](https://aws.amazon.com/blogs/machine-learning/structured-outputs-on-amazon-bedrock-schema-compliant-ai-responses/)。
- [修正评估偏差，在 Amazon Bedrock 上解锁更好的模型](https://aws.amazon.com/blogs/machine-learning/fix-evaluation-bias-to-unlock-better-models-on-amazon-bedrock/)。

要试用受约束的决策调用，请打开 [Amazon Bedrock 控制台](https://console.aws.amazon.com/bedrock/)，或从其 [GitHub 仓库](https://github.com/strands-labs/strands-decider)部署 Strands Decider。

从一个高流量的工作流开始，测量其中有多少部分其实从来不需要模型。

## 关于作者
