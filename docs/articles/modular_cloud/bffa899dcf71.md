---
vendor: modular_cloud
title: Triton 与 Python eDSL 怎么样？（AI 算力民主化，第 7 篇）
original_title: Modular: What about Triton and Python eDSLs? (Democratizing AI Compute, Part 7)
url: https://www.modular.com/blog/democratizing-ai-compute-part-7-what-about-triton-and-python-edsls
date: 2025-03-26
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Triton 与 Python eDSL 怎么样？（AI 算力民主化，第 7 篇）

AI 编译器受制于一个根本性的权衡：它们为了可用性与可扩展性而抽象掉底层细节，但现代 GenAI 工作负载却要求可编程性与硬件控制力才能达到顶级性能。CUDA C++ 提供了这种控制力，但它出了名的笨重难用。与此同时，AI 开发是在 Python 中进行的——于是业界很自然地尝试把 GPU 编程与 Python 撮合到一起，以弥合这一鸿沟。

但有个问题：Python 无法在 GPU 上运行。为了跨越这个鸿沟，研究者构建了**嵌入式领域特定语言（eDSL）**——基于 Python 的抽象，*看起来*像 Python，但在底层编译为高效的 GPU 代码。想法很简单：让工程师拥有 CUDA 的威力，而不必忍受 C++ 的痛苦。但它真的可行吗？

在本文中，我们将拆解 Python eDSL 的工作原理、优缺点，并仔细看看 **Triton**——这一领域最受欢迎的方法之一——以及其他几个项目。Python eDSL 能同时交付性能与易用性，还是只是通往 AI 算力民主化道路上的又一次绕路？

让我们深入看看。🚀

# 什么是嵌入式领域特定语言（eDSL）？

