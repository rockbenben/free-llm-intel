---
vendor: aws_bedrock
title: Introducing Web Search on Amazon Bedrock AgentCore
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/introducing-web-search-on-amazon-bedrock-agentcore
date: 2026-06-19
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 3963958d2cc5
---

# 推出 Amazon Bedrock AgentCore 上的 Web Search

AI agent 正在改变组织查找信息并据此行动的方式，但它们都有一个结构性的局限：知识在训练时就冻结了。当你向一个只依赖训练数据的 agent 询问今天的股价、一场比赛的比分，或者一小时前刚发布的版本时，它无法作答。

[Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) 上的 *Web Search* 现已正式可用（generally available），正好补上这个缺口。这项全托管、兼容 Model Context Protocol（MCP）的网页搜索能力，让 agent 无需承担基础设施开销就能从网页获取信息。它以托管目标（target）或连接器（connector）的形式提供，你把它接入自己的 [AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html) 即可。agent 通过标准的 `tools/list` 调用发现它，并像调用其他 MCP 工具一样调用它。无需预置搜索 API，无需管理出站凭证，也无需维护结果解析用的胶水代码。

这个单一连接器的背后，是 Amazon 自行维护、专为此用途构建的网页索引，覆盖数百亿份文档。Amazon 持续刷新该索引，几分钟内就能反映新内容。其隐私模型确保查询不会离开 AWS。检索可以把知识图谱与针对模型上下文调优的语义片段抽取结合起来。

在本文中，我们会说明 Amazon Bedrock AgentCore 上的 Web Search 有何不同、为什么重要，以及如何用几行代码把它接进来。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/06/17/ml-21231-image1-new.png)

**图 1：** 你的应用连接到 AgentCore Gateway（入站认证使用 AWS Identity and Access Management（IAM）或 JSON Web Token（JWT）），Gateway 再通过托管连接器把查询路由到 AWS 服务账号中的 Web Search 工具。查询流量始终留在 AWS 内部。

把 agent 落地到网页上是解决知识陈旧的办法，但很多团队也正是卡在这里。自己动手构建意味着：

- 采购第三方搜索 API，并管理密钥、配额和速率限制。
- 解析各家提供商互不一致的结果格式。
- 想清楚客户查询会流向哪里，以及这些数据可能如何被保留或复用。
- 编写片段抽取逻辑，让模型拿到相关段落而不是原始 HTML。
- 长期维护新鲜度、覆盖范围和质量。

其中每一项本身就是个项目。Amazon Bedrock AgentCore 上的 Web Search 把它们一并解决了。

## 专为此用途构建的网页索引

许多“给 agent 加上网页搜索”的方案，其实是对第三方搜索引擎的封装。Amazon Bedrock AgentCore 上的 Web Search 由 Amazon 直接运营的网页索引支撑，覆盖数百亿份文档。这样的规模对覆盖率很关键。举例来说，关于某个小众库或某个冷门产品规格的长尾问题，只有当索引足够广、而不是只局限于最热门的页面时，才能被更有效地回答。

### 持续刷新

Amazon 持续刷新该索引，几分钟内就能反映新内容。对于需要回答价格波动或最近发布的公告类问题的 agent 来说，这个新鲜度窗口决定了它给出的是有据可依的回答，还是自信满满的错误回答。当你的 agent 搜索“今天发生了什么”时，结果反映的就是今天真实发生的事。

### 高置信事实用的知识图谱

Amazon Bedrock AgentCore 上的 Web Search 内置知识图谱，为实体及其关系提供依据。对于事实型问题（比如谁担任某个职位、某事物创立于何时），知识图谱给出高置信度的回答，而不是让模型从抽取出的页面文本里去推断。这减少了 agent 仅凭片段拼凑回答时容易渗入的那种细微事实漂移。

### 面向模型上下文优化的语义片段抽取

这个工具不会把原始 HTML 转储或整页内容丢给模型、指望它自己找到相关部分，而是执行语义相关的片段抽取。它从每个网页中取出与查询有关的段落，再以针对模型上下文窗口优化的形式返回。模型只看到真正重要的部分，花在样板文字和导航装饰上的 token 更少。这有助于提升带引用回答的精确度。

## 从设计上保证隐私

对许多企业来说，拦住网页搜索上线的并不是“它能不能用”，而是“我的用户查询会去哪里，之后又会怎样”。Amazon Bedrock AgentCore 上的 Web Search 的构建方式，让这些问题的答案很简单。

