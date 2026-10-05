---
vendor: huggingface
title: Hugging Face 与 TruffleHog 合作扫描密钥
original_title: Hugging Face partners with TruffleHog to Scan for Secrets
url: https://huggingface.co/blog/trufflesecurity-partnership
date: 2025-02-04
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: d96a08aac7e1
---

# Hugging Face 与 TruffleHog 合作扫描密钥

我们很高兴宣布与 Truffle Security 建立合作与集成，把 TruffleHog 强大的密钥（secret）扫描能力带到我们的平台上——这也是[我们持续安全承诺](https://huggingface.co/blog/2024-security-features)的一部分。

TruffleHog 是一个开源工具，用于检测并验证代码中的密钥泄露。它针对主流 SaaS 和云厂商备有广泛的检测器，可以扫描文件和仓库中的敏感信息，如凭据、token 和加密密钥。

不小心把密钥提交到代码仓库可能造成严重后果。通过扫描仓库里的密钥，TruffleHog 帮助开发者在问题爆发前捕获并清除这些敏感信息，保护数据、防止代价高昂的安全事件。

为了应对公开与私有仓库中的密钥泄露，我们与 TruffleHog 团队推进了两项举措：用 TruffleHog 增强我们的自动扫描流水线；在 TruffleHog 中打造 Hugging Face 原生扫描器。

## 用 TruffleHog 增强自动扫描流水线

在 Hugging Face，我们致力于保护用户的敏感信息。为此我们实现了自动安全扫描流水线，对所有仓库和提交进行扫描。我们把 TruffleHog 加入了这条自动扫描流水线，现在共有三类扫描：

- 恶意软件扫描：用 [ClamAV](https://www.clamav.net/) 检查已知恶意软件特征
- pickle 扫描：用 [picklescan](https://github.com/mmaitre314/picklescan) 检查 pickle 文件中的恶意可执行代码
- 密钥扫描：用 [TruffleHog](https://github.com/trufflesecurity/trufflehog) 检查密码、token 和 API key

每当仓库有新的推送、文件或内容被修改，我们都会对其运行 `trufflehog filesystem` 命令扫描潜在的密钥。一旦检测到经过验证的密钥，我们会通过邮件通知用户，让他们可以采取补救措施。

"已验证密钥"指确认可以对其对应服务商成功认证（authentication）的密钥。但要注意，未验证密钥未必无害或无效：验证可能因技术原因失败，比如服务商宕机。

即便我们已经替你扫描，自己用 trufflehog 扫一遍仓库仍然有价值。例如你可能已经轮换掉了泄露的密钥，想确认它们以"未验证"状态出现；或者你想手工检查未验证密钥是否仍构成威胁。

等 LFS 支持到位后，我们最终会迁移到 TruffleHog 的 Hugging Face 原生扫描命令 `trufflehog huggingface`。

## TruffleHog 的 Hugging Face 原生扫描器

在 TruffleHog 中打造 Hugging Face 原生扫描器的目标，是让我们的用户（以及保护他们的安全团队）能主动扫描自己账号数据中泄露的密钥。

TruffleHog 新推出的开源 Hugging Face 集成可以扫描模型、数据集和 Spaces，以及相关的 PR 和 Discussions。唯一的限制是目前不扫描存放在 LFS 中的文件。他们的团队计划很快为所有 `git` 数据源解决这个问题。

要用 TruffleHog 扫描你自己或你组织的所有 Hugging Face 模型、数据集和 Spaces 中的密钥，运行以下命令：

```
# For your user
trufflehog huggingface --user <username>

# For your organization
trufflehog huggingface --org <orgname>

# Or both
trufflehog huggingface --user <username> --org <orgname>
```

你可以选择加上讨论（`--include-discussions`）和 PR（`--include-prs`）标志来扫描 Hugging Face 的讨论与 PR 评论。

如果只想扫描某一个模型、数据集或 Space，TruffleHog 分别为它们提供了专用标志。

```
# Scan one model
trufflehog huggingface --model <model_id>

# Scan one dataset
trufflehog huggingface --dataset <dataset_id>

# Scan one Space
trufflehog huggingface --space <space_id>
```

如果需要传入认证 token，可以用 --token 标志，或设置 HUGGINGFACE_TOKEN 环境变量。

下面是对 [mcpotato/42-eicar-street](https://huggingface.co/mcpotato/42-eicar-street) 运行 TruffleHog 的输出示例：

```
trufflehog huggingface --model mcpotato/42-eicar-street
🐷🔑🐷  TruffleHog. Unearth your secrets. 🐷🔑🐷

2024-09-02T16:39:30+02:00	info-0	trufflehog	running source	{"source_manager_worker_id": "3KRwu", "with_units": false, "target_count": 0, "source_manager_units_configurable": true}
2024-09-02T16:39:30+02:00	info-0	trufflehog	Completed enumeration	{"num_models": 1, "num_spaces": 0, "num_datasets": 0}
2024-09-02T16:39:32+02:00	info-0	trufflehog	scanning repo	{"source_manager_worker_id": "3KRwu", "model": "https://huggingface.co/mcpotato/42-eicar-street.git", "repo": "https://huggingface.co/mcpotato/42-eicar-street.git"}
Found unverified result 🐷🔑❓
Detector Type: HuggingFace
Decoder Type: PLAIN
Raw result: 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
Commit: 9cb322a7c2b4ec7c9f18045f0fa05015b831f256
Email: Luc Georges <luc.sydney.georges@gmail.com>
File: token_leak.yml
Line: 1
Link: https://huggingface.co/mcpotato/42-eicar-street/blob/9cb322a7c2b4ec7c9f18045f0fa05015b831f256/token_leak.yml#L1
Repository: https://huggingface.co/mcpotato/42-eicar-street.git
Resource_type: model
Timestamp: 2024-06-17 13:11:50 +0000
2024-09-02T16:39:32+02:00	info-0	trufflehog	finished scanning	{"chunks": 19, "bytes": 2933, "verified_secrets": 0, "unverified_secrets": 1, "scan_duration": "2.176551292s", "trufflehog_version": "3.81.10"}
```

感谢 TruffleHog 团队提供了这么棒的工具来守护社区安全！随着我们继续协作让 Hub 对所有人更安全，敬请期待更多功能。
