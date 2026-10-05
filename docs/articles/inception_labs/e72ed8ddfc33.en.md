---
vendor: inception_labs
title: Mercury 2 for Search: Fast enough to run a hundred times per query
original_title: Mercury 2 for Search: Fast enough to run a hundred times per queryRead story
url: https://www.inceptionlabs.ai/blog/mercury-2-for-search
date: 2026-09-29
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 5a3091806470
---

For the past two years, “search” stopped meaning a ranked list of links and started meaning an agentic pipeline. Classify, rewrite, fan out, rerank, and synthesize. Fifty to a hundred LLM calls per search query, almost all sequential.

That's a brutal place to put an autoregressive model: a 400ms rewrite blocks retrieval, which blocks reranking, which blocks the first word the user sees. So teams cut the pipeline down until it's shallow enough to be fast.

The industry has split into two camps: synchronous search running thin, cheap models that barely think, and deep-research agents that take thirty minutes. Nobody ships the thing in the middle: a pipeline deep enough to be smart and fast enough to be useful. 

Mercury 2 decodes over 1000 tokens per second on standard NVIDIA GPUs. Fast enough to run every step inside the latency budget you already have.

## Latency is the quality budget

In most products, latency and quality are separate dials. You can make the answer better by letting the user wait. In search they're the same dial, because every step that improves makes the answer is itself an LLM call that increase latency:

- **Query rewriting** finds the documents a literal match misses.
- **Reranking** narrows the merged set to the passages worth synthesizing from.
- **Snippet summarization** keeps the synthesis context clean enough to cite.

Each step is an LLM call. Every one of them is either blocking the user or generating the output the user reads.

Agents that run six rewrites instead of one, rerank a hundred results instead of ten, and summarize every retrieved page don't just retrieve faster, they retrieve better.

## Why diffusion doesn't need to go one token at a time

Autoregressive models generate left to right, one token per forward pass. Every token waits for every prior token. That serialization is the structural bottleneck, and it's why the industry's answer to search latency has been "use a smaller model". That’s the only lever available when the decode order is fixed.

Diffusion language models don't have a fixed decode order. Mercury 2 generates in parallel, refining a whole span of output across a small, bounded number of steps rather than emitting one token per pass. Each step is a full-context forward pass over the whole span. The model sees the developing answer holistically and converges on the final output over successive passes. A 300-token reranking rationale and a 500-token snippet summary come back in a fraction of the time. A search pipeline generates hundreds of them.

## The fastest model in every step, measured

"Fast" in a search pipeline isn't one number. What matters is how long each step takes, because each step blocks the next one. So we measured per-step latency directly on **WideSearch**, a benchmark of exhaustive info-gathering tasks requiring dozens of live queries each. Same agentic harness, same 100 tasks, same live retrieval, four models, every LLM call timed.

> Reproducibility: WideSearch benchmark, 100 English tasks, live Exa retrieval. Latency medians over 336–493 calls per model, each on its own provider's public API. Harness and per-call timing are public at: github.com/apoorvumang/retrieval-vs-recall

Mercury 2 is the fastest model at every step of the pipeline, almost 2x faster than Gemini 3.1 Flash Lite on query planning, 4.7x faster than Claude Haiku 4.5, 10x faster than GPT-5 Mini. That per-step gap is where the end-to-end numbers in the next section come from: a pipeline is only as fast as the sum of its hops.

## Doing the math on a real pipeline

Take a mid-complexity answer-engine query with a 2-second budget to first token.

A conventional pipeline spends that budget on one rewrite, a single retrieval pass, no LLM rerank, and a synthesis step that starts streaming late. Most of the 2 seconds is decode time, and the quality ceiling is set by whatever the retriever happened to return.

The same budget on Mercury 2 buys four parallel rewrites, retrieval fan-out across all of them, an LLM rerank over the merged candidate set, per-document snippet summarization, and a synthesis step that starts streaming with room to spare. Same latency envelope. A structurally better answer, because the pipeline did the work.

At $0.25/M input and $0.75/M output, that deeper pipeline runs roughly 2x cheaper that the same one on frontier speed-optimized models.

## Quality at full speed

Speed only matters if the answers hold up. So we ran the cost-efficiency generation tier on two grounded-search benchmarks: **FRAMES** (multi-hop retrieval and synthesis, 2–15 Wikipedia articles per question) and **DeepSearchQA** (open-ended agentic search, graded on whether the answer set is complete).

> n=100 per benchmark, identical question set for every model, all at medium reasoning effort. Agentic tool-calling loop over Exa; 25-call budget on FRAMES, 30 on DSQA. Graded with each paper's official prompt and mandated judge — GPT-5.4 for FRAMES, Gemini-2.5-flash for DSQA. Cost includes Exa retrieval at list rates and bills input at full price with no prompt-cache discount. *Claude Haiku 4.5 routed via OpenRouter (direct key depleted); its latency includes a proxy hop and is likely a couple of seconds high.

