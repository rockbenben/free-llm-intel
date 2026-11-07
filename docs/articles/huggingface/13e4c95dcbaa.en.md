---
vendor: huggingface
title: Egyptian and Nigerian English join the Open ASR Leaderboard
original_title: Egyptian and Nigerian English join the Open ASR Leaderboard
url: https://huggingface.co/blog/open-asr-leaderboard-liva
date: 2026-11-06
lang: en
captured: 2026-11-07
extractor: readability-v1
status: ok
body_sha: bb47a3416526
---

[ Back to Articles](https://huggingface.co/blog)

# Egyptian and Nigerian English join the Open ASR Leaderboard

Published November 6, 2026

Update on GitHub


5

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6384db7fb2906edaf835a91d/MOTXxaOmjlTZ8wONYifnD.jpeg)](https://huggingface.co/bezzam)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/g0ECTo_lbbi8O4Wt_e37M.png)](https://huggingface.co/ausyeternal)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/OcluLHMjRNEC15-7X46GD.png)](https://huggingface.co/decypher01)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6824dfdc3df9a0dff0a59b6f/WizAqpnpoeY2_C1NUPQDT.jpeg)](https://huggingface.co/luckygall)
- [![](https://huggingface.co/avatars/d380b48d9b44431a5376b465daf057fb.svg)](https://huggingface.co/ashleymo2025)

[![Eric Bezzam's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/6384db7fb2906edaf835a91d/MOTXxaOmjlTZ8wONYifnD.jpeg)](https://huggingface.co/bezzam)

Eric Bezzam

bezzam

[![Ashley Mo's avatar](https://huggingface.co/avatars/d380b48d9b44431a5376b465daf057fb.svg)](https://huggingface.co/ashleymo2025)

Ashley Mo

ashleymo2025

[![Liva AI's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/64d5eff05900b6d111c9e1ad/upXC_tilVUY3zVD_7UqJu.png)](https://huggingface.co/liva-ai) [liva-ai](https://huggingface.co/liva-ai)

[![Aoi Otani's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/64d5eff05900b6d111c9e1ad/hGnt9yx6LyQP5a2MBpXGg.jpeg)](https://huggingface.co/aonorii)

Aoi Otani

aonorii

[![Liva AI's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/64d5eff05900b6d111c9e1ad/upXC_tilVUY3zVD_7UqJu.png)](https://huggingface.co/liva-ai) [liva-ai](https://huggingface.co/liva-ai)

A few months ago, we added private data to the [Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard): 11 splits from Appen and DataOceanAI covering scripted and conversational speech from five accents ([blog](https://huggingface.co/blog/open-asr-leaderboard-private-data)). The community response was great, with many **highlighting the importance of held-out sets for trustworthy evaluations**. Since then, we added one more private split for Indian-accented English with Voice Arena ([blog](https://huggingface.co/blog/open-asr-leaderboard-global-south)).

We’re excited to announce a new collaboration with [Liva AI](https://huggingface.co/liva-ai) to add even more private data with two new accents: **Egyptian** 🇪🇬 and **Nigerian** 🇳🇬.

| Dataset | Accent | Duration [h] | Style | Transcription |
| --- | --- | --- | --- | --- |
| Liva AI Conversational EG | Egyptian | 1.34 | Conversational, spontaneous | Punctuated, cased, with disfluencies. |
| Liva AI Conversational NG | Nigerian | 1.55 | Conversational, spontaneous | Punctuated, cased, with disfluencies. |

This is part of our continued effort to improve representation in ASR evals (more accents and more languages) and to improve trust (new private data to minimize benchmaxxing, and new data providers). We’re excited to see the community continuing to push ASR performance for the world 🤗

## Richer accent breakdown in the Private tab

With these new accents, we can now present a richer breakdown of accents, based on [Kachru’s Three Circles](https://en.wikipedia.org/wiki/World_Englishes#Kachru%27s_Three_Circles_of_English) (kudos to Hume AI for this idea in their [leaderboard](https://huggingface.co/spaces/HumeAI/asr-leaderboard)). The Open ASR Leaderboard will now report:

- US vs. non-US (*UK, Australia, Canada, India, Nigeria, Egypt*)
- Inner Circle (*US, UK, Australia, Canada*) vs. Outer & Expanding Circles (*India, Nigeria, Egypt*)

As more accents join, we’ll split the Outer and Expanding Circles.

![thumbnail](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/open_asr_leaderboard/private_data_accent_breakdown.png)

## About Liva AI

Liva AI collects multimodal interaction data through consumer products used by real people. Because Liva owns both the collection environment and distribution, it can design products around specific model gaps across domains, industries, languages, modalities, and interaction types. This gives it access to natural, high-context behavior that emerges through real product use, rather than artificially elicited or task-based interactions.

## Spaces mentioned in this article 2

More Articles from our Blog

audiospeechleaderboard

## Open TTS Leaderboard: Scalable Evaluation for Multilingual Text-to-Speech and Voice Cloning

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6384db7fb2906edaf835a91d/MOTXxaOmjlTZ8wONYifnD.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/654bcb6fae75d15300d48205/T4L1RZUgCZgdik4ZhEWCq.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/660bc459d81d6112496f30f8/jMrpAckFyg-_iHMI7sn2h.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/62e54f0eae9d3f10acb95cb9/VAyk05hqB3OZWXEZW-B0q.png)

80

September 30, 2026

audiospeechleaderboard

## The Open ASR Leaderboard Adds Its First Global South Language

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6384db7fb2906edaf835a91d/MOTXxaOmjlTZ8wONYifnD.jpeg)
- ![](https://huggingface.co/avatars/56ce7e0fea0166a14997e7876fb23621.svg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/67bc3e2f4b9d3615a6e2c982/8x33LQ0fwbnUtIn9CAwv2.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6673251287330d7378e6b5e3/VVvuAsOUMiAPNgsdoRZjM.png)
- +6

61

August 28, 2026

### Community

![](https://huggingface.co/avatars/ab7fc92bae0354165d3f9890ac7f5b0b.svg)

wookute221

about 7 hours ago

hay

Upload images, audio, and videos by dragging in the text input, pasting, or clicking here.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fopen-asr-leaderboard-liva) or [log in](https://huggingface.co/login?next=%2Fblog%2Fopen-asr-leaderboard-liva) to comment


5

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6384db7fb2906edaf835a91d/MOTXxaOmjlTZ8wONYifnD.jpeg)](https://huggingface.co/bezzam)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/g0ECTo_lbbi8O4Wt_e37M.png)](https://huggingface.co/ausyeternal)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/OcluLHMjRNEC15-7X46GD.png)](https://huggingface.co/decypher01)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6824dfdc3df9a0dff0a59b6f/WizAqpnpoeY2_C1NUPQDT.jpeg)](https://huggingface.co/luckygall)
- [![](https://huggingface.co/avatars/d380b48d9b44431a5376b465daf057fb.svg)](https://huggingface.co/ashleymo2025)

## Spaces mentioned in this article 2
