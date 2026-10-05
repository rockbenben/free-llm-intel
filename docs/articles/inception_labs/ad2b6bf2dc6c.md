---
vendor: inception_labs
title: 'Mercury 2：第一个快到能接起电话的推理模型'
original_title: 'Mercury 2: the first reasoning model fast enough to pick up the phone'
url: https://www.inceptionlabs.ai/blog/mercury-2-the-first-reasoning-model-fast-enough-to-pick-up-the-phone
date: 2026-09-29
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

过去两年，每个前沿实验室都在用同一种方式向智能爬坡：**让模型思考更长时间**。推理模型如今在开口之前要烧掉数以千计的"思考"token（吹嘘、苦思、磨洋工）。在占主导地位的自回归解码范式下，这些 token 中的每一个都是串行生成的，每一个都需要一次完整的前向传播。在和语音 agent 通话时，这些生成（解码）时间累积到让人宁愿直接挂电话。

结果就是行业里一个奇怪的分化。推理智能的前沿一骑绝尘，而**实时智能却原地踏步**。语音是为数不多的 GPT 5.x、Claude Sonnet 和 Gemini Pro 直接不及格的垂直领域，因为没人愿意每次回答一个关于牙医预约的问题都等上 3 秒。

**Mercury 2 是全球第一款推理 diffusion 语言模型**，在标准 NVIDIA GPU 上每秒解码 1000+ 个 token。快到足以在自然对话的延迟预算内*既*跑完一整轮推理，*又*开始开口说话。我们把推理的代价从 3 秒的静默降到只有 300 毫秒。

## 语音 Agent 还停留在 2025 年 4 月

语音客户告诉我们，端到端 LLM 延迟必须落在约 500ms 以内，否则对话就不再像人和人说话。

一个以典型自回归 60–100 tokens/秒的速度输出 500 个思维链 token 的推理模型，会把这笔预算一口气超掉*五到八秒*。于是语音开发者只能在"听起来像坏掉的聪明模型"和"快但跟不上指令的模型"之间二选一。

他们中的大多数人用同一种方式解决了这个问题：**GPT 4.1——OpenAI 最强的非推理模型，来自 2025 年 4 月（！）——仍是大多数生产语音 agent 的默认「大脑」**。它是极少数兼具强指令遵循和工具调用、具备实时延迟，同时价格又能撑得起每天数千次调用的模型。但 GPT 4.1 今年晚些时候将在多家 provider 那里下线，这意味着语音 agent 行业即将失去它的默认模型，而没有任何前沿推理模型能坐上这个位置。

一条逃生通道是特殊硬件：在 Cerebras 或 Groq 上服务，可以得到速度惊人的自回归解码。但定制芯片的容量稀缺、经常被订满，等待期长达 12 个月以上；Cerebras 与 OpenAI 的多年巨额协议锁定了其大部分资源，挤压了较小的合同。所以真正的问题是：如果能在人人都有的 NVIDIA GPU 上获得**定制芯片级的解码速度**呢？

## Diffusion 为什么不必一次只走一个 token

每个自回归 LLM 的瓶颈都是结构性的。串行解码意味着每个输出 token 都需要一次完整的前向传播，而每次前向传播都意味着把整个模型的权重从 GPU HBM 流入片上 SRAM。在延迟敏感服务所要求的低 batch size 下，GPU 的算术带宽大部分处于闲置。

Mercury 系列模型是 diffusion 大语言模型（dLLM），采用**并行生成 token 的架构**。

