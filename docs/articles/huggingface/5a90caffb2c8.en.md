---
vendor: huggingface
title: ToyBlocks: A controlled world for robot learning and evaluation
original_title: ToyBlocks: A controlled world for robot learning and evaluation
url: https://huggingface.co/blog/allenai/toyblocks
date: 2026-11-06
lang: en
captured: 2026-11-07
extractor: readability-v1
status: ok
body_sha: 1325b1504c9f
---

[ Back to Articles](https://huggingface.co/blog)

# ToyBlocks: A controlled world for robot learning and evaluation

Enterprise  Article

Published November 6, 2026


5

- [![](https://huggingface.co/avatars/ab7fc92bae0354165d3f9890ac7f5b0b.svg)](https://huggingface.co/wookute221)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/XcLxZc6CL6VO7tOlh0T0g.jpeg)](https://huggingface.co/SmokeyPete)
- [![](https://huggingface.co/avatars/35af30f8a3713e3eda81ac4b9be515f5.svg)](https://huggingface.co/arahul2k2)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/DPzSLPCg9RvVBvkD3Mcys.png)](https://huggingface.co/rapidum)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/67953e11098348e24ae7f316/ZNT-1c2NOyhugYrzK5Vyf.png)](https://huggingface.co/sebast242)

[![Kyle Wiggers's avatar](https://huggingface.co/avatars/9c2a0976ea68fe021a4191d3d4c5454b.svg)](https://huggingface.co/Ai2Comms)

Kyle Wiggers

Ai2Comms

[![Ai2's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/652db071b62cf1f8463221e2/CxxwFiaomTa1MCX_B7-pT.png)](https://huggingface.co/allenai) [allenai](https://huggingface.co/allenai)

💻 [Code](https://github.com/allenai/ToyBlocks) | 📊 [Data](https://huggingface.co/datasets/allenai/toyblocks-data) | 🤖 [Models](https://huggingface.co/collections/allenai/toyblocks) | 📖 [Documentation](https://allenai.github.io/ToyBlocks/docs/user_guide/index.html)

[![ToyBlocks isometric robot illustration](https://www.datocms-assets.com/64837/1793826687-david-thumbnail-download-1.jpg)](https://www.datocms-assets.com/64837/1793826687-david-thumbnail-download-1.jpg)

Robots are learning to fold laundry, sort parts, and handle unfamiliar objects. But those demonstrations are often rather narrow and don't explain what a robot has learned or why it fails.

To study a complex system, scientists often begin with a small, controlled environment, such as a petri dish or terrarium, where they can vary conditions and observe the effects. Robotics needs environments that make this kind of investigation possible—researchers should be able to change the training data or model design, repeat a test, and trace the cause of a failure.

Today we're introducing a framework for creating these environments; we call them FoundationWorlds. Each pairs a controlled, simulated world targeted at studying robotics in a specific environment with tools for automatically generating tasks and training demonstrations, as well as metrics for measuring a robot's behavior over time. Together, they provide a setting for studying questions such as how models improve as more training data becomes available, and how to best combine high-level reasoning with precise physical control.

Our first foundation world is [ToyBlocks](https://github.com/allenai/ToyBlocks): an open simulation framework built around a robot arm and blocks on a tabletop. The setting is deliberately simple, but the robot must still reason about how the blocks interact and how to arrange them while pushing, flipping, and stacking.

ToyBlocks automatically generates demonstrations, which are recordings of a robot completing tasks in simulation, without requiring time-consuming teleoperation, in which a person remotely controls the robot. Researchers can easily vary these training experiences. For example, a team could generate more pushing or flipping demonstrations, then evaluate performance on tasks kept out of training.

Starting with ToyBlocks as our first FoundationWorld, we aim to extend the approach to increasingly complex environments.

## How ToyBlocks works

Building on our earlier work in open robot learning, including [MolmoAct 2](https://allenai.org/blog/molmoact2), [MolmoBot](https://allenai.org/blog/molmobot-robot-manipulation), and [MolmoSpaces](https://allenai.org/blog/molmospaces), ToyBlocks gives researchers a way to study robotics questions in a deliberately constrained domain.

As a FoundationWorld, ToyBlocks is designed around four requirements: (1) realistic physics and appearance, (2) automatic generation of tasks and demonstrations at scale, (3) challenges that combine reasoning with dexterity, and (4) broad coverage of the tasks possible within a domain.

Open-ended domains require modeling a wide range of objects and interactions, making it infeasible to fulfill all these requirements. ToyBlocks’ narrow scope, on the other hand, makes it possible to fulfill them all.

Within ToyBlocks' smaller setting, researchers can work toward investigating how a robot can learn to perform any reasonable task while being confident that the simulated arm and blocks behave very similarly to their physical counterparts.

[![Physical robot gripper above wooden blocks in the ToyBlocks setup](https://cdn-uploads.huggingface.co/production/uploads/638e39b249de7ae552d977b5/ov2i4rZoAkJw4z9FBaGfm.jpeg)](https://cdn-uploads.huggingface.co/production/uploads/638e39b249de7ae552d977b5/ov2i4rZoAkJw4z9FBaGfm.jpeg)

*A physical robot gripper above wooden blocks in the ToyBlocks setup.*

ToyBlocks is not just about picking and stacking blocks: pictures and letters on the blocks' faces allow for searching, sorting, and arranging tasks. A robot may need to turn a block to see a hidden face before deciding where it belongs. Domain randomization – varying block size, table height, and other physical properties from scene to scene – tests how well models generalize as the geometry changes.

[![ToyBlocks framework architecture](https://www.datocms-assets.com/64837/1793917318-toyblocks-framework-current.png)](https://www.datocms-assets.com/64837/1793917318-toyblocks-framework-current.png)

*ToyBlocks automatically generates skills (behaviors for short tasks) and task demonstrations that can be used to train models or adapt previously trained models through additional training (fine-tuning). High-level reasoning models decide what to do; low-level action models control the robot’s movements. The framework can also be used to easily design experiments and validate hypotheses.*

ToyBlocks uses reinforcement learning (RL) and motion planning, which computes how the robot should move, to generate skills for short-horizon tasks, which involve brief sequences of actions. Skill training takes place in Isaac Lab, Nvidia's open-source framework for robot learning in simulation. Through trial and error, these policies – models that choose the robot’s actions – learn non-prehensile skills such as pushing a block across the table or flipping it onto another face without picking it up. Skill generation can draw on privileged information – values the simulator can supply directly but a real robot cannot, such as a block's exact position and orientation – instead of estimating it from camera images. This enables the automatic generation of skills that would require teleoperation in the real world.

To generate demonstration data, a task-and-motion planner (TAMP) automatically selects and sequences the skills needed to solve a task and plans the robot’s movements between them. Running each plan in simulation produces a dataset of recorded demonstrations along with labels describing which task or skill the robot performs. ToyBlocks scales data generation through generating and executing hundreds of such plans in parallel on a single graphics processing unit (GPU), reaching up to 24 times real-time performance.

Acting from sensor observations adds a perception problem: a model has to estimate a block’s pose – its position and orientation – which the simulator could supply directly. To reflect real-world conditions, ToyBlocks trains models that map raw sensor observations to actions.

*Execution of Molmo 2 (a high-level model) and ManiFlow (a low-level model) trained in ToyBlocks. Molmo 2 selects skills such as rotation and flipping, indicating the relevant block via a pointing interface, while ManiFlow controls the simulated arm to execute the commanded skills.*

ToyBlocks' controllable data generator lets users create training mixtures that emphasize particular skills or fill gaps in existing datasets. Researchers can study how much data a model needs and which experiences help it generalize to unseen tasks. For example, they could test whether adding rotation and pick-and-place demonstrations improves flipping, or vary the balance of examples inside and outside a defined workspace region—evaluating their choices on tasks kept out of training. Importantly, evaluation of trained models generates metrics beyond success rates; it provides information such as execution speeds, forces exerted on objects, and task progress measured via the same specifications used by the planning module.

A webpage interface lets users connect Claude – or another frontier model – and use natural language to instruct the robot or try tasks, offering a way to explore how a model plans and acts without needing robotics expertise.

## Research building on ToyBlocks

The evaluations below use ToyBlocks to study how training data and methods affect performance, spatial reasoning, generalization to new letters and block appearances, multi-step planning, transfer to physical robots, and frontier models that act through tools. Users can easily design their own tasks and measures to investigate other questions—for example, whether a model performs better when it selects objects by pointing or by issuing text commands such as "pick the yellow block."

### Low-level action models: VLA spatial generalization

Low-level action models, such as vision-language-action models (VLAs), map language instructions and visual observations to robot actions.

The premise of VLAs is that, by pretraining on large-scale datasets, they can rapidly generalize to different scenarios or a specific workspace. However, evidence on how well these action models generalize remains conflicting. Some studies report that these action models are brittle to changes in inputs, such as different object layouts and lighting, whereas others show that VLAs generalize well. We argue that these studies often rely on real-world datasets with limited flexibility in spatial variations. ToyBlocks enables us to test how well action models generalize in a simple, easily reproducible setting with meaningful task-space diversity.

We design generalization tests that vary the skill sequences needed to complete an instruction, the letters or colors on the blocks, and the number of blocks in a scene. A stacking study can withhold four-block stacks from training, then test whether a model can combine familiar movements to build them. Workspace studies distinguish performance at new positions within a training region from performance beyond its boundaries, where the model has to extrapolate. We illustrate the study setup and findings below.

*We consider four tasks: Stack, Unstack, Flip, and Rotate. For these tasks, we study interpolation (new configurations within the training range) and extrapolation (configurations beyond that range). For example, we evaluate generalization by training on scenarios where objects spawn only in the left region (green) and testing on the right region (orange), or by training on stack heights of 2 and 5 blocks and testing on heights 3 and 4.*

[![Spatial generalization results](https://www.datocms-assets.com/64837/1793904303-toyblocks-visual-08-ai2.png)](https://www.datocms-assets.com/64837/1793904303-toyblocks-visual-08-ai2.png)

*Spatial generalization studies for VLA models (results based on [ManiFlow](https://arxiv.org/abs/2509.01819), [π0.5](https://arxiv.org/abs/2504.16054), and MolmoAct 2). Despite large-scale pretraining, these popular action models generalize poorly in the initial results. We improve generalization and analyze the contribution of each technique. The chart’s LoRA label stands for low-rank adaptation, a method for fine-tuning a model with a small set of trainable weight updates. We believe action model generalization remains far from solved; ToyBlocks provides a valuable testbed for systematically exploring generalization techniques.*

### High-level reasoning: vision-language models

Long-horizon tasks, which require many steps, allow us to measure how well models can plan a sequence of actions to solve them. Our framework enables us to create such long-horizon tasks, and create oracles – reference components that provide correct plans or actions – at both the high and low levels. This allows us to isolate whether the high-level planning or low-level execution failed when a model fails at a task. An example long-horizon task might be to spell “Ai2” with a block stack; because the letters may not be immediately visible, the agent must first choose actions that reveal information, and then plan and execute a sequence of actions to build the stack.

We evaluate hierarchical models with explicit high-level planning and low-level execution models. In this instance, we choose Molmo 2, a vision-language model (VLM), as the high-level planner, and ManiFlow as the low-level policy. Molmo 2 chooses the skill to execute and the block to execute it on, while the low-level model executes the instruction. We train low-level models such as ManiFlow to pause after completing the execution and query the high-level model for the next instruction. We evaluate the model’s planning abilities on three scenarios of increasing difficulty. The easiest scenario initializes with each character upright and facing the camera. The medium scenario has characters that may not be upright, and the hardest scenario contains characters that are not visible at the start of the episode.

[![Molmo 2 and ManiFlow block spelling results](https://www.datocms-assets.com/64837/1793904303-toyblocks-visual-09-ai2.png)](https://www.datocms-assets.com/64837/1793904303-toyblocks-visual-09-ai2.png)

*Success rates on three-letter block-spelling tasks using Molmo 2 as the high-level reasoning model and either ManiFlow or a motion planner for low-level manipulation. An example task is “Stack Ai2”. Molmo 2 and ManiFlow are trained on ToyBlocks and evaluated across three difficulty settings and two generalization conditions.*

### High-level reasoning: agentic systems

Our experiments with agentic systems test how frontier models plan and act through tool calls. We study three settings using Claude Opus 5.5. In the search-and-spell setting, we expose ToyBlocks skills through the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro), a standard for connecting AI applications to tools. The agent sees the scene through camera images, calls skills such as pick, flip, or rotate by pointing at a pixel, and decides when to search, build, or declare the task complete or impossible. The same MCP tools can execute either the scripted skills that generate ToyBlocks demonstrations (motion-planned pick and place, plus RL-based rotate and flip) or learned ManiFlow skills. ToyBlocks includes the framework behind these experiments, which also powers the natural-language web interface described earlier.

*A frontier model (Claude Fable 5.1) controls a robot in a ToyBlocks world to search for and stack blocks into a tower spelling “Ai2.” During the episode, the agent muses, “I need to figure out whether pick-and-place naturally straightens orientation or if I need to correct it manually… I have 63 calls left, plenty to run a controlled test” (0:06). The agent later hypothesizes: “…maybe the gripper’s yaw is radial—pointing from the robot base toward the block” (0:15) and eventually confirms this hypothesis (0:26) before constructing the three-block tower, but the ‘A’ is sideways (1:11). Surprisingly, current frontier models often make similar perceptual errors (see the next figure), despite their impressive planning, spatial reasoning, and search capabilities.*

For classical planning, the agent (our system using Claude Opus 5.5 to plan and choose actions) solves all 30 of a group of block-stacking tasks similar to ones that frontier models struggled with [a few years ago](https://proceedings.neurips.cc/paper_files/paper/2023/hash/7a92bcdede88c7afd108072faf5485c8-Abstract-Datasets_and_Benchmarks.html), using text descriptions. It also solves 30 out of 30 while repeatedly observing camera images and choosing its next action in a closed loop.

In the search-and-spell setting, the agent had to generate stacks spelling out three-letter words. It had to find the blocks with the corresponding letters among up to eight blocks in the scene. Importantly, 50% of the scenes did not have blocks with all the required letters, rendering the task infeasible. In this case, we required the agent to state that the task is infeasible. We found that in this experiment, the agent was able to successfully solve or correctly declare infeasible 63% of the tasks. Errors were mostly caused by the agent confusing letters with look-alike letters (13%) or choosing an incorrect orientation for a letter in a stack (15%).

Our results also show that the agent was able to solve the task more efficiently when the blocks had semantic regularities, or patterns, taking advantage of such patterns to reason about occluded faces. For instance, in most of the infeasible scenes, when the blocks had no patterns, the agent correctly looked at all the blocks’ faces before declaring infeasibility, whereas it was able to declare infeasibility significantly faster when the blocks had semantic patterns.

Our third experimental setting asks whether an agent can learn how its skills behave, using experiments as a scientist would. When a skill behaves unexpectedly, the agent forms a hypothesis, designs a small test, and revises its understanding from the result. We expand on this idea by having an agent run its own experiments and write its own [skill descriptions based on what it finds](https://openreview.net/forum?id=gxEC7M0oZj). These learned descriptions raise success rates from 24% with the default descriptions to 63%, outperforming the 36% achieved with descriptions written by a human expert.

[![Search and Spell outcomes and exposed faces](https://www.datocms-assets.com/64837/1793911236-toyblocks-visual-10a-corrected.png)](https://www.datocms-assets.com/64837/1793911236-toyblocks-visual-10a-corrected.png)

*Share of letter-block faces the agent had exposed by the end of each “search and spell” episode (bars averaged over 20 episodes; one marker per episode, styled by outcome). In a feasible task every letter of the three-letter target word is present; in an infeasible task, one letter is missing and the agent should say so. Each patterned block carries uppercase and lowercase instances of a letter, plus images that begin with the letter (e.g., A-block: apple, ant, A, 1, airplane, a); an unpatterned block’s six faces are randomized and unrelated. Correct: the tower spelled the word, or for infeasible tasks, the agent correctly declared the task impossible. Letter rotated or look-alike: the agent built the tower, but a letter was turned or a look-alike substituted, including five infeasible tasks declared solved with a look-alike in the missing letter’s place. Block fell out of reach; reported: a needed block was pushed out of the arm’s reach, so the agent reported that its task had become impossible. No report: the agent used up its motor-skill budget and stopped without claiming either outcome. With patterned blocks, the agent finishes having seen fewer faces, because it can infer what hidden faces must depict rather than checking every one.*

### Action-conditioned world models as simulators

Action-conditioned world models are trained to predict how a scene changes in response to a robot’s actions. Using them as an alternative to model-based simulators for training and evaluating robot policies is an active area of research. How well they serve this purpose depends on how accurately they predict physical interactions, which is hard to measure without knowing the true state of the scene. ToyBlocks provides this ground truth – the actual simulated scene state – enabling highly controlled tests of how recently developed world models perform in low-level object manipulation. Here, the arm’s end effector is its gripper.

Specifically, we tested whether action-conditioned world models are capable of predicting the motions of blocks or the outcomes of skill executions after being trained on example executions. To do so, we chose four different skills (pick-and-place, flip, rotate, and a mixed task) and generated 900 trajectories – sequences of robot states and actions over time – for each skill. 50% of these trajectories were successful demonstrations of the skill, and 50% were unsuccessful because of small changes to spatial configurations. With equal numbers of successful and unsuccessful executions, a model that always predicts success would be correct only half the time. The models were fine-tuned on these demonstrations and then tested on their ability to predict the outcome of action sequences of the same skills.

[![World model comparison](https://www.datocms-assets.com/64837/1793904303-toyblocks-visual-11-ai2.png)](https://www.datocms-assets.com/64837/1793904303-toyblocks-visual-11-ai2.png)

*We find that Wan 2.2 predicts block motion and task outcomes most accurately. Astra tracks the gripper well but struggles to simulate contact. LeWM is fast and more accurate over short interaction segments, though it drifts over full trajectories. In additional experiments, we also showed that models that score higher on pose and success prediction also produce better training data: adding 100 model-generated trajectories (rollouts) from the best video-generation model raises a policy’s success in an unseen region from 19% to 78%.*

We tested three types of models: a video prediction model with 5 billion parameters ([Wan 2.2](https://arxiv.org/abs/2503.20314)), [an agentic model that created its own physics simulator tuned to match the demonstration data (Astra)](https://openai.com/index/gpt-6-astra/), and [a latent world model (LeWM)](https://arxiv.org/abs/2603.19312). During testing, each trained model has to predict future images, simulator states, or latent states (learned internal representations), respectively, based on an initial image and a sequence of actions. For full trajectories, models use the initial image as the only observed image, along with the action sequence. For short interaction segments – a single pick, place, flip, or rotate – models start from the real image immediately before that interaction. Full trajectories show how errors accumulate over long horizons, while interaction segments isolate a single interaction, such as the gripper making contact with a block, and show how well the model predicts it. To compare models fairly, we probe each model’s predictions, reading out where it expects the blocks and gripper to be at different points in the trajectory and whether it expects the task to succeed at the end.

### Real-world experiments with high- and low-level models

Sim-to-real evaluations test policies trained in simulation on physical robots performing block manipulation tasks. By comparing simulation and real-world execution, we assess whether behaviors and failure patterns observed in simulation provide meaningful indications of real-world performance. For example, researchers can evaluate individual skills and their composition in longer-horizon tasks to identify where failures arise and whether these patterns carry over to physical deployments.

We test whether the models trained entirely on ToyBlocks simulation datasets can be deployed in the real world zero-shot, without training on real-world examples. We evaluate ManiFlow and each low-level skill (pick, place, flip, and rotate) individually. We test whether the hierarchical system (Molmo 2 + ManiFlow) can complete long-horizon three-block spelling tasks requiring sequences of these actions. Real-world experiments use a Franka FR3 arm with a Robotiq gripper across thirty scene configurations. Each scene contains 4–10 blocks seen during training. An episode is successful only if the relevant blocks are moved to target poses without collisions. If the operator intervenes to stop the robot due to an unsafe motion during an episode, it is marked as a failure.

ManiFlow’s atomic-skill success rates were similar in simulation and the real world (80.0% and 81.1%). The hierarchical Molmo 2 + ManiFlow system succeeded in 55.5% of simulated episodes (111/200) and 50.0% of real-world episodes (15/30); further trials are needed to establish statistical confidence across tasks.

[![Simulation and real-world success rates](https://www.datocms-assets.com/64837/1793919269-toyblocks-visual-12a-30-trials.png)](https://www.datocms-assets.com/64837/1793919269-toyblocks-visual-12a-30-trials.png)

*Success rates of the ManiFlow low-level model and the hierarchical Molmo 2–ManiFlow system in simulation and the real world. For ManiFlow, the total count represents individual skill executions (pick, place, flip, and rotate), whereas for Molmo 2–ManiFlow, it represents block-spelling task episodes. The Molmo 2–ManiFlow evaluations use the easiest scene configuration defined in the simulation evaluation, with block characters visible and upright.*

*Side-by-side real-world and simulated block-stacking executions using the same high-level planner. Pink rings mark the planner’s target point for each skill. The scenes use different block labels, and simulation playback is retimed to align grasps and releases with the real robot.*

To transfer Molmo 2 and ManiFlow – both trained exclusively on ToyBlocks data – to a physical robot, we address the differences between simulation and reality in three stages.

Before data generation, we perform system identification by tuning simulated robot parameters, including joint friction and armature (the motor and gearbox inertia reflected at the joint), to match real-robot trajectories. During data generation, we randomize physical properties (object size, friction, and table height) and visual properties (lighting, backgrounds, materials, and camera parameters). At inference time, observations are captured using a front-facing ZED camera and a wrist-mounted ZED Mini. For policies that use depth images, we generate clean depth maps, which estimate distance at each pixel, from paired red-green-blue (RGB) camera images using [FastFoundationStereo](https://arxiv.org/abs/2512.11130), rather than relying on noisy depth sensor measurements.

[![The physical ToyBlocks setup with a robot arm, wooden blocks, and a camera](https://www.datocms-assets.com/64837/1793811059-image2.jpg?ts=ae95e598)](https://www.datocms-assets.com/64837/1793811059-image2.jpg?ts=ae95e598)

*The physical ToyBlocks setup: a robot arm, wooden blocks, and a camera.*

## Opening the tools for further research

ToyBlocks connects data generation, training, and evaluation in one controlled setting, so researchers can investigate how robots learn over time and test how changes to a model or its training data affect robot behavior. We’re releasing simulation assets, procedural task and demonstration generators, automatically generated demonstrations, two trained models showcasing what the framework can do (one based on [Molmo 2](https://huggingface.co/allenai/Molmo2-4B-tb) and one based on [ManiFlow](https://huggingface.co/allenai/maniflow-tb)), training code, and evaluation code and validation sets. This allows other teams to build their own training mixtures and investigate failure modes beyond those covered in our initial experiments.

Our initial data release is a proof point with 85,336 long-horizon demonstrations, each comprising about 6–12 skill demonstrations, depending on the set. The initial datasets cover nearly 1,600 hours of robot execution data and 144 million frames. In a few weeks, we're targeting a second release with a larger-scale dataset, more skills, and more comprehensive benchmarking. We’ll also add fully integrated RL training capability that is not contained in the current package.

Other directions for ToyBlocks include bimanual (two-arm) manipulation and dexterous robot hands, equipped with force and touch sensors for studying motion and tasks that involve frequent physical contact. We're also exploring play with unstructured piles of blocks as a way to collect data and study how new behaviors and tasks might emerge through interaction.

*Future direction: RL-based pile manipulation.*

*Future direction: bimanual block manipulation.*

With ToyBlocks, we want to advance the science of robot learning toward a future where robots can reliably apply what they've learned to unfamiliar tasks and environments. We encourage the research community to explore ToyBlocks for their own investigations and even as a basis to build their own FoundationWorlds.

## Models mentioned in this article 2

## Datasets mentioned in this article 1

## Collections mentioned in this article 1

More from this author

## StateBench: Testing how language models track state changes over long documents

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/652db071b62cf1f8463221e2/CxxwFiaomTa1MCX_B7-pT.png)

18

November 3, 2026

## Can we trust LLMs to judge whether a research idea is novel?

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/652db071b62cf1f8463221e2/CxxwFiaomTa1MCX_B7-pT.png)

18

October 27, 2026

### Community

![](https://huggingface.co/avatars/26fa040c7f334785b26ae42de24ab4dc.svg)

Entmarch

about 10 hours ago

I love the concept, id like to see practical applications how can we encorporate AI into PLCs and OBD systems retrofit extant applications niche revenue

![](https://huggingface.co/avatars/ab7fc92bae0354165d3f9890ac7f5b0b.svg)

wookute221

about 7 hours ago

selona I love the concept, id like to see practical applications how can we encorporate AI into PLCs and OBD systems retrofit extant applications niche revenue

Upload images, audio, and videos by dragging in the text input, pasting, or clicking here.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fallenai%2Ftoyblocks) or [log in](https://huggingface.co/login?next=%2Fblog%2Fallenai%2Ftoyblocks) to comment


5

- [![](https://huggingface.co/avatars/ab7fc92bae0354165d3f9890ac7f5b0b.svg)](https://huggingface.co/wookute221)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/XcLxZc6CL6VO7tOlh0T0g.jpeg)](https://huggingface.co/SmokeyPete)
- [![](https://huggingface.co/avatars/35af30f8a3713e3eda81ac4b9be515f5.svg)](https://huggingface.co/arahul2k2)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/DPzSLPCg9RvVBvkD3Mcys.png)](https://huggingface.co/rapidum)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/67953e11098348e24ae7f316/ZNT-1c2NOyhugYrzK5Vyf.png)](https://huggingface.co/sebast242)

## Models mentioned in this article 2

## Datasets mentioned in this article 1

## Collections mentioned in this article 1
