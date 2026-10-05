---
vendor: openai
title: Codex 全面升级
original_title: Introducing upgrades to Codex
url: https://openai.com/index/introducing-upgrades-to-codex
date: 2026-10-02
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Codex 全面升级

Codex 现在运行更高效、性能更稳定，实时协作与独立任务处理能力显著提升，无论是在终端、IDE、网页，还是在手机上进行开发，均能随时使用。

$ npm i -g @openai/codex

***2025 年 9 月 23 日更新****：** GPT-5-Codex 现已向通过 API key 使用 Codex 的开发者开放（除了向通过 ChatGPT 订阅使用 Codex 的开发者开放之外）。GPT-5 Codex 与 GPT-5 同价，且仅在 Responses API 中提供。底层模型快照将持续更新。更多细节请查看 Codex *[*开发者文档*⁠（在新窗口中打开）](http://platform.openai.com/docs/models/gpt-5-codex)* 和 *[*changelog*⁠（在新窗口中打开）](https://developers.openai.com/codex/changelog)*。*

今天，我们发布 GPT-5-Codex——一个针对 Codex 中 agentic 编程进一步优化的 GPT-5 版本。GPT-5-Codex 的训练聚焦真实世界的软件工程工作；它既擅长快速交互式会话，也能独立攻克冗长复杂的任务。它的代码审查能力可以在严重 bug 上线前将其捕获。GPT-5-Codex 在你使用 Codex 的任何地方都可用——它是云端任务和代码审查的默认模型，开发者也可以在 Codex CLI 和 IDE 扩展中选择用它处理本地任务。

自今年 4 月首次推出 [Codex CLI⁠（在新窗口中打开）](https://github.com/openai/codex)、5 月推出 [Codex⁠](https://openai.com/zh-Hans-CN/index/introducing-codex/) 网页版以来，Codex 已稳步演化为更有效的编程协作者。两周前，我们把 Codex 统一为一个由 ChatGPT 账号串联的单一产品体验，让你能在本地环境与云端之间无缝迁移工作而不丢失上下文。Codex 现在在你开发的地方工作——终端、IDE、网页、GitHub，甚至 ChatGPT iOS 应用。ChatGPT Plus、Pro、Business、Edu 和 Enterprise 套餐均已包含 Codex。

随着这些更新，Codex 更接近我们一直在打造的目标——一个理解你的上下文、与你并肩工作、并能可靠地为你的团队承接工作的队友。

## GPT-5-Codex

GPT-5-Codex 是 GPT-5 针对 Codex 中 agentic 软件工程进一步优化的版本。它在复杂的真实工程任务上训练，例如从零构建完整项目、添加功能与测试、调试、执行大规模重构，以及进行代码审查。它更可控，能更好地遵循 [AGENTS.md⁠（在新窗口中打开）](http://agents.md) 指令，产出更高质量的代码——只需告诉它你要什么，不必为风格或代码整洁度写冗长指令。

***SWE-Bench 验证：****在 GPT-5 发布时及历史评估中，我们报告的是 477 个 SWE-bench 验证任务的结果，因为有些任务无法在我们的基础设施中运行。我们已修复这个问题，现在可以报告全部 500 项任务的评估结果。*

***代码重构任务：****我们的代码重构评估包含来自大型、成熟代码库的重构式任务，包括 Python、Go 甚至 OCaml 中的任务。一个示例任务是*[*来自 Gitea 的以下拉取请求*⁠（在新窗口中打开）](https://github.com/go-gitea/gitea/commit/fd7d83ace60258acf7139c4c787aa8af75b7ba8c)*，它更改了 232 个文件和 3,541 行代码，以将 ctx 变量贯穿应用程序逻辑。*

GPT-5-Codex 会根据任务复杂度更动态地调整思考时间。该模型结合了一个编程 agent 的两项必备技能：在交互式会话中与开发者结对，以及在较长任务上持续独立执行。这意味着 Codex 在处理小的、定义明确的请求或你与它聊天时会更轻快，而在大型重构等复杂任务上则会工作更久。在测试中，我们看到 GPT-5-Codex 在大型复杂任务上单次独立工作超过 7 小时，不断迭代实现、修复测试失败，最终交付成功的实现。

在 OpenAI 员工流量上我们看到：按模型生成 token 数（含隐藏推理和最终输出）排序，处于底部 10% 的用户轮次中，GPT-5-Codex 比 GPT-5 少用 93.7% 的 token。反过来，在顶部 10% 的轮次中，GPT-5-Codex 思考更多——花两倍时间推理、编辑和测试代码并迭代。

GPT-5-Codex 专门为代码审查和发现关键缺陷而训练。审查时，它会在你的代码库中导航、推理依赖关系，并运行你的代码和测试以验证正确性。我们在热门开源仓库的近期提交上评估代码审查表现。对每个提交，由经验丰富的软件工程师评估审查评论的正确性与重要性。我们发现 GPT-5-Codex 的评论更不容易出错或不重要，把用户的注意力更多留给关键问题。

GPT-5-Codex 是前端任务上可靠的伙伴。除了创建美观的桌面应用，GPT-5-Codex 在创建移动网站的人类偏好评估中也有显著提升。在云端工作时，它可以查看你提供的图片或截图作为输入，目视检查自己的进度，并把成果截图展示给你。

GPT-5-Codex 为 Codex CLI、Codex IDE 扩展、Codex 云环境以及 GitHub 中的工作而专门构建，并支持多种工具调用。与通用模型 GPT-5 不同，我们建议仅在 Codex 或类 Codex 环境中把 GPT-5-Codex 用于 agentic 编程任务。

## Codex 的更新

我们最近还做了一些更新，让 Codex 成为更好的结对编程伙伴，包括重造的 Codex CLI 和全新的 Codex IDE 扩展。

### Codex CLI

Codex CLI 是开源的，过去几个月社区反馈对其演进弥足珍贵。基于这些反馈，我们围绕 agentic 编程工作流重建了 Codex CLI，把我们的模型塑造成更强、更可靠的伙伴。你现在可以直接在 CLI 中附加并分享图片——截图、线框图和图表——就设计决策建立共享上下文，就得到你想要的结果。在做更复杂的工作时，Codex 现在会用 to-do 列表跟踪进度，并内置网页搜索和 MCP 等连接外部系统的工具，整体工具调用也更准确。

终端 UI 也做了升级：工具调用和 diff 的格式更清晰、更易读。审批模式简化为三个层级：只读并需显式审批；auto 模式拥有完整工作区访问权、工作区外需审批；完全访问模式可在任意位置读文件并带网络访问运行命令。它还支持压缩会话状态，让更长的会话更易管理。

更多内容请查看 [Codex CLI 快速上手⁠（在新窗口中打开）](https://developers.openai.com/codex/cli)。

### Codex IDE 扩展

Codex 在你已经工作的地方与你相遇，包括 IDE。IDE 扩展把 Codex agent 带进 VS Code、Cursor 和其他 VS Code 分支，让你无缝预览本地更改并与 Codex 一起编辑代码。在 IDE 中使用 Codex 时，你可以写更短的 prompt、获得更快的结果，因为 Codex 能利用你打开的文件、选中的代码等上下文。

Codex IDE 扩展还能让你在云端与本地环境之间顺畅迁移工作。你可以不离开编辑器就创建新的云任务、跟踪进行中的工作、审阅已完成任务。要做收尾润色时，可以在 IDE 中打开云任务，Codex 会保持上下文。关于如何充分利用 IDE 扩展，请在[快速上手⁠（在新窗口中打开）](https://developers.openai.com/codex/ide)了解更多。

### Codex 云

除了 Codex CLI，全新的 IDE 扩展和 GitHub 集成让 Codex 云 agent 更贴近开发者工作流，你现在可以委派任务而不必切换出编辑器或 GitHub。

在幕后，我们也在持续提升云基础设施性能。通过缓存容器，我们把新任务和追加任务的中位完成时间缩短了 90%。Codex 现在还会自动搭建自身环境——扫描常见的安装脚本并执行；配合可配置的网络访问，它可以在运行时执行 pip install 等命令按需获取依赖。

与 CLI 和 IDE 扩展一样，你现在可以用图片分享前端设计规范或解释 UI bug。在为你构建的过程中，Codex 可以启动自己的浏览器、查看构建结果、迭代，并把成果截图附加到任务和 GitHub PR 上。更多细节请查看[文档⁠（在新窗口中打开）](https://developers.openai.com/codex/cloud)。

### 代码审查

Codex 现在还内置了为捕获关键缺陷而训练的代码审查能力。与静态分析工具不同，它会把 PR 声明的意图与实际 diff 对照、对整个代码库和依赖进行推理，并执行代码和测试来验证行为。只有最一丝不苟的人类审查者才会对每个 PR 下这样的功夫，Codex 补上了这个缺口——帮助团队更早发现问题、减轻审查者负担、更放心地发布。

在 GitHub 仓库开启后，Codex 会在 PR 从草稿转为 ready 时自动审查，并把分析发布在 PR 上。如果它建议修改，你可以在同一线程里让 Codex 直接实施。你也可以在 PR 里提到 "@codex review" 明确请求审查，或给出额外指引，如 "@codex review for security vulnerabilities" 或 "@codex review for outdated dependencies"。关于如何为你的仓库设置代码审查，请查看[快速上手⁠（在新窗口中打开）](https://developers.openai.com/codex/cloud/code-review)。

在 OpenAI，Codex 现在审查了我们绝大多数 PR，每天捕获数百个问题——常常在人工审查开始之前。它是 Codex 团队更快、更放心地推进的关键。

### 开发人员如何使用 Codex

## 构建安全可信的 AI agent

我们构建 Codex 时专注于保护代码和数据免遭外泄、防范滥用。默认情况下，无论在本地还是云端，Codex 都在禁用[网络访问⁠（在新窗口中打开）](https://platform.openai.com/docs/codex/agent-network)的沙箱环境中运行。这有助于确保 Codex 无法在你的计算机上执行有害操作，并降低来自不可信来源的 prompt 注入风险。

Codex 会在潜在危险操作前请求许可，并被训练运行命令以验证自身输出。开发者可以按自身风险承受度定制安全设置。在云端，你可以把网络访问限制到可信域名。在 CLI 和 IDE 扩展中，开发者可以批准以完全访问权限运行的命令，或允许 agent 使用网页搜索并连接 MCP 服务器。这可以扩展 agent 的能力，同时也会增加风险——关于如何安全运行和管理 Codex，请[在此⁠（在新窗口中打开）](https://developers.openai.com/codex/security)了解更多。

我们始终鼓励开发者在做出更改或部署到生产环境前审查 agent 的工作。Codex 会为每个任务提供引用、终端日志和测试结果以便审查。虽然 Codex 代码审查有助于降低危险问题被部署到生产的风险——无论问题由人还是 agent 产生——我们始终建议把 Codex 作为额外的审查者，而非人工审查的替代。

与我们对 GPT-5 的处理方式一致，我们决定在生物与化学领域把 GPT-5-Codex 视为高能力（High capability）级别，并实施了缓解相关风险的防护措施。关于我们的评估与稳健的安全方案，请阅读[系统卡附录⁠](https://openai.com/zh-Hans-CN/index/gpt-5-system-card-addendum-gpt-5-codex/)。

## 定价与可用性

Codex 已包含在 ChatGPT Plus、Pro、Business、Edu 和 Enterprise 套餐中。用量随套餐扩展：Plus、Edu 和 Business 席位每周可覆盖几次专注的编程会话，而 Pro 可支撑跨多个项目的完整工作周。

Business 套餐可购买 credit，让开发者超出包含限额；Enterprise 套餐提供共享 credit 池，你只需为开发者实际用量付费。关于 ChatGPT 用量限额的更多信息请[点击这里⁠（在新窗口中打开）](https://developers.openai.com/codex/pricing)。

对于通过 API key 使用 Codex CLI 的开发者，我们计划很快在 API 中提供 GPT-5-Codex。

Codex 正在成为我们一直设想的编程伙伴——更快、更可靠，并深度集成进你已在使用的工具。我们很期待看到你用它的创造，并将持续改进 Codex，让它成为你最雄心项目中更好的队友。
