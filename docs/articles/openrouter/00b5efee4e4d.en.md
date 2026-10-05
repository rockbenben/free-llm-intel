---
vendor: openrouter
title: Introducing Web Search via the API
original_title: Introducing Web Search via the API
url: https://openrouter.ai/blog/announcements/introducing-web-search-via-the-api
date: 2025-01-23
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 346e1433d207
---

# Introducing Web Search via the API

OpenRouter ·1/23/2025 · Updated 6/11/2026

The OpenRouter API now supports a **web search** feature, available for all models. This enables developers to fetch and integrate web search results directly into their message streams. By appending `:online` to the model slug or activating the `web` plugin, you can include relevant, up-to-date information in your workflows.

## Key Details

- **Default Behavior**: Fetches up to 5 web results per request.
- **Pricing**: $4 per 1,000 web results.
- **Integration Options**: Use the `web` plugin directly in your API requests, or the `:online` shortcut for easier setup.

### How it works

The web search plugin uses Exa.ai to retrieve results. Your prompt is passed to Exa, which executes relevant searches and summarizes the results. The results are then merged into a prompt. This is customizable (see below) but by default is:

> A web search was conducted on {todays_date}. Incorporate the following web search results into your response. IMPORTANT: Cite them using markdown links named using the domain of the source. Example: nytimes.com. [web search results are inserted here]

The plugin injects this as a **system message** before the user message in the request payload.

## Example Usage

Append `:online` to any model slug to enable web search.

```
{
  "model": "openai/gpt-4o:online"
}
```

This `:online` tag is simply shorthand for specifying the `web` plugin, which also works:

```
{
  "model": "openai/gpt-4o",
  "plugins": [{ "id": "web" }]
}
```

## Customization Options

The `web` plugin has two customization options:

- **Maximum Results**: Control the number of results with `max_results` (default: 5).
- **Custom Search Prompts**: Tailor the prompt used to integrate results into the conversation.

Example:

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

For more information, check the documentation or try it directly with OpenRouter Chat by toggling the ‘web’ icon on the model selector.
