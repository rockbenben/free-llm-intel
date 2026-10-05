---
vendor: huggingface
title: 案例研究：用 Hugging Face Infinity 与现代 CPU 实现毫秒级延迟
original_title: 'Case Study: Millisecond Latency using Hugging Face Infinity and modern CPUs'
url: https://huggingface.co/blog/infinity-cpu-performance
date: 2024-08-14
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# 案例研究：用 Hugging Face Infinity 与现代 CPU 实现毫秒级延迟

2022 年 12 月更新：Hugging Face 已不再将 Infinity 作为商业推理方案提供。若要部署并加速你的模型，我们推荐以下新方案：

- [Inference Endpoints](https://huggingface.co/docs/inference-endpoints/index)，在由 Hugging Face 管理的专用基础设施上轻松部署模型。
- 我们的开源优化库 [🤗 Optimum Intel](https://huggingface.co/blog/openvino) 和 [🤗 Optimum ONNX Runtime](https://huggingface.co/docs/optimum/main/en/onnxruntime/overview)，在训练和推理运行模型时获得最高效率。
- Hugging Face [专家加速计划](https://huggingface.co/support)——一项商业服务，让 Hugging Face 专家与你的团队直接协作，加速你的机器学习路线图和模型。

## 引言

迁移学习改变了机器学习——从自然语言处理（NLP）到音频和计算机视觉任务，准确率达到了新的高度。在 Hugging Face，我们努力让这些复杂的新模型和大型 checkpoint 尽可能易于获取和使用。但尽管研究者和数据科学家已经转入 Transformer 新世界，很少有公司能够把这些庞大的复杂模型规模化地部署到生产环境。

主要瓶颈是预测延迟——它让大规模部署运行昂贵、让实时用例无法落地。解决这一难题对任何机器学习工程团队都是艰苦的工程挑战，需要使用先进技术把模型一路优化到硬件层。

通过 [Hugging Face Infinity](https://huggingface.co/infinity)，我们提供一个容器化方案，让最受欢迎的 Transformer 模型可以轻松地部署为低延迟、高吞吐、硬件加速的推理管道。企业既能获得 Transformer 的精度，也能获得大批量部署所需的效率，而一切都在一个易用的包里。在这篇博客中，我们想分享 Infinity 运行在最新一代 Intel Xeon CPU 上的详细性能结果，帮你的 Transformer 部署达到成本、效率与延迟的最优。

## 什么是 Hugging Face Infinity

Hugging Face Infinity 是一个面向客户的容器化方案，可在任意基础设施上为最先进 Transformer 模型部署端到端优化的推理管道。

Hugging Face Infinity 由 2 个主要服务组成：

- Infinity Container 是一个硬件优化的推理方案，以 Docker 容器交付。
- Infinity Multiverse 是一个模型优化服务，把 Hugging Face Transformer 模型针对目标硬件进行优化。Infinity Multiverse 与 Infinity Container 兼容。

Infinity Container 专为在目标硬件架构上运行而构建，并暴露一个 HTTP /predict 端点用于推理。

Figure 1. Infinity Overview

一个 Infinity Container 被设计为服务 1 个模型和 1 个任务。任务对应 [Transformers Pipelines 文档](https://huggingface.co/docs/transformers/master/en/main_classes/pipelines)中定义的机器学习任务。撰写本文时，支持的任务包括特征提取/文档嵌入、排序、序列分类和 token 分类。

关于 Hugging Face Infinity 的更多信息见 [hf.co/infinity](https://huggingface.co/infinity)；如果你有兴趣亲自测试，可以在 [hf.co/infinity-trial](https://huggingface.co/infinity-trial) 注册免费试用。

## 基准测试

推理性能基准常常只测量模型执行本身。在这篇博客中，以及在讨论 Infinity 性能时，我们始终测量端到端管道，包括预处理、预测和后处理。在与其他延迟测量比较时请记住这一点。

Figure 2. Infinity End-to-End Pipeline

### 环境

基准环境使用 [Amazon EC2 C6i 实例](https://aws.amazon.com/ec2/instance-types/c6i)——由第三代 Intel Xeon Scalable 处理器驱动的算力优化实例。这些新的 Intel 实例采用 ice-lake 制程技术，支持 Intel AVX-512、Intel Turbo Boost 和 Intel Deep Learning Boost。

除了对机器学习负载的卓越性能，Intel Ice Lake C6i 实例还提供了出色的性价比，是我们在 Amazon Web Services 上部署 Infinity 的推荐选择。更多内容请访问 [EC2 C6i instance](https://aws.amazon.com/ec2/instance-types/c6i) 页面。

### 方法论

对 BERT 类模型做基准时，最常被采用的指标有两个：

- **延迟（Latency）**：模型单次预测（预处理、预测、后处理）所花时间
- **吞吐（Throughput）**：在固定时间内、遵循物理 CPU 核心数、序列长度和 Batch Size 的某一基准配置下完成的执行次数

本博客将用这两个指标在多种配置下对 Hugging Face Infinity 做基准，以理解各项收益与取舍。

## 结果

为运行基准，我们为 [EC2 C6i 实例](https://aws.amazon.com/ec2/instance-types/c6i)（Ice-lake）构建了 infinity 容器，并使用 Infinity Multiverse 对用于序列分类的 [DistilBERT](https://huggingface.co/docs/transformers/model_doc/distilbert) 模型做了优化。

这个针对 ice-lake 优化的 Infinity Container，相比现有的 cascade-lake 实例可实现最高 34% 的延迟与吞吐改善，相比运行在 ice-lake 上的原版 transformers 可实现最高 800% 的延迟与吞吐改善。

我们创建的基准由 192 个不同实验与配置组成。实验覆盖了：

- 物理 CPU 核心数：1、2、4、8
- 序列长度：8、16、32、64、128、256、384、512
- Batch_size：1、2、4、8、16、32

每个实验中，我们收集以下数据：

- 吞吐（每秒请求数）
- 延迟（min、max、avg、p90、p95、p99）

基准的完整数据见这个 google spreadsheet：[🤗 Infinity: CPU Ice-Lake Benchmark](https://docs.google.com/spreadsheets/d/1GWFb7L967vZtAS1yHhyTOZK1y-ZhdWUFqovv7-73Plg/edit?usp=sharing)。

本文挑选展示部分基准结果，包括最佳延迟和最佳吞吐配置。

此外，我们把基准所用的 [DistilBERT](https://huggingface.co/bhadresh-savani/distilbert-base-uncased-emotion) 模型以 API endpoint 形式部署在 2 个物理核心上。你可以亲自测试，感受 Infinity 的性能。下面是向该托管端点发送请求的 `curl` 命令。API 会返回一个 `x-compute-time` HTTP 头，包含端到端管道的耗时。

```
curl --request POST `-i` \
  --url https://infinity.huggingface.co/cpu/distilbert-base-uncased-emotion \
  --header 'Content-Type: application/json' \
  --data '{"inputs":"I like you. I love you"}'
```

### 吞吐

下面是 infinity 以 batch size 1 运行在 2 个物理核心上的吞吐对比，对照组为原版 transformers。

Figure 3. Throughput: Infinity vs Transformers

| Sequence Length | Infinity | Transformers | improvement |
| --- | --- | --- | --- |
| 8 | 248 req/sec | 49 req/sec | +506% |
| 16 | 212 req/sec | 50 req/sec | +424% |
| 32 | 150 req/sec | 40 req/sec | +375% |
| 64 | 97 req/sec | 28 req/sec | +346% |
| 128 | 55 req/sec | 18 req/sec | +305% |
| 256 | 27 req/sec | 9 req/sec | +300% |
| 384 | 17 req/sec | 5 req/sec | +340% |
| 512 | 12 req/sec | 4 req/sec | +300% |

### 延迟

下面是 Hugging Face Infinity 在 2 个物理核心、Batch Size 1 下某次实验的延迟结果。值得注意的是 Infinity 的稳健与恒定——p95、p99 或 p100（最大延迟）的偏离极小。基准中的其他实验也印证了这一结果。

Figure 4. Latency (Batch=1, Physical Cores=2)

## 结论

在本文中，我们展示了 Hugging Face Infinity 在新型 Intel Ice Lake Xeon CPU 上的表现。我们创建了包含 190 多种配置的详尽基准，分享了你在使用 CPU 版 Infinity 时可预期的结果：为优化延迟该选什么配置、为最大化吞吐该选什么配置。

相比原版 transformers，Hugging Face Infinity 可提供最高 800% 的吞吐提升，并在序列长度不超过 64 token 时把延迟降到 1-4ms。

针对吞吐、延迟或两者兼得地优化 transformer 模型的灵活性，让企业既能在同等负载下削减基础设施成本，也能解锁此前无法实现的实时用例。

如果你想试用 Hugging Face Infinity，请到 [hf.co/infinity-trial](https://hf.co/infinity-trial) 注册试用。

## 资源

- [Hugging Face Infinity](https://huggingface.co/infinity)
- [Hugging Face Infinity Trial](https://huggingface.co/infinity-trial)
- [Amazon EC2 C6i instances](https://aws.amazon.com/ec2/instance-types/c6i)
- [DistilBERT](https://huggingface.co/docs/transformers/model_doc/distilbert)
- [DistilBERT paper](https://arxiv.org/abs/1910.01108)
- [DistilBERT model](https://huggingface.co/bhadresh-savani/distilbert-base-uncased-emotion)
- [🤗 Infinity: CPU Ice-Lake Benchmark](https://docs.google.com/spreadsheets/d/1GWFb7L967vZtAS1yHhyTOZK1y-ZhdWUFqovv7-73Plg/edit?usp=sharing)
