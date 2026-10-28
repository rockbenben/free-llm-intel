---
vendor: anthropic
title: 正式推出 Claude for Financial Advisors
original_title: 
url: https://claude.com/resources/articles/claude-for-financial-advisors
date: 2026-10-27
lang: zh
captured: 2026-10-28
extractor: readability-v1
translator: agent
status: translated
body_sha: b7091be33738
---

# 正式推出 Claude for Financial Advisors

今天，我们发布 Claude for Financial Advisors，这是一套连接器与工作流技能，旨在协助完成研究、准备和文档类任务——这些任务占用了顾问的时间，使他们无法投入到面向客户的工作中。

金融顾问的时间非常稀缺。根据 [Kitces 的研究](https://www.kitces.com/kitces-report-how-financial-planners-actually-do-financial-planning/)，一家典型的顾问机构只有六分之一的时间用于客户会议。其余时间都花在会议之外的工作上：在多个系统之间拼凑信息，为会议做准备、做规划，并

记录讨论过的内容。与此同时，根据 [EBRI 的 2026 年退休信心调查](https://www.ebri.org/docs/default-source/rcs/2026-rcs/rcs_26-fs-3_prep.pdf)，超过四成的美国劳动者表示，他们不知道该向谁寻求优质的财务或退休规划建议。顾问在准备和文书工作上节省下来的时间，可以投入到现有客户，或他们目前尚无余力服务的新家庭上。

Claude for Financial Advisors 包含：

- **Connectors**，让 Claude 能够访问顾问最常依赖的托管机构、资产管理公司和财富科技提供商，使顾问可以在一处处理客户信息。
- **Skills**，利用这些信息协助完成具体任务，例如会议准备、投资组合分析和合规检查，始终服务于顾问自己的判断与风格。

## 连接顾问已经在使用的工具

新的连接器接入了顾问所依赖的 CRM、托管机构、投资组合报告、财务规划软件、遗产规划工具和会议记录能力。

- **Addepar** 将投资智能带入 Claude，让顾问以受治理的方式访问公开与私募市场中的投资组合数据、分析和流程。
- **BlackRock** 通过 Advisor Center 将其投资组合构建专长、模型投资组合和机构级分析带入 Claude，使顾问能够在公开与私募市场中提供整体建议。
- **CAIS** 向 Claude 中的顾问开放其另类投资平台，使他们可以查询基金数据、审查管理人与基金业绩，并把客户的公开与私募持仓放在一起查看。
- **Charles Schwab** 将 Claude 连接到 Schwab Advisor Services 的托管数据，包括余额、持仓、交易、成本基础、提醒和资金划转状态，使顾问可以查看客户信息、识别哪些客户需要关注，并为客户回顾做好准备。
- **Conquest Planning** 将其 Strategic Advice Manager 规划引擎带入 Claude，使顾问可以在一处创建新的客户计划、审查并应用策略、更新现有计划，并为客户会议做准备。
- **Envestnet** 让顾问用自然语言汇总 Tamarac 的账户与家庭，并附带来自 MoneyGuide 的财务计划快照。
- **FactSet** 将多资产类别内容带入 Claude，包括基金与 ETF、新闻、公司基本面、分析师预期和市场数据，使顾问可以研究客户投资组合中的公司和证券。
- **FINNY**，这个增长与拓客平台，将 Claude 连接到顾问按渠道和触达序列步骤划分的营销活动结果，并让顾问可以从其 CRM 中丰富潜在客户名单，或直接在 Claude 中上传新名单。
- **Flourish** 将 Claude 连接到金融顾问的业务簿，使他们能够在 Claude 内处理客户信息、查询费率、管理邀请，并为客户会议做准备。
- **Franklin Templeton** 在 Claude 中提供经公开批准的基金与份额类别信息，包括业绩、费率、NAV、持仓、分红和基金文件，以及其已发布的市场与投资洞察。
- **iCapital** 将客户的另类投资持仓带入 Claude，使顾问可以查看 NAV、承诺出资、未出资资本、近期资本活动和业绩，并更容易地将这些洞察与客户更广泛的投资组合联系起来。
- **Invesco** 通过其 Invesco for Advisors 连接器，将投资组合智能与实践管理洞察带入 Claude。
- **J.P. Morgan Asset Management (55ip)** 将税务过渡技术扩展到 Claude，使顾问可以评估把客户持仓转入新投资组合的税务影响。
- **Jump**，一个面向金融专业人士的 AI 平台，为 Claude 提供客户上下文（会议、文档、任务）以及由 Jump 构建的技能，为顾问准备待审阅的后续步骤。
- **MSCI** 将其专有数据与分析带入 Claude，使财富管理机构可以评估公开与私募市场中的投资选项、监控业绩，并评估再平衡机会。
- **Nevis**，这个面向财富管理的 AI 平台，利用来自会议、文档和沟通中的客户信息，在 Claude 中支持会议准备与跟进。
- **Orion** 将投资组合报告和 Redtail CRM 洞察带入 Claude，用于家庭回顾、机会分析、会议准备和跟进。
- **SS&C Black Diamond** 将投资组合、业绩、持仓和再平衡数据带入 Claude，使顾问可以审阅自己的业务簿、找出偏离容忍区间的客户、发现税损收割机会，并在获得批准后生成客户报告、任务和再平衡会话。
- **Wealthbox** 将 Claude 连接到客户记录和会议历史，以支撑客户入驻、会议准备和跟进。
- **Wealth.com** 为 Claude 提供每位客户遗产与税务状况的结构化视图，包括信托和遗嘱摘要、纳税申报洞察以及完整资产负债表，使顾问可以基于对现有信息的有序汇总开始规划，而不必依赖散落在多个系统中的文档。
- **Vanguard** 将其模型投资组合和顾问投资解决方案的信息带入 Claude，使顾问在为客户做决策时能够借助 Vanguard 值得信赖的研究、投资组合构建和资产配置专长。
- **Zocks**，这个面向金融顾问的 AI 会议助手，将它在每次对话中捕捉到的客户情报带给 Claude，包括画像、目标、生活事件和承诺事项。

这些连接器加入了 Claude 中已有的其他[连接器](https://claude.com/connectors)，包括 Microsoft 365、Salesforce、DocuSign、Box、S&P Global、Morningstar 等。

Claude for Financial Advisors 插件把顾问技能和连接器打包成一次安装，可与 BlackRock、Charles Schwab、Addepar、Envestnet、iCapital、Orion、Wealthbox、Wealth.com 和 Zocks 配合使用，顾问可在引导式设置过程中选择要连接其中的哪些。部分合作伙伴也提供自己的插件：BlackRock 正在为 Advisor Center 推出一款插件，加入 S&P Global 和 LSEG 已有插件的行列。

## 围绕顾问一天工作构建的技能

Claude for Financial Advisors 插件中的每项技能都对应顾问一天中的某个具体时刻，从为客户会议做准备到解释一个发生漂移的投资组合，并会路由到公司已经用于经营业务的工具。公司可以按原样采用我们的 Claude for financial advisors [技能仓库](https://github.com/anthropics/claude-for-financial-advisors)中的这些技能，也可以根据自身的工作流、服务模式和机构风格加以调整。

- **Advisor onboarding** 连接公司的工具，并自动执行第一次会议准备，帮助新顾问在第一天而不是第三周就能产出成果。
- **Alternative investments brief** 从 iCapital 或 Addepar 提取某个家庭的另类投资，汇总成可直接用于会议的摘要，与投资组合的其余部分并列展示，而无需顾问手工核对彼此独立的对账单。
- **Compliance and AI policy** 根据用户配置的标准，标出可能需要额外合规审查的内容，协助公司记录审查流程，并支持 AI 治理文档流程。
- **Estate and tax brief** 将客户的遗产计划与实际账户户名和受益人进行核对，回顾上一年的税务情况，并可创建 CRM 跟进任务，使不一致之处浮现出来供顾问审查。
- **Portfolio rebalance review** 对照客户的目标配置，标记漂移和集中持仓，并生成一份首版说明——否则这份说明要由顾问从零撰写。
- **Post-meeting notes and follow-up** 一次就把转录内容转成客户摘要、回顾邮件和 CRM 任务，而不用顾问在通话后逐项手工完成。
- **Pre-meeting prep** 把来自已连接系统的信息（包括客户持仓、近期账户活动和以往会议的未结事项）整合成一份简报供顾问审阅，使他们能够做好准备、走进会议时就能围绕该客户的具体情况展开对话，而不必从三个系统里重建上下文。
- **Prospect intake** 将潜在客户分享的信息整理成摘要、分析师交接材料和一份「可以期待什么」的备忘录，让第一次会议在基本信息已经就位的情况下开始。

这些技能合在一起，在顾问的一天中收集信息、加以汇总，并起草客户沟通内容。投资建议、客户沟通、合规判定及其他受监管活动仍需经过人工审查与批准。

## 为受监管专业人士打造

Claude for Financial Advisors 的设计让顾问始终处于掌控之中，关键任务需要批准。Claude 为顾问准备简报、摘要和分析草稿，并把 CRM 更新或客户沟通草稿这类行政操作准备好，交由顾问审查和批准。合规技能会对照 SEC Marketing Rule 筛查面向客户的语言，以标记潜在问题，帮助公司在现有治理与记录保存流程内记录审查活动，并包含一套自助式 AI 政策工作流，帮助公司按照 SEC 规则记录其对 AI 的使用。工作流活动可以被记录，以协助公司维持适当的记录与监督流程。

## 服务更多家庭

当 Claude 处理会议准备、跟进草稿和销售管道回顾这类行政任务时，顾问可以把更多时间用于服务客户。顾问机构可以扩大客户基础，并提供更多客户需要的服务，如税务、遗产、保险和退休规划。

以下是客户和生态合作伙伴对与 Claude 合作的看法：

![zocks](https://assets.claude.com/05a6a0c1132f543d0537102984022c0c90774dde.png)

> “优质的财务建议取决于了解客户生活中正在发生什么，而不只是他们账户里有什么，”Zocks 首席执行官兼联合创始人 Mark Gilbert 表示。“Claude 与 Zocks 之间扩展的合作，把过去分散在多个来源和系统中的数据与个人客户上下文汇集在一起。如今，通过 Claude 完成的每一项任务和分析，都建立在更完整的客户理解之上。这也让企业机构拥有更大的灵活性，围绕其顾问实际的工作方式来构建 AI 工作流。”

Mark Gilbert，首席执行官兼联合创始人

![RFG Advisory](https://assets.claude.com/b85fd6f58a1f1a493b2cc9de09044b6b2164466e.png)

> “MCP 正在从根本上改变我们为顾问构建技术的方式。随着 Claude 和 Zocks 直接集成进我们的技术栈，过去需要数月配置并依赖外部合作伙伴的问题，正越来越多地能由我们自己的开发团队解决。这让我们可以自由地更快行动、与一流的合作伙伴协作，并围绕顾问实际运作的方式去构建。与其要求顾问适应技术，我们可以让技术去适应他们。”

Dr. Jordan Hutchison，技术与运营副总裁

![Wealthbox](https://assets.claude.com/31be98f5c18121a5063482dbcb91cd4bb812e9c7.svg)

> “顾问们多年来在 Wealthbox 中积累了深厚的客户上下文。这让他们可以把这些上下文直接带入 Claude，并让前沿模型据此工作，例如准备会议、处理跟进、起草沟通内容，同时一切都保持与他们业务所依赖的 CRM 相连。”

John Rourke，首席执行官兼联合创始人

![BlackRock](https://assets.claude.com/d72d42304889c5ecd4f2ba410dfde53b13255b97.svg)

> “顾问们正在应对日益复杂的客户需求，同时面对市场与技术加速变化的节奏。我们与 Anthropic 的合作是我们更广泛努力中的重要一步，旨在把 BlackRock 的投资组合智能与资产配置专长带给更多顾问，帮助他们扩展业务、构建更好的投资组合。通过让机构级投资组合分析更易获得，我们正在帮助更多顾问利用我们的投资组合智能，从而把更多时间专注于客户关系。”

Jaime Magyera，美国财富与退休业务主管

![Mercer Advisors](https://assets.claude.com/e417bbb81bf909eb4ebe19fe0dee25370dbfd28e.svg)

> “Anthropic 构建与人类价值观一致的 AI。Mercer Advisors 构建与客户利益一致的家庭办公室。这种共同的执着是两家公司的核心，也锚定了我们的合作。Claude 帮助我们的团队在客户的财务生活中无缝协作，而判断与问责仍留在顾问身上。这就是 AI 在任何建立在信任之上的职业中应有的运作方式。”

Daniel Gourvitch，总裁

![Rockefeller Capital Management](https://assets.claude.com/70a6a06de8cab56f6dea00611e665aa99e4d17a4.svg)

> “我们很高兴看到 Anthropic 持续投入于为金融顾问的独特需求量身打造的能力。我们的合作源于一个共同信念：技术应当支持顾问，而不是取代他们，帮助他们应对复杂性、更高效地服务客户，同时让人工判断与自主权始终处于首位。”

Ashley McCarthy，首席运营官兼法律顾问-董事总经理

![Vanguard](https://assets.claude.com/02f6ce25017d80f975786c571ae223b9da5eb42b.svg)

> “Vanguard 致力于帮助顾问把更多时间花在客户身上，少花在应对复杂性上。我们与 Claude 的集成扩展了对 Vanguard 投资解决方案的访问，释放顾问的时间，以提供更个性化的服务。”

Sid Ratna，财务顾问服务部数字与分析主管

![Charles Schwab](https://assets.claude.com/ee30d9d9145114578de5ae6a8bdbf4d06f6b1848.svg)

> “顾问技术的未来将由公司能否把可信数据、强大智能和日常工作流连接起来来定义。我们与 Anthropic 的合作体现了 Schwab 的承诺：帮助注册投资顾问（RIA）在他们已在使用的工具中利用创新，使服务客户、扩展业务并自信成长变得更加容易。”

Jon Beatty，Schwab Advisor Services 主管

![Ritholtz Wealth Management](https://assets.claude.com/7337a170485b3c8f7db6f39e25cbdb18e35dc6d7.png)

> “AI 已经是咨询业务日常工作流的一部分。我不希望我的 CFP 每周花好几个小时埋头于 CRM 更新和任务分配。我希望他们在与客户交谈、投入到规划本身，因为那才是客户真正看重的部分。Claude for Financial Advisors 是我见过的第一个能坐在整个技术栈之上、跨栈完成这些工作、并且内置了我们所需合规控制的产品。”

Josh Brown，首席执行官

![Ritholtz Wealth Management](https://assets.claude.com/7337a170485b3c8f7db6f39e25cbdb18e35dc6d7.png)

> “Ritholtz 没有人会被聊天机器人取代。这门生意的算术是小时，而不是人头：一个顾问拥有的小时数是有限的，而其中大部分被用在了准备和文书工作上，而不是那些真正付钱给我们的人。Claude for Financial Advisors 可以在我们已经在使用的系统之间推进这些琐碎工作，而任何发给客户的内容仍由顾问把关。这为整个公司夺回了有意义的时间，让客户得到更快的响应和更专注的关注。”

Michael Batnick，管理合伙人

![Dynasty Financial Partners](https://assets.claude.com/bf0c4721da997cf3b0cabe9b5b57a4df8e3bd702.png)

> “这是行业不再适应 AI、而开始运行在 AI 之上的时刻。在我们看来，Anthropic 是引擎，Dynasty 是飞机，而顾问始终是飞行员。我们造好飞机，让顾问能够规模化、安全地驾驶它，而永远不必触碰下面的机械结构。结果是，我们不是给顾问另一个仪表盘，我们是把他们的时间还给他们！”

Shirl Penney，首席执行官兼创始人

![Envestnet](https://assets.claude.com/8cb3d07594ed09df536f166bdacceed33d85eadf.svg)

> “顾问花在拼凑信息上的每一个小时，都是没有花在客户身上的一个小时。把 Claude 与 Tamarac 和 MoneyGuide 结合在一起，意味着顾问可以在提问所需的这段时间里理解一个家庭或一份财务计划的某些要素。”

Andrew Stavaridis，首席关系官

![iCapital](https://assets.claude.com/8d7d47070da0c183b9e93c94a2ddb4cf3237318b.svg)

> “随着私募市场在客户投资组合中占据更大比重，顾问需要更简便的方式来应对复杂性。iCapital 将全面的市场平台与管理专业投资所需的数据和基础设施结合起来，而通过 Claude 连接这些数据，有助于把投资智能转化为可行动的洞察。”

Gary Gallagher，总裁

![SS&C](https://assets.claude.com/eeae4806401748e5b724e60461e592ce2ba81204.svg)

> “当 AI 与顾问已经在使用的数据和系统配合工作时，它对顾问最为有效。将 Claude 与 SS&C Black Diamond Wealth Solutions 连接，让顾问可以把客户和投资组合信息带入他们的工作流，减少准备时间，并确保他们始终处于掌控之中。”

Steve Leivent，高级副总裁兼联席主管

![Addepar](https://assets.claude.com/fb76688c14d76e8ecea2860238c3074e4bf75a4e.svg)

> “Addepar 构建了全球领先投资专业人士所依赖的数据与智能基础，用于管理近 10 万亿美元的资产，治理、严谨与控制在我们的平台中原生内置。Addepar 与 Anthropic 的合作，把我们对着复杂投资组合独特而深入的理解带入 Claude，让客户无论在哪里工作都能获得 Addepar 业界领先的投资组合智能。”

Eric Poirier，首席执行官

![Wealth.com](https://assets.claude.com/7d2f8c61095816e9f787e52e70f871b8d7ebdfe8.svg)

> “遗产与税务是客户计划中必须精确的那几层。顾问已经信任 Wealth.com，将其作为客户实际遗产与税务状况的记录系统。在 Claude 内部，这份记录可以直接回答问题，每一个数字都能追溯到产生它的源文件。”

Rafael Loureiro，首席执行官

![Salesforce](https://assets.claude.com/122680b4a90e354a227934e7b37b3cd62b0cc11f.svg)

> “顾问在掌握客户全貌时才能发挥最佳水平。将 Salesforce 连接到 Claude，让公司在我们的平台上建立的关系可以随顾问一起流动，且仍处于他们已有的权限与控制之内。与 Anthropic 一起，我们正在给公司更多方式，把可信的客户数据用于服务他们所服务的人。”

Eran Agrios，金融服务高级副总裁兼总经理

![Orion](https://assets.claude.com/43c094e940d801886608b78e8b4ad48d4852dd04.svg)

> “客户从不会看到一场好会议背后的工作，但一旦缺失，他们就能感觉到。通过与 Anthropic 的合作，Orion 为 Claude for Financial Advisors 提供的插件把公司的投资组合和 CRM 数据带入会议准备、跟进草稿和销售管道回顾，全部在公司现有的权限与控制之内完成。技术承担了更多后台准备工作，让顾问可以继续专注于客户和对话。顾问走进会议时已准备就绪，而不必花几个小时把所有材料拼起来。”

Reed Colley，总裁

![zocks](https://assets.claude.com/05a6a0c1132f543d0537102984022c0c90774dde.png)

> “优质的财务建议取决于了解客户生活中正在发生什么，而不只是他们账户里有什么，”Zocks 首席执行官兼联合创始人 Mark Gilbert 表示。“Claude 与 Zocks 之间扩展的合作，把过去分散在多个来源和系统中的数据与个人客户上下文汇集在一起。如今，通过 Claude 完成的每一项任务和分析，都建立在更完整的客户理解之上。这也让企业机构拥有更大的灵活性，围绕其顾问实际的工作方式来构建 AI 工作流。”

Mark Gilbert，首席执行官兼联合创始人

![RFG Advisory](https://assets.claude.com/b85fd6f58a1f1a493b2cc9de09044b6b2164466e.png)

> “MCP 正在从根本上改变我们为顾问构建技术的方式。随着 Claude 和 Zocks 直接集成进我们的技术栈，过去需要数月配置并依赖外部合作伙伴的问题，正越来越多地能由我们自己的开发团队解决。这让我们可以自由地更快行动、与一流的合作伙伴协作，并围绕顾问实际运作的方式去构建。与其要求顾问适应技术，我们可以让技术去适应他们。”

Dr. Jordan Hutchison，技术与运营副总裁

![Wealthbox](https://assets.claude.com/31be98f5c18121a5063482dbcb91cd4bb812e9c7.svg)

> “顾问们多年来在 Wealthbox 中积累了深厚的客户上下文。这让他们可以把这些上下文直接带入 Claude，并让前沿模型据此工作，例如准备会议、处理跟进、起草沟通内容，同时一切都保持与他们业务所依赖的 CRM 相连。”

John Rourke，首席执行官兼联合创始人

![BlackRock](https://assets.claude.com/d72d42304889c5ecd4f2ba410dfde53b13255b97.svg)

> “顾问们正在应对日益复杂的客户需求，同时面对市场与技术加速变化的节奏。我们与 Anthropic 的合作是我们更广泛努力中的重要一步，旨在把 BlackRock 的投资组合智能与资产配置专长带给更多顾问，帮助他们扩展业务、构建更好的投资组合。通过让机构级投资组合分析更易获得，我们正在帮助更多顾问利用我们的投资组合智能，从而把更多时间专注于客户关系。”

Jaime Magyera，美国财富与退休业务主管

![Mercer Advisors](https://assets.claude.com/e417bbb81bf909eb4ebe19fe0dee25370dbfd28e.svg)

> “Anthropic 构建与人类价值观一致的 AI。Mercer Advisors 构建与客户利益一致的家庭办公室。这种共同的执着是两家公司的核心，也锚定了我们的合作。Claude 帮助我们的团队在客户的财务生活中无缝协作，而判断与问责仍留在顾问身上。这就是 AI 在任何建立在信任之上的职业中应有的运作方式。”

Daniel Gourvitch，总裁

![Rockefeller Capital Management](https://assets.claude.com/70a6a06de8cab56f6dea00611e665aa99e4d17a4.svg)

> “我们很高兴看到 Anthropic 持续投入于为金融顾问的独特需求量身打造的能力。我们的合作源于一个共同信念：技术应当支持顾问，而不是取代他们，帮助他们应对复杂性、更高效地服务客户，同时让人工判断与自主权始终处于首位。”

Ashley McCarthy，首席运营官兼法律顾问-董事总经理

1/18

## 开始使用

顾问插件今天即可使用。我们建议注册投资顾问采用 Enterprise 计划，因为它包含支持记录保存的审计日志。如果你已有 Enterprise 许可证，请打开 Cowork，在插件浏览器中找到「Claude for Financial Advisors」，安装它并按照引导式设置连接你的工具（也可以从[此处的市场](http://github.com/anthropics/claude-for-financial-advisors)安装）。

如果你没有 Enterprise 许可证，请使用这个[表单](https://forms.gle/y9YmFF2j4moRinJA7)提出申请，Anthropic 团队成员会与你联系说明后续步骤。在 2026 年 9 月底之前申请新许可证的公司，还将获得一次性用量额度，帮助他们开始使用该插件。

在我们的[解决方案页面](https://claude.com/solutions/financial-services#financial-advisors)了解更多信息，并参加我们本周五 9/18 上午 11 点（美东时间）的[网络研讨会](https://claude.com/resources/webinars/inside-claude-for-financial-advisors)。

*本文最初发布于 2026 年 9 月 14 日。文章已更新，以加入来自 Anthropic 合作伙伴的更多连接器。*

文章

2026 年 10 月 26 日

### 扩展 Claude for Nonprofits

我们的新 Claude for Nonprofits 插件为每个经过验证的非营利组织带来新技能，接手那些让小型团队在筹款、营销和招聘之间捉襟见肘的运营工作。

文章

2026 年 10 月 23 日

### Claude Cowork 与聊天功能在 Enterprise 中融为一体

Claude Enterprise

文章

2026 年 10 月 23 日

### Claude Duet 的安全性、隐私与保障

Claude Duet 是一个主动为你工作的智能体，即使你离开时也是如此。它建立在两层保护之上：Claude 模型本身的安全训练，以及 Claude Code 和 Claude Managed Agents 等产品中已有的防护措施。在此之上，我们又增加了针对跨账户工作和代你行动的新保护。

文章

2026 年 10 月 22 日

### 完整的 Claude Platform 现已在 Google Cloud 上提供

使用 Google Cloud 上的 Claude Models（Anthropic 托管），借助 Google Cloud 的身份验证、计费与承诺用量到期，访问 Claude Platform 的各项功能。

Claude Platform

## 用 Claude 变革你的组织运作方式

[查看定价](https://claude.com/pricing#api)[联系销售](https://claude.com/contact-sales)

### 订阅开发者通讯

产品更新、操作指南、社区聚焦，以及更多内容。每月送达你的收件箱。

如果你希望收到我们的月度开发者通讯，请提供你的电子邮箱地址。你可以随时退订。
