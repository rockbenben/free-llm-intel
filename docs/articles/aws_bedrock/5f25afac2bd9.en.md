---
vendor: aws_bedrock
title: Building health care agents using Amazon Bedrock AgentCore
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/building-health-care-agents-using-amazon-bedrock-agentcore
date: 2025-09-26
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 0a2ee158a628
---

# Building health care agents using Amazon Bedrock AgentCore

*This blog was co-authored with Kuldeep Singh, Head of AI Platform at Innovaccer.*

The integration of agentic AI is ushering in a transformative era in health care, marking a significant departure from traditional AI systems. Agentic AI demonstrates autonomous decision-making capabilities and adaptive learning in complex medical environments, enabling it to monitor patient progress, coordinate care teams, and adjust treatment strategies in real time. These intelligent systems are becoming deeply embedded in healthcare operations, from enhancing diagnostic precision through advanced pattern recognition to optimizing clinical workflows and accelerating drug discovery processes. Agentic AI combines proactive problem-solving abilities with real-time adaptability so that healthcare professionals can focus on high-value, patient-centered activities while the AI handles routine tasks and complex data analysis.

Innovaccer, a pioneering healthcare AI company, recently launched [Innovaccer Gravity™](https://innovaccer.com/resources/news/innovaccer-launches-gravity-healthcare-intelligence-platform-accelerate-ai-driven-transformation), built using [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore), a new healthcare intelligence platform set to revolutionize data integration and AI-driven healthcare transformation. Building on their impressive track record—where their existing solutions serve more than 1,600 US care locations, manage more than 80 million unified health records, and have generated $1.5B in cost savings—this exemplifies how AWS customers are leading the agentic AI evolution by creating intelligent solutions that transform healthcare delivery while delivering significant ROI.

Health care demands precision and accountability. AI agents operating within this domain must handle sensitive patient data securely, adhere to rigorous compliance regulations (like [HIPAA](https://www.cdc.gov/phlp/php/resources/health-insurance-portability-and-accountability-act-of-1996-hipaa.html)), and maintain consistent interoperability across diverse clinical workflows. Standard, generalized protocols fall short when dealing with complex healthcare systems and patient data protection requirements. Healthcare organizations need a robust service to convert their existing APIs into [Model Context Protocol (MCP) ](https://modelcontextprotocol.io/docs/getting-started/intro)compatible tools that can scale effectively while providing built-in authentication, authorization, encryption, and comprehensive audit trails. [Amazon Bedrock AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html) offers health care providers and digital health companies a straightforward and secure way to build, deploy, discover, and connect to tools at scale that they can use to create AI-powered healthcare solutions while maintaining the highest standards of security and compliance.

## Problem

Healthcare organizations face significant data silo challenges because of diverse electronic health record (EHR) formats across different systems, often maintaining multiple systems to serve specialized departmental needs and legacy systems. FHIR (Fast Healthcare Interoperability Resources) solves these interoperability challenges by standardizing healthcare data into exchangeable *resources* (like patient records and lab results), enabling seamless communication between different systems while maintaining security and improving care coordination. However, implementing FHIR presents its own challenges, including technical complexity in integrating with legacy systems and the need for specialized expertise in healthcare informatics and API development.

The implementation of AI agents introduces new layers of complexity, requiring careful design and maintenance of interfaces with existing systems. AI agents need secure access to the FHIR data and other healthcare tools with authentication (both inbound and outbound) and end-to-end encryption. MCP is a standardized communication framework that enables AI systems to seamlessly interact with external tools, data sources, and services through a unified interface. However, the development and scaling of MCP servers require substantial resources and expertise. Hosting these services demands ongoing development time and attention to maintain optimal performance and reliability. As healthcare organizations navigate this complex terrain, addressing these challenges becomes critical for achieving true interoperability and harnessing the full potential of modern healthcare technology.

## Deploy, enhance, and monitor AI agents at scale using Amazon Bedrock AgentCore

By using Amazon Bedrock AgentCore, you can deploy and operate highly capable AI agents securely at scale. It offers infrastructure purpose-built for dynamic agent workloads, powerful tools to enhance agents, and essential controls for real-world deployment. Bedrock AgentCore offers a set of composable services with the services most relevant to the solution in this post mentioned in the following list. For more information, see the [Bedrock AgentCore documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html).

- [AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html) provides a secure, serverless runtime purpose-built for deploying and scaling dynamic AI agents and tools using any open source framework, protocol, and model. Runtime was built to work for agentic workloads with industry-leading extended runtime support, fast cold starts, true session isolation, built-in identity, and support for multi-modal payloads.
- [AgentCore Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html) provides a secure way for agents to discover and use tools along with straightforward transformation of APIs, [AWS Lambda](https://aws.amazon.com/lambda) functions, and existing services into agent-compatible tools. Gateway speeds up custom code development, infrastructure provisioning, and security implementation so developers can focus on building innovative agent applications.
- [AgentCore Identity](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity.html) provides a secure, scalable agent identity and access management capability accelerating AI agent development. It is compatible with existing identity providers, avoiding the need to migrate uses or rebuild authentication flows.
- [AgentCore Observability](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html) helps developers trace, debug, and monitor agent performance in production through unified operational dashboards. With support for OpenTelemetry compatible telemetry and detailed visualizations of each step of the agent workflow.

In this solution, we demonstrate how the user (a parent) can interact with a Strands or LangGraph agent in conversational style and get information about the immunization history and schedule of their child, inquire about the available slots, and book appointments. With some changes, AI agents can be made event-driven so that they can automatically send reminders, book appointments, and so on. This reduces the administrative burden on healthcare organizations and the parents who no longer need to keep track of the paperwork or make multiple calls to book appointments.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/18/ML-19648-Arch.png)

As shown in the preceding diagram, the workflow for the healthcare appointment book built using Amazon Bedrock AgentCore is the following:

- **User interacts with Strands or LangGraph agent: **The solution contains both [Strands](https://strandsagents.com/) and [LangGraph](https://www.langchain.com/langgraph) agents. You can also use other frameworks such as AutoGen and CrewAI.
- **Reasoning LLM from Amazon Bedrock:** Claude 3.5 Sonnet large language model (LLM) is used from Amazon Bedrock. The model demonstrates advanced reasoning by grasping nuances and complex instructions, along with strong tool-calling capabilities that allow it to effectively integrate with external applications and services to automate various tasks such as web browsing, calculations, or data interactions.
- **Tools exposed using AgentCore Gateway:** AgentCore Gateway provides secure access to the necessary tools required for the Strands or LangGraph agent using standard MCP clients. In this solution, REST APIs are hosted on [Amazon API Gateway](https://aws.amazon.com/gateway) and exposed as MCP tools using AgentCore Gateway.
- **Ingress authentication for AgentCore Gateway:** AgentCore Gateway is protected with oAuth 2.0 using [Amazon Cognito](https://aws.amazon.com/cognito) as the identity provider. You can use other oAuth 2.0 compatible identity providers such as Auth0, and Keycloak as needed to fit your use case.
- **OpenAPI specs converted into tools with AgentCore Gateway:** Amazon API Gateway is used as the backend to expose the APIs. By importing the OpenAPI specs, AgentCore Gateway provides an MCP compatible server without additional configuration for tool metadata. The following are the tools used in the solution.  `get_patient_emr()`: Gets the parent’s and child’s demographics information. `search_immunization_emr()` – Gets the immunization history and schedule for the child. `get_available_slots()` – Gets the pediatrician’s schedule around parent’s preferred date. `book_appointment()` – Books an appointment and returns the confirmation number.
- **AWS Healthlake as the FHIR server:** [HealthLake](https://aws.amazon.com/healthlake/) is used to manage patient data related to demographics, immunization history, schedule and appointments, and so on. HealthLake is a HIPAA-eligible service offering healthcare companies a complete view of individual and patient population health data using FHIR API-based transactions to securely store and transform their data into a queryable format at petabyte scale, and further analyze this data using machine learning (ML) models.
- **Egress authentication from AgentCore Gateway to tools:** OAuth 2.0 with Amazon Cognito as the identity provider is used to do the authentication between AgentCore Gateway and the tools used in the solution.

## Solution setup

| **Important:** The following code example is meant for learning and demonstration purposes only. For production implementations, it is recommended to add required error handling, input validation, logging, and security controls. |
| --- |

The code and instructions to set up and clean up this example solution are available on [GitHub](https://github.com/awslabs/amazon-bedrock-agentcore-samples/tree/main/02-use-cases/healthcare-appointment-agent). When set up, the solution looks like the following and is targeted towards parents to use the for immunization related appointments.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/18/ML-19648-Demo.gif)

## Customizing the solution

The solution can be customized to extend the same or a different use case through the following mechanisms:

- **OpenAPI specification:** The solution uses a sample OpenAPI specification (named `fhir-openapi-spec.yaml`) with APIs hosted on API Gateway. The OpenAPI specification can be customized to add more tools or use entirely different tools by editing the YAML file. You must recreate the AgentCore gateway after making changes to the OpenAPI spec.
- **Agent instructions and LLM:** The `strands_agent.py` or `langgraph_agent.py` can be modified to make changes to the goal or instructions for the Agent or to work with a different LLM.

## Future enhancements

We’re already looking forward and planning future enhancements for this solution.

- **AgentCore Runtime:** Host strands or a LangGraph agent on AgentCore Runtime.
- **AgentCore Memory:** Use AgentCore Memory to preserve session information in short-term (in session) as well as long-term (across sessions) to provide a more personalized experience to the agent users.

## Innovaccer’s use case for Bedrock AgentCore

Innovaccer’s gravity platform includes more than 400 connectors to unify data from EHRs from sources such as Epic, Oracle Cerner, and MEDITECH, more than 20 pre-trained models, 15 pre-built AI agents, 100 FHIR resources, and 60 out-of-the-box solutions with role based access control, comprehensive audit trail, end-to-end encryption, and secure personal health information (PHI) handling. They also provide a low-code or no-code interface to build additional AI agents with the tools exposed using Healthcare Model Context Protocol (HMCP) servers.

Innovaccer uses Bedrock AgentCore for the following purposes:

- AgentCore Gateway to turn their OpenAPI specifications into HMCP compatible tools without the heavy lifting required to build, secure, or scale MCP servers.
- AgentCore Identity to handle the inbound and outbound authentication integrating with Innovaccer- or customer-provided OAuth servers.
- AgentCore Runtime to deploy and scale the AI agents with multi-agent collaboration, along with logging, traceability and ability to plug in custom guardrails.

Bedrock AgentCore supports enterprise-grade security with encryption in transit and at rest, complete session isolation, audit trails using [AWS CloudTrail](https://aws.amazon.com/cloudtrail), and comprehensive controls to help Innovaccer agents operate reliably and securely at scale.

## Pricing for Bedrock AgentCore Gateway:

AgentCore Gateway offers a consumption-based pricing model with billing based on API invocations (such as `ListTools`, `InvokeTool` and `Search API`), and indexing of tools. For more information, see the [pricing page](https://aws.amazon.com/bedrock/agentcore/pricing/).

## Conclusion

The integration of Amazon Bedrock AgentCore with healthcare systems represents a significant leap forward in the application of AI to improve patient care and streamline healthcare operations. By using the suite of services provided by Bedrock AgentCore, healthcare organizations can deploy sophisticated AI agents that securely interact with existing systems, adhere to strict compliance standards, and scale efficiently.

The solution architecture presented in this post demonstrates the practical application of these technologies, showcasing how AI agents can simplify complex processes such as immunization scheduling and appointment booking. This can reduce administrative burdens on healthcare providers and enhance the patient experience by providing straightforward access to critical health information and services.

As we look to the future, the potential for AI agents in the healthcare industry is vast. From improving diagnostic accuracy to personalizing treatment plans and streamlining clinical workflows, the possibilities are endless. Tools like Amazon Bedrock AgentCore can help healthcare organizations confidently navigate the complexities of implementing AI while maintaining the highest standards of security, compliance, and patient care.

The healthcare industry stands at the cusp of a transformative era, where AI agents will play an increasingly central role in delivering efficient, personalized, and high-quality care. By embracing these technologies and continuing to innovate, we can create a healthcare network that is more responsive, intelligent, and patient-centric than ever before.

### About the Authors

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/18/ML-19648-AuthorHeadshot-100x133.jpeg)**Kamal Manchanda** is a Senior Solutions Architect at AWS with 17 years of experience in cloud, data, and AI technologies. He works closely with C-level executives and technical teams of AWS customers to drive cloud adoption and digital transformation initiatives. Prior to AWS, he led global teams delivering cloud-centric systems, data-driven applications, and AI/ML solutions across consulting and product organizations. Kamal specializes in translating complex business challenges into scalable, secure solutions that deliver measurable business value.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/19/ML-19648-KuldeepHeadshot-100x101.jpeg)**Kuldeep Singh** is AVP and Head of AI Platform at Innovaccer. He leads the work on AI agentic workflow layers for Gravity by Innovaccer, a healthcare intelligence platform designed to unify data, agents, and compliant workflows so health systems can deploy AI at scale. With deep experience in data engineering, AI, and product leadership, Kuldeep focuses on making healthcare more efficient, safe, and patient-centered. He plays a key role in building tools that allow care teams to automate complex, multi-step tasks (like integrating payer or EHR data, orchestrating clinical agents) without heavy engineering. He’s passionate about reducing clinician burnout, improving patient outcomes, and turning pilot projects into enterprise-wide AI solutions.
