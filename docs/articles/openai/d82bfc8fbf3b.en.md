---
vendor: openai
title: Ingredients for robotics research
original_title: Ingredients for robotics research
url: https://openai.com/index/ingredients-for-robotics-research
date: 2022-10-19
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 68be70e6bfcb
---


February 26, 2018

Release

# Ingredients for robotics research

View Gym environments



View Baselines






Ben Barry


We’re releasing eight simulated robotics environments and a Baselines implementation of Hindsight Experience Replay, all developed for our research over the past year. We’ve used these environments to train models which work on physical robots. We’re also releasing a set of requests for robotics research.

This release includes four environments using the [Fetch](http://fetchrobotics.com/platforms-research-development/) research platform and four environments using the [ShadowHand](https://www.shadowrobot.com/products/dexterous-hand/) robot. The manipulation tasks contained in these environments are significantly more difficult than the MuJoCo continuous control environments currently available in Gym, all of which are now easily solvable using recently released algorithms like [PPO⁠](https://openai.com/index/openai-baselines-ppo/). Furthermore, our newly released environments use models of real robots and require the agent to solve realistic tasks.

## Environments


This release ships with eight robotics environments for [Gym](https://github.com/openai/gym) that use the [MuJoCo](https://www.mujoco.org/) physics simulator. The environments are:

## Goals

All of the new tasks have the concept of a “goal”, for example the desired position of the puck in the slide task or the desired orientation of a block in the hand block manipulation task. All environments by default use a sparse reward of -1 if the desired goal was not yet achieved and 0 if it was achieved (within some tolerance). This is in contrast to the shaped rewards used in the old set of Gym continuous control problems, for example [Walker2d-v2](https://github.com/openai/gym/blob/master/gym/envs/mujoco/walker2d.py) with its [shaped reward](https://github.com/openai/gym/blob/master/gym/envs/mujoco/walker2d.py#L16-L18).

We also include a variant with dense rewards for each environment. However, we believe that sparse rewards are more realistic in robotics applications and we encourage everyone to use the sparse reward variant instead.

## Hindsight Experience Replay

Alongside these new robotics environments, we’re also [releasing code](https://github.com/openai/baselines) for [Hindsight Experience Replay](https://arxiv.org/abs/1707.01495) (or HER for short), a reinforcement learning algorithm that can learn from failure. Our results show that HER can learn successful policies on most of the new robotics problems from only sparse rewards. Below, we also show some potential directions for future research that could further improve the performance of the HER algorithm on these tasks.

## Understanding HER

To understand what HER does, let’s look at in the context of [FetchSlide](https://gym.openai.com/envs/FetchSlide-v0), a task where we need to learn to slide a puck across the table and hit a target. Our first attempt very likely will not be a successful one. Unless we get very lucky, the next few attempts will also likely not succeed. Typical reinforcement learning algorithms would not learn anything from this experience since they just obtain a constant reward (in this case: `-1`) that does not contain any learning signal.

The key insight that HER formalizes is what humans do intuitively: Even though we have not succeeded at a specific goal, we have at least achieved a different one. So why not just pretend that we wanted to achieve this goal to begin with, instead of the one that we set out to achieve originally? By doing this substitution, the reinforcement learning algorithm can obtain a learning signal since it has achieved *some* goal; even if it wasn’t the one that we meant to achieve originally. If we repeat this process, we will eventually learn how to achieve arbitrary goals, including the goals that we really want to achieve.

This approach lets us learn how to slide a puck across the table even though our reward is fully sparse and even though we may have never actually hit the desired goal early on. We call this technique Hindsight Experience Replay since it replays experience (a technique often used in off-policy RL algorithms like [DQN⁠](https://openai.com/index/openai-baselines-dqn/) and [DDPG](https://arxiv.org/abs/1509.02971)) with goals which are chosen in hindsight, after the episode has finished. HER can therefore be combined with any off-policy RL algorithm (for example, HER can be combined with DDPG, which we write as “DDPG + HER”).

## Results

We’ve found HER to work extremely well in goal-based environments with sparse rewards. We compare DDPG + HER and vanilla DDPG on the new tasks. This comparison includes the sparse and the dense reward versions of each environment.

Median test success rate (line) with interquartile range (shaded area) for four different configurations on HandManipulateBlockRotateXYZ-v0. Data is plotted over training epochs and summarized over five different random seeds per configuration.

DDPG + HER with sparse rewards significantly outperforms all other configurations and manages to learn a successful policy on this challenging task only from sparse rewards. Interestingly, DDPG + HER with dense reward is able to learn but achieves worse performance. Vanilla DDPG mostly fails to learn in both cases. We find this trend to be generally true across most environments and we include full results in our accompanying [technical report](https://arxiv.org/abs/1802.09464).

### Requests for Research: HER edition

Though HER is a promising way towards learning complex goal-based tasks with sparse rewards like the robotics environments that we propose here, there is still a lot of room for improvement. Similar to our recently published [Requests for Research 2.0⁠](https://openai.com/index/requests-for-research-2/), we have a few ideas on ways to improve HER specifically, and reinforcement learning in general.

- **Automatic hindsight goal creation**. We currently have a hard-coded strategy for selecting hindsight goals that we want to substitute. It would be interesting if this strategy could be learned instead.
- **Unbiased HER**. The goal substitution changes the distribution of experience in an unprincipled way. This bias can in theory lead to instabilities, although we do not find this to happen in practice. Still, it would be nice to derive an unbiased version of HER, for example by utilizing [importance sampling](https://en.wikipedia.org/wiki/Importance_sampling).
- **HER + HRL**. It would be interesting to further combine HER with a [recent idea](https://arxiv.org/abs/1712.00948) in hierarchical reinforcement learning (HRL). Instead of applying HER just to goals, it could also be applied to actions generated by a higher-level policy. For example, if the higher level asked the lower level to achieve goal A but instead goal B was achieved, we could assume that the higher level asked us to achieve goal B originally.
- **Richer value functions**. It would be interesting to extend [recent](http://proceedings.mlr.press/v37/schaul15.pdf) [research](https://openreview.net/forum?id=Skw0n-W0Z) and condition the value function on additional inputs like discount factor or success threshold and (maybe?) also substitute them in hindsight.
- **Faster information propagation**. Most off-policy [deep](https://www.nature.com/articles/nature14236) [reinforcement](https://arxiv.org/abs/1509.02971) [learning](https://arxiv.org/abs/1603.00748) [algorithms](https://arxiv.org/abs/1801.01290) use target networks to stabilize training. However, since changes need time to propagate, this will limit the speed of training and we have noticed in our experiments that it is often the most important factor determining the speed of DDPG+HER learning. It would be interesting to investigate other means of stabilizing training that do not incur such a slowdown.
- **HER + multi-step returns**. The experience used in HER is extremely off-policy since we substitute goals. This makes it hard to use it with [multi-step returns](https://arxiv.org/pdf/1703.01327.pdf). However, multi-step returns are desirable since they allow much faster propagation of information about the returns.
- **On-policy HER**. Currently, HER can only be used with off-policy algorithms since we substitute goals, making the experience extremely off-policy. However, recent state of the art algorithms like [PPO](https://arxiv.org/abs/1707.06347) exhibit very attractive stability traits. It would be interesting to investigate whether HER can be combined with such on-policy algorithms, for example by [importance sampling](https://en.wikipedia.org/wiki/Importance_sampling). There are already some [preliminary results](https://arxiv.org/abs/1711.06006) in this direction.
- **RL with very frequent actions**. Current RL algorithms are very sensitive to the frequency of taking actions which is why frame skip technique is usually used on Atari. In continuous control domains, the performance goes to zero as the frequency of taking actions goes to infinity, which is caused by two factors: inconsistent exploration and the necessity to bootstrap more times to propagate information about returns backward in time. How to design a sample-efficient RL algorithm which can retain its performance even when the frequency of taking actions goes to infinity?
- **Combine HER with recent advances in RL**. There is a vast body of recent research that improves different aspects of RL. As a start, HER could be combined with [Prioritized Experience Replay](https://arxiv.org/abs/1511.05952), [distributional RL](https://arxiv.org/abs/1707.06887), [entropy-regularized RL](https://arxiv.org/abs/1704.06440), or [reverse curriculum generation](https://arxiv.org/abs/1707.05300).

You can find additional additional information and references on these proposals and on the on the new Gym environments in our accompanying [technical report](https://arxiv.org/abs/1802.09464).

## Using goal-based environments

Introducing the notion of a “goal” requires a few backwards-compatible changes to the [existing Gym API](https://gym.openai.com/docs):

- All goal-based environments use a `gym.spaces.Dict` observation space. Environments are expected to include a desired goal, which the agent should attempt to achieve (`desired_goal`), the goal that it has currently achieved instead (`achieved_goal`), and the actual observation (`observation`), e.g. the state of the robot.
- We expose the reward function of an environment and thus allow to re-compute a reward with changed goals. This allows for HER-style algorithms, which substitute goals.

Here is a simple example that interacts with the one of the new goal-based environments and performs goal substitution:


The new goal-based environments can be used with existing Gym-compatible reinforcement learning algorithms, such as [Baselines](https://github.com/openai/baselines). Use `gym.wrappers.FlattenDictWrapper` to flatten the dict-based observation space into an array:



## Authors

Matthias Plappert, Marcin Andrychowicz, Alex Ray, Bob McGrew, Bowen Baker, Glenn Powell, Jonas Schneider, Josh Tobin, Maciek Chociej, Peter Welinder, Vikash Kumar, Wojciech Zaremba
