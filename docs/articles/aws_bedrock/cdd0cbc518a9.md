---
vendor: aws_bedrock
title: Introducing Amazon Bedrock AgentCore Identity: Securing agentic AI at scale
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/introducing-amazon-bedrock-agentcore-identity-securing-agentic-ai-at-scale
date: 2025-08-15
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 17a130fd18ae
---

# 推出 Amazon Bedrock AgentCore Identity：大规模加固 agentic AI 安全

我们很高兴推出 [Amazon Bedrock AgentCore Identity](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity.html)，这是一项专为 AI agent 打造的全面的身份与访问管理服务。借助 AgentCore Identity AI，agent 开发人员和管理员可以安全地访问 AWS 资源，以及 GitHub、Salesforce 或 Slack 等第三方工具。AgentCore Identity 提供大规模且稳健的身份与访问管理，使 agent 既可以代表用户访问你的资源或工具，也可以在获得用户预先授权的前提下以自身身份访问，从而尽可能减少对自定义访问控制和身份基础设施开发的需求。

随着组织把 AI agent 部署到生产环境，它们面临一个关键挑战：如何大规模、安全地管理身份与访问。应用需要对调用 AI agent 的用户进行身份验证，而这些 agent 需要访问多种工具和服务、维护审计轨迹，并集成到现有的企业身份系统中——同时还要避免数据泄露，并持续符合组织要求。当 agent 跨异构系统运行、代表不同用户行事，并且需要访问 AWS 与外部第三方服务中的资源和工具时，这些要求会成倍地复杂化。

本文探讨 AgentCore Identity 如何解决这些 agentic AI 安全挑战。我们首先分析企业 AI agent 的核心身份与安全需求，然后深入介绍 AgentCore Identity 用于管理 agent 身份与凭据的架构。接着通过一个客户支持的实际用例演示如何实现安全的 agent 身份验证，最后给出实现大规模企业级安全的最佳实践。

## 规模化场景下的 agentic AI 安全

为企业部署构建安全的 AI agent 会带来独特的身份与访问管理挑战，这些挑战是传统应用安全模型在设计之初并未考虑到的。下图展示了典型 agentic 工作流中需要通过身份验证和授权来实现访问控制的各个环节。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/14/ML-19464-image-1.png)

让我们来看看让 agentic AI 系统格外复杂的那些具体安全需求：

### 入站身份验证：谁可以访问 agent？

当用户或应用调用 AI agent 时，你需要验证他们的身份，并确定他们有哪些操作权限。这种入站身份验证必须支持多种模式：

- **用户身份验证**：验证通过 Web 应用或 API 访问 agent 的人类用户
- **服务身份验证**：校验需要与你的 agent 通信的其他服务或 agent
- **多租户隔离**：阻止来自不同组织的用户访问彼此的数据

### 出站身份验证：agent 可以访问什么？

AI agent 需要与各种资源和工具交互才能完成任务。这种出站身份验证有其自身的挑战：

- **代表用户行事**：agent 经常需要在具备相应权限的情况下访问用户专属的资源（例如其 Google Drive 或 Slack 工作区）
- **服务间身份验证**：agent 可能需要自己的凭据来访问共享资源或 API
- **token 管理**：安全地存储和管理 OAuth 访问 token、API key 及其他凭据，避免它们暴露给潜在威胁

### 企业集成要求

现代企业在身份基础设施上投入巨大，AI agent 必须能够无缝集成：

- **身份提供商兼容性**：支持 Amazon Cognito、Okta 或 Microsoft Entra ID（原 Azure Active Directory）等现有系统。
- **标准协议**：使用 OAuth 2.0、OpenID Connect 及其他行业标准
- **稳健的访问控制**：实施最小权限访问与持续验证

### 合规与可审计性

对金融服务公司及其他受监管行业而言，agent 的每一个操作都必须可追溯：

- **完整的审计轨迹**：记录谁在什么时间访问了什么，以及代表谁访问
- **数据隔离**：避免不同用户的数据相互串扰
- **法规合规**：满足数据保护和隐私法规的各项要求

