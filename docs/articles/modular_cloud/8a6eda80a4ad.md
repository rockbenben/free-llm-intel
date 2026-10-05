---
vendor: modular_cloud
title: Blackwell 上的矩阵乘法（二）：用硬件特性优化 Matmul
original_title: Modular: Matrix Multiplication on Blackwell: Part 2 - Using Hardware Features to Optimize Matmul
url: https://www.modular.com/blog/matrix-multiplication-on-nvidias-blackwell-part-2-using-hardware-features-to-optimize-matmul
date: 2025-09-05
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Blackwell 上的矩阵乘法（二）：用硬件特性优化 Matmul

> 🛠️ 本系列提到的所有内核代码都已在 GitHub 上开源。

本篇继续我们的旅程，把性能提升到最初内核基准的 50 倍以上。过程中我们会讲解更多 GPU 编程概念，并利用 Blackwell 的新特性。注意这并不是系列的终点，后续博客还会在本篇方法的基础上继续改进。

第 2 篇的性能改进路线图

为了简化问题，我们只看一种特定形状的 matmul：`A` 矩阵为 `MxK`，`B` 矩阵为 `KxN`（转置存放），结果 `C` 矩阵为 `MxN`，且 `M=N=K=4096`。整个系列都假设这一形状；在最后一篇中我们会展示这些技术如何推广到任意形状。

回想我们之前的 4 行 matmul，把镜头拉近看核心计算：

Mojo

acc += a[row, k].cast[DType.float32]() * b[col, k].cast[DType.float32]()

