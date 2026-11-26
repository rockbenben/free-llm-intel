---
vendor: anthropic
title: 保护编码 agent 的企业指南
original_title: 
url: https://claude.com/resources/articles/enterprise-guide-to-securing-coding-agents
date: 2026-11-23
lang: zh
captured: 2026-11-26
extractor: readability-v1
translator: agent
status: translated
body_sha: 853ca5c53c02
---

# 保护编码 agent 的企业指南

## 一边快速交付，一边保障安全

编码 agent 很可能已经在你的组织里编写代码、提交 pull request 了。对许多领先企业而言，它们还在审查、测试并合并这些代码。

例如，在把整个工程组织统一到 Claude Code 之后，[Salesforce](https://www.salesforce.com/news/stories/how-engineering-became-agentic/)¹ [报告](https://www.salesforce.com/news/stories/how-engineering-became-agentic/)说：

79%

每位开发者在 Salesforce 合并的 pull request 更多

5%

Salesforce 的事故总数更少

随着 agent 承担的工作越来越多，技术与安全负责人必须用分层控制来缓解 prompt injection 与权限滥用之类的风险，例如经过校验的权限和有边界的运行环境。

前两章聚焦于界定风险的边界。我们讨论每个 AI 供应商都应满足的要求，以及需要缓解的四类 agentic 风险。

接下来的三章聚焦于约束风险。我们介绍借助 Claude Code 可以部署的防御层级，以及如何集中管理和强制执行这些控制。

本指南旨在提供一个有用的 agent 安全框架，让组织有把握、有信心在规模化场景下有效运行 agent。

防御一个 AI agent 的组成部分：模型、模型周围的环境，以及对输入和输出的外部检查。

*本指南面向使用 Claude Team 与 Enterprise 套餐的组织。如果你通过 AWS、Google Cloud 或 Microsoft Azure 等云服务商访问 Claude，同样的原则与本地控制也适用。*

## 01 设定 agent 安全的门槛

每个编码 agent 都该回答的六个问题 · 把 SaaS 要求套用到你的 AI 供应商

> “在 agentic AI 时代，CISO 的职责并不是实现零风险。我们的工作是让 agentic 风险变得可被看清、可被约束。这样我们才能有意识地接受自己能够管理的风险，让业务按我们的方式推进，而不是绕开我们。”

[Jason Clinton](https://claude.com/resources/articles/ciso-guide-to-agentic-ai)，Anthropic 副 CISO

### 每个编码 agent 都该回答的六个问题

以下是负责人在评估编码 agent 时可以提出的六个问题，用来核实它们是否已具备企业级就绪度。

| 要问的问题 | 为什么你该关心 | 好的回答 | 弱的回答 |
| --- | --- | --- | --- |
| **模型在应当拒绝时会拒绝吗？** | 模型是对有害请求的第一道检查，让坏动作更不容易发生。 | 拒绝能力训练进了权重，并公布相关比率。 | “我们的 system prompt 指示模型拒绝。” |
| **动作在执行之前，是否在模型之外被自动检查？** | 外部检查可以在模型被诱导或判断失误时抓到问题。 | 对命令做静态分析，外加一个独立的评估模型。prompt injection 探测。 | “模型能力很强。” |
| **爆炸半径是否被环境所约束？** | 这限定了事件的严重程度，因而限定了风险。 | 内核级沙箱，管理员可以强制要求并设为 fail closed，或为每个会话提供隔离 VM。在网络层做出口白名单。 | “我们指示 agent 不要离开工作目录。” |
| **策略能否被集中锁定？** | 设定个人无法撤销的最低标准。 | 托管设置配上本地用户无法覆盖的 hard-deny 规则。 | “按开发者各自的配置文件，外加一份靠自觉遵守的策略文档。” |
| **agent 写的代码是否安全？** | 代码量在激增，如果检查不随代码量一起扩展，漏洞就会上线。 | 自动化安全审查，由人工批准高风险改动。 | “模型经过训练，会写安全的代码。” |
| **你能否还原一起事件？** | 合规。持续改进安全。 | 会话[遥测导出](https://code.claude.com/docs/en/monitoring-usage)、[审计 API](https://platform.claude.com/docs/en/manage-claude/compliance-api)（Enterprise），以及明确列出的已知缺口。 | “日志可按需提供。” |

### 把 SaaS 要求套用到你的 AI 供应商

你已经有了一份 SaaS 供应商检查清单，涵盖单点登录、基于角色的访问、数据处理条款和审计日志等控制项。对 AI 供应商也应当采用类似的清单。举例来说，Claude Code 通过以下方式支持这些安全预期：

- **单点登录与基于角色的访问控制**（Enterprise），用你管理其他企业工具的方式来管理。
- 按我们的商业条款，我们**不会用代码或 prompt 训练生成式模型**，除非你的组织选择与我们共享这些数据。
- **Enterprise Frontier Safeguards（分阶段推出）**把零数据保留的隐私性与最先进的滥用检测防护结合起来，覆盖能力极强的模型。数据可以用你自己的密钥加密，并在你控制的存储中保留有限时间。[了解更多](https://www.anthropic.com/news/enterprise-frontier-safeguards)。
- 在 Enterprise 上，一旦应用 HIPAA 配置，Claude Code CLI 与桌面应用本地模式下的 Code 标签页即享有 **BAA** 覆盖。
- 云平台上的**加密选项**：Amazon Bedrock 上的 AWS KMS 客户托管密钥、Google Cloud 上的 CMEK，或 Microsoft Foundry 的 Hosted on Azure 选项。
- [Anthropic Trust Center](https://trust.anthropic.com) 中的 **SOC 2 Type 2 报告与 ISO 27001 证书**。

## 02 识别 AI 特有的风险

凭据泄漏与权限滥用 · 未经审查的依赖与扩展 · 数据外泄 · prompt injection

安全与技术负责人对凭据泄漏、权限滥用、被污染的依赖和内部威胁等风险并不陌生。然而一旦涉及 agent，攻击面、速度与规模都会改变。我们来看其中一些风险。

| 风险 | 你今天怎么处理 | 有了 agent 之后有什么变化 |
| --- | --- | --- |
| **凭据泄漏与权限滥用** | 最小权限、短时效 token、通过 workload identity 或 OIDC 实现无密钥认证。定期审查权限过高的账户。人员用具名账户，软件按工作负载分配身份。 | 凭据应当是短时效的，并限定到具体任务或作业，而不是开发者的全部权限。agent 在开发者的会话内行动，而 Claude Code 之外的多数日志只显示开发者的名字。 |
| **未经审查的依赖与扩展** | 锁定版本、审查关卡、清单变更需两名审查者。配置纳入版本控制。 | agent 添加依赖的速度——不分是否经过审查——都快于人工流程。扩展一旦连接，就会向 agent 下达指令。 |
| **数据外泄** | 在网络层做出口白名单。 | 被攻陷的 agent 可以通过你本就允许的服务把数据送出去。与传统恶意软件不同，它可以尝试多条路径，而攻击者不必事先定义这些路径。 |
| **内部风险** | 社会工程意识培训、验证、上报路径。 | prompt injection：检查点转移到了工具调用与网络边界上。 |

### 风险 1：凭据泄漏与权限滥用

agent 能读到的任何东西，它都可能泄漏出去，包括长期有效的 AWS access key 或 GitHub token 这类凭据。

agent 能做的任何事，被攻陷或过于积极的 agent 都可能滥用。默认情况下，Claude Code 中的 agent 以监管它的那位开发者的身份运行。发生事件时，你可能需要区分 agent 的动作与开发者的动作，才能作出恰当的响应。

pull request 对话的示意图。在流水线中，agent 的工作以它自己的名字呈现。

### 风险 2：未经审查的依赖与扩展

agentic 编码加快了代码生成与审查的速度，也就加快了依赖被添加、配置被修改的速度。

当你让 agent 加上 JSON schema 校验时，它会找到一个包、装上最新版本，几分钟内就写出可用的代码。如果 agent 没有被指向正确的方向，这种速度本身就是风险。

MCP servers、plugins、skills、subagent 定义，以及仓库里的 `CLAUDE.md` 文件也都是依赖，它们值得你像对待一个包那样去审查。与被污染的库不同——后者要等被调用才发作——它们一加载就会抵达 agent。在 agent 做任何工作之前，它们的描述与指令就已经进入了上下文窗口。

在 Enterprise 套餐上，[skill 与 plugin 扫描](https://support.claude.com/en/articles/15927065-get-started-with-skill-and-plugin-scanning)会在组织内有人上传或编辑第三方 skills 和 plugins 时检查其中的恶意内容。

Enterprise 套餐上 skill 与 plugin 扫描拦截某个 plugin 时，管理员所看到的界面的示意图。

### 风险 3：数据外泄

每一次泄漏都需要一条通往外面的路径。难点在于，域名白名单无法把你自己账户和攻击者的账户区分开来。举例来说，如果你允许 github.com，那么 agent 就可以推送到攻击者拥有的仓库。

DNS 是 HTTP 白名单容易漏掉的第二条潜在外泄路径，因为数据可以被编码进 agent 查询的名字里。

当然，token 一旦泄漏，攻击者根本不需要 agent 的网络。他们可以从任何地方使用这份凭据，于是出口过滤永远看不到那个请求。

### 风险 4：prompt injection

自 2023 年该榜单创立以来，OWASP 在每一版 [LLM 应用 Top 10](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/) 中都把 prompt injection 列为首要风险。

社会工程与 prompt injection 的作用方式相同。社会工程之所以能绕过技术控制，是因为受骗的人自己执行了操作，系统看到的是一个已授权的请求。被注入指令的 agent 同样以自身的权限行动，而每条日志显示的都是合法请求。

对编码 agent 来说，prompt injection 可以通过多种途径发生，包括：

- issue tracker 与 pull request 评论；
- 依赖的 README 与 changelog；
- agent 抓取的网页；
- MCP 工具调用的响应；
- 源文件中的注释；等等。

网页中的一条隐藏指令，在造成危害之前必须越过哪些关卡。

## 03 判断层

分层防御 · 理解对齐训练 · prompt injection 探测 · auto mode 分类器

### 分层防御

在 Claude Code 中，一个被攻陷或对齐不良的 agent 必须先越过多重控制和两层防御，才能造成危害。

第一层基于判断。这些控制判断某件事看起来是否不对劲。

- **对齐训练**教 Claude 拒绝恶意请求，并偏好谨慎的动作。
- **prompt injection 探测**在 auto mode 下、Claude 对传入的工具结果采取行动之前扫描这些结果，并标记看起来像注入指令的内容。
- **auto mode 分类器**把多数拟议的工具调用与用户声明的意图做比对。

第二层通过限制任何命令能做什么来强制执行固定边界：

- **权限规则、命令分析和 hooks** 在动作运行之前，按你设定的规则检查每一个动作。
- **沙箱与出口白名单**限定一条被允许的命令能触及什么、数据能去往哪里。

本章讲判断层，下一章考察固定边界层。

### 理解对齐训练

Claude 的训练目标是[由一系列硬性规则支撑的良好判断](https://www.anthropic.com/constitution)，比如不编写可能造成重大损害的恶意代码。

[在 Claude Code 的测试中](https://www.anthropic.com/document/claude-fable-5-2-mythos-5-2-system-card)，在没有生产环境防护的情况下，当前的 Claude 模型拒绝了 **81% 到 85%** 的恶意请求，同时完成了 **98% 到 100%** 的双用途与良性请求，例如运行侦察工具或测试站点漏洞。

Claude 还被训练成[偏好谨慎的动作而非不可逆的动作](https://www.anthropic.com/constitution)，并在遇到疑虑时提出担忧或请求指引，而不是即兴发挥。Claude 被训练得不会把抓取内容中的指令当作来自用户的指令来执行。

请记住，模型对齐训练降低了坏结果出现的可能性，但它并不限制坏结果能坏到什么程度。

### prompt injection 探测

Claude 的 prompt injection 探测机制旨在标记工具结果中任何疑似被注入的指令。

该探测会在被注入的指令旁加上一条警告，告诉 Claude 这段内容可疑，用户的原始请求仍然是任务。警告与锚定让 Claude 可以使用这段内容，同时把其中的指令当作数据而非命令。

### auto mode 分类器

一个被说服“删除某个目录是合法任务”的模型，会以它对待一切事情时同样的彻底与娴熟把这个目录删掉。

这种破坏性的、过于积极的动作，正是 [auto mode 分类器](https://code.claude.com/docs/en/auto-mode-config)要捕获的。对于你的规则与内置审批尚未决定其命运的动作，auto mode 分类器会判断拟议的动作是否契合开发者指令的意图。

auto mode 分类器如何决定一项拟议的动作是否执行。

例如，对“修好 auth_test.py 中失败的测试”而言合理的命令，与对“把 .env 的内容外传出去”而言合理的命令，看起来是不一样的。

Claude Code 发送给分类器的请求中会剔除工具结果，因此被注入的文本无法直接操纵分类器。如果动作符合用户的要求，它就会执行；如果不符合，它会被拦截，或者 Claude 回去向开发者请求权限。

如今 Auto mode 是各套餐上交互式会话的[默认起始模式](https://code.claude.com/docs/en/permission-modes#which-mode-a-session-starts-in)。无头模式 `claude -p`、Agent SDK 与 HIPAA 配置默认使用 manual。

Auto mode 之所以成为默认，是因为[多项测试](https://claude.com/resources/articles/auto-mode-default-in-claude-code)表明它比人工审批能捕获更多危险动作。举例来说，在 Anthropic 于 2026 年 8 月发表的一项对照研究中，1,053 名付费测试者捕获了 13.6% 的危险命令，而 auto mode 拦截了同一批命令中的 89%。

人工审查与 auto mode 分别捕获的危险命令。来源：一项针对 1,053 名付费测试者的对照研究，这些测试者对所测的具体行为并不知情。

[配置 auto mode](https://code.claude.com/docs/en/auto-mode-config) 介绍了如何调整分类器，以及覆盖它的拦截规则与放行规则。

#### 批准高风险动作

Auto mode 依赖分类系统，并不能消除所有风险。

在推广之前，用这样的提问找出高风险动作：这个动作不可逆吗？单次失误的代价会不会超过让一个人审查每一个实例？当两个问题的答案都是“是”时，就要求人工批准。

对多数组织而言，这份清单大致如下：

- 生产数据库迁移
- IAM 策略变更与凭据轮换
- 对基础设施定义的修改

## 04 强制执行固定边界

设定权限规则 · Bash 命令分析 · 用 hooks 为动作设卡 · 用沙箱收束 agent 的动作

判断层善于捕获新颖的攻击，但它的控制是概率性的，因此每一项都有被攻破的可能。

固定边界层可以被做成确定性的，并划定 agent 的爆炸半径。权限规则、命令分析和 hooks 决定一项动作是否执行，沙箱与出口白名单限定能触及什么、数据能去往哪里。

它们的局限在于只拦截你让它们拦截的东西，因此需要结合你的环境来设置。

### 设定权限规则

权限规则有三种：

- `Allow` 规则让动作执行，
- `Ask` 规则在执行前询问某人，以及
- `Deny` 规则拦截该动作。

Claude Code 会先检查 [deny 规则，然后 ask 规则，最后 allow 规则](https://code.claude.com/docs/en/permissions)。这样可以避免 allow 规则为 deny 规则制造例外。托管设置中定义的 deny 规则无法被任何用户或项目设置覆盖。对于宽泛到可以运行任意代码的任何命令，例如 `Bash(python:*)`，你都应当避免设置 allow 规则。

Claude Code 先检查 deny 规则，再检查 ask 规则，最后检查 allow 规则，因此 allow 规则无法为 deny 规则制造例外。

[Subagents](https://code.claude.com/docs/en/sub-agents#permission-modes) 继承父会话的权限规则与权限模式，因此为顶层会话编写的宽泛规则会适用于它委派的每一个 agent。

### Bash 命令分析

Claude Code 会在每条 Bash 命令运行之前解析它。如果不解析，一条允许 git status 的[权限规则](https://code.claude.com/docs/en/permissions)也会批准 git status && curl attacker.example，而把一条被拒绝的命令包进子 shell 就能让它绕过规则。

Claude Code 会把一条命令拆成各个部分，并逐一对照你的规则检查。

解析是确定性的，因此同一条命令每次都会得到同样的答案。deny 与 ask 规则在每种权限模式下都会作用于命令的每个部分，包括 `bypassPermissions`。

### 用 hooks 为动作设卡

[hook](https://code.claude.com/docs/en/hooks) 是一段脚本、一个 HTTP endpoint 或一个 MCP 工具，Claude Code 会在会话中的固定节点自动运行它。其中对安全尤为重要的两个是：

- **`PreToolUse`** 在工具调用之前运行，可以拦截它、批准它、询问开发者，或（在无头运行中）延后等待稍后批准。举例来说，你可能想拦截一个包含密钥的 commit。
- **`ConfigChange`** 在会话进行中设置文件发生变化时运行，可以拒绝该变更。这就是你发现某个仓库或开发者试图在本地放松控制的方式。

Hooks 位于固定边界之内，而不是凌驾于其上。PreToolUse hook 可以拦截一次工具调用，但 hook 返回 `"allow"` 也不能越过 deny 规则、ask 规则或关键路径删除。

托管设置中定义的 hooks 会在每台机器上运行，个别开发者无法移除它们。[`allowManagedHooksOnly`](https://code.claude.com/docs/en/hooks) 更进一步，完全阻止用户、项目与 plugin hooks 运行，于是能触达 agent 的 hook 只可能是你的平台团队放进去的。

### 用沙箱收束 agent 的动作

沙箱是控制事件严重程度最重要的方式之一，因为它限定了 agent 的活动范围。但收束 agent 说起来容易做起来难，因为约束与能力往往负相关。

Claude Code 有三种主要环境：本地、带沙箱的本地，以及云端。

我们将讨论默认设置，以及如何为组织内的各种用例考虑哪一种更合适。这些默认值可以被集中修改并锁定，这将在下一章介绍。

#### 本地

多数 Claude Code 会话通过终端、IDE 或桌面应用在本地进行。默认情况下，agent 能访问你电脑上你能访问的任何东西。在 auto mode 下，分类器会审查你的规则与内置审批尚未决定其命运的动作。

这是最不受收束的环境，适合低风险、自成一体的工作。对多数企业组织，我们建议对本地会话强制启用沙箱。

#### 本地沙箱

Claude Code 沙箱在操作系统层面隔离每条 shell 命令，因此命令只能修改项目文件夹中的文件，并且只能连接白名单上的站点，除非某项例外获得批准。

命令可以修改项目。别的一切要么撞墙，要么经过检查点。

默认情况下，开发者或 auto mode 分类器在他们认为安全时，可以批准 agent 在沙箱之外操作，或访问不在白名单上的站点。

使用[托管设置](https://code.claude.com/docs/en/managed-settings)（下一章会展开），管理员可以让本地沙箱成为强制要求，把 agent 的命令限制在该沙箱内，并让 agent [只能访问集中批准的站点](https://code.claude.com/docs/en/sandboxing#network-isolation)。

一旦把 agent 收束进沙箱，你不会希望它通过读取项目之外的文件来获取凭据，从而逃逸出去。为对抗凭据泄漏，管理员可以为组织的凭据路径添加 Read deny 规则，并设置[凭据掩码](https://code.claude.com/docs/en/sandboxing#mask-credentials)，让命令可以在从不持有真实值的情况下完成登录。

#### 云会话

[**Claude Code 云会话**](https://claude.dev/blog/claude-code-in-the-cloud/)运行在 Anthropic 托管的环境中，每个任务拥有自己的 VM。这不仅收束了 Claude 能执行的位置，也把 GitHub 凭据留在 VM 之外。

云会话适合需要读取不可信内容或无人值守运行的工作。这是因为它们默认与开发者的机器和内部网络隔离，而且 VM 可以随时丢弃。

云会话的构成：每一个都运行在全新的 VM 中，GitHub 凭据留在 VM 之外。

当开发者创建新的云环境时，Claude 从一组有限的[预装工具与允许域名](https://code.claude.com/docs/en/cloud-environments#default-allowed-domains)开始，不过开发者可以添加例外。开发者每次会话都必须选择要克隆哪些 repos。

云环境设置的示意图。

组织所有者可以设定默认环境，并发布成员无法更改其中设置的共享环境。

开发者仍然可以创建新环境并修改这些环境设置。需要锁定这一点的组织会自行托管会话，在他们自行启动和运营的基础设施上运行 Claude Code，从而掌控这些会话的策略。

请记住，使用零数据保留、HIPAA 配置或客户托管加密密钥的组织无法使用云会话。

## 05 强制执行策略

集中设置一览 · 哪些设置会生效

我们在前几章介绍了默认设置。下表涵盖两种额外的配置。

我们把其中一种标记为 **baseline**，当你想建立另一套默认值——或一个允许个别开发者在此基础上追加的起点——时应当选择它。

我们把另一种标记为 **locked**，管理员借此锁定一组开发者层面无法更改的规则。锁定一项设置，正是把纸面策略变成可强制执行的安全控制的关键。

这里并非设置的完整清单，而是聚焦于限定 agent 风险的关键维度。

### 集中设置一览

|  | **本地会话**在托管设置中设定 | **云会话**在 claude.ai 管理设置中设定 |
| --- | --- | --- |
| **它被允许吗？** | 可在桌面应用中关闭（`disableDesktopLocalSessions`），终端中不可关闭 | 组织级的云会话开关 |
| **它被收束到什么程度？** | **Baseline：** 所有本地会话开启沙箱（`sandbox.enabled`）**Locked：** 不开启就不运行，也不做未沙箱化的重试（`failIfUnavailable`、`allowUnsandboxedCommands: false`） | **Baseline：** 所有者在 Cloud environments 页面创建成员无法更改设置的共享环境，并选定其中一个作为组织的默认环境**Locked：** 在你自行运营的基础设施上运行 Claude Code。在 Anthropic 托管的环境中，开发者仍可创建带自己设置的个人环境 |
| **它能连接到哪里？** | **Baseline：** 一份托管的批准站点清单，开发者可以在其中添加（`sandbox.network.allowedDomains`）**Locked：** 只有你的清单算数（`allowManagedDomainsOnly`）。该清单覆盖 shell 命令，因此要用 WebFetch 工具自身的权限规则来限制它 | **Baseline：** 默认使用 Anthropic 的可信清单（包注册中心、GitHub、云 SDK），或所有者在每个共享环境上设定的网络访问（connector、GitHub 与 Anthropic API 流量不受此设置限制）**Locked：** 使用[自托管环境](https://code.claude.com/docs/en/self-hosted-environments)（公开 beta），由你自己的网络边界限制连接。Anthropic 托管的环境没有组织级白名单 |
| **它能读取什么？** | **Baseline：** 针对敏感路径的 Read deny 规则（`permissions.deny`）**Locked：** 把文件工具的读取限制在项目内，并阻止列出路径（`permissions.blockReadsOutsideWorkingDirectories`、`sandbox.filesystem.denyRead`） | **Baseline：** 同样的 Read deny 规则**Locked：** 无法完全锁定。把 Claude GitHub App 限制在批准的 repositories 上，以控制会话能克隆和推送什么。开发者仍可从终端上传本地 repository。 |
| **它能使用哪些凭据？** | 用 Read deny 规则阻止凭据文件，并设置凭据掩码（`sandbox.credentials`） | 所有者把密钥作为共享环境上的 Network secrets 存储，绝不要存成环境变量。 |
| **它能使用哪些 connectors？** | **Baseline：** 一份批准的清单，开发者可以在其中添加（`allowedMcpServers`）。**Locked：** 只有你的清单算数（`allowManagedMcpServersOnly`）桌面应用自带的 connectors 会跳过该清单，并受组织 connector 设置的限制。 |  |
| **它不问就能做什么？** | **Baseline：** 托管的 deny 与 ask 规则，开发者可自行添加 allow 规则。**Locked：** 只有你的规则与 hooks 生效，且 bypass 模式关闭（`allowManagedPermissionRulesOnly`、`allowManagedHooksOnly`、`permissions.disableBypassPermissionsMode`）。 |  |

### 哪些设置会生效

托管设置可以通过三种途径到达会话：来自 Claude 管理控制台的服务器托管设置、MDM 或操作系统级策略，以及托管设置文件。只有服务器托管设置能到达 Anthropic 托管的云会话。

默认情况下，Claude Code 使用第一个含有策略键的来源。把 managedSourcesBehavior 设为 “merge” 会把各管理来源合并起来。

默认情况下，[Claude Code 只应用排名最高的来源，并忽略其余来源](https://code.claude.com/docs/en/managed-settings#how-claude-code-combines-managed-sources)，按此顺序，且不给任何警告。如果你的 MDM 配置档开启了沙箱，而托管设置文件里放着出口白名单，那么该白名单永远不会生效。

## 06 上手

本指南中的控制是分层起效的，每一层都覆盖其他层漏掉的部分。在一个 repository 上做试点，可以在扩大推广之前看清这些层在你的环境中如何发挥作用。

试点清单

**给 repositories 分级，并做供应商审查。** 按敏感度给 agent 将要触及的 repositories 排序，然后对照第 1 章的要求检查你的供应商。

**从最低一档中挑一个 repository，** 比如一个正在积极开发中的内部工具。它应当足够繁忙，能产生真实的会话，又足够低风险，失手时代价很小。

**部署一套集中策略基线。** 以严格模式开启沙箱，对凭据路径设置 deny 规则、凭据掩码、出口白名单，并启用 auto mode。设定并配置一个默认云环境。添加 `security-guidance` plugin，以及任何强制你不可让步规则的 hooks。

**打开记录。** 启用带工具内容的 OpenTelemetry 导出（beta），并确保沙箱与出口日志已被保留。

**在两周内不改动策略地运行，** 这样每个结果都能追溯回同一套配置。

**复盘这些层做了什么。** 查看分类器的拒绝、沙箱的拦截、未沙箱化的重试尝试以及被拒绝的出口。每一项要么是控制发挥了作用，要么是基线没有预想到的正当需求。应当补充工作所需的 allowlist 条目，而不是放松 deny 规则。

**在扩展到第二个团队之前，对照第 1 章的五个问题给试点打分。**

做对了，这套安全框架会加速而不是拖慢你的团队用编码 agent 全速运转的能力。

*¹ Salesforce Ventures 是 Anthropic 的投资方。*
