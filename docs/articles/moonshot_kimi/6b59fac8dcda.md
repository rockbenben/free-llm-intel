---
vendor: moonshot_kimi
title: Kimi K2 Thinking
original_title: 
url: https://www.kimi.com/blog/kimi-k2-thinking
date: 2025-11-06
lang: zh
captured: 2026-11-21
extractor: readability-v1
translator: agent
status: translated
body_sha: 1155721b6390
---

# 推出 Kimi K2 Thinking

今天，我们推出 **Kimi** **K2** **Thinking**，这是我们最好的开源思考模型。

它是一个**思考型 agent**，在调用工具的同时逐步推理，在 Humanity's Last Exam (HLE)、BrowseComp 等基准测试上取得业界领先的成绩，在推理、agentic 搜索、编码、写作与通用能力上都有大幅提升。

Kimi K2 Thinking 无需人工干预即可连续执行最多 **200 – 300 次工具调用**，在数百个步骤中保持连贯推理，攻克复杂问题。

它代表我们在**测试时扩展**上的最新努力：同时扩展思考 token 与工具调用步数。

K2 Thinking 现已在 [kimi.com](https://www.kimi.com/en) 的聊天模式下上线 [[1]](https://www.kimi.com/en/blog/kimi-k2-thinking#footnote-1)，完整的 agentic 模式即将推出。你也可以通过 Kimi K2 Thinking [API](https://platform.kimi.com/) 访问它。

### 评测结果

Kimi K2 Thinking 在考察推理、编码与 agent 能力的多项 benchmark 上刷新纪录。K2 Thinking 在带工具的 HLE 上达到 44.9%，在 BrowseComp 上达到 60.2%，在 SWE-Bench Verified 上达到 71.3%，展现出作为业界领先思考型 agent 模型的强大泛化能力。

### Agentic 推理

K2 Thinking 展现出卓越的推理与问题求解能力。Humanity's Last Exam (HLE) 是一套严谨构建的封闭式基准，涵盖 100 多个学科、数千道专家级题目；在配备搜索、python 与网页浏览工具的情况下，K2 Thinking 取得了**业界领先的 44.9%** 成绩，在多领域专家级推理性能上创下新纪录。

通过在积极调用多种工具的同时进行推理，K2 Thinking 能够**在数百个步骤中规划、推理、执行并调整**，攻克一些最具挑战性的学术与分析难题。其中一例是，它经过 **23 次交错的推理与工具调用**，成功解出一道**博士级数学难题**，体现出深度结构化推理与长程问题求解的能力：

### Agentic 编码

K2 Thinking 在编码与软件开发任务上有显著提升。它在 SWE-Multilingual 上得分 61.1%，在 SWE-Bench Verified 上 71.3%，在 Terminal-Bench 上 47.1%，显示出跨编程语言与 agent scaffold 的强大泛化能力。

该模型在 HTML、React 以及组件密集型前端任务上有明显改进——把想法变成功能完整、响应式适配的产品。在 agentic 编码场景中，它一边调用工具一边推理，能顺畅地接入软件 agent，精确而灵活地执行复杂的多步开发工作流。

以下是 Kimi K2 Thinking 仅凭一句 prompt 构建出的一些示例：

### Agentic 搜索与浏览

K2 Thinking 在 agentic 搜索与浏览场景中表现强劲。BrowseComp 是一项颇具挑战的基准，用来评估模型**持续浏览、搜索并推理难以找到的真实世界网络信息**的能力；K2 Thinking 在该基准上取得 **60.2%**，大幅超过 29.2% 的人类基线。这一结果凸显了 K2 Thinking 在目标导向的网页推理上的出众能力，以及它在动态、信息密集环境中的稳健表现。

K2 Thinking 可以执行 **200–300 次顺序工具调用**，由**长程规划**与**自适应推理**驱动。它循环执行 *思考 → 搜索 → 使用浏览器 → 思考 → 写代码*，不断生成并修正假设、验证证据、推理，并构建连贯的答案。这种交错推理让它能把含糊的开放式问题拆解成清晰、可执行的子任务。

以下是 **Kimi K2 Thinking** 仅凭一句 prompt 完成研究的一个示例：

### 通用能力

**创意写作：**K2 Thinking 在完整度与丰富度上都有提升。它对风格与指令的驾驭更强，能自然流畅地处理多样的语气与格式。它的文字更鲜活、更富想象——诗性意象承载更深的联想，故事与剧本读起来更像人写的，有情感、有意图。它表达的想法往往达到更深的主题层次与共鸣。

**实用写作：**K2 Thinking 在推理深度、视角广度与指令遵循上进步明显。它更精确地遵循 prompt，清晰而有条理地回应每一项要求——常常把提到的每个点都展开，确保覆盖周全。在学术、研究和长篇分析写作中，它擅长产出严谨、逻辑连贯、内容扎实的文字，在学术与专业场景中尤其好用。

**个人与情感：**面对个人或情感类问题时，K2 Thinking 的回应更有同理心、更平衡。它的思考细致而具体，给出有层次的视角与可执行的下一步。它帮用户清醒而妥帖地梳理复杂决策——脚踏实地、务实，语气也真切地像人。

### 推理效率

低位量化是降低大规模推理服务器上推理延迟与 GPU 显存占用的有效手段。然而思考模型使用的解码长度过长，量化往往会带来明显的性能下降。

为克服这一难题，我们在 post-training 阶段采用量化感知训练（QAT），对 MoE 组件施加 INT4 仅权重量化。这让 K2 Thinking 支持原生 INT4 推理，生成速度约提升 2 倍，同时保持业界领先的性能。所有 benchmark 结果均以 INT4 精度报告。

### 完整评测 [[2]](https://www.kimi.com/en/blog/kimi-k2-thinking#footnote-2)

下表显示，Kimi K2 Thinking 在广泛任务上与最新的开源模型和前沿模型持平或超越，在推理、agentic 搜索与编码类 benchmark 上表现突出。

**脚注**

- 为保证快速、轻量的体验，我们在 [kimi.com](https://www.kimi.com/en) 的聊天模式下有选择地使用一部分工具，并减少工具调用的轮数。因此，在 [kimi.com](https://www.kimi.com/en) 上聊天可能无法复现我们的 benchmark 成绩。我们的 agentic 模式很快会更新，以体现 K2 Thinking 的完整能力。
- **测试细节：** a. 除 SciCode 遵循官方的 0.0 温度设置外，K2 Thinking 的所有 benchmark 均在 temperature = 1.0、256 k 上下文长度下评测。b. HLE（无工具）、AIME25、HMMT25 与 GPQA 的思考 token 预算上限为 96k，IMO-Answer Bench、LiveCodeBench 与 OJ-Bench 的上限为 128k。Longform Writing 的补全 token 预算上限为 32k。c. AIME 与 HMMT（无工具）报告 32 次运行的平均值（avg@32）。AIME 与 HMMT（使用 Python）报告 16 次运行的平均值（avg@16）。IMO-AnswerBench 报告 8 次运行的平均值（avg@8）。
- **基线：** a. GPT-5、Claude-4.5-sonnet、Grok-4 的结果与 DeepSeek-V3.2 的结果引自 [GPT-5 发布文](https://openai.com/index/introducing-gpt-5/)、[GPT-5 for Developers 发布文](https://openai.com/index/introducing-gpt-5-for-developers/)、[GPT-5 system card](https://openai.com/index/gpt-5-system-card/)、[claude-sonnet-4-5](https://www.anthropic.com/news/claude-sonnet-4-5)、[grok-4](https://x.ai/news/grok-4)、[deepseek-v3.2](https://api-docs.deepseek.com/news/news250929/)、公开的 [Terminal-Bench 排行榜](https://www.tbench.ai/)（Terminus-2）、公开的 [Vals AI 排行榜](https://www.vals.ai/benchmarks/legal_bench) 以及 [artificialanalysis](https://artificialanalysis.ai/)。对没有公开可用分数的 benchmark，我们在与 k2 thinking 相同的条件下重新测试，并以星号（*）标注。GPT-5 测试中，我们把 reasoning effort 设为 high。 b. HLE 全套题（带工具）上，GPT-5 与 Grok-4 的分数按其官方发布文分别为 35.2 和 38.6。在我们对 HLE 纯文本子集的内部评测中，GPT-5 得分 **41.7**，Grok-4 得分 **38.6**（Grok-4 发布时在纯文本子集上引用的是 **41.0**）。GPT-5 在 HLE 纯文本无工具设置下，我们采用 [Scale.ai](https://labs.scale.com/leaderboard/humanitys_last_exam_text_only) 的分数；HLE 全套（无工具）的官方 GPT-5 分数为 24.8。 c. 关于 [IMO-AnswerBench](https://aclanthology.org/2025.emnlp-main.1794.pdf)：GPT-5 在基准论文中得 65.6。我们用官方 API 重新评测 GPT-5，得到 76。
- **HLE（带工具）与 agentic 搜索类 benchmark：** a. K2 Thinking 配备了搜索、代码解释器与网页浏览工具。b. BrowseComp-ZH、Seal-0、FinSearchComp-T3 各自独立运行 4 次，报告平均值（avg@4）。c. 评测使用 o3-mini 作为 judge，配置与官方 HLE 设置一致；judge prompt 逐字取自官方仓库。d. HLE 上最大步数限制为 120 步，每步 48 k-token 推理预算；agentic 搜索任务限制为 300 步，每步 24 k-token 推理预算。e. 当工具执行结果使累计输入超过模型上下文上限（256k）时，我们采用简单的上下文管理策略，隐藏此前所有工具输出。f. 对 Hugging Face 的网络访问可能导致某些 benchmark（如 HLE）出现数据泄漏。不屏蔽 Hugging Face 时，K2 Thinking 在 HLE 上可以拿到 51.3 分。为确保公平严谨的对比，我们在测试期间屏蔽了对 Hugging Face 的访问。
- **编码任务：** a. Terminal-Bench 分数使用默认 agent 框架（Terminus-2）与随附的 JSON parser 获得。b. 其他编码任务的结果由我们内部的评测 harness 产出。该 harness 源自 SWE-agent，但我们收紧了 Bash 与 Edit 工具的上下文窗口，并重写了 system prompt 以匹配任务语义。c. 所有报告的编码任务分数均为 5 次独立运行的平均值。
- **Heavy Mode**：K2 Thinking Heavy Mode 采用一种高效的并行策略：先同时铺开八条轨迹，再反思性地聚合所有输出，生成最终结果。GPT-5 的 heavy mode 指官方 GPT-5 Pro 分数。
