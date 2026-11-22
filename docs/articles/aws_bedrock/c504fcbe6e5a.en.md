---
vendor: aws_bedrock
title: Amazon Bedrock Flows is now generally available with enhanced safety and traceability
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-flows-is-now-generally-available-with-enhanced-safety-and-traceability
date: 2024-11-22
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 20e268b1ab75
---

# Amazon Bedrock Flows is now generally available with enhanced safety and traceability

Today, we are excited to announce the general availability of [Amazon Bedrock Flows](https://aws.amazon.com/bedrock/prompt-flows/) (previously known as Prompt Flows). With Bedrock Flows, you can quickly build and execute complex [generative AI](https://aws.amazon.com/ai/generative-ai/) workflows without writing code. Key benefits include:

- Simplified generative AI workflow development with an intuitive visual interface.
- Seamless integration of latest foundation models (FMs), Prompts, Agents, Knowledge Bases, Guardrails, and other AWS services.
- Flexibility to define the workflow based on your business logic.
- Reduced time and effort in testing and deploying AI workflows with SDK APIs and serverless infrastructure.

Bedrock Flows makes it easier for developers and businesses to harness the power of generative AI, enabling you to create more sophisticated and efficient AI-driven solutions for your customers.

[Thomson Reuters](https://www.thomsonreuters.com/en.html) transforms the way professionals work by delivering innovative tech and GenAI powered by trusted expertise and industry-leading insights.

> “The mandate of the Thomson Reuters Enterprise AI Platform is to enable our subject-matter experts, engineers, and AI researchers to co-create Gen-AI capabilities that bring cutting-edge, trusted technology in the hands of our customers and shape the way professionals work. Amazon Bedrock Flows will enable us to create complex, flexible, multi-prompt workflows which we can easily evaluate, compare and version. We can also quickly integrate flows with our applications using the SDK APIs for serverless flow execution — without wasting time in deployment and infrastructure management. We are excited about the potential productivity gain and acceleration for generative-AI application development with Bedrock Flows.” 
>         – Laura Skylaki, VP of Artificial Intelligence, Business Intelligence and Data Platforms at Thomson Reuters.

[Dentsu Creative](https://www.dentsucreative.com/) is a global creative agency network designed to create meaningful connection between brands and consumers.

> “We have successfully leveraged Amazon Bedrock Flows to transform customer experiences. Using Bedrock Flows, we accelerated the process of reshaping books into an easy-to-read format for readers with learning disabilities. Bedrock Flows also enabled us to easily connect customer service solutions with foundation models like Claude Haiku to address common inquiries, saving hours and allowing customer support teams to focus on more complex requests. By empowering non-technical users to understand how AI and business logic are applied with the intuitive visual interface, Bedrock Flows has driven transparency and visibility for generative AI solutions in our organization. Whether reaching new audiences or scaling customer requests, Dentsu continues to innovate with cutting-edge generative AI technology powered by Amazon Bedrock Flows.” 
>         – Thiago Winkler, Executive Director of Operations for Dentsu Creative Brazil

## **New capabilities in Amazon Bedrock Flows**

Organizations leveraging generative AI need robust safety controls and clear visibility into their AI workflows. Today, we’re announcing two new capabilities in Amazon Bedrock Flows that help customers build more secure and traceable AI applications:

- **Enhanced safety**: Ability to filter out harmful content and unwanted topics for Prompt and Knowledge base nodes powered by [Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/). Guardrails are now supported in two types of nodes:  **Prompt node**: Define and enforce controls over your FM interactions. **Knowledge base node**: Apply guardrails to responses generated from your knowledge base.

- **Enhanced traceability**: Ability to quickly validate and debug workflows with traceability of input & output and inline validations. Gain comprehensive visibility into your workflow execution and quickly pinpoint errors through:  Detailed traceability support for input and output nodes. Complete execution path information showing input, output, execution time, and errors for each node. Inline validation status of nodes in the visual builder.

Consider ACME Corp, a fictional ecommerce company building a customer service chatbot using Amazon Bedrock Flows. They face several challenges in their implementation:

- Their chatbot sometimes generates responses containing sensitive customer information.
- They struggle to maintain consistent response quality and tone across different customer interactions.
- They spend a lot of time and effort in troubleshooting issues in their application.
- They have no way to ensure that responses comply with company policies and regulatory requirements.
- They lack visibility into performance bottlenecks affecting customer experience.

Let’s explore how the new capabilities in Amazon Bedrock Flows address these challenges and enable Acme Corp to build a more secure, efficient, and transparent customer service solution.

## **Prerequisites**

Before implementing the new capabilities, make sure that you have the following:

- An AWS account
- In Amazon Bedrock:  [Create and test your base prompts](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-create.html) for customer service interactions in Prompt Management. [Set up your knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-create.html) with relevant customer service documentation, FAQs, and product information. Configure any auxiliary AWS services needed for your customer service workflow (for example, Amazon DynamoDB for order history).

- In Amazon Bedrock Guardrails:  [Create a guardrail configuration](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-create.html) for customer service interactions (for example, `CustomerServiceGuardrail-001`) with:  Content filters for inappropriate language and harmful content Personally identifiable information (PII) detection and masking rules for customer data Custom word filters for company-specific terms  Contextual grounding checks to ensure accurate information Test and validate your guardrail configuration. Publish a working version of your guardrail.

- Required IAM permissions:  [Access to Amazon Bedrock Flows](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-permissions.html) [Permissions to use configured guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-permissions.html) Appropriate access to any integrated AWS services

After these components are in place, you can proceed with implementing the new capabilities in your customer service workflow.

## **Enabling enhanced safety in Flows**

For Acme Corp’s customer service chatbot, implementing guardrails helps ensure safe, compliant, and consistent customer interactions.

Here’s how to enable guardrails in both Prompt node and Knowledge base node:

- In the AWS Management Console for Amazon Bedrock, open the Prompt node or Knowledge base node in your `customer service flow` where you want to add guardrails. Create a new flow if required.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image001.png)
- In the node configuration panel, locate the **Guardrail **section.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image003.png)
- Select an existing guardrail from the dropdown menu. For example, **CustomerServiceGuardrail-001**.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image005.png)
- In this instance, `CustomerServiceGuardrail-001` is configured to:  Mask customer PII data (name and email) Block inappropriate language and harmful content Have responses align with company policy Maintain professional tone in responses

