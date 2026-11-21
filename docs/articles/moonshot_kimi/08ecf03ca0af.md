---
vendor: moonshot_kimi
title: Agent Swarm
original_title: 
url: https://www.kimi.com/blog/agent-swarm
date: 2026-02-09
lang: zh
captured: 2026-11-21
extractor: readability-v1
translator: agent
status: translated
body_sha: 3e3c5bd8ac42
---

# Kimi 推出 Agent Swarm：让 100 个 AI agent 为你工作

![Introducing Agent Swarm](https://kimi-file.kimi.ai/prod-chat-kimi/kfs/4/2/2026-02-13/1d67gvgudcmosb3rlf92g?x-tos-process=image%2Fauto-orient%2C1%2Fstrip%2Fignore-error%2C1)

2025 年，你走进任何一场 AI 大会，可能都会听到同一套福音：更快的推理、更长的上下文窗口、更低的推理成本。

仿佛这些年我们一直在打磨同一把锤子，让它更轻、更结实、配重更精准，却从没问过一句：木匠仍然只有两只手，一天仍然只有二十四小时。

**现在，Kimi 推出 Agent Swarm。** 它不是一把更好的锤子，它是整个车间的重建。

这不是一个“许多 AI agent 协同工作”的故事。我们要建的是一种有老板、有员工、有分工的组织结构，只不过这个组织不是由人设计的。**它自己设计自己。**

当你让 Agent Swarm 研究一个课题时，你指挥的不再是一个助手。你是在雇一位 CEO，由它自己去找到研究员、分析师、事实核查员，全部当场招齐。**而你不需要事无巨细地盯。**

但要走到这一步，我们必须先面对一个过去一直绕开的问题：

## 单 agent 推理的局限

在测试时，我们究竟能把一个模型推到多远？

这个问题其实与智能无关。今天 AI 推理真正的瓶颈，是单 agent 顺序执行这一模式本身。

无论你是想拉长模型能处理的任务跨度（研究者称之为长程任务），还是在推理过程中动态扩展算力与结构（测试时扩展），单 agent 顺序执行模式都会撞墙。

举个例子：让一个单 agent 深度研究工具调研一百家公司，或综合几十篇论文。任务越往后走，context 窗口越满。系统只好退回到简单的历史折叠或摘要，为新 token 腾出位置。这种压缩是有损的，后续推理随之退化。

这不是 bug，也不是暂时性限制。这是 context 窗口、时间，以及把长程推理交给单个 agent 所共同设定的结构性天花板。

## 向外扩展，而不只是向上扩展

多年来，AI 的主流叙事一直是扩展：更大的模型、更多的参数、更高的基准分数。这套叙事确实成果斐然。但纵向扩展有天花板——物理的、经济的，或许还有智力的。

横向扩展不一样。一个大脑，对比许多个大脑。单个模型是一位专家；一张自组织的网络则是一家公司、一间实验室、一个情报机构。

2025 年 6 月，我们推出 Kimi Researcher 后不久，团队里一位成员——就称她为“热衷炒股的业余选手”吧——冒出一个看上去很简单的想法：Kimi 能不能每天自动收集股票信息？

她让 Kimi 查新闻看宏观趋势，查历史涨停数量，条件符合就再往下挖，最后综合。她写了一个 Python 工作流，一串层层嵌套的 if-else。

写到第一百行，她停手了。*“我这是在手写一个多 agent 系统。”*

如果模型会调用工具、能处理长程任务，为什么不能自己搭架构？自己决定何时并行、招谁、怎么分派？

**未来不是更好的单 agent，而是会组建组织的 agent。** Agent Swarm 就诞生于这个假设。

数字只能说明一部分。借助 Agent Swarm，Kimi K2.5 可以：

- 部署最多 **100 个 sub-agent** 并行工作
- 执行超过 **1,500 次工具调用**
- 比顺序执行**快 4.5 倍**地交付更好的结果

## Agent Swarm 最佳实践

显然，Agent Swarm 擅长的是可以并行的活：大范围调研、批量下载、多文件处理、多角度分析、长篇写作。

但更深的收益在结构层面：它创造了**建设性分歧的条件**——让彼此独立的 agent 各自得出结论，再迫使它们达成一致。**它从结构上避免了群体思维。**

所以在下面这些场景里，我们建议你亲自体验一下 Agent Swarm 的魔力。

### 规模化发现

从最简单的情况开始：找**一大堆**很难找的东西。

假设你需要 100 个细分 YouTube 领域各自的前 3 名创作者。K2.5 Agent Swarm 会先研究并界定每个领域，然后自主**创建 100 个 sub-agent 并行搜索。**

又或者你想收齐 Paul Graham 的 200 多篇文章，它们散落在个人网站、旧博客、演讲转录稿里。K2.5 Agent Swarm 可以派出专门的 sub-agent 去搜索、下载、分类、摘要并汇编。它们合力把 **200 多篇原文**整理进 **6 个按主题划分的文件夹**，并产出一份完整的总结报告。

![100 Sub-agents Hunting for Creators](https://kimi-file.kimi.ai/prod-chat-kimi/kfs/4/2/2026-02-09/1d64nsivf2ena627qcitg?x-tos-process=image%2Fauto-orient%2C1%2Fstrip%2Fignore-error%2C1)

> 100 Sub-agents Hunting for Creators: https://www.kimi.ai/share/19c40eea-b272-8ef2-8000-0000af5e0baa

### 规模化输出

除了收集零散信息，你还可以让 Agent Swarm **消化大体量文档集**，协调不同的专家角色，**产出书籍篇幅的专业报告。**

比如让它基于四十篇社会心理学 PDF 生成一份 100 页的文献综述。K2.5 Agent Swarm 把任务拆到整个文档集上，派出多个专攻写作的 sub-agent。各自认领特定章节，输出再被综合成一份 **100 页、双栏**的学术文档，引文与参考文献格式齐全。

![Generate 100-Page Literature Review from 40 PDFs](https://kimi-file.kimi.ai/prod-chat-kimi/kfs/4/2/2026-02-09/1d64nuepl51jas5bh88fg?x-tos-process=image%2Fauto-orient%2C1%2Fstrip%2Fignore-error%2C1)

> Generate 100-Page Literature Review from 40 PDFs: https://www.kimi.ai/share/19c4106b-89b2-8361-8000-0000d07b8235

### 规模化视角

最有意思的用法，是你需要分歧本身——想同时从多个视角看一个问题。

**要发布一个复杂产品？** 派一支专家团队：怀疑派的 VC 质疑单位经济模型，资深 PM 担心技术债，伦理学家盯住暗黑模式，客户成功负责人替边缘场景说话。

![Get your product plan reviewed by a team of experts](https://kimi-file.kimi.ai/prod-chat-kimi/kfs/4/2/2026-02-09/1d64nu0d3v89kkema91ag?x-tos-process=image%2Fauto-orient%2C1%2Fstrip%2Fignore-error%2C1)

> Get your product plan reviewed by a team of experts: https://www.kimi.ai/share/19c40bc9-31a2-8533-8000-0000bad59b7a

**或者探索不同的故事走向。** 你可以让 20 位不同文学风格的作家续写刘慈欣的《三体》：从弗吉尼亚·伍尔夫式的内心独白，到博尔赫斯式的观念迷宫、卡夫卡式的荒诞世界，再到加西亚·马尔克斯式由循环宿命塑造的故事。

![Let 20 writers create alternative endings for The Three-Body Problem](https://kimi-file.kimi.ai/prod-chat-kimi/kfs/4/2/2026-02-09/1d64nvf7f2ena627qcve0?x-tos-process=image%2Fauto-orient%2C1%2Fstrip%2Fignore-error%2C1)

> Let 20 writers create alternative endings for The Three-Body Problem: https://www.kimi.ai/share/19c409c8-8692-821a-8000-0000070ad369

## 现已向顶级订阅用户开放

你过去拥有的 Kimi Agent 只是一位勤勉的研究员。现在你拥有的 Kimi Agent Swarm 是一支专家团队：各有专长、并行工作，能同时容纳互相矛盾的观点。

这是一个早期研究预览版。我们会继续加固架构，加入 sub-agent 之间的直接通信、并行宽度的动态控制——但底座已经能承接你最难的工作。

在 AI 时代，识字率也许要按我们用掉多少 token 来衡量。

所以，敲下你的 prompt，让 Kimi 替你自主指挥 100 个 sub-agent：[https://www.kimi.com/agent-swarm](https://www.kimi.com/en/?agent=1&swarm=1)
