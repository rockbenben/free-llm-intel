---
vendor: aws_bedrock
title: Use Amazon SageMaker Unified Studio to build complex AI workflows using Amazon Bedrock Flows
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/use-amazon-sagemaker-unified-studio-to-build-complex-ai-workflows-using-amazon-bedrock-flows
date: 2025-07-01
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 73822f5796b1
---

# Use Amazon SageMaker Unified Studio to build complex AI workflows using Amazon Bedrock Flows

Organizations face the challenge to manage data, multiple artificial intelligence and machine learning (AI/ML) tools, and workflows across different environments, impacting productivity and governance. A unified development environment consolidates data processing, model development, and AI application deployment into a single system. This integration streamlines workflows, enhances collaboration, and accelerates AI solution development from concept to production.

The next generation of [Amazon SageMaker](https://aws.amazon.com/sagemaker/) is the center for your data, analytics, and AI. SageMaker brings together AWS AI/ML and analytics capabilities and delivers an integrated experience for analytics and AI with unified access to data. [Amazon SageMaker Unified Studio](https://aws.amazon.com/sagemaker/unified-studio/) is a single data and AI development environment where you can find and access your data and act on it using AWS analytics and AI/ML services, for SQL analytics, data processing, model development, and generative AI application development.

With SageMaker Unified Studio, you can efficiently build generative AI applications in a trusted and secure environment using [Amazon Bedrock](https://aws.amazon.com/bedrock/). You can choose from a selection of high-performing foundation models (FMs) and advanced customization and tooling such as [Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/), [Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/), [Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/), and [Amazon Bedrock Flows](https://aws.amazon.com/bedrock/flows/). You can rapidly tailor and deploy generative AI applications, and share with the built-in catalog for discovery.

In this post, we demonstrate how you can use SageMaker Unified Studio to create complex AI workflows using Amazon Bedrock Flows.

## Solution overview

Consider FinAssist Corp, a leading financial institution developing a generative AI-powered agent support application. The solution offers the following key features:

- **Complaint reference system** – An AI-powered system providing quick access to historical complaint data, enabling customer service representatives to efficiently handle customer follow-ups, support internal audits, and aid in training new staff.
- **Intelligent knowledge base** – A comprehensive data source of resolved complaints that quickly retrieves relevant complaint details, resolution actions, and outcome summaries.
- **Streamlined workflow management** – Enhanced consistency in customer communications through standardized access to past case information, supporting compliance checks and process improvement initiatives.
- **Flexible query capability** – A straightforward interface supporting various query scenarios, from customer inquiries about past resolutions to internal reviews of complaint handling procedures.

Let’s explore how SageMaker Unified Studio and Amazon Bedrock Flows, integrated with Amazon Bedrock Knowledge Bases and Amazon Bedrock Agents, address these challenges by creating an AI-powered complaint reference system. The following diagram illustrates the solution architecture.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/1_Soultion_Architecture_image-1.png)

The solution uses the following key components:

- **SageMaker Unified Studio **– Provides the development environment
- **Flow app** – Orchestrates the workflow, including:  Knowledge base queries Prompt-based classification Conditional routing Agent-based response generation

The workflow processes user queries through the following steps:

- A user submits a complaint-related question.
- The knowledge base provides relevant complaint information.
- The prompt classifies if the query is about resolution timing.
- Based on the classification using the condition, the application takes the following action:  Routes the query to an AI agent for specific resolution responses. Returns general complaint information.
- The application generates an appropriate response for the user.

## Prerequisites

For this example, you need the following:

- [Access to SageMaker Unified Studio](https://docs.aws.amazon.com/sagemaker-unified-studio/latest/userguide/getting-started-access-the-portal.html). (You will need the SageMaker Unified Studio portal URL from your administrator). You can authenticate using either:  [AWS Identity and Access Management](https://aws.amazon.com/iam/) (IAM) user credentials. Single sign-on (SSO) credentials with [AWS IAM Identity Center](https://aws.amazon.com/iam/identity-center/).
- The IAM user or IAM Identity Center user must have appropriate permissions for:  SageMaker Unified Studio.  Amazon Bedrock (including Amazon Bedrock Flows, Amazon Bedrock Agents, Amazon Bedrock Prompt Management, and Amazon Bedrock Knowledge Bases). For more information, refer to [Identity-based policy examples](https://docs.aws.amazon.com/sagemaker-unified-studio/latest/adminguide/security_iam_id-based-policy-examples.html).
- [Access to Amazon Bedrock FMs](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html) (make sure these are enabled for your account), for example:Anthropic’s Claude 3 Haiku (for the agent).
- [Configure access](https://docs.aws.amazon.com/sagemaker-unified-studio/latest/adminguide/amazon-bedrock.html#manage-models) to your Amazon Bedrock serverless models for Amazon Bedrock in SageMaker Unified Studio projects.
- Amazon Titan Embedding (for the knowledge base).
- Sample complaint data prepared in CSV format for creating the knowledge base.

## Prepare your data

We have created a sample dataset to use for Amazon Bedrock Knowledge Bases. This dataset has information of complaints received by customer service representatives and resolution information.The following is an example from the sample dataset:

```
complaint_id,product,sub_product,issue,sub_issue,complaint_summary,action_taken,next_steps,financial_institution,state,submitted_via,resolution_type,timely_response
FIN-2024-001,04/26/24,"Mortgage","Conventional mortgage","Payment issue","Escrow dispute","Customer disputes mortgage payment increase after recent escrow analysis","Reviewed escrow analysis, explained property tax increase impact, provided detailed payment breakdown","1. Send written explanation of escrow analysis 2. Schedule annual escrow review 3. Provide payment assistance options","Financial Institution-1","TX","Web","Closed with explanation","Yes"
FIN-2024-002,04/26/24,"Money transfer","Wire transfer","Processing delay","International transfer","Wire transfer of $10,000 delayed, customer concerned about international payment deadline","Located wire transfer in system, expedited processing, waived wire fee","1. Confirm receipt with receiving bank 2. Update customer on delivery 3. Document process improvement needs","Financial Institution-2","FL","Phone","Closed with monetary relief","No"
```

## Create a project

In SageMaker Unified Studio, users can use projects to collaborate on various business use cases. Within projects, you can manage data assets in the SageMaker Unified Studio catalog, perform data analysis, organize workflows, develop ML models, build generative AI applications, and more.

To create a project, complete the following steps:

- Open the SageMaker Unified Studio landing page using the URL from your admin.
- Choose **Create project**.
- Enter a project name and optional description.
- For **Project profile**, choose **Generative AI application development**.
- Choose **Continue**.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/2_Create_Project_image-2.png)

- Complete your project configuration, then choose **Create project**.

## Create a prompt

Let’s create a reusable prompt to capture the instructions for FMs, which we will use later while creating the flow application. For more information, see [Reuse and share Amazon Bedrock prompts](https://docs.aws.amazon.com/sagemaker-unified-studio/latest/userguide/prompt-mgmt.html).

- In SageMaker Unified Studio, on the **Build** menu, choose **Prompt** under **Machine Learning & Generative AI**.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/3_Prompt_image-3.png)

- Provide a name for the prompt.
- Choose the appropriate FM (for this example, we choose **Claude 3 Haiku**).
- For **Prompt message**, we enter the following:

```
You are a complaint analysis classifier. You will receive complaint data from a knowledge base. Analyze the {{input}} and respond with a single letter:
T: If the input contains information about complaint resolution timing, response time, or processing timeline (whether timely or delayed)
F: For all other types of complaint information
Return only 'T' or 'F' based on whether the knowledge base response is about resolution timing. Do not add any additional text or explanation - respond with just the single letter 'T' or 'F'.
```

- Choose **Save**.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/4_Create_Version_image-4.png)

- Choose **Create version**.

## Create a chat agent

Let’s create a chat agent to handle specific resolution responses. Complete the following steps:

- In SageMaker Unified Studio, on the **Build** menu, choose **Chat agent** under **Machine Learning & Generative AI**.
- Provide a name for the prompt.
- Choose the appropriate FM (for this example, we choose **Claude 3 Haiku**).
- For **Enter a system prompt**, we enter the following:

```
You are a Financial Complaints Assistant AI. You will receive complaint information from a knowledge base and questions about resolution timing.
When responding to resolution timing queries:
1. Use the provided complaint information to confirm if it was resolved within timeline
2. For timely resolutions, provide:
   - Confirmation of timely completion
   - Specific actions taken (from the provided complaint data)
   - Next steps that were completed
2. For delayed resolutions, provide:
   - Acknowledgment of delay
   - Standard compensation package:
     • $75 service credit
     • Priority Status upgrade for 6 months
     • Service fees waived for current billing cycle
   - Actions taken (from the provided complaint data)
   - Contact information for follow-up: Priority Line: ************** 
Always reference the specific complaint details provided in your input when discussing actions taken and resolution process.
```

- Choose **Save**.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/5_Chat_Agent_image-5.png)

- After the agent is saved, choose **Deploy**.
- For **Alias name**, enter `demoAlias`.
- Choose **Deploy**.

## Create a flow

Now that we have our prompt and agent ready, let’s create a flow that will orchestrate the complaint handling process:

- In SageMaker Unified Studio, on the **Build** menu, choose **Flow** under **Machine Learning & Generative AI**.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/6_flow_image-6.jpeg)

