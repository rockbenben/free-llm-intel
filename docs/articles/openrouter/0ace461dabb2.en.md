---
vendor: openrouter
title: Understand your AI usage: every agent, model, and request
original_title: Understand your AI usage: every agent, model, and request
url: https://openrouter.ai/blog/announcements/activity-dashboard
date: 2026-08-17
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 191530170379
---

# Understand your AI usage: every agent, model, and request

Cailee Moberg ·8/17/2026 · Updated 8/20/2026

Every company that spent the last two years deploying agents is now asking the same question: what are they costing us, and which ones are worth it? OpenRouter’s [Activity dashboard](https://openrouter.ai/activity) and [Analytics API](https://openrouter.ai/docs/api/api-reference/analytics/query-analytics-data) answer that question per agent, per model, per request.

Open [Activity](https://openrouter.ai/activity) to see how spend breaks down across agents, apps, and team members. Find out which models and tasks drive costs, and where caching cuts your bill. Create and save custom views, then drill from any chart down to the individual requests.

All of the data is available through the [Analytics API](https://openrouter.ai/docs/api/api-reference/analytics/query-analytics-data). Point your agent at the [openrouter-analytics skill](https://github.com/OpenRouterTeam/skills/tree/main/skills/openrouter-analytics) to dig into your usage, get a quick answer in your terminal, or pull the numbers into your own dashboards.

## Start with the big picture

[Overview](https://openrouter.ai/activity) is your usage at a glance. Five metrics at the top: total spend, requests, token volume, cache hit rate, and blended cost per million tokens, each with a sparkline and a comparison against the previous period. On the same screen, your top users and apps, spend by model, OpenRouter credits versus BYOK spend, request volume by model, prompt and completion token breakdown, and prompt caching.

![Activity Overview showing total spend, requests, token volume, cache hit rate, and blended cost per million tokens, with top users, top apps, and a stacked bar chart of daily usage by model](https://openrouter.ai/blog/images/activity-overview-summary.png)

![Four Activity Overview charts: BYOK versus OpenRouter spend over time, request volume by model, prompt, completion, and reasoning token breakdown, and cached versus uncached prompt tokens](https://openrouter.ai/blog/images/activity-overview-charts.png)

[Trends](https://openrouter.ai/activity/trends) takes the same data and sorts by movement instead of size, with a panel showing what’s rising and falling. See your trends across models, users, API keys, and apps. Use it to spot a runaway agent, a new model gaining traction, or a tool spreading across your org.

![Activity Trends showing spend over time by model and by user, with side panels ranking which models and users are rising or falling](https://openrouter.ai/blog/images/activity-trends-models-users.png)

![Activity Trends showing spend over time by API key and by app, with side panels ranking which keys and apps are rising or falling](https://openrouter.ai/blog/images/activity-trends-keys-apps.png)

## Explore any question

Every card on Overview and Trends links into [Explore](https://openrouter.ai/activity/explore), where you assemble the view yourself:

- **Metric**: spend, request count, tokens (prompt, completion, reasoning, or cached), cache hit rate, blended cost per million tokens, BYOK versus credit spend, or latency and throughput down to P50/P90/P99
- **Group by** (up to two dimensions): model, variant, provider, API key, app, user, workspace, origin, country, data region, finish reason, context length, session, generation, custom user IDs, or any [classifier](https://openrouter.ai/docs/guides/features/classifiers) dimension you’ve defined
- **Rollup**: minute, hour, day, week, or month, or drop the time axis for a ranked table
- **Chart type**: bar, line, or dot plot

Use it to see which apps are driving usage in each workspace, which models your agents are using for each task type, or how your provider latency is trending over time.

![Activity Explore showing total usage grouped by workspace and app, as a stacked bar with a ranked table of workspace and app pairs](https://openrouter.ai/blog/images/activity-explore-workspace-app.png)

![Activity Explore showing request count grouped by task family and model for a single workspace, with a ranked table of task and model pairs](https://openrouter.ai/blog/images/activity-explore-task-model.png)

![Activity Explore showing average latency by provider as weekly line charts across ten providers](https://openrouter.ai/blog/images/activity-explore-provider-latency.png)

Save your go-to views. Open the options menu, choose **Save current chart**, and name it. In an organization you also choose who sees it: **Only me**, or **Everyone in my organization**.

![The Activity Explore options menu open over a chart, showing Show Other, Cumulative sum, chart type buttons, Download CSV, Download PDF, Save current chart, and Saved charts](https://openrouter.ai/blog/images/activity-explore-chart-menu.png)

**Download CSV** or **Download PDF** to send any chart’s data straight into a spreadsheet or report.

[Guardrails](https://openrouter.ai/activity/guardrails) shows what your prompt injection and sensitive-information rules blocked, redacted, or flagged, and which rules are doing the work. Use it to monitor the rate of sensitive data entering your prompts, and which rules and data types are catching it. Filter by workspace or classifier to narrow in on where it’s coming from.

![Activity Guardrails showing two cards: blocked requests rejected before reaching the model, and redacted or flagged content broken down by sensitive info and prompt injection](https://openrouter.ai/blog/images/activity-guardrails-overview.png)

Expand a card to get the full breakdown, including which combinations of detected patterns drove each block, redaction, and flag.

![Expanded Redacted and Flagged card listing sensitive-information redactions by detected entity type, such as phone, person, location, IP address, and email](https://openrouter.ai/blog/images/activity-guardrails-detail.png)

## Click a chart, land in the logs

Aggregates show you that something got expensive. The next question is which requests.

Every chart and ranked table in Activity links through to the logs behind it. Click Tuesday’s bar, one model’s slice of a stacked chart, or a row in a ranked table, and you land in your [logs](https://openrouter.ai/logs) filtered to those requests.

![A stacked Usage by model chart in Activity with one day's bar selected, showing a popover offering View logs and Open in Explorer](https://openrouter.ai/blog/images/activity-chart-view-logs.png)

Open any row in [logs](https://openrouter.ai/logs) for the **Generation** detail view. It shows:

- **Cost**: upstream inference, caching, web search, and file processing, plus the discounts and cache savings applied
- **Performance**: provider latency, throughput, and time to first token
- **Routing**: which provider served the request, whether it fell back to another one, and the finish reason
- **Attribution**: the app, API key, and workspace behind it, plus session and request IDs and data region
- **Context**: any guardrail events, classifier tags, and the raw metadata

![Generation details panel open beside the logs list, showing provider latency, throughput, cost, token counts, model and canonical IDs, data policy, and the app, API key, request, session, and generation identifiers](https://openrouter.ai/blog/images/activity-generation-overview.png)

![Generation details panel showing a provider response waterfall for routing, provider call, and generation, with usage, classifications, prompt, completion, and raw JSON sections](https://openrouter.ai/blog/images/activity-generation-responses.png)

The **Prompt** detail view renders the full messages array and a flamegraph of estimated tokens per message colored by role: system, user, assistant, and tool. A conversation that costs three times what you expected usually shows it here as a wide band of tool calls or a heavy system prompt. The cached prefix is shaded, so you can see how far into the prompt the cache held and which message broke it.

![Prompt detail view for a 48-message generation, with a tokens-per-message flamegraph colored by role, cached and prompt token totals with cost, a per-role breakdown, a role filter over the message list, and the selected message's raw content](https://openrouter.ai/blog/images/activity-prompt-detail.png)

Per-message token counts are estimates derived from message size; the totals on the generation itself are recorded usage. Prompts and completions detail only exist if private input/output logging was enabled when the request ran, which you can enable in your workspace observability.

## Same data as Explore, via API

Everything in Explore is also available through the [Analytics API](https://openrouter.ai/docs/api/api-reference/analytics/query-analytics-data): let your agent run the analysis, get a quick answer in your terminal, or pull the numbers into your own dashboards. Analytics queries require a [management key](https://openrouter.ai/settings/management-keys). Two endpoints:

- [`GET /api/v1/analytics/meta`](https://openrouter.ai/docs/api/api-reference/analytics/get-available-analytics-metrics-and-dimensions) returns the currently supported metrics, dimensions, filter operators, and granularities. Call the metadata endpoint first to see what’s available; we’re always adding new metrics and dimensions.
- [`POST /api/v1/analytics/query`](https://openrouter.ai/docs/api/api-reference/analytics/query-analytics-data) runs the query and returns the same aggregates the Explore charts are drawn from.

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

## For agents

The [cost control cookbook](https://openrouter.ai/docs/cookbook/administration/analytics-cost-control) puts your agent in charge of spend analysis. Give your coding agent a management key and the [openrouter-analytics skill](https://github.com/OpenRouterTeam/skills/tree/main/skills/openrouter-analytics) and have it run a cost review on your OpenRouter account. It finds the models costing a multiple of your blended rate per million tokens, traces them back to the keys and pipelines responsible, and returns ranked recommendations.

We ran this internally and found a preview model burning ~$6.2K/month at roughly 25x the org’s blended rate. One drill-down query later, 98% of it traced to a single batch-pipeline key running a task that never needed a frontier model. The fix was a one-line model swap. See the query recipes and agent prompts we used in the [cookbook](https://openrouter.ai/docs/cookbook/administration/analytics-cost-control).

## Get started

[Open Activity](https://openrouter.ai/activity), or start in [Explore](https://openrouter.ai/activity/explore) if you already know the question you want answered. To work from your terminal instead, grab a [management key](https://openrouter.ai/settings/management-keys) and hit the [Analytics API](https://openrouter.ai/docs/api/api-reference/analytics/query-analytics-data).

Tell us what you’d like to see next in [#feedback](https://discord.gg/fVyRaUDgxW) on Discord.
