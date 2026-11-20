---
vendor: huggingface
title: 180B Parameters, 32GB of RAM: Pushing MoE Inference to the Limit with Transformers
original_title: 
url: https://huggingface.co/blog/moe-expert-streaming
date: 2026-11-18
lang: zh
captured: 2026-11-20
extractor: readability-v1
translator: mt
status: translated
body_sha: c8683b37374e
---

[ 返回文章](https://huggingface.co/blog)

# 180B 参数，32GB RAM：利用 Transformers 将 MoE 推理推向极限

发表于 2026 年 11 月 18 日

GitHub 上更新

14

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/65baa31607366d903890bcf4/6M9WaawnvJ-2h5wSUic1I.jpeg)](https://huggingface.co/badaoui)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)](https://huggingface.co/pcuenq)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6a5dfb8ac450460a466bd07c/huiG-tO1nldQRFCUjXvO5.jpeg)](https://huggingface.co/aisyndicate)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/qz3OXCjrQi0KZZ5OJkEgq.png)](https://huggingface.co/bigmikeq92)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/7sTK8Q_gZRoOz0uaKnVNJ.png)](https://huggingface.co/luke-loan-atlas)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/FZm4zYHMsgadLGM1bIAJq.png)](https://huggingface.co/dboglou)

[![塔里克·齐亚德的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/657f3d21f4f72f2c4c51d2ca/EUpt1X9P3BSaLHehRDEd-.png)](https://huggingface.co/tarekziade)

塔里克·齐亚德

塔雷克齐亚德

*直接来自 SSD 的流媒体 MoE 专家在代币生成方面与 Strata 的差距在 6% 以内。*

我一直在尝试减少对在线模型的依赖，并在本地运行更大的模型。家里我有一台配有两台 RTX 4090 的 PC（我们称之为 **Orthrus** - 希腊神话中的双头猎犬），工作时我有一台配备 32G 统一内存的 MacBook M5。

Orthrus 在 Windows 11 上运行，因为我的孩子一直在玩游戏。我使用 Ubuntu 进行双启动，但他们的游戏最终占用了 2 TB 磁盘的大部分。

我也是 RMD（房间移动开发）的忠实粉丝：在厨房喝咖啡一小时，在办公桌前呆两个小时，然后在沙发上。固定的台式塔不适合我。

我的第一个实验是在 Orthrus 上运行 [Qwen 3.8 27B](https://huggingface.co/Qwen/Qwen3.8-27B) 和 [`llama.app`](https://llama.app/)，并通过 [`pi`](https://pi.dev/) 从我的笔记本电脑使用它。该模型执行编码任务，Opus 等在线模型负责编排，第二个 RTX 运行 FIM 模型以在 Neovim 中自动完成。

当我在社交网络上谈论这个问题时，我得到了非常强烈的反馈：将 [Strata](https://github.com/niko1221/strata) 与 [Qwen3.8-Flash-Next](https://huggingface.co/Qwen/Qwen3.8-Flash-Next) 一起使用。

## 什么是分层？

Strata 是 Qwen 等 MoE 模型的推理引擎。只有热门专家保留在 VRAM 中，其余的进入 RAM，甚至磁盘。专家占 MoE 模型权重的 90% 以上，因此像这样的 180B 模型可以在内存少得多的 GPU 上运行。就像我的 RTX 4090！

它也适用于笔记本电脑，我偶然发现 [这篇博文](https://modelfit.io/blog/strata-qwen38-flash-next-mac/) 正是这样做的：Qwen3.8-Flash-Next 在 32 GB Mac M4 上，比 [llama.cpp](https://github.com/ggml-org/llama.cpp) 更快，速度为 13.5 tok/s。

对于我使用编码代理的方式来说，这太慢了，但这是一个有趣的渴望。所有 MoE 型号都不适合 MacBook 的统一内存，并且可以以不错的速度运行。

## 其他引擎如何卸载？

在致力于 Strata 之前，我研究了当 MoE 模型不适合时 llama.cpp、[vLLM](https://github.com/vllm-project/vllm) 和 [Transformers](https://github.com/huggingface/transformers) 会做什么。三个问题很重要：专家住在哪里，专家 matmul 在哪里运行，以及每个代币发生了什么变化？

**llama.cpp** 将 GGUF 文件与 `mmap` 进行映射，并且可以将专家保留在 CPU 上（`--cpu-moe`、`--n-cpu-moe N`、`-ot "exps=CPU"` 或 `--fit on` 供您选择）。这些专家也在 CPU 上“计算”，因此只有跨 PCIe 的激活，而不是权重。当专家适合 RAM 时就很好了。如果不这样做，页面缓存就会崩溃。 GPU 专家缓存 (`--moe-cache-mib`) 刚刚落地，但它使图表碎片化（每个令牌 2 个分割变成 50 个），即使一切都合适，也会损失约 10%。

**vLLM** 的 `--cpu-offload-gb N` 将 N GB 权重放入固定 RAM 中，内核通过 PCIe 读取它们。对于 MoE 层，这只是路由的专家，但不会缓存任何内容：热门专家在每个令牌上再次跨越 PCIe，并且没有磁盘层。默认情况下，卸载的权重包括密集层，读取每个令牌； `--cpu-offload-params experts` 将其保留给专家。这适合 vLLM 的大批量，无论如何，它几乎涉及每一位专家，更不用说一个用户使用一个 GPU。

**Transformers** 通过 [Accelerate](https://github.com/huggingface/accelerate)（`device_map="auto"`、`offload_folder`）卸载，一次一个*模块*：钩子在 `forward` 之前将其权重复制到 GPU。对于 MoE 来说，该模块是一层的整个专家库，因此每个代币都会复制每个卸载层的每个专家以使用其中的 8 个或 10 个专家。没有缓存，没有路由的概念。在 Mac 上，CPU 和 GPU 共享相同的内存，因此“卸载到 CPU”不会释放任何内容。

我在一台具有充足 RAM 的 A10G (24 GB) 上的 [Qwen3.6-35B-A3B](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) 上运行了所有这些程序，Harry Mellor 则使用更好的标志重新运行了 vLLM：

|发动机|解码（tok/s）|
| --- | --- |
|地层，Q8_0 | 82 - 88 | 82 - 88
| llama.cpp，Q8_0，`--fit on` | 63 - 64 | 63 - 64
| llama.cpp、BF16、`--fit on` | 35 - 36 | 35 - 36
| vLLM、FP8、`--cpu-offload-gb 16 --cpu-offload-params experts` | 20.1 | 20.1
| vLLM，FP8，相同的标志，`--enforce-eager` | 14.7 | 14.7
| vLLM、FP8、`--cpu-offload-gb 16` | 9.7 | 9.7
| vLLM，BF16，`--cpu-offload-gb 50 --cpu-offload-params experts` | 7.3 | 7.3
| vLLM，BF16，`--cpu-offload-gb 50` | 3.3 |
|变形金刚+加速| 0.16 | 0.16

仅卸载专家可以使 vLLM 的速度加倍，而 FP8 可以提供帮助（每个专家一半的字节，GPU 上的模型更多）。 vLLM 的另一个卸载后端会提前复制层组，运行速度低于 1 tok/s。

如果专家能够适应 RAM，那么 llama.cpp 就很难被击败。如果没有，您必须通过有界缓存仅传输路由器选择的内容，速度足够快，以至于 SSD 成为瓶颈，而不是 Python，理想情况下重用模型的快速专家内核。这是 32 GB Mac 上的 Qwen3.8-Flash-Next，而 Transformers 无法开箱即用。

## 使用 Transformers 让 Qwen3.8-Flash-Next 在我的 32 GB Mac 上运行

Strata 在笔记本电脑上对我来说已经太慢了，变形金刚不会很快打败它。但加速路径还很遥远，我想尝试修复变形金刚本身的卸载问题，以笔记本电脑上的大型模型为目标，因为我知道它对于我的工作方式来说可能会太慢。

所有代码都是用 AI 构建的：Transformers PR、特定于模型的包和 Metal 内核。我的职责是选择尝试什么、阅读资料并决定保留什么。一切都在一个空间中：[tarekziade/moe-expert-streaming](https://huggingface.co/spaces/tarekziade/moe-expert-streaming)。

###从小事做起

我从 [OLMoE-1B-7B](https://huggingface.co/allenai/OLMoE-1B-7B-0924) 开始，它适合内存，因此我可以将每个标记与普通变形金刚进行比较。

第一个版本：磁盘上的专家、设备上的 LRU 缓存以及一次运行一个专家的 Python 循环。每个专家都已缓存，它的速度为 10.1 tok/s。香草做了〜32。 I/O 很好，我的循环则不然：vanilla 使用 `grouped_mm`，它在一个内核中运行一层的所有专家。

该修复以及该项目的关键思想是将缓存转变为**槽池**：一个由所有层共享的预分配设备张量，以及从专家 ID 到槽的每层表。将路由器的专家 ID 重新映射到插槽，池看起来就像一个常规的专家库，因此 `grouped_mm` 按原样在其上运行。无需定制专家 matmul。这使其达到 34.6 tok/s，而普通版本为 38.1 tok/s。

### `experts_offload`

然后我将独立加载程序变成了 `from_pretrained` 的一个选项，在 [huggingface/transformers#50717](https://github.com/huggingface/transformers/pull/50717) 中。要尝试它，请从该 PR 安装 Transformers：
```
pip install "git+https://github.com/huggingface/transformers.git@refs/pull/50717/head"
```
然后，从 OLMoE 转向真正的目标 Qwen3.8-Flash-Next：
```
path = snapshot_download("tarekziade/Qwen3.8-Flash-Next-expert-streaming")

model = AutoModelForCausalLM.from_pretrained(
    f"{path}/dense",
    dtype=torch.bfloat16,
    device_map={"": "mps", "experts.*": "disk"},
    quantization_config=MetalConfig(bits=8),
    experts_offload={
        "cache_bytes": 12 << 30,
        "quantized_experts": f"{path}/experts-q3",
    },
)
```
[该存储库](https://huggingface.co/tarekziade/Qwen3.8-Flash-Next-expert-streaming) 保存项目的[转换脚本](https://github.com/tarekziade/moe-expert-streaming#readme) 的输出：密集权重、量化为 3 位的专家以及 n 元语法表。

映射到 `"disk"` 的专家通过流路径而不是 Accelerate 的卸载：加载器跳过它们的张量，MoE 层切换到卸载的实现。未命中由 8 个 I/O 线程读取，每个专家一次连续读取。接下来两层的路由器会尽早在当前隐藏状态上运行，以猜测要预取哪些专家。专家可以离线量化，因此读取量更小。它适用于具有标准专家布局的 MoE 模型。

该 API 仍在与 Transformers 维护人员讨论。 `device_map` 形式由此而来，量化专家可能会执行 [#50245](https://github.com/huggingface/transformers/pull/50245) 的每层量化计划，而不是他们自己的选择。

### 在 32 GB Mac 上运行 121 GB Expert

Qwen3.8-Flash-Next 有 48 层，共 512 个专家（10 个活动），FP8 中有 121 GB。流式传输它们还不够：还有一个 51 GB n-gram 嵌入表需要自己的磁盘路径。所以：

- 专家量化为 3 位：磁盘上 49 GB，设备上缓存 12 GiB
- 8 位密集层（~5.4 GB，与 BF16 相比 +0.2% 困惑度）
- n-gram 表保留在磁盘上，需要时读取行

转换大约需要 5 小时。加载后，它使用约 18 GiB，6K 提示峰值为 25.4 GiB。这就是限制：我必须关闭浏览器，否则 macOS 就会开始交换。

特定于模型的位（n-gram 表、Metal 内核）位于 PR 顶部的一个小包 [moe-expert-streaming](https://github.com/tarekziade/moe-expert-streaming) 中。第一个版本的运行速度约为 10 tok/s。

然后我在同一个M5上安装了Strata，同样的提示：

|  |变形金刚|地层 |差距|
| --- | --- | --- | --- |
|解码，200 个代币 | 10.0 托克/秒 | 14.8 | 14.8 1.5 倍 |
|预填充，4K 提示 | 68 托克/秒 | 220 | 220 3.2 倍 |
| 6K文档后解码 | 7.3 托克/秒 | 13.7 | 13.7 1.9 倍 |

Strata 0.1.60 使用了 IQ3_XXS 专家。两者都运行贪婪，思考、MTP 和投机草案以及 1,024 个代币预填充块。完整的设置和原始结果位于空间的[详细信息页面](https://tarekziade-moe-expert-streaming.static.hf.space/details.html)。

我还尝试了 [vllm-metal](https://github.com/vllm-project/vllm-metal)，通过 MLX 在 Apple GPU 上进行 vLLM，最近得到了专家的卸载。它通过有界缓存从 MLX 检查点传输路由专家，就像这个项目一样。但由于上述 n-gram 原因，它无法在 32 GB 上运行 Qwen3.8-Flash-Next：仅对专家进行流式传输，并且 n-gram 表保留在内存中。在 Hub 上的 MLX 检查点中，这是 32 GB，在大约 5 GB 的密集层和任何专家缓存之前。

## 缩小差距

大部分时间没有花在专家身上。以下是有帮助的：

- **尽早提交 GPU 工作。** MPS 上的 [PyTorch](https://github.com/pytorch/pytorch) 保留小内核，直到下一次同步，因此 GPU 在 Python 工作时空闲。在每个块之后强制提交会增加 10%。这确实应该在 PyTorch 中修复。
- **金属内核**，适用于 macOS 上没有快速路径的部分：门控 DeltaNet 和超连接。
- **Strata 自己的权重。** 我切换到 [Strata 的 GGUF 权重](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF)，将每个令牌的密集权重流量从 5.4 GB 减少到 3.9 GB，将单个专家大小从 2.15 MB 减少到 1.75 MB，每个专家大小都有一个单独的缓存池。
- **预填充**，我们使用更大的块从 68 tok/s 提高到约 228 tok/s，并在计算当前层时读取下一层的专家。
- **长文档**：仅关注索引器选定的块，以及就地增长而不是在每个令牌处复制的 KV 缓存。
- **未命中**：Strata 不会隐藏它们，它像我一样等待，并且没有缓存策略比 LRU 性能好得多。有用的是每层只读取一位猜测的专家，否则 SSD 就会闲置。

这是一个代币的一个 MoE 层，它现在正在运行：

[！[对于一层和一个令牌，路由器会从 512 个专家中选择 10 个。八个已经在专家缓存中，两个从 SSD 读取到空闲缓存插槽中。然后，专家从缓存槽在 GPU 上运行，而 SSD 为下一层读取一个猜测的专家，该专家仅在使用时才进入缓存。](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/moe-expert-streaming/expert-streaming.svg)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/moe-expert-streaming/expert-streaming.svg)

以下是在相同的 M5 上进行这些优化后的最终结果，并具有相同的提示：

|  |变形金刚|地层 |差距|
| --- | --- | --- | --- |
|解码，200 个代币 | 13.9 托克/秒 | 14.8 | 14.8 1.06 倍 |
|预填充，4K 提示 | 228 托克/秒 | 220 | 220 1.0 倍 |
| 6K文档后解码 | 12.4 托克/秒 | 13.7 | 13.7 1.1 倍 |

在短解码方面，比 Strata 落后约 6%，预填充速度稍快，全部通过 Transformers 实现。

剩下的大部分是主机往返，每个令牌约 10 毫秒。同步后唤醒只需约 1 毫秒。剩下的就是 GPU 空运行，而 Python 则对下一层进行排队。 Strata 将整个代币的工作预先排队，GPU 在每一层等待 Metal 共享事件，同时主机读取专家。 PyTorch 没有公开这一点。我试图用一个内核在 CPU 写入的标志上旋转来伪造它，而 GPU 花了一秒钟才看到写入。真正的解决方案是 PyTorch 的 MPS 流上的本机操作，有挂起的风险，所以我还没有构建它。

## 结论

它的运行速度约为 14 tok/s，接近 Strata，但对于我使用编码代理的方式来说仍然太慢。 Orthrus 一直在做真正的工作。

Transformers 没有击败 Strata，关闭最后约 6% 需要对堆栈进行更深入的更改，首先是对每层同步的控制，而 PyTorch 目前还没有提供这一点。有趣的部分是它是如何做到这一点的：仅流式传输路由专家、`grouped_mm` 按原样运行的有界缓存以及一些目标 Metal 内核。该项目中没有 C++ 扩展：只有 Python、使用 `torch.mps.compile_shader` 在运行时编译的 Metal 内核以及预构建的 [来自 Hub 的内核](https://huggingface.co/kernels-community)。为此实验编写的所有 Metal 内核现已[发布在 Hub 上](https://tarekziade-moe-expert-streaming.static.hf.space/details.html#published-kernels)，项目从那里加载它们。

不过，击败 Strata 从来都不是唯一的目标。构建这个是从系统角度了解 MoE 和 LLM 如何工作的好方法：路由到底有多稀疏、专家缓存能为您带来多少、每个令牌的内存带宽在哪里，以及主机和 GPU 相互等待的时间。 Transformer 让所有这些都变得很容易，一次一个模块。

通用专家流实现位于 [huggingface/transformers#50717](https://github.com/huggingface/transformers/pull/50717) 中，基准测试位于 [Space](https://huggingface.co/spaces/tarekziade/moe-expert-streaming) 中。欢迎对该方法和 API 提供反馈。

感谢 Pedro、Lysandre 和 Arthur 的出色反馈，并感谢 Harry 帮助测试 vLLM。

最后，感谢 Niko Veit 的 [Strata](https://github.com/niko1221/strata)。 Strata 为消费者硬件上的专家流媒体的可能性设定了标准，而追逐这些数字正是推动这项工作取得进展的原因。

## 本文提到的型号 6

## 本文提到的空间1

我们博客的更多文章

变形金刚米斯特拉维姆

## 欢迎 Le Chonk：Hugging Face部的 Mistral Large 4

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6141a88b3a0ec78603c9e784/DJsxSmWV39M33JFheLobC.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/60f0608166e5701b80ed3f02/H9LNnlf0W4fiOJhQMxnbW.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6123945a0ed258ebc83f3d56/8wMHFQHEV24G_ljl4kPxQ.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/649a943906690b959319d192/k8ZlmJWF3GNpYLHrdpejY.jpeg)
- +7

91

2026 年 10 月 29 日

开源 collabllmtransformers

## 欢迎光束：您可以拥有、定制和扩展的 501B 开放模型

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/62d648291fa3e4e7ae3fa6e8/oatOwf8Xqe5eDbCSuYqCd.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6141a88b3a0ec78603c9e784/DJsxSmWV39M33JFheLobC.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)

82

2026 年 10 月 16 日

### 社区

![](https://cdn-avatars.huggingface.co/v1/production/uploads/6afa05210b2b38354a566ca3/A-j9wYe8kZ1ZEgSrC7ZBv.png)

jdjsjsj28828

1 天前

s7327-所有者博客评论

通过拖入文本输入、粘贴或单击此处来上传图像、音频和视频。

点击或粘贴此处上传图像

· [注册](https://huggingface.co/join?next=%2Fblog%2Fmoe-expert-streaming) 或 [登录](https://huggingface.co/login?next=%2Fblog%2Fmoe-expert-streaming) 发表评论

14

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/65baa31607366d903890bcf4/6M9WaawnvJ-2h5wSUic1I.jpeg)](https://huggingface.co/badaoui)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)](https://huggingface.co/pcuenq)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6a5dfb8ac450460a466bd07c/huiG-tO1nldQRFCUjXvO5.jpeg)](https://huggingface.co/aisyndicate)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/qz3OXCjrQi0KZZ5OJkEgq.png)](https://huggingface.co/bigmikeq92)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/7sTK8Q_gZRoOz0uaKnVNJ.png)](https://huggingface.co/luke-loan-atlas)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/FZm4zYHMsgadLGM1bIAJq.png)](https://huggingface.co/dboglou)
- [![](https://huggingface.co/avatars/2fa431d2f7fda60021dae107f3138e90.svg)](https://huggingface.co/syl0390)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/yu32gPCVLqnpeQd_MMZ74.png)](https://huggingface.co/darrowoflykos)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/67e199e97f6b4386bad07cc7/fxCC9xs9m8_Qw2IHl1y2j.jpeg)](https://huggingface.co/AdrianLepers)
- [![](https://huggingface.co/avatars/4dd5862915dc3443a05cd19076cb643f.svg)](https://huggingface.co/zaz2026)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/_t5ifHICcVJNBHoUvJ5VQ.png)](https://huggingface.co/AsTrO963)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64fdfaeb01aedd0e86014de9/UliF1du7InfuCs7RHLiA5.png)](https://huggingface.co/eramax)

## 本文提到的型号 6

## 本文提到的空间1
