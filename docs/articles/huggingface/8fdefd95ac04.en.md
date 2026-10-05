---
vendor: huggingface
title: The Open Arabic LLM Leaderboard 2
original_title: The Open Arabic LLM Leaderboard 2
url: https://huggingface.co/blog/leaderboard-arabic-v2
date: 2024-08-27
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 6fe239ff1236
---

Back to Articles

# The Open Arabic LLM Leaderboard 2

Published
					February 10, 2025

Update on GitHub

Upvote

39

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6740a691ddc2c8e208a41102/Lt-aqBhzx-tQ58kFlSPjp.jpeg)](https://huggingface.co/robb-0)
- [![](https://huggingface.co/avatars/eccc801aa993bd11486c68422b6a5071.svg)](https://huggingface.co/hassanraha)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/626237d9bbcbd1c34f1bb231/EJrOjvAL-68qMCYdnvOrq.png)](https://huggingface.co/alielfilali01)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/60420dccc15e823a685f2b03/AOApMWt_jvm9e6XQ2vlrJ.jpeg)](https://huggingface.co/dvilasuero)
- [![](https://huggingface.co/avatars/66b0d4461fe6ae8b24494e1461231e02.svg)](https://huggingface.co/tarickMorty)
- [![](https://huggingface.co/avatars/598ecc79af157308a031693aec53dcf2.svg)](https://huggingface.co/basma-b)

Ali El Filali

alielfilali01

2A2I

Manel ALOUI

Manel-Hik

OALL

Tarique Husaain

tarickMorty

AI71ai

Ahmed Alzubaidi

amztheory

tiiuae

Basma Boussaha

basma-b

tiiuae

Ruxandra Cojocaru

rcojocaru

tiiuae

Hakim Hacid

HakimHacid

tiiuae

Clémentine Fourrier

clefourrier

## Current status of Arabic LLMs leaderboards

The growing availability of LLMs supporting Arabic, both as monolingual and multilingual models, prompted the community to create dedicated Arabic language leaderboards. Previously, Arabic-focused leaderboards were typically confined to narrow benchmarks introduced by specific authors, often as demos for their work. In these cases, the authors would set up leaderboards to demonstrate how models performed on a particular task or dataset. Alternatively, other leaderboards required users to run evaluations on their own computing resources and then submit a JSON file containing their results for display.

While these approaches helped spark initial interest in Arabic benchmarking, they also introduced several challenges:

- **Resource Limitations**: Many community members lack access to the substantial computational resources needed to evaluate all available open-source models in order to establish which model would be best for their downstream project or application, being forced to rely only on the results shared by model makers in their documentation, which many times does not allow for a direct comparison. This high cost in both time and compute power can become a major barrier to participation in further developing Arabic LLMs, making a leaderboard a valuable shared resource.
- **Integrity of Reported Results**: Because some platforms required users to evaluate their models independently and then simply submit a file of scores, there was no robust mechanism to ensure those results were accurate or even produced through a genuine evaluation. This lack of centralized verification could potentially undermine the credibility and fairness of the leaderboard.

These limitations underscore the need for a more unified, accessible, and transparent benchmarking platform—one that not only enables but encourages genuine and reproducible experimentation for the entire Arabic NLP community. To address these issues, in May 2024, 2A2I, TII, and HuggingFace launched the first version of the [Open Arabic LLM Leaderboard - OALL](https://huggingface.co/blog/leaderboard-arabic) [1], featuring 14 benchmarks across a wide range of tasks including reading comprehension, sentiment analysis, and question answering among others.

In September 2024, a collaboration between SDAIA and the King Salman Global Academy for Arabic Language introduced the [Balsam Index](https://benchmarks.ksaa.gov.sa/b/balsam), which includes approximately 1,400 datasets with 50,000 questions covering 67 tasks, such as grammar correction, paraphrasing, cause-and-effect classification, and text comprehension ... etc.

Later that year, on December 5th, Inception and MBZUAI announced the [AraGen Leaderboard](https://huggingface.co/blog/leaderboard-3c3h-aragen), the first generative tasks leaderboard for Arabic, introducing the 3C3H evaluation metric, which uses dynamic evaluation cycles with private test, and provides a native-Arabic and culturally-aware generative tasks dataset, AraGen Bench, to assess LLMs across four main tasks.

And to end the year strong, on 19th of December 2024, Scale's Safety, Evaluations, and Alignment Lab (SEAL) published an [Arabic leaderboard](https://scale.com/leaderboard/arabic) as part of their multilingual leaderboards. The benchmark empowering this leaderboard remains always private like all the other languages within their family of leaderboards, and relies on human-preference evaluation, using a dataset of 1,000 Arabic prompts designed to enhance chatbot interaction capabilities across complex and culturally nuanced conversations.

## Impact of the previous leaderboard

In less than 7 months after its launch, the first version of the Open Arabic LLM Leaderboard quickly became a vital platform for the Arabic AI community, attracting over 46,000 visitors and more than 2,000 visits in the past month (January 2025). The HuggingFace space received over 100 likes and 8 citations on Google Scholar. The community submitted more than 700 models, ranging from 1B to over 70B parameters. The submitted models originate from more than 180 unique organizations making it one of the most active LLM evaluation leaderboards. Since its launch, the leaderboard sparked numerous engaging discussions across social media, HuggingFace, Reddit, making it the most prominent Arabic leaderboard to date.

As depicted in Figure 1, among the ~700 models submitted to the initial version of the leaderboard, the majority are chat and finetuned models, comprising over 70%, whereas pretrained models constitute only 11%. In terms of model size, more than 50% of the models are smaller than 7B parameters.

![](https://raw.githubusercontent.com/alielfilali01/OALL-assets/refs/heads/main/v2-blog-plots/piechart_requests.png)

Figure 1: Distribution of model types and size.

We omit the count for unknown model type ('?') as this represented only 0.12% of total requests.

Compared to leaderboards for other languages and as shown in Figure 2, the Open Arabic LLM leaderboard stands out as one of the most active, following closely behind the [Korean](https://huggingface.co/spaces/upstage/open-ko-llm-Leaderboard), [Polish](https://huggingface.co/spaces/speakleash/open_pl_llm_Leaderboard), and [Portuguese](https://huggingface.co/spaces/eduagarcia/open_pt_llm_Leaderboard) leaderboards, all within less than a year of its launch. Considering that Arabic is one of the most spoken languages globally, yet has relatively limited content available on the internet, these figures carry even greater significance compared to other languages.

![](https://raw.githubusercontent.com/alielfilali01/OALL-assets/refs/heads/main/v2-blog-plots/leaderboard_comparison_sort_uptime.png)

Figure 2: Number of evaluated models versus uptime in months for different MCQ leaderboards hosted on huggingface.

Data collected prior to January 13, 2025. Languages covered:

Arabic

,

Chinese-China

,

Chinese-Taiwan

,

Czech

,

Dutch

,

French

,

Hebrew

,

Icelandic

,

Italian

,

Japanese

,

Korean (v2)

,

Malay

,

Persian

,

Polish

,

Portuguese

,

Spanish

,

Turkish

.

## Why do we need a new leaderboard?

Recent discussions within the community, including critiques of the Open Arabic LLM Leaderboard (OALL) and similar initiatives, [have highlighted key shortcomings in current benchmarking practices](https://arxiv.org/abs/2409.12623v2) [2]. Many researchers, developers, and language enthusiasts have emphasized the need for more direct evaluations of Arabic-specific tasks, increased transparency in how benchmarks are created, and the inclusion of more diverse datasets that reflect the breadth of Arabic dialects, domains, and real-world applications. These insights have played a central role in shaping the updated leaderboard.

The Arabic language presents unique challenges and characteristics that require specialized evaluation beyond what general NLP tasks can capture. These include intricate grammar, rich and complex morphology, the diversity of spoken dialects, and culturally nuanced safety-related considerations. A leaderboard that addresses these factors can provide a clearer picture of how well models perform in real-world Arabic language contexts.

In the first iteration of OALL, a large portion of datasets and tasks originated from non-Arabic-speaking contexts. When adapted to Arabic, these tasks often failed to reflect real-world use cases or meet the practical needs of Arabic-speaking communities. Many tasks were direct translations from English, which frequently introduced linguistic and contextual mismatches. This approach overlooked Arabic’s unique morphological and syntactic complexities, making the tasks less effective in measuring true language understanding and modeling capabilities.

Additionally, some benchmarks from the first version of OALL became less effective over time as models achieved near-perfect scores, limiting their ability to differentiate incremental improvements. In response, the new leaderboard replaces these saturated benchmarks, introducing a more relevant and up-to-date suite of evaluation tasks.

To address these gaps, the new leaderboard incorporates tasks that are natively developed in Arabic. These tasks are designed to capture the language’s distinctive features—such as its rich morphology, subtle syntax, and context-specific usage—elements that are often lost in translation-based benchmarks. This shift ensures that evaluations are more authentic and better aligned with the realities of Arabic language use.

Furthermore, we identified a silent bug in one of the main tasks, AlGhafa, which inadvertently impacted model rankings. The issue stemmed from a mismatch in how answer choices were checked—rather than verifying their indices, the task evaluated responses based on the choices themselves. While this was not entirely incorrect, it affected small/weak models disproportionately. Some models experienced score drops of up to 20 points, while stronger models remained relatively unaffected. This issue compromised the consistency, fairness and uniformity of the evaluations.

## What's new in this version?

In reforming the leaderboard, we follow two guiding principles: remove saturated and machine translated tasks, due to inherent lower quality and possible cultural bias, and add newly available high quality native or human curated benchmarks to increase the coverage of the evaluation.

From the first version of the Open Arabic LLM Leaderboard (OALL), we keep the following benchmark datasets:

- [AlGhafa benchmark](https://gitlab.com/tiiuae/alghafa) [3]: from the original benchmark released by TII, we keep only the native Arabic datasets, namely the human-curated versions of Facts-Balanced, SOCAL, XGLUE, Sentiment, Sentiment-Rating, Sentiment-Rating-No-Neutral, the two Arabic tasks from [Meta's Belebele](https://huggingface.co/datasets/facebook/belebele) [4] (Arabic-MSA and Arabic-Dialects), and finally the [Arabic EXAMS benchmarks]() [5].

We enrich the leaderboard by adding the following datasets, released in the past year:

- [Native Arabic MMLU](https://huggingface.co/datasets/MBZUAI/ArabicMMLU) [6]: a native Arabic benchmark released by MBZUAI and inspired by the original English MMLU dataset; consists of 40 tasks and almost 15,000 multiple-choice questions in Modern Standard Arabic (MSA), sourced from school exams.
- Human Translated MMLU (MMLU-HT) [7]: a human translation of the original English MMLU dataset containing 57 tasks, curated by Inception as part of the JAIS project, and published under the MBZUAI HF Organization.
- [MedinaQA](https://huggingface.co/datasets/MBZUAI/MadinahQA): released by MBZUAI in order to foster the adoption of more native Arabic benchmarks. This dataset focuses on general Arabic language and grammar aspects.
- [AraTrust](https://huggingface.co/datasets/asas-ai/AraTrust) [8]: a dataset comprising of 522 human-written multiple-choice questions covering different aspects related to safety and truthfulness.

Finally, we introduce the **ALRAGE** benchmark: Arabic Language Retrieval Augmented Generation Evaluation. It introduces a comprehensive framework for evaluating Large Language Models' retrieval-augmented generation capabilities in Arabic. Built upon a meticulously curated [dataset](https://huggingface.co/datasets/OALL/ALRAGE) sourced from 40 Arabic books spanning diverse topics, from Arts & Literature to Technology & Innovation, the benchmark was created using meta-llama/Meta-Llama-3.1-70B for synthetic generation and validated by native Arabic speakers with a [community sprint](https://huggingface.co/spaces/OALL/alrage-sprint-progress) with Argilla. The dataset structure includes questions, ground-truth answers, candidate contexts retrieved through the BAAI/bge-m3 embedding model, and target candidate indices, all designed to authentically simulate real-world RAG scenarios in Arabic.

The innovative aspect of ALRAGE lies in its evaluation methodology, which implements a LLM-as-judge metric within the lighteval framework. Using Qwen2.5-72B-Instruct as the judge model, the system evaluates generated responses through a structured Arabic prompt that compares the model's output against gold answers. The evaluation employs a nuanced 0-10 scoring rubric that assesses answer accuracy, relevance, and quality, with scores normalized to a 0-1 range for standardization. This technical implementation, manifested through a custom JudgeMetricWrapper class, provides a rigorous, reproducible method for evaluating Arabic language generation while maintaining sensitivity to Arabic linguistic nuances, effectively addressing the critical need for sophisticated evaluation metrics in Arabic NLP.

Table 1 summarizes the datasets kept from the first version of the leaderboard as well as the new datasets introduced in this second version.

| **Datasets kept from OALL v1** | **Datasets added for OALL v2** |
| --- | --- |
| AlGhafa (6 tasks) | Native Arabic MMLU (40 tasks) |
| EXAMS | Human Translated MMLU (57 tasks) |
| Belebele (2 tasks) | MedinaQA |
|  | AraTrust |
|  | ALRAGE |

Besides adding and removing datasets, we fixed multiple issues related to the UI and its filters, and we also introduced chat templates. In terms of user submissions, now the number of submissions is limited to 5 per organization per week. This limitation is meant to limit the usage of the leaderboard and give the chance to varied organizations to have their models evaluated. NOTE that for the models submitted by OALL's team to v2, if chat template is found in the config, it is used for the evaluation. Otherwise, chat template is disabled.

## Results from v1 and v2

To assess the impact of the second iteration of the Open Arabic LLM Leaderboard, we conducted a series of statistical comparisons between the two versions.

Figure 3 displays the performance scores across six benchmarks for Versions 1 and 2. Notably, ACVA and Toxigen demonstrate saturation effects at various model sizes. Alghafa in Version 1 exhibits lower saturation, which we hypothesize is due to the inclusion of both native and translated Arabic benchmarks. In contrast, the models' performance for AraTrust, ALRAGE, and Alghafa form v2 is more dispersed with respect to model size.

![](https://raw.githubusercontent.com/alielfilali01/OALL-assets/refs/heads/main/v2-blog-plots/task_comparison_pretrained_only.png)

Figure 3: Comparing the behavior of removed/kept/added tasks between the two version of the Open Arabic LLM Leaderboard.

To examine the correlation between OALL and other Arabic LLM leaderboards, we compared the relative rankings of five open Arabic LLMs: [google/gemma-2-27b-it](https://huggingface.co/google/gemma-2-27b-it), [CohereForAI/aya-23-35B](https://huggingface.co/CohereForAI/aya-23-35B), [CohereForAI/aya-expanse-32b](https://huggingface.co/CohereForAI/aya-expanse-32b), [inceptionai/jais-adapted-70b-chat](https://huggingface.co/inceptionai/jais-adapted-70b-chat), and [meta-llama/Llama-3.3-70B-Instruct](https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct), across three leaderboards: OALL v2, SEAL Arabic, and AraGen. As illustrated in Figure 4, a correlation between the leaderboards is notable, with the Llama3.3-70-instruct model ranking first on both OALL v2 and AraGen, and third on SEAL. *As a clarification, AraGen currently only features the scores for [inceptionai/jais-adapted-70b-chat](https://huggingface.co/inceptionai/jais-adapted-70b-chat), and the Arabic SEAL leaderboard only includes Jais Adapted 70B, so presumably the pretrained model. As we could not fully solve this discrepancy, we decided to evaluate [inceptionai/jais-adapted-70b-chat](https://huggingface.co/inceptionai/jais-adapted-70b-chat) on OALL v2 for this comparison.

![](https://raw.githubusercontent.com/alielfilali01/OALL-assets/refs/heads/main/v2-blog-plots/different_leaderboards_comparison_public_models_by_rank.png)

Figure 4: Comparing the relative ranking of five open models on the second edition of the Open Arabic LLM Leaderboard with the AraGen and SEAL-Arabic leaderboards. Data retrieved on 29 January 2025.

To further explore the differences between the two versions of OALL, we present in Figure 5 the top models across two categories: pretrained and chat. For models submitted to OALL v1, Qwen2.5 establishes itself as a strong baseline for Arabic in all categories, particularly for pretrained models. In OALL v2, Qwen models also dominate the pretrained models category, however the Qwen/Qwen2-72B model surpasses Qwen/Qwen2.5-72B as the best pretrained/continually pretrained model, and Llama3.3-70B-instruct emerges as the leader in all categories, surpassing calme-2.1-qwen2.5-72b in performance. Overall, some model rankings have shifted in v2, while others have remained consistent. We attribute these changes to two key factors: first, the robustness of models with respect to Arabic-native benchmarks, safety, and trustworthiness; and second, the evaluation of over 700 models in OALL v1 compared to 80 models in v2, including a few recent models that might not be present in v1. We anticipate that the community will contribute to expanding the leaderboard following its release.

![](https://raw.githubusercontent.com/alielfilali01/OALL-assets/refs/heads/main/v2-blog-plots/best_pretrained_by_range.png) ![](https://raw.githubusercontent.com/alielfilali01/OALL-assets/refs/heads/main/v2-blog-plots/best_chat_by_range.png)

Figure 5: Comparison between best pretrained/continuously pretrained model for each model size range.

Finally, we analyzed the average scores on OALL v1 and v2 for two model families: AceGPT and Jais. As depicted in Figure 6, the trend is consistent across both versions: larger models tend to achieve higher average scores, with the exception of inceptionai/jais-family-30b-8k, that surpasses the larger inceptionai/jais-adapted-70b model on OALL v2. Overall, the average scores in v2 are higher than in v1, except for the 7B models in both families. We hypothesize that this discrepancy is due to the lower performance of smaller models on ALRAGE, as it is a generative task, which typically favors larger models.

![](https://raw.githubusercontent.com/alielfilali01/OALL-assets/refs/heads/main/v2-blog-plots/reference_models_pretrained_by_range.png)

Figure 6: Comparison for the AceGPT and Jais families of models.

## Conclusion and future work

In this blog post, we introduced the second version of the Open Arabic LLM Leaderboard. We analyzed the existing Arabic leaderboards as well as the first version of the OALL, remarking issues such as the saturation of specific benchmarks that were removed in this second iteration. We also removed machine-translated benchmarks and retained only the Arabic native and human-translated benchmarks. Finally, we introduced new benchmarks such as Aratrust, MadinaQA, native MMLU, human translated MMLU (MMLU-HT) and ALRAGE. Our goal is to offer the community an objective evaluation of Arabic LLMs, aiding in the understanding of the strengths and weaknesses of each submitted model.

Looking ahead, we hope to see the release of additional Arabic benchmarks, particularly in areas such as mathematics, reasoning, hallucination and both general and domain-specific benchmarks.

## Acknowledgments

The authors would like to thank Mohamed bin Zayed University of Artificial Intelligence (MBZUAI) for providing some of the new native benchmarks we are using in this version, including the new MMLU-HT dataset. We also extend our gratitude to TII for their generous sponsorship of the inference hardware needed for the evaluation backend. We also thank our friends at Hugging Face for their continuous support and being always 🤗 whenever needed. Thanks to all people focusing on evaluation and leaderboards for their languages and tasks. Lastly, we thank the community for their engagement and valuable feedback on the first version of the OALL. Looking forward to seeing many models on the leaderboard 🚀.

## Citations

```
@misc{OALL2,
  author = {El Filali, Ali and ALOUI, Manel and Husaain, Tarique and Alzubaidi, Ahmed and Boussaha, Basma El Amel and Cojocaru, Ruxandra and Fourrier, Clémentine and Habib, Nathan and Hacid, Hakim},
  title = {The Open Arabic LLM Leaderboard 2},
  year = {2025},
  publisher = {OALL},
  howpublished = {https://huggingface.co/spaces/OALL/Open-Arabic-LLM-Leaderboard}
}
```

## References

- [1] [Introducing the Open Arabic LLM Leaderboard](https://huggingface.co/blog/leaderboard-arabic) (El Filali et al., 2024)
- [2] [CamelEval: Advancing Culturally Aligned Arabic Language Models and Benchmarks](https://arxiv.org/abs/2409.12623v2) (Qian et al., 2024)
- [3] [AlGhafa Evaluation Benchmark for Arabic Language Models](https://aclanthology.org/2023.arabicnlp-1.21/) (Almazrouei et al., ArabicNLP 2023)
- [4] [The Belebele Benchmark: a Parallel Reading Comprehension Dataset in 122 Language Variants](https://aclanthology.org/2024.acl-long.44/) (Bandarkar et al., ACL, 2023)
- [5] [{EXAMS}: A Multi-subject High School Examinations Dataset for Cross-lingual and Multilingual Question Answering"](https://aclanthology.org/2020.emnlp-main.438/) (Hardalov et al., EMNLP, 2023)
- [6] [ArabicMMLU: Assessing Massive Multitask Language Understanding in Arabic](https://aclanthology.org/2024.findings-acl.334/)(Koto et al., ACL, 2024)
- [7] [Jais and jais-chat: Arabic-centric foundation and instruction-tuned open generative large language models](https://arxiv.org/abs/2308.16149) (Sengupta et al., 2023)
- [8] [AraTrust: An Evaluation of Trustworthiness for LLMs in Arabic](https://arxiv.org/abs/2403.09017) (Alghamdi et al., 2024)
- [9] [LightEval: A lightweight framework for LLM evaluation](https://github.com/huggingface/lighteval) (Fourrier et al., 2023)

## Models mentioned in this article 2

## Datasets mentioned in this article 5

## Spaces mentioned in this article 1

More Articles from our Blog

leaderboard

evaluation

nlp

## Arabic Leaderboards: Introducing Arabic Instruction Following, Updating AraGen, and More

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/626237d9bbcbd1c34f1bb231/EJrOjvAL-68qMCYdnvOrq.png)
- ![](https://huggingface.co/avatars/c71a54d7c9824d17ab4ad3deaf33afd1.svg)
- ![](https://huggingface.co/avatars/c12168cdda7085eb8d649e63115a82b5.svg)
- ![](https://huggingface.co/avatars/9b3b2d12ad3e1959aacfefbb931986dd.svg)
- +2

20

April 8, 2025

leaderboard

evaluation

nlp

## Rethinking LLM Evaluation with 3C3H: AraGen Benchmark and Leaderboard

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/626237d9bbcbd1c34f1bb231/EJrOjvAL-68qMCYdnvOrq.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6429100588215cee63b9334e/L5-CPVDsIC_1mI_izizyX.jpeg)
- ![](https://huggingface.co/avatars/c12168cdda7085eb8d649e63115a82b5.svg)
- ![](https://huggingface.co/avatars/cc9c6210fdc822d8a106937e747dff41.svg)
- +1

39

December 4, 2024

### Community

amohammed3339

Mar 24, 2025

Thanks for a detailed article. Why is there is no mention of allam from SDAIA?

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/626237d9bbcbd1c34f1bb231/EJrOjvAL-68qMCYdnvOrq.png)](https://huggingface.co/alielfilali01)

·

alielfilali01

Article author

Jun 24, 2025

At the time of the release ( February 10, 2025) there was no ALLaM from SDAIA available on the Hub to be evaluated !

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fleaderboard-arabic-v2) or [log in](https://huggingface.co/login?next=%2Fblog%2Fleaderboard-arabic-v2) to comment

Upvote

39

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6740a691ddc2c8e208a41102/Lt-aqBhzx-tQ58kFlSPjp.jpeg)](https://huggingface.co/robb-0)
- [![](https://huggingface.co/avatars/eccc801aa993bd11486c68422b6a5071.svg)](https://huggingface.co/hassanraha)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/626237d9bbcbd1c34f1bb231/EJrOjvAL-68qMCYdnvOrq.png)](https://huggingface.co/alielfilali01)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/60420dccc15e823a685f2b03/AOApMWt_jvm9e6XQ2vlrJ.jpeg)](https://huggingface.co/dvilasuero)
- [![](https://huggingface.co/avatars/66b0d4461fe6ae8b24494e1461231e02.svg)](https://huggingface.co/tarickMorty)
- [![](https://huggingface.co/avatars/598ecc79af157308a031693aec53dcf2.svg)](https://huggingface.co/basma-b)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6460bc5a933afb0106a7b31c/ps-YRqNufnVi_lP7CL05-.jpeg)](https://huggingface.co/rcojocaru)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1658510827196-5fc52718fa6eef7667a4d68e.jpeg)](https://huggingface.co/Manel-Hik)
- [![](https://huggingface.co/avatars/874c3eac1d738f805fa9b42d19bf4472.svg)](https://huggingface.co/amztheory)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6640bbd0220cfa8cbfdce080/wiAHUu5ewawyipNs0YFBR.png)](https://huggingface.co/John6666)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/654bcb6fae75d15300d48205/T4L1RZUgCZgdik4ZhEWCq.jpeg)](https://huggingface.co/Steveeeeeeen)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6423906a2d5965e7229efdc0/QDCWEO-pMQ3x3GOxLMYqx.png)](https://huggingface.co/MH0386)

## Models mentioned in this article 2

## Datasets mentioned in this article 5

## Spaces mentioned in this article 1
