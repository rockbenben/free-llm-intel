---
vendor: openai
title: 解锁 Codex 运行框架：我们如何构建 App Server
original_title: 
url: https://openai.com/index/unlocking-the-codex-harness
date: 2026-09-11
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: native
status: translated
body_sha: 9be21066d92e
---


2026年2月4日

工程

# 解锁 Codex 运行框架：我们如何构建 App Server

Celia Chen，技术团队成员


OpenAI 的编码智能体 Codex 部署于多个不同的平台：[Web 应用](https://chatgpt.com/codex)、[CLI](https://github.com/openai/codex)、[IDE 扩展](https://developers.openai.com/codex/ide/)，以及[新的 Codex macOS 应用](https://openai.com/index/introducing-the-codex-app/)。其底层架构均由同一个 Codex 运行框架驱动 — 支撑着所有 Codex 体验的智能体循环和逻辑。它们之间有何重要关联？[Codex App Server](https://developers.openai.com/codex/app-server) 是客户端友好型双向 JSON-RPC[1](https://openai.com/zh-Hans-CN/index/unlocking-the-codex-harness/#citation-bottom-1) API。

在这篇文章中，我们将介绍 Codex App Server，并分享我们迄今为止所掌握的经验，助你将 Codex 的功能引入产品，以便用户能够大幅提升工作流效率。我们将介绍 App Server 的架构和协议，及其如何与不同的 Codex 界面集成，并分享利用 Codex 的技巧；无论你是想让 Codex 充当代码审查员、SRE 智能体，还是编程助手，它都能助你一臂之力。

## App Server 的起源

在深入了解架构之前，不妨先看看 App Server 的背景故事。最初，App Server 是一种在不同产品中复用 Codex 运行框架的实用方法，后来逐渐演变为我们的标准协议。

Codex CLI 最初曾作为 TUI（终端用户界面），这意味着你可以通过终端访问 Codex。当我们构建 VS Code 扩展（一种更适用于与 Codex 智能体交互的 IDE 友好型方案）时，我们需要应用相同的运行框架，在不重新实施的情况下，从 IDE 用户界面 (UI) 驱动相同的智能体循环。这意味着要支持超越请求/响应的丰富交互模式，例如探索工作空间、在智能体进行推理时流式传输进程，以及输出差异。我们最初尝试将 [Codex 作为 MCP 服务器](https://github.com/openai/codex/pull/2264)对外发布，但我们发现难以运用 VS Code 方案来维护 MCP 语义。相反，我们引入了一个类似 TUI 循环的 JSON-RPC 协议，它成为了 App Server 的[非官方首发版本](https://github.com/openai/codex/pull/4471)。当时，我们并未预料到其他客户会选择 App Server，因为其设计初衷并非是构建稳定的 API。

在接下来的几个月里，随着 Codex 的应用率不断增长，内部团队和外部合作伙伴希望能够在其自研产品中嵌入同一个运行框架，以加速其用户的软件开发工作流。例如，JetBrains 和 Xcode 希望获得 IDE 级智能体体验，而 Codex 桌面应用则需要并行编排多个 Codex 智能体。这些需求促使我们设计了一个平台界面，确保我们的产品和合作伙伴集成能够基于该平台实现长期稳定运行。它既要易于集成，又要向后兼容，这意味着我们可以在不破坏现有客户端的情况下优化该协议。

接下来，我们将逐步介绍如何设计相关架构和协议，以便不同的客户端可以应用同一个运行框架。

## 在 Codex 运行框架内

首先，让我们聚焦于 Codex harness 内部的运行框架，以及 Codex App Server 如何向客户端呈现这一框架。在上一篇 Codex [博客](https://openai.com/index/unrolling-the-codex-agent-loop/)中，我们拆解了用于协调用户、模型和工具间交互的核心智能体循环。这正是 Codex 运行框架的核心逻辑，但完整的智能体体验远不止于此：

**1. 线程生命周期和持久性**。线程是用户与智能体间的 Codex 对话。Codex 可创建、恢复、派生和归档线程，并持久保存事件历史记录，以便客户端重新连接并呈现一致的时间线。

**2. 配置和身份验证**。Codex 可加载配置、管理默认值，并运行“使用 ChatGPT 登录”等身份验证流程，包括凭据状态。

**3. 工具执行和扩展**。Codex 可在沙盒中执行 shell/文件工具，并连接 MCP 服务器和技能等集成，从而根据一致的策略模式参与智能体循环。

我们在此提到的所有智能体逻辑（包括核心智能体循环），都位于 Codex CLI 代码库中名为“[Codex 核心](https://github.com/openai/codex/tree/main/codex-rs/core)”的模块内。“Codex 核心”既是一个存放所有智能体代码的存储库，也是一个可启动的运行时环境，可用于运行智能体循环并管理 Codex 线程（对话）的持久性。

为了发挥效力，Codex 运行框架需要授予客户端访问权限。这正是 App Server 的“用武之地”。

App Server 既是客户端与服务器间的 JSON-RPC 协议，也是托管 Codex 核心线程的长期进程。如上图所示，App Server 进程包含四个主要组件：stdio 读取器、Codex 消息处理器、线程管理器和核心线程。线程管理器可为每个线程启动一个核心会话，Codex 消息处理器则可直接与每个核心会话通信，以提交客户端请求并接收更新。

一个客户端请求可能会导致多个事件更新，正是这些详细的事件支持我们在 App Server 上构建丰富的用户界面。此外，stdio 读取器和 Codex 消息处理器可作为客户端与 Codex 核心线程间的转换层。它们可将客户端 JSON-RPC 请求转换为 Codex 核心操作，监听 Codex 核心的内部事件流，然后将这些低级事件转换为一小组稳定的用户界面就绪型 JSON-RPC 通知。

客户端与 App Server 间的 JSON-RPC 协议处于完全双向模式。典型的线程包含一个客户端请求和多个服务器通知。此外，当智能体需要输入（例如审批）时，服务器可以发起请求，然后暂停该轮次，直到客户端响应。

## 对话原语

接下来，我们将拆解对话原语，即 App Server 协议的构建模块。为智能体循环设计 API 颇为棘手，因为用户/智能体交互并非简单的请求/响应。一个用户请求可能会展开为一系列结构化的操作序列，客户端需要忠实呈现相应信息：用户的输入、智能体的增量进度，以及在此过程中产生的工件（例如，差异文件）。为了确保交互流易于集成并在各种用户界面中保持弹性，我们确定了三个包含明确边界和生命周期的核心原语：

**1. 项目：**项目是 Codex 中输入/输出的基本单位。各个项目都有相应的类型（例如，用户消息、智能体消息、工具执行、审批请求、差异），并且每一个项目都有明确的生命周期：

- `item/started`：当项目开始时
- 可选的 `item/*/delta` 事件：作为内容流输入（用于流式项目类型）
- `item/completed`：当项目完成其终端负载时

此生命周期允许客户端在 `started` 时立即开始渲染，在 `delta` 时流式传输增量更新，并在 `completed` 时最终完成处理。

**2. 轮次**：轮次是由用户输入发起的智能体工作单位。当客户端提交输入（例如，“运行测试并总结失败”）时，轮次就会启动；当智能体为该输入生成输出时，轮次就会终止。一个轮次包含一系列项目，这些项目代表了在此过程中产生的中间步骤和输出结果。

**3. 线程**：线程是用户与智能体间正在进行的 Codex 会话的持久容器。它包含多个轮次。线程可以被创建、恢复、派生和归档。线程历史记录会被持久化保存，以便客户端重新连接并呈现一致的时间线。

现在，我们来看看客户端和智能体间的简化对话，该对话由原语表示：

在对话开始时，客户端和服务器需要建立 `initialize` 握手。客户端必须在调用任何其他方法前发送一个 `initialize` 请求，服务器会通过响应进行确认。这样，服务器就能展现自己的能力，并确保双方在真正投入运行前就协议版本、功能标志和默认值达成一致。以下是 OpenAI VS Code 扩展的负载示例：

#### JSON

```
1{2  "method": "initialize",3  "id": 0,4  "params": {5    "clientInfo": {6      "name": "codex_vscode",7      "title": "Codex VS Code Extension",8      "version": "0.1.0"9    }10  }11}
```

以下是服务器返回的内容：

#### JSON

```
1{2  "id": 0,3  "result": {4    "userAgent": "codex_vscode/0.94.0-alpha.7 (Mac OS 26.2.0; arm64) vscode/2.4.22 (codex_vscode; 0.1.0)"5  }6}
```

当客户端发起新请求时，它会先创建一个线程，然后创建一个轮次。服务器将返回进度通知（`thread/started` 和 `turn/started`）。它还会返回自身识别为项目的输入，比如此示例中的用户消息。

工具调用也会作为项目发送回客户端。此外，服务器在执行操作之前，可能会通过发送服务器请求来请求客户端进行审批。审批将暂停该轮次，直到客户端回复“允许”或“拒绝”。VS Code 扩展中的审批流程如下：

最后，服务器会发送一条智能体消息，然后以 `turn/completed` 结束该轮次。智能体消息增量事件会持续流式返回消息片段，直到消息以 `item/completed` 收尾。

为便于理解，示意图中的信息已经过简化。如果你想查看完整轮次的 JSON，可以从 Codex CLI 代码仓库运行测试客户端：

#### Bash

```
1codex debug app-server send-message-v2 "run tests and summarize failures"
```

## 与客户端集成

现在，让我们看看不同的客户端界面如何通过 App Server 嵌入 Codex。我们将介绍三种模式：本地应用和 IDE、Codex Web 运行时，以及 TUI。

在上述三种模式中，传输方式均为 JSON-RPC over stdio (JSONL)。JSON-RPC 可助你使用所选的语言，轻松构建客户端绑定。Codex 界面和合作伙伴集成已在 Go、Python、TypeScript、Swift 和 Kotlin 等多种语言中部署 App Server 客户端。对于 TypeScript，你可以通过运行以下命令直接从 Rust 协议生成定义：

#### Bash

```
1codex app-server generate-ts
```

对于其他语言，你可以生成一个 JSON 模式捆绑包，并通过运行以下命令将其输入到你首选的代码生成器中：

#### Bash

```
1codex app-server generate-json-schema
```

#### 本地应用和 IDE

本地客户端通常会捆绑或获取特定平台的 App Server 二进制文件，将其作为一个长期运行的子进程启动，并为 JSON-RPC 开通一个双向 stdio 通道。例如，在我们的 VS Code 扩展和桌面应用中，随附的工件包含特定平台的 Codex 二进制文件，并固定为已测试版本，以便客户端始终运行与验证完全一致的代码。

并非所有集成都能频繁发布客户端更新。部分合作伙伴（如 Xcode）通过保持客户端稳定，并在需要时允许其指向更新的 App Server 二进制文件，解耦发布周期。这样一来，他们就可以应用服务器端的优化（例如，Codex 核心中更好的自动压缩或新的支持配置键），并推出错误修复程序，而无需等待客户端发布。App Server 的 JSON-RPC 接口采用向后兼容设计，因此旧版客户端可以安全地与新版服务器通信。

#### Codex Web

Codex Web 使用 Codex 运行框架，但其在容器环境中运行。工作节点会提供一个包含已签出工作空间的容器，在其中启动 App Server 二进制文件，并通过 stdio[2](https://openai.com/zh-Hans-CN/index/unlocking-the-codex-harness/#citation-bottom-2) 通道维护长期运行的 JSON-RPC。Web 应用（在用户的浏览器标签页中运行）通过 HTTP 和 SSE 与 Codex 后端对话，后者则会流式传输由工作节点生成的任务事件。这样既能保持浏览器端用户界面的轻量化状态，又能在桌面和 Web 端保持一致的运行时。

由于网页会话为临时性质（标签页关闭、网络中断），因此 Web 应用不能作为长期任务的可信数据源。在服务器上保留状态和进度意味着，即使标签页消失，任务也会继续运行。流式传输协议和已保存的线程会话可支持新会话轻松实现重新连接、从中断处继续运行，并快速同步状态，而无需在客户端内重建状态。

#### TUI/Codex CLI

就传统意义而言，TUI 是一个“原生”客户端，它在与智能体循环相同的进程中运行，且直接与 Rust 核心类型通信，而非使用应用服务器协议。这有助于提高早期迭代速度，同时也会让 TUI 成为特殊的界面。

既然 App Server 已经存在，我们计划[重构 TUI](https://github.com/openai/codex/pull/10192) 以投入实际应用，确保其发挥类似于其他客户端的作用：启动一个 App Server 子进程，通过 stdio 进行 JSON-RPC 通信，并渲染相同的流式事件和审批。这样一来，TUI 就可以连接远程设备上运行的 Codex 服务器，确保智能体部署于接近计算资源的位置，即使笔记本电脑休眠或断开连接也能继续运行，同时还能在本地实现实时更新和控制。

## 选择合适的协议

Codex App Server 将是我们今后维护的首要集成方案，但也有其他功能较为有限的方法。默认情况下，我们建议客户使用 Codex App Server 与 Codex 集成，借鉴其他集成方法并深入研究其优缺点。以下是驱动 Codex 的最常见方式，以及每种方式的应用场景。

### JSON-RPC 协议

#### 作为 MCP 服务器的 Codex

运行 [`codex mcp-server`](https://developers.openai.com/codex/guides/agents-sdk/)，然后从任何支持 stdio 服务器的 MCP 客户端连接（例如，[OpenAI Agents SDK](https://openai.github.io/openai-agents-js/)）。如果你已构建基于 MCP 的工作流，并希望将 Codex 作为可调用的工具，那么这一方案就是理想选择。其缺点在于，你只能获取 MCP 公开的内容，因此依赖更丰富会话语义（例如，差异更新）的 Codex 特定交互可能无法通过 MCP 端点清晰映射。

#### 跨提供商智能体运行框架协议

部分生态系统可面向多个模型提供商和运行时环境提供可移植接口。如果你需要借助抽象化来协调多个智能体，这就是一个不错的选择。其代价在于，这些协议往往趋同于通用的功能子集，这可能会使更丰富的交互难以表示，特别是当特定提供商的工具和会话语义至关重要时。这一领域正在迅速发展，我们预计，随着 OpenAI 不断探索用于表示真实智能体工作流的最佳原语，更多的通用标准也会相继涌现（[技能](https://agentskills.io/home)就是其中的典型案例）。

#### Codex App Server

当你希望将完整的 Codex 运行框架以稳定的用户界面友好型事件流形式展示时，请选择 App Server。你将同时获得智能体循环的完整功能，以及其他支持功能，例如使用 ChatGPT 登录、模型发现和配置管理。其主要成本在于集成工作，因为你需要使用所选的语言构建客户端的 JSON-RPC 绑定。但实际上，如果你向 Codex 提供 JSON 模式和文档，它就能完成大量繁重的工作。与我们合作的许多团队都会使用 Codex 快速开发可用集成。

### 嵌入 Codex 的其他方法

#### [Codex Exec](https://developers.openai.com/codex/cli/reference/#codex-exec)

一种轻量级、可编写脚本的 CLI 模式，适用于一次性任务和 CI 运行。它适用于自动化和管道场景，在这些场景中，你希望通过一条命令以非交互形式实现全程运行，为日志流式传输结构化输出，并在退出时发出明确的成功或失败信号。

#### [Codex SDK](https://developers.openai.com/codex/sdk/)

TypeScript 代码库，用于在你自己的应用程序中以编程方式控制本地 Codex 智能体。当你希望为服务器端工具和工作流提供原生库接口，而无需构建单独的 JSON-RPC 客户端时，它就是最佳选择。由于它比 App Server 更早发布，目前支持的语言较少，且覆盖范围也较小。如果开发人员有意了解相关信息，我们可能会添加更多封装 App Server 协议的 SDK，以便你的团队覆盖更多的运行框架界面，而无需编写 JSON-RPC 绑定。

## 推进相关工作

在这篇文章中，我们分享了如何设计与智能体交互的新标准，以及如何将 Codex 运行框架转变为稳定的客户端友好型协议。我们介绍了 App Server 如何公开 Codex 核心，如何支持客户端驱动整个智能体循环，以及如何为 TUI、本地 IDE 集成和网络运行时等环境提供动力。

如果这激发了你将 Codex 集成至专属工作流的灵感，那么 App Server 值得一试。所有源代码都存放在 Codex CLI 开源[代码仓库](https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md)中。欢迎你分享反馈意见和功能建议。我们期望收到你的回复，并将继续面向所有用户推广智能体。


## 作者

Celia Chen

## 致谢

特别鸣谢 Michael Bolin、Owen Lin、Eric Traut 和 Rasmus Rygaard 参与本文的撰稿工作，以及从事 App Server 开发工作的 Codex 团队全体成员。

## 脚注

- 1我们使用“JSON‑RPC lite”的变体：它能保留请求/响应/通知的结构，但会省略 `"jsonrpc": "2.0"` 标头，且采用 JSONL over stdio 格式，而非严格的 JSON‑RPC 2.0.
- 2“stdio” 指的是容器内应用服务器的 stdin/stdout。在托管设置中，这些数据流通常通过持久化网络连接（例如，类似 WebSocket 的网络连接）信道传输到容器运行时 — 因此其行为近似于 stdio，即使它并非字面意义上的本地管道。
