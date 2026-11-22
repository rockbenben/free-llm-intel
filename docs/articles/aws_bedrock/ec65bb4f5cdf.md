---
vendor: aws_bedrock
title: Accelerate benefits claims processing with Amazon Bedrock Data Automation
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/accelerate-benefits-claims-processing-with-amazon-bedrock-data-automation
date: 2025-09-25
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 0fc78206dda0
---

# 用 Amazon Bedrock Data Automation 加速福利理赔处理

在福利管理行业，理赔处理是至关重要的运营支柱，它确保员工和受益人及时获得健康、牙科或伤残等福利给付，同时控制成本并遵守 HIPAA 和 ERISA 等法规。企业希望优化整个工作流——涵盖理赔提交、校验、裁定、支付和申诉——以提升员工满意度、强化与医疗服务提供方的关系，并降低财务风险。该流程包含若干具体环节，例如理赔提交（通过门户或纸质材料）、数据校验（核实资格与准确性）、裁定（依据计划规则评估覆盖范围）、支付或拒付（包括用于报销的支票处理），以及申诉处理。高效的理赔处理有助于提供有竞争力的福利方案，这对人才保留和雇主品牌至关重要，但也需要在高度监管的环境中平衡速度、准确性和成本。

尽管理赔处理如此重要，许多组织在这一环节仍面临重大挑战。最突出的是对遗留系统和人工流程的依赖，导致解决时间慢得令人沮丧、错误率高、行政成本上升。提交信息不完整或不准确的理赔——例如缺少诊断码或资格不匹配——经常导致拒付和返工，让员工和医疗服务提供方都感到沮丧。此外，欺诈、浪费和滥用行为持续推高成本，而在不拖延合法理赔的前提下发现这些问题依然困难。复杂的监管要求需要系统不断更新，而系统之间（例如人力资源信息系统（HRIS）与其他下游系统）集成不佳严重限制了可扩展性。这些问题抬高了运营开支、侵蚀了人们对福利计划的信任，并让客户服务团队不堪重负，在申诉流程或理赔高峰期尤为明显。

