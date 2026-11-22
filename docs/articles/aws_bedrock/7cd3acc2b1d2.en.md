---
vendor: aws_bedrock
title: Orchestrate an intelligent document processing workflow using tools in Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/orchestrate-an-intelligent-document-processing-workflow-using-tools-in-amazon-bedrock
date: 2025-02-21
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: ab8dc1532841
---

# Orchestrate an intelligent document processing workflow using tools in Amazon Bedrock

[Generative AI](https://aws.amazon.com/ai/generative-ai/) is revolutionizing enterprise automation, enabling AI systems to understand context, make decisions, and act independently. Generative AI foundation models (FMs), with their ability to understand context and make decisions, are becoming powerful partners in solving sophisticated business problems. At AWS, we’re using the power of models in [Amazon Bedrock](https://aws.amazon.com/bedrock/) to drive automation of complex processes that have traditionally been challenging to streamline.

In this post, we focus on one such complex workflow: document processing. This serves as an example of how generative AI can streamline operations that involve diverse data types and formats.

## Challenges with document processing

Document processing often involves handling three main categories of documents:

- Structured – For example, forms with fixed fields
- Semi-structured – Documents that have a predictable set of information but might vary in layout or presentation
- Unstructured – For example, paragraphs of text or notes

Traditionally, processing these varied document types has been a pain point for many organizations. Rule-based systems or specialized machine learning (ML) models often struggle with the variability of real-world documents, especially when dealing with semi-structured and unstructured data.

We demonstrate how generative AI along with [external tool use](https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html) offers a more flexible and adaptable solution to this challenge. Through a practical use case of processing a patient health package at a doctor’s office, you will see how this technology can extract and synthesize information from all three document types, potentially improving data accuracy and operational efficiency.

## Solution overview

This intelligent document processing solution uses Amazon Bedrock FMs to orchestrate a sophisticated workflow for handling multi-page healthcare documents with mixed content types. The solution uses the FM’s tool use capabilities, accessed through the Amazon Bedrock [Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html). This enables the FMs to not just process text, but to actively engage with various external tools and APIs to perform complex document analysis tasks.

The solution employs a strategic multi-model approach, optimizing for both performance and cost by selecting the most appropriate model for each task:

- [Anthropic’s Claude 3 Haiku](https://aws.amazon.com/blogs/aws/upgraded-claude-3-5-sonnet-from-anthropic-available-now-computer-use-public-beta-and-claude-3-5-haiku-coming-soon-in-amazon-bedrock/) – Serves as the workflow orchestrator due to its low latency and cost-effectiveness. This model’s strong reasoning and tool use abilities make it ideal for the following:   Coordinating the overall document processing pipeline  Making routing decisions for different document types  Invoking appropriate processing functions  Managing the workflow state
- [Anthropic’s Claude 3.5 Sonnet (v2)](https://aws.amazon.com/blogs/aws/upgraded-claude-3-5-sonnet-from-anthropic-available-now-computer-use-public-beta-and-claude-3-5-haiku-coming-soon-in-amazon-bedrock/) – Used for its advanced reasoning capabilities, notably strong visual processing abilities, particularly excelling at interpreting charts and graphs. Its key strengths include:   Interpreting complex document layouts and structure  Extracting text from tables and forms  Processing medical charts and handwritten notes  Converting unstructured visual information into structured data

Through the Amazon Bedrock Converse API’s standardized tool use (function calling) interface, these models can work together seamlessly to invoke document processing functions, call external APIs for data validation, trigger storage operations, and execute content transformation tasks. The API serves as the foundation for this intelligent workflow, providing a unified interface for model communication while maintaining conversation state throughout the processing pipeline. The API’s standardized approach to tool definition and function calling provides consistent interaction patterns across different processing stages. For more details on how tool use works, refer to [The complete tool use workflow](https://github.com/aws-samples/prompt-engineering-with-anthropic-claude-v-3/blob/main/10_2_3_Complete_Tool_Use_Workflow.ipynb).

The solution incorporates [Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/) to implement robust content filtering policies and sensitive information detection, making sure that personal health information (PHI) and personally identifiable information (PII) data is appropriately protected through automated detection and masking capabilities while maintaining industry standard compliance throughout the document processing workflow.

## Prerequisites

You need the following prerequisites before you can proceed with this solution. For this post, we use the `us-west-2` AWS Region. For details on available Regions, see [Amazon Bedrock endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/bedrock.html).

- An [AWS account](https://signup.aws.amazon.com/billing/signup) with an [AWS Identity and Access Management](https://aws.amazon.com/iam) (IAM) role that has permissions to Amazon Bedrock and [Amazon SageMaker Studio](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-updated.html).
- Access to the Anthropic’s Claude 3.5 Sonnet (v2) and Claude 3 Haiku models in Amazon Bedrock. For instructions, see [Access Amazon Bedrock foundation models](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html) and [CreateInferenceProfile](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_CreateInferenceProfile.html).
- Access to create an Amazon Bedrock guardrail. For more information, see [Create a guardrail](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-create.html).

## Use case and dataset

For our example use case, we examine a patient intake process at a healthcare institution. The workflow processes a patient health information package containing three distinct document types:

- Structured document – A new patient intake form with standardized fields for personal information, medical history, and current symptoms. This form follows a consistent layout with clearly defined fields and check boxes, making it an ideal example of a structured document.
- Semi-structured document – A health insurance card that contains essential coverage information. Although insurance cards generally contain similar information (policy number, group ID, coverage dates), they come from different providers with varying layouts and formats, showing the semi-structured nature of these documents.
- Unstructured document – A handwritten doctor’s note from an initial consultation, containing free-form observations, preliminary diagnoses, and treatment recommendations. This represents the most challenging category of unstructured documents, where information isn’t confined to any predetermined format or structure.

The example document can be downloaded from the following [GitHub repo](https://github.com/aws-samples/anthropic-on-aws/blob/main/medical-idp/docs/new-patient-registration.pdf).

This healthcare use case is particularly relevant because it encompasses common challenges in document processing: the need for high accuracy, compliance with healthcare data privacy requirements, and the ability to handle multiple document formats within a single workflow. The variety of documents in this patient package demonstrates how a modern intelligent document processing solution must be flexible enough to handle different levels of document structure while maintaining consistency and accuracy in data extraction.

The following diagram illustrates the solution workflow.

![IDP flow using external tool claling](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/02/11/blog.drawio-3-980x1024.png)

This self-orchestrated workflow demonstrates how modern generative AI solutions can balance capability, performance, and cost-effectiveness in transforming traditional document processing workflows in healthcare settings.

## Deploy the solution

- Create an Amazon SageMaker domain. For instructions, see Use quick setup for Amazon SageMaker AI.
- Launch SageMaker Studio, then create and launch a JupyterLab space. For instructions, see Create a space.
- Create a guardrail. Focus on adding sensitive information filters that would mask PII or PHI.
- Clone the code from the GitHub repository: `git clone https://github.com/aws-samples/anthropic-on-aws.git`
- Change the directory to the root of the cloned repository: `cd medical-idp`
- Install dependencies: `pip install -r requirements.txt`
- Update setup.sh with the guardrail ID you created in Step 3. Then set the ENV variable: `source setup.sh`
- Finally, start the Streamlit application: `streamlit run streamlit_app.py`

Now you’re ready to explore the intelligent document processing workflow using Amazon Bedrock.

## Technical implementation

The solution is built around the Amazon Bedrock Converse API and tool use framework, with Anthropic’s Claude 3 Haiku serving as the primary orchestrator. When a document is uploaded through the Streamlit interface, Haiku analyzes the request and determines the sequence of tools needed by consulting the tool definitions in `ToolConfig`. These definitions include tools for the following:

- Document processing pipeline – Handles initial PDF processing and classification
- Document notes processing – Extracts information from medical notes
- New patient information processing – Processes patient intake forms
- Insurance form processing – Handles insurance card information

The following code is an example tool definition for extracting consultation notes. Here, `extract_consultation_notes` represents the name of the function that the orchestration workflow will call, and `document_paths` defines the schema of the input parameter that will be passed to the function. The FM will contextually extract the information from the document and pass to the method. A similar `toolspec` will be defined for each step. Refer to the [GitHub repo](https://github.com/aws-samples/anthropic-on-aws/blob/4c2365cc6d763b0a48d253da2e67beef7f702f16/medical-idp/utils/constants.py#L107) for the full `toolspec` definition.

```
{
            "toolSpec": {
                "name": "extract_consultation_notes",
                "description": "Extract diagnostics information from a doctor's consultation notes. Along with the extraction include the full transcript in a <transcript> node",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "document_paths": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Paths to the files that were classified as DOC_NOTES"
                            }
                        },
                        "required": ["document_paths"]
                    }
                }
            }
        }
```

When a PDF document is uploaded through the Streamlit interface, it is temporarily stored and passed to the FileProcessor class along with the tool specification and a user prompt:

```
prompt = ("1. Extract 2. save and 3. summarize the information from the patient information package located at " + tmp_file + ". " +
                          "The package might contain various types of documents including insurance cards. Extract and save information from all documents provided. "
                          "Perform any preprocessing or classification of the file provided prior to the extraction." + 
                          "Set the enable_guardrails parameter to " + str(enable_guardrails) + ". " + 
                          "At the end, list all the tools that you had access to. Give an explantion on why each tool was used and if you are not using a tool, explain why it was not used as well" + 
                          "Think step by step.")
                processor.process_file(prompt=prompt, 
toolspecs=toolspecs,...
```

The `BedrockUtils` class manages the conversation with Anthropic’s Claude 3 Haiku through the Amazon Bedrock Converse API. It maintains the conversation state and handles the tool use workflow:

```
# From bedrockutility.py
def invoke_bedrock(self, message_list, system_message=[], tool_list=[],
                  temperature=0, maxTokens=2048, guardrail_config=None):
    response = self.bedrock.converse(
        modelId=self.model_id,
        messages=message_list,
        system=system_message,
        inferenceConfig={
            "maxTokens": maxTokens,
            "temperature": temperature
        },
        **({"toolConfig": {"tools": tool_list}} if tool_list else {})
    )
```

When the processor receives a document, it initiates a conversation loop with Anthropic’s Claude 3 Haiku, which analyzes the document and determines which tools to use based on the content. The model acts as an intelligent orchestrator, making decisions about the following:

- Which document processing tools to invoke
- The sequence of processing steps
- How to handle different document types within the same package
- When to summarize and complete the processing

This orchestration is managed through a continuous conversation loop that processes tool requests and their results until the entire document package has been processed.

The first key decision in the workflow is initiating the document classification process. Through the `DocumentClassifier` class, the solution uses Anthropic’s Claude 3.5 Sonnet to analyze and categorize each page of the uploaded document into three main types: intake forms, insurance cards, and doctor’s notes:

```
# from document_classifier.py
class DocumentClassifier:
    def __init__(self, file_handler):
        self.sonnet_3_5_bedrock_utils = BedrockUtils(
            model_id=ModelIDs.anthropic_claude_3_5_sonnet
        )
        
    def categorize_document(self, file_paths):
        # Convert documents to binary format for model processing
        binary_data_array = []
        for file_path in file_paths:
            binary_data, media_type = self.file_handler.get_binary_for_file(file_path)
            binary_data_array.append((binary_data[0], media_type))

        # Prepare message for classification
        message_content = [
            {"image": {"format": media_type, "source": {"bytes": data}}}
            for data, media_type in binary_data_array
        ]
        
        # Create classification request
        message_list = [{
            "role": 'user',
            "content": [
                *message_content,
                {"text": "What types of document is in this image?"}
            ]
        }]
        
        # Define system message for classification
        system_message = [{
            "text": '''You are a medical document processing agent. 
                      Categorize images as: INTAKE_FORM, INSURANCE_CARD, or DOC_NOTES'''
        }]
        
        # Get classification from model
        response = self.sonnet_3_5_bedrock_utils.invoke_bedrock(
            message_list=message_list,
            system_message=system_message
        )
        return [response['output']['message']]
```

Based on the classification results, the FM determines the next tool to be invoked. The tool’s description and input schema define exactly what information needs to be extracted. Following the previous example, let’s assume the next page to be processed is a consultation note. The workflow will invoke the `extract_consultation_notes` function. This function processes documents to extract detailed medical information. Like the classification process discussed earlier, it first converts the documents to binary format suitable for model processing. The key to accurate extraction lies in how the images and system message are combined:

```
def extract_info(self, file_paths):
    # Convert documents to binary data
    # This will follow the same pattern to as in the classification function
    message_content = [
        {"image": {"format": media_type, "source": {"bytes": data}}}
        for data, media_type in binary_data_array
    ]

    message_list = [{
        "role": 'user',
        "content": [
            *message_content,  # Include the processed document images
            {"text": '''Extract all information from this file
                       If you find a visualization
                           - Provide a detailed description in natural language
                           - Use domain specific language for the description
                    '''}
        ]
    }]
    
    system_message = [{
        "text": '''You are a medical consultation agent with expertise in diagnosing and treating various health conditions.
                   You have a deep understanding of human anatomy, physiology, and medical knowledge across different specialties.
                   During the consultation, you review the patient's medical records, test results, and documentation provided.
                   You analyze this information objectively and make associations between the data and potential diagnoses.
Associate a confidence score to each extracted information. This should reflect how confident the model in the extracted value matched the requested entity.
        '''}
    ]
    
    response = self.bedrock_utils.invoke_bedrock(
        message_list=message_list,
        system_message=system_message
    )
    return [response['output']['message']]
```

The system message serves three crucial purposes:

- Establish medical domain expertise for accurate interpretation.
- Provide guidelines for handling different types of information (text and visualizations).
- Provide a self-scored confidence. Although this is not an independent grading mechanism, the score is directionally indicative of how confident the model is in its own extraction.

Following the same pattern, the FM will use the other tools in the `toolspec` definition to save and summarize the results.

A unique advantage of using a multi-modal FM for the extraction task is its ability to have a deep understanding of the text it is extracting. For example, the following code is an abstract of the data schema we are requesting as input to the `save_consultation_notes` function. Refer to the code in [constants.py](https://github.com/aws-samples/anthropic-on-aws/blob/main/medical-idp/utils/constants.py#L133) for full definition. The model needs to not only extract a transcript, but also understand it to extract such structured data from an unstructured document. This significantly reduces the postprocessing efforts required for the data to be consumed by a downstream application.

```
"consultation": {
                            "type": "object",
                            "properties": {
                            "date": {"type": "string"},
                            "concern": {
                                "type": "object",
                                "properties": {
                                    "primaryComplaint": {
                                        "type": "string",
                                        "description": "Primary medical complaint of the patient. Only capture the medical condition. no timelines"
                                    },
                                    "duration": {"type": "number"},
                                    "durationUnit": {"type": "string", "enum": ["days", "weeks", "months", "years"]},
                                    "associatedSymptoms": {
                                        "type": "object",
                                        "additionalProperties": {
                                            "type": "boolean"
                                        },
                                        "description": "Key-value pairs of symptoms and their presence (true) or absence (false)"
                                    },
                                    "absentSymptoms": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    }
                                },
                                "required": ["primaryComplaint", "duration", "durationUnit"]
                            }
```

The documents contain a treasure trove of personally identifiable information (PII) and personal health information (PIH). To redact this information, you can pass enable_guardrails as true. This will use the guardrail you setup earlier as part of the information extraction process and mask information identified as PII or PIH.

```
processor.process_file(prompt=prompt, 
                                        enable_guardrails=True,
                                        toolspecs=toolspecs,
      …
)
```

Finally, cross-document validation is crucial for maintaining data accuracy and compliance in healthcare settings. Although the current implementation performs basic consistency checks through the [summary prompt](https://github.com/aws-samples/anthropic-on-aws/blob/main/medical-idp/utils/constants.py#L35), organizations can extend the framework by implementing a dedicated validation tool that integrates with their specific business rules and compliance requirements. Such a tool could perform sophisticated validation logic like insurance policy verification, appointment date consistency checks, or any other domain-specific validation requirements, providing complete data integrity across the document package.

## Future considerations

As Amazon Bedrock continues to evolve, several powerful features can be integrated into this document processing workflow to enhance its enterprise readiness, performance, and cost-efficiency. Let’s explore how these advanced capabilities can take this solution to the next level:

- [Inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html) in Amazon Bedrock define a model and its associated Regions for routing invocation requests, enabling various tasks such as usage tracking, cost monitoring, and cross-Region inference. These profiles help users track metrics through [Amazon CloudWatch](https://aws.amazon.com/cloudwatch) logs, monitor costs with cost allocation tags, and increase throughput by distributing requests across multiple Regions.
- [Prompt caching](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html) can help when you have workloads with long and repeated contexts that are frequently reused for multiple queries. Instead of reprocessing the entire context for each document, the workflow can reuse cached prompts, which is particularly beneficial when using the same image across different tooling workflows. With support for multiple cache checkpoints, this feature can substantially reduce processing time and inference costs while maintaining the workflow’s intelligent orchestration capabilities.
- [Intelligent prompt routing](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html) can dynamically select the most appropriate model for each task based on performance and cost requirements. Rather than explicitly assigning Anthropic’s Claude 3 Haiku for orchestration and Anthropic’s Claude 3.5 Sonnet for document analysis, the workflow can use intelligent routing to automatically choose the optimal model within the Anthropic family for each request. This approach simplifies model management while providing cost-effective processing of different document types, from simple structured forms to complex handwritten notes, all through a single endpoint.

## Conclusion

This intelligent document processing solution demonstrates the power of combining Amazon Bedrock FMs with tool use capabilities to create sophisticated, self-orchestrating workflows. By using Anthropic’s Claude 3 Haiku for orchestration and Anthropic’s Claude 3.5 Sonnet for complex visual tasks, the solution effectively handles structured, semi-structured, and unstructured documents while maintaining high accuracy and compliance standards.

Key benefits of this approach include:

- Reduced manual processing through intelligent automation
- Improved accuracy through specialized model selection
- Built-in compliance with guardrails for sensitive data
- Flexible architecture that adapts to various document types
- Cost-effective processing through strategic model usage

As organizations continue to digitize their operations, solutions like this showcase how generative AI can transform traditional document processing workflows. The combination of powerful FMs in Amazon Bedrock and the tool use framework provides a robust foundation for building intelligent, scalable document processing solutions across industries.

For more information about Amazon Bedrock and its capabilities, visit the [Amazon Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html).

### About the Author

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/02/13/raju-rangan-ml-blog-profile.png)

**Raju Rangan** is a Senior Solutions Architect at AWS. He works with government-sponsored entities, helping them build AI/ML solutions using AWS. When not tinkering with cloud solutions, you’ll catch him hanging out with family or smashing birdies in a lively game of badminton with friends.
