---
vendor: anthropic
title: 用 Agent Skills 为 agent 装备现实世界的能力
original_title: Equipping agents for the real world with Agent Skills \ Anthropic
url: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
date: 2025-10-16
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

Anthropic 工程实践

# 用 Agent Skills 为 agent 装备现实世界的能力

发布于 2025 年 10 月 16 日

Claude 很强大，但真实工作需要程序性知识和组织上下文。我们推出 Agent Skills——一种用文件和文件夹构建专用 agent 的新方式。

*更新：我们已把* [*Agent Skills*](https://agentskills.io/) *作为一项开放标准发布，以实现跨平台可移植性。（2025 年 12 月 18 日）*

随着模型能力提升，我们现在可以构建与完整计算环境交互的通用 agent。例如 [Claude Code](https://claude.com/product/claude-code) 能通过本地代码执行和文件系统，跨领域完成复杂任务。但随着这些 agent 变得更强大，我们需要更可组合、可扩展、可移植的方式，来为它们装备领域专有的专业知识。

这促使我们创建了 [**Agent Skills**](https://www.anthropic.com/news/skills)：有组织的指令、脚本和资源文件夹，agent 可以动态地发现并加载它们，从而在特定任务上表现得更好。Skills 通过把你的专业知识打包成 Claude 可组合的资源，扩展 Claude 的能力，把通用 agent 变成契合你需求的专用 agent。

为一个 agent 构建一个 skill，就像为新员工编一份入职指南。不必为每个用例去构建零散、定制设计的 agent，任何人都可以通过捕捉并分享他们的程序性知识，用可组合的能力来专业化他们的 agent。在本文里，我们解释 Skills 是什么、展示它们如何工作，并分享构建你自己 skills 的最佳实践。

一个 skill 是一个包含 SKILL.md 文件的目录，里面有有组织的指令、脚本和资源文件夹，为 agent 提供额外能力。

## skill 的构造

要看 Skills 如何运作，我们来走一遍一个真实例子：驱动 Claude 最近发布文档编辑能力的 skills 之一。Claude 本已对理解 PDF 知之甚多，但在直接操作 PDF（例如填写一份表单）上受限。这个 [PDF skill](https://github.com/anthropics/skills/tree/main/document-skills/pdf) 让我们能赋予 Claude 这些新能力。

最简单地说，skill 是一个包含 `SKILL.md` 文件的目录。这个文件必须以包含一些必填元数据的 YAML frontmatter 开头：`name` 和 `description`。在启动时，agent 把每个已安装 skill 的 `name` 和 `description` 预加载进它的系统 prompt。

这份元数据是*渐进式披露（progressive disclosure）*的**第一层**：它只提供恰到好处的信息，让 Claude 知道每个 skill 该在何时被使用，而无需把全部内容加载进上下文。这个文件的实际正文是**第二层**细节。如果 Claude 认为该 skill 与当前任务相关，它会通过读取完整的 `SKILL.md` 进上下文来加载这个 skill。

一个 SKILL.md 文件必须以包含文件名和描述的 YAML frontmatter 开头，这会在启动时加载进它的系统 prompt。

随着 skill 变得复杂，它们可能包含太多无法塞进单个 `SKILL.md` 的上下文，或只在特定情景下才相关的上下文。在这些情况下，skill 可以在其目录里捆绑额外文件，并在 `SKILL.md` 中按名字引用它们。这些额外链接的文件是（第三层及更）细节，Claude 可以选择只在需要时才去浏览和发现它们。

在下面展示的 PDF skill 里，`SKILL.md` 引用了两个额外文件（`reference.md` 和 `forms.md`），skill 作者选择把它们与核心 `SKILL.md` 捆绑在一起。通过把填表指令移到单独的文件（`forms.md`），skill 作者得以让 skill 的核心保持精简，并信任 Claude 只会在填表时才去读 `forms.md`。

你可以通过额外文件把你的更多上下文并入 skill，随后由 Claude 基于系统 prompt 触发。

渐进式披露是让 Agent Skills 灵活、可扩展的核心设计原则。就像一本组织良好的手册，从目录开始，到具体章节，最后是详细的附录，skills 让 Claude 只在需要时加载信息：

带文件系统和代码执行工具的 agent，在处理某个具体任务时，无需把一个 skill 的全部内容读进它的上下文窗口。这意味着能捆绑进一个 skill 的上下文量，实际上是无上限的。

### Skills 与上下文窗口

下图展示了当一个 skill 被用户消息触发时，上下文窗口如何变化。

Skills 通过你的系统 prompt 在上下文窗口中被触发。

图中展示的操作顺序：

- 起初，上下文窗口里有核心系统 prompt、每个已安装 skill 的元数据，以及用户的初始消息；
- Claude 通过调用一个 Bash 工具读取 `pdf/SKILL.md` 的内容，来触发 PDF skill；
- Claude 选择读取与该 skill 捆绑的 `forms.md` 文件；
- 最后，在从 PDF skill 加载了相关指令之后，Claude 继续处理用户的任务。

### Skills 与代码执行

Skills 还能包含供 Claude 在其酌情下作为工具执行的代码。

大语言模型擅长许多任务，但某些操作更适合传统的代码执行。例如，通过 token 生成来排序一个列表，比直接运行一个排序算法昂贵得多。除了效率考量，许多应用需要只有代码才能提供的确定性可靠性。

在我们的例子里，PDF skill 包含一个预先写好的 Python 脚本，它读取一份 PDF 并提取全部表单字段。Claude 可以运行这个脚本，而无需把脚本或 PDF 加载进上下文。而且因为代码是确定性的，这个工作流一致且可重复。

Skills 还能包含供 Claude 基于任务性质、在其酌情下作为工具执行的代码。

## 开发与评估 skills

下面是一些帮助你着手编写和测试 skills 的有用指南：

- **从评估开始：** 通过在代表性任务上运行你的 agent、并观察它们在何处吃力或需要额外上下文，来识别你 agent 能力上的具体缺口。然后逐步构建 skills 来弥补这些不足。
- **为规模化而组织：** 当 `SKILL.md` 文件变得臃肿时，把它的内容拆分成单独的文件并加以引用。如果某些上下文互斥或很少一起使用，把它们的路径分开会减少 token 用量。最后，代码既能作为可执行工具，也能作为文档。应当清楚 Claude 是该直接运行脚本，还是把它们读进上下文作为参考。
- **站在 Claude 的角度思考：** 监控 Claude 在真实场景中如何使用你的 skill，并基于观察迭代：留意出人意料的轨迹或对某些上下文的过度依赖。特别关注你 skill 的 `name` 和 `description`。Claude 在其响应当前任务决定是否触发 skill 时会用到这些。
- **与 Claude 一起迭代：** 当你与 Claude 合作处理一项任务时，请 Claude 把它的成功做法和常见错误捕捉成可复用的上下文和代码，纳入一个 skill。如果它在使用某 skill 完成任务时跑偏，请它自我反思哪里出了问题。这个过程会帮你发现 Claude 实际需要什么样的上下文，而不是试图提前预判它。

### 使用 Skills 时的安全考量

Skills 通过指令和代码为 Claude 提供新能力。这虽然让它们强大，也意味着恶意 skill 可能在其被使用的环境中引入漏洞，或指示 Claude 外泄数据、采取非预期动作。

我们建议只从受信任的来源安装 skill。当从一个不太受信任的来源安装 skill 时，在使用前彻底审计它。先阅读该 skill 捆绑文件的内容以理解它做什么，特别留意代码依赖和捆绑的资源，如图像或脚本。同样，留意 skill 里那些指示 Claude 连接到可能不受信任的外部网络源的指令或代码。

## Skills 的未来

Agent Skills 今天已[获得支持](https://www.anthropic.com/news/skills)，横跨 [Claude.ai](http://claude.ai/redirect/website.v1.beb1e262-5397-47f2-839b-5856b13cd1bd)、Claude Code、Claude Agent SDK 和 Claude Developer Platform。

接下来几周，我们会继续添加功能，支持创建、编辑、发现、分享和使用 Skills 的完整生命周期。我们对 Skills 能帮助组织和个人与 Claude 分享其上下文和工作流的机会尤其感到兴奋。我们也会探索 Skills 如何与 [Model Context Protocol](https://modelcontextprotocol.io/)（MCP）服务器互补，通过教 agent 那些涉及外部工具和软件的更复杂工作流。

更长远看，我们希望让 agent 能自行创建、编辑和评估 Skills，让它们把自己的行为模式编码成可复用的能力。

Skills 是一个简单的概念，有着相应简单的格式。这种简单使组织、开发者和终端用户更容易构建定制化 agent、并赋予它们新能力。

我们很期待看到人们用 Skills 构建什么。查看我们的 Skills [文档](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)和 [cookbook](https://github.com/anthropics/claude-cookbooks/tree/main/skills)，今天就上手。

## 致谢

本文由 Barry Zhang、Keith Lazuka 和 Mahesh Murag 撰写——他们都非常喜欢文件夹。特别感谢 Anthropic 内许多倡导、支持并构建 Skills 的其他人。
