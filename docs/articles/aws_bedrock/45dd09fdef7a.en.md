---
vendor: aws_bedrock
title: Configuring Amazon Bedrock AgentCore Gateway for secure access to private resources
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/configuring-amazon-bedrock-agentcore-gateway-for-secure-access-to-private-resources
date: 2026-04-30
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 1a533b61607b
---

# Configuring Amazon Bedrock AgentCore Gateway for secure access to private resources

***October 2026: This post was reviewed and updated for accuracy.***

AI agents in production environments often need to reach internal APIs, databases, and private resources that sit behind [Amazon Virtual Private Cloud (Amazon VPC)](https://aws.amazon.com/vpc/) boundaries. Managing private connectivity for each agent-to-tool path adds operational overhead and slows deployment. Amazon Bedrock AgentCore [VPC connectivity](https://docs.aws.amazon.com/bedrock/latest/userguide/usingVPC.html) is designed to deploy AI agents and [Model Context Protocol (MCP)](https://modelcontextprotocol.io/docs/getting-started/intro) servers without requiring the network traffic to be exposed to the public internet. This capability extends to managed Amazon VPC egress for [Amazon Bedrock AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html), so you can connect to endpoints inside private networks across your AWS environment.

In this post, you will configure Amazon Bedrock AgentCore Gateway to access private endpoints using [Resource Gateway](https://docs.aws.amazon.com/vpc/latest/privatelink/resource-gateway.html), a managed construct that provisions [Elastic Network Interfaces (ENIs)](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-eni.html) directly inside your Amazon VPC, one per subnet. You will explore two implementation modes (managed and self-managed) and walk through three practical scenarios: connecting to a private [Amazon API Gateway](https://aws.amazon.com/api-gateway/) endpoint, integrating with an MCP server on [Amazon Elastic Kubernetes Service](https://aws.amazon.com/eks/) (Amazon EKS), and accessing a private REST API.

## Key terms

The following terms are used throughout this post. Review them before proceeding to understand how each component fits into the AgentCore Gateway VPC egress architecture.

**Resource VPC:** The Amazon VPC where your private resource lives. For example, the VPC containing your privately hosted MCP server or API endpoint. This is the Amazon VPC that AgentCore Gateway needs to reach. Resource VPC can either be in the same AWS account as the AgentCore Gateway account or in a different account.

**AgentCore Gateway account:** The AWS account where you create and manage your AgentCore Gateway resources. This account may or may not be the same account as the Resource VPC.

**Resource Gateway:** [Resource gateway](https://docs.aws.amazon.com/vpc/latest/privatelink/resource-gateway.html) acts as the private entry point into your Resource VPC. When created, it provisions one ENI per subnet that you specify, each sitting inside your VPC. Traffic from AgentCore Gateway to your private resource arrives through these ENIs.

**Resource Configuration:** [Resource configuration for VPC resources](https://docs.aws.amazon.com/vpc/latest/privatelink/resource-configuration.html) defines the specific resource AgentCore Gateway is allowed to reach through the Resource Gateway, identified by a domain name or IP address. Rather than granting access to your entire Amazon VPC, a Resource Configuration scopes connectivity to a single endpoint.

**Service Network Resource Association**: A service network resource association connects a resource configuration to the AgentCore service network, which allows AgentCore Gateway service to invoke your private endpoint. AgentCore creates and manages this association on your behalf, regardless of which mode you use.

## How does AgentCore Gateway VPC egress work?

AgentCore Gateway VPC egress supports two modes depending on how much control you want over the underlying networking infrastructure and how you want to architect for cross-VPC connectivity.

### Managed VPC resource

In this mode, AgentCore Gateway handles everything on your behalf. You provide your VPC ID, subnet IDs, and security groups as part of your target configuration, and AgentCore automatically creates and manages the VPC Resource Gateway in your account. This mode integrates with existing network architectures, whether you use [VPC peering](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html) for same-Region or cross-Region connectivity or a hub-and-spoke model with [AWS Transit Gateway](https://aws.amazon.com/transit-gateway/) for multi-VPC and hybrid environments.

The following architecture shows how AgentCore Gateway connects to private [Amazon API Gateway](https://aws.amazon.com/api-gateway/) using managed VPC resource mode.

![Architecture of AgentCore Gateway connecting to a private Amazon API Gateway through a Resource Gateway in managed VPC resource mode](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/07/REVBLOG-1336-1.png)

Figure 1: AgentCore Gateway connecting to a private Amazon API Gateway in managed VPC resource mode

When you create an AgentCore Gateway Target with a managed VPC resource configuration, AgentCore Gateway initiates the request and routes it to the Resource Gateway inside your Resource Owner VPC. The Resource Gateway forwards traffic through an ENI provisioned in your subnet, governed by the security groups you configure. From the ENI, the request reaches the [execute-api VPC endpoint](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-private-apis.html). In managed VPC resource mode, AgentCore creates and manages the Resource Gateway on your behalf. You only have read-only visibility into it.

### Self-managed Lattice resource

In this mode, you create and manage the Amazon VPC Lattice Resource Gateway and Resource configuration before referencing it during target creation on AgentCore Gateway. This gives you visibility and control over the Resource configuration, including the number of IPv4 addresses per ENI, subnet placement, and security group rules. More importantly, it gives you visibility into the resource configuration itself, with the ability to view it, share it using [AWS Resource Access Manager (AWS RAM)](https://aws.amazon.com/ram/) (required for cross-account connectivity), see associations tied to it, and retain the ability to revoke those associations when you choose.

The following architecture shows how AgentCore Gateway connects to private REST API endpoints using self-managed lattice resource mode.

![Architecture of AgentCore Gateway connecting to private REST API endpoints in self-managed Lattice resource mode](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/07/REVBLOG-1336-2.png)

Figure 2: AgentCore Gateway connecting to private REST API endpoints in self-managed Lattice resource mode

In self-managed lattice resource mode, you pre-create the Resource Gateway and Resource Configuration before configuring your AgentCore Gateway Target. When you call [CreateGatewayTarget](https://docs.aws.amazon.com/bedrock-agentcore-control/latest/APIReference/API_CreateGatewayTarget.html), you pass the Resource Configuration ID to associate AgentCore Gateway target with your private endpoint. At invocation time, Resource Gateway forwards the request through an ENI provisioned in your subnet, governed by the security groups you configure. From the ENI, the request reaches the execute-api VPC endpoint. Unlike managed VPC Resource mode, you own and manage the Resource Gateway and Resource Configuration.

Use the following table to determine which mode fits your architecture. Choose managed VPC resource mode for streamlined setup, or self-managed Lattice resource mode for control over Resource Gateway lifecycle, cross-account connectivity, and visibility into associations.

| **Dimension** | **AgentCore Managed VPC Resource** | **Self-Managed Lattice Resource** |
| --- | --- | --- |
| Setup complexity | Straightforward. Provide VPC ID, subnet IDs, and security group IDs. AgentCore manages the rest | Advanced. You create and manage the Amazon VPC Lattice Resource Gateway and Resource Configurations yourself, then pass the resource configuration ID to each target |
| IPv4 consumption | Each managed resource gateway consumes 1 IP address per ENI. This is not configurable | When used with Amazon Bedrock AgentCore, it consumes one IP address per subnet. If also attached to other VPC Lattice service networks, it consumes additional IPs based on the ipv4AddressesPerEni value on the resource gateway |
| Cross-account | Not natively supported. Use hub-and-spoke architectures ([VPC peering](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html) or [AWS Transit Gateway](https://aws.amazon.com/transit-gateway/)) for cross-account / cross-VPC scenarios. | Supported with [AWS Resource Access Manager (AWS RAM)](https://aws.amazon.com/ram/). Enables direct cross-account connectivity without requiring VPC peering or Transit Gateway. |
| Reusing existing ENIs | AgentCore automatically reuses one Resource Gateway (and its ENIs) across targets in the account whose managedVpcResource config matches on Amazon VPC, subnet set, security-group set, tags, and IP address type | You attach multiple Resource Configurations to a single Resource Gateway you own. Target whose resourceConfigurationIdentifier resolves to that Resource Gateway shares its ENIs |
| Resource Gateway Lifecycle management | Amazon Bedrock AgentCore creates, reuses, and deletes Resource Gateways on your behalf | You own the full lifecycle of resource gateways and resource configurations |
| Governance and visibility | Resource Configurations are managed in the Amazon Bedrock AgentCore service account and aren’t visible in your Amazon VPC console. The underlying Resource Gateway is visible in your account in read-only mode | Full visibility into Resource Configurations, Service Network associations, and connected domains in your Amazon VPC Lattice console. You can audit connections and revoke access at a granular level |
| Pricing | Per-GB data processing charges only (for data processed through the Resource Gateway) | 1) Hourly charge for Service Network association. 2) Per-GB data processing charges |

## Get started with AgentCore Gateway VPC egress

In this post, you focus on the managed VPC resource mode. If you want to explore the self-managed lattice resource offering, follow the [code samples](https://github.com/awslabs/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastructure/01-gateway/03-private-connectivity/connect-gateway-to-private-resources). Before getting started, this post assumes basic familiarity with Amazon VPC, [AWS Command Line Interface](https://aws.amazon.com/cli/) (AWS CLI), Amazon Bedrock AgentCore, and Amazon Bedrock AgentCore Gateway. Make sure that you have the following in place.

- [AWS Command Line Interface](https://aws.amazon.com/cli/) (AWS CLI).
- [AWS Credentials](https://docs.aws.amazon.com/cli/v1/userguide/cli-chap-configure.html).
- TLS certificate trust.

By default, AgentCore Gateway trusts only server certificates that a public certificate authority (CA) issues. If your endpoint presents a certificate that a private CA issues, you can register the private CA certificate on the target so the gateway trusts it. For details, see the Private certificate authority section later in this post.

- [AWS Identity and Access Management (IAM)](https://aws.amazon.com/iam/) permissions.

Your IAM principal needs the iam:CreateServiceLinkedRole permission for bedrock-agentcore.amazonaws.com, so that AgentCore can create the service-linked role on your behalf if it does not already exist. For the required IAM policy, see Gateway [service-linked role](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/service-linked-roles.html#gateway-service-linked-role).

- Set up security groups.

The Resource Gateway security group controls what traffic the Resource Gateway ENIs can send outbound to resources inside your Amazon VPC. If you don’t provide the security group while invoking [CreateGatewayTarget](https://docs.aws.amazon.com/bedrock-agentcore-control/latest/APIReference/API_CreateGatewayTarget.html) API, then the default security group is used.

- AgentCore Gateway.

This walkthrough assumes that you have an existing AgentCore Gateway. If you haven’t created one yet, run:

```
aws bedrock-agentcore create-gateway \
  --name my-gateway \
  --role-arn arn:aws:iam::<account-=id>:role/AgentCoreGatewayRole
```

Note the `gatewayId` from the response. You need it when creating AgentCore Gateway Targets in the steps that follow.

- For in-depth examples, see the GitHub [repository](https://github.com/awslabs/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastructure/01-gateway/03-private-connectivity/connect-gateway-to-private-resources).

### Private Amazon API Gateway

In this section, you create an AgentCore Gateway target that routes to a private Amazon API Gateway. Call the [CreateGatewayTarget](https://docs.aws.amazon.com/bedrock-agentcore-control/latest/APIReference/API_CreateGatewayTarget.html) API with the following parameters. In the openApiSchema field, provide your private Amazon API Gateway endpoint URL (`https://{api-id}-{vpce-id}.execute-api.{region}.amazonaws.com/{stage}`). In the managedVpcResource block, provide your VPC ID, subnet IDs, and security group ID.

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

After you run the command, AgentCore Gateway uses its service-linked role to provision a Resource Gateway in your VPC, creating one ENI per subnet you specified.

The following architecture diagram shows the network flow.

![Network flow from AgentCore Gateway through a Resource Gateway ENI to the execute-api VPC endpoint and private Amazon API Gateway](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/07/REVBLOG-1336-3.png)

Figure 3: Network flow to a private Amazon API Gateway through the Resource Gateway

AgentCore Gateway initiates the request and routes it to the Resource Gateway provisioned inside Resource Owner VPC. Traffic passes through the ENI inside your private subnet, where your security group rules govern what reaches the next hop. From there, the request reaches the execute-api VPC endpoint, which provides private connectivity to your Amazon API Gateway internal endpoint. The endpoint URL format https://{api-id}-{vpce-id}.execute-api.{region}.amazonaws.com/{stage} is what you provided in the openApiSchema field of your CreateGatewayTarget call.

### Private MCP server on Amazon EKS

In this section, you create an AgentCore Gateway target that routes to a private MCP server running on Amazon EKS. Call the CreateGatewayTarget API with the following parameters. In the mcpServer block, provide your internal MCP server endpoint URL. In the managedVpcResource block, provide your VPC ID, subnet IDs, and security group ID.

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

After you run this command, AgentCore provisions a Resource Gateway in your VPC, creating one ENI per subnet you specified. The following architecture diagram shows the end-to-end traffic path.

![Network flow from AgentCore Gateway through a Resource Gateway to an internal Network Load Balancer and NGINX Ingress Controller on Amazon EKS](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/07/REVBLOG-1336-4.png)

Figure 4: Network flow to a private MCP server on Amazon EKS through an internal Network Load Balancer

AgentCore Gateway sends an HTTPS request to your internal endpoint. The Amazon Route 53 private hosted zone resolves that domain to the internal [Network Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/introduction.html#:~:text=Classic%20Load%20Balancers.-,Network%20Load%20Balancer%20components,listeners%20to%20your%20load%20balancer.) (NLB). The request enters the Resource Owner VPC through the Resource Gateway, passes through the ENI governed by your security groups, and arrives at the NLB. The NLB terminates TLS on port 443 using an [AWS Certificate Manager (ACM) public certificate](https://docs.aws.amazon.com/acm/latest/userguide/gs-acm-request-public.html), then forwards the request over HTTP on port 80 to the [NGINX Ingress Controller](https://docs.nginx.com/nginx-ingress-controller/) running on Amazon EKS, which routes it to the appropriate pod.

### Private REST API target

In this section, you create an AgentCore Gateway target that routes to a private REST API endpoint. This applies to any REST API running inside your Amazon VPC such as a containerized microservice. The CreateGatewayTarget API call follows the same pattern as the previous sections. In the openApiSchema field, provide your OpenAPI schema describing the REST API. In the `managedVpcResource` block, provide your VPC ID, subnet IDs, and security group ID. After AgentCore Gateway provisions the Resource Gateway in your VPC, the following architecture diagram shows the end-to-end traffic path.

![Network flow from AgentCore Gateway through a Resource Gateway to an internal Application Load Balancer and backend servers for a private REST API](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/07/REVBLOG-1336-5.png)

Figure 5: Network flow to a private REST API through an internal Application Load Balancer

AgentCore Gateway sends an HTTPS request to your internal endpoint. The Amazon Route 53 private hosted zone resolves that domain to the internal [Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html) (ALB). The request enters the Resource Owner VPC through the Resource Gateway, passes through the ENI governed by your security groups, and arrives at the internal ALB. The ALB terminates TLS on port 443 using an AWS Certificate Manager (ACM) public certificate, then forwards the request over HTTP on port 8000 to the target group containing your backend servers.

### Private certificate authority

The previous sections use certificates that a public CA issues, such as an ACM public certificate. Many internal workloads instead use server certificates that your organization’s private CA issues, for example from [AWS Private Certificate Authority (AWS Private CA)](https://docs.aws.amazon.com/privateca/latest/userguide/PcaWelcome.html) or an enterprise PKI. AgentCore Gateway can trust a private CA natively.

You attach a reference to the CA certificate, not the certificate content, to an individual target when you create or update it. The CA certificate is a PEM-encoded file that you store in [Amazon Simple Storage Service (Amazon S3)](https://aws.amazon.com/s3/) or [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/). The gateway fetches, validates, and encrypts the certificate when you create or update the target, then uses it as the trust anchor for outbound TLS to that target. The following architecture diagram shows the network flow for a private MCP server on Amazon EKS.

![Network flow where an internal Network Load Balancer presents a private CA server certificate that AgentCore Gateway validates against the registered CA certificate](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/07/REVBLOG-1336-6.png)

Figure 6: Network flow for a private MCP server on Amazon EKS using a private certificate authority

AgentCore Gateway sends an HTTPS request to `https://internal.egress-test.example.com/mcp`. The Route 53 private hosted zone resolves the domain to the internal Network Load Balancer. The request enters the Resource Owner VPC through the Resource Gateway, passes through the ENI governed by your security groups, and arrives at the NLB. The NLB presents a server certificate that your private CA issues (`*.egress-test.example.com`) on TLS port 443, and the gateway validates it against the CA certificate that you registered on the target. The NLB then forwards the request over HTTP on port 80 to the NGINX Ingress Controller running on Amazon EKS, which routes it to the appropriate pod.

#### Before you begin

- The target uses a private endpoint (`privateEndpoint`), either managed VPC resource or self-managed Lattice resource.
- The target type is an MCP server (`mcpServer`), an OpenAPI schema (`openApiSchema`), or an HTTP passthrough target.
- The certificate is a PEM-encoded X.509 CA certificate with the basic constraints extension set to `CA:TRUE`. The gateway rejects a leaf (end-entity) certificate.
- The certificate is within its validity window, and the PEM file, including the full chain, is no larger than 16 KB.
- If you store the certificate in Amazon S3, the bucket is in the same AWS Region as the gateway.
- The server certificate that your endpoint presents chains to the CA certificate and matches the target host name.

#### Grant the execution role access to the certificate

The gateway fetches the CA certificate using the gateway execution role. Grant `s3:GetObject` on the certificate object for an Amazon S3 source, or `secretsmanager:GetSecretValue` on the secret for an AWS Secrets Manager source. If the object or secret is encrypted with a customer managed AWS Key Management Service (AWS KMS) key, also grant permission to decrypt with that key. The CA certificate is public information, but scope these permissions to the specific object or secret rather than the whole bucket or all secrets.

#### Register the CA certificate on the target

Add the `certificateConfigurations` field to your CreateGatewayTarget call. The array must contain exactly one entry, and the entry must set exactly one source, either `s3` or `secretsManager`. The following example registers a CA certificate from Amazon S3 on a private MCP server target.

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

To use AWS Secrets Manager instead, replace the `s3` block with the following. The secret must be a string secret, not a binary secret.

```
"certificateConfigurations": [
  {
    "secretsManager": {
      "secretArn": "arn:aws:secretsmanager:us-west-2:<ACCOUNT_ID>:secret:private-ca-AbCdEf"
    }
  }
]
```

We recommend that you set `bucketOwnerAccountId` for an Amazon S3 source. Amazon S3 verifies it against the bucket owner, which protects against the gateway reading a certificate from a bucket in an unexpected account.

#### Validation, rotation, and monitoring

- **Validation is asynchronous.** Only the field formats and the exactly-one-source rule are rejected immediately. Problems such as an expired certificate, a leaf certificate, a missing object or secret, or an oversized file cause the target to reach `FAILED` (create) or `UPDATE_UNSUCCESSFUL` (update). Check `statusReasons` on the target for details. A failed update doesn’t replace the certificate that the target already uses.
- **Rotate before expiry.** When the certificate expires, the TLS handshake fails and tool invocations to the target fail. Call UpdateGatewayTarget with the new CA certificate to replace it. Existing open connections can continue to use the previous certificate until the gateway recycles them.
- **Monitor expiry.** For targets with a private CA, the gateway emits the Amazon CloudWatch metric `EarliestCertificateDaysToExpiry`, the number of days until the earliest expiration across the certificates in the file. Create a CloudWatch alarm that triggers well before the value reaches zero. A negative value means the certificate has expired.
- **Plan for revocation yourself.** The gateway doesn’t check certificate revocation lists (CRLs) or use OCSP, and it trusts any certificate that chains to the configured CA until the certificate expires. To stop trusting a certificate, update the target with a CA certificate that no longer chains to it. To revert to public CA trust, call UpdateGatewayTarget and omit `certificateConfigurations`.

## Clean up

To avoid ongoing charges, delete all resources created in this walkthrough. For reference, see the AgentCore Gateway VPC egress [pricing page](https://aws.amazon.com/bedrock/agentcore/pricing/). Additionally, Amazon EKS clusters, load balancers, and API Gateway endpoints incur charges while running. Verify that your resources are deleted to stop charges. If you followed the GitHub [sample](https://github.com/awslabs/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastructure/01-gateway/03-private-connectivity/connect-gateway-to-private-resources), make sure to run the cleanup section at the end of each Jupyter Notebook.

If you used managed VPC resource mode, deleting the Gateway Target removes the associated Amazon VPC Resource Gateway.

```
aws bedrock-agentcore delete-gateway-target \
    --gateway-identifier <gateway-id> \
    --target-id <target-id>
```

## Conclusion

As AI agents take on more complex tasks, they need secure access to the tools and services that power your business, many of which live inside private networks. With AgentCore Gateway VPC egress, your agents can reach private MCP servers, internal APIs, databases, and on-premises systems without exposing them to the public internet. Managed VPC resource mode integrates directly with your existing VPC and requires minimal configuration. Self-managed lattice resource mode gives you fine-grained control but requires additional setup. Both route traffic through a Resource Gateway that doesn’t leave the AWS network.

## Next steps

- Identify one internal API or MCP server in your environment that would benefit from AI agent access.
- Review your existing Amazon VPC architecture to determine which mode (Managed VPC Resource or Self-Managed Lattice Resource) fits your requirements.
- Review the Amazon Bedrock AgentCore Gateway [documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-vpc-egress.html) for additional configuration options.
- Explore the Amazon VPC Lattice Resource Gateway [documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/vpc-egress-private-endpoints.html) for cross-account scenarios.
- For more integration patterns and advanced configurations, see the [GitHub samples](https://github.com/awslabs/agentcore-samples/tree/main/01-features/07-centralize-and-govern-your-ai-infrastructure/01-gateway/03-private-connectivity/connect-gateway-to-private-resources).

## About the authors
