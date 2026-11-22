---
vendor: aws_bedrock
title: How Beekeeper by LumApps optimized user personalization with Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/how-beekeeper-optimized-user-personalization-with-amazon-bedrock
date: 2026-01-09
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 1f5c40086d2b
---

# Beekeeper by LumApps 如何借助 Amazon Bedrock 优化用户个性化

*本文由 Beekeeper 的 Mike Koźmiński 共同撰写。*

大语言模型（LLM）演进迅速，这让组织难以针对每个具体用例挑选最佳模型、在质量与成本之间优化 prompt、适应不断变化的模型能力，并为不同用户个性化响应。

选定“正确”的 LLM 与 prompt 并非一次性决策——它会随着模型、价格与需求的变化而漂移。system prompt 正变得越来越大（例如 Anthropic 的[ system prompt](https://docs.anthropic.com/en/release-notes/system-prompts)）也越来越复杂。许多中型企业并没有资源去快速评估并改进它们。为解决这一问题，Beekeeper 构建了一套由 [Amazon Bedrock](https://aws.amazon.com/bedrock/) 驱动的系统，持续评估 model+prompt 候选组合，在实时 leaderboard 上为它们排名，并把每个请求路由到该用例当前的最佳选择。

## Beekeeper：连接并赋能一线员工队伍

[Beekeeper by LumApps](https://www.beekeeper.io/) 提供一套专为一线员工队伍运营而设计的全面数字化工作场所系统。该公司提供移动优先的沟通与生产力解决方案，把非坐班员工彼此之间、以及与他们总部连接起来，帮助组织精简运营、提升员工参与度并高效管理任务。其系统具备与现有业务系统（人力资源、排班、薪酬）的健壮集成能力，同时面向酒店、制造、零售、医疗和运输等拥有一线员工队伍的行业。Beekeeper 的核心，是解决一线员工与其组织之间的传统脱节：通过提供易于获取的数字工具来增强沟通、运营效率和员工留存，而这些都通过一套基于云的 SaaS 系统交付，包含移动应用、管理仪表板和企业级安全特性。

## Beekeeper 的方案：一套动态评估系统

Beekeeper 用一套自动化系统解决了这一挑战：它持续测试不同的 model 与 prompt 组合，依据质量、成本和速度对选项排名，纳入用户反馈以实现响应个性化，并自动把请求路由到当前最佳选项。质量用小规模合成测试集打分，并在生产环境中用用户反馈（点赞/点踩与评论）验证。通过引入 prompt mutation，Beekeeper 构建了一个会随时间演化的有机系统。最终形成一套持续优化的配置，在质量、延迟与成本之间取得平衡，并在环境变化时自动适应。

## 真实用例：聊天摘要

Beekeeper 的 Frontline Success Platform 为各行业非坐班员工统一沟通。其 LLM 系统的一个实际应用是聊天摘要。用户回到班次时，可能会发现聊天中有许多未读消息——他们不必逐条读完，而是可以请求一份摘要。系统会生成一份简洁的概览，并附上针对该用户需求的行动事项。用户随后可以提供反馈，以改进后续摘要。这个看似简单的功能背后依赖复杂的技术：系统必须理解对话上下文、识别要点、辨认行动事项，并以简洁的方式呈现信息——同时还要适应用户偏好。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/08/ML-16803-image-1-1.jpeg)

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/08/ML-16803-image-2.jpeg)

## 方案概述

Beekeeper 的方案包含两个主要阶段：构建 baseline leaderboard，以及借助用户反馈进行个性化。

