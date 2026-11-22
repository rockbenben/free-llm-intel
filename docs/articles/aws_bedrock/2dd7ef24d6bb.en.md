---
vendor: aws_bedrock
title: Rede Mater Dei de Saúde: Monitoring AI agents in the revenue cycle with Amazon Bedrock AgentCore
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/rede-mater-dei-de-saude-monitoring-ai-agents-in-the-revenue-cycle-with-amazon-bedrock-agentcore
date: 2026-04-15
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 1310dcaba6e3
---

# Rede Mater Dei de Saúde: Monitoring AI agents in the revenue cycle with Amazon Bedrock AgentCore

*This post is cowritten by Renata Salvador Grande, Gabriel Bueno and Paulo Laurentys at Rede Mater Dei de Saúde.*

The growing adoption of multi-agent AI systems is redefining critical operations in healthcare. In large hospital networks, where thousands of decisions directly impact cash flow, service delivery times, and the risk of claim denials, the ability to monitor, track, and govern AI agents has become essential for operational sustainability. This is the journey of Rede Mater Dei de Saúde, which is implementing its suite of 12 AI agents using [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/), a comprehensive service that provides agent runtime, tool integration, memory management, and built-in observability for production AI agents.

## **About Rede Mater Dei de Saúde**

With 45 years of history, Rede Mater Dei is one of Brazil’s most respected healthcare institutions, operating facilities in Belo Horizonte, Betim-Contagem, Nova Lima, Salvador, Uberlândia, Goiânia, Feira de Santana, and a new project underway in São Paulo. The organization combines technology, advanced analytical intelligence, and high-complexity care to deliver patient-centered outcomes and operational excellence.

## **Addressing a structural challenge in Brazilian healthcare**

