---
vendor: huggingface
title: ScreenEnv: Deploy your full stack Desktop Agent
original_title: ScreenEnv: Deploy your full stack Desktop Agent
url: https://huggingface.co/blog/screenenv
date: 2025-07-11
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: bcfb3b4f5e0f
---


# ScreenEnv: Deploy your full stack Desktop Agent

					July 10, 2025

Update on GitHub


77

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/630df2bf8df86f1e5bec538c/Cljm7XPueDHHQDIO0461N.jpeg)](https://huggingface.co/hironow)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/j_1BcYB_3v6R59t_LilCN.jpeg)](https://huggingface.co/rahul1493)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/g5cD9CzBJagr34X3T_rxK.png)](https://huggingface.co/Hardik1910)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6455528dfbe00f9e73c14661/rgW33HCYq3-emlf6Zk293.png)](https://huggingface.co/rogerscuall)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/65e5d45cf09dfaab9b0ef691/kYVh_LVcrV5_uk-ITtU5o.jpeg)](https://huggingface.co/DarrenHuangTW)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63d10d4e8eaa4831005e92b5/7p7-OmWM6PqqCs7ZStPGD.jpeg)](https://huggingface.co/m-ric)

Amir Mahla

A-Mahla

Aymeric Roucher

m-ric

**TL;DR**: ScreenEnv is a powerful Python library that lets you create isolated Ubuntu desktop environments in Docker containers for testing and deploying GUI Agents (aka Computer Use agents). With built-in support for the Model Context Protocol (MCP), it's never been easier to deploy desktop agents that can see, click, and interact with real applications.

## What is ScreenEnv?

Imagine you need to automate desktop tasks, test GUI applications, or build an AI agent that can interact with software. This used to require complex VM setups and brittle automation frameworks.

ScreenEnv changes this by providing a **sandboxed desktop environment** that runs in a Docker container. Think of it as a complete virtual desktop session that your code can fully control - not just clicking buttons and typing text, but managing the entire desktop experience including launching applications, organizing windows, handling files, executing terminal commands, and recording the entire session.

## Why ScreenEnv?

- **🖥️ Full Desktop Control**: Complete mouse and keyboard automation, window management, application launching, file operations, terminal access, and screen recording
- **🤖 Dual Integration Modes**: Support both Model Context Protocol (MCP) for AI systems and direct Sandbox API - adapting to any agent or backend logic
- **🐳 Docker Native**: No complex VM setup - just Docker. The environment is isolated, reproducible, and easily deployed anywhere in less than 10 seconds. Support AMD64 and ARM64 architecture.

### 🎯 **One-Line Setup**

```
from screenenv import Sandbox
sandbox = Sandbox()  # That's it!
```

## Two Integration Approaches

ScreenEnv provides **two complementary ways** to integrate with your agents and backend systems, giving you flexibility to choose the approach that best fits your architecture:

### Option 1: Direct Sandbox API

Perfect for custom agent frameworks, existing backends, or when you need fine-grained control:

```
from screenenv import Sandbox

# Direct programmatic control
sandbox = Sandbox(headless=False)
sandbox.launch("xfce4-terminal")
sandbox.write("echo 'Custom agent logic'")
screenshot = sandbox.screenshot()
image = Image.open(BytesIO(screenshot_bytes))
...
sandbox.close()
# If close() isn’t called, you might need to shut down the container yourself.
```

### Option 2: MCP Server Integration

Ideal for AI systems that support the Model Context Protocol:

```
from screenenv import MCPRemoteServer
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Start MCP server for AI integration
server = MCPRemoteServer(headless=False)
print(f"MCP Server URL: {server.server_url}")

# AI agents can now connect and control the desktop
async def mcp_session():
    async with streamablehttp_client(server.server_url) as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()
            print(await session.list_tools())

            response = await session.call_tool("screenshot", {})
            image_bytes = base64.b64decode(response.content[0].data)
            image = Image.open(BytesIO(image_bytes))

server.close()
# If close() isn’t called, you might need to shut down the container yourself.
```

This dual approach means ScreenEnv adapts to your existing infrastructure rather than forcing you to change your agent architecture.

## ✨ Create a Desktop Agent with screenenv and smolagents

`screenenv` natively supports `smolagents`, making it easy to build your own custom Desktop Agent for automation. Here’s how to create your own AI-powered Desktop Agent in just a few steps:

### **1. Choose Your Model**

Pick the backend VLM you want to power your agent.

```
import os

from smolagents import OpenAIServerModel
model = OpenAIServerModel(
    model_id="gpt-4.1",
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Inference Endpoints
from smolagents import HfApiModel
model = HfApiModel(
    model_id="Qwen/Qwen2.5-VL-7B-Instruct",
    token=os.getenv("HF_TOKEN"),
    provider="nebius",
)

# Transformer models
from smolagents import TransformersModel
model = TransformersModel(
    model_id="Qwen/Qwen2.5-VL-7B-Instruct",
    device_map="auto",
    torch_dtype="auto",
    trust_remote_code=True,
)

# Other providers
from smolagents import LiteLLMModel
model = LiteLLMModel(model_id="anthropic/claude-sonnet-4-20250514")

# see smolagents to get the list of available model connectors
```

### **2. Define Your Custom Desktop Agent**

Inherit from `DesktopAgentBase` and implement the `_setup_desktop_tools` method to build your own action space!

```
from screenenv import DesktopAgentBase, Sandbox
from smolagents import Model, Tool, tool
from smolagents.monitoring import LogLevel
from typing import List

class CustomDesktopAgent(DesktopAgentBase):
    """Agent for desktop automation"""

    def __init__(
        self,
        model: Model,
        data_dir: str,
        desktop: Sandbox,
        tools: List[Tool] | None = None,
        max_steps: int = 200,
        verbosity_level: LogLevel = LogLevel.INFO,
        planning_interval: int | None = None,
        use_v1_prompt: bool = False,
        **kwargs,
    ):
        super().__init__(
            model=model,
            data_dir=data_dir,
            desktop=desktop,
            tools=tools,
            max_steps=max_steps,
            verbosity_level=verbosity_level,
            planning_interval=planning_interval,
            use_v1_prompt=use_v1_prompt,
            **kwargs,
        )

        # OPTIONAL: Add a custom prompt template - see src/screenenv/desktop_agent/desktop_agent_base.py for more details about the default prompt template
        # self.prompt_templates["system_prompt"] = CUSTOM_PROMPT_TEMPLATE.replace(
        #     "<<resolution_x>>", str(self.width)
        # ).replace("<<resolution_y>>", str(self.height))
        # Important: Adjust the prompt based on your action space to improve results.

    def _setup_desktop_tools(self) -> None:
        """Define your custom tools here."""
        
        
        @tool
        def click(x: int, y: int) -> str:
            """
            Clicks at the specified coordinates.
            Args:
                x: The x-coordinate of the click
                y: The y-coordinate of the click
            """
            self.desktop.left_click(x, y)
            # self.click_coordinates = (x, y) to add the click coordinate to the observation screenshot 
            return f"Clicked at ({x}, {y})"
        
        self.tools["click"] = click
        

        @tool
        def write(text: str) -> str:
            """
            Types the specified text at the current cursor position.
            Args:
                text: The text to type
            """
            self.desktop.write(text, delay_in_ms=10)
            return f"Typed text: '{text}'"

        self.tools["write"] = write

        @tool
        def press(key: str) -> str:
            """
            Presses a keyboard key or combination of keys
            Args:
                key: The key to press (e.g. "enter", "space", "backspace", etc.) or a multiple keys string to press, for example "ctrl+a" or "ctrl+shift+a".
            """
            self.desktop.press(key)
            return f"Pressed key: {key}"

        self.tools["press"] = press
        
        @tool
        def open(file_or_url: str) -> str:
            """
            Directly opens a browser with the specified url or opens a file with the default application.
            Args:
                file_or_url: The URL or file to open
            """

            self.desktop.open(file_or_url)
            # Give it time to load
            self.logger.log(f"Opening: {file_or_url}")
            return f"Opened: {file_or_url}"

        @tool
        def launch_app(app_name: str) -> str:
            """
            Launches the specified application.
            Args:
                app_name: The name of the application to launch
            """
            self.desktop.launch(app_name)
            return f"Launched application: {app_name}"

        self.tools["launch_app"] = launch_app

        ... # Continue implementing your own action space.
```

### 3. **Run the Agent on a Desktop Task**

```
from screenenv import Sandbox

# Define your sandbox environment
sandbox = Sandbox(headless=False, resolution=(1920, 1080))

# Create your agent
agent = CustomDesktopAgent(
    model=model,
    data_dir="data",
    desktop=sandbox,
)

# Run a task
task = "Open LibreOffice, write a report of approximately 300 words on the topic ‘AI Agent Workflow in 2025’, and save the document."

result = agent.run(task)
print(f"📄 Result: {result}")

sandbox.close()
```

> If you encounter acces denied docker error, you can try to run the agent with sudo -E python -m test.py or add your user to the docker group.

> 💡 For a comprehensive implementation, see this CustomDesktopAgent source on GitHub.

## Get Started Today

```
# Install ScreenEnv
pip install screenenv

# Try the examples
git clone git@github.com:huggingface/screenenv.git
cd screenenv
python -m examples.desktop_agent
# use 'sudo -E python -m examples.desktop_agent` if you're not in 'docker' group
```

## What's Next?

ScreenEnv aims to expand beyond Linux to support **Android, macOS, and Windows**, unlocking true cross-platform GUI automation. This will enable developers and researchers to build agents that generalize across environments with minimal setup.

These advancements pave the way for creating **reproducible, sandboxed environments** ideal for benchmarking and evaluation.

Repository: [https://github.com/huggingface/screenenv](https://github.com/huggingface/screenenv)

More Articles from our Blog

open-responses

responses

open-source

## Open Responses: What you need to know

- ![](https://huggingface.co/avatars/909635453bf62a2a7118a01dd51b811c.svg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/62d648291fa3e4e7ae3fa6e8/oatOwf8Xqe5eDbCSuYqCd.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6141a88b3a0ec78603c9e784/DJsxSmWV39M33JFheLobC.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)

114

January 15, 2026

agents

gui

vlm

## Smol2Operator: Post-Training GUI Agents for Computer Use

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/67f2f500e329a81a62a05d44/DOlzc8GFQzrnfVrsOdtbN.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6141a88b3a0ec78603c9e784/DJsxSmWV39M33JFheLobC.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/61929226ded356549e20c5da/ONUjP2S5fUWd07BiFXm0i.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1655385361868-61b85ce86eb1f2c5e6233736.jpeg)
- +1

139

September 23, 2025

### Community

tc-wolf

Jul 11, 2025

This is really cool, would love to play around with this and see if can get running on Mac OS w/ a local MCP server and tool call implementations.

Where are the existing tool call implementations for clicking, screenshots, etc. implemented?

I.e., I see a method for `left_click` in the sandbox class, but these are all making requests to the IP address from the Docker Provider (?):

```
def left_click(self, x: Optional[int] = None, y: Optional[int] = None):
    """
    Clicks the left button of the mouse at the specified coordinates.
    """
    self._make_request("POST", "/left_click", params={"x": x, "y": y})
```

I can see the Docker image `amhma/ubuntu-desktop:22.04-0.0.1-dev` is used, but the server code (if that lives there) and Dockerfile would that would be very helpful (especially to rebuild and run with an aarch64 Linux image).

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/67f2f500e329a81a62a05d44/DOlzc8GFQzrnfVrsOdtbN.png)](https://huggingface.co/A-Mahla)
- [![](https://huggingface.co/avatars/ec1886b40f507ad01964c519133ba701.svg)](https://huggingface.co/tc-wolf)


A-Mahla

Article author

Jul 11, 2025


edited Jul 11, 2025

Hi [@tc-wolf](https://huggingface.co/tc-wolf) .
Thanks for your interest! We’re actively working toward open-sourcing the Docker image. Once we have a stable version ready to share.
However, you can already use the Docker image on Mac with the arm64 architecture. The image supports both amd64 and arm64 (aarch64). Have you already tested it on your macOS?

deleted

Jul 11, 2025


This comment has been hidden

YacineMk

Jul 16, 2025


edited Jul 16, 2025

Amazing work as always, thank you to the HuggingFace team!
Is there any sort of roadmap or discord community server for this library?
I am currently working on a multi-agent system (with smolagents) for computer-use. Usually my test-suite runs locally, and I was just looking for a way to make it run in conteneurized environments for consistency and reproducibility, so this is perfect!
I would love to get in closer contact with the team working on this and contribute.

nageshsomayajula

Aug 1, 2025

very useful !!

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fscreenenv) or [log in](https://huggingface.co/login?next=%2Fblog%2Fscreenenv) to comment


77

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/630df2bf8df86f1e5bec538c/Cljm7XPueDHHQDIO0461N.jpeg)](https://huggingface.co/hironow)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/j_1BcYB_3v6R59t_LilCN.jpeg)](https://huggingface.co/rahul1493)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/g5cD9CzBJagr34X3T_rxK.png)](https://huggingface.co/Hardik1910)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6455528dfbe00f9e73c14661/rgW33HCYq3-emlf6Zk293.png)](https://huggingface.co/rogerscuall)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/65e5d45cf09dfaab9b0ef691/kYVh_LVcrV5_uk-ITtU5o.jpeg)](https://huggingface.co/DarrenHuangTW)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63d10d4e8eaa4831005e92b5/7p7-OmWM6PqqCs7ZStPGD.jpeg)](https://huggingface.co/m-ric)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/67f2f500e329a81a62a05d44/DOlzc8GFQzrnfVrsOdtbN.png)](https://huggingface.co/A-Mahla)
- [![](https://huggingface.co/avatars/dc736bc9f749ef69e1b7fca8ed0584f6.svg)](https://huggingface.co/chongxi666)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/660bc459d81d6112496f30f8/jMrpAckFyg-_iHMI7sn2h.jpeg)](https://huggingface.co/eustlb)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6821b385525882a5706eed20/R8BdCB6qwmlaHgYtwu_hB.jpeg)](https://huggingface.co/h-tonywu)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6663093dc7adb6d708d27a49/1yOQD8ibhfyiZUs6pzGXU.jpeg)](https://huggingface.co/ErwandKer)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/66a9e76d8b6380ffd5d7cc00/eYeqz2onGhaAcL0qv_8zL.png)](https://huggingface.co/chmadran)
