---
vendor: together_ai
title: 研究观点：是的，AGI 可以到来——一个计算视角
original_title: "Research POV: Yes, AGI Can Happen – A Computational Perspective"
url: https://www.together.ai/blog/research-pov-yes-agi-can-happen
date: 2025-12-17
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

*我们的 Kernels 副总裁 Dan Fu 发布了一篇新文章，反驳"AI 正撞上硬件墙"的说法。他主张我们严重低估了当前芯片的利用率，而更好的软硬件协同设计将解锁下一个数量级的性能。*

通往 AGI 的进步遇到墙了吗？

在快速发展的 AI 世界里，关于"数字计算极限"的争论正在升温。一些[近期分析](https://timdettmers.com/2025-12-10/why-agi-will-not-happen/)认为硬件约束和停滞的 GPU 进步可能把通往通用有用 AI 的道路堵在瓶颈。

领导我们 kernels 研究团队的 **Dan Fu** 在他的最新文章中给出了不同、更乐观的视角：**"[是的，AGI 可以到来——一个计算视角。](https://danfu.org/notes/agi/)"**

尽管承认我们面临的真实约束，Dan 主张我们远未触及天花板。事实上，他认为当今 AI 系统距离理论极限还差得远。在他的深度剖析中，他拆解了数字，指明"余量"在哪里：

- **我们在低效利用当前硬件：** 当今最先进的训练运行（如 DeepSeek-V3 或 Llama-4）往往只达到约 20% 的平均浮点利用率（MFU），推理利用率则常常只有个位数。通过更好的软硬件协同设计和 FP4 训练等创新，有巨大效率空间可释放。
- **模型是滞后指标：** 我们今天的模型是在"旧"硬件上训练的。下一代算力——10 万+ 最新世代 GPU 的大规模集群——甚至还未完全进入等式。
- **效用已经到来：** 即便没有未来的飞跃，当前模型已经在改变复杂工作流——比如在人在回路的指导下编写高性能 GPU kernel。

如果你对系统工程、硬件效率和 AI scaling 未来的交叉点感兴趣，这是必读之作。

[在这里阅读 Dan 的完整分析。](https://danfu.org/notes/agi/)
