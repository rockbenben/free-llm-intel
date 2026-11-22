---
vendor: aws_bedrock
title: Introducing agent quality optimization in AgentCore, now in preview
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/introducing-agent-quality-optimization-in-agentcore-now-in-preview
date: 2026-05-04
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: d81d09bb327d
---

# 在 AgentCore 中引入 agent 质量优化，现已进入预览

*从生产 trace 生成建议，用批量评估和 A/B 测试验证建议，然后放心发布。*

在发布时表现良好的 AI agent 并不会一直保持良好。随着模型演进、用户行为变化，以及提示词被复用到它们从未被设计过的场景中，agent 的质量会悄悄下降。在大多数团队里，改进流程仍然一模一样：没有自动反馈闭环时，当用户抱怨，开发者会翻看 trace、形成假设、重写提示词、测试几个案例，然后发布修复。接着循环重复，而且往往会给另一个用户引入一个新问题。直到今天，[Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) 提供的只是让你手动调试或自建实现的组件：查看评估分数以发现质量下降，深入 trace 确定根因，并用改进后的配置更新 agent。开发者就是那个性能引擎，依靠直觉而非系统化的数据支撑证据。专职的科学团队和大型集中式基准测试有帮助，但对大多数产品团队来说既不实用也不及时。即便你拥有这样的机制，它往往以周或月为周期运转，而 agent 在生产环境中每天都在漂移。

AgentCore 是用于大规模构建、连接和优化 agent 的平台，安全在基础设施层强制执行。已有数千名开发者使用 AgentCore 构建能在复杂工作流中推理、规划和行动的 agent。今天我们宣布 AgentCore 的新能力，它们补全了针对 agent 性能与质量的观测、评估、改进闭环：建议（recommendations），以及两种验证建议的方式。

[建议（Recommendations）](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/optimization-recommendations.html) 会分析生产 trace 和评估输出，针对你指定的评估器优化你的 system prompt 或工具描述。[批量评估（Batch evaluation）](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/batch-evaluations.html) 帮助在预定义的测试数据集上测试建议并报告聚合分数，在你已知的重要案例上捕捉回归。当手工编写的场景不够用时，你还可以用由 LLM 驱动的角色来扮演终端用户，[模拟一个数据集](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/simulation.html)。[A/B 测试](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/ab-testing.html) 通过 [AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html) 在 agent 的不同版本之间做受控对比，按你配置的百分比切分实时生产流量，并用置信区间和统计显著性报告结果。建议提出改动，批量评估和 A/B 测试验证改动，两者合起来替代了阅读 trace、猜测修复、盲目部署的人工循环。

> “持续评估和改进 agent 对于以数据驱动价值创造至关重要。过去需要数周人工提示调优的流程，如今借助 AgentCore 已演变为快速、可重复的循环。通过从生产 trace 数据中得出改进建议，并用 A/B 测试验证其影响，组织可以在优化性能的同时确保准确性和有效性。这种方法使大规模、持续且高效的改进成为可能。”NTT DATA 生成式 AI 业务战略部负责人 Yoshiharu Okuda

**这个闭环在实践中如何运转**

以下是该闭环在模型升级场景中的运转方式。对于任何变更——提示词重构、工具集更新、框架升级——模式都相同。

AgentCore 中的端到端可追溯性把每次模型调用、工具调用和推理步骤都记录为与 OpenTelemetry 兼容的 trace，并由 [AgentCore Observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html) 管理。评估会使用内置评估器、与标准答案对比，或自定义的 LLM-as-judge 评分，按目标成功率、工具选择准确率、有用性和安全性等维度自动为这些 trace 打分。

**生成一条建议。** 把 Recommendations API 指向你的 agent 写入 trace 的 CloudWatch Log 组。把你想要优化的评估器选为奖励信号，可以是 AgentCore 的内置评估器，也可以是你自建的自定义评估器，并选择要优化什么：system prompt 还是工具描述。AgentCore 会结合所提供的奖励信号反思这些 trace，并生成一条旨在提升该奖励信号表现的建议。对于工具描述类建议，它只改进工具描述，不会触碰工具实现。服务负责提出建议，由你决定把哪些推进到验证步骤。

