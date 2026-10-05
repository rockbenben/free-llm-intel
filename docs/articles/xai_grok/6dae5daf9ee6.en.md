---
vendor: xai_grok
title: Use Grok in OpenClaw
original_title: Use Grok in OpenClaw
url: https://x.ai/news/grok-openclaw
date: 2026-05-19
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 0ea6992558f7
---

Back to news

May 19, 2026

# Use Grok in OpenClaw

Use your SuperGrok or X Premium subscription inside OpenClaw, an open-source, local-first agent and personal assistant.

Starting today, log in and use your SuperGrok or X Premium subscription inside OpenClaw.

OpenClaw is an open-source, local-first agent and personal assistant. It runs on any hardware — a Mac Mini, laptop, server, VPS, or even a Raspberry Pi — and keeps persistent memory across sessions.

OpenClaw connects to WhatsApp, Telegram, Slack, Discord, Signal, iMessage, and many other messaging platforms, so you can interact with your agent wherever you already chat.

If you already have a Grok or X Premium subscription, you can now use Grok models inside OpenClaw. Connecting Grok to your OpenClaw agent is available on every tier.

## [Setup](https://x.ai/news/grok-openclaw#setup)

Install OpenClaw:

```
curl -fsSL https://openclaw.ai/install.sh | bash
```

bash

Run the guided onboarding:

```
openclaw onboard --install-daemon
```

bash

On a VPS or over SSH, use device-code. OpenClaw prints a short code and URL you can open in any browser to finish sign-in:

```
openclaw onboard --auth-choice xai-device-code
```

bash

Or connect a messaging app — Telegram, WhatsApp, Slack, Discord, Signal, iMessage, and more — and talk to your agent there.

For more, see [OpenClaw getting started](https://docs.openclaw.ai/start/getting-started) and the [xAI provider docs](https://docs.openclaw.ai/providers/xai).

More open-source agents and integrations are coming soon.
