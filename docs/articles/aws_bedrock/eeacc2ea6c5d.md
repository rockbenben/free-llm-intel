---
vendor: aws_bedrock
title: Build an intelligent multi-agent business expert using Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-an-intelligent-multi-agent-business-expert-using-amazon-bedrock
date: 2025-06-25
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: e3310ceb668c
---

# 使用 Amazon Bedrock 构建智能多 agent 业务专家

本文演示如何使用 [Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/) 中的[多 agent 协作（multi-agent collaboration）](https://aws.amazon.com/blogs/aws/introducing-multi-agent-collaboration-capability-for-amazon-bedrock/)，构建多 agent 系统来解决生物制药行业的复杂业务问题。我们展示研发（R&D）、法务与财务领域的专用 agent 如何协同工作，通过分析来自多个来源的数据来提供全面的业务洞察。

## Amazon Bedrock Agents 与多 agent 协作

商业智能与市场研究让大小企业都能通过数据把握行业趋势与竞争格局，并影响关键的业务战略。例如，生物制药公司利用数据了解药品市场规模、临床试验、副作用发生率以及创新与陷阱——通过分析专利与法律文书来形成投资策略。在此过程中，组织面临访问与分析分散在多个数据源中的信息这一挑战。整合并查询这些异构数据集可能是一项复杂而耗时的任务，需要开发者应对不同的数据格式、查询语言与访问机制。此外，要全面理解组织的运作，往往需要结合来自法务、财务与研发等不同板块的数据洞察。

生成式 AI 的 agentic 系统已成为有前景的解决方案，使组织能够利用生成式 AI 完成自主推理与基于行动的任务。然而，迄今为止许多 agentic 系统采用单 agent 架构，这在复杂的商业环境中带来挑战。除了管理多个数据源的难题之外，为多个业务领域编码信息与指引，可能使 agent 所用大语言模型（LLM）的 prompt 膨胀到因长上下文而“遗忘中间部分”的程度。因此，agent 能有效编码的每个领域的知识在广度与深度之间存在权衡。此外，为 agent 使用单个 LLM 也会限制针对所选模型在成本、延迟与准确性方面的优化。

Amazon Bedrock Agents 及其多 agent 协作功能为应对这些挑战、构建智能且自动化的 agentic 系统提供了强大的企业级解决方案。作为 AWS 生态中的托管服务，Amazon Bedrock Agents 提供与 AWS 数据源的无缝集成、内建的安全控制以及企业级的可扩展性。它内建支持其他 Amazon Bedrock 功能，例如 [Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/) 与 [Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/)。该服务显著降低了部署开销，让开发者可以在熟悉且 API 驱动的 AWS Cloud 环境与控制台中专注于 agent 逻辑。具备专用子 agent 的 supervisor agent 模式实现了高效的分布式问题求解，通过智能路由来拆解复杂任务。

本文中，我们讨论如何使用多 agent 协作构建多 agent 系统，以解决一家虚构生物制药公司面临的复杂业务问题——这些问题需要来自研发、法务与财务三个专用领域的专业知识与数据。我们演示如何智能地组合异构来源中的数据以支持复杂推理，以及 agent 协作如何促进开放式问答，例如“治疗产品 X 的副作用可能带来哪些潜在的法律与财务风险？这些风险可能如何影响公司的长期股价表现？”

*(下图展示了我们在制药示例中所用的 supervisor agent 与 3 个子 agent 的角色，以及使用多 agent 协作带来的好处。)*

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/05/image-1-7.png)

## 解决方案概览

我们的用例围绕一家虚构制药公司 PharmaCorp 展开，它面临的挑战是管理其制药研发、法务与财务部门的大量数据。每个部门都同时处理结构化数据（例如股价）与非结构化数据（例如临床试验报告）。各部门的数据位于不同的数据存储中，这让团队难以获得跨职能洞察，也拖慢了决策流程。