如果没有专门打造的解决方案，开发者要花上几个月来构建自定义身份验证系统、实现 token vault、管理 OAuth 流程并创建审计机制——同时还要努力维持安全最佳实践。

## AgentCore Identity：主要功能

AgentCore Identity 通过提供集中化的能力来应对上述大部分挑战：管理 agent 身份、保护凭据，并通过 Sigv4、标准化的 OAuth 2.0 流程和 API key 支持与 AWS 及第三方服务的无缝集成。

AgentCore Identity 提供的主要组件包括：

- **Agent 身份目录：** 通过统一的目录服务创建、管理和组织 agent 与 workload 身份，该目录服务是组织内 agent 身份的唯一可信来源。
- **Agent 授权器：** 校验某个用户或服务是否被允许调用 agent。
- **资源凭据提供程序：** 存储 agent 获取凭据以访问下游资源服务器所需的配置。它随后会检索 Google、GitHub 等下游资源服务器的凭据以便访问它们，例如从 Gmail 获取邮件或向 Google Calendar 添加会议。
- **资源 token vault：** 存储用户的 OAuth 访问 token，并允许 agent 安全地取回它们，以代表用户执行操作，同时减少不必要的用户授权。

AgentCore Identity 实现了身份验证与授权控制，对每个请求独立校验，无论请求来源如何，访问尝试都需要经过明确验证。它能与 AWS 服务无缝集成，同时也让 agent 能够安全地访问外部工具和服务。你可以用 AgentCore Identity 保护对 agent 的访问，也可以保护 agent 代表用户所访问的资源或工具，如下图所示。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/14/ML-19464-image-2.png)

无论你构建的是简单的自动化脚本还是复杂的多 agent 系统，AgentCore Identity 都能提供身份基础，帮助你的应用安全、高效地运行。

### 独立的 agent 身份

每个 agent 都会获得一个唯一身份，并附带相关元数据（例如名称、Amazon Resource Name（ARN）、OAuth 返回 URL、创建时间、最后更新时间），可以在整个组织中集中管理。这种 workload 身份方案意味着 agent 是安全架构中的一等公民，而不只是冒充用户的应用。

### 双重身份验证模型

AgentCore Identity 实现了双重身份验证方案：

