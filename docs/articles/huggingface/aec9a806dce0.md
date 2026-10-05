---
vendor: huggingface
title: 面向大规模 transformers 的 8-bit 矩阵乘法入门：基于 transformers、accelerate 和 bitsandbytes
original_title: A Gentle Introduction to 8-bit Matrix Multiplication for transformers at scale using transformers, accelerate and bitsandbytes
url: https://huggingface.co/blog/hf-bitsandbytes-integration
date: 2022-08-17
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 4b76a315eec8
translator: agent
---

返回文章列表

# 面向大规模 transformers 的 8-bit 矩阵乘法入门：基于 Hugging Face Transformers、Accelerate 和 bitsandbytes

发布于
					2022 年 8 月 17 日

在 GitHub 上更新

点赞

140

- [![](https://huggingface.co/avatars/ee3327ba714e824e0e04d5cd6f950770.svg)](https://huggingface.co/TengWang)
- [![](https://huggingface.co/avatars/f94b783c8f49019ebb0a69f6e3053b77.svg)](https://huggingface.co/jeongah)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1648631057413-noauth.png)](https://huggingface.co/ybelkada)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63ce875d199b36f7552d4f07/bpUrvhXDagzRqZ3vxTcSF.jpeg)](https://huggingface.co/marcsun13)
- [![](https://huggingface.co/avatars/a454cde25975abd09acb20067b447720.svg)](https://huggingface.co/fordacre)
- [![](https://huggingface.co/avatars/269b11f3b48a48e8a5a34a7d85d53bce.svg)](https://huggingface.co/rsarkar1)

Younes B

ybelkada

Tim Dettmers

timdettmers

guest

本文也有中文版本 [简体中文](https://huggingface.co/blog/zh/hf-bitsandbytes-integration)。

[![thumbnail](https://huggingface.co/blog/assets/96_hf_bitsandbytes_integration/Thumbnail_blue.png)](https://huggingface.co/blog/assets/96_hf_bitsandbytes_integration/Thumbnail_blue.png)

## 引言

语言模型的体积一直在变大。写作本文时，PaLM 有 540B 参数，OPT、GPT-3 和 BLOOM 大约 176B 参数，而且趋势是朝着更大的模型去。下面这张图展示了一些近期语言模型的规模。

[![LLM](https://huggingface.co/blog/assets/96_hf_bitsandbytes_integration/LLM3.png)](https://huggingface.co/blog/assets/96_hf_bitsandbytes_integration/LLM3.png)

因此，这些模型很难在容易入手的设备上运行。举个例子，只做 BLOOM-176B 的推理就需要 8 块 80GB 的 A100 GPU（每块约 1.5 万美元）。要微调 BLOOM-176B，则需要 72 块这样的 GPU！更大的模型，比如 PaLM，需要的资源还要多。

正因为这些超大模型需要这么多 GPU 才能跑起来，我们需要找到既降低资源需求、又保住模型性能的办法。业界已经发展出多种试图缩小模型体积的技术——你可能听说过量化（quantization）和蒸馏（distillation），此外还有很多。

完成 BLOOM-176B 的训练之后，我们 HuggingFace 和 BigScience 一直在想办法让这个大模型能在更少的 GPU 上运行。通过 BigScience 社区，我们了解到关于 Int8 推理的研究：它不损害大型模型的预测性能，却能把大型模型的内存占用降低 2 倍。很快我们就开始参与这项合作研究，最终把它完整地集成进了 Hugging Face `transformers`。随着这篇博客，我们为所有 Hugging Face 模型提供 LLM.int8() 集成，下面会详细解释。想深入了解这项研究，可以读我们的论文 [LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale](https://arxiv.org/abs/2208.07339)。

本文侧重对这项量化技术的高层概览，梳理把它纳入 `transformers` 库时遇到的困难，并展望这一合作的长期目标。

在这里你将了解到：一个大模型究竟为什么这么吃内存？BLOOM 的 350GB 是怎么来的？我们从几个基本前提开始逐步展开。

## 机器学习中的常见数据类型

我们先理解不同的浮点数据类型——在机器学习语境里它们也常被称为“精度”（precision）。

模型的大小由其参数数量和参数精度决定，精度通常是 float32、float16 或 bfloat16（下图来自：[https://blogs.nvidia.com/blog/2020/05/14/tensorfloat-32-precision-format/](https://blogs.nvidia.com/blog/2020/05/14/tensorfloat-32-precision-format/)）。

[![Summary](https://huggingface.co/blog/assets/96_hf_bitsandbytes_integration/tf32-Mantissa-chart-hi-res-FINAL.png)](https://huggingface.co/blog/assets/96_hf_bitsandbytes_integration/tf32-Mantissa-chart-hi-res-FINAL.png)

Float32（FP32）是标准化的 IEEE 32 位浮点表示。用这种数据类型可以表示很宽的浮点数范围。FP32 中，“指数”占 8 位，“尾数”占 23 位，符号占 1 位。此外，绝大多数硬件都支持 FP32 运算和指令。

在 float16（FP16）数据类型中，指数占 5 位，尾数占 10 位。这使得 FP16 可表示的范围比 FP32 小得多，FP16 数因此面临溢出（表示非常大的数）和下溢（表示非常小的数）的风险。

举个例子，如果你计算 `10k * 10k`，结果是 `100M`，这在 FP16 里表示不了——FP16 最大只能到 `64k`。于是你会得到 `NaN`（Not a Number），而在神经网络这种顺序计算中，之前的工作全部报废。通常用 loss scaling 来绕过这个问题，但它并不总是奏效。

为了避免这些限制，人们创造了新格式 bfloat16（BF16）。BF16 的指数占 8 位（与 FP32 相同），小数部分占 7 位。

这意味着 BF16 能保留和 FP32 一样的动态范围，但相比 FP16 少了 3 位精度。现在表示超大数值完全没问题了，只是精度比 FP16 差。

在 Ampere 架构上，NVIDIA 还引入了 [TensorFloat-32](https://blogs.nvidia.com/blog/2020/05/14/tensorfloat-32-precision-format/)（TF32）精度格式， combining BF16 的动态范围和 FP16 的精度，只使用 19 位。它目前只在某些运算内部使用。

在机器学习的行话里，FP32 叫全精度（full precision，4 字节），BF16 和 FP16 叫半精度（half-precision，2 字节）。另外，int8（INT8）数据类型是一种 8 位表示，可以存储 2^8 个不同的值（范围 [0, 255]，有符号整数为 [-128, 127]）。

理想情况下训练和推理都应在 FP32 下进行，但它比 FP16/BF16 慢一倍，所以实践中采用混合精度方案：权重以 FP32 保存为精确的“主权重”（main weights）参照，而前向和反向传播用 FP16/BF16 计算以加快训练。FP16/BF16 的梯度随后用来更新 FP32 主权重。

训练期间主权重始终存为 FP32，但实际上半精度权重在推理时往往能提供与 FP32 相近的质量——只有在模型要接收多次梯度更新时才需要精确参照。这意味着我们可以直接用半精度权重，用一半的 GPU 达到同样效果。

[![Model-storage](https://huggingface.co/blog/assets/96_hf_bitsandbytes_integration/Model-storage.png)](https://huggingface.co/blog/assets/96_hf_bitsandbytes_integration/Model-storage.png)

计算模型字节数的方法是：参数数量乘以所选精度的字节数。例如 BLOOM-176B 的 bfloat16 版本，我们有 `176*10**9 x 2 bytes = 352GB`！如前所述，把这么大的模型塞进几块 GPU 相当困难。

但能不能用另一种数据类型、以更少内存存储这些权重？深度学习里广泛使用了一种叫量化的方法。

## 模型量化简介

实验上我们发现，与其用 4 字节的 FP32 精度，用 2 字节的 BF16/FP16 半精度可以得到几乎一致的推理结果，模型体积减半。要是能再减半就太好了，但精度再低下去，推理质量就会急剧下降。

为此我们引入 8-bit 量化。这种方法只用四分之一的精度，模型只需要 1/4 的体积！但这不是简单地再砍掉一半位数就能做到的。

量化本质上是从一种数据类型向另一种“取整”。例如，一种数据类型范围是 0..9，另一种是 0..4，那么第一种里的“4”会四舍五入成第二种里的“2”。但如果第一种里是“3”，它介于第二种的 1 和 2 之间，一般也会取整到“2”。可以看到，第一种的“4”和“3”在第二种里都成了“2”。这说明量化是一个有噪声的过程，会造成信息损失——某种意义上的有损压缩。

两种最常见的 8-bit 量化技术是 zero-point 量化和绝对最大值（absmax）量化。Zero-point 量化和 absmax 量化把浮点值映射到更紧凑的 int8（1 字节）值。首先，这些方法通过乘一个量化常数对输入做归一化。

例如在 zero-point 量化中，如果我的范围是 -1.0…1.0，想量化到 -127…127，那我就乘以 127 再取整到 8-bit 精度。要还原原始值，需要把 int8 值除以同一个量化因子 127。比如 0.3 会被缩放成 `0.3*127 = 38.1`，取整得 38。反推回去得到 `38/127=0.2992`——本例的量化误差是 0.008。这些看似微小的误差会在模型各层传播中累积放大，导致性能下降。

[![quantization](https://huggingface.co/blog/assets/96_hf_bitsandbytes_integration/quantization.png)](https://huggingface.co/blog/assets/96_hf_bitsandbytes_integration/quantization.png)

（图片来自：[这篇博客](https://intellabs.github.io/distiller/algo_quantization.html)）

再来看 absmax 量化的细节。要计算 fp16 数与其对应 int8 数之间的映射，先除以张量的绝对最大值，再乘以数据类型的总范围。

例如，假设你要对向量 `[1.2, -0.5, -4.3, 1.2, -3.1, 0.8, 2.4, 5.4]` 做 absmax 量化。先提取绝对最大值，这里是 `5.4`。Int8 的范围是 `[-127, 127]`，用 127 除以 `5.4` 得到缩放因子 `23.5`。把原向量乘以它就得到量化后的向量 `[28, -12, -101, 28, -73, 19, 56, 127]`。

[![out-quant.gif](https://huggingface.co/blog/assets/96_hf_bitsandbytes_integration/out-quant.gif)](https://huggingface.co/blog/assets/96_hf_bitsandbytes_integration/out-quant.gif)

要还原，只需在全精度下用 int8 数除以量化因子；但由于上面做了“取整”，一些精度会丢失。

[![quant-freeze](https://huggingface.co/blog/assets/96_hf_bitsandbytes_integration/quant-freeze.png)](https://huggingface.co/blog/assets/96_hf_bitsandbytes_integration/quant-freeze.png)

对于无符号 int8，我们会减去最小值并按绝对最大值缩放。这接近 zero-point 量化的做法。它类似 min-max 缩放，但后者保持数值尺度的方式是：“0”这个值总能被某个整数精确表示，没有量化误差。

在做矩阵乘法以求更高精度时，这些技巧可以组合出多种花样，比如按行（row-wise）或按向量（vector-wise）量化。看矩阵乘法 A*B=C：不同于按张量绝对最大值归一化的常规量化，vector-wise 量化会分别求 A 的每一行、B 的每一列的绝对最大值，然后用这些向量除 A 和 B 做归一化，再计算 A*B 得到 C。最后要回到 FP16 值，就用 A 和 B 的绝对最大值向量做外积来反归一化。更多细节见 [LLM.int8() 论文](https://arxiv.org/abs/2208.07339)，或 Tim 博客上[关于量化与涌现特征的文章](https://timdettmers.com/2022/08/17/llm-int8-and-emergent-features/)。

这些基础技术让我们能够量化深度学习模型，但对大模型通常会带来精度下降。我们集成到 Hugging Face Transformers 和 Accelerate 库里的 LLM.int8() 实现，是第一个即使是 176B 参数的大模型（如 BLOOM）也不损失性能的技术。

## LLM.int8() 温和入门：大语言模型的零损失矩阵乘法

在 LLM.int8() 中，我们证明了：要理解为什么传统量化对大模型会失败，就必须理解 transformers 中尺度相关的涌现特性（scale-dependent emergent properties）。我们表明性能退化是由离群特征（outlier features）造成的，下一节会解释。LLM.int8() 算法本身可以这样理解。

本质上，LLM.int8() 分三步完成矩阵乘法计算：

- 从输入的隐藏状态中，按列提取离群值（即大于某个阈值的值）。
- 对离群部分用 FP16 做矩阵乘法，对非离群部分用 int8 做矩阵乘法。
- 将非离群结果反量化，把离群与非离群结果相加，得到 FP16 的完整结果。

这些步骤可以总结在下面这个动画里：

[![Mixed-int8.gif](https://huggingface.co/blog/assets/96_hf_bitsandbytes_integration/Mixed-int8.gif)](https://huggingface.co/blog/assets/96_hf_bitsandbytes_integration/Mixed-int8.gif)

### 离群特征的重要性

一个值落在某些数全局分布范围之外，通常就被称为离群值（outlier）。离群值检测在现有文献中被广泛应用和讨论，而对你特征分布的先验知识有助于完成离群值检测任务。更具体地，我们观察到经典量化在 >6B 参数的 transformer 模型上大规模失效。虽然较小的模型里也存在大的离群特征，但我们观察到越过某个阈值后，这些离群值在 transformer 中呈现出高度系统的模式，且存在于 transformer 的每一层。关于这些现象的更多细节，见 [LLM.int8() 论文](https://arxiv.org/abs/2208.07339)和[涌现特征博客文章](https://timdettmers.com/2022/08/17/llm-int8-and-emergent-features/)。

如前所述，8-bit 精度限制极其严格，因此量化一个含多个大值的向量可能产生非常离谱的错误结果。而且，transformer 架构有一个把所有元素相互关联的内建特性，这些误差会随层间传播不断复合放大。因此人们发展了混合精度分解（mixed-precision decomposition），以便在存在这种极端离群值时仍能高效量化。下一节展开。

### MatMul 内部

计算出隐藏状态后，我们用自定义阈值提取离群值，把矩阵分解成上面所述的两部分。我们发现，以这种方式提取所有幅值 ≥6 的离群值，就能完全恢复推理性能。离群部分用 fp16 做经典矩阵乘法；8-bit 矩阵乘法则通过 vector-wise 量化把权重和隐藏状态都量化到 8-bit 精度——即隐藏状态按行量化、权重矩阵按列量化。这一步之后，结果被反量化并以半精度返回，以便与第一个矩阵乘法的结果相加。

[![Matmul.png](https://huggingface.co/blog/assets/96_hf_bitsandbytes_integration/Matmul.png)](https://huggingface.co/blog/assets/96_hf_bitsandbytes_integration/Matmul.png)

### “零退化”是什么意思？

我们该如何恰当地评估这个方法带来的性能退化？用 8-bit 模型会在生成质量上损失多少？

我们用 lm-eval-harness 在 8-bit 模型和原生模型上跑了几个常用基准并报告结果。

OPT-175B 的结果：

| 基准 | - | - | - | - | 差值 |
| --- | --- | --- | --- | --- | --- |
| 名称 | 指标 | int8 值 | fp16 值 | fp16 标准误 | - |
| hellaswag | acc_norm | 0.7849 | 0.7849 | 0.0041 | 0 |
| hellaswag | acc | 0.5921 | 0.5931 | 0.0049 | 0.001 |
| piqa | acc | 0.7965 | 0.7959 | 0.0094 | 0.0006 |
| piqa | acc_norm | 0.8101 | 0.8107 | 0.0091 | 0.0006 |
| lambada | ppl | 3.0142 | 3.0152 | 0.0552 | 0.001 |
| lambada | acc | 0.7464 | 0.7466 | 0.0061 | 0.0002 |
| winogrande | acc | 0.7174 | 0.7245 | 0.0125 | 0.0071 |

BLOOM-176 的结果：

| 基准 | - | - | - | - | 差值 |
| --- | --- | --- | --- | --- | --- |
| 名称 | 指标 | int8 值 | bf16 值 | bf16 标准误 | - |
| hellaswag | acc_norm | 0.7274 | 0.7303 | 0.0044 | 0.0029 |
| hellaswag | acc | 0.5563 | 0.5584 | 0.005 | 0.0021 |
| piqa | acc | 0.7835 | 0.7884 | 0.0095 | 0.0049 |
| piqa | acc_norm | 0.7922 | 0.7911 | 0.0095 | 0.0011 |
| lambada | ppl | 3.9191 | 3.931 | 0.0846 | 0.0119 |
| lambada | acc | 0.6808 | 0.6718 | 0.0065 | 0.009 |
| winogrande | acc | 0.7048 | 0.7048 | 0.0128 | 0 |

我们确实观察到这些模型零性能退化，因为各指标的绝对差值都小于标准误（只有 BLOOM-int8 在 lambada 上略好于原生模型）。想更细致地了解与 SOTA 方法的性能对比，请看[论文](https://arxiv.org/abs/2208.07339)！

### 它比原生模型更快吗？

LLM.int8() 方法的主要目的是让大模型在不损失性能的前提下更易获取。但如果非常慢，这个方法的价值就大打折扣。所以我们测评了多个模型生成速度。我们发现 BLOOM-176B 用 LLM.int8() 比 fp16 版本慢约 15% 到 23%——这仍然相当可以接受。较小的模型（如 T5-3B 和 T5-11B）减速更明显。我们努力提速这些小模型，一天之内就把 T5-3B 的每 token 推理时间从 312 毫秒降到 173 毫秒，T5-11B 从 45 毫秒降到 25 毫秒。此外，问题[已经被指出](https://github.com/TimDettmers/bitsandbytes/issues/6#issuecomment-1211345635)，在后续版本中 LLM.int8() 对小模型还会更快。目前的数字见下表。

| 精度 | 参数量 | 硬件 | Batch Size 1 每 token 耗时（毫秒） | Batch Size 8 每 token 耗时（毫秒） | Batch Size 32 每 token 耗时（毫秒） |
| --- | --- | --- | --- | --- | --- |
| bf16 | 176B | 8xA100 80GB | 239 | 32 | 9.9 |
| int8 | 176B | 4xA100 80GB | 282 | 37.5 | 10.2 |
| bf16 | 176B | 14xA100 40GB | 285 | 36.5 | 10.4 |
| int8 | 176B | 5xA100 40GB | 367 | 46.4 | oom |
| fp16 | 11B | 2xT4 15GB | 11.7 | 1.7 | 0.5 |
| int8 | 11B | 1xT4 15GB | 43.5 | 5.3 | 1.3 |
| fp32 | 3B | 2xT4 15GB | 45 | 7.2 | 3.1 |
| int8 | 3B | 1xT4 15GB | 312 | 39.1 | 10.2 |

三个模型分别是 BLOOM-176B、T5-11B 和 T5-3B。

### Hugging Face `transformers` 集成的细微之处

接下来讨论 Hugging Face `transformers` 集成的具体细节，看看用法，以及搭环境时常见的那些坑。

### 用法

实现本文所述全部魔法的模块叫 `Linear8bitLt`，可以从 `bitsandbytes` 库轻松导入。它派生自经典的 `torch.nn` Module，可以用下面的代码轻松在你的架构里使用和部署。

这里是一个分步示例，场景是：用 `bitsandbytes` 把一个小模型转成 int8。

- 首先要有下面这些正确的 import！

```
import torch
import torch.nn as nn

import bitsandbytes as bnb
from bnb.nn import Linear8bitLt
```

- 然后你可以定义自己的模型。注意，任何精度的 checkpoint 或模型都能转成 8-bit（FP16、BF16 或 FP32），但目前模型的输入必须是 FP16，我们的 Int8 模块才能工作。所以这里我们把模型当作 fp16 模型处理。

```
fp16_model = nn.Sequential(
    nn.Linear(64, 64),
    nn.Linear(64, 64)
)
```

- 假设你已经在你最爱的数据集和任务上训练好了模型！现在保存模型：

```
[... train the model ...]
torch.save(fp16_model.state_dict(), "model.pt")
```

- `state_dict` 保存好了，现在定义一个 int8 模型：

```
int8_model = nn.Sequential(
    Linear8bitLt(64, 64, has_fp16_weights=False),
    Linear8bitLt(64, 64, has_fp16_weights=False)
)
```

这里非常重要的是加上 `has_fp16_weights` 标志。默认值为 `True`，用于以 Int8/FP16 混合精度训练。而我们关心的是省内存的推理，所以要用 `has_fp16_weights=False`。

- 现在可以把模型加载成 8-bit 了！

```
int8_model.load_state_dict(torch.load("model.pt"))
int8_model = int8_model.to(0) # Quantization happens here
```

注意，量化步骤发生在第二行——模型被放上 GPU 时。如果你在调用 `.to` 之前打印 `int8_model[0].weight`，得到的是：

```
int8_model[0].weight
Parameter containing:
tensor([[ 0.0031, -0.0438,  0.0494,  ..., -0.0046, -0.0410,  0.0436],
        [-0.1013,  0.0394,  0.0787,  ...,  0.0986,  0.0595,  0.0162],
        [-0.0859, -0.1227, -0.1209,  ...,  0.1158,  0.0186, -0.0530],
        ...,
        [ 0.0804,  0.0725,  0.0638,  ..., -0.0487, -0.0524, -0.1076],
        [-0.0200, -0.0406,  0.0663,  ...,  0.0123,  0.0551, -0.0121],
        [-0.0041,  0.0865, -0.0013,  ..., -0.0427, -0.0764,  0.1189]],
       dtype=torch.float16)
```

而在第二行调用之后再打印，得到：

```
int8_model[0].weight
Parameter containing:
tensor([[   3,  -47,   54,  ...,   -5,  -44,   47],
        [-104,   40,   81,  ...,  101,   61,   17],
        [ -89, -127, -125,  ...,  120,   19,  -55],
        ...,
        [  82,   74,   65,  ...,  -49,  -53, -109],
        [ -21,  -42,   68,  ...,   13,   57,  -12],
        [  -4,   88,   -1,  ...,  -43,  -78,  121]],
        device='cuda:0', dtype=torch.int8, requires_grad=True)
```

权重值如我们在前面量化章节所见的那样被“截断”了，数值分布看起来在 [-127, 127] 之间。你可能还想知道如何取回 FP16 权重，以便在 fp16 下做离群值的 MatMul？可以简单地：

```
(int8_model[0].weight.CB * int8_model[0].weight.SCB) / 127
```

得到：

```
tensor([[ 0.0028, -0.0459,  0.0522,  ..., -0.0049, -0.0428,  0.0462],
        [-0.0960,  0.0391,  0.0782,  ...,  0.0994,  0.0593,  0.0167],
        [-0.0822, -0.1240, -0.1207,  ...,  0.1181,  0.0185, -0.0541],
        ...,
        [ 0.0757,  0.0723,  0.0628,  ..., -0.0482, -0.0516, -0.1072],
        [-0.0194, -0.0410,  0.0657,  ...,  0.0128,  0.0554, -0.0118],
        [-0.0037,  0.0859, -0.0010,  ..., -0.0423, -0.0759,  0.1190]],
       device='cuda:0')
```

这和原始的 FP16 值（往上数两个打印输出！）已经足够接近了。

- 现在你可以放心用模型做推理了，只需确保输入在正确的 GPU 上并且是 FP16：

```
input_ = torch.randn((1, 64), dtype=torch.float16)
hidden_states = int8_model(input_.to(torch.device('cuda', 0)))
```

完整的最小代码见[示例脚本](https://huggingface.co/assets/96_hf_bitsandbytes_integration/example.py)。

顺带提一句，要注意这些模块与 `nn.Linear` 模块有个小区别：它们的参数来自 `bnb.nn.Int8Params` 类而不是 `nn.Parameter` 类。后面你会看到，这给我们的集成之路又添了一道坎！

现在，是时候了解如何把它集成进 `transformers` 库了！

### 有 `accelerate` 就够了

处理超大模型时，`accelerate` 库提供了很多有用的工具。其中 `init_empty_weights` 方法特别有用：任何模型，无论多大，都可以用它作为上下文管理器来初始化，而不为模型权重分配任何内存。

```
import torch.nn as nn
from accelerate import init_empty_weights

with init_empty_weights():
    model = nn.Sequential([nn.Linear(100000, 100000) for _ in range(1000)]) # This will take ~0 RAM!
```

这样初始化的模型会被放到 PyTorch 的 `meta` 设备上——这是一种不分配存储内存、只表示形状和 dtype 的底层机制。是不是很酷？

起初，`.from_pretrained` 函数内部会调用这个函数，并把所有参数覆盖成 `torch.nn.Parameter`。这不符合我们的需求，因为如上所述，我们想在 `Linear8bitLt` 模块里保留 `Int8Params` 类。我们在[这个 PR](https://github.com/huggingface/accelerate/pull/519) 里修好了，把：

```
module._parameters[name] = nn.Parameter(module._parameters[name].to(torch.device("meta")))
```

改成

```
param_cls = type(module._parameters[name])
kwargs = module._parameters[name].__dict__
module._parameters[name] = param_cls(module._parameters[name].to(torch.device("meta")), **kwargs)
```

这个修好之后，我们就能轻松利用这个上下文管理器，用一个自定义函数在不占用内存的情况下把所有 `nn.Linear` 模块替换成 `bnb.nn.Linear8bitLt`！

```
def replace_8bit_linear(model, threshold=6.0, module_to_not_convert="lm_head"):
    for name, module in model.named_children():
        if len(list(module.children())) > 0:
            replace_8bit_linear(module, threshold, module_to_not_convert)

        if isinstance(module, nn.Linear) and name != module_to_not_convert:
            with init_empty_weights():
                model._modules[name] = bnb.nn.Linear8bitLt(
                    module.in_features,
                    module.out_features,
                    module.bias is not None,
                    has_fp16_weights=False,
                    threshold=threshold,
                )
    return model
```

这个函数递归地替换在 `meta` 设备上初始化的模型中所有 `nn.Linear` 层，换成 `Linear8bitLt` 模块。属性 `has_fp16_weights` 必须设为 `False`，才能直接以 `int8` 连同量化统计信息一起加载权重。

我们也对某些模块（这里是 `lm_head`）不做替换，因为希望它们保持原生精度，以获得更精确、更稳定的结果。

但还没完！上面的函数在 `init_empty_weights` 上下文管理器里执行，意味着新模型仍然处于 `meta` 设备上。对于在该上下文管理器下初始化的模型，`accelerate` 会手动加载每个模块的参数并搬运到正确的设备。而在 `bitsandbytes` 里，给 `Linear8bitLt` 模块设置设备是关键一步（好奇的话可以看[这段代码](https://github.com/TimDettmers/bitsandbytes/blob/bd515328d70f344f935075f359c5aefc616878d5/bitsandbytes/nn/modules.py#L94)），正如我们的玩具脚本里看到的。

这里的问题是量化步骤被调用两次时会失败。我们不得不为 `accelerate` 的 `set_module_tensor_to_device` 函数另做一个实现（称为 `set_module_8bit_tensor_to_device`），确保不会重复调用。细节在下面这小节展开！

### 用 `accelerate` 设置设备时要格外小心

这里我们在 `accelerate` 库上做了一次非常微妙的平衡表演！加载模型并放到正确设备之后，有时仍需调用 `set_module_tensor_to_device`，配合 hook 把模型分发到所有设备。这发生在 `accelerate` 的 `dispatch_model` 函数内部，可能涉及多次 `.to` 调用——正是我们要避免的。为此花了两个 Pull Request 才达成目标！最初的 PR [在这里](https://github.com/huggingface/accelerate/pull/539/)提出，弄坏了一些测试，但[这个 PR](https://github.com/huggingface/accelerate/pull/576/) 成功把一切都修好了！

### 总结一下

所以最终的配方是：

- 在 `meta` 设备上用正确的模块初始化模型
- 逐个把参数设置到正确的 GPU 设备上，并确保这个流程不会走两遍！
- 在所有地方把新的关键字参数放到正确位置，再写点漂亮的文档
- 添加非常全面的测试！详见我们的[测试](https://github.com/huggingface/transformers/blob/main/tests/mixed_int8/test_mixed_int8.py)。听起来挺简单，但我们一起经历了很多艰难的调试，很多时候还要上手 CUDA kernel！

话虽如此，这段集成之旅非常好玩：从深入钻研、给不同库做“手术”，到把一切对齐、让整套东西跑起来！

现在来看看如何受益于这个集成、如何在 `transformers` 里成功使用它！

## 在 `transformers` 中使用

### 硬件要求

CPU 不支持 8-bit tensor core。bitsandbytes 只能运行在支持 8-bit tensor core 的硬件上，即 Turing 和 Ampere GPU（RTX 20s、RTX 30s、A40-A100、T4+）。例如，Google Colab 的 GPU 通常是 NVIDIA T4，其最新一代 GPU 支持 8-bit tensor core。我们的 demo 基于 Google Colab，见下面的链接！

### 安装

用下面的命令安装最新版库（确保使用 python>=3.8），然后运行下面的命令试用

```
pip install accelerate
pip install bitsandbytes
pip install git+https://github.com/huggingface/transformers.git
```

### 示例 demo——在 Google Colab 上运行 T5 11b

来看看在 BLOOM-3B 模型上运行 8bit 模型的 Google Colab demo！

这是 T5-11B 的 demo。T5-11B 模型 checkpoint 是 FP32，占用 42GB 内存，Google Colab 装不下。用我们的 8-bit 模块只需要 11GB，轻松放下：

[![Open In Colab: T5-11b demo](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1YORPWx4okIHXnjW7MSAidXN29mPVNT7F?usp=sharing)

或者这个 BLOOM-3B 的 demo：

[![Open In Colab: BLOOM-3b demo](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/huggingface/blog/blob/main/notebooks/HuggingFace_int8_demo.ipynb)

## 改进空间

我们认为，这个方法极大地改善了访问超大模型的途径。在不损失性能的前提下，算力较少的人也能用上原本够不着的模型。我们也发现了若干可以在未来继续改进的方向，让这个方法对大模型更好用！

### 更小的模型推理更快

如[基准测试一节](https://huggingface.co/blog/hf-bitsandbytes-integration#is-it-faster-than-native-models)所示，我们已经把小模型（<=6B 参数）的运行时速度提升了近 2 倍。不过，虽然 BLOOM-176B 这样的大模型推理速度很稳，小模型仍有改进空间。我们已经定位了问题，很可能恢复到与 fp16 相当的性能，甚至还能有些加速。这些改动会在未来几周内合并进来。

### 支持 Kepler GPU（GTX 1080 等）

虽然我们支持近四年的所有 GPU，但一些老 GPU 如 GTX 1080 仍被大量使用。这些 GPU 没有 Int8 tensor core，但确实有 Int8 向量单元（一种“弱化版”tensor core），因此也能体验 Int8 加速。不过，它需要一整套不同的软件栈才能实现快速推理。我们确实计划集成对 Kepler GPU 的支持，让 LLM.int8() 功能触达更多人，但其复杂度决定了这需要一些时间。

### 在 Hub 上保存 8-bit state dict

目前，把 8-bit state dict 推送到 Hub 之后无法直接加载回 8-bit 模型。原因是模型计算出的统计信息（还记得 `weight.CB` 和 `weight.SCB` 吗）当前没有被存储，也没在 state dict 中被考虑，`Linear8bitLt` 模块还不支持这一特性。我们认为，能够保存它并推送到 Hub 会有助于提升可及性。

### CPU 支持

正如本文开头所述，CPU 设备不支持 8-bit core。但我们能不能绕过这一点？在 CPU 上运行这个模块将显著改善可用性和可及性。

### 扩展到其它模态

目前超大模型以语言模型为主。随着这些模型在未来几年变得更普及，把本方法用于超大的视觉、音频和多模态模型将是一个很有意思的方向，能进一步改善可及性。

## 致谢

非常感谢以下各位，他们既帮助提升了本文的可读性，也为 `transformers` 的集成过程做出了贡献（按字母顺序）：JustHeuristic (Yozh)、Michael Benayoun、Stas Bekman、Steven Liu、Sylvain Gugger、Tim Dettmers

我们博客的更多文章

llm

nlp

inference

## 越小越好：Xeon 上高效生成式 AI 体验 Q8-Chat

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/615ad80355a0d1b0f2f15666/fJ0p0s2DmDkw2o8EoNURW.jpeg)

2

2023 年 5 月 16 日

llm

intel

nlp

## 用深度剪枝草稿模型加速 Intel® Core™ Ultra 上的 Qwen3-8B 智能体

- ![](https://huggingface.co/avatars/a09cbec3bcd29b5093ce30b3c47e27f6.svg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1616423186722-5f8907c65d083370c711f284.jpeg)
- ![](https://huggingface.co/avatars/d5adafb8958f422f363d2b1ecde12ba4.svg)
- ![](https://huggingface.co/avatars/06df4ead5a2014480c128103b9862f98.svg)
- +1

25

2025 年 9 月 29 日

### 社区

将图片、音频和视频拖到输入框、粘贴，或

点击这里

上传。

点击或粘贴到这里上传图片

· [注册](https://huggingface.co/join?next=%2Fblog%2Fhf-bitsandbytes-integration)或[登录](https://huggingface.co/login?next=%2Fblog%2Fhf-bitsandbytes-integration)即可评论

点赞

140

- [![](https://huggingface.co/avatars/ee3327ba714e824e0e04d5cd6f950770.svg)](https://huggingface.co/TengWang)
- [![](https://huggingface.co/avatars/f94b783c8f49019ebb0a69f6e3053b77.svg)](https://huggingface.co/jeongah)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1648631057413-noauth.png)](https://huggingface.co/ybelkada)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63ce875d199b36f7552d4f07/bpUrvhXDagzRqZ3vxTcSF.jpeg)](https://huggingface.co/marcsun13)
- [![](https://huggingface.co/avatars/a454cde25975abd09acb20067b447720.svg)](https://huggingface.co/fordacre)
- [![](https://huggingface.co/avatars/269b11f3b48a48e8a5a34a7d85d53bce.svg)](https://huggingface.co/rsarkar1)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63411db18d8089ebaeef5bd3/FWZJOr1Y_ykEvYh5jtZiM.png)](https://huggingface.co/xMaulana)
- [![](https://huggingface.co/avatars/766d0a481868c5fa27afa995c736ba0a.svg)](https://huggingface.co/iam-ajaymeena)
- [![](https://huggingface.co/avatars/307d69eb93691eff608a32f196afa3bf.svg)](https://huggingface.co/ZeliangLee)
- [![](https://huggingface.co/avatars/a89495511e569e4243997087daa7f007.svg)](https://huggingface.co/strategen01)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1678125746875-noauth.png)](https://huggingface.co/tmoroder)
- [![](https://huggingface.co/avatars/ab5961e37a9bc13017afb0d7b2e3c962.svg)](https://huggingface.co/shinoun)
