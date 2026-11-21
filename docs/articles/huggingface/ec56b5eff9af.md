---
vendor: huggingface
title: 180B Parameters, 32GB of RAM: Pushing MoE Inference to the Limit with Transformers
original_title: 
url: https://huggingface.co/blog/moe-expert-streaming
date: 2026-11-18
lang: zh
captured: 2026-11-21
extractor: readability-v1
translator: agent
status: translated
body_sha: 46f18637d16e
---

[ 返回文章](https://huggingface.co/blog)

# 180B 参数，32GB 内存：用 Transformers 把 MoE 推理逼到极限

发布于 2026 年 11 月 18 日

在 GitHub 上更新


14

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/65baa31607366d903890bcf4/6M9WaawnvJ-2h5wSUic1I.jpeg)](https://huggingface.co/badaoui)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)](https://huggingface.co/pcuenq)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6a5dfb8ac450460a466bd07c/huiG-tO1nldQRFCUjXvO5.jpeg)](https://huggingface.co/aisyndicate)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/qz3OXCjrQi0KZZ5OJkEgq.png)](https://huggingface.co/bigmikeq92)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/7sTK8Q_gZRoOz0uaKnVNJ.png)](https://huggingface.co/luke-loan-atlas)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/FZm4zYHMsgadLGM1bIAJq.png)](https://huggingface.co/dboglou)

[![Tarek Ziadé 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/657f3d21f4f72f2c4c51d2ca/EUpt1X9P3BSaLHehRDEd-.png)](https://huggingface.co/tarekziade)

Tarek Ziadé

tarekziade

*把 MoE 专家直接从 SSD 流式读取，token 生成速度与 Strata 相差不到 6%。*

我一直想少用在线模型、在本地跑更大的模型。家里是台双 RTX 4090 的 PC（就叫它 **Orthrus**，希腊神话里的双头犬），工作用一台 32G 统一内存的 MacBook M5。

Orthrus 跑 Windows 11，因为孩子总在打游戏。原本的 Ubuntu 双系统，两块 TB 的盘被游戏占掉大半。

我也是 RMD（rooms moving development，换房间开发）的拥趸：厨房喝一小时咖啡，办公桌坐两小时，再换到沙发。固定台式机箱不适合我。

第一个实验是在 Orthrus 上用 [`llama.app`](https://llama.app/) 跑 [Qwen 3.8 27B](https://huggingface.co/Qwen/Qwen3.8-27B)，再从笔记本通过 [`pi`](https://pi.dev/) 用它。模型写代码，Opus 这类在线模型负责编排，第二块 RTX 跑 FIM 模型，给 Neovim 做补全。

我把这套东西发到社交网络，反馈很强烈：用 [Qwen3.8-Flash-Next](https://huggingface.co/Qwen/Qwen3.8-Flash-Next) 配 [Strata](https://github.com/niko1221/strata)。

## 什么是 Strata？

Strata 是面向 Qwen 这类 MoE 模型的推理引擎。只有热专家留在 VRAM，其余放到 RAM 甚至磁盘。专家占 MoE 权重的 90% 以上，所以这个 180B 模型也能跑在显存小得多的 GPU 上，比如我的 RTX 4090！

笔记本上同样可行：[这篇博文](https://modelfit.io/blog/strata-qwen38-flash-next-mac/)做的就是这件事——Qwen3.8-Flash-Next 在 32 GB Mac M4 上比 [llama.cpp](https://github.com/ggml-org/llama.cpp) 更快，13.5 tok/s。

按我使用编码 agent 的方式，这太慢了，但确实值得一挠。一批 MoE 模型装不进 MacBook 的统一内存，本可以跑到不错的速度。

## 其他引擎是怎么卸载的？

决定用 Strata 之前，我先看 MoE 模型装不下时 llama.cpp、[vLLM](https://github.com/vllm-project/vllm) 和 [Transformers](https://github.com/huggingface/transformers) 怎么做。三点最关键：专家放在哪、matmul 在哪算、每个 token 搬什么。

**llama.cpp** 用 `mmap` 映射 GGUF，可把专家留在 CPU 上（`--cpu-moe`、`--n-cpu-moe N`、`-ot "exps=CPU"`，或用 `--fit on` 让它自己挑），并且就在 CPU 上*计算*：跨 PCIe 的只有激活值，权重从不过线。装得进 RAM 时很好用；装不下，page cache 就会抖动。GPU 专家缓存（`--moe-cache-mib`）刚落地，但会把计算图切碎（每个 token 的 split 从 2 个变成 50 个），即使全装得下也损失约 10%。

**vLLM** 的 `--cpu-offload-gb N` 把 N GB 权重放进 pinned RAM，kernel 经 PCIe 就地读。MoE 层里只有被路由到的专家，且无缓存：热专家每个 token 都要再过一次 PCIe，也没有磁盘层。默认卸载还包含 dense 层，每个 token 都读；`--cpu-offload-params experts` 可收窄到专家。这契合 vLLM 的大 batch：大批次几乎碰到每个专家，一个用户一块 GPU 就不合适。

**Transformers** 通过 [Accelerate](https://github.com/huggingface/accelerate)（`device_map="auto"`、`offload_folder`）卸载，一次一个*模块*：hook 在 `forward` 前把权重复制到 GPU。MoE 的这个模块是一层整个专家库，于是每个 token 都要复制每个被卸载层的所有专家，只用其中 8 个或 10 个。没有缓存，也没有路由的概念。Mac 上 CPU 与 GPU 共用内存，「卸载到 CPU」并不释放空间。

我在一块 A10G（24 GB）、RAM 充足，用 [Qwen3.6-35B-A3B](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) 跑遍这些引擎；Harry Mellor 又用更好的参数重跑了 vLLM：

| 引擎 | 解码（tok/s） |
| --- | --- |
| Strata，Q8_0 | 82 - 88 |
| llama.cpp，Q8_0，`--fit on` | 63 - 64 |
| llama.cpp，BF16，`--fit on` | 35 - 36 |
| vLLM，FP8，`--cpu-offload-gb 16 --cpu-offload-params experts` | 20.1 |
| vLLM，FP8，同参数，`--enforce-eager` | 14.7 |
| vLLM，FP8，`--cpu-offload-gb 16` | 9.7 |
| vLLM，BF16，`--cpu-offload-gb 50 --cpu-offload-params experts` | 7.3 |
| vLLM，BF16，`--cpu-offload-gb 50` | 3.3 |
| Transformers + Accelerate | 0.16 |

只卸载专家，vLLM 速度翻倍，再叠 FP8 更好（每个专家字节数减半，更多模型进 GPU）。vLLM 另一个卸载后端提前成组复制层，跑下来不到 1 tok/s。

专家装得进 RAM，llama.cpp 很难被击败。装不进，只能流式读取 router 选中的部分，过一层有界缓存，快到瓶颈落在 SSD 而非 Python，最好还能复用模型自带的快速专家 kernel。这正是 32 GB Mac 上跑 Qwen3.8-Flash-Next 要解决的问题，Transformers 开箱做不到。

## 用 Transformers 让 Qwen3.8-Flash-Next 跑在我的 32 GB Mac 上

Strata 在笔记本上对我已经太慢，Transformers 短期也超不过它。但 Accelerate 那条路差得太远，我干脆动手修 Transformers 的卸载机制，目标就是笔记本上这个大模型，心里清楚它大概还是慢到不合我的用法。

代码全是 AI 写的：Transformers 的 PR、模型专用包、Metal kernel。我只负责决定试什么、读 profile、判断留什么。全部在一个 Space 里：[tarekziade/moe-expert-streaming](https://huggingface.co/spaces/tarekziade/moe-expert-streaming)。

### 从小处开始

我从 [OLMoE-1B-7B](https://huggingface.co/allenai/OLMoE-1B-7B-0924) 起步，它能完全装进内存，这样就能拿每个 token 与原生 Transformers 对比。

第一版：专家放磁盘，设备上放 LRU 缓存，Python 循环一次跑一个。全部缓存后跑到 10.1 tok/s，原生约 32。I/O 没问题，问题在循环：原生用 `grouped_mm`，一个 kernel 跑完一层所有专家。

解决办法、也是项目的核心思路，是把缓存变成**槽位池（slot pool）**：一块所有层共享的预分配设备张量，加每层一张 expert id 到槽位的表。把 router 的 expert id 重映射到槽位，池子看起来就跟普通专家库一样，`grouped_mm` 能原样运行，不必自己写专家 matmul。这一步推到 34.6 tok/s，原生 38.1。

### `experts_offload`

随后我把独立加载器做成 `from_pretrained` 的一个选项，提交在 [huggingface/transformers#50717](https://github.com/huggingface/transformers/pull/50717)。试的话从那个 PR 安装：

```
pip install "git+https://github.com/huggingface/transformers.git@refs/pull/50717/head"
```

再把目标从 OLMoE 换成真正的对象 Qwen3.8-Flash-Next：

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

[那个仓库](https://huggingface.co/tarekziade/Qwen3.8-Flash-Next-expert-streaming) 存放项目[转换脚本](https://github.com/tarekziade/moe-expert-streaming#readme)的产物：dense 权重、量化到 3 bit 的专家，以及 n-gram 表。

映射到 `"disk"` 的专家走流式路径而非 Accelerate 卸载：加载器跳过它们的张量，MoE 层切到卸载实现。未命中由 8 个 I/O 线程读取，每个专家一次连续读。接下来两层的 router 会基于当前 hidden state 提前跑，猜该预取哪些专家。专家可离线量化，让读取更小。机制适用于标准专家布局的 MoE 模型。

这个 API 还在和 Transformers 维护者讨论。`device_map` 的写法就是讨论的结果；量化专家之后大概率走 [#50245](https://github.com/huggingface/transformers/pull/50245) 的逐层量化方案，而不是单独开选项。

### 在一台 32 GB 的 Mac 上跑 121 GB 专家

Qwen3.8-Flash-Next 有 48 层、每层 512 个专家（激活 10 个），FP8 下共 121 GB。光流式读还不够：还有一张 51 GB 的 n-gram embedding 表要单独走磁盘。所以：

- 专家量化到 3 bit：磁盘上 49 GB，设备上缓存 12 GiB
- dense 层用 8 bit（约 5.4 GB，相比 BF16 困惑度 +0.2%）
- n-gram 表留在磁盘，用到哪行读哪行

转换约需 5 小时。加载后占约 18 GiB，6K prompt 峰值 25.4 GiB。这差不多是极限：我得关掉浏览器，否则 macOS 开始 swap。

模型专用部分（n-gram 表、Metal kernel）放在小包 [moe-expert-streaming](https://github.com/tarekziade/moe-expert-streaming) 里，叠在那个 PR 之上。第一版约 10 tok/s。

然后我在同一台 M5 上装了 Strata，用同样的 prompt：

|  | Transformers | Strata | 差距 |
| --- | --- | --- | --- |
| 解码，200 token | 10.0 tok/s | 14.8 | 1.5x |
| Prefill，4K prompt | 68 tok/s | 220 | 3.2x |
| 解码，6K 文档之后 | 7.3 tok/s | 13.7 | 1.9x |

Strata 0.1.60 用 IQ3_XXS 专家。两边都跑 greedy，关掉 thinking、MTP 和投机草稿，prefill 块 1,024 token。完整配置与原始结果在 Space 的[详情页](https://tarekziade-moe-expert-streaming.static.hf.space/details.html)。

我还试了 [vllm-metal](https://github.com/vllm-project/vllm-metal)，即通过 MLX 在 Apple GPU 上跑 vLLM，最近刚支持专家卸载。它同样从小型有界缓存流式读取被路由的专家，思路一致。但它在 32 GB 上跑不了 Qwen3.8-Flash-Next：只有专家被流式化，n-gram 表仍在内存，光 Hub 上 MLX checkpoint 里这部分就占 32 GB，还没算约 5 GB 的 dense 层和专家缓存。

## 缩小差距

大部分时间并不是花在专家上。起作用的是这些：

- **尽早提交 GPU 工作。** MPS 上的 [PyTorch](https://github.com/pytorch/pytorch) 会把小 kernel 攒到下次 sync 才发，Python 干活时 GPU 空转。每算完一个 block 就强制 commit，提升 10%。这本来就该在 PyTorch 里修掉。
- 给 macOS 上没有快速路径的部分写 **Metal kernel**：Gated DeltaNet 和 hyper-connections。
- **换用 Strata 自己的权重。** 我切到 [Strata 的 GGUF 权重](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF)，每个 token 的 dense 权重流量从 5.4 GB 降到 3.9 GB，单个专家从 2.15 MB 降到 1.75 MB，并按专家大小各配缓存池。
- **Prefill** 从 68 提到约 228 tok/s，靠更大的块，以及在算当前层时读下一层的专家。
- **长文档**：attention 只算 indexer 选中的 block，KV cache 原地增长，而不是每个 token 复制一次。
- **未命中**：Strata 不藏它，它和我一样等，也没什么策略明显强过 LRU。有用的是每层多读一个猜出来的专家，反正这时 SSD 本来闲着。

下面是一个 token 经过一个 MoE 层时现在的样子：

[![一层一个 token：router 从 512 个专家里选出 10 个。其中 8 个已在专家缓存中，2 个正从 SSD 读入空闲的缓存槽位。随后专家从缓存槽位在 GPU 上执行，同时 SSD 为下一层读取一个猜测的专家，该专家只有被用到才会进入缓存。](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/moe-expert-streaming/expert-streaming.svg)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/moe-expert-streaming/expert-streaming.svg)

这些是做完上述优化后，在同一台 M5、同样 prompt 下的最终结果：

|  | Transformers | Strata | 差距 |
| --- | --- | --- | --- |
| 解码，200 token | 13.9 tok/s | 14.8 | 1.06x |
| Prefill，4K prompt | 228 tok/s | 220 | 1.0x |
| 解码，6K 文档之后 | 12.4 tok/s | 13.7 | 1.1x |

短解码上落后 Strata 约 6%，prefill 略快，全程都在 Transformers 里。

剩下的开销主要是 host 往返，每 token 约 10 ms。sync 后唤醒只占约 1 ms，其余是 GPU 空等 Python 排下一层。Strata 一次排好整个 token 的活儿，GPU 每层等一个 Metal shared event，host 同时读专家。PyTorch 没暴露这个。我试过用小 kernel 空转等 CPU 写的标志位来伪造，GPU 有时一秒后才看到写入，有时永远看不到。真正的解法是在 PyTorch 的 MPS 流上加原生 op，但有挂死风险，我没做。

## 结论

它跑到约 14 tok/s，接近 Strata，但按我使用编码 agent 的方式仍然太慢。真正干活的还是 Orthrus。

Transformers 没能击败 Strata。要追掉最后约 6%，得在栈上做更深的改动，首先是对逐层 sync 的控制权，PyTorch 目前不给。有意思的是它怎么追得这么近：只流式读取被路由的专家，一个有界缓存让 `grouped_mm` 原样运行，再加几个针对性的 Metal kernel。项目里没有 C++ 扩展：只有 Python、用 `torch.mps.compile_shader` 运行时编译的 Metal kernel，以及预编译的[来自 Hub 的 kernel](https://huggingface.co/kernels-community)。为实验写的 Metal kernel 都已[发布到 Hub](https://tarekziade-moe-expert-streaming.static.hf.space/details.html#published-kernels)，项目直接从那里加载。

不过击败 Strata 从不是唯一目标。做这件事是从系统视角理解 MoE 与 LLM 的好办法：路由到底多稀疏、专家缓存能换来多少、每个 token 的内存带宽花在哪、host 与 GPU 互相等待占多少时间。Transformers 让这些都能一个个模块地随手试探。

通用的专家流式实现位于 [huggingface/transformers#50717](https://github.com/huggingface/transformers/pull/50717)，基准测试在 [Space](https://huggingface.co/spaces/tarekziade/moe-expert-streaming)。欢迎对方法和 API 提意见。

感谢 Pedro、Lysandre 与 Arthur 的反馈，也感谢 Harry 帮忙测 vLLM。

最后，感谢 Niko Veit 带来 [Strata](https://github.com/niko1221/strata)。Strata 树立了消费级硬件上专家流式推理的标杆，有这些数字可追，这项工作才走到这一步。

## 本文提到的模型 6

## 本文提到的 Space 1

博客更多文章

transformersmistralvllm

## 欢迎 Le Chonk：Hugging Face 上的 Mistral Large 4

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6141a88b3a0ec78603c9e784/DJsxSmWV39M33JFheLobC.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/60f0608166e5701b80ed3f02/H9LNnlf0W4fiOJhQMxnbW.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6123945a0ed258ebc83f3d56/8wMHFQHEV24G_ljl4kPxQ.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/649a943906690b959319d192/k8ZlmJWF3GNpYLHrdpejY.jpeg)
- +7

91

2026 年 10 月 29 日

open-source-collabllmtransformers

## 欢迎 Beam：一个你可以拥有、定制并扩展的 501B 开放模型

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/62d648291fa3e4e7ae3fa6e8/oatOwf8Xqe5eDbCSuYqCd.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6141a88b3a0ec78603c9e784/DJsxSmWV39M33JFheLobC.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)

82

2026 年 10 月 16 日

### 社区

![](https://cdn-avatars.huggingface.co/v1/production/uploads/6afa05210b2b38354a566ca3/A-j9wYe8kZ1ZEgSrC7ZBv.png)

jdjsjsj28828

1 天前

s7327-owner-blog-comment

把图片、音频和视频拖进输入框、粘贴或点击这里即可上传。

点击或粘贴此处上传图片

· [注册](https://huggingface.co/join?next=%2Fblog%2Fmoe-expert-streaming) 或 [登录](https://huggingface.co/login?next=%2Fblog%2Fmoe-expert-streaming) 后发表评论


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

## 本文提到的模型 6

## 本文提到的 Space 1
