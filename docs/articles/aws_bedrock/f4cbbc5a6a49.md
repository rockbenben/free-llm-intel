---
vendor: aws_bedrock
title: 5 production challenges in multi-agent systems and how Deep Insight solved them
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/5-production-challenges-in-multi-agent-systems-and-how-deep-insight-solved-them
date: 2026-10-21
lang: zh
captured: 2026-10-23
extractor: readability-v1
translator: mt
status: translated
body_sha: 6625353045dc
---

## [人工智能](https://aws.amazon.com/blogs/machine-learning/)

# 多代理系统中的 5 个生产挑战以及 Deep Insight 如何解决这些挑战

现在构建多代理系统非常简单。将其投入生产才是真正挑战的开始。借助开源框架和云服务，您可以在几天内设置代理。一些工具调用，几行提示，你就得到了一些看起来令人印象深刻的东西。但当团队试图超越试点并进入真正的业务应用程序时，他们遇到了熟悉的障碍。如果您曾经尝试将代理投入生产，这些挫折听起来很熟悉：

*为什么代理不遵循我们的业务逻辑、跳过验证步骤或捕获边缘情况？*

您调整提示，添加更多示例，更换模型。同样的问题不断出现。这是因为特工不遵循固定的指令顺序。他们根据上下文做出自己的判断。仅有说明是不够的。您需要设计代理的思考方式、验证时间以及出现问题时的处理方式。 This is exactly why it’s become critical to go beyond prompt engineering alone and design the agent’s entire cognitive architecture and execution flow.

