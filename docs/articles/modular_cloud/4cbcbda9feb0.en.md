---
vendor: modular_cloud
title: Structured Mojo Kernels Part 1 - Peak Performance, Half the Code
original_title: Modular: Structured Mojo Kernels Part 1
url: https://www.modular.com/blog/structured-mojo-kernels-part-1-peak-performance-half-the-code
date: 2026-03-05
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: a1765132c91c
---

March 5, 2026

# Structured Mojo Kernels Part 1 - Peak Performance, Half the Code

Fabio Riccardi

Modular Kernel Team

Engineering

## GPU programming doesn't have to be this hard

GPU programming has always demanded precision, but the cost of that precision keeps rising. A production matmul kernel written in C++ spans 3,000–5,000 lines of tightly coupled code where a misplaced barrier silently corrupts results. That complexity gatekeeps hardware that should be available to far more developers, and it's a direct product of how GPUs have evolved: with each architecture generation, more of the orchestration burden has shifted onto the programmer.

DSLs like Triton improve accessibility, but at a real cost. When you need peak utilization for inference at scale, you eventually have to drop below the abstraction layer, at which point you've surrendered the productivity benefit the DSL offered in the first place. For a deeper look at this tradeoff, see our [post on Python eDSLs](https://www.modular.com/blog/democratizing-ai-compute-part-7-what-about-triton-and-python-edsls).

Frameworks like CUTLASS and CuTe take the opposite approach: expose everything. The result is 500K+ lines of C++ template machinery, a Python DSL layer with restricted control flow (no `break`, no `return` from loops), error messages that require archaeology through multiple abstraction layers, and NVIDIA lock-in. You get peak performance, but the framework becomes the complexity problem.

