---
vendor: huggingface
title: 用提前编译让您的 ZeroGPU Spaces 更加快速
original_title: Make your ZeroGPU Spaces go brrr with ahead-of-time compilation
url: https://huggingface.co/blog/zerogpu-aoti
date: 2026-09-01
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: 7ceb00aeb0c4
---

# 用提前编译让您的 ZeroGPU Spaces 更加快速

ZeroGPU 让每个人都能在 Hugging Face Spaces 上拉起强劲的 **Nvidia H200** 硬件，而不必为闲时流量占住一块 GPU。它高效、灵活，是做 demo 的理想选择——但它并不总能用尽 GPU 和 CUDA 技术栈能提供的一切。生成图像或视频可能耗时可观。在这种情况下，从 H200 硬件上榨出更多性能确实重要。

这就是 PyTorch 提前编译（ahead-of-time，AoT）登场的地方。与其在运行时现编模型（这和 ZeroGPU 的短生命周期进程合不来），AoT 让你优化一次、随时秒加载。

**结果**：demo 反应更快、体验更顺，在 Flux、Wan、LTX 这类模型上带来 **1.3×–1.8×** 的加速 🔥

本文展示如何在 ZeroGPU Spaces 中接入 Ahead-of-Time（AoT）编译。我们会探索 FP8 量化、动态形状等高级技巧，并分享可以直接上手的可运行 demo。等不及的话，欢迎去 [zerogpu-aoti](https://huggingface.co/zerogpu-aoti) 组织看看由 ZeroGPU 驱动的 demo。

> Pro 用户以及 Team / Enterprise 组织成员可以创建 ZeroGPU Space，而任何人都可以自由使用（Pro、Team 和 Enterprise 用户的 ZeroGPU 配额是 8 倍）

## 目录

- [什么是 ZeroGPU](https://huggingface.co/blog/zerogpu-aoti#what-is-zerogpu)
- [PyTorch 编译](https://huggingface.co/blog/zerogpu-aoti#pytorch-compilation)
- [ZeroGPU 上的提前编译](https://huggingface.co/blog/zerogpu-aoti#ahead-of-time-compilation-on-zerogpu)
- [坑](https://huggingface.co/blog/zerogpu-aoti#gotchas) [量化](https://huggingface.co/blog/zerogpu-aoti#quantization) [动态形状](https://huggingface.co/blog/zerogpu-aoti#dynamic-shapes) [多份编译 / 共享权重](https://huggingface.co/blog/zerogpu-aoti#multi-compile--shared-weights) [FlashAttention-3](https://huggingface.co/blog/zerogpu-aoti#flashattention-3) [区域编译](https://huggingface.co/blog/zerogpu-aoti#regional-compilation) [使用 Hub 上的已编译图](https://huggingface.co/blog/zerogpu-aoti#use-a-compiled-graph-from-the-hub)
- [AoT 编译的 ZeroGPU Spaces demo](https://huggingface.co/blog/zerogpu-aoti#aot-compiled-zerogpu-spaces-demos)
- [结论](https://huggingface.co/blog/zerogpu-aoti#conclusion)
- [资源](https://huggingface.co/blog/zerogpu-aoti#resources)

## 什么是 ZeroGPU

[Spaces](https://huggingface.co/spaces) 是 Hugging Face 提供的平台，让 ML 从业者能轻松发布 demo 应用。

Spaces 上的典型 demo 长这样：

```
import gradio as gr
from diffusers import DiffusionPipeline

pipe = DiffusionPipeline.from_pretrained(...).to('cuda')

def generate(prompt):
    return pipe(prompt).images

gr.Interface(generate, "text", "gallery").launch()
```

这挺好使，但结果是整个 Space 生命周期内都占着一块 GPU——哪怕没有任何用户活动。

当这行代码执行 `.to('cuda')`：

```
pipe = DiffusionPipeline.from_pretrained(...).to('cuda')
```

PyTorch 会初始化 NVIDIA 驱动，从此把这个进程永久绑定在 CUDA 上。考虑到 app 的流量从来不平滑、而是极其稀疏且尖峰化，这谈不上资源高效。

ZeroGPU 对 GPU 初始化采用 just-in-time（即时）方案。它不设置主进程的 CUDA，而是自动 fork 进程、在 fork 上初始化 CUDA、跑 GPU 任务，最后在需要释放 GPU 时杀掉 fork。

也就是说：

- app 没有流量时，完全不使用 GPU
- 真正执行任务时，使用一块 GPU
- 需要并发执行任务时，可以用多块 GPU

多亏 Python 的 `spaces` 包，要获得这个行为只需一处代码改动：

```
  import gradio as gr
+ import spaces
  from diffusers import DiffusionPipeline

  pipe = DiffusionPipeline.from_pretrained(...).to('cuda')

+ @spaces.GPU
  def generate(prompt):
      return pipe(prompt).images

  gr.Interface(generate, "text", "gallery").launch()
```

通过 import `spaces` 并加上 `@spaces.GPU` 装饰器，我们：

- 拦截 PyTorch API 调用，推迟 CUDA 操作
- 让被装饰的函数在调用时于 fork 中运行
- （还会调用一个内部 API 让正确的设备对 fork 可见，但这超出本文范围）

> ZeroGPU 目前分配的是 H200 的 MIG 切片（3g.71gb profile）。更多 MIG 规格，包括整片（7g.141gb profile），将于 2025 年底推出。

## PyTorch 编译

PyTorch、JAX 等现代 ML 框架都有「编译」概念，用来优化模型延迟或推理时间。编译在幕后执行一连串（往往依赖硬件的）优化步骤，如算子融合、常量折叠等。

PyTorch（2.0 起）目前有两个主要编译接口：

- 即时编译（JIT）：`torch.compile`
- 提前编译（AoT）：`torch.export` + `AOTInductor`

[`torch.compile`](https://docs.pytorch.org/tutorials/intermediate/torch_compile_tutorial.html) 在标准环境里表现出色：第一次运行时编译模型，后续调用复用优化版本。

但在 ZeroGPU 上，进程几乎每个 GPU 任务都是全新拉起的，这意味着 `torch.compile` 无法高效复用编译结果，只能依赖它的[文件系统缓存](https://docs.pytorch.org/tutorials/recipes/torch_compile_caching_tutorial.html#modular-caching-of-torchdynamo-torchinductor-and-triton)来恢复已编译模型。视模型而定，这个过程要花几十秒到几分钟——对 Spaces 里的实用 GPU 任务来说太久了。

这正是 **ahead-of-time（AoT）编译**大显身手之处。

用 AoT，我们可以把编译出的模型导出一次、保存下来，之后在任何进程里即刻重新加载——这正是 ZeroGPU 需要的。它帮我们降低框架开销，也消除了 JIT 编译通常带来的冷启动耗时。

那我们在 ZeroGPU 上怎么做提前编译？往下看。

## ZeroGPU 上的提前编译

回到我们的 ZeroGPU 基础示例，拆开看看启用 AoT 编译需要什么。这个 demo 我们用 `black-forest-labs/FLUX.1-dev` 模型：

```
import gradio as gr
import spaces
import torch
from diffusers import DiffusionPipeline

MODEL_ID = 'black-forest-labs/FLUX.1-dev'

pipe = DiffusionPipeline.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16)
pipe.to('cuda')

@spaces.GPU
def generate(prompt):
    return pipe(prompt).images

gr.Interface(generate, "text", "gallery").launch()
```

> 下文讨论中我们只编译 pipe 的 transformer 组件，因为在这些生成模型里，transformer（更一般地说是去噪器）是计算量最大的部件。

在 PyTorch 中提前编译模型分多步：

### 1. 获取示例输入

记住我们是在模型运行*之前*编译，因此需要为模型弄到示例输入。注意这些就是我们期望在实际运行中看到的同类输入。为捕获这些输入，我们借助 `spaces` 包里的 `spaces.aoti_capture` 助手：

```
with spaces.aoti_capture(pipe.transformer) as call:
    pipe("arbitrary example prompt")
```

`aoti_capture` 作为上下文管理器使用时，会拦截对任意可调用对象（这里是 `pipe.transformer`）的调用，阻止其执行，捕获本应传入的参数，并把值存进 `call.args` 和 `call.kwargs`。

### 2. 导出模型

有了 transformer 组件的示例 args 和 kwargs，就可以用 [`torch.export.export`](https://docs.pytorch.org/docs/stable/export.html#torch.export.export) 把它导出为 PyTorch 的 [`ExportedProgram`](https://docs.pytorch.org/docs/stable/export.html#torch.export.ExportedProgram)：

```
exported_transformer = torch.export.export(
    pipe.transformer,
    args=call.args,
    kwargs=call.kwargs,
)
```

导出的 PyTorch 程序是一个计算图，表示张量计算以及原始模型参数值。

### 3. 编译导出的模型

模型导出之后，编译就相当直接。

PyTorch 传统的 AoT 编译通常要把模型存盘以便稍后重新加载。在我们的场景里，用 `spaces` 包提供的助手函数 `spaces.aoti_compile`。它是 `torch._inductor.aot_compile` 的一个小封装，按需管理模型的保存和懒加载。用法如下：

```
compiled_transformer = spaces.aoti_compile(exported_transformer)
```

这个 `compiled_transformer` 现在就是可投入推理的 AoT 编译二进制。

### 4. 在 pipeline 中使用编译后的模型

接下来要把编译好的 transformer 绑回原来的 `pipe`。

一个天真、几乎能用的做法是直接 `pipe.transformer = compiled_transformer` 打补丁。遗憾的是这不行，因为会丢掉 `dtype`、`config` 等重要属性。只补丁 `forward` 方法也不行，因为这样原始模型参数还留在内存里，运行时常常 OOM。

`spaces` 包对这个也提供了工具——`spaces.aoti_apply`：

```
spaces.aoti_apply(compiled_transformer, pipe.transformer)
```

Et voilà! 它会负责用编译后的模型打补丁 `pipe.transformer.forward`，同时[把旧模型参数清出内存](https://pypi-browser.org/package/spaces/spaces-0.40.1-py3-none-any.whl/spaces/zero/torch/aoti.py#L87)。

### 5. 串起来

要执行前三步（拦截示例输入、导出模型、用 PyTorch inductor 编译），需要真实的 GPU。`@spaces.GPU` 函数之外拿到的 CUDA 模拟不够用，因为编译是真正依赖硬件的——例如依靠 micro-benchmark 运行来调优生成的代码。所以我们要把这一切包进一个 `@spaces.GPU` 函数，再把编译好的模型取回 app 的根部。从原始 demo 代码出发，最终是这样：

```
  import gradio as gr
  import spaces
  import torch
  from diffusers import DiffusionPipeline
  
  MODEL_ID = 'black-forest-labs/FLUX.1-dev'
  
  pipe = DiffusionPipeline.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16)
  pipe.to('cuda')
  
+ @spaces.GPU(duration=1500) # maximum duration allowed during startup
+ def compile_transformer():
+     with spaces.aoti_capture(pipe.transformer) as call:
+         pipe("arbitrary example prompt")
+ 
+     exported = torch.export.export(
+         pipe.transformer,
+         args=call.args,
+         kwargs=call.kwargs,
+     )
+     return spaces.aoti_compile(exported)
+ 
+ compiled_transformer = compile_transformer()
+ spaces.aoti_apply(compiled_transformer, pipe.transformer)
  
  @spaces.GPU
  def generate(prompt):
      return pipe(prompt).images
  
  gr.Interface(generate, "text", "gallery").launch()
```

只加了十几行代码，我们的 demo 就明显更快了（FLUX.1-dev 场景下快 **1.7 倍**）。

想更多了解 AoT 编译，可以读 PyTorch 的 [AOTInductor 教程](https://docs.pytorch.org/tutorials/recipes/torch_export_aoti_python.html)

## 坑

展示完在 ZeroGPU 约束下能实现的速度提升后，我们聊聊这套配置中遇到的一些坑。

### 量化

AoT 可以与量化结合，带来更大的加速。对图像和视频生成，FP8 训练后动态量化方案能在速度和质量之间给出不错的权衡。不过 FP8 需要至少 9.0 的 CUDA compute capability。好在 ZeroGPU 基于 H200，我们正好能享用 FP8 量化方案。

要在我们的 AoT 编译工作流中启用 FP8 量化，可以用 [`torchao`](https://github.com/pytorch/ao) 提供的 API，像这样：

```
+ from torchao.quantization import quantize_, Float8DynamicActivationFloat8WeightConfig

+ # Quantize the transformer just before the export step.
+ quantize_(pipe.transformer, Float8DynamicActivationFloat8WeightConfig())

exported_transformer = torch.export.export(
    pipe.transformer,
    args=call.args,
    kwargs=call.kwargs,
)
```

（关于 TorchAO 的更多细节见[这里](https://docs.pytorch.org/ao/stable/index.html)。）

之后照前文继续执行其余步骤即可。使用量化又带来 **1.2 倍**加速。

### 动态形状

图像和视频有不同形状和尺寸。因此在 AoT 编译时也要考虑形状动态性。`torch.export.export` 提供的原语可以很方便地配置哪些输入应按动态形状处理，如下所示。

对 Flux.1-Dev 的 transformer，不同图像分辨率会影响它 `forward` 的两个参数：

- `hidden_states`：带噪输入 latents，transformer 负责对其去噪。它是 3D 张量，表示 `batch_size, flattened_latent_dim, embed_dim`。batch size 固定时，图像分辨率变化改变的是 `flattened_latent_dim`。
- `img_ids`：编码像素坐标的 2D 数组，形状为 `height * width, 3`。这里我们要把 `height * width` 设为动态。

我们先定义希望让（latent）图像分辨率浮动的范围。为得到这些取值范围，我们观察了 pipeline 中 [`hidden_states`](https://github.com/huggingface/diffusers/blob/0ff1aa910cf3d87193af79ec1ae4487be542e872/src/diffusers/pipelines/flux/pipeline_flux.py#L920) 随图像分辨率变化时的形状。具体取值依赖模型，需要手动检查和一些直觉。对 Flux.1-Dev，我们最终定为：

```
transformer_hidden_dim = torch.export.Dim('hidden', min=4096, max=8212)
```

然后定义参数名到「输入值中哪些维度应为动态」的映射：

```
transformer_dynamic_shapes = {
    "hidden_states": {1: transformer_hidden_dim}, 
    "img_ids": {0: transformer_hidden_dim},
}
```

接着要让动态形状对象复刻示例输入的结构。不需要动态形状的输入必须设为 `None`。用 PyTorch 的 [tree_map](https://github.com/pytorch/pytorch/blob/2f0de0ff9361ca4f2b1e6f9edbc600b5fb6abcd6/torch/utils/_pytree.py#L1341-L1373) 工具做这件事非常方便：

```
from torch.utils._pytree import tree_map

dynamic_shapes = tree_map(lambda v: None, call.kwargs)
dynamic_shapes |= transformer_dynamic_shapes
```

现在执行导出步骤时，只需把 `transformer_dynamic_shapes` 传给 `torch.export.export`：

```
exported_transformer = torch.export.export(
    pipe.transformer,
    args=call.args,
    kwargs=call.kwargs,
    dynamic_shapes=dynamic_shapes,
)
```

> 看看这个 Space，它在导出步骤同时使用了量化和动态形状。

### 多份编译 / 共享权重

当动态性太重要时，动态形状有时不够用。

比如 Wan 系列视频生成模型，如果你想让编译后的模型输出不同分辨率，就是这种情况。此时可以做的是：每个分辨率编译一份模型，模型参数保持共享，运行时分发到正确的那一份。

这是该方案的最小示例：[zerogpu-aoti-multi.py](https://gist.github.com/cbensimon/8dc0ffcd7ee024d91333f6df01907916)。完整可运行的实现见 [Wan 2.2 Space](https://huggingface.co/spaces/zerogpu-aoti/wan2-2-fp8da-aoti-faster/blob/main/optimization.py)。

### FlashAttention-3

ZeroGPU 硬件和 CUDA 驱动与 Flash-Attention 3（FA3）完全兼容，因此可以在 ZeroGPU Space 里用它进一步提速。FA3 兼容提前编译，对我们来说堪称完美。

从源码编译构建 FA3 要花好几分钟，而且依赖硬件。作为用户，我们不想浪费宝贵的 ZeroGPU 算力小时。Hugging Face 的 [`kernels` 库](https://github.com/huggingface/kernels)此时出手救援：它提供针对特定硬件预构建好的 kernel。例如我们尝试运行：

```
from kernels import get_kernel

vllm_flash_attn3 = get_kernel("kernels-community/vllm-flash-attn3")
```

它会尝试从 [`kernels-community/vllm-flash-attn3`](https://huggingface.co/kernels-community/vllm-flash-attn3) 仓库加载与当前环境兼容的 kernel；不兼容就会报错。幸运的是，这在 ZeroGPU Spaces 上无缝可用。这意味着我们可以借 `kernels` 库在 ZeroGPU 上发挥 FA3 的威力。

这里有一份[完整可用的 FA3 attention processor 示例](https://gist.github.com/sayakpaul/ff715f979793d4d44beb68e5e08ee067#file-fa3_qwen-py)，用于 Qwen-Image 模型。

### 区域编译

到目前为止我们编译的是整个模型。视模型而定，全模型编译可能导致很长的冷启动。冷启动太久会让开发体验很难受。

我们也可以只编译模型内部的*区域*，大幅缩短冷启动时间，同时保留全模型编译几乎全部收益。当模型有重复计算块时，区域编译特别有前景。例如标准语言模型就有许多结构相同的 Transformer 块。

在我们的例子里，可以提前编译 Flux transformer 的重复块，再把编译图传播给其余重复块。[Flux Transformer](https://github.com/huggingface/diffusers/blob/c2e5ece08bf22d249c62e964f91bc326cf9e3759/src/diffusers/models/transformers/transformer_flux.py) 有两种重复块：`FluxTransformerBlock` 和 `FluxSingleTransformerBlock`。

完整示例见[这个 Space](https://huggingface.co/spaces/cbensimon/FLUX.1-dev-fa3-aoti/tree/main)。

> 💡 对 Flux.1-Dev，切换到区域编译把编译时间从 6 分钟降到 30 秒，同时给出相同的加速。

### 使用 Hub 上的已编译图

模型（甚至一个模型块）提前编译之后，我们可以把编译图模块序列化为工件供之后复用。对 Spaces 上的 ZeroGPU demo 而言，这能跳过编译时间、大幅削减启动时间。

为节省存储空间，我们可以只保存编译好的模型图，工件里不包含任何模型参数。

看看这个 [collection](https://huggingface.co/collections/zerogpu-aoti/using-compiled-graph-from-the-hub-68c2afcc03de7609f9f91e35)：完整演示获取编译模型图、推到 Hub、再用它搭建 demo 的工作流。

## AoT 编译的 ZeroGPU Spaces demo

### 加速对比

- [不带 AoTI 的 FLUX.1-dev](https://huggingface.co/spaces/zerogpu-aoti/FLUX.1-dev-base)
- [带 AoTI 和 FA3 的 FLUX.1-dev](https://huggingface.co/spaces/zerogpu-aoti/FLUX.1-dev-fa3-aoti)（**1.75 倍**加速）

### 精选 AoTI Spaces

- [FLUX.1 Kontext](https://huggingface.co/spaces/zerogpu-aoti/FLUX.1-Kontext-Dev)
- [QwenImage Edit](https://huggingface.co/spaces/multimodalart/Qwen-Image-Edit-Fast)
- [Wan 2.2](https://huggingface.co/spaces/zerogpu-aoti/wan2-2-fp8da-aoti-faster)

### 区域编译

- [区域编译配方](https://docs.pytorch.org/tutorials/recipes/regional_compilation.html)
- [带 AOT 的区域编译](https://docs.pytorch.org/tutorials/recipes/regional_aot.html)
- [Diffusers 中的原生集成](https://huggingface.co/docs/diffusers/main/en/optimization/fp16)
- [更多性能数字](https://pytorch.org/blog/torch-compile-and-diffusers-a-hands-on-guide-to-peak-performance/)

## 结论

Hugging Face Spaces 里的 ZeroGPU 是一项为 AI 构建者提供强劲算力入口的强大能力。本文展示了用户如何利用 PyTorch 的提前编译技术加速使用 ZeroGPU 的应用。

我们在 Flux.1-Dev 上演示了加速，但这些技术并不局限于这一个模型。鼓励你试一试这些技术，并在这个[社区讨论](https://huggingface.co/spaces/zerogpu-aoti/README/discussions/1)里给我们反馈。

## 资源

- 访问我们在 Hub 上的 [ZeroGPU-AOTI org](https://huggingface.co/zerogpu-aoti)，查看运用本文技术的 demo 合集。
- 浏览 `spaces.aoti_*` API 的[源码](https://pypi-browser.org/package/spaces/spaces-0.40.1-py3-none-any.whl/spaces/zero/torch/aoti.py)，了解接口细节
- 看看 hub 上的 [Kernels Community org](https://huggingface.co/kernels-community)
- 从[这里](https://huggingface.co/blog/pytorch.org/tutorials/recipes/regional_compilation.html)了解更多区域编译
- 升级到 Hugging Face [Pro](https://huggingface.co/pro)，创建你自己的 ZeroGPU Space（每天可得 25 分钟 H200 使用）

*致谢：感谢 ChunTe Lee 为本文制作了出色的缩略图。感谢 Pedro 和 Vaibhav 对文章的反馈。感谢 PyTorch 团队的 Angela Yi 在 AOT 上给予我们的指导。*