**把变更打包为配置包（bundle）。** 配置以 bundle 的形式发布，它是 agent 配置的不可变、带版本的快照，以 runtime ARN 为键：模型 ID、system prompt、工具描述。你的 agent 在运行时通过 AgentCore SDK 动态读取其生效配置，因此换一个提示词或换一个模型是配置变更，而不是代码变更。为当前配置创建一个 bundle，为建议再创建一个。bundle 是可选的。对于包含代码的变更，请改为部署到单独的 runtime 端点。

**离线验证：批量评估。** 用新的 bundle 让 agent 在一套精选数据集上运行，然后批量评估由此产生的会话，并把聚合分数与基线比较。这样可以在你已定义的用例上捕捉回归。团队通常会把批量评估接入 CI/CD 流水线，使任何配置变更都必须通过其已知可用案例才能进入生产。

**针对实时流量验证：A/B 测试。** 配置 AgentCore Gateway 在两个变体之间切分实时生产流量，以当前版本作为对照组、候选版本作为实验组。变体可以是同一 runtime 上不同的 bundle 版本（用于仅含配置的变更），也可以是网关的不同目标、分别指向不同的 runtime 端点（用于包含代码的变更）。在线评估用你指定的评估器为每个会话打分。A/B 测试结果包含置信区间和 p 值。当你有足够数据对新版本的表现建立信心时，停止测试并把新变体设为默认以完成推广。要回滚时，暂停测试，agent 就会回到它原有的配置。

*“过去需要数周人工提示迭代的工作，如今借助 AgentCore 成为可重复的循环：从生产 trace 生成建议、用统计显著性针对实时流量验证建议、并部署胜出的配置。每个循环都为下一个循环产出基线数据——改进过程会不断累积放大。*”——Nomura Research Institute, Ltd. 高级常务董事 Masashi Shimizu

**我们前进的方向**

今天的预览版在设计上是由开发者触发的。你决定何时生成建议、针对哪个评估器，以及是否推广结果。我们的愿景是一个飞轮：trace 喂养评估，评估揭示漂移，建议把该信号转化为具体变更，A/B 测试证明它有效。胜出的配置成为新的基线，它产生的 trace 又成为下一个循环的输入。随着时间推移，飞轮的转动会越来越省力。建议会把多个评估器放在一起权衡，用证据揭示取舍。它们还会把优化范围扩展到技能（skill），根据生产使用情况提出新技能或改进现有技能。trace 分析会把生产故障聚类为模式，让你能在它们成倍增长之前加以处理。当某个评估器低于阈值时，监控告警会自行启动一次建议与验证，并把结果送入审核队列。你决定发布什么，而系统可以承担走到那一步的重活。

**看看实际效果**

[GitHub 上的 Market Trends Agent 示例](https://github.com/awslabs/agentcore-samples/tree/main/02-use-cases/market-trends-agent) 是为投资经纪商构建的市场情报 agent，覆盖实时股票数据、行业分析、新闻搜索和个性化经纪商画像。对于一个要为风险偏好、行业关注点和对话风格各不相同的经纪商服务的 agent 来说，质量下降很难被发现，而没有合适的工具就更难修复。

走完整个改进闭环：生成一条建议，暴露出该 agent 在何处未能依据经纪商声明的策略个性化建议，或在查询跨越多个行业时选错了工具。把该变更打包为一个配置 bundle 版本。用一批精选的经纪商对话做批量评估来验证修复。然后在有统计置信度的情况下，用真实经纪商会话对该配置做 A/B 测试，再推广到生产。

**开始使用**

这些能力今天已在提供 AgentCore Evaluations 的 [AWS 区域中的 Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-regions.html) 以预览形式提供。在预览期间，AgentCore Optimization 针对部署在 AgentCore Runtime 上并使用 AgentCore Observability 和 Evaluations 的 agent 的 system prompt 与工具描述。

通过 AgentCore Console 或 CLI 开始使用。阅读[文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/optimization.html)，并按照[这里的](https://github.com/awslabs/agentcore-samples/tree/main/01-tutorials/12-AgentCore-optimization)分步教程操作。

## 关于作者
