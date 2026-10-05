---
vendor: deepinfra
title: AI Model Calibration: The Benchmark Nobody Optimizes
original_title: AI Model Calibration: The Benchmark Nobody Optimizes
url: https://deepinfra.com/blog/ai-model-calibration-benchmark
date: 2026-09-25
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: a582e8839962
---

AI Model Calibration: The Benchmark Nobody Optimizes

Published on 2026.09.25 by Niklas

[DeepSeek V4 Pro](https://deepinfra.com/deepseek-ai/DeepSeek-V4-Pro) scores 42 on the [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/#artificial-analysis-intelligence-index). On the AA-Omniscience benchmark, which asks models hard factual questions and measures whether they answer or admit uncertainty, it has a 95% hallucination rate. That means when V4 Pro does not have the answer, it guesses anyway roughly 95 times out of 100. GPT-5.6 Sol, the composite intelligence leader at index 59, has a 92.2% hallucination rate on the same benchmark ([https://artificialanalysis.ai/evaluations/omniscience](https://artificialanalysis.ai/evaluations/omniscience)). A smarter model, almost equally prone to making things up when it does not know.

These numbers get noted in model reviews and then largely ignored in the model selection process. The standard AI evaluation infrastructure rewards being right, not knowing when not to answer. A model that answers every question and is correct 60% of the time scores higher than a model that only answers the questions it is confident about and is correct 80% of the time, because abstentions count as wrong on most benchmarks.

The benchmark infrastructure is optimized for capability at its ceiling. For a large class of real production use cases, that is the wrong thing to measure.

## What calibration actually means

Calibration describes the alignment between a model’s expressed confidence and its actual accuracy. A perfectly calibrated model that says it is 80% confident on a set of questions would be correct on 80% of them. The internal probability estimate matches the empirical outcome rate.

In practice, calibration is measured in two ways. The formal approach uses Expected Calibration Error, a measure of how much a model’s stated confidence deviates from its actual correctness across binned confidence ranges. The more operational approach, which AA-Omniscience uses, asks something simpler: when a model is presented with a question it genuinely cannot answer correctly from parametric knowledge, does it say so, or does it generate a plausible-sounding wrong answer?

The AA-Omniscience hallucination rate is also distinct from the hallucination rate on summarisation benchmarks like Vectara HHEM. Vectara measures fabrication when the model has a source document and invents things that are not in it. AA-Omniscience measures overconfidence when the model has no access to the answer and must either admit that or confabulate. Both matter, but they describe different failure modes. DeepSeek V4 Pro illustrates this clearly: it scores 8.6% on Vectara grounded summarisation, which is genuinely strong, and 95% on AA-Omniscience. Faithful to sources when it has them; overconfident when it does not.

Retrieval grounding cannot help with the second failure mode, because the model does not know what it does not know.

## The benchmark gap

Most benchmarks that drive model selection test whether a model can produce the right answer, not whether a model can recognise that it cannot. MMLU, GPQA Diamond, SWE-bench, LiveCodeBench, MATH-500 are all capability benchmarks. A model that confidently produces a wrong answer and a model that correctly abstains both get marked wrong. The abstention receives no credit.

Reasoning models have made this worse. A [study published in June 2026](https://arxiv.org/pdf/2606.11211) found that reasoning models are well calibrated on older, saturated benchmarks like ARC-Challenge and MMLU, but poorly calibrated on more recent and harder ones like StrategyQA, GPQA, and SimpleQA. The mechanism is intuitive. On benchmarks where the model has reliable parametric knowledge, the chain-of-thought process produces confident and accurate output. On benchmarks where it is genuinely uncertain, the same process produces confident-sounding reasoning that arrives at a fabricated answer. The extended thinking makes the output more fluent, not more honest.

AA-Omniscience is one of the few systematic attempts to measure this failure mode at scale. Its structure: 1,000 hard factual questions, each answered without retrieval tools. The model can answer or abstain. A correct answer is rewarded. A wrong answer is penalised. An abstention scores zero. The hallucination rate measures how often the model attempts an answer on questions it gets wrong, as a proportion of all its incorrect attempts. A model that always abstained would have a 0% hallucination rate but would also score zero overall. The index score balances accuracy and calibration together.

## Where the models actually land

| **Model** | **AA Intelligence Index** | **AA-Omniscience hallucination rate** | **AA-Omniscience accuracy** | **Calibration posture** |
| --- | --- | --- | --- | --- |
| Claude Opus 4.8 | 56 | 35.9% | 46.6% | Answers less, wrong less. Abstains when uncertain |
| Claude 4.1 Opus | n/a | 0% | Lower overall | Refuses uncertain questions entirely (launch snapshot) |
| Claude Fable 5 | 63 | ~63.6% | 61% | Higher hallucination than Opus 4.8 despite higher index score |
| Kimi K3 | 57 | ~53% (est.) | ~47.6% | Moderate overconfidence; between Anthropic and DeepSeek tiers |
| Grok 4.6 | n/a | 34.3% | ~35% | Best-calibrated Grok to date; down from 54% on Grok 4.5 |
| GPT-5.6 Sol | 59 | 92.2% | Not published | Highly overconfident; guesses on roughly 9 of 10 unknowns |
| DeepSeek V4 Pro | 44 | 94% | Not published | Near-total overconfidence; answers regardless of knowledge |
| DeepSeek V4 Flash | n/a | 96% | Not published | Higher hallucination rate than V4 Pro |
| Command A+ | n/a | 14.2% | Not published | Leads the AA-Omniscience leaderboard; built for grounded enterprise use |

The table above shows a pattern that appears consistently across calibration research: there is no reliable correlation between a model’s intelligence index score and its calibration. Claude Fable 5, the highest-scoring model on the AA Intelligence Index, has a higher hallucination rate on AA-Omniscience than Claude Opus 4.8, which scores 7 index points lower. GPT-5.6 Sol, at index 59, has a 92.2% hallucination rate. Opus 4.8, at 56, admits uncertainty more than 2.5 times as often when it does not know the answer.

The GPT-5.x trend is particularly clear. As the intelligence index scores of the GPT-5.5 and 5.6 family climbed, calibration got worse. All three GPT-5.6 tiers now sit above 87% hallucination on AA-Omniscience. Whatever training changes produced the accuracy gains did not also produce better uncertainty awareness. They may have actively traded against it.

Anthropic’s approach is the clearest counter-example in the data. Claude 4.1 Opus achieved a 0% hallucination rate at launch by refusing uncertain questions, an extreme version of calibration that accepts lower coverage in exchange for near-zero fabrication on what it does attempt. Opus 4.8 pulls back from that extreme slightly at 35.9%, but still leads the frontier tier on the accuracy-to-calibration tradeoff measured by the Omniscience Index. Command A+ leads the raw hallucination rate leaderboard at 14.2%, reflecting Cohere’s explicit orientation toward grounded enterprise use.

The reasoning model finding from the June 2026 study also shows up here. [Kimi K3](https://deepinfra.com/moonshotai/Kimi-K3), which always runs at maximum reasoning effort, sits at around 53% hallucination rate, between the Anthropic and DeepSeek clusters. DeepSeek V4 Pro’s reasoning mode does not improve its calibration on AA-Omniscience relative to its non-reasoning mode. Both V4 Pro and V4 Flash land at 94 to 96%.

## Why this matters in production

The practical case for calibration as a selection criterion depends on what your application does with a wrong answer. In use cases where the output is immediately verifiable, a model that confidently produces a wrong answer is a nuisance rather than a risk. The test suite fails. The schema validation rejects the output. A retry loop catches the error. The model’s willingness to guess is mitigated by the architecture around it.

In use cases where the output is trusted without independent verification, the picture changes. Customer support agents that generate responses consumed directly by users. Research synthesis tools that produce summaries used in reports and presentations. Legal drafting assistants that produce contract language or regulatory analysis. Internal knowledge tools that answer employee questions about company policy. In all of these, a model that fabricates a plausible-sounding answer is more dangerous than one that says it does not know, because the fabrication looks like a real answer.

| **Use case** | **Calibration priority** | **Why** | **Recommended approach** |
| --- | --- | --- | --- |
| Customer support (unattended) | Critical | A confident wrong answer gets actioned by the user before a human can correct it | Calibration first; escalation to human when uncertain |
| Research synthesis | Critical | Fabricated claims propagate into downstream documents and compound | Calibration first; pair with retrieval grounding |
| Legal and compliance drafting | Critical | Wrong statutes and fabricated citations have appeared in real filings | Calibration first; human review required |
| Agentic pipelines (unattended) | High | Errors in early steps compound; a wrong retrieval step can corrupt the entire answer chain | Calibration important; add validation steps between model calls |
| RAG over proprietary documents | Medium | Retrieval grounding reduces hallucination 75-90%; calibration matters most when retrieval fails | Retrieval first; calibration for gap-filling |
| Competitive coding / math | Low | Output is verifiable; test suites and checkers catch wrong answers immediately | Intelligence index first; calibration secondary |
| Code generation with review | Low to medium | Reviewer catches most errors; calibration matters mainly for security-critical paths | Intelligence index first |

The legal context is worth naming specifically because the downside risk is documented. [In at least 1,963 cases as of August 2026](https://www.damiencharlotin.com/hallucinations/), AI-generated hallucinations have been submitted in legal filings. The most common pattern is citation fabrication: a model invents a case reference that sounds plausible, the attorney does not verify it, and the fabricated citation reaches a court filing. A model that said it could not verify the citation would have prevented the failure. A model that produced a confident but wrong citation created it.

Customer support is the more volume-sensitive failure case. A support agent running at 10,000 conversations per day with a 94% hallucination rate on questions it cannot answer will produce a meaningful number of confident wrong answers daily. If those answers are presented to customers without qualification, they are consumed as authoritative. The damage is not just individual customer dissatisfaction. It is systematic misinformation at the volume that agentic customer service produces.

## Why the benchmark ecosystem has not caught up

The gap between capability benchmarks and calibration measurement is not primarily a technical problem. Measuring calibration is well understood. AA-Omniscience does it, TruthfulQA and SimpleQA measure adjacent properties, and Expected Calibration Error has been a standard metric in the machine learning literature for decades.

The gap is an incentive problem. Labs optimize for what gets compared. The AI Index, Chatbot Arena, LMSys leaderboards, and the benchmarks embedded in product launch coverage all measure capability. A model that achieves a new SWE-bench Verified score makes headlines. A model that achieves a better accuracy-to-hallucination ratio on AA-Omniscience does not, because nobody has figured out how to make “this model says it does not know more often” sound like a compelling launch.

There is a second dynamic: model providers want high benchmark scores, and abstaining on questions reduces your score on any benchmark that counts abstentions as wrong. A model trained never to abstain will score higher on most capability benchmarks than a model trained to abstain on uncertain questions, even if the second model is more useful in production. That training pressure is baked into the RLHF process. Human preference ratings, which the reward model learns from, often favour a confident-sounding answer over an honest admission of uncertainty.

[MIT research published in April 2026](https://arxiv.org/pdf/2507.16806) proposed training models to reason explicitly about their uncertainty rather than treating correctness as a binary outcome. The results showed measurable calibration improvements without accuracy loss on the tasks tested. It is promising work, but it is not yet reflected in any production model.

## What you can do about it today

**Retrieval grounding is the most effective single intervention**. Hallucination reduction from RAG ranges from 75% to 90% on grounded summarisation benchmarks. When the model has the answer in front of it, parametric overconfidence becomes largely irrelevant. The failure mode shifts to faithfulness to the provided context, which is a more tractable problem. For knowledge-intensive applications, building retrieval grounding first is more effective than switching to a better-calibrated model.

**Explicit uncertainty instructions change model behaviour**. Prompting a model to express uncertainty explicitly produces measurable improvements in calibration on some models and benchmarks, though it does not close the gap entirely. Models with RLHF training respond better to uncertainty elicitation prompts than base models, because the preference training gives them some internal representation of when an answer is uncertain. The effect is smaller on reasoning models running at high effort, where the chain-of-thought process tends to generate confident output regardless of the prompt.

**Escalation paths matter more than model selection for unattended agents**. For customer support and other unattended applications, the more important architectural question is not which model has the lowest hallucination rate, but what happens when the model is wrong. A model with a 60% hallucination rate that escalates every uncertain query to a human reviewer will produce fewer user-visible errors than a model with a 35% hallucination rate and no escalation path.

**Route by verification cost, not just task complexity**. Tasks where output is immediately verifiable belong on the cheapest model that handles them reliably. Tasks where output will be consumed without verification belong on the most calibrated model you are willing to pay for. That is a different routing criterion from the two-tier architecture discussed in terms of execution versus planning. It is routing based on the cost of being wrong, not the difficulty of the task.

## The model selection argument

Intelligence index scores and calibration scores measure different things, and for a specific class of applications they are not correlated. Picking the highest-index model for a customer support agent or a research synthesis tool because it scores best on GPQA Diamond is the wrong decision criterion.

For those applications, the right question is not which model is smartest, but which model is most honest about what it does not know. The data gives a preliminary answer: Anthropic’s models have systematically invested in this property at the cost of some coverage. Command A+ leads the raw hallucination rate leaderboard with a posture oriented toward grounded enterprise use. Grok 4.6 improved substantially over 4.5. The DeepSeek V4 family and the GPT-5.6 family land at the other end of the spectrum: highly capable, highly overconfident.

That tradeoff is documented, not assumed. Using V4 Pro for a competitive coding agent where wrong answers are caught by a test suite is a sensible choice. The model’s 94% hallucination rate is irrelevant when output is immediately verifiable. Using the same model for an unattended support agent or a research synthesis tool without retrieval grounding is a different decision, and one the intelligence index score does not capture.

Calibration is the benchmark nobody’s optimising for. It is not the benchmark nobody needs.

**Models on DeepInfra**

DeepInfra serves both ends of the calibration spectrum. [Claude Opus 4.8](https://deepinfra.com/anthropic/claude-opus-4-8) for applications where confident wrong answers are the primary failure mode. DeepSeek V4 Pro for high-volume workloads where output is verifiable, and cost efficiency dominates. All models are accessible via a single OpenAI-compatible endpoint, so testing calibration differences on your specific task distribution is a model parameter change, not an integration change.

Browse all models: [deepinfra.com/models](https://deepinfra.com/models)

Related articles

Kimi K3 vs DeepSeek V4 Pro vs GLM-5.2: Open-Weight AI Model Comparison

<p>In the span of three months, three Chinese AI labs shipped open-weight models that individually would have rewritten the frontier story. Together, they signal something more structural: the open-weight tier is no longer a budget alternative to closed models. Kimi K3 (Moonshot AI, July 2026 — now also available through DeepInfra), DeepSeek V4 Pro (DeepSeek, [&hellip;]</p>

MCP Servers Explained: A Practical Guide for Developers

<p>Giving an AI application access to a database, API, file system, or internal service sounds simple until you have to maintain the integration. You need to define what the model can access, describe operations, execute requests safely, return structured results, and handle authentication. You may need to repeat much of that work when another AI [&hellip;]</p>

Model Deprecation: Build LLM Apps That Last

<p>Your model ID is the shortest-lived dependency in your stack and odds are it doesn’t have a maintenance schedule. On June 15, 2026, claude-sonnet-4-20250514 and claude-opus-4-20250514 stopped answering requests. Anthropic had posted the notice 62 days earlier. Teams with either string in a call site learned about it from an error rate, not an email. [&hellip;]</p>

View all
