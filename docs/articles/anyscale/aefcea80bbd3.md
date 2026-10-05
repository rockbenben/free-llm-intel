---
vendor: anyscale
title: Ray Data 2.56：提升 AI 数据流水线的可靠性
original_title: Ray Data 2.56: Improving Reliability for AI Data Pipelines
url: https://anyscale.com/blog/ray-data-256-updates
date: 2026-06-30
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Ray Data 2.56：提升 AI 数据流水线的可靠性

作者：Balaji Veeramani、Justin Yu、Ray Huang、Ayush Kumar、David Dai、Akshay Malik、Richard Liaw 和 Xinyuan Gui | 2026 年 6 月 30 日

Ray Data 是大规模批量推理与训练摄取（ingest）流水线最常见的方案之一。在 Ray Data 2.56 中，我们聚焦用户报告最多的两大可靠性挑战：OOM（内存溢出）故障与不必要的对象溢出（spilling）。

这两个问题都会显著拖慢 Ray Data 流水线，甚至常把作业直接打崩。例如，溢出可能引发磁盘写满错误，而严重的内存压力会让操作系统终止关键的 driver 进程。

在 Ray Data 2.56 的开发中，我们花时间同时攻克这两个问题，旨在为用户提供可靠得多的体验。借助最新更新，我们在多种内部负载上看到 OOM 与溢出显著减少。

这些收益主要来自：

- **内存感知执行。** Ray Data 现在更准确地注册任务内存、自动调优 CPU `map_batches` 负载的 batch size，并在内存压力下优先终止空闲 worker 而非关键进程。
- **改进的训练预取。** Ray Data 现在对 GPU stream 的争用更少、训练线程内存占用更低，带来更好的性能与稳定性。

下文分节介绍这些改动与研究过程。

运行 `pip install -U ray` 即可试用 Ray Data 2.56！

## 更少 OOM，更少崩溃

在 2.56 之前运行 Ray Data 的用户经常报告 OOM 错误，有时还会导致 Ray Data 流水线崩溃。这通常是内存超售（oversubscription）导致的：同一节点上运行多个任务，累计申请的内存超过了机器可用量。内存超售随后会触发操作系统开始杀进程，于是出现 OOM 警告、组件死亡、流水线失败。

要解决这一问题，我们需要：

- 确保 Ray Data 任务向 Ray 调度器注册恰当的内存量
- 确保 OOM 真的发生时，按优先级从低到高终止进程

在内存注册方面，Ray Data 2.56 有两个主要改进。第一，Ray Data 提供开关 `DataContext.get_current().default_map_logical_memory_enabled`。设置该开关后，所有 map 任务（包括 map_batches、flat_map、map 与 read 下执行的任务）的逻辑内存会被配置为每 CPU 4GB（若尚未配置）。

我们还为 CPU `map_batches` 调用引入了 batch size 调优功能，在 `map_batches` 调用中传入 `batch_size="auto"` 即可启用。现在无需用户手动调 batch size，系统会剖析行大小，自动选择一个 batch size，使输入大小落在安全阈值内（这里是 16MB 以下）。

我们还改进了 Ray 在高内存场景下的进程管理能力。Ray 现在自行处理 OOM 进程终止，而不是丢给底层操作系统。这让 Ray 可以终止空闲 worker 而非关键 driver 进程，避免节点死亡或无谓的任务击杀。此外，Ray 现在还会为 raylet 等系统进程预留固定的内存开销，给应用内存使用留出更多余量。

