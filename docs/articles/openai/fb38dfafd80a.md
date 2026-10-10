---
vendor: openai
title: OpenAI 安全性风险赏金计划正式上线
original_title: 
url: https://openai.com/index/safety-bug-bounty
date: 2026-09-30
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: native
status: translated
body_sha: d39ed1d06cd2
---

OpenAI

2026年3月25日

安全

安全防护

# OpenAI 安全性风险赏金计划正式上线

全面检测 OpenAI 各项服务的安全性风险与滥用问题

今天，OpenAI 正式启动面向公众的[安全性风险赏金计划 (Safety Bug Bounty)](https://bugcrowd.com/engagements/openai-safety)，旨在识别我们各项产品中可能存在的 AI 滥用及安全风险。随着 AI 技术的飞速演进，其被误用的潜在方式也在不断增加。我们的目标是确保系统具备足够的安全性，能够有效抵御可能导致实质性损害的误用或滥用行为。

这项新计划将与 OpenAI 原有的[安全漏洞赏金计划 (Security Bug Bounty)](https://bugcrowd.com/engagements/openai) 形成互补 — 即便某些问题不符合传统安全漏洞的判定标准，只要其构成了显著的滥用或安全风险，我们也将予以受理。通过该计划，我们期待与安全研究人员持续合作，共同发现并解决那些虽不属于传统范畴、但仍带有真实风险的问题。所有提交的内容将由 OpenAI 的安全性风险与安全漏洞赏金团队统一分拣，并根据职能范围在两个计划之间进行流转。

## 计划概览

这项全新的[安全性风险赏金计划](https://bugcrowd.com/engagements/openai-safety)专注于下述 AI 特有的安全场景：

**包括 MCP 在内的智能体风险**

- 第三方提示注入与数据外泄：攻击者输入的文本能够稳定劫持受害者的智能体（包括浏览器、ChatGPT 智能体及类似智能体产品），并诱导其执行有害操作或泄露用户敏感信息。此类行为必须具备至少 50% 的可复现性。
- OpenAI 智能体产品在 OpenAI 网站上大规模执行被禁止的操作。
- OpenAI 智能体产品执行上述未列出的其他潜在有害操作。有效报告必须证明该行为可能导致实质性的严重损害。
- 任何针对 MCP 风险的测试均须遵守相关第三方的服务条款。

**OpenAI 专有信息**

- 返回推理相关专有信息的模型生成内容。
- 泄露其他 OpenAI 专有信息的漏洞。

**账户与平台完整性**

- 账户与平台完整性识别机制中的漏洞，例如绕过防自动化控制系统 (Anti-automation control)、操纵账户信任信号、规避账户限制/停用/封禁等类似问题。
- 对于允许用户越权访问功能、数据或权限的操作，应提交至[安全漏洞赏金计划 (Security Bug Bounty)](https://bugcrowd.com/engagements/openai)。

虽然“越狱 (Jailbreak)”不属于本计划的受理范围，但我们会定期针对特定的损害类型开展私密赏金活动，例如针对 [ChatGPT 智能体⁠](https://openai.com/bio-bug-bounty/)和 [GPT‑5⁠](https://openai.com/gpt-5-bio-bug-bounty/) 中生物风险 (Biorisk) 内容问题的专项测试。我们邀请感兴趣的研究人员在相关项目启动时踊跃申请。

除上述类别外，如果研究人员发现的缺陷能够导致直接的用户损害，并能提供具体、可操作的修复建议，我们将根据实际情况评估是否给予奖励。对于没有实质性安全影响或滥用后果的常规内容政策绕过行为，本计划不予受理。例如，仅导致模型使用粗鲁言辞，或返回那些通过搜索引擎即可轻松获取的信息等“越狱”行为，均不在奖励范围内。

## 如何参与

有意参与的研究人员可以通过[安全性风险赏金计划 (Safety Bug Bounty)](https://bugcrowd.com/engagements/openai-safety) 进行申请。我们期待与广大研究人员、白帽黑客，以及安全防护社区携手合作，共同打造一个安全的 AI 生态系统。

- [2026 年](https://openai.com/news/?tags=2026)
- [网络安全](https://openai.com/news/?tags=cybersecurity)

## 作者

OpenAI
