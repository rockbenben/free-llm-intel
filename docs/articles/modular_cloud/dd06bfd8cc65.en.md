---
vendor: modular_cloud
title: Modular’s bet to break out of the Matrix (Democratizing AI Compute, Part 10)
original_title: Modular: Modular’s bet to break out of the Matrix (Democratizing AI Compute, Part 10)
url: https://www.modular.com/blog/modulars-bet-to-break-out-of-the-matrix-democratizing-ai-compute-part-10
date: 2025-05-08
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 81cc2d5b3981
---

May 8, 2025

# Modular’s bet to break out of the Matrix (Democratizing AI Compute, Part 10)

Chris Lattner

Series

Over the course of this series, we’ve seen just how hard it is to break free from the matrix of constraints imposed by the status quo. Everyone wants a solution—developers, startups, hardware vendors—but nothing sticks. Promising efforts flame out. Clever hacks don’t scale. The pace of GenAI accelerates, while **Moore’s Law** fades and the stack only gets heavier.

While AI has unbounded optimism and hype, it also has problems - the purpose of this series is to shine a light on the complexities and challenges of AI infrastructure. It’s with this experience, plenty of scars, and a bit of bull-headedness that we finally said: enough. If we want a different outcome, we have to try a different approach.

That’s why Tim and I started Modular. Not because CUDA is evil—it isn’t. CUDA earned its place with brilliant engineering and relentless execution. The truth is, most people are frustrated with CUDA **because it won,** **the stakes are so high, and they yearn for something better.**

