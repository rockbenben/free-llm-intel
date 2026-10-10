---
vendor: openai
title: Hindsight Experience Replay
original_title: Hindsight Experience Replay
url: https://openai.com/index/hindsight-experience-replay
date: 2022-10-19
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: a996653c1c45
---

OpenAI

July 5, 2017

Publication

# Hindsight Experience Replay

Read paper



Loading…

## Abstract

Dealing with sparse rewards is one of the biggest challenges in Reinforcement Learning (RL). We present a novel technique called Hindsight Experience Replay which allows sample-efficient learning from rewards which are sparse and binary and therefore avoid the need for complicated reward engineering. It can be combined with an arbitrary off-policy RL algorithm and may be seen as a form of implicit curriculum.

We demonstrate our approach on the task of manipulating objects with a robotic arm. In particular, we run experiments on three different tasks: pushing, sliding, and pick-and-place, in each case using only binary rewards indicating whether or not the task is completed. Our ablation studies show that Hindsight Experience Replay is a crucial ingredient which makes training possible in these challenging environments. We show that our policies trained on a physics simulation can be deployed on a physical robot and successfully complete the task.

- [Learning Paradigms](https://openai.com/research/index/?tags=learning-paradigms)

## Authors

Marcin Andrychowicz, Filip Wolski, Alex Ray, Jonas Schneider, Rachel Fong, Peter Welinder, Bob McGrew, Josh Tobin, Pieter Abbeel, Wojciech Zaremba

## Related articles

View all

Scaling laws for reward model overoptimization

PublicationOct 19, 2022

Learning to play Minecraft with Video PreTraining

ConclusionJun 23, 2022

Dota 2 with large scale deep reinforcement learning

PublicationDec 13, 2019
