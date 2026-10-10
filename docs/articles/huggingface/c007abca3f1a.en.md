---
vendor: huggingface
title: HuggingFace, IISc partner to supercharge model building on India's diverse languages
original_title: HuggingFace, IISc partner to supercharge model building on India's diverse languages
url: https://huggingface.co/blog/iisc-huggingface-collab
date: 2026-09-17
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: aaa3d7dba16c
---


# HuggingFace, IISc partner to supercharge model building on India's diverse languages

					February 27, 2025

Update on GitHub


31

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/61b839889f7cfeae618e72c9/5kFRCChdqwv7MGM8T_y5v.jpeg)](https://huggingface.co/rbiswasfc)
- [![](https://huggingface.co/avatars/13aa6a9a79d9caeda105de81bd692cf8.svg)](https://huggingface.co/sid-artpark)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64e6f435c0cc3e95d1d2485c/z0AYSVOtUvvbG10xeKLow.png)](https://huggingface.co/llm-artpark)
- [![](https://huggingface.co/avatars/6e3b64d2a4d61b4781ce665d06db812d.svg)](https://huggingface.co/jigarkdoshi)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/65c07bca8e150328840949f5/xKu-F08hrJXx36_puq0sH.jpeg)](https://huggingface.co/theharshithh)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/42ZnpUdf-jANafNZ_2-Qg.png)](https://huggingface.co/physmatician)

Prasanta Kumar Ghosh

prasantg

ARTPARK-IISc

Nihar Desai

nihar-artpark

ARTPARK-IISc

Sanka

Visruth-sanka

ARTPARK-IISc

Sujith Pulikodan

SujithPulikodan

ARTPARK-IISc

The Indian Institute of Science [IISc](https://iisc.ac.in/) and [ARTPARK](https://artpark.in/) partner with Hugging Face to enable developers across the globe to access [Vaani](https://vaani.iisc.ac.in/), India's most diverse open-source, multi-modal, multi-lingual dataset. Both organisations share a commitment to building inclusive, accessible, and state-of-the-art AI technologies that honor linguistic and cultural diversity.

## Partnership

The partnership between Hugging Face and IISc/ARTPARK aims to increase the accessibility and improve usability of the Vaani dataset, encouraging the development of AI systems that better understand India's diverse languages and cater to the digital needs of its people.

## About Vaani Dataset

Launched in 2022 by IISc/ARTPARK and Google, Project Vaani is a pioneering initiative aimed at creating an open-source multi-modal dataset that truly represents India's linguistic diversity. This dataset is unique in its geo-centric approach, allowing for the collection of dialects and languages spoken in remote regions rather than focusing solely on mainstream languages.

Vaani targets the collection of over 150,000 hours of speech and 15,000 hours of transcribed text data from 1 million people across all 773 districts, ensuring diversity in language, dialects, and demographics.

The dataset is being built in phases, with Phase 1 covering 80 districts, which has already been open-sourced. Phase 2 is currently underway, expanding the dataset to 100 more districts, further strengthening Vaani's reach and impact across India's diverse linguistic landscape.

[![Key Highlights](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/iisc-huggingface-collab/Vaani_Dataset_summary.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/iisc-huggingface-collab/Vaani_Dataset_summary.png) *Key Highlights of the Vaani data set, open sourced so far: (as of 15-02-2025)*

### District wise language distribution

The Vaani dataset shows a rich distribution of languages across India's districts, highlighting linguistic diversity at a local level. This information is valuable for researchers, AI developers, and language technology innovators looking to build speech models tailored to specific regions and dialects. To explore the detailed district-wise language distribution, visit: [Vaani Dataset on HuggingFace](https://huggingface.co/datasets/ARTPARK-IISc/Vaani)

### Transcribed subset

If you need to access only transcribed data and you would like to skip untranscribed audio-only data, a subset of the larger dataset has been open sourced here. This dataset has 790 Hrs of transcribed audio, from ~7L speakers covering 70K images. This resource includes smaller, segmented audio units matched with precise transcriptions, allowing for different tasks including:

- Speech Recognition: Training models to accurately transcribe spoken language.
- Language Modeling: Building more refined language models.
- Segmentation Tasks: Identifying distinct speech units for improved transcription accuracy.

This additional dataset complements the main Vaani dataset, making it possible to develop end-to-end speech recognition systems and more targeted AI solutions.

## Utility of Vaani in the Age of LLMs

The Vaani dataset offers several key advantages, including extensive language coverage (54 languages), representation across diverse geographical regions, diverse educational and socio economic background, very large speaker coverage, spontaneous speech data, and real-life data collection environments. These features can enable inclusive AI models for:

- Speech-to-Text and Text-to-Speech: Fine-tuning these models for both LLM and non-LLM-based applications. Additionally, the transcription tagging enables the development of code-switching (Indic and English language)ASR models.
- Foundational Speech Models for Indic Languages: The dataset's significant linguistic and geographical coverage supports the development of robust foundational models for Indic languages.
- Speaker Identification/Verification Models: With data from over 80,000 speakers, the dataset is well-suited for developing robust speaker identification and verification models.
- Language Identification Models: Enables the creation of language identification models for various real-world applications.
- Speech Enhancement Systems: The dataset's tagging system supports the development of advanced speech enhancement technologies.
- Enhancing Multimodal LLMs: The unique data collection approach makes it valuable for building and improving multimodal capabilities in LLMs when combined with other multimodal datasets.
- Performance Benchmarking: The dataset is an ideal choice for benchmarking speech models due to its diverse linguistic, geographical, and real-world data properties.

These AI models can power a wide range of Conversational AI applications. From educational tools to telemedicine platforms, healthcare solutions, voter helplines, media localization, and multilingual smart devices, the Vaani dataset can be a game-changer in real-world scenarios.

## What's next

IISc/ARTPARK and Google have extended the partnership to Phase 2 (additional 100 districts). With this, Vaani covers all states in India! We are excited to bring this dataset to all of you.

[![Map of districts where data has been collected](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/iisc-huggingface-collab/district_map.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/iisc-huggingface-collab/district_map.png) *The map highlights the districts across India where data has been collected as of Feb 5,2025*

## How You Can Contribute

The most meaningful contribution you can make is to use the Vaani dataset. Whether building new AI applications, conducting research, or exploring innovative use cases, your engagement helps improve and expand the project.

We would be delighted to hear from you if you have feedback or insights from using the dataset. Please reach out to [vaanicontact@gmail.com](mailto:vaanicontact@gmail.com) to share your experiences/inquire about collaboration opportunities or please do fill out this [feedback form](https://docs.google.com/forms/d/e/1FAIpQLSdJ_oMoafkVabj0vgfbTsmECyFFQmbVy3b18NOsxUhYVJKeDQ/viewform).

Made with ❤️ for India's linguistic diversity

## Datasets mentioned in this article 1

More Articles from our Blog

evaluation

research

community

## How UK AISI and EvalEval Are Making Benchmark Results Reproducible

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6413251362e6057cbb6259bd/k8UMg_tnorG_uCXidybZ7.jpeg)
- ![](https://huggingface.co/avatars/d913dff9380e711aa4ecf368e3070f88.svg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/682434234254a325ecf16a29/PBoBR5WX9PA7IZqjcMOS8.png)
- ![](https://huggingface.co/avatars/70e55e861656a52ae535182db17d3789.svg)
- +5

27

September 22, 2026

partnerships

audio

open-source-collab

## Hugging Face and Cerebras bring Gemma 4 to real-time voice AI

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/67f2f500e329a81a62a05d44/DOlzc8GFQzrnfVrsOdtbN.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/65d66b494bbd0d92b641cdbb/6-7dm7B-JxcoS1QlCPdMN.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/5e48005437cb5b49818287a5/4uCXGGui-9QifAT4qelxU.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/qbWPAosFCnSgPJ-SRNZeG.png)

107

July 1, 2026

### Community

ngxson

Mar 1, 2025

📻 🎙️ Hey, I generated an **AI podcast** about this blog post, check it out!

*This podcast is generated via [ngxson/kokoro-podcast-generator](https://huggingface.co/spaces/ngxson/kokoro-podcast-generator), using [DeepSeek-R1](https://huggingface.co/deepseek-ai/DeepSeek-R1) and [Kokoro-TTS](https://huggingface.co/hexgrad/Kokoro-82M).*

soph000

Mar 4, 2025

I am interested in exploring partnership possibilities with Hugging Face. May I send an email to someone in charge of partnerships?

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fiisc-huggingface-collab) or [log in](https://huggingface.co/login?next=%2Fblog%2Fiisc-huggingface-collab) to comment


31

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/61b839889f7cfeae618e72c9/5kFRCChdqwv7MGM8T_y5v.jpeg)](https://huggingface.co/rbiswasfc)
- [![](https://huggingface.co/avatars/13aa6a9a79d9caeda105de81bd692cf8.svg)](https://huggingface.co/sid-artpark)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64e6f435c0cc3e95d1d2485c/z0AYSVOtUvvbG10xeKLow.png)](https://huggingface.co/llm-artpark)
- [![](https://huggingface.co/avatars/6e3b64d2a4d61b4781ce665d06db812d.svg)](https://huggingface.co/jigarkdoshi)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/65c07bca8e150328840949f5/xKu-F08hrJXx36_puq0sH.jpeg)](https://huggingface.co/theharshithh)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/42ZnpUdf-jANafNZ_2-Qg.png)](https://huggingface.co/physmatician)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/608aabf24955d2bfc3cd99c6/-YxmtpzEmf3NKOTktODRP.jpeg)](https://huggingface.co/ariG23498)
- [![](https://huggingface.co/avatars/da7059645ea516e7d76440d861320fa2.svg)](https://huggingface.co/nihar-artpark)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6640bbd0220cfa8cbfdce080/wiAHUu5ewawyipNs0YFBR.png)](https://huggingface.co/John6666)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/613a226b0fd0cb3c9b9ede5a/Dhi8bmqnAiG6s1rqNxJjM.jpeg)](https://huggingface.co/pulkitmehtawork)
- [![](https://huggingface.co/avatars/4bf3733caf68a04bab9ed970197e730d.svg)](https://huggingface.co/adit94)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/626237d9bbcbd1c34f1bb231/EJrOjvAL-68qMCYdnvOrq.png)](https://huggingface.co/alielfilali01)

## Datasets mentioned in this article 1
