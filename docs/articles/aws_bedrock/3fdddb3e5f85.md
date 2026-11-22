---
vendor: aws_bedrock
title: Migrate agentic workloads to Amazon Bedrock AgentCore
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/migrate-agentic-workloads-to-amazon-bedrock-agentcore
date: 2026-09-03
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 0210dae2943c
---

# 把 agentic 工作负载迁移到 Amazon Bedrock AgentCore

在 notebook 里能跑通的 agent，并不是生产环境里的 agent。真实用户到来之后，你需要承担大量与 agent 推理毫无关系的工作：把某个用户的会话与其他用户的会话隔开，并跨多轮对话、跨多天保持状态；agent 调用的每个工具的鉴权都写在你的代码里；底层操作系统还需要打补丁。这些都只是本文梳理的十项运维负担中的四项。

当 agent 进入生产环境时，还要加上 Amazon Bedrock Guardrails 来过滤有害内容、对照源文档校验 grounding，并拦截 prompt injection 尝试。无论你停在哪一个阶段，这些控制项都适用于任何 agent。

本文从你手上已有的一个 agent 出发。它是一个 [LangGraph](https://langchain-ai.github.io/langgraph/) 客服 agent：对每条消息进行分类，把愤怒的客户升级处理，用三个工具回答其他人，而它的模型调用已经走 Amazon Bedrock。容器、Web 服务器以及进程内的会话状态都由你负责。推理是迁移唯一不会触碰的调用，所以“已经在 Amazon Bedrock 上”并不像听上去那样是一种先发优势。如果你的模型调用直接走 OpenAI 或 Anthropic，只需改一个构造函数，如阶段 0 所示。

本文分两个阶段迁移这个 agent。阶段 1 把它迁移到 [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) Runtime、Gateway 和 Memory 上，graph 保持不变。阶段 2 把循环重建为 Strands Agents 上的模型驱动规划。停在阶段 1，你就得到一个托管的 agent，带有托管的工具和持久化状态。阶段 3 把循环交给 AgentCore harness（Amazon Bedrock AgentCore 的一项能力），本文只做说明，不进行构建。

## 你当前所处的位置

本文中的 agent 负责回答客服问题。客户问订单到哪了，或者如何退货，agent 去查询、能回答的就回答、不能回答的就升级。它运行在你自行开通、打补丁和扩缩容的计算资源上。

最后这句话正是本文的主题。它完全不描述 agent 在做什么。

在代码层面，迁移是有边界的，它只触及四个构造。而你实际运维的东西是一份更长的清单，下一节会把它梳理出来。

| **LangGraph 构造** | **Strands 中的对应物** | **AgentCore 特性** |
| --- | --- | --- |
| `build_graph(...)`，以及运行它的容器和 Web 服务器 | `Agent(model=..., system_prompt=..., tools=...)`，可被调用 | [Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime.html)：`BedrockAgentCoreApp` 与一个 `@app.entrypoint` 函数，每个会话运行在一个 microVM 上 |
| 用 `ToolNode(tools)` 和 `llm.bind_tools(tools)` 绑定的 `@tool` 函数 | 来自 `MCPClient.list_tools_sync()` 的工具，传给 `Agent(tools=...)` | [Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)：一个 AWS Lambda 目标，以名为 `supportTools___<name>` 的 Model Context Protocol（MCP）工具形式发布 |
| 带 `thread_id`（写在 invoke 配置里）的 `MemorySaver()` | `AgentCoreMemorySessionManager(AgentCoreMemoryConfig(...))` | [Memory](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html)：以 `actor_id` 和会话为键的状态 |
| `add_conditional_edges("classify_intent", route_intent)` | 无对应物：模型驱动的规划取代该分支，或者保留 graph | Runtime 原样托管它。没有任何东西取代它 |

最后一行回答了“AgentCore 从我这里拿走了什么”这个问题：什么也没有拿走。Runtime 只是 agent 运行的地方，并不决定它的下一步。丢掉手写分支是一种选择，在阶段 2 才做出。

## 解决方案概览

迁移的意义在于卸掉那些与 agent 推理无关的工作。Amazon Bedrock AgentCore 是一个用于以任意框架或模型大规模构建、连接并优化 agent 的平台。你一项一项地接入它的服务，每接入一项就卸下特定的负担，下图把十项负担映射到对应服务上。Runtime 接走计算，于是操作系统打补丁、自动扩缩容和会话隔离不再由你负责。默认情况下它运行在 AWS 托管的基础设施上，你也可以把它接到自己拥有的虚拟私有云（VPC）里。无论哪种方式，你仍然要设计网络、在你的入口前面部署边缘防护，并决定授权方式。Gateway 接走工具鉴权，并用自己的执行角色调用你的函数。检查点存储交给 Memory，它跨多轮对话、跨进程、跨天保存会话状态。

AWS Identity and Access Management（IAM）策略、VPC 配置、Web 应用防火墙（WAF）规则和密钥轮换在每个阶段都仍由你负责。依赖更新要到阶段 3 才转移，此前任何阶段都不会转。

另外还有三项服务可以在不取代任何东西的情况下接入。Identity 代理凭证，并为 agent 代表某人调用的 API 刷新 OAuth 访问 token。本演练不会用到它。agent 使用自己的 IAM 凭证、以 Signature Version 4 为它的 Gateway 调用签名，随后 Gateway 以自己的执行角色调用 AWS Lambda 目标。这条路径上没有任何环节需要第三方 token。Policy 在 Gateway 上决定每一次单独的工具调用。Observability 无需你配置，就会把 Runtime 的日志、指标和 trace 发送到 Amazon CloudWatch。

按顺序推进各阶段。阶段 1 改变 agent 运行的位置，不改变它如何思考，这样只让一个变量变化。阶段 2 改变它如何规划，而运行时已经过验证。如果团队本来就要重写 agent，可以直接从阶段 2 开始，因为先建好的 gateway、target 和 Memory store 在哪个阶段都能用。阶段 3 只有说明，不做构建。

![标题为“把示例 LangGraph agent 逐阶段迁移到 AgentCore”的对比矩阵。副标题说明每个阶段衡量的两件事：我们不再运维了什么，以及由谁规划下一步；其下方的注释补充说每次只移动一个变量：阶段 1 移动 agent 运行的位置，阶段 2 移动它规划的方式。顶部横贯一条带子，标注为“在每个阶段都不变”，其中放的是 agent 本身：classify、route、escalate、三个工具。四个带编号的阶段列分属三个标题之下。“我们的起点”下是阶段 0——在我们自行运行并打补丁的计算资源上自托管的 LangGraph，标注为基线，报告十项仍属我们。“本文构建的内容”带有一个 Amazon Bedrock AgentCore 图标，下含两个高亮列：阶段 1，replatform，采用 Runtime、Gateway 和 Memory，标注为“本文已走通”，报告五项已移动、五项仍属我们；以及阶段 2，rebuild，循环变为模型驱动的规划，同样标注为“本文已走通”，报告同样的五项已移动、五项仍属我们。“本文之外”下是阶段 3，把循环交出去，由 AgentCore 运行它，标注为“仅有说明”，报告六项已移动、四项仍属我们。标注为“谁规划下一步”的一行，在阶段 0 读作我们的代码，阶段 1 是我们的代码，阶段 2 是模型，阶段 3 是模型。标注为“本阶段移动了什么”的一行读作：阶段 0 尚未移动任何东西，十项全属我们，由我们的 router 规划；阶段 1 有五个移到 AWS，同样五项仍属我们，仍由我们的 router 规划；阶段 2 没有任何运维项移动，同样五项仍属我们，模型接管了规划，且阶段 2 可独立运行；阶段 3 还会再移动一项——依赖更新，本文不构建。随后，十项运维负担作为行沿左侧向下排列：VPC、WAF、IAM 策略、密钥轮换、操作系统打补丁、依赖更新、自动扩缩容规则、会话隔离、检查点存储和工具鉴权。阶段 0 在全部十项上都显示实心方块。阶段 1 与阶段 2 彼此相同：在操作系统打补丁、自动扩缩容规则、会话隔离、检查点存储和工具鉴权上是实心圆，在 VPC、WAF、IAM 策略、密钥轮换和依赖更新上是实心方块。阶段 3 显示六个实心圆，新增了依赖更新，剩下的四个方块是 VPC、WAF、IAM 策略和密钥轮换。图例定义两种标记：实心圆表示已移到 AgentCore，实心方块表示仍由我们运维。页脚说明这些计数是从已提交的示例中量出来的，不是凭空断言的。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/31/ML-20753-1.png)

图 1：哪些运维不再属于你，以及由谁规划 agent 的下一步。阶段 1 改变前者，阶段 2 改变后者

## 迁移演练

[示例仓库](https://github.com/aws-samples/sample-migrate-agents-to-amazon-bedrock-agentcore)按下列阶段组织，因此每个阶段都可以与前一个阶段对比。下图展示这种对比的形态：每个阶段从什么出发、移动了什么，以及为什么接下来是这个阶段。本文凡给出“移动了什么”的计数，都是从已提交的示例中量出来的，而不是估算。

![标题为“示例迁移流程，逐阶段”的示意图。副标题说明阶段 1 和阶段 2 在示例中已构建并运行。三张纵向排列的卡片自上而下以向下箭头相连，每张卡片都把灰色的“问题”与其下方的“结果”配对。第一张卡片是阶段 0，标题为“你已经拥有的 agent”。它的问题写道：一个支持 agent 已经在回答客户问题，而我们团队这一周花在它底下的服务器上，而不是花在它给出的答案上。它的结果以砖红色标示：在动任何东西之前，我们先数了自己运维的东西——十项，全属我们，下面每个阶段都必须比这个数字更好。箭头指向第二张卡片，阶段 1，标题为“同一个 agent，重新部署平台”，带有一个 Amazon Bedrock AgentCore 图标和一个标注“已构建并运行”的标签。它阶段层面的问题写道：有三件独立的事情需要我们来运行，其中没有一件是 agent 真正的职责；它的结果以青色标示：我们一次移动一件，并在每次之后检查，从而能看出每一步到底买到了什么。这卡片内嵌了四个片段，每个都按同样的方式把问题与结果配对。Runtime：agent 底下的操作系统仍需要打补丁，而那是我们的周末而不是模型的；AgentCore Runtime 接管了打补丁，agent 一行代码都没改。Gateway：只有这个 agent 能调用自己的工具，因为权限写在我们代码里；现在 Gateway 持有这些权限，这意味着下一个 agent 可以免费获得同样的工具。Memory：重启进程会丢掉对话，客户注意到了，因为他们得从头再来；现在 AgentCore Memory 保存会话线索，而 agent 的另一个副本能够回答一个它从未见过的订单问题。Verify：有三处发生了变化，不该只凭我们一句话就相信它仍然表现正常。我们重跑了同样的三段对话并对比，行为保持不变，十项负担中有五项现在属于 AWS，五项仍属我们。第二个箭头指向第三张卡片，阶段 2，标题为“因为你选择如此，重建循环”，带有一个 Strands SDK 图标和一个标注“已构建并运行”的标签。它的问题写道：每出现一类新问题，就意味着我们 router 里多一个分支，而每一个分支都是我们写的。它的结果以青色标示：Strands 让模型来规划，而不是我们的 router；没有任何运维项移动；我们失去了一个本来可以审计的分支，并以“我们不会把这称为免费升级”收尾。页脚说明阶段 3 把循环交给 AgentCore harness，只有说明、不做构建。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/31/ML-20753-2.png)

图 2：每个阶段从何出发、移动了什么，以及为什么接下来是这个阶段

### 前置条件

你需要一个已启用 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 模型访问权限的 [AWS 账户](https://aws.amazon.com/free/)、[Python 3.12](https://www.python.org/)，以及配置好凭证的 [AWS 命令行界面（AWS CLI）](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)，该凭证需能创建 AgentCore、Lambda、Amazon Simple Storage Service（Amazon S3）和 IAM 资源。另外还需为该账户启用一次 [CloudWatch Transaction Search](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-get-started.html)，否则本演练产生的 trace 无法查看。

```
git clone https://github.com/aws-samples/sample-migrate-agents-to-amazon-bedrock-agentcore.git
cd sample-migrate-agents-to-amazon-bedrock-agentcore
./setup.sh
```

这会创建一个虚拟环境并安装七项依赖。如果你已经在 Amazon Bedrock 上运行 LangGraph agent，新增的是 `strands-agents`、`bedrock-agentcore`、`mcp` 和 `langgraph-checkpoint-aws`。其中两项固定了版本而不是只给最低版本，因为未固定版本的 `langchain-aws` 会解析到更高版本，并把 `boto3` 一并往前拖。

用测试套件确认安装，它不需要凭证：

```
source .venv/bin/activate
python -m unittest discover -s tests -q
```

### 阶段 0：你已经拥有的 agent

在改动之前先读懂这个 agent，因为它当前的行为是后续每个阶段都必须保持的基线。它是一个编译好的 `StateGraph`：`classify_intent` 让模型给出一个词，手写的 `route_intent` 读取它。愤怒的客户进入 `escalate`，它返回固定的转交话术，不调用模型。其他人进入 `assist`，它在绑定工具的情况下调用模型：

```
builder.add_edge(START, "classify_intent")
builder.add_conditional_edges(
    "classify_intent",
    route_intent,
    {"escalate": "escalate", "assist": "assist"},
)
builder.add_edge("escalate", END)
builder.add_conditional_edges("assist", tools_condition)
builder.add_edge("tools", "assist")

return builder.compile(checkpointer=checkpointer)
```

它挂着三个基于 HTTP 后端的 `@tool` 函数：`lookup_order`、`process_return` 和 `search_faq`。它们返回 `{"error": ...}` payload 而不是抛异常，因为工具节点内的异常会终止整次运行，而错误 payload 是模型可以据此行动的信息。

状态是一个 `MemorySaver` 检查点存储，以调用时传入的 `thread_id` 为键，而这是唯一一处有硬性限制的部分。进程里的字典会随进程一起消亡，两个副本也看不到彼此的对话。这里的其他东西在生产规模下都没问题，唯独它不是。

模型是 `ChatBedrockConverse`，因此推理已经走 Amazon Bedrock，阶段 0 不触碰任何 AgentCore API。如果你是从 OpenAI 或 Anthropic 过来的，那么这个构造函数就是你唯一要改的地方，参数是模型 ID 和 AWS 区域。各区域的模型可用性请参阅 [Amazon Bedrock 中各 AWS 区域支持的模型](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html)。在移动任何东西之前先记录基线：跑了哪些工具，以及图状态中的最终消息，而不是模型的回复。这样下一阶段才是对比，而不是指望。下面的命令在本地运行，不会在 AWS 中创建任何资源：

```
python -m examples.run_walkthrough --stage 0
```

### 阶段 1：同一个 agent，完成迁移

阶段 0 留给你一个可用的 agent 和一份记录好的基线。阶段 1 是十项负担中有五项不再属于你的地方，而 agent 的行为恰恰是不该改变的东西。有三样东西移动：Runtime 接走进程，三个工具中的两个移到 Gateway 之后，会话状态落进 Memory。推理不移动，因为它从来不是问题所在。

迁移后的包不复制阶段 0，而是导入它：

```
from examples.stage0_langgraph.agent import build_graph
from examples.stage0_langgraph.tools import SUPPORT_TOOLS
```

这两行导入承载了图拓扑、router、状态 schema、三个 prompt 和三个工具的全部实现，因此这些内容都不会漂移。它们也让代价可被计数——从磁盘量出来，而不是口头断言：**agent 内部改动了 45 行**、**22 行是 SDK 未提供的新增支撑代码**、**85 行被原样导入**。那 22 行之所以小，只有一个原因：过去昂贵的那部分是在 AgentCore Memory 之上手写的 LangGraph 检查点存储，现在它已经随包发布，所以剩下的胶水代码只有一个工具适配层。

#### Runtime：托管循环

十项运维负担此时仍全在你手上，而基线现在已跨三轮对话记录下来。循环底下的机器最先移动，因为给操作系统打补丁并不是你的 agent 在做的事。这同样是用最少的代码换取最大的回报：操作系统不再由你打补丁，会话隔离变成每个会话一个 microVM。把你现有的循环包进 `BedrockAgentCoreApp`，并给它一个 entrypoint：

```
from bedrock_agentcore import BedrockAgentCoreApp
from langchain_core.messages import HumanMessage

app = BedrockAgentCoreApp()

@app.entrypoint
def agent_invocation(payload, context):
    state = support_graph().invoke(
        {"messages": [HumanMessage(payload.get("prompt", ""))]},
        config={"configurable": {"thread_id": context.session_id or "local-session"}},
    )
    return {"result": state["messages"][-1].text}

if __name__ == "__main__":
    app.run()
```

里面的 invoke 调用就是阶段 0 的那一个。变化的是 `thread_id` 的来源。阶段 0 是自己选的，这里它作为 `context.session_id` 出现，来自 Runtime 传入的 `RequestContext`。图只构建一次并持有它，因为每次请求都重建图会重建模型客户端，并可能拆掉工具所需要的 MCP 会话。

同一个封装也能承载 [CrewAI](https://www.crewai.com/) 或 [LlamaIndex](https://www.llamaindex.ai/) 的循环，或者你自己写的循环：接受一个 payload dict，调用，返回一个 dict。

#### Gateway：发布三个工具中的两个

循环底下的操作系统和计算资源已经不再属于你，但工具鉴权还属于你。把工具放到 gateway 之后的理由，在于随之移动的东西：鉴权不再是你代码的问题，而且触及范围变大——已发布的工具[可以被你的下一个 agent 调用](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)，而进程内的函数永远只属于这个 agent。因此 `lookup_order` 和 `process_return` 变成由 [AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)（Amazon Bedrock AgentCore 的一项能力）从一个 Lambda 函数发布的 MCP 工具。你注册它，而不改动它内部的任何代码。

`search_faq` 在每个阶段都保持为本地 Python 函数，这是常态而非妥协。一个别的 agent 不需要、也没有策略把关的工具，走这一趟没有任何收益。

转换就是在 `bedrock-agentcore-control` 客户端上的两次调用。先创建 gateway，并选择 `authorizerType`。`AWS_IAM` 用你已有的凭证签名，`CUSTOM_JWT` 则需要 bearer token。

```
client = boto3.client("bedrock-agentcore-control", region_name=region)

gateway = client.create_gateway(
    name="MigratedAgentGateway",
    roleArn=role_arn,  # gateway execution role
    protocolType="MCP",
    authorizerType="AWS_IAM",
)
gateway_id = gateway["gatewayId"]
gateway_url = gateway["gatewayUrl"]
```

两个返回值后续都要用到：注册 target 时用 `gateway_id` 指定 gateway，而 `gateway_url` 是 agent 连接的 MCP 端点。

然后注册 target，这一步才是转换本身。把 Gateway 指向你的函数，并用 JSON schema 声明它的工具。

```
response = client.create_gateway_target(
    gatewayIdentifier=gateway_id,
    name="supportTools",
    targetConfiguration={
        "mcp": {
            "lambda": {
                "lambdaArn": lambda_arn,
                "toolSchema": {"inlinePayload": TOOL_SCHEMA},
            }
        }
    },
    credentialProviderConfigurations=[
        {"credentialProviderType": "GATEWAY_IAM_ROLE"}
    ],
)
```

使用 `GATEWAY_IAM_ROLE` 时，Gateway 以自己的身份调用你的函数，并把工具参数作为原始事件传入，因此 Amazon API Gateway 的处理函数需要做适配。

agent 发现这些工具，并对每个请求做 SigV4 签名：

```
import boto3
from mcp.client.streamable_http import streamablehttp_client
from strands.tools.mcp import MCPClient

from examples.tools.gateway_mcp_tools import SigV4HTTPXAuth

auth = SigV4HTTPXAuth(boto3.Session().get_credentials(),
                      "bedrock-agentcore", region)
mcp_client = MCPClient(lambda: streamablehttp_client(gateway_url, auth=auth))
mcp_client.start()  # not a `with` block: held for the process lifetime
tools = mcp_client.list_tools_sync()
```

发现到的工具会带上 target 名称加三个下划线的前缀。`lookup_order` 变成 `supportTools___lookup_order`，在列表里搜原名什么也搜不到。

`list_tools_sync()` 返回 Strands 工具对象，而 LangGraph 的工具节点要的是 LangChain `BaseTool` 对象，两者没有共同接口。那 22 行就在两者之间做转换。同一模块还合并两个来源，以最后一个 `___` 之后的部分来匹配，因此 Gateway 工具会取代同名本地函数，而 `search_faq` 保持本地。

#### Memory：过去随进程一起消亡的状态

计算和工具鉴权移动之后，会话状态是本阶段剩下的边界。它仍然随进程消亡，所以两个实例读不到同一条对话。Memory 让这个限制退场。阶段 0 的 `MemorySaver` 变成由 [AgentCore Memory](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html) 支持的检查点存储，以 `actor_id` 和会话为键，而不是你自己选的 `thread_id`。先创建存储，并有意识地设置 `event_expiry_days`，因为检查点会继承它。

该检查点存储由官方发布，是一项依赖，而不是你拥有的文件。它在你已安装的 requirements 里，且固定了版本：

```
langgraph-checkpoint-aws==1.2.1
```

只用 memory id 构造它，不带其他参数。它不接收 `actor_id`。它每次调用时从 `RunnableConfig` 读取 `actor_id` 和 `thread_id`，而不是在构造时绑定其中任何一个，因此两者随每次调用一起传递：

```
from langgraph_checkpoint_aws import AgentCoreMemorySaver

graph = build_graph(
    llm=llm,
    tools=tools,
    checkpointer=AgentCoreMemorySaver(memory_id, region_name=region),
)

state = graph.invoke(
    {"messages": [HumanMessage(prompt)]},
    config={"configurable": {"thread_id": session_id, "actor_id": actor_id}},
)
```

去测试持久性，别假定它成立。第二个进程只共享 memory、actor 和会话 id，却回答了一个它从未被告知的订单问题。不过不要对事件数量做断言：完全相同的代码跑两次，总数并不一样。

你得到跨实例共享的持久化会话状态，同步与异步皆可。该 saver 还实现了 `list` 和 `delete_thread`。历史记录与时间旅行通过 LangGraph 已在使用的接口就能工作。

#### 部署，并验证它确实运行过

先在本地验证模块，因为失败在本地是看得清的，而在 Runtime 内部则不然。`app.run()` 提供与 Runtime 调用相同的 `POST /invocations` 契约。然后带上 [codeConfiguration](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-code-deploy-python.html) 调用 `CreateAgentRuntime`，它就是放在 Amazon S3 里的源码 zip，旁边附上已 vendored 的依赖。不用容器、不用 Amazon Elastic Container Registry（Amazon ECR）、不用 Docker。如果你在估算这次迁移，这句话就是估算：pip 是部署唯一需要的构建工具。

有两个陷阱很耗时间，而两者的报错都不点明原因。第一，在笔记本上执行 `pip install -t` 装的是笔记本的 wheel，而 Runtime 是 ARM64（Advanced RISC Machine 64-bit）Linux。要为部署所指定的目标应用与 Python 版本做 vendoring，让 wheel 与运行时一致：

```
pip install -r requirements.txt -t build/ \
    --platform manylinux2014_aarch64 --python-version 3.12 --only-binary=:all:
```

那个 3.12 是部署目标的版本，不是你本地解释器的版本。

第二，zip 里的 `requirements.txt` 是无效的。压缩包就是最终环境。漏掉一个依赖时，报错会是 `Runtime initialization time exceeded ... 30s`，而不是实际发生的 `ModuleNotFoundError`。要做的是把依赖 vendoring 进去，而不是调超时时间。

接下来的命令会创建真实的 AWS 资源并开始计费。文末的“清理”一节会移除本演练创建的所有东西。

然后对照你记录的基线进行校验。阶段 1 需要两个 ARN，有一个脚本会创建 gateway target 背后的 Lambda 并打印这两个值：

```
./examples/gateway/lambda_target/deploy.sh
python -m examples.run_walkthrough --stage 1 \
    --role-arn <gateway-role-arn> --lambda-arn <tools-function-arn>
```

阶段 1 打印与阶段 0 相同的逐轮输出，因此检查是一次 diff，而不是对回复文本的主观判断。示例把这个 diff 做成了断言，而不是留给你用眼睛看：`test_stage1_replatform.py` 要求 gateway 调用以 `supportTools___lookup_order` 到达并携带 `{"order_id": "12345"}`，于是工具被改名或参数被丢掉时，运行会失败，而不是在目视检查中蒙混过关。

当 agent 做了你没预料到的事，你需要看见它实际做了什么。通常这意味着你得自己负责埋点：一个 tracing 包、一堆环境变量、一个要跑的 collector。Runtime 会为其托管的 agent 做埋点，AgentCore Observability（Amazon Bedrock AgentCore 的一项能力）把结果发送到 CloudWatch。requirements 里没有 tracing 包，也没有需要设置的 `OTEL_*` 变量。日志组在第一次调用后无需请求就出现，span 则在启用 Transaction Search 之后出现在 CloudWatch 中。

![标题为“阶段 1：重新部署运行时”的架构图。副标题：直接调用、编排不变、部分工具迁移。顶部横贯一条带子，标注为“部署时，而非请求路径”，把源码加 vendored 依赖打成 zip，进入 Amazon S3 成为 agent.zip，进入一次 CreateAgentRuntime 调用（其 codeConfiguration 指回 S3），最终到达“Runtime 已部署”。这条路径上任何地方都没有容器，也没有 Amazon ECR。其下一条标注为“请求路径”的带子，从一张客户端应用卡片开始，该卡片调用 InvokeAgentRuntime，runtimeSessionId 至少 33 个字符，并标注为“直接调用”。一条箭头从它直接进入 Amazon Bedrock AgentCore Runtime 卡片，该卡片被描述为 serverless、每个会话一个 microVM，中间没有负载均衡器，也没有 API Gateway。在 Runtime 卡片内，三个盒子自上而下堆叠。第一是 agent_runtime.py，其中包含 BedrockAgentCoreApp 和一个 @app.entrypoint 函数，并把 RequestContext.session_id 映射到 thread_id。第二是 LangGraph 图，标注为“已导入，未重写”，由阶段 0 的 build_graph 构建，并注明这是同一个图、调用全部三个工具。第三是工具，分成两块：一个以强调色描边、标注为“本地 Python”的盒子放着 search_faq，并说明它留在 Runtime 内；另一个标注为“由 gateway 提供”的盒子放着 supportTools___lookup_order 和 supportTools___process_return，因此三个工具中有两个由 Gateway 提供，一个不是。右侧向下排列四张服务卡片。使用 ChatBedrockConverse 的 Amazon Bedrock 标注为“未移动，本来就是 Bedrock”。从 Runtime 到达的 AgentCore Memory 注明为 AgentCoreMemorySaver——来自 langgraph-checkpoint-aws 的官方 saver。AgentCore Gateway 通过经 SigV4 签名的调用以 MCP 通信，使用 AWS_IAM 授权器，从“由 gateway 提供”的工具盒子到达。AWS Lambda 是 Gateway 的 target，以原始事件接收参数，工具名在客户端上下文中。沿底部有一张可观测性卡片，带有 Amazon CloudWatch 和 AWS Distro for OpenTelemetry 图标，报告 Runtime 的日志、指标和 trace。其旁一张标注为“挂接到此 gateway”的 AgentCore Policy 卡片，注明在阶段 2 演示，描述在数据平面中对每次工具调用来评估 Cedar，并用虚线连到 Gateway。页脚上方的一行记录：阶段 1 的验证方式是重跑阶段 0 的基线、覆盖同样的三轮，并对比跑过的工具与最终状态；同时说明 VPC 配置、WAF、IAM 策略、密钥轮换和依赖更新仍属我们。页脚一行读作：阶段 1 重新部署了运行时，没有负载均衡器、没有 API Gateway、没有容器、没有 Amazon ECR。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/31/ML-20753-3.png)

图 3：客户端直接调用 Runtime，图是导入而非重写，三个工具中的两个移到 Gateway 之后

这就是阶段 1：同一个 agent 给出同样的回答，十项负担中已有五项由 AgentCore 承担。谁规划下一步没有改变，而这个问题属于阶段 2。

### 阶段 2：因为你选择如此，重建循环

十项运维负担中已有五项移动，还有五项仍属于你：VPC 配置、WAF、IAM 策略、密钥轮换和依赖更新。阶段 2 一项也不移动，因为这个阶段改变的是“谁规划下一步”。当手写分支成为天花板时就走这一步：当 `route_intent` 是你不停在改的文件，而新增一种意图意味着新增一个节点、而不是在 prompt 里加一行。

模型驱动的编排取代该分支。阶段 0 的 `classify_intent` 节点和 `route_intent` 用 Python 决定下一步。Strands agent 把这个决定交给模型，因此 `add_conditional_edges` 没有对应物。这既是收益也是损失。该分支是确定性的、可审计的，而模型的计划两者都不是。

`bedrock-agentcore` SDK 为 Strands agent 提供了会话管理器，所以接线就是一个配置对象加一个构造参数：

```
config = AgentCoreMemoryConfig(
    memory_id=memory_id, session_id=session_id, actor_id=actor_id
)
kwargs["session_manager"] = AgentCoreMemorySessionManager(
    config, region_name=region_name
)

return Agent(**kwargs)
```

会话管理器与模型、system prompt 和工具一起进入 `Agent(**kwargs)`，它携带阶段 1 的那三个 id，只是 `thread_id` 现在叫 `session_id`。

阶段 2 复用阶段 1 的 gateway、target 和 Memory 存储。它不复用阶段 1 的 runtime，因为里面的程序是另一个循环。Amazon Bedrock 在这里也没有移动：每个阶段都是同一个模型。用同样的两个 ARN 运行它：

```
python -m examples.run_walkthrough --stage 2 \
    --role-arn <gateway-role-arn> --lambda-arn <tools-function-arn>
```

#### 对工具调用本身的授权

阶段 2 把规划交给模型，也失去了可审计的分支。[Amazon Bedrock AgentCore 中的 Policy](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy.html) 把确定性的决策重新放到每次工具调用之前：Cedar 规则通过 gateway、在数据平面上、在应用无法绕过的路径上对每次调用求值。针对模型输出的 guardrail 不在这条路径上，等它运行时，工具调用已经发生了。

Policy 挂接在 Gateway 上而不是循环上，所以它在阶段 1 的 agent 上不加改动就能生效。它出现在这里，只是因为示例在这里运行它。

示例提供两条规则：只读身份可以调用 `lookup_order`，特权身份还可以调用 `process_return`。**任何地方都没有 `forbid` 规则。** Cedar 默认拒绝，因此只读调用方被拒绝，是因为缺少匹配的 permit。如果你来自 IAM，这是需要改掉的习惯。

两个调用方角色用完全相同的 IAM 策略创建，因此可以证明这项强制来自 Cedar，而不是 IAM 的缺口。相同权限、同一个 gateway、两个调用方对两个工具、一次拒绝。

![标题为“阶段 2：重建循环”的架构图。副标题：模型驱动的规划、SDK 提供的 memory 接线、每次工具调用上的 Cedar。上半部分标题为“重建改变了什么”，包含两张卡片。第一张标注为“循环，已重建”，展示一个 Strands Agent 在 AgentCore Runtime 上运行 strands_agent.py，采用模型驱动的规划而不是 router，没有 route_intent 也没有 add_conditional_edges，并注明失去的是一个确定性、可审计的分支。第二张标注为“memory 接线，SDK 提供”，展示 AgentCore Memory 复用阶段 1 的存储，SDK 会话管理器名为 AgentCoreMemorySessionManager。下半部分标题为“证明：数据平面中的 Cedar”，包含 AgentCore Policy，描述为“两个调用方乘以两个工具”，在 Gateway 上、在数据平面中对每次工具调用求值，并注明 2×2 是能归因一次拒绝的最小实验，因为单看一次被拒绝的调用像是 IAM 缺失。随后是一个 2×2 表格：只读角色被允许 supportTools___lookup_order，但因没有匹配的 permit 而被拒绝 supportTools___process_return；支持 agent 角色则两者都允许。两行文字说明：任何地方都不存在 forbid 规则，因为 Cedar 默认拒绝，所以拒绝就是缺少 permit；两个角色的 IAM 策略完全相同，所以那一次拒绝可以证明是 Cedar 造成的。一条虚线箭头向下指向最后一个带子，其标签列出被复用的东西：Gateway、target 和 Memory，但不包括阶段 1 的 runtime，并注明演练步骤 1 到 3 为任一阶段构建它们。该带子展示带 AWS_IAM 授权器的 AgentCore Gateway、作为不变 target 的 AWS Lambda，以及作为每个阶段同一模型的 Amazon Bedrock，并补充说 Memory 存储也是阶段 1 的、两个 Gateway 工具取代同名的本地 stub、search_faq 如每个阶段一样保持本地、部署沿用与阶段 1 相同的 zip 路径。页脚一行说明归属未变：VPC 配置、WAF、IAM 策略、密钥轮换和依赖更新；改变的是谁来做规划。第二行页脚注明 AWS_IAM 主体携带 ARN 且没有标签，因此规则把工具限定到调用方，无法更细。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/31/ML-20753-4.png)

图 4：循环归模型所有，memory 接线收敛为 SDK 提供的会话管理器，而 Cedar 在 Gateway 上决定每次工具调用

循环现在归模型所有，但它仍作为你的代码交付。阶段 3 就是去掉最后这一块的样子。

### 阶段 3：把循环交出去

有一项负担始终与“拥有代码”绑定，而这是唯一移动它的阶段。[AgentCore harness](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-vs-runtime.html) 会替你运行循环，由 Strands Agents 驱动。你把 agent 声明为配置（模型、system prompt、工具、memory 和限制），由 AWS 运行它，于是切换模型是配置变更而不是重新部署。如果你要使用 harness，你运行的就是阶段 2 的 agent。它托管的是单一模型驱动循环，而不是图，所以图形态的 agent 必须先变成那个循环才能用上它。这也是唯一一处“推荐顺序”同时就是“唯一顺序”的地方。

图中把那一列标为“有说明”而非“已测量”。十项负担中有六项在那里移动，而阶段 2 是五项；这里唯一新移动的是依赖更新，因为 agent 不再是你写的代码。密钥轮换不在其中。Identity 刷新的是 token，而不是轮换 token 背后的密钥，所以那项负担在阶段 3 也仍属于你。

## 常见陷阱

迁移改变的不只是基础设施。以下是团队在迁移之后最耗时间的几种模式。

### 1. 假设功能对等

假设功能对等，会埋下一场谁也结束不了的争论。迁移之后你的 agent 不会表现完全一致，而如果没有在迁移前约定好标准，每一处措辞差异都会变成那场争论。请把验收标准定义在结果上而不是实现上，然后去测试它们：90% 的订单状态查询无需升级即解决、响应时间在 5 秒以内。[AgentCore Evaluations](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations.html)（Amazon Bedrock AgentCore 的一项能力）内置了评估器。

### 2. 把状态放在进程里

这一项的代价在生产环境里由一位离开了一会儿的用户付出，因为任何快速测试都不会闲置到足够久去撞上它。会话不是一次调用：一个会话承载一次又一次调用，而 Runtime 默认在闲置 15 分钟后结束执行环境，并为同一个会话开通新的环境。这个闲置窗口就是 [idleRuntimeSessionTimeout](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-lifecycle-settings.html)，可在 60 秒到 8 小时之间设置，所以调整它只是把期限挪后，而不是取消它。会话存活下来，你的内存状态不会，症状是状态只在安静一段时间之后才消失。像阶段 1 那样持有图，但下一轮需要的每一个事实都要放进 Memory。

### 3. 忽视身份验证架构

身份验证上的缺口带来的是返工，而不是配置调整：需要用户委托访问的工具会在后期才浮现，并改变调用路径。所以先把每条流程画清楚：你的 agent 如何对外部 API 进行身份验证、人如何对 agent 进行身份验证、你如何限定权限范围。AgentCore Identity（Amazon Bedrock AgentCore 的一项能力）回答第一个问题——在你的 gateway target 上引用它即可替代 `GATEWAY_IAM_ROLE`。

## 清理

为避免持续计费，请移除你创建的内容。演练会拆掉它创建的所有东西：

```
python -m examples.run_walkthrough --teardown
```

这是按依赖顺序排列的十二个资源，其中要注意的是 Amazon CloudWatch 日志组。没有人请求它，服务在 runtime 打出第一行日志时创建了它，而删除 runtime 并不会删除它。先删除 gateway target 再删除 gateway，并轮询 `GetMemory` 直到存储消失，因为 `DeleteMemory` 会先返回。

支撑你工具的 Lambda 函数、它的执行角色以及 gateway 的执行角色都需要你自己删除。

## 结论

阶段 1 是一个可以停下的点。你在托管计算上得到你已经信任的编排，并带有托管工具和持久化状态。对有手写路由已成为约束的 agent 而言，阶段 2 也是一个停下的点。阶段 3 则把循环移出你的代码库。

这些事情不需要做两次。AgentCore 的特性以四种形态接入：gateway 工具是一个关键字参数，检查点存储是一个固定版本的依赖，会话管理器是一个配置对象，Policy 是一个 Cedar 规则文件。再接入 Identity 或第二个 gateway target，就是这样的改动量，而不是再做一次本次迁移。

对大多数 agent 来说顺序相同，而停下的阶段不同。有状态会话和硬性的外部依赖，是你需要重排顺序的地方。

欢迎留言提出你的问题或分享你自己的经验。

## 下一步

克隆[示例仓库](https://github.com/aws-samples/sample-migrate-agents-to-amazon-bedrock-agentcore)，阅读其中的[安全架构对比](https://github.com/aws-samples/sample-migrate-agents-to-amazon-bedrock-agentcore/blob/main/docs/security-comparison.md)，然后参阅 [Amazon Bedrock AgentCore 文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)。

## 关于作者
