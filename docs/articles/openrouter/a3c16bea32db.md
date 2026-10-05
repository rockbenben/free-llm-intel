---
vendor: openrouter
title: 推出 Presets：在你的仪表盘管理 LLM 配置！
original_title: Introducing Presets: Manage LLM Configs from Your Dashboard!
url: https://openrouter.ai/blog/announcements/introducing-presets-manage-llm-configs-from-your-dashboard
date: 2025-06-26
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

我们很高兴推出 **Presets**——一项让你把 LLM 配置与代码分离的强大新功能！
直接在 OpenRouter 仪表盘上创建、管理和更新模型设置、system prompt 与路由规则。

## 🚀 为什么要用 Presets？

- 在一处定义模型选择、服务商路由、system prompts 和生成参数。
- 轻松对模型或参数做 A/B 测试，或无需改代码即可即时更新 prompt。
- 让代码库专注于产品逻辑，把配置的复杂度交给 presets。

## 🛠️ 如何在 API 调用中使用 Presets

你可以通过几种灵活方式引用 presets：

- 直接作为模型：`model: @preset/your-preset-slug`
- 带模型覆盖：`model: google/gemini-2.0-flash-001@preset/your-preset-slug`
- 使用新的专用字段：`preset: your-preset-slug`

## 📘 文档与详情

[https://openrouter.ai/docs/features/presets](https://openrouter.ai/docs/features/presets)
