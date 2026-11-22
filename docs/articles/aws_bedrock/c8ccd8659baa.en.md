---
vendor: aws_bedrock
title: Evaluating multi-agent systems for explainability and helpfulness with Amazon Bedrock AgentCore
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/evaluating-multi-agent-systems-for-explainability-and-helpfulness-with-amazon-bedrock-agentcore
date: 2026-10-05
lang: en
captured: 2026-10-06
extractor: readability-v1
status: ok
body_sha: 9555946d7521
---

## [Artificial Intelligence](https://aws.amazon.com/blogs/machine-learning/)

# Evaluating multi-agent systems for explainability and helpfulness with Amazon Bedrock AgentCore

A critical challenge that emerges as multi-agent systems move from experimentation to production is making sure that these systems are consistently helpful, accurate, and explainable in real-world scenarios. Enterprises are increasingly adopting multi-agent systems to solve complex, real-world problems that require reasoning across data sources, tools, and business constraints. From supply chain planning to financial analysis and customer operations, these systems go beyond simple question answering. They coordinate multiple specialized agents to make decisions, execute workflows, and generate actionable recommendations.

While large language models can generate fluent responses, enterprise applications require much deeper guarantees, where agents must follow instructions reliably, select the right tools, respect constraints, and provide clear reasoning behind their outputs.

[Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) is a platform to build, connect, and optimize agents at scale, with any framework or model. [Amazon Bedrock AgentCore Evaluations](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations.html), a capability of Amazon Bedrock AgentCore, is designed to address this challenge as a fully managed capability for assessing agent performance across development and production, so teams can measure accuracy, task success, and behavior across multiple quality dimensions. Traditional evaluation approaches that focus only on model response quality are insufficient for agentic systems, where correctness depends on tool selection, workflow execution, and adherence to business constraints. In addition to evaluation, production deployment of agentic systems requires responsible AI controls. [Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/) provides configurable safeguards such as content filtering, denied topic detection, and grounding validation that complement the evaluation framework. While evaluations assess agent quality after execution, Guardrails enforce safety constraints during execution. In this post, we focus on operationalizing this evaluation framework with Amazon Bedrock AgentCore Evaluations support for both built-in evaluators and custom evaluators. Built-in evaluators offer pre-defined assessments for common quality dimensions such as helpfulness, task success, and instruction following, so teams can quickly baseline agent performance without additional setup. However, enterprise use cases require deeper, domain-specific validation. Custom evaluators address this, so you can define business-aware checks.

We also focus specifically on explainability as a first-class evaluation dimension. We demonstrate how built-in evaluators can assess general response clarity. We showcase how custom evaluators are used to verify that agents explicitly articulate decision rationale, reference supporting data or tool outputs, and explain tradeoffs such as cost versus service level. By combining these evaluators, we show how AgentCore Evaluations can move beyond surface-level response quality and provide structured, measurable insights into how and why agents arrive at their decisions.

To make these concepts concrete, the following sections walk through a reference architecture and implementation that demonstrates how these components work together in practice.

## Solution overview

For this post, we use a fictitious global retail company called AnyCompany Retail, a multinational retailer operating ecommerce channels, regional fulfillment centers, distribution centers, and thousands of physical stores. AnyCompany experiences frequent inventory imbalances: some regions face stockouts during promotions, while others carry excess inventory. Transportation teams must also balance delivery speed, carrier capacity, and cost. The company wants an agentic assistant that can help planners optimize inventory allocation, recommend distribution adjustments, analyze inventory health, and simulate routing or fulfillment scenarios.

