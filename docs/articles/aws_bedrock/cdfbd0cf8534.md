---
vendor: aws_bedrock
title: How an AWS team detects dashboard content failures at scale using Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/how-an-aws-team-detects-dashboard-content-failures-at-scale-using-amazon-bedrock
date: 2026-09-02
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: d6d32c6a24de
---

# AWS 团队如何借助 Amazon Bedrock 大规模检测看板内容故障

设想一个任何大规模运行商业智能（BI）的组织都熟悉的场景：用户在重要会议开始前几分钟打开看板，却发现某个图表是空白的。所有基础设施监控都报告健康：服务器在线、API 有响应、数据 pipeline 按时完成。但屏幕上的内容已经坏了，而没有任何监控系统把它标记出来。这类故障天生是无声的：它只存在于用户所看到的内容里，因此对基础设施监控不可见，只能依赖用户抽时间提交报告。我们后来的埋点数据显示，这种情况发生的比例不到 1%。

看板元素（表格、图表与可视化组件）可能显示空白、过期或错误的数据。常见原因包括上游 pipeline 故障、权限变更，以及短暂的基础设施问题。即便每个图表都能正确渲染，数字本身也可能是错的。当组织把看板数据输入到为业务领导者生成叙述的 AI 系统时，这一风险会进一步放大。

