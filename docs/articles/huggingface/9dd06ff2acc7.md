---
vendor: huggingface
title: PyTorch 性能分析（第 3 部分）：注意力即是你所分析的一切
original_title: Profiling in PyTorch (Part 3): Attention is all you profile
url: https://huggingface.co/blog/torch-attention-profile
date: 2026-07-06
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: 9a465a3d8c5d
---

[![Thumbnail of the blog post](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/profile-3-thumbnail.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/profile-3-thumbnail.png)

这是《PyTorch 性能分析》系列的第三篇文章。在这个系列中，我们将逐步培养阅读性能分析器追踪信息的技能，并用它指导优化：

- [ PyTorch 性能分析（第 1 部分）：torch.profiler 新手指南 ](https://huggingface.co/blog/torch-profiler)
- [ PyTorch 性能分析（第 2 部分）：从 nn.Linear 到融合的 MLP ](https://huggingface.co/blog/torch-mlp-fusion)
- [ PyTorch 性能分析（第 3 部分）：注意力即是你所分析的一切 ](https://huggingface.co/blog/torch-attention-profile) *（当前）*

《PyTorch 性能分析》系列旨在让你能从容地阅读分析器的追踪信息与表格。在[第 1 部分](https://huggingface.co/blog/torch-profiler)中，我们对加法和乘法这类基础数学运算做了分析，看到了分析表格如何揭示热点、分析追踪如何展示算法随时间的执行顺序。

在[第 2 部分](https://huggingface.co/blog/torch-mlp-fusion)中，我们把加法和乘法封装进 torch 的线性层，然后把若干线性层堆叠起来（一个多层感知器）并对其分析。一路上我们还分析了融合 kernel 和手调 kernel。

从 Transformer 架构的角度看，我们接下来要分析的自然对象是另一个基础算法——注意力。注意力虽以二次时间复杂度"臭名昭著"，但已有许多巧妙的技巧来缓解这一问题、让它变快。这里的目标不是详尽讲解每一个技巧，而是观察每一个在分析器下长什么样。

> 本文脚本位于：04_a_naive_attention.py、04_b_inplace_ops_attention.py、04_c_sdpa_attention.py 和 04_d_kernels_attention.py。像之前一样，边读边另开一个标签页对照代码很有帮助。我们在 NVIDIA A100-SXM4-80GB GPU 上运行脚本。在 Hugging Face 基础设施上开一块 GPU 很容易，可以用 Spaces 的 Dev Mode 实验这些脚本，也可以用 Hugging Face Jobs 管线来跑。

## 朴素注意力

注意力处理查询（`q`）、键（`k`）和值（`v`）。它们之间的交互可以写成短短几步：

- 构建注意力分数 `scores`：`matmul(q, k.T)`
- 缩放分数：`scores * scale`
- 对分数施加因果掩码：`scores.masked_fill(mask, "-inf")`
- 用 softmax 归一化分数得到注意力权重 `attn`：`softmax(scores)`
- 用这些权重对值重新加权：`matmul(attn, v)`

所以注意力其实就是原始运算的集合。有些我们已经认识（那些矩阵乘法），其余的也容易辨认。让我们用 PyTorch 写一个朴素注意力模块并分析它。

```
class NaiveCausalAttention(nn.Module):
    def __init__(self, head_dim):
        super().__init__()
        self.scale = 1.0 / math.sqrt(head_dim)

    def forward(self, q, k, v, mask):
        scores = torch.matmul(q, k.transpose(-2, -1))
        scores = scores * self.scale
        scores = scores.masked_fill(mask, float("-inf"))
        attn = torch.softmax(scores, dim=-1)
        out = torch.matmul(attn, v)
        return out
```

打开追踪之前，照例先做个"猜你会看到什么"的练习。追踪这个模块的 `forward`，我们预期看到：

- 一个 matmul kernel（`q . k.T`）
- 一个 mul kernel（缩放）
- 一个掩码操作
- 一个 softmax kernel
- 一个 matmul kernel（`atten . v`）

```
uv run 04_a_naive_attention.py
uvx trace-util -f traces/ -b <hf_uname>/traces
```

| [![CPU lane of the naive attention profiler trace, with the `attn_fwd` block expanded to show its matmul, mul, masked_fill and softmax operations](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/cpu-profile-naive.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/cpu-profile-naive.png) |
| --- |
| 图 1：朴素注意力分析追踪的 CPU 通道，展开 `attn_fwd` 区块显示其 matmul、mul、masked_fill 和 softmax 操作 |

图 1 展示了分析结果的 CPU 通道（GPU 通道折叠起来以免淹没我们）。在 `attn_fwd`（我们标注的 forward 调用）里，我们恰好看到猜测的那些操作。matmul 如今已是老朋友，新面孔也一眼认出：

- `mul`：缩放
- `masked_fill`：因果掩码
- `softmax`：softmax kernel

现在展开 GPU 通道，看看实际启动了哪些 kernel。

| [![Profiler trace of naive attention showing the CPU lane above the GPU lane, with each `attn_fwd` step mapping to a cluster of GPU kernels](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/gpu-profile-naive.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/gpu-profile-naive.png) |
| --- |
| 图 2：朴素注意力分析追踪的 GPU 与 CPU 通道，每个 `attn_fwd` 步骤对应一簇 GPU kernel。 |

图 2 把 GPU 通道摆在 CPU 通道旁边。我们把 GPU 通道中单个 `attn_fwd` 区块放大，逐个查看 kernel。

| [![Zoomed-in GPU lane of naive attention showing the individual kernels for one step: two matmuls, a mul, a memory copy, a masking kernel and a softmax](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/each-kernels-naive.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/each-kernels-naive.png) |
| --- |
| 图 3：朴素注意力实现的分析追踪 GPU 通道放大图。 |

图 3 让我们读出单个分析步骤的各个 kernel：

- matmul（查询与键）
- mul（缩放）
- 内存拷贝 🤔
- 因果掩码
- softmax（产出注意力权重）
- matmul（注意力权重与值）

其中五个符合预期。内存拷贝是异类，它从何而来？线索是 PyTorch 有原地（in-place）操作。当你以常规（非原地，out-of-place）方式对张量做运算时，PyTorch 常常先做一次拷贝、在拷贝上应用请求的运算、再返回这份拷贝。沿着操作序列看，这里的"嫌疑人"是我们的 [`masked_fill`](https://docs.pytorch.org/docs/2.13/generated/torch.Tensor.masked_fill.html)。

如果我们把它换成原地操作呢？

## 使用原地因果掩码的朴素注意力

我们只把 `masked_fill` 改成 `masked_fill_`（注意结尾的下划线，这是 PyTorch 原地操作的命名约定），然后运行同一个脚本。

```
def forward(self, q, k, v, mask):
    # q, k, v: [batch, heads, seq, head_dim]
    scores = torch.matmul(q, k.transpose(-2, -1))  # [batch, heads, seq, seq]
    scores = torch.mul(scores, self.scale)
-    scores = scores.masked_fill(mask, float("-inf"))
+    scores.masked_fill_(mask, float("-inf"))
    attn = torch.softmax(scores, dim=-1)
    out = torch.matmul(attn, v)  # [batch, heads, seq, head_dim]
    return out
```

看看追踪，观察是否有变化。

```
uv run 04_b_inplace_ops_attention.py
uvx trace-util -f traces/ -b <hf_uname>/traces
```

| 类型 | CPU 流 |
| --- | --- |
| 图 4：朴素掩码 | [![CPU lane of naive attention with out-of-place `masked_fill`, showing several dispatch ops for the masking step](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/cpu-profile-naive.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/cpu-profile-naive.png) |
| 图 5：原地掩码 | [![CPU lane of naive attention with in-place `masked_fill_`, showing fewer dispatch ops for the masking step](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/cpu-profile-inplace.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/cpu-profile-inplace.png) |

原地版本（图 5）在掩码步骤里包裹的 CPU 运算比非原地版本（图 4）少得多，这是个好兆头。展开 GPU 通道确认那边发生了什么。

| 类型 | GPU 流 |
| --- | --- |
| 图 6：朴素掩码 | [![GPU kernels for naive attention including a separate Memcpy kernel before the masking](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/each-kernels-naive.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/each-kernels-naive.png) |
| 图 7：原地掩码 | [![GPU kernels for naive attention with in-place masking, with the Memcpy kernel gone](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/each-kernels-inpace.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/each-kernels-inpace.png) |

在 GPU 通道上，`Memcpy` kernel 彻底消失了（图 6 与图 7）。一行改动，就从每次前向传播削掉一个完整的 kernel。单看似乎不多，但请记住这只是一个注意力操作。在 Transformer 大模型（LLM、扩散模型等）的语境下，它每层都要执行一次，而层数很多，节省会迅速累积（如果因此涨了工资，分我们至少 10% 才合理）。

> 非原地是 PyTorch 的默认，理由充分。要计算梯度，autograd 必须记住前向传播时看到的张量值，因为许多反向公式会复用它们。原地操作会覆盖内存中的这些值，反向传播就会读到错误的数字。由于我们在 torch.no_grad 下只跑前向，原地对我们是安全的——没有反向传播，也没有可被破坏的东西。另外值得注意的是，原地操作不仅省时间（如我们所见），还省内存（因为不需要额外拷贝），这对 logits 这类大张量非常友好！

## 缩放点积注意力（SDPA）

我们刚刚用原始运算搭出了注意力，甚至削掉了 `Memcpy`。好消息是 PyTorch 团队已经替我们把这一切做完，并把整个管线打包成一个函数：

```
from torch.nn import functional as F

F.scaled_dot_product_attention(q, k, v, is_causal=True)
```

这一行替换了我们手写的模块，`is_causal=True` 连手动构建掩码都省了。值得停下来体会这一个调用隐藏了多少东西——它隐藏的不只是几行代码。缩放点积注意力（SDPA）并没有单一实现。它在底层会*派发*到若干后端之一，挑选支持我们输入（dtype、头维度、掩码、硬件等）的最快后端。

[官方 SDPA 教程](https://docs.pytorch.org/tutorials/intermediate/scaled_dot_product_attention_tutorial.html)讲解了这一选择过程，后端本身列在 `torch.nn.attention.SDPBackend` 枚举里：

```
from torch.nn.attention import SDPBackend

BACKENDS = {
    "math": SDPBackend.MATH,
    "flash": SDPBackend.FLASH_ATTENTION,
    "efficient": SDPBackend.EFFICIENT_ATTENTION,
    "cudnn": SDPBackend.CUDNN_ATTENTION,
}
```

通常 SDPA 替我们选择，但我们可以用 `torch.nn.attention.sdpa_kernel` 上下文管理器锁定特定后端。我们的脚本就是这么做的，这样就能逐个分析每个后端，读出它们为何在追踪中长得不一样。我们一个个来。

### Math 后端

```
uv run 04_c_sdpa_attention.py --backend math
uvx trace-util -f traces/ -b <hf_uname>/traces
```

打开任何东西之前先猜猜。我们把手写注意力（matmul、mul、掩码、softmax、matmul）换成了单行调用，所以预期追踪会变*得更简单、更快*：更少的 kernel、更少的 CPU 派发，甚至可能有融合 kernel。先看分析表格。

| 指标 | 去哪里看？ | 朴素原地 | SDPA math |
| --- | --- | --- | --- |
| `*_fwd` CUDA time avg | "CUDA time avg" 列里的 `*_fwd` 运算 | 1.955 ms | 7.239 ms |
| Self CUDA time total | 分析表格底部 | 7.194 ms | 27.279 ms |

这是我们遇到的第一个意外：单行调用反而慢了 `3.7x`。

|  | 分析追踪 |
| --- | --- |
| 图 8：朴素原地注意力分析追踪，一次前向启动五个 GPU kernel | [![GPU lane of naive in-place attention with five kernel launches for one forward pass](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/inplace-kernel-launches.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/inplace-kernel-launches.png) |
| 图 9：SDPA math 后端分析追踪，单次注意力前向启动 20 个 GPU kernel | [![GPU lane of the SDPA math backend with twenty kernel launches for a single attention forward pass](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/math-kernel-launches.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/math-kernel-launches.png) |

打开追踪（图 9）就知道为什么警报大响了：math 后端每次前向启动 `20` 个 GPU kernel，而我们朴素注意力实现只启动 `5` 个（图 8）。这与猜测完全相反。我们来弄清原因。

####  tensor core 被闲置

在[第 2 部分](https://huggingface.co/blog/torch-mlp-fusion#where-did-the-transpose-go-kernel-layouts-and-pre-ops)我们学会了把 kernel 名字当指纹来读，现在就用这个习惯：

| 运行 | matmul kernel |
| --- | --- |
| 图 10：朴素注意力 | [![Matmul kernel name for naive attention in Perfetto, carrying the s16816 bfloat16 Tensor-core GEMM signature](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/tensor-core-kernels.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/tensor-core-kernels.png) |
| 图 11：SDPA math 后端 | [![Matmul kernel name for the SDPA math backend, carrying the sgemm FP32 CUDA-core signature](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/cuda-core-kernels.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/cuda-core-kernels.png) |

我们用来抓追踪的 A100 配有 [Tensor Cores](https://www.nvidia.com/en-us/data-center/tensor-cores/)，一种专门加速矩阵乘法的硬件，远快于普通的 CUDA core。要明白这在这里为何重要，先了解 GPU 内部有什么。流式多处理器（SM）是 GPU 的计算单元，每个 SM 有两种算术单元：CUDA core 和 Tensor core。CUDA core 是通用的，一次处理少量元素；而 Tensor core 用一条指令完成整个小矩阵块的乘加。于是问题很简单："每个后端到底有没有走快路径？"

kernel 名字给出了答案。朴素 kernel（图 10）里的 `s16816` 是一个 `bfloat16` Tensor Core matmul 的签名（`16x8x16` 的 Tensor Core 指令），所以朴素版本走在快路径上。`sgemm`（图 11）是跑在普通 CUDA core 上的经典单精度（`FP32`）矩阵乘法。换句话说，math 后端完全没碰 Tensor core：为了用数值精度换速度，它把张量上转成 `FP32`（即便输入是 `bf16` 也让搬运数据量翻倍），并退回到更慢的 CUDA core。

#### 每次都在重建因果掩码

在朴素版本里，我们只构建一次因果掩码然后复用。这里我们传了 `is_causal=True`，math 后端就*每次*调用都替我们物化一个。你可以在 CPU 通道看着它发生：

| [![CPU lane of the SDPA math backend showing the ops that rebuild the causal mask: aten::ones, aten::tril, aten::scalar_tensor, aten::fill_ and aten::where](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/mask-math.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/mask-math.png) |
| --- |
| 图 12：显示掩码相关运算的 CPU 通道 |

图 12 里我们看到的是

```
aten::ones -> aten::tril            build a [seq, seq] lower-triangular matrix
aten::scalar_tensor -> aten::fill_  make the -inf fill value
aten::where                         turn it into an additive bias (0 or -inf)
```

在 GPU 上，这表现为一个 `triu_tril_kernel`、若干 `where` kernel 和一个 `add_`。让我们不用再操心掩码的便利开关并没有消除工作，只是把活挪到了下一层——每次前向都从零重建掩码。

#### 安全 softmax

我们手写的版本调用普通的 `aten::softmax`。math 后端调用的是 `aten::_safe_softmax`，区别再次体现为额外的 kernel（图 13）：

| [![GPU lane of the SDPA math backend showing the extra kernels that aten::_safe_softmax launches compared to a plain softmax](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/safe-softmax-extra-kernels.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/safe-softmax-extra-kernels.png) |
| --- |
| 图 13：安全 softmax，高亮与普通 softmax 相比多出的 kernel |

一个被完全掩码的行（全为 `-inf`）会让普通 softmax 算出 `exp(-inf)/sum(exp(-inf)) = 0/0 = NaN`。`_safe_softmax` 正是防这一手。我们的朴素 kernel 从不理会这种情况，在这个角落场景会悄悄产出 `NaN`。

#### 那 math 后端有何用？

合起来看，math 后端就是参考实现：把注意力直白、dtype 安全、NaN 安全地拆解成原始 ATen 运算。它本质上就是我们手写的朴素注意力，只是更谨慎。而这份谨慎恰恰让它慢得离谱。

它的职责不是快，而是*永远*能跑。这使它成为完美的基线。我们接下来分析的每个后端（flash、efficient、cudnn）都在设法把 `20` 个 GPU kernel 坍缩成大约一个融合 kernel，全程留在 bf16，并且完全不再物化中间矩阵。

### Efficient 后端

```
uv run 04_c_sdpa_attention.py --backend efficient
uvx trace-util -f traces -b <hf_uname>/traces
```

| [![Profiler trace of the SDPA efficient backend showing a single fused fmha_cutlassF attention kernel per forward](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/efficient-backend.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/efficient-backend.png) |
| --- |
| 图 14：SDPA efficient 后端的分析追踪 |

math 后端在一个分析步骤里启动 20 个 kernel，而 efficient 后端只启动一个 `fmha_cutlassF_bf16_aligned_64x64_rf_sm80`（见图 14）。

我们来解码这个 kernel 名：

- `fmha`（fused multi-head attention，融合多头注意力）：注意力里所有原始运算现在"融合"进了一个运算。
- `cutlassF`：基于 CUTLASS（NVIDIA 开源的 tensor core GEMM 模板），`F` 表示前向。
- `bf16_aligned`：以 bfloat16 运行（不像 math 那样上转到 FP32）。
- `64x64`：分块尺寸。
- `rf`（register file，寄存器堆）：工作集保存在寄存器里——芯片上最快的存储。
- `sm80`：为 Ampere 编译（A100 的计算能力 8.0）。

这就是源自 Meta 的 [xformers](https://github.com/facebookresearch/xformers) 库、后被上游合入 PyTorch 的 memory efficient attention kernel。当人们说"xformers 后端"时，指的就是这个 `fmha_cutlassF` kernel。

### Flash 后端

```
uv run 04_c_sdpa_attention.py --backend flash
uvx trace-util -f traces -b <hf_uname>/traces
```

| [![Profiler trace of the SDPA flash backend](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/flash-backend.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/flash-backend.png) |
| --- |
| 图 15：flash 后端追踪，每次前向一个融合 `pytorch_flash` kernel |

`void pytorch_flash` kernel（图 15）就是被引入 PyTorch 仓库的 [FlashAttention-2](https://arxiv.org/abs/2307.08691)（Tri Dao 的实现）。

在继续读追踪之前，值得回答你此刻应该正在问的问题：*为什么会有一个整个后端叫"flash"，它为何如此重要？*

#### flash attention 为何而生

让我们暂回 math 后端。它真正的问题不在于 20 个 kernel 的数目，而在于这些 kernel 互相传递的内容。

第 1 步构建完整的分数矩阵 `attn = q . k.T`，**每个头**都有 `[seq, seq]`。序列长 4096 时，单个头就是 `4096 x 4096 ≈ 1600 万`个数字。这个矩阵会被写到 HBM（GPU 主存）——前提是还有足够空间的话。然后它又被读回来做缩放、再写一次做掩码、再读一次做 softmax，依此类推。注意力的开销主要被这种**往返 HBM 的流量**支配，而不是矩阵乘法本身。

FlashAttention 直击这一点。它不先算出整个 `s` 矩阵再归约，而是**分块**遍历 `k` 和 `v`，边走边维护一个"在线 softmax"（running softmax），并一块一块地累加输出。完整的 `[seq, seq]` 分数矩阵**从不写入 HBM**，它只存在于片上。就是这个想法让整条注意力管线坍缩成一个融合 kernel，在 Tensor core 上全程保持 bf16。

#### 为什么 flash 在分析器下看起来"不对劲"

| [![Perfetto footprint of the flash kernel reporting an estimated achieved occupancy of 13%](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/flash-occupancy.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/flash-occupancy.png) |
| --- |
| 图 16：flash kernel 的估计占用率显示为 13% |

这里是 flash 让读分析数据的人吃惊的地方。它是最快的后端，但分析器报告它的**占用率（occupancy）很低**（见图 16）。要明白这为什么没关系，需要三个快速定义。

GPU kernel 本质上是由大量小型执行单元执行的一串指令。这些独立的执行单元（线程）负责装载变量、相加、存回等等。对每个 kernel 我们启动海量线程，为了管理它们，我们把线程编组为块（block）。

块被调度到流式多处理器（SM）上——GPU 的主要计算单元。一个块完整地生活在一个 SM 上，而只要*资源足够*，一个 SM 可以同时容纳多个块。这些资源包括寄存器、共享内存、最大常驻线程数和最大常驻 warp 数。所以我们说一个 kernel 的**占用率**低，是指每个 SM 的常驻 warp 少于其理论上限。

> 如果想更多了解线程、块、网格等，这里是一份很好的资源。

如果你在追踪中点击 flash kernel，它的占用情况会讲述故事（图 17）。

| [![Resource footprint of the pytorch_flash kernel in Perfetto, showing a high per-thread register count and large shared memory usage per block](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/flash-reg-count.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/flash-reg-count.png) |
| --- |
| 图 17：flash kernel 的占用情况，每个块的寄存器和共享内存都很"重"。 |

Flash 使用大量线程级寄存器和每块大容量共享内存。例如，若一个块有 128 个线程、每个线程用 255 个寄存器，这个块就需要 `128 × 255 = 32,640` 个寄存器。在拥有 65,536 个寄存器的 Ampere SM 上，一次只能容下两个这样的块。每个 128 线程的块有 `128 / 32 = 4` 个 warp，所以两个块只有 8 个常驻 warp。相对 64 个常驻 warp 的上限，这就是约 13% 的占用率。flash 占用率低并非优化不佳，而是每个块刻意在片上资源使用上非常"重"。

而这正是重点所在。高占用率通过让更多 warp 待命来*隐藏延迟*，但并不能让工作本身高效。Flash 有意把这些寄存器和共享内存花在刀刃上：把注意力数据块留在片上、激进地复用数据，并且从不把完整注意力矩阵物化到全局内存。

### cuDNN 后端

```
uv run 04_c_sdpa_attention.py --backend cudnn
uvx trace-util -f traces -b <hf_uname>/traces
```

| [![Profiler trace of the SDPA cuDNN backend showing a single cudnn_generated attention kernel per forward](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/cudnn-backend.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/cudnn-backend.png) |
| --- |
| 图 18：cuDNN 后端追踪，每次前向一个生成的注意力 kernel。 |

到这里模式已经眼熟了。与 flash 和 efficient 一样，cuDNN 也给了我们每次前向一个融合的 flash 风格 kernel（图 18）。自然的问题是：**既然 flash 已经融合了注意力，为什么 PyTorch 还要提供另一个 flash 后端？**答案在于*谁来写 kernel、如何构建*，而这一差异正让追踪看起来不同。

#### cuDNN 的 kernel 有何不同

flash 和 efficient 是**固定的预编译 kernel**，被引入 PyTorch 仓库。每次拿到的都是同一个二进制。cuDNN 是 NVIDIA 自家的深度学习库，它的注意力 kernel 是**针对手头具体问题生成并调优**的。它在精神上更接近 `torch.compile` 的代码生成，而非固定的 cuBLAS 二进制。你可以直接从（很长的）kernel 名字里读出来：

```
cudnn_generated_fort_native_sdpa_sm80_flash_fprop_wmma_f16_knob_6_128x64x64_4x1x1_cga1x1x1_kernel0_0
```

- `cudnn_generated`：不是预置的二进制，是由 cuDNN 生成的。
- `flash_fprop`：flash 注意力风格的前向传播，算法与 flash 后端同族。
- `wmma_f16`：使用 warp 级矩阵乘加（WMMA）API，即 16-bit 浮点管线上的 Tensor core 路径。
- `knob_6`：cuDNN 从一组预先调优的配置（"knobs"）中挑选。不同的形状选择不同的 knob，就像 cuBLAS 挑选 tile 变体一样。
- `128x64x64`：它选择的分块尺寸。

这一个事实——*按问题生成*——解释了追踪中一切看起来不寻常的地方。

- 没有转置：CPU 通道从 `_cudnn_attention_forward` 直接到几个 `aten::empty` 分配、然后是 kernel，零个 `aten::transpose`（图 19、20、21）。flash 和 efficient 各自插入四次（元数据）转置来重塑张量，而 cuDNN 直接消费原生 `[B, H, S, D]` 布局，因为它的生成器就是为该布局发出 kernel 的。    变体 追踪   图 19：flash [![CPU lane of the flash backend showing four aten::transpose ops before the fused attention kernel](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/flash-transpose.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/flash-transpose.png)   图 20：efficient [![CPU lane of the efficient backend showing four aten::transpose ops before the fused attention kernel](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/efficient-trasnpose.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/efficient-trasnpose.png)   图 21：cuDNN [![CPU lane of the cuDNN backend going straight to aten::empty allocations and the kernel, with no transpose ops](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/cudnn-backend.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/cudnn-backend.png)
- 它通过 `cuLaunchKernelEx` 启动，而非 `cudaLaunchKernel`：本系列里其他所有 kernel 都经过运行时 API `cudaLaunchKernel`。cuDNN 使用驱动级的*扩展*启动方式，携带启动属性（图 22）。    [![CPU lane of the cuDNN backend showing the cuLaunchKernelEx driver-level launch instead of cudaLaunchKernel](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/cudnn-launch.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/cudnn-launch.png)   图 22：cuDNN 后端的 CPU 通道，显示驱动级 cuLaunchKernelEx 启动而非 cudaLaunchKernel
- 分析器报告 0% 的实际占用率：别当真，那是测量缺口，不是 GPU 停摆。CUPTI（分析后端）无法像对 `cudaLaunchKernel` 那样把占用率归属到驱动 API（`cuLaunchKernelEx`）的启动，所以该字段读数为 0。占用情况数据还原了真相（图 23）：`240 寄存器 × 256 线程 = 每个块 61,440` 个寄存器，对比 SM 的 65,536，所以每个 SM 只能容下**一个块**（8 个 warp ≈ 12.5%），与 flash 处于同一水平。    [![Perfetto footprint of the cuDNN kernel reporting 0% achieved occupancy, with 240 registers per thread and 256 threads per block](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/cudnn-footprint.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/torch-attention-profile/cudnn-footprint.png)   图 23：cuDNN kernel 报告 0% 实际占用率，但每线程 240 个寄存器、每块 256 个线程

#### 成本转移到了 CPU

"没有转置"的故事让我们期待 cuDNN 会是 CPU 上最*精简*的后端。恰恰相反。

| 后端 | CUDA 平均耗时 | CPU 平均耗时 |
| --- | --- | --- |
| efficient | 277.9 µs | 117 µs |
| flash | 146.8 µs | 138 µs |
| cudnn | 186.3 µs | **214 µs** |

即便零转置运算，cuDNN 每次前向在 CPU 上仍花约 **214 µs**，比 flash（138）和 efficient（117）都多。几乎全部集中在 `aten::scaled_dot_product_attention` 的 self time（占整个运行的 26%）和 `_cudnn_attention_forward`。这是 cuDNN 的运行时引擎在每次调用时选择并准备执行计划（"knob" 搜索）。

可见的 ATen 运算变少并不意味着 CPU 工作变少——它把活**挪进了库内部**，分析器只能把它显示成一根又粗又黑的方块。当追踪突然变*干净*时，工作并不总是消失了，有时只是搬去了分析器无法细分的地方。

在 GPU 上，cuDNN（186.3 µs）介于 efficient 和 flash 之间。在这个对 flash 极其友好的形状上，手写的 FlashAttention-2 略胜一筹。cuDNN 常常在*其他*形状（更大的头维度、不同的序列长度）上取胜，正因为它的生成器按问题重新调优——但那份调优也正是你刚才在 CPU 上付掉的成本。

## 我们讲过的全部内容，一览

收尾之前，用一张表回顾我们分析过的每一种注意力变体，以及每份追踪教会我们的那一课。

| 变体 | 改了什么 | 每次前向 kernel 数 | 追踪揭示了什么 |
| --- | --- | --- | --- |
| 朴素注意力 | 用原始运算手工搭注意力（matmul、mul、掩码、softmax、matmul） | 6 | 非原地 `masked_fill` 带来一次隐藏的 `Memcpy`。 |
| 朴素原地 | `masked_fill` → `masked_fill_` | 5 | 一行改动彻底去掉 `Memcpy` kernel。 |
| SDPA math | `F.scaled_dot_product_attention` 锁定 math 后端 | 20 | 参考实现：CUDA core 上的 FP32、每次调用重建掩码、`_safe_softmax`。正确但慢约 3.7 倍。 |
| SDPA efficient | efficient（xformers）后端 | 1 | 一个融合 `fmha_cutlassF` kernel，全程 bf16 跑在 Tensor core 上。 |
| SDPA flash | flash 后端 | 1 | 一个融合 `pytorch_flash` kernel（FlashAttention-2）。尽管 13% 的"看起来不对劲"占用率，仍然最快。 |
| SDPA cuDNN | cuDNN 后端 | 1 | 按问题生成的 kernel：没有转置、用 `cuLaunchKernelEx`，但成本转移成一根粗壮的 CPU 黑块。 |

## 系列结语

如果整个系列你只带走一样东西，请带走我们在打开每份追踪之前反复练习的习惯：**先猜，再看。**

大声说出你预期追踪里有什么，然后打开它，把任何不符视为屏幕上最有意思的东西。这三篇文章里每一个真正的洞见——隐藏的 `Memcpy`、`addmm` 尾声、20 个 kernel 的 math 后端、flash 的"看起来不对劲"占用率、cuDNN 粗壮的 CPU 黑块——都来自一次与追踪不符的猜测。

性能分析不是留给 GPU 专家的独立而吓人技能。它只是仔细观察并追问"等等，*那个*为什么会发生？"直到答案浮现的自律。你现在已经具备在自己的模型上做这件事的词汇和条件反射。打开一份追踪、形成一个猜测，去找那个不匹配。

感谢阅读《**PyTorch 性能分析**》系列。现在去分析点什么吧。🤗

感谢 [Noe Flandre](https://huggingface.co/NoeFlandre) 对本文早期草稿的审校！

> 本文使用 LLM 润色过。这绝不意味着我们让智能体在后台自行生成了这篇文章。团队里有些人不是英语母语者，我们认为 LLM（大多以英语训练）可以纠正低级语法错误，或把句子改写得更平和、更干净。希望这能解答"既然 LLM 参与生成，我为什么要读"的疑虑。🤗