### 查询不离开 AWS

当你的 agent 发起搜索时，查询完全在 AWS 基础设施内完成。客户查询不会被发送到第三方搜索引擎，也不会离开 AWS。Gateway 向 AWS 自有的连接器做认证，并在内部路由请求，因此数据通路端到端都留在 AWS 内。对于有数据驻留或第三方出站顾虑的团队来说，这直接消除了一整类评审工作。

## 上手演练

要开始使用 Web Search 工具，你需要创建一个 AgentCore Gateway（如果你不想用现有的），添加 web search 工具目标，然后从 agent 中通过 MCP 调用它。

### 前置条件

要跟着本文的设置步骤操作，你需要：

- 一个 AWS 账号，并具备创建 IAM 角色和 Amazon Bedrock AgentCore 资源的权限。
- 已安装并配置好的 AWS Command Line Interface（AWS CLI）v2，或者可以访问 AWS Management Console。
- Python 3.10 或更高版本（用于 SDK 和 Strands 示例）。
- 已更新到最新版本的 `boto3` SDK。
- 一个 Amazon Bedrock AgentCore Gateway。你可以把 Web Search 工具作为目标加到现有 Gateway 上，也可以新建一个。创建 Gateway 的说明见开发者指南中的 [Create an Amazon Bedrock AgentCore gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-create.html)。

注意：按这些步骤操作会创建产生费用的 AWS 资源。Amazon Bedrock AgentCore Gateway 和 Web Search 的调用都是计费的。详情见后面的“定价”一节，并记得在完成后清理资源，以免持续产生费用。

### 设置

给 agent 加上网页搜索，归结起来就是用 `connectorId: "web-search"` 把一个 Web Search 工具目标附加到你的 Gateway 上。Gateway 会快照工具 schema、预置集成，并替你处理 schema 管理、参数治理、端点解析和服务认证。

```
import boto3

gateway_client = boto3.client("bedrock-agentcore-control", region_name="us-east-1")

# Add the Web Search Tool as a target on an existing Gateway
gateway_client.create_gateway_target(
    gatewayIdentifier=gateway_id,  # your existing or newly created Gateway ID
    name="web-search-tool",
    targetConfiguration={
        "mcp": {
            "connector": {
                "source": {"connectorId": "web-search"},
                "configurations": [{"name": "WebSearch", "parameterValues": {}}],
            }
        }
    },
    credentialProviderConfigurations=[
        {"credentialProviderType": "GATEWAY_IAM_ROLE"}
    ],
)
```

通过调用 `describe_gateway_target` 或 `list_gateway_targets`，并确认响应中出现 Web Search-tool，来验证目标已添加成功。

### 出站角色与权限

注意前面代码里的 `credentialProviderConfigurations`。这就是出站授权的全部故事：你不必再去预置 API 密钥或管理搜索凭证，Gateway 使用自己的 IAM 服务角色向 Web Search 后端做认证。

该角色需要一份信任策略（让 AgentCore 能代入它，并限定到你的账号和区域），以及一份包含两个操作的权限策略：

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "InvokeGateway",
      "Effect": "Allow",
      "Action": "bedrock-agentcore:InvokeGateway",
      "Resource": "arn:aws:bedrock-agentcore:us-east-1:<ACCOUNT_ID>:gateway/<gateway-ID>"
    },
    {
      "Sid": "InvokeWebSearch",
      "Effect": "Allow",
      "Action": "bedrock-agentcore:InvokeWebSearch",
      "Resource": "arn:aws:bedrock-agentcore:us-east-1:aws:tool/web-search.v1"
    }
  ]
}
```

`InvokeWebSearch` 的资源 ARN 归 AWS 所有（账号为 `aws`）。授权是按调用、针对该 ARN 强制执行的，所以正是授予它 `bedrock-agentcore:InvokeWebSearch` 权限，才让 Gateway 能够代表你调用网页搜索。

有几条边界需要分清：

- 这个角色只用于出站认证（Gateway 访问 Web Search 后端）。入站认证（谁能调用你的 Gateway）是另外处理的，通常用 OAuth 或 JWT 授权器，例如 Amazon Cognito。
- 该角色不包含 `bedrock:InvokeModel`。模型访问权限属于运行你的 agent 的那个身份，而不属于 Gateway 的服务角色。

### 从 MCP 兼容框架中调用

由于 Web Search 通过 MCP 暴露，像 Strands、LangChain、LangGraph、CrewAI 或你自己实现的 MCP 兼容框架都能发现并调用它。agent 调用 `tools/list`，找到 `WebSearchTool`，然后在需要最新信息时自动使用它：

```
from datetime import date
from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.tools.mcp import MCPClient
from mcp_proxy_for_aws.client import aws_iam_streamablehttp_client

