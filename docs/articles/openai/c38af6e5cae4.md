---
vendor: openai
title: GPT‑6 系列模型指南
original_title: 
url: https://openai.com/index/practical-guide-building-gpt-6
date: 2026-10-07
lang: zh
captured: 2026-10-10
extractor: readability-v1
translator: native
status: translated
body_sha: e87bae8e6d56
---

2026年10月2日


指南

# GPT‑6 系列模型指南

在控制时间和成本的同时，充分发挥 GPT‑6 模型能力的实用技巧


GPT‑6 是[我们迄今最先进的模型系列](https://openai.com/index/introducing-gpt-6-1-sol/)，提供多款模型供你选择，以适应不同类型的工作。

无论你是将想法转化为可运行的原型、开发并测试功能，还是编排跨代码仓库、数据库和外部 API 的多步骤工作流，本指南都会介绍如何选择 GPT‑6 模型、为其提供有效指令、管理长时间运行的任务，以及为投入生产做好准备。

- GPT-6Astra我们最智能的模型， 带来最佳效果。输入US$10.00输出US$50.00缓存输入US$1.00
- GPT-6.1Sol接近 Astra 的智能水平，价格仅为其五分之一。输入US$2.00输出US$10.00缓存输入US$0.10
- GPT-6Luna快速高效地处理 大规模日常任务。输入US$0.10输出US$0.50缓存输入US$0.01

## 要点速览

- **在生产环境中高效运行。**使用[缓存](https://developers.openai.com/api/docs/guides/prompt-caching)和[压缩](https://developers.openai.com/api/docs/guides/compaction)来管理上下文和成本。衡量任务成功率和延迟，并规划监控与数据控制措施。
- **根据工作负载选择模型。**选择适合任务的模型、[推理强度](https://developers.openai.com/api/docs/guides/reasoning)和速度，平衡能力、成本与延迟。
- **调整提示词和技能。**在提示词、技能和代码仓库指令中，对模型应交付什么、可以独立执行哪些操作，以及什么算作完成，保持一致的要求。
- **让长时间运行的任务保持正轨。**使用[引导](https://developers.openai.com/api/docs/guides/steering)、[异步工具](https://developers.openai.com/api/docs/guides/async-tool-calling)和[任务委派](https://developers.openai.com/api/docs/guides/responses-multi-agent#overview)，处理更新和可独立执行的工作。明确模型应在何时征求你的意见。

## 1. 在生产环境中高效运行

### 让工作流为投入生产做好准备

部署前，需要落实几项检查和最佳实践。

- 注重效率。 [删减任务不需要的上下文](https://developers.openai.com/api/docs/guides/cost-optimization#cost-and-latency)，同时保留必要的依据。如果应用支持，就[并行运行彼此独立的任务](https://developers.openai.com/api/docs/guides/latency-optimization#parallelize)，避免某个缓慢的步骤拖累无关的工作。
- 对于重复性工作，通过[提示词缓存](https://developers.openai.com/api/docs/guides/prompt-caching)复用共享上下文。缓存输入 Token 的费用比未缓存输入 Token 最多[降低 95%](https://developers.openai.com/api/docs/guides/prompt-caching#why-prompt-caching-matters)，具体取决于模型。将固定的指令和参考资料放在会变化的任务细节之前，并保持工具定义一致。[缓存仪表板](https://platform.openai.com/usage?usage_section=prompt-caching)和[诊断指南](https://developers.openai.com/api/docs/guides/prompt-caching/diagnostics)可帮助你找出缓存复用在哪些环节失效。估算完整工作流的成本时，要计入缓存写入费用，以及适用的长上下文费率。
- 对于较长的对话，[压缩](https://developers.openai.com/api/docs/guides/compaction)可以减小上下文体积，同时保留继续执行所需的状态。
- 确定如何[监控行为](https://developers.openai.com/api/docs/guides/safety-checks/misalignment-monitoring)，并审查应用的[数据控制措施](https://developers.openai.com/api/docs/guides/your-data)。
- 部署前先测试：运行有代表性的任务，衡量任务成功率、延迟，以及每次成功完成任务的成本。查看我们的 [API 部署检查清单](https://developers.openai.com/api/docs/guides/deployment-checklist#choose-a-model-for-the-workload)。

### 根据工作负载选择模型

选择模型和推理级别，本质上是在智能水平与价格之间做权衡。

- **模型：**[GPT‑6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) 适合需要最高智能水平、难度最大的推理工作。[GPT‑6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol) 适合复杂编程、研究和计算机使用任务。[GPT‑6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna) 适合大规模处理特定任务，以及目标明确的日常重复性工作，例如提取发票字段、对请求进行分类，或生成结构化摘要。

评估哪款模型最适合任务时，请[比较各款模型的价格](https://developers.openai.com/api/docs/models/compare)。

- **推理级别：**在 API 中，选择模型为任务投入多少推理资源。低：常规任务，例如提取事实或进行小幅修改。中：需要判断的工作，例如规划功能或比较方案。高：高难度调试、深入分析或细致审查。极高 / Max：如果“高”仍无法满足需求，可在支持的情况下测试这些级别；只有效果提升足以抵偿额外的时间和成本时，才保留使用。

在 API 中，你可以[在对话中途调整推理强度](https://developers.openai.com/api/docs/guides/reasoning#change-reasoning-mid-conversation)，而不会使缓存失效。

在 Codex 中，先使用该模型的默认推理级别，再针对简单任务调低级别，或为深入分析调高级别。

- **速度：**在 API 中，对于聊天应用或编程工具等对响应时间要求较高的场景，可使用[快速 (Fast) 模式](https://developers.openai.com/api/docs/guides/fast-mode)。与标准处理相比，它的响应速度更快、更稳定，但每个 Token 的费用也更高。在 Codex 和 API 中，如果更快的响应值得额外付费，例如需要快速迭代代码时，可使用 [Ultrafast](https://developers.openai.com/api/docs/guides/ultrafast-mode)。它可以加快 Token 生成速度，而不改变推理强度。[适用于 GPT‑6 Astra](https://x.com/OpenAIDevs/status/2104996045482778973)。

## 2. 调整提示词和技能

### 给模型明确的任务说明

[*“模型理解细微差别和模糊含义的能力已经大幅提升，因此，过去有帮助的过于具体的指导，如今反而可能妨碍模型发挥。”*](https://x.com/pvncher/status/2095991462416490862)

—Eric Provencher，OpenAI 开发者体验团队

首先明确任务：你想要什么结果、面向谁、有哪些相关上下文和限制，以及什么算作完成。接下来，从以下四个方面深入了解如何更新指令。这些要点摘自[*《重新思考 GPT‑6 Astra 的技能与提示词》*](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra#better-skills)：

- **打造更好的技能：**用简短描述明确每项技能的运行时机，仅在需要时加载补充细节，并用适合团队所用模型的指导原则代替僵化的操作步骤。
- **更新 AGENTS.md：**说明特定文档和测试适用于哪些情况，并明确授权安全的常规工作流，例如使用一次性数据运行本地测试，且不访问生产环境。
- **设定决策边界：**说明哪些操作可以独立进行、哪些需要批准，用清晰的边界代替一概要求“始终先询问”的规则。
- **明确要求任务执行到底：**定义“完成”包含哪些环节 — 实施改动、运行、检查结果并修复问题 — 同时指出哪些决策需要你来审查。

更多指导请参阅[推理最佳实践](https://developers.openai.com/api/docs/guides/reasoning-best-practices#how-to-prompt-reasoning-models-effectively)。

### 明确你需要的输出

无论是在 Codex 中工作，还是使用 API 开发，都要说明模型可以做哪些决策、何时应征求意见，以及怎样的回复才有用。

给模型足够的指导，让它能够持续推进工作，而不必猜测重要决策该如何做。 [告诉它可以自行做哪些选择，以及何时需要征求你的意见](https://developers.openai.com/api/docs/guides/latest-model#initiative-and-follow-through)。例如，它可以决定如何组织摘要，但在更改项目范围之前应先与你确认。[描述怎样的回复才有用](https://developers.openai.com/api/docs/guides/latest-model#personality-and-writing-style)。例如，使用通俗语言、提供适合受众的技术细节，并给出简短的交接说明，交代修改了什么、检查了什么，以及还有哪些事项需要关注。

## 3. 优化长时间运行的任务

### 持续推进复杂工作

借助 GPT‑6 系列模型，你现在可以处理持续数小时甚至数天的任务。使用以下功能，更好地管理执行长时间任务的智能体。

#### API

在 API 中，使用引导、异步工具和并行工作，让长时间运行的任务持续推进。

- **在运行过程中更新指令：**[轮次中途引导](https://developers.openai.com/api/docs/guides/steering#send-a-steering-message)让你可以在模型工作时，通过 [Responses WebSocket API](https://developers.openai.com/api/docs/guides/websocket-mode) 发送纠正信息。更新会进入队列，不会取消正在运行的工具，也不会撤销已完成的操作。
- **工具运行期间继续工作：**[异步工具调用](https://developers.openai.com/api/docs/guides/async-tool-calling#how-async-tools-work)让模型可以在应用执行测试等较慢任务时，继续处理其他独立工作。结果就绪后，应用会将其返回。依赖该结果的工作，应等结果返回后再开始。
- **委派独立子任务：**GPT‑6.1 Sol 支持[通过 Responses API 运行多智能体工作流](https://developers.openai.com/api/docs/guides/responses-multi-agent#overview)。它可以将独立工作分配给子智能体（例如调查代码库的不同部分），并将它们的发现汇总为最终回复。多智能体功能目前处于测试阶段。

#### Codex

长时间运行的任务可能会遇到需要决策的事项，而这些未必能在编写初始提示词时预见。通过澄清和引导，让工作保持正确方向。

- **随着工作推进回答问题：**借助 GPT‑6 Astra，Codex 可以[在工作过程中请求澄清](https://developers.openai.com/api/docs/guides/latest-model#initiative-and-follow-through)。解决影响下一步的问题，并说明在你做决定期间，哪些独立工作可以继续进行。如果你要暂时离开，请告诉 Codex 哪些任务可以继续，以及何时应暂停并等待你的答复。
- **需求变化时调整工作方向：**用新信息[引导当前任务](https://developers.openai.com/blog/mastering-codex-remote-for-engineering#2-learn-the-difference-between-queue-and-steer)，说明哪些内容需要改变、哪些应保持不变。这样可以避免在已不符合需求的方案上继续耗费时间。

### 利用计算机使用能力完成更多工作

[**计算机使用**](https://developers.openai.com/api/docs/guides/tools-computer-use)功能让 GPT‑6 Astra、GPT‑6.1 Sol 和 GPT‑6 Luna 可以直接与网站和桌面应用交互，即使应用没有 API 也可以。例如，你可以让模型调查缺陷、修复代码，并在浏览器中打开你的产品，检查修复是否生效。

为每个步骤选择最简单可靠的完成方式：

- 如果 API 或已连接的工具可以直接完成工作，就使用它们。
- 当模型需要替你读取屏幕、点击按钮或填写表单时，使用计算机使用功能。

如果要将计算机使用功能集成到自己的应用中，请为模型提供一个能通过运行代码来控制浏览器或桌面的工具。[Playwright 可用于操作浏览器](https://developers.openai.com/api/docs/guides/tools-computer-use#code-execution-harness-examples)；PyAutoGUI 可用于操作桌面应用。

### 从测试到生产：团队如何使用 GPT‑6 Astra 开发

1 条/ 共 4 条

> Harvey：更丰富的上下文，更实用的文稿。⁠Harvey 结合了法院信息、判例法、律所文档和律师的偏好，量身定制文稿。联合创始人 Gabe Pereyra 表示：“我们可以为模型提供更多上下文，让结构化输出的质量不断提升。”

> Cognition：让测试结果可供工程师核查。⁠Cognition 在 Devin 中使用 GPT‑6 Astra 测试软件，并提供测试依据。在一个 iPhone 游戏案例中，Devin 生成了模拟器录屏和一份报告，将已通过的检查项与尚未测试的部分区分开来，让剩余工作一目了然。

> Hex：从业务问题到交互式仪表板。⁠Hex 使用 GPT‑6 Astra，将有关销售渠道表现的问题转化为书面分析结果和交互式仪表板，其中还包括按地区细分的数据。它还会让模型检查数据是否合理，以及分析是否回答了业务问题。

> Invideo：更好地掌控最终剪辑效果。⁠Invideo 使用 GPT‑6 Astra 规划时间线剪辑，并创建可供剪辑师进一步调整的自定义特效。据该公司报告，调色和色彩校正任务的成功率提升至原来的约三倍。几位剪辑师还在一天内制作了约 50 种特效。


## 作者
