---
vendor: aws_bedrock
title: Accelerate development with the Amazon Bedrock AgentCore MCP server
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/accelerate-development-with-the-amazon-bedrock-agentcore-mcpserver
date: 2025-10-02
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 6ce500ab5b86
---

# 使用 Amazon Bedrock AgentCore MCP server 加速开发

今天，我们很高兴宣布推出 Amazon Bedrock AgentCore Model Context Protocol (MCP) Server。借助对 runtime、gateway 集成、身份管理和 agent memory 的内置支持，AgentCore MCP Server 专门为加速创建与 Bedrock AgentCore 兼容的组件而构建。你可以将 AgentCore MCP server 用于快速原型验证、生产级 AI 解决方案，或为企业扩展你的 agent 基础设施。

[Kiro](https://kiro.dev/)、[Amazon Q Developer for CLI](https://aws.amazon.com/developer/learning/q-developer-cli/)、[Claude Code](https://claude.com/product/claude-code)、[GitHub Copilot](https://github.com/features/copilot) 和 [Cursor](https://cursor.com/) 等 Agentic IDE，再加上成熟的 MCP server，正在改变开发者构建 AI agent 的方式。以往需要投入大量时间和精力的工作，例如了解 Bedrock AgentCore 的各项服务、集成 Runtime 与 Tools Gateway、管理安全配置以及部署到生产环境，如今都可以通过与编码助手对话式交互，在几分钟内完成。

在本文中，我们介绍新的 AgentCore MCP server，并逐步演示安装步骤，让你可以开始在 AgentCore 上进行 vibe coding。

## AgentCore MCP server 的能力

AgentCore MCP server 为 AWS 带来了全新的 agentic 开发体验，提供专业化工具来自动化完整的 agent 生命周期、消除陡峭的学习曲线，并减少可能拖慢创新周期的开发摩擦。为应对具体的 agent 开发挑战，AgentCore MCP server 可以：

- **将 agent 转换为可集成 AgentCore Runtime 的形态**：为你的编码助手提供指导，说明所需的最小功能改动——添加 Runtime 库的导入、更新依赖、用 `BedrockAgentCoreApp()` 初始化应用、将入口点转换为装饰器，以及把直接调用 agent 改为处理 payload——同时保留你既有的 agent 逻辑与 Strands Agents 特性。
- **自动化开发环境准备**：通过你的编码助手完成整套设置流程：安装所需依赖（bedrock-agentcore SDK、bedrock-agentcore-starter-toolkit CLI 辅助工具、strands-agents SDK）、配置 AWS 凭证与 AWS Region、定义带有 Bedrock AgentCore 权限的执行角色、设置 ECR 仓库，以及创建 .bedrock_agentcore.yaml 配置文件。
- **简化与 Bedrock AgentCore Gateway 的工具集成**，实现云环境中无缝的 agent 与工具通信。
- **让 agent 的调用与测试变得简单**：通过编码助手提供自然语言命令，即可调用 AgentCore Runtime 上已配置的 agent 并验证完整工作流，包括在适用时调用 AgentCore Gateway 工具。

## 分层方案

在你喜欢的客户端中使用 AgentCore MCP server 时，我们建议你考虑一种分层架构，它可以提供全面的 AI agent 开发支持：

- **第 1 层：Agentic IDE 或客户端** – 使用 Kiro、Amazon Q Developer for CLI、Claude Code、Cursor、VS Code 扩展，或其他面向开发者的自然语言界面。对于非常简单的任务，Agentic IDE 已经配备了合适的工具来查阅文档并执行 Bedrock AgentCore 相关任务。不过，仅靠这一层，开发者在 AgentCore 的各条开发路径上可能会遇到次优的表现。
- **第 2 层：AWS 服务文档 **– 安装 [AWS Documentation MCP Server ](https://awslabs.github.io/mcp/servers/aws-documentation-mcp-server/)以获取全面的 AWS 服务文档，包括关于 Bedrock AgentCore 的上下文。
- **第 3 层：框架文档 **– 安装 [Strands](https://github.com/strands-agents/mcp-server)、[LangGraph](https://github.com/langchain-ai/mcpdoc) 或其他框架文档的 MCP server，或使用 llms.txt 获取框架特定的上下文。
- **第 4 层：SDK 文档** – 安装对应的 MCP，或使用 Agent Framework SDK 与 Bedrock AgentCore SDK 的 llms.txt，形成一个合并的文档层，涵盖 Strands Agents SDK 文档与 Bedrock AgentCore API 参考。
- **第 5 层：Steering 文件** – 针对更复杂、更重复的工作流提供任务特定指导。每个 IDE 使用 steering 文件的方式各不相同（例如可参阅 Kiro 文档中的 [Steering](https://kiro.dev/docs/steering/)）。

每一层都建立在前一层之上，提供越来越具体的上下文，使你的编码助手能够处理从基础 AWS 操作到复杂的 agent 转换与部署在内的所有工作。

## 安装

要开始使用 Amazon Bedrock AgentCore MCP server，你可以使用 [Github repository](https://github.com/awslabs/mcp/tree/main/src/amazon-bedrock-agentcore-mcp-server) 上的一键安装。

每个 IDE 通过 mcp.json 文件与 MCP 的集成方式各不相同。请查阅你所使用 IDE 的 MCP 文档，例如 [Kiro](https://kiro.dev/docs/mcp/)、[Cursor](https://cursor.com/docs/context/mcp)、[Amazon Q Developer for CLI](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/qdev-mcp.html) 和 [Claude Code](https://docs.claude.com/en/docs/claude-code/mcp)，以确定 mcp.json 的位置。

| **客户端** | **mcp.json 的位置** | **文档** |
| --- | --- | --- |
| Kiro | .kiro/settings/mcp.json | [https://kiro.dev/docs/mcp/](https://kiro.dev/docs/mcp/) |
| Cursor | .cursor/mcp.json | [https://cursor.com/docs/context/mcp](https://cursor.com/docs/context/mcp) |
| Amazon Q Developer for CLI | ~/.aws/amazonq/mcp.json | [https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/qdev-mcp.html](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/qdev-mcp.html) |
| Claude Code | ~/.claude/mcp.json | [https://docs.claude.com/en/docs/claude-code/mcp](https://docs.claude.com/en/docs/claude-code/mcp) |

请注意，上述路径和/或 json 文件在你的系统中默认可能并不存在，你可能需要手动添加它们。例如在 Kiro 中，你可以将以下内容添加到 `.kiro/settings/mcp.json`。如果该路径不存在，请参阅 [Creating Configuration Files](https://kiro.dev/docs/mcp/configuration/#creating-configuration-files)。

在 mcp.json 中使用以下内容：

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

例如，下图展示了在 Kiro 上接入 AgentCore MCP server 以及 `search_agentcore_docs` 和 `fetch_agentcore_doc` 两个工具后 IDE 的样子：

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/02/ML-19737-2.jpg)

## 使用 AgentCore MCP server 进行 agent 开发

虽然下面的演示使用 Kiro IDE 覆盖了多种用例，但 AgentCore MCP server 也已在 Claude Code、Amazon Q CLI、Cursor 和 VS Code Q 插件上测试可用。首先，我们来看一个使用 AgentCore 服务的典型 agent 开发生命周期（请记住，这只是现有工具下的一个示例，你完全可以只通过向你喜欢的 Agentic IDE 中的 agent 下达指令，去探索更多此类用例）：

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/02/ML-19737-4.png)

agent 开发生命周期包含以下步骤：

- 用户拿一组本地工具或 MCP server，然后 为 AgentCore Gateway 创建一个 lambda 目标；或者 将 MCP server 原样部署到 AgentCore Runtime
- 用户使用偏好的框架（如 Strands Agents 或 LangGraph）准备实际的 agent 代码。用户可以选择： 从零开始（server 可以从 Strands Agents 或 LangGraph 文档中获取资料） 从完全或部分可用的 agent 代码开始
- 用户要求 agent 将代码转换为与 AgentCore Runtime 兼容的格式，以便后续部署该 agent。这会促使 agent： 编写合适的 requirements.txt 文件 import 包括 bedrock_agentcore 在内的必要库 为主 handler 添加装饰器（或创建新的 handler），以接入核心的 agent 调用逻辑或输入处理器
- 随后用户可以要求 agent 部署到 AgentCore Runtime。agent 会查阅文档，并可使用 AgentCore CLI 将 agent 代码部署到 Runtime
- 用户可以让 agent 自行测试已部署的 agent。所需的 AgentCore CLI 命令由客户端写入并执行
- 之后用户要求修改代码，以便在这个 AgentCore Runtime agent 内使用已部署的 AgentCore Gateway MCP server。agent 修改原始代码，添加一个可以调用已部署 gateway 的 MCP client；然后 agent 将新版本 v2 部署到 Runtime；随后 agent 用新的 prompt 测试这一集成

以下是 MCP server 与 Cursor IDE 配合工作的演示。可以看到 agent 执行了以下步骤：

- 将 weather_agent.py 转换为与 AgentCore runtime 兼容
- 使用 AgentCore CLI 部署 agent
- 用一个成功的 prompt 测试已部署的 agent

这里是另一个示例：在 Cursor IDE 中把 LangGraph agent 部署到 AgentCore Runtime，执行的步骤与上面类似。

## 清理

如果你想卸载该 MCP server，请按照你所使用 IDE 的 MCP 文档操作，例如 [Kiro](https://kiro.dev/docs/mcp/)、[Amazon Q Developer for CLI](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/command-line.html)、[Cursor](https://cursor.com/docs/context/mcp) 和 [Claude Code](https://docs.claude.com/en/docs/claude-code/mcp)。

## 结论

在本文中，我们展示了如何将 AgentCore MCP server 与你喜欢的 Agentic IDE 搭配使用，以加速你的开发工作流。

我们建议你查看 [Github repository](https://github.com/awslabs/mcp/tree/main/src/amazon-bedrock-agentcore-mcp-server)，并在开发中阅读和使用以下资源：

- [Amazon Bedrock AgentCore CLI documentation](https://aws.github.io/bedrock-agentcore-starter-toolkit/api-reference/cli.html)
- [Strands Agents MCP Server](https://github.com/strands-agents/mcp-server)
- [LangGraph llms.txt](https://langchain-ai.github.io/langgraph/llms-txt-overview/)

我们鼓励你试用 AgentCore MCP server，并通过我们的 [GitHub repository](https://github.com/awslabs/mcp/tree/main/src/amazon-bedrock-agentcore-mcp-server) 中的 issue 提供反馈。

### 关于作者
