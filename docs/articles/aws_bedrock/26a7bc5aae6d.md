---
vendor: aws_bedrock
title: Amazon Bedrock AgentCore harness is now generally available: Go from idea to production-grade agent in minutes
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-harness-is-now-generally-available-go-from-idea-to-production-grade-agent-in-minutes
date: 2026-06-18
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: b60b0150732c
---

# Amazon Bedrock AgentCore harness 正式可用：从想法到生产级 agent 只需几分钟

一年前，Simon Willison 写下了关于 agent 的一个最简洁的定义，并且一直流传至今：

> 一个 LLM agent 在循环中运行工具，以达成某个目标。

这个定义之所以站得住，是因为它描述了每一个生产环境 agent 实际在做的事。Kiro、Amazon Q Developer、Quick Agents、Codex、Claude Code：在底层，它们运行的都是同一种形态。agent 循环是共同的分母。

但这个循环从来都不是难的部分。难的是围绕它的一切。

选一个框架。把工具接好。备好沙箱化的计算资源。配置存储、密钥、网络。决定记忆放在哪里。再加装可观测性。把正确的依赖装进正确的容器。而且，本地原型往往是最容易的部分：一个开发者可以在一个下午之内就在自己的笔记本电脑上把一个 agent 立起来。**真正让工作量爆炸的是把它送进生产环境**，而一旦它需要服务不止一个用户，一整层新的工作就会出现：并发、隔离、身份、状态、扩缩容。

更糟的是，每增加一个新的用例，这些开销就会成倍放大。那些想做实验、想换一个模型、想替换一个工具、想把 agent 指向一个新领域的团队，发现自己在一遍又一遍地重复同样的管线搭建工作。瓶颈从来不是智能，而是编排与基础设施。

今年 4 月我们以预览版推出 **AgentCore harness** 时，我们下了一个判断：AgentCore 的原语（Runtime、Memory、Gateway、Browser、Identity、Observability）已经为团队提供了在生产环境运行 agent 所需的一切；他们不该做的是每次都手工把这些原语接起来。harness 以一种托管抽象的方式处理这些接线工作，于是它变成了你去配置的东西，而不是你去构建的东西。

今天，**Amazon Bedrock AgentCore harness 正式可用（GA）**。两次 API 调用（用 [CreateHarness](https://docs.aws.amazon.com/bedrock-agentcore-control/latest/APIReference/API_CreateHarness.html) 定义 agent，用 [InvokeHarness](https://docs.aws.amazon.com/bedrock-agentcore/latest/APIReference/API_InvokeHarness.html) 运行它）、在 AgentCore CLI 里走一遍快速上手流程（如下面的 gif 所示），或者在控制台里点几下，你就能在几分钟内让一个 agent 跑起来。它运行在自己隔离的环境中，带有文件系统和 shell，因此可以安全地读取文件、执行命令、编写代码。它能跨会话记住用户与对话，加载你指向的 skills（包括 AWS 精选目录），浏览网页，通过 gateway 或 MCP 调用你的工具，并且能在会话中途切换模型供应商而不丢失上下文。每一步都会实时流式返回给你，并自动追踪到 CloudWatch。除非你确实想这么做，否则无需编写编排代码，也无需构建容器。

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/harness-cli-full.gif)

## harness 为你提供什么

harness 就是 agent 在生产环境运行所需的一切，被封装在两次 API 调用之后。你指定想要的模型、工具、skills 和指令。AgentCore 负责沙箱环境、记忆、存储、身份，以及把所有这一切串联起来的可观测性。GA 新增的能力在下图中以星号标出。

![AgentCore harness 的架构图：两次 API 调用的表层（CreateHarness、InvokeHarness）包裹着 AgentCore 原语——Runtime、Memory、Gateway、Browser、Code Interpreter、Identity 与 Observability。GA 新增的能力以星号标出。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/06/11/ML-20804-1.png)

## 任意模型：为任务选择正确的模型，需要时随时切换

不同的任务需要不同的模型。客户告诉我们，他们希望用一个模型做规划、用另一个模型做执行，为了做性价比测试而替换供应商，或者从一个刚出了回归问题的模型上迁走，而这一切都不能丢掉对话。在 `CreateHarness` 上选择一个默认模型，然后在你需要时于任何一次 `InvokeHarness` 调用上覆盖它。其余每一次调用都保持这个默认值。为你想要的供应商设置 `model` 上对应的字段：

