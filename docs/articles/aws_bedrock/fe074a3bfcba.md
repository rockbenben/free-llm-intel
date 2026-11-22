---
vendor: aws_bedrock
title: Detect and redact personally identifiable information using Amazon Bedrock Data Automation and Guardrails
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/detect-and-redact-personally-identifiable-information-using-amazon-bedrock-data-automation-and-guardrails
date: 2026-01-08
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: d0a2ee1204b8
---

# 使用 Amazon Bedrock Data Automation 和 Guardrails 检测并遮盖个人可识别信息

组织通过各种通信渠道处理海量的敏感客户信息。保护个人可识别信息（Personally Identifiable Information，PII）——例如社会安全号码（SSN）、驾照号码和电话号码——对于满足数据隐私法规的合规要求以及建立客户信任正变得日益关键。然而，人工审阅并遮盖 PII 既耗时又容易出错，而且随着数据量增长，很难扩展。

组织在处理散落于不同内容类型（从文本到图像）中的 PII 时面临挑战。传统方法往往需要为文本内容和图像内容分别准备工具与工作流，导致遮盖做法不一致，并留下潜在的安全缺口。这种割裂的做法不仅增加了运维开销，也提高了 PII 意外暴露的风险。

本文以一个处理大量来信及其附件中文本与图像内容的用例，展示了一套使用 [Amazon Bedrock Data Automation](https://aws.amazon.com/bedrock/bda/) 和 [Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/) 的自动化 PII 检测与遮盖方案。该方案提供完整的电子邮件处理工作流，并配有基于 React 的用户界面，让获授权人员可以更安全地管理和审阅已遮盖的邮件通信与附件。我们逐步讲解了用于部署该方案的实施步骤。最后，我们讨论了该方案的收益，包括运营效率、可扩展性、安全与合规性以及适应性。

## 方案概览

该方案通过三项主要能力，为保护商业通信中的敏感信息提供了一套自动化系统：

- **自动化 PII 检测与遮盖**：对邮件正文和附件都使用 Amazon Bedrock Data Automation 与 Guardrails，确保敏感数据在不同内容类型之间得到一致的保护。
- **更安全的数据管理工作流**：处理过的通信经过加密，并在适当的访问控制下存储，同时保留完整的操作审计轨迹。
- **基于 Web 的界面选项**：让获授权的坐席高效管理已遮盖的通信，并由邮件自动分类和可自定义的文件夹管理等特性提供支持。

这种统一的做法帮助组织在满足数据隐私要求的同时精简其通信工作流。

下图概述了该方案的架构。 ![使用 Amazon Bedrock 进行 PII 检测与遮盖的方案架构](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/23/ML-184361.png)

该图展示了后端的 PII 检测与遮盖工作流，以及由 [AWS Lambda](https://aws.amazon.com/lambda/) 和 [Amazon EventBridge](https://aws.amazon.com/eventbridge/) 编排的前端应用用户界面。整个过程按以下步骤进行：

- 工作流从用户向托管在 [Amazon Simple Email Service (Amazon SES)](https://aws.amazon.com/ses/) 上的来信服务器发送电子邮件开始。这一步是可选的。
- 或者，用户也可以把电子邮件和附件直接上传到 [Amazon Simple Storage Service (S3)](https://aws.amazon.com/s3/) 落地存储桶。
- S3 事件通知会触发负责初始处理的 AWS Lambda 函数，该函数生成唯一的案例 ID，并在 [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) 中创建一条跟踪记录。
- Lambda 负责编排 PII 检测与遮盖工作流：从电子邮件中提取邮件正文和附件并保存到原始邮件存储桶，随后调用 Amazon Bedrock Data Automation 与 Guardrails 来检测和遮盖 PII。
- Amazon Bedrock Data Automation 处理附件，从文件中提取文本。
- Amazon Bedrock Guardrails 从邮件正文和附件文本中检测并遮盖 PII，并把遮盖后的内容存储到另一个 S3 存储桶。
- DynamoDB 表会更新电子邮件消息、文件夹元数据和电子邮件筛选规则。
- 使用 Amazon EventBridge Scheduler 按计划运行 Rules Engine Lambda，依据已启用的电子邮件筛选规则条件，处理尚未归类到文件夹的新邮件。
- Rules Engine Lambda 还会与 DynamoDB 通信，访问消息表和规则表。
- 用户可以通过 [Amazon API Gateway](https://aws.amazon.com/api-gateway/) 访问可选的应用程序用户界面，它负责管理用户 API 请求，并把渲染用户界面的请求路由到 S3 静态托管。用户可以根据自身的安全要求选择为用户界面启用身份验证。或者，用户也可以查看 DynamoDB 表和存放已遮盖 PII 内容的 S3 存储桶，了解其电子邮件的处理状态。
- Portal API Lambda 根据用户请求获取案例详情。
- 由 API Gateway 提供服务的静态资源存放在私有 S3 存储桶中。
- 可选地，用户可以启用 [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/) 和 [AWS CloudTrail](https://aws.amazon.com/cloudtrail/) 来提升 PII 检测与遮盖过程的可见性，同时使用 [Amazon Simple Notification Service](https://aws.amazon.com/sns/) 为任何失败发送实时告警，便于及时处理问题。

在接下来的各节中，我们将逐步介绍实施该方案的过程。

## 操作演练

该方案的实施包括基础设施配置和可选的门户配置。

### **先决条件**

在开始实施之前，请确保已安装并配置以下组件。

- 一个 [AWS 账户](https://signin.aws.amazon.com/signup?request_type=builderId)
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Python 3.7](https://www.python.org/downloads/release/python-370/) 或更高版本
- [Node v18](https://nodejs.org/en/blog/release/v18.12.0) 或更高版本
- [NPM v9.8](https://www.npmjs.com/package/npm/v/9.8.0) 或更高版本
- [AWS CDK v2.166](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html) 或更高版本
- 终端/CLI，例如 macOS Terminal、PowerShell 或 Windows Terminal，或 Linux 命令行。当所有代码都位于同一个 AWS 账户内时，也可以使用 [AWS CloudShell](https://aws.amazon.com/cloudshell/)

### 基础设施配置与部署流程

请确认你的 AWS 账户中已创建一个现有 [virtual private cloud VPC](https://docs.aws.amazon.com/vpc/latest/userguide/create-vpc.html)，其中包含三个无互联网访问的私有子网。所有 [AWS CloudFormation](https://aws.amazon.com/cloudformation/) 堆栈都需要部署在同一个 AWS 账户内。

#### CloudFormation 堆栈

该方案包含三个堆栈（两个必需、一个可选），它们会部署到你的 AWS 账户中：

- **S3Stack** – 预置核心基础设施，包括用于存放原始和已遮盖电子邮件的 S3 存储桶（带自动生命周期策略）、用于跟踪电子邮件元数据的 DynamoDB 表（带生存时间 TTL 和全局二级索引），以及用于更安全地访问 Lambda 函数的 VPC 安全组。它还创建对 S3、DynamoDB 和 Bedrock 服务拥有完整权限的 [Amazon Identity and Access Management (IAM)](https://aws.amazon.com/iam/) 角色，为整个 PII 检测与遮盖工作流奠定更安全的基础。
- **ConsumerStack **– 预置核心处理基础设施，包括用于文档文本提取的 Amazon Bedrock Data Automation 项目、配置为对各类 PII 实体进行匿名化的 Bedrock Guardrails，以及用于处理电子邮件和附件的 Lambda 函数，并配有用于成功/失败通知的 [Amazon Simple Notification Service (SNS)](https://aws.amazon.com/sns/) 主题。在配置了域的情况下，它还会创建用于处理来信的 [Amazon Simple Email Service (SES)](https://aws.amazon.com/ses/) 接收规则，以及用于自动触发电子邮件处理工作流的 S3 事件通知。
- **PortalStack（可选）** – 仅在用户希望使用基于 Web 的用户界面管理电子邮件时才需要。它预置可选的 Web 界面，包括区域级 API Gateway、用于存储已遮盖消息的 DynamoDB 表和用于静态 Web 资源的 S3 存储桶。

#### Amazon SES（可选）

如果不使用 Amazon SES，请直接跳到后面“方案部署”一节。

以下 Amazon SES 配置是可选的。不进行此项配置同样可以测试代码。无论是否使用 Amazon SES，测试该应用程序的步骤都涵盖在“测试”一节中。

在开启生产环境访问权限的情况下配置 Amazon SES，并验证该方案要使用的域/电子邮件身份。我们还需要在维护该域的 DNS 服务商处添加 MX 记录。请参考以下链接：

- [申请 SES 生产环境访问权限](https://docs.aws.amazon.com/ses/latest/dg/request-production-access.html)
- [配置 Amazon SES 电子邮件接收](https://docs.aws.amazon.com/ses/latest/dg/receiving-email-setting-up.html)

为 SMTP 创建凭证，并保存到名为 SmtpCredentials 的 [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/) 密钥中。此过程会创建一个 IAM 用户。

如果该密钥使用了其他名称，请用所创建密钥的名称更新 `context.json` 中的 `secret_name` 行。

在 AWS Secrets Manager 中存储该密钥时，用户名的键应为 `smtp_username`，密码的键应为 `smtp_password`。

- [获取 Amazon SES SMTP 凭证](https://docs.aws.amazon.com/ses/latest/dg/smtp-credentials.html)

### 方案部署

在终端/CLI 环境中运行以下命令。

- 克隆代码仓库  `git clone https://github.com/aws-samples/sample-bda-redaction.git`
- `infra/cdk.json` 文件告诉 CDK Toolkit 如何执行你的应用  `cd sample-bda-redaction/infra/`
- **可选：** 创建并激活一个新的 Python 虚拟环境（请务必使用 python 3.12，因为 CDK 中的 lambda 也是按该版本配置的。如果使用其他 python 版本，请更新 CDK 代码，使其在 lambda 运行时中反映相同版本）  `python3 -m venv .venv . .venv/bin/activate`
- 升级 pip  `pip install --upgrade pip`
- 安装 Python 包  `pip install -r requirements.txt`
- 创建 `context.json` 文件  `cp context.json.example context.json`
- 用该环境的正确配置选项更新 `context.json` 文件。

| **属性名称** | **默认值** | **描述** | **创建时机** |
| --- | --- | --- | --- |
| `vpc_id` | “” | 部署资源的 VPC ID | 需要在执行前创建 VPC |
| `raw_bucket` | “” | 存储原始消息和附件的 S3 存储桶 | 在 CDK 部署期间创建 |
| `redacted_bucket_name` | “” | 存储已遮盖消息和附件的 S3 存储桶 | 在 CDK 部署期间创建 |
| `inventory_table_name` | “” | 存储已遮盖消息详情的 DynamoDB 表名 | 在 CDK 部署期间创建 |
| `resource_name_prefix` | “” | 创建堆栈期间为资源命名所使用的前缀 | 在堆栈创建期间 |
| `retention` | 90 | 已遮盖和原始 S3 存储桶中消息的保留天数 | 在堆栈创建期间 |

- 以下属性仅在预置门户时才需要。

| **属性名称** | **默认值** | **描述** |
| --- | --- | --- |
| `environment` | development | 预置资源所在的环境类型。取值为 development 或 production |

- 需要使用 Amazon SES 管理已遮盖电子邮件消息的用例，需要设置以下配置变量。否则这些是可选的。

| **属性名称** | **描述** | **备注** |
| --- | --- | --- |
| `domain` | 用于 Amazon SES 的已验证域或电子邮件名称 | 如果未配置 Amazon SES，可以留空 |
| `auto_reply_from_email` | 电子邮件消息“from”字段的邮箱地址。同时用作从 Portal 应用程序转发电子邮件的地址 | 如果未配置 Portal，可以留空 |
| `secret_name` | 包含 SMTP 凭证的 AWS Secrets Manager 密钥，用于从门户转发电子邮件的功能 |  |

- 在 infra 目录的根目录下运行以下命令来部署基础设施。  引导 AWS 账户以使用 AWS CDK  `cdk bootstrap`  现在用户可以为此代码合成 CloudFormation 模板。在 cdk synth 前后附加环境变量可抑制警告。首次部署大约需要 10 分钟才能完成。  `JSII_DEPRECATED=quiet JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=quiet cdk synth --no-notices`  将 `<<resource_name_prefix>>` 替换为所选的值，然后运行：  `JSII_DEPRECATED=quiet JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=quiet cdk deploy <<resource_name_prefix>>-S3Stack <<resource_name_prefix>>-ConsumerStack --no-notices`

### 测试

- **在有 Amazon SES 的情况下测试应用程序 **

在开始测试之前，请确认由 `<<resource_name_prefix>>-ConsumerStack` 堆栈创建的 Amazon SES 电子邮件接收规则集处于活动状态。我们可以执行下面的命令来检查，并确认输出中的名称为 `<<resource_name_prefix>>-rule-setaws ses describe-active-receipt-rule-set`。如果名称不匹配或输出为空，请执行以下命令将其激活：

```
# Replace <<resource_name_prefix>> with resource_name_prefix used in context.json

aws ses set-active-receipt-rule-set --rule-set-name <<resource_name_prefix>>-rule-set
```

确认正确的规则集处于活动状态后，我们就可以通过向 Amazon SES 中已验证的电子邮件或域发送邮件来测试该应用程序，这会自动触发遮盖流水线。进度可以在 DynamoDB 表 `<<inventory_table_name>>` 中跟踪。该清单表名称可以在 AWS CloudFormation 控制台中 `<<resource_name_prefix>>-S3Stack` 堆栈的资源选项卡上找到，其逻辑 ID 为 `EmailInventoryTable`。每封被处理的邮件都会生成一个唯一的 `<<case_id>>`，并在 DynamoDB 清单表中使用。遮盖完成后，遮盖后的邮件正文可以在 `<<redacted_bucket_name>>/redacted/<<today_date>>/<<case_id>>/email_body/` 中找到，遮盖后的附件可以在 `<<redacted_bucket_name>>/redacted/<<today_date>>/<<case_id>>/attachments/` 中找到。

- **在没有 Amazon SES 的情况下测试应用程序**

如前所述，该方案用于遮盖邮件正文和附件中的任何 PII 数据。因此，要测试该应用程序，我们需要提供一个需要被遮盖的电子邮件文件。我们可以不借助 Amazon SES，直接把电子邮件文件上传到原始 S3 存储桶来完成这件事。原始存储桶的名称可以在 AWS CloudFormation 控制台中 `<<resource_name_prefix>>-S3Stack` 堆栈的输出选项卡上找到，其导出名称为 `RawBucket`。这会通过 S3 事件通知触发 Lambda，从而启动遮盖邮件正文和附件的工作流。为方便你使用，代码仓库的 `infra/pii_redaction/sample_email` 目录中提供了一个示例电子邮件。以下是使用同一个电子邮件文件、在不借助 Amazon SES 的情况下测试该应用程序的步骤。

```
# Replace <<raw_bucket>> with raw bucket name created during deployment

aws s3 cp pii_redaction/sample_email/ccvod0ot9mu6s67t0ce81f8m2fp5d2722a7hq8o1 s3://<<raw_bucket>>/domain_emails/
```

上述操作会触发电子邮件内容的遮盖流程。你可以在 DynamoDB 表 `<<inventory_table_name>>` 中跟踪进度。每封被处理的邮件都会生成一个唯一的 `<<case_id>>`，并在 DynamoDB 清单表中使用。该清单表名称可以在 AWS CloudFormation 控制台中 `<<resource_name_prefix>>-S3Stack` 堆栈的资源选项卡上找到，其逻辑 ID 为 `EmailInventoryTable`。遮盖完成后，遮盖后的邮件正文可以在 `<<redacted_bucket_name>>/redacted/<<today_date>>/<<case_id>>/email_body/` 中找到，遮盖后的附件可以在 `<<redacted_bucket_name>>/redacted/<<today_date>>/<<case_id>>/attachments/` 中找到。

### 门户配置

门户的安装完全是可选的。这一节可以跳过；只需查看部署该方案的 AWS 账户控制台，即可看到所创建的资源。门户作为一个 Web 界面，用于管理由后端 AWS 基础设施处理过的、已遮盖 PII 的电子邮件，让用户可以查看已净化的邮件内容。门户可以用于：

- 列出消息：查看已处理且内容已遮盖的电子邮件
- 消息详情：查看单封电子邮件的内容与附件

门户先决条件：该门户需要安装以下软件工具：

- [TypeScript](https://www.typescriptlang.org/download/)
- [Node v18](https://nodejs.org/en/blog/release/v18.12.0) 或更高版本
- [NPM v9.8](https://www.npmjs.com/package/npm/v/9.8.0) 或更高版本

#### 基础设施部署

- 进入该方案的目录根，为此代码合成 CloudFormation 模板。现在运行以下命令：  `cd sample-bda-redaction/infra/`
- 可选：创建并激活一个新的 Python 虚拟环境（如果此前尚未创建该虚拟环境）：  `python3 -m venv .venv. .venv/bin/activatepip install -r requirements.txt`
- 现在用户可以为此代码合成 CloudFormation 模板。  `JSII_DEPRECATED=quiet JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=quiet cdk synth --no-notices`
- 部署基于 React 的门户。将 `<<resource_name_prefix>>` 替换为所选的值：  `JSII_DEPRECATED=quiet JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=quiet cdk deploy <<resource_name_prefix>>-PortalStack --no-notices`

首次部署大约需要 10 分钟才能完成。

#### 环境变量

- 进入 app 目录的根目录创建新的环境文件，并使用以下命令在终端/CLI 环境中创建 `.env` 文件，在其中更新以下变量（把 `.env.example` 文件复制为 `.env`）。  `cp .env.example .env`
- 也可以使用你惯用的文本编辑器创建该文件。

| **环境变量名称** | **默认值** | **描述** | **是否必需** |
| --- | --- | --- | --- |
| `VITE_APIGW` | “” | API Gateway invoke URL 的 URL（含协议）但不含路径（从值中移除 /portal）。该值可以在通过 AWS CDK 部署后 PortalStack 的输出中找到。它也可以在 PortalStack CloudFormation 堆栈的 Outputs 选项卡下，以 `PiiPortalApiGatewayInvokeUrl` 的导出名称找到 | 是 |
| `VITE_BASE` | /portal | 指定请求渲染门户所需静态文件时使用的路径 | 是 |
| `VITE_API_PATH` | /api | 指定向 API Gateway 发送请求所需的路径 | 是 |

#### 门户部署

在终端/CLI 环境中运行以下命令。

- 在运行以下任何命令之前，先进入 app 目录的根目录，通过运行以下命令为生产环境构建该应用：安装 NPM 包  `npm install`  构建文件  `npm run build`
- 构建成功后，把 `dist/` 目录中的所有文件传输到为此类资源指定的 Amazon S3 存储桶（在通过 CDK 预置的 PortalStack 中指定）。示例：`aws s3 sync dist/ s3://<<name-of-s3-bucket>> --delete<<name-of-s3-bucket>>` 是在 `<<resource-name-prefix>>-PortalStack` CloudFormation 堆栈中创建、逻辑 ID 为 `PrivateWebHostingAssets` 的 S3 存储桶。该值可以从 AWS 控制台中该 CloudFormation 堆栈的 Resources 选项卡获取。当 PortalStack 成功完成后，该值也会在 `cdk deploy` 过程中输出。

#### 访问门户

使用 `cdk deploy` 过程中创建的 API Gateway 的 invoke URL，即可从 Web 浏览器访问门户。该 URL 可以通过以下步骤找到：

- 访问 AWS 控制台
- 前往 API Gateway，找到 `cdk deploy` 过程中创建的 API Gateway。该 API Gateway 的名称可以在 `<<resource-name-prefix>>-PortalStack` CloudFormation 堆栈的 Resources 部分找到。
- 点击左侧菜单中的 **Stages** 链接。
- 确认已选中 **portal** 阶段
- 找到 **Invoke URL** 并复制该值
- 把该值输入到 Web 浏览器的地址栏中

门户的用户界面现在就会显示在 Web 浏览器中。如果有任何电子邮件已被处理，它们会列在门户的首页上。

#### 访问控制（可选）

对于生产环境部署，我们推荐采用[这些方法](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-control-access-to-api.html)来控制和治理对 Portal 的访问。

### 清理

为避免产生后续费用，请按以下步骤删除该方案创建的资源：

- 删除该方案创建的 [S3 存储桶](https://docs.aws.amazon.com/AmazonS3/latest/userguide/delete-bucket.html)中的内容：原始邮件存储桶、已遮盖邮件存储桶、门户静态资源存储桶（如果部署了门户）
- 使用下面的 cli 命令删除或停用该方案创建的 Amazon SES 规则步骤：  `#to disable the rule set use below command aws ses set-active-receipt-rule-set #to delete the rule set use below command # Replace <<resource_name_prefix>> with resource_name_prefix used in context.json aws ses delete-receipt-rule-set --rule-set-name <resource_name_prefix>>-rule-set`
- 按以下顺序删除 CloudFormation 堆栈：  `cdk destroy <<resource_name_prefix>>-PortalStack (if deployed) cdk destroy <<resource_name_prefix>>-ConsumerStack cdk destroy <<resource_name_prefix>>-S3Stack`
- CDK Destroy 不会删除部署过程中创建的访问日志 Amazon S3 存储桶。用户可以在 `<<resource_name_prefix>>-S3Stack` 堆栈的输出选项卡中，以 AccessLogsBucket 的导出名称获取该日志存储桶名称。执行以下步骤删除访问日志存储桶：要删除访问日志存储桶的内容，请按照[删除 S3 存储桶的说明](https://docs.aws.amazon.com/AmazonS3/latest/userguide/delete-bucket.html)操作。访问日志存储桶启用了版本控制，在上述步骤中删除存储桶内容不会删除存储桶中的版本化对象。需要使用下面的 aws cli 命令单独删除它们：  `#to remove versioned objects use below aws cli command aws s3api delete-objects --bucket ${accesslogbucket} --delete "$(aws s3api list-object-versions --bucket ${accesslogbucket} --query='{Objects: Versions[].{Key:Key,VersionId:VersionId}}')" #once versioned objects are removed we need to remove the delete markers of the versioned objects using below aws cli command aws s3api delete-objects --bucket ${accesslogbucket} --delete "$(aws s3api list-object-versions --bucket ${accesslogbucket} --query='{Objects: DeleteMarkers[].{Key:Key,VersionId:VersionId}}')"`  使用下面的 aws cli 命令删除访问日志 Amazon S3 存储桶：  `#delete the access log bucket itself using below aws cli command aws s3api delete-bucket --bucket ${accesslogbucket}`
- 如果配置了 Amazon SES：删除已验证的域/电子邮件身份；从你的 DNS 服务商处删除 MX 记录；从 AWS Secrets Manager 中删除 SMTP 凭证
- [删除 Lambda 函数创建的任何 CloudWatch 日志组](https://docs.aws.amazon.com/solutions/latest/video-on-demand-on-aws-foundation/deleting-the-cloudwatch-logs.html)

作为该方案先决条件的 VPC 及其关联资源，如果可能被其他应用程序使用，则不应删除。

## 结论

本文中，我们演示了如何使用 Amazon Bedrock Data Automation 和 Amazon Bedrock Guardrails，自动完成跨文本与图像内容的 PII 检测和遮盖。通过集中化并精简遮盖流程，组织可以加强与数据隐私要求的一致性、提升安全实践水平并减少运维开销。

然而，同样重要的是，要确保你的方案在设计时考虑到 Amazon Bedrock Data Automation 文档处理的[约束](https://docs.aws.amazon.com/bedrock/latest/userguide/bda-output-documents.html)。Amazon Bedrock Data Automation 支持 PDF、JPEG 和 PNG 文件格式，控制台处理的最大大小为 200 MB（通过 API 为 500 MB），并且除非启用文档拆分，单个文档不得超过 20 页。

通过使用 Amazon Bedrock Data Automation 和 Amazon Bedrock Guardrails 的集中化遮盖能力，组织可以加强数据隐私合规管理、削减运维开销，并在多样化的工作负载中维持严格的安全水平。该方案的可扩展性还进一步支持与其他 AWS 服务集成、针对更高级的 PII 模式微调检测逻辑，以及在未来拓展对更多文件类型或语言的支持，从而演进为更健壮的企业级数据保护框架。

我们鼓励你探索[提供的 GitHub 代码仓库](https://github.com/aws-samples/sample-bda-redaction)，在你的组织中部署该方案。除了带来运营效率、可扩展性、安全性和适应性之外，该方案还提供统一的界面和健壮的审计轨迹，简化了数据治理。通过改进检测规则，用户可以在可能的情况下集成额外的文件格式，并使用 Amazon Bedrock Data Automation 和 Amazon Bedrock Guardrails 的模块化框架。

我们邀请你在以下 [GitHub 仓库](https://github.com/aws-samples/sample-bda-redaction)中实施这套 PII 检测与遮盖方案，在 Amazon Bedrock 上构建更安全、更贴合合规要求且高度可适应的数据保护方案，以应对不断变化的业务与监管要求。

### 关于作者

![作者 Himanshu Dixit](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/23/ML-184362.jpeg)**Himanshu Dixit** 是 AWS Professional Services 的交付顾问，专攻数据库与分析，在技术领域拥有超过 18 年的经验。他热衷于人工智能、机器学习和生成式 AI，善用这些前沿技术打造创新方案，解决客户面临的现实挑战。工作之余，他喜欢打羽毛球、网球、板球和乒乓球，并与两个女儿共度时光。

![作者 David Zhang](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/23/ML-184363.jpeg)**David Zhang** 是 AWS Professional Services 的客户经理，负责为电信、金融、媒体和娱乐行业的财富 100 强客户主导企业级 AI/ML 与云转型计划。工作之余，他喜欢在厨房里尝试新菜谱、吹次中音萨克斯，并用相机记录生活中的瞬间。

![作者 Richard Session](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/23/ML-184364.jpeg)**Richard Session** 是 AWS ProServe 的首席用户界面开发者，作为全栈开发者拥有超过 15 年的经验，涉足营销/广告、企业技术、汽车和电子商务等行业。他热衷于打造直观且富有吸引力的用户体验，并运用自己深厚的背景为 AWS 的企业客户构建出色的界面。不在设计创新用户体验时，Richard 会去追寻他对咖啡的热爱、以 DJ 身份打碟，或探索全球新的目的地。

![作者 Viyoma Sachdeva](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/23/ML-184365.jpeg)**Viyoma Sachdeva** 是 AWS 的首席行业专家。她专注于 AWS DevOps、容器化和 IoT，帮助客户加速迈向 AWS 云的旅程。
