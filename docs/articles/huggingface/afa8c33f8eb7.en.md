---
vendor: huggingface
title: Getting the Source Right, Not Just the Fact: Source-Aware Verification for MCP Agents
original_title: Getting the Source Right, Not Just the Fact: Source-Aware Verification for MCP Agents
url: https://huggingface.co/blog/MultiverseComputingCAI/getting-the-source-right-not-just-the-fact-source
date: 2024-04-11
lang: en
captured: 2026-10-10
extractor: readability-v1
status: ok
body_sha: 0a073aae3650
---

Back to Articles

# Getting the Source Right, Not Just the Fact: Source-Aware Verification for MCP Agents

Team

Article

Published
					September 29, 2026

Upvote

21

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/668e37fd9c9aa124a3c867e8/4ivwrPQnZGMDF6ovxnAdA.jpeg)](https://huggingface.co/AntonioTN)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/68aea9113e6515ab6246bc1a/Nw5J61eDhzNo-aHDvCzlg.jpeg)](https://huggingface.co/ander-alvarez)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/1iQUUZFQh6BZXCgGY7zJT.png)](https://huggingface.co/AlexDGenu)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/QU3ijZPXiAWJKJQTof3nF.png)](https://huggingface.co/DuckDuckDown)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/tGmQJzeT9SYL_sK839ifI.png)](https://huggingface.co/AlgoEnergy)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/3xs4KD-K8_TSwUNSbWp9o.png)](https://huggingface.co/fakoor)

Antonio Tiene

AntonioTN

MultiverseComputingCAI

Ander Alvarez Sanz

ander-alvarez

MultiverseComputingCAI

Oliver Wirjadi

oliverwirjadi

MultiverseComputingCAI

Alessandro Genuardi

AlexDGenu

MultiverseComputingCAI

Tool-using LLM agents no longer read from a single retrieved passage. Through the [Model Context Protocol (MCP)](https://modelcontextprotocol.io), an agent can call a search tool, inspect a structured patient or account record, query a database, and pull metadata, then weave all of it into one answer. That m aakes the usual question of factuality more subtle than it looks. Most of the systems built to check LLM answers, from [RAGAS faithfulness](https://github.com/explodinggradients/ragas) to fine-grained checkers like MiniCheck, AlignScore, and SummaC, ask whether a claim is supported by the available evidence once that evidence has been pooled together. In their usual form, they do not tell us which MCP tool output supports each claim, or whether that is the source the answer names.

Our latest paper, *ProvenanceGuard: Source-Aware Factuality Verification for MCP-Based LLM Agents* (read it on [Hugging Face](https://huggingface.co/blog/MultiverseComputingCAI/%5BHF-PAPER-LINK%5D), or on [arXiv](https://arxiv.org/abs/2606.18037) in the meantime), targets that gap. The failure mode we care about is one we call cross-source conflation: a claim that is true somewhere in the evidence, but attributed to the wrong source. A source-blind verifier may pass it, because the fact does exist in the pool. A source-aware verifier should not.

## The problem: supported somewhere is not the same as supported by the right source

Consider a customer support agent that answers, "According to the account record, this plan includes a 30-day refund window." The refund window may be perfectly real, but stated in a policy document, not in the account record the answer points to. Pool the two together and the claim looks supported. Keep them separate and the attribution is wrong, and in a data-sensitive setting a wrong attribution can be as damaging as a wrong fact. The same pattern shows up in a clinical agent, where a patient-specific medication detail taken from a patient-history tool becomes misleading the moment the answer presents it as a finding from the medical literature.

[![Diagram contrasting source-blind pooled support with source-aware verification, using a refund-window claim that is supported by a policy document but attributed to the account record.](https://cdn-uploads.huggingface.co/production/uploads/668e37fd9c9aa124a3c867e8/svnUpzhFgTpLqOF_bRDHl.png)](https://cdn-uploads.huggingface.co/production/uploads/668e37fd9c9aa124a3c867e8/svnUpzhFgTpLqOF_bRDHl.png)

*A claim can be supported by one MCP source while the answer attributes it to another. Source-blind scoring sees support in the pooled evidence and passes it; ProvenanceGuard separately checks whether the supporting source matches the one the answer states or implies. Source: paper Figure 1.*

This is why faithfulness scores, useful as they are, are not enough for MCP agents. An answer carries provenance, sometimes explicitly ("according to the account record") and sometimes implicitly. ProvenanceGuard keeps that connection between claim and source available for inspection.

## What ProvenanceGuard does

ProvenanceGuard is a post-generation verification layer that sits on top of a black-box MCP agent. It runs after an agent produces an answer, and never collapses the evidence into one anonymous context. Instead it carries the source identity all the way through the pipeline. It reads the captured MCP trace, including the tool outputs and their source IDs, without retraining the agent. Then it does five things in sequence: it breaks the answer into specific claims, finds the source most relevant to each one, checks whether that source actually supports it, compares the source with the one the answer names or implies, and finally emits both a per-claim source verdict and a global, answer-level allow or block decision.

[![Pipeline diagram showing the agent producing a draft answer and trace, then ProvenanceGuard decomposing claims, routing to sources, checking support with NLI, calibrating, checking attributions, and either allowing the answer or sending it to repair.](https://cdn-uploads.huggingface.co/production/uploads/668e37fd9c9aa124a3c867e8/nDchWzRhBSmscjaa8w5G5.png)](https://cdn-uploads.huggingface.co/production/uploads/668e37fd9c9aa124a3c867e8/nDchWzRhBSmscjaa8w5G5.png)

*The verification flow. Source identity is preserved through decomposition, routing, support scoring, attribution checking, and repair, rather than being pooled. Blocked answers can go through RARR-style repair and be re-verified. Source: paper Figure 2.*

A few of the design choices are worth calling out. For the experiments in our paper, we used local models so the captured traces could be processed in a controlled, offline setup: [MiniLM](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) helps find the relevant source, a [DeBERTa NLI verifier model](https://huggingface.co/MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli) checks whether that source supports the claim, and a local language model helps break answers into claims. The verifier also checks literal values closely: a number, date, or identifier absent from the source cannot pass merely because the sentence sounds plausible. A calibrated decision step combines these signals. If an answer is blocked, a [RARR](https://arxiv.org/abs/2210.08726)-style repair step can try a source-grounded revision or a safe fallback, which the verifier then checks again.

Those named models are the setup we evaluated, not a requirement of ProvenanceGuard. The same claim, source, and decision steps can be adapted to hosted models where a team prefers cloud services; a new setup would need its own testing and calibration. Our reported results come from the local configuration. Its conservative decision policy suits data-sensitive review, where getting the source right matters more than producing the fastest possible answer.

## Results

We tested ProvenanceGuard on answers from a medical agent that had used patient records, research articles, and other tools. This gave us 281 real traces to study. Medicine is a useful test because a fact from a patient's record and a fact from general research cannot be treated as the same source. The method can also be used in other fields when an agent keeps a record of its tool outputs and source IDs. For the main test, human experts checked 361 claims from 40 answers set aside from the data used to develop the system.

The most direct result is this: experts said 139 claims should not pass, and ProvenanceGuard caught 138 of them. It let one through. It also held 67 claims that the experts considered supported, sending them for review or repair. This reflects the cautious setting we tested: it favors a second look at some supported claims over letting unsupported ones through. For claims with an identifiable source, it also picked the right source about 86% of the time in this test.

We ran four other support checkers on the same claims. ProvenanceGuard scored highest on the paper's measure of how well a system catches claims that should be blocked while avoiding unnecessary blocks. The other checkers in this comparison did not tell us which tool output supported each claim. ProvenanceGuard records that connection, so a reviewer can see the source checked for each claim and the decision it produced.

| Verifier | Reject/block F1 | Emits claim-to-source ID |
| --- | --- | --- |
| ProvenanceGuard (ours) | **0.802** | Yes |
| MiniCheck | 0.783 | No |
| RAGAS Faithfulness | 0.758 | No |
| AlignScore | 0.662 | No |
| SummaC-ZS | 0.436 | No |

*Binary support metrics on the same held-out claim packet. ProvenanceGuard matches or beats the source-blind baselines on blocking while also producing per-claim source verdicts. Source: paper abstract and Table III.*

## Checking claims when sources look similar

In a separate, harder test with several similar sources, ProvenanceGuard scored 0.846 F1 for deciding which claims to block, but identified the exact source correctly in 50.3% of claims. Telling similar sources apart remains an important area for improvement.

We also ran a controlled test focused on wrong attribution: we changed the named source in 50 cases while leaving the supporting evidence intact. ProvenanceGuard caught all 50 swaps. This shows it can detect a clear source error, while the harder test shows the challenge of choosing among many plausible sources.

## Repairing blocked answers

Blocking is only useful if there is something to do with a blocked answer. Wired to the RARR-style repair loop, the full-trace run resolved all 173 blocked answers, though 144 of them ended in fallback text rather than a substantive rewrite, which is the system choosing to avoid an unverifiable answer rather than manufacture one. On reconstructed multi-source test traces, a fresh repair run resolved all 59 initially blocked answers with only two terminal fallbacks. As an offline gate the overhead is modest, roughly half a second per answer on the reported local configuration, with the NLI and routing calls themselves in the tens of milliseconds.

## Why this fits Multiverse Computing

As agents move from single-passage RAG to multi-tool MCP setups, the question of which source a fact actually came from stops being a footnote and becomes part of what factuality means. ProvenanceGuard makes that source connection visible claim by claim. For Multiverse Computing, that means a way to check existing agents while keeping sensitive traces in a controlled environment when needed. The medical study is one use case; the same approach can be adapted wherever an agent's trace preserves its tools and sources.

That adaptation is already visible in [NVIDIA NVFlow](https://github.com/NVIDIA/nvflow/pull/9), which merged an optional grounding-verification stage for its finance agent. It checks completed answers against the SEC excerpts the agent retrieved and saves separate decisions without changing the original rollout or training data. The NVFlow contribution uses ProvenanceGuard's source-aware verification approach; the repair loop discussed above belongs to the broader research system.

ProvenanceGuard was also [presented as a poster at the Agentic AI Summit 2026 at UC Berkeley](https://github.com/aalvsz/provenanceguard/blob/main/poster/ProvenanceGuard_Agentic_AI_Summit_2026_Berkeley.pdf).

Want the full technical details, including the routing and NLI derivations, the calibration ablations, the multi-source stress slices, and the complete results tables? Read the full paper on [Hugging Face](https://huggingface.co/papers/2606.18037), or get in touch with our team to talk about applying source-aware verification to your own agents.

## Models mentioned in this article 2

## Papers mentioned in this article 1

More from this author

## Pruning LLMs Like a Physicist: Block Removal as an Ising Optimization Problem

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6835694d56d5a69517655698/C3QUBARPGF4kbzJzZaT29.png)

34

September 21, 2026

## Safety for Whom? Refusing the Right Subset of a Topic, Not the Whole Topic

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6835694d56d5a69517655698/C3QUBARPGF4kbzJzZaT29.png)

31

September 8, 2026

### Community

Nomad-link-id

10 days ago

The failure mode that matters for MCP agents is quieter than "hallucination": a claim that is true *somewhere* in the pooled tool outputs, attributed to the wrong source.

Source-blind faithfulness can still go green in that case — the fact exists in the soup. Source-aware verification is the contract upgrade: keep tool/source IDs through claim decomposition, support check, and attribution check, then allow/block with a per-claim source verdict a reviewer can actually inspect.

Practical ask for teams wiring MCP: when your eval says "grounded," does it mean supported-by-any-tool-output, or supported-by-the-source-the-answer-named? Those are different release gates. In multi-tool setups the second one is the one that catches cross-source conflation before a human trusts the citation.

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/68aea9113e6515ab6246bc1a/Nw5J61eDhzNo-aHDvCzlg.jpeg)](https://huggingface.co/ander-alvarez)

·

ander-alvarez

Article author

10 days ago

Hi, thank you for your comment. You’ve captured the issue well. For ProvenanceGuard, when a claim is “grounded” it means it is supported by the source the answer names or implies. Finding the fact somewhere else in the tool outputs isn’t enough. In the refund-window example, the policy supports the fact, but the answer credits the account record, so we flag the mismatch and show the source verdict.

mghwaz

10 days ago

•

edited 10 days ago

I had a brief read on the paper, but I could not find any comparison with cheaper llm agent for source aware judge. Like this is my reading of the paper;

- An LLM calls multiple tools and generates an answer using their outputs, which may describe many claims
- A claim can be supported by (one or more) tool’s output while being incorrectly attributed to another.
- Basically, split the answer into claims and uses embeddings to find a likely supporting source for each.
- Using NLI & random forest, check if the selected source supports the claim;
- Also check in response, claim's is attributed by correct source.

Like, it seems (2 - 5) can be done via basic prompts in lifecycle, if you own the executing agent. If not, this can also be done via hooks in harness as plugin. Do you have any comparison on this. Basically, how much of random forest, and all of these eng/plumbing is buying, vs second llm call over traces+ans?

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/68aea9113e6515ab6246bc1a/Nw5J61eDhzNo-aHDvCzlg.jpeg)](https://huggingface.co/ander-alvarez)
- [![](https://huggingface.co/avatars/72f6f613035501a07c402999e7718f5f.svg)](https://huggingface.co/mghwaz)

·

ander-alvarez

Article author

9 days ago

Hi, fair question. A source-aware LLM judge could do these checks, and we don’t report a direct comparison with a cheaper one in the paper.

However, part of our motivation is that introducing an LLM judge can itself give inconsistent verdicts or confuse sources (the same kinds of errors we’re trying to catch). A second LLM call can therefore introduce new errors of its own. ProvenanceGuard uses explicit source tracking and calibrated support checks to reduce reliance on another generative judgment. The comparison you suggest would indeed be a useful further study to quantify the benefit in accuracy, latency and cost.

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2FMultiverseComputingCAI%2Fgetting-the-source-right-not-just-the-fact-source) or [log in](https://huggingface.co/login?next=%2Fblog%2FMultiverseComputingCAI%2Fgetting-the-source-right-not-just-the-fact-source) to comment

Upvote

21

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/668e37fd9c9aa124a3c867e8/4ivwrPQnZGMDF6ovxnAdA.jpeg)](https://huggingface.co/AntonioTN)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/68aea9113e6515ab6246bc1a/Nw5J61eDhzNo-aHDvCzlg.jpeg)](https://huggingface.co/ander-alvarez)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/1iQUUZFQh6BZXCgGY7zJT.png)](https://huggingface.co/AlexDGenu)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/QU3ijZPXiAWJKJQTof3nF.png)](https://huggingface.co/DuckDuckDown)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/tGmQJzeT9SYL_sK839ifI.png)](https://huggingface.co/AlgoEnergy)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/3xs4KD-K8_TSwUNSbWp9o.png)](https://huggingface.co/fakoor)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/7sTK8Q_gZRoOz0uaKnVNJ.png)](https://huggingface.co/luke-loan-atlas)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/tI3V8-PZ8d3CC32fzO31e.png)](https://huggingface.co/Stars321123)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/jzzvCtkAVcFuwfuh2k_va.png)](https://huggingface.co/asepsafrudin)
- [![](https://huggingface.co/avatars/327b3a9c4c54e49640d52651c6a8428b.svg)](https://huggingface.co/kbommasani)
- [![](https://huggingface.co/avatars/5f3f1a55b0878bbca0cd10ae8fdf2ed4.svg)](https://huggingface.co/kamal24h)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/Ft9XaIrp9M75oRHfxtCbi.png)](https://huggingface.co/abdullahashraf122)

## Models mentioned in this article 2

## Papers mentioned in this article 1