- `bedrock`：用于在 Amazon Bedrock 上提供的任何模型，包括 Anthropic Claude、Amazon Nova、Meta Llama、DeepSeek、Qwen、Kimi、MiniMax、Cohere、Mistral，以及最近上线的 [Amazon Bedrock 上的 OpenAI GPT-5.5 与 GPT-5.4](https://aws.amazon.com/blogs/aws/get-started-with-openai-gpt-5-5-gpt-5-4-models-and-codex-on-amazon-bedrock/)
- `openAi`：直接访问 OpenAI 的 API（api.openai.com）
- `gemini`：用于 Google Gemini
- `liteLlm`：用于 [LiteLLM](https://docs.litellm.ai) 支持的任何第三方供应商，包括 Anthropic 直连、Cohere、Mistral、Vertex、Azure OpenAI 等

而客户说最重要的一点是：**可以在任何时候切换供应商，甚至在会话中途，并且保持上下文。**例如，你可以用 Claude Opus 做规划，切到 GPT-5.5 写代码，再切到 Gemini 做总结。对话继续进行。harness 无缝地处理这次切换。

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/Invoke+Harness.gif)

如果你使用 API key 访问任何底层模型供应商，它们会被安全地存放在 **AgentCore Identity 的 token vault** 中。agent 永远看不到原始凭证。

## 工具即配置：无需编写胶水代码即可让你的 agent 连接世界

工具是 agent 影响自身推理之外任何事物的方式，而把这些工具接起来，正是大多数团队暗中讨厌的部分。客户告诉我们，他们不想为每个 API 编写适配代码，不想管理 MCP 服务器的生命周期，也不想自己构建浏览器沙箱。他们想声明 agent 可以使用什么，然后让 harness 去处理连接、认证与执行。

`CreateHarness` 上的 `tools` 是一个列表。每个条目有一个 type 和一个 config 块，harness 会把它们接进来：

- `agentcore_gateway`：你可以按 ARN 引用一个 [AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)。网关暴露的每个 target（OpenAPI、Smithy、Lambda、MCP）都会以一个工具的形式出现，IAM/JWT 认证、按工具授权以及出站凭证代理都由它替你处理。
- `remote_mcp`：你可以按 URL 直接连接任何 MCP 服务器。当服务器本身已经做好安全防护、你不需要在它前面加一层 Gateway 的治理时，这很合适。
- `agentcore_browser`：用一行引用即可获得一个完整的浏览器沙箱。点击、输入、导航、截图。
- `agentcore_code_interpreter`：沙箱化的 Python 与 Node 执行，同样是单行模式。
- `inline_function`：harness 会把一个工具 schema 作为 tool-use 事件发到流中，并等待你回应。它适用于人在回路中的审批，或者必须在你自己这一侧运行的工具。

```
"tools": [
  { "type": "agentcore_browser" },
  { "type": "agentcore_code_interpreter" },
  { "type": "remote_mcp",
      "name": "X_tool",
      "config": { "remoteMcp": { "url": "https://mcp.X_tool/mcp" } } },
  { "type": "agentcore_gateway",
      "name": "Y_tool",
      "config": { "agentCoreGateway": { "arn": "arn:aws:bedrock-agentcore:..." } } }
]
```

每个会话还内置了 shell（在 microVM 内执行命令）与 `file_operations`（在 agent 的文件系统上读写），无需你显式列出。正是它们让有状态的文件系统与 shell 方案能从模型侧真正可用。

在 `InvokeHarness` 上你有同样的选项来做按调用修改：可以传入新的 tools 来改变单次调用的工具集合，也可以通过 `allowed_tools` 参数把列表裁剪成这一次调用所需要的专注集合。默认值在创建时设定，但你在调用时可以轻松覆盖。

## 内置记忆：你的 harness 会记住用户与对话

客户希望自己的 agent 能认出回访的用户、从上一次对话中断的地方继续，并在没有人重放消息历史的情况下记住偏好。在预览版中，你必须单独供应一个 AgentCore Memory 资源并传入它的 ARN，这虽然可用，但等于多一次 API 调用，而且在上生产的路上很容易被忘掉。

在 GA 版本中，在 `CreateHarness` 上省略 memory 会自动供应一个托管 memory，并带有合理的默认值：`SEMANTIC` + `SUMMARIZATION` 策略、30 天事件过期、AWS 自有加密，以及默认通过以 `actorId` 为键的命名空间模板实现的多租户隔离。它是一个真实的、归客户所有的 Memory 资源，只是由系统为你供应。Memory 并非强制。如果你的 agent 是无状态的，设置 `memory: { disabled: {} }`，harness 就会完全跳过 memory。如果你更愿意挂载一个自己已有的 AgentCore Memory 资源，传入带有其 ARN 的 `agentCoreMemoryConfiguration`。这三条路径看起来如下：

```
// Configure built-in memory 

"memory": { 
 "managedMemoryConfiguration": { 
    "strategies": ["SEMANTIC", "SUMMARIZATION"], 
    "eventExpiryDuration": 30 
  } 
} 

// BYO existing memory 

"memory": { "agentCoreMemoryConfiguration": { "arn": "arn:aws:bedrock-agentcore:..." } } 

// Stateless agent 
"memory": { "disabled": {} } 
```

切换到自己的 memory 只需一次 `UpdateHarness` 调用。传入带有你 memory ARN 的 `agentCoreMemoryConfiguration`，之前托管的 memory 会立即解除关联。它仍然是你账户中一个普通的 AgentCore Memory 资源，因此你可以在任何地方继续使用它、把它挂到另一个 harness 上、直接查询它，或者按你自己的条件删除它。当你删除 harness 时，托管 memory 默认会被级联删除（`deleteManagedMemory: true`）。如果你想保留它，传入 `deleteManagedMemory: false`。

托管 memory 虽然自动创建，但并不是黑箱。它是一个真实的、可寻址的 AWS 资源，你可以查询它、把它挂到另一个 agent 上、审计它，或者交给一条分析 pipeline。

## Skills：为 agent 在正确的任务上提供正确的专业能力

客户希望自己的 agent 在尝试某个具体任务之前就知道该怎么处理它。例如，如何格式化一份 Excel 报表、如何按团队的方式提交 JIRA 工单，或者如何遵循 AWS 推荐的流程来访问他们在 AWS 上的数据。Skills 就是你按需把这些知识交给 agent 的方式。它们是一组文件、脚本与指令的打包。harness 会加载 skill 的元数据，只在任务真正需要时才把完整内容拉进上下文。

在 GA 版本中，[HarnessSkill](https://docs.aws.amazon.com/bedrock-agentcore-control/latest/APIReference/API_HarnessSkill.html) 是一个包含四种来源的 union，因此你可以以声明式的方式挂载 skills，而不必把它们烤进容器里，或者 shell 进去：

- `awsSkills` – 开启 AWS 精选的 skill 包。
- `git` – 通过 HTTPS 克隆一个公共或私有仓库，并固定在某个提交或分支上。
- `s3` – 从你自己的 Amazon Simple Storage Service（Amazon S3）存储桶中拉取 skill 包。
- `path` – 引用你自带容器中已经存在的某个路径。

```
"skills": [ 
 { "awsSkills": {*} }, 
  { "git": { "uri": "https://github.com/anthropics/skills", "path": "document-skills/xlsx" } }, 
  { "s3":  { "uri": "s3://my-bucket/skills/team-sops/" } } 
] 
```

同样的形态在 `InvokeHarness` 上也适用，用于按调用分层。harness 会在会话启动时把每个 skill 落到会话文件系统上；如果 Skills 配置发生变化，则在下一次调用时落盘。

**对 AWS 构建者而言最大的解锁点：**[AWS skills 仓库](https://github.com/aws/agent-toolkit-for-aws/tree/main/skills) 提供了覆盖 AWS 各领域的精选 skills，从核心 skills（SDK 用法、基础设施即代码（IaC）、AWS Identity and Access Management（IAM）、Amazon CloudWatch 与 Amazon Bedrock）到针对分析、数据库、Amazon Elastic Compute Cloud（Amazon EC2）、网络、安全、无服务器与存储的服务专属深度工作流。

为了让这件事更简单，GA 引入了一个一等公民的 `awsSkills` 开关：无需任何管线代码、无需 URL、无需网络抓取即可开启 AWS skill 包（这些 skills 会在你需要时被带入 harness 的底层运行时）。

```
aws bedrock-agentcore-control create-harness \ 
  --harness-name myAgent \ 
  --skills '[{"awsSkills": {}}]' 

# OR scope to specific bundles with a paths glob 
aws bedrock-agentcore-control create-harness \ 
  --harness-name myAgent \ 
  --skills '[{"awsSkills": {"paths": ["core-skills/*", "specialized-skills/operations-skills/*"]}}]' 
```

## 环境与文件系统：让 agent 在它需要的环境中运行

大多数 agent 在 harness 的默认环境中就能正常运行，该环境包含 Python 与 bash。当你需要更多东西时（一个私有依赖、某个运行时版本、一个 CLI 工具，或者跨会话的持久化），有两个旋钮可以让你把 agent 的运行时塑造成与你的技术栈匹配：*容器镜像*与*文件系统*。

**容器镜像。**如果 Python 与 bash 不够用，你可以把源代码、依赖、运行时和工具打包进一个自定义容器，推送到 Amazon Elastic Container Registry（Amazon ECR），并在 `CreateHarness` 中引用它。agent 随后就会使用这个完全一致的环境。你还可以把它与 [InvokeAgentRuntimeCommand](https://docs.aws.amazon.com/bedrock-agentcore/latest/APIReference/API_InvokeAgentRuntimeCommand.html) 搭配使用——这个 API 直接在 agent 的 microVM 会话内执行 shell 命令，用于那些每次调用都不同的会话级准备工作（克隆某个特定分支、播种测试数据，或者拉取凭证）。它是确定性的，不经过模型，也不消耗 token。

**文件系统。**agent 常常需要文件比单次响应活得更久：一个共享知识库、一个跨会话的工作目录，或者一个可以把产出的文档放回你存储桶的地方。harness 为你提供三种文件系统选项，各自有不同的可达范围与持久性特征。

| **类型** | **托管** | **是否需要虚拟私有云（VPC）** | **持久性** |
| --- | --- | --- | --- |
| **托管会话存储** | 是 | 否 | 在同一个 `runtimeSessionId` 的停止/恢复周期之间保持。 |
| **Amazon Elastic File System（Amazon EFS）接入点** | 自带（BYO） | 是 | 跨所有会话，并可在多个 harness 之间共享。 |
| **Amazon Simple Storage Service（Amazon S3）Files 接入点** | 自带（BYO） | 是 | 跨所有会话与 harness，具备完整的 Amazon S3 持久性、版本控制与历史记录。 |

当工作文件需要在一次会话内熬过 microVM 重启时，选择**托管会话存储**。当多个 harness 或会话需要共享参考数据、prompt 或 skill 包时，选择 **EFS**。当你希望 agent 通过标准文件操作读写、同时改动会自动同步到后端 S3 存储桶时，选择 **S3 Files**（agent 写一份报告，报告会随之出现在你的 S3 存储桶里）。

## 统一可观测性：在一个地方看到你的 agent 做了什么

出问题时，客户希望在一个地方知道 agent 运行了什么、调用了什么、在哪里变慢、在哪里失败。一次典型的 harness 调用会横跨 runtime + memory + gateway + 一两个内置工具，而把这张图拼起来，过去意味着要打开五个标签页。

在 GA 版本中，AgentCore 控制台里的每个 harness 页面都会显示**一个统一的可观测性组件**：一行聚合信息，概括该 harness 所触及的每一个原语；此外还有按原语划分的区块，只在该 harness 配置了或使用过某个原语时才出现。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/06/18/ml-20804-image.png)

若要做更深入的分析，**CloudWatch GenAI Observability** 在 Runtime 及其他原语之外新增了一个 **Harnesses 标签页**。你可以从 harness 下钻到会话，再下钻到单条 trace，准确看到 agent 做了什么、以什么顺序、每一步耗时多久、在哪里失败。来自每个原语（memory、gateway、browser、code interpreter）的日志会内联呈现在正确的 span 上，于是你不必再在多个日志组之间跳来跳去拼凑发生了什么。

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/harness_observability_flow_with_trace.gif)

## 评估与优化：在生产中持续改进 agent

一旦 agent 进入生产，问题就从“它能用吗？”变成了“它在变好吗？”客户希望有一种方法能在真实流量上给 agent 的实际表现打分、获得该改什么的建议，并在铺开之前验证这些改动。GA 带来两个组件来闭合这个回路：

- **[AgentCore Evaluations](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations.html)** 用内置的以大语言模型（LLM）作为裁判的评估器（有用性、忠实性、安全性），或者用你自己编写的自定义评估器给 harness trace 打分。你可以在线运行（每个会话发生时即打分）、针对单条 trace 按需运行、对历史 trace 批量运行、针对固定测试数据集运行，或者以合成用户模拟的形式运行，在上线前做压力测试。
- **[AgentCore optimization](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/optimization.html)** 会读取这些评估器分数并生成 **prompt 与工具描述的改进建议**，然后通过 AgentCore Gateway 在实时流量中于两个变体之间分流来验证它们，并对每个会话做在线评估打分、报告统计显著性。变体可以是同一 runtime 上一个可选的**配置包**的不同版本，也可以是指向不同端点的不同版本，因此你只需指向另一个端点，就能 A/B 测试 prompt 与工具描述的改动，而不必重新部署代码。

运行你的 harness，捕获 trace，拿到分数，拿到建议，把推荐的配置与当前配置做 A/B 测试，然后发布胜出的那个。

## 版本与回滚：安全地铺开改动，瞬间回滚

客户希望更新 prompt、替换一个工具，或者在一部分流量上试用新模型，而不把整个 agent 置于风险之中。harness 上的版本管理与端点复刻了 AgentCore Runtime 已经提供的能力：每次 `UpdateHarness` 都会创建一个**不可变版本**，捕获完整配置（模型、system prompt、工具、memory 配置、skills、环境、截断、执行限制），而回滚就是“把端点指向一个更早的版本”。

```
# Create PROD pinned to V2 

aws bedrock-agentcore-control create-harness-endpoint \ 
  --harness-id my-harness-xxx --endpoint-name PROD --harness-version 2 

# Promote V5 to PROD (or roll back to V4) 
aws bedrock-agentcore-control update-harness-endpoint \ 
  --harness-id my-harness-xxx --endpoint-name PROD --harness-version 5 
```

`DEFAULT` 端点会在每次更新时自动前进。具名端点（`PROD`、`STAGING`）会保持固定，直到你显式提升。

## 导出为代码：当配置不够用时毕业

当一个用例超出了配置能承载的范围（自定义编排、多 agent 协同、深度埋点），客户希望把 agent 推进得更远，而不必从零重建。一条 CLI 命令就能把 harness 导出为基于 Strands 的代码，它可以托管在 AgentCore Runtime 上，也可以托管在任何其他地方：

```
agentcore export harness --name myHarness-6dk4df --output ./my-agent 
```

导出的项目会保留你的模型、prompt、工具、memory 接线、skills 与容器环境。相同的计算路径、相同的可观测性、相同的身份原语。**这次毕业是一次从配置到代码的翻译，而不是一次架构切换。**

Strands 是第一个导出目标；Claude Agent SDK 即将支持，因此偏好那个框架的客户可以用同样的方式毕业。

这是我们最在意的 harness 故事的一部分。当配置不再够用，你会毕业到相同的计算与相同的原语上，拿到你可以阅读和修改的代码，而不是从头再来一遍。

## 其他值得注意的新增内容

我们还新增了以下内容：

**Step Functions 集成。**一次 harness 调用现在在 [AWS Step Functions](https://docs.aws.amazon.com/step-functions/latest/dg/connect-bedrockagentcore.html) 中是一个一等公民状态。在 Workflow Studio 中搜索 **AgentCore InvokeHarness** 并把它拖进你的工作流。使用 **Quick Create Harness** 在 Step Functions 内部脚手架式地新建一个 harness 与执行角色，或者指向一个已有的 harness 并按调用覆盖。InvokeHarness 的语义保持一致：默认值在 harness 上，覆盖值在 Task 状态上。

**AgentCore 上的 Web Search。**新增的 [Web Search on AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-target-connector-web-search-tool.html)（同样在纽约峰会上发布）可通过 AgentCore Gateway 提供给 harness agent：把 Web Search 暴露为一个 Gateway target，从 harness 引用该 Gateway，agent 就具备了搜索能力。一个一方的 `agentcore_web_search` 工具类型即将推出，与 `agentcore_browser` 和 `agentcore_code_interpreter` 的单行模式一致。

## 用这一切你能做什么

harness 能支持数不清的用例，跨越各行各业与各种 agent 类型。为了让你感受这种多样性，这里有三个具体示例，每一个都是团队告诉我们他们过去要手工拼凑起来的东西。

**一个研究与写作 agent。**该 agent 可以搜索网页、浏览来源、起草文档，并把一个真实的 xlsx 或 pptx 文件交还给你，memory 会跨会话延续，这样下一个问题不必重放所有内容。把它立起来的最低要求是一次 `CreateHarness` 调用：

- `tools`：`agentcore_browser`，外加一个暴露 Web Search on AgentCore 的 Gateway target。
- `skills`：一个指向 `anthropics/skills` 的 `git` 来源，用于 document-skills 包。

Memory 默认开启，因此你无需显式配置它。就这样。

**一个为你团队服务的 AWS 数据与分析 agent。**该 agent 可以从你的 AWS 账户拉取数据（Amazon Athena、AWS Glue、Amazon S3、Amazon Redshift、Amazon CloudWatch），执行分析，并交回一份摘要、一张图表或一个发现，同时按 AWS 推荐的流程一步一步地访问每项服务，而不是即兴发挥。把它立起来的最低要求是一次 `CreateHarness` 调用：

- `skills`：`[{"awsSkills": {}}]`，开启精选的 AWS 目录（分析、数据库、Amazon EC2、网络、安全、无服务器与存储）。
- `executionRoleArn`：一个 IAM 角色，其作用域限定为你希望 agent 读取的那些 AWS API。

如果你还想让 agent 在沙箱中运行 Python 来切分并可视化它拉取的数据，就再加上 `agentcore_code_interpreter`。

**一个编码 agent。**该 agent 可以读取你的代码库、规划一项改动、把它写出来、运行测试，并开一个 pull request（PR），同时具备在会话中途为设计与实现切换到另一个模型而不丢失上下文的能力。把它立起来的最低要求是两步：

- 把一个包含你仓库与工具链的自定义容器推送到 Amazon ECR。
- 调用 `CreateHarness`，用 `environmentArtifact` 指向那个镜像，并加一个接好 GitHub（或你内部的 GitLab / Bitbucket 等价物）的 Gateway target，让 agent 能与分支、PR 和评审交互。

对于 clone、commit、push、open a PR 这类确定性的 git 操作（不必付钱让模型去思考它们），直接调用 `InvokeAgentRuntimeCommand`。

这是三个不同的 agent，用的是完全相同的 harness。唯一变化的东西就是 API 配置。

## 只为使用量付费

不额外收取 harness 费用。你按实际消耗为底层能力付费。

- **Runtime 计算**（harness 会话运行的地方）：按秒计的活跃消耗定价，每 vCPU-小时 $0.0895，每 GB-小时 $0.00945。agent 类工作负载会花大量时间等待模型与工具的 I/O。Runtime 只在 CPU 真正被消耗时计费。
- **Browser** 与 **Code Interpreter**：相同的活跃消耗模型。
- **Gateway**：按每 1,000 次调用与每 1,000 次搜索查询计费。
- **Memory**：按每 1,000 个短期事件、每月每 1,000 条长期记录、每 1,000 次检索计费。
- **可观测性**：span、日志与指标按 Amazon CloudWatch 的标准定价计费。
- **模型推理**：由 Amazon Bedrock 或第三方供应商按其标准费率收费。

每一项都是独立的。用一项，或用全部。一个运行 60 秒并调用两个工具的 agent 就按这个计费。一个运行一小时、计算密集的 agent 也按这个计费。**你支付多少，与你的 agent 实际计算多少成正比。**

完整的定价细节，请参阅 [AgentCore 定价页面](https://aws.amazon.com/bedrock/agentcore/pricing/)。

## 我们的一些客户对 harness 感到兴奋的地方

**Omar Paul，Twilio 产品副总裁**表示：*“Twilio 的客户正在构建跨语音、消息与数字渠道工作的 AI agent——借助实时智能与持久记忆，让每一次交互都像一场对话。通过把 AgentCore harness 与 Twilio Conversations 结合，开发者可以从想法走到上线 agent，而无需重新改造基础设施。最好的客户体验，发生在优秀的 AI 与优秀的通信基础设施一起构建的时候。”*

**Dr. Lukas Schack，TUI GROUP 首席机器学习工程师**告诉我们：*“Amazon Bedrock AgentCore 已经成为 TUI 的核心构建块：我们用 Runtime 跨框架托管 agent，用 Memory 在它们之间共享上下文，既在生产环境，也在有 500 多名员工参与的研讨会上，有时有超过 130 人同时构建。有了 AgentCore harness，过去从想法到可用产品需要数周，现在只需几分钟，面向客户的用例是下一步。”*

**Rodrigo Moreira，VTEX 工程副总裁**说：*“我们正在构建将彻底改变电子商务的 AI agent。**以前，给每个新 agent 做原型都需要数天的编排代码与基础设施搭建，才能验证一个想法。AgentCore harness 改变了这一点：替换模型、添加工具、更换 skill，或者改进 agent 的指令，现在都是一次配置变更，而不是一次重建。**我们现在可以在几分钟内而不是几天内验证 agent 的想法，并且期待用这些新能力进一步加速 agent 开发。”*

**Kazumi Matsuda，FUJISOFT AI 推进部高级经理**指出：*“在 FUJISOFT，我们正在构建 AI agent，以加速各团队的软件开发与运维。我们的框架 Character Capsule 把 agent 角色、skills 与执行流程打包成可复用的胶囊，可扩展到 AgentCore 上的多 agent 编排。借助 AgentCore harness，我们能在几分钟内部署新 agent，并为每次改动做版本管理。进入生产后，Evaluations 用执行日志给我们的 agent 表现打分，AgentCore 的优化能力会基于这些分数生成 prompt 与工具建议。我们在铺开之前会在实时流量上对这些建议做 A/B 测试，因此改进是连续的，而不是靠猜。这些能力合在一起，让我们能快速立起新 agent，并有信心持续改进它们，在质量回归到达生产之前就抓住它，只铺开我们已经在多 agent 模式中验证过的改动。”*

## 开始使用

Amazon Bedrock AgentCore harness 今天已在 [AgentCore 正式可用的所有 AWS 区域](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-regions.html) 提供。

```
# CLI (fastest path) 

npm install -g @aws/agentcore@preview 
agentcore create --name myresearchagent --model-provider bedrock 
agentcore deploy 
agentcore invoke "Plan a 5-day Tokyo itinerary with daily budgets and reservation links." 
```

```
# SDK 

import boto3, uuid 
control = boto3.client("bedrock-agentcore-control", region_name="us-west-2") 
data    = boto3.client("bedrock-agentcore",         region_name="us-west-2") 

# 1. Define 
harness = control.create_harness( 
    harnessName="MyAgent", 
    executionRoleArn="arn:aws:iam::123456789012:role/MyAgentRole" 
) 

# 2. Invoke 
session_id = str(uuid.uuid4()).ljust(33, "0")  # must be at least 33 chars 
response = data.invoke_harness( 
    harnessArn=harness["harnessArn"], 
    runtimeSessionId=session_id, 
    messages=[{"role": "user", 
               "content": [{"text": "Plan a 5-day Tokyo itinerary."}]}] 
) 

for event in response["stream"]: 
    print(event)
```

一个团队从想法走到可用 agent 的速度越快，他们负担得起测试的想法就越多。harness 把这个回路从数天压缩到数分钟。我们很期待看到你构建的东西。

### 更多资源

更多信息，请参阅以下内容：

- [开始使用](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-get-started.html)
- [GitHub 示例](https://github.com/awslabs/agentcore-samples/tree/main/01-features/01-harness)
- 文档  [AgentCore harness 概览](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness.html) [模型与指令](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-models.html) [Skills](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-skills.html) [Memory](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-memory.html) [环境与文件系统](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-environment.html) [可观测性与成本控制](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-operations.html) [版本管理与端点](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-versioning.html) [导出为代码](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-export.html) [安全与访问控制](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-security.html) [Harness 与 Runtime 的对比](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-vs-runtime.html) [CreateHarness API](https://docs.aws.amazon.com/bedrock-agentcore-control/latest/APIReference/API_CreateHarness.html) – [InvokeHarness API](https://docs.aws.amazon.com/bedrock-agentcore/latest/APIReference/API_InvokeHarness.html)

## 关于作者
