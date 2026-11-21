---
vendor: moonshot_kimi
title: Agent Swarm
original_title: 
url: https://www.kimi.com/blog/agent-swarm
date: 2026-02-09
lang: zh
captured: 2026-11-21
extractor: readability-v1
translator: llm
status: translated
body_sha: b9df2eebb959
---

# Kimi 推出 Agent Swarm：让 100 个 AI Agent 为你工作

![Introducing Agent Swarm](https://kimi-file.kimi.ai/prod-chat-kimi/kfs/4/2/2026-02-13/1d67gvgudcmosb3rlf92g?x-tos-process=image%2Fauto-orient%2C1%2Fstrip%2Fignore-error%2C1)

2025 年，如果你走进任何一场 AI 大会，可能都会听到同一套福音：更快的推理速度、更长的上下文窗口、更低的推理成本。

仿佛我们花了多年时间打磨这把锤子，让它更轻、更强、重心更精准，却从未质疑过一个事实：木匠仍然只有两只手，一天仍然只有二十四小时。

**现在，Kimi 推出 Agent Swarm。** 它不是一把更好的锤子。它是对整个车间的重建。

这不是一个“多个 AI Agent 协同工作”的故事。我们要构建的是一种拥有老板、员工和分工的组织结构，只不过这个组织不是由人类设计的。**它自己设计自己。**

当你让 Agent Swarm 研究一个课题时，你不再是在指挥一个助手。你是在雇佣一位 CEO，由它来帮忙寻找研究员、分析师、事实核查员，全部当场自主招聘。**而你不需要事无巨细地管理。**

但要做到这一点，我们必须直面一个过去一直在回避的问题：

## 单 Agent 推理的局限

在测试阶段，我们究竟能把一个模型推到多远？

这个问题本质上与智能无关。当今 AI 推理的真正瓶颈，是单 Agent 顺序执行模型本身。

无论你是想延长模型能够处理的任务长度（研究者称之为长程任务），还是在推理过程中动态扩展算力和结构（测试时扩展），单 Agent 顺序执行模型都会撞墙。

举个例子，让一个单 Agent 深度研究工具调研一百家公司，或综合数十篇论文。随着任务推进，上下文窗口被填满。系统退回到简单的历史折叠或摘要，以便为新 token 腾出空间。这种压缩是有损的，后续推理质量随之下降。

这不是 bug，也不是临时性限制。这是上下文窗口、时间，以及依赖单一 Agent 管理长程推理所施加的结构性天花板。

## 向外扩展，而不只是向上扩展

多年来，AI 领域的主流叙事一直是扩展：更大的模型、更多的参数、更好的基准分数。这一叙事带来了非凡的成果。但纵向扩展存在天花板——物理上的、经济上的，或许还有智力上的。

横向扩展则不同。一个大脑对比许多个大脑。单一模型是一位专家。一个自组织网络则是一家公司、一个实验室、一个情报机构。

2025 年 6 月，在我们推出 Kimi Researcher 后不久，团队里一位成员——我们姑且称她为“热情的业余股票交易员”——有了一个看似简单的想法：Kimi 能不能自动收集股票的每日信息？

她让 Kimi 查新闻看宏观趋势。查询历史涨停数量。条件匹配就进一步深挖。综合。她写了一个 Python 工作流，一串级联的 if-else 语句。

写到第一百行，她停下了。*“我这是在手写一个多 Agent 系统。”*

如果模型能够使用工具并处理长程任务，为什么它们不能自己架构自己？决定何时并行、雇佣谁、如何委派？

**未来不是更好的单 Agent。而是能够构建组织的 Agent。** Agent Swarm 正是诞生于这一假设。

数字说明了部分故事。借助 Agent Swarm，Kimi K2.5 可以：

- 部署最多 **100 个子 agent** 并行工作
- 执行超过 **1,500 次工具调用**
- 比顺序执行**快 4.5 倍**地交付更好的结果

## Agent Swarm 最佳实践

显然，Agent Swarm 在可并行的工作中表现出色：广泛调研、批量下载、多文件处理、多角度分析、长文写作。

但更深层的收益是结构性的，它创造了**建设性分歧的条件**——让独立的 agent 得出不同结论，然后强制进行调和。**它从结构上避免了群体思维。**

因此在以下场景中，我们建议你体验 agent swarm 的魔力。

### 规模化发现

从最简单的场景开始：寻找**海量难以找到的东西**。

假设你需要 100 个细分 YouTube 领域中的前 3 位创作者。K2.5 Agent Swarm 会先研究并定义每个领域，然后自主**创建 100 个子 agent 进行并行搜索。**

或者你想收集所有 200 多篇 Paul Graham 的文章，它们散落在个人网站、旧博客、演讲转录稿中。K2.5 Agent Swarm 可以分配专门的子 agent 去搜索、下载、分类、总结并汇编 Paul Graham 的文章。它们共同将 **200 多篇原始文章**整理进 **6 个主题文件夹**，并产出一份全面的总结报告。

![100 Sub-agents Hunting for Creators](https://kimi-file.kimi.ai/prod-chat-kimi/kfs/4/2/2026-02-09/1d64nsivf2ena627qcitg?x-tos-process=image%2Fauto-orient%2C1%2Fstrip%2Fignore-error%2C1)

> 100 Sub-agents Hunting for Creators: https://www.kimi.ai/share/19c40eea-b272-8ef2-8000-0000af5e0baa

### 规模化输出

除了收集零散信息，你还可以让 Agent Swarm **消化海量文档集**，并协调专家角色**产出书籍长度的专业级报告。**

例如，让它从四十篇社会心理学 PDF 生成一份 100 页的文献综述。K2.5 Agent Swarm 将任务分解到整个文档集上，部署多个专注写作的子 agent。每个子 agent 负责特定章节，它们的输出被综合成一份 **100 页、双栏**的学术文档，引文和参考文献格式完整。

![Generate 100-Page Literature Review from 40 PDFs](https://kimi-file.kimi.ai/prod-chat-kimi/kfs/4/2/2026-02-09/1d64nuepl51jas5bh88fg?x-tos-process=image%2Fauto-orient%2C1%2Fstrip%2Fignore-error%2C1)

> Generate 100-Page Literature Review from 40 PDFs: https://www.kimi.ai/share/19c4106b-89b2-8361-8000-0000d07b8235

### 规模化视角

最有趣的用例是当你需要分歧本身——当你想同时从多个视角审视一个问题。

**面对一次复杂的产品发布？** 部署一支专家团队：持怀疑态度的 VC 质疑单位经济模型，资深 PM 担心技术债，伦理学家探查暗黑模式，客户成功负责人为边缘案例发声。

![Get your product plan reviewed by a team of experts](https://kimi-file.kimi.ai/prod-chat-kimi/kfs/4/2/2026-02-09/1d64nu0d3v89kkema91ag?x-tos-process=image%2Fauto-orient%2C1%2Fstrip%2Fignore-error%2C1)

> Get your product plan reviewed by a team of experts: https://www.kimi.ai/share/19c40bc9-31a2-8533-8000-0000bad59b7a

**或者探索不同的故事走向。** 你可以让 20 位不同文学风格的作家续写刘慈欣的《三体》：从弗吉尼亚·伍尔夫式的内心独白，到博尔赫斯式的思想迷宫，卡夫卡式的荒诞世界，以及加西亚·马尔克斯式由重复命运塑造的故事。

![Let 20 writers create alternative endings for The Three-Body Problem](https://kimi-file.kimi.ai/prod-chat-kimi/kfs/4/2/2026-02-09/1d64nvf7f2ena627qcve0?x-tos-process=image%2Fauto-orient%2C1%2Fstrip%2Fignore-error%2C1)

> Let 20 writers create alternative endings for The Three-Body Problem: https://www.kimi.ai/share/19c409c8-8692-821a-8000-0000070ad369

## 现已向顶级订阅用户开放

你曾经拥有的 Kimi Agent 是一位 single、勤勉的研究员。你现在拥有的 Kimi Agent Swarm 是一支专家团队：专业化、并行化，能够同时持有相互矛盾的观点。

这是一个早期研究预览。我们将继续加固架构，引入子 agent 之间的直接通信、并行宽度的动态控制——但基础已经为你的最严苛工作准备就绪。

在 AI 时代，素养或许可以用我们消耗多少 token 来衡量。

所以输入你的提示词，让 Kimi 为你自主指挥 100 个子 agent：[https://www.kimi.com/agent-swarm](https://www.kimi.com/en/?agent=1&swarm=1)