为衡量改动效果，我们在 AWS 的 8 台 g6.xlarge 实例上运行了语音转写基准[[链接](https://github.com/ray-project/ray/blob/eeb194f3bdce65a7e21bba971e20aecc068d668f/release/nightly_tests/multimodal_inference_benchmarks/audio_transcription/ray_data_main.py)]。从 2.55 到 2.56，OOM 从 **300+** 降到 **0**，端到端运行时间从 **1055 秒** 降到 **447 秒**。

**2.55**

*2.55 下的意外系统级 Worker 失败*

**2.56**

*2.56 下的意外系统级 Worker 失败*

关于诊断与规避 OOM 的更深入指南，参阅新用户手册：[https://docs.ray.io/en/master/data/how-to-avoid-ooms.html](https://docs.ray.io/en/master/data/how-to-avoid-ooms.html)

## 更少溢出，更快流水线

Ray Data 在训练摄取这类负载上也经常发生溢出。分析这些问题的成因，一个主因是对象存储内存用量估计不准。

Ray Data 内部维护着当前对象存储用量估计。这个内部指标还被用于触发反压（backpressure）（即向上游算子发信号放慢产出）。但如果估计错误，反压就会误触发或根本不触发，导致数据流水线里出现不必要的溢出。

两大主因是 **Pandas 块格式**，以及在训练数据加载场景下，**没有把训练 worker 上预取与 collation 管线占用的对象存储内存完全计入**。

**Pandas 块格式：** Ray Data 过去有多种内部数据表示的块格式——其中一种是 Pandas DataFrame。然而 Pandas DataFrame 无法有效核算总内存大小，对泛型 Python 对象尤其如此，导致估计不准。在 Ray Data 2.56 中，我们统一了块格式，现在只使用 PyArrow 作为唯一块格式，其内存大小估计精确得多。

**改进预取：** 在我们对溢出问题的调查中，注意到 Ray Data 每个 worker 实际预取的数量是配置的 `prefetch_batches` 的数倍，而吞吐毫无提升。多预取的数据贡献了对象存储内存占用，且大多不被 Ray Data 的用量估计跟踪——一旦数据超过对象存储溢出阈值就会落盘。

此外，这些预取的 batch 既被钉在对象存储中，又没有计入对象存储内存用量，意味着 Ray Data 低估了训练 worker 节点上的对象存储用量。

通过减少预取 batch 数量并正确计入，我们降低了对象存储用量，带来更少溢出与更低的对象存储峰值内存。

我们还发现，从 CPU 向 GPU 预取时会与默认 CUDA stream 争用，导致 GPU 侧计算 kernel 排队，拉低训练吞吐。减少预取量后，训练吞吐也随之改善。

**实验：** 在我们的内部对象存储内存[反压压测](https://github.com/ray-project/ray/blob/14ee057472ffaa034ded79fbca4d7dcb82846119/release/nightly_tests/dataset/backpressure_benchmark.py#L4)中，2.56 的溢出被完全消除（2.55 为 70GiB），对象存储峰值内存降低 41%。

在另一个以数据加载为瓶颈的基准中，由于少预取不必要的 batch、降低了 CUDA stream 争用，训练 step 吞吐实际提升了 25%。详情见这个 [PR](https://github.com/ray-project/ray/pull/63682)。

*对象存储峰值内存*

## 其他可靠性改进

除上述两组问题（OOM、溢出）外，我们还引入了许多其他可靠性与稳定性改进：

- **多数据集支持：** Ray Data 2.56 通过子集群 label 调度增加了多数据集支持。这解锁了常见模式：与训练并行跑验证（同步或[异步](https://docs.ray.io/en/latest/train/user-guides/asynchronous-validation.html)）、数据集多租户、把训练数据集的预处理 worker 隔离在训练 GPU 节点之外。我们把[这些改进写成了文档](https://docs.ray.io/en/master/data/concurrent-dataset-execution.html)。
- **训练 shuffle 改进：** 我们优化了本地 shuffle buffer 性能，在多种负载上内存占用最多降低 2.5 倍、吞吐提高 3 倍。我们还在此记录了训练 shuffle [最佳实践](https://docs.ray.io/en/master/data/shuffling-data.html#map-batches-shuffle)。
- **调度循环可扩展性：** 我们收到报告称高 worker 数量下调度循环延迟劣化。我们已落地多项调度循环吞吐改进，目前在大规模（2000+ worker）下调度循环 P90 延迟最多下降 6 倍。为 Ray Data 2.57，这项工作仍在继续。

## 展望 2.57

2.57 还有一批稳定性改进与新特性在排期中——发布时我们会再写一篇博客。Ray Data 2.57 改进的快速预览：

- 彻底修复预取训练 batch 的记账。2.56 缓解了问题并大幅减少预算超支，2.57 将根治。
- Epoch 中途恢复，为训练负载提供更快的基于 checkpoint 的恢复。
- Datasource V2，带来好得多的 schema 处理与推断。
- 容错 shuffle。

升级到 2.56，收获这些稳定性与性能收益。一如既往，我们期待你的反馈——现在就 `pip install -U ray` 试用 Ray。
