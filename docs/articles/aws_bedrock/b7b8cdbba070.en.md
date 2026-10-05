---
vendor: aws_bedrock
title: Building ambient agents with Amazon Bedrock AgentCore: From event-driven signals to human-in-the-loop workflows
original_title: Building ambient agents with Amazon Bedrock AgentCore: From event-driven signals to human-in-the-loop workflows
url: https://aws.amazon.com/blogs/machine-learning/building-ambient-agents-with-amazon-bedrock-agentcore-from-event-driven-signals-to-human-in-the-loop-workflows
date: 2026-10-01
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 762357639474
---

## [Artificial Intelligence](https://aws.amazon.com/blogs/machine-learning/)

# Building ambient agents with Amazon Bedrock AgentCore: From event-driven signals to human-in-the-loop workflows

Teams that process documents at scale know the routine: files land in storage, someone notices, opens each one, decides what it needs, and routes it for review. Monitoring alerts queue up the same way, waiting for a person to act on them. The hours lost to manual triage are the operational problem ambient agents solve. Imagine a document lands in your Amazon Simple Storage Service (Amazon S3) bucket and within seconds a job appears on your Jobs page, ready to run (or already running if you configured it that way). The agent analyzes the file, surfaces the findings, and asks you for approval before taking the next step. The event itself is the prompt. That is an ambient agent: it responds to event streams, pauses for human input through a single `ask_human` tool when it needs to, and resumes from where it left off once the human answers.

Figure 1: Overview of an ambient agent responding to an event on AgentCore Runtime and pausing for human input

Most AI agent experiences today follow a different pattern: a user opens a chat interface, types a prompt, and waits for a response. That works for one-time questions, but it limits the agent to one conversation at a time and requires a human to describe what happened before anything can act on it. For scenarios where agents should react to events happening across your infrastructure (file uploads, database changes, scheduled tasks, system alerts), that chat-only model breaks down.

