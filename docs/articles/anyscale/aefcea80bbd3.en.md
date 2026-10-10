---
vendor: anyscale
title: Ray Data 2.56: Improving Reliability for AI Data Pipelines
original_title: Ray Data 2.56: Improving Reliability for AI Data Pipelines
url: https://anyscale.com/blog/ray-data-256-updates
date: 2026-06-30
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 0267afda1257
---



Blog Detail

# Ray Data 2.56: Improving Reliability for AI Data Pipelines

By

Balaji Veeramani

,

Justin Yu

,

Ray Huang

,

Ayush Kumar

,

David Dai

,

Akshay Malik

,

Richard Liaw

and

Xinyuan Gui

|

June 30, 2026

Ray Data is one of the most common solutions for large-scale batch inference and training ingest pipelines. In Ray Data 2.56, we focused on two of the biggest reliability challenges users reported: out-of-memory (OOM) failures and unnecessary object spilling.

Both of these issues significantly slow down Ray Data pipelines and can often crash the job outright. For example, spilling can lead to out-of-disk errors, and significant memory pressure can cause the operating system to terminate critical driver processes.

In the development of Ray Data 2.56, we’ve spent time tackling both problems, aiming to provide users with a much more reliable experience. With the latest updates, we saw reduced OOMs and spilling on a variety of internal workloads

These gains were primarily driven by:

- **Memory-aware execution.** Ray Data now registers task memory more accurately, automatically tunes batch sizes for CPU `map_batches` workloads, and prioritizes terminating idle workers instead of critical processes during memory pressure.
- **Improved prefetching for training. **Ray Data now has less contention on the GPU stream and reduced memory usage on training threads, leading to better performance and stability.

We cover these changes and investigations in the sections below.

Try out Ray Data 2.56 by running `pip install -U ray`!

## LinkFewer OOMs, fewer crashes

Users running Ray Data prior to 2.56 often report seeing out-of-memory (OOM) errors, which sometimes also leads to Ray Data pipelines crashing. This is often due to memory oversubscription, where multiple tasks are run on the same node but requesting and provisioning more memory in aggregate than available on the machine. Memory oversubscription will then trigger the operating system to start killing processes, resulting in OOM warning messages and dying components and failing pipelines

To address this issue, we need to:

- Make sure Ray Data tasks register the appropriate amount of memory with the Ray scheduler
- Make sure that processes are terminated in order of lowest priority when out-of-memory errors do occur.

For memory registration, Ray Data 2.56 offers two main improvements. First, Ray Data features a flag `DataContext.get_current().default_map_logical_memory_enabled`. By setting this flag, all map tasks, which can include tasks executed under map_batches, flat_map, map, and reads, will have their logical memory configured to 4GB per CPU (if not already configured).

We also introduced a batch size tuning feature for CPU `map_batches` calls, enabled by passing `batch_size=”auto”` to your `map_batches` calls. Now, instead of users manually tuning batch sizes, the system profiles row sizes and automatically chooses a batch size such that the size of the inputs is within a safe threshold (in this case, under 16mb).

We’ve also improved Ray’s process management capabilities for high memory scenarios. Ray also now handles OOM process termination itself rather than leaving it to the underlying operating system. This lets Ray terminate idle workers instead of critical driver processes, preventing node deaths or unnecessary task kills. In addition, Ray also now reserves a fixed memory overhead for system processes like the raylet, giving more headroom for application memory usage.