如我们的[技术报告](https://arxiv.org/abs/2506.17298)所述，生成由一对过程完成。*前向*过程把干净文本在一系列步骤中逐步破坏成噪声。模型——一个标准 Transformer——被训练来反向运行这个过程：给定一段含噪的隐变量序列，它预测干净文本，并以去噪目标训练，**同时对序列中的所有位置**进行预测。

每次去噪会处理许多 token，因此生成的算术强度远高于一次一个 token 的解码——也就是说，同样从显存加载一次权重，可以完成许多 token 的有用计算。结果是：**在 NVIDIA H100 上超过 1,000 tokens/秒——此前只有定制芯片才能达到的吞吐**——同时质量与 GPT Mini、Claude Haiku 之类较小的前沿模型相当。

## 给实时推理算一笔账

在 1000+ tokens/秒下，一段 300 token 的推理轨迹在 300ms 内就能完成。这意味着让推理模型在工具选择、策略遵从和多步工作流上表现出色的那种斟酌，如今**能塞进单个轮次之内**，对通话者完全不可闻。

Mercury 2 提供一个 `reasoning_effort` 旋钮，有四档——instant、low、medium、high——让开发者可以根据应用所需的智能水平进行调节。

我们在 **IFBench**（指令遵循）和 **Tau3Bench Telecom**（面向客服 agent 的拟真多轮工具调用）上基准测试了 `instant`、`low` 和 `medium`，延迟以 OpenCall 的真实生产提示词测量。

“在 OpenCall，我们一直用 Mercury 2 为我们的生产语音 agent 提供支持，处理复杂的患者来电。在我们的测试中，Mercury 2 在指令遵循、工具使用和多步工作流的推理上，超过了在 Cerebras 上运行的 GPT OSS 120B。它给了我们需要的高质量推理，同时不牺牲自然电话体验所要求的低延迟。”

Oliver Silverstein，OpenCall CEO

**Instant** 用智能换取反射般的速度，适合确认、附和语以及不需要工具调用的轮次。**Low** 在指令遵循上已经击败 GPT 4.1，而延迟只是它的一小部分。**Medium** 才是头条：在 IFBench 上高出 GPT 4.1 27 分、在 Tau3Bench Telecom 上高出 24 分，同时*仍然*比 GPT 4.1 的非推理解码更快：

## 为什么级联流水线仍然胜过 Speech-to-Speech

你可能会想：既然有 speech-to-speech 模型，为什么还要去优化级联流水线里的 LLM？尽管全双工语音模型十分自然，2026 年几乎所有生产语音 agent 仍然运行 **ASR → LLM → TTS**，至少出于四个原因：

**灵活性。**跨多地区、多口音运营语音 agent 时，你可以按市场切换转写模型和音色。

**可观测性。**级联流水线产出的是文本转写，而不是成千上万小时不透明的音频，可实现规模化的质检与审计。

**智能。**当今的 speech-to-speech 模型在长上下文表现、多轮连贯性和工具调用准确率上仍然落后。

**成本。**按每百万 token $32/$64 的定价，GPT Realtime 2 的价格扛不住呼叫中心的话务量。Mercury 2 定价为**输入 $0.25/M、输出 $0.75/M**，折合约**每分钟对话半美分**。

> 假设一个生产语音 agent 画像：每分钟约 4 个对话轮次；每轮重发约 2,000 token 的系统提示加不断增长的对话历史（每分钟对话约 20,000 输入 token）；每分钟约 600 输出 token，含推理 token（每轮约 50 个口语音答 token 加约 100 个推理 token）。Mercury 2 牌价为输入 $0.25/M、输出 $0.75/M。仅计模型层成本；不含 STT、TTS 和电话线路。

级联流水线仍然是主流，但此前缺的是一个能实时推理的大脑。作为兼容 OpenAI API 的端点，Mercury 可以直接插进你现有编排栈的 LLM 槽位——LiveKit、Pipecat、Vapi、Retell，或你自己的。

## 下一步

实时推理改变语音 agent 能力的边界。我们正与语音平台和企业客户一起攻关更长的上下文、前沿水平的工具调用性能，以及一种感知延迟的推理模式。

**想看看 Mercury 2 如何处理你的提示词？** API 已在 [platform.inceptionlabs.ai](https://platform.inceptionlabs.ai/) 上线。**在为生产语音延迟做基准测试？**我们会配置更高吞吐的容量，让你能在自己的负载上测量真实性能。[联系我们的团队](https://www.inceptionlabs.ai/enterprise#contact-sales)。
