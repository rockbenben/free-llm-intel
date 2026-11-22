---
vendor: aws_bedrock
title: Build an MCP application with Mistral models on AWS
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-an-mcp-application-with-mistral-models-on-aws
date: 2025-07-10
lang: en
captured: 2026-11-22
extractor: readability-v1
status: ok
body_sha: 5e20b4cc31be
---

# Build an MCP application with Mistral models on AWS

*This post is cowritten with Siddhant Waghjale and Samuel Barry from Mistral AI.*

[Model Context Protocol](https://modelcontextprotocol.io/introduction) (MCP) is a standard that has been gaining significant traction in recent months. At a high level, it consists of a standardized interface designed to streamline and enhance how AI models interact with external data sources and systems. Instead of hardcoding retrieval and action logic or relying on one-time tools, MCP offers a structured way to pass contextual data (for example, user profiles, environment metadata, or third-party content) into a [large language model](https://aws.amazon.com/what-is/large-language-model/) (LLM) context and to route model outputs to external systems. For developers, MCP abstracts away integration complexity and creates a unified layer for injecting external knowledge and executing model actions, making it more straightforward to build robust and efficient agentic AI systems that remain decoupled from data-fetching logic.

[Mistral AI](https://mistral.ai/) is a frontier research lab that emerged in 2023 as a leading open source contender in the field of [generative AI](https://aws.amazon.com/generative-ai/). Mistral has released many state-of-the-art models, from Mistral 7B and Mixtral in the early days up to the recently announced Mistral Medium 3 and Small 3—effectively popularizing the mixture of expert architecture along the way. Mistral models are generally described as extremely efficient and versatile, frequently reaching state-of-the-art levels of performance at a fraction of the cost. These models are now seamlessly integrated into [Amazon Web Services](https://aws.amazon.com/) (AWS) services, unlocking powerful deployment options for developers and enterprises. Through [Amazon Bedrock](https://aws.amazon.com/bedrock/), users can access Mistral models using a fully managed API, enabling rapid prototyping without managing infrastructure. [Amazon Bedrock Marketplace](https://aws.amazon.com/bedrock/marketplace/) further extends this by allowing quick model discovery, licensing, and integration into existing workflows. For power users seeking fine-tuning or custom training, [Amazon SageMaker JumpStart](https://aws.amazon.com/sagemaker-ai/jumpstart/) offers a streamlined environment to customize Mistral models with their own data, using the scalable infrastructure of AWS. This integration makes it faster than ever to experiment, scale, and productionize Mistral models across a wide range of applications.

This post demonstrates building an intelligent AI assistant using Mistral AI models on AWS and MCP, integrating real-time location services, time data, and contextual memory to handle complex multimodal queries. This use case, restaurant recommendations, serves as an example, but this extensible framework can be adapted for enterprise use cases by modifying MCP server configurations to connect with your specific data sources and business systems.

## Solution overview

This solution uses Mistral models on Amazon Bedrock to understand user queries and route the query to relevant MCP servers to provide accurate and up-to-date answers. The system follows this general flow:

- **User input** – The user sends a query (text, image, or both) through either a terminal-based or web-based Gradio interface
- **Image processing** – If an image is detected, the system processes and optimizes it for the AI model
- **Model request** – The query is sent to the Amazon Bedrock [Converse API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html) with appropriate system instructions
- **Tool detection** – If the model determines it needs external data, it requests a tool invocation
- **Tool execution** – The system routes the tool request to the appropriate MCP server and executes it
- **Response generation** – The model incorporates the tool’s results to generate a comprehensive response
- **Response delivery** – The final answer is displayed to the user

In this example, we demonstrate the MCP framework using a general use case of restaurant or location recommendation and route planning. Users can provide multimodal input (such as text plus image), and the application integrates [Google Maps](https://www.npmjs.com/package/@modelcontextprotocol/server-google-maps), [Time](https://github.com/yokingma/time-mcp), and [Memory](https://github.com/modelcontextprotocol/servers/tree/main/src/memory) MCP servers. Additionally, this post showcases how to use the [Strands Agent](https://strandsagents.com/latest/) framework as an alternative approach to build the same MCP application with significantly reduced complexity and code. Strands Agent is an open source, multi-agent coordination framework that simplifies the development of intelligent, context-aware agent systems across various domains. You can build your own MCP application by modifying the MCP server configurations to suit your specific needs. You can find the complete source code for this example in our [Git repository](https://github.com/aws-samples/mistral-on-aws/tree/main/MCP/MCP_Mistral_app_demo). The following diagram is the solution architecture.

![MCP Module architecture with Host, Clients, Servers components bridging UI and Bedrock foundation models](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/30/ML-18862-image-1.png)

## Prerequisites

Before implementing the example, you need to set up the account and environment. Use the following steps.To set up the AWS account :

- Create an AWS account. If you don’t already have one, sign up at [https://aws.amazon.com](https://aws.amazon.com/)
- To enable Amazon Bedrock access, go to the Amazon Bedrock console and request access to the models you plan to use (for this walkthrough, request access to Mistral Pixtral Large). Or deploy Mistral Small 3 model from Amazon Bedrock Marketplace. (For more details, refer to the **Mistral Model Deployments on AWS** section later in this post.) When your request is approved, you’ll be able to use these models through the Amazon Bedrock Converse API

To set up the local environment:

- Install the required tools:  Python 3.10 or later Node.js (required for MCP tool servers) [AWS Command Line Interface](https://aws.amazon.com/cli/) (AWS CLI), which is needed for configuration
- Clone the [Repository](https://github.com/aws-samples/mistral-on-aws/tree/main/MCP/MCP_Mistral_app_demo):

```
git clone https://github.com/aws-samples/mistral-on-aws.git
cd mistral-on-aws/MCP/MCP_Mistral_app_demo/
```

- Install Python dependencies:

```
pip install -r requirements.txt
```

- Configure AWS credentials:

```
aws configure
```

Then enter your AWS access key ID, secret access key, and preferred [AWS Region](https://docs.aws.amazon.com/glossary/latest/reference/glos-chap.html#region).

- Set up MCP tool servers. The server configurations are provided in file: `server_configs.py`. The system uses Node.js-based MCP servers. They’ll be installed automatically when you run the application for the first time using NPM. You can add other MCP server configurations in this file. This solution can be quickly modified and extended to meet your business requirements.

## Mistral model deployments on AWS

Mistral models can be accessed or deployed using the following methods. To use [foundation models](https://aws.amazon.com/what-is/foundation-models/) (FMs) in MCP applications, the models must support tool use functionality.

### Amazon Bedrock serverless (Pixtral Large)

To enable this model, follow these steps:

- Go to the Amazon Bedrock console.
- From the left navigation pane, select **Model access**.
- Choose **Manage model access**.
- Search for the model using the keyword **Pixtral**, select it, and choose **Next**, as shown in the following screenshot. The model will then be ready to use.

This model has cross-Region inference enabled. When using the model ID, always add the Region prefix `eu` or `us` before the model ID, such as `eu.mistral.pixtral-large-2502-v1:0`. Provide this model ID in config.py. You can now test the example with the Gradio web-based app.

![Amazon Bedrock interface for managing base model access with Pixtral Large model highlighted](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/30/ML-18862-image-2.png)

### Amazon Bedrock Marketplace (Mistral-Small-24B-Instruct-2501)

Amazon Bedrock Marketplace and SageMaker JumpStart deployments are dedicated instances (serverful) and incur charges as long as the instance remains deployed. For more information, refer to [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/) and [Amazon SageMaker pricing](https://aws.amazon.com/sagemaker/pricing/).

To enable this model, follow these steps:

- Go to the Amazon Bedrock console
- In the left navigation pane, select **Model catalog**
- In the search bar, search for “Mistral-Small-24B-Instruct-25-1,” as shown in the following screenshot

![Amazon Bedrock UI with model catalog, filters, and Mistral-Small-24B-Instruct-2501 model spotlight](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/30/ML-18862-image-3.png)

- Select the model and select **Deploy**.
- In the configuration page, you can keep all fields as default. This endpoint requires an instance type ml.g6.12xlarge. Check service quotas under the Amazon SageMaker service to make sure you have more than two instances available for endpoint usage (you’ll use another instance for Amazon SageMaker JumpStart deployment). If you don’t have more than two instances, request a quota increase for this instance type. Then choose **Deploy**. The model deployment might take a few minutes.
- When the model is in service, copy the endpoint Amazon Resource Name (ARN), as shown in the following screenshot, and add it to the config.py file in the `model_id` field. Then you can test the solution with the Gradio web-based app.
- The Mistral-Small-24B-Instruct-25-1 model doesn’t support image input, so only text-based Q&A is supported.

![AWS Bedrock marketplace deployments interface with workflow steps and active Mistral endpoint](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/30/ML-18862-image-4.png)

### Amazon SageMaker JumpStart (Mistral-Small-24B-Instruct-2501)

To enable this model, follow these steps:

- Go to the Amazon SageMaker console
- Create a domain and user profile
- Under the created user profile, launch Studio
- In the left navigation pane, select **JumpStart**, then search for “Mistral”
- Select **Mistral-Small-24B-Instruct-2501**, then choose **Deploy**

This deployment might take a few minutes. The following screenshot shows that this model is marked as **Bedrock ready**. This means you can register this model as an Amazon Bedrock Marketplace deployment and use Amazon Bedrock APIs to invoke this Amazon SageMaker endpoint.

![Dark-themed SageMaker dashboard displaying Mistral AI models with Bedrock ready status](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/30/ML-18862-image-5.png)

- After the model is in service, copy its endpoint ARN from the Amazon Bedrock Marketplace deployment, as shown in the following screenshot, and provide it to the config.py file in the `model_id` field. Then you can test the solution with the Gradio web-based app.

The Mistral-Small-24B-Instruct-25-1 model doesn’t support image input, so only text-based Q&A is supported.

![SageMaker real-time inference endpoint for Mistral small model with AllTraffic variant on ml.g6 instance](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/30/ML-18862-image-6.png)

## Build an MCP application with Mistral models on AWS

The following sections provide detailed insights into building MCP applications from the ground up using a component-level approach. We explore how to implement the three core MCP components, MCP host, MCP client, and MCP servers, giving you complete control and understanding of the underlying architecture.

### MCP host component

The MCP is designed to facilitate seamless interaction between AI models and external tools, systems, and data sources. In this architecture, the MCP host plays a pivotal role in managing the lifecycle and orchestration of MCP clients and servers, enabling AI applications to access and utilize external resources effectively. The MCP host is responsible for integration with FMs, providing context, capabilities discovery, initialization, and MCP client management. In this solution, we have three files to provide this capability.

The first file is agent.py. The `BedrockConverseAgent` class in `agent.py` is the core component that manages communication with the Amazon Bedrock service and provides the FM models integration. The constructor initializes the agent with model settings and sets up the AWS Bedrock client.

```
def __init__(self, model_id, region, system_prompt='You are a helpful assistant.'):
    """
    Initialize the Bedrock agent with model configuration.
    
    Args:
        model_id (str): The Bedrock model ID to use
        region (str): AWS region for Bedrock service
        system_prompt (str): System instructions for the model
    """
    self.model_id = model_id
    self.region = region
    self.client = boto3.client('bedrock-runtime', region_name=self.region)
    self.system_prompt = system_prompt
    self.messages = []
    self.tools = None
```

Then, the agent intelligently handles multimodal inputs with its image processing capabilities. This method validates image URLs provided by the user, downloads images, detects and normalizes image formats, resizes large images to meet API constraints, and converts incompatible formats to JPEG.

```
async def _fetch_image_from_url(self, image_url):
    # Download image from URL
    # Process and optimize for model compatibility
    # Return binary image data with MIME type
```

When users enter a prompt, the agent detects whether it contains an uploaded image or an image URL and processes it accordingly in the `invoke_with_prompt` function. This way, users can paste an image URL in their query or upload an image from their local device and have it analyzed by the AI model.

```
async def invoke_with_prompt(self, prompt):
    # Check if prompt contains an image URL
    has_image, image_url = self._is_image_url(prompt)
    if image_input:
        # First check for direct image upload
        # ...
    if has_image_url:
       # Second check for image URL in prompt
    else:
        # Standard text-only prompt
        content = [{'text': prompt}]
    return await self.invoke(content)
```

The most powerful feature is the agent’s ability to use external tools provided by MCP servers. When the model wants to use a tool, the agent detects the `tool_use` stop reason from Amazon Bedrock and extracts tool request details, including names and inputs. It then executes the tool through the `UtilityHelper`, and the tool use results are returned back to the model. The MCP host then continues the conversation with the tool results incorporated.

```
async def _handle_response(self, response):
    # Add the response to the conversation history
    self.messages.append(response['output']['message'])
    # Check the stop reason
    stop_reason = response['stopReason']
    if stop_reason == 'tool_use':
        # Extract tool use details and execute
        tool_response = []
        for content_item in response['output']['message']['content']:
            if 'toolUse' in content_item:
                tool_request = {
                    "toolUseId": content_item['toolUse']['toolUseId'],
                    "name": content_item['toolUse']['name'],
                    "input": content_item['toolUse']['input']
                }
                tool_result = await self.tools.execute_tool(tool_request)
                tool_response.append({'toolResult': tool_result})
        # Continue conversation with tool results
        return await self.invoke(tool_response)
```

The second file is utility.py. The `UtilityHelper` class in utility.py serves as a bridge between Amazon Bedrock and external tools. It manages tool registration, formatting tool specifications for Bedrock compatibility, and tool execution.

```
def register_tool(self, name, func, description, input_schema):
    corrected_name = UtilityHelper._correct_name(name)
    self._name_mapping[corrected_name] = name
    self._tools[corrected_name] = {
        "function": func,
        "description": description,
        "input_schema": input_schema,
        "original_name": name,
    }
```

For Amazon Bedrock to understand available tools from MCP servers, the utility module generates tool specifications by providing name, description, and `inputSchema` in the following function:

```
def get_tools(self):
    tool_specs = []
    for corrected_name, tool in self._tools.items():
        # Ensure the inputSchema.json.type is explicitly set to 'object'
        input_schema = tool["input_schema"].copy()
        if 'json' in input_schema and 'type' not in input_schema['json']:
            input_schema['json']['type'] = 'object'
        tool_specs.append(
            {
                "toolSpec": {
                    "name": corrected_name,
                    "description": tool["description"],
                    "inputSchema": input_schema,
                }
            }
        )
    return {"tools": tool_specs}
```

When the model requests a tool, the utility module executes it and formats the result:

```
async def execute_tool(self, payload):
    tool_use_id = payload["toolUseId"]
    corrected_name = payload["name"]
    tool_input = payload["input"]
    # Find and execute the tool
    tool_func = self._tools[corrected_name]["function"]
    original_name = self._tools[corrected_name]["original_name"]
    # Execute the tool
    result_data = await tool_func(original_name, tool_input)
    # Format and return the result
    return {
        "toolUseId": tool_use_id,
        "content": [{"text": str(result)}],
    }
```

The final component in the MCP host is the `gradio_app.py` file, which implements a web-based interface for our AI assistant using Gradio. First, it initializes the model configurations and the agent, then connects to MCP servers and retrieves available tools from the MCP servers.

```
async def initialize_agent():
  """Initialize Bedrock agent and connect to MCP tools"""
  # Initialize model configuration from config.py
  model_id = AWS_CONFIG["model_id"]
  region = AWS_CONFIG["region"]
  # Set up the agent and tool manager
  agent = BedrockConverseAgent(model_id, region)
  agent.tools = UtilityHelper()
  # Define the agent's behavior through system prompt
  agent.system_prompt = """
  You are a helpful assistant that can use tools to help you answer questions and perform tasks.
  Please remember and save user's preferences into memory based on user questions and conversations.
  """
  # Connect to MCP servers and register tools
  # ...
  return agent, mcp_clients, available_tools
```

When a user sends a message, the app processes it through the agent `invoke_with_prompt()` function. The response from the model is displayed on the Gradio GUI:

```
async def process_message(message, history):
  """Process a message from the user and get a response from the agent"""
  global agent
  if agent is None:
      # First-time initialization
      agent, mcp_clients, available_tools = await initialize_agent()
  try:
      # Process message and get response
      response = await agent.invoke_with_prompt(message)
      # Return the response
      return response
  except Exception as e:
      logger.error(f"Error processing message: {e}")
      return f"I encountered an error: {str(e)}"
```

### MCP client implementation

MCP clients serve as intermediaries between the AI model and the MCP server. Each client maintains a one-to-one session with a server, managing the lifecycle of interactions, including handling interruptions, timeouts, and reconnections. MCP clients route protocol messages bidirectionally between the host application and the server. They parse responses, handle errors, and make sure that the data is relevant and appropriately formatted for the AI model. They also facilitate the invocation of tools exposed by the MCP server and manage the context so that the AI model has access to the necessary resources and tools for its tasks.

The following function in the mcpclient.py file is designed to establish connections to MCP servers and manage connection sessions.

```
async def connect(self):
  """
  Establishes connection to MCP server.
  Sets up stdio client, initializes read/write streams,
  and creates client session.
  """
  # Initialize stdio client with server parameters
  self._client = stdio_client(self.server_params)
  # Get read/write streams
  self.read, self.write = await self._client.__aenter__()
  # Create and initialize session
  session = ClientSession(self.read, self.write)
  self.session = await session.__aenter__()
  await self.session.initialize()
```

After it’s connected with MCP servers, the client lists available tools from each MCP server with their specifications:

```
async def get_available_tools(self):
    """List available tools from the MCP server."""
    if not self.session:
        raise RuntimeError("Not connected to MCP server")
    response = await self.session.list_tools()
    # Extract and format tools
    tools = response.tools if hasattr(response, 'tools') else []
    formatted_tools = [
        {
            'name': tool.name,
            'description': str(tool.description),
            'inputSchema': {
                'json': {
                    'type': 'object',
                    'properties': tool.inputSchema.get('properties', {}),
                    'required': tool.inputSchema.get('required', [])
                }
            }
        }
        for tool in tools
    ]
    return formatted_tools
```

When a tool is defined and called, the client first validates the session is active, then executes the tool through the MCP session that is established between client and server. Finally, it returns the structured response.

```
async def call_tool(self, tool_name, arguments):
    # Execute tool
    start_time = time.time()
    result = await self.session.call_tool(tool_name, arguments=arguments)
    execution_time = time.time() - start_time
    # Augment result with server info
    return {
        "result": result,
        "tool_info": {
            "tool_name": tool_name,
            "server_name": server_name,
            "server_info": server_info,
            "execution_time": f"{execution_time:.2f}s"
        }
    }
```

### MCP server configuration

The server_configs.py file defines the MCP tool servers that our application will connect to. This configuration sets up Google Maps MCP server with an API key, adds a time server for date and time operations, and includes a memory server for storing conversation context. Each server is defined as a `StdioServerParameters` object, which specifies how to launch the server process using Node.js (using npx). You can add or remove MCP server configurations based on your application objectives and requirements.

```
from mcp import StdioServerParameters
SERVER_CONFIGS = [
        StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-google-maps"],
            env={"GOOGLE_MAPS_API_KEY": "<ADD_GOOGLE_API_KEY>"}
        ),
        StdioServerParameters(
            command="npx",
            args=["-y", "time-mcp"],
        ),
        StdioServerParameters(
            command="npx",
            args=["@modelcontextprotocol/server-memory"]
            )
]
```

### Alternative implementation: Strands Agent framework

For developers seeking a more streamlined approach to building MCP-powered applications, the [Strands Agents](https://strandsagents.com/latest/) framework provides an alternative that significantly reduces implementation complexity while maintaining full MCP compatibility. This section demonstrates how the same functionality can be achieved with substantially less code using Strands Agents. The code sample is available in this [Git repository](https://github.com/aws-samples/mistral-on-aws/tree/main/MCP/MCP_Mistral_app_demo_with_Strands).

First, initialize the model and provide the Mistral model ID on Amazon Bedrock.

```
from strands import Agent
from strands.tools.mcp import MCPClient
from strands.models import BedrockModel
# Initialize the Bedrock model
bedrock_model = BedrockModel(
    model_id="us.mistral.pixtral-large-2502-v1:0",
    streaming=False
)
```

The following code creates multiple MCP clients from server configurations, automatically manages their lifecycle using context managers, collects available tools from each client, and initializes an AI agent with the unified set of tools.

```
from contextlib import ExitStack
from mcp import stdio_client
# Create MCP clients with automatic lifecycle management
mcp_clients = [
    MCPClient(lambda cfg=server_config: stdio_client(cfg))
    for server_config in SERVER_CONFIGS
]
with ExitStack() as stack:
    # Enter all MCP clients automatically
    for mcp_client in mcp_clients:
        stack.enter_context(mcp_client)
    
    # Aggregate tools from all clients
    tools = []
    for i, mcp_client in enumerate(mcp_clients):
        client_tools = mcp_client.list_tools_sync()
        tools.extend(client_tools)
        logger.info(f"Loaded {len(client_tools)} tools from client {i+1}")
    
    # Create agent with unified tool registry
    agent = Agent(model=bedrock_model, tools=tools, system_prompt=system_prompt)
```

The following function processes user messages with optional image inputs by formatting them for multimodal AI interaction, sending them to an agent that handles tool routing and response generation, and returning the agent’s text response:

```
def process_message(message, image=None):
    """Process user message with optional image input"""
    try:
        if image is not None:
            # Convert PIL image to Bedrock format
            image_data = convert_image_to_bytes(image)
            if image_data:
                # Create multimodal message structure
                multimodal_message = {
                    "role": "user",
                    "content": [
                        {
                            "image": {
                                "format": image_data['format'],
                                "source": {"bytes": image_data['bytes']}
                            }
                        },
                        {
                            "text": message if message.strip() else "Please analyze the content of the image."
                        }
                    ]
                }
                agent.messages.append(multimodal_message)
        
        # Single call handles tool routing and response generation
        response = agent(message)
        
        # Extract response content
        return response.text if hasattr(response, 'text') else str(response)
        
    except Exception as e:
        return f"Error: {str(e)}"
```

The Strands Agents approach streamlines MCP integration by reducing code complexity, automating resource management, and unifying tools from multiple servers into a single interface. It also offers built-in error handling and native multimodal support, minimizing manual effort and enabling more robust, efficient development.

## Demo

This demo showcases an intelligent food recognition application with integrated location services. Users can submit an image of a dish, and the AI assistant:

- Accurately identifies the cuisine from the image Provides restaurant recommendations based on the identified food Offers route planning powered by the Google Maps MCP server

The application demonstrates sophisticated multi-server collaboration to answer complex queries such as “Is the restaurant open when I arrive?” To answer this, the system:

- Determines the current time in the user’s location using the time MCP server
- Retrieves restaurant operating hours and calculates travel time using the Google Maps MCP server
- Synthesizes this information to provide a clear, accurate response

We encourage you to modify the solution by adding additional MCP server configurations tailored to your specific personal or business requirements.

![MCP applicaiton demo](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/30/ML-18862-blog-post-mcp-demo.gif)

## Clean up

When you finish experimenting with this example, delete the SageMaker endpoints that you created in the process:

- Go to Amazon SageMaker console
- In the left navigation pane, choose **Inference** and then choose **Endpoints**
- From the endpoints list, delete the ones that you created from Amazon Bedrock Marketplace and SageMaker JumpStart.

## Conclusion

This post covers how integrating MCP with Mistral AI models on AWS enables the rapid development of intelligent applications that interact seamlessly with external systems. By standardizing tool use, developers can focus on core logic while keeping AI reasoning and tool execution cleanly separated, improving maintainability and scalability. The Strands Agent framework enhances this by streamlining implementation without sacrificing MCP compatibility. With AWS offering flexible deployment options, from Amazon Bedrock to Amazon Bedrock Marketplace and SageMaker, this approach balances performance and cost. The solution demonstrates how even lightweight setups can connect AI to real-time services.

We encourage developers to build upon this foundation by incorporating additional MCP servers tailored to their specific requirements. As the landscape of MCP-compatible tools continues to expand, organizations can create increasingly sophisticated AI assistants that effectively reason over external knowledge and take meaningful actions, accelerating the adoption of practical, agentic AI systems across industries while reducing implementation barriers.

Ready to implement MCP in your own projects? Explore the official AWS [MCP server repository](https://github.com/awslabs/mcp) for examples and reference implementations. For more information about the Strands Agents framework, which simplifies agent building with its intuitive, code-first approach to data source integration, visit [Strands Agent](https://strandsagents.com/0.1.x/). Finally, dive deeper into open protocols for agent interoperability in the recent AWS blog post: [Open Protocols for Agent Interoperability](https://aws.amazon.com/blogs/opensource/open-protocols-for-agent-interoperability-part-1-inter-agent-communication-on-mcp/), which explores how these technologies are shaping the future of AI agent development.

### About the authors

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2023/11/29/ying_hou-1.jpg)**Ying Hou, PhD,** is a Sr. Specialist Solution Architect for Gen AI at AWS, where she collaborates with model providers to onboard the latest and most intelligent AI models onto AWS platforms. With deep expertise in Gen AI, ASR, computer vision, NLP, and time-series forecasting models, she works closely with customers to design and build cutting-edge ML and GenAI applications.

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/30/Siddhant-Waghjale.jpeg)**Siddhant Waghjale**, is an Applied AI Engineer at Mistral AI, where he works on challenging customer use cases and applied science, helping customers achieve their goals with Mistral models. He’s passionate about building solutions that bridge AI capabilities with actual business applications, specifically in agentic workflows and code generation.

![Samuel-Barry](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/30/Samuel-Barry.jpeg)**Samuel Barry** is an Applied AI Engineer at Mistral AI, where he helps organizations design, deploy, and scale cutting-edge AI systems. He partners with customers to deliver high-impact solutions across a range of use cases, including RAG, agentic workflows, fine-tuning, and model distillation. Alongside engineering efforts, he also contributes to applied research initiatives that inform and strengthen production use cases.

![Preston Tuggle](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/05/17/tuggle.jpeg)**Preston Tuggle** is a Sr. Specialist Solutions Architect with the Third-Party Model Provider team at AWS. He focuses on working with model providers across Amazon Bedrock and Amazon SageMaker, helping them accelerate their go-to-market strategies through technical scaling initiatives and customer engagement.
