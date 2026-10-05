---
vendor: huggingface
title: 使用 DeepSpeed 和 Accelerate 实现极速 BLOOM 推理
original_title: Incredibly Fast BLOOM Inference with DeepSpeed and Accelerate
url: https://huggingface.co/blog/bloom-inference-pytorch-scripts
date: 2026-07-29
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: e8d98e10ee57
---

# 使用 DeepSpeed 和 Accelerate 实现极速 BLOOM 推理

本文展示如何在使用 1760 亿参数的 [BLOOM 模型](https://huggingface.co/bigscience/bloom)做生成时，获得快得惊人的逐 token 吞吐。

该模型在 bf16（bfloat16）下需要 352GB 权重（`176*2`），最高效的配置是 8×80GB A100 GPU。也可以用 2×8×40GB A100 或 2×8×48GB A6000。选用这些 GPU 的主要原因是：写作本文时它们提供最大的 GPU 显存，但其他 GPU 也能用。例如 24×32GB V100 就可以。

通常单节点能给出最快的吞吐，因为多数情况下节点内 GPU 互联硬件比节点间更快——但并非总是如此。

如果你有不了这么多硬件，依然可以通过 CPU 或 NVMe offload 在更小的 GPU 上跑 BLOOM 推理，当然生成时间会慢得多。

我们还会介绍 [8bit 量化方案](https://huggingface.co/blog/hf-bitsandbytes-integration)，它以略低的吞吐为代价换取一半的 GPU 显存需求，届时会讨论 [BitsAndBytes](https://github.com/TimDettmers/bitsandbytes) 和 [Deepspeed-Inference](https://www.deepspeed.ai/tutorials/inference-tutorial/) 库。

## 基准测试

废话少说，直接上数字。

为保证一致性，除非另有说明，本文所有基准都在 [Jean Zay HPC](http://www.idris.fr/eng/jean-zay/index.html) 上同一个 8×80GB A100 节点（配 512GB CPU 内存）完成。JeanZay HPC 用户享有约 3GB/s 读速的超快 IO（GPFS），这对 checkpoint 加载时间很重要。磁盘慢，加载就慢——尤其因为我们会在多个进程里并发做 IO。

所有基准都是[贪心生成](https://huggingface.co/blog/how-to-generate#greedy-search) 100 个输出 token：

```
Generate args {'max_length': 100, 'do_sample': False}
```

输入 prompt 只有几个 token。前 token 缓存也是开着的，因为每次都重算它们会很慢。

首先看看准备工作化了多长时间——即加载和准备模型用时：

| 项目 | 秒数 |
| --- | --- |
| accelerate | 121 |
| ds-inference shard-int8 | 61 |
| ds-inference shard-fp16 | 60 |
| ds-inference unsharded | 662 |
| ds-zero | 462 |

Deepspeed-Inference 自带预分片（pre-sharded）权重仓库，加载只需约 1 分钟。Accelerate 的加载时间同样出色——约 2 分钟。其他方案在这里慢得多。

加载时间重不重要视情况而定：一旦加载完成，你可以持续不断地生成 token，不再有额外加载开销。

接下来是最重要的基准——token 生成吞吐。这里的吞吐指标很直白：生成 100 个新 token 花了多长时间，除以 100 再除以批次大小（即除以生成 token 总数）。

以下是 8×80GB GPU 上以毫秒计的吞吐：

| 项目 \ bs | 1 | 8 | 16 | 32 | 64 | 128 | 256 | 512 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| accelerate bf16 | 230.38 | 31.78 | 17.84 | 10.89 | oom |  |  |  |
| accelerate int8 | 286.56 | 40.92 | 22.65 | 13.27 | oom |  |  |  |
| ds-inference fp16 | 44.02 | 5.70 | 3.01 | 1.68 | 1.00 | 0.69 | oom |  |
| ds-inference int8 | 89.09 | 11.44 | 5.88 | 3.09 | 1.71 | 1.02 | 0.71 | oom |
| ds-zero bf16 | 283 | 34.88 | oom |  |  |  |  |  |

其中 OOM == Out of Memory，批次太大装不进 GPU 显存。

用 Deepspeed-Inference 的张量并行（TP）和定制融合 CUDA kernel，实现了低于 1ms 的吞吐！太惊人了！不过要把这个方案用在它没试过其他模型上，可能需要一些开发时间才能跑通。

Accelerate 也超级快。它用的是非常简单的朴素流水线并行（PP）方案：正因为简单，它应该能在任何模型上开箱即用。

由于 Deepspeed-ZeRO 可以并行处理多条生成流，它的吞吐还可以进一步除以 8 或 16，取决于 `generate` 调用时用了 8 还是 16 块 GPU。当然，这意味着它（在上表的 8×80 A100 配置下）能处理 64 的批次大小，于是吞吐约为 4ms——三个方案其实非常接近。

再回顾一下这些数字是怎么算出来的。用 Deepspeed-Inference fp16 模式对批次大小 128 生成 100 个新 token，实际耗时 8832ms。于是吞吐计算为：墙钟时间/(batch_size*new_tokens)，即 `8832/(128*100) = 0.69`。

现在看看 Deepspeed-Inference 和 BitsAndBytes 提供的量化 int8 模型的实力——它们只需 bfloat16 或 float16 推理原始 GPU 显存的一半。

以毫秒计的吞吐，4×80GB A100：

| 项目 bs | 1 | 8 | 16 | 32 | 64 | 128 |
| --- | --- | --- | --- | --- | --- | --- |
| accelerate int8 | 284.15 | 40.14 | 21.97 | oom |  |  |
| ds-inference int8 | 156.51 | 20.11 | 10.38 | 5.50 | 2.96 | oom |

要复现这些基准结果，只需在下面讨论的 3 个脚本后面加 `--benchmark`。

## 方案

先检出 demo 仓库：

```
git clone https://github.com/huggingface/transformers-bloom-inference
cd transformers-bloom-inference
```

本文将使用 `bloom-inference-scripts/` 下的 3 个脚本。

各框架的方案按字母顺序介绍：

## HuggingFace Accelerate

[Accelerate](https://github.com/huggingface/accelerate)

Accelerate 以如下方式处理大模型推理：

- 以空权重实例化模型。
- 分析每一层的大小以及每个设备（GPU、CPU）的可用空间，决定每层放在哪里。
- 逐块加载模型 checkpoint，把每个权重放到它的设备上。

随后，它通过 hooks 保证模型正常运行：在正确的设备间搬运输入输出，并在前向传播即将开始前，把之前 offload 到 CPU（甚至磁盘）的权重加载回 GPU，前向传播一结束再 offload 回去。

在多块 GPU 且总空间足以容纳整个模型的情况下，控制权从一块 GPU 切换到下一块，直到所有层跑完。任一时刻只有一块 GPU 在工作——听起来效率很低，但尽管其他 GPU 在闲置，它确实能产出不错的吞吐。

它也非常灵活，因为同一份代码可以在任何配置上运行。Accelerate 会先用尽所有可用 GPU，然后在 RAM 装满前 offload 到 CPU，最后落到磁盘。offload 到 CPU 或磁盘会变慢。例如有用户报告，在仅 2 块 A100 上不改代码运行 BLOOM，吞吐为每 token 15 秒，而 8×80 A100 上是每 token 10 毫秒。

可在 [Accelerate 文档](https://huggingface.co/docs/accelerate/big_modeling)了解该方案的更多细节。

### 安装

```
pip install transformers>=4.21.3 accelerate>=0.12.0
```

### 运行

简单执行方式是：

```
python bloom-inference-scripts/bloom-accelerate-inference.py --name bigscience/bloom --batch_size 1 --benchmark
```

要启用 [BitsAndBytes](https://github.com/TimDettmers/bitsandbytes) 的 8bit 量化方案，先安装 `bitsandbytes`：

```
pip install bitsandbytes
```

然后在之前的命令行里加上 `--dtype int8`：

```
python bloom-inference-scripts/bloom-accelerate-inference.py --name bigscience/bloom --dtype int8 --batch_size 1 --benchmark
```

如果你有超过 4 块 GPU，可以用下面的方式让它只用 4 块：

```
CUDA_VISIBLE_DEVICES=0,1,2,3 python bloom-inference-scripts/bloom-accelerate-inference.py --name bigscience/bloom --dtype int8 --batch_size 1 --benchmark
```

这种情况下不触发 OOM 的最大批次大小是 40。如果你查看脚本内部会发现，我们调整了显存分配图，让第一块 GPU 腾出来只负责激活值和前 token 缓存。

## DeepSpeed-Inference

[DeepSpeed-Inference](https://www.deepspeed.ai/tutorials/inference-tutorial/) 使用张量并行和高效融合的 CUDA kernel，在 128 的大批次下实现了每 token 低于 1ms 的超快推理。

### 安装

```
pip install deepspeed>=0.7.3
```

### 运行

- 最快的方式是使用 TP 预分片（TP = Tensor Parallel）checkpoint，加载只需约 1 分钟，相比之下非预分片的 bloom checkpoint 要 10 分钟：

```
deepspeed --num_gpus 8 bloom-inference-scripts/bloom-ds-inference.py --name microsoft/bloom-deepspeed-inference-fp16
```

1a. 如果你想运行原始的 bloom checkpoint，加载后吞吐与上一个方案相同，但加载要 10-20 分钟：

```
deepspeed --num_gpus 8 bloom-inference-scripts/bloom-ds-inference.py --name bigscience/bloom
```

2a. 8bit 量化版本只需要普通半精度版本一半的 GPU 显存：

```
deepspeed --num_gpus 8 bloom-inference-scripts/bloom-ds-inference.py --name microsoft/bloom-deepspeed-inference-int8 --dtype int8
```

这里我们用了 `microsoft/bloom-deepspeed-inference-int8`，并告诉脚本以 `int8` 运行。

当然，现在 4×80GB A100 就够了：

```
deepspeed --num_gpus 4 bloom-inference-scripts/bloom-ds-inference.py --name microsoft/bloom-deepspeed-inference-int8 --dtype int8
```

这种情况下不触发 OOM 的最大批次大小是 128。

可以看出这里有两个因素共同带来更好的性能：

- 吞吐的提升来自用张量并行（TP）替代 Accelerate 的流水线并行（PP）。Accelerate 由于要足够通用， unfortunately 很难把 GPU 利用率拉满。计算先在 GPU 0 上完成所有层之前的部分，然后交给 GPU 1，依此类推直到 GPU 8——意味着 7 块 GPU 一直闲着。DeepSpeed-Inference 则用 TP：把张量发给所有 GPU，每块 GPU 各算生成的一部分，然后所有 GPU 互相通信结果，再进入下一层。也就是说所有 GPU 同时工作，但它们之间的通信量也大得多。
- DeepSpeed-Inference 还使用定制 CUDA kernel，避免分配过多内存以及在 GPU 之间来回拷贝张量。效果是显存需求更低、kernel 启动次数更少，从而提升吞吐，并允许更大的批次，带来更高的总体吞吐。

想看更多示例，可以参考 [Accelerate GPT-J inference with DeepSpeed-Inference on GPUs](https://www.philschmid.de/gptj-deepspeed-inference) 或 [Accelerate BERT inference with DeepSpeed-Inference on GPUs](https://www.philschmid.de/bert-deepspeed-inference)。

## Deepspeed ZeRO-Inference

[Deepspeed ZeRO](https://www.deepspeed.ai/tutorials/zero/) 采用一种魔法般的分片方法，几乎可以把任何模型扩展到几块甚至几百块 GPU 上，并进行训练或推理。

### 安装

```
pip install deepspeed
```

### 运行

注意，脚本目前会在所有 GPU 上跑相同的输入，但你可以给每块 GPU 跑不同的流，从而把吞吐提升 `n_gpu` 倍。这是 Deepspeed-Inference 做不到的。

```
deepspeed --num_gpus 8 bloom-inference-scripts/bloom-ds-zero-inference.py --name bigscience/bloom --batch_size 1 --benchmark
```

请记住，用 ZeRO 时可以同时生成多条独立的流——因此总体性能应为 secs/token 的吞吐除以参与的 GPU 数——即根据用了 8 还是 16 块 GPU，快 8 到 16 倍！

你还可以用仅一块小 GPU 尝试 offload 方案。运行时间会很长，但如果你没有 8 块大 GPU，这已经是能做到的最好水平。

CPU-Offload（1× GPU）：

```
deepspeed --num_gpus 1 bloom-inference-scripts/bloom-ds-zero-inference.py --name bigscience/bloom --batch_size 8 --cpu_offload --benchmark
```

NVMe-Offload（1× GPU）：

```
deepspeed --num_gpus 1 bloom-inference-scripts/bloom-ds-zero-inference.py --name bigscience/bloom --batch_size 8 --nvme_offload_path=/path/to/nvme_offload --benchmark
```

请务必把 `/path/to/nvme_offload` 改成你在快速 NVMe 盘上拥有约 400GB 空闲空间的位置。

## 额外的客户端与服务器方案

在 [transformers-bloom-inference](https://github.com/huggingface/transformers-bloom-inference) 你还能找到更多高效方案，包括服务器方案。

先睹为快。

服务器方案：

- [Mayank Mishra](https://github.com/mayank31398) 把本文提到的所有 demo 脚本打包成了一个 webserver 包，可以从[这里](https://github.com/huggingface/transformers-bloom-inference)下载。
- [Nicolas Patry](https://github.com/Narsil) 开发了一个超高效率的 [Rust webserver 方案](https://huggingface.co/blog/(https://github.com/Narsil/bloomserver)。

更多客户端方案：

- [Thomas Wang](https://github.com/thomasw21) 正在开发一个极快的 [定制 CUDA kernel BLOOM 模型](https://github.com/huggingface/transformers_bloom_parallel)。
- HuggingFace 的 JAX 团队开发了一个 [基于 JAX 的方案](https://github.com/huggingface/bloom-jax-inference)。

这篇博客在你数月后读到它时很可能已经过时，请以 [transformers-bloom-inference](https://github.com/huggingface/transformers-bloom-inference) 上的最新方案为准。

## 博客致谢

衷心感谢以下好心人提出了好问题并帮助改善了文章的可读性：Olatunji Ruwase 和 Philipp Schmid。
