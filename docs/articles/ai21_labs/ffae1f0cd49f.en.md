---
vendor: ai21_labs
title: Modular intelligence: a human-like model for agent orchestration
original_title: Modular intelligence: a human-like model for agent orchestration
url: https://www.ai21.com/blog/modular-intelligence-agent-orchestration
date: 2026-02-26
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 9580c762fdc5
---

TL;DR

Human language production can be instructive for building agent architectures that are similarly modular, with discrete stages for reasoning, planning, and execution and strategies that mirror external self-monitoring. Not only does this cognitive analogy more aptly reflect the increasing complexity of today’s agent flows, the modularity model produces AI systems that are more auditable, more diagnosable, and more amenable to principled improvement.

## Introduction

As AI systems have grown more capable, the tasks assigned to them have grown correspondingly more complex. Contemporary agentic systems are not to follow a single task, but to plan, retrieve, and reason across multiple sources, take actions in external environments, and produce outputs that are contingent on sequences of intermediate decisions. In these settings, end-to-end evaluation is too opaque. Evaluation of the end result, whether automatic or with human experts in the loop, is too limited. A fluent and superficially correct final output can mask failures at intermediate stages: retrieval of an outdated document, incorrect routing of a request, or synthesis that is plausible but unsupported by the evidence actually retrieved. Evaluating only the final output leaves these failures invisible.

This challenge invites a different framing. Rather than asking only whether the system produced a correct answer, we might ask ***how*** the system produced its answer, and whether each step in that process can be assessed on its own terms. Well, this is precisely the kind of question that researchers in psycholinguistics have been asking about human language production for decades.

## Human language production as a modular reference model

The seminal work of Levelt (1989) established theoretical foundations for understanding the cognitive architecture underlying human language production. Levelt’s model describes the process from abstract communicative intention to realized speech or writing as a sequence of distinct, functionally separable stages.

During **conceptualization**, a speaker identifies what they intend to communicate, drawing on context and prior knowledge to construct a pre-verbal conceptual message. The **formulation** stage translates this abstract message into a structured linguistic plan: lexical items are selected and mapped into grammatical structures, and an internal phonological (auditory) or orthographic (visual) representation is prepared. Finally, **articulation** converts this linguistic blueprint into motor commands, realized as speech or written output.

What makes Levelt’s model particularly relevant in the current context is not just its sequential structure, but its modularity. Each stage has a defined input and output, a specific computational role, and can in principle be studied and evaluated independently of the others.

## Agentic architectures and the move toward modularity

The broader shift in AI toward agentic architectures reflects a growing recognition that end-to-end generation from a single model call is insufficient for complex knowledge flows. Even relatively simple agent designs, such as ReAct-style loops, introduce multi-step structure: the system reasons about a situation, selects an action, observes the result, and iterates. This is already meaningfully closer to the staged processing described by Levelt than a single-pass language model call.

Other, orchestrator-based designs, introduce higher modularity. For example, in our AI21 Maestro framework, this is an explicit design principle, separating the core functions of reasoning, planning, and execution into distinct components. The reasoning component determines what the system should do in response to a given request, analogous to Levelt’s conceptualization stage. The orchestration component translates that intent into a structured, programmatic execution plan, analogous to Levelt’s formulation stage.

[**Learn more about how AI21 Maestro leverages test-time compute scaling and structured planning to improve accuracy and efficiency on long-horizon agent tasks**](https://www.ai21.com/blog/test-time-compute-swe-bench/).

This separation addresses a failure mode common in less structured agentic systems: *context drift*, where a system that must reason, plan, and act within a single undifferentiated process may lose track of the original intent as the context window grows and intermediate results accumulate. By preserving the communicative intention as an explicit plan, Maestro’s architecture ensures that the goal set at the reasoning stage remains recoverable and auditable at the execution stage.

The modularity also enables a form of external self-monitoring that parallels Levelt’s human perceptual loop. It suggests that in human language production, speakers monitor their own output using the comprehension system, the same cognitive machinery used to understand others, allowing them to detect and repair errors as they occur. *In Maestro, *rather than relying on the model’s internal assessment of whether an action succeeded, discrete verifiers check the result of each action against objective criteria. This externalizes monitoring, making the detect-and-repair loop less dependent on the model’s self-evaluation and more grounded in observable outcomes.

## Modularity as a prerequisite for meaningful evaluation

The architectural properties described above have direct consequences for human evaluation. When a system’s internal process is opaque, evaluation is necessarily confined to outputs. When the process is made explicit through modular decomposition, evaluation can be distributed: each component can be assessed against criteria appropriate to its specific function, using test data that reflects the distribution that component will encounter in deployment.

Consider an agentic system designed to serve both conversational and investigatory functions within an enterprise setting. Such a system must determine whether an incoming request calls for dialogue or for retrieval and synthesis, then execute accordingly. It might not distinguish between requests as different as *“I’m exhausted today, can you cheer me up?”* and *“Was the policy on bringing pets to the office changed, and if so, what changed?”*, while, in fact, these two requests require entirely different processing paths.

In a modular setup, these responsibilities are made explicit and traceable. A routing component determines the nature of the request. For investigatory queries, a retrieval component fetches relevant documents, and can be evaluated on **grounding**: did it retrieve the actual current and historical HR policies on the relevant topic, rather than semantically close office guidelines? A synthesis component integrates the retrieved evidence into a coherent response, and can be evaluated on **faithfulness and coverage**: does the response accurately reflect what the retrieved documents contain, and does it address all relevant aspects of the query?

This structure makes it possible to identify where a failure occurred. A fluent but unfaithful synthesis response can be traced to the synthesis component, independently of retrieval quality. An incorrect routing decision can be identified and corrected without modifying the retrieval or synthesis components. Each component owns a sub-goal with an explicit quality standard, and can be configured and evaluated independently with respect to model choice, policy constraints, latency requirements, and evaluation metrics.

## Compositional accountability and the limits of global objectives

Global objectives such as “be helpful” or “produce accurate responses” are too abstract to enforce or evaluate directly at the system level. They do not specify which component is responsible for which aspect of helpfulness, nor do they provide criteria for determining where a failure occurred. Modular decomposition replaces these global objectives with local ones that are sharp, assignable, and testable: classification accuracy for a routing component, precision and recall against a ground-truth document set for retrieval, entailment and coverage metrics for synthesis.

This compositional accountability has practical implications beyond evaluation. When a failure can be localized to a specific component, remediation can be targeted to that component rather than requiring retraining or rescaling of the entire system. Configurations can be adjusted at the level where the problem exists, and the effects of those adjustments can be measured against the component’s specific evaluation criteria.

## Conclusion

The move toward agentic AI systems creates evaluation problems that end-to-end evaluation was not designed to solve. The response to these problems need not be a search for better global metrics; it can be addressed architecturally, by designing systems whose internal structure is explicit enough to support component-level assessment.

The analogy to human language production is instructive not because human cognition is the only valid model for AI systems, but because it offers a well-studied example of how a complex, multi-stage process can be made robust and self-correcting through modular organization. Levelt’s framework illustrates that separating concerns, preserving intent across stages, and externalizing monitoring are strategies with a long track record in the most sophisticated language-production system we know of.

Applied to agentic AI, these principles yield systems that are more auditable, more diagnosable, and more amenable to principled improvement. The kind of human-likeness worth pursuing in this context is not surface fluency, but structural transparency: systems whose reasoning can be inspected, whose failures can be localized, and whose outputs can be explained in terms of what the system actually did, rather than merely what it produced.
