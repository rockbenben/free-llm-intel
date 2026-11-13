---
vendor: aws_bedrock
title: Four Amazon Bedrock inference choices that affect cost
original_title: Four Amazon Bedrock inference choices that affect cost
url: https://aws.amazon.com/blogs/machine-learning/four-amazon-bedrock-inference-choices-that-affect-cost
date: 2026-11-12
lang: en
captured: 2026-11-13
extractor: readability-v1
status: ok
body_sha: 9a0dd89a7ed8
---

## [Artificial Intelligence](https://aws.amazon.com/blogs/machine-learning/)

# Four Amazon Bedrock inference choices that affect cost

Your Amazon Bedrock inference bill can keep climbing after you tune prompts and application logic. Request-level choices can still change how many tokens the service processes and the rate applied to them. Cache duration, service tier, reasoning effort, and `maxTokens` can affect cost without changing your model or prompt.

Each choice depends on the model and workload. This post shows how we tested each choice and how to verify its effect from response metadata, logs, and billing data.

To try these settings yourself, start with the Amazon Bedrock Samples notebooks [Mixed TTL Caching](https://github.com/aws-samples/amazon-bedrock-samples/blob/main/introduction-to-bedrock/prompt-caching/converse_api/notebooks/04_mixed_ttl_caching.ipynb) and [Tenant Isolation with Prompt Caching](https://github.com/aws-samples/amazon-bedrock-samples/blob/main/introduction-to-bedrock/prompt-caching/converse_api/notebooks/05_tenant_isolation.ipynb). For `maxTokens` and reasoning effort, see the 01-low-effort folder of the [sample-code-for-genai-cost-management-workshop](https://github.com/aws-samples/sample-code-for-genai-cost-management-workshop/tree/main/samples/2-optimize/01-low-effort) GitHub repo. Each sample sets its own model ID, so change it, and the inference parameters, to match the model you call. For model availability by AWS Region, refer to [Models at a glance](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards.html). For broader decisions such as model selection, batch inference, routing, and distillation, see [Effective cost optimization strategies for Amazon Bedrock](https://aws.amazon.com/blogs/machine-learning/effective-cost-optimization-strategies-for-amazon-bedrock/).

## Where inference cost comes from

Every Amazon Bedrock response carries usage metadata. Input and output tokens bill at the rate for the model and tier that served the request. Cache reads and writes use separate token counters, and reasoning tokens count as output tokens.

## Prompt cache duration

Repeated system instructions, tool definitions, or reference context can be processed again when the cache expires before the next request. The [Prompt caching for faster model inference](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html) guide lists 5-minute and 1-hour time-to-live (TTL) values for supported Anthropic models. It also lists a 30-minute minimum TTL for supported GPT-5.6 models. Support and API fields depend on the model, so check the current support matrix before selecting a duration.

For supported models, Amazon Bedrock also offers [implicit prompt caching](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html#prompt-caching-implicit), which attempts to reuse eligible prompt prefixes without cache controls in your request. Because implicit caching is best effort and doesn’t guarantee a cache hit, the duration choices in this section apply to explicit caching.

This Converse API signature requests a 1-hour entry on models that support it:

```
{ "cachePoint": { "type": "default", "ttl": "1h" } }
```

For supported Anthropic models, InvokeModel places the same `ttl` value in `cache_control`.

A longer duration is not automatically cheaper. The [Amazon Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/) page lists separate rates for 5-minute writes, 1-hour writes, and cache reads. For Anthropic Claude Sonnet 5 and Anthropic Claude Opus 5 on Amazon Bedrock, a 5-minute write costs 1.25 times the input rate. A 1-hour write costs 2 times, and a cache read costs 0.1 times.

These rates set the break-even, assuming each request reuses the exact prefix and each cache read refreshes the TTL. A 5-minute cache pays back on the first reuse within 5 minutes. When requests for the same prefix arrive more than 5 minutes apart, it rewrites at 1.25 times on every request. The 1-hour cache is then cheaper from the second request within the hour.

Cache rates and checkpoint minimums differ by model. Check the [Amazon Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/) page and the [prompt caching guide](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html) for the model you call. Rerun the comparison for your model, then confirm it with cache read and write tokens after rollout.

Keep stable content before dynamic content, meet the model’s checkpoint minimum, and use on-demand inference because prompt caching doesn’t work with batch inference.

Changing a cached prefix, including a system instruction or tool definition, causes a miss and a new write. Checkpoints are evaluated in the order tools, system, then messages, so a change in an earlier section also invalidates the later ones. Version prompts that change often so each version gets its own cache entry. We ran six calls on Claude Sonnet 5 with a 1-hour checkpoint, changing the system prompt once and the tool definition once. Each change produced zero cache reads and a new write.

AWS describes cache entries as scoped to your account and Region, not to your tenants. In a multi-tenant application, prepend a tenant-specific SHA-256 hash to the cacheable prefix. The [Optimizing cost and latency with Amazon Bedrock prompt caching for Anthropic models](https://aws.amazon.com/blogs/machine-learning/optimizing-cost-and-latency-with-amazon-bedrock-prompt-caching/) post describes this pattern. Enforce tenant authorization before you build the prompt. The hash partitions entries inside one account. If a regulated workload needs a hard data boundary, keep each tenant in a separate AWS account.

Keep the 5-minute default for frequent reuse. Move from it to a longer supported duration when the same prefix recurs at least twice an hour with gaps longer than 5 minutes. To beat no caching at all, the 1-hour cache needs three requests an hour.

## Service tiers for latency-tolerant workloads

Background jobs, evaluation harnesses, nightly summarization, and backfills don’t always need the latency profile used by interactive requests. For models that support Flex, select it with this request signature:

```
{ "serviceTier": { "type": "flex" } }
```

Use `default`, not `standard`, to request the Standard tier. You can also omit `serviceTier`:

```
{ "serviceTier": { "type": "default" } }
```

Tier support is model-specific, so record support by exact model version. The [Amazon Nova 2 Lite](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-2-lite.html) and [OpenAI gpt-oss-120b](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-oss-120b.html) model cards list Flex as supported. The cards for [Anthropic Claude Sonnet 5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-sonnet-5.html) and [Anthropic Claude Opus 5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-5.html) on Amazon Bedrock list it as not supported. A Flex request to an unsupported model fails with a `ValidationException` instead of silently running on Standard. Our request to Anthropic Claude Sonnet 5 returned that error.

If your policy allows Standard as a fallback, catch the unsupported-tier error and retry once with `default`. Don’t retry every `ValidationException`, because malformed requests raise it too. Cap application-level retries. The bounded retry strategy of the AWS SDK handles throttling and transient errors.

Set your own deadline for Flex requests. A supported response reports the resolved tier, which you can also verify with Amazon CloudWatch `ResolvedServiceTier`. See [Service tiers for optimizing performance and cost](https://docs.aws.amazon.com/bedrock/latest/userguide/service-tiers-inference.html) and the [Amazon Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/) page for the exact model you call.

We tested Flex on Amazon Nova 2 Lite with 200 `default` requests and 200 `flex` requests, sent in interleaved pairs. Both tiers processed the same number of input and output tokens. All 400 requests resolved to the requested tier, and the median latency difference was too small to separate from noise. At the time of writing, the published Flex rate for Nova 2 Lite in us-west-2 is half the Standard rate, and our bill reflected that. Check the [Amazon Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/) page for current rates. Keep latency-sensitive traffic on `default`.

## Adaptive thinking effort

Reasoning tokens bill as output tokens. Claude Sonnet 5 and Claude Opus 5 use adaptive thinking at `high` effort by default, even when a request omits the `thinking` field. An application moved from Claude Sonnet 4.6 without changes starts billing thinking tokens, and `maxTokens` now caps thinking plus response text. Claude Haiku 5.5 defaults to `medium`. All three models support `low`, `medium`, `high`, `xhigh`, and `max`. Lower the effort for a task with this request signature:

```
{
  "thinking": { "type": "adaptive" },
  "output_config": { "effort": "low" }
}
```

Keep effort in `output_config`, not inside `thinking`. Check [Adaptive thinking](https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html) whenever you change models.

We tested a tool-calling agent on Claude Opus 5. Its three tasks follow the design in [Build long-horizon agents with Grok 4.7 on Amazon Bedrock](https://aws.amazon.com/blogs/machine-learning/build-long-horizon-agents-with-grok-4-7-on-amazon-bedrock/), and each has one correct answer. We ran each task eight times at every effort level. The table shows median output tokens:

| **Effort** | **Correct runs** | **Median output tokens** | **Change from low (95% interval)** |
| --- | --- | --- | --- |
| low | 24 of 24 | 936 | baseline |
| medium | 24 of 24 | 1,484 | +59% (50% to 78%) |
| high (default) | 24 of 24 | 2,521 | +169% (112% to 190%) |
| xhigh | 24 of 24 | 2,964 | +217% (170% to 260%) |
| max | 24 of 24 | 3,762 | +302% (180% to 402%) |

Accuracy at lower effort depends on the model and the task. Measure on tasks shaped like yours.

On the Amazon Bedrock Samples [Invoke Bedrock model for code generation](https://github.com/aws-samples/amazon-bedrock-samples/blob/main/genai-use-cases/text-generation/how_to_work_with_code_generation_w_bedrock.ipynb) workload, median output tokens were 676 at `low` and 743 at `high`, a difference within run-to-run variation. The programs we graded passed at each effort level.

Use per-request output-token counts, CloudWatch `AWS/Bedrock OutputTokenCount`, invocation logs, and a task pass rate to evaluate the choice. Start below `high` for routine, well-bounded tasks. Keep `high` where your quality tests show that the task needs it. A token reduction that breaks the task is not a saving.

## Output token limits

`maxTokens` is an application output ceiling. It limits the output that a bad prompt, regression, or loop can produce before the request stops. The quota rule is documented in [How tokens are counted in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-token-burndown.html). Amazon Bedrock deducts your input tokens plus `maxTokens` when a request starts, so an oversized value reduces concurrency.

An output ceiling isn’t a safety control. Use Amazon Bedrock Guardrails as a standard responsible AI control in production generative AI workloads. Guardrails can filter content, detect prompt attacks, and check grounding on supported inputs and responses. See [Detect and filter harmful content by using Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html).

Set `maxTokens` per task type after observing a representative output-token distribution:

```
{ "inferenceConfig": { "maxTokens": 155 } }
```

See [Inference using Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html) for the request parameters.

In our test on Claude Sonnet 5, five normal outputs peaked at 103 tokens, so we set an illustrative fence of 155 tokens with headroom. We then sent the same deliberately verbose prompt with adaptive thinking disabled, once under a 2,048-token ceiling and once under the 155-token fence. The first request generated 2,048 output tokens and the second generated 155, so the fence avoided 1,893 output tokens. Both stopped at `max_tokens`, so both responses were truncated. The fence limits spend but does not make an unsuitable prompt useful, and in a multi-turn or agentic chain a truncated turn can break the steps after it.

For production calibration, compare the 95th and 99th percentiles (P95 and P99) for each task type and add headroom to the selected percentile. With adaptive thinking on, `maxTokens` also caps thinking tokens, so calibrate with thinking enabled. P95 limits exposure more aggressively but accepts more truncation risk. P99 preserves more valid long-tail responses at a higher ceiling. Monitor `max_tokens` stops and investigate the request before raising the task’s limit.

## Putting it together

Use the same test loop for each setting: confirm model support, change one request choice, measure tokens or cost, and track quality or completion. If you route across models, keep a capability record for each model version, Region, and API: supported cache duration, service tiers, reasoning levels, and output ceiling. Validate each request against that record before you send it, then check the response for the resolved tier and cache counters.

| **Setting** | **Default or permissive state** | **Result** | **Risk to accept** |
| --- | --- | --- | --- |
| Cache duration | Model-specific TTL | From published Sonnet 5 and Opus 5 rates, a 1-hour cache wins from the second request per hour when gaps exceed 5 minutes | A 1-hour write costs 2 times input, so low reuse loses money. Partition tenant prefixes |
| Service tier | `default` | At the time of writing, Nova 2 Lite Flex was published at half the Standard rate, and our bill matched | Longer processing. Set your own deadline and a fallback |
| Reasoning effort | `high` on the tested adaptive model | Low to high: +169% median output tokens on the agent test, no reliable difference on code generation | Quality can drop near the task’s capability boundary. Track pass rate with tokens |
| `maxTokens` | Permissive 2,048-token cap | An illustrative 155-token fence avoided 1,893 output tokens in one test | Truncation can cascade through multi-turn or agentic chains. Check `stopReason` before raising the limit |

## Signals to watch

| **Setting** | **Symptom** | **Verify with** | **First response** |
| --- | --- | --- | --- |
| Cache duration | Repeated context does not produce the expected latency or cost benefit | Application latency and cost telemetry | Check prefix stability, reuse interval, and model support before changing TTL |
| Service tier | The requested tier is unsupported or the serving tier differs from expectation | Response `serviceTier` and CloudWatch `ResolvedServiceTier` | Use a supported tier or return latency-sensitive traffic to `default` |
| Reasoning effort | Output tokens rise while quality holds | Per-request response telemetry, CloudWatch `OutputTokenCount`, invocation logs, and task pass rate | Lower effort for that task class and rerun its quality test |
| `maxTokens` | `stopReason` is `max_tokens` | Response stop reason and task-scoped output-token distribution | Inspect the prompt and task fence before raising the limit |

Derive P95 and P99 for each task type from task-tagged application telemetry or invocation logs.

## Conclusion

All four choices live in the inference request. Recheck support when you change models, then change one setting at a time and measure the result in your application.

Use these resources to evaluate the choices for your workload:

- Amazon Bedrock console: [console.aws.amazon.com/bedrock](https://console.aws.amazon.com/bedrock/).
- Prompt caching: [Prompt caching for faster model inference](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html).
- Service tiers: [Service tiers for optimizing performance and cost](https://docs.aws.amazon.com/bedrock/latest/userguide/service-tiers-inference.html).
- Adaptive thinking: [Adaptive thinking](https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html).
- Responsible AI controls: [Detect and filter harmful content by using Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html).
- Related reading: [Effective cost optimization strategies for Amazon Bedrock](https://aws.amazon.com/blogs/machine-learning/effective-cost-optimization-strategies-for-amazon-bedrock/).
- Related samples and posts: [Invoke Bedrock model for code generation](https://github.com/aws-samples/amazon-bedrock-samples/blob/main/genai-use-cases/text-generation/how_to_work_with_code_generation_w_bedrock.ipynb) and [Build long-horizon agents with Grok 4.7 on Amazon Bedrock](https://aws.amazon.com/blogs/machine-learning/build-long-horizon-agents-with-grok-4-7-on-amazon-bedrock/).

## About the authors