该系统使用多个 AWS 组件，包括用于调度的 [Amazon EventBridge](https://aws.amazon.com/eventbridge/)、用于编排的 [Amazon Elastic Kubernetes Service（EKS）](https://aws.amazon.com/eks/)、用于评估函数的 [AWS Lambda](https://aws.amazon.com/lambda/)、用于数据存储的 [Amazon Relational Database Service（RDS）](https://aws.amazon.com/rds/)，以及用于人工验证的 [Amazon Mechanical Turk](https://www.mturk.com/)。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/08/ML-16803-image-3.png)

工作流由一个 synthetic rank creator 开始，它建立 baseline 性能。调度器触发协调器，协调器获取测试数据并发送给评估器。这些评估器测试每个 model/prompt 组合并返回结果，其中一部分会被送去做人工验证。系统对有潜力的 prompt 进行变异以生成变体，再次评估这些变体，并保存表现最佳者。当用户反馈到达时，系统通过第二阶段将其纳入：协调器获取已排名的 model/prompt 组合，连同用户反馈一起发送给 mutator，mutator 返回个性化后的 prompt。漂移检测器确保这些个性化版本不会偏离质量标准太远，通过验证的 prompt 会为特定用户保存下来。

## 构建 baseline leaderboard

为启动优化之旅，Beekeeper 的工程师挑选了多种模型，并为它们提供由人工撰写的领域专用 prompt。技术团队使用 LLM 生成的示例测试这些 prompt，以确保它们没有错误。扎实的 baseline 在此至关重要。这一基础有助于他们在纳入真实用户反馈时改进方法。

在接下来的小节中，我们深入探讨他们的成功指标，这些指标指导他们对 prompt 的改进，并帮助打造最优的用户体验。

## baseline 的评估标准

model/prompt 组合所生成摘要的质量，通过定量与定性两类指标衡量，包括：

- **Compression ratio ** – 衡量摘要长度相对于原文的长度，奖励符合目标长度的结果，并惩罚过长。
- **Presence of action items ** – 确保与用户相关的行动事项被清晰识别。
- **Lack of hallucinations ** – 验证事实准确性与一致性。
- **Vector comparison ** – 评估与人工生成的完美结果之间的语义相似度。

在接下来的小节中，我们逐一走过每项评估标准及其实现方式。

### 压缩比

压缩比评估摘要文本相对于原文的长度，以及其是否符合目标长度（它奖励接近目标值的压缩比，并惩罚偏离目标长度的文本）。相应的得分介于 0 到 100 之间，由以下 Python 代码以程序化方式计算：

```
def calculate_compression_score(original_text, compressed_text):
    max_length = 650
    target_ratio = 1 / 5
    margin = 0.05
    max_penalty_points = 100 # Maximum penalty if the text is too long
    
    original_length = len(original_text)
    compressed_length = len(compressed_text)
    
    # Calculate penalty for exceeding maximum length
    excess_length = max(0, original_length - max_length)
    penalty = (excess_length / original_length) * max_penalty_points
    
    # Calculate the actual compression ratio
    actual_ratio = compressed_length / original_length
    lower_bound = target_ratio * (1 - margin)
    upper_bound = target_ratio * (1 + margin)
    
    # Calculate the base score based on the compression ratio
    if actual_ratio < lower_bound:
        base_score = 100 * (actual_ratio / lower_bound)
    elif actual_ratio > upper_bound:
        base_score = 100 * (upper_bound / actual_ratio)
    else:
        base_score = 100
    
    # Apply the penalty to the base score
    score = base_score - penalty
    
    # Ensure the score does not go below 0
    score = max(0, score)
    
    return round(score, 2)
```

### 与用户相关的行动事项是否存在

为检查摘要是否包含所有与用户相关的行动事项，Beekeeper 依靠与 ground truth 的对比。在 ground truth 对比中，期望的输出格式要求有一个标注为“Action items:”的小节，后接项目符号列表，并用正则表达式提取行动事项清单，如下方的 Python 代码：

```
import re

def extract_action_items(text):
    action_section = re.search(r'Action items:(.*?)(?=\n\n|\Z)', text, re.DOTALL)
 
    if action_section:
        action_content = action_section.group(1).strip() 
        action_items = re.findall(r'^\s*-\s*(.+)$', action_content, re.MULTILINE)
        return action_items
    else:
        return []
```

他们加入这一额外的提取步骤，是为了确保数据格式便于 LLM 处理。提取出的列表连同核对请求一起发送给 LLM，由它判断是否正确。每个被正确指认的行动事项记 +1 分，出现误报则记 -1 分。之后会对分数做归一化，以免因摘要中行动事项的多少而惩罚或奖励。

### 无幻觉

为评估幻觉，Beekeeper 采用两种方法：跨 LLM 评估与人工验证。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/08/ML-16803-image-4.png)

