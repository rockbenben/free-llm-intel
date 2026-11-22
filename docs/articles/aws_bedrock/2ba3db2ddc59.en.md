---
vendor: aws_bedrock
title: Migrating multi-model AI agents to Amazon Bedrock AgentCore runtime
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/migrating-multi-model-ai-agents-to-amazon-bedrock-agentcore-runtime
date: 2026-09-18
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 97d71219d0c8
---

# Migrating multi-model AI agents to Amazon Bedrock AgentCore runtime

Organizations building multi-model agentic AI applications face growing infrastructure complexity. Managing container orchestration, scaling policies, identity, and observability for multiple model types adds operational overhead. Teams often spend more time on infrastructure than on agent logic development.

Developers running agentic frameworks on self-managed infrastructure such as [Amazon Elastic Container Service (Amazon ECS)](https://aws.amazon.com/ecs/) with [AWS Fargate](https://aws.amazon.com/fargate/) have full control over their deployment configuration. As agentic workloads evolve and scale, teams might choose to adopt managed runtimes that provide built-in session management, identity, and observability.

[Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) is a platform to build, connect, and optimize agents at scale, with any framework or model. AgentCore runtime, its managed deployment capability, handles container lifecycle, scaling, identity, and observability, so you can focus on your agent code.

In a previous post, [Agentic AI with multi-model framework using Hugging Face smolagents on AWS](https://aws.amazon.com/blogs/machine-learning/agentic-ai-with-multi-model-framework-using-hugging-face-smolagents-on-aws/), we showed how to build a healthcare AI agent with multi-model orchestration on self-managed infrastructure. In this post, we show you how to migrate that multi-model agent to Amazon Bedrock AgentCore runtime. The migration reduces infrastructure management while preserving agent capabilities, including triple-model orchestration and vector-enhanced knowledge retrieval.

## Solution overview

This solution migrates a multi-model healthcare AI agent to Amazon Bedrock AgentCore runtime while preserving the existing agent logic. The agent processes medical queries across three model backends with vector-enhanced knowledge retrieval, all running inside a single AgentCore-managed container. You can direct each query to the model backend suited to the task. A domain-specific model such as [BioM-ELECTRA-Large-SQuAD2](https://huggingface.co/sultan/BioM-ELECTRA-Large-SQuAD2) on [Amazon SageMaker AI](https://aws.amazon.com/sagemaker/ai/) handles specialized biomedical queries, and a foundation model (FM) such as [Llama 3.1 70B Instruct by Meta](https://aws.amazon.com/bedrock/meta/) on [Amazon Bedrock](https://aws.amazon.com/bedrock/) handles broader medical reasoning. This approach helps healthcare teams address a range of query types while reducing the operational overhead of managing the underlying infrastructure.

The standalone version from the previous post deployed on Amazon ECS with AWS Fargate includes container orchestration, scaling, identity, and observability configured by the user. The AgentCore version wraps the same agent logic with the AgentCore runtime decorator pattern, and AgentCore runtime handles these operational concerns automatically.

[Hugging Face smolagents](https://huggingface.co/docs/smolagents/en/index) is an open source Python library designed to build and run agents using a few lines of code. This solution uses Hugging Face smolagents framework as a reference implementation, demonstrating that AgentCore runtime supports any agentic framework. With the bring-your-own (BYO) agent approach, you can deploy existing agent code to AgentCore runtime without rewriting or adapting to a specific framework.

**Note:** This solution is a sample implementation for demonstration purposes. Production deployments handling medical or other sensitive queries use Amazon Bedrock Guardrails for content filtering and grounding validation as a standard control.

## Architecture

The solution consists of the following services and features:

- Amazon Bedrock AgentCore runtime for managed agent container deployment, scaling, identity, and observability.
- Amazon Bedrock with Llama 3.1 70B Instruct by Meta for complex medical reasoning. For model availability by AWS Region, refer to [Supported models by AWS Region in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html).
- Amazon SageMaker AI with BioM-ELECTRA-Large-SQuAD2 for specialized biomedical queries and managed auto scaling.
- [Amazon OpenSearch Service](https://aws.amazon.com/opensearch-service/) for vector similarity matching and contextual knowledge retrieval with medical knowledge indexing.
- Containerized model server with BioM-ELECTRA-Large-SQuAD2 for self-hosted model deployment.
- [AWS Identity and Access Management (IAM)](https://aws.amazon.com/iam) for security and access control.

**Note:** The previous post (standalone version) uses [Claude 3.5 Sonnet V2 by Anthropic](https://aws.amazon.com/bedrock/anthropic/). This post uses Llama 3.1 70B Instruct by Meta, demonstrating that AgentCore runtime is model-agnostic. The model choice is an implementation decision, not a requirement.

The following diagram illustrates the solution architecture and how the agent orchestrates across three model backends.

![Architecture diagram showing user connecting through a client web interface to Amazon Bedrock AgentCore runtime, which hosts a healthcare agent container with Hugging Face smolagents framework and AgentCore runtime decorator. The agent connects to three model backends (Amazon SageMaker AI, Amazon Bedrock, and containerized model server) and Amazon OpenSearch Service for vector knowledge retrieval. Hugging Face Hub provides models to SageMaker AI and the containerized server.](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/09/08/ML-21510-1.png)

Figure 1: Multi-model healthcare agent architecture on Amazon Bedrock AgentCore runtime

A client web interface connects to Amazon Bedrock AgentCore runtime, which hosts the healthcare agent container. The container uses the Hugging Face smolagents framework with the AgentCore runtime decorator. AgentCore runtime provides built-in identity and observability. The agent orchestrates across three model backends: Amazon SageMaker AI with BioM-ELECTRA, Amazon Bedrock with Llama 3.1 70B Instruct by Meta, and a containerized model server with BioM-ELECTRA. The solution includes Amazon OpenSearch Service for vector-enhanced knowledge retrieval.

This solution supports deployment options with each backend optimized for different scenarios:

- Amazon SageMaker AI for managed endpoints with auto scaling using [Hugging Face Hub](https://huggingface.co/models) models.
- Amazon Bedrock for serverless access to foundation models and complex reasoning through AWS APIs.
- A containerized model server for self-hosted model deployment and tool integration from Hugging Face Hub (deployable on Amazon ECS, [Amazon Elastic Kubernetes Service (Amazon EKS)](https://aws.amazon.com/eks/), or other container environments).

The three backends implement [Hugging Face Messages API compatibility](https://huggingface.co/docs/text-generation-inference/en/messages_api), providing consistent request and response formats regardless of the selected model service.

The complete implementation is available in the sample-healthcare-agent-with-agentcore-on-aws [GitHub](https://github.com/aws-samples/sample-healthcare-agent-with-agentcore-on-aws) repository.

## Migrate the agent to AgentCore runtime

This section walks through migrating the existing healthcare AI agent to Amazon Bedrock AgentCore runtime using the AgentCore CLI.

### Prerequisites

Before you deploy the solution, you need the following:

- An AWS account with access to Amazon Bedrock AgentCore runtime and appropriate permissions to create [IAM roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html) and [Amazon OpenSearch Service domains](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/createupdatedomains.html).
- [AWS Command Line Interface (AWS CLI)](https://aws.amazon.com/cli) version 2.0 or later installed and configured.
- [Node.js](https://nodejs.org/) 20 or later (required for the deployment CLI).
- [AWS Cloud Development Kit (AWS CDK)](https://docs.aws.amazon.com/cdk/v2/guide/getting-started.html) installed.
- [AgentCore CLI](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-cli.html) installed.
- [Python](https://www.python.org/downloads/) 3.10 or later for running deployment scripts.
- [Docker](https://docs.docker.com/get-docker/) installed and running (required for code execution isolation).
- Access to Amazon Bedrock model, Amazon SageMaker AI, and Amazon OpenSearch Service domain in your AWS Region with appropriate IAM permissions to create and manage resources.
- [bedrock-agentcore Python SDK](https://github.com/aws/bedrock-agentcore-sdk-python) installed.
- For this implementation, we’re using [Python 3.10+](https://www.python.org/downloads/), [smolagents framework](https://huggingface.co/docs/smolagents/en/index), [transformers 4.55.0+](https://pypi.org/project/transformers/), and [boto3](https://pypi.org/project/boto3/).

### AgentCore runtime concepts

Amazon Bedrock AgentCore runtime uses a decorator pattern to wrap your agent logic. The key components are:

- [BedrockAgentCoreApp](https://github.com/aws/bedrock-agentcore-sdk-python) – initializes the AgentCore application.
- `@app.entrypoint` – decorates the function that AgentCore runtime calls when a request arrives.
- `app.run()` – starts the AgentCore runtime server.

The following code shows the AgentCore integration pattern:

```
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint
def healthcare_agent_entrypoint(payload):
    user_input = payload.get("prompt", "")
    model_type = payload.get("model_type", "sagemaker")
    # Your existing agent logic here
    agent = TripleHealthcareAgent(vector_store=vector_store)
    response = agent.run(user_input, model_type=model_type)
    return str(response)

if __name__ == "__main__":
    app.run()
```

The agent code between the decorator and return statement remains unchanged from the standalone version. AgentCore runtime handles container lifecycle, scaling, identity, and observability automatically.

### Set up the project

Create an AgentCore project and add your existing agent using the AgentCore CLI.

**Install the AgentCore CLI:**

```
npm install -g @aws/agentcore
```

**Create a new AgentCore project:**

```
agentcore create --project-name healthcareagent --no-agent --build Container --language Python --protocol HTTP --model-provider Bedrock --memory none
```

**Add your existing agent as a bring-your-own (BYO) agent:**

```
agentcore add agent --name healthcare_agentcore --type byo --build Container --language Python --protocol HTTP --network-mode PUBLIC --code-location ./agent-code --entrypoint healthcare_agentcore.py --framework Strands --model-provider Bedrock
```

**Note:** The `--framework` flag specifies the CLI template. The actual agent code uses Hugging Face smolagents, which is compatible with AgentCore runtime regardless of the template selection.

### Prepare the container

- Create a `pyproject.toml` in your agent code directory to define dependencies:  `[project] name = "healthcare-agentcore" version = "1.0.0" requires-python = ">=3.10" dependencies = [ "smolagents>=1.24.0", "transformers>=4.55.0", "boto3>=1.37.0", "opensearch-py>=3.1.0", "requests-aws4auth>=1.3.1", "bedrock-agentcore>=0.1.0", "numpy>=1.26.0", "requests>=2.32.0", "docker>=7.1.0", ]`
- Create a `Dockerfile`:  `FROM public.ecr.aws/docker/library/python:3.12-slim RUN pip install --no-cache-dir uv WORKDIR /app COPY pyproject.toml ./ RUN uv pip install --system -r pyproject.toml COPY . . EXPOSE 8080 CMD ["python", "healthcare_agentcore.py"]`
- Create a `.dockerignore` to keep the image size within the 2 GB limit:  `venv/ .venv/ __pycache__/ .git/ *.pyc`

### Deploy to AgentCore runtime

With the project configured, you can deploy the agent using a single CLI command.

**Deploy the agent:**

```
agentcore deploy -y
```

The CLI builds the container, pushes it to Amazon Elastic Container Registry (Amazon ECR), and creates the AgentCore runtime agent. Deployment takes approximately 10–15 minutes.

### Test the deployed agent

You can test the deployed agent in two ways: using the AgentCore CLI or programmatically with boto3.

**Invoke the agent using the AgentCore CLI:**

```
agentcore invoke --prompt '{"prompt": "What are the side effects of metformin?", "model_type": "llama"}'
```

**Or, invoke programmatically using boto3:**

This path invokes the same deployed agent as the CLI, using the boto3 SDK directly. The `agentRuntimeArn` identifies your deployed agent, `contentType` specifies the request format, and `payload` carries the prompt and model selection.

```
import boto3, json

client = boto3.client('bedrock-agentcore', region_name='us-west-2')

payload = json.dumps({
    "prompt": "What are the side effects of metformin?",
    "model_type": "llama"
})

response = client.invoke_agent_runtime(
    agentRuntimeArn='<your-agent-runtime-arn>',
    contentType='application/json',
    accept='application/json',
    payload=payload.encode('utf-8')
)

result = response['response'].read().decode('utf-8')
print(result)
```

## Key differences from self-managed deployment

The standalone version and the AgentCore runtime version deploy the same agent in different ways. The following sections describe what each path provides.

### Amazon ECS with AWS Fargate deployment

The standalone version runs on Amazon ECS with AWS Fargate. You define ECS task definitions and service configuration, set auto scaling policies, configure IAM roles per service, and set up observability through [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/). Deployment uses a Docker build, an Amazon ECR push, and an ECS service update. This path gives you full control over container configuration, networking, and scaling behavior. The agent code lives in `healthcare_agentcore.py`, integrates with Amazon Bedrock, Amazon SageMaker AI, and the containerized backend, and uses Amazon OpenSearch Service for vector search.

### Amazon Bedrock AgentCore runtime deployment

The AgentCore runtime version runs the same `healthcare_agentcore.py` agent code with the AgentCore decorator pattern. AgentCore runtime provides container orchestration, session-based scaling, identity management through IAM integration, and observability through built-in tracing and logging. Deployment uses a single command (`agentcore deploy`). The model integration (Amazon Bedrock, Amazon SageMaker AI, containerized backend) and vector search (Amazon OpenSearch Service) remain the same as the standalone version.

Both deployment approaches have distinct advantages. Amazon ECS with AWS Fargate provides full control over container configuration, networking, and scaling policies, suitable for teams with existing container operations expertise or specific infrastructure requirements. Amazon Bedrock AgentCore runtime is suited for teams that prefer managed infrastructure and want to focus primarily on agent logic development.

Regardless of the deployment path, the following elements remain unchanged when migrating from the standalone version to AgentCore runtime:

- Core agent logic (`BedrockAgentCoreApp` decorator + existing code).
- Multi-model orchestration across Amazon Bedrock, Amazon SageMaker AI, and containerized backends.
- Vector-enhanced knowledge retrieval with Amazon OpenSearch Service.
- Hugging Face Messages API compatibility across model backends.

## Clean up

To avoid incurring future charges, delete the resources you created when you no longer need them. If you plan to continue using the deployed agent, no action is required.

- **Remove the AgentCore runtime agent:
**First, remove all resources from your local configuration:   `agentcore remove all`  Then deploy again to tear down the AWS resources:  `agentcore deploy`
- **Delete the Amazon SageMaker AI endpoint:**  `aws sagemaker delete-endpoint --endpoint-name healthcare-agentcore-endpoint-1 --region us-west-2`
- **Delete the Amazon OpenSearch Service domain:**  `aws opensearch delete-domain --domain-name healthcare-vector-store --region us-west-2`

## Conclusion

In this post, we showed how to migrate a multi-model healthcare AI agent from self-managed Amazon ECS with AWS Fargate infrastructure to Amazon Bedrock AgentCore runtime. The migration required no changes to the core agent logic. The same `healthcare_agentcore.py` file orchestrates across Amazon Bedrock, Amazon SageMaker AI, and a containerized model server. It runs on AgentCore runtime with the addition of the AgentCore decorator pattern (`BedrockAgentCoreApp`, `@app.entrypoint`, and `app.run()`). For healthcare teams, this pattern directs specialized biomedical queries to a domain-specific model such as BioM-ELECTRA-Large-SQuAD2 on Amazon SageMaker AI. It routes broader medical reasoning to a foundation model such as Llama 3.1 70B Instruct by Meta on Amazon Bedrock. Together, these backends support a range of query types.

For teams that choose managed infrastructure, AgentCore runtime handles container orchestration, scaling, identity management, and observability. You can focus on agent logic development instead. The framework-agnostic design supports a wide combination of models and agentic frameworks, making this migration pattern applicable across industries including healthcare, financial services, and manufacturing.

To get started, clone the sample-healthcare-agent-with-agentcore-on-aws [GitHub](https://github.com/aws-samples/sample-healthcare-agent-with-agentcore-on-aws) repository and follow the deployment steps in this post. To understand the standalone implementation that this post migrates from, see [Agentic AI with multi-model framework using Hugging Face smolagents on AWS](https://aws.amazon.com/blogs/machine-learning/agentic-ai-with-multi-model-framework-using-hugging-face-smolagents-on-aws/). If there are questions about getting started with Amazon Bedrock AgentCore, speak with an [AWS generative AI Specialist](https://pages.awscloud.com/global-ln-gc-400-ai-contact-us.html).

## Further reading

- [Agentic AI on AWS – Build, deploy, and scale AI agents with AWS](https://builder.aws.com/learn/topics/agentic-ai)
- [Make agents a reality with Amazon Bedrock AgentCore: Now generally available](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-is-now-generally-available/)
- [Amazon Bedrock documentation](https://docs.aws.amazon.com/bedrock/)
- [Build trustworthy AI agents with Amazon Bedrock AgentCore Observability](https://aws.amazon.com/blogs/machine-learning/build-trustworthy-ai-agents-with-amazon-bedrock-agentcore-observability/)

## About the author
