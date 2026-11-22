---
vendor: aws_bedrock
title: Introducing structured output for Custom Model Import in Amazon Bedrock
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/introducing-structured-output-for-custom-model-import-in-amazon-bedrock
date: 2025-11-07
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 1e9248ac504b
---

# Introducing structured output for Custom Model Import in Amazon Bedrock

With [Amazon Bedrock](https://aws.amazon.com/bedrock/) [Custom Model Import](https://aws.amazon.com/bedrock/custom-model-import/), you can deploy and scale fine-tuned or proprietary foundation models in a fully managed, serverless environment. You can bring your own models into Amazon Bedrock, scale them securely without managing infrastructure, and integrate them with other Amazon Bedrock capabilities.

Today, we are excited to announce the addition of structured output to Custom Model Import. Structured output constrains a model’s generation process in real time so that every token it produces conforms to a schema you define. Rather than relying on prompt-engineering tricks or brittle post-processing scripts, you can now generate structured outputs directly at inference time.

For certain production applications, the predictability of model outputs is more important than their creative flexibility. A customer service chatbot might benefit from varied, natural-sounding responses, but an order processing system needs exact, structured data that conforms to predefined schemas. Structured output bridges this gap by maintaining the intelligence of foundation models while verifying their outputs meet strict formatting requirements.

This represents a shift from free-form text generation to outputs that are consistent, machine-readable, and designed for seamless integration with enterprise systems. While free-form text excels for human consumption, production applications require more precision. Businesses can’t afford the ambiguity of natural language variations when their systems depend on structured outputs to reliably interface with APIs, databases, and automated workflows.

In this post, you will learn how to implement structured output for Custom Model Import in Amazon Bedrock. We will cover what structured output is, how to enable it in your API calls, and how to apply it to real-world scenarios that require structured, predictable outputs.

## Understanding structured output

Structured output, also known as constrained decoding, is a method that directs LLM outputs to conform to a predefined schema, such as valid JSON. Rather than allowing the model to freely select tokens based on probability distributions, it introduces constraints during generation that limit choices to only those that maintain structural validity. If a particular token would violate the schema by producing invalid JSON, inserting stray characters, or using an unexpected field name the structured output rejects it and requires the model to select another allowed option. This real-time validation helps keep the final output consistent, machine readable, and immediately usable by downstream applications without the need for additional post-processing.

Without structured output, developers often attempt to enforce structure through prompt instructions like “*Respond only in JSON.*” While this approach sometimes works, it remains unreliable due to the inherently probabilistic nature of LLMs. These models generate text by sampling from probability distributions, introducing natural variability that makes responses feel human but creates significant challenges for automated systems.

Consider a customer support application that classifies tickets: if responses vary between “*This seems like a billing issue,*” “*I’d classify this as: Billing,*” and “*Category = BILLING,*” downstream code cannot reliably interpret the results. What production systems require instead is predictable, structured output. For example:

```
{
  "category": "billing",
  "priority": "high",
  "sentiment": "negative"
}
```

With a response like this, your application can automatically route tickets, trigger workflows, or update databases without human intervention. By providing predictable, schema-aligned responses, structured output transforms LLMs from conversational tools into reliable system components that can be integrated with databases, APIs, and business logic. This capability opens new possibilities for automation while maintaining the intelligent reasoning that underpin the value of these models.

Beyond improving reliability and simplifying post-processing, structured output offers additional benefits that strengthens performance, security and safety in production environments.

- **Lower token usage and faster responses:** By constraining generation to a defined schema, structured output removes unnecessary verbose, free-form text, resulting in reduced token count. Because token generation is sequential, shorter outputs directly translate to faster responses and lower latency, improving overall performance and cost efficiency.
- **Enhanced security against prompt injection:** Structured output narrows the model’s expression space and helps prevent it from producing arbitrary or unsafe content. Bad actors cannot inject instructions, code or unexpected text outside the defined structure. Each field must match its expected type and format, making sure outputs remain within safe boundaries.
- **Safety and policy controls:** Structured output enables you to design schemas that inherently help prevent harmful, toxic, or policy-violating content. By limiting fields to approved values, enforcing patterns, and restricting free-form text, schemas make sure outputs align with regulatory requirements.

In the next section, we will explore how structured output works with Custom Model Import in Amazon Bedrock and walks through an example of enabling it in your API calls.

## Using structured output with Custom Model Import in Amazon Bedrock

Let’s start by assuming you have already imported a Hugging Face model into Amazon Bedrock using the Custom Model Import feature.

### Prerequisites

Before proceeding, make sure you have:

- An active AWS account with access to Amazon Bedrock
- A custom model created in Amazon Bedrock using the Custom Model Import feature
- Appropriate [AWS Identity and Access Management (IAM)](https://aws.amazon.com/iam/) permissions to invoke models through the Amazon Bedrock Runtime

With these prerequisites in place, let’s explore how to implement structured output with your imported model.

To start using structured output with a Custom Model Import in Amazon Bedrock, begin by configuring your environment. In Python, this involves creating a Bedrock Runtime client and initializing a tokenizer from your imported Hugging Face model.

The Bedrock Runtime client provides access to your imported model using the Bedrock `InvokeModel` API. The tokenizer applies the correct chat template that aligns with the imported model, which defines how user, system, and assistant messages are combined into a single prompt, how the role markers (for example, `<|user|>`, `<|assistant|>`) are inserted, and where the model’s response should begin.

By calling `tokenizer.apply_chat_template(messages, tokenize=False)` you can generate a prompt that matches the exact input format your model expects, which is essential for consistent and reliable inference, especially when structured encoding is enabled.

```
import boto3
from transformers import AutoTokenizer
from botocore.config import Config

# HF model identifier imported into Bedrock
hf_model_id = "<<huggingface_model_id>>" # Example: "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B
model_arn = "arn:aws:bedrock:<<aws-region>>:<<account-id>>:imported-model/your-model-id"
region      = "<<aws-region>>"

# Initialize tokenizer aligned with your imported model 
tokenizer = AutoTokenizer.from_pretrained(hf_model_id)

# Initialize Bedrock client
bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name=region)
```

## Implementing structured output

When you invoke a custom model on Amazon Bedrock, you have the option to enable structured output by adding a `response_format` block to the request payload. This block accepts a JSON schema that defines the structured of the model’s response. During inference, the model enforces this schema in real-time, making sure that each generated token conforms to the defined structure. Below is a walkthrough demonstrating how to implement structured output using a simple address extraction task.

### Step 1: Define the data structure

You can define your expected output using a Pydantic model, which serves as a typed contract for the data you want to extract.

```
from pydantic import BaseModel, Field

class Address(BaseModel):
    street_number: str = Field(description="Street number")
    street_name: str = Field(description="Street name including type (Ave, St, Rd, etc.)")
    city: str = Field(description="City name")
    state: str = Field(description="Two-letter state abbreviation")
    zip_code: str = Field(description="5-digit ZIP code")
```

### Step 2: Generate the JSON schema

Pydantic can automatically convert your data model into a JSON schema:

```
schema = Address.model_json_schema()
address_schema = {
    "name": "Address",
    "schema": schema
}
```

This schema defines each field’s type, description, and requirement, creating a blueprint that the model will follow during generation.

### Step 3: Prepare your input messages

Format your input using the chat format expected by your model:

```
messages = [{
    "role": "user",
    "content": "Extract the address: 456 Tech Boulevard, San Francisco, CA 94105"
}]
```

### Step 4: Apply the chat template

Use your model’s tokenizer to generate the formatted prompt:

```
prompt = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)
```

### Step 5: Build the request payload

Create your request body, including the `response_format` that references your schema:

```
request_body = {
    'prompt': prompt,
    'temperature': 0.1,
    'max_gen_len': 1000,
    'top_p': 0.9,
    'response_format': {
        "type": "json_schema",
        "json_schema": address_schema
    }
}
```

### Step 6: Invoke the model

Send the request using the `InvokeModel` API:

```
response = bedrock_runtime.invoke_model(
    modelId=model_arn,
    body=json.dumps(request_body),
    accept="application/json",
    contentType="application/json"
)
```

### Step 7: Parse the response

Extract the generated text from the response:

```
result = json.loads(response['body'].read().decode('utf-8'))
raw_output = result['choices'][0]['text']
print(raw_output)
```

Because the schema defines required fields, the model’s response will contain them:

```
{
"street_number": "456",
"street_name": "Tech Boulevard",
"city": "San Francisco",
"state": "CA",
"zip_code": "94105"
}
```

The output is clean, valid JSON that can be consumed directly by your application with no extra parsing, filtering, or cleanup required.

## Conclusion

Structured output with Custom Model Import in Amazon Bedrock provides an effective way to generate structures, schema-aligned outputs from your models. By shifting validation into the model inference itself, structured output reduce the need for complex post-processing workflows and error handling code.

Structured output generates outputs that are predictable and straightforward to integrate into your systems and supports a variety of use cases, for example, building financial applications that require precise data extraction, healthcare systems that need structured clinical documentation, or customer service systems that demand consistent ticket classification.

Start experimenting with structured output with your [Custom Model Import](https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-import-model.html) today and transform how your AI applications deliver consistent, production-ready results.

### About the authors

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/07/07/manoj.png)Manoj Selvakumar** is a Generative AI Specialist Solutions Architect at AWS, where he helps organizations design, prototype, and scale AI-powered solutions in the cloud. With expertise in deep learning, scalable cloud-native systems, and multi-agent orchestration, he focuses on turning emerging innovations into production-ready architectures that drive measurable business value. He is passionate about making complex AI concepts practical and enabling customers to innovate responsibly at scale—from early experimentation to enterprise deployment. Before joining AWS, Manoj worked in consulting, delivering data science and AI solutions for enterprise clients, building end-to-end machine learning systems supported by strong MLOps practices for training, deployment, and monitoring in production.

[![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/06/16/yanyan.png)](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/06/16/yanyan.png)**Yanyan Zhang** is a Senior Generative AI Data Scientist at Amazon Web Services, where she has been working on cutting-edge AI/ML technologies as a Generative AI Specialist, helping customers use generative AI to achieve their desired outcomes. Yanyan graduated from Texas A&M University with a PhD in Electrical Engineering. Outside of work, she loves traveling, working out, and exploring new things.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/13/ravi.png)**Lokeshwaran Ravi** is a Senior Deep Learning Compiler Engineer at AWS, specializing in ML optimization, model acceleration, and AI security. He focuses on enhancing efficiency, reducing costs, and building secure ecosystems to democratize AI technologies, making cutting-edge ML accessible and impactful across industries.

**![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/09/11/image-8-4-100x133.png)Revendra Kumar** is a Senior Software Development Engineer at Amazon Web Services. In his current role, he focuses on model hosting and inference MLOps on Amazon Bedrock. Prior to this, he worked as an engineer on hosting Quantum computers on the cloud and developing infrastructure solutions for on-premises cloud environments. Outside of his professional pursuits, Revendra enjoys staying active by playing tennis and hiking.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/11/06/image-23-100x100.png)**Muzart Tuman** is a software engineer utilizing his experience in fields like deep learning, machine learning optimization, and AI-driven applications to help solve real-world problems in a scalable, efficient, and accessible manner. His goal is to create impactful tools that not only advance technical capabilities but also inspire meaningful change across industries and communities.
