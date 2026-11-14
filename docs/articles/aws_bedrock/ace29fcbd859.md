---
vendor: aws_bedrock
title: 影响成本的四个 Amazon Bedrock 推理选项
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/four-amazon-bedrock-inference-choices-that-affect-cost
date: 2026-11-12
lang: zh
captured: 2026-11-14
extractor: readability-v1
translator: agent
status: translated
body_sha: 1fb4d7fbdd8f
---

## [人工智能](https://aws.amazon.com/blogs/machine-learning/)

# 影响成本的四个 Amazon Bedrock 推理选项

就算调好了 prompt 和应用逻辑，Amazon Bedrock 的推理账单仍可能一路往上涨。请求层面的选择照样能改变服务处理的 token 数量，以及套在它们身上的费率。缓存时长、服务层级、推理力度和 `maxTokens` 都能在不换模型、不改 prompt 的前提下影响成本。

每个选择都取决于具体模型和工作负载。本文讲我们怎么逐项测试，以及怎么用响应元数据、日志和账单数据核实效果。

想亲手试这些设置，可以从 Amazon Bedrock Samples 的 [混合 TTL 缓存](https://github.com/aws-samples/amazon-bedrock-samples/blob/main/introduction-to-bedrock/prompt-caching/converse_api/notebooks/04_mixed_ttl_caching.ipynb) 和 [用 prompt 缓存做租户隔离](https://github.com/aws-samples/amazon-bedrock-samples/blob/main/introduction-to-bedrock/prompt-caching/converse_api/notebooks/05_tenant_isolation.ipynb) notebook 入手。`maxTokens` 和推理力度可看 [sample-code-for-genai-cost-management-workshop](https://github.com/aws-samples/sample-code-for-genai-cost-management-workshop/tree/main/samples/2-optimize/01-low-effort) GitHub 仓库里的 01-low-effort 文件夹。每个示例都设了自己的模型 ID，记得把它和推理参数一起改成你实际调用的模型。各 AWS Region 的模型可用性参见[模型速览](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards.html)。模型选型、批量推理、路由、蒸馏这类更上层的决策，参见 [Amazon Bedrock 的有效成本优化策略](https://aws.amazon.com/blogs/machine-learning/effective-cost-optimization-strategies-for-amazon-bedrock/)。

## 推理成本从何而来

Amazon Bedrock 的每个响应都带用量元数据。输入和输出 token 按服务该请求的模型与层级的费率计费。缓存读写用单独的 token 计数器，推理 token 计作输出 token。

## Prompt 缓存时长

重复出现的系统指令、工具定义或参考上下文，如果缓存赶在下一个请求之前过期，就得重新处理一遍。[用 prompt 缓存加快模型推理](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html)指南列出了受支持的 Anthropic 模型可用的 5 分钟和 1 小时 time-to-live（TTL）取值，也列出了受支持的 GPT-5.6 模型 30 分钟的最小 TTL。支持情况和 API 字段因模型而异，选定时长前先查最新的支持矩阵。

对受支持的模型，Amazon Bedrock 还提供[隐式 prompt 缓存](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html#prompt-caching-implicit)：请求里不写缓存控制，它也会尝试复用符合条件的 prompt 前缀。由于隐式缓存是尽力而为、不保证命中，本节的时长选择针对的是显式缓存。

下面这个 Converse API 签名会在支持它的模型上申请一个 1 小时的缓存条目：

```
{ "cachePoint": { "type": "default", "ttl": "1h" } }
```

对受支持的 Anthropic 模型，InvokeModel 会把同样的 `ttl` 值放进 `cache_control`。

时长更长并不自动等于更便宜。[Amazon Bedrock 定价](https://aws.amazon.com/bedrock/pricing/)页面对 5 分钟写入、1 小时写入和缓存读取分别列出费率。在 Amazon Bedrock 上，Anthropic Claude Sonnet 5 和 Anthropic Claude Opus 5 的 5 分钟写入是输入费率的 1.25 倍，1 小时写入是 2 倍，缓存读取是 0.1 倍。

这些费率决定了盈亏平衡点，前提是每个请求都复用完全相同的前缀，且每次缓存读取都会刷新 TTL。5 分钟缓存在 5 分钟内第一次复用就能回本；如果同一前缀的请求间隔超过 5 分钟，它就会在每个请求上按 1.25 倍重写一遍。这种情况下，1 小时缓存从一小时内第二次请求起反而更便宜。

缓存费率和检查点最小值因模型而异。针对你调用的模型，查 [Amazon Bedrock 定价](https://aws.amazon.com/bedrock/pricing/)页面和 [prompt 缓存指南](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html)。按自己的模型重跑一遍对比，上线后再用缓存读写 token 确认。

把稳定内容放在动态内容之前，满足模型的检查点最小值，并且用按需推理——prompt 缓存不适用于批量推理。

改动已缓存的前缀（包括系统指令或工具定义）会导致未命中，并触发一次新写入。检查点按工具、系统、消息的顺序求值，所以靠前的部分一改，后面的也跟着失效。对频繁变动的 prompt 做版本管理，让每个版本有自己的缓存条目。我们在 Claude Sonnet 5 上用 1 小时检查点跑了六次调用，其中改过一次系统 prompt、一次工具定义；每次改动都带来零次缓存读取和一次新写入。

AWS 说缓存条目的作用域是账户和 Region，不是租户。在多租户应用里，给可缓存前缀前面加一个租户专属的 SHA-256 哈希。[用 Amazon Bedrock prompt 缓存优化 Anthropic 模型的成本与延迟](https://aws.amazon.com/blogs/machine-learning/optimizing-cost-and-latency-with-amazon-bedrock-prompt-caching/)一文讲了这个做法。构造 prompt 之前先做好租户鉴权。哈希只是把同一个账户内的条目分区；如果受监管的工作负载需要硬性数据边界，就让每个租户各用一个 AWS 账户。

频繁复用的场景保留 5 分钟默认值。当同一前缀每小时至少出现两次、且间隔超过 5 分钟时，再换到更长的受支持时长。要胜过完全不缓存，1 小时缓存需要每小时三次请求。

## 可容忍延迟工作负载的服务层级

后台作业、评测框架、夜间汇总和回填，未必需要交互式请求那套延迟表现。对支持 Flex 的模型，用下面这个请求签名选用它：

```
{ "serviceTier": { "type": "flex" } }
```

要请求 Standard 层级，用 `default`，不是 `standard`。也可以直接省略 `serviceTier`：

```
{ "serviceTier": { "type": "default" } }
```

层级支持因模型而异，要按确切的模型版本记录。[Amazon Nova 2 Lite](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-2-lite.html) 和 [OpenAI gpt-oss-120b](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-oss-120b.html) 的模型卡把 Flex 列为支持；Amazon Bedrock 上 [Anthropic Claude Sonnet 5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-5.html) 和 [Anthropic Claude Opus 5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-5.html) 的模型卡则列为不支持。向不支持的模型发 Flex 请求会报 `ValidationException`，而不是悄悄按 Standard 跑。我们发给 Anthropic Claude Sonnet 5 的请求就返回了这个错误。

如果策略允许回退到 Standard，就捕获"层级不支持"的错误，用 `default` 重试一次。别对每个 `ValidationException` 都重试，格式错误的请求也会抛这个异常。应用层的重试要设上限。限流和瞬时错误交给 AWS SDK 的有界重试策略去处理。

给 Flex 请求设自己的截止时间。受支持的响应会带回最终解析出的层级，也可以用 Amazon CloudWatch `ResolvedServiceTier` 核实。针对你调用的确切模型，参见[用于优化性能与成本的服务层级](https://docs.aws.amazon.com/bedrock/latest/userguide/service-tiers-inference.html)和 [Amazon Bedrock 定价](https://aws.amazon.com/bedrock/pricing/)页面。

我们在 Amazon Nova 2 Lite 上测了 Flex：200 个 `default` 请求和 200 个 `flex` 请求，成对交错发送。两个层级处理的输入、输出 token 数相同，全部 400 个请求都解析到了所请求的层级，延迟中位数之差小到和噪声分不开。撰文时，us-west-2 里 Nova 2 Lite 的 Flex 公布费率是 Standard 的一半，我们的账单也印证了这一点。当前费率请查 [Amazon Bedrock 定价](https://aws.amazon.com/bedrock/pricing/)页面。对延迟敏感的流量继续留在 `default`。

## Adaptive thinking 的推理力度

推理 token 按输出 token 计费。Claude Sonnet 5 和 Claude Opus 5 默认以 `high` 力度启用 adaptive thinking，哪怕请求里没写 `thinking` 字段。一个从 Claude Sonnet 4.6 原样迁过来的应用，会开始为 thinking token 计费，而且 `maxTokens` 现在同时限制 thinking 和响应正文。Claude Haiku 5.5 默认 `medium`。这三个模型都支持 `low`、`medium`、`high`、`xhigh` 和 `max`。要给某个任务降力度，用这个请求签名：

```
{
  "thinking": { "type": "adaptive" },
  "output_config": { "effort": "low" }
}
```

effort 要放在 `output_config` 里，别塞进 `thinking`。每次换模型都查一下 [Adaptive thinking](https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html)。

我们在 Claude Opus 5 上测了一个会调用工具的 agent。它的三个任务沿用[在 Amazon Bedrock 上用 Grok 4.7 构建长程 agent](https://aws.amazon.com/blogs/machine-learning/build-long-horizon-agents-with-grok-4-7-on-amazon-bedrock/)里的设计，每个任务只有一个正确答案。每个任务在每个力度档位各跑八次。下表是输出 token 的中位数：

| **力度** | **正确次数** | **输出 token 中位数** | **相对 low 的变化（95% 区间）** |
| --- | --- | --- | --- |
| low | 24 of 24 | 936 | 基线 |
| medium | 24 of 24 | 1,484 | +59% (50% to 78%) |
| high (default) | 24 of 24 | 2,521 | +169% (112% to 190%) |
| xhigh | 24 of 24 | 2,964 | +217% (170% to 260%) |
| max | 24 of 24 | 3,762 | +302% (180% to 402%) |

低力度下的准确率取决于模型和任务。用跟你自己的任务形态相近的任务去测。

在 Amazon Bedrock Samples 的[调用 Bedrock 模型做代码生成](https://github.com/aws-samples/amazon-bedrock-samples/blob/main/genai-use-cases/text-generation/how_to_work_with_code_generation_w_bedrock.ipynb)工作负载上，`low` 的输出 token 中位数是 676，`high` 是 743，差异落在多次运行本身的波动范围内。我们评分的程序在每个力度档位都通过了。

评估这个选择，可以看每请求的输出 token 数、CloudWatch `AWS/Bedrock OutputTokenCount`、调用日志和任务通过率。常规、边界清晰的任务从 `high` 以下起步；质量测试表明确实需要时再保留 `high`。把任务搞坏的 token 削减不叫省钱。

## 输出 token 上限

`maxTokens` 是应用侧的输出上限，用来在请求停止之前，兜住糟糕的 prompt、回归缺陷或循环可能吐出的输出。配额规则写在 [Amazon Bedrock 中 token 如何计数](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-token-burndown.html)里。请求一开始，Amazon Bedrock 就扣掉输入 token 加上 `maxTokens`，所以这个值设得过大会压低并发。

输出上限不是安全控制。生产环境的生成式 AI 工作负载，应当把 Amazon Bedrock Guardrails 当作标准的负责任 AI 控制。Guardrails 能过滤内容、检测 prompt 攻击，并对受支持的输入和响应做接地检查。参见[使用 Amazon Bedrock Guardrails 检测并过滤有害内容](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)。

先观察有代表性的输出 token 分布，再按任务类型设定 `maxTokens`：

```
{ "inferenceConfig": { "maxTokens": 155 } }
```

请求参数参见[使用 Converse API 进行推理](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html)。

在 Claude Sonnet 5 的测试里，五个正常输出最多到 103 个 token，于是我们留了余量，设了一道示意性的 155 token 围栏。接着关掉 adaptive thinking，把同一条故意写得很啰嗦的 prompt 发两次：一次放在 2,048 token 上限下，一次放在 155 token 围栏下。第一次生成了 2,048 个输出 token，第二次 155 个，围栏因此省下 1,893 个输出 token。两次都停在 `max_tokens`，响应都被截断了。围栏能限住支出，但不会让一条不合适的 prompt 变得有用；而且在多轮或 agentic 链条里，被截断的一轮可能把后面的步骤带崩。

生产环境校准时，比较每类任务的第 95 和第 99 百分位（P95 与 P99），再给选定的百分位加余量。开着 adaptive thinking 时，`maxTokens` 也会限制 thinking token，所以校准要在启用 thinking 的状态下做。P95 更激进地压住敞口，但要多担截断风险；P99 上限更高，能保留更多有效的长尾响应。盯住 `max_tokens` 停止的情况，调高任务上限之前先把请求查清楚。

## 综合起来

每个设置都用同一套测试循环：确认模型支持、只改一个请求选项、测 token 或成本、跟踪质量或完成情况。如果跨模型路由，就为每个模型版本、Region 和 API 留一份能力记录：支持的缓存时长、服务层级、推理档位和输出上限。发请求前先拿这份记录校验，再在响应里核对最终层级和缓存计数器。

| **设置** | **默认或宽松状态** | **结果** | **需要接受的风险** |
| --- | --- | --- | --- |
| 缓存时长 | 因模型而异的 TTL | 按已公布的 Sonnet 5 和 Opus 5 费率，当间隔超过 5 分钟时，1 小时缓存从每小时第二个请求起更划算 | 1 小时写入成本是输入的 2 倍，复用率低反而亏钱。给租户前缀做分区 |
| 服务层级 | `default` | 撰文时 Nova 2 Lite Flex 的公布费率是 Standard 的一半，我们的账单也吻合 | 处理时间更长。设好自己的截止时间和回退方案 |
| 推理力度 | 被测自适应模型上为 `high` | 从 low 到 high：agent 测试里输出 token 中位数 +169%，代码生成上没有可靠差异 | 质量可能在接近任务能力边界时下滑。连着 token 一起跟踪通过率 |
| `maxTokens` | 宽松的 2,048 token 上限 | 一次测试里，示意性的 155 token 围栏省下 1,893 个输出 token | 截断会在多轮或 agentic 链条里级联。调高上限前先查 `stopReason` |

## 需要留意的信号

| **设置** | **症状** | **用什么核实** | **第一步动作** |
| --- | --- | --- | --- |
| 缓存时长 | 重复的上下文没带来预期的延迟或成本收益 | 应用延迟与成本遥测 | 改 TTL 之前先查前缀稳定性、复用间隔和模型支持情况 |
| 服务层级 | 请求的层级不受支持，或实际服务层级与预期不符 | 响应里的 `serviceTier` 和 CloudWatch `ResolvedServiceTier` | 换用受支持的层级，或把延迟敏感的流量退回 `default` |
| 推理力度 | 输出 token 上去了，质量却没变 | 每请求的响应遥测、CloudWatch `OutputTokenCount`、调用日志和任务通过率 | 给这类任务调低力度，重跑它的质量测试 |
| `maxTokens` | `stopReason` 是 `max_tokens` | 响应停止原因和按任务统计的输出 token 分布 | 调高上限之前，先检查 prompt 和任务围栏 |

每类任务的 P95 和 P99，从带任务标签的应用遥测或调用日志里算出来。

## 结论

这四个选择都落在推理请求里。换模型时重新确认支持情况，然后一次只改一个设置，在自己的应用里量结果。

用这些资源评估适合你工作负载的选择：

- Amazon Bedrock 控制台：[console.aws.amazon.com/bedrock](https://console.aws.amazon.com/bedrock/)。
- Prompt 缓存：[用 prompt 缓存加快模型推理](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html)。
- 服务层级：[用于优化性能与成本的服务层级](https://docs.aws.amazon.com/bedrock/latest/userguide/service-tiers-inference.html)。
- Adaptive thinking：[Adaptive thinking](https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html)。
- 负责任 AI 控制：[使用 Amazon Bedrock Guardrails 检测并过滤有害内容](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)。
- 延伸阅读：[Amazon Bedrock 的有效成本优化策略](https://aws.amazon.com/blogs/machine-learning/effective-cost-optimization-strategies-for-amazon-bedrock/)。
- 相关示例与文章：[调用 Bedrock 模型做代码生成](https://github.com/aws-samples/amazon-bedrock-samples/blob/main/genai-use-cases/text-generation/how_to_work_with_code_generation_w_bedrock.ipynb) 和 [在 Amazon Bedrock 上用 Grok 4.7 构建长程 agent](https://aws.amazon.com/blogs/machine-learning/build-long-horizon-agents-with-grok-4-7-on-amazon-bedrock/)。

## 关于作者
