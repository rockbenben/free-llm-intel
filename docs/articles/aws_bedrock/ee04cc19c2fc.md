---
vendor: aws_bedrock
title: 在 Amazon SageMaker HyperPod 上引入工作负载恢复和扩展基础设施检查
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/introducing-workload-recovery-and-expanded-infrastructure-checks-on-amazon-sagemaker-hyperpod
date: 2026-11-18
lang: zh
captured: 2026-11-21
extractor: readability-v1
translator: agent
status: translated
body_sha: 1c40c167604f
---

## [人工智能](https://aws.amazon.com/blogs/machine-learning/)

# 在 Amazon SageMaker HyperPod 上引入工作负载恢复和扩展基础设施检查

大型训练作业即便每个节点看起来都健康，也可能失败。一颗存在细微故障的 GPU 能通过压力测试，却依然返回错误的数值。作业因 NCCL 超时而卡住时，GPU 仍被它占着，Slurm 也依旧显示它正在运行。某个节点上的设备插件崩溃，作业随之失败，而报错信息里根本不会提到这个插件。团队往往要等到 loss 发散或作业失败之后才发现这些问题，此时算力已经白白烧掉。上述每一种故障都会拉低有效吞吐量——也就是集群时间中真正用于有效训练的那部分占比。今天我们推出 Amazon SageMaker HyperPod 上的工作负载恢复与基础设施检查，可以更早发现这些故障，提升训练工作负载的有效吞吐量。

SageMaker HyperPod 已经能处理上报硬件故障的节点：健康监控 agent（HMA）持续观察每个节点上的 GPU 错误，深度健康检查在配置阶段测试节点，自动节点恢复则重启或替换有故障的硬件。这些功能一次只看一个节点的硬件，无法判断 GPU 是否训练正确、作业是否仍在推进，也无法判断作业依赖的 Kubernetes 组件是否正常工作。

本文将逐一介绍捕捉这些故障的三项新能力。对每一项，我们都会说明如何配置，以及它发现问题时会报告什么：

- `MultiNodeTrainingValidation` 是面向由 Amazon Elastic Kubernetes Service（Amazon EKS）编排的 HyperPod 集群的新深度健康检查。无论是 HyperPod 配置实例时，还是你按需触发检查时，它都会先在单个实例上训练一个小模型，再在同一类型的多个实例之间训练。只要 loss 变成 NaN 或无穷大，或者训练未在时限内完成，该实例就会被判为失败。
- HyperPod Kubernetes Resource Monitoring Agent 观察 EKS 集群的 Kubernetes 层，捕捉设备插件陷入崩溃循环、DaemonSet 缺失、节点被加上污点等问题。作业失败时，它会把涉及的 Pod 和节点以 Kubernetes 事件和 Amazon CloudWatch 日志的形式报告出来。
- 挂起作业检测负责找出已经停止推进的 Slurm 作业。每个节点上的 agent 会观察作业的输出与 GPU 活动，或你定义的日志模式。它向 CloudWatch 写入事件，并可以取消作业，让 Slurm 将其重新排队。

## 为什么只有节点健康还不够

现有的 HyperPod 弹性能力一次只检查单个节点。健康监控 agent（HMA）盯住每个节点上的 GPU 错误，例如 Xid 与 NVLink 故障、Elastic Fabric Adapter（EFA）错误和内核错误。InstanceStress 深度健康检查执行 DCGM 四级诊断，测试每个实例的 GPU、GPU 显存、NVLink 与 EFA 设备。InstanceConnectivity 检查则在 GPU 实例之间运行 NCCL 测试，在 AWS Trainium 上运行 NCCOM 测试。这些检查合起来能确认每个节点的硬件是好的，却看不出 GPU 计算是否正确、作业是否仍在推进、集群的 Kubernetes 组件是否健康。有三类故障能绕过它们：

