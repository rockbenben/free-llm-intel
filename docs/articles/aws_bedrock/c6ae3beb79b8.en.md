---
vendor: aws_bedrock
title: Improving HCLS AI reasoning with open-source agent skills
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/improving-hcls-ai-reasoning-with-open-source-agent-skills
date: 2026-09-16
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 1c5d6bdeef9e
---

# Improving HCLS AI reasoning with open-source agent skills

AI agents built on foundation models (FMs) often misapply healthcare and life sciences (HCLS) decision frameworks, even when they’ve seen the guidelines in training and in the system prompt. Ask an agent to classify a TP53 missense variant using ACMG/AMP criteria. It will cite the correct framework but misapply evidence categories, skip population frequency thresholds, or hallucinate computational predictor scores. The model knows facts but lacks the structured reasoning procedures that domain practitioners internalize over years of training. The gap produces silent failures across variant interpretation, claims adjudication, clinical trial design, and imaging analysis. Outputs look correct but apply wrong criteria, with regulatory and patient safety consequences.

In this post, we share a collection of 38 open source agent skills spanning 11 HCLS domains that help close this methodology gap. We walk through installation and show how to use them across agentic AI services. We share our evaluation results to demonstrate measurable improvement across drug discovery, healthcare operations, and medical imaging workflows. Agents equipped with these skills win 70–86 percent of head-to-head comparisons against the same agents without skills, varying agent harness setup. The strongest effect is on critical thinking (78–85 percent win rate, d = 0.65–1.03). We also show you how you can customize, extend, and create your own agent skills for your specific use case.

## Solution overview

