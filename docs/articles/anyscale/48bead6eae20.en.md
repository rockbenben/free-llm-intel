---
vendor: anyscale
title: Ray Datasets for large-scale machine learning ingest and scoring
original_title: Ray Datasets for large-scale machine learning ingest and scoring
url: https://anyscale.com/blog/ray-datasets-for-machine-learning-training-and-scoring
date: 2022-02-14
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: d678716d9f56
---

Home

Blog

Blog Detail

# Ray Datasets for large-scale machine learning ingest and scoring

By

Clark Zinzow

,

Alex Wu

,

Jiajun Yao

,

Eric Liang

and

Chen Shen

|

February 14, 2022

We're happy to introduce Ray Datasets, a data loading and preprocessing library built on Ray. Datasets leverages Ray’s task, actor, and object APIs to enable large-scale machine learning (ML) ingest, training, and inference, all within a single Python application.

blog-ray-datasets-1

In a nutshell, Datasets:

- Is the standard way to **load distributed data into Ray**, supporting popular storage backends and file formats.
- Supports common **ML preprocessing operations **including basic parallel data transformations such as map, batched map, and filter, and global operations such as sort, shuffle, groupby, and stats aggregations.
- Supports operations requiring stateful setup and GPU acceleration.
- Works seamlessly with Ray-integrated **data processing libraries** (Spark, Pandas, NumPy, Dask, Mars) and **ML frameworks** (TensorFlow, Torch, Horovod).

