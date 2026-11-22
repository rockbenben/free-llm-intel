---
vendor: aws_bedrock
title: Simplify multimodal generative AI with Amazon Bedrock Data Automation
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/simplify-multimodal-generative-ai-with-amazon-bedrock-data-automation
date: 2024-12-17
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: bae542ca372f
---

# Simplify multimodal generative AI with Amazon Bedrock Data Automation

| **March 2025:** Amazon Bedrock Data Automation (BDA) is now generally available with the following improvements:   New region: BDA is now available in `us-east-1` in addition to `us-west-2`. Cross-region inference support: BDA now uses AWS cross-region inference to optimize routing across regions within your geography to process your request. Document accuracy improvements: Accuracy improvements across a variety of document types. Video accuracy improvements: Enhanced scene-level and full video summarization accuracy for richer contextual insights. Logo detection: Support for detection of 35,000+ company logos in images and videos. Tagging support: BDA now supports tagging of BDA resources and jobs to track costs and enforce tag-based access policies in AWS Identity and Access Management (IAM). AWS PrivateLink support: Access BDA via PrivateLink for private connectivity from your VPC. KMS-CMK Support: BDA now supports Customer Managed Keys (CMK) for granular encryption control. |
| --- |

Developers face significant challenges when using [foundation models](https://aws.amazon.com/what-is/foundation-models/) (FMs) to extract data from unstructured assets. This data extraction process requires carefully identifying models that meet the developer’s specific accuracy, cost, and feature requirements. Additionally, developers must invest considerable time optimizing price performance through fine-tuning and extensive prompt engineering. Managing multiple models, implementing safety guardrails, and adapting outputs to align with downstream system requirements can be difficult and time consuming.

[Amazon Bedrock Data Automation](https://aws.amazon.com/bedrock/bda/) helps address these and other challenges. This new capability from [Amazon Bedrock](https://aws.amazon.com/bedrock/) offers a unified experience for developers of all skillsets to easily automate the extraction, transformation, and generation of relevant insights from documents, images, audio, and videos to build [generative AI](https://aws.amazon.com/generative-ai/)–powered applications. With Amazon Bedrock Data Automation, customers can fully utilize their data by extracting insights from their unstructured multimodal content in a format compatible with their applications. Amazon Bedrock Data Automation’s managed experience, ease of use, and customization capabilities help customers deliver business value faster, eliminating the need to spend time and effort orchestrating multiple models, engineering prompts, or stitching together outputs.

In this post, we demonstrate how to use Amazon Bedrock Data Automation in the [AWS Management Console](https://aws.amazon.com/console/) and the [AWS SDK for Python (Boto3)](https://aws.amazon.com/sdk-for-python/) for media analysis and intelligent document processing (IDP) workflows.

## Amazon Bedrock Data Automation overview

You can use Amazon Bedrock Data Automation to generate standard outputs and custom outputs. Standard outputs are modality-specific default insights, such as video summaries that capture key moments, visual and audible toxic content, explanations of document charts, graph figure data, and more. Custom outputs use customer-defined blueprints that specify output requirements using natural language or a schema editor. The blueprint includes a list of fields to extract, data format for each field, and other instructions, such as data transformations and normalizations. This gives customers full control of the output, making it easy to integrate Amazon Bedrock Data Automation into existing applications.

Using Amazon Bedrock Data Automation, you can build powerful generative AI applications and automate use cases such as media analysis and IDP. Amazon Bedrock Data Automation is also integrated with [Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/), making it easier for developers to generate meaningful information from their unstructured multimodal content to provide more relevant responses for [Retrieval Augmented Generation](https://aws.amazon.com/what-is/retrieval-augmented-generation/) (RAG).

Customers can get started with standard outputs for all four modalities: documents, images, videos, and audio and custom outputs for documents and images. Custom outputs for video and audio will be supported in the future.

## Amazon Bedrock Data Automation for images, audio, and video

To take a media analysis example, suppose that customers in the media and entertainment industry are looking to monetize long-form content, such as TV shows and movies, through contextual ad placement. To deliver the right ads at the right video moments, you need to derive meaningful insights from both the ads and the video content. Amazon Bedrock Data Automation enables your contextual ad placement application by generating these insights. For instance, you can extract valuable information such as video summaries, scene-level summaries, content moderation concepts, and scene classifications based on the Interactive Advertising Bureau (IAB) taxonomy.

To get started with deriving insights with Amazon Bedrock Data Automation, you can create a project where you can specify your output configuration using the AWS console, [AWS Command Line Interface](https://aws.amazon.com/cli/) (AWS CLI) or API.

To create a project on the [Amazon Bedrock console](https://console.aws.amazon.com/bedrock), follow these steps:

- Expand the **Data Automation** dropdown menu in the navigation pane and select **Projects**, as shown in the following screenshot.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/03/1_2025-02-25_12-37-01.jpg)
- From the **Projects** console, create a new project and provide a project name, as shown in the following screenshot.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/03/2_2025-02-25_12-38-06.jpg)
- From within the project, choose **Edit**, as shown in the following screenshot, to specify or modify an output configuration. Standard output is the default way of interacting with Amazon Bedrock Data Automation, and it can be used with audio, documents, images and videos, where you can have one standard output configuration per data type for each project.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/03/3_2025-02-25_12-40-45.jpg)
- For customers who want to analyze images and videos for media analysis, standard output can be used to generate insights such as image summary, video scene summary, and scene classifications with IAB taxonomy. You can select the image summarization, video scene summarization, and IAB taxonomy checkboxes from the **Standard output** tab and then choose **Save changes** to finish configuring your project, as shown in the following screenshot.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/03/4_2025-02-25_12-43-28.jpg)
- To test the standard output configuration using your media assets, choose **Test**, as shown in the following screenshot.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/03/5_2025-02-25_12-44-31.jpg)

The next example uses the project to generate insights for a travel ad.

- Upload an image, then choose **Generate results**, as shown in the following screenshot, for Amazon Bedrock Data Automation to invoke an inference request.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/03/6_2025-02-25_12-46-58.jpg)
- Amazon Bedrock Data Automation will process the uploaded file based on the project’s configuration, automatically detecting that the file is an image and then generating a summary and IAB categories for the travel ad.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/03/7_2025-02-25_12-50-57.jpg)
- After you have generated insights for the ad image, you can generate video insights to determine the best video scene for effective ad placement. In the same project, upload a video file and choose **Generate results**, as shown in the following screenshot.
![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/03/8_2025-02-25_12-52-48.jpg)

