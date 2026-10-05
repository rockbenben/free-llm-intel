---
vendor: openrouter
title: Introducing Presets: Manage LLM Configs from Your Dashboard!
original_title: Introducing Presets: Manage LLM Configs from Your Dashboard!
url: https://openrouter.ai/blog/announcements/introducing-presets-manage-llm-configs-from-your-dashboard
date: 2025-06-26
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 216387d56538
---

# Introducing Presets: Manage LLM Configs from Your Dashboard!

OpenRouter ·6/26/2025 · Updated 6/11/2026

We’re excited to launch **Presets**, a powerful new feature that lets you separate your LLM configuration from your code!
 Create, manage, and update model settings, system prompts, and routing rules directly from your OpenRouter dashboard.

## 🚀 Why Use Presets?

- Define model selection, provider routing, system prompts, and generation parameters all in one place.
- Easily A/B test models or parameters, or update prompts on the fly without code changes.
- Focus your codebase on product logic while offloading config complexity to your presets.

## 🛠️ How to Use Presets in API Calls

You can reference presets in a few flexible ways:

- Directly as a model: `model: @preset/your-preset-slug`
- With model override: `model: google/gemini-2.0-flash-001@preset/your-preset-slug`
- Using the new dedicated field: `preset: your-preset-slug`

## 📘 Docs & Details

[https://openrouter.ai/docs/features/presets](https://openrouter.ai/docs/features/presets)
