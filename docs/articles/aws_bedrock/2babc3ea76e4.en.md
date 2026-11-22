---
vendor: aws_bedrock
title: Make agents a reality with Amazon Bedrock AgentCore: Now generally available
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-is-now-generally-available
date: 2025-10-13
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: cfd3374c214c
---

# Make agents a reality with Amazon Bedrock AgentCore: Now generally available

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/10/img3.png)

## Get agents out of prototype purgatory and into production with security, scalability, and reliability

When we launched AWS in 2006, we believed that cloud computing would transform how organizations build and scale technology. We’re now at a similar inflection point with AI agents. We envision a world where billions of agents work together, transforming everything from daily operations to complex business processes. However, making this a reality requires more than frameworks or low-code builder tools. Agents that companies are willing to bet their business on need an enterprise-grade operational foundation—one that is secure, reliable, scalable, and purpose-built for the non-deterministic nature of agents. Drawing on our experience building mission-critical systems, [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) is a comprehensive agentic platform that enables organizations to get to production with confidence.

## AgentCore: Get agents to production fast

AgentCore, now generally available, makes it possible for every developer to get agents from pilots to full-scale production fast. AgentCore gives you the complete foundation you need to build, deploy, and operate agents. You can easily equip agents with tools, memory, and data to handle complex workflows. You can deploy agents with a few lines of code on one of the most secure and scalable runtimes available today. And you can operate those agents with the controls and access management required for enterprise deployments. You can do all of this without any infrastructure management, and it’s easy to get started using any model or agent framework of your choice.

The AgentCore SDK has been downloaded over a million times by customers of all sizes across multiple industries. Some of the early customers include Clearwater Analytics (CWAN), Cox Automotive, Druva, Ericsson, Experian, Heroku, National Australia Bank, Sony, Thomson Reuters, and many more. Supported by AWS Partners, including Accenture, Cisco, Deloitte, and Salesforce, AgentCore is already delivering transformative results.

## AgentCore: A comprehensive agentic platform

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/13/image-20-2.png)

Building agents can be hard – you need to figure out how to integrate with identity providers, how to build memory and observability, and integrate with tools. Our agentic platform offers fully-managed services across the agent development lifecycle from build to deploy to operate. You can mix and match, use any model or framework, offering maximum flexibility with access to enterprise-grade infrastructure and tools. Let’s look at its core capabilities.

**Build the way you want:** The agent landscape is evolving rapidly, with new frameworks, models, and protocols emerging almost weekly. You can build the way you want with composable AgentCore services that can be used together or independently. Your organization can choose which AgentCore services the team needs while using their preferred frameworks (including CrewAI, Google ADK, LangGraph, LlamaIndex, OpenAI Agents SDK, and Strands Agents) and models (including those available on Amazon Bedrock or models available outside Bedrock including OpenAI and Gemini), so you stay free to build the way you want.

**Foundational tools for agent success:** Agents create value with concrete actions – writing and executing code, connecting to company systems, and navigating the web. AgentCore provides these essential services: AgentCore Code Interpreter enables agents to generate and execute code securely in isolated environments, and AgentCore Browser allows agents to interact with web applications at scale. Meanwhile, AgentCore Gateway transforms your existing APIs and AWS Lambda functions into agent-compatible tools, connects to existing MCP servers, and provides seamless integration with essential third-party business tools and services (such as Jira, Asana, and Zendesk). This unified access point enables secure integration across your enterprise systems. With AgentCore Identity, agents can securely access and operate across these tools with proper authentication and authorization using OAuth standards.

**Context-aware agents with intelligent memory:** For agents to be truly effective, they need to maintain context and learn from interactions over time. Consider a sales support agent helping a customer explore enterprise software options – it should remember the customer’s industry, budget constraints, and technical requirements across multiple conversations, eliminating repetitive questions and delivering increasingly personalized recommendations. Similarly, when assisting with complex technical troubleshooting, an agent should recall previous debugging attempts and their outcomes to provide more targeted solutions. AgentCore Memory helps developers create these sophisticated, context-aware experiences without managing complex memory infrastructure, helping agents build and maintain detailed understanding of user preferences, historical interactions, and relevant context that enriches every conversation.

