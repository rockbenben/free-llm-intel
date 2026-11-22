---
vendor: aws_bedrock
title: Accelerating software delivery with agentic QA automation using Amazon Nova Act
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/accelerating-software-delivery-with-agentic-qa-automation-using-amazon-nova-act
date: 2026-03-31
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: d0e0fa613a43
---

# Accelerating software delivery with agentic QA automation using Amazon Nova Act

Quality assurance (QA) automation is critical for modern software delivery. It catches regressions before production, validates user journeys at scale, and enables confident feature releases. But traditional QA automation solutions are brittle and demand specialized programming knowledge, decelerating software delivery.

Automation frameworks rely on implementation details including UI selectors, element identifiers, and structural references to navigate applications. When developers refactor UI code or designers adjust layouts, tests break even though functionality remains intact. This maintenance burden stems from a mismatch in how teams work. Product managers define acceptance criteria in the business language, development teams implement features, then developers write automation code. This puts distance between testing and those who understand user needs, forcing software teams to maintain tests instead of delivering features.

These challenges are addressed by Amazon Nova Act, an AWS service to build fleets of reliable agents that automate production UI workflows at scale. Its custom computer use model interacts with applications the same way that users do: through natural language and visual understanding, rather than code inspection. This removes code-dependent selectors and technical barriers, enabling agentic QA automation that reduces test maintenance overhead, democratizes test management, and accelerates software delivery cycles.

In this post, we demonstrate how to implement agentic QA automation through QA Studio, a reference solution built with Amazon Nova Act. You will see how to define tests in natural language that adapt automatically to UI changes, explore the serverless architecture that executes tests reliably at scale, and get step-by-step deployment guidance for your AWS environment.

### **QA Studio overview**

QA Studio provides a web frontend, API, and CLI for managing QA automation, built on serverless AWS infrastructure and powered by Amazon Nova Act for agentic UI automation. Run tests on demand, schedule them automatically, or trigger them as part of your continuous integration and delivery CI/CD pipeline.

Figure 1 – Nova QA Studio Test Case Execution Demo

### **Natural language test management**

Amazon Nova Act translates natural language instructions into browser interactions including navigation, data extraction, and assertions. Teams can use this to define tests in the same language that they use to describe product requirements, creating unified specifications where requirement changes flow directly into test definitions.