In this blog post, we will survey the current state of distributed training and model scoring pipelines and give an overview of Ray Datasets and how it solves problems present in the status quo. If that leaves you wanting more, be sure to [register for our upcoming webinar](https://www.anyscale.com/events/2022/02/16/ray-datasets-scalable-data-preprocessing-for-distributed-ml), where you can get a first-hand look at Datasets in action. With that, let’s dive in!

## LinkCurrent ML training and inference pipelines

### LinkThe status quo pipeline

Today, users often stitch together their training pipeline using various distributed compute frameworks. While this approach has its advantages in re-using existing systems, there are several drawbacks, which we covered in our blog post on [data ingest in third-gen ML architectures](https://www.anyscale.com/blog/deep-dive-data-ingest-in-a-third-generation-ml-architecture).

Training pipeline status quo: workflow orchestration frameworks are required to orchestrate this multi-language, multi-job pipeline with intermediate data persistence.

blog-ray-datasets-2

### LinkThe vision

Ray is enabling [simple Python scripts](https://www.anyscale.com/blog/the-third-generation-of-production-ml-architectures) to replace these pipelines, avoiding their tradeoffs and also [improving performance](https://www.anyscale.com/blog/why-third-generation-ml-platforms-are-more-performant). Ray Datasets are a key part of this vision, acting as the "distributed Arrow" format for exchanging data between distributed steps in Ray.

## LinkIntroduction to Ray Datasets

### LinkDatasets in a nutshell

Datasets is fundamentally a distributed dataset abstraction, where the underlying data blocks (partitions) are distributed across a Ray cluster, sitting in distributed memory.

A Dataset holds references to one or more in-memory data blocks, distributed across a Ray cluster.

blog-ray-datasets-3

This distributed representation allows for the Dataset to be built by distributed parallel tasks, each pulling a block’s worth of data from a source (e.g., S3) and putting the block into the node’s local object store, with the client-side Dataset object holding references to the distributed blocks. Operations on the client-side Dataset object then result in parallel operations on those blocks.

A Dataset’s blocks can contain data of any modality, including text, arbitrary binary bytes (e.g., images), and numerical data; however, the full power of Datasets is unlocked when used with tabular data. In this case, each block consists of a partition of a distributed table, and these row-based partitions are represented as Arrow Tables under the hood, yielding a distributed Arrow dataset.

Visualization of a Dataset that has three Arrow table blocks, with each block holding 1000 rows.

blog-ray-datasets-4

### LinkHow does Datasets fit into my training pipeline?

Datasets is **not** intended as a replacement for generic data processing systems like Spark. Datasets is meant to be the last-mile bridge between ETL pipelines and distributed applications running on Ray.

Ray Datasets is the last-mile data bridge to a Ray cluster.

blog-ray-datasets-5

This bridge becomes extra powerful when using Ray-integrated DataFrame libraries for your data processing stage, as this allows you to run a full data-to-ML pipeline on top of Ray, eliminating the need to materialize data to external storage as an intermediate step. Ray serves as the universal compute substrate for your ML pipeline, with Datasets forming the distributed data bridge between pipeline stages.

When the entire pipeline runs on Ray, distributed data can seamlessly pass from relational data processing to model training without touching a disk or centralized data broker.

blog-ray-datasets-6

Check out our [blog post on ingest in third-generation ML architectures](https://www.anyscale.com/blog/deep-dive-data-ingest-in-a-third-generation-ml-architecture) for more on how this works under the hood.

### LinkBasic features

#### LinkScalable parallel I/O

Datasets aims to be a universal parallel data loader, data writer, and exchange format, providing a narrow data waist for Ray applications and libraries to interface with.

blog-ray-datasets-7

This is accomplished by heavily leveraging Arrow’s I/O layer, using Ray’s high-throughput task execution to parallelize Arrow’s high-performance single-threaded I/O. The Datasets I/O layer has scaled to [multi-petabyte data ingest jobs](https://www.youtube.com/watch?v=h7svj_oAY14) in production at Amazon.

Datasets’ scalable I/O is all available behind a [dead-simple API](https://docs.ray.io/en/latest/data/dataset.html), expressible via a single call: `ray.data.read_<format>()`.

#### LinkData format compatibility

With Arrow’s I/O layer comes support for many of your favorite tabular file formats (JSON, CSV, Parquet) and storage backends (local disk, S3, GCS, Azure Blog Storage, HDFS). Beyond tabular data, we’ve added support for parallel reads and writes of NumPy, text, and binary files. This comprehensive support for reading many formats from [many external sources](https://docs.ray.io/en/latest/data/dataset.html#datasource-compatibility-matrices), coupled with the extremely scalable parallelization scheme, makes Datasets the preferred way to ingest large amounts of data into a Ray cluster.

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

#### LinkData framework compatibility

In addition to storage I/O, Datasets also allows for bidirectional in-memory data exchange with many popular distributed frameworks when they are run on Ray, such as Spark, Dask, Modin, and Mars, as well as Pandas and NumPy for small local in-memory data. For convenient ingestion of data into model trainers, Datasets provides an exchange API for both PyTorch and TensorFlow, yielding the familiar framework-specific datasets, [torch.util.data.IterableDataset](https://pytorch.org/docs/stable/data.html#torch.utils.data.IterableDataset) and [tf.data.Dataset](https://www.tensorflow.org/api_docs/python/tf/data/Dataset).

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
```

#### LinkLast-mile preprocessing

Datasets offers convenient [data preprocessing functionality](https://docs.ray.io/en/master/data/dataset-ml-preprocessing.html) for common last-mile transformations that you wish to perform right before training your model or doing batch inference. “Last-mile preprocessing” covers transformations that differ across models or that involve per-run or per-epoch randomness. Datasets allow you to do these operations in parallel while keeping everything in (distributed) memory with `.map_batches(fn)`, with no need to persist the results back to storage before starting to train your model or do batch inference.

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
```

#### LinkStateful GPU tasks

To enable [batch inference on large datasets](https://docs.ray.io/en/master/data/advanced-pipelines.html#example-pipelined-batch-inference), Datasets supports running stateful computations on GPUs. This is quite simple: instead of calling `.map_batches(fn)` with a stateless function, call `.map_batches(callable_cls, compute="actors")`. The callable class will be instantiated on a Ray actor, and re-used multiple times to transform input batches for inference:

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

### LinkPipelined compute with Datasets

Reading into, transforming, and consuming/writing out of your Dataset creates a series of execution stages. By default, these stages are eagerly executed via blocking calls, which provides an easy-to-understand bulk synchronous parallel execution model and maximal parallelism for each stage:

blog-ray-datasets-8

However, this doesn’t allow you to overlap computation across stages: when the first data block is done loading, we can’t start transforming it until all other data blocks are done being loaded as well. If different stages require different resources, this lock-step execution may over-saturate the current stage’s resources while leaving all other stage’s resources idle. Pipelining solves this problem:

blog-ray-datasets-9

Pipelining is natively supported in the Datasets API: simply call **.window()** or **.repeat()** to generate a DatasetPipeline that can be read, transformed, and written just like a normal Dataset. This means you can easily incrementally process or stream data for ML training and inference. Read more about it in our [pipelining docs](https://docs.ray.io/en/master/data/key-concepts.html#dataset-pipelines).

### LinkWhy build Datasets on top of Ray, anyway?

Ray has a robust [distributed dataplane](https://docs.google.com/document/d/1lAy0Owi-vPz2jEqBSaHNQcy2IBSDEHyXNOQZlGuj93c/preview), combining decentralized scheduling with a best-in-class distributed object layer, featuring:

- **Efficient zero-copy reads** via shared memory for workers on the same node, obviating the need for serialization when sharing data across worker processes.
- **Locality-aware scheduling**, where data-intensive tasks are scheduled onto the node that has the most of the task’s required data already local.
- **Resilient object transfer protocols**, with a [memory manager](https://www.anyscale.com/blog/analyzing-memory-management-and-performance-in-dask-on-ray) that ensures prefetching and forward progress while bounding the amount of memory usage.
- **A fast data transport implementation**, transferring data chunks in parallel in order to maximize transfer throughput.

Given Ray's distributed dataplane, building a library like Datasets becomes comparatively simple. Datasets delegates most of the heavy lifting to the Ray dataplane, focusing on providing higher-level features such as convenient APIs, data format support, and stage pipelining.

## LinkHow is the community using Datasets?

The Ray Datasets project is still in its early stages. Post-beta, we plan to add a number of additional features, including:

- Support for more data formats and integrations
- Reducing object store memory overhead in large-scale pipelines
- Improved performance and scalability of shuffle (scaling to 100+TB)

That said, users are already finding Datasets to be providing distinct advantages today.

### LinkCase study 1: ML training and inference vs Petastorm/Pandas

One organization utilizing Ray for their ML infra has found Datasets to be effective at speeding up their training and inference workloads at small scales:

**At training**, Ray Datasets was 8x faster than Pandas + S3 + Petastorm when used from a single GPU instance, showing reduction in serialization overheads:

Benchmark: NYC Taxi dataset (5 GB subset), single g4dn.4xlarge instance.

blog-ray-datasets-10

**At inference**, Dask-on-Ray + Datasets + Torch was 5x faster than Pandas + Torch again even when evaluating on a single machine:

Benchmark: NYC Taxi dataset (5 GB subset), single r5d.4xlarge instance

blog-ray-datasets-11

### LinkCase study 2: ML ingest at large scale

Another ML platform group evaluating a larger scale S3 → Datasets → Horovod data pipeline found significant gains when scaling their ingest pipeline to a cluster of machines. In this use case, not only did Datasets provide higher throughput, but better shuffle quality since it supported a true distributed shuffle.

## LinkConclusion

To summarize, Datasets simplifies ML pipelines by providing a flexible and scalable API for working with data within Ray. We're just getting started with Datasets, but users are already finding it effective for training and inference at a variety of scales. [Check out the documentation](https://docs.ray.io/en/master/data/dataset.html) or [register for our upcoming webinar](https://www.anyscale.com/events/2022/02/16/ray-datasets-scalable-data-preprocessing-for-distributed-ml) to get a first-hand look at Datasets in action.

*This post is based on Alex Wu and Clark Zinzow's talk, “*[*Unifying Data preprocessing and training with Ray Datasets*](https://www.youtube.com/watch?v=wl4tvru9_Cg)*,” from PyData Global 2021.*

#### Table of contents

- [Current ML training and inference pipelines](https://www.anyscale.com/blog/ray-datasets-for-machine-learning-training-and-scoring#current-ml-training-and-inference-pipelines)
- [The status quo pipeline](https://www.anyscale.com/blog/ray-datasets-for-machine-learning-training-and-scoring#the-status-quo-pipeline)
- [The vision](https://www.anyscale.com/blog/ray-datasets-for-machine-learning-training-and-scoring#the-vision)
- [Introduction to Ray Datasets](https://www.anyscale.com/blog/ray-datasets-for-machine-learning-training-and-scoring#introduction-to-ray-datasets)
- [Datasets in a nutshell](https://www.anyscale.com/blog/ray-datasets-for-machine-learning-training-and-scoring#datasets-in-a-nutshell)
- [How does Datasets fit into my training pipeline?](https://www.anyscale.com/blog/ray-datasets-for-machine-learning-training-and-scoring#how-does-datasets-fit-into-my-training-pipeline?)
- [Basic features](https://www.anyscale.com/blog/ray-datasets-for-machine-learning-training-and-scoring#basic-features)
- [Pipelined compute with Datasets](https://www.anyscale.com/blog/ray-datasets-for-machine-learning-training-and-scoring#pipelined-compute-with-datasets)
- [Why build Datasets on top of Ray, anyway?](https://www.anyscale.com/blog/ray-datasets-for-machine-learning-training-and-scoring#why-build-datasets-on-top-of-ray,-anyway?)
- [How is the community using Datasets?](https://www.anyscale.com/blog/ray-datasets-for-machine-learning-training-and-scoring#how-is-the-community-using-datasets?)
- [Case study 1: ML training and inference vs Petastorm/Pandas](https://www.anyscale.com/blog/ray-datasets-for-machine-learning-training-and-scoring#case-study-1:-ml-training-and-inference-vs-petastorm/pandas)
- [Case study 2: ML ingest at large scale](https://www.anyscale.com/blog/ray-datasets-for-machine-learning-training-and-scoring#case-study-2:-ml-ingest-at-large-scale)
- [Conclusion](https://www.anyscale.com/blog/ray-datasets-for-machine-learning-training-and-scoring#conclusion)

#### Sharing

#### Tags

Ray Datasets

#### Sign up for product updates

#### Recommended content

#### Ray Summit 2026: Physical AI, RL, and the infrastructure that runs them all

Read more

#### Scaling Ray for AI workloads to 10k node clusters

Read more

#### Optimizing LLM Serving Efficiency: Moving Beyond KV Cache Reuse to Token-Load Awareness with Ray Serve LLM

Read more

## Explore Anyscale today

Build, run, and scale any AI workload on Ray with a multi-cloud platform built for production AI.

Start for Free

Talk to an expert
