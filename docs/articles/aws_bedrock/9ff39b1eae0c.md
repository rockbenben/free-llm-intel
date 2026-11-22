---
vendor: aws_bedrock
title: Simplify multimodal generative AI with Amazon Bedrock Data Automation
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/simplify-multimodal-generative-ai-with-amazon-bedrock-data-automation
date: 2024-12-17
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 45c5da4173c4
---

# 用 Amazon Bedrock Data Automation 简化多模态生成式 AI

| **2025 年 3 月：** Amazon Bedrock Data Automation（BDA）现已正式可用，并带来以下改进：  新增区域：除 `us-west-2` 之外，BDA 现也已在 `us-east-1` 提供。跨区域推理支持：BDA 现在使用 AWS 跨区域推理，在你所在的地理范围内优化跨区域路由以处理你的请求。文档准确性改进：多种文档类型的准确性均有所提升。视频准确性改进：提升了场景级和整段视频摘要的准确性，从而提供更丰富的上下文洞见。Logo 检测：支持检测图像和视频中 35,000+ 个公司 logo。标签支持：BDA 现在支持为 BDA 资源和任务打标签，以追踪成本并在 AWS Identity and Access Management（IAM）中实施基于标签的访问策略。AWS PrivateLink 支持：可通过 PrivateLink 从你的 VPC 私有访问 BDA。KMS-CMK 支持：BDA 现在支持客户托管密钥（CMK），以实现细粒度的加密控制。 |
| --- |

开发者在使用[基础模型](https://aws.amazon.com/what-is/foundation-models/)（FM）从非结构化资产中提取数据时会面临重大挑战。这一数据提取过程需要仔细挑选符合开发者特定准确性、成本和功能要求的模型。此外，开发者还必须投入大量时间，通过微调和大量的 prompt 工程来优化性价比。管理多个模型、实施安全防护栏，以及调整输出以对齐下游系统要求，都可能既困难又耗时。

[Amazon Bedrock Data Automation](https://aws.amazon.com/bedrock/bda/) 有助于应对这些及其他挑战。这项来自 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 的新能力，为各种技能水平的开发者提供统一体验，轻松实现从文档、图像、音频和视频中提取、转换并生成相关洞见的自动化，从而构建由[生成式 AI](https://aws.amazon.com/generative-ai/) 驱动的应用。借助 Amazon Bedrock Data Automation，客户可以从其非结构化多模态内容中提取洞见，并以与应用兼容的格式呈现，从而充分利用自身数据。Amazon Bedrock Data Automation 的托管体验、易用性和定制能力帮助客户更快交付业务价值，免去花时间精力去编排多个模型、设计 prompt 或拼接输出。

在本文中，我们演示如何在 [AWS Management Console](https://aws.amazon.com/console/) 和 [AWS SDK for Python（Boto3）](https://aws.amazon.com/sdk-for-python/)中使用 Amazon Bedrock Data Automation，以支持媒体分析和智能文档处理（IDP）工作流。

## Amazon Bedrock Data Automation 概览

你可以使用 Amazon Bedrock Data Automation 生成标准输出和自定义输出。标准输出是与模态相关的默认洞见，例如捕捉关键时刻的视频摘要、视觉和听觉上的有害内容、文档图表解释、图形数据等。自定义输出使用客户定义的 blueprint，通过自然语言或 schema 编辑器指定输出要求。blueprint 包含要提取的字段列表、每个字段的数据格式，以及其他指令，例如数据转换和归一化。这使客户能够完全掌控输出，从而轻松把 Amazon Bedrock Data Automation 集成到既有应用中。

使用 Amazon Bedrock Data Automation，你可以构建强大的生成式 AI 应用，并自动化媒体分析和 IDP 之类的用例。Amazon Bedrock Data Automation 还与 [Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/) 集成，使开发者更容易从其非结构化多模态内容中生成有意义的信息，为[检索增强生成](https://aws.amazon.com/what-is/retrieval-augmented-generation/)（RAG）提供更相关的响应。

客户可以开始使用全部四种模态（文档、图像、视频和音频）的标准输出，以及文档和图像的自定义输出。视频和音频的自定义输出将在未来提供支持。

## 面向图像、音频和视频的 Amazon Bedrock Data Automation

举一个媒体分析的例子：假设媒体与娱乐行业的客户希望通过上下文广告投放，把电视剧和电影这类长内容变现。要在恰当的视频时刻投放恰当的广告，你需要从广告和视频内容双方都提取有意义的洞见。Amazon Bedrock Data Automation 通过生成这些洞见，为你的上下文广告投放应用提供支持。例如，你可以提取视频摘要、场景级摘要、内容审核概念以及基于 Interactive Advertising Bureau（IAB）分类法的场景分类等有价值的信息。

要开始使用 Amazon Bedrock Data Automation 提取洞见，你可以创建一个项目，在其中通过 AWS 控制台、[AWS Command Line Interface](https://aws.amazon.com/cli/)（AWS CLI）或 API 指定输出配置。

要在 [Amazon Bedrock 控制台](https://console.aws.amazon.com/bedrock) 中创建项目，请按以下步骤操作：

- 在导航窗格中展开 **Data Automation** 下拉菜单并选择 **Projects**，如下方截图所示。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/03/1_2025-02-25_12-37-01.jpg)
- 在 **Projects** 控制台中创建一个新项目并填写项目名称，如下方截图所示。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/03/2_2025-02-25_12-38-06.jpg)
- 在项目内选择 **Edit**（如下方截图所示），以指定或修改输出配置。标准输出是与 Amazon Bedrock Data Automation 交互的默认方式，可用于音频、文档、图像和视频；每个项目可以为每种数据类型配置一份标准输出配置。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/03/3_2025-02-25_12-40-45.jpg)
- 对于希望分析图像和视频以做媒体分析的客户，标准输出可用于生成图像摘要、视频场景摘要以及基于 IAB 分类法的场景分类等洞见。你可以在 **Standard output** 选项卡中勾选图像摘要、视频场景摘要和 IAB 分类法复选框，然后选择 **Save changes** 完成项目配置，如下方截图所示。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/03/4_2025-02-25_12-43-28.jpg)
- 要用你的媒体资产测试该标准输出配置，请选择 **Test**，如下方截图所示。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/03/5_2025-02-25_12-44-31.jpg)

下一个示例使用该项目为一条旅游广告生成洞见。

- 上传一张图像，然后选择 **Generate results**（如下方截图所示），让 Amazon Bedrock Data Automation 发起推理请求。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/03/6_2025-02-25_12-46-58.jpg)
- Amazon Bedrock Data Automation 会根据项目配置处理上传的文件，自动识别出该文件是图像，然后为该旅游广告生成摘要和 IAB 类目。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/03/7_2025-02-25_12-50-57.jpg)
- 为该广告图像生成洞见后，你还可以生成视频洞见，以确定最适合有效投放广告的视频场景。在同一项目中，上传一个视频文件并选择 **Generate results**，如下方截图所示。
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/03/8_2025-02-25_12-52-48.jpg)

