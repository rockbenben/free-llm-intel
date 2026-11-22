---
vendor: aws_bedrock
title: Build a read-through semantic cache with Amazon OpenSearch Serverless and Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-a-read-through-semantic-cache-with-amazon-opensearch-serverless-and-amazon-bedrock
date: 2024-11-26
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: f5b30bd8808d
---

# 使用 Amazon OpenSearch Serverless 与 Amazon Bedrock 构建读穿透式语义缓存

在[生成式 AI](https://aws.amazon.com/generative-ai/) 领域，延迟和成本构成了重大挑战。常用的大型语言模型（LLM）往往以自回归方式逐个 token 顺序处理文本、预测下一个 token。这种方式可能引入延迟，导致用户体验不够理想。此外，对 AI 驱动应用日益增长的需求导致对这些 LLM 的调用量巨大，可能超出预算约束，给组织带来财务压力。

本文提出一种优化基于 LLM 应用的策略。鉴于对高效且成本合理的 AI 解决方案的需求日益增长，我们给出一个利用重复数据模式的无服务器读穿透式缓存蓝图。借助该缓存，开发者可以有效地保存并访问相似的 prompt，从而提升系统的效率和响应时间。所提出的缓存方案使用 [Amazon OpenSearch Serverless](https://aws.amazon.com/opensearch-service/features/serverless/) 和 [Amazon Bedrock](https://aws.amazon.com/bedrock/)——后者是一项完全托管服务，通过单一 API 提供来自 AI21 Labs、Anthropic、Cohere、Meta、Stability AI 和 Amazon 等领先 AI 公司的高性能基础模型（FM）供你选择，并附带一整套构建安全、隐私和负责任 AI 的生成式 AI 应用所需的能力。

## 解决方案概览

本方案中的缓存充当缓冲区，在 prompt——以自然语言表达的发给 LLM 的请求——到达主模型之前将其拦截。语义缓存充当存储此前遇到的相似 prompt 的记忆库。它专为高效而设计，能够迅速把用户的 prompt 与最接近的语义对应项匹配起来。然而在实际的缓存系统中，细化相似度的定义至关重要。这种细化是必要的，以便在两个关键因素之间取得平衡：提高缓存命中率、减少缓存碰撞。缓存命中发生在所请求的 prompt 在缓存中被找到时，意味着系统无需将其发送给 LLM 做新的生成。相反，当多个 prompt 因其语义特征的相似性被映射到同一缓存位置时，就发生了缓存碰撞。为了更好地理解这些概念，让我们看几个例子。

设想一个由 LLM 驱动的礼宾式 AI 助手，专门为一家旅行公司设计。它擅长从过往互动的池子中提取个性化响应，确保每条回复都相关且贴合旅行者的需求。在这种情况下，我们可能会优先追求高召回率，也就是说宁愿有更多缓存的响应，即使这偶尔会导致 prompt 重叠。

现在考虑另一个场景：一个用于协助该旅行公司后台坐席人员的 AI 助手，使用 LLM 将自然语言查询转换为 SQL 命令。这使得坐席人员能够从发票和其他财务数据生成报表，并应用日期和总金额等筛选条件来简化报表创建。这里的精确率至关重要。我们需要把每个用户请求都准确映射到对应的 SQL 命令，不容有误。在这种情况下，我们会选择更严格的相似度阈值，确保把缓存碰撞控制在绝对最低水平。

从本质上讲，读穿透式语义缓存不只是中间人，而是根据不同应用的具体需求优化系统性能的战略性工具。无论是为聊天机器人优先保证召回率，还是为查询解析器优先保证精确率，可调节的相似度特性都能确保缓存以最高效率运行，从而提升整体用户体验。

语义缓存系统的核心是一个存储文本查询数值向量嵌入的数据库。在存储之前，每个自然语言查询都会被转换为对应的嵌入向量。借助 Amazon Bedrock，你可以灵活地从多种托管嵌入模型中选择，包括 Amazon 自有的 Amazon Titan 嵌入模型，或 Cohere 等第三方替代方案。这些嵌入模型专门设计用于把相似的自然语言查询映射到欧几里得距离相近的向量嵌入，从而体现语义相似性。借助 OpenSearch Serverless，你可以建立适合搭建稳健缓存系统的向量数据库。

通过利用这些技术，开发者可以构建一个语义缓存，高效地存储和检索语义相关的查询，提升系统的性能与响应速度。在本文中，我们演示如何使用多种 AWS 技术建立无服务器语义缓存系统。这一设置支持快速查找以取回可用响应，绕开耗时的 LLM 调用。结果不仅是更快的响应时间，还有明显的价格下降。

本文介绍的方案可通过 [AWS CloudFormation](https://aws.amazon.com/cloudformation/) 模板部署。它使用以下 AWS 服务：

- 一个 Amazon Bedrock 托管的文本生成模型，例如 [Anthropic 的 Claude](https://aws.amazon.com/bedrock/claude/)
- 一个 Amazon Bedrock 托管的文本嵌入模型，例如 [Amazon Titan Text Emebeddings Model V2](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html)
- 一个 OpenSearch Serverless 向量搜索集合
- 作为缓存处理器的 [AWS Lambda](https://aws.amazon.com/lambda/)

以下架构展示了一种无服务器读穿透式语义缓存模式，你可以将其集成到基于 LLM 的解决方案中。

![语义缓存示意图](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/18/semantic-cache3-1.png)

在该架构中，缓存未命中和命中的示例分别用红色和绿色表示。在这个特定场景中，客户端发送一个查询，该查询随后与此前见过的查询进行语义比较。由于在给定相似度阈值下没有缓存命中，作为缓存管理器的 Lambda 函数会提示 LLM 进行新的生成。新的生成结果随后被发送给客户端，并用于更新向量数据库。在缓存命中的情况下（绿色路径），此前生成的语义相似查询会立即发送给客户端。

对于这个短查询，下表汇总了以“Who was the first US president”进行查询、在 Anthropic Claude V2 上测试得到的响应延迟结果。

| 测试查询 | 未命中缓存 | 命中缓存 |
| --- | --- | --- |
| 美国第一任总统是谁？ | 2 秒 | 0.5 秒以内 |

## 先决条件

Amazon Bedrock 用户需要先为 FM [申请访问权限](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)，模型才可用。这是一次性操作，耗时不到一分钟。对本方案而言，你需要一个嵌入模型，例如 Amazon Bedrock 上的 Cohere Embed-English 或 Amazon Titan Text Embedding。文本生成则可以从 Anthropic 的 Claude 模型中选择。文本生成模型的完整列表请参阅 Amazon Bedrock。

![Bedrock 模型访问权限](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/25/ModelAccess-2.png)

## 部署解决方案

本方案需要设置一个 Lambda 层，其中包含与服务（如 OpenSearch Serverless 和 Amazon Bedrock）交互所需的依赖。已有一个预构建的层被编译并添加到公有 [Amazon Simple Storage Service](https://aws.amazon.com/s3)（Amazon S3）前缀中，可在所提供的 CloudFormation 模板中使用。你也可以选择用其他库构建自己的层；更多信息请参阅以下 [GitHub 仓库](https://github.com/kamrazi/aws-opensearch-bedrock-layer/tree/main)。

你可以使用所提供的模板，连同所需的角色一起部署本方案：
[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/05/30/ML16442_2_launch.png)](https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/review?templateURL=https://aws-blogs-artifacts-public.s3.amazonaws.com/ML-16295/llm_cache.yaml&stackName=semantic-cache)

本方案使用以下输入参数：

- 嵌入模型
- LLM
- 相似度阈值

部署成功后（大约需要 2 分钟），你就可以获取 Lambda 函数名称并开始试验。你可以在 CloudFormation 堆栈的 **Outputs** 选项卡中找到 Lambda 函数名称，如下图所示。

![堆栈输出](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/18/StackOutputs-3.png)

你可以从 Lambda 控制台或通过 [AWS Command Line Interface](https://aws.amazon.com/cli)（AWS CLI）调用该 Lambda 函数：

```
aws lambda invoke \
--function-name YOUR_LAMBDA_FUNCTION_NAME \
--invocation-type RequestResponse \
--cli-binary-format raw-in-base64-out
--payload '{"prompt": "your question here"}' \
output.txt
```

你的载荷还可以包含以下其他选项来控制缓存和生成：

```
{
"max_tokens_to_sample": int, // Optional. Controls the length of LLM generation in case of a cache miss. Default is 1000.
"reset": bool // Optional. To reset cache
}
```

## 测试解决方案

要使用 Lambda 控制台测试你的缓存，请打开 Functions 页面。导航到你从堆栈输出中获取的函数。按下图所示设置测试事件。

![Lambda 测试事件](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/18/TestEvent-4.png)

运行成功后，结果类似以下截图。

![Lambda 测试事件结果](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/18/TestEventResult.png)

我们再做一次实验，更仔细地观察缓存的工作方式。本次实验使用 Amazon Bedrock 上的 Cohere 嵌入模型，相似度阈值设为 0.75。我们提出以下问题，模型用 Anthropic 的 Claude V2 生成完整响应大约花了 15 秒：

> Prompt：人工智能和区块链技术对全球金融业可能有哪些长期影响？
>         Generation：以下是 AI 和区块链对全球金融业的一些潜在长期影响：
>         常规任务自动化 – AI 和机器学习可以自动化许多常规金融任务，例如贷款处理、欺诈检测、客户入驻等。这可以为金融公司降低运营成本并提升效率。
>         更好的数据分析与洞见 – AI 能比人类更高效地分析海量金融数据。这可以带来更好的洞见、为客户提供个性化建议，以及企业改进风险管理。
>         改进的交易与投资平台 – AI 算法有可能比人类交易员更快、更优地执行交易。它们还可以实现提供自动化投资建议和组合管理的 robo-advisor。
>         增强的安全性与欺诈检测 – 机器学习模型能够检测数据中的模式，以识别潜在的欺诈、洗钱或网络安全威胁。区块链提供去中心化、加密的交易记录，更难被篡改。

当我们尝试这些 prompt 变体时，缓存系统成功返回了此前生成的响应（**0.5 秒以内**）：

> 相似 Prompt 1：AI 和区块链对全球金融板块可能有哪些未来影响？
>         相似 Prompt 2：讨论人工智能和区块链的进步在未来几十年对全球金融格局可能产生的影响。

我们把“*financial sector*”一词替换为“*healthcare sector*”；我们预期不会发生缓存碰撞，而会有新的生成：

> Prompt：能否概述 AI 和区块链对全球医疗健康板块的未来影响？
>         Generation：以下是 AI 可能对医疗健康板块产生的一些潜在长期影响：
>         个性化医疗 – AI 可以分析有关基因、生活方式、病史等海量数据集，提供针对每位患者具体需求与风险的个性化治疗方案。这可以改善治疗效果并减少系统中的浪费。
>         疾病早期检测 – 算法在分析医学影像和数据以识别人体医生更早发现潜在疾病和状况方面越来越擅长。这可以带来更早的治疗和严重疾病的预防。
>         降低成本 – AI 有潜力自动化和精简医疗健康领域的许多流程，从而带来更高效率和更低成本。例如，AI 聊天机器人和虚拟助手可以以远低于人工员工成本的方式提供部分基础服务。

下表汇总了在 Anthropic 的 Claude V2 上测试的未命中缓存与命中缓存时的查询延迟结果。

| 测试查询 | 未命中缓存 | 命中缓存 |
| --- | --- | --- |
| 能否概述 AI 和区块链对全球医疗健康板块的未来影响？ | 15 秒 | 0.5 秒以内 |

除了延迟，你还可以为 LLM 系统节省成本。通常，嵌入模型比生成模型更具成本效率。例如，Amazon Titan Text Embedding V2 每 1,000 个输入 token 收费 $0.00002，而 Anthropic 的 Claude V2 每 1,000 个输入 token 收费 $0.008，每 1,000 个输出 token 收费 $0.024。即便考虑 OpenSearch Service 带来的额外成本，视缓存数据的规模而定，该缓存系统在许多用例中仍具备成本效率。

## 清理

在完成对 Lambda 函数的试验后，你可以快速删除构建此语义缓存所用的所有资源，包括 OpenSearch Serverless 集合和 Lambda 函数。为此，请在 AWS CloudFormation 控制台上找到你的 CloudFormation 堆栈并将其删除。

请确保堆栈状态从 **Delete in progress** 变为 **Deleted**。

## 结论

在本文中，我们带你走过了搭建无服务器读穿透式语义缓存的过程。通过实施这里概述的模式，你可以改善基于 LLM 应用的延迟，同时优化成本并丰富用户体验。我们的方案允许试验规模各异的嵌入模型，这些模型都便捷地托管在 Amazon Bedrock 上。此外，它还支持微调相似度阈值，以在缓存命中率与缓存碰撞率之间取得完美平衡。拥抱这一方法，在项目中释放更高的效率与效果。

更多信息请参阅 [Amazon Bedrock 用户指南](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html) 和 [Amazon OpenSearch Serverless 开发者指南](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-overview.html)。

### 作者简介

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/Kamran-photo-scaled-1.jpg)Kamran Razi** 是 Amazon 生成式 AI 创新中心的数据科学家。Kamran 热衷于交付前沿的生成式 AI 方案，帮助客户充分释放 AWS AI/ML 服务的潜力，以解决真实世界的业务挑战。凭借十多年软件开发经验，他专注于构建 AI 驱动方案，包括聊天机器人、文档处理以及检索增强生成（RAG）pipeline。Kamran 拥有女王大学电气工程博士学位。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/09/30/SungminHong-1.jpg)Sungmin Hong** 是 Amazon 生成式 AI 创新中心的高级应用科学家，帮助加快 AWS 客户各类用例的推进。加入 Amazon 之前，Sungmin 是哈佛医学院的博士后研究员。他拥有纽约大学计算机科学博士学位。工作之外，Sungmin 喜欢徒步、阅读和烹饪。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/yash.png)**Yash Shah** 是 AWS 生成式 AI 创新中心的科学经理。他与由应用科学家和机器学习工程师组成的团队，处理从医疗健康、体育、汽车到制造业的一系列机器学习用例。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/image-16-2-249x300-1.png)Anila Joshi** 拥有十多年构建 AI 解决方案的经验。作为 AWS 生成式 AI 创新中心应用科学高级经理，Anila 开创 AI 的创新应用，拓展可能性的边界，并通过帮助客户构思、识别和实施安全的生成式 AI 方案，加快 AWS 服务在客户中的采用。