当某个特定领域拥有能让开发者更高效表达事物的独特方式时，就会使用[领域特定语言](https://en.wikipedia.org/wiki/Domain-specific_language)——最著名的莫过于 HTML、SQL 和[正则表达式](https://en.wikipedia.org/wiki/Regular_expression)。**eDSL**则是一种复用现有语言语法、但借助编译器技术改变代码工作方式的 DSL。从分布式计算（PySpark）到深度学习框架（TensorFlow、PyTorch）再到 GPU 编程（Triton），许多系统都由 eDSL 驱动。

例如，**PySpark** 让用户用 Python 表达数据转换，但会构建一个优化的执行计划，在集群上高效运行。类似地，**TensorFlow** 的 `tf.function` 和 **PyTorch** 的 `torch.fx` 把类 Python 代码转换为优化的计算图。这些 eDSL 抽象掉底层细节，让没有分布式系统、GPU 编程或编译器设计专业知识的人也能更容易地编写高效代码。

## eDSL 是如何工作的？

eDSL 的魔法在于：在 Python 代码运行之前捕获它，并转换成它能处理的形式。它们通常借助**装饰器**——Python 中能在函数运行前进行拦截的特性。当你应用 `@triton.jit` 时，Python 会把函数交给 Triton 而不是直接执行。

下面是一个简单的 Triton 例子：

Python

@triton.jit
def kernel(x_ptr, y_ptr, BLOCK_SIZE: tl.constexpr):
  offs = tl.arange(0, BLOCK_SIZE)
  x = tl.load(x_ptr + offs)
  tl.store(y_ptr + offs, x)

Copy

当 Triton 收到这段代码时，它会把函数解析为一棵**抽象语法树（AST）**，表示函数的结构，包括操作和数据依赖。这种表示让 Triton 能够分析模式、应用优化，并生成执行相同操作的高效 GPU 代码。

借助 Python 既有的语法和工具链，eDSL 的创造者可以专注于构建编译器逻辑，而不必从零设计一门带自己解析器、语法和工具链的全新语言。

## eDSL 的优势

对**构建领域特定编译器的人**而言，eDSL 提供了巨大优势：把语言嵌入 Python 内部，开发者可以专注编译器逻辑，而不必重新发明一整个编程语言。设计新语法、编写解析器、构建 IDE 工具是庞大的工程——利用 Python 已有的语法和 AST 工具，eDSL 创造者跳过这一切，直接着手解决手头的问题。

**eDSL 的用户**同样受益：Python eDSL 让开发者留在熟悉的领地。他们使用同样的 Python IDE、自动补全、调试工具、包管理器（如 `pip` 和 `conda`）以及库生态。他们不必学习 CUDA C++ 这样的全新语言——代码用 Python 写，eDSL 在底层引导执行。

然而，这种便利伴随着显著权衡，会让期望 eDSL 表现得像普通 Python 代码的开发者深感沮丧。

## eDSL 的挑战

当然，天下没有免费的午餐。eDSL 有取舍，有些还令人无比抓狂。

###### **长得像 Python，但它不是 Python**

这是 eDSL 最令人困惑之处。代码*看起来*像普通 Python，但在关键方面*表现*得不像 Python：

Python

# Regular Python: This works as expected
def works():
  kv = dict((i, i * i) for i in range(5))
  return sum(kv.values())

# Python eDSL: The same code fails
@numba.njit()
def fails():
  # Generator expressions aren't supported
  kv = dict((i, i * i) for i in range(5))
  # Built-in function sum isn't implemented
  return sum(kv.values())

Copy

为什么？因为 eDSL 并不是在*执行* Python——它在捕获函数并把它转换成别的东西。由它决定支持哪些构造，而许多日常 Python 特性（如动态列表、异常处理或递归）可能根本不能用。这会导致*静默失败*或*晦涩的错误*——你本以为在 Python 里能用的东西突然不行了。

###### **错误信息与工具链的局限**

调试 eDSL 代码可能是一场**噩梦**。当代码出错时，你往往看不到习以为常的友好 Python 错误信息，而是盯着来自编译器内部深处的不透明堆栈跟踪，毫无线索。更糟的是，Python 调试器等标准工具常常完全失效，你只能依赖 eDSL 提供的调试设施（如果有的话）。此外，虽然 eDSL 存在于 Python 之内，却不能直接使用 Python 库。

###### **表达力受限**

eDSL 靠搭乘 Python 语法的便车工作，这意味着它们**不能**引入对其领域可能有用的新语法。像 CUDA C++ 这样的语言可以添加自定义关键字、新构造或领域专属优化，而 eDSL 被锁死在 Python 的一个子语言里，限制了它能优雅表达的内容。

归根结底，某个具体 eDSL 的*质量*决定了这些权衡有多痛苦。实现良好的 eDSL 能提供顺滑的体验，而设计糟糕的则可能是一个期望不断落空的雷区。那么像 **Triton** 这样的 eDSL 做对了吗？它与 CUDA 相比如何？

# Triton：OpenAI 面向 GPU 编程的 Python eDSL

Triton 起步于哈佛大学的 [Philippe Tillet](https://scholar.google.com/citations?user=SQfo7UgAAAAJ&hl=fr) 的研究项目，[于 2019 年首次发表](https://www.eecs.harvard.edu/~htk/publication/2019-mapl-tillet-kung-cox.pdf)——此前他[多年深耕 OpenCL](https://youtu.be/WnBG7je7tO4?si=_M9jWBO4m0XR2R-e&t=70)（参见我[早前关于 OpenCL 的文章](https://www.modular.com/blog/democratizing-ai-compute-part-5-what-about-cuda-c-alternatives)）。当 Tillet 加入 OpenAI、PyTorch 2 决定拥抱 Triton 后，项目获得了强劲动力。

与通用 AI 编译器不同，Triton **聚焦于让 Python 开发者易于上手**，同时仍允许深度优化。它在**高层简洁与底层控制**之间取得平衡——给开发者恰到好处的灵活度来微调性能，而不至于淹没在 CUDA 的复杂性中。

让我们看看 Triton 因何而有用。

## 以块为中心的编程模型

传统 GPU 编程迫使开发者以**单个线程**为单位思考，手工管理同步和复杂索引。Triton 通过在**块（block）级别**运作来简化——这正是 GPU 天然的工作粒度——消除了不必要的底层协调：

Python

@triton.jit
def simplified_kernel(input_ptr, output_ptr, n_elements, BLOCK_SIZE: tl.constexpr):
    # One line gets us our block position
    block_start = tl.program_id(0) * BLOCK_SIZE
    # Create indexes for the entire block at once
    offsets = block_start + tl.arange(0, BLOCK_SIZE)
    # Process a whole block of data in one operation
    data = tl.load(input_ptr + offsets, mask=offsets

<

n_elements)
    # No need to worry about thread synchronization

Copy

这个模型抽象掉了线程管理、简化了基本索引，同时也让**利用 TensorCores 容易得多**——正是这些专用硬件贡献了 GPU 的大部分 FLOPS：

Python

# This simple dot product automatically uses TensorCores when available
result = tl.dot(matrix_a, matrix_b)

Copy

原本需要**几十行复杂 CUDA 代码**的事情变成了一次函数调用，同时仍能实现高性能。Triton 自动处理数据布局变换和硬件专属优化。

## 简化的优化

CUDA 最令人沮丧的方面之一是为多维数据管理复杂的索引计算。Triton 极大地简化了这一点：

Python

# Simple indexing with broadcast semantics
row_indices = tl.arange(0, BLOCK_M)[:, None]
col_indices = tl.arange(0, BLOCK_N)[None, :]

Copy

这些数组操作与 NumPy 类似，但编译后成为无运行时开销的高效 GPU 代码。

Triton 还包含编译器驱动的优化——比如向量化——并支持简化的双缓冲和软件流水线，让内存传输与计算重叠。在 CUDA 中，这些技术需要深厚的 GPU 专业知识；在 Triton 中，它们的暴露方式**让非专家也能真正用起来**。想深入了解，OpenAI 提供了[详细教程](https://triton-lang.org/main/getting-started/tutorials/)。

**Triton 让 GPU 编程变得亲民得多，但这种亲民是有代价的。**让我们看看几个关键挑战。

## Triton 的短板

Triton 被广泛使用，在某些场景非常成功（例如研究前沿模型训练的研究者和特定用例）。但它在所有应用上并未被广泛采用：尤其是对要求极致效率的 AI 推理场景，它并不好用。此外，[尽管行业领袖多年前就做出预测](https://semianalysis.com/2023-01-16/nvidiaopenaitritonpytorch/)，Triton 并未统一生态，也没能挑战 CUDA 的统治。让我们深挖一下：在一切 eDSL 的通用局限（前文已述）之外，Triton 还面临哪些额外挑战。

###### **显著的 GPU 性能/TCO 损失（相比 CUDA C++）**

**‍**Triton **用性能换取生产力**[（其作者本人如此解释）](https://youtu.be/WnBG7je7tO4?si=VwRalE1KOPX0k3eo&t=1186)。这让编写 GPU 代码更容易，但也使 Triton 无法达到峰值效率。损失程度不一，但在如今主导 AI 算力的 **NVIDIA H100** 上损失 20% 是常态。

问题在哪？**编译器无法优化得像熟练的 CUDA 开发者一样好，尤其是在当今的高级 GPU 上。**在我数十年的编译器生涯中，从未见过“[**足够聪明的编译器**](https://wiki.c2.com/?SufficientlySmartCompiler)”的神话真正实现！这就是包括 DeepSeek 在内的领先 AI 实验室**在苛刻负载上仍然依赖 CUDA 而非 Triton** 的原因：20% 的差距在 GenAI 中无法承受——在规模化下，这是 10 亿美元云账单与 8 亿美元云账单的区别！

###### **治理：OpenAI 的控制与关注点**

Triton 是开源的，但 OpenAI **掌控其路线图**。这有问题，因为 OpenAI 与其他前沿模型实验室直接竞争，这就引出疑问：**它会优先考虑广大 AI 社区的需求，还是只服务自己？**

许多工程师吐槽**向 Triton 贡献增强功能有多难**——尤其是当改动不符合 OpenAI 内部优先级时。一个反复出现的抱怨是**对替代硬件的支持远远落后**——因为 OpenAI 没有动力为自己不用的加速器做优化。Triton 的领导层也承认“[对新用户的支持几乎不存在](https://youtu.be/o3DrHb-mVLM?si=9cp9syo9S8tKwqQ0&t=880)”，且他们没有带宽跟上社区需求。

###### **糟糕的工具链与调试器支持**

CUDA 的复杂性被**成熟的工具生态**所抵消——Nsight Compute、profiler API 和内存调试器——让开发者深入洞察性能瓶颈。Triton 无法使用这些工具。eDSL 在设计上本应把细节抽象掉。结果就是，一旦出现问题，开发者无法确定问题源头，往往只能***猜测编译器做了什么***。这种可观测性的缺失，让 Triton 中的性能调试比 CUDA 更难，尽管它的编程模型更简单。

###### **有 GPU 可移植性，却没有性能可移植性或通用性**

用 Triton 写的 GPU 代码，若针对某一款特定 GPU 编写可以跑得“相当快”，但同样的代码换一种 GPU 就跑不快——即便同在 NVIDIA 硬件之间也是如此。例如，针对 **A100** 优化的 Triton 代码在 **H100** 上往往表现糟糕，因为新架构即使要达到 80% 的性能也需要不同的代码结构——Triton 没有把流水线和异步内存传输这类东西抽象掉。

Triton kernel 需要为新一代 NVIDIA 硬件重写才能释放其性能。

迁移到 **AMD GPU** 更糟。虽然 Triton 技术上支持 AMD 硬件，但性能和特性与 NVIDIA **相去甚远**，使跨厂商可移植性不切实际。对于**非 GPU 的 AI 加速器**（如 TPU、Groq 芯片或 Cerebras 晶圆），情况堪称灾难。这些架构不遵循 Triton 假设的 **SIMT 执行模型**，导致**性能严重劣化**，或者需要如此多的变通以至于该方法适得其反。

归根结底，**“一次编写，到处运行”**的承诺通常兑现为：**“一次编写，到处运行——但在替代平台上性能显著劣化。”**

# Triton 的综合评价如何？

在[上一篇](https://www.modular.com/blog/democratizing-ai-compute-part-6-what-about-ai-compilers)和[上上篇](https://www.modular.com/blog/democratizing-ai-compute-part-5-what-about-cuda-c-alternatives)中，我们开始为 AI 编程系统列一份愿望清单。以此为标准衡量，Triton 既有几大优势，也有若干挑战：

- **“提供参考实现”**：Triton 提供的是完整实现而非规范，附带实用示例和教程。👍
- **“拥有强有力的领导和愿景”**：Triton 在 OpenAI 之下有明确的领导层，但优先级与 OpenAI 自身需求而非广大社区一致。长期治理仍是隐忧，对竞争的 AI 实验室尤其如此。👍👎
- **“在行业领导者的硬件上跑出顶级性能”**：Triton 在 NVIDIA 硬件上运行良好，但与优化后的 CUDA 相比通常有约 20% 的性能差距。它对 FP8、TMA 等最新硬件特性的支持力不从心。👎
- **“快速演进”**：Triton 适应了一些 GenAI 需求，但在支持前沿硬件特性上落后。演进速度取决于 OpenAI 的内部优先级而非行业需求。👎
- **“培养开发者的热爱”**：Triton 提供了简洁的基于 Python 的编程模型，许多开发者觉得直观高效。它与 PyTorch 2.0 的集成扩大了影响力。👍👍👍
- **“建设开放社区”**：虽然开源，但 Triton 的社区受限于 OpenAI 对路线图的控制。外部组织的贡献面临重重障碍。👎
- **“避免碎片化”**：面向 NVIDIA GPU 的 Triton 本身是统一的 👍，但它被其他硬件厂商的版本广泛碎片化，各家版本有不同的局限与取舍。👎
- **“实现完全可编程”**：Triton 对标准操作提供了良好的可编程性 👍，但无法访问/控制所有硬件特性，尤其是最新加速器的能力。👎
- **“提供对抗 AI 复杂度的杠杆”**：Triton 高效处理常见模式并简化了开发 👍。但它不支持自动融合来解决指数级复杂度问题。👎
- **“支撑大规模应用”**：Triton 聚焦单设备 kernel，缺少对多 GPU 或多节点扩展的内建支持，但与 PyTorch 集成出色，由后者负责这部分。👍

总体而言，显然 Triton 是 AI 开发生态中极有价值的一部分，尤其当目标是 NVIDIA GPU 时。话虽如此，虽然 Triton 因与 PyTorch 的集成而最知名，其他项目——如 **Pallas、CUTLASS Python 和 cuTile**——正在探索生产力、性能与硬件支持之间的不同取舍。这些替代方案都建立在相似理念之上，但各自采用独特方式解决 GPU 可编程性。

# 其他 Python eDSL：Pallas、**CUTLASS** Python、cuTile 等

Python eDSL 的使命不是交付最好的性能——而是让编译器开发者更容易把东西推向市场。因此，**这类项目非常多**——Triton 只是最出名的那个。以下是常被问到的几个。*（免责声明：我没有直接使用过它们。）*

## Google Pallas

[Google Pallas](https://docs.jax.dev/en/latest/pallas/index.html) 是 JAX 的子项目，旨在支持自定义算子——尤其是为 TPU。它大量借鉴 Triton，但**暴露了更多底层编译器细节**，而不是提供高层、用户友好的 API。

从外部视角看，Pallas 显得**强大但难用**，需要对 TPU 硬件和编译器内部机制的深刻理解。其官方文档也列出了[大量陷阱（footguns）](https://docs.jax.dev/en/latest/pallas/design/async_note.html#why-doesnt-this-work)，清楚表明这是给掌握底层知识的专家用的工具。因此，其在 Google 之外的采用相当有限。

## CUTLASS Python 与 cuTile

在 **GTC 2025** 上，NVIDIA 发布了两个新的 Python eDSL：**CUTLASS Python** 和 **cuTile**。两者都还未开放下载，以下是初步印象：

- **CUTLASS Python** – 在[这场 GTC 演讲](https://www.nvidia.com/gtc/session-catalog/?tab.catalogallsessionstab=16566177511100015Kus#/session/1738891305735001ygGc)中展示，看起来深受 Google Pallas 启发。它暴露**底层编译器细节**，需要很深的硬件知识，却没有 CUDA 开发者赖以工作的工具链或调试器。它首先在 Blackwell 上发布，我怀疑 NVIDIA 会开源它或支持其他硬件厂商。我也很好奇 Python 缺乏静态类型对编写这类底层系统代码能适配到什么程度。
- **cuTile** – 这个项目在 X 上被广泛转发*[（示例）](https://x.com/blelbach/status/1902113767066103949)*，但除几页幻灯片外，发布日期和技术细节一无所知。它的定位似乎是专有的 Triton 替代方案。NVIDIA 承认 [cuTile 大约比 TRT-LLM 慢 15%](https://x.com/blelbach/status/1905707348506918967)。考虑到 NVIDIA 对峰值性能的追求，尚不清楚它是否会用 cuTile 构建自己的 CUDA 库。如果发布，**NVIDIA 内部的真实采用才是试金石**。

这些 eDSL 只是 NVIDIA 庞大 Python GPU 生态的一部分。在 **GTC 2025** 上，[NVIDIA 说](https://www.nvidia.com/gtc/session-catalog/?tab.catalogallsessionstab=16566177511100015Kus&search=what%27s%20new%20in%20cuda#/session/1726614035480001yvEQ)，*“没有一种万能工具——****你要为工作****选对工具。”* NVIDIA 甚至有一场题为[《用 Python 编写 CUDA kernel 的一千零一种方法》](https://www.nvidia.com/gtc/session-catalog/?tab.catalogallsessionstab=16566177511100015Kus#/session/1727175449007001EIKh)的演讲——光是想到要选对路径就已是噩梦。

据 NVIDIA 称，“没有单一工具对所有应用都是最优的”。（来源：NVIDIA GTC 2025，

CUDA: New Features and Beyond

）

作为一名开发者，我不认为几十个各有微妙取舍的选项能帮到我。我们需要**更少但更好用的工具**——而不是不断增长的取舍清单。NVIDIA 正在**碎片化自己的开发者生态**。

# MLIR：AI 编译器的统一未来？

2017 至 2018 年我在 Google 推动 TPU 规模化时，一个模式浮现出来：**以 TensorFlow 和 PyTorch 为代表的*第一代* AI 框架缺乏可扩展性，而*第二代* AI 编译器如 **[**XLA**](https://www.modular.com/blog/democratizing-ai-compute-part-6-what-about-ai-compilers)** 牺牲了灵活性**。为了打破这个循环，我带领团队构建了新的 [**MLIR 编译器框架**](https://en.wikipedia.org/wiki/MLIR_(software))——一个模块化、可扩展的编译器框架，旨在支撑 AI 快速演进的硬件版图。

它成功了吗？MLIR 推动了行业级突破——**Triton、cuTile 等** Python DSL 都构建在其上，重新定义了 GPU 编程。但像此前的 **[**TVM 和 XLA**](https://www.modular.com/blog/democratizing-ai-compute-part-6-what-about-ai-compilers)** 一样，MLIR 也面临**治理挑战、碎片化与公司利益冲突**。真正**统一**的 AI 编译器栈愿景仍遥不可及，被困在塑造了这个行业数十年的同样的权力博弈中。

碎片化似乎不可避免，抵抗亦是徒劳。一种统一性的编译技术真的能帮助 AI 算力走向民主化吗？

**敬请期待下篇**——我们将深入 MLIR：**好的、坏的……以及组织动态。**

—Chris
