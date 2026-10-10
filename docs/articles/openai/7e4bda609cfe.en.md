---
vendor: openai
title: More on Dota 2
original_title: More on Dota 2
url: https://openai.com/index/more-on-dota-2
date: 2022-10-19
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 67d2abf5167f
---

August 16, 2017

Milestone

# More on Dota 2


Our Dota 2 result shows that self-play can catapult the performance of machine learning systems from far below human level to superhuman, given sufficient compute. In the span of a month, our system went from barely matching a high-ranked player to beating the top pros and has continued to improve since then. Supervised deep learning systems can only be as good as their training datasets, but in self-play systems, the available data improves automatically as the agent gets better.

[TrueSkill](https://en.wikipedia.org/wiki/TrueSkill) rating (similar to the ELO rating in chess) of our best bot over time, computed by simulating games between the bots and observing the win ratios. Improvements came from every part of the system, from adding new features to algorithmic improvements to scaling things up. The graph is surprisingly linear, meaning the team improved the bot exponentially over time.

The project’s timeline is the following. For some perspective, 15% of players are below 1.5k [MMR](https://dota.rgp.io/mmr/); 58% of players are below 3k; 99.99% are below 7.5k.

- **March 1st**: had our first classical reinforcement learning [results](https://www.youtube.com/watch?v=5Fv2c4aNS2w&feature=youtu.be) in a simple Dota environment, where a Drow Ranger learns to kite a hardcoded Earthshaker.
- **May 8th**: 1.5k MMR tester says he’s been getting better faster than the bot.
- **Early June**: beat 1.5k MMR tester
- **June 30th**: winning most games against 3k MMR tester
- **July 8th**: barely get first [win](https://www.youtube.com/watch?v=FBoUHay7XBI&feature=youtu.be&t=345) against 7.5k MMR semi-pro tester.
- **August 7th**: beat [Blitz](http://wiki.teamliquid.net/dota2/Blitz) (6.2k former pro) 3–0, [Pajkatt](http://wiki.teamliquid.net/dota2/Pajkatt) (8.5k pro) 2–1, and [CC&C](http://wiki.teamliquid.net/dota2/CC%26C) (8.9k pro) 3–0. All agreed that Sumail would figure out how to beat it.
- **August 9th**: beat Arteezy (10k pro, top player) 10–0. He says Sumail could figure out this bot.
- **August 10th**: beat Sumail (8.3k pro, top 1v1 player) 6–0, who says it’s unbeatable. Plays the Aug 9th bot, where he goes 2–1.
- **August 11th**: beat Dendi (7.3k pro, former world champion, old-school crowd favorite) 2–0. Bot has 60% win rate versus August 10th bot.

## The task

The full game is 5v5, but 1v1 also [appears](https://www.youtube.com/watch?v=KOlw9SYjr4c) in some [tournaments](http://wiki.teamliquid.net/dota2/Dota_2_Asia_Championships/2017/Solo_Tournament#Rules). Our bot played under standard tournament rules—we did not add AI-specific simplifications to 1v1.

The bot operated off the following interfaces:

- **Observations:** Bot API features, which are designed to be the same set of features that humans can see, related to heroes, creeps, courier, and the terrain near the hero. The game is partially observable.
- **Actions:** Actions accessible by the bot API, chosen at a frequency comparable to humans, including moving to a location, attacking a unit, or using an item.
- **Feedback:** The bot received incentives for winning and basic metrics like health and [last hits](https://dota2.gamepedia.com/Creep_control_techniques#Last-hitting).

We whitelisted a few dozen item builds that bots could use, and picked one for evaluation. We also separately trained the initial creep block using traditional RL techniques, as it happens before the opponent appears.

## The International

Our approach, combining small amounts of “coaching” with self-play, allowed us to massively improve our agent between the Monday and Thursday of The International. On Monday evening, Pajkatt won using an unusual item build (buying an early magic wand). We added this item build to the training whitelist.

Around 1pm on Wednesday, we tested the latest bot. The bot would lose a bunch of health in the first wave. We thought perhaps we needed to roll back, but noticed further gameplay was amazing, and the first wave behavior was baiting the other bots to be aggressive towards it. Further self-play fixed the issue, as the bot learned to counter the baiting strategy. In the meanwhile, we stitched it together with Monday’s bot for the first wave only, and completed the process twenty minutes before Arteezy showed up at 4pm.

After the Arteezy matches, we updated the creep block model, which increased TrueSkill by one point. Further training before Sumail’s match on Thursday increased TrueSkill by two points. Sumail pointed out that the bot had learned to cast razes out of the enemy’s vision. This was due to a mechanic we hadn’t known about: abilities cast outside of the enemy’s vision prevent the enemy from gaining a wand charge.

Arteezy also played a match against our 7.5k semi-pro tester. Arteezy was winning the whole game, but our tester still managed to surprise him with a strategy he’d learned from the bot. Arteezy remarked afterwards that this was a strategy that Paparazi had used against him once and was not commonly practiced.

Pajkatt beating Monday’s bot. Note he baits the bot into engaging, and uses regeneration (faerie fires and a magic wand) to heal up. The bot is generally very good at deciding who will win a fight, but it’s never played against someone with early wand before.

## Bot exploits

Though Sumail called the bot “unbeatable”, it can still be confused in situations very different from what it’s seen. We set up the bot at a LAN event at The International, where players played over 1,000 games to beat the bot by any means possible.

The successful exploits fell into three archetypes:

- **Creep pulling**: it’s possible to repeatedly attract the lane creeps into chasing you right when they spawn (between the bot’s tier 2 and tier 3 towers). You end up with dozens of creeps chasing you around the map, and eventually the bot’s tower dies via attrition.
- **Orb of venom + wind lace**: this gives you a big movement speed advantage over the bot at level 1 and allows for a quick first blood. You need to exploit this head start to kill the bot one more time.
- **Level 1 raze**: this requires a lot of skill, but several 6–7k MMR players were able to kill the bot at level 1 by successfully hitting 3–5 razes in a short span of time.

Fixing these issues for 1v1 would be similar to fixing the Pajkatt bug. But for 5v5, such issues aren’t exploits at all, and we’ll need a system which can handle totally weird and wacky situations it’s never seen.

## Infrastructure

We’re not ready to talk about agent internals—the team is focused on solving 5v5 first.

The first step in the project was figuring out how to run Dota 2 in the cloud on a physical GPU. The game gave an obscure error message on GPU cloud instances. But when starting it on Greg’s personal GPU desktop (which is the desktop brought onstage during the show), we noticed that Dota booted when the monitor was plugged in, but gave the same error message when unplugged. So we configured our cloud GPU instances to pretend there was a physical monitor attached.

Dota didn’t support custom dedicated servers at the time, meaning that running scalably and without a GPU was possible only with very slow software rendering. We then created a shim to stub out most OpenGL calls, except the ones needed to boot.

At the same time, we wrote a scripted bot—we needed a baseline for comparison (especially because the builtin bots don’t work well on 1v1) and to understand all the semantics of the [bot API](https://developer.valvesoftware.com/wiki/Dota_Bot_Scripting). The scripted bot reaches 70 last hits in ten minutes on an empty lane, but still loses to reasonable humans. Our current best 1v1 bot reaches more like 97 (it destroys the tower before then, so we can only extrapolate), and the theoretical maximum is 101.

Bot playing versus [SirActionSlacks](http://wiki.teamliquid.net/dota2/SirActionSlacks). The strategy of distracting the bot with a courier rush did not work.

## 5v5

1v1 is complicated, but 5v5 is an ocean of complexity. We know we’ll need to further push the limits of AI in order to solve it.

One well-established place to start is with behavioral cloning. Dota has about a million public matches a day. The replays for these matches are stored on Valve’s servers for two weeks. We’ve been downloading every expert-level replay since last November, and have amassed a dataset of 5.8M games (each game is about 45 minutes with 10 humans). We use [OpenDota](https://www.opendota.com/) to discover these replays, and are donating $12k (10 years of their fundraising goal) to support the project.

We have many more ideas, and are [hiring⁠](https://openai.com/careers/) engineers (must be intrigued by machine learning, but need not be an expert) and researchers to help us make this happen. We thank Microsoft Azure and Valve for their support in this endeavor.


## Author
