---
vendor: huggingface
title: 把来源弄对，而不只是把事实弄对：面向 MCP Agent 的 source-aware 校验
original_title: Getting the Source Right, Not Just the Fact: Source-Aware Verification for MCP Agents
url: https://huggingface.co/blog/MultiverseComputingCAI/getting-the-source-right-not-just-the-fact-source
date: 2024-04-11
lang: zh
captured: 2026-10-10
extractor: readability-v1
translator: agent
status: translated
body_sha: 945b447078e4
---

# 把来源弄对，而不只是把事实弄对：面向 MCP Agent 的 source-aware 校验

团队

文章

发布于
					September 29, 2026

点赞

21

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/668e37fd9c9aa124a3c867e8/4ivwrPQnZGMDF6ovxnAdA.jpeg)](https://huggingface.co/AntonioTN)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/68aea9113e6515ab6246bc1a/Nw5J61eDhzNo-aHDvCzlg.jpeg)](https://huggingface.co/ander-alvarez)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/1iQUUZFQh6BZXCgGY7zJT.png)](https://huggingface.co/AlexDGenu)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/QU3ijZPXiAWJKJQTof3nF.png)](https://huggingface.co/DuckDuckDown)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/tGmQJzeT9SYL_sK839ifI.png)](https://huggingface.co/AlgoEnergy)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/3xs4KD-K8_TSwUNSbWp9o.png)](https://huggingface.co/fakoor)

Antonio Tiene

AntonioTN

MultiverseComputingCAI

Ander Alvarez Sanz

ander-alvarez

MultiverseComputingCAI

Oliver Wirjadi

oliverwirjadi

MultiverseComputingCAI

Alessandro Genuardi

AlexDGenu

MultiverseComputingCAI

使用工具的 LLM agent 不再只从单篇检索到的段落里取信息。借助 [Model Context Protocol (MCP)](https://modelcontextprotocol.io)，一个 agent 可以调用搜索工具、查看结构化的患者或账户记录、查询数据库、拉取元数据，然后把这一切编织进同一个回答。这让那个关于事实性的老问题比看上去更微妙。为核查 LLM 回答而建立的绝大多数系统，从 [RAGAS faithfulness](https://github.com/explodinggradients/ragas) 到 MiniCheck、AlignScore、SummaC 这类细粒度检查器，问的都是：一旦可用证据被汇总到一处，某条论断是否被这些证据支撑。在它们的常见形态里，这些系统并不告诉我们每条论断是由哪个 MCP 工具输出支撑的，也不告诉我们那是不是回答里所点名的来源。

我们最新的论文 *ProvenanceGuard: Source-Aware Factuality Verification for MCP-Based LLM Agents*（可在 [Hugging Face](https://huggingface.co/blog/MultiverseComputingCAI/%5BHF-PAPER-LINK%5D) 上阅读，在此期间也可读 [arXiv](https://arxiv.org/abs/2606.18037) 版）正是冲着这一空白去的。我们在意的失败模式，我们称之为 cross-source conflation（跨来源混同）：某条论断在证据中的某处是真的，却被归到了错误的来源上。一个 source-blind（对来源无感知）的校验器可能放它通过，因为这个事实在汇总池里确实存在。而一个 source-aware 的校验器不应该放行。

## 问题：在某处被支撑，不等于被正确的来源支撑

设想一个客服 agent 回答："根据账户记录，这个套餐包含 30 天退款窗口。" 这个退款窗口可能完全真实，但它是写在政策文档里的，而不是写在回答所指的那份账户记录里。把两者合并到一起，这条论断看起来就有支撑；把它们分开保留，归属就是错的——而在数据敏感的场景里，错误的归属和错误的事实一样有害。同样的模式也出现在临床 agent 上：一条来自病史工具、针对特定患者的用药细节，一旦回答把它呈现成来自医学文献的发现，就会造成误导。

[![一张对比图：用一条由政策文档支撑却被归到账户记录名下的退款窗口论断，对照展示 source-blind 的汇总支撑与 source-aware 的校验。](https://cdn-uploads.huggingface.co/production/uploads/668e37fd9c9aa124a3c867e8/svnUpzhFgTpLqOF_bRDHl.png)](https://cdn-uploads.huggingface.co/production/uploads/668e37fd9c9aa124a3c867e8/svnUpzhFgTpLqOF_bRDHl.png)

*一条论断可以由某个 MCP 来源支撑，而回答却把它归到另一个来源上。source-blind 打分在汇总后的证据里看到支撑，于是放行；ProvenanceGuard 则另外检查提供支撑的来源是否与回答所述或所暗示的那个来源一致。来源：论文 Figure 1。*

这正是为什么 faithfulness 分数尽管有用，对 MCP agent 来说仍然不够。一个回答自带来源信息（provenance），有时是显式的（"根据账户记录"），有时是隐含的。ProvenanceGuard 把论断与来源之间的这层关联保留下来，供人检视。

## ProvenanceGuard 做了什么

ProvenanceGuard 是一个生成后（post-generation）校验层，架在一个黑箱 MCP agent 之上。它在 agent 产出回答之后运行，并且绝不把证据坍缩成一份匿名的 context。相反，它把来源标识一路贯穿整条流水线。它读取捕获到的 MCP trace，包括各工具输出及其 source ID，而无需重新训练 agent。然后它依次做五件事：把回答拆解成一条条具体的论断，为每条论断找出最相关的来源，检查那个来源是否真的支撑它，把该来源与回答所点名或所暗示的来源做比较，最后同时给出逐条论断的来源判定，以及一个全局的、回答层面的放行或拦截决定。

[![流水线示意图：agent 产出回答草稿与 trace，随后 ProvenanceGuard 拆解论断、路由到来源、用 NLI 检查支撑、做校准、检查归属，最终要么放行回答，要么把它送去修复。](https://cdn-uploads.huggingface.co/production/uploads/668e37fd9c9aa124a3c867e8/nDchWzRhBSmscjaa8w5G5.png)](https://cdn-uploads.huggingface.co/production/uploads/668e37fd9c9aa124a3c867e8/nDchWzRhBSmscjaa8w5G5.png)

*校验流程。来源标识在拆解、路由、支撑打分、归属检查与修复的全程都得以保留，而不是被汇总成一池。被拦截的回答可以走 RARR 风格的修复，然后重新校验。来源：论文 Figure 2。*

有几个设计选择值得单独说明。在论文的实验中，我们使用本地模型，以便在受控的离线环境里处理捕获到的 trace：[MiniLM](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) 帮助找到相关来源，一个 [DeBERTa NLI verifier model](https://huggingface.co/MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli) 检查那个来源是否支撑该论断，一个本地语言模型帮助把回答拆成论断。校验器还会仔细核查字面值：源里没有的数字、日期或标识符，不能仅仅因为句子读起来合理就通过。一个经过校准的决定步骤把这些信号合在一起。如果某条回答被拦截，一个 [RARR](https://arxiv.org/abs/2210.08726) 风格的修复步骤可以尝试基于来源的改写，或者一个安全的兜底回答，随后校验器再对它检查一遍。

这些被点名的模型是我们评测所用的配置，并不是 ProvenanceGuard 的硬性要求。同样的论断拆解、来源匹配与决定步骤可以改造到托管模型上，供更偏好云服务的团队使用；但新的配置需要它自己的测试和校准。我们报告的结果来自这套本地配置。它保守的决定策略适合数据敏感的审查场合，在那里，把来源弄对比给出尽可能快的回答更重要。

## 结果

我们在一个医疗 agent 的回答上测试了 ProvenanceGuard，这个 agent 用过了患者病历、研究文章以及其他工具。这让我们得到 281 条真实 trace 可供研究。医学是一个有用的试验场，因为来自某个患者病历的事实和来自一般研究的事实不能算作同一个来源。当 agent 保存了它的工具输出与 source ID 的记录时，这套方法也能用在其他领域。在主测试里，人类专家核查了 361 条论断，它们来自 40 条回答，这些回答是从开发该系统所用数据中留出的一部分。

最直接的结果是这个：专家判定有 139 条论断不该通过，而 ProvenanceGuard 抓到了其中的 138 条，只放过 1 条。它另外扣下了 67 条专家认为有支撑的论断，把它们送去复审或修复。这反映了我们所测试的谨慎设置：对某些其实有支撑的论断多看一眼，也好过让没有支撑的论断溜过去。对于来源可识别的论断，在这次测试里它也在大约 86% 的情况下选对了来源。

我们在同样的论断上跑了另外四个支撑检查器。按论文中那个衡量标准——系统在抓到该被拦截的论断与避免不必要拦截之间做得多好——ProvenanceGuard 得分最高。这轮比较里的其他检查器都没有告诉我们每条论断是由哪个工具输出支撑的。ProvenanceGuard 把这层关联记录下来，因此复审者能看到每条论断所核查的来源以及由此得出的决定。

| 校验器 | Reject/block F1 | 是否输出论断到 source ID 的映射 |
| --- | --- | --- |
| ProvenanceGuard（我们的） | **0.802** | 是 |
| MiniCheck | 0.783 | 否 |
| RAGAS Faithfulness | 0.758 | 否 |
| AlignScore | 0.662 | 否 |
| SummaC-ZS | 0.436 | 否 |

*在同一份留出的论断包上计算的二元支撑指标。在拦截这件事上，ProvenanceGuard 追平或超过了 source-blind 基线，同时还给出逐条论断的来源判定。来源：论文摘要与 Table III。*

## 当来源彼此很像时如何核查论断

在另一个更难、包含多个相似来源的独立测试中，ProvenanceGuard 在决定拦截哪些论断上拿到 0.846 的 F1，但在 50.3% 的论断上正确识别出了确切的来源。把相似来源区分开来仍然是一个重要的改进方向。

我们还跑了一个聚焦于错误归属的受控测试：在 50 个案例里我们改动被点名的来源，同时保持支撑证据不变。ProvenanceGuard 抓到了全部 50 次替换。这说明它能够检出明确的来源错误，而那个更难的测试则说明了在多个貌似合理的来源之间做选择的难度。

## 修复被拦截的回答

只有当被拦截的回答还有后续可做时，拦截才有意义。接入 RARR 风格的修复循环后，完整 trace 的那一轮运行处理掉了全部 173 条被拦截的回答，尽管其中 144 条最终落到兜底文本而不是实质性的改写——这是系统在选择不给出一个无法校验的回答，而不是编造一个。在重建的多来源测试 trace 上，一次全新的修复运行解决了最初被拦截的全部 59 条回答，只有两次以兜底收尾。作为一个离线关卡，它的开销不大，在所报告的本地配置上大约每条回答半秒，而 NLI 与路由调用本身只有几十毫秒。

## 为什么这契合 Multiverse Computing

当 agent 从单段落 RAG 走向多工具的 MCP 配置，"某个事实究竟来自哪个来源"这个问题就不再是脚注，而成为事实性含义的一部分。ProvenanceGuard 把这条来源关联逐论断地显现出来。对 Multiverse Computing 而言，这意味着一种检查现有 agent 的办法，并能在需要时把敏感 trace 留在受控环境里。医疗研究只是其中一个用例；只要 agent 的 trace 保留了它的工具与来源，同样的思路就能改造适用。

这种改造已经能在 [NVIDIA NVFlow](https://github.com/NVIDIA/nvflow/pull/9) 上看到：它合并了一个可选的 grounding 校验阶段，用于其金融 agent。该阶段把已经完成的回答对照 agent 检索到的 SEC 摘录做检查，并单独保存各项决定，而不改动原本的 rollout 或训练数据。NVFlow 的这项贡献用的是 ProvenanceGuard 的 source-aware 校验思路；上文讨论的修复循环属于更宽泛的研究系统。

ProvenanceGuard 还以海报形式在 [UC Berkeley 举办的 Agentic AI Summit 2026 上做过展示](https://github.com/aalvsz/provenanceguard/blob/main/poster/ProvenanceGuard_Agentic_AI_Summit_2026_Berkeley.pdf)。

想要完整的技术细节吗——包括路由与 NLI 的推导、校准的消融实验、多来源的压力切片，以及完整的结果表格？请在 [Hugging Face](https://huggingface.co/papers/2606.18037) 上阅读完整论文，或者联系我们团队，聊聊把 source-aware 校验用到你自己的 agent 上。

## 本文提及的模型 2

## 本文提及的论文 1

该作者的更多内容

## 像物理学家一样剪枝 LLM：把 Block 移除当作 Ising 优化问题

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6835694d56d5a69517655698/C3QUBARPGF4kbzJzZaT29.png)

34

September 21, 2026

## 为谁做安全？拒绝某个主题中恰当的那部分，而不是整个主题

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6835694d56d5a69517655698/C3QUBARPGF4kbzJzZaT29.png)

31

September 8, 2026

### 社区

Nomad-link-id

10 天前

对 MCP agent 真正要紧的失败模式比"幻觉"更安静：某条论断在汇总后的工具输出里的*某处*是真的，却被归到了错误的来源。

那种情况下，source-blind 的 faithfulness 依旧可以亮绿灯——这个事实在那锅汤里存在着。source-aware 校验是契约层面的升级：在论断拆解、支撑检查和归属检查的全程保留 tool/source ID，然后给出放行或拦截，并附上复审者真能检视的逐条论断来源判定。

给正在接入 MCP 的团队一个实际的追问：当你的 eval 说"grounded"时，它指的是被任意一个工具输出支撑，还是被回答所点名的那个来源支撑？这是两道不同的发布关卡。在多工具配置里，只有后者能在人类相信这条引用之前抓到跨来源混同。

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/68aea9113e6515ab6246bc1a/Nw5J61eDhzNo-aHDvCzlg.jpeg)](https://huggingface.co/ander-alvarez)

·

ander-alvarez

文章作者

10 天前

你好，谢谢你的评论。你把问题的要害抓得很准。对 ProvenanceGuard 来说，一条论断是"grounded"意味着它被回答所点名或所暗示的那个来源支撑。在工具输出里的别处找到这个事实并不够。在退款窗口那个例子里，政策文档支撑了这个事实，但回答把它记在账户记录名下，所以我们标出这处不一致，并给出来源判定。

mghwaz

10 天前

•

编辑于 10 天前

我粗读了一遍论文，但没找到任何与"用更便宜的 llm agent 来做 source aware judge"的对比。以下是我对论文的理解；

- 一个 LLM 调用多个工具，并用它们的输出生成回答，其中可能陈述许多条论断
- 一条论断可以由（一个或多个）工具的输出支撑，却被错误地归到另一个来源上。
- 基本上是把回答拆成论断，并用 embeddings 为每条找到一个可能的支撑来源。
- 用 NLI 与 random forest 检查所选来源是否支撑该论断；
- 同时在回答里检查该论断是否被归到了正确的来源。

看起来，(2 - 5) 这几步似乎能在 lifecycle 里用基本的 prompts 就完成，前提是你拥有那个执行 agent。如果不是，也可以通过 harness 里的 hooks 以插件形式实现。你们有没有这方面的对比。说到底，random forest 以及这一整套 eng/plumbing，相比"对 traces+ans 再做一次 llm 调用"到底买到了多少东西？

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/68aea9113e6515ab6246bc1a/Nw5J61eDhzNo-aHDvCzlg.jpeg)](https://huggingface.co/ander-alvarez)
- [![](https://huggingface.co/avatars/72f6f613035501a07c402999e7718f5f.svg)](https://huggingface.co/mghwaz)

·

ander-alvarez

文章作者

9 天前

你好，这个问题很合理。一个 source-aware 的 LLM judge 可以完成这些检查，而我们在论文里没有报告与某个更便宜方案的直接对比。

不过，我们的部分动机在于：引入一个 LLM judge 本身就可能给出不一致的判定，或者把来源搞混（正是我们想要抓的那一类错误）。因此第二次 LLM 调用会引入它自己的新错误。ProvenanceGuard 用显式的来源追踪和经过校准的支撑检查，来减少对另一次生成式判断的依赖。你建议的这个对比确实是一项有用的后续研究，可以量化在 accuracy、延迟和成本上的收益。

上传：把图片、音频和视频拖进文本输入框、粘贴，或

点击此处

.

在此轻点或粘贴即可上传图片

· [注册](https://huggingface.co/join?next=%2Fblog%2FMultiverseComputingCAI%2Fgetting-the-source-right-not-just-the-fact-source)或[登录](https://huggingface.co/login?next=%2Fblog%2FMultiverseComputingCAI%2Fgetting-the-source-right-not-just-the-fact-source)以发表评论

点赞

21

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/668e37fd9c9aa124a3c867e8/4ivwrPQnZGMDF6ovxnAdA.jpeg)](https://huggingface.co/AntonioTN)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/68aea9113e6515ab6246bc1a/Nw5J61eDhzNo-aHDvCzlg.jpeg)](https://huggingface.co/ander-alvarez)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/1iQUUZFQh6BZXCgGY7zJT.png)](https://huggingface.co/AlexDGenu)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/QU3ijZPXiAWJKJQTof3nF.png)](https://huggingface.co/DuckDuckDown)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/tGmQJzeT9SYL_sK839ifI.png)](https://huggingface.co/AlgoEnergy)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/3xs4KD-K8_TSwUNSbWp9o.png)](https://huggingface.co/fakoor)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/7sTK8Q_gZRoOz0uaKnVNJ.png)](https://huggingface.co/luke-loan-atlas)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/tI3V8-PZ8d3CC32fzO31e.png)](https://huggingface.co/Stars321123)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/jzzvCtkAVcFuwfuh2k_va.png)](https://huggingface.co/asepsafrudin)
- [![](https://huggingface.co/avatars/327b3a9c4c54e49640d52651c6a8428b.svg)](https://huggingface.co/kbommasani)
- [![](https://huggingface.co/avatars/5f3f1a55b0878bbca0cd10ae8fdf2ed4.svg)](https://huggingface.co/kamal24h)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/Ft9XaIrp9M75oRHfxtCbi.png)](https://huggingface.co/abdullahashraf122)

## 本文提及的模型 2

## 本文提及的论文 1