在跨 LLM 评估中，由 LLM A（例如 Mistral Large）生成的摘要，连同 prompt 与初始输入一起传给评估器组件。评估器把这段文本提交给 LLM B（例如 Anthropic 的 Claude），询问摘要中的事实是否与原始上下文相符。这类评估会使用不同家族的 LLM。借助 [Converse API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html)，Amazon Bedrock 让这件事变得格外简单——用户只需更改 model 标识符字符串，就能选用不同的 LLM。

另一点同样重要：Beekeeper 会在小部分评估上保留人工核验，以避免双重幻觉的情形。如果未检测到幻觉记 1 分，检测到则记 -1 分。在整个 pipeline 中，他们沿用同一条 7% 人工评估的启发式做法（细节将在本文稍后讨论）。

### 向量比较

作为额外的评估方法，对于有 ground truth 信息的数据会使用语义相似度。embedding 模型从 [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)（embedding 模型的多任务、多语言对比榜）中挑选，并考虑较大的向量维度，以最大化向量中存储的信息量。Beekeeper 以 Qwen3 作为 baseline，该模型提供 4096 的维度，并支持 16 位量化以实现快速计算。此外也直接使用来自 Amazon Bedrock 的其他 embedding 模型。在分别计算 ground truth 答案与给定 model/prompt 组合所生成答案的 embedding 向量之后，使用余弦相似度计算相似度，如下方的 Python 代码所示：

```
from sklearn.metrics.pairwise import cosine_similarity
cosine_similarity(synthetic_summary_embed, generated_summary_embed)
```

## 评估 baseline

每个 model/prompt 组合的评估 baseline，是通过收集一组固定的预定义查询的生成输出来完成的；这些查询都经过人工标注，带有包含“真实答案”的 ground truth 输出（在此即是来自内部与公开数据集的理想摘要）。如前所述，该集合由公开数据集以及更能代表客户领域的人工编写示例构成。分数依据先前所述的指标自动评估：压缩比、无幻觉、行动事项是否存在以及向量比较，从而构建出 leaderboard 的 baseline 版本。

## 人工评估

为进一步验证，Beekeeper 使用 Amazon Mechanical Turk 对由科学方法确定的评估样本进行人工复核。该样本量按 [Cochran 公式](https://www.myrelab.com/learn/sample-size)计算，以保证统计显著性。

Amazon Mechanical Turk 让企业得以借助人类智能来完成计算机无法有效完成的任务。这一众包市场把用户与全球的按需劳动力连接起来，以完成数据标注、内容审核和研究验证等微任务——在不牺牲质量、也不增加管理开销的前提下扩大运营规模。如前所述，Beekeeper 借助人工反馈来验证基于 LLM 的自动评分系统是否正常工作。根据此前的假设，他们知道应有百分之多少的响应会被判定为包含幻觉。如果人工验证检测到的比例与他们的估计相差超过两个百分点，就说明自动化流程未正常工作、需要修订。如今 Beekeeper 已建立 baseline，可以为客户提供最佳结果。通过持续更新模型，他们能以自动化的方式带来新的价值。每当工程师对新的 prompt 优化有了想法，就可以让 pipeline 用 baseline 结果把它与以往的版本做对比评估。Beekeeper 还能更进一步，把用户反馈嵌入进来，从而实现更可定制的结果。不过，他们并不希望用户反馈通过往反馈里注入 prompt 的方式完全改变模型行为。在下一节中，我们考察 Beekeeper pipeline 中把用户偏好嵌入响应、又不影响其他用户的那个有机部分。

## 用户反馈的评估

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/08/ML-16803-image-5.png)

