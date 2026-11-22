---
vendor: aws_bedrock
title: Build an AI-powered recruitment assistant using Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-an-ai-powered-recruitment-assistant-using-amazon-bedrock
date: 2026-05-21
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 50fbccd33094
---

# 使用 Amazon Bedrock 构建 AI 驱动的招聘助手

根据一项覆盖 748 位 HR 负责人的[人力管理调查](https://www.peoplemanagement.co.uk/article/1929340/uk-recruiters-lose-two-days-per-hire-admin-report-finds)，招聘人员平均每个职位空缺要花 17.7 小时在行政事务上。这超过每次招聘两个工作日。另一项 [2024 年 SmartRecruiters 调查](https://www.kinematiclabs.dev/blog/staffing/recruiters-spending-time-on-admin-work) 发现，45% 的人才招聘负责人把超过一半的工作时间花在本可自动化的任务上。这种行政负担迫使人们做肤浅的筛选：既会漏掉合格候选人，又会依据格式和关键词密度、而非真实的能力匹配来推进人选。

在本文中，我们将演示如何使用 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 构建一个由 AI 驱动的招聘助手，为候选人评估带来效率提升，生成个性化的面试问题，并为人工招聘决策提供数据驱动的洞察。本文给出的是一个用于学习目的的参考架构，并非可直接投产的解决方案。Amazon Bedrock 与本文用到的 AWS 服务都是通用工具，客户可以把它们组合起来支持各类用例，其中也包括招聘工作流。该架构只是展示了一种可能的做法，客户应依据自身具体需求加以调整。

你将学会部署用于简历解析、候选人评分、技能评估和面试问题生成的专项 AI 能力——其中 [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) 提供 PII 匿名化、prompt 攻击检测和与偏见相关的内容过滤——所有这些都通过一个协同的无服务器架构共同工作。该解决方案使用 [Amazon Bedrock Converse API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html) 搭配 [Amazon Nova Pro](https://aws.amazon.com/nova/)，用 [AWS Lambda](https://aws.amazon.com/lambda/) 做处理，用 [Amazon API Gateway](https://aws.amazon.com/api-gateway/) 做路由，用 [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) 和 [Amazon Simple Storage Service (Amazon S3)](https://aws.amazon.com/s3/) 做数据存储，并用 Amazon Bedrock Guardrails 做负责任的 AI 评估。

# 解决方案概览

这个 AI 候选人筛选助手使用 Amazon Bedrock 中可用的基础模型（FM），帮助完成候选人评估、简化面试准备，并为招聘决策提供数据驱动的洞察。该解决方案会对简历做全面分析处理，计算多维度的匹配度分数，并根据职位要求和候选人画像生成个性化面试问题。

身份认证与前端层使用 [AWS Amplify](https://aws.amazon.com/amplify/) 托管 Web 应用，并用 Amazon Cognito 做用户身份验证。[Amazon Cognito](https://aws.amazon.com/cognito/) 负责用户注册、登录，并提供 JWT token，这些 token 会在每次 API 请求时由 Amazon API Gateway Cognito 授权方校验。

后端层使用 Amazon API Gateway 把请求路由到专门的 AWS Lambda 函数，每个 Lambda 函数负责一个特定工作流。Lambda 函数调用 Amazon Bedrock Converse API，执行深度简历分析、计算匹配度分数，并生成针对具体角色的面试问题。

# 架构图

下图展示了 AI Recruiting Assistant 的架构。

[![AI Assistant 的架构示意图，展示五个层次：由 AWS Amplify 构成的前端层、由 Amazon Cognito 和 IAM 构成的安全层、由 Amazon API Gateway 构成的 API 层、包含四个 Lambda 函数（Jobs API、Job Creation、AI Recruitment、Resume Processor）的处理层、由 Amazon Bedrock 和 Amazon Nova 构成的 AI 处理层，以及由 Amazon DynamoDB 和 Amazon S3 构成的数据层。箭头展示了数据流：招聘人员经 HTTPS 访问前端，通过 REST API 调用访问后端，经 Amazon Bedrock 进行 AI 处理，并在 DynamoDB 与 S3 中存储数据。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-1.jpeg)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-1.jpeg)

**该架构包含以下关键部分：**

**前端层：**AWS Amplify 托管一个响应式的、基于 React 的 Web 应用，为招聘人员提供直观的界面，用于管理职位发布、审阅 AI 生成的候选人评估，以及访问个性化的面试准备材料。

**安全层：**Amazon Cognito 管理用户注册与身份验证，提供 JWT token，这些 token 会在每次 API 请求时由 Amazon API Gateway Cognito 授权方校验。AWS Identity and Access Management（IAM）角色为 AWS Lambda 函数提供最小权限访问，以便与存储和 AI 服务交互。客户有责任正确配置这些安全控制。

**API 层：**Amazon API Gateway 通过 RESTful 端点编排客户端与服务端通信，涵盖职位管理、AI 驱动的候选人匹配、简历上传处理和面试问题生成服务。

**处理层：**专门的 AWS Lambda 函数处理招聘工作流，每个函数都针对适当的超时和内存配置进行设计。

**AI 处理层：**Amazon Bedrock 基础模型使用 Converse API 进行分析，执行深度简历分析、计算多维度匹配度分数、生成针对具体角色的面试问题，并识别可迁移技能。Amazon Bedrock Guardrails 对每个请求做过滤：匿名化输入中的 PII、阻止来自简历内容的 prompt 注入尝试，并拒绝涉及候选人口统计特征的响应。

下面的代码片段展示了该解决方案如何使用 Amazon Bedrock Guardrails（它在模型处理之前自动匿名化输入中的 PII）、带证据的评分结构化 prompt，以及感知偏见的系统指令：

```
import json

SYSTEM_PROMPT = """You are an expert recruitment analyst. Evaluate
candidates based exclusively on demonstrated skills, experience,
and qualifications. Do not reference or make assumptions based on
candidate names, contact details, demographics, or personal
characteristics. Focus only on job-relevant qualifications.
For every claim, cite the specific resume text as evidence."""

ANALYSIS_PROMPT = """Analyze the following candidate resume against
the job requirements. Return a structured JSON response.

<job_requirements>
{job_description}
</job_requirements>

<candidate_resume>
{resume_content}
</candidate_resume>

Provide your analysis in the following JSON format:
{{
  "compatibilityScore": 0-100,
  "scoreJustification": "Evidence-based reasoning with resume quotes",
  "technicalSkills": {{
    "matched": [{{"skill": "X", "evidence": "resume quote"}}],
    "missing": ["skill3"],
    "transferable": [{{"skill": "Y", "evidence": "resume quote"}}]
  }},
  "experienceAnalysis": {{
    "relevantYears": 0,
    "industryAlignment": "high|medium|low",
    "keyAccomplishments": ["accomplishment with evidence"]
  }},
  "strengths": ["strength with specific resume evidence"],
  "concerns": ["concern with context"],
  "interviewQuestions": [
    {{
      "question": "Targeted question text",
      "purpose": "What this question evaluates",
      "lookFor": "Ideal response indicators"
    }}
  ],
  "overallRecommendation": "strong_match|good_match|partial_match|weak_match"
}}"""

response = bedrock_client.converse(
    modelId=model_id,
    system=[{"text": SYSTEM_PROMPT}],
    messages=[{
        "role": "user",
        "content": [{"text": ANALYSIS_PROMPT.format(
            job_description=job_description,
            resume_content=resume_content
        )}]
    }],
    inferenceConfig={
        "maxTokens": 4096,
        "temperature": 0.2,
        "topP": 0.9
    },
    guardrailConfig={
        "guardrailIdentifier": guardrail_id,
        "guardrailVersion": guardrail_version,
        "trace": "enabled"
    }
)

# Validate informational output for recruiter; not a hiring recommendation
try:
    analysis = json.loads(
        response["output"]["message"]["content"][0]["text"]
    )
except json.JSONDecodeError:
    analysis = {"error": "Model returned invalid JSON"}
```

*注：我们使用较低的 temperature（0.2）以产生一致、可复现的候选人评估。当 Guardrails 介入时（例如阻止嵌入在简历中的 prompt 注入），响应中会包含 GUARDRAIL_INTERVENED 动作——请实现错误处理以记录这些事件，并向招聘人员返回安全的兜底响应。*

**数据层：**Amazon DynamoDB 存储结构化的职位发布和分析结果。Amazon S3 为候选人简历提供存储，并启用服务端加密（AES-256）、阻止公开访问和仅允许 HTTPS 的存储桶策略。

**以下步骤描述了招聘人员分析候选人时的请求流程：**

- 招聘人员打开由 AWS Amplify 托管的 Web 应用，并通过 Amazon Cognito 完成身份验证。
- 招聘人员创建包含角色要求、所需技能和经验水平的职位发布。
- 招聘人员为该职位上传候选人简历（PDF、DOCX 或 TXT 格式）。
- 前端向 Amazon API Gateway 的 /matches 端点发送 POST 请求。
- API Gateway Cognito 授权方校验请求头中的 JWT token。
- API Gateway 将已认证的请求路由到 AI 招聘 Lambda 函数。
- Lambda 函数从 Amazon DynamoDB 获取职位发布，从 Amazon S3 获取候选人简历。该函数使用职位要求和简历内容调用 Amazon Bedrock Converse API。
- Amazon Bedrock 分析每位候选人，计算匹配度分数，识别优势与顾虑，并生成个性化面试问题。
- 结果存储在 Amazon DynamoDB 中，并在 Web 界面中返回给招聘人员。

# 核心能力

**智能简历分析**
 该解决方案会处理简历，然后分析技能深度和经验相关性，而不只是依赖关键词匹配。它会针对职位要求计算匹配度分数，并附上简历原文中的具体证据，同时识别出人工筛选常常漏掉的可迁移技能。

**高级候选人匹配**
 系统使用自然语言处理（NLP）将候选人画像与职位描述进行比对，给出基于百分比的匹配分数，并引用简历中的证据。它突出候选人的优势与顾虑，同时按匹配度对候选人排序，方便招聘人员高效审阅。

**个性化面试准备**
 该解决方案会根据具体职位角色和候选人背景创建量身定制的面试问题，生成带评分量规的评估框架。它会产出详细的面试指南，包含开场话题和追问建议。

**工作流自动化**
 系统协助处理重复性的行政任务，并支持批量操作。它通过 RESTful API 与现有系统集成，并提供用量分析。

# 前提条件

在开始之前，请确认你已具备：

- 一个具有相应权限的 AWS 账户，可用于 Amazon Bedrock、[AWS Identity and Access Management (IAM)](https://aws.amazon.com/iam/)、[AWS CloudFormation](https://aws.amazon.com/cloudformation/)、Amazon API Gateway、Amazon Cognito、Amazon DynamoDB、Amazon S3、AWS Lambda 和 AWS Amplify。
- 在你部署所在的 AWS 区域中具有 Amazon Nova Pro 的 Amazon Bedrock 模型访问权限。你也可以改用其他受支持的模型。有关当前的模型可用性，请参阅[各 AWS 区域的模型支持](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html)。
- 已安装 [AWS Command Line Interface (AWS CLI)](https://aws.amazon.com/cli/) v2.0 或更高版本，并配置好相应凭证。
- 已安装 Python 3.10 或更高版本。
- 可访问终端或命令提示符。

**成本估算：**用于测试 100 位候选人时，总成本约为每月 $1–2。Amazon Bedrock（Nova Pro 为每百万输入/输出 token $0.80/$3.20）完成 100 次分析[成本](https://aws.amazon.com/bedrock/pricing/)不到 $1。Amazon Bedrock Guardrails 每位候选人增加约 $0.01。本文提到的其他服务在测试量级下处于 AWS 免费套餐范围内。详细估算请使用 [AWS Pricing Calculator](https://calculator.aws/)。

**重要：确认 AWS 区域一致性**
 确认以下各项都配置为使用同一个 AWS 区域：你在 aws configure 中设置的默认区域、你已启用 Amazon Bedrock 模型访问的区域，以及部署期间创建的所有资源。

# 部署解决方案

**部署后端基础设施**。你将需要为本次解决方案中使用的 AWS 资源付费。

[![用于部署 AI Assistant 解决方案 AWS CloudFormation 模板的启动堆栈按钮。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-2.png)](https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create?stackName=AIRecruiterAssistantBlogSetup&templateURL=https://aws-blogs-artifacts-public.s3.us-east-1.amazonaws.com/ML-18419/AIRecruitingAssistantBackendTemplate.yaml)

控制台会跳转到 AWS CloudFormation，模板 URL 已预填到堆栈参数中。

- 在 Stack name 中，输入部署名称（默认：AIRecruiterAssistantBlogSetup）。
- 在 BedrockModelId 中，选择要使用的 Amazon Bedrock 模型（默认：Amazon Nova Pro）。
- 检查堆栈配置。
- 选择 **Create stack**。
- 部署成功后，在 CloudFormation 堆栈的 **Outputs** 选项卡中记录以下值：

- ApiGatewayUrl CognitoUserPoolId CognitoClientId AWSRegion AmplifyAppUrl AmplifyConsoleUrl

**部署前端应用**

- 下载 [AIRecruitingAssistantFrontEndAmplifyDeployment.zip](https://aws-blogs-artifacts-public.s3.us-east-1.amazonaws.com/ML-18419/AIRecruitingAssistantFrontEndAmplifyDeployment.zip) 文件。
- 导航到 **CloudFormation Outputs** 下的 AmplifyConsoleUrl。
- 选择 ai-recruitment-system-frontend 应用。
- 选择 **Deploy updates**。
- 在 Method 中选择 **Drag and drop**。
- 选择要上传的 .zip 文件。
- 选择 **Save and deploy**。

# 测试解决方案

基础设施部署完成且前端应用运行起来后，你可以通过 Web 界面测试 AI Recruiting Assistant 的核心功能。

**第 1 步：配置应用设置**

导航到 **System Configuration** 页面，填入 CloudFormation 堆栈输出中的值：

- API Gateway URL：输入 ApiGatewayUrl
- Amazon Cognito User Pool ID：输入 CognitoUserPoolId
- Amazon Cognito Client ID：输入 CognitoClientId
- AWS Region：输入 AWS 区域

[![AI Assistant Web 应用的系统配置页面，展示 API Gateway URL、Cognito 用户池 ID、Cognito 客户端 ID 和 AWS 区域四项快速设置字段，以及一个保存配置按钮。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-3.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-3.png)

**第 2 步：用户注册与登录**

- 在登录页面选择 **SIGN UP**。
- 输入你的姓名、电子邮箱和一个安全密码。
- 选择 **Create Account**。

[![AI Assistant 注册页面，包含全名、电子邮箱、密码和确认密码四个字段，以及一个创建账户按钮。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-4.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-4.png)

- 输入发送到你邮箱的一次性验证码。
- 选择 **Verify Email**。

[![AI Assistant 邮箱验证页面，提示用户输入发送到其电子邮箱的六位验证码，并带有一个验证邮箱按钮。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-5.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-5.png)

- 验证成功后，使用邮箱和密码登录。

[![AI Assistant 登录页面，包含电子邮箱和密码字段，以及一个登录按钮。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-6.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-6.png)

**第 3 步：创建职位发布**

- 导航到 AI Recruiting Assistant 仪表板并创建新的职位发布。

[![AI Assistant 仪表板，展示岗位总数、活跃岗位、候选人总数和最近匹配四张汇总卡片，数值均为零。快捷操作面板包含新建岗位、查看全部岗位、管理简历和 AI 候选人匹配的链接。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-7.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-7.png)

- 填写详细要求，包括职位名称、所需技能、经验水平和职位描述。这些信息构成 AI 驱动的候选人匹配和分析的基础。

[![新建岗位表单，包含基本信息字段（职位名称、部门、地点、工作类型、经验水平、薪资范围）、职位详情字段（职位描述、任职要求、职责、福利），以及带 AI/ML、Large Language Models、Java、Agentic、JavaScript 和 Node.js 标签的所需技能。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-8.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-8.png)

- 选择 **Create Job**。职位将在招聘门户中创建。

[![岗位列表页面，展示一个状态为活跃的 Senior Software Engineer 职位，位于 Herndon, VA 的工程部门，带有 AI/ML、Large Language Models 和 Java 的技能标签，以及查看详情和查找候选人按钮。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-9.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-9.png)

- 选择 **View Details** 查看职位详情。

[![Senior Software Engineer 角色的职位详情页面，展示完整的职位描述、所需技能、任职要求，以及包含管理简历和 AI 候选人匹配按钮的岗位操作侧边栏，还有岗位 ID、发布日期、类型和候选人数量等职位元数据。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-10.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-10.png)

你可以选择 **Manage Resumes** 为已创建的职位上传候选人简历。

**第 4 步：上传候选人简历**

- 使用 Upload Resumes 功能提交候选人申请以供分析。系统接受 PDF、DOCX 和 TXT 文件格式。

***注**：这个基于界面的上传流程用于演示解决方案在测试场景下的功能。在生产环境中，简历通常通过你所在组织的招聘门户提交，自动存入 Amazon S3，并通过事件驱动的触发器进行处理。*

[![简历管理页面，展示 Senior Software Engineer 的职位选择器、支持 PDF、DOC、DOCX 和 TXT 格式的上传简历区域，以及三条已上传候选人简历的列表，含文件名、上传时间戳和文件大小。页面上有查找候选人按钮用于启动 AI 分析。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-11.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-11.png)

**第 5 步：生成 AI 分析和面试问题**

- 选择 **Find Best Matches**，开始对已上传的候选人进行针对你职位发布的 AI 分析。系统会处理简历内容、计算匹配度分数、识别关键优势与顾虑，并生成个性化面试问题。

[![AI 候选人匹配结果页面，展示三位候选人按匹配分数排序：Jeff Williams 为 95%（优秀匹配，建议强烈推荐）、Kevin Martinez 为 75%（良好匹配，建议考虑面试）、Brian Foster 为 40%（部分匹配，不建议录用）。每位候选人的卡片展示匹配的技能、经验年限，以及查看详情和面试问题按钮。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-12.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-12.png)

- 选择 **View Details** 查看候选人详情、匹配分数、优势、顾虑和面试建议。

[![Jeff Williams 的候选人详情弹窗，展示匹配分析，分数为 95%，建议为强烈推荐。优势包括丰富的 Java、JavaScript 和 Node.js 经验、AI/ML 专长，以及 AI 驱动的广告背景。顾虑指出其没有明确的 Agentic 框架经验，主要经验在 Google Ads 和 Meta 而非 Amazon Ads。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-13.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-13.png)

[![Brian Foster 的候选人详情弹窗，展示匹配分析，分数为 40%，状态为不建议录用。优势包括前端开发技能、React 和 JavaScript 经验，以及对 Agile/Scrum 的理解。顾虑指出其缺乏所需的 AI/ML 和 Large Language Models 技能，且专业经验年限不足。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-14.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-14.png)

[![Kevin Martinez 的候选人详情弹窗，展示匹配分析，分数为 75%，建议为考虑面试。优势包括 Java、JavaScript 和 Node.js 经验、AWS 服务与 REST API 经验，以及协作式的团队交付能力。顾虑指出其 AI/ML 和 Large Language Models 经验有限，设计与架构方面的经验也较少。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-15.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-15.png)

- 使用 **Interview Questions** 按钮生成个性化面试问题。

[![AI 生成的面试问题按三列组织：技术问题涵盖微服务架构、LLM 集成、生成式 AI 微调、Java 与 JavaScript 项目以及广告投放系统；领导力问题涵盖团队领导、持续改进、冲突解决、艰难决策和带教；个性化问题针对候选人背景量身定制，涵盖广告平台集成、Spring Boot 与 Express.js 对比、RAG 与 prompt 工程项目、多云策略，以及下一代 AI 广告平台设计。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-16.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/24/ML-18419-image-16.png)

- 结果包含匹配度分数、技能评估、经验分析、面试问题和关键洞察——全部以简历中的具体证据为依据。

在部署到生产环境之前，请审阅以下安全性、合规性和扩展方面的注意事项。

**安全与责任共担**
 安全是 AWS 与客户共同承担的责任。AWS 负责底层云基础设施的安全，而客户负责保护自己的数据、配置访问控制、实施加密，并核验其对 AWS 服务的使用符合自身的合规要求。更多信息请参阅 [AWS 责任共担模型](https://aws.amazon.com/compliance/shared-responsibility-model/)。

CloudFormation 模板实现了以下安全控制：

- 在存储桶上启用 S3 Block Public Access
- Amazon API Gateway Cognito 授权方在非 OPTIONS 方法上校验 JWT token
- 候选人简历静态存储时使用 S3 服务端加密（AES-256）与 DynamoDB 加密，并启用时间点恢复
- Amazon API Gateway 阶段级限流（100 请求/秒，突发上限 50）
- Amazon Bedrock 的 IAM 权限限定到特定的基础模型，Lambda 执行角色使用限定到具体资源 ARN 的最小权限 IAM 策略
- Amazon Bedrock Guardrails 具备 prompt 攻击检测、PII 匿名化、人口统计偏见主题拒绝和内容过滤（防止 PII 泄漏）
- 强制仅允许 HTTPS 访问的 S3 存储桶策略
- 用于简历自动过期的 S3 生命周期策略（可配置保留期，以符合 GDPR/CCPA）
- Amazon Cognito 支持可选的多重身份验证（TOTP）
- 在 Lambda 函数和 API Gateway 上启用 [AWS X-Ray](https://aws.amazon.com/xray/) 主动追踪，实现端到端请求可见性（提升检测能力）

客户负责配置 Amazon Cognito 用户池策略、管理用户访问、为审计日志启用 [AWS CloudTrail](https://aws.amazon.com/cloudtrail/)，并根据组织要求添加安全控制。

**威胁模型与安全分析**
 为验证我们 AI 招聘系统的安全性，我们开展了一次威胁建模演练，以识别潜在的安全风险、分析攻击途径并验证我们的安全控制。本节记录了系统面临的主要威胁——包括未经授权访问候选人 PII、通过简历内容发起的 prompt 注入攻击，以及 API 滥用——并给出其攻击途径、对应的缓解措施和残余风险评估。通过系统性地应对这些威胁，我们帮助保护候选人隐私、维护系统完整性，并满足企业安全标准。

**AI 公平性与负责任使用**
 该解决方案协助进行候选人评估和评分，这属于高风险 AI 应用。客户有责任验证 AI 生成的评估不会在受保护群体之间引入偏见。建议实施公平性测试程序、对 AI 生成的分数进行定期审计复核，并在关键决策点设置强制的人工复核环节。招聘人员仍是最终招聘决策的责任人，应把 AI 生成的洞察作为其评估过程中众多输入之一。

**数据隐私与合规**
 客户有责任核实其实现符合适用的数据保护法规，包括 [GDPR](https://gdpr.eu/)、[CCPA](https://oag.ca.gov/privacy/ccpa) 以及各地的雇佣法律。建议使用 Amazon S3 生命周期规则实施数据保存策略、为候选人的被遗忘权请求建立数据删除工作流，并通过 AWS CloudTrail 记录访问日志，以追踪谁访问了候选人信息。AWS 为底层服务提供安全能力和合规认证，但客户必须按照自身具体的监管要求配置这些功能。

**输入验证与内容安全**
 该解决方案接受用户上传的简历，并将其送入 Amazon Bedrock 基础模型处理。建议为简历上传实施文件大小限制、使用文件类型检查（而不只是文件扩展名）进行内容验证，并对职位发布表单字段做输入清洗，以帮助防止注入攻击。Amazon API Gateway 的请求限流有助于防止 API 端点被滥用。

**扩展到企业级**
 该解决方案面向测试与评估设计。在扩展到生产环境时，可考虑在安全性、可观测性和运行韧性方面做以下增强：

- API 防护：在 Amazon API Gateway 阶段上添加 [AWS WAF](https://aws.amazon.com/waf/)，配置基于速率的规则以防滥用，并使用 AWS 托管 common 规则集提供 OWASP top 10 防护。这会增加约每个月 $6 的成本，但可提供分布式拒绝服务（DDoS）缓解和 bot 过滤。
- 可观测性与告警：为 AWS Lambda 错误率、Amazon API Gateway 5xx 响应和 Amazon Bedrock 限流事件配置 [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/) 告警。启用 Amazon Bedrock 模型调用日志，捕获请求/响应对以用于审计追踪。使用 AWS X-Ray 追踪（本解决方案已启用）识别请求链路中的延迟瓶颈。
- 输出校验：针对模型返回格式错误 JSON 的情况，实现带指数退避的重试逻辑。把系统 prompt 存放到 [AWS Systems Manager Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) 中，以便无需重新部署即可管理版本；或使用 [Amazon Bedrock prompt management](https://aws.amazon.com/bedrock/prompt-management/) 在基础模型之间集中创建、优化、管理版本并并排比较 prompt。
- 并发管理：设置 AWS Lambda 预留并发，以防分析请求突发耗尽你的 Amazon Bedrock 服务配额。监控 Amazon Bedrock 限流指标，并在扩展前申请提高服务配额。
- 数据生命周期自动化：该解决方案包含用于简历过期的 S3 生命周期策略。生产环境中，请与你所在组织的数据保存策略集成，并为 GDPR 和 CCPA 下的候选人被遗忘权请求实现自动化删除工作流。

**模型灵活性**
 Converse API 的抽象有助于提供灵活性，让你可以在有更新的基础模型可用时升级，而无需修改应用代码。CloudFormation 模板包含一个用于选择 Amazon Bedrock 模型的参数，因此你可以根据准确度和成本要求在受支持的模型之间切换。

# 清理资源

*重要：本解决方案部署的 AWS 资源在删除之前会持续产生费用。这包括 Amazon S3 存储、Amazon DynamoDB 表、AWS Amplify 托管和 Amazon Cognito 用户池。AWS Lambda 和 Amazon Bedrock 仅在使用时计费。请完成以下清理步骤以停止产生费用。*

*警告：删除 Amazon S3 存储桶会永久移除候选人简历和生成的面试材料。如果你出于合规、法律或记录保存目的必须保留这些数据，请在删除前导出或备份存储桶内容。*

- 清空 Amazon S3 存储桶：导航到 Amazon S3 控制台，选择该解决方案创建的存储桶，选择 **Empty**，然后**确认**。
- 删除 AWS Amplify 应用：导航到 AWS Amplify 控制台，选择 ai-recruitment-system-frontend 应用，然后选择 **Delete**。
- 删除 CloudFormation 堆栈：在 AWS CloudFormation 控制台中选择你的堆栈，然后选择 **Delete**。这会移除 Lambda 函数、Amazon API Gateway、Amazon DynamoDB 表、Amazon Cognito 资源和 IAM 角色。
- 确认 Amazon S3 存储桶已删除：如果存储桶未被 CloudFormation 自动删除，请导航到 Amazon S3 控制台手动删除
- 确认清理完成：在 AWS CloudFormation 控制台中确认堆栈状态显示 DELETE_COMPLETE。
- 检查 Amazon S3 控制台，确认存储桶已被移除。
- 检查 AWS Amplify 控制台，确认应用已被移除。

# 后续步骤

在部署并测试该解决方案之后，可以考虑以下增强：

- 多轮对话式招聘：使用 [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) 搭配 Strands Agents SDK 构建一个跨会话保留记忆的对话式招聘助手，支持追问和上下文感知的交互。
- AI 辅助候选人触达：添加一个由高匹配分数触发的 AWS Step Functions 工作流，生成个性化的触达邮件草稿并通知招聘人员审阅。招聘人员可以查看候选人画像、编辑草稿，并批准或拒绝该次触达。已批准的邮件可通过 Amazon [Amazon Simple Email Service (Amazon SES)](https://aws.amazon.com/ses/) 发送。
- 实时简历摄取 pipeline 管理：用基于 Amazon S3 事件通知和 [AWS Step Functions](https://aws.amazon.com/step-functions) 的事件驱动 pipeline 替代手动上传，在简历从你的招聘门户到达时自动处理。
- 偏见审计仪表板：构建一个 AWS Quick Sight 仪表板，跟踪各匿名化人群群体的分数分布，以持续监控 AI 生成评估中的统计偏见。

# 结论

AI Recruiting Assistant 展示了 Amazon Bedrock 如何帮助减轻这项行政负担——对普通招聘人员来说，每个职位空缺要消耗超过 17 小时。通过 Converse API 使用基础模型，你可以自动化简历筛选、候选人评分和面试问题生成——让招聘人员腾出精力专注于推动招聘成功的候选人评估和关系构建。根据 [LinkedIn 的 2025 年招聘未来报告](https://www.linkedin.com/business/talent/blog/talent-acquisition/future-of-recruiting-2025)，使用生成式 AI 工具的人才团队每周大约节省 20% 的工作时间，相当于整整一天。

该架构是可扩展的，因此你可以将其调整为适应你的招聘工作流。要添加 AI 辅助候选人触达、智能排期或动态追问序列等能力，可增加 Lambda 函数和 API Gateway 端点。

本文中的示例代码以 MIT-0 许可证提供。详情请参阅 LICENSE 文件。

***免责声明：**** 本内容仅供参考，不应被视为法律或合规建议。客户有责任对本文档中的信息以及任何 AWS 产品或服务的使用自行做出独立评估。*

# 资源

- [Amazon Bedrock 用户指南](https://docs.aws.amazon.com/bedrock/latest/userguide/)
- [Amazon Bedrock 研讨会](https://catalog.workshops.aws/workshops/cdbce152-b193-43df-8099-908ee2d1a6e4/en-US)
- [研讨会：Strands Agents 入门](https://catalog.workshops.aws/workshops/33f099a6-45a2-47d7-9e3c-a23a6568821e/en-US)

## 关于作者
