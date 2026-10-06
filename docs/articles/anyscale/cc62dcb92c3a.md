---
vendor: anyscale
title: 在 Anyscale 上将大型 AI 模型的自动扩缩容提速至多 5.1 倍
original_title: Autoscaling Large AI Models up to 5.1x Faster on Anyscale
url: https://anyscale.com/blog/autoscale-large-ai-models-faster
date: 2024-10-01
lang: zh
captured: 2026-10-06
extractor: readability-v1
translator: agent
status: translated
---

# 在 Anyscale 上将大型 AI 模型的自动扩缩容提速至多 5.1 倍

作者：Christopher Chou、Austin Kuo、Richard Liaw、Edward Oakes 和 Chris Sivanich | 2024 年 10 月 1 日

最先进的 AI 模型体积逐月增大，GPU 依然贵得离谱，而 AI 从业者的时间又十分稀缺。把这几个因素放在一起看，结论很清楚：效率是 AI 应用的关键，无论处于开发阶段还是生产阶段。

不幸的是，AI 从业者的常见经历是花大量时间干等：等实例启动、等容器镜像拉取、等模型加载。下文会讲到，在 Kubernetes 上用典型的 Ray Serve 配置为 [Meta-Llama-3-70B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-70B-Instruct) 置备一个推理副本可能需要长达 10-12 分钟。

在 Anyscale，我们对整个技术栈的扩容速度做了优化，使得 **Meta-Llama-3-70B-Instruct 的自动扩缩容（autoscaling）在 Anyscale 平台上最快可比使用 KubeRay 在 Amazon Elastic Kubernetes Service（EKS）上运行同一应用快 5.1 倍**。

更快的扩容速度，是使用 Anyscale 平台的 AI 工程师和研究者的力量倍增器：他们在开发中可以快速迭代、避免空等，在生产中可以按照工作负载需求自动扩缩、避免资源闲置。

## 问题：大容量容器、大模型与昂贵的 GPU

