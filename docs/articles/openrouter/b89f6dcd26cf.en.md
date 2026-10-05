---
vendor: openrouter
title: Zero Data Retention (ZDR): What It Means for AI APIs
original_title: Zero Data Retention (ZDR): What It Means for AI APIs
url: https://openrouter.ai/blog/insights/zero-data-retention
date: 2026-09-11
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 07dec6a0b862
---

# Zero Data Retention (ZDR): What It Means for AI APIs

OpenRouter ·9/11/2026 · Updated 9/24/2026

[Zero Data Retention (ZDR)](https://openrouter.ai/docs/guides/features/zdr) means an AI provider processes your prompt, returns a response, and doesn’t store it afterward. It’s a retention guarantee. It doesn’t keep data inside your network, control what your application logs, or automatically cover third-party tools connected to the request.

This page explains what ZDR covers, what it doesn’t, and how to enforce it on your API calls.

## Tl;dr

- ZDR prevents an eligible inference provider from retaining your prompts and responses.
- Your data still reaches the provider and is processed by the model.
- On OpenRouter, you can enforce ZDR through account settings, guardrails, or the `provider.zdr` request field.
- ZDR applies to provider inference. Your logs, enabled tools, plugins, and other storage features require separate controls.

## What is zero data retention (ZDR)?

[Zero Data Retention is a data-handling policy](https://openrouter.ai/docs/guides/features/zdr) under which an AI provider processes your request without persisting the prompt or response. ZDR governs provider-side retention. It doesn’t mean your data remained inside your network or that every service involved in the request followed the same policy.

We evaluate data policies at the endpoint level because a provider’s general policy may differ from the policy attached to a particular model endpoint. When we can’t confirm an endpoint’s policy, we take the conservative position and classify it as retaining and training on data.

ZDR answers one of three separate questions:

- **Retention at rest**: Whether the provider stores prompts and responses after the response returns. ZDR covers this.
- **Data in transit**: Your request still travels to the provider, and the model still processes it. ZDR doesn’t change that.
- **Training on data**: Whether a provider uses your inputs to improve its models. That’s a distinct control, though providers often pair it with ZDR.

A “no training” policy doesn’t necessarily mean ZDR. A provider may decline to train on your data while retaining it temporarily for another reason. The reverse relationship is stronger. An endpoint that doesn’t retain your data can’t later use that data for training.

ZDR routing is also separate from our own logging policy. We don’t store prompt or response content unless you opt in to [input and output logging](https://openrouter.ai/docs/guides/features/input-output-logging). We still retain request metadata such as token counts, latency, model, and cost so you can view usage and activity information.

## What ZDR covers and what it doesn’t

ZDR has a specific boundary. It covers provider-side retention for eligible inference endpoints. It doesn’t become a universal privacy policy for every system your request touches.

| **Data-handling question** | **Covered by ZDR?** | **What it means** |
| --- | --- | --- |
| Provider stores your prompt after inference | Yes | A ZDR endpoint doesn’t persist the prompt |
| Provider stores the model response | Yes | A ZDR endpoint doesn’t persist the completion |
| Provider trains on the retained prompt | Indirectly prevented | There is no retained prompt available for training |
| Data reaches the model | No | The provider must process the input to generate a response |
| Processing stays in a specific country or region | No | Use data residency or [in-region routing](https://openrouter.ai/docs/guides/features/in-region-routing) |
| OpenRouter stores request metadata | No | Metadata can be retained without prompt or response content |
| Your application logs prompts | No | Your own logging and storage policies still apply |
| A plugin or tool retains data | No | Tools have their own operators and data policies |
| An endpoint retains data for abuse or legal review | No | We don’t treat a retaining endpoint as ZDR |

“We do not train on your data” may still allow temporary retention for abuse detection or legal obligations. That endpoint doesn’t meet our ZDR definition. You can still use it under a no-training policy, but you shouldn’t describe the request as zero retention.

ZDR enforcement also applies only to inference provider routing. A [web search plugin](https://openrouter.ai/docs/guides/features/plugins/web-search), external tool, or other service you enable can receive request data under its own retention terms. Review those policies separately before using them in a workflow with strict retention requirements.

Your application remains another retention layer. A ZDR request can still leave a complete prompt in an error tracker, an analytics event, a database row, or an application log. Provider-side ZDR doesn’t delete any of those copies.

![Diagram of what ZDR does and does not cover: the request flows from your application through OpenRouter to a ZDR provider endpoint where the prompt and response are not persisted, while application logs, request metadata, plugins and tools, and processing region sit outside the ZDR boundary and require their own controls](https://openrouter.ai/blog/images/zero-data-retention-coverage.png)

### Check caching separately

We consider [provider-side in-memory prompt caching](https://openrouter.ai/blog/insights/is-implicit-caching-prompt-retention/) compatible with ZDR because the prompt isn’t written to persistent storage. Cached representations remain in provider memory long enough to reuse the prompt and improve performance.

Our [response caching feature](https://openrouter.ai/docs/guides/features/response-caching) has different behavior because it temporarily stores generated responses. Account-level ZDR disables response caching, but the per-request `provider.zdr` field doesn’t affect response-cache eligibility. A system that requires zero storage across every layer should therefore review its response-caching configuration separately.

## ZDR versus related AI privacy controls

ZDR is one of several privacy controls. Each control answers a different question.

### ZDR vs. “no training on your data”

These often ship together, but they answer different questions. “No training” governs whether your inputs improve a model. ZDR governs whether the provider stores those inputs after the response returns. A provider can promise not to train on your data while still holding it briefly for abuse checks or legal reasons. If you need both, enforce both.

On OpenRouter, `data_collection` lets you filter providers based on whether they store user data non-transiently and may train on it. Setting it to `"deny"` excludes those endpoints. You can combine it with `zdr: true` when you want both controls to be explicit in the request.

### ZDR vs. data residency and region pinning

[Region pinning](https://openrouter.ai/blog/insights/ai-data-residency/) controls where your request is processed, inside a specific region for GDPR, for example, while ZDR controls whether the data is kept afterward. A provider might process and retain a request in the EU, or process a ZDR request somewhere else entirely.

Use both controls when a policy names a permitted processing location and a retention requirement. We provide [in-region routing](https://openrouter.ai/blog/announcements/us-in-region-routing/) for the US and EU on Business and Enterprise plans through the `us.openrouter.ai` and `eu.openrouter.ai` API domains. This is separate from ZDR enforcement.

### ZDR vs. self-hosting

Self-hosting keeps inference inside your own infrastructure. Before choosing it, check whether these controls meet your requirements:

- **Region pinning**: Controls where the request is processed.
- **ZDR routing**: Prevents provider-side storage of prompts and responses.
- **Per-key or per-workspace guardrails**: Separate one customer’s traffic and policy from another’s.
- **Your own logging**: Records what was sent and where.

Self-hosting is required when policy prohibits all third-party processing, including transient inference.

## How to route to ZDR-eligible endpoints on OpenRouter

A provider offering ZDR doesn’t automatically make every request ZDR-compliant. You must enforce the policy at the account, guardrail, or request level.

### Account-level enforcement in privacy settings

You can enforce ZDR across every request without touching your code, from your account’s [privacy settings](https://openrouter.ai/settings/privacy). ZDR can be required per model group, covering Anthropic, OpenAI, Google, SpaceXAI, and non-frontier endpoints, so you can require it for some model groups and not others. You can also enforce it through [guardrails](https://openrouter.ai/docs/guides/features/guardrails). See the [Zero Data Retention guide](https://openrouter.ai/docs/guides/features/zdr).

[Data policy filtering](https://openrouter.ai/docs/guides/privacy/provider-logging) is a separate switch. It lets you disable providers that store inputs for training. Opt out of training in your account settings and we won’t route to providers that train on your data.

### Per-request enforcement with the zdr routing control

For request-level control, set the `zdr` field inside the `provider` block. When `zdr` is `true`, the request routes only to endpoints with a Zero Data Retention policy. When it’s `false` or omitted, it doesn’t affect routing.

```
{
  "model": "meta-llama/llama-3.3-70b-instruct",
  "messages": [{ "role": "user", "content": "Hello" }],
  "provider": {
    "zdr": true,
    "data_collection": "deny"
  }
}
```

The related [`data_collection`](https://openrouter.ai/docs/guides/routing/provider-selection) control takes `"allow"`, the default, or `"deny"`. Set it to `"deny"` and routing excludes endpoints that store user data non-transiently and may train on it.

The per-request `zdr` parameter composes as an OR with your account-wide and guardrail settings. If any one of them turns ZDR on, enforcement applies. The request-level flag can only ensure ZDR is on, it can’t override or loosen an account-wide or guardrail rule.

![Side-by-side comparison of a plain chat completion request and the same request with a provider block containing zdr true and data_collection deny, which routes only to Zero Data Retention endpoints](https://openrouter.ai/blog/images/zero-data-retention-request.png)

## How to verify a vendor’s ZDR claim

Check these five points.

- **What exact data does ZDR cover?** Confirm whether it includes prompts, completions, uploaded files, tool inputs, cached representations, and identifiers.
- **Does the policy apply per provider or per endpoint?** Model features and API endpoints can have different storage requirements. A provider-wide statement may hide exclusions.
- **What falls outside the policy?** Ask about metadata, plugins, tools, prompt caching, response caching, logging, batch APIs, and stateful features.
- **How is ZDR enforced?** Look for an account policy, guardrail, or request-level routing control rather than manual provider selection.
- **How can you verify continued eligibility?** Data policies change. We maintain endpoint-level policy information and publish the current list of ZDR endpoints at `https://openrouter.ai/api/v1/endpoints/zdr`, so routing decisions can follow the current policy rather than a static spreadsheet.

## Conclusion

ZDR reduces provider-side storage risk, but only when your request reaches a qualifying endpoint. Treat it as an enforceable routing requirement.

For sensitive inference traffic, combine the controls that match the actual policy. Use ZDR for retention, `data_collection: "deny"` for storage and training restrictions, and in-region routing when processing location matters. Then review your application logs, enabled tools, and caching configuration so another layer doesn’t recreate the data you removed from the provider.

Building on our API? Restrict your calls to ZDR endpoints, starting with our [ZDR docs](https://openrouter.ai/docs/guides/features/zdr) and [provider routing](https://openrouter.ai/docs/guides/routing/provider-selection) controls. Reviewing AI data handling for your org? See [OpenRouter for Enterprise](https://openrouter.ai/enterprise).

## FAQ

### What is ZDR (zero data retention)?

Zero Data Retention means an AI provider processes your prompt and returns a response without persisting either one afterward. ZDR governs provider-side storage for eligible endpoints. It doesn’t prevent the data from reaching the model, keep the request inside your network, or control copies created by your own systems.

### What is a zero data retention policy for AI?

A zero data retention policy states that an AI provider won’t store prompts or responses after processing them. The policy should identify which endpoints and features qualify, how it’s enforced, and what happens to metadata, caches, tools, and logs. A no-training policy alone doesn’t guarantee zero retention.

### What is a zero-retention API?

A zero-retention API processes requests without storing the prompt or response after inference. With OpenRouter, you can restrict a request to eligible endpoints by setting `provider.zdr` to `true`. Account-level privacy settings and guardrails can enforce the same requirement across broader groups of requests.

### Which LLM is best for privacy?

Privacy depends on the endpoint and routing policy, rather than the model name alone. The same model can be available through providers with different retention rules. Filter the model catalog for eligible endpoints, then enforce ZDR, data-collection, and residency requirements through your routing configuration.
