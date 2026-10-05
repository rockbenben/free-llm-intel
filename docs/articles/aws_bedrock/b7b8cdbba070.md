---
vendor: aws_bedrock
title: 用 Amazon Bedrock AgentCore 构建环境智能体：从事件驱动信号到人在回路工作流
original_title: Building ambient agents with Amazon Bedrock AgentCore: From event-driven signals to human-in-the-loop workflows
url: https://aws.amazon.com/blogs/machine-learning/building-ambient-agents-with-amazon-bedrock-agentcore-from-event-driven-signals-to-human-in-the-loop-workflows
date: 2026-10-01
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

大规模处理文档的团队都熟悉这套例行流程：文件落到存储里，有人注意到、逐个打开、决定它需要什么，并路由去审阅。监控告警以同样的方式排队，等着人来处理。浪费在人工分类上的时间，正是环境智能体（ambient agents）要解决的运营问题。想象一个文件落到你的 Amazon Simple Storage Service (Amazon S3) 桶里，几秒之内你的 Jobs 页面上就出现一个待运行（如果你那样配置了，可能已经在运行）的作业。智能体分析该文件、呈现发现，并在采取下一步之前征求你的批准。事件本身就是 prompt。这就是一个环境智能体：它响应事件流，在需要时通过单个 `ask_human` 工具暂停以等待人工输入，并在人回答后从它停下的地方恢复。

图 1：环境智能体在 AgentCore Runtime 上响应一个事件并暂停等待人工输入的概览

今天大多数 AI 智能体体验遵循另一种模式：用户打开一个聊天界面、输入一个 prompt、等待响应。这对一次性问题有效，但它把智能体限制为一次只能进行一个会话，并且需要人类先描述发生了什么，任何动作才能在其上展开。对于智能体应当响应你基础设施各处所发生事件（文件上传、数据库变更、计划任务、系统告警）的场景，那种仅聊天的模型就失效了。