After two decades, the cracks are showing. CUDA—and the cathedral of software built atop it—have grown brittle. Complexity compounds. Innovation slows. What started as an accelerator is now a constraint. The real problem isn’t CUDA itself: [**it’s the complexity it drove into the AI software stack**](https://www.youtube.com/watch?v=pdJQ8iVTwj8&t=3884s)—a weight we all carry.

If we want a different future, we can’t just rail against the one we’ve got. We must **build something better, together**. Something that doesn’t just copy CUDA, but goes beyond it—solving the root problems it grew up around. Something simpler, more flexible, and more empowering for every AI developer.

The problem is that **this isn’t an incremental step**. It takes *years* of development from a large and focused team of experts to move the needle. Even if you can attract the experts, how do you **get them to work together** and avoid them getting dragged into the firefight of the day… for *years* at a time? This post explains how we started Modular—and why we believe it’s possible to break through the matrix of constraints and build a better foundation for AI.

Let’s see just how deep the rabbit hole goes. 🐇🕳️

# What does “Democratizing AI Compute” mean to me?

When we talk about democratizing AI compute, we don’t just mean “run it on more devices.” We mean rethinking ***who* gets to build *what*—and *how***. It means removing the gatekeepers, lowering the barriers, and leveling the playing field for developers, hardware vendors, and researchers alike.

Back in 2021, I gave an [industry keynote at a prominent academic conference](https://docs.google.com/presentation/d/1ZMtzT6nmfvNOlIaHRzdaXpFeaAklcT7DvfGjhgpzcxk/edit?slide=id.p#slide=id.p), laying out a vision for a unifying software layer that could finally bring the field together. I hoped someone would pick up the torch and build it. People were intrigued. Conversations sparked. But no one made it to the finish line.

So we asked a different question: **What if we designed the stack for AI developers first?** What if performance engineering wasn’t the exclusive domain of chip vendors and compiler gurus? What if these tools were *programmable*, *composable*, and *understandable*—so that *anyone* could build with them? I think we'd get more "[DeepSeek moments](https://www.modular.com/blog/democratizing-compute-part-1-deepseeks-impact-on-ai)" with innovation coming even faster from more innovators, helping the entire world.

I’ve seen this kind of transformation before. In 2010, the iPhone was an incredible technical platform—but Objective-C’s complexity was gatekeeping app development to experts. [Swift](https://www.swift.org/) changed that. It unlocked a wave of creativity, empowering an order of magnitude more developers to build great apps. Today, CUDA and other AI infrastructure face the same problem. The tools are powerful, but the complexity is crushing.

##### So: **how do we break past that?**

I believe the answer lies in the intersection of **usability, portability, and performance**. After working on highly specialized stacks for TPUs and other accelerators, I saw both the upside of vertical integration—and the downside of brittle systems that can’t evolve fast enough in a rapidly changing landscape.

That experience defined our metrics for success—[the scorecard we’ve been building](https://www.modular.com/blog/democratizing-ai-compute-part-8-what-about-the-mlir-compiler-infrastructure) throughout this series:

- Does it serve developers?
- Does it unlock full hardware performance?
- Does it enable innovation *above* and *below* the stack?
- Does it scale across use cases and chip types?
- Can you actually use it in production?

We need something inspired by the [design of LLVM](https://aosabook.org/en/v1/llvm.html)—but reimagined for the modern era of AI. A system where hardware makers can plug in their chips, express what makes them great, and still own their performance. A system where AI software developers can build at the frontier—*without* reinventing the stack every time.

That’s what “**Democratizing AI Compute**” means to us. Not just more devices. Not just lower cost. But a fundamentally open, modern foundation—one that unlocks progress for *everyone,* not just the trillion-dollar incumbents.

# How do we tackle an industry-scale problem?

There’s just one small challenge: building a [high-performance AI stack for a *single* chip is already hard](https://www.modular.com/blog/democratizing-ai-compute-part-9-why-do-hw-companies-struggle-to-build-ai-software). Solving it at **industry scale**—across devices, vendors, and workloads—is an order of magnitude harder.

This isn’t Clayton Christensen’s [*Innovator’s Dilemma*](https://en.wikipedia.org/wiki/The_Innovator%27s_Dilemma), where incumbents stumble because they ignore disruption. This is the *opposite* problem: **everyone sees the challenge. Everyone is trying to solve it.** And yet—despite smart people, serious funding, and real effort—most attempts stall out.

Let’s be honest: a lot of folks today believe the system *can’t* be changed. Not because they love it, but because they’ve watched team after team try—and fail. Meanwhile, the world keeps moving. GenAI explodes. Moore’s Law slows. The stack grows more brittle and complex. More chips are announced, but **CUDA remains the gravitational center of it all**. So why does nothing stick? Why do smart people with serious funding at the biggest companies keep hitting the same wall?

I’ve been through this before. I’ve seen—and helped solve—industry-scale problems like this. In my experience, when transformation keeps failing, it's not usually for lack of talent or funding. It's because **those projects aren’t solving the whole problem**. Instead of disruption theory, we need to understand why **new solutions** fail to stick.

For that, I’ve come to value a different lens: the [**Lippitt-Knoster Model for Managing Complex Change**](https://sergiocaredda.eu/organisation/models-the-lippitt-knoster-model-for-managing-complex-change). It outlines six things every successful transformation needs:

The Lippitt-Knoster Model for Managing Complex Change. Image credit:

Sergio Caredda

**Vision, Consensus, Skills, Incentives, Resources, and Action Plan.**

If any one of them is missing, change fails—and it fails in a *predictable* way.

- ❌ Weak vision → **Confusion** 😵‍💫
- ⚔️ Weak consensus → **Conflict & Resistance** 🙅
- 🧠 Inadequate skillset → **Stress & Anxiety** 😬
- 💸 Misaligned incentives → **Drag & Delay** 🐌
- 🪫 Insufficient resources → **Fatigue & Frustration** 😤
- 🌀 No clear plan → **False starts & Chaos** 🤯

We’ve seen all of this in previous blog posts: [OpenCL & SYCL](https://www.modular.com/blog/democratizing-ai-compute-part-5-what-about-cuda-c-alternatives), [TVM & XLA](https://www.modular.com/blog/democratizing-ai-compute-part-6-what-about-ai-compilers), [Triton](https://www.modular.com/blog/democratizing-ai-compute-part-7-what-about-triton-and-python-edsls), and even [MLIR](https://www.modular.com/blog/democratizing-ai-compute-part-8-what-about-the-mlir-compiler-infrastructure). The patterns are real—and the failures weren’t technical, they were **systemic**.

So if we want to break the cycle, we can’t just build great tech. We have to solve the *whole equation*. That’s the bar we set at Modular—not just to write a better point solution or design a slicker API, but to align **vision, capability, and momentum** across the ecosystem.

Because that’s what it takes for real change to stick—and that’s exactly what we set out to do.

# How we set up Modular to maximize odds of success

Once we understood the full complexity of the problem—and the long history of failed attempts—we knew we had to build Modular differently from day one. That meant engineering great software, yes—but also designing a team, a structure, and a mission that could sustain progress where so many others had stalled.

**We started with a clear vision**: to make [AI compute accessible, performant, and programmable](https://www.modular.com/blog/the-future-of-ai-depends-on-modularity)—for everyone. Not just for billion-dollar chipmakers or compiler wizards. For researchers, developers, startups, and hardware builders. That meant [rethinking and rebuilding the *entire* stack, not just optimizing one layer](https://www.modular.com/blog/the-case-for-a-next-generation-ai-developer-platform). We needed a system that could scale across use cases, not a point solution [destined to be thrown away](https://petewarden.com/2023/10/15/the-unstoppable-rise-of-disposable-ml-frameworks/) when AI shifts again.

**We **[**assembled a team**](https://www.modular.com/company/careers)** that had lived the pain**. Folks who helped build CUDA, TPUs, MLIR, TensorFlow, PyTorch, and many other software systems. We weren’t armchair critics—we wrote the code, built the infra, and lived the failures. That gave us a deep understanding of both the technical and human sides of the problem—and a shared sense of unfinished business.

But having great people isn’t enough. To take on an industry-scale challenge, we had to **empower them** with the right [environment and values](https://www.modular.com/company/culture). We focused early on **leadership, culture, and product excellence**, because we’d seen how quickly misaligned incentives can derail even great technology. We made space to “build things right” because so little in AI actually is.

**We are independent and focused on AI infrastructure**—because we knew we couldn’t truly serve the ecosystem if we were secretly trying to sell chips, cloud services, foundation models, or autonomous vehicles. Our incentive had to be aligned with the long-term success of AI software itself—not just one narrow application. We’re not building a chip. Or a cloud. Or a foundation model. We’re building the *neutral ground*—the infrastructure others can build on. An enabler, not a competitor.

**We also needed scale.** This is a huge vision, and requires not just talent and alignment, but serious resources to pay for it. We were fortunate to raise enough funding to launch this mission. Even more importantly, we were backed by investors like [Dave Munichiello at GV](https://www.gv.com/team/dave-munichiello) and the [team at General Catalyst](https://www.generalcatalyst.com/team)—people who brought not only deep technical understanding, but long time horizons and conviction about what success could mean for the entire field.

All of this was just the starting point. With the fundamentals in place—clear vision, the right people, aligned incentives, and enough runway—we could finally begin building. But there was still one enormous problem: **there was no shared direction in the industry.** No common foundation. No unifying plan. Just a tangle of competing tools, brittle abstractions, and hardware racing ahead of the software meant to support it. We had many ideas—but no illusions. Real progress meant solving what the industry had failed to crack for over a decade: **a massive open research problem**, with no guaranteed answers.

# How to tackle a massive open research problem

AI isn’t a sleepy industry, and the pace of system-building isn’t calm either. It’s a [hardware regatta in a turbulent sea](https://www.modular.com/blog/democratizing-ai-compute-part-9-why-do-hw-companies-struggle-to-build-ai-software) 🌊.

Everyone’s racing—the startup speedboats 🚤, the focused yachts ⛵, the megacorp ocean liners 🛳️, and of course, NVIDIA’s aircraft carrier 🚢. They’re all jockeying for position—building chips and stacks, launching foundation models and platforms, locking down APIs while chasing the next GenAI breakthrough. And while they collide, the sea is littered with wreckage: churn, complexity, fragmentation… and a graveyard of half-built stacks.

**We took a different path. We got out of the water and took to the air. ✈️**

Instead of entering the same race and dodging torpedoes, we made space for deep research. We stepped back, recharted the map, and spent *years* quietly working on problems others had circled for a decade but never solved. And yes, some people told us we were crazy.

(This popular meme is actually from

This is a Book

by Demetri Martin)

> 🧪 Taking years for fundamental R&D sounds slow… until you realize everyone else has been stuck for a decade.

While others chased accelerators and point solutions, [we proved generality on CPUs](https://www.modular.com/blog/the-worlds-fastest-unified-matrix-multiplication)—because if it works on CPUs, it can work anywhere. While the world narrowed toward vertical silos, we doubled down on programmability and flexibility. Because the only way to crack a grand challenge isn’t just to race faster—it’s to build something fundamentally new.

We also stayed deliberately closed—not because we don’t know open ecosystems, but because **consensus kills research**. Sometimes, you need space to *figure things out* before inviting the world in. I learned this the hard way with [OpenCL](https://www.modular.com/blog/democratizing-ai-compute-part-5-what-about-cuda-c-alternatives) and [MLIR](https://www.modular.com/blog/democratizing-ai-compute-part-8-what-about-the-mlir-compiler-infrastructure): everyone has opinions, especially in infrastructure, and too many inputs and constraints too early just slows you down.

We took flack for that. But let’s be clear:

> We're not here to win points on Twitter. We’re willing to do the hard thing in order to make fundamental progress.

# Scaling into this deliberately: one step at a time

With space to do the fundamental work, we tackled the hard problems head-on—and scaled deliberately, one milestone at a time. First, we had to prove that a new approach to code generation could actually work. Then came syntax, usability, performance, and ecosystem fit.

As we built the platform, we were our own first users. We hit the bugs, ran into the limitations, struggled through the early pain—and used that pain to guide our priorities. That kept us honest.

No proxy metrics. No vague abstractions. Just one question:

> Can real engineers build real systems, faster, with this?

We kept raising the bar. First, it was PyTorch, TorchScript, and ONNX. Then TensorRT-LLM, vLLM, and the bleeding edge of GenAI workloads. And when we finally got to H100 earlier this year—with a tiny team and no vendor hand-holding—we brought it up from scratch, tuned it ourselves, and got real models running in under two months.

> Most teams don’t even have their kernel compiler booting in two months. We were already running production-grade models at performance matching the rest of the world. This was on the most popular hardware that had been tuned by the entire world for years at this point.

That’s the kind of pressure that forges breakthroughs. Because in this space, if you’re not catching up from behind while the bar keeps moving, you’re not even in the race. Getting here took over three years of methodical, closed development. But from the very beginning, we weren’t building just for ourselves. We always knew this had to scale beyond us.

We’re not here to build everything—we’re here to build the **foundation**. A foundation that’s fast, flexible, and open. One that can scale with the industry, adapt to new use cases, and help everyone go faster. But that only works if it's open so the whole community can participate.

# Modular is now Open!

After more than three years of heads-down R&D, we’re officially out of the lab—and into the wild. Modular is now in full execution mode: shipping major releases every 6–8 weeks, and developer builds nearly every night. The platform is working. The stack is coming together. The APIs are starting to settle.

This means it’s time to open the doors—and see what *you* can build with it.

[We’ve just open-sourced over half a million lines](https://www.modular.com/blog/modular-platform-25-3-450k-lines-of-open-source-code-and-pip-install-modular) of high-performance GPU primitives—optimized, portable, and ready to run across multiple architectures. Alongside that, we’ve released serving infrastructure, models, and more. You can run it all for free.

**This isn’t a teaser. This is real software, running real GenAI workloads, built to move at real-world speed.**

##### **Our goal is simple: finally, truly, Democratize AI Compute.**

We’re not just here to “catch up to CUDA.” CUDA launched the AI revolution—but it’s time for the next step. We’re building a better way to program *all* accelerators—even NVIDIA’s.

Because while NVIDIA makes incredible hardware, it faces the same challenges as everyone else: fragmentation, usability, and the fast moving nature of AI. That’s the problem we’ve signed up to solve—with something *portable*, *programmable*, and *powerful* enough to serve the entire AI community.

Let’s end the gatekeeping. Let’s stop pretending GPU programming is just for compiler wizards or billion-dollar chip companies. It’s time to open up the frontier—to make AI compute usable and accessible for everyone. Just like Swift opened up iOS development, this is about unlocking the next wave of developer innovation.

> “The best way to predict the future is to invent it.” -Alan Kay

Next time, we’ll dig into how it all comes together—starting with a run-through of Modular's product line-up.

Until then—stay above the waves, keep your compass steady, and chart your own path. ✈️🌊

- Chris

## Read more from Modular

View all blogs

Matrix Multiplication on Blackwell: Part 4 - Breaking SOTA

September 19, 2025

Matrix Multiplication on Blackwell: Part 3 - The Optimizations Behind 85% of SOTA Performance

September 12, 2025

Matrix Multiplication on Blackwell: Part 2 - Using Hardware Features to Optimize Matmul

September 5, 2025

Build the future of AI with Modular

Get started - FREE

View Editions

- ![Person with blonde hair using a laptop with an Apple logo.](https://cdn.prod.website-files.com/68c9c3107effc2ea46e1a81f/68cc733ff9050921bab7782c_emoji-dev.png)Sign up todaySignup to our Cloud Platform today to get started easily.[Sign Up](https://docs.modular.com/max/get-started)
- ![Magnifying glass emoji with black handle and round clear lens.](https://cdn.prod.website-files.com/68c9c3107effc2ea46e1a81f/68cc733fb111718bbd49ca31_emoji-zoom.png)Browse open modelsBrowse our model catalog, or deploy your own custom model[Browse models](https://www.modular.com/models)

## Sign up for our newsletter

Get all our latest news, announcements and updates delivered directly to your inbox. Unsubscribe at anytime.

Thanks for signing up to our newsletter! 🚀

Thank you,

Modular Sales Team

Oops! Something went wrong while submitting the form.