[Ambient agents](https://blog.langchain.com/introducing-ambient-agents/) describe a different paradigm, one that LangChain among others has articulated. Instead of waiting for users to initiate conversations, ambient agents listen to an event stream and act on it, potentially handling many events in parallel. They aren’t solely triggered by human messages, and multiple agents can run simultaneously. Crucially, they aren’t fully autonomous: a production design pays careful attention to when the agent pauses to interact with humans. When a signal fires, the agent executes its workflow and only interrupts a human when clarification, approval, or review is needed. This human-in-the-loop component lowers the stakes for deploying agents to production, builds user trust, and lets agents learn and improve over time through feedback.

Organizations running on AWS already have the event-driven infrastructure in place: Amazon S3 event notifications, Amazon EventBridge rules, AWS Lambda triggers, and Amazon DynamoDB streams. The missing piece is connecting those event sources to intelligent agents that can reason about what happened, act, and loop in humans when the situation calls for it. Fully automated pipelines like [AWS Step Functions](https://aws.amazon.com/step-functions/) can orchestrate workflows but can’t reason through ambiguity or ask clarifying questions. Chat-based agents can reason but require someone to start the conversation. Ambient agents bridge this gap.

[Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/) is a platform to build, connect, and optimize agents at scale, with any framework or model. AgentCore Runtime provides the execution environment that makes this pattern work: container-based agent hosting with support for long-running workloads, built-in session isolation, and integration with Amazon Bedrock foundation models. AgentCore Runtime supports sessions long enough to cover the signal → agent → human-in-the-loop (HITL) flow shown here. The reference implementation caps each agent turn at the Lambda 15-minute timeout, which is more than enough headroom in practice. Combined with AWS Lambda for event processing and Amazon DynamoDB for state management, the result is a fully serverless ambient-agent platform.

In this post we walk through the pattern end-to-end on Amazon Bedrock AgentCore. You will come away understanding:

- How an Amazon S3 or scheduled event becomes a job that an agent runs on AgentCore Runtime, with or without a human in the loop.
- How a single `ask_human` tool plus a canonical response envelope is enough to support the full range of human-in-the-loop interactions.
- What you get from the reference sample, and what you write on top for your own use case.

## Prerequisites

Before deploying the reference implementation, make sure you have the following in place:

- An AWS account with permissions to create AWS Identity and Access Management (IAM) roles, Lambda functions, DynamoDB tables, S3 buckets, Amazon Simple Queue Service (Amazon SQS) queues, Amazon API Gateway APIs, Amazon CloudFront distributions, Amazon Cognito user pools, Amazon Elastic Container Registry (Amazon ECR) repositories, and Bedrock AgentCore runtimes. Administrator access on a sandbox account is a good starting point.
- The [AWS Command Line Interface (AWS CLI)](https://docs.aws.amazon.com/cli/) configured with credentials for that account and a default AWS Region of `us-east-1` (the sample defaults are wired up for that Region).
- The [AWS Cloud Development Kit (AWS CDK)](https://docs.aws.amazon.com/cdk/) v2 installed and bootstrapped in your account and Region (`cdk bootstrap`).
- [Docker](https://www.docker.com/) installed and running locally. The agent container is built and pushed to Amazon ECR as part of deployment.
- Python 3.11 or later for the backend Lambda functions and the agent build, and `Node.js` 18 or later for the React frontend.
- Access to the Anthropic Claude Sonnet 4.5 model in Amazon Bedrock in your target Region. If you haven’t used Bedrock before, follow [Manage access to Amazon Bedrock foundation models](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html) (FMs) to enable the model. Model availability varies by AWS Region. Check the Amazon Bedrock documentation for the current list of models supported in your target Region. Switching models is a one-line config change later.

## Understanding ambient agents

Before we get into the architecture, it helps to look at what makes an ambient agent different from a typical chatbot and at the building blocks the rest of the post relies on: the event-driven trigger model, the ambient signal abstraction, and the single human-in-the-loop tool that ties them together.

### Event-driven compared to user-initiated agents

User-initiated agents follow a request-response pattern:

```
User → Prompt → Agent → Response → User
```

Ambient agents follow an event-driven pattern:

```
Event → Signal → Agent → [Optional human interaction] → Action
```

The key difference is the trigger mechanism. Ambient agents are activated by system events rather than explicit user requests, which makes them a natural fit for document-processing pipelines, monitoring and alerting, scheduled analysis, and multi-step workflows that need approval gates along the way.

### Ambient signals: The trigger mechanism

An ambient signal is a configuration that maps an event source to an agent. When the event occurs, the platform automatically creates a job for the agent. What happens next depends on one setting on the signal:

- With `autoExecute: false` (the default), the job lands on the Jobs page in `idle` status and waits for a human to review and run it. This is the safe, review-first flow you want when a signal could fire on unknown input or when the agent has high-stakes tools available.
- With `autoExecute: true`, the signal processor enqueues the job straight onto the worker queue, the agent runs immediately, and a human is only pulled in if the agent itself calls `ask_human`. This is the fully autonomous flow.

The pattern covers several signal event sources. The reference sample ships the first two. The rest are extension points you add by writing a new handler Lambda function and a corresponding form field on the Signals page:

- **Amazon S3 file uploads** (ships): Trigger when files are uploaded to specific buckets and prefixes.
- **Scheduled events** (ships): Trigger agents on a cron-like schedule. Driven by jobs carrying `jobType: "scheduled"` rather than by a signal on the Signals page.
- **API webhooks** (extension point): Respond to external system notifications.
- **Database changes** (extension point): React to Amazon DynamoDB streams or Amazon Relational Database Service (Amazon RDS) events.

### Human-in-the-loop: One tool, one envelope, one view

Ambient agents need structured ways to interact with humans. In this sample the agent surfaces those interactions through a single tool (`ask_human`) and returns a canonical response envelope. In that envelope, `status` is one of `completed`, `interrupted`, or `error`, and the matching field is `result`, `question`, or `error`. The platform additionally threads `session_id` and `job_id` through every response so continuation turns can be correlated. Those are correlation metadata, not part of the core contract your agent must implement. When the agent returns `interrupted`, the platform moves the job into `interrupted` status and sets its `requiresAction` flag to `true`. The reference React frontend surfaces these on the **Interrupted** tab of the Jobs page with a warning indicator on each row, so there is no separate review queue to poll. The same Jobs view shows pending questions, proposed actions awaiting approval, final results, and failed jobs, giving a user one place to see everything their agents are doing instead of monitoring multiple chat windows or email threads.

The same mechanism supports several prompting patterns that a reader may recognize from the wider agents literature: a Notify turn where the agent simply reports a result, a Question turn where it asks for clarification, a Review turn where it proposes an action and waits for `APPROVE` / `REJECT` / `MODIFY`, and an Error turn where the failure is captured on the job record and the user decides whether to retry. These are conventions for how the agent writes its question, not separate runtime modes. At the platform level there is exactly one code path and exactly one envelope.

Figure 2: The Notify, Question, and Review human-in-the-loop patterns, all surfaced through the ask_human tool

## Architecture overview

The platform is a small set of serverless components stitched together by an event pipeline. This section walks through the end-to-end flow first, then describes each component in turn.

Events flow through the platform end-to-end as follows. Amazon S3 emits an `s3:ObjectCreated` notification, which a Signal Processor Lambda function receives. The Signal Processor queries a global secondary index (GSI) on the ambient-signals table to find any matching signal for the event bucket, then creates a job record for each match. The API tier (or the scheduler) enqueues the job onto an Amazon SQS queue. The same Job Execution Lambda function that serves the API path also drains the queue through an attached SQS event source, invokes the agent on Amazon Bedrock AgentCore Runtime, and writes results (and any human-input requests) back to Amazon DynamoDB. A React frontend served from Amazon S3 through Amazon CloudFront polls a small Amazon API Gateway and Lambda tier for updates and lets the user respond to pending interactions.

The major components are:

- **Amazon S3** with event notifications serves as the entry point for signals when files are uploaded. Prefix and suffix filters are pushed down into the bucket’s notification configuration so the signal processor is only invoked for events that could plausibly match a signal.
- **Amazon SQS** decouples the API Gateway request from the agent call. A job-execution queue holds pending work. A dead-letter queue (DLQ) captures messages the worker can’t process after the configured number of retries.
- **Three pipeline Lambda functions** carry the event from intake to agent (a separate management tier behind API Gateway is described later in this section):  *Signal Processor* matches incoming events to configured signal definitions and creates jobs. *Job Execution* has two entry paths in one Lambda function: an API handler that enqueues messages, and an SQS worker that consumes them and invokes AgentCore Runtime with the job context. *Scheduler* fires on a one-minute cron and enqueues due scheduled jobs onto the same SQS queue.
- **Amazon Bedrock AgentCore Runtime** runs agent code in isolated containers and supports long-running workloads.
- **Amazon DynamoDB** stores the agent registry, job records, ambient signal definitions, chat threads, conversation history, and Powertools idempotency records. Conversation messages are appended atomically with `UpdateItem` + `list_append` so concurrent writers do not clobber each other.
- **Five management-tier Lambda functions behind Amazon API Gateway** expose the REST API the frontend consumes (`agent_management`, `job_management`, `signal_management`, `chat_management`, `conversation_management`), plus a `chat_execution` worker Lambda that `chat_management` invokes asynchronously so chat API calls return immediately. See [Production deployment](https://aws.amazon.com/cn/blogs/machine-learning/building-ambient-agents-with-amazon-bedrock-agentcore-from-event-driven-signals-to-human-in-the-loop-workflows/#production-deployment) for how they are provisioned.
- **A React frontend** served from Amazon S3 through Amazon CloudFront provides the Agent Management UI where users monitor jobs, chat with agents, respond to questions, and review pending actions.

Figure 3: Event flow from Amazon S3 through Amazon SQS and AWS Lambda to AgentCore Runtime, with state in Amazon DynamoDB and a React frontend

## Building the event infrastructure

With the architecture in mind, the next step is wiring up the event source that turns an Amazon S3 upload into an agent job. This section creates the bucket, points its event notifications at the Signal Processor Lambda function, and walks through how the processor matches events against configured signals.

### Setting up the Amazon S3 signal trigger

Create the Amazon S3 bucket and configure event notifications that drive the Signal Processor:

```
aws s3 mb s3://amzn-s3-demo-bucket-$(date +%s)
```

The bucket is configured to send `s3:ObjectCreated:*` events directly to the Signal Processor Lambda function. In this sample the notification configuration is installed dynamically by the `signal_management` Lambda function when a signal is created or updated, so adding a new signal for a new prefix doesn’t require a redeploy.

### Signal Processor Lambda function

The Signal Processor receives Amazon S3 events, finds matching signal definitions in DynamoDB, and creates a job per match. At its heart the handler is the shape shown in the following example. The real handler in `backend/functions/multi_agent/signal_processor.py` also uses AWS Lambda Powertools for structured logging and idempotency, queries the `bucketName-signalId-index` GSI on the signals table, applies the prefix and suffix checks configured on each signal, and writes a `signal_triggered` job row.

```
def process_s3_signal(event):
    """Process S3 file-upload events and create agent jobs."""
    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        for signal in find_matching_signals(bucket, key):
            create_agent_job(signal, {"bucket": bucket, "key": key})
```

### Signal configuration data model

Signals are stored in DynamoDB with this structure:

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

You only set `configuration.bucketName` when creating a signal through the API. The top-level `bucketName` shown in the preceding example is populated by the platform. DynamoDB GSI partition keys can’t be nested inside a map attribute, so `signal_management` mirrors `configuration.bucketName` out to a top-level `bucketName` on every write so the `bucketName-signalId-index` GSI can fan out to matching signals on every Amazon S3 event.

The `autoExecute` flag is the single switch that decides whether the agent fires autonomously or a human reviews the job first. The Signals form in the Agent Management UI exposes it as a checkbox alongside the familiar `enabled` setting, so changing the behavior is a quick edit without touching code or the database.

Figure 4: The Signals page with the autoExecute toggle on a signal definition

## Deploying agents on AgentCore Runtime

Amazon Bedrock AgentCore Runtime hosts the agent container and exposes it through an `InvokeAgentRuntime` API that the worker Lambda function calls on every job. This section walks through the agent layout that ships with the sample, the configuration that drives it, and the small orchestrator that turns LangGraph tool calls into the platform’s response envelope.

### Agent packaging and structure

AgentCore Runtime provides a container-based execution environment for agents, so you can bring any Python agent framework. The sample uses a modular design:

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

### Agent configuration

`config.yaml` defines agent behavior, tools, and the system prompt. The sample defaults to Anthropic Claude Sonnet 4.5 on Amazon Bedrock for this walkthrough, a fit for the multi-step tool calling and long-context reasoning the human-in-the-loop workflow relies on. Switching to Claude Haiku, Amazon Nova, or another tool-calling model available on Amazon Bedrock (availability varies by Region) is a one-line change to `model_id` in the following configuration. `max_iterations: 10` gives the graph enough headroom for around ten model-to-tool round trips before it halts (the orchestrator doubles the value to compute LangGraph’s recursion limit, since each round trip traverses two graph nodes), which covers the multi-step tool use the sample’s S3, calculator, and `ask_human` tools expect. The file also contains an `execution:` block (loop-detector, circuit-breaker, session-cache thresholds) omitted here for brevity. See `agent/config.example.yaml` for the full file.

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

### Core agent implementation

The agent is built on `langchain.agents.create_agent`, a tool-calling agent compiled as a LangGraph. LangChain handles the orchestration layer because it brings pre-built tool-calling patterns, a broad open ecosystem of integrations, and APIs many teams already know, while AgentCore Runtime supplies the managed hosting, session isolation, and scaling underneath. The two layers are complementary. The platform wrapper around the graph does three things: it builds the message list for the turn (including any conversation history and, for signal-triggered jobs, the Amazon S3 bucket and key that fired the signal so the model can pick up the file without being told), it invokes the graph, and it scans the tool output for the `ask_human` sentinel so a tool call can be turned into an `interrupted` response.

In its simplest form (the full version in `agent/core/agent_core.py` also handles per-session history caching, loop detection, and an execution trace), the orchestrator is this:

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

### Deploying the agent

Deploy the agent to AgentCore Runtime using the provided script:

```
cd agent

# Configure AWS settings in .env and any overrides in config.yaml.
# Then build the container, push to Amazon ECR, and register it with
# Bedrock AgentCore Runtime.
./deploy_agent.sh
```

The script returns an Agent Runtime Amazon Resource Name (ARN) which the backend stores in the agent registry so the Job Execution Lambda function can invoke it.

## State management with DynamoDB

Amazon DynamoDB is the system of record for everything that needs to outlive a single Lambda invocation: which agents are registered, which jobs are in flight, the conversation history that gives an agent continuity across turns, and the signal definitions and chat threads the UI reads. The next subsections describe the table layout, the session model, and how the Job Execution Lambda function uses both to drive a job to completion.

### Database design

The state layer is backed by DynamoDB. The core tables exercised in this post are:

**Agent registry table** (one record per registered agent runtime):

```
{
  "agentId": "agent-123abc",
  "agentName": "Document Analyzer",
  "agentArn": "arn:aws:bedrock-agentcore:us-east-1:123456789012:agent-runtime/abc123",
  "status": "active"
}
```

**Job registry table** (one record per agent invocation). With the default `autoExecute: false`, a new signal-triggered job lands here in `idle` status, waiting for a user to choose Execute:

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

While a job is running the worker flips `status` to `busy`. If the agent pauses by calling `ask_human`, `status` becomes `interrupted` and `requiresAction` becomes `true`, which surfaces the job on the Jobs page’s Interrupted tab.

**Conversation store table** (full message history per session, with a 30-day time to live (TTL)):

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

Additional tables exist for ambient signals, chat threads, and Powertools idempotency records. Scheduled execution reuses the job-registry table through a `jobType` and `nextRun` GSI rather than having its own table.

### Session management

Sessions provide conversation continuity across job executions and chat turns. The `conversation_management` Lambda function owns DynamoDB persistence: every turn (human + AI pair) is appended to the session with an atomic `UpdateItem` + `list_append` so two concurrent writers on the same session can’t clobber each other, and a 30-day TTL takes care of cleanup.

### Job execution with conversation continuity

The Job Execution Lambda function has two entry paths. The API path sends an SQS message (adding Powertools idempotency and a `userId` ownership check) and returns 202 Accepted immediately, so the frontend never waits for the model. The SQS worker path is where the real work happens: it loads conversation history, folds any human response into a continuation prompt, calls AgentCore Runtime, and writes the result back. That worker looks roughly like this:

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

Figure 5: Job execution sequence, from API enqueue through the SQS worker and AgentCore invocation to the DynamoDB write-back

## Implementing human-in-the-loop patterns

The agent snippet earlier returned a sentinel-based `interrupted` envelope when the graph produced an `ask_human` tool call. This section zooms in on the `ask_human` tool itself and shows exactly how the orchestrator catches that sentinel without breaking the reasoning loop.

### The human input tool

The core of human-in-the-loop functionality is the `ask_human` tool. It doesn’t raise an exception: because LangGraph’s tool node captures tool exceptions as error observations and feeds them back to the model, the tool instead returns a sentinel string. The orchestrator detects the sentinel on the `ToolMessage` stream after the graph finishes and converts it into an `interrupted` response. Per-invocation state (metrics, session ID, and so on) isn’t a tool argument. The orchestrator binds it on a `ContextVar` that tools read through `current_execution_state.get()`, which keeps concurrent invocations inside the same container isolated from each other.

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

### Agent-side usage

The agent uses the tool naturally as part of its tool-calling loop. For example, when analyzing an invoice with multiple line items the agent may call:

```
Tool call: ask_human
Arguments: {
  "question": "This invoice spans three expense categories. Should I analyze Hardware, Services, or Software Licenses in detail?"
}
```

The tool returns the sentinel, the orchestrator stops the graph, persists the question as the latest AI turn in the conversation store, and surfaces an `interrupted` job to the UI. When the user replies, the Job Execution Lambda function invokes the agent again with the answer folded into a continuation prompt.

## Building the Agent Management UI

The Agent Management UI is the human side of the platform: where users browse jobs, answer pending questions, and chat with agents directly. It’s a React single-page application that talks to the same REST API the rest of the post has been describing. The next two subsections cover the layout and the user experience flow that ties signals, jobs, and human input together.

### Frontend architecture

The frontend is a React and Cloudscape Design single-page application served from Amazon S3 behind Amazon CloudFront. It exposes a five-tab navigation:

- **Workflows**: A gallery and CRUD surface for workflow-level definitions that group agents and signals.
- **Chat**: A standalone chat page (`/chat`, `/chat/:threadId`) for user-initiated conversations with a registered agent.
- **Agents**: Manages registered agent runtimes (name, ARN, capabilities, status).
- **Jobs**: Lists all jobs with status filters and a detail view that includes an interactive Chat tab, an execution trace, and metadata.
- **Signals**: Defines and toggles ambient signals. The shipped form covers Amazon S3 prefix and suffix filters and schedules. Webhook, Amazon EventBridge, and DynamoDB stream fields are added when you wire those extension points.

The same chat component is reused by both the standalone Chat page and the Jobs detail Chat tab. While a job is running (`status === "busy"`), the panel polls `/conversations/:sessionId` on a short interval so turns from the agent or from a second browser tab show up within a few seconds. After the job settles, polling stops. Because it’s the same component in both places, a user can freely converse with an agent from the Jobs detail view while a job is active. They are not limited to answering a single pending question.

### User experience flow

- **Signal fires**: A new job appears in the Jobs list with `jobType: "signal_triggered"`. If the signal has `autoExecute: false` (the default) the job lands in `idle` and the user runs it manually. With `autoExecute: true` the worker is already drafting a response by the time the list refreshes. User-initiated jobs carry `jobType: "user_initiated"` and render with a different badge so you can tell the two apart at a glance.
- **Human input requested**: Any job that calls `ask_human` moves to the Interrupted tab and its `requiresAction` flag flips to `true`, which renders a warning indicator on the row.
- **Responding**: The detail view surfaces a Provide Response button so the user can answer the pending question without leaving the job context.
- **Execution feedback**: Status transitions (`idle` → `busy` → `completed` | `interrupted` | `error`) are polled and reflected in the list and in the Chat tab header.
- **Interactive chat**: The Jobs detail Chat tab and the `/chat` page both render full conversation history and accept new user messages, so humans can answer pending questions or nudge the agent with additional context without leaving the UI.
- **Response submission**: Sending a message calls the Chat Execution or Job Execution Lambda function, which invokes the agent on AgentCore Runtime with the job context and the human response folded into the next turn.
- **Completion and audit**: The final result is stored on the job record and the full conversation history is preserved on the session, available in the Chat tab for audit and re-use.

Authentication is handled by Amazon Cognito and an API Gateway `CognitoUserPoolsAuthorizer` (see `backend/infrastructure/multi_agent_stack.py`).

Real-time updates are implemented as lightweight polling of the conversation and job endpoints, so there is no WebSocket infrastructure to run.

## Extending the sample

The reference implementation is deliberately small so you can see the contract before you start adding to it. This section describes what ships in the box, what you build on top, and where to plug in new event sources or tools.

### What ships in the sample compared to what you build

Before extending, it helps to know where the seams are. This sample is a reference implementation of the ambient-agent pattern, not a turnkey product. What ships out of the box:

- **The platform**: Signal intake, the SQS-backed job pipeline, the HITL interrupt mechanism, job and conversation state in DynamoDB, the React UI with the Jobs page and Chat surfaces, and AgentCore integration with Cognito-backed auth.
- **A reference agent**: A containerized LangChain agent with four tools (calculator, `ask_human`, `list_s3_files`, `read_s3_file`) and a generic system prompt. Useful for validating the pipeline end-to-end, not for solving your business problem out of the gate.
- **One signal source wired through the Signals UI** (Amazon S3 file uploads, matched by bucket, prefix, and suffix), plus a job-level scheduler that runs on a one-minute cron for jobs created with `jobType: "scheduled"`. Adding new signal types such as webhooks, Amazon EventBridge events, or DynamoDB streams requires extending the `signalType` enum in both the backend and the Signals page form.

What you build on top, and what the platform expects from each:

- **Your agent**: A containerized Python agent tailored to your domain, with its own tools and its own system prompt. It must speak the two conventions the platform relies on: return the three-status envelope (`completed`, `interrupted`, or `error` with the matching `result`, `question`, or `error` field) and use the `ask_human` sentinel to request human input. That is roughly 50 lines of adapter code around whatever agent framework you prefer.
- **New signal types** if Amazon S3 uploads and cron are not enough: A new handler Lambda function that queries the signals table and writes a `signal_triggered` job row (shown in the following template), plus a corresponding form field on the Signals page so users can configure it.
- **New tools** for your agent: A new module under `agent/tools/`, a registration entry in `agent/core/tool_factory.py`, and an enable flag in `config.yaml`. The orchestrator and HITL flow do not change. Any tool that returns a string participates in the same graph.

In short: the platform does the plumbing, you bring the brain. The three places you will write code (agent logic, tool implementations, and new signal handlers) all slot into the existing contract without touching the rest of the stack.

### Configuration over code

Enabling a new capability for an existing agent is a config change rather than a code change. The agent’s `config.yaml` toggles tools on or off and supplies their descriptions, so adding a new Amazon S3 prefix handler or a new calculator mode doesn’t require rebuilding the container. Signal definitions live in DynamoDB and are edited from the Signals page in the UI.

### Adding a new signal type

Signals today trigger on Amazon S3 events and on cron schedules. Adding a new type (a webhook, an Amazon EventBridge rule, a DynamoDB stream, a Kafka topic) follows the same three-step contract. The downstream pipeline is signal-agnostic: everything from the SQS worker through the AgentCore call through the UI treats all `signal_triggered` jobs the same, so you only need to write the bridge from your event source into a job row.

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

You add the Lambda function and its API Gateway route in the CDK stack, extend `signalType` in the frontend’s TypeScript union and the Signals page form, and the rest (the Jobs page UI, the `ask_human` interrupt handling, the conversation persistence, the `autoExecute` toggle, the contract tests) all apply without change. Like the production Signal Processor, a real webhook handler would add AWS Lambda Powertools idempotency so a retried delivery doesn’t create duplicate jobs.

## Production deployment

After the pieces fit together locally, the next step is provisioning them in an account. The platform deploys as a single AWS CDK stack. The following subsections describe what that stack creates, the deploy commands, the metrics that matter when it is running, and the security and scaling defaults the sample ships with.

### Infrastructure as code

The whole platform is an AWS CDK stack defined in `backend/infrastructure/multi_agent_stack.py`. For storage and messaging, it provisions the DynamoDB tables (agent registry, job registry, conversation store, ambient signals, chat threads, idempotency records) with pay-per-request billing and point-in-time recovery, plus the SQS job-execution queue and its dead-letter queue.

For compute and delivery, it provisions the three pipeline Lambda functions from the Architecture section (Signal Processor, Job Execution, Scheduler), the five management-tier Lambda functions that back the REST API (`agent_management`, `job_management`, `signal_management`, `chat_management`, `conversation_management`) and the `chat_execution` worker Lambda that `chat_management` invokes asynchronously, a Cognito-backed REST API, and the CloudFront distribution that serves the React frontend.

IAM grants flow directly from the code: DynamoDB `grant_read_write_data` on each table, SQS `grant_send_messages` and `grant_consume_messages` as appropriate, and a scoped `bedrock-agentcore:InvokeAgentRuntime` policy on the worker role.

### Deployment steps

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

### Monitoring and observability

The Lambda functions emit custom CloudWatch metrics under the `AmbientAgents` namespace for the events that matter in this pattern: signal matches, jobs enqueued, jobs completed, jobs interrupted, and jobs errored. Combined with the default Lambda and SQS metrics (invocation count, errors, queue depth, DLQ depth), these give you a dashboard where the signal → job → agent → human cycle is visible end-to-end. Set an alarm on DLQ depth as the first line of defense against silent failures.

### Security best practices

- **IAM least privilege**: Grant only the permissions required by each Lambda function (reads on its own table, targeted `bedrock-agentcore:InvokeAgentRuntime`, targeted Amazon S3 prefixes).
- **Encryption at rest**: All DynamoDB tables use AWS-managed keys. Amazon S3 buckets use S3-managed encryption. CloudFront logs live in a dedicated logging bucket.
- **Encryption in transit**: All API Gateway endpoints and CloudFront distributions require HTTPS. Amazon S3 bucket policies enforce SSL.
- **Audit logging**: AWS CloudTrail captures API calls across the stack. DynamoDB streams can be enabled on the job table for richer job-lifecycle audit.
- **Responsible AI**: Apply Amazon Bedrock Guardrails to agent inputs and outputs so content filters, denied topics, and contextual grounding checks run before findings surface on the Jobs page or reach a reviewer through the `ask_human` prompt. This protects the human-in-the-loop interaction and keeps agent outputs grounded in the source documents.

### Scaling strategies

- **Lambda concurrency**: Reserve concurrency for the Job Execution worker Lambda function to cap downstream Bedrock invocations at a predictable per-account ceiling.
- **DynamoDB capacity**: Pay-per-request is the default. Switch to provisioned capacity with auto scaling when traffic patterns stabilize.
- **Cost optimization**: Use DynamoDB TTL to retire old conversations automatically, Amazon S3 lifecycle policies to age out processed documents, and CloudWatch metric filters to track per-agent model invocation cost.

## Clean up

To avoid ongoing charges after you are finished evaluating the sample, tear the stack back down in the reverse order it was created.

First, delete the agent runtime from Amazon Bedrock AgentCore so the container stops being billed:

```
aws bedrock-agentcore delete-agent-runtime \
    --agent-runtime-arn <your-agent-runtime-arn>
```

Next, empty the Amazon S3 buckets the stack provisions (the documents bucket, the frontend hosting bucket, and the CloudFront logging bucket) so CloudFormation can delete them:

```
aws s3 rm s3://<amzn-s3-demo-documents-bucket> --recursive
aws s3 rm s3://<amzn-s3-demo-frontend-bucket>  --recursive
aws s3 rm s3://<amzn-s3-demo-logs-bucket>      --recursive
```

Then destroy the AWS CDK stack itself, which removes the Lambda functions, API Gateway, CloudFront distribution, DynamoDB tables, SQS queues, Cognito user pool, and IAM roles:

```
cd backend
cdk destroy --all
```

Finally, delete the Amazon ECR repository created by the agent deploy script if you do not plan to redeploy:

```
aws ecr delete-repository \
    --repository-name ambient-agent \
    --force
```

If you enabled Amazon Bedrock model access only for this walkthrough and no longer need it, you can revoke it from the **Model access** page of the Amazon Bedrock console.

## Summary

Ambient agents shift AI automation from “wait for a user” to “respond to signals”. Time-to-action drops from hours to seconds, and around-the-clock monitoring becomes possible without constant human attention. Each agent operates independently with isolated sessions, so the platform handles many concurrent events in parallel without coordination overhead. Humans stay in the loop only when their input is truly needed. The unified Jobs page removes context switching across multiple tools, and full conversation history means you never lose track of what an agent did or why it paused.

### When to use ambient patterns

The following use cases describe the ambient-agent pattern in general. The reference sample ships the plumbing for Amazon S3 and the scheduler today. Webhooks, database changes, and external integrations are extension points you wire up on top.

The pattern is a strong fit whenever an event in your environment should drive work that a model can reason about and a human should occasionally weigh in on. Document-processing pipelines are the canonical example: a file lands, an agent reads it, summarizes it, and asks for approval before acting. Monitoring and alerting flows benefit from the same shape, with the agent triaging an alert and asking a human only when escalation is needed. Scheduled processing, analysis, and reporting fit naturally on the cron path, and any multi-step workflow that needs an approval gate or a human checkpoint along the way maps cleanly onto the `ask_human` interrupt.

There are also workloads where ambient agents are the wrong tool. Real-time chat applications belong in a traditional chat agent that is purpose-built for low-latency conversational turn-taking. Simple request-response APIs do not need an agent at all. A plain API endpoint is faster, cheaper, and easier to reason about. And for purely deterministic workflows that do not need large language model (LLM) reasoning, AWS Step Functions is still the right choice. Note that ambient agents with `autoExecute: true` already cover the fully autonomous case if you want LLM reasoning without a human gate.

### Next steps

Clone the [reference implementation](https://github.com/aws-samples/sample-ambient-agent) and follow the top-level README for deployment and configuration.

Further reading:

- [Amazon Bedrock AgentCore documentation](https://docs.aws.amazon.com/bedrock/)
- [LangChain documentation](https://python.langchain.com/)
- [AWS CDK documentation](https://docs.aws.amazon.com/cdk/)

Start small. Pick a single use case (document processing or a monitoring alert) and expand from there. Clone the sample, point it at your own event source, and see how much routine work the Jobs page takes off your plate.

## About the authors
