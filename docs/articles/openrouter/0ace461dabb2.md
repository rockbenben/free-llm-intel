---
vendor: openrouter
title: 看懂你的 AI 用量：每个 agent、模型与请求
original_title: 'Understand your AI usage: every agent, model, and request'
url: https://openrouter.ai/blog/announcements/activity-dashboard
date: 2026-08-17
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# 看懂你的 AI 用量：每个 agent、模型与请求

过去两年部署 agent 的每一家公司，现在都在问同一个问题：它们花了我们多少钱，哪些是值得的？OpenRouter 的 [Activity 仪表盘](https://openrouter.ai/activity)和 [Analytics API](https://openrouter.ai/docs/api/api-reference/analytics/query-analytics-data)能够按 agent、按模型、按请求回答这个问题。

打开 [Activity](https://openrouter.ai/activity)，查看支出如何拆分到各个 agent、应用和团队成员。找出哪些模型和任务在推高成本，以及缓存在哪里削减了你的账单。创建并保存自定义视图，然后从任意图表下钻到单个请求。

所有数据都可以通过 [Analytics API](https://openrouter.ai/docs/api/api-reference/analytics/query-analytics-data) 获取。让你的 agent 对接 [openrouter-analytics skill](https://github.com/OpenRouterTeam/skills/tree/main/skills/openrouter-analytics)，深入分析你的用量、在终端里快速得到答案，或把数据拉进你自己的仪表盘。

## 从大局开始

[Overview](https://openrouter.ai/activity) 让你一眼看清用量。顶部有五项指标：总支出、请求数、token 总量、缓存命中率、每百万 token 混合成本，每项都带一条迷你趋势线以及与上一周期的对比。同一屏上还有你的 Top 用户和应用、按模型的支出、OpenRouter 额度与 BYOK 支出对比、按模型的请求量、prompt 与 completion token 拆分，以及 prompt 缓存。

![Activity Overview showing total spend, requests, token volume, cache hit rate, and blended cost per million tokens, with top users, top apps, and a stacked bar chart of daily usage by model](https://openrouter.ai/blog/images/activity-overview-summary.png)

![Four Activity Overview charts: BYOK versus OpenRouter spend over time, request volume by model, prompt, completion, and reasoning token breakdown, and cached versus uncached prompt tokens](https://openrouter.ai/blog/images/activity-overview-charts.png)

[Trends](https://openrouter.ai/activity/trends) 用同样的数据，但按变化幅度而非规模排序，并有一个面板显示哪些在上升、哪些在下降。查看模型、用户、API key 和应用维度的趋势。用它来发现失控的 agent、正在起量的新模型，或在组织内扩散的工具。

![Activity Trends showing spend over time by model and by user, with side panels ranking which models and users are rising or falling](https://openrouter.ai/blog/images/activity-trends-models-users.png)

![Activity Trends showing spend over time by API key and by app, with side panels ranking which keys and apps are rising or falling](https://openrouter.ai/blog/images/activity-trends-keys-apps.png)

## 探索任何疑问

Overview 和 Trends 上的每张卡片都会链接到 [Explore](https://openrouter.ai/activity/explore)，在那里由你自己组装视图：

- **Metric（指标）**：支出、请求数、tokens（prompt、completion、reasoning 或 cached）、缓存命中率、每百万 token 混合成本、BYOK 与额度支出对比，或精确到 P50/P90/P99 的延迟与吞吐
- **Group by（分组，最多两个维度）**：模型、variant、provider、API key、应用、用户、workspace、来源（origin）、国家、数据区域、结束原因（finish reason）、上下文长度、session、generation、自定义用户 ID，或任何你已定义的 [classifier](https://openrouter.ai/docs/guides/features/classifiers) 维度
- **Rollup（聚合粒度）**：分钟、小时、天、周或月，或去掉时间轴得到排名表
- **Chart type（图表类型）**：柱状图、折线图或点图

用它来看各 workspace 中哪些应用在驱动用量、你的 agent 对每类任务分别用了哪些模型，或你的 provider 延迟随时间的走势。

![Activity Explore showing total usage grouped by workspace and app, as a stacked bar with a ranked table of workspace and app pairs](https://openrouter.ai/blog/images/activity-explore-workspace-app.png)

![Activity Explore showing request count grouped by task family and model for a single workspace, with a ranked table of task and model pairs](https://openrouter.ai/blog/images/activity-explore-task-model.png)

![Activity Explore showing average latency by provider as weekly line charts across ten providers](https://openrouter.ai/blog/images/activity-explore-provider-latency.png)

保存你的常用视图。打开选项菜单，选择 **Save current chart**，命名即可。在组织中，你还要选择谁能看到它：**Only me**，或 **Everyone in my organization**。

![The Activity Explore options menu open over a chart, showing Show Other, Cumulative sum, chart type buttons, Download CSV, Download PDF, Save current chart, and Saved charts](https://openrouter.ai/blog/images/activity-explore-chart-menu.png)

用 **Download CSV** 或 **Download PDF** 把任意图表的数据直接发进电子表格或报告。

[Guardrails](https://openrouter.ai/activity/guardrails) 展示你的 prompt 注入与敏感信息规则拦截、脱敏或标记了什么，以及哪些规则在发挥作用。用它来监控敏感数据进入 prompt 的比率，以及哪些规则和数据类型在捕捉它们。按 workspace 或 classifier 过滤，可以聚焦问题的来源。

![Activity Guardrails showing two cards: blocked requests rejected before reaching the model, and redacted or flagged content broken down by sensitive info and prompt injection](https://openrouter.ai/blog/images/activity-guardrails-overview.png)

展开卡片可获得完整拆分，包括是哪些检测模式的组合导致了每一次拦截、脱敏和标记。

![Expanded Redacted and Flagged card listing sensitive-information redactions by detected entity type, such as phone, person, location, IP address, and email](https://openrouter.ai/blog/images/activity-guardrails-detail.png)

## 点一下图表，落到日志里

聚合数据告诉你某样东西变贵了。下一个问题是：哪些请求？

Activity 中的每张图表和排名表都会链接到背后的日志。点击周二的柱子、堆叠图中某个模型的那一块，或排名表中的一行，你就会落到已按这些请求过滤的 [logs](https://openrouter.ai/logs)。

![A stacked Usage by model chart in Activity with one day's bar selected, showing a popover offering View logs and Open in Explorer](https://openrouter.ai/blog/images/activity-chart-view-logs.png)

在 [logs](https://openrouter.ai/logs) 中打开任意一行，进入 **Generation** 详情视图。它展示：

- **Cost（成本）**：上游推理、缓存、web 搜索和文件处理，外加已生效的折扣和缓存节省
- **Performance（性能）**：provider 延迟、吞吐和首 token 时间
- **Routing（路由）**：哪个 provider 服务了该请求、是否回退到了另一个，以及结束原因
- **Attribution（归属）**：背后的应用、API key 和 workspace，外加 session 与请求 ID 及数据区域
- **Context（上下文）**：任何 guardrail 事件、classifier 标签和原始元数据

![Generation details panel open beside the logs list, showing provider latency, throughput, cost, token counts, model and canonical IDs, data policy, and the app, API key, request, session, and generation identifiers](https://openrouter.ai/blog/images/activity-generation-overview.png)

![Generation details panel showing a provider response waterfall for routing, provider call, and generation, with usage, classifications, prompt, completion, and raw JSON sections](https://openrouter.ai/blog/images/activity-generation-responses.png)

**Prompt** 详情视图会渲染完整的 messages 数组，以及一张按角色着色的每条消息估算 token 火焰图：system、user、assistant 和 tool。一段成本超出预期三倍的对话，通常会在这里以一大片 tool 调用或过重的 system prompt 现形。已缓存的前缀会被阴影标记，你可以看到缓存深入到 prompt 的哪个位置、是哪条消息打破了它。

![Prompt detail view for a 48-message generation, with a tokens-per-message flamegraph colored by role, cached and prompt token totals with cost, a per-role breakdown, a role filter over the message list, and the selected message's raw content](https://openrouter.ai/blog/images/activity-prompt-detail.png)

每条消息的 token 数是基于消息大小的估算值；generation 本身的总量才是记录的实测用量。只有当请求运行时启用了私有输入/输出日志，prompt 和 completion 的详情才会存在，你可以在 workspace 的可观测性设置中启用它。

## 同样的数据，通过 API 获取

Explore 里的一切也都可以通过 [Analytics API](https://openrouter.ai/docs/api/api-reference/analytics/query-analytics-data) 获取：让你的 agent 来做分析、在终端里快速得到答案，或把数据拉进你自己的仪表盘。Analytics 查询需要 [management key](https://openrouter.ai/settings/management-keys)。两个端点：

- [`GET /api/v1/analytics/meta`](https://openrouter.ai/docs/api/api-reference/analytics/get-available-analytics-metrics-and-dimensions) 返回当前支持的指标、维度、过滤操作符和聚合粒度。先调用元数据端点看看有什么可用；我们会不断新增指标和维度。
- [`POST /api/v1/analytics/query`](https://openrouter.ai/docs/api/api-reference/analytics/query-analytics-data) 执行查询，返回与 Explore 图表同源的同款聚合结果。

```
curl -X POST https://openrouter.ai/api/v1/analytics/query \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "metrics": ["total_usage", "tokens_total", "cache_hit_rate"],
    "dimensions": ["model"],
    "granularity": "day",
    "time_range": {"start": "2026-07-01T00:00:00Z", "end": "2026-08-01T00:00:00Z"},
    "limit": 20
  }'
```

## 面向 agent

[cost control cookbook](https://openrouter.ai/docs/cookbook/administration/analytics-cost-control) 把支出分析交给你的 agent。给你的编码 agent 一个 management key 和 [openrouter-analytics skill](https://github.com/OpenRouterTeam/skills/tree/main/skills/openrouter-analytics)，让它对你的 OpenRouter 账户跑一次成本审查。它会找出那些成本达到你每百万 token 混合成本数倍的模型，追溯到对应的 key 和流水线，并返回按优先级排序的建议。

我们在内部跑了这套流程，发现一个预览模型每月烧掉约 $6.2K，成本约为该组织混合成本的 25 倍。再一次下钻查询后发现，其中 98% 可追溯到一个批次流水线的 key，而它跑的任务根本不需要前沿模型。修复只需改一行模型配置。查询配方和我们用到的 agent 提示词见 [cookbook](https://openrouter.ai/docs/cookbook/administration/analytics-cost-control)。

## 开始使用

[打开 Activity](https://openrouter.ai/activity)，如果你已经知道要问什么问题，直接从 [Explore](https://openrouter.ai/activity/explore) 开始。想在终端里操作，就取一个 [management key](https://openrouter.ai/settings/management-keys)，调用 [Analytics API](https://openrouter.ai/docs/api/api-reference/analytics/query-analytics-data)。

想好下一个要看什么了？请到 Discord 的 [#feedback](https://discord.gg/fVyRaUDgxW) 告诉我们。
