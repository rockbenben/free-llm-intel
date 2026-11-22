---
vendor: aws_bedrock
title: Innovate business logic by implementing return of control in Amazon Bedrock Agents
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/innovate-business-logic-by-implementing-return-of-control-in-amazon-bedrock-agents
date: 2025-06-16
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: b781b74acc1b
---

# Innovate business logic by implementing return of control in Amazon Bedrock Agents

In the context of distributed systems and microservices architecture, orchestrating communication between diverse components presents significant challenges. However, with the launch of [Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/), the landscape is evolving, offering a simplified approach to agent creation and seamless integration of the return of control capability. In this post, we explore how Amazon Bedrock Agents revolutionizes agent creation and demonstrates the efficacy of the [return of control](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-returncontrol.html) capability in orchestrating complex interactions between multiple systems.

Amazon Bedrock Agents simplifies the creation, deployment, and management of agents in distributed systems. By using the power of [AWS Lambda](https://aws.amazon.com/lambda/) and [AWS Step Functions](https://aws.amazon.com/step-functions/), Amazon Bedrock Agents abstracts away the complexities of agent implementation, which means developers can focus on building robust and scalable applications without worrying about infrastructure management.

You can use agents in Amazon Bedrock in various scenarios where you need to handle the return of control to the user or the system. Use cases include conversational assistants, task automation, decision support systems, interactive tutorials and walkthroughs, and virtual assistants. In these use cases, the key aspect of the agents is their ability to handle the return of control to the user or the system. This allows for a more natural and responsive interaction, where the user feels in control of the process while still benefiting from the agent’s guidance and automation capabilities.

## Solution overview

In this post, we demonstrate an automated personalized investment portfolio solution using Amazon Bedrock Agents. The solution calls a third-party API to fetch a user’s current investment portfolio. These are then analyzed using [foundation models](https://aws.amazon.com/what-is/foundation-models/) (FMs) available on Amazon Bedrock to produce recommendations inline to the inputs provided by the end user, showcasing a return of control capability integrated with Amazon Bedrock Agents.

This solution uses a combination of synchronous data retrieval and [generative AI](https://aws.amazon.com/generative-ai/) to provide tailored investment recommendations that align with users’ specific financial goals and risk tolerance. By incorporating [machine learning](https://aws.amazon.com/ai/machine-learning/) (ML) and simulation techniques, the system can generate personalized portfolios and assess their potential performance, making sure the recommended solutions are optimized for individual needs.

With Amazon Bedrock Agents, the capability to return control to the application invoking the agent can handle external functions and business logic at the application level instead of using a Lambda function. This way, an application can manage external interactions and return the response while the agent continues its orchestration. This is illustrated in the following diagram.

[![Illustration Diagram](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/arch.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/arch.png)

The option to return control is particularly useful in two main scenarios:

- Calling an API from an existing application rather than building a new Lambda function with the required authentication and networking configurations
- Handling tasks that might run longer than 15 minutes and can’t be accommodated through a Lambda function, instead requiring containers, virtual servers, or workflow orchestration tools such as AWS Step Functions

The following sample code uses Amazon Bedrock Agents with handling return of control in the code. With the Amazon Bedrock Agents feature, you can manage Amazon Bedrock Agents return of control in your backend services and simplify application integrations. To demonstrate this, we have the following four code snippets: `external-bedrock-agent-api.py`, `streamlit-app-portfolio-recommender.py`, `Portfolio-Recommender-CFN-Template.yaml`, and `requirements.txt`, along with detailed steps to replicate the scenario.

The [external-bedrock-agent-api](https://aws-blogs-artifacts-public.s3.us-east-1.amazonaws.com/ML-16807/external-bedrock-agent-api.py) code implements a portfolio recommendation system using Amazon Bedrock Agents and [Flask](https://pypi.org/project/Flask/). Here’s a high-level overview of the functions used:

- **fetch_user_data**: Processes user profile information such as risk tolerance or investment goals
- **generate_portfolios**: Creates sample investment portfolios with different risk levels
- **fetch_custom_portfolio**: Combines user data and portfolio generation
- **send_custom_portfolio_as_email**: Sends portfolio recommendations by email using an [Amazon Simple Email Service](https://aws.amazon.com/ses/) (Amazon SES) verified email identity
- **/sns-handler endpoint**: This API endpoint receives POST requests with user investment preferences, processes the message containing user preference details, invokes the Amazon Bedrock agent to generate recommendations, and handles email communication of the recommendations

The [streamlit-app-portfolio-recommender](https://aws-blogs-artifacts-public.s3.us-east-1.amazonaws.com/ML-16807/streamlit-app-portfolio-recommender.py) code is a [Streamlit](https://pypi.org/project/streamlit/) web application for investment portfolio recommendations. The code sets up the webpage with a title and configuration. The app collects several pieces of information through form elements:

- **Email address** – Text input
- **Financial goal** – Dropdown with options for retirement, wealth accumulation, and passive income
- **Risk tolerance** – Dropdown with options for low, medium, and high
- **Investment horizon** – Dropdown with options for short-term and long-term
- **Environmental, social, and governance (ESG) preference** – Checkbox for environmental, social, and governance preferences
- **Email preference** – Checkbox for receiving recommendations by email

The system operates through a Portfolio Generation Function that actively sending POST requests to a local API endpoint. This function transforms user preferences into JSON data and delivers either an API response or error message back to the user.

The process to display results begins when user click the Submit button, which triggers the `custom_portfolio` function with their specific inputs. The system then displays the portfolio recommendation in a text area for successful executions, while immediately alerting users with an error message if any issues occur during the process.

## Solution walkthrough

Follow the steps to set up the environment and test the application in the US East (N. Virginia) us-east-1 [Region](https://docs.aws.amazon.com/glossary/latest/reference/glos-chap.html#region).

To enable Anthropic’s Claude model on Amazon Bedrock in your AWS account:

- On the Amazon Bedrock console, in the left navigation pane under **Amazon Bedrock configurations**, select **Model access**
- Select **Claude 3 Sonnet**, as shown in the following screenshot

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot123.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot123.png)

- To create the Amazon Bedrock agents, related action groups, [Amazon SageMaker AI](https://aws.amazon.com/sagemaker-ai/) domain, sample user profile, and JupyterLab space, follow these steps:

- Invoke the [AWS CloudFormation](https://aws.amazon.com/cloudformation/) template at [Portfolio-Recommender-CloudFormation-Template.yml](https://aws-blogs-artifacts-public.s3.us-east-1.amazonaws.com/ML-16807/Portfolio-Recommender-CloudFormation-Template.yml) Give a name to the stack Provide an email address for the `EmailIdentityParameter`

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot223.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot223.png)

- Select the checkbox to acknowledge that the template contains [AWS Identity and Access Management](https://aws.amazon.com/iam/) (IAM) resources, as shown in the following screenshot

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot323.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot323.png)

- Monitor AWS CloudFormation until it completes the resource creation process. You can verify the successful deployment by checking the Stack details output tab, which will display the `AgentId` and `AgentAliasId` values, as shown in the screenshot below.

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot423.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot423.png)

You will receive an email address verification request email from AWS for in the US East (N. Virginia) Region. Select the link in the email to verify.

After creating your CloudFormation resources, follow these steps to access Amazon SageMaker Studio:

- On the Amazon SageMaker AI console, under **Admin configurations** in the left navigation pane, select **Domains**
- Select the **bedrock-return-of-control-demo** domain created by the CloudFormation template, as shown in the following screenshot

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot523.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot523.png)

- Select the **User profiles** tab
- To open the SageMaker Studio environment, under **User profiles**, next to the **sagemakeruser** profile on the right, select **Launch**. From the dropdown menu, choose **Studio**, as shown in the following screenshot

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot623.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot623.png)

You should now observe the SageMaker Studio home page. This environment is where you will execute Python scripts to set up your application.

To access the JupyterLab environment for this lab, follow these steps:

- On the SageMaker Studio console, in the left navigation pane under **Applications**, select **JupyterLab**
- You’ll find bedrock-agent-space that has been preprovisioned for this lab. Its **Status** should be **Stopped**. On the right side under **Action**, choose **Run**
- Within 30–40 seconds, the JupyterLab application status will change from **Starting** to **Running**

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot723.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot723.png)

- When it’s running, under **Action**, choose **Open**, as shown in the following screenshot

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot823.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot823.png)

Three required files are copied under the `/home/sagemaker-user/scripts` directory: two Python files ([external-bedrock-agent-api](https://aws-blogs-artifacts-public.s3.us-east-1.amazonaws.com/ML-16807/external-bedrock-agent-api.py) and [streamlit-app-portfolio-recommender](https://aws-blogs-artifacts-public.s3.us-east-1.amazonaws.com/ML-16807/streamlit-app-portfolio-recommender.py)) and one [requirements.txt](https://aws-blogs-artifacts-public.s3.us-east-1.amazonaws.com/ML-16807/requirements.txt) file, as shown in the following screenshot. The JupyterLab application environment is under the default directory.

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot923.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot923.png)

- In the **File** menu, select **New**. In the dropdown menu, select **Terminal** to open a new terminal window, as shown in the following screenshot.
[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot1023.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot1023.png)
- Go to the scripts directory where you have the required files in the terminal and enter:  `pip install -r requirements.txt`
- Enter the following command on the terminal:  `python3 external-bedrock-agent-api.py`
- Open a new terminal and go to the `/home/sagemaker-user/scripts` directory and enter:  `streamlit run streamlit-app-portfolio-recommender.py`
- From the command execution in the terminal, note the port number (8501) and studio URL from the browser. The URL will be in the format of: `https://{domainid}.studio.{region}-1.sagemaker.aws/jupyterlab/default/lab/tree/scripts`
- To access the Streamlit app, modify the Studio URL, replacing everything after the default/ lab/tree/scripts with proxy/[PORT NUMBER]/. The modified Streamlit UI URL will look like this: `https://{domainid}.studio.{region}.sagemaker.aws/jupyterlab/default/proxy/8501/`
- Select all appropriate inputs for generating your custom portfolio recommendation. Choose whether you prefer to receive email notifications or inline recommendations through the application interface by checking the corresponding box. Then choose **Submit**. Provide the same email address that was verified earlier in this walkthrough.

The sample output and email response are shown in the following demo screenshot.
[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/04/TrimFullv4.gif)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/04/TrimFullv4.gif)

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot1223.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot1223.png)

## Cleanup

When you’re done, delete resources you no longer need to avoid ongoing costs. Follow these steps:

- Go to the SageMaker AI JupyterLab environment and [stop the Amazon SageMaker Studio application or running instance](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-updated-running-stop.html)
- Delete the resources created by deleting the CloudFormation stack.

The following screenshot demonstrates how to view and stop running instances in the SageMaker AI JupyterLab environment. For more information, refer to [Delete a stack from the CloudFormation console](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-console-delete-stack.html).

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot1323.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/shot1323.png)

## Amazon Bedrock Agents return of control considerations

When implementing return of control, consider the following:

- **Return of control performance considerations** – When implementing return of control, developers should focus on optimizing action execution times and response handling. Each action should be designed to complete within reasonable timeframes to maintain conversation flow. Consider implementing caching mechanisms for frequently accessed data and facilitate efficient state management between return of control cycles. The application should be designed to handle concurrent user sessions effectively while maintaining responsiveness.
- **Return of control limitations** – Actions must be defined with clear input and output schemas. Each action should be atomic and focused on a specific task to maintain simplicity and reliability. Consider payload sizes for requests and responses because there might be size limitations. Actions execute sequentially, and the system needs to maintain conversation context throughout the interaction cycle.
- **Security recommendations** – Security implementation requires proper authentication and authorization mechanisms for all actions, following the principle of least privilege when defining permissions. Input parameters must be validated before processing, with comprehensive error handling in place. Rate limiting and request validation should be implemented to prevent abuse, and sensitive data handling must comply with security requirements and include proper logging mechanisms for audit trails. Additionally, implement input filtering to prevent prompt injection attacks, configure response filters to protect sensitive information, and set up content scanning for both input and output. Deploy regex-based response filtering to help prevent personally identifiable information (PII) exposure and establish content moderation filters to block inappropriate content.
- **Monitoring and observability** – Implement comprehensive logging for all action executions and responses. Monitor key metrics such as action execution times, success rates, and error rates. Set up alerts for abnormal patterns or failures. Use [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/) for monitoring system health and performance. Consider implementing tracing to track request flow through different components of your system. Regular review of metrics and logs helps identify potential issues and optimization opportunities.

## Conclusion

In this post, we’ve demonstrated how Amazon Bedrock Agents simplifies agent creation and streamlines the orchestration of complex interactions between microservices using the return of control capability. By abstracting away infrastructure management and providing seamless integration with your application, Amazon Bedrock Agents empowers developers to build resilient and scalable applications with ease. As organizations embrace microservices architecture and distributed systems, tools such as Amazon Bedrock Agents play a pivotal role in accelerating innovation and driving digital transformation.

## Resources

For the most current and specific information, refer to:

- [Amazon Bedrock documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [AWS Well-Architected Framework best practices](https://docs.aws.amazon.com/wellarchitected/latest/framework/appendix.html)
- [AWS Security best practices](https://aws.amazon.com/architecture/security-identity-compliance/)
- [AWS observability best practices](https://docs.aws.amazon.com/wellarchitected/latest/management-and-governance-guide/observability.html)

### About the Authors

**
[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/28/vh2-1.jpg)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/vh2.jpg)Vishwanatha Handadi** is a Sr. Solutions Architect within the Global Financial Services vertical, working with Amazon Web Services (AWS) for over 2 years and has over 22 years of experience in the IT industry primarily in data and analytics. At AWS, he drives customers through their cloud transformation journeys by converting complex challenges into actionable roadmaps for both technical and business audiences. He is based out of Bangalore, India.

**
[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/28/ab-1-1.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/24/ab-1.png)Mohammed Asadulla Baig** is a Sr. Technical Account Manager with Amazon Web Services (AWS) Enterprise Support. Asad helps customers architect scalable, resilient, and secure solutions. With a keen eye for innovation and a passion for delivering customer success, Asad has established himself as a thought leader in the industry, helping enterprises navigate their cloud transformation journeys with confidence and ease.