**Comprehensive observability for trustworthy agents:** Because agents reason in real-time and non-deterministically perform actions, you need complete visibility into the reasoning and actions of agents. Powered by [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/), AgentCore Observability provides comprehensive monitoring through real-time dashboards and detailed audit trails. Organizations can track every agent action, debug issues quickly, and continuously optimize performance. Through OpenTelemetry (OTEL) compatibility, AgentCore Observability integrates with existing monitoring tools, such as CloudWatch, Dynatrace, Datadog, Arize Phoenix, LangSmith, and Langfuse.

**Industry-leading reliability at any scale:** Unlike traditional applications, agent workload durations can be inherently unpredictable. AgentCore Runtime is designed for this variability, automatically scaling from zero to thousands of sessions as needed, and it offers an industry-leading runtime of eight hours for long running tasks.

**Enterprise-grade agent security:** Agents need to securely access multiple systems and handle sensitive data while acting on behalf of users, making robust security and regulatory compliance non-negotiable. AgentCore embeds security across every service to help agents operate safely. It supports virtual private cloud (VPC) environments and AWS PrivateLink to keep network traffic private and secure. Most importantly, AgentCore Runtime provides industry-leading security through microVM technology, giving each agent session its own isolated computing environment to prevent data leaks and maintain the integrity of every interaction.

**With AgentCore, speed, scale, and security get along:** AgentCore makes it easy to build production-ready agents through its MCP server, which works with integrated development environments (IDEs) like Kiro or Cursor AI. While it takes just minutes to get started, these aren’t simplified tools – they’re full-featured, production-ready solutions that can immediately scale from zero to thousands of sessions while maintaining robust security. This means your team can move quickly from idea to deployment with confidence, knowing your agents are built on a proven foundation.

## Making the promise of AI agents a reality: Customer stories

Pioneering organizations—from Cohere Health’s regulated healthcare environment to Ericsson’s complex technical systems to Sony’s global transformation—demonstrate how AgentCore is driving the next wave of AI innovation across industries. The organizations that succeed in the AI era won’t be those who perfectly predict the future, but those who build on proven foundations while maintaining the flexibility to evolve. When you build on AgentCore, you’re not just getting specialized services to deploy and operate agents, you’re getting a partner with nearly two decades of experience helping companies transform securely at global scale. Here are some stories that demonstrate customer impact:

Watch how Epsilon, part of the world’s largest advertising company Publicis Groupe, is using AgentCore to revolutionize campaign personalization for large brands. Their Intelligent Campaign Automation solution enables automated campaign design, audience targeting, and real-time optimization across multiple channels – delivering faster execution times and improved customer targeting precision at scale.

### Transforming manufacturing with intelligent workflow automation

Amazon Devices Operations & Supply Chain team is using AgentCore to develop an agentic manufacturing approach. As part of this new approach, AI agents work together using product specifications to automate manual processes. One agent reads the product requirements and creates detailed test procedures for quality control, while another agent trains the vision systems that robots need on the manufacturing line. As a result, fine-tuning an object detection model, which used to take days of engineering time, can now be done in under an hour with high precision. This proof-of-concept is just the beginning of their vision for smarter manufacturing, where AI agents will streamline the journey from initial product requirements to final production.

### Accelerating healthcare decisions with agents

In healthcare, every minute matters. Cohere Health® is a clinical intelligence company focused on strengthening payer-provider collaboration as well as improving the speed and accuracy of clinical decision-making, both pre- and post-care. The company’s clinically trained AI helps accelerate access to patient care, improve patient outcomes, reduce administrative burden for providers, and improve healthcare economics across the care continuum.

Using AgentCore, Cohere Health built Cohere Review Resolve™, an AI-powered copilot that optimizes the accuracy and efficiency of health plan medical necessity reviews. Cohere Review Resolve™ analyzes both structured and unstructured data–such as clinical records, patient notes, and faxes, quickly identifying and surfacing evidence to validate the medical necessity of a requested treatment. The copilot will provide health plans’ reviewers with complete clinical context for prior authorization requests and respond intelligently to reviewers’ queries.

Cohere Health chose AgentCore because they needed enterprise-grade infrastructure for their first production deployment of agentic AI in a highly regulated healthcare environment. The comprehensive audit trails, extended session support, and ability to maintain history throughout complex multi-hour workflows available in AgentCore are essential for their healthcare use case.

