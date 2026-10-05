---
vendor: huggingface
title: Hugging Face 与 VirusTotal 合作加强 AI 安全
original_title: Hugging Face and VirusTotal collaborate to strengthen AI security
url: https://huggingface.co/blog/virustotal
date: 2025-03-18
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Hugging Face 与 VirusTotal 合作加强 AI 安全

我们很高兴宣布 Hugging Face 与 [VirusTotal](https://virustotal.com)——全球领先的威胁情报与恶意软件分析平台——达成新合作。这项合作增强了在 Hugging Face Hub 上共享文件的安全性，帮助机器学习社区免受恶意或被篡改资产的侵害。

TL;DR - 从今天起，Hugging Face Hub 上 220 万+ 个公开模型与数据集仓库都将持续接受 VirusTotal 扫描。

## 为什么这很重要

AI 模型很强大，但它们也是复杂的数字制品，可能包含大型二进制文件、序列化数据和依赖，有时暗藏风险。截至目前，HF Hub 托管着 220 万个公开模型工件。随着我们成长为全球最大的开放机器学习模型与数据集平台，确保共享资产保持安全至关重要。

威胁可以有多种形态：

- 伪装成模型文件或压缩包的恶意载荷
- 在上传前就已被篡改的文件
- 与已知恶意软件活动相关联的二进制资产
- 加载时会执行不安全代码的依赖或序列化对象

与 VirusTotal 合作，让我们增加了一层额外的保护和可见性：通过 Hugging Face 共享的文件可以与全球最大、最受信赖的恶意软件情报数据库之一进行比对检查。

## 合作如何运作

每当你访问一个仓库页面、文件或目录页面时，Hub 会自动获取对应文件的 VirusTotal 信息。[示例](https://huggingface.co/Juronuim/xbraw2025/tree/main)

具体流程如下：

- 我们将文件哈希与 VirusTotal 的威胁情报数据库进行比对。
- 如果该文件哈希此前已被 VirusTotal 分析过，则获取其状态（干净或恶意）。
- 不会向 VirusTotal 共享任何原始文件内容，从而保护用户隐私并符合 Hugging Face 的数据保护原则。
- 结果包含元数据，如检出数量、已知恶意关联，以及相关的威胁活动情报。

这为用户和组织在下载或集成 Hub 上的文件之前提供了宝贵上下文。

## 对社区的益处

- 透明：用户可以看到文件是否在 VirusTotal 生态中被标记或分析过。
- 安全：组织可以把 VirusTotal 检查集成到其 CI/CD 或部署工作流中，帮助阻止恶意资产扩散。
- 高效：复用已有的 VirusTotal 情报，减少重复或冗余扫描的需要。
- 信任：我们共同努力，让 Hugging Face Hub 成为更安全、更可靠的开源 AI 协作之地。

## 加入我们

如果你想了解更多关于这一集成的信息，或探讨如何共建更安全开源 AI 生态的方式，请联系 [security@huggingface.co](mailto:security@huggingface.co)。

携手同行，我们能让 AI 协作不仅开放，而且从设计上就安全。
