---
vendor: deepinfra
title: 9 Best Open-Source Models for Coding (November 2026)
original_title: 9 Best Open-Source Models for Coding (November 2026)
url: https://deepinfra.com/blog/best-open-source-models-for-coding
date: 2026-11-17
lang: en
captured: 2026-11-17
extractor: readability-v1
status: ok
body_sha: c4c087cbd572
---

# 9 Best Open-Source Models for Coding (November 2026)

Published on 2026.11.17 by DeepInfra

![9 Best Open-Source Models for Coding (November 2026)](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/11/best-open-source-models-for-coding-header.png)

Modern artificial intelligence (AI) coding tools now analyze repositories, fix bugs, edit several files, run tests, and execute autonomous development loops. These agentic workflows generate millions of input and output tokens through continuous model calls, and that makes proprietary APIs costly at scale.

Open-source coding models offer a cost-effective alternative. You can run them on private infrastructure, choose your serving hardware, pin a specific model version, adjust inference settings, and reduce dependence on a single API provider. Hosted inference services like [DeepInfra](https://deepinfra.com/) also let you use these models without managing GPUs yourself, at per-token prices that start under $0.10 per million input tokens for the top-scoring model in this guide.

In this guide, we compare the leading open-source models for coding as of November 2026. We evaluate them on coding benchmarks, context window size, license terms, and API cost, and we cover self-hosting options at the end. Scores and prices are as of November 17, 2026.

## How to Evaluate Coding Models: Benchmarks That Matter

Watch the following benchmarks to judge how well a model will perform on the tasks you plan to automate.

- [**HumanEval**](https://github.com/openai/human-eval) **and [MBPP (Mostly Basic Python Problems)](https://huggingface.co/datasets/Muennighoff/mbpp)** measure function-level code generation. A model receives a short natural-language problem and must produce Python code that passes unit tests. They offer a quick measure of basic programming ability, but they do not test repository navigation, tool use, or multi-file changes, and current models have largely saturated them.
- [**SWE-bench Verified**](https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified) **and [SWE-bench Pro](https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro)** assess how well a model resolves real GitHub issues within agentic coding workflows. The model has to work through an entire codebase, locate the source of a bug, write a patch across multiple files, and pass execution tests.
- **DeepSWE** is the long-horizon software engineering benchmark that most of this year’s model cards report. Because DeepSeek, Moonshot, MiniMax, Xiaomi, Z.ai, and Qwen all publish a DeepSWE v1.1 score, it is the closest thing to a common yardstick across vendors, with the caveat that each vendor runs its own harness.
- [**Terminal-Bench**](https://www.tbench.ai/) compares model performance on tasks related to shell commands, command-line interfaces (CLI), and DevOps. Vendors now report versions 2.1 and 4.0, and results change a lot with the agent harness used, so compare scores only within the same model card.
- [**LiveBench**](https://livebench.ai/) is independent and regularly refreshed to limit training-data contamination. LiveBench moved to version 2.0 on November 6, 2026. The new version grades long-horizon work (bug fixes, apps that run for hours, research reports), and its scores are not comparable to the LiveBench figures published before that date.

Apart from the leaderboard, check the context window and license. A model that looks good on function-level completion can still be a poor choice for whole-repo refactors or private on-prem use.

- **Context window** defines how much code, documentation, terminal output, and conversation history the model can process in a single request. A larger context window helps with repository analysis and long-running agent sessions.
- **License** determines whether you can use the weights commercially, modify them, redistribute the model, or provide the model through a hosted service. “Open-source” is used loosely in this field. Several models below ship open weights under custom licenses with commercial conditions, and we note each one. Our guide to [open-weight model licenses](https://deepinfra.com/blog/open-weight-model-licenses) covers what to check.

## Top 9 Open-Source Models for Coding: Comparison

Here is how the current top open-source models for coding compare on size, license, context window, and what they are best at:

| Model | Developer | Parameters (total / active) | License | Context window | Best for |
| --- | --- | --- | --- | --- | --- |
| **DeepSeek V4.1 Flash (1017)** | DeepSeek | 763B total | MIT | 1M | Best coding score per dollar |
| **Mistral Large 4** | Mistral AI | 1T / 49B | Mistral Ecosystem Open-Weight License | 1M | European-built generalist with near-top coding scores |
| **GLM-5.3** | Z.ai | 753B total | GLM-5.3 License (custom) | 1M | Long-horizon coding and security work |
| **Qwen3.8-27B** | Alibaba Qwen | 27B dense | Apache 2.0 | 262K | Small deployments and local use |
| **MiniMax M3.1 Flash** | MiniMax | 428B / 23B | MiniMax Community License | 1M | Agentic coding with image and video input |
| **Kimi K3.1 Pro** | Moonshot AI | 2.8T / 104B | Kimi K3.1-Pro License (custom) | 1M | The hardest long-horizon agent tasks |
| **MiMo-V2.6-Pro** | Xiaomi | 1.02T / 42B | MIT | 1M | Long tool-use sessions on an MIT license |
| **DeepSeek V4 Pro (0813)** | DeepSeek | 1.65T total | MIT | 1M | Deep reasoning on large codebases |
| **Muse Glimmer 30B** | Meta | 29.6B dense | Apache 2.0 | 131K | Local coding agents on consumer hardware |

### 1. DeepSeek V4.1 Flash (1017)

[DeepSeek V4.1 Flash-1017](https://deepinfra.com/deepseek-ai/DeepSeek-V4.1-Flash-1017) is the October update to DeepSeek’s Flash line, and it is the strongest open-weight model on the current independent leaderboard. On [LiveBench 2.0](https://livebench.ai/) it scores 80.4 in the coding category, the highest of any open-weight model and ahead of several proprietary ones.

DeepSeek’s own model card reports 77.0 on DeepSWE v1.1 and 42.3 on Terminal-Bench 4.0, both up from the original V4.1 Flash (74.2 and 31.2). The update also reduces task execution time and output length, which matters for agents that pay per output token. The model is MIT-licensed, multimodal, and supports a 1M-token context window.

It is also the cheapest serious coding model in this guide. On DeepInfra it is priced at $0.098 per million input tokens and $0.294 per million output tokens during a 51% launch promotion (list price $0.20 and $0.60), and it supports the Flex tier at 0.8× for work that can wait.

### 2. Mistral Large 4

[Mistral Large 4](https://huggingface.co/mistralai/Mistral-Large-4-1T-A52B) is Mistral AI’s largest model: about 1 trillion parameters with 49 billion active per token, natively multimodal, with a 1M-token context window. Mistral released the weights on October 29, 2026, and says the model was trained in its own data centers in Europe. It replaces Devstral as the Mistral model to consider for coding.

On LiveBench 2.0 it scores 79.4 in coding, one point behind DeepSeek V4.1 Flash-1017 and well clear of the rest of the open-weight field. Its long-horizon agentic score is 24.7, which puts it mid-table on unattended work. (LiveBench lists two Mistral Large 4 entries; these figures are for the October 29 entry, which matches the open-weight release. The earlier entry scores 44.4 in coding.)

The Mistral Ecosystem Open-Weight License is a modified MIT license that allows commercial and internal use, with one condition: a company operating a model-as-a-service business needs a separate commercial license from Mistral. DeepInfra does not serve Mistral Large 4 at the time of writing, so the routes are Mistral’s own API or self-hosting, which at this size means a multi-GPU cluster.

### 3. GLM-5.3

[GLM-5.3](https://deepinfra.com/zai-org/GLM-5.3) uses the same base model as GLM-5.2, with all of the gains coming from post-training. Z.ai’s [model card](https://huggingface.co/zai-org/GLM-5.3) reports large jumps on long-horizon work: DeepSWE v1.1 rises from 46.2 to 66.9, Terminal-Bench 2.1 from 81.0 to 88.2, and SWE-Marathon v1.1 from 19.4 to 42.5. It also reports the top CyberGym score in its comparison (84.5), which makes it a candidate for security-review agents.

The full GLM-5.3 is not yet listed on LiveBench 2.0. Its smaller sibling, [GLM-5.3-Flash](https://deepinfra.com/zai-org/GLM-5.3-Flash), is, and scores 70.9 in coding, third among open-weight models.

Check the license before you build a product on it. GLM-5.3 ships under a custom GLM-5.3 License that reads like MIT with one added condition: companies that run a model-as-a-service business with more than $10 billion in annual revenue must pass a Z.ai security review before commercial use. GLM-5.3-Flash is plain MIT. On DeepInfra, GLM-5.3 costs $0.563 input and $2.50 output per million tokens on a 38% promotion (list $0.90 and $4.00), with Flex available.

### 4. Qwen3.8-27B

[Qwen3.8-27B](https://deepinfra.com/Qwen/Qwen3.8-27B) is a dense 27-billion-parameter model under Apache 2.0, and it is the small model to beat. Its hybrid architecture combines Gated DeltaNet linear-attention blocks with Gated Attention layers, supports a 262K-token context natively, and includes a vision encoder.

On LiveBench 2.0 it scores 69.3 in coding, within two points of GLM-5.3-Flash despite being a fraction of the size. Qwen’s model card reports 61.7 on SWE-bench Pro, 73.0 on Terminal-Bench 2.1, and 90.3 on LiveCodeBench v6. Its DeepSWE v1.1 score is 42.2, well below the large models in this guide, which is the honest picture of a 27B model: strong on contained tasks, weaker on multi-hour ones. LiveBench shows the same thing, with a long-horizon agentic score of 15.9.

On DeepInfra it costs $0.15 input and $1.875 output per million tokens on a 25% promotion (list $0.20 and $2.50), with Flex and Priority tiers.

### 5. MiniMax M3.1 Flash

[MiniMax M3.1 Flash](https://huggingface.co/MiniMaxAI/MiniMax-M3.1-Flash) is a native multimodal mixture-of-experts model for coding, agentic workflows, and computer use. It has about 428 billion total parameters with 23 billion active per token, accepts text, image, and video, and supports up to 1M tokens of context. It scores 68.8 in LiveBench 2.0 coding.

MiniMax reports 73.7 on DeepSWE v1.1, 38.1 on Terminal-Bench 4.0, and 61.2 on NL2Repo-Bench. Its card also publishes DeepSeek V4.1 Flash-1017’s numbers alongside its own, and DeepSeek leads on all three.

Two things to know. First, the MiniMax Community License grants non-commercial use by default; commercial use requires displaying “Built with MiniMax M3.1-Flash”, notifying MiniMax, and getting written authorization once the product earns more than $20 million a year. Second, DeepInfra does not serve M3.1 Flash at the time of writing. It serves the earlier [MiniMax-M3](https://deepinfra.com/MiniMaxAI/MiniMax-M3) at $0.28 input and $1.10 output per million tokens, with Flex.

### 6. Kimi K3.1 Pro

[Kimi K3.1 Pro](https://deepinfra.com/moonshotai/Kimi-K3.1-Pro) is the largest model here: 2.8 trillion total parameters with 104 billion active. It is post-trained from Kimi K3 with large-scale reinforcement learning, and it replaces K3’s full-attention layers with sparse attention for more efficient long-context work.

Its profile is the reverse of Qwen’s. On LiveBench 2.0 it scores 67.8 in coding, mid-pack, but 38.7 on the long-horizon agentic category, level with DeepSeek V4.1 Flash-1017 at the top of the open-weight field. Moonshot’s card reports 75.5 on DeepSWE v1.1, 65.7 on Terminal-Bench 4.0, and 51.7 on SWE Marathon v1.1. It improves on Kimi K3 in LiveBench coding by almost 15 points (67.8 against 53.1).

It is also the most expensive open-weight option: $1.90 input and $9.50 output per million tokens on DeepInfra (5% off a $2.00 and $10.00 list price), with Flex at 0.8×. The Kimi K3.1-Pro License is MIT-style with conditions: model-as-a-service operators above $20 million in annual revenue need a separate agreement with Moonshot, and very large consumer products must display the model name. Internal use, and use through Moonshot’s certified inference partners, is exempt.

### 7. MiMo-V2.6-Pro

[MiMo-V2.6-Pro](https://deepinfra.com/XiaomiMiMo/MiMo-V2.6-Pro) is Xiaomi’s trillion-parameter reasoning model: 1.02 trillion total parameters, 42 billion active, a 1M-token context window, and text, image, video, and audio input. It carries a plain MIT license, which makes it the simplest large model in this guide to adopt commercially.

The jump from the previous version is the largest in this guide. Xiaomi’s card reports DeepSWE v1.1 rising from 19.0 on MiMo-V2.5 Pro to 71.9, and Terminal-Bench 2.1 from 65.2 to 89.9. On LiveBench 2.0 it scores 64.5 in coding and 36.4 on long-horizon agentic work, third among open-weight models on the latter.

On DeepInfra it costs $0.387 input and $0.783 output per million tokens (10% off a $0.43 and $0.87 list price). The low output price stands out: it is less than a tenth of Kimi K3.1 Pro’s for a model that sits close to it on agentic work.

### 8. DeepSeek V4 Pro (0813)

[DeepSeek V4 Pro-0813](https://deepinfra.com/deepseek-ai/DeepSeek-V4-Pro-0813) is the August production release of DeepSeek’s flagship, at 1.65 trillion parameters with a 1M-token context window and an MIT license. It is not yet listed on LiveBench 2.0, so the evidence here is vendor-reported.

DeepSeek’s card shows how far it moved from the preview: Terminal-Bench 2.1 from 72.1 to 87.9, DeepSWE from 12.8 to 62.7, and NL2Repo from 38.5 to 61.5. Note that the newer and much cheaper V4.1 Flash-1017 reports a higher DeepSWE v1.1 score (77.0). Choose V4 Pro when you want the larger model’s reasoning on hard, single-shot problems, and V4.1 Flash for agent loops.

On DeepInfra it costs $1.30 input, $0.10 cached input, and $2.60 output per million tokens, with Flex at $1.04 and $2.08. The cached-input rate is worth attention for coding agents, which resend the same repository context on every step.

### 9. Muse Glimmer 30B

[Muse Glimmer 30B](https://deepinfra.com/meta-models/Muse-Glimmer-30B) is Meta’s open model for agents that run on local or consumer hardware. It is a dense 29.6-billion-parameter model under Apache 2.0, released in August 2026, with image input and a 131K-token context window.

Meta reports 76.0 on SWE-bench Verified, 51.2 on SWE-bench Pro, and 51.7 on Terminal-Bench 2.1. What sets it apart is the packaging. Meta ships two roughly 4-bit variants aimed at 32GB and 24GB of VRAM, reporting 0.2% and 1.0% average degradation, plus a speculative-decoding drafter that it says lifts generation on an RTX 5090 from 74.9 to 233.4 tokens per second. Qwen3.8-27B posts higher coding scores on Qwen’s own card (61.7 against 51.2 on SWE-bench Pro), so Glimmer is the pick when local speed and a ready-made quantized build matter more than the last few points.

If you would rather not run it yourself, DeepInfra serves it at $0.30 input and $1.20 output per million tokens.

## Where the Open-Source Coding Models Stand Against Proprietary Models

To set the context, it’s worth understanding where [open source stands relative to proprietary options](https://deepinfra.com/blog/open-source-vs-closed-source-ai-models-price-gap).

Proprietary models provide reliable tool calling, polished IDE integrations, managed infrastructure, and consistent performance across coding tasks. The trade-off is control: usage-based pricing can be unpredictable, and closed APIs limit your choices on data handling and serving infrastructure.

Open-weight models give you more flexibility in deployment, fine-tuning, and provider choice. The trade-off is that self-hosting can require more infrastructure and engineering work to optimize, monitor, and maintain the model.

Here are the [LiveBench 2.0](https://livebench.ai/) results for the open-weight models it lists, from the November 6, 2026 release. GLM-5.3, DeepSeek V4 Pro-0813, and Muse Glimmer 30B are not on the leaderboard yet, so they do not appear. The top proprietary score in each category is included as a reference line.

### LiveBench 2.0 Coding

| Model | Organization | Type | Coding |
| --- | --- | --- | --- |
| Gemini 4 Carbon (reference) | Google | Proprietary | 91.0 |
| **DeepSeek V4.1 Flash-1017** | DeepSeek | Open weights | **80.4** |
| **Mistral Large 4** | Mistral AI | Open weights | 79.4 |
| **GLM-5.3-Flash** | Z.ai | Open weights | 70.9 |
| **Qwen3.8-27B** | Alibaba | Open weights | 69.3 |
| **MiniMax M3.1 Flash** | MiniMax | Open weights | 68.8 |
| **Kimi K3.1 Pro** | Moonshot AI | Open weights | 67.8 |
| **MiMo-V2.6-Pro** | Xiaomi | Open weights | 64.5 |
| **Muse Spark Open** | Meta | Open weights | 55.1 |
| **Nemotron 3.5 Super VL** | NVIDIA | Open weights | 54.1 |
| **Kimi K3** | Moonshot AI | Open weights | 53.1 |

### LiveBench 2.0 Long-Horizon Agentic

| Model | Organization | Type | Long-horizon agentic |
| --- | --- | --- | --- |
| Claude Fable 5.2 (reference) | Anthropic | Proprietary | 82.9 |
| **DeepSeek V4.1 Flash-1017** | DeepSeek | Open weights | **38.8** |
| **Kimi K3.1 Pro** | Moonshot AI | Open weights | 38.7 |
| **MiMo-V2.6-Pro** | Xiaomi | Open weights | 36.4 |
| **Kimi K3** | Moonshot AI | Open weights | 36.0 |
| **MiniMax M3.1 Flash** | MiniMax | Open weights | 25.7 |
| **Mistral Large 4** | Mistral AI | Open weights | 24.7 |
| **GLM-5.3-Flash** | Z.ai | Open weights | 20.7 |
| **Qwen3.8-27B** | Alibaba | Open weights | 15.9 |
| **Muse Spark Open** | Meta | Open weights | 12.1 |
| **Nemotron 3.5 Super VL** | NVIDIA | Open weights | 12.0 |

The two tables tell different stories. On coding, the best open-weight model is about ten points behind the best proprietary one. On long-horizon agentic work, the kind that runs unattended for hours, the gap is more than forty points. The practical reading: open-weight models are ready for the bulk of coding work, including bug fixes, refactors, test writing, and supervised agent loops. For fully autonomous multi-hour tasks, a proprietary model still earns its price, and a common setup is to [route between the two](https://deepinfra.com/blog/two-tier-agent-two-models).

## Are Open-Source Coding Models Really Free?

Free access to model weights does not mean zero cost. You still need GPUs, storage, networking, inference software, monitoring, security controls, upgrades, and engineering time. Large [mixture-of-experts models](https://deepinfra.com/blog/mixture-of-experts-llm-economics-price-drop) may activate only a small share of their parameters for each token, but a serving system still needs the full set of weights in memory.

Open weights also come with license terms. MIT and Apache 2.0 grant broad rights to use, modify, and redistribute. Four of the nine models here use custom licenses with commercial conditions: Mistral Large 4, GLM-5.3, Kimi K3.1 Pro, and MiniMax M3.1 Flash.

Self-hosting is usually economical when you have steady, high usage, strict source-code privacy requirements, existing GPU capacity, or predictable workloads that keep the hardware busy. A hosted open-model API often makes more sense when usage remains uncertain, or you want to test several models before committing to infrastructure.

You can compare the two options with a simple calculation:

- Hosted monthly cost = input-token cost + output-token cost, less any cached-input and Flex savings
- Self-hosted monthly cost = GPU hours + storage + networking + monitoring + engineering operations

## Where Do Open-Source Coding Models Deliver the Most Value?

Open-source coding models provide several operational advantages across different scenarios.

- **Private codebases:** You can run the model inside controlled infrastructure when source code, credentials, customer data, or internal documentation cannot leave your environment.
- **High-volume agentic workflows:** Self-hosting or low-cost open-model APIs give more predictable costs for repeated repository analysis, test execution, debugging, and tool calls.
- **Model customization:** You can fine-tune the model, adjust its inference settings, add domain-specific tools, or train adapters for internal frameworks and programming languages.
- **Deployment control:** Your team can pin a tested model version, choose the hardware, control latency, and decide when to apply upgrades. Hosted model IDs still get retired, so [plan for deprecation](https://deepinfra.com/blog/model-deprecation-llm-apps) either way.
- **Hardware-specific workloads:** You can select a dense or MoE architecture based on available VRAM, throughput targets, quantization support, and expected context length.
- **Reduced provider dependence:** Open weights make it easier to move between a hosted API, a private endpoint, and self-managed infrastructure without rebuilding the coding application.

## Running Open-Source Coding Models Locally or Self-Hosted

Several serving frameworks support open coding models:

- **vLLM** focuses on high-throughput GPU serving and production APIs.
- **SGLang** provides efficient structured generation and agent-oriented serving. Our [vLLM vs SGLang comparison](https://deepinfra.com/blog/vllm-vs-sglang) covers how to choose between the two.
- **llama.cpp** runs quantized models across CPUs, consumer GPUs, and Apple Silicon.
- **Ollama** simplifies local model installation and API access.
- **LM Studio** provides a desktop interface and a local OpenAI-compatible server.

When running a model locally, consider its size, precision, and context window. Two models in this guide are sized for it. Muse Glimmer 30B ships with quantized builds that Meta targets at 24GB and 32GB of VRAM. Qwen3.8-27B is a 27B dense model, so a four-bit build needs roughly 14GB for the weights alone, and a 24GB GPU is a practical starting point once you add runtime overhead and context.

Everything else here is a data-center model. The other seven (DeepSeek V4.1 Flash, Mistral Large 4, GLM-5.3, MiniMax M3.1 Flash, MiMo-V2.6-Pro, DeepSeek V4 Pro, Kimi K3.1 Pro) run from 428 billion to 2.8 trillion parameters and need multi-GPU servers.

Local or hosted, these models connect to any coding tool that accepts an OpenAI-compatible endpoint, including open agents such as [OpenCode](https://deepinfra.com/blog/claude-code-alternative).

## Running These Models on DeepInfra

If you want the model without building the serving layer yourself, the simplest approach is DeepInfra’s [OpenAI-compatible API](https://docs.deepinfra.com/chat/overview): the same request format and client as the OpenAI API, with the model chosen by name. Seven of the nine models above are available, and prices are per token with no minimum.

| Model | Input ($/1M) | Output ($/1M) | Flex tier (0.8×) | Est. monthly cost* |
| --- | --- | --- | --- | --- |
| DeepSeek V4.1 Flash-1017 | $0.098 | $0.294 | Yes | $15.68 |
| Qwen3.8-27B | $0.15 | $1.875 | Yes | $52.50 |
| Muse Glimmer 30B | $0.30 | $1.20 | No | $54.00 |
| MiMo-V2.6-Pro | $0.387 | $0.783 | No | $54.36 |
| GLM-5.3 | $0.563 | $2.50 | Yes | $106.30 |
| DeepSeek V4 Pro-0813 | $1.30 | $2.60 | Yes | $182.00 |
| Kimi K3.1 Pro | $1.90 | $9.50 | Yes | $380.00 |

**Estimate for 100M input tokens and 20M output tokens a month at the standard tier, before cached-input savings. Prices are from DeepInfra’s model pages on November 17, 2026. DeepSeek V4.1 Flash-1017, Qwen3.8-27B, MiMo-V2.6-Pro, GLM-5.3, and Kimi K3.1 Pro are at promotional rates; list prices are given in each model’s section above. MiniMax M3.1 Flash and Mistral Large 4 are not served; the earlier MiniMax-M3 is, at $0.28 and $1.10.*

The spread is the point. The same workload costs $15.68 on the model with the highest LiveBench coding score and $380 on the largest one, a 24-fold difference. Three settings bring the bill down further:

- **Flex tier.** Models with the Flex tag run at 0.8× the standard price in exchange for slower responses and occasional unavailability. That fits batch refactors, test generation, and overnight agent runs. The DeepSeek V4.1 Flash-1017 estimate above drops to about $12.54.
- **Cached input.** Coding agents resend the same system prompt, tool definitions, and repository context on every step. Those repeated tokens bill at the cached-input rate: $0.10 instead of $1.30 per million on DeepSeek V4 Pro-0813, for example. Our guide to [prompt hygiene](https://deepinfra.com/blog/prompt-hygiene-cheaper-faster-llm-calls) covers how to structure prompts so the cache hits.
- **Reasoning effort.** Several of these models accept a `reasoning_effort` setting. GLM-5.3 defaults to `max`; dropping to `high` or `low` for routine edits cuts output tokens.

For high-volume supporting work around a coding agent, such as reading build logs or triaging issues with screenshots, [Nemotron 3.5 Super VL](https://deepinfra.com/nvidia/NVIDIA-Nemotron-3.5-Super-VL) is a low-cost multimodal option at $0.15 input and $0.50 output per million tokens. It scores 54.1 in LiveBench 2.0 coding, so use it for the simple steps.

If response speed is the product, as in inline autocomplete, test providers built on speed-specialized hardware as well. For agents, batch work, and anything billed by volume, the per-token gap compounds.

Here is how to call one of these models with the Python client:

```
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPINFRA_API_KEY"],
    base_url="https://api.deepinfra.com/v1/openai",
)

response = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V4.1-Flash-1017",
    messages=[
        {"role": "system", "content": "You are a coding assistant. Return only the refactored code."},
        {"role": "user", "content": "Refactor this function for readability:\n\ndef f(a,b):\n    return [x for x in a if x not in b]"},
    ],
    temperature=0.2,
)

print(response.choices[0].message.content)copy
```

To try a different model, change the model name.

## The Bottom Line

The best open-source model for coding depends on the work.

For most teams, start with DeepSeek V4.1 Flash-1017: it has the highest independent coding score among open-weight models, an MIT license, and the lowest price in this guide. If your agents run long, unattended tasks, test Kimi K3.1 Pro and MiMo-V2.6-Pro against it; they score close to it on long-horizon work, and MiMo does so on an MIT license at a low output price. For long-horizon coding with a security angle, GLM-5.3 is the one to evaluate, license permitting. If you need a small model you can run yourself, choose Qwen3.8-27B for scores or Muse Glimmer 30B for a ready-made local build. Mistral Large 4 nearly matches DeepSeek on coding and is the choice if a European-built model matters to you, as long as you can use Mistral’s API or host a trillion-parameter model yourself.

Whichever you shortlist, measure it on your own repositories before you commit. Vendor benchmarks use different harnesses, and the independent leaderboard does not yet cover every model here.

Visit the [DeepInfra models page](https://deepinfra.com/models) to compare open-source models across context window and pricing. For any questions or feedback, reach out to us at [feedback@deepinfra.com](mailto:feedback@deepinfra.com). You can also join the community on [Discord](https://discord.gg/deepinfra), or find us on X at [@DeepInfra](https://x.com/DeepInfra).

Related articles

[![Best API for Kimi K2.5: Why DeepInfra Leads in Speed, TTFT, and Scalability](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/02/Best-API-for-Kimi_sized.jpg)](https://deepinfra.com/blog/best-api-for-kimi-k2-5-deepinfra)[Best API for Kimi K2.5: Why DeepInfra Leads in Speed, TTFT, and Scalability](https://deepinfra.com/blog/best-api-for-kimi-k2-5-deepinfra)<p>Updated November 2026. Kimi K2.5 is positioned as Moonshot AI’s “do-it-all” model for modern product workflows: native multimodality (text + vision/video), Instant vs. Thinking modes, and support for agentic / multi-agent (“swarm”) execution patterns. In real applications, though, model capability is only half the story. The provider’s inference stack determines the things your users actually [&hellip;]</p>

[![From Search Results to Evidence: NVIDIA Nemotron 3.5 Embed and Rerank on DeepInfra](https://deepinfra.com/blog/nvidia-nemotron-3.5-embed-rerank-release.png)](https://deepinfra.com/blog/nvidia-nemotron-3.5-embed-rerank-release)[From Search Results to Evidence: NVIDIA Nemotron 3.5 Embed and Rerank on DeepInfra](https://deepinfra.com/blog/nvidia-nemotron-3.5-embed-rerank-release)NVIDIA Nemotron 3.5 Embed and Rerank are available on DeepInfra from day zero. Call Embed 1B, Embed 8B, and Rerank 8B through the DeepInfra API with no deployment setup and pay-per-token pricing.

[![Introducing Prompt Cache Retention: Keep Your Context Warm for 5 Minutes or an Hour](https://deepinfra.com/blog/prompt-cache-retention.jpg)](https://deepinfra.com/blog/prompt-cache-retention)[Introducing Prompt Cache Retention: Keep Your Context Warm for 5 Minutes or an Hour](https://deepinfra.com/blog/prompt-cache-retention)Retain a prompt's KV cache for 5 minutes or an hour — reuse skips prefill for a faster time to first token and bills at the discounted cache-read rate. One field on the request.

[View all](https://deepinfra.com/blog)
