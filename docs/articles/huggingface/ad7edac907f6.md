---
vendor: huggingface
title: Gradio MCP Server 的五项重大改进
original_title: Five Big Improvements to Gradio MCP Servers
url: https://huggingface.co/blog/gradio-mcp-updates
date: 2026-04-06
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Gradio MCP Server 的五项重大改进

[Gradio](https://gradio.app) 是用于创建 AI 驱动 Web 应用的开源 Python 包。Gradio 兼容 [MCP server 协议](https://modelcontextprotocol.io/introduction)，为托管在 [Hugging Face Spaces](https://hf.co/spaces) 上的数千个 MCP server 提供支撑。Gradio 团队正在**下重注**，把 Gradio + Spaces 打造为构建和托管 AI 驱动 MCP server 的最佳方式。

为此，以下是自 [5.38.0](https://github.com/gradio-app/gradio/releases/tag/gradio%405.38.0) 版本起 Gradio MCP server 加入的一些重大改进。

## 无缝本地文件支持

如果你尝试过使用一个以文件（图像、视频、音频）作为输入的远程 Gradio MCP server，你可能遇到过这个错误：

之所以发生这种情况，是因为 Gradio 服务器托管在另一台机器上，这意味着任何输入文件都必须通过公开 URL 可访问，才能被远程下载。

虽然把文件托管到线上的方法很多，但它们都会给你的工作流增加一个手动步骤。在 LLM agent 时代，我们难道不该指望 agent 替你处理这些吗？

Gradio 现在内置了一个 **"File Upload" MCP server**，agent 可以用它把文件直接上传到你的 Gradio 应用。如果你的 Gradio MCP server 中有工具需要文件输入，连接文档现在会告诉你如何启动 "File Upload" MCP server：

关于如何使用该服务器（以及重要的安全注意事项），请在 [Gradio Guides](https://www.gradio.app/guides/file-upload-mcp) 中了解更多。

## 实时进度通知

取决于 AI 任务，拿到结果可能需要一段时间。现在，Gradio 会向你的 MCP 客户端**流式推送进度通知**，让你能够实时监控状态！

作为 MCP 开发者，强烈建议在你的 MCP 工具实现中发出这些进度状态。我们的[指南](https://www.gradio.app/guides/building-mcp-server-with-gradio#sending-progress-updates)会告诉你怎么做。

## 一行代码把 OpenAPI 规范转成 MCP

如果你想把已有的后端 API 接入 LLM，就必须手动把 API endpoint 映射为 MCP 工具。这既耗时又容易出错。随着本次发布，Gradio 可以自动完成整个流程！只需一行代码，就能把你的业务后端接入任何兼容 MCP 的 LLM。

[OpenAPI](https://www.openapis.org/) 是以机器可读格式（通常是 JSON 文件）描述 RESTful API 的广泛采用标准。Gradio 现在提供 `gr.load_openapi` 函数，可以直接从 OpenAPI schema 创建 Gradio 应用。然后用 `mcp_server=True` 启动应用，就能自动为你的 API 创建 MCP server！

```
import gradio as gr

demo = gr.load_openapi(
    openapi_spec="https://petstore3.swagger.io/api/v3/openapi.json",
    base_url="https://petstore3.swagger.io/api/v3",
    paths=["/pet.*"],
    methods=["get", "post"],
)

demo.launch(mcp_server=True)
```

更多细节见 Gradio [Guides](https://www.gradio.app/guides/from-openapi-spec)。

## 身份验证改进

MCP server 开发中的一个常见模式，是使用认证 header 代表你的用户调用服务。作为 MCP server 开发者，你希望清晰地向用户说明：要正确使用服务器，他们需要提供哪些凭据。

为此，你现在可以把 MCP server 的参数类型标注为 `gr.Header`。Gradio 会自动从传入请求中提取该 header（如果存在）并传给您的函数。使用 `gr.Header` 的好处是：MCP 连接文档会自动展示连接服务器时需要提供的 header！

在下面的例子中，`X-API-Token` header 会从传入请求中被提取，并作为 `x_api_token` 参数传给 `make_api_request_on_behalf_of_user`。

```
import gradio as gr

def make_api_request_on_behalf_of_user(prompt: str, x_api_token: gr.Header):
    """Make a request to everyone's favorite API.
    Args:
        prompt: The prompt to send to the API.
    Returns:
        The response from the API.
    Raises:
        AssertionError: If the API token is not valid.
    """
    return "Hello from the API" if not x_api_token else "Hello from the API with token!"


demo = gr.Interface(
    make_api_request_on_behalf_of_user,
    [
        gr.Textbox(label="Prompt"),
    ],
    gr.Textbox(label="Response"),
)

demo.launch(mcp_server=True)
```

[![MCP Header Connection Page](https://huggingface.co/datasets/freddyaboulton/bucket/resolve/main/MCPUploadUpdated.png)](https://huggingface.co/datasets/freddyaboulton/bucket/resolve/main/MCPUploadUpdated.png)

更多阅读见 Gradio [Guides](https://www.gradio.app/guides/building-mcp-server-with-gradio#using-the-gr-header-class)。

## 修改工具描述

Gradio 会根据你的函数名和 docstring 自动生成工具描述。现在你可以用 `api_description` 参数进一步自定义工具描述。在这个例子中，工具描述将为 "Apply a sepia filter to any image."。

```
import gradio as gr
import numpy as np

def sepia(input_img):
    """
    Args:
        input_img (np.array): The input image to apply the sepia filter to.

    Returns:
        The sepia filtered image.
    """
    sepia_filter = np.array([
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131]
    ])
    sepia_img = input_img.dot(sepia_filter.T)
    sepia_img /= sepia_img.max()
    return sepia_img

gr.Interface(sepia, "image", "image", 
             api_description="Apply a sepia filter to any image.")\
            .launch(mcp_server=True)
```

更多阅读见[指南](https://www.gradio.app/guides/building-mcp-server-with-gradio#modifying-tool-descriptions)。

## 结论

想让我们给 Gradio 添加新的 MCP 相关功能？在博客评论区或 [GitHub](https://github.com/gradio-app/gradio/issues) 上告诉我们。如果你做了一个很酷的 MCP server 或 Gradio 应用，也欢迎在评论里告诉我们，我们会帮你宣传！
