---
vendor: anthropic
title: 推出 Claude Haiku 5.5
original_title: Introducing Claude Haiku 5.5
url: https://www.anthropic.com/claude-haiku-5-5
date: 2026-10-06
lang: zh
captured: 2026-10-11
extractor: readability-v1
translator: agent
status: translated
body_sha: d541fbaf6ac8
---

October 7, 2026

# Claude Haiku 5.5

推出 Claude Haiku 5.5：这是我们迄今发布的最小尺寸模型里最便宜、最快、能力最强的一款。

Claude Haiku 5.5 为大批量、成本敏感的任务而设计。它能可靠地处理快速且重复的工作负载（比如摘要、压缩、数据库查询和分类请求）。在编码工作中，它作为 subagent 与 Opus 5.5、Sonnet 5.5 搭配使用很合适。而且，由于它也是我们迄今最快的模型，对于实时客服、浏览器操作这类对速度敏感的任务尤其好用。¹

Haiku 5.5 的定价比 Haiku 4.5 低得多。平均下来，运行成本现在大约便宜 75%。²

伴随这次发布，我们也在提升整个模型档位的性价比。我们把 Claude Sonnet 5.5 的缓存读取价格下调一半，这意味着 Sonnet 5.5 在大多数 agentic 任务上现在大约便宜 20%。同时，我们为 Claude Max 和 Team 订阅用户推出一项新的每月 API 额度，用来支持用户构建运行在 Claude Platform 上的新 agent 与应用。

## 性能

以下是 Claude Haiku 5.5 在一系列 benchmark 上的表现：

|  | Haiku 5.5 | Haiku 4.5 | GPT-6 Luna |  | Sonnet 5.5供参考 |
| --- | --- | --- | --- | --- | --- |
| 知识工作GDPval-AA v2.1 |  |  |  |  |  |
| 知识工作GDPval-AA v2.1 | 1620 | 735 | 1437 |  | 1840 |
| 知识工作AA-Briefcase v1.1 |  |  |  |  |  |
| 知识工作AA-Briefcase v1.1 | 1578 | 614 | 1336 |  | 1824 |
| 计算机操作OSWorld 2.1 |  |  |  |  |  |
| 计算机操作OSWorld 2.1 | 72.4%离线子集 | 15.7%离线子集 | 48.9%离线子集 |  | 83.9%离线子集 |
| 多学科推理Humanity’s Last Exam |  |  |  |  |  |
| 多学科推理Humanity’s Last Exam | 45.9%无工具 | 10.2%无工具 | — |  | 56.9%无工具 |
| 57.4%有工具 | 18.7%有工具 | — |  | 64.5%有工具 |  |
| Agentic 编码Terminal-Bench 4.0 |  |  |  |  |  |
| Agentic 编码Terminal-Bench 4.0 | 39.2% | 0.0% | 16.4% |  | 70.6% |
| Agentic 编码FrontierCode 1.1 (Main) |  |  |  |  |  |
| Agentic 编码FrontierCode 1.1 (Main) | 46.4% | — | 42.4% |  | 52.1%Xhigh |
| 视觉推理Chartography |  |  |  |  |  |
| 视觉推理Chartography | 46.4%无工具 | 6.4%无工具 | 29.1%无工具 |  | 61.6%无工具 |

