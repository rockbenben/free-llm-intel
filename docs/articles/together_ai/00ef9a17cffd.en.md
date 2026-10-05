---
vendor: together_ai
title: How speech models fail where it matters the most and what to do about it
original_title: How speech models fail where it matters the most and what to do about it
url: https://www.together.ai/blog/how-speech-models-fail
date: 2026-02-23
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 845acc42426f
---

All blog posts

Research

Published 2/23/2026

# How speech models fail where it matters the most and what to do about it

- AuthorsKaitlyn Zhou, Martijn Bartelds, Federico Bianchi, James Zou
- Table of contents[40+ Models Chosen for Production...40+ Models Chosen for Production...40+ Models Chosen for Production...](https://www.together.ai/blog/how-speech-models-fail#)
- Links in this article[arXiv paper](https://arxiv.org/abs/2602.12249)[Dataset](https://huggingface.co/datasets/kzhou/sf_streets)‍

Summary

We demonstrate that voice recognition systems struggle to understand street name pronunciations when speakers have diverse linguistic backgrounds — with an average transcription error rate of 39% across 15 state-of-the-art models, and an 18% accuracy gap between non-English and English primary speakers. We show that a synthetic data generation technique called "cross-lingual style transfer" can reduce these errors by up to 60% relative to the base model, using fewer than 1,000 training samples.

2,262 utterances from 78 speakers across 13 languages, evaluated against 15 ASR models — yielding an average street name transcription error rate of 39%.

Automatic speech recognition systems such as Whisper, Deepgram, Phi-4, are integral to our current digital infrastructure. These models have been tested canonically on speech benchmarks like Librispeech and Switchboard and achieve near-human parity on metrics like Word Error Rate. However, these aggregate metrics, focused solely on word accuracy, can often mask critical errors. One of the most significant gaps is the inability to reliably transcribe short, high-stakes utterances in the real world. When a user dictates a command to a navigation system or an emergency dispatcher, a single error in a named entity can end up costing vital time to both the person and the dispatching entity.

Our latest research investigates the gap between benchmark performance and real-world reliability. We introduce SF Streets and US Streets, two new benchmarks designed to stress-test named entity recognition in deployed systems. Our evaluation reveals that even the most capable models from OpenAI, Deepgram, Google, and Microsoft struggle with this task. To address this, we developed a synthetic data generation recipe that leverages cross-lingual style transfer to improve performance by up to 60% (relative to the base model) with fewer than 1,000 training samples.

## Address recognition in STT benchmarking

Standard speech benchmarks are often dominated by long-form, read speech, where semantic context helps resolve ambiguities. Street names, when pronounced by residents of multi-lingual cities, represent a different challenge. They are context-poor, acoustically diverse, and intolerant of phonetic errors: a minor difference in pronunciation can make a big difference on the map.

To quantify this difficulty, we collected the SF Streets dataset. This collection comprises 2,262 utterances from 78 linguistically diverse participants from the U.S., pronouncing street names from San Francisco. We focused on the city's boulevards, such as "Cesar Chavez" or "Alemany,” as they serve as major arteries and are frequently referenced in navigation queries.

Non-English primary speakers consistently underperform across all model families, with an 18-point accuracy gap relative to English-only speakers (46% vs. 64%).

We evaluated 15 state-of-the-art models on this dataset and despite these models achieving low WER on general speech, the models exhibited an average transcription error rate of 39% on street names. This disconnect challenges the assumption that model scale automatically solves robustness. For example, Whisper-Large achieves a respectable general Word Error Rate of 14%, but its specific error rate on street names rises to 27%.

In a city like San Francisco, taxi services provide essential and subsidized transportation for elderly and disabled populations. These deviations result in tangible economic loss. Using standard taxi fare schedules and traffic data, we estimate that the additional driving time required to correct these errors costs of approximately \$4.00 per incident. If we aggregate this over the city's annual taxi volume, transcription errors alone could generate roughly 43,500 hours of avoidable delay per year. This amounts to an estimated \$2.1 million annually in wasted time and fares.

## Demographics and disparate impact

The reliability of these systems varies significantly across different groups. As modern speech models are deployed in diverse urban environments, they encounter speakers with varying accents and linguistic backgrounds. Our analysis of the SF Streets data revealed a significant performance disparity. Across our 15 models and model variants, non-English primary speakers exhibited an 18% lower accuracy compared to English primary speakers (46% versus 64%).

ASR errors send non-English speakers 2.40 miles off course on average — nearly double the 1.26-mile deviation seen for English-only speakers.

This technical failure translates directly into a more practical operational friction: to measure the real-world consequences, we mapped the transcribed street names to geographic coordinates using the Google Maps API; we found that mis-transcriptions for non-English primary speakers resulted in routing destinations that were, on average, 2.40 miles away from the intended location. Errors for English-only speakers resulted in a smaller deviation of 1.26 miles.

## Improving Representativeness with Data Cloning

Collecting representative human speech data for every possible named entity is prohibitively expensive and unscalable. Consequently, we investigated whether synthetic data could help us bridge this gap.

Cross-lingual style transfer uses XTTS to apply non-English phonetics to English street names, generating a <1,000 sample fine-tuning dataset that improves accuracy by 60% relative to the base model.

We exploited the inherent biases of multilingual text-to-speech models. We utilized a technique we call cross-lingual style transfer. We prompted the open-source XTTS model to generate speech in a foreign language like Spanish, but we injected specific English street names into the prompt. This forced the model to apply non-English phonetic rules to English words. Prompting the model with "Estoy en Washington" produces the word "Washington" with a distinct Spanish phonetic realization.

This method allowed us to generate a highly diverse set of pronunciations without needing human speakers. We created a fine-tuning dataset with fewer than 1,000 of these synthetic utterances. Fine-tuning Whisper-Base on this small synthetic set yielded a 60% relative improvement in accuracy from the base model, with the biggest improvements happening among non-English primary speakers. Illustrating that synthetic and open-sourced voice cloning at small scales can make significant improvements in the transcription of named entities.

## Moving forward

Our work highlights a persistent weakness in modern speech recognition. While general-purpose models continue to improve, they still fail disproportionately on the short, information-dense utterances that drive critical systems like emergency dispatch and navigation. However, we also demonstrate that this is a solvable problem. Creative use of synthetic data and style transfer allows practitioners to improve model robustness without the need for massive and expensive data collection efforts.

To facilitate further research, we will be releasing both the [SF Streets dataset](https://huggingface.co/datasets/kzhou/sf_streets) and the larger US Streets benchmark. The US Streets set contains 3,600 recordings from 12 major U.S. cities. We hope these resources help the community move beyond aggregate metrics and focus on the reliability that matters most in deployment.

## Related articles

View All

View All
