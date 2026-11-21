---
vendor: moonshot_kimi
title: Kimi Introduces Agent Swarm: Let 100 AI Agents Work for You
original_title: 
url: https://www.kimi.com/blog/agent-swarm
date: 2026-02-09
lang: en
captured: 2026-11-21
extractor: readability-v1
status: ok
body_sha: 70f3302d55dc
---

# Kimi Introduces Agent Swarm: Let 100 AI Agents Work for You

![Introducing Agent Swarm](https://kimi-file.kimi.ai/prod-chat-kimi/kfs/4/2/2026-02-13/1d67gvgudcmosb3rlf92g?x-tos-process=image%2Fauto-orient%2C1%2Fstrip%2Fignore-error%2C1)

In 2025, if you walked into any AI conference, you may hear the same gospel: faster inference, longer context windows, cheaper inference costs.

It's as if we've spent years perfecting the hammer, making it lighter, stronger, more precisely balanced, while never questioning the fact that the carpenter still has only two hands and twenty-four hours in a day.

**Now, Kimi introduces Agent Swarm.** It is not a better hammer. It is a reconstruction of the entire workshop.

This is not the story of "many AI agents working together". What we're building is an organizational structure with bosses, employees, and divisions of labor, except this organization isn't designed by humans. **It designs itself.**

When you tell Agent Swarm to research a topic, you aren't commanding an assistant. You are hiring a CEO, who helps find researchers, analysts, fact-checkers, all hired on the spot on its own. **And you don't need to micromanage.**

But to get there, we had to confront a question that we used to avoid:

## The Limits of Single-Agent Reasoning

How far can we really push a model at test time?

This question isn't really about intelligence. The real bottleneck in AI reasoning today is the single-agent, sequential execution model itself.

Whether you're trying to extend the length of tasks a model can handle (what researchers call long-horizon tasks), or dynamically scaling compute and structure during inference (test-time scaling), the single-agent sequential execution model hits a wall.

For example, ask a single-agent deep research tool to survey a hundred companies or synthesize dozens of papers. As the task goes on, the context window fills. The system falls back to simple history folding or summarization to make room for new tokens. This compression is lossy, and later reasoning degrades.

It's not a bug, nor a temporary limitation. It's a structural ceiling imposed by context windows, time, and the constraints of relying on a single agent to manage long-horizon reasoning.

## Scale Out, Not Just Up

For many years, the dominant narrative in AI has been scaling: bigger models, more parameters, better benchmark scores. This narrative has delivered remarkable results. But vertical scaling has a ceiling—physical, economic, and perhaps intellectual.

Horizontal scaling is different. One brain versus many. A single model is one expert. A self-organizing network is a company, a laboratory, an intelligence agency.

In June 2025, shortly after we launched Kimi Researcher, a member of our team — let's call her an "enthusiastic amateur stock trader"—had an idea that seemed simple enough: Could Kimi automatically gather daily information about stocks?

She let Kimi check news for macro trends. Query historical limit-up counts. Drill deeper if conditions match. Synthesize. She wrote a Python workflow, a cascade of if-else statements.

At line one hundred, she stopped. *"I'm hand-coding a multi-agent system."*

If models can use tools and handle long-horizon tasks, why can't they architect themselves? Decide when to parallelize, whom to hire, how to delegate?

**The future isn't better single agents. It's agents that build organizations.** Agent Swarm was born from this hypothesis.

The numbers tell part of the story. With Agent Swarm, Kimi K2.5 can:

- Deploy up to **100 sub-agents** working in parallel
- Execute over **1,500 tool calls**
- Deliver better results **4.5x faster** than sequential execution

## Agent Swarm Best Practices

Obviously, Agent Swarm excels where work parallelizes: broad research, batch downloads, multi-file processing, multi-angle analysis, long-form writing.

But the deeper benefit is structural, it creates **the conditions for productive disagreement** — for independent agents to arrive at different conclusions, then force a reconciliation. **It avoids groupthink structurally.**

So in the following cases, we suggest you experience the magic of agent swarm.

### Discovery at Scale

Start with the simplest case: finding **a mountain of things** that are hard to find.

Say you need the top 3 creators in 100 niche YouTube domains. K2.5 Agent Swarm first researches and defines each domain, then autonomously **creates 100 sub-agents to conduct parallel searches.**

Or you want to collect all 200+ Paul Graham essays, scattered across personal sites, old blogs, transcribed talks. K2.5 Agent Swarm can assign specialized sub-agents to search for, download, categorize, summarize, and compile Paul Graham's essays. They collectively organize over **200 original essays** into **6 topic-based folders** and produces a comprehensive summary report.

![100 Sub-agents Hunting for Creators](https://kimi-file.kimi.ai/prod-chat-kimi/kfs/4/2/2026-02-09/1d64nsivf2ena627qcitg?x-tos-process=image%2Fauto-orient%2C1%2Fstrip%2Fignore-error%2C1)

> 100 Sub-agents Hunting for Creators: https://www.kimi.ai/share/19c40eea-b272-8ef2-8000-0000af5e0baa

### Output at Scale

Beyond gathering scattered information, you can task Agent Swarm with **consuming massive document sets** and coordinating expert personas to **produce book-length, professional-grade reports.**

For example, let it generate a 100-page literature review from forty social psychology PDFs. K2.5 Agent Swarm decomposes the task across the document set, deploying multiple writing-focused sub-agents. Each claims responsibility for specific sections, and their outputs are synthesized into a **100-page, two-column** academic document with fully formatted citations and references.

![Generate 100-Page Literature Review from 40 PDFs](https://kimi-file.kimi.ai/prod-chat-kimi/kfs/4/2/2026-02-09/1d64nuepl51jas5bh88fg?x-tos-process=image%2Fauto-orient%2C1%2Fstrip%2Fignore-error%2C1)

> Generate 100-Page Literature Review from 40 PDFs: https://www.kimi.ai/share/19c4106b-89b2-8361-8000-0000d07b8235

### Perspective at Scale

The most interesting use case is when you need the disagreement itself—when you want to see a problem through multiple perspectives at once.

**Facing a complex product launch?** Deploy a team of experts: the skeptical VC questions unit economics, the veteran PM worries about technical debt, the ethicist probes dark patterns, customer success lead champions edge cases.

![Get your product plan reviewed by a team of experts](https://kimi-file.kimi.ai/prod-chat-kimi/kfs/4/2/2026-02-09/1d64nu0d3v89kkema91ag?x-tos-process=image%2Fauto-orient%2C1%2Fstrip%2Fignore-error%2C1)

> Get your product plan reviewed by a team of experts: https://www.kimi.ai/share/19c40bc9-31a2-8533-8000-0000bad59b7a

**Or explore different story directions.** You can have 20 writers from different literary styles to continue Liu Cixin's *The Three-Body Problem*: from Virginia Woolf–style inner monologues to Borges-like idea mazes, Kafkaesque absurd worlds, and Gabriel García Márquez–style stories shaped by repeating fate.

![Let 20 writers create alternative endings for The Three-Body Problem](https://kimi-file.kimi.ai/prod-chat-kimi/kfs/4/2/2026-02-09/1d64nvf7f2ena627qcve0?x-tos-process=image%2Fauto-orient%2C1%2Fstrip%2Fignore-error%2C1)

> Let 20 writers create alternative endings for The Three-Body Problem: https://www.kimi.ai/share/19c409c8-8692-821a-8000-0000070ad369

## Now Available to Top Tier Subscribers

You once had Kimi Agent as a single, diligent researcher. You now have Kimi Agent Swarm as a team of experts: specialized, parallel, capable of holding contradictory viewpoints simultaneously.

This is an early research preview. We will continue to harden the architecture, introducing direct sub-agent communication, dynamic control of parallel width—but the foundation is ready for your most demanding work.

In the AI age, literacy may be measured by how many tokens we use.

So type your prompt, and let Kimi self-direct 100 sub-agents for you: [https://www.kimi.com/agent-swarm](https://www.kimi.com/en/?agent=1&swarm=1)
