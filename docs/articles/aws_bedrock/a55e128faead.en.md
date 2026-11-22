---
vendor: aws_bedrock
title: Automate IT operations with Amazon Bedrock Agents
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/automate-it-operations-with-amazon-bedrock-agents
date: 2025-03-21
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 862b75a3aa75
---

# Automate IT operations with Amazon Bedrock Agents

IT operations teams face the challenge of providing smooth functioning of critical systems while managing a high volume of incidents filed by end-users. Manual intervention in incident management can be time-consuming and error prone because it relies on repetitive tasks, human judgment, and potential communication gaps. Using [generative AI](https://aws.amazon.com/ai/generative-ai/) for IT operations offers a transformative solution that helps automate incident detection, diagnosis, and remediation, enhancing operational efficiency.

AI for IT operations (AIOps) is the application of AI and machine learning (ML) technologies to automate and enhance IT operations. AIOps helps IT teams manage and monitor large-scale systems by automatically detecting, diagnosing, and resolving incidents in real time. It combines data from various sources—such as logs, metrics, and events—to analyze system behavior, identify anomalies, and recommend or execute automated remediation actions. By reducing manual intervention, AIOps improves operational efficiency, accelerates incident resolution, and minimizes downtime.

This post presents a comprehensive AIOps solution that combines various AWS services such as [Amazon Bedrock](https://aws.amazon.com/bedrock/), [AWS Lambda](https://aws.amazon.com/lambda/), and [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/) to create an AI assistant for effective incident management. This solution also uses [Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/) and [Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/). The solution uses the power of Amazon Bedrock to enable the deployment of intelligent agents capable of monitoring IT systems, analyzing logs and metrics, and invoking automated remediation processes.

Amazon Bedrock is a fully managed service that makes foundation models (FMs) from leading AI startups and Amazon available through a single API, so you can choose from a wide range of FMs to find the model that is best suited for your use case. With the Amazon Bedrock serverless experience, you can get started quickly, privately customize FMs with your own data, and integrate and deploy them into your applications using AWS tools without having to manage the infrastructure. Amazon Bedrock Knowledge Bases is a fully managed capability with built-in session context management and source attribution that helps you implement the entire [Retrieval Augmented Generation](https://aws.amazon.com/what-is/retrieval-augmented-generation/) (RAG) workflow, from ingestion to retrieval and prompt augmentation, without having to build custom integrations to data sources and manage data flows. Amazon Bedrock Agents is a fully managed capability that make it straightforward for developers to create generative AI-based applications that can complete complex tasks for a wide range of use cases and deliver up-to-date answers based on proprietary knowledge sources.

Generative AI is rapidly transforming businesses and unlocking new possibilities across industries. This post highlights the transformative impact of large language models (LLMs). With the ability to encode human expertise and communicate in natural language, generative AI can help augment human capabilities and allow organizations to harness knowledge at scale.

## Challenges in IT operations with runbooks

Runbooks are detailed, step-by-step guides that outline the processes, procedures, and tasks needed to complete specific operations, typically in IT and systems administration. They are commonly used to document repetitive tasks, troubleshooting steps, and routine maintenance. By standardizing responses to issues and facilitating consistency in task execution, runbooks help teams improve operational efficiency and streamline workflows. Most organizations rely on runbooks to simplify complex processes, making it straightforward for teams to handle routine operations and respond effectively to system issues. For organizations, managing hundreds of runbooks, monitoring their status, keeping track of failures, and setting up the right alerting can become difficult. This creates visibility gaps for IT teams. When you have multiple runbooks for various processes, managing the dependencies and run order between them can become complex and tedious. It’s challenging to handle failure scenarios and make sure everything runs in the right sequence.

The following are some of the challenges that most organizations face with manual IT operations:

- Manual diagnosis through run logs and metrics
- Runbook dependency and sequence mapping
- No automated remediation processes
- No real-time visibility into runbook progress

## Solution overview

Amazon Bedrock is the foundation of this solution, empowering intelligent agents to monitor IT systems, analyze data, and automate remediation. The solution provides sample [AWS Cloud Development Kit](https://aws.amazon.com/cdk/) (AWS CDK) code to deploy this solution. The AIOps solution provides an AI assistant using Amazon Bedrock Agents to help with operations automation and runbook execution.

The following architecture diagram explains the overall flow of this solution.

![Amazon Bedrock AIOps Automation](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/19/ML-16260-Architecture-Diagram.jpg)

The agent uses Anthropic’s Claude LLM available on Amazon Bedrock as one of the FMs to analyze incident details and retrieve relevant information from the knowledge base, a curated collection of runbooks and best practices. This equips the agent with business-specific context, making sure responses are precise and backed by data from Amazon Bedrock Knowledge Bases. Based on the analysis, the agent dynamically generates a runbook tailored to the specific incident and invokes appropriate remediation actions, such as creating snapshots, restarting instances, scaling resources, or running custom workflows.

Amazon Bedrock Knowledge Bases create an [Amazon OpenSearch Serverless](https://aws.amazon.com/opensearch-service/features/serverless/) vector search collection to store and index incident data, runbooks, and run logs, enabling efficient search and retrieval of information. Lambda functions are employed to run specific actions, such as sending notifications, invoking API calls, or invoking automated workflows. The solution also integrates with [Amazon Simple Email Service](https://aws.amazon.com/ses) (Amazon SES) for timely notifications to stakeholders.

The solution workflow consists of the following steps:

- Existing runbooks in various formats (such as Word documents, PDFs, or text files) are uploaded to [Amazon Simple Storage Service](https://aws.amazon.com/s3) (Amazon S3).
- Amazon Bedrock Knowledge Bases converts these documents into vector embeddings using a selected embedding model, configured as part of the knowledge base setup.
- These vector embeddings are stored in OpenSearch Serverless for efficient retrieval, also configured during the knowledge base setup.
- Agents and action groups are then set up with the required APIs and prompts for handling different scenarios.
- The OpenAPI specification defines which APIs need to be called, along with their input parameters and expected output, allowing Amazon Bedrock Agents to make informed decisions.
- When a user prompt is received, Amazon Bedrock Agents uses RAG, action groups, and the OpenAPI specification to determine the appropriate API calls. If more details are needed, the agent prompts the user for additional information.
- Amazon Bedrock Agents can iterate and call multiple functions as needed until the task is successfully complete.

## Prerequisites

To implement this AIOps solution, you need an active AWS account and basic knowledge of the AWS CDK and the following AWS services:

- Amazon Bedrock
- Amazon CloudWatch
- AWS Lambda
- Amazon OpenSearch Serverless
- Amazon SES
- Amazon S3

Additionally, you need to provision the required infrastructure components, such as [Amazon Elastic Compute Cloud](https://aws.amazon.com/ec2) (Amazon EC2) instances, [Amazon Elastic Block Store](https://aws.amazon.com/ebs) (Amazon EBS) volumes, and other resources specific to your IT operations environment.

## Build the RAG pipeline with OpenSearch Serverless

This solution uses a RAG pipeline to find relevant content and best practices from operations runbooks to generate responses. The RAG approach helps make sure the agent generates responses that are grounded in factual documentation, which avoids hallucinations. The relevant matches from the knowledge base guide Anthropic’s Claude 3 Haiku model so it focuses on the relevant information. The RAG process is powered by Amazon Bedrock Knowledge Bases, which stores information that the Amazon Bedrock agent can access and use. For this use case, our knowledge base contains existing runbooks from the organization with step-by-step procedures to resolve different operational issues on AWS resources.

The pipeline has the following key tasks:

- **Ingest documents in an S3 bucket **– The first step ingests existing runbooks into an S3 bucket to create a searchable index with the help of OpenSearch Serverless.
- **Monitor infrastructure health using CloudWatch** – An Amazon Bedrock action group is used to invoke Lambda functions to get CloudWatch metrics and alerts for EC2 instances from an AWS account. These specific checks are then used as Anthropic’s Claude 3 Haiku model inputs to form a health status overview of the account.

## Configure Amazon Bedrock Agents

Amazon Bedrock Agents augment the user request with the right information from Amazon Bedrock Knowledge Bases to generate an accurate response. For this use case, our knowledge base contains existing runbooks from the organization with step-by-step procedures to resolve different operational issues on AWS resources.

By configuring the appropriate [action groups](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-action-create.html) and populating the knowledge base with relevant data, you can tailor the Amazon Bedrock agent to assist with specific tasks or domains and provide accurate and helpful responses within its intended scopes.

Amazon Bedrock agents empower Anthropic’s Claude 3 Haiku to use tools, overcoming LLM limitations like knowledge cutoffs and hallucinations, for enhanced task completion through API calls and other external interactions.

The agent’s workflow is to check for resource alerts using an API, then if found, fetch and execute the relevant runbook’s steps (for example, create snapshots, restart instances, and send emails).

The overall system enables automated detection and remediation of operational issues on AWS while enforcing adherence to documented procedures through the runbook approach.

To set up this solution using Amazon Bedrock Agents, refer to the [GitHub repo](https://github.com/aws-samples/improving-it-operations-efficiency-with-aiops) that provisions the following resources. Make sure to verify the [AWS Identity and Access Management](https://aws.amazon.com/iam/) (IAM) permissions and follow [IAM best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html) while deploying the code. It is advised to apply [least-privilege permissions for IAM policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#grant-least-privilege).

- S3 bucket
- Amazon Bedrock agent
- Action group
- Amazon Bedrock agent IAM role
- Amazon Bedrock agent action group
- Lambda function
- Lambda service policy permission
- Lambda IAM role

## Benefits

With this solution, organizations can automate their operations and save a lot of time. The automation is also less prone to errors compared to manual execution. It offers the following additional benefits:

- **Reduced manual intervention** – Automating incident detection, diagnosis, and remediation helps minimize human involvement, reducing the likelihood of errors, delays, and inconsistencies that often arise from manual processes.
- **Increased operational efficiency** – By using generative AI, the solution speeds up incident resolution and optimizes operational workflows. The automation of tasks such as runbook execution, resource monitoring, and remediation allows IT teams to focus on more strategic initiatives.
- **Scalability** – As organizations grow, managing IT operations manually becomes increasingly complex. Automating operations using generative AI can scale with the business, managing more incidents, runbooks, and infrastructure without requiring proportional increases in personnel.

## Clean up

To avoid incurring unnecessary costs, it’s recommended to delete the resources created during the implementation of this solution when not in use. You can do this [by deleting the AWS CloudFormation stacks](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-delete-stack.html) deployed as part of the solution, or manually deleting the resources on the [AWS Management Console](https://aws.amazon.com/console) or using the [AWS Command Line Interface](https://aws.amazon.com/cli) (AWS CLI).

## Conclusion

The AIOps pipeline presented in this post empowers IT operations teams to streamline incident management processes, reduce manual interventions, and enhance operational efficiency. With the power of AWS services, organizations can automate incident detection, diagnosis, and remediation, enabling faster incident resolution and minimizing downtime.

Through the integration of Amazon Bedrock, Anthropic’s Claude on Amazon Bedrock, Amazon Bedrock Agents, Amazon Bedrock Knowledge Bases, and other supporting services, this solution provides real-time visibility into incidents, automated runbook generation, and dynamic remediation actions. Additionally, the solution provides timely notifications and seamless collaboration between AI agents and human operators, fostering a more proactive and efficient approach to IT operations.

Generative AI is rapidly transforming how businesses can take advantage of cloud technologies with ease. This solution using Amazon Bedrock demonstrates the immense potential of generative AI models to enhance human capabilities. By providing developers expert guidance grounded in AWS best practices, this AI assistant enables DevOps teams to review and optimize cloud architecture across of AWS accounts.

Try out the solution yourself and leave any feedback or questions in the comments.

### **About the Authors**

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/19/Upen.jpeg)****Upendra V** is a Sr. Solutions Architect at Amazon Web Services, specializing in Generative AI and cloud solutions. He helps enterprise customers design and deploy production-ready Generative AI workloads, implement Large Language Models (LLMs) and Agentic AI systems, and optimize cloud deployments. With expertise in cloud adoption and machine learning, he enables organizations to build and scale AI-driven applications efficiently.

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/19/DD-Pic-1-1.jpg)**Deepak Dixit ****is a Solutions Architect at Amazon Web Services, specializing in Generative AI and cloud solutions. He helps enterprises architect scalable AI/ML workloads, implement Large Language Models (LLMs), and optimize cloud-native applications.