Amazon Bedrock Data Automation will detect that the file is a video and will generate insights for the video based on the standard output configuration specified in the project, as shown in the following screenshot.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/03/03/9_2025-02-25_12-54-55.jpg)

These insights from Amazon Bedrock Data Automation, can help you effectively place relevant ads in your video content, which can help improve content monetization.

## Intelligent document processing with Amazon Bedrock Data Automation

You can use Amazon Bedrock Data Automation to automate IDP workflows at scale, without needing to orchestrate complex document processing tasks such as classification, extraction, normalization, or validation.

To take a mortgage example, a lender wants to automate the processing of a mortgage lending packet to streamline their IDP pipeline and improve the accuracy of loan processing. Amazon Bedrock Data Automation simplifies the automation of complex IDP tasks such as document splitting, classification, data extraction, output format normalization, and data validation. Amazon Bedrock Data Automation also incorporates confidence scores and visual grounding of the output data to mitigate hallucinations and help improve result reliability.

For example, you can generate custom output by defining blueprints, which specify output requirements using natural language or a schema editor, to process multiple file types in a single, streamlined API. Blueprints can be created using the console or the API, and you can use a catalog blueprint or create a custom blueprint for documents and images.

For all modalities, this workflow consists of three main steps: creating a project, invoking the analysis, and retrieving the results.

