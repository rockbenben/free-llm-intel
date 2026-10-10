---
vendor: openai
title: Spinning Up in Deep RL: Workshop review
original_title: Spinning Up in Deep RL: Workshop review
url: https://openai.com/index/spinning-up-in-deep-rl-workshop-review
date: 2020-06-20
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 449ddf569460
---

OpenAI

February 26, 2019

Company

# Spinning Up in Deep RL: Workshop review

On February 2, we held our first Spinning Up Workshop as part of our new education initiative at OpenAI.

Loading…

We hosted ~90 people at our office and engaged nearly 300 more through our livestream. Participants came from a wide range of backgrounds, including academia, software engineering, data science, ML engineering, medicine, and education. This workshop built off our [Spinning Up in Deep RL⁠](https://openai.com/index/spinning-up-in-deep-rl/) resource package and took a deeper dive into RL algorithm design, robotics, and building safe AI systems.

## Building educational tools

One of the goals for education at OpenAI is to help people develop the skills needed to participate in research and development in AI—especially in deep RL, a core area of research at OpenAI. From our experience working with [Scholars](https://blog.openai.com/openai-scholars-2018-final-projects/) and [Fellows](https://blog.openai.com/openai-summer-fellows-2018/), we’ve found that the key ingredients for skill development are:

- a flexible curriculum that includes core material and a review of research frontiers,
- mentorship and discussions with experts, and
- having the students work on projects that are at the right level to help them grow.

The challenge for education at OpenAI is to figure out how to deliver these at scale. While sharing a curriculum at scale is relatively easy, it isn’t obvious how to scale up mentorship and guidance on projects. Our working theory is that workshops might help us do just that. Our first Spinning Up workshop has given us several positive signs that this is a useful direction, and we’re excited to share what we learned.

## The crowd

We hosted around 90 people at our office and involved nearly 300 more through our livestream. Our guests came from a wide range of backgrounds, including academic research, software engineering, data science, ML engineering, medicine, and education. The level of ML experience varied quite significantly across the group, from “almost none” to “built their own Dota bot!”

More than 500 people, from all around the world, applied to participate in this workshop. Although we sadly couldn’t invite everyone to this one because of space constraints, we want to continue engaging the community with future events.

## The talks

The workshop kicked off with three hours of talks. To start us off, [Joshua Achiam](https://twitter.com/jachiam0) laid out the conceptual foundations of reinforcement learning and gave an overview of different kinds of RL algorithms. If you’d like to study this material, check out [Spinning Up in Deep RL](https://blog.openai.com/spinning-up-in-deep-rl/).

Matthias Plappert presented on OpenAI’s [recent](https://blog.openai.com/learning-dexterity/) [work](https://arxiv.org/abs/1808.00177) training a dexterous robot hand in simulation to manipulate objects in the real world. Domain randomization, recurrent neural networks, and large-scale distributed training were necessary ingredients in bridging the “sim2real” gap for this task.

Dario Amodei, the leader of the Safety Team at OpenAI, presented an overview of problems in AI safety and [recent](https://blog.openai.com/amplifying-ai-training/) [work](https://blog.openai.com/debate/) in this space. He described the central safety problem: the fact that correctly specifying agent behavior is hard! It is easy to inadvertently give agents incentives to perform different behavior than what you would have wanted, and when agents are very powerful, this could be dangerous. Dario also described [work](https://blog.openai.com/deep-reinforcement-learning-from-human-preferences/) that OpenAI and collaborators at DeepMind have done to address this issue, in which reward functions are learned from human preferences instead of designed.

## The afternoon

The workshop continued into the afternoon with a semi-structured program of hacking and breakout sessions. Participants were able to seek guidance on project ideas and research tips from our slate of volunteers, which included [Amanda Askell](https://twitter.com/AmandaAskell), [Alex Ray](https://twitter.com/machinaut), [Daniel Ziegler](https://www.linkedin.com/in/daniel-ziegler-b4b61882), [Dylan Hadfield-Menell](https://twitter.com/dhadfieldmenell), [Ethan Knight](https://github.com/hyperdo?tab=repositories), [Karl Cobbe](https://twitter.com/karlcobbe), [Matthias Plappert](https://twitter.com/mplappert), and [Sam McCandlish](https://www.linkedin.com/in/sam-mccandlish).

The breakout sessions turned out to be the main highlight of the afternoon. Whereas the morning talks covered the conceptual foundations of RL, the breakout sessions were designed to help participants boost their implementation and research skills.

In the first session, Karl Cobbe gave an introduction to [TensorFlow](https://www.tensorflow.org/), a key library used in deep learning research. In the second session, “Writing DQN Together,” Daniel Ziegler led participants step-by-step through the process of implementing a deep RL algorithm. In the third session, “Advanced RL Q&A,” Joshua Achiam described recent research frontiers in RL and took audience questions about doing RL research.

## Our takeaways

This was our first experiment with the workshop format, and we were generally pleased with the outcome. In particular, we found it quite gratifying to work directly with such a capable and enthusiastic group of participants. The experience, along with feedback from the group, gave us a good sense of what to keep and what to change for future workshops.

**What worked**: We asked our participants what their highlights were, and these responses are a fairly representative sample:

> “Learning A TON in a very safe, friendly environment where everyone was mainly on the same level in terms of learning.”

> “I thought the ability to get one-on-one help and to take on some ‘paired programming’-like time with folks who really know what they’re doing was incredibly helpful. The enthusiasm of the volunteers was also very high, and I felt very encouraged to ask for help.”

Responses like these gave us a sense that the workshop format shined on delivering “mentorship and discussions with experts.”

**What could be improved**: We asked our participants what they thought we could have done differently to enhance their experience, and received responses like:

> “I would’ve liked a presentation section of potential projects that we could pursue based on our experience level.”

> “Extend the workshop to two days.”

Many participants felt like they either weren’t sure what to work on during the hackathon, or didn’t have enough time to make significant progress on their hacking project.

We think this kind of feedback is a good indicator that the 1-day workshop format isn’t enough to “have the students work on projects that are at the right level to help them grow” in RL. In the future, we’ll consider running longer events so we can meet that goal. This feedback also suggests that we should do more to create “shovel-ready” RL projects that participants can jump right in to.

**What else?** Aside from the technical content of the workshop, creating a supportive and inclusive environment was top-of-mind for us, and participants told us this was important for their experience. One piece of feedback read:

> “This is the first non-female exclusive social event I’ve been to in Silicon Valley with ~50% women in the room. It was so shocking that I thought I was in the wrong room in the beginning. It was noticeably easier to socialize as a result of the gender balance, so thank you for that.”

## What’s next

OpenAI’s [Charter](https://blog.openai.com/openai-charter/) gives us a mandate “to create a global community working together to address AGI’s global challenges,” and we’ll continue developing education at OpenAI to help serve that goal. This includes more work on resources like [Spinning Up in Deep RL](https://spinningup.openai.com/en/latest/) and more events like this Spinning Up Workshop. We are currently planning a second workshop with [CHAI at Berkeley](https://humancompatible.ai/), which we expect to formally announce soon.

If you would like to help us do research on RL or teach people about AI, please get in touch! [We’re hiring⁠](https://openai.com/careers/).

*Thanks to Maddie Hall and Loren Kwan for co-organizing the event, to Ian Atha for livestreaming and recording the lectures, as well as helping participants with Python and Tensorflow issues, and to* [*Blake Tucker*](https://www.blaketucker.com/) *for filming and photography!*

- [Events](https://openai.com/news/?tags=events)
- [2019](https://openai.com/news/?tags=2019)

## Author

Joshua Achiam

## Related articles

View all

Procgen and MineRL Competitions

CompanyJun 20, 2020

OpenAI Robotics Symposium 2019

CompanyJun 5, 2019

OpenAI Five Finals

CompanyMar 26, 2019
