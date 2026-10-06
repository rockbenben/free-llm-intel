---
vendor: aws_bedrock
title: 使用 Amazon Bedrock AgentCore 评估多智能体系统的可解释性与有用性
original_title: Evaluating multi-agent systems for explainability and helpfulness with Amazon Bedrock AgentCore
url: https://aws.amazon.com/blogs/machine-learning/evaluating-multi-agent-systems-for-explainability-and-helpfulness-with-amazon-bedrock-agentcore
date: 2026-10-05
lang: zh
captured: 2026-10-06
extractor: readability-v1
translator: agent
status: translated
---

随着多智能体系统从实验阶段走向生产环境，一个关键挑战随之浮现：如何确保这些系统在真实场景中始终有用、准确且可解释。企业正越来越多地采用多智能体系统来解决复杂的现实问题，这类问题需要跨数据源、工具和业务约束进行推理。从供应链规划到财务分析和客户运营，这些系统已超越了简单的问答。它们协调多个专职智能体（specialized agent）来做决策、执行工作流，并生成可落地的建议。

虽然大语言模型能生成流畅的回答，但企业应用需要更深层的保障：智能体必须可靠地遵循指令、选对工具、尊重约束，并为其输出提供清晰的推理过程。

[Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) 是一个平台，支持以任意框架或模型大规模地构建、连接和优化智能体。[Amazon Bedrock AgentCore Evaluations](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations.html) 是 Amazon Bedrock AgentCore 的一项能力，正是为应对这一挑战而设计：它是一项完全托管的能力，用于在开发和生产环境中评估智能体表现，让团队能够跨多个质量维度衡量准确性、任务成功率和行为表现。仅关注模型回答质量的传统评估方法对智能体式（agentic）系统而言是不够的，因为这类系统的正确性取决于工具选择、工作流执行以及对业务约束的遵守。除了评估，智能体式系统的生产部署还需要负责任 AI 的控制措施。[Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/) 提供可配置的防护手段，例如内容过滤、禁用主题检测和基于事实的校验（grounding validation），与评估框架形成互补：评估在执行之后衡量智能体质量，而 Guardrails 在执行期间强制落实安全约束。在这篇文章中，我们聚焦于如何把这一评估框架落地运转起来——Amazon Bedrock AgentCore Evaluations 同时支持内置评估器（built-in evaluator）和自定义评估器（custom evaluator）。内置评估器为常见质量维度（如有用性、任务成功、指令遵循）提供预定义评估，让团队无需额外配置就能快速建立智能体性能基线。然而企业用例需要更深入的、领域特定的验证，自定义评估器正好补上这一点，让你可以定义业务感知的检查项。

我们还特别把可解释性（explainability）作为一等公民的评估维度来讨论。我们演示内置评估器如何评估回答的一般清晰度；也展示如何借助自定义评估器来验证智能体是否明确阐述决策依据、引用支撑数据或工具输出，并解释成本与服务质量之间的取舍。通过组合这些评估器，我们说明 AgentCore Evaluations 如何超越表层的回答质量，针对智能体如何以及为何得出其决策，给出结构化、可度量的洞察。

为了让这些概念更具体，下面的章节将通过一个参考架构和实现，演示这些组件在实践中如何协同工作。

## 方案概览

在这篇文章中，我们使用一家虚构的全球零售公司 AnyCompany Retail——一家跨国零售商，运营电商渠道、区域履约中心、配送中心以及数千家实体店。AnyCompany 频繁遭遇库存失衡：有些区域在大促期间缺货，另一些区域却积压过剩库存。运输团队还必须兼顾交付速度、运力与成本。公司希望有一个智能体式助手，帮助计划员优化库存分配、推荐调拨调整、分析库存健康度，并模拟干线运输或履约场景。

