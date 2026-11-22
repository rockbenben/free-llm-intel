---
vendor: aws_bedrock
title: Build a serverless audio summarization solution with Amazon Bedrock and Whisper
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-a-serverless-audio-summarization-solution-with-amazon-bedrock-and-whisper
date: 2025-06-06
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: afc18bf96f55
---

# Build a serverless audio summarization solution with Amazon Bedrock and Whisper

Recordings of business meetings, interviews, and customer interactions have become essential for preserving important information. However, transcribing and summarizing these recordings manually is often time-consuming and labor-intensive. With the progress in [generative AI](https://aws.amazon.com/ai/generative-ai/) and automatic speech recognition (ASR), automated solutions have emerged to make this process faster and more efficient.

Protecting personally identifiable information (PII) is a vital aspect of data security, driven by both ethical responsibilities and legal requirements. In this post, we demonstrate how to use the Open AI Whisper foundation model (FM) Whisper Large V3 Turbo, available in [Amazon Bedrock Marketplace](https://aws.amazon.com/bedrock/marketplace/), which offers access to over 140 models through a dedicated offering, to produce near real-time transcription. These transcriptions are then processed by [Amazon Bedrock](https://aws.amazon.com/bedrock/) for summarization and redaction of sensitive information.

Amazon Bedrock is a fully managed service that offers a choice of high-performing FMs from leading AI companies like [AI21 Labs](https://aws.amazon.com/bedrock/ai21/), [Anthropic](https://aws.amazon.com/bedrock/claude/), [Cohere](https://aws.amazon.com/bedrock/cohere/), [DeepSeek](https://aws.amazon.com/bedrock/deepseek), [Luma](https://aws.amazon.com/bedrock/luma-ai/), [Meta](https://aws.amazon.com/bedrock/llama/), [Mistral AI](https://aws.amazon.com/bedrock/mistral/), [poolside](https://aws.amazon.com/bedrock/poolside/) (coming soon), [Stability AI](https://aws.amazon.com/bedrock/stability-ai/), and [Amazon Nova](https://aws.amazon.com/ai/generative-ai/nova/) through a single API, along with a broad set of capabilities to build generative AI applications with security, privacy, and responsible AI. Additionally, you can use [Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/) to automatically redact [sensitive information](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-sensitive-filters.html), including PII, from the transcription summaries to support compliance and data protection needs.

In this post, we walk through an end-to-end architecture that combines a React-based frontend with Amazon Bedrock, [AWS Lambda](https://aws.amazon.com/lambda), and [AWS Step Functions](https://aws.amazon.com/step-functions/) to orchestrate the workflow, facilitating seamless integration and processing.

## Solution overview

The solution highlights the power of integrating serverless technologies with generative AI to automate and scale content processing workflows. The user journey begins with uploading a recording through a React frontend application, hosted on [Amazon CloudFront](https://aws.amazon.com/cloudfront/) and backed by [Amazon Simple Storage Service](https://aws.amazon.com/s3) (Amazon S3) and [Amazon API Gateway](https://aws.amazon.com/api-gateway). When the file is uploaded, it triggers a Step Functions state machine that orchestrates the core processing steps, using AI models and Lambda functions for seamless data flow and transformation. The following diagram illustrates the solution architecture.

![AWS serverless architecture for audio processing: CloudFront to S3, EventBridge trigger, Lambda and Bedrock for transcription and summarization](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/15/Picture1-5-1024x478.png)

The workflow consists of the following steps:

- The React application is hosted in an S3 bucket and served to users through CloudFront for fast, global access. API Gateway handles interactions between the frontend and backend services.
- Users upload audio or video files directly from the app. These recordings are stored in a designated S3 bucket for processing.
- An [Amazon EventBridge](https://aws.amazon.com/eventbridge/) rule detects the S3 upload event and triggers the Step Functions state machine, initiating the AI-powered processing pipeline.
- The state machine performs audio transcription, summarization, and redaction by orchestrating multiple Amazon Bedrock models in sequence. It uses Whisper for transcription, Claude for summarization, and Guardrails to redact sensitive data.
- The redacted summary is returned to the frontend application and displayed to the user.

The following diagram illustrates the state machine workflow.

![AWS Step Functions state machine for audio processing: Whisper transcription, speaker identification, and Bedrock summary tasks](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/19/Picture2-4-crop.png)

The Step Functions state machine orchestrates a series of tasks to transcribe, summarize, and redact sensitive information from uploaded audio/video recordings:

- A Lambda function is triggered to gather input details (for example, Amazon S3 object path, metadata) and prepare the payload for transcription.
- The payload is sent to the OpenAI Whisper Large V3 Turbo model through the Amazon Bedrock Marketplace to generate a near real-time transcription of the recording.
- The raw transcript is passed to Anthropic’s Claude Sonnet 3.5 through Amazon Bedrock, which produces a concise and coherent summary of the conversation or content.
- A second Lambda function validates and forwards the summary to the redaction step.
- The summary is processed through Amazon Bedrock Guardrails, which automatically redacts PII and other sensitive data.
- The redacted summary is stored or returned to the frontend application through an API, where it is displayed to the user.

## Prerequisites

Before you start, make sure that you have the following prerequisites in place:

- Before using Amazon Bedrock models, you must request access—a one-time setup step. For this solution, verify that access to the Anthropic’s Claude Sonnet 3.5 model is enabled in your Amazon Bedrock account. For instructions, see [Access Amazon Bedrock foundation models](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html).
- Set up a guardrail to enable PII redaction by configuring filters that block or mask sensitive information. For guidance on configuring filters for additional use cases, see [Remove PII from conversations by using sensitive information filters](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-sensitive-filters.html).
- Deploy the Whisper Large V3 Turbo model within the [Amazon Bedrock Marketplace](https://aws.amazon.com/bedrock/marketplace/). This post also offers step-by-step guidance for the deployment.
- The [AWS Command Line Interface](https://aws.amazon.com/cli) (AWS CLI) should be installed and configured. For instructions, see [Installing or updating to the latest version of the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
- [Node.js 14.x](https://nodejs.org/en/download) or later should be installed.
- The [AWS CDK CLI](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html#getting_started_install) should be installed.
- You should have [Python 3.8+](https://www.python.org/downloads/).

## Create a guardrail in the Amazon Bedrock console

For instructions for creating guardrails in Amazon Bedrock, refer to [Create a guardrail](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-create.html). For details on detecting and redacting PII, see [Remove PII from conversations by using sensitive information filters](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-sensitive-filters.html). Configure your guardrail with the following key settings:

- Enable PII detection and handling
- Set PII action to Redact
- Add the relevant PII types, such as:  Names and identities Phone numbers Email addresses Physical addresses Financial information Other sensitive personal information

After you deploy the guardrail, note the Amazon Resource Name (ARN), and you will be using this when deploys the model.

## Deploy the Whisper model

Complete the following steps to deploy the Whisper Large V3 Turbo model:

- On the Amazon Bedrock console, choose **Model catalog **under **Foundation models **in the navigation pane.
- Search for and choose **Whisper Large V3 Turbo**.
- On the options menu (three dots), choose **Deploy**.

![Amazon Bedrock console displaying filtered model catalog with Whisper Large V3 Turbo speech recognition model and deployment option](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/15/Picture3-1.png)

- Modify the endpoint name, number of instances, and instance type to suit your specific use case. For this post, we use the default settings.
- Modify the **Advanced settings** section to suit your use case. For this post, we use the default settings.
- Choose **Deploy**.

This creates a new [AWS Identity and Access Management](https://aws.amazon.com/iam/) IAM role and deploys the model.

You can choose **Marketplace deployments** in the navigation pane, and in the **Managed deployments** section, you can see the endpoint status as **Creating**. Wait for the endpoint to finish deployment and the status to change to **In Service**, then copy the Endpoint Name, and you will be using this when deploying the

![Amazon Bedrock console: "How it works" overview, managed deployments table with Whisper model endpoint in service](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/15/Picture4.png)

## Deploy the solution infrastructure

In the [GitHub repo](https://github.com/aws-samples/sample-bedrock-whisper-pii-audio-summarizer/), follow the instructions in the [README file](https://github.com/aws-samples/sample-bedrock-whisper-pii-audio-summarizer?tab=readme-ov-file) to clone the repository, then deploy the frontend and backend infrastructure.

We use the [AWS Cloud Development Kit](https://aws.amazon.com/cdk/) (AWS CDK) to define and deploy the infrastructure. The AWS CDK code deploys the following resources:

- React frontend application
- Backend infrastructure
- S3 buckets for storing uploads and processed results
- Step Functions state machine with Lambda functions for audio processing and PII redaction
- API Gateway endpoints for handling requests
- IAM roles and policies for secure access
- CloudFront distribution for hosting the frontend

## Implementation deep dive

The backend is composed of a sequence of Lambda functions, each handling a specific stage of the audio processing pipeline:

- **Upload handler** – Receives audio files and stores them in Amazon S3
- **Transcription with Whisper** – Converts speech to text using the Whisper model
- **Speaker detection** – Differentiates and labels individual speakers within the audio
- **Summarization using Amazon Bedrock** – Extracts and summarizes key points from the transcript
- **PII redaction** – Uses Amazon Bedrock Guardrails to remove sensitive information for privacy compliance

Let’s examine some of the key components:

The transcription Lambda function uses the Whisper model to convert audio files to text:

```
def transcribe_with_whisper(audio_chunk, endpoint_name):
    # Convert audio to hex string format
    hex_audio = audio_chunk.hex()
    
    # Create payload for Whisper model
    payload = {
        "audio_input": hex_audio,
        "language": "english",
        "task": "transcribe",
        "top_p": 0.9
    }
    
    # Invoke the SageMaker endpoint running Whisper
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType='application/json',
        Body=json.dumps(payload)
    )
    
    # Parse the transcription response
    response_body = json.loads(response['Body'].read().decode('utf-8'))
    transcription_text = response_body['text']
    
    return transcription_text
```

We use Amazon Bedrock to generate concise summaries from the transcriptions:

```
def generate_summary(transcription):
    # Format the prompt with the transcription
    prompt = f"{transcription}\n\nGive me the summary, speakers, key discussions, and action items with owners"
    
    # Call Bedrock for summarization
    response = bedrock_runtime.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
        body=json.dumps({
            "prompt": prompt,
            "max_tokens_to_sample": 4096,
            "temperature": 0.7,
            "top_p": 0.9,
        })
    )
    
    # Extract and return the summary
    result = json.loads(response.get('body').read())
    return result.get('completion')
```

A critical component of our solution is the automatic redaction of PII. We implemented this using Amazon Bedrock Guardrails to support compliance with privacy regulations:

```
def apply_guardrail(bedrock_runtime, content, guardrail_id):
# Format content according to API requirements
formatted_content = [{"text": {"text": content}}]

# Call the guardrail API
response = bedrock_runtime.apply_guardrail(
guardrailIdentifier=guardrail_id,
guardrailVersion="DRAFT",
source="OUTPUT",  # Using OUTPUT parameter for proper flow
content=formatted_content
)

# Extract redacted text from response
if 'action' in response and response['action'] == 'GUARDRAIL_INTERVENED':
if len(response['outputs']) > 0:
output = response['outputs'][0]
if 'text' in output and isinstance(output['text'], str):
return output['text']

# Return original content if redaction fails
return content
```

When PII is detected, it’s replaced with type indicators (for example, {PHONE} or {EMAIL}), making sure that summaries remain informative while protecting sensitive data.

To manage the complex processing pipeline, we use Step Functions to orchestrate the Lambda functions:

```
{
"Comment": "Audio Summarization Workflow",
"StartAt": "TranscribeAudio",
"States": {
"TranscribeAudio": {
"Type": "Task",
"Resource": "arn:aws:states:::lambda:invoke",
"Parameters": {
"FunctionName": "WhisperTranscriptionFunction",
"Payload": {
"bucket": "$.bucket",
"key": "$.key"
}
},
"Next": "IdentifySpeakers"
},
"IdentifySpeakers": {
"Type": "Task",
"Resource": "arn:aws:states:::lambda:invoke",
"Parameters": {
"FunctionName": "SpeakerIdentificationFunction",
"Payload": {
"Transcription.$": "$.Payload"
}
},
"Next": "GenerateSummary"
},
"GenerateSummary": {
"Type": "Task",
"Resource": "arn:aws:states:::lambda:invoke",
"Parameters": {
"FunctionName": "BedrockSummaryFunction",
"Payload": {
"SpeakerIdentification.$": "$.Payload"
}
},
"End": true
}
}
}
```

This workflow makes sure each step completes successfully before proceeding to the next, with automatic error handling and retry logic built in.

## Test the solution

After you have successfully completed the deployment, you can use the CloudFront URL to test the solution functionality.

![Audio/video upload and summary interface with completed file upload for team meeting recording analysis](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/29/mlblog-crop.gif)

## Security considerations

Security is a critical aspect of this solution, and we’ve implemented several best practices to support data protection and compliance:

- **Sensitive data redaction** – Automatically redact PII to protect user privacy.
- **Fine-Grained IAM Permissions** – Apply the principle of least privilege across AWS services and resources.
- **Amazon S3 access controls** – Use strict bucket policies to limit access to authorized users and roles.
- **API security** – Secure API endpoints using [Amazon Cognito](https://aws.amazon.com/cognito/) for user authentication (optional but recommended).
- **CloudFront protection** – Enforce HTTPS and apply modern TLS protocols to facilitate secure content delivery.
- **Amazon Bedrock data security** – Amazon Bedrock (including Amazon Bedrock Marketplace) protects customer data and does not send data to providers or train using customer data. This makes sure your proprietary information remains secure when using AI capabilities.

## Clean up

To prevent unnecessary charges, make sure to delete the resources provisioned for this solution when you’re done:

- Delete the Amazon Bedrock guardrail:  On the Amazon Bedrock console, in the navigation menu, choose **Guardrails**. Choose your guardrail, then choose **Delete**.
- Delete the Whisper Large V3 Turbo model deployed through the Amazon Bedrock Marketplace:  On the Amazon Bedrock console, choose **Marketplace deployments **in the navigation pane. In the **Managed deployments** section, select the deployed endpoint and choose **Delete**.
- Delete the AWS CDK stack by running the command `cdk destroy`, which deletes the AWS infrastructure.

## Conclusion

This serverless audio summarization solution demonstrates the benefits of combining AWS services to create a sophisticated, secure, and scalable application. By using Amazon Bedrock for AI capabilities, Lambda for serverless processing, and CloudFront for content delivery, we’ve built a solution that can handle large volumes of audio content efficiently while helping you align with security best practices.

The automatic PII redaction feature supports compliance with privacy regulations, making this solution well-suited for regulated industries such as healthcare, finance, and legal services where data security is paramount. To get started, deploy this architecture within your AWS environment to accelerate your audio processing workflows.

### About the Authors

![Kaiyin Hu](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/15/kaiyin_pt.jpeg)**Kaiyin Hu** is a Senior Solutions Architect for Strategic Accounts at Amazon Web Services, with years of experience across enterprises, startups, and professional services. Currently, she helps customers build cloud solutions and drives GenAI adoption to cloud. Previously, Kaiyin worked in the Smart Home domain, assisting customers in integrating voice and IoT technologies.

![Sid Vantair](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/05/15/image-3-2.png)**Sid Vantair** is a Solutions Architect with AWS covering Strategic accounts. He thrives on resolving complex technical issues to overcome customer hurdles. Outside of work, he cherishes spending time with his family and fostering inquisitiveness in his children.
