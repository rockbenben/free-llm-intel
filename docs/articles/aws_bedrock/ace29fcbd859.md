---
vendor: aws_bedrock
title: 影响成本的四种 Amazon Bedrock 推理选择
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/four-amazon-bedrock-inference-choices-that-affect-cost
date: 2026-11-12
lang: zh
captured: 2026-11-13
extractor: readability-v1
translator: mt
status: translated
body_sha: 8c8203360a27
---

## [人工智能](https://aws.amazon.com/blogs/machine-learning/)

# 影响成本的四个 Amazon Bedrock 推理选择

在您调整提示和应用程序逻辑后，您的 Amazon Bedrock 推理费用可能会继续攀升。请求级别的选择仍然可以改变服务处理的令牌数量以及应用于它们的速率。缓存持续时间、服务层、推理工作和“maxTokens”可能会影响成本，而无需更改模型或提示。

每个选择都取决于模型和工作负载。这篇文章展示了我们如何测试每个选择以及如何从响应元数据、日志和计费数据验证其效果。

要亲自尝试这些设置，请从 Amazon Bedrock 示例笔记本 [混合 TTL 缓存](https://github.com/aws-samples/amazon-bedrock-samples/blob/main/introduction-to-bedrock/prompt-caching/converse_api/notebooks/04_mixed_ttl_caching.ipynb) 和 [带提示的租户隔离] 开始缓存](https://github.com/aws-samples/amazon-bedrock-samples/blob/main/introduction-to-bedrock/prompt-caching/converse_api/notebooks/05_tenant_isolation.ipynb)。有关“maxTokens”和推理工作，请参阅 [sample-code-for-genai-cost-management-workshop](https://github.com/aws-samples/sample-code-for-genai-cost-management-workshop/tree/main/samples/2-optimize/01-low-effort) GitHub 存储库的 01-low-effort 文件夹。每个样本都会设置自己的模型 ID，因此请更改它和推理参数，以匹配您调用的模型。有关 AWS 区域的模型可用性，请参阅[模型一览](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards.html)。有关模型选择、批量推理、路由和蒸馏等更广泛的决策，请参阅 [Amazon Bedrock 的有效成本优化策略](https://aws.amazon.com/blogs/machine-learning/ effective-cost-optimization-strategies-for-amazon-bedrock/)。

## 推理成本从何而来

每个 Amazon Bedrock 响应都携带使用情况元数据。输入和输出令牌按照服务请求的模型和层的费率计费。缓存读取和写入使用单独的令牌计数器，推理令牌计为输出令牌。

## 提示缓存时长

当缓存在下一个请求之前过期时，可以再次处理重复的系统指令、工具定义或引用上下文。 [提示缓存以加快模型推理速度](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html) 指南列出了受支持的 Anthropic 模型的 5 分钟和 1 小时生存时间 (TTL) 值。它还列出了受支持的 GPT-5.6 型号的 30 分钟最小 TTL。支持和 API 字段取决于模型，因此在选择持续时间之前请检查当前的支持矩阵。

对于支持的模型，Amazon Bedrock 还提供[隐式提示缓存](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html#prompt-caching-implicit)，它会尝试在请求中重用符合条件的提示前缀，而无需进行缓存控制。由于隐式缓存是尽力而为，并且不能保证缓存命中，因此本节中的持续时间选择适用于显式缓存。

此 Converse API 签名请求支持它的型号的 1 小时条目：
```
{ "cachePoint": { "type": "default", "ttl": "1h" } }
```
对于支持的 Anthropic 模型，InvokeModel 在“cache_control”中放置相同的“ttl”值。

持续时间越长并不一定会更便宜。 [Amazon Bedrock 定价](https://aws.amazon.com/bedrock/pricing/) 页面列出了 5 分钟写入、1 小时写入和缓存读取的单独费率。对于 Amazon Bedrock 上的 Anthropic Claude Sonnet 5 和 Anthropic Claude Opus 5，5 分钟写入成本是输入速率的 1.25 倍。 1小时写入成本是2倍，缓存读取成本是0.1倍。

这些速率设置盈亏平衡，假设每个请求重复使用确切的前缀并且每个缓存读取都会刷新 TTL。 5 分钟缓存在第一次重用时会在 5 分钟内得到回报。当对相同前缀的请求到达间隔超过 5 分钟时，它会对每个请求重写 1.25 次。 1 小时缓存比一小时内的第二个请求便宜。

缓存速率和检查点最小值因型号而异。检查您调用的模型的 [Amazon Bedrock 定价](https://aws.amazon.com/bedrock/pricing/) 页面和[提示缓存指南](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html)。重新运行模型比较，然后在推出后使用缓存读取和写入令牌进行确认。

在动态内容之前保留稳定内容，满足模型的最低检查点要求，并使用按需推理，因为即时缓存不适用于批量推理。

更改缓存的前缀（包括系统指令或工具定义）会导致未命中和新的写入。检查点按照工具、系统、消息的顺序进行评估，因此前面部分的更改也会使后面的部分失效。版本提示经常更改，因此每个版本都有自己的缓存条目。我们对 Claude Sonnet 5 运行了 6 次调用，检查点为 1 小时，更改了一次系统提示符和一次工具定义。每次更改都会产生零次缓存读取和一次新写入。

AWS 将缓存条目描述为您的账户和区域，而不是您的租户。在多租户应用程序中，将租户特定的 SHA-256 哈希值添加到可缓存前缀之前。 [使用 Amazon Bedrock 提示缓存优化人类模型的成本和延迟](https://aws.amazon.com/blogs/machine-learning/optimizing-cost-and-latency-with-amazon-bedrock-prompt-caching/) 文章描述了这种模式。在构建提示之前强制执行租户授权。哈希对一个帐户内的条目进行分区。如果受监管的工作负载需要硬数据边界，请将每个租户保留在单独的 AWS 账户中。

保留 5 分钟默认值以便频繁重复使用。当同一前缀每小时至少重复两次且间隔时间超过 5 分钟时，请从该时间改为更长的受支持持续时间。为了避免完全没有缓存，1 小时缓存每小时需要 3 个请求。

## 耐延迟工作负载的服务层

后台作业、评估工具、夜间总结和回填并不总是需要交互式请求使用的延迟配置文件。对于支持 Flex 的型号，请使用以下请求签名选择它：
```
{ "serviceTier": { "type": "flex" } }
```
使用“default”而不是“standard”来请求标准层。您还可以省略`serviceTier`：
```
{ "serviceTier": { "type": "default" } }
```
层支持是特定于型号的，因此请按确切的型号版本记录支持。 [Amazon Nova 2 Lite](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-2-lite.html) 和 [OpenAI gpt-oss-120b](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-oss-120b.html) 型号卡将 Flex 列为受支持。 Amazon Bedrock 上的 [Anthropic Claude Sonnet 5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-5.html) 和 [Anthropic Claude Opus 5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-5.html) 的卡片将其列为未列出支持。对不受支持的模型的 Flex 请求失败并出现“ValidationException”，而不是在 Standard 上静默运行。我们对 Anthropic Claude Sonnet 5 的请求返回了该错误。

如果您的策略允许标准作为后备，请捕获不支持的层错误并使用“default”重试一次。不要重试每个“ValidationException”，因为格式错误的请求也会引发该异常。限制应用程序级别的重试。 AWS 开发工具包的有限重试策略可处理限制和暂时性错误。

为 Flex 请求设置您自己的截止日期。支持的响应会报告已解析的层，您也可以使用 Amazon CloudWatch `ResolvedServiceTier` 进行验证。请参阅[用于优化性能和成本的服务层级](https://docs.aws.amazon.com/bedrock/latest/userguide/service-tiers-inference.html) 和 [Amazon Bedrock 定价](https://aws.amazon.com/bedrock/pricing/) 页面，了解您调用的确切模型。

我们在 Amazon Nova 2 Lite 上测试了 Flex，使用 200 个“默认”请求和 200 个“flex”请求，以交错对的方式发送。两层处理相同数量的输入和输出令牌。所有 400 个请求都解析到所请求的层，并且中值延迟差异太小，无法与噪声区分开。在撰写本文时，us-west-2 公布的 Nova 2 Lite Flex 费率是标准费率的一半，我们的账单也反映了这一点。检查 [Amazon Bedrock 定价](https://aws.amazon.com/bedrock/pricing/) 页面了解当前费率。将延迟敏感的流量保持在“默认”状态。

## 适应性思维努力

推理令牌作为输出令牌进行计费。默认情况下，Claude Sonnet 5 和 Claude Opus 5 会以“高”努力使用适应性思维，即使请求省略了“思考”字段也是如此。从 Claude Sonnet 4.6 迁移而来的应用程序没有进行任何更改，开始对思考令牌进行计费，并且“maxTokens”现在限制思考和响应文本。Claude Haiku 5.5 默认为“中”。所有三个模型都支持“low”、“medium”、“high”、“xhigh”和“max”。使用此请求签名可以减少任务的工作量：
```
{
  "thinking": { "type": "adaptive" },
  "output_config": { "effort": "low" }
}
```
将精力放在“output_config”中，而不是“thinking”中。每当您更改模型时，请检查[自适应思维](https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html)。

我们在 Claude Opus 5 上测试了一种工具调用代理。它的三个任务遵循[在 Amazon Bedrock 上使用 Grok 4.7 构建长范围代理](https://aws.amazon.com/blogs/machine-learning/build-long-horizo​​n-agents-with-grok-4-7-on-amazon-bedrock/) 中的设计，每个任务都有一个正确答案。我们在每个努力级别上将每个任务运行八次。该表显示了中值输出标记：

| **努力** | **正确运行** | **中值输出令牌** | **从低位变化（95% 区间）** |
| --- | --- | --- | --- |
|低| 24 共 24 | 936 | 936基线 |
|中等| 24 共 24 | 1,484 | 1,484 +59%（50% 至 78%）|
|高（默认）| 24 共 24 | 2,521 | 2,521 +169%（112% 至 190%）|
| x高 | 24 共 24 | 2,964 | 2,964 +217%（170% 至 260%）|
|最大| 24 共 24 | 3,762 | 3,762 +302%（180% 至 402%）|

较低工作量的准确性取决于模型和任务。衡量与您的任务相似的任务。

在 Amazon Bedrock 示例[调用 Bedrock 模型进行代码生成](https://github.com/aws-samples/amazon-bedrock-samples/blob/main/genai-use-cases/text- Generation/how_to_work_with_code_genesis_w_bedrock.ipynb) 工作负载中，输出令牌中位数在“低”时为 676，在“高”时为 743，这是运行与运行之间的差异。我们评分的项目在每个努力级别上都通过了。

使用每个请求的输出令牌计数、CloudWatch `AWS/Bedrock OutputTokenCount`、调用日志和任务通过率来评估选择。从“高”以下开始执行常规的、有明确界限的任务。当质量测试表明任务需要时，保持“高”。破坏任务的代币减少并不是节省。

## 输出代币限制

`maxTokens` 是应用程序输出上限。它限制了请求停止之前错误的提示、回归或循环可能产生的输出。配额规则记录在 [Amazon Bedrock 中的令牌计算方式](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-token-burndown.html) 中。当请求开始时，Amazon Bedrock 会扣除您的输入令牌加上“maxTokens”，因此过大的值会降低并发性。

输出上限不是安全控制。使用 Amazon Bedrock Guardrails 作为生产生成 AI 工作负载中的标准负责任 AI 控制。 Guardrails 可以过滤内容、检测即时攻击并检查支持的输入和响应的接地情况。请参阅[使用 Amazon Bedrock Guardrails 检测和过滤有害内容](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)。

观察代表性输出令牌分布后，设置每个任务类型的“maxTokens”：
```
{ "inferenceConfig": { "maxTokens": 155 } }
```
有关请求参数，请参阅[使用 Converse API 进行推理](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html)。

在我们对 Claude Sonnet 5 的测试中，五个正常输出的峰值为 103 个令牌，因此我们设置了一个具有净空的 155 个令牌的说明性栅栏。然后，我们在禁用自适应思维的情况下发送了相同的故意冗长的提示，一次低于 2,048 个代币上限，一次低于 155 个代币围栏。第一个请求生成 2,048 个输出令牌，第二个请求生成 155 个，因此栅栏避免了 1,893 个输出令牌。两者都停在“max_tokens”处，因此两个响应都被截断。栅栏限制了支出，但不会使不合适的提示变得有用，并且在多回合或代理链中，截断的回合可能会破坏其后面的步骤。

对于生产校准，比较每个任务类型的第 95 个和第 99 个百分位数（P95 和 P99），并向选定的百分位数添加余量。启用自适应思维后，“maxTokens”也会限制思维标记，因此请在启用思维的情况下进行校准。 P95 更积极地限制暴露，但接受更多的截断风险。 P99 在更高的上限下保留了更有效的长尾响应。在提高任务限制之前，监视“max_tokens”停止并调查请求。

## 把它放在一起

对每个设置使用相同的测试循环：确认模型支持、更改一个请求选择、测量令牌或成本以及跟踪质量或完成情况。如果跨模型路由，请保留每个模型版本、区域和 API 的能力记录：支持的缓存持续时间、服务层级、推理级别和输出上限。在发送之前根据该记录验证每个请求，然后检查已解析层和缓存计数器的响应。

| **设置** | **默认或许可状态** | **结果** | **接受风险** |
| --- | --- | --- | --- |
|缓存持续时间|特定型号 TTL |从已发布的 Sonnet 5 和 Opus 5 速率来看，当间隙超过 5 分钟时，1 小时缓存胜过每小时第二个请求 | 1 小时的写入成本是输入的 2 倍，因此低重用会造成损失。分区租户前缀 |
|服务等级| `默认` |在撰写本文时，Nova 2 Lite Flex 的发布价格是标准价格的一半，我们的账单也与之相符 |处理时间较长。设定自己的截止日期和后备方案 |
|推理努力|测试自适应模型的“高”|从低到高：代理测试中输出令牌中值+169%，代码生成没有可靠的差异 |质量可能会下降到接近任务的能力边界。使用代币追踪通过率 |
| `maxTokens` |允许的 2,048 个代币上限 |示例性的 155 个令牌栅栏在一次测试中避免了 1,893 个输出令牌 |截断可以通过多轮链或代理链级联。在提高限制之前检查“stopReason” |

## 需要注意的信号

| **设置** | **症状** | **验证** | **第一反应** |
| --- | --- | --- | --- |
|缓存持续时间|重复上下文不会产生预期的延迟或成本效益 |应用程序延迟和成本遥测|更改 TTL 之前检查前缀稳定性、重用间隔和模型支持 |
|服务等级|请求的层不受支持或服务层与预期不同 |响应 `serviceTier` 和 CloudWatch `ResolvedServiceTier` |使用受支持的层或将延迟敏感流量返回到“默认” |
|推理努力|产出代币上升，质量保持不变 |每个请求响应遥测、CloudWatch `OutputTokenCount`、调用日志和任务通过率 |减少该任务类别的工作量并重新运行其质量测试 |
| `maxTokens` | `stopReason` 是 `max_tokens` |响应停止原因和任务范围的输出令牌分配 |在提高限制之前检查提示和任务栏 |

从任务标记的应用程序遥测或调用日志中派生每种任务类型的 P95 和 P99。

## 结论

所有四个选择都存在于推理请求中。更改型号时重新检查支持，然后一次更改一项设置并在应用程序中测量结果。

使用这些资源来评估适合您的工作负载的选择：

- Amazon Bedrock 控制台：[console.aws.amazon.com/bedrock](https://console.aws.amazon.com/bedrock/)。
- 提示缓存：[提示缓存以加快模型推理速度](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html)。
- 服务层级：[用于优化性能和成本的服务层级](https://docs.aws.amazon.com/bedrock/latest/userguide/service-tiers-inference.html)。
- 适应性思维：[适应性思维](https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html)。
- 负责任的 AI 控制：[使用 Amazon Bedrock Guardrails 检测和过滤有害内容](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)。
- 相关阅读：[Amazon Bedrock 的有效成本优化策略](https://aws.amazon.com/blogs/machine-learning/ effective-cost-optimization-strategies-for-amazon-bedrock/)。
- 相关示例和帖子：[调用 Bedrock 模型进行代码生成](https://github.com/aws-samples/amazon-bedrock-samples/blob/main/genai-use-cases/text- Generation/how_to_work_with_code_ Generation_w_bedrock.ipynb) 和 [在 Amazon 上使用 Grok 4.7 构建长期代理Bedrock](https://aws.amazon.com/blogs/machine-learning/build-long-horizon-agents-with-grok-4-7-on-amazon-bedrock/)。

## 关于作者