生成式 AI 可以帮助应对这些挑战。借助 [Amazon Bedrock Data Automation](https://aws.amazon.com/bedrock/bda/)，你可以从文档、图像、音频和视频等非结构化多模态内容中自动生成有用的洞察。Amazon Bedrock Data Automation 可用于福利理赔流程，通过以业界领先的准确率从理赔包、保单申请和支持性文档中抽取并分类文档来自动化文档处理，减少人工错误并加快解决速度。Amazon Bedrock Data Automation 的自然语言处理能力可解读医疗服务提供方备注等非结构化数据，有助于符合计划规则和法规要求。通过自动化重复性任务并提供洞察，Amazon Bedrock Data Automation 帮助减轻行政负担、改善员工和医疗服务提供方的体验，并以经济高效的方式支持合规。此外，其可扩展的架构可与现有系统无缝集成，改善 HRIS、理赔系统和医疗服务提供方网络之间的数据流动，而高级分析有助于发现欺诈模式以优化成本控制。

在本文中，我们考察典型的福利理赔处理工作流，并识别生成式 AI 驱动的自动化能在哪些环节带来最大影响。

## 福利理赔处理

当员工或受益人自付了其健康福利覆盖范围内的费用时，他们会提交理赔申请以获取报销。该流程需要多份支持性文档，包括医生处方和付款凭证，付款凭证可能是支票影像、收据或电子支付确认。

理赔处理工作流包含几个关键步骤：

- **文档接收与处理**——系统接收并归类提交的文档，包括：病历与处方、付款凭证文档、支持性表单与资格核验
- **付款核验处理**——对于基于支票的报销，系统必须完成以下步骤：从支票影像中抽取信息，包括 MICR 行中包含的账号和路由号；将收款人名称和付款人名称与理赔提交过程中提供的信息进行核对；确认付款金额与申报费用一致；标记不一致之处交由人工复核
- **裁定与报销**——核验完成后，系统执行以下几项操作：依据计划规则和覆盖限额确定资格；计算相应的报销金额；通过直接存款或开具支票发起付款处理；就报销状态通知申请人

在本文中，我们通过一个真实场景来更清晰地呈现这一多步骤流程的复杂性。下面的示例演示 Amazon Bedrock Data Automation 如何简化从初次提交到最终报销的理赔处理工作流。

## 解决方案概览

设想这样一个场景：一位福利计划参与者去看病，并用支票自付了医生费用，随后又在药房购买了医生开具的药品。之后，他们登录福利提供方的门户，提交理赔申请，并附上支票影像和药品付款收据。

该解决方案使用 Amazon Bedrock Data Automation 来自动化该工作流中最关键、最耗时的两个方面：文档接收与付款核验处理。下面的架构图展示了福利理赔处理的架构。

![展示端到端流程的解决方案概览](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/15/image-1-13.png)

端到端流程通过四个相互衔接的阶段运作：摄取、抽取、校验和集成。

### 摄取

当受益人通过公司的福利理赔门户上传支持性文档（支票影像和药房收据）时，这些文档会被安全保存在一个 [Amazon Simple Storage Service](https://aws.amazon.com/s3)（Amazon S3）存储桶中，从而触发自动化的理赔处理 pipeline。

### 抽取

文档摄取完成后，系统立即开始智能数据抽取：

- S3 对象上传会触发一个 [AWS Lambda](https://aws.amazon.com/lambda) 函数，该函数调用 [Amazon Bedrock Data Automation 项目](https://docs.aws.amazon.com/bedrock/latest/userguide/bda-projects.html)。
- Amazon Bedrock Data Automation 使用 [blueprints](https://docs.aws.amazon.com/bedrock/latest/userguide/bda-blueprint-info.html) 进行文件处理和抽取。[Blueprints](https://docs.aws.amazon.com/bedrock/latest/userguide/bda-blueprint-info.html) 是一种工件（artifact），用于配置文件处理的业务逻辑：指定用于数据抽取的字段名列表，以及每个字段期望的数据格式（string、number 或 Boolean）和用于数据归一化的自然语言上下文与校验规则。Amazon Bedrock Data Automation 开箱即用地提供示例 blueprint 目录。你可以为目录中未预定义的独特文档类型[创建自定义 blueprint](https://docs.aws.amazon.com/bedrock/latest/userguide/bda-idp.html)。该解决方案针对不同的文档类型使用了两个 blueprint，如下面的截图所示：用于支票处理的目录 blueprint `US-Bank-Check`。用于药房专用收据的自定义 blueprint `benefit-claims-pharmacy-receipt-blueprint`。

![显示带两个 blueprint 的 Bedrock Data Automation 项目的图片](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/22/image-2-Bedrock-Data-Automation-Project-with-two-blueprints.png)

`US-Bank-Check` 是 Amazon Bedrock Data Automation 开箱即用提供的目录 blueprint。自定义 blueprint `benefit-claims-pharmacy-receipt-blueprint` 使用 [AWS CloudFormation](https://aws.amazon.com/cloudformation) 模板创建，用于处理药房收据，以覆盖标准 blueprint 目录中没有的特定文档类型。福利管理员希望为福利理赔处理查找厂商特定信息，例如名称、地址和电话详情。该自定义 blueprint 的 schema 包含这些字段的自然语言说明，例如 `VendorName`、`VendorAddress`、`VendorPhone` 以及其他字段，说明该字段代表什么、期望的数据类型，以及每个抽取字段的推断类型（在 [Creating Blueprints for Extraction](https://docs.aws.amazon.com/bedrock/latest/userguide/idp-cases-extraction.html) 中有说明），如下面的截图所示。

![显示 “benefit-claims-pharmacy-receipt-blueprint” 自定义 blueprint schema 的图片](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/16/image-3-13.png)

3. 这两个 blueprint 会被加入 Amazon Bedrock Data Automation 项目。Amazon Bedrock Data Automation 项目是标准 blueprint 与自定义 blueprint 的集合，你可以用它按特定配置设置处理不同类型的文件（如文档、音频和图像），并可控制希望从每种文件类型中抽取哪类信息。当项目被异步调用时，它会自动应用合适的 blueprint，抽取每个字段的置信度分数和边界框详情等信息，并把结果保存到另一个 S3 存储桶中。这种智能分类免去了你编写复杂文档分类逻辑的需要。

下面的截图展示了由标准目录 blueprint `US-Bank-Check` 完成的文档分类。

![由标准目录 blueprint “US-Bank-Check” 完成的文档分类](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/16/image-4-2.jpg)

下面的截图展示了由自定义 blueprint `benefit-claims-pharmacy-receipt-blueprint` 完成的文档分类。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/22/benefit-claims-pharmacy-receipt-blueprint.png)

### 校验

数据抽取完成后，系统进入校验与决策流程，使用针对每种文档类型的具体业务规则。

业务规则记录在标准操作规程文档中（[AnyCompany Benefit Checks Standard Operating procedure.docx](https://github.com/aws-samples/sample-accelerate-benefits-claims-processing-with-amazon-bedrock-data-automation/blob/main/assets/others/AnyCompany%20Benefit%20Checks%20Standard%20Operating%20procedure.docx) 和 [AnyCompany Benefit Claims Standard Operating procedure.docx](https://github.com/aws-samples/sample-accelerate-benefits-claims-processing-with-amazon-bedrock-data-automation/blob/main/assets/others/AnyCompany%20Benefit%20Claims%20Standard%20Operating%20procedure.docx)），并上传到 S3 存储桶。随后，系统以该 S3 存储桶为数据源创建一个 [knowledge base for Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-create.html)，如下面的截图所示。

![利用标准操作规程的 Amazon Bedrock Knowledge Bases](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/16/image-6-2-scaled.jpg)

当抽取出的 Amazon Bedrock Data Automation 结果被保存到配置的 S3 存储桶时，会自动触发一个 Lambda 函数。系统依据从知识库检索到的、针对特定文档类型的业务规则，以及 Amazon Bedrock Data Automation 的抽取输出，由一个 [Amazon Nova Lite](https://aws.amazon.com/ai/generative-ai/nova/) 大语言模型（LLM）对理赔做出自动的批准/拒付决定。

下面的截图展示了 `US-Bank-Check` 的福利理赔裁定自动决策。

![“US-Bank-Check” 的福利理赔裁定自动决策](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/16/image-7-3.png)

下面的截图展示了 `benefit-claims-pharmacy-receipt-blueprint` 的福利理赔裁定自动决策。

![“benefit-claims-pharmacy-receipt-blueprint” 的福利理赔裁定自动决策](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/22/Figure-8-Benefit-claim-adjudication-automated-decision-for-pharmacy-receipt.png)

### 集成

该系统可与现有业务流程无缝集成。

校验完成后，会向 [Amazon EventBridge](https://aws.amazon.com/eventbridge/) 推送一个事件，进而触发一个用于下游集成的 Lambda 函数。在此实现中，我们使用 [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) 表和 [Amazon Simple Notification Service](https://aws.amazon.com/pm/sns/)（Amazon SNS）电子邮件来完成下游集成。部署栈中会创建一个 DynamoDB 表，用于写入文档分类、抽取数据和自动决策等详情。在系统做出最终决定后，支票和收据两类场景都会发送电子邮件通知。下面的截图展示了一封药房收据批准邮件示例。

![显示自动批准决定的福利理赔结果邮件](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/15/image-9-1.jpeg)

这种灵活的架构帮助你通过内部 API 或事件与现有应用集成，在核验失败时更新理赔状态或触发额外的工作流。

## 通过智能业务规则管理减少人工投入

除了实现文档处理自动化，该解决方案还解决了一个常见的运营难题：传统上，客户必须编写并维护用于处理理赔裁定与处理相关业务规则的代码。每一次业务规则变更都需要开发工作和代码改动，拖慢上市速度并增加维护开销。

我们的方法使用 [Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/) 把业务规则和标准操作规程（SOP）转化为知识库，可用于自动化决策。这种方法在业务规则变更时可大幅缩短上市时间，因为更新可以通过知识管理完成，而不必部署代码。

在下面几节中，我们带你一步步把该解决方案部署到你自己的 AWS 账户。

## 前提条件

要实施本文提供的解决方案，你必须具备以下条件：

- 一个 [AWS 账户](https://signin.aws.amazon.com/signup?request_type=builderId)
- 在 Amazon Bedrock 中[启用](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access-modify.html)对 [Amazon Titan Text Embeddings V2](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html) 和 [Amazon Nova Lite](https://aws.amazon.com/ai/generative-ai/nova/) 基础模型（FM）的访问权限

该解决方案使用 Python 3.13 搭配 Boto3 1.38. 或更高版本，以及 [AWS Serverless Application Model Command Line Interface](https://aws.amazon.com/serverless/sam/)（AWS SAM CLI）1.138.0 版本。我们假定你已在本机安装好这些工具。如果尚未安装，请参考以下说明：

- [安装 Python 3.13](https://www.python.org/downloads/)
- [安装 AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)

## 在本地机器上准备代码

要准备代码，请克隆 [GitHub 仓库](https://github.com/aws-samples/sample-accelerate-benefits-claims-processing-with-amazon-bedrock-data-automation)。将仓库克隆到本地机器后，项目文件夹结构将如下面代码所示，与 README 文件中所述一致：

![显示 README.md 文件中所述的项目文件夹结构的图片](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/16/Image10-code-structure.png)

## 在你的账户中部署解决方案

示例代码附带一个 CloudFormation 模板，用于创建必要的资源。要在你的账户中部署该解决方案，请按 README 文件中的部署说明操作。

## 清理

在你的账户中部署该解决方案会产生费用。完成后请按照 README 文件中的清理说明操作，以免产生费用。

## 结论

福利管理公司可以通过使用本文所述解决方案实现理赔处理自动化，显著改善其运营。这一策略直接应对行业的核心挑战，并可带来以下几项关键优势：

- 通过加快理赔解决速度、降低人工错误率和提高直通处理率来提升处理效率，从而最大限度减少困扰遗留系统的恼人延迟和人工返工
- 简化文档集成并增强欺诈检测能力：借助新的 Amazon Bedrock Data Automation blueprint，新增支持性文档变得无缝；同时 AI 驱动的分析能够识别可疑模式而不拖延合法理赔，避免传统上长达数月的开发周期，并减少代价高昂的欺诈、浪费和滥用
- 敏捷的业务规则管理，能够快速适应不断变化的 HIPAA 和 ERISA 要求并修改业务规则，显著降低行政成本和上市时间，同时提升可扩展性及与现有 HRIS 和理赔系统的集成，最终提升员工满意度、强化与医疗服务提供方的关系，并支撑有竞争力的福利方案——这对人才保留和雇主品牌至关重要

要开始使用该解决方案，请参阅 [GitHub 仓库](https://github.com/aws-samples/sample-accelerate-benefits-claims-processing-with-amazon-bedrock-data-automation)。有关 Amazon Bedrock Data Automation 的更多信息，请参阅[使用 Amazon Bedrock Data Automation 把非结构化数据转化为有价值的洞察](https://docs.aws.amazon.com/bedrock/latest/userguide/bda.html)，并试用[使用 Amazon Bedrock Data Automation 进行文档处理的 workshop](https://catalog.us-east-1.prod.workshops.aws/workshops/c64e3606-ab68-4521-81ea-b2eb36c993b9/en-US)。

### 关于作者

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/16/saurabks-phonetool-pic-100x133.jpeg)**Saurabh Kumar** 是 AWS 的资深解决方案架构师，常驻北卡罗来纳州罗利，专长于韧性工程、混沌工程和生成式 AI 解决方案。他为客户提供容错策略和生成式 AI 驱动的现代化方法方面的建议，帮助组织在利用生成式 AI 技术推动创新的同时构建稳健的架构。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/16/image-26-100x100.png)Kiran Lakkireddy** 是 AWS 的首席解决方案架构师，专长于金融服务、福利管理和人力资源服务行业。Kiran 为客户在业务转型中提供技术与架构指导，尤其专注于 GenAI 安全、合规与治理。他经常就 GenAI 安全、合规和治理主题向客户的安全领导层分享见解，帮助组织在应对 AI 实施复杂局面的同时保持稳健的安全标准。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/16/tamil-pic-100x133.jpeg)**Tamilmanam Sambasivam** 是 AWS 的解决方案架构师兼 AI/ML 专家。她通过推荐合适的 AWS 解决方案，帮助企业客户解决业务问题。她在信息技术领域拥有深厚背景（24 年以上经验），帮助客户在 AWS 云上规划、开发和现代化其业务问题。业余时间，Tamil 喜欢旅行和园艺。
