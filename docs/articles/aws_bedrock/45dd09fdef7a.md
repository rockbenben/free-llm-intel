---
vendor: aws_bedrock
title: Configuring Amazon Bedrock AgentCore Gateway for secure access to private resources
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/configuring-amazon-bedrock-agentcore-gateway-for-secure-access-to-private-resources
date: 2026-04-30
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 3d7745a464ea
---

# 配置 Amazon Bedrock AgentCore Gateway 以安全访问私有资源

***2026 年 10 月：本文已复核并更新以确保准确。***

生产环境中的 AI agent 常常需要访问位于 [Amazon Virtual Private Cloud（Amazon VPC）](https://aws.amazon.com/vpc/) 边界之后的内网 API、数据库和私有资源。为每一条 agent 到工具的路径单独管理私有连接，会增加运维负担并拖慢部署。Amazon Bedrock AgentCore 的 [VPC 连接能力](https://docs.aws.amazon.com/bedrock/latest/userguide/usingVPC.html)正是为在不把网络流量暴露到公网的前提下部署 AI agent 和 [Model Context Protocol（MCP）](https://modelcontextprotocol.io/docs/getting-started/intro) server 而设计的。这一能力已扩展到面向 [Amazon Bedrock AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html) 的托管 Amazon VPC 出口，因此你可以连到私有网络中横跨你 AWS 环境的端点。

本文将用 [Resource Gateway](https://docs.aws.amazon.com/vpc/latest/privatelink/resource-gateway.html) 配置 Amazon Bedrock AgentCore Gateway 以访问私有端点。Resource Gateway 是一种托管构造，它直接在你的 Amazon VPC 内创建 [Elastic Network Interface（ENI）](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-eni.html)，每个子网一个。我们会介绍两种实现模式（托管与自管理），并走过三个实际场景：连接私有的 [Amazon API Gateway](https://aws.amazon.com/api-gateway/) 端点、与 [Amazon Elastic Kubernetes Service](https://aws.amazon.com/eks/)（Amazon EKS）上的 MCP server 集成，以及访问私有的 REST API。

## 关键术语

以下术语贯穿全文。开始之前先过一遍，有助于理解每个组件在 AgentCore Gateway VPC 出口架构中的位置。

**Resource VPC：** 你的私有资源所在的 Amazon VPC。例如，包含你自托管 MCP server 或 API 端点的那个 VPC。这正是 AgentCore Gateway 需要访问的 Amazon VPC。Resource VPC 可以与 AgentCore Gateway 账户同属一个 AWS 账户，也可以位于不同账户。

**AgentCore Gateway 账户：** 用于创建和管理 AgentCore Gateway 资源的 AWS 账户。该账户可能与 Resource VPC 所在账户相同，也可能不同。

**Resource Gateway：** [Resource gateway](https://docs.aws.amazon.com/vpc/latest/privatelink/resource-gateway.html) 充当进入 Resource VPC 的私有入口。创建时，它会为你指定的每个子网各创建一个 ENI，每个 ENI 都位于你的 VPC 内。从 AgentCore Gateway 到私有资源的流量正是通过这些 ENI 抵达。

**Resource Configuration：** [面向 VPC 资源的 resource configuration](https://docs.aws.amazon.com/vpc/latest/privatelink/resource-configuration.html) 定义了 AgentCore Gateway 允许通过 Resource Gateway 访问的具体资源，以域名或 IP 地址标识。Resource Configuration 不授予整个 Amazon VPC 的访问权，而是把连接范围限定到单个端点。

**Service Network Resource Association**：service network resource association 把一个 resource configuration 连接到 AgentCore service network，从而允许 AgentCore Gateway 服务调用你的私有端点。无论使用哪种模式，AgentCore 都会代你创建并管理这个关联。

## AgentCore Gateway 的 VPC 出口如何工作？

AgentCore Gateway 的 VPC 出口支持两种模式，取决于你希望对底层网络基础设施掌握多少控制权，以及你打算如何为跨 VPC 连接做架构设计。

### 托管 VPC 资源

在该模式下，AgentCore Gateway 替你处理一切。你在 target 配置中提供 VPC ID、子网 ID 和安全组，AgentCore 便会在你的账户中自动创建并管理 VPC Resource Gateway。该模式可与现有网络架构配合，无论你是用 [VPC peering](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html) 做同区域或跨区域连接，还是用 [AWS Transit Gateway](https://aws.amazon.com/transit-gateway/) 搭建 hub-and-spoke 模型应对多 VPC 与混合环境。

下面的架构展示了 AgentCore Gateway 如何以托管 VPC 资源模式连接私有的 [Amazon API Gateway](https://aws.amazon.com/api-gateway/)。

![架构图：AgentCore Gateway 在托管 VPC 资源模式下通过 Resource Gateway 连接私有的 Amazon API Gateway](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/07/REVBLOG-1336-1.png)

图 1：AgentCore Gateway 在托管 VPC 资源模式下连接私有的 Amazon API Gateway

当你用托管 VPC 资源配置创建 AgentCore Gateway Target 时，AgentCore Gateway 发起请求并将其路由到 Resource Owner VPC 内的 Resource Gateway。Resource Gateway 再通过在你子网中创建、并受你所配置安全组管控的 ENI 转发流量。从该 ENI 出发，请求抵达 [execute-api VPC 端点](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-private-apis.html)。在托管 VPC 资源模式下，AgentCore 代你创建并管理 Resource Gateway，你对其只有只读可见性。

### 自管理的 Lattice 资源

在该模式下，你先自行创建并管理 Amazon VPC Lattice 的 Resource Gateway 和 Resource configuration，然后在 AgentCore Gateway 上创建 target 时引用它。这样你对 Resource configuration 拥有可见性和控制权，包括每个 ENI 的 IPv4 地址数量、子网放置和安全组规则。更重要的是，你能看清 resource configuration 本身：可以查看它、用 [AWS Resource Access Manager（AWS RAM）](https://aws.amazon.com/ram/) 共享它（跨账户连接时必需）、查看与它绑定的关联，并在需要时保留撤销这些关联的能力。

下面的架构展示了 AgentCore Gateway 如何以自管理 Lattice 资源模式连接私有 REST API 端点。

![架构图：AgentCore Gateway 在自管理 Lattice 资源模式下连接私有 REST API 端点](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/07/REVBLOG-1336-2.png)

图 2：AgentCore Gateway 在自管理 Lattice 资源模式下连接私有 REST API 端点

在自管理 Lattice 资源模式下，你需要在配置 AgentCore Gateway Target 之前预先创建 Resource Gateway 和 Resource Configuration。调用 [CreateGatewayTarget](https://docs.aws.amazon.com/bedrock-agentcore-control/latest/APIReference/API_CreateGatewayTarget.html) 时，传入 Resource Configuration ID，把 AgentCore Gateway target 与你的私有端点关联起来。调用时，Resource Gateway 通过在你子网中创建、并受你所配置安全组管控的 ENI 转发请求。从该 ENI 出发，请求抵达 execute-api VPC 端点。与托管 VPC 资源模式不同，Resource Gateway 和 Resource Configuration 归你所有并管理。

用下表判断哪种模式适合你的架构。要简化配置就选托管 VPC 资源模式；要掌控 Resource Gateway 生命周期、做跨账户连接并看清关联关系，就选自管理 Lattice 资源模式。

| **维度** | **AgentCore 托管 VPC 资源** | **自管理 Lattice 资源** |
| --- | --- | --- |
| 配置复杂度 | 简单。提供 VPC ID、子网 ID 和安全组 ID，其余由 AgentCore 管理 | 高级。你需要自行创建并管理 Amazon VPC Lattice 的 Resource Gateway 和 Resource Configuration，再把 resource configuration ID 传给每个 target |
| IPv4 消耗 | 每个托管 resource gateway 每个 ENI 消耗 1 个 IP 地址，不可配置 | 与 Amazon Bedrock AgentCore 配合使用时，每个子网消耗一个 IP 地址。若还挂到其他 VPC Lattice service network，则按 resource gateway 上的 ipv4AddressesPerEni 值消耗更多 IP |
| 跨账户 | 不原生支持。跨账户 / 跨 VPC 场景请用 hub-and-spoke 架构（[VPC peering](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html) 或 [AWS Transit Gateway](https://aws.amazon.com/transit-gateway/)）。 | 支持，需使用 [AWS Resource Access Manager（AWS RAM）](https://aws.amazon.com/ram/)。无需 VPC peering 或 Transit Gateway 即可直接跨账户连接。 |
| 复用现有 ENI | 在同一账户内，只要 target 的 managedVpcResource 配置在 Amazon VPC、子网集合、安全组集合、标签和 IP 地址类型上一致，AgentCore 就会自动复用同一个 Resource Gateway（及其 ENI） | 你可以把多个 Resource Configuration 挂到你自己拥有的单个 Resource Gateway 上。resourceConfigurationIdentifier 解析到该 Resource Gateway 的 target 共享其 ENI |
| Resource Gateway 生命周期管理 | Amazon Bedrock AgentCore 代你创建、复用和删除 Resource Gateway | resource gateway 和 resource configuration 的全生命周期由你负责 |
| 治理与可见性 | Resource Configuration 在 Amazon Bedrock AgentCore 服务账户中管理，不会出现在你的 Amazon VPC 控制台里。底层 Resource Gateway 在你的账户中以只读方式可见 | 在 Amazon VPC Lattice 控制台中可完整查看 Resource Configuration、Service Network 关联和已连接的域。你可以审计连接，并在细粒度上撤销访问 |
| 定价 | 仅按 GB 收取数据处理费（针对经 Resource Gateway 处理的数据） | 1）Service Network 关联按小时收费。2）按 GB 收取数据处理费 |

## 开始使用 AgentCore Gateway 的 VPC 出口

本文聚焦托管 VPC 资源模式。如果你想探索自管理 Lattice 资源方案，请参考[代码示例](https://github.com/awslabs/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastructure/01-gateway/03-private-connectivity/connect-gateway-to-private-resources)。开始之前，本文假定你对 Amazon VPC、[AWS Command Line Interface](https://aws.amazon.com/cli/)（AWS CLI）、Amazon Bedrock AgentCore 和 Amazon Bedrock AgentCore Gateway 有基本了解。请确认以下条件已具备。

- [AWS Command Line Interface](https://aws.amazon.com/cli/)（AWS CLI）。
- [AWS 凭证](https://docs.aws.amazon.com/cli/v1/userguide/cli-chap-configure.html)。
- TLS 证书信任。

默认情况下，AgentCore Gateway 只信任由公共证书颁发机构（CA）签发的服务器证书。如果你的端点出示的是私有 CA 签发的证书，可以把该私有 CA 证书注册到 target 上，让 gateway 信任它。详情见本文后面的“私有证书颁发机构”一节。

- [AWS Identity and Access Management（IAM）](https://aws.amazon.com/iam/)权限。

你的 IAM 主体需要针对 bedrock-agentcore.amazonaws.com 的 iam:CreateServiceLinkedRole 权限，这样在服务关联角色尚不存在时，AgentCore 才能代你创建它。所需的 IAM 策略见 Gateway 的[服务关联角色](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/service-linked-roles.html#gateway-service-linked-role)。

- 配置安全组。

Resource Gateway 安全组控制 Resource Gateway 的 ENI 能向 Amazon VPC 内资源发出哪些出站流量。如果在调用 [CreateGatewayTarget](https://docs.aws.amazon.com/bedrock-agentcore-control/latest/APIReference/API_CreateGatewayTarget.html) API 时未提供安全组，则会使用默认安全组。

- AgentCore Gateway。

本演练假定你已有一个 AgentCore Gateway。如果还没创建，请运行：

```
aws bedrock-agentcore create-gateway \
  --name my-gateway \
  --role-arn arn:aws:iam::<account-=id>:role/AgentCoreGatewayRole
```

记下响应中的 `gatewayId`。后续步骤创建 AgentCore Gateway Target 时需要用到它。

- 更深入的示例见 GitHub [仓库](https://github.com/awslabs/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastructure/01-gateway/03-private-connectivity/connect-gateway-to-private-resources)。

### 私有 Amazon API Gateway

本节创建一个路由到私有 Amazon API Gateway 的 AgentCore Gateway target。用以下参数调用 [CreateGatewayTarget](https://docs.aws.amazon.com/bedrock-agentcore-control/latest/APIReference/API_CreateGatewayTarget.html) API。在 openApiSchema 字段中给出你的私有 Amazon API Gateway 端点 URL（`https://{api-id}-{vpce-id}.execute-api.{region}.amazonaws.com/{stage}`）。在 managedVpcResource 块中给出你的 VPC ID、子网 ID 和安全组 ID。

```
aws bedrock-agentcore-control create-gateway-target \
  --region us-west-2 \
  --cli-input-json '{
    "gatewayIdentifier": "<GATEWAY_ID>",           
    "name": "private-apigw",
    "description": "Private API Gateway",                 
    "targetConfiguration": {                     
      "mcp": {
        "openApiSchema": {                     
          "inlinePayload": "..."
        }
      }
    },
    "credentialProviderConfigurations": [...],          
    "privateEndpoint": {
      "managedVpcResource": {
        "vpcIdentifier": "<VPC_ID>",
        "subnetIds": ["<SUBNET_ID_1>", "<SUBNET_ID_2>"],
        "endpointIpAddressType": "IPV4",
        "securityGroupIds": ["<VPCE_SG_ID>"]
      }                                        
    }           
  }'       
```

运行该命令后，AgentCore Gateway 会用其服务关联角色在你的 VPC 中创建 Resource Gateway，并为你指定的每个子网各创建一个 ENI。

下面的架构图展示了网络流向。

![网络流向：从 AgentCore Gateway 经 Resource Gateway 的 ENI 到 execute-api VPC 端点及私有 Amazon API Gateway](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/07/REVBLOG-1336-3.png)

图 3：经 Resource Gateway 到私有 Amazon API Gateway 的网络流向

AgentCore Gateway 发起请求，并将其路由到 Resource Owner VPC 内已创建的 Resource Gateway。流量经过你私有子网中的 ENI，由你的安全组规则决定哪些流量能到达下一跳。从那里，请求抵达 execute-api VPC 端点，由它为你的 Amazon API Gateway 内部端点提供私有连接。端点 URL 格式 https://{api-id}-{vpce-id}.execute-api.{region}.amazonaws.com/{stage} 就是你在 CreateGatewayTarget 调用的 openApiSchema 字段中提供的那一个。

### Amazon EKS 上的私有 MCP server

本节创建一个路由到运行在 Amazon EKS 上的私有 MCP server 的 AgentCore Gateway target。用以下参数调用 CreateGatewayTarget API。在 mcpServer 块中给出你内部 MCP server 的端点 URL。在 managedVpcResource 块中给出你的 VPC ID、子网 ID 和安全组 ID。

```
aws bedrock-agentcore-control create-gateway-target \
  --region us-west-2 \
  --cli-input-json '{
    "gatewayIdentifier": "<GATEWAY_ID>",           
    "name": "private-apigw",
    "description": "Private API Gateway",                 
    "targetConfiguration": {                     
      "mcp": {
        "mcpServer": {                     
          "endpoint": "https://internal.example.com/csm/mcp"
        }
      }
    },
    "credentialProviderConfigurations": [...],          
    "privateEndpoint": {
      "managedVpcResource": {
        "vpcIdentifier": "<VPC_ID>",
        "subnetIds": ["<SUBNET_ID_1>", "<SUBNET_ID_2>"],
        "endpointIpAddressType": "IPV4",
        "securityGroupIds": ["<VPCE_SG_ID>"]
      }                                        
    }           
  }'
```

运行该命令后，AgentCore 会在你的 VPC 中创建 Resource Gateway，并为你指定的每个子网各创建一个 ENI。下面的架构图展示了端到端的流量路径。

![网络流向：从 AgentCore Gateway 经 Resource Gateway 到内部 Network Load Balancer 以及 Amazon EKS 上的 NGINX Ingress Controller](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/07/REVBLOG-1336-4.png)

图 4：经内部 Network Load Balancer 到 Amazon EKS 上私有 MCP server 的网络流向

AgentCore Gateway 向你内部的端点发送 HTTPS 请求。Amazon Route 53 私有托管区把该域名解析到内部 [Network Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/introduction.html#:~:text=Classic%20Load%20Balancers.-,Network%20Load%20Balancer%20components,listeners%20to%20your%20load%20balancer.)（NLB）。请求经 Resource Gateway 进入 Resource Owner VPC，穿过受你安全组管控的 ENI，到达 NLB。NLB 使用 [AWS Certificate Manager（ACM）公共证书](https://docs.aws.amazon.com/acm/latest/userguide/gs-acm-request-public.html)在 443 端口终止 TLS，然后以 HTTP 在 80 端口把请求转发给运行在 Amazon EKS 上的 [NGINX Ingress Controller](https://docs.nginx.com/nginx-ingress-controller/)，由它把请求路由到相应的 pod。

### 私有 REST API target

本节创建一个路由到私有 REST API 端点的 AgentCore Gateway target。这适用于在你的 Amazon VPC 内运行的任何 REST API，例如容器化微服务。CreateGatewayTarget API 调用与前几节的模式相同。在 openApiSchema 字段中给出描述该 REST API 的 OpenAPI schema。在 `managedVpcResource` 块中给出你的 VPC ID、子网 ID 和安全组 ID。待 AgentCore Gateway 在你的 VPC 中创建好 Resource Gateway 后，下面的架构图展示了端到端的流量路径。

![网络流向：从 AgentCore Gateway 经 Resource Gateway 到内部 Application Load Balancer 及私有 REST API 的后端服务器](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/07/REVBLOG-1336-5.png)

图 5：经内部 Application Load Balancer 到私有 REST API 的网络流向

AgentCore Gateway 向你内部的端点发送 HTTPS 请求。Amazon Route 53 私有托管区把该域名解析到内部 [Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)（ALB）。请求经 Resource Gateway 进入 Resource Owner VPC，穿过受你安全组管控的 ENI，到达内部 ALB。ALB 在 443 端口使用 AWS Certificate Manager（ACM）公共证书终止 TLS，然后以 HTTP 在 8000 端口把请求转发给包含你后端服务器的 target group。

### 私有证书颁发机构

前几节使用的都是由公共 CA 签发的证书，例如 ACM 公共证书。而许多内部负载改用你组织的私有 CA 签发的服务器证书，例如来自 [AWS Private Certificate Authority（AWS Private CA）](https://docs.aws.amazon.com/privateca/latest/userguide/PcaWelcome.html) 或企业 PKI 的证书。AgentCore Gateway 可以原生信任私有 CA。

在创建或更新单个 target 时，你附加的是对 CA 证书的引用，而不是证书内容。CA 证书是一个 PEM 编码的文件，存放在 [Amazon Simple Storage Service（Amazon S3）](https://aws.amazon.com/s3/) 或 [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/) 中。在你创建或更新 target 时，gateway 会获取、验证并加密该证书，然后把它作为对该 target 出站 TLS 的信任锚。下面的架构图展示了 Amazon EKS 上私有 MCP server 的网络流向。

![网络流向：内部 Network Load Balancer 出示私有 CA 签发的服务器证书，由 AgentCore Gateway 对照已注册的 CA 证书校验](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/07/REVBLOG-1336-6.png)

图 6：使用私有证书颁发机构时 Amazon EKS 上私有 MCP server 的网络流向

AgentCore Gateway 向 `https://internal.egress-test.example.com/mcp` 发送 HTTPS 请求。Route 53 私有托管区把该域名解析到内部 Network Load Balancer。请求经 Resource Gateway 进入 Resource Owner VPC，穿过受你安全组管控的 ENI，到达 NLB。NLB 在 TLS 443 端口出示由你私有 CA 签发的服务器证书（`*.egress-test.example.com`），gateway 则用你注册到该 target 上的 CA 证书对它做校验。NLB 随后以 HTTP 在 80 端口把请求转发给运行在 Amazon EKS 上的 NGINX Ingress Controller，由它把请求路由到相应的 pod。

#### 开始之前

- target 使用私有端点（`privateEndpoint`），即托管 VPC 资源或自管理 Lattice 资源。
- target 类型为 MCP server（`mcpServer`）、OpenAPI schema（`openApiSchema`）或 HTTP passthrough target。
- 证书是 PEM 编码的 X.509 CA 证书，其 basic constraints 扩展设置为 `CA:TRUE`。gateway 会拒绝叶子（终端实体）证书。
- 证书处于有效期内，且包含完整证书链的 PEM 文件不超过 16 KB。
- 如果把证书存放在 Amazon S3 中，该 bucket 需与 gateway 处于同一个 AWS Region。
- 你端点出示的服务器证书能链接到该 CA 证书，并与 target 的主机名匹配。

#### 授予执行角色访问证书的权限

gateway 使用 gateway 执行角色获取 CA 证书。若来源是 Amazon S3，请对证书对象授予 `s3:GetObject`；若来源是 AWS Secrets Manager，请对该 secret 授予 `secretsmanager:GetSecretValue`。如果对象或 secret 由客户管理的 AWS Key Management Service（AWS KMS）密钥加密，还需授予使用该密钥解密的权限。CA 证书属于公开信息，但请把这些权限限定到具体的对象或 secret，而不是整个 bucket 或所有 secret。

#### 在 target 上注册 CA 证书

在 CreateGatewayTarget 调用中加入 `certificateConfigurations` 字段。该数组必须只包含一个条目，且该条目必须只设置一个来源，即 `s3` 或 `secretsManager`。下面的示例在私有 MCP server target 上注册来自 Amazon S3 的 CA 证书。

```
aws bedrock-agentcore-control create-gateway-target \
  --region us-west-2 \
  --cli-input-json '{
    "gatewayIdentifier": "<GATEWAY_ID>",
    "name": "private-ca-mcp",
    "description": "Private MCP server with private CA certificate",
    "targetConfiguration": {
      "mcp": {
        "mcpServer": {
          "endpoint": "https://internal.egress-test.example.com/mcp"
        }
      }
    },
    "credentialProviderConfigurations": [...],
    "privateEndpoint": {
      "managedVpcResource": {
        "vpcIdentifier": "<VPC_ID>",
        "subnetIds": ["<SUBNET_ID_1>", "<SUBNET_ID_2>"],
        "endpointIpAddressType": "IPV4",
        "securityGroupIds": ["<VPCE_SG_ID>"]
      }
    },
    "certificateConfigurations": [
      {
        "s3": {
          "uri": "s3://<CA_BUCKET>/private-ca.pem",
          "bucketOwnerAccountId": "<ACCOUNT_ID>"
        }
      }
    ]
  }'
```

若要改用 AWS Secrets Manager，请把 `s3` 块替换为以下内容。该 secret 必须是字符串 secret，而非二进制 secret。

```
"certificateConfigurations": [
  {
    "secretsManager": {
      "secretArn": "arn:aws:secretsmanager:us-west-2:<ACCOUNT_ID>:secret:private-ca-AbCdEf"
    }
  }
]
```

对于 Amazon S3 来源，我们建议设置 `bucketOwnerAccountId`。Amazon S3 会用它校验 bucket 所有者，从而避免 gateway 从意料之外的账户下的 bucket 中读取证书。

#### 校验、轮换与监控

- **校验是异步的。** 只有字段格式和“恰好一个来源”的规则会立即报错。证书已过期、叶子证书、对象或 secret 缺失、文件过大等问题会让 target 进入 `FAILED`（创建）或 `UPDATE_UNSUCCESSFUL`（更新）状态。详情请查看 target 上的 `statusReasons`。更新失败不会替换该 target 已在使用的证书。
- **在到期前轮换。** 证书过期后，TLS 握手会失败，对该 target 的工具调用也会失败。调用 UpdateGatewayTarget 并传入新的 CA 证书以替换它。已经建立的连接可以继续使用旧证书，直到 gateway 回收它们。
- **监控到期时间。** 对于使用私有 CA 的 target，gateway 会发出 Amazon CloudWatch 指标 `EarliestCertificateDaysToExpiry`，即文件中所有证书里最早到期者距现在的天数。请创建一个 CloudWatch 告警，在该值远未降到零时就触发。值为负数表示证书已过期。
- **吊销需自行规划。** gateway 不检查证书吊销列表（CRL），也不使用 OCSP，且会信任任何能链接到所配置 CA 的证书，直到该证书过期。要停止信任某个证书，请用一个不再链接到它的 CA 证书更新 target。要恢复为信任公共 CA，调用 UpdateGatewayTarget 并省略 `certificateConfigurations`。

## 清理

为避免持续产生费用，请删除本演练中创建的所有资源。参考 AgentCore Gateway VPC 出口的[定价页面](https://aws.amazon.com/bedrock/agentcore/pricing/)。此外，Amazon EKS 集群、负载均衡器和 API Gateway 端点运行期间都会计费。请确认资源已删除以停止计费。如果你跟着 GitHub [示例](https://github.com/awslabs/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastructure/01-gateway/03-private-connectivity/connect-gateway-to-private-resources)操作，请务必运行每个 Jupyter Notebook 末尾的清理部分。

如果你使用的是托管 VPC 资源模式，删除 Gateway Target 会一并移除关联的 Amazon VPC Resource Gateway。

```
aws bedrock-agentcore delete-gateway-target \
    --gateway-identifier <gateway-id> \
    --target-id <target-id>
```

## 结论

随着 AI agent 承担越来越复杂的任务，它们需要安全地访问支撑业务运转的工具与服务，而其中许多都位于私有网络内。借助 AgentCore Gateway 的 VPC 出口，你的 agent 可以访问私有 MCP server、内网 API、数据库和本地系统，而无需把它们暴露到公网。托管 VPC 资源模式直接与你现有的 VPC 集成，配置量最小。自管理 Lattice 资源模式提供细粒度控制，但需要额外配置。两者都通过 Resource Gateway 转发流量，且流量不出 AWS 网络。

## 后续步骤

- 在你的环境中挑一个能从 AI agent 访问中受益的内部 API 或 MCP server。
- 审视你现有的 Amazon VPC 架构，判断哪种模式（托管 VPC 资源或自管理 Lattice 资源）符合你的需求。
- 查阅 Amazon Bedrock AgentCore Gateway [文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-vpc-egress.html)，了解其他配置选项。
- 探索 Amazon VPC Lattice Resource Gateway [文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/vpc-egress-private-endpoints.html)，了解跨账户场景。
- 更多集成模式和高级配置，见 [GitHub 示例](https://github.com/awslabs/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastructure/01-gateway/03-private-connectivity/connect-gateway-to-private-resources)。

## 关于作者
