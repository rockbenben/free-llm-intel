---
vendor: mistral
title: 常驻终端的 Mistral Vibe
original_title: Terminally online Mistral Vibe.
url: https://mistral.ai/news/mistral-vibe-2-0
date: 2026-01-27
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

今天，我们发布 Mistral Vibe 2.0——对我们终端原生的编码 agent 的一次重大升级，由最先进的 Devstral 2 模型家族驱动。构建自定义子 agent，先澄清再执行，用斜杠命令加载技能（skills），并配置属于你自己的工作流来契合你的工作方式。

Vibe 赋能你和你的团队更快地构建、维护和交付代码。

Mistral Vibe 现已纳入 Le Chat Pro 和 Team 套餐——可按量付费（pay-as-you-go）额度供重度使用，也可以自带 API key。

## 亮点

- Mistral Vibe 2.0：自定义子 agent、多选项澄清、斜杠命令技能、统一的 agent 模式以及自动更新。
- 今天在 Le Chat Pro 和 Team 套餐上可用，超额用量按量付费（PAYG），或自带密钥（BYOK）。
- Devstral 2 转为付费 API 访问：在 Mistral Studio 的 Experiment 套餐上仍可免费使用。
- 企业服务：微调、强化学习与代码现代化。

## Vibe 的新功能

Mistral Vibe 已经为你提供终端原生的代码自动化：自然语言命令、多文件编排、智能引用和完整代码库上下文。在 2.0 中，我们加入让你真正驾驭它的控制项。

自定义子 agent：为特定任务构建专门 agent——部署脚本、PR 审查、测试生成——并按需调用。

多选项澄清：Vibe 先问后做。当意图不明确时，它会给出选项让你选择，而不是瞎猜。

斜杠命令技能：用 / 加载技能——针对部署、lint、生成文档等常见任务的预置工作流。

统一的 agent 模式：配置组合了工具、权限和行为的自定义模式。无需切换工具即可切换上下文。

Vibe CLI 的 bug 修复与改进现在持续自动发布，无需手动更新。

## 套餐与定价

Mistral Vibe 包含在 Le Chat Pro 和 Team 套餐中，提供足以支撑全职开发的用量。订阅用户在超出限额后可以按 API 费率付费用量继续使用，直到用量重置。Devstral 2 现转为付费 API 访问。

[完整访问 Mistral Vibe CLI 和 Devstral 2。学生享 5 折优惠。适合持续的日常开发工作。](https://chat.mistral.ai/upgrade/plans)[包含 Pro 的全部功能，另有统一账单、管理功能和优先支持。](https://chat.mistral.ai/upgrade/plans)

通过 [Mistral Studio](https://console.mistral.ai/home) 直接用 Devstral 构建。

|  | 输入 | 输出 |
| --- | --- | --- |
| Devstral 2 | $0.40/百万 token | $2.00/百万 token |
| Devstral 2 Small | $0.10/百万 token | $0.30/百万 token |

Experiment 套餐仍提供免费 API 用量——非常适合测试和原型验证。

## 企业增值项

面向有更高需求的团队，我们提供针对内部语言和 DSL 的微调、基于你自己环境的强化学习，以及端到端代码现代化——把整个代码库迁移到现代技术栈，同时不丢失业务逻辑、不破坏行为。我们已为全球金融、国防和基础设施领域的一些最大组织交付这些方案。

如需了解详情，请[联系我们](https://mistral.ai/contact)。

## 开始使用

1. 在你的终端中安装 Vibe CLI：

```
curl -LsSf https://mistral.ai/vibe/install.sh | bash
```

```
uv tool install mistral-vibe
```

2. [注册并开始使用](https://console.mistral.ai/codestral/cli)以解锁完整访问。

3. 开始构建：在终端里运行 vibe。

4. 查阅[文档](https://docs.mistral.ai/mistral-vibe/introduction)，或[在 X 上关注我们](https://x.com/Mistralvibe)获取更新。

## 我们在招人

如果你想和我们一起打造世界级的 AI 产品，我们期待你的来信。[投递简历加入我们的团队](https://mistral.ai/careers)。
