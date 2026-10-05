---
vendor: openrouter
title: 给任意模型配上终端和文件
original_title: Give any model a terminal and files
url: https://openrouter.ai/blog/announcements/shell-tool
date: 2026-09-08
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# 给任意模型配上终端和文件

Brian Thomas · 2026-09-08

我们推出 `openrouter:shell` 服务端工具（server tool）和 Files API：OpenRouter 上的任意模型现在都可以在托管的 Linux 容器中运行命令。Files API 支持上传文件供模型处理，也支持下载产出文件。两者今天即以 beta 形式开放。

Shell 和 Files 加入了我们不断壮大的 [server tools](https://openrouter.ai/docs/guides/features/server-tools) 列表，让你可以创建可在不同模型间无缝切换的服务端 agentic 行为。例如，你可以让任意模型搜索网络、编写一个把结果转成图表的脚本，并完全使用服务端算力运行它。

![Shell 工具、容器与 Files API 如何协同工作的示意图。模型编写命令，shell 工具在容器中运行它们，Files API 负责把文件移入移出该容器（浅色模式）](https://openrouter.ai/blog/images/shell-tool-concepts-light.png)

![Shell 工具、容器与 Files API 如何协同工作的示意图。模型编写命令，shell 工具在容器中运行它们，Files API 负责把文件移入移出该容器（深色模式）](https://openrouter.ai/blog/images/shell-tool-concepts-dark.png)

可以在 [chatroom](https://openrouter.ai/chat) 中打开 shell 工具开关来试用，并阅读 [shell](https://openrouter.ai/docs/guides/features/server-tools/shell)、[containers](https://openrouter.ai/docs/guides/features/containers) 和 [Files API](https://openrouter.ai/docs/guides/features/files-api) 指南了解 API 细节。沙箱时间按每秒 $0.0001 计费，随请求一并计费，且包含 Files API 的使用。详见 [Pricing](https://openrouter.ai/blog/announcements/shell-tool/#pricing) 一节。

## Shell 的工作原理

要使用 `openrouter:shell`，把它放进任意支持工具调用（tool calling）的模型的 `tools` 数组即可。这让模型自行决定何时需要终端、何时调用它：

```
curl https://openrouter.ai/api/v1/responses \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek/deepseek-v4-pro-0813",
    "input": "Check the Python version, then write a script that prints the first 20 primes and run it.",
    "tools": [
      { "type": "openrouter:shell", "parameters": { "engine": "openrouter" } }
    ]
  }'
```

我们引入了三项协同工作的能力，提供服务端命令执行与文件能力：

- **Shell 和 Bash**：我们支持 OpenAI 兼容的 Shell 工具，可用于 [Responses API](https://openrouter.ai/docs/api/api-reference/responses/create-a-response) 和 [Anthropic Messages API](https://openrouter.ai/docs/api/api-reference/anthropic-messages/create-a-message)；同时也支持 Anthropic 兼容的 Bash 工具 `openrouter:bash`，用于 Messages API。两者都适用于任何模型。
- **Files API**：位于 [`/api/v1/files`](https://openrouter.ai/docs/api/api-reference/files/upload-a-file) 下的 workspace 存储。上传文件、按 id 附加到容器、并保留某次运行产出的文件。
- **Containers**：即 shell 命令运行的沙箱。共享同一 container id 的请求之间，写入其中的文件会持续保留。你可以通过 [`/api/v1/containers` API](https://openrouter.ai/docs/guides/features/containers#download-container-files) 访问容器内容。

当模型调用该工具时，会发出一批命令。它们在容器内逐条执行，每条各自一次调用，并把 `stdout`、`stderr` 和退出码返回给模型。这让模型能针对收到的输出作出反应。例如，如果它写了一个解析你的 CSV 的脚本而解析失败，它能在 `stderr` 上看到问题所在，并在回答前修复脚本。

[Logs 页面](https://openrouter.ai/logs)上的生成详情视图会把请求以时间线展示。模型轮次和沙箱运行各占独立的一行，每行有自己的耗时和费用：

![带 shell 工具的请求的 server-tool 生成时间线，显示模型轮次、工具调用、shell 工具运行以及后续的模型轮次，各自带有独立的耗时和费用](https://openrouter.ai/blog/images/shell-tool-timeline.png)

## Shell 与 bash

我们发布了两个不同的沙箱命令执行工具，以同时兼容 OpenAI 和 Anthropic 的规范。最显著的区别是：bash 工具默认请求由你的应用本地执行命令。在 OpenRouter 上，你可以更改 engine 来覆盖这一行为，改在服务端执行。

|  | `openrouter:shell` | `openrouter:bash` |
| --- | --- | --- |
| 兼容 | OpenAI 的 `shell` 工具 | Anthropic 的 bash 工具 |
| API | Responses、Messages | Messages |
| 默认命令执行位置 | OpenRouter 沙箱 | 你的应用程序 |

在任一工具上设置 **`engine: "openrouter"`**，即可保证在 OpenRouter 沙箱内对任何模型进行服务端执行。

## 容器

容器是 OpenRouter 基础设施上、限定在你 workspace 范围内的隔离 Linux 环境。容器可以按你的应用需求配置：

- **网络**：出站访问默认关闭。对于 `pip3 install` 这类任务，把 `network_policy` 设为允许列表，例如 `{ "type": "allowlist", "allowed_domains": ["pypi.org", "files.pythonhosted.org"] }`，或使用 `{ "type": "allowlist", "allowed_domains": ["*"] }` 实现不受限的出站。允许列表中的主机可通过 80 和 443 端口访问；访问允许列表之外的域名会以 HTTP 520 失败，而不是连接错误。容器启动后策略不可更改。
- **文件**：只有家目录（`/workspace/home`）下的文件会被捕获。每个 shell 结果还会返回该命令创建或修改的文件 id 列表（前缀为 `cfile_`）。[container files endpoint](https://openrouter.ai/docs/api/api-reference/containers/list-container-files) 列出容器中保存的所有文件，而 [Files API](https://openrouter.ai/docs/guides/features/files-api) 用于文件的进出传输。
- **跨请求复用**：默认情况下每次会话获得一个全新容器。如果请求带有一个 `session_id`，或带有此前 shell 结果中可识别的容器，则该容器会被复用。要明确指定容器，在工具的 `environment` 字段传入 `{ "type": "container_reference", "container_id": "my-project" }`。
- **生命周期**：容器空闲 5 分钟后进入休眠，此时间不可配置。

## 文件与 shell 协同使用

[Files API](https://openrouter.ai/docs/guides/features/files-api) 是与容器并列的 workspace 存储。你把输入上传到那里供 shell 处理，也把 shell 的产出放回那里。

### 上传供 shell 使用的文件

用 [`POST /api/v1/files`](https://openrouter.ai/docs/api/api-reference/files/upload-a-file) 上传输入。响应会包含一个以 `or_file_` 开头的文件 id：

```
curl https://openrouter.ai/api/v1/files \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -F "file=@data/sales.csv"
```

然后在工具的 `environment` 中按 id 附加它：

```
{
  "type": "openrouter:shell",
  "parameters": {
    "engine": "openrouter",
    "environment": {
      "type": "container_auto",
      "file_ids": ["or_file_011CNha8iCJcU1wXNR6q4V8w"]
    }
  }
}
```

附加的文件会以可写副本的形式出现在家目录中，每个容器最多 20 个。每份副本以文件 id 的后 8 个字符加原始文件名命名，因此按上述 id 附加的 `data/sales.csv` 会变成 `~/NR6q4V8w-sales.csv`。容器内的修改不会影响 workspace 中的原始文件。容器启动时只包含你附加给它的文件。

### 下载 shell 生成的文件

每个 shell 结果都会列出该命令触碰过的文件，每个文件带一个 `cfile_` id。用 [container file content endpoint](https://openrouter.ai/docs/api/api-reference/containers/download-container-file-content) 下载这些文件：

```
curl "https://openrouter.ai/api/v1/containers/$CONTAINER_ID/files/$FILE_ID/content" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -o output.txt
```

容器文件保留 30 天。想长期保留某份文件，就把它[提升（promote）](https://openrouter.ai/docs/api/api-reference/containers/promote-a-container-file-into-workspace-documents)：

```
curl -X POST "https://openrouter.ai/api/v1/containers/$CONTAINER_ID/files/$FILE_ID/promote" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

提升（promote）会把容器文件复制进你的 workspace 并返回一个新的 `or_file_` id，之后你可以像附加上传文件一样把它附加到后续运行。与上传不同，被提升的文件可以通过 Files API 下载。

### Files API 细节

你可以在 [workspace files 页面](https://openrouter.ai/workspaces/default/files)查看你的全部文件。直接上传的文件不可下载，但从容器提升来的文件可以。

## 多个 server tools 组合使用

Shell 是我们提供的众多 [server tools](https://openrouter.ai/docs/guides/features/server-tools) 之一，组合使用时非常强大。这里模型用网络搜索来查找素材，再用 shell 把素材写成文件：

```
curl https://openrouter.ai/api/v1/responses \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek/deepseek-v4-pro-0813",
    "input": "Look up the three biggest open-source AI releases this week, then write ~/out/releases.md with one paragraph each and a source link.",
    "tools": [
      { "type": "openrouter:web_search" },
      { "type": "openrouter:shell", "parameters": { "engine": "openrouter" } }
    ]
  }'
```

生成的 `~/out/releases.md` 会出现在 shell 结果的文件列表中，你可以用上面的 container file content endpoint 下载它。

如果你不想给容器开网络访问，这个组合也大有用处。网络搜索在容器之外运行，因此模型可以拉取网络内容并传入它的命令，而容器保持默认网络策略、自身无法访问互联网。

在 [chatroom](https://openrouter.ai/chat) 中，打开 shell 和 web search 开关即可使用同样的组合。运行创建的文件会以下载链接的形式出现在会话中。

## 定价

Shell 和 Bash 的使用按沙箱时间计费。价格是**每活跃秒 $0.0001**，从请求首次运行沙箱命令的时刻起计量，直到最后一条沙箱命令为止。请求结束后容器空闲的时间不计费。

当请求启动一个冷容器（新建的或已进入休眠的）时，我们按最低 30 秒计费。如果一个 agent 连续向同一容器发出多个请求，只有第一个需要付最低时长。

按请求计费让查找某个具体请求的运行成本变得容易。一个请求的费用等于其 token 费用加上沙箱时间，而沙箱时间在 Logs 页面该请求的时间线中自成一列。

Files API 的使用不单独收费，但总存储量限制为 10 GiB。

## 为 workspace 禁用工具

Server tools 默认启用。Workspace 管理员可以在 workspace 的 **Server Tools** 页面关闭其中任何一项，每个工具都有显示 Available 或 Blocked 的开关。该设置对 workspace 发起的每一条请求生效，无论通过 API key、chatroom 还是 presets。

## 开始使用

Shell、Bash、Files API 和容器均处于 beta 阶段，现已可用。API 在 beta 期间可能变动。如果有东西不符合你的预期，请到我们 Discord 的 [#feedback](https://discord.gg/fVyRaUDgxW) 频道告诉我们。

- [Shell server tool](https://openrouter.ai/docs/guides/features/server-tools/shell)
- [Bash server tool](https://openrouter.ai/docs/guides/features/server-tools/bash)
- [Files API](https://openrouter.ai/docs/guides/features/files-api)
- [Containers](https://openrouter.ai/docs/guides/features/containers)
- [All server tools](https://openrouter.ai/docs/guides/features/server-tools)
