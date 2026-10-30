---
vendor: together_ai
title: DeepSeek-V4 Flash 0731 vs GPT-5.6 Luna on DeepSWE: Cost and Coding
original_title: 
url: https://www.together.ai/blog/deepseek-v4-flash-0731-vs-gpt-5-6-luna-on-deepswe-cost-and-coding
date: 2026-08-06
lang: en
captured: 2026-10-30
extractor: readability-v1
status: ok
body_sha: dcbfafbafb61
---

All blog posts

Model Library

Published 8/6/2026

# DeepSeek-V4 Flash 0731 vs GPT-5.6 Luna on DeepSWE: Cost and Coding

The open-weight model setting the new price-intelligence bar

- AuthorsZain Hasan, Shobhit Dixit
- Table of contents[40+ Models Chosen for Production...40+ Models Chosen for Production...40+ Models Chosen for Production...](https://www.together.ai/blog/deepseek-v4-flash-0731-vs-gpt-5-6-luna-on-deepswe-cost-and-coding)

Key Takeaways

While GPT-5.6 Luna is the stronger engineer on every quality measure, DeepSeek-V4 Flash 0731 is cheap enough that a DeepSeek-first cascade beats Luna alone on both accuracy and cost.

- GPT-5.6 Luna leads DeepSWE pass@1 decisively at 67.2% vs 53.3%, a 14 point gap, and holds the lead at every equal attempt count.
- DeepSeek-V4 Flash is the cheapest model on the DeepSWE board: $0.10 per rollout vs $0.61, delivering 532 solves per $100 against Luna's 110.
- DeepSeek-V4 Flash fails more cleanly, breaking the repo's existing test suite in 9% of failures vs Luna's 15%.
- Running DeepSeek-V4 Flash first and escalating to Luna only on failure solves 78.9% of tasks at $0.385 each: more accurate than Luna alone and 37% cheaper.

Available now · Open weights

Run DeepSeek-V4 Flash on Together AI

The cheapest model on the DeepSWE board, about ten cents a task. Serve the cheap first stage at production scale without frontier token prices.

Open the playground


[DeepSeek-V4 Flash 0731](https://www.together.ai/models/deepseek-v4-flash-0731) is the cheapest model on the entire DeepSWE board: about ten cents a task! GPT-5.6 Luna, a solid upper-tier flagship, runs $0.61 a task, roughly six times [DeepSeek](https://www.together.ai/models-providers/deepseek)’s price. So the question is not which one wins the leaderboard (Luna, comfortably) but what six-times-cheaper buys you, what it costs you, and whether the two together beat either one alone.

We ran DeepSeek-V4 Flash 0731 (max) against GPT-5.6 Luna (max) on all 113 DeepSWE tasks: real, long-horizon feature requests from live open-source repos, four trials each, graded pass/fail by a hidden test suite. That is 900 rollouts in total from the published per-trial records (452 on DeepSeek's side, 448 on Luna's). Every figure below comes from this run, so it can differ from other public scorecards.

## **At a glance**

DeepSWE · Head to Head

### DeepSeek-V4 Flash vs GPT-5.6 Luna at a glance

| Model | Pass@1 | Avg cost | Out tok | Steps |
| --- | --- | --- | --- | --- |
| gpt-5.6-luna [max] | **67% ± 4%** | $0.61 | 73k | 102 |
| deepseek-v4-flash [max] | 53% ± 4% | **$0.10** | 108k | 153 |

Luna is ~6x the cost for ~14 points more accuracy; DeepSeek uses more output tokens and steps to get less far, but at $0.10 it is the cheapest run in the set by a wide margin.

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a755ae9f29796baf154f58d_08-accuracy-cost-effort.png)

## **The DeepSWE scoreboard: pass@1 and pass@k**

Luna wins single shot clearly: 67.2% pass@1 to DeepSeek's 53.3% under DeepSWE's official scoring, a 14 point lead, or about 26% more accurate in relative terms. At equal attempt counts Luna stays ahead at every k (81.6 vs 70.1 at two attempts, 90.3 vs 80.5 at four). On raw solving ability, this is not a close fight.

But DeepSWE is exactly the kind of workload where you can fan out several attempts in parallel, and there the economics rewrite the picture. DeepSeek's pass@2 (70.1%) already edges Luna's single shot (67.2%), and two DeepSeek attempts cost about $0.20 to Luna's $0.61. If a verifier can pick the winning run, the cheap model matches the flagship's first-try quality for a third of the price, before any of the routing tricks below even come into play.

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a7537e9d60a38a5c400d7e0_01-solve-rate-by-attempts.png)

