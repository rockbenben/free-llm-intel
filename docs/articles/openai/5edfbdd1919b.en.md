---
vendor: openai
title: Prediction and control with temporal segment models
original_title: Prediction and control with temporal segment models
url: https://openai.com/index/prediction-and-control-with-temporal-segment-models
date: 2022-04-13
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: de7ffdf5d124
---

OpenAI

March 12, 2017

Publication

# Prediction and control with temporal segment models

Read paper

(opens in a new window)

Loading…

## Abstract

We introduce a method for learning the dynamics of complex nonlinear systems based on deep generative models over temporal segments of states and actions. Unlike dynamics models that operate over individual discrete timesteps, we learn the distribution over future state trajectories conditioned on past state, past action, and planned future action trajectories, as well as a latent prior over action trajectories. Our approach is based on convolutional autoregressive models and variational autoencoders. It makes stable and accurate predictions over long horizons for complex, stochastic systems, effectively expressing uncertainty and modeling the effects of collisions, sensory noise, and action delays. The learned dynamics model and action prior can be used for end-to-end, fully differentiable trajectory optimization and model-based policy optimization, which we use to evaluate the performance and sample-efficiency of our method.

- [Generative Models](https://openai.com/research/index/?tags=generative-models)

## Authors

Nikhil Mishra, Pieter Abbeel, Igor Mordatch

## Related articles

View all

Hierarchical text-conditional image generation with CLIP latents

PublicationApr 13, 2022

DALL·E: Creating images from text

MilestoneJan 5, 2021

Image GPT

PublicationJun 17, 2020
