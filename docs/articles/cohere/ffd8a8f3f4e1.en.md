---
vendor: cohere
title: The future of work debate has an evidence problem
original_title: AI Future of Work Evidence Gap
url: https://cohere.com/blog/the-future-of-work-debate-has-an-evidence-problem
date: 2026-06-10
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 401972704bd1
---

Jun 10, 2026

7 minute read

# The future of work debate has an evidence problem

Key takeaways

- A 2023 paper estimating that 80% of U.S. workers have tasks exposed to large language models has been cited by the IMF, European Parliament, and referenced in U.S. Senate proposals. Three years later, the mismatch between this paper's original conclusions and where its findings are being applied has consequences for policy decisions.
- The limitations of these scores are not independent; scores calculated against one model, using an American taxonomy, decomposed into discrete tasks, compounds rather than simply accumulates these constraints.
- More dynamic, representative, and actionable evidence measurement tools exist, however they are not reaching policymakers at the pace the policy conversation requires.
- Both policymakers and researchers have a role in closing the gap between the evidence we have and the decisions we need to make, and both need to start treating workers as partners in that process, not subjects of analysis.

Read the full report

**

You’ve probably heard that AI is coming for your job. The reality is more complicated than any single number suggests.

**When researchers talk about AI’s impact on the labor market, one of the most discussed concepts is “exposure”. An occupation’s exposure score is an estimate of how many of its core-work-tasks could plausibly be performed by an AI system, faster, cheaper, or just as well. The idea is straightforward: take a list of occupations, list the tasks each one involves, and ask how many of those tasks an AI *could* handle.