In 2024, claim denials in Brazil reached alarming levels, according to the National Association of Private Hospitals ([Anahp](https://www.anahp.com.br/noticias/hospitais-reduzem-mortalidade-e-tempo-de-internacao-mas-enfrentam-alta-de-glosas-e-de-rotatividade/)): the sector average jumped from 11.89% to 15.89%, representing up to R$ 10 billion in unreceived revenues. Like many institutions, Rede Mater Dei faced operational challenges:

- **Manual processes** were typically handled by hundreds of operational staff.
- **Fragmented processes** were characterized by unstructured and dispersed data.
- **High-turnover teams** handled these procedures because the repetitive nature of tasks drove staff away.
- **Complex verifications **that demanded intense, constant attention created inconsistencies and rework in vulnerable stages of the process.

These weaknesses directly impacted the revenue cycle, from credentialing to billing, and exposed the organization to the same risks pressuring the entire sector to increase denials. With support from A3Data and AWS, Rede Mater Dei launched a transformation program to help reduce the causes of denials, accelerate analyses, and consolidate a governed, observable, scalable, and high-quality operation through AI agents.

### **Suite of 12 AI agents deployed on Amazon Bedrock AgentCore Runtime**

Rede Mater Dei, together with A3Data and the AWS Generative AI (GenAI) Innovation Center, structured a program featuring a complete suite of 12 AI agents designed to cover the entire hospital revenue cycle. This suite created a “digital force” where AI agents perceive, decide, and act as autonomously as possible, in an orchestrated, continuous, and auditable manner.

Among the first implemented agents of the 12 planned are:

- **Contracts Agent**: Centralizes and structures complex contractual rules previously scattered across disparate documents.
- **Parameterization Agent**: Automatically translates rules into the hospital’s enterprise resource planning (ERP) system, helping reduce human errors and accelerate updates.
- **Authorization Agent**: Automates requests, validations, and interactions with health insurers.

The agents are executed on Amazon Bedrock **AgentCore Runtime**, which provides the secure, serverless hosting environment for deploying, running, and scaling AI agents and tools.

The team organized the architecture into three complementary layers:

- **DEL (Data Execution Layer)**: Organizes data from multiple sources into a structured data lake.
- **AEL (Agent Execution Layer)**: Orchestrates and executes agents in an integrated manner.
- **TCL (Trust and Compliance Layer)**: Applies governance, security, and compliance alignment, facilitating traceability.

To govern AI agents, Rede Mater Dei partnered with A3Data and the AWS GenAI Innovation Center. Together, they built the entire critical execution and governance layer for agents on **Amazon Bedrock AgentCore**, which became the operational heart of the suite. This project is a pioneering initiative in Latin America. It tests [AgentCore Evaluations](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations.html) in a comprehensive, large-scale AI solution for a high-impact healthcare business application.

## **Why Amazon Bedrock AgentCore?**

As part of Amazon Bedrock, AgentCore is a comprehensive set of services providing the foundation for agentic use cases. It offers tools, deployment, and observability, along with the modular capabilities needed to deploy, operate, and refine AI agents at scale and with security. Components include:

- **Secure, serverless **[AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html).
- [AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html) to connect agents to existing tools and services.
- [AgentCore Memory](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html) for short- and long-term persistent memory to maintain context across sessions.
- **Observability resources** for monitoring.

The initial implementation focused on adding a monitoring and improvement layer to the existing multi-agent AI solution through [AgentCore Observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html) and **AgentCore Evaluations**.

Using AgentCore Evaluations, Rede Mater Dei added a **monitoring and evaluation layer to the solution. This layer supports continuous improvement of** multi-agent AI systems with measurable, controlled performance and high accuracy.

Through this service, it is possible to evaluate metrics and indicators considered global best practices, such as correctness, utility, precision, safety, objective success rate, and context relevance.

This evaluation structure provides **measurement and traceability** for AI agents. These capabilities help maintain stability, resilience, predictability, and regulatory adherence in the healthcare environment.

## **Architecture with AgentCore Evaluations**

The solution was designed and implemented as shown below, already incorporating AgentCore Evaluations:

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/04/01/ML-20233-image-1.png)

Architecture AgentCore Evaluations

### **517% ROI and structural efficiency across multiple processes**

The initial phase, anchored in AgentCore Observability and AgentCore Evaluations, enabled Rede Mater Dei to achieve measurable gains and lay the groundwork for a safer, more predictable, and data-driven AI operation. The initial phase delivered strong financial and clinical results: **517% return on investment (ROI) in the first four months**, **66% reduction in authorization time**, and **33% reduction in surgery start times**. Beyond these gains, the AgentCore governance layer expanded the institution’s capacity to operate and evolve its agents with control and transparency.

### **Governance and compliance**

Structured observability provided complete traceability for critical revenue cycle decisions, creating an immutable audit trail for every interaction, rule applied, and action taken by agents. This helped reduce regulatory risks, strengthen operational security, and simplify internal and external verifications—especially in sensitive processes like contracts, authorizations, and billing.

### **Operational efficiency**

With unified telemetry, teams reduced the time spent identifying and resolving failures, replicating impacts seen in other use cases with targets of up to **50% reduction in incident resolution time**. Teams can immediately spot anomalous behaviors, performance drops, or inconsistencies in agents, helping accelerate continuous improvement cycles and increase reliability in workflows directly affecting denial risk.

### **Strategic decision-making**

Real-time visibility into key performance indicators (KPIs) covers the volume of automated analyses, projected financial impacts, processing speed, estimated denial risk, successful validation rates, and metrics per insurer. These insights transformed operational data into faster, more precise executive decisions. They guide rule adjustments, backlog prioritization, team scaling, and surgical interventions in workflows most impacting revenue and efficiency. Together, these results demonstrate that the combination of Mater Dei’s agent suite and AgentCore helps not only deliver immediate gains but also helps establish the foundation for a more robust, auditable, and scalable hospital operation capable of supporting the network’s expansion and tackling Brazil’s structural challenge of claim denials.

Beyond achieved results, the project has become a global reference, featured in a [keynote speech by Ruba Borno](https://youtu.be/JVj-r7B0gOU?t=991) (VP, AWS Specialists and Partners) at AWS re:Invent 2025 in Las Vegas, showcasing that transforming the revenue cycle is not only possible: it is measurable, rapid, and capable of generating substantial returns.

## **Testimonials**

> “Together with A3Data, we are transforming a historical industry challenge with a more analytical, structured, and innovation-driven approach. Our focus is to enhance accuracy, predictability, and agility in critical revenue cycle stages, reducing variability and strengthening operational and financial efficiency for the network. This improved consistency naturally translates into a smoother patient experience, driven by more organized and technically robust processes.”
>         – Renata Salvador Grande, Vice President of Commercial and Marketing, Rede Mater Dei de Saúde

### **About the authors**