Mojo was designed to break this tradeoff. The language gives you direct access to the full hardware stack (we covered this in depth in our [four-part series on Blackwell performance](https://www.modular.com/blog/matrix-multiplication-on-nvidias-blackwell-part-1-introduction)) while also enabling compile-time metaprogramming powerful enough to support high-level abstractions with no runtime cost.

Structured Mojo Kernels are the practical result. They are a set of APIs built around separation of concerns: modular components with clean interfaces that make GPU kernels more productive to write and easier to maintain, without giving anything back on performance. The rest of this post shows you exactly how they work.

💡

Try this yourself: All Mojo kernels mentioned in this series are available in the

Modular repository

.

## The solution: structured kernel architecture

Structured Mojo Kernels organize kernel logic into three core components, unified by a shared configuration layer and a shared data management layer.

Structured Kernel Architecture

Each component has a single responsibility and well-defined interfaces:

| Component | Responsibility | Encapsulates |
| --- | --- | --- |
| TileIO | Moves data between memory levels. Acts as a producer to TilePipeline. | TMA/DMA, layout transforms, swizzling |
| **TilePipeline** | Coordinates pipeline stages, and manages shared memory. | Barriers, producer-consumer sync |
| **TileOp** | Executes compute operations. Acts as a consumer to TilePipeline. | MMA instructions, register management |

Note that these are pattern names, not library APIs. The concrete implementations (`InputTilePipeline`, `OutputTilePipeline`, and their counterparts) live in the open-source kernels library and follow these patterns.

Separation of concerns keeps each component tractable:

- TileIO doesn't know about compute operations.
- TilePipeline doesn't know about memory layouts.
- TileOp doesn't know about global memory.

If this sounds like basic software engineering, that's the point. The reason it matters here is that conventional GPU kernel development doesn't work this way. A CUTLASS kernel interleaves pipeline coordination, compute logic, and data movement throughout thousands of lines. The same is true for hand-written CUDA or HIP kernels. Structured Mojo Kernels bring the same separation of concerns that every other domain of software treats as a baseline requirement.

### The power of separation

In conventional kernel development, adding block-scaled quantization means writing a separate 1,500-line kernel. Those lines are mostly adapted from the existing kernel, with changes scattered throughout. There’s no natural seam to cut along because pipeline coordination, compute logic, and data movement are all interleaved.

With structured components, those changes are almost all localized in a single place: the “payload” structure representing the data passed between the components.

mojo

```
# Monolithic Kernel: Scattered changes across 3000+ lines

# Structured Kernel: Localized changesstruct BlockScaledTilePayload[...](TilePayload):
var a_tiles: Pointer[...]
var b_tiles: Pointer[...]
var sfa_tiles: Pointer[...]  # NEW: Scale factor A
var sfb_tiles: Pointer[...]  # NEW: Scale factor B
```

The pipeline coordination (TilePipeline), compute logic (TileOp), and data movement patterns (TileIO) didn’t need to change because they're properly decoupled.

The same principle scales to entirely different kernel types. We recently built an SM100 convolution kernel by swapping a single component (replacing the standard TMA tile loader with an im2col-aware variant) and reusing the entire matmul infrastructure: pipelines, MMA warp context, epilogue, scheduler, and output writer. In CUTLASS, the equivalent conv kernel is a [separate 870-line file](https://github.com/NVIDIA/cutlass/blob/main/include/cutlass/conv/kernel/sm100_implicit_gemm_tma_warpspecialized.hpp) largely duplicated from the matmul kernel. With structured components, the [conv-specific code](https://github.com/modular/modular/blob/2e6b98d33b02b91366b5fb79141c528473c6903c/max/kernels/src/nn/conv_sm100/conv2d.mojo) is ~130 lines.

### What this replaces

To see why structure matters, here’s what pipeline setup looks like in a real CUTLASS SM100 kernel. The kernel must initialize 6 separate pipeline objects, each with explicit role assignment, arrival counts, transaction bytes, and barrier configuration:

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

In structured Mojo kernels, role assignment and arrival counts are encoded in compile-time parameters, eliminating them from the kernel body entirely. The same pipeline setup that required 100+ lines of explicit configuration in CUTLASS becomes:

mojo

```
# Structured Mojo: pipeline setup
var tile_payload = Self.TilePayload(smem.act_tiles(), smem.filter_tiles())
var input_pipeline = Self.InputTilePipeline(
    smem.pipelines.input_barriers(), tile_payload)
var ctx = Self.Context(smem.pipelines.tmem_addr())
```

The type system carries the configuration. No role assignment, no arrival counts in the kernel body, no state variables to track.

### Context managers replace manual protocol

The biggest source of bugs in GPU kernels is pipeline synchronization. In the CUTLASS MMA warp, the programmer manually allocates TMEM, acquires and commits pipeline stages, and handles a multi-step deallocation sequence:

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

Every `producer_acquire` must pair with a `producer_commit`. The cleanup sequence (lock release, tail signal, peer sync, free) must happen in exact order. Miss any step and you get a silent hang.

In structured Mojo kernels, context managers make incorrect synchronization unrepresentable:

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

The `with mma_ctx:` block handles the entire TMEM lifecycle. The nested `with` blocks handle output pipeline producer staging, input pipeline consumer stepping, and per-tile barrier acquire/release. There are no manual `acquire`/`commit` pairs to get wrong; the compiler enforces correct ordering.

## Why this needs Mojo

Mojo's compile-time metaprogramming and RAII patterns ensure these abstractions leave no runtime trace; the generated assembly is identical to hand-written code.

This combination is what makes “structured” possible without “slow.” CUTLASS achieves similar goals with C++ templates but at the cost of enormous framework complexity and impenetrable error messages. Triton achieves productivity but can’t express the low-level control needed for peak performance. Mojo is currently the only language that combines full compile-time metaprogramming, guaranteed resource management, and first-class GPU support, enabling these abstractions with zero runtime cost.

## How it compares

|  | CUTLASS / CuTe DSL | Structured Mojo Kernels |
| --- | --- | --- |
| **Peak performance** | Yes | Yes (~1770 TFLOPS on SM100) |
| **Framework size** | ~500K+ lines | ~7K lines |
| **Platform support** | NVIDIA only | NVIDIA + AMD |
| **Pipeline safety** | Manual (forget `.commit()` → hang) | Compile-time (context managers) |
| **Error messages** | C++ template archaeology | Line number + fix suggestion |
| **Control flow** | Restricted in DSL | Full (break, return, etc.) |

And here’s actual data from our updating our SM100 matmul kernel to use structured components:

| Metric | Conventional approach | Structured Mojo Kernels | Change |
| --- | --- | --- | --- |
| Total lines | 14,683 | 7,634 | **-48%** |
| Main kernel | 3,721 | 1,843 | **-50%** |
| Performance | ~1770 TFLOPS | ~1770 TFLOPS | **Equal** |

We cut the code nearly in half while maintaining identical performance. The compiled output is indistinguishable from a hand-written kernel so there is no abstraction overhead.

The payoff compounds when you build new kernels. Our SM100 conv2d required only ~130 lines of conv-specific code (an im2col tile loader and shared memory layout) while reusing the entire matmul infrastructure: pipelines, MMA warp context, epilogue, scheduler, and output writer. The CUTLASS equivalent is a [separate 870-line kernel](https://github.com/NVIDIA/cutlass/blob/main/include/cutlass/conv/kernel/sm100_implicit_gemm_tma_warpspecialized.hpp) largely duplicated from their matmul kernel. That's the difference between separation of concerns and copy-paste.

When you do need to go lower, when a specific kernel demands something the structured components don't express, Mojo lets you. Nothing in this architecture prevents you from writing directly to the hardware. The difference is that you'll rarely need to, and when you do, you'll be modifying a codebase that's half the size and considerably easier to reason about.

## What's next

This post introduced the architecture and the motivation. The next three posts get into the specifics:

- [**Part 2: The Three Pillars.**](https://www.modular.com/blog/structured-mojo-kernels-part-2-the-three-pillars) TileIO, TilePipeline, and TileOp explained with real code: how each component works, why the interfaces are designed the way they are, and how they compose into a complete kernel.
- [**Part 3: Composition in Practice**](https://www.modular.com/blog/structured-mojo-kernels-part-3-composition-in-practice)**.** Extending the architecture for conv2d, block-scaled matmul, and other demanding kernel variants.
- [**Part 4: Portability and the Road Ahead**](https://www.modular.com/blog/structured-mojo-kernels-part-4-portability-and-the-road-ahead)**.** How the same structured patterns map onto NVIDIA Blackwell and AMD MI300X, and what changes when the underlying hardware does.

## TL;DR

- **Production GPU kernels are hard to write and harder to maintain.** Modern hardware demands explicit software orchestration of pipelines, barriers, and memory. Existing frameworks respond with enormous complexity.
- **Structured Mojo Kernels separate concerns.** TileIO, TilePipeline, and TileOp each own one responsibility with clean interfaces between them. Changes stay localized. New kernel variants compose from existing components.
- **Context managers eliminate synchronization bugs.** The `with` blocks that manage pipeline transitions make incorrect ordering unrepresentable in source code.
- **Zero-cost abstractions are real.** Mojo’s compile-time metaprogramming and RAII patterns make the structure disappear at runtime. 48% less code, identical performance.
- **Lightweight, portable, and open.** ~7K lines of library code, runs on NVIDIA and AMD, available in the [Modular repository](https://github.com/modular/modular).

## Read more from Modular

View all blogs

Modular and Qualcomm: Same code, new silicon

August 18, 2026

Why LLM Inference Needs a New Kind of Router - Part 3

June 5, 2026

Three trends from MLSys 2026

May 29, 2026

Build the future of AI with Modular

Get started - FREE

View Editions

- ![Person with blonde hair using a laptop with an Apple logo.](https://cdn.prod.website-files.com/68c9c3107effc2ea46e1a81f/68cc733ff9050921bab7782c_emoji-dev.png)Sign up todaySignup to our Cloud Platform today to get started easily.[Sign Up](https://docs.modular.com/max/get-started)
- ![Magnifying glass emoji with black handle and round clear lens.](https://cdn.prod.website-files.com/68c9c3107effc2ea46e1a81f/68cc733fb111718bbd49ca31_emoji-zoom.png)Browse open modelsBrowse our model catalog, or deploy your own custom model[Browse models](https://www.modular.com/models)

## Sign up for our newsletter

Get all our latest news, announcements and updates delivered directly to your inbox. Unsubscribe at anytime.

Thanks for signing up to our newsletter! 🚀

Thank you,

Modular Sales Team

Oops! Something went wrong while submitting the form.
