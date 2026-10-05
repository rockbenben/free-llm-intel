---
vendor: huggingface
title: 图解基于人类反馈的强化学习（RLHF）
original_title: Illustrating Reinforcement Learning from Human Feedback (RLHF)
url: https://huggingface.co/blog/rlhf
date: 2023-05-26
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: b6626af1bbbf
---

# 图解基于人类反馈的强化学习（RLHF）

作者：Nathan Lambert、Louis Castricato（客座）、Leandro von Werra、Alex Havrilla（客座）

本文另有中文版本 [简体中文](https://huggingface.co/blog/zh/rlhf)。

*本文还有中文 [简体中文](https://huggingface.co/blog/zh/rlhf) 和越南文 [đọc tiếng việt](https://trituenhantao.io/kien-thuc/minh-hoa-rlhf-vu-khi-dang-sau-gpt/) 译本。*

过去几年，语言模型从人类输入提示词生成多样而引人入胜的文本，展现出惊人的能力。但什么样的文本算"好"，本身就很难定义——它既主观又依赖上下文。有的应用（如写故事）要创意，有的信息性文本要真实，有的代码片段要能运行。

要把这些属性写成一个损失函数看起来不可行，多数语言模型至今仍用简单的下一 token 预测损失（如交叉熵）训练。为了弥补损失函数本身的不足，人们定义了更能刻画人类偏好的指标，如 [BLEU](https://en.wikipedia.org/wiki/BLEU) 和 [ROUGE](https://en.wikipedia.org/wiki/ROUGE_(metric))。虽然它们比损失函数更能衡量性能，但也不过是用简单规则把生成文本和参考文本做比对，因此同样有限。如果我们能把对生成文本的人类反馈直接当作性能度量，甚至更进一步——把它作为损失来优化模型，那该多好？这就是基于人类反馈的强化学习（RLHF）的想法：用强化学习方法，直接以人类反馈优化语言模型。RLHF 让语言模型开始能够把在通用语料上训练出的模型，对齐到复杂的人类价值观。

RLHF 最近的高光时刻是在 [ChatGPT](https://openai.com/blog/chatgpt/) 中的应用。鉴于 ChatGPT 能力惊人，我们请它给我们讲讲 RLHF：

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/rlhf/chatgpt-explains.png)

它讲得出奇地好，但没讲全。我们来补上缺口！

## RLHF：一步一步来

基于人类反馈的强化学习（也称基于人类偏好的 RL）是个不轻的概念，因为训练涉及多个模型、部署也分多个阶段。在这篇博客里，我们把训练过程拆成三个核心步骤：

- 预训练一个语言模型（LM）；
- 收集数据并训练奖励模型；
- 用强化学习微调语言模型。

先看语言模型是怎么预训练的。

#### 预训练语言模型

RLHF 的起点是一个已按经典预训练目标训练好的语言模型（更多细节见这篇[博客](https://huggingface.co/blog/how-to-train)）。OpenAI 在其第一个广为人知的 RLHF 模型 [InstructGPT](https://openai.com/blog/instruction-following/) 中用的是 GPT-3 的缩小版。Anthropic 在共享的论文中使用了从 1000 万到 520 亿参数的 transformer 模型。DeepMind 公开记录中最多用到其 2800 亿参数的 [Gopher](https://arxiv.org/abs/2112.11446) 模型。可以想见，这些公司在 RLHF 产品中用的模型只会更大。

这个初始模型*可以*再在额外文本或条件下微调，但并非必须。比如 OpenAI 在"更优"的人类生成文本上做了微调；Anthropic 则把原始 LM 在体现"有用、诚实、无害"标准的上下文线索上做蒸馏，生成 RLHF 的初始 LM。这些都是所谓昂贵的*增强*数据的来源，但不是理解 RLHF 的必要环节。启动 RLHF 流程的核心，是有一个*能很好地响应多样指令的模型*。

总的来说，"哪个模型"最适合做 RLHF 的起点，目前没有明确答案。这会是本文的常见主题——RLHF 训练的设计空间远未被充分探索。

接下来，有了语言模型，就需要生成数据来训练**奖励模型**——人类偏好正是通过它整合进系统的。

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/rlhf/pretraining.png)

#### 奖励模型训练

生成一个经人类偏好校准的奖励模型（RM，也称偏好模型），是 RLHF 这项较新研究的真正起点。其根本目标是得到一个模型或系统：输入一段文本序列，返回一个标量奖励，数值上代表人类偏好。这个系统可以是端到端的 LM，也可以是输出奖励的模块化系统（例如模型给输出排序，再把排序转成奖励）。输出是**标量奖励**这一点至关重要，因为这样就能与后面对接的现有 RL 算法无缝集成。

用于奖励建模的 LM，既可以是另一个微调过的 LM，也可以在偏好数据上从头训练。例如 Anthropic 在预训练后对这些模型采用了一种专门的微调方法来初始化（偏好模型预训练，PMP），因为他们发现这比微调更节省样本；但对奖励模型而言，并没有公认的单一最佳基座模型。

奖励模型训练所用的提示-生成对数据，来自对预定义数据集中提示的采样（Anthropic 的数据主要在 Amazon Mechanical Turk 的聊天工具上生成，已在 Hub 上[开放](https://huggingface.co/datasets/Anthropic/hh-rlhf)；OpenAI 用的是用户提交给 GPT API 的提示）。这些提示经过初始语言模型生成新文本。

由人类标注员对 LM 生成的文本输出进行排序。起初你可能觉得，直接给每段文本打一个标量分就能构建奖励模型，但实践中这很难做。人与人的价值标准不同，这些分数既不准也噪声大。取而代之的做法是用排序来比较多个模型的输出，从而得到正则化好得多的数据集。

文本排序有多种方法。被证明有效的一种，是让用户比较两个语言模型在相同提示下的生成文本。通过模型输出的两两对决，可以用 [Elo](https://en.wikipedia.org/wiki/Elo_rating_system) 系统生成模型及输出之间的相对排名。这些不同的排序方法最终被归一化成标量奖励信号用于训练。

这一流程有个有意思的现象：迄今成功的 RLHF 系统，其奖励语言模型与文本生成模型的尺寸关系各不相同（例如 OpenAI 用 175B LM 配 6B 奖励模型；Anthropic 的 LM 和奖励模型从 10B 到 52B；DeepMind 的 LM 和奖励模型都用 70B 的 Chinchilla）。一个直观理解是：偏好模型需要与生成模型相当的能力来理解给它看的文本。

到这一步，RLHF 系统已经有了：一个能生成文本的初始语言模型，以及一个给任意文本打上"人类觉得多好"分数的偏好模型。接下来，我们用**强化学习（RL）**在奖励模型的目标上优化最初的语言模型。

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/rlhf/reward-model.png)

#### 用 RL 微调

用强化学习训练语言模型，在很长一段时间里，人们无论从工程还是算法角度都认为不可能。多个机构似乎跑通的方案是：用策略梯度 RL 算法——近端策略优化（PPO）——微调**初始 LM 副本**的部分或全部参数。由于对整个 10B 或 100B+ 参数模型做微调代价过高（更多见 LM 的低秩适配 [LoRA](https://arxiv.org/abs/2106.09685) 或 DeepMind 的 [Sparrow](https://arxiv.org/abs/2209.14375) LM），LM 的一些参数会被冻结——具体取决于模型规模和所用基础设施。到底冻结多少参数的精确动态，仍是一个开放研究问题。PPO 已经存在相当长时间——关于它如何工作的[教程](https://spinningup.openai.com/en/latest/algorithms/ppo.html)和[指南](https://huggingface.co/blog/deep-rl-ppo)不胜枚举。这种相对成熟使它成为扩展到 RLHF 分布式训练这一新应用的有利选择。事实证明，RLHF 的许多核心 RL 进展，就是在设法用一种熟悉的算法更新如此大的模型（后文详述）。

先把这个微调任务形式化为一个 RL 问题。**策略**是一个语言模型：接受提示，返回一段文本序列（或文本上的概率分布）。该策略的**动作空间**是对应语言模型词表的全部 token（通常约 5 万 token）；**观测空间**是所有可能输入 token 序列的分布，相对以往 RL 应用而言维度极大（维度约为词表大小 ^ 输入 token 序列长度）。**奖励函数**是偏好模型与策略偏移约束的组合。

奖励函数把前面讨论的所有模型整合进一个 RLHF 流程。给定数据集中的提示 *x*，文本 *y* 由当前迭代微调中的策略生成。把生成的文本与原提示拼接后输入偏好模型，返回一个标量的"可偏好度" rθ r_\theta rθ​。另外，把 RL 策略每个 token 的概率分布与初始模型的分布比较，计算二者差异的惩罚。OpenAI、Anthropic 和 DeepMind 的多篇论文中，这个惩罚被设计为这些 token 分布序列之间 Kullback–Leibler [(KL) 散度](https://en.wikipedia.org/wiki/Kullback%E2%80%93Leibler_divergence)的缩放版本，记作 rKL r_\text{KL} rKL​。KL 散度项惩罚 RL 策略在每个训练 batch 中偏离初始预训练模型太远，这有助于让模型输出保持连贯。没有这个惩罚，优化可能开始生成胡言乱语却能骗过奖励模型给出高分。实践中，KL 散度通过对两个分布采样来近似（John Schulman 在[这里](http://joschu.net/blog/kl-approx.html)有解释）。最终送入 RL 更新规则的奖励是 r=rθ−λrKL r = r_\theta - \lambda r_\text{KL} r=rθ​−λrKL​。

一些 RLHF 系统在奖励函数中加了更多项。例如 OpenAI 在 InstructGPT 上成功实验了把额外预训练梯度（来自人工标注集）混入 PPO 更新规则。随着 RLHF 被继续研究，这个奖励函数的形式大概率还会演化。

最后，**更新规则**就是 PPO 对参数的更新——在当前数据 batch 上最大化奖励指标（PPO 是 on-policy 的，即参数只用当前 batch 的提示-生成对更新）。PPO 是一种信赖域优化算法，用梯度约束确保更新步不会破坏学习过程的稳定。DeepMind 对 Gopher 用了类似的奖励设置，但用[同步优势演员-评论家](http://proceedings.mlr.press/v48/mniha16.html?ref=https://githubhelp.com)（A2C）优化梯度——这与 PPO 明显不同，且尚未被外部复现。

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/rlhf/rlhf.png)

*技术细节说明：上图看起来像是两个模型对同一提示生成不同的回答，实际发生的是：RL 策略生成文本，然后把该文本喂给初始模型，算出它的相对概率用于 KL 惩罚。训练期间初始模型不受梯度更新影响。*

RLHF 还可以选择从这一步继续迭代更新奖励模型和策略。随着 RL 策略更新，用户可以持续把这些新输出与模型的早期版本做排序对比。多数论文尚未讨论如何实现这一操作——要收集这类数据，部署形态只对拥有活跃用户群的对话智能体可行。Anthropic 讨论过这种选项，称为 *Iterated Online RLHF*（见原[论文](https://arxiv.org/abs/2204.05862)），把策略的各代版本纳入模型间的 ELO 排名体系。这引入了策略与奖励模型共同演化的复杂动态，是一个复杂且开放的研究问题。

## RLHF 的开源工具

最早用于对 LM 做 RLHF 的[代码](https://github.com/openai/lm-human-preferences)是 OpenAI 在 2019 年发布的 TensorFlow 实现。

如今 PyTorch 已经有几个活跃的 RLHF 仓库，都是从它发展而来的。主要有 Transformers Reinforcement Learning（[TRL](https://github.com/lvwerra/trl)）、源自 TRL fork 的 [TRLX](https://github.com/CarperAI/trlx)，以及 Reinforcement Learning for Language models（[RL4LMs](https://github.com/allenai/RL4LMs)）。

TRL 旨在用 PPO 在 Hugging Face 生态中微调预训练 LM。TRLX 是 [CarperAI](https://carper.ai/) 打造的 TRL 扩展 fork，面向更大模型的在线和离线训练。目前 TRLX 的 API 已能以 LLM 部署所需的规模（如 33B 参数）用 PPO 和隐式语言 Q-learning [ILQL](https://sea-snell.github.io/ILQL_site/) 进行生产就绪的 RLHF。TRLX 的后续版本将支持最高 200B 参数的语言模型。也因此，与 TRLX 打交道是为有这种规模经验的机器学习工程师优化的。

[RL4LMs](https://github.com/allenai/RL4LMs) 提供了用多种 RL 算法（PPO、NLPO、A2C 和 TRPO）、奖励函数和指标来微调与评估 LLM 的积木。该库易于定制，可以在任意用户指定的奖励函数上训练任何 encoder-decoder 或 encoder-only transformer LM。值得注意的是，它在[近期工作](https://arxiv.org/abs/2210.01241)中的大量任务（约 2000 组实验）上经过充分测试和基准验证，总结出若干实用结论：数据预算对比（专家示范 vs 奖励建模）、如何处理 reward hacking、如何应对训练不稳定等。RL4LMs 当前的计划包括大模型的分布式训练和新 RL 算法。

TRLX 和 RL4LMs 都在大力开发中，很快会有更多功能。

Anthropic 创建的大规模 [数据集](https://huggingface.co/datasets/Anthropic/hh-rlhf)也在 Hub 上可用。

## RLHF 的下一步？

这些技术尽管极具前景和影响力，吸引了 AI 领域最大的研究机构，仍有明显的局限。模型虽然更好了，但依然可能输出有害或失实的内容，而且毫无不确定性。这种不完美代表了 RLHF 的长期挑战与动力——工作在本质上是人类的问题域，就意味着永远不存在一条让模型可以被标记为*完成*的清晰终点线。

部署 RLHF 系统时，人类偏好数据的收集非常昂贵，因为训练环路之外需要直接引入其他人类工作者。RLHF 的表现上限就是其人类标注的质量，标注有两种形态：人类生成文本（如 InstructGPT 中对初始 LM 的微调），以及对模型输出之间人类偏好的标签。

针对特定提示写出高质量人类文本代价很高，往往要雇佣专职人员（而不能指望产品用户或众包）。好在多数 RLHF 应用中奖励模型训练的数据规模（约 5 万标注偏好样本）并没有那么贵。但对学术实验室来说仍是难以承受的成本。目前面向通用语言模型的大规模 RLHF 数据集只有一个（来自 [Anthropic](https://huggingface.co/datasets/Anthropic/hh-rlhf)），另有若干小规模任务专用数据集（如 [OpenAI](https://github.com/openai/summarize-from-feedback) 的摘要数据）。RLHF 数据的第二个挑战是：人类标注员之间常常意见不一，这给训练数据带来巨大方差，却又没有标准答案。

尽管有这些局限，仍有大片未被探索的设计空间能让 RLHF 取得长足进步。其中许多属于改进 RL 优化器的范畴。PPO 是相对古老的算法，但没有任何结构性原因阻止其他算法为现有 RLHF 流程带来收益和变体。微调 LM 策略时，反馈部分的一大开销是策略生成的每段文本都要过一遍奖励模型（它在标准 RL 框架里扮演环境的一部分）。为避免这些昂贵的大模型前向计算，可以把离线 RL 用作策略优化器。近期出现了新算法，如[隐式语言 Q-learning](https://arxiv.org/abs/2206.11871)（ILQL）[（CarperAI 关于 ILQL 的演讲）]，恰好契合这类优化需求。RL 过程中其他核心权衡（如探索-利用的平衡）也没有被系统记录。探索这些方向，至少能加深对 RLHF 工作原理的理解，说不定还能带来性能提升。

我们在 2022 年 12 月 13 日（周二）办了一场讲座，内容在本文基础上做了拓展，可以在[这里](https://www.youtube.com/watch?v=2MBJOuVq380&feature=youtu.be)观看！

#### 延伸阅读

以下是迄今 RLHF 领域最重要的论文列表。这个领域随深度强化学习（约 2017 年）的兴起而流行起来，如今已扩展为众多大型科技公司对 LLM 应用的广泛研究。先列几篇在聚焦 LM 之前的 RLHF 论文：

- [TAMER: Training an Agent Manually via Evaluative Reinforcement](https://www.cs.utexas.edu/~pstone/Papers/bib2html-links/ICDL08-knox.pdf)（Knox 和 Stone 2008）：提出一个学习型智能体，人类对其所采取的动作迭代地给分，从而学出奖励模型。
- [Interactive Learning from Policy-Dependent Human Feedback](http://proceedings.mlr.press/v70/macglashan17a/macglashan17a.pdf)（MacGlashan 等 2017）：提出演员-评论家算法 COACH，用人类反馈（正负都有）来调节优势函数。
- [Deep Reinforcement Learning from Human Preferences](https://proceedings.neurips.cc/paper/2017/hash/d5e2c0adad503c91f91df240d0cd4e49-Abstract.html)（Christiano 等 2017）：在 Atari 轨迹之间的偏好上应用 RLHF。
- [Deep TAMER: Interactive Agent Shaping in High-Dimensional State Spaces](https://ojs.aaai.org/index.php/AAAI/article/view/11485)（Warnell 等 2018）：扩展 TAMER 框架，用深度神经网络建模奖励预测。
- [A Survey of Preference-based Reinforcement Learning Methods](https://www.jmlr.org/papers/volume18/16-634/16-634.pdf)（Wirth 等 2017）：把上述工作汇总，并附大量参考文献。

下面是展示 RLHF 在 LM 上表现的"关键"论文快照（该列表仍在增长）：

- [Fine-Tuning Language Models from Human Preferences](https://arxiv.org/abs/1909.08593)（Ziegler 等 2019）：早期论文，研究奖励学习对四个特定任务的影响。
- [Learning to summarize with human feedback](https://proceedings.neurips.cc/paper/2020/hash/1f89885d556929e98d3ef9b86448f951-Abstract.html)（Stiennon 等 2020）：把 RLHF 用于文本摘要任务。相关后续还有 [Recursively Summarizing Books with Human Feedback](https://arxiv.org/abs/2109.10862)（OpenAI Alignment Team 2021），用人类反馈摘要书籍。
- [WebGPT: Browser-assisted question-answering with human feedback](https://arxiv.org/abs/2112.09332)（OpenAI，2021）：用 RLHF 训练一个能上网浏览的智能体。
- InstructGPT：[Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155)（OpenAI Alignment Team 2022）：把 RLHF 应用于通用语言模型 [（InstructGPT 博客）](https://openai.com/blog/instruction-following/)。
- GopherCite：[Teaching language models to support answers with verified quotes](https://www.deepmind.com/publications/gophercite-teaching-language-models-to-support-answers-with-verified-quotes)（Menick 等 2022）：用 RLHF 训练 LM，回答时附带具体引用。
- Sparrow：[Improving alignment of dialogue agents via targeted human judgements](https://arxiv.org/abs/2209.14375)（Glaese 等 2022）：用 RLHF 微调对话智能体。
- [ChatGPT: Optimizing Language Models for Dialogue](https://openai.com/blog/chatgpt/)（OpenAI 2022）：用 RLHF 训练 LM，作为通用聊天机器人。
- [Scaling Laws for Reward Model Overoptimization](https://arxiv.org/abs/2210.10760)（Gao 等 2022）：研究 RLHF 中学到的偏好模型的缩放性质。
- [Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback](https://arxiv.org/abs/2204.05862)（Anthropic，2022）：详尽记录如何用 RLHF 训练一个有用且无害的 LM 助手。
- [Red Teaming Language Models to Reduce Harms: Methods, Scaling Behaviors, and Lessons Learned](https://arxiv.org/abs/2209.07858)（Ganguli 等 2022）：详细记录"发现、度量并尝试减少[语言模型]潜在有害输出"的努力。
- [Dynamic Planning in Open-Ended Dialogue using Reinforcement Learning](https://arxiv.org/abs/2208.02294)（Cohen 等 2022）：用 RL 增强开放式对话智能体的会话能力。
- [Is Reinforcement Learning (Not) for Natural Language Processing?: Benchmarks, Baselines, and Building Blocks for Natural Language Policy Optimization](https://arxiv.org/abs/2210.01241)（Ramamurthy 和 Ammanabrolu 等 2022）：讨论 RLHF 开源工具的设计空间，并提出新算法 NLPO（自然语言策略优化）作为 PPO 的替代。
- [Llama 2](https://arxiv.org/abs/2307.09288)（Touvron 等 2023）：包含大量 RLHF 细节的高影响力开放访问模型。

这个领域是多学科的交汇点，因此还能在其他方向找到相关资源：

- 指令的持续学习（[Kojima 等 2021](https://arxiv.org/abs/2108.04812)、[Suhr 和 Artzi 2022](https://arxiv.org/abs/2212.09710)）或基于用户反馈的 bandit 学习（[Sokolov 等 2016](https://arxiv.org/abs/1601.04468)、[Gao 等 2022](https://arxiv.org/abs/2203.10079)）
- 更早的使用其他 RL 算法做文本生成的历史（并非都含人类偏好），例如在循环神经网络上（[Ranzato 等 2015](https://arxiv.org/abs/1511.06732)）、用于文本预测的演员-评论家算法（[Bahdanau 等 2016](https://arxiv.org/abs/1607.07086)），或把人类偏好加入该框架的早期工作（[Nguyen 等 2017](https://arxiv.org/abs/1707.07402)）。

**引用**：如果你在工作中觉得本文有用，请考虑引用我们的工作，正文引用格式：

```
Lambert, et al., "Illustrating Reinforcement Learning from Human Feedback (RLHF)", Hugging Face Blog, 2022.
```

BibTeX 引用：

```
@article{lambert2022illustrating,
  author = {Lambert, Nathan and Castricato, Louis and von Werra, Leandro and Havrilla, Alex},
  title = {Illustrating Reinforcement Learning from Human Feedback (RLHF)},
  journal = {Hugging Face Blog},
  year = {2022},
  note = {https://huggingface.co/blog/rlhf},
}
```

*感谢 [Robert Kirk](https://robertkirk.github.io/) 修正了关于 RLHF 具体实现的若干事实性错误。感谢 Stas Bekman 修正错别字和含混表述。感谢 [Peter Stone](https://www.cs.utexas.edu/~pstone/)、[Khanh X. Nguyen](https://machineslearner.com/) 和 [Yoav Artzi](https://yoavartzi.com/) 帮助把相关工作列表向更早的历史扩展。感谢 [Igor Kotenkov](https://www.linkedin.com/in/seeall/) 指出 RLHF 流程中 KL 惩罚项、图示及文字描述中的技术错误。*
