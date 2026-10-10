---
vendor: openai
title: Procgen and MineRL Competitions
original_title: Procgen and MineRL Competitions
url: https://openai.com/index/procgen-minerl-competitions
date: 2024-03-13
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: d86b2297e10c
---


June 20, 2020

Company

# Procgen and MineRL Competitions

We’re excited to announce that OpenAI is co-organizing two NeurIPS 2020 competitions with AIcrowd, Carnegie Mellon University, and DeepMind, using Procgen Benchmark and MineRL.


We’re excited to announce that OpenAI is co-organizing two NeurIPS 2020 competitions with AIcrowd, Carnegie Mellon University, and DeepMind, using Procgen Benchmark and MineRL. We rely heavily on these environments internally for research on reinforcement learning, and we look forward to seeing the progress the community makes in these challenging competitions.

## Procgen Competition


The [Procgen Competition](https://www.aicrowd.com/challenges/neurips-2020-procgen-competition) focuses on improving sample efficiency and generalization in reinforcement learning. Participants will attempt to maximize agents’ performance using a fixed number of environment interactions. Agents will be evaluated in each of the 16 environments already publicly released in [Procgen Benchmark](https://arxiv.org/abs/1912.01588), as well as in four secret test environments created specifically for this competition. By aggregating performance across so many diverse environments, we obtain high quality metrics to judge the underlying algorithms. More information about the details of each round can be found [here](https://www.aicrowd.com/challenges/neurips-2020-procgen-competition).

Since all content is procedurally generated, each Procgen environment intrinsically requires agents to generalize to never-before-seen situations. These environments therefore provide a robust test of an agent’s ability to learn in many diverse settings. Moreover, we designed Procgen environments to be fast and simple to use. Participants with limited computational resources will be able to easily reproduce our baseline results and run new experiments. We hope that this will empower participants to iterate quickly on new methods to improve sample efficiency and generalization in RL.

- [Sign up for Procgen](https://www.aicrowd.com/challenges/neurips-2020-procgen-competition)

## MineRL Competition


Many of the recent, celebrated successes of artificial intelligence, such as AlphaStar, AlphaGo, and our own [OpenAI Five⁠](https://openai.com/projects/five/), utilize deep reinforcement learning to achieve human or super-human level performance in sequential decision-making tasks. These improvements to the state-of-the-art have thus far required an [exponentially increasing⁠](https://openai.com/index/ai-and-compute/) amount of compute and simulator samples, and therefore it is difficult[A](https://openai.com/index/procgen-minerl-competitions/#citation-bottom-A) to apply many of these systems directly to real-world problems where environment samples are expensive. One well-known way to reduce the environment sample complexity is to leverage human priors and demonstrations of the desired behavior.

To further catalyze research in this direction, we are co-organizing the [MineRL 2020 Competition](https://www.aicrowd.com/challenges/neurips-2020-minerl-challenge) which aims to foster the development of algorithms which can efficiently leverage human demonstrations to drastically reduce the number of samples needed to solve complex, hierarchical, and sparse environments. To that end, participants will compete to develop systems which can obtain a diamond in [Minecraft](http://minercraft.net/) from raw pixels using only 8,000,000 samples from the [MineRL simulator](http://minerl.io/docs) and 4 days of training on a single GPU machine. Participants will be provided the MineRL-v0 dataset ([website](http://minerl.io/dataset/), [paper](https://arxiv.org/abs/1907.13440)), a large-scale collection of over 60 million frames of human demonstrations, enabling them to utilize expert trajectories to minimize their algorithm’s interactions with the Minecraft simulator.

This competition is a follow-up to the [MineRL 2019 Competition](https://www.aicrowd.com/challenges/neurips-2019-minerl-competition) in which the [top team’s agent](https://arxiv.org/pdf/1912.08664v2.pdf) was able to [obtain an iron pickaxe](https://www.youtube.com/watch?v=GHo8B4JMC38&feature=youtu.be) (the penultimate goal of the competition) under this extremely limited compute and simulator-interaction budget. Put in perspective, state-of-the-art standard reinforcement learning systems require hundreds of millions of environment interactions on large multi-GPU systems to achieve the same goal. This year, we anticipate competitors will push the state-of-the-art even further.

To guarantee that competitors develop truly sample efficient algorithms, the MineRL competition organizers train the top team’s final round models from scratch with strict constraints on the hardware, compute, and simulator-interaction available. The MineRL 2020 Competition also features a novel measure to avoid hand engineering features and overfitting solutions to the domain. More details on the competition structure can be found [here](https://www.aicrowd.com/challenges/neurips-2020-minerl-challenge).

- [Sign up for MineRL](https://www.aicrowd.com/challenges/neurips-2020-minerl-competition)


## Footnotes

- AWhile direct application is not possible due to the sheer number of samples required, Sim2Real and data augmentation techniques can mittigate the need to sample real-world dynamics directly.

## Author

OpenAI
