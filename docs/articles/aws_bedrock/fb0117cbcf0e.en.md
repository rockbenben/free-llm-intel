---
vendor: aws_bedrock
title: How Standard Bank Group automates AI risk assessment for generative AI
original_title: How Standard Bank Group automates AI risk assessment for generative AI
url: https://aws.amazon.com/blogs/machine-learning/how-standard-bank-group-automates-ai-risk-assessment-for-generative-ai
date: 2026-11-20
lang: en
captured: 2026-11-21
extractor: readability-v1
status: ok
body_sha: 1f46dc6ead8d
---

## [Artificial Intelligence](https://aws.amazon.com/blogs/machine-learning/)

# How Standard Bank Group automates AI risk assessment for generative AI

*This post is co-written with Tala Qraitem from AWS and Jörg Fischer from Standard Bank Group*

Having an AI policy is one thing. Proving, one use case at a time, that AI systems follow it is another. Every new generative AI application adds one more system to prove. Teams can now build one in days, but each still needs a risk committee’s approval before it reaches customers or employees. When that approval depends on reviewers reading documents and testing the system by hand, governance becomes the slowest step in the pipeline.

Standard Bank Group chose to automate that proof. Working with AWS Professional Services, the bank deployed an automated assessment that scores each generative AI use case against international AI standards and its own policies. The assessment produces reports and a dashboard that show what is already in place, what is working well, and what still needs mitigation. This post explains how the assessment runs on AWS and what Standard Bank Group learned from its first runs.

## Governing AI with the framework you already have

Standard Bank Group didn’t need a new AI policy. Like most large banks, it already had an established model risk practice that covers concerns such as explainability and fairness, and a change risk process that assesses each new use case according to its level of risk before it goes live.

Generative AI increases the complexity, because models and tooling change every three to six months, yet each use case still needs to meet the same high security and compliance bar.

> “At Standard Bank, this assessment demonstrates how we are working with AWS to embed intelligent, automated risk management into our AI journey, allowing us to accelerate meaningful business value while maintaining the trust and controls that banking demands. We believe responsible AI is not about slowing innovation down but enabling it to build and scale with confidence.”

— Jörg Fischer, Group Chief Information and AI Officer, Standard Bank Group

The goal was to automate evidence gathering and testing, then feed the results into the approval gates Standard Bank Group already runs. Review and approval stay with the risk committee, but the committee now bases each decision on consistent evidence, collected the same way across use cases.

## How the assessment works

Figure 1 shows how the assessment’s components fit together in Standard Bank Group’s AWS account, from intake through evaluation to reporting.

![Architecture diagram of the automated AI risk assessment running in Standard Bank Group’s AWS account](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/19/ML-22493-1.png)

Figure 1: The assessment pipeline in Standard Bank Group’s AWS account, from intake through evaluation to reporting

The assessment runs entirely in Standard Bank Group’s own AWS account. Documents, code, and test results stay in an Amazon Simple Storage Service (Amazon S3) bucket there. The AWS Well-Architected Tool handles intake, AWS Step Functions orchestrates the pipeline, and a foundation model on Amazon Bedrock evaluates the evidence. It uses a technique called LLM-as-a-judge, in which a large language model checks evidence against defined criteria.

With Amazon Bedrock, Standard Bank Group could use a foundation model without stepping outside the controls it already runs on AWS. The bank controls access to the model through AWS Identity and Access Management (IAM), just as it does for its other AWS workloads. Amazon Bedrock doesn’t share the bank’s prompts or model outputs with model providers, and doesn’t use them to train models. Because Amazon Bedrock offers many foundation models through one API, the team can move to a newer judge model by changing a configuration setting instead of rebuilding the pipeline.

Each assessment moves through four steps. In the first two, a pre-assessment agent collects evidence about the use case, then the pipeline examines it and tests the application directly. The third evaluates that evidence against controls. The fourth summarizes the results in a standard, predefined format and delivers them to the people who act on them.

### Step 1: A pre-assessment agent collects the evidence

