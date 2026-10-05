---
vendor: cerebras
title: 为什么速度制胜：更快的推理不只是答案更快——它是通往准确率的新路径
original_title: "Why speed wins: faster inference is about more than just quicker answers–it’s the new path to accuracy"
url: https://www.cerebras.ai/blog/speedandaccuracyblog
date: 
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

Feb 19 2026

# 为什么速度制胜：更快的推理不只是答案更快——它是通往准确率的新路径

Eric Gardner

过去两周，观看优秀运动员在米兰-科尔蒂纳冬奥会上角逐，是一种提醒：世界级表现要求在多个战线同时做到卓越——而且难以无限期维持。

冬季两项（Biathlon）起源于 1700 年代瑞典-挪威边境滑雪巡逻队之间"边滑边打"的比赛，是一个特别好的例子。运动员以接近极限的强度越野滑雪，随即立刻转入射击。

这项运动奖赏的不是孤立的"快"或"准"——它加冕的是在疲劳、天气与压力之下，滑雪速度与射击精度的最佳组合。原始速度不仅是领先对手所必需，也提供了足够的余量去干净地完成射击、避免昂贵的罚时。这项运动严苛到连世代级别的天才也有保质期。

今天的推理，与此有许多相似。

### 推理的范式转移

多年来，一种常见的说法是：只要模型输出文本快过人的阅读速度，速度就不再重要。速度主要是一条可用性门槛：模型必须足够快才有交互感，随着它们变得更智能、更复杂尤其如此。更好的模型带来更准确的答案，基础设施的任务是跟上节奏——有一段时间它干得还算不错。

一切都随 OpenAI 在 2024 年底发布其首个"推理"模型（1）而改变。此后，更高的准确率越来越多地通过额外的推理步骤获得。这一范式转移导致基于 GPU 的基础设施上出现了显著的等待时间——哪怕只是简单查询。