Amazon Bedrock Data Automation 会识别出该文件是视频，并根据项目中指定的标准输出配置为该视频生成洞见，如下方截图所示。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/03/9_2025-02-25_12-54-55.jpg)

来自 Amazon Bedrock Data Automation 的这些洞见，可以帮助你在视频内容中有效投放相关广告，从而有助于提升内容变现。

## 使用 Amazon Bedrock Data Automation 进行智能文档处理

你可以使用 Amazon Bedrock Data Automation 大规模自动化 IDP 工作流，而无需编排分类、提取、归一化或校验等复杂的文档处理任务。

以一个抵押贷款为例：贷款方希望自动化抵押贷款资料包的处理，以简化其 IDP pipeline 并提升贷款处理的准确性。Amazon Bedrock Data Automation 简化了文档拆分、分类、数据提取、输出格式归一化和数据校验等复杂 IDP 任务的自动化。Amazon Bedrock Data Automation 还引入了置信度评分和输出数据的可视化定位（visual grounding），以缓解幻觉并帮助提升结果可靠性。

例如，你可以通过定义 blueprint 来生成自定义输出，blueprint 使用自然语言或 schema 编辑器指定输出要求，从而在一次简化的 API 调用中处理多种文件类型。Blueprint 可以通过控制台或 API 创建，你可以使用目录中的 blueprint，也可以为文档和图像创建自定义 blueprint。

对于所有模态，该工作流都包含三个主要步骤：创建项目、发起分析、取回结果。

