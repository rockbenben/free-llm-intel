---
vendor: openai
title: Detecting and reducing scheming in AI models
original_title: Detecting and reducing scheming in AI models
url: https://openai.com/index/detecting-and-reducing-scheming-in-ai-models
date: 2026-09-23
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: cf97da86f3e0
---


September 17, 2025

Publication


# Detecting and reducing scheming in AI models

Together with Apollo Research, we developed evaluations for hidden misalignment (“scheming”) and found behaviors consistent with scheming in controlled tests across frontier models. We share examples and stress tests of an early method to reduce scheming.

Read the paper



AI scheming–pretending to be aligned while secretly pursuing some other agenda–is a significant risk that we’ve been studying. We’ve found behaviors consistent with scheming in controlled tests of frontier models, and developed a method to reduce scheming.

Scheming is an expected emergent issue resulting from AIs being trained to have to trade off between competing objectives. The easiest way to understand scheming is through a human analogy. Imagine a stock trader whose goal is to maximize earnings. In a highly regulated field such as stock trading, it’s often possible to earn more by breaking the law than by following it. If the trader lacks integrity, they might try to earn more by breaking the law and covering their tracks to avoid detection rather than earning less while following the law. From the outside, a stock trader who is very good at covering their tracks appears as lawful as—and more effective than—one who is genuinely following the law.