关于我们如何运行评测，参见 [Haiku 5.5 System Card](https://www.anthropic.com/claude-haiku-5-5-system-card)。

Haiku 5.5 是我们第一个带可调 effort 档位的 Haiku 级模型。也就是说，和其他模型一样，用户可以自己决定是偏向成本还是偏向智能。下面几张图展示 Haiku 5.5 在每个 effort 档位上三项 benchmark 的表现：

计算机操作：OSWorld知识工作：GDPval-AA多学科推理：Humanity’s Last Exam

OSWorld 2.1（离线子集）准确率 vs. 成本

OSWorld 2.1 衡量 agent 在真实计算机上完成冗长、多步骤任务的能力。

GDPval-AA v2.1准确率 vs. 成本

Artificial Analysis 的 GDPval-AA v2.1 在 44 种真实职业的专业工作上评测 agent。

Humanity’s Last Exam（无工具）准确率 vs. 成本

Humanity’s Last Exam（HLE）考察专家级的学术知识与推理能力。

在早期测试中，我们的客户反馈的结果与上面展示的性能和成本提升一致。以下是他们对我们说起的新模型评价：

AsanaHubSpotAlphaSenseBoxRogoCognition

Quote

> “我们对 Claude Haiku 5.5 印象非常深刻，尤其是它的速度。我们把它跑了一遍 AI Teammates（我们的 AI agent 产品）的评测套件，覆盖分诊 bug、搭建项目，以及检索大型项目组合以找出高风险或逾期工作这类用例。与我们现在用的模型相比，任务完成的延迟降低了 30% 以上，每个 agent turn 的推理快达 2.5 倍。体验上明显更利落。”

公司Asana

作者Aaron Vinh, Staff Software Engineer

Quote

> “在 HubSpot，我们用模拟门户来评测新模型在 CRM 任务上的表现，比如对 deals 做报表。我们主要测试更小、更高效的模型，而 Claude Haiku 5.5 拿到了我们在这套套件上见过的最高分，三次运行平均 92.8%。其中一项 CRM 审计任务要求模型识别出陈旧但表述含糊的记录。在我们测过的所有模型里，Haiku 5.5 完成任务最快，命中率最高，误报率最低。”

公司HubSpot

作者Ze’ev Klapow, Distinguished Software Engineer

Quote

> “Ask in Document 是我们的主要开销来源之一，生产环境每周大约 800 万次调用。它在一篇或几篇文档之上回答非常具体的问题。我们跑了 400 条查询，Claude Haiku 5.5 相对 Haiku 4.5 是统计显著的改进：0.84 对 0.76。”

公司AlphaSense

作者Daniel Campos, Distinguished Engineer

Quote

> “我们的客户在海量企业内容上使用 Box AI。使用面广，就意味着要管理效率和成本，要找到最适合当前任务的模型。早期测试中，Claude Haiku 5.5 的得分比 Haiku 4.5 高 11 分，延迟只有大约一半。我们会把它用在规模化运行的分析型工作上，从成本报表到财务摘要，再到每周例行复盘。”

公司Box

作者Yashodha Bhavnani, VP of AI Products

Quote

> “短小、大批量的工作正是 Claude Haiku 5.5 适合我们的位置，比如快速查检、subagent 和摘要。当一个大模型在做 deck 时，一个 Haiku 5.5 的 subagent 会钻进 10-K 里，把 deck 需要的那行分部营收取出来。它的准确度让我们敢在这个位置信任它，而它足够快、足够便宜，我们可以大量地跑。”

公司Rogo

作者Alex Wang, Applied AI

Quote

> “Claude Haiku 5.5 加入 Devin Fusion 的 sidekick 阵容，是一个很出色的选择。用 Haiku 5.5 做 sidekick 时，Fusion 保持了一流的 FrontierCode 得分 66.2，同时压低了成本和延迟。你现在就可以在 Devin CLI 里试，搭配 Opus 5.5 作为 lead。”

公司Cognition

作者Walden Yan, Co-Founder & CPO

## 定价

下表展示 Claude Haiku 5.5 的定价与我们其他模型的对比。当任务的 prompt 在 100,000 tokens 以内时，Haiku 5.5 尤其划算——这类请求占我们上一代 Haiku 模型大约 90%。

| 每 100 万 tokens 价格 | **Haiku 5.5** prompt 100k 以内 / 以上 | **Haiku 4.5** | **Sonnet 5.5** |
| --- | --- | --- | --- |
| 缓存读取 | $0.01 / $0.05 | $0.10 | $0.10 |
| 缓存写入 | $0.125 / $0.625 | $1.25 | $2.50 |
| 输入 tokens | $0.10 / $0.50 | $1.00 | $2.00 |
| 输出 tokens | $0.50 / $2.50 | $5.00 | $10.00 |

## 安全性

**对齐。** 相对 Haiku 4.5，Claude Haiku 5.5 在我们几乎全部对齐评测上都有明显改进。具体而言，我们发现的失准行为实例少得多，配合滥用的意愿也更低。该模型的 [system card](https://www.anthropic.com/claude-haiku-5-5-system-card) 更详细地说明了我们的评测过程与结果。

**防护栏。** 与其能力相称，Haiku 5.5 的网络安全防护栏比 Haiku 4.5 更严格，但比我们施加给其他近期模型的略宽松一些。在网络安全方面，它允许的防御性任务范围比 Sonnet 5.5 的防护栏更宽，但仍然会拦截渗透测试及其他更可能被攻击者使用的技术。

Haiku 5.5 的生物学防护栏与 Sonnet 5、Sonnet 5.5、Opus 5 相同：允许研究性的生物学问题，但会限制我们判断为可能造成伤害的请求。从事范围更广的生物学与网络安全活动的机构，可以申请加入我们的 [Life Sciences Verification Program](https://www.anthropic.com/news/life-sciences-verification-program) 和 [Cyber Verification Program](https://www.anthropic.com/news/cyber-verification-program)。

## 可用性

Claude Haiku 5.5 现已在所有平台上线，包括 Amazon Web Services、Google Cloud 和 Microsoft Azure。在 Claude Platform 上，开发者可以用 `claude-haiku-5-5` 开始使用。

详情见我们的[迁移指南](https://platform.claude.com/docs/en/models/haiku-5-5/migration-guide)。

## 其他更新

随着 Claude Haiku 5.5 的新定价，我们还在进一步改进模型与产品的性价比。

第一，从今天起，我们**下调 Claude Sonnet 5.5 的缓存读取价格**。缓存读取现在便宜 50%：每百万 tokens $0.10，而非 $0.20。由于缓存读取在模型的 token 消耗中占比很大，这把 Sonnet 5.5 在多数 agentic 任务上的成本降低了约 20%。

举例来说，下面是这次降价对 Sonnet 5.5 在 Terminal-Bench 4.0 上「性能相对成本」的影响：

Terminal-Bench 4.0准确率 vs. 成本

Terminal-Bench 4.0 衡量模型在命令行界面中完成复杂、多步骤专业任务的能力。

这张图说明了 Haiku 5.5 与我们更大模型之间的一个重要差别。对于 Terminal-Bench 4.0 所衡量的那类复杂 agentic 编码任务，Sonnet 5.5 和 Opus 5.5 仍是更好的选择。相比之下，Haiku 5.5 最适合范围更窄的任务——那些在旧版 Claude 上会因成本过高而做不起的活儿，比如压缩、摘要，或 subagent 工作。

第二，本周我们会向**所有 Max 和 Team 订阅用户发放一项新的每月 API 额度，可用于 Claude Platform**。Max 5x 用户每月获得 $100 额度，Max 20x 用户获得 $200，Team 订阅用户最多可获得 $500，在其成员之间共享。这些额度的设计目的，是让我们的用户能够试用自己的点子，构建调用我们 API 的工具、应用与 agent。它们可以用在我们的任何模型上。更多信息[见我们的 Help Center 文章](https://support.claude.com/en/articles/17154008)。

对于开发者，我们还在**更新 Claude 的 Python 和 TypeScript SDK，加入 beta 阶段的 computer use 与 browser use 支持**。鉴于 Haiku 5.5 在速度、能力与价格上的组合，它特别适合这类任务。你可以[在我们的 Claude Platform 文档](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-sdk)中了解更多。

## 脚注

1 Claude Haiku 5.5 是我们迄今最快的模型（按各模型的标准速度比较），不过在 Fast Mode 下它不如 Opus 系列模型快。

2 Claude Haiku 5.5 相对 Claude Haiku 4.5，在 100,000 tokens 以内的请求上定价低 90%，在超过 100,000 tokens 的请求上低 50%。在 Haiku 4.5 上，90% 的请求属于前者。这项计算还考虑了 Haiku 4.5 与 Haiku 5.5 在完成同一件工作时所用 token 数的变化：Haiku 5.5 使用了更新过的 tokenizer（与 Sonnet 5.5、Opus 5.5 相同），这意味着它每项任务用的 tokens 略多。
