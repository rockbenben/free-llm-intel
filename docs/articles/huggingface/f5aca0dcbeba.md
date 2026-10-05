---
vendor: huggingface
title: 用 RiskRubric.ai 让 AI 安全普惠化
original_title: Democratizing AI Safety with RiskRubric.ai
url: https://huggingface.co/blog/riskrubric
date: 2025-09-18
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# 用 RiskRubric.ai 让 AI 安全普惠化

*通过标准化风险评估，建立对开放模型生态的信任*

Hugging Face hub 上能找到超过 50 万个模型，但对用户来说如何挑选最适合自己的模型——尤其是在安全层面——并不总是清晰的。开发者也许找到了完全契合用例的模型，却没有系统化的方法来评估它的安全态势、隐私影响或潜在失效模式。

随着模型越来越强大、采用速度不断加快，AI 安全与安全报告也需要同样快速的进步。因此我们很高兴宣布 [RiskRubric.ai](https://riskrubric.ai/)——一项由 Cloud Security Alliance 与 [Noma Security](https://noma.security) 主导、Haize Labs 和 Harmonic Security 参与贡献的全新倡议，为 AI 模型生态提供标准化、透明的风险评估。

## Risk Rubric：面向模型的全新标准化风险评估

RiskRubric.ai 通过在六大支柱上评估模型——透明性、可靠性、安全性、隐私、安全（safety）与声誉——提供**贯穿整个模型版图的、一致且可比的风险分数**。

该平台的方法与开源价值观完全契合：严谨、透明、可复现。借助 Noma Security 的能力实现自动化，每个模型都会经过：

- **1000+ 可靠性测试**，检查一致性与边界情况处理
- **200+ 对抗性安全探测**，针对越狱和 prompt 注入
- 模型组件的**自动化代码扫描**
- 对训练数据与方法的**全面文档审查**
- 包括数据保留与泄露测试的**隐私评估**
- 通过结构化有害内容测试进行的**安全（safety）评估**

这些评估为每个风险支柱产出 0-100 的分数，汇总为清晰的 A-F 等级。每份评估还包含发现的具体漏洞、推荐的缓解措施，以及改进建议。

RiskRubric 还配有筛选器，帮助开发者和组织按自己在意的维度做部署决策。需要隐私保障强的模型用于医疗健康应用？按隐私分数筛选。构建要求输出一致的对客应用？优先看可靠性评分。

## 我们的发现（截至 2025 年 9 月）

用完全相同的标准评估开放与闭源模型，凸显了一些有趣的结果：许多开放模型在特定风险维度上确实超越了闭源对手（尤其在透明性上，开放开发实践的优势尽显）。

看看总体趋势：

**风险分布两极化——多数模型很强，但中段分数暴露的风险偏高**

[![total_score](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/riskrubric/RiskRubric.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/riskrubric/RiskRubric.png)

总风险分数范围是 47 到 94，中位数 81（满分 100）。多数模型聚集在"更安全"区间（54% 为 A 或 B 级），但一长串表现欠佳的尾部拖低了平均值。这种分化显示了极化：模型要么防护良好，要么落在中段分数，两者之间的很少。

集中在 50-67 区间（C/D 档）的模型并非彻底糟糕，但只提供中到低的整体防护。这个区间是最值得关注的现实地带——安全缺口大到值得优先处理。

**这意味着：**不要假设"平均"模型就是安全的。弱表现模型的尾部真实存在——攻击者会聚焦那里。团队可以用综合分数设定**最低门槛（例如 75）**用于采购或部署，确保离群值不会溜进生产环境。

**Safety 风险是"摆动因子"——但与安全防护态势高度相关**

[![safety_histogram](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/riskrubric/Safety.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/riskrubric/Safety.png)

*Safety & Societal*（安全与社会）支柱（如有害输出防护）在各模型间表现出最大的差异。重要的是，在**安全加固**（prompt 注入防御、策略执行）上投入的模型，几乎总在 safety 上也得分更高。

**这意味着**：加强核心安全控制的价值不止于防止越狱，还直接减少下游危害！Safety 似乎是强健安全态势的副产品。

**护栏可能侵蚀透明性——除非你为之设计**

更严格的防护常让模型对终端用户*更不透明*（例如不给解释的拒绝、隐藏边界）。这会造成信任鸿沟：即使系统是安全的，用户也可能觉得它"黑箱"。

**这意味着**：安全不应以牺牲信任为代价。要兼顾两者，请把强防护措施与**带解释的拒绝、来源信号和可审计性**搭配。这样在不放松防御的前提下保住透明性。

持续更新的 results sheet 可在[这里](https://huggingface.co/datasets/nomasecurity/riskrubric-results)访问。

## **结语**

当风险评估公开且标准化时，整个社区就能协作改进模型安全。开发者可以确切看到自己的模型需要加固之处，社区可以贡献修复、补丁和更安全的微调变体。这创造了一个封闭式系统不可能实现的、透明改进的良性循环。它也通过研究最佳模型，帮助整个社区理解安全层面什么有效、什么无效。

如果你想参与这项倡议，可以提交你的模型进行评估（或推荐现有模型！），了解其风险画像！

我们也欢迎对评估方法和评分框架的一切反馈。
