---
vendor: anyscale
title: Advances in Foundation Models — Technology, Society, and Applications
original_title: Advances in Foundation Models
url: https://anyscale.com/blog/advances-in-foundation-models-technology-society-and-applications
date: 2023-11-03
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 42adc004c64c
---



Blog Detail

# Advances in Foundation Models — Technology, Society, and Applications

By

Anyscale Ray Team

|

November 3, 2023

Update June 2024: Anyscale Endpoints (Anyscale's LLM API Offering) and Private Endpoints (self-hosted LLMs) are now available as part of the Anyscale Platform. Click [here](https://console.anyscale.com/?utm_source=anyscale&utm_medium=blog&utm_campaign=blog_callout&utm_content=june2024_product_update_subheading) to get started on the Anyscale platform.

*This blog post is part of the Ray Summit 2023 highlights series where we provide a summary of the most exciting talk from our recent LLM developer conference.*

*Disclaimer: Summary was AI generated with human edits from video transcript.*

## LinkKey takeaways

In this blog post, we dive into Percy Liang’s insights into the latest developments in the field of AI and ML, the societal implications, and real-world applications. From technical innovations to their role in law, healthcare, and robotics, this blog post highlights the challenges and opportunities presented by foundation models.

- Foundation models are AI models that are trained on broad datasets and can then be adapted for many different downstream tasks. Companies are spending huge amounts of resources training these models.
- Academia has an important role to play in researching foundation models responsibly. Stanford founded a center combining computer scientists with experts in law, ethics, etc. to take a holistic socio-technical approach.
- They are working on advancing foundation models in 3 main dimensions: technical advances, applications (law, healthcare, robotics), and social responsibility (privacy, fairness, etc.)
- They have developed new techniques to improve data selection, model architectures, optimization, and alignment. These lead to significant speedups in training the models.
- They are evaluating foundation model capabilities comprehensively across many metrics beyond just accuracy, looking at things like robustness, fairness, and efficiency.
- Moving beyond just models, they want to evaluate entire organizations on their practices around transparency.
- Overall, an academic perspective allows them to do more neutral research to advance the technology responsibly.

## LinkAdvances in Foundation Models — Technology, Society, and Applications

The realm of Artificial Intelligence (AI) and Machine Learning (ML) is evolving at an astonishing pace, making it an incredibly exciting time for the industry. The developments in foundation models hold the potential to transform various sectors of society and it is imperative that it is done responsibly, transparently and ethically.

## LinkUnderstanding Foundation Models

Before delving into the details of the presentation, let's establish what foundation models are. These models serve as the backbone of AI and ML applications, providing a basis for various tasks such as text generation, image processing, and video generation. They are trained on vast datasets, enabling them to adapt to a wide array of downstream tasks. Foundation models are like the Swiss Army knives of the AI world, and their capabilities are only expected to grow.

## LinkThe Holistic Approach

Liang introduces a holistic socio-technical approach to understanding foundation models. Unlike the conventional approach that focuses solely on technical advancements, this approach combines the expertise of computer scientists with professionals from diverse fields such as law, economics, philosophy, education, and humanities. This holistic perspective aims to address the broader implications of foundation models on society.

## LinkTechnical Advances

The presentation delves into three key dimensions: technical advances, applications, and social responsibility. We'll start by exploring the technical advances in the field.

### LinkData Selection: Doremi Method

Data is the lifeblood of AI models, and selecting the right data is crucial. The Doremi method, developed in collaboration with Google, offers a statistically principled approach to data selection. It optimizes domain weights on a small model and transfers them to train large models, resulting in a 2.6 times faster training process.

### LinkModel Architecture: Beyond Transformers

While Transformers have been dominant in recent years, there's a growing demand for models capable of handling long sequences like DNA sequences or legal documents. The presentation introduces a novel approach using long convolutions inspired by state-space models from control theory, offering a remarkable speedup in processing long sequences.

### LinkOptimization: Sophia Optimization

Optimizing AI models is typically done using first-order information, such as gradients, which limits the understanding of curvature in the optimization landscape. Sophia optimization introduces a diagonal approximation of the Hessian with clipping, providing an effective way to optimize AI models. This method offers a 2x speedup compared to conventional optimization techniques.

### LinkAlignment: Direct Preference Optimization

The process of aligning AI models involves training them against pairwise preference data. Liang presents a simpler approach called Direct Preference Optimization, which simplifies the alignment process by eliminating the need for complex reward models and completion sampling. This streamlined approach offers an effective means of aligning models.

These technical advances not only improve the efficiency and speed of AI model development but also enhance the overall robustness of foundation models.

## LinkApplications of Foundation Models

Foundation models are being applied to various domains, and the presentation highlights their relevance in three specific areas: law, healthcare, and robotics.

### LinkLaw

In the legal domain, there's a significant opportunity to bridge the gap in legal services, particularly for underserved individuals. Foundation models can be used to deliver legal services efficiently. However, addressing legal reasoning, dealing with long legal texts, and ensuring reliability and trustworthiness are key challenges. The presentation introduces datasets like the Pile of Law and the Legal Bench, along with the development of models for legal reasoning. These initiatives aim to make legal services more accessible and reliable.

### LinkHealthcare

Healthcare, which accounts for a substantial portion of the GDP, is another sector where foundation models can make a significant impact. Privacy, trust, and clinical expertise are key concerns in this domain. Models like Biomed LM, trained on PubMed articles, and Renkin, a text and image model for generating medical images, illustrate the potential of AI in healthcare. The presentation discusses the use of foundation models to augment existing classifiers, enhance data augmentation, and serve as teaching tools in the medical field.

### LinkRobotics

Foundation models have the potential to revolutionize the field of robotics, making tasks like household cleaning more accessible. However, robotics presents unique challenges, including the need for physical embodiment, limited data, sequential decision-making, and a strong focus on safety and reliability. The presentation introduces data collection efforts and the development of models for household robotics. These efforts aim to make household robots a reality, with the promise of enhancing our daily lives.

### LinkSocial Responsibility and Policy Implications

The societal implications of foundation models cannot be understated, and the presentation discusses their role in addressing critical issues such as copyright, privacy, and watermarking.

### LinkCopyright

One of the pressing issues is the use of copyrighted data to train foundation models. The presentation highlights the ongoing legal disputes over whether training models on copyrighted data constitutes fair use. It also discusses technical mitigations like data filtering, reinforcement of human feedback (ROHF), and provenance tracking to navigate the complex landscape of copyright in AI.

### LinkPrivacy

Privacy is a paramount concern when it comes to AI models. The presentation explores the challenges of applying differential privacy to high-dimensional data like language models. The development of techniques to protect private data while still enabling training represents a critical step forward.

### LinkWatermarking

With increasing concerns about the misuse of AI-generated text, watermarking becomes essential. Watermarking text is challenging, as it should not distort the text's usefulness. The presentation introduces a distortion-free watermarking technique that preserves the capabilities of language models while enabling easy detection of AI-generated content.

## LinkEvaluation and Transparency

To ensure the responsible use of foundation models, it's crucial to evaluate organizations for their practices, specifically regarding transparency. The presentation highlights the need for organizations to be transparent about their data sets, model evaluations, and practices. This transparency can help guide policy decisions and ensure responsible AI development.

## LinkConclusion

Foundation models have emerged as a driving force in the AI and ML industry. Their technical advances are revolutionizing the way we train and use AI models, making them more efficient and reliable. Their applications in law, healthcare, and robotics hold the promise of transforming these domains. However, with great power comes great responsibility, and the presentation highlights the need for ethical and responsible use of foundation models.

As we continue to advance in the field of foundation models, it's crucial to consider the broader societal implications. Copyright, privacy, and watermarking are just a few of the issues that require careful consideration. Moreover, transparency and responsible practices are essential for organizations involved in AI development.

The presentation serves as a comprehensive guide to the evolving landscape of foundation models, shedding light on the challenges and opportunities they present. As society embraces AI and ML, understanding and addressing the implications of these technologies is more critical than ever. With responsible development and thoughtful policy decisions, foundation models have the potential to benefit humanity in numerous ways, shaping a more intelligent and efficient future.

In conclusion, the journey of foundation models is an exciting one, and we're only scratching the surface of their potential. As we continue to advance in the field of foundation models, it's crucial to consider the broader societal implications. Copyright, privacy, and watermarking are just a few of the issues that require careful consideration. Moreover, transparency and responsible practices are essential for organizations involved in AI development.

Sign up now for[ Anyscale endpoints](https://www.anyscale.com/endpoints?utm_source=anyscale&utm_campaign=ray-highlights-2023-blog) and get started fast or[ contact sales](https://www.anyscale.com/signup?utm_source=anyscale&utm_campaign=ray-highlights-2023-blog) if you are looking for a comprehensive overview of the Anyscale platform.

#### Table of contents

- [Key takeaways](https://www.anyscale.com/blog/advances-in-foundation-models-technology-society-and-applications#key-takeaways)
- [Advances in Foundation Models — Technology, Society, and Applications](https://www.anyscale.com/blog/advances-in-foundation-models-technology-society-and-applications#advances-in-foundation-models-—-technology,-society,-and-applications)
- [Understanding Foundation Models](https://www.anyscale.com/blog/advances-in-foundation-models-technology-society-and-applications#understanding-foundation-models)
- [The Holistic Approach](https://www.anyscale.com/blog/advances-in-foundation-models-technology-society-and-applications#the-holistic-approach)
- [Technical Advances](https://www.anyscale.com/blog/advances-in-foundation-models-technology-society-and-applications#technical-advances)
- [Data Selection: Doremi Method](https://www.anyscale.com/blog/advances-in-foundation-models-technology-society-and-applications#data-selection:-doremi-method)
- [Model Architecture: Beyond Transformers](https://www.anyscale.com/blog/advances-in-foundation-models-technology-society-and-applications#model-architecture:-beyond-transformers)
- [Optimization: Sophia Optimization](https://www.anyscale.com/blog/advances-in-foundation-models-technology-society-and-applications#optimization:-sophia-optimization)
- [Alignment: Direct Preference Optimization](https://www.anyscale.com/blog/advances-in-foundation-models-technology-society-and-applications#alignment:-direct-preference-optimization)
- [Applications of Foundation Models](https://www.anyscale.com/blog/advances-in-foundation-models-technology-society-and-applications#applications-of-foundation-models)
- [Law](https://www.anyscale.com/blog/advances-in-foundation-models-technology-society-and-applications#law)
- [Healthcare](https://www.anyscale.com/blog/advances-in-foundation-models-technology-society-and-applications#healthcare)
- [Robotics](https://www.anyscale.com/blog/advances-in-foundation-models-technology-society-and-applications#robotics)
- [Social Responsibility and Policy Implications](https://www.anyscale.com/blog/advances-in-foundation-models-technology-society-and-applications#social-responsibility-and-policy-implications)
- [Copyright](https://www.anyscale.com/blog/advances-in-foundation-models-technology-society-and-applications#copyright)
- [Privacy](https://www.anyscale.com/blog/advances-in-foundation-models-technology-society-and-applications#privacy)
- [Watermarking](https://www.anyscale.com/blog/advances-in-foundation-models-technology-society-and-applications#watermarking)
- [Evaluation and Transparency](https://www.anyscale.com/blog/advances-in-foundation-models-technology-society-and-applications#evaluation-and-transparency)
- [Conclusion](https://www.anyscale.com/blog/advances-in-foundation-models-technology-society-and-applications#conclusion)

#### Sharing

#### Tags

#### Sign up for product updates

#### Recommended content

#### Ray Summit 2026: Physical AI, RL, and the infrastructure that runs them all


#### Scaling Ray for AI workloads to 10k node clusters


#### Optimizing LLM Serving Efficiency: Moving Beyond KV Cache Reuse to Token-Load Awareness with Ray Serve LLM


## Explore Anyscale today

Build, run, and scale any AI workload on Ray with a multi-cloud platform built for production AI.

Start for Free

Talk to an expert
