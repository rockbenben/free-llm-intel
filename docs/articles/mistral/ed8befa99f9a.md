---
vendor: mistral
title: 用 Mistral Agents API 构建 AI Agent
original_title: Build AI agents with the Mistral Agents API
url: https://mistral.ai/news/agents-api
date: 2025-05-27
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# 用 Mistral Agents API 构建 AI Agent

![Cover](https://mistral.ai/_astro/f2a4b295-ff64-4c16-a42a-14f858c65766_ZHm3tW.webp?dpl=6abbd11780b53c00082eea6f)

今天我们发布全新的 Agents API，这是让 AI 更强、更有用、成为主动问题求解者的重要一步。

传统语言模型擅长生成文本，但在执行动作或保持上下文方面能力有限。我们的新 Agents API 将 Mistral 强大的语言模型与以下能力结合，弥补了这些短板：

- 代码执行、网页搜索、图像生成和 MCP 工具等内置连接器
- 跨对话的持久化记忆
- Agent 编排能力

Agents API 与我们的 [Chat Completion API](https://docs.mistral.ai/capabilities/completion/) 互为补充，提供了一个专门简化 Agent 类用例实现的框架。它是企业级 Agent 平台的骨干。

通过为 AI Agent 提供可靠框架来处理复杂任务、保持上下文并协调多个动作，Agents API 使企业能够以更务实、更有影响力的方式使用 AI。

## Mistral Agent 实战展示。

探索 Mistral Agents API 在各行业的多样应用：

### 结合 Github 的编码助手。

一个基于 Mistral Agents API 构建的 Agent 工作流：由 DevStral 驱动编写代码的 Agent 与 Github 交互并监管一个开发者 Agent。该 Agent 被授予对 Github 的完全权限，展示了自动化的软件开发任务管理。

[阅读我们的 cookbook](https://github.com/mistralai/cookbook/tree/main/mistral/agents/agents_api/github_agent)

### Linear 工单助手。

一个由 Agents API 驱动的智能任务协调助手，采用多服务器 MCP 架构，把通话记录转换为 PRD，再转化为可执行的 Linear issue，并跟踪项目交付物。

[阅读我们的 cookbook](https://github.com/mistralai/cookbook/tree/main/mistral/agents/agents_api/prd_linear_ticket)

### 金融分析师。

一个用 Agents API 构建的金融顾问 Agent，编排多个 MCP 服务器来获取金融指标、汇总洞见并安全归档结果。

[阅读我们的 cookbook](https://github.com/mistralai/cookbook/tree/main/mistral/agents/agents_api/financial_analyst)

### 旅行助手。

一个强大的 AI 旅行助手，帮助用户规划行程、预订住宿并管理旅行需求。

[阅读我们的 cookbook](https://github.com/mistralai/cookbook/tree/main/mistral/agents/agents_api/travel_assistant)

### 营养助手。

一个 AI 驱动的饮食伴侣，帮助用户设定目标、记录餐食、获得个性化饮食建议、追踪每日成就，并发现符合其营养目标的就餐选择。

[阅读我们的 cookbook](https://github.com/mistralai/cookbook/tree/main/mistral/agents/agents_api/food_diet_companion)

## 用内置连接器和 MCP 工具创建 Agent。

每个 Agent 都可以配备强大的内置连接器——即已部署、可供 Agent 按需调用的工具——以及 MCP 工具：

- [代码执行](https://docs.mistral.ai/agents/connectors/code_interpreter/)Agents API 可以使用代码执行连接器，让开发者创建在安全沙箱环境中执行 Python 代码的 Agent。这使 Agent 能够处理广泛的任务，包括数学计算与分析、数据可视化与绘图，以及科学计算。
- [图像生成](https://docs.mistral.ai/agents/connectors/image_generation/)由 Black Forest Lab FLUX1.1 [pro] Ultra 驱动的图像生成连接器工具，使 Agent 能为各种应用创建图像。该功能可用于多种用例，例如为教育内容生成视觉辅助材料、为营销物料创建定制图形，甚至创作艺术图像。
- [文档库](https://docs.mistral.ai/agents/connectors/document_library/)Document Library 是一个内置连接器工具，使 Agent 能够访问 Mistral Cloud 上的文档。它为集成的 RAG 功能提供支撑，借助用户上传文档的内容来增强 Agent 的知识。
- [网页搜索](https://docs.mistral.ai/agents/connectors/websearch/)Agents API 将网页搜索作为连接器提供，使开发者能够将 Mistral 模型与来自网页搜索、权威新闻及其他来源的多样、最新信息相结合。这一集成有助于给出与时俱进、有依据支撑的回答。具备网页搜索能力的 Agent 性能显著提升。在 SimpleQA 基准上，Mistral Large 和 Mistral Medium 配合网页搜索分别取得 75% 和 82.32% 的分数，而没有网页搜索时仅为 23% 和 22.08%（见下图）。SimpleQA Accuracy (Higher is better)
- [MCP 工具](https://docs.mistral.ai/agents/mcp/)Agents API SDK 还能利用基于 Model Context Protocol（MCP）构建的工具——这是一套开放、标准化的协议，使 Agent 与外部系统实现无缝集成。MCP 工具为 Agent 提供了灵活、可扩展的接口，以访问真实世界的上下文，包括 API、数据库、用户数据、文档及其他动态资源。查看 [Github](https://mistral.ai/news/agents-api/#demo-github)、[金融分析师](https://mistral.ai/news/agents-api/#demo-finance) 和 [Linear](https://mistral.ai/news/agents-api/#demo-linear) 的 MCP 演示，了解 Mistral Agent 实际如何使用 MCP 工具。
![Mcp Mistral](https://cms.globalaegis.net/api/legacy-media/file/5a0eb67b-819c-4a3f-9cc0-7dba190d58d2.svg)

## 通过有状态对话实现记忆与上下文。

Agents API 通过灵活、有状态的对话系统提供强大的对话管理。每个对话都保留其上下文，从而实现随时间推移无缝且连贯的交互。

- [对话管理](https://docs.mistral.ai/agents/agents_basics/#conversations)启动对话有两种方式：
每个对话通过 conversation entry 维护结构化历史，确保上下文在多次交互中得以保留。
- 借助 Agent：使用特定 agent_id 创建对话，以利用其专属能力。直接访问：直接指定模型和补全参数来启动对话，快速访问内置连接器。
- [有状态交互与对话分支](https://docs.mistral.ai/agents/agents_basics/#continue-a-conversation-working)开发者不再需要自行跟踪对话历史；他们可以查看过往对话，随时继续任何一个对话，或从任意节点开启新的对话分支。
- [流式输出](https://docs.mistral.ai/agents/agents_basics/#streaming-output-working)API 也支持流式输出，无论是开始新对话还是继续既有对话。该功能可实现实时更新与交互。

## Agent 编排。

Agents API 的真正威力在于编排多个 Agent 来解决复杂问题。通过动态编排，可以根据需要向对话中添加或移除 Agent——每个 Agent 贡献其独特能力来解决问题的不同部分。

![Agents](https://cms.globalaegis.net/api/legacy-media/file/55ca02be-4dfa-4f0e-ba6a-adc7c54dce4c.svg)

- [创建 Agent 工作流](https://docs.mistral.ai/agents/handoffs/#create-an-agentic-workflow)要构建带交接（handoff）的工作流，先创建所有必要的 Agent。你可以按需创建任意数量的 Agent，各自配备特定工具与模型，组成定制化的工作流。
- [Agent 交接](https://docs.mistral.ai/agents/handoffs/)Agent 创建完成后，定义哪些 Agent 可以把任务交接给哪些 Agent。例如，一个金融 Agent 可以根据对话需要，把任务委派给网页搜索 Agent 或计算器 Agent。
交接实现了无缝的行动链。单个请求可以触发跨多个 Agent 的任务，每个 Agent 处理请求的特定部分。这种协作方式带来高效的问题解决，为真实世界应用解锁了强大可能性。

## 开始使用。

要上手，请查阅我们的[文档](https://docs.mistral.ai/agents/introduction)，创建你的第一个 Agent，开始构建吧！
