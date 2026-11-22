---
vendor: aws_bedrock
title: Build an AI-powered website assistant with Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-an-ai-powered-website-assistant-with-amazon-bedrock
date: 2025-12-29
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 5a340ac53ef7
---

# 使用 Amazon Bedrock 构建 AI 驱动的网站助手

企业面临一个日益严峻的挑战：客户需要快速得到答案，而支持团队却不堪重负。产品手册和知识库文章这类支持文档，通常需要用户在数百页内容中翻找；而支持 agent 往往每天要处理 20–30 条客户查询，才能定位到具体信息。

本文演示如何利用 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 和 [Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/) 构建一个由 AI 驱动的网站助手来解决这一挑战。该方案旨在同时惠及内部团队与外部客户，并可带来以下收益：

- 为客户提供即时、相关的答案，免去他们翻阅文档的负担
- 为支持 agent 提供强大的知识检索系统，缩短问题解决时间
- 全天候自动化支持

## 方案概述

该方案使用检索增强生成（RAG），从知识库中检索相关信息，并依据用户的访问权限返回给用户。它由以下关键组件构成：

- Amazon Bedrock Knowledge Bases – 公司网站上的内容会被抓取并存储到知识库中。来自 [Amazon Simple Storage Service](https://aws.amazon.com/s3)（Amazon S3）桶的文档（包括手册和故障排查指南）也会被索引并存储到知识库中。借助 Amazon Bedrock Knowledge Bases，你可以配置多个数据源，并使用筛选配置来区分内部信息与外部信息。这有助于通过先进的安全控制保护内部数据。
- **Amazon Bedrock 托管的 LLM – **Amazon Bedrock 中的大语言模型（LLM）为用户问题生成由 AI 驱动的响应。
- **可扩展的无服务器架构** **–** 该方案使用 [Amazon Elastic Container Service](https://aws.amazon.com/ecs/)（Amazon ECS）托管 UI，并使用 [AWS Lambda](https://aws.amazon.com/lambda/) 函数处理用户请求。
- **自动化 CI/CD 部署** – 该方案使用 [AWS Cloud Development Kit](https://aws.amazon.com/cdk/)（AWS CDK）处理持续集成与持续交付（CI/CD）部署。

下图展示了该方案的架构。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/16/image-1-8.png)

工作流包含以下步骤：

- Amazon Bedrock Knowledge Bases 对上传到 Amazon S3 的文档进行分块并生成 embedding，以此来处理它们。此外，Amazon Bedrock 的网页抓取器会访问选定的网站，以提取并摄取其内容。
- 该 Web 应用以 ECS 应用的形式运行。内部与外部用户通过 [Elastic Load Balancing](https://aws.amazon.com/elasticloadbalancing/)（ELB）使用浏览器访问该应用。用户使用注册在 [Amazon Cognito](https://aws.amazon.com/cognito/) 用户池中的登录凭证登录应用。
- 当用户提交问题时，应用会调用一个 Lambda 函数，该函数使用 Amazon Bedrock API 从知识库中检索相关信息。它还会根据用户类型（外部或内部）向 Amazon Bedrock 提供相应的数据源 ID，使知识库只检索该用户类型可访问的信息。
- 随后，Lambda 函数调用 [Amazon Nova Lite](https://aws.amazon.com/ai/generative-ai/nova/) LLM 生成响应。LLM 用知识库中的信息作补充来生成对用户查询的响应，该响应由 Lambda 函数返回并展示给用户。

在接下来的小节中，我们演示如何抓取并配置外部网站作为知识库，以及如何上传内部文档。

## 前提条件

要部署本文中的方案，你需要准备好以下内容：

- 一个 [AWS 账户](https://signin.aws.amazon.com/signup?request_type=builderId)。
- 在 Amazon Bedrock 中为 [Amazon Titan](https://aws.amazon.com/bedrock/amazon-models/titan/) 和 [Amazon Nova Lite](https://aws.amazon.com/ai/generative-ai/nova/) 开通[模型访问](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)。模型访问所用的 AWS 区域应与部署方案的区域保持一致。
- 同一区域中用于存储内部数据的 S3 桶。

## 创建知识库并摄取网站数据

第一步是构建一个知识库，用于摄取来自某个网站的数据以及来自 S3 桶的运营文档。请完成以下步骤来创建知识库：

- 在 Amazon Bedrock 控制台的导航窗格中，选择 **Builder tools** 下的 **Knowledge Bases**。
- 在 **Create** 下拉菜单中，选择 **Knowledge Base with vector store**。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/16/image-2-8.png)

- 在 **Knowledge Base name** 中，输入一个名称。
- 在 **Choose a data source** 中，选择 **Web Crawler**。
- 选择 **Next**。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/16/image-3-8.png)

- 在 **Data source name** 中，为你的数据源输入一个名称。
- 在 **Source URLs** 中，输入要抓取的目标网站 HTML 页面。例如，我们使用 `https://docs.aws.amazon.com/AmazonS3/latest/userguide/GetStartedWithS3.html`。
- 在 **Website domain range** 中，选择 **Default** 作为抓取范围。如果你想把抓取限制在特定的域或子域，也可以将其配置为仅限主机域或子域。
- 在 **URL regex filter** 中，你可以配置 URL 模式以包含或排除特定 URL。本示例中我们留空此设置。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/16/image-4-8.png)

- 在 **Chunking strategy** 中，你可以配置内容解析选项来定制数据分块策略。本示例中我们保留 **Default chunking**。
- 选择 **Next**。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/16/image-5-7.png)

- 选择 Amazon Titan Text Embeddings V2 模型，然后选择 **Apply**。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/16/image-6-6.png)

- 在 **Vector store type** 中，选择 **Amazon OpenSearch Serverless**，然后选择 **Next**。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/16/image-7-6.png)

