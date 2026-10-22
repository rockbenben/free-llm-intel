---
vendor: aws_bedrock
title: 5 production challenges in multi-agent systems and how Deep Insight solved them
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/5-production-challenges-in-multi-agent-systems-and-how-deep-insight-solved-them
date: 2026-10-21
lang: en
captured: 2026-10-22
extractor: readability-v1
status: ok
body_sha: 1c6cf5de1498
---

## [Artificial Intelligence](https://aws.amazon.com/blogs/machine-learning/)

# 5 production challenges in multi-agent systems and how Deep Insight solved them

Building a multi-agent system is now pretty straightforward. Taking it to production is where the real challenges begin. Thanks to open source frameworks and cloud services, you can set up an agent in a matter of days. A few tool calls, a few lines of prompt, and you have something that looks impressive. But the moment teams try to move beyond a pilot and into real business applications, they hit a familiar wall. If you’ve ever tried to put an agent into production, these frustrations will sound familiar:

*Why doesn’t the agent follow our business logic, skip validation steps, or catch edge cases?*

You tweak the prompt, add more examples, swap out the model. The same problems keep coming back. That’s because agents don’t follow a fixed sequence of instructions. They make their own judgments based on context. Instructions alone aren’t enough. You need to design how the agent thinks, when it verifies, and what it does when things go wrong. This is exactly why it’s become critical to go beyond prompt engineering alone and design the agent’s entire cognitive architecture and execution flow.

