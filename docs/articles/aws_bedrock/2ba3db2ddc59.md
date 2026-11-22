---
vendor: aws_bedrock
title: Migrating multi-model AI agents to Amazon Bedrock AgentCore runtime
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/migrating-multi-model-ai-agents-to-amazon-bedrock-agentcore-runtime
date: 2026-09-18
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 3cf19548fe85
---

# 将多模型 AI agent 迁移到 Amazon Bedrock AgentCore runtime

构建多模型 agentic AI 应用的组织面临着日益增长的基础设施复杂性。为多种模型类型管理容器编排、扩缩容策略、身份和可观测性，会带来额外的运维开销。团队往往在基础设施上花费的时间比在 agent 逻辑开发上还多。

在自管理基础设施（例如 [Amazon Elastic Container Service（Amazon ECS）](https://aws.amazon.com/ecs/) 搭配 [AWS Fargate](https://aws.amazon.com/fargate/)）上运行 agentic 框架的开发者，对其部署配置拥有完全控制权。随着 agentic 工作负载的演进和扩展，团队可能会选择采用提供内置会话管理、身份和可观测性的托管 runtime。

[Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) 是一个用于大规模构建、连接和优化 agent 的平台，支持任何框架和模型。AgentCore runtime 是它的托管部署能力，负责容器生命周期、扩缩容、身份和可观测性，因此你可以专注于 agent 代码。

在之前的一篇文章中，我们展示了如何在自管理基础设施上构建一个带多模型编排的医疗 AI agent（见[在 AWS 上使用 Hugging Face smolagents 多模型框架构建 Agentic AI](https://aws.amazon.com/blogs/machine-learning/agentic-ai-with-multi-model-framework-using-hugging-face-smolagents-on-aws/)）。在本文中，我们将展示如何把这个多模型 agent 迁移到 Amazon Bedrock AgentCore runtime。这次迁移减少了基础设施管理工作，同时保留了 agent 的能力，包括三模型编排和向量增强的知识检索。

## 解决方案概览

本解决方案把一个多模型医疗 AI agent 迁移到 Amazon Bedrock AgentCore runtime，同时保留现有的 agent 逻辑。该 agent 借助向量增强的知识检索，在三个模型后端之间处理医疗查询，所有这些都运行在单个由 AgentCore 管理的容器内。你可以把每个查询导向适合该任务的模型后端。像 [Amazon SageMaker AI](https://aws.amazon.com/sagemaker/ai/) 上的 [BioM-ELECTRA-Large-SQuAD2](https://huggingface.co/sultan/BioM-ELECTRA-Large-SQuAD2) 这样的领域专用模型负责处理专业的生物医学查询，而像 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 上 [Meta 的 Llama 3.1 70B Instruct](https://aws.amazon.com/bedrock/meta/) 这样的基础模型（FM）负责更广泛的医学推理。这种方法帮助医疗团队应对多种类型的查询，同时降低管理底层基础设施的运维开销。

上一篇文章中的独立版本部署在 Amazon ECS 与 AWS Fargate 上，其容器编排、扩缩容、身份和可观测性都由用户自行配置。AgentCore 版本用 AgentCore runtime 的装饰器模式包装了相同的 agent 逻辑，由 AgentCore runtime 自动处理这些运维关注点。

[Hugging Face smolagents](https://huggingface.co/docs/smolagents/en/index) 是一个开源 Python 库，旨在用几行代码构建和运行 agent。本解决方案使用 Hugging Face smolagents 框架作为参考实现，说明 AgentCore runtime 支持任何 agentic 框架。采用自带 agent（bring-your-own，BYO）的方式，你可以把已有的 agent 代码部署到 AgentCore runtime，而无需重写或适配特定框架。

**注意：** 本解决方案是用于演示的示例实现。处理医疗或其他敏感查询的生产部署会把 Amazon Bedrock Guardrails 用于内容过滤和 grounding 校验，作为标准控制措施。

## 架构

本解决方案包含以下服务和功能：

- Amazon Bedrock AgentCore runtime，用于托管的 agent 容器部署、扩缩容、身份和可观测性。
- Amazon Bedrock 搭配 Meta 的 Llama 3.1 70B Instruct，用于复杂的医学推理。有关各 AWS 区域的模型可用性，请参阅 [Amazon Bedrock 中各 AWS 区域支持的模型](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html)。
- Amazon SageMaker AI 搭配 BioM-ELECTRA-Large-SQuAD2，用于专业的生物医学查询和托管自动扩缩容。
- [Amazon OpenSearch Service](https://aws.amazon.com/opensearch-service/)，用于向量相似度匹配以及基于医学知识索引的上下文知识检索。
- 带 BioM-ELECTRA-Large-SQuAD2 的容器化模型服务器，用于自托管模型部署。
- [AWS Identity and Access Management（IAM）](https://aws.amazon.com/iam)，用于安全和访问控制。

**注意：** 上一篇文章（独立版本）使用的是 [Anthropic 的 Claude 3.5 Sonnet V2](https://aws.amazon.com/bedrock/anthropic/)。本文使用 Meta 的 Llama 3.1 70B Instruct，以说明 AgentCore runtime 与模型无关。模型选择是一项实现决策，而不是硬性要求。

下图展示了解决方案架构，以及该 agent 如何跨三个模型后端进行编排。

![架构图：用户通过客户端 Web 界面连接到 Amazon Bedrock AgentCore runtime，后者托管一个包含 Hugging Face smolagents 框架和 AgentCore runtime 装饰器的医疗 agent 容器。该 agent 连接到三个模型后端（Amazon SageMaker AI、Amazon Bedrock 和容器化模型服务器）以及用于向量知识检索的 Amazon OpenSearch Service。Hugging Face Hub 为 SageMaker AI 和容器化服务器提供模型。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/09/08/ML-21510-1.png)

图 1：Amazon Bedrock AgentCore runtime 上的多模型医疗 agent 架构

客户端 Web 界面连接到 Amazon Bedrock AgentCore runtime，后者托管医疗 agent 容器。该容器使用 Hugging Face smolagents 框架和 AgentCore runtime 装饰器。AgentCore runtime 提供内置的身份和可观测性。该 agent 在三个模型后端之间进行编排：带 BioM-ELECTRA 的 Amazon SageMaker AI、带 Meta 的 Llama 3.1 70B Instruct 的 Amazon Bedrock，以及带 BioM-ELECTRA 的容器化模型服务器。解决方案还包括用于向量增强知识检索的 Amazon OpenSearch Service。

本解决方案支持多种部署选项，每个后端针对不同场景做了优化：

- Amazon SageMaker AI，用于使用 [Hugging Face Hub](https://huggingface.co/models) 模型的托管端点并支持自动扩缩容。
- Amazon Bedrock，用于无服务器访问基础模型，并通过 AWS API 进行复杂推理。
- 容器化模型服务器，用于自托管模型部署以及来自 Hugging Face Hub 的工具集成（可部署在 Amazon ECS、[Amazon Elastic Kubernetes Service（Amazon EKS）](https://aws.amazon.com/eks/) 或其他容器环境中）。

这三个后端都实现了 [Hugging Face Messages API 兼容性](https://huggingface.co/docs/text-generation-inference/en/messages_api)，无论选择哪种模型服务，都提供一致的请求与响应格式。

完整实现见 sample-healthcare-agent-with-agentcore-on-aws 的 [GitHub](https://github.com/aws-samples/sample-healthcare-agent-with-agentcore-on-aws) 仓库。

## 将 agent 迁移到 AgentCore runtime

本节将介绍如何使用 AgentCore CLI 把现有的医疗 AI agent 迁移到 Amazon Bedrock AgentCore runtime。

### 先决条件

在部署解决方案之前，你需要以下条件：

- 一个 AWS 账户，可访问 Amazon Bedrock AgentCore runtime，并具备创建 [IAM 角色](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html) 和 [Amazon OpenSearch Service 域](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/createupdatedomains.html) 的相应权限。
- 已安装并配置 [AWS Command Line Interface（AWS CLI）](https://aws.amazon.com/cli) 2.0 或更高版本。
- [Node.js](https://nodejs.org/) 20 或更高版本（部署 CLI 需要）。
- 已安装 [AWS Cloud Development Kit（AWS CDK）](https://docs.aws.amazon.com/cdk/v2/guide/getting-started.html)。
- 已安装 [AgentCore CLI](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-cli.html)。
- [Python](https://www.python.org/downloads/) 3.10 或更高版本，用于运行部署脚本。
- 已安装并正在运行 [Docker](https://docs.docker.com/get-docker/)（代码执行隔离需要）。
- 在你的 AWS 区域中可以访问 Amazon Bedrock 模型、Amazon SageMaker AI 和 Amazon OpenSearch Service 域，并具备创建和管理资源所需的相应 IAM 权限。
- 已安装 [bedrock-agentcore Python SDK](https://github.com/aws/bedrock-agentcore-sdk-python)。
- 在本实现中，我们使用 [Python 3.10+](https://www.python.org/downloads/)、[smolagents 框架](https://huggingface.co/docs/smolagents/en/index)、[transformers 4.55.0+](https://pypi.org/project/transformers/) 和 [boto3](https://pypi.org/project/boto3/)。

### AgentCore runtime 概念

Amazon Bedrock AgentCore runtime 使用装饰器模式包装你的 agent 逻辑。关键组件包括：

- [BedrockAgentCoreApp](https://github.com/aws/bedrock-agentcore-sdk-python) —— 初始化 AgentCore 应用。
- `@app.entrypoint` —— 装饰 AgentCore runtime 在请求到达时调用的函数。
- `app.run()` —— 启动 AgentCore runtime 服务器。

以下代码展示了 AgentCore 集成模式：

```
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint
def healthcare_agent_entrypoint(payload):
    user_input = payload.get("prompt", "")
    model_type = payload.get("model_type", "sagemaker")
    # Your existing agent logic here
    agent = TripleHealthcareAgent(vector_store=vector_store)
    response = agent.run(user_input, model_type=model_type)
    return str(response)

if __name__ == "__main__":
    app.run()
```

装饰器与 return 语句之间的 agent 代码与独立版本保持一致。AgentCore runtime 会自动处理容器生命周期、扩缩容、身份和可观测性。

### 准备项目

使用 AgentCore CLI 创建一个 AgentCore 项目，并添加你现有的 agent。

**安装 AgentCore CLI：**

```
npm install -g @aws/agentcore
```

**创建一个新的 AgentCore 项目：**

```
agentcore create --project-name healthcareagent --no-agent --build Container --language Python --protocol HTTP --model-provider Bedrock --memory none
```

**把你现有的 agent 作为自带（BYO）agent 添加：**

```
agentcore add agent --name healthcare_agentcore --type byo --build Container --language Python --protocol HTTP --network-mode PUBLIC --code-location ./agent-code --entrypoint healthcare_agentcore.py --framework Strands --model-provider Bedrock
```

**注意：** `--framework` 参数指定的是 CLI 模板。实际的 agent 代码使用 Hugging Face smolagents，无论选择哪个模板，它都与 AgentCore runtime 兼容。

### 准备容器

- 在你的 agent 代码目录中创建 `pyproject.toml` 来定义依赖：  `[project] name = "healthcare-agentcore" version = "1.0.0" requires-python = ">=3.10" dependencies = [ "smolagents>=1.24.0", "transformers>=4.55.0", "boto3>=1.37.0", "opensearch-py>=3.1.0", "requests-aws4auth>=1.3.1", "bedrock-agentcore>=0.1.0", "numpy>=1.26.0", "requests>=2.32.0", "docker>=7.1.0", ]`
- 创建 `Dockerfile`：  `FROM public.ecr.aws/docker/library/python:3.12-slim RUN pip install --no-cache-dir uv WORKDIR /app COPY pyproject.toml ./ RUN uv pip install --system -r pyproject.toml COPY . . EXPOSE 8080 CMD ["python", "healthcare_agentcore.py"]`
- 创建 `.dockerignore`，把镜像大小控制在 2 GB 限制以内：  `venv/ .venv/ __pycache__/ .git/ *.pyc`

### 部署到 AgentCore runtime

项目配置完成后，你可以用一条 CLI 命令部署 agent。

**部署 agent：**

```
agentcore deploy -y
```

CLI 会构建容器、把它推送到 Amazon Elastic Container Registry（Amazon ECR），并创建 AgentCore runtime agent。部署大约需要 10–15 分钟。

### 测试已部署的 agent

你可以用两种方式测试已部署的 agent：使用 AgentCore CLI，或用 boto3 以编程方式调用。

**使用 AgentCore CLI 调用 agent：**

```
agentcore invoke --prompt '{"prompt": "What are the side effects of metformin?", "model_type": "llama"}'
```

**或者用 boto3 以编程方式调用：**

这条路径使用 boto3 SDK 直接调用与 CLI 相同的已部署 agent。`agentRuntimeArn` 标识你部署的 agent，`contentType` 指定请求格式，`payload` 携带 prompt 和模型选择。

```
import boto3, json

client = boto3.client('bedrock-agentcore', region_name='us-west-2')

payload = json.dumps({
    "prompt": "What are the side effects of metformin?",
    "model_type": "llama"
})

response = client.invoke_agent_runtime(
    agentRuntimeArn='<your-agent-runtime-arn>',
    contentType='application/json',
    accept='application/json',
    payload=payload.encode('utf-8')
)

result = response['response'].read().decode('utf-8')
print(result)
```

## 与自管理部署的关键差异

独立版本和 AgentCore runtime 版本以不同方式部署同一个 agent。以下各节说明每条路径分别提供什么。

### Amazon ECS 与 AWS Fargate 部署

独立版本运行在 Amazon ECS 与 AWS Fargate 上。你需要定义 ECS 任务定义和服务配置、设置自动扩缩容策略、为每个服务配置 IAM 角色，并通过 [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/) 设置可观测性。部署过程包括 Docker 构建、推送至 Amazon ECR 以及更新 ECS 服务。这条路径让你完全控制容器配置、网络和扩缩容行为。agent 代码位于 `healthcare_agentcore.py` 中，与 Amazon Bedrock、Amazon SageMaker AI 和容器化后端集成，并使用 Amazon OpenSearch Service 进行向量搜索。

### Amazon Bedrock AgentCore runtime 部署

AgentCore runtime 版本用 AgentCore 装饰器模式运行相同的 `healthcare_agentcore.py` agent 代码。AgentCore runtime 提供容器编排、基于会话的扩缩容、通过 IAM 集成实现的身份管理，以及通过内置追踪和日志实现的可观测性。部署只需一条命令（`agentcore deploy`）。模型集成（Amazon Bedrock、Amazon SageMaker AI、容器化后端）和向量搜索（Amazon OpenSearch Service）与独立版本保持一致。

两种部署方式各有明显优势。Amazon ECS 与 AWS Fargate 让你完全控制容器配置、网络和扩缩容策略，适合已经具备容器运维经验或有特定基础设施要求的团队。Amazon Bedrock AgentCore runtime 适合偏好托管基础设施、希望把主要精力放在 agent 逻辑开发上的团队。

无论采用哪条部署路径，从独立版本迁移到 AgentCore runtime 时，以下要素保持不变：

- 核心 agent 逻辑（`BedrockAgentCoreApp` 装饰器 + 现有代码）。
- 跨 Amazon Bedrock、Amazon SageMaker AI 和容器化后端的多模型编排。
- 使用 Amazon OpenSearch Service 的向量增强知识检索。
- 跨模型后端的 Hugging Face Messages API 兼容性。

## 清理

为避免产生后续费用，请在不再需要时删除你创建的资源。如果你计划继续使用已部署的 agent，则无需任何操作。

- **移除 AgentCore runtime agent：
**首先，从本地配置中移除所有资源：   `agentcore remove all`  然后再次部署以拆除 AWS 资源：  `agentcore deploy`
- **删除 Amazon SageMaker AI 端点：**  `aws sagemaker delete-endpoint --endpoint-name healthcare-agentcore-endpoint-1 --region us-west-2`
- **删除 Amazon OpenSearch Service 域：**  `aws opensearch delete-domain --domain-name healthcare-vector-store --region us-west-2`

## 结论

在本文中，我们展示了如何把一个多模型医疗 AI agent 从自管理的 Amazon ECS 与 AWS Fargate 基础设施迁移到 Amazon Bedrock AgentCore runtime。这次迁移不需要修改核心 agent 逻辑。同一个 `healthcare_agentcore.py` 文件在 Amazon Bedrock、Amazon SageMaker AI 和容器化模型服务器之间进行编排。它通过增加 AgentCore 装饰器模式（`BedrockAgentCoreApp`、`@app.entrypoint` 和 `app.run()`）运行在 AgentCore runtime 上。对医疗团队而言，这种模式把专业的生物医学查询导向领域专用模型，例如 Amazon SageMaker AI 上的 BioM-ELECTRA-Large-SQuAD2；它把更广泛的医学推理路由到基础模型，例如 Amazon Bedrock 上 Meta 的 Llama 3.1 70B Instruct。这些后端共同支持多种类型的查询。

对于选择托管基础设施的团队，AgentCore runtime 负责容器编排、扩缩容、身份管理和可观测性，你可以转而专注于 agent 逻辑开发。这种与框架无关的设计支持多种模型和 agentic 框架的组合，使这一迁移模式可适用于医疗、金融服务和制造业等各个行业。

要开始使用，请克隆 sample-healthcare-agent-with-agentcore-on-aws 的 [GitHub](https://github.com/aws-samples/sample-healthcare-agent-with-agentcore-on-aws) 仓库，并按本文的部署步骤操作。要了解本文所迁移的独立实现，请参阅[在 AWS 上使用 Hugging Face smolagents 多模型框架构建 Agentic AI](https://aws.amazon.com/blogs/machine-learning/agentic-ai-with-multi-model-framework-using-hugging-face-smolagents-on-aws/)。如果对 Amazon Bedrock AgentCore 的入门有疑问，请与 [AWS 生成式 AI 专家](https://pages.awscloud.com/global-ln-gc-400-ai-contact-us.html)交流。

## 延伸阅读

- [AWS 上的 Agentic AI —— 用 AWS 构建、部署和扩展 AI agent](https://builder.aws.com/learn/topics/agentic-ai)
- [用 Amazon Bedrock AgentCore 让 agent 成为现实：现已正式可用](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-is-now-generally-available/)
- [Amazon Bedrock 文档](https://docs.aws.amazon.com/bedrock/)
- [使用 Amazon Bedrock AgentCore Observability 构建可信赖的 AI agent](https://aws.amazon.com/blogs/machine-learning/build-trustworthy-ai-agents-with-amazon-bedrock-agentcore-observability/)

## 关于作者
