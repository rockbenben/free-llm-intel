---
vendor: aws_bedrock
title: Automate IT operations with Amazon Bedrock Agents
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/automate-it-operations-with-amazon-bedrock-agents
date: 2025-03-21
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: caf94d7874f2
---

# 使用 Amazon Bedrock Agents 自动化 IT 运维

IT 运维团队面临这样的挑战：在管理最终用户提交的大量事件（incident）的同时，保障关键系统的顺畅运行。事件管理中的人工干预可能既耗时又容易出错，因为它依赖重复性任务、人的判断，以及可能存在的沟通缺口。把[生成式 AI](https://aws.amazon.com/ai/generative-ai/) 用于 IT 运维提供了一种变革性的解决方案，帮助自动化事件的检测、诊断和修复，提升运维效率。

面向 IT 运维的 AI（AIOps）是应用 AI 和机器学习（ML）技术来自动化并增强 IT 运维。AIOps 通过实时自动检测、诊断和解决事件，帮助 IT 团队管理和监控大规模系统。它把来自各种来源的数据——例如日志、指标和事件——结合起来，以分析系统行为、识别异常，并推荐或执行自动化的修复动作。通过减少人工干预，AIOps 提升运维效率、加快事件解决速度并最大限度缩短停机时间。

本文介绍一个全面的 AIOps 解决方案，它结合 [Amazon Bedrock](https://aws.amazon.com/bedrock/)、[AWS Lambda](https://aws.amazon.com/lambda/) 和 [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/) 等各种 AWS 服务，构建一个用于高效事件管理的 AI 助手。该解决方案还使用 [Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/) 和 [Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/)。该解决方案借助 Amazon Bedrock 的力量，支持部署能够监控 IT 系统、分析日志和指标并调用自动化修复流程的智能 agent。

Amazon Bedrock 是一项完全托管的服务，通过单一 API 提供来自领先 AI 初创公司和 Amazon 的基础模型（FM），因此你可以从广泛的 FM 中选择最适合自己使用场景的模型。借助 Amazon Bedrock 的无服务器体验，你可以快速上手、用自己的数据私密地定制 FM，并使用 AWS 工具将其集成和部署到你的应用中，而无需管理基础设施。Amazon Bedrock Knowledge Bases 是一项完全托管的能力，内置会话上下文管理和来源标注，帮助你实现完整的[检索增强生成](https://aws.amazon.com/what-is/retrieval-augmented-generation/)（RAG）工作流——从数据摄取到检索和 prompt 增强——而无需自行构建与数据源的自定义集成、也无需管理数据流。Amazon Bedrock Agents 是一项完全托管的能力，让开发者能够直接创建基于生成式 AI 的应用，为广泛的用例完成复杂任务，并基于专有知识来源提供最新的答案。

生成式 AI 正在迅速改变企业，并在各行各业释放新的可能性。本文着重说明 large language model（LLM）的变革性影响。凭借编码人类专业知识并以自然语言交流的能力，生成式 AI 可以帮助增强人类能力，让组织能够规模化地利用知识。

## 使用 runbook 进行 IT 运维的挑战

Runbook 是详细的逐步指南，列明完成特定操作所需的流程、规程和任务，通常用于 IT 和系统管理领域。它们常被用来记录重复性任务、故障排查步骤和日常维护。通过标准化对问题的响应并促进任务执行的一致性，runbook 帮助团队提升运维效率、精简工作流。大多数组织依赖 runbook 来简化复杂流程，使团队能够直接处理日常操作并有效响应系统问题。对组织而言，管理数百个 runbook、监控其状态、跟踪失败情况并建立恰当的告警可能变得困难，这会给 IT 团队造成可见性缺口。当你为各种流程准备多个 runbook 时，管理它们之间的依赖关系和运行顺序可能变得复杂而繁琐。处理失败场景并确保一切按正确顺序运行颇具挑战。

以下是大多数组织在人工 IT 运维中面临的一些挑战：

- 通过运行日志和指标进行手工诊断
- runbook 依赖与执行顺序的梳理
- 没有自动化的修复流程
- 无法实时了解 runbook 的执行进度

## 解决方案概述

Amazon Bedrock 是该解决方案的基础，赋能智能 agent 监控 IT 系统、分析数据并自动化修复。该解决方案提供示例 [AWS Cloud Development Kit](https://aws.amazon.com/cdk/)（AWS CDK）代码来部署它。该 AIOps 解决方案使用 Amazon Bedrock Agents 提供一个 AI 助手，帮助实现运维自动化和 runbook 执行。

以下架构图说明了该解决方案的整体流程。

![Amazon Bedrock AIOps 自动化](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/19/ML-16260-Architecture-Diagram.jpg)

该 agent 使用 Amazon Bedrock 上可用的 Anthropic’s Claude LLM 作为 FM 之一，来分析事件详情，并从 knowledge base 中检索相关信息——该知识库是经过整理的 runbook 和最佳实践集合。这使 agent 具备业务专属的上下文，确保响应精确，并以 Amazon Bedrock Knowledge Bases 中的数据为支撑。基于分析结果，agent 动态生成针对该具体事件定制的 runbook，并调用恰当的修复动作，例如创建快照、重启实例、扩展资源或运行自定义工作流。

Amazon Bedrock Knowledge Bases 创建一个 [Amazon OpenSearch Serverless](https://aws.amazon.com/opensearch-service/features/serverless/) 向量搜索集合，用于存储并索引事件数据、runbook 和运行日志，从而实现信息的高效搜索和检索。Lambda 函数被用来执行特定动作，例如发送通知、调用 API 或调用自动化工作流。该解决方案还与 [Amazon Simple Email Service](https://aws.amazon.com/ses)（Amazon SES）集成，以便及时通知利益相关方。

该解决方案的工作流包含以下步骤：

- 以各种格式（例如 Word 文档、PDF 或文本文件）存在的现有 runbook 被上传到 [Amazon Simple Storage Service](https://aws.amazon.com/s3)（Amazon S3）。
- Amazon Bedrock Knowledge Bases 使用选定的嵌入模型把这些文档转换为向量嵌入，该模型在 knowledge base 设置过程中配置。
- 这些向量嵌入存储在 OpenSearch Serverless 中以实现高效检索，这一点同样在 knowledge base 设置期间配置。
- 随后设置 agent 和 action group，为其配置处理不同场景所需的 API 和 prompt。
- OpenAPI 规范定义需要调用哪些 API，以及它们的输入参数和预期输出，使 Amazon Bedrock Agents 能够做出有依据的决策。
- 收到用户 prompt 后，Amazon Bedrock Agents 使用 RAG、action group 和 OpenAPI 规范来确定恰当的 API 调用。若需要更多细节，agent 会向用户询问补充信息。
- Amazon Bedrock Agents 可以按需迭代并调用多个函数，直到任务成功完成。

## 先决条件

要实现这一 AIOps 解决方案，你需要一个有效的 AWS 账户，以及对 AWS CDK 和以下 AWS 服务的基本了解：

- Amazon Bedrock
- Amazon CloudWatch
- AWS Lambda
- Amazon OpenSearch Serverless
- Amazon SES
- Amazon S3

此外，你还需要预置所需的基础设施组件，例如 [Amazon Elastic Compute Cloud](https://aws.amazon.com/ec2)（Amazon EC2）实例、[Amazon Elastic Block Store](https://aws.amazon.com/ebs)（Amazon EBS）卷，以及你的 IT 运维环境特有的其他资源。

## 使用 OpenSearch Serverless 构建 RAG pipeline

该解决方案使用 RAG pipeline 从运维 runbook 中找出相关内容与最佳实践，以生成响应。RAG 方法有助于确保 agent 生成的响应以事实性文档为依据，从而避免幻觉。来自 knowledge base 的相关匹配项引导 Anthropic’s Claude 3 Haiku 模型聚焦于相关信息。RAG 过程由 Amazon Bedrock Knowledge Bases 提供动力，它存储的信息可供 Amazon Bedrock agent 访问和使用。对本用例而言，我们的 knowledge base 包含组织现有的 runbook，其中提供了解决 AWS 资源上各类运维问题的逐步规程。

该 pipeline 包含以下关键任务：

- **把文档摄取到 S3 桶 **——第一步把现有 runbook 摄取到 S3 桶，借助 OpenSearch Serverless 创建可搜索的索引。
- **使用 CloudWatch 监控基础设施健康状况**——使用一个 Amazon Bedrock action group 调用 Lambda 函数，从某个 AWS 账户获取 EC2 实例的 CloudWatch 指标和告警。这些具体的检查随后被用作 Anthropic’s Claude 3 Haiku 模型的输入，以形成该账户的健康状况概览。

## 配置 Amazon Bedrock Agents

Amazon Bedrock Agents 用来自 Amazon Bedrock Knowledge Bases 的正确信息来增强用户请求，以生成准确的响应。对本用例而言，我们的 knowledge base 包含组织现有的 runbook，其中提供了解决 AWS 资源上各类运维问题的逐步规程。

通过配置恰当的 [action group](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-action-create.html)，并用相关数据填充 knowledge base，你可以把 Amazon Bedrock agent 定制为协助特定任务或领域，并在其预期范围内提供准确、有用的响应。

Amazon Bedrock agent 使 Anthropic’s Claude 3 Haiku 能够使用工具，克服知识截止和幻觉等 LLM 局限，通过 API 调用和其他外部交互提升任务完成度。

该 agent 的工作流是：使用 API 检查资源告警，若发现告警，则获取并执行相关 runbook 中的步骤（例如创建快照、重启实例和发送电子邮件）。

整个系统实现了对 AWS 上运维问题的自动检测和修复，同时通过 runbook 方法强制遵循已有文档记录的规程。

要使用 Amazon Bedrock Agents 设置该解决方案，请参阅 [GitHub 仓库](https://github.com/aws-samples/improving-it-operations-efficiency-with-aiops)，它会预置以下资源。部署代码时请务必核实 [AWS Identity and Access Management](https://aws.amazon.com/iam/)（IAM）权限并遵循 [IAM 最佳实践](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)。建议为 [IAM 策略应用最小权限](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#grant-least-privilege)。

- S3 桶
- Amazon Bedrock agent
- Action group
- Amazon Bedrock agent IAM 角色
- Amazon Bedrock agent action group
- Lambda 函数
- Lambda 服务策略权限
- Lambda IAM 角色

## 优势

借助该解决方案，组织可以自动化其运维并节省大量时间。与人工执行相比，自动化也更不容易出错。它还带来以下额外优势：

- **减少人工干预**——自动化事件的检测、诊断和修复有助于最大限度减少人工参与，降低人工流程中常见的错误、延迟和不一致的可能性。
- **提升运维效率**——通过使用生成式 AI，该解决方案加快了事件解决速度并优化了运维工作流。runbook 执行、资源监控和修复等任务的自动化使 IT 团队能够聚焦于更具战略性的工作。
- **可扩展性**——随着组织成长，人工管理 IT 运维变得越来越复杂。使用生成式 AI 实现运维自动化可以随业务扩展，管理更多的事件、runbook 和基础设施，而无需按比例增加人员。

## 清理

为避免产生不必要的费用，建议在不再使用时删除实现该解决方案期间创建的资源。你可以[通过删除 AWS CloudFormation 堆栈](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-delete-stack.html)（作为该解决方案的一部分部署）来做，或在 [AWS Management Console](https://aws.amazon.com/console) 上手动删除资源，或使用 [AWS Command Line Interface](https://aws.amazon.com/cli)（AWS CLI）。

## 结语

本文介绍的 AIOps pipeline 赋能 IT 运维团队精简事件管理流程、减少人工干预并提升运维效率。借助 AWS 服务的能力，组织可以自动化事件的检测、诊断和修复，从而更快解决事件并最大限度缩短停机时间。

通过整合 Amazon Bedrock、Amazon Bedrock 上的 Anthropic’s Claude、Amazon Bedrock Agents、Amazon Bedrock Knowledge Bases 以及其他配套服务，该解决方案提供了对事件的实时可见性、自动化的 runbook 生成和动态修复动作。此外，该解决方案还提供及时通知以及 AI agent 与人类操作员之间的无缝协作，促成更主动、更高效的 IT 运维方式。

生成式 AI 正在迅速改变企业轻松利用云技术的方式。这个使用 Amazon Bedrock 的解决方案展示了生成式 AI 模型在增强人类能力方面的巨大潜力。通过为开发者提供以 AWS 最佳实践为依据的专业指导，这个 AI 助手使 DevOps 团队能够审视并优化跨 AWS 账户的云架构。

不妨亲自试用该解决方案，并在评论区留下任何反馈或问题。

### **关于作者**

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/19/Upen.jpeg)****Upendra V** 是 Amazon Web Services 的高级解决方案架构师，专长于生成式 AI 和云解决方案。他帮助企业客户设计并部署可用于生产的生成式 AI 工作负载、实施 large language model（LLM）和 Agentic AI 系统，并优化云部署。凭借在云采用和机器学习方面的专长，他帮助组织高效构建并扩展 AI 驱动的应用。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/19/DD-Pic-1-1.jpg)**Deepak Dixit ****是 Amazon Web Services 的解决方案架构师，专长于生成式 AI 和云解决方案。他帮助企业对可扩展的 AI/ML 工作负载进行架构设计、实施 large language model（LLM），并优化云原生应用。
