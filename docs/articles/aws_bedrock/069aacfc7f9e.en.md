---
vendor: aws_bedrock
title: New agent skill: Amazon SageMaker optimized generative AI inference for your coding agent
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/new-agent-skill-amazon-sagemaker-optimized-generative-ai-inference-for-your-coding-agent
date: 2026-10-05
lang: en
captured: 2026-10-06
extractor: readability-v1
status: ok
body_sha: 8899b8aa1b95
---

## [Artificial Intelligence](https://aws.amazon.com/blogs/machine-learning/)

# New agent skill: Amazon SageMaker optimized generative AI inference for your coding agent

Engineers increasingly use coding assistance tools to accelerate their development workflows. Today, [Amazon SageMaker AI optimized generative AI inference](https://aws.amazon.com/blogs/machine-learning/amazon-sagemaker-ai-now-supports-optimized-generative-ai-inference-recommendations/) introduces the `aws-ai-ml` skill, available through the [Agent Toolkit for AWS](https://aws.amazon.com/products/developer-tools/agent-toolkit-for-aws/). This skill gives coding agents like [Kiro](https://kiro.dev/), Claude Code, and Codex deep expertise in inference optimization and benchmarking. Install the skill, and your existing agent can benchmark endpoints, recommend deployment configurations, compare performance runs, and generate executable SageMaker Python SDK v3 code on your behalf. The `aws-ai-ml` skill is a toolkit that plugs into any coding agent that supports the Model Context Protocol (MCP), turning it into a SageMaker AI inference optimization expert.

In this post, we walk through what the skill enables, how to set it up, and how it helps you move faster from model to production.

## The challenge: Bridging intent and infrastructure

Amazon SageMaker AI supports serverful hosting across real-time, batch, and asynchronous modes. It offers on-demand and reserved capacity, heterogeneous instances, virtual private cloud (VPC) isolation, automatic scaling, and integration with every SageMaker AI training path. The surface area is broad and deep, but most engineers do not arrive knowing which instance family or serving container will best serve their needs. They arrive with a use case: a performance target they want to hit, a cost envelope they need to stay within, or a model they need to evaluate before committing to production.

The agentic experience for SageMaker AI optimized generative AI inference closes this gap. You tell the agent what you want to accomplish, and it produces executable SageMaker Python SDK v3 code that you can review, modify, and run in your own environment. The agent asks targeted clarifying questions, generates code grounded in real benchmarks and measured performance data, and adapts to your business constraints the way a solutions architect would.

Throughout, you stay in control. Every step is visible in real time and expressed as code you can read and question. Nothing happens behind an opaque UI.

## Getting started

You can install the `aws-ai-ml` skill through the [Agent Toolkit for AWS](https://aws.amazon.com/products/developer-tools/agent-toolkit-for-aws/) on your local machine, or use it within an Amazon SageMaker Studio JupyterLab space. Either way, you can go from zero to a working conversation in 10 minutes.

### Option A: Use with any coding agent (Kiro, Claude Code, Codex, or any MCP-compatible agent)

**Step 1: Install the Agent Toolkit for AWS.** If you haven’t already, set up the Agent Toolkit. This requires AWS Command Line Interface (AWS CLI) 2.35+ and [uv](https://docs.astral.sh/uv/) installed.

```
aws configure agent-toolkit
```

This auto-detects your agents, installs skills, and configures the AWS MCP Server. For agent-specific setup (plugin install commands, MCP config), see the [Agent Toolkit for AWS getting started guide](https://aws.amazon.com/products/developer-tools/agent-toolkit-for-aws/).

**Step 2: Install the `aws-ai-ml` skill.** Add the SageMaker AI optimized generative AI inference skill to your agent:

```
npx skills add aws/agent-toolkit-for-aws/skills/aws-ai-ml
```

**Step 3: Confirm and begin.** Open your coding agent’s chat panel and ask: “What skills are available?” You should see `aws-ai-ml` listed. After you confirm, describe your intent in natural language. Your coding agent now has SageMaker AI inference optimization expertise built in.

**Prerequisites:** Your AWS credentials must have permissions to call SageMaker AI APIs (creating endpoints, running benchmark and recommendation jobs). The skill generates code that runs under your credentials. No additional AWS Identity and Access Management (IAM) configuration is needed for the skill itself.

**Note:** For Kiro and Claude Code, agents can discover skills at runtime. They can search for and load skills on demand through the [AWS MCP Server](https://aws.amazon.com/blogs/aws/the-aws-mcp-server-is-now-generally-available/), without any local installation. Ask your agent: “Search for AWS skills related to databases.” Refer to the [readme](https://github.com/aws/agent-toolkit-for-aws/tree/main/skills) for discovering skills at runtime.

### Option B: Use within Amazon SageMaker Studio

If you prefer to work inside a managed JupyterLab environment, you can use the skill in Amazon SageMaker Studio with a pre-configured image.

**Step 1: Open Amazon SageMaker Studio.** Navigate to Amazon SageMaker Studio in your target AWS account and AWS Region. Select your Studio domain and launch the Studio IDE from your user profile.

**Step 2: Create a JupyterLab space.** From the Studio landing page, choose **JupyterLab**, then choose **Create JupyterLab space**. Name the space (for example, `my-inference-opt`) and keep the sharing setting **Private** (skills only sync on private spaces). Under the **Image** menu, select the image that includes the SageMaker AI optimized generative AI inference skill. This image ships pre-configured with the `aws-ai-ml` agent skill and all necessary dependencies. Choose **Run space** and wait for it to boot (5–10 minutes the first time).

**Note:** Use a fresh space. A reused space with a locally modified skill version may not pick up the pre-configured image.

**Step 3: Open JupyterLab and launch a terminal.** After the space boots, open JupyterLab and choose **Terminal**.

**Step 4: Authorize your coding agent.** In the terminal, authenticate with your coding agent using your identity provider. For example, with Kiro:

```
kiro-cli login --license pro --identity-provider <your-IdP-start-URL> --region us-east-1 --use-device-flow
```

**Step 5: Confirm and begin.** Open your coding agent’s chat panel and ask: “What skills are available?” You should see `aws-ai-ml` listed. Once confirmed, describe your intent in natural language.

> Troubleshooting:
>         If the agent reports no skills are available, verify that your space is set to Private. You can also check from the terminal:

```
ls ~/.kiro/skills/
```

> If that directory is empty but /etc/sagemaker/skills/ contains the skill files, run restart-jupyter-server, refresh the page, and retry.

## What you can do

The agentic experience covers the following capabilities across the inference optimization lifecycle. You don’t need to know which capability to invoke. Describe what you want, and your agent figures out the next step or asks clarifying questions if anything is unclear.

### Benchmark an existing endpoint

If you already have a model deployed on a SageMaker AI endpoint, you can ask the agent to benchmark it. Tell the agent which endpoint you want to test, and it generates a Python notebook that runs a load test using the `Workload.synthetic()` and `start_benchmark()` APIs from the SageMaker Python SDK.

Before running any benchmark, the agent confirms that your endpoint is safe to load-test, because benchmarking drives real traffic to a live endpoint.

When the benchmark completes, you get a quantitative performance report with:

- **Throughput**: requests per second, output tokens per second.
- **Latency**: p50, p99, time-to-first-token, inter-token latency.
- **Concurrency**: number of simultaneous requests supported.

These are measured values from real load on real infrastructure, not estimates. The agent also recommends improvement mechanisms (such as prefill decoding) to boost performance.

**Example prompt:** *“Benchmark my Llama endpoint on SageMaker AI.”*

### Find the right instance type for your model

If you have a model and need to find the right instance type to deploy it on SageMaker AI, tell your agent. It doesn’t matter where your model lives or how you obtained it:

- **Fine-tuned or custom model in Amazon Simple Storage Service (Amazon S3)**: You trained or downloaded a model and stored it in S3. Provide the S3 URI and your optimization goal. Example prompt: *“I want to find the cheapest instance type to deploy my fine-tuned model on SageMaker.”*
- **Publicly available foundation model from [Amazon SageMaker JumpStart](https://aws.amazon.com/sagemaker/jumpstart/)**: You want to deploy a foundation model (FM) from the JumpStart catalog then provide the model ID. Example prompt: *“Find the best instance for model huggingface-reasoning-qwen3-8b on SageMaker AI.”*
- **Model on the [Hugging Face Hub](https://huggingface.co/models)**: You want to use a model hosted on Hugging Face. Provide the model name. For gated models (such as Llama variants), your agent surfaces the license terms and asks you to accept them and provide your Hugging Face token. Example prompt: *“I want to deploy a Llama model from Hugging Face Hub. What’s the cheapest option?”*

In every case, your agent generates code that evaluates your model against candidate instances and configurations, then presents ranked deployment options with concrete performance metrics: throughput, latency percentiles, time-to-first-token, and concurrency. You choose based on your cost and performance requirements.

### Compare benchmark runs

If you ran multiple benchmarks (for example, before and after a configuration change, or across two instance types), you can ask the agent to compare them. Provide the two benchmark job names, and the agent generates a comparison that computes deltas across key metrics: throughput, latency percentiles, and time-to-first-token.

The results show percentage changes where positive means better, giving you a single, interpretable summary of whether your change improved performance, degraded it, or had no meaningful effect.

If one of the benchmark runs doesn’t exist, the agent offers to run it first before proceeding with the comparison.

**Example prompt:** *“I have two benchmark runs and I want to compare them. Which one is faster?”*

## Benchmark results

This table compares two deployed models on the same benchmark workload (512/256 tokens, concurrency 4). The Δ% column shows how much faster Model B (Qwen3-8B) is than Model A (Qwen3-1.7B) on each metric. A positive value means Model B is better.

| **Metric** | **Qwen3-1.7B (Model A)** | **Qwen3-8B (Model B)** | **Δ%** |
| --- | --- | --- | --- |
| Output token throughput | 188.2 tokens/s | 271.2 tokens/s | +44.1% ✅ |
| Per-user throughput | 47.5 tokens/s | 69.4 tokens/s | +45.9% ✅ |
| Request throughput | 0.736 req/s | 1.08 req/s | +46.7% ✅ |
| Inter-token latency | 20.9 ms | 14 ms | +33.0% ✅ |
| Request latency | 5,382 ms | 3,658 ms | +32.0% ✅ |
| Time to first token | 67.5 ms | 166.3 ms | −146.5% ❌ |

The two models run on different hardware. Qwen3-8B uses a 4-GPU `ml.g5.12xlarge` (4x A10G), while Qwen3-1.7B uses a single L4 GPU (`ml.g6.4xlarge`). The deltas reflect approximately 4x the compute, not just the models themselves.

The takeaway: Qwen3-8B delivers approximately 44–47 percent higher throughput and lower end-to-end latency, largely thanks to the additional GPU compute. Qwen3-1.7B wins only on time-to-first-token, the expected advantage of a smaller model on a single GPU.

## Putting it all together

You don’t need to memorize capability names or know which workflow to request. The following table shows how common requests map to outcomes.

| **You say** | **What you get** |
| --- | --- |
| “I already deployed a model and want to know how fast it is.” | Quantitative performance report: throughput, latency percentiles, concurrency metrics from real load. |
| “I have a model in S3 and I don’t know what instance to deploy on.” | Ranked deployment options with cost, throughput, and latency for each candidate configuration. |
| “I want to deploy a JumpStart model and find the cheapest instance. I only have the model ID.” | Ranked deployment options, no S3 staging required. Gated-model alternative surfaced if needed. |
| “I ran a benchmark before and after a change. Which one is faster?” | Percentage change across all metrics indicating improvement or regression. |
| “I want to optimize a Llama model from Hugging Face Hub.” | License surfaced, model staged to S3, then standard recommendation output. |

If your request spans multiple capabilities (for example, staging a Hugging Face model and then getting deployment recommendations), the agent chains them naturally within the same conversation.

## What to expect from the agent

Your agent, equipped with the `aws-ai-ml` skill, follows a few behaviors that make the experience predictable and safe:

- **It asks for what it needs.** If information is missing (such as an endpoint name or S3 URI), the agent asks you to provide it rather than guessing.
- **It confirms before impactful actions.** Before running a benchmark that drives real traffic to a live endpoint, the agent warns you about the impact and asks for explicit confirmation.
- **It tells you when something is out of scope.** If you ask for something the agent can’t do (such as deploying a model), it explains what it can offer instead, such as generating the deployment configuration that you need.
- **It generates SageMaker Python SDK v3 code.** Every output is executable code you can inspect, modify, and run in your own environment.

## Clean up

To avoid ongoing charges, delete the resources you created:

- [Delete SageMaker AI endpoints](https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints-delete.html) created during benchmarking or recommendations.
- [Stop or delete your JupyterLab space](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-updated-jl-user-guide-shutdown.html) if you used SageMaker Studio.
- [Remove S3 objects](https://docs.aws.amazon.com/AmazonS3/latest/userguide/DeletingObjects.html) stored by benchmark and recommendation jobs in your SageMaker AI default bucket.

## Conclusion

The `aws-ai-ml` skill for Amazon SageMaker AI optimized generative AI inference turns your existing coding agent into a SageMaker AI inference optimization expert. Whether you need to benchmark a live endpoint, find the cheapest instance for your model, compare configurations, or stage a Hugging Face model for evaluation, you describe what you want and your agent delivers measurable results.

To get started, install the skill through the [Agent Toolkit for AWS](https://aws.amazon.com/products/developer-tools/agent-toolkit-for-aws/) and add it to the coding agent you already use, or launch a pre-configured JupyterLab space in Amazon SageMaker Studio. For more information, see the [Amazon SageMaker AI documentation](https://docs.aws.amazon.com/sagemaker/latest/dg/whatis.html).

## About the authors