The custom lens in the Well-Architected Tool holds about 40 questions, each covering a risk event such as incomplete technical documentation or insufficient human oversight. Delivery teams no longer fill it in from scratch. A pre-assessment agent running on AWS Fargate scans the use case’s code repository and documentation. It maps relevant files to each question and pre-populates the lens with answers and links to the evidence. The delivery team then reviews those answers, corrects any mistakes, and adds the evidence the agent couldn’t find.

### Step 2: The pipeline examines the artifacts and tests the application

The pipeline works from four kinds of evidence.

- System documentation, which describes how the application was designed, built, and evaluated.
- Policy documents, which set out roles, responsibilities, and procedures such as incident handling.
- Source code and the system prompt, which show how controls are implemented.
- Live calls to the application, which show how it behaves in practice.

For documents and code, the pipeline checks whether each artifact contains what its mapped control requires. Each control comes from an international AI standard or framework, or from Standard Bank Group’s own policies. An incident procedure, for example, needs to describe how incidents are reported.

For live testing, the pipeline calls the application through its AWS Lambda function or API. The delivery team supplies questions a typical user would ask. The pipeline adds a built-in set of jailbreak attempts and off-topic questions, which the application is expected to decline. It also sends the same prompt several times, in its original and reworded forms, and uses an embedding model on Amazon Bedrock to check that the answers stay consistent in meaning. Where the team provides expected answers, the pipeline measures how closely the responses match them. Every response is stored in Amazon S3, so reviewers can see exactly what the application generated.

### Step 3: LLM-as-a-judge evaluation against standards

In this step, a foundation model on Amazon Bedrock acts as the judge. The assessment uses the model as-is with no fine-tuning or customization. (Model availability varies by AWS Region, so check the [supported models by Region](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html) before you deploy.) For each question, the model checks whether specific evidence appears in the artifacts and in the application’s responses, and returns yes or no.

Every check maps to a control in an international standard or framework for AI management, AI risk, or AI security. Standard Bank Group also customized the lens with judge questions built from its own standards, bringing the total to more than 300. The checks cover the eight AWS responsible AI dimensions in the following table:

| **Dimension** | **What the assessment looks for** |
| --- | --- |
| Veracity and robustness | Correct outputs, even with unexpected or adversarial inputs |
| Privacy and security | Appropriate collection, use, and protection of data and models |
| Transparency | Information that helps stakeholders make informed choices about their use of an AI system |
| Fairness | Consideration of impacts on different groups of stakeholders |
| Safety | Prevention of harmful output and misuse |
| Controllability | Mechanisms to monitor and steer system behavior |
| Governance | Best practices across the AI supply chain, including providers and deployers |
| Explainability | Ways to understand and evaluate system outputs |

Each risk receives a likelihood score, the share of required evidence the model couldn’t find, and a fixed severity level that the bank’s risk team can adjust. Together they produce a rating from Very low to Critical. Each missing piece of evidence maps to a specific mitigation and to the clause of the standard or policy it came from. A risk officer can then trace any findings back to their source when explaining decisions to a regulator. Figure 2 follows one missing piece of evidence through this process, from the evidence request to the recommended fix.

![A single missing piece of evidence traced to a scored finding and a recommended fix](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/19/ML-22493-2.png)

Figure 2: How one finding is traced from evidence to fix

Standard Bank Group protects and checks the assessment’s output in two ways. Every AI model interaction is protected by Amazon Bedrock Guardrails, ensuring alignment with the bank’s established security and responsible AI standards. The assessment’s model calls pass through the same safeguards the bank enforces across its AWS accounts for its AI workloads. These guardrails screen for harmful content and for attempts to manipulate the model.

The assessment is also designed so its output can be checked. Instead of asking the model for an open-ended opinion, the pipeline asks narrow yes-or-no questions, each worded to match a specific control. A fixed formula that the risk team can inspect turns those answers into scores. Each evaluation runs multiple times to measure how consistent the answers are and any inconsistent findings are flagged in the review interface. Every judgment is stored with the evidence behind it so that reviewers and auditors can trace how it was reached.

### Step 4: Reports for each audience