- Choose the appropriate version of your guardrail. For example, **Working draft**.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image007.png)
- Enter your prompt message for customer service scenarios. For example, `Respond to customer queries`.
- Connect your Prompt node to the flow’s input and output nodes.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image009.png)
- Test your Flows with the implemented guardrails by entering a prompt in the Test Flow. For example, `Hi, my name is John Smith, email – [john.smith@email.com](mailto:john.smith@email.com). How do I get started with setting up an ACME Corp account?`
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image011.png)
- In the **Test flow** shown on the right pane of the interface, you can see how the model response handles sensitive information. For example:  Original response: “Dear Mr. *John Smith*…” Guardrail response: “Dear Mr. *{NAME}*…”  ![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image013.png)

## **Enhanced traceability with Flows Trace View**

The new Flows Tracing capability now provides detailed visibility into the execution of the flows, enhancing debugging capability with Trace view and inline validations. This comprehensive monitoring solution helps developers monitor, debug, and optimize their AI workflows more effectively.

Key benefits of enhanced traceability include:

- Complete execution path with visibility through Trace view
- Detailed input/output tracing for each node
- Errors, warnings, and execution timing for every node
- Quick identification of bottlenecks and issues
- Faster root-cause analysis for errors

For Acme Corp’s customer service team, the new Flows Tracing capability provides crucial insights into their chatbot’s performance and behaviours. This helps them:

- Monitor response times for customer interactions
- Identify patterns in customer queries that cause delays
- Debug issues in the conversation flow
- Optimize the customer experience

To use the Trace view:

- In the Amazon Bedrock console, open your flow and test it with sample query.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image015.png)
- After running your flow, choose **Show trace** to analyze the interaction.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image017.png)
- Review the Flow Trace window showing:  Response times for each step of the customer interaction How customer inputs are processed Where guardrails are applied Performance bottlenecks  ![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image019.png)
- Analyze execution details, including:  Customer query processing steps Response generation and validation Time taken by each step Error details and cause analysis  ![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image021.png)

## **Inline validation status**

The Flows visual builder and SDK now include intuitive node validation capabilities:

Visual Builder:

- Green background indicates a valid node configuration.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image023.png)
- Red background indicates an invalid node configuration that needs attention.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image025.png)
- Yellow background indicates a node configuration with warnings.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/ML-17650-image027-new.png)

These validation capabilities help developers quickly identify and resolve potential issues in their flows by giving real-time validation feedback during both visual and programmatic development.

## **Conclusion**

The integration of Bedrock Guardrails and enhanced traceability in Bedrock Flows represent a significant advancement in generative AI development. These capabilities enable developers to create more secure, transparent, and efficient AI-powered solutions, addressing critical challenges in the rapidly evolving field of AI application development.

Bedrock Flows with the new capabilities are now generally available in all regions that Amazon Bedrock is available except for GovCloud. Starting February 1st 2025, you will also be charged for Bedrock Flows usage based on the number of node transitions required to operate your workflows at $0.035 per 1000 node transitions. We invite you to explore these new capabilities and experience firsthand how they can improve your generative AI development process. To get started, open the Amazon Bedrock console and begin building flows with enhanced safety and visibility with Flows today. To learn more, see the AWS user guide for [Guardrails integration](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-guardrails.html) and [Traceability](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-trace.html). For pricing information, visit the [Amazon Bedrock pricing page](https://aws.amazon.com/bedrock/pricing/).

We’re excited to see the innovative applications you’ll build with these new capabilities. As always, we welcome your feedback through [AWS re:Post](https://repost.aws/) for Amazon Bedrock or your usual AWS contacts. Join the generative AI builder community at [community.aws](https://community.aws/) to share your experiences and learn from others.

### About the Authors

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/Amit-lulla.jpg) Amit Lulla **is a Principal Solutions Architect at AWS, where he architects enterprise-scale generative AI and machine learning solutions for software companies. With over 15 years in software development and architecture, he’s passionate about turning complex AI challenges into bespoke solutions that deliver real business value. When he’s not architecting cutting-edge systems or mentoring fellow architects, you’ll find Amit on the squash court, practicing yoga, or planning his next travel adventure. He also maintains a daily meditation practice, which he credits for keeping him centered in the fast-paced world of AI innovation.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/19/Huuong.jpg)**Huong Nguyen** is a Principal Product Manager at AWS. She is leading the Amazon Bedrock Flows, with 18 years of experience building customer-centric and data-driven products. She is passionate about democratizing responsible machine learning and generative AI to enable customer experience and business innovation. Outside of work, she enjoys spending time with family and friends, listening to audiobooks, traveling, and gardening.
