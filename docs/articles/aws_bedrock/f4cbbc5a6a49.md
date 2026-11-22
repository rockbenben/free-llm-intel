---
vendor: aws_bedrock
title: 多智能体系统的 5 个生产挑战，以及 Deep Insight 如何解决它们
original_title: 5 production challenges in multi-agent systems and how Deep Insight solved them
url: https://aws.amazon.com/blogs/machine-learning/5-production-challenges-in-multi-agent-systems-and-how-deep-insight-solved-them
date: 2026-10-21
lang: zh
captured: 2026-10-24
extractor: readability-v1
translator: agent
status: translated
body_sha: b69c21448b38
---

## [Artificial Intelligence](https://aws.amazon.com/blogs/machine-learning/)

# 多智能体系统的 5 个生产挑战，以及 Deep Insight 如何解决它们

构建一个多智能体系统如今已经相当直接。真正的挑战始于把它投入生产。得益于开源框架和云服务，你可以在几天内搭好一个智能体。几次工具调用、几行提示词，你就有了看起来令人印象深刻的东西。但一旦团队试图走出试点、进入真实业务应用，就会撞上一堵熟悉的墙。如果你曾经尝试把智能体投入生产，这些挫败感听起来会很熟悉：

*为什么智能体不遵循我们的业务逻辑、跳过校验步骤，或者捕捉不到边界情况？*

你调整提示词、添加更多示例、更换模型。同样的问题反复出现。这是因为智能体并不会遵照固定的指令序列行事。它们根据上下文自行做出判断。仅有指令是不够的。你需要设计智能体如何思考、何时验证，以及出错时该怎么做。这正是为什么仅仅做提示词工程已经不够，必须设计智能体的整个认知架构与执行流程。

