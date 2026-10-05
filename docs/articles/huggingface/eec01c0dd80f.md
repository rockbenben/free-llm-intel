---
vendor: huggingface
title: 推出 Daggr：以编程方式串联应用，以可视化方式检查
original_title: Introducing Daggr: Chain apps programmatically, inspect visually
url: https://huggingface.co/blog/daggr
date: 2026-02-24
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 1f2793ffcb99
translator: agent
---

返回文章列表

# 推出 Daggr：以编程方式串联应用，以可视化方式检查

发布于
					2026 年 1 月 29 日

在 GitHub 上更新

点赞

107

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/608aabf24955d2bfc3cd99c6/-YxmtpzEmf3NKOTktODRP.jpeg)](https://huggingface.co/ariG23498)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63e24395419922d5a6d7a6cc/bOFr0La0VdpIZ06-ZWJa4.jpeg)](https://huggingface.co/emredeveloper)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1621947938344-noauth.png)](https://huggingface.co/abidlabs)
- [![](https://huggingface.co/avatars/85bb740aa905416c52d3e70fd433bd24.svg)](https://huggingface.co/Gabriel)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)](https://huggingface.co/pcuenq)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/648a374f00f7a3374ee64b99/YPwSOrronoozwHbJchPn3.jpeg)](https://huggingface.co/cfahlgren1)

merve

merve

yuvraj sharma

ysharma

Abubakar Abid

abidlabs

hysts

hysts

Pedro Cuenca

pcuenq

**TL;DR：** [Daggr](https://github.com/gradio-app/daggr) 是一个全新的开源 Python 库，用于构建连接 Gradio 应用、ML 模型和自定义函数的 AI 工作流。它会自动生成一个可视化画布，你可以在里面查看中间输出、单独重跑某个步骤、管理复杂流水线的状态——而这一切只需几行 Python 代码！

## 目录

- [背景](https://huggingface.co/blog/daggr#background)
- [快速上手](https://huggingface.co/blog/daggr#getting-started)
- [分享你的工作流](https://huggingface.co/blog/daggr#sharing-your-workflows)
- [使用不同类型节点的端到端示例](https://huggingface.co/blog/daggr#end-to-end-example-with-different-nodes)
- [下一步](https://huggingface.co/blog/daggr#next-steps)

## 背景

如果你构建过需要组合多个模型或多个处理步骤的 AI 应用，你一定懂那种痛：串联 API 调用、调试流水线、然后迷失在中间结果里。当一个 10 步工作流在第 5 步出问题时，你往往得把整个流程重跑一遍，只为看看发生了什么。

大多数开发者要么写脆弱的、难以调试的脚本，要么转向为生产流水线设计的重量级编排平台——而不是快速实验。

我们做 Daggr，是为了解决我们在构建 AI 演示和工作流时反复遇到的问题：

**可视化你的代码流**：与拖拽连线式的节点 GUI 编辑器不同，Daggr 采用代码优先（code-first）的方式。你用 Python 定义工作流，可视化画布自动生成。这样两全其美：代码可以进版本控制，中间输出又能可视化查看。

**检查并重跑任意步骤**：可视化画布不只是摆设。你可以查看任意节点的输出、修改输入、单独重跑某个步骤，而不必执行整条流水线。当你在调试一个 10 步工作流、只有第 7 步在捣乱时，这非常有用。你甚至可以提供"备份节点"——用一个模型或 Space 替换另一个——来构建有弹性的工作流。

**一等公民的 Gradio 集成**：Daggr 出自 Gradio 团队之手，与 Gradio Spaces 无缝协作。指向任意公开（或私有）Space，就能把它当作工作流中的一个节点。不需要适配器、不需要包装——引用 Space 名字和 API 端点即可。

**状态持久化**：Daggr 会自动保存你的工作流状态、输入值、缓存结果、画布位置——随时可以从上次中断的地方继续。用"sheets（工作表）"还能在同一个应用里维护多个工作区。

## 快速上手

用 pip 或 uv 安装 daggr，只需要 Python 3.10 或更高版本：

```
pip install daggr
uv pip install daggr
```

下面是一个简单示例：生成一张图并去掉背景。可以看看 [这个 Space 的 API 参考](https://huggingface.co/spaces/hf-applications/Z-Image-Turbo)（在 Space 页面底部），了解它接受哪些输入、产出哪些输出。在这个例子里，Space 同时返回原图和编辑后的图，所以我们只返回编辑后的图。

```
import random
import gradio as gr
from daggr import GradioNode, Graph

# Generate an image using a Gradio Space
image_gen = GradioNode(
    "hf-applications/Z-Image-Turbo",
    api_name="/generate_image",
    inputs={
        "prompt": gr.Textbox(
            label="Prompt",
            value="A cheetah sprints across the grassy savanna.",
            lines=3,
        ),
        "height": 1024,
        "width": 1024,
        "seed": random.random,
    },
    outputs={
        "image": gr.Image(label="Generated Image"),
    },
)

# Remove background using another Gradio Space
bg_remover = GradioNode(
    "hf-applications/background-removal",
    api_name="/image",
    inputs={
        "image": image_gen.image,  # Connect to previous node's output
    },
    outputs={
        "original_image": None,  # Hide this output
        "final_image": gr.Image(label="Final Image"),
    },
)

graph = Graph(
    name="Transparent Background Generator", 
    nodes=[image_gen, bg_remover]
)
graph.launch()
```

就这么简单。运行这个脚本，就会在 7860 端口自动启动一个可视化画布，同时给出可分享的在线链接：两个节点相连，每一步的输入可修改、输出可查看。

[![App](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/daggr-blog/app1.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/daggr-blog/app1.png)

### 节点类型

Daggr 支持三种节点：

**GradioNode** 调用 Gradio Space 的 API 端点或本地运行的 Gradio 应用。传入 `run_locally=True` 时，Daggr 会自动克隆该 Space、创建隔离的虚拟环境并启动应用。如果本地执行失败，会平滑降级到远程 API。

```
node = GradioNode(
    "username/space-name",
    api_name="/predict",
    inputs={"text": gr.Textbox(label="Input")},
    outputs={"result": gr.Textbox(label="Output")},
)

# clone a Space locally and serve
node = GradioNode(
    "hf-applications/background-removal",
    api_name="/image",
    run_locally=True,
    inputs={"image": gr.Image(label="Input")},
    outputs={"final_image": gr.Image(label="Output")},
```

**FnNode** —— 运行一个自定义 Python 函数：

```
def process(text: str) -> str:
    return text.upper()

node = FnNode(
    fn=process,
    inputs={"text": gr.Textbox(label="Input")},
    outputs={"result": gr.Textbox(label="Output")},
)
```

**InferenceNode** —— 通过 Hugging Face Inference Providers 调用模型：

```
node = InferenceNode(
    model="moonshotai/Kimi-K2.5:novita",
    inputs={"prompt": gr.Textbox(label="Prompt")},
    outputs={"response": gr.Textbox(label="Response")},
)
```

### 分享你的工作流

用 Gradio 的隧道功能生成公开 URL：

```
graph.launch(share=True)
```

想要永久托管，就用 Gradio SDK 部署到 Hugging Face Spaces——只需把 `daggr` 加进你的 `requirements.txt`。

## 使用不同类型节点的端到端示例

接下来我们要开发一个应用：输入一张图，生成一个 3D 资产。这个演示可以在 daggr 0.4.3 上运行。步骤如下：

- **拿到图像，去除背景：** 为此我们克隆 [BiRefNet Space](https://huggingface.co/spaces/merve/background-removal) 并在本地运行。
- **为提升效率缩小图像尺寸：** 我们用 FnNode 写一个简单的函数来做这件事。
- **生成 3D 资产风格的图像以获得更好效果：** 我们使用 InferenceNode，通过 Inference Providers 调用 [Flux.2-klein-4B 模型](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B)。
- **把输出图像交给 3D 生成器：** 我们将输出图像发送到托管在 Spaces 上的 Trellis.2 Space。

> 本地运行的 Spaces 可能会在应用文件里把模型加载到 CUDA（`to.("cuda")`）或使用 ZeroGPU。如果想禁用这一行为、在 CPU 上运行模型（对没有 NVIDIA GPU 的设备很有用），可以复制（duplicate）你想用的 Space 再克隆。

最终生成的图如下。

[![App](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/daggr-blog/app2.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/daggr-blog/app2.png)

先写第一步——背景移除器。我们克隆并在本地运行[这个 Space](https://huggingface.co/spaces/merve/background-removal)。它运行在 CPU 上，耗时约 13 秒。如果你有 NVIDIA GPU，可以换成[这个应用](https://huggingface.co/spaces/hf-applications/background-removal)。

```
from daggr import FnNode, GradioNode, InferenceNode, Graph

background_remover = GradioNode(
   "merve/background-removal",
   api_name="/image",
   run_locally=True, 
   inputs={
       "image": gr.Image(),
   },
   outputs={
       "original_image": None,
       "final_image": gr.Image(
           label="Final Image"
       ),
   },
)
```

第二步，我们需要写一个辅助函数来缩小图像，并把它传给 `FnNode`。

```
from PIL import Image
from daggr.state import get_daggr_files_dir


def downscale_image_to_file(image: Any, scale: float = 0.25) -> str | None:
   pil_img = Image.open(image)
   scale_f = max(0.05, min(1.0, float(scale)))
   w, h = pil_img.size
   new_w = max(1, int(w * scale_f))
   new_h = max(1, int(h * scale_f))
   resized = pil_img.resize((new_w, new_h), resample=Image.LANCZOS)
   out_path = get_daggr_files_dir() / f"{uuid.uuid4()}.png"

   resized.save(out_path)
   return str(out_path)
```

现在可以把这个函数传入以初始化 `FnNode`。

```
downscaler = FnNode(
   downscale_image_to_file,
   name="Downscale image for Inference",
   inputs={
       "image": background_remover.final_image,
       "scale": gr.Slider(
           label="Downscale factor",
           minimum=0.25,
           maximum=0.75,
           step=0.05,
           value=0.25,
       ),
   },
   outputs={
       "image": gr.Image(label="Downscaled Image", type="filepath"),
   },
)
```

接下来用 Flux 模型写 `InferenceNode`。

```
flux_enhancer = InferenceNode(
   model="black-forest-labs/FLUX.2-klein-4B:fal-ai",
   inputs={
       "image": downscaler.image,
       "prompt": gr.Textbox(
           label="prompt",
           value=("Transform this into a clean 3D asset render"),
           lines=3,
       ),
   },
   outputs={
       "image": gr.Image(label="3D-Ready Enhanced Image"),
   },
)
```

> 将带 InferenceNode 的应用部署到 Hugging Face Spaces 时，请使用只勾选 "Make calls to Inference Providers" 权限的细粒度 Hugging Face 访问令牌。

最后一个节点是查询 Hugging Face 上的 Trellis.2 Space 来做 3D 生成。

```
trellis_3d = GradioNode(
   "microsoft/TRELLIS.2",
   api_name="/image_to_3d",
   inputs={
       "image": flux_enhancer.image,
       "ss_guidance_strength": 7.5,   
       "ss_sampling_steps": 12,     
   },
   outputs={
       "glb": gr.HTML(label="3D Asset (GLB preview)"),
   },
)
```

把它们串联起来并启动应用，就这么简单。

```
graph = Graph(
   name="Image to 3D Asset Pipeline",
   nodes=[background_remover, downscaler, flux_enhancer, trellis_3d],
)

if __name__ == "__main__":
   graph.launch()
```

完整示例运行在[这个 Space](https://huggingface.co/spaces/merve/daggr-image-to-3d)里；想在本地运行，只需拿到 app.py、安装依赖并登录 Hugging Face Hub。

## 下一步

Daggr 目前处于 beta 阶段，刻意保持轻量。API 在不同版本间可能变化；虽然我们在本地持久化工作流状态，但更新过程中仍有数据丢失的可能。如果你有功能需求或发现了 bug，请在[这里](https://github.com/gradio-app/daggr/issues)提 issue。我们期待你的反馈！带上 Gradio 在社交媒体上分享你的 daggr 工作流，有机会被精选展示。所有精选作品见[这里](https://huggingface.co/collections/ysharma/daggr-hf-spaces)。

## 文中提到的模型 1

## 文中提到的 Spaces 4

## 文中提到的 Collections 1

我们博客的更多文章

gradio

workflows

automatic1111

## Rebuilding AUTOMATIC1111 with Gradio Workflow

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1624431552569-noauth.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1621947938344-noauth.png)

71

2026 年 9 月 10 日

gradio

workflows

tutorial

## Wire It, Run It, Deploy It: AI Workflows in Gradio

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1624431552569-noauth.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1621947938344-noauth.png)

49

2026 年 8 月 25 日

### 社区

ArseniyPerchik

1 月 31 日

·

1 月 31 日编辑

条件节点有考虑吗？我是说那种根据当前节点的输出来决定下一个执行哪个节点的节点。

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1621947938344-noauth.png)](https://huggingface.co/abidlabs)

·

abidlabs

本文作者

2 月 5 日

这个点很好。我们想支持它，但正在斟酌合适的 API，因为我们同时也希望支持程序化检查 / API 调用，这需要一定程度的确定性。如果你有任何建议，欢迎在这里提 issue：[https://github.com/gradio-app/daggr](https://github.com/gradio-app/daggr)

hxgdzyuyi

2 月 5 日

为什么不用 jupyternotebook

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1621947938344-noauth.png)](https://huggingface.co/abidlabs)

·

abidlabs

本文作者

2 月 5 日

你在 Jupyter notebook 里运行 Daggr 遇到什么问题了吗？理论上应该是支持的，如果遇到问题，欢迎在这里提 issue：[https://github.com/gradio-app/daggr](https://github.com/gradio-app/daggr)

MatthewFrank

2 月 9 日

对链式应用的可视化检查能力太棒了！能在保持可见性的同时以编程方式看到流程，对调试和理解系统行为非常重要。说到可视化系统流程，我一直在用 InfraSketch（[https://www.infrasketch.net/](https://www.infrasketch.net/)）来记录我们的应用架构——它能从通俗英语描述生成图表，还能通过对话进一步细化。作为 Daggr 这类工具的补充，它向整个团队传达系统设计非常得力。

Funnelsflex

2 月 21 日

·

3 月 3 日编辑

这是实现流水线透明度的扎实思路。在做 Funnelsflex 部署时，我们经常看到僵化的 UI 漏斗构建器和原始 Python 脚本灵活性之间的摩擦点。Daggr 似乎弥合了这个鸿沟：逻辑留在代码里该在的地方，同时提供标准 Gradio 链式应用通常缺失的可视化状态持久化。

能单独重跑某个节点而不触发整个推理栈，对调试复杂的弹性工作流来说是个巨大的胜利。我很想看看它在高并发环境下如何处理状态管理，但就快速原型和"可检查"的 AI 应用而言，这是一个非常干净的实现。
[https://funnelsflex.io/](https://funnelsflex.io/)

将文件拖入文本输入框、粘贴，或

点击此处

，即可上传图像、音频和视频。

点击或粘贴此处上传图片

· [注册](https://huggingface.co/join?next=%2Fblog%2Fdaggr)或[登录](https://huggingface.co/login?next=%2Fblog%2Fdaggr)发表评论

点赞

107

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/608aabf24955d2bfc3cd99c6/-YxmtpzEmf3NKOTktODRP.jpeg)](https://huggingface.co/ariG23498)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63e24395419922d5a6d7a6cc/bOFr0La0VdpIZ06-ZWJa4.jpeg)](https://huggingface.co/emredeveloper)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1621947938344-noauth.png)](https://huggingface.co/abidlabs)
- [![](https://huggingface.co/avatars/85bb740aa905416c52d3e70fd433bd24.svg)](https://huggingface.co/Gabriel)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)](https://huggingface.co/pcuenq)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/648a374f00f7a3374ee64b99/YPwSOrronoozwHbJchPn3.jpeg)](https://huggingface.co/cfahlgren1)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/CWjxjU3HSVmkWBfugVL10.png)](https://huggingface.co/hvbhanot)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1605114051380-noauth.jpeg)](https://huggingface.co/jeffboudier)
- [![](https://huggingface.co/avatars/3a2f12b6111f135e24b4844fdb1b0748.svg)](https://huggingface.co/maxcorbeau)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6415a939e38b2bdc189f1da7/alb9EC84UTeGpVqqGD6VQ.png)](https://huggingface.co/atasoglu)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/J8onuxUInfk_05Jaou5Lq.png)](https://huggingface.co/johnmoonwalker)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1659922312540-610a70f35a40a8bfebfbf09b.jpeg)](https://huggingface.co/mrdbourke)

## 文中提到的模型 1

## 文中提到的 Spaces 4

## 文中提到的 Collections 1
