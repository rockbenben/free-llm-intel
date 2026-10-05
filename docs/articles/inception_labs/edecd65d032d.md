---
vendor: inception_labs
title: 推出 Mercury 2
original_title: Introducing Mercury 2
url: https://www.inceptionlabs.ai/blog/introducing-mercury-2
date: 2026-09-29
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

## 最快的推理 LLM，由 diffusion 驱动

今天，我们推出 Mercury 2——全球最快的推理语言模型，旨在让生产环境中的 AI 响应快到近乎即时。

### 为什么速度如今更加重要

生产环境中的 AI 早已不是一问一答。它是循环：agents、检索流水线和抽取任务在后台大规模运行。在循环中，延迟不会只出现一次，而是在每一步、每个用户、每次重试中不断累积。

然而当前的 LLM 仍共享同一个瓶颈：自回归（autoregressive）的串行解码。一次一个 token，从左到右。

### 新的基础：面向实时推理的 Diffusion

Mercury 2 不进行串行解码。它通过并行精化生成响应，同时产出多个 token，并在少量步骤内收敛。不像打字机逐字输出，更像编辑一次性修改整篇草稿。结果是：生成速度快 5 倍以上，并带来一条根本不同的速度曲线。

速度优势还会改变推理的权衡关系。如今，更高的智能意味着更多的测试时计算——更长的思维链、更多采样、更多重试——直接以延迟和成本为代价。基于 diffusion 的推理则能让你在实时延迟预算内获得推理级的质量。

## Mercury 2 一览

Mercury 2 为生产部署改变了质量-速度曲线：

- **速度：** 在 NVIDIA Blackwell GPU 上达到 1,009 tokens/秒
- **价格：** 输入 $0.25/1M tokens · 输出 $0.75/1M tokens
- **质量**：与领先的 speed-optimized 模型不相上下
- **特性**：可调推理强度 · 128K 上下文 · 原生工具调用 · 符合 schema 的 JSON 输出

我们优化的速度，是用户真正能感受到的速度：在用户能察觉的关键时刻的响应性——高并发下的 p95 延迟、轮次之间的一致表现，以及系统繁忙时稳定的吞吐量。

“Inception 的 Mercury 2 展示了当新的模型架构遇上 NVIDIA AI 基础设施时所能达到的成就。在 NVIDIA GPU 上突破每秒 1,000 token，印证了我们平台在支撑全谱系 AI 负载方面的性能、可扩展性与多功能性。”

Shruti Koparkar，NVIDIA 加速计算组产品高级经理

## Mercury 2 在生产环境中解锁了什么

Mercury 2 在延迟敏感、用户体验不容妥协的应用中表现出色。

#### 1. 编程与编辑

自动补全、下一个编辑建议、重构、交互式代码 agents——这些场景中开发者都在环中，任何停顿都会打断心流。

“建议出现得足够快，让人感觉像是你自己思考的一部分，而不是需要等待的东西。”

Max Brunsfeld，Zed 联合创始人

#### 2. Agent 循环

Agentic 工作流每个任务会串联数十次推理调用。降低单次调用的延迟不只是节省时间，它改变了你能负担得起运行多少步骤，以及最终输出能有多好。

“我们现在正利用最新的 Mercury 模型智能地优化大规模的营销活动执行。通过实时呈现洞察并动态增强投放，我们正在推动更强的表现、更高的效率，以及一个更具韧性、由 AI 驱动的广告生态系统。这一进展强化了我们对自主广告的承诺——让智能系统持续优化执行，为客户交付可衡量的成果。”

Adrian Witas，Viant 高级副总裁兼首席架构师

“我们一直在评估 Mercury 2，因为它的延迟和品质表现无可比拟，对实时转录文本清理和交互式 HCI 应用尤其有价值。没有其他模型能接近 Mercury 提供的速度！”

Sahaj Garg，Wispr Flow CTO 兼联合创始人

"Mercury 2 至少比 GPT-5.2 快一倍，这对我们来说是颠覆性的。"

Suchintan Singh，Skyvern CTO 兼联合创始人

#### 3. 实时语音与交互

语音接口拥有 AI 中最严苛的延迟预算。Mercury 2 让推理级质量在自然语音节奏内变得可行。

“我们打造栩栩如生的 AI 视频化身，与真人进行实时对话，所以低延迟不是锦上添花，而是一切。Mercury 2 是我们语音技术栈的一大突破：快速、一致的文本生成让整个体验保持自然、有人味。”

Max Sapo，Happyverse AI CEO 兼联合创始人

“Mercury 2 的质量非常出色，模型的低延迟让语音 agent 的响应更加及时。”

Oliver Silverstein，OpenCall CEO 兼联合创始人

#### 4. 搜索与 RAG 流水线

多跳检索、重排序与摘要的延迟会迅速叠加。Mercury 2 让你在搜索循环中加入推理，而不突破延迟预算。

“与 Inception 的合作让我们搜索产品的实时 AI 变得可行。每一位 SearchBlox 客户——无论是客户支持、合规、风控、分析还是电商——都能从覆盖其全部数据的亚秒级智能中受益。”

Timo Selvaraj，SearchBlox 首席产品官

## 开始使用

Mercury 2 现已可用。

- [**试用 Mercury 2 API**](https://platform.inceptionlabs.ai/)
- [**在 Chat 中试用 Mercury 2**](https://chat.inceptionlabs.ai)

Mercury 2 兼容 OpenAI API。直接接入你现有的技术栈——无需重写。

如果你正在进行企业级评估，我们会在负载适配、评估设计以及你所预期的服务约束下的性能验证方面与你合作。

### Mercury 2 已上线。欢迎来到 diffusion。
