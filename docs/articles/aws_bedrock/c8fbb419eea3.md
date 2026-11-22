---
vendor: aws_bedrock
title: Build generative UI for AI agents on Amazon Bedrock AgentCore with the AG-UI protocol
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-generative-ui-for-ai-agents-on-amazon-bedrock-agentcore-with-the-ag-ui-protocol
date: 2026-06-30
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 26cb1c1d7e59
---

# 用 AG-UI 协议在 Amazon Bedrock AgentCore 上为 AI agent 构建生成式 UI

AI agent 能做的远不止聊天。有了合适的协议，agent 可以在你的对话中内联渲染交互式图表、实时更新共享画布，或在执行中途暂停、等你批准后再继续。这些交互（生成式 UI、共享状态和人机协同）需要一种标准方式，让 agent 后端能把动态事件传达给前端。

[AG-UI](https://docs.ag-ui.com/introduction)（Agent-User Interaction Protocol）是一个定义该标准的开放协议。它可配合多种 agent 框架（Strands Agents、LangGraph、CrewAI）与前端库（React、Angular、Vue）使用。借助 AG-UI，你的 agent 代码与前端代码保持解耦。你为后端挑最合适的框架、为前端挑最合适的库，由 AG-UI 把它们连接起来。

[Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) 是 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 生成式 AI 服务家族的一员。AgentCore 是一个 agentic 平台，用任何框架、任何模型，安全地大规模构建、部署和运营 AI agent。

本文介绍 AG-UI 如何集成进 [Fullstack AgentCore Solution Template（FAST）](https://github.com/awslabs/fullstack-solution-template-for-agentcore)，从而在 Amazon Bedrock AgentCore 上构建交互式 agent 前端。随后我们展示 [CopilotKit](https://copilotkit.ai/) 如何用生成式 UI、共享状态和人机协同交互来扩展这套方案，全部部署在 Amazon Bedrock AgentCore 上。

## 方案概览

Amazon Bedrock AgentCore Runtime 提供安全、无服务器且专门构建的托管环境，用于部署和运行 AI agent 或工具。AgentCore Runtime 支持多种 agent 协议。Model Context Protocol（MCP）连接 agent 与工具，Agent2Agent（A2A）连接 agent 与其他 agent，而 AG-UI 连接 agent 与用户。当你部署带有 AG-UI 协议标志的 agent 容器时，AgentCore 充当透明代理。它处理认证（Signature Version 4 [SigV4]，或通过 Amazon Cognito 的 OAuth 2.0）、会话隔离、扩缩容和可观测性。你的容器在 8080 端口上为 AG-UI 请求暴露 `POST /invocations`，为健康检查暴露 `GET /ping`。AgentCore 原样转发请求。更多细节请参阅 [在 AgentCore Runtime 中部署 AGUI 服务器](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-agui.html)。

FAST 是一个可直接部署的起步项目。它把 AgentCore Runtime、Gateway、Identity、Memory 和 Code Interpreter 与 React 前端、Amazon Cognito 认证连接起来，全部用 AWS Cloud Development Kit（AWS CDK）定义。它自带面向 Strands Agents、LangGraph 和 Claude Agent SDK 的 agent 模式。FAST v0.4.1 新增了两个共享同一个前端解析器的 AG-UI 模式（`agui-strands-agent` 与 `agui-langgraph-agent`）。FAST 架构与部署的完整演练请参阅[用面向 Amazon Bedrock AgentCore 的全栈起步模板加速 agentic 应用开发](https://aws.amazon.com/blogs/machine-learning/accelerate-agentic-application-development-with-a-full-stack-starter-template-for-amazon-bedrock-agentcore/)。

这套方案有两层。**FAST 中的 AG-UI** 提供两个新的 agent 模式，以及一个能同时处理两者的前端解析器，因此前端无需知道自己跑的是哪个 agent 框架。**CopilotKit + FAST** 是一个独立示例，用 CopilotKit 替换 FAST 内置的聊天 UI。它增加了生成式 UI（内联图表与组件）、双向共享状态（一个 todo 画布）和人机协同交互（一个会议排程器，会让 agent 暂停并等待你的输入）。两层都部署在 AgentCore Runtime 上，带 Cognito 认证、用于 MCP 工具连接的 AgentCore Gateway，以及用于持久对话的 AgentCore Memory。

架构总览。前端通过 AG-UI 事件与 AgentCore Runtime 通信。AgentCore 负责认证、扩缩容和会话隔离。agent 运行时把框架特定的事件转换为 AG-UI 协议。

## 演练

本次演练分两部分。首先，我们展示 AG-UI 模式在 FAST 中如何运作，以及单个前端解析器如何同时处理 Strands 和 LangGraph 后端。其次，我们部署 CopilotKit 示例，演示 AgentCore 上的生成式 UI、共享状态和人机协同。

源代码：

- [FAST 仓库（含 AG-UI 模式）](https://github.com/awslabs/fullstack-solution-template-for-agentcore)。
- [CopilotKit + FAST 示例](https://github.com/aws-samples/sample-FAST-applications/tree/main/samples/copilotkit-generative-ui)。

### 前置条件

本次演练需要具备以下前置条件：

- 一个 [AWS 账户](https://signin.aws.amazon.com/signin?redirect_uri=https%3A%2F%2Fportal.aws.amazon.com%2Fbilling%2Fsignup%2Fresume&client_id=signup)，具备 AWS CloudFormation、Amazon Elastic Container Registry（Amazon ECR）、Amazon Bedrock AgentCore、Amazon Cognito 和 AWS Amplify 的权限。
- 已安装并配置 [AWS Command Line Interface（AWS CLI）v2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)。
- 已安装 [AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/getting-started.html)。
- [Node.js 18 或更高版本](https://nodejs.org/) 以及 Python 3.11 或更高版本。
- Docker 正在运行，用于构建容器。
- 在 Amazon Bedrock 控制台中为 agent 使用的模型启用了模型访问权限。

### FAST 中的 AG-UI：一个解析器，两种框架

`agui-strands-agent` 模式把 Strands Agent 包装在来自 `ag-ui-strands` 库的 `StrandsAgent` 中。该包装器会自动把 Strands 的流式事件转换为 AG-UI 的 Server-Sent Events。

每个请求都会用 Gateway MCP 工具创建一个全新的 agent。AgentCore Memory 通过 session-manager provider 按 thread 挂载，因此对话历史能在 AgentCore Runtime 扩缩容时保持。Memory 是可选项：当 `MEMORY_ID` 未设置时，provider 返回 `None`：

```
# patterns/agui-strands-agent/agent.py
from ag_ui_strands import StrandsAgent, StrandsAgentConfig
from bedrock_agentcore.runtime import BedrockAgentCoreApp, RequestContext
from strands import Agent

app = BedrockAgentCoreApp()

# Build the model and Code Interpreter once at module load
MODEL = BedrockModel(model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0")
CODE_INTERPRETER = StrandsCodeInterpreterTools(REGION).execute_python_securely


@app.entrypoint
async def invocations(payload: dict, context: RequestContext):
    input_data = RunAgentInput.model_validate(payload)
    actor_id = extract_user_id_from_context(context)
    # Fresh agent per request --- picks up the caller's identity and tools
    agent = Agent(
        model=MODEL,
        system_prompt=SYSTEM_PROMPT,
        tools=[create_gateway_mcp_client(actor_id), CODE_INTERPRETER],
        session_manager=get_memory_session_manager(actor_id, session_id),
    )
    agui_agent = StrandsAgent(
        agent=agent,
        name="agui_strands_agent",
        config=StrandsAgentConfig(
            session_manager_provider=make_memory_provider(actor_id),
            replay_history_into_strands=False,
        ),
    )
    async for event in agui_agent.run(input_data):
        yield event.model_dump(mode="json", by_alias=True, exclude_none=True)
```

`BedrockAgentCoreApp` 读取 AgentCore Runtime 的请求头（`WorkloadAccessToken`、`Authorization`、`Session-Id`）并填充上下文变量，因此 Gateway 认证与 Memory 的工作方式与 HTTP 模式一致。

`agui-langgraph-agent` 模式使用来自 `copilotkit` 库的 `LangGraphAGUIAgent`。它在每个请求上重新构建编译好的图，因此每次调用都会拿到限定给调用方的 MCP 工具。这里的 AgentCore Memory 同样是可选项：当 `MEMORY_ID` 未设置时，helper 返回 `None`，因此你可以在不配置 Memory 的情况下运行该模式：

```
# patterns/agui-langgraph-agent/agent.py
from copilotkit import CopilotKitMiddleware, LangGraphAGUIAgent


async def build_graph(actor_id: str):
    """Build a fresh LangGraph compiled graph with Gateway tools."""
    mcp_client = await create_gateway_mcp_client(actor_id)
    tools = await mcp_client.get_tools()
    tools.append(CODE_INTERPRETER)
    return create_agent(
        model=MODEL,
        tools=tools,
        checkpointer=get_memory_saver(),  # None when MEMORY_ID is unset
        middleware=[CopilotKitMiddleware()],
        system_prompt=SYSTEM_PROMPT,
    )


@app.entrypoint
async def invocations(payload: dict, context: RequestContext):
    input_data = RunAgentInput.model_validate(payload)
    actor_id = extract_user_id_from_context(context)
    graph = await build_graph(actor_id)
    agui_agent = LangGraphAGUIAgent(
        name="agui_langgraph_agent",
        graph=graph,
        config={"configurable": {"actor_id": actor_id}},
    )
    async for event in agui_agent.run(input_data):
        yield event.model_dump(mode="json", by_alias=True, exclude_none=True)
```

两个模式产生相同的 AG-UI 事件。该协议定义了基于 Server-Sent Events 的类型化事件流。例如，一次工具调用会产生下面这个序列：

```
data: {"type": "RUN_STARTED", "threadId": "t1", "runId": "r1"}
data: {"type": "TEXT_MESSAGE_START", "messageId": "m1", "role": "assistant"}
data: {"type": "TEXT_MESSAGE_CONTENT", "messageId": "m1", "delta": "Let me check "}
data: {"type": "TEXT_MESSAGE_CONTENT", "messageId": "m1", "delta": "that for you."}
data: {"type": "TEXT_MESSAGE_END", "messageId": "m1"}
data: {"type": "TOOL_CALL_START", "toolCallId": "tc1", "toolCallName": "get_weather"}
data: {"type": "TOOL_CALL_ARGS", "toolCallId": "tc1", "delta": "{\"location\": \"Seattle\"}"}
data: {"type": "TOOL_CALL_END", "toolCallId": "tc1"}
data: {"type": "TOOL_CALL_RESULT", "toolCallId": "tc1", "content": "{\"temp\": 55}"}
data: {"type": "RUN_FINISHED", "threadId": "t1", "runId": "r1"}
```

前端解析器把每个事件映射到一个前端动作：

```
// frontend/src/lib/agentcore-client/parsers/agui.ts
export const parseAguiChunk: ChunkParser = (line, callback) => {
  if (!line.startsWith("data: ")) return;
  const json = JSON.parse(line.substring(6).trim());
  switch (json.type) {
    case "TEXT_MESSAGE_CONTENT":
      callback({ type: "text", content: json.delta ?? "" });
      break;
    case "TOOL_CALL_START":
      callback({ type: "tool_use_start", toolUseId: json.toolCallId, name: json.toolCallName });
      break;
    case "TOOL_CALL_RESULT":
      callback({ type: "tool_result", toolUseId: json.toolCallId, result: json.content ?? "" });
      break;
    case "RUN_FINISHED":
      callback({ type: "result", stopReason: "end_turn" });
  }
};
```

与 HTTP 模式相比——在那些模式里，Strands、LangGraph 和 Claude-agent-sdk 各自都需要一个单独的解析器来处理不同的流式格式——有了 AG-UI，后端框架被抽象掉了。你可以在配置里把 `agui-strands-agent` 换成 `agui-langgraph-agent`，而前端不用改。

要部署，请在 `infra-cdk/config.yaml` 中设置模式并运行 CDK：

```
backend:
  pattern: agui-strands-agent  # or agui-langgraph-agent
  deployment_type: docker
```

```
cd infra-cdk
cdk deploy --require-approval never
python3 ../scripts/deploy-frontend.py
```

### CopilotKit + FAST：生成式 UI、共享状态与人机协同

基础 FAST 前端提供了一个可用的聊天界面，但 AG-UI 支持丰富得多的交互：agent 渲染自定义 UI 组件、与前端同步状态，以及执行中途暂停等待用户输入。CopilotKit 是一个专门为这些模式构建的 React 库。CopilotKit 团队在 FAST 之上构建了一个[示例应用](https://github.com/aws-samples/sample-FAST-applications/tree/main/samples/copilotkit-generative-ui)，在 AgentCore 上演示这些能力。它同时包含 LangGraph 和 Strands 的 agent 模式，你可以在部署时选择其一。

生成式 UI 跨越从「前端高度控制」到「agent 高度自由」的一个谱系。本示例处在受控的那一端：前端掌握预构建的 React 组件，agent 选择渲染哪一个并通过 AG-UI 事件提供数据。再往谱系的另一端，agent 返回声明式 UI 描述由前端渲染，或返回完整 UI 界面由前端嵌入。AG-UI 三种都能承载，因为它标准化的是事件与状态流，而不是 UI 本身。你交给 agent 的自由越多，承担的就越多：开放式界面需要沙箱与输入校验。

CopilotKit 示例的架构。CopilotKit Runtime Lambda 充当浏览器与 AgentCore Runtime 之间的服务端桥梁，负责 AG-UI 事件解析、生成式 UI 路由和认证转发。

#### 生成式 UI：agent 渲染 React 组件

使用 CopilotKit，agent 可以在聊天中内联渲染自定义 React 组件，而不仅是文本。前端注册组件，agent 便能通过 AG-UI 的工具调用事件来调用它们：

```
// Register a pie chart the agent can render
useComponent({
  name: "pieChart",
  description: "Displays data as a pie chart.",
  parameters: PieChartPropsSchema,
  render: PieChart,
});
```

当 agent 调用 `pieChart` 工具时，CopilotKit 拦截 `TOOL_CALL_START` 和 `TOOL_CALL_ARGS` 事件，并直接在对话中渲染 `PieChart` 组件。agent 先调用 `query_data` 工具，从一份示例的逗号分隔值（CSV）文件中取数据，再把结果传给图表组件。

#### 共享状态：与 agent 同步的 todo 画布

示例中包含一个 todo 画布，在 agent 与 UI 之间双向保持同步。当你告诉 agent“加三个任务：设计 API、写测试、部署到 staging”，agent 会调用 `manage_todos`，画布则通过 AG-UI 的 `STATE_SNAPSHOT` 事件实时更新。你也可以直接在 UI 中编辑 todo。agent 在下一轮就能看到更新后的状态，因为 Strands 模式会把当前 todos 注入 system prompt：

```
def state_context_builder(state: dict) -> str:
    todos = state.get("todos", [])
    if todos:
        return f"\nCurrent todos:\n{json.dumps(todos, indent=2)}"
    return ""
```

#### 人机协同：agent 暂停并等待

示例演示了一个会议排程器：agent 在执行中途暂停并渲染一个时间选择器。用户选定时间后，agent 带着该选择继续：

```
useHumanInTheLoop({
  name: "scheduleTime",
  description: "Schedule a meeting with the user.",
  parameters: z.object({
    reasonForScheduling: z.string(),
    meetingDuration: z.number(),
  }),
  render: ({ respond, status, args }) => (
    <MeetingTimePicker status={status} respond={respond} {...args} />
  ),
});
```

这通过 AG-UI 的工具调用流程实现：agent 为 `scheduleTime` 发出 `TOOL_CALL_START`，CopilotKit 渲染选择器而不是执行后端工具，用户的响应则以 `TOOL_CALL_RESULT` 回传。

#### 部署 CopilotKit 示例

克隆 FAST Samples 仓库并部署：

```
git clone https://github.com/aws-samples/sample-FAST-applications.git
cd sample-FAST-applications/samples/copilotkit-generative-ui
cp config.yaml.example config.yaml
# Edit config.yaml --- set stack_name_base and admin_user_email
./deploy-langgraph.sh  # or ./deploy-strands.sh
```

部署脚本会创建整套栈：Amazon Cognito 用户池、Amazon ECR 仓库、AgentCore Runtime、AgentCore Gateway、AgentCore Memory、带 Amazon API Gateway 的 CopilotKit Runtime Lambda，以及 AWS Amplify 托管。执行完成后，打开末尾打印的 Amplify URL 并登录。你会进入 CopilotKit 聊天界面，只需几项快速检查即可确认部署可用：

- 让 agent 用示例数据画一个饼图。它会在对话中内联渲染。
- 要求往 todo 画布里加三个任务。画布会实时更新。
- 要求安排一次会议。agent 会暂停并显示时间选择器。

### 清理

本次演练会部署两套独立的栈。请拆除你实际部署的那一套，让它们不再产生费用。

移除 FAST 部署：

```
cd infra-cdk
npx cdk destroy --all
```

移除 CopilotKit 示例：

```
cd sample-FAST-applications/samples/copilotkit-generative-ui
npx cdk destroy --all
```

如果某个 Amazon ECR 仓库里仍存有容器镜像，请手动删除它，因为某些 CDK 配置会把仓库保留在原位。

## 结语

本文展示了如何使用 AG-UI 协议在 Amazon Bedrock AgentCore 上构建交互式 agent 前端。FAST 中的 AG-UI 集成让你能在 Strands 与 LangGraph agent 后端之间切换，而无需改动前端代码。CopilotKit 示例用生成式 UI、共享状态和人机协同交互对其做了扩展，全部运行在带托管认证、扩缩容和记忆的 AgentCore 上。

要了解更多，请查阅以下资源：

- [FAST 仓库](https://github.com/awslabs/fullstack-solution-template-for-agentcore)：克隆并部署一个 AG-UI 模式，使用 `pattern: agui-strands-agent` 或 `pattern: agui-langgraph-agent`。
- [CopilotKit 生成式 UI 示例](https://github.com/aws-samples/sample-FAST-applications/tree/main/samples/copilotkit-generative-ui)：在 AgentCore 上试用生成式 UI、共享状态和人机协同。
- [AgentCore AG-UI 文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-agui.html)：完整协议契约与部署细节。
- [AG-UI 协议规范](https://docs.ag-ui.com/concepts/overview)：核心事件类型与协议设计。
- [CopilotKit 文档](https://docs.copilotkit.ai/)：生成式 UI 的前端集成指南。

如果有问题或反馈，请在 [FAST 仓库](https://github.com/awslabs/fullstack-solution-template-for-agentcore/issues) 或 [FAST Samples 仓库](https://github.com/aws-samples/sample-FAST-applications/issues) 中开一个 issue。

## 关于作者