- 检查配置，然后选择 **Create Knowledge Base***。 *

至此，你已创建了一个知识库，其数据源已配置为你提供的网站链接。

- 在知识库详情页上，选择你新建的数据源并选择 **Sync**，以抓取网站并摄取数据。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/16/image-8-5.png)

## 配置 Amazon S3 数据源

请完成以下步骤，把你 S3 桶中的文档配置为内部数据源：

- 在知识库详情页的 **Data source** 区域中，选择 **Add**。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/16/image-9-5.png)

- 将数据源指定为 Amazon S3。
- 选择你的 S3 桶。
- 解析策略保留默认设置。
- 选择 **Next**。
- 检查配置，然后选择 **Add data source**。
- 在知识库详情页的 **Data source** 区域中，选择你新建的数据源并选择 **Sync**，以索引 S3 桶中文档的数据。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/16/image-10-7.png)

## 上传内部文档

在本示例中，我们向新建的 S3 桶数据源上传一份文档。下面的截图展示了我们的文档示例。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/24/image-11-9.png)

请完成以下步骤上传该文档：

- 在 Amazon S3 控制台的导航窗格中，选择 **Buckets**。
- 选择你创建的桶，然后选择 **Upload** 上传该文档。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/16/image-12-5.png)

- 在 Amazon Bedrock 控制台中，进入你创建的知识库。
- 选择你创建的内部数据源，然后选择 **Sync**，把上传的文档同步到向量存储。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/16/image-13-4.png)

记下知识库 ID，以及外部与内部数据源的数据源 ID。下一步部署方案基础设施时，你会用到这些信息。

## 部署方案基础设施

要使用 AWS CDK 部署方案基础设施，请完成以下步骤：

- 从[代码仓库](https://github.com/aws-samples/sample-aipowered-web-using-amazon-bedrock)下载代码。
- 进入下载项目内的 iac 目录：

`cd ./customer-support-ai/iac`

- 打开 parameters.json 文件，用上一节中记录的值更新知识库 ID 和数据源 ID：

```
"external_source_id": "Set this to value from Amazon Bedrock Knowledge Base datasource",
"internal_source_id": "Set this to value from Amazon Bedrock Knowledge Base datasource",
"knowledge_base_id": "Set this to value from Amazon Bedrock Knowledge Base",
```

- 按照 customer-support-ai/README.md 文件中定义的部署说明，搭建方案基础设施。

部署完成后，你可以在脚本执行输出中找到 [Application Load Balancer](https://aws.amazon.com/elasticloadbalancing/application-load-balancer/)（ALB）的 URL 以及演示用户的信息。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/16/image-14-5.png)

你也可以打开 Amazon EC2 控制台，在导航窗格中选择 **Load Balancers **来查看该 ALB。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/16/image-15-4.png)

在 ALB 详情页上，复制其 DNS 名称。你可以用它访问 UI 来试用该方案。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/16/image-16-5.png)

