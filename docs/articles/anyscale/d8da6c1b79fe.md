---
vendor: anyscale
title: 阿里云上的 Ray：构建机器学习平台
original_title: 
url: https://anyscale.com/blog/ray-on-alibaba-cloud-building-an-ml-platform
date: 2025-06-12
lang: zh
captured: 2026-10-14
extractor: readability-v1
translator: agent
status: translated
body_sha: 01d641a12ee3
---

# 阿里云上的 Ray：构建机器学习平台

作者：Kun Wu（阿里云） | 2025 年 6 月 12 日

人工智能（AI）的推进速度前所未有。不同的用例需要不同的技术与基础设施。举例来说，批量推理需要异构的算力资源——用 CPU 节点做 I/O、用 GPU 节点做推理——才能把性能发挥到最大。此外，RLHF 通常要把 LLM 推理框架和训练框架集成到一起。因此，灵活的机器学习（ML）基础设施，对于在生产环境中可靠地部署 AI 负载至关重要。

Ray 是广受欢迎的 AI 计算引擎，支撑着世界各地公司的 ML 基础设施。[阿里云容器服务 Kubernetes 版](https://www.alibabacloud.com/en/product/kubernetes?_p_lc=1)（ACK）把 Ray 作为一等公民来支持，帮助用户加速从概念验证走向生产的 Ray 之路。许多公司都在阿里云上广泛使用 Ray，比如 [Moonshot AI](https://www.alibabacloud.com/blog/kimi-large-model-based-massive-data-preprocessing-practice-of-moonshot-ai_602119) 就把它用于大规模数据处理以及其他算力密集的 AI 负载。

本文简要介绍 Ray 与 KubeRay，以及在 ACK 上支持 Ray 的相关工作。

#### **Ray**

Ray 是一个开源的分布式计算引擎，能为任意规模的分布式负载、在任意加速硬件上精确地编排基础设施。Ray 的架构分为三层：Ray Core、Ray AI Libraries 和 Ray Deployment。

图 1

#### **Ray Core**

Ray Core 是一个强大的分布式计算引擎，它只提供一小组必备的原语（**task、actor 和 object**），用来构建和扩展分布式应用。Ray 的 task、actor 和 object，与编程中最基础的函数、类和变量一一对应，因此用户用 Ray Core API 编写分布式应用，就像在笔记本上编程一样。下面是 Ray Core API 的一个示例：

```
1import ray
2import numpy as np
3
4# Define a task that sums the values in a matrix.
5@ray.remote
6def sum_matrix(matrix):
7    return np.sum(matrix)
8
9# Call the task with a literal argument value.
10print(ray.get(sum_matrix.remote(np.ones((100, 100)))))
11# -> 10000.0
12
13# Put a large array into the object store.
14matrix_ref = ray.put(np.ones((1000, 1000)))
15
16# Call the task with the object reference as an argument.
17print(ray.get(sum_matrix.remote(matrix_ref)))
18# -> 1000000.0
```

这个示例定义了一个 Ray task **sum_matrix**，用来对一个 NumPy 矩阵里的值求和。第一个调用传入的是字面量数组；第二个调用则先用 **ray.put** 把数组存进 Ray 的对象存储，再把对象引用传给 task。有了 Ray Core，用户写代码时不必关心 Ray 的 task、actor 和 object 分别落在哪些节点上，也不必关心它们之间如何交互。

#### **Ray AI Libraries**

Ray 生态包含 Ray Data、Ray Train、Ray Tune、Ray Serve 和 RLlib 等 AI 库，覆盖从数据处理、训练、调参到服务的整个 ML 生命周期。这些库都构建在 Ray Core 之上，让开发者能够高效地用上 Ray 的分布式执行能力。

#### **Ray Deployment**

Ray 支持以虚拟机和 Kubernetes 作为底层的容器编排层。下一节将讨论官方的 Ray on Kubernetes 方案 KubeRay。

## **KubeRay**

KubeRay 是 Ray 的 Kubernetes operator，用来简化 Kubernetes 上 Ray 集群及其相关应用的生命周期管理。有了 KubeRay，**数据科学家和 ML 科学家**可以专注于自己的机器学习逻辑，**基础设施工程师**则专注于 Kubernetes。

KubeRay 架构示意

也就是说，数据科学家可以专心开发自己的 Python 脚本，不必关心 Kubernetes 是怎么运转的；基础设施工程师则可以专心把 KubeRay 与 Kubernetes 生态的工具集成起来，用于可观测性、流量管理和安全。

KubeRay 针对不同使用方式提供了三个 API，也就是三种自定义资源定义（CRD）：RayCluster、RayJob 和 RayService。

- **RayCluster**：KubeRay 全面管理 RayCluster 的生命周期，包括集群的创建、删除、自动扩缩和容错。
- **RayJob**：KubeRay 会自动创建一个 RayCluster，并在集群就绪后提交作业。你也可以配置 RayJob，让它在作业结束后自动删除这个 RayCluster。
- **RayService**：RayService 由两部分组成：一个 RayCluster，以及一个或多个 Ray Serve 应用。RayService 为 RayCluster 提供零停机升级和高可用。

```
1helm repo add kuberay https://ray-project.github.io/kuberay-helm/
2helm repo update
3
4# Deploy KubeRay operator
5helm install kuberay-operator kuberay/kuberay-operator
6# Deploy a RayCluster
7helm install raycluster kuberay/ray-cluster
```

这个示例演示了在一个已经运行起来的 Kubernetes 集群里，如何只用几条命令、借助 KubeRay 的 RayCluster CRD 轻松拉起一个 Ray 集群。更多细节见「[RayCluster Quickstart](https://docs.ray.io/en/latest/cluster/kubernetes/getting-started/raycluster-quick-start.html)」文档。

## **Ray on ACK**

#### **Overview**

[阿里云容器服务 Kubernetes 版](https://www.alibabacloud.com/en/product/kubernetes?_p_lc=1)（ACK）支持以托管组件的形式启用 KubeRay，具备以下优势，可以帮助用户把 AI 负载以极快的速度从概念验证推向生产。

- **ACK 中的弹性计算**：ACK 支持多种计算类型，以满足不同用例下各异的负载需求。
- **可观测性**：ACK 简化了日志与指标的持久化，并通过 Ray History Server 支持事后分析，让用户能轻松掌握 Ray 集群和应用的状态。
- **安全性**：ACK 团队基于专用的基础镜像构建 KubeRay 镜像，以尽量缩小攻击面。
- **免运维**：ACK 为 KubeRay operator 自动配置了 Vertical Pod Autoscaling（VPA），保证资源得到扩缩，从而减少故障。ACK 还负责组件升级和缺陷修复，让用户专注于应用开发。
- **高可用部署**：ACK 确保 KubeRay operator 分布在至少两个可用区，具备抵御可用区级故障的能力。

## **ACK 中的弹性计算**

ACK 节点池

ACK 集群支持通过节点池来管理节点，从而能在不同场景下使用多种计算类型：用于智能计算的灵骏（Lingjun）节点，按量付费或包年包月的 Elastic Compute Service（ECS）实例，以及按秒计费、便于弹性的 Container Compute Service（ACS）实例。这保证了 ACK 集群能够满足不同用例下各异的负载需求。

## **可观测性**

#### **日志**

**KubeRay 日志**：ACK 集群会自动采集控制面 KubeRay operator 的日志。用户可以通过控制面组件日志查看这些日志，确认 operator 的状态。

KubeRay 日志

**Ray 日志**：借助资源标签，用户可以把数据面 RayCluster 的日志采集到 [Simple Log Service（SLS）](https://www.alibabacloud.com/help/en/sls/)。与自建的日志存储方案相比，SLS 提供结构化的日志查询与分析；因为不再需要维护基础设施，总体拥有成本（TCO）降低 50%；同时具备 99.99% 的 SLA 可用性，可靠性有保障。

Ray 日志

#### **指标**

ACK 集群默认集成了 Prometheus 监控能力。用户只需提交 PodMonitor 和 ServiceMonitor 配置，就能开启对 ACK 集群内数据面 RayCluster 监控数据的采集，随后所有 RayCluster 指标都可以通过统一的 Prometheus 接口查看。

指标

#### **Ray History Server：事后分析**

原生的 Ray Dashboard 只在 Ray 集群运行期间可用。集群一旦终止，用户就再也看不到历史日志和监控数据。为了解决这个限制，ACK 提供了 **Ray History Server**，可以访问处于活跃状态和已终止的 RayCluster 自定义资源的看板。History Server 看板提供的功能与原生 Ray Dashboard 保持一致，同时还把指标监控自动接入了 [Application Real-Time Monitoring Service（ARMS）](https://www.alibabacloud.com/help/en/arms/product-overview/what-is-arms)，无需手动部署 Prometheus 和 Grafana。下面的图示展示了如何访问和使用 History Server 看板。

下图展示的是，用户在 Ray History Server 中可以访问活跃和已终止两种状态的 RayCluster 自定义资源的 Ray Dashboard。

Ray 历史记录

下图展示的是与 Ray Dashboard 一致的页面，也就是在 Ray head Pod 上看到的内容

列表

## **生产实践案例**

本节用一个真实用例来展示 Ray on ACK 的进阶能力。在这个用例中，客户面临三个核心挑战：

- 多个 RayJob 之间的配额限制与优先级排序。
- 为应对突发负载做资源预留（尤其是 RayService 负载）。
- RayJob 终止之后 Ray Dashboard 的留存。

通过集成 [kube-queue](https://github.com/kube-queue/kube-queue) 实现排队与基于优先级的调度，再配合 Ray History Server，这位客户成功地把 Ray 负载在生产环境跑了起来，同时把资源用得很充分。更多细节见下文。

#### **用 ResourcePolicy API 实现智能计算编排**

如前文「**ACK 中的弹性计算**」所述，阿里云提供了多种计算类型，它们在价格、可靠性、可用性、性能和计费模式上各有不同。要把这些各异的算力资源用好，需要成熟的调度方案。

阿里云提供了 ResourcePolicy API，通过定义 Pod 偏好哪类节点的优先级，来实现计算资源类型的编排。以下面这段 YAML 为例，它优先使用包年包月的 ECS 实例，当 ECS 资源不足时切换到按量付费的 ACS 实例。把这一做法与 Kubernetes 的 Pod 自动扩缩组件（如 Ray Autoscaler 和 Horizontal Pod Autoscaler）结合起来，非常适合应对流量洪峰。

```
1apiVersion: scheduling.alibabacloud.com/v1alpha1
2kind: ResourcePolicy
3metadata: 
4  name: resourcepolicy-example
5  namespace: default
6spec:
7  selector:
8    key1: value1
9  units:
10  - resource: ecs
11  - resource: acs
```

该客户同时部署了基于 cron 的数据处理 RayJob 自定义资源，以及长期运行的 RayService ML 推理负载。RayJob 优先消费包年包月的 ECS 实例，资源紧张时退回到用 ACS 实例做补充算力。对于 RayService 负载，客户只使用包年包月的 ECS 实例，并预留额外容量，以支撑 RayCluster 快速扩缩来应对突发流量。更多细节见下图。

智能计算编排

#### **用 kube-queue 支持多租户资源管理**

ACK 通过 kube-queue 支持任务排队与配额。有了配额和队列，用户可以为特定团队或服务定义保障性的资源配额，并设置上限防止超额使用，从而同时保证公平性和可扩展性。

客户创建了一棵配额树，如下图所示，以便在不同团队和不同类型的负载之间高效共享资源。

- 每个团队都有自己的资源配额上下限，既保证最低可用量，也允许最大程度的超卖。
- 每个配额都有自己的队列，创建时定义的优先级更高的 RayJob 会在各自队列中按优先级被执行。

最后一张图
