---
vendor: openrouter
title: 通过 API 提供 Web 搜索
original_title: Introducing Web Search via the API
url: https://openrouter.ai/blog/announcements/introducing-web-search-via-the-api
date: 2025-01-23
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

OpenRouter API 现在支持 **web search** 功能，对所有模型可用。这让开发者可以直接把网页搜索结果抓取并整合进消息流。在模型 slug 后追加 `:online` 或启用 `web` 插件，你就能在工作流中加入相关的最新信息。

## 关键细节

- **默认行为**：每个请求抓取最多 5 条搜索结果。
- **定价**：每 1,000 条搜索结果 $4。
- **集成方式**：在 API 请求中直接使用 `web` 插件，或用 `:online` 快捷标记更简单地配置。

### 工作原理

web 搜索插件使用 Exa.ai 获取结果。你的 prompt 会传给 Exa，由它执行相关搜索并总结结果，随后结果被合并进一个 prompt。这一步可定制（见下文），默认为：

> A web search was conducted on {todays_date}. Incorporate the following web search results into your response. IMPORTANT: Cite them using markdown links named using the domain of the source. Example: nytimes.com. [web search results are inserted here]

该插件会把这条消息作为 **system message** 注入到请求负载中用户消息之前。

## 使用示例

在任意模型 slug 后追加 `:online` 即可启用 web 搜索。

```
{
  "model": "openai/gpt-4o:online"
}
```

`:online` 标记只是指定 `web` 插件的简写，下面这种写法同样有效：

```
{
  "model": "openai/gpt-4o",
  "plugins": [{ "id": "web" }]
}
```

## 定制选项

`web` 插件有两个定制项：

- **Maximum Results**：用 `max_results` 控制结果数量（默认：5）。
- **Custom Search Prompts**：定制用于把结果整合进对话的 prompt。

示例：

```
{
  "model": "openai/gpt-4o:online",
  "plugins": [
    {
      "id": "web",
      "max_results": 3,
      "search_prompt": "Consider these web results when forming your response:"
    }
  ]
}
```

更多信息请查看文档，或直接在 OpenRouter Chat 中切换模型选择器上的 ‘web’ 图标试用。
