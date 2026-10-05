---
vendor: xai_grok
title: 在 OpenClaw 中使用 Grok
original_title: Use Grok in OpenClaw
url: https://x.ai/news/grok-openclaw
date: 2026-05-19
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# 在 OpenClaw 中使用 Grok

在你的 SuperGrok 或 X Premium 订阅基础上，使用开源自托管智能体与个人助理 OpenClaw。

从今天起，登录即可在 OpenClaw 内使用你的 SuperGrok 或 X Premium 订阅。

OpenClaw 是一个开源、local-first 的智能体与个人助理。它可以在任何硬件上运行——Mac Mini、笔记本、服务器、VPS，甚至树莓派——并在会话之间保持持久记忆。

OpenClaw 可连接 WhatsApp、Telegram、Slack、Discord、Signal、iMessage 以及许多其他消息平台，让你在你已有的聊天入口与智能体交互。

如果你已经有 Grok 或 X Premium 订阅，现在就可以在 OpenClaw 内使用 Grok 模型。把 Grok 连接到你的 OpenClaw 智能体在所有档位均可用。

## [设置](https://x.ai/news/grok-openclaw#setup)

安装 OpenClaw：

```
curl -fsSL https://openclaw.ai/install.sh | bash
```

bash

运行引导式上手流程：

```
openclaw onboard --install-daemon
```

bash

在 VPS 或通过 SSH 时，使用 device-code。OpenClaw 会打印一个短码和 URL，你在任意浏览器打开即可完成登录：

```
openclaw onboard --auth-choice xai-device-code
```

bash

或者连接一个消息应用——Telegram、WhatsApp、Slack、Discord、Signal、iMessage 等——在那里与你的智能体对话。

更多信息见 [OpenClaw 上手指南](https://docs.openclaw.ai/start/getting-started)和 [xAI provider 文档](https://docs.openclaw.ai/providers/xai)。

更多开源智能体与集成即将到来。