- Create a new flow called demo-flow.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/7_new_flow_image-7.png)

### Add a knowledge base to your flow application

Complete the following steps to add a knowledge base node to the flow:

- In the navigation pane, on the **Nodes **tab, choose **Knowledge Base**.
- On the **Configure** tab, provide the following information:  For **Node name**, enter a name (for example, `complaints_kb`). Choose **Create new Knowledge Base**.
- In the **Create Knowledge Base **pane, enter the following information:  For **Name**, enter a name (for example, `complaints`). For **Description**, enter a description (for example, `user complaints information`). For **Add data sources**, select **Local file** and upload the complaints.txt file. For **Embeddings model**, choose **Titan Text Embeddings V2**. For **Vector store**, choose **OpenSearch Serverless**. Choose **Create**.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/8_Knowledge_base_image-8.png)

- After you create the knowledge base, choose it in the flow.
- In the details name, provide the following information:
- For **Response generation model**, choose **Claude 3 Haiku**.
- Connect the output of the flow input node with the input of the knowledge base node.
- Connect the output of the knowledge base node with the input of the flow output node.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/9_first_connection_image-9.png)

- Choose **Save**.

### Add a prompt to your flow application

Now let’s add the prompt you created earlier to the flow:

- On the **Nodes** tab in the** Flow app builder** pane, add a prompt node.
- On the **Configure** tab for the prompt node, provide the following information:
- For **Node name**, enter a name (for example, `demo_prompt`).
- For **Prompt**, choose `financeAssistantPrompt`.
- For **Version**, choose **1**.
- Connect the output of the knowledge base node with the input of the prompt node.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/10_KB_Prompt_connection_image-10.png)
- Choose **Save**.

