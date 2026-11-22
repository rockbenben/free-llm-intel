---
vendor: aws_bedrock
title: Build an intelligent photo search using Amazon Rekognition, Amazon Neptune, and Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-an-intelligent-photo-search-using-amazon-rekognition-amazon-neptune-and-amazon-bedrock
date: 2026-02-24
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 06357474b073
---

# 使用 Amazon Rekognition、Amazon Neptune 和 Amazon Bedrock 构建智能照片搜索

管理庞大的照片集对组织和个人都是重大挑战。传统方法依赖手动打标签、基础元数据和基于文件夹的组织方式，当面对成千上万张包含多个人物和复杂关系的图像时，这些做法会变得不切实际。智能照片搜索系统通过结合计算机视觉、图数据库和自然语言处理来应对这些挑战，改变我们发现与组织视觉内容的方式。这类系统不仅捕捉照片中出现了谁和什么，还捕捉赋予其意义的复杂关系与上下文，从而实现自然语言查询和语义发现。

在本文中，我们展示如何使用 [AWS Cloud Development Kit](https://aws.amazon.com/cdk/)（AWS CDK）构建一个完整的照片搜索系统，它集成了用于人脸与物体检测的 [Amazon Rekognition](https://aws.amazon.com/rekognition/)、用于关系映射的 [Amazon Neptune](https://aws.amazon.com/neptune/)，以及用于 AI 驱动图像说明（captioning）的 [Amazon Bedrock](https://aws.amazon.com/bedrock/)。我们会演示这些服务如何协同工作，构建出一个能理解自然语言查询的系统，例如“找出所有祖父母与孙辈在生日派对上的照片”，或“给我看公路旅行中家庭用车的照片”。

关键优势在于：能够把搜索焦点个性化、定制到特定人物、物体或关系上，同时扩展到处理数千张照片和复杂的家庭或组织结构。我们的方案表明，把 Amazon Neptune 的图数据库能力与 Amazon AI 服务集成，可以实现理解上下文与关系的自然语言照片搜索，从简单的元数据打标签迈向智能的照片发现。我们通过一个完整的 serverless 实现来展示这一点，你可以部署它并针对自己的用例进行定制。

## 方案概览

本节概述我们智能照片搜索系统的技术架构与工作流。如下图所示，该方案使用 serverless AWS 服务构建一个可扩展、高性价比的系统，能够自动处理照片并支持自然语言搜索。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/02/13/p1.png)

这种 serverless 架构能高效扩展到多种用例：

- **企业** – 员工表彰与活动记录
- **医疗** – 符合 HIPAA 的照片管理与关系跟踪
- **教育** – 跨院系的学生与教职工照片组织
- **活动** – 带自动打标与客户交付的专业摄影

该架构组合了多项 AWS 服务，构成一个具备上下文感知能力的照片搜索系统：

