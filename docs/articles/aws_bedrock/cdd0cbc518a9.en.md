---
vendor: aws_bedrock
title: Introducing Amazon Bedrock AgentCore Identity: Securing agentic AI at scale
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/introducing-amazon-bedrock-agentcore-identity-securing-agentic-ai-at-scale
date: 2025-08-15
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 17864ff0d5f5
---

# Introducing Amazon Bedrock AgentCore Identity: Securing agentic AI at scale

We’re excited to introduce [Amazon Bedrock AgentCore Identity](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity.html), a comprehensive identity and access management service purpose-built for AI agents. With AgentCore Identity AI, agent developers and administrators can securely access AWS resources and third-party tools such as GitHub, Salesforce, or Slack. AgentCore Identity provides robust identity and access management at scale so that agents can access your resources or tools either on behalf of users or themselves with pre-authorized user consent to minimize the need for custom access controls and identity infrastructure development.

As organizations deploy AI agents into production environments, they face a critical challenge: how to securely manage identity and access at scale. Applications need to authenticate users for invoking AI agents, and these agents need to access multiple tools and services, maintain audit trails, and integrate with existing enterprise identity systems—all while avoiding data leakage and maintaining compliance with organizational requirements. These requirements become exponentially more complex when agents operate across disparate systems, act on behalf of different users, and need to access resources and tools in both AWS and external third-party services.

In this post, we examine how AgentCore Identity solves these agentic AI security challenges. We start by exploring the core identity and security needs for enterprise AI agents, then dive into the architecture of AgentCore Identity for managing agent identities and credentials. We then demonstrate how to implement secure agent authentication through a practical customer support use case and conclude with best practices for enterprise-grade security at scale.

## Agentic AI security at scale

Building secure AI agents for enterprise deployment presents unique identity and access management challenges that traditional application security models weren’t designed to handle. The following diagram illustrates the areas where access control through authentication and authorization is required in a typical agentic workflow.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/14/ML-19464-image-1.png)

Let’s examine the specific security requirements that make agentic AI systems particularly complex:

### Inbound authentication: Who can access the agent?

When users or applications invoke an AI agent, you need to verify their identity and determine what they’re authorized to do. This inbound authentication must support multiple patterns:

- **User authentication**: Verifying human users accessing agents through web applications or APIs
- **Service authentication**: Validating other services or agents that need to communicate with your agent
- **Multi-tenant isolation**: Blocking users from different organizations from accessing each other’s data

### Outbound authentication: What can the agent access?

AI agents need to interact with various resources and tools to accomplish tasks. This outbound authentication presents its own challenges:

- **Acting on behalf of users**: Agents often need to access user-specific resources (such as their Google Drive or Slack workspace) with appropriate permissions
- **Service-to-service authentication**: Agents might need their own credentials to access shared resources or APIs
- **Token management**: Securely storing and managing OAuth access tokens, API keys, and other credentials without exposing them to potential threats

### Enterprise integration requirements

Modern enterprises have invested heavily in identity infrastructure, and AI agents must integrate seamlessly:

- **Identity provider compatibility**: Supporting existing systems such as Amazon Cognito, Okta, or Microsoft Entra ID (formerly Azure Active Directory).
- **Standard protocols**: Using OAuth 2.0, OpenID Connect, and other industry standards
- **Robust access controls**: Implementing least-privilege access and continuous verification

### Compliance and auditability

For financial services companies and other regulated industries, every agent action must be traceable:

- **Comprehensive audit trails**: Logging who accessed what, when, and on whose behalf
- **Data isolation**: Avoiding cross-contamination between different users’ data
- **Regulatory compliance**: Meeting requirements for data protection and privacy regulations

Without a purpose-built solution, developers spend months building custom authentication systems, implementing token vaults, managing OAuth flows, and creating audit mechanisms—all while trying to maintain security best practices.

## AgentCore Identity: Main features

AgentCore Identity addresses most of these challenges by providing a centralized capability for managing agent identities, securing credentials, and supporting seamless integration with AWS and third-party services through Sigv4, standardized OAuth 2.0 flows, and API keys.

