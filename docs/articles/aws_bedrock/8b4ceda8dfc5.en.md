---
vendor: aws_bedrock
title: Reducing hallucinations in large language models with custom intervention using Amazon Bedrock Agents
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/reducing-hallucinations-in-large-language-models-with-custom-intervention-using-amazon-bedrock-agents
date: 2024-11-26
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 73c5e8061399
---

# Reducing hallucinations in large language models with custom intervention using Amazon Bedrock Agents

[Hallucinations](https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)) in large language models (LLMs) refer to the phenomenon where the LLM generates an output that is plausible but factually incorrect or made-up. This can occur when the model’s training data lacks the necessary information or when the model attempts to generate coherent responses by making logical inferences beyond its actual knowledge. Hallucinations arise because of the inherent limitations of the [language modeling](https://h2o.ai/wiki/language-modeling/) approach, which aims to produce fluent and contextually appropriate text without necessarily ensuring factual accuracy.

Remediating hallucinations is crucial for production applications that use LLMs, particularly in domains where incorrect information can have serious consequences, such as healthcare, finance, or legal applications. Unchecked hallucinations can undermine the reliability and trustworthiness of the system, leading to potential harm or legal liabilities. Strategies to mitigate hallucinations can include rigorous fact-checking mechanisms, integrating external knowledge sources using [Retrieval Augmented Generation (RAG),](https://aws.amazon.com/what-is/retrieval-augmented-generation/) applying confidence thresholds, and implementing human oversight or verification processes for critical outputs.

RAG is an approach that aims to reduce hallucinations in language models by incorporating the capability to retrieve external knowledge and making it part of the prompt that’s used as input to the model. The retriever module is responsible for retrieving relevant passages or documents from a large corpus of textual data based on the input query or context. The retrieved information is then provided to the LLM, which uses this external knowledge in conjunction with prompts to generate the final output. By grounding the generation process in factual information from reliable sources, RAG can reduce the likelihood of hallucinating incorrect or made-up content, thereby enhancing the factual accuracy and reliability of the generated responses.

[Amazon Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/) offer hallucination detection with contextual grounding checks, which can be seamlessly applied using Amazon Bedrock APIs (such as `Converse` or `InvokeModel`) or embedded into workflows. After an LLM generates a response, these workflows perform a check to see if hallucinations occurred. This setup can be achieved through [Amazon Bedrock Prompt Flows](https://aws.amazon.com/bedrock/flows/) or with custom logic using [AWS Lambda](https://aws.amazon.com/lambda) functions. Customers can also do batch evaluation with human reviewers using Amazon Bedrock model evaluation’s human-based evaluation feature. However, these are static workflows, updating the hallucination detection logic requires modifying the entire workflow, limiting adaptability.

To address this need for flexibility, Amazon Bedrock Agents enables dynamic workflow orchestration. With Amazon Bedrock Agents, organizations can implement scalable, customizable hallucination detection that adjusts based on specific needs, reducing the effort needed to incorporate new detection techniques and additional API calls in the workflow without restructuring the entire workflow and letting the LLM decide the plan of action to orchestrate the workflow.

In this post, we will set up our own custom agentic AI workflow using [Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/) to intervene when LLM hallucinations are detected and route the user query to customer service agents through a human-in-the-loop process. Imagine this to be a simpler implementation of calling a customer service agent when the chatbot is unable to answer the customer query. The chatbot is based on a RAG approach, which reduces hallucinations to a large extent, and the [agentic workflow](https://promptengineering.org/exploring-agentic-wagentic-workflows-the-power-of-ai-agent-collaborationorkflows-the-power-of-ai-agent-collaboration/) provides a customizable mechanism in how to measure, detect, and mitigate hallucinations that might occur.

Agentic workflows are a fresh new perspective in building dynamic and complex business use case-based workflows with the help of LLMs as the [reasoning engine](https://cohere.com/blog/llm-reasoning-sets-new-benchmarks-for-ai) or brain. These agentic workflows decompose the natural language query-based tasks into multiple actionable steps with iterative feedback loops and [self-reflection](https://blog.langchain.dev/reflection-agents/) to produce the final result using tools and APIs.

Amazon Bedrock Agents helps accelerate generative AI application development by orchestrating multistep tasks. Amazon Bedrock Agents uses the reasoning capability of LLMs to break down user-requested tasks into multiple steps. They use the given instruction to create an orchestration plan and then carry out the plan by invoking company APIs or accessing knowledge bases using RAG to provide a final response to the user. This offers tremendous use case flexibility, enables dynamic workflows, and reduces development cost. Amazon Bedrock Agents is instrumental in customizing applications to help meet specific project requirements while protecting private data and helping to secure applications. These agents work with AWS managed infrastructure capabilities such as Lambda and [Amazon Bedrock](https://aws.amazon.com/bedrock), reducing infrastructure management overhead. Additionally, agents streamline workflows and automate repetitive tasks. With the power of AI automation, you can boost productivity and reduce costs.

Amazon Bedrock is a fully managed service that offers a choice of high-performing foundation models (FMs) from leading AI companies such as AI21 Labs, Anthropic, Cohere, Meta, Mistral AI, Stability AI, and Amazon through a single API, along with a broad set of capabilities to build generative AI applications with security, privacy, and responsible AI.

## Use case overview

In this post, we add our own custom intervention to a RAG-powered chatbot in an event of hallucinations being detected. We will be using Retrieval Augmented Generation Automatic Score (metrics such as answer correctness and answer relevancy to **develop a custom hallucination score** for measuring hallucinations. If the hallucination score for a particular LLM response is less than a custom threshold, it indicates that the generated model response is not well-aligned with the ground truth. In this situation, we notify a pool of human agents through [Amazon Simple Notification Service (Amazon SNS) notification](https://docs.aws.amazon.com/code-library/latest/ug/python_3_sns_code_examples.html) to assist with the query instead of providing the customer with the hallucinated LLM response.

The RAG-based chatbot we use ingests the [Amazon Bedrock User Guide](https://docs.aws.amazon.com/pdfs/bedrock/latest/userguide/bedrock-ug.pdf) to assist customers on queries related to Amazon Bedrock.

## Dataset

The dataset used in the [notebook](https://github.com/aws-samples/responsible_ai_reduce_hallucinations_for_genai_apps/blob/main/other-examples/bedrock-agent-self-reflection/bedrock-agent-self-reflection.ipynb) is the latest [Amazon Bedrock User guide PDF](https://docs.aws.amazon.com/pdfs/bedrock/latest/userguide/bedrock-ug.pdf) file, which is publicly available to download. Alternatively, you can use other PDFs of your choice to create the knowledge base from scratch and use it in this notebook.

If you use a custom PDF, you will need to curate a supervised dataset of ground truth answers to multiple questions to test this approach. The custom hallucination detector uses RAGAS metrics, which are generated using a CSV file containing question-answer pairs. For custom PDFs, it is necessary to replace this CSV file and re-run the notebook for a different dataset.

In addition to the dataset in the notebook, we ask the agent multiple questions, a few of them from the PDF and a few not part of the PDF. The ground truth answers are manually curated based on the PDF contents if relevant.

## ![this image has 4 sample questions. we ask the agent multiple questions, a few of them from the PDF and a few not part of the PDF. The ground truth answers are manually curated based on PDF contents if relevant.](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/24/ML-17639-Lab2-dataset-1024x260.png)

## Prerequisites

To run this solution in your AWS account, complete the following prerequisites:

- Clone the [GitHub repository](https://github.com/aws-samples/responsible_ai_reduce_hallucinations_for_genai_apps) and follow the steps explained in the README.
- Set up an [Amazon SageMaker](https://aws.amazon.com/sagemaker/) notebook on an ml.t3.medium [Amazon Elastic Compute Cloud (Amazon EC2)](https://aws.amazon.com/ec2)
- Acquire access to models hosted on Amazon Bedrock. Choose **Manage model access** in the navigation pane of the Amazon Bedrock console and choose from the list of available options. We use [Anthropic’s Claude v3 (Sonnet)](https://www.anthropic.com/news/claude-3-family) on Amazon Bedrock and [Amazon Titan Embeddings](https://aws.amazon.com/bedrock/titan/) Text v2 on Amazon Bedrock for this post.

## Implement the solution

The following illustrates the solution architecture:

Architecture Diagram for Custom Hallucination Detection and Mitigation

The overall workflow involves the following steps:

- Data ingestion involving raw PDFs stored in an [Amazon Simple Storage Service (Amazon S3)](https://aws.amazon.com/s3) bucket synced as a data source with [Amazon Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/).
- User asks questions relevant to the Amazon Bedrock User Guide, which are handled by an Amazon Bedrock agent that is set up to handle user queries.

`User query: What models are supported by bedrock agents?`

- The agent creates a plan and identifies the need to use a knowledge base. It then sends a request to the knowledge base, which retrieves relevant data from the underlying vector database. The agent retrieves an answer through RAG using the following steps:  The search query is directed to the vector database ([Amazon OpenSearch Serverless](https://aws.amazon.com/opensearch-service/features/serverless/)). Relevant answer chunks are retrieved. The knowledge base response is generated from the retrieved answer chunks and sent back to the agent.

`Generated Answer: Amazon Bedrock supports foundation models from various providers including Anthropic (Claude models), AI21 Labs (Jamba models), Cohere (Command models), Meta (Llama models), Mistral AI`

- The user query and knowledge base response are used together to invoke the correct action group.
- The user question and knowledge base response are passed as inputs to a Lambda function that calculates a hallucination score.

`The generated answer has some correct and some incorrect information as it picks up general Amazon Bedrock model support and not Amazon Bedrock Agents-specific model support. Therefore we have hallucination detected with a score of 0.4.`

- An [SNS](https://aws.amazon.com/sns/) notification is sent if the answer score is lower than the custom threshold.

`Because answer score is 0.4 < 0.9 (hallucination threshold), the SNS notification is triggered.`

- If the answer score is higher than the custom threshold, the hallucination detector set up in Lambda responds with a final knowledge base response. Otherwise, it returns a pre-defined response asking the user to wait until a customer service agent joins the conversation shortly.

`Customer service human agent queue is notified and the next available agent joins or emails back if it is an offline response mechanism.`

- The final agent response is shown in the chatbot UI(User Interface).

In the GitHub repository [notebook](https://github.com/aws-samples/responsible_ai_reduce_hallucinations_for_genai_apps/blob/main/other-examples/bedrock-agent-self-reflection/bedrock-agent-self-reflection.ipynb), we cover the following learning objectives:

- Measure and detect hallucinations with an Agentic AI workflow which has the ability to notify humans-in-the-loop to remediate hallucinations, if detected.
- Custom hallucination detector with pre-defined thresholds based on select evaluation metrics in RAGAS.
- To remediate, we will send an SNS notification to the customer service queue and wait for a human to help us with the question.

### Step 1: Setting up Amazon Bedrock Knowledge Bases with Amazon Bedrock Agents

In this section, we will integrate [Amazon Bedrock Knowledge Bases ](https://aws.amazon.com/bedrock/knowledge-bases/)with Amazon Bedrock Agents to create a RAG workflow. RAG systems use external knowledge sources to augment the LLM’s output, improving factual accuracy and reducing hallucinations. We create the agent with the following high-level instruction encouraging it to take a question-answering role.

```
agent_instruction = """

You are a question answering agent that helps customers answer questions from the Amazon Bedrock User Guide inside the associated knowledge base.

Next you will always use the knowledge base search result to detect and measure any hallucination using the functions provided"

"""
```

### Step 2: Invoke Amazon Bedrock Agents with user questions about Amazon Bedrock documentation

We are using a supervised dataset with predefined questions and ground truth answers to invoke Amazon Bedrock Agents which triggers the custom hallucination detector based on the agent response from the knowledge base. In the notebook, we demonstrate how the answer score based on RAGAS metrics can notify a human customer service representative if it does not meet a pre-defined custom threshold score.

We use RAGAS metrics such as `answer correctness` and `answer relevancy` to determine the custom threshold score. Depending on the use case and dataset, the list of applicable RAGAS metrics can be customized accordingly.

To change the threshold score, you can modify the `measure_hallucination()` method inside the Lambda function `lambda_hallucination_detection()`.

The agent is prompted with the following template. The `user_question` in the template is iterated from the supervised dataset CSV file that contains the question and ground truth answers.

```
USER_PROMPT_TEMPLATE = """Question: {user_question}

Given an input question, you will search the Knowledge Base on Amazon Bedrock User Guide to answer the user question. 
If the knowledge base search results do not return any answer, you can try answering it to the best of your ability, but do not answer anything you do not know. Do not hallucinate.
Using this knowledge base search result you will ALWAYS execute the appropriate action group API to measure and detect the hallucination on that knowledge base search result.

Remove any XML tags from the knowledge base search results and final user response.


Some samples for `user_question` parameter:

What models are supported by bedrock agents?
Which models can I use with Amazon Bedrock Agents?
Which are the dates for reinvent 2024?
What is Amazon Bedrock?

"""
```

### Step 3: Trigger human-in-the-loop in case of hallucination

If the custom hallucination score threshold is not met by the agent response, a human in the loop is notified using SNS notifications. These notifications can be sent to the customer service representative queue or [Amazon Simple Queue Service (Amazon SQS)](https://aws.amazon.com/sqs) queues for email and text notifications. These representatives can respond to the email (offline) or ongoing chat (online) based on their training and knowledge of the system and additional resources. This would be based out of the specific product workflow design.

To view the actual SNS messages sent out, we can view the latest Lambda [AWS CloudWatch](https://aws.amazon.com/cloudwatch) logs following the instructions as given in [viewing CloudWatch logs for Lambda functions](https://docs.aws.amazon.com/lambda/latest/dg/monitoring-cloudwatchlogs-view.html). You can search for the string `Received SNS message ::` inside the [CloudWatch logs](https://aws.amazon.com/cloudwatch/) for the Lambda function `LambdaAgentsHallucinationDetection().`

## Cost considerations

The following are important cost considerations:

- This current implementation has no separate charges for building resources using Amazon Bedrock Knowledge Bases or Amazon Bedrock Agents.
- You will incur charges for the embedding model and text model invocation on Amazon Bedrock. For more details, see [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/).
- You will incur charges for Amazon S3 and vector database usage. For more details, see [Amazon S3 pricing](https://aws.amazon.com/s3/pricing/) and [Amazon OpenSearch Service pricing](https://aws.amazon.com/opensearch-service/pricing/), respectively.

## Clean up

To avoid incurring unnecessary costs, the implementation has the option to clean up resources after an entire run of the notebook. You can check the instructions in the [`cleanup_infrastructure()`](https://github.com/aws-samples/responsible_ai_reduce_hallucinations_for_genai_apps/blob/main/reduce_llm_hallucinations_labs/lab2/lab2.ipynb) method for how to avoid the automatic cleanup and experiment with different prompts and datasets.

The order of resource cleanup is as follows:

- Disable the action group.
- Delete the action group.
- Delete the alias.
- Delete the agent.
- Delete the Lambda function.
- Empty the S3 bucket.
- Delete the S3 bucket.
- Delete [AWS Identity and Access Management (IAM)](https://aws.amazon.com/iam) roles and policies.
- Delete the vector DB collection policies.
- Delete the knowledge bases.

## Key considerations

Amazon Bedrock Agents can increase overall latency compared to using just Amazon Bedrock Guardrails and Amazon Bedrock Prompt Flows. It is a trade-off decision between having LLM generated workflows compared to static or deterministic workflows. With agents, the LLM generates the workflow orchestration in real time using the available knowledge bases, tools, and APIs. Whereas with prompt flows and guardrails, the workflow has to be orchestrated and designed offline.

For evaluation, while we have chosen an LLM-based evaluation framework RAGAS, it is possible to swap out the elements in the hallucination detection Lambda function for another framework.

## Conclusion

This post demonstrated how to use Amazon Bedrock Agents, Amazon Knowledge Bases, and the RAGAS evaluation metrics to build a custom hallucination detector and remediate it by using human-in-the-loop. The agentic workflow can be extended to custom use cases through different hallucination remediation techniques and offers the flexibility to detect and mitigate hallucinations using custom actions.

For more information on creating agents to orchestrate workflows, see [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html) Agents. To learn about multiple RAGAS metrics for LLM evaluations see [RAGAS: Getting Started](https://github.com/explodinggradients/ragas/blob/main/docs/getstarted/index.md).

### About the Authors

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/09/20/shayan.png)**Shayan Ray** is an Applied Scientist at Amazon Web Services. His area of research is all things natural language (like NLP, NLU, and NLG). His work has been focused on conversational AI, task-oriented dialogue systems, and LLM-based agents. His research publications are on natural language processing, personalization, and reinforcement learning.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/11/25/bharathiphoto-1.png)**Bharathi Srinivasan** is a Generative AI Data Scientist at AWS WWSO where she works building solutions for Responsible AI challenges. She is passionate about driving business value from machine learning applications by addressing broad concerns of Responsible AI. Outside of building new AI experiences for customers, Bharathi loves to write science fiction and challenge herself with endurance sports.
