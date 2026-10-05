---
vendor: xai_grok
title: Grok Build 现已开源
original_title: Grok Build is Now Open Source
url: https://x.ai/news/grok-build-open-source
date: 2026-07-15
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Grok Build 现已开源

探索我们编码智能体与 TUI 背后的 harness。

View on GitHub

Try Grok Build

我们正在开源 Grok Build——SpaceXAI 的编码智能体与 TUI。源代码现已在 [GitHub](https://github.com/xai-org/grok-build) 开放。

公开代码是迈向健壮可靠 harness 的最直接方式。你可以阅读源码，看清它究竟如何工作——从上下文组装到工具调用分发。

开源也让 harness 更容易被探索和扩展：如果你在使用 skills、插件、hooks、MCP 服务器或子智能体，源码就是每一种机制如何加载与调用的权威参考。

最后，Grok Build 现在可以完全 local-first 运行：自己编译，指向你自己的本地推理服务，一切通过你的 `config.toml` 驱动。

## [关于代码库](https://x.ai/news/grok-build-open-source#about-the-codebase)

公开的源码包括：

- 智能体循环：如何组装上下文、如何解析模型响应、如何分发工具调用
- 工具：智能体如何读取、编辑和搜索代码，如何运行命令
- 终端 UI：渲染、输入处理、计划审阅和内联 diff 查看器
- 扩展系统：skills、插件、hooks、MCP 服务器和子智能体

在 [GitHub](https://github.com/xai-org/grok-build) 上探索源码。

## 开始使用

View on GitHub

Get Grok Build
