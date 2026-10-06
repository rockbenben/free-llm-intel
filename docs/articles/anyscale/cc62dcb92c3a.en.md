---
vendor: anyscale
title: Autoscaling Large AI Models up to 5.1x Faster on Anyscale
original_title: 
url: https://anyscale.com/blog/autoscale-large-ai-models-faster
date: 2024-10-01
lang: en
captured: 2026-10-06
extractor: readability-v1
status: ok
body_sha: 29055d4e4421
---

Home

Blog

Blog Detail

# Autoscaling Large AI Models up to 5.1x Faster on Anyscale

By

Christopher Chou

,

Austin Kuo

,

Richard Liaw

,

Edward Oakes

and

Chris Sivanich

|

October 1, 2024

State of the art AI models are getting larger by the month, GPUs remain wildly expensive, and AI practitioners’ time is scarce. When you put these factors together, it becomes clear that efficiency is key for AI applications, both in development and production.

Unfortunately, a common experience for AI practitioners is to spend a lot of time waiting around for instances to boot, containers to pull, and models to load. As we’ll discuss below, it can take up to 10-12 minutes to provision a replica of [Meta-Llama-3-70B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-70B-Instruct) for inference using a typical setup of Ray Serve on Kubernetes.

image3

At Anyscale, we’ve optimized scale-up speed across the entire stack, leading to **up to 5.1x faster autoscaling for Meta-Llama-3-70B-Instruct** on the Anyscale platform when compared to running the same application using KubeRay on Amazon Elastic Kubernetes Service (EKS).

image4

Faster scale-up is a force multiplier for AI engineers and researchers using the Anyscale platform. They’re able to iterate quickly and avoid idle time in development and autoscale to meet workloads’ demands and avoid idle resources in production.

## LinkThe Problem: Large Containers, Large Models, and Pricey GPUs

