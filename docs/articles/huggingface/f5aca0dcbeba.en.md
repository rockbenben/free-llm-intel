---
vendor: huggingface
title: Democratizing AI Safety with RiskRubric.ai
original_title: Democratizing AI Safety with RiskRubric.ai
url: https://huggingface.co/blog/riskrubric
date: 2025-09-18
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 20800936b662
---


# Democratizing AI Safety with RiskRubric.ai

					September 18, 2025

Update on GitHub


21

- [![](https://huggingface.co/avatars/8f3fa0abf9ca323b27950da2c4161e44.svg)](https://huggingface.co/nadavlotan)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64c13ee9e98a5e02c93459ee/o7huQQPXZ5vS8r5RVDvWP.png)](https://huggingface.co/leonardtang)
- [![](https://huggingface.co/avatars/00caacd29818152a2de7cdfdf6f06ce8.svg)](https://huggingface.co/rglauser)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/mPF9iTwFDPVKnoowo_9wn.png)](https://huggingface.co/GalOfer)
- [![](https://huggingface.co/avatars/95ba8fc9c73075d5b4112599cca63ce1.svg)](https://huggingface.co/galmo-noma)
- [![](https://huggingface.co/avatars/725df414d7af56b3c3542a624bad7537.svg)](https://huggingface.co/idolaman)

Gal Moyal

galmo-noma

guest

*Building trust in the open model ecosystem through standardized risk assessment*

More than 500,000 models can be found on the Hugging Face hub, but it’s not always clear to users how to choose the best model for them, notably on the security aspects. Developers might find a model that perfectly fits their use case, but have no systematic way to evaluate its security posture, privacy implications, or potential failure modes.

As models become more powerful and adoption accelerates, we need equally rapid progress in AI safety and security reporting. We're therefore excited to announce [RiskRubric.ai](https://riskrubric.ai/), a novel initiative led by Cloud Security Alliance and [Noma Security](https://noma.security), with contributions by Haize Labs and Harmonic Security, for standardized and transparent risk assessment in the AI model ecosystem.

## Risk Rubric, a new Standardized Assessment of Risk for models

RiskRubric.ai provides **consistent, comparable risk scores across the entire model landscape**, by evaluating models across six pillars: transparency, reliability, security, privacy, safety, and reputation.

The platform's approach aligns perfectly with open-source values: rigorous, transparent, and reproducible. Using Noma Security capabilities to automate the effort, each model undergoes:

- **1,000+ reliability tests** checking consistency and edge case handling
- **200+ adversarial security probes** for jailbreaks and prompt injections
- **Automated code scanning** of model components
- **Comprehensive documentation review** of training data and methods
- **Privacy assessment** including data retention and leakage testing
- **Safety evaluation** through structured harmful content tests

These assessments produce 0-100 scores for each risk pillar, rolling up to clear A-F letter grades. Each evaluation also includes specific vulnerabilities found, recommended mitigations, and suggestions for improvements.

RiskRubric also comes with filters to help developers and organizations make deployment decisions based on what’s important for them. Need a model with strong privacy guarantees for healthcare applications? Filter by privacy scores. Building a customer-facing application requiring consistent outputs? Prioritize reliability ratings.

## What we found (as of September 2025)

Evaluating both open and closed models with the exact same standards highlighted some interesting results: many open models actually outperform their closed counterparts in specific risk dimensions (particularly transparency, where open development practices shine).

Let’s look at general trends:

**Risk distribution is polarized – most models are strong, but mid-tier scores show elevated exposure**

[![total_score](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/riskrubric/RiskRubric.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/riskrubric/RiskRubric.png)

The total risk scores range from 47 to 94, with a median of 81 (on a 100 points). Most models cluster in the “safer” range (54% are A or B level), but a long tail of underperformers drags the average down. That split shows a polarization: models tend to be either well-protected or in the middle-score range, with fewer in between.

The models concentrated in the 50–67 band (C/D range) are not outright broken, but they do provide only medium to low overall protection. This band represents the most practical area of concern, where security gaps are material enough to warrant prioritization.

**What this means:** Don’t assume the “average” model is safe. The tail of weak performers is real – and that’s where attackers will focus. Teams can use composite scores to set a **minimum threshold (e.g. 75)** for procurement or deployment, ensuring outliers don’t slip into production.

**Safety risk is the “swing factor” – but it tracks closely with security posture**

[![safety_histogram](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/riskrubric/Safety.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/riskrubric/Safety.png)

The *Safety & Societal* pillar (e.g. harmful output prevention) shows the widest variation across models. Importantly, models that invest in **security hardening** (prompt injection defenses, policy enforcement) almost always score better on safety as well.

**What this means**: Strengthening core security controls goes beyond preventing jailbreaks, but also directly reduces downstream harms! Safety seems like it is a byproduct of robust security posture.

**Guardrails can erode transparency – unless you design for it**

Stricter protections often make models *less transparent* to end users (e.g. refusals without explanations, hidden boundaries). This can create a trust gap: users may perceive the system as “opaque” even while it’s secure.

**What this means**: Security shouldn’t come at the cost of trust. To balance both, pair strong safeguards with **explanatory refusals, provenance signals, and auditability**. This preserves transparency without loosening defenses.

An updating results sheet can be accessed [here](https://huggingface.co/datasets/nomasecurity/riskrubric-results)

## **Conclusion**

When risk assessments are public and standardized, the entire community can work together to improve model safety. Developers can see exactly where their models need strengthening, and the community can contribute fixes, patches, and safer fine-tuned variants. This creates a virtuous cycle of transparent improvement that's impossible with closed systems. It also helps the community at large understand what works and does not, safety wise, by studying best models.

If you want to take part in this initiative, you can submit your model for evaluation (or suggest existing models!) to understand their risk profile!

We also welcome all feedback on the assessment methodology and scoring framework

## Datasets mentioned in this article 1

### Community

andreywpaddaone

Oct 15, 2025

Really insightful breakdown, Gal, the level of depth and transparency RiskRubric brings is impressive, especially given how fast the open model ecosystem is growing. At Openforge.io we’ve worked with teams navigating healthcare and finance compliance, and the lack of clear security benchmarks for AI models is often a blocker for adoption.

The six-pillar framework feels like a solid step toward building that missing trust layer. Curious, do you see RiskRubric evolving into something that could be integrated into CI/CD pipelines for real-time scoring during development?

- [![](https://huggingface.co/avatars/95ba8fc9c73075d5b4112599cca63ce1.svg)](https://huggingface.co/galmo-noma)


galmo-noma

Article author

Oct 16, 2025

Thanks a lot for the thoughtful comment!
Yes, RiskRubric can absolutely be integrated into CI/CD or model approval workflows. Several companies that have adopted RiskRubric already use it that way: models that achieve a risk score above a defined threshold can be automatically fast-tracked for deployment, while others trigger additional reviews, compensating controls, or specific-use restrictions.
We are also working on additional integrations that would make this easier and more extensible for that use!

We also have an AMA session to connect with the community and answer any further questions - feel free to register and attend!
[https://noma.security/behind-the-riskrubric-ai-algorithm-an-ama-on-transparent-ai-model-risk/](https://noma.security/behind-the-riskrubric-ai-algorithm-an-ama-on-transparent-ai-model-risk/)

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Friskrubric) or [log in](https://huggingface.co/login?next=%2Fblog%2Friskrubric) to comment


21

- [![](https://huggingface.co/avatars/8f3fa0abf9ca323b27950da2c4161e44.svg)](https://huggingface.co/nadavlotan)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64c13ee9e98a5e02c93459ee/o7huQQPXZ5vS8r5RVDvWP.png)](https://huggingface.co/leonardtang)
- [![](https://huggingface.co/avatars/00caacd29818152a2de7cdfdf6f06ce8.svg)](https://huggingface.co/rglauser)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/mPF9iTwFDPVKnoowo_9wn.png)](https://huggingface.co/GalOfer)
- [![](https://huggingface.co/avatars/95ba8fc9c73075d5b4112599cca63ce1.svg)](https://huggingface.co/galmo-noma)
- [![](https://huggingface.co/avatars/725df414d7af56b3c3542a624bad7537.svg)](https://huggingface.co/idolaman)
- [![](https://huggingface.co/avatars/424ea1cb34b28f497e24ba9b99e56893.svg)](https://huggingface.co/nomaor)
- [![](https://huggingface.co/avatars/7b68e250bc25e642d5b0e0699f4133f9.svg)](https://huggingface.co/nadavsenior)
- [![](https://huggingface.co/avatars/02a571bc791b78d3993d9a0484b70a29.svg)](https://huggingface.co/adampo)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/BCQuek0KU8EzRHaj7-yfh.png)](https://huggingface.co/Ogennoma)
- [![](https://huggingface.co/avatars/4e84ac947e91d9b42e5753440e3a90bc.svg)](https://huggingface.co/tralon)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/I4HmR-RvH6Cvd5qQxaPcu.png)](https://huggingface.co/roynoma)

## Datasets mentioned in this article 1
