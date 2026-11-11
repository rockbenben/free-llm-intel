---
vendor: huggingface
title: BotPsy: On-Device Personal Assistant with a Sub-Billion-Parameter Agentic Language Model
original_title: BotPsy: On-Device Personal Assistant with a Sub-Billion-Parameter Agentic Language Model
url: https://huggingface.co/blog/qvac/botpsy
date: 2026-11-11
lang: en
captured: 2026-11-11
extractor: readability-v1
status: ok
body_sha: ecce79318726
---

[ Back to Articles](https://huggingface.co/blog)

# BotPsy: On-Device Personal Assistant with a Sub-Billion-Parameter Agentic Language Model

Team Article

Published November 11, 2026


2

- [![](https://huggingface.co/avatars/0532faec32a12d143b5329642a709b0f.svg)](https://huggingface.co/joooon)
- [![](https://huggingface.co/avatars/30ff51594b6454a1eced9a0d472d2ec1.svg)](https://huggingface.co/milangritta)

[![Milan Gritta's avatar](https://huggingface.co/avatars/30ff51594b6454a1eced9a0d472d2ec1.svg)](https://huggingface.co/milangritta)

Milan Gritta

milangritta

[![QVAC's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)](https://huggingface.co/qvac) [qvac](https://huggingface.co/qvac)

[![Jihye Back's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/61a623353aff6ad7c083e882/biFOfePqURZW0snJHfy_Y.jpeg)](https://huggingface.co/happy-jihye)

Jihye Back

happy-jihye

[![QVAC's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)](https://huggingface.co/qvac) [qvac](https://huggingface.co/qvac)

[![JinUk, Cho's avatar](https://huggingface.co/avatars/1299f5cd3558e75571711d544f4a6d29.svg)](https://huggingface.co/jucho2725)

JinUk, Cho

jucho2725

[![QVAC's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)](https://huggingface.co/qvac) [qvac](https://huggingface.co/qvac)

[![ohjoon kwon's avatar](https://huggingface.co/avatars/0532faec32a12d143b5329642a709b0f.svg)](https://huggingface.co/joooon)

ohjoon kwon

joooon

[![QVAC's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)](https://huggingface.co/qvac) [qvac](https://huggingface.co/qvac)

[![Patrik Lambert's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/Pmar3VJzQzgT4gdO8dpwt.png)](https://huggingface.co/patrik-lambert)

Patrik Lambert

patrik-lambert

[![QVAC's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)](https://huggingface.co/qvac) [qvac](https://huggingface.co/qvac)

[![Mathias Buus's avatar](https://huggingface.co/avatars/04b3527ef6ff1d6feebcad80e5c0e5c6.svg)](https://huggingface.co/mafintosh)

Mathias Buus

mafintosh

[![QVAC's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)](https://huggingface.co/qvac) [qvac](https://huggingface.co/qvac)

[![Amril Nurman's avatar](https://huggingface.co/avatars/321662b676eb3141ce8410614e581e2c.svg)](https://huggingface.co/Nurman)

Amril Nurman

Nurman

[![QVAC's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)](https://huggingface.co/qvac) [qvac](https://huggingface.co/qvac)

Frontier cloud LLMs carry high operational costs that can fluctuate unexpectedly, and relying on such third-party models introduces vulnerabilities, as providers can modify, deny, or deprecate access at any time. Furthermore, proprietary models offer limited customization for specific workflows, while posing risks to privacy, data control, and transparency. Besides, not every task demands frontier-level intelligence: small, specialized agents can be equally capable on specific tasks and significantly cheaper to run, since many routine or smaller workloads can be processed efficiently on-device. As intelligence per parameter continues to improve rapidly, we aim to stand at the forefront of this shift toward performant, privacy-focused, self-hosted models.

Tether AI Research introduces **BotPsy**, a 0.8B-parameter model introduce **BotPsy**, a 0.8B-parameter model designed for function calling and agentic workflows, built on top of Qwen3.5-0.8B and suitable for on-device deployment. BotPsy is a "personal assistant" that uses tools to perform a variety of simple tasks for the user, in domains such as web search & research, travel & lifestyle, commerce & finance, business & customer operations, device & vehicle control, files & documents, calendar, and email & messaging. Due to its small parameter count, it is best suited to tasks of low to medium difficulty. BotPsy achieves state-of-the-art (SOTA) tool-use and agentic performance for its size, outperforming every model of up to 1.2B parameters that we tested (Figures 1 and 2). Designed for secure on-device workflows, it provides exceptional instruction-following reliability and efficiency while keeping user data private. As a small model, BotPsy still makes mistakes and is not intended for high-stakes use; please read the [Intended Use and Limitations](https://huggingface.co/blog/qvac/botpsy#intended-use-and-limitations) for more information.

🤗 [Model (safetensors)](https://huggingface.co/qvac/BotPsy-0.8B) | 📦 [GGUFs (bf16, Q8, Q4)](https://huggingface.co/qvac/BotPsy-0.8B-GGUFs)

**Figure 1:** BotPsy-0.8B significantly outperforms its base model and leads five of the six tool-use and agentic benchmarks, including against Qwen3.5-2B-Think (2.5× its size); only on Claw-Eval does Qwen3.5-2B-Think edge ahead.

**Figure 2:** *Knowledge:* tool-use training preserved and improved BotPsy's general knowledge compared to similarly sized models, though overall knowledge still scales primarily with parameter count. *Instruction following:* BotPsy excels at following explicit instructions and multi-turn tasks, though its performance drops as instructions accumulate and lags in lower-resource languages.

### Copyright Complaints

We will take appropriate actions in response to notice of copyright infringement. If you believe your work has been used or copied in a manner that infringes upon your intellectual property rights, please email [data-apps@tether.io](mailto:data-apps@tether.io) identifying and describing both the copyrighted work and alleged infringing content to file a notice of infringement.

## Key Highlights

### Benchmark results

- **Twice the performance of its base model:** BotPsy roughly doubles the agentic capability of Qwen3.5-0.8B-Think on key benchmarks: BFCL v4 rises from 23.4 to 44.0, ACEBench from 30.1 to 58.7, and τ-bench from 23.2 to 51.5 (mean of the retail, telecom and banking subsets).
- **Best agent in its category:** BotPsy outperforms leading models in the ≤1.2B-parameter weight class (Qwen3.5-0.8B-Think, LFM2.5-1.2B-Think, MiniCPM5-1B-Think) on all six tool-use and agentic benchmarks: BFCL v4, ACEBench, τ-bench, ToolSandbox, Claw-Eval and BrowseComp-Plus.
- **Outperforms its larger sibling:** BotPsy has the highest score of all models tested on five of the six benchmarks, beating Qwen3.5-2B-Think, a model 2.5× its size, on BFCL v4 (44.0 vs 37.7), ACEBench (58.7 vs 55.4), τ-bench (51.5 vs 46.5), ToolSandbox (64.6 vs 41.2) and BrowseComp-Plus (4.5 vs 2.8). Only on Claw-Eval does Qwen3.5-2B-Think lead (48.9 vs 46.5).

### Model capabilities

- **More reliable in multi-turn workflows:** On τ²-bench, where the agent must hold a long customer conversation, follow a strict policy, and act on the customer's behalf, it scores 82.5 in telecom, ahead of Qwen3.5-2B-Think (69.3). On BFCL v4's multi-turn tasks, it rises from 7.5 to 46.1 over its base, nearly double Qwen3.5-2B-Think (23.8). Grouped by application, its multi-step scores lead all models tested in commerce and services (58.3 vs 47.4 for the next best, Qwen3.5-2B-Think) and in device and system management (46.1 vs 31.9).
- **Knows when (not) to call tools:** An agent that acts must also know when not to act. On BFCL v4's hallucination tests, which check that the model declines when no appropriate tool exists, BotPsy scores 86.1, the highest of all models tested. On ACEBench's special cases, where the request is incomplete, contains wrong parameters, or cannot be served by the given tools, it scores 51.3, up from 13.7 for its base model.
- **Follows instructions while preserving knowledge:** BotPsy specializes in tool use while preserving general skills. Instruction following improves sharply, with IFEval rising from 59.7 to 90.8 and IFBench from 22.0 to 55.9, the highest IFBench score of all models tested. General knowledge also improves, with GPQA Diamond rising from 33.2 to 38.1 and MMLU-Pro from 41.6 to 48.9. On all four benchmarks, BotPsy outperforms every other model of 1.2B parameters or fewer that we tested.

### Safety, efficiency and deployment

- **Safer than leading models in its category:** In automated red-teaming across six harm categories, BotPsy produces unsafe responses 21% of the time, compared with 36% for its base model. This is the lowest rate of all models of up to 1.2B parameters (LFM2.5-1.2B-Think: 35%; MiniCPM5-1B-Think: 47%). Under prompt-injection attacks, which matter most for agents that read untrusted tool outputs, the unsafe rate drops from 46% for its base model to 31%.
- **More efficient reasoning and less looping:** On questions that all five models answer correctly, BotPsy reaches the answer with about 3× fewer reasoning tokens than its base model on GPQA Diamond (3,690 vs 11,563) and 2.7× fewer on MMLU-Pro (1,912 vs 5,105). Across all IFBench attempts, its rate of getting stuck in repetitive reasoning loops falls from 22.9% to 1.4%, and runs that hit the 32k-token limit fall from 28.3% to 0.2%. Shorter, more decisive reasoning should reduce latency on-device.
- **Open-source and ready to use:** BotPsy will be released with open weights under the Apache 2.0 license for research and educational use. It will be available in three precisions (bf16, Q8, Q4), as Hugging Face safetensors and as GGUF files for the QVAC SDK and llama.cpp.

## Broader Vision

Building upon the foundation of BotPsy, future development by Tether Data, S.A. de C.V. (“Tether AI Research”, “we”, “our”) will focus on expanding on-device agentic capabilities to seamlessly integrate with an even broader array of hardware and local services. Tether's Hypersearch will evolve to support more robust decentralized peer-to-peer (P2P) queries, further ensuring private, encrypted web searches that bypass corporate trackers. QVAC Fabric local fine-tuning mechanisms will be optimized to adapt more deeply to individual user preferences, workflows, and specialized tool environments. Future iterations will allow the smartphone interface to smoothly delegate heavy computational tasks to home PCs or trusted secure P2P nodes during offline-online transitions. Privacy protocols will be continuously strengthened to guarantee that all personal data, credentials, and decisions remain strictly on local hardware. Collaborative features will be introduced to allow secure agent-to-agent communication across trusted local networks without compromising user confidentiality. Ultimately, these advancements will solidify BotPsy as a fully autonomous, highly capable personal AI ecosystem that keeps users entirely in control of their digital lives.

## Methodology

BotPsy is based on Qwen3.5-0.8B and is post-trained in four sequential stages: Supervised Fine-Tuning (SFT), Multi-teacher On-Policy Distillation (MOPD), and two rounds of Reinforcement Learning (RL). Each stage uses the previous stage's best checkpoint as its starting point and benefits from a different learning signal: imitation of reference trajectories, the token distributions of much larger teacher models, and rule-based tool-calling rewards (see Figure 3).

**Figure 3:** BotPsy training recipe. The student goes through four stages. Three specialist Qwen3.5-4B teachers, each RL-trained for one skill, guide it during the distillation stage.

### Training procedure: four stages, three types of feedback

Our approach uses four stages of training, which learn from three types of signal: demonstrations, specialist teachers, and verifiable rewards.

**Learning from demonstrations (SFT)**

We first perform full-parameter supervised fine-tuning on tool-use conversations. These include multi-turn agent trajectories from simulated environments, replayed single, parallel and multi-step calls, and cases where no tool should be called.

**Learning from teachers (MOPD)**

Next, the student is trained with on-policy distillation (OPD): it generates its own responses, and a specialist teacher provides feedback on every token, using the per-token reverse KL divergence as the training signal. To build the teachers, we first RL-trained three Qwen3.5-4B models to specialize in tool use, general reasoning, and instruction following. During training, every prompt is routed to one of these teachers. This stage mainly aims to recover knowledge and instruction following, which degraded during the SFT stage, although the tool-use metrics also increase (see Figure 4).

**Figure 4:** Mean score of each capability group after each training stage. SFT boosts tool use but pushes knowledge and instruction following below the base model; distillation brings both back above base, and the RL stages add further gains on all three.

**Learning from rules and environments (RL stages)**

Finally, the model is trained with reinforcement learning using DAPO [1], learning only from rewards computed by rules and verifiers. The first round focuses on tool calling, accompanied by instruction following and STEM multiple-choice questions. As in Tool-N1 [2], the tool-calling reward first checks the reasoning and tool-call format. Instead of Tool-N1's binary correctness reward, however, it gives fine-grained partial credit in the spirit of ToolRL [3], matching the predicted tool names, argument names, and argument values against the ground truth.

The second round widens the training mix to general-domain verifiable tasks: math, code, knowledge (multiple-choice) questions, instruction following, structured outputs, and multi-step tool use in a simulated workplace environment. Although this mix contains no multi-turn conversations, it further improves multi-turn function calling.

### Data composition

Each stage of training uses a different data mixture (Figure 5). The SFT stage focuses mainly on tool use and prepares the ground for the subsequent stages. The MOPD mixture combines tool-use, knowledge and instruction-following data, both to further improve function calling and to recover the general-domain regressions from the SFT stage. The first RL stage again focuses mainly on tool use, while the second RL stage shifts the balance toward general-domain data (instruction following, knowledge, math and code), keeping a smaller share of tool use.

**Figure 5:** Approximate training-data composition per stage, grouped by capability.

## Results

### Tool use & agents

BotPsy roughly doubles the tool-use performance of its Qwen3.5-0.8B base and is the strongest of the five models on five of the six agentic benchmarks: BFCL v4 (44.0 vs 23.4), ACEBench (58.7 vs 30.1), τ-bench (51.5 vs 23.2), BrowseComp-Plus (4.5 vs 1.9) and ToolSandbox (64.6 vs 30.5). On all five, it is also ahead of Qwen3.5-2B-Think, a model 2.5× its size (37.7, 55.4, 46.5, 2.8 and 41.2 respectively; see Table 1). On Claw-Eval, Qwen3.5-2B-Think leads (48.9 vs 46.5).

| Benchmark | **BotPsy-0.8B** ours | Qwen3.5-0.8B-Think base · 1× | Qwen3.5-2B-Think 2.5× | LFM2.5-1.2B-Think 1.5× | MiniCPM5-1B-Think 1.25× |
| --- | --- | --- | --- | --- | --- |
| BFCL v4¹ | **44.0** | 23.4 | 37.7 | 28.1 | 22.8 |
| ACEBench² | **58.7** | 30.1 | 55.4 | 39.4 | 24.5 |
| τ-bench³ | **51.5** | 23.2 | 46.5 | 6.5 | 28.8 |
| Claw-Eval⁴ | 46.5 | 39.3 | **48.9** | 31.6 | 31.0 |
| BrowseComp-Plus⁵ | **4.5** | 1.9 | 2.8 | 0.2 | 0.8 |
| ToolSandbox⁶ | **64.6** | 30.5 | 41.2 | 45.7 | 28.1 |
| *Average* | ***45.0*** | *24.7* | *38.8* | *25.3* | *22.7* |

**Table 1:** Tool-use and agentic benchmarks (0–100, higher is better). Best score per row in **bold**, second best underlined; multipliers give parameter count relative to BotPsy-0.8B. The average is the unweighted mean of the six benchmarks. See [Evaluation Footnotes](https://huggingface.co/blog/qvac/botpsy#evaluation-footnotes) for details of the evaluation setup.

### Knowledge

Tool-use training did not cost general knowledge: GPQA Diamond rises from 33.2 to 38.1 and MMLU-Pro from 41.6 to 48.9, the best of the models at 1.2B parameters or below (LFM2.5-1.2B-Think: 35.0 and 39.4; MiniCPM5-1B-Think: 15.8 and 40.0). Knowledge still scales mainly with parameter count, and Qwen3.5-2B-Think scores well above (59.9 and 65.5). BotPsy is therefore designed to call tools for facts it does not know, not to serve as a knowledge model.

| Benchmark | **BotPsy-0.8B** ours | Qwen3.5-0.8B-Think base · 1× | Qwen3.5-2B-Think 2.5× | LFM2.5-1.2B-Think 1.5× | MiniCPM5-1B-Think 1.25× |
| --- | --- | --- | --- | --- | --- |
| GPQA Diamond⁷ | 38.1 | 33.2 | **59.9** | 35.0 | 15.8 |
| MMLU-Pro⁸ | 48.9 | 41.6 | **65.5** | 39.4 | 40.0 |

**Table 2:** General-knowledge benchmarks (0–100, higher is better). Best score per row in **bold**, second best underlined. See [Evaluation Footnotes](https://huggingface.co/blog/qvac/botpsy#evaluation-footnotes) for details of the evaluation setup.

### Instruction following

BotPsy is the best of the five at following explicit instructions: IFEval 90.8 (base 59.7; Qwen3.5-2B-Think 80.0) and IFBench 55.9 (base 22.0; Qwen3.5-2B-Think 40.9). On Multi-IF, which tests instruction following over three turns in eight languages, it scores 67.2, on par with Qwen3.5-2B-Think (66.9) and LFM2.5-1.2B-Think (68.2). It starts strongest (84.3 in turn 1, the highest of the five) but drops faster as instructions accumulate (51.0 in turn 3, vs 56.5 and 56.2 for those two models). Lower-resource languages remain a weakness: Hindi (24.5) and Russian (57.6) are far below the 72–80 reached in English, Chinese, French, Spanish, Italian and Portuguese.

| Benchmark | **BotPsy-0.8B** ours | Qwen3.5-0.8B-Think base · 1× | Qwen3.5-2B-Think 2.5× | LFM2.5-1.2B-Think 1.5× | MiniCPM5-1B-Think 1.25× |
| --- | --- | --- | --- | --- | --- |
| IFEval⁹ | **90.8** | 59.7 | 80.0 | 85.6 | 78.4 |
| IFBench⁹ | **55.9** | 22.0 | 40.9 | 33.9 | 40.6 |
| Multi-IF¹⁰ | 67.2 | 43.2 | 66.9 | **68.2** | 53.4 |

**Table 3:** Instruction-following benchmarks (0–100, higher is better). Best score per row in **bold**, second best underlined. See [Evaluation Footnotes](https://huggingface.co/blog/qvac/botpsy#evaluation-footnotes) for details of the evaluation setup.

### Multi-turn conversations

The largest relative gains come in multi-turn, stateful interaction, where BotPsy leads four of the five multi-turn benchmarks (Figure 6). On BFCL v4 multi-turn it rises from 7.5 to 46.1, nearly double Qwen3.5-2B-Think (23.8), and on ACEBench Agent from 7.9 to 28.3 (Qwen3.5-2B-Think: 16.2). On τ²-bench it doubles its base in retail (67.8 vs 33.9, a narrow lead over Qwen3.5-2B-Think at 65.5) and reaches 82.5 in telecom, where the agent has to guide a user through troubleshooting over many turns (MiniCPM5-1B-Think: 74.0; Qwen3.5-2B-Think: 69.3). It is also the most reliable of the five at single calls (BFCL non-live: 83.0) and at not calling a tool when none fits (BFCL hallucination: 86.1).

**Figure 6:** Multi-turn agentic tasks: BFCL v4 multi-turn, ACEBench Agent, τ²-bench (retail, telecom) and τ³-bench (banking). BotPsy leads four of the five benchmarks; on τ³-banking, every model stays below 5.

### Weak spots

BotPsy's weaker spots are open-ended search and a few areas where Qwen3.5-2B-Think still leads. BotPsy's BrowseComp-Plus score of 4.5 is the best of the five, but low in absolute terms, and on BFCL web search (14.0) and memory (16.3) it trails Qwen3.5-2B-Think (19.8 and 26.1). On Claw-Eval, BotPsy improves clearly on its base (46.5 vs 39.3) but remains slightly below Qwen3.5-2B-Think (48.9). On ACEBench's special cases (incomplete or erroneous requests), Qwen3.5-2B-Think is also ahead (58.0 vs 51.3), although BotPsy is far above its base there (13.7). τ³-banking is the one multi-turn benchmark where BotPsy does not lead: no model gets above 5 (BotPsy 4.1, unchanged from its base; Qwen3.5-2B-Think 4.8).

## Where it works: app-level performance breakdown

BotPsy can handle a variety of use cases and scenarios. Figure 7 breaks the benchmark scenarios down by app group, separating simple scenarios (single turn, one tool call) from complex ones (multi-turn or multi-tool). The overall scores quoted in this section are averaged over all scenarios; the bottom row of Figure 7 is an unweighted mean of the seven groups, so its numbers differ.

### Single tool calls work well everywhere

Simple scenarios score 70–79 in every app group with a meaningful sample (Communication & Social has only 6). Overall, BotPsy scores 75, about 21 points above its base model (54) and slightly above Qwen3.5-2B-Think (70).

**Figure 7:** Mean per-scenario score (0–100, higher is better) by app group, for simple (left) and complex (right) scenarios. n gives the number of simple / complex scenarios in each group; the bottom row is the unweighted mean of the seven groups.

### The largest gains are in multi-step tasks

On complex scenarios, BotPsy scores 39.5 overall, against 17.9 for its base and 30.8 for Qwen3.5-2B-Think. The gain is largest in Communication & Social (61 vs 13 for the base), Commerce & Services (58 vs 27) and Device & System Management (46 vs 15). Qwen3.5-2B-Think is ahead only in Personal Productivity & Work (64 vs 58, 38 scenarios, mostly Claw-Eval), and MiniCPM5-1B-Think is marginally ahead in Communication & Social (61.5 vs 60.5). Multi-step tasks still score lower than single calls, which remains the main limit for harder tasks.

### Multi-step information retrieval is the weak spot

Complex Information Retrieval & Research scenarios score 15 (single calls: 79). Most are BrowseComp-Plus deep-research questions, which stay hard for every model in this size range (base: 9; Qwen3.5-2B-Think: 14).

## Inference efficiency

BotPsy reaches correct answers with much less reasoning than its base, and with fewer turns on multi-turn agent tasks. This aligns with our explicit focus on reasoning efficiency throughout training. All comparisons below are made on the same questions or tasks (those that all five models answered correctly or solved), so differences in difficulty do not drive the numbers. Reasoning tokens are counted with each model's own tokenizer.

**Figure 8:** Accuracy against reasoning tokens per correct answer on GPQA Diamond, MMLU-Pro, IFEval and IFBench. Tokens are measured on questions all five models answer correctly; accuracy is over all questions. Top-left is better; the dashed line is the Pareto frontier.

**Shorter reasoning, with higher accuracy.** Compared with its base, BotPsy uses 1.4–3.1× fewer reasoning tokens per correct answer on GPQA Diamond (3,690 vs 11,563), MMLU-Pro (1,912 vs 5,105), IFEval (3,148 vs 4,433) and IFBench (4,204 vs 11,576), while scoring higher on all four (Figure 8). It is not the shortest model everywhere: LFM2.5-1.2B-Think writes shorter reasoning on MMLU-Pro, IFEval and IFBench, and MiniCPM5-1B-Think on IFEval and IFBench, but at lower accuracy than BotPsy on each.

**Figure 9:** Pass rate against assistant turns per solved task on τ²-bench retail and telecom. Turns are measured on tasks all five models solve; pass rate is over all tasks. Top-left is better; the dashed line is the Pareto frontier.

**Fewer turns than the base on multi-turn agent tasks.** On τ²-bench tasks that all five models solve, BotPsy needs fewer assistant turns than its base (Figure 9):

- τ²-retail: 10.7 turns, against 11.7 for the base (9% fewer) and 10.6 for Qwen3.5-2B-Think.
- τ²-telecom: 13.1 turns, against 17.6 for the base (26% fewer) and 13.8 for Qwen3.5-2B-Think (5% fewer).

It does this while passing 2.0× (retail) and 2.6× (telecom) as many tasks as the base. MiniCPM5-1B-Think uses fewer turns on retail (8.7), but passes only 9.9% of retail tasks.

## Intended Use and Limitations

BotPsy has been developed to advance the state of the art and to support research and educational uses. Models developed based on our work could be suitable for tasks in domains such as device & system management (settings, files & documents, clocks & alarms), personal productivity & work (calendar & tasks, email, collaboration tools), communication (messaging), information retrieval & research (web search, weather, news), media & lifestyle (video, music, recipes & fitness, photos) and commerce & services (maps & travel, finance, shopping & delivery). Due to its small parameter count, it is **best suited to tasks of low to medium difficulty**.

BotPsy has been primarily trained and tested in English, which is the recommended language. It has also been evaluated on Multi-IF, which covers seven additional languages (Chinese, French, Hindi, Italian, Portuguese, Russian and Spanish): it performs well in most of them, but scores much lower in Hindi and Russian. BotPsy is a small language model, and it makes mistakes. It is not intended for safety-critical or high-stakes automated decisions, or for applications involving money, personal information, health and other sensitive topics.

## Citation

```
@misc{botpsy2026,
  title  = {BotPsy: On-Device Personal Assistant with a Sub-Billion-Parameter Agentic Language Model},
  author = {{Tether Data, S.A. de C.V. d.b.a. Tether AI Research}},
  year   = {2026},
  note   = {Hugging Face blog}
}
```

## References

[1] Yu, Qiying, et al. "DAPO: An Open-Source LLM Reinforcement Learning System at Scale." *Advances in Neural Information Processing Systems* 38 (2025): 113222–113244.

[2] Zhang, Shaokun, et al. "Nemotron-Research-Tool-N1: Exploring Tool-Using Language Models with Reinforced Reasoning." *International Conference on Learning Representations* (2026).

[3] Qian, Cheng, et al. "ToolRL: Reward is All Tool Learning Needs." *Advances in Neural Information Processing Systems* 38 (2025).

## Evaluation Footnotes

- All scores are percentages (higher is better).
- All models were evaluated in thinking (reasoning) mode.
- All benchmarks that use an external API were run on **November 3, 2026**.
- ¹ BFCL v4: overall score calculated using the official weighted formula (40% Agentic, 30% Multi-Turn, 10% Live, 10% Non-Live, and 10% Hallucination), averaged over 3 runs.
- ² ACEBench: overall accuracy. All models were evaluated in function-calling (FC) mode; mean of 2 runs.
- ³ τ-bench: average of τ²-bench (retail, telecom) and τ³-bench (banking), excluding airline; mean of 3 runs.
- ⁴ Claw-Eval: official average task score, where each task scores safety × (0.8 × completion + 0.2 × robustness); mean of 3 runs.
- ⁵ BrowseComp-Plus: accuracy, with a maximum of 30 steps for all models.
- ⁶ ToolSandbox: mean similarity score over 8 settings.
- ⁷ GPQA Diamond: accuracy over all 198 questions, mean of 3 runs, thinking enabled.
- ⁸ MMLU-Pro: accuracy.
- ⁹ IFEval, IFBench: prompt-level strict accuracy.
- ¹⁰ Multi-IF: average of 3 runs.

More from this author

## QVAC TranscribePsy: State-of-the-Art On-Device Multilingual Speech Recognition

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)

8

October 14, 2026

## QVAC Genesis III: A Large-Scale, High-Quality Open Synthetic STEM Corpus for Efficient Language Model Pre-Training

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)

September 23, 2026

### Community

Upload images, audio, and videos by dragging in the text input, pasting, or clicking here.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fqvac%2Fbotpsy) or [log in](https://huggingface.co/login?next=%2Fblog%2Fqvac%2Fbotpsy) to comment


2

- [![](https://huggingface.co/avatars/0532faec32a12d143b5329642a709b0f.svg)](https://huggingface.co/joooon)
- [![](https://huggingface.co/avatars/30ff51594b6454a1eced9a0d472d2ec1.svg)](https://huggingface.co/milangritta)