你将使用 [Strands Agents SDK](https://strandsagents.com/)、[Amazon Bedrock AgentCore MCP Server](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp.html) 和 Amazon Bedrock AgentCore Evaluations，构建并评估一个多智能体供应链决策系统。该方案基于 Strands Agents，采用一个编排智能体（orchestrator agent）加四个专职子智能体：优化智能体、调拨智能体、路由智能体和分析智能体。每个智能体都运行在 [Amazon Bedrock AgentCore runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html) 上，并启用了 [Amazon Bedrock AgentCore memory](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html) 和 [Amazon Bedrock AgentCore Observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html)。

编排智能体接收计划员的请求，并把工作分派给以工具形式暴露的专职智能体。优化智能体调用由模拟 [Amazon API Gateway](https://aws.amazon.com/api-gateway/) REST 接口支撑的 MCP 工具，返回优化决策。调拨智能体调用推荐 API，建议在履约中心、门店和数字渠道之间重新平衡库存。路由智能体调用物流 API，推荐承运商与线路方案；分析智能体回答供应链诊断类问题。该方案使用 Amazon Bedrock 上的基础模型驱动智能体循环。各区域可用的模型参见 [Amazon Bedrock 中按 AWS Region 支持的模型](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html)。

该方案使用内置评估器来评估有用性、任务完成度等一般质量维度，同时提供自定义评估器来评估供应链特有的行为，例如约束满足、路线可行性、SQL 正确性、库存数据落地（grounding）与解释质量。这样，AnyCompany 既能评估回答的语言质量，也能评估智能体决策的业务有效性。

该方案通过 Amazon Bedrock AgentCore Evaluations 同时支持按需（on-demand）和在线（online）两种模式。按需模式适用于开发基准测试、回归测试以及持续集成与持续交付（CI/CD）门禁；在线模式用于持续的生产监控与告警。两种模式都能帮助你闭环，并根据用户反馈采取行动。用于按需评估的同一批自定义评估器（例如你供应链方案中的约束满足、路线可行性、SQL 正确性和可解释性评估器）可以通过一个 OnlineEvaluationConfig 对象改造复用：该对象引用这些评估器的 Amazon Resource Name（ARN），指定采样率（例如生产 trace 的 1–10%），并可加上可选的会话过滤器。随后服务会自动从 AgentCore Observability 读取 trace、进行评分，并把结果流送到 [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/) 仪表盘和告警。在这篇文章中，你将使用按需模式来测试该方案。

下面的架构图展示了我们方案的各个组件。

图 1：多智能体供应链决策方案的架构

## 评估框架

在这篇文章中，你将采用一种面向多智能体系统的三层评估方法，循序渐进地建立企业级信任。该方法遵循清晰的递进路线：先以内置评估器覆盖一般质量，再加入自定义评估器保障业务准确性，最后叠加可解释性评估器实现信任与可审计性。

第一层使用无需任何配置的内置评估器。我们以有用性（Helpfulness）作为普适基线，再针对每个智能体的主要失效模式选配第二个智能体专属评估器：编排智能体用工具选择准确性（Tool Selection Accuracy），优化与调拨智能体用回答相关性（Response Relevance），路由智能体用指令遵循（Instruction Following），分析智能体用忠实度（Faithfulness）。

第二层加入编码了领域特定业务规则的自定义评估器：优化用约束满足、调拨用数据落地（grounding）、路由用路线可行性、分析用 SQL 正确性、编排用计划连贯性。这些评估器验证的是业务有效性：建议是否遵守了预算上限、是否使用了真实库存数据、产出是否在运营上正确。

下表梳理了你要为每个智能体实现的两个内置评估器和一个自定义评估器的选择。第二个内置评估器针对各智能体的主要失效模式，而自定义评估器编码领域特定的业务规则，用于验证运营上的正确性。

| **智能体** | **内置评估器** | **自定义评估器** |
| --- | --- | --- |
| 编排智能体 | Helpfulness；Tool Selection Accuracy | 计划连贯性评估器：它是否把子智能体的输出组合成了一份有效、不自相矛盾的建议？工具轨迹（tool trajectory）评估器：它是否路由到了正确的子智能体？ |
| 优化智能体 | Helpfulness；Response Relevance | 约束满足评估器：预算、库存覆盖（demand ≤ qty ≤ 2× demand）和仓库容量约束。关键绩效指标（KPI）达成评估器：是否达到满足率/收入提升目标。 |
| 调拨智能体 | Helpfulness；Response Relevance | 建议落地性（groundedness）评估器：建议是否基于当前库存/需求数据。风险影响评估器：建议是否改善了缺货/积压风险。 |
| 路由智能体 | Helpfulness；Instruction Following | 路线可行性评估器：路线是否满足交付窗口、成本、承运商运力和区域约束。服务等级协议（SLA）评估器：预计交付是否达到目标服务水平。 |
| 分析智能体 | Helpfulness；Faithfulness | SQL 正确性评估器：查询是否匹配用户意图。数据落地评估器：回答是否有 Amazon Relational Database Service（Amazon RDS）查询结果支撑。无未经支撑论断的评估器。 |

## 可解释性

我们评估方法的第三层把可解释性评估器作为独立的、横切各智能体的检查项。这些评估器独立判断：智能体是否阐述了决策依据、是否引用了来自工具输出的支撑证据、是否解释了哪些约束塑造了最终回答、是否说清了相互冲突目标之间的取舍、是否阐明了为何调用特定的子智能体，以及在数据不完整时是否披露了假设。把可解释性拆成独立的评估层，我们就能单独度量透明度。一条建议可能准确却无法解释（通过自定义评估器但在可解释性上失分），这给团队提供了可操作的信号：智能体需要改进的是推理表达，而非决策逻辑本身。

下表定义了你要在此实现的六个独立可解释性评估器，它们作为横切层应用于各智能体。这些评估器判断智能体是否阐述推理、引用证据、解释约束与取舍、披露假设。它们与准确性分开度量，以便团队区分"正确但无法解释"与"解释得好但答错了"两类回答。

| **评估器** | **适用智能体** | **检查内容** |
| --- | --- | --- |
| 决策依据质量 | 全部 | 智能体是否解释了它为什么给出这条建议？ |
| 证据归因 | 分析、调拨、路由 | 它是否引用了所用的数据字段、API 响应或 SQL 结果？ |
| 约束推理 | 优化、路由 | 它是否解释了哪些约束塑造了最终回答？ |
| 取舍解释 | 优化、调拨、路由 | 它是否解释了成本、服务水平与库存风险之间的取舍？ |
| 工具使用可解释性 | 编排 | 它是否解释了为何调用每个子智能体或 MCP 工具？ |
| 假设披露 | 全部智能体 | 它在数据不完整时是否明确陈述了假设？ |

## 前置条件

在部署该方案之前，用以下工具搭好你的开发环境。

- 安装 [AWS Command Line Interface (AWS CLI)](https://aws.amazon.com/cli)
- 安装 [AWS Serverless Application Model (AWS SAM) CLI v1.100.0+](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- 安装 [Docker v20.x+](https://docs.docker.com/engine/install/)
- 安装 [Node.js v18.x+](https://nodejs.org/)
- 安装 [Python v3.11+](https://www.python.org/downloads/)

## 依赖

Strands Agents 的实现还需要以下依赖，已打包在 DockerFile 中：

- strands-agents # Strands Agents 多智能体框架
- strands-agents-tools # Strands 智能体工具与实用函数
- requests # 用于 API 调用的 HTTP 库
- bedrock-agentcore # Amazon Bedrock 智能体核心功能
- boto3 # AWS SDK for Python（Boto3）

## 部署并运行方案

该方案可从我们的 [GitHub 仓库](https://github.com/aws-samples/sample-agentic-genai-agentcore/tree/main/aws-genai-evaluations-supply-chain)下载，提供单步部署，在你的 AWS 环境中部署并访问该方案：

```
# Edit terraform.tfvars: set vpc_id and runtime_subnet_azs
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply
```

输出中包含运行时 ARN、AnyCompany Retail API URL、评估器 API URL 以及 memory ARN。

## 运行方案

按以下步骤运行该方案：

test_client/ 目录中有一个 Python 脚本，用 20 个示例查询（每个子智能体 5 个）调用已部署的供应链智能体，以验证端到端功能。每个类别以多轮会话的形式运行，脚本结束时打印会话 ID，供评估器 API 使用。

```
cd test_client
pip install -r requirements.txt
cd terraform
terraform output supply_chain_arn
```

**运行全部查询（共 20 个，4 个会话）**

```
cd test_client
python test_agent.py --runtime-arn "<supply_chain_arn>" --region <your_region>
```

### 运行特定子智能体类别

```
#Only optimization queries (1 session, 5 turns)
python test_agent.py --runtime-arn "<supply_chain_arn>" --category optimization
#Only routing and analytics (2 sessions, 5 turns each)
python test_agent.py --runtime-arn "<supply_chain_arn>" --category routing analytics
```

测试客户端会打印每条查询及智能体的完整响应，并在结束时打印供评估器使用的会话 ID。

**创建并运行评估**

test_evaluators/ 目录中的脚本用于针对智能体会话运行评估。这些评估异步执行，结果会以 markdown 文件形式保存到 S3。

你必须先按前文所述调用供应链决策多智能体方案，生成带有 trace 的智能体会话，并记下测试客户端运行结束时打印的会话 ID。运行完方案后还要再等 3-5 分钟，让 trace 传播到 CloudWatch。

```
cd test_evaluators
pip install -r requirements.txt
cd terraform
terraform output evaluators_api_url
```

**创建自定义评估器**

```
python test_evaluator.py --api-url "https://<evaluators-api-url>" create
```

这会注册自定义评估器并打印它们的 ID。保存好这些 ID，供 run 命令使用。

**运行评估**

传入以逗号分隔的评估器 ID 列表（自定义或内置），至少需要 1 个：

```
# Run custom + built-in evaluators
python test_evaluator.py --api-url "https://<evaluators-api-url>" run \
--agent-id "supply_chain_orchestrator_agent-<id>" \
--session-id "<session-id-from-test-client>" \
--evaluators " sc_optimization_constraint-<id>,sc_distribution_groundedness-<id>,Builtin.Correctness,Builtin.GoalSuccessRate"
```

API 会立即返回 202。结果异步保存到 S3：

```
s3://<amzn-s3-demo-agent-source-bucket>/evaluations/<session-id>/<timestamp>/EvaluationResults.md
```

**删除评估器**

```
python test_evaluator.py --api-url "https://<evaluators-api-url>" delete \
--evaluator-ids "sc_optimization_constraint-<id>,sc_distribution_groundedness-<id>"
```

## 运行一次优化评估

现在你已经了解评估框架并部署了方案，我们来对优化智能体做一次端到端的聚焦评估。这一演示展示如何把一个自定义业务准确性评估器（第二层）与可解释性评估器（第三层）结合使用，同时评估优化决策的正确性与透明度。

**第 1 步：运行优化查询**

首先，仅以优化类别调用测试客户端，生成一个聚焦的会话：

```
cd test_client
python test_agent.py --runtime-arn "<supply_chain_arn>" \
--category optimization \
--region <your_region>
```

这会以多轮会话形式运行 5 个优化查询。智能体处理的请求例如："prod-001 未来 30 天的最优库存水位是多少？"每个查询都要求优化智能体调用 MCP 工具、获取需求预测，并给出遵守预算、库存覆盖和仓库容量约束的备货建议。运行结束时，测试客户端会打印优化会话 ID。

**第 2 步：运行约束满足评估器（第二层：业务准确性）**

有了优化会话后，运行自定义的约束满足（Constraint Satisfaction）评估器，验证智能体的备货建议是否遵守业务规则。该评估器同时检查三项约束：

- 预算：新增持有成本是否落在剩余预算内（budget_limit − budget_used）？
- 库存覆盖：建议水位是否 ≥ 需求预测（避免缺货）且 ≤ 2× 需求（避免积压）？
- 仓库容量：建议水位是否放得下可用的仓库空间？

把该评估器与内置的 Helpfulness、Response Relevance 评估器一起运行：

```
cd test_evaluators
python test_evaluator.py --api-url "https://<evaluators-api-url>" run \
--agent-id "supply_chain_orchestrator_agent-<id>" \
--session-id "<optimization-session-id>" \
--evaluators "sc_optimization_constraint-<id>,Builtin.Helpfulness,Builtin.ResponseRelevance"
```

API 立即返回 HTTP 202。评估异步运行，结果保存到 S3：

```
s3://<amzn-s3-demo-agent-source-bucket>/evaluations/<optimization-session-id>/<timestamp>/EvaluationResults.md
```

**第 3 步：运行可解释性评估器（第三层：信任与可审计性）**

确认优化智能体能给出满足约束的建议之后，下一个问题是：它有没有解释自己的推理？一条建议可能准确但晦涩——这类建议能通过约束评估器，却无法说明它为什么选择某个库存水位。

沿用第 1 步得到的同一个优化会话 ID，现在运行适用于优化智能体的两个可解释性评估器：

- 决策依据质量（Decision Rationale Quality）—— 智能体是否解释了它为什么给出该建议？（例如"因为需求预测为 1,200、我们按 1.25× 安全系数备货，所以建议 1,500 件"）
- 约束推理（Constraint Reasoning）—— 智能体是否解释了哪些约束塑造了最终回答？（例如"预算允许最多 1,800 件，但仓库容量把我们限制在 1,600 件，因此建议 1,500 件"）

```
python test_evaluator.py --api-url "https://<evaluators-api-url>" run \
--agent-id "supply_chain_orchestrator_agent-<id>" \
--session-id "<optimization-session-id>" \
--evaluators "sc_decision_rationale-<id>,sc_constraint_reasoning-<id>"
```

这些评估器独立度量透明度，与准确性分开评估。

**解读组合结果**

对同一个优化会话运行全部三个评估器后，你就能从两个维度完整把握智能体的质量：

| **维度** | **评估器** | **回答的问题** |
| --- | --- | --- |
| 业务准确性（第二层） | 约束满足 | 建议在运营上是否正确？ |
| 可解释性（第三层） | 决策依据质量 | 智能体*为什么*给出这条建议？ |
| 可解释性（第三层） | 约束推理 | *哪些约束*塑造了回答？ |

表 3：跨质量维度的评估覆盖

这种分层方法支持有针对性的改进。如果约束满足得分高、可解释性得分低，说明智能体的决策逻辑是可靠的，但表达方式需要改进。反之，如果可解释性高但约束被违反，说明智能体推理讲得很清楚，但用的逻辑是错的。每种失效模式的修复路径不同，而评估框架让这种区分变得可度量。

## 清理

为避免持续产生费用，试用完方案后请用一个步骤清理你的 AWS 账户。

```
terraform destroy
```

## 结论

在这篇文章中，我们演示了如何用 Amazon Bedrock AgentCore Evaluations 构建并评估一个多智能体供应链决策系统，重点验证智能体行为不仅功能可用，而且有用、准确、可解释。借助 AnyCompany Retail 的场景，我们展示了编排智能体如何与专职子智能体协作解决库存分配、调拨规划、路由优化和供应链诊断等复杂问题，同时与企业数据源和 API 集成。正如架构部分所阐明的，智能体式系统中的"正确"远不止回答质量，它取决于选对工具、执行正确的工作流、遵守业务约束，并让输出扎根于数据。

把内置评估器与自定义评估器结合使用，团队就能系统性地验证一般回答质量和领域特定的决策准确性。再加上以可解释性为核心的评估器，可以进一步确保智能体清晰阐述推理、引用支撑数据、解释取舍，让业务用户能够信任并据以行动。这种评估驱动的做法支持用真实执行数据持续改进，在上线生产前建立质量门禁，并为交付一致、透明、贴合业务的多智能体系统提供了可扩展的框架。

要开始上手，请了解 [Amazon Bedrock AgentCore Evaluations](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations.html)，把这些模式应用到你自己的多智能体应用中。完整源码见 [GitHub 上的 Amazon Bedrock AgentCore 示例仓库](https://github.com/awslabs/agentcore-samples/tree/main/06-workshops/07-AgentCore-evaluations)。建议从启用可观测性开始，为你的用例定义关键评估维度，再逐步引入内置和自定义评估器，度量最重要的东西。

欲了解更多，请访问 [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) 服务页面，或直接在 [Amazon Bedrock 控制台](https://console.aws.amazon.com/bedrock/)开始上手。

**相关文章：**

- [Build reliable AI agents with Amazon Bedrock AgentCore Evaluations](https://aws.amazon.com/blogs/machine-learning/build-reliable-ai-agents-with-amazon-bedrock-agentcore-evaluations/)
- [Build highly scalable serverless LangGraph multi-agent systems in AWS with Amazon Bedrock AgentCore](https://aws.amazon.com/blogs/machine-learning/build-highly-scalable-serverless-langgraph-multi-agent-systems-in-aws-with-amazon-bedrock-agentcore/)
- [Evaluating AI agents: Real-world lessons from building agentic systems at Amazon](https://aws.amazon.com/blogs/machine-learning/evaluating-ai-agents-real-world-lessons-from-building-agentic-systems-at-amazon/)