[环境智能体](https://blog.langchain.com/introducing-ambient-agents/) 描述的是另一种范式，LangChain 及其他厂商都在阐发这一范式。环境智能体不等用户发起会话，而是监听一个事件流并对其采取行动，可能并行处理许多事件。它们不单纯由人类消息触发，且多个智能体可同时运行。关键在于，它们并非完全自主：一个生产设计会审慎对待智能体何时暂停以与人交互。当一个信号触发时，智能体执行其工作流，只在需要澄清、批准或审阅时才打断一个人。这一人在回路（human-in-the-loop）组件降低了部署智能体到生产的风险、建立用户信任，并让智能体能通过反馈随时间学习和改进。

在 AWS 上运行的组织已经具备了事件驱动的基础设施：Amazon S3 事件通知、Amazon EventBridge 规则、AWS Lambda 触发器和 Amazon DynamoDB streams。缺失的一环是把那些事件源连接到能够推理发生了什么、采取行动、并在情况需要时把人类拉进来的智能体。像 [AWS Step Functions](https://aws.amazon.com/step-functions/) 这样的全自动流水线能编排工作流，却无法就模糊性推理或提出澄清问题。基于聊天的智能体能够推理，但需要有人发起会话。环境智能体弥合了这一鸿沟。

[Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/) 是一个以任意框架或模型大规模构建、连接并优化智能体的平台。AgentCore Runtime 提供了让这一模式运作起来的执行环境：基于容器的智能体托管，支持长时间运行的工作负载，内建会话隔离，并与 Amazon Bedrock 基础模型集成。AgentCore Runtime 支持的会话足够长，足以覆盖这里展示的信号 → 智能体 → 人在回路（HITL）流程。参考实现把每个智能体回合限制在 Lambda 的 15 分钟超时之内，实践中这有充裕余量。配合用于事件处理的 AWS Lambda 和用于状态管理的 Amazon DynamoDB，结果就是一个完全无服务器的环境智能体平台。

在本文中，我们在 Amazon Bedrock AgentCore 上端到端演练这一模式。读完你会理解：

- 一个 Amazon S3 或计划事件如何变成一个智能体在 AgentCore Runtime 上运行的作业，可以有人在环，也可以没有。
- 单个 `ask_human` 工具加一个规范的响应封装（envelope）如何足以支撑完整范围的人在回路交互。
- 参考示例给你提供了什么，你又需要在其之上为自己的用例写什么。

## 前提条件

在部署参考实现前，请确保你具备以下内容：

- 一个 AWS 账户，具备创建 AWS Identity and Access Management (IAM) 角色、Lambda 函数、DynamoDB 表、S3 桶、Amazon Simple Queue Service (Amazon SQS) 队列、Amazon API Gateway API、Amazon CloudFront 分配、Amazon Cognito 用户池、Amazon Elastic Container Registry (Amazon ECR) 仓库和 Bedrock AgentCore 运行时的权限。在一个沙箱账户上拥有管理员访问权是很好的起点。
- 已用该账户的凭证配置好 [AWS Command Line Interface (AWS CLI)](https://docs.aws.amazon.com/cli/)，默认 AWS 区域为 `us-east-1`（示例的默认值都是为该区域接好的）。
- 已在你的账户和区域中安装并引导好 [AWS Cloud Development Kit (AWS CDK)](https://docs.aws.amazon.com/cdk/) v2（`cdk bootstrap`）。
- 本地已安装并运行 [Docker](https://www.docker.com/)。智能体容器在部署过程中被构建并推送到 Amazon ECR。
- 用于后端 Lambda 函数和智能体构建的 Python 3.11 或更新版本，以及用于 React 前端的 `Node.js` 18 或更新版本。
- 在你目标区域的 Amazon Bedrock 中访问 Anthropic Claude Sonnet 4.5 模型的权限。如果你此前没用过 Bedrock，请按 [Manage access to Amazon Bedrock foundation models](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)（基础模型 FM）启用该模型。模型可用性因 AWS 区域而异。查看 Amazon Bedrock 文档以获取你目标区域当前支持的模型列表。切换模型在之后是一行配置的改动。

## 理解环境智能体

在讲架构之前，先看看是什么让一个环境智能体不同于典型聊天机器人，以及本文其余部分所依赖的构建块：事件驱动的触发模型、环境信号抽象，以及把两者串起来的单个的人在回路工具。

### 事件驱动 vs 用户发起的智能体

用户发起的智能体遵循请求-响应模式：

```
User → Prompt → Agent → Response → User
```

环境智能体遵循事件驱动模式：

```
Event → Signal → Agent → [Optional human interaction] → Action
```

关键区别在触发机制。环境智能体由系统事件而非显式用户请求激活，这使它们天然适合文档处理流水线、监控与告警、计划分析，以及沿途需要审批关卡的多步工作流。

### 环境信号：触发机制

一个环境信号是把一个事件源映射到一个智能体的配置。当事件发生时，平台自动为该智能体创建一个作业。接下来发生什么取决于信号上的一个设置：

- 当 `autoExecute: false`（默认）时，作业以 `idle` 状态落到 Jobs 页面，等待人工审阅并运行它。当一个信号可能因未知输入触发，或智能体拥有高风险工具时，这是你想要的、安全的、审阅优先的流程。
- 当 `autoExecute: true` 时，信号处理器把作业直接排入 worker 队列，智能体立即运行，只有当智能体自己调用 `ask_human` 时才把人类拉进来。这是完全自主的流程。

这一模式覆盖若干信号事件源。参考示例提供了前两个。其余的是扩展点，你通过写一个新的 handler Lambda 函数和一个对应的 Signals 页表单字段来添加：

- **Amazon S3 文件上传**（已提供）：当文件上传到特定桶和前缀时触发。
- **计划事件**（已提供）：按类 cron 计划触发智能体。由携带 `jobType: "scheduled"` 的作业驱动，而非由 Signals 页上的一个信号驱动。
- **API webhook**（扩展点）：响应外部系统的通知。
- **数据库变更**（扩展点）：对 Amazon DynamoDB streams 或 Amazon Relational Database Service (Amazon RDS) 事件做出反应。

### 人在回路：一个工具、一个封装、一个视图

环境智能体需要结构化的方式与人交互。在本示例中，智能体通过单个工具（`ask_human`）呈现这些交互，并返回一个规范的响应封装。在该封装中，`status` 是 `completed`、`interrupted` 或 `error` 之一，而对应的字段是 `result`、`question` 或 `error`。平台还会在每个响应上贯穿 `session_id` 和 `job_id`，以便关联续接回合。这些是关联元数据，不是你智能体必须实现的核心契约的一部分。当智能体返回 `interrupted` 时，平台把作业移到 `interrupted` 状态并把它的 `requiresAction` 标志置为 `true`。参考 React 前端在 Jobs 页面的 **Interrupted** 标签页上呈现这些，并在每行上显示一个警告指示器，因此没有单独的审阅队列要轮询。同一个 Jobs 视图展示待处理的问题、等待批准的建议动作、最终结果和失败的作业，给用户一个地方看到他们的智能体正在做的一切，而不必监控多个聊天窗口或邮件线程。

同一机制支撑多种提示模式，读者可能从更广泛的智能体文献中认出它们：一个 Notify 回合（智能体只报告结果）、一个 Question 回合（它请求澄清）、一个 Review 回合（它提议一个动作并等待 `APPROVE` / `REJECT` / `MODIFY`），以及一个 Error 回合（失败被记录到作业记录上，由用户决定是否重试）。这些是智能体如何撰写其问题的约定，而非独立的运行时模式。在平台层面，正好只有一条代码路径和正好只有一个封装。

图 2：Notify、Question 和 Review 人在回路模式，全部通过 ask_human 工具呈现

## 架构概览

该平台是一小组由事件流水线拼接起来的无服务器组件。本节先讲端到端流程，然后依次描述每个组件。

事件在平台中端到端流转如下。Amazon S3 发出一个 `s3:ObjectCreated` 通知，一个 Signal Processor Lambda 函数接收它。Signal Processor 查询 ambient-signals 表上的一个全局二级索引（GSI），为该事件桶查找任何匹配的信号，然后为每个匹配创建一个作业记录。API 层（或调度器）把作业排入一个 Amazon SQS 队列。为 API 路径服务的同一个 Job Execution Lambda 函数还通过一个附加的 SQS 事件源抽取队列，在 Amazon Bedrock AgentCore Runtime 上调用智能体，并把结果（以及任何人工输入请求）写回 Amazon DynamoDB。一个从 Amazon S3 经 Amazon CloudFront 服务的 React 前端轮询一个小的 Amazon API Gateway 和 Lambda 层以获取更新，并让用户响应待处理的交互。

主要组件有：

- **Amazon S3**（带事件通知）在文件上传时充当信号的入口点。前缀和后缀过滤被下推到桶的通知配置中，因此 signal processor 只对那些可能匹配某个信号的事件被调用。
- **Amazon SQS** 把 API Gateway 请求与智能体调用解耦。一个作业执行队列保存待处理的工作。一个死信队列（DLQ）捕获 worker 在配置的重试次数后仍无法处理的消息。
- **三个流水线 Lambda 函数**把事件从接收带到智能体（API Gateway 后有一个单独的管理层，本节后面会描述）：  *Signal Processor* 把传入事件匹配到配置的信号定义并创建作业。*Job Execution* 在一个 Lambda 函数中有两个入口路径：一个排入消息的 API handler，和一个消费消息、带着作业上下文调用 AgentCore Runtime 的 SQS worker。*Scheduler* 在一分钟 cron 上触发，并把到期的计划作业排入同一个 SQS 队列。
- **Amazon Bedrock AgentCore Runtime** 在隔离容器中运行智能体代码并支持长时间运行的工作负载。
- **Amazon DynamoDB** 存储智能体注册表、作业记录、环境信号定义、聊天线程、会话历史和 Powertools 幂等记录。会话消息通过 `UpdateItem` + `list_append` 原子追加，因此并发写入者不会互相覆盖。
- **Amazon API Gateway 后的五个管理层 Lambda 函数**暴露前端消费的 REST API（`agent_management`、`job_management`、`signal_management`、`chat_management`、`conversation_management`），外加一个 `chat_management` 异步调用的 `chat_execution` worker Lambda，使聊天 API 调用能立即返回。关于它们如何被配置，见[生产部署](https://aws.amazon.com/cn/blogs/machine-learning/building-ambient-agents-with-amazon-bedrock-agentcore-from-event-driven-signals-to-human-in-the-loop-workflows/#production-deployment)。
- **一个 React 前端**从 Amazon S3 经 Amazon CloudFront 服务，提供 Agent Management UI，用户在其中监控作业、与智能体聊天、响应问题并审阅待处理的动作。

图 3：从 Amazon S3 经 Amazon SQS 和 AWS Lambda 到 AgentCore Runtime 的事件流，状态在 Amazon DynamoDB，并有 React 前端

## 构建事件基础设施

有了架构在脑海，下一步是接好那个把一个 Amazon S3 上传变成智能体作业的事件源。本节创建桶、把它的事件通知指向 Signal Processor Lambda 函数，并演练处理器如何把事件与配置的信号做匹配。

### 设置 Amazon S3 信号触发器

创建 Amazon S3 桶并配置驱动 Signal Processor 的事件通知：

```
aws s3 mb s3://amzn-s3-demo-bucket-$(date +%s)
```

桶被配置为把 `s3:ObjectCreated:*` 事件直接发送到 Signal Processor Lambda 函数。在本示例中，通知配置是由 `signal_management` Lambda 函数在创建或更新信号时动态安装的，因此为一个新前缀添加新信号不需要重新部署。

### Signal Processor Lambda 函数

Signal Processor 接收 Amazon S3 事件，在 DynamoDB 中查找匹配的签名定义，并为每个匹配创建一个作业。其核心 handler 是下面示例展示的样子。`backend/functions/multi_agent/signal_processor.py` 中的真实 handler 还使用 AWS Lambda Powertools 做结构化日志和幂等，查询信号表上的 `bucketName-signalId-index` GSI，应用每个信号上配置的前缀和后缀检查，并写入一个 `signal_triggered` 作业行。

```
def process_s3_signal(event):
    """Process S3 file-upload events and create agent jobs."""
    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        for signal in find_matching_signals(bucket, key):
            create_agent_job(signal, {"bucket": bucket, "key": key})
```

### 信号配置数据模型

信号以如下结构存储在 DynamoDB 中：

```
{
  "signalId": "sig-123abc",
  "userId": "user-456def",
  "agentId": "agent-789ghi",
  "signalName": "Document Processor",
  "signalType": "s3_file_upload",
  "enabled": true,
  "autoExecute": false,
  "bucketName": "ambient-agent-documents",
  "configuration": {
    "bucketName": "ambient-agent-documents",
    "prefix": "invoices/",
    "suffix": ".pdf"
  },
  "triggerCount": 42,
  "lastTriggered": "2026-04-15T10:30:00Z",
  "createdAt": "2026-04-01T00:00:00Z"
}
```

你只在通过 API 创建信号时设置 `configuration.bucketName`。上面示例展示的顶层 `bucketName` 由平台填充。DynamoDB GSI 分区键不能嵌套在一个 map 属性里，所以 `signal_management` 在每次写入时把 `configuration.bucketName` 镜像到顶层 `bucketName`，以便 `bucketName-signalId-index` GSI 能在每个 Amazon S3 事件上扇出到匹配的信号。

`autoExecute` 标志是那个决定智能体自主触发还是人类先审阅作业的单一切换。Agent Management UI 里的 Signals 表单把它作为一个复选框暴露，与常见的 `enabled` 设置并列，因此改变行为是一次快速编辑，无需动代码或数据库。

图 4：Signals 页面，在一个信号定义上带有 autoExecute 开关

## 在 AgentCore Runtime 上部署智能体

Amazon Bedrock AgentCore Runtime 托管智能体容器，并通过一个 `InvokeAgentRuntime` API 暴露它，worker Lambda 函数在每个作业上调用它。本节演练示例自带提供的智能体布局、驱动它的配置，以及那个把 LangGraph 工具调用转成平台响应封装的小型编排器。

### 智能体打包与结构

AgentCore Runtime 为智能体提供基于容器的执行环境，因此你可以带入任意 Python 智能体框架。示例使用模块化设计：

```
agent/
├── agent.py             # Entry point
├── config.yaml          # Agent configuration
├── requirements.txt     # Dependencies
├── core/                # Platform integration
│   ├── agent_core.py        # Main agent logic
│   ├── tool_factory.py      # Config-driven tool creation
│   └── execution_control.py # Session state + loop detection
└── tools/               # Custom tools
    ├── calculator.py        # Math operations
    ├── human_input.py       # Human-in-the-loop
    └── s3_reader.py         # Exports list_s3_files + read_s3_file
```

### 智能体配置

`config.yaml` 定义智能体行为、工具和 system prompt。示例在本演练中默认使用 Amazon Bedrock 上的 Anthropic Claude Sonnet 4.5，它很适合人在回路工作流所依赖的多步工具调用和长上下文推理。切换到 Claude Haiku、Amazon Nova，或 Amazon Bedrock 上可用的另一个支持工具调用的模型（可用性因区域而异），只需在下面配置里对 `model_id` 作一行改动。`max_iterations: 10` 给图足够余量，在停止前大约可进行十次模型到工具的往返（编排器把该值翻倍来计算 LangGraph 的递归上限，因为每次往返穿过两个图节点），这覆盖了示例的 S3、计算器和 `ask_human` 工具所期望的多步工具使用。该文件还含一个 `execution:` 块（loop-detector、circuit-breaker、session-cache 阈值），为简洁起见在此省略。完整文件见 `agent/config.example.yaml`。

```
# Amazon Bedrock Configuration
aws:
  bedrock:
    model_id: "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    region_name: "us-east-1"

# Agent behavior
agent:
  verbose: true
  max_iterations: 10
  handle_parsing_errors: true

# Tool configuration (enables config-driven tool composition)
tools:
  calculator:
    enabled: true
    type: "calculator"
    name: "calculator"
    description: "Perform mathematical calculations."

  human_input:
    enabled: true
    type: "human_input"
    name: "ask_human"
    description: "Request input or clarification from a human user."

  s3_list:
    enabled: true
    type: "s3_list"
    name: "list_s3_files"
    description: "List files in an Amazon S3 bucket."

  s3_reader:
    enabled: true
    type: "s3_reader"
    name: "read_s3_file"
    description: "Read and analyze files from Amazon S3."

prompts:
  system_template: |
    You are a helpful AI assistant with access to a set of tools.
    Call tools only when they add value. Prefer concise answers
    grounded in tool results.
```

### 核心智能体实现

智能体基于 `langchain.agents.create_agent` 构建，那是一个编译成 LangGraph 的工具调用智能体。之所以由 LangChain 承担编排层，是因为它带来预构建的工具调用模式、一个广泛的开放集成生态，以及许多团队已经熟悉的 API，而 AgentCore Runtime 在其下提供托管托管、会话隔离和伸缩。两层相辅相成。围绕图的平台包装器做三件事：它为本回合构建消息列表（包括任何会话历史，以及对于信号触发的作业，触发信号的 Amazon S3 桶和键，以便模型无需被告知就能取到文件）、调用图，并扫描工具输出以寻找 `ask_human` 哨兵值，从而把一个工具调用转成一个 `interrupted` 响应。

在其最简形式中（`agent/core/agent_core.py` 中的完整版还处理每会话历史缓存、循环检测和执行 trace），编排器就是下面这样：

```
from bedrock_agentcore import BedrockAgentCoreApp
from langchain.agents import create_agent
from langchain_aws import ChatBedrock
from langchain_core.messages import ToolMessage

from core.tool_factory import create_tools_from_config, load_config
from tools.human_input import HUMAN_INPUT_SENTINEL


class Agent:
    def __init__(self):
        self.config = load_config()
        self.llm = ChatBedrock(
            model_id=self.config["aws"]["bedrock"]["model_id"],
            region_name=self.config["aws"]["bedrock"]["region_name"],
        )
        # Tools are built from config.yaml so enabling a tool is a
        # config change rather than a code change.
        self.tools, _ = create_tools_from_config()
        self.agent_graph = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.config["prompts"]["system_template"],
        )

    def invoke(self, payload):
        """Run the agent graph for one turn. Simplified: the real method
        also loads conversation history, binds execution state on a
        ContextVar for tools to read, records an execution trace, and
        threads ``session_id`` and ``job_id`` through on every response
        so the platform can correlate continuation turns.
        """
        session_id = payload.get("session_id", "default")
        job_id = payload.get("job_id")
        result = self.agent_graph.invoke(
            {"messages": self._build_messages(payload)},
        )

        for msg in result["messages"]:
            if isinstance(msg, ToolMessage):
                content = str(msg.content)
                if content.startswith(HUMAN_INPUT_SENTINEL):
                    question = content[len(HUMAN_INPUT_SENTINEL):].strip()
                    return {
                        "status": "interrupted",
                        "question": question,
                        "session_id": session_id,
                        "job_id": job_id,
                    }

        return {
            "status": "completed",
            "result": self._extract_final_output(result["messages"]),
            "session_id": session_id,
            "job_id": job_id,
        }


app = BedrockAgentCoreApp()
agent = Agent()


@app.entrypoint
def invoke(payload):
    """AgentCore Runtime entrypoint. Delegates to the Agent wrapper."""
    return agent.invoke(payload)
```

### 部署智能体

使用提供的脚本把智能体部署到 AgentCore Runtime：

```
cd agent

# Configure AWS settings in .env and any overrides in config.yaml.
# Then build the container, push to Amazon ECR, and register it with
# Bedrock AgentCore Runtime.
./deploy_agent.sh
```

脚本返回一个 Agent Runtime 的 Amazon Resource Name (ARN)，后端把它存进智能体注册表，以便 Job Execution Lambda 函数能调用它。

## 用 DynamoDB 做状态管理

Amazon DynamoDB 是凡需要活得比单次 Lambda 调用更久之事实的记录系统：注册了哪些智能体、哪些作业在途、给智能体跨回合连续性的会话历史，以及 UI 读取的信号定义和聊天线程。下面的小节描述表布局、会话模型，以及 Job Execution Lambda 函数如何用这两者驱动一个作业到完成。

### 数据库设计

状态层由 DynamoDB 支撑。本文使用的核心表有：

**智能体注册表**（每个已注册智能体运行时一条记录）：

```
{
  "agentId": "agent-123abc",
  "agentName": "Document Analyzer",
  "agentArn": "arn:aws:bedrock-agentcore:us-east-1:123456789012:agent-runtime/abc123",
  "status": "active"
}
```

**作业注册表**（每次智能体调用一条记录）。在默认的 `autoExecute: false` 下，一个新建的信号触发作业以 `idle` 状态落在这里，等待用户选择 Execute：

```
{
  "jobId": "job-789ghi",
  "agentId": "agent-123abc",
  "sessionId": "session-xyz789",
  "jobName": "Signal: Document Processor - invoice.pdf",
  "jobType": "signal_triggered",
  "status": "idle",
  "requiresAction": false,
  "metadata": {
    "signalId": "sig-123abc",
    "triggerPayload": {
      "bucket": "documents",
      "key": "invoices/invoice.pdf",
      "eventSource": "s3"
    }
  }
}
```

作业运行期间 worker 把 `status` 翻到 `busy`。如果智能体通过调用 `ask_human` 暂停，`status` 变为 `interrupted`，`requiresAction` 变为 `true`，这会把作业呈现在 Jobs 页面的 Interrupted 标签上。

**会话存储表**（每会话的完整消息历史，带 30 天存活时间（TTL））：

```
{
  "sessionId": "session-xyz789",
  "agentId": "agent-123abc",
  "messages": [
    { "type": "human", "content": "Analyze this invoice", "timestamp": "2026-04-15T10:30:00Z" },
    { "type": "ai", "content": "Which category should I focus on?", "timestamp": "2026-04-15T10:30:30Z" }
  ],
  "ttl": 1778803200
}
```

还有额外的表用于环境信号、聊天线程和 Powertools 幂等记录。计划执行通过一个 `jobType` 和 `nextRun` GSI 复用作业注册表，而非有自己的表。

### 会话管理

会话在作业执行和聊天回合之间提供对话连续性。`conversation_management` Lambda 函数掌管 DynamoDB 持久化：每个回合（human + AI 一对）都用一个原子的 `UpdateItem` + `list_append` 追加到会话，因此同一会话上的两个并发写入者不会互相覆盖，而 30 天的 TTL 负责清理。

### 带对话连续性的作业执行

Job Execution Lambda 函数有两个入口路径。API 路径发送一个 SQS 消息（加上 Powertools 幂等和一个 `userId` 所有权检查）并立即返回 202 Accepted，因此前端从不等待模型。SQS worker 路径是真正干活的地方：它加载会话历史、把任何人工响应折进一个续接 prompt、调用 AgentCore Runtime，并把结果写回。那个 worker 大致如下：

```
# Worker path - consumes the SQS queue and invokes AgentCore Runtime
def execute_task(job, human_response=None):
    session_id = job["sessionId"]
    agent_id = job["agentId"]
    if human_response:
        prompt = (
            "Previous conversation:\n"
            f"{load_conversation_context(session_id, agent_id)}\n\n"
            f"Human: {human_response}"
        )
    else:
        prompt = job["prompt"]

    response = bedrock_agentcore.invoke_agent_runtime(
        agentRuntimeArn=job["agentArn"],
        runtimeSessionId=session_id,
        # The SDK expects the payload as a JSON-encoded string.
        payload=json.dumps(
            {"prompt": prompt, "metadata": job.get("metadata", {})},
        ),
    )
    result = json.loads(response["response"].read())
    save_conversation_turn(
        session_id, agent_id, prompt, result.get("result", ""),
    )

    return {
        "status": result.get("status", "completed"),
        "sessionId": session_id,
        "result": result.get("result"),
        "question": result.get("question"),
    }
```

图 5：作业执行序列，从 API 入队，经 SQS worker 和 AgentCore 调用，到 DynamoDB 写回

## 实现在人回路模式

前面那段智能体代码在图产生一个 `ask_human` 工具调用时返回了一个基于哨兵值的 `interrupted` 封装。本节聚焦 `ask_human` 工具本身，并精确展示编排器如何在不断裂推理循环的前提下捕获那个哨兵值。

### 人工输入工具

人在回路功能的核心是 `ask_human` 工具。它不抛出异常：因为 LangGraph 的工具节点会把工具异常捕获为错误观察值并喂回给模型，所以该工具改为返回一个哨兵字符串。编排器在图完成后于 `ToolMessage` 流上检测到哨兵值，并把它转换成一个 `interrupted` 响应。每次调用的状态（指标、会话 ID 等）不是工具参数。编排器把它绑定在一个 `ContextVar` 上，工具通过 `current_execution_state.get()` 读取它，这使同一容器内的并发调用彼此隔离。

```
from core.execution_control import current_execution_state

HUMAN_INPUT_SENTINEL = "__HUMAN_INPUT_REQUIRED__::"


def create_human_input_tool_func():
    """Create the ask_human tool function."""

    def ask_human_wrapper(question: str) -> str:
        """Request input or clarification from a human user.

        Returns a sentinel string that the orchestrator converts into
        an interrupt. The model never sees the sentinel because the
        orchestrator stops the graph when it is observed.
        """
        state = current_execution_state.get()
        if state is not None:
            state.execution_metrics.record_human_interaction()
        return f"{HUMAN_INPUT_SENTINEL}{question}"

    return ask_human_wrapper
```

### 智能体侧的使用

智能体在其工具调用循环中自然地使用该工具。例如，在分析一份有多个明细项的发票时，智能体可能调用：

```
Tool call: ask_human
Arguments: {
  "question": "This invoice spans three expense categories. Should I analyze Hardware, Services, or Software Licenses in detail?"
}
```

工具返回哨兵值，编排器停止图、把该问题作为会话存储中最新的 AI 回合持久化，并向 UI 呈现一个 `interrupted` 作业。当用户回复时，Job Execution Lambda 函数把答案折进一个续接 prompt 再次调用智能体。

## 构建 Agent Management UI

Agent Management UI 是该平台的人类一侧：用户在其中浏览作业、回答待处理问题，并直接与智能体聊天。它是一个 React 单页应用，与本文其余部分一直在描述的那个 REST API 通信。下面两个小节涵盖把信号、作业和人工输入串起来的布局和用户体验流程。

### 前端架构

前端是一个 React 与 Cloudscape Design 的单页应用，从 Amazon S3 在 Amazon CloudFront 后服务。它暴露一个五标签导航：

- **Workflows**：一个用于分组智能体和信号的 workflow 级定义的图库和 CRUD 界面。
- **Chat**：一个独立的聊天页（`/chat`、`/chat/:threadId`），用于用户发起的、与某个已注册智能体的对话。
- **Agents**：管理已注册的智能体运行时（名称、ARN、能力、状态）。
- **Jobs**：列出所有作业，带状态过滤和一个包含交互式 Chat 标签、执行 trace 和元数据的详情页。
- **Signals**：定义并切换环境信号。所提供的表单覆盖 Amazon S3 前缀和后缀过滤以及计划。Webhook、Amazon EventBridge 和 DynamoDB stream 字段会在你接好那些扩展点时添加。

同一个聊天组件被独立的 Chat 页面和 Jobs 详情的 Chat 标签复用。当一个作业在运行（`status === "busy"`）时，面板在一个短间隔上轮询 `/conversations/:sessionId`，使来自智能体或来自第二个浏览器标签页的回合在几秒内出现。作业结束后，轮询停止。因为在两处是同一个组件，用户可以在作业活跃时从 Jobs 详情视图自由地与智能体对话，而不限于回答单个待处理问题。

### 用户体验流程

- **信号触发**：Jobs 列表中出现一个新作业，带 `jobType: "signal_triggered"`。如果该信号有 `autoExecute: false`（默认），作业以 `idle` 落定，用户手动运行它。若 `autoExecute: true`，等到列表刷新时 worker 已经在起草响应了。用户发起的作业携带 `jobType: "user_initiated"` 并以不同徽章渲染，因此你一眼就能区分两者。
- **请求人工输入**：任何调用 `ask_human` 的作业移到 Interrupted 标签，其 `requiresAction` 标志翻到 `true`，这在行上渲染一个警告指示器。
- **响应**：详情视图浮现一个 Provide Response 按钮，用户可以在不离开作业上下文的情况下回答待处理问题。
- **执行反馈**：状态转换（`idle` → `busy` → `completed` | `interrupted` | `error`）被轮询并反映到列表和 Chat 标签页头中。
- **交互式聊天**：Jobs 详情的 Chat 标签和 `/chat` 页面都渲染完整会话历史并接受新的用户消息，因此人类可以回答待处理问题或用额外上下文轻推智能体，而不必离开 UI。
- **响应提交**：发送一条消息会调用 Chat Execution 或 Job Execution Lambda 函数，它带着作业上下文和折进下一回合的人工响应在 AgentCore Runtime 上调用智能体。
- **完成与审计**：最终结果存储在作业记录上，完整会话历史保留在会话上，可在 Chat 标签中用于审计和复用。

认证由 Amazon Cognito 和一个 API Gateway 的 `CognitoUserPoolsAuthorizer` 处理（见 `backend/infrastructure/multi_agent_stack.py`）。

实时更新实现为对会话和作业端点的轻量轮询，因此没有 WebSocket 基础设施要运行。

## 扩展示例

参考实现刻意做得很小，以便你在开始往里加东西之前先看清契约。本节描述盒内自带什么、你在其上构建什么，以及在哪里插入新事件源或工具。

### 示例自带 vs 你构建的部分

在扩展之前，知道接缝在哪里很有帮助。本示例是环境智能体模式的一个参考实现，而非一个交钥匙产品。开箱自带的：

- **平台**：信号接收、SQS 支撑的作业流水线、HITL 中断机制、DynamoDB 中的作业与会话状态、带 Jobs 页面和 Chat 界面的 React UI，以及带 Cognito 认证的 AgentCore 集成。
- **一个参考智能体**：一个容器化的 LangChain 智能体，带四个工具（计算器、`ask_human`、`list_s3_files`、`read_s3_file`）和一个通用 system prompt。对端到端验证流水线有用，但不能一上来就解决你的业务问题。
- **一个经 Signals UI 接好的信号源**（Amazon S3 文件上传，按桶、前缀和后缀匹配），外加一个作业级调度器，对用 `jobType: "scheduled"` 创建的作业按一分钟 cron 运行。添加新信号类型（如 webhook、Amazon EventBridge 事件或 DynamoDB streams）需要在后端和 Signals 页表单中都扩展 `signalType` 枚举。

你在其上构建的，以及平台对每一部分所要求的：

- **你的智能体**：一个容器化的 Python 智能体，为你的领域定制，带自己的工具和自己的 system prompt。它必须遵守平台所依赖的两条约定：返回三状态封装（`completed`、`interrupted` 或 `error`，配上对应的 `result`、`question` 或 `error` 字段），并使用 `ask_human` 哨兵值请求人工输入。围绕你偏好的任意智能体框架，这大约是 50 行适配代码。
- **新的信号类型**（如果 Amazon S3 上传和 cron 不够）：一个新的 handler Lambda 函数，查询信号表并写一个 `signal_triggered` 作业行（在下面模板中展示），加上 Signals 页上一个对应的表单字段以便用户配置它。
- **给你的智能体的新工具**：`agent/tools/` 下一个新模块、`agent/core/tool_factory.py` 里一个注册条目，以及 `config.yaml` 中一个启用标志。编排器和 HITL 流程不变。任何返回字符串的工具都参与同一个图。

简言之：平台做管道，你带大脑。你要写代码的三个地方（智能体逻辑、工具实现和新信号 handler）都能插入现有契约而不触碰栈的其余部分。

### 配置优于代码

为现有智能体启用一个新能力是配置改动而非代码改动。智能体的 `config.yaml` 切换工具的开或关并提供其描述，因此添加一个新的 Amazon S3 前缀 handler 或一个新的计算器模式不需要重新构建容器。信号定义活在 DynamoDB 中，并从 UI 的 Signals 页编辑。

### 添加一个新信号类型

信号如今在 Amazon S3 事件和 cron 计划上触发。添加一个新类型（webhook、Amazon EventBridge 规则、DynamoDB stream、Kafka topic）遵循同样的三步契约。下游流水线与信号无关：从 SQS worker 到 AgentCore 调用到 UI 的一切，都同样对待所有 `signal_triggered` 作业，所以你只需写从你的事件源到一个作业行的桥接。

```
# backend/functions/multi_agent/webhook_signal_processor.py (new file)
import json, os, uuid, boto3
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
sqs = boto3.client("sqs")
signals = dynamodb.Table(os.environ["AMBIENT_SIGNALS_TABLE"])
# The jobs table env var is named TASK_REGISTRY_TABLE for historical
# reasons; the table itself holds the same job rows the rest of the
# blog refers to.
jobs = dynamodb.Table(os.environ["TASK_REGISTRY_TABLE"])
QUEUE = os.environ["JOB_EXECUTION_QUEUE_URL"]


def handler(event, _context):
    """Webhook -> ambient job. Invoked behind API Gateway."""
    payload = json.loads(event.get("body") or "{}")
    source = payload.get("source", "unknown")

    # 1. Find enabled webhook signals matching this event source.
    resp = signals.query(
        IndexName="signalType-source-index",  # add this GSI in CDK
        KeyConditionExpression=Key("signalType").eq("webhook") & Key("source").eq(source),
        FilterExpression="enabled = :e",
        ExpressionAttributeValues={":e": True},
    )

    for signal in resp.get("Items", []):
        job_id, session_id = str(uuid.uuid4()), str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        auto = bool(signal.get("autoExecute", False))

        # 2. Write a job row using the same shape the S3 path uses.
        jobs.put_item(Item={
            "jobId": job_id,
            "userId": signal["userId"],
            "agentId": signal["agentId"],
            "jobName": f"Signal: {signal['signalName']} - {source}",
            "jobType": "signal_triggered",
            "status": "busy" if auto else "idle",
            "sessionId": session_id,
            "prompt": f"Webhook from {source}:\n{json.dumps(payload)}",
            "requiresAction": False,
            "createdAt": now, "updatedAt": now,
            "metadata": {"signalId": signal["signalId"],
                         "signalType": "webhook",
                         "triggerPayload": payload,
                         "autoExecute": auto},
        })

        # 3. Enqueue if the signal is configured to auto-execute.
        if auto:
            sqs.send_message(QueueUrl=QUEUE,
                             MessageBody=json.dumps({"jobId": job_id,
                                                     "signalTriggered": True,
                                                     "signalId": signal["signalId"]}))

    return {"statusCode": 202, "body": "accepted"}
```

你在 CDK 栈中添加该 Lambda 函数及其 API Gateway 路由，在前端的 TypeScript union 和 Signals 页表单中扩展 `signalType`，其余部分（Jobs 页面 UI、`ask_human` 中断处理、会话持久化、`autoExecute` 开关、契约测试）都原样适用。像生产的 Signal Processor 一样，一个真实 webhook handler 会加上 AWS Lambda Powertools 幂等，以便一次重试投递不会创建重复作业。

## 生产部署

当各部分在本地拼合后，下一步是在一个账户中配置它们。该平台作为单个 AWS CDK 栈部署。下面小节描述该栈创建什么、部署命令、运行时重要的指标，以及示例自带的安全和伸缩默认。

### 基础设施即代码

整个平台是一个定义在 `backend/infrastructure/multi_agent_stack.py` 的 AWS CDK 栈。对于存储和消息，它配置 DynamoDB 表（智能体注册表、作业注册表、会话存储、环境信号、聊天线程、幂等记录），采用按请求付费计费和时点恢复，外加 SQS 作业执行队列及其死信队列。

对于计算和交付，它配置架构一节中的三个流水线 Lambda 函数（Signal Processor、Job Execution、Scheduler）、支撑 REST API 的五个管理层 Lambda 函数（`agent_management`、`job_management`、`signal_management`、`chat_management`、`conversation_management`）以及 `chat_management` 异步调用的 `chat_execution` worker Lambda、一个 Cognito 支撑的 REST API，以及服务 React 前端的 CloudFront 分配。

IAM 授权直接由代码流给出：每张表上的 DynamoDB `grant_read_write_data`、按需的 SQS `grant_send_messages` 和 `grant_consume_messages`，以及 worker 角色上一个限定的 `bedrock-agentcore:InvokeAgentRuntime` 策略。

### 部署步骤

```
# Clone the sample
git clone https://github.com/aws-samples/sample-ambient-agent.git
cd sample-ambient-agent

# Deploy the backend (CDK) and build / deploy the frontend
cd backend
pip install -r requirements.txt
cdk bootstrap   # first time only
cdk deploy --all

cd ../frontend
npm install
npm run build

# Deploy the agent container to Bedrock AgentCore Runtime
cd ../agent
./deploy_agent.sh
```

### 监控与可观测性

Lambda 函数在 `AmbientAgents` 命名空间下发出自定义 CloudWatch 指标，覆盖这一模式中重要的事件：信号匹配、作业入队、作业完成、作业中断和作业出错。结合默认的 Lambda 和 SQS 指标（调用计数、错误、队列深度、DLQ 深度），这给你一个能看到信号 → 作业 → 智能体 → 人这一周期端到端的大仪表盘。对 DLQ 深度设一个告警，作为防范静默失败的第一道防线。

### 安全最佳实践

- **IAM 最小权限**：只授予每个 Lambda 函数所需的权限（读自己的表、限定的 `bedrock-agentcore:InvokeAgentRuntime`、限定的 Amazon S3 前缀）。
- **静态加密**：所有 DynamoDB 表使用 AWS 托管密钥。Amazon S3 桶使用 S3 托管加密。CloudFront 日志位于一个专用日志桶。
- **传输加密**：所有 API Gateway 端点和 CloudFront 分配要求 HTTPS。Amazon S3 桶策略强制 SSL。
- **审计日志**：AWS CloudTrail 捕获整个栈中的 API 调用。可以在作业表上启用 DynamoDB streams 以获得更丰富的作业生命周期审计。
- **负责任的 AI**：对智能体的输入和输出应用 Amazon Bedrock Guardrails，使内容过滤器、禁用主题和上下文接地检查在发现呈现在 Jobs 页面或通过 `ask_human` prompt 到达审阅者之前运行。这保护了人在回路交互，并让智能体输出接地位于源文档。

### 伸缩策略

- **Lambda 并发**：为 Job Execution worker Lambda 函数预留并发，把下游 Bedrock 调用封顶在一个可预测的每账户上限。
- **DynamoDB 容量**：默认是按请求付费。当流量模式稳定后切换到带自动伸缩的预留容量。
- **成本优化**：用 DynamoDB TTL 自动退役旧会话，用 Amazon S3 生命周期策略让已处理的文档老化过期，用 CloudWatch 指标过滤器跟踪每智能体的模型调用成本。

## 清理

在你评估完示例后为避免持续产生费用，按创建的反向顺序拆掉栈。

首先，从 Amazon Bedrock AgentCore 删除智能体运行时，使容器停止被计费：

```
aws bedrock-agentcore delete-agent-runtime \
    --agent-runtime-arn <your-agent-runtime-arn>
```

接着，清空该栈配置的 Amazon S3 桶（文档桶、前端托管桶和 CloudFront 日志桶），以便 CloudFormation 能删除它们：

```
aws s3 rm s3://<amzn-s3-demo-documents-bucket> --recursive
aws s3 rm s3://<amzn-s3-demo-frontend-bucket>  --recursive
aws s3 rm s3://<amzn-s3-demo-logs-bucket>      --recursive
```

然后销毁 AWS CDK 栈本身，这会移除 Lambda 函数、API Gateway、CloudFront 分配、DynamoDB 表、SQS 队列、Cognito 用户池和 IAM 角色：

```
cd backend
cdk destroy --all
```

最后，如果你不打算重新部署，删除由智能体部署脚本创建的 Amazon ECR 仓库：

```
aws ecr delete-repository \
    --repository-name ambient-agent \
    --force
```

如果你仅为本演练启用了 Amazon Bedrock 模型访问且不再需要它，可以从 Amazon Bedrock 控制台的 **Model access** 页面撤销它。

## 总结

环境智能体把 AI 自动化从“等待用户”转向“响应信号”。行动所需时间从数小时降到数秒，而无需持续人工关注也能实现全天候监控。每个智能体以隔离的会话独立运作，因此平台无需协调开销就能并行处理许多并发事件。人类只在真正需要其输入时才留在环中。统一的 Jobs 页面消除了跨多个工具的上下文切换，而完整会话历史意味着你从不失去对智能体做了什么、为何暂停的跟踪。

### 何时使用环境模式

以下用例总体上描述了环境智能体模式。参考如今自带了为 Amazon S3 和调度器接好的管道。Webhook、数据库变更和外部集成是你在其上接好的扩展点。

只要环境中某个事件应当驱动一份模型可推理、而人类偶尔应发表意见的工作，这一模式就很合适。文档处理流水线是典型例子：文件落下，智能体读取、总结并在行动前请求批准。监控与告警流程受益于同样的形态，由智能体对告警分类并只在需要升级时才问人。计划处理、分析和报告天然契合 cron 路径，而任何沿途需要审批关卡或人工检查点的多步工作流都能干净地映射到 `ask_human` 中断上。

也有一些环境智能体是错误工具的工作负载。实时聊天应用属于一个专为低延迟对话回合而打造的传统聊天智能体。简单的请求-响应 API 根本不需要智能体。一个普通 API 端点更快、更便宜、更容易推理。而对于不需要大语言模型（LLM）推理的纯确定性工作流，AWS Step Functions 仍是正确选择。注意，如果你想要 LLM 推理而不设人工关卡，带 `autoExecute: true` 的环境智能体已经覆盖了完全自主的情形。

### 后续步骤

克隆[参考实现](https://github.com/aws-samples/sample-ambient-agent)，并按顶层 README 进行部署和配置。
