---
vendor: anyscale
title: 深潜：第三代 ML 架构中的数据摄取
original_title: Deep Dive: Data Ingest in a Third Generation ML Architecture
url: https://anyscale.com/blog/deep-dive-data-ingest-in-a-third-generation-ml-architecture
date: 2021-11-30
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# 深潜：第三代 ML 架构中的数据摄取

作者：Eric Liang、Chen Shen、Clark Zinzow 和 Waleed Kadous | 2021 年 11 月 30 日

这是我们[第三代 ML 架构](https://www.anyscale.com/blog/the-third-generation-of-production-ml-architectures)系列的第三篇。上一篇我们谈到分布式库如何通过利用分布式内存的全部带宽来提升[性能](https://www.anyscale.com/blog)，并带来更强的可编程性。但这*到底是怎么运作的*？代码长什么样？

本文用一个带代码示例的具体案例来说明：用 [Ray Datasets](https://docs.ray.io/en/latest/data/data.html) 与 [Ray Train](https://docs.ray.io/en/latest/train/user-guides.html) 做 ML 数据摄取。

- 我们展示这些分布式库只需几行 Python 即可编织在一起——这是第二代架构做不到的关键能力。
- 我们剖析 Datasets 与 Train 如何利用 Ray 任务、actor、对象这些可互操作的原语，实现这种可组合架构。

提供了可直接运行的脚本，你可以改造后在自己的 Ray 集群上使用。

## 小数据训练

先热个身，看看小数据场景下的 ML 训练。这类流水线很简单，因为所有数据都能放入内存，shuffle 开销也很小。几行伪码即可表达：

```
1data = load_data()
2preprocess(data)
3for each epoch:
4    random_shuffle(data)
5    train_one_epoch(data)
```

回顾上面各步骤：

- **加载**：小数据通常从本地磁盘文件读入内存，某些情况下也从文件流式读取。
- **预处理**：应用简单变换（即特征工程）。
- **Shuffle**：随机打乱数据集中条目的顺序。每个 epoch 随机洗牌对随机梯度下降[至关重要](https://arxiv.org/abs/1709.10432)。
- **训练**：在数据上拟合模型（如用 [PyTorch](https://pytorch.org/) 或 [Horovod](https://horovod.readthedocs.io/en/stable/index.html) 等框架）。

## 大数据训练的挑战

在大数据上训练模型会新增三方面需求：（1）分布式预处理，（2）分布式 shuffle 以提升收敛速度，（3）与 ML 训练的流水线化执行：

- **分布式预处理**：大规模训练的数据摄取需求可能非常庞大，催生了 Facebook 的 [DPP](https://arxiv.org/abs/2108.09373)、Uber 的 [Petastorm](https://www.uber.com/blog/petastorm/) 等专门系统。这类系统可以把预处理卸载到集群中区别于 GPU 机器的其他节点上。一部分预处理可以离线完成，但为保持灵活性，数据最好是"最小化预处理"的。
- **分布式 shuffle**：训练的每个 epoch 都对数据集洗牌（随机重排）很重要。这能显著[改善 SGD 收敛](https://arxiv.org/abs/1709.10432)，但在[分布式环境](https://en.wikipedia.org/wiki/MapReduce)下很有挑战。虽然*全局 shuffle* 是最优的，但由于把大规模数据 shuffle 与 ML 训练衔接起来的工程复杂性，TensorFlow/Pytorch 数据加载器和 Petastorm 等方案通常只做局部洗牌。
- **数据处理与训练的流水线化**：受限于集群内存规模以及每 epoch 随机洗牌的需求，我们看到预处理与 shuffle 计算可能需要与训练交错执行。今天这只有在 DPP 这类专门系统中才可能实现（例如，你无法简单地把 Spark 的分布式 shuffle 与 Horovod 串起来，因为它们是两个独立的分布式系统）。

换句话说，我们简单的流水线变难了，因为各组件为了性能必须变得分布式且流水线化：

```
1data = load_data()         # larger than cluster memory :(
2preprocess(data)           # distributed transforms :(
3for each epoch:
4    random_shuffle(data)   # distributed shuffle :(
5    train_one_epoch(data)  # pipelined with above distributed steps :(
```

## 第二代方案

简要考虑如何组合现有分布式系统解决这一分布式摄取问题。我们需要搭一个 Spark 集群做数据处理、一个 Horovod 集群做训练、一个协调服务做控制面操作，还需要外部存储做数据面通信。

*第二代——数据摄取问题*

训练流水线按以下步骤工作。首先，协调服务（1）向 Spark 集群提交一个 shuffle 作业，Spark（2）读取数据并写出到外部存储。接着，Horovod 的数据读取器（如 Petastorm）（3）从协调服务获取已写入的数据集位置，并（4）读出 shuffle 数据用于训练。这些步骤在训练的每个 epoch 重复，并且可以并发运行以优化执行延迟。

第二代方案的缺点：

- [缺乏可编程性](https://www.anyscale.com/blog/the-third-generation-of-production-ml-architectures)：需要搭建并管理 3 个以上独立分布式系统。由于 shuffle 与训练交错，用 workflow 系统编排也很困难。
- [性能开销](https://www.anyscale.com/blog)：中间数据必须写入外部存储，因为它要跨分布式系统传递。

## 第三代方案

相比之下，第三代架构可以用分布式*库*组合出整条数据摄取流水线。下面代码片段（[完整可运行示例见此](https://docs.ray.io/en/master/train/examples/train_linear_dataset_example.html#train-linear-dataset-example)）把一个 [Ray Dataset 流水线](https://docs.ray.io/en/latest/data/data.html)与一个分布式 [Ray Train 作业](https://docs.ray.io/en/latest/train/user-guides.html)组合起来：

```
1from ray.train import Trainer, get_dataset_shard
2
3# Distributed Preprocessing and Shuffle
4pipe = ray.data.read_parquet(path).window(size).repeat()
5pipe = pipe.map_batches(preprocess)
6pipe = pipe.random_shuffle_each_window()
7
8# Ray Train Function
9def train_func():
10    model = NeuralNetworkModel(...)
11    model = train.torch.prepare_model(model)
12    for epoch_data in get_dataset_shard().iter_epochs():
13        model.fit(epoch_data.to_torch(...))
14
15# Compose and Run
16trainer = Trainer(num_workers=3, backend="torch", use_gpu=True)
17result = trainer.run(train_func, dataset=dataset_pipeline)
```

上述代码虽然简化，却只花几行 Python 就表达了前述的 ML 摄取与训练流水线——完全无需摆弄分布式系统。底层上，Dataset 与 Train 库分别利用 Ray 任务与 actor 执行分布式数据预处理与 ML 训练。我们只需把 `dataset_pipeline` 对象的引用传给 Train，就完成了组合：

*上图为上述代码创建的 tasks 与 actors。*

相比第二代方案，第三代方案实现了：

- 更低的运维与开发开销：得益于第三代架构的可编程性，开发者可以在单个脚本中组合并*定制*整个分布式训练系统。
- 更好的性能：正如案例研究所示，该方法允许数据在内存中传递，从而削减开销。

## 代码逐段讲解

它究竟如何工作？从系统需求出发逐段走查上面的例子。

### 示例的需求

- 为了性能，我们希望数据在预处理、shuffle 与训练之间通过内存传递。
- 应支持摄取大于内存的数据集。下面的例子假设 2TB 数据集、1TB 内存的集群。
- 支持异构集群（例如含 GPU 训练节点与 CPU 预处理节点的集群）。

### 第 1 部分：分窗数据加载

先看代码的第一部分，它创建数据加载流水线。

```
1pipe = ray.data.read_parquet(path).window(size).repeat()
```

这里用 Ray Dataset 库创建一个 DatasetPipeline，从磁盘读取 parquet 数据。由于数据集（2TB）大于集群内存（1TB），我们用 .window() 每次处理 size=200GB 的窗口，为执行留出额外内存余量。由于希望无限循环数据集，之后再用 .repeat() 算子。

### 第 2 部分：预处理与 shuffle 流水线

流水线的第二部分应用分布式变换与洗牌操作。

```
1pipe = pipe.map_batches(preprocess)
2pipe = pipe.random_shuffle()
```

这是告诉 Ray 用给定的 `preprocess` 函数变换流水线中的记录，然后对整个窗口随机洗牌（例如每次 200GB），以避免落入核外（out-of-core）处理。到目前为止除了读取文件元数据外什么都没执行——我们是在搭建逻辑流水线。

### 第 3 部分：Ray Train 设置

接下来定义在每个 GPU worker 上运行、实现分布式训练的代码。每个 worker 都可以通过调用 `get_dataset_shard` 读取我们定义的流水线的某个分片。它用 `train.torch.prepare_model` 设置模型以参与分布式训练，然后在数据集的每个 epoch（repeat）数据上训练。

```
1def train_func():
2    model = NeuralNetworkModel(...)
3    model = train.torch.prepare_model(model)
4    for epoch_data in get_dataset_shard().iter_epochs():
5        model.fit(epoch_data.to_torch(...))
```

要创建训练 actor，我们实例化一个需要 3 个 GPU worker 的 ray.train.Trainer：

```
1trainer = Trainer(num_workers=3, backend="torch", use_gpu=True)
```

此时流水线已完全定义，训练 actor 已创建并被分配到集群中的 GPU，只差运行了。

### 第 3 部分：运行一切

这一行代码触发整条流水线的执行：

```
1result = trainer.run(train_func, dataset=dataset_pipeline)
```

集群里到底发生了什么？

- Ray Train 向每个 actor 发送 actor 方法调用，运行各自的训练函数。
- 每个 actor 从分给它的那个 `DatasetPipeline` 分片中拉数据（每个流水线分片都持有一个由 Datasets 为该 DatasetPipeline 实例创建的协调 actor 的句柄）。
- 这会触发对协调 actor 的调用。
a. 协调器调度流水线下一个窗口的执行，例如用集群 CPU 节点运行 Ray 任务来：
 i. 加载该窗口的数据（200GB）
 ii. 预处理数据
 iii. 随机洗牌
 iv. 切分数据并把各分片分配给 trainer actor
b. 协调器向 trainer actor 返回其被分配的 Dataset 分片的对象引用。
- trainer actor 用 `ray.get()` 从其 Dataset 分片取回数据块，生成 mini-batch 传给底层学习库（即 PyTorch）。

整体数据流可见下面的时间线图。数据一旦加载，shuffle 与执行便完全流水线化地进行：CPU 节点上的任务实现洗牌，GPU 上的 actor 做训练：

在 Ray 1.8 中亲手试用这些示例：

- [https://docs.ray.io/en/master/train/examples/train_linear_dataset_example.html](https://docs.ray.io/en/master/train/examples/train_linear_dataset_example.html)
- [https://docs.ray.io/en/master/data/examples/big_data_ingestion.html](https://docs.ray.io/en/master/data/examples/big_data_ingestion.html)

## 基准测试

在之前的博客中，我们讨论过内存传数与流水线化的[性能优势](https://www.anyscale.com/blog)，并通过消融实验展示了提升。此后，多位开源用户使用 Datasets 实现了大规模洗牌式 ML 摄取。我们呈现两个来自 [PyData Dataset 演讲](https://docs.google.com/presentation/d/1zANPlmrxQkjPU62I-p92oFO3rJrmjVhs73hL4YbM4C4/edit#slide=id.p1)的案例研究，均显示显著性能提升：

**案例 1：高科技 ML 平台初创公司**

Dask-on-Ray → Datasets → Horovod

- 即便在单机上，Dask-on-Ray + Datasets 也比 Pandas + S3 + Petastorm **快 8 倍**。
- **基准：**[Ludwig AI](https://ludwig.ai/latest/) 模型，NYC Taxi 数据集（5GB 子集），单台 g4dn.4xlarge 实例

*Shuffle 数据基准*

**案例 2：大型交通科技公司**

S3 → Datasets → Horovod

- 从 S3 读取的 Datasets 比从 S3 读取的 Petastorm **快 4 倍**
- **基准：**1.5TB 合成表格数据集，16 个节点（40 vCPU、180GB 内存），2 个 shuffle 窗口

*Petastorm vs Datasets*

## 结语

我们相信第三代 ML 架构将帮助工程师为大规模 ML 应用开发并标准化基础设施。本文展示了仅用一个 Python 脚本，就能以高性能方式把分布式数据预处理与训练连接起来。

而且，以真正第三代的方式，我们在不构建专门系统的前提下完成了这一切。我们用 Ray 交错执行两个独立的分布式库——这是第二代架构做不到的关键能力。这种可组合性之所以成立，是因为两个库都构建在 Ray 任务、actor、对象这一共同且可互操作的原语之上。

ML 摄取我们才刚刚起步——未来几个月 Ray Datasets 将从 beta 毕业，届时请关注新示例与性能增强——而这只是 Ray 可编程分布式计算的其中一面。欢迎了解调参、训练、服务等更多用例：[https://www.ray.io/](https://www.ray.io/)
