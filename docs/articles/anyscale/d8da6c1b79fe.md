---
vendor: anyscale
title: 阿里云上的 Ray：构建机器学习平台
original_title: 
url: https://anyscale.com/blog/ray-on-alibaba-cloud-building-an-ml-platform
date: 2025-06-12
lang: zh
captured: 2026-10-09
extractor: readability-v1
translator: mt
status: translated
body_sha: 7a64334f6be4
---

博客详细信息

# 阿里云上的 Ray：构建 ML 平台

由

吴坤（阿里云）

|

2025 年 6 月 12 日

人工智能的发展速度比以往任何时候都快。不同的用例需要不同的技术和基础设施。例如，批量推理需要异构计算资源（用于 I/O 的 CPU 节点和用于推理的 GPU 节点）以最大限度地提高性能。此外，RLHF 通常涉及集成 LLM 推理和训练框架。因此，灵活的机器学习 (ML) 基础设施对于在生产中可靠地部署 AI 工作负载至关重要。

Ray 是一种流行的 AI 计算引擎，为世界各地公司的 ML 基础设施提供支持。 [阿里云 Kubernetes 容器服务](https://www.alibabacloud.com/en/product/kubernetes?_p_lc=1) (ACK) 以一等公民的身份支持 Ray，帮助用户加速 Ray 从概念验证到生产的旅程。 Ray 在阿里云上被 [Moonshot AI](https://www.alibabacloud.com/blog/kimi-large-model-based-massive-data-preprocessing-practice-of-moonshot-ai_602119) 等公司广泛用于大规模数据处理和其他计算密集型 AI 工作负载。

本博客将简要介绍 Ray 和 KubeRay，以及在 ACK 上支持 Ray 的相关工作。

#### 链接**雷**

Ray是一个开源分布式计算引擎。它可以为任何规模的任何加速器上的任何分布式工作负载精确编排基础设施。 Ray 的架构由三层组成：Ray Core、Ray AI Libraries 和 Ray Deployment。

图片1

#### 链接**雷核心**

Ray Core 是一个强大的分布式计算引擎，提供一小组用于构建和扩展分布式应用程序的基本原语（**任务、参与者和对象**）。 Ray 任务、参与者和对象与函数、类和变量（这些是编程的基本组成部分）具有一对一的映射关系，因此用户可以使用 Ray Core API 编写分布式应用程序，就像在笔记本电脑上编程一样。下面是 Ray Core API 的示例：
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
此示例定义了一个 Ray 任务 **sum_matrix**，用于对 NumPy 矩阵中的值求和。在第一个示例中，使用文字数组调用任务。在第二种情况下，首先使用 **ray.put** 将数组存储在 Ray 的对象存储中，然后使用对象引用调用任务。借助 Ray Core，用户可以进行编程，而无需担心哪些节点托管 Ray 任务、参与者和对象，或者它们如何相互交互。

#### 链接**Ray AI 库**

Ray 生态系统包括 Ray Data、Ray Train、Ray Tune、Ray Serve 和 RLlib 等 AI 库，涵盖从数据处理到训练、调优到服务的机器学习生命周期。这些库构建在 Ray Core 之上，使开发人员能够有效利用 Ray 的分布式执行功能。

#### 链接**Ray 部署**

Ray 支持虚拟机和 Kubernetes 作为底层容器编排器。下一节将讨论官方 Ray on Kubernetes 解决方案 KubeRay。

## 链接**KubeRay**

KubeRay 是 Ray Kubernetes 运算符，可简化 Kubernetes 上 Ray 集群和相关应用程序的生命周期管理。 KubeRay 使**数据科学家和机器学习科学家**能够专注于他们的机器学习逻辑，而**基础设施工程师**则专注于 Kubernetes。

库伯雷

也就是说，数据科学家可以专注于开发 Python 脚本，而不必担心 Kubernetes 的工作原理，而基础设施工程师可以专注于将 KubeRay 与 Kubernetes 生态系统工具集成，以实现可观察性、流量管理和安全性。

KubeRay 针对不同的使用模式提供了三个 API，即自定义资源定义 (CRD)：RayCluster、RayJob 和 RayService。

- **RayCluster**：KubeRay 完全管理 RayCluster 的生命周期，包括集群创建、删除、自动缩放和容错。
- **RayJob：**KubeRay 自动创建 RayCluster，并在集群准备就绪时提交作业。您还可以将 RayJob 配置为在作业完成后自动删除 RayCluster。
- **RayService：**RayService 由两部分组成：RayCluster 和一个或多个 Ray Serve 应用程序。 RayService 为 RayCluster 和高可用性提供零停机升级。
```
1helm repo add kuberay https://ray-project.github.io/kuberay-helm/
2helm repo update
3
4# Deploy KubeRay operator
5helm install kuberay-operator kuberay/kuberay-operator
6# Deploy a RayCluster
7helm install raycluster kuberay/ray-cluster
```
该示例演示了如何在运行的 Kubernetes 集群中使用 KubeRay 的 RayCluster CRD 轻松启动 Ray 集群，只需几个命令。有关更多详细信息，请参阅“[RayCluster 快速入门](https://docs.ray.io/en/latest/cluster/kubernetes/getting-started/raycluster-quick-start.html)”文档。

## 链接**Ray on ACK**

#### 链接**概述**

[阿里云 Kubernetes 容器服务](https://www.alibabacloud.com/en/product/kubernetes?_p_lc=1) (ACK) 支持 KubeRay 作为托管组件，具有以下优势，可帮助用户将 AI 工作负载从概念验证快速转移到生产。

- **ACK 中的弹性计算：** ACK 支持多种计算类型，以满足跨用例的不同工作负载要求。
- **可观察性：**ACK 简化了持久日志和指标，并支持使用 Ray History Server 进行事后分析，以便用户可以轻松了解 Ray 集群和应用程序的状态。
- **安全性：** ACK 团队基于专门的基础映像构建 KubeRay 映像，以最大程度地减少攻击面。
- **零运维：**ACK为KubeRay算子配置自动Vertical Pod Autoscaling（VPA），确保资源扩展以减少故障。 ACK还处理组件升级和错误修复，使用户能够专注于应用程序开发。
- **高可用性部署：** ACK 确保 KubeRay 操作员分布在至少两个可用区域中，从而提供针对区域级故障的恢复能力。

##链接**ACK中的弹性计算**

确认

ACK集群支持通过节点池进行节点管理，支持在不同场景下使用多种计算类型：智能计算的灵君节点、按量付费或订阅的弹性计算服务（ECS）实例、按秒计费的容器计算服务（ACS）实例以实现可扩展性。这可确保 ACK 集群满足跨用例的不同工作负载要求。

## 链接**可观察性**

#### 链接**日志记录**

**KubeRay 日志：**ACK 集群自动从控制平面的 KubeRay 操作员收集日志。用户可以通过控制平面组件日志检查这些日志，以验证操作员的状态。

KubeRay 日志

**Ray日志：**通过资源标签，用户可以将数据平面RayCluster中的日志收集到[简单日志服务（SLS）](https://www.alibabacloud.com/help/en/sls/)。与自管理日志存储解决方案相比，SLS提供结构化日志查询和分析，无需基础设施维护，总体拥有成本（TCO）降低50%，SLA可用性高达99.99%，保证高可靠性。

射线日志

#### 链接**指标**

默认情况下，ACK 集群与 Prometheus 监控功能集成。用户只需提交PodMonitor和ServiceMonitor配置即可实现ACK集群内数据面RayCluster监控数据的采集。然后可以通过统一的 Prometheus 界面查看所有 RayCluster 指标。

指标

#### 链接**射线历史服务器：事后分析**

本机 Ray 仪表板仅在 Ray 集群运行时可用。一旦集群终止，用户将无法访问历史日志和监控数据。为了解决此限制，ACK 提供了 **Ray History Server**，它允许访问活动和终止的 RayCluster 自定义资源的仪表板。 History Server 仪表板提供与本机 Ray 仪表板一致的功能。它还提供与[应用程序实时监控服务（ARMS）]（https://www.alibabacloud.com/help/en/arms/product-overview/what-is-arms）自动集成的指标监控，无需手动部署Prometheus和Grafana。下图显示了如何访问和使用 History Server 仪表板。

下图显示用户可以访问 Ray 历史记录服务器中活动和终止的 RayCluster 自定义资源的 Ray 仪表板。

雷历史

下图显示了 Ray 仪表板的镜像页面，如 Ray head Pod 上所示

列表

## 链接**生产案例研究**

本节使用实际用例来演示 Ray on ACK 的高级功能。在此用例中，客户面临三个核心挑战：

- 多个 RayJobs 的配额限制和优先级。
- 资源预留以处理突发工作负载（特别是 RayService 工作负载）。
- RayJob 终止后 Ray 仪表板持久性。

通过利用 [kube-queue](https://github.com/kube-queue/kube-queue) 集成进行排队和基于优先级的调度，以及 Ray 历史服务器，客户成功地在生产中操作了 Ray 工作负载，同时有效地利用了资源。有关更多详细信息，请参阅以下部分。

#### 链接**使用 ResourcePolicy API 进行智能计算编排**

正如前面**“ACK 中的弹性计算”**中提到的，阿里云提供了多种计算类型，这些类型在定价、可靠性、可用性、性能和计费模型方面有所不同。有效利用这些不同的计算资源需要复杂的调度方法。

阿里云提供了ResourcePolicy API，通过定义Pod喜欢的节点类型的优先级来实现计算资源类型的编排。以下面的YAML为例，优先使用订阅型ECS实例，当ECS资源不足时，切换到按量付费的ACS实例。当与 Kubernetes Pod 自动缩放器（例如 Ray Autoscaler 和 Horizo​​ntal Pod Autoscaler）结合使用时，此方法非常适合处理流量峰值。
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
客户部署基于 cron 的数据处理 RayJob 自定义资源和长期运行的 RayService ML 推理工作负载。 RayJobs 优先使用基于订阅的 ECS 实例，在短缺期间回退到使用 ACS 实例作为补充计算。对于 RayService 工作负载，客户专门使用订阅 ECS 实例，保留额外容量来支持快速 RayCluster 自动缩放，以处理突发流量。更多详情请参见下图。

智能计算

####链接**使用kube-queue支持多租户资源管理**

ACK 通过 kube-queue 支持任务排队和配额。通过配额和队列，用户可以为特定团队或服务定义有保证的资源配额，并设置上限以防止过度使用，确保公平性和可扩展性。

客户创建了一个配额树，如下图所示，以在不同团队和不同类型的工作负载之间高效共享资源。

- 每个团队都有自己的最小和最大资源配额，以确保最小可用性和最大过度使用资源。
- 每个配额都有自己的队列，并且在创建期间定义的更高优先级的 RayJobs 将根据每个队列内的优先级执行。

最后一张图片

#### 目录

- [KubeRay](https://www.anyscale.com/blog/ray-on-alibaba-cloud-building-an-ml-platform#kuberay)
- [Ray 上的 ACK](https://www.anyscale.com/blog/ray-on-alibaba-cloud-building-an-ml-platform#ray-on-ack)
- [ACK中的弹性计算](https://www.anyscale.com/blog/ray-on-alibaba-cloud-building-an-ml-platform#elastic-compute-in-ack)
- [可观测性](https://www.anyscale.com/blog/ray-on-alibaba-cloud-building-an-ml-platform#observability)
- [生产案例研究](https://www.anyscale.com/blog/ray-on-alibaba-cloud-building-an-ml-platform#product-case-study)

####分享

####标签

法学硕士

#### 注册产品更新

####推荐内容

#### 将编码代理成本降低 90%：在 Anyscale 上使用 Ray + vLLM 提供安全的 LLM 服务


#### Azure 上的 Anyscale 全面可用：使企业能够拥有完整的 AI 循环，而不仅仅是推理


#### Ray Summit 2026：物理 AI、RL 以及运行它们的基础设施


## 立即探索 Anyscale

使用专为生产 AI 构建的多云平台，在 Ray 上构建、运行和扩展任何 AI 工作负载。

免费开始

与专家交谈
