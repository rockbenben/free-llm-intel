---
vendor: openai
title: Improving mathematical reasoning with process supervision
original_title: Improving mathematical reasoning with process supervision
url: https://openai.com/index/improving-mathematical-reasoning-with-process-supervision
date: 2023-10-19
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 5303a5dd7c2b
---

OpenAI

May 31, 2023

Publication

# Improving mathematical reasoning with process supervision

Read paper

(opens in a new window)

Browse samples

Download dataset

(opens in a new window)

Loading…

We’ve trained a model to achieve a new state-of-the-art in mathematical problem solving by rewarding each correct step of reasoning (“process supervision”) instead of simply rewarding the correct final answer (“outcome supervision”). In addition to boosting performance relative to outcome supervision, process supervision also has an important alignment benefit: it directly trains the model to produce a chain-of-thought that is endorsed by humans.

## Introduction

In recent years, large language models have greatly improved in their ability to perform complex multi-step reasoning. However, even state-of-the-art models still produce logical mistakes, often called *hallucinations*. Mitigating hallucinations is a critical step towards building aligned AGI.

We can train reward models to detect hallucinations using either *outcome supervision*, which provides feedback based on a final result, or *process supervision*, which provides feedback for each individual step in a chain-of-thought. Building on previous work[1](https://openai.com/index/improving-mathematical-reasoning-with-process-supervision/#citation-bottom-1), we conduct a detailed comparison of these two methods using the MATH dataset[2](https://openai.com/index/improving-mathematical-reasoning-with-process-supervision/#citation-bottom-2) as our testbed. We find that process supervision leads to significantly better performance, even when judged by outcomes. To encourage related research, we release our full dataset of process supervision.

## Alignment impact

Process supervision has several alignment advantages over outcome supervision. It directly rewards the model for following an aligned chain-of-thought, since each step in the process receives precise supervision. Process supervision is also more likely to produce interpretable reasoning, since it encourages the model to follow a human-approved process. In contrast, outcome supervision may reward an unaligned process, and it is generally harder to scrutinize.

In some cases, safer methods for AI systems can lead to reduced performance[3](https://openai.com/index/improving-mathematical-reasoning-with-process-supervision/#citation-bottom-3), a cost which is known as an *alignment tax*. In general, any alignment tax may hinder the adoption of alignment methods, due to pressure to deploy the most capable model. Our results below show that process supervision in fact incurs a negative alignment tax, at least in the math domain. This could increase the adoption of process supervision, which we believe would have positive alignment side-effects.

## Solving MATH problems

Loading...

We evaluate our process-supervised and outcome-supervised reward models using problems from the MATH test set. We generate many solutions for each problem and then pick the solution ranked the highest by each reward model. The graph shows the percentage of chosen solutions that reach the correct final answer, as a function of the number of solutions considered. Not only does the process-supervised reward model perform better across the board, but the performance gap widens as we consider more solutions per problem. This shows us that the process-supervised reward model is much more reliable.

We showcase 10 problems and solutions below, along with commentary about the reward model’s strengths and weaknesses.

Loading...

It is unknown how broadly these results will generalize beyond the domain of math, and we consider it important for future work to explore the impact of process supervision in other domains. If these results generalize, we may find that process supervision gives us the best of both worlds – a method that is both more performant and more aligned than outcome supervision.

- [GPT](https://openai.com/research/index/?tags=gpt)
- [Language](https://openai.com/research/index/?tags=language)
- [Learning Paradigms](https://openai.com/research/index/?tags=learning-paradigms)
- [Reasonings & Policy](https://openai.com/research/index/?tags=reasoning-policy)

## References

- 1Uesato, J., Kushman N., Kumar R., Song F., Siegel N., Wang L., Creswell A., Irving G. and Higgins, I., 2022. Solving math word problems with process- and outcome-based feedback. arXiv preprint arXiv:2211.14275.
- 2Hendrycks D., Burns C., Kadavath S., Arora A., Basart S., Tang E., Song D. and Steinhardt J., 2021. Measuring Mathematical Problem Solving With the MATH Dataset. arXiv preprint arXiv:2103.03874.
- 3Ouyang L., Wu J., Jiang X., Almedia D., Wainwright C.L., Mishkin P., Zhang C., Agarwal S., Slama K., Ray A., Schulman J., Hilton J., Kelton F., Miller L., Simens M., Askell A., Welinder P., Christiano P., Leike J. and Lowe R., 2022. Training language models to follow instructions with human feedback. arXiv preprint arXiv:2203.02155.

## Authors

Karl Cobbe, Hunter Lightman, Vineet Kosaraju, Yura Burda, Harri Edwards, Jan Leike, Ilya Sutskever

## Contributors

Bowen Baker, Teddy Lee, John Schulman, Greg Brockman, Kendra Rimbach, Hannah Wong, Thomas Degry

## Related articles

View all

DALL·E 3 is now available in ChatGPT Plus and Enterprise

ProductOct 19, 2023

Language models can explain neurons in language models

PublicationMay 9, 2023

Solving (some) formal math olympiad problems

MilestoneFeb 2, 2022