### Add a condition to your flow application

The condition node determines how the flow handles different types of queries. It evaluates whether a query is about resolution timing or general complaint information, enabling the flow to route the query appropriately. When a query is about resolution timing, it will be directed to the chat agent for specialized handling; otherwise, it will receive a direct response from the knowledge base. Complete the following steps to add a condition:

- On the **Nodes** tab in the **Flow app builder** pane, add a condition node.
- On the **Configure** tab for the condition node, provide the following information:  For **Node name**, enter a name (for example, `demo_condition`). Under **Conditions**, for **Condition**, enter `conditionInput == "T"`. Connect the output of the prompt node with the input of the condition node.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/11_condition_connection_image-11.png)
- Choose **Save**.

### Add a chat agent to your flow application

Now let’s add the chat agent you created earlier to the flow:

- On the **Nodes** tab in the** Flow app builder** pane, add the agent node.
- On the **Configure** tab for the agent node, provide the following information:  For **Node name**, enter a name (for example, `demo_agent`). For **Chat agent**, choose `DemoAgent`. For **Alias**, choose `demoAlias`.
- Create the following node connections:  Connect the input of the condition node (`demo_condition`) to the output of the prompt node (`demo_prompt`). Connect the output of the condition node:  Set **If condition is true** to the agent node (`demo_agent`). Set **If condition is false** to the existing flow output node (`FlowOutputNode`).  Connect the output of the knowledge base node (`complaints_kb`) to the input of the following:  The agent node (`demo_agent`). The flow output node (`FlowOutputNode`).  Connect the output of the agent node (`demo_agent`) to a new flow output node named `FlowOutputNode_2`.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/12_agent_connection_image-12.png)
- Choose **Save**.