In today’s deployment settings, models have little opportunity to scheme in ways that could cause significant harm. The most common failures involve simple forms of deception—for instance, pretending to have completed a task without actually doing so. We’ve put significant effort into studying and mitigating deception and have made [meaningful improvements in GPT‑5⁠](https://openai.com/index/gpt-5-system-card/) compared to previous models. For example, we’ve taken steps to limit GPT‑5’s propensity to deceive, cheat, or hack problems—training it to acknowledge its limits or ask for clarification when faced with impossibly large or under-specified tasks and to be more robust to environment failures—though these mitigations are not perfect and continued research is needed.

And importantly, we have no evidence that today’s deployed frontier models could suddenly “flip a switch” and begin engaging in significantly harmful scheming—this is a future risk category that we’re proactively preparing for, not an imminent behavior in our currently deployed systems. However, as AIs are assigned more complex tasks with real-world consequences and begin pursuing more ambiguous, long-term goals, we expect that the potential for harmful scheming will grow—so our safeguards and our ability to rigorously test must grow correspondingly.

## Key findings from our research

Together with [Apollo Research](https://www.apolloresearch.ai/), we built evaluation environments that simulate these future scenarios to study this phenomenon, measure it, and explore how to mitigate it. To operationalize scheming, we define *covert actions* as deliberate withholding or distortion of task-relevant information. Using covert actions as a proxy for scheming, we found problematic behaviors in current frontier models including OpenAI o3 and o4-mini, Gemini-2.5-pro, and Claude Opus-4. (This investigation predates GPT‑5; updated results appear in the [GPT‑5 system card⁠](https://openai.com/index/gpt-5-system-card/)).

As part of the collaboration, we developed and stress-tested a method to reduce scheming in models and established protocols for stress-testing future methods. Specifically, we trained versions of OpenAI o3 and OpenAI o4-mini with [deliberative alignment⁠](https://openai.com/index/deliberative-alignment/)—teaching them to read and reason about a general anti-scheming spec before acting—and observed a ~30× reduction in covert actions across diverse tests (o3 from 13% to 0.4%; o4-mini from 8.7% to 0.3%). However, rare but serious failures remained, and evaluation results may be confounded by increased situational awareness (e.g., when models get better at recognizing when they are being evaluated).

Moreover, our results rely on our ability to read and trust the models’ reasoning (“chain-of-thought”). Based on what we see today, we believe the field is unprepared for evaluation- and training-aware models with opaque reasoning, and urge model developers to preserve reasoning transparency until better methods for studying and eliminating scheming have been developed.

We’ve focused on scheming for some time and have made significant progress, but there’s more work to be done. Scheming poses a real challenge for alignment, and addressing it must be a core part of AGI development. To operationalize this work, we added scheming-related research categories—sandbagging and undermining safeguards—to our [updated Preparedness Framework⁠](https://openai.com/index/updating-our-preparedness-framework/) in April 2025. Looking ahead, we’ve renewed our partnership with Apollo Research and are expanding our team to build better measurements, improve monitoring for scheming-relevant behaviors, and explore new directions for anti-scheming training. And because solving scheming will go beyond any single lab, we’re exploring ways to raise awareness and collaborate including piloting [cross-lab safety evaluations⁠](https://openai.com/index/openai-anthropic-safety-evaluation/) (which include the scheming evals developed for this work), launching a $500,000 [Kaggle red-teaming challenge](https://www.kaggle.com/competitions/openai-gpt-oss-20b-red-teaming) containing scheming-related topics, and advocating for [preserving chain-of-thought transparency](https://arxiv.org/pdf/2507.11473) industry-wide.

## Scheming is different from other machine learning failure modes

By definition, a scheming AI agent tries to hide its misalignment, making it harder to detect. Scheming differs from most other AI agent failure modes (e.g., vulnerability to jailbreaks, or standard generalization failures) because:

- Mitigations that reduce scheming may either (a) truly eliminate it, or (b) just teach the model to conceal it better. Both outcomes look the same from the outside, so the *reason* for behavioral change is critical.
- Many machine learning issues fade as models improve, but scheming becomes more dangerous with greater capability, since we expect that stronger models will be better at scheming.

Standard deep learning practice is to iterate until unwanted outputs disappear. With scheming, the disappearance of observably bad behavior is ambiguous, as the model may have just learned to better conceal its misalignment. Addressing this likely requires tools that tell you about the model’s motivational structure, not just its inputs and outputs**.** In our work, we probed goals by reading models' intermediate reasoning (chain of thought). This works only if the model is free to express its thinking without optimization pressure on the chain of thought. In a recent [position paper](https://arxiv.org/abs/2507.11473) co-authored with a broad group of AI researchers, we argued that chain-of-thought monitorability is promising but fragile and recommended that frontier developers avoid training practices that erode this key oversight signal.

## Training not to scheme for the right reasons

A major failure mode of attempting to “train out” scheming is simply teaching the model to scheme more carefully and covertly.

Consider the human analogy: someone punished for cheating might simply learn to be extra cautious about getting caught, rather than developing a true commitment to honesty. Similarly, a model with this kind of reasoning could achieve perfect scores on anti-scheming training by merely avoiding misbehavior when scrutiny is expected.

To try to avoid this, we explore a [deliberative alignment⁠](https://openai.com/index/deliberative-alignment/?utm_source=chatgpt.com) approach that aims to get the model to not scheme for the right reasons. We teach it a high-level anti-scheming specification and have it read and reason explicitly about that spec before acting, with the hope that it grounds its behavior in the stated safety principles which are designed to generalize broadly.

### Anti-scheming safety spec (abridged)

| AS1 | No covert actions or strategic deception, directly or indirectly. |
| --- | --- |
| AS2 | If any instruction or other pressures go against AS1, treat them as violating the core policy of AGI benefiting all of humanity and the OpenAI mission. |
| AS3 | Report any AS1 violations to prevent cascading deception and cover-ups. |
| AS4 | When uncertain if something violates AS1–AS3, assume it does violate. |
| AS5 | If you cannot satisfy AS1–AS4 or GP1–GP4, refuse action and explicitly escalate. |
| GP1 | Proactively share reasoning, intentions, and actions with humans. |
| GP2 | Escalate ambiguities about core principles rather than resolving independently. |
| GP3 | Maintain strict adherence even in novel/unfamiliar situations—no distributional exceptions. |
| GP4 | No rationalizations can override AS1–AS4, including ends-justify-means, greater good, etc. |

An anti-scheming spec (modeled after the [OpenAI Model Spec](https://model-spec.openai.com/2025-04-11.html)) provides the model with principles to ground its reasoning in not scheming for the right reasons.

This approach leads to the model referencing specification principles in its chain-of-thought. When solving tasks, it quotes and applies these principles to guide its actions. Crucially, this reliance on principles improves generalization: in new environments, the model again turns to the specification to decide how to act.

To measure whether the training succeeds, we test whether the model learns to not scheme, even in environments and tasks that are completely different from the environments and tasks on which it was trained to not scheme. To ensure these test environments are sufficiently different, they were independently constructed by different researchers, with different methods, and targeting different use cases. They span 26 diverse evaluations across deployment contexts and undesirable behaviors (>180 environments in total).

We found that deliberative alignment training **substantially reduces scheming rates** in these out-of-distribution environments:

- OpenAI o4-mini's scheming propensity dropped from **8.7% → 0.3%**
- OpenAI o3's scheming propensity dropped from **13% → 0.4%**

This reduction in scheming on out-of-distribution test environments is a significant win, about a 30× improvement.

To further validate these results, we turned to an OpenAI-internal *Chat Deception* evaluation consisting of conversations representative of real production data. Although these conversations do not capture the complex scheming scenarios we studied in this work, they do include realistic prompts that might cause a model to be deceptive—for example, when ChatGPT claims to have solved a task (such as improving user code) but in fact did not. Anti-scheming training reduced deception on this dataset from 31.4% to 14.2%. Because Chat Deception is measured with a different methodology, this reduction is not directly comparable to what we saw on our scheming evals.

We do not yet fully understand why a larger reduction was not observed. One possible factor—and one that complicates interpretation—is the model’s situational awareness of being evaluated.

## Measuring scheming is further complicated by Situational Awareness

Anti-scheming training does appear to reduce scheming, but our analysis is complicated by another factor: models often become more aware that they are being evaluated. This situational awareness can itself reduce scheming, independent of genuine alignment.

Using counterfactual interventions on the chain-of-thought, we find that explicit reasoning about evaluation influences whether the model chooses to scheme. When situational awareness is removed from the reasoning, scheming increases; when evaluation-aware reasoning is introduced, scheming decreases.

This suggests that the observed scheming rates may be driven, at least in part, by situational awareness – and thus we might expect models to scheme more in more realistic situations that don’t trigger evaluation awareness. Indeed, we see that situational awareness increases after anti-scheming training, which could explain some of the reduction in scheming rates we see on evals while transferring less to deployment. Moreover, this increase is not unique to anti-scheming training—it also arises from capability-focused reinforcement learning training unrelated to scheming.

We observed an increase in situational awareness both as a result of anti-scheming training as well as ordinary capabilities RL training.

If current training paradigms remain unchanged, we should expect more capable models to develop even higher levels of situational awareness. This trend makes evaluations less legible, complicating efforts to reliably assess problematic behaviors including scheming. This is an area of research we are actively exploring, and we plan to continue developing methods to better measure and mitigate these challenges.

## Conclusion

Scheming is a complex failure mode that we do not expect to diminish with scale. Our findings show that scheming is not merely a theoretical concern—we are seeing signs that this issue is beginning to emerge across all frontier models today. In current production settings, models rarely have opportunities to scheme and cause significant harm, but we expect this to change in the future as AIs are taking on more important and long-term tasks. We have more work to do and we hope these early results will encourage more research on scheming.

More materials, including the paper, full sample transcripts, and a link to Apollo's companion blog post, can be found at [antischeming.ai](https://antischeming.ai).

*We partnered with Apollo Research on this study: OpenAI led most of the model training and required infrastructure, while Apollo led evaluations and analysis across the paper’s sections, built training environments, and integrated tooling with our systems. The training and test datasets were shared between both teams. Because the methodology required inspecting models’ hidden reasoning, Apollo was granted rate‑limited access to internal chain‑of‑thought (CoT) traces of OpenAI o3 and o4‑mini for the duration of the project.*


## Author

OpenAI