为了正面应对这些挑战，AWS Solutions Architecture 团队构建了 [Deep Insight](https://github.com/aws-samples/sample-deep-insight)，一个生产级的多智能体系统。在本系列博文中，我们将分三篇分享团队在构建 Deep Insight 过程中的第一手经验。我们会讲解如何把 Anthropic 提出的 Context Engineering 技巧（多智能体架构、结构化笔记、人在环中等等）应用到真实生产环境中。我们还会介绍过程中遇到的权衡（附代码），以及将这个智能体部署并运行在 AWS 上所获得的运维洞察。

## 博文系列概览

- 第 1 部分：多智能体系统的 5 个生产挑战，以及 Deep Insight 如何解决它们。
- 第 2 部分：超越上下文窗口：Context Engineering 技巧以及 Deep Insight 如何应用它们。
- 第 3 部分：实践中的 harness 工程：把 Deep Insight 从开发环境推进到生产环境。

这是三篇系列中的第 1 部分。它定义了任何生产级多智能体系统都必须解决的五个核心挑战，并展示技术栈的每一层如何应对它们——从 [Strands Agents SDK](https://strandsagents.com/) 和 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 到 [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/)、[Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/create-application-load-balancer.html) 和 [AWS Fargate](https://aws.amazon.com/fargate/)。第 2、3 部分将讲解 Context Engineering 与生产部署。

## Deep Insight 简介

Deep Insight 是一个多智能体系统，把复杂的数据分析转化为自动化洞察。给定一个 CSV 文件和一段自然语言提示词，一组分层的专职智能体（Coordinator、Planner、Supervisor、Coder、Validator、Reporter 和 Tracker）会协作完成分析。它们一起加载数据、运行分析、生成图表、校验计算，并产出一份带引用的专业报告（.docx）。

我们稍后会详细探讨架构。先看看它的实际运行。在演示中，我们喂入一家虚构食品公司 Yummy Food 的广告数据（`yummy-food-market.csv`）以及一个列定义文件（`column_definitions.json`），并提供这样一段提示词：*从销售与营销的角度分析这份数据，生成图表和洞察，并产出一份 .docx 报告。* Deep Insight 会生成分析计划，呈交给用户批准，一旦获批就执行分析。

|  | **内容** |
| --- | --- |
| 输入 | CSV 数据文件（`yummy-food-market.csv`）+ 列定义文件（`column_definitions.json`） |
| 示例提示词 | “从销售与营销的角度分析这份数据，生成图表和洞察，并产出一份 .docx 报告。” |
| 输出 | DOCX 报告（两个版本，一份带引用、一份不带引用）以及图表图片（PNG） |

接下来的 [Deep Insight Web 演示视频](https://www.youtube.com/watch?v=tMN29C4nam0)展示了完整工作流，从上传数据和审阅分析计划，到实时流式输出并下载完成的报告。

## 我如何试用？

Deep Insight 已在 [GitHub](https://github.com/aws-samples/sample-deep-insight) 上开源，配有完整的安装指南，并提供三种覆盖从开发到生产的部署选项。

第一种是[自托管版本](https://github.com/aws-samples/sample-deep-insight/tree/main/self-hosted)，通过 CLI 在本地运行。它针对快速迭代做了优化，可以完整访问每个智能体、提示词和工作流的代码。大约 10 分钟即可完成安装，因此很适合开发阶段。（自托管版本的演示视频见 [YouTube](https://www.youtube.com/watch?v=pnyvBo98E1k)。）

第二种是 [Web 版本](https://github.com/aws-samples/sample-deep-insight/tree/main/deep-insight-web)，一个基于浏览器的界面，用于上传数据、审阅分析计划（Human-in-the-Loop，即 HITL）和下载报告，全程无需写代码，因此非开发人员也能使用。（前面的演示视频展示的就是 Web 版本的实际运行。）

第三种是 [Managed AgentCore 版本](https://github.com/aws-samples/sample-deep-insight/tree/main/managed-agentcore)，一个由 Amazon Bedrock AgentCore 驱动的生产部署选项，后者是一个可用任意框架或模型大规模构建、连接和优化智能体的平台。该版本把智能体部署在 AgentCore runtime 上，这是 Amazon Bedrock AgentCore 的一项能力。系统完全运行在私有虚拟私有云（VPC）中，自定义 Code Interpreter 单独托管在 AWS Fargate 上，智能体在按用户隔离的环境中并发运行。当你需要会话隔离和私有 VPC 部署时，这是正确的选择。第 3 部分会详细介绍它的部署与运维。

三者共享同一套多智能体架构，因此在开发阶段验证过的智能体可以原样部署到生产环境。

## 方案概览

构建生产级多智能体系统，光有好提示词远远不够。你需要正确的技术栈和基础设施，来解决智能体如何协作、如何推理、如何部署、在哪里安全地执行代码，以及如何监控运行状况。Deep Insight 在以下五个关键领域解决问题。由于智能体既生成代码又生成报告内容，我们还会在方案细节 2 中介绍生产环境的负责任 AI 控制措施。

| **挑战** | **技术** | **做法** |
| --- | --- | --- |
| “我们如何控制多个智能体之间的执行流程？” | Strands Agents SDK | 使用 Strands 的 Graph 模式定义智能体之间的执行顺序，并实现人在环中的分支。使用 Strands 的 Agents as Tools 模式，让 Supervisor 按需把专职智能体（Coder、Validator、Reporter、Tracker）当作工具调用。 |
| “每个智能体应该用哪个大语言模型（LLM）？” | Amazon Bedrock | 为每个角色选择合适的 Claude 模型：Haiku 用于基础路由，Opus 用于规划，Sonnet 用于执行。 |
| “我们如何可靠地在生产环境运维一个已完成的智能体？” | Amazon Bedrock AgentCore | 带监控、会话隔离和私有 VPC 部署的托管运行时。 |
| “我们如何缓解执行 AI 生成代码带来的安全问题？” | AWS Fargate + Application Load Balancer (ALB) | 通过自定义 Code Interpreter，在按会话的临时沙箱容器中隔离执行代码。 |
| “我们如何监控和管理这个系统？” | Amazon DynamoDB + Amazon Simple Notification Service (Amazon SNS) + Amazon Cognito | 管理仪表盘和故障告警系统。 |

下面的架构图（图 1）一目了然地展示了这一点。绿色方框代表 Strands Agents 的多智能体结构，它应对上表中的挑战 1 和 2。我们将在后面的方案细节 1：多智能体系统设计一节中详细讲解。图中其余的基础设施组件应对挑战 3、4 和 5，我们将在方案细节 2：生产部署与运维中逐一介绍。

![Deep Insight architecture: the Strands Agents multi-agent layer on Amazon Bedrock AgentCore, with an Application Load Balancer routing code execution to AWS Fargate containers in a private VPC](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21081-1-1.png)

图 1：方案架构

## 方案细节 1：多智能体系统设计

Deep Insight 采用多智能体架构，八个智能体协作产出单一的高质量交付物。每个智能体在自己的独立上下文中工作，只执行自己的专项任务，并且只把压缩后的结果往下传递。

![Hierarchical multi-agent structure where the Coordinator and Planner feed the Supervisor, which orchestrates the Coder, Validator, Reporter, and Tracker agents](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21081-2-1.png)

图 2：多智能体结构

Coordinator 负责路由用户请求，Planner 把任务拆解成离散步骤，Plan Reviewer 收集用户反馈，Supervisor 按照计划调用相应的专职智能体。Coder 编写并执行数据分析代码，Validator 校验计算，Reporter 生成最终报告，Tracker 跟踪进度。我们分三层来说明：

- 【第 1 层】Coordinator → Planner → Plan Reviewer：请求分析并创建执行计划。
- 【第 2 层】Supervisor：专职智能体的编排。
- 【第 3 层】Coder、Validator、Reporter、Tracker：专项任务的执行。

来自 Strands Agents SDK 的两个关键模式被结合起来，用于控制这些智能体之间的执行流程。首先，[Graph 模式](https://strandsagents.com/docs/user-guide/concepts/multi-agent/graph/)把智能体的执行顺序和流程定义为一张有向图。请求依次流经 Coordinator、Planner、Plan Reviewer，然后是 Supervisor，并带有一条在收到修改请求时回到 Planner 的条件分支。通过条件决定下一步，使 HITL 和错误处理这类复杂工作流变得直接了当。其次，[Agents-as-Tools 模式](https://strandsagents.com/docs/user-guide/concepts/multi-agent/agents-as-tools/)让 Supervisor 仅在需要时把专职智能体（Coder、Validator、Reporter、Tracker）当作工具调用。每个智能体在独立上下文中工作、只返回结果，从而在保留领域专业能力的同时把上下文用量降到最低。

本节展示该架构如何解决路由、规划和编排。

### 【第 1 层】Coordinator → Planner → Plan Reviewer

这一层把用户请求转化为一份获批的执行计划。

#### 1.1 Coordinator（路由）：并非每个请求都需要昂贵的编排

Coordinator 是用户请求的入口。它直接处理基本的问候语，并通过 `handoff_to_planner` 标记把数据分析这类复杂任务交给 Planner。

关键的设计决策是模型选择：由于 Coordinator 只做分类，它使用轻量的 Claude Haiku，避免在基本问候上付 Opus 级别的成本，同时提供快速响应。

```
# builder.py: conditional edges for routing decisions
builder.set_entry_point("coordinator")
builder.add_edge("coordinator", "planner", condition=should_handoff_to_planner)
```

路由条件来自 Coordinator 的提示词：任何需要工具、推理或多步思考的请求都交给 Planner。

#### 1.2 Planner（创建计划）：复杂分析需要先分解再执行

在 Deep Insight 的多智能体结构中，Planner 智能体承担着把任务分配到各智能体的关键角色。在实质性工作开始之前，它把大任务拆成更小的步骤，各专职智能体一次执行一个，使每个智能体的上下文保持精简。

Planner 使用开启 Extended Thinking 的 Claude Opus 模型来制定分析计划。它把计划组织成 `[ ]` 清单格式，指明分配给每个智能体的具体任务，并存储在 `full_plan` 变量中。它把请求拆成 5–10 个清晰步骤，如下例所示：

```
## title
Yummy Food Consumer Purchase Patterns and Advertising Effectiveness Analysis Report

## steps

### 1. Coder: Comprehensive Data Analysis and Insight Generation
- [ ] Load all data files from './data/*' path and understand structure
- [ ] Analyze consumer purchase history (patterns, preferences, customer segments)
- [ ] Analyze advertising data by channel (cost, effectiveness, channel comparison)
- [ ] Category-level analysis (fresh food, convenience food, health food ad effectiveness)
- [ ] Calculate key business metrics (conversion rate, CPA, ROAS, etc.)
- [ ] Generate visualizations (5+ charts, consumer segment charts)
- [ ] Derive strategic marketing insights
- [ ] Generate calculation metadata (for validation)

### 2. Validator: Calculation Verification and Citation Metadata Generation
- [ ] Identify verification targets and extract filter calculations
- [ ] Load data files directly and perform recalculations
- [ ] Verify accuracy of per-channel performance metrics
- [ ] Validate data consistency of visuals and graphs
- [ ] Generate citation metadata (reference numbers for verified items)

### 3. Reporter: Marketing Analysis Report Generation
- [ ] Write report overview
- [ ] Create structured report using verified analysis results
- [ ] Insert visualizations and analysis sections
- [ ] Present marketing strategy recommendations and improvement proposals
- [ ] Generate professional marketing report in DOCX format
```

#### 1.3 Plan Reviewer

Plan Reviewer 是一个 HITL 节点，把计划呈现给用户并收集*批准或修改反馈*。如果有反馈，它会回到 Planner 修改计划。如果获批，它就把任务交给 Supervisor。设置了最大修改次数（`MAX_PLAN_REVISIONS`）以防止无限循环。

```
# builder.py: Plan Reviewer's bidirectional conditional edges
builder.add_edge("plan_reviewer", "planner", condition=should_revise_plan)
builder.add_edge("plan_reviewer", "supervisor", condition=should_proceed_to_supervisor)
builder.set_max_node_executions(25)
```

在 Web 版本中，Plan Reviewer 会显示一个浏览器弹窗，用户在其中阅读计划并批准它或输入修改反馈。如果 300 秒内没有响应，倒计时结束后会自动批准计划。

![Deep Insight web UI showing the Plan Reviewer modal where the user approves or revises the generated analysis plan](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21081-3-1.png)

图 3：Web UI 中 Plan Reviewer 智能体的执行

如果不做规划，智能体就在运行时决定一切，一次中途纠偏会让之前的工作作废，而用户对进度毫无可见性。有了 Planner 和 Plan Reviewer，用户可以审阅并修改计划、实时监控进度，并且只重新执行失败的那一步。

### 【第 2 层】Supervisor（编排器）：专职智能体需要一位指挥

Supervisor 按顺序执行 Planner 的 `full_plan`，通过 Tool Use 调用注册在它上面的第 3 层智能体（Coder、Validator、Reporter、Tracker）工具。

```
# nodes.py: registering sub-agents as tools on the Supervisor
agent = strands_utils.get_agent(
    agent_name="supervisor",
    system_prompts=apply_prompt_template(prompt_name="supervisor", prompt_context={}),
    model_id=os.getenv("SUPERVISOR_MODEL_ID", os.getenv("DEFAULT_MODEL_ID")),
    prompt_cache_info=(True, "default"),
    tool_cache=True,
    tools=[coder_agent_tool, reporter_agent_tool, tracker_agent_tool, validator_agent_tool],
    streaming=True,
)
```

Supervisor 的系统提示词定义了严格的工作流规则：

- 强制执行顺序：Coder、Tracker、Validator、Tracker、Reporter、Tracker：每个智能体运行后都会调用 Tracker 跟踪进度，让 Supervisor 管理整体任务状态。
- 小节完成规则：在当前智能体的所有清单项被标记为 [x] 之前，Supervisor 不会进入下一个智能体。
- 上下文保留：Supervisor 把 clues 和 full_plan 变量传给每个工具智能体，保持完整上下文并防止信息丢失。

### 【第 3 层】Coder、Validator、Reporter、Tracker：分工决定质量

每个第 3 层智能体（Coder、Validator、Reporter、Tracker）都被封装为一个 `PythonAgentTool`，接收来自 Supervisor 的 Tool Use 调用。每个都在 Strands SDK 中创建为独立的 `Agent()` 实例，拥有自己的系统提示词、模型 ID 和工具集。

| **智能体** | **角色** | **工具** | **关键输出** |
| --- | --- | --- | --- |
| Coder | 数据分析、图表生成、洞察推导 | write_and_execute_tool, bash_tool, file_read, skill_tool | *.png 图表、`calculation_metadata.json` |
| Validator | 数值计算复验、引用生成 | write_and_execute_tool, bash_tool, file_read | `citations.json`、validation_report.txt |
| Reporter | DOCX 报告生成 | write_and_execute_tool, bash_tool, file_read | final_report.docx、final_report_with_citations.docx |
| Tracker | 清单进度状态更新 | 无（仅 LLM 推理） | 更新后的 full_plan |

Supervisor 依据 Planner 的清单，按以下顺序发起 Tool Use 调用：

- Coder —— 加载数据、编写并运行分析代码、生成 PNG 图表、把结果累积到 all_results.txt，并留下 `calculation_metadata.json` 供校验。
- Tracker（第 1 轮）—— 把已完成的清单项从 [ ] 更新为 [x]，Supervisor 据此判断是否继续。
- Validator —— 从源数据重新执行 `calculation_metadata.json` 中的每一项计算。误差在 0.01 以内的判为通过，不匹配的会被标记。通过校验的计算写入 `citations.json`，供 Reporter 引用。
- Tracker（第 2 轮）—— 在清单中反映 Validator 的完成状态。
- Reporter —— 读取 all_results.txt 和 `citations.json`，生成两个版本的最终 DOCX 报告，一份带引用、一份不带引用。
- Tracker（第 3 轮）—— 反映所有任务的最终完成状态。

Tracker 在每个智能体之后运行，这样 Supervisor 就能跟踪进度并强制执行完成规则（在全部条目变为 [x] 之前不往下走）。由于它仅靠 LLM 推理更新清单、不使用工具，因此带来的开销很小。

### 每个智能体的 LLM 模型配置

Deep Insight 为每个智能体的角色量身定制模型和设置。这不是模型选型，而是一项优化成本与质量的架构决策。

| **智能体** | **模型** | **Extended Thinking** | **Prompt Caching** | **角色** |
| --- | --- | --- | --- | --- |
| Coordinator | Haiku | 禁用 | 否 | 快速路由：成本最小化 |
| Planner | Opus | 启用（约 8,192 个 token） | 否 | 深度思考：高质量规划 |
| Supervisor | Sonnet | 禁用 | 是 | 执行编排：用缓存节省成本 |
| Coder | Sonnet | 禁用 | 是 | 代码生成/执行：缓存对重复调用有效 |
| Validator | Sonnet | 禁用 | 否 | 数值校验：每次数据不同，缓存无用 |
| Reporter | Sonnet | 禁用 | 是 | 报告生成：缓存对长提示词有效 |
| Tracker | Sonnet | 禁用 | 否 | 状态更新：轻量任务，缓存无用 |

Supervisor、Coder 和 Reporter 智能体使用 Prompt Caching 缓存它们的系统提示词和工具定义，在重复调用时把输入 token 成本最多降低 90%。Coordinator 只运行一次，Validator 和 Tracker 每次运行时的上下文都不同，因此缓存对它们无效，保持禁用。这种有选择性的缓存策略是一个深思熟虑的成本/性能权衡。

## 方案细节 2：生产部署与运维

如果说方案细节 1 定义的是*系统做什么*，那么本节定义的是它在哪里、如何安全运行。从这里开始，内容全部是生产运维的基础设施决策。具体来说，本节涵盖 LLM 生成代码的安全执行环境，以及团队的运维可见性。

### 1. 代码执行：LLM 生成的代码需要安全的执行环境

Coder 智能体编写并运行 Python 来做数据分析。在自托管版本中，它通过 `subprocess.run()` 在本地运行；但在生产环境（AgentCore）中，安全和隔离至关重要。直接在生产服务器上运行 LLM 生成的代码风险极高：模型可能删除系统文件、在死循环中耗尽资源，或者触及其他用户的分析数据。Deep Insight 用 AWS Fargate 上按会话的临时容器加上 ALB 来解决这个问题。这些组件并不是孤立运行的。如图 1 所示，AgentCore runtime、ALB 和 Fargate 任务都运行在同一个私有 VPC 内。VPC 端点把它们连接到 Amazon Simple Storage Service (Amazon S3)、Amazon Bedrock 和 Amazon Elastic Container Registry (Amazon ECR)，无需经过公共互联网。安全组限制哪些组件可以访问 Code Interpreter 容器。AWS Identity and Access Management (IAM) 角色把每个组件的作用范围限定在它所需的 AWS 资源上。Amazon CloudWatch 收集来自 AgentCore Observability（Amazon Bedrock AgentCore 的一项能力）的容器日志和可观测性数据。

- 自定义容器 Docker 镜像：一个预先优化好的沙箱，带有多智能体系统所需的字体、系统库和 Python 包。
- 容器隔离：每个分析会话都会在私有 VPC 子网中分到一个独立的 Fargate 容器，无法直接访问互联网。
- 两步执行：LLM 生成的代码先做 base64 编码，通过 HTTP 发送，写入文件（第 1 步），然后通过 subprocess 执行（第 2 步）。
- 会话亲和性：即使智能体多次执行代码，ALB 的粘性会话 cookie 也会把它路由回同一个容器。
- 产物管理：分析完成时，图表、报告和日志上传到 Amazon S3。容器在一小时后自动终止。

容器隔离保护了基础设施，但它并不约束智能体生成的内容。Validator 智能体会复验计算，但它检测不出上传数据中隐藏的提示注入指令，也不会筛查 LLM 生成的文本是否含有有害或无依据的内容。对于生产部署，我们建议增加 Amazon Bedrock Guardrails 作为负责任 AI 控制：对用户提示词和上传数据应用内容过滤和提示攻击检测，并对智能体输出应用上下文 grounding 检查，使报告文本始终有源数据和已校验计算作为依据。

### 2. 运维与监控：团队需要可见性

一个生产系统光有代码并不完整。团队必须评估系统健康状况、诊断问题并审阅结果，因此 Deep Insight 提供了 Web UI 和一个 Ops 仪表盘。

#### Web UI（deep-insight-web）

一个基于 FastAPI 的 Web 界面，通过 AgentCore Native Protocol（`boto3.invoke_agent_runtime()`）与后端通信。用户上传数据并输入提示词，然后通过 Server-Sent Events (SSE) 流式输出监控进度。计划生成后，弹窗让用户批准或给出修改反馈（HITL）。完成的报告可以直接下载。同时支持韩语和英语。

![Deep Insight web interface for uploading data, entering a prompt, and downloading the generated report](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21081-4-1.png)

图 4：Deep Insight Web 版本截图

#### Ops 仪表盘（deep-insight-web/ops）

Ops 仪表盘是可选的。没有它 Deep Insight 也能正常工作，但它为需要的团队增加了这些功能：

- 任务跟踪：所有分析任务的指标，包括状态、token 用量和耗时，都记录在 Amazon DynamoDB 中。
- 故障告警：分析失败时，立即通过 Amazon SNS 向管理员发送电子邮件。
- 管理仪表盘：一个专用的管理仪表盘，通过 Amazon Cognito 的 JSON Web Token (JWT) 认证保护，用于安全的任务监控。

![Deep Insight Ops dashboard listing analysis tasks with status, token usage, and elapsed time](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21081-5-1.png)

图 5：Deep Insight Ops 仪表盘截图

![Deep Insight Ops dashboard detail view showing metrics for a single analysis task](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/19/ml-21081-6.png)

图 6：Deep Insight Ops 仪表盘详情视图

## 扩展 Deep Insight 架构

Deep Insight 的多智能体架构并不局限于数据分析报告生成这一个领域。下面两个例子表明，这种分层编排的设计原则在完全不同的领域依然有效。

### 案例 1：LG Electronics：由 Agentic AI 驱动的营销洞察提取系统

LG Electronics 韩国销售事业部基于与 Deep Insight 相同的多智能体架构构建了 ChatInsight，在那之前，数据分析请求需要 2–3 周，而且营销人员和数据科学家之间的意图会走样。Coordinator 按复杂度路由，Planner 跟踪任务，Supervisor 编排 Coder 和 Reporter，智能体之间的状态通过 all_results.txt 文件累积传递。原本需要 3 天的分析现在只需 30 分钟，生产力提升 288 倍。不懂 SQL 的营销人员也可以让智能体探索数据并提出策略（参见 [AWS Tech Blog 上的 LG Electronics Agentic AI Insight Extraction System](https://aws.amazon.com/ko/blogs/tech/lge-agentic-report-automation/)）。

![LG Electronics ChatInsight architecture using the same Coordinator, Planner, Supervisor, Coder, and Reporter multi-agent pattern as Deep Insight](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21081-7-1.png)

图 7：LG Electronics Agentic AI 营销洞察系统架构

### 案例 2：TechRecon：AI 驱动的技术侦察智能体（re:Invent 2025）

TechRecon 在 AWS re:Invent 2025 上做了展示（session SNR203），把 Deep Insight 的架构应用于技术战略。给定一家公司和所属行业，Researcher 收集技术趋势，Coder 进行分析，Validator 进行校验，Reporter 产出 Landscape Analysis 和 Technical Position Paper。该架构与 Deep Insight 几乎完全相同，使用 Strands Agents SDK 的 Graph 模式、Extended Thinking 和 Prompt Caching 构建，只是由 Researcher 取代 Coder 成为主要的执行智能体。这表明该设计是一个通用模式：替换智能体的角色和提示词，同样的编排结构就能解决完全不同的问题。

![TechRecon output showing a Landscape Analysis and a Technical Position Paper produced by the reconnaissance agent](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21081-8-1.png)

图 8：TechRecon 的成果

（延伸阅读：[TechRecon GitHub](https://github.com/aws-samples/sample-tech-recon) | [AWS re:Invent 会议视频](https://www.youtube.com/watch?v=NwkH_F3yUiY)）

## 结论

构建一个能在生产环境运行的智能体，不是模型能力的问题，而是架构的问题。Deep Insight 提供了一个经过验证的答案：

- 工作流管理：Strands Agents SDK 的 Graph 模式定义智能体之间的执行顺序并实现 HITL 分支，而 Agents-as-Tools 模式让 Supervisor 仅在需要时调用专职智能体。
- 推理引擎：我们按角色从 Amazon Bedrock 分配 Claude 模型（先是 Haiku，再是 Opus，然后是 Sonnet），以优化成本与质量。
- 部署：Amazon Bedrock AgentCore 提供带会话隔离、私有 VPC 部署和 OpenTelemetry 可观测性的托管运行时。
- 代码执行：Application Load Balancer 加上 Fargate 上的 Amazon Elastic Container Service (Amazon ECS)，把 LLM 生成的代码执行隔离在按会话的临时沙箱容器中，防止访问系统文件、资源耗尽和意外数据泄露等安全问题。
- 运维：Web UI 的 SSE 流式输出和 Ops 仪表盘（DynamoDB + Cognito + SNS）为整个团队提供可见性。

LG Electronics 的营销洞察系统和 re:Invent 2025 上的 TechRecon 案例验证了这些设计原则。

在第 2 部分中，我们将在此架构之上考察四层 Context Engineering 技巧，用来克服上下文窗口的限制，从架构级隔离到提示词设计、工具优化和校验保障，并把我们的做法与 Anthropic 的工程研究进行对比。

Deep Insight 是开源的。欢迎探索代码，并将其扩展到你的领域。

- [GitHub](https://github.com/aws-samples/sample-deep-insight)
- Workshop：Deep Insight Workshop（[英文](https://catalog.us-east-1.prod.workshops.aws/workshops/ee17ba6e-edc4-4921-aaf6-ca472841c49b/en-US) | [韩文](https://catalog.us-east-1.prod.workshops.aws/workshops/ee17ba6e-edc4-4921-aaf6-ca472841c49b/ko-KR)）

## 关于作者
