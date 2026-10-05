---
vendor: modular_cloud
title: 结构化 Mojo 内核（三）：组合实战
original_title: Modular: Structured Mojo Kernels Part 3
url: https://www.modular.com/blog/structured-mojo-kernels-part-3-composition-in-practice
date: 2026-03-26
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# 结构化 Mojo 内核（三）：组合实战

在[第 2 篇](https://www.modular.com/blog/structured-mojo-kernels-part-2-the-three-pillars)中，我们建起了结构化 Mojo 内核的三大支柱：负责数据搬运的 TileIO、负责协调的 TilePipeline、负责计算的 TileOp。这三根支柱构成了内核编程的一个强结构抽象——让内核成为模块化、带类型、可测试零件的组合，而不是大块交织逻辑的单体。

本篇展示这种模块化设计的实际收益。我们拿两个真实内核家族——conv2d 和 block-scaled matmul——逐一追述它们如何在 matmul 地基上搭建。两个案例里，一个新内核家族都只需改动一个组件，其余原封不动。conv2d 内核新增约 130 行代码，block-scaled matmul 新增约 200 行，且都没有任何性能损失。

💡

代码：本系列提到的所有内核都可以在

Modular 仓库

中找到。

## Blackwell 执行模型

本文两个例子都面向 NVIDIA Blackwell（SM100）。两项硬件特性塑造了内核设计。**TMA（Tensor Memory Accelerator）**负责全局内存与共享内存之间的大块异步传输，把计算 warp 从数据搬运中彻底解放出来。**TMEM（Tensor Memory）**是一块专用的 256KB 片上累加器存储，与共享内存分离，因此 MMA（矩阵乘累加）warp 累加结果时不必争抢共享内存带宽（[这些硬件特性详见这篇博客](https://www.modular.com/blog/matrix-multiplication-on-nvidias-blackwell-part-1-introduction)）。

结构化 matmul 内核给它 7 个 warp 各分配固定角色：

| Warps | 角色 | 职责 |
| --- | --- | --- |
| 0–3（128 线程） | Epilogue | TMEM → 寄存器 → SMEM → 经 TMA 写全局内存 |
| 4（32 线程） | Scheduler | 基于 CLC 的工作分发 |
| 5（32 线程） | Load | A、B tile 的 TMA 加载 |
| 6（32 线程） | MMA | Tensor Core 操作、TMEM 累加 |

Warp 特化实现了完全重叠：load warp 预取 tile N+1 时，MMA warp 正在计算 tile N。流水线用 5 到 7 个 stage，把访存延迟（约 500-800 周期）藏到计算（每 tile 约 100 周期）背后。

### 上下文管理的 warp 生命周期

每个 warp 角色都运行在持有其资源的 Mojo 上下文管理器里。MMA warp 的 `MmaWarpContext` 管理完整 TMEM 生命周期：

mojo

```
struct MmaWarpContext[
    opc: OutputPipelineConfig,
    mma_threads: Int,
    epilogue_threads: Int,
]:
    """MMA warp context - owns TMEM lifecycle and output pipeline."""

    comptime Tmem = TmemAllocation[Self.opc.cta_group]
    comptime Pipeline = OutputTilePipeline[Self.opc]
    comptime Dealloc = TmemDeallocBarrier[Self.opc.cta_group]

    var tmem: Self.Tmem
    var output_pipeline: Self.Pipeline
    var dealloc_barrier: Self.Dealloc

    @always_inline
    def __enter__(self) -> Self:
        Self.Sync.arrive()  # Signal epilogue that TMEM is ready
        return self

    @always_inline
    fn __exit__(self):
        self.dealloc_barrier.complete_dealloc(self.tmem)
```

Mojo 的上下文管理器与 Python 一样：保证 `__enter__` 的调用必与 `__exit__` 配对。这里，`__enter__` 向 epilogue warps 发出"TMEM 已分配、就绪"的信号；`__exit__` 等 epilogue 读完后才释放 TMEM。这个朴素做法确保内核作者不会在 TMEM 就绪前误用、忘记与 epilogue 协调，或在提前 return 时泄漏 TMEM。这一切由编译器强制——"构造即正确"。

Epilogue 一侧与之镜像：`EpilogueWarpContext.__enter__` 是空操作（同步由 MMA warp 驱动），`__exit__` 调用 `signal_complete()` 告诉 MMA warp 可以安全释放了。

## 组合轴一：换 TileIO 得到 Conv2d

第一种组合模式是替换：换一个组件，其余组件保持不变。

卷积可以通过 im2col 变换表达成矩阵乘法。我们不必显式物化 im2col 缓冲区（代价是 O(M × K) 内存），而是让 TMA 在加载时就地做坐标变换。这意味着 conv2d 就是"换了个 tile 加载器的 matmul"：数据访问模式变了，但流水线协调和计算完全相同。而这一切靠交换 TileIO 组件即可完成。

### 什么变了

matmul 内核的 `TileLoaderTMA` 从连续内存加载矩形 tile。Conv2d 把它换成 `TileLoaderTMAIm2col`——在考虑步幅、填充和膨胀的情况下，把输出的空间坐标映射为输入坐标：

mojo

```
# Matmul: contiguous tile load
loader_a.load(tiles.a_tile, tiles.barrier, k_coord, m_coord)

# Conv2d: im2col tile load - same interface, different addressing
loader_act.load(tiles.a_tile, tiles.barrier, k_coord, m_coord)
```

调用点一模一样。而把线性索引分解为 (N, H, W, C) 坐标、施加步幅与填充偏移、发出 TMA im2col 事务的寻址逻辑，全部活在加载器内部。

### 什么没变

其余一切。conv2d 内核原样复用 matmul 基础设施：

- **TilePipeline**：同样 `producer()`/`consumer()` 接口的 `InputTilePipeline`
- **TileOp**：TMEM 生命周期完全相同的 `MmaWarpContext`
- **Epilogue**：同样的 `TileWriter` 和 `EpilogueWarpContext`
- **Scheduler**：同样的基于 CLC 的 `TileScheduler`
- **共享内存布局**：同样的流水线存储、同样的屏障数组

conv 特定代码是 [Modular 仓库里约 130 行](https://github.com/modular/modular)：im2col tile 加载器、考虑激活 tile 形状的共享内存布局，以及把二者接起来的内核入口。

### 第 8 个 warp：融合残差加法

带融合残差加法的 Conv2d（`D = Conv(A,B) + beta*C`）在 7-warp 的 matmul 架构上再加一个 warp 角色：

| Warps | 角色 | 职责 |
| --- | --- | --- |
| 0–3 | Epilogue | TMEM → 寄存器、加残差、存储 |
| 4 | Scheduler | 基于 CLC 的工作分发 |
| 5 | MainLoad | 激活与滤波器的 TMA im2col 加载 |
| 6 | MMA | Tensor Core 操作 |
| **7** | **EpilogueLoad** | **残差张量 C 的 TMA 加载** |

EpilogueLoad warp 预取残差张量，与 MMA 计算重叠。当 epilogue warps 把累加结果从 TMEM 读进寄存器时，残差数据已经躺在共享内存里。加法在寄存器层面完成，融合不需要共享内存往返。

结果是零开销。融合残差加法与标准 conv2d 同速，因为加载被完全藏在计算背后。

| 层 | 仅 Conv | Conv + Residual | 开销 |
| --- | --- | --- | --- |
| 16×16, 128→128 | 0.037 ms | 0.037 ms | ~0% |
| 32×32, 256→256 | 0.068 ms | 0.066 ms | ~0% |
| 64×64, 256→128 | 0.068 ms | 0.066 ms | ~0% |

加这第 8 个 warp，对原有 7 个 warp 零改动。

### 别人是怎么做的

拿提供最优实现的 CUTLASS 来对比。CUTLASS 把 conv2d 实现为一个[独立的 870 行内核](https://github.com/NVIDIA/cutlass/blob/main/include/cutlass/conv/kernel/sm100_implicit_gemm_tma_warpspecialized.hpp)，大半复制自其 matmul 内核。流水线搭建、warp 协调、屏障管理、TMEM 生命周期全部重新实现一遍。matmul 内核的每一项优化都得手工移植到 conv2d 内核并独立验证。这是因为 CUTLASS 的模板实例化模型把流水线、屏障和 epilogue 逻辑耦合在具体的 tile 与布局类型上，根本不存在一个能替换加载器而不复制周边基础设施的抽象边界。

用结构化组件，conv2d 内核直接 import matmul 基础设施，只换其中一块。共享组件的 bug 修复和优化自动传导。

## 组合轴二：通过 TilePayload 得到 Block-scaled matmul

Conv2d 靠换组件完成组合。Block-scaled matmul 展示第二种模式：给组件参数化，让它处理结构上不同的数据流，而搬运它的流水线不变。

Block-scaled 矩阵乘法在标准 matmul 之上为 FP8/FP4 量化推理增加了逐块缩放因子：

这改变了数据流：TMA 加载从 2 次变 4 次、缩放因子 tile 需要额外共享内存、epilogue 要感知缩放并在输出时应用因子。在单体内核里，这些改动会散落在数千行中。有了结构化组件，它们收敛到一个地方：payload。这种组合模式适用于任何"payload 类型更新但流水线结构不变"的内核。

### TilePayload trait

`InputTilePipeline` 的关键设计决策是：流水线按其 payload 类型参数化。流水线管理同步——屏障等待、stage 推进、生产者/消费者角色。payload 管理被同步的东西——哪些 tile、多少个、什么布局。trait 本身只是个标记，结构来自各实现：

mojo

```
trait TilePayload:
    """Marker trait for tile payload types."""
    pass
```

### 三种 payload，一条流水线

`StandardTilePayload` 为标准 matmul 携带 A、B tiles：

mojo

```
struct StandardTilePayload[...](TilePayload):
    var a_tiles: Self.ATileArray
    var b_tiles: Self.BTileArray

    def get_tile[k_group_size: Int](
        self, stage: UInt32, k_idx: Int,
    ) -> Tuple[Self.ATile, Self.BTile]:
        var idx = stage * UInt32(k_group_size) + UInt32(k_idx)
        return (self.a_tiles[idx], self.b_tiles[idx])
```

`BlockScaledTilePayload` 为 MXFP8/NVFP4 增加缩放因子 tiles：

mojo

```
struct BlockScaledTilePayload[...](TilePayload):
    var a_tiles: Self.ATileArray
    var b_tiles: Self.BTileArray
    var sfa_tiles: Self.SFATileArray
    var sfb_tiles: Self.SFBTileArray

    def get_tile[k_group_size: Int](
        self, stage: UInt32, k_idx: Int,
    ) -> Tuple[Self.ATile, Self.BTile, Self.SFATile, Self.SFBTile]:
        var idx = stage * UInt32(k_group_size) + UInt32(k_idx)
        return (
            self.a_tiles[idx], self.b_tiles[idx],
            self.sfa_tiles[idx], self.sfb_tiles[idx],
        )
```

`BlockwiseFP8TilePayload` 携带 A、B 和 A-scale（B-scale 在 epilogue 期间从全局内存读取）：

mojo

```
struct BlockwiseFP8TilePayload[...](TilePayload):
    var a_tiles: Self.ATileArray
    var b_tiles: Self.BTileArray
    var a_scales_tiles: Self.AScalesTileArray

    def get_tile[k_group_size: Int](
        self, stage: UInt32, k_idx: Int,
    ) -> Tuple[Self.ATile, Self.BTile, Self.AScalesTile]:
        var idx = stage * UInt32(k_group_size) + UInt32(k_idx)
        return (
            self.a_tiles[idx], self.b_tiles[idx],
            self.a_scales_tiles[idx],
        )
```

于是，`InputTilePipeline` 对任何满足 `TilePayload` 的类型泛型可用。

### 泛型流水线

mojo

```
struct InputTilePipeline[
    Payload: TilePayload,
    num_group_stages: Int,
    k_group_size: Int,
]:
    """Tile pipeline parameterized by payload type."""

    comptime Pipeline = ProducerConsumerPipeline[Self.num_group_stages]

    var pipeline: Self.Pipeline
    var payload: Self.Payload

    def producer(ref [origin]self) -> InputProducer[...]:
        return InputProducer(pipeline_ptr=Pointer(to=self))

    def consumer(ref [origin]self) -> InputConsumer[...]:
        return InputConsumer(pipeline_ptr=Pointer(to=self))
```

`producer()` 和 `consumer()` 返回的 `InputProducer`、`InputConsumer` 提供 `acquire()` 上下文管理器。`with producer.acquire() as tiles:` 在进入时等屏障、期间提供 payload tiles 的访问、退出时推进 stage。

Mojo 的编译期元编程把每个 `InputTilePipeline[StandardTilePayload]`、`InputTilePipeline[BlockScaledTilePayload]` 单态化（monomorphize）为完全特化的代码。因此没有 vtable 分派开销，你得到的正是零成本抽象。

### 改什么 vs 复用什么

| 组件 | 标准 | Block-Scaled | Blockwise FP8 | 共享？ |
| --- | --- | --- | --- | --- |
| InputTilePipeline | ✓ | ✓ | ✓ | **是** |
| InputProducer/Consumer | ✓ | ✓ | ✓ | **是** |
| ProducerConsumerPipeline | ✓ | ✓ | ✓ | **是** |
| MmaWarpContext | ✓ | ✓ | ✓ | **是** |
| EpilogueWarpContext | ✓ | ✓ | ✓ | **是** |
| TileScheduler | ✓ | ✓ | ✓ | **是** |
| TilePayload | Standard | BlockScaled | BlockwiseFP8 | 否 |
| Epilogue | Standard | Scale-aware | Per-K scales | 否 |

加入 block-scaled 支持约 200 行。给单体内核加等价功能则需要约 1,500 行散落各处的修改。

## 零成本抽象

抽象只有不损失性能才站得住脚。我们比对了结构化与旧版 Blackwell matmul 内核的 SASS（GPU 汇编）输出来验证——指令序列完全一致。我们还在端到端模型上验证了性能，比如 Llama 基准显示性能持平而代码少 50%：

| 基准 | 平均差异 | 说明 |
| --- | --- | --- |
| Llama 8B Decode | -0.2% | 性能持平 |
| Llama 8B Prefill | -0.1% | 性能持平 |
| Llama 405B TP8 | +0.2% | 略有更快 |

## 这两个例子说明了什么

Conv2d 和 block-scaled matmul 代表了实践中内核需求变化的两种最常见方式：需要不同的数据访问模式（换 TileIO），或需要带更多操作数的新数据类型（参数化 TilePayload）。结构化设计对两者都应付自如，共享基础设施零改动。

这些组合模式可以推广到其他场景。如果变的是"数据从内存到共享内存的路径"，就换 TileIO。如果变的是"加载后在流水线里流动的东西的结构"，就参数化 payload。

对任何构建或维护内核库的人来说，这种可预测性价值巨大：在共享流水线或 epilogue 代码里发现一个 bug，修一次，所有用到该组件的内核都得到修复；出现一种新量化方案，增量成本是 200 行量级而非整体重写；新一代 GPU 架构到来，平台特定代码留在自己层内，内核逻辑不变。这个架构不会随每个新变体累积债务。

[第 4 篇](https://www.modular.com/blog/structured-mojo-kernels-part-4-portability-and-the-road-ahead)把最后这一点带到 AMD。我们展示把这些内核移植到根本不同的内存层次与执行模型实际意味着什么，以及这套架构接下来往哪走。

## TL;DR

- **Conv2d 靠换 TileIO 组合而成。**把连续 tile 加载器换成支持 im2col 的变体；整条 matmul 流水线、计算、epilogue、调度器原样复用。约 130 行 conv 特定代码，对比 CUTLASS 870 行的独立内核。
- **Block-scaled matmul 靠参数化 TilePipeline 组合而成。**`TilePayload` trait 把同步与 tile 存储解耦。三个 payload 实现共享一条流水线，屏障管理零改动。
- **第 8 个 warp 扩展而不用分叉。**Conv2d 的融合残差加法新增一个 warp 角色，原有七个不动。零开销，因为残差加载藏在计算背后。
- **抽象是零成本的。**结构化与旧版内核的 SASS 输出完全一致。Llama 基准证实性能持平。
- **改动保持局部。**新内核由现有组件组合。修复自动传导。每个新内核变体的增量行数可预期，而非整体重写。
