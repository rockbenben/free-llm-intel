---
vendor: aws_bedrock
title: Build a conversational data assistant, Part 2 – Embedding generative business intelligence with Amazon Q in QuickSight
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-a-conversational-data-assistant-part-2-embedding-generative-business-intelligence-with-amazon-q-in-quicksight
date: 2025-07-11
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 3e86edc5481a
---

# 构建对话式数据助手，第 2 部分 – 使用 AWS Quick Sight 嵌入生成式商业智能

在本系列[第 1 部分](https://aws.amazon.com/blogs/machine-learning/build-a-conversational-data-assistant-part-1-text-to-sql-with-amazon-bedrock-agents/)中，我们探讨了 Amazon 的 Worldwide Returns & ReCommerce（WWRR）组织如何构建 Returns & ReCommerce Data Assist（RRDA）——一个使用 [Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/) 把自然语言问题转化为经过校验的 SQL 查询的生成式 AI 方案。这项能力虽然改善了技术用户的数据访问，但 WWRR 组织迈向真正数据民主化的旅程并未就此结束。

对 WWRR 内的许多利益相关方来说，把趋势与模式可视化远比处理原始数据更有价值。这些用户需要快速获得洞察以推动决策，而不必去解读 SQL 结果。虽然我们为常被跟踪的指标维护了预构建的 [AWS Quick Sight](https://aws.amazon.com/quicksight/) 仪表板，但业务用户经常需要长尾分析的支持——也就是能够针对标准报表未覆盖的具体问题、异常或区域差异做深入下钻。

为弥合这一差距，我们把 RRDA 方案从 SQL 生成扩展到包含可视化能力。本文深入介绍我们如何集成 [AWS Quick Sight](https://aws.amazon.com/quicksight/q/)，把"显示过去 6 个月美国退货商品数量"这类自然语言请求转化为有意义的数据可视化。我们展示了如何将 Amazon Bedrock Agents 与 AWS Quick Sight 结合，打造一个全面的数据助手，通过单一、直观的对话式界面同时交付 SQL 代码与可视化洞察——让数据访问在整个企业内实现民主化。

## 面向可视化分析的意图与领域分类

RRDA 系统的整体架构图包含两部分。在[第 1 部分](https://aws.amazon.com/blogs/machine-learning/build-a-conversational-data-assistant-part-1-text-to-sql-with-amazon-bedrock-agents/)中，我们聚焦于生成 SQL 的上层路径；在第 2 部分，我们探讨下层路径（下图中以红色标出），它通过 AWS Quick Sight 把用户直接连接到可视化洞察。

RRDA 架构概览，突出显示可视化路径（以红色标出）：该路径通过 Q topic 检索与选择处理 SHOW_METRIC 意图，交付嵌入的 AWS Quick Sight 可视化。

正如[第 1 部分](https://aws.amazon.com/blogs/machine-learning/build-a-conversational-data-assistant-part-1-text-to-sql-with-amazon-bedrock-agents/)所述，RRDA 让用户查询经过意图与领域分类系统，由这些系统决定每个请求应如何处理。当查询被分类为 `SHOW_METRIC` 时（由"show me"或"display"之类的短语，或关于可视化趋势的问题触发），系统会路由到我们的 AWS Quick Sight 集成路径，而不是生成 SQL。同时，我们的领域分类器会识别退货处理（Returns Processing）或促销（Promotions）等业务上下文，以收窄搜索范围。这种双重分类使得在保持业务上下文的同时，能够在接收代码与接收可视化洞察之间无缝切换用户体验。

例如，当用户问"显示上一季度退货商品数量的趋势"时，我们的系统会同时识别出可视化意图与退货处理业务领域，从而让后续的 LLM 在特定领域的 [AWS Quick Sight Q topic](https://docs.aws.amazon.com/quicksight/latest/user/quicksight-q-topics.html) 内搜索，而不是在整个目录中搜索。用户意图分类完成后，RRDA 会通知用户它正在 AWS Quick Sight 中查找相关指标，并启动下一节所述的、按领域过滤的 Q topic 选择流程。

## Q topic 的检索与选择

在用户意图被分类为 `SHOW_METRIC` 并识别出相关业务领域之后，RRDA 必须确定哪个具体的 Q topic 最能可视化所请求的信息。Q topic 是一种专门配置，让业务用户能够针对特定数据集提出自然语言问题。每个 Q topic 都包含可用指标、维度、时间段与同义词的元数据，因此 topic 选择是交付准确可视化洞察的关键一步。挑战在于智能地把用户请求映射到我们 50 多个专门配置目录中最合适的 Q topic。为了解决这个问题，RRDA 采用两步法：先用带[元数据过滤](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-knowledge-bases-now-supports-metadata-filtering-to-improve-retrieval-accuracy/)的向量搜索检索语义相关的 Q topic，以高效收窄候选范围；再用 [Amazon Bedrock](https://aws.amazon.com/bedrock/) [基础模型](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)（foundation model，FM）选出最佳匹配，评估每个候选能否处理用户查询中的特定指标与维度。

我们用 [Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/) 构建了专用的 Q topic 知识库来实现这种"先检索后选择"的做法。Amazon Bedrock Knowledge Bases 是一项全托管服务，可用于存储、搜索并检索组织专属信息，供大语言模型（LLM）使用。每个 Q topic 的元数据——包括名称、描述、可用指标、维度与示例问题——都会被转换为可搜索的文档，并使用 [Amazon Titan Text Embeddings V2](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html) 模型做嵌入。当用户提问时，RRDA 提取查询的核心意图与指定领域，然后针对我们的 Q topic 知识库执行向量相似度搜索。当识别出具体业务领域时，系统会把领域过滤器应用到[向量搜索配置](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_KnowledgeBaseVectorSearchConfiguration.html)上，确保只考虑相关的 Q topic。在这份检索结果列表上，一个轻量的 Amazon Bedrock 基础模型会分析各候选，结合指标可用性、维度支持与查询兼容性等因素，找出最能回答用户具体问题的最相关 Q topic。

下图展示了 Q topic 的检索与选择工作流。

Q topic 检索与选择工作流，展示 RRDA 如何通过向量搜索识别相关的可视化来源，然后使用 Amazon Bedrock 为 AWS Quick Sight 优化用户问题。

延续前面的例子，当用户问"显示上一季度退货商品数量的趋势"时，我们的系统首先把意图识别为 `SHOW_METRIC`，然后判断是否指定了退货处理或促销之类的领域。随后查询被传给我们的 Q topic 检索函数，该函数使用 [Retrieve API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_Retrieve.html) 搜索具有相关元数据的 Q topic。搜索结果返回一份排好序的 10 个候选 Q topic 列表，每个候选都包含其能力、支持的指标与可视化选项等信息。

这种检索机制解决了企业商业智能（BI）环境中的一个关键问题——发现哪份报表或哪个数据集包含能回答用户问题的信息。我们的系统不要求用户知道该查询我们 50 多个 Q topic 中的哪一个，而是基于对请求的语义理解自动识别相关的 Q topic。这种智能的 Q topic 选择营造了无摩擦的体验：业务用户可以专注于用自然语言提问，而 RRDA 在幕后处理寻找正确数据源的复杂性。

## 为获得最佳 Q topic 结果而改写问题

在 RRDA 识别出相关 Q topic 之后，我们还面临另一个关键挑战：弥合用户自然提问方式与 AWS Quick Sight 所期望的最佳格式之间的差距。缺少这个关键步骤，即便选对了 Q topic，用户也可能拿到次优的可视化结果。

### 问题改写的挑战

业务用户会用无数种方式表达自己的数据需求：

- 时间范围不精确："最近退回了多少商品？"
- 复杂多段问题："比较第一季度北美与欧洲的退货商品数量"
- 追问："写一个 SQL 查询，统计退货中心当前正在处理的退货商品数量"，在 RRDA 回复该 SQL 查询之后，再问"很好！现在把这个指标按今年展示给我"

虽然 AWS Quick Sight 旨在处理自然语言，但它是生成式问答系统，而不是对话式界面，在问题清晰且结构良好时表现最佳。恰当的措辞能确保 AWS Quick Sight 精确理解要可视化什么，从而显著提升回复质量。

### 使用 Amazon Bedrock Converse API 生成结构化问题

为解决这一挑战，我们使用 Amazon Bedrock [Converse API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html) 配合[结构化输出](https://docs.aws.amazon.com/nova/latest/userguide/prompting-structured-output.html)，实现了一套问题改写系统。这种做法确保把用户查询转换为适合 AWS Quick Sight 的最佳格式，同时保留关键的过滤条件与参数。

首先，我们定义 [Pydantic](https://docs.pydantic.dev/latest/concepts/models/) 数据模型来约束基础模型的输出结构：

```
class QTopicQuestionPair(BaseModel):
    """A question related to a Q topic."""
    topic_id: str = Field(..., description="The ID of the chosen Q topic")
    question: str = Field(..., description="The relevant question to ask this Q topic")

class ListOfQTopicQuestionPairs(BaseModel):
    """Response containing a list of questions corresponding to Q topics."""
    pairs: List[QTopicQuestionPair] = Field(
        default_factory=list, description="List of {Q topic Id, Question} pair objects."
    )
```

Converse API 的[工具使用能力](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use-inference-call.html)使得可以按这些已定义的数据模型来组织回复，从而让我们的代码可靠地解析它们。我们的系统把用户查询、对话历史以及检索到的 Q topic 元数据传给 Amazon Bedrock 基础模型，由它按经过验证的模式来构造问题：

- "为我展示 [特定指标] 在 [用户筛选条件] 下的数据"
- "从 [起始时间范围] 到 [结束时间范围]，[特定指标] 发生了怎样的变化？"
- "就 [时间范围] 比较 [指标 A] 与 [指标 B]"
- "[用户筛选条件] 下的 [特定指标] 是多少？"

在我们的各个业务领域中，这些格式在 AWS Quick Sight 中持续产出最佳结果，同时保留了关键的业务上下文——包括领域专用术语、时间过滤条件、维度约束与对比要素。例如，在查看了某个解决指数（resolution index）指标的 SQL 结果之后，用户可能会追问"现在把这个指标按过去 6 个月的趋势展示给我"，我们的系统会把它改写为"展示解决指数在过去 6 个月的趋势"，并且只选择与退货处理业务领域相关的 Amazon Q topic。

## 在聊天界面中嵌入 AWS Quick Sight 可视化

当用户在 RRDA 聊天界面中请求可视化数据时，系统会把 AWS Quick Sight 无缝嵌入对话之中。借助 Quick Sight 的嵌入功能，RRDA 会生成一个安全的嵌入 URL，直接在聊天窗口中渲染交互式可视化。用户无需离开对话流即可查看数据可视化。系统会自动选择合适的 Q topic 并改写用户问题以获得最佳结果，然后把这些信息传给嵌入的 Quick Sight 组件，由它生成并显示可视化。下面的截图展示了这种嵌入体验的样子（数据为示例数据）。关于所用嵌入能力的详细信息，请参阅[嵌入 AWS Quick Sight 生成式问答体验](https://docs.aws.amazon.com/quicksight/latest/user/embedding-gen-bi.html)。

示例 Q topic，展示 RRDA 聊天界面中的嵌入可视化能力，说明用户如何从自然语言问题无缝过渡到交互式数据可视化。

### 针对可视化请求直接推荐 Q topic

当用户带着 `SHOW_METRIC` 意图提出面向可视化的问题时（例如"展示过去 3 个月的退货商品数量"），RRDA 会在对话流中以可交互的建议卡片形式呈现相关的 Q topic。每条建议都包含 topic 名称（例如"Returns Processing – Sample Topic"），以及一个优化后的问题格式，用户可以选择它立即生成可视化。

![RRDA 界面截图：用户查询"Show me how many items were returned over the past 3 months?"，系统回复中推荐了相关的 AWS Quick Sight topic。回复建议了"Returns Processing - Sample Topic"，并给出一个具体问题链接"What is the return quantity for the past 3 months?"。回复底部显示大拇指向上与向下两个反馈按钮。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/24/ML-18493-rp-chat.png)

这些建议会带着一个清晰的标题出现："以下是与你最相关的问题与 AWS Quick Sight Q topic："，这样用户就能直接看出哪个数据源最能回答自己的问题。系统会把这些建议格式化为可点击的 prompt，一旦选中，就会自动触发上一节所展示的嵌入式 AWS Quick Sight 生成式问答弹窗。

### 对话中的上下文相关后续可视化

即使用户正在与[第 1 部分](https://aws.amazon.com/blogs/machine-learning/build-a-conversational-data-assistant-part-1-text-to-sql-with-amazon-bedrock-agents/)所述的 Amazon Bedrock agent 进行普通文本对话，RRDA 也会主动推荐相关的可视化。例如，当用户询问某个具体指标的信息时（"什么是解决指数指标？用 1-2 句话给我解释一下"），系统会给出文字解释（在下面的截图中被模糊处理），同时也会自动识别出可视化分析的机会。这些建议会以"从 AWS Quick Sight 获取相关洞察："开头，后面跟着像"过去 3 个月的解决指数是多少？"这样的相关问题。这在了解指标与将指标可视化之间架起了一座无缝的桥梁——用户可以从关于指标定义的简单查询出发，快速转向数据探索，而无需重新组织请求。这种上下文感知确保用户能发现自己原本不会想到去请求的有价值可视化，从而提升整体分析体验。

![RRDA 界面截图：查询"Define the RP resolution index metric in 1-2 sentences"，系统回复以"The Returns Processing Resolution Index is the percentage of returned items that are successfully processed within 7 business days, tracking how efficiently the returns fulfillment centers handle incoming returns."给出定义。界面还显示了计算公式，并推荐来自 Amazon Q in QuickSight 的相关洞察，底部有反馈按钮。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/24/ML-18493-rp-chat-2.png)

## 自动化 Q topic 元数据管理

RRDA 能够推荐相关可视化的背后，是一个包含 50 多个 Q topic 及其元数据的知识库。随着我们的分析版图不断扩大，为了让这个知识库保持最新，我们使用 [AWS Step Functions](https://aws.amazon.com/step-functions/) 实现了一套每日刷新的自动化元数据管理工作流，如下图所示。

使用 AWS Step Functions 的自动化 Q topic 元数据管理工作流，每日刷新，使知识库与最新的 Quick Sight Q topic 配置及已验证问题保持同步。

工作流从我们的 `FetchQTopicMetadata` [AWS Lambda](https://aws.amazon.com/lambda/) 函数开始，它连接 Quick Sight，收集每个 Q topic 的关键信息——跟踪哪些指标、用户可以应用哪些过滤器，以及很重要的，它过去成功回答过哪些问题。我们特地使用了 [DescribeTopic](https://docs.aws.amazon.com/quicksight/latest/APIReference/API_DescribeTopic.html) 与 [ListTopicReviewedAnswers](https://docs.aws.amazon.com/quicksight/latest/APIReference/API_ListTopicReviewedAnswers.html) 这两个 API，并把得到的元数据存入 [Amazon DynamoDB](https://aws.amazon.com/dynamodb/)——一个 NoSQL 键值数据库。这就形成了强大的反馈回路：当 Q topic 作者审阅并验证来自用户的问题时，这些已验证的问题会被自动并入我们的知识库，确保系统持续从用户交互与专家整理中学习。

工作流的下一步由 `BatchSummarizeQTopics` 函数使用 Amazon Bedrock 基础模型为收集到的元数据生成简明摘要。这一步是必要的，因为原始的 Q topic 配置常常[超出基础模型上下文窗口的 token 上限](https://aws.amazon.com/blogs/security/context-window-overflow-breaking-the-barrier/)。该函数把关键信息——指标、度量、维度与示例问题——抽取成紧凑的摘要，以便在向量检索与问题构造阶段被有效处理。

工作流的最后一步是 `SyncQTopicsKnowledgeBase` 函数，它把这份丰富的元数据转换为可向量搜索的文档，每个 Q topic 一份，并带有明确的业务领域标签，以支持按领域过滤的检索。该函数触发 Amazon Bedrock 的[知识库数据导入](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_StartIngestionJob.html)，重建向量嵌入（捕捉语义含义的数值表示），完成从 Q topic 配置到可搜索知识资产的全循环。这条 pipeline 确保 RRDA 始终能拿到最新、全面的 Q topic 元数据，而无需人工更新，在显著降低运营开销的同时提升了 Q topic 推荐的质量。

## 最佳实践

基于我们通过 AWS Quick Sight 为 RRDA 扩展可视化能力的经验，以下是在企业中实施生成式 BI 方案的一些最佳实践：

- **用智能建议预判分析需求** – 使用 AI 推测用户潜在期待的可视化，在关于指标或 SQL 的对话中自动浮现相关图表。这缓解了发现门槛，让用户获得他们最初可能没想到的洞察，无缝弥合理解数据与可视化趋势之间的差距。
- **连接异构 AI 系统时构建自动翻译层** – 使用 AI 自动把自然语言查询改写为各系统期望的结构化模式，而不是要求用户去学习精确的、系统专属的措辞。在确保每个系统以其偏好的格式接收输入的同时，保留用户的原始意图与上下文。
- **设计反馈回路** – 建立自动化系统，从用户交互中收集经过验证的内容，并回灌到知识库中。通过从 AWS Quick Sight 之类的工具中采集经人工审阅的问题，你的系统无需重新训练模型就能借助更好的检索数据持续改进。
- **先检索、后生成** – 先用带领域过滤的向量搜索收窄相关的可视化来源，再让生成式 AI 选择并构造最优问题，从而大幅提升回复质量并降低延迟。
- **在不同模态之间保持领域上下文** – 确保业务领域上下文贯穿整个用户旅程，无论用户得到的是 SQL 代码还是可视化，以保持指标定义与数据解读的一致性。

关于构建生产级生成式 AI 方案的全面指引，请参阅 [AWS Well-Architected Framework Generative AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lens.html)，其中涵盖安全性、可靠性、性能效率、成本优化、运营卓越与可持续性方面的最佳实践。

## 结语

在这个[两部分系列](https://aws.amazon.com/blogs/machine-learning/build-a-conversational-data-assistant-part-1-text-to-sql-with-amazon-bedrock-agents/)中，我们探讨了 Amazon 的 Worldwide Returns & ReCommerce 组织如何构建 RRDA——一个把自然语言转化为 SQL 查询与数据可视化的对话式数据助手。通过把负责编排与 SQL 生成的 Amazon Bedrock Agents 与负责可视化分析的 AWS Quick Sight 结合，我们的方案让数据访问在整个组织内实现民主化。领域感知的架构、智能的问题改写与自动化的元数据管理，缓解了业务问题与数据洞察之间的障碍，显著缩短了做出数据驱动决策所需的时间。随着我们基于用户反馈与基础模型的进步持续为 RRDA 增加新能力，我们仍专注于自己的使命：在自然语言问题与可执行的业务洞察之间架起无缝的桥梁。

### 关于作者

**![作者照片：Dheer Toprani](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/13/ML-18493-dtoprani-100x150.jpeg)Dheer Toprani** 是 Amazon Worldwide Returns and ReCommerce 数据服务团队的系统开发工程师。他专长于大语言模型、云基础设施与可扩展数据系统，专注于构建提升 Amazon 各业务运营的自动化与数据可访问性的智能方案。此前，他是 AWS 的数据与机器学习工程师，与客户紧密合作开发企业级数据基础设施，包括数据湖、分析仪表板与 ETL pipeline。

**![作者照片：Nicolas Alvarez](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/24/ML-18493-nickkalv-100x150.jpeg)Nicolas Alvarez** 是 Amazon Worldwide Returns and ReCommerce 数据服务团队的数据工程师，专注于构建并优化 reCommerce 数据系统。他在开发先进技术方案方面发挥关键作用，包括 Apache Airflow 实现以及团队门户的前端架构。他的工作在支撑 Amazon 逆向物流运营的数据驱动决策、提升产品生命周期末段管理效率方面至关重要。

**![作者照片：Lakshdeep Vatsa](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/24/ML-18493-lvatsa-100x150.jpeg)Lakshdeep Vatsa** 是 Amazon Worldwide Returns and ReCommerce 数据服务团队的高级数据工程师。他专长于设计、构建并优化大规模数据与报表方案。在 Amazon，他在开发可扩展数据 pipeline、提升数据质量、为逆向物流与 ReCommerce 运营提供可执行洞察方面发挥关键作用。他对改善用户的自助服务体验抱有浓厚兴趣，并持续寻找机会利用生成式 BI 能力解决复杂的客户难题。

**![作者照片：Karam Muppidi](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/24/ML-18493-karamup-100x138.jpeg)Karam Muppidi** 是 Amazon Retail 的高级工程经理，在 Worldwide Returns and ReCommerce 组织内领导数据工程、基础设施与分析团队。他专长于使用 LLM 与多 agent 架构改造数据分析，并推动组织采用 AI 工具。他在使用 AWS 与第三方工具开发企业级数据架构、分析服务与治理策略方面拥有丰富经验。在现任职位之前，Karam 为 Amazon 的 Fintech 与 Merchant Technologies 部门开发了 PB 级数据与合规方案。

**![作者照片：Sreeja Das](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/24/ML-18493-sreejdas-100x150.jpeg)Sreeja Das** 是 Amazon 退货与 ReCommerce 组织的首席工程师。在公司 10 多年的时间里，她深耕于电商与支付领域的高规模分布式系统、企业服务与生成式 AI 创新的交叉地带。在现任职位上，Sreeja 聚焦于系统与数据架构转型，以在退货与 ReCommerce 流程中实现更好的可追溯性与自助服务。此前，她主导了 Amazon 一些核心系统的架构与技术战略，包括每天服务数十万亿次客户请求的订单与退款处理系统以及计费系统。
