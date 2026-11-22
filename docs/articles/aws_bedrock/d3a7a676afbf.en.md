---
vendor: aws_bedrock
title: Vxceed builds the perfect sales pitch for sales teams at scale using Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/vxceed-builds-the-perfect-sales-pitch-for-sales-teams-at-scale-using-amazon-bedrock
date: 2025-10-08
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: acb34e69e948
---

# Vxceed builds the perfect sales pitch for sales teams at scale using Amazon Bedrock

*This post was co-written with Cyril Ovely from Vxceed.*

Consumer packaged goods (CPG) companies face a critical challenge in emerging economies: how to effectively retain revenue and grow customer loyalty at scale. Although these companies invest 15–20% of their revenue in trade promotions and retailer loyalty programs, the uptake of these programs has historically remained below 30% due to their complexity and the challenge of addressing individual retailer needs.

[Vxceed](https://vxceed.com/)’s Lighthouse platform tackles this challenge with its innovative loyalty module. Trusted by leading global CPG brands across emerging economies in Southeast Asia, Africa, and the Middle East, Lighthouse provides field sales teams with a cutting-edge, AI-driven toolkit. This solution uses generative AI to create personalized sales pitches based on individual retailer data and trends, helping field representatives effectively engage retailers, address common objections, and boost program adoption.

In this post, we show how Vxceed used [Amazon Bedrock](https://aws.amazon.com/bedrock/) to develop this AI-powered multi-agent solution that generates personalized sales pitches for field sales teams at scale.

### The challenge: Solving a revenue retention problem for brands

Vxceed operates mostly in the emerging economies. The CPG industry is facing challenges such as constant change, high customer expectations, and low barriers to entry. These challenges are more pronounced in the emerging economies. To combat these challenges, CPG companies worldwide invest 15–20% of their revenue annually in trade promotions, often in the format of loyalty programs to retailers.

The uptake of these loyalty programs, however, has traditionally been lower than 30% due to their complexity and the need to address each individual outlet’s needs. To make this challenge more complex, in emerging economies, these loyalty programs are primarily sold through the field sales team, who also act in the role of order capture and fulfilment, and the scale of their operation often spans across millions of outlets. To uplift the loyalty programs uptake, which in turn uplifts the brands revenue retention, the loyalty programs needed to be tailored at a personalized level and pitched properly to each outlet.

Vxceed needed a solution to solve this problem at scale, creating unique, personalized loyalty program selling stories tailored for each individual outlet that the field sales team can use to sell the programs.

This challenge led Vxceed to use Amazon Bedrock, a fully managed service that offers a choice of high-performing foundation models (FMs) from leading AI companies through a single API.

## Solution overview

To address the challenges of personalization, scale, and putting the solution in the hands of tens of thousands of field sales teams, Vxceed developed Lighthouse Loyalty Selling Story, an AI-powered solution. The Lighthouse Loyalty Selling Story architecture uses Amazon Bedrock, Amazon API Gateway, Amazon DynamoDB, and AWS Lambda to create a secure, scalable, AI-powered selling story generation system. The solution implements a multi-agent architecture, shown in the following figure, where each component operates within the customer’s private AWS environment, maintaining data security, scalability, and intuitive user interactions.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/19/vxceed-cpg-arch-1-1024x503.png)
 The solution architecture is built around several key components that work together to provide a curated sales enablement experience that is unique for each retailer customer:

- **Salesperson app** – A mobile application is used by field sales teams to access compelling program sales pitches and interact with the system through a chat interface. This serves as the primary touchpoint for sales representatives.
- **API Gateway and security** – The solution uses the following security services:  API Gateway serves as the entry point for application interactions. Security is enforced using[ AWS Key Management Service](https://aws.amazon.com/kms/) (AWS KMS) for encryption and [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/) for secure credentials management. [Amazon Simple Storage Service](https://aws.amazon.com/s3/) (Amazon S3) is used for image storage and management.
- **Intelligent agents** – The solution uses the following Lambda based agents:  Orchestration Agent coordinates the overall flow and interaction between components. Story Framework Agent establishes the narrative structure. Story Generator Agent creates personalized content. Story Review Agent maintains quality and compliance with brand guidelines. Brand Guidelines Agent maintains brand consistency. Business Rules Agent enforces business logic and constraints.
- **Data services layer** – The data services layer consists of the following components:  Data API services provide access to critical business information, including:  Outlet profile data Loyalty program details Historical data Purchase profile information  Integration with Lighthouse artificial intelligence and machine learning (AI/ML) models and data lake for advanced analytics. [Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/) for enhanced context and information.
- **Advanced capabilities** – The solution offers the following additional capabilities:  Q&A Service enables natural language interactions for sales queries. CTA (Call-to-Action) Service streamlines the retail outlet signup process. An Amazon Bedrock large language model (LLM) powers intelligent responses. [Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/) facilitates appropriate and compliance-aligned interactions.

The architecture implements a secure, scalable, and serverless design that uses AWS managed services to deliver a sophisticated sales enablement solution.

## Multi-agent AI architecture for secure orchestration

Vxceed built a multi-agent AI system on Lambda to manage personalized sales storytelling. The architecture comprises specialized agents that work together to create, validate, and deliver compelling sales pitches while maintaining alignment with business rules and brand guidelines.

The following is a detailed breakdown of the multi-agent AI architecture:

- **Orchestration Agent** – Coordinates the workflow between agents and manages the overall story creation process, interfacing with the Amazon Bedrock LLM for intelligent processing.
- **Story Framework Agent** – Establishes the narrative structure and flow of sales pitches based on proven storytelling patterns and sales methodologies.
- **Story Generator Agent** – Creates personalized content by combining data from multiple sources, including outlet profiles, loyalty program details, and historical data.
- **Story Review Agent** – Validates generated content for accuracy, completeness, and effectiveness before delivery to sales personnel.
- **Brand Guidelines Agent** – Makes sure generated content adheres to brand voice, tone, and visual standards.
- **Business Rules Agent** – Enforces business logic, customer brand compliance requirements, and operational constraints across generated content.

Each agent is implemented as a serverless Lambda function, enabling scalable and cost-effective processing while maintaining strict security controls through integration with AWS KMS and Secrets Manager. The agents interact with the Amazon Bedrock LLM and guardrails to provide appropriate and responsible AI-generated content.

## Guardrails

Lighthouse uses Amazon Bedrock Guardrails to maintain professional, focused interactions. The system uses denied topics and word filters to help prevent unrelated discussions and unprofessional language, making sure conversations remain centered on customer needs. These guardrails screen out inappropriate content, establish clear boundaries around sensitive topics, and diplomatically address competitive inquiries while staying aligned with organizational values.

## Why Vxceed chose Amazon Bedrock

Vxceed selected Amazon Bedrock over other AI solutions because of four key advantages:

- **Enterprise-grade security and privacy** – With Amazon Bedrock, you can configure your AI workloads and data so your information remains securely within your own virtual private cloud (VPC). This approach maintains a private, encrypted environment for AI operations, helping keep data protected and isolated within the your VPC. For more details, refer to Security in Amazon Bedrock.
- **Managed services on AWS** – Lighthouse Loyalty Selling Story runs on Vxceed’s existing AWS infrastructure, minimizing integration effort and providing end-to-end control over data and operations using managed services such as Amazon Bedrock.
- **Access to multiple AI models** – Amazon Bedrock supports various FMs, so Vxceed can experiment and optimize performance across different use cases. Vxceed uses Anthropic’s Claude 3.5 Sonnet for its ability to handle sophisticated conversational interactions and complex language processing tasks.
- **Robust AI development tools** – Vxceed accelerated development by using Amazon Bedrock Knowledge Bases, prompt engineering libraries, and agent frameworks for efficient AI orchestration.

## Business impact and future outlook

The implementation delivered significant measurable improvements across three key areas.

## Enhanced customer service

The solution achieved a 95% response accuracy rate while automating 90% of loyalty program-related queries. This automation facilitates consistent, accurate responses to customer objections and queries, helping salespeople and significantly improving the retailer experience.

### Accelerated revenue growth

Early customer feedback and industry analysis indicate program enrollment increased by 5–15%. This growth demonstrates how removing friction from the enrollment process directly impacts business outcomes.

### Improved operational efficiency

The solution delivered substantial operational benefits:

- 20% reduction in enrolment processing time
- 10% decrease in support time requirements
- Annual savings of 2 person-months per geographical region in administrative overhead

These efficiency gains help Vxceed customers focus on higher-value activities while reducing operational costs. The combination of faster processing and reduced support requirements creates a scalable foundation for program growth.

## Conclusion

AWS partnered with Vxceed to support their AI strategy, resulting in the development of Lighthouse Loyalty Selling Story, an innovative personalized sales pitch solution. Using AWS services including Amazon Bedrock and Lambda, Vxceed successfully built a secure, AI-powered solution that creates personalized selling stories at scale for CPG industry field sales teams. Looking ahead, Vxceed plans to further refine Lighthouse Loyalty Selling Story by:

- Optimizing AI inference costs to improve scalability and cost-effectiveness
- Adding a Language Agent to present the generated selling story in the native language of choice
- Adding RAG and GraphRAG to further enhance the story generation effectiveness

With this collaboration, Vxceed aims to significantly improve CPG industry field sales management, delivering secure, efficient, and AI-powered solutions for CPG companies and brands.

If you are interested in implementing a similar AI-powered solution, start by understanding how to implement asynchronous AI agents using Amazon Bedrock. See [Creating asynchronous AI agents with Amazon Bedrock](https://aws.amazon.com/blogs/machine-learning/creating-asynchronous-ai-agents-with-amazon-bedrock/) to learn about the implementation patterns for multi-agent systems and develop secure, AI-powered solutions for your organization.

### About the Authors

| ![Roger Wang](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/19/yibowang.jpg) | Roger Wang is a Senior Solution Architect at AWS. He is a seasoned architect with over 20 years of experience in the software industry. He helps New Zealand and global software and SaaS companies use cutting-edge technology at AWS to solve complex business challenges. Roger is passionate about bridging the gap between business drivers and technological capabilities, and thrives on facilitating conversations that drive impactful results. |
| --- | --- |
| ![Deepika Kumar](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/19/awsdeep.jpg) | Deepika Kumar is a Solutions Architect at AWS. She has over 13 years of experience in the technology industry and has helped enterprises and SaaS organizations build and securely deploy their workloads on the cloud. She is passionate about using generative AI in a responsible manner, whether that is driving product innovation, boosting productivity, or enhancing customer experiences. |
| ![Jhalak Modi](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/19/jhalaknz.jpg) | Jhalak Modi is a Solution Architect at AWS, specializing in cloud architecture, security, and AI-driven solutions. She helps businesses use AWS to build secure, scalable, and innovative solutions. Passionate about emerging technologies, Jhalak actively shares her expertise in cloud computing, automation, and responsible AI adoption, empowering organizations to accelerate digital transformation and stay ahead in a rapidly evolving tech landscape. |
| ![Cyril Ovely](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/19/cyril-vxceed.jpg) | Cyril Ovely, CTO and co-founder of Vxceed Software Solutions, leads the company’s SaaS-based logistics solutions for CPG brands. With 33 years of experience, including 22 years at Vxceed, he previously worked in analytical and process control instrumentation. An engineer by training, Cyril architects Vxceed’s SaaS offerings and drives innovation from his base in Auckland, New Zealand. |
