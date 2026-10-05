---
vendor: modular_cloud
title: Structured Mojo Kernels 第 1 篇——峰值性能，一半代码
original_title: Modular: Structured Mojo Kernels Part 1
url: https://www.modular.com/blog/structured-mojo-kernels-part-1-peak-performance-half-the-code
date: 2026-03-05
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Structured Mojo Kernels 第 1 篇——峰值性能，一半代码

## GPU 编程不必这么难

GPU 编程向来要求精确，但精确的代价在不断攀升。一个用 C++ 写的生产 matmul kernel 有 3,000–5,000 行紧耦合代码，一个放错位置的 barrier 就能悄悄损坏结果。这种复杂性把关乎大量开发者本应可用的硬件挡在门外，而它正是 GPU 演进方式的直接产物：每一代架构，都有更多编排重担转移到程序员肩上。

Triton 这类 DSL 改善了可及性，但代价真实存在。当你需要为规模化推理榨取峰值利用率，最终不得不钻到抽象层之下——那时你早已把 DSL 最初带来的生产力红利拱手让出。想更深入理解这一权衡，见我们[关于 Python eDSL 的文章](https://www.modular.com/blog/democratizing-ai-compute-part-7-what-about-triton-and-python-edsls)。

CUTLASS 与 CuTe 这类框架走另一个极端：把一切暴露出来。结果是 50 万行以上的 C++ 模板机器、一个控制流受限的 Python DSL 层（不许 `break`、不许从循环 `return`）、需要穿越多重抽象层做“考古”才能懂的错误信息，以及 NVIDIA 锁定。你拿到峰值性能，但框架本身成了复杂性问题的来源。

Mojo 的设计目标正是打破这一权衡。这门语言给你直达整个硬件栈的访问能力（我们在[四篇 Blackwell 性能系列](https://www.modular.com/blog/matrix-multiplication-on-nvidias-blackwell-part-1-introduction)中详细讲过），同时其编译期元编程足够强大，可以支撑零运行时开销的高层抽象。

Structured Mojo Kernels 是实际的成果。它是一套围绕关注点分离构建的 API：带干净接口的模块化组件，让 GPU kernel 写起来更高效、维护起来更容易，同时在性能上分毫不让。本文余下部分展示它们具体如何工作。

💡

自己动手试试：本系列提到的所有 Mojo kernels 均可在

Modular 仓库

中找到。

## 解法：结构化的 kernel 架构

Structured Mojo Kernels 把 kernel 逻辑组织为三个核心组件，由一个共享的配置层和一个共享的数据管理层统一起来。

Structured Kernel Architecture

每个组件职责单一、接口明确：

| Component | Responsibility | Encapsulates |
| --- | --- | --- |
| TileIO | Moves data between memory levels. Acts as a producer to TilePipeline. | TMA/DMA, layout transforms, swizzling |
| **TilePipeline** | Coordinates pipeline stages, and manages shared memory. | Barriers, producer-consumer sync |
| **TileOp** | Executes compute operations. Acts as a consumer to TilePipeline. | MMA instructions, register management |

注意这些是模式名而非库 API。具体实现（`InputTilePipeline`、`OutputTilePipeline` 及对应件）位于开源 kernel 库中，遵循这些模式。

关注点分离让每个组件都可驾驭：

- TileIO 不知道计算操作。
- TilePipeline 不知道内存布局。
- TileOp 不知道全局内存。

如果这听起来就是基本软件工程——这正是重点。它在这里之所以要紧，是因为传统 GPU kernel 开发不是这么干的。一个 CUTLASS kernel 把流水线协调、计算逻辑与数据搬运交缠在数千行里。手写的 CUDA 或 HIP kernel 同样如此。Structured Mojo Kernels 把软件其他所有领域当作底线要求的关注点分离带了进来。

### 分离的力量

在传统 kernel 开发中，加入 block-scaled 量化意味着另写一个 1,500 行的 kernel。这些行大多是从既有 kernel 改来的，修改散布各处。因为没有天然的切缝——流水线协调、计算逻辑、数据运动全都交叠在一起。

有了结构化组件，这些改动几乎全部集中在一个地方：代表组件间传递数据的 “payload” 结构。

mojo

```
# Monolithic Kernel: Scattered changes across 3000+ lines

# Structured Kernel: Localized changesstruct BlockScaledTilePayload[...](TilePayload):
var a_tiles: Pointer[...]
var b_tiles: Pointer[...]
var sfa_tiles: Pointer[...]  # NEW: Scale factor A
var sfb_tiles: Pointer[...]  # NEW: Scale factor B
```

流水线协调（TilePipeline）、计算逻辑（TileOp）与数据搬运模式（TileIO）无需改动——因为它们被正确解耦了。

同一原则可放大到完全不同的 kernel 类型。我们最近构建 SM100 卷积 kernel，只换了一个组件（把标准 TMA tile 加载器换成 im2col 感知变体），其余整个 matmul 基础设施全部复用：流水线、MMA warp 上下文、epilogue、调度器与输出写入器。在 CUTLASS 中，等价的 conv kernel 是一个[独立的 870 行文件](https://github.com/NVIDIA/cutlass/blob/main/include/cutlass/conv/kernel/sm100_implicit_gemm_tma_warpspecialized.hpp)，大体是从 matmul kernel 复制的。用结构化组件，[conv 专属代码](https://github.com/modular/modular/blob/2e6b98d33b02b91366b5fb79141c528473c6903c/max/kernels/src/nn/conv_sm100/conv2d.mojo)约 130 行。

### 这取代了什么

要看清结构为何重要，先看看真实 CUTLASS SM100 kernel 里流水线的搭建过程。kernel 必须初始化 6 个独立的流水线对象，每个都要显式角色分配、到达计数、事务字节与 barrier 配置：

c++

```
// CUTLASS SM100 kernel: pipeline setup.
// Each pipeline needs: Params struct, role assignment per warp category,
// arrival counts, transaction bytes, initializing warp ID, and construction.

// Mainloop Load pipeline
typename MainloopPipeline::Params mainloop_pipeline_params;
if (WarpCategory::MainloopLoad == warp_category) {
  mainloop_pipeline_params.role = MainloopPipeline::ThreadCategory::Producer;
}
if (WarpCategory::MMA == warp_category) {
  mainloop_pipeline_params.role = MainloopPipeline::ThreadCategory::Consumer;
}
mainloop_pipeline_params.is_leader = lane_predicate && is_mma_leader_cta
                                     && is_participant.main_load;
mainloop_pipeline_params.transaction_bytes = CollectiveMainloop::TmaTransactionBytes;
mainloop_pipeline_params.initializing_warp = 0;
MainloopPipeline mainloop_pipeline(shared_storage.pipelines.mainloop,
                                   mainloop_pipeline_params, cluster_shape,
                                   cute::true_type{}, cute::false_type{});

// Epilogue Load pipeline
typename EpiLoadPipeline::Params epi_load_pipeline_params;
if (WarpCategory::EpilogueLoad == warp_category) {
  epi_load_pipeline_params.role = EpiLoadPipeline::ThreadCategory::Producer;
}
if (WarpCategory::Epilogue == warp_category) {
  epi_load_pipeline_params.role = EpiLoadPipeline::ThreadCategory::Consumer;
}
epi_load_pipeline_params.dst_blockid = cta_rank_in_cluster;
epi_load_pipeline_params.producer_arv_count = NumEpilogueLoadThreads;
epi_load_pipeline_params.consumer_arv_count = NumEpilogueThreads;
epi_load_pipeline_params.transaction_bytes = CollectiveEpilogue::TmaTransactionBytes;
epi_load_pipeline_params.initializing_warp = 1;
EpiLoadPipeline epi_load_pipeline(shared_storage.pipelines.epi_load,
                                   epi_load_pipeline_params);

// Epilogue Store pipeline
typename EpiStorePipeline::Params epi_store_pipeline_params;
epi_store_pipeline_params.always_wait = true;
EpiStorePipeline epi_store_pipeline(epi_store_pipeline_params);

// Load order barrier
typename LoadOrderBarrier::Params load_order_barrier_params;
load_order_barrier_params.group_id = (warp_category == WarpCategory::MainloopLoad) ? 0 : 1;
load_order_barrier_params.group_size = NumMainloopLoadThreads;
load_order_barrier_params.initializing_warp = 3;
LoadOrderBarrier load_order_barrier(shared_storage.pipelines.load_order,
                                    load_order_barrier_params);

// CLC pipeline
typename CLCPipeline::Params clc_pipeline_params;
if (WarpCategory::Sched == warp_category) {
  clc_pipeline_params.role = CLCPipeline::ThreadCategory::ProducerConsumer;
} else {
  clc_pipeline_params.role = CLCPipeline::ThreadCategory::Consumer;
}
clc_pipeline_params.producer_blockid = 0;
clc_pipeline_params.producer_arv_count = 1;
clc_pipeline_params.consumer_arv_count = NumSchedThreads + cluster_size *
    (NumMainloopLoadThreads + NumEpilogueThreads + NumMMAThreads);
if (is_epi_load_needed) {
  clc_pipeline_params.consumer_arv_count += cluster_size * NumEpilogueLoadThreads;
}
clc_pipeline_params.transaction_bytes = CLCResponseSize;
clc_pipeline_params.initializing_warp = 4;
CLCPipeline clc_pipeline(shared_storage.pipelines.clc,
                          clc_pipeline_params, cluster_shape);

// Accumulator pipeline
typename AccumulatorPipeline::Params accumulator_pipeline_params;
if (WarpCategory::MMA == warp_category) {
  accumulator_pipeline_params.role = AccumulatorPipeline::ThreadCategory::Producer;
}
if (WarpCategory::Epilogue == warp_category) {
  accumulator_pipeline_params.role = AccumulatorPipeline::ThreadCategory::Consumer;
}
accumulator_pipeline_params.producer_arv_count = 1;
accumulator_pipeline_params.consumer_arv_count = size(AtomThrShapeMNK{})
                                                 * NumEpilogueThreads;
accumulator_pipeline_params.initializing_warp = 5;
AccumulatorPipeline accumulator_pipeline(shared_storage.pipelines.accumulator,
                                         accumulator_pipeline_params, cluster_shape,
                                         cute::true_type{}, cute::false_type{});

// TMEM allocator + 2 deallocation barriers
TmemAllocator tmem_allocator{};
arch::NamedBarrier tmem_allocation_result_barrier(
    NumMMAThreads + NumEpilogueThreads,
    cutlass::arch::ReservedNamedBarriers::TmemAllocBarrier);
arch::ClusterBarrier& tmem_deallocation_result_barrier =
    shared_storage.pipelines.tmem_dealloc;

// 7 pipeline state variables
MainloopPipelineState mainloop_pipe_consumer_state;
MainloopPipelineState mainloop_pipe_producer_state = make_producer_start_state<MainloopPipeline>();
EpiLoadPipelineState epi_load_pipe_consumer_state;
EpiLoadPipelineState epi_load_pipe_producer_state = make_producer_start_state<EpiLoadPipeline>();
EpiStorePipelineState epi_store_pipe_producer_state = make_producer_start_state<EpiStorePipeline>();
CLCPipelineState clc_pipe_consumer_state;
AccumulatorPipelineState accumulator_pipe_producer_state = make_producer_start_state<AccumulatorPipeline>();
AccumulatorPipelineState accumulator_pipe_consumer_state;
Mojo (lines 789-834 of conv2d_fprop_kernel.mojo):


# Pipeline + payload: 2 lines
var tile_payload = Self.TilePayload(smem.act_tiles(), smem.filter_tiles())
var input_pipeline = Self.InputTilePipelineType(
    smem.pipelines.input_barriers(), tile_payload)

# Context: 1 line
var ctx = Self.Context(smem.pipelines.tmem_addr())

# Epilogue load pipeline: 2 lines
var epi_load_pipeline = Self.EpiLoadPipelineType(smem.epi_load_barriers().ptr)
var load_order_barrier = LoadOrderBarrier(smem.get_load_order_barrier().ptr)
```

在结构化 Mojo kernel 中，角色分配与到达计数被编码进编译期参数，从 kernel 主体中彻底消失。CUTLASS 中需要 100 多行显式配置的同一套流水线搭建，在这里变成：

mojo

```
# Structured Mojo: pipeline setup
var tile_payload = Self.TilePayload(smem.act_tiles(), smem.filter_tiles())
var input_pipeline = Self.InputTilePipeline(
    smem.pipelines.input_barriers(), tile_payload)
var ctx = Self.Context(smem.pipelines.tmem_addr())
```

类型系统承载了配置。没有角色分配、kernel 主体里没有到达计数、没有要跟踪的状态变量。

### 上下文管理器取代手工协议

GPU kernel 最大的 bug 来源是流水线同步。在 CUTLASS 的 MMA warp 中，程序员要手工分配 TMEM、获取并提交流水线 stage、还要处理多步的释放序列：

c++

```
// CUTLASS SM100 kernel: MMA warp
else if (is_participant.mma) {
  // Manual TMEM allocation
  tmem_allocator.allocate(TmemAllocator::Sm100TmemCapacityColumns,
                          &shared_storage.tmem_base_ptr);
  __syncwarp();
  tmem_allocation_result_barrier.arrive();
  uint32_t tmem_base_ptr = shared_storage.tmem_base_ptr;

  // Manual TMEM stage pointer setup
  for (int acc_stage = 0; acc_stage < AccumulatorPipelineStageCount; acc_stage++) {
    tmem_stage_ptrs[acc_stage] = tmem_base_ptr
        + (TmemColumnsPerAccumulatorTile * acc_stage) & cutlass::detail::TmemColMask;
  }
  auto mma_inputs = collective_mainloop.mma_init(shared_storage.tensors.mainloop);

  do {
    auto k_tile_count = scheduler.get_work_k_tile_count(...);
    auto [next_work_tile_info, increment_pipe] = scheduler.fetch_next_work(
        work_tile_info, clc_pipeline, clc_pipe_consumer_state);
    if (increment_pipe) { ++clc_pipe_consumer_state; }

    // Manual pipeline acquire
    if (is_mma_leader_cta) {
      accumulator_pipeline.producer_acquire(accumulator_pipe_producer_state);
    }
    int acc_stage = accumulator_pipe_producer_state.index();
    accumulators.data() = tmem_stage_ptrs[acc_stage];

    if (is_mma_leader_cta) {
      mainloop_pipe_consumer_state = collective_mainloop.mma(
          mainloop_pipeline, mainloop_pipe_consumer_state,
          accumulators, mma_inputs, k_tile_count);
      // Manual pipeline commit
      accumulator_pipeline.producer_commit(accumulator_pipe_producer_state);
    }
    ++accumulator_pipe_producer_state;
    work_tile_info = next_work_tile_info;
  } while (work_tile_info.is_valid());

  // Manual cleanup: release lock, wait for peers, deallocate
  tmem_allocator.release_allocation_lock();
  if (is_mma_leader_cta) {
    accumulator_pipeline.producer_tail(accumulator_pipe_producer_state);
  }
  if constexpr (has_mma_peer_cta) {
    tmem_deallocation_result_barrier.arrive(mma_peer_cta_rank, not is_mma_leader_cta);
    tmem_deallocation_result_barrier.wait(dealloc_barrier_phase);
    tmem_deallocation_result_barrier.arrive(mma_peer_cta_rank, is_mma_leader_cta);
  }
  tmem_allocator.free(tmem_base_ptr, TmemAllocator::Sm100TmemCapacityColumns);
}
```

每个 `producer_acquire` 必须与一个 `producer_commit` 配对。清理序列（释放锁、tail 信号、对端同步、free）必须按精确顺序发生。漏掉任何一步，你就得到一个静默挂死。

在结构化 Mojo kernel 中，上下文管理器让错误的同步根本无法被表达：

mojo

```
# Structured Mojo: MMA warp
if WarpRole.is_mma():
    var tmem = Self.Tmem.allocate(smem.pipelines.tmem_addr())
    var mma_ctx = Self.MmaCtx(tmem, Self.OutputPipeline(...), Self.TmemDealloc(...))

    with mma_ctx:  # TMEM alloc → sync → lock release → dealloc on exit
        while work_iter.has_work():
            with work_iter.wait_and_advance():
                if ctx.elect_one_cta:
                    with mma_ctx.output_pipeline.producer() as output_stage:
                        with input_pipeline.consumer() as consumer:
                            for i in range(0, num_iters, Self.config.k_group_size):
                                with consumer.acquire() as input_tiles:
                                    Self.mma(output_stage.tmem, input_tiles,
                                             mma_op, ctx.elect_one_warp, UInt32(i), 0)
```

`with mma_ctx:` 块处理整个 TMEM 生命周期。嵌套的 `with` 块处理输出流水线的 producer 分 stage、输入流水线的 consumer 步进，以及逐 tile 的 barrier 获取/释放。没有可能搞错的手工 `acquire`/`commit` 配对——顺序由编译器强制。

## 为什么这非 Mojo 不可

Mojo 的编译期元编程与 RAII 模式确保这些抽象不留任何运行时痕迹：生成的汇编与手写代码完全相同。

正是这个组合让“structured”成为可能而又不“slow”。CUTLASS 用 C++ 模板达成类似目标，代价是庞大的框架复杂度与密不透风的错误信息。Triton 换来了生产力，却表达不出峰值性能所需的底层控制。Mojo 目前是唯一同时具备完整编译期元编程、可保证的资源管理与一等公民 GPU 支持的语言，让这些抽象以零运行时成本成立。

## 对比一览

|  | CUTLASS / CuTe DSL | Structured Mojo Kernels |
| --- | --- | --- |
| **Peak performance** | Yes | Yes (~1770 TFLOPS on SM100) |
| **Framework size** | ~500K+ lines | ~7K lines |
| **Platform support** | NVIDIA only | NVIDIA + AMD |
| **Pipeline safety** | Manual (forget `.commit()` → hang) | Compile-time (context managers) |
| **Error messages** | C++ template archaeology | Line number + fix suggestion |
| **Control flow** | Restricted in DSL | Full (break, return, etc.) |

这是我们把 SM100 matmul kernel 迁移到结构化组件后的真实数据：

| Metric | Conventional approach | Structured Mojo Kernels | Change |
| --- | --- | --- | --- |
| Total lines | 14,683 | 7,634 | **-48%** |
| Main kernel | 3,721 | 1,843 | **-50%** |
| Performance | ~1770 TFLOPS | ~1770 TFLOPS | **Equal** |

代码几乎减半，性能分毫未损。编译产物与手写 kernel 无法区分，没有任何抽象开销。

当你构建新 kernel 时，这份收益还在复利。我们的 SM100 conv2d 只需约 130 行 conv 专属代码（im2col tile 加载器与共享内存布局），其余 matmul 基础设施整体复用：流水线、MMA warp 上下文、epilogue、调度器与输出写入器。CUTLASS 的等价物是一个[独立的 870 行 kernel](https://github.com/NVIDIA/cutlass/blob/main/include/cutlass/conv/kernel/sm100_implicit_gemm_tma_warpspecialized.hpp)，大体复制自其 matmul kernel。这就是关注点分离与复制粘贴的区别。

当你确实需要下沉——当某个 kernel 需要结构化组件没有表达的东西——Mojo 允许你。这套架构不阻止你直接对硬件编程。区别在于：你很少再需要这么干；即使需要，你改的也是一个只有一半大、推理起来容易得多的代码库。

## 接下来

本文介绍了架构与动机。接下来三篇进入细节：

- [**第 2 篇：三根支柱。**](https://www.modular.com/blog/structured-mojo-kernels-part-2-the-three-pillars)用真实代码讲解 TileIO、TilePipeline 与 TileOp：每个组件如何工作、接口为何这样设计、它们如何组合成完整 kernel。
- [**第 3 篇：组合的实践**](https://www.modular.com/blog/structured-mojo-kernels-part-3-composition-in-practice)**。**把架构扩展到 conv2d、block-scaled matmul 与其他苛刻的 kernel 变体。
- [**第 4 篇：可移植性与前路**](https://www.modular.com/blog/structured-mojo-kernels-part-4-portability-and-the-road-ahead)**。**同样的结构化模式如何映射到 NVIDIA Blackwell 与 AMD MI300X，底层硬件改变时什么会变。

## TL;DR

- **生产级 GPU kernel 难写，更难维护。**现代硬件要求对流水线、barrier 与内存做显式软件编排。现有框架的回应是巨大的复杂度。
- **Structured Mojo Kernels 分离关注点。**TileIO、TilePipeline 与 TileOp 各守一责，接口干净。改动保持局部。新 kernel 变体由既有组件组合而成。
- **上下文管理器消除同步 bug。**管理流水线转换的 `with` 块让错误顺序在源码里无法表达。
- **零成本抽象是真的。**Mojo 的编译期元编程与 RAII 模式让结构在运行时消失。代码少 48%，性能相同。
- **轻量、可移植、开放。**约 7K 行库代码，跑在 NVIDIA 与 AMD 上，可在 [Modular 仓库](https://github.com/modular/modular)获取。
