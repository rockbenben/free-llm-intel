---
vendor: cerebras
title: GLM-4.7：前沿智能，纪录速度——现已登陆 Cerebras
original_title: "GLM-4.7: Frontier intelligence at record speed — now available on Cerebras"
url: https://www.cerebras.ai/blog/glm-4-7
date: 
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

Jan 08 2026

# GLM-4.7：前沿智能，纪录速度——现已登陆 Cerebras

Eric Gardner

今天，我们宣布 GLM-4.7——Z.ai 发布的最新 GLM 家族模型——现已在 Cerebras Inference Cloud 上可用。这款模型把速度与前沿智能融为一体，服务于编码、工具驱动的 agent、多轮推理等场景。

### 前沿智能

GLM-4.7 相比 GLM-4.6 是一次清晰的跃升。对照领先的闭源模型，GLM-4.7 展现出可媲美的高质量代码生成与编辑、可靠的工具使用，以及一致的多轮推理。而这一切的速度与性价比最高可达一个数量级的提升！

在反映真实开发者工作负载的基准上，GLM-4.7 如今位居最强开放权重模型，在 SWEbench、τ²bench、LiveCodeBench 等一系列高级开发者基准上全面领先 DeepSeek-V3.2。

从 GLM-4.6 到 4.7，日常开发工作中编码能力的提升是最立竿见影的进步。GLM-4.7 的解答更准确、结构更干净、多语言输出更强，智能显著更高，同时在漫长的迭代式编码会话中保持稳定。它对项目上下文的理解、从错误中恢复、跨轮次打磨代码的能力也更强。

工具驱动的 agent 工作流在 4.7 中同样迈上新台阶。模型在规划、调用工具、跨多步交互维持上下文方面更可靠——这是它内部处理推理方式的直接成果。

GLM-4.7 进一步推进了推理在实际中的运作方式。它延续了交错思考（interleaved thinking）的思想：模型在每次行动、工具调用或回复之前都先推理，而不是把推理当作一次性前置步骤。它还引入了保留思考（preserved thinking），让推理上下文跨轮次持久存在。

这些变化共同提升了复杂数学、逻辑和工具增强任务的表现，减少了从零重推计划的必要，让多步工作流中的行为更一致。结果是：agent 能随时间更可靠地推理，而包括聊天与角色扮演在内的一般交互也感觉更自然、更稳定，语气和意图不再突兀切换。

### 纪录速度

真正让 GLM-4.7 与众不同之处，是这种水平的智能如今能在 Cerebras 晶圆引擎上以实时速度运行。部署在 Cerebras 硬件上时，GLM-4.7 的代码生成速度约为 1,000 tokens/秒（某些用例最高可达 [1,700 TPS](https://artificialanalysis.ai/models/glm-4-7-non-reasoning/providers)）。这种速度需要 Cerebras 的 AI 专用硬件，运行在 GPU 或其他架构上的同类模型做不到。

当推理延迟退出关键路径，团队就能把模型直接部署进面向用户的产品和时间敏感的工作流，而不必牺牲能力。GLM-4.7 在 Cerebras 上的实时表现，让前沿级编码助手、在线 agent 和延迟敏感应用真正可行——同时借助开放权重设计保留灵活性。

### 性价比

评估模型成本时，人们容易只盯着每 token 价格。实际上，更重要的是模型多快能产出有用输出。

在真实编码与 agentic 工作负载上，GLM-4.7 比 Claude Sonnet 4.5 等领先闭源模型最快快一个数量级。这种速度通过缩短会话、降低并发需求、减少交付同样用户体验所需的基础设施，直接压低了端到端成本。

即便各服务商的单 token 定价相近，经济学也会迅速分化。生成更快意味着开发者等待时间更短、agent 用更少轮次完成任务、系统在单位时间内交付更多可用工作。这正是让 GLM-4.6 令人动心的同一种动力，而 GLM-4.7 用更强的智能把它进一步延伸。

Cerebras 上的 GLM-4.7 提供约 10 倍于 Claude Sonnet 4.5 的性价比，与 DeepSeek-V3.2 相当——但准确率更高。

### 今天就开始

GLM-4.7 是 GLM-4.6 的全面升级，也是 Cerebras 迄今部署的最强开放模型。它在关键开发者评测上胜过 DeepSeek-V3.2 等其他开放权重模型，在生产中最重要的编码与 agentic 工作负载上与领先闭源模型智能相当——同时在 Cerebras 上提供快一个数量级的生成速度。

GLM-4.7 与现有的 GLM-4.6 chat completions 工作流完全兼容，API 表面不变，质量更高。对多数团队来说，迁移只需改个模型名。我们建议从默认设置开始，并在编码与 agentic 用例中启用 preserved thinking。

即刻在 Cerebras Cloud 上开始，包括起步价仅 $10 的按量付费开发者档位——宽松的速度限制让你无需大额前期投入就能原型、构建和扩展。

如果你在用 GLM-4.6，请参照这份[简单迁移](https://inference-docs.cerebras.ai/resources/glm-47-migration)[清单](https://inference-docs.cerebras.ai/resources/glm-47-migration)。
如果不是，今天就[试试 GLM-4.7](https://cloud.cerebras.ai/)——Cerebras Cloud 开发者档位 $10 起步。

从 Z.ai 了解更多模型信息：https://z.ai/blog/glm-4.7
一如既往，欢迎在 [Discord](https://discord.com/invite/q6bZcMWJVu) 或 [X](https://x.com/cerebras) 上给我们反馈。
