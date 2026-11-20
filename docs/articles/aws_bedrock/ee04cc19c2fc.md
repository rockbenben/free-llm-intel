---
vendor: aws_bedrock
title: 在 Amazon SageMaker HyperPod 上引入工作负载恢复和扩展基础设施检查
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/introducing-workload-recovery-and-expanded-infrastructure-checks-on-amazon-sagemaker-hyperpod
date: 2026-11-18
lang: zh
captured: 2026-11-20
extractor: readability-v1
translator: mt
status: translated
body_sha: 2333a838ac27
---

## [人工智能](https://aws.amazon.com/blogs/machine-learning/)

# 在 Amazon SageMaker HyperPod 上引入工作负载恢复和扩展基础设施检查

即使每个节点看起来都很健康，大型训练作业也可能会失败。存在细微故障的 GPU 可以通过压力测试，但仍然返回错误的值。当作业因 NCCL 超时而停止时，它会保留其 GPU，并且 Slurm 仍将其显示为正在运行。如果设备插件在一个节点上崩溃，则作业将失败并出现从未提及该插件的错误。团队通常只有在损失出现分歧或作业失败后才发现这些问题，那时计算量就已经用完。这些故障中的每一个都会降低有效吞吐量，即集群用于有用训练的时间份额。今天，我们在 Amazon SageMaker HyperPod 上引入工作负载恢复和基础设施检查，可以更快地发现这些故障并提高训练工作负载的吞吐量。

SageMaker HyperPod 已经可以处理报告硬件故障的节点。运行状况监控代理 (HMA) 监视每个节点是否存在 GPU 错误、在配置期间深度运行状况检查测试节点以及自动节点恢复重新启动或更换有故障的硬件。这些功能一次查看一个节点的硬件。他们无法判断 GPU 训练是否正确、作业是否仍在取得进展，或者作业所依赖的 Kubernetes 组件是否正在运行。

在这篇文章中，我们将介绍捕获这些故障的三种新功能。对于每一个，我们都会展示如何设置它以及它发现问题时报告的内容：

- `MultiNodeTrainingValidation` 是由 Amazon Elastic Kubernetes Service (Amazon EKS) 协调的 HyperPod 集群的新深度运行状况检查。当 HyperPod 配置实例时，或者当您按需运行检查时，它会在实例上训练一个小型模型，然后在相同类型的实例上训练。如果损失变为 NaN 或无穷大，或者训练未及时完成，则实例失败。
- HyperPod Kubernetes 资源监控代理监视 EKS 集群的 Kubernetes 层是否存在崩溃循环设备插件、缺少 DaemonSet 和受污染节点等问题。当作业失败时，它会以 Kubernetes 事件和 Amazon CloudWatch 日志的形式报告涉及的 Pod 和节点。
- 挂起作业检测可发现已停止进展的 Slurm 作业。每个节点上的代理会监视作业的输出和 GPU 活动，或您定义的日志模式。它将一个事件写入 CloudWatch 并可以取消作业，以便 Slurm 重新对其进行排队。

## 为什么仅节点健康状况还不够

现有的 HyperPod 弹性功能一次检查一个节点。运行状况监控代理 (HMA) 监视每个节点是否存在 GPU 错误，例如 Xid 和 NVLink 故障、Elastic Fabric Adapter (EFA) 错误和内核错误。 InstanceStress 深度运行状况检查运行 DCGM 4 级诊断并测试每个实例的 GPU、GPU 内存、NVLink 和 EFA 设备。 InstanceConnectivity 检查跨 GPU 实例运行 NCCL 测试，或在 AWS Trainium 上运行 NCCOM 测试。这些共同确认每个节点的硬件正常工作。它们不会显示 GPU 计算是否正确、作业是否仍在取得进展，或者集群的 Kubernetes 组件是否运行正常。他们会遇到三种失败：

