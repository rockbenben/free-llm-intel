---
vendor: aws_bedrock
title: Programmatically creating an IDP solution with Amazon Bedrock Data Automation
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/programmatically-creating-an-idp-solution-with-amazon-bedrock-data-automation
date: 2025-12-24
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 0b68fc0ead46
---

# 以编程方式用 Amazon Bedrock Data Automation 构建 IDP 解决方案

智能文档处理（IDP）改变了组织处理非结构化文档数据的方式，使发票、合同与报告中有价值的信息可以被自动提取。今天，我们将探索如何以编程方式构建一个 IDP 解决方案，它使用 [Strands SDK](https://aws.amazon.com/blogs/opensource/introducing-strands-agents-an-open-source-ai-agents-sdk/)、[Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/)、[Amazon Bedrock Knowledge Base](https://aws.amazon.com/bedrock/knowledge-bases/) 与 [Bedrock Data Automation（BDA）](https://aws.amazon.com/bedrock/bda/)。该方案通过一个 Jupyter notebook 提供，用户可以在其中上传多模态业务文档，并使用 BDA 作为解析器提取洞察——检索相关 chunk 并增强发往基础模型（FM）的 prompt。在本用例中，我们的方案从美国教育部发布的 Nation's Report Card 中检索与公立学区相关的上下文。

[Amazon Bedrock Data Automation](https://aws.amazon.com/bedrock/bda/) 既可作为独立功能使用，也可在为[检索增强生成（RAG）](https://aws.amazon.com/what-is/retrieval-augmented-generation/) 工作流搭建知识库时作为解析器使用。BDA 可以从文档、图像、视频与音频等非结构化多模态内容中生成有价值的洞察。借助 BDA，你可以快速且高性价比地构建自动化 IDP 与 RAG 工作流。在构建 RAG 工作流时，你可以使用 [Amazon OpenSearch Service](https://aws.amazon.com/opensearch-service/) 存储必要文档的向量嵌入。本文中，Bedrock AgentCore 通过工具调用 BDA，为该 IDP 方案执行多模态 RAG。

[Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) 是一项完全托管的服务，让你可以构建并配置自主 agent。开发者可以使用流行的框架与一系列模型（包括来自 Amazon Bedrock、Anthropic、Google 与 OpenAI 的模型）构建并部署 agent，而无需管理底层基础设施或编写自定义代码。

[Strands Agents SDK](https://aws.amazon.com/blogs/machine-learning/amazon-strands-agents-sdk-a-technical-deep-dive-into-agent-architectures-and-observability/) 是一套精巧的开源工具包，通过模型驱动的方式革新人工智能（AI）agent 的开发。开发者可以用一段 prompt（定义 agent 行为）与一组工具来创建 Strands Agent。大语言模型（LLM）负责推理，根据上下文与任务自主决定最优动作以及何时使用工具。这一工作流支持复杂系统，最大限度减少通常用于编排多 agent 协作的代码。Strands SDK 用于创建 agent 并定义执行智能文档处理所需的工具。

按照以下前置条件与分步实现，在你自己的 AWS 环境中部署该方案。

## 前置条件

要跟随这些示例用例操作，请设置以下前置条件：

- 具有适当权限的 AWS 凭证
- 可访问 Github
- 本地已安装 Git；操作说明请参阅 [Getting Started – Installing Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

## 架构

该方案使用以下 AWS 服务：

- [Amazon S3](https://aws.amazon.com/s3/) 用于文档存储与上传能力
- Bedrock Knowledge Bases 用于把存储在 S3 中的对象转换为可支持 RAG 的工作流
- [Amazon OpenSearch](https://aws.amazon.com/opensearch-service/) 用于向量嵌入
- Amazon Bedrock AgentCore 用于 IDP 工作流
- Strands Agent SDK 作为定义执行 IDP 工具的开源框架
- Bedrock Data Automation（BDA）用于从你的文档中提取结构化洞察

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/22/ml-18711-image-1.jpg)

按以下步骤开始：

- 把相关文档上传到 Amazon S3
- 使用 Amazon Bedrock Data Automation 创建 Amazon Bedrock Knowledge Base 并解析 S3 数据源。
- 文档 chunk 以向量嵌入形式存储在 Amazon OpenSearch 中
- 部署在 Amazon Bedrock AgentCore Runtime 上的 Strands Agent 执行 RAG 以回答用户问题。
- 最终用户收到响应

### 配置 AWS CLI

使用以下命令，用你的 Amazon 账户与 AWS 区域的 AWS 凭证配置 [AWS 命令行界面](https://aws.amazon.com/cli)（AWS CLI）。开始之前，请查看 [AWS Bedrock Data Automation 的区域可用性与定价](https://aws.amazon.com/bedrock/pricing/)：

```
aws configure
```

### 在本地克隆并构建 GitHub 仓库

```
git clone https://github.com/aws-samples/sample-for-amazon-bda-agents
cd sample-for-amazon-bda-agents
```

打开下面这个 Jupyter notebook：

```
bedrock-data-automation-with-agents.ipynb
```

## Bedrock Data Automation 与 AgentCore Notebook 操作说明：

该 notebook 演示如何使用 BDA 与 Amazon Bedrock AgentCore Runtime 创建 IDP 方案。我们不使用传统的 Bedrock Agents，而是通过 AgentCore 部署 Strands Agent，从而在框架灵活性之上获得企业级能力。更具体的说明包含在 Jupyter notebook 中。以下是使用 Bedrock AgentCore 以 data automation 作为解析器设置 Bedrock Knowledge Bases 的概览。

步骤：

- 导入库并设置 AgentCore 能力
- 使用 BDA 创建 Amazon Bedrock 的 Knowledge Base
- 把学术报告数据集上传到 Amazon S3
- 使用 AgentCore Runtime 部署 Strands Agent
- 测试由 AgentCore 托管的 agent
- 清理所有资源

## 安全考量

该实现使用了若干安全防护措施，例如：

- 安全的文件上传处理
- 基于 Identity and Access Management（IAM）角色的访问控制
- 输入验证与错误处理

注意：该实现仅用于演示目的。在生产环境部署之前，还需要额外的安全控制、测试与架构评审。

## 优势与用例

该方案对以下场景尤其有价值：

- 自动化文档处理工作流
- 大规模数据集上的智能文档分析
- 基于文档内容的问答系统
- 多模态内容处理

## 结论

该方案演示了如何使用 Amazon Bedrock AgentCore 的能力构建智能文档处理应用。通过构建支持 Amazon Bedrock Data Automation 的 Strands Agent，我们可以打造强大的应用，用工具理解多模态文档内容并与之交互。借助 Amazon Bedrock Data Automation，我们可以为视觉丰富的文档、图像、音频与视频等更复杂的数据格式增强 RAG 体验。

## 补充资源

更多信息请访问 [Amazon Bedrock](https://aws.amazon.com/bedrock/)。

服务用户指南：

- [Amazon Bedrock Knowledge Bases 用户指南](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [Amazon Bedrock AgentCore 用户指南](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)
- [Strands Agents：开源 AI Agents SDK](https://aws.amazon.com/blogs/opensource/introducing-strands-agents-an-open-source-ai-agents-sdk/)
- [Amazon Bedrock Data Automation 用户指南](https://docs.aws.amazon.com/bedrock/latest/userguide/bda.html)

相关示例：

- [Amazon Bedrock Data Automation AWS 示例](https://github.com/aws-solutions-library-samples/guidance-for-multimodal-data-processing-using-amazon-bedrock-data-automation)
- [Amazon Bedrock AgentCore AWS 示例](https://github.com/awslabs/amazon-bedrock-agentcore-samples/tree/main?tab=readme-ov-file)
- [Strands Agents 示例](https://github.com/strands-agents/samples)

### 关于作者

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/22/ml-18711-image-2-1.png)**Raian Osman** 是 AWS 的技术客户经理，与位于北美的教育科技客户紧密合作。他在 AWS 已有 3 年以上，最初以解决方案架构师的身份开始他的旅程。Raian 与组织紧密合作，优化并保护其在 AWS 上的工作负载，同时探索生成式 AI 的创新用例。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/22/ml-18711-image-3-1.jpeg)Andy Orlosky** 是 Amazon Web Services（AWS）的战略性业务拓展解决方案架构师，常驻德克萨斯州奥斯汀。他在 AWS 约有 2 年，但与公共部门的教育客户有着密切合作。作为 AI/ML 技术社区（Technical Field Community）的负责人，Andy 持续与客户深入交流，设计与扩展生成式 AI 方案。他持有 7 项 AWS 认证，业余时间喜欢与家人相处、与朋友一起运动，并为自己喜爱的球队加油。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/22/ml-18711-image-4-1.jpeg)Spencer Harrison** 是 Amazon Web Services（AWS）的合作伙伴解决方案架构师，帮助公共部门组织利用云技术专注于业务成果。他热衷于用技术改进流程与工作流。工作之外，Spencer 的兴趣包括阅读、匹克球与个人理财。
