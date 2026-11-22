---
vendor: aws_bedrock
title: Improving HCLS AI reasoning with open-source agent skills
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/improving-hcls-ai-reasoning-with-open-source-agent-skills
date: 2026-09-16
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 6d90a92d9d9a
---

# 用开源 agent skill 提升 HCLS 的 AI 推理

基于基础模型（FM）构建的 AI agent 常常误用医疗与生命科学（HCLS）的决策框架，即便它们在训练数据和 system prompt 中都见过相应指南。让一个 agent 用 ACMG/AMP 标准对某个 TP53 错义变异进行分类：它会引用正确的框架，却误用证据类别、跳过人群频率阈值，或者凭空编造计算预测器评分。模型掌握事实，但缺少领域从业者在多年训练中内化的结构化推理流程。这一缺口会在变异解读、理赔审核、临床试验设计和影像分析中造成无声的失败：输出看起来正确，却套用了错误的标准，进而带来监管与患者安全方面的后果。

本文将分享一组 38 个开源 agent skill，覆盖 11 个 HCLS 领域，用于弥补上述方法论缺口。我们会走一遍安装流程，并演示如何在各类 agentic AI 服务中使用它们；也会分享评估结果，以展示在药物发现、医疗运营与医学影像工作流中可量化的改进。配备这些 skill 的 agent，在与未配备 skill 的同款 agent 进行一对一对比时，胜率为 70–86%，且这一结果随 agent harness 配置不同而变化。效应最强的是批判性思维（胜率 78–85%，d = 0.65–1.03）。我们还会展示如何针对你的具体用例定制、扩展并创建你自己的 agent skill。

## 解决方案概览

