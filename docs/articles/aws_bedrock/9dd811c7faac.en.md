---
vendor: aws_bedrock
title: Control agent behaviors and cost beyond a single action: new capabilities in Amazon Bedrock AgentCore
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/control-agent-behaviors-and-cost-beyond-a-single-action-new-capabilities-in-amazon-bedrock-agentcore
date: 2026-08-06
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: d00326c1d047
---

# Control agent behaviors and cost beyond a single action: new capabilities in Amazon Bedrock AgentCore

Agents are becoming more autonomous and teams are running more of them, but trust and security have not kept pace. According to McKinsey, roughly 80% of organizations have already encountered risky behavior from AI agents. As a result, security and risk concerns are the leading barrier to scaling agentic AI (McKinsey’s State of AI Trust in 2026, and Trust in the age of AI agents 2026).

That makes trust the pacing factor for agent innovation and adoption. Earning it takes control across a wide surface, including identity, access, observability, evaluation, and traceability. We believe that investment in trust and security will accelerate agent adoption in enterprises. When guardrails are dependable, approving a new agent stops being a one-off negotiation and becomes something the platform handles at scale.

The challenge is that most guardrails today were designed for software that behaves predictably. Agents decide their own path as they go, so every step can pass on its own while the shape of the whole goes unexamined. An agent looks up a customer’s account, then transfers money to a different account number, because each call was judged on its own. An agent places a series of orders that each sits under the approval threshold, because nothing is tracking the total against the budget. An agent hits a failing tool and retries through the night, running through the token budget, because nothing capped how much it could consume. Every one of those requests was legitimate. The problem appears only in the pattern, and the agent is the last thing you would rely on to catch it.

We built [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) to give teams what they need to build, connect, and optimize agents at scale without assembling the infrastructure themselves. One principle has guided it from the start: security controls belong in the infrastructure layer, enforced consistently across every agent, rather than in application code where each team implements them differently.

AgentCore’s gateway is where that idea becomes concrete. The gateway is a fully managed, serverless entry point for AI traffic, routing requests to Model Context Protocol (MCP) servers, large language models (LLMs), agents, and knowledge bases. Because every call passes through it, the gateway is the natural place to apply limits that hold no matter how an agent behaves. Today we are advancing that work with new capabilities: temporal policies, powered by [Dogwood](https://github.com/dogwood-policy), a new open source policy language purpose-built for AI agents, and rate limiting in the gateway.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/05/Screenshot-2026-08-05-at-6.32.14 PM.png)

## Boundaries on sequences of actions, not only individual ones with temporal policies

Policies in AgentCore today give teams deterministic control over agent behavior, checking every action before it runs to evaluate who can call which tool and under what conditions. Those checks are stateless by design. Each request is judged on its own merits, quickly and provably, which is what authorization has always required. As agents take on longer tasks with less supervision, another question arises: whether its actions, taken together, add up to something that should be allowed. That is only visible when you look at the sequence of actions, not only individual ones.

Temporal policies extend the policies in AgentCore to close that gap. Rather than judging a request in isolation, the policy engine also looks at what the agent has already done in that session, then permits or denies the call based on that sequence of actions. The transfer that used the wrong account number can be blocked by a policy requiring that a value passed into one call match what an earlier call returned. A policy can tally what an agent has spent in a session and block the next purchase once the budget is reached, even if that purchase is under the individual limit. Teams can also require that the steps happen in a set order, or that a significant action needs a recorded human approval. Permissions can narrow automatically when a person is no longer engaged.

Temporal policies are enforced at the gateway layer, outside the agent’s own code. The agent does not see the policy logic and cannot reason around it, regardless of how it is prompted or whatever defects it carries. For security leaders being asked to approve autonomous systems, this is the distinction that matters. It is the difference between trusting an agent to behave and knowing the boundary holds over the course of its actions. Decisions are deterministic, deny by default, and logged with the full context behind them. A reviewer can see not only that a call was blocked but why.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/05/Screenshot-2026-08-05-at-6.32.28 PM.png)

Powering temporal policies is Dogwood, a new policy language purpose-built for AI agents. Built on the foundation of Cedar, Dogwood was designed to address a new dimension of agent control: evaluating whether a sequence of agent actions conforms to a policy as it unfolds. Dogwood embeds Cedar and adds temporal constructs for agent governance including rate limits, time windows, prerequisite steps, and escalation triggers. Dogwood is available as an open source specification and reference implementation under Apache 2.0. This gives customers full visibility into how their policies are evaluated and allows the broader ecosystem to build supporting tooling.

## Control what agents consume with rate limiting on gateway

AI cost is its own governance question, and with agents it starts with how fast they consume tokens and calls. An agent takes as many steps as it judges necessary, so what a task costs depends on how it chooses to work rather than on a predetermined rate. Left unbounded, a retry loop or an unusually heavy session consumes at whatever speed the agent decides. That unpredictability is a real constraint on approval. Forrester found that the reasons agentic AI rarely reaches scale starts with cost ([The State Of Agentic AI In 2026](https://www.forrester.com/blogs/the-state-of-agentic-ai-in-2026-companies-are-chasing-few-are-catching/)). Teams need a ceiling that holds regardless of how an agent behaves.

Available today, you can set those ceilings directly on AgentCore’s gateway. [Rate limiting](https://aws.amazon.com/blogs/machine-learning/configure-rate-limits-for-ai-traffic-on-agentcore-gateway/) lets teams cap consumption per user across every tool, model, and agent behind the gateway, using the identities they already manage through OAuth or IAM. Limits can cover how many requests someone makes, how many tokens a model processes for them, and how long they hold connections open. Having all three matters because agents run up cost in different ways. A retry loop shows up as request volume, a reasoning-heavy task shows up as tokens, and a long research session shows up as a connection held open while very little traffic moves. Any single measure leaves a way to exhaust a service without tripping a limit.

Limits apply in per-second and per-minute windows, which is what contains the failure mode teams actually hit: an agent consuming at a rate nobody intended, discovered after the fact. Rate limits take effect once they are configured, with no changes to agent code. Capacity allocation becomes something platform teams configure rather than build. Different users, teams, tools, and models can carry different ceilings, without throttling logic written into any of them.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/06/Screenshot-2026-08-06-at-11.41.58 AM.png)

## Where this is heading

Models keep improving, and that progress is what makes agents worth deploying. It also raises what is at stake, because a more capable agent takes more consequential actions with less supervision. What an enterprise earns from better models depends on whether it can run those agents with the same discipline it applies to everything else in production.

Trust in an agent is not really a judgment about the model. It is a judgment about the system the model runs inside, and whether that system holds when an agent behaves unexpectedly. Building that system is a young discipline, and the questions customers bring us now are noticeably more sophisticated than the ones they brought a year ago. We expect to keep moving quickly here, alongside continued investment in identity, observability, evaluation, and traceability. Every control that moves out of application code and into the platform is one fewer thing that must be rebuilt, reviewed, and trusted separately for each agent. The more reliably a platform can bound what agents do and how much they consume, the more autonomy you can extend without hesitation.

Neither capability requires rearchitecting agents already in production, and you can adopt either on its own. To learn more, see the AgentCore [documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) and [pricing pages](https://aws.amazon.com/bedrock/agentcore/pricing/), and explore the [Dogwood reference implementation](https://github.com/dogwood-policy).

## About the author
