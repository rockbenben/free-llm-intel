---
vendor: aws_bedrock
title: Build a serverless audio summarization solution with Amazon Bedrock and Whisper
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-a-serverless-audio-summarization-solution-with-amazon-bedrock-and-whisper
date: 2025-06-06
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: cd997c78d147
---

# 使用 Amazon Bedrock 与 Whisper 构建无服务器音频摘要方案

业务会议、访谈和客户互动的录音已成为保存重要信息的必要手段。然而，人工转录和总结这些录音往往既耗时又费力。随着[生成式 AI](https://aws.amazon.com/ai/generative-ai/)和自动语音识别（ASR）的进步，自动化方案已经出现，让这一过程更快、更高效。

保护个人可识别信息（PII）是数据安全的关键环节，既是道德责任，也是法律要求。本文演示如何使用 [Amazon Bedrock Marketplace](https://aws.amazon.com/bedrock/marketplace/) 中提供的 Open AI Whisper 基础模型（FM）Whisper Large V3 Turbo 来生成准实时转录——该 marketplace 通过专用部署提供对 140 多个模型的访问。随后，这些转录文本会交由 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 处理，进行摘要和敏感信息脱敏。

Amazon Bedrock 是一项完全托管的服务，可通过单一 API 提供来自领先 AI 公司的高性能基础模型供你选择，包括 [AI21 Labs](https://aws.amazon.com/bedrock/ai21/)、[Anthropic](https://aws.amazon.com/bedrock/claude/)、[Cohere](https://aws.amazon.com/bedrock/cohere/)、[DeepSeek](https://aws.amazon.com/bedrock/deepseek)、[Luma](https://aws.amazon.com/bedrock/luma-ai/)、[Meta](https://aws.amazon.com/bedrock/llama/)、[Mistral AI](https://aws.amazon.com/bedrock/mistral/)、[poolside](https://aws.amazon.com/bedrock/poolside/)（即将推出）、[Stability AI](https://aws.amazon.com/bedrock/stability-ai/) 和 [Amazon Nova](https://aws.amazon.com/ai/generative-ai/nova/)；同时还提供一整套能力，帮助你以安全、隐私和负责任 AI 的方式构建生成式 AI 应用。此外，你可以使用 [Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/) 自动从转录摘要中脱敏[敏感信息](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-sensitive-filters.html)（包括 PII），以满足合规与数据保护需求。

本文会带你看一套端到端架构：它以 React 前端配合 Amazon Bedrock、[AWS Lambda](https://aws.amazon.com/lambda) 和 [AWS Step Functions](https://aws.amazon.com/step-functions/) 来编排工作流，实现无缝集成与处理。

## 方案概览

本方案展示了将无服务器技术与生成式 AI 结合、以自动化和扩展内容处理工作流的威力。用户旅程始于通过 React 前端应用上传录音，该应用托管在 [Amazon CloudFront](https://aws.amazon.com/cloudfront/) 上，后端由 [Amazon Simple Storage Service](https://aws.amazon.com/s3)（Amazon S3）和 [Amazon API Gateway](https://aws.amazon.com/api-gateway) 支撑。文件上传后会触发 Step Functions 状态机，由它编排核心处理步骤，借助 AI 模型和 Lambda 函数实现无缝的数据流转与转换。下图展示了方案架构。

![用于音频处理的 AWS 无服务器架构：CloudFront 到 S3、EventBridge 触发、Lambda 与 Bedrock 负责转录和摘要](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/15/Picture1-5-1024x478.png)

该工作流包含以下步骤：

- React 应用托管在 S3 存储桶中，通过 CloudFront 向用户提供访问，实现快速的全球接入。API Gateway 负责处理前端与后端服务之间的交互。
- 用户直接从应用中上传音频或视频文件。这些录音会存储到指定的 S3 存储桶中等待处理。
- [Amazon EventBridge](https://aws.amazon.com/eventbridge/) 规则检测到 S3 上传事件后触发 Step Functions 状态机，启动由 AI 驱动的处理 pipeline。
- 状态机按顺序编排多个 Amazon Bedrock 模型，完成音频转录、摘要与脱敏。它使用 Whisper 做转录、Claude 做摘要，并用 Guardrails 脱敏敏感数据。
- 脱敏后的摘要返回前端应用并展示给用户。

下图展示了状态机工作流。

![用于音频处理的 AWS Step Functions 状态机：Whisper 转录、说话人识别和 Bedrock 摘要任务](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/19/Picture2-4-crop.png)

Step Functions 状态机编排一系列任务，对上传的音频/视频录音进行转录、摘要和敏感信息脱敏：

- 触发一个 Lambda 函数收集输入细节（例如 Amazon S3 对象路径、元数据）并准备用于转录的 payload。
- payload 通过 Amazon Bedrock Marketplace 发送给 OpenAI Whisper Large V3 Turbo 模型，生成录音的准实时转录。
- 原始转录文本通过 Amazon Bedrock 传给 Anthropic 的 Claude Sonnet 3.5，由它生成简洁、连贯的对话或内容摘要。
- 第二个 Lambda 函数校验摘要并将其转发到脱敏步骤。
- 摘要经 Amazon Bedrock Guardrails 处理，自动脱敏 PII 及其他敏感数据。
- 脱敏后的摘要会被存储，或通过 API 返回前端应用并展示给用户。

## 先决条件

开始之前，请确认已具备以下先决条件：

- 使用 Amazon Bedrock 模型前必须先申请访问权限，这是一次性设置步骤。就本方案而言，请确认你的 Amazon Bedrock 账户中已启用对 Anthropic 的 Claude Sonnet 3.5 模型的访问。具体说明参见[访问 Amazon Bedrock 基础模型](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)。
- 设置 guardrail，通过配置拦截或掩码敏感信息的过滤器来启用 PII 脱敏。有关为其他用例配置过滤器的指导，参见[使用敏感信息过滤器从对话中移除 PII](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-sensitive-filters.html)。
- 在 [Amazon Bedrock Marketplace](https://aws.amazon.com/bedrock/marketplace/) 内部署 Whisper Large V3 Turbo 模型。本文也提供了分步部署指导。
- 应已安装并配置 [AWS Command Line Interface](https://aws.amazon.com/cli)（AWS CLI）。具体说明参见[安装或更新到最新版本的 AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)。
- 应已安装 [Node.js 14.x](https://nodejs.org/en/download) 或更高版本。
- 应已安装 [AWS CDK CLI](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html#getting_started_install)。
- 你应具备 [Python 3.8+](https://www.python.org/downloads/)。

## 在 Amazon Bedrock 控制台中创建 guardrail

关于在 Amazon Bedrock 中创建 guardrail 的说明，请参见[创建 guardrail](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-create.html)。有关检测和脱敏 PII 的细节，参见[使用敏感信息过滤器从对话中移除 PII](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-sensitive-filters.html)。请按以下关键设置配置你的 guardrail：

- 启用 PII 检测与处理
- 将 PII 操作设置为 Redact
- 添加相关的 PII 类型，例如：姓名与身份 电话号码 电子邮箱地址 实际地址 财务信息 其他敏感个人信息

部署 guardrail 后，请记下 Amazon Resource Name（ARN），部署模型时会用到它。

## 部署 Whisper 模型

请完成以下步骤来部署 Whisper Large V3 Turbo 模型：

- 在 Amazon Bedrock 控制台的导航窗格中，在 **Foundation models ** 下选择 **Model catalog **。
- 搜索并选择 **Whisper Large V3 Turbo**。
- 在选项菜单（三个点）中，选择 **Deploy**。

![Amazon Bedrock 控制台展示筛选后的模型目录，其中包含 Whisper Large V3 Turbo 语音识别模型和部署选项](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/15/Picture3-1.png)

- 按你的具体用例修改 endpoint 名称、实例数量和实例类型。本文使用默认设置。
- 按你的用例修改 **Advanced settings** 部分。本文使用默认设置。
- 选择 **Deploy**。

这会创建一个新的 [AWS Identity and Access Management](https://aws.amazon.com/iam/) IAM 角色并部署模型。

你可以在导航窗格中选择 **Marketplace deployments**，然后在 **Managed deployments** 部分可以看到 endpoint 状态为 **Creating**。等待 endpoint 完成部署、状态变为 **In Service**，然后复制 Endpoint Name，部署时会用到它

![Amazon Bedrock 控制台：“How it works”概览，以及 Whisper 模型 endpoint 处于 in service 状态的托管部署表](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/15/Picture4.png)

## 部署方案基础设施

在 [GitHub repo](https://github.com/aws-samples/sample-bedrock-whisper-pii-audio-summarizer/) 中，按 [README 文件](https://github.com/aws-samples/sample-bedrock-whisper-pii-audio-summarizer?tab=readme-ov-file)中的说明克隆仓库，然后部署前端和后端基础设施。

我们使用 [AWS Cloud Development Kit](https://aws.amazon.com/cdk/)（AWS CDK）来定义和部署基础设施。AWS CDK 代码会部署以下资源：

- React 前端应用
- 后端基础设施
- 用于存储上传文件和处理结果的 S3 存储桶
- 包含 Lambda 函数的 Step Functions 状态机，用于音频处理和 PII 脱敏
- 用于处理请求的 API Gateway endpoint
- 用于安全访问的 IAM 角色与策略
- 用于托管前端的 CloudFront 分配

## 实现深入剖析

后端由一系列 Lambda 函数组成，每个函数负责音频处理 pipeline 的一个特定阶段：

- **Upload handler** – 接收音频文件并将其存储到 Amazon S3
- **Transcription with Whisper** – 使用 Whisper 模型把语音转换为文本
- **Speaker detection** – 区分并标注音频中的各个说话人
- **Summarization using Amazon Bedrock** – 从转录文本中提取并总结要点
- **PII redaction** – 使用 Amazon Bedrock Guardrails 移除敏感信息以满足隐私合规

让我们来看一些关键组件：

转录 Lambda 函数使用 Whisper 模型把音频文件转换为文本：

```
def transcribe_with_whisper(audio_chunk, endpoint_name):
    # Convert audio to hex string format
    hex_audio = audio_chunk.hex()
    
    # Create payload for Whisper model
    payload = {
        "audio_input": hex_audio,
        "language": "english",
        "task": "transcribe",
        "top_p": 0.9
    }
    
    # Invoke the SageMaker endpoint running Whisper
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType='application/json',
        Body=json.dumps(payload)
    )
    
    # Parse the transcription response
    response_body = json.loads(response['Body'].read().decode('utf-8'))
    transcription_text = response_body['text']
    
    return transcription_text
```

我们使用 Amazon Bedrock 从转录文本生成简洁摘要：

```
def generate_summary(transcription):
    # Format the prompt with the transcription
    prompt = f"{transcription}\n\nGive me the summary, speakers, key discussions, and action items with owners"
    
    # Call Bedrock for summarization
    response = bedrock_runtime.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
        body=json.dumps({
            "prompt": prompt,
            "max_tokens_to_sample": 4096,
            "temperature": 0.7,
            "top_p": 0.9,
        })
    )
    
    # Extract and return the summary
    result = json.loads(response.get('body').read())
    return result.get('completion')
```

本方案的关键组件之一是 PII 自动脱敏。我们使用 Amazon Bedrock Guardrails 实现这一点，以符合隐私法规要求：

```
def apply_guardrail(bedrock_runtime, content, guardrail_id):
# Format content according to API requirements
formatted_content = [{"text": {"text": content}}]

# Call the guardrail API
response = bedrock_runtime.apply_guardrail(
guardrailIdentifier=guardrail_id,
guardrailVersion="DRAFT",
source="OUTPUT",  # Using OUTPUT parameter for proper flow
content=formatted_content
)

# Extract redacted text from response
if 'action' in response and response['action'] == 'GUARDRAIL_INTERVENED':
if len(response['outputs']) > 0:
output = response['outputs'][0]
if 'text' in output and isinstance(output['text'], str):
return output['text']

# Return original content if redaction fails
return content
```

检测到 PII 时，会用类型指示符（例如 {PHONE} 或 {EMAIL}）替换，确保摘要在保护敏感数据的同时仍然信息充分。

为了管理复杂的处理 pipeline，我们使用 Step Functions 编排这些 Lambda 函数：

```
{
"Comment": "Audio Summarization Workflow",
"StartAt": "TranscribeAudio",
"States": {
"TranscribeAudio": {
"Type": "Task",
"Resource": "arn:aws:states:::lambda:invoke",
"Parameters": {
"FunctionName": "WhisperTranscriptionFunction",
"Payload": {
"bucket": "$.bucket",
"key": "$.key"
}
},
"Next": "IdentifySpeakers"
},
"IdentifySpeakers": {
"Type": "Task",
"Resource": "arn:aws:states:::lambda:invoke",
"Parameters": {
"FunctionName": "SpeakerIdentificationFunction",
"Payload": {
"Transcription.$": "$.Payload"
}
},
"Next": "GenerateSummary"
},
"GenerateSummary": {
"Type": "Task",
"Resource": "arn:aws:states:::lambda:invoke",
"Parameters": {
"FunctionName": "BedrockSummaryFunction",
"Payload": {
"SpeakerIdentification.$": "$.Payload"
}
},
"End": true
}
}
}
```

该工作流确保每一步都成功完成后才进入下一步，并内置了自动错误处理和重试逻辑。

## 测试方案

成功完成部署后，你可以使用 CloudFront URL 测试方案功能。

![音频/视频上传与摘要界面，已完成团队会议录音分析的文件上传](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/29/mlblog-crop.gif)

## 安全考量

安全是本方案的关键方面，我们实施了多项最佳实践以支持数据保护和合规：

- **敏感数据脱敏** – 自动脱敏 PII 以保护用户隐私。
- **细粒度 IAM 权限** – 在 AWS 服务和资源上应用最小权限原则。
- **Amazon S3 访问控制** – 使用严格的存储桶策略，仅允许授权用户和角色访问。
- **API 安全** – 使用 [Amazon Cognito](https://aws.amazon.com/cognito/) 进行用户身份验证来保护 API endpoint（可选但推荐）。
- **CloudFront 保护** – 强制使用 HTTPS 并采用现代 TLS 协议，保障内容安全分发。
- **Amazon Bedrock 数据安全** – Amazon Bedrock（包括 Amazon Bedrock Marketplace）保护客户数据，不会把数据发送给提供商，也不会使用客户数据训练模型。这确保你在使用 AI 能力时专有信息始终安全。

## 清理

为避免产生不必要的费用，使用完毕后请务必删除为本方案预配的资源：

- 删除 Amazon Bedrock guardrail：在 Amazon Bedrock 控制台的导航菜单中，选择 **Guardrails**。选择你的 guardrail，然后选择 **Delete**。
- 删除通过 Amazon Bedrock Marketplace 部署的 Whisper Large V3 Turbo 模型：在 Amazon Bedrock 控制台的导航窗格中选择 **Marketplace deployments **。在 **Managed deployments** 部分，选中已部署的 endpoint 并选择 **Delete**。
- 运行 `cdk destroy` 命令删除 AWS CDK 堆栈，该命令会删除 AWS 基础设施。

## 结语

这个无服务器音频摘要方案展示了组合 AWS 服务以构建成熟、安全且可扩展应用的好处。通过使用 Amazon Bedrock 提供 AI 能力、Lambda 进行无服务器处理、CloudFront 分发内容，我们构建了一套能够高效处理大量音频内容的方案，同时帮助你符合安全最佳实践。

自动 PII 脱敏功能支持满足隐私法规要求，使该方案非常适合医疗健康、金融和法律服务等数据安全至关重要的受监管行业。要开始使用，请在你的 AWS 环境中部署这套架构，以加速你的音频处理工作流。

### 关于作者

![Kaiyin Hu](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/15/kaiyin_pt.jpeg)**Kaiyin Hu** 是 Amazon Web Services 战略客户部的高级解决方案架构师，在企业、初创公司和专业服务领域拥有多年经验。目前，她帮助客户构建云上解决方案，并推动 GenAI 在云上的采用。此前，Kaiyin 在智能家居领域工作，帮助客户集成语音与 IoT 技术。

![Sid Vantair](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/15/image-3-2.png)**Sid Vantair** 是 AWS 的解决方案架构师，负责战略客户。他擅长解决复杂的技术问题，帮助客户克服障碍。工作之外，他珍惜与家人共度的时光，并培养孩子们的好奇心。
