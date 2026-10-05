---
vendor: openai
title: Vixen 与 Keyhole Panda：中国关联的网络行动
original_title: Vixen and Keyhole Panda: China-linked cyber operations
url: https://openai.com/index/disrupting-malicious-uses-of-ai-vixen-keyhole-panda
date: 2025-06-01
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Vixen 与 Keyhole Panda：中国关联的网络行动

OpenAI 封禁了与多个被公开归因于中华人民共和国的威胁行为者关联的账号——其用 AI 支持漏洞研究、脚本编写、翻译和行动排障。

*本案例研究最初发表于 OpenAI [2025 年 6 月](https://cdn.openai.com/threat-intelligence-reports/5f73af09-a3a3-4a55-992e-069237681620/disrupting-malicious-uses-of-ai-june-2025.pdf)报告。*

## 行为者

我们封禁了与多个被公开归因于中华人民共和国（PRC）的威胁行为者相关联的 ChatGPT 账号。这些账号使用了与已知威胁团体 [KEYHOLE PANDA（即 APT5）](https://attack.mitre.org/groups/G1023/)和 [VIXEN PANDA（即 APT15）](https://attack.mitre.org/groups/G0004/)相关的基础设施。

## 行为

这些威胁行为者用中文和英文与我们的模型交互。我们观察到的活动来自相同网络，但按行为可分为不同子集。

一个子集用我们的模型辅助开展与开源调研相关的行为，对象为若干关注实体与技术主题。在技术性较强的模型交互中，威胁行为者用我们的模型修改脚本或排查系统配置问题。此类活动涉及 reNgine——一个面向 Web 应用的自动化侦察框架——以及用于绕过登录机制、截获授权令牌的 Selenium 自动化。

另一个子集似乎在试图开展支持性开发活动，包括 Linux 系统管理、软件开发和基础设施搭建。其系统管理工作涉及防火墙与域名服务器的配置建议、为离线部署构建软件包。其软件开发活动包括 Web 与 Android 应用开发，以及 C 语言和 Golang 软件。基础设施搭建包括配置 VPN、软件安装、Docker 容器部署，以及 DeepSeek 等本地 LLM 部署。

## 生成内容

这些威胁行为者生成的内容涉及多个主题：

- 口令爆破：威胁行为者求助编写对 FTP 服务器尝试多种用户名/密码组合的脚本。
- 端口扫描软件：威胁行为者用我们的模型修改并完善用于扫描服务器特定端口的脚本。
- AI 驱动的渗透测试：某威胁行为者研究如何用 LLM 自动化渗透测试——分析 Nmap 扫描输出、构造要执行的命令、并把命令输出迭代送回 LLM 以生成新命令。
- 社交媒体自动化：某威胁行为者在开发用于管理一批 Android 设备、自动化社交媒体平台操作的代码。
- 对美国联邦防务产业、军方网络和政府技术的调研：多个威胁行为者检索关于美国特种作战司令部、卫星通信技术、地面站终端位置、政府身份验证卡和网络设备的公开信息。

这些活动的代表性示例可映射到 LLM ATT&CK 框架如下：

- 研究漏洞并生成设计用于 OpenAI API 的 AI 辅助渗透测试脚本：LLM 辅助的漏洞研究。
- 自动化 IP 段转换与网络侦察脚本：LLM 增强的脚本技术。
- 粘贴文本并用模型提取 IP 与主机名以刻画网络基础设施：LLM 引导的基础设施画像。
- 询问政府身份验证细节与电信基础设施分析：LLM 建议的战略规划。
- 为操纵 Android 设备社交媒体自动化指挥与控制：LLM 增强的脚本技术。
- 用 LLM 分析并总结漏洞报告、生成利用载荷创意：LLM 辅助的漏洞研究。
- 为恶意软件开发生成代码混淆与反逆向技术：LLM 优化的载荷制作。

## 影响

我们禁用了与该活动关联的全部账号，并向行业伙伴共享了相关指标。虽然本次调查对一张 PRC 关联威胁行为者网络及其行动工作流——包括工具开发、开源调研和基础设施画像——提供了异乎寻常的广泛可见性，但我们没有发现证据表明访问我们的模型给了这些行为者无法从多个公开资源获取的新能力或新方向。
