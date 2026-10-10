---
vendor: anyscale
title: Deep Dive: Data Ingest in a Third Generation ML Architecture
original_title: Deep Dive: Data Ingest in a Third Generation ML Architecture
url: https://anyscale.com/blog/deep-dive-data-ingest-in-a-third-generation-ml-architecture
date: 2021-11-30
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: c829dfbcb655
---



Blog Detail

# Deep Dive: Data Ingest in a Third Generation ML Architecture

By

Eric Liang

,

Chen Shen

,

Clark Zinzow

and

Waleed Kadous

|

November 30, 2021

This is part 3 of our series on [third generation ML architectures](https://www.anyscale.com/blog/the-third-generation-of-production-ml-architectures). In the previous post, we talked about how distributed libraries allow improved [performance](https://www.anyscale.com/blog) by exploiting the full bandwidth of distributed memory, and giving greater programmability. But how does that *actually work*? What does the code look like?

In this post, we’ll be looking at a concrete example with code samples: ML ingest with [Ray Datasets](https://docs.ray.io/en/latest/data/data.html) and [Ray Train](https://docs.ray.io/en/latest/train/user-guides.html).

- We show how these distributed libraries can be woven together with just a few lines of Python--- a key capability not possible in 2nd gen architectures.
- We examine how Datasets and Train use the interoperable primitives of Ray tasks, actors, and objects to enable this composable architecture.

Runnable scripts are available that can be adapted for use on your own Ray cluster.

## LinkSmall Data Training

To set the stage, let's consider ML training in the small-data setting. These kinds of pipelines are quite simple since all data fits in memory, and the overhead of shuffling is minimal. You can express it as just a few lines of pseudocode:

```
1data = load_data()
2preprocess(data)
3for each epoch:
4    random_shuffle(data)
5    train_one_epoch(data)
```

Let's review the steps above:

- **Loading**: Small data is typically read from files on local disk into memory. It may be streamed from files in some cases.
- **Preprocessing**: Apply simple transformations (i.e., feature engineering).
- **Shuffling**: Randomly permute the order of items in the dataset. Shuffling randomly for each epoch is [important](https://arxiv.org/abs/1709.10432) for stochastic gradient descent.
- **Training**: Fit the model over the data (e.g., using a framework like [PyTorch](https://pytorch.org/) or [Horovod](https://horovod.readthedocs.io/en/stable/index.html)).

## LinkBig Data Training Challenges

Training models over big data adds additional needs around (1) distributed preprocessing, (2) distributed shuffling to improve convergence rates, and (3) pipelined execution with ML training:

- **Distributed preprocessing**: The data ingestion requirements of large-scale training can be substantial, motivating specialized systems such as [DPP](https://arxiv.org/abs/2108.09373) from Facebook and [Petastorm](https://www.uber.com/blog/petastorm/) from Uber. The systems allow for preprocessing to be off-loaded to separate nodes in the cluster distinct from the GPU machines. Some portion of preprocessing can be done offline, but it is desirable for data to be "minimally preprocessed" for flexibility.
- **Distributed shuffling**: It is important for the dataset to be shuffled (randomly re-ordered) for each epoch of training. This can significantly [improve the convergence of SGD](https://arxiv.org/abs/1709.10432), but is challenging in the [distributed setting](https://en.wikipedia.org/wiki/MapReduce). While *global shuffling* is optimal, typically solutions like TensorFlow/Pytorch data loaders and Petastorm only perform local shuffling due to the engineering complexity of stitching together large-scale data shuffles with ML training.
- **Pipelining data processing and training**: Due to limited cluster memory sizes and the need for random per-epoch shuffles, we see that preprocessing and shuffle computations may need to be interleaved with training. This is only possible today in specialized systems like DPP (e.g., you cannot trivially connect Spark's distributed shuffle with Horovod, since they are separate distributed systems).
In other words, our simple pipeline became hard since components necessarily become distributed and pipelined for performance:

In other words, our simple pipeline became hard since components necessarily become distributed and pipelined for performance:

```
1data = load_data()         # larger than cluster memory :(
2preprocess(data)           # distributed transforms :(
3for each epoch:
4    random_shuffle(data)   # distributed shuffle :(
5    train_one_epoch(data)  # pipelined with above distributed steps :(
```

## LinkSecond Generation Approach

Let's briefly consider how we could compose existing distributed systems to solve this distributed ingest problem. We need to set up a Spark cluster for data processing, a Horovod cluster for training, a coordinator service for control plane operations, and external storage for data plane communication.

2nd Generation - Data Ingest Problem

The training pipeline would work in the following steps. First, the coordinator service would (1) submit a shuffle job to the Spark cluster, which (2) reads and writes data out to external storage. Next, the Horovod data reader (e.g., Petastorm) would (3) fetch the written dataset location from the coordinator and (4) read the shuffle data for training. These steps would repeat for each epoch of training, and can run concurrently to optimize execution latencies.

The disadvantages of the 2nd generation approach are:

- [Lack of programmability](https://www.anyscale.com/blog/the-third-generation-of-production-ml-architectures): need to setup and manage 3+ separate distributed systems. It's also hard to orchestrate with workflow systems due to the interleaving of shuffle with training.
- [Performance overhead](https://www.anyscale.com/blog): intermediate data written to external storage since it needs to cross between distributed systems.

## LinkThird Generation Approach

In contrast, with a 3rd gen architecture we can compose the entire data ingest pipeline using distributed *libraries*. In the snippet below [(see here for a full runnable example)](https://docs.ray.io/en/master/train/examples/train_linear_dataset_example.html#train-linear-dataset-example), we compose a [Ray Dataset Pipeline](https://docs.ray.io/en/latest/data/data.html) with a distributed [Ray Train Job](https://docs.ray.io/en/latest/train/user-guides.html):

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

The above snippet, while simplified, is able to express the aforementioned ML ingest and training pipeline with just a few lines of Python code--- without any need to wrangle distributed systems. Under the hood, the Dataset and Train libraries leverage Ray Tasks and Actors respectively to execute distributed data preprocessing and ML training. We are able to compose them by just passing a reference to the `dataset_pipeline` object to Train:

3rdGenTasks andActors

The above figure illustrates the tasks and actors created by the above code snippet.

Compared to the 2nd gen approach, the 3rd gen approach achieves:

- Lower operational and development overheads: developers can compose and *customize* the entire distributed training system in a single script thanks to the programmability of a 3rd gen architecture.
- Better performance: as we'll see in the case studies, this approach reduces overheads by allowing data to be passed in-memory.

## LinkCode Walkthrough

So how does it work? Let's walk through the above example starting with the system requirements.

### LinkRequirements for the Example

- For performance, we want data to be passed in-memory between preprocessing, shuffle, and training.
- We should support ingestion of a dataset that is larger than memory. In the example below, we'll assume a 2TB dataset, and a cluster with 1TB of memory.
- Support for heterogeneous clusters (e.g., a cluster with GPU training nodes and CPU preprocessing nodes).

### LinkPart 1: Windowed data loading

Let's look at the first part of the code above, which creates a data loading pipeline.

```
1pipe = ray.data.read_parquet(path).window(size).repeat()
```

This uses the Ray Dataset library to create a DatasetPipeline reading our parquet data from disk. Since the dataset (2TB) is larger than our cluster memory (1TB), we use the .window() function to process windows of size=200GB at a time, leaving extra memory headroom for execution. Since we want to loop over the dataset indefinitely, we use the .repeat() operator after that.

### LinkPart 2: Preprocessing and shuffle pipeline

The second part of the pipeline is applying the distributed transform and shuffling operations.

```
1pipe = pipe.map_batches(preprocess)
2pipe = pipe.random_shuffle()
```

This is telling Ray to transform records in the pipeline with a given `preprocess` function, and then shuffling the entire window randomly (e.g., 200GB at a time), to avoid going out of core. So far, nothing has been executed beyond reading the file metadata--- we're building up a logical pipeline.

### LinkPart 3: Ray Train Setup

Next we define the code that is run on each GPU worker and implements distributed training. Each worker can read a particular split of the pipeline we defined by calling `get_dataset_shard`. It sets up a model using `train.torch.prepare_model` to participate in distributed training. Then, it trains over the data in each epoch (repeat) of the dataset.

```
1def train_func():
2    model = NeuralNetworkModel(...)
3    model = train.torch.prepare_model(model)
4    for epoch_data in get_dataset_shard().iter_epochs():
5        model.fit(epoch_data.to_torch(...))
```

To create the training actors, we create a ray.train.Trainer that requires 3 GPU workers:

```
1trainer = Trainer(num_workers=3, backend="torch", use_gpu=True)
```

At this point, our pipeline is fully defined, and our training actors have been created and assigned GPUs in the cluster, we just need to run it.

### LinkPart 3: Running everything

This line of code triggers the execution of the entire pipeline:

```
1result = trainer.run(train_func, dataset=dataset_pipeline)
```

So what's happening in the cluster?

- Ray Train sends actor method calls to each actor to run its given training function.
- Each actor pulls data from the `DatasetPipeline` shard given to it (each pipeline shard contains a handle to a coordinator actor created by Datasets for this DatasetPipeline instance).
- This triggers actor calls to the coordinator actor.
a. The coordinator schedules execution of the next window of the pipeline, e.g., Ray tasks that use CPU nodes in the cluster to:
 i. load data for the window (200GB)
 ii. preprocess the data
 iii. randomly shuffle the data
 iv. split up the data and assign splits to trainer actors
b. The coordinator returns to the trainer actors object references to their assigned Dataset split.
- The trainer actors `ray.get()` data blocks from their Dataset split and generate mini-batches to pass to the underlying learning library (i.e., PyTorch).

You can visualize the overall dataflow in the following timeline diagram. Once data is loaded, shuffle and execution proceed in a fully pipelined way, leveraging tasks running on CPU nodes to implement shuffling, and actors running on GPUs for training:

dataflow

Try it out yourself with these examples in Ray 1.8:

- [https://docs.ray.io/en/master/train/examples/train_linear_dataset_example.html](https://docs.ray.io/en/master/train/examples/train_linear_dataset_example.html)
- [https://docs.ray.io/en/master/data/examples/big_data_ingestion.html](https://docs.ray.io/en/master/data/examples/big_data_ingestion.html)

## LinkBenchmarks

In a previous blog post, we discussed the [performance advantages](https://www.anyscale.com/blog) of passing data in-memory and with pipelining and showed improvements in an ablation study. Since then, Datasets has been used by several open source users to implement large-scale shuffled ML ingest. We present two case studies from our [PyData Dataset talk](https://docs.google.com/presentation/d/1zANPlmrxQkjPU62I-p92oFO3rJrmjVhs73hL4YbM4C4/edit#slide=id.p1) showing significant performance improvements:

**Case Study 1: high-tech ML platform startup**

Dask-on-Ray → Datasets → Horovod

- Dask-on-Ray and Datasets was **8x faster** than Pandas + S3+ Petastorm, even on a single machine.
- **Benchmark:** [Ludwig AI](https://ludwig.ai/latest/) model, NYC Taxi dataset (5 GB subset), single g4dn.4xlarge instance

Shuffled Data Benchmark

**Case Study 2: large transport tech company**

S3 → Datasets → Horovod

- Datasets from S3 was **4x faster** than Petastorm from S3
- **Benchmark:** 1.5 TB synthetic tabular dataset, 16 nodes (40 vCPUs, 180 GB RAM), 2 shuffle windows

Petastorm Datasets

## LinkConclusion

We believe 3rd gen ML architectures will help engineers develop and standardize infrastructure for large-scale ML apps. This blog demonstrated that with just a single Python script, we can connect distributed data preprocessing with training in a highly performant way.

Moreover, in true 3rd-gen fashion, we were able to do the above without building a specialized system. We used Ray to interleave execution of two independent distributed libraries--- a key capability not possible in 2nd gen architectures. This composability is possible since both libraries are built on the common and interoperable primitives of Ray tasks, actors, and objects.

While we're just getting started with ML ingest-- look for new examples and performance enhancements as Ray Datasets graduates from beta in the next few months--- this is just one aspect of programmable distributed compute with Ray. Check out other use cases in Tuning, Training, Serving, and more here: [https://www.ray.io/](https://www.ray.io/)

#### Table of contents

- [Small Data Training](https://www.anyscale.com/blog/deep-dive-data-ingest-in-a-third-generation-ml-architecture#small-data-training)
- [Big Data Training Challenges](https://www.anyscale.com/blog/deep-dive-data-ingest-in-a-third-generation-ml-architecture#big-data-training-challenges)
- [Second Generation Approach](https://www.anyscale.com/blog/deep-dive-data-ingest-in-a-third-generation-ml-architecture#second-generation-approach)
- [Third Generation Approach](https://www.anyscale.com/blog/deep-dive-data-ingest-in-a-third-generation-ml-architecture#third-generation-approach)
- [Code Walkthrough](https://www.anyscale.com/blog/deep-dive-data-ingest-in-a-third-generation-ml-architecture#code-walkthrough)
- [Requirements for the Example](https://www.anyscale.com/blog/deep-dive-data-ingest-in-a-third-generation-ml-architecture#requirements-for-the-example)
- [Part 1: Windowed data loading](https://www.anyscale.com/blog/deep-dive-data-ingest-in-a-third-generation-ml-architecture#part-1:-windowed-data-loading)
- [Part 2: Preprocessing and shuffle pipeline](https://www.anyscale.com/blog/deep-dive-data-ingest-in-a-third-generation-ml-architecture#part-2:-preprocessing-and-shuffle-pipeline)
- [Part 3: Ray Train Setup](https://www.anyscale.com/blog/deep-dive-data-ingest-in-a-third-generation-ml-architecture#part-3:-ray-train-setup)
- [Part 3: Running everything](https://www.anyscale.com/blog/deep-dive-data-ingest-in-a-third-generation-ml-architecture#part-3:-running-everything)
- [Benchmarks](https://www.anyscale.com/blog/deep-dive-data-ingest-in-a-third-generation-ml-architecture#benchmarks)
- [Conclusion](https://www.anyscale.com/blog/deep-dive-data-ingest-in-a-third-generation-ml-architecture#conclusion)

#### Sharing

#### Tags

Ray Train

,

Ray Datasets

#### Sign up for product updates

#### Recommended content

#### Ray Summit 2026: Physical AI, RL, and the infrastructure that runs them all


#### Scaling Ray for AI workloads to 10k node clusters


#### Optimizing LLM Serving Efficiency: Moving Beyond KV Cache Reuse to Token-Load Awareness with Ray Serve LLM


## Explore Anyscale today

Build, run, and scale any AI workload on Ray with a multi-cloud platform built for production AI.

Start for Free

Talk to an expert
