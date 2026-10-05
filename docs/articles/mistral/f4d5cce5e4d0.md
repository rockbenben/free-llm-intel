---
vendor: mistral
title: Devstral
original_title: Devstral
url: https://mistral.ai/news/devstral
date: 2025-05-21
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

今天我们推出 Devstral，我们面向软件工程任务的 agentic LLM。Devstral 由 Mistral AI 与 [All Hands AI](https://www.all-hands.dev/) 合作打造 🙌，在 SWE-Bench Verified 上以大幅优势超越所有开源模型。我们以 Apache 2.0 许可证发布 Devstral。

![Devstral Swe](https://mistral.ai/_astro/a8f418f6-f7ee-4f21-8ab8-08bd76c37186_1KGqfr.webp?dpl=6abbd11780b53c00082eea6f)

## 面向软件开发的 Agentic LLM

典型 LLM 擅长写独立函数、代码补全这类原子级编码任务，但迄今难以解决真实世界的软件工程问题。真实开发需要把代码放进大型代码库的上下文中理解、识别彼此分散的组件之间的关系，并在错综复杂的函数中发现细微 bug。

Devstral 正是为解决这一问题而设计。Devstral 以解决真实 GitHub issue 为目标训练；它运行在 OpenHands 或 SWE-Agent 等代码 agent 脚手架之上，这些脚手架定义了模型与测试用例之间的接口。这里展示 Devstral 在流行的 SWE-Bench Verified 基准上的表现——该数据集包含 500 个经人工筛验正确性的真实 GitHub issue。

Devstral 在 SWE-Bench Verified 上取得 46.8% 的分数，比此前开源 SoTA 模型高出 6 个百分点以上。在同一测试脚手架（[All Hands AI](https://www.all-hands.dev/) 提供的 OpenHands 🙌）下评测时，Devstral 超越了 Deepseek-V3-0324（671B）和 Qwen3 232B-A22B 等远大于它的模型。

在下表中，我们还将 Devstral 与在各种（包括为模型定制的）脚手架下评测的闭源和开源模型进行比较。我们发现 Devstral 的表现显著优于多款闭源替代品。例如，Devstral 比新近发布的 GPT-4.1-mini 高出 20% 以上。

## 多面手：本地部署 ↔️ 企业使用 ↔️ 编码副驾

Devstral 足够轻量，可在单张 RTX 4090 或 32GB 内存的 Mac 上运行，是本地部署和端侧使用的理想选择。[OpenHands](https://github.com/All-Hands-AI/OpenHands) 等编码平台可以让模型与本地代码库交互，为 issue 提供快速解决方案。想亲自试用，请查看[文档](https://docs.all-hands.dev/modules/usage/llms/local-llms)或[教程视频](https://www.youtube.com/watch?v=oV9tAkS2Xic)。

模型的性能也使其成为企业中隐私敏感仓库上 agentic 编码的合适选择，尤其适用于有严格安全与合规要求的场景。

最后，如果你正在构建或使用 agentic 编码 IDE、插件或环境，Devstral 是加入你的模型选择器的好选择。

## 可用性

我们以 Apache 2.0 许可证免费发布此模型，供社区在其上构建、定制并加速自主软件开发。想亲自试用，请前往我们的[模型卡](https://huggingface.co/mistralai/Devstral-Small-2505)。

该模型也以 devstral-small-2505 之名在我们的 API 上提供，价格与 Mistral Small 3.1 相同：每百万输入 token $0.1，每百万输出 token $0.3。

若选择自托管，从今天起你可以在 [HuggingFace](https://huggingface.co/mistralai/Devstral-Small-2505)、[Ollama](https://ollama.com/library/devstral)、[Kaggle](https://www.kaggle.com/models/mistral-ai/devstral-small-2505)、[Unsloth](https://docs.unsloth.ai/basics/devstral)、[LM Studio](https://lmstudio.ai/model/devstral-small-2505-MLX) 下载模型。

如需在私有代码库上微调的企业部署，或更高保真的定制（如持续预训练、把 Devstral 的能力蒸馏进其他模型），请[联系我们](https://mistral.ai/contact)接洽我们的应用 AI 团队。

## 下一步

Devstral 是一个研究预览版，欢迎反馈！我们正在加紧构建一个更大的 agentic 编码模型，将于未来几周发布。

有意探讨我们如何帮助你的团队用上 Devstral，或了解我们的模型、产品与解决方案组合？[联系我们](https://mistral.ai/contact)，我们乐意效劳。
