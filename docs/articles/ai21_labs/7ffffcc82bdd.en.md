---
vendor: ai21_labs
title: AI Agents: Real Hype or Just If-Else Logic? | AI21
original_title: The AI Agent Hype Is Real – But Many Are Still Just Glorified If-Else Statements
url: https://www.ai21.com/blog/ai-agent
date: 2025-02-25
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: b07ee2ae2271
---

If you look at LinkedIn posts and keynote titles from 2024, you might think it was *the* year of [AI agents](https://www.ai21.com/ai-agents/). Social networks are flooded with videos of agents taking on all sorts of complex tasks, from ordering pizza to writing production-level code. The conceptual leap came when Anthropic released their “[Computer use](https://www.anthropic.com/news/3-5-models-and-computer-use)” in October, followed by OpenAI’s “[Operator](https://openai.com/index/introducing-operator/),” which took it even further—agents that connect to a computer and gain access to the keyboard and mouse. Just like a real human. Although these are still early-stage technologies, the very fact they are presented so naturally is both exciting and unsettling.

Many companies are promising solutions that replace entire development teams with a single AI agent, but reality paints a very different picture. Not only are there almost no AI agents in actual production environments, but most products that call themselves AI agents *lack any real “agency.”* The gap between promise and reality isn’t surprising—it’s a pattern we’ve seen often in the tech world. Still, it’s vital to understand *why* that gap is so wide, especially when we’re dealing with a technology that aims to change how we develop and run software systems.

## Why Aren’t There More AI Agents in Production?

Two years ago, the idea of putting a large language model (LLM) into production seemed almost unthinkable, yet today every company has a Generative AI team. Most of us can rattle off the main challenges with LLMs in our sleep: these are statistical models whose outputs aren’t always reliable, whether it’s about formatting or outright hallucinations. In the end, they take text as input and provide text as output, and despite their sometimes extraordinary “understanding,” they remain limited in isolation.

The natural progression from that point is the concept of [*Compound AI Systems*](https://bair.berkeley.edu/blog/2024/02/18/compound-ai-systems/)—which use language models as part of a larger system. This approach can provide better guarantees about outputs or better fine-tune inputs. One classic example is RAG (Retrieval-Augmented Generation), which has become a standard method. AI agents are a particularly complex example of this approach. At their core is a component that observes the current situation, takes an action, receives feedback, then repeats the cycle. But to paraphrase Uncle Ben, “*with* *great* complexity come *great* challenges”.

We can break down these challenges into four main areas.

### 1. Quality

The tasks we assign to AI agents are often difficult for humans themselves. Consider project management—you need to grasp both business and technical aspects, communicate effectively with different people, and make tough decisions. While we’ve seen impressive breakthroughs in models’ reasoning abilities (for instance, [OpenAI’s o3](https://www.youtube.com/watch?v=SKBG1sqdyIU)), they’re still not mature enough to stand on their own. And all the usual liability and reliability issues with language models apply here, too. Admittedly, AI agents include a hefty layer of guardrails, but we generally expect *more* from an agent than from a standard language model. A vivid example of reliability issues is the lawsuit filed against [Air Canada](https://www.forbes.com/sites/marisagarcia/2024/02/19/what-air-canada-lost-in-remarkable-lying-ai-chatbot-case/), which ended with the company paying compensation for misinformation from its chatbot. After a verdict like that, any company would think twice before putting out a feature driven by an AI agent in production.

### 2. Resources

Much like you don’t need a sledgehammer to drive a small nail, you don’t need a full-blown AI agent for simple tasks. Running an AI agent involves multiple model calls—and each call costs money—so expenses can add up quickly. An inefficient implementation might make a hundred different calls just to complete a single simple task. Add in the processing time for each call, and you could be waiting several minutes for an answer that might be right in front of you.

### 3. Transparency

Deep Learning in general (and LLMs in particular) suffers from a major explainability problem. Why do these models make the decisions they do, and what underpins them? This challenge hits AI agents just as hard, as it’s extremely difficult to decipher the rationale behind their actions.

It all stems from decision-making based on complex statistical calculations. Even if you ask the agent to explain how it reached its decision, how can you be sure it’s telling you the truth and not just “making up” a rationale after the fact? Many developers feel like they’re dealing with a black box, which complicates both the development process and the drive for consistent results.

### 4. Development Complexity

Building a production-ready AI agent demands a deep skill set. You need expertise in working with language models (who’s got time to craft the “perfect” prompt?), access to quality data (whether public or internal), and the ability to evaluate the agent’s performance (a tough challenge even with simpler language models).

## So, If These Aren’t Really “Agents,” What Are They?

At this point, most commercial “AI Agent” solutions typically fall into one of the following categories:

### Tool Use and Function Calling

This concept first appeared in a [2022 paper by AI21](https://arxiv.org/pdf/2205.00445) and was later formally [introduced by OpenAI](https://openai.com/index/function-calling-and-other-api-updates/) as part of their API. The idea is straightforward: while language models excel at writing tasks, what about mathematical calculations? Or searching the internet for relevant information? By connecting them to external tools, we can expand their capabilities.
When you call a language model, you provide a set of “tools” (in practice, function signatures). If the model recognizes it needs more information or an external resource, it outputs a call to the relevant tool. The “agentic” element here is the system that checks the language model’s output, detects when it wants to call an external function, performs that call, and feeds the result back in. This technology is now more stable, and indeed, the major enterprise platforms (AWS, Azure AI, Google Vertex) primarily feature agents of this type.

### LLM as a Router

Here, too, we’re talking about a *system*, not a pure agent. At its core sits a language model that receives an incoming request and routes it to the appropriate resource—whether that’s an external tool, a Python script, or a smaller, specialized language model. One example is [arcee.ai](http://arcee.ai).

### ReAct – Reasoning and Acting

First [introduced in 2023](https://arxiv.org/pdf/2210.03629), this approach combines two essentials for any agent: the ability to reason about instructions and states, and the capacity to take actions. It utilizes techniques like [Chain of Thought](https://arxiv.org/pdf/2201.11903) for deep logical processes (think about word problems you need to solve step by step), plus the ability to connect to external tools. At each step, the model makes an *observation* based on the data it has, decides on an *action*, executes it, and then moves to the next observation stage. It continues until the final decision is to return a response to the user.
There are significant constraints here: the process runs sequentially, which complicates runtime optimization. Also, end users don’t control the decision-making sequence; it all happens autonomously. That might be convenient, but the results aren’t always great, and debugging can be downright impossible.

ReAct framework, REACT: SYNERGIZING REASONING AND ACTING IN LANGUAGE MODELS, 2023

## But It’s Not Just Hype

The landscape is moving quickly, and it’s very probable that 2025 will indeed be the year of AI Agents (or, at least, another one). The challenges are clear: quality, cost, transparency, and complexity. But overcoming them isn’t impossible; it just requires a different way of thinking.

The whole ecosystem is focused on At AI21, we’re not just watching this unfold—we’re busy building. The next generation of AI agents won’t be glorified function-callers. They’ll be capable, reliable, and built for real-world impact.
