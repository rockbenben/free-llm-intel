---
vendor: huggingface
title: Granite 4.0 Nano：模型究竟能做多小？
original_title: 'Granite 4.0 Nano: Just how small can you go?'
url: https://huggingface.co/blog/ibm-granite/granite-4-nano
date: 2026-09-14
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Granite 4.0 Nano：模型究竟能做多小？

今天我们很高兴分享 [Granite 4.0 Nano](https://huggingface.co/collections/ibm-granite/granite-40-nano-language-models)——迄今我们最小的模型，作为 IBM Granite 4.0 模型家族的一部分发布。这些模型面向边缘与端侧应用设计，在其体量下展现出卓越性能，代表了 IBM 持续打造强大、实用模型的承诺：完成任务并不需要几千亿参数。

与所有 [Granite 4.0 模型](https://huggingface.co/collections/ibm-granite/granite-40-language-models)一样，Nano 系列以 Apache 2.0 许可证发布，并在 vLLM、llama.cpp、MLX 等主流运行时上提供原生架构支持。这些模型使用了为最初 Granite 4.0 模型开发的相同改进训练方法、训练管道和超过 15T token 的训练数据。本次发布包含受益于 Granite 4.0 [全新高效混合架构](https://www.ibm.com/new/announcements/ibm-granite-4-0-hyper-efficient-high-performance-hybrid-models#The+Granite+4+architecture)的变体；与所有 Granite 语言模型一样，Granite 4.0 Nano 也带有 IBM 的 [ISO 42001 认证](https://www.ibm.com/new/announcements/ibm-granite-iso-42001)，证明其负责任的模型开发，让用户对模型按全球标准构建和治理更有信心。

具体而言，Granite 4.0 Nano 包含 4 个 instruct 模型及其对应的 base 模型：

- **Granite 4.0 H 1B** – 约 15 亿参数的稠密 LLM，采用基于混合 SSM 的架构。
- **Granite 4.0 H 350M** – 约 3.5 亿参数的稠密 LLM，采用基于混合 SSM 的架构。
- **Granite 4.0 1B 与 Granite 4.0 350M** – 我们 1B 和 350M Nano 模型的传统 transformer 替代版本，用于支持混合架构尚未优化的工作负载（如 Llama.cpp）。

构建亚十亿到约十亿参数的模型是一个活跃且竞争激烈的领域，近期众多模型开发者如 Alibaba（Qwen）、LiquidAI（LFM）、Google（Gemma）等都在性能和架构上取得进展。与这些模型相比，Granite 4.0 Nano 展示了用极小参数规模可获得的能力显著提升——这一点通过涵盖通用知识、数学、代码和安全领域的系列通用基准得到衡量。

[![granite-4-nano-chart1](https://cdn-uploads.huggingface.co/production/uploads/65c1173865086cabf46fe1b9/vx93cgRtkLdDvirdCGF18.png)](https://cdn-uploads.huggingface.co/production/uploads/65c1173865086cabf46fe1b9/vx93cgRtkLdDvirdCGF18.png) *Chart 1. Average accuracy of 0.2B–2B parameter models across Knowledge, Math, Code, and Safety benchmarks. See Appendix I for full details.*

除了更通用的基准，在 agentic 工作流至关重要的任务上——包括指令遵循和工具调用（由 IFEval 和伯克利 Function Calling Leaderboard v3（BFCLv3）基准衡量）——Granite Nano 模型也超越了多个同规模模型。

[![granite-4-nano-chart2](https://cdn-uploads.huggingface.co/production/uploads/65c1173865086cabf46fe1b9/Xzmabcv6MzAvGapHFhXg4.png)](https://cdn-uploads.huggingface.co/production/uploads/65c1173865086cabf46fe1b9/Xzmabcv6MzAvGapHFhXg4.png) *Chart 2. Accuracy on IFEval and BFCLv3 benchmarks.*

Granite 4.0 Nano 的完整细节见 [Hugging Face 模型卡](https://huggingface.co/collections/ibm-granite/granite-40-nano-language-models)。未来，随着我们持续壮大 Granite 4.0 家族、努力让 AI 成为对开发者更高效实用的工具，请期待 IBM 的更多发布。

*附录 I. 通用性能基准明细* [![granite-4-nano-chart3](https://cdn-uploads.huggingface.co/production/uploads/65c1173865086cabf46fe1b9/8fdBK5XHiGvsaEkvqzLq4.png)](https://cdn-uploads.huggingface.co/production/uploads/65c1173865086cabf46fe1b9/8fdBK5XHiGvsaEkvqzLq4.png)