现在 Beekeeper 已经用 ground truth 集合建立了 baseline，就可以开始纳入人工反馈。其运作原理与此前描述的幻觉检测流程相同。用户反馈会连同输入与 LLM 响应一起取出。他们按以下格式向 LLM 提问：

```
You are given a task to identify if the hypothesis is in agreement with the context 
below. You will only use the contents of the context and not rely on external knowledge.
Answer with yes/no."context": {{input}} "summary": {{output}} "hypothesis": {{ statement }} "agreement":
```

他们用这套方法来检查所给的反馈在 prompt-model 组合更新之后是否仍然适用。这作为纳入用户反馈的基准。此时他们已准备好开始对 prompt 进行变异。这样做是为了避免同一条反馈被多次应用。如果模型变更或变异已经解决了该问题，就没有必要再应用一次。

变异过程包括：在 prompt 变异之后重新评估用户生成的数据集，直到输出纳入了用户反馈；随后我们用 baseline 来理解差异，并在改动可能削弱模型原有表现时将其丢弃。

在 baseline 评估中选出的表现最好的四个 model/prompt 组合（针对已变异的 prompt）会进一步走一遍 prompt mutation 流程，以检查结果是否还有残余的改进空间。这在这样一个环境中至关重要：即使对 prompt 做很小的修改，在与用户反馈结合使用时也可能带来截然不同的结果。

初始 prompt 会被补充上 prompt 变异、收到的用户反馈、一种思维风格（一种具体的认知取向，例如“Make it creative”或“Think in steps”，用于引导 LLM 如何处理变异任务）、用户上下文，然后发送给 LLM 以产出变异后的 prompt。变异后的 prompt 被加入清单、接受评估，相应分数被并入 leaderboard。当存在用户反馈时，变异 prompt 也可以包含这些反馈。

生成的变异 prompt 示例如下：

```
“Add hints which would help LLM solve this problem:”

“Modify Instructions to be simpler:”

“Repeat that instruction in another way:”

“What additional instructions would you give someone to include this feedback {feedback}
 into that instructions:”
```

## 方案示例

baseline 评估流程从八对 prompt 与相应模型开始（[Amazon Nova](https://aws.amazon.com/nova/)、Anthropic Claude 4 Sonnet、Meta Llama 3 和 Mistral 8x7B）。Beekeeper 通常以四个基础 prompt 和两个模型起步。这些 prompt 会用于所有模型，但结果按 prompt-model 组合来考量。模型会随着 Amazon Bedrock 上出现更新版本而自动更新。

Beekeeper 从评估这八个已有组合开始：

- 每次评估需要为每个组合生成 20 份摘要（8 x 20 = 160）
- 每份摘要经过三项静态检查与两项 LLM 检查（160 x 2 = 320）

总共产生 480 次 LLM 调用。比较分数、生成 leaderboard，并选出两个 prompt-model 组合。这两个 prompt 会用用户反馈做变异，产出 10 个新 prompt，它们再次被评估，产生 600 次 LLM 调用（10 x 20 + 10 x 20 x 2 = 600）。

该过程可以运行 *n* 次以进行更具创造性的变异；Beekeeper 通常执行两轮。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/08/ML-16803-image-6.png)

总体而言，这次演练对 (8 + 10 + 10) x 2 个 model/prompt 组合进行了测试。整个流程平均需要约 8,352,000 个输入 token 和约 1,620,000 个输出 token，成本约 $48。新选出的 model/prompt 组合会以 1st: 50%、2nd: 30%、3rd: 20% 的比例用于生产。部署新的 model/prompt 组合之后，Beekeeper 从用户那里收集反馈。这些反馈被送入 mutator，以创建三个新 prompt。这些 prompt 会送去漂移检测，与 baseline 比较。合计产生四次 LLM 调用，成本约 4,800 个输入 token 和 500 个输出 token。

