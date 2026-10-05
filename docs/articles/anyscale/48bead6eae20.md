---
vendor: anyscale
title: Ray Datasets：大规模机器学习数据摄取与打分
original_title: Ray Datasets for large-scale machine learning ingest and scoring
url: https://anyscale.com/blog/ray-datasets-for-machine-learning-training-and-scoring
date: 2022-02-14
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Ray Datasets：大规模机器学习数据摄取与打分

作者：Clark Zinzow、Alex Wu、Jiajun Yao、Eric Liang 和 Chen Shen | 2022 年 2 月 14 日

我们很高兴介绍 Ray Datasets——一个构建在 Ray 上的数据加载与预处理库。Datasets 利用 Ray 的任务、actor 与对象 API，在单个 Python 应用内实现大规模机器学习（ML）摄取、训练与推理。

*blog-ray-datasets-1*

简而言之，Datasets：

- 是**把分布式数据载入 Ray** 的标准方式，支持流行存储后端与文件格式。
- 支持常见 **ML 预处理操作**：包括 map、批量 map、filter 等基础并行数据变换，以及 sort、shuffle、groupby、统计聚合等全局操作。
- 支持需要状态化初始化的操作与 GPU 加速。
- 与集成 Ray 的**数据处理库**（Spark、Pandas、NumPy、Dask、Mars）和 **ML 框架**（TensorFlow、Torch、Horovod）无缝协作。