- **数值故障——** 一颗 GPU 可以通过全部硬件测试，却仍然算出错误结果。最先暴露的迹象，往往是生产训练中 loss 变成 NaN 或无穷大。Meta 在为期 54 天的 Llama 3 405B 预训练中遇到 419 次意外中断，其中 6 次被归因于静默数据损坏（[The Llama 3 Herd of Models](https://arxiv.org/abs/2407.21783)）。
- **作业挂起——** NCCL 超时、数据管道停滞或死锁都能让作业停住却不退出。作业继续占着 GPU 和显存，Slurm 也一直报它正在运行，直到有人去查 loss 曲线或日志。
- **集群级故障——** 有些故障出在 Kubernetes 里，而不是节点的硬件上：设备插件反复崩溃重启，必需的 DaemonSet 在新节点上始终起不来，或者不同节点上的 rank 在 NCCL 集合通信中失去同步。HMA 是逐个节点单独检查的，因此看不到这类问题。作业失败时，报错通常也不会说明是哪个 Pod 或哪个节点造成的。

## 方案概览

这三项能力分别覆盖训练运行中的不同环节。`MultiNodeTrainingValidation` 在实例配置时或按需运行时执行，确认其 GPU 能正确训练。挂起作业检测伴随每个 Slurm 作业运行，捕捉已经停止推进的作业。HyperPod Kubernetes Resource Monitoring Agent 持续观察集群，并在作业失败时报告涉及的 Pod 与节点。下表对三者做了总结。

| **能力** | **捕捉什么** | **何时运行** | **可用范围** |
| --- | --- | --- | --- |
| `MultiNodeTrainingValidation` 深度健康检查 | 在通过硬件检查的 GPU 上出现 NaN 或无穷大的 loss，或训练未在时限内完成 | 创建或更新实例时，或按需触发 | EKS 集群，限支持 EFA 的 NVIDIA GPU 实例类型 |
| HyperPod Kubernetes Resource Monitoring Agent | 节点状态变化、Pod 与 DaemonSet 故障、训练作业失败，并给出涉及的 Pod 和节点；以及主动启用的作业的 NCCL 通信状态 | 持续运行 | EKS 集群 |
| 挂起作业检测 | 停止推进但不退出的作业 | 每个作业运行期间 | Slurm 集群 |

挂起作业检测是 Slurm 集群上的新功能。在 EKS 集群上，HyperPod 早已能检测通过 [HyperPod training operator](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-eks-operator-usage.html) 运行的挂起作业，Ray Train 作业则[默认启用挂起检测](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-ray-hung-job-detection.html)。这两种方式我们都会在挂起作业检测一节中说明。

每项能力针对的是有效吞吐量流失的不同来源。调度有效吞吐量指作业所需全部资源都可用的时间占比；运行时有效吞吐量指这些时间里作业真正向前推进的占比；程序有效吞吐量指作业能达到硬件峰值性能的占比。下表列出每项能力的作用。

| **能力** | **调度有效吞吐量** | **运行时有效吞吐量** | **程序有效吞吐量** |
| --- | --- | --- | --- |
| `MultiNodeTrainingValidation` | 未通过训练测试的实例会被打上标签，并在开启自动节点恢复时被替换，作业因此不会跑在产出无效结果的硬件上 | 因故障 GPU 导致 NaN 或无穷大 loss 而损失的生产训练更少 | 标记训练未能在时限内完成的实例 |
| HyperPod Kubernetes Resource Monitoring Agent | 报告丢失 GPU 或 EFA 设备的节点、缺失的设备插件以及污点，帮助你更快恢复容量 | 指出失败作业背后的 Pod 与节点，让你更快定位原因并重启 | 无直接影响 |
| 挂起作业检测 | 无直接影响 | 几分钟内而非几小时后标出挂起作业，并可取消它让 Slurm 重新排队 | 无直接影响 |

设想一个跑在 32 台 ml.p5.48xlarge 实例（256 颗 NVIDIA H100 GPU）上的预训练作业。如果作业在凌晨 1:00 挂起，直到上午 9:00 才被发现，就白白浪费了 256 个实例小时，也就是 2,048 个 GPU 小时。按美国东部（弗吉尼亚北部）区域 [SageMaker HyperPod 按需价格](https://aws.amazon.com/sagemaker-ai/pricing/)约每实例小时 66 美元计算，这次挂起要花掉约 16,900 美元。若配置 15 分钟的挂起作业检测规则，HyperPod 会取消停滞的作业，由 Slurm 重新排队，挂起成本降到约 530 美元，节省约 16,400 美元。

## 用 `MultiNodeTrainingValidation` 深度健康检查验证训练正确性

`MultiNodeTrainingValidation` 深度健康检查会训练一个固定的、已知可用的工作负载：先在每个实例内部训练，再跨实例训练。它能抓出那些通过了 InstanceStress 与 InstanceConnectivity、但一旦联合训练就产生 NaN 或无穷大 loss 的 GPU。实例失败时，HyperPod 会[将其标记为失败](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-eks-resiliency-node-labels.html)，若已开启自动节点恢复，还会重启或替换它。检查在配置阶段运行时，这一切都发生在作业能够使用该实例之前。

### 工作方式

`MultiNodeTrainingValidation` 为深度健康检查增加了两项测试：

- **Tiny Megatron 测试：** 在每个实例的全部 GPU 上做一次简短的 Megatron-LM 训练。
- **Megatron 测试：** 在同一类型的多个实例之间跑同样的工作负载，通过 EFA 通信。

只要训练 loss 变成 NaN 或无穷大，或者训练未在时限内完成，任意一项测试都会让实例判为失败。工作负载是固定的，因此失败指向硬件，而不是模型或代码改动。

下表说明它与其他深度健康检查的关系。

| **检查项** | **运行内容** | **捕捉什么** |
| --- | --- | --- |
| `InstanceStress` | GPU 与 NVLink 数量、DCGM 四级诊断、EFA 延迟与带宽测试（Trainium 上为 Neuron 测试） | 缺失、故障或不稳定的硬件 |
| `InstanceConnectivity` | 跨 GPU 实例的 NCCL 测试（Trainium 上为 NCCOM） | 实例之间通信缓慢或中断 |
| `MultiNodeTrainingValidation` | 每个实例上的 Tiny Megatron 测试、跨实例的 Megatron 测试 | 能运行但训练不正确的 GPU：NaN 或无穷大 loss，或训练未在时限内完成 |

### 前提条件

你需要准备：

- 由 Amazon EKS 编排的 Amazon SageMaker HyperPod 集群。
- 一个实例组，使用受支持的、启用 EFA 的 NVIDIA GPU 实例类型，例如 ml.p5.48xlarge。Megatron 测试会在同一类型的多个实例之间运行。

### 为实例组开启 MultiNodeTrainingValidation

HyperPod 在创建或更新实例时执行深度健康检查。要纳入 `MultiNodeTrainingValidation`，把它加到传给 `create-cluster` 或 `update-cluster` 的实例组配置中的 `OnStartDeepHealthChecks` 里即可。我们开启了全部三项检查：

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

执行以下命令确认该设置：

```
aws sagemaker describe-cluster \
    --cluster-name <cluster-name> \
    --query "InstanceGroups[?InstanceGroupName=='<instance-group>'].OnStartDeepHealthChecks"
```

输出会列出这三项检查：

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

你也可以检查已经在集群里的实例，比如在一次长时间的预训练之前。使用 `StartClusterHealthCheck` API：

```
aws sagemaker start-cluster-health-check \
    --cluster-name <cluster-name> \
    --deep-health-check-configurations \
    '[{"InstanceGroupName": "<instance-group>", "DeepHealthChecks": ["MultiNodeTrainingValidation"]}]'
```

如果只想检查指定实例而非整个组，在配置里加上 `"InstanceIds": [...]`。

### 查看结果

HyperPod 会为每项测试向集群 CloudWatch 日志组 `/aws/sagemaker/Clusters/<cluster-name>/<cluster-id>` 中名为 `DeepHealthCheckResults/<id>` 的日志流写一行记录。下面是我们在两台 ml.p5.48xlarge 实例上运行时得到的日志流。`TINY_MEGATRON` 和 `MEGATRON` 就是 `MultiNodeTrainingValidation` 的两项测试：

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

运行结束后，每个实例都会把结果写成一个节点标签：

```
kubectl get nodes \
    -l sagemaker.amazonaws.com/instance-group-name=<instance-group> \
    -L sagemaker.amazonaws.com/deep-health-check-status

NAME STATUS ROLES AGE VERSION DEEP-HEALTH-CHECK-STATUS
hyperpod-i-0a1b2c3d4e5f60001 Ready <none> 120m v1.34.2-eks-ecaa3a6 Passed
hyperpod-i-0a1b2c3d4e5f60002 Ready <none> 120m v1.34.2-eks-ecaa3a6 Passed
```

想看训练细节，可以读取实例上的 `/var/log/aws/clusters/sagemaker-deep-health-check.log`，例如通过 AWS Systems Manager 会话。在运行 rank 0 的那台实例上，日志末尾是 Megatron 测试的汇总：

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

另一台实例的日志则为每次迭代写一行，包含 loss 以及 NaN 迭代的累计计数：

```
iteration 300/ 300 | consumed samples: 9600 | elapsed time per iteration (ms): 509.5 |
learning rate: 1.000E-04 | global batch size: 32 | lm loss: 3.397480E+00 | loss scale: 1.0 |
grad norm: 1.386 | number of skipped iterations: 0 | number of nan iterations: 0 |
```

在我们的运行中，16 颗 H100 GPU 上 loss 经过 300 次迭代从 11.57 降到 3.62，没有出现 NaN 或跳过的迭代，每次迭代约 507 毫秒。

### MultiNodeTrainingValidation 需要多长时间

在我们的双节点集群上，实例执行完生命周期脚本之后，完整的深度健康检查耗时 1 小时 28 分钟，其中大部分时间花在 DCGM 四级诊断上。两项 `MultiNodeTrainingValidation` 测试额外增加了约 8 分钟。检查不结束，实例就无法承接工作负载，因此扩容时要把这段时间计算在内。

| **测试** | **检查** | **距上一结果的时间** |
| --- | --- | --- |
| `HARDWARE_CHECK` | `InstanceStress` | 3 分钟 |
| DCGM（四级） | `InstanceStress` | 74 分钟 |
| EFA | `InstanceStress` | 1 分钟 |
| `TINY_MEGATRON` | `MultiNodeTrainingValidation` | 4 分钟 |
| NCCL | `InstanceConnectivity` | 1 分钟 |
| `MEGATRON`（2 个实例） | `MultiNodeTrainingValidation` | 4 分钟 |

需要说明的是，`MultiNodeTrainingValidation` 用一个固定的参考工作负载来检验硬件。通过只代表这些实例能正确训练该工作负载，并不保证你自己的作业一定能收敛。建议在新扩容的容量上、在替换实例上，以及长时间预训练开始之前运行它。

## 用 HyperPod Kubernetes Resource Monitoring Agent 捕捉集群级故障

HMA 盯的是每个节点上的硬件，但很多让训练作业停摆的故障发生在 Kubernetes 里。设备插件可能一直崩溃重启，直到节点不再向调度器提供 GPU；污点也可能把作业的 Pod 驱逐出去。作业报错很少点明涉及的 Pod 或节点，工程师只能从 kubectl 输出、各 rank 的日志和时间戳里拼凑发生了什么。

HyperPod Kubernetes Resource Monitoring Agent 从集群中的一个位置统一观察这些资源。出问题时，它会告诉你发生了什么变化，以及哪些节点、Pod 和作业受影响，并通过 Kubernetes 事件和结构化 CloudWatch 日志输出。这个 agent 只做报告：它不会重启节点或重启作业，因为根因可能就在工作负载本身。硬件故障仍由 HMA 和 HyperPod 节点恢复处理，作业重启仍由 HyperPod training operator 负责。

### agent 的工作方式

该 agent 在每个集群中以单个 Pod 的形式运行在 aws-hyperpod 命名空间里，并优先调度到 CPU 节点，因此不占用 GPU 容量。它会观察以下对象：

- **节点：** agent 会报告这些变化：`NotReady` 等状态变化，或内存、磁盘、PID 压力；可分配的 GPU 或 EFA 设备减少；NVIDIA capability 标签丢失；污点被添加、修改或移除；HyperPod 标签缺失。
- **关键基础设施 Pod：** kube-system、aws-hyperpod 和 kubeflow 中的 DaemonSet Pod，以及 training operator 的 controller。agent 会报告崩溃循环、重启、容器错误以及长期处于未就绪状态的 Pod。
- **DaemonSet：** 标记为必需的 DaemonSet 缺失或没有可用 Pod，rollout 停滞，以及 Pod 仍运行在已不允许其运行的节点上。
- **训练作业：** HyperPodPyTorchJob、Kubeflow PyTorchJob（v1）和 Kubeflow TrainJob（v2）。作业失败时，agent 会记录失败原因以及该作业的 Pod 和节点。
- **NCCL 通信：** 对于主动启用的作业，读取 NCCL 内置的可靠性、可用性与可服务性（RAS）子系统，获取作业各 NCCL communicator 的状态。

agent 会在两个地方报告发现：

- **Kubernetes 事件**，挂在受影响的节点、Pod、DaemonSet 或作业上。Warning 事件表示出现问题，Normal 事件表示已经恢复。可以用 kubectl get events 和 kubectl describe 查看。
- **结构化 JSON 日志**，写入集群的 CloudWatch 日志组，在 Kubernetes 事件过期后仍保留历史。

下表列出最可能出现的事件。

| **事件原因** | **触发条件** |
| --- | --- |
| TrainingJobFailed | HyperPodPyTorchJob 或 Kubeflow 作业失败。消息中包含作业 operator 给出的失败原因。 |
| CriticalPodCrashLoop, CriticalPodRestarted | 设备插件、HMA 或其他关键 Pod 陷入崩溃循环或发生重启。 |
| NecessaryDaemonSetMissing | 你声明为必需的 DaemonSet 缺失或没有可用 Pod。 |
| NodeResourceDegraded | 节点的可分配 GPU 或 EFA 设备数量下降或消失。 |
| NodeConditionDegraded | 节点变为 NotReady，或上报内存、磁盘、PID 压力。 |
| NodeTaintAdded, NoExecuteTaintApplied | 节点被加上污点。对于 NoExecute 污点，日志会列出可能被驱逐的 Pod 和作业。 |
| DaemonSetMisscheduled | DaemonSet 的 Pod 运行在已不允许它们运行的节点上。 |
| NodeRecovered, PodRecovered, DaemonSetRecovered | 先前报告的问题已消失。 |

完整的事件列表见[文档](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-eks-resiliency.html)。

### 前提条件

你需要准备：

- 由 Amazon EKS 编排的 SageMaker HyperPod 集群。
- 对于已有集群，需要能通过 kubectl 和 Helm 访问该集群，并需要 [sagemaker-hyperpod-cli](https://github.com/aws/sagemaker-hyperpod-cli) 仓库中的 HyperPod Helm chart。
- 如果希望监控 NCCL 通信，训练容器中需要 NCCL 2.24 或更高版本。

### 安装并验证 agent

如果你的集群已经在使用 HyperPod Helm chart，请先应用该 agent 的自定义资源定义（CRD），因为 Helm 在升级时不会安装 CRD。然后开启 agent 并升级 release：

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

这次升级还会把 chart 中的其他 HyperPod 组件（例如 HMA 和设备插件）一并迁到 chart 的当前版本。想先看清会改动什么，可以在同一条命令上加 `--dry-run=server` 执行。

确认 agent 正在运行，且其健康报告已经存在：

```
kubectl get deployment \
    -n aws-hyperpod \
    hyperpod-kubernetes-resource-monitoring-agent

kubectl get hyperpodkrmaconfigs default -o yaml
```

健康报告会列出 agent 跟踪的 HyperPod 组件（例如 HMA）及其状态最后一次变化的时间：

```
status:
  components:
    - name: DaemonSet/aws-hyperpod/health-monitoring-agent
      since: "2026-11-10T16:47:57Z"
      status: Healthy
      instances: []
  lastReportTime: "2026-11-10T17:19:36Z"
```

默认情况下，HMA 是唯一被标记为必需的 DaemonSet。如果你的集群使用了 HyperPod Helm chart 里的设备插件，把它们也加进去，这样插件缺失时 agent 才会报告。同时把你的训练作业所在命名空间加进去，agent 才能把 Pod 故障关联到对应作业。每个列表都会覆盖默认值，所以务必保留默认条目。将以下内容保存为 `krma-values.yaml`：

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

### 看看 agent 会报告什么

为了看 HyperPod Kubernetes Resource Monitoring Agent 如何处理基础设施故障，我们在 aws-hyperpod 里部署了一个小型 DaemonSet，把它固定到一个节点上，并让它在启动几秒后退出。它的行为和崩溃循环的设备插件一样，但没有碰真正的插件。几秒之内，agent 就在该 Pod 和 DaemonSet 上发出了事件：

```
kubectl get events -A \
    --field-selector source=hyperpod-kubernetes-resource-monitoring-agent

NAMESPACE TYPE REASON OBJECT MESSAGE
aws-hyperpod Warning CriticalPodRestarted pod/demo-plugin-4wsqw Critical infrastructure pod container crash restarted (count: 2)
aws-hyperpod Warning CriticalPodCrashLoop pod/demo-plugin-4wsqw Critical infrastructure pod container crash in CrashLoopBackOff
aws-hyperpod Warning DaemonSetMisscheduled daemonset/demo-plugin DaemonSet has 1 misscheduled pods
```

接着，我们运行了一个双节点的 HyperPodPyTorchJob，并让其中一个 rank 在训练中途退出。agent 在该作业上发出了 TrainingJobFailed 事件：

```
NAMESPACE TYPE REASON OBJECT MESSAGE
ml-team-a Warning TrainingJobFailed hyperpodpytorchjob/llama-pretrain Training job HyperPod PyTorchJob failed:
Fault detected on training pod llama-pretrain-pod-7dc7c-nh5gb:
A training worker process has crashed: Local Rank 0 exited ...
```

它还把失败连同涉及的 Pod 和节点写入了 CloudWatch，你无需再从作业的 Pod 列表里逐个查找：

```
{"level":"warn","msg":"=== Job Failure Detected ===","component":"HyperpodPyTorchJob",
"job":"llama-pretrain","namespace":"ml-team-a","type":"HyperPod PyTorchJob",
"reason":"Fault detected on training pod llama-pretrain-pod-7dc7c-nh5gb: A training worker process has crashed ..."}
{"level":"warn","msg":"Affected Pods","component":"HyperpodPyTorchJob",
"pods":["llama-pretrain-pod-7dc7c-nh5gb","llama-pretrain-pod-7dc7c-f9dmg"]}
{"level":"warn","msg":"Affected Nodes","component":"HyperpodPyTorchJob",
"nodes":["hyperpod-i-0a1b2c3d4e5f60001","hyperpod-i-0a1b2c3d4e5f60002"]}
```

agent 把这些日志写入集群日志组 `/aws/sagemaker/Clusters/<cluster-name>/<cluster-id>` 中名为 `SageMakerClusterMonitoringAgent/<instance-group>/<instance-id>` 的日志流。它切换到其他节点时会新建日志流，因此请按日志流前缀过滤。示例查询见[文档](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-eks-resiliency.html)。

### 监控作业的 NCCL 通信

NCCL 2.24 及更高版本包含可靠性、可用性与可服务性（RAS）子系统：每个 NCCL 进程里有一个小的监听器，负责报告作业各 communicator 的状态。对于主动启用的作业，agent 每 30 秒从每个 Pod 读取一次该报告。

默认情况下，NCCL 把 RAS 监听器绑定到 Pod 内的 `localhost`，agent 无法访问。要让作业主动启用，需要改为把监听器绑定到 Pod IP。这样端口 28028 就能在 Pod 网络上访问，NVIDIA 的文档指出这会带来安全影响。开启之前，先应用一条 Kubernetes NetworkPolicy，只允许来自 agent Pod 的 TCP 28028 流量，同时仍然允许作业自身各 Pod 之间的通信。agent 的[文档](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-eks-resiliency.html)中给出了示例策略。然后在训练容器里设置 `NCCL_RAS_ADDR`：

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

要确认设置是否生效，可用 `NCCL_DEBUG=INFO` 和 `NCCL_DEBUG_SUBSYS=INIT,RAS` 打开 NCCL 调试日志。每个 rank 会打印 RAS 监听的地址：

```
[default3]:llama-pretrain-workers-6c7f5bb445-gxnsf:129:203 [3] NCCL INFO RAS client listening socket at 10.0.1.11<28028>
```

如果地址是 `::1` 或 `127.0.0.1`，说明 `NCCL_RAS_ADDR` 没有设置，agent 也就无法访问该监听器。

对每个被监控的作业，agent 会把各 Pod 的结果汇总成作业级状态：所有 Pod 都返回有效报告时为健康，只有部分返回时为降级，全都返回不了时为不健康。不健康通常意味着训练进程已经停止。

每个轮询周期结束后，agent 都会记录一条汇总。在我们用两台 ml.p5.48xlarge 实例做的一次运行中，每个周期都报告两个训练 Pod 健康，间隔 30 秒：

```
{"level":"info","timestamp":"2026-11-12T07:14:27.163Z","msg":"NCCL RAS monitoring cycle completed","component":"nccl-ras-informer-llama-pretrain","duration":4.00535305,"total_endpoints":2,"healthy":2,"failed":0,"overall_status":"healthy"}
```

agent 还会把每份 RAS 报告写入 CloudWatch，因此作业仍在运行时就能发现 communicator 的问题。在我们的测试中，我们让一个双节点作业里的某个 rank 停止调用 `all_reduce`。下一个轮询周期的报告显示该 communicator 已失去同步，并指明了落后的 rank、GPU、进程和节点：

```
Group Comms Nodes Ranks Ranks Ranks Status Errors
# in group per comm per node per comm in group
0 1 2 1 2 2 RUNNING MISMATCH

#0-0 (2958ae23ccc57a88) MISMATCH
Communicator ranks have different AllReduce operation counts
Rank 0 has launched up to operation 3078 -- GPU 0 managed by process 473 on node 10.0.1.11
Rank 1 has launched up to operation 3077 -- GPU 0 managed by process 474 on node 10.0.2.22
```

rank 1 比 rank 0 落后一次操作，所以排查应从节点 10.0.2.22 上 rank 1 的 GPU 开始。

## 在 HyperPod Slurm 集群上检测并恢复挂起作业

训练作业可能挂起却不退出。NCCL 超时、数据管道停滞或死锁，都能让作业一直占着 GPU，而 Slurm 仍显示它正在运行。这种状态会一直持续，直到有人注意到 loss 或日志不再变化。跑 Slurm 的团队常常自己写看门狗脚本和告警来捕捉这类作业，然后还得维护它们。

今天我们正式推出面向 SageMaker HyperPod Slurm 集群的挂起作业检测。它能找出这类作业、向 CloudWatch 写入事件，还可以取消挂起作业，让 Slurm 把它放回队列。你只需为每个作业设置一个指向小型规则文件的环境变量即可开启，无需改动训练脚本或容器，并且支持 PyTorch、TensorFlow、JAX 和自定义脚本。

### 挂起作业检测的工作方式

挂起作业检测以 agent 形式运行在每个节点上，默认关闭。它只监控那些把 `HYPERPOD_HANG_RULES` 环境变量设为某规则文件路径的作业。由规则文件决定 agent 如何判定挂起：

- *默认检测* 观察作业的标准输出和 GPU 活动。当输出长时间停止、GPU 空闲但仍占着显存时，它判定为挂起——这正是 rendezvous 挂起的样子：一个节点故障，其余节点在屏障处等待。当输出停止更长时间时，无论 GPU 在做什么，它也会判定为挂起。在我们的测试中，第一种情况在作业最后一次输出 15 分钟后触发。
- *自定义规则* 用你选定的正则表达式观察日志。进度规则在诸如训练步信息这样的行未在超时内出现时判定挂起；错误规则一旦出现诸如 NCCL 错误这样的行就立即判定挂起。自定义规则会取代该作业的默认检测。

|  | **默认检测** | **自定义规则** |
| --- | --- | --- |
| 开启方式 | {“enabled”: true} | 一条或多条启用的 log_pattern 规则 |
| 判定挂起的条件 | 输出停止且 GPU 空闲但仍占用显存，或输出停止更长一段时间 | 进度模式未在超时内出现，或出现错误模式 |
| 漏检情况 | GPU 一直忙碌却毫无进展的作业，例如卡在循环里的作业 | 你的模式描述不了的挂起。如果某个模式持续匹配，即使 GPU 空闲也不会判定挂起 |

agent 判定挂起时，会向 CloudWatch 写入 `HANG_DETECTED` 事件。如果规则文件把动作设为 `cancel`，agent 还会取消作业，由 Slurm 重新排队。默认动作是 `notify`，此时 agent 只写事件，作业继续运行。

挂起作业检测与 [auto-resume](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-auto-resume.html) 是两回事：后者负责重启因硬件故障而退出的作业。auto-resume 处理崩溃的作业，挂起作业检测处理仍在运行却毫无进展的作业。

在由 Amazon EKS 编排的 HyperPod 集群上，HyperPod 已经能在两种情况下检测挂起作业。[HyperPod training operator](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-eks-operator-usage.html) 会按作业规格里的规则检查每个 HyperPodPyTorchJob 的日志，作业挂起时将其重启。同一套规则还能重启吞吐量下降或 loss 突增的作业，而且不需要 Ray。对于 Ray Train 作业，[HyperPod hung job detection for Ray](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-ray-hung-job-detection.html) 默认监控每个 worker，无需改动你的代码。

### 前提条件

你需要准备：

- 由 Slurm 编排的 SageMaker HyperPod 集群。
- 2026 年 11 月 10 日或之后发布的 HyperPod Slurm AMI，其中包含挂起作业检测。该日期之后创建的集群已经具备此功能。要在不升级的前提下检查已有集群，可在集群节点上运行 `srun --help`：如果输出里列出 `--no-hang-detection`，说明该集群支持挂起作业检测；如果没有，请先[更新集群软件](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-operate-slurm-cli-command.html)。更新会替换每个实例的根卷，因此更新前请备份存放在根卷上的所有内容。
- 一个规则文件，作业中每个计算节点都能在同一路径下读取它。agent 会在每个节点上从该路径读取文件。使用 Amazon FSx for Lustre 或 Amazon Elastic File System（Amazon EFS）这类共享存储是最省事的做法。若要把规则文件放在 Amazon Simple Storage Service（Amazon S3），请把它们复制到每个节点的同一路径，例如在生命周期脚本里完成。如果你打算使用 `/opt/slurm` 这样的目录，先确认它在各节点间是共享的，而不是每个节点本地独有的。

### 开启挂起作业检测

在共享存储上创建规则文件。最小的合法文件即可开启默认检测：

```
echo '{"enabled": true}' > /fsx/my-project/rules.json
chmod 600 /fsx/my-project/rules.json
```

agent 会使用作业指向的任何规则文件，并不检查文件归谁所有。任何能编辑该文件、或在所在目录里替换它的人，都能改变所有使用该文件的作业的检测行为，甚至让 agent 取消这些作业。示例中的 `chmod 600` 让个人规则文件仅其所有者可读写。若是团队共享的文件，请用 `chmod 644`，让团队可以读取、只有维护者能编辑。两种情况下，都要让父目录仅其所有者可写，以免有人替换文件。

然后在提交作业时让它指向该规则文件：

```
#!/bin/bash
#SBATCH --job-name=llama-pretrain
#SBATCH --nodes=4
#SBATCH --export=ALL,HYPERPOD_HANG_RULES=/fsx/my-project/rules.json

srun python train.py
```

若想让多个作业共用同一个规则文件，也可以在 shell profile 或站点级 profile 脚本里设置 `HYPERPOD_HANG_RULES`。

被监控的作业启动时，输出的前几行会显示 agent 已注册该作业：

```
[Auto Resume] Info: [hang_detection] Exported stdout path for job 1: /fsx/my-project/llama-pretrain-1.out
[Auto Resume] Info: [hang_detection] Registered job step: job=1 step=0 node=ip-10-1-40-47
```

规则文件无效时同样会出现这几行，所以还要到 CloudWatch 里查一下 `CONFIG_ERROR` 事件，详见下一节。

### 添加自定义规则以跟踪训练进度

默认检测抓不住那种一直占满 GPU 却毫无进展的作业，因此我们建议至少配置一条规则来观察你的训练步或 epoch。下面的规则文件会在 45 分钟内没有任何 epoch 完成，或一旦出现 NCCL 错误时取消作业：

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

各字段含义如下：

- 为每条规则把 enabled 设为 true。规则默认关闭。
- `start_timeout_minutes` 是模式首次出现之前作业可以运行多久。把它设得比作业加载模型、编译和恢复 checkpoint 所需的时间更长。
- `timeout_minutes` 是此后模式可以持续不出现多久。把它设得比正常情况下的最大间隔更长，包括保存 checkpoint 和评估所占的时间。
- `stop_pattern` 在匹配时关闭该规则，这样训练结束后的工作不会被误报。
- `fault_on_match` 标记错误模式：匹配一次即表示作业挂起。

默认情况下，agent 读取作业的 Slurm 输出文件。要观察其他文件，可设置 `monitoring.log_file`。为减少误报，可在规则上设置 `metric_evaluation_data_points`，要求连续多次 10 秒检查都不通过，agent 才判定挂起。一个规则文件最多可包含 20 条规则，大小上限为 1 MB。

在调校超时和模式时先用 `"action": "notify"`，等事件与真实挂起吻合后再切换到 `cancel`。

### 在 CloudWatch 中查看挂起作业检测事件

HyperPod 会把检测事件从 controller 节点写入集群的 CloudWatch 日志组 `/aws/sagemaker/Clusters/<cluster-name>/<cluster-id>`，日志流为 `SageMakerHangJobDetectionEvents/<controller-instance-group>/<controller-instance-id>`。无论作业跑在哪个节点上，所有作业的事件都会进入这条日志流。要查找某个作业的事件，按作业 ID 过滤：

```
aws logs filter-log-events \
    --log-group-name /aws/sagemaker/Clusters/<cluster-name>/<cluster-id> \
    --log-stream-name-prefix SageMakerHangJobDetectionEvents/ \
    --filter-pattern '{ $.job_id = "12345" }'
```

我们在一个带两台 ml.p5.48xlarge 实例的 HyperPod Slurm 集群上测试了每种检测方式。第一个测试作业分配了 GPU 显存后便停止产生输出，默认检测在它最后一次输出 15 分钟后将其标记：

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

`layer` 字段说明是哪一种方式触发：默认检测为 `signal_evaluator`，自定义规则为 `pattern_evaluator`。在第二次测试中，一条超时为 2 分钟的进度规则在作业最后一步之后 2 分钟触发。第三次测试中，错误规则在作业打印出 NCCL 错误行约 1 秒后触发。由于该规则文件使用 cancel，agent 还写了一条 `HANG_ACTION_TAKEN` 事件，记录 Slurm 采取的动作（我们省略了 time、level 和 msg 字段）：

```
{"event_type":"HANG_DETECTED","job_id":"3","step_id":"0","node":"ip-10-1-40-47","evidence":"rule \"nccl_error\": fault pattern matched immediately","layer":"pattern_evaluator","detected_at":"2026-11-12T16:34:41.870908329Z","job_action":"cancel","config_source":"per_job_env_var"}
{"event_type":"HANG_ACTION_TAKEN","job_id":"3","action":"requeue","node":"ip-10-1-40-47","instance_id":"i-0a1b2c3d4e5f60001"}
```

Slurm 把作业放回队列，重新排队的运行在约 2.5 分钟后启动。`sacct` 显示两次运行：

```
$ sacct --duplicates -X -j 3 --format=JobID,State,Restarts,Start,End
JobID State Restarts Start End
----------- --------- ------- ------------------- -------------------
3 REQUEUED 0 2026-11-12T16:34:25 2026-11-12T16:34:41
3 COMPLETED 1 2026-11-12T16:37:10 2026-11-12T16:37:26
```

Slurm 重新排队作业的次数受集群 `MaxBatchRequeue` 上限约束，我们集群上是 5 次。用 `#SBATCH --no-requeue` 提交的作业会报告 `"action": "cancel"`，并保持取消状态。使用 `notify` 时不会出现 `HANG_ACTION_TAKEN` 事件，agent 会在 `HANG_DETECTED` 之后追加一条记录，内容为 `Hang notification sent, no automatic action taken`。

如果规则文件缺失或无效，agent 不会监控该作业，而是写入一条 `CONFIG_ERROR` 事件。下面是规则文件存在 JSON 语法错误时的事件：

```
{"event_type":"CONFIG_ERROR","job_id":"5","node":"ip-10-1-40-47","config_path":"/fsx/my-project/rules.json","error":"config file found but failed to load: load failed: invalid JSON in config file /fsx/my-project/rules.json: unexpected end of JSON input","message":"Hang detection rules file is invalid and will not be applied. Please fix the rules file and resubmit your job."}
```

该作业在没有任何监控的情况下跑完了，`sbatch`、`squeue` 和作业输出里都没有任何提示。新规则文件先拿短作业试跑、确认没有出现这条事件，再用于生产作业。

使用 notify 时，作业会一直运行，直到有人根据事件采取行动。要收到告警，可为 `HANG_DETECTED` 事件创建 CloudWatch 指标筛选器，并创建一个向 Amazon Simple Notification Service（Amazon SNS）主题发送通知的告警：

```
aws logs put-metric-filter \
    --log-group-name /aws/sagemaker/Clusters/<cluster-name>/<cluster-id> \
    --filter-name hung-jobs \
    --filter-pattern '{ $.event_type = "HANG_DETECTED" }' \
    --metric-transformations \
    metricName=HungJobsDetected,metricNamespace=HyperPod/HungJobs,metricValue=1
```

### 关闭挂起作业检测

要让某个本来会继承 `HYPERPOD_HANG_RULES` 的作业关闭检测，可在 `srun` 上加 `--no-hang-detection`，或者加在 `sbatch` 上以覆盖该作业的每个 step。要让所有使用某规则文件的作业都关闭检测，在文件里设置 `"enabled": false`。正在运行的作业保持当前设置，改动只对之后提交的作业生效。

```
srun --no-hang-detection python train.py
```

## 结语

节点健康是可靠分布式训练的基础，但它无法完整反映工作负载的健康状况。`MultiNodeTrainingValidation` 能发现那些通过了硬件诊断、却产出无效训练结果的实例。HyperPod Kubernetes Resource Monitoring Agent 把 Kubernetes 基础设施故障与相关的作业、Pod 和节点关联起来。挂起作业检测识别出停止推进后仍在运行的 Slurm 作业，并能自动把它们送回队列。

这些能力合在一起，能帮你更早发现故障、缩短排查时间，并通过减少花在无法有效推进的工作负载上的 GPU 时间来提升有效吞吐量。扩容或重新验证容量时使用 `MultiNodeTrainingValidation`；在受支持的 Amazon EKS 集群上持续运行 HyperPod Kubernetes Resource Monitoring Agent；挂起作业检测先以 notify 模式起步，之后再切换到自动取消。入门可参阅 [Amazon EKS 的 SageMaker HyperPod 弹性文档](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-eks-resiliency.html) 和 [Slurm 的挂起作业检测文档](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-resiliency-slurm-hang-detection.html)。想了解更多，请访问 [Amazon SageMaker HyperPod 产品页](https://aws.amazon.com/sagemaker-ai/hyperpod/)。

*作者感谢 Hengyu Lou、Vishal Shahane、Ziyao Huang 和 Haard Mehta 对本文及相关功能的贡献。*

## 关于作者
