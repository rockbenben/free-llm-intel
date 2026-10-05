---
vendor: openrouter
title: Consistent Web Search and Fetch Across Every Model
original_title: Consistent Web Search and Fetch Across Every Model
url: https://openrouter.ai/blog/announcements/agentic-web-tools
date: 2026-05-07
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 5650587c239a
---

# Consistent Web Search and Fetch Across Every Model

David Bai ·5/7/2026 · Updated 6/24/2026

Introducing `openrouter:web_search` and `openrouter:web_fetch`, two new tools that any model can call during a request. When a model decides to use one, OpenRouter executes it server-side and returns the result to the model without requiring any client-side implementation.

- **Web Search**: a tool for agentic search 0 to N times per request, letting the model choose its own queries and timing.
- **Web Fetch**: a tool for retrieving full page content from any URL. Commonly used for pages found during search.

Try it now in the [chatroom](https://openrouter.ai/chat) by clicking the tool icon ![tool icon](https://openrouter.ai/blog/images/web-tools-tool-icon.png) and [read the docs](https://openrouter.ai/docs/guides/features/server-tools) for the API details.

## Swap Models Without Swapping Tools

Each model provider has its own built-in web search tool with a different schema. Switch models or providers, and you’re stuck rewriting how you define, configure, and parse search results. You’re also not guaranteed to have the same behaviors available, which can be problematic if you need features like strictly enforced blocked domains.

These new server tools give you one consistent way of enabling search and fetch. Specify `{"type": "openrouter:web_search"}` once, and the tool definition, invocation, and result format stay identical across all tool-calling models. If you want identical search behavior as well, you can specify a provider like Exa or Parallel so the results coming back to the model are consistent regardless of whether the request routes to GPT-5.5, Claude, or Kimi.

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

Web search supports four engines:

| Engine | How it works | Pricing |
| --- | --- | --- |
| **Auto** (default) | Uses native if the provider supports it, otherwise Exa | Varies |
| **Native** | The provider’s built-in search (OpenAI, Anthropic, Google, xAI, Perplexity) | Provider pricing |
| **[Exa](https://exa.ai)** | Passes the search to [Exa](https://exa.ai) and bills from your OpenRouter credits | $0.005 per request. Includes up to 10 results, then $0.001 per additional result. |
| **[Parallel](https://parallel.ai)** | Passes the search to [Parallel](https://parallel.ai) and bills from your OpenRouter credits | $0.005 per request. Includes up to 10 results, then $0.001 per additional result. |

Each engine has different strengths. Native search is tightly integrated with the provider’s model. Exa and Parallel add configurable result context size (`search_context_size`), which native engines ignore. Most engines support domain filtering (`allowed_domains`, `excluded_domains`).

You can configure this in the chatroom UI or via the API:

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

## Parallel Searches in Agentic Loops

When a model needs to compare information across sources, it can fire multiple searches in a single request. A question like “compare the pricing of the top 3 cloud GPU providers” might trigger three separate searches, each with different queries, before the model synthesizes an answer.

![Parallel web searches running in the background in the OpenRouter chatroom](https://openrouter.ai/blog/images/web-tools-parallel-search.png)

Use `max_total_results` to cap cumulative results across all searches in a request. This keeps costs and context usage predictable:

```
{
  "type": "openrouter:web_search",
  "parameters": {
    "max_results": 5,
    "max_total_results": 15
  }
}
```

Once the cap is hit, the model gets a message saying the limit was reached instead of running another search.

## Web Fetch

Web fetch lets models retrieve full page content from URLs and comes with five supported engines.

| Engine | How it works | Pricing |
| --- | --- | --- |
| **Auto** (default) | Uses native if supported, otherwise Exa | Varies |
| **Native** | The provider’s built-in fetch | Provider pricing |
| **OpenRouter** | Direct HTTP fetch by OpenRouter | Free |
| **[Exa](https://exa.ai)** | Content extraction and clean markdown output | $0.001 per fetch |
| **[Parallel](https://parallel.ai)** | High-quality content extraction via Parallel’s extract API | $0.001 per fetch |

Specifying Exa, Parallel, or OpenRouter as the engine ensures consistent fetch behavior across all models, including the ability to restrict which URLs the model can fetch using `allowed_domains` and `blocked_domains`. Native provider fetch capabilities vary, so choose one of these engines if you need the parameters to be respected across models.

Use `max_content_tokens` to cap how much content the model receives (useful for large pages that would eat your context window):

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

## Migrating From the Web Search Plugin

Until now, models could only search through the [web search plugin](https://openrouter.ai/docs/guides/features/plugins/web-search), which ran exactly one search per request regardless of what the model actually needed. The model had no say in when to search, what to search for, or whether to search at all.

To migrate, replace `plugins` with `tools` in your request body:

**Before** (plugin):

```
"plugins": [{ "id": "web" }]
```

**After** (server tool):

```
"tools": [{ "type": "openrouter:web_search" }]
```

Server tools let the model decide when and how often to search. One caveat: server tools require a model that supports tool calling. If your current model doesn’t support tools, you’ll need to switch to one that does or keep using the plugin.

We’ve created a [migration guide](https://openrouter.ai/docs/guides/features/server-tools/web-search#migrating-from-the-web-search-plugin) with full details.