以在 Kubernetes 上用 [vLLM](https://github.com/vllm-project/vllm) 运行流行的开源大语言模型（LLM）[Meta-Llama-3-70B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-70B-Instruct) 为例。典型的启动流程大致如下：

- 创建 Pod，Kubernetes 集群自动扩缩器新增一个带 GPU 的节点：**1-1.5 分钟**
- 从容器镜像仓库拉取容器镜像（约 12 GB，含 CUDA 与 vLLM 依赖）：**4-5 分钟**
- 容器启动，vLLM 从云存储加载模型（FP16 下约 140 GB）：**4-5 分钟**

累计下来，这意味着要等上**最多 10-12 分钟**才能让一份模型副本上线。当然，有多级缓存可以在同一硬件上加速后续启动，但 GPU 价格高企，不用的时候必须及时释放 GPU 机器。

在开发中，这种等待会消耗 AI 从业者的生产力——他们发现自己一直在等实例拉起、等容器拉取、等模型下载。

在生产中，扩容速度慢会导致过度置备。通常，自动扩缩策略是为了应对波动的入站流量模式而配置的：流量增大时扩起更多服务副本，流量减小时再缩下去。但如果响应流量增长而扩容耗时过长，现有副本就可能过载，导致响应延迟升高甚至失败。

对此一个简单而常见的解法是：在稳态下多备一些副本以承接更高负载，同时在新副本上线的等待期内，随流量增加更激进地扩容。但当每个模型副本都需要昂贵的 GPU 才能运行时，这种做法很快就会代价高昂。

理想情况下，在线服务系统能够快速扩容、对入站流量做出更敏捷的响应，同时避免 GPU 资源闲置。

## Anyscale 自动扩缩容：全栈优化

[Anyscale Platform](https://www.anyscale.com/platform) 是一个全托管的 Ray 解决方案。基础设施的每一个部分都经过量身定制，以在使用 Ray 运行 AI 应用时提供最佳用户体验、高性能与成本效益。就扩容速度而言，这体现为几项关键优势：

- Anyscale 控制平面与 Ray autoscaler 直接集成，能够快速响应资源请求并做出智能的自动扩缩决策。
- 机器镜像与启动流程经过调优，以优化实例启动时间。
- 拉取容器镜像时，Anyscale 使用自定义的容器镜像格式和客户端来缩短镜像拉取时间。
- Anyscale 提供了一个快速模型加载库，可将张量从云存储直接流式传输到 GPU。

为展示这些优化的效果，我们运行了一个实验，测量在 AWS 上使用 [vLLM](https://github.com/vllm-project/vllm) 把单个 [Ray Serve](https://www.anyscale.com/library/ray-serve) 副本扩容至可托管 LLM 推理模型所需的时间。我们针对两个代表性模型重复了该实验：

- Mistral-7B-Instruct-v0.1，运行在单张 NVIDIA A10G GPU 上（1x AWS g5.8xlarge 实例）。模型权重在 FP16 下约 14 GB。
- Meta-Llama-70B-Instruct，使用张量并行运行在四张 NVIDIA L40S GPU 上（1x AWS g6e.12xlarge 实例）。模型权重在 FP16 下约 140 GB。

在 Anyscale 上，应用以 [Service](https://docs.anyscale.com/platform/services/) 形式运行；在 KubeRay 上，则以 [RayService](https://docs.ray.io/en/latest/serve/production-guide/kubernetes.html) 形式运行。两种情况下都不涉及本地缓存：都需要启动新实例、从镜像仓库拉取容器、从远端云存储加载模型权重。

Anyscale 能够端到端地在仅 **75 秒内为 Mistral-7B-Instruct-v0.1**、**107 秒内为 Meta-Llama-70B-Instruct** 扩容出一个新副本。相较于在同一工作负载上运行于 Amazon EKS 的 KubeRay，这分别带来了 **4.3 倍**和 **5.1 倍**的提升。

### 自定义容器格式与客户端

实现这一加速的关键差异之一，是 Anyscale 的自定义容器镜像格式与运行时。客户在 Anyscale 平台上首次使用某个新容器镜像时，该镜像会被转换并以优化格式存储，使同一镜像在同一 region 内的后续运行快如闪电。

为单独展示这种优化格式的收益，我们运行了一个实验，测试在一台刚启动的 g5.8xlarge 实例上，于 Amazon EKS 和 Anyscale 平台上拉取容器镜像并启动容器所需的时间。

- 使用的两个镜像：ray:2.34.0 默认镜像（约 6.2 GB），以及以 ray:2.34.0 为基底、安装了 vLLM 及其所需依赖的自定义镜像（约 12.8 GB）。
- 在 Anyscale 和 EKS 上，实例均运行在 us-west-2 region，源容器镜像托管在同一 region、同一 AWS 账号下的 Amazon Elastic Container Registry 中。
- Amazon EKS 节点组配置为使用预置 3,000 IOPs 的 GP3 EBS 卷。

在该实验中，对于 6GB 的镜像，Anyscale 拉取容器镜像的速度比 AWS EKS 最快高 **30 倍**；对于 13GB 的镜像最快高 **14 倍**。

### 优化的直传 GPU 加载

Anyscale 还提供了一个优化客户端，可将 [safetensors](https://github.com/huggingface/safetensors) 格式的模型权重从远端存储直接加载到 GPU。该技术利用流水线并行，避免了先把全部模型权重同步拷贝到磁盘、再加载到 CPU 内存、最后载入 GPU 内存的流程；取而代之的是把模型权重按 chunk 从远端存储流式传输到 CPU 内存再到 GPU 内存。技术细节可阅读这篇[先前的博客文章](https://www.anyscale.com/blog/loading-llama-2-70b-20x-faster-with-anyscale-endpoints)，最新文档见[这里](https://docs.anyscale.com/platform/services/fast-loading)。

为单独展示这种更快模型加载技术的收益，我们测量了 vLLM 启动并加载一个推理模型所需的时间。所用模型与硬件同上文端到端实验一致：

- Mistral-7B-Instruct-v0.1，运行在单张 NVIDIA A10G GPU 上（1x AWS g5.8xlarge 实例）。模型权重在 FP16 下约 14 GB。
- Meta-Llama-70B-Instruct，使用张量并行运行在四张 NVIDIA L40S GPU 上（1x AWS g6e.12xlarge 实例）。模型权重在 FP16 下约 140 GB。

与典型工作流（用 AWS S3 CLI 下载到本地磁盘——配置项已设为最大化吞吐——再用 [safetensors](https://github.com/huggingface/safetensors) 库从本地磁盘加载到 GPU）相比，Anyscale 将 vLLM 的启动与模型加载时间对 **Mistral-7B-Instruct-v0.1 最快提升 2 倍**，对 **Meta-Llama-70B-Instruct 最快提升 4.8 倍**。

## 结论

[Anyscale Platform](https://www.anyscale.com/platform) 实现了全栈优化，带来极速的自动扩缩容。对 Meta-Llama-3-70B-Instruct 而言，与使用 KubeRay 在 Amazon EKS 上运行同一应用相比，这带来了**最快 5.1 倍的自动扩缩提速**。

这些优化让 AI 从业者更高效，也让推理服务的运营成本更低。

今天就免费上手 Anyscale 平台：[https://www.anyscale.com/](https://www.anyscale.com/)。
