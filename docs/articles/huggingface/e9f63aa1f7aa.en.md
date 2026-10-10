---
vendor: huggingface
title: How UK AISI and EvalEval Are Making Benchmark Results Reproducible
original_title: How UK AISI and EvalEval Are Making Benchmark Results Reproducible
url: https://huggingface.co/blog/evaleval-aisi
date: 2026-09-28
lang: en
captured: 2026-10-10
extractor: readability-v1
status: ok
body_sha: 4564444a75d7
---


# How UK AISI and EvalEval Are Making Benchmark Results Reproducible

					September 22, 2026

Update on GitHub


28

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6413251362e6057cbb6259bd/k8UMg_tnorG_uCXidybZ7.jpeg)](https://huggingface.co/evijit)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/vnmbzcTMfdqnuzbONym__.png)](https://huggingface.co/dariocava)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1583857146757-5e67bdd61009063689407479.jpeg)](https://huggingface.co/clem)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1594144055859-5ee3a7cd2a3eae3cbdad1305.jpeg)](https://huggingface.co/yjernite)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/66e691d778f2c37966d1d614/1MJg4zMGny3kmC5TPdjN3.png)](https://huggingface.co/DVRRK)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/69d94b034b0d592e906bc968/8HDc1xHMRnIlqJDI6CG_4.jpeg)](https://huggingface.co/vzn2auto)

Avijit Ghosh

evijit

evaleval

Jenny Chim

j-chim

evaleval

Deep Joshi

deeplumiere

evaleval

Srishti

srishtiy

evaleval

Matt Kennedy

wmmkennedy

evaleval

Irene Solaiman

irenesolaiman

evaleval

Jessica McFadyen

mcfadyen-aisi

ai-safety-institute

Lynn Tan

lynn-aisi

ai-safety-institute

Coz

coz-aisi

ai-safety-institute

The [EvalEval Coalition](https://evalevalai.com/) is thrilled to share that the [UK AI Security Institute (AISI)](https://www.aisi.gov.uk/) is using EvalEval's infrastructure to openly share evaluation results, supporting more reproducible and verifiable evaluation science.

AISI and EvalEval have previously collaborated on research that began at a [joint workshop alongside NeurIPS 2025](https://evalevalai.com/events/workshop-2025/), and feedback from the Institute has helped shape the [Every Eval Ever (EEE) schema](https://evalevalai.com/projects/every-eval-ever/). This next phase of the collaboration puts that shared infrastructure into practice.

## Why reproducible evaluation reporting matters

As AI deployment accelerates, evaluations are becoming increasingly important sources of evidence about model and system performance. Yet results are reported across many formats, platforms, and outlets, often without enough information to reproduce them. Running the evaluations again may itself be prohibitively expensive.

EvalEval's mission is to improve this ecosystem through a shared reporting schema, [Every Eval Ever](https://evalevalai.com/projects/every-eval-ever/), and an open platform, [Evaluation Cards](https://evalcards.evalevalai.com/), that brings evaluation results and the information needed to interpret them into a common structure.

This builds naturally on AISI's work to make evaluation more efficient through [OptStop](https://arxiv.org/abs/2608.14425), more statistically rigorous through [HiBayES](https://www.aisi.gov.uk/blog/hibayes-improving-llm-evaluation-with-hierarchical-bayesian-modelling), and more standardised in areas including transcript analysis and capability elicitation. Together, AISI and EvalEval are working to diagnose gaps in evaluation reporting and build shared infrastructure to close them.

## What AISI is sharing

Transcript-level transparency matters not only for reproducibility, but also for analysis and diagnosis. In this new phase of the collaboration, AISI is making publicly reported evaluation methods and findings available through Evaluation Cards where appropriate. The release includes verified results, context, and configuration information for the five benchmarks in the paper's main experiment:

- HealthBench
- FrontierMath
- Humanity's Last Exam
- SWE-Bench Pro
- Terminal-Bench 2.0

These results cover six frontier models: Claude Opus 4, Claude Opus 4.5, Claude Opus 4.6, GPT-5, GPT-5.2, and GPT-5.4. The release also includes results from two related cyber evaluations—Cyber CTFs and The Last Ones—which use a different, partially overlapping set of models. The data accompany AISI's paper, [*How Inference Compute Shapes Frontier LLM Evaluation*](https://arxiv.org/abs/2606.17930), which studies how benchmark performance depends on inference-time compute and evaluation protocol.

*Performance on Humanity's Last Exam changes with evaluation protocol and inference compute. Each curve shows the cumulative share of attempted tasks solved within a given token count, using the earliest observed success per task. When models received correctness feedback from an oracle after each attempt, they continued to solve additional tasks as token use increased.*

When results are openly released with setup information, researchers and practitioners can examine individual studies more closely and compare findings across the wider ecosystem. Where other reports lack these details, releases like AISI's provide verified reference points for interpreting evaluations in context—for example, by helping researchers understand how setup choices may influence reported performance. As more evaluators adopt EEE, open comparisons like these can support broader and more reliable meta-research.

*AISI's Terminal-Bench 2.0 results alongside other reported evaluations for the same models, under different evaluation setups.*

We are excited about this adoption and look forward to further standardising and sharing evaluations with AISI and other AI evaluation organisations.

## Contribute to the shared mission

- **Model developers:** [Report verified evaluation results](https://evalcards.evalevalai.com/help/get-verified).
- **Evaluation developers:** Report benchmarks and run data using the [Every Eval Ever schema](https://github.com/evaleval/every_eval_ever).
- **Evaluation, governance, and policy researchers:** [Explore Evaluation Cards](https://evalcards.evalevalai.com/) by benchmark or model, or use it to examine the state of evaluation reporting as a whole.

## About the EvalEval Coalition

The EvalEval Coalition is a research community developing scientifically grounded research and robust deployment infrastructure for the evaluation ecosystem. Its goal is to improve evaluation science, address the lack of consensus around documenting evaluation applicability and utility, and broaden coverage of the impacts that matter for scientific research and policy analysis.

The coalition's flagship projects include [Every Eval Ever](https://evalevalai.com/projects/every-eval-ever/), a shared schema and repository for evaluation results, and [Evaluation Cards](https://evalevalai.com/projects/eval-cards/), which combines benchmark metadata, evaluation-run data, and model metadata into interpretable records. Together, they make it easier to understand when apparently similar scores were produced under meaningfully different conditions.

## About the UK AI Security Institute

The [UK AI Security Institute](https://www.aisi.gov.uk/) is a research organisation within the UK government's Department for Science, Innovation and Technology. Its mission is to equip governments with a scientific understanding of the risks posed by advanced AI. AISI conducts research and builds infrastructure to understand advanced AI capabilities and impacts, develop and test mitigations, and inform policy.

## Further reading

- [*How Inference Compute Shapes Frontier LLM Evaluation*](https://arxiv.org/abs/2606.17930)
- [HiBayES: Improving LLM evaluation with hierarchical Bayesian modelling](https://www.aisi.gov.uk/blog/hibayes-improving-llm-evaluation-with-hierarchical-bayesian-modelling)
- [HiBayES paper](https://arxiv.org/abs/2505.05602)
- [OptStop paper](https://arxiv.org/abs/2608.14425)
- [Every Eval Ever](https://evalevalai.com/projects/every-eval-ever/)
- [Evaluation Cards](https://evalcards.evalevalai.com/)

More Articles from our Blog

evaluation

community

leaderboard

## Featuring Every Eval Ever Results on Hugging Face Model Pages

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6238f87f35384c2bcccb3889/vvQDZb934B36xPt_Gokjh.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6413251362e6057cbb6259bd/k8UMg_tnorG_uCXidybZ7.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1678663263366-63e0eea7af523c37e5a77966.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/67c7276e0c51bafa5ee8e033/yBl9QsWcQp4XtqUj4Ni_0.jpeg)
- +3

54

June 30, 2026

nlp

evaluation

retrieval

## Introducing RTEB: A New Standard for Retrieval Evaluation

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/61f33092a92c9a858b654991/jFRUSeZ6DnI27dlCAQRHq.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/5ff5943752c26e9bc240bada/Exyzf3C_gJ2KdsL4K5_cq.png)
- ![](https://huggingface.co/avatars/7a4067accdd1005f78c3c4adad3ee0a5.svg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/64cc0e80a257a3212c0c4b24/wqs6WZN8-3OQthcnQXgN7.png)
- +2

149

October 1, 2025

### Community

Nomad-link-id

11 days ago

The line that matters for practitioners is quiet: apparently similar scores can be produced under meaningfully different conditions.

Once you've watched a benchmark move just by changing inference-time compute or the elicitation protocol, "Model A beat Model B on X" without a card is marketing, not comparison. Evaluation Cards that ship verified results *with* configuration — especially transcript-level context where it's appropriate — are how eval becomes a contract instead of a leaderboard screenshot.

One ask I'd put to teams adopting EEE: which fields get skipped first under deadline pressure (seed, tool access, attempt budget, oracle feedback), and do you treat a missing field as "do not cite the delta" rather than "assume defaults"?

Reproducible reporting won't remove disagreement. It will make the disagreement about the right variables.

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fevaleval-aisi) or [log in](https://huggingface.co/login?next=%2Fblog%2Fevaleval-aisi) to comment


28

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6413251362e6057cbb6259bd/k8UMg_tnorG_uCXidybZ7.jpeg)](https://huggingface.co/evijit)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/vnmbzcTMfdqnuzbONym__.png)](https://huggingface.co/dariocava)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1583857146757-5e67bdd61009063689407479.jpeg)](https://huggingface.co/clem)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1594144055859-5ee3a7cd2a3eae3cbdad1305.jpeg)](https://huggingface.co/yjernite)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/66e691d778f2c37966d1d614/1MJg4zMGny3kmC5TPdjN3.png)](https://huggingface.co/DVRRK)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/69d94b034b0d592e906bc968/8HDc1xHMRnIlqJDI6CG_4.jpeg)](https://huggingface.co/vzn2auto)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/01iAmRqyak7mlJT6EDgxJ.png)](https://huggingface.co/MikeEliteLLM)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/62543749b777cd32720675c2/EF_KRZO4hTo8TWXOtvc-n.png)](https://huggingface.co/irenesolaiman)
- [![](https://huggingface.co/avatars/89ddd33671ed6f23c8b9c33f0674033b.svg)](https://huggingface.co/Jureko11)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/IWp7GmKqFXZxE8LB2nADg.png)](https://huggingface.co/birkanoge)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64a99fe3e831371424f583b9/dhKFIea8_zxhLnc2DVQuU.png)](https://huggingface.co/enixmeng)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/7sTK8Q_gZRoOz0uaKnVNJ.png)](https://huggingface.co/luke-loan-atlas)
