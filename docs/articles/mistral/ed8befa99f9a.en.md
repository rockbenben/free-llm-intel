---
vendor: mistral
title: Build AI agents with the Mistral Agents API
original_title: Build AI agents with the Mistral Agents API
url: https://mistral.ai/news/agents-api
date: 2025-05-27
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 2239e00f9577
---

Product

# Build AI agents with the Mistral Agents API

May 27, 2025

By Mistral AI


5 min read




![Cover](https://mistral.ai/_astro/f2a4b295-ff64-4c16-a42a-14f858c65766_ZHm3tW.webp?dpl=6abbd11780b53c00082eea6f)

Today we announce our new Agents API, a major step forward in making AI more capable, useful, and an active problem-solver.

Traditional language models excel at generating text but are limited in their ability to perform actions or maintain context. Our new Agents API addresses these limitations by combining Mistral's powerful language models with:

- Built-in connectors for code execution, web search, image generation, and MCP tools
- Persistent memory across conversations
- Agentic orchestration capabilities

The Agents API complements our [Chat Completion API](https://docs.mistral.ai/capabilities/completion/) by offering a dedicated framework that simplifies implementing agentic use cases. It serves as the backbone of enterprise-grade agentic platforms.

By providing a reliable framework for AI agents to handle complex tasks, maintain context, and coordinate multiple actions, the Agents API enables enterprises to use AI in more practical and impactful ways.

## Mistral agents in action.

Explore the diverse applications of Mistral’s Agents API across various sectors:

### Coding assistant with Github.

An agentic workflow built with Mistral's agents API where an agent interacts with Github and oversees a developer agent, powered by DevStral to write code. The agent is granted full authority over Github, showcasing automated software development task management.

[Read our cookbook](https://github.com/mistralai/cookbook/tree/main/mistral/agents/agents_api/github_agent)

### Linear tickets assistant.

An intelligent task coordination assistant powered by our Agents API, using multi-server MCP architecture to transform call transcripts to PRDs to actionable Linear issues and track project deliverables.

[Read our cookbook](https://github.com/mistralai/cookbook/tree/main/mistral/agents/agents_api/prd_linear_ticket)

### Financial analyst.

A financial advisory agent constructed with our Agents API, orchestrating multiple MCP servers to source financial metrics, compile insights, and archive results securely.

[Read our cookbook](https://github.com/mistralai/cookbook/tree/main/mistral/agents/agents_api/financial_analyst)

### Travel assistant.

A powerful AI travel assistant that helps users plan their trips, book accommodations, and manage travel needs.

[Read our cookbook](https://github.com/mistralai/cookbook/tree/main/mistral/agents/agents_api/travel_assistant)

### Nutrition assistant.

An AI-powered food diet companion designed to help users establish goals, log meals, receive personalized food suggestions, track their daily achievements, and discover dining options that align with their nutritional targets.

[Read our cookbook](https://github.com/mistralai/cookbook/tree/main/mistral/agents/agents_api/food_diet_companion)

## Create an agent with built-in connectors and MCP tools.

Each agent can be equipped with powerful built-in connectors, which are tools that are deployed and ready for Agents to call on demand, and MCP tools:

- [Code execution](https://docs.mistral.ai/agents/connectors/code_interpreter/)The Agents API can use the code execution connector, empowering developers to create agents that execute Python code in a secure sandboxed environment. This enables agents to tackle a wide range of tasks, including mathematical calculations and analysis, data visualization and plotting, and scientific computing.
- [Image generation](https://docs.mistral.ai/agents/connectors/image_generation/)The image generation connector tool, powered by Black Forest Lab FLUX1.1 [pro] Ultra, enables agents to create images for diverse applications. This feature can be leveraged for various use cases such as generating visual aids for educational content, creating custom graphics for marketing materials, or even producing artistic images.
- [Document library](https://docs.mistral.ai/agents/connectors/document_library/)Document Library is a built-in connector tool that enables agents to access documents from Mistral Cloud. It powers the integrated RAG functionality, strengthening agents’ knowledge by leveraging the content of user-uploaded documents.
- [Web search](https://docs.mistral.ai/agents/connectors/websearch/)The Agents API offers web search as a connector, enabling developers to combine Mistral models with diverse, up-to-date information from web search, reputable news, and other sources. This integration facilitates the delivery of up-to-date, informed, evidence-supported responses.
Agents with web search capabilities show a significant improvement in performance. In the SimpleQA benchmark, Mistral Large and Mistral Medium with web search achieve scores of 75% and 82.32%, respectively, compared to 23% and 22.08% without web search (see figure below).SimpleQA Accuracy (Higher is better)
- [MCP tools](https://docs.mistral.ai/agents/mcp/)The Agents API SDK can also leverage tools built on the Model Context Protocol (MCP)—an open, standardized protocol that enables seamless integration between agents and external systems. MCP tools provide a flexible and extensible interface for agents to access real-world context, including APIs, databases, user data, documents, and other dynamic resources. Check out the [Github](https://mistral.ai/news/agents-api/#demo-github), [Financial Analyst](https://mistral.ai/news/agents-api/#demo-finance), and [Linear](https://mistral.ai/news/agents-api/#demo-linear) MCP demos to learn how to use MCP tools with Mistral Agents in action.
![Mcp Mistral](https://cms.globalaegis.net/api/legacy-media/file/5a0eb67b-819c-4a3f-9cc0-7dba190d58d2.svg)

## Memory and context with stateful conversations.

The Agents API provides robust conversation management through a flexible and stateful conversation system. Each conversation retains its context, allowing for seamless and coherent interactions over time.

- [Conversation management](https://docs.mistral.ai/agents/agents_basics/#conversations)There are two ways to start a conversation:
Each conversation maintains a structured history through conversation entries, ensuring that the context is preserved across interactions.
- With an Agent: Create a conversation with a specific agent_id to leverage its specialized capabilities.Direct Access: Start a conversation by directly specifying the model and completion parameters, providing quick access to built-in connectors.
- [Stateful interactions and conversation branching](https://docs.mistral.ai/agents/agents_basics/#continue-a-conversation-working)Developers are no longer required to monitor conversion history; they have the ability to view past conversations. They can always continue any conversation or initiate new conversation paths from any point.
- [Streaming output](https://docs.mistral.ai/agents/agents_basics/#streaming-output-working)The API also supports streaming outputs, both when starting a conversation and continuing a previous one. This feature allows for real-time updates and interactions.

## Agent orchestration.

The true power of our Agents API lies in its ability to orchestrate multiple agents to solve complex problems. Through dynamic orchestration, agents can be added or removed from a conversation as needed—each one contributing its unique capabilities to tackle different parts of a problem.

![Agents](https://cms.globalaegis.net/api/legacy-media/file/55ca02be-4dfa-4f0e-ba6a-adc7c54dce4c.svg)

- [Creating an agentic workflow](https://docs.mistral.ai/agents/handoffs/#create-an-agentic-workflow)To build a workflow with handoffs, start by creating all necessary agents. You can create as many agents as needed, each with specific tools and models, to form a tailored workflow.
- [Agent handoffs](https://docs.mistral.ai/agents/handoffs/)Once agents are created, define which agents can hand off tasks to others. For example, a finance agent might delegate tasks to a web search agent or a calculator agent based on the conversation's needs.
Handoffs enable a seamless chain of actions. A single request can trigger tasks across multiple agents, each handling specific parts of the request. This collaborative approach allows for efficient and effective problem-solving, unlocking powerful possibilities for real-world applications.

## Get started.

To get started, check out our [docs](https://docs.mistral.ai/agents/introduction), create your first agent, and start building!

0%
