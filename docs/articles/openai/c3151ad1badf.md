---
vendor: openai
title: 网络行动：为韩语恶意软件活动提供支持
original_title: 
url: https://openai.com/index/disrupting-malicious-uses-of-ai-korean-language-malware-support
date: 2025-10-01
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: native
status: translated
body_sha: f1e8c2cb1ff9
---

OpenAI

2025年10月1日

安全

# 网络行动：为韩语恶意软件活动提供支持

OpenAI 封禁了利用 AI 辅助恶意软件开发、调试、网络钓鱼和凭据窃取流程的韩语账户。

正在加载…

*本案例研究最初发表于 OpenAI 的*[*2025 年 10 月*⁠（在新窗口中打开）](https://cdn.openai.com/threat-intelligence-reports/7d662b68-952f-4dfd-a2f2-fe55b041cc4a/disrupting-malicious-uses-of-ai-october-2025.pdf)*报告。*

## 行动者

我们发现并封禁了一批 ChatGPT 账户。这些账户的韩语使用者试图利用我们的模型开发恶意软件和命令与控制（C2）系统。我们在调查中发现的指标与 Trellix 的一份报告存在重合。该报告将类似活动与针对韩国外交使团的鱼叉式网络钓鱼活动、XenoRAT 恶意软件的部署，以及利用 GitHub 仓库进行 C2 活动联系起来。

这些活动与 Trellix 报告所述情况存在重合，包括使用韩语、活动时间符合 UTC+8 和 UTC+9 时区，以及行动主题和话题相似。这与安全界对朝鲜（DPRK）行动者的认知一致，但我们无法独立确认归因。此外，我们也禁止从朝鲜访问我们的服务。

## 行为

这些账户主要使用韩语与我们的模型交互，呈现出结构化工作流程，许多账户集中在较短的时间窗口内活动。每个账户似乎都专注于特定用途，而非同时涉足多个技术领域，例如将 Chrome 扩展转换为 Safari 扩展以发布到 Apple App Store、配置 Windows Server VPN，或开发 macOS Finder 扩展。

我们观察到，他们与模型的交互涉及 Windows API 挂钩、访问浏览器凭据和 Cookie 的工作流程（DPAPI），以及仿冒 reCAPTCHA 等验证页面。我们还发现了韩语网络钓鱼邮件草稿，内容往往以加密货币为主题，并伪装成政府机构或金融服务提供商发送的消息。

此外，这些行动者还尝试使用 pCloud、file.io 等云存储服务，构建 GDrive 直链并编写 API 脚本，以及使用 GitHub 的原始内容检索和 Token 处理等功能。我们没有发现证据表明，Trellix 所述活动使用的恶意二进制文件由我们的模型生成。同一批操作者可能在通过开发者平台和云平台暂存有效载荷的同时，也使用了我们的模型。

## 生成结果

威胁行动者生成了旨在支持多个行动领域的模型输出，包括：

- 植入程序及 RAT 相关开发：探索反射式 DLL 加载、内存执行和 Windows API 挂钩技术。
- 凭据窃取流程：生成、修改和调试脚本，通过 Chrome／Edge DPAPI 工作流程提取浏览器加密密钥、Cookie 和已保存的密码。
- 网络钓鱼与诱饵：起草疑似韩语网络钓鱼内容，主题通常涉及加密货币、政府机构或金融服务提供商；尝试使用 HTML 混淆和 reCAPTCHA 代理，制作逼真的登录页面。
- macOS 开发框架：提出与 Finder 和 Safari 扩展开发有关的请求，并生成 App Store 隐私政策示例。
- 加密货币操作：排查 API 调用和钱包交互问题。

其中许多请求属于军民两用活动的灰色地带。这些技术完全可以用于软件调试、密码学或浏览器开发等合法用途，但被威胁行动者改作他用时，其性质便截然不同。

## 影响

我们停用了与此次行动有关的所有账户，并与合作伙伴分享了相关指标。我们没有发现证据表明，访问模型让这些行动者获得了超出公开可用技术范围的新能力。

- [韩国](https://openai.com/news/?tags=target-geography-south-korea)
- [网络行动](https://openai.com/news/?tags=cyber-operations)

## 作者

OpenAI