## 收益

Beekeeper 方案的核心收益在于其快速演进并适应用户需求的能力。借助这一方法，他们可以初步估计哪些 model/prompt 组合会成为每项任务的最优候选，同时控制成本与结果质量。通过把合成数据的优势与用户反馈结合，该方案甚至适合规模较小的工程团队。Beekeeper 不把重点放在通用 prompt 上，而是优先让 prompt 改进流程贴合每个租户的独特需求。这样做，他们能把 prompt 打磨得高度相关且易于使用。这一做法让用户可以发展出自己的风格，而用户提供反馈并看到其影响时，体验也随之提升。他们观察到的一个副作用是，某些人群偏好不同的沟通风格。通过把这些结果映射到客户交互上，他们希望呈现更贴合需求的体验。这确保某位用户给出的反馈不会影响到另一位用户。他们的初步结果显示，按租户汇总后，响应评分提升了 13–24%。总之，该方案带来若干显著收益：它通过自动化 LLM 与 prompt 的选择流程减少了人工劳动，缩短了反馈周期，支持创建面向用户或租户的改进，并具备以与以往模型相同的方式无缝集成新模型并评估其表现的能力。

## 结论

Beekeeper 用于动态选择 LLM 与 prompt 组合的自动化 leaderboard 方法及人工反馈闭环系统，解决了组织在应对快速演进的语言模型格局时所面临的关键挑战。通过持续评估并优化质量、规模、速度与成本，该方案帮助客户为其具体用例采用表现最佳的 model/prompt 组合。展望未来，Beekeeper 计划进一步完善并扩展该系统的能力，纳入更先进的 prompt 工程与评估技术。此外，团队正在探索让用户能够开发自己的定制 prompt，从而营造更个性化、更具参与感的体验。如果你的组织正在探索优化 LLM 选择与 prompt 工程的方法，不必从零开始。使用 Amazon Bedrock 提供模型访问、AWS Lambda 做轻量评估、Amazon EKS 做编排、Amazon Mechanical Turk 做人工验证等 AWS 服务，就可以构建一条能够自动评估、排名并演化你的 prompt 的 pipeline。与其手动更新 prompt 或重新为模型做基准测试，不如专注于构建一套由反馈驱动的系统，为用户持续改进结果。从少量模型与 prompt 开始，定义好你的评估指标，让系统随着新模型和新用例的出现而扩展。

### 关于作者

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/08/ML-16803-image-7-1.png)Mike (Michał) Koźmiński** 是 Beekeeper by LumApps 驻苏黎世的首席工程师（Principal Engineer），他为让 AI 成为产品一等公民构建基础。他拥有横跨初创企业与大型企业的 10 年以上经验，专注于把新技术转化为可靠的系统与真实的客户价值。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/08/ML-16803-image-8-1.png)Magdalena Gargas** 是一位解决方案架构师，热衷于技术并致力于解决客户挑战。在 AWS，她主要与软件公司合作，帮助它们在云上创新。

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/01/08/ML-16803-image-9-1.png)Luca Perrozzi** 是 Amazon Web Services（AWS）驻瑞士的解决方案架构师。他关注 AWS 的创新议题，尤其是人工智能领域。Luca 拥有粒子物理学博士学位，并有 15 年作为研究科学家与软件工程师的实战经验。

**![Simone Pomata](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/02/Simone-Pomata.jpg)Simone Pomata** 是 AWS 的首席解决方案架构师（Principal Solutions Architect）。他在科技行业热忱工作了 10 年以上。在 AWS，他每天帮助客户成功构建新技术。
