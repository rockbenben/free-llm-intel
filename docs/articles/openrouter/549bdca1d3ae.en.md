---
vendor: openrouter
title: How to Connect SillyTavern to OpenRouter (2026 Guide)
original_title: How to Connect SillyTavern to OpenRouter (2026 Guide)
url: https://openrouter.ai/blog/tutorials/sillytavern-openrouter
date: 2026-06-18
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 5f40d74cdae9
---

# How to Connect SillyTavern to OpenRouter (2026 Guide)

OpenRouter ·6/18/2026 · Updated 9/24/2026

Using several AI models in SillyTavern normally means signing up with Anthropic, Google, Mistral, and a few others separately, each with its own account and often a $20 per month subscription. One OpenRouter key replaces that with a single credit balance and [300+ models](https://openrouter.ai/models) from 70+ providers in one SillyTavern dropdown. Many are free to start, and you can be chatting in about five minutes.

This guide covers the connection steps, the roleplay models to try, the settings that actually matter, and fixes for the errors SillyTavern users hit most. The same key also works in coding agents and editors, see [how to use OpenRouter with any coding agent](https://openrouter.ai/blog/tutorials/any-coding-agent/).

## Connect SillyTavern to OpenRouter in five steps

Work in SillyTavern’s API Connections panel. The goal is to point SillyTavern at OpenRouter, verify your key, pick a model, and send one test message before a longer chat.

- Open the API Connections panel (the plug icon in the top bar) and set **API Type** to Chat Completion.
- Set **Chat Completion Source** to OpenRouter.
- Click **Authorize** to create a key through the OAuth flow, or generate one at [openrouter.ai/settings/keys](https://openrouter.ai/settings/keys) and paste it into the API key field.
- Click **Connect** and wait for SillyTavern to verify the key.
- Pick a model from the dropdown, then click **Test Message**.

Send that test message before you commit to a long session. A successful Connect only proves SillyTavern can verify your key. Generation can still fail if the model is unavailable, the provider route can’t serve the request, the slug is wrong, your account can’t reach that model, or your prompt exceeds the model’s context window.

Use Chat Completion for almost every setup. Image inlining and tool calling only work through Chat Completion, which matches how current OpenRouter models expect prompts. Text Completion gives finer control over raw prompt formatting for advanced users, but it’s not the place to start. If OpenRouter only shows up under Chat Completion sources in your version, that’s expected. Full setup details live in the [SillyTavern OpenRouter docs](https://docs.sillytavern.app/usage/api-connections/openrouter/).

## Free models and the $10 credit rule

Models tagged `:free` cost $0 per token, but request limits still apply, and that catches people out.

| Account state | Daily :free cap | Per-minute cap |
| --- | --- | --- |
| Under $10 in credits | 50 requests/day | 20 requests/min |
| $10 or more in credits | 1,000 requests/day | 20 requests/min |

The $10 is a one-time credit purchase, not a subscription, and it stays usable for paid models. OpenRouter adds no [markup on provider pricing](https://openrouter.ai/pricing), so the catalog price is what you pay, and failed requests aren’t billed. If you already pay a provider directly and want to keep that contract, [bring your own key](https://openrouter.ai/docs/guides/overview/auth/byok) instead.

Charges on a “free” model almost always mean per-token billing and request limits got crossed. Check whether you actually selected a paid model, enabled a paid fallback route, or used a slug that doesn’t end in `:free`. Hitting the free-model ceiling is a limit problem, not the free model billing you.

## Roleplay models to try

DeepSeek V3.2 is the cheap, reliable default for long scenes. For more expressive, less filtered prose, try the Euryale finetunes. When a character card carries complicated instructions the model has to follow, Hermes 4 405B handles it better than most.

| Model slug | Context | In / Out per 1M | Free variant | Best for |
| --- | --- | --- | --- | --- |
| `deepseek/deepseek-v3.2` | 131K | $0.23 / $0.34 | No | Cheap, coherent default for long sessions |
| `deepseek/deepseek-r1-0528` | 164K | $0.50 / $2.15 | No | Reasoning-heavy scenes and planning |
| `sao10k/l3.3-euryale-70b` | 131K | $0.65 / $0.75 | No | Characterful RP prose with a long window |
| `gryphe/mythomax-l2-13b` | 4K | $0.06 / $0.06 | No | Classic budget workhorse, tiny context |
| `aion-labs/aion-rp-llama-3.1-8b` | 32K | $0.80 / $1.60 | No | Purpose-built roleplay tune, lightweight |
| `nousresearch/hermes-4-405b` | 131K | $1.00 / $3.00 | No | Complex cards, strict instruction following |
| `z-ai/glm-4.6` | 203K | $0.43 / $1.74 | No | Strong general model |
| `mistralai/mistral-large-2512` | 262K | $0.50 / $1.50 | No | Polished paid option, less filtered |

Prices and context windows verified against the OpenRouter catalog on 2026-06-16. Per-token rates change, so confirm on the model’s page before a long session.

Free variants come and go without the model itself changing, and they often run smaller context windows than the paid version. That’s the usual reason a character card starts forgetting mid-scene. Before you build a setup around any free model, check [openrouter.ai/models?q=free](https://openrouter.ai/models?q=free) and confirm the exact `:free` slug is still live.

## Settings and routing that matter

Start with settings that keep the chat stable, then tune once the connection is solid.

- Turn streaming on so replies appear as the model generates them.
- Set the context length slider to the model’s real window from the table above. Free variants are smaller, so check the catalog page, not a third-party guide.
- Leave fallback providers enabled for reliability. Disable them only when you need to control exactly which provider serves the request.
- Use [prompt caching](https://openrouter.ai/docs/guides/best-practices/prompt-caching) for long-running characters with a big system prompt or repeated lorebook context. It doesn’t make requests free, but it cuts the cost of repeated input across turns.

Two routing suffixes go on the end of a model slug. `:nitro` sorts to the fastest provider; `:floor` sorts to the cheapest. Both map to OpenRouter’s [provider routing](https://openrouter.ai/docs/guides/routing/provider-selection) sort options. For long sessions with a fixed character card, `:floor` plus prompt caching meaningfully reduces cost. For time-sensitive generation, reach for `:nitro`.

One billing note on streaming: aborting a stream stops processing and billing only for providers that support cancellation. Several don’t, including AWS Bedrock, Groq, Google, Google AI Studio, Minimax, and Mistral. For those, or for non-streaming requests, the model can run to completion and bill the full response.

## Keep roleplay chats private

OpenRouter privacy comes down to two layers: what OpenRouter stores, and what the provider serving your request stores. OpenRouter doesn’t store prompts or responses unless you opt into logging, though it keeps usage metadata like token counts and latency. The downstream provider has its own retention policy, which is why routing controls matter.

Enable [Zero Data Retention](https://openrouter.ai/docs/guides/routing/provider-selection) to route only to providers that don’t store prompts or responses, per request or account-wide. OpenRouter may offer a small discount for opting into prompt and completion logging; most roleplay users should leave it off rather than expose character cards and chat histories to logs.

OpenRouter doesn’t filter content itself, but it routes to providers that enforce their own policies, so calling the setup “uncensored” overstates it. If a model keeps refusing or cutting scenes, that’s provider moderation. Switch to a less-filtered model or provider. The [trust center](https://trust.openrouter.ai) has the specifics.

## Fix the most common errors

Most SillyTavern and OpenRouter issues fall into a few patterns. Start from the exact error message, then apply the matching fix.

**“Could not verify OpenRouter token.”** A common error, and the message is misleading. The key is almost always fine; the real cause is a DNS or network issue that stops SillyTavern from reaching openrouter.ai, so the request never gets verified. Confirm the key is active at [your keys page](https://openrouter.ai/settings/keys), paste it again without trailing spaces, re-Authorize if you used OAuth, and restart. If it persists, switch your DNS resolver to 8.8.8.8 or 1.1.1.1 and restart. DNS is the fix most of the time.

**401 error.** This means OpenRouter rejected the key SillyTavern sent. Regenerate it, paste it again without trailing spaces, and confirm the account has credits if you’re calling a paid model.

**OpenRouter is missing from the source list.** Set API Type to Chat Completion first, since it won’t show under other types. Update and restart SillyTavern. Only edit `config.yaml` on an older or unusual install, where `show_openrouter_api: true` exists as a workaround, not a default. Check the [related SillyTavern issue](https://github.com/SillyTavern/SillyTavern/issues/3796) before changing it.

**Empty model dropdown.** The account is usually fine; SillyTavern failed to load the list. Refresh the connection and restart. If it still fails, enter the exact model slug from the model page by hand.

**Connect works, but generation fails.** Connect only proves the key is valid. Switch to another model and test, confirm the account has credits for a paid model, check the slug, and lower the context length if a large card, lorebook, or history is overflowing the window.

## Frequently asked questions

### How do I connect OpenRouter to SillyTavern?

Open the API Connections panel, set API Type to Chat Completion, choose OpenRouter as the source, click Authorize for an OAuth key or paste one from [openrouter.ai/settings/keys](https://openrouter.ai/settings/keys), click Connect, pick a model, and send a test message.

### Is OpenRouter actually free for SillyTavern?

For models tagged `:free`, yes, with limits. Free-model usage is capped at 50 requests per day and 20 per minute. Buying $10 in credits once raises the daily cap to 1,000 requests, while the per-minute cap stays the same. It’s not a subscription, and the credit stays usable for paid models.

### What is the best free model for SillyTavern roleplay?

`meta-llama/llama-3.3-70b-instruct:free` is a strong pick, with a 131K context when available. Free model availability changes often, so confirm the exact `:free` slug is live at [openrouter.ai/models?q=free](https://openrouter.ai/models?q=free) before building a setup around it.

### How do I fix “could not verify OpenRouter token”?

It’s usually a DNS or network problem, not a bad key. Switch your DNS to 8.8.8.8 (Google) or 1.1.1.1 (Cloudflare), confirm the key is active, paste it again without trailing spaces, and restart SillyTavern.

### Why does my generation stop early?

Check the response’s finish reason first, since the same symptom has several causes: provider moderation, a max-tokens limit, a context-length issue, or streaming behavior. If one provider keeps cutting scenes short, try another model or provider, then raise the max output setting if responses simply end too soon.

### OpenRouter or a single-provider key for SillyTavern?

Use a direct key if you only ever use one provider and want the simplest billing. Use OpenRouter if you want one setup for many models, provider routing, fallback when a route goes down, free models to experiment with, and a single credit pool.