- [Amazon API Gateway](https://aws.amazon.com/api-gateway) 用于 REST API 端点与 Web 界面集成
- [Amazon Bedrock](https://aws.amazon.com/bedrock/) 配合 Anthropic 的 Claude 3.5 Sonnet，用于 AI 驱动的上下文图像说明
- [Amazon DynamoDB](https://aws.amazon.com/dynamodb) 用于快速的元数据存储与检索
- [AWS Lambda](https://aws.amazon.com/lambda/) 用于跨方案组件的 serverless 计算编排
- [Amazon Neptune](https://aws.amazon.com/neptune/) 用于以图数据库存储复杂关系
- [Amazon Rekognition](https://aws.amazon.com/rekognition/) 用于人脸检测、识别与物体标注
- [Amazon Simple Storage Service](https://aws.amazon.com/s3/)（Amazon S3）用于可扩展的照片存储，并触发处理工作流

系统遵循一条精简的工作流：

- 图像被上传到 S3 桶，并自动触发 Lambda。
- faces/ 前缀下的参考照片会被处理，以构建识别模型。
- 新照片触发 Amazon Rekognition 进行人脸检测和物体标注。
- Neptune 存储人物、物体与上下文之间的连接。
- Amazon Bedrock 利用检测到的人脸与关系生成带上下文的描述。
- DynamoDB 存储可搜索的元数据，并提供快速检索能力。
- 自然语言查询会遍历 Neptune 图，以获得智能结果。

完整源代码可在 [GitHub](https://github.com/aws-samples/sample-serverless-image-captioning-neptune) 上获取。

## 前提条件

在实施本方案之前，请确保具备以下条件：

- 一个对 Amazon S3、Lambda、Amazon Rekognition、Neptune、Amazon Bedrock 和 DynamoDB 具备相应权限的 AWS 账户
- 已配置编程访问的 [AWS Command Line Interface](https://aws.amazon.com/cli)（AWS CLI）[v2.15.0 或更高版本](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- 已安装 [AWS CDK v2.92.0 或更高版本](https://docs.aws.amazon.com/cdk/v2/guide/getting-started.html)（`npm install -g aws-cdk`）
- [Python 3.11 或更高版本](https://www.python.org/downloads/) 及 pip 包管理器
- [Node.js 18.x 或更高版本](https://nodejs.org/en/download)，用于 AWS CDK 操作
- 具备 serverless 架构与图数据库的基础知识
- 在你的 AWS Region 中拥有对 Amazon Bedrock 上 Anthropic Claude 3.5 Sonnet 的访问权限

## 部署方案

从 [GitHub 仓库](https://github.com/aws-samples/sample-serverless-image-captioning-neptune) 下载完整源代码。更详细的安装与部署说明见 README。

该项目按关注点分离并支持模块化开发的原则，组织为若干关键目录：

```
smart-photo-caption-and-search/
├── lambda/                          
│   ├── face_indexer.py              # Indexes reference faces in Rekognition
│   ├── faces_handler.py             # Lists indexed faces via API
│   ├── image_processor.py           # Main processing pipeline
│   ├── search_handler.py            # Handles search queries
│   ├── style_caption.py             # Generates styled captions
│   ├── relationships_handler_neptune.py # Manages Neptune relationships
│   ├── label_relationships.py       # Queries label hierarchies
│   └── neptune_search.py            # Neptune relationship parsing
├── lambda_layer/                    # Pillow image processing layer
├── neptune_layer/                   # Gremlin Python Neptune layer
├── ui/
│   └── demo.html                    # Web interface with Cognito authentication
├── app.py                           # CDK application entry point
├── image_name_cap_stack_neptune.py  # Neptune-enabled CDK stack
└── requirements_neptune.txt         # Python dependencies
```

该方案使用以下关键 Lambda 函数：

- **image_processor.py** – 核心处理，包含人脸识别、标签检测与关系增强的说明生成
- **search_handler.py** – 自然语言查询处理，支持多步关系遍历
- **relationships_handler_neptune.py** – 配置驱动的关系管理与图连接
- **label_relationships.py** – 层级标签查询、物体—人物关联与语义发现

要部署该方案，请完成以下步骤：

- 运行以下命令安装依赖：

`pip install -r requirements_neptune.txt`

- 首次设置时，运行以下命令引导 AWS CDK：

`cdk bootstrap`

- 运行以下命令预置 AWS 资源：

`cdk deploy`

- 在 Web UI 中设置 [Amazon Cognito](https://aws.amazon.com/cognito/) 用户池凭证。
- 上传参考照片以建立识别基线。
- 通过 API 或 Web UI 创建示例家庭关系。

系统通过 serverless pipeline 自动处理人脸识别、标签检测、关系解析和 AI 说明生成，从而支持由 Neptune 图遍历驱动的自然语言查询，例如“某人的母亲与汽车”。

## 主要功能与用例

本节讨论该方案的主要功能与用例。

### 自动化人脸识别与打标

借助 Amazon Rekognition，你可以从参考照片自动识别个人，无需手动打标。为每个人上传几张清晰图像，系统就能在整个照片集中识别他们，不受光照或角度影响。这种自动化把打标时间从数周缩短到数小时，可支持企业通讯录、合规档案和活动管理工作流。

### 支持关系感知的搜索

通过使用 Neptune，该方案能理解照片中出现了谁，以及他们之间如何关联。你可以运行诸如“Sarah 的经理”或“妈妈和她的孩子们”这样的自然语言查询，系统会遍历多跳关系来返回相关图像。这种语义搜索用直观、上下文感知的发现取代了手动文件夹整理。

### 自动理解物体与上下文

Amazon Rekognition 检测物体、场景与活动，Neptune 再把它们与人物和关系关联起来。这使“与公司车辆同行的高管”或“教室里的老师”这类复杂查询成为可能。标签层级会动态生成，并能适配不同领域——例如医疗或教育——无需手动配置。

### 用 Amazon Bedrock 生成上下文感知的说明

借助 Amazon Bedrock，系统会生成有意义、感知关系的说明，例如“Sarah 和她的经理讨论季度业绩”，而不是泛泛的描述。说明可以针对语气进行调校（例如合规场景用客观语气、营销场景用叙事语气、高管摘要用简洁语气），从而同时提升可搜索性与沟通效果。

### 提供直观的 Web 体验

借助 Web UI，用户可以用自然语言搜索照片、查看 AI 生成的说明，并动态调整语气。例如“与孩子们在一起的母亲”或“户外活动”这类查询会立即返回带说明的相关结果。这种统一的体验同时支持企业工作流和个人照片集。

下面的截图演示了使用 Web UI 进行智能照片搜索与说明风格调校。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/02/13/p2.png)

### 用标签层级扩展图关系

Neptune 可以扩展以建模跨组织或数据集成千上万的关系与标签层级。关系在图像处理期间自动生成，从而实现快速的语义发现，并在数据增长时保持性能与灵活性。

下图展示了一个示例人物关系图（配置驱动）。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/02/13/p3.png)

人物关系是通过传给 `initialize_relationship_data()` 函数的 JSON 数据结构来配置的。这种配置驱动的方式无需修改代码就能支持无限多的用例——你只需在配置对象中定义自己的人物和关系。

下图展示了一个示例标签层级图（由 Amazon Rekognition 自动生成）。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/02/13/p4.png)

标签层级与共现模式在图像处理期间自动生成。Amazon Rekognition 提供类别分类，用来创建 `belongs_to` 关系；而 `appears_with` 与 `co_occurs_with` 关系则在处理图像时动态建立。

下面的截图展示了完整图的一个子集，演示了多层关系类型。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/02/13/p5.png)

## 数据库生成方式

关系图通过 `initialize_relationship_data()` 函数采用灵活的配置驱动方式。这减少了对硬编码的需要，并支持无限多的用例：

```
# Generic configuration structure
config = {
    "people": [
        {"name": "alice", "gender": "woman", "role": "mother"},
        {"name": "jane", "gender": "girl", "role": "daughter"}
    ],
    "relationships": [
        {"from": "alice", "to": "jane", "type": "parent_of", "subtype": "mother_of"},
        {"from": "jane", "to": "david", "type": "sibling_of", "bidirectional": True}
    ]
}

# Generic relationship creation
for rel in relationships_data:
    g.V().has('name', rel["from"]).addE(rel["type"]).to(
        __.V().has('name', rel["to"])
    ).property('type', rel["subtype"]).next()
# Business example - just change the configuration
business_config = {
    "people": [{"name": "sarah", "role": "manager"}],
    "relationships": [{"from": "sarah", "to": "john", "type": "manages", "subtype": "manager_of"}]
}
```

标签关系数据库在图像处理期间通过 `store_labels_in_neptune()` 函数自动创建：

```
# Rekognition provides labels with categories
response = rekognition.detect_labels(
    Image={'Bytes': image_bytes},
    MaxLabels=20,
    MinConfidence=70
)

# Extract labels and categories
for label in response.get('Labels', []):
    label_data = {
        'name': label['Name'],  # e.g., "Car"
        'categories': [cat['Name'] for cat in label.get('Categories', [])]  # e.g., ["Vehicle", "Transportation"]
    }
# Automatic hierarchy creation in Neptune
for category in categories:
    # Create belongs_to relationship (Car -> Vehicle -> Transportation)
    g.V().has('name', label_name).addE('belongs_to').to(
        __.V().has('name', category_name)
    ).property('type', 'hierarchy').next()
    
    # Create appears_with relationship (Person -> Car)
    g.V().has('name', person_name).addE('appears_with').to(
        __.V().has('name', label_name)
    ).property('confidence', confidence).next()
```

借助这些函数，你可以管理包含复杂关系查询的大型照片集、按语义上下文发现照片，并通过标签共现模式找到主题合集。

## 性能与可扩展性考量

请考虑以下性能与可扩展性因素：

- **处理批量上传 **– 系统能高效处理从家庭小相册到拥有数千张图像的企业档案等大型照片集。内置的智能机制会管理 API 速率限制，即使在高峰上传时段也能保证可靠处理。
- **成本优化 **– serverless 架构确保你只为实际用量付费，对小型团队和大型企业都具成本效益。作为参考，处理 1,000 张图像通常花费约 $15–25（包括 Amazon Rekognition 人脸检测、Amazon Bedrock 说明生成与 Lambda 函数执行），而 Neptune 集群成本为每月 $100–150，与数据量无关。在 Amazon S3 中，存储成本保持在每 1,000 张图像低于 $1 的极低水平。
- **扩展性能 **– Neptune 图数据库方式能从小型家庭结构高效扩展到拥有数千人的企业级网络。系统对关系查询保持快速响应时间，并通过自动重试逻辑与进度跟踪支持大型照片集的批量处理。

## 安全与隐私

该方案实施全面的安全措施来保护敏感的图像与人脸识别数据。系统使用 [AWS Key Management Service](https://aws.amazon.com/kms)（AWS KMS）管理的密钥，以 AES-256 加密对静态数据进行加密，并用 TLS 1.2 或更高版本保护传输中的数据。Neptune 与 Lambda 函数运行在 virtual private cloud（VPC）子网内，与直接互联网访问隔离，API Gateway 提供唯一的公共端点，并配有 CORS 策略与速率限制。访问控制遵循最小权限原则，[AWS Identity and Access Management](https://aws.amazon.com/iam/)（IAM）策略只授予所需的最低权限：Lambda 函数只能访问特定的 S3 桶和 DynamoDB 表，对 Neptune 的访问被限制在授权的数据库操作上。图像与人脸识别数据保留在你的 AWS 账户内，绝不会被共享到 AWS 服务之外。你可以配置 Amazon S3 生命周期策略来自动管理数据保留，[AWS CloudTrail](https://aws.amazon.com/cloudtrail) 提供完整的数据访问与 API 调用审计日志以支持合规监控，并通过额外的 [Amazon GuardDuty](https://aws.amazon.com/guardduty/) 威胁检测监控来满足 GDPR 与 HIPAA 要求。

## 清理

为避免将来产生费用，请完成以下步骤删除你创建的资源：

- 从 S3 桶中删除图像：

`aws s3 rm s3://YOUR_BUCKET_NAME –recursive`

- 删除 Neptune 集群（该命令还会自动删除 Lambda 函数）：

`cdk destroy`

- 删除 Amazon Rekognition 人脸集合：

`aws rekognition delete-collection --collection-id face-collection`

## 结论

该方案展示了 Amazon Rekognition、Amazon Neptune 与 Amazon Bedrock 如何协同工作，实现同时理解视觉内容与上下文的智能照片搜索。它构建在完全 serverless 的架构之上，结合计算机视觉、图建模与自然语言理解，交付可扩展、类人的发现体验。通过把照片集转变为由人物、物体与时刻构成的知识图谱，它重新定义了用户与视觉数据的交互方式——让搜索更具语义、更讲关系、也更有意义。最终，它体现了 AWS AI 与图技术在实现安全、上下文感知的照片理解方面的可靠与可信。

如需了解更多，请参阅以下资源：

- [AWS CDK 文档](https://docs.aws.amazon.com/cdk/)
- [Amazon Rekognition 开发人员指南](https://docs.aws.amazon.com/rekognition/latest/dg/what-is.html)
- [Amazon Neptune 用户指南](https://docs.aws.amazon.com/neptune/latest/userguide/intro.html)
- [Amazon Bedrock 用户指南](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)

### 关于作者
