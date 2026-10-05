---
vendor: aws_bedrock
title: How Trane gets building insights 60x faster with Amazon Bedrock AgentCore
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/how-trane-gets-building-insights-60x-faster-with-amazon-bedrock-agentcore
date: 2026-09-22
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 66989ec7a284
---

## [Artificial Intelligence](https://aws.amazon.com/blogs/machine-learning/)

# How Trane gets building insights 60x faster with Amazon Bedrock AgentCore

Trane Technologies manages millions of connected heating, ventilation, and air conditioning (HVAC) assets worldwide, but getting a single operational answer could mean cross-referencing multiple dashboards and drilling through menus for 20 minutes or more. For organizations operating at this scale, that kind of friction slows operations, defers corrective action, and creates material business impact across the enterprise.

In 3–4 weeks, Trane’s engineering team built an AI-powered agentic solution on [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) that reduced a 20-minute multi-screen diagnostic workflow to a 20-second natural language interaction. This is based on Trane’s internal benchmarking with technicians over several weeks. This represents a 60x improvement in time-to-insight, helping shift operations from reactive response to more proactive, data-driven optimization.

In this post, we describe the architectural approach and key design decisions behind the solution:

- Separating agent logic from tool execution.
- Integrating real-time telemetry through a centralized tool gateway.
- Tailoring responses to different personas.

## Trane Technologies and the building intelligence challenge