本文介绍我们如何构建一套最后一公里（last-mile）的自动化内容校验方案。它同时扫描托管在 AWS Insights 应用（由 [Amazon Quick](https://aws.amazon.com/quick/) 提供支持）上的数百个看板，以检测缺失或错误的元素。借助该方案，BI 与分析团队可以在用户看到问题之前就完成修复。该方案主动监控看板，并使用 [Amazon Bedrock](https://aws.amazon.com/bedrock/?nc2=type_a) 上的大语言模型（LLM）对其进行视觉分析，在检测到健康问题时实时提醒构建者。这让平均检测时间从最长 72 小时缩短到 1 小时以内。

你将了解：

- 内容层监控的缺口，以及为什么仅靠用户报告无法可靠地暴露内容故障。
- 一套构建在 AWS 托管服务之上的五阶段无服务器校验架构。
- 两套并行的 AI 校验机制，一套针对视觉完整性、一套针对数值一致性，二者基于同一设计原则构建。
- 生产工程经验：针对误报进行设计，以及让 LLM 远离算术运算。

## 内容层校验为何重要

传统的基础设施监控确认服务在运行、API 有响应。但基础设施健康并不保证用户看到的内容是正确的。我们发现这一缺口表现为两个不同的问题：

- **无声的视觉故障。** 即使所有上游服务都报告正常，看板区块仍可能显示空白、过期数据或错误状态。在自动化监控上线之后，30 天的数据量化了这一缺口：共检测到 802 次内容故障（行级数据权限错误、过滤器跳过记录、渲染问题等），其中不到 1% 有对应的用户报告。没有自动化检测，这类降级对被动响应式的支持渠道而言实际上是不可见的。
- **未被察觉的数值不一致。** 图表可以完美渲染，却显示错误的数字。过滤器配置错误、聚合逻辑错误与刷新时序问题会产生只在渲染输出中才显现的差异，数据层校验永远发现不了它们。当 AI 叙述系统消费这些数据时，风险会上升，因为数值错误会直接传导进那些支撑高管决策的洞察之中。

## 现有监控工具的定位

值得一提的是，[Amazon CloudWatch Synthetics](https://aws.amazon.com/cloudwatch/?refid=5d83343f-40c5-4167-8ec4-5b70bac566f7) 已经负责端点监控（页面能否加载、链接能否解析、延迟是否稳定），数据层校验也能在上游捕获 pipeline 故障。缺口在 BI 呈现层：在那里，过滤器配置错误、聚合逻辑错误或刷新时序问题会让错误的数字出现在屏幕上，而所有上游检查都已通过。本方案补充的正是这最后一公里的语义判断。它是对基础设施监控与数据质量校验的补充，而不替代其中任何一项。

## 工作原理：使用体验

从看板负责人的角度看，只需几项配置即可定义指标与看板的比较范围。当自己所负责的区块被检测到视觉内容故障时，他们会收到一条 Slack 通知。通知包含受影响的区块名称、展示故障的截图、AI 置信度分数，以及指向监控看板、便于进一步排查的直接链接。

对于数值校验，每次每周数据刷新都会触发一轮校验周期，产出一份人类可读的报告。只有被标记的不一致需要审核者关注，经确认的数据问题会升级给所属团队。

## 解决方案概览

为应对这些挑战，我们设计了一套由 AI 驱动的最后一公里自动化内容校验方案。下图从高层展示了该方案的工作流。

![高层方案概览：定时抓取经 AI 分析流向看板负责人告警](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/31/ML-21432-1.png)

图 1：最后一公里自动化内容校验方案概览

这幅高层视图勾勒了从定时抓取、经 AI 分析到负责人告警的流程。下图把它展开为端到端处理 pipeline，其中包括在原有视觉校验结构上新增的数值校验组件。

![端到端 pipeline 图：五个处理阶段，第 3 阶段包含两套并行校验机制](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/31/ML-21432-2.png)

图 2：端到端处理 pipeline，展示五个阶段，以及第 3 阶段中的两套并行校验机制

该方案包含五个处理阶段，每个阶段都构建在无服务器与托管的 AWS 服务之上，可在校验周期之间缩减到零，因此成本与实际用量成正比。

**阶段 1：区块注册表与调度。** [Amazon EventBridge](https://aws.amazon.com/eventbridge/?refid=5d83343f-40c5-4167-8ec4-5b70bac566f7) 为视觉检查触发每小时的校验周期。每周的数据刷新触发数值校验周期。[Amazon Redshift](https://aws.amazon.com/redshift/?nc2=h_prod_an_rs&refid=5d83343f-40c5-4167-8ec4-5b70bac566f7) 中的配置注册表维护被监控区块的清单，包括区块标识、负责人分配与调度偏好。

**阶段 2：截图抓取。** 两套机制以不同方式抓取证据，各自匹配任务所需。对于视觉检查，[AWS Lambda](https://aws.amazon.com/lambda/?nc2=type_a) 函数编排无头浏览器会话，把每个看板区块完全按照用户所见的方式渲染出来。对于数值基准真值的抓取，仅靠渲染并不够：agent 必须导航看板并应用特定过滤器，因此改用 agentic 浏览器自动化方式（见阶段 3 的说明）。

在存储之前，每张截图都要经过一步脱敏（redaction）：Amazon Rekognition 检测图像中的文本与数值，随后 pipeline 把它们替换为遮蔽后的等价内容——文本替换为脱敏占位符，数字替换为合成值——从而让存储的截图中不保留任何敏感数据。Amazon Rekognition 预训练的光学字符识别（OCR）与文本检测模型无需自定义训练，并会随 Lambda 调用自动伸缩，使脱敏工作既省力又可重复。之后截图存储在 [Amazon Simple Storage Service（Amazon S3）](https://aws.amazon.com/s3/?nc2=type_a) 中，并通过 [Amazon CloudFront](https://aws.amazon.com/cloudfront/?nc2=type_a) 提供访问，以在分析期间实现低延迟读取。

**阶段 3：AI 分析。** 该阶段运行两套并行的校验机制，二者遵循同一设计原则：AI 模型处理需要语义理解的任务，而确定性逻辑处理精度不容妥协的决策。

**视觉内容校验***。* 每张截图连同看板区块的上下文元数据一次性完成分析。Amazon Bedrock 上可用的 Anthropic Claude 模型会检测结构异常，例如空白磁贴、错误状态与缺失的可视化组件。它们还会对问题中最难的部分应用上下文推理：区分合法的空状态（某组过滤器组合确实没有返回数据）与真正的内容故障（pipeline 错误导致图表空白）。按 AWS 区域查看模型可用性，请参阅 [Amazon Bedrock 中按 AWS 区域支持的模型](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html)。若干生产控制措施限定了模型的角色边界：截图在分析前已完成脱敏（阶段 2）；模型输出被限制为带置信度分数的结构化判定，而非自由文本；含糊的结果会转人工审核，而不是触发自动告警。

**数值跨源校验***。* 第二套机制对同一指标在其出现的各个看板之间做一致性交叉核对。它采用一种我们称为混合校验（hybrid validation）的模式：LLM 负责语义工作，确定性代码负责数值判定。同一指标在两个看板上很少以完全相同的标签或版式出现，因此识别它需要语义理解。Amazon Bedrock 上的 LLM 会在抓取的截图中定位每个已声明的指标、读取其数值与单位，并产出成对读数。LLM 对比较规则的应用并不稳定：何时取整、允许多大容差、如何处理单位差异。因此单位归一化（$1.2B 与 $1,200M）与小数精度（58.484 与 58.5）由确定性代码处理，随后对每一对指标给出判定（一致或不一致），为审核者提供可供行动的明确信号。

**阶段 4：告警路由。** 当视觉故障被确认后，系统使用 Block Kit 格式生成一条 Slack 通知，并把它路由给注册的区块负责人，附带视觉证据、置信度分数与可操作的排查链接。对于持续存在的故障，系统会自动创建工单并路由到所属团队以完成升级。数值不一致会被汇总成校验报告供人工审核。

**阶段 5：遥测持久化。** 分析结果持久化到 Amazon Redshift，用于历史趋势与模式分析。[Amazon CloudWatch](https://aws.amazon.com/cloudwatch/?nc2=type_a) 为监控系统自身提供运维指标。

## 面向生产环境的工程实践

从原型走向生产的过程中，浮现出两条经验，如果你正在构建 AI 驱动的校验系统，它们同样适用。

### 先针对误报做设计

在告警系统里，误报是会扼杀采用率的失效模式：收到误报的负责人会不再信任通知。最难处理的不是明显出问题的页面，而是含糊不清的情形——某区块为空，是因为某组过滤器组合确实没有数据。要把上下文推理置于原始速度之上：接受每次检查的分析更慢，换来的是负责人可以直接据此行动、无需再三斟酌的判断。对于每小时的监控周期而言，准确性与可解释性的重要性高于实时性要求。

### 让 LLM 远离算术运算

数值校验机制最初采用双层 LLM 设计：一个 agent 提取并比较数值，第二个裁判 agent 独立核验结果，两者都可使用计算器工具。尽管如此，生产运行仍暴露出偶发错误——问题不在原始算术，而在比较逻辑的一致性：何时取整、应用多大容差、如何处理单位差异。对于一个校验系统来说，哪怕只是偶发的不一致，也会削弱人们对每一次判定的信心。

用确定性代码替换比较阶段，把精度从依赖模型的结果变成了设计上的保证：只要提取出的数值正确，程序化比较就不会出错，与由哪个模型执行提取无关。之后的模型升级改进了提取阶段，把因误读看板数值而产生的误报降了下来，使召回率从 0.88 提升到 0.95。

两套校验机制得出的关键经验是一致的：在设计你自己的系统时，把 AI 分配到它擅长且依赖语义的任务上——看、读、导航；把判定交给确定性代码，因为在判定上哪怕一个错误都会侵蚀信任。

## 实施结果与影响

在视觉校验机制投入生产运行的 30 天里，系统展示了以下结果：

- **数百个看板**处于持续监控之下。
- 执行了 **153,000 次自动化内容检查**。
- 检测到 **802 次内容故障**（占全部检查的 0.52%），相当于系统内容可用性为 99.48%。
- 检测到的故障分布在大范围被监控区块上，而非集中在少数几个问题看板上，这印证了**内容层监控需要全覆盖，而不是抽查**。
- **平均检测时间从最长 72 小时缩短到 1 小时以内**：由于校验周期每小时运行一次，最坏情况下的检测时间受扫描间隔限制。

数值校验机制已按每周周期在生产中运行 6 个多月，每周期校验 50–70 个数据点。在确定性比较设计下，一致的数值会被自动批准；截至目前的生产评估中，没有任何数据问题绕过人工审核而被错误批准。在其中一个生产周期里，系统检测到一处影响一组相关指标的系统性不一致，该问题在下游消费者拿到数据之前就被升级并解决。

## 未来展望

下一阶段的重点在三项能力：

- 跨看板一致性检查：比较整个 AWS Insights 应用中本应相互对齐的相关区块的数值。
- 自动化建议系统：分析错误模式，并基于历史解决数据提出修复动作建议。
- 预测性分析：利用历史故障模式，在问题影响用户之前做出预判。

## 结论

本文展示了我们团队如何构建一套主动式内容校验系统。它通过两套并行的 AI 机制监控数百个在线看板：用 LLM 视觉推理保障视觉完整性，用 agentic 提取配合确定性比较保障数值准确性。借助自动化检测，你可以在内容故障侵蚀用户信任之前、在它传导到消费这些数据的 AI 系统与业务领导者之前，就把它解决掉。

这里展示的模式可迁移到大规模运营 BI 资产的组织：基于截图与基础模型的内容校验、把浏览器自动化作为基准真值抓取机制、在精度关键环节使用确定性判定，以及由遥测闭环支撑的基于归属的告警路由。

要开始使用类似能力，可探索用于获取基础模型访问的 [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/)，以及用于无服务器编排的 [Amazon EventBridge](https://aws.amazon.com/eventbridge/?nc2=type_a) 与 [AWS Lambda](https://aws.amazon.com/lambda/?nc2=type_a)。关于 AI 驱动业务叙述的相关做法，请参阅 [AWS SMGS 如何用 AI 驱动的会话助理和 Amazon Bedrock AgentCore 改造业务管理](https://aws.amazon.com/blogs/machine-learning/how-aws-smgs-uses-an-ai-powered-conversational-assistant-to-transform-business-management-with-amazon-bedrock-agentcore/)。关于我们遥测层所用的 text-to-SQL 模式，请参阅[由 Amazon Bedrock 提供支持的 Text-to-SQL 方案](https://aws.amazon.com/blogs/machine-learning/text-to-sql-solution-powered-by-amazon-bedrock/)。最新动态请访问 [What's New with AWS](https://aws.amazon.com/new/)。

## 致谢

我们感谢各位高管发起人与导师，正是他们的远见与指导让这项工作成为可能。[Aizaz Manzar](https://www.linkedin.com/in/aizazmanzar/)，AWS 全球销售总监；[Sujit Narapareddy](https://www.linkedin.com/in/sujit-narapareddy/)，AWS Insights 总监；[Bernardo Sajonz](https://www.linkedin.com/in/bernardo-sajonz-77b621a2/)，EMEA Insights 产品负责人。

我们也感谢这些专注的团队成员，他们的技术专长与贡献对产品落地至关重要：[Alfonso Mateos Vicente](https://www.linkedin.com/in/alfonso-mateos-vicente-064573223/)，商业智能实习生；[Chris Corcoran](https://www.linkedin.com/in/chris-corcoran-4705b833/)，可靠性工程负责人；[Kimiya Yokoo](https://www.linkedin.com/in/kimiya-yokoo/)，高级技术产品经理；[Matteo Paganotto](https://www.linkedin.com/in/matteo-paganotto-2831549b/)，资深数据工程师；[Ryo Okano](https://www.linkedin.com/in/%E4%BA%AE-%E5%B2%A1%E9%87%8E-4a629b1b2/)，商业智能工程师；[Vaibhav Yadav](https://www.linkedin.com/in/iyadavvaibhav/)，数据工程师；[Ruben Fondon Alcalde](https://www.linkedin.com/in/rub%C3%A9n-fond%C3%B3n-alcalde-253214a/)，资深洞察与分析负责人；[Tatevik Hovhannisyan](https://www.linkedin.com/in/tatevik-hovhannisyan-62b65592/)，资深洞察与分析负责人。

## 关于作者