本文会巡礼分布式训练与模型打分流水线的现状，概述 Ray Datasets 如何解决其中的痛点。意犹未尽的话，请[报名我们即将举办的网络研讨会](https://www.anyscale.com/events/2022-02-16/ray-datasets-scalable-data-preprocessing-for-distributed-ml)，第一手观看 Datasets 的实战。下面开讲！

## 当前的 ML 训练与推理流水线

### 现状流水线

如今，用户常常用各种分布式计算框架拼出自己的训练流水线。这种做法在复用既有系统上有优势，但也有若干缺陷——我们在[第三代 ML 架构中的数据摄取](https://www.anyscale.com/blog/deep-dive-data-ingest-in-a-third-generation-ml-architecture)一文中已详述。

*训练流水线现状：需要一个 workflow 编排框架来编排这种多语言、多作业、中间数据落盘的流水线。*

*blog-ray-datasets-2*

### 愿景

Ray 正在让[简单的 Python 脚本](https://www.anyscale.com/blog/the-third-generation-of-production-ml-architectures)取代这些流水线，既规避其取舍，又[提升性能](https://www.anyscale.com/blog/why-third-generation-ml-platforms-are-more-performant)。Ray Datasets 是这一愿景的关键一环，充当 Ray 中分布式步骤之间交换数据的"分布式 Arrow"格式。

## Ray Datasets 入门

### Datasets 简说

Datasets 本质上是一个分布式数据集抽象：底层数据块（分区）分布在 Ray 集群上，位于分布式内存中。

*一个 Dataset 持有一个或多个内存数据块的引用，这些块分布在整个 Ray 集群上。*

*blog-ray-datasets-3*

这种分布式表示让 Dataset 可以由分布式并行任务构建：每个任务从数据源（如 S3）拉取一个块的数据并放入所在节点的本地对象存储，客户端侧的 Dataset 对象则持有这些分布式块的引用。对客户端 Dataset 对象的操作，随之转化为对这些块的并行操作。

Dataset 的块可以容纳任意模态的数据——文本、任意二进制字节（如图像）、数值数据；但与表格数据配合才能释放 Datasets 的全部威力。此时每个块是分布式表的一个分区，这些按行划分的分区底层用 Arrow Table 表示，形成一个分布式 Arrow 数据集。

*含三个 Arrow 表块的 Dataset 可视化，每块容纳 1000 行。*

*blog-ray-datasets-4*

### Datasets 如何嵌入我的训练流水线？

Datasets **不**打算替代 Spark 这类通用数据处理系统。Datasets 的定位是 ETL 流水线与运行在 Ray 上的分布式应用之间最后一公里桥梁。

*Ray Datasets 是通往 Ray 集群的最后一公里数据桥。*

*blog-ray-datasets-5*

当你的数据处理阶段使用集成 Ray 的 DataFrame 库时，这座桥会更加强大：你可以在 Ray 之上运行完整的数据到 ML 流水线，消除中间数据物化到外部存储的需要。Ray 充当 ML 流水线的通用计算基座，Datasets 则在流水线阶段之间构成分布式数据桥。

整条流水线跑在 Ray 上时，分布式数据可以从关系型数据处理无缝流进模型训练，其间不碰磁盘、也不经中心化的数据中转。

*blog-ray-datasets-6*

关于底层如何工作，参阅我们[第三代 ML 架构中的摄取](https://www.anyscale.com/blog/deep-dive-data-ingest-in-a-third-generation-ml-architecture)一文。

### 基础特性

#### 可扩展的并行 I/O

Datasets 志在成为通用的并行数据加载器、写出器与交换格式，为 Ray 应用与库提供一个窄窄的数据腰部接口。

*blog-ray-datasets-7*

这靠重度利用 Arrow 的 I/O 层达成：用 Ray 高吞吐的任务执行来并行化 Arrow 高性能的单线程 I/O。Datasets 的 I/O 层已在 Amazon 生产环境扩展到[多 PB 级的数据摄取作业](https://www.youtube.com/watch?v=h7svj_oAY14)。

Datasets 的可扩展 I/O 全部藏在[极简 API](https://docs.ray.io/en/latest/data/dataset.html)之后，一次调用即可表达：`ray.data.read_<format>()`。

#### 数据格式兼容

借助 Arrow 的 I/O 层，支持你喜爱的多数表格格式（JSON、CSV、Parquet）与存储后端（本地磁盘、S3、GCS、Azure Blob Storage、HDFS）。表格之外，我们增加了 NumPy、文本与二进制文件的并行读写。对从[众多外部源](https://docs.ray.io/en/latest/data/dataset.html#datasource-compatibility-matrices)读取多种格式的全面支持，加上极可扩展的并行化方案，让 Datasets 成为向 Ray 集群摄取大量数据的首选方式。

```
1# Read structured data from disk, cloud storage, etc.
2ray.data.read_parquet("s3://path/to/parquet")
3ray.data.read_json("...")
4ray.data.read_csv("...")
5ray.data.read_text("...")
6
7# Read tensor / image / file data.
8ray.data.read_numpy("...")
9ray.data.read_binary_files("...")
10
11# Create from in-memory objects.
12ray.data.from_objects([list, of, python, objects])
13ray.data.from_pandas([list, of, pandas, dfs])
14ray.data.from_numpy([list, of, numpy, arrays])
15ray.data.from_arrow([list, of, arrow, tables])
```

#### 数据框架兼容

除存储 I/O 外，Datasets 还支持与许多在 Ray 上运行的流行分布式框架双向内存数据交换——Spark、Dask、Modin、Mars——小规模本地内存数据则支持 Pandas 与 NumPy。为把数据方便地喂进模型训练器，Datasets 为 PyTorch 与 TensorFlow 提供交换 API，产出各框架熟悉的 [torch.util.data.IterableDataset](https://pytorch.org/docs/stable/data.html#torch.utils.data.IterableDataset) 与 [tf.data.Dataset](https://www.tensorflow.org/api_docs/python/tf/data/Dataset)。

```
1# Convert from existing DataFrames.
2ray.data.from_spark(spark_df)
3ray.data.from_dask(dask_df)
4ray.data.from_modin(modin_df)
5
6# Convert to DataFrames and ML datasets.
7dataset.to_spark()
8dataset.to_dask()
9dataset.to_modin()
10dataset.to_torch()
11dataset.to_tf()
12
13# Convert to objects in the shared memory object store.
14dataset.to_numpy_refs()
15dataset.to_arrow_refs()
16dataset.to_pandas_refs()
17
```

#### 最后一公里预处理

Datasets 为常见的最后一公里变换提供便捷的[数据预处理功能](https://docs.ray.io/en/master/data/dataset-ml-preprocessing.html)——那些你希望在训练模型或批量推理之前一刻完成的变换。"最后一公里预处理"涵盖因模型而异、或带有每次运行/每个 epoch 随机性的变换。Datasets 让你在（分布式）内存中并行完成这些操作，用 `.map_batches(fn)` 即可，无需在开始训练或批量推理前把结果持久化回存储。

```
1# Simple transforms.
2dataset.map(fn)
3dataset.flat_map(fn)
4dataset.map_batches(fn)
5dataset.filter(fn)
6
7# Aggregate operations.
8dataset.repartition()
9dataset.groupby()
10dataset.aggregate()
11dataset.sort()
12
13# ML Training utilities.
14dataset.random_shuffle()
15dataset.split()
16dataset.iter_batches()
17
```

#### 有状态的 GPU 任务

为支持[大数据集的批量推理](https://docs.ray.io/en/master/data/advanced-pipelines.html#example-pipelined-batch-inference)，Datasets 支持在 GPU 上运行有状态计算。做法很简单：不要用无状态函数调 `.map_batches(fn)`，而是 `.map_batches(callable_cls, compute="actors")`。可调用类会被实例化到一个 Ray actor 上，并多次复用来变换输入 batch 做推理：

```
1# Example of GPU batch inference on an ImageNet model.
2def preprocess(image: bytes) -> bytes:
3    return image
4
5class BatchInferModel:
6    def __init__(self):
7        self.model = ImageNetModel()
8    def __call__(self, batch: pd.DataFrame) -> pd.DataFrame:
9        return self.model(batch)
10
11ds = ray.data.read_binary_files("s3://bucket/image-dir")
12
13# Preprocess the data.
14ds = ds.map(preprocess)
15# -> Map Progress: 100%|████████████████████| 200/200 [00:00<00:00, 1123.54it/s]
16
17# Apply GPU batch inference with actors, and assign each actor a GPU using
18# ``num_gpus=1`` (any Ray remote decorator argument can be used here).
19ds = ds.map_batches(BatchInferModel, compute="actors", batch_size=256, num_gpus=1)
20# -> Map Progress (16 actors 4 pending): 100%|██████| 200/200 [00:07, 27.60it/s]
21
22# Save the results.
23ds.repartition(1).write_json("s3://bucket/inference-results")
```

### Datasets 的流水线化计算

读取、变换、消费/写出 Dataset 会形成一串执行阶段。默认情况下这些阶段以阻塞调用即时执行，提供易于理解的 bulk synchronous parallel 执行模型，且每个阶段并行度最大化：

*blog-ray-datasets-8*

但这不允许跨阶段重叠计算：第一个数据块加载完成时，要等所有其他块也加载完才能开始变换它。若不同阶段需要不同资源，这种锁步执行会让当前阶段的资源过度饱和、其他阶段的资源闲置。流水线化正是解决之道：

*blog-ray-datasets-9*

流水线在 Datasets API 中原生支持：只需调用 **.window()** 或 **.repeat()**，生成一个 DatasetPipeline——它可以像普通 Dataset 一样被读取、变换与写出。这意味着你可以轻松地为 ML 训练与推理做增量处理或流式处理。详见[流水线文档](https://docs.ray.io/en/master/data/key-concepts.html#dataset-pipelines)。

### 为什么要把 Datasets 建在 Ray 上？

Ray 有强健的[分布式数据面](https://docs.google.com/document/d/1lAy0Owi-vPz2jEqBSaHNQcy2IBSDEHyXNOQZlGuj93c/preview)，把去中心化调度与同类最佳的分布式对象层结合，特点是：

- **高效零拷贝读取**：同节点 worker 通过共享内存读取，跨 worker 进程共享数据不再需要序列化。
- **局部性感知调度**：数据密集型任务被调度到已本地持有该任务所需数据最多的节点。
- **韧性对象传输协议**：配有[内存管理器](https://www.anyscale.com/blog/analyzing-memory-management-and-performance-in-dask-on-ray)，在约束内存用量的同时确保预取与向前推进。
- **高速数据传输实现**：并行传输数据分块以最大化传输吞吐。

有了 Ray 的分布式数据面，构建 Datasets 这样的库就相对简单了。Datasets 把大部分重活委托给 Ray 数据面，自己专注于更高层特性：便捷 API、数据格式支持与阶段流水线化。

## 社区如何使用 Datasets？

Ray Datasets 项目仍处早期。beta 之后，我们计划增加若干特性，包括：

- 支持更多数据格式与集成
- 降低大规模流水线中对象存储的内存开销
- 改进 shuffle 的性能与可扩展性（扩展到 100TB+）

尽管如此，用户如今已经发现 Datasets 带来切实的优势。

### 案例 1：ML 训练与推理 vs Petastorm/Pandas

一家用 Ray 做 ML 基础设施的组织发现，Datasets 在小规模上就能有效加速其训练与推理负载：

**训练**时，在单个 GPU 实例上，Ray Datasets 比 Pandas + S3 + Petastorm 快 8 倍，序列化开销显著下降：

基准：NYC Taxi 数据集（5GB 子集），单台 g4dn.4xlarge 实例。

*blog-ray-datasets-10*

**推理**时，Dask-on-Ray + Datasets + Torch 比 Pandas + Torch 快 5 倍——即便只在单机上评估：

基准：NYC Taxi 数据集（5GB 子集），单台 r5d.4xlarge 实例。

*blog-ray-datasets-11*

### 案例 2：大规模 ML 摄取

另一个 ML 平台团队评估了更大规模的 S3 → Datasets → Horovod 数据流水线，把摄取流水线扩展到多机集群时获得显著收益。该用例中，Datasets 不仅提供了更高吞吐，还因支持真正的分布式 shuffle 而带来更好的洗牌质量。

## 结语

总之，Datasets 通过灵活、可扩展的 Ray 内数据处理 API 简化了 ML 流水线。Datasets 才刚起步，但用户已经在多种规模上验证了它在训练与推理上的有效性。请[查阅文档](https://docs.ray.io/en/master/data/dataset.html)，或[报名我们的网络研讨会](https://www.anyscale.com/events/2022-02-16/ray-datasets-scalable-data-preprocessing-for-distributed-ml)，第一手感受 Datasets。

*本文基于 Alex Wu 与 Clark Zinzow 在 PyData Global 2021 的演讲《*[*Unifying Data preprocessing and training with Ray Datasets*](https://www.youtube.com/watch?v=wl4tvru9_Cg)*》。*
