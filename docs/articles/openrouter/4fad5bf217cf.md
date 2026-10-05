---
vendor: openrouter
title: 所有模型一致的 Web 搜索与抓取
original_title: Consistent Web Search and Fetch Across Every Model
url: https://openrouter.ai/blog/announcements/agentic-web-tools
date: 2026-05-07
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

介绍 `openrouter:web_search` 和 `openrouter:web_fetch`——两个任何模型都能在请求期间调用的新工具。当模型决定使用其一，OpenRouter 会在服务端执行并把结果返回给模型，无需任何客户端实现。

- **Web Search**：一个用于 agentic 搜索的工具，每个请求可搜索 0 到 N 次，由模型自己选择查询词和时机。
- **Web Fetch**：一个从任意 URL 获取完整页面内容的工具，常用于抓取搜索中找到的页面。

现在就在 [chatroom](https://openrouter.ai/chat) 中点击工具图标 ![tool icon](https://openrouter.ai/blog/images/web-tools-tool-icon.png) 试用，并[阅读文档](https://openrouter.ai/docs/guides/features/server-tools)了解 API 细节。

## 换模型不换工具

每家模型服务商都有自己内建的 web 搜索工具，schema 各不相同。换模型或换服务商，你就得重写搜索结果的定义、配置和解析方式。而且你不一定拥有相同的行为可用——如果你需要严格强制的屏蔽域名这类特性，这会是个问题。

这些新的服务端工具给你一种启用搜索与抓取的一致方式。指定一次 `{"type": "openrouter:web_search"}`，工具定义、调用和结果格式在所有支持 tool calling 的模型上保持完全一致。如果你连搜索行为也要一致，可以指定 Exa 或 Parallel 这样的服务商，这样无论请求路由到 GPT-5.5、Claude 还是 Kimi，返回给模型的结果都一致。

```
{
  "model": "openai/gpt-5.5",
  "messages": [{ "role": "user", "content": "What happened in tech news today?" }],
  "tools": [
    { "type": "openrouter:web_search" },
    { "type": "openrouter:web_fetch" }
  ]
}
```

## Web Search

Web 搜索支持四种引擎：

| Engine | How it works | Pricing |
| --- | --- | --- |
| **Auto**（默认） | 服务商支持则用 native，否则用 Exa | 视情况 |
| **Native** | 服务商内建搜索（OpenAI、Anthropic、Google、xAI、Perplexity） | 按服务商定价 |
| **[Exa](https://exa.ai)** | 把搜索传给 [Exa](https://exa.ai)，从你的 OpenRouter 额度扣费 | 每请求 $0.005，含最多 10 条结果，之后每条结果加收 $0.001。 |
| **[Parallel](https://parallel.ai)** | 把搜索传给 [Parallel](https://parallel.ai)，从你的 OpenRouter 额度扣费 | 每请求 $0.005，含最多 10 条结果，之后每条结果加收 $0.001。 |

各引擎所长不同。Native 搜索与服务商的模型深度集成。Exa 和 Parallel 支持配置结果上下文大小（`search_context_size`），native 引擎会忽略此项。多数引擎支持域名过滤（`allowed_domains`、`excluded_domains`）。

你可以在 chatroom UI 中或通过 API 配置：

```
{
  "type": "openrouter:web_search",
  "parameters": {
    "engine": "exa",
    "max_results": 5,
    "search_context_size": "high",
    "allowed_domains": ["arxiv.org", "nature.com"]
  }
}
```

## Agentic 循环中的并行搜索

当模型需要跨来源比较信息时，可以在一次请求中并发多次搜索。像“比较排名前三的云 GPU 服务商的价格”这样的触发的可能是三次各自使用不同查询词的独立搜索，然后模型再综合作答。

![Parallel web searches running in the background in the OpenRouter chatroom](https://openrouter.ai/blog/images/web-tools-parallel-search.png)

用 `max_total_results` 为一个请求内所有搜索的累计结果设上限，让成本和上下文用量可预期：

```
{
  "type": "openrouter:web_search",
  "parameters": {
    "max_results": 5,
    "max_total_results": 15
  }
}
```

一旦触顶，模型收到的将是“已达上限”的消息，而不是再跑一次搜索。

## Web Fetch

Web fetch 让模型可以从 URL 获取完整页面内容，支持五种引擎。

| Engine | How it works | Pricing |
| --- | --- | --- |
| **Auto**（默认） | 支持则用 native，否则用 Exa | 视情况 |
| **Native** | 服务商内建 fetch | 按服务商定价 |
| **OpenRouter** | 由 OpenRouter 直接 HTTP 抓取 | 免费 |
| **[Exa](https://exa.ai)** | 内容抽取，输出干净的 markdown | 每次抓取 $0.001 |
| **[Parallel](https://parallel.ai)** | 通过 Parallel 的 extract API 进行高质量内容抽取 | 每次抓取 $0.001 |

把引擎指定为 Exa、Parallel 或 OpenRouter，可确保所有模型上 fetch 行为一致，包括用 `allowed_domains` 和 `blocked_domains` 限制模型可抓取的 URL。各服务商的 native fetch 能力不一，若需要这些参数跨模型被严格遵守，请选择上述引擎之一。

用 `max_content_tokens` 限制模型能收到多少内容（对会吃掉上下文窗口的大页面很有用）：

```
{
  "type": "openrouter:web_fetch",
  "parameters": {
    "engine": "openrouter",
    "max_content_tokens": 50000,
    "allowed_domains": ["docs.example.com", "api.example.com"],
    "blocked_domains": ["internal.example.com"]
  }
}
```

## 从 Web Search 插件迁移

此前，模型只能通过 [web 搜索插件](https://openrouter.ai/docs/guides/features/plugins/web-search)进行搜索，而它每个请求恰好只跑一次搜索，不管模型实际需要什么。模型对何时搜、搜什么、搜不搜都没有发言权。

迁移时，把请求体中的 `plugins` 换成 `tools`：

**之前**（插件）：

```
"plugins": [{ "id": "web" }]
```

**之后**（服务端工具）：

```
"tools": [{ "type": "openrouter:web_search" }]
```

服务端工具让模型自己决定何时、多频地搜索。一个注意点：服务端工具要求模型支持 tool calling。如果你当前的模型不支持工具，你需要换一个支持的，或继续使用插件。

我们准备了一份含完整细节的[迁移指南](https://openrouter.ai/docs/guides/features/server-tools/web-search#migrating-from-the-web-search-plugin)。