On FRAMES, four models land within three points of each other — 0.78, 0.78, 0.78, 0.81. At n=100 the standard error is four to five points, so that spread is noise. On multi-hop grounded QA this tier is tied, and GPT-5 Mini's nominal top score isn't a real lead.

DeepSearchQA separates them, and not in Mercury 2’s favor. GPT-5 Mini scores 0.44 against Mercury 2’s 0.34 — a ten-point gap, wider than the spread among the other three, though still inside two standard errors at this sample size. DSQA rewards breadth: finding every item that matches a constraint, rather than reasoning through a chain. A model that plans decisively and reads widely does better there, and GPT-5 Mini does.

What doesn't change on either benchmark is what a right answer costs and how long you wait for it. Mercury 2 finishes a FRAMES query in 10.8 seconds, against 19.8 for Gemini 3.5 Flash Lite, 21.0 for Claude Haiku 4.5, and 38.8 for GPT-5 Mini. And per *correct* answer (the number that reaches your bill) Mercury 2 is the lowest of the four on both benchmarks: **$0.047 on FRAMES against $0.072, $0.097 and $0.133; $0.432 on DeepSearchQA against $0.457, $0.676 and $0.938.**

So GPT-5 Mini buys ten points of DeepSearchQA accuracy for 3.6x the latency and still costs slightly more per correct answer than Mercury 2 does. In a pipeline that fires a model a hundred times per query, that trade doesn't close.

One honest note on DeepSearchQA: it costs three to seven times more than FRAMES for every model, because breadth means more turns and every extra turn re-sends a growing transcript. Cost in an agentic pipeline is driven by turn count and input volume, not by output length or unit price. Which is another way of saying that the number of steps you can afford is what decides what your pipeline costs to run.

## How Mercury 2 lost on WideSearch

There's a problem underneath every number above, including ours. We found it because Mercury 2 lost.

Mercury 2 scored worse than Gemini 3.1 Flash Lite on WideSearch, an agentic-search benchmark. A customer asked why. So we dug in and ended up running the benchmark with retrieval turned **off**. If a benchmark measures search, unplugging the search should be devastating.

Every model gains from retrieval except Gemini, which scores slightly *worse* with search (−0.02) than without it. It isn't searching; it's reciting. WideSearch tasks are built from facts older than every model's cutoff (e.g. university rankings, product specs, 2022 house prices ) so a model can ignore every page it retrieves and answer from its weights. Nobody's cheating; it's what the grader rewards. The score looks like search. It's recall.

For a search product this distinction is the whole ballgame. A model that answers from memory will confidently contradict your index, your catalog, your freshly-crawled pages, and look great on a benchmark while doing it.

One task makes it concrete. `ws_en_034` asks for UK monthly house prices and instructs the model to cite every statistic from government websites, retrieval by construction. With search on, the agent couldn't verify the figures in its sources and returned a blank table: **0.03**. Closed-book, it recited plausible numbers from memory: **0.86**. Faithful loses to fluent, by a factor of thirty.

So we rebuilt the tasks from events after every model's training cutoff (e.g. the 2026 World Cup group stage, the French Open, Cannes, Eurovision). Same format, same official grader, nothing memorizable. Closed-book scores collapse to **zero** for every model, confirming the tasks can't be recalled. With retrieval on, Gemini scores **0.929** and Mercury 2 scores **0.923**.

That's a tie, and we're reporting it as one. On data where the score is purely retrieval and synthesis, a diffusion model running several times faster per step does the same quality of work as a frontier autoregressive model.

**SealQA**, a contamination-resistant benchmark refreshed monthly, shows the same signature from the other direction: Gemini's closed-book lead lives entirely in pre-2024 questions, fades as the facts get fresher, and *flips to Mercury* on post-cutoff 2026. Same setup throughout — the only variable is whether the answer was memorizable.

Before you benchmark a model for search, run three checks:

- turn retrieval off (if the score holds, you're grading recall)
- include post-cutoff questions no model could have memorized
- confirm the gold answers are retrievable, not just true.

Everything above is reproducible. Bring your own keys and run it on any model, including ours:[ github.com/apoorvumang/retrieval-vs-recall](https://github.com/apoorvumang/retrieval-vs-recall)

## What's next

Search is the clearest case for parallel generation because it's the workload that runs an LLM the most times per unit of user patience. The same shape shows up anywhere a pipeline fires a model repeatedly. Agentic research is the obvious next step. Reducing per-step latency by 5x to 10x turns an overnight research job into something you finish within a reasonable wait time.

**Try Mercury 2**. The API is live at[ platform.inceptionlabs.ai](https://platform.inceptionlabs.ai/). 

**Benchmarking a production search pipeline?** We'll provision higher throughput capacity so you can measure real-world latency on your own query mix, and we'll help you run the retrieval-off ablation on your own eval set.[ Get in touch with our engineers.](https://www.inceptionlabs.ai/enterprise#contact-sales)