[Trane Technologies](https://www.tranetechnologies.com/en/index.html) is a global climate innovator with over $21 billion in annual revenue and operations in more than 100 countries. Through its strategic brand Trane, the company manages millions of connected HVAC assets, spanning data centers, hospitals, manufacturing facilities, and commercial real estate portfolios. At the heart of this vast landscape is [Trane Cloud](https://www.trane.com/commercial/north-america/us/en/products-systems/smart-building-technology/digital-platform.html), a digital hub that aggregates real-time performance data from millions of HVAC systems. Trane Cloud transforms raw equipment telemetry into actionable intelligence for predictive maintenance, energy optimization, and operational excellence.

While dashboard-based building management systems provide a foundation for monitoring and control, extracting cross-system insights can still require users to navigate multiple screens, layered menus, and disconnected dashboards. By combining natural language processing with deep integration into Trane Cloud, users can access that operational context through a single conversational interface. The result is faster answers to complex building management questions and a more proactive, informed approach to facility operations.

## Business challenge: Why building operators need an AI agent

Building operators, field technicians, and service managers have abundant data at their fingertips. Equipment telemetry, performance analytics, fault alerts, energy consumption patterns, and optimization opportunities flood in from disparate systems, yet extracting actionable insights remains difficult. The fundamental problem is that different stakeholders need radically different views of the same data.

Field technicians require diagnostic precision. They need refrigerant pressures, fault codes, and system-level troubleshooting workflows. Account managers need strategic intelligence. They need uptime metrics, cost savings opportunities, and portfolio performance trends. Building owners demand executive clarity. They need efficiency scores, sustainability metrics, and simplified operational summaries. Existing tools present a single interface across all roles, requiring each user to navigate features outside their workflow.

Existing building management applications rely on screen-by-screen navigation that makes cross-equipment comparison more challenging and demands that users memorize menu hierarchies and technical terminology. Even basic portfolio-level questions can require time-intensive manual workflows across multiple screens.

Together, Trane’s agentic AI solution and Trane Cloud deliver four capabilities:

- **Role-based access control** that tailors responses to each user’s permissions and needs.
- **Real-time HVAC analytics** providing instant access to current and historical performance data.
- **Intelligent search** across Trane’s knowledge base of technical documentation and best practices.
- **Extensible architecture** that evolves with advancing AI capabilities and expands to additional building systems.

These capabilities create a more scalable way to access building intelligence across roles, workflows, and operational environments.

## Solution overview: Architecture

The challenge of scaling intelligent building operations lies in turning the massive volume of data generated by millions of connected assets into actionable insight. Although Trane Cloud ingests real-time telemetry at scale, answering operational questions has traditionally required users to navigate disconnected dashboards and manually connect information across systems. To solve this, the team built a conversational agent on [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) and the [Strands framework](https://strandsagents.com/), deployed through [AWS Cloud Development Kit (AWS CDK)](https://aws.amazon.com/cdk/) infrastructure as code. The team chose Strands for the agent framework layer because it provides the developer SDK and orchestration logic for building agent behavior, while AgentCore handles the managed runtime, memory, tool gateway, and production infrastructure underneath.

To avoid the limitations of a monolithic design, the solution uses a multi-agent architecture where each specialized assistant is governed by its own system prompt, keeping it tightly focused on a single capability domain:

- **Resources Assistant** – Retrieves and summarizes reference material. For example, a user might ask: “Who do I contact, what manual should I follow, or what documentation can I share with the customer?”
- **Knowledge Assistant** – Synthesizes technical answers about how equipment works, its system parameters, or whether Trane Cloud’s infrastructure is SOC 2 attested.
- **Analytics Insights Assistant** – Interrogates live telemetry to surface efficiency opportunities, flag items needing inspection, and trace fault root causes.
- **Expert Advisor** – Helps users decide which product solution fits a scenario, how to maximize customer value, or how to assemble a customized demo.
- **Navigation Assistant** – Returns the exact links and tools a user needs, from the tech support escalation form to the replacement-parts order page.

This architecture is designed for extensibility. Teams can connect additional agents or tools, such as work order management systems and enterprise customer relationship management (CRM) systems, through AgentCore Gateway, a capability of Amazon Bedrock AgentCore, and open standards like the Model Context Protocol (MCP).

Figure 1: High-level architecture of Trane’s conversational agent on Amazon Bedrock AgentCore

## Microservices architecture: System design and implementation challenges

Supporting these distinct user needs at enterprise scale requires an architecture that can evolve independently across capabilities. A monolithic agent would force every change (new tools, updated prompts, additional data sources) through a single deployment pipeline, creating bottlenecks as the system grows.

Reducing a 20-minute manual diagnosis to a 20-second conversation surfaced four architectural challenges. The first challenge was integration. The solution had to combine real-time telemetry with intelligent search across an extensive knowledge base while supporting connections to external systems like CRMs. The second was separation. Agent logic had to be untangled from backend tool execution so the two could deploy independently, with clear ownership boundaries. Third was context. The system needed to maintain conversational state across troubleshooting sessions without standing up complex custom vector database infrastructure. Fourth was observability. When an agent orchestrates multiple tools across a multi-step reasoning chain, failures become difficult to localize. A wrong answer could stem from a missing API credential, a malformed tool response, or a model hallucination. Without end-to-end tracing, the team had no way to distinguish between them at production scale.

## How Amazon Bedrock AgentCore addresses the challenges

Amazon Bedrock AgentCore is an agentic platform to build, connect, and optimize agents at scale, with any framework or model. The Trane team used four AgentCore capabilities to address the preceding challenges.

Before selecting AgentCore, the team evaluated hosting the agent on Amazon Elastic Container Service (Amazon ECS) and AWS Lambda. That approach would have required building session isolation, auto scaling logic, and per-session billing on top of the compute layer. Four differentiators drove the decision. First, the managed agent runtime alleviates infrastructure operations. There are no clusters to provision or scale, and no idle capacity to pay for between user sessions. Second, built-in session memory removes the need to stand up and maintain external vector databases or build custom context-window management code. Third, native tool orchestration through AgentCore Gateway turns existing internal APIs into agent-compatible tools without writing custom integration logic for each one. Fourth, AgentCore’s framework-agnostic design meant the team could use the Strands SDK without being locked into a proprietary orchestration layer, preserving flexibility as requirements change.

- **AgentCore runtime**: Trane uses AgentCore runtime, a capability of Amazon Bedrock AgentCore, to isolate each user session in a dedicated microVM with its own CPU, memory, and filesystem. AgentCore runtime terminates and sanitizes each microVM on session completion. The team chose it because the microVM model separates the user-facing agent from the backend MCP Server, letting the two deploy independently with clear ownership boundaries. AgentCore runtime physically isolates a field technician’s session from a building owner’s, reinforcing role-based access without custom infrastructure. Trane pays only for active compute during a session. The long pauses between tool calls (typical of agentic workflows) don’t accumulate cost.
- **AgentCore Gateway**: Trane uses AgentCore Gateway to expose Trane Cloud’s internal APIs as MCP-compatible tools that the team organized by capability domain and integrated with Amazon OpenSearch Service. The team chose it because connecting the suite of assistants to real-time analytics, equipment telemetry, and issue diagnostics required a single access layer that handles authentication and schema translation. Future integrations (CRMs, work order systems) connect through the same Gateway without additional plumbing.
- **AgentCore memory**: Trane uses AgentCore memory, a capability of Amazon Bedrock AgentCore, to maintain conversational state across troubleshooting sessions so users can ask natural follow-ups (“now compare that to last month”) without re-specifying context. The team chose it because the alternative was standing up a separate vector database and writing custom context-window management code. AgentCore memory provides short-term session memory out of the box, with a 90-day expiry lifecycle that balances contextual awareness with storage efficiency, helping Trane address their data retention policies.
- **AgentCore Observability**: Trane uses AgentCore Observability, a capability of Amazon Bedrock AgentCore, to trace tool calls an agent makes and isolate failures across multi-step reasoning chains. The team chose it after encountering consistent tool failures during development that could not be identified without end-to-end visibility. Through the agent traces in Amazon CloudWatch, engineers confirmed the identical failure pattern across multiple invocations and traced it to a missing secret in AWS Secrets Manager. After adding the secret, the failures resolved.

The real-time data flow works as follows:

- The user’s query, carrying a JSON Web Token (JWT), hits AgentCore runtime. The Runtime’s inbound authorizer (AgentCore Identity, a capability of Amazon Bedrock AgentCore) validates the token against the OpenID Connect (OIDC) discovery endpoint. AgentCore memory then injects previous conversation context before the agent processes the request.
- The agent then triggers the separate MCP Server through OAuth 2.0 machine-to-machine authentication to securely access backend tools.
- The MCP Server executes parallel tool calls to OpenSearch Service and other connected systems for rapid semantic data retrieval.
- Finally, Anthropic Claude models on Amazon Bedrock synthesize the telemetry and stream the response back to the user through Server-Sent Events (SSE). This minimizes perceived latency, delivering answers in seconds. For model availability by AWS Region, refer to [Supported models by AWS Region in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html).

## Results and impact

Using Amazon Bedrock AgentCore and the Strands framework, the team achieved the 60x time-to-insight improvement described earlier. Cross-equipment comparisons and diagnostic workflows that once required navigating multiple screens now complete through a single natural language query in seconds. This helps teams move faster, reduce analysis steps, and take a more proactive approach to facility operations.

Beyond runtime performance, the architecture delivered additional benefits:

- **Rapid prototyping to production:** The team stood up a working prototype and demoed it to stakeholders within 3–4 weeks, then rolled the agent out first to internal field technicians as beta testers. Field technicians exercise the most demanding diagnostic workflows, so their feedback surfaced accuracy and usability gaps under real conditions. The team refined the agent responses based on that feedback before releasing to external customers.
- **Rapid integration across applications:** With decoupled microservices architecture and the centralized AgentCore Gateway, integrating the same agent backend into other enterprise applications took less than a day.
- **Effective production debugging:** The full invocation traces from AgentCore Observability in CloudWatch let the team pinpoint a recurring tool failure quickly.

## Production controls and responsible AI

Deploying an AI agent that returns diagnostic recommendations from live operational data requires controls against misuse and out-of-scope responses. The team configured [Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/) with content filters to block harmful or inappropriate outputs and topic denial policies that restrict the agent to its operational domain, helping restrict it from answering questions outside its operational domain. Sensitive information filters detect and redact personally identifiable information (PII) before responses reach the user, and prompt attack detection helps guard against jailbreak attempts that could bypass the agent’s system prompt.

At the infrastructure layer, Trane’s role-based access model helps restrict each user to data within their authorization scope. AgentCore runtime’s per-session microVM isolation helps prevent cross-tenant data leakage risk at the compute level. These controls work together so Trane can scale the agent to production users with confidence. Responses stay within scope, role-based access and PII filters help protect sensitive data, and Bedrock Guardrails help enforce the agent’s intended operational boundaries.

## Conclusion

Trane’s implementation demonstrates how organizations can use AI agents and their proprietary data as a distinct competitive advantage. By building on [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/), the organization established a robust, secure enterprise standard that can be scaled and reused across different business units.

This phased rollout, from a 3–4 week prototype, through accuracy tuning and an internal beta, to external release and reuse, surfaced five insights for scaling enterprise AI:

- **Data is your differentiator**: The foundation of the agent’s success relies on existing enterprise data, such as OpenSearch Service indexes and Internet of Things (IoT) telemetry. The agent’s true value comes directly from using this proprietary data to drive more efficient energy usage and operational excellence.
- **Architectural foundation matters:** The Strands framework helped the team get started and iterate rapidly, while Amazon Bedrock AgentCore provided the purpose-built infrastructure and secure services necessary for running agents at scale. Committing to open standards like MCP helped provide flexibility for future enhancements and accelerated the build.
- **Phase your rollout, harden internally first:** Deploying to internal field technicians (the most demanding users) captured critical technical feedback and let the team refine accuracy before releasing externally to Trane Cloud customers.
- **Role-based access and responses:** Different roles require different tools and different response formats. Dynamic policy mapping means a field technician receives step-by-step diagnostic workflows while a building owner receives simplified efficiency scores. This drives adoption because users see responses tailored to their role.
- **Observability is key for agentic systems:** When an agent orchestrates multiple tools in a reasoning chain, failures can be hard to identify. End-to-end invocation tracing through CloudWatch gave the team the ability to pinpoint and resolve issues quickly.

To learn more about building agentic solutions, visit the [Amazon Bedrock AgentCore documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html), explore the [Strands Agents SDK](https://strandsagents.com/), or follow the [AWS Artificial Intelligence Blog](https://aws.amazon.com/blogs/machine-learning/) for more customer stories.

## What’s next

The team is expanding the solution in several areas.

First, AgentCore Evaluations, a capability of Amazon Bedrock AgentCore, will gate future rollout phases on automated accuracy thresholds. Easing the burden on the quality assurance (QA) team, the team will define pass-rate benchmarks that must clear before each release moves forward.

Second, Policy in Amazon Bedrock AgentCore will replace custom authorization logic currently coded into the Runtime. Tool-level access decisions will shift to declarative policy definitions, making it easier to onboard new roles and audit who can invoke which tools.

Third, the team is opening their AgentCore Gateway to other engineering teams across Trane. Because the Gateway exposes tools through MCP, an open standard, other teams can build their own agents on top of the same centralized data layer without learning proprietary interfaces or standing up duplicate integrations. The team is building self-service onboarding with usage tracking so they can measure adoption and identify which tools other teams find most valuable.

Fourth, the team is adding new tools at a rapid pace. One example already in progress: field offices currently perform deep cost savings analyses manually for each customer site. The team is building this as an agent tool so the analysis runs on demand through natural language, removing hours of manual work per engagement.

## About the authors
