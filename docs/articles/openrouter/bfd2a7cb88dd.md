---
vendor: openrouter
title: Provider 差异：推出 Exacto
original_title: Provider Variance: Introducing Exacto
url: https://openrouter.ai/blog/announcements/provider-variance-introducing-exacto
date: 2025-10-21
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Provider 差异：推出 Exacto

Chris Clark · 2025-10-21 · 更新于 2026-06-24

今天，我们推出一组新的 endpoint——`exacto`，它专注于提供更高的工具调用（tool-calling）准确率：通过把请求路由到一组在工具使用成功率上可测量地更高的 provider 子集来实现（[文档](https://openrouter.ai/docs/features/exacto-variant)）。

关于 LLM provider 准确率的猜测一直很多：同一家 provider 运行同一个模型，不同 provider 之间表现是否一致？理论上，相同的模型权重（在相同量化条件下）当然应该给出相同的结果。但实际上，把模型落地为生产级推理服务既复杂又充满细微差别，差异因此浮现。

OpenRouter 每月处理来自全球的数十亿请求，因此我们拥有独特的视角来观察这些差异、弄清到底发生了什么，并为用户提供高质量、无意外的体验。

## Provider 生态

在 OpenRouter，我们与各家 provider 建立的是长期、稳定的合作关系。我们定期与他们沟通，在 Slack 频道里交流，去他们办公室拜访，并持续分享反馈。这些是活跃的、贴身实时的真实关系。

我们相信没有任何一家 provider 会故意损害模型质量。他们是否努力压缩成本？当然。他们是否深挖 VLLM 和 SGLang 来榨取性能？是的。我们也确实在极少数情况下看到，随着推理引擎栈的调整，质量出现了下滑。但所有 provider 都非常认真地对待质量。当我们报告问题时，得到的都是聪明、敬业的专业人士的高度参与。我们的激励是一致的：我们是中立平台，致力于为推理消费者提供最佳体验，provider 们也是如此。

话虽如此，规模化运行推理并不容易，有些模型比其他模型更难托管，而且错误在所难免。我们看到行业专家的评测报告，查看我们自己的数据，也听到客户关于各家 provider 输出质量存在定性差异的反馈：显然，我们需要做更多工作，以确保在 OpenRouter 上获得尽可能好的体验。

## 基准测试

Artificial Analysis 在 gpt-oss-120b 发布后不久[公布](https://x.com/ArtificialAnlys/status/1955102409044398415)了一组针对它的出色基准测试，显示各家 provider 在某一特定基准上存在显著差异：
 ![](https://imagedelivery.net/Xq3eUzdKO2-MoBklzEEuMQ/1552a4f1-5d60-4bfb-d2ce-1a8974a0d000/public) 性能差异确实显著。但重要的是，这款模型于 2025 年 8 月 5 日发布，而 Artificial Analysis 的这份数据来自 8 月 11 日。我们亲身体会到，provider 需要一些时间来"烧机"（burn in）一个新模型，让它在自己的硬件和推理引擎栈上真正运转起来。我们见过太多次了——从 R1 到 Kimi K2，随着 provider 打磨推理引擎，性能会不断提升。我们的直觉是这种差距会收窄，而事实上，截至 2025 年 9 月，数据变成了[这样](https://artificialanalysis.ai/models/gpt-oss-120b/providers#evaluations)：

![](https://imagedelivery.net/Xq3eUzdKO2-MoBklzEEuMQ/18a26677-6ede-49b0-ab3a-b57ad5433b00/public)

差距已经明显收窄，OpenRouter 上的大部分 provider 在基准测试上表现相近。

我们与 Artificial Analysis 合作，对 Deepseek 3.1——一款已经发布许久的模型——跑了基准测试。同样，我们看到的是一个很窄的性能区间：

![](https://imagedelivery.net/Xq3eUzdKO2-MoBklzEEuMQ/f1acf24f-0b51-4893-32e9-a43167046300/public)

值得注意的是，即使是 Deepinfra——唯一一家把模型量化到 fp4 的 provider——也颇具竞争力。

接下来，我们将：

- 在新开放权重模型可用后不久对各 provider 进行基准测试
- （私下）与 provider 分享结果
- 把任何落在可接受范围之外的 provider 从路由轮换中移除
- 待性能问题解决后再将其加回

## 工具调用数据

2025 年 8 月，我们开始推出额外的质量遥测数据，聚焦于工具调用和结构化输出。具体来说，对 OpenRouter 上*每一次* `tool_call` 响应，我们检查三种可能的失败模式：

- LLM 返回的 `tool_call` 是合法的 json 吗？
- `tool_call` 中的工具名是否存在于原始的 tools 输入中？
- `tool_call` 的 schema 是否与所提供工具的 schema 匹配？

这让我们能够针对同一模型，在不同 provider 之间比较工具调用的准确率和调用倾向。由于某些 provider 的使用方式可能存在偏差，我们对大客户做了降采样、跨 provider 比较单一应用各自的准确率，并核查 schema 复杂度是否可比。总体上，我们已测量了数十亿次 LLM 工具调用的准确率。

例如，下面是 DeepSeek Terminus 前五名 provider 的工具调用准确率（都非常优秀！）。

![](https://imagedelivery.net/Xq3eUzdKO2-MoBklzEEuMQ/3b059e35-430c-4035-4342-13d2ce55a600/public)

此外，我们还测量：在输入中提供了工具的前提下，模型与各 provider 请求使用工具的频率。我们暂不公开完整数据集，因为想先与 provider 合作弄清差异的来源。下面是 Kimi K2 部分 provider 之间工具调用*倾向*（propensity）差异的一个例子。这与 [Moonshot 发布的内容](https://x.com/kimi_moonshot/status/1976926483319763130?s=46)类似——但基于真实使用而非基准测试。

![](https://imagedelivery.net/Xq3eUzdKO2-MoBklzEEuMQ/0ec36b6b-a920-4301-3b7e-648b45223f00/public)

虽然这里只分享了一部分样本数据，但完整数据集清楚地表明：LLM 使用工具的*倾向*以及这些工具调用的*准确率*，在不同 provider 之间的差异远比标准基准测试所显示的要大。

## 实时的用户偏好

除了测量到的工具调用数据，我们还能获得另一类数据：provider 偏好。

OpenRouter 支持忽略（ignore）某些 provider，我们可以把这解读为一票——表示该 provider 没有满足这位客户的需求。

```
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{
    "model": "meta-llama/llama-3.3-70b-instruct",
    "messages": [
      {"role": "user", "content": "What is the capital of France?"}
    ],
    "provider": {
      "ignore": ["omega"]
    }
  }'
```

总体而言，每个模型都积累了几千条 provider 偏好设置，我们还可以进一步把它们限定在提供了工具的 LLM 生成请求上。这是判断哪些 provider 表现好、哪些表现差的强大信号。

## 推出 Exacto

利用我们的工具调用数据、客户 provider 偏好数据，以及在 [Groq OpenBench](https://github.com/groq/openbench) 上运行的工具调用基准，我们创建了一组全新的、经过精选的 endpoint，专门聚焦于工具调用准确率。它们今天即可使用，我们称之为 exacto。

首发提供以下模型的 exacto endpoint：

- [Kimi K2](https://openrouter.ai/moonshotai/kimi-k2-0905:exacto)（`moonshotai/kimi-k2-0905:exacto`）
- [DeepSeek v3.1 Terminus](https://openrouter.ai/deepseek/deepseek-v3.1-terminus:exacto)（`deepseek/deepseek-v3.1-terminus:exacto`）
- [GLM 4.6](https://openrouter.ai/z-ai/glm-4.6:exacto)（`z-ai/glm-4.6:exacto`）
- [GPT-OSS 120b](https://openrouter.ai/openai/gpt-oss-120b:exacto)（`openai/gpt-oss-120b:exacto`）
- [Qwen3 Coder](https://openrouter.ai/qwen/qwen3-coder:exacto)（`qwen/qwen3-coder:exacto`）

你可以通过 `model_slug:exacto` 使用这些新 endpoint。例如：

```
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{
    "model": "moonshotai/kimi-k2:exacto",
    "messages": [
      {"role": "user", "content": "What is the capital of France?"}
    ]
  }'
```

你会被路由到满足以下全部条件的 provider 之一：

- 在工具调用准确率方面属于头部 provider
- 工具调用倾向处于正常范围内
- 在工具调用场景下*没有*被 OpenRouter 用户频繁忽略或拉黑

在运行我们的内部工具调用评测套件，以及 [tau2-Bench](https://github.com/sierra-research/tau2-bench) 和 [LiveMCPBench](https://arxiv.org/html/2508.01780v1) 等开源基准时，我们观察到工具调用失败的发生率可测量地更低，模型也更能可靠地利用分派给它的工具。基准测试（本例中是 Kimi K2 0905）显示，通过 `exacto` 工具调用成功率有实质性提升：

![](https://imagedelivery.net/Xq3eUzdKO2-MoBklzEEuMQ/5a1d1b5d-71e4-4918-38e1-f7dde6c8ab00/public)

我们预计这些 endpoint 会在许多 agentic 工作流中大受欢迎，也预计会与目前未进入 Exacto 路由池的 provider 合作，帮助他们改进，最终达到纳入标准。请注意，exacto endpoint *专门聚焦于工具调用*，不应被视为对 endpoint 或 provider 整体质量的更广泛评判。

最后，我们正在努力将更多数据公开；预计在今年年底前会公开一部分底层数据，帮助用户做出更明智的决策。由于这些都是新发现，在发布完整数据集之前，我们希望先给某些 provider 改进的机会（或对我们的方法论提出反馈）。

## 结语

虽然我们回答了一些问题，但也怀疑这份分析会引出更多问题。我们期待听取反馈，并预计会有大量后续讨论。请到 [X](https://x.com/openrouterai) 或 [Discord](https://discord.gg/openrouter) 上联系我们参与讨论。如果你对某家 provider 在 exacto 下有具体反馈，请填写[这个表单](https://openrouter.notion.site/2932fd57c4dc8097ba74ffb6d27f39d1?pvs=105)。

希望用户觉得 Exacto endpoint 有用。在今年余下的时间里，我们也很期待分享更多数据（无论是基准测试还是实证数据），并将其融入我们的产品。
