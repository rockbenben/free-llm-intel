---
vendor: together_ai
title: 宣布完成 8 亿美元 C 轮融资，加速向开源 AI 的转变
original_title: "Announcing our $800M Series C to accelerate the shift to open-source AI"
url: https://www.together.ai/blog/announcing-our-series-c
date: 2026-07-01
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

四年前，我和联合创始人创立 Together AI，是因为我们看到了生成式 AI 是人类进步的转折点。我们相信，这项一代人一遇的技术应当是开放的、随处可得的，而不是被少数几家公司掌控。

自那以后，我们为开源 AI 构建了一个全栈 AI 平台，以前沿研究为根基，为 AI 应用和 agent 提供最快、最高效的推理。今天，Together AI 受到数千家客户的信赖，其中包括许多全球增长最快的 AI 公司，如 Cognition、Decagon、Eleven Labs、Cursor 和 Suno。那个关于 AI 未来的信念，其成长速度甚至超过了我们最乐观的预测。

今天，我很 high 兴地宣布我们旅程中的下一个里程碑：获得 [8 亿美元的 C 轮融资](https://www.nytimes.com/2026/07/01/business/dealbook/together-ai-funding.html?unlocked_article_code=1.uVA.wspf.9WMvlyMEhaBk&smid=nytcore-ios-share)，投资方阵容强大，包括 Aramco Ventures、NVIDIA、Vista Equity、General Catalyst、Emergence Capital、SE Ventures、Pegatron、Salesforce Ventures、March Capital、DTCP Growth、Lux Capital、Geodesic、PSP Partners 等。除股权资本外，我们还锁定了超过 500 MW 算力容量的承诺，由我们的新投资者独立出资建设，以支持我们未来数年预期的[算力](https://www.together.ai/gpu-clusters)增长。

## 生产级 AI 的经济学

随着 AI 系统开始承担真正的智力劳动，它们正从偶尔使用的工具转变为生产核心基础设施。公司不再是为演示生成几条回复；它们部署的 agent 在写代码、解决客户问题、分析文档、自动化整条工作流。随着这些工作的规模化，对推理的需求也在同步扩大。

许多公司发现这带来了根本性的经济挑战：封闭前沿 LLM 的成本结构在原型阶段看似可控，到了生产环境往往难以为继。随着用量增长，推理账单比预算复利得更快，迫使公司在需求加速之际对"智能"实行配给。最成功的公司正在以市场一贯的方式回应：找到更高效的方式来生产一种日益不可或缺的资源。

Together AI 已成为开源与定制 AI 的生产平台，把前沿模型与推理栈的持续创新结合起来，在规模化下交付最优经济性。[DeepSeek](https://www.together.ai/models-providers/deepseek)、Nemotron、MiniMax、Kimi、GLM 等开放权重模型已经追平了与专有前沿模型的质量差距，同时给予开发者按自己的应用进行定制和[微调](https://www.together.ai/fine-tuning)的自由。结果是，用开放模型构建的公司 routinely 实现 6 倍到 20 倍的成本降低，同时保持同等或更优的性能。例如，Decagon 迁移到 Together AI 后推理成本降低了六倍。

但生产 AI 的经济学不只由模型决定，而是由整个技术栈决定：模型、kernel、编译器、推理系统、训练基础设施、硬件利用率，以及把这一切整合在一起的软件。

Together AI 是一家研究驱动的公司。过去几个季度，我们的"研究到生产"流水线显著加速。我们发布了面向 NVIDIA Blackwell 的 [FlashAttention-4](https://www.together.ai/blog/flashattention-4)、[Together Megakernel](https://hazyresearch.stanford.edu/blog/2025-05-27-no-bubbles) 和 together.compile，把 kernel 级优化带入生产工作负载；并扩展了后训练 API 以支持 tool calling、推理和视觉-语言模型。我们推出了 Leading 前沿开源模型的最快 endpoint，并已成为全球最大的 AI token 生产者之一。

我为我们建成的平台感到自豪：它在[推理](https://www.together.ai/serverless-inference)、训练、加速计算这一整套生成式 AI 生产能力中提供选择权、掌控力、占优的经济性和前沿性能；我也为 Together AI 在加速创新、在全球范围交付开源 AI 生态所扮演的角色感到自豪。

致我们的客户、团队和投资者：感谢你们相信这个愿景并帮助我们把它变为现实。这个里程碑当然值得庆祝，但它更像是一个开始。这场将重塑每一个行业的技术变革，我们仍处在最早期。

如果我们的愿景与你共鸣，请联系我们——我们正在工程、研究、产品和市场拓展等岗位大规模招聘。
