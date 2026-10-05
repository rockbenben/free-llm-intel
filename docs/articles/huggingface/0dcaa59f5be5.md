---
vendor: huggingface
title: 用 ONNX Runtime 和 Olive 加速 SD Turbo 与 SDXL Turbo 推理
original_title: Accelerating SD Turbo and SDXL Turbo Inference with ONNX Runtime and Olive
url: https://huggingface.co/blog/sdxl_ort_inference
date: 2024-02-03
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: fb5c1bfcc202
---

# 用 ONNX Runtime 和 Olive 加速 SD Turbo 与 SDXL Turbo 推理

## 引言

[SD Turbo](https://huggingface.co/stabilityai/sd-turbo) 和 [SDXL Turbo](https://huggingface.co/stabilityai/sdxl-turbo) 是两个快速的生成式文生图模型，最少只需一步就能产出可用图像——相比此前 Stable Diffusion 模型动辄 30+ 步，是巨大的改进。SD Turbo 是 [Stable Diffusion 2.1](https://huggingface.co/stabilityai/stable-diffusion-2-1) 的蒸馏版本，SDXL Turbo 是 [SDXL 1.0](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0) 的蒸馏版本。我们此前已[演示过](https://medium.com/microsoftazure/accelerating-stable-diffusion-inference-with-onnx-runtime-203bd7728540)如何用 ONNX Runtime 加速 Stable Diffusion 推理。ONNX Runtime 用在 SD Turbo 和 SDXL Turbo 上不仅有性能收益，还让模型能在 Python 以外的语言中使用，比如 C# 和 Java。

### 性能收益

本文介绍 ONNX Runtime 的 CUDA 与 TensorRT 执行提供者（execution provider）中的优化，它们显著加速了 SD Turbo 和 SDXL Turbo 在 NVIDIA GPU 上的推理。

在所有测试过的（批大小，步数）组合中，ONNX Runtime 都胜过 PyTorch：SDXL Turbo 的吞吐提升最高达 229%，SD Turbo 达 120%。ONNX Runtime CUDA 在动态 shape 下表现特别好，在静态 shape 下相对 PyTorch 也有明显提升。

[![](https://huggingface.co/blog/assets/sdxl_ort_inference/sdxl_turbo_ort_vs_torch.svg)](https://huggingface.co/blog/assets/sdxl_ort_inference/sdxl_turbo_ort_vs_torch.svg)

## 如何运行 SD Turbo 与 SDXL Turbo

要用 ONNX Runtime CUDA 执行提供者加速推理，请到 Hugging Face 获取我们优化过的 [SD Turbo](https://huggingface.co/tlwu/sd-turbo-onnxruntime) 和 [SDXL Turbo](https://huggingface.co/tlwu/sdxl-turbo-onnxruntime) 版本。

这些模型由 [Olive](https://github.com/microsoft/Olive/tree/main/examples/stable_diffusion) 生成——一个易用且感知硬件的模型优化工具。注意：要获得最佳性能，必须通过命令行启用 fp16 VAE，如所分享的优化版本所示。关于如何用托管在 Hugging Face 上的 ONNX 文件运行 SD 和 SDXL pipeline，见 [SD Turbo 使用示例](https://huggingface.co/tlwu/sd-turbo-onnxruntime#usage-example)和 [SDXL Turbo 使用示例](https://huggingface.co/tlwu/sdxl-turbo-onnxruntime#usage-example)。

要改用 ONNX Runtime TensorRT 执行提供者加速推理，请按[这里](https://github.com/microsoft/onnxruntime/blob/main/onnxruntime/python/tools/transformers/models/stable_diffusion/README.md#run-demo-with-docker)的说明操作。

下面是用 SDXL Turbo 模型按文本提示词生成图像的示例：

```
python3 demo_txt2img_xl.py \
  --version xl-turbo \
  "little cute gremlin wearing a jacket, cinematic, vivid colors, intricate masterpiece, golden ratio, highly detailed"
```

![生成的哥布林示例](https://huggingface.co/blog/assets/sdxl_ort_inference/gremlin_example_image.svg)
 *图 1. 用 SDXL Turbo 按文本提示词生成的"穿着夹克的小可爱哥布林"图像。*

注意示例图像只用 4 步就生成了，体现了 SD Turbo 和 SDXL Turbo 相比以往 Stable Diffusion 模型用更少步数产出可用图像的能力。

想要更友好的方式试用 Stable Diffusion 模型，请看我们的 [ONNX Runtime Automatic1111 SD WebUI 扩展](https://github.com/tianleiwu/Stable-Diffusion-WebUI-OnnxRuntime)。该扩展在 NVIDIA GPU 上优化执行 Stable Diffusion UNet 模型，使用 ONNX Runtime CUDA 执行提供者运行经 Olive 优化的模型推理。目前该扩展只针对 Stable Diffusion 1.5 做过优化；SD Turbo 和 SDXL Turbo 也能用，但性能优化仍在进行中。

### C# 与 Java 中的 Stable Diffusion 应用

借助 ONNX Runtime 的跨平台、性能与易用优势，社区成员也贡献了他们自己的 Stable Diffusion × ONNX Runtime 示例和 UI 工具。

这些社区贡献包括 [OnnxStack](https://github.com/saddam213/OnnxStack)——一个 .NET 库，在我们的[先前 C# 教程](https://github.com/cassiebreviu/StableDiffusion/)基础上构建，为用户用 C# 和 ONNX Runtime 做推理时提供覆盖多种 Stable Diffusion 模型的丰富能力。

此外，Oracle 发布了一个 [Java 版 Stable Diffusion 示例](https://github.com/oracle-samples/sd4j)，在 ONNX Runtime 之上运行推理。这个项目同样基于我们的 C# 教程。

## 基准结果

我们在 Standard_ND96amsr_A100_v4 虚拟机（A100-SXM4-80GB）和一台带 RTX-4090 GPU 的 [Lenovo 台式机](https://www.lenovo.com/us/en/p/desktops/legion-desktops/legion-t-series-towers/legion-tower-7i-gen-8-(34l-intel)/90v7003bus)（WSL Ubuntu 20.04）上对 SD Turbo 和 SDXL Turbo 做了基准测试，使用 LCM Scheduler 和 fp16 模型生成 512x512 分辨率图像。结果测量使用以下规格：

- onnxruntime-gpu==1.17.0（源码构建）
- torch==2.1.0a0+32f93b1
- tensorrt==8.6.1
- transformers==4.36.0
- diffusers==0.24.0
- onnx==1.14.1
- onnx-graphsurgeon==0.3.27
- polygraphy==0.49.0

要复现这些结果，建议使用"使用示例"一节中链接的说明。

由于 SDXL Turbo 的原始 VAE 无法以 fp16 精度运行，我们在 SDXL Turbo 测试中使用了 [sdxl-vae-fp16-fix](https://huggingface.co/madebyollin/sdxl-vae-fp16-fix)。它的输出与原始 VAE 略有差异，但解码出的图像对大多数用途足够接近。

静态 shape 的 PyTorch pipeline 应用了 channel-last 内存格式和带 reduce-overhead 模式的 torch.compile。

下面的图表展示了不同（批大小，步数）组合下各框架的吞吐（每秒图像数）。值得注意的是每根柱子上方的标签标明了相对 Torch Compile 的加速百分比——例如第一张图中，对（批，步）组合（4, 1），ORT_TRT (Static) 比 Torch (Compile) 快 31%。

我们选择 1 步和 4 步来测，因为 SD Turbo 和 SDXL Turbo 最少 1 步就能产出可用图像，但通常在 3-5 步时质量最佳。

### SDXL Turbo

下面两图展示 SDXL Turbo 模型在静态和动态 shape 下每秒图像数的吞吐，数据在 A100-SXM4-80GB GPU 上按不同（批大小，步数）组合采集。动态 shape 下，TensorRT 引擎支持批大小 1 到 8、图像尺寸 512x512 到 768x768，但针对批大小 1、图像尺寸 512x512 优化。

[![SDXL Turbo 在 A100 Tensor Cores GPU 上的吞吐（静态 shape）](https://huggingface.co/blog/assets/sdxl_ort_inference/sdxl_turbo_perf_chart_static.svg)](https://huggingface.co/blog/assets/sdxl_ort_inference/sdxl_turbo_perf_chart_static.svg) [![SDXL Turbo 在 A100 Tensor Cores GPU 上的吞吐（动态 shape）](https://huggingface.co/blog/assets/sdxl_ort_inference/sdxl_turbo_perf_chart_dynamic.svg)](https://huggingface.co/blog/assets/sdxl_ort_inference/sdxl_turbo_perf_chart_dynamic.svg)

### SD Turbo

接下来两图展示 SD Turbo 模型在 A100-SXM4-80GB GPU 上静态与动态 shape 的每秒图像数吞吐。

[![SD Turbo 在 A100 Tensor Cores GPU 上的吞吐（静态 shape）](https://huggingface.co/blog/assets/sdxl_ort_inference/sd_turbo_a100_perf_chart_static.svg)](https://huggingface.co/blog/assets/sdxl_ort_inference/sd_turbo_a100_perf_chart_static.svg) [![SD Turbo 在 A100 Tensor Cores GPU 上的吞吐（动态 shape）](https://huggingface.co/blog/assets/sdxl_ort_inference/sd_turbo_a100_perf_chart_dynamic.svg)](https://huggingface.co/blog/assets/sdxl_ort_inference/sd_turbo_a100_perf_chart_dynamic.svg)

最后一组图展示 SD Turbo 在 RTX-4090 GPU 上静态与动态 shape 的吞吐。动态 shape 测试中，TensorRT 引擎为批大小 1 到 8 构建（针对批大小 1 优化），并因显存限制固定图像尺寸 512x512。

[![SD Turbo 在 RTX 4090 上的吞吐（静态 shape）](https://huggingface.co/blog/assets/sdxl_ort_inference/sd_turbo_rtx_perf_chart_static.svg)](https://huggingface.co/blog/assets/sdxl_ort_inference/sd_turbo_rtx_perf_chart_static.svg) [![SD Turbo 在 RTX 4090 上的吞吐（动态 shape）](https://huggingface.co/blog/assets/sdxl_ort_inference/sd_turbo_rtx_perf_chart_dynamic.svg)](https://huggingface.co/blog/assets/sdxl_ort_inference/sd_turbo_rtx_perf_chart_dynamic.svg)

### 用 ONNX Runtime 的 SD Turbo 和 SDXL Turbo 有多快？

这些结果表明，在所有展示的（批，步）组合、静态与动态 shape 下，ONNX Runtime 搭配 CUDA 和 TensorRT 执行提供者都显著优于 PyTorch。这一结论对两种模型规模（SD Turbo 与 SDXL Turbo）以及测试的两种 GPU 都成立。值得注意的是，对（批，步）组合（1, 4），ONNX Runtime + CUDA（动态 shape）比 Torch Eager 快 229%。

另外，ONNX Runtime TensorRT 执行提供者在静态 shape 下略优——在多数（批，步）组合中 ORT_TRT 的吞吐高于对应的 ORT_CUDA。静态 shape 通常适合在图定义时就确定批大小和图像尺寸的用户（例如只计划用批大小 1、图像 512x512 生成图像）。这种情况下静态 shape 性能更快。但如果用户之后换用不同的批大小和/或图像尺寸，TensorRT 必须新建引擎（意味着磁盘上多一份引擎文件）并切换引擎（意味着加载新引擎的额外时间）。

另一方面，在 A100-SXM4-80GB GPU 上使用 SD Turbo 和 SDXL Turbo 时，动态 shape 下 ONNX Runtime + CUDA 往往是更好的选择；而在 RTX-4090 上，ONNX Runtime + TensorRT 在动态 shape 的多数（批，步）组合中略好。动态 shape 的好处在于：批大小和图像尺寸要到图执行时才确定时（例如一张图用批 1 + 512x512，另一张用批 4 + 512x768），用户能更快地运行推理。在这些情况下使用动态 shape，用户只需构建并保存一个引擎，而不是推理时来回切换引擎。

## GPU 优化

除了我们[上一篇 Stable Diffusion 博客](https://medium.com/microsoftazure/accelerating-stable-diffusion-inference-with-onnx-runtime-203bd7728540)介绍的技术，ONNX Runtime 还应用了以下优化以得到本文中的 SD Turbo 和 SDXL Turbo 结果：

- 为静态 shape 输入启用 CUDA graph。
- 添加 Flash Attention V2。
- 移除 text encoder 中的多余输出（保留 clip_skip 参数指定的 hidden state 输出）。
- 添加 SkipGroupNorm 融合，把组归一化与其前面的 Add 节点融合。

此外，我们新增了对一些特性的支持，包括潜一致性模型（LCM）的 [LoRA](https://huggingface.co/docs/peft/conceptual_guides/lora) 权重。

## 下一步

未来，我们计划通过更新 demo 支持新特性，把 Stable Diffusion 的工作继续做下去，例如 [IP Adapter](https://github.com/tencent-ailab/IP-Adapter) 和 Stable Video Diffusion。[ControlNet](https://huggingface.co/docs/diffusers/api/pipelines/controlnet) 支持也很快就会提供。

我们还在用现有的 [Stable Diffusion Web UI 扩展](https://github.com/tianleiwu/Stable-Diffusion-WebUI-OnnxRuntime)优化 SD Turbo 与 SDXL Turbo 的性能，并计划推动 ONNX Runtime 社区成员开发的 Windows UI 支持这两款模型。

另外，用 C# 和 ONNX Runtime 运行 SD Turbo 与 SDXL Turbo 的教程很快就来。在此期间，可以先看我们[之前的 Stable Diffusion C# 教程](https://onnxruntime.ai/docs/tutorials/csharp/stable-diffusion-csharp.html)。

## 资源

看看本文讨论的一些资源：

- [SD Turbo](https://huggingface.co/tlwu/sd-turbo-onnxruntime)：托管在 Hugging Face 上、为 ONNX Runtime CUDA 经 Olive 优化的 SD Turbo 模型。
- [SDXL Turbo](https://huggingface.co/tlwu/sdxl-turbo-onnxruntime)：托管在 Hugging Face 上、为 ONNX Runtime CUDA 经 Olive 优化的 SDXL Turbo 模型。
- [Stable Diffusion GPU 优化](https://github.com/microsoft/onnxruntime/blob/main/onnxruntime/python/tools/transformers/models/stable_diffusion/README.md)：ONNX Runtime GitHub 仓库中用 NVIDIA GPU 优化 Stable Diffusion 的说明。
- [ONNX Runtime Automatic1111 SD WebUI 扩展](https://github.com/tianleiwu/Stable-Diffusion-WebUI-OnnxRuntime)：在 NVIDIA GPU 上优化执行 Stable Diffusion UNet 模型的扩展。
- [OnnxStack](https://github.com/saddam213/OnnxStack)：社区贡献的 .NET 库，支持用 C# 和 ONNX Runtime 做 Stable Diffusion 推理。
- [SD4J（Java 中的 Stable Diffusion）](https://github.com/oracle-samples/sd4j)：Oracle 的 Java + ONNX Runtime Stable Diffusion 示例。
- [用 C# 和 ONNX Runtime 推理 Stable Diffusion](https://onnxruntime.ai/docs/tutorials/csharp/stable-diffusion-csharp.html)：此前发布的 C# 教程。