如果推理能跑得更快，你就能在同样的延迟预算内做更多推理——用富余的速度换取更高准确率的结果。我们甚至去年就在[博客](https://www.cerebras.ai/blog/the-cerebras-scaling-law-faster-inference-is-smarter-ai)中为这一新兴趋势提出了"Cerebras 扩展定律"，而这篇跟进文章展示它如何走向主流。

Cerebras 的推理比 NVIDIA GPU 最快快 15 倍。当我们告诉人们 Cerebras 比 NVIDIA 快这么多时，常会招来质疑：这不可能，没人能比全球市值最高的公司更快。你们一定是引用了某个在生产中行不通的实验室合成跑分。购置和/或切换成本一定高得离谱。如此种种。这些反应很自然——当根深蒂固的信念被挑战时，人总会经历认知失调。

事实是：在输出速度上，Cerebras 最快比 NVIDIA 快 15 倍并领跑——这一加速没有任何数量的 GPU 能够匹敌。这种性能今天在开源模型上、在生产环境中即可获得，具有领先的性价比，且零 CUDA 切换成本。

当推理与更快的速度结合时会发生什么？推理速度不再只是一条可用性门槛。它成为对 AI 最要害指标——准确率——的关键杠杆。

### 准确率依然是第一要务，而推理速度现在是关键杠杆

更高的准确率不是锦上添花——它是第一大部署需求。根据 LangChain 的 2025 年 Agent 工程现状调查（2），质量/准确率仍是走向生产的头号障碍——紧随其后的是延迟。

为达到更高准确率，推理模型会多走"思考"步骤：作答前的规划、中间工作与自检。"Agentic"意味着它跨多条推理线反复这么做——常常带着工具调用去执行真实行动——直到完成一个任务。要"答对"，越来越多的时候需要更多 token、更多轮次——以及数量级更多的算力。因此，需要更快的推理算力来完成所有这些"思考"，同时仍装进用户的延迟预算。

生产使用数据表明这不是假想。OpenRouter 的 2025 年 AI 现状研究（3）显示，2025 全年，来自"推理"模型的 token 份额增长到超过全部处理 token 的一半。换句话说，在更高准确率需求的驱动下，通过推理时算力做推理，如今已在 AI 应用中占主导。

### GenAI 推理是顺序型、受内存带宽制约的

自回归推理有两个主要阶段：prefill 和 decode。Prefill 可以并行，往往决定长 prompt 的首 token 时间。Decode 不同：即使有 key-value（KV）缓存，模型每生成下一个 token 都得再跑一次前向传播。因为 token 在时间上是顺序生成的，decode 处于交互式延迟的关键路径上——随着推理同时推高推理算力和输出长度，尤其如此。

即使今天最小的模型也比 GPU 片上内存大数百倍。因此每块 GPU 都在其 interposer 上集成一颗"高带宽"内存（HBM）模组，通过一条相对窄的内存总线与计算单元相连，内存带宽是个位数 TB/s。

问题在于：GenAI 推理的闸门是内存带宽——即把权重和激活值以足够快的速度从内存搬到计算单元，以生成每一个新 token 的能力。GPU 的计算单元常常闲置，而内存流量与通信开销迅速成为瓶颈——随着模型规模与上下文增长尤其如此。

Cerebras 采取了截然不同的架构路线：把计算与内存（SRAM）紧密封织在全球最大的处理器上——比 NVIDIA 的 B200 芯片大 56 倍。Cerebras 不把每片硅晶圆切成更小的处理器、再用外部内存与互联把它们缝起来——从而避免了一种可能变成又慢又低效的大杂烩的设计。目标很简单：削减分布式开销，用巨大的片上内存带宽喂养计算单元，让每个 token 都以纪录速度生成。

### 最快给出答案、峰值准确率，还是介于两者之间

更高的推理速度不再等于"答案更快"这么简单。它现在是一个准确率杠杆。如果你跑在与 GPU 相比同档模型最快快 15 倍（4）的 Cerebras 晶圆引擎上，你可以自行决定这份余量怎么花。这开启了一种新的推理范式——通过快速的推理迭代来做推理，从而达到更高准确率。

**"最快给出答案"的金牌得主是 Cerebras**——它持续证明比 GPU 最快快 15 倍的推理（4）。其他 ASIC 设备相对 GPU 只能给出个位数低位的加速，因为它们的小芯片共享同样的根本难题。

而峰值准确率，大多数能跑最先进推理模型的架构都能达到。但抵达峰值准确率所花的时间，取决于每个推理步骤完成的快慢。同样地，**"最快以峰值准确率给出答案"的金牌还是 Cerebras 的**。其他 ASIC 设备比 GPU 略快，而 GPU 垫底。

**多数应用大概会落在峰值速度与准确率两个极端之间的曲线上**，这条曲线斜率递减——因为逼近峰值准确率时，每多一步推理的准确率收益递减。因此，构建者通常会选择加*够用*的推理，尽可能多地吃到准确率收益，同时不超出用户的延迟预算。

以下是一些真实例子，展示领先公司如何把 Cerebras 的推理优势用于速度和/或准确率：

**用速度把对话式 AI 的延迟压到最低**
Tavus 构建了一个对话式视频界面，响应速度就是产品本身。没有延迟，没有假装打字的键盘音效。交互必须即时，轮换（turn-taking）才能成立。Tavus 集成 Cerebras Inference，为其对话视频体验降低 LLM 延迟，在 Llama 3.1-8B 上实现约 2,000 tokens/秒 的输出速度和约 440 毫秒的首 token 时间——这对自然的对话流动至关重要。（5）[了解更多](https://www.cerebras.ai/blog/building-real-time-digital-twin-with-cerebras-at-tavus)

**用速度更快迭代，以纪录时间交付更好的代码**
OpenAI 的 Codex Spark 以超过 1000 tokens/秒 生成代码，让快速、精确的代码改动以秒计。实际效果是复利式的：开发者同一小时能跑的迭代越多，无需切换上下文就能完成的验证与打磨就越多。结果不只是输出更快，而是更快收敛到正确、可交付的代码——因为反馈恰好在意图尚新鲜的时候抵达。[了解更多](https://www.cerebras.ai/blog/openai-codexspark)

**用速度获取最聪明的市场洞察**
AlphaSense 是领先的市场情报平台，它运用推理速度不只是为更快响应，更是为拓展推理的覆盖面。运行在 Cerebras 上，他们能以一半的时间处理比 GPU 系统多 100 倍的文档（监管文件、电话会、研报等）。这种"速度换覆盖面"的转化，正是更快推理通向更高准确率答案的方式——本例中还顺带拿到了 2 倍整体提速。[了解更多](https://www.cerebras.ai/customer-spotlights/alphasense)

### 通向一类全新 AI 应用的旅程

冬季两项与推理在许多方面相似。在冬季两项中，速度决定的不仅是你在对手身前的距离，还可能是"干净靶场"与"罚时"之间的差别。对推理而言，速度是"有根据的猜测"与"你可以信赖的答案"之间的差别——并且快到足以可用。两个领域里，世代天才最终都会让位给更快、更准的新人。

观看这届奥运会也提醒我们：抵达巅峰表现是一段旅程。冬季两项里看似毫不费力的速度与沉稳射击，是多年训练与逆境坚持的结果。高科技领域也有自己的这种磨砺。Cerebras 不是沿着显而易见的路走到晶圆级推理的——它源自对一种许多人认为不可能的架构的承诺，并在长达十年的旅途中跨越无数技术障碍。

对你而言庆幸的是——与那些旅程不同——构建由 Cerebras Inference 驱动、比 GPU 方案既快又准的应用是容易的。今天就与我们开始你的旅程：[https://www.cerebras.ai/build-with-us](https://www.cerebras.ai/build-with-us)。

*感谢 **Joyce Er** 对本文的出色贡献！*

*来源：*

†[https://commons.wikimedia.org/wiki/File:2023-02-12_BMW_IBU_World_Championships_Biathlon_Oberhof_2023_%E2%80%93_Men_12.5_km_Pursuit_by_Sandro_Halank%E2%80%93046.jpg](https://commons.wikimedia.org/wiki/File:2023-02-12_BMW_IBU_World_Championships_Biathlon_Oberhof_2023_%E2%80%93_Men_12.5_km_Pursuit_by_Sandro_Halank%E2%80%93046.jpg)（许可：[https://creativecommons.org/licenses/by-sa/4.0/](https://creativecommons.org/licenses/by-sa/4.0/)）

- [https://openai.com/index/learning-to-reason-with-llms/](https://openai.com/index/learning-to-reason-with-llms/)
- [https://www.langchain.com/state-of-agent-engineering](https://www.langchain.com/state-of-agent-engineering)
- [https://openrouter.ai/state-of-ai](https://openrouter.ai/state-of-ai)
- [https://www.cerebras.ai/blog/openai-gpt-oss-120b-runs-fastest-on-cerebras?utm_source=chatgpt.com](https://www.cerebras.ai/blog/openai-gpt-oss-120b-runs-fastest-on-cerebras)
- [https://www.cerebras.ai/blog/building-real-time-digital-twin-with-cerebras-at-tavus](https://www.cerebras.ai/blog/building-real-time-digital-twin-with-cerebras-at-tavus)
- [https://www.cerebras.ai/blog/case-study-cognition-x-cerebras](https://www.cerebras.ai/blog/case-study-cognition-x-cerebras)
- [https://www.cerebras.ai/customer-spotlights/alphasense](https://www.cerebras.ai/customer-spotlights/alphasense)