- **数值错误 –** GPU 可以通过所有硬件测试，但仍然计算出错误的结果。第一个迹象通常是 NaN 或生产运行中的无限损失。 Meta 将其 54 天的 Llama 3 405B 预训练运行中的 419 次意外中断中的 6 次归因于静默数据损坏（[The Llama 3 Herd of Models](https://arxiv.org/abs/2407.21783)）。
- **挂起的作业 –** NCCL 超时、停滞的数据管道或死锁可以停止作业而不结束它。该作业会保留其 GPU 及其内存，Slurm 会将其报告为正在运行，直到有人检查损失曲线或日志。
- **集群级故障 –** 有些故障发生在 Kubernetes 中，而不是节点的硬件中。设备插件崩溃循环、所需的 DaemonSet 永远不会在新节点上启动，或者不同节点上的排名在 NCCL 集合中不同步。 HMA 会自行检查每个节点，因此不会发现这些问题。当作业失败时，错误通常不会说明是哪个 pod 或节点导致的。

## 解决方案概述

每种能力涵盖训练运行中的不同点。 `MultiNodeTrainingValidation` 在配置实例或按需运行时运行，并确认其 GPU 训练正确。挂起作业检测与每个 Slurm 作业一起运行，并捕获已停止进展的作业。 HyperPod Kubernetes 资源监控代理持续监视集群，当作业失败时，报告涉及的 Pod 和节点。下表总结了这三者。

| **能力** | **它捕获了什么** | **当它运行时** | **可用** |
| --- | --- | --- | --- |
| `MultiNodeTrainingValidation`深度健康检查|在通过硬件检查的 GPU 上出现 NaN 或无限损失，或者训练未及时完成 |何时创建或更新实例，或按需 | EKS 集群，位于支持的启用 EFA 的 NVIDIA GPU 实例上 |
| HyperPod Kubernetes 资源监控代理 |节点条件变化、Pod 和 DaemonSet 故障以及训练作业失败（涉及 Pod 和节点）。选择加入的职位的 NCCL 沟通状态 |持续 | EKS 集群 |
|挂起作业检测|停止进步但不退出的工作 |当每个作业运行时 |泥浆团|

挂起作业检测对于 Slurm 集群来说是一项新功能。在 EKS 集群上，HyperPod 已检测到通过 [HyperPod 训练运算符](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-eks-operator-usage.html) 运行的挂起作业，并且 Ray Train 作业获得 [默认情况下挂起检测](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-ray-hung-job-detection.html)。我们在挂起作业检测部分描述了这两个选项。

每种功能都针对不同的吞吐量损失来源。调度有效吞吐量是指作业所需的所有资源可用的时间份额。运行时有效吞吐量是作业取得进展的时间份额。程序有效吞吐量是作业获得的硬件峰值性能的份额。下表显示了每个功能的效果。

| **能力** | **调度有效吞吐量** | **运行时有效吞吐量** | **程序吞吐量** |
| --- | --- | --- | --- |
| `MultiNodeTrainingValidation` |未通过训练测试的实例将被标记，并通过自动节点恢复进行替换，因此作业不会在产生无效输出的硬件上启动 |减少因 NaN 导致的生产运行损失或因 GPU 故障而造成的无限损失 |标记训练未在时限内完成的实例 |
| HyperPod Kubernetes 资源监控代理 |报告丢失 GPU 或 EFA 设备、缺少设备插件和污点的节点，以便您可以更快地恢复容量 |命名失败作业背后的 Pod 和节点，以便您更快地找到原因并重新启动 |无直接影响|
|挂起作业检测|无直接影响|在几分钟而不是几小时内标记挂起的作业，并可以取消它，以便 Slurm 重新排队它 |无直接影响|

考虑在 32 ml.p5.48xlarge 实例（256 个 NVIDIA H100 GPU）上运行的预训练作业。如果作业在凌晨 1:00 挂起并且直到上午 9:00 才被人注意到，那么就会浪费 256 个实例小时或 2,048 个 GPU 小时。美国东部（弗吉尼亚北部）的 [SageMaker HyperPod 按需价格](https://aws.amazon.com/sagemaker-ai/pricing/) 约为每实例小时 66 美元，挂起成本约为 16,900 美元。通过 15 分钟挂起作业检测规则，HyperPod 会取消停滞的作业，并且 Slurm 将其重新排队。悬挂成本约为 530 美元，可节省约 16,400 美元。

## 使用 `MultiNodeTrainingValidation` 深度健康检查验证训练的正确性

`MultiNodeTrainingValidation` 深度运行状况检查首先在每个实例上训练固定的、已知良好的工作负载，然后跨实例训练。它捕获通过 InstanceStress 和 InstanceConnectivity 但在它们一起训练后产生 NaN 或无限损失的 GPU。如果实例失败，HyperPod [将其标记为失败](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-eks-resiliency-node-labels.html)，并在打开自动节点恢复的情况下重新启动或替换它。当检查在配置期间运行时，这会在您的作业可以使用实例之前发生。

### 它是如何工作的

`MultiNodeTrainingValidation` 在深度健康检查运行中添加了两个测试：

- **Tiny Megatron 测试：** 在每个实例的所有 GPU 上运行简短的 Megatron-LM 训练。
- **威震天测试：** 同一类型实例之间的相同工作负载，通过 EFA 进行通信。

如果训练损失变为 NaN 或无穷大，或者训练未在时限内完成，则测试会失败。工作负载是固定的，因此故障指向硬件而不是模型或代码更改。

下表显示了它如何与其他深度健康检查配合。

| **检查** | **它运行什么** | **它捕获了什么** |
| --- | --- | --- |
| `InstanceStress` | GPU 和 NVLink 计数、DCGM 4 级诊断以及 EFA 延迟和带宽测试（Trainium 上的 Neuron 测试）|硬件丢失、出现故障或不稳定 |
| `InstanceConnectivity` |跨 GPU 实例的 NCCL 测试（Trainium 上的 NCCOM）|实例之间的通信缓慢或中断 |
| `MultiNodeTrainingValidation` |每个实例上的微型威震天测试，跨实例的威震天测试 | GPU 运行但训练不正确：NaN 或无限损失，或训练未及时完成 |

### 先决条件

您需要以下内容：

- 由 Amazon EKS 编排的 Amazon SageMaker HyperPod 集群。
- 支持的启用 EFA 的 NVIDIA GPU 实例类型的实例组，例如 ml.p5.48xlarge。威震天测试在相同类型的实例上运行。

### 为实例组启用 MultiNodeTrainingValidation

HyperPod 在创建或更新实例时运行深度运行状况检查。要包含 `MultiNodeTrainingValidation`，请将其添加到您传递给 `create-cluster` 或 `update-cluster` 的实例组配置中的 `OnStartDeepHealthChecks`。我们打开了所有三项检查：
```
{
    "InstanceGroupName": "<instance-group>",
    "InstanceType": "ml.p5.48xlarge",
    "InstanceCount": 2,
    "LifeCycleConfig": {
        "SourceS3Uri": "s3://<bucket>/<prefix>",
        "OnCreate": "on_create.sh"
    },
    "ExecutionRole": "arn:aws:iam::<account-id>:role/<hyperpod-execution-role>",
    "OnStartDeepHealthChecks": [
        "InstanceStress",
        "InstanceConnectivity",
        "MultiNodeTrainingValidation"
    ]
}
```
要确认设置，请运行以下命令：
```
aws sagemaker describe-cluster \
    --cluster-name <cluster-name> \
    --query "InstanceGroups[?InstanceGroupName=='<instance-group>'].OnStartDeepHealthChecks"
```
输出列出了三项检查：
```
[
    [
        "InstanceStress",
        "InstanceConnectivity",
        "MultiNodeTrainingValidation"
    ]
]
```
### 按需运行 MultiNodeTrainingValidation

您还可以检查集群中已有的实例，例如在长时间预训练运行之前。使用 `StartClusterHealthCheck` API：
```
aws sagemaker start-cluster-health-check \
    --cluster-name <cluster-name> \
    --deep-health-check-configurations \
    '[{"InstanceGroupName": "<instance-group>", "DeepHealthChecks": ["MultiNodeTrainingValidation"]}]'
```
要检查特定实例而不是整个组，请将 `"InstanceIds": [...]` 添加到配置中。

### 检查结果

HyperPod 每次测试都会将一行写入集群的 CloudWatch 日志组 `/aws/sagemaker/Clusters/<cluster-name>/<cluster-id>` 中的 `DeepHealthCheckResults/<id>` 日志流。这是我们在两个 ml.p5.48xlarge 实例上运行的流。 `TINY_MEGATRON` 和 `MEGATRON` 是两个 `MultiNodeTrainingValidation` 测试：
```
2026-11-11T10:58:33Z Deep health check configuration validation passed
2026-11-11T11:01:41Z 2 out of 2 nodes succeeded HARDWARE_CHECK test. Instance IDs: [i-0a1b2c3d4e5f60001 i-0a1b2c3d4e5f60002]
2026-11-11T12:16:07Z 2 out of 2 nodes succeeded DCGM test. Instance IDs: [i-0a1b2c3d4e5f60001 i-0a1b2c3d4e5f60002]
2026-11-11T12:17:14Z 2 out of 2 nodes succeeded EFA test. Instance IDs: [i-0a1b2c3d4e5f60001 i-0a1b2c3d4e5f60002]
2026-11-11T12:21:16Z 2 out of 2 nodes succeeded TINY_MEGATRON test. Instance IDs: [i-0a1b2c3d4e5f60001 i-0a1b2c3d4e5f60002]
2026-11-11T12:22:25Z 0 nodes failed NCCL test at batch size 2. Instance IDs: []
2026-11-11T12:22:29Z 2 out of 2 nodes succeeded NCCL test. Instance IDs: [i-0a1b2c3d4e5f60001 i-0a1b2c3d4e5f60002]
2026-11-11T12:26:31Z 0 nodes failed MEGATRON test at batch size 2. Instance IDs: []
2026-11-11T12:26:31Z 2 out of 2 nodes succeeded MEGATRON test. Instance IDs: [i-0a1b2c3d4e5f60001 i-0a1b2c3d4e5f60002]
```
运行完成后，每个实例都会将结果作为节点标签：
```
kubectl get nodes \
    -l sagemaker.amazonaws.com/instance-group-name=<instance-group> \
    -L sagemaker.amazonaws.com/deep-health-check-status

NAME STATUS ROLES AGE VERSION DEEP-HEALTH-CHECK-STATUS
hyperpod-i-0a1b2c3d4e5f60001 Ready <none> 120m v1.34.2-eks-ecaa3a6 Passed
hyperpod-i-0a1b2c3d4e5f60002 Ready <none> 120m v1.34.2-eks-ecaa3a6 Passed
```
有关培训详细信息，请阅读实例上的 `/var/log/aws/clusters/sagemaker-deep-health-check.log`，例如通过 AWS Systems Manager 会话。在运行排名 0 的实例上，日志以威震天测试摘要结束：
```
CONVERGENCE TEST PASSED
Completed 300 training iterations in 161.5s
Training forward steps: 300
Evaluation forward steps: 20
Total forward steps: 320
Final training loss: 3.6213
Initial training loss: 11.5671
Loss reduction: 7.9458
Training iterations per second: 1.86
```
另一个实例的日志每次迭代都有一行，其中包含损失和 NaN 迭代的运行计数：
```
iteration 300/ 300 | consumed samples: 9600 | elapsed time per iteration (ms): 509.5 |
learning rate: 1.000E-04 | global batch size: 32 | lm loss: 3.397480E+00 | loss scale: 1.0 |
grad norm: 1.386 | number of skipped iterations: 0 | number of nan iterations: 0 |
```
在我们的运行中，在 300 次迭代中，损失从 11.57 下降到 3.62，没有 NaN 或跳过迭代，在 16 个 H100 GPU 上每次迭代大约需要 507 毫秒。

### MultiNodeTrainingValidation 需要多长时间

在我们的两节点集群上，实例完成其生命周期脚本后，完整的深度运行状况检查需要 1 小时 28 分钟。 DCGM 4 级诊断占据了大部分。两次`MultiNodeTrainingValidation`测试增加了大约8分钟。在检查完成之前，实例无法承受工作负载，因此在添加容量时请规划好这段额外的时间。

| **测试** | **检查** | **自上次结果以来的时间** |
| --- | --- | --- |
| `HARDWARE_CHECK` | `InstanceStress` | 3 分钟 |
| DCGM（4级）| `InstanceStress` | 74 分钟 |
|全民教育| `InstanceStress` | 1 分钟 |
| `TINY_MEGATRON` | `MultiNodeTrainingValidation` | 4 分钟 |
| NCCL | `InstanceConnectivity` | 1 分钟 |
| `MEGATRON`（2 个实例）| `MultiNodeTrainingValidation` | 4 分钟 |

请记住，`MultiNodeTrainingValidation` 使用固定参考工作负载测试硬件。通过意味着实例正确地训练了该工作负载。它并不能保证你自己的工作会收敛。我们建议在新容量、替换实例上以及长时间预训练运行之前运行它。

## 使用 HyperPod Kubernetes 资源监控代理捕获集群级故障

HMA 监视每个节点上的硬件，但许多导致训练作业停止的故障发生在 Kubernetes 中。设备插件可能会崩溃循环，直到其节点停止向调度程序提供 GPU，或者污点可能会驱逐作业的 Pod。作业错误很少会命名所涉及的 pod 或节点，因此工程师会根据 kubectl 输出、每个等级的日志和时间戳将发生的情况拼凑起来。

HyperPod Kubernetes 资源监控代理从集群中的一处监控这些资源。当出现问题时，它会告诉您发生了什么变化以及哪些节点、pod 和作业受到影响。它通过 Kubernetes 事件和结构化 CloudWatch 日志进行报告。代理仅报告。它不会重新启动节点或重新启动作业，因为原因可能在于工作负载。 HMA和HyperPod节点恢复仍然处理硬件故障，HyperPod训练操作员仍然处理作业重启。

### 代理如何工作

该代理在 aws-hyperpod 命名空间中作为每个集群的单个 pod 运行，并且更喜欢 CPU 节点，因此它不使用 GPU 容量。它监视以下内容：

- **节点：** 代理报告这些更改：条件更改，例如 `NotReady` 或内存、磁盘或 PID 压力。可分配的 GPU 或 EFA 设备更少。丢失 NVIDIA 功能标签。添加、更改或删除污点。缺少 HyperPod 标签。
- **关键基础设施 Pod：** kube-system、aws-hyperpod 和 kubeflow 中的 DaemonSet Pod，以及训练操作员的控制器。代理报告崩溃循环、重新启动、容器错误和尚未准备就绪的 Pod。
- **DaemonSets：** 缺少或没有可用 Pod 的必需 DaemonSet、部署停止以及在不再允许它们的节点上运行的 Pod。
- **训练作业：** HyperPodPyTorchJob、Kubeflow PyTorchJob (v1) 和 Kubeflow TrainJob (v2)。当作业失败时，代理会使用作业的 Pod 和节点记录失败原因。
- **NCCL 通信：** 对于选择加入的作业，作业的 NCCL 通信器的状态可从 NCCL 的内置可靠性、可用性和可服务性 (RAS) 子系统中读取。

代理报告在两个地方发现的内容：

- 受影响的节点、pod、DaemonSet 或作业上的 **Kubernetes 事件**。警告事件标志着问题，正常事件标志着问题的恢复。您可以使用 kubectl get events 和 kubectl describe 来阅读它们。
- 集群的 CloudWatch 日志组中的 **结构化 JSON 日志**，在 Kubernetes 事件过期后保留历史记录。

下表列出了您最有可能看到的事件。

| **事件原因** | **引发时间** |
| --- | --- |
|培训工作失败 | HyperPodPyTorchJob 或 Kubeflow 作业失败。该消息包括来自作业操作员的失败原因。 |
| CriticalPodCrashLoop、CriticalPodRestarted | CriticalPodCrashLoop设备插件、HMA 或其他关键 Pod 崩溃循环或重新启动。 |
| NecessaryDaemonSet 缺失 |您根据需要声明的 DaemonSet 丢失或没有可用的 Pod。 |
|节点资源降级 |节点的可分配 GPU 或 EFA 设备丢失或消失。 |
| NodeConditionDegraded | 节点条件降级节点变为 NotReady 或报告内存、磁盘或 PID 压力。 |
| NodeTaintAdded，NoExecuteTaintApplied |节点被污染。对于 NoExecute 污点，日志列出了可能被驱逐的 Pod 和作业。 |
| DaemonSet 计划错误 | DaemonSet Pod 正在不再允许它们运行的​​节点上运行。 |
| NodeRecovered、PodRecovered、DaemonSetRecovered |之前报告的问题已经解决。 |

有关事件的完整列表，请参阅[文档](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-eks-resiliency.html)。

### 先决条件

您需要以下内容：

- 由 Amazon EKS 编排的 SageMaker HyperPod 集群。
- 对于现有集群，kubectl 和 Helm 可以访问集群，以及 [sagemaker-hyperpod-cli](https://github.com/aws/sagemaker-hyperpod-cli) 存储库中的 HyperPod Helm 图表。
- 训练容器中的 NCCL 2.24 或更高版本（如果您想监控 NCCL 通信）。

### 安装并验证代理

如果您的集群已使用 HyperPod Helm 图表，请首先应用代理的自定义资源定义 (CRD)，因为 Helm 在升级过程中不会安装 CRD。然后在代理打开的情况下升级版本：
```
git clone https://github.com/aws/sagemaker-hyperpod-cli.git
cd sagemaker-hyperpod-cli/helm_chart
helm dependencies update HyperPodHelmChart

kubectl apply \
    -f HyperPodHelmChart/charts/hyperpod-kubernetes-resource-monitor/crds/

helm upgrade dependencies HyperPodHelmChart \
    --namespace kube-system \
    --reset-then-reuse-values \
    --set hyperpod-kubernetes-resource-monitor.enabled=true \
    --set hyperpod-kubernetes-resource-monitor.region=<region>
```
此次升级还将图表中的其他 HyperPod 组件（例如 HMA 和设备插件）移至图表的当前版本。要查看首先会发生什么变化，请使用 `--dry-run=server` 运行相同的命令。

检查代理是否正在运行以及其运行状况报告是否存在：
```
kubectl get deployment \
    -n aws-hyperpod \
    hyperpod-kubernetes-resource-monitoring-agent

kubectl get hyperpodkrmaconfigs default -o yaml
```
运行状况报告列出了代理跟踪的 HyperPod 组件（例如 HMA）及其状态上次更改的时间：
```
status:
  components:
    - name: DaemonSet/aws-hyperpod/health-monitoring-agent
      since: "2026-11-10T16:47:57Z"
      status: Healthy
      instances: []
  lastReportTime: "2026-11-10T17:19:36Z"
```
默认情况下，HMA 是唯一需要的 DaemonSet。如果您的集群使用 HyperPod Helm 图表中的设备插件，请添加它们，以便代理报告缺少的插件。还要添加训练作业运行的命名空间，以便它可以将 Pod 故障与其作业关联起来。每个列表都会替换其默认值，因此请保留默认条目。将以下内容另存为 `krma-values.yaml`：
```
hyperpod-kubernetes-resource-monitor:
  monitoring:
    monitoredNamespaces:
      - aws-hyperpod
      - kube-system
      - default
      - kubeflow
      - ml-team-a
    necessaryDaemonsets:
      - name: health-monitoring-agent
        namespace: aws-hyperpod
      - name: dependencies-nvidia-device-plugin
        namespace: kube-system
      - name: dependencies-aws-efa-k8s-device-plugin
        namespace: kube-system
```
然后应用它：
```
helm upgrade dependencies HyperPodHelmChart \
    --namespace kube-system \
    --reset-then-reuse-values \
    -f krma-values.yaml
```
### 查看代理报告的内容

为了了解 HyperPod Kubernetes 资源监控代理如何处理基础设施故障，我们将一个小型 DaemonSet 部署到 aws-hyperpod 中，将其固定到一个节点，并使其在启动几秒钟后退出。它的行为就像一个崩溃循环设备插件，而不接触真实的设备插件。几秒钟内，代理在 pod 和 DaemonSet 上引发了事件：
```
kubectl get events -A \
    --field-selector source=hyperpod-kubernetes-resource-monitoring-agent

NAMESPACE TYPE REASON OBJECT MESSAGE
aws-hyperpod Warning CriticalPodRestarted pod/demo-plugin-4wsqw Critical infrastructure pod container crash restarted (count: 2)
aws-hyperpod Warning CriticalPodCrashLoop pod/demo-plugin-4wsqw Critical infrastructure pod container crash in CrashLoopBackOff
aws-hyperpod Warning DaemonSetMisscheduled daemonset/demo-plugin DaemonSet has 1 misscheduled pods
```
接下来，我们运行了两个节点的 HyperPodPyTorchJob 并在训练期间退出了一个等级。代理在作业中引发了 TrainingJobFailed 事件：
```
NAMESPACE TYPE REASON OBJECT MESSAGE
ml-team-a Warning TrainingJobFailed hyperpodpytorchjob/llama-pretrain Training job HyperPod PyTorchJob failed:
Fault detected on training pod llama-pretrain-pod-7dc7c-nh5gb:
A training worker process has crashed: Local Rank 0 exited ...
```
它还将失败以及涉及的 Pod 和节点写入 CloudWatch，因此您无需从作业的 Pod 列表中查找它们：
```
{"level":"warn","msg":"=== Job Failure Detected ===","component":"HyperpodPyTorchJob",
"job":"llama-pretrain","namespace":"ml-team-a","type":"HyperPod PyTorchJob",
"reason":"Fault detected on training pod llama-pretrain-pod-7dc7c-nh5gb: A training worker process has crashed ..."}
{"level":"warn","msg":"Affected Pods","component":"HyperpodPyTorchJob",
"pods":["llama-pretrain-pod-7dc7c-nh5gb","llama-pretrain-pod-7dc7c-f9dmg"]}
{"level":"warn","msg":"Affected Nodes","component":"HyperpodPyTorchJob",
"nodes":["hyperpod-i-0a1b2c3d4e5f60001","hyperpod-i-0a1b2c3d4e5f60002"]}
```
代理将这些日志写入名为 `SageMakerClusterMonitoringAgent/<instance-group>/<instance-id>` 的流中的集群日志组 `/aws/sagemaker/Clusters/<cluster-name>/<cluster-id>`。当它移动到另一个节点时，它会启动一个新流，因此可以按流前缀进行过滤。有关示例查询，请参阅[文档](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-eks-resiliency.html)。

### 监控作业的 NCCL 通信

NCCL 2.24 及更高版本包括可靠性、可用性和可服务性 (RAS) 子系统，它是每个 NCCL 进程中的一个小型侦听器，用于报告作业通信器的状态。对于选择加入的作业，代理每 30 秒从每个 Pod 读取此报告。

默认情况下，NCCL 将 RAS 侦听器绑定到 pod 内的 `localhost`，代理无法到达它。要选择加入作业，请将侦听器绑定到 pod IP。这使得 Pod 网络上的端口 28028 可以访问，NVIDIA 的文档指出这具有安全隐患。在打开它之前，应用一个 Kubernetes NetworkPolicy，该策略仅允许来自代理的 pod 的 TCP 端口 28028，并且仍然允许作业自己的 pod 之间的流量。代理的[文档](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-eks-resiliency.html) 包含一个示例策略。然后在训练容器中设置`NCCL_RAS_ADDR`：
```
apiVersion: sagemaker.amazonaws.com/v1
kind: HyperPodPyTorchJob
...
containers:
  - name: pytorch
    env:
      - name: POD_IP
        valueFrom:
          fieldRef: {fieldPath: status.podIP}
      - name: NCCL_RAS_ADDR # set only after the NetworkPolicy is in place
        value: "$(POD_IP):28028"
```
要确认设置，请使用 `NCCL_DEBUG=INFO` 和 `NCCL_DEBUG_SUBSYS=INIT,RAS` 打开 NCCL 调试日志记录。然后，每个等级都会记录 RAS 侦听的地址：
```
[default3]:llama-pretrain-workers-6c7f5bb445-gxnsf:129:203 [3] NCCL INFO RAS client listening socket at 10.0.1.11<28028>
```
如果地址是 `::1` 或 `127.0.0.1`，则未设置 `NCCL_RAS_ADDR`，并且代理无法到达侦听器。

对于每个受监控的作业，代理将每个 Pod 的结果组合成作业级别的状态。当每个 pod 返回有效报告时，该作业是健康的；当只有一些 pod 返回有效报告时，该作业会降级；当没有一个 pod 返回时，作业是不健康的。不健康通常意味着训练过程已经停止。

代理在每个轮询周期后记录摘要。在两个 ml.p5.48xlarge 实例上运行时，每个周期都报告两个训练 Pod 均运行良好，间隔 30 秒：
```
{"level":"info","timestamp":"2026-11-12T07:14:27.163Z","msg":"NCCL RAS monitoring cycle completed","component":"nccl-ras-informer-llama-pretrain","duration":4.00535305,"total_endpoints":2,"healthy":2,"failed":0,"overall_status":"healthy"}
```
该代理还将每个 RAS 报告写入 CloudWatch，以便您可以在作业仍在运行时发现通信器问题。在我们的测试中，我们对两节点作业进行了一级停止调用 `all_reduce`。下一个轮询周期的报告显示通信器失步，并列出了落后的排名、GPU、进程和节点：
```
Group Comms Nodes Ranks Ranks Ranks Status Errors
# in group per comm per node per comm in group
0 1 2 1 2 2 RUNNING MISMATCH

#0-0 (2958ae23ccc57a88) MISMATCH
Communicator ranks have different AllReduce operation counts
Rank 0 has launched up to operation 3078 -- GPU 0 managed by process 473 on node 10.0.1.11
Rank 1 has launched up to operation 3077 -- GPU 0 managed by process 474 on node 10.0.2.22
```
Rank 1 是Rank 0 后面的一个操作，因此从节点 10.0.2.22 上的Rank 1 GPU 开始。

## 检测并恢复 HyperPod Slurm 集群上挂起的作业

训练作业可以挂起而不退出。 NCCL 超时、数据管道停滞或死锁可能会使作业保留其 GPU，而 Slurm 仍将其显示为正在运行。它会保持这种状态，直到有人注意到丢失或日志已停止更改。运行 Slurm 的团队通常会构建自己的看门狗脚本和警报来捕获这些作业，然后需要维护它们。

今天，我们将为 SageMaker HyperPod Slurm 集群启动挂起作业检测。它找到这些作业，将事件写入 CloudWatch，并可以取消挂起的作业，以便 Slurm 将其放回队列中。您可以使用指向小规则文件的环境变量为每个作业打开它。它不需要更改您的训练脚本或容器，并且可以与 PyTorch、TensorFlow、JAX 和自定义脚本配合使用。

### 挂起作业检测的工作原理

挂起作业检测作为代理在每个节点上运行，并且默认情况下处于关闭状态。代理仅监视将 `HYPERPOD_HANG_RULES` 环境变量设置为规则文件路径的作业。规则文件决定代理如何检测挂起：

- *默认检测*观察作业的标准输出和 GPU 活动。当输出长时间停止而 GPU 处于空闲状态但仍保留内存时，它会声明挂起。当一个节点发生故障而其他节点在屏障处等待时，这就是会合挂起的样子。当输出停止较长时间时，无论 GPU 正在做什么，它也会声明挂起。在我们的测试中，第一个案例在作业最后一次输出 15 分钟后触发。
- *自定义规则*查看您的日志以查找您选择的正则表达式。当诸如训练步骤消息之类的行在超时时间内没有出现时，进度规则将声明挂起。一旦出现 NCCL 错误等行，错误规则就会声明挂起。自定义规则替换该作业的默认检测。

|  | **默认检测** | **自定义规则** |
| --- | --- | --- |
|用 | 打开{“启用”：true} |一个或多个已启用的 log_pattern 规则 |
|当 | 时声明挂起当 GPU 空闲但保留内存时输出停止，或者输出停止较长时间 |进度模式在超时内未出现，或出现错误模式 |
|错过|使 GPU 忙碌而没有取得进展的作业，例如陷入循环的作业 |悬挂你的图案没有描述。如果模式保持匹配，即使 GPU 空闲，也不会声明挂起 |

当代理声明挂起时，它会将 `HANG_DETECTED` 事件写入 CloudWatch。如果规则文件将操作设置为 `cancel`，则代理也会取消作业，并且 Slurm 会将其重新排队。使用默认操作 `notify`，代理会写入事件并让作业保持运行。

挂起作业检测与[自动恢复](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html) 是分开的，后者会重新启动在硬件故障后退出的作业。自动恢复处理崩溃的作业，挂起作业检测处理继续运行但没有进展的作业。

在 Amazon EKS 编排的 HyperPod 集群上，HyperPod 已在两种情况下检测到挂起作业。 [HyperPod 训练操作员](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-eks-operator-usage.html) 根据作业规范中的规则检查每个 HyperPodPyTorchJob 的日志，并在作业挂起时重新启动该作业。相同的规则还可以重新启动吞吐量下降或损失激增的作业。你不需要雷来做这件事。对于 Ray Train 作业，[HyperPod 挂起作业检测 Ray](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-ray-hung-job-detection.html) 默认情况下会监视每个工作线程，无需更改代码。

### 先决条件

您需要以下内容：

- 由 Slurm 编排的 SageMaker HyperPod 集群。
- 2026 年 11 月 10 日或之后发布的 HyperPod Slurm AMI，其中包括挂起作业检测。在该日期或之后创建的集群已拥有它。要检查现有集群而不更新它，请在集群节点上运行 `srun --help`。如果输出列出 `--no-hang-detection`，则集群支持挂起作业检测。如果没有，请先【更新集群软件】(https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-operate-slurm-cli-command.html)。该更新会替换每个实例的根卷，因此在更新之前请备份其中存储的所有内容。
- 作业中的每个计算节点都可以在同一路径读取的规则文件。代理从每个节点上的该路径读取文件。 Amazon FSx for Lustre 或 Amazon Elastic File System (Amazon EFS) 等共享存储是一个简单的选择。要将规则文件保留在 Amazon Simple Storage Service (Amazon S3) 中，请将它们复制到每个节点上的相同路径，例如在生命周期脚本中。如果您计划使用 `/opt/slurm` 等目录，请首先确认它是跨节点共享的，而不是每个节点本地的。

### 打开挂起作业检测

在共享存储上创建规则文件。最小的有效文件开启默认检测：
```
echo '{"enabled": true}' > /fsx/my-project/rules.json
chmod 600 /fsx/my-project/rules.json
```
代理使用作业指向的任何规则文件，并且不检查谁拥有它。任何可以编辑该文件或在其目录中替换该文件的人都可以更改对使用该文件的每个作业的检测，包括使代理取消这些作业。示例中的 `chmod 600` 将个人规则文件保留为其所有者私有。对于团队共享的文件，请使用 `chmod 644`，以便团队可以读取它，并且只有其维护者可以编辑它。在这两种情况下，使父目录只能由其所有者写入，这样就没有人可以交换文件。

然后在提交时将作业指向规则文件：
```
#!/bin/bash
#SBATCH --job-name=llama-pretrain
#SBATCH --nodes=4
#SBATCH --export=ALL,HYPERPOD_HANG_RULES=/fsx/my-project/rules.json

srun python train.py
```
要将一个规则文件用于多项作业，您还可以在 shell 配置文件或站点范围配置文件脚本中设置 `HYPERPOD_HANG_RULES`。

当受监控的作业启动时，其输出的第一行显示代理已注册它：
```
[Auto Resume] Info: [hang_detection] Exported stdout path for job 1: /fsx/my-project/llama-pretrain-1.out
[Auto Resume] Info: [hang_detection] Registered job step: job=1 step=0 node=ip-10-1-40-47
```
当规则文件无效时，这些行也会出现，因此也请检查 CloudWatch 中的 `CONFIG_ERROR` 事件，如下一节所述。

### 添加自定义规则来跟踪训练进度

默认检测无法捕获导致 GPU 忙碌而不取得进展的作业，因此我们建议至少有一个规则来监视您的训练步骤或周期。如果 45 分钟内没有 epoch 完成，或者一旦出现 NCCL 错误，以下规则文件将取消作业：
```
{
    "enabled": true,
    "rules": [
        {
            "name": "epoch_progress",
            "type": "log_pattern",
            "enabled": true,
            "log_pattern": "Epoch \\d+/\\d+ complete",
            "start_timeout_minutes": 30,
            "timeout_minutes": 45,
            "stop_pattern": "Training complete"
        },
        {
            "name": "nccl_error",
            "type": "log_pattern",
            "enabled": true,
            "log_pattern": "NCCL error",
            "fault_on_match": true
        }
    ],
    "action_policy": {
        "action": "cancel"
    }
}
```
这些字段的工作方式如下：

- 将每个规则的启用设置为 true。默认情况下规则处于关闭状态。
- `start_timeout_minutes` 是在模式首次出现之前作业可以运行的时间。将其设置为比作业加载模型、编译和恢复检查点所需的时间更长。
- `timeout_minutes` 是此后该形态可以保持不存在的时间长度。将其设置为比最大正常间隙更长，包括检查点保存和评估。
- `stop_pattern` 在匹配时关闭规则，因此训练结束后的工作不会被标记。
- `fault_on_match` 标记错误模式。一场比赛意味着工作悬而未决。

默认情况下，代理读取作业的 Slurm 输出文件。要观看不同的文件，请设置 `monitoring.log_file`。要减少误报，请在规则上设置 `metric_evaluation_data_points`，以便在代理声明挂起之前连续多次 10 秒检查必须失败。一个规则文件最多可包含 20 条规则，最大大小为 1 MB。

从 `"action": "notify"` 开始，同时调整超时和模式，并在事件匹配真实挂起后切换到 `cancel`。

### 在 CloudWatch 中查看挂起作业检测事件

HyperPod 将检测事件从控制器节点写入流 `SageMakerHangJobDetectionEvents/<controller-instance-group>/<controller-instance-id>` 中的集群的 CloudWatch 日志组 `/aws/sagemaker/Clusters/<cluster-name>/<cluster-id>`。每个作业的事件都会落在该流中，无论作业在哪个节点上运行。要查找一项作业的事件，请按其作业 ID 进行筛选：
```
aws logs filter-log-events \
    --log-group-name /aws/sagemaker/Clusters/<cluster-name>/<cluster-id> \
    --log-stream-name-prefix SageMakerHangJobDetectionEvents/ \
    --filter-pattern '{ $.job_id = "12345" }'
```
我们在具有两个 ml.p5.48xlarge 实例的 HyperPod Slurm 集群上测试了每种检测方法。第一个测试作业分配了 GPU 内存，然后停止生成输出。默认检测在最后一次输出后 15 分钟对其进行标记：
```
{
    "time": "2026-11-12T16:49:36.39710952Z",
    "level": "INFO",
    "msg": "HANG_DETECTED",
    "event_type": "HANG_DETECTED",
    "job_id": "1",
    "step_id": "0",
    "node": "ip-10-1-40-47",
    "evidence": "stdout stale for 15 min and GPU idle with memory allocated",
    "layer": "signal_evaluator",
    "detected_at": "2026-11-12T16:49:36.378940227Z",
    "job_action": "notify",
    "config_source": "per_job_env_var"
}
```
`layer` 字段显示触发的方法：`signal_evaluator` 用于默认检测，或 `pattern_evaluator` 用于自定义规则。在第二个测试中，在作业最后一步后 2 分钟触发了 2 分钟超时的进度规则。第三种情况是，在作业打印 NCCL 错误行后大约一秒，错误规则被触发。因为该规则文件使用了取消，所以代理还使用 Slurm 所采取的操作编写了一个 `HANG_ACTION_TAKEN` 事件（我们省略了时间、级别和消息字段）：
```
{"event_type":"HANG_DETECTED","job_id":"3","step_id":"0","node":"ip-10-1-40-47","evidence":"rule \"nccl_error\": fault pattern matched immediately","layer":"pattern_evaluator","detected_at":"2026-11-12T16:34:41.870908329Z","job_action":"cancel","config_source":"per_job_env_var"}
{"event_type":"HANG_ACTION_TAKEN","job_id":"3","action":"requeue","node":"ip-10-1-40-47","instance_id":"i-0a1b2c3d4e5f60001"}
```
Slurm 将作业放回到队列中，大约 2.5 分钟后开始重新排队运行。 `sacct` 显示两次运行：
```
$ sacct --duplicates -X -j 3 --format=JobID,State,Restarts,Start,End
JobID State Restarts Start End
----------- --------- ------- ------------------- -------------------
3 REQUEUED 0 2026-11-12T16:34:25 2026-11-12T16:34:41
3 COMPLETED 1 2026-11-12T16:37:10 2026-11-12T16:37:26
```
Slurm 重新排队作业直至集群的 `MaxBatchRequeue` 限制，在我们的集群上为 5。使用 `#SBATCH --no-requeue` 提交的作业改为报告 `"action": "cancel"` 并保持取消状态。对于 `notify`，没有 `HANG_ACTION_TAKEN` 事件。该代理跟踪 `HANG_DETECTED`，记录为 `Hang notification sent, no automatic action taken`。

如果规则文件丢失或无效，代理不会监视作业，而是写入 `CONFIG_ERROR` 事件。以下是具有 JSON 语法错误的规则文件的事件：
```
{"event_type":"CONFIG_ERROR","job_id":"5","node":"ip-10-1-40-47","config_path":"/fsx/my-project/rules.json","error":"config file found but failed to load: load failed: invalid JSON in config file /fsx/my-project/rules.json: unexpected end of JSON input","message":"Hang detection rules file is invalid and will not be applied. Please fix the rules file and resubmit your job."}
```
该作业在没有监控的情况下运行完成，并且 `sbatch`、`squeue` 或作业的输出中没有出现任何内容。使用简短作业测试新规则文件，并在将其用于生产作业之前检查此事件。

通过通知，作业将继续运行，直到有人对该事件采取行动。要获取警报，请为 `HANG_DETECTED` 事件创建 CloudWatch 指标过滤器以及通知 Amazon Simple Notification Service (Amazon SNS) 主题的警报：
```
aws logs put-metric-filter \
    --log-group-name /aws/sagemaker/Clusters/<cluster-name>/<cluster-id> \
    --filter-name hung-jobs \
    --filter-pattern '{ $.event_type = "HANG_DETECTED" }' \
    --metric-transformations \
    metricName=HungJobsDetected,metricNamespace=HyperPod/HungJobs,metricValue=1
```
### 关闭挂起作业检测

要关闭对本来继承 `HYPERPOD_HANG_RULES` 的作业的检测，请将 `--no-hang-detection` 添加到 `srun` 或 `sbatch` 以覆盖作业中的每个步骤。要为每个使用规则文件的作业关闭它，请在文件中设置 `"enabled": false`。正在运行的作业会保留其当前设置，并且更改会应用到您之后提交的作业。
```
srun --no-hang-detection python train.py
```
## 结论

节点健康状况对于可靠的分布式训练至关重要，但它并不能提供工作负载健康状况的完整情况。 `MultiNodeTrainingValidation` 检测通过硬件诊断但产生无效训练结果的实例。 HyperPod Kubernetes 资源监控代理将 Kubernetes 基础设施故障连接到所涉及的作业、Pod 和节点。挂起作业检测可识别在停止进展后仍保持活动状态的 Slurm 作业，并可自动将它们返回到队列。

这些功能共同帮助您更早地检测故障、缩短调查时间，并通过减少花在无法取得有用进展的工作负载上的 GPU 时间来提高产出。添加或重新验证容量时使用 `MultiNodeTrainingValidation`，在支持的 Amazon EKS 集群上连续运行 HyperPod Kubernetes 资源监控代理，并在切换到自动取消之前以通知模式开始挂起作业检测。要开始使用，请参阅 [Amazon EKS 的 SageMaker HyperPod 弹性文档](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-eks-resiliency.html) 和 [Slurm 的挂起作业检测文档](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-hang-detection.html)。要了解更多信息，请访问 [Amazon SageMaker HyperPod 产品页面](https://aws.amazon.com/sagemaker-ai/hyperpod/)。

*作者要感谢 Hengyu Lou、Vishal Shahane、Ziyao Huang 和 Haard Mehta 对本文和专题的贡献。*

## 关于作者
