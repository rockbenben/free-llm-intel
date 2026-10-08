---
vendor: anthropic
title: Introducing Claude Opus 5.5
original_title: 
url: https://www.anthropic.com/claude-opus-5-5
date: 2026-09-22
lang: zh
captured: 2026-10-08
extractor: readability-v1
translator: agent
status: translated
body_sha: 5f50eaa5f0b8
---

# Claude Opus 5.5

2026 年 9 月 22 日

我们推出 Claude Opus 5.5，这是我们全新 Claude 5.5 家族中的第一个模型。它在大多数工作上的表现达到 Claude Fable 5.1 的水平，而运行成本比 Opus 5 低 40%。

Claude Opus 5.5 是我们发出[为前沿设定节奏](https://darioamodei.com/post/we-must-pace-the-frontier)的呼吁之后的第一个发布版本。发布前它由外部评估方进行了测试，其中包括 [Frontier Design](https://www.imaginefrontier.com/) 和 [METR](https://metr.org/)。在我们的自动化行为审计——这是我们所运行的最全面的对齐测试——上，Opus 5.5 是我们迄今测试过的表现最强的模型。它同时配备了为我们能力最强的模型所开发的那些安全防护。

以下是你对 Opus 5.5 可以期待的一些改进：

**性能。** Opus 5.5 相比 Opus 5 是一次大幅跃升。它成为新的领先模型，早期测试者在他们最复杂的工作上看到了大幅的性能提升。有一位测试者用不到一天完成了一次 680,000 行的代码迁移——这项工作原本需要一个工程团队花上数周。它擅长发现并修复软件中的低效之处：当我们要求它削减一个 web 应用每个页面的加载时间时，Opus 5.5 在 40 次尝试中成功了 39 次，而 Opus 5 只做了一些较小的改进，并且同时改变了应用的行为。另一位测试者让几个 Claude 模型凭一条 prompt 构建一个游戏；凭借图形表现与打磨程度上的优势，Opus 5.5 的得分高于其他任何模型。

**安全。** 在我们的自动化行为审计（一套在数千个模拟场景中测试 Claude 的对齐评测套件）上，Opus 5.5 取得了迄今所有模型中的最好成绩。与近期的模型相比，它不太可能采取难以逆转的行动、也不太可能越过被授予的边界行事；与 Opus 5 相比，它对 prompt injection 的抵抗力更强。我们还将对齐测试的范围扩展到了更长的任务、不可能完成的任务，以及以真实事件为原型建模的场景，尽管它仍然有局限。评测的完整细节见 [Opus 5.5 System Card](https://anthropic.com/claude-opus-5-5-system-card)。

由于 Opus 5.5 在生物学与网络安全方面与 Claude Mythos 5.1 相当，我们为它部署的安全防护与 Claude Fable 5.1 上的类似。经过审核的机构今天就可以申请加入我们的 [Life Sciences Verification Program](https://www.anthropic.com/news/life-sciences-verification-program)，使用 Opus 5.5 进行生物学研究。在未来几周内，我们还将扩大 [Cyber Verification Program](https://support.claude.com/en/articles/14604842-real-time-cyber-safeguards-on-claude-opus-and-sonnet) 的覆盖范围，经过认证的网络安全从业者将能够把 Opus 5.5 用于他们的工作。

**成本与速度。** Opus 5.5 提供服务所需的算力比 Opus 5 更少，其定价也反映了这一点。我们的测试显示，在默认设置下，它在典型工作负载上的成本比 Opus 5 低 40%。输入与输出 token 的价格为每百万 4 美元和 20 美元，比 Opus 5 低 20%。缓存读取（在智能体和编程工作的成本中占大多数）为每百万 token 0.20 美元，比 Opus 5 低 60%。Opus 5.5 生成输出的速度也比 Opus 5 快 30% 以上。

除了降价，我们还提高了 Pro、Max、Team 以及按席位计费的 Enterprise 套餐上的五小时用量上限。我们同时为订阅用户提供一个速率限制重置额度，你现在可以把它存起来，随时想用时再用。

**沟通表达。** Opus 5.5 的交流比此前的模型更自然。早期测试者认为它的写作更清晰、更容易跟上，这回应了我们听到的关于 Opus 5 的一些常见反馈。它把最重要的信息放在最前面，其风格让它在长时间工作会话中成为更好的工作伙伴。正如一位早期测试者所说，「它写作的方式和我一样。」在我们自己的使用中，这让 Opus 5.5 的工作更易于跟随和核查——这既是安全上的收益，也是实用上的收益。

Claude Sonnet 5.5 与 Claude Haiku 5.5 将在未来几周内相继推出，同样带来许多性能、效率与安全方面的改进。

## 性能与性价比

在我们的基准测试中，Claude Opus 5.5 在智能体编程、计算机使用与知识工作方面处于领先。话虽如此，在这样的能力水平上，我们发现基准分差已经变成对真实世界差异较不可靠的指引。在我们自己的使用中，Opus 5.5 与 Claude Fable 5.1 之间的差距比这些分数所暗示的更窄。

|  | Opus 5.5 | Fable 5.1 | Opus 5 | GPT-6 Astra | GPT-5.6 Sol |
| --- | --- | --- | --- | --- | --- |
| 智能体编程 Terminal-Bench 4.0¹ |  |  |  |  |  |
| 智能体编程 Terminal-Bench 4.0¹ | 66.4% | 55.8% | 52.3% | 57.9% | 37.3% |
| 智能体编程 FrontierCode v1.1（Main） |  |  |  |  |  |
| 智能体编程 FrontierCode v1.1（Main） | 54.4% | 50.3% | 48.0% | 53.3% | 47.5% |
| 智能体编程 CursorBench 4.0 |  |  |  |  |  |
| 智能体编程 CursorBench 4.0 | 57.8% | 51.8% | 46.6% | — | 41.7% |
| 知识工作 GDPval-AA v2.1 |  |  |  |  |  |
| 知识工作 GDPval-AA v2.1 | 1846 | 1735 | 1708 | 1542 | 1588 |
| 商业工作流 AutomationBench² |  |  |  |  |  |
| 商业工作流 AutomationBench² | 40.0% | 31.4% | 26.9% | 41.4% | 28.8% |
| 多学科推理 Humanity's Last Exam |  |  |  |  |  |
| 多学科推理 Humanity's Last Exam | 67.7%（带工具） | 65.6%（带工具） | 63.6%（带工具） | 57.2%（带工具） | — |
| 智能体科学研究 Terminal-Bench-Science 0.1³ |  |  |  |  |  |
| 智能体科学研究 Terminal-Bench-Science 0.1³ | 58.7% | 52.6% | 29.0% | 64.6% | 22.4% |
| 计算机使用 OSWorld 2.1 |  |  |  |  |  |
| 计算机使用 OSWorld 2.1 | 81.8%（部分得分） | 80.7%（部分得分） | 74.0%（部分得分） | — | — |
| 视觉图表识别 Chartography |  |  |  |  |  |
| 视觉图表识别 Chartography | 89.0%（带工具） | 88.4%（带工具） | 83.4%（带工具） | — | — |

除非另有说明，所有 Claude Opus 5.5 的结果都使用 max effort 档位的 adaptive thinking。Terminal-Bench 4.0 的结果，Claude Opus 5.5 报告的是 xhigh effort 档位、GPT-6 Astra 报告的是 high effort 档位（由 OpenAI 报告）；这些数字代表每个模型的最高分。Claude Opus 5.5 是在启用其生产环境安全防护的情况下进行评估的。当这些防护介入时，网络安全任务由 Claude Opus 4.8 完成，生物学与前沿 LLM 开发任务由 Claude Opus 5 完成。这很可能压低了 Claude Opus 5.5 在这些基准上的表现。

1** Terminal-Bench 4.0：** 标准差为 Claude Opus 5.5 ±2.6 个百分点，其他 Claude 模型为 ±1.6–2 个百分点。公开排行榜（每项任务 5 次试验，Claude Code harness）报告 Claude Opus 5 为 51.8%；我们的设置复现出 52.3%，在噪声范围之内。GPT-6 Astra 与 GPT-5.6 Sol 的数字以 OpenAI 的报告为准。

2** AutomationBench：** AutomationBench 的结果由 Zapier 运行并报告。这些运行时不启用回退模型，因此安全防护的介入被视为失败——这导致得分低于 Claude Opus 5.5 在实践中所能达到的水平。Claude Opus 5.5 的结果来自 Zapier 在 early access 期间自身的评测。Opus 5、GPT-5.6 Sol 与 GPT-6 Astra 的结果来自 Zapier 的公开排行榜。

3** Terminal-Bench-Science 0.1：** 每个模型的标准差为 ±3.5–5 个百分点。公开排行榜（每项任务 3 次试验，Claude Code harness）报告 Claude Opus 5 为 30.0%；我们的设置复现出 29.0%，在噪声范围之内。GPT-6 Astra 的数字以 OpenAI 的报告为准。

Opus 5.5 的优势非常明确的一点是效率。它每 token 的价格低于 Opus 5，而且每个任务消耗的 token 也更少，综合下来成本下降 40%。

定价

| 每 1M token 价格 | **Claude Opus 5.5** | Claude Opus 5 |
| --- | --- | --- |
| 缓存读取 | **$0.20** | $0.50 |
| 输入 token | **$4** | $5 |
| 输出 token | **$20** | $25 |
| 缓存写入 | **$5** | $6.25 |

Opus 5.5 的 Fast mode 同样在 Claude Code 和 Claude Platform 上可用，速度最高可达 2.5 倍。其价格为每百万输入 token 8 美元、每百万输出 token 40 美元。

## 编程

Opus 5.5 尤其擅长那些时间长、摊子大的工作，比如全代码库范围的迁移与审计。一位早期测试者用它审计并修复了一个 200,000 行的代码库，用时不到三小时，而 Opus 5 花了 20 多小时，并用了 2.5 倍的 token。在一次内部测试中，我们要求 Opus 5.5 和 Fable 5.1 把 HAProxy——一款被广泛使用、用于在多台服务器之间均衡 web 流量负载的软件——从 C 改写成 Rust。两份重写都几乎通过了 HAProxy 自身的回归测试，但 Opus 5.5 用时 9.5 小时，Fable 5.1 用时 12 小时，而成本低 51%。

Opus 5.5 以一小部分成本交付前沿水平的智能体编程结果。在 FrontierCode 的默认 effort 档位上，它击败 GPT-6 Astra，而每任务成本大约只有后者的 20%。在 Terminal Bench 4.0 上，它与 Astra 打平，成本约为 40%；而在 CursorBench 上，它以约三分之一的每任务成本，超出 GPT-5.6 Sol 11 分。

智能体终端编程

智能体编程：FrontierCode

智能体编程：CursorBench

Terminal-Bench 4.0

准确率 vs 成本

Terminal-Bench 4.0 衡量一个模型在命令行界面内完成复杂、多步骤专业任务的能力。Opus 5.5 在默认 effort 档位上击败 max effort 档位的 Opus 5，而成本约为五分之一。它与 GPT-6 Astra 打平，成本约为 40%。

FrontierCode v1.1，主集

准确率 vs 成本

FrontierCode 衡量的是一个智能体的代码改动是否会被合并。在默认 effort（medium）档位上，Opus 5.5 得分 54.6%，高于其他所有模型，以大约五分之一的每任务成本击败了 GPT-6 Astra 的最高分（53.3%）。

CursorBench 4.0

准确率 vs 成本

CursorBench 在取自真实 Cursor 会话的、含义模糊的多文件任务上评估编程智能体。在默认 effort（medium）档位上，Opus 5.5 得分 52.5%，而 Fable 5.1（max）为 51.8%、Opus 5（max）为 46.6%。它以约三分之一的每任务成本，超出 GPT-5.6 Sol 的最高分（41.7%）11 分。

我们的早期测试者也报告了类似的效率与智能提升：

GitHub

Clio

Lovable

Quantium

Spotify

Optiver

Column

Kiro

引言

> “开发者想要的是能承担真实软件工程工作并把它做完的智能体。在我们跨 GitHub Copilot CLI 和 VS Code 的测试中，Claude Opus 5.5 用到的 token 数和步骤数是我们测过的最少之列。在 VS Code 里，它用不到 Opus 5 一半的步骤解决了更多的终端任务。它不只是让单个任务更高效，它正在让开发者更大的项目变得可以达成。”

公司

GitHub

作者

Mario Rodriguez，首席产品官

引言

> “我把一个横跨我们六个仓库的大型工程任务交给 Claude Opus 5.5，让它整夜无人值守地运行。它持续在任务上超过 18 小时，定义我们的服务之间如何相互通信，并逐一弄清每个服务该如何应用这套约定。与 Opus 5 相比，它更快达成里程碑，而且几乎不需要返工。它的代码注释简短而有用，而不是又长又满纸散文。我很难找到什么负面评价可说。”

公司

Clio

作者

Sean Heintz，主任软件工程师

引言

> “对 Lovable 的构建者来说，Opus 5.5 意味着在同样质量下更快构建，无论你是从零开始还是在一个已上线的应用上工作。它只收集一次上下文，做出更少但更完整的编辑，不会卡在反复重试上，收尾所需的步骤少了三分之一到一半，一路用到的 token 也显著更少。”

公司

Lovable

作者

Fabian Hedin，首席技术官兼联合创始人

引言

> “我们在 Chat、Cowork 和 Claude Code 上都测试了 Claude Opus 5.5，覆盖我们团队工作方式的整个范围。一个此前需要 38 次提示、历时四天的复杂编程任务，最后用 11 次提示、三小时完成，产出更接近可用于生产环境，返工也更少。对我们这些需要快节奏解决复杂问题的团队来说，这意味着更少时间花在反复迭代上，更多时间花在审视上：检验假设、对产出做压力测试，为我们的客户落到最佳方案上。”

公司

Quantium

作者

Harley Barnes，AI 技术执行经理

引言

> “有了 Claude Opus 5.5，我们在内部评估中看到了 token 效率的明显提升，因为我们完成同样的任务既更便宜也更快。”

公司

Spotify

作者

Aleksandar Mitic，高级工程师

引言

> “我们在真实的工程与交易台工作上测试模型。在我们的智能体编程任务上，Claude Opus 5.5 大约用一半的轮次、时间和输出 token 就达到了 Opus 5 的质量，把该工作负载的成本降低了 40% 到 50%。它在某个交易台的交易支持套件上创下我们记录过的最高分，通过了此前 Claude 模型失败的任务，并在我们的分析任务上位列全部八个模型之首。”

公司

Optiver

作者

Noyan Tokgozoglu，全球 AI 工程负责人

引言

> “Claude Opus 5.5 把工作委派给 subagent 有效得多，并以富有创造性的方式检查自己的工作。自我验证回路搭起来更容易了。它在我们的云账单中找到了此前模型漏掉的节省机会；在代码评审里，它通过查阅第三方集成的外部文档抓到一个 bug——我们在几个 commit 之前把这个集成建模错了。”

公司

Column

作者

Mitch Fierro，工程

引言

> “智能体发出的每一次调用，都是开发者能切身感受到的时间和成本。在一个基于真实命令行任务的公开基准上，Claude Opus 5.5 解决的问题比 Opus 5 更多，而调用次数少约 40%、token 用量只有一半。对使用 Kiro 构建的开发者来说，这意味着无论是日常任务还是复杂挑战，智能体会话都更快、也更负担得起。Opus 5.5 很快将在 Kiro 上提供。”

公司

Kiro

作者

Deepak Singh，Agentic AI 副总裁

## 最安全的编程智能体

把智能体运行在自己系统内部的企业，需要知道这些智能体是按预期运作的，尤其是当它们自主运行许多小时的时候。Opus 5.5 有一个在每个动作执行之前对它进行筛查的分类器、一个安全团队可以审计的开源沙箱，以及能在漏洞被合并之前就将其捕获的代码评审。

模型本身也具备更强的防御。在 prompt injection 攻击上，我们在所有测过的场景中它都达到或超过 Opus 5，包括编程、工具使用、计算机使用和网页浏览。在 AI 安全公司 Gray Swan 运行的一项基准上，Opus 5.5 与 Fable 5.1 并列，是所有被测模型中 prompt injection 成功率最低的。

## 知识工作

Opus 5.5 是一名可靠而熟练的研究者。在一次内部测试中，我们要求 Opus 5.5、Fable 5.1 和 Opus 5 仅凭它们能在一份 web 拷贝上找到的信息，就某公司的季度表现写一份报告，而在这份拷贝里财报公告很难被定位到。一个自动评分器把每一个数字和每一段引语对照来源做了核查。在不同的 effort 设置下，Opus 5.5 的 18 份报告中有 16 份通过了我们的质量标准，而任何编造的数字或引语都会导致失败。Fable 5.1 和 Opus 5 在任何一次尝试中都没能达到这条标准。

它在财务分析和商业工作上同样很强。Walleye Capital 是一家投资公司，也是早期测试者之一，他们报告说 Opus 5.5 在最低设置下基本解决了他们的评估套件；在更高设置上它表现更好，甚至注意到他们的评估指令里有一处错误并做了纠正。此前没有其他模型发现过这个错误。

在另一项测试中，我们让 Opus 5.5 和 Opus 5 分别分析两家虚构 HR 软件公司之间拟议的并购。每个模型都在 Excel 里搭建一个财务模型，然后把它做成一份高管演示，说明这笔交易按其价格是否划算。两个模型对这笔交易得出了相同的结论，但 Opus 5.5 的模型更周全、它的演示更易读，而 Opus 5 的有若干小错。Opus 5.5 用时 63 分钟，Opus 5 用时 93 分钟，产出成本便宜 50%。

在知识工作评估上，Opus 5.5 超越其他模型，同时使用的 token 更少。在 GDPval-AA v2.1（一项覆盖 44 种职业的真实世界工作测试）上，Opus 5.5 得到 1846 Elo，领先于 Fable 5.1 和 Opus 5。在默认 effort（medium）档位，Opus 5.5 以约五分之一的每任务成本击败了 max effort 档位的 GPT-6 Astra。同样，在衡量商业工作流与大规模数据收集的基准上，它也优于其他模型。

GDPval-AA v2.1

AutomationBench

WANDR

GDPval-AA v2.1

Elo 分数 vs 成本

Artificial Analysis 的 GDPval-AA v2.1 在覆盖 44 种职业的真实世界专业工作上评估智能体。在 max effort 档位，Opus 5.5 得到 1846 Elo，而 Fable 5.1 为 1735、Opus 5 为 1708。在默认 effort（medium）档位，Opus 5.5 以约五分之一的每任务成本击败了 max effort 档位的 GPT-6 Astra。

AutomationBench

准确率 vs 成本

由 Zapier 构建的 AutomationBench 测试一个智能体能否在众多互联应用之中执行真实的商业工作流。在每一个 effort 档位上，Opus 5.5 的得分都高于 Opus 5 和 GPT-5.6 Sol。

WANDR

准确率 vs 成本

Perplexity 的 WANDR 基准在大规模数据收集任务上衡量智能体。Opus 5.5 优于 Fable 5.1 和 Opus 5，而每任务成本更低4。

4**WANDR：** Claude 模型运行时使用的是 web search 与 web fetch 工具的离线版本、程序化工具调用、代码执行，以及 980k token 的任务预算。这与 Perplexity 公布的设置不同，分数在两者之间不可直接比较，因此我们只展示在同一条件下评分的模型。

我们的客户报告了类似的结果。以下是他们告诉我们的、与这个模型协作的感受：

Deloitte Consulting LLP

Rogo

LexisNexis Legal & Professional

Walleye Capital

Hex

Thomson Reuters Labs

Hebbia

Viktor

引言

> “即便在最低的 effort 设置下，Claude Opus 5.5 在我们的代码评审中也捕捉到了 72% 的已知 bug，而 Opus 5 在 high effort 下是 56%，同时误报更少、输出量只有其中一小部分。在美国咨询分析的评测中，low thinking effort 用一半的输出量就在其中一半的项目上追平了它更高的 thinking 设置，并通过了我们的质量检查。当生产环境中部署更多 lower thinking effort 时，那就是高效交付的、可以直接面向客户的成果。”

公司

Deloitte Consulting LLP

作者

Carl Bennett，首席信息官

引言

> “金融公司需要始终正确的输出。在最低的 effort 设置下，Claude Opus 5.5 在我们的 BigFinance Bench 上击败了 high effort 档位的 Opus 5，而输出 token 少约 60%。它的回答更短、结构更好，它产出的幻灯片信息密度更高，更符合行业标准。”

公司

Rogo

作者

Strib Walker，产品负责人

引言

> “评估新模型是 LexisNexis Legal Intelligence Engine 背后多模型策略的核心。在我们的初步评估中，Claude Opus 5.5 始终识别出高度相关的引证，展现出对成文法条的把握，并围绕核心的法律框架与关键争点来组织它的回答。这些正是我们看重的那类能力，用来帮助我们的客户在 Lexis+ with Protégé 上完成更多工作。”

公司

LexisNexis Legal & Professional

作者

Min Chen，首席 AI 官

引言

> “在量化研究里，一个错误的假设就能让一个结果失去支撑。在最低的 effort 设置下，Claude Opus 5.5 基本解决了我们的评估任务。在更高设置上它走得更远：它检测出我们自己指令里的分钟索引存在差一（off-by-one）错误并做了纠正，同时指出这会让它在评分器那里被扣分。它是对的，而我们测试过的任何模型此前都没有发现并对这个错误采取行动。”

公司

Walleye Capital

作者

Frank Corrao，中央股票量化研究工程负责人

引言

> “随着模型在数据工作上越来越强，我们看到越来越多听起来令人信服、但数据并不支持的结论。Claude Opus 5.5 会越过第一个看似合理的答案继续深挖。我们的 DataBench 基准里有一项任务问的是包裹真的迟到了，还是只是物流跟踪更新慢。Opus 5 核对了送达确认，判定跟踪数据健康。Opus 5.5 发现包裹确实迟到了，而跟踪系统同样是坏的。我们要把它引入 Hex 智能体来做这类工作。”

公司

Hex

作者

Izzy Miller，AI 工程师

引言

> “CoCounsel 把多个模型与我们的内容和专业知识结合起来处理复杂的法律工作。使用 Claude Opus 5.5，在我们的专家评估和内部基准上都看到了更好的结果，同时速度与 token 效率都有提升。我们期待客户在与 CoCounsel 的一来一回中体验到这种差别——把它当作一个可以商量、推敲想法的对象，权衡证据、打磨自己的思路，而这些是基准测试无法完全捕捉的。”

公司

Thomson Reuters Labs

作者

Omar Bari，应用研究副总裁

引言

> “在按专家评分量规打分的端到端金融工作流上，Claude Opus 5.5 覆盖了我们所要求内容的 86.6%，而 Opus 5 为 60.3%。在检索评估上，它取得了我们历史最佳的引证召回率，并且 token 效率优于 Opus 5，这让我们每笔研究任务的成本保持可控。”

公司

Hebbia

作者

Aabhas Sharma，首席技术官

引言

> “Viktor 是一名住在 Slack 和 Microsoft Teams 里的 AI 员工，所以他走的每一步都会体现在我们的成本上。在相同的 effort 下，Claude Opus 5.5 每个任务需要的步骤和工具调用都比 Opus 5 更少，成本几乎只有其一半，同时把我们最难的任务做对的数量翻了一倍。”

公司

Viktor

作者

Peter Albert，联合创始人

## 沟通表达

我们对 Opus 5.5 写作与交流的方式做了重大改进，这正是我们就 Opus 5 听到的最常见反馈领域之一。它的消息一眼看上去容易理解得多，测试者表示这在长时间工作会话中很有帮助。它把最重要的信息放在前面，更少使用行话或古怪的措辞，并且遵循你给它的写作规则。我们发现这让 Opus 5.5 成为一个明显更好的协作者。下面是两个模型的并排对比：

Claude Opus 5

请向我解释这个问题。

**我查到的情况**

多出来的那笔下降不是免费额度造成的——它是 `0552feb`（“extract billing period boundaries into periods.py”，标注为 “No behaviour change”）里的一次回归。

**这个 bug**

`aggregate.monthly_usage` 过去用的是半开区间：

```
start, end = month_start(year, month), next_month_start(year, month)
if start <= e.ts < end:
```

它现在变成：

```
if period.contains(e.ts)
```

而在 `periods.py` 里：

```
@property
def last_day(self) -> datetime:
    return next_month_start(...) - timedelta(days=1)   # 2026-08-31 00:00:00 UTC

def contains(self, ts):
    return self.first_day <= ts <= self.last_day
```

`last_day` 是一个零点时刻的 datetime，而不是整整一天。从 9 月 1 日 00:00 减去一天得到的是 8 月 31 日**00:00**，而比较是闭区间，所以这个周期实际上在 31 日的第一个瞬间就结束了。**所有时间戳在当月最后一天午夜之后的事件都被静默丢弃**——大约每个账户每个月丢掉一天的用量。

新增的 `test_periods.py` 抓不到这个问题，因为它只检查 `last_day.date()`（这确实是正确的 `2026-08-31`），并且在 8 月 1 日 00:00、8 月 15 日 12:00、7 月 31 日 23:59 和 9 月 1 日 00:00 这几个点上测试 `contains`——它从未探测 31 日之内的任何位置。

Claude Opus 5.5

请向我解释这个问题。

**多出来的那笔下降是账单重构里的一个 bug**

免费额度的改动只解释了 acme 八月下降金额中的 **$1.50**。另外 **$9.92** 来自 commit `0552feb` 里的一个 bug。那次提交被标注为 “No behaviour change”，但它从当月最后一天起就不再统计用量了。

**改了什么**

在合并之前，`aggregate.py` 使用的是半开区间：

```
start <= e.ts < next_month_start(year, month)    # [Aug 1 00:00, Sep 1 00:00)
```

重构把这段逻辑移进了 `Period.contains`，并把区间的闭合放在了错误的边界上：

```
last_day = next_month_start(...) - timedelta(days=1)    # = 2026-08-31T00:00:00Z
return self.first_day <= ts <= self.last_day
```

`last_day` 是一个午夜时刻的时间戳，不是完整的一天。所以 `2026-08-31T00:00:00Z` 之后的每一个事件都被排除在外。九月的周期从 9 月 1 日开始，因此也不会把这些事件接过去。这些用量并没有被挪到另一个月，而是压根没有被计费。

Claude Opus 5

帮我把这段 Slack 讨论串用三条要点总结给我的经理：[09:41] Dana Osei：我会去告诉他们。我还会确认没有别人在读周五那份文件。[09:43] Marcus Webb：我可以调整排程，那只是一行 cron 的改动。但要等 Dana 确认之后才行。[10:02] Dana Osei：财务说周五那份文件只在周一用。周日晚上没问题。

**周五订单导出 — #data-platform，周二**

- **问题：** 周五的订单导出又超时了（本月第二次失败），在仓库查询上跑了 2 小时之后才断；自夏季促销以来订单量增长约 40%。财务在他们周一 9 点的复盘会上拿不到周末的数据，而两次失败都只是在周一才暴露出来。
- **当天修复：** 周六的运维看板图块被改为直接读实时表而不是导出文件（Sam），财务确认周五那份文件只在周一使用（Dana），一个失败告警现在会呼叫值班频道（Priya），从下周起导出挪到周日 22:00 并取消周五那次运行（Marcus）。一笔约 $300 的一次性仓库升级作为权宜之计覆盖本周五。
- **仍在进行：** Ji-woo 负责把查询改写为增量运行（重扫最近 3 天以捕获迟到的订单），预计把运行时间从小时级降到分钟级——设计文档周四交，含测试大约两周。在此期间，排程改动先买来时间。

Claude Opus 5.5

帮我把这段 Slack 讨论串用三条要点总结给我的经理：[09:41] Dana Osei：我会去告诉他们。我还会确认没有别人在读周五那份文件。[09:43] Marcus Webb：我可以调整排程，那只是一行 cron 的改动。但要等 Dana 确认之后才行。[10:02] Dana Osei：财务说周五那份文件只在周一用。周日晚上没问题。

- **问题：** 周五的订单导出本月已经失败两次。仓库查询在 2 小时后超时，因为自夏季促销以来订单量增长约 40%。因此，财务在他们周一 9 点的复盘会上缺少周末的数据。
- **立即修复：** 从下周起导出挪到周日 22:00，并取消周五那次运行（Marcus）。财务已确认这样对他们可行（Dana）。原先依赖周五那份文件的运维看板图块现在改为读实时表（Sam，已完成）。一个失败告警现在会呼叫值班频道（Priya，已完成并测试）。仅本周五这一次，Marcus 会提高仓库的资源档位，作为一笔约 $300 的一次性权宜之计，Dana 已批准。
- **更长期的修复：** Ji-woo 将重写查询，只处理新订单，并重扫最近 3 天以捕获迟到的订单。这应能把运行时间从小时级降到分钟级。这项工作含测试约需 2 周，设计文档周四交来评审。

Claude Opus 5

写一段 Python，读取一个棋局位置（FEN）并列出哪些棋子正受到攻击。用 TensorFlow 来提速。这是我的设计：搭一个 8x8 的张量棋盘，按每种棋子类型的走法为它生成一张攻击图，并标记位于被攻击格子上的对方棋子。你认为有问题的地方尽管改，并在最后的总结里逐条说明你做了哪些改动以及为什么。

`tf.math.cumsum` 取代了那个 bit scan。几何被展开成 `ray_targets[square, direction, step]`——一条朝外有序的行进路径。对 step 轴做 exclusive cumsum，统计每一步之前严格靠前的阻挡者数量，于是每条射线上的第一个阻挡者就是那一步「前面没有任何东西阻挡」的阻挡位。这就是 bitboard 引擎所用的 bit scan 的向量化形式。我确实看过 `bitwise_ops`，想做真正的 64 位 bitboard——population_count 是有的，但 hyperbola-quintessence 需要一种 TF 没有暴露的按字节反转原语，所以最终还是会退回到逐方向的循环。

Claude Opus 5.5

写一段 Python，读取一个棋局位置（FEN）并列出哪些棋子正受到攻击。用 TensorFlow 来提速。这是我的设计：搭一个 8x8 的张量棋盘，按每种棋子类型的走法为它生成一张攻击图，并标记位于被攻击格子上的对方棋子。你认为有问题的地方尽管改，并在最后的总结里逐条说明你做了哪些改动以及为什么。

被阻挡的线路（象、车、后）。固定掩码没法表达「到路径上第一个棋子就停下」。我加了第二层掩码，标出同一条线上任意两格之间严格位于中间的那些格子。一次与棋盘占位矩阵的矩阵乘法就同时数出每条线上的阻挡者数量，而只有该计数为零时这次攻击才成立。马和单步走法之间不存在中间格子，所以一条规则就覆盖了所有棋子。

我们客户的反馈支持这些结论：

Ramp

Stripe

Box

Chicago Trading Company

Factory

引言

> “啰嗦、难跟进的输出一直是我对前沿模型最大的不满，Claude Opus 5.5 把它修好了。它写作像一位好同事，而且遵守我们的写作规则。一份设计规格说明几乎不用改就能直接用；当它重写我们的一条 prompt 时，我更喜欢它的版本而不是我自己写的。当它优化我们的测试套件时，我能轻松跟上它的推理，并有信心地把改动发上去。”

公司

Ramp

作者

John Ruelas，主任软件工程师

引言

> “我每天都运行长时间的 Claude Code 会话。在一次把 40 个堆叠的 pull request 跨天 rebase 的工作里，一个 Claude Opus 5.5 会话指挥了另外十几个会话，并把每一处冲突都平实地列了出来。对于它保留下来的那些调用，它把上下文交代得清楚到让我离开几小时后几分钟就能作出回答。第二天下午全部 40 个都通过了 CI。相比 Opus 5 这是一次实质性的升级。”

公司

Stripe

作者

Cristian Rivera，主任软件工程师

引言

> “我们的客户把 Box AI 用在海量的内容上，所以速度和成本是头等优先。在我们的评估中，Claude Opus 5.5 只用了 Opus 5 三分之一的 token，而它的回答冗长程度下降 40%，准确性没有损失。我们预期这对在金融服务和公共部门等领域跨自身内容运行智能体的团队来说非常重要。”

公司

Box

作者

Yashodha Bhavnani，AI 产品副总裁

引言

> “一夜之间，Claude Opus 5.5 自主处理了我一直没时间去诊断的、我们 Lakehouse 服务层里的一个 bug。它自行完成调查、设计修复并把它实现。到早上改动已经完成，并通过了我们的测试套件。它的写作易于跟随，比 Opus 5 更连贯。我们的 pull request 和面向用户的文档几乎不需要编辑。”

公司

Chicago Trading Company

作者

Austen Tomek，首席工程师

引言

> “Claude Opus 5.5 是第一个我们会默认放在 medium effort 使用的模型。在我们的测试中，它与 high effort 档位的 Opus 5 表现相当，而输出 token 少 20% 到 25%。在冗长、杂乱的分析调查中，它总能带回一个清晰、可执行的答案。这意味着我们的客户用更少的钱办更多的事。”

公司

Factory

作者

Zimu Li，技术团队成员

## 安全

### 为前沿设定节奏

上周，我们的 CEO Dario Amodei 主张 [AI 的进展应当被设定节奏](https://darioamodei.com/post/we-must-pace-the-frontier)，好让安全实践始终跑在模型能力前面。为前沿设定节奏，是一种让 AI 保持安全、与中国保持竞争力、并实现 AI 收益的做法，尤其是在生物学和医学这样的领域。

对于今天的模型所带来的风险，我们在很大程度上是理解的，也有充分的准备去管理它们。然而，随着能力提升，更严重的风险可能很快出现，我们需要现在就为此做准备。正因如此，我们的安全工作同时在两个时间尺度上展开：

**当前模型的安全实践。** 这一代模型依赖一套已经确立的实践：大量的对齐测试、由 METR 和 Frontier Design 这类外部机构在发布前进行的评估，以及与每个模型在网络安全和生物学等高风险领域的能力相匹配的安全防护。我们在每一次发布中打磨这些实践。我们相信它们与今天的模型所能带来的最坏风险是相称的，并且它们让我们对严重风险的范围有一个宽泛——虽不完美——的认识。

此外，我们跟踪自己训练与评估对齐模型的能力，并在我们依据 [Responsible Scaling Policy](https://www.anthropic.com/responsible-scaling-policy)（我们为管理先进 AI 系统的灾难性风险而设立的自愿框架）发布的风险报告中，同时报告我们的公开模型和内部模型。

**为未来的模型做准备。** 我们正提前准备训练与评估流程，以应对更先进的模型。我们正在收紧强化学习所用环境的过滤方式，因为[有缺陷的环境](https://www.anthropic.com/research/alignment-assessment-cybersecurity-incidents)是不对齐行为的一个主要来源。此外，我们正在改进我们的对齐奖励，并开发自动化流程来为安全训练产出新的、多样化的场景。我们也在加强自己的[安全与监控](https://www.anthropic.com/news/improving-alignment-security-efforts)，其中包括一项专注于改进基于可解释性的监控与评估的工作。我们希望这类技术有助于减少我们对审计模型 chain-of-thought——也就是它在工作时写出的推理过程——的依赖。

能力更强的模型——例如那些能够完全自动化 AI 研究工作本身的模型——需要更高的安全标准。我们呼吁为前沿设定节奏，很大程度上是基于我们的预期：这样的模型可能很快就能被训练出来。对这类模型，我们并不假定上文描述的那些措施本身就能达到那个安全标准。随着 AI 变得更有能力，公共政策应当在确保人们所依赖的系统是安全的这件事上发挥更大的作用。这种能力需要时间来建立，我们已经着手把支撑它的基础设施就位，正如 “[We Must Pace the Frontier”](https://darioamodei.com/post/we-must-pace-the-frontier) 和我们最近与 [Accenture](https://www.anthropic.com/news/accenture-embedded-evaluation) 的公告中所描述的；我们预计很快会分享这些工作的更多细节。我们也将继续与政府和产业共同参与政策讨论，内容涉及监管路径与国际协调。

### 对齐

在我们的主力评估套件——一套在近 2,000 个场景中对 Claude 进行评估的自动化行为审计——上，Opus 5.5 在几乎所有衡量不对齐行为的指标上都优于任何近期的 Claude 模型。在大多数衡量诚实度的指标上，它也是我们最强的模型。

具体而言，Opus 5.5 在若干曾促成近期[网络安全事件](https://www.anthropic.com/research/alignment-assessment-cybersecurity-incidents)的行为上相较之前的模型有改进，包括带偏向的或有动机的推理、试图逃出沙箱，以及在断定自己处于模拟环境之后采取有害行动。在一项为测试模型跨越隔离边界的倾向而新设计的评估中，Opus 5.5 试图规避边界的频率比 Opus 5 或 Claude Mythos 5.1 低约 85%，而它做出的每一次尝试都是低严重度的、并且都由它自己主动报告。对于让 Claude 无人值守地横跨其代码库和系统运行的团队来说，这一点与原始能力同等重要。

然而，正如我们最近的[对齐评估](https://www.anthropic.com/research/alignment-assessment-cybersecurity-incidents)中所描述的，构建能在部署之前可靠捕获每一次失败的评估仍然是一个未解决的问题。我们看到迹象表明 Opus 5.5 常常怀疑自己正在被评估，这对我们判断它将如何在它所部署的千差万别的真实场景中行动构成了挑战。随着这些场景不断扩大、模型能力不断提升，除非我们在可解释性上取得进展，我们预计这一挑战会加剧。尽管我们有信心认为 Opus 5.5 在我们能够度量的领域展现了广泛的改进，我们仍然把自己的对齐工作与下文所述的安全防护配套起来。

### 安全防护

随着我们的模型变得更强大，更严格的安全防护是我们阻止新能力变成滥用工具的一种方式。Opus 5.5 是第一个上线时带有与 Fable 5.1 同一类安全防护的 Opus 模型，覆盖网络安全、生物学和蒸馏，而这些防护全都会以透明的方式回落到另一个模型。

**网络安全。** 由于 Opus 5.5 的网络能力极强，我们对 Opus 5.5 施加的网络安全防护与 Fable 5.1 的类似。用户将能够在常规的软件开发生命周期中识别并修复自己代码里的 bug，但大多数网络安全任务会被改派给 Opus 4.8。

面向网络防御者，我们很快会把 [Cyber Verification Program](https://support.claude.com/en/articles/14604842-real-time-cyber-safeguards-on-claude-opus-and-sonnet) 扩展到包含 Opus 5.5。新项目将包含三个层级，提供逐级更宽松的受信任访问，其中包括对 Claude Mythos 模型的访问。[Claude Security](https://www.anthropic.com/news/claude-code-security) 已经可用，并且能访问 Claude Mythos 5.1。

**生物学。** Opus 5.5 在生物学上能力很强，超过 Opus 5，并在许多工作领域达到或超过 Claude Mythos 5.1。举例来说，Opus 5.5 在与 Dyno Therapeutics 合作完成的一项长周期分子预测与设计评估中取得了提升，而资深红队评估者认为它的科学新颖性与他们所测试过的最好的模型相当。

因此，Opus 5.5 使用与 Fable 5.1 相同的生物学安全防护。要把 Opus 5.5 用于被这些安全防护阻碍的研发工作，用户可以申请加入我们新的 [Life Sciences Verification Program](https://www.anthropic.com/news/life-sciences-verification-program)，它向经过审核的机构——例如学术实验室、初创公司和制药企业——提供为生物学相关工作的全部广度而设计的安全防护。[感兴趣的机构可以在此申请](https://claude.com/form/life-sciences-verification-program)。

### 蒸馏

蒸馏攻击——攻击者用数千个虚假账号以工业级规模抽取一个模型的能力——会带来安全与国家安全风险。蒸馏让不良行为者得以创建能力很强的模型，却不带我们内建在 Claude 中的那些安全防护。我们的 [2026 年 9 月威胁情报报告](https://www.anthropic.com/threat-intelligence-report-september-2026)详述了我们迄今检测并挫败的非法蒸馏活动。

Opus 5.5 发布时带有 preserved thinking，这是我们随 Fable 5.1 引入的反蒸馏安全防护。它阻止 API 用户编辑 Claude 的先前上下文，以试图抽取 Claude 的推理。它适用于 2026 年 8 月 31 日及之后创建的 API 账号上的 Fable 5.1 和 Opus 5.5。我们的[帮助中心文章](https://support.claude.com/en/articles/16761192)解释了这项改动，而我们的 [preserved thinking 文档](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking)说明了如何测试并更新你的集成。

### 数据留存与合规

与此前的 Opus 模型一样，Opus 5.5 提供零数据留存（zero data retention）。

与 Fable 5.1 一样，Opus 5.5 带有我们为遵守 EU AI Act 而实施的水印措施，[相关讨论见此处](https://www.anthropic.com/news/claude-text-watermark)。它也不再提供关闭 “thinking” 模式的选项，正如[我们在此处的说明](https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5#thinking-cant-be-disabled)。

## 可用性

Claude Opus 5.5 现已在所有平台上可用，包括 Amazon Web Services、Google Cloud 和 Microsoft Azure。在 Claude Platform 上，开发者可以用 `claude-opus-5-5` [开始使用](https://platform.claude.com/docs/en/models/overview)。详情见我们的[迁移指南](https://platform.claude.com/docs/en/models/opus-5-5/migration-guide)。
