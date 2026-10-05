---
vendor: huggingface
title: Docmatix - A huge dataset for Document Visual Question Answering
original_title: Docmatix
url: https://huggingface.co/blog/docmatix
date: 2025-12-10
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 1d2b74caf3cf
---

Back to Articles

# Docmatix - A huge dataset for Document Visual Question Answering

Published
					July 18, 2024

Update on GitHub

Upvote

80

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6253fb19d3e43081e102af4f/0M0Ksd8rzm_g4k-hl0xP6.jpeg)](https://huggingface.co/Dreamer312)
- [![](https://huggingface.co/avatars/fb50773ac49948940eb231834ee6f2fd.svg)](https://huggingface.co/irotem98)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/utGl1liVi34zGMz6fi6Jz.jpeg)](https://huggingface.co/JayRay5)
- [![](https://huggingface.co/avatars/ad7e7c6e7e6c24e0e75e718d49db990e.svg)](https://huggingface.co/marcovaldo)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1666440274544-6353dc3e3bc1819d22d41e7f.jpeg)](https://huggingface.co/TankNee)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/61ed0ff29539bc0a3bbc89f4/iYWK7GParA7Ke5F6q132W.jpeg)](https://huggingface.co/mfarre)

Andres Marafioti

andito

Hugo Laurençon

HugoLaurencon

This article is also available in Chinese [简体中文](https://huggingface.co/blog/zh/docmatix).

With this blog we are releasing [Docmatix - a huge dataset for Document Visual Question Answering](https://huggingface.co/datasets/HuggingFaceM4/Docmatix) (DocVQA) that is 100s of times larger than previously available. Ablations using this dataset for fine-tuning Florence-2 show a 20% increase in performance on DocVQA.

![Example from the dataset](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/docmatix_example.png)
 *An example from the dataset*

We first had the idea to create Docmatix when we developed [The Cauldron](https://huggingface.co/datasets/HuggingFaceM4/the_cauldron), an extensive collection of 50 datasets for the fine-tuning of Vision-Language Model (VLM), and [Idefics2](https://huggingface.co/blog/idefics2) in particular. Through this process, we identified a significant gap in the availability of large-scale Document Visual Question Answering (DocVQA) datasets. The primary dataset we relied on for Idefics2 was DocVQA, which contains 10,000 images and 39,000 question-answer (Q/A) pairs. Fine-tuning on this and other datasets, open-sourced models still maintain a large gap in performance to closed-source ones. To address this limitation, we are excited to introduce Docmatix, a DocVQA dataset featuring 2.4 million images and 9.5 million Q/A pairs derived from 1.3 million PDF documents. A **240X** increase in scale compared to previous datasets.

![Comparing Docmatix to other DocVQA datasets](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/docmatix_dataset_comp.png)
 *Comparing Docmatix to other DocVQA datasets*

Here you can explore the dataset yourself and see the type of documents and question-answer pairs contained in Docterix.

Docmatix is generated from [PDFA, an extensive OCR dataset containing 2.1 million PDFs](https://huggingface.co/datasets/pixparse/pdfa-eng-wds). We took the transcriptions from PDFA and employed a [Phi-3-small](https://huggingface.co/microsoft/Phi-3-small-8k-instruct) model to generate Q/A pairs. To ensure the dataset's quality, we filtered the generations, discarding 15% of the Q/A pairs identified as hallucinations. To do so, we used regular expressions to detect code and removed answers that contained the keyword “unanswerable”. The dataset contains a row for each PDF. We converted the PDFs to images at a resolution of 150 dpi, and uploaded the processed images to the Hugging Face Hub for easy access. All the original PDFs in Docmatix can be traced back to the original PDFA dataset, providing transparency and reliability. Still, we uploaded the processed images for convenience because converting many PDFs to images can be resource-intensive.

![Processing for Docmatix](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/docmatix_processing.png)
 *Processing pipeline to generate Docmatix*

After processing the first small batch of the dataset, we performed several ablation studies to optimize the prompts. We aimed to generate around four pairs of Q/A per page. Too many pairs indicate a large overlap between them, while too few pairs suggest a lack of detail. Additionally, we aimed for answers to be human-like, avoiding excessively short or long responses. We also prioritized diversity in the questions, ensuring minimal repetition. Interestingly, when we guided the [Phi-3 model](https://huggingface.co/docs/transformers/main/en/model_doc/phi3) to ask questions based on the specific information in the document (e.g., "What are the titles of John Doe?"), the questions showed very few repetitions. The following plot presents some key statistics from our analysis:

![Prompt analysis Docmatix](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/docmatix_prompt_analysis.png)
 *Analysis of Docmatix per prompt*

To evaluate Docmatix's performance, we conducted ablation studies using the Florence-2 model. We trained two versions of the model for comparison. The first version was trained over several epochs on the DocVQA dataset. The second version was trained for one epoch on Docmatix (20% of the images and 4% of the Q/A pairs), followed by one epoch on DocVQA to ensure the model produced the correct format for DocVQA evaluation. The results are significant: training on this small portion of Docmatix yielded a relative improvement of almost 20%. Additionally, the 0.7B Florence-2 model performed only 5% worse than the 8B Idefics2 model trained on a mixture of datasets and is significantly larger.

| Dataset | ANSL on DocVQA | model size |
| --- | --- | --- |
| Florence 2 fine-tuned on DocVQA | 60.1 | 700M |
| Florence 2 fine-tuned on Docmatix | 71,4 | 700M |
| Idefics2 | 74,0 | 8B |

## Conclusion

In this post, we presented Docmatix, a gigantic dataset for DocVQA. We showed that using Docmatix we can achieve a 20% increase in DocVQA performance when finetuning Florence-2. This dataset should help bridge the gap between proprietary VLMs and open-sourced VLMs. We encourage the open-source community to leverage Docmatix and train new amazing DocVQA models! We can't wait to see your models on the 🤗 Hub!

## Useful Resources

- [Docmatix used to finetune Florence-2 Demo](https://huggingface.co/spaces/HuggingFaceM4/Docmatix-Florence-2)
- [Finetuning Florence-2 Blog](https://huggingface.co/blog/finetune-florence2)
- [Fine tuning Florence-2 Github Repo](https://github.com/andimarafioti/florence2-finetuning)
- [Vision Language Models Explained](https://huggingface.co/blog/vlms)

We would like to thank merve and leo for their reviews and thumbnails for this blog.

## Models mentioned in this article 1

## Datasets mentioned in this article 3

## Spaces mentioned in this article 1

More Articles from our Blog

community

evaluation

synthetic-data

## LAVE: Zero-shot VQA Evaluation on Docmatix with LLMs - Do We Still Need Fine-Tuning?

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/640e21ef3c82bd463ee5a76d/nVR1DFPAsiLw6Boys28Rb.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/65d66b494bbd0d92b641cdbb/6-7dm7B-JxcoS1QlCPdMN.jpeg)

17

July 25, 2024

llm

nlp

synthetic-data

Hot

## SmolLM - blazingly fast and remarkably powerful

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/61c141342aac764ce1654e43/81AwoT5IQ_Xdw0OVw7TKu.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1613655355830-noauth.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/651e96991b97c9f33d26bde6/-Bqs6qrmz0yCfwtB2e-6q.jpeg)

470

July 16, 2024

### Community

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fdocmatix) or [log in](https://huggingface.co/login?next=%2Fblog%2Fdocmatix) to comment

Upvote

80

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6253fb19d3e43081e102af4f/0M0Ksd8rzm_g4k-hl0xP6.jpeg)](https://huggingface.co/Dreamer312)
- [![](https://huggingface.co/avatars/fb50773ac49948940eb231834ee6f2fd.svg)](https://huggingface.co/irotem98)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/utGl1liVi34zGMz6fi6Jz.jpeg)](https://huggingface.co/JayRay5)
- [![](https://huggingface.co/avatars/ad7e7c6e7e6c24e0e75e718d49db990e.svg)](https://huggingface.co/marcovaldo)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1666440274544-6353dc3e3bc1819d22d41e7f.jpeg)](https://huggingface.co/TankNee)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/61ed0ff29539bc0a3bbc89f4/iYWK7GParA7Ke5F6q132W.jpeg)](https://huggingface.co/mfarre)
- [![](https://huggingface.co/avatars/db193ee4ec32c14dd36388deb4152b2b.svg)](https://huggingface.co/SKB2021)
- [![](https://huggingface.co/avatars/82ec820375403def510c895d4bf9c12d.svg)](https://huggingface.co/windgrin)
- [![](https://huggingface.co/avatars/50f05c2692b8bf04d7477918eddd7a8e.svg)](https://huggingface.co/yzlii)
- [![](https://huggingface.co/avatars/5476622a4961f4fe5d1c85476badad37.svg)](https://huggingface.co/imjliao)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/66330485060ab1f666c9c0e4/fcVdNVk61zwFylOEUzxyR.png)](https://huggingface.co/mransby-groq)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/mSruVvc9kNgzZaSbZ5r6M.png)](https://huggingface.co/chenhaodev)

## Models mentioned in this article 1

## Datasets mentioned in this article 3

## Spaces mentioned in this article 1