## Test the flow application

Now that the flow application is ready, let’s test it. On the right side of the page, choose the expand icon to open the **Test** pane.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/13_fina_connection_image-13.png)

In the **Enter prompt** text box, we can ask a few questions related to the dataset created earlier. The following screenshots show some examples.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/14_question_image-14.png)

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/15_answer_image-15.png)

## Clean up

To clean up your resources, delete the flow, agent, prompt, knowledge base, and associated OpenSearch Serverless resources.

## Conclusion

In this post, we demonstrated how to build an AI-powered complaint reference system using a flow application in SageMaker Unified Studio. By using the integrated capabilities of SageMaker Unified Studio with Amazon Bedrock features like Amazon Bedrock Knowledge Bases, Amazon Bedrock Agents, and Amazon Bedrock Flows, you can rapidly develop and deploy sophisticated AI applications without extensive coding.

As you build AI workflows using SageMaker Unified Studio, remember to adhere to the AWS [Shared Responsibility Model](https://aws.amazon.com/compliance/shared-responsibility-model/) for security. Implement SageMaker Unified Studio [security](https://docs.aws.amazon.com/sagemaker-unified-studio/latest/adminguide/security.html) best practices, including proper IAM configurations and data encryption. You can also refer to [Secure a generative AI assistant with OWASP Top 10 mitigation](https://aws.amazon.com/blogs/machine-learning/secure-a-generative-ai-assistant-with-owasp-top-10-mitigation/) for details on how to assess the security posture of a generative AI assistant using OWASP TOP 10 mitigations for common threats. Following these guidelines helps establish robust AI applications that maintain data integrity and system protection.

To learn more, refer to [Amazon Bedrock in SageMaker Unified Studio](https://docs.aws.amazon.com/sagemaker-unified-studio/latest/userguide/bedrock.html) and join discussions and share your experiences in [AWS Generative AI Community](https://community.aws/generative-ai?trk=4a84f0b4-a654-4729-9e51-6d6dc54134f2&sc_channel=el).

We look forward to seeing the innovative solutions you will create with these powerful new features.

### About the authors

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/sumeettr-100x133.jpg)**Sumeet Tripathi** is an Enterprise Support Lead (TAM) at AWS in North Carolina. He has over 17 years of experience in technology across various roles. He is passionate about helping customers to reduce operational challenges and friction. His focus area is AI/ML and Energy & Utilities Segment. Outside work, He enjoys traveling with family, watching cricket and movies.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/18/Vsnak-100x133.jpg)**Vishal Naik** is a Sr. Solutions Architect at Amazon Web Services (AWS). He is a builder who enjoys helping customers accomplish their business needs and solve complex challenges with AWS solutions and best practices. His core area of focus includes Generative AI and Machine Learning. In his spare time, Vishal loves making short films on time travel and alternate universe themes.