为了应对这些挑战，AWS 解决方案架构团队构建了 [Deep Insight](https://github.com/aws-samples/sample-deep-insight)，这是一个生产级多代理系统。在本系列文章中，我们分享了团队在通过三篇文章构建深度洞察时所学到的第一手资料。我们将介绍如何在真实的生产环境中应用 Anthropic 提出的上下文工程技术（多代理架构、结构化笔记、人机交互等）。我们还介绍了我们在此过程中遇到的权衡（通过代码）以及我们从在 AWS 上部署和运行此代理获得的操作见解。

## 博客系列概述

- 第 1 部分：多代理系统中的 5 个生产挑战以及 Deep Insight 如何解决这些挑战。
- 第 2 部分：超越上下文窗口：上下文工程技术以及 Deep Insight 如何应用它们。
- 第 3 部分：实践中的利用工程：将 Deep Insight 从开发转向生产。

这是由三部分组成的系列中的第 1 部分。它定义了任何生产多代理系统必须解决的五个核心挑战，并展示了堆栈的每一层如何解决这些挑战，从 [Strands Agents SDK](https://strandsagents.com/) 和 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 到 [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/)、[应用程序负载]平衡器](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/create-application-load-balancer.html) 和 [AWS Fargate](https://aws.amazon.com/fargate/)。第 2 部分和第 3 部分介绍了上下文工程和生产部署。

## 深入洞察介绍

Deep Insight 是一个多代理系统，可将复杂的数据分析转化为自动化的见解。给定 CSV 文件和自然语言提示，专业代理（协调员、规划员、主管、编码员、验证员、报告员和跟踪员）的层次结构将协作进行分析。他们一起加载数据、运行分析、生成图表、验证计算并生成带有引文的专业报告 (.docx)。

我们稍后将详细探讨该架构。首先，让我们看看它的实际效果。在演示中，我们使用列定义文件 (`column_definitions.json`) 提供来自虚构食品公司 Yummy Food (`yummy-food-market.csv`) 的广告数据，并提供提示：*从销售和营销角度进行分析，生成图表和见解，并生成 .docx 报告。* Deep Insight 生成分析计划，将其提交给用户批准，一旦获得批准，就执行分析。

|  | **内容** |
| --- | --- |
|输入 | CSV 数据文件 (`yummy-food-market.csv`) + 列定义文件 (`column_definitions.json`) |
|示例提示 | “从销售和营销的角度进行分析，生成图表和见解，并生成 .docx 报告。” |
|输出| DOCX 报告（两种版本，一种带有引文，一种没有）以及图表图形 (PNG) |

接下来的 [Deep Insight 网络演示视频](https://www.youtube.com/watch?v=tMN29C4nam0) 显示了完整的工作流程，从上传数据和审查分析计划到实时流式传输和下载完成的报告。

## 我该如何尝试？

Deep Insight 在 [GitHub](https://github.com/aws-samples/sample-deep-insight) 上开源，提供完整的设置指南，并提供从开发到生产的三种部署选项。

第一个是[自托管版本](https://github.com/aws-samples/sample-deep-insight/tree/main/self-hosted)，它通过 CLI 在本地运行。它针对快速迭代进行了优化，可以对每个代理、提示和工作流程进行完整的代码级访问。它在大约 10 分钟内完成设置，这使得它非常适合开发。 （[YouTube](https://www.youtube.com/watch?v=pnyvBo98E1k) 上提供了自托管演示视频。）

第二个是[Web 版本](https://github.com/aws-samples/sample-deep-insight/tree/main/deep-insight-web)，一个基于浏览器的 UI，用于上传数据、审查分析计划（Human-in-the-Loop，或 HITL）和下载报告，所有这些都无需编写代码，使非开发人员也可以访问。 （前面的演示视频显示了正在运行的网络版本。）

第三个是 [托管 AgentCore 版本](https://github.com/aws-samples/sample-deep-insight/tree/main/driven-agentcore)，这是一个由 Amazon Bedrock AgentCore 支持的生产部署选项，它是一个使用任何框架或模型大规模构建、连接和优化代理的平台。此版本在 AgentCore 运行时部署代理，这是 Amazon Bedrock AgentCore 的一项功能。该系统完全在私有虚拟私有云 (VPC) 内运行，并在 AWS Fargate 上单独托管自定义代码解释器，并且代理在隔离的每用户环境中同时运行。当您需要会话隔离和私有 VPC 部署时，这是正确的选择。第 3 部分详细介绍了其部署和操作。

这三者共享相同的多代理架构，因此在开发中验证的代理可以按原样部署到生产中。

## 解决方案概述

构建生产多代理系统需要的不仅仅是良好的提示。您需要正确的技术堆栈和基础设施来解决代理如何协作、如何推理、如何部署它们、它们在何处安全执行代码以及如何监控运行状况。 Deep Insight 解决了这五个关键领域的问题。由于代理会生成代码和报告内容，因此我们还在解决方案详细信息 2 中介绍了负责生产的 AI 控制。

| **挑战** | **技术** | **方法** |
| --- | --- | --- |
| “我们如何控制跨多个代理的执行流程？” |股线代理 SDK |使用 Strands 的图形模式定义代理之间的执行顺序并实现人机循环分支。使用 Strands 的代理作为工具模式，以便主管可以根据需要调用专门的代理（编码器、验证器、报告器、跟踪器）作为工具。 |
| “每个代理应该使用哪种大型语言模型（LLM）？” |亚马逊基岩 |为每个角色选择正确的克劳德模型：俳句用于基本路线，作品用于规划，十四行诗用于执行。 |
| “我们如何在生产中可靠地操作成品代理？” |亚马逊基岩代理核心 |具有监控、会话隔离和私有 VPC 部署的托管运行时。 |
| “我们如何减轻执行人工智能生成代码的安全问题？” | AWS Fargate + 应用程序负载均衡器 (ALB) |每个会话的临时沙箱容器，用于通过自定义代码解释器隔离代码执行。 |
| “我们如何监控和管理系统？” | Amazon DynamoDB + Amazon 简单通知服务 (Amazon SNS) + Amazon Cognito |管理仪表板和故障警报系统。 |

下面的架构图（图 1）一目了然地说明了这一点。绿色框代表 Strands Agents 多代理结构，它解决了上表中的挑战 1 和 2。我们将在即将发布的解决方案详细信息 1：多代理系统设计部分中详细介绍这一点。图中显示的其余基础设施组件解决了挑战 3、4 和 5，我们将在解决方案详细信息 2：生产部署和运营中详细介绍这些挑战。

![Deep Insight 架构：Amazon Bedrock AgentCore 上的 Strands Agents 多代理层，通过应用程序负载均衡器将代码执行路由到私有环境中的 AWS Fargate 容器。 VPC](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21081-1-1.png)

图 1：解决方案架构

## 解决方案细节1：多智能体系统设计

Deep Insight 使用多代理架构，其中八个代理协作生成一份高质量的交付成果。每个代理都在自己独立的上下文中工作，仅执行其专门任务，并且仅向前传递压缩结果。

![分层多代理结构，协调员和规划员为主管提供信息，主管协调编码员、验证员、报告员和跟踪员代理](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21081-2-1.png)

图2：多智能体结构

协调员路由用户请求，规划员将任务分解为离散的步骤，计划审核员收集用户反馈，主管根据计划调用适当的专业代理。 Coder 编写并执行数据分析代码，Validator 验证计算，Reporter 生成最终报告，Tracker 跟踪进度。我们将通过三个层次来解释这一点：

- [第一层] 协调员到计划员到计划审核员：请求分析和执行计划创建。
- [第二层] Supervisor：专门的代理编排。
- [第三层] 编码器、验证器、报告器、跟踪器：专门的任务执行。

Strands Agents SDK 中的两个关键模式相结合来控制这些代理之间的执行流。首先，图模式将代理的执行顺序和流程定义为有向图。请求流程为协调员、计划员、计划审核员，然后是主管，并根据修订请求循环返回计划员的条件分支。按条件确定下一步使复杂的工作流程（如 HITL 和错误处理）变得简单。其次，[代理即工具模式](https://strandsagents.com/docs/user-guide/concepts/multi-agent/agents-as-tools/) 允许主管仅在需要时调用专用代理（编码器、验证器、报告器、跟踪器）作为工具。每个都在独立的上下文中工作并仅返回结果，最大限度地减少上下文使用，同时保留领域专业知识。

本节展示该架构如何解决路由、规划和编排问题。

### [第一层] 协调员到规划员到计划审核员

该层将用户请求转化为批准的执行计划。

#### 1.1 协调器（路由）：并非每个请求都需要昂贵的编排

协调器是用户请求的入口点。它直接处理基本问候语，并使用 handoff_to_planner 标记将数据分析等复杂任务路由到 Planner。

关键的设计决策是模型选择：因为协调器仅进行分类，所以它使用轻量级的 Claude Haiku，避免了基本问候语的 Opus 级别成本并提供快速响应。
```
# builder.py: conditional edges for routing decisions
builder.set_entry_point("coordinator")
builder.add_edge("coordinator", "planner", condition=should_handoff_to_planner)
```
路由条件来自协调员的提示：任何需要工具、推理或多步骤思考的请求都会发送给计划员。

#### 1.2 Planner（计划创建）：复杂的分析需要在执行前分解

在 Deep Insight 的多智能体结构中，Planner 智能体在跨智能体分配任务方面发挥着关键作用。在实质性工作开始之前，它将大型任务分解为较小的步骤，每个专门代理一次执行一个任务，从而保持每个代理的上下文较小。

规划器使用 Claude Opus 模型并启用扩展思维来制定分析计划。它将计划组织成“[]”清单格式，指定分配给每个代理的具体任务，存储在“full_plan”变量中。它将请求分为 5-10 个清晰的步骤，如以下示例所示：
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
#### 1.3 计划审核员

计划审核者是一个 HITL 节点，它将计划呈现给用户并收集*批准或修订反馈*。如果有反馈，它会循环回到规划器以修改计划。如果获得批准，它将把任务交给主管。设置最大修订计数（“MAX_PLAN_REVISIONS”）以防止无限循环。
```
# builder.py: Plan Reviewer's bidirectional conditional edges
builder.add_edge("plan_reviewer", "planner", condition=should_revise_plan)
builder.add_edge("plan_reviewer", "supervisor", condition=should_proceed_to_supervisor)
builder.set_max_node_executions(25)
```
在 Web 版本中，计划审阅者显示一个浏览器模式，用户可以在其中阅读计划并批准它或输入修订反馈。如果没有响应，300 秒倒计时会自动批准该计划。

![Deep Insight Web UI 显示计划审阅者模式，用户可以在其中批准或修改生成的分析计划](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21081-3-1.png)

图 3：在 Web UI 中计划 Reviewer 代理执行

如果没有计划，代理会在运行时决定一切，中途修正会使之前的工作失效，并且用户无法了解进度。通过规划器和计划审核器，用户可以审核和修改计划、实时监控进度并仅重新执行失败的步骤。

###【第二层】主管（指挥）：专业特工需要指挥

Supervisor 按顺序执行 Planner 的“full_plan”，调用第 3 层代理（Coder、Validator、Reporter、Tracker）作为通过 Tool Use 注册到其上的工具。
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
Supervisor的系统提示定义了严格的工作流程规则：

- 强制执行顺序：Coder、Tracker、Validator、Tracker、Reporter、Tracker：每个 Agent 运行后，调用 Tracker 来跟踪进度，让 Supervisor 管理整体任务状态。
- 部分完成规则：在当前座席的所有清单项目都标记为 [x] 之前，主管不会移动到下一个座席。
- 上下文保存：Supervisor 将线索和 full_plan 变量传递给每个工具代理，维护完整的上下文并防止信息丢失。

### 【第三层】编码员、验证员、报告员、跟踪员：分工驱动质量

每个第 3 层代理（编码器、验证器、报告器、跟踪器）都被包装为“PythonAgentTool”，并接收来自 Supervisor 的工具使用调用。每个都在 Strands SDK 中创建为独立的“Agent()”实例，具有自己的系统提示、模型 ID 和工具集。

| **代理** | **角色** | **工具** | **关键输出** |
| --- | --- | --- | --- |
|编码员 |数据分析、图表生成、洞察推导 | write_and_execute_tool、bash_tool、file_read、skill_tool | *.png 图表，`calculation_metadata.json` |
|验证者 |数值计算重新验证、引文生成 | write_and_execute_tool、bash_tool、file_read | `引用.json`，validation_report.txt |
|记者| DOCX 报告生成 | write_and_execute_tool、bash_tool、file_read | Final_report.docx、final_report_with_itations.docx |
|追踪器 |清单进度状态更新 |无（仅限法学硕士推理）|更新完整计划 |

主管根据计划员的清单按以下顺序调用工具使用调用：

- Coder – 加载数据，编写并运行分析代码，生成 PNG 图表，在 all_results.txt 中累积结果，并留下 `calculation_metadata.json` 进行验证。
- 跟踪器（第 1 遍）- 将已完成的清单项目从 [ ] 更新为 [x]，主管用来决定是否继续。
- 验证器 – 根据源数据重新执行 `calculation_metadata.json` 中的每个计算。 0.01 以内的匹配通过，不匹配被标记。经过验证的计算结果会转到“itations.json”供记者引用。
- 跟踪器（第二遍）——反映验证器在清单中的完成状态。
- Reporter – 读取 all_results.txt 和 `itations.json` 以生成两个版本的最终 DOCX 报告（带引用和不带引用）。
- 跟踪器（第三遍）——反映所有任务的最终完成状态。

跟踪器在每个代理之后运行，以便主管可以跟踪进度并强制执行完成规则（在所有项目都完成 [x] 之前不会继续）。因为它使用 LLM 推理更新清单，而不使用任何工具，所以几乎不会增加开销。

### 每个代理 LLM 模型配置

Deep Insight 根据每个代理的角色定制模型和设置。这不是模型选择。这是优化成本和质量的架构决策。

| **代理** | **型号** | **延伸思考** | **提示缓存** | **角色** |
| --- | --- | --- | --- | --- |
|协调员|俳句 |已禁用 |没有 |快速路由：成本最小化 |
|规划师|作品|已启用（约 8,192 个代币）|没有 |深度思考：高质量策划|
|主管|十四行诗|已禁用 |是的 |执行编排：缓存以节省成本|
|编码员 |十四行诗|已禁用 |是的 |代码生成/执行：缓存对重复调用有效|
|验证者 |十四行诗|已禁用 |没有 |数值验证：每次数据不同，无需缓存 |
|记者|十四行诗|已禁用 |是的 |报告生成：缓存对长提示有效|
|追踪器 |十四行诗|已禁用 |没有 |状态更新：轻量级任务，无需缓存 |

主管、编码员和报告员代理使用提示缓存来缓存其系统提示和工具定义，从而将重复调用的输入令牌成本降低高达 90%。协调器仅运行一次，而验证器和跟踪器每次都在不同的上下文中运行，因此缓存对它们来说无效并保持禁用状态。这种选择性缓存策略是经过深思熟虑的成本/性能权衡。

## 解决方案细节2：生产部署和运营

如果解决方案细节 1 定义了*系统的功能*，则本节定义了系统安全运行的地点和方式。从这里开始的一切都涵盖了生产运营的基础设施决策。具体来说，本节涵盖了 LLM 生成代码的安全执行环境以及团队的操作可见性。

### 1.代码执行：LLM生成的代码需要安全的执行环境

Coder 代理编写并运行 Python 以进行数据分析。在自托管版本中，它通过“subprocess.run()”在本地运行，但在生产 (AgentCore) 中，安全性和隔离至关重要。直接在生产服务器上运行 LLM 生成的代码是有风险的：模型可能会删除系统文件、无限循环中耗尽资源或访问其他用户的分析数据。 Deep Insight 通过 AWS Fargate 和 ALB 上的每会话临时容器解决了这个问题。这些组件并不是孤立运行的。如图 1 所示，AgentCore 运行时、ALB 和 Fargate 任务都在同一私有 VPC 内运行。 VPC 终端节点将它们连接到 Amazon Simple Storage Service (Amazon S3)、Amazon Bedrock 和 Amazon Elastic Container Registry (Amazon ECR)，而无需遍历公共互联网。安全组限制哪些组件可以访问代码解释器容器。 AWS Identity and Access Management (IAM) 角色将每个组件的范围仅限于其所需的 AWS 资源。 Amazon CloudWatch 从 AgentCore 可观察性（Amazon Bedrock AgentCore 的一项功能）收集容器日志和可观察性数据。

- 自定义容器 Docker 映像：预先优化的沙箱，其中包含用于多代理系统的字体、系统库和 Python 包。
- 容器隔离：每个分析会话都会在私有 VPC 子网中获得一个独立的 Fargate 容器，无法直接访问互联网。
- 两步执行：LLM 生成的代码经过 base64 编码，通过 HTTP 发送，写入文件（步骤 1），然后通过子进程执行（步骤 2）。
- 会话亲和性：ALB 粘性会话 cookie 会将代理路由回同一容器，即使它多次执行代码也是如此。
- 工件管理：分析完成后，图表、报告和日志上传到 Amazon S3。容器在一小时后自动终止。

容器隔离可以保护基础设施，但它不能控制代理生成的内容。验证器代理重新验证计算。它不会检测隐藏在上传数据中的提示注入指令，也不会筛选 LLM 生成的文本中是否存在有害或不可靠的内容。对于生产部署，我们建议添加 Amazon Bedrock Guardrails 作为负责任的 AI 控制：对用户提示和上传的数据应用内容过滤器和提示攻击检测，并对代理输出应用上下文基础检查，以便报告文本保持源数据和经过验证的计算的基础。

### 2. 运营和监控：团队需要可见性

生产系统仅靠代码是不完整的。团队必须评估系统运行状况、诊断问题并审查结果，因此 Deep Insight 提供了 Web UI 和 Ops 仪表板。

#### Web UI（深度洞察网络）

基于 FastAPI 的 Web 界面，通过 AgentCore 本机协议 (`boto3.invoke_agent_runtime()`) 与后端通信。用户上传数据并输入提示，然后通过服务器发送事件 (SSE) 流式传输监控进度。生成计划后，用户会通过一个模式批准或提供修订反馈 (HITL)。完成的报告可以直接下载。支持韩语和英语。

![Deep Insight Web 界面，用于上传数据、输入提示和下载生成的报告](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21081-4-1.png)

图4：Deep Insight网页版截图

#### 操作仪表板（deep-insight-web/ops）

Ops 仪表板是可选的。 Deep Insight 在没有它的情况下也能正常工作，但它为需要它们的团队添加了以下功能：

- 任务跟踪：所有分析任务指标（包括状态、令牌使用情况和已用时间）都记录在 Amazon DynamoDB 中。
- 失败警报：当分析失败时，会立即通过 Amazon SNS 向管理员发送电子邮件。
- 管理仪表板：专用管理仪表板通过 Amazon Cognito 受到 JSON Web 令牌 (JWT) 身份验证的保护，以实现安全任务监控。

![Deep Insight Ops 仪表板列出了分析任务的状态、令牌使用情况和已用时间](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21081-5-1.png)

图 5：Deep Insight Ops 仪表板屏幕截图

![Deep Insight Ops 仪表板详细视图显示单个分析任务的指标](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/19/ml-21081-6.png)

图 6：Deep Insight Ops 仪表板详细视图

## 扩展 Deep Insight 架构

Deep Insight 的多代理架构并不局限于数据分析报告生成的单一领域。以下两个示例表明，分层编排设计原则在完全不同的领域中仍然有效。

### 案例 1：LG 电子：Agentic AI 支持的营销洞察提取系统

LG 电子的韩国销售部门在与 Deep Insight 相同的多代理架构上构建了 ChatInsight，其中数据分析请求需要 2-3 周的时间，并且营销人员和数据科学家之间失去了意图。协调器按复杂性进行路由，规划器跟踪任务，主管协调编码器和报告器，代理间状态通过 all_results.txt 文件累积传递。原本需要 3 天的分析现在只需 30 分钟，生产力提高了 288 倍。不了解 SQL 的营销人员可以让代理探索数据并提出策略（请参阅 [AWS 技术博客上的 LG Electronics Agentic AI 洞察提取系统](https://aws.amazon.com/ko/blogs/tech/lge-agentic-report-automation/)）。

![LG Electronics ChatInsight 架构使用与 Deep 相同的协调员、计划员、主管、编码员和报告员多代理模式洞察](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21081-7-1.png)

图7：LG电子Agentic AI营销洞察系统架构

### 案例 2：TechRecon：人工智能驱动的技术侦察代理（re:Invent 2025）

TechRecon 在 AWS re:Invent 2025（会议 SNR203）上发表，将 Deep Insight 的架构应用于技术战略。对于给定的公司和行业，研究人员收集技术趋势，编码人员进行分析，验证人员进行验证，报告人员进行景观分析和技术立场文件。该架构与 Deep Insight 几乎相同，采用 Strands Agents SDK 图形模式以及扩展思维和提示缓存构建，Researcher 取代 Coder 作为主要执行代理。它表明该设计是一种通用模式：交换代理的角色和提示，相同的编排结构可以解决完全不同的问题。

![TechRecon 输出显示侦察代理制作的景观分析和技术立场文件](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21081-8-1.png)

图 8：TechRecon 结果

（了解更多：[TechRecon GitHub](https://github.com/aws-samples/sample-tech-recon) | [AWS re:Invent 会议视频](https://www.youtube.com/watch?v=NwkH_F3yUiY))

## 结论

构建一个在生产环境中工作的代理并不是模型能力的问题。这是一个架构问题。 Deep Insight 提供了经过验证的答案：

- 工作流管理：Strands Agents SDK 的图形模式定义代理之间的执行顺序并实现 HITL 分支，而代理即工具模式允许主管仅在需要时调用专用代理。
- 推理引擎：我们按角色（Haiku、Opus、Sonnet）分配来自 Amazon Bedrock 的 Claude 模型，以优化成本和质量。
- 部署：Amazon Bedrock AgentCore 提供具有会话隔离、私有 VPC 部署和 OpenTelemetry 可观测性的托管运行时。
- 代码执行：Fargate 上的应用程序负载均衡器和 Amazon Elastic Container Service (Amazon ECS) 将 LLM 生成的代码执行隔离在每个会话的临时沙箱容器中，从而防止系统文件访问、资源耗尽和意外数据泄露等安全问题。
- 运营：Web UI 的 SSE 流和运营仪表板（DynamoDB + Cognito + SNS）提供整个团队的可见性。

LG 电子的营销洞察系统和 re:Invent 2025 上的 TechRecon 案例验证了这些设计原则。

在第 2 部分中，我们研究了四层上下文工程技术，用于克服该架构之上的上下文窗口限制，从架构级隔离到提示设计、工具优化和验证保障措施，并将我们的方法与 Anthropic 的工程研究进行比较。

Deep Insight 是开源的。探索代码并将其扩展到您自己的域。

- [GitHub](https://github.com/aws-samples/sample-deep-insight)
- 研讨会：深度洞察研讨会（[英语](https://catalog.us-east-1.prod.workshops.aws/workshops/ee17ba6e-edc4-4921-aaf6-ca472841c49b/en-US) | [韩语](https://catalog.us-east-1.prod.workshops.aws/workshops/ee17ba6e-edc4-4921-aaf6-ca472841c49b/ko-KR))

## 关于作者