gateway_url = "https://gateway-<id>.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"

mcp_client = MCPClient(lambda: aws_iam_streamablehttp_client(
    endpoint=gateway_url,
    aws_region="us-east-1",
    aws_service="bedrock-agentcore",
))

model = BedrockModel(model_id="us.anthropic.claude-sonnet-4-6")

system_prompt = (
    f"You are a helpful assistant. Today's date is {date.today().isoformat()}. "
    "Use the available tools when you need current information."
)

with mcp_client:
    tools = mcp_client.list_tools_sync()  # WebSearch tool discovered from the Gateway
    agent = Agent(model=model, tools=tools, system_prompt=system_prompt)

    result = agent("What are the latest AI breakthroughs announced this week?")
    print(result)
```

agent 判断自己需要最新信息，用合适的查询调用 `WebSearchTool`，并组织出带有来源引用的有据回答。你这边不需要写任何工具专用代码。

### 响应格式

结果以标准的 MCP `tools/call` 信封返回。该工具返回一个类型为 `text` 的 `content` 块，里面是包含结果的序列化 JSON 文档。解析这段内层文本，你会得到一个 `id` 和一个存放观测结果的 `results` 数组：

```
{
  "publishedDate": "04:43AM, Wednesday, June 17 2026, PDT",
  "text": "The 2026 NBA Finals was the championship...",
  "title": "2026 NBA Finals",
  "url": "https://en.wikipedia.org/wiki/2026_NBA_Finals"
}
```

每条网页索引观测结果（总是返回）都带有 `title`、`url`、`publishedDate` 和 `text`。知识图谱观测结果（可选，用于实体查询）的 `title` 和 `url` 为 null，并在 `text` 字段中给出结构化的键/值事实。

## Web Search 工具的定位

如果你需要用企业自有数据为 agent 提供依据，Amazon Bedrock Knowledge Bases 和 Amazon Bedrock Managed Knowledge Bases 就是合适的工具。它们对你拥有的内容做摄取、索引和检索。Web Search 工具则是补足的角色：它为 agent 提供公共网页上的依据，用来回答那些答案存在于组织之外、并且每一分钟都在变化的问题。许多生产环境中的 agent 两者都用：知识库回答“我们的文档怎么说的”，网页搜索回答“世界上现在什么是真的”。

## 定价

按每 1,000 次查询 7 美元的价格，采用按量付费模式，跑一个网页搜索 agent 每个问题花费不到一美分。

## 清理资源

如果你在跟着操作时创建了资源，可以把它们删掉以避免持续产生费用：

- 删除 Gateway 目标：用你的 `gatewayIdentifier` 和 `targetId` 调用 `delete_gateway_target`。
- 如果该 Gateway 是专为本次演练创建的，用 `delete_gateway` 将其删除。

除了这些资源之外，AWS 侧没有持久化的基础设施。资源移除之后，你就不再产生费用。

## 结论

Amazon Bedrock AgentCore Web Search 工具通过一个 `connectorId` 就把最新的网页知识交给你的 agent。无需预置搜索 API，也无需维护结果解析。在这份简洁之下，是 AWS 自行构建的网页索引（数百亿份文档、几分钟内刷新）、让查询不离开 AWS 的隐私模型，以及可以把知识图谱与针对模型上下文调优的语义片段抽取结合起来的检索能力。最终得到的 agent 能准确回答时效性问题、引用来源，并把你的数据留在它该在的地方。

由于整条搜索栈都由 Amazon 运营，新鲜度、覆盖率、相关性和片段质量的改进会通过同一个托管连接器自动流到你的 agent，你这边不需要做版本升级或迁移。

你现在就可以在 `us-east-1`（美国东部（弗吉尼亚北部））区域使用 Web Search 工具连接器。

要开始使用，请参阅 [Web Search 工具文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-target-connector-web-search-tool.html)。

## 关于作者
