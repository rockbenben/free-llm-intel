---
vendor: aws_bedrock
title: Build an MCP application with Mistral models on AWS
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/build-an-mcp-application-with-mistral-models-on-aws
date: 2025-07-10
lang: zh
captured: 2026-11-22
extractor: readability-v1
translator: agent
status: translated
body_sha: 6ef779874cd5
---

# 在 AWS 上使用 Mistral 模型构建 MCP 应用

*本文由来自 Mistral AI 的 Siddhant Waghjale 与 Samuel Barry 共同撰写。*

[Model Context Protocol](https://modelcontextprotocol.io/introduction)（MCP）是一项近几个月来获得显著关注的标准。从高层看，它由一套标准化接口组成，旨在简化并增强 AI 模型与外部数据源和系统交互的方式。MCP 不采用硬编码的检索与动作逻辑，也不依赖一次性的工具，而是提供一种结构化的方式，把上下文数据（例如用户档案、环境元数据或第三方内容）传入[大语言模型](https://aws.amazon.com/what-is/large-language-model/)（LLM）的上下文，并把模型的输出路由到外部系统。对开发者来说，MCP 抽象掉了集成复杂度，并形成一个统一的层，用于注入外部知识与执行模型动作，从而让构建健壮、高效的 agentic AI 系统更直截了当，且这些系统与取数逻辑保持解耦。

[Mistral AI](https://mistral.ai/) 是一家前沿研究实验室，2023 年崛起为[生成式 AI](https://aws.amazon.com/generative-ai/) 领域领先的开源竞争者。Mistral 发布了许多最先进的模型，从早期的 Mistral 7B 和 Mixtral，到最近公布的 Mistral Medium 3 与 Small 3——在此过程中切实推动了混合专家架构的普及。Mistral 模型通常被形容为极其高效且用途广泛，常常以极低的成本达到最先进的性能水平。这些模型如今已无缝集成到 [Amazon Web Services](https://aws.amazon.com/)（AWS）的各项服务中，为开发者和企业解锁了强大的部署选项。通过 [Amazon Bedrock](https://aws.amazon.com/bedrock/)，用户可以用全托管的 API 访问 Mistral 模型，无需管理基础设施即可快速做原型验证。[Amazon Bedrock Marketplace](https://aws.amazon.com/bedrock/marketplace/) 进一步扩展了这一点，支持快速发现模型、完成授权，并将其集成到既有工作流中。对于希望微调或自定义训练的高级用户，[Amazon SageMaker JumpStart](https://aws.amazon.com/sagemaker-ai/jumpstart/) 提供了一个精简的环境，可借助 AWS 可扩展的基础设施，用自己的数据定制 Mistral 模型。这一集成让在广泛的应用场景中试验、扩展并把 Mistral 模型投入生产比以往更快。

本文演示如何在 AWS 上借助 MCP 使用 Mistral AI 模型构建一个智能 AI 助手，它整合实时位置服务、时间数据与上下文记忆来处理复杂的多模态查询。这一用例以餐厅推荐为例，但通过修改 MCP 服务器配置以连接你特定的数据源与业务系统，这个可扩展的框架也可以适配企业用例。

## 方案概览

本方案使用 Amazon Bedrock 上的 Mistral 模型来理解用户查询，并把查询路由到相关的 MCP 服务器，从而给出准确、最新的回答。系统遵循如下总体流程：

- **用户输入** – 用户通过基于终端的或基于 Web 的 Gradio 界面发送查询（文本、图像或两者兼有）
- **图像处理** – 如果检测到图像，系统会对其进行处理并为 AI 模型优化
- **模型请求** – 查询连同相应的系统指令被发送到 Amazon Bedrock [Converse API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html)
- **工具检测** – 如果模型判断需要外部数据，它会请求调用工具
- **工具执行** – 系统把工具请求路由到相应的 MCP 服务器并执行
- **响应生成** – 模型结合工具结果生成全面的回答
- **响应投递** – 最终答案展示给用户

在本示例中，我们以餐厅或地点推荐以及路线规划这一通用用例来演示 MCP 框架。用户可以输入多模态内容（例如文本加图像），应用则集成了 [Google Maps](https://www.npmjs.com/package/@modelcontextprotocol/server-google-maps)、[Time](https://github.com/yokingma/time-mcp) 与 [Memory](https://github.com/modelcontextprotocol/servers/tree/main/src/memory) 三个 MCP 服务器。此外，本文还展示了如何使用 [Strands Agent](https://strandsagents.com/latest/) 框架作为另一种方式，以显著降低的复杂度与代码量构建同一个 MCP 应用。Strands Agent 是一个开源的多 agent 协同框架，可简化跨多个领域构建智能、具备上下文感知能力的 agent 系统。你可以修改 MCP 服务器配置以适配自己的具体需求，从而构建自己的 MCP 应用。你可以在我们的 [Git 仓库](https://github.com/aws-samples/mistral-on-aws/tree/main/MCP/MCP_Mistral_app_demo) 中找到本示例的完整源代码。下图是方案架构。

![连接 UI 与 Bedrock 基础模型的 MCP 模块架构，包含 Host、Clients、Servers 组件](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/30/ML-18862-image-1.png)

## 前提条件

在实现本示例之前，你需要先准备好账户与环境。请按以下步骤操作。要设置 AWS 账户：

- 创建一个 AWS 账户。如果你还没有，请在 [https://aws.amazon.com](https://aws.amazon.com/) 注册
- 要启用 Amazon Bedrock 访问权限，请前往 Amazon Bedrock 控制台，为你计划使用的模型申请访问权限（本次演示中请申请 Mistral Pixtral Large 的访问权限）。或者从 Amazon Bedrock Marketplace 部署 Mistral Small 3 模型。（更多细节请参阅本文后面的 **AWS 上的 Mistral 模型部署** 一节。）申请获批后，你就可以通过 Amazon Bedrock Converse API 使用这些模型

要设置本地环境：

- 安装所需的工具：Python 3.10 或更高版本、Node.js（MCP 工具服务器需要）以及 [AWS Command Line Interface](https://aws.amazon.com/cli/)（AWS CLI），配置过程中需要用到后者
- 克隆[仓库](https://github.com/aws-samples/mistral-on-aws/tree/main/MCP/MCP_Mistral_app_demo)：

```
git clone https://github.com/aws-samples/mistral-on-aws.git
cd mistral-on-aws/MCP/MCP_Mistral_app_demo/
```

- 安装 Python 依赖：

```
pip install -r requirements.txt
```

- 配置 AWS 凭证：

```
aws configure
```

然后输入你的 AWS 访问密钥 ID、私有访问密钥，以及首选的 [AWS 区域](https://docs.aws.amazon.com/glossary/latest/reference/glos-chap.html#region)。

- 设置 MCP 工具服务器。服务器配置放在文件：`server_configs.py` 中。系统使用基于 Node.js 的 MCP 服务器。它们会在你首次用 NPM 运行应用时自动安装。你可以在此文件中添加其他 MCP 服务器配置。本方案可以快速修改和扩展，以满足你的业务需求。

## AWS 上的 Mistral 模型部署

Mistral 模型可以通过以下方式访问或部署。要在 MCP 应用中使用[基础模型](https://aws.amazon.com/what-is/foundation-models/)（FM），模型必须支持工具使用功能。

### Amazon Bedrock 无服务器（Pixtral Large）

要启用该模型，请按以下步骤操作：

- 前往 Amazon Bedrock 控制台。
- 在左侧导航窗格中选择 **Model access**。
- 选择 **Manage model access**。
- 以关键词 **Pixtral** 搜索该模型，选中它并选择 **Next**，如下图所示。该模型随后即可使用。

该模型已启用跨区域推理。使用模型 ID 时，务必在模型 ID 前加上区域前缀 `eu` 或 `us`，例如 `eu.mistral.pixtral-large-2502-v1:0`。请在 config.py 中提供这个模型 ID。现在你就可以用基于 Web 的 Gradio 应用测试本示例了。

![Amazon Bedrock 中管理基础模型访问权限的界面，其中 Pixtral Large 模型被高亮](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/30/ML-18862-image-2.png)

### Amazon Bedrock Marketplace（Mistral-Small-24B-Instruct-2501）

Amazon Bedrock Marketplace 与 SageMaker JumpStart 的部署都是专用实例（serverful），只要实例仍在部署状态就会计费。更多信息请参阅 [Amazon Bedrock 定价](https://aws.amazon.com/bedrock/pricing/) 与 [Amazon SageMaker 定价](https://aws.amazon.com/sagemaker/pricing/)。

要启用该模型，请按以下步骤操作：

- 前往 Amazon Bedrock 控制台
- 在左侧导航窗格中选择 **Model catalog**
- 在搜索栏中搜索“Mistral-Small-24B-Instruct-25-1”，如下图所示

![Amazon Bedrock 界面，展示模型目录、筛选器以及 Mistral-Small-24B-Instruct-2501 模型](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/30/ML-18862-image-3.png)

- 选中该模型并选择 **Deploy**。
- 在配置页面中，所有字段都可以保持默认值。该端点需要 ml.g6.12xlarge 实例类型。请在 Amazon SageMaker 服务下检查服务配额，确保你有两个以上实例可用于端点（你还会用另一个实例做 Amazon SageMaker JumpStart 部署）。如果没有两个以上实例，请为该实例类型申请提高配额。然后选择 **Deploy**。模型部署可能需要几分钟。
- 模型进入运行状态后，复制端点的 Amazon Resource Name（ARN），如下图所示，并把它加到 config.py 文件的 `model_id` 字段中。然后你就可以用基于 Web 的 Gradio 应用测试本方案。
- Mistral-Small-24B-Instruct-25-1 模型不支持图像输入，因此只支持基于文本的问答。

![AWS Bedrock Marketplace 部署界面，展示工作流步骤与处于活动状态的 Mistral 端点](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/30/ML-18862-image-4.png)

### Amazon SageMaker JumpStart（Mistral-Small-24B-Instruct-2501）

要启用该模型，请按以下步骤操作：

- 前往 Amazon SageMaker 控制台
- 创建一个域和用户配置文件
- 在所创建的用户配置文件下启动 Studio
- 在左侧导航窗格中选择 **JumpStart**，然后搜索“Mistral”
- 选择 **Mistral-Small-24B-Instruct-2501**，然后选择 **Deploy**

该部署可能需要几分钟。下图显示该模型被标记为 **Bedrock ready**。这意味着你可以把这个模型注册为 Amazon Bedrock Marketplace 部署，并使用 Amazon Bedrock API 调用这个 Amazon SageMaker 端点。

![深色主题的 SageMaker 仪表盘，展示状态为 Bedrock ready 的 Mistral AI 模型](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/30/ML-18862-image-5.png)

- 模型进入运行状态后，从 Amazon Bedrock Marketplace 部署中复制其端点 ARN，如下图所示，并在 config.py 文件的 `model_id` 字段中提供它。然后你就可以用基于 Web 的 Gradio 应用测试本方案。

Mistral-Small-24B-Instruct-25-1 模型不支持图像输入，因此只支持基于文本的问答。

![Mistral Small 模型在 ml.g6 实例上带 AllTraffic 变体的 SageMaker 实时推理端点](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/30/ML-18862-image-6.png)

## 在 AWS 上使用 Mistral 模型构建 MCP 应用

以下各节以组件级的视角，深入讲解如何从零开始构建 MCP 应用。我们会探讨如何实现三个核心 MCP 组件——MCP host、MCP 客户端与 MCP 服务器——让你对底层架构有完整的控制与理解。

### MCP host 组件

MCP 旨在促进 AI 模型与外部工具、系统和数据源之间的无缝交互。在这一架构中，MCP host 在管理 MCP 客户端与服务器的生命周期和编排方面起着关键作用，使 AI 应用能够有效地访问并使用外部资源。MCP host 负责与 FM 集成，提供上下文、能力发现、初始化以及 MCP 客户端管理。在本方案中，我们用三个文件来提供这一能力。

第一个文件是 agent.py。`agent.py` 中的 `BedrockConverseAgent` 类是与 Amazon Bedrock 服务通信并完成 FM 模型集成的核心组件。构造函数用模型配置初始化 agent，并创建 AWS Bedrock 客户端。

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

随后，agent 借助其图像处理能力智能地处理多模态输入。该方法会校验用户提供的图像 URL、下载图像、检测并规范化图像格式、把过大的图像调整为符合 API 约束的尺寸，并将不兼容的格式转换为 JPEG。

```
async def _fetch_image_from_url(self, image_url):
    # Download image from URL
    # Process and optimize for model compatibility
    # Return binary image data with MIME type
```

当用户输入 prompt 时，agent 会在 `invoke_with_prompt` 函数中检测其中是否包含上传的图像或图像 URL，并做相应处理。这样，用户可以在查询中粘贴图像 URL，或从本地设备上传图像，交给 AI 模型分析。

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

最强大的特性是 agent 能够使用 MCP 服务器提供的外部工具。当模型希望使用某个工具时，agent 会从 Amazon Bedrock 检测到 `tool_use` 这一停止原因，并提取工具请求的细节，包括名称与输入。随后它通过 `UtilityHelper` 执行该工具，工具使用结果再回传给模型。MCP host 之后带着已并入的工具结果继续对话。

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

第二个文件是 utility.py。utility.py 中的 `UtilityHelper` 类充当 Amazon Bedrock 与外部工具之间的桥梁。它负责工具注册、把工具规格格式化为 Bedrock 可兼容的形式，以及工具执行。

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

为了让 Amazon Bedrock 理解 MCP 服务器上可用的工具，效用模块在下面的函数中通过提供名称、描述和 `inputSchema` 来生成工具规格：

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

当模型请求某个工具时，效用模块会执行它并格式化结果：

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

MCP host 的最后一个组件是 `gradio_app.py` 文件，它用 Gradio 为我们的 AI 助手实现了一个基于 Web 的界面。它先初始化模型配置与 agent，然后连接 MCP 服务器并从这些 MCP 服务器获取可用工具。

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

当用户发送消息时，应用通过 agent 的 `invoke_with_prompt()` 函数处理该消息。模型的响应会显示在 Gradio GUI 上：

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

### MCP 客户端实现

MCP 客户端充当 AI 模型与 MCP 服务器之间的中介。每个客户端与一个服务器维持一对一的会话，管理交互的生命周期，包括处理中断、超时和重连。MCP 客户端在宿主应用与服务器之间双向路由协议消息。它们解析响应、处理错误，并确保数据与 AI 模型相关且格式恰当。它们还负责调用 MCP 服务器暴露的工具，并管理上下文，使 AI 模型能够获得完成任务所需的资源与工具。

mcpclient.py 文件中的以下函数用于建立与 MCP 服务器的连接并管理连接会话。

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

与 MCP 服务器连接之后，客户端会列出每个 MCP 服务器上可用的工具及其规格：

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

当某个工具被定义并调用时，客户端会先校验会话处于活动状态，然后通过客户端与服务器之间建立的 MCP 会话执行该工具。最后返回结构化的响应。

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

### MCP 服务器配置

server_configs.py 文件定义了我们的应用将要连接的 MCP 工具服务器。该配置用 API key 设置 Google Maps MCP 服务器，添加一个用于日期与时间操作的时间服务器，并包含一个用于存储对话上下文的记忆服务器。每个服务器都定义为一个 `StdioServerParameters` 对象，其中指定了如何使用 Node.js（通过 npx）启动服务器进程。你可以根据应用目标与需求增删 MCP 服务器配置。

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

### 另一种实现：Strands Agent 框架

对于希望以更精简的方式构建由 MCP 驱动的应用的开发者，[Strands Agents](https://strandsagents.com/latest/) 框架提供了一个替代方案，在保持完整 MCP 兼容性的同时显著降低实现复杂度。本节演示如何用 Strands Agents 以少得多的代码实现同样的功能。代码示例见这个 [Git 仓库](https://github.com/aws-samples/mistral-on-aws/tree/main/MCP/MCP_Mistral_app_demo_with_Strands)。

首先，初始化模型并提供 Amazon Bedrock 上的 Mistral 模型 ID。

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

以下代码根据服务器配置创建多个 MCP 客户端，用上下文管理器自动管理它们的生命周期，收集每个客户端的可用工具，并用统一的工具集初始化一个 AI agent。

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

以下函数处理带有可选图像输入的用户消息：把消息格式化为适合多模态 AI 交互的形式，发送给负责工具路由与响应生成的 agent，并返回 agent 的文本响应：

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

Strands Agents 的方式通过降低代码复杂度、自动化资源管理，并把来自多个服务器的工具统一到单一接口，从而精简了 MCP 集成。它还提供内置的错误处理与原生的多模态支持，最大限度减少手工工作，支持更健壮、更高效的开发。

## 演示

本演示展示了一个集成了位置服务的智能食物识别应用。用户可以提交一张菜品的图像，AI 助手会：

- 从图像中准确识别菜系，根据识别出的食物给出餐厅推荐，并提供由 Google Maps MCP 服务器驱动的路线规划

该应用展示了多个服务器之间的精细协作，以回答诸如“我到达时这家餐厅还营业吗？”这样的复杂查询。为此，系统会：

- 使用 time MCP 服务器确定用户所在位置的当前时间
- 使用 Google Maps MCP 服务器获取餐厅营业时间并计算通行时间
- 综合这些信息给出清晰、准确的回答

我们鼓励你通过添加适合自己个人或业务需求的额外 MCP 服务器配置来修改本方案。

![MCP 应用演示](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/30/ML-18862-blog-post-mcp-demo.gif)

## 清理

在完成对本示例的试验后，请删除在此过程中创建的 SageMaker 端点：

- 前往 Amazon SageMaker 控制台
- 在左侧导航窗格中选择 **Inference**，然后选择 **Endpoints**
- 在端点列表中，删除你从 Amazon Bedrock Marketplace 与 SageMaker JumpStart 创建的那些端点。

## 结论

本文介绍了在 AWS 上把 MCP 与 Mistral AI 模型集成，如何支撑快速开发出能与外部系统无缝交互的智能应用。通过标准化工具使用，开发者可以专注于核心逻辑，同时让 AI 推理与工具执行保持清晰的分离，从而提升可维护性与可扩展性。Strands Agent 框架在不牺牲 MCP 兼容性的前提下精简了实现，进一步强化了这一点。AWS 提供了从 Amazon Bedrock 到 Amazon Bedrock Marketplace 与 SageMaker 的灵活部署选项，使这一方式在性能与成本之间取得平衡。本方案说明，即便是轻量的配置，也能把 AI 连接到实时服务。

我们鼓励开发者在这个基础上继续构建，纳入针对自身具体需求的额外 MCP 服务器。随着 MCP 兼容工具的生态不断扩展，组织可以打造出日益精密的 AI 助手，有效地在外部知识上推理并采取有意义的行动，在降低实现门槛的同时，加速在各行各业落地实用的 agentic AI 系统。

准备在你自己的项目中实现 MCP 了吗？浏览官方的 AWS [MCP 服务器仓库](https://github.com/awslabs/mcp) 获取示例与参考实现。想了解更多关于 Strands Agents 框架的信息——它以直观的代码优先方式简化了数据源集成与 agent 构建——请访问 [Strands Agent](https://strandsagents.com/0.1.x/)。最后，想更深入地了解 agent 互操作的开放协议，请阅读最近这篇 AWS 博客文章：[Open Protocols for Agent Interoperability](https://aws.amazon.com/blogs/opensource/open-protocols-for-agent-interoperability-part-1-inter-agent-communication-on-mcp/)，其中探讨了这些技术如何塑造 AI agent 开发的未来。

### 关于作者

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2023/11/29/ying_hou-1.jpg)**Ying Hou, PhD,** 是 AWS 的生成式 AI 高级专家解决方案架构师，与模型提供方合作，把最新、最智能的 AI 模型引入 AWS 平台。她在生成式 AI、ASR、计算机视觉、NLP 以及时序预测模型方面有深厚专长，与客户紧密合作，设计和构建前沿的机器学习与生成式 AI 应用。

![](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/30/Siddhant-Waghjale.jpeg)**Siddhant Waghjale**，是 Mistral AI 的应用 AI 工程师，负责处理有挑战性的客户用例与应用科学研究，帮助客户借助 Mistral 模型达成目标。他热衷于构建把 AI 能力与实际业务应用连接起来的方案，尤其是在 agentic 工作流与代码生成方面。

![Samuel-Barry](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2025/06/30/Samuel-Barry.jpeg)**Samuel Barry** 是 Mistral AI 的应用 AI 工程师，帮助组织设计、部署并扩展前沿的 AI 系统。他与客户合作，在一系列用例中交付高影响力的方案，包括 RAG、agentic 工作流、微调与模型蒸馏。除工程工作外，他还参与应用研究项目，为生产用例提供依据并强化其实践。

![Preston Tuggle](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2024/05/17/tuggle.jpeg)**Preston Tuggle** 是 AWS 第三方模型提供方团队的高级专家解决方案架构师。他专注于与 Amazon Bedrock 和 Amazon SageMaker 上的模型提供方合作，通过技术规模化举措与客户互动，帮助他们加速 go-to-market 策略。
