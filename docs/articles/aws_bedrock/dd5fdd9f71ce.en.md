---
vendor: aws_bedrock
title: Accelerate development with the Amazon Bedrock AgentCore MCP server
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/accelerate-development-with-the-amazon-bedrock-agentcore-mcpserver
date: 2025-10-02
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 1c9408f65653
---

# Accelerate development with the Amazon Bedrock AgentCore MCP server

Today, we’re excited to announce the Amazon Bedrock AgentCore Model Context Protocol (MCP) Server. With built-in support for runtime, gateway integration, identity management, and agent memory, the AgentCore MCP Server is purpose-built to speed up creation of components compatible with Bedrock AgentCore. You can use the AgentCore MCP server for rapid prototyping, production AI solutions, or to scale your agent infrastructure for your enterprise.

Agentic IDEs like [Kiro](https://kiro.dev/), [Amazon Q Developer for CLI](https://aws.amazon.com/developer/learning/q-developer-cli/), [Claude Code](https://claude.com/product/claude-code), [GitHub Copilot](https://github.com/features/copilot), and [Cursor](https://cursor.com/), along with sophisticated MCP servers are transforming how developers build AI agents. What typically takes significant time and effort, for example learning about Bedrock AgentCore services, integrating Runtime and Tools Gateway, managing security configurations, and deploying to production can now be completed in minutes through conversational commands with your coding assistant.

In this post we introduce the new AgentCore MCP server and walk through the installation steps so you can start vibe coding on AgentCore.

## AgentCore MCP server capabilities

The AgentCore MCP server brings a new agentic development experience to AWS, providing specialized tools that automate the complete agent lifecycle, eliminate the steep learning curve, and reduce development friction that can slow innovation cycles. To address specific agent development challenges the AgentCore MCP server:

- **Transforms agents for AgentCore Runtime integration** by providing guidance to your coding assistant on the minimum functionality changes needed—adding Runtime library imports, updating dependencies, initializing apps with `BedrockAgentCoreApp()`, converting entrypoints to decorators, and changing direct agent calls to payload handling—while preserving your existing agent logic and Strands Agents features.
- **Automates development environment provisioning** by handling the complete setup process through your coding assistant: installing required dependencies (bedrock-agentcore SDK, bedrock-agentcore-starter-toolkit CLI helpers, strands-agents SDK), configuring AWS credentials and AWS Regions, defining execution roles with Bedrock AgentCore permissions, setting up ECR repositories, and creating .bedrock_agentcore.yaml configuration files.
- **Simplifies tool integration with Bedrock AgentCore Gateway** for seamless agent-to-tool communication in the cloud environment.
- **Enables simple agent invocation and testing** by providing natural language commands through your coding assistant to invoke provisioned agents on AgentCore Runtime and verify the complete workflow, including calls to AgentCore Gateway tools when applicable.

## Layered approach

When using the AgentCore MCP server with your favorite client, we encourage you to consider a layered architecture designed to provide comprehensive AI agent development support:

- **Layer 1: Agentic IDE or client** – Use Kiro, Amazon Q Developer for CLI, Claude Code, Cursor, VS Code extensions, or another natural language interface for developers. For very simple tasks, agentic IDEs are equipped with the right tools to look up documentation and perform tasks specific to Bedrock AgentCore. However, with this layer alone, developers may observe sub-optimal performance across AgentCore developer paths.
- **Layer 2: AWS service documentation **– Install the [AWS Documentation MCP Server ](https://awslabs.github.io/mcp/servers/aws-documentation-mcp-server/)for comprehensive AWS service documentation, including context about Bedrock AgentCore.
- **Layer 3: Framework documentation **– Install the [Strands](https://github.com/strands-agents/mcp-server), [LangGraph](https://github.com/langchain-ai/mcpdoc), or other framework docs MCP servers or use the llms.txt for framework-specific context.
- **Layer 4: SDK documentation** – Install the MCP or use the llms.txt for the Agent Framework SDK and Bedrock AgentCore SDK for a combined documentation layer that covers the Strands Agents SDK documentation and Bedrock AgentCore API references.
- **Layer 5: Steering files** – Task-specific guidance for more complex and repeated workflows. Each IDE has a different approach to using steering files (for example, see [Steering](https://kiro.dev/docs/steering/) in the Kiro documentation).

Each layer builds upon the previous one, providing increasingly specific context so your coding assistant can handle everything from basic AWS operations to complex agent transformations and deployments.

## Installation

To get started with the Amazon Bedrock AgentCore MCP server you can use the one-click install on the [Github repository](https://github.com/awslabs/mcp/tree/main/src/amazon-bedrock-agentcore-mcp-server).

Each IDE integrates with an MCP differently using the mcp.json file. Review the MCP documentation for your IDE, such as [Kiro](https://kiro.dev/docs/mcp/), [Cursor](https://cursor.com/docs/context/mcp), [Amazon Q Developer for CLI](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/qdev-mcp.html), and [Claude Code](https://docs.claude.com/en/docs/claude-code/mcp) to determine the location of the mcp.json.

| **Client** | **Location of mcp.json** | **Documentation** |
| --- | --- | --- |
| Kiro | .kiro/settings/mcp.json | [https://kiro.dev/docs/mcp/](https://kiro.dev/docs/mcp/) |
| Cursor | .cursor/mcp.json | [https://cursor.com/docs/context/mcp](https://cursor.com/docs/context/mcp) |
| Amazon Q Developer for CLI | ~/.aws/amazonq/mcp.json | [https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/qdev-mcp.html](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/qdev-mcp.html) |
| Claude Code | ~/.claude/mcp.json | [https://docs.claude.com/en/docs/claude-code/mcp](https://docs.claude.com/en/docs/claude-code/mcp) |

Note that the above paths and/or json files may not exist by default in your system, and you may need to manually add them. For example, in Kiro, you can add add the below contents to `.kiro/settings/mcp.json`. If this path doesn’t exist, see [Creating Configuration Files](https://kiro.dev/docs/mcp/configuration/#creating-configuration-files).

Use the following in your mcp.json:

```
{
  "mcpServers": {
    "bedrock-agentcore-mcp-server": {
      "command": "uvx",
      "args": [
        "awslabs.amazon-bedrock-agentcore-mcp-server@latest"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "disabled": false,
      "autoApprove": [
        "search_agentcore_docs",
        "fetch_agentcore_doc"
      ]
    }
  }
}
```

For example, here is what the IDE looks like on Kiro, with the AgentCore MCP server and the two tools, `search_agentcore_docs` and `fetch_agentcore_doc`, connected:

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/02/ML-19737-2.jpg)

## Using the AgentCore MCP server for agent development

While we show demos for various use cases below using the Kiro IDE, the AgentCore MCP server has also been tested to work on Claude Code, Amazon Q CLI, Cursor, and the VS Code Q plugin. First, let’s take a look at a typical agent development lifecycle using AgentCore services (remember that this is only one example with the tools available, and you are free to explore more such use cases simply by instructing the agent in your favorite Agentic IDE):

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/02/ML-19737-4.png)

The agent development lifecycle follows these steps:

- The user takes a local set of tools or MCP servers and  Creates a lambda target for AgentCore Gateway; or Deploys the MCP server as-is on AgentCore Runtime
- The user prepares the actual agent code using a preferred framework like Strands Agents or LangGraph. The user can either:  Start from scratch (the server can fetch docs from the Strands Agents or LangGraph documentation) Start from fully or partially working agent code
- The user asks the agent to transform the code into a format compatible with AgentCore Runtime with the intention to deploy the agent later. This causes the agent to:  Write an appropriate requirements.txt file import necessary libraries including bedrock_agentcore decorate the main handler (or create one) to access the core agent calling logic or input handler
- The user may then ask the agent to deploy to AgentCore Runtime. The agent can look up documentation and can use the AgentCore CLI to deploy the agent code to Runtime
- The user can test the agent by asking the agent to do so. The AgentCore CLI command required for this is written and executed by the client
- The user then asks to modify the code to use the deployed AgentCore Gateway MCP server within this AgentCore Runtime agent.  The agent modifies the original code to add an MCP client that can call the deployed gateway The agent then deploys a new version v2 of the agent to Runtime The agent then tests this integration with a new prompt

Here is a demo of the MCP server working with Cursor IDE. We see the agent perform the following steps:

- Transform the weather_agent.py to be compatible with AgentCore runtime
- Use the AgentCore CLI to deploy the agent
- Test the deployed agent with a successful prompt

Here’s another example of deploying a LangGraph agent to AgentCore Runtime with the Cursor IDE performing similar steps as seen above.

## Clean up

If you’d like to uninstall the MCP server, follow the MCP documentation for your IDE, such as [Kiro](https://kiro.dev/docs/mcp/), [Amazon Q Developer for CLI](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/command-line.html), [Cursor](https://cursor.com/docs/context/mcp), and [Claude Code](https://docs.claude.com/en/docs/claude-code/mcp) for instructions.

## Conclusion

In this post, we showed how you can use the AgentCore MCP server with your favorite Agentic IDE of choice to speed up your development workflows.

We encourage you to review the [Github repository](https://github.com/awslabs/mcp/tree/main/src/amazon-bedrock-agentcore-mcp-server), as well read through and use the following resources in your development:

- [Amazon Bedrock AgentCore CLI documentation](https://aws.github.io/bedrock-agentcore-starter-toolkit/api-reference/cli.html)
- [Strands Agents MCP Server](https://github.com/strands-agents/mcp-server)
- [LangGraph llms.txt](https://langchain-ai.github.io/langgraph/llms-txt-overview/)

We encourage you to try out the AgentCore MCP server and provide any feedback through issues in our [GitHub repository](https://github.com/awslabs/mcp/tree/main/src/amazon-bedrock-agentcore-mcp-server).

### About the authors