The following solution walks you through a simplified mortgage lending process with Amazon Bedrock Data Automation using the [Amazon SDK for Python (Boto3)](https://aws.amazon.com/sdk-for-python/), which is straightforward to integrate into an existing IDP workflow.

## Prerequisites

Before you invoke the Amazon Bedrock API, make sure you have the following:

- An AWS account that provides access to AWS services, including Amazon Bedrock Data Automation and [Amazon Simple Storage Service](https://aws.amazon.com/s3/) (Amazon S3)
- The AWS CLI [set up](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html)
- An [AWS Identity and Access Management](https://aws.amazon.com/iam/) (IAM) user [set up for the Amazon Bedrock Data Automation API](https://docs.aws.amazon.com/bedrock/latest/userguide/bda-using-api.html) and appropriate permissions added to the IAM user
- The IAM user access key and secret key to [configure](https://docs.aws.amazon.com/cli/v1/userguide/cli-chap-configure.html) the AWS CLI and permissions
- The latest [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) library
- The minimum Python version 3.8 configured with your integrated development environment (IDE)
- An S3 bucket

## Create custom blueprint

In this example, you have the lending packet, as shown in the following image, which contains three documents: a pay stub, a W-2 form, and a driver’s license.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/13/ML-17989-image010.png)

Amazon Bedrock Data Automation has sample blueprints for these three documents that define commonly extracted fields. However, you can also customize Amazon Bedrock Data Automation to extract specific fields from each document. For example, you can extract only the gross pay and net pay from the pay stub by creating a custom blueprint.

To create a custom blueprint using the API, you can use the `CreateBlueprint` operation using the [Amazon Bedrock Data Automation Client](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-data-automation.html). The following example shows the gross pay and net pay being defined as properties passed to `CreateBlueprint`, to be extracted from the lending packet:

```
bda_create_blueprint_response = bedrock_data_automation_client.create_blueprint(
    blueprintName='CUSTOM_PAYSLIP_BLUEPRINT',
    type='DOCUMENT',
    blueprintStage='LIVE',
    schema=json.dumps({
        '$schema': 'http://json-schema.org/draft-07/schema#',
        'description': 'default',
        'documentClass': 'default',
        'type': 'object',
        'properties': {
            'gross_pay_this_period': {
                'type': 'number',
                'inferenceType': 'extractive',
                'description': 'The gross pay for this pay period from the Earnings table'
            },
            'net_pay': {
                'type': 'number',
                'inferenceType': 'extractive',
                'description': 'The net pay for this pay period from the bottom of the document'
            }
        }
    }),
)
```

The `CreateBlueprint` response returns the `blueprintARN` for the pay stub’s custom blueprint:

```
'blueprintArn: arn:aws:bedrock:us-west-2:<AWS_ACCOUNT_ID>:blueprint/<BLUEPRINT_ID>'
```

### Configure Amazon Bedrock Data Automation project

To begin processing files using blueprints with Amazon Bedrock Data Automation, you first need to create a data automation project. To process a multiple-page document containing different file types, you can configure a project with different blueprints for each file type.

Use Amazon Bedrock Data Automation to apply multiple document blueprints within one project so you can process different types of documents within the same project, each with its own custom extraction logic.

When using the API to create a project, you invoke the `CreateDataAutomationProject` operation. The following is an example of how you can configure custom output using the custom blueprint for the pay stub and the sample blueprints for the W-2 and driver’s license:

```
bda_bedrock_automation_create_project_response = bedrock_data_automation_client.create_data_automation_project(
    projectName='TEST_PROJECT',
    projectDescription='test BDA project',
    projectStage=bda_stage,
    standardOutputConfiguration={
        'document': {
            'outputFormat': {
                'textFormat': {
                    'types': ['PLAIN_TEXT']
                },
                'additionalFileFormat': {
                    'state': 'ENABLED',
                }
            }
        },
    },
    customOutputConfiguration={
        'blueprints': [
          {
              'blueprintArn': 'arn:aws:bedrock:us-west-2:<AWS_ACCOUNT_ID>:blueprint/<BLUEPRINT_ID>'
          },
          {
              'blueprintArn': 'arn:aws:bedrock:us-west-2:aws:blueprint/bedrock-data-automation-public-w2-form'
          },
          {
              'blueprintArn': 'arn:aws:bedrock:us-west-2:aws:blueprint/bedrock-data-automation-public-us-driver-license'
          },
        ],
    },
    overrideConfiguration={
        'document': {
            'splitter': {
                'state': 'ENABLED'
            }
        }
    },
)
```

The `CreateProject` response returns the `projectARN` for the project:

```
'arn:aws:bedrock:us-west-2:<AWS_ACCOUNT_ID>:data-automation-project/<PROJECT_ID>'
```

To process different types of documents using multiple document blueprints in a single project, Amazon Bedrock Data Automation uses a splitter configuration, which must be enabled through the API. The following is the override configuration for the splitter, and you can refer to the [Boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-data-automation/client/create_data_automation_project.html) for more information:

```
overrideConfiguration={
    'document': {
        'splitter': {
            'state': 'ENABLED' | 'DISABLED'
        }
    }
},
```

Upon creation, the API validates the input configuration and creates a new project, returning the `projectARN`, as shown in the following screenshot.

```
'arn:aws:bedrock:us-west-2:<AWS_ACCOUNT_ID>:data-automation-project/<PROJECT_ID>'
```

### Test the solution

Now that the blueprint and project setup is complete, the `InvokeDataAutomationAsync` operation from the [Amazon Bedrock Data Automation runtime](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-data-automation.html) can be used to start processing files. This API call initiatives the asynchronous processing of files in an S3 bucket, in this case the lending packet, using the configuration defined in the project by passing the project’s ARN:

```
bda_invoke_data_automation_async_response = bedrock_data_automation_runtime_client.invoke_data_automation_async(
    inputConfiguration={'s3Uri': '<S3_URI>'},
    outputConfiguration={'s3Uri': '<S3_URI>'},
    dataAutomationProfileARN=‘arn:aws:bedrock:us-west-2:<AWS_ACCOUNT_ID>:data-automation-profile/bda.v1:0‘
    dataAutomationConfiguration={
        ‘dataAutomationProjectArn’: ‘arn:aws:bedrock:us-west-2:<AWS_ACCOUNT_ID>:data-automation-project/<PROJECT_ID>‘,
        'stage': 'LIVE'
    }
)
```

`InvokeDataAutomationAsync` returns the `invocationARN`:

```
'arn:aws:bedrock:us-west-2:<AWS_ACCOUNT_ID>:data-automation-invocation/<INVOCATION_ID>'
```

`GetDataAutomationStatus` can be used to view the status of the invocation, using the `InvocationARN` from the previous response:

```
bda_invoke_data_automation_async_response = bedrock_data_automation_runtime_client.get_data_automation_status(
    invocationArn='arn:aws:bedrock:us-west-2:<AWS_ACCOUNT_ID>:data-automation-invocation/<INVOCATION_ID>'
)
```

When the job is complete, view the results in the S3 bucket used in the `outputConfiguration` by navigating to the `~/JOB_ID/0/custom_output/` folder.

From the following sample output, Amazon Bedrock Data Automation associated the pay stub file with the custom pay stub blueprint with a high level of confidence:

```
'matched_blueprint': {
    'arn': '<BLUEPRINT_ARN>', 'name': 'CUSTOM_PAYSLIP_BLUEPRINT', 'confidence': 0.99959725
}
```

Using the matched blueprint, Amazon Bedrock Data Automation was able to accurately extract each field defined in the blueprint:

```
'inference_result': {
    'net_pay': 291.9, 'gross_pay_this_period': 452.43
}
```

Additionally, Amazon Bedrock Data Automation returns confidence intervals and bounding box information for each field:

```
'explainability_info': [{
    'net_pay': {'success': true, 'confidence': 0.96484375, 'geometry': [{'boundingBox': ...
```

This example demonstrates how customers can use Amazon Bedrock Data Automation to streamline and automate an IDP workflow. Amazon Bedrock Data Automation automates complex document processing tasks such as data extraction, normalization, and validation from documents. Amazon Bedrock Data Automation helps to reduce operational complexity and improves processing efficiency to handle higher loan processing volumes, minimize errors, and drive operational excellence.

## Cleanup

When you’re finished evaluating this feature, delete the S3 bucket and any objects to avoid any further charges.

## Summary

Customers can get started with Amazon Bedrock Data Automation, which is available in [AWS Region](https://docs.aws.amazon.com/glossary/latest/reference/glos-chap.html#region)s US East (N. Virginia) and US West (Oregon). Learn more about [Amazon Bedrock Data Automation](https://aws.amazon.com/bedrock/bda/) and how to automate the generation of accurate information from unstructured content for building generative AI–based applications.

## About the authors

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/13/ian.jpg)**[**Ian Lodge**](https://www.linkedin.com/in/ian-lodge/) is a Solutions Architect at AWS, helping ISV customers in solving their architectural, operational, and cost optimization challenges. Outside of work he enjoys spending time with his family, ice hockey and woodworking.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/12/16/alex.jpg)[**Alex Pieri**](https://www.linkedin.com/in/alexander-pieri/) is a Solutions Architect at AWS that works with retail customers to plan, build, and optimize their AWS cloud environments. He specializes in helping customers build enterprise-ready generative AI solutions on AWS.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/12/raj.jpeg)[**Raj Pathak**](https://www.linkedin.com/in/rajpathakaws/) is a Principal Solutions Architect and Technical advisor to Fortune 50 and Mid-Sized FSI (Banking, Insurance, Capital Markets) customers across Canada and the United States. Raj specializes in Machine Learning with applications in Generative AI, Natural Language Processing, Intelligent Document Processing, and MLOps.
