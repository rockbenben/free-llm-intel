---
vendor: aws_bedrock
title: ServiceNow 代表与 Bedrock AgentCore Gateway 进行代币交换
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/servicenow-on-behalf-of-token-exchange-with-bedrock-agentcore-gateway
date: 2026-11-03
lang: zh
captured: 2026-11-05
extractor: readability-v1
translator: mt
status: translated
body_sha: 75ee7ef03c38
---

## [人工智能](https://aws.amazon.com/blogs/machine-learning/)

# ServiceNow 代表与 Bedrock AgentCore Gateway 进行代币交换

代表用户与企业 API 交互的 AI 代理需要在整个请求链中维护用户身份。如果没有身份传播，API 调用将作为应用程序本身而不是发起操作的用户到达下游服务。这会破坏审计跟踪，绕过用户级访问控制，并违反最小权限原则。

Amazon Bedrock AgentCore 是一个使用任何框架或模型大规模构建、连接和优化代理的平台。本文介绍如何配置 [AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)（Amazon Bedrock AgentCore 的一项功能），以便与 Microsoft Entra ID 进行代表 (OBO) 令牌交换。然后，AI 代理可以调用​​ [ServiceNow REST API](https://www.servicenow.com/docs/r/api-reference/rest-apis/api-rest.html)，同时保留调用用户的身份。您在网关目标上配置令牌交换，AgentCore Gateway 对每个请求执行交换。该模式可以应用于受 OAuth 保护的其他 REST API。

在生产中，您还可以将身份传播与 Amazon Bedrock Guardrails 配对，以过滤有害内容并验证代理的输入和输出。

## 解决方案概述

该架构涉及通过 AgentCore Gateway 连接的三个关键组件：

- AI 代理应用程序，通过 OAuth 应用程序注册受 Microsoft Entra ID 保护。
- 模型上下文协议 (MCP) 服务器，使用 AgentCore 网关实现，位于代理和 ServiceNow 之间。
- ServiceNow REST API，配置了与 Microsoft Entra ID 绑定的入站 OAuth 集成。

下图显示了端到端解决方案架构，包括 AWS、Microsoft Entra ID 和 ServiceNow 内的组件。

![显示代理、AgentCore Gateway、Microsoft Entra ID 和 ServiceNow 以及它们之间的令牌流的解决方案架构](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-1.png)

图 1：跨 AWS、Microsoft Entra ID 和 ServiceNow 的解决方案架构

如图 1 所示，用户获取 JSON Web 令牌 (JWT) 来调用代理 1. 代理使用作用域为代理自己的应用程序注册的 JWT 令牌向网关进行身份验证 2. 然后，网关使用 OBO 流将该令牌交换为作用域为 ServiceNow API 连接器的新令牌，并保留原始用户的身份 3. ServiceNow 收到一个有效令牌，其“preferred_username”声明映射到现有 ServiceNow 用户并应用该令牌4. 用户对API调用的权限

## OBO 代币交换在此背景下如何运作

当代理调用网关时，它会提供一个 JWT，其中包含与代理的客户端 ID 匹配的“受众”声明（例如，“3ff88e17-XXXX-XXXX-XXXX-XXXXXXXXXXXX”）。然而，ServiceNow 需要一个带有“audience”声明的令牌，与其自己的 API 连接器客户端 ID 匹配（“5d4a7a11-XXXX-XXXX-XXXX-XXXXXXXXXXXX”）。

OBO 流程弥补了这一差距。 AgentCore Gateway 将入站令牌连同代理应用程序的客户端凭据、目标范围和参数“requested_token_use: on_behalf_of”发送到 Entra 令牌端点。 Entra 验证调用用户是否同意委托，然后为 ServiceNow API 发出新令牌，并保持原始用户的声明不变。

## 先决条件

在开始之前，您需要满足以下条件：

- 有权访问 AgentCore Gateway 的 AWS 账户。
- 有权创建[应用程序注册](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app) 的 Microsoft Entra ID 租户。您的帐户至少需要[应用程序开发人员角色](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference#application-developer)才能注册应用程序。
- 具有管理访问权限的 ServiceNow 实例，用于配置入站 OAuth 集成。您可以在 ServiceNow 个人开发人员实例注册页面 [https://developer.servicenow.com/](https://developer.servicenow.com/) 创建 ServiceNow 个人开发人员实例 (PDI)。
- 两个 Entra 应用程序注册：一个代表 AI 代理，一个代表 ServiceNow API 连接器。

## 配置 Microsoft Entra ID

首先创建一个应用程序注册来代表 ServiceNow API 连接器。以下屏幕截图显示了 Microsoft Entra ID 中 ServiceNow API 连接器的应用程序注册页面。

![ServiceNow API 连接器应用程序的 Microsoft Entra 应用程序注册页面](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-2.png)

图 2：Microsoft Entra ID 中 ServiceNow API 连接器的应用程序注册

创建后，在概述页面中记下**应用程序（客户端）ID。**

在导航菜单中，展开 **管理** 并选择 **公开 API** 并使用默认应用程序 ID URI 添加名为“user_impersonation”的范围。此范围是 OBO 流在交换令牌时所请求的范围。以下屏幕截图显示了如何在 Microsoft Entra ID 中公开 API。

![在 Microsoft Entra ID 中公开 API 页面，并添加了 user_impersonation 范围](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-3.png)

图 3：在 Microsoft Entra ID 中公开 user_impersonation 范围

接下来，为 AI 代理创建应用程序注册。以下屏幕截图显示了 Microsoft Entra ID 中 ServiceNow 代理应用程序的应用程序注册页面。

![ServiceNow 代理应用程序的 Microsoft Entra 应用程序注册页面](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-4.png)

图 4：Microsoft Entra ID 中 ServiceNow Agent 的应用程序注册

记下 ServiceNowAgent 的应用程序（客户端）ID。

在此注册上创建客户端密码。网关需要这些凭据来执行 OBO 交换。以下屏幕截图显示了如何在 Microsoft Entra ID 中的 ServiceNow 代理应用程序注册上创建客户端密钥。

![证书和机密页面显示 ServiceNow 代理注册中的新客户端机密](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-5.png)

图 5：在 ServiceNow 代理应用程序注册上创建客户端密钥

然后将代理应用程序配置为具有调用 ServiceNow API 连接器应用程序的 API 权限。以下屏幕截图显示了您需要在 Microsoft Entra ID 中注册 ServiceNow 代理应用程序时配置的 API 权限。

![授予代理应用程序访问 ServiceNow API 连接器的 API 权限页面](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-6.png)

图 6：Microsoft Entra ID 中的 API 权限配置

除了为两个应用程序之间的任何标准 OBO 集成设置的设置外，无需对 Entra 配置进行任何更改。

## 配置 ServiceNow

在 ServiceNow 管理控制台中，导航到 **系统 OAuth > 入站集成** 并创建一个新的入站集成（由支持身份提供商的 OIDC 颁发的第三方 ID 令牌）。指定您在 Entra 中创建的 ServiceNow API 连接器应用程序注册中的客户端 ID。以下屏幕截图显示了 ServiceNow 中入站集成的配置。

![使用 API 连接器客户端 ID 配置的 ServiceNow 入站集成](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-7.png)

图 7：在 ServiceNow 中配置入站集成

在同一屏幕中，创建新的 OpenID Connect (OIDC) 提供商配置并输入 Entra 租户的 OIDC 元数据 URL。将用户声明映射到适当的用户字段。例如，如果您的 Entra 租户将用户的电子邮件放在“preferred_username”声明中，请将其映射到 ServiceNow 中的 **电子邮件** 字段。如果您的 Entra 租户未将 JTI 验证包含在令牌中，请清除 JTI 验证。 Entra 在其发行的代币上使用名为“uti”的内部声明，这相当于 JTI。考虑将此“uti”声明映射到“jti”声明，以提供额外的重播保护和拒绝列表。以下屏幕截图显示了如何在 ServiceNow 中配置 OIDC 提供程序。

![使用 Entra 元数据 URL 和声明映射的 ServiceNow OIDC 提供商配置](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-8.png)

图 8：在 ServiceNow 中配置 OAuth OIDC 提供程序

最后，在同一屏幕中，为集成创建一个身份验证范围（例如“APIConnector”）。以下屏幕截图显示了如何在 ServiceNow 中创建新的身份验证范围。

![用于集成的 ServiceNow 身份验证范围创建表单](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-9.png)

图 9：在 ServiceNow 中创建新的身份验证范围

将身份验证范围限制为表 API 或您的代理需要访问的任何 ServiceNow API，如以下屏幕截图所示。

![ServiceNow 身份验证范围仅限于表 API](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-10.png)

图 10：将身份验证范围限制为 ServiceNow 中的表 API

完成此配置后，ServiceNow 接受带有 API 连接器客户端 ID 的“audience”的授权令牌，并根据“preferred_username”声明解析调用用户。

## 配置 AgentCore 网关

配置 Entra 和 ServiceNow 后，您现在可以设置 AgentCore Gateway 以本机处理 OBO 交换。

### 第 1 步：创建出站身份验证配置

在 AgentCore 中创建新的出站身份验证配置（选择 **构建 > 身份 > 添加出站身份验证 > 添加 OAuth 客户端**），然后选择 **自定义提供程序**。输入代理应用程序注册中的客户端 ID 和客户端密钥，以及 Entra 发现 URL，如以下屏幕截图所示。

![AgentCore 出站身份验证添加带有代理客户端 ID、密钥和 Entra 发现 URL 的 OAuth 客户端](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-11.png)

图 11：在 AgentCore Gateway 中添加 OAuth 客户端

展开 **其他配置** 并选择 **JWT 授权授予**，如以下屏幕截图所示。这告诉网关使用基于 JWT 的授权类型进行令牌交换。

![选择了 JWT 授权的其他配置面板](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-12.png)

图 12：配置 JWT 授权

### 步骤 2：创建 MCP 版本为 2025-11-25 的网关

创建新的 AgentCore 网关（**构建 > 网关 > 创建网关**）。定义网关详细信息时，展开 **其他配置 — 可选** 并选择 MCP 版本 **2025-11-25**，如以下屏幕截图所示。本机 OBO 支持需要此版本。您无法为使用早期 MCP 版本创建的网关启用本机 OBO。

![选择 MCP 版本 2025-11-25 的网关创建附加配置](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-13.png)

图 13：选择 MCP 版本 2025-11-25

使用代理的应用程序注册来配置入站身份（选择 **使用现有身份提供商配置**），就像对待任何接受 Entra 身份验证请求的网关一样。

在 **JWT 授权配置** 下，添加我们之前为 **ServiceNowAgent** 记录的应用程序 ID，如以下屏幕截图所示。

![将 ServiceNowAgent 应用程序 ID 添加为入站身份的 JWT 授权配置](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-14.png)

图 14：在 AgentCore 网关中配置入站授权

### 步骤 3：添加具有代币交换的目标

将目标添加到指向您的 ServiceNow REST 端点的网关。内联定义架构。例如，要公开调用 ServiceNow Table API 的名为 ListIncidents 的工具，您可以使用以下 OpenAPI 规范（将服务器 URL 替换为您的 PDI 的服务器 URL）。
```
{
  "openapi": "3.0.0",
  "info": {
    "title": "ServiceNow Incident API (Minimal)",
    "description": "A subset of the ServiceNow Table API for listing incident records.",
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "https://devxxx.service-now.com/api/now/table",
      "variables": {
        "instance": {
          "default": "devxxx",
          "description": "Your ServiceNow instance name."
        }
      }
    }
  ],
  "paths": {
    "/incident": {
      "get": {
        "operationId": "getIncidents",
        "summary": "List incidents",
        "description": "Retrieves a list of incident records from the ServiceNow instance.",
        "parameters": [
          {
            "name": "sysparm_limit",
            "in": "query",
            "description": "Maximum number of records to return.",
            "schema": {
              "type": "integer",
              "default": 10
            }
          },
          {
            "name": "sysparm_query",
            "in": "query",
            "description": "An encoded query string to filter results (e.g., active=true).",
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "sysparm_fields",
            "in": "query",
            "description": "A comma-separated list of fields to return.",
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "A successful response containing an array of incidents.",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "result": {
                      "type": "array",
                      "items": {
                        "$ref": "#/components/schemas/Incident"
                      }
                    }
                  }
                }
              }
            }
          },
          "401": {
            "description": "Unauthorized - Invalid credentials."
          }
        },
        "security": [
          {
            "bearerAuth": []
          }
        ]
      }
    }
  },
  "components": {
    "securitySchemes": {
      "bearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
      }
    },
    "schemas": {
      "Incident": {
        "type": "object",
        "properties": {
          "sys_id": {
            "type": "string",
            "description": "Unique identifier for the incident."
          },
          "number": {
            "type": "string",
            "description": "Incident ID (e.g., INC0000001)."
          },
          "short_description": {
            "type": "string",
            "description": "A brief summary of the incident."
          },
          "severity": {
            "type": "string",
            "description": "The severity level of the incident."
          },
          "state": {
            "type": "string",
            "description": "The current state of the incident (e.g., New, In Progress, Closed)."
          },
          "sys_created_on": {
            "type": "string",
            "format": "date-time",
            "description": "The timestamp when the incident was created."
          }
        }
      }
    }
  }
}
```
以下屏幕截图显示了如何使用 OpenAPI 架构在 AgentCore Gateway 中配置 REST API 目标。

![使用内联定义的 ServiceNow OpenAPI 架构配置的 AgentCore 网关目标](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-15.png)

图 15：使用 ServiceNow OpenAPI 架构配置 REST API 目标

对于目标上的 **出站身份验证配置**，选择 **OAuth** 作为出站身份提供商，并选择您在步骤 1 中创建的出站身份验证配置。

现在展开 **其他配置** 部分并选择 **令牌交换授予**。配置以下内容：

**范围：** `api://5d4a7a11-xxxx-xxxx-xxxx-xxxxxxxxxxxx/user_impersonation`

这是您在 Entra 中的 ServiceNow API 连接器应用程序注册中公开的范围。

**自定义参数（键值对）：** `requested_token_use:on_behalf_of`

这个参数很关键。如果没有它，Entra 就不会执行 OBO 交换，并且对 ServiceNow 的调用会失败并出现身份验证错误。

最终配置如下图所示。

![具有 user_impersonation 范围和 request_token_use 自定义参数的出站身份验证令牌交换授权](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-16.png)

图 16：AgentCore 网关目标上的令牌交换授予配置

### 第 4 步：保存并测试

保存目标配置。 AgentCore Gateway 现在自动将入站令牌交换为有效的 ServiceNow 令牌，从而保留用户身份，无需自定义代码。

当代理呼叫网关时，会透明地发生以下情况：

- 网关接收代理的 JWT（“受众”：代理客户端 ID）。
- 网关使用 OBO 授权类型将令牌发送到 Entra 的令牌端点。
- Entra 发布带有原始用户声明的新令牌（“audience”：ServiceNow API 连接器客户端 ID）。
- 网关使用交换的令牌将请求转发到 ServiceNow。
- ServiceNow 从令牌解析用户并应用他们的权限。

以下代码片段显示了通过 MCP 服务器与 ServiceNow 交互的最小聊天代理。
```
import sys
import strands
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client

token = sys.argv[1] if len(sys.argv) > 1 else sys.exit("Usage: python snow_agent.py <TOKEN>")
MCP_URL = "<GATEWAY_URL>"
mcp_client = MCPClient(lambda: streamablehttp_client(url=MCP_URL, headers={"Authorization": f"Bearer {token}"}))
agent = strands.Agent(
    model=BedrockModel(model_id="global.anthropic.claude-sonnet-4-6", streaming=False),
    system_prompt=(
        "You have a tool called 'target-snow___getIncidents'. "
        "When asked about incidents, call it immediately with no parameters. "
        "Never ask the user for credentials or instance details --- the tool is pre-configured."
    ),
    tools=[mcp_client],
)

while (user_input := input("\nYou: ")).lower() not in ("quit", "exit", "q"):
    print(f"\nAgent: {agent(user_input)}")
```
## 故障排除

如果您收到来自 ServiceNow 的身份验证错误，请验证：

- 交换令牌中的“preferred_username”声明映射到 ServiceNow 中的有效用户电子邮件。
- ServiceNow 入站集成上的身份验证范围允许访问您的代理正在调用的 API 端点。
- 代理应用程序具有 Entra 中 ServiceNow API 连接器应用程序的 API 权限。

## 清理

为了避免持续产生费用，请删除以下资源（如果您为测试创建了这些资源）：

- AgentCore 网关及其目标。
- 出站身份验证配置。
- Entra 应用程序注册（如果专门为本演练创建）。
- ServiceNow 入站集成和 OIDC 提供商配置。

## 结论

AgentCore Gateway 中的本机 OBO 支持无需自定义 AWS Lambda 拦截器来执行令牌交换。您可以直接在网关目标上配置令牌交换，网关会根据每个请求透明地处理它。这种方法可以在整个代理到 API 链中维护用户身份，支持 ServiceNow 的用户级访问控制，并消除需要单独维护的自定义代码。

要开始使用 AgentCore Gateway，请参阅 [Amazon Bedrock AgentCore 文档](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore.html)。有关 Microsoft Entra 的 OBO 流程的更多信息，请参阅 [Microsoft 身份平台文档](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-on-behalf-of-flow)。

## 关于作者
