---
vendor: openai
title: Variational option discovery algorithms
original_title: Variational option discovery algorithms
url: https://openai.com/index/variational-option-discovery-algorithms
date: 2022-10-19
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 9129d0332b69
---

OpenAI

July 26, 2018

Publication

# Variational option discovery algorithms

Read paper



Loading…

## Abstract

We explore methods for option discovery based on variational inference and make two algorithmic contributions. First: we highlight a tight connection between variational option discovery methods and variational autoencoders, and introduce Variational Autoencoding Learning of Options by Reinforcement (VALOR), a new method derived from the connection. In VALOR, the policy encodes contexts from a noise distribution into trajectories, and the decoder recovers the contexts from the complete trajectories. Second: we propose a curriculum learning approach where the number of contexts seen by the agent increases whenever the agent's performance is strong enough (as measured by the decoder) on the current set of contexts. We show that this simple trick stabilizes training for VALOR and prior variational option discovery methods, allowing a single agent to learn many more modes of behavior than it could with a fixed context distribution. Finally, we investigate other topics related to variational option discovery, including fundamental limitations of the general approach and the applicability of learned options to downstream tasks.

- [Learning Paradigms](https://openai.com/research/index/?tags=learning-paradigms)

## Authors

Joshua Achiam, Harri Edwards, Dario Amodei, Pieter Abbeel

## Related articles

View all

Scaling laws for reward model overoptimization

PublicationOct 19, 2022

Learning to play Minecraft with Video PreTraining

ConclusionJun 23, 2022

Dota 2 with large scale deep reinforcement learning

PublicationDec 13, 2019
