---
vendor: huggingface
title: Granite 4.0 Nano: Just how small can you go?
original_title: Granite 4.0 Nano: Just how small can you go?
url: https://huggingface.co/blog/ibm-granite/granite-4-nano
date: 2026-09-14
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 692c423cf54b
---


# Granite 4.0 Nano: Just how small can you go?

Enterprise

Article

					October 28, 2025


128

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/65c1173865086cabf46fe1b9/FAv5DpwQ-t9Qqo8936Tp1.jpeg)](https://huggingface.co/ibibrahim)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1655385361868-61b85ce86eb1f2c5e6233736.jpeg)](https://huggingface.co/reach-vb)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1594144055859-5ee3a7cd2a3eae3cbdad1305.jpeg)](https://huggingface.co/yjernite)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6141a88b3a0ec78603c9e784/DJsxSmWV39M33JFheLobC.jpeg)](https://huggingface.co/merve)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1627505688463-60107b385ac3e86b3ea4fc34.jpeg)](https://huggingface.co/davanstrien)
- [![](https://huggingface.co/avatars/0cf4c75a0531f337f0b3319faced4f65.svg)](https://huggingface.co/emmagauthier)

Kate Soule

katesoule

ibm-granite

Rameswar Panda

rpand002

ibm-granite

Today we are excited to share [Granite 4.0 Nano](https://huggingface.co/collections/ibm-granite/granite-40-nano-language-models), our smallest models yet, released as part of IBM's Granite 4.0 model family. Designed for the edge and on-device applications, these models demonstrate excellent performance for their size and represent IBM's continued commitment to develop powerful, useful, models that don't require hundreds of billions of parameters to get the job done.

Like all [Granite 4.0 models](https://huggingface.co/collections/ibm-granite/granite-40-language-models), the Nano models are released under an Apache 2.0 license with native architecture support on popular runtimes like vLLM, llama.cpp, and MLX. The models were trained with the same improved training methodologies, pipelines, and over 15T tokens of training data developed for the original Granite 4.0 models. This release includes variants benefiting from the Granite 4.0’s [new, efficient hybrid architecture](https://www.ibm.com/new/announcements/ibm-granite-4-0-hyper-efficient-high-performance-hybrid-models#The+Granite+4+architecture), and like all Granite language models, the Granite 4.0 Nano models also carry with them IBM's [ISO 42001 certification](https://www.ibm.com/new/announcements/ibm-granite-iso-42001) for responsible model development, giving users added confidence that models are built and governed to global standards.

Specifically, Granite 4.0 Nano comprises of 4 instruct models and their base model counterparts:

- **Granite 4.0 H 1B** – A ~1.5B parameter, dense LLM featuring a hybrid-SSM based architecture.
- **Granite 4.0 H 350M** – A ~350M parameter, dense LLM featuring a hybrid-SSM based architecture.
- **Granite 4.0 1B and Granite 4.0 350M** – Alternative traditional transformer versions of our 1B and 350M Nano models, designed to enable workloads where hybrid architectures may not yet have optimized support (e.g. Llama.cpp).

Building sub-billion to ~1 billion parameter models is an active and competitive space, with advancements in performance and architectures recently made by a number of model developers such as Alibaba (Qwen), LiquidAI (LFM), Google (Gemma) and others. When compared to these other models, Granite 4.0 Nano models demonstrate a significant increase in capabilities that can be achieved with a minimal parameter footprint, as measured by a series of general benchmarks across General Knowledge, Math, Code, and Safety domains.

[![granite-4-nano-chart1](https://cdn-uploads.huggingface.co/production/uploads/65c1173865086cabf46fe1b9/vx93cgRtkLdDvirdCGF18.png)](https://cdn-uploads.huggingface.co/production/uploads/65c1173865086cabf46fe1b9/vx93cgRtkLdDvirdCGF18.png) *Chart 1. Average accuracy of 0.2B–2B parameter models across Knowledge, Math, Code, and Safety benchmarks. See Appendix I for full details.*

In addition to more general benchmarks, Granite Nano models outperformed several similarly sized models on tasks critical for agentic workflows, including instruction following and tool calling, as measured by IFEval and Berkley's Function Calling Leaderboard v3 (BFCLv3) benchmarks.

[![granite-4-nano-chart2](https://cdn-uploads.huggingface.co/production/uploads/65c1173865086cabf46fe1b9/Xzmabcv6MzAvGapHFhXg4.png)](https://cdn-uploads.huggingface.co/production/uploads/65c1173865086cabf46fe1b9/Xzmabcv6MzAvGapHFhXg4.png) *Chart 2. Accuracy on IFEval and BFCLv3 benchmarks.*

Full details of the Granite 4.0 Nano can be found on the [Hugging Face model cards](https://huggingface.co/collections/ibm-granite/granite-40-nano-language-models). Moving forward, expect to see more releases from IBM as we continue to grow the Granite 4.0 family and work to make AI a more efficient and effective tool for developers.

*Appendix I. Breakdown of General Performance Benchmarks* [![granite-4-nano-chart3](https://cdn-uploads.huggingface.co/production/uploads/65c1173865086cabf46fe1b9/8fdBK5XHiGvsaEkvqzLq4.png)](https://cdn-uploads.huggingface.co/production/uploads/65c1173865086cabf46fe1b9/8fdBK5XHiGvsaEkvqzLq4.png)

## Collections mentioned in this article 2

More from this author

## Granite 4.2 LLMs: How They're Built

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/639bcaa2445b133a4e942436/CEW-OjXkRkDNmTxSu8Egh.png)

128

August 25, 2026

## Extremely Fast and Accurate Transcription with Granite Speech 5.0 Turbo CTC

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/639bcaa2445b133a4e942436/CEW-OjXkRkDNmTxSu8Egh.png)

36

August 25, 2026

### Community

saharadesertfox

Oct 28, 2025


edited Oct 28, 2025

No description provided.

paladin1

Oct 29, 2025

❤️💪🥹

wissam6

Oct 29, 2025

👏👏

kmehant

Oct 29, 2025

👏

clem

Oct 29, 2025

very cool!

LocPilot

Oct 30, 2025

We just tested local granite-4-h-tiny model for contract analysis in Word: [https://youtu.be/acX1CqF8TDA](https://youtu.be/acX1CqF8TDA)

It's impressive. We plan to give nano a try soon.

xtolxy1

Nov 3, 2025

salom

xtolxy1

Nov 3, 2025

salom
[![1762166798800.Screenshot_20251103-154413](https://cdn-uploads.huggingface.co/production/uploads/687b180808e6c4ce0b4b50f9/tARVQzN2t9UyZ4PEHSNkg.jpeg)](https://cdn-uploads.huggingface.co/production/uploads/687b180808e6c4ce0b4b50f9/tARVQzN2t9UyZ4PEHSNkg.jpeg)

agentlans

Nov 14, 2025

The whole Granite series is underrated. I've been training the Granite 3 and 4 small models and they learn very quickly. They're my go-to models for specialized tasks.

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fibm-granite%2Fgranite-4-nano) or [log in](https://huggingface.co/login?next=%2Fblog%2Fibm-granite%2Fgranite-4-nano) to comment


128

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/65c1173865086cabf46fe1b9/FAv5DpwQ-t9Qqo8936Tp1.jpeg)](https://huggingface.co/ibibrahim)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1655385361868-61b85ce86eb1f2c5e6233736.jpeg)](https://huggingface.co/reach-vb)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1594144055859-5ee3a7cd2a3eae3cbdad1305.jpeg)](https://huggingface.co/yjernite)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6141a88b3a0ec78603c9e784/DJsxSmWV39M33JFheLobC.jpeg)](https://huggingface.co/merve)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1627505688463-60107b385ac3e86b3ea4fc34.jpeg)](https://huggingface.co/davanstrien)
- [![](https://huggingface.co/avatars/0cf4c75a0531f337f0b3319faced4f65.svg)](https://huggingface.co/emmagauthier)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6422eab8e2029ade06eeee2c/Gai3BHr2WJ0YuhdumqQ_z.png)](https://huggingface.co/MElHuseyni)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64319ed9034ecbefddd4f46f/PnglqSRCJFT7xM1pP3XnO.png)](https://huggingface.co/gheorgheiuga)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/639582473d9ac9664fd436f5/yWH354yTLKVchFD2N498z.jpeg)](https://huggingface.co/ashish23)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63b7e09359060ca9f4c4de35/0PH1dWNfcXTQ9H0QAeD91.jpeg)](https://huggingface.co/Avihu)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/5f106ce5348d4c7346cd19ab/Uu08yZZlFuj3dtG4wld3n.jpeg)](https://huggingface.co/abdullah)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/630b4269e67c604e9b7a429c/qsmA2ObMFfLwPIAyveo9F.jpeg)](https://huggingface.co/sroecker)

## Collections mentioned in this article 2