The main components provided with AgentCore Identity include:

- **Agent identity directory:** Create, manage, and organize agent and workload identities through a unified directory service that acts as the single source of truth for the agent identities within your organization.
- **Agent authorizer:** Validates whether a user or service is allowed to invoke an agent or not.
- **Resource credential provider:** Stores the configuration for an agent that needs to get credentials to access downstream resource servers. It subsequently retrieves credentials of downstream resource servers such as Google or GitHub to access them, for actions like in example fetching emails from Gmail or adding a meeting to Google Calendar.
- **Resource token vault:** Stores user’s OAuth access tokens and allows agents to retrieve them securely to perform actions on behalf of users and reduce unnecessary user consents.

AgentCore Identity implements authentication and authorization controls that verify each request independently, requiring explicit verification for access attempts regardless of source. It integrates seamlessly with AWS services while also enabling agents to securely access external tools and services. You can use AgentCore Identity for securing access to the agents, and for securing access to the resources or tools that your agents access on behalf of users, as shown in the following diagram.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/14/ML-19464-image-2.png)

Whether you’re building simple automation scripts or complex multi-agent systems, AgentCore Identity provides the identity foundation to help your applications operate securely and efficiently.

### Distinct agent identities

Each agent receives a unique identity with associated metadata (such as name, Amazon Resource Name (ARN), OAuth return URLs, created time, last updated time) that can be managed centrally across your organization. This workload identity approach means agents are first-class citizens in your security architecture, not just applications masquerading as users.

### Dual authentication model

AgentCore Identity implements a dual authentication approach:

- **Inbound authentication**: Validates users and applications attempting to invoke agents  Supports [AWS Identity and Access Management (IAM)](https://aws.amazon.com/iam) credentials (SigV4) for AWS authentication Integrates with OAuth 2.0 or OpenID Connect identity providers Provides JSON Web Token (JWT) token validation
- **Outbound authentication**: Enables agents to securely access resources:  The token vault provides security for storing OAuth 2.0 access tokens, OAuth client credentials, and API keys with comprehensive encryption at rest and in transit. Supports both two-legged OAuth (machine-to-machine) and three-legged OAuth (on behalf of users) Pre-configured integrations with authorization providers for popular services such as GitHub, Slack, or Salesforce.

### Secure token vault

The secure token vault is a key element of the security model for AgentCore Identity:

- **Encryption**: Credentials are encrypted using customer managed [AWS Key Management Service (AWS KMS)](https://aws.amazon.com/kms) keys
- **Access control**: Credentials bound to specific agent-user combinations
- **Zero token sharing**: Avoids credentials from being accessed across users or agents

### Seamless SDK integration

Seamless integration with the AgentCore SDK through declarative annotations such as `@requires_access_token` and `@requires_api_key` that automatically handle credential retrieval and injection, reducing boilerplate code and potential security vulnerabilities.

## How to get started

Let’s walk through a practical example of deploying a developer productivity agent that helps engineering teams manage their GitHub repositories, track issues, and streamline their development workflow, as shown in the following diagram.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/14/ML-19464-image-3.png)

This agent will authenticate developers using OAuth and then access GitHub to help them manage repositories, track issues, and review pull requests on their behalf. You can follow the complete example in [this notebook](https://github.com/awslabs/amazon-bedrock-agentcore-samples/blob/main/01-tutorials/03-AgentCore-identity/06-Outbound_Auth_Github/runtime_with_strands_and_egress_github_3lo.ipynb).

### Prerequisites

- AWS account with Amazon Bedrock AgentCore access. For more information review [Permissions for AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-permissions.html) documentation.
- Python 3.10 or later
- Docker or Finch installed
- GitHub OAuth App configured (see [GitHub documentation](https://docs.github.com/en/developers/apps/building-oauth-apps/creating-an-oauth-app))
- Basic understanding of [OAuth 2.0](https://oauth.net/2/)

### Step 1: Set up your identity provider

First, configure your identity provider for agent users. You can use an OAuth 2.0-compatible identity provider of your choice. For this example, we use [Amazon Cognito](https://aws.amazon.com/cognito) with a handy script provided in [the notebook](https://github.com/awslabs/amazon-bedrock-agentcore-samples/blob/main/01-tutorials/03-AgentCore-identity/06-Outbound_Auth_Github/runtime_with_strands_and_egress_github_3lo.ipynb). We can then map the attributes required either directly or by relying on [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/) for storing and retrieving this information securely.

```
from bedrock_agentcore_starter_toolkit import Runtime
from boto3.session import Session
boto_session = Session()
region = boto_session.region_name
# Configure your Cognito User Pool
discovery_url = f'https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/openid-configuration'
client_id = 'your-cognito-app-client-id'
```

### Step 2: Create your agent with JWT authentication

Configure your agent runtime to accept JWT tokens from your identity provider:

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

### Step 3: Configure OAuth credential provider for GitHub

Set up the OAuth provider to enable your agent to access GitHub services. AgentCore Identity provides preconfigured settings for popular services:

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

### Step 4: Implement the agent with automatic token handling

Create tools with AgentCore SDK annotations to automatically handle the three-legged OAuth process. The `@requires_access_token` decorator manages the entire OAuth flow, including user consent. You can check the full code for this example in [the notebook](https://github.com/awslabs/amazon-bedrock-agentcore-samples/blob/main/01-tutorials/03-AgentCore-identity/06-Outbound_Auth_Github/runtime_with_strands_and_egress_github_3lo.ipynb), but we highlight the key parts in the snippet below:

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

### Step 5: Deploy and test

Deploy your agent using the AgentCore CLI:

```
bedrock-agentcore runtime launch
```

When users invoke your agent with their JWT token, AgentCore Identity will:

- Validate the incoming JWT token
- Establish the user’s identity
- Establish its own identity and obtain a workload access token for the user and agent pair
- When the agent needs GitHub access, use the workload access token to automatically handle the user consent as part of the three-legged OAuth flow by providing an authorization URL
- Securely store and retrieve tokens from the vault
- Inject tokens into your function calls

Let’s explore a demonstration of how an application would look like for this example.

As you can see, the agent seamlessly authenticates users and accesses their GitHub repositories without exposing credentials or requiring manual token management. The entire OAuth flow, including user consent and secure token storage, is handled automatically by AgentCore Identity.

### Clean up

Once you’ve completed the example provided, you can clean up the resources with the commands below to avoid unnecessary charges in your account. Remember to replace the provider ID with your own ID.

```
# Delete the agent runtime
bedrock-agentcore runtime delete --agent-name github-support-agent

# Delete the OAuth credential provider
aws bedrock-agentcore-identity delete-oauth-credential-provider \
    --provider-id <provider-id>
```

## Integration with AgentCore environment and identity providers

AgentCore Identity is designed to work seamlessly with the broader AgentCore environment and your existing identity infrastructure.

### AgentCore service integration

- **AgentCore Runtime**: Runtime, powered by AgentCore Identity, assigns distinct identities to AI agents and seamlessly integrates with your corporate identity provider such as Okta, Microsoft Entra ID, or Amazon Cognito, among others.
- **AgentCore Gateway**: When using Gateway to expose tools using Model Context Protocol (MCP), AgentCore Identity handles authentication for both incoming agent requests and outgoing tool calls

### Identity provider compatibility

AgentCore Identity supports OAuth 2.0 or OpenID Connect-compatible identity providers, and providers accessible through API keys. For example, Amazon Cognito, Okta, and Microsoft Entra ID, among others.

Customers who use AgentCore Identity through either AgentCore Runtime or AgentCore Gateway, do not incur any additional charges for their use of AgentCore Identity. For other scenarios, you pay for only what you use and are charged based on the number of requests from the agent to AgentCore Identity for an OAuth token or an API key. For more information on pricing, refer to the [AgentCore public pricing](https://aws.amazon.com/bedrock/agentcore/pricing/).

## Security considerations and best practices

When implementing AgentCore Identity, follow these security best practices:

### Principle of least privilege

Minimize security risks by restricting agent access to only essential resources and capabilities:

- Grant agents only the minimum permissions needed
- Regularly audit and review agent permissions

### Agent and user identities based access

Establish clear identity verification and management protocols for both human users and AI agents:

- Provide user identity in a verifiable form
- Manage agent identities

### Token management

Protect authentication credentials through proper token lifecycle management:

- Enable automatic token refresh to minimize credential exposure
- Use `force_authentication=True` for sensitive operations
- Implement token expiration policies appropriate for your use case

### Audit and monitoring

Maintain visibility into agent activities to detect anomalies and ensure compliance with organizational requirements:

- Enable [Amazon CloudWatch](https://aws.amazon.com/cloudwatch) logging for the agent operations
- Set up alerts for unusual authentication patterns
- Regularly review audit logs for compliance

### Multi-tenant security

For software as a service (SaaS) providers and multi-tenant environments:

- Configure separate credential providers per tenant
- Use tenant-specific JWT claims for validation
- Implement additional authorization checks in your agent logic

## Conclusion and future outlook

Amazon Bedrock AgentCore Identity transforms how organizations secure AI agents at scale. By providing purpose-built identity and access management, it extinguishes months of custom development while providing enterprise-grade security. The service’s dual authentication model, secure token vault, and seamless integration with existing identity providers make it possible to deploy agents that can safely operate across organizational boundaries and access diverse resources .As AI agents become more prevalent in enterprise environments, the need for robust identity and access management will only grow. AgentCore Identity provides the foundation for this future, enabling organizations to build agents that are not just intelligent, but also secure, compliance-aligned, and trustworthy.

### Resources to get started

Ready to secure your AI agents with AgentCore Identity? Here are your next steps:

- **Explore the documentation**: Visit the [Amazon Bedrock AgentCore documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)
- **Try the samples**: Check out the [GitHub repository](https://github.com/awslabs/amazon-bedrock-agentcore-samples) with complete examples
- **No cost preview**: You can try AgentCore services at no additional charge until September 16, 2025: [Introducing Amazon Bedrock AgentCore: Securely deploy and operate AI agents at any scale (preview) | AWS News Blog](https://aws.amazon.com/blogs/aws/introducing-amazon-bedrock-agentcore-securely-deploy-and-operate-ai-agents-at-any-scale/)

Start building secure, scalable AI agents today with Amazon Bedrock AgentCore Identity. Transform your proof-of-concept into production-ready systems that meet the highest enterprise security standards.

### About the Authors

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/14/ML-19464-image-4-100x109.png)Rahul Sharma** is a Principal Product Manager-Technical at Amazon Web Services with over 5 years of cumulative product management experience spanning Customer Identity and Access Management (CIAM), Infrastructure as Code (IaC), and most recently the agent identity space.

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/08/14/ML-19464-image-5-100x125.png)Fei Yuan** is a Principal Engineer at AWS. During his 20+ years of experience, Fei has led different teams through various projects across Amazon and AWS, such as Amazon Lending Marketplace, Amazon Payment Services, Alexa ML Secure Computing, Amazon DataZone, Amazon SageMaker data governance, and Amazon Cognito. Most recently, he led the team that launched Amazon Bedrock AgentCore Identity service. Today he focuses on designing and implementing AWS products in the areas of agent identity, workload identity, and customer identity and access management.

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/06/Satveer-1.jpg)Satveer Khurpa** is a Sr. WW Specialist Solutions Architect, Amazon Bedrock at Amazon Web Services, specializing in Amazon Bedrock security. In this role, he uses his expertise in cloud-based architectures to develop innovative generative AI solutions for clients across diverse industries. Satveer uses his deep understanding of generative AI technologies and security principles to design scalable, secure, and responsible applications that unlock new business opportunities and drive tangible value while maintaining robust security postures.

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/10/28/rodzanto.jpg)Antonio Rodriguez** is a Principal Generative AI Specialist Solutions Architect at Amazon Web Services. He helps companies of all sizes solve their challenges, embrace innovation, and create new business opportunities with Amazon Bedrock. Apart from work, he loves to spend time with his family and play sports with his friends.