To tackle these challenges head-on, the AWS Solutions Architecture team built [Deep Insight](https://github.com/aws-samples/sample-deep-insight), a production-grade multi-agent system. In this post series, we share what the team learned firsthand while building Deep Insight across three posts. We will walk through how we applied Context Engineering techniques proposed by Anthropic (multi-agent architecture, structured note-taking, human-in-the-loop, and more) in a real production environment. We also cover the trade-offs we encountered along the way (with code) and the operational insights we gained from deploying and running this agent on AWS.

## Blog series overview

- Part 1: 5 production challenges in multi-agent systems and how Deep Insight solved them.
- Part 2: Beyond the context window: Context Engineering techniques and how Deep Insight applied them.
- Part 3: Harness engineering in practice: moving Deep Insight from dev to production.

This is Part 1 of a three-part series. It defines the five core challenges any production multi-agent system must solve and shows how each layer of the stack addresses them, from [Strands Agents SDK](https://strandsagents.com/) and [Amazon Bedrock](https://aws.amazon.com/bedrock/) to [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/), [Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/create-application-load-balancer.html), and [AWS Fargate](https://aws.amazon.com/fargate/). Parts 2 and 3 cover Context Engineering and production deployment.

## Introducing Deep Insight

Deep Insight is a multi-agent system that turns complex data analysis into automated insights. Given a CSV file and a natural-language prompt, a hierarchy of specialized agents (Coordinator, Planner, Supervisor, Coder, Validator, Reporter, and Tracker) collaborates on the analysis. Together they load the data, run analyses, generate charts, validate calculations, and produce a professional report (.docx) with citations.

We will explore the architecture in detail later. First, let’s see it in action. For the demo, we feed advertising data from a fictional food company, Yummy Food (`yummy-food-market.csv`) with a column definitions file (`column_definitions.json`), and provide the prompt: *Analyze this from a sales and marketing perspective, generate charts and insights, and produce a .docx report.* Deep Insight generates an analysis plan, presents it to the user for approval, and, once approved, executes the analysis.

|  | **Content** |
| --- | --- |
| Input | CSV data file (`yummy-food-market.csv`) + Column definitions file (`column_definitions.json`) |
| Example prompt | “Analyze this from a sales and marketing perspective, generate charts and insights, and produce a .docx report.” |
| Output | DOCX report (two versions, one with citations and one without) plus chart graphics (PNG) |

The [Deep Insight web demo video](https://www.youtube.com/watch?v=tMN29C4nam0) that follows shows the full workflow, from uploading data and reviewing the analysis plan to real-time streaming and downloading the finished report.

## How can I try it?

Deep Insight is open sourced on [GitHub](https://github.com/aws-samples/sample-deep-insight) with a full setup guide, and offers three deployment options spanning development to production.

The first is the [Self-Hosted version](https://github.com/aws-samples/sample-deep-insight/tree/main/self-hosted), which runs locally through the CLI. It’s optimized for rapid iteration with full code-level access to every agent, prompt, and workflow. It sets up in about 10 minutes, which makes it well suited to development. (A Self-Hosted demo video is available on [YouTube](https://www.youtube.com/watch?v=pnyvBo98E1k).)

The second is the [Web version](https://github.com/aws-samples/sample-deep-insight/tree/main/deep-insight-web), a browser-based UI for uploading data, reviewing analysis plans (Human-in-the-Loop, or HITL), and downloading reports, all without writing code, making it accessible for non-developers. (The preceding demo video shows the Web version in action.)

The third is the [Managed AgentCore version](https://github.com/aws-samples/sample-deep-insight/tree/main/managed-agentcore), a production deployment option powered by Amazon Bedrock AgentCore, a platform to build, connect, and optimize agents at scale, with any framework or model. This version deploys the agents on AgentCore runtime, a capability of Amazon Bedrock AgentCore. The system runs entirely within a private virtual private cloud (VPC), with a custom Code Interpreter hosted separately on AWS Fargate, and agents run concurrently in isolated per-user environments. It’s the right choice when you need session isolation and private VPC deployment. Part 3 covers its deployment and operations in detail.

All three share the same multi-agent architecture, so an agent validated in development deploys to production as-is.

## Solution overview

Building a production multi-agent system takes more than good prompts. You need the right technology stack and infrastructure to address how agents collaborate, how they reason, how you deploy them, where they safely execute code, and how you monitor operational health. Deep Insight solves problems across these five key areas. Because the agents generate both code and report content, we also cover responsible AI controls for production in Solution detail 2.

| **Challenge** | **Technology** | **Approach** |
| --- | --- | --- |
| “How do we control execution flow across multiple agents?” | Strands Agents SDK | Use Strands’ Graph pattern to define execution order between agents and implement human-in-the-loop branching. Use Strands’ Agents as Tools pattern so the Supervisor can invoke specialized agents (Coder, Validator, Reporter, Tracker) as tools on demand. |
| “Which large language model (LLM) should each agent use?” | Amazon Bedrock | Select the right Claude model for each role: Haiku for basic routing, Opus for planning, Sonnet for execution. |
| “How do we reliably operate a finished agent in production?” | Amazon Bedrock AgentCore | Managed runtime with monitoring, session isolation, and private VPC deployment. |
| “How do we mitigate the security issues of executing AI-generated code?” | AWS Fargate + Application Load Balancer (ALB) | Per-session ephemeral sandbox containers for isolated code execution through a custom Code Interpreter. |
| “How do we monitor and manage the system?” | Amazon DynamoDB + Amazon Simple Notification Service (Amazon SNS) + Amazon Cognito | Admin dashboard and failure alerting system. |

The following architecture diagram (Figure 1) illustrates this at a glance. The green boxes represent the Strands Agents multi-agent structure, which addresses challenges 1 and 2 from the preceding table. We will cover this in detail in the upcoming Solution detail 1: Multi-agent system design section. The remaining infrastructure components shown in the diagram address challenges 3, 4, and 5, which we will walk through in Solution detail 2: Production deployment and operations.

![Deep Insight architecture: the Strands Agents multi-agent layer on Amazon Bedrock AgentCore, with an Application Load Balancer routing code execution to AWS Fargate containers in a private VPC](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21081-1-1.png)

Figure 1: Solution architecture

## Solution detail 1: Multi-agent system design

Deep Insight uses a multi-agent architecture in which eight agents collaborate to produce one high-quality deliverable. Each agent works in its own independent context, performs only its specialized tasks, and passes only compressed results onward.

![Hierarchical multi-agent structure where the Coordinator and Planner feed the Supervisor, which orchestrates the Coder, Validator, Reporter, and Tracker agents](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21081-2-1.png)

Figure 2: Multi-agent structure

The Coordinator routes user requests, the Planner breaks tasks into discrete steps, the Plan Reviewer collects user feedback, and the Supervisor invokes the appropriate specialized agents according to the plan. The Coder writes and executes data analysis code, the Validator verifies calculations, the Reporter generates the final report, and the Tracker tracks progress. We will explain this across three layers:

- [1st Layer] Coordinator to Planner to Plan Reviewer: Request analysis and execution plan creation.
- [2nd Layer] Supervisor: Specialized agent orchestration.
- [3rd Layer] Coder, Validator, Reporter, Tracker: Specialized task execution.

Two key patterns from the Strands Agents SDK are combined to control execution flow across these agents. First, the [Graph pattern](https://strandsagents.com/docs/user-guide/concepts/multi-agent/graph/) defines the execution order and flow of agents as a directed graph. Requests flow Coordinator, Planner, Plan Reviewer, then Supervisor, with a conditional branch looping back to the Planner on revision requests. Determining the next step by condition makes complex workflows like HITL and error handling straightforward. Second, the [Agents-as-Tools pattern](https://strandsagents.com/docs/user-guide/concepts/multi-agent/agents-as-tools/) lets the Supervisor invoke specialized agents (Coder, Validator, Reporter, Tracker) as tools only when needed. Each works in an independent context and returns only results, minimizing context usage while preserving domain expertise.

This section shows how the architecture solves routing, planning, and orchestration.

### [1st Layer] Coordinator to Planner to Plan Reviewer

This layer turns a user request into an approved execution plan.

#### 1.1 Coordinator (routing): Not every request needs expensive orchestration

The Coordinator is the entry point for user requests. It handles basic greetings directly and routes complex tasks like data analysis to the Planner with a handoff_to_planner marker.

The key design decision is model selection: because the Coordinator only classifies, it uses the lightweight Claude Haiku, avoiding Opus-level costs on basic greetings and delivering fast responses.

```
# builder.py: conditional edges for routing decisions
builder.set_entry_point("coordinator")
builder.add_edge("coordinator", "planner", condition=should_handoff_to_planner)
```

Routing conditions come from the Coordinator’s prompt: any request needing tools, reasoning, or multi-step thinking goes to the Planner.

#### 1.2 Planner (plan creation): Complex analyses need decomposition before execution

In Deep Insight’s multi-agent structure, the Planner agent plays the critical role of distributing tasks across agents. Before substantive work begins, it breaks large tasks into smaller steps, and each specialized agent executes them one at a time, keeping each agent’s context small.

The Planner uses a Claude Opus model with Extended Thinking turned on to develop the analysis plan. It organizes the plan into a `[ ]` checklist format that specifies concrete tasks assigned to each agent, stored in a `full_plan` variable. It breaks the request into 5–10 clear steps, as shown in the following example:

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

The Plan Reviewer is a HITL node that presents the plan to the user and collects *approval or revision feedback*. If there is feedback, it loops back to the Planner to revise the plan. If approved, it hands the task off to the Supervisor. A maximum revision count (`MAX_PLAN_REVISIONS`) is set to prevent infinite loops.

```
# builder.py: Plan Reviewer's bidirectional conditional edges
builder.add_edge("plan_reviewer", "planner", condition=should_revise_plan)
builder.add_edge("plan_reviewer", "supervisor", condition=should_proceed_to_supervisor)
builder.set_max_node_executions(25)
```

In the Web version, the Plan Reviewer shows a browser modal where the user reads the plan and approves it or enters revision feedback. A 300-second countdown auto-approves the plan if no response arrives.

![Deep Insight web UI showing the Plan Reviewer modal where the user approves or revises the generated analysis plan](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21081-3-1.png)

Figure 3: Plan Reviewer agent execution in the web UI

Without planning, the agent decides everything at runtime, a mid-course correction invalidates previous work, and users have no visibility into progress. With the Planner and Plan Reviewer, the user can review and revise the plan, monitor progress in real time, and re-execute only a failed step.

### [2nd Layer] Supervisor (orchestrator): Specialized agents need a conductor

The Supervisor executes the Planner’s `full_plan` in order, invoking the Layer 3 agents (Coder, Validator, Reporter, Tracker) as tools registered on it through Tool Use.

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

The Supervisor’s system prompt defines strict workflow rules:

- Mandatory execution order: Coder, Tracker, Validator, Tracker, Reporter, Tracker: after each agent runs, Tracker is invoked to track progress, letting the Supervisor manage overall task state.
- Section completion rule: The Supervisor does not move to the next agent until all checklist items for the current agent are marked [x].
- Context preservation: The Supervisor passes clues and full_plan variables to each tool agent, maintaining full context and preventing information loss.

### [3rd Layer] Coder, Validator, Reporter, Tracker: Division of labor drives quality

Each Layer 3 agent (Coder, Validator, Reporter, Tracker) is wrapped as a `PythonAgentTool` and receives Tool Use calls from the Supervisor. Each is created as an independent `Agent()` instance in the Strands SDK with its own system prompt, model ID, and toolset.

| **Agent** | **Role** | **Tools** | **Key Output** |
| --- | --- | --- | --- |
| Coder | Data analysis, chart generation, insight derivation | write_and_execute_tool, bash_tool, file_read, skill_tool | *.png charts, `calculation_metadata.json` |
| Validator | Numerical calculation re-verification, citation generation | write_and_execute_tool, bash_tool, file_read | `citations.json`, validation_report.txt |
| Reporter | DOCX report generation | write_and_execute_tool, bash_tool, file_read | final_report.docx, final_report_with_citations.docx |
| Tracker | Checklist progress status updates | None (LLM reasoning only) | Updated full_plan |

The Supervisor invokes Tool Use calls in this order, based on the Planner’s checklist:

- Coder – Loads data, writes and runs analysis code, produces PNG charts, accumulates results in all_results.txt, and leaves `calculation_metadata.json` for verification.
- Tracker (1st pass) – Updates completed checklist items from [ ] to [x], which the Supervisor uses to decide whether to proceed.
- Validator – Re-performs each calculation in `calculation_metadata.json` from the source data. Matches within 0.01 pass, mismatches are flagged. Verified calculations go to `citations.json` for the Reporter to cite.
- Tracker (2nd pass) – Reflects the Validator’s completion status in the checklist.
- Reporter – Reads all_results.txt and `citations.json` to generate the final DOCX report in two versions, with and without citations.
- Tracker (3rd pass) – Reflects the final completion status of all tasks.

Tracker runs after every agent so the Supervisor can track progress and enforce the completion rule (no moving on until all items are [x]). Because it updates the checklist with LLM reasoning and no tools, it adds little overhead.

### Per-agent LLM model configuration

Deep Insight tailors the model and settings to each agent’s role. This isn’t a model selection. It’s an architectural decision to optimize cost and quality.

| **Agent** | **Model** | **Extended Thinking** | **Prompt Caching** | **Role** |
| --- | --- | --- | --- | --- |
| Coordinator | Haiku | Disabled | No | Fast routing: cost minimization |
| Planner | Opus | Enabled (~8,192 tokens) | No | Deep thinking: high-quality planning |
| Supervisor | Sonnet | Disabled | Yes | Execution orchestration: caching for cost savings |
| Coder | Sonnet | Disabled | Yes | Code generation/execution: caching effective for repeated calls |
| Validator | Sonnet | Disabled | No | Numerical verification: different data each time, caching unnecessary |
| Reporter | Sonnet | Disabled | Yes | Report generation: caching effective for long prompts |
| Tracker | Sonnet | Disabled | No | Status updates: lightweight tasks, caching unnecessary |

The Supervisor, Coder, and Reporter agents use Prompt Caching to cache their system prompts and tool definitions, reducing input token costs by up to 90 percent on repeated calls. The Coordinator runs only once, and the Validator and Tracker run with different contexts each time, so caching is ineffective for them and stays disabled. This selective caching strategy is a deliberate cost/performance trade-off.

## Solution detail 2: Production deployment and operations

If Solution detail 1 defined *what the system does*, this section defines where and how it runs safely. Everything from here on covers infrastructure decisions for production operations. Specifically, this section covers the secure execution environment for LLM-generated code, and operational visibility for the team.

### 1. Code execution: LLM-generated code needs a secure execution environment

The Coder agent writes and runs Python for data analysis. In the Self-Hosted version it runs locally through `subprocess.run()`, but in production (AgentCore) security and isolation are essential. Running LLM-generated code directly on a production server is risky: the model might delete system files, exhaust resources in an infinite loop, or reach other users’ analysis data. Deep Insight solves this with per-session ephemeral containers on AWS Fargate and ALB. These components don’t run in isolation. As shown in Figure 1, AgentCore runtime, the ALB, and the Fargate tasks all run inside the same private VPC. VPC endpoints connect them to Amazon Simple Storage Service (Amazon S3), Amazon Bedrock, and Amazon Elastic Container Registry (Amazon ECR) without traversing the public internet. Security groups restrict which components can reach the Code Interpreter containers. AWS Identity and Access Management (IAM) roles scope each component to only the AWS resources it needs. Amazon CloudWatch collects container logs and observability data from AgentCore Observability, a capability of Amazon Bedrock AgentCore.

- Custom container Docker image: A pre-optimized sandbox with fonts, system libraries, and Python packages for the multi-agent system.
- Container isolation: Each analysis session gets an independent Fargate container in a private VPC subnet with no direct internet access.
- 2-step execution: LLM-generated code is base64-encoded, sent over HTTP, written to a file (Step 1), then executed through subprocess (Step 2).
- Session affinity: ALB sticky session cookies route an agent back to the same container even when it executes code multiple times.
- Artifact management: Charts, reports, and logs upload to Amazon S3 when analysis completes. Containers terminate automatically after one hour.

Container isolation protects the infrastructure, but it doesn’t govern what the agents generate. The Validator agent re-verifies calculations. It doesn’t detect prompt-injection instructions hidden in uploaded data or screen LLM-generated text for harmful or ungrounded content. For production deployments, we recommend adding Amazon Bedrock Guardrails as a responsible AI control: apply content filters and prompt attack detection to user prompts and uploaded data, and apply contextual grounding checks to agent outputs so that report text stays grounded in the source data and verified calculations.

### 2. Operations and monitoring: Teams need visibility

A production system isn’t complete with code alone. The team must assess system health, diagnose issues, and review results, so Deep Insight provides a Web UI and an Ops dashboard.

#### Web UI (deep-insight-web)

A FastAPI-based web interface that communicates with the backend through the AgentCore Native Protocol (`boto3.invoke_agent_runtime()`). Users upload data and enter a prompt, then monitor progress through Server-Sent Events (SSE) streaming. When the plan is generated, a modal lets the user approve or give revision feedback (HITL). The finished report can be downloaded directly. Both Korean and English are supported.

![Deep Insight web interface for uploading data, entering a prompt, and downloading the generated report](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21081-4-1.png)

Figure 4: Deep Insight web version screenshot

#### Ops dashboard (deep-insight-web/ops)

The Ops dashboard is optional. Deep Insight works fine without it, but it adds these features for teams that need them:

- Task tracking: All analysis task metrics, including status, token usage, and elapsed time, are recorded in Amazon DynamoDB.
- Failure alerting: When an analysis fails, an email is immediately sent to administrators through Amazon SNS.
- Admin dashboard: A dedicated admin dashboard is protected by JSON Web Token (JWT) authentication through Amazon Cognito for secure task monitoring.

![Deep Insight Ops dashboard listing analysis tasks with status, token usage, and elapsed time](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21081-5-1.png)

Figure 5: Deep Insight Ops dashboard screenshot

![Deep Insight Ops dashboard detail view showing metrics for a single analysis task](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/19/ml-21081-6.png)

Figure 6: Deep Insight Ops dashboard detail view

## Extending the Deep Insight architecture

Deep Insight’s multi-agent architecture isn’t confined to the single domain of data analysis report generation. The following two examples demonstrate that the hierarchical orchestration design principles remain effective in entirely different domains.

### Case 1: LG Electronics: Agentic AI-powered marketing insight extraction system

LG Electronics’ Korea Sales Division built ChatInsight on the same multi-agent architecture as Deep Insight, where data analysis requests had taken 2–3 weeks and lost intent between marketers and data scientists. The Coordinator routes by complexity, the Planner tracks tasks, and the Supervisor orchestrates the Coder and Reporter, with inter-agent state passed cumulatively through an all_results.txt file. Analysis that took 3 days now takes 30 minutes, a 288x productivity improvement. Marketers who don’t know SQL can let the agent explore data and propose strategies (see the [LG Electronics Agentic AI Insight Extraction System on the AWS Tech Blog](https://aws.amazon.com/ko/blogs/tech/lge-agentic-report-automation/)).

![LG Electronics ChatInsight architecture using the same Coordinator, Planner, Supervisor, Coder, and Reporter multi-agent pattern as Deep Insight](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21081-7-1.png)

Figure 7: LG Electronics Agentic AI marketing insight system architecture

### Case 2: TechRecon: AI-powered technology reconnaissance agent (re:Invent 2025)

Presented at AWS re:Invent 2025 (session SNR203), TechRecon applies Deep Insight’s architecture to technology strategy. Given a company and sector, a Researcher gathers technology trends, the Coder analyzes, the Validator verifies, and the Reporter produces a Landscape Analysis and a Technical Position Paper. The architecture is nearly identical to Deep Insight, built with the Strands Agents SDK Graph pattern and Extended Thinking and Prompt Caching, with Researcher replacing Coder as the primary execution agent. It shows the design is a general-purpose pattern: swap the agents’ roles and prompts, and the same orchestration structure solves entirely different problems.

![TechRecon output showing a Landscape Analysis and a Technical Position Paper produced by the reconnaissance agent](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/14/ML-21081-8-1.png)

Figure 8: TechRecon results

(Read more: [TechRecon GitHub](https://github.com/aws-samples/sample-tech-recon) | [AWS re:Invent Session Video](https://www.youtube.com/watch?v=NwkH_F3yUiY))

## Conclusion

Building an agent that works in production is not a matter of model capability. It’s a matter of architecture. Deep Insight offers a proven answer:

- Workflow management: The Strands Agents SDK’s Graph pattern defines execution order between agents and implements HITL branching, while the Agents-as-Tools pattern lets the Supervisor invoke specialized agents only when needed.
- Reasoning engine: We assign Claude models from Amazon Bedrock by role (Haiku, then Opus, then Sonnet) to optimize cost and quality.
- Deployment: Amazon Bedrock AgentCore provides a managed runtime with session isolation, private VPC deployment, and OpenTelemetry observability.
- Code execution: Application Load Balancer plus Amazon Elastic Container Service (Amazon ECS) on Fargate isolates LLM-generated code execution in per-session ephemeral sandbox containers, preventing security issues such as system file access, resource exhaustion, and unintended data disclosure.
- Operations: The Web UI’s SSE streaming and the Ops dashboard (DynamoDB + Cognito + SNS) provide visibility across the entire team.

LG Electronics’ marketing insight system and the TechRecon case at re:Invent 2025 validated these design principles.

In Part 2, we examine four layers of Context Engineering techniques for overcoming context-window limits on top of this architecture, from architecture-level isolation to prompt design, tool optimization, and verification safeguards, comparing our approach with Anthropic’s engineering research.

Deep Insight is open source. Explore the code and extend it for your own domain.

- [GitHub](https://github.com/aws-samples/sample-deep-insight)
- Workshop: Deep Insight Workshop ([English](https://catalog.us-east-1.prod.workshops.aws/workshops/ee17ba6e-edc4-4921-aaf6-ca472841c49b/en-US) | [Korean](https://catalog.us-east-1.prod.workshops.aws/workshops/ee17ba6e-edc4-4921-aaf6-ca472841c49b/ko-KR))

## About the authors
