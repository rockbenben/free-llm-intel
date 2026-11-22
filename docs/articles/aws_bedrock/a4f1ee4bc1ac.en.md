---
vendor: aws_bedrock
title: How DiDi built intelligent contact center QA with Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/how-didi-built-intelligent-contact-center-qa-with-amazon-bedrock
date: 2026-09-08
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 37e5fe9f87f2
---

# How DiDi built intelligent contact center QA with Amazon Bedrock

DiDi partnered with AWS to build an intelligent contact center quality assurance (QA) system on [Amazon Bedrock](https://aws.amazon.com/bedrock/) for its International Business Group’s Customer Experience (CX) department. The system covers Spanish and Portuguese across three business lines (ride-hailing, food delivery, and financial services) and migrates QA capabilities from an opaque third-party solution to a transparent, self-owned AI architecture. It comprises three core pipelines: intent verification, compliance evaluation, and Voice of Customer (VOC) analysis. In DiDi’s production validation, intent verification accuracy improved from 38 percent to 86 percent, compliance scoring accuracy exceeded 90 percent, and VOC analysis compressed hours of manual summarization into minutes.

In this post, we walk through how DiDi International Business Group and AWS built a self-owned, transparent contact center QA system on Amazon Bedrock, replacing an opaque third-party solution. We describe the three core pipelines that power the system: intent verification, compliance evaluation, and Voice of Customer (VOC) analysis. We also explain the design rationale behind each. Along the way, we show how a single principle, precise context management (controlling exactly what information the model sees in each call), drove the key results, and VOC trend analysis compressing hours of manual work into minutes.

## About DiDi International Business Group

DiDi International Business Group (IBG) is the overseas arm of DiDi Global, operating across 14 countries and regions with three business lines: ride-hailing, food delivery, and financial services, serving tens of millions of users. The CX department processes a large volume of Spanish and Portuguese tickets each month across live chat and phone channels, where service quality directly affects user retention and brand trust.

## Challenges

As the business scaled and QA standards evolved rapidly, the existing third-party QA solution lacked transparency and flexibility. DiDi’s IBG CX team faced four core challenges:

- **QA judgments lack traceability.** QA judgments drive compliance audit outcomes and service improvement priorities. Yet the existing system operated as an opaque, closed system with no visible reasoning, while throughput and cost constrained manual spot-checks. Neither approach provided an audit trail for past decisions.
- **Combinatorial complexity of service scenarios.** Customer service operations span multiple languages and business lines, each combination governed by its own compliance standards and QA rules. As combinations multiply, rule maintenance costs escalate and consistency becomes harder to guarantee.
- **Slow response to QA standard changes.** QA standards shift frequently as the business evolves. Each change requires retraining QA analysts or updating execution guidelines, creating transition periods where old and new standards coexist and inconsistent results emerge.
- **Lack of proactive trend detection.** When a specific issue type surges within a short time window, the operations team can only detect it by reading tickets one by one and manually tallying. Early trend identification and timely intervention become nearly impossible.

To address these challenges, DiDi’s IBG CX team partnered with AWS to build a self-owned intelligent QA system on Amazon Bedrock. The team chose Amazon Bedrock for three reasons. First, its model-agnostic access to a broad selection of foundation models through a single API means the team can choose the best-fit model for each pipeline without re-architecting. Second, its built-in governance and security controls keep sensitive customer service data within DiDi’s network boundary and deliver the transparency and oversight the previous third-party solution lacked. These controls include private connectivity through Amazon Virtual Private Cloud (Amazon VPC) endpoints powered by AWS PrivateLink, encryption in transit and at rest, and fine-grained access control through AWS Identity and Access Management (IAM). Third, Amazon Bedrock Guardrails provides configurable safeguards such as content filtering and sensitive information redaction, giving the team a foundation for building the QA system in line with responsible AI practices.

## Solution overview

The system implements three specialized pipelines on [Amazon Bedrock](https://aws.amazon.com/bedrock/), each targeting a different QA dimension and producing a complete reasoning chain alongside every judgment. The intent pipeline verifies whether contact reasons assigned by representatives are correct. The evaluation pipeline audits service compliance and extracts business insights. The VOC pipeline aggregates large volumes of similar tickets to surface systemic trends.

The following diagram shows the end-to-end system architecture, from dual-channel data ingestion through preprocessing into the three pipelines powered by Amazon Bedrock.

![Dual-channel contact data flowing through preprocessing into the intent, evaluation, and VOC pipelines on Amazon Bedrock](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/31/ML-21371-1.png)

Figure 1: System architecture. Dual-channel data flows through preprocessing into three parallel pipelines powered by Amazon Bedrock, producing structured outputs with full reasoning

The preprocessing layer ingests live chat and phone data, normalizes it into a common schema, and fans out to three parallel pipelines. The overall workflow is as follows:

- **Data ingestion and preprocessing.** Live chat and phone transcripts (using speech-to-text) pass through channel-specific preprocessing, producing a unified conversation format for downstream consumption.
- **Intent pipeline.** Verifies whether the contact reason (CR, Sub-CR) assigned by the representative is accurate and recommends alternative classifications when incorrect. It also independently analyzes tickets labeled “Other” (those that cannot be classified under the existing taxonomy) to identify coverage gaps in the classification system.
- **Evaluation pipeline.** Performs multi-item compliance scoring and business insight (BI) analysis for each ticket simultaneously in a single large language model (LLM) call.
- **VOC pipeline.** Triggered on demand by the operations team, performs aggregation analysis on batches of similar tickets within a specific time window, producing structured analysis reports.
- **Output.** Delivers structured results from each pipeline for the operations team to query and visualize.

Because the system scores and classifies real customer conversations at scale, responsible AI controls are built in. We use Amazon Bedrock Guardrails to mask sensitive information such as personally identifiable information (PII) before it reaches the model and to apply contextual grounding checks that flag ungrounded responses, reducing hallucinated judgments. Beyond Guardrails, the system does not treat the model’s output as final: for rule-deterministic criteria, a programmatic post-validation layer re-checks the model’s judgments against the raw conversation. For example, reported spelling errors are verified only against the agent’s own messages, and the pass or fail threshold is applied on the verified count rather than the model’s own tally. Computable facts, such as agent response-wait times, are derived deterministically in code and injected into the prompt rather than left to the model to infer. Together with a full reasoning chain attached to every score for human review, these controls keep the system’s compliance decisions auditable and reliable in production.

## Intent pipeline: Information isolation for accurate classification

During ticket handling, the representative assigns contact reason labels. DiDi’s contact reason taxonomy (CR Tree) branches from broad categories into progressively finer subcategories across many levels. The deeper the hierarchy, the more subtle the distinctions, so mislabeling is inevitable at scale. The system must automatically verify whether these labels are accurate and recommend alternatives when wrong. It also audits the CR Tree in reverse, identifying coverage gaps, suggesting new labels, and closing the loop between QA and taxonomy maintenance.

The most direct approach was to feed the complete CR Tree plus conversation to the LLM in a single call. This approach produced accuracy far below expectations. We identified the root cause: when the LLM sees the complete list of options, it automatically compares them one by one. Even when the original label is entirely reasonable, finding a *slightly more precise* alternative triggers a judgment that the current label is wrong. Multiple rounds of prompt tuning could not change this behavior. The problem lay in context management, not prompt wording.

The team redesigned the pipeline in two ways:

- **Task isolation.** Contact reason verification and “Other” label analysis are fundamentally different tasks, so they are split into independent paths. Tickets labeled “Other” go through a dedicated three-level analysis. The system first checks whether a more appropriate label exists among sibling categories. If none is found, it searches the full CR Tree. If there is still no match, this indicates a coverage gap, and the system suggests adding a new label.
- **Information isolation.** For standard contact reasons, the flow is further split into verification and classification phases. In the verification phase, the LLM receives only the current contact reason label and judges whether the current label is reasonable based on conversation content alone. Only when verification determines a failure does the system enter the classification phase. At this point the LLM receives the full CR Tree along with the verification-phase reasoning, and recommends an alternative classification with confidence score and rationale.

Through this two-level design, intent verification accuracy improved from 38 percent to 86 percent in DiDi’s production validation.

## Evaluation pipeline: Dynamic assembly for multilingual, multi-business-line coverage

The evaluation pipeline scores multiple compliance items and extracts business insights for each ticket in one pass. Given the combinatorial complexity of languages and business lines and frequently changing QA standards, maintaining a separate prompt for each combination is unsustainable.

The solution is a unified prompt template with dynamic variable injection. Language context, business-line context, and each criterion’s definition and judgment rules live as external configurations. At call time, the system assembles them into a complete prompt based on the ticket’s metadata. Adding a new evaluation item, language, or business line requires only a configuration update. One template covers all combinations in a single LLM call.

The following diagram illustrates how the evaluation pipeline assembles external configuration into a unified prompt and produces structured output.

![Evaluation pipeline assembling external configuration into a unified prompt on Amazon Bedrock, producing structured compliance scores and business insights](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/08/31/ML-21371-2.png)

Figure 2: Evaluation pipeline. External configuration dynamically assembled into a unified prompt, processed by Amazon Bedrock to produce structured compliance scores and business insights

The following example is simplified to illustrate the two mechanisms working together: dynamic prompt assembly from external configuration, and the Tool Use capability of Amazon Bedrock forcing the model to return schema-validated JSON.

```
import boto3

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

MODEL_ID = "<your-bedrock-model-id>"

def build_output_schema(num_criteria):
    """Derive the JSON schema from the checklist size — adding a new
    compliance item requires only a config change, not a code change."""
    criteria = {
        f"criteria_{i}": {
            "type": "object",
            "properties": {
                "reasoning": {"type": "string"},
                "score": {"type": "integer"},  # 0 = pass, 1 = fail
            },
            "required": ["reasoning", "score"],
        }
        for i in range(1, num_criteria + 1)
    }
    return {
        "type": "object",
        "properties": {"scoring": {"type": "object", "properties": criteria}},
        "required": ["scoring"],
    }

def assemble_prompt(criteria_config, language, business_line):
    """Dynamic assembly: one template covers every language x business-line
    combination. Context lives in external config, injected at call time."""
    criteria_block = "\n".join(
        f"CRITERIA_{i}:\n- {c['parameter']}\n- PASS: {c['pass']}\n- FAIL: {c['fail']}"
        for i, c in enumerate(criteria_config, 1)
    )
    return (
        f"You are a customer service quality auditor for DiDi.\n"
        f"LANGUAGE CONTEXT: the conversation is in {language}.\n"
        f"BUSINESS CONTEXT: this is a {business_line} service interaction.\n\n"
        f"SCORING CRITERIA TO EVALUATE:\n{criteria_block}"
    )

def evaluate(transcript, criteria_config, language, business_line):
    system_prompt = assemble_prompt(criteria_config, language, business_line)
    schema = build_output_schema(len(criteria_config))
    response = bedrock.converse(
        modelId=MODEL_ID,
        system=[{"text": system_prompt}],
        messages=[{"role": "user", "content": [{"text": transcript}]}],
        # Tool Use with a forced tool choice constrains the model to emit
        # schema-valid JSON — every score carries its own reasoning chain.
        toolConfig={
            "tools": [{
                "toolSpec": {
                    "name": "output_result",
                    "description": "Output the structured evaluation result",
                    "inputSchema": {"json": schema},
                }
            }],
            "toolChoice": {"tool": {"name": "output_result"}},
        },
        inferenceConfig={"maxTokens": 8192, "temperature": 0.0},
    )
    for block in response["output"]["message"]["content"]:
        if "toolUse" in block:
            return block["toolUse"]["input"]
```

The Tool Use capability in Amazon Bedrock constrains output to structured JSON, with each score containing both the judgment and its reasoning chain. For rule-deterministic metrics, the system applies programmatic post-validation, using deterministic logic to calibrate the model’s semantic judgments.

In production validation, compliance scoring achieved over 90% average accuracy. The pipeline also outputs business insights (such as issue resolution rate and customer satisfaction). Because every judgment carries a reasoning chain, QA becomes a two-way improvement mechanism: representatives can understand why a score was assigned and adjust their service accordingly.

## VOC pipeline: Multi-stage processing for proactive trend discovery

The VOC pipeline is triggered on demand to analyze large batches of contacts within a specific time window, surfacing high-frequency issues that warrant systemic action. The challenge is extracting structured insights from thousands of conversations efficiently. Feeding them all to the LLM at once produces overly coarse categories and buries critical details.

The VOC pipeline uses a three-stage approach: **parallel extraction** to **issue clustering** to **report generation**, with each stage precisely controlling the information scope visible to the LLM.

- **Parallel extraction.** Each conversation independently calls the LLM to extract structured fields: issue type, user sentiment, resolution outcome, root cause, and more. Tickets are naturally parallelizable at this stage.
- **Issue clustering.** An embedding model computes semantic similarity between extracted issue-type labels, merging synonymous expressions (for example, “unpaid cancellation fee” and “cancellation fee not paid”), then ranks results by ticket frequency to surface the highest-impact issues. Because this stage uses embedding distance and statistical ranking rather than LLM generation, results are deterministic and reproducible.
- **Report generation.** The LLM generates an analysis report from the high-frequency clusters, covering an executive summary, pain-point analysis, and actionable improvement recommendations.

**Example:** When cancellation fee complaints surged across Latin American markets within a short period, the operations team triggered a VOC analysis. Within minutes, the system identified the primary root causes and high-frequency trigger scenarios from multilingual conversations, producing a structured report with actionable recommendations. This work previously took hours of manual reading and summarization.

## Conclusion

Reflecting on the collaboration, DiDi’s team summarized both the measurable outcomes and the deeper lesson the project delivered:

> “In international operations, multilingual and multi-business customer service QA is a scaling challenge — the existing solution was not only opaque, but also difficult to iterate quickly as business standards changed. After rebuilding this system with Amazon Bedrock, we achieved full transparency of QA judgments: intent verification accuracy improved from 38% to 86%, compliance scoring accuracy exceeded 90%, and trend analysis across large volumes of tickets was compressed from hours to minutes. This project taught us something fundamental: building reliable LLM applications depends not on the tool itself, but on the team’s deep mastery of context management and data definitions. That capability cannot be outsourced — and it is the most valuable outcome of this collaboration.”

— Raphael Hua, Data Analytics Team, DiDi International Business Group

DiDi’s intelligent QA system, built on [Amazon Bedrock](https://aws.amazon.com/bedrock/), achieved the transition from a third-party opaque system to transparent, controllable quality assurance through three pipelines:

- **Intent verification accuracy improved from 38 percent to 86 percent.** The two-level isolation design alleviated the LLM’s tendency to over-correct, improving the reliability of intent judgments.
- **Compliance scoring accuracy exceeded 90 percent.** Dynamic prompt assembly covered all language × business-line combinations in one template. The system outputs full reasoning chains with every judgment, making QA decisions traceable and actionable.
- **The VOC pipeline compressed hours of manual work to minutes.** The three-stage pipeline automatically extracted structured insights from large volumes of multilingual conversations, so the operations team could rapidly identify systemic trends.

The core takeaway: the performance bottleneck of LLM applications often lies not in prompt wording, but in context management. Precisely controlling what information the model sees in each call matters more than how you phrase the instruction. This principle runs through all three pipelines: information isolation in intent verification, dynamic assembly in evaluation, and multi-stage processing in VOC analysis.

DiDi plans to extend the system to additional business lines and languages, explore cross-pipeline data integration, and build deeper analytical capabilities on top of the existing foundation.

To learn more about the services used in this post, see [the Amazon Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html). For related guidance on building LLM applications and contact center AI on AWS, see [AI | AWS Contact Center](https://aws.amazon.com/blogs/contact-center/tag/ai/). If you’re interested in building similar intelligent QA systems, explore [Amazon Bedrock](https://aws.amazon.com/bedrock/) or contact [the AWS Generative AI Innovation Center](https://aws.amazon.com/ai/generative-ai/innovation-center/).

## About the authors