每次融合乘加（FMA）运算需要两次[全局](https://docs.modular.com/glossary/gpu/memory)加载和一次内存写。全局内存的问题是：虽然容量充足，但比其他存储要慢得多。因此，优化 matmul 的功夫就在于如何利用 GPU 上的[存储层次](https://en.wikipedia.org/wiki/Memory_hierarchy)，来避免或隐藏访存操作。下图直观展示了本系列将用到的各类操作的延迟。

🔥 怎样让你的内核在这张图上尽可能靠右？[来源：

Intro to GPUs

]

退后一步看，我们可以给每个线程分配一种颜色，把 4 行 matmul 的访存可视化，看看每个线程如何从输入矩阵读取数据。

4 行 matmul 中各线程的访存情况

- 线程 0 计算 C[0, 0]，读取 A 的第 0 行和 B 的第 0 列
- 线程 1 计算 C[0, 1]，读取 A 的第 0 行和 B 的第 1 列
- 线程 2 计算 C[1, 0]，读取 A 的第 1 行和 B 的第 0 列
- 线程 3 计算 C[1, 1]，读取 A 的第 1 行和 B 的第 1 列

仅考虑这 4 个线程，每个线程为了算一个输出值就要加载一整行和一整列。把 4 个线程的访存加起来，每一行和每一列的加载都重复了两次。这些观察指向了我们可以做的第一项改进：减少缓慢的全局内存访问。

## 共享内存

减少重复加载的一个常用技术叫[循环分块](https://en.wikipedia.org/wiki/Loop_nest_optimization)（loop tiling）。思路很简单：把矩阵的一小块 tile 加载到快得多的缓存里，处理器就可以在这块数据上完成所有必要计算，而不必反复回到缓慢的主存。一块算完，再加载下一块。

我们用共享内存当缓存。Blackwell 每个 SM 有 228KB 共享内存，意味着我们*可以*在多个线程之间共享数据、跨整个块做分块。具体做法：

矩阵乘法的循环分块

我们把矩阵划分为 tile：矩阵 `A` 划分为 `BMxBK` 的 tile，矩阵 `B` 划分为 `BNxBK` 的 tile，其中 `BMxBNxBK=64x64x64`。可选的数值及其约束以后讨论，现在就把它们当作 `4096x4096` 方阵上的 tile。目前唯一要记住的约束是：tile 不能超过共享内存的容量。

在 `K/BK` 循环的第一次迭代中，我们从矩阵 `A` 加载一个 `BMxBK` 的 tile，从矩阵 `B` 加载 `BNxBK` 的 tile。这肯定放得进共享内存——两个 `64x64` 的 tile，即 `8192` 个 2 字节元素，每个块大约需要 16KB，远小于可用的 228KB。然后对这个 tile 执行矩阵乘累加（MMA）运算，把结果作为中间值保存：

用循环分块执行矩阵乘累加

第二次迭代，我们把下两组 chunk 加载进共享内存，并把这次 MMA 的结果**加**到上一次迭代的结果上。如此重复 K/BK 次（在我们的例子里是 256 次），直到算出最后一个 tile。K/BK 循环结束后，我们就得到了最终的输出 tile，该 tile 的最终结果可以**只写一次**到全局内存。

将最终结果写入全局内存

思路草图已完成，现在进入我们改进后的第二个 matmul 内核。

## 内核 2：TMA 与 Tensor Core

本节开发下一个内核。Kernel 2 比最初的内核更高级，同时使用分块和 Tensor Core 来优化。可跟随[这里的代码](https://github.com/modular/modular/blob/main/max/kernels/test/gpu/linalg/matmul_blackwell_iterative/2_tensor_core.mojo)。大致的伪代码逻辑如下：

Mojo

kernel_setup()

for i in range(K // BK):
  load_tiles_ab()               # leader thread loads A and B tiles
  issue_mma_axb()               # leader thread issues MMA(A x B)

transfer_c_tile_to_registers()    # move final C tile from tmem to registers
write_c_tile_to_global_memory()   # store C tile from registers to gmem

我们把 `B` 矩阵按转置形式存储，以保证访问时的内存合并布局。这可以通过 [Layout](https://docs.modular.com/mojo/kernels/layout/layout/) 变换完成：

Mojo

alias a_layout = Layout.row_major(M, K)
alias b_layout = Layout.row_major(N, K) # Transposed
...

内核确实需要改动一些主机侧的设置，我们会循序渐进地解释这些改动。

### 1 —— 把 tile 加载进共享内存

NVIDIA Hopper 架构引入了张量内存加速器（TMA），这是一个专门的硬件单元，可在 GPU 的全局内存（GMEM）和共享内存（SMEM）之间异步搬运数据。

要用 TMA，我们需要先在主机上创建一个[张量 tile](https://docs.modular.com/mojo/kernels/layout/tma_async/create_tma_tile)（tensor map），再把它传给内核。tensor map 是一个 128B 的数据块，编码了输入张量的形状、步长和全局内存地址。（它还能编码一个*swizzle 模式*，这是我们稍后要讨论的优化。）在 Mojo 中用提供的 [API](https://docs.modular.com/mojo/kernels/layout/tma_async/) 创建 TMA tile 很简单：

Mojo

# Rank 2 matrix
# A/B tiles in shared memory have shapes BMxBK and BNxBK, respectively
a_tma_op = create_tma_tile[
  a_type, 2, Index(BM, BK)
](ctx, a_global_mem_address)

b_tma_op = create_tma_tile[
  b_type, 2, Index(BN, BK),
](ctx, b_global_mem_address)

在内核中使用 TMA 对象的方式如下：

Mojo

alias num_iters = K // BK

for i in range(num_iters):
  # One a single thread launches the TMA async copy.
  if elect_one_thread:
    tma_mbar[0].expect_bytes(expected_bytes)

    a_tma_op.async_copy(
      a_smem_tile,  # shared memory tile containing the address
      tma_mbar[0],  # barrier to guard the copy is finished
      (i * BK, block_idx.y * BM),  # tile's coordinate in the input.
    )
        
    b_tma_op.async_copy(
      b_smem_tile,
      tma_mbar[0],
      (i * BK, block_idx.x * BN),
    )
  # All threads wait for the copy to finish.
  tma_mbar[0].wait(tma_phase)
  tma_phase ^= 1

从高层看，由一个线程（`elect_one_thread`）发起异步拷贝，并用内存屏障（`tma_mbar`）保证拷贝完成。我们逐个来看。

`a_tma_op.async_copy` 接受三个参数：

- `a_smem_tile:` 提供 tile 共享内存地址的 `LayoutTensor`
- `tma_mbar:` 用于跟踪已传输数据量的内存屏障
- `(i * BK, block_idx.y * BM):` 当前 tile 在全局内存中的坐标，取决于迭代次数和块坐标（参见[第 1 篇](https://www.modular.com/blog/matrix-multiplication-on-nvidias-blackwell-part-1-introduction)）

#### 为什么需要 TMA 屏障

TMA 操作是异步的，所以我们必须有某种机制确保在所有 tile 完全进入共享内存之前，MMA 不能继续。这就是使用内存屏障（`mbar`）的原因：线程会在屏障上等待/阻塞，直到 tile 拷贝到共享内存为止。

具体做法是每个线程各自持有一个屏障阶段值（`tma_phase=0`），内存屏障*自身*的内部阶段值也初始化为 `0`。当线程的阶段值与屏障的阶段值相同时，线程无法解锁屏障，也无法通过；只有当两者不同时，线程才能继续。

Mojo

tma_mbar[0].wait(tma_phase)

上面的代码会让线程阻塞，执行轨迹是这样的：

TMA 屏障造成线程阻塞的示意

在 TMA 传输开始之前，屏障要先通过 `tma_mbar[0].expect_bytes(expected_bytes)` 初始化预期接收的字节数。expected_bytes 是两个被传输 tile 的总字节数。

Mojo

alias a_expected_bytes = a_size * sizeof[a_type]()
alias b_expected_bytes = b_size * sizeof[b_type]()
alias expected_bytes = a_expected_bytes + b_expected_bytes

TMA 会持续向屏障更新已传输的字节数，一旦已传字节数达到总字节数，屏障的阶段值就会翻转，线程得以继续。

TMA 屏障的阶段翻转

然后我们通过 `tma_phase ^= 1` 手动翻转每个线程的 `tma_phase`，确保下一轮迭代中线程会阻塞，直到 TMA 把*这一*迭代的 tile 搬进共享内存。

手动翻转 TMA 屏障阶段

Mojo 确实提供了抽象，帮你隐藏更多 TMA 细节和优化技巧。举个例子：如果我问你 `a_tma_op` 的布局是什么，你会怎么回答？

> 💭 我们说过 tile 是 BM x BK，如果 BM 是 64、BK 是 64，那么 ((shape), (stride)) 元组就是 ((64, 64):(64, 1))，因为它是 Row-Major/K-Major。

你答对了！那如果问题是：TMA 单元要搬运我们这个 `64x64` 的 tile，需要发起多少次取数？

> 💭 既然声明的是 64x64 布局，那显然是一次。

很遗憾，这次你错了。实际上需要 8 次。虽然我们指定的逻辑 tile 大小是 `64x64`，但 TMA 硬件会把 `64x64` 的 tile 划分为八个 `64x8` 的子 tile，逐个加载。要解释为什么必须这样做，就得引入"core matrix（核心矩阵）"。

#### Core matrices

TMA、Tensor Core 乃至整个 NVIDIA GPU 有一个隐藏的讲究：core matrix。

概念很简单。Tensor Core 不认识*元素*，只认识*矩阵*。在它眼里，矩阵只能被看作一组 `8x16B` 的 tile——也就是 `8x8` 元素的 core matrix。

Tensor Core 的矩阵

`tcgen05.mma` 在共享内存中[支持](https://docs.nvidia.com/cuda/parallel-thread-execution/#asynchronous-warpgroup-level-matrix-shared-memory-layout) 8 种 core matrix 的标准布局（继承自 WGMMA），取决于布局（行主序或列主序）和 swizzle 模式。我们当前的内核对 `A` 和 `B` 都使用 K-major，对应的布局要求每列 core matrix（`8x1`）在共享内存中必须连续。这就是描述符布局显示 `(64, 8)` 的原因——TMA 一次拷贝一列 8 个 core matrix，这样的操作要重复 8 次才能填满 tile 的 64 元素宽度。

把 8 列 core matrix 拷贝 8 次

当然，我们 Mojo 库的 `async_copy` 把这一复杂性抽象掉了：程序员只需发出一次拷贝，就能等着 tile 出现在共享内存里。

### 2 —— 发射 MMA 指令

简单回顾：Blackwell 引入的第五代 Tensor Core 带来了一组新指令（`tcgen05` 指令），以及 MMA 运算的三项根本改进：

- 单 SM 最大 `tcgen05.mma` 形状提升到 `128×256×16`，对比 Hopper 上此前的 `64x256x16`，吞吐近乎翻倍。
- 引入了 2SM 的 `tcgen05.mma`，最大可达 `256x256x16`（2SM 操作会在本系列后续博客中解释）。
- 通过引入一种新的存储——Tensor Memory——降低了寄存器压力。`tcgen05.mma` 指令可以把结果存到 Tensor Memory 而不是寄存器里。那 Tensor Memory 是什么？

#### 什么是 Tensor Memory？

Blackwell 还有一项改进，我们在系列第一篇中简要提过，那就是 Tensor Memory（TMEM）。

Tensor Memory（TMEM）

TMEM 是一块 256K 的片上存储，专门存放 `tcgen05` MMA 指令的输入或输出。它有 128 条 lane、512 列，共 65,536 个元素，每个元素 4 字节，总计 256KB。分配以列为单位，粒度是 32 列，也就是说一次最少分配 32 列（16k 字节）。

在之前的 NVIDIA 架构世代，matmul 结果只能放在通用寄存器里，这带来几个问题：

- 寄存器空间稀缺，每个 SM 只有 64k 个寄存器，Tensor Core 和通用 ALU 之间存在争用。
- 寄存器是线程私有的，而在 Blackwell 之前的 GPU 上 MMA 是 warp 级操作。因此发起 MMA 的 warp 必须等待其完成，才能继续依赖 MMA 结果的任务（如 epilogue）。

TMEM 解决了这些问题，把 ALU 使用的寄存器与 Tensor Core 需要的存储分离开来。

我们在代码中使用 `tcgen05.mma` 和 tensor memory 的方式：

Mojo

for i in range(num_iters):  
  load_tiles_ab()  #section 1 
  if elect_one_thread:
    @parameter
    for j in range(num_k_mmas):
      alias idx = IntTuple(0, MMA_K * j)
      alias a_offset = a_smem_layout(idx) * sizeof[a_type]()
      alias b_offset = b_smem_layout(idx) * sizeof[b_type]()

      # Use c_scale=0 for the first mma to initialize results and use 
      # c_scale=1 subsequently to accumulate resutls.
      var c_scale_value: UInt32 = 0 if (i == 0 and j == 0) else 1
      mma(
        adesc + a_offset,
        bdesc + b_offset,
        tmem_addr,
        idesc,
        c_scale=c_scale_value,
      )

    mma_arrive(mma_mbar)

  mma_mbar[0].wait(mma_phase)
  mma_phase ^= 1

`tcgen05.mma` 指令是异步执行的，和 TMA 操作类似——由单个线程发起、由内存屏障守护。区别在于这里我们用 `mma_arrive`，它包装了 `tcgen05.commit`，动态地给内存屏障发信号并与 MMA 指令关联。

注意我们发射了 `num_k_mmas` 条 MMA 指令（而不是把 `A`、`B` 两个 tile 一次性喂给 Tensor Core 相乘）。原因是 `BM×BN×BK` 的分块还不够——真实的硬件指令有尺寸限制。`tcgen05.mma` 要求 K 维度为 32B（对 BF16/FP16 来说就是 16 个元素）。因此当 `BK = 64` 时，MMA 需要 4 次迭代。

BK=64 时 MMA 需要 4 次迭代

没错，这意味着我们在采用嵌套分块策略。MMA 函数调用 `tcgen05.mma` 指令，把结果累加到地址 `tmem_addr` 处的 tensor memory 中。分配 tensor memory 需要执行：

Mojo

# allocate all 2^18 bytes of smem for tcgen05, all 512 cols allocated
  if elect_one_warp:
    tcgen05_alloc(ptr_tmem_addr, max_tmem_cols)

  # Ensure all threads see initialized mbarrier and
  # tensor memory allocation
  barrier()

  tmem_addr = ptr_tmem_addr[0]

这个分配其实相当不直观。首先，分配必须由单个 warp（而不是单个线程）发起。其次，我们还要绕道共享内存才能拿到分配好的 `tmem` 地址。

`tcgen05.mma` 的输入和配置都编码在描述符里：

- **指令描述符**（`idesc`）：编码指令形状、数据类型、矩阵布局等。这个描述符在迭代间不变，因为这些属性在整个计算过程中保持恒定。
- 共享内存描述符（`adesc` 和 `bdesc`）：编码矩阵 `A` 和 `B` 的共享内存布局与访问模式。这些描述符会变，会在 `num_k_mma` 次迭代中递增，因为随着遍历矩阵的不同 K 切片，共享内存地址在变化。

> 📚 更深入的细节见附录。

MMA 完成后，它会在 MMA 屏障上"到达"。机制与 TMA 屏障基本相同，阻塞所有线程直到 MMA 操作完成。这样，在当前 tile 的所有 MMA 操作完成之前，没有任何线程会进入下一轮迭代去发起 TMA 操作。

### 3 —— TMEM → 寄存器

到这里，两个主要函数我们已经覆盖了：

Mojo

for i in range(K // BK):
  load_tiles_ab()              # leader thread loads A and B tiles
  issue_mma_axb()              # leader thread issues MMA(A x B)

结果已经累加并存在 tensor memory 里。下一个问题是：怎么把它从 tensor memory 搬到全局内存？

从 tensor memory 搬运数据的唯一途径是先搬到寄存器。这可以通过 `tcgen05_ld` 操作完成：

Mojo

c_frag = tcgen05_ld[
  datapaths=16,
  bits=256,
  repeat = BN // 8,
  dtype=accum_type,
  pack=False,
  width=c_frag_size,
](tmem_addr)

tcgen05_load_wait()  # wait for the load to finish

这条指令相当复杂，我们拆开看。查阅数据在 tensor memory 中的存放方式文档，会注意到 tensor memory 存的是一个 `64x64` 的 C_tile。按照 NVIDIA [Parallel Thread Execution ISA Version 9.0](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html) 的 [Figure 215](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html?highlight=tcgen05%2520mma#tcgen05-data-path-layout-f1)，其布局组织和访问模式如下：

Tensor Memory 的布局组织与访问模式

所以要访问这块内存，我们启动的块中每个 warp 需要读出 16 条 lane，整个 warp-group（4 个 warp）读出 64 条 lane。参数（datapaths 和 bits）指定了这一加载模式，`tcgen05_ld` 内部会分派 `tcgen05.ld.16x256b` 指令来加载每一组 lane。

也就是说，每次迭代线程沿 tensor memory 的列加载 256 位、即 8 个元素（不是 16 个——还记得第一篇说过我们用 FP32 累加以保证精度，因此每个元素在 tensor memory 中占 4 字节），共进行 `BN/8` 次迭代。这意味着 warp 中 32 个线程里的每一个必须持有 4 个元素（见 [Figure 185](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html?highlight=tcgen05%2520mma#tcgen05-mma-fragment-16128b)）。

把这一过程重复 `BN//8 = 8` 次，每个线程就在寄存器数组中持有 tile 的 32 个元素。完成后，我们就成功把所有数据搬进了寄存器，接下来释放之前分配的 tensor memory。

Mojo

if elect_one_warp:
  tcgen05_release_allocation_lock[1]()
  tcgen05_dealloc[1](tmem_addr, max_tmem_cols)

### 4 —— 寄存器 → GMEM

从代码上看，我们现在到了这里：

Mojo

setup_kernel()

for i in range(K // BK):
  load_tiles_ab()              # leader thread loads A and B tiles
  issue_mma_axb()               # leader thread issues MMA(A x B)

transfer_c_tile_to_registers()    # move final C tile from tmem to registers

还差关键一步：`write_c_tile_to_global_memory`，把数据从寄存器写入全局内存。要搬数据，先确定要写到*哪里*。我们的矩阵是 `4096x4096`，每个块负责输出的一个 `64x64` tile。假设把注意力放在 `block_idx.y = 2, block_idx.x = 2` 上，它负责输出第 3 行的第 3 个 tile：

输出第 3 行的第 3 个 tile

我们用 `LayoutTensor.tile()` 方法从输出矩阵中切出一个 tile：

Mojo

ctile = c.tile[BM, BN](block_idx.y, block_idx.x)

再按 warp 进一步分块：

Mojo

c_gmem_warp_tile = ctile.tile[BM // num_warps, BN](warp_id, 0)

为每个 warp 划分输出矩阵

聚焦 warp 0 的 tile，看看会发生什么。`tile 0` 的 `c_gmem_warp_tile` 对应前 16 行乘 64 列（`16xBN`），由于累加值就存在 warp 0，我们需要把这个 16x64 的 tile 映射给 `warp 0`。下图展示了 [`tcgen05.ld.16x256`](https://docs.nvidia.com/cuda/parallel-thread-execution/#tcgen05-matrix-fragments-shape-16256b) PTX 指令下元素如何映射到 lane（线程）：

tcgen05.ld.16x256 PTX 指令的元素-线程映射

涉及不少索引计算。要是有办法为 warp 的 tile 创建视图——一个个小"口袋"——让每个线程恰好拿到它放数据所需的布局，那该多好？Mojo 就提供了这样一个库函数，可以简洁地做到：

Mojo

c_gmem_frag = c_gmem_warp_tile.vectorize[1, 2]().distribute[
  Layout.row_major(8, 4)
](lane_id())

对于第一次接触 LayoutTensor 的读者，这可能有点复杂，我们来可视化 `thread 0` 的视图。代码的第一部分意识到：既然每个线程存 2 个连续元素，`16x64` 的 tile 可以看作 `16x32` 的 tile，每个位置是一个 2 元素向量：

16x64 的 tile 可视为由 2 元素向量组成的 16x32 tile

接下来 `.distribute[Layout.row_major(8, 4)]` 把 `16x32` 个向量按 `8x4` 的线程布局循环分派，如下所示。

偏移量按 `row_major(8, 4)(lane_id())` 计算。例如，`thread 0` 在每个子矩阵中都拿到 `(0, 0)` 处的向量（绿色格子），`thread 6` 同理拿到 `(1, 3)` 处的向量（下图中蓝色格子）。事实上，每个子矩阵与 NVIDIA [Figure 185](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html?highlight=tcgen05%2520mma#tcgen05-mma-fragment-16128b) 的布局一一对应：

子矩阵映射

最终形成 2x8 个子矩阵，每个子矩阵存 `8x4` 个 2 元素向量。而且 `distribute` 如约给了每个线程所需"口袋"的视图。

distribute 操作与 NVIDIA 映射的对比

有了这个映射，向全局内存的输出就只是简单循环的事：

Mojo

alias num_vecs_m = c_gmem_frag.shape[0]()
alias num_vecs_n = c_gmem_frag.shape[1]()

@parameter
for n_vec in range(num_vecs_n):
  @parameter
  for m_vec in range(num_vecs_m):
    alias i_vec = n_vec * num_vecs_m + m_vec
    c_gmem_frag[m_vec, n_vec] = [c_frag[2 * i_vec], c_frag[2 * i_vec + 1]]

以 `num_vecs_n, num_vecs_m=(8,2)` 为例，意味着每个 warp 一次写出一个子矩阵：先在 `M` 维度上写 2 次，再在 `N` 维度上写 8 次。下面是循环执行过程的速览：

迭代 n_vec=0, m_vec=0，单个 warp

迭代 n_vec=0, m_vec=1，单个 warp

迭代 n_vec=1, m_vec=0，单个 warp

最后一次迭代 n_vec=7, m_vec=1

以上是单个 warp 的情况。把镜头拉远到 CTA 级别，可以把 CTA 的 tile 映射到全局内存中的 `C` 矩阵：

CTA tile 到全局内存中 C 矩阵的映射

### 5 —— 为以上所有准备工作设置共享内存

在看怎么设置共享内存之前，先看看 SM 上我们的共享内存布局长什么样——也就是前面一直跳过的 `setup()` 阶段。共享内存主要用于输入 tile、内存屏障和 TMEM 分配。

Mojo

var a_smem = external_memory[Scalar[a_type],
															address_space = AddressSpace.SHARED]())
# Offset BMxBK for A tile												
var b_smem = (a_smem + a_size).bitcast[Scalar[b_type]]()
# Offset BNxBK for B tile
var tma_mbar = (b_smem + b_size).bitcast[Int64]()
# Offset 8B for tma memory barrier
mma_mbar = tma_mbar + 1
# Offset 8B for mma memory barrier
ptr_tmem_addr = mma_mbar + 1

上面的设置代码从动态共享内存分配（`external_memory`）拿到基地址，然后按下图所示逐步向后偏移。

async_copy() 操作把 tile 块拷贝到共享内存

把所有内容拼在一起并对这个内核做基准测试，我们得到 155.0 TFLOPS，比朴素内核**提升了 28 倍**。但要客观看待：**该内核性能仍只有 cuBLAS 的 8.7%**。

TMA 与 Tensor Core 优化的性能

## 内核 3：swizzling

Kernel 2 的一项开销是为加载输入 tile 发起多次 TMA 调用。回顾一下，原因就在于 `BK=64`，而 Tensor Core 需要的标准布局一次只允许沿 K 拷贝 16B。其他布局支持每次拷贝更大的 `K` 维度，例如最宽的 128B 布局。CUTLASS 的一段[注释](https://github.com/NVIDIA/cutlass/blob/b2dd65dc864e09688245b316ac46c4a6cd07e15c/include/cute/atom/mma_traits_sm100.hpp#L197)是最好的说明：

C++

# T = 16B // sizeof(datatype) = 8 for BFloat16
Swizzle

<

3,4,3> o smem_ptr o ((8,m),(T,2)):((8T,SBO),(1, T ))

这段式子表明：只要配上 `Swizzle<3, 4, 3>`，我们确实可以用单个行主序 tile `BMxBK`、`BK = 64`（见式中的 `8T`）。那 swizzle 是什么？`<3, 4, 3>` 这组神奇数字又是怎么回事？要弄清楚，先复习一下共享内存。

Kernel 3 的代码在[这里](https://github.com/modular/modular/blob/main/max/kernels/test/gpu/linalg/matmul_blackwell_iterative/3_swizzling.mojo)。

### 共享内存组（bank）

共享内存由 32 个连续的 4B 宽 bank 组成：

共享内存布局：32 个连续的 4B 宽 bank

共享内存中每个 bank 每周期可以服务一个请求，访问不同 bank 的多个线程可以在同一周期内同时被服务。也就是说，`bank 0` 服务 `thread 0` 的同时，`bank 16` 可以服务 `thread 1`：

多线程在同一周期访问不同 bank

### Bank 冲突

那如果两个请求访问同一个 bank 呢？比如两个线程都要访问 `bank 0` 的不同地址——假设 `thread 1` 现在想访问第 3 行第 0 列的元素。

两个线程访问同一 bank 造成 bank 冲突

这就要花 2 个周期。`Bank 2` 先服务 `thread 0`，一个周期后再服务 `thread 1`。从直觉上也说得通：为了最大化吞吐，GPU 被设计成每周期最多加载 128B——一次扫过所有 bank（32 个 bank × 每 bank 4B）。对同一 bank 的第二次加载就得安排到后面的周期。

回想一下，指令是以 warp 为单位发射的。当一个 warp 内的线程访问映射到同一 bank 的不同地址时，硬件必须把执行拆成多个周期。这种执行停顿就叫 bank 冲突，它对性能的危害不言而喻。

把上述分析套到 128B 标准布局上（即 tile 为 `BMxBK` 且 `BK=64`），第一个 core matrix 的 8 行全部映射到相同的 bank `0-3`。

8 路 bank 冲突

这会让每个 core matrix 产生 8 路 bank 冲突，每行的写入只能顺序进行。显然，我们需要一种技术，在读取所需数据时不被 bank 冲突拖住。

### Swizzling

Swizzling 就是解决 bank 冲突的技术。它利用按位 `xor`（^）交换索引，让数据不再落在同一个 bank 上。举个例子说明 swizzle，为简单起见假设有 16 个 bank。

`Row 0` 保持不动，`^00:`

`Row 1`：用 `^01` 翻转相邻对 `(0↔1, 2↔3, 4↔5, ...):`

`Row 2`：用 `^10` 翻转"对的对" `(01 ↔23, 45↔67)`:

`Row 3`：用 `^11` 每四个一组整体取反:

注意，不同行上相同的索引 `(1-16)` 已被换到了不同的 bank。也就是说，当线程按相同索引访问不同行的元素时，不会产生 bank 冲突。

#### 128 字节 swizzling

来解读 `<3, 4, 3>` 这个 128B swizzle 模式。第一个 `3` 对应 `2^3 = 8`：core matrix 的行数。`4` 对应 `2^4 = 16B`（core matrix 的宽度，8 个元素 × 2B）。最后一个 `3` 是 `2^3 = 8`，意味着 8 个 16B 的 chunk 正好铺满 32 个 bank（128B）。有了这些值，swizzle 函数就能给出正确的 `xor` 模式，消解 core matrix 的 bank 冲突。这个模式[可以用 Mojo 写出](https://github.com/modular/modular/blob/ee9ecef5f25a708bb58a5b83add273decc407c01/max/kernels/src/layout/swizzle.mojo#L325-L328)，并且[可推广到常见模式](https://github.com/modular/modular/blob/ee9ecef5f25a708bb58a5b83add273decc407c01/max/kernels/src/layout/swizzle.mojo#L542C1-L554C8)。可视化效果如下：

128 字节 swizzle 模式

每 8 个元素（`16B = 8*2B`）为一组，方法是在 `xor` 操作数中把低 3 位清零。`xor` 运算像我们之前展示的那样在每行内交换这些组。结果就是每 8 个元素分布在不同 bank 上，并如下图所示持续下去：

经过 128 字节 swizzle 的共享内存 tile

完整的数学细节见附录。看看相邻两个 core matrix 如何被 swizzle 到 32 个 bank 上：

无 swizzle 的内存访问

加上 swizzle 后，上面的情形变成：

有 swizzle 的内存访问

同一 core matrix 中的任意两个元素绝不会落在同一个 bank——因为 core matrix 宽 16 字节，所以在 128 字节 swizzle 下没有 bank 冲突。

> 🍭 这就是 swizzling 极其有用的原因，每个高性能 GPU 内核都会用它。

### 更新后的内核

内核的代码改动很小，因为 [swizzling](https://en.wikipedia.org/wiki/Swizzling_(computer_graphics)) 的支持来自库的 layout tensor 和指令本身。唯一需要的改动是告诉 TMA 和 `tcgen05.mma` 采用哪种 swizzle 模式：

Mojo

alias a_swizzle = TensorMapSwizzle.SWIZZLE_128B
alias b_swizzle = TensorMapSwizzle.SWIZZLE_128B
    
#for the tma, used on writing in data from global memory
alias a_smem_layout = tile_layout_k_major[
  a_type, BM, BK, swizzle_mode=a_swizzle
]()
alias b_smem_layout = tile_layout_k_major[
  b_type, BN, BK, swizzle_mode=b_swizzle
]()

#for the mma
adesc = MMASmemDescriptor.create[aSBO, aLBO, a_swizzle](a_smem_tile.ptr)
bdesc = MMASmemDescriptor.create[bSBO, bLBO, b_swizzle](b_smem_tile.ptr)

由于 `LayoutTensor` 理解 swizzling，swizzle 操作的细节可以完全藏在 layout tensor API 后面，代码保持简洁。

### 性能

有了以上优化，我们在 B200 上达到 288.3 TFLOPs（提升 87%）。换句话说，共享内存 bank 冲突的影响几乎让性能腰斩；而解决 bank 冲突后，我们达到了 cuBLAS 的 16.4%，差距正在快速缩小。

加入 swizzling 后的性能提升

## 内核 4：在共享内存中打包输出并使用 TMA store

上一个内核的输出阶段，我们每次向全局内存写两个连续的 BF16 值，即每次 store 只有 4B——而 Blackwell 的单条 store 指令（`st.global.v8.b32`）最多支持 32B，这个写入粒度相当小。此外，我们可以用 TMA 一条指令存整个输出 tile，减少发射的指令数。Kernel 4 的[代码在这里](https://github.com/modular/modular/blob/main/max/kernels/test/gpu/linalg/matmul_blackwell_iterative/4_tma_stmatrix.mojo)。

### 在共享内存中打包输出

要利用 TMA store，需要先把输出数据打包进共享内存。做法是在把输出从 tensor memory 读到寄存器后，先把寄存器拷贝到共享内存。由于全局内存中的输出是 BF16，拷贝到共享内存之前必须把寄存器从 FP32 转成 BF16。

但是，输出结果按特定布局分散在各寄存器中（`16x256` 位加载，见 TMEM→寄存器一节），把寄存器拷贝到共享内存时必须处理这种分布。幸好 NVIDIA 提供了 `stmatrix` 指令来简化这一步。`stmatrix` 指令可以把 8x16B 的 core matrix 按 16x256 位的精确布局存入共享内存，并且用户可以灵活指定每行在共享内存中的地址。256 位（32B）与每行 16B 之间看似有矛盾——其实是因为从 TMEM 读出的数据是 FP32，存进共享内存时才转成 BF16。`stmatrix` 指令单条最多可存四个 core matrix（2x2）。因此，打包 `16x64 (BN=64)` 的 warp tile 需要 `stmatrix` 迭代四次。

stmatrix 的四次迭代

注意，写入共享内存时仍会遇到 bank 冲突，所以我们用 128B swizzling（`BN * 2B = 128B`）来规避冲突。

### TMA store

数据完成 swizzle 并打包进共享内存后，就可以发起 TMA store 操作，异步把数据写回全局内存。下面的代码展示了 TMA store 及其同步处理方式。在 TMA 发出异步 store 之前，先通过 `fence_async_view_proxy` 对内存做 fence，确保先前在共享内存中的打包对 TMA store 可见。

Mojo

# Launch one TMA store per thread
if elect_one_warp and thread_idx.x

<

BN // TMA_BN:
  # memory fence to ensure previous shared memory access 
  # is seen by TMA instruction 
  fence_async_view_proxy()
    c_tma_tile = ...  # setup the tile for tma
    # c_tma_op is created similarly like a_tma_op for loading data
    c_tma_op.async_store(
      c_tma_tile,
      (block_idx.x * BN + thread_idx.x * TMA_BN, block_idx.y * BM),
    )
    # Commit TMA store
    c_tma_op.commit_group()
    # wait for the store to complete
    c_tma_op.wait_group[0]()

发出 TMA store 后，先用 `commit_group()` 提交这些 store。它把自上次 commit 以来到当前程序计数器位置发出的所有 store 归为一组。随后的 `wait_group[N]()` 会等待到最多还剩 `N` 组 store 在途。例如，若已提交 3 组，`wait_group[2]()` 保证第一组已完成、后两组仍在途。在上面这段代码里，`wait_group[0]()` 确保所有 TMA store 都完成。这种按 commit 组等待的能力，让你能在后续优化中构建流水线、高效地把其他任务重叠进来。

TMA store 与 TMA load 还有一个区别：多个线程可以并行发起 TMA store。

Mojo

# Launch one TMA store per thread
if elect_one_warp and thread_idx.x

<

BN // TMA_BN:

这里 `TMA_BN` 取决于 swizzle 模式（例如 128B swizzle + BF16 时 `TMA_BN=64`）。如果 tile 维度 `BN` 更大，就要把该维度除以 `TMA_BN`，发起多个 TMA store。例如 `BN=128` 对应两条 store，如下所示，由两个线程分别发起以最大化并行度。

用两个线程分派两条 TMA store 以最大化并行

### 性能

这个内核的性能基本持平，为 293.6 TFLOPs，精确说还慢了 0.7%。为什么？因为性能从根本上仍受全局内存访问的束缚。

TMA 与 ST_Matrix 优化后的性能

下图是 NCU 给出的计算与内存吞吐。绿色柱是 kernel 3，蓝色柱是 kernel 4。可以看到，两个内核的计算和内存吞吐都很低。

NCU 的计算与内存吞吐剖析

此外，TMA store 真正的威力在于其异步性，可实现流水线与操作重叠。当前内核已经为后续博客中利用这些特性打下了正确的基础。

总结：本篇演示了如何对 matmul 分块，以及如何用最优指令（TMA load/store、`tcgen05.mma`、`stmatrix` 等特性）为 Blackwell GPU 编程。**这些努力让性能相对朴素内核提升了 58 倍**，但仍落后于 cuBLAS。

后续博客将基于本篇的内核继续改进底层调度与执行算法。具体地说，下一篇会展示如何构建 warp 特化流水线，把数据传输与计算重叠，逼近最先进（state-of-the-art）的性能。

## 附录

### 描述符

`tcgen05.mma` 用描述符指定输入数据在共享内存中的布局、指令形状、数据类型等。在 Mojo 中创建 smem 描述符的方式：

`adesc = MMASmemDescriptor.create[aSBO, aLBO, a_swizzle](a_smem_tile.ptr)`

`MMASmemDescriptor` 负责按 `tcgen05.mma` 要求的格式编码所有这些信息。最重要的细节是 `LBO` 和 `SBO`：

- LBO（*leading dimension byte offset*，前导维字节偏移）：K 维度上相邻两个 core matrix 之间的字节数。
- SBO（*stride dimension byte offset*，步进维字节偏移）：`M` / `N` 维度上相邻两个 core matrix 之间的字节数。

在 kernel 2（即未启用 swizzling）中，把 `A` 的这两个值打印出来是：

Mojo

aSBO=128 
aLBO=1024

如下图所示，`LBO` 是 1024B，因为两列 core matrix 之间的距离是 `BM*16B = 1024B`。`SBO` 是 128B，因为每个 core matrix 的大小是 `8x16B = 128B`。

UMMA 描述符 `idesc` 的思路类似，只不过它是 32 位，编码的是稀疏性、数据类型、矩阵是否转置等其他信息。详细编码方式请参考我们的[源代码](https://github.com/modular/modular/blob/386dba7051e1455b145ff2d33bcadfeb971ac7ed/mojo/stdlib/stdlib/gpu/mma_sm100.mojo#L737)。

### Swizzling 的数学

swizzling 的数学定义如下。给定 `Swizzle(bits, base, shift)` 定义的 swizzle：

Mojo

## A generic Swizzle functor
# 0bxxxYYYxxxxZZZxxxx
#                ^--^  Base is the number of least-sig bits to keep constant
#      ^-^    ^-^      Bits is the number of bits in the mask
#        ^------^      Shift is the distance to shift the YYY mask
1) ZZZ is the first mask, extracted right after the base
2) YYY is the second mask, extracted shift after the base
3) We XOR these two, to get AAA=YYY XOR ZZZ
4) We place this new substring in place of the first mask, ZZZ
5) Final answer becomes:
# 0bxxxYYYxxxxAAAxxxx

看 Mojo 的底层代码，swizzle 的实现是：

Mojo

bit_msk = (1

<

<

bits) - 1
self.yyy_mask = bit_msk

<

<

(base + max(0, shift))
self.zzz_mask = bit_msk

<

<

(base - min(0, shift))
swizzled = offset ^ (offset & self.yyy_mask) >> shift

以 128B swizzle 为例，`bits=3`、`base=4`、`shift=3`。按数学含义，我们提取输入地址的第 7-9 位作为掩码，并用它对第 4-6 位做 `xor`，就生成了 kernel 3 中展示的模式：

kernel 3 的 swizzle 模式

读完"Blackwell 上的矩阵乘法"系列全部 4 篇：

[第 1 篇 - 简介](https://www.modular.com/blog/matrix-multiplication-on-nvidias-blackwell-part-1-introduction)

[第 2 篇 - 用硬件特性优化 Matmul](https://www.modular.com/blog/matrix-multiplication-on-nvidias-blackwell-part-2-using-hardware-features-to-optimize-matmul)

[第 3 篇 - 85% SOTA 性能背后的优化](https://www.modular.com/blog/matrix-multiplication-on-nvidias-blackwell-part-3-the-optimizations-behind-85-of-sota-performance)

[第 4 篇 - 突破 SOTA](https://www.modular.com/blog/matrix-multiplication-on-blackwell-part-4---breaking-sota)

[全部篇章](https://www.modular.com/matrix-multiplication-on-blackwell)