## **Cost comparison: DeepSeek-V4 Flash vs GPT-5.6 Luna pricing**

- At $0.61 a task, Luna returns 110 solves per $100 to DeepSeek's 532: a 4.8x value edge for the cheap model. The cost per rollout gap is about 6x.
- The one thing the cheap model does not buy you is speed, and this is the twist versus the usual "flash" model story: DeepSeek is the slower of the two here, taking a median 23 minutes and 148 steps to Luna's 16 minutes and 92. It grinds (and emits more output, 104k median tokens to Luna's 70k). DeepSeek's advantage is money, not time.
- That wall-clock gap is partly an artifact of how new the model is; expect it to shrink as inference engines get tuned for it.

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a7537fb7738b3678fd7a4eb_02-cost-value-speed.png)

## **Failure modes: DeepSeek fails more gracefully than the flagship**

The other thing the cheap model quietly wins is discipline. When DeepSeek fails, it breaks the repository's existing test suite in only 9% of failures. Luna does so in 15%: the GPT-family regression signature, the same 15 to 20% we see across Sol and the other OpenAI-lineage models. Both fail mostly by near miss (DeepSeek 69%, Luna 66%), but the more expensive model is the one more likely to disturb code that already worked. If you deploy Luna, gate it behind a full regression run; DeepSeek needs that guardrail less.

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a7538243beaa9328632f73d_03-failure-anatomy.png)

## **DeepSeek-V4 Flash vs GPT-5.6 Luna by task domain**

Classify the 113 tasks by what the code actually is, and Luna wins 7 of 8 domains. Its biggest edges are exactly the reasoning-heavy work: program analysis (69 vs 33), concurrency and durability (70 vs 38), language and runtime internals (86 vs 59), roughly a 30 point gap in each. This is where model capability actually shows up, and DeepSeek falls off hard.

DeepSeek holds exactly one domain, and it is a telling one: query and config languages, 78 vs 70. The SQL builders, window functions, keyset pagination, config parsers. Structured, schema-shaped, convention-following work is where the cheap model is genuinely competitive, even ahead. Everywhere the task demands holding a hard invariant across a whole system, Luna's capability separates.

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a75382dae51b2becd28595c_04-solve-rate-by-task-domain.png)

## **DeepSeek-V4 Flash vs GPT-5.6 Luna by programming language**

Luna wins all five, but the margins tell you where to be careful with DeepSeek. It is respectable on Rust (55 vs 60) and Go (62 vs 79), but its JavaScript is a collapse: 35 vs Luna's 60, the weakest single cell in the entire matchup, and a 25 point hole. DeepSeek's Python is also soft (49 vs 65). If your stack is JS-heavy, the cheap model is a false economy; if it is config, query, or Rust, DeepSeek closes most of the gap.

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a753839093e357145b4f8e6_05-solve-rate-by-language.png)

## **How similar are DeepSeek-V4 Flash and GPT-5.6 Luna?**

Less than the cheap-tier pairs. Per-task correlation is 0.50, and the diversity is lopsided: they both solve 87 tasks, Luna alone gets 15, and DeepSeek alone gets only 4. Crucially, there is no task DeepSeek sweeps that Luna misses entirely (zero four-for-zero corners in DeepSeek's favor), while Luna sweeps four that DeepSeek never lands (go-critic-doc-link-checker, langchain-request-coalescing, meriyah-explicit-resource-declarations, superjson-error-stack-serialization). Their union covers 106 of 113 (93.8%), but almost all of that is Luna's own reach. As a raw diversity play, DeepSeek adds little.

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a753840433021ff99b04a3f_06-task-level-agreement.png)

## **The portfolio play: why the cascade works anyway**

So the pairing should be pointless. It is not, and the reason is the price. Run DeepSeek first and escalate to Luna only when your test suite rejects the answer: 78.9% solved at $0.385 per task. Read that carefully. It is more accurate than Luna alone (67.2%, up 11.7 points) and cheaper than Luna alone ($0.61), landing at about 63% of Luna's per-task cost.

The near-free first stage is the entire trick: DeepSeek clears roughly 53% of the queue for a dime each, so Luna's charge only ever touches the hard remainder, and the tasks that reach Luna get a second independent attempt on top. The cascade even beats a perfect one-shot oracle router (74.3%), because two swings beat one perfect pick. Accuracy is identical whichever model leads, but DeepSeek-first is much cheaper ($0.385 vs $0.64), so always lead with the cheap one.

The pair's ceiling is 93.8%; the 7 tasks neither ever solves (including gql-incremental-graphql-delivery and bandit-structured-nosec-directives) need a stronger third model, not a better router.

