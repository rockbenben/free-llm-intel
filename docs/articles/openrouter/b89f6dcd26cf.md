---
vendor: openrouter
title: 零数据保留（ZDR）：对 AI API 意味着什么
original_title: Zero Data Retention (ZDR): What It Means for AI APIs
url: https://openrouter.ai/blog/insights/zero-data-retention
date: 2026-09-11
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 07dec6a0b862
translator: agent
---

# 零数据保留（ZDR）：对 AI API 意味着什么

OpenRouter ·9/11/2026 · 更新于 9/24/2026

[零数据保留（ZDR）](https://openrouter.ai/docs/guides/features/zdr)的意思是：AI 提供商处理你的提示词、返回一个响应，此后不再存储它。这是一条**保留**承诺。它不保证数据留在你的网络内、管不了你的应用记什么日志，也不自动覆盖挂在请求上的第三方工具。

本文解释 ZDR 覆盖什么、不覆盖什么，以及如何在你的 API 调用上强制执行它。

## 太长不看

- ZDR 阻止符合条件的推理提供商保留你的提示词和响应。
- 你的数据仍然会到达提供商、仍然会被模型处理。
- 在 OpenRouter 上，你可以通过账户设置、guardrails 或 `provider.zdr` 请求字段来强制执行 ZDR。
- ZDR 管的是提供商推理。你的日志、启用的工具、插件和其他存储类功能需要各自独立的控制。

## 什么是零数据保留（ZDR）？

[零数据保留是一种数据处理政策](https://openrouter.ai/docs/guides/features/zdr)：AI 提供商处理你的请求，但不持久化提示词或响应。ZDR 管的是提供商侧的保留。它不意味着你的数据留在你的网络里，也不意味着请求涉及的每个服务都遵循同一政策。

我们按端点级别评估数据政策，因为一家提供商的总体政策可能与挂在某个具体模型端点上的政策不同。当我们无法确认某个端点的政策时，采取保守立场，把它归类为"会保留数据并可能用于训练"。

ZDR 回答的是三个独立问题中的一个：

- **静态存储保留**：提供商是否在响应返回之后还存储提示词和响应。ZDR 管这个。
- **传输中的数据**：你的请求仍然要发往提供商，模型仍然要处理它。ZDR 不改变这一点。
- **用数据训练**：提供商是否用你的输入来改进它的模型。这是另一条独立的控制，尽管提供商常把它和 ZDR 配对提供。

"不训练"政策不一定等于 ZDR。提供商可能承诺不拿你的数据训练，但出于其他原因临时保留它。反向关系更强：一个不保留你数据的端点，之后也就无法用那份数据做训练。

ZDR 路由也和我们自己的日志政策分开。除非你主动开启[输入输出日志](https://openrouter.ai/docs/guides/features/input-output-logging)，我们不会存储提示词或响应内容。我们会保留请求元数据——token 数、延迟、模型、成本——以便你查看用量和活动信息。

## ZDR 覆盖什么、不覆盖什么

ZDR 有一条明确的边界。它覆盖符合条件的推理端点上的提供商侧保留，不会变成你的请求所触及的全部系统的通用隐私政策。

| **数据处理问题** | **ZDR 覆盖吗？** | **含义** |
| --- | --- | --- |
| 提供商在推理后存储你的提示词 | 覆盖 | ZDR 端点不持久化提示词 |
| 提供商存储模型响应 | 覆盖 | ZDR 端点不持久化补全 |
| 提供商拿被保留的提示词训练 | 被间接阻止 | 根本没有可用来训练的保留提示词 |
| 数据到达了模型 | 不覆盖 | 提供商必须处理输入才能生成响应 |
| 处理发生在某个特定国家或地区 | 不覆盖 | 请用数据驻留或[域内路由](https://openrouter.ai/docs/guides/features/in-region-routing) |
| OpenRouter 存储请求元数据 | 不覆盖 | 元数据可以在不含提示词或响应内容的情况下被保留 |
| 你的应用记录提示词 | 不覆盖 | 你自己的日志和存储政策照旧生效 |
| 某个插件或工具保留数据 | 不覆盖 | 工具有自己的运营者和数据政策 |
| 端点为滥用或法务审查保留数据 | 不覆盖 | 我们不会把一个会保留的端点当作 ZDR |

"我们不拿你的数据训练"仍可能允许为了滥用检测或法律义务做临时保留。这样的端点不符合我们的 ZDR 定义。你在 no-training 政策下仍然可以用它，但别把该请求描述成零保留。

ZDR 强制执行也只作用于推理提供商路由。你启用的[网页搜索插件](https://openrouter.ai/docs/guides/features/plugins/web-search)、外部工具或其他服务，可以按其自身的保留条款接收请求数据。在有严格保留要求的工作流里使用它们之前，请单独审阅它们的政策。

你的应用是另一层保留来源。一个 ZDR 请求仍然可能在错误追踪系统、分析事件、数据库行或应用日志里留下一份完整的提示词。提供商侧的 ZDR 不会删除这些副本中的任何一个。

![ZDR 覆盖范围的示意图：请求从你的应用经 OpenRouter 流向一个 ZDR 提供商端点，提示词和响应在那里不被持久化；而应用日志、请求元数据、插件与工具、处理地区位于 ZDR 边界之外，需要各自的控制](https://openrouter.ai/blog/images/zero-data-retention-coverage.png)

### 缓存要单独检查

我们认为[提供商侧的内存内提示词缓存](https://openrouter.ai/blog/insights/is-implicit-caching-prompt-retention/)与 ZDR 兼容，因为提示词没有被写入持久存储。缓存表示在提供商内存中停留的时间，刚好够复用提示词、提升性能。

我们的[响应缓存功能](https://openrouter.ai/docs/guides/features/response-caching)行为不同，因为它会临时存储生成的响应。账户级 ZDR 会关闭响应缓存，但按请求的 `provider.zdr` 字段不影响响应缓存资格。要求每一层都零存储的系统，应当因此单独审查自己的响应缓存配置。

## ZDR 与相关 AI 隐私控制的区别

ZDR 是众多隐私控制中的一种，每种控制回答的问题不同。

### ZDR vs"不拿你的数据训练"

两者经常一起出现，但回答的问题不同。"不训练"管你的输入是否会改进模型；ZDR 管提供商在响应返回之后是否还存储这些输入。提供商可以承诺不训练你的数据，同时为了滥用检查或法律原因短暂持有。两个都需要，就两个都强制执行。

在 OpenRouter 上，`data_collection` 允许你按提供商是否做非短暂存储并可能训练来过滤。设为 `"deny"` 会排除这些端点。当你想让两个控制在请求中都明确时，它可以和 `zdr: true` 组合使用。

### ZDR vs 数据驻留与区域锁定

[区域锁定](https://openrouter.ai/blog/insights/ai-data-residency/)控制你的请求**在哪里**被处理——比如 GDPR 要求下限制在某个区域内；ZDR 控制数据事后**是否被留下**。提供商可能在 EU 内处理并保留请求，也可能在别处处理一个 ZDR 请求。

当政策既点名允许的处理地点、又有保留要求时，两个控制都要用。我们在 Business 和 Enterprise 计划上通过 `us.openrouter.ai` 和 `eu.openrouter.ai` 两个 API 域名提供美国和 EU 的[域内路由](https://openrouter.ai/blog/announcements/us-in-region-routing/)。这与 ZDR 强制执行是相互独立的。

### ZDR vs 自托管

自托管把推理留在你自己的基础设施里。选它之前，先看看这些控制是否已经满足你的要求：

- **区域锁定**：控制请求在哪里被处理。
- **ZDR 路由**：阻止提供商侧存储提示词和响应。
- **按 key 或按 workspace 的 guardrails**：把一个客户的流量和政策同另一个隔开。
- **你自己的日志**：记录发送了什么、去了哪里。

当政策禁止一切第三方处理——包括短暂推理本身——时，才需要自托管。

## 如何在 OpenRouter 上路由到符合 ZDR 的端点

提供商支持 ZDR，不等于每个请求都自动符合 ZDR。你必须在账户、guardrail 或请求层面强制这条政策。

### 隐私设置里的账户级强制执行

不碰代码就能对你账户的每个请求强制 ZDR——入口在账户的[隐私设置](https://openrouter.ai/settings/privacy)。ZDR 可以按模型组要求，覆盖 Anthropic、OpenAI、Google、SpaceXAI 和非前沿端点这几组，你可以对某些组要求、对其他组不要求。也可以通过 [guardrails](https://openrouter.ai/docs/guides/features/guardrails) 强制执行。详见[零数据保留指南](https://openrouter.ai/docs/guides/features/zdr)。

[数据政策过滤](https://openrouter.ai/docs/guides/privacy/provider-logging)是另一个独立的开关。它让你关闭为训练存储输入的提供商。在账户设置里选择退出训练，我们就不会把请求路由到拿你的数据训练的提供商。

### 用 zdr 路由控制做按请求强制执行

要请求级控制，在 `provider` 块里设置 `zdr` 字段。`zdr` 为 `true` 时，请求只路由到具有零数据保留政策的端点；为 `false` 或省略时，不影响路由。

```
{
  "model": "meta-llama/llama-3.3-70b-instruct",
  "messages": [{ "role": "user", "content": "Hello" }],
  "provider": {
    "zdr": true,
    "data_collection": "deny"
  }
}
```

相关的 [`data_collection`](https://openrouter.ai/docs/guides/routing/provider-selection) 控制取 `"allow"`（默认）或 `"deny"`。设为 `"deny"` 后，路由会排除非短暂存储用户数据并可能用其训练的端点。

按请求的 `zdr` 参数与你的全账户设置和 guardrail 设置按 OR 组合：任何一处打开 ZDR，强制执行就生效。请求级标记只能**确保** ZDR 开着，不能覆盖或放松账户级或 guardrail 规则。

![普通 chat completion 请求与同一请求加上包含 zdr true 和 data_collection deny 的 provider 块的并排对比：后者只路由到零数据保留端点](https://openrouter.ai/blog/images/zero-data-retention-request.png)

## 如何核验供应商的 ZDR 声明

检查这五点。

- **ZDR 到底覆盖哪些数据？**确认它是否包括提示词、补全、上传文件、工具输入、缓存表示和标识符。
- **政策是按提供商还是按端点生效？**模型功能和 API 端点可能有不同的存储要求。一句覆盖全提供商的声明可能藏了例外。
- **什么在政策之外？**问清元数据、插件、工具、提示词缓存、响应缓存、日志、批处理 API 和有状态功能。
- **ZDR 怎么强制执行？**找账户政策、guardrail 或请求级路由控制，而不是人工选提供商。
- **如何持续验证资格？**数据政策会变。我们维护端点级的政策信息，并在 `https://openrouter.ai/api/v1/endpoints/zdr` 公布当前的 ZDR 端点清单，路由决策因此能跟着现行政策走，而不是跟着一张静态表格。

## 结论

ZDR 降低的是提供商侧的存储风险，而且只有当你的请求到达合格端点时才成立。把它当作一条可强制执行的路由要求来对待。

处理敏感的推理流量时，把控制与实际政策逐条对上：保留问题用 ZDR，存储和训练限制用 `data_collection: "deny"`，处理地点重要时加域内路由。然后检查你的应用日志、启用的工具和缓存配置，别让另一层把你从提供商那里拿掉的数据重新造出来。

在我们的 API 上构建？从 [ZDR 文档](https://openrouter.ai/docs/guides/features/zdr)和[提供商路由](https://openrouter.ai/docs/guides/routing/provider-selection)控制开始，把你的调用限定在 ZDR 端点上。在为你的组织审查 AI 数据处理？看 [OpenRouter for Enterprise](https://openrouter.ai/enterprise)。

## 常见问题

### 什么是 ZDR（零数据保留）？

零数据保留的意思是 AI 提供商处理你的提示词并返回响应，之后不把任何一份持久化下来。ZDR 管的是合格端点上的提供商侧存储。它不阻止数据到达模型，不把请求留在你的网络内，也管不了你自己的系统创建的副本。

### 针对 AI 的零数据保留政策是什么？

零数据保留政策声明 AI 提供商在处理之后不会存储提示词或响应。政策应当写明哪些端点和功能符合、如何强制执行，以及元数据、缓存、工具和日志的去向。只有 no-training 政策并不能保证零保留。

### 什么是零保留 API？

零保留 API 在处理请求后、推理结束时不存储提示词或响应。在 OpenRouter 上，你可以把 `provider.zdr` 设为 `true`，把请求限定到合格端点。账户级隐私设置和 guardrails 可以在更大的请求群体上强制同一要求。

### 哪个 LLM 最适合隐私场景？

隐私取决于端点和路由政策，不只是模型名字。同一个模型可能通过保留规则不同的多家提供商可用。先在目录里筛出合格端点，再通过路由配置强制执行 ZDR、数据收集和驻留要求。