To measure the impact of the changes, we ran an audio transcription benchmark [[link](https://github.com/ray-project/ray/blob/eeb194f3bdce65a7e21bba971e20aecc068d668f/release/nightly_tests/multimodal_inference_benchmarks/audio_transcription/ray_data_main.py)] on 8 g6.xlarge instances on AWS. Going from 2.55 to 2.56, OOMs dropped from **300+** to **0**, and end-to-end runtime fell from **1055s** to **447s**.

**2.55**

Unexpected System Level Worker Failures 2.55

**2.56**

Unexpected System Level Worker Failures 2.56

For a deeper guide on diagnosing and avoiding OOMs, see the new user guide: [https://docs.ray.io/en/master/data/how-to-avoid-ooms.html](https://docs.ray.io/en/master/data/how-to-avoid-ooms.html)

## LinkLess spilling, faster pipelines

Ray Data will also often have spilling occur on workloads such as training ingestion. In understanding these issues, a major cause of these issues is due to incorrect object store memory usage estimation.

Ray Data maintains an internal estimate of how much object store is currently used. This internal metric would also be used for triggering backpressure (i.e., signaling to upstream operators to slow down production). However, if the estimate is wrong, backpressure will misfire or not kick in at all, causing unnecessary spilling in the data pipeline.

Two of the main causes of this were **Pandas block formats** and, in the case of training dataloading, **not fully accounting for object store memory used by the prefetching and collation pipeline on the training workers.**

**Pandas block format: **Ray Data previously had multiple block formats for internal data representation -- one of those being Pandas Dataframes. Pandas Dataframes, however, did not provide an effective approach for accounting for the total memory size especially for generic Python objects. This would lead to inaccurate estimation. In Ray Data 2.56, we’ve consolidated block formats and now use PyArrow as the only block format, which has a much more accurate in-memory size estimation.

**Improving prefetching: **In our investigation into the reported spilling issues, we noticed that Ray Data prefetched multiple times the number of configured `prefetch_batches` per worker despite not having any improvement to throughput. The extra prefetched data contributes to object store memory usage and was mostly untracked by Ray Data’s usage estimation, which would cause spilling to disk if the data exceeded the object store spilling threshold.

Further, these prefetched batches were both pinned to object store and were not being accounted for in the object store memory usage, meaning that Ray Data was underestimating the amount of object store it was using on the training worker nodes.

By reducing the amount of prefetched batches and accounting for them properly, we were able to reduce object store usage leading to less spilling and lower peak object store memory usage.

We also noticed that prefetching from CPU to GPU was contending with the default CUDA stream, resulting in queuing of compute kernels on the GPU side and thus lowering training throughput. By reducing the amount of prefetching, we were also able to see training throughput improvements as well.

**Experiments: **In our internal object store memory [backpressure stress test](https://github.com/ray-project/ray/blob/14ee057472ffaa034ded79fbca4d7dcb82846119/release/nightly_tests/dataset/backpressure_benchmark.py#L4), we saw that spilling in 2.56 was eliminated (from 70GiB in 2.55), and peak object store memory reduced by 41%.

In another benchmark where dataloading is the bottleneck, we actually saw a 25% training step throughput increase due to reducing CUDA stream contention from prefetching fewer unnecessary batches to GPU. See this [PR](https://github.com/ray-project/ray/pull/63682) for more details.

peak object store memory

## LinkOther Reliability Improvements

Beyond the above two set of issues (OOMs, Spilling), we’ve introduced a variety of other reliability and stability improvements as well:

- **Multiple dataset support: **Ray Data 2.56 adds multiple dataset support with subcluster label scheduling. This unlocks common patterns like running validation (sync or [async](https://docs.ray.io/en/latest/train/user-guides/asynchronous-validation.html)) alongside training, dataset multi-tenancy, and keeping training-dataset preprocessing workers off your training GPU nodes. We document [these improvements here](https://docs.ray.io/en/master/data/concurrent-dataset-execution.html).
- **Training shuffle improvements: **We improved local shuffle buffer performance to reduce memory usage by up to 2.5x and 3x higher throughput on a variety of workloads. We also documented training shuffle [best practices here](https://docs.ray.io/en/master/data/shuffling-data.html#map-batches-shuffle).
- **Scheduling loop scalability: **We received reports of scheduling loop latency degradation at high worker volumes. We have landed a number of improvements to the scheduling loop to increase throughput, and currently see scheduling loop P90 latencies drop by up to 6x at large scale (2000+ workers). We are continuing to do work here in preparation of Ray Data 2.57.

## LinkLooking forward to 2.57

We still have more stability improvements and features slated for 2.57 – we’ll have another blog post when that is released. A quick preview of Ray Data 2.57 improvements include:

- Fully fixed accounting for prefetched training batches. 2.56 mitigated the issue and reduced budget overages significantly, but 2.57 will fix the root cause fully.
- Mid-epoch resumption for faster checkpoint-based recovery for training workloads
- Datasource V2, which will have much better schema handling and inference
- Fault-tolerant shuffles

Upgrade to 2.56 to pick up these stability and performance gains. As always, we'd love your feedback -- try out Ray today via `pip install -U ray`.

#### Table of contents

- [Fewer OOMs, fewer crashes](https://www.anyscale.com/blog/ray-data-256-updates#fewer-ooms,-fewer-crashes)
- [Less spilling, faster pipelines](https://www.anyscale.com/blog/ray-data-256-updates#less-spilling,-faster-pipelines)
- [Other Reliability Improvements](https://www.anyscale.com/blog/ray-data-256-updates#other-reliability-improvements)
- [Looking forward to 2.57](https://www.anyscale.com/blog/ray-data-256-updates#looking-forward-to-2.57)

#### Sharing

#### Tags

#### Sign up for product updates

#### Recommended content

#### Ray Summit 2026: Physical AI, RL, and the infrastructure that runs them all


#### Scaling Ray for AI workloads to 10k node clusters


#### Optimizing LLM Serving Efficiency: Moving Beyond KV Cache Reuse to Token-Load Awareness with Ray Serve LLM


## Explore Anyscale today

Build, run, and scale any AI workload on Ray with a multi-cloud platform built for production AI.

Start for Free

Talk to an expert