The pipeline summarizes the results in a standard format and delivers them as an executive presentation, a mitigation checklist, a detailed technical report, and an Amazon CloudWatch dashboard that tracks scores across use cases over time. Before a gate decision, reviewers confirm findings in a custom review interface with single sign-on. There they can add the use case, review the questions, amend answers with a business justification, and rewrite the output.

The assessment produces evidence against controls. It doesn’t certify compliance with any regulation, and Standard Bank Group remains responsible for its own regulatory determinations.

## Testing against Standard Bank Group’s own rules

International standards give every use case a common baseline, but the bank’s risk committees approve use cases against its own policy. A question factory addresses this by generating extra judge questions from internal documents. Standard Bank Group’s risk team used it to turn internal policies into checks that run on every use case.

Because those checks are derived directly from policy language, a policy change becomes a test change. Every subsequent assessment applies the updated rule automatically, with minimal manual rework by the risk team.

> “Most organizations treat policy as something you read. Standard Bank Group treats it as something you run. When every rule becomes a check that runs against the live system, a policy update stops being a memo and becomes a test. That fundamentally changes how fast a bank can scale AI responsibly.”

— Sri Elaprolu, Director, Frontier AI Science & Engineering, AWS

## Built into the use case lifecycle

The assessment fits into three stages of the use case lifecycle. During a proof of concept, it is optional, giving teams an early view of potential gaps. At the build stage, it becomes mandatory, and the approval gate draws on its results as formal evidence. Today the assessment runs in Standard Bank Group’s production environment, evaluating use cases before they go live. After live workloads are connected, the assessment will rerun on a schedule or whenever code or configuration changes, keeping the evidence current well beyond launch. The bank’s teams already trigger assessments on their own through a central system where use cases flow from intake to evaluation in a single workflow.

## What this means for financial institutions

At Standard Bank Group, the assessment reduced a traditionally manual two-week review to a comprehensive risk report generated in approximately two hours, demonstrated across six assessments. It also delivered a 14% improvement in use-case risk scores after remediation. This strengthens responsible AI governance, reduces compliance bottlenecks, and shortens the path from assessment to production.

This approach can benefit three groups involved in approving AI use cases:

- Risk and compliance leaders get evidence in the same format for every use case, traceable to a published standard or an internal policy clause. Start from the framework you already run, as Standard Bank Group did with its existing risk processes and approval gates.
- Delivery teams learn what to fix during the proof of concept, when changes cost the least, instead of meeting a rejection at the approval gate.
- Executives can grow the AI portfolio without growing the review effort at the same rate.

> “Adoption of AI at scale across the enterprise requires trust, both internally and with our customers. This assessment is proving key in enabling all our product teams to demonstrate that they are building enterprise-grade solutions aligned with both our own and industry best practices.”

— Duncan Macdonald, Chief Technology Officer, Standard Bank Group

## From approval gates to continuous assurance

Banks designed approval gates for systems that changed a few times a year. Generative AI applications change with every prompt update, model version, and new data source. As they take on more autonomous tasks, the number of decisions that need evidence keeps growing. Adding reviewers can’t keep pace with that rate of change.

Standard Bank Group’s approach points to a different operating model. When policies become tests and evidence is collected automatically, governance moves out of a checkpoint at the end of delivery and into the system itself. Every AI application in the portfolio can carry a current, auditable record of how it meets the bank’s standards, refreshed whenever its code or configuration changes. Risk teams spend their time on judgment calls and policy design, and the bank can show regulators the same evidence it uses for its own decisions.

The same foundation extends further. Continuous reassessment keeps evidence aligned with a changing code base after launch. New regulations can be encoded once as checks and applied across every use case. Aggregated scores give boards an enterprise-wide view of AI risk instead of a collection of individual reviews.

For any institution scaling AI, the question worth asking is how many of its policies have ever been tested against a running system. To explore how [AWS Professional Services](https://aws.amazon.com/professional-services/) can help your organization automate AI risk assessment, contact your AWS account team. To learn more about building AI responsibly on AWS, visit [Responsible AI on AWS](https://aws.amazon.com/ai/responsible-ai/).

## About the authors