HCLS Agent Skills 集合中的 agent skill 是结构化的 markdown 文档（`SKILL.md`），它把领域决策流程编码成 AI agent 在推理时可通过渐进式披露（progressive disclosure）读取的格式。每个 skill 都遵循 [Agent Skills 开放标准](https://agentskills.io)，在 YAML frontmatter 中声明触发器、依赖与元数据；其后的内容包含决策框架、参数表、代码模式与校验标准。该集合涵盖 11 个 HCLS 领域的 38 个 skill，包括基因组学、药物发现、理赔运营与医学影像。按领域组织的完整清单见 [完整 skill 目录](https://github.com/awslabs/hcls-agent-skills#skill-catalog)。全部以 MIT-0 许可发布。

仓库中的 skill 分为 reasoning skill 与 pipeline skill 两类。reasoning skill 编码方法与决策框架，指导 agent 如何思考。例如 [genomic-variant-interpretation](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/skills/genomic-variant-interpretation/SKILL.md) skill 编码了完整的 ACMG/AMP 分类框架，包括证据类别、人群频率阈值与计算预测器的截断值。pipeline skill 则编码特定工具的命令、经验证的参数与代码模板，用于产出可直接运行的产物。[variant-calling](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/skills/variant-calling/SKILL.md) skill 提供 GATK4 HaplotypeCaller 命令，并附带正确的注释组、VQSR tranche 灵敏度目标以及 Mutect2 肿瘤–正常配对配置。

这种双重分类让 agent 既具备做出正确决策的判断力，也具备执行这些决策的技术精度。与检索增强生成（RAG）不同——RAG 从已索引文档中检索有限的片段来增强响应生成——skill 编码的是决策流程本身以及错误条件。skill 也不是微调：它们是结构化的 prompt，依据用户 query 中的触发模式在相应语境下被激活。

有三个特性让 skill 区别于其他领域专业化方案：skill 可审计、可移植，且易于维护。每一条决策标准都以 markdown 格式呈现、人类可读，而不隐藏于模型权重之中。一个 skill 无需针对各服务单独定制，即可在 20 多个服务中使用（[Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/)、[AWS Strands Agents SDK](https://strandsagents.com/)、[Kiro](https://kiro.dev/)、[AWS Quick Desktop](https://aws.amazon.com/quick/desktop/)、Claude Code、OpenAI Codex 等）。年度医疗政策变化或新的实验标准，只需编辑一个文本文件即可快速体现，而无需重新训练模型。

了解了 skill 包含什么，接下来我们把它装起来。

## 前置条件

要跟着本文的示例动手实践，你需要 AWS 受支持服务中的一种：[Kiro](https://kiro.dev/ide/) 或 [Kiro CLI](https://kiro.dev/cli/)（用于交互式使用 skill 与多 agent 编排）、可访问 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 基础模型的 [AWS Strands Agents SDK](https://strandsagents.com/)、[AgentCore harness](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness.html)（Amazon Bedrock AgentCore 的一项能力，需已有 agent 实现），或用于图形界面管理 skill 的 [Quick Desktop](https://aws.amazon.com/quick/desktop/)。你也可以使用自选的编码 agent harness，例如 Claude Code 或 OpenAI Codex。此外还需要 Python 3.10+ 与 uv，以及用于克隆仓库的 Git。

先克隆仓库：

```
git clone https://github.com/awslabs/hcls-agent-skills.git
cd hcls-agent-skills
```

如果只想安装 skill、不需要 agent 配置，可使用通用的 [skills CLI](https://github.com/vercel-labs/skills)：

```
npx skills add awslabs/hcls-agent-skills
```

对于 Kiro，`install.sh` 脚本会同时安装 skill 和一个已预先配置好这些 skill 的 agent。该 agent 会自动处理 skill 路由，因此你无需按名称逐个调用 skill。运行 `./install.sh --target kiro`，然后在 Kiro CLI 中用 `/agent hcls` 切换到该 agent。多 agent 模式下，运行 `./install.sh --target kiro --mode multiagent` 并使用 `/agent hcls-multiagent`。

对于 AWS Strands Agents SDK，可在 Python 代码中直接加载 skill：

```
from strands import Agent
from strands.skills import AgentSkills

agent = Agent(
    model=model_id,
    skills=AgentSkills(skills="./skills/"),
)
```

对于 [AgentCore](https://aws.amazon.com/bedrock/agentcore/)，请参照 [Skills](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-skills.html) 将 agent skill 添加到由 AgentCore 托管的 agent 中。AgentCore 提供托管运行、自动扩缩容、安全边界与可观测性能力。

对于 AWS Quick Desktop，运行 `./install.sh --target quick-desktop` 可查看在图形界面中添加 skill 的完整说明。你也可以按照 AWS Quick 文档中 [Skills](https://docs.aws.amazon.com/quick/latest/userguide/skills-desktop.html) 的说明操作。

## 解决方案实践

skill 装好之后，我们演示三种部署模式：Quick Desktop 中最简单的单 agent 方案；Kiro CLI 中应对上下文工程挑战的多 agent 编排；以及在 Amazon Bedrock AgentCore 上用 Strands SDK 的生产部署。随后我们会给出三个示例用例，展示 skill 在真实 HCLS 工作流中带来的可量化差异。

### 在 Quick Desktop 中实际使用 agent skill

skill 安装完成后，Quick Desktop 的 agent 无需额外配置就获得了结构化的 HCLS 领域推理能力。当你提出一个领域问题时，agent 会依据 query 中的触发模式自动激活相关 skill。例如，提问「把 E11.9 而不是 E11.42 编码，会对 RAF 产生什么影响？」，会触发 `risk-adjustment` skill，agent 会给出具体的 HCC 映射、层级解析以及量化的 RAF 变化量，而不是笼统地建议「查看文档」。skill 是按需选择性激活的：针对该响应只会触发相关的那一个 skill，从而有助于让输出保持聚焦与准确。下面的视频展示了在 AWS Quick Desktop 中为该问题动态加载 skill 的过程。

在 AWS Quick Desktop 对话中动态加载 risk-adjustment skill，以回答一个 RAF 编码问题

### Kiro 的多 agent 架构

把全部 38 个 skill 加载进单个 agent 上下文大约消耗 80K token。对大上下文模型来说这可行，但会带来上下文工程上的挑战：agent 在每次 query 时都必须从 38 个可用 skill 中挑出正确的子集，而不相关的 skill 内容会争夺注意力。另一种办法是显式调用 skill（例如 `/risk-adjustment`），但这要求你在提问之前就知道该调用哪个 skill——而这正是 skill 本来要弥合的专业知识缺口。

Kiro CLI 的多 agent 架构同时解决了这两个问题。一个轻量的协调器 agent（不加载任何 skill）把 query 路由给八个领域专家，每个专家只加载与其相关的 skill（每个专家约 15K token）。协调器负责意图分类，专家负责领域推理。这种专业化分工按下表定义。

![Kiro CLI 多 agent 架构中八个领域专家 agent 以及分配给各自的 skill 的表格](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/09/11/ML-21213-2.png)

Kiro CLI 多 agent 架构中八个领域专家 agent 以及分配给各自的 skill 的表格

多 agent 配置定义在 JSON agent 文件中。路由逻辑请参阅 [协调器 agent 配置](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/agents/multiagent/kiro/hcls-multiagent.json)，领域 skill 如何挂载到专家 agent 的示例请参阅[专家 agent 配置](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/agents/multiagent/kiro/hcls-drug-discovery.json)。下面的视频展示了在 Kiro CLI 中于代码库内工作时，多 agent 路由与动态 skill 激活如何回答一个复杂的药物重定位问题。

Kiro CLI 在代码库中使用多 agent 路由与动态 skill 激活回答一个药物重定位问题

### Strands SDK 集成

AWS Strands Agents SDK 提供原生 skill 加载能力，用于构建自定义 HCLS agent：

```
from strands import Agent
from strands.skills import AgentSkills
from strands.multiagent import MultiAgentOrchestrator

# Define domain specialists with their skill sets
genomics_agent = Agent(
    name="hcls-genomics",
    model=model_id,
    skills=AgentSkills(skills="./skills/genomics/"),
)

imaging_agent = Agent(
    name="hcls-imaging",
    model=model_id,
    skills=AgentSkills(skills="./skills/imaging/"),
)

# Coordinator routes to specialists
coordinator = MultiAgentOrchestrator(
    agents=[genomics_agent, imaging_agent, ...],
    model=model_id,
)

response = coordinator("Classify NM_000546.6:c.743G>A in TP53 using ACMG criteria")
```

### 部署到 Amazon Bedrock AgentCore

当配备 skill 的 agent 在本地跑通之后，就可以把它推向生产。Amazon Bedrock AgentCore 提供了另一条将 skill 注入托管 agent 的路径：除了把它们嵌入 Strands agent 代码，你还可以在环境层面配置 skill，使其对该 harness 中运行的 agent 可用。AgentCore harness 无需你自行管理基础设施，即可提供托管运行、自动扩缩容、安全边界与可观测性能力。请参照 AgentCore 文档中的 [Skills](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-skills.html)。

部署讲完了，接下来看看配备 skill 的 agent 在实践中产出什么。以下示例用例取自我们的评估 prompt 集。

### 用例 1：在药物发现中评估罕见纤维化疾病的药物重定位候选

某生物技术公司的一个团队正在研究特发性肺纤维化（IPF）的药物重定位，希望评估那些通过受体激酶 TGFBR1（ALK5）调节 TGF-β1 信号通路的已获批药物。在实践中，研究者需要查询药物–基因相互作用数据库、按证据强度对候选药物排序、评估作用机制与 IPF 病理生理的重叠程度，并在既有安全性数据的基础上判断可转化性。但研究者往往会随手给 agent 一个模糊的 prompt：「我正在研究把 TGFBR1 作为 IPF 的治疗靶点。有没有已获批药物值得重定位？最强的候选是哪个，临床转化的现实性如何？」

在添加 skill 之前，agent 给出的是一份泛泛的文献综述，罗列已知的 TGFBR1 抑制剂，却没有结构化的排序标准、证据层级或可转化性评估框架。为 agent 配备 skill 之后，它会触发 [drug-repurposing](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/skills/drug-repurposing/SKILL.md) 与 [translational-research](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/skills/translational-research/SKILL.md) skill，并完成以下工作：

- agent 套用 DGIdb 查询框架，优先考虑相互作用类型（抑制剂 > 调节剂 > 结合剂）与来源数据库（ChEMBL、DrugBank），而非置信度更低的来源。
- 它用结构化的证据层级对候选药物排序：直接的靶点结合证据优先于通路层面证据，通路层面证据又优先于表型关联，并把既有适应症相关性作为调节项。
- 它通过把 TGFBR1 抑制映射到 IPF 的关键病理过程来评估作用机制重叠：成纤维细胞向肌成纤维细胞转化、上皮–间充质转化，以及细胞外基质沉积。
- 它使用 T0→T1 标准评估临床可转化性，考察原适应症的既有安全性数据、治疗窗的兼容性，以及现有临床前纤维化模型与人类疾病的吻合度。

这条 skill 链把表层回答转变为具备监管意识的结构化评估，并给出量化的证据排序。

### 用例 2：在医疗理赔运营中构建 CMS-HCC 风险调整 pipeline

一个拥有 12,000 名成员的 Medicare Advantage 计划，需要用 CMS-HCC Model V28 系数从 ICD-10 诊断理赔数据中计算风险调整因子（RAF）评分。该 pipeline 必须应用 `ICD-10-to-HCC` 对照表、正确解析疾病层级，并在纳入人口学调整后算出最终的成员级风险评分。而一位初级分析师可能这样给 agent 下 prompt：「我们是一个有 12,000 名成员的 Medicare Advantage 计划。PostgreSQL 数据库里有 ICD-10 诊断理赔数据（member_diagnoses 与 member_demographics 两张表）。给我搭一个 pipeline，计算当前支付年度的成员级 RAF 评分。」

在添加 skill 之前，agent 产出的 pipeline 看似合理但并不完整：常常完全漏掉层级解析、使用过时的 V24 系数，或者在求和之后才应用层级（这会抬高评分）。为 agent 配备 skill 之后，它会触发 [risk-adjustment](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/skills/risk-adjustment/SKILL.md) 与 [claims-billing-rules](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/skills/claims-billing-rules/SKILL.md) skill，并完成以下工作：

- agent 生成正确的 SQL，把诊断编码与 `ICD-10-to-HCC` 对照表连接，并在测量年度内去重，确保每个 HCC 对每位成员只计数一次。
- 它正确实现 V28 的层级解析：HCC 18（伴慢性并发症的糖尿病）取代 HCC 19（不伴并发症的糖尿病），HCC 326（CKD 5 期）取代 HCC 327（CKD 4 期），有助于避免在多个特异性层次上重复计数。
- 它应用正确的人口学分群，在汇总 HCC 系数之前把成员划入社区、机构或双重资格（dual-eligible）人群，并做年龄/性别调整。
- 它会主动说明：跳过层级解析会在多个特异性层次上重复计算病情，系统性地抬高 RAF 评分，并在 CMS RADV 审核下形成审计风险。

该 skill 支持产出经得起审计的 RAF 评分，而不是会触发 CMS RADV 审计发现问题的虚高估算。

### 用例 3：医学影像研究中用于基于体素形态学分析的 T1 加权 MRI 预处理

一项包含 45 名健康成人的神经影像研究，需要一个标准的 T1w 预处理 pipeline 来支撑基于体素的形态学分析（VBM）。原始 DICOM 数据已转换为 NIfTI。该 pipeline 必须按正确顺序、并以适合健康成人脑的参数，在 FSL/ANTs 混合环境中完成重新定向、偏置场校正、颅骨剥离，以及配准到 MNI152 空间。研究者可能这样给 agent 下 prompt：「我有 45 例健康成人的 T1w 扫描，需要为一项 VBM 分析做预处理。用 FSL 和 ANTs 搭一个 pipeline。」

在添加 skill 之前，agent 会给出一个看似合理的 pipeline，但可能把偏置场校正排到颅骨剥离之后（这会让脑掩膜产生偏差）、使用不合适的阈值，或者遗漏失效模式检测策略。为 agent 配备 skill 之后，它会触发 [radiology-preprocessing](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/skills/radiology-preprocessing/SKILL.md) 与 [imaging-study-design](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/skills/imaging-study-design/SKILL.md) skill，并完成以下工作：

- agent 给出正确的处理顺序并说明理由：先重新定向到标准空间，再在颅骨剥离之前做偏置场校正，然后用针对健康成人调优的参数做脑提取，最后配准到 MNI152 模板。
- 它解释了这个关键的顺序依赖关系：如果事先没有做偏置场校正，脑边界处的强度不均匀会使颅骨剥离算法去除过多或过少的组织，在颞叶与额叶区域尤为明显。
- 它提供一份完整的 bash 脚本，包含各阶段的错误检查，以及用于目视检查中间结果的质量控制输出。
- 它记录每一步的失效模式：方向元数据不正确、表面线圈附近残留信号阴影、提取阈值过宽时混入颈部组织，以及老年受试者脑室边界处的配准失败。

该 skill 抓住了会给 VBM 分析引入系统性偏差的那个顺序依赖关系。

这些用例说明了 HCLS skill 如何从质上重塑 agent 行为、产出更贴合领域的回答；但对研究者和开发者来说，总会有一个问题：到底好了多少。

### 评估结果

我们做了一次成对评估，用两套 harness 配置衡量 skill 在 410 条领域 prompt（380 条单一 skill、30 条跨 skill）上的影响。其中一套 agent harness 是 Kiro CLI，其中使用 Auto 模型，由 Kiro 为任务挑选最合适的模型；Kiro 中的 agent 可以使用 thinking 工具与文件读取操作。另一套配置是用 AWS Strands Agents SDK 构建的 agent，调用形式为 `Agent(model=BedrockModel(...), callback_handler=None)`，模型显式固定为 Claude Sonnet 4.6；其 skills 条件还会额外加载 `AgentSkills(skills="./skills/")` 插件。两种条件都对称地提供了 think 工具。具体配置见 [eval/execute.py](https://github.com/awslabs/hcls-agent-skills/blob/bb26f0b2d767ce21bd711d069fc762bf2c212c4b/eval/execute.py#L103)。在两种配置中，都比较了两个条件：一个是不具备任何 skill 的基线 agent，另一个是通过渐进式加载获得全部 38 个 skill 的 skilled agent。

我们让大语言模型（LLM）裁判从五个评分维度衡量 skill 对 agent 回答的影响。科学准确性（Scientific accuracy）评估事实、机制、引用与领域知识的正确性。连贯性（Coherence）评估回答是否遵循逻辑结构，具有清晰的推理链与内在一致性。相关性（Relevance）衡量 agent 在切题的前提下、以合适深度覆盖 prompt 各部分的程度。批判性思维（Critical thinking）考察 agent 挑战假设、识别局限并考虑替代方案的能力，而不是只给出一份未经审视的回答。可操作性（Actionability）评估 agent 提供具体后续步骤、明确参数与可运行命令的能力——从业者可以立刻据此行动。我们使用 Amazon Bedrock 上的 Claude Opus 4.7 作为裁判。完整评分 prompt 见 [eval/judge.py](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/eval/judge.py)。

裁判按 0–100 的刻度为每个维度打分。然而 LLM 裁判存在分数压缩（score compression）现象：分数会聚集在某个区间内，使得原始差值（例如 +1.5）难以解读。因此我们报告两个主要指标。第一是胜率（win rate，WR），即 skills 条件下的得分高于基线的 prompt 所占百分比；这一指标直观，且对刻度压缩具有稳健性。第二是 Cohen's d 效应量（简称 d），用于衡量两组均值之间的标准化差异，计算方式为均值差除以合并标准差，用来反映改进相对于自然波动有多大。Cohen's d 的通用解释为：0.2（小）、0.5（中）、0.8（大）。

总体来看，在两套 agent harness 配置下，skill 在一对一对比中的胜率为 69.5–85.9%。两种配置下 skill 都提升了批判性思维、可操作性与科学准确性。最强的信号出现在批判性思维上，这印证了 skill 的主要贡献是方法论层面的：教会 agent 该套用哪些框架、该挑战哪些假设、该标注哪些局限，而不是补充基础模型可能已经掌握的事实内容。下表汇总了高层级结果。

| **指标** | **Kiro CLI** | **Strands Agent** |
| --- | --- | --- |
| 评估的 prompt 数 | 410 | 410 |
| skills 总体 WR（d） | 69.5% (0.39) | 85.9% (0.97) |
| 批判性思维 WR（d） | 78.0% (0.65) | 85.1% (1.03) |
| 科学准确性 WR（d） | 69.3% (0.34) | 86.2% (0.85) |
| 可操作性 WR（d） | 68.0% (0.37) | 77.3% (0.56) |
| 基线–收益相关性（r） | -0.59 | -0.61 |
| 方差最大降幅 | -61.9% | -52.1% |

#### 按基线强弱看效果

有强有力的证据表明：基础 agent 表现最吃力时，agent skill 的帮助最大。基线回答质量与 skill 收益之间的 Pearson 相关系数在 Kiro CLI 中为 −0.59，在 Strands agent 中为 −0.61。我们依据基线 agent 的总体得分把 prompt 分为弱、中、强三档。多数 prompt 落在中档，skill 在此带来明显收益；落在强档（模型本身表现已经很好）的 prompt，从 agent skill 获得的提升有限。弱档代表基础 agent 吃力的情形，这些情形横跨多个领域（临床数据、医疗运营、基因组学），通常涉及多步骤的监管流程，或模型只能近似处理、无法精确套用的细分方法论。

不过，强档的结论并非绝对。跨领域 reasoning skill 即使在基线高达 90.2 的强档中也能取得 80% 的胜率，这说明设计良好的方法论框架只要教会了模型原本不会自行套用的决策流程，就能在整个质量谱系上带来价值。

按基线强弱列出的基线 agent 与 skilled agent 总体得分见下表。

在 Kiro CLI 中

| **基线档位** | **N** | **基线（mean±sd）** | **skills（mean±sd）** | **差值** | **胜率** |
| --- | --- | --- | --- | --- | --- |
| 弱（<80） | 15 | 75.8±4.0 | 84.4±6.3 | +8.7 | **87%** |
| 中（80-90） | 227 | 86.8±2.5 | 89.1±3.3 | +2.3 | 79% |
| 强（>90） | 168 | 91.3±1.0 | 91.0±2.5 | -0.3 | 55% |

在 Strands agent 中

| **基线档位** | **N** | **基线（mean±sd）** | **skills（mean±sd）** | **差值** | **胜率** |
| --- | --- | --- | --- | --- | --- |
| 弱（<80） | 46 | 77.0±2.6 | 84.9±3.5 | +7.9 | **96%** |
| 中（80-90） | 325 | 85.8±2.6 | 89.5±3.3 | +3.7 | 89% |
| 强（>90） | 39 | 91.0±0.7 | 91.1±2.0 | +0.0 | 54% |

#### 方差缩减

skill 还降低了某一领域内所有示例 prompt 的回答分数标准差。例如在 Kiro CLI 中加载 skill 后，裁判对临床数据类回答评分的标准差从 6.8 降到 3.3，降幅 51%。这意味着 skill 让输出更加一致，遵循 skill 中编码的知识与框架。在一致性同平均质量一样重要的受监管 HCLS 工作流中，这种方差缩减是有意义的收益。

完整的评估方法、prompt 与原始结果见[评估技术报告](https://github.com/awslabs/hcls-agent-skills/blob/main/eval/TECHNICAL_REPORT.md)。

### 扩展 skill 与构建新的 skill

这些结果针对仓库中随附的 38 个 skill。你团队的工作流可能需要不同的阈值、额外的协议，或完全新的领域覆盖。仓库提供三份 skill 定制指南：

- [CUSTOMIZING.md](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/CUSTOMIZING.md) 讲解修改、扩展与从零创建 skill 的实用流程，包括向既有 skill 添加组织特定规则（LCD 编码、处方集阶梯治疗、内部协议）。
- [SKILL_DESIGN_GUIDE.md](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/SKILL_DESIGN_GUIDE.md) 记录编写高效 skill 的循证模式：决策树、阈值表、常见陷阱清单、响应格式小节，以及与高评估胜率相关的结构性特征。
- [QUALITY_CHECKLIST.md](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/QUALITY_CHECKLIST.md) 提供合并前质量检查清单，覆盖 frontmatter、结构、内容质量与测试要求。

要为你的组织定制 skill，先复制相关的 `SKILL.md`，然后修改决策阈值、添加组织特定协议，或删除无关小节。用设计指南来组织新内容以获得最佳效果：例如 reasoning skill 受益于决策树与编号步骤流程，而 pipeline skill 则以参数表与特定版本的注意事项提供很强的价值。

要测试你的改动，先生成反映你团队实际工作流的评估 prompt，然后运行评估框架：

```
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -e ".[dev]"
# Generate 30 evaluation prompts for each of the skills
python eval/generate_prompts.py --count 30
# Run pairwise evaluation against your modified skills
python -m eval.run --skills ./my-custom-skills/ --parallel 2
python eval/build_review.py
open eval/results/review.html
```

下面的视频展示了 review.html 评估看板，其中包含每次评估的评分、领域分布、prompt 与响应。

review.html 评估看板，展示每次评估的评分、领域分布、prompt 与响应

该评估会产出成对比较，显示你修改后的 skill 是否相对基线改善了回答，并给出与前述结果相同的逐维度细分结果。欢迎按照[贡献指南](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/CONTRIBUTING.md)把新的领域 skill 回馈到开源集合中。

## 清理

skill 是本地文件，不会创建 AWS 资源。本文的示例无需拆除清理。如果你把 Strands agent 部署到了 Amazon Bedrock AgentCore harness，请按[清理步骤](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-cli.html#agentcore-cli-cleanup)删除已部署的 agent 资源。

## 结论

agent skill 为你的 HCLS agent 提供结构化的领域方法论。agent skill 中的决策框架、监管阈值与常见错误清单，可以把近似回答变为精确回答。借助覆盖基因组学、药物发现、理赔运营、医学影像等领域的 38 个 skill，你可以在 Quick Desktop、Kiro，或运行在 Amazon Bedrock AgentCore 上、基于 Strands SDK 的架构中部署领域专家 agent。

可量化的效果本身就说明了问题。我们的评估显示，skilled agent 的胜率为 70–86%，其中批判性思维上的提升最强（d = 0.65），而在缺少引导的 agent 最容易失败的最难 query 上提升幅度最大。skill 是可审计的文本文件，你可以按所在组织的协议进行定制，并用随附的评估框架加以测试。

要开始使用：

- 克隆[仓库](https://github.com/awslabs/hcls-agent-skills)
- 通过 [Kiro](https://kiro.dev/docs/#get-started) 或 [AWS Quick Desktop](https://docs.aws.amazon.com/quick/latest/userguide/amazon-quick-desktop.html) 交互式使用 skill
- 使用 [AWS Strands Agents SDK](https://strandsagents.com/docs/user-guide/quickstart/overview/) 构建自定义 agent
- 使用 [Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-get-started-cli.html) 将 agent 部署到生产
- 在 [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html) 上探索基础模型

## 关于作者
