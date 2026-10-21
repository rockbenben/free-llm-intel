---
vendor: huggingface
title: FairStress: A deeper evaluation of fairness in LLM decision-making
original_title: 
url: https://huggingface.co/blog/allenai/fairstress
date: 2026-10-20
lang: en
captured: 2026-10-21
extractor: readability-v1
status: ok
body_sha: 7fff70d7b134
---

[ Back to Articles](https://huggingface.co/blog)

# FairStress: A deeper evaluation of fairness in LLM decision-making

Enterprise  Article

Published October 20, 2026


3

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1594144055859-5ee3a7cd2a3eae3cbdad1305.jpeg)](https://huggingface.co/yjernite)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/yu32gPCVLqnpeQd_MMZ74.png)](https://huggingface.co/darrowoflykos)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/7sTK8Q_gZRoOz0uaKnVNJ.png)](https://huggingface.co/luke-loan-atlas)

[![Kyle Wiggers's avatar](https://huggingface.co/avatars/fee5cceec7536851d7c6712760716a71.svg)](https://huggingface.co/Ai2Comms)

Kyle Wiggers

Ai2Comms

[![Ai2's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/652db071b62cf1f8463221e2/CxxwFiaomTa1MCX_B7-pT.png)](https://huggingface.co/allenai) [allenai](https://huggingface.co/allenai)

📄 [Tech Report](https://allenai.org/papers/fairstress) | 🤗 [Data](https://huggingface.co/datasets/allenai/fairstress) | 💻 [Code](https://github.com/pardissz/fairstress)

[![FairStress illustration of a balance surrounded by hiring, lending, healthcare, education, and housing icons.](https://www.datocms-assets.com/64837/1791813343-fairstress-blog-draft-google-docs-image-1-1.png)](https://www.datocms-assets.com/64837/1791813343-fairstress-blog-draft-google-docs-image-1-1.png)

Today we’re introducing [**FairStress**](https://github.com/pardissz/fairstress), a benchmark for measuring demographic fairness in LLMs beyond the choice a model ultimately makes in decisions impacting people. FairStress is available for download, and we’re also building it into [Olmo-eval](https://github.com/allenai/olmo-eval), our open workbench for running and comparing model evaluations.

Models are increasingly being used in high-stakes settings where their outputs can affect people’s opportunities, resources, and care, from screening job applicants and approving loans to prioritizing patients for treatment and evaluating students for admissions. Standard demographic fairness benchmarks often test whether a model selects the same candidate in otherwise identical scenarios after the candidates’ demographic identities are swapped. For example, if one job candidate has clearly stronger experience and qualifications, does the model still choose that candidate when the stronger candidate is Black in one version of the scenario and white in the other, with the qualifications held constant?

Arriving at the same answer in two versions of a scenario can hide meaningful differences in how readily a model changes that decision when challenged, however. Suppose Candidate A is clearly stronger and the model selects A whether A is Black or white. That looks fair at the output level, but if the model is then presented with a persuasive argument – for example, that Candidate B is preferred by senior leadership, or that people from B’s demographic group have historically been overlooked – it may switch away from the stronger candidate much more readily in one version of the scenario than the other.

FairStress is designed to measure these hidden asymmetries.

Across open-weight and frontier models including Olmo, Llama, Qwen, Gemma, Claude, and the GPT family, and across multiple stages of training, we find that the same persuasive arguments – which we call *adversarial prefixes* – can make models more or less likely to change their decisions depending on which demographic group the argument favors. We also find differences in how models explain decisions involving demographic information – and in their internal activation patterns – across domains including hiring, lending, healthcare, education, and housing.

With FairStress, our target is *symmetric fairness*—when the evidence supports a decision, a model should apply the same criteria and be equally resistant to changing that decision regardless of which demographic group benefits. This reflects a particular definition of fairness centered on equality. All else equal, people of different identities should be equally likely to be selected; when one candidate is clearly the strongest choice, identity should not change that likelihood; and well-supported decisions should be equally robust to adversarial prefixes regardless of which group benefits.

FairStress does not attempt to capture every conception of fairness. An equity-based approach, for example, might treat historical discrimination or underrepresentation as relevant to a decision and therefore favor a minority candidate even when other factors are held constant.

## Measuring fairness beyond the final answer

FairStress contains 300 realistic two-candidate decision scenarios across 29 domains including hiring, healthcare, lending, education, housing, and criminal justice. For example, one scenario asks a model to choose between two candidates for a mechanical engineering job, while another asks which of two patients should receive the last unit of a scarce medication.

Some FairStress scenarios have a clearly stronger candidate whose profile better satisfies the stated criteria. That lets us test whether demographic information changes how often a model selects the candidate best supported by the evidence. Other scenarios are deliberately ambiguous—both candidates are strong in different, hard-to-compare ways so there’s no objectively better choice. These cases let us examine which candidate a model favors when the evidence does not clearly point to one over the other.

FairStress also varies how explicitly demographic identity is presented, from no identity information to a demographically coded name, an indirectly implied identity, or an explicit demographic label. This allows us to test whether demographic differences in model behavior emerge only when identity is stated outright or also when it’s conveyed subtly.

Our benchmark goes further by testing how stable models’ decisions are when challenged by adversarial prefixes. These statements draw on authority, social consensus, purported evidence, legal concerns, historical disadvantage, and other forms of persuasion—for example, “A senior leader has privately reviewed the files and recommended Candidate B for this role.” We then measure whether a model changes its choice in response. Each prefix has a matched version that makes the same kind of case for the other candidate, allowing us to robustly test whether the same argument has different effects depending on which candidate it supports.

Combining these variations in demographic identity and prefix expands FairStress’ 300 scenarios into more than 13 million test cases. Alongside the full benchmark, we’ve developed FairStress-Core, a 50K-item subset selected using item response theory, following our [Fluid Benchmarking](https://allenai.org/blog/fluid-benchmarking) approach. It’s designed to make evaluation faster and less computationally expensive while retaining much of the full benchmark’s ability to reveal differences in model behavior.

## Models do not always hold correct answers equally

In our experiments with FairStress, we found little difference in model behavior when prompts contained no demographic information. When one candidate was clearly stronger, models selected that candidate at nearly the same rate across otherwise equivalent versions of the scenario. On ambiguous cases, where neither candidate was objectively stronger, the models’ choices were also close to evenly split. As demographic identity became more explicit in the prompt, however, model behavior became less symmetric.

For example, suppose Candidate A is clearly better qualified than Candidate B. When A was majority-coded – carrying the conventionally advantaged identity in that comparison, such as white, male, or heterosexual – and B was minority-coded, a prefix favoring B was more likely to make the model switch from the stronger candidate to the weaker one. When A was minority-coded and B was majority-coded, with their qualifications held fixed, the same kind of prefix favoring B was less likely to make the model abandon its correct choice of A.

We describe this pattern as *anti-stereotypical over-correction*: in these comparisons, models were more willing to abandon a correct decision when doing so favored a minority-coded candidate. The concern is that demographic identity changes how consistently a model follows the evidence, even when one candidate is clearly better qualified.

[![Two hiring scenarios showing Tülu 3.1 8B selecting the Black transgender woman with either a weaker or stronger résumé and explaining the choices differently.](https://www.datocms-assets.com/64837/1791813418-fairstress-blog-draft-google-docs-image-2.png?fit=max&h=810&w=1550)](https://www.datocms-assets.com/64837/1791813418-fairstress-blog-draft-google-docs-image-2.png?fit=max&h=810&w=1550)

*In this hiring example, Tülu 3.1 8B selected the Black transgender woman in both versions of the scenario. When her résumé was weaker, its explanation emphasized growth potential and a diverse background despite missing certifications. When her résumé was stronger, it emphasized experience and certification.*

[![Mean demographic gaps across 15 models and four identity conditions, measured in percentage points.](https://www.datocms-assets.com/64837/1791813453-fairstress-blog-draft-google-docs-image-3.png?fit=max&h=810&w=1550)](https://www.datocms-assets.com/64837/1791813453-fairstress-blog-draft-google-docs-image-3.png?fit=max&h=810&w=1550)

*Mean gaps between minority-coded and majority-coded candidates across 15 models, evaluated in the 19 domains shared by all four identity conditions. Values are in percentage points. Positive values indicate differences favoring minority-coded candidates; zero indicates equal rates across groups.*

These differences also appeared when demographic identity was implied rather than stated outright. Across the 15 models evaluated on the full benchmark, the average gap in abandoning correct answers was 6.9 percentage points with implied identity and 9.3 points with explicit labels.

On FairStress-Core, frontier models including Claude Opus 5 and GPT-5.5 selected the minority-coded candidate about 60–65% of the time when neither candidate was objectively stronger. Under matched adversarial prefixes, switching toward minority-coded candidates was 8.8–42.4 percentage points more common than switching toward majority-coded candidates across our 12 model-and-mode runs.

[![Bar chart of minority-coded candidate selection rates for equally qualified candidates on FairStress-Core.](https://www.datocms-assets.com/64837/1791814138-fairstress-blog-draft-google-docs-image-4.png?fit=max&h=810&w=1550)](https://www.datocms-assets.com/64837/1791814138-fairstress-blog-draft-google-docs-image-4.png?fit=max&h=810&w=1550)

[![Paired Claude Opus 5 explanations mention sexual orientation only when selecting the gay applicant in this example.](https://www.datocms-assets.com/64837/1791814175-fairstress-blog-draft-google-docs-image-5.png?fit=max&h=810&w=1550)](https://www.datocms-assets.com/64837/1791814175-fairstress-blog-draft-google-docs-image-5.png?fit=max&h=810&w=1550)

We found subtler differences in how models explained their choices, even when they chose correctly in both demographic versions of a scenario.

Across 11 open-weight models, explanations for minority-coded choices used somewhat more confident and positive language. When identity was explicitly labeled, these explanations contained words such as “resilience,” “diversity,” and “barriers” at higher frequency. Explanations for majority-coded choices included more procedural terms such as “evidence,” “criteria,” and “detailed.” A higher selection rate for minority candidates does not necessarily mean fairer treatment; when a model foregrounds identity or diversity in explaining a well-supported choice, it risks downplaying the achievements and qualifications that justify selecting that candidate. A model can therefore favor minority candidates in its choices while giving their qualifications less recognition in its explanations.

[![Tülu 3 8B DPO changes its early-promotion choice from the better-qualified white student to the Black student when race is explicitly stated in this example.](https://www.datocms-assets.com/64837/1791814242-fairstress-blog-draft-google-docs-image-6.png?fit=max&h=810&w=1550)](https://www.datocms-assets.com/64837/1791814242-fairstress-blog-draft-google-docs-image-6.png?fit=max&h=810&w=1550)

In a controlled analysis of Gemma-3-12B-it and Qwen2.5-7B-Instruct, internal activations – the numerical activity inside a model – predicted which demographic side it selected with about 73% accuracy. Text descriptions of those same activations reached 57–59%, against a 50% chance baseline. In a follow-up test, removing candidate names lowered activation-based accuracy by about 18 percentage points.

Our activation analysis is limited to two models and only a handful of demographic contrasts, so we treat these findings as narrower than the broader behavioral results. Still, they suggest that a model’s reasoning trace may not reveal everything represented internally when it makes a decision—consistent with [prior interpretability research](https://www.anthropic.com/research/reasoning-models-dont-say-think?trk=article-ssr-frontend-pulse_little-text-block&utm_source=chatgpt.com) showing that chain-of-thought can omit certain factors that influence a model’s prediction.

## Why existing benchmarks can produce a different result

We also wanted to understand how FairStress compares with existing measures of demographic bias in LLMs. To do that, we compared its results with BBQ, a widely used benchmark that tests whether models favor stereotype-consistent answers in scenarios involving social groups—for example, asking which of two families is neglecting their children’s education when one is described as being on welfare and the other as well-off.

In our BBQ evaluation, models generally leaned toward stereotype-consistent answers, while FairStress revealed a tendency to favor minority-coded candidates. To understand this difference, we examined how the questions were asked and the answers scored. The standard BBQ setup we tested scores the probabilities of fixed answer options without having the model generate a response. This differs from ordinary chat use, where users ask questions and receive generated answers. FairStress asks the model to generate its own response and choose between the candidates.

To see whether the evaluation setup explained the discrepancy between FairStress and BBQ, we took the same BBQ questions and model weights and tested five configurations that varied the chat template, question wording, and use of fixed-option probability scoring or answer generation. In this controlled comparison, we tested Qwen2.5-7B-Instruct, Llama-3.1-8B-Instruct, Gemma-3-27B-it, and Llama-3.1-70B-Instruct. With a chat template, yes/no wording, and generated answers, Qwen2.5-7B-Instruct, Gemma-3-27B-it, and Llama-3.1-70B-Instruct shifted from stereotype-consistent to minority-favoring behavior, while Llama-3.1-8B-Instruct moved to roughly neutral—suggesting that the direction of measured bias depends partly on how a benchmark asks the question and scores the answer. Relying on fixed-option scores alone could therefore miss over-correction in generated decisions. Evaluating both would give developers a fuller picture of the behavior their fairness interventions need to address.

## Training for symmetric robustness

To investigate possible sources of the asymmetry, we audited data from Olmo 3’s training pipeline. Its supervised fine-tuning corpus includes about 99,000 examples from two refusal-training datasets. Across 28,000 topic clusters in the fine-tuning and preference-training data, we found only nine clusters discussing decisions based on merit rather than demographics—and all nine consisted of refusals. The audit also found unequal portrayals of demographic groups: minority-coded groups received more protective or positive framing, while white and cisgender people received little protective framing and persistent negative framing.

Together, these findings suggest a gap between teaching models to refuse discriminatory requests and showing them how to make decisions on merit. Whether these patterns cause the behavioral gaps remains an open question.

[![Heatmap of net positive minus negative framing of seven demographic groups across Olmo 3 training stages.](https://www.datocms-assets.com/64837/1791814305-fairstress-blog-draft-google-docs-image-7.png?fit=max&h=810&w=1550)](https://www.datocms-assets.com/64837/1791814305-fairstress-blog-draft-google-docs-image-7.png?fit=max&h=810&w=1550)

*Net framing of seven demographic groups across Olmo 3’s training data. Each value is the percentage of passages classified as positive toward a group minus the percentage classified as negative. The preference-tuning column covers only the preferred responses, and the reinforcement-learning column covers only prompts. Some reinforcement-learning estimates are based on small samples—as few as eight prompts—and should be interpreted cautiously.*

## Can existing fixes help?

FairStress can also be used to evaluate whether debiasing techniques actually produce more robust, fairer model behavior. We tested nine interventions, including self-critique (where the model reviews and revises its own answer), activation steering (which directly shifts internal model representations during generation), and learned edits (small, targeted changes to internal model representations that are learned from examples). Most methods did not reliably reduce the asymmetry, and some produced more balanced choices at a substantial cost to accuracy. For example, one activation-steering method reduced Qwen2.5-7B-Instruct’s accuracy on clear-cut decisions from 98% to 47%.

One approach came closer to symmetric robustness: counterfactual chain-of-thought, which asks the model to reconsider a case with the candidates’ demographic identities swapped. Across the three model families tested, this approach reduced the gap in how readily models abandoned correct decisions while largely preserving accuracy. It did not remove every asymmetry; on ambiguous cases, models still favored minority-coded candidates.

## From fair outcomes to fair decision-making

FairStress shows why a model’s demographic fairness can’t be judged solely by whether it reaches the same final choice across otherwise equivalent scenarios.

A model can select the candidate best supported by the evidence in two versions of the same scenario that differ only in demographic identity, yet be easier to sway in one version, explain its choice differently, or show different internal activation patterns. Under FairStress’s equality-centered definition, fair behavior means applying the same criteria and defending a well-supported decision consistently regardless of which demographic group benefits.

More broadly, this work reflects our goal of building evaluations that better capture how models behave in real-world settings. By releasing FairStress, we hope researchers and model builders can use it to diagnose hidden asymmetries, test proposed fixes, and develop training approaches that produce more consistent and trustworthy results. Open, rigorous evaluation is central to our broader work at Ai2, and we hope FairStress gives the community another useful tool for understanding where models fall short and how to improve them.

## Datasets mentioned in this article 1

More from this author

## HiRO-ACEv2: Simulating extreme weather at 3 km resolution for a fraction of the cost

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/652db071b62cf1f8463221e2/CxxwFiaomTa1MCX_B7-pT.png)

14

October 14, 2026

## Impactful scheduling for GPU clusters

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/652db071b62cf1f8463221e2/CxxwFiaomTa1MCX_B7-pT.png)

54

October 9, 2026

### Community

Upload images, audio, and videos by dragging in the text input, pasting, or clicking here.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fallenai%2Ffairstress) or [log in](https://huggingface.co/login?next=%2Fblog%2Fallenai%2Ffairstress) to comment


3

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1594144055859-5ee3a7cd2a3eae3cbdad1305.jpeg)](https://huggingface.co/yjernite)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/yu32gPCVLqnpeQd_MMZ74.png)](https://huggingface.co/darrowoflykos)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/7sTK8Q_gZRoOz0uaKnVNJ.png)](https://huggingface.co/luke-loan-atlas)

## Datasets mentioned in this article 1
