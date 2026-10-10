---
vendor: huggingface
title: Launching the Artificial Analysis Text to Image Leaderboard & Arena
original_title: Launching the Artificial Analysis Text to Image Leaderboard & Arena
url: https://huggingface.co/blog/leaderboard-artificial-analysis2
date: 2024-06-06
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 31fc01a7b342
---


# Launching the Artificial Analysis Text to Image Leaderboard & Arena

					June 6, 2024

Update on GitHub


16

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/638eb5f949de7ae552dd6211/mJkQJGpn9tXV37N2VLFCh.jpeg)](https://huggingface.co/derek-thomas)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/62b085e6a14cbd643867d561/9gR-XStGUTE-T6vVhKUlA.png)](https://huggingface.co/thliang01)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/65d9903fdceb54d42011a98d/5jnLeCY9sDtS98JyO9qzX.jpeg)](https://huggingface.co/meng-shao)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1667018139063-noauth.jpeg)](https://huggingface.co/ojasvisingh786)
- [![](https://huggingface.co/avatars/6bbe81608f9fb82506dec7cbd182d94b.svg)](https://huggingface.co/hppdqdq)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/647f36a8454af0237bd49574/jshkqBUTY-GZL8As8y6Aq.jpeg)](https://huggingface.co/fdaudens)

Micah Hill-Smith

mhillsmith

ArtificialAnalysis

George Cameron

georgewritescode

ArtificialAnalysis

In two short years since the advent of diffusion-based image generators, AI image models have achieved near-photographic quality. How do these models compare? Are the open-source alternatives on par with their proprietary counterparts?

The Artificial Analysis Text to Image Leaderboard aims to answer these questions with human preference based rankings. The ELO score is informed by over 45,000 human image preferences collected in the Artificial Analysis Image Arena. The leaderboard features the leading open-source and proprietary image models : the latest versions of Midjourney, OpenAI's DALL·E, Stable Diffusion, Playground and more.

[![Untitled](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/leaderboards-on-the-hub/artificial_analysis_vision_leaderboard.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/leaderboards-on-the-hub/artificial_analysis_vision_leaderboard.png)

Check-out the leaderboard here: [https://huggingface.co/spaces/ArtificialAnalysis/Text-to-Image-Leaderboard](https://huggingface.co/spaces/ArtificialAnalysis/Text-to-Image-Leaderboard)

You can also take part in the Text to Image Arena, and get your personalized model ranking after 30 votes!

## Methodology

Comparing the quality of image models has traditionally been even more challenging than evaluations in other AI modalities such as language models, in large part due to the inherent variability in people’s preferences for how images should look. Early objective metrics have given way to expensive human preference studies as image models approach very high accuracy. Our Image Arena represents a crowdsourcing approach to gathering human preference data at scale, enabling comparison between key models for the first time.

We calculate an ELO score for each model via a regression of all preferences, similar to Chatbot Arena. Participants are presented with a prompt and two images, and are asked select the image that best reflects the prompt. To ensure the evaluation reflects a wide-range of use-cases we generate >700 images for each model. Prompts span diverse styles and categories including human portraits, groups of people, animals, nature, art and more.

## Early Insights From the Results 👀

- **While proprietary models lead, open source is increasingly competitive**: Proprietary models including Midjourney, Stable Diffusion 3 and DALL·E 3 HD lead the leaderboard. However, a number of open-source models, currently led by Playground AI v2.5, are gaining ground and surpass even OpenAI’s DALL·E 3.
- **The space is rapidly advancing:** The landscape of image generation models is rapidly evolving. Just last year, DALL·E 2 was a clear leader in the space. Now, DALL·E 2 is selected in the arena less than 25% of the time and is amongst the lowest ranked models.
- **Stable Diffusion 3 Medium being open sourced may have a big impact on the community**: Stable Diffusion 3 is a contender to the top position on the current leaderboard and Stability AI’s CTO recently announced during a presentation with AMD that Stable Diffusion 3 Medium will be open sourced June 12. Stable Diffusion 3 Medium may offer lower quality performance compared to the Stable Diffusion 3 model served by Stability AI currently (presumably the full-size variant), but the new model may be a major boost to the open source community. As we have seen with Stable Diffusion 1.5 and SDXL, it is likely we will see many fine tuned versions released by the community.

## How to contribute or get in touch

To see the leaderboard, check out the space on Hugging Face here: [https://huggingface.co/spaces/ArtificialAnalysis/Text-to-Image-Leaderboard](https://huggingface.co/spaces/ArtificialAnalysis/Text-to-Image-Leaderboard)

To participate in the ranking and contribute your preferences, select the ‘Image Arena’ tab and choose the image which you believe best represents the prompt. After 30 images, select the ‘Personal Leaderboard’ tab to see your own personalized ranking of image models based on your selections.

For updates, please follow us on [**Twitter**](https://twitter.com/ArtificialAnlys) and [**LinkedIn**](https://linkedin.com/company/artificial-analysis). (We also compare the speed and pricing of Text to Image model API endpoints on our website at [https://artificialanalysis.ai/text-to-image](https://artificialanalysis.ai/text-to-image)).

We welcome all feedback! We're available via message on Twitter, as well as on [**our website](https://artificialanalysis.ai/contact)** via our contact form.

## Other Image Model Quality Initiatives

The Artificial Analysis Text to Image leaderboard is not the only quality image ranking or crowdsourced preference initiative. We built our leaderboard to focus on covering both proprietary and open source models to give a full picture of how leading Text to Image models compare.

Check out the following for other great initiatives:

- [Open Parti Prompts Leaderboard](https://huggingface.co/spaces/OpenGenAI/parti-prompts-leaderboard)
- [imgsys Arena](https://huggingface.co/spaces/fal-ai/imgsys)
- [GenAI-Arena](https://huggingface.co/spaces/TIGER-Lab/GenAI-Arena)
- [Vision Arena](https://huggingface.co/spaces/WildVision/vision-arena)

## Spaces mentioned in this article 4

More Articles from our Blog

leaderboard

research

collaboration

## Evaluating Audio Reasoning with Big Bench Audio

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/662f2349d9b837e4b9afcc4b/kgebZafkGF2fRzRelZP0y.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/65ff2f9fcc7a4f35567b9098/oilyj1kmz11ifVoCLrK-H.png)

31

December 20, 2024

community

research

nlp

## Letting Large Models Debate: The First Multilingual LLM Debate Competition

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/62fcd91b03f866462204b591/BkAVmJRKzBX_zRimf_yXY.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/662f4fed259fa63f77da1f72/JOPCmhNeKE0d01tx-le5c.jpeg)
- ![](https://huggingface.co/avatars/bb8db04ea1444eac0820fee3acd652c1.svg)
- ![](https://huggingface.co/avatars/cf2d4a9295b5da9e2e4d2278bbb36040.svg)
- +8

33

November 20, 2024

### Community

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fleaderboard-artificial-analysis2) or [log in](https://huggingface.co/login?next=%2Fblog%2Fleaderboard-artificial-analysis2) to comment


16

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/638eb5f949de7ae552dd6211/mJkQJGpn9tXV37N2VLFCh.jpeg)](https://huggingface.co/derek-thomas)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/62b085e6a14cbd643867d561/9gR-XStGUTE-T6vVhKUlA.png)](https://huggingface.co/thliang01)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/65d9903fdceb54d42011a98d/5jnLeCY9sDtS98JyO9qzX.jpeg)](https://huggingface.co/meng-shao)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1667018139063-noauth.jpeg)](https://huggingface.co/ojasvisingh786)
- [![](https://huggingface.co/avatars/6bbe81608f9fb82506dec7cbd182d94b.svg)](https://huggingface.co/hppdqdq)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/647f36a8454af0237bd49574/jshkqBUTY-GZL8As8y6Aq.jpeg)](https://huggingface.co/fdaudens)
- [![](https://huggingface.co/avatars/2a6062d390533e6693a106aa00d85267.svg)](https://huggingface.co/myagudaev)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/60c8d264224e250fb0178f77/i8fbkBVcoFeJRmkQ9kYAE.png)](https://huggingface.co/Abecid)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64b695dcd3df8086e5ed7c89/ZULwnPE8Q5q7bxKJsJ7v5.jpeg)](https://huggingface.co/0xFieldsy)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/673902aa41d69ace67e40cad/Ber311om5T2bziYeN4GJx.jpeg)](https://huggingface.co/aidiffusion99)
- [![](https://huggingface.co/avatars/d3501c12545757a8adb60c5ad7be18f9.svg)](https://huggingface.co/m-tuyishime)
- [![](https://huggingface.co/avatars/1cabf575c0c6e99a7e0e1e2c59402346.svg)](https://huggingface.co/Jzelll)

## Spaces mentioned in this article 4