You will build and evaluate a multi-agent supply chain decisioning system using [Strands Agents SDK](https://strandsagents.com/), [Amazon Bedrock AgentCore MCP Server](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp.html) and Amazon Bedrock AgentCore Evaluations. The solution uses Strands Agents with an orchestrator agent and four specialized sub-agents: an optimization agent, distribution agent, routing agent, and analytics agent. Each agent runs on [Amazon Bedrock AgentCore runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html) with [Amazon Bedrock AgentCore memory](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html) and [Amazon Bedrock AgentCore Observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html) enabled.

The orchestrator agent receives the planner’s request and delegates work to specialized agents exposed as tools. The optimization agent calls MCP tools backed by mock [Amazon API Gateway](https://aws.amazon.com/api-gateway/) REST interfaces that return optimization decisions. The distribution agent calls recommendation APIs to suggest inventory rebalancing across fulfillment centers, stores, and digital channels. The routing agent calls logistics APIs to recommend carrier and route options and the analytics agent answers supply chain diagnostics questions. This solution uses foundation models on Amazon Bedrock for the agent loop. For model availability by Region, refer to [Supported models by AWS Region in Amazon Bedrock.](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html)

The solution uses built-in evaluators that assess general quality dimensions such as helpfulness and task completion. It also provides custom evaluators that assess supply-chain-specific behavior such as constraint satisfaction, route feasibility, SQL correctness, inventory grounding, and explanation quality. AnyCompany can evaluate both the language quality of the response and the business validity of the agent’s decision.

The solution supports both on-demand and online modes with Amazon Bedrock AgentCore Evaluations. The on-demand mode is meant for development benchmarking, regression testing, and continuous integration and continuous delivery (CI/CD) gates. The online mode is for continuous production monitoring and alerts. Both modes help you close the loop and act on feedback from your users. The same custom evaluators (such as the constraint satisfaction, route feasibility, SQL correctness, and explainability evaluators from your supply chain solution) used for on-demand evaluations are repurposed with an OnlineEvaluationConfig object that references the Amazon Resource Names (ARNs) of the evaluators and specifies a sampling rate (for example, 1–10% of production traces) along with optional session filters. The service then automatically reads traces from AgentCore Observability, scores them and streams results to [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/) dashboards and alarms. In this post, you will use the on-demand mode to test the solution.

The following architecture diagram illustrates the various components of our solution.

Figure 1: Architecture of the multi-agent supply chain decisioning solution

## Evaluation framework

In this post, you will use a three-layer evaluation approach for multi-agent systems that progressively builds enterprise trust. The approach follows a clear progression starting with built-in evaluators for general quality then adding custom evaluators for business accuracy and finally layering explainability evaluators for trust and auditability.

The first layer uses built-in evaluators requiring no setup. We apply Helpfulness as a universal baseline plus a second agent-specific evaluator targeting each agent’s primary failure mode: Tool Selection Accuracy for the orchestrator, Response Relevance for optimization and distribution, Instruction Following for routing, and Faithfulness for analytics.

The second layer adds custom evaluators encoding domain-specific business rules: constraint satisfaction for optimization, data grounding for distribution, route feasibility for routing, SQL correctness for analytics, and plan coherence for orchestration. These validate business validity: did the recommendation respect budget limits, use real inventory data, and produce operationally correct outputs?

The following table maps the two built-in evaluators and custom evaluator selected for each agent that you will implement here. The second built-in evaluator targets each agent’s primary failure mode, while the custom evaluator encodes domain-specific business rules that validate operational correctness.

| **Agent** | **Built-in evaluators** | **Custom evaluators** |
| --- | --- | --- |
| Orchestrator agent | Helpfulness; Tool Selection Accuracy | Plan coherence evaluator: Did it combine sub-agent outputs into a valid, non-contradictory recommendation? Tool trajectory evaluator: Did it route to the correct sub-agent? |
| Optimization agent | Helpfulness; Response Relevance | Constraint satisfaction evaluator: budget, inventory coverage (demand ≤ qty ≤ 2× demand), and warehouse capacity constraints. Key performance indicator (KPI) attainment evaluator: fill-rate/revenue improvement target met. |
| Distribution agent | Helpfulness; Response Relevance | Recommendation groundedness evaluator: recommendation is grounded in current inventory/demand data. Risk impact evaluator: recommendation improves stockout/overstock risk. |
| Routing agent | Helpfulness; Instruction Following | Route feasibility evaluator: route respects delivery window, cost, carrier capacity, and region constraints. Service level agreement (SLA) evaluator: expected delivery meets target service level. |
| Analytics agent | Helpfulness; Faithfulness | SQL correctness evaluator: query matches user intent. Data-grounding evaluator: response is supported by Amazon Relational Database Service (Amazon RDS) query results. No unsupported claims evaluator. |

## Explainability

The third layer of our evaluation approach applies explainability evaluators as distinct, cross-cutting checks across the agents. These independently assess whether agents articulate decision rationale, cite supporting evidence from tool outputs, explain which constraints shaped the response, articulate trade-offs between competing objectives, clarify why specific sub-agents were invoked, and disclose assumptions when data is incomplete. By separating explainability into its own evaluation layer, we can independently measure transparency. A recommendation can be accurate but unexplainable (passing custom evaluators but failing explainability), giving teams actionable signals about whether agents need better reasoning articulation rather than better decision logic.

The following table defines the six independent explainability evaluators that you implement here and that are applied across agents as a cross-cutting layer. These assess whether agents articulate reasoning, cite evidence, explain constraints and trade-offs, and disclose assumptions. They are measured separately from accuracy so teams can distinguish unexplainable-but-correct responses from well-explained-but-wrong ones.

| **Evaluator** | **Agents** | **What it checks** |
| --- | --- | --- |
| Decision rationale quality | All | Did the agent explain why it made the recommendation? |
| Evidence attribution | Analytics, Distribution, Routing | Did it cite the data fields, API response, or SQL result used? |
| Constraint reasoning | Optimization, Routing | Did it explain which constraints shaped the final response? |
| Trade-off explanation | Optimization, Distribution, Routing | Did it explain the trade-offs among cost, service level, and inventory risk? |
| Tool-use explainability | Orchestrator | Did it explain why each sub-agent or MCP tool was invoked? |
| Assumption disclosure | All agents | Did it clearly state assumptions when data was incomplete? |

## Prerequisites

Before you deploy this solution, set up your development environment with the following tools.

- Install the [AWS Command Line Interface (AWS CLI)](https://aws.amazon.com/cli)
- Install the [AWS Serverless Application Model (AWS SAM) CLI v1.100.0+](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- Install [Docker v20.x+](https://docs.docker.com/engine/install/)
- Install [Node.js v18.x+](https://nodejs.org/)
- Install [Python v3.11+](https://www.python.org/downloads/)

## Dependencies

The Strands Agents implementation also needs to have the following dependencies that are packaged in the DockerFile:

- strands-agents # Strands Agents multi-agent framework
- strands-agents-tools # Strands agent tools and utilities
- requests # HTTP library for API calls
- bedrock-agentcore # Amazon Bedrock agent core functionality
- boto3 # AWS SDK for Python (Boto3)

## Deploy and run the solution

The solution is available for download from our [GitHub repo](https://github.com/aws-samples/sample-agentic-genai-agentcore/tree/main/aws-genai-evaluations-supply-chain) and provides a single step deployment to deploy and access the solution in your AWS environment:

```
# Edit terraform.tfvars: set vpc_id and runtime_subnet_azs
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply
```

The outputs include runtime ARNs, AnyCompany Retail API URL, evaluator API URL, and memory ARN.

## Run the solution

Follow these steps to run the solution:

The test_client/ folder contains a Python script that invokes the deployed Supply Chain agent with 20 sample queries (5 per sub-agent) to validate end-to-end functionality. Each category runs as a multi-turn session, and session IDs are printed at the end for use with the evaluators API.

```
cd test_client
pip install -r requirements.txt
cd terraform
terraform output supply_chain_arn
```

**Run all queries (20 total, 4 sessions)**

```
cd test_client
python test_agent.py --runtime-arn "<supply_chain_arn>" --region <your_region>
```

### Run specific sub-agent categories

```
#Only optimization queries (1 session, 5 turns)
python test_agent.py --runtime-arn "<supply_chain_arn>" --category optimization
#Only routing and analytics (2 sessions, 5 turns each)
python test_agent.py --runtime-arn "<supply_chain_arn>" --category routing analytics
```

The test client prints each query and the full agent response. At the end it prints the session IDs for use with the evaluators.

**Create and run evaluations**

The test_evaluators/ folder contains scripts to run evaluations against agent sessions. These evaluations run asynchronously and the results are saved as markdown files in S3.

You must invoke the supply chain decisioning multi-agent solution first as outlined earlier to generate agent sessions with traces and note down the session IDs printed at the end of the test client run. Finally wait 3-5 minutes after running the solution for traces to propagate to CloudWatch.

```
cd test_evaluators
pip install -r requirements.txt
cd terraform
terraform output evaluators_api_url
```

**Create custom evaluators**

```
python test_evaluator.py --api-url "https://<evaluators-api-url>" create
```

This registers custom evaluators and prints their IDs. Save these for use with the run command.

**Run evaluations**

Pass a comma-separated list of evaluator IDs (custom or built-in). At least 1 is required:

```
# Run custom + built-in evaluators
python test_evaluator.py --api-url "https://<evaluators-api-url>" run \
--agent-id "supply_chain_orchestrator_agent-<id>" \
--session-id "<session-id-from-test-client>" \
--evaluators " sc_optimization_constraint-<id>,sc_distribution_groundedness-<id>,Builtin.Correctness,Builtin.GoalSuccessRate"
```

The API returns 202 immediately. Results are saved asynchronously to S3 at:

```
s3://<amzn-s3-demo-agent-source-bucket>/evaluations/<session-id>/<timestamp>/EvaluationResults.md
```

**Delete evaluators**

```
python test_evaluator.py --api-url "https://<evaluators-api-url>" delete \
--evaluator-ids "sc_optimization_constraint-<id>,sc_distribution_groundedness-<id>"
```

## Run an optimization evaluation

Now that you understand the evaluation framework and have deployed the solution, let’s walk through a focused end-to-end evaluation of the optimization agent. This walkthrough demonstrates how to combine a custom business-accuracy evaluator (Layer 2) with explainability evaluators (Layer 3) to assess both the correctness and transparency of optimization decisions.

**Step 1: Run optimization queries**

First, invoke the test client with only the optimization category to generate a focused session:

```
cd test_client
python test_agent.py --runtime-arn "<supply_chain_arn>" \
--category optimization \
--region <your_region>
```

This runs 5 optimization queries as a multi-turn session. The agent processes requests such as “What is the optimal inventory level for prod-001 over the next 30 days?” Each query requires the optimization agent to call MCP tools, retrieve demand forecasts, and produce stocking recommendations that respect budget, inventory coverage, and warehouse capacity constraints. At the end of the run, the test client prints the optimization session ID.

**Step 2: Run the Constraint Satisfaction evaluator (Layer 2: business accuracy)**

With the optimization session generated, run the custom Constraint Satisfaction evaluator to validate whether the agent’s stocking recommendations respect business rules. This evaluator checks three constraints simultaneously:

- Budget: Does the incremental holding cost fit within remaining budget (budget_limit − budget_used)?
- Inventory coverage: Is the recommended level ≥ demand forecast (avoids stockout) and ≤ 2× demand (avoids excess)?
- Warehouse capacity: Does the recommended level fit within available warehouse space?

Run the evaluator along with the built-in Helpfulness and Response Relevance evaluators:

```
cd test_evaluators
python test_evaluator.py --api-url "https://<evaluators-api-url>" run \
--agent-id "supply_chain_orchestrator_agent-<id>" \
--session-id "<optimization-session-id>" \
--evaluators "sc_optimization_constraint-<id>,Builtin.Helpfulness,Builtin.ResponseRelevance"
```

The API returns HTTP 202 immediately. Evaluations run asynchronously. Results are saved to S3:

```
s3://<amzn-s3-demo-agent-source-bucket>/evaluations/<optimization-session-id>/<timestamp>/EvaluationResults.md
```

**Step 3: Run explainability evaluators (Layer 3: trust and auditability)**

After confirming that the optimization agent produces constraint-satisfying recommendations, the next question is: does it explain its reasoning? A recommendation can be accurate but opaque. Such a recommendation passes the constraint evaluator but fails to articulate why it chose a specific inventory level.

Using the same optimization session ID from Step 1, now run the two explainability evaluators that apply to the optimization agent:

- Decision Rationale Quality — Did the agent explain why it made the recommendation? (for example, “Recommending 1,500 units because demand forecast is 1,200 and we target a 1.25× safety factor”)
- Constraint Reasoning — Did the agent explain which constraints shaped the final response? (for example, “Budget allows up to 1,800 units but warehouse capacity limits us to 1,600, so we recommend 1,500”)

```
python test_evaluator.py --api-url "https://<evaluators-api-url>" run \
--agent-id "supply_chain_orchestrator_agent-<id>" \
--session-id "<optimization-session-id>" \
--evaluators "sc_decision_rationale-<id>,sc_constraint_reasoning-<id>"
```

These evaluators independently assess transparency. They are measured separately from accuracy.

**Interpreting the combined results**

By running all three evaluators against the same optimization session, you get a complete picture of agent quality across two dimensions:

| **Dimension** | **Evaluator** | **Question answered** |
| --- | --- | --- |
| Business accuracy (Layer 2) | Constraint Satisfaction | Are the recommendations operationally correct? |
| Explainability (Layer 3) | Decision Rationale Quality | *Why* does the agent make this recommendation? |
| Explainability (Layer 3) | Constraint Reasoning | *Which constraints* shaped the response? |

Table 3: Evaluation coverage across quality dimensions

This layered approach enables targeted improvements. If constraint satisfaction scores are high but explainability scores are low, the agent’s decision logic is sound, but its communication needs work. Conversely, if explainability is high but constraints are violated, the agent articulates reasoning well but applies incorrect logic. Each failure mode has a different remediation path, and the evaluation framework makes this distinction measurable.

## Clean up

To avoid recurring charges, clean up your AWS account in a single step after trying the solution.

```
terraform destroy
```

## Conclusion

In this post, we demonstrated how to build and evaluate a multi-agent supply chain decisioning system using Amazon Bedrock AgentCore Evaluations, with a focus on verifying that agent behavior is not only functional, but also helpful, accurate, and explainable. Using the AnyCompany Retail Group scenario, we showed how an orchestrator agent and specialized sub-agents collaborate to solve complex problems such as inventory allocation, distribution planning, routing optimization, and supply chain diagnostics, while integrating with enterprise data sources and APIs. As illustrated throughout the architecture, correctness in agentic systems goes beyond response quality. It depends on selecting the right tools, executing the correct workflow, adhering to business constraints, and grounding outputs in data.

By combining built-in evaluators with custom evaluators, teams can systematically validate both general response quality and domain-specific decision accuracy. Incorporating explainability-focused evaluators further make sure that agents clearly articulate their reasoning, reference supporting data, and explain tradeoffs in a way that business users can trust and act upon. This evaluation-driven approach enables continuous improvement using real execution data, establishes quality gates before production rollout, and provides a scalable framework for delivering consistent, transparent, and business-aligned multi-agent systems.

To get started, explore [Amazon Bedrock AgentCore Evaluations](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations.html) and apply these patterns to your own multi-agent applications. Find the complete source code in the [Amazon Bedrock AgentCore samples repository on GitHub.](https://github.com/awslabs/agentcore-samples/tree/main/06-workshops/07-AgentCore-evaluations) Begin by enabling observability, defining key evaluation dimensions for your use case, and incrementally introducing built-in and custom evaluators to measure what matters most.

To learn more, visit the [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) service page or get started directly in the [Amazon Bedrock console](https://console.aws.amazon.com/bedrock/).

**Related posts:**

- [Build reliable AI agents with Amazon Bedrock AgentCore Evaluations](https://aws.amazon.com/blogs/machine-learning/build-reliable-ai-agents-with-amazon-bedrock-agentcore-evaluations/)
- [Build highly scalable serverless LangGraph multi-agent systems in AWS with Amazon Bedrock AgentCore](https://aws.amazon.com/blogs/machine-learning/build-highly-scalable-serverless-langgraph-multi-agent-systems-in-aws-with-amazon-bedrock-agentcore/)
- [Evaluating AI agents: Real-world lessons from building agentic systems at Amazon](https://aws.amazon.com/blogs/machine-learning/evaluating-ai-agents-real-world-lessons-from-building-agentic-systems-at-amazon/)

## About the author
