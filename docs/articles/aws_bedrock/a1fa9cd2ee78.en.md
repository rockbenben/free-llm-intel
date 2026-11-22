---
vendor: aws_bedrock
title: Built from the inside out: How AWS Professional Services became a frontier team first
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/built-from-the-inside-out-how-aws-professional-services-became-a-frontier-team-first
date: 2026-06-12
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 47abefaae7f1
---

# Built from the inside out: How AWS Professional Services became a frontier team first

[AWS Professional Services](https://aws.amazon.com/professional-services/) (AWS ProServe) compressed engagement timelines from months to days, not by adding artificial intelligence (AI) tools to an existing process, but by fundamentally rebuilding how we deliver from the inside out. The shift mirrors what my colleague Swami Sivasubramanian outlined in [How Frontier Teams Are Reinventing AI-Native Development](https://aws.amazon.com/blogs/machine-learning/how-frontier-teams-are-reinventing-ai-native-development/): real productivity gains come from reimagining how software gets built, not from layering AI onto existing workflows.

In this post, I’ll share how AWS ProServe became a frontier team, the practices that enabled it, and what your engineering organization can take from our experience.

## A partner who’s already done it

Building a frontier team is something every organization can do. For customers who want help accelerating, AWS ProServe is a partner whose consultants have already absorbed AI-native development into how they work every day.

AI-native development moves at a pace traditional consulting cadences weren’t built for. Work that used to span months compresses into days, and the rhythm changes accordingly: tighter loops, faster feedback, more decisions made in the flow of building. Helping a customer operate at that pace requires consultants who know which decisions can move quickly, which need careful human judgment, and how to keep quality high when execution speeds up. That intuition emerges from doing the work.

Our driver mirrored what Swami described: free consultants from non-coding overhead (documentation, coordination, status reporting, repetitive scaffolding) that consumed most of every engagement. This let human judgment focus where it actually moves outcomes. So we did what frontier teams do. We invested in agent context, restructured work around what agents do well, and stopped treating AI as an assistant. We started treating it as a foundation.

## Our pathfinder team: APEX

Swami’s blog describes three paths Amazon teams took into AI-native development: a pathfinder initiative, a structured sprint, and an in-situ experiment. AWS ProServe began as a pathfinder.

Our Agentic AI ProServe Experiences team (APEX) had a single mandate: redesign how ProServe delivers. [APEX built the ProServe Delivery Agent](https://aws.amazon.com/blogs/machine-learning/accelerate-enterprise-solutions-with-agentic-ai-powered-consulting-introducing-aws-professional-service-agents/), a multi-agent system spanning requirements, architecture validation, implementation, security review, testing, and deployment. A supervisor agent orchestrates specialized sub-agents across each lifecycle phase.

The Delivery Agent is how ProServe implements **AI-DLC**, the **AI-Driven Development Lifecycle**. AI-DLC was built by AWS field teams, developed and refined through hundreds of hands-on customer workshops. AI-native development is the foundation. AI-DLC is the AWS-built process for running it across a complete delivery lifecycle, for ourselves and our customers.

APEX proved the model on its own production workloads. The Delivery Agent now works alongside human consultants on engagements globally, and the patterns APEX validated are becoming the default delivery motion across ProServe. This is not a pilot. It’s how we deliver at scale.

## How we redesigned the delivery motion

A typical ProServe engagement used to follow a familiar consulting rhythm: discovery in long documents, architectural decisions debated in workshops, implementation on sprint cadences, testing and security at phase boundaries. Each handoff introduced lag, and each artifact was written for human consumption only.

The redesign changed every step. Requirements moved from prose to structured specs that humans and agents can both read, becoming the source of truth rather than a byproduct. Architectural standards and lessons from past engagements were codified into steering files the agents draw on continuously. Implementation shifted from contributors working serially on tickets to consultants feeding well-scoped tasks to multiple agents in parallel. Testing and security review moved into the build loop, with agents validating output locally and self-correcting before any human review begins. Status reporting and coordination overhead largely disappeared.

The net effect: continuous flow, with human judgment concentrated on prioritization, validation, and high-stakes decisions.

[![Diagram of the redesigned ProServe delivery motion: a continuous flow from requirements through deployment where agents handle scaffolding and humans concentrate on prioritization, validation, and high-stakes decisions](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/06/11/ML-21052-1.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/06/11/ML-21052-1.png)

## Building the Delivery Agent by using the Delivery Agent

APEX builds the Delivery Agent using the same AI-native practices it provides to customers. A feature request enters the system. Agents generate structured tickets, produce code, and run automated testing through our GitLab-integrated DevOps pipeline. On human review and approval, the change deploys.

Humans handle judgment: prioritizing, validating quality, approving high-stakes decisions. Agents handle scaffolding. Low-stakes decisions run autonomously. Human gates concentrate where judgment matters.

As delivery teams across ProServe adopt the Delivery Agent on engagements, they feed learnings back, making it sharper with every project. That’s how Amazon builds. We run our own products, see what breaks, and fix it.

## Five practices that make this work

The five practices from Swami’s blog now define how we run AI-DLC inside ProServe:

**Slow down to speed up.** Frontier teams invest before they accelerate, building agent context and standardizing the practice before velocity compounds. APEX made that investment once, so we transfer the muscle memory directly rather than asking each customer to start from scratch.

**Invest heavily in agent context.** Steering files and architectural standards are first-order artifacts in every engagement. The richer the context, the more autonomy an agent can safely exercise.

**Feed agents instead of babysitting them.** Builders maintain a steady backlog of well-scoped tasks and run multiple agents in parallel, reviewing output asynchronously.

**Use specs as the source of truth.** Spec-driven development is the default workflow. Specs aren’t documentation. They’re the contract agents build against.

**Shift testing left.** Agents validate locally and self-correct before output reaches a human reviewer.

## AI-native delivery in customer environments

On customer engagements, the Delivery Agent operates alongside human consultants. Together they work through the full lifecycle, from planning to deployment, against business outcomes the customer has selected. The governing principle: humans provide intent, AI creates, humans verify.

Customers retain choice of foundation models and can extend the system with their own data and tools.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/06/22/AI-DLC_Architecture-blog.jpg)

## What we learned by going first

Calibration isn’t optional, but you don’t need to start from zero. Teams need time to build trust in what agents handle well, decompose complex work into verifiable tasks, and restructure artifacts for AI consumption. We transfer that muscle memory directly during the engagement, shortening the curve.

The workflow is the constant. Tools are enablers. We use Kiro, Amazon Bedrock AgentCore, and Strands, but the stack isn’t what creates the productivity gain. Tools compound only when the workflow is redesigned around them.

Align to outcomes. Traditional consulting charges for time and materials, incentivizing duration over impact. We moved to fixed-price engagements tied to production-deployed business outcomes. When the commercial model aligns with customer needs, everything else follows.

## Real outcomes

*“We adopted Amazon Application Recovery Controller’s (ARC) new Region Switch functionality to streamline our multi-region resiliency approach. Region Switch replaced custom failover orchestration with declarative plans that coordinated scaling, database switchover, and DNS routing across our services in parallel. Kiro with AWS Professional Services Delivery Agent compressed weeks of backlog creation into hours, accelerated code delivery by 60%, and enforced consistent quality across every deliverable. Our region switch test executed on schedule and we were able to run in our secondary region. This gives us even more confidence in the speed and reliability this approach delivers for our customers.” Matt McKeever, CTO Infrastructure & Operations, LexisNexis Legal & Professional.*

## Getting started

**Hands-on workshops**: AWS Solutions Architects run AI-DLC workshops, two-to-five-day engagements demonstrating AI-native development against your own stack. Hundreds of customers have already participated.

**Production engagements**: When you’re ready to take business use cases to production, AWS ProServe enters the journey. Our consultants and the Delivery Agent embed with your team to deliver production outcomes while building organizational capability to sustain and scale the practice. By the end, you have working systems in production and trained internal champions ready to carry it forward.

*“Our Solutions Architects have been on the front lines of this transformation, working hands-on with customers in AI-DLC workshops to reimagine how they build software. Once teams experience AI-native development firsthand, they don’t want to go back. AWS Professional Services takes that momentum and operationalizes it, at scale.” Shaown Nandi, Vice President, Technology, AWS.*

Many organizations have outcomes waiting to be realized and engineering teams ready to work differently. The path isn’t more experimentation. It’s committed execution with a team that has already proven the approach on its own production workloads.

Contact your AWS account team or visit the [AWS Professional Services webpage](https://aws.amazon.com/professional-services/) to start delivering production outcomes faster.

## About the author
