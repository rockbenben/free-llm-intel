---
vendor: aws_bedrock
title: Build an agentic solution with Amazon Nova, Snowflake, and LangGraph
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-an-agentic-solution-with-amazon-nova-snowflake-and-langgraph
date: 2025-11-19
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: e723b0b916c4
---

# Build an agentic solution with Amazon Nova, Snowflake, and LangGraph

*This post was written with Bharath Suresh and Mary Law from Snowflake.*

[Agentic AI](https://aws.amazon.com/ai/agentic-ai/) is a type of AI that functions autonomously, automating a broader range of tasks with minimal supervision. It combines traditional AI and [generative AI](https://aws.amazon.com/generative-ai/) capabilities to make decisions, perform tasks, and adapt to its environment without constant human intervention. These autonomous systems can plan, reason, and take actions to achieve specific goals. The following diagram, taken from [A Practical Guide to AI Agents](https://www.snowflake.com/wp-content/uploads/2025/03/A-Practical-Guide-to-AI-Agents-1.pdf), shows the flow of these autonomous actions.

![Visual representation of AI agent workflow with six connected blue circles showing progression from input sensing to continuous learning](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/17/ml-18769-image-1.png)

In this post, we cover how you can use tools from [Snowflake](https://www.snowflake.com/en/) AI Data Cloud and [Amazon Web Services](https://aws.amazon.com/) (AWS) to build generative AI solutions that organizations can use to make data-driven decisions, increase operational efficiency, and ultimately gain a competitive edge.

Snowflake is an [AWS Competency Partner](https://partners.amazonaws.com/partners/001E000000d8qQcIAI/Snowflake) with multiple AWS Competencies including Generative AI, Data & Analytics, Machine Learning, and Retail independent software vendor (ISV). Snowflake is [available in the AWS Marketplace](https://partners.amazonaws.com/partners/001E000000d8qQcIAI/Snowflake). Snowflake builds tools for every organization to mobilize their data, unify siloed data, and discover and securely share data. Snowflake brings AI to governed data, enabling teams to run analytical workflows on unstructured data, develop agentic applications, and train models using both structured and unstructured data with minimal operational overhead and end-to-end governance. Snowflake is a strong AWS Partner, available in [over 20 AWS Regions](https://docs.snowflake.com/en/user-guide/intro-regions), offering a wide range of support and integration with AWS services. This includes features such as [AWS PrivateLink](https://aws.amazon.com/privatelink/) for secure connectivity and Snowpipe for automated data loading from [Amazon Simple Storage Service](https://aws.amazon.com/s3/) (Amazon S3), [AWS Glue](https://aws.amazon.com/glue/) for data cataloging, and model development with [Amazon SageMaker](https://aws.amazon.com/sagemaker/). Snowflake has received Amazon SageMaker Ready Product service validation.

## The business challenge

Traditional vehicle insurance claim processing involves several stages, from manually validating documents such as driver’s licenses, claim forms, and car damage images. This manual workflow is often siloed and prone to errors. In this post, we demonstrate an agentic AI workflow that automates this end-to-end process. This sample demonstrates the art of the possible while improving operational efficiency and scalability, reducing human errors, and enabling informed decision-making. The sample solution involves the following key services:

- **[Snowflake](https://partners.amazonaws.com/partners/001E000000d8qQcIAI/Snowflake)** – The AI Data Cloud. A unified platform that eliminates data silos and makes data and AI straightforward, connected, and trusted.
- **[Snowflake Document AI](https://docs.snowflake.com/en/user-guide/snowflake-cortex/document-ai/overview)** – AI feature that uses Arctic-TILT, a proprietary [large language model](https://aws.amazon.com/what-is/large-language-model/) (LLM), to extract data from documents. Document AI is best used to turn unstructured data from documents into structured data in tables. Refer to [Document AI availability](https://docs.snowflake.com/en/user-guide/snowflake-cortex/document-ai/limitations.html#label-document-ai-availability).
- **[Streamlit](https://streamlit.io/)** in Snowflake is an open source Python library that makes it seamless to create and share custom web apps for [machine learning](https://aws.amazon.com/ai/machine-learning/) (ML) and data science. By using Streamlit, you can quickly build and deploy powerful data applications. For additional use cases on building dashboards, data tools, and [artificial intelligence and machine learning](https://aws.amazon.com/training/learn-about/machine-learning/) (AI/ML), refer to [Streamlit in Snowflake demos](https://github.com/Snowflake-Labs/snowflake-demo-streamlit).
- **[Amazon Bedrock](https://aws.amazon.com/bedrock)** – A fully managed service to build generative AI applications, offering a choice of high-performing [foundation models](https://aws.amazon.com/what-is/foundation-models/) (FMs) from leading AI companies. [Amazon Nova Lite](https://aws.amazon.com/ai/generative-ai/nova/) is a low-cost multimodal model that is lightning fast for processing image, video, and text input.
- **[LangGraph](https://www.langchain.com/langgraph)** – A stateful, orchestration framework that brings added control to agent workflows.

The demonstration of the solution is shown in the following video.

![](https://d2908q01vomqb2.cloudfront.net/artifacts/DBSBlogs/ML-18769/ml-18769-image-2.gif)

## Solution overview

![Insurance claim workflow using AWS services including S3, Textract, and Step Functions for document processing](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/11/13/ml-18769-image-2.1-1.png)

This solution implements a fully autonomous, explainable workflow for vehicle insurance claim processing using an agentic AI architecture. At its core, the pipeline combines structured document extraction, multimodal image analysis, policy validation, and natural language generation, chained together using a stateful LangGraph workflow and surfaced through an interactive Streamlit UI. Here’s how the end-to-end flow works at a high level:

- The user uploads three essential artifacts:  A scanned driver’s license (DL) A filled-out claim form (PDF or image) A car damage photo
- The uploaded license and claim documents are processed using Snowflake’s Cortex Document AI models (`LICENSE_DATA` and `CLAIMS_DATA`). These models extract structured fields such as name, DL number, vehicle details, and the incident date, all with zero-shot or fine-tuned inference.
- The car damage photo is analyzed by Amazon Nova Lite through Amazon Bedrock. The image and a text prompt are passed to the model, which returns a professional summary of visible damage, car type, make, and color. This adds unstructured image insight into the reasoning process.
- Extracted values from the license, claim, and image are cross-checked for consistency (for example, name match, DL number, vehicle color) and verified against Snowflake policy records (for example, customer profile, VIN, policy expiration). This confirms the claim is authentic and eligible.
- The incident date from the claim is compared to the policy end date retrieved from Snowflake. Claims outside the policy window are flagged automatically.
- A decision is made based on match accuracy and policy status. The system compiles the comparison summary and generates a customer-facing decision email using natural language generation in Amazon Nova Lite.
- All stages are linked as nodes in a LangGraph state machine, where each node processes the shared workflow state and passes it forward. This structure provides modularity, auditability, and deterministic control.
- The final outputs—including workflow steps, decision status, matched values, and the email—are displayed to the user in real time through a Streamlit UI. A debugging expander reveals full raw JSON data from each extraction stage.

This solution showcases how multiple AI components—document understanding, multimodal reasoning, and generation of custom models—can be tightly integrated into a single pipeline that autonomously perceives, reasons, and acts. The solution workflow follows these steps:

- The user submits all the documents to Streamlit apps.
- The user uploads documents such as incident photos, driver’s licenses, and insurance claim forms to Snowflake Stage.
- Snowflake Document AI is used to extract data from the insurance claim form.
- Amazon Nova Lite in Amazon Bedrock is used to compare the extracted claims data for authenticity.
- Amazon Nova Lite in Amazon Bedrock analyzes car images to identify damage details.
- The system combines the outcomes from the previous steps to decide the claim.
- An email is drafted to the customer informing them of the decision.
- Workflow information and the decision are sent to the user through email.

These steps are shown in the following diagram.

![End-to-end insurance claim architecture showing document analysis, data processing, and automated decision workflow](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/11/13/ml-18769-image-2.2-1.png)

## Prerequisites

To implement the solution provided in this post, you need the following:

- **Snowflake account** – Active account with permissions, Snowflake SQL or Snowsight familiarity, and Cortex Document AI enabled.
- **AWS account** – Active account with Amazon Bedrock access, including access to Amazon Nova Lite, and configured AWS credentials.
- **Python environment** – Python 3.x and required packages installed.
- **GitHub access** – Clone the provided [GitHub repository](https://github.com/Snowflake-Labs/sf-samples/tree/main/samples/vehicle-insurance-agentic-ai). This repository provides a comprehensive understanding of how each component integrates and functions together seamlessly through a LangGraph-powered state machine, from document upload and extraction to validation.
- **Document preparation** – Sample driver’s license images, claim form PDFs, and car damage images with relevant data.
- **Snowflake data setup** – A ``customer_policy_view`` table or view with policyholder data (`customer ID`, `VIN`, and `POLICY_END`) and sample data.
- **Snowflake Document AI model builds** – Two models in Snowsight for licenses and claims, trained and published for prediction.
- **Amazon Bedrock configuration** – AWS credentials set up for Python to access FMs in Amazon Bedrock models.

## **Documents used**

To simulate a realistic insurance claim scenario for this agentic AI workflow, we prepared three representative input documents that align with how real users might file claims. The dataset includes:

- A driver’s license (DL) showing name, DL number, date of birth, address, and license validity date, as shown in the following image

![Mock California driver's license displaying layout, bear logo, and basic information fields with placeholder data](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/17/ml-18769-image-3.png)

- A completed claim form (PDF) capturing customer ID, vehicle details, accident description, and incident date, as shown in the following image

![Comprehensive motor insurance claim form template displaying policy details, incident documentation fields, and declaration section for third-party accidents](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/17/ml-18769-image-4.png)

- Photographs showing damage to the vehicle, as shown in the following image

![Green sedan with visible front collision damage displayed in automotive repair lot, showing extent of hood and bumper impact](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/17/ml-18769-image-6.png)![Significant impact damage visible on vehicle's front end, showing crumpled bodywork and misaligned panels](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/17/ml-18769-image-5.png)

The car damage images used in this are sourced from [car damage dataset](https://www.kaggle.com/datasets/lplenka/coco-car-damage-detection-dataset).

## **Document processing**

This sample solution uses Snowflake Document AI, powered by the proprietary Arctic-TILT LLM, to extract information from uploaded documents with impressive flexibility. For information about getting started with Document AI, visit [Setting up Document AI](https://docs.snowflake.com/en/user-guide/snowflake-cortex/document-ai/setting-up).

We created two Document AI model builds in Snowsight—one for driver’s licenses and one for claim forms—using Snowflake’s `DOCUMENT_INTELLIGENCE` class powered by the Arctic-TILT LLM. For each model, we uploaded sample documents, defined extraction fields using natural language prompts (for example, “What is the license number?”), reviewed confidence-scored results, and published the models for use using the `MODEL_NAME!PREDICT(GET_PRESIGNED_URL(...))` SQL syntax. This enabled zero-shot extraction in the pipeline without requiring retraining for every new file. The following diagram shows the workflow for document processing.

![End-to-end Document AI workflow diagram illustrating model creation, training, document upload, query building and automated processing pipeline](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/17/ml-18769-image-7.png)

Uploaded documents go through specialized AI-driven processing. Licenses are parsed using LICENSE_DATA!PREDICT for fields such as name and DL number. Claims are parsed using CLAIMS_DATA!PREDICT for vehicle and incident details (including inferred vehicle color).

Car images are analyzed by the Amazon Nova Lite model on Amazon Bedrock to extract structured damage details. This multi-modal extraction layer transforms raw inputs into structured insights for downstream decisioning.

### **Preparing the Document AI models in Snowsight**

To extract information from unstructured documents such as driver’s licenses and insurance claim forms, we use Snowflake’s Document AI. We’ve created two model builds—`LICENSE_DATA` and `CLAIMS_DATA`—each designed to extract specific fields using natural language prompts. After signing into Snowsight with the appropriate role, we choose **AI & ML** and **Document AI **in the left navigation pane. Then we create a new build and upload sample documents.

Each file passes through optical character recognition (OCR), after which we define fields by pairing value names with extraction questions. We then receive confidence-scored answers, which we review and confirm. When accuracy is satisfactory, we publish the models, making them callable from SQL using the `MODEL_NAME!PREDICT(GET_PRESIGNED_URL(...))` syntax. For improved precision, we have the option to fine-tune the models using reviewed documents. This setup enables robust, zero-shot field extraction from real-world forms—no custom ML pipeline required.

After creating and training the Document AI models in Snowsight (for example, ``LICENSE_DATA`` and ``CLAIMS_DATA``) and ensuring they’re published and ready for predictions using ``MODEL_NAME!PREDICT(GET_PRESIGNED_URL(...))``, we transition to using Python code to process the rest of the workflow. The Python code will handle the orchestration, data retrieval, LLM interactions, and decision-making steps required to complete the insurance claim processing pipeline.

The following video shows this process.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/11/17/ml-18769-image-8-1.gif)

### **Amazon Nova Lite for car damage analysis**

To evaluate vehicle damage from incident images, we use Amazon Nova Lite in AWS Bedrock, a high-performance, low-latency multimodal FM. Nova Lite enables our agentic workflow to interpret unstructured image data—such as car photos—using a single natural language prompt, without the need for specialized computer vision models.

After the image is uploaded through the Streamlit interface, it’s encoded in base64 and wrapped in a multimodal prompt. We simulate a professional damage inspection scenario by sending both the image and a textual instruction to the model. Here’s the actual logic used in our backend:

```
with open(path, "rb") as image_file:
    binary_data = image_file.read()
    base64_string = base64.b64encode(binary_data).decode("utf-8")
client = boto3.client("bedrock-runtime", region_name="us-east-1")
model_id = "us.amazon.nova-lite-v1:0"
system_list = [{
    "text": "You are an expert car inspector. When provided with a car accident photo, return a technical summary describing the vehicle and any visible damage."
}]
message_list = [{
    "role": "user",
    "content": [
        {
            "image": {
                "format": ext,
                "source": {"bytes": base64_string}
            }
        },
        {
            "text": "Please inspect this damaged car image and return a summary of the damage and car type in professional language."
        }
    ],
}]
native_request = {
    "schemaVersion": "messages-v1",
    "messages": message_list,
    "system": system_list,
    "inferenceConfig": {"maxTokens": 500, "topP": 0.1, "topK": 20, "temperature": 0.3}
}
The invoke_model() method then sends this payload to Bedrock:
response = client.invoke_model(
    modelId=model_id,
    body=json.dumps(native_request),
    accept="application/json",
    contentType="application/json"
)
```

The model returns a natural language response, such as:

```
The vehicle appears to be a hatchback with moderate rear-end collision damage. There are visible dents around the rear bumper. The car is likely a dark purple Ford Focus.
```

We store this summary as part of the `car` object in the shared workflow state:

```
model_response = json.loads(response["body"].read())
content_text = model_response["output"]["message"]["content"][0]["text"]
car_data = {
    "visible_damage": content_text
}
```

By using the multimodal capabilities in Amazon Nova Lite, we significantly reduce the complexity of image processing and avoid the need for training and maintaining separate image recognition models. This step adds visual intelligence to the agentic pipeline—enabling more complete and human-aligned assessments of insurance claims.

## **Cross-document comparison and policy validation with Amazon Nova**

After extracting data from the driver’s license, claim form, and car image, the agentic AI workflow verifies the consistency and authenticity of the information. This is done through cross-document comparison and a policy validation check against Snowflake’s records.

First, we identify the customer using the name extracted from the claim form. We query a Snowflake view (`customer_policy_view`) to retrieve the associated customer ID. Then, we join this view with the `DRIVER_LICENSES` table to fetch reference fields such as color, make and model, date of birth, license number, and the policy end date.

Here’s the actual SQL logic used in the workflow:

```
df_id = session.sql(f"""
    SELECT CUSTOMER_ID FROM customer_policy_view
    WHERE LOWER(NAME) = '{extracted_name.lower()}'
""").to_pandas()
df = session.sql(f"""
    SELECT
        cpv.NAME,
        cpv.COLOR,
        cpv.MAKE_MODEL,
        cpv.POLICY_END,
        dl.LICENSE_NO,
        dl.DOB
    FROM
        customer_policy_view cpv
    JOIN
        DRIVER_LICENSES dl ON LOWER(cpv.NAME) = LOWER(dl.NAME)
    WHERE
        cpv.CUSTOMER_ID = '{customer_id}'
""").to_pandas()
```

Next, we compare each extracted value from the documents with its counterpart from the database. Fields compared include:

- `full_name`
- `dl_no`
- `dob`
- `vehicle_color`
- `make_model`

Each comparison returns a match status (`true` or `false`) and both the extracted and reference values so we can trace mismatches clearly. The comparison dictionary is structured like this:

```
comparison = {
    "full_name": {
        "match": extracted_name.lower() == db_name.lower(),
        "claim_value": extracted_name,
        "db_value": db_name
    },
    ...
}
```

We then validate the policy’s active status by comparing the incident date from the claim against the policy end date from Snowflake:

```
incident_date = datetime.strptime(claim.get("date_of_incident", [{}])[0].get("value"), "%Y-%m-%d").date()
valid = incident_date and db_policy_end_date_obj and incident_date <= db_policy_end_date_obj
decision = "✅ Claim Accepted" if valid else "❌ Claim Rejected due to expired policy"
```

This dual-layer validation helps make the claim both factually accurate and legally valid. Critical mismatches (such as an invalid DL number or expired policy) lead to automatic rejection, whereas verified matches and in-policy incidents result in acceptance.

By performing this reasoning step entirely in Python using structured comparison logic, we maintain full transparency, flexibility, and auditability—crucial for enterprise insurance systems.

## **Autonomous reasoning and claim decision with Amazon Nova**

With all relevant data extracted and validated—across the driver’s license, claim form, car photo, and policy database—the final step in the workflow is to reason over the full context and generate a clear, professional claim decision. This is where Amazon Nova Lite steps in again, this time as a logic processor and natural language generator.

We craft a structured prompt that provides Amazon Nova Lite with all the evidence gathered so far, including field-level comparison results, the policy end date, the date of the incident, and a computed decision flag (accepted or rejected). Here’s how the decision logic is computed in Python: `decision = "✅ Claim Accepted" if valid else "❌ Claim Rejected due to expired policy"`

We then prepare a human-readable reasoning prompt that summarizes the situation:

```
email_prompt = f"""Write a short professional email to a customer summarizing their insurance claim review.
Comparison:
{json.dumps(comparison, indent=2)}
Incident Date: {incident_date}
Policy End: {db_policy_end_date_obj}
Decision: {decision}
"""
```

This prompt is passed to Amazon Nova Lite using the Amazon Bedrock Runtime API. Nova Lite interprets the full context and generates a clear message tailored to the customer:

```
body = {
    "schemaVersion": "messages-v1",
    "messages": [{"role": "user", "content": [{"text": email_prompt}]}],
    "inferenceConfig": {"maxTokens": 1000}
}
email_response = bedrock.invoke_model(
    body=json.dumps(body),
    modelId="us.amazon.nova-lite-v1:0",
    accept="application/json",
    contentType="application/json"
)
```

The response might look like this:

```
Dear Steven, we have completed the review of your insurance claim submitted on February 14, 2025. Based on our evaluation, your documents have been successfully verified and the incident falls within your active policy period. We’re pleased to inform you that your claim has been accepted.
```

This output is stored in the workflow state alongside the structured decision and comparison result. For all outcomes, in the final step in our agentic application, the system will automatically generate a customer-ready message without human involvement.

By using Amazon Nova Lite for multimodal inputs and autonomous decision communication, we close the loop of an intelligent, self-reasoning workflow that mimics the judgment and empathy of a human insurance adjuster, and it can do this at scale.

### **Final output example**

After processing the uploaded documents, analyzing the car image, validating extracted fields, and confirming policy eligibility, the agentic AI workflow produces a structured and interpretable output that includes comparison results across documents and Snowflake records, a claim decision (accepted or rejected), and a customer-facing email generated by Amazon Nova Lite. Here’s an example of a complete output from a successful claim:

```
{
  "decision": "✅ Claim Accepted",
  "comparison": {
    "full_name": {
      "match": true,
      "claim_value": "Steven Smith",
      "db_value": "Steven Smith"
    },
    "dl_no": {
      "match": true,
      "claim_value": "DL-2605979475",
      "db_value": "DL-2605979475"
    },
    "dob": {
      "match": true,
      "claim_value": "1991-08-15",
      "db_value": "1991-08-15"
    },
    "vehicle_color": {
      "match": true,
      "claim_value": "Purple",
      "db_value": "Dark Purple"
    },
    "make_model": {
      "match": true,
      "claim_value": "Ford Focus",
      "db_value": "Ford Focus Titanium"
    }
  },
  "email": "Dear Steven, we have completed the review of your insurance claim submitted on February 14, 2025. Based on our evaluation, your documents have been successfully verified and the incident falls within your active policy period. We’re pleased to inform you that your claim has been accepted. You will receive a follow-up with next steps shortly. Thank you for choosing our services."
}
```

This output showcases the full power of the pipeline, with ground truth from Snowflake, intelligent extraction with Document AI, multimodal reasoning using Amazon Nova Lite, and decision explanation in natural language.

The structured format makes it straightforward to audit, log, or integrate with downstream systems such as customer relationship management (CRM) systems, email workflows, or insurance management platforms. More importantly, it closes the loop on trustable, explainable AI in production.

## **How the agentic AI workflow is automated**

The entire vehicle insurance claim processing pipeline is implemented as an agentic AI workflow, in which each stage observes inputs, applies reasoning, makes decisions using LLMs, and forwards context to the next stage. This is orchestrated using LangGraph, a stateful workflow engine that treats each task as a modular node and passes a shared state throughout the graph.

At the heart of this automation is a LangGraph state machine, where major processing stages such as document extraction, car image analysis, and final claim decision are defined as nodes. These nodes are connected through directed edges to form a sequential and explainable pipeline:

```
builder = StateGraph(WorkflowState)
builder.add_node("upload", upload_all)
builder.add_node("extract_dl", extract_dl)
builder.add_node("extract_claim", extract_claim)
builder.add_node("extract_car", extract_car)
builder.add_node("compare_email", compare_and_email)
```

Each function takes in the current state, performs its designated task—such as running LLM inference or querying Snowflake—and returns updated state information. Here’s how each step contributes:

- **Document upload and staging **– The `upload_all` node handles file uploads from the Streamlit frontend and stages them into a Snowflake internal stage using:

`session.file.put(local_path, STAGE_NAME, overwrite=True)`

- **Document extraction with Document AI **– Both `extract_dl` and `extract_claim` nodes invoke Snowflake Document AI using zero-shot prediction with presigned URLs:

`sql = f"SELECT LICENSE_DATA!PREDICT(GET_PRESIGNED_URL(@doc_ai_stage, '{path}'), 2)"`

- **Multimodal car image analysis (Amazon Nova Lite) **– The `extract_car` node sends a structured prompt and the Base64-encoded image to Amazon Nova Lite. Although the reference version returns detailed JSON fields such as make and model, the current implementation uses natural language summaries for damage inspection.
- **Cross-document reasoning and comparison **– The `compare_and_email` node performs the reasoning phase by comparing extracted values from:  Driver’s license and claim (name, DL number) Car image and claim (vehicle color, make and model) Claim and Snowflake policy (policy dates)
- These are organized into a structured prompt and passed to Amazon Nova Lite. The output is parsed into a `comparison` dictionary for downstream decision-making.
- **Policy validity check (Snowflake SQL)** – Still within the same node, a SQL query retrieves policy records:

`SELECT VEHICLE_NUMBER, POLICY_END FROM customer_policy_view WHERE customer_id = '{customer_id}'`

- It then checks if the claim’s incident date falls within the policy’s active period.
- **Claim decision and email generation **– A claim is either accepted or rejected based on field-level and date-level validation:

`decision = "✅ Claim Accepted" if incident_date <= policy_end_date else "❌ Claim Rejected"`

- This result, along with the comparison context, is used to construct a customer-facing email using Amazon Nova Lite.
- **Agentic state chaining** – The flow is linked through directed edges in the graph:

```
builder.set_entry_point("upload")
builder.add_edge("upload", "extract_dl")
builder.add_edge("extract_dl", "extract_claim")
builder.add_edge("extract_claim", "extract_car")
builder.add_edge("extract_car", "compare_email")
builder.add_edge("compare_email", END)
```

Each node augments the state with new observations and decisions, enabling the pipeline to autonomously perceive, reason, and act—the hallmarks of an agentic AI system.

## **Interactive frontend with Streamlit**

To make the workflow accessible and intuitive, we built a clean user-facing frontend using Streamlit, a popular open source Python framework for rapid UI prototyping and data apps. Streamlit app users can upload their claim-related documents and get real-time outputs including claim validation, policy decision, and a generated customer-facing email.

The Streamlit interface starts by requesting three required documents: a scanned driver’s license, the claim form (PDF or image), and a car damage photo. These are captured through `file_uploader` widgets with format restrictions to ensure valid input:

```
dl_file = st.file_uploader("Driver's License", type=["jpg", "jpeg", "png", "pdf"])
claim_file = st.file_uploader("Claim Document", type=["jpg", "jpeg", "png", "pdf"])
car_file = st.file_uploader("Car Damage Photo", type=["jpg", "jpeg", "png", "pdf"])
```

After all documents are uploaded, users choose a button to initiate the backend pipeline, which calls the LangGraph-powered function `run_claim_processing_workflow()`:

```
if st.button("Run Claim Workflow"):
    result = run_claim_processing_workflow({
        "dl": dl_file,
        "claim": claim_file,
        "car": car_file
    })
```

A spinner is shown while the workflow executes, and errors are surfaced immediately to the UI for troubleshooting.

When the workflow is complete, the UI displays the results in structured sections for workflow steps that were completed, a field-level comparison output, a policy validity result, and a

final customer email generated by Amazon Nova Lite. These results are rendered using `st.markdown()` and `st.json()` for easy interpretation:

```
st.markdown("### Workflow Steps")
for step in result.get("steps", []):
    st.markdown(f"✅ {step}")
st.markdown("### Document Comparison")
st.json(result.get("comparison", {}))
st.markdown("### Policy Validity")
st.markdown(result.get("decision"))
st.markdown("### Final Email")
st.code(result.get("email"))
```

For developers or quality assurance (QA) teams, a collapsible section provides access to raw JSON outputs extracted from the driver’s license, claim form, and car image:

```
with st.expander("Raw Data"):
    st.json(result.get("dl", {}))
    st.json(result.get("claim", {}))
    st.json(result.get("car", {}))
```

This provides full transparency across all AI-driven decisions and supports auditability, a critical feature in regulated industries such as insurance.

## **Cleanup**

After the demo, perform the following cleanup steps:

- Snowflake cleanup:  (Optional) Truncate or drop the ``customer_policy_view`` table or view if it was created solely for the demo. Consider deleting the Document AI models (`LICENSE_DATA` and `CLAIMS_DATA`) if they’re no longer needed. Remove files uploaded to the internal stage (``doc_ai_stage``)
- AWS cleanup:  If temporary AWS resources were created, delete them. Amazon Bedrock model access typically doesn’t require cleanup, but temporary [AWS Identity and Access Management](https://aws.amazon.com/iam/) (IAM) roles or policies should be removed if they were created.

Following these setup and cleanup steps provides a smooth demo experience and a clean environment afterward.

## **Conclusion**

This project demonstrates the potential of agentic AI workflows in managing real-world, document-centric processes, using vehicle insurance claim validation as a case study. The system executes complex workflows across multiple tasks and data streams, orchestrating operations without constant human supervision. By integrating Snowflake’s Document AI, the multimodal and reasoning models of Amazon Bedrock and Amazon Nova Lite, and orchestration by LangGraph, we’ve created a robust, explainable, and production-ready solution capable of autonomous perception, reasoning, and action.

From structured document extraction to visual damage understanding, cross-document comparison, policy lookup, and natural language email drafting — each step of the pipeline behaves as a specialized agent contributing to the overall goal. LangGraph’s stateful workflow design makes it easy to extend this further with more capabilities such as fraud detection, document classification, or vendor coordination.

This isn’t merely an insurance app, it’s a template for building next-generation AI systems that reason across modalities, interact with enterprise data, and execute with autonomy. These modular, explainable workflows will be essential for implementing AI in real-world business processes as agentic AI becomes more prevalent. Agentic AI has the potential to increase efficiency, improve decision-making, accelerate time to market, raise customer satisfaction, and create more opportunities for innovation.

## Resources

- Refer to [Amazon Nova Foundation Models](https://aws.amazon.com/ai/generative-ai/nova/) for more information and to get started with Amazon Nova.
- Try Snowflake for a no cost [30-day trial](https://aws.amazon.com/marketplace/saas/ordering?productId=106ff316-230f-4ad7-9d64-91e400266426&tryForFree=true) in AWS Marketplace. Watch this [AWS and Snowflake Better Together webinar](https://www.snowflake.com/en/resources/webinar/snowflake-on-snowflake/modern-revenue-automation/thankyou/).
- To learn more and get hands-on resources to start using Snowflake’s generative AI, visit [Snowflake for AI](https://www.snowflake.com/en/product/ai/) and [download “A Practical Guide to AI Agents”](https://www.snowflake.com/resource/a-practical-guide-to-ai-agents/).

### About the Authors

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/30/ml-18769-image-8-BharathSuresh-1.jpeg)**Bharath Suresh** is a Senior Solutions Engineer at Snowflake and former Amazon Web Services (AWS) and IBM Architect with over 15 years of experience in cloud architecture, data platforms, and AI-driven solutions across global enterprises. At Snowflake, he empowers customers to modernize data and AI workloads, with a focus on agentic workflows, governance, and multi-cloud transformation.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/30/Mary-1-1.jpg)**Mary Law** is an APJ Partner Tech Lead at Snowflake, the AI Data Cloud. Her background includes leading the APJ Analytics Acceleration Lab at AWS and Data & AI specialist roles at Microsoft. This journey through different cloud ecosystems gives Mary unique insights into solving complex data challenges. She is passionate about helping partners develop solutions that deliver real business value.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/10/30/ml-18769-image-10-aamantle-2.jpeg)**Amelia Mantle** is an Associate Solutions Architect at Amazon Web Services (AWS). With a background in data science, Amelia continues to help customers develop AI/ML solutions in the cloud. She serves as a trusted AI advisor to organizations navigating their digital transformation journey, working closely with AWS partners and customers to architect and implement innovative AI services.
