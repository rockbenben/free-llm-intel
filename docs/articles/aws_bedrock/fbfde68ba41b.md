---
vendor: aws_bedrock
title: NewDay builds A Generative AI based Customer service Agent Assist with over 90% accuracy
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/newday-builds-a-generative-ai-based-customer-service-agent-assist-with-over-90-accuracy
date: 2025-06-24
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 864e573e24ff
---

# NewDay 构建基于生成式 AI 的客服 Agent 助手，准确率超过 90%

*本文与 NewDay 的 Sergio Zavota 和 Amy Perring 共同撰写。*

[NewDay](https://www.newday.co.uk/) 有一个清晰而明确的宗旨：帮助人们借助信贷向前迈进。NewDay 通过其自研技术系统，为约 400 万名客户负责任地提供信贷渠道，并交付卓越的客户体验。NewDay 的联络中心每年处理 250 万通来电，因此，拥有合适的技术来赋能客服 agent 与客户进行有效对话，对于交付出色的客户体验至关重要。

联络中心的角色很复杂，仅在 Customer Services 一个领域就有近 200 篇知识文章，agent 有时需要从这些文章中为客户问题找到正确答案。这引出了 NewDay 在 2024 年初的一个黑客松命题：如何借助生成式 AI 的力量提升问题解决速度，同时改善客户与 agent 的体验。

这次黑客松催生了 NewAssist——一个实时生成式 AI 助手，通过语音转文字能力赋能客服 agent。NewAssist 构建在 [Amazon Bedrock](https://aws.amazon.com/bedrock/?gclid=EAIaIQobChMIptmIuvijjAMVzhWtBh1HJCgLEAAYASAAEgIh6_D_BwE&trk=0eaabb80-ee46-4e73-94ae-368ffb759b62&sc_channel=ps&ef_id=EAIaIQobChMIptmIuvijjAMVzhWtBh1HJCgLEAAYASAAEgIh6_D_BwE:G:s&s_kwcid=AL!4422!3!692006004688!p!!g!!amazon%20bedrock!21048268554!159639952935) 之上，可在与客户的实时交互中提供快速、具备上下文感知的支持。

本文分享 NewDay 如何把黑客松点子变成成功的生成式 AI 方案，以及他们在这段旅程中的经验。

## 缘起与早期挑战

NewAssist 凭借生成式 AI 在缩短通话解决时间上的潜力赢得了这次黑客松。然而，尽管开局不错，团队仍面临重大障碍：

- **成本管理与优先级竞争 ——** 在大型战略举措众多、资源有限的情况下，团队保持了专注和主动，即便争取高管支持并不容易
- **缺少基础设施 ——** 现有遗留系统不利于快速试验
- **技术尚未验证 ——** NewAssist 团队需要证明这项投入确实能为业务带来价值

考虑到这些挑战，实现一个成熟语音助手的雄心过于高远，团队因此做了战略调整。他们收缩到聊天机器人方案，集中精力搭起一个概念验证，以验证现有的知识管理方案能否与生成式 AI 技术有效配合。NewDay 联络中心团队的目标是为其未来的生成式 AI 方案使用单一事实来源，因此这项任务对于为稳固的长期战略奠定正确基础至关重要。团队采用敏捷、循序渐进的方式，由三名专家组成的小型跨职能团队着手构建概念验证，目标准确率为 80%。他们构建了一个包含 100 多个问题及对应正确答案的黄金数据集（golden dataset），并用它测试该生成式 AI 应用，以评估回答的准确率。

## 方案概览

NewAssist 的技术设计与实现遵循以下原则：

- **拥抱实验文化 ——** 组建了一个三人的小型跨职能团队。团队遵循 [Improvement Kata](https://public.websites.umich.edu/~jmondisa/TK/Handbook/Full_IK_Handbook_v32.0.pdf) 方法论，实施快速的“构建-度量-学习”循环。仅用 10 周、超过 8 轮实验，团队就打磨出了方案。早期迭代的准确率低于 60%，但通过严格的测试和明智的数据策略，他们把性能提升到 80% 以上，短短几周内提升了 33%。
- **采用无服务器基础设施 ——** [Amazon Bedrock](https://aws.amazon.com/bedrock/)、[AWS Fargate](https://aws.amazon.com/fargate/)、[AWS Lambda](https://aws.amazon.com/pm/lambda/?gclid=Cj0KCQjwhYS_BhD2ARIsAJTMMQbJI73vM8jqZQpj-unBFHpqG1XSWnWcCpeTN6pLuCeotwd8WhVGVxgaAnyXEALw_wcB&trk=27324d1f-ee08-40b9-8e7b-5ac228e2fecc&sc_channel=ps&ef_id=Cj0KCQjwhYS_BhD2ARIsAJTMMQbJI73vM8jqZQpj-unBFHpqG1XSWnWcCpeTN6pLuCeotwd8WhVGVxgaAnyXEALw_wcB:G:s&s_kwcid=AL!4422!3!651612449951!e!!g!!aws%20lambda!19836376234!148728884764)、[Amazon API Gateway](https://aws.amazon.com/api-gateway/) 和 [Amazon OpenSearch Serverless](https://aws.amazon.com/opensearch-service/features/serverless/) 构成了该应用的骨干。这种做法不仅降低了成本（运行成本保持在每月 400 美元以下），还确保系统能够按实时需求扩展。此外，这让团队中的开发者可以只专注于能验证实验结果的活动，无需操心基础设施管理。

NewAssist 以[检索增强生成](https://aws.amazon.com/what-is/retrieval-augmented-generation/)（RAG）方案的形式实现。下图展示了高层方案架构。

[![NewAssist 架构，包含 Cognito、Lambda 与 Amazon Bedrock](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/13/ML-18185-arch-diag.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/13/ML-18185-arch-diag.png)

该高层架构由五个组件构成：

- **用户界面 ——** 使用 [Streamlit](https://streamlit.io/) 框架构建的简洁 AI 助手 UI。用户可以登录、提问、以点赞或点踩的形式对答案给出反馈，并可选择性地提供评论说明负面反馈的原因。UI 托管在 Fargate 上，身份验证通过 [Amazon Cognito](https://aws.amazon.com/cognito/) 结合 [Microsoft Entra ID](https://www.microsoft.com/en-us/security/business/identity-access/microsoft-entra-id) 集成实现，为客服 agent 提供单点登录（SSO）能力。
- **知识库处理 ——** 这个组件主要带来了 40% 的准确率提升。在这里，文章通过第三方知识库的 API 检索，并按既定的分块（chunking）策略切分。分块被处理为向量嵌入（vector embedding），最终存入用 OpenSearch Serverless 实现的向量数据库。
- **建议生成 ——** UI 上的问题被转发到建议生成组件，该组件检索最相关的分块，并把这些分块传给大语言模型（LLM），由其基于上下文生成建议。[Anthropic 的 Claude 3 Haiku](https://www.anthropic.com/news/claude-3-haiku) 是首选 LLM，通过 Amazon Bedrock 访问。尽管已有性能更强的模型发布，撰写本文时仍在用 Anthropic 的 Claude 3 Haiku。原因有两点：第一，它是在 Amazon Bedrock 上可访问且能给出满意结果的最具成本效益的模型；第二，NewDay 有最长 5 秒的响应时间要求，Anthropic 的 Claude 3 Haiku 能满足。为达到所需准确率，NewDay 尝试了不同的分块策略和检索配置，同时以 Anthropic Claude 3 Haiku 控制成本。
- **可观测性 ——** 问题、答案与反馈会被记录到 [Snowflake](https://www.snowflake.com/en/uk/) 中。在其上构建了仪表盘，展示准确率等不同指标。每周，业务专家会审阅带负面反馈的答案，AI 工程师把它们转化为实验，若实验成功则提升方案性能。此外，[Amazon CloudWatch](https://aws.amazon.com/cloudwatch/) 记录架构中所述 AWS 服务处理的请求。
- **离线评估 ——** 当实验循环中产生 NewAssist 的新版本时，先在预生产环境用评估数据集评估。若该版本的准确率超过指定阈值，就可以部署到生产环境。

## 理解你的数据，并在健壮的数据处理方案上投入

对 NewAssist 准确率影响最大的一项实验——使其提升了 20%——是把通用的知识文章数据解析器替换为定制版本。这个新解析器专为理解 NewDay 数据的结构与含义而设计，借助这些数据，LLM 能够生成更准确的输出。起初，实现数据处理逻辑的工作流包含以下步骤：

- 从数据源手动提取文章并保存为 PDF。
- 使用 [PyPDF](https://pypi.org/project/pypdf/) 解析文章。

采用这种做法，方案的准确率约为 60%。原因很简单：该逻辑没有考虑所处理数据的类型，因而给出了低于平均水平的结果。当 NewDay 开始研究自己的数据后，情况发生了变化。在 NewDay，面向 agent 的知识文章由联络中心领域的专家团队创建。他们按照特定方法论创建文章，并存储在第三方内容管理系统中。这个系统尤其支持通过 widget 创建文章，例如列表、横幅和表格。此外，该系统提供可用于检索文章的 API。文章以 JSON 对象的形式返回，其中每个对象包含一个 widget。可用的 widget 数量有限，每一种都有特定的 JSON schema。发现这一点后，团队研究了每一种 widget 的 schema，并编写了定制的解析逻辑，以提取相关内容并用精致的方式格式化。这比简单地用 PyPDF 解析耗时更长，但结果积极。仅专注于数据、完全不碰 AI 组件，方案的准确率就从 60% 提升到 73%。这表明数据质量在开发有效的生成式 AI 应用中起着关键作用。

## 理解用户如何使用你的方案

在达到 80% 准确率这一里程碑后，团队证明了概念验证可行，因此在仅仅 3 个月后就获批把试验扩展到 10 名客服 agent。NewDay 挑选了 10 名经验丰富的 agent，因为他们需要找出方案在哪些地方给出了错误回答。NewAssist 刚交到客服 agent 手中，就发生了意料之外的事。agent 使用 NewAssist 的方式与 NewDay 技术团队的预期不同：他们在向 NewAssist 提问时使用了各种缩写。例如，请看下面两个问题：

- 我如何为客户设置直接借记（direct debit）？
- 我如何为 cst 设置 dd？

在这里，direct debit 被缩写为“dd”，customer 被缩写为“cst”。除非上下文中提供了这些信息，否则 LLM 很难给出正确答案。结果，当 agent 开始使用时，NewAssist 的准确率降到了 70%。NewDay 采用的解决办法是把缩略语和简写静态注入 LLM 的 prompt，从而让它更好地理解问题。准确率慢慢恢复到 80% 以上。这只是一个简单的例子，说明把产品交到最终用户手中来验证假设有多么重要。另一个被发现的积极之处是，agent 会用 NewAssist 来了解如何向客户解释某个流程。众所周知，把技术内容转换成非技术人员能理解的形式并不容易。agent 开始向 NewAssist 提出这样的问题：“我该如何向客户解释如何解锁他们的账户？”，结果得到了可以直接读给客户听的出色答案。

## 扩大规模以产生更大影响

通过把 NewDay 的试验扩展到 10 名 agent，NewDay 得以测试许多不同的场景。团队审阅了负面回答并做根因分析。NewAssist 团队发现知识库中存在若干缺口，并通过新增和改进内容解决了这些问题。他们还通过在缩略语和内部语言上训练来增强方案。此外，他们为试点团队提供了关于如何有效使用该方案的培训和反馈。通过这些做法，NewAssist 团队把准确率提升到 90% 以上，并获得 NewDay 高管团队批准把方案产品化。NewDay 目前正向 150 多名 agent 推广该方案，并计划把范围扩展到 Customer Operations 内的所有部门（例如欺诈与催收）。早期结果显示，agent 提出问题后检索答案所需的时间大幅缩短。此前，他们平均需要 90 秒才能检索到答案；现在该方案在 4 秒内就能检索到答案。

## 构建可用于生产的生成式 AI 应用的经验

NewDay 在部署可用于生产的生成式 AI 应用过程中获得了以下洞见：

- **拥抱实验文化 —— 这包括以下策略：** 采用敏捷、迭代的方式快速验证假设并改进方案；采用 Improvement Kata 和“构建-度量-学习”循环等方法，在短时间内取得显著收益；从聚焦的概念验证小步起步，在全面部署前逐步扩展以验证有效性
- **专注数据质量 ——** 花时间理解并正确处理你的数据，因为这会带来可观的改善
- **理解用户如何与产品交互 —— 这包括以下步骤：** 与真实用户进行真实场景测试，以发现意料之外的使用模式与行为；准备好根据用户洞见调整方案，例如容纳内部行话或缩略语；留意用户测试中可能出现的未预见用例，因为它们能为功能开发提供宝贵方向。在 AI 能力与人类专业知识之间取得平衡，认识到监督与培训对于让技术得到最佳使用的重要性

## 展望未来

NewAssist 的旅程远未结束。借助健壮的反馈机制和恰当程度的监督，团队将继续交付优化，进一步提升输出的准确率。未来的迭代将探索与 AWS AI 服务更深度的集成，在客户交互中进一步优化人类智能与机器智能之间的平衡。通过采用 AWS 无服务器方案以及敏捷、数据驱动的方法，NewDay 把一个黑客松点子变成了优化客户服务的强大工具。NewAssist 的成功印证了当创造力遇上健壮的云基础设施时所能实现的创新，也为联络中心技术的下一波进步铺平了道路。

## 结论

NewAssist 的旅程展示了 AWS 在支撑 RAG 方案快速试验与部署方面的能力。对于希望提升客户服务、精简运营或从数据中挖掘新洞见的组织，AWS 除了提供众多其他机会之外，也提供了推动创新的工具与基础设施：

- **加速 RAG 实验 ——** Amazon Bedrock、Lambda 和 Amazon Serverless 等服务让想法的快速构建与迭代成为可能
- **放心扩展 ——** AWS 的[无服务器](https://aws.amazon.com/serverless/)产品在提供有效成本管理的同时，确保方案能随需求增长
- **专注数据质量 ——** 如果源头的数据质量不够好，你可以实施数据处理、清洗和抽取技术来提升回答的准确率
- **简化部署 ——** Fargate 和 API Gateway 简化了从概念验证走向生产就绪应用的过程
- **优化性能 ——** [跨区域推理](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html)及其他 AWS 特性有助于在满足严格延迟要求的同时平衡成本考量

想进一步了解 AWS 如何帮助你的生成式 AI 之旅，请访问：[用生成式 AI 重塑你的业务](https://aws.amazon.com/ai/generative-ai/?trk=c30d9c04-dff1-48dd-85e1-551e986fbb60&sc_channel=ps&ef_id=Cj0KCQjw0qTCBhCmARIsAAj8C4bw3YeanT24ZgQMVnhHaz-aEf0ZlaiRhlBt2SAM3-O64F26TOyjIA4aAr9rEALw_wcB:G:s&s_kwcid=AL!4422!3!686122457182!e!!g!!amazon%20generative%20ai!20894978760!155960704734&gad_campaignid=20894978760&gbraid=0AAAAADjHtp_zSYqiHDZM4hgKjksmG3mYT&gclid=Cj0KCQjw0qTCBhCmARIsAAj8C4bw3YeanT24ZgQMVnhHaz-aEf0ZlaiRhlBt2SAM3-O64F26TOyjIA4aAr9rEALw_wcB)。

### 关于作者

**[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/13/DSC_3445.jpg)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/13/DSC_3445.jpg) Kaushal Goyal** 是 AWS 的解决方案架构师，服务于英国和爱尔兰地区的企业金融服务客户。Kaushal 拥有深厚的银行技术背景，此前曾在多家大型银行主导数字化转型举措。在 AWS，Kaushal 帮助金融机构对遗留系统进行现代化改造并实施云原生方案。作为生成式 AI 爱好者与容器专家，Kaushal 专注于为企业客户带来创新的 AI 方案，并通过博客和公开演讲分享这些经验。

**[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/13/IMG_2370.jpg)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/13/IMG_2370.jpg)Sergio Zavota** 是 NewDay 的 AI 架构师，专长于 MLOps 与生成式 AI。Sergio 设计可扩展的平台，把机器学习工作负载产品化，并在 NewDay 实现规模化的生成式 AI。Sergio 在行业会议和研讨会上分享他的专业知识，重点是如何把 AI 方案产品化，以及让 AI 与组织目标保持一致。

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/13/Picture1-9.jpg)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/13/Picture1-9.jpg)**Amy Perring** 是 NewDay 的高级优化经理，常驻伦敦。她擅长通过客户和 agent 的反馈深入理解联络驱动因素。这有助于识别优化机会，通过引入或改进产品与流程来提升整体效率与体验。

**[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2023/01/03/udemayur.jpg)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2023/01/03/udemayur.jpg)Mayur Udernani** 负责 AWS 在英国和爱尔兰面向商业企业的生成式 AI 与 ML 业务。在工作中，Mayur 把大部分时间花在客户和合作伙伴身上，帮助他们借助 AWS Cloud、生成式 AI 与 ML 服务，打造有影响力的方案，解决客户最迫切的需求或服务更广泛的行业。Mayur 住在伦敦地区。他拥有印度管理学院的 MBA 学位和孟买大学的计算机工程学士学位。