Take the example of trying to run a popular open source large language model (LLM), [Meta-Llama-3-70B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-70B-Instruct), on Kubernetes using [vLLM](https://github.com/vllm-project/vllm). The typical startup sequence looks something like:

- Pod is created, Kubernetes cluster autoscaler adds a new node with a GPU: **1-1.5min**
- Container image (~12 GB including CUDA and vLLM dependencies) is pulled from container registry: **4-5min**
- Container starts, vLLM loads the model (~140 GB in FP16) from cloud storage: **4-5min**

Summed up, this means waiting up to **10-12 minutes** for a copy of the model to come online. Of course, there are various levels of caching that might speed up subsequent runs on the same hardware, but with sky-high GPU prices, it’s critical to relinquish GPU machines when they’re not actively in use.

In development, this drains the productivity of AI practitioners who find themselves waiting around for their instance to spin up, container to pull, and model to download.

In production, slow upscaling speeds lead to overprovisioning. Often, autoscaling policies are configured to handle variable incoming traffic patterns; the number of serving replicas is scaled up when traffic increases and scaled down when it decreases. However, if it takes too long to scale up in response to increased traffic, existing replicas can be overloaded, resulting in high response latencies or even failures.

A simple and common solution to this problem is to add more replicas in steady state to accommodate higher load while waiting for new replicas to come online and upscale more aggressively as traffic increases. However, when each replica of a model requires expensive GPUs to run, this can quickly become expensive.

Ideally, an online serving system can upscale quickly and be more responsive to incoming traffic, avoiding idle GPU resources.

## LinkAnyscale Autoscaling: Full-Stack Optimization

The [Anyscale Platform](https://www.anyscale.com/platform) is a fully-managed Ray solution. Every part of the infrastructure is tailored to provide the best user experience, high performance, and cost effectiveness to run AI applications using Ray. For upscaling speed, this manifests as a few key benefits:

- The Anyscale control plane is directly integrated with the Ray autoscaler, allowing it to react quickly to resource requests and make intelligent autoscaling decisions.
- The machine image and startup sequence have been tuned to optimize instance boot times.
- When pulling container images, Anyscale uses a custom container image format and client to reduce image pull times.
- Anyscale provides a library for fast model loading, streaming tensors directly from cloud storage onto the GPU.

To demonstrate the effect of these optimizations, we ran an experiment to measure the time taken to scale up a single [Ray Serve](https://www.anyscale.com/library/ray-serve) replica to host an LLM model for inference using [vLLM](https://github.com/vllm-project/vllm) on AWS. We repeated this experiment for two representative models:

- Mistral-7B-Instruct-v0.1 on a single NVIDIA A10G GPU (1x AWS g5.8xlarge instance). Model weights are about 14 GB in FP16.
- Meta-Llama-70B-Instruct on four NVIDIA L40S GPUs using tensor parallelism (1x AWS g6e.12xlarge instance). Model weights are about 140 GB in FP16.

On Anyscale, the application is run as a [Service](https://docs.anyscale.com/platform/services/) and on KubeRay, it’s run as a [RayService](https://docs.ray.io/en/latest/serve/production-guide/kubernetes.html). In both cases, there is no local caching involved; a new instance needs to be booted, the container pulled from a registry, and the model weights loaded from remote cloud storage.

image5

Anyscale is able to scale up a new replica end-to-end in only **75 seconds for Mistral-7B-Instruct-v0.1 **and **107 seconds for Meta-Llama-70B-Instruct**. This represents a **4.3x** and **5.1x** improvement when compared to KubeRay running on Amazon EKS for this workload, respectively.

### LinkCustom Container Format and Client

One of the key differences that enables this speedup is Anyscale’s custom container image format and runtime. The first time a new container image is used by a customer on the Anyscale platform, the image is converted and stored in an optimized format that is used to make subsequent runs with the same image in the same region lightning fast.

To show the benefit of this optimized format in isolation, we ran an experiment to test the time that it takes to pull a container image and start a container on a freshly-booted g5.8xlarge instance on Amazon EKS and the Anyscale platform.

- The two images used are a ray:2.34.0 default image (~6.2 GB) and a custom image that uses ray:2.34.0 as its base and installs vLLM and its required dependencies (~12.8 GB).
- On Anyscale and EKS, the instances are running in the us-west-2 region and the source container images are hosted in an Amazon Elastic Container Registry in the same region and same AWS account.
- The Amazon EKS node group is configured to use GP3 EBS volumes with 3,000 provisioned IOPs.

image7

In this experiment, Anyscale is able to pull the container image up to **30x** faster than AWS EKS for a 6GB image and up to **14x** faster for a 13GB image.

### LinkOptimized Direct-to-GPU Loading

Anyscale also provides an optimized client to load model weights in the [safetensors](https://github.com/huggingface/safetensors) format from remote storage directly onto a GPU. This technique leverages pipeline parallelism, avoiding a synchronous copy of the full model weights to disk, followed by loading them to CPU memory, and finally loading to GPU memory. Instead, model weights are streamed chunk-by-chunk from remote storage to CPU memory to GPU memory. You can read more about the technical details in this [previous blog post](https://www.anyscale.com/blog/loading-llama-2-70b-20x-faster-with-anyscale-endpoints) and read the latest documentation [here](https://docs.anyscale.com/platform/services/fast-loading).

To show the benefit of this faster model loading technique in isolation, we measured the time that it takes vLLM to start up and load a model for inference. The models and hardware used are the same as the above end-to-end experiment:

- Mistral-7B-Instruct-v0.1 on a single NVIDIA A10G GPU (1x AWS g5.8xlarge instance). Model weights are about 14 GB in FP16.
- Meta-Llama-70B-Instruct on four NVIDIA L40S GPUs using tensor parallelism (1x AWS g6e.12xlarge instance). Model weights are about 140 GB in FP16.

image1

When compared to a typical workflow of using the AWS S3 CLI to download to local disk (with configuration options configured to maximize throughput) and the [safetensors](https://github.com/huggingface/safetensors) library to load from local disk to GPU, Anyscale improves the startup and model loading time of vLLM by up to **2x for Mistral-7B-Instruct-v0.1 **and up to **4.8x for Meta-Llama-70B-Instruct**.

## LinkConclusion

The [Anyscale Platform](https://www.anyscale.com/platform) implements full-stack optimizations to enable blazing fast autoscaling. For Meta-Llama-3-70B-Instruct, this leads to **up to 5.1x faster autoscaling** when compared to running the same application using KubeRay on Amazon EKS.

These optimizations make AI practitioners more effective and inference services less expensive to operate.

Get started on the Anyscale platform for free today at: [https://www.anyscale.com/](https://www.anyscale.com/).

#### Table of contents

- [The Problem: Large Containers, Large Models, and Pricey GPUs](https://www.anyscale.com/blog/autoscale-large-ai-models-faster#the-problem:-large-containers,-large-models,-and-pricey-gpus)
- [Anyscale Autoscaling: Full-Stack Optimization](https://www.anyscale.com/blog/autoscale-large-ai-models-faster#anyscale-autoscaling:-full-stack-optimization)
- [Custom Container Format and Client](https://www.anyscale.com/blog/autoscale-large-ai-models-faster#custom-container-format-and-client)
- [Optimized Direct-to-GPU Loading](https://www.anyscale.com/blog/autoscale-large-ai-models-faster#optimized-direct-to-gpu-loading)
- [Conclusion](https://www.anyscale.com/blog/autoscale-large-ai-models-faster#conclusion)

#### Sharing

#### Tags

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