Agent skills in the HCLS Agent Skills collection are structured markdown documents (`SKILL.md`) that encode domain decision procedures into a format AI agents can consume at inference time through progressive disclosure. Following the [Agent Skills open standard](https://agentskills.io), each skill declares triggers, dependencies, and metadata in YAML frontmatter. The content that follows contains decision frameworks, parameter tables, code patterns, and validation criteria. The collection covers 38 skills across 11 HCLS domains including genomics, drug discovery, claims operations, and medical imaging. Refer to the [full skill catalog](https://github.com/awslabs/hcls-agent-skills#skill-catalog) for the complete list organized by domain. All are released under the MIT-0 license.

Skills in this repository are sorted as either reasoning or pipeline skills. Reasoning skills encode methodology and decision frameworks that guide how the agent thinks. For example, the [genomic-variant-interpretation](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/skills/genomic-variant-interpretation/SKILL.md) skill encodes the full ACMG/AMP classification framework such as evidence categories, population frequency thresholds, and computational predictor cutoffs. Pipeline skills encode tool-specific commands, validated parameters, and code templates that produce runnable artifacts. The [variant-calling](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/skills/variant-calling/SKILL.md) skill provides GATK4 HaplotypeCaller commands with correct annotation groups, VQSR tranche sensitivity targets, and Mutect2 tumor-normal configurations.

This dual taxonomy gives agents both the judgment to make correct decisions and the technical precision to execute them. Unlike Retrieval Augmented Generation (RAG), which retrieves limited passages from indexed documents to augment the response generation, skills encode the decision procedure and error conditions itself. Skills are not fine-tuning either. They’re structured prompts that activate contextually based on trigger patterns in the user’s query.

Three properties make skills distinct from other approaches to domain specialization. Skills are auditable, portable, and straightforward to maintain. Every decision criterion is human-readable in markdown format, not hidden in model weights. A skill works across over 20 services ([Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/), [AWS Strands Agents SDK](https://strandsagents.com/), [Kiro](https://kiro.dev/), [AWS Quick Desktop](https://aws.amazon.com/quick/desktop/), Claude Code, OpenAI Codex and more) without customization to each. Annual medical policy changes or new experiment criteria can be reflected quickly by editing a text file, not retraining a model.

Now that you understand what skills contain, let’s set them up.

## Prerequisites

To follow along with the examples in this post, you need one of the supported services from AWS: [Kiro](https://kiro.dev/ide/) or [Kiro CLI](https://kiro.dev/cli/) for interactive skill use and multi-agent orchestration, the [AWS Strands Agents SDK](https://strandsagents.com/) with [Amazon Bedrock](https://aws.amazon.com/bedrock/) foundation model access, [AgentCore harness](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness.html), a capability of Amazon Bedrock AgentCore, with an existing agent implementation, or [Quick Desktop](https://aws.amazon.com/quick/desktop/) for GUI-based skill management. You can also use a coding agent harness of your choice such as Claude Code or OpenAI Codex. You also need Python 3.10+ with uv, and Git for cloning the repository.

Start by cloning the repository:

```
git clone https://github.com/awslabs/hcls-agent-skills.git
cd hcls-agent-skills
```

To install skills only without the agent configuration, use the universal [skills CLI](https://github.com/vercel-labs/skills):

```
npx skills add awslabs/hcls-agent-skills
```

For Kiro, the `install.sh` script installs both skills and a pre-configured agent that equips them. The agent handles skill routing automatically, so you don’t need to invoke individual skills by name. Run `./install.sh --target kiro`, then switch to the agent in Kiro CLI with `/agent hcls`. For multi-agent mode, run `./install.sh --target kiro --mode multiagent` and use `/agent hcls-multiagent`.

For the AWS Strands Agents SDK, load skills directly in your Python code:

```
from strands import Agent
from strands.skills import AgentSkills

agent = Agent(
    model=model_id,
    skills=AgentSkills(skills="./skills/"),
)
```

For [AgentCore](https://aws.amazon.com/bedrock/agentcore/), follow [Skills](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-skills.html) to add agent skills to an AgentCore-hosted agent. AgentCore provides managed hosting, auto scaling, security boundaries, and observability capabilities.

For AWS Quick Desktop, run `./install.sh --target quick-desktop` to see the full instructions for adding skills in the graphical interface. Alternatively, follow the instructions in [Skills](https://docs.aws.amazon.com/quick/latest/userguide/skills-desktop.html) in the AWS Quick documentation.

## Solution walkthrough

With skills installed, we demonstrate three deployment patterns: the simplest single-agent approach in Quick Desktop, multi-agent orchestration in Kiro CLI that addresses context engineering challenges, and production deployment with Strands SDK on Amazon Bedrock AgentCore. We then show three sample use cases that highlight the measurable difference skills make in real HCLS workflows.

### Agent skills in action with Quick Desktop

With skills installed, Quick Desktop’s agent gains structured HCLS domain reasoning without additional configuration. When you ask a domain question, the agent automatically activates relevant skills based on trigger patterns in your query. For example, asking “What is the RAF impact of coding E11.9 instead of E11.42?” triggers the `risk-adjustment` skill and the agent responds with specific HCC mappings, hierarchy resolution, and quantified RAF deltas rather than a generic suggestion to “review documentation.” Skills are activated selectively. Only the relevant skill is triggered for the response, helping keep output focused and accurate. The following video shows a skill dynamically loaded for the question in AWS Quick Desktop.

AWS Quick Desktop chat with the risk-adjustment skill dynamically loaded to respond to a RAF coding question

### Multi-agent architecture with Kiro

Loading all 38 skills into a single agent context consumes ~80K tokens. This is workable with large-context models, but it creates a context engineering challenge. The agent must select the right subset from 38 available skills on every query and irrelevant skill content competes for attention. An alternative is explicit skill invocation (for example, `/risk-adjustment`), but this requires you to know which skill to invoke before asking your question, which is exactly the expertise gap skills are meant to bridge.

Kiro CLI’s multi-agent architecture solves both problems. A lightweight coordinator agent (no skills loaded) routes queries to eight domain specialists, each loading only its relevant skills (approximately 15K tokens per specialist). The coordinator handles intent classification while the specialists handle domain reasoning. The specialization can be defined as described in the following table.

![Table of the eight domain specialist agents in the Kiro CLI multi-agent architecture and the skills assigned to each](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/09/11/ML-21213-2.png)

Table of the eight domain specialist agents in the Kiro CLI multi-agent architecture and the skills assigned to each

The multi-agent configuration is defined in JSON agent files. Refer to the [coordinator agent config](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/agents/multiagent/kiro/hcls-multiagent.json) for the routing logic, and a [specialist agent config](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/agents/multiagent/kiro/hcls-drug-discovery.json) for an example of how domain skills are attached to a specialist. The following video shows multiagent and dynamic skill activation answering a complex drug repurposing question while working in a code base in Kiro CLI.

Kiro CLI answering a drug repurposing question in a code base using multi-agent routing and dynamic skill activation

### Strands SDK integration

The AWS Strands Agents SDK provides native skill loading for building custom HCLS agents:

```
from strands import Agent
from strands.skills import AgentSkills
from strands.multiagent import MultiAgentOrchestrator

# Define domain specialists with their skill sets
genomics_agent = Agent(
    name="hcls-genomics",
    model=model_id,
    skills=AgentSkills(skills="./skills/genomics/"),
)

imaging_agent = Agent(
    name="hcls-imaging",
    model=model_id,
    skills=AgentSkills(skills="./skills/imaging/"),
)

# Coordinator routes to specialists
coordinator = MultiAgentOrchestrator(
    agents=[genomics_agent, imaging_agent, ...],
    model=model_id,
)

response = coordinator("Classify NM_000546.6:c.743G>A in TP53 using ACMG criteria")
```

### Deploying to Amazon Bedrock AgentCore

After your skill-equipped agent works locally, you can move it to production. Amazon Bedrock AgentCore provides an alternative path to inject skills into hosted agents. In addition to embedding them in the Strands agent code, you can configure skills at the environment level so they’re available to agents running in that harness. AgentCore harness provides managed hosting, auto scaling, security boundaries, and observability capabilities without managing infrastructure. Follow [Skills](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-skills.html) in the AgentCore documentation.

With deployment covered, let’s look at what skill-equipped agents produce in practice. The following sample use cases are drawn from our evaluation prompt set.

### Use case 1: Evaluating repurposing candidates for rare fibrotic disease in drug discovery

A team at a biotech company investigating drug repurposing for idiopathic pulmonary fibrosis (IPF) wants to evaluate approved drugs that modulate TGF-β1 signaling through the receptor kinase TGFBR1 (ALK5). In practice, a researcher needs to query drug-gene interaction databases, rank candidates by evidence strength, assess mechanism-of-action overlap with IPF pathophysiology, and determine translatability given existing safety data. However, a researcher might be quick to prompt an agent vaguely: “I’m investigating TGFBR1 as a therapeutic target for IPF. Are there any approved drugs worth repurposing? What’s the strongest candidate and how realistic is clinical translation?”

Before adding skills, the agent provides a general literature review listing known TGFBR1 inhibitors without structured ranking criteria, evidence hierarchy, or translatability assessment framework. After equipping the agent with skills, the agent triggers [drug-repurposing](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/skills/drug-repurposing/SKILL.md), and [translational-research](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/skills/translational-research/SKILL.md) skill and does the following:

- The agent applies the DGIdb query framework, prioritizing interaction types (inhibitor > modulator > binder) and source databases (ChEMBL, DrugBank) over lower-confidence sources.
- It ranks candidates using a structured evidence hierarchy where direct target engagement outweighs pathway-level evidence, which in turn outweighs phenotypic association, with existing indication relevance applied as a modifier.
- It assesses mechanism-of-action overlap by mapping TGFBR1 inhibition to the key IPF pathological processes: fibroblast-to-myofibroblast transition, epithelial-mesenchymal transition, and extracellular matrix deposition.
- It evaluates clinical translatability using T0→T1 criteria, examining existing safety data from the original indication, therapeutic window compatibility, and concordance between available preclinical fibrosis models and human disease.

The skill chain transforms a surface-level response into a structured regulatory-aware evaluation with quantified evidence rankings.

### Use case 2: Building a CMS-HCC risk adjustment pipeline in healthcare claims operations

A Medicare Advantage plan with 12,000 members needs to calculate Risk Adjustment Factor (RAF) scores from ICD-10 diagnosis claims data using CMS-HCC Model V28 coefficients. The pipeline must apply the `ICD-10-to-HCC` crosswalk, resolve disease hierarchies correctly, and compute final member-level risk scores with demographic adjustments. However, a junior analyst may prompt the agent: “We’re a Medicare Advantage plan with 12,000 members. We have ICD-10 diagnosis claims in a PostgreSQL database (member_diagnoses and member_demographics tables). Build me a pipeline to calculate member-level RAF scores for the current payment year.”

Before adding skills, the agent produces a plausible but incomplete pipeline, often missing hierarchy resolution entirely, using outdated V24 coefficients, or applying hierarchies after summing (which inflates scores). After equipping the agent with skills, the agent triggers [risk-adjustment](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/skills/risk-adjustment/SKILL.md), and [claims-billing-rules](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/skills/claims-billing-rules/SKILL.md) skill and does the following:

- The agent generates correct SQL that joins diagnosis codes to the `ICD-10-to-HCC` crosswalk table with deduplication within the measurement year, making sure each HCC is counted only once per member.
- It implements V28 hierarchy resolution correctly, where HCC 18 (Diabetes with Chronic Complications) supersedes HCC 19 (Diabetes without Complications) and HCC 326 (CKD Stage 5) supersedes HCC 327 (CKD Stage 4), helping prevent double-counting at multiple specificity levels.
- It applies the correct demographic segmentation by categorizing members into community, institutional, or dual-eligible populations with age/sex adjustments before summing HCC coefficients.
- It proactively explains that skipping hierarchy resolution double-counts conditions at multiple specificity levels, systematically inflating RAF scores and creating audit liability under CMS RADV review.

The skill supports producing audit-defensible RAF scores rather than inflated estimates that would trigger CMS RADV audit findings.

### Use case 3: T1-weighted MRI preprocessing for voxel-based morphometry in medical imaging research

A neuroimaging study with 45 healthy adults needs a standard T1w preprocessing pipeline for voxel-based morphometry (VBM) analysis. Raw DICOM data has been converted to NIfTI. The pipeline must reorient, correct bias field, skull-strip, and register to MNI152 space in the correct order and with parameters appropriate for healthy adult brains in an FSL/ANTs hybrid environment. A researcher may prompt the agent: “I have 45 healthy adult T1w scans that need preprocessing for a VBM analysis. Build a pipeline using FSL and ANTs.”

Before adding skills, the agent suggests a reasonable pipeline but may order bias correction after skull stripping (which biases brain masks), use inappropriate thresholds, or omit failure mode detection strategies. After equipping the agent with skills, the agent triggers [radiology-preprocessing](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/skills/radiology-preprocessing/SKILL.md), and [imaging-study-design](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/skills/imaging-study-design/SKILL.md) skill and does the following:

- The agent specifies the correct processing order with justification: reorient to standard space, then bias field correction before skull stripping, then brain extraction with parameters tuned for healthy adults, and finally registration to the MNI152 template.
- It explains the critical ordering dependency. Intensity inhomogeneity at brain borders causes the skull-stripping algorithm to remove too much or too little tissue if bias correction hasn’t been applied first, particularly in temporal and frontal regions.
- It provides a complete bash script with error checking at each stage and quality control outputs for visual inspection of intermediate results.
- It documents failure modes at each step: incorrect orientation metadata, residual signal shading near surface coils, neck tissue inclusion when extraction thresholds are too permissive, and registration failure at ventricular boundaries in older subjects.

The skill catches the ordering dependency that would introduce systematic bias into the VBM analysis.

These use cases illustrate how HCLS skills reshape agent behavior qualitatively to produce more domain-aligned responses, but there’s always a question of how much better it is for researchers and developers.

### Evaluation results

We conducted a pairwise evaluation to measure skill impact across 410 domain prompts (380 single-skill and 30 cross-skill) using two harness configurations. One of the two agent harnesses is Kiro CLI in which the Auto model is used to allow Kiro to select an optimal model for the task. The agent in Kiro has access to a thinking tool and file-read operations. The other agent configuration is an agent built with the AWS Strands Agents SDK using `Agent(model=BedrockModel(...), callback_handler=None)` with the model explicitly pinned to Claude Sonnet 4.6. The skills condition additionally loads an `AgentSkills(skills="./skills/")` plugin. A think tool is provided to both conditions symmetrically. The configuration can be found in [eval/execute.py](https://github.com/awslabs/hcls-agent-skills/blob/bb26f0b2d767ce21bd711d069fc762bf2c212c4b/eval/execute.py#L103). In both configurations, two conditions are compared. One is the baseline agent who does not have access to any skill. The other one is the skilled agent who is invoked with all 38 skills available through progressive loading.

We employ five scoring dimensions for the large language model (LLM) judge to measure how skills impact the agent’s response. Scientific accuracy evaluates the correctness of facts, mechanisms, citations, and domain knowledge. Coherence assesses whether the response follows a logical structure with a clear reasoning chain and internal consistency. Relevance measures how well the agent addresses all parts of the prompt at appropriate depth while staying on topic. Critical thinking captures the agent’s ability to challenge assumptions, identify limitations, and consider alternatives rather than presenting a single uncritiqued response. Actionability scores the agent’s ability to provide concrete next steps, specific parameters, and runnable commands that a practitioner could act on immediately. We use Claude Opus 4.7 from Amazon Bedrock as the judge. The full scoring prompt is in [eval/judge.py](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/eval/judge.py).

The judge scores each dimension with 0–100 scale. However, LLM judges exhibit score compression, a phenomenon where the scores cluster in a certain range, making raw deltas (for example, +1.5) difficult to interpret. We therefore report two primary metrics. Firstly, win rate (WR), a percentage of prompts where the skills condition scored higher than the baseline, is reported. This is an intuitive measure and robust to scale compression. Secondly, Cohen’s d effect size (d in short) is reported. This is to measure the standardized difference between two group means. It’s computed with mean delta divided by the pooled standard deviation. This measures how large the improvement is relative to natural variance. General interpretation of Cohen’s d is 0.2 (small), 0.5 (medium), and 0.8 (large).

Overall, skills win 69.5–85.9 percent of head-to-head comparisons in the two agent harness configurations. Skills improve critical thinking, actionability, and scientific accuracy in both configurations. The strongest signal is on critical thinking, confirming that skills’ primary contribution is methodological: teaching the agent which frameworks to apply, which assumptions to challenge, and which limitations to flag, rather than adding factual content the base model may already possess. The following table summarizes the high-level results.

| **Metric** | **Kiro CLI** | **Strands Agent** |
| --- | --- | --- |
| Prompts evaluated | 410 | 410 |
| Skills overall WR (d) | 69.5% (0.39) | 85.9% (0.97) |
| Critical thinking WR (d) | 78.0% (0.65) | 85.1% (1.03) |
| Scientific accuracy WR (d) | 69.3% (0.34) | 86.2% (0.85) |
| Actionability WR (d) | 68.0% (0.37) | 77.3% (0.56) |
| Baseline-benefit correlation (r) | -0.59 | -0.61 |
| Max variance reduction | -61.9% | -52.1% |

#### Effect by baseline strength

There is strong evidence showing agent skills help the most when the base agent struggles the most. The Pearson correlation between baseline response quality and skill benefit is −0.59 in Kiro CLI and −0.61 in Strands agent. We categorize the prompts based on the baseline agent’s overall scores into three tiers, weak, medium, and strong. Most prompts fall in the medium tier where skills provide clear benefit. Prompts that fall in the strong tier where the model already performs well get marginal improvement from agent skills. The weak tier represents cases where the base agent struggles. These span multiple domains (clinical data, healthcare operations, genomics) and typically involve multi-step regulatory procedures or niche methodology the model approximates rather than applies precisely.

However, the strong tier finding is not absolute. Cross-domain reasoning skills achieve 80 percent win rate even at a strong baseline of 90.2, demonstrating that well-designed methodology frameworks add value across the quality spectrum when they teach a decision procedure the model wouldn’t apply on its own.

The overall scores for baseline and skilled agents by baseline strength are shown in the following tables.

In Kiro CLI

| **Baseline Tier** | **N** | **Baseline (mean±sd)** | **Skills (mean±sd)** | **Delta** | **Win Rate** |
| --- | --- | --- | --- | --- | --- |
| Weak (<80) | 15 | 75.8±4.0 | 84.4±6.3 | +8.7 | **87%** |
| Medium (80-90) | 227 | 86.8±2.5 | 89.1±3.3 | +2.3 | 79% |
| Strong (>90) | 168 | 91.3±1.0 | 91.0±2.5 | -0.3 | 55% |

In Strands agent

| **Baseline Tier** | **N** | **Baseline (mean±sd)** | **Skills (mean±sd)** | **Delta** | **Win Rate** |
| --- | --- | --- | --- | --- | --- |
| Weak (<80) | 46 | 77.0±2.6 | 84.9±3.5 | +7.9 | **96%** |
| Medium (80-90) | 325 | 85.8±2.6 | 89.5±3.3 | +3.7 | 89% |
| Strong (>90) | 39 | 91.0±0.7 | 91.1±2.0 | +0.0 | 54% |

#### Variance reduction

Skills also reduce the standard deviation of response scores across all sample prompts within a domain. For example, standard deviation of judge’s scores on clinical-data responses drops from 6.8 to 3.3 with skills loaded in the Kiro CLI, a 51 percent reduction. This means skills make outputs more consistent, adhering to the knowledge and framework encoded in the skill. In regulated HCLS workflows where consistency matters as much as average quality, this variance reduction is a meaningful benefit.

The full evaluation methodology, prompts, and raw results are available in the [evaluation technical report](https://github.com/awslabs/hcls-agent-skills/blob/main/eval/TECHNICAL_REPORT.md).

### Extending skills and building new ones

These results are for the 38 skills shipped in the repository. Your team’s workflows may need different thresholds, additional protocols, or entirely new domain coverage. The repository includes three guides for skill customization:

- [CUSTOMIZING.md](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/CUSTOMIZING.md) covers practical workflows for modifying, extending, and creating skills from scratch, including adding organization-specific rules (LCD codes, formulary step therapy, internal protocols) to existing skills.
- [SKILL_DESIGN_GUIDE.md](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/SKILL_DESIGN_GUIDE.md) documents evidence-based patterns for writing effective skills: decision trees, threshold tables, gotcha lists, response format sections, and the structural features that correlate with high evaluation win rates.
- [QUALITY_CHECKLIST.md](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/QUALITY_CHECKLIST.md) provides a pre-merge quality checklist covering frontmatter, structure, content quality, and testing requirements.

To customize a skill for your organization, start by copying the relevant `SKILL.md` and modifying decision thresholds, adding org-specific protocols, or removing irrelevant sections. Use the design guide to structure new content for optimal outcomes. For example, reasoning skills benefit from decision trees and numbered procedures while pipeline skills provide strong value with parameter tables and version-specific gotchas.

To test your changes, first generate evaluation prompts that reflect your team’s actual workflows, then run the evaluation framework:

```
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -e ".[dev]"
# Generate 30 evaluation prompts for each of the skills
python eval/generate_prompts.py --count 30
# Run pairwise evaluation against your modified skills
python -m eval.run --skills ./my-custom-skills/ --parallel 2
python eval/build_review.py
open eval/results/review.html
```

The following video shows the review.html evaluation dashboard, which includes scoring, domain breakdown, prompts, and responses for each evaluation.

The review.html evaluation dashboard showing scores, domain breakdown, prompts, and responses for each evaluation

The evaluation produces a pairwise comparison showing whether your modified skill improves responses relative to the baseline, with per-dimension breakdowns identical to the results reported earlier. Contribute new domain skills back to the open-source collection following the [contribution guide](https://github.com/aws-samples/sample-hcls-agent-skills/blob/main/CONTRIBUTING.md).

## Clean up

Skills are local files and do not create AWS resources. No teardown is required for the examples in this post. If you deployed a Strands agent to Amazon Bedrock AgentCore harness, follow the [Clean up step](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-cli.html#agentcore-cli-cleanup) to delete the deployed agent resources.

## Conclusion

Agent skills give your HCLS agents structured domain methodology. The decision frameworks, regulatory thresholds, and common-mistake checklists in an agent skill can turn approximate answers into precise ones. With 38 skills covering genomics, drug discovery, claims operations, medical imaging, and more, you can deploy domain-expert agents on Quick Desktop, Kiro, or Strands SDK-based architecture running on Amazon Bedrock AgentCore.

The measurable impact speaks for itself. Our evaluation demonstrated a 70–86 percent win rate for the skilled agent, with the strongest gains on critical thinking (d = 0.65) and the highest lift on the hardest queries where unguided agents fail most. Skills are auditable text files you can customize for your organization’s protocols and test with the included evaluation framework.

To get started:

- Clone the [repository](https://github.com/awslabs/hcls-agent-skills)
- Use skills interactively with [Kiro](https://kiro.dev/docs/#get-started) or [AWS Quick Desktop](https://docs.aws.amazon.com/quick/latest/userguide/amazon-quick-desktop.html)
- Build custom agents with [AWS Strands Agents SDK](https://strandsagents.com/docs/user-guide/quickstart/overview/)
- Deploy agents to production with [Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-get-started-cli.html)
- Explore foundation models on [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html)

## About the author