Teams can use QA Studio to create and execute tests using natural language to define test steps. Users create test suites through live browser preview powered by [Amazon Bedrock AgentCore Browser,](https://aws.amazon.com/bedrock/agentcore/) test generation from user journey descriptions using [Amazon Bedrock](https://aws.amazon.com/bedrock/), secure data entry through [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/), and other capabilities. Amazon Nova Act translates these test definitions into browser actions, while QA Studio provides the interface, so test authors can create and manage tests without writing or maintaining code.

Figure 2 – Test creation with the User Journey Wizard

### **Visual navigation that adapts to change**

The computer use model of Amazon Nova Act navigates applications using their visual appearance and context rather than relying on code dependent selectors. When designers adjust button placement or developers refactor component structure, tests adapt automatically. This removes the brittleness that creates maintenance overhead in traditional frameworks so that test authors can focus on what the application should do rather than how to locate elements in code.QA Studio provides an interface for users to execute and monitor tests, using the visual navigation of Amazon Nova Act for UI automation, data extraction, and state validation. Teams can use this to focus on delivering features rather than maintaining test infrastructure.

Figure 3 – A test in the QA Studio vs the equivalent traditional test automation code

### **End-to-End test visibility**

Amazon Nova Act provides trajectory logs that capture its visual reasoning and decision making at each step, showing exactly what the agent saw and why it took specific actions. This transparency transforms debugging from parsing technical stack traces into understanding test behavior through natural language descriptions and visual context.

QA Studio surfaces these insights throughout the testing lifecycle. During test creation, users preview steps with the live browser. When tests execute, teams receive real-time status updates and can monitor progress across test suites. After tests complete, QA Studio provides test recordings, results, and Nova Act trajectory logs with screenshots so that teams can identify issues without debugging code level errors.

## **Technical architecture**

QA Studio uses the following AWS services:

- [**Amazon Nova Act** ](https://aws.amazon.com/nova/act/)– Agentic UI automation
- [**Amazon CloudFront**](https://aws.amazon.com/cloudfront/)** and **[**Amazon Simple Storage Service (Amazon S3)**](https://aws.amazon.com/s3/) – React frontend delivery built with AWS Cloudscape Design System
- [**Amazon API Gateway**](https://aws.amazon.com/api-gateway/) – API endpoints and request routing
- [**AWS Lambda**](https://aws.amazon.com/pm/lambda/) – Backend API and application logic
- [**Amazon Cognito**](https://aws.amazon.com/cognito/) – User and machine-to-machine authentication
- [**Amazon DynamoDB** ](https://aws.amazon.com/dynamodb/)– Test definitions, execution history, and results storage using single-table design
- [**Amazon Elastic Container Service (Amazon ECS)**](https://aws.amazon.com/ecs/)** with **[**AWS Fargate**](https://aws.amazon.com/fargate/) – Containerized test execution workloads using [Nova Act SDK](https://github.com/aws/nova-act)
- [**Amazon Bedrock**](https://aws.amazon.com/bedrock/) – Access to foundational models for test case generation and [**AgentCore Browser**](https://aws.amazon.com/bedrock/agentcore/) for managed remote browsers
- [**Amazon Simple Queue Service (Amazon SQS)**](https://aws.amazon.com/sqs/) – Reliable test execution through queue-based processing
- [**Amazon S3**](https://aws.amazon.com/s3/) – Test recordings, screenshots, logs, and traces storage
- [**Amazon EventBridge**](https://aws.amazon.com/eventbridge/) – Automated test run scheduling

Figure 4 – QA Studio AWS architecture

This serverless architecture provides automatic scaling and consumption-based economics with pay-per-use pricing across all AWS services. You maintain control over security policies, compliance requirements, and customization needs.

## **Getting started with QA Studio**

QA Studio is available as a [GitHub repository](https://github.com/aws-samples/sample-qa-studio) that you deploy in your own AWS account using the [AWS Cloud Development Kit (AWS CDK)](https://aws.amazon.com/cdk/). This gives you complete control over your testing infrastructure, security policies, and compliance requirements—all test data, recordings, and logs remain within your security boundary. You can configure VPC settings and access controls according to your organization’s requirements.

To deploy the QA Studio in your AWS Account:

- Clone the [GitHub repository](https://github.com/aws-samples/sample-qa-studio).
- Follow the README guide to deploy the infrastructure using the AWS CDK.
- Configure notifications and CI/CD integration (optional).

For complete deployment instructions, refer to the [QA Studio GitHub repository](https://github.com/aws-samples/sample-qa-studio). The repository includes AWS CDK templates and all necessary components, guides, and documentation to deploy the QA Studio in your own AWS environment.

## **Cleaning Up**

If you deployed QA Studio for evaluation purposes, remember to delete the AWS resources to avoid incurring future costs. Refer to the GitHub repository README for complete deletion instructions.

Have questions about implementing QA Studio in your environment? Leave a comment, we’d love to hear about your testing challenges and how you’re planning to use AI-powered testing to accelerate your software delivery.

## **Conclusion**

In this post, we showed how agentic QA automation with Amazon Nova Act accelerates software delivery through natural language test management and visual navigation. QA Studio is a reference solution that removes technical barriers to QA automation and removes brittleness through visual understanding so that teams can focus on delivering features rather than maintaining test infrastructure.

In the [next post](https://aws.amazon.com/blogs/machine-learning/accelerating-software-delivery-with-agentic-qa-automation-using-amazon-nova-act-part-2/), we extend that foundation to demonstrate how QA Studio addresses batch regression testing and pipeline integration through test suites that organize and parallelize execution, and a command-line interface that brings agentic testing into automated CI/CD pipelines.

## About the authors