![__wf_reserved_inherit](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6a75384f88064ca1d33a4adf_07-cascade.png)

## **What it means**

On its own, DeepSeek-V4 Flash 0731 is a mid-pack model with one real domain (query and config), a clean failure profile, a catastrophic JavaScript weakness, and an unbeatable price. GPT-5.6 Luna is the better engineer by every quality measure: 14 points of pass@1, 7 of 8 domains, all 5 languages, faster too. You pay about 6x for it, plus a GPT-family regression habit to guardrail. At $0.61 a task the flagship is genuinely cheap, and it is the easy default when quality is what you care about. But the sharpest use of DeepSeek is not as a Luna replacement; it is as a Luna front-end. A first stage that costs a dime and clears half the work lets you buy flagship-beating accuracy for less than the flagship's own price. When the cheap model is this cheap, the cascade stops being a compromise and becomes the best row on the board.

Available now · Open weights

Run DeepSeek-V4 Flash on Together AI

The cheapest model on the DeepSWE board, about ten cents a task. Serve the cheap first stage at production scale without frontier token prices.

Open the playground

## **Appendix: Data Table**

DeepSWE · Appendix

### DeepSeek-V4 Flash vs GPT-5.6 Luna: full data table

| Metric | DeepSeek-V4 Flash 0731 (max) | GPT-5.6 Luna (max) |
| --- | --- | --- |
| pass@1 (official scoring) | 53.3% | **67.2%** |
| pass@1 (errors as failures) | 53.3% | **67.2%** |
| pass@2 / pass@4 | 70.1 / 80.5% | **81.6 / 90.3%** |
| Coverage / reliability | 80.5 / 66.2% | **90.3 / 74.8%** |
| Solid (4/4) / walls (0/4) | 23 / 22 | **43 / 11** |
| Cost per rollout / total | **$0.10 / $45** | $0.61 / $273 |
| Solves per $100 | **532** | 110 |
| Median minutes / steps | 23 / 148 | **16 / 92** |
| Median peak context / output tokens | 202k / 104k | 202k / 70k |
| Failure anatomy | **69% near, 9% regression** | 66% near, 15% regression |
| Domains won (of 8) | 1 (query & config) | **7** |
| Languages won | none | **all 5** |
| Per-task correlation / union | 0.50 / 106 of 113 (93.8%) |  |
| Cascade DeepSeek > Luna (accuracy / cost) | **78.9% / $0.385** | vs Luna alone 67.2% / $0.61 |
| Oracle 1-shot router | 74.3% |  |
| Leaderboard rank (of 52 configs) | 30th | **13th** |
| Infra errors | 0 | 0 |

## **FAQs**

### **Is GPT-5.6 Luna better than DeepSeek-V4 Flash?**

On quality, yes. GPT-5.6 Luna wins DeepSWE pass@1 67.2% to 53.3%, leads at every equal attempt count, wins 7 of 8 task domains and all 5 languages, and is faster. DeepSeek-V4 Flash wins on price by roughly 6x per rollout and fails more cleanly when it does fail.

### **How much cheaper is DeepSeek-V4 Flash than GPT-5.6 Luna?**

In our run, DeepSeek-V4 Flash cost about $0.10 per rollout versus $0.61 for GPT-5.6 Luna, roughly a sixth of the price. Measured per solved task, DeepSeek returned 532 solves per $100 against Luna's 110, about 4.8x the work per dollar.

### **Should you use DeepSeek-V4 Flash and GPT-5.6 Luna together?**

Yes, in a cascade. Running DeepSeek first and escalating to Luna only when the test suite rejects the answer solved 78.9% of tasks at $0.385 each in our run: more accurate than Luna alone (67.2%) and cheaper than Luna alone ($0.61). Always lead with the cheap model; accuracy is the same either way but DeepSeek-first costs less.

### **Which is better for coding, DeepSeek-V4 Flash or GPT-5.6 Luna?**

Luna wins every language in our breakdown, but the margins vary. DeepSeek is respectable on Rust and competitive on query and config work, where it actually leads. Its JavaScript is the weakest cell in the matchup (35 vs 60), so JS-heavy stacks should not rely on the cheap model alone.

### **What is pass@k on DeepSWE?**

pass@k measures whether at least one of k attempts at a task passes the hidden test suite. pass@1 rewards getting it right first try; higher k rewards a model that can eventually reach a solution across several tries. DeepSeek's pass@2 (70.1%) already edges Luna's pass@1 (67.2%), which is what makes the parallel-attempt and cascade economics work.

## Related articles

View All

View All
