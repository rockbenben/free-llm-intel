---
vendor: huggingface
title: 在 Hugging Face Spaces 上用 Gradio 免费运行 ComfyUI 工作流
original_title: Run ComfyUI workflows for free with Gradio on Hugging Face Spaces
url: https://huggingface.co/blog/run-comfyui-workflows-on-spaces
date: 2025-01-15
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: 64dcc657015f
---

# 在 Hugging Face Spaces 上用 Gradio 免费运行 ComfyUI 工作流

Apolinário（multimodal AI art，账号 multimodalart）

Charles Bensimon（账号 cbensimon）

本文亦有[简体中文](https://huggingface.co/blog/zh/run-comfyui-workflows-on-spaces)版本。

目录：

- [引言](https://huggingface.co/blog/run-comfyui-workflows-on-spaces#intro) [前置条件](https://huggingface.co/blog/run-comfyui-workflows-on-spaces#prerequisites)
- [把 ComfyUI 工作流导出为纯 Python 运行](https://huggingface.co/blog/run-comfyui-workflows-on-spaces#1-exporting-your-comfyui-workflow-to-run-on-pure-python)
- [为导出的 Python 创建一个 Gradio 应用](https://huggingface.co/blog/run-comfyui-workflows-on-spaces#2-create-a-gradio-app-for-the-exported-python)
- [准备在 Hugging Face Spaces 上运行](https://huggingface.co/blog/run-comfyui-workflows-on-spaces#3-preparing-it-to-run-hugging-face-spaces)
- [导出到 Spaces 并在 ZeroGPU 上运行](https://huggingface.co/blog/run-comfyui-workflows-on-spaces#4-exporting-to-spaces-and-running-on-zerogpu)
- [结语](https://huggingface.co/blog/run-comfyui-workflows-on-spaces#5-conclusion)

## 引言

在这篇教程里，我会给出一份手把手指南：如何把一个复杂的 ComfyUI 工作流转成一个简单的 Gradio 应用，并把这个应用部署到 Hugging Face Spaces 的 ZeroGPU 无服务器架构上——这样就能以无服务器方式免费部署和运行它。本教程以 [Nathan Shipley 的 Flux[dev] Redux + Flux[dev] Depth ComfyUI 工作流](https://gist.github.com/nathanshipley/7a9ac1901adde76feebe58d558026f68)为例，但你可以换成任何自己想用的工作流。

[![comfy-to-gradio](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/comfyu-to-gradio/main_ui_conversion.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/comfyu-to-gradio/main_ui_conversion.png)

本教程内容的 tl;dr 摘要：

- 用 [`ComfyUI-to-Python-Extension`](https://github.com/pydn/ComfyUI-to-Python-Extension) 导出你的 ComfyUI 工作流；
- 为导出的 Python 创建一个 Gradio 应用；
- 用 ZeroGPU 把它部署到 Hugging Face Spaces；
- 很快：这整个流程都会自动化；

### 前置条件

- 懂得如何运行 ComfyUI：本教程要求你能拿到一个 ComfyUI 工作流并在自己机器上跑起来，包括安装缺失的节点、找到缺失的模型（我们确实计划很快把这一步自动化掉）；
- 把你想导出的工作流先跑通（如果你想不带具体工作流地学，可以随便把 [Nathan Shipley 的 Flux[dev] Redux + Flux[dev] Depth ComfyUI 工作流](https://gist.github.com/nathanshipley/7a9ac1901adde76feebe58d558026f68)跑起来）；
- 一点编程基础：不过我鼓励初学者也试着跟一遍，因为它是对 Python、Gradio 和 Spaces 一个很好的入门，不需要太多前置编程知识。

（如果你在找一个端到端的"工作流到应用"方案，不需要自己装 Comfy、也不需要懂写代码，请留意我在 [Hugging Face](https://huggingface.co/multimodalart/) 或 [Twitter/X](https://twitter.com/multimodalart) 上的主页——我们计划在 2025 年初做出这个功能！）

## 1. 把 ComfyUI 工作流导出为纯 Python 运行

ComfyUI 很棒，顾名思义，它带一个 UI。但 Comfy 远不止一个 UI，它还有一个基于 Python 的后端。由于本教程不打算用 Comfy 的节点式 UI，我们需要把代码导出成纯 Python 来运行。

幸好，[Peyton DeNiro](https://github.com/pydn) 做了一个非常给力的 [ComfyUI-to-Python-Extension](https://github.com/pydn/ComfyUI-to-Python-Extension)，可以把任何 Comfy 工作流导出成一个 Python 脚本，让你不用启动 UI 就能跑工作流。

[![comfy-to-gradio](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/comfyu-to-gradio/export_as_python_steps.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/comfyu-to-gradio/export_as_python_steps.png)

安装这个扩展最简单的办法是：(1) 在 ComfyUI Manager 扩展的 Custom Nodes Manager 菜单里搜索 `ComfyUI to Python Extension`，(2) 安装它。然后为了让选项出现，你需要 (3) 打开 UI 右下角的设置，(4) 禁用新菜单，(5) 点击 `Save as Script`。这样你就得到一个 Python 脚本了。

## 2. 为导出的 Python 创建一个 Gradio 应用

现在我们拿到了 Python 脚本，是时候创建一个 Gradio 应用来驱动它了。Gradio 是一个 Python 原生的 Web UI 构建器，能让我们创建简洁流畅的应用。如果你的环境里还没有它，可以用 `pip install gradio` 安装。

接下来，我们要把 Python 脚本稍作 rearrange，给它做一个 UI。

> 提示：ChatGPT、Claude、Qwen、Gemini、LLama 3 这些大模型都知道怎么写 Gradio 应用。把导出的 Python 脚本贴给它们、让它们生成一个 Gradio 应用，基本能用，但你多半还得用本教程里学到的知识去修正一些地方。为了教学目的，这里我们自己动手创建应用。

打开导出的 Python 脚本，加一行 Gradio 的导入

```
import os
import random
import sys
from typing import Sequence, Mapping, Any, Union
import torch
+ import gradio as gr
```

现在要思考 UI——复杂的 ComfyUI 工作流里，我们想在 UI 上暴露哪些参数？对于 `Flux[dev] Redux + Flux[dev] Depth ComfyUI 工作流`，我想暴露：提示词（prompt）、结构图、风格图、深度强度（对应结构）和风格强度。

*演示哪些节点会暴露给最终用户的视频*

为此，一个最简的 Gradio 应用是：

```
if __name__ == "__main__":
    # Comment out the main() call in the exported Python code
    
    # Start your Gradio app
    with gr.Blocks() as app:
        # Add a title
        gr.Markdown("# FLUX Style Shaping")

        with gr.Row():
            with gr.Column():
                # Add an input
                prompt_input = gr.Textbox(label="Prompt", placeholder="Enter your prompt here...")
                # Add a `Row` to include the groups side by side 
                with gr.Row():
                    # First group includes structure image and depth strength
                    with gr.Group():
                        structure_image = gr.Image(label="Structure Image", type="filepath")
                        depth_strength = gr.Slider(minimum=0, maximum=50, value=15, label="Depth Strength")
                    # Second group includes style image and style strength
                    with gr.Group():
                        style_image = gr.Image(label="Style Image", type="filepath")
                        style_strength = gr.Slider(minimum=0, maximum=1, value=0.5, label="Style Strength")
                
                # The generate button
                generate_btn = gr.Button("Generate")
            
            with gr.Column():
                # The output image
                output_image = gr.Image(label="Generated Image")

            # When clicking the button, it will trigger the `generate_image` function, with the respective inputs
            # and the output an image
            generate_btn.click(
                fn=generate_image,
                inputs=[prompt_input, structure_image, style_image, depth_strength, style_strength],
                outputs=[output_image]
            )
        app.launch(share=True)
```

应用渲染出来是这个样子

[![Comfy-UI-to-Gradio](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/comfyu-to-gradio/gradio_ui_rendered.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/comfyu-to-gradio/gradio_ui_rendered.png)

但直接运行还不行，因为我们还需要同改造导出 Python 脚本里的 `def main()` 函数，把 `generate_image` 这个函数搭起来：

```
- def main():
+ def generate_image(prompt, structure_image, style_image, depth_strength, style_strength)
```

然后在函数内部，找到我们想要的那些节点里硬编码的值，替换成我们想控制的变量，比如：

```
loadimage_429 = loadimage.load_image(
-    image="7038548d-d204-4810-bb74-d1dea277200a.png"
+    image=structure_image
)
# ...
loadimage_440 = loadimage.load_image(
-    image="2013_CKS_01180_0005_000(the_court_of_pir_budaq_shiraz_iran_circa_1455-60074106).jpg"
+    image=style_image
)
# ...
fluxguidance_430 = fluxguidance.append(
-   guidance=15,
+   guidance=depth_strength,
    conditioning=get_value_at_index(cliptextencode_174, 0)
)
# ...
stylemodelapplyadvanced_442 = stylemodelapplyadvanced.apply_stylemodel(
-   strength=0.5,
+   strength=style_strength,
    conditioning=get_value_at_index(instructpixtopixconditioning_431, 0),
    style_model=get_value_at_index(stylemodelloader_441, 0),
    clip_vision_output=get_value_at_index(clipvisionencode_439, 0),
)
# ...
cliptextencode_174 = cliptextencode.encode(
-   text="a girl looking at a house on fire",
+   text=prompt,   
    clip=get_value_at_index(cr_clip_input_switch_319, 0),
)
```

对于输出，我们要找到 save image 输出节点，并导出它的路径，比如：

```
saveimage_327 = saveimage.save_images(
    filename_prefix=get_value_at_index(cr_text_456, 0),
    images=get_value_at_index(vaedecode_321, 0),
)
+ saved_path = f"output/{saveimage_327['ui']['images'][0]['filename']}"
+ return saved_path
```

这些改动的视频讲解在这里：

现在，我们应该可以运行代码了！把 Python 文件保存为 `app.py`，放到 ComfyUI 文件夹的根目录，然后运行

```
python app.py
```

就这样，你应该就能在 [http://0.0.0.0:7860](http://0.0.0.0:7860) 上运行你的 Gradio 应用了

```
* Running on local URL:  http://127.0.0.1:7860
* Running on public URL: https://366fdd17b8a9072899.gradio.live
```

要调试这个过程，看[这里](https://gist.github.com/apolinario/47a8503c007c5ae8494324bed9e158ce/revisions?diff=unified&w=47a8503c007c5ae8494324bed9e158ce#diff-faf377dc15b3371a15d2c4a03b4d012825533bd2fb2297852cb2244d07fe36eeL1)：`ComfyUI-to-Python-Extension` 导出的原始 Python 文件与 Gradio 应用之间的 diff。你可以在那个 URL 上下载两个文件，与自己的工作流的改动对照检查。

搞定，恭喜你！你把 ComfyUI 工作流转成了 Gradio 应用。你可以在本地运行它，甚至可以把 URL 发给客户或朋友，但是，一旦你关电脑，或者 72 小时过去，这个临时 Gradio 链接就失效了。想要一个持久的应用托管结构——包括让大家以无服务器方式免费运行它——可以用 Hugging Face Spaces。

## 3. 准备在 Hugging Face Spaces 上运行

Gradio 演示现在能跑了，我们可能忍不住想把所有东西直接传到 Hugging Face Spaces。但那样就得把几十 GB 的模型上传到 Hugging Face，不仅慢，而且完全没必要，因为这些模型本来就都在 Hugging Face 上！

正确的做法是：先 `pip install huggingface_hub`（如果还没装），然后在 `app.py` 文件顶部做以下操作：

```
from huggingface_hub import hf_hub_download

hf_hub_download(repo_id="black-forest-labs/FLUX.1-Redux-dev", filename="flux1-redux-dev.safetensors", local_dir="models/style_models")
hf_hub_download(repo_id="black-forest-labs/FLUX.1-Depth-dev", filename="flux1-depth-dev.safetensors", local_dir="models/diffusion_models")
hf_hub_download(repo_id="Comfy-Org/sigclip_vision_384", filename="sigclip_vision_patch14_384.safetensors", local_dir="models/clip_vision")
hf_hub_download(repo_id="Kijai/DepthAnythingV2-safetensors", filename="depth_anything_v2_vitl_fp32.safetensors", local_dir="models/depthanything")
hf_hub_download(repo_id="black-forest-labs/FLUX.1-dev", filename="ae.safetensors", local_dir="models/vae/FLUX1")
hf_hub_download(repo_id="comfyanonymous/flux_text_encoders", filename="clip_l.safetensors", local_dir="models/text_encoders")
hf_hub_download(repo_id="comfyanonymous/flux_text_encoders", filename="t5xxl_fp16.safetensors", local_dir="models/text_encoders/t5")
```

这会把 ComfyUI 里所有本地模型映射到它们在 Hugging Face 上的版本。遗憾的是，目前这个过程没法自动化，你得自己在工作流涉及的模型中找到 Hugging Face 上的对应版本，并映射到相同的 ComfyUI 文件夹。

如果你用的模型不在 Hugging Face 上，就得想办法用 Python 代码把它们下载到正确的文件夹。这段下载只会在 Space 启动时执行一次。

最后，我们对 `app.py` 再做一处修改：给函数加上 ZeroGPU 的装饰器，这样就能免费做推理了！

```
import gradio as gr
from huggingface_hub import hf_hub_download
+ import spaces
# ...
+ @spaces.GPU(duration=60) #modify the duration for the average it takes for your worflow to run, in seconds
def generate_image(prompt, structure_image, style_image, depth_strength, style_strength):
```

在这里查看加入 Spaces 相关改动后与上一版 Gradio 演示的 [diff](https://gist.github.com/apolinario/47a8503c007c5ae8494324bed9e158ce/revisions?diff=unified&w=47a8503c007c5ae8494324bed9e158ce#diff-faf377dc15b3371a15d2c4a03b4d012825533bd2fb2297852cb2244d07fe36eeL4)。

## 4. 导出到 Spaces 并在 ZeroGPU 上运行

代码准备好了——你可以在本地运行，也可以在任意你喜欢的云服务上运行，包括独占的 Hugging Face Spaces GPU。但要在无服务器的 ZeroGPU 上运行，请接着往下看。

### 修复 requirements

首先，需要修改 `requirements.txt`，把 `custom_nodes` 文件夹里的依赖也包含进来。因为 Hugging Face Spaces 只认一个根目录的 `requirements.txt` 文件，务必把这个工作流所用节点的依赖加进根目录的 `requirements.txt`。

见下面的演示，对每个 `custom_nodes` 都要重复同样的过程：

现在准备好了！

[![create-space](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/comfyu-to-gradio/create_space.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/comfyu-to-gradio/create_space.png)

- 打开 [https://huggingface.co](https://huggingface.co)，创建一个新 Space。
- 硬件选 ZeroGPU（如果你是 Hugging Face PRO 订阅用户）；不是 PRO 用户就选 CPU basic（非 PRO 用户结尾还要多做一步）。2.1（如果你更想要付费的独占 GPU，别选 ZeroGPU，改选 L4、L40S、A100，那是付费选项）
- 点击 Files 标签页，Add `File > Upload Files`。把 ComfyUI 文件夹里的所有文件拖上来，**除了** `models` 文件夹（如果试图上传 `models` 文件夹，上传会失败），这正是我们需要第 3 步的原因。
- 点击页面底部的 `Commit changes to main` 按钮，等待全部上传完成
- 如果你用的是受限模型（gated models），比如 FLUX，需要在设置里加一个 Hugging Face token。先在[这里](https://huggingface.co/settings/tokens)创建一个对你需要的所有受限模型有 `read` 权限的 token，然后进入 Space 的 `Settings` 页面，创建一个名为 `HF_TOKEN` 的 secret，值就是你刚创建的 token。

[![variables-and-secrets](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/comfyu-to-gradio/variables_and_secrets.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/comfyu-to-gradio/variables_and_secrets.png)

### 把模型移出被装饰的函数（仅 ZeroGPU）

你的演示此刻应该已经能跑了，但在当前结构下，每次运行都会把模型完整地从磁盘加载到 GPU。为了吃到无服务器 ZeroGPU 的效率红利，我们需要把所有模型声明从被装饰的函数里挪到 Python 的全局上下文。来改一下 `app.py`。

```
@@ -4,6 +4,7 @@
from typing import Sequence, Mapping, Any, Union
import torch
import gradio as gr
from huggingface_hub import hf_hub_download
+from comfy import model_management
import spaces

hf_hub_download(repo_id="black-forest-labs/FLUX.1-Redux-dev", filename="flux1-redux-dev.safetensors", local_dir="models/style_models")
@@ -109,6 +110,62 @@

from nodes import NODE_CLASS_MAPPINGS

+intconstant = NODE_CLASS_MAPPINGS["INTConstant"]()
+dualcliploader = NODE_CLASS_MAPPINGS["DualCLIPLoader"]()
+dualcliploader_357 = dualcliploader.load_clip(
+    clip_name1="t5/t5xxl_fp16.safetensors",
+    clip_name2="clip_l.safetensors",
+    type="flux",
+)
+cr_clip_input_switch = NODE_CLASS_MAPPINGS["CR Clip Input Switch"]()
+cliptextencode = NODE_CLASS_MAPPINGS["CLIPTextEncode"]()
+loadimage = NODE_CLASS_MAPPINGS["LoadImage"]()
+imageresize = NODE_CLASS_MAPPINGS["ImageResize+"]()
+getimagesizeandcount = NODE_CLASS_MAPPINGS["GetImageSizeAndCount"]()
+vaeloader = NODE_CLASS_MAPPINGS["VAELoader"]()
+vaeloader_359 = vaeloader.load_vae(vae_name="FLUX1/ae.safetensors")
+vaeencode = NODE_CLASS_MAPPINGS["VAEEncode"]()
+unetloader = NODE_CLASS_MAPPINGS["UNETLoader"]()
+unetloader_358 = unetloader.load_unet(
+    unet_name="flux1-depth-dev.safetensors", weight_dtype="default"
+)
+ksamplerselect = NODE_CLASS_MAPPINGS["KSamplerSelect"]()
+randomnoise = NODE_CLASS_MAPPINGS["RandomNoise"]()
+fluxguidance = NODE_CLASS_MAPPINGS["FluxGuidance"]()
+depthanything_v2 = NODE_CLASS_MAPPINGS["DepthAnything_V2"]()
+downloadandloaddepthanythingv2model = NODE_CLASS_MAPPINGS[
+    "DownloadAndLoadDepthAnythingV2Model"
+]()
+downloadandloaddepthanythingv2model_437 = (
+    downloadandloaddepthanythingv2model.loadmodel(
+        model="depth_anything_v2_vitl_fp32.safetensors"
+    )
+)
+instructpixtopixconditioning = NODE_CLASS_MAPPINGS[
+    "InstructPixToPixConditioning"
+]()
+text_multiline_454 = text_multiline.text_multiline(text="FLUX_Redux")
+clipvisionloader = NODE_CLASS_MAPPINGS["CLIPVisionLoader"]()
+clipvisionloader_438 = clipvisionloader.load_clip(
+    clip_name="sigclip_vision_patch14_384.safetensors"
+)
+clipvisionencode = NODE_CLASS_MAPPINGS["CLIPVisionEncode"]()
+stylemodelloader = NODE_CLASS_MAPPINGS["StyleModelLoader"]()
+stylemodelloader_441 = stylemodelloader.load_style_model(
+    style_model_name="flux1-redux-dev.safetensors"
+)
+text_multiline = NODE_CLASS_MAPPINGS["Text Multiline"]()
+emptylatentimage = NODE_CLASS_MAPPINGS["EmptyLatentImage"]()
+cr_conditioning_input_switch = NODE_CLASS_MAPPINGS[
+    "CR Conditioning Input Switch"
+]()
+cr_model_input_switch = NODE_CLASS_MAPPINGS["CR Model Input Switch"]()
+stylemodelapplyadvanced = NODE_CLASS_MAPPINGS["StyleModelApplyAdvanced"]()
+basicguider = NODE_CLASS_MAPPINGS["BasicGuider"]()
+basicscheduler = NODE_CLASS_MAPPINGS["BasicScheduler"]()
+samplercustomadvanced = NODE_CLASS_MAPPINGS["SamplerCustomAdvanced"]()
+vaedecode = NODE_CLASS_MAPPINGS["VAEDecode"]()
+saveimage = NODE_CLASS_MAPPINGS["SaveImage"]()
+imagecrop = NODE_CLASS_MAPPINGS["ImageCrop+"]()

@@ -117,75 +174,6 @@
def generate_image(prompt, structure_image, style_image, depth_strength, style_strength):
    import_custom_nodes()
    with torch.inference_mode():
-        intconstant = NODE_CLASS_MAPPINGS["INTConstant"]()
         intconstant_83 = intconstant.get_value(value=1024)

         intconstant_84 = intconstant.get_value(value=1024)

-        dualcliploader = NODE_CLASS_MAPPINGS["DualCLIPLoader"]()
-        dualcliploader_357 = dualcliploader.load_clip(
-            clip_name1="t5/t5xxl_fp16.safetensors",
-            clip_name2="clip_l.safetensors",
-            type="flux",
-        )
-
-        cr_clip_input_switch = NODE_CLASS_MAPPINGS["CR Clip Input Switch"]()
         cr_clip_input_switch_319 = cr_clip_input_switch.switch(
             Input=1,
             clip1=get_value_at_index(dualcliploader_357, 0),
             clip2=get_value_at_index(dualcliploader_357, 0),
         )

-        cliptextencode = NODE_CLASS_MAPPINGS["CLIPTextEncode"]()
         cliptextencode_174 = cliptextencode.encode(
             text=prompt,
             clip=get_value_at_index(cr_clip_input_switch_319, 0),
         )

         cliptextencode_175 = cliptextencode.encode(
             text="purple", clip=get_value_at_index(cr_clip_input_switch_319, 0)
         )

-        loadimage = NODE_CLASS_MAPPINGS["LoadImage"]()
         loadimage_429 = loadimage.load_image(image=structure_image)

-        imageresize = NODE_CLASS_MAPPINGS["ImageResize+"]()
         imageresize_72 = imageresize.execute(
             width=get_value_at_index(intconstant_83, 0),
             height=get_value_at_index(intconstant_84, 0),
             interpolation="bicubic",
             method="keep proportion",
             condition="always",
             multiple_of=16,
             image=get_value_at_index(loadimage_429, 0),
         )

-        getimagesizeandcount = NODE_CLASS_MAPPINGS["GetImageSizeAndCount"]()
         getimagesizeandcount_360 = getimagesizeandcount.getsize(
             image=get_value_at_index(imageresize_72, 0)
         )

-        vaeloader = NODE_CLASS_MAPPINGS["VAELoader"]()
-        vaeloader_359 = vaeloader.load_vae(vae_name="FLUX1/ae.safetensors")

-        vaeencode = NODE_CLASS_MAPPINGS["VAEEncode"]()
         vaeencode_197 = vaeencode.encode(
             pixels=get_value_at_index(getimagesizeandcount_360, 0),
             vae=get_value_at_index(vaeloader_359, 0),
         )

-        unetloader = NODE_CLASS_MAPPINGS["UNETLoader"]()
-        unetloader_358 = unetloader.load_unet(
-            unet_name="flux1-depth-dev.safetensors", weight_dtype="default"
-        )

-        ksamplerselect = NODE_CLASS_MAPPINGS["KSamplerSelect"]()
         ksamplerselect_363 = ksamplerselect.get_sampler(sampler_name="euler")

-        randomnoise = NODE_CLASS_MAPPINGS["RandomNoise"]()
         randomnoise_365 = randomnoise.get_noise(noise_seed=random.randint(1, 2**64))

-        fluxguidance = NODE_CLASS_MAPPINGS["FluxGuidance"]()
         fluxguidance_430 = fluxguidance.append(
             guidance=15, conditioning=get_value_at_index(cliptextencode_174, 0)
         )

-        downloadandloaddepthanythingv2model = NODE_CLASS_MAPPINGS[
-            "DownloadAndLoadDepthAnythingV2Model"
-        ]()
-        downloadandloaddepthanythingv2model_437 = (
-            downloadandloaddepthanythingv2model.loadmodel(
-                model="depth_anything_v2_vitl_fp32.safetensors"
-            )
-        )

-        depthanything_v2 = NODE_CLASS_MAPPINGS["DepthAnything_V2"]()
         depthanything_v2_436 = depthanything_v2.process(
             da_model=get_value_at_index(downloadandloaddepthanythingv2model_437, 0),
             images=get_value_at_index(getimagesizeandcount_360, 0),
         )

-        instructpixtopixconditioning = NODE_CLASS_MAPPINGS[
-            "InstructPixToPixConditioning"
-        ]()
         instructpixtopixconditioning_431 = instructpixtopixconditioning.encode(
             positive=get_value_at_index(fluxguidance_430, 0),
             negative=get_value_at_index(cliptextencode_175, 0),
             vae=get_value_at_index(vaeloader_359, 0),
             pixels=get_value_at_index(depthanything_v2_436, 0),
         )

-        clipvisionloader = NODE_CLASS_MAPPINGS["CLIPVisionLoader"]()
-        clipvisionloader_438 = clipvisionloader.load_clip(
-            clip_name="sigclip_vision_patch14_384.safetensors"
-        )

         loadimage_440 = loadimage.load_image(image=style_image)

-        clipvisionencode = NODE_CLASS_MAPPINGS["CLIPVisionEncode"]()
         clipvisionencode_439 = clipvisionencode.encode(
             crop="center",
             clip_vision=get_value_at_index(clipvisionloader_438, 0),
             image=get_value_at_index(loadimage_440, 0),
         )

-        stylemodelloader = NODE_CLASS_MAPPINGS["StyleModelLoader"]()
-        stylemodelloader_441 = stylemodelloader.load_style_model(
-            style_model_name="flux1-redux-dev.safetensors"
-        )
-
-        text_multiline = NODE_CLASS_MAPPINGS["Text Multiline"]()
         text_multiline_454 = text_multiline.text_multiline(text="FLUX_Redux")

-        emptylatentimage = NODE_CLASS_MAPPINGS["EmptyLatentImage"]()
-        cr_conditioning_input_switch = NODE_CLASS_MAPPINGS[
-            "CR Conditioning Input Switch"
-        ]()
-        cr_model_input_switch = NODE_CLASS_MAPPINGS["CR Model Input Switch"]()
-        stylemodelapplyadvanced = NODE_CLASS_MAPPINGS["StyleModelApplyAdvanced"]()
-        basicguider = NODE_CLASS_MAPPINGS["BasicGuider"]()
-        basicscheduler = NODE_CLASS_MAPPINGS["BasicScheduler"]()
-        samplercustomadvanced = NODE_CLASS_MAPPINGS["SamplerCustomAdvanced"]()
-        vaedecode = NODE_CLASS_MAPPINGS["VAEDecode"]()
-        saveimage = NODE_CLASS_MAPPINGS["SaveImage"]()
-        imagecrop = NODE_CLASS_MAPPINGS["ImageCrop+"]()

         emptylatentimage_10 = emptylatentimage.generate(
             width=get_value_at_index(imageresize_72, 1),
             height=get_value_at_index(imageresize_72, 2),
             batch_size=1,
         )
```

另外，为了预加载模型，我们需要使用 ComfyUI 的 `load_models_gpu` 函数，它会把上面预声明的模型里所有实际加载过的模型都载入（一个不错的经验法则：检查上面哪些加载了 `*.safetensors` 文件）

```
from comfy import model_management

#Add all the models that load a safetensors file
model_loaders = [dualcliploader_357, vaeloader_359, unetloader_358, clipvisionloader_438, stylemodelloader_441, downloadandloaddepthanythingv2model_437]

# Check which models are valid and how to best load them
valid_models = [
    getattr(loader[0], 'patcher', loader[0]) 
    for loader in model_loaders
    if not isinstance(loader[0], dict) and not isinstance(getattr(loader[0], 'patcher', None), dict)
]

#Finally loads the models
model_management.load_models_gpu(valid_models)
```

[查看 diff](https://gist.github.com/apolinario/47a8503c007c5ae8494324bed9e158ce/revisions#diff-faf377dc15b3371a15d2c4a03b4d012825533bd2fb2297852cb2244d07fe36eeL6) 以准确了解改了哪些地方

### 如果你不是 PRO 订阅用户（是的话跳过这步）

如果你不是 Hugging Face PRO 订阅用户，需要申请 ZeroGPU 配额。操作很简单：进入 Space 的 Settings 页面，提交一个 ZeroGPU grant 申请即可。所有以 ComfyUI 为后端的 Spaces 的 ZeroGPU 申请都会获批 🎉。

### 演示已上线

用本教程搭建的演示已经上线在 Hugging Face Spaces。来这儿玩：[https://huggingface.co/spaces/multimodalart/flux-style-shaping](https://huggingface.co/spaces/multimodalart/flux-style-shaping)

## 5. 结语

😮‍💨，全部讲完了！我知道这活儿不算少，但回报是用一个简单的 UI 就能分享你的工作流，还能给所有人提供免费推理！如前所述，我们的目标是在 2025 年初把这个流程尽可能自动化、 streamlined。节日快乐 🎅✨