Cohere Health expects that Review Resolve™ will reduce review times by 30-40%, helping them to meet critical, mandated turnaround times. For patients, quicker decision-making will accelerate care access, increase adherence to therapy, improve outcomes and reduce costs. Review Resolve™ also improves upon their existing 90% automation rate while helping health plans by further increasing the accuracy of clinical determinations, thereby improving medical expense savings and patient outcomes.

### Agents in telecommunications: simplifying complex systems

Ericsson, a global leader in telecommunications technology, has used AgentCore to tackle its primary challenge in deploying agents. Dag Lindbo, Head of AI and Emerging Technologies in Business Area Networks at Ericsson says “At Ericsson, our 3G/4G/5G/6G systems span millions of lines of code across thousands of interconnected subsystems, representing decades of engineering innovation at the scale of nation-wide critical infrastructure. AgentCore powers our crucial fusion of data and information to deliver AI agents of unprecedented capability in real-world R&D, scaling to double-digit gains across a workforce in the tens of thousands. AgentCore also lets us use any agent framework, which is critical to help us scale across many teams and use cases.”

### Agents in entertainment: achieving security, observability and scalability

At Sony Group, one of the world’s leading technology and entertainment companies, AgentCore is already having an impact. “Agentic AI, which enables a new level of advanced operational efficiency and sophistication, is an essential technology for our AI transformation journey,” notes Masahiro Oba, Senior General Manager of AI Acceleration Division, Digital & Technology Platform for Sony Group Corporation. “However, it is also true that it presents many technical challenges. By leveraging Amazon Bedrock AgentCore, we built a group-wide Agentic AI Platform, achieving enterprise-level security, observability and scalability, along with seamless cross-platform connectivity to AI resources—a critical capability for us. By placing Amazon Bedrock AgentCore at the core of our agentic AI ecosystem, we gain the ability to govern and share vast amounts of AI, enabling us to accelerate AI transformation with confidence and security.”

## Building the foundation for the AI agent era at AWS

AgentCore is now generally available in nine AWS Regions to support global deployment needs, including Asia Pacific (Mumbai), Asia Pacific (Singapore), Asia Pacific (Sydney), Asia Pacific (Tokyo), Europe (Dublin), Europe (Frankfurt), US East (N. Virginia), US East (Ohio), and US West (Oregon). Organizations can accelerate time-to-value with pre-built agents and tools from [AWS Marketplace](https://aws.amazon.com/marketplace/solutions/ai-agents-and-tools?trk=70405219-a2f8-4816-a915-9932f523f1bd&sc_channel=el) that are designed to work on AgentCore.

Get started with AgentCore today – Visit [aws.amazon.com/bedrock/agentcore/](https://aws.amazon.com/bedrock/agentcore/) to start building your agentic future!

**Learn more:**

- [Accelerate development with the Amazon Bedrock AgentCore MCP server](https://aws.amazon.com/blogs/machine-learning/accelerate-development-with-the-amazon-bedrock-agentcore-mcpserver/) (by Shreyas Subramanian and Primo Mu, AWS ML Blog, 10/02/2025)
- [Introducing Amazon Bedrock AgentCore: Securely deploy and operate AI agents at any scale (preview)](https://aws.amazon.com/blogs/aws/introducing-amazon-bedrock-agentcore-securely-deploy-and-operate-ai-agents-at-any-scale/) (by Danilo Poccia, AWS News Blog, 7/16/2025)
- [AWS announces new innovations for building AI agents at AWS Summit New York 2025](https://www.aboutamazon.com/news/aws/aws-summit-agentic-ai-innovations-2025) (Amazon news summary, 7/16/2025)

### About the author

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2022/10/31/swami.png)Swami Sivasubramanian** is Vice President for Agentic AI at Amazon Web Services (AWS). At AWS, Swami has led the development and growth of leading AI services like Amazon DynamoDB, Amazon SageMaker, Amazon Bedrock, and Amazon Q. His team’s mission is to provide the scale, flexibility, and value that customers and partners require to innovate using agentic AI with confidence and build agents that are not only powerful and efficient, but also trustworthy and responsible. Swami also served from May 2022 through May 2025 as a member of the National Artificial Intelligence Advisory Committee, which was tasked with advising the President of the United States and the National AI Initiative Office on topics related to the National AI Initiative.