## 提交问题

让我们探索一个 Amazon S3 服务支持的示例。该方案支持不同类别的用户解决各自的查询，同时使用 Amazon Bedrock Knowledge Bases 管理特定数据源（例如网站内容、文档和支持工单），并借助内置的筛选控制把内部运营文档与可公开访问的信息区分开来。例如，内部用户可以同时访问公司专属的运营指南与公开文档，而外部用户只能接触公开可用的内容。

在浏览器中打开该 DNS URL。输入外部用户的凭证，并选择 **Login**。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/16/image-17-5.png)

身份验证成功后，你将被重定向到首页。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/16/image-18-4.png)

在导航窗格中选择 **Support AI Assistant**，即可提出与 Amazon S3 相关的问题。该助手可以基于 [Getting started with Amazon S3 guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/GetStartedWithS3.html) 中可用的信息给出相关响应。不过，如果外部用户提出的问题涉及仅内部用户可访问的信息，AI 助手不会把内部信息提供给该用户，只会给出外部用户可访问的信息。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/16/image-19-4.png)

退出登录，再以内部用户身份重新登录，并提出相同的查询。内部用户可以访问内部文档中可用的相关信息。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/24/image-20-6.png)

## 清理

如果你决定停止使用该方案，请完成以下步骤以移除其相关资源：

- 进入项目代码内的 iac 目录，并在终端中运行以下命令：要运行清理脚本，请使用以下命令：`cd iac ./cleanup.sh` 如需手动执行此操作，请使用以下命令：`cd iac cdk destroy --all`
- 在 Amazon Bedrock 控制台的导航窗格中，选择 **Builder tools** 下的 **Knowledge Bases**。
- 选择你创建的知识库，然后选择 **Delete**。
- 输入 delete 并选择 **Delete** 以确认。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/16/image-21-6.png)
- 在 OpenSearch Service 控制台的导航窗格中，选择 **Serverless** 下的 **Collections **。
- 选择在基础设施预置期间创建的集合，然后选择 **Delete**。
- 输入 confirm 并选择 **Delete** 以确认。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/16/image-22-4.png)

## 结论

本文演示了如何通过网页抓取构建知识库并上传文档，从而创建一个能快速检索信息的 AI 驱动网站助手。你可以用同样的方法开发其他生成式 AI 原型与应用。

如果你对生成式 AI 的基础知识以及如何使用 FM 感兴趣，包括高级 prompt 技巧，可以看看实践课程 [Generative AI with LLMs](https://www.deeplearning.ai/courses/generative-ai-with-llms/)。这门按需的为期 3 周课程面向希望学习如何用 LLM 构建生成式 AI 应用的数据科学家与工程师。它是开始用 Amazon Bedrock 构建的良好基础。[注册](https://pages.awscloud.com/generative-AI-interest-learn.html) 以了解更多关于 Amazon Bedrock 的信息。

### 关于作者

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/19/shashank-2-1.jpeg)Shashank Jain** 是 Amazon Web Services（AWS）的云应用架构师（Cloud Application Architect），专精于生成式 AI 解决方案、云原生应用架构与可持续性。他与客户合作，使用无服务器技术、现代 DevSecOps 实践、基础设施即代码（Infrastructure as Code）以及事件驱动架构，设计和实施安全、可扩展的 AI 驱动应用，从而交付可衡量的业务价值。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/19/jeffli.small_-1.jpg)Jeff Li** 是 AWS Professional Services 团队的高级云应用架构师（Senior Cloud Application Architect）。他热衷于与客户深入合作，打造解决方案并现代化应用，以支撑业务创新。业余时间，他喜欢打网球、听音乐和阅读。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/19/ranjith-1.png)Ranjith Kurumbaru Kandiyil** 是 Amazon Web Services（AWS）驻多伦多的数据与 AI/ML 架构师（Data and AI/ML Architect）。他专精于与客户协作，设计和实施前沿的 AI/ML 解决方案。他当前的重点是利用最先进的人工智能技术解决复杂的业务挑战。
