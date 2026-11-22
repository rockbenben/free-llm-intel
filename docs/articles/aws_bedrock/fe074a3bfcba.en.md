---
vendor: aws_bedrock
title: Detect and redact personally identifiable information using Amazon Bedrock Data Automation and Guardrails
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/detect-and-redact-personally-identifiable-information-using-amazon-bedrock-data-automation-and-guardrails
date: 2026-01-08
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 74de596e1242
---

# Detect and redact personally identifiable information using Amazon Bedrock Data Automation and Guardrails

Organizations handle vast amounts of sensitive customer information through various communication channels. Protecting Personally Identifiable Information (PII), such as social security numbers (SSNs), driver’s license numbers, and phone numbers has become increasingly critical for maintaining compliance with data privacy regulations and building customer trust. However, manually reviewing and redacting PII is time-consuming, error-prone, and scales poorly as data volumes grow.

Organizations face challenges when dealing with PII scattered across different content types – from texts to images. Traditional approaches often require separate tools and workflows for handling text and image content, leading to inconsistent redaction practices and potential security gaps. This fragmented approach not only increases operational overhead but also raises the risk of accidental PII exposure.

This post shows an automated PII detection and redaction solution using [Amazon Bedrock Data Automation](https://aws.amazon.com/bedrock/bda/) and [Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/) through a use case of processing text and image content in high volumes of incoming emails and attachments. The solution features a complete email processing workflow with a React-based user interface for authorized personnel to more securely manage and review redacted email communications and attachments. We walk through the step-by-step solution implementation procedures used to deploy this solution. Finally, we discuss the solution benefits, including operational efficiency, scalability, security and compliance, and adaptability.

## Solution overview

The solution provides an automated system for protecting sensitive information in business communications through three main capabilities:

- **Automated PII detection and redaction** for both email content and attachments using Amazon Bedrock Data Automation and Guardrails, making sure that sensitive data is consistently protected across different content types.
- **More secure data management workflows** where processed communications are encrypted and stored with appropriate access controls, while maintaining a complete audit trail of operations.
- **Web-based interface options** for authorized agents to efficiently manage redacted communications, supported by features like automated email categorization and customizable folder management.

This unified approach helps organizations maintain compliance with data privacy requirements while streamlining their communication workflows.

The following diagram outlines the solution architecture. ![Solution architecture for PII detection and redaction using Amazon Bedrock](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/23/ML-184361.png)

The diagram illustrates the backend PII detection and redaction workflow and the frontend application user interface orchestrated by [AWS Lambda](https://aws.amazon.com/lambda/) and [Amazon EventBridge](https://aws.amazon.com/eventbridge/). The process follows these steps:

- The workflow starts with the user sending an email to the incoming email server hosted on [Amazon Simple Email Service (Amazon SES)](https://aws.amazon.com/ses/). This is an optional step.
- Alternatively, users can upload the emails and attachments directly into an [Amazon Simple Storage Service (S3)](https://aws.amazon.com/s3/) landing bucket.
- An S3 event notification triggers the initial processing AWS Lambda function that generates a unique case ID and creates a tracking record in [Amazon DynamoDB](https://aws.amazon.com/dynamodb/).
- Lambda orchestrates the PII detection and redaction workflow by extracting email body and attachments from the email and saving it in a raw email bucket followed by invoking Amazon Bedrock Data Automation and Guardrails for detecting and redacting PII.
- Amazon Bedrock Data Automation processes attachments to extract text from the files.
- Amazon Bedrock Guardrails detects and redacts the PII from both email body and text from attachments and stores the redacted content in another S3 bucket.
- DynamoDB tables are updated with email messages, folders metadata, and email filtering rules.
- An Amazon EventBridge Scheduler is used to run the Rules Engine Lambda on a schedule which processes new emails that have yet to be categorized into folders based on enabled email filtering rules criteria.
- The Rules Engine Lambda also communicates with DynamoDB to access the messages table and the rules table.
- Users can access the optional application user interface through [Amazon API Gateway](https://aws.amazon.com/api-gateway/), which manages user API requests and routes requests to render the user interface through S3 static hosting. Users may choose to enable authentication for the user interface based on their security requirements. Alternatively, users can check the status of their email processing in the DynamoDB table and S3 bucket with PII redacted content.
- A Portal API Lambda fetches the case details based on user requests.
- The static assets served by API Gateway are stored in a private S3 bucket.
- Optionally, users may enable [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/) and [AWS CloudTrail](https://aws.amazon.com/cloudtrail/) to provide visibility into the PII detection and redaction process, while using [Amazon Simple Notification Service](https://aws.amazon.com/sns/) to deliver real-time alerts for any failures, facilitating immediate attention to issues.

In the following sections, we walk through the procedures for implementing this solution.

## Walkthrough

The solution implementation involves infrastructure and optional portal setup.

### **Prerequisites**

Before beginning the implementation, make sure to have the following components installed and configured.

- An [AWS account](https://signin.aws.amazon.com/signup?request_type=builderId)
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Python 3.7](https://www.python.org/downloads/release/python-370/) or higher
- [Node v18](https://nodejs.org/en/blog/release/v18.12.0) or higher
- [NPM v9.8](https://www.npmjs.com/package/npm/v/9.8.0) or higher
- [AWS CDK v2.166](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html) or higher
- Terminal/CLI such as macOS Terminal, PowerShell or Windows Terminal, or the Linux command line. [AWS CloudShell](https://aws.amazon.com/cloudshell/) can also be used when all code is located within an AWS account

### Infrastructure setup and deployment process

Verify that an existing [virtual private cloud VPC](https://docs.aws.amazon.com/vpc/latest/userguide/create-vpc.html) that contains three private subnets with no internet access is created in your AWS account. All [AWS CloudFormation](https://aws.amazon.com/cloudformation/) stacks need to be deployed within the same AWS account.

#### CloudFormation stacks

The solution contains three stacks (two required, one optional) that deploys in your AWS account:

- **S3Stack** – Provisions the core infrastructure including S3 buckets for raw and redacted email storage with automatic lifecycle policies, a DynamoDB table for email metadata tracking with time-to-live (TTL) and global secondary indexes, and VPC security groups for more secure Lambda function access. It also creates [Amazon Identity and Access Management (IAM)](https://aws.amazon.com/iam/) roles with comprehensive permissions for S3, DynamoDB, and Bedrock services, forming a more secure foundation for the entire PII detection and redaction workflow.
- **ConsumerStack **– Provisions the core processing infrastructure including Amazon Bedrock Data Automation projects for document text extraction and Bedrock Guardrails configured to anonymize comprehensive PII entities, along with Lambda functions for email and attachment processing with [Amazon Simple Notification Service (SNS)](https://aws.amazon.com/sns/) topics for success/failure notifications. It also creates [Amazon Simple Email Service (SES)](https://aws.amazon.com/ses/) receipt rules for incoming email handling when a domain is configured and S3 event notifications to trigger the email processing workflow automatically.
- **PortalStack (optional)** – This is only needed when users want to use a web-based user interface for managing emails. It provisions the optional web interface including a regional API Gateway, DynamoDB tables for redacted message storage, and S3 buckets for static web assets.

#### Amazon SES (optional)

Move directly to the Solution Deployment section that follows if Amazon SES is not being used.

The following Amazon SES Setup is optional. The code may be tested without this setup as well. Steps to test the application with or without Amazon SES is covered in the Testing section.

Set up Amazon SES with prod access and verify the domain/email identities for which the solution is to work. We also need to add the MX records in the DNS provider maintaining the domain. Please refer to the following links:

- [Request SES Production Access](https://docs.aws.amazon.com/ses/latest/dg/request-production-access.html)
- [Setting up Amazon SES email receiving](https://docs.aws.amazon.com/ses/latest/dg/receiving-email-setting-up.html)

Create credentials for SMTP and save it in [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/) secret with name SmtpCredentials. An IAM user is created for this process.

If any other name is being used for the secret, update the `context.json` line `secret_name` with the name of the secret created.

The key for the username in the secret should be `smtp_username` and the key for password should be `smtp_password` when storing the same in AWS Secrets Manager.

- [Obtaining Amazon SES SMTP credentials](https://docs.aws.amazon.com/ses/latest/dg/smtp-credentials.html)

### Solution deployment

Run the following commands from within a terminal/CLI environment.

- Clone the repository  `git clone https://github.com/aws-samples/sample-bda-redaction.git`
- The `infra/cdk.json` file tells the CDK Toolkit how to execute your app  `cd sample-bda-redaction/infra/`
- **Optional:** Create and activate a new Python virtual environment (make sure to use python 3.12 as lambda is in CDK is configured for same. If using some other python version update CDK code to reflect the same in lambda runtime)  `python3 -m venv .venv . .venv/bin/activate`
- Upgrade pip  `pip install --upgrade pip`
- Install Python packages  `pip install -r requirements.txt`
- Create `context.json` file  `cp context.json.example context.json`
- Update the `context.json` file with the correct configuration options for the environment.

| **Property Name** | **Default** | **Description** | **When to Create** |
| --- | --- | --- | --- |
| `vpc_id` | “” | VPC ID where resources are deployed | VPC needs to be created prior to execution |
| `raw_bucket` | “” | S3 bucket storing raw messages and attachments | Created during CDK deployment |
| `redacted_bucket_name` | “” | S3 bucket storing redacted messages and attachments | Created during CDK deployment |
| `inventory_table_name` | “” | DynamoDB table name storing redacted message details | Created during CDK deployment |
| `resource_name_prefix` | “” | Prefix used when naming resources during the stack creation | During stack creation |
| `retention` | 90 | Number of days for retention of the messages in the redacted and raw S3 buckets | During stack creation |

- The following properties are only required when the portal is being provisioned.

| **Property Name** | **Default** | **Description** |
| --- | --- | --- |
| `environment` | development | The type of environment where resources are provisioned. Values are development or production |

- Use cases that require the usage of Amazon SES to manage redacted email messages need to set the following configuration variables. Otherwise, these are optional.

| **Property Name** | **Description** | **Comment** |
| --- | --- | --- |
| `domain` | The verified domain or email name that is used for Amazon SES | This can be left blank if not setting up Amazon SES |
| `auto_reply_from_email` | Email address of the “from” field of the email message. Also used as the email address where emails are forwarded from the Portal application | This can be left blank if not setting up the Portal |
| `secret_name` | AWS Secrets Manager secret containing SMTP credentials for forward email functionality from the portal |  |

- Deploy Infrastructure by running the following commands from the root of the infra directory.  Bootstrap the AWS account to use AWS CDK  `cdk bootstrap`  Users can now synthesize the CloudFormation template for this code. Additional environment variables before the cdk synth suppresses the warnings. The deployment process should take approximately 10 min for a first-time deployment to complete.  `JSII_DEPRECATED=quiet JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=quiet cdk synth --no-notices`  Replace `<<resource_name_prefix>>` with its chosen value and then run:  `JSII_DEPRECATED=quiet JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=quiet cdk deploy <<resource_name_prefix>>-S3Stack <<resource_name_prefix>>-ConsumerStack --no-notices`

### Testing

- **Testing the application with Amazon SES **

Before starting the test, make sure the Amazon SES Email Receiving rule set that was created by the `<<resource_name_prefix>>-ConsumerStack` stack is active. We can check by executing the below command and make sure name in the output is `<<resource_name_prefix>>-rule-setaws ses describe-active-receipt-rule-set`. If the name does not match or the output is blank, execute the following to activate the same:

```
# Replace <<resource_name_prefix>> with resource_name_prefix used in context.json

aws ses set-active-receipt-rule-set --rule-set-name <<resource_name_prefix>>-rule-set
```

Once we have the correct rule set active, we can test the application using Amazon SES by sending an email to the verified email or domain in Amazon SES, which automatically triggers the redaction pipeline. Progress can be tracked in the DynamoDB table `<<inventory_table_name>>`. The inventory table name can be found on the resources tab in the AWS CloudFormation Console for the `<<resource_name_prefix>>-S3Stack` stack and Logical ID `EmailInventoryTable`. A unique `<<case_id>>` is generated and used in the DynamoDB inventory table for each email being processed. Once redaction is complete, the redacted email body can be found in `<<redacted_bucket_name>>/redacted/<<today_date>>/<<case_id>>/email_body/` and redacted attachments in `<<redacted_bucket_name>>/redacted/<<today_date>>/<<case_id>>/attachments/`.

- **Testing the application without Amazon SES**

As described earlier, the solution is used to redact any PII data in the email body and attachments. Therefore, to test the application, we need to provide an email file which needs to be redacted. We can do that without Amazon SES by directly uploading an email file to the raw S3 bucket. The raw bucket name can be found on the output tab in the AWS CloudFormation Console for `<<resource_name_prefix>>-S3Stack` stack and Export Name `RawBucket`. This triggers the workflow of redacting the email body and attachments by S3 event notification triggering the Lambda. For your convenience, a sample email is available in the `infra/pii_redaction/sample_email` directory of the repository. Below are the steps to test the application without Amazon SES using the same email file.

```
# Replace <<raw_bucket>> with raw bucket name created during deployment

aws s3 cp pii_redaction/sample_email/ccvod0ot9mu6s67t0ce81f8m2fp5d2722a7hq8o1 s3://<<raw_bucket>>/domain_emails/
```

The above triggers the redaction of the email process. You can track the progress in the DynamoDB table `<<inventory_table_name>>`. A unique `<<case_id>>` is generated and used in the DynamoDB inventory table for each email being processed. The inventory table name can be found on the resources tab in the AWS CloudFormation Console for `<<resource_name_prefix>>-S3Stack` stack and Logical ID `EmailInventoryTable`. Once redaction is complete, the redacted email body can be found in `<<redacted_bucket_name>>/redacted/<<today_date>>/<<case_id>>/email_body/` and redacted attachments in `<<redacted_bucket_name>>/redacted/<<today_date>>/<<case_id>>/attachments/`.

### Portal setup

The installation of the portal is completely optional. This section can be skipped; check the console of the AWS account where the solution is deployed to view the resources created. The portal serves as a web interface to manage the PII-redacted emails processed by the backend AWS infrastructure, allowing users to view sanitized email content. The Portal can be used to:

- List messages: View processed emails with redacted content
- Message details: View individual email content and attachments

Portal Prerequisites: This portal requires the installation of the following software tools:

- [TypeScript](https://www.typescriptlang.org/download/)
- [Node v18](https://nodejs.org/en/blog/release/v18.12.0) or higher
- [NPM v9.8](https://www.npmjs.com/package/npm/v/9.8.0) or higher

#### Infrastructure Deployment

- Synthesize the CloudFormation template for this code by going to the directory root of the solution. Now run the following command:  `cd sample-bda-redaction/infra/`
- Optional: Create and activate a new Python virtual environment (if the virtual environment has not been created previously):  `python3 -m venv .venv. .venv/bin/activatepip install -r requirements.txt`
- Users can now synthesize the CloudFormation template for this code.  `JSII_DEPRECATED=quiet JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=quiet cdk synth --no-notices`
- Deploy the React-based portal. Replace `<<resource_name_prefix>>` with its chosen value:  `JSII_DEPRECATED=quiet JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=quiet cdk deploy <<resource_name_prefix>>-PortalStack --no-notices`

The first-time deployment should take approximately 10 minutes to complete.

#### Environment Variables

- Create a new environment file by going to the root of the app directory and update the following variables in the `.env` file (by copying the `.env.example` file to `.env`) using the following command to create the `.env` file using a terminal/CLI environment.  `cp .env.example .env`
- The file can be created using your preferred text editor as well.

| **Environment Variable Name** | **Default** | **Description** | **Required** |
| --- | --- | --- | --- |
| `VITE_APIGW` | “” | URL of the API Gateway invokes URL (including protocol) without the path (remove /portal from the value). This value can be found in the output of the PortalStack after deploying through AWS CDK. It can also be found under the Outputs tab of the PortalStack CloudFormation stack under the export name of `PiiPortalApiGatewayInvokeUrl` | Yes |
| `VITE_BASE` | /portal | It specifies the path used to request the static files needed to render the portal | Yes |
| `VITE_API_PATH` | /api | It specifies the path needed to send requests to the API Gateway | Yes |

#### Portal deployment

Run the following commands from within a terminal/CLI environment.

- Before running any of the following commands, go to the root of the app directory to build this application for production by running the following commands:  Install NPM packages  `npm install`  Build the files  `npm run build`
- After the build succeeds, transfer all of the files within the `dist/` directory into the Amazon S3 bucket that is designated for these assets (specified in the PortalStack provisioned via CDK).  Example: `aws s3 sync dist/ s3://<<name-of-s3-bucket>> --delete<<name-of-s3-bucket>>` is the S3 bucket that has been created in the `<<resource-name-prefix>>-PortalStack` CloudFormation stack with the Logical ID of `PrivateWebHostingAssets`. This value can be obtained from the Resources tab of the CloudFormation stack in the AWS Console. This value is also output during the `cdk deploy` process when the PortalStack has been successfully completed.

#### Accessing the portal

Use the API Gateway invoke URL from the API Gateway that has been created during the `cdk deploy` process to access the portal from a web browser. This URL can be found by following these steps:

- Visit the AWS Console
- Go to API Gateway and find the API Gateway that has been created during the `cdk deploy` process. The name of the API Gateway can be found in the Resources section of the `<<resource-name-prefix>>-PortalStack` CloudFormation stack.
- Click on the **Stages** link in the left-hand menu.
- Make sure that the **portal** stage is selected
- Find the **Invoke URL** and copy that value
- Enter that value in the address bar of your web browser

The portal’s user interface is now visible within the web browser. If any emails have been processed, they are listed on the home page of the portal.

#### Access control (optional)

For production deployment, we recommend [these approaches](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-control-access-to-api.html) to controlling and managing access to the Portal.

### Clean up

To avoid incurring future charges, follow these steps to remove the resources created by this solution:

- Delete the contents of the [S3 buckets](https://docs.aws.amazon.com/AmazonS3/latest/userguide/delete-bucket.html) created by the solution:  Raw email bucket Redacted email bucket Portal static assets bucket (if portal was deployed)
- Delete or disable the Amazon SES rule step created by the solution using below cli command:  `#to disable the rule set use below command aws ses set-active-receipt-rule-set #to delete the rule set use below command # Replace <<resource_name_prefix>> with resource_name_prefix used in context.json aws ses delete-receipt-rule-set --rule-set-name <resource_name_prefix>>-rule-set`
- Remove the CloudFormation stacks in the following order:  `cdk destroy <<resource_name_prefix>>-PortalStack (if deployed) cdk destroy <<resource_name_prefix>>-ConsumerStack cdk destroy <<resource_name_prefix>>-S3Stack`
- CDK Destroy does not remove the access log Amazon S3 bucket created as part of the deployment. Users can get access to the log bucket name in the output tab of stack `<<resource_name_prefix>>-S3Stack` with export name AccessLogsBucket. Execute the below steps to delete the access log bucket:  To delete the contents of the access log bucket, follow the [instructions on deleting S3 bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/delete-bucket.html) Access to the log bucket is version-enabled and deleting the content of the bucket in the above step does not delete versioned objects in the bucket. That needs to be removed separately using below aws cli commands:  `#to remove versioned objects use below aws cli command aws s3api delete-objects --bucket ${accesslogbucket} --delete "$(aws s3api list-object-versions --bucket ${accesslogbucket} --query='{Objects: Versions[].{Key:Key,VersionId:VersionId}}')" #once versioned objects are removed we need to remove the delete markers of the versioned objects using below aws cli command aws s3api delete-objects --bucket ${accesslogbucket} --delete "$(aws s3api list-object-versions --bucket ${accesslogbucket} --query='{Objects: DeleteMarkers[].{Key:Key,VersionId:VersionId}}')"`  Delete the access log Amazon S3 bucket using below aws cli command:  `#delete the access log bucket itself using below aws cli command aws s3api delete-bucket --bucket ${accesslogbucket}`
- If Amazon SES is configured:  Remove the verified domain/email identities Delete the MX records from your DNS provider Delete the SMTP credentials from AWS Secrets Manager
- [Delete any CloudWatch Log groups](https://docs.aws.amazon.com/solutions/latest/video-on-demand-on-aws-foundation/deleting-the-cloudwatch-logs.html) created by the Lambda functions

The VPC and its associated resources as prerequisites for this solution may not be deleted if they may be used by other applications.

## Conclusion

In this post, we demonstrated how to automate the detection and redaction of PII across both text and image content using Amazon Bedrock Data Automation and Amazon Bedrock Guardrails. By centralizing and streamlining the redaction process, organizations can strengthen alignment with data privacy requirements, enhance security practices, and minimize operational overhead.

However, it is equally important to make sure that your solution is built with Amazon Bedrock Data Automation’s document processing [constraints](https://docs.aws.amazon.com/bedrock/latest/userguide/bda-output-documents.html) in mind. Amazon Bedrock Data Automation supports PDF, JPEG, and PNG file formats with a maximum console-processing size of 200 MB (500 MB via API), and single documents may not exceed 20 pages unless document splitting is enabled.

By using Amazon Bedrock Data Automation and Amazon Bedrock Guardrails centralized redaction capabilities, organizations can boost data privacy compliance management, cut operational overhead, and maintain stringent security across diverse workloads. This solution’s extensibility further enables integration with other AWS services, fine-tuning detection logic for more advanced PII patterns, and broadening support for additional file types or languages in the future, thereby evolving into a more robust, enterprise-scale data protection framework.

We encourage exploration of the [provided GitHub repository](https://github.com/aws-samples/sample-bda-redaction) to deploy this solution within your organization. In addition to delivering operational efficiency, scalability, security, and adaptability, the solution also provides a unified interface and robust audit trail that simplifies data governance. By refining detection rules, users can integrate additional file formats where possible and use Amazon Bedrock Data Automation and Amazon Bedrock Guardrails modular framework.

We invite you to implement this PII detection and redaction solution in the following [GitHub repo](https://github.com/aws-samples/sample-bda-redaction) to build a more secure, compliance-aligned, and highly adaptable data protection solution on Amazon Bedrock that addresses evolving business and regulatory requirements.

### About the Authors

![Author Himanshu Dixit](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/23/ML-184362.jpeg)**Himanshu Dixit** is a Delivery Consultant at AWS Professional Services specializing in databases and analytics, bringing over 18 years of experience in technology. He is passionate for artificial intelligence, machine learning, and generative AI, leveraging these cutting-edge technologies to create innovative solutions that address real-world challenges faced by customers. Outside of work, he enjoys playing badminton, tennis, cricket, table tennis and spending time with her two daughters.

![Author David Zhang](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/23/ML-184363.jpeg)**David Zhang** is an Engagement Manager at AWS Professional Services, where he leads enterprise-scale AI/ML, cloud transformation initiatives for Fortune 100 customers in telecom, finance, media, and entertainment. Outside of work, he enjoys experimenting with new recipes in his kitchen, playing tenor saxophone, and capturing life’s moments through his camera.

![Author Richard Session](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/23/ML-184364.jpeg)**Richard Session** is a Lead User Interface Developer for AWS ProServe, bringing over 15 years of experience as a full-stack developer across marketing/advertising, enterprise technology, automotive, and ecommerce industries. With a passion for creating intuitive and engaging user experiences, he uses his extensive background to craft exceptional interfaces for AWS’s enterprise customers. When he’s not designing innovative user experiences, Richard can be found pursuing his love for coffee, spinning tracks as a DJ, or exploring new destinations around the globe.

![Author Viyoma Sachdeva](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/12/23/ML-184365.jpeg)**Viyoma Sachdeva** is a Principal Industry Specialist in AWS. She is specialized in AWS DevOps, containerization and IoT helping Customer’s accelerate their journey to AWS Cloud.