- **入站身份验证**：校验尝试调用 agent 的用户和应用；支持用于 AWS 身份验证的 [AWS Identity and Access Management (IAM)](https://aws.amazon.com/iam) 凭据（SigV4）；与 OAuth 2.0 或 OpenID Connect 身份提供商集成；提供 JSON Web Token（JWT）token 校验
- **出站身份验证**：使 agent 能够安全地访问资源；token vault 为存储 OAuth 2.0 访问 token、OAuth 客户端凭据和 API key 提供安全保障，并对静态存储和传输中的数据全面加密；同时支持双边 OAuth（机器对机器）和三边 OAuth（代表用户）；为 GitHub、Slack、Salesforce 等热门服务预置了与授权提供商的集成。

### 安全 token vault

安全 token vault 是 AgentCore Identity 安全模型中的关键要素：

- **加密**：凭据使用客户托管的 [AWS Key Management Service (AWS KMS)](https://aws.amazon.com/kms) 密钥加密
- **访问控制**：凭据绑定到特定的 agent-用户组合
- **零 token 共享**：避免凭据在用户或 agent 之间被交叉访问

### 无缝的 SDK 集成

通过 `@requires_access_token` 和 `@requires_api_key` 等声明式注解与 AgentCore SDK 无缝集成，自动处理凭据的获取与注入，减少样板代码和潜在的安全漏洞。

## 如何开始

让我们通过一个实际示例，看看如何部署一个开发者生产力 agent，帮助工程团队管理 GitHub 仓库、跟踪 issue 并简化开发工作流，如下图所示。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/14/ML-19464-image-3.png)

这个 agent 会用 OAuth 对开发者进行身份验证，然后访问 GitHub，代表他们管理仓库、跟踪 issue 并审查 pull request。你可以在[这个 notebook](https://github.com/awslabs/amazon-bedrock-agentcore-samples/blob/main/01-tutorials/03-AgentCore-identity/06-Outbound_Auth_Github/runtime_with_strands_and_egress_github_3lo.ipynb) 中查看完整示例。

### 前置条件

- 具有 Amazon Bedrock AgentCore 访问权限的 AWS 账户。更多信息请参阅 [AgentCore Runtime 的权限](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-permissions.html)文档。
- Python 3.10 或更高版本
- 已安装 Docker 或 Finch
- 已配置 GitHub OAuth App（参见 [GitHub 文档](https://docs.github.com/en/developers/apps/building-oauth-apps/creating-an-oauth-app)）
- 对 [OAuth 2.0](https://oauth.net/2/) 有基本了解

### 步骤 1：设置身份提供商

首先，为 agent 用户配置身份提供商。你可以使用任意兼容 OAuth 2.0 的身份提供商。在本示例中，我们使用 [Amazon Cognito](https://aws.amazon.com/cognito)，并配合 [notebook](https://github.com/awslabs/amazon-bedrock-agentcore-samples/blob/main/01-tutorials/03-AgentCore-identity/06-Outbound_Auth_Github/runtime_with_strands_and_egress_github_3lo.ipynb) 中提供的便捷脚本。之后，我们可以直接映射所需属性，也可以借助 [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/) 来安全地存储和检索这些信息。

```
from bedrock_agentcore_starter_toolkit import Runtime
from boto3.session import Session
boto_session = Session()
region = boto_session.region_name
# Configure your Cognito User Pool
discovery_url = f'https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/openid-configuration'
client_id = 'your-cognito-app-client-id'
```

### 步骤 2：创建使用 JWT 身份验证的 agent

把 agent runtime 配置为接受来自身份提供商的 JWT token：

```
from bedrock_agentcore_starter_toolkit import Runtime
agentcore_runtime = Runtime()
response = agentcore_runtime.configure(
    entrypoint="github_agent.py",
    auto_create_execution_role=True,
    auto_create_ecr=True,
    requirements_file="requirements.txt",
    region=region,
    agent_name="strands_agent_github",
    authorizer_configuration={
        "customJWTAuthorizer": {
            "discoveryUrl": discovery_url,
            "allowedClients": [client_id]
        }
    }
)
```

### 步骤 3：为 GitHub 配置 OAuth 凭据提供程序

设置 OAuth 提供程序，使你的 agent 能够访问 GitHub 服务。AgentCore Identity 为热门服务提供了预置配置：

```
import boto3
agentcore_client = boto3.client('bedrock-agentcore-control', region_name=region)
response = agentcore_client.create_oauth2_credential_provider(
    name='github-provider',
    credentialProviderVendor='GithubOauth2',
    oauth2ProviderConfigInput={
        'githubOauth2ProviderConfig': {
            'clientId': "<your-github-client-id>",
            'clientSecret': "<your-github-client-secret>"
        }
    }
)
```

### 步骤 4：实现自动处理 token 的 agent

使用 AgentCore SDK 注解创建工具，自动处理三边 OAuth 流程。`@requires_access_token` 装饰器管理整个 OAuth 流程，包括用户授权。你可以在[这个 notebook](https://github.com/awslabs/amazon-bedrock-agentcore-samples/blob/main/01-tutorials/03-AgentCore-identity/06-Outbound_Auth_Github/runtime_with_strands_and_egress_github_3lo.ipynb) 中查看此示例的完整代码，下面的代码片段重点展示了关键部分：

```
from bedrock_agentcore import BedrockAgentCoreApp
from bedrock_agentcore.identity.auth import requires_access_token
from strands import Agent, tool

# Global token storage
github_access_token = None

app = BedrockAgentCoreApp()

@tool
def inspect_github_repos() -> str:
    """Tool that requires authentication to access private repos."""
    global github_access_token
    # Check if authentication is required
    if not github_access_token:
        return "Authentication required for GitHub access"
    # Use token for authenticated API calls
    headers = {"Authorization": f"Bearer {github_access_token}"}
    ### ... code for making authenticated requests with GitHub APIs ...

async def agent_task(user_message: str) -> None:
    """Main agent logic with authentication handling."""
    global github_access_token
    # Initial agent call
    response = agent(user_message)
    # Check if authentication is needed
    if "Authentication required" in str(response.message):
        # Trigger authentication flow
        github_access_token = await need_token_3LO_async(access_token='')
        # Retry with authentication
        response = agent(user_message)

@requires_access_token(
    provider_name="github-provider",
    scopes=["repo", "read:user"],
    auth_flow='USER_FEDERATION',
    force_authentication=True,
)
async def need_token_3LO_async(*, access_token: str) -> str:
    """Handle OAuth authentication flow."""
    global github_access_token
    github_access_token = access_token
    return access_token

# Create agent with authentication-aware tool
agent = Agent(
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    tools=[inspect_github_repos]
)
@app.entrypoint
async def agent_invocation(payload):
    """Main entrypoint."""
    user_message = payload.get("prompt", "...")
    await agent_task(user_message)
	
    ### ... Code for returning responses ...
```

### 步骤 5：部署并测试

使用 AgentCore CLI 部署你的 agent：

```
bedrock-agentcore runtime launch
```

当用户携带 JWT token 调用你的 agent 时，AgentCore Identity 将：

- 校验传入的 JWT token
- 确定用户身份
- 确定自身身份，并为该用户与 agent 的组合获取 workload 访问 token
- 当 agent 需要访问 GitHub 时，使用该 workload 访问 token 提供授权 URL，作为三边 OAuth 流程的一部分自动完成用户授权
- 安全地在 vault 中存储和检索 token
- 把 token 注入到你的函数调用中

我们来看看这个示例中的应用会是什么样子。

如你所见，agent 无需暴露凭据，也无需手动管理 token，就能无缝地对用户进行身份验证并访问他们的 GitHub 仓库。包括用户授权和安全 token 存储在内的整个 OAuth 流程，都由 AgentCore Identity 自动处理。

### 清理

完成本示例后，你可以用下面的命令清理资源，避免账户产生不必要的费用。请记得把 provider ID 替换成你自己的 ID。

```
# Delete the agent runtime
bedrock-agentcore runtime delete --agent-name github-support-agent

# Delete the OAuth credential provider
aws bedrock-agentcore-identity delete-oauth-credential-provider \
    --provider-id <provider-id>
```

## 与 AgentCore 环境及身份提供商的集成

AgentCore Identity 可与更广泛的 AgentCore 环境以及你现有的身份基础设施无缝协作。

### AgentCore 服务集成

- **AgentCore Runtime**：由 AgentCore Identity 提供支持的 Runtime 会为 AI agent 分配独立身份，并与 Okta、Microsoft Entra ID 或 Amazon Cognito 等企业身份提供商无缝集成。
- **AgentCore Gateway**：使用 Gateway 通过 Model Context Protocol（MCP）暴露工具时，AgentCore Identity 负责处理传入的 agent 请求和传出的工具调用的身份验证

### 身份提供商兼容性

AgentCore Identity 支持兼容 OAuth 2.0 或 OpenID Connect 的身份提供商，以及可通过 API key 访问的提供商。例如 Amazon Cognito、Okta 和 Microsoft Entra ID 等。

通过 AgentCore Runtime 或 AgentCore Gateway 使用 AgentCore Identity 的客户，无需为使用 AgentCore Identity 支付任何额外费用。其他场景下，你只需为实际用量付费，费用依据 agent 向 AgentCore Identity 请求 OAuth token 或 API key 的次数计算。有关定价的更多信息，请参阅 [AgentCore 公开定价](https://aws.amazon.com/bedrock/agentcore/pricing/)。

## 安全考量与最佳实践

实施 AgentCore Identity 时，请遵循以下安全最佳实践：

### 最小权限原则

通过把 agent 的访问限制在仅必需的资源和能力上，将安全风险降到最低：

- 仅授予 agent 所需的最小权限
- 定期审计和复查 agent 的权限

### 基于 agent 与用户身份的访问控制

为人类用户和 AI agent 建立清晰的身份验证与管理规程：

- 以可验证的形式提供用户身份
- 管理 agent 身份

### Token 管理

通过恰当的 token 生命周期管理来保护身份验证凭据：

- 启用自动 token 刷新，尽量减少凭据暴露
- 对敏感操作使用 `force_authentication=True`
- 实施适合你的用例的 token 过期策略

### 审计与监控

保持对 agent 活动的可见性，以便发现异常并确保符合组织要求：

- 为 agent 操作启用 [Amazon CloudWatch](https://aws.amazon.com/cloudwatch) 日志记录
- 为异常的身份验证模式设置告警
- 定期审查审计日志以确保合规

### 多租户安全

对于软件即服务（SaaS）提供商和多租户环境：

- 为每个租户配置独立的凭据提供程序
- 使用租户专属的 JWT claim 进行校验
- 在 agent 逻辑中实施额外的授权校验

## 结论与未来展望

Amazon Bedrock AgentCore Identity 改变了组织大规模保护 AI agent 的方式。通过提供专门打造的身份与访问管理，它省去了数月的自定义开发工作，同时带来企业级安全。该服务的双重身份验证模型、安全 token vault，以及与现有身份提供商的无缝集成，使组织能够部署可跨组织边界安全运行、可访问多种资源的 agent。随着 AI agent 在企业环境中日益普及，对稳健身份与访问管理的需求只会不断增长。AgentCore Identity 为这一未来奠定了基础，使组织能够构建不仅智能，而且安全、合规且值得信赖的 agent。

### 入门资源

准备好用 AgentCore Identity 保护你的 AI agent 了吗？以下是你的下一步：

- **查阅文档**：访问 [Amazon Bedrock AgentCore 文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)
- **试用示例**：查看包含完整示例的 [GitHub 仓库](https://github.com/awslabs/amazon-bedrock-agentcore-samples)
- **免费预览**：在 2025 年 9 月 16 日之前，你可以免费试用 AgentCore 的各项服务：[推出 Amazon Bedrock AgentCore：以任意规模安全部署和运营 AI agent（预览）| AWS News Blog](https://aws.amazon.com/blogs/aws/introducing-amazon-bedrock-agentcore-securely-deploy-and-operate-ai-agents-at-any-scale/)

立即使用 Amazon Bedrock AgentCore Identity 构建安全、可扩展的 AI agent。把你的概念验证转化为满足最高企业安全标准的生产级系统。

### 关于作者

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/14/ML-19464-image-4-100x109.png)Rahul Sharma** 是 Amazon Web Services 的资深技术产品经理，累计拥有 5 年以上的产品管理经验，涵盖客户身份与访问管理（CIAM）、基础设施即代码（IaC），以及最近专注的 agent 身份领域。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/14/ML-19464-image-5-100x125.png)Fei Yuan** 是 AWS 的首席工程师。在 20 多年的职业生涯中，Fei 带领不同团队完成了 Amazon 与 AWS 上的多个项目，例如 Amazon Lending Marketplace、Amazon Payment Services、Alexa ML Secure Computing、Amazon DataZone、Amazon SageMaker 数据治理以及 Amazon Cognito。最近，他带领团队推出了 Amazon Bedrock AgentCore Identity 服务。如今他专注于设计和实现 agent 身份、workload 身份以及客户身份与访问管理领域的 AWS 产品。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/06/Satveer-1.jpg)Satveer Khurpa** 是 Amazon Web Services 的 Amazon Bedrock 全球专项解决方案架构师，专精于 Amazon Bedrock 安全。在这一职位上，他运用自己在云架构方面的专长，为不同行业的客户开发创新的生成式 AI 解决方案。Satveer 凭借对生成式 AI 技术和安全原则的深入理解，设计可扩展、安全且负责任的应用程序，在保持稳健安全态势的同时，帮助客户发掘新的业务机会并创造切实价值。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/10/28/rodzanto.jpg)Antonio Rodriguez** 是 Amazon Web Services 的首席生成式 AI 专项解决方案架构师。他帮助各种规模的公司应对挑战、拥抱创新，并借助 Amazon Bedrock 创造新的业务机会。工作之外，他喜欢与家人共度时光，并与朋友一起运动。