Exposure scoring exists because [empirical evidence about AI's actual labor market impact is inconclusive](https://www.piie.com/blogs/realtime-economics/2026/research-ai-and-labor-market-still-first-inning). The adoption of AI is moving faster than our current labor statistics systems can capture – historically, the effects of new technologies take years to show up clearly in employment and wage data. In the meantime, researchers turn to theoretical measurement: estimating, on the basis of what AI can plausibly do, which jobs are most likely to be affected. Exposure scores are one way to generate a working signal in the absence of harder evidence.

The most widely cited version of this estimate comes from a 2023 paper, “[*GPTs are GPTs*](https://arxiv.org/pdf/2303.10130),” by Eloundou et al. Their headline findings: 80% of the U.S. workforce has at least 10% of their occupational tasks exposed to large language models, and 19% have 50% or more. These numbers have traveled widely – they have been cited by the [IMF](https://www.imf.org/en/publications/wp/issues/2023/10/04/labor-market-exposure-to-ai-cross-country-differences-and-distributional-implications-539656), the [OECD](https://www.oecd.org/en/publications/macroeconomic-productivity-gains-from-artificial-intelligence-in-g7-economies_a5319ab5-en.html), referenced in [U.S. Senate proposals](https://www.sanders.senate.gov/wp-content/uploads/10.6.2025-The-Big-Tech-Oligarchs-War-Against-Workers.pdf), and built upon by research institutions across multiple countries. The figure below maps this distance across recent AI labor market research:

Like all empirical tools, the *GPTs are GPTs* scores are a bounded instrument, and the distance between what they were designed to answer and what they are being asked to support deserves attention.

### What do these scores measure?

The GPTs are GPTs scores measure the technical feasibility of a GPT-4-era model, evaluated against the U.S. Department of Labor’s occupational taxonomy, for tasks with verifiable outputs that can be completed faster with AI assistance. That is a specific and answerable question, and the paper addresses it carefully.

But that specificity matters for three main reasons:

- The scores reflect a model from early 2023. Since then, frontier AI capabilities have improved substantially, with [one index](https://epoch.ai/eci?view=graph&tab=release-date&subset-view=graph&subset-tab=Software+engineering) estimating a roughly 26 percentage point gap between the model represented by the *GPTs are GPTs* scores and current AI capabilities.
- The scores are built on an American occupational taxonomy that does not transfer cleanly onto other labor markets, even with translation.
- The scores model work as a bundle of discrete, scorable tasks, which captures what can be itemized but not the judgment, relationships, and context that often constitute the most consequential parts of a job.

These are all limitations the original authors acknowledged, and [recent work begins to formalize](https://www.nber.org/papers/w35110). But what happens when the scores travel beyond those boundaries*?*

### What happens when these scores drive policy?

Policymakers are under pressure to act. They need to know which workers will need support, which industries are at risk, what kinds of interventions are justified and when to enact them. The* GPTs are GPTs* scores have become a primary input to those discussions, appearing in [government reports](https://www.stlouisfed.org/on-the-economy/2025/aug/is-ai-contributing-unemployment-evidence-occupational-variation), [think tank policy briefs](https://britishprogress.org/reports/ai-and-the-uk-labour-market-the-evidence-so-far), and [U.S. Senate proposals](https://www.sanders.senate.gov/wp-content/uploads/10.6.2025-The-Big-Tech-Oligarchs-War-Against-Workers.pdf).

But the questions policymakers are asking require more information than static exposure scores alone can provide. **A score calculated against a 2023 model, using an American taxonomy, treating work as a bundle of discrete tasks, is being used to inform decisions about workers in 2026 and beyond, in labor markets outside the U.S., doing jobs that involve far more than itemizable tasks. The limitations don’t disappear when the scores cross those boundaries. They compound.

**The scores driving the future of work debate reveal which work appears to be automatable. However, this is a representation of one possible future under one set of assumptions. When work is viewed through a different lens, [different definitions of exposure emerge](https://budgetlab.yale.edu/research/labor-market-ai-exposure-what-do-we-know).

This should also prompt us to ask, *what’s missing? *Which workers, regions, and futures of work are not represented by these figures? Notably, the dataset contains no discrete categories for [data workers](https://www.youtube.com/watch?v=aooiDA-AsNo)—the actual labor that powers AI systems. The labor of these workers is structurally embedded in every LLM whose capabilities O*NET tasks are being evaluated against, yet they remain outside the policy debate those scores enable.

A recent [ILO review](https://www.ilo.org/publications/workers%E2%80%99-exposure-ai-what-indicators-tell-us-%E2%80%93-and-what-they-don%E2%80%99t) of AI exposure research concluded plainly: the most widely used indicators tell us something meaningful, but not everything we need to know about who is at risk and why.

### The research community is responding

Researchers have not been standing still. A growing body of work is emerging which directly addresses the gaps in static exposure scoring.

- **Dynamic indexes **evaluate AI capabilities as they exist today rather than in 2023, and link those evaluations to real labor market data. [One recent study](https://arxiv.org/pdf/2507.08244) finds that a 10-point increase in occupation-level exposure is associated with a 5.6 to 8.5 percentage point decline in employment, among the first empirical evidence that dynamically-measured exposure predicts actual labor market outcomes rather than just theoretical susceptibility.
- **Ensemble approaches **combine multiple exposure frameworks, weighted to emphasize the most informative element of each score. [This produces a more reliable estimate](https://academic.oup.com/pnasnexus/article/4/4/pgaf107/8104152) than any single framework can provide alone. Individual scores, which differ across methodology and institution, turn out to be weakly or even negatively correlated with each other, meaning they are capturing different dimensions of exposure.
- **Task-framework extensions **examine not just which tasks are exposed, but [how they fit together within a job](https://www.nber.org/papers/w34859). The sequencing and adjacency of AI-exposed tasks turns out to matter just as much as the raw share, a finding that changes which occupations appear most at risk.
- **Worker-centered measures **add what all of the above leave out: what workers want, and how prepared they are to navigate change. [One study](https://arxiv.org/pdf/2506.06576) finds a substantial category of tasks that AI could perform but that workers do not want automated. [Another maps workers’ adaptive capacity](https://www.brookings.edu/articles/measuring-us-workers-capacity-to-adapt-to-ai-driven-job-displacement/) alongside their exposure, finding that exposure alone does not map cleanly onto vulnerability.
- **Adoption and usage data** provides insight into how AI is actually used, rather than its theorized potential. Frontier labs have begun to analyze how their technology is used in the workplace, including reports on [Claude](https://www.anthropic.com/research/labor-market-impacts), [Copilot](https://arxiv.org/abs/2507.07935), and [ChatGPT](https://cdn.openai.com/pdf/the-ai-jobs-transition-framework_report.pdf).

Together, these approaches point toward a richer evidence base, one that uses the original scores as a starting point rather than a final answer.

### What we’re calling for

The future of work debate is [asking three distinct questions](https://www.nber.org/papers/w35046):

- whether AI capabilities will advance meaningfully,
- what that means for economic outcomes, and
- what the optimal policy responses are.

These questions are related, but not equivalent. We have the most evidence for answering the first (what AI can do). The questions about what happens when capable AI meets a working economy, and what we decide to do about it remain. Two groups in particular can take steps towards broadening this debate;

**Policymakers **should treat exposure scores as one signal among several. The most robust policy interventions are [those whose value does not depend on any single forecast being correct](https://knightcolumbia.org/content/ai-as-normal-technology): strengthening worker protections, investing in reskilling infrastructure, and building the institutional capacity to respond as impacts materialize. Workers should be engaged as partners in that process. They have direct knowledge of how their work is changing, and what they want the future of work to look like.

**Researchers **should prioritize building the evidence base that policy decisions actually require. That means measurement tools that update alongside AI capabilities, that extend beyond U.S. labor markets, and that connect directly to the questions policymakers are trying to answer. It also means [treating workers as epistemic partners](https://data-workers.org/wp-content/uploads/2025/08/DWI_Method_AIES-6.pdf) throughout the research process, not just as data sources. The goal is research that closes the distance between what we can measure and what policymakers can act on.

The 80% exposure figure describes technical feasibility under a particular set of assumptions at a particular moment in time. It is not a forecast, and it is not a mandate. The future of work will be shaped by decisions that researchers, policymakers, and workers make together. The evidence base those decisions rest on should be up to the task.

*For the full analysis and recommendations, [read our complete report](https://arxiv.org/abs/2606.23633).*

[Your occupation is in this data](https://cohere.com/labormap). The U.S. Department of Labor maintains O*NET, a public database that catalogs every U.S. occupation as a list of tasks—the same task list that underpins most AI exposure estimates, including *GPTs are GPTs*. See how O*NET tasks have been re-rated, dropped, or rewritten since GPT-4 and tell us whether any of it reflects how your work has actually changed.

## Read this next

- [![Logo depicting RCP-DCG](https://cdn.sanity.io/images/rjtqmwfu/web3-prod/ef9d5d5c1ab3414923df1fa97e3754ecc0a8f393-2912x1630.png?auto=format&fit=max&q=80&w=440)](https://cohere.com/blog/rcp-ndcg)[Technology](https://cohere.com/blog/tag/technology)[AI for Developers](https://cohere.com/blog/tag/ai-for-developers)[Research](https://cohere.com/blog/tag/research)[RCP-nDCG@10: A more complete way to measure retrieval relevanceSep 30, 20267 min read](https://cohere.com/blog/rcp-ndcg)
- [![Embed 5 logo on an abstract blue and black background.](https://cdn.sanity.io/images/rjtqmwfu/web3-prod/707e10f3b1b953018b94864b0a4b9e99a8843cde-3840x2160.png?auto=format&fit=max&q=80&w=440)](https://cohere.com/blog/embed-5)[Product Launch](https://cohere.com/blog/tag/product-launch)[Company News](https://cohere.com/blog/tag/company-news)[Introducing Embed 5—A new family of frontier embedding modelsSep 30, 20267 min read](https://cohere.com/blog/embed-5)
- [![Compass cloud logo](https://cdn.sanity.io/images/rjtqmwfu/web3-prod/3ff9058d77d0a46ac36c66e586eecb01128c3bba-3840x2160.png?auto=format&fit=max&q=80&w=440)](https://cohere.com/blog/compass-cloud-beta)[Product Launch](https://cohere.com/blog/tag/product-launch)[AI for Developers](https://cohere.com/blog/tag/ai-for-developers)[Compass is coming to the cloudSep 25, 20265 min read](https://cohere.com/blog/compass-cloud-beta)
