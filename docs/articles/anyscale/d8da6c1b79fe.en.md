---
vendor: anyscale
title: Ray on Alibaba Cloud: Building an ML Platform
original_title: Ray on Alibaba Cloud: Building an ML Platform
url: https://anyscale.com/blog/ray-on-alibaba-cloud-building-an-ml-platform
date: 2025-06-12
lang: en
captured: 2026-10-09
extractor: readability-v1
status: ok
body_sha: 1c531f25f790
---



Blog Detail

# Ray on Alibaba Cloud: Building an ML Platform

By

Kun Wu (Alibaba Cloud)

|

June 12, 2025

Artificial intelligence is advancing faster than ever. Different use cases demand different techniques and infrastructure. For example, batch inference requires heterogeneous computing resources—CPU nodes for I/O and GPU nodes for inference—to maximize performance. Additionally, RLHF typically involves integrating both LLM inference and training frameworks. Therefore, flexible machine learning (ML) infrastructure is essential for reliably deploying AI workloads in production.

Ray is a popular AI compute engine that powers the ML infrastructure of companies around the world. [Alibaba Cloud Container Service for Kubernetes](https://www.alibabacloud.com/en/product/kubernetes?_p_lc=1) (ACK) supports Ray as a first-class citizen, helping users accelerate their Ray journey from proof of concept to production. Ray is widely used on Alibaba Cloud by companies like [Moonshot AI](https://www.alibabacloud.com/blog/kimi-large-model-based-massive-data-preprocessing-practice-of-moonshot-ai_602119) for large-scale data processing and other compute-intensive AI workloads.

This blog will briefly introduce Ray and KubeRay, along with the related efforts to support Ray on ACK.

#### Link**Ray**

Ray is an open-source distributed computing engine. It precisely orchestrates infrastructure for any distributed workload on any accelerator at any scale. Ray's architecture consists of three layers: Ray Core, Ray AI Libraries, and Ray Deployment.

Image1

#### Link**Ray Core**

Ray Core is a powerful distributed compute engine that provides a small set of essential primitives (**task, actor, and object**) for building and scaling distributed applications. Ray tasks, actors, and objects have a one-to-one mapping with functions, classes, and variables, which are fundamental components in programming, so users can program distributed applications with the Ray Core API just like programming on a laptop. Below is an example of Ray Core API:

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

This example defines a Ray task **sum_matrix** that sums the values in a NumPy matrix. In the first example, the task is called with a literal array. In the second, the array is first stored in Ray’s object store using **ray.put**, and the task is called with the object reference. With Ray Core, users can program without worrying about which nodes host Ray tasks, actors, and objects, or how they interact with each other.

#### Link**Ray AI Libraries**

The Ray ecosystem includes AI libraries such as Ray Data, Ray Train, Ray Tune, Ray Serve, and RLlib that cover the ML lifecycle, from data processing to training to tuning to serving. These libraries are built on top of Ray Core, enabling developers to efficiently leverage the distributed execution capabilities of Ray.

#### Link**Ray Deployment**

Ray supports virtual machines and Kubernetes as the underlying container orchestrator. The next section will discuss the official Ray on Kubernetes solution, KubeRay.

## Link**KubeRay**

KubeRay is a Ray Kubernetes operator that simplifies the management of the lifecycle of Ray clusters and associated applications on Kubernetes. KubeRay enables **data scientists and ML scientists** to focus on their machine learning logic while **infra engineers** concentrate on Kubernetes.

Kuberay

That is, data scientists can focus on developing their Python scripts without worrying about how Kubernetes works, and infrastructure engineers can focus on integrating KubeRay with Kubernetes ecosystem tools for observability, traffic management, and security.

KubeRay provides three APIs, which are custom resource definitions (CRDs), for different usage patterns: RayCluster, RayJob, and RayService.

- **RayCluster**: KubeRay fully manages the lifecycle of a RayCluster, including cluster creation, deletion, autoscaling, and fault tolerance.
- **RayJob: **KubeRay automatically creates a RayCluster and submits a job when the cluster is ready. You can also configure RayJob to automatically delete the RayCluster once the job finishes.
- **RayService: **RayService is made up of two parts: a RayCluster and one or more Ray Serve applications. RayService offers zero-downtime upgrades for RayCluster and high availability.

```
1helm repo add kuberay https://ray-project.github.io/kuberay-helm/
2helm repo update
3
4# Deploy KubeRay operator
5helm install kuberay-operator kuberay/kuberay-operator
6# Deploy a RayCluster
7helm install raycluster kuberay/ray-cluster
```

The example demonstrates how to launch a Ray cluster easily using KubeRay’s RayCluster CRD with just a few commands in a running Kubernetes cluster. See the “[RayCluster Quickstart](https://docs.ray.io/en/latest/cluster/kubernetes/getting-started/raycluster-quick-start.html)” documentation for more details.

## Link**Ray on ACK**

#### Link**Overview**

[Alibaba Cloud Container Service for Kubernetes](https://www.alibabacloud.com/en/product/kubernetes?_p_lc=1) (ACK) supports KubeRay as a managed component, offering the following advantages to help users move their AI workloads from proof of concept to production at lightspeed.

- **Elastic Compute in ACK:** ACK supports diverse compute types to meet varied workload requirements across use cases.
- **Observability: **ACK streamlines persisting logs and metrics, and enables post-mortem analysis with Ray History Server so users can easily understand the status of Ray clusters and applications.
- **Security:** ACK team builds KubeRay images based on specialized base images to minimize the attack surface.
- **Zero Operations and Maintenance: **ACK configures automatic Vertical Pod Autoscaling (VPA) for the KubeRay operator, ensuring resource scaling to reduce failures. ACK also handles component upgrades and bug fixes, allowing users to focus on application development.
- **High Availability Deployment:** ACK ensures that the KubeRay operator is distributed across at least two availability zones, providing resilience against zone-level failures.

## Link**Elastic Compute in ACK**

ACK

ACK clusters support node management via node pools, enabling the use of diverse compute types in different scenarios: Lingjun nodes for intelligent computing, Elastic Compute Service (ECS) instances with pay-as-you-go or subscription, and Container Compute Service (ACS) instances with per-second billing for scalability. This ensures that ACK clusters meet varied workload requirements across use cases.

## Link**Observability**

#### Link**Logging**

**KubeRay logs: **ACK clusters automatically collect logs from the control plane’s KubeRay operator. Users can inspect these logs via the control plane component logs to verify the operator’s status.

KubeRay Logs

**Ray logs: **With resource labels, users are able to gather logs from data-plane RayClusters into [Simple Log Service (SLS)](https://www.alibabacloud.com/help/en/sls/). Compared with self-managed log storage solutions, SLS offers structured log query and analysis, a 50% lower Total Cost of Ownership (TCO) by eliminating infrastructure maintenance, and an SLA availability of 99.99%, which ensures high reliability.

Ray Logs

#### Link**Metrics**

By default, ACK clusters integrate with Prometheus monitoring capabilities. Users only need to submit PodMonitor and ServiceMonitor configurations to enable the collection of monitoring data for data-plane RayClusters within ACK clusters. All RayCluster metrics can then be viewed through a unified Prometheus interface.

Metrics

#### Link**Ray History Server: Post-Mortem Analysis**

The native Ray Dashboard is available only while Ray clusters are running. Once a cluster is terminated, users lose access to historical logs and monitoring data. To address this limitation, ACK provides the **Ray History Server**, which enables access to dashboards for both active and terminated RayCluster custom resources. The History Server dashboard offers features consistent with those of the native Ray Dashboard. It also provides metric monitoring that is automatically integrated with [Application Real-Time Monitoring Service (ARMS)](https://www.alibabacloud.com/help/en/arms/product-overview/what-is-arms), eliminating the need to manually deploy Prometheus and Grafana. The following figures show how to access and use the History Server dashboard.

In the following figure, it is shown that users can access Ray Dashboards for both active and terminated RayCluster custom resources in the Ray History Server.

ray History

The image below displays pages mirroring the Ray dashboard, as shown on the Ray head Pods

list

## Link**Production Case Study**

This section uses an actual use case to demonstrate the advanced capabilities of Ray on ACK. In this use case, the customer faced three core challenges:

- Quota limits and prioritization across multiple RayJobs.
- Resource reservations to handle bursty workloads (particularly for RayService workloads).
- Ray dashboard persistence after the termination of a RayJob.

By leveraging [kube-queue](https://github.com/kube-queue/kube-queue) integration for queuing and priority-based scheduling, along with the Ray History Server, the customer successfully operationalized Ray workloads in production while utilizing resources efficiently. See the following sections for more details.

#### Link**Smart Compute Orchestration with ResourcePolicy API**

As mentioned previously under **“Elastic Compute in ACK,”** Alibaba Cloud provides diverse compute types that differ in pricing, reliability, availability, performance, and billing models. Effectively leveraging these varied compute resources requires sophisticated scheduling approaches.

Alibaba Cloud provides a ResourcePolicy API to enable the orchestration of compute resource types by defining the priorities of which types of nodes the Pod prefers. Taking the following YAML as an example, it prioritizes subscription-based ECS instances and switches to pay-as-you-go ACS instances when ECS resources are insufficient. This approach is ideal for handling traffic spikes when combined with Kubernetes Pod autoscalers, such as the Ray Autoscaler and the Horizontal Pod Autoscaler.

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

The customer deploys both cron-based data processing RayJob custom resources and long-running RayService ML inference workloads. RayJobs preferentially consume subscription-based ECS instances, falling back to using ACS instances as supplemental compute during shortages. For RayService workloads, the customer exclusively uses subscription ECS instances, reserving extra capacity to support rapid RayCluster autoscaling to handle bursty traffic. See the following figure for more details.

Smart Compute

#### Link**Support Multi-Tenant Resource Management with kube-queue**

ACK supports task queuing and quotas through kube-queue. With quotas and queues, users can define guaranteed resource quotas for specific teams or services and set upper limits to prevent overuse, ensuring both fairness and scalability.

The customer created a quota tree, as shown in the following figure, to efficiently share resources across different teams and types of workloads.

- Each team has its own minimum and maximum resource quotas to ensure minimum availability and maximum overcommitted resources.
- Each quota has its own queue, and higher priority RayJobs, as defined during creation, will be executed based on priority within each queue.

last image

#### Table of contents

- [KubeRay](https://www.anyscale.com/blog/ray-on-alibaba-cloud-building-an-ml-platform#kuberay)
- [Ray on ACK](https://www.anyscale.com/blog/ray-on-alibaba-cloud-building-an-ml-platform#ray-on-ack)
- [Elastic Compute in ACK](https://www.anyscale.com/blog/ray-on-alibaba-cloud-building-an-ml-platform#elastic-compute-in-ack)
- [Observability](https://www.anyscale.com/blog/ray-on-alibaba-cloud-building-an-ml-platform#observability)
- [Production Case Study](https://www.anyscale.com/blog/ray-on-alibaba-cloud-building-an-ml-platform#production-case-study)

#### Sharing

#### Tags

LLM

#### Sign up for product updates

#### Recommended content

#### Cut coding agent costs by 90%: Secure LLM serving with Ray + vLLM on Anyscale


#### Anyscale on Azure is Generally Available: Enabling Enterprises to Own the Full AI Loop, Not Just Inference


#### Ray Summit 2026: Physical AI, RL, and the infrastructure that runs them all


## Explore Anyscale today

Build, run, and scale any AI workload on Ray with a multi-cloud platform built for production AI.

Start for Free

Talk to an expert
