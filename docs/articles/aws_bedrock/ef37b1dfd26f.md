---
vendor: aws_bedrock
title: ServiceNow 借 Bedrock AgentCore Gateway 实现 on-behalf-of token 交换
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/servicenow-on-behalf-of-token-exchange-with-bedrock-agentcore-gateway
date: 2026-11-03
lang: zh
captured: 2026-11-05
extractor: readability-v1
translator: agent
status: translated
body_sha: 6025a8c002fe
---

# ServiceNow 借 Bedrock AgentCore Gateway 实现 on-behalf-of token 交换

代表用户去交互企业 API 的 AI agent，需要在整条请求链上保持用户身份。缺少身份传递时，API 调用到达下游服务代表的就是应用本身，而不是发起这个动作的用户。这会切断审计链、绕过用户级的访问控制，也违背最小权限原则。

Amazon Bedrock AgentCore 是一个平台，用任意框架或模型都能大规模地构建、连接和优化 agent。本文演示如何把 [AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)——Amazon Bedrock AgentCore 的一项能力——配置成与 Microsoft Entra ID 做 on-behalf-of（OBO）token 交换。这样 AI agent 就能在保留调用者身份的前提下调用 [ServiceNow REST API](https://www.servicenow.com/docs/r/api-reference/rest-apis/api-rest.html)。你在 gateway target 上配置 token 交换，AgentCore Gateway 则会在每一次请求上执行这个交换。这个模式可以套用到其他受 OAuth 保护的 REST API 上。

在生产环境里，你还可以把身份传递与 Amazon Bedrock Guardrails 配对使用，用来过滤有害内容并校验 agent 的输入与输出。

## 方案概览

架构里有三个关键组件，通过 AgentCore Gateway 连接起来：

- 一个 AI agent 应用，由一个 OAuth application registration 通过 Microsoft Entra ID 保护。
- 一个 Model Context Protocol（MCP）server，用 AgentCore Gateway 实现，位于 agent 与 ServiceNow 之间。
- ServiceNow REST API，配置了一个与 Microsoft Entra ID 关联的入站 OAuth 集成。

下图展示了端到端的方案架构，包括 AWS、Microsoft Entra ID 与 ServiceNow 内部的组件。

![方案架构，展示 agent、AgentCore Gateway、Microsoft Entra ID 与 ServiceNow，以及它们之间的 token 流转](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-1.png)

图 1：横跨 AWS、Microsoft Entra ID 与 ServiceNow 的方案架构

如图 1 所示，用户先获取一个 JSON Web Token（JWT）来调用 agent 1。agent 用一个限定到它自己那份 application registration 的 JWT token 向 gateway 认证 2。接着 gateway 用 OBO flow 把那个 token 换成一个限定到 ServiceNow API connector 的新 token，同时保留最初那个用户的身份 3。ServiceNow 收到一个有效 token，其 `preferred_username` claim 映射到一个已存在的 ServiceNow 用户，并把该用户的 permissions 应用到这次 API 调用上 4。

## OBO token 交换在这个场景里如何工作

agent 调用 gateway 时，出示的是一个 `audience` claim 与其 client ID 相匹配的 JWT（例如 `3ff88e17-XXXX-XXXX-XXXX-XXXXXXXXXXXX`）。而 ServiceNow 期望的是一个 `audience` claim 与它自己那个 API connector 的 client ID（`5d4a7a11-XXXX-XXXX-XXXX-XXXXXXXXXXXX`）相匹配的 token。

OBO flow 补上了这段差距。AgentCore Gateway 把入站 token 连同 agent 应用的 client credentials、目标 scope，以及一个参数 `requested_token_use: on_behalf_of`，一起发给 Entra 的 token endpoint。Entra 校验调用者确实同意了这个委托，然后为 ServiceNow API 签发一个新 token，其中原用户的 claims 原封不动。

## 前提条件

开始之前，你需要以下内容：

- 一个可访问 AgentCore Gateway 的 AWS 账户。
- 一个 Microsoft Entra ID tenant，且具备创建 [application registration](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app) 的 permissions。要注册应用，你的账户至少需要 [Application Developer role](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference#application-developer)。
- 一个 ServiceNow 实例，且具备配置入站 OAuth 集成所需的管理员权限。你可以在 ServiceNow personal developer instance 的注册页 [https://developer.servicenow.com/](https://developer.servicenow.com/) 创建一个 ServiceNow personal developer instance（PDI）。
- 两个 Entra application registration：一个代表 AI agent，一个代表 ServiceNow API connector。

## 配置 Microsoft Entra ID

先创建一个 application registration 来代表 ServiceNow API connector。下面的截图展示的是 Microsoft Entra ID 中 ServiceNow API Connector 的 application registration 页面。

![Microsoft Entra ID 中 ServiceNow API connector 应用的 application registration 页面](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-2.png)

图 2：Microsoft Entra ID 中 ServiceNow API connector 的 application registration

创建完成后，在 Overview 页面记下 **Application (client) ID.**

在导航菜单里展开 **Manage**，选择 **Expose an API**，用默认的 Application ID URI 添加一个名为 `user_impersonation` 的 scope。OBO flow 在交换 token 时申请的就是这个 scope。下面的截图展示如何在 Microsoft Entra ID 中 expose 一个 API。

![Microsoft Entra ID 的 Expose an API 页面，已添加 user_impersonation scope](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-3.png)

图 3：在 Microsoft Entra ID 中 expose user_impersonation scope

接下来，为 AI agent 创建一个 application registration。下面的截图展示的是 Microsoft Entra ID 中 ServiceNow Agent 应用的 application registration 页面。

![Microsoft Entra ID 中 ServiceNow Agent 应用的 application registration 页面](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-4.png)

图 4：Microsoft Entra ID 中 ServiceNow Agent 的 application registration

记下 ServiceNowAgent 的 Application (client) ID。

在这份 registration 上创建一个 client secret。gateway 需要这份凭证来执行 OBO 交换。下面的截图展示如何在 Microsoft Entra ID 的 ServiceNow Agent application registration 上创建 client secret。

![Certificates and secrets 页面，展示 ServiceNow Agent registration 上一个新建的 client secret](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-5.png)

图 5：在 ServiceNow Agent 的 application registration 上创建 client secret

然后配置 agent 应用，让它具备调用 ServiceNow API connector 应用的 API permissions。下面的截图展示你在 Microsoft Entra ID 的 ServiceNow Agent application registration 上需要配置的 API permissions。

![API permissions 页面，为 agent 应用授予访问 ServiceNow API connector 的权限](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-6.png)

图 6：Microsoft Entra ID 中的 API permission 配置

除了两个应用之间任何标准 OBO 集成本来就要做的配置之外，Entra 这边不需要再做改动。

## 配置 ServiceNow

在 ServiceNow 管理控制台中，导航到 **System OAuth > Inbound Integrations**，创建一个新的 inbound integration（Third party ID token issued by OIDC supporting identity provider）。填入你在 Entra 中创建的 ServiceNow API connector application registration 的 client ID。下面的截图展示 ServiceNow 中 inbound integration 的配置。

![ServiceNow inbound integration，已配置 API connector 的 client ID](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-7.png)

图 7：在 ServiceNow 中配置 inbound integration

在同一个页面里，新建一个 OpenID Connect（OIDC）provider 配置，并填入你 Entra tenant 的 OIDC metadata URL。把用户 claim 映射到合适的用户字段。例如，如果你的 Entra tenant 把用户邮箱放在 `preferred_username` claim 里，就把它映射到 ServiceNow 的 **Email** 字段。如果你的 Entra tenant 不在 token 里包含 JTI，就清除 JTI verification。Entra 在它签发的 token 上使用一个名为 `uti` 的内部 claim，它等价于 JTI。可以考虑把这个 `uti` claim 映射到一个 `jti` claim，以提供更强的重放保护和 denylist。下面的截图展示如何在 ServiceNow 中配置 OIDC provider。

![ServiceNow 的 OIDC provider 配置，含 Entra metadata URL 与 claim 映射](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-8.png)

图 8：在 ServiceNow 中配置 OAuth OIDC provider

最后，在同一个页面里为该集成创建一个 auth scope（例如 `APIConnector`）。下面的截图展示如何在 ServiceNow 中创建新的 auth scope。

![ServiceNow 中为集成新建 auth scope 的表单](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-9.png)

图 9：在 ServiceNow 中创建新的 auth scope

把 auth scope 限定为 Table API，或你 agent 需要访问的那些 ServiceNow API，如下图所示。

![ServiceNow 的 auth scope 限定为 Table API](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-10.png)

图 10：在 ServiceNow 中把 auth scope 限定为 Table API

这套配置完成后，ServiceNow 就会接受 `audience` 为你 API connector 的 client ID 的授权 token，并从 `preferred_username` claim 解析出调用者的用户。

## 配置 AgentCore Gateway

Entra 和 ServiceNow 都配好之后，你就可以设置 AgentCore Gateway，让它原生地处理 OBO 交换。

### 步骤 1：创建一个出站 auth 配置

在 AgentCore 中新建一个 outbound auth 配置（依次选择 **Build > Identity > Add Outbound Auth > Add OAuth client**），并选择 **Customized provider**。填入你 agent application registration 的 client ID 与 client secret，再填入 Entra 的 discovery URL，如下图所示。

![AgentCore 的 outbound auth 中添加 OAuth client，含 agent 的 client ID、secret 与 Entra discovery URL](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-11.png)

图 11：在 AgentCore Gateway 中添加 OAuth client

展开 **Additional configurations**，选择 **JWT authorization grant**，如下图所示。这就是告诉 gateway 使用基于 JWT 的 grant type 来做 token 交换。

![Additional configurations 面板，已选中 JWT authorization grant](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-12.png)

图 12：配置 JWT authorization grant

### 步骤 2：用 MCP 版本 2025-11-25 创建 gateway

新建一个 AgentCore Gateway（**Build > Gateways > Create gateway**）。在定义 gateway 详情时，展开 **Additional configurations — optional**，选择 MCP 版本 **2025-11-25**，如下图所示。原生 OBO 支持必须用这个版本。用更早 MCP 版本创建的 gateway，无法开启原生 OBO。

![Gateway 创建的 Additional configurations，已选中 MCP 版本 2025-11-25](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-13.png)

图 13：选择 MCP 版本 2025-11-25

用你 agent 的 application registration 配置入站身份（选择 **Use existing identity provider configurations**），这和你为任何接受 Entra 认证请求的 gateway 所做的配置一样。

在 **JWT Authorization Configuration** 下，把前面记录下来的 **ServiceNowAgent** 的 Application ID 添加进去，如下图所示。

![JWT authorization configuration，把 ServiceNowAgent 的 application ID 作为入站身份加入](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-14.png)

图 14：在 AgentCore Gateway 中配置入站授权

### 步骤 3：添加一个带 token 交换的 target

往 gateway 上添加一个指向你 ServiceNow REST endpoint 的 target。把 schema 内联定义。例如，要暴露一个名为 ListIncidents、会调用 ServiceNow Table API 的工具，你可以使用下面这份 OpenAPI specification（把 server URL 换成你 PDI 的那个）。

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

下面的截图展示如何在 AgentCore Gateway 中用这份 OpenAPI schema 配置 REST API target。

![AgentCore Gateway 的 target，已内联定义 ServiceNow OpenAPI schema](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-15.png)

图 15：用 ServiceNow OpenAPI schema 配置 REST API target

在 target 的 **Outbound Auth configuration** 上，选择 **OAuth** 作为出站 identity provider，并选择你在步骤 1 创建的那个 outbound auth 配置。

现在展开 **Additional configurations** 区块，选择 **Token exchange grant**。按下面这样配置：

**Scope:** `api://5d4a7a11-xxxx-xxxx-xxxx-xxxxxxxxxxxx/user_impersonation`

这就是你在 Entra 的 ServiceNow API connector application registration 上 expose 的那个 scope。

**Custom parameter（键值对）：** `requested_token_use:on_behalf_of`

这个参数是关键。没有它，Entra 不会执行 OBO 交换，对 ServiceNow 的调用会以认证错误失败。

最终配置见下面的截图。

![Outbound auth 的 token exchange grant，含 user_impersonation scope 与 requested_token_use 自定义参数](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/02/ML-21070-16.png)

图 16：AgentCore Gateway target 上的 token exchange grant 配置

### 步骤 4：保存并测试

保存 target 配置。此后 AgentCore Gateway 会自动把入站 token 换成有效的 ServiceNow token，保留用户身份，且不需要任何自定义代码。

当 agent 调用 gateway 时，下面这些都会透明地发生：

- gateway 收到 agent 的 JWT（`audience`：agent 的 client ID）。
- gateway 带着 OBO grant type 把这个 token 发给 Entra 的 token endpoint。
- Entra 签发一个新 token（`audience`：ServiceNow API connector 的 client ID），带上原用户的 claims。
- gateway 用交换后的 token 把请求转发给 ServiceNow。
- ServiceNow 从 token 中解析出用户，并应用该用户的 permissions。

下面的代码片段展示一个最小的聊天 agent，通过 MCP server 与 ServiceNow 交互。

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

## 排查问题

如果你从 ServiceNow 收到认证错误，请核实以下几点：

- 交换后的 token 里的 `preferred_username` claim 映射到 ServiceNow 中一个有效的用户邮箱。
- ServiceNow inbound integration 上的 auth scope 允许访问你 agent 正在调用的那些 API endpoint。
- 该 agent 应用在 Entra 中具备指向 ServiceNow API connector 应用的 API permissions。

## 清理

为避免持续产生费用，如果你为测试创建了以下资源，请把它们删除：

- AgentCore Gateway 及其 targets。
- outbound auth 配置。
- Entra application registrations（如果专门为这篇走查而创建）。
- ServiceNow inbound integration 与 OIDC provider 配置。

## 结论

AgentCore Gateway 的原生 OBO 支持，让你不再需要自定义的 AWS Lambda interceptor 来执行 token 交换。你直接在 gateway target 上配置 token 交换，gateway 会在每个请求上透明地处理它。这种做法在 agent 到 API 的整条链路上保持了用户身份，支持了 ServiceNow 的用户级访问控制，也省掉了那份本来需要单独维护的自定义代码。

要开始使用 AgentCore Gateway，参见 [Amazon Bedrock AgentCore 文档](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore.html)。想了解更多 Microsoft Entra 的 OBO flow，参阅 [Microsoft identity platform 文档](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-on-behalf-of-flow)。

## 关于作者
