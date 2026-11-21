---
vendor: moonshot_kimi
title: Kimi K2 Thinking
original_title: 
url: https://www.kimi.com/blog/kimi-k2-thinking
date: 2025-11-06
lang: zh
captured: 2026-11-21
extractor: readability-v1
translator: mt
status: translated
body_sha: 5cc16d28b01f
---

# Kimi K2 思维介绍

今天，我们要介绍 **Kimi** **K2** **Thinking**，我们最好的开源思维模型。

作为一个**思考代理**，它在使用工具的同时逐步进行推理，在 Humanity's Last Exam (HLE)、BrowseComp 和其他基准测试中实现了最先进的性能，在推理、代理搜索、编码、写作和一般能力方面取得了重大进展。

Kimi K2 Thinking 可以执行多达 **200 – 300 个连续工具调用**，无需人工干预，通过数百个步骤进行连贯推理来解决复杂问题。

它标志着我们通过扩展思维标记和工具调用步骤在**测试时间扩展**方面所做的最新努力。

K2 Thinking 现已在 [kimi.com](https://www.kimi.com/en) 上以聊天模式 [[1]](https://www.kimi.com/en/blog/kimi-k2-thinking#footnote-1) 上线，其完整的代理模式即将推出。也可以通过 Kimi K2 Thinking [API](https://platform.kimi.com/) 访问它。

### 评价

Kimi K2 Thinking 在评估推理、编码和代理能力的基准测试中创下了新记录。 K2 Thinking 在使用工具的 HLE 上取得了 44.9% 的成绩，在 BrowseComp 上取得了 60.2% 的成绩，在 SWE-Bench Verified 上取得了 71.3% 的成绩，展示了作为最先进的思维代理模型的强大泛化能力。

### 代理推理

K2 Thinking 表现出出色的推理和解决问题的能力。在 Humanity’s Last Exam (HLE)（一项精心设计的封闭式基准测试，涵盖 100 多个科目的数千个专家级问题）中，K2 Thinking 凭借搜索、Python 和网络浏览工具取得了**a​** ​**最先进**​ ​**​分数** **​​44.9%**，在多领域专家级推理性能方面创造了新记录。

通过在积极使用各种工具的同时进行推理，K2 Thinking 能够**规划、推理、执行和适应数百个步骤**，以解决一些最具挑战性的学术和分析问题。在一个实例中，它通过**23次交错推理和工具调用**成功解决了**博士级数学问题**，体现了其深度、结构化推理和长期解决问题的能力：

### 代理编码

K2 Thinking 在编码和软件开发任务方面表现出了巨大的进步。它在 SWE-Multilingual 上得分为 61.1%，在 SWE-Bench Verified 上得分为 71.3%，在 Terminal-Bench 上得分为 47.1%，展示了跨编程语言和代理支架的强大泛化能力。

该模型对 HTML、React 和组件密集型前端任务进行了显着改进，将想法转化为功能齐全、响应迅速的产品。在代理编码设置中，它在调用工具时进行推理，流畅地集成到软件代理中，以精确且适应性强地执行复杂的多步骤开发工作流程。

以下是 Kimi K2 Thinking 根据单个提示构建的一些示例：

### 代理搜索和浏览

K2 Thinking 在代理搜索和浏览场景中表现出了强大的性能。在 BrowseComp（一项旨在评估模型持续浏览、搜索和推理难以找到的现实世界网络信息的能力的具有挑战性的基准）上，K2 Thinking 取得了 **​​60.​2%** 的分数，显着超过了 29.2% 的人类基线。这一结果凸显了 K2 Thinking 在目标导向、基于网络的推理方面的卓越能力及其在动态、信息丰富的环境中的稳健性。

K2 Thinking 可以执行​**200–300 个顺序工具调用**​，由 **长期规划** 和 **自适应推理**​ 驱动。它执行*思考→搜索→浏览器使用→思考→代码*​的动态循环，不断生成和完善假设、验证证据、推理并构建连贯的答案。这种交错推理使其能够将模糊的、开放式的问题分解为清晰的、可操作的子任务。

以下是 **Kimi ​**​**K2**​**​ Thinking** 仅根据一个提示进行研究的一个示例：

### 一般功能

**创意写作：​**K2 Thinking 提高了完整性和丰富性。它显示出对风格和指令的更强掌握，能够自然流畅地处理不同的语气和格式。它的写作变得更加生动和富有想象力——诗意意象带有更深层次的联想，而故事和剧本感觉更加人性化、情感化和有目的性。它所表达的思想往往能达到更大的主题深度和共鸣。

**实用写作：​**K2 Thinking 在推理深度、视角广度和指令遵守方面表现出显着的进步。它更精确地遵循提示，清晰、系统地解决每项要求——通常会扩展每个提到的点，以确保全面覆盖。在学术、研究和长篇分析写作中，它擅长撰写严谨、逻辑连贯且内容丰富的内容，使其在学术和专业环境中特别有效。

**个人和情感：​**在解决个人或情感问题时，K2 Thinking 会以更多的同理心和平衡来回应。它的思考是深思熟虑和具体的，提供了细致入微的观点和可行的后续步骤。它帮助用户清晰、谨慎地做出复杂的决策——脚踏实地、实用且真正人性化。

### 推理效率

低位量化是减少大规模推理服务器上的推理延迟和 GPU 内存使用的有效方法。然而，思维模型使用过多的解码长度，因此量化通常会导致性能大幅下降。

为了克服这一挑战，我们在训练后阶段采用量化感知训练（QAT），对 MoE 组件应用 INT4 仅权重量化。它使 K2 Thinking 支持原生 INT4 推理，生成速度提高了大约 2 倍，同时实现了最先进的性能。所有基准测试结果均以 INT4 精度报告。

### 完整评估 [[2]](https://www.kimi.com/en/blog/kimi-k2-thinking#footnote-2)

下表显示，Kimi K2 Thinking 在广泛的任务中匹配或超越了最新的开源和前沿模型，在推理、代理搜索和编码的基准方面表现出色。

**脚注**

- 为了确保快速、轻量级的体验，我们选择性地使用一部分工具，并减少 [kimi.com](https://www.kimi.com/en) 聊天模式下工具调用的次数。因此，在 [kimi.com](https://www.kimi.com/en) 上聊天可能无法重现我们的基准分数。我们的代理模式将很快更新，以体现 K2 Thinking 的全部功能。
- **测试详细信息：**所有基准测试均在 K2 Thinking 的温度 = 1.0 和 256 k 上下文长度下进行评估，但 SciCode 除外，我们遵循官方温度设置 0.0。 b. HLE（无工具）、AIME25、HMMT25 和 GPQA 的思维代币预算上限为 96k，而 IMO-Answer Bench、LiveCodeBench 和 OJ-Bench 的思维代币预算上限为 128k。长篇写作的完成令牌预算上限为 32k。 c.对于 AIME 和 HMMT（无工具），我们报告 32 次运行的平均值 (avg@32)。对于 AIME 和 HMMT（使用 Python），我们报告 16 次运行的平均值 (avg@16)。对于 IMO-AnswerBench，我们报告 8 次运行的平均值 (avg@8)。
- **基线：** GPT-5、Claude-4.5-sonnet、Grok-4 结果和 DeepSeek-V3.2 结果引用自[GPT-5 帖子](https://openai.com/index/introducing-gpt-5/)、[GPT-5 开发者帖子](https://openai.com/index/introducing-gpt-5-for-developers/)、[GPT-5 系统卡](https://openai.com/index/gpt-5-system-card/)、[claude-sonnet-4-5](https://www.anthropic.com/news/claude-sonnet-4-5)、 [grok-4](https://x.ai/news/grok-4)、[deepseek-v3.2](https://api-docs.deepseek.com/news/news250929/)、公共[Terminal-Bench排行榜](https://www.tbench.ai/) (Terminus-2)、公共[Vals AI排行榜](https://www.vals.ai/benchmarks/legal_bench)和[人工分析](https://artificialanalysis.ai/)。没有可用公共分数的基准在与 k2 思维相同的条件下重新测试，并标有星号 (*)。对于 GPT-5 测试，我们将推理工作设置为高。  b. HLE 全套工具中的 GPT-5 和 Grok-4 从其官方帖子来看分别为 35.2 和 38.6。在我们对 HLE 纯文本子集的内部评估中，GPT-5 得分 **41.7**，Grok-4 得分 **38.6 **​（Grok-4 的发布在纯文本子集上引用 **41.0**）。对于 GPT-5 的 HLE 纯文本无工具，我们使用 [Scale.ai](https://labs.scale.com/leaderboard/humanitys_last_exam_text_only) 的分数，HLE 全套（无工具）的官方 GPT-5 分数为 24.8。  c.对于 [IMO-AnswerBench](https://aclanthology.org/2025.emnlp-main.1794.pdf)：GPT-5 在基准论文中得分为 65.6。我们用官方API重新评估了GPT-5，得到了76分。
- **对于 HLE（带工具）和代理搜索基准：** K2 Thinking 配备了搜索、代码解释器和网络浏览工具。 b. BrowseComp-ZH、Seal-0、FinSearchComp-T3 独立运行 4 次并报告平均值 (avg@4)。 c.评测使用o3-mini作为评委，配置与官方HLE设置相同；法官提示逐字取自官方存储库。 d.在 HLE 上，最大步数限制为 120，每步推理预算为 48 k-token；在代理搜索任务中，限制为 300 个步骤，每个步骤有 24 k-token 推理预算。 e.当工具执行结果导致累积输入超过模型的上下文限制（256k）时，我们采用简单的上下文管理策略来隐藏所有先前的工具输出。 f. Web 访问 Hugging Face 可能会导致某些基准测试（例如 HLE）中的数据泄露。 K2 Thinking 在不屏蔽 Hugging Face 的情况下，在 HLE 上可以取得 51.3 的分数。为了确保公平和严格的比较，我们在测试期间阻止了对 Hugging Face 的访问。
- **对于编码任务：** Terminal-Bench 分数是使用默认代理框架 (Terminus-2) 和提供的 JSON 解析器获得的。 b.对于其他编码任务，结果是通过我们的内部评估工具生成的。该工具源自 SWE-agent，但我们限制了 Bash 和编辑工具的上下文窗口，并重写了系统提示符以匹配任务语义。 c.所有报告的编码任务分数均是 5 次独立运行的平均值。
- ​**重模式**​：K2 Thinking Heavy 模式采用高效的并行策略：它首先同时推出八个轨迹，然后反思性地聚合所有输出以生成最终结果。 GPT-5 的重度模式表示官方 GPT-5 Pro 分数。