为解决这一问题，我们使用 Amazon Bedrock Agents 中的多 agent 协作，为每个部门构建带领域专用子 agent 的多 agent 系统。这些子 agent 高效处理数据查询与信息检索，主 agent 在子 agent 之间传递必要的上下文，并综合跨部门的洞察。多 agent 架构让 PharmaCorp 能在几分钟内获得原本需要耗费数小时人力才能汇编的专业知识与信息。这种做法打破了数据孤岛，强化了组织协作。

下面的架构图展示了该方案的部署方式。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/05/image-2-8.png)

主 agent 充当编排者，向多个子 agent 提问并综合检索到的数据：

- 研发子 agent 可通过 [Amazon Athena](https://aws.amazon.com/athena/) 访问临床试验数据，以及非结构化的临床试验报告
- 法务子 agent 可访问非结构化的专利与诉讼法律文书
- 财务子 agent 可通过 Athena 访问研究预算数据，以及存储在 [Amazon Redshift](https://aws.amazon.com/redshift/) 中的历史股价数据

每个子 agent 都只有细粒度的权限，仅能访问其所在领域的数据。所用数据与模型的详细信息，以及主 agent 的交互方式，将在后续章节中说明。

### 数据集

我们使用 [Anthropic 的 Claude](https://www.anthropic.com/claude) 3.5 Sonnet 模型生成了合成数据，涵盖制药研发、法务与财务三个领域。这些领域包含存储在 SQL 表中的结构化数据，以及用于领域知识库的非结构化数据。相关数据可通过以下文件获取：[研发](https://aws-blogs-artifacts-public.s3.us-east-1.amazonaws.com/artifacts/ML-16929/clinical_trial_reports.zip)、[法务](https://aws-blogs-artifacts-public.s3.us-east-1.amazonaws.com/artifacts/ML-16929/legal_briefs.zip)、[财务](https://aws-blogs-artifacts-public.s3.us-east-1.amazonaws.com/artifacts/ML-16929/patents.zip)。

我们已努力在领域内部与跨领域之间对齐合成数据。例如，临床试验报告与相关表中的每个试验及副作用相对应。股价的涨跌往往与专利和诉讼相关联。不过，数据之间仍可能存在轻微的不一致。

### 制药研发领域

制药研发领域有三张表：Drugs、Drug Trials 与 Side Effects。每张表都通过 Athena 从 [Amazon Simple Storage Service](https://aws.amazon.com/s3/)（Amazon S3）查询。Drugs 表包含公司现有产品、治疗领域、目标适应症、作用机制、研发阶段、发现年份与首席科学家的信息。Drug Trials 表包含每种药物的具体试验信息，例如阶段、日期、参与人数与结果。Side Effects 表包含各试验报告的副作用、发生频率与严重程度。

制药研发领域的非结构化数据由每次试验的合成临床试验报告构成，其中包含关于试验设计、结果与建议的更详细信息。

### 法务领域

法务领域包含由专利与诉讼法律文书构成的非结构化数据。专利包含发明背景、描述与实验结果等信息。法律文书包含诉讼庭审程序、结果与分析等信息。

### 财务领域

财务领域有两张表：Stock Price 与 Research Budgets。Stock Price 表存储在 Amazon Redshift 中，包含 PharmaCorp 的历史月度股价与成交量。Amazon Redshift 是一款针对联机分析处理（OLAP）优化的数据库，这类处理通常涉及分析大量数据并执行复杂分析，就像分析师研究历史股价时那样。Research Budgets 表通过 Athena 从 Amazon S3 访问，包含各部门的年度预算。

这一数据设置展示了多 agent 框架如何综合来自多个数据源与数据库的数据。实践中，数据也可以存储在 [Amazon Relational Database Service](https://aws.amazon.com/rds/)（Amazon RDS）等其他数据库中。

### 使用的模型

本次多 agent 演示使用 Anthropic 的 Claude 3 Sonnet，它在智能与速度之间有良好的平衡。采用多 agent 架构后，你还可以根据用例以及准确性与延迟等需求，选用更强大的模型或更小、更快的模型。

## 前置条件

要部署该方案，你需要以下前置条件：

- 一个有效的 AWS 账户。
- 在 Amazon Bedrock 上可访问 Amazon Titan Embeddings G1 – Text、Anthropic 的 Claude 3 Sonnet 与 Anthropic 的 Claude 3.5 Sonnet。具体说明请参阅[添加或移除 Amazon Bedrock 基础模型的访问权限](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access-modify.html)。

## 部署方案

我们使用 [AWS CloudFormation](https://aws.amazon.com/cloudformation) 部署该方案的资源。CloudFormation 模板会创建两个 S3 存储桶、两个 [AWS Lambda](https://aws.amazon.com/lambda) 函数、一个 Amazon Bedrock agent、一个 Amazon Bedrock 知识库，以及一个 [Amazon Elastic Compute Cloud](https://aws.amazon.com/ec2)（Amazon EC2）实例。

下载提供的 [CloudFormation 模板](https://aws-blogs-artifacts-public.s3.us-east-1.amazonaws.com/artifacts/ML-16929/cfn/mac-stack-template.yaml)，然后完成以下步骤来部署该堆栈：

- 打开 AWS CloudFormation 控制台（该方案首选的 AWS Region 为 `us-west-2` 或 `us-east-1`）。
- 在导航窗格中选择 **Stacks**。
- 选择 **Create stack** 与 **With new resources (standard)**。
- 选择 **Choose existing template **，并上传所提供的 CloudFormation 模板文件。
- 输入堆栈名称，然后选择 **Next**。
- 保持堆栈设置为默认值，然后选择 **Next**。
- 勾选确认复选框，然后创建堆栈。

堆栈创建完成后，你可以在 Amazon Bedrock 控制台上看到新的 supervisor agent。

## agent 协作示例

部署完成后，你可以测试各 agent 之间的通信，它们能帮助回答跨 PharmaCorp 三个部门的复杂问题。例如，我们向主 agent 提问“NeuroClear 的 2 期试验结果如何影响了 PharmaCorp 的股价、专利申请以及潜在的法律风险？”

这个问题需要全面理解 NeuroClear 临床试验结果、财务影响与 PharmaCorp 法律结果之间的关系。下面我们看看多 agent 系统如何处理这一复杂查询。

主 agent 判断需要三个专用子 agent 的输入，才能全面评估 NeuroClear 的临床试验结果可能如何影响 PharmaCorp 的法务与财务表现。它把用户的问题拆解为关键组成部分，并制定计划，从每位专家那里收集详细的洞察。以下是它的思维链推理、任务拆解与子 agent 路由：

```
This is a complex question that requires information from all three divisions to 
provide a comprehensive answer. 
I need to:
Get information about NeuroClear's Phase 2 trial results from Pharmaceutical division
Check stock price movements around the trial period from Finance division
Look for any patent filings and legal implications from Legal division
```

接着，主 agent 向研发子 agent 提问：

```
Please provide details about NeuroClear's Phase 2 clinical trials, including trial dates,
outcomes, success rates, and any significant findings or side effects.
```

研发子 agent 正确地规划并执行了自己的一系列步骤，包括执行查询与搜索自有的知识库。它的响应如下：

```
Based on the information from the knowledge base search and Athena database queries,
here are the key details about NeuroClear's Phase 2 clinical trials:

* There were two Phase 2 trials conducted for NeuroClear, a novel drug for treating 
Alzheimer's disease.
* The first trial ran from June 2019 to May 2020 with 250 participants. It showed a 
moderate success rate of 0.65 in slowing cognitive decline compared to placebo.
* The second trial ran from August 2021 to August 2022 with 400 participants. It had 
a slightly higher success rate of 0.68.
* Both trials were randomized, double-blind, and placebo-controlled. The dosages tested 
were 25mg, 50mg, and 75mg once daily.
* Primary endpoints were change in ADAS-Cog score and secondary endpoints included CDR-SB, 
hippocampal volume, and CSF biomarkers.
* Notable side effects observed included insomnia (frequency 0.14-0.15, severity 3), 
anxiety (frequency 0.12-0.13, severity 3), tremors (frequency 0.09-0.1, severity 2), 
and weight loss (frequency 0.08, severity 2).

The trials showed NeuroClear had moderate efficacy in slowing cognitive decline in 
Alzheimer's patients, with an acceptable safety profile. The results supported 
advancing NeuroClear to larger Phase 3 trials to further evaluate its potential 
as a treatment for Alzheimer's disease.
```

主 agent 拿到这些信息后确定了下一步：

```
Now that I have the trial dates and outcomes, I should check the stock price movements
during these periods and any patent/legal activities.
```

它向财务子 agent 提出以下请求：

```
Please provide stock price analysis for two periods:

1. June 2019 - May 2020
2. August 2021 - August 2022

Specifically looking for significant price movements and trading volume changes around
the completion dates of these periods, which correspond to NeuroClear's Phase 2 trial
results.
```

财务子 agent 规划并在其股票数据库上执行查询，响应如下：

```
Stock Price Analysis for NeuroClear's Phase 2 Trial Periods:

Period 1 (June 2019 - May 2020):
* Final closing price: $34.69
* Average price: $31.43
* Price range: $27.99 - $34.69
* Average daily volume: 630,874 shares
* The period ended with moderate trading volume (566,927 shares)

Period 2 (August 2021 - August 2022):
* Final closing price: $53.71
* Average price: $49.79
* Price range: $44.11 - $55.41
* Average daily volume: 640,098 shares
* The period ended with slightly lower volume (491,629 shares)

Key Observations:
* Significant price appreciation between periods, with Period 2 showing ~58% 
higher average prices
* Both periods showed similar trading volume patterns, with Period 2 showing 
slightly higher average volume
* The stock showed slight negative movement on both completion dates 
(-0.20% and -0.77% respectively)
```

随后，主 agent 向法务子 agent 提问：

```
Please provide information about:
1. Any patent filings related to NeuroClear, particularly during or after the 
Phase 2 trials (2019-2022)
2. Any legal risks or challenges identified related to NeuroClear's development 
or trial results during this period.
```

法务子 agent 搜索其知识库并响应如下：

```
Based on the patent search results, two key patent filings related to NeuroClear 
during or after its Phase 2 trials from 2019-2022 were:

1. A blood-brain barrier penetration enhancer system using nanoparticles to improve 
delivery of neurological drugs like NeuroClear to the brain (Patent ID: PAT004, 
filed in 2022). This technology could have been developed to address challenges 
with getting NeuroClear across the blood-brain barrier during clinical trials.
2. A targeted neurological receptor blocker designed to selectively inhibit 
receptors implicated in neurodegenerative diseases (Patent ID: PAT003, filed in 2021). 
This suggests NeuroClear may work by blocking certain neural receptors involved in 
conditions like Alzheimer's disease.

The legal search results identified a few key legal risks and challenges related to 
NeuroClear's development and trial results from 2019-2022:

1. A product liability lawsuit alleging NeuroClear caused cognitive impairment in a 
patient, with evidence that PharmaCorp failed to properly warn about this risk despite 
internal knowledge of it (Case 2023-CV-006).
2. A class action lawsuit alleging failure to warn about the risk of seizures associated 
with NeuroClear use, based on medical records, expert testimony, and internal PharmaCorp 
documents showing awareness of this risk.
3. Another product liability case where PharmaCorp was found liable for failing to warn 
about risk of liver damage from a different product, suggesting potential issues with 
adequate risk disclosure for NeuroClear as well.
```

最后，主 agent 把收到的信息综合为对用户问题的回答：

```
NeuroClear's Phase 2 trials had mixed impacts across different aspects of 
PharmaCorp's operations:

Clinical Results:
- Two Phase 2 trials (2019-2020 and 2021-2022) showed moderate success in treating
 Alzheimer's disease
- Success rates of 0.65 and 0.68 respectively
- Notable side effects included insomnia, anxiety, tremors, and weight loss

Stock Performance:
- The stock showed resilience during both trial periods
- Average stock price increased significantly (58%) between the first and second trial periods
- Interestingly, both trial completion dates saw slight negative price movements (-0.20% and -0.77%)

Patents and Legal Implications:
- Two significant patents were filed:
* Blood-brain barrier penetration enhancer system (2022)
* Targeted neurological receptor blocker (2021)
- However, several legal risks emerged:
* Product liability lawsuit regarding cognitive impairment
* Class action lawsuit concerning seizure risks
* Potential issues with risk disclosure based on previous cases

These results suggest that while NeuroClear showed promising clinical potential 
and led to valuable intellectual property, it also exposed PharmaCorp to significant 
legal risks that could impact future development and commercialization.
```

通过这个例子可以看到，多 agent 协作如何借助不同领域的专业知识，对复杂业务问题进行全面分析。主 agent 有效地编排子 agent 之间的交互，综合它们的洞察，给出一个综合性的答案，涵盖 NeuroClear 临床试验的研发、财务与法务方面及其对 PharmaCorp 的潜在影响。

## 清理

测试完该 agent 之后，请完成以下步骤清理 AWS 环境，避免产生不必要的费用：

- 删除 S3 存储桶：  在 Amazon S3 控制台中，清空存储桶 `structured-data-${AWS::AccountId}-${AWS::Region}` 与 `unstructured-data-${AWS::AccountId}-${AWS::Region}`。请删除其中的文件，确认两个存储桶都已清空。逐个选择文件，选择 **Delete**，然后输入存储桶名称进行确认。
- 删除 Lambda 函数：  在 Lambda 控制台中，选择 `CopyDataLambda` 函数。选择 **Delete** 并确认该操作。对 `CopyUnstructuredDataLambda` 函数重复这些步骤。
- 删除 Amazon Bedrock agent：  在 Amazon Bedrock 控制台的导航窗格中选择 **Agents**。选中该 agent，然后选择 **Delete**。
- 在 Bedrock 中删除 Amazon Bedrock 知识库：  在 Amazon Bedrock 控制台的导航窗格中，选择 **Builder tools ** 下的 **Knowledge bases**。选中该知识库并选择 **Delete**。
- 删除 EC2 实例：  在 Amazon EC2 控制台的导航窗格中选择 **Instances **。选中你创建的 EC2 实例，然后选择 **Delete**。

## 业务影响

使用 Amazon Bedrock Agents 实施这套多 agent 系统，可为制药公司带来显著收益。通过自动化跨领域的数据检索与分析，公司可以缩短研究时间，实现更快、由数据驱动的决策，尤其在领域专家分散于不同组织单元、直接交流有限的情况下更是如此。该系统能在几分钟内提供全面的跨职能洞察，从而改善风险缓解，因为通过关联分散的数据点，可以更早发现潜在的法律与财务问题。这种自动化还能让人力资源得到更有效的配置，把专家从例行数据分析中解放出来，专注于高价值任务。

我们的示例展示了多 agent 系统在制药研发中的能力，但这项技术的应用远不止单个用例。例如，生物科技公司可以让专家 agent 并行地从 Amazon Redshift 提取基因组信号、执行 Kaplan-Meier 生存分析并解读 CT 扫描，从而加速癌症生物标志物的发现。大型医疗系统可以自动汇总患者病历、检验结果与试验数据，以简化诊疗协调并标记紧急病例。旅行社可以编排端到端的行程，各类公司也可以管理个性化的客户沟通。关于潜在应用的更多信息，请参阅以下文章：

- [使用 Amazon Bedrock Agents 加速癌症生物标志物的分析与发现](https://aws.amazon.com/blogs/machine-learning/accelerate-analysis-and-discovery-of-cancer-biomarkers-with-amazon-bedrock-agents/)
- [agentic AI 系统如何解决当今医疗领域最紧迫的三大问题](https://aws.amazon.com/blogs/industries/how-agentic-ai-systems-can-solve-the-three-most-pressing-problems-in-healthcare-today/)
- [在 Amazon Bedrock 上通过多 agent 协作解锁复杂问题求解](https://aws.amazon.com/blogs/machine-learning/unlocking-complex-problem-solving-with-multi-agent-collaboration-on-amazon-bedrock/)
- [借助 Amazon Bedrock Agents 实现复杂的生成式 AI 应用](https://aws.amazon.com/blogs/machine-learning/enabling-complex-generative-ai-applications-with-amazon-bedrock-agents)

尽管多 agent 系统在这些多样应用中的潜力很吸引人，但理解实施此类系统时的实际考量也很重要。复杂的编排工作流会因多次模型调用而推高推理成本、增加端到端延迟、放大测试与维护需求，并在速率限制、重试以及 agent 之间或数据连接协议方面带来运维开销。不过，当前的技术水平正在快速进步。新一代更快、更便宜的模型有助于压低单次调用费用与延迟，而更强的模型可以用更少的轮次完成任务。可观测性工具为多 agent pipeline 提供端到端追踪与仪表盘。最后，像 Anthropic 的 [Model Context Protocol](https://www.anthropic.com/news/model-context-protocol) 这类协议正开始标准化 agent 访问数据的方式，为健壮的多 agent 生态铺平道路。

## 结论

本文中，我们探讨了使用 Amazon Bedrock Agents 并通过多 agent 协作实现的多 agent 生成式 AI 系统，如何应对跨多个业务领域的数据访问与分析挑战。通过一个虚构制药公司管理各部门数据的演示用例，我们展示了针对各领域定制的专用子 agent 如何简化信息检索与综合。每个子 agent 使用针对领域优化的模型，并安全地访问相关数据源，使组织能够产出跨职能洞察。

借助这种多 agent 架构，组织可以打破数据孤岛、加强协作，并在优化成本、延迟与安全性的同时实现高效、由数据驱动的决策。具备多 agent 协作的 Amazon Bedrock Agents 通过提供安全、可扩展的框架来促成这一架构，该框架负责管理 agent 之间的协作、通信与任务委派。可通过以下资源探索更多关于 Amazon Bedrock 多 agent 协作的演示与工作坊：

- [Amazon Bedrock 多 agent 协作能力简介（预览）](https://aws.amazon.com/blogs/aws/introducing-multi-agent-collaboration-capability-for-amazon-bedrock/)
- [Amazon Bedrock 多 agent 协作工作坊](https://github.com/aws-samples/bedrock-multi-agents-collaboration-workshop)
- [Amazon Bedrock 多 agent 协作 | Amazon Web Services](https://www.youtube.com/watch?v=tMqTy1HR974)

### 关于作者

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/06/justin-ossai-headshot-pic.jpg)Justin Ossai** 是常驻得克萨斯州达拉斯的 GenAI Labs 专家级解决方案架构师。他是一位极具热情的 IT 专业人士，拥有超过 15 年的技术经验。他为小型与企业级公司设计并实施过基于本地基础设施与云基础设施的方案。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2021/08/18/Michael-Hsieh.jpg)Michael Hsieh** 是首席 AI/ML 专家级解决方案架构师。他与 HCLS 客户合作，凭借其在医学影像方面的专长，用 AWS 技术推进他们的 ML 之旅。作为西雅图的新居民，他喜欢探索这座城市所提供的自然之美，例如徒步步道、在 SLU 划皮划艇的景色，以及 Shilshole Bay 的日落。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/06/shreya-img-.jpeg)Shreya Mohanty** 是 AWS 生成式 AI 创新中心的深度学习架构师，与各行业客户合作，设计并实施高影响力的 GenAI 驱动方案。她擅长把客户目标转化为能带来可衡量影响的切实成果。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/10/rhanspal.jpeg)Rachel Hanspal** 是 AWS 生成式 AI 创新中心的深度学习架构师，专长于端到端 GenAI 方案，重点在 frontend 架构与 LLM 集成。她擅长把复杂的业务需求转化为创新应用，并运用其在自然语言处理、自动化可视化与安全云架构方面的专长。