下面的方案使用 [Amazon SDK for Python（Boto3）](https://aws.amazon.com/sdk-for-python/)带你走一遍用 Amazon Bedrock Data Automation 实现的简化抵押贷款流程，它很容易集成到既有的 IDP 工作流中。

## 前提条件

在调用 Amazon Bedrock API 之前，请确认你已具备以下条件：

- 一个可访问 AWS 服务（包括 Amazon Bedrock Data Automation 和 [Amazon Simple Storage Service](https://aws.amazon.com/s3/)（Amazon S3））的 AWS 账户
- 已[设置好](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html)的 AWS CLI
- 已为 [Amazon Bedrock Data Automation API 设置好](https://docs.aws.amazon.com/bedrock/latest/userguide/bda-using-api.html)的 [AWS Identity and Access Management](https://aws.amazon.com/iam/)（IAM）用户，并为该 IAM 用户添加了相应权限
- 用于[配置](https://docs.aws.amazon.com/cli/v1/userguide/cli-chap-configure.html) AWS CLI 和权限的 IAM 用户访问密钥与私有密钥
- 最新版本的 [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) 库
- 在你的集成开发环境（IDE）中配置的最低 Python 版本 3.8
- 一个 S3 桶

## 创建自定义 blueprint

在本示例中，你有一个如下方图像所示的贷款资料包，其中包含三份文档：一张工资单、一份 W-2 表格和一张驾驶证。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/13/ML-17989-image010.png)

Amazon Bedrock Data Automation 为这三份文档提供了示例 blueprint，其中定义了常用的提取字段。不过，你也可以自定义 Amazon Bedrock Data Automation，从每份文档中提取特定字段。例如，你可以通过创建自定义 blueprint，仅从工资单中提取税前工资和实发工资。

要使用 API 创建自定义 blueprint，你可以通过 [Amazon Bedrock Data Automation 客户端](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-data-automation.html)使用 `CreateBlueprint` 操作。下面的示例展示了把税前工资和实发工资定义为传给 `CreateBlueprint` 的属性，以从贷款资料包中提取：

```
bda_create_blueprint_response = bedrock_data_automation_client.create_blueprint(
    blueprintName='CUSTOM_PAYSLIP_BLUEPRINT',
    type='DOCUMENT',
    blueprintStage='LIVE',
    schema=json.dumps({
        '$schema': 'http://json-schema.org/draft-07/schema#',
        'description': 'default',
        'documentClass': 'default',
        'type': 'object',
        'properties': {
            'gross_pay_this_period': {
                'type': 'number',
                'inferenceType': 'extractive',
                'description': 'The gross pay for this pay period from the Earnings table'
            },
            'net_pay': {
                'type': 'number',
                'inferenceType': 'extractive',
                'description': 'The net pay for this pay period from the bottom of the document'
            }
        }
    }),
)
```

`CreateBlueprint` 响应会返回工资单自定义 blueprint 的 `blueprintARN`：

```
'blueprintArn: arn:aws:bedrock:us-west-2:<AWS_ACCOUNT_ID>:blueprint/<BLUEPRINT_ID>'
```

### 配置 Amazon Bedrock Data Automation 项目

要开始使用 Amazon Bedrock Data Automation 的 blueprint 处理文件，你首先需要创建一个数据自动化项目。要处理包含不同文件类型的多页文档，你可以为每种文件类型配置不同的 blueprint。

使用 Amazon Bedrock Data Automation 可以在一个项目内应用多个文档 blueprint，从而在同一项目中处理不同类型的文档，每种文档各有自己的自定义提取逻辑。

使用 API 创建项目时，你需要调用 `CreateDataAutomationProject` 操作。下面的示例展示了如何为工资单使用自定义 blueprint、为 W-2 和驾驶证使用示例 blueprint 来配置自定义输出：

```
bda_bedrock_automation_create_project_response = bedrock_data_automation_client.create_data_automation_project(
    projectName='TEST_PROJECT',
    projectDescription='test BDA project',
    projectStage=bda_stage,
    standardOutputConfiguration={
        'document': {
            'outputFormat': {
                'textFormat': {
                    'types': ['PLAIN_TEXT']
                },
                'additionalFileFormat': {
                    'state': 'ENABLED',
                }
            }
        },
    },
    customOutputConfiguration={
        'blueprints': [
          {
              'blueprintArn': 'arn:aws:bedrock:us-west-2:<AWS_ACCOUNT_ID>:blueprint/<BLUEPRINT_ID>'
          },
          {
              'blueprintArn': 'arn:aws:bedrock:us-west-2:aws:blueprint/bedrock-data-automation-public-w2-form'
          },
          {
              'blueprintArn': 'arn:aws:bedrock:us-west-2:aws:blueprint/bedrock-data-automation-public-us-driver-license'
          },
        ],
    },
    overrideConfiguration={
        'document': {
            'splitter': {
                'state': 'ENABLED'
            }
        }
    },
)
```

`CreateProject` 响应会返回项目的 `projectARN`：

```
'arn:aws:bedrock:us-west-2:<AWS_ACCOUNT_ID>:data-automation-project/<PROJECT_ID>'
```

要在单个项目中使用多个文档 blueprint 处理不同类型的文档，Amazon Bedrock Data Automation 会使用拆分器（splitter）配置，该配置必须通过 API 启用。下面是拆分器的覆盖配置，更多信息可参阅 [Boto3 文档](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-data-automation/client/create_data_automation_project.html)：

```
overrideConfiguration={
    'document': {
        'splitter': {
            'state': 'ENABLED' | 'DISABLED'
        }
    }
},
```

创建时，该 API 会校验输入配置并创建新项目，返回 `projectARN`，如下方截图所示。

```
'arn:aws:bedrock:us-west-2:<AWS_ACCOUNT_ID>:data-automation-project/<PROJECT_ID>'
```

### 测试方案

至此 blueprint 和项目都已设置完成，可以使用 [Amazon Bedrock Data Automation 运行时](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-data-automation.html)的 `InvokeDataAutomationAsync` 操作来开始处理文件。该 API 调用会通过传入项目的 ARN，使用项目中定义的配置来启动对 S3 桶中文件（此处为贷款资料包）的异步处理：

```
bda_invoke_data_automation_async_response = bedrock_data_automation_runtime_client.invoke_data_automation_async(
    inputConfiguration={'s3Uri': '<S3_URI>'},
    outputConfiguration={'s3Uri': '<S3_URI>'},
    dataAutomationProfileARN=‘arn:aws:bedrock:us-west-2:<AWS_ACCOUNT_ID>:data-automation-profile/bda.v1:0‘
    dataAutomationConfiguration={
        ‘dataAutomationProjectArn’: ‘arn:aws:bedrock:us-west-2:<AWS_ACCOUNT_ID>:data-automation-project/<PROJECT_ID>‘,
        'stage': 'LIVE'
    }
)
```

`InvokeDataAutomationAsync` 会返回 `invocationARN`：

```
'arn:aws:bedrock:us-west-2:<AWS_ACCOUNT_ID>:data-automation-invocation/<INVOCATION_ID>'
```

`GetDataAutomationStatus` 可用于查看调用的状态，传入上一个响应中的 `InvocationARN`：

```
bda_invoke_data_automation_async_response = bedrock_data_automation_runtime_client.get_data_automation_status(
    invocationArn='arn:aws:bedrock:us-west-2:<AWS_ACCOUNT_ID>:data-automation-invocation/<INVOCATION_ID>'
)
```

任务完成后，导航到 `~/JOB_ID/0/custom_output/` 文件夹，在 `outputConfiguration` 所用的 S3 桶中查看结果。

从下面的示例输出可以看到，Amazon Bedrock Data Automation 以很高的置信度把该工资单文件与自定义工资单 blueprint 关联起来：

```
'matched_blueprint': {
    'arn': '<BLUEPRINT_ARN>', 'name': 'CUSTOM_PAYSLIP_BLUEPRINT', 'confidence': 0.99959725
}
```

使用匹配到的 blueprint，Amazon Bedrock Data Automation 能够准确提取 blueprint 中定义的每个字段：

```
'inference_result': {
    'net_pay': 291.9, 'gross_pay_this_period': 452.43
}
```

此外，Amazon Bedrock Data Automation 还会为每个字段返回置信区间和边界框信息：

```
'explainability_info': [{
    'net_pay': {'success': true, 'confidence': 0.96484375, 'geometry': [{'boundingBox': ...
```

本示例演示了客户如何使用 Amazon Bedrock Data Automation 简化并自动化 IDP 工作流。Amazon Bedrock Data Automation 自动化了从文档中提取数据、归一化和校验等复杂的文档处理任务。Amazon Bedrock Data Automation 有助于降低运营复杂度、提升处理效率，以应对更高的贷款处理量、减少错误并推动运营卓越。

## 清理

评估完该功能后，请删除 S3 桶及其中所有对象，以避免产生进一步费用。

## 总结

客户可以开始使用 Amazon Bedrock Data Automation，它已在 [AWS 区域](https://docs.aws.amazon.com/glossary/latest/reference/glos-chap.html#region) 美国东部（弗吉尼亚北部）和美国西部（俄勒冈）提供。进一步了解 [Amazon Bedrock Data Automation](https://aws.amazon.com/bedrock/bda/) 以及如何自动化地从非结构化内容生成准确信息，以构建基于生成式 AI 的应用。

## 关于作者

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/13/ian.jpg)**[**Ian Lodge**](https://www.linkedin.com/in/ian-lodge/) 是 AWS 的解决方案架构师，帮助 ISV 客户解决架构、运维和成本优化方面的挑战。工作之外，他喜欢与家人共度时光、打冰球和做木工。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/16/alex.jpg)[**Alex Pieri**](https://www.linkedin.com/in/alexander-pieri/) 是 AWS 的解决方案架构师，与零售客户合作规划、构建并优化其 AWS 云环境。他专精于帮助客户在 AWS 上构建企业级生成式 AI 方案。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/12/raj.jpeg)[**Raj Pathak**](https://www.linkedin.com/in/rajpathakaws/) 是首席解决方案架构师，也是加拿大与美国各地财富 50 强及中型 FSI（银行、保险、资本市场）客户的技术顾问。Raj 专精于机器学习在生成式 AI、自然语言处理、智能文档处理和 MLOps 中的应用。
