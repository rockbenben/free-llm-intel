---
vendor: huggingface
title: ScreenEnv：部署你的全栈桌面智能体
original_title: "ScreenEnv: Deploy your full stack Desktop Agent"
url: https://huggingface.co/blog/screenenv
date: 2025-07-11
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: 8d7149898cf9
---

# ScreenEnv：部署你的全栈桌面智能体

作者：Amir Mahla（A-Mahla）、Aymeric Roucher（m-ric）

**TL;DR**：ScreenEnv 是一个强大的 Python 库，让你在 Docker 容器里创建隔离的 Ubuntu 桌面环境，用来测试和部署 GUI 智能体（也叫 Computer Use 智能体，即"电脑操作"智能体）。它内置支持 Model Context Protocol（MCP），部署能看、能点、能操作真实应用的桌面智能体从未如此简单。

## ScreenEnv 是什么？

设想你需要自动化桌面任务、测试 GUI 应用，或者构建一个能和软件交互的 AI 智能体。过去这需要复杂的虚拟机配置和脆弱不堪的自动化框架。

ScreenEnv 改变了这一点：它提供一个运行在 Docker 容器里的**沙箱桌面环境**。你可以把它当成一整场虚拟桌面会话，由你的代码完全掌控——不只是点按钮、敲文字，而是管理整个桌面体验：启动应用、组织窗口、处理文件、执行终端命令、录制整个会话。

## 为什么选 ScreenEnv？

- **🖥️ 完整的桌面控制**：鼠标键盘全量自动化、窗口管理、应用启动、文件操作、终端访问、屏幕录制
- **🤖 双集成模式**：同时支持面向 AI 系统的 Model Context Protocol（MCP）和直接的 Sandbox API——适配任何智能体或后端逻辑
- **🐳 Docker 原生**：无需复杂虚拟机——只要 Docker。环境隔离、可复现，10 秒内轻松部署到任何地方。支持 AMD64 和 ARM64 架构

### 🎯 **一行代码完成配置**

```
from screenenv import Sandbox
sandbox = Sandbox()  # That's it!
```

## 两种集成方式

ScreenEnv 提供**两种互补的集成方式**，让你可以选择最贴合自己架构的路子：

### 方式 1：直接用 Sandbox API

适合自定义智能体框架、已有后端，或者需要细粒度控制的场景：

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

### 方式 2：MCP Server 集成

适合支持 Model Context Protocol 的 AI 系统：

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

这种双轨设计意味着 ScreenEnv 适配你已有的基础设施，而不是逼你重构智能体架构。

## ✨ 用 screenenv 和 smolagents 创建桌面智能体

`screenenv` 原生支持 `smolagents`，可以轻松搭建自己的桌面自动化智能体。只需几步，就能做出你自己的 AI 桌面智能体：

### **1. 选择模型**

挑一个后端 VLM 来驱动你的智能体。

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

### **2. 定义你的自定义桌面智能体**

继承 `DesktopAgentBase` 并实现 `_setup_desktop_tools` 方法，构建你自己的动作空间！

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

### 3. **在桌面任务上运行智能体**

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

> 如果遇到 docker 拒绝访问错误，可以尝试用 `sudo -E python -m test.py` 运行智能体，或把你的用户加入 docker 用户组。

> 💡 完整实现请参考 GitHub 上的 CustomDesktopAgent 源码。

## 现在开始

```
# Install ScreenEnv
pip install screenenv

# Try the examples
git clone git@github.com:huggingface/screenenv.git
cd screenenv
python -m examples.desktop_agent
# use 'sudo -E python -m examples.desktop_agent` if you're not in 'docker' group
```

## 接下来？

ScreenEnv 计划从 Linux 扩展到 **Android、macOS 和 Windows**，解锁真正跨平台的 GUI 自动化。这能让开发者和研究者以极少的配置构建跨环境泛化的智能体。

这些进展也将为创建**可复现的沙箱环境**铺路——它们是基准测试与评估的理想载体。

仓库：[https://github.com/huggingface/screenenv](https://github.com/huggingface/screenenv)
