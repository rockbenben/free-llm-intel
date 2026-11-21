---
vendor: aws_bedrock
title: Amazon SageMaker HyperPod Global Inference Gateway 简介：一个端点覆盖多个区域与集群
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/introducing-amazon-sagemaker-hyperpod-global-inference-gateway-one-endpoint-across-regions-and-clusters
date: 2026-11-20
lang: zh
captured: 2026-11-21
extractor: readability-v1
translator: agent
status: translated
body_sha: 0fcf9a75c99d
---

## [人工智能](https://aws.amazon.com/blogs/machine-learning/)

# 推出 Amazon SageMaker HyperPod 全局推理网关：一个端点覆盖多个区域与集群

流量高峰时，请求可能堵在已经饱和的 HyperPod 集群队列里，而另一个集群上的 GPU——有时在另一个 AWS 区域——却闲着。那部分容量你已经付过钱，请求却到不了那里。

在[推出 Amazon SageMaker HyperPod 推理网关](https://aws.amazon.com/blogs/machine-learning/introducing-amazon-sagemaker-hyperpod-inference-gateway/)一文中，我们介绍了推理网关如何为每个 Amazon SageMaker HyperPod 集群提供一个统一的、感知 GPU 的端点。它读取键值（KV）缓存利用率和队列深度等实时信号，把每个请求放到最合适的 pod 上。这解决了单个集群内部的路由，却没有解决跨集群的路由。

今天，SageMaker HyperPod 推出全局推理网关。它是一个由 SageMaker 管理的网关，在你注册的每个集群之间路由，无论这些集群在同一个区域还是跨多个区域。网关负责挑选集群，并经由 AWS 骨干网承载请求，自动故障转移，通过 AWS Signature Version 4（SigV4）和 AWS Identity and Access Management（IAM）完成身份验证。在每个集群内部，推理网关照旧挑选 pod，行为不变。全局推理网关就是第 1 部分所述架构中的第二层。

## 挑战：容量分散在多个集群和区域

模型越来越大，服务它们所需的 GPU 容量也越来越难找。为了凑够容量，你只能把它摊到更多集群、更多区域。

设想一个团队，在两个区域的五个 HyperPod 集群上服务四个模型。没有推理网关时，客户端要跟踪 20 个端点：每个集群上每个模型各一个。推理网关把它减到五个，每个集群一个。但每个客户端仍然得自己挑集群。

这个选择是有代价的：

- **负载不均。** 高峰期请求在一个区域排队，另一个区域的 GPU 却闲着。
- **人工故障转移。** 集群故障时，由工程师改配置把流量挪走。
- **自建管道。** 要让流量跨区域，就得自己搭建并维护负载均衡器、DNS 和跨区域网络。

这个团队需要的，是一个能把每个请求送到最合适集群、并在集群故障时自行把流量挪走的端点。

## 主要优势

全局推理网关让你把已有的 GPU 容量用得更充分，运维反而更少。

- **让闲置 GPU 干起活来。** 高峰期，请求溢出到同区域或另一区域还有余量的集群，而不是在饱和集群上排队。
- **自动故障转移。** 集群故障时，网关把它的流量切到次优集群。客户端什么都不用改。
- **所有场景共用一个端点。** 客户端只调用一个由 SageMaker 管理的端点，不必再按集群或按模型去跟踪一堆端点。
- **省掉自建网络。** 不用搭建或维护负载均衡器、DNS 和跨区域网络。
- **默认私密。** 每个请求都用 SigV4 和 IAM 做身份验证，且只经 AWS PrivateLink 抵达你的集群。

## 客户反馈

> “在 Bagelcode，我们在 AWS 上运行自己的 LLM 推理服务，帮助公司各团队——包括我们的游戏团队——用 AI 改进工作方式。在 beta 测试中，Amazon SageMaker HyperPod 的全局推理网关通过单一端点跨两个 AWS 区域路由请求，并在其中一个集群无法继续服务该模型时保持服务不中断。这让我们这支小型平台团队获得了跨区域故障转移能力，而不必自建或维护自己的路由层。”

— Jinhyung Park，Bagelcode 副总裁（AI 平台）

## 工作原理

搭建网关要做两个决定：开放哪些集群参与路由，以及把其中哪些集群归到同一个网关后面。

- **发布集群。** 每个集群做一次。你在集群现有的 `InferenceGatewayConfig` 里打开 `spec.globalRouting` 块，HyperPod Inference 控制器随后就从你自己的账户私有地发布这个集群。
- **创建网关。** 每个网关做一次。你调用 `CreateGlobalInferenceGateway`，传入要跨其路由的集群，SageMaker 返回一个端点。

集群只有发布之后才可达。发布集群时，控制器会在该集群的推理网关前面创建一个 Network Load Balancer，在其上发布一个虚拟私有云（VPC）端点服务，并把监听器证书上传到你的 TLS 存储桶。这些资源都在你的账户里。如果你把一个尚未发布的集群写进网关，调用会失败，并给出提示说明要修什么。

### 请求如何流转

图 1 展示了每个请求的路径：（1）你的客户端用 SigV4 给请求签名，发往网关的区域端点。（2）网关验证调用方身份，并挑选最合适的集群。（3）AWS PrivateLink 把请求送到该集群，无论同区域还是跨区域；（4）该集群的推理网关再把它路由到某个模型 pod，和现在一样。

![图 1：全局推理网关架构](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/20/ML-22376-1-1.png)

图 1：全局推理网关在一个区域端点接收每个请求，经 AWS PrivateLink 转发到最合适的 HyperPod 集群，该集群的推理网关再把它路由到模型 pod。每个集群都会把自己的负载回传给网关。

### AWS 负责运营哪些部分

哪些集群发布、哪些归到同一个网关后面、路由权重怎么设，由你决定。其余由 AWS 运营：

- **路由机群。** SageMaker 负责预置和运营这支机群，由它终止 TLS、验证调用方、给集群打分并转发每个请求。
- **私有连接。** SageMaker 为每个集群创建一个私有端点，流量走 AWS 骨干网，区域内和跨区域都是如此。
- **证书与校验。** 服务用一个由你创建的执行角色读取每个集群的 VPC 端点服务名称、证书和区域，你不需要手工抄写。在路由流量之前，它会先做校验。
- **健康检查与故障转移。** 网关对每个集群做健康检查，并自动把流量从故障集群挪走。细节见「操作网关」一节。
- **身份验证与速率限制。** 网关检查 SigV4 签名、IAM 权限和速率限制，不合格的请求在任何集群看到它之前就被拒绝。

在每个集群上，一个由服务管理、拥有独立 IAM 角色的指标发布器会把该集群的负载发给网关。

## 网关如何挑选集群

对每个请求，网关根据四项信号给每个健康集群打分，然后把请求发给得分最高的那个。各集群的指标发布器提供负载信号。

每项信号占多大权重由你通过路由权重控制。每个权重是 0.0 到 1.0 之间的值，设为 0 就关闭该信号。若设置权重，必须四项全设，且加起来等于 1.0。若不设置，则沿用下表中的默认值。

| **权重** | **评的是什么** | **默认值** |
| --- | --- | --- |
| `KVHeadroom` | 集群上可用的 KV 缓存与 GPU 内存 | 0.20 |
| `QueueDepth` | 集群积压的程度 | 0.25 |
| `RegionProximity` | 集群与网关所在区域之间的距离 | 0.40 |
| `ErrorRate` | 集群上近期的失败请求 | 0.15 |

默认值偏向靠近网关所在区域的集群，同时仍会把流量引向有余量的集群、带离正在故障的集群。如果你的工作负载更看重韧性而非邻近程度，就调高 `ErrorRate`、调低 `RegionProximity`。例如下面这段路由配置把近期错误的权重设到 0.7：

```
{"Weights": {"KVHeadroom": 0.1, "QueueDepth": 0.1, "RegionProximity": 0.1, "ErrorRate": 0.7}}
```

权重通过 `CreateGlobalInferenceGateway` 的 `Routing` 参数传入，之后可以用 `UpdateGlobalInferenceGateway` 修改。

## 选择你的起点

走哪条路取决于你现在跑的是什么。如果只从一个集群提供服务，就继续用该集群的推理网关端点；等加上第二个集群，再迁到全局推理网关。

| **起点** | **你要做什么** | **结果** |
| --- | --- | --- |
| 每个集群都跑着推理网关，例如 us-east-1 和 us-west-2 的五个集群上跑四个模型 | 更新附加组件，逐个发布集群，创建网关 | 所有集群共用一个端点。在客户端迁移期间，按集群的端点继续服务。 |
| HyperPod Inference 附加组件在运行，但推理网关是关的 | 通过一次附加组件更新和每个集群一份 `InferenceGatewayConfig` 打开推理网关，为每个模型加一个调度器，然后按第一行操作 | 按模型的端点合并为一个 |
| 两个区域都有 GPU 容量，但还没搭 HyperPod Inference | 在每个区域用 HyperPod Inference 附加组件创建 HyperPod 集群，部署模型，打开推理网关，然后按第一行操作 | 从第一天起就是一个端点，路由可精细调整，某个区域出问题也能继续服务 |

## 开始使用

要搭建全局推理网关，你需要准备每个集群、创建一个执行角色，然后调用 `CreateGlobalInferenceGateway`。之后把经 SigV4 签名、兼容 OpenAI 的请求发到网关端点。包括 IAM 角色和策略在内的分步说明，见 [AWS 文档](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-model-deployment-global-inference-gateway.html)。

## 安全与访问

发往网关的每个请求都用 SigV4 签名、经 IAM 授权。调用方需要有调用网关的权限，流式调用另有一个操作：

```
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "sagemaker:InvokeGlobalInferenceGateway",
      "sagemaker:InvokeGlobalInferenceGatewayWithResponseStream"
    ],
    "Resource": "arn:aws:sagemaker:<region>:<account-id>:global-inference-gateway/<gateway-id>"
  }]
}
```

把这份策略附加到每个发请求的 IAM 身份上。要允许账户内所有网关，资源写 `global-inference-gateway/*`。

执行角色遵循最小权限：它只能描述你列出的集群，只能访问这些集群的 Amazon Elastic Kubernetes Service（Amazon EKS）API，只能读取你 TLS 存储桶中 `gig/` 前缀下、标记为由 HyperPod Inference 创建的路由证书。

**身份 token。** 如果你的集群会校验 JSON Web Tokens（JWT），就用 `--customer-identity-token` 传入 token（即 `X-Amzn-SageMaker-Customer-Identity-Token` 标头），不要加 `Bearer` 前缀。token 在 SigV4 签名内传输，因此未签名的 token 会被拒绝并返回 403，重复的 token 会被拒绝并返回 400。要么在每个提供模型服务的集群上都打开 JWT 校验，要么全都不开，免得请求在一个集群成功、在另一个集群失败。

如图 1 所示，请求只经 AWS PrivateLink 抵达你的集群。网关不记录也不存储 prompt 或补全内容。

## 操作网关

以下是配置网关的步骤。

### 添加集群

按文档说明准备好新集群，并在其上创建执行角色的 EKS 访问条目。同时把新集群加入执行角色权限策略的 `Resource` 列表。然后在网关所在区域调用 `AddInferenceGateway`，即使新集群在另一个区域：

```
aws sagemaker add-inference-gateway \
  --identifier <gateway-name> \
  --region <region> \
  --cluster-arn arn:aws:sagemaker:<region-3>:<account-id>:cluster/<cluster-id-3> \
  --name <gateway-config-name-3> \
  --namespace inference-gateway
```

网关会校验该集群，健康之后开始向它路由。端点、其他集群和客户端都不受影响。

### 分离集群

在网关所在区域调用 `RemoveInferenceGateway`：

```
aws sagemaker remove-inference-gateway \
  --identifier <gateway-name> \
  --region <region> \
  --cluster-arn arn:aws:sagemaker:<region-3>:<account-id>:cluster/<cluster-id-3> \
  --name <gateway-config-name-3> \
  --namespace inference-gateway
```

网关停止向该集群发送新请求，让在途请求跑完，并删除私有端点。一个网关始终至少保留一个集群。要彻底撤出该集群，就在它的 `InferenceGatewayConfig` 里设 `globalRouting.enabled: false` 并重新应用。

### 删除网关

调用 `DeleteGlobalInferenceGateway`：

```
aws sagemaker delete-global-inference-gateway \
  --identifier <gateway-name> --region <region>
```

网关端点停止服务，按集群的端点继续服务。网关删除后，用 `globalRouting.enabled: false` 逐个撤出集群，再删掉执行角色以及你为全局路由添加的 IAM 权限。

下表汇总了常见事件和变更对流量的影响。

| **事件** | **会发生什么** | **你要做什么** |
| --- | --- | --- |
| 网关创建失败 | 网关进入 `FAILED` 状态，`FailureReason` 说明失败原因，例如证书名称不匹配 | 修复原因。要查看各集群状态，调用 `ListInferenceGateways`。 |
| 集群故障 | 流量切到次优集群，集群恢复后逐步回流。失败的请求会在另一个集群上重试一次，除非它已经开始流式传输。如果没有健康集群，网关返回 503。 | 无需操作。客户端什么都不用改。 |
| 更改路由权重 | 新请求使用新权重，在途请求按旧权重跑完。不会重新预置任何东西。 | 调用 `UpdateGlobalInferenceGateway` |
| 添加集群 | 集群健康后开始路由。其他都不变。 | 见「添加集群」 |
| 分离集群 | 新请求停止，在途请求跑完 | 见「分离集群」 |
| 删除网关 | 网关端点停止服务，按集群的端点继续服务 | 见「删除网关」 |

如需排障帮助，请参阅[故障排除指南](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-model-deployment-ts-global-inference-gateway.html)。

## 最佳实践与注意事项

- **发布之前先规划分组。** 想清楚哪些集群放在哪个网关后面，凡是应当共享某个模型流量的集群，都用同一个 `modelName`。如果希望高峰流量跨区域溢出，就要给两个区域的集群都留出余量。
- **只发布你加进网关的集群。** 已发布但不在任何网关里的集群收不到流量，可它的 Network Load Balancer 照样运行、照样计费。
- **覆盖每个模型。** `InferenceGatewayConfig` 里的每个调度器把模型名称映射到服务它的 pod。不在任何调度器中的模型无法经网关访问，请求它会返回 404。
- **附加组件配置要保持完整。** 用 `--resolve-conflicts OVERWRITE` 时，一份不完整的配置可能把你的负载均衡器或 TLS 设置重置掉。每次都要从当前配置出发。
- **每条** `kubectl` **命令都必须传** `--context`。 你要跨多个集群操作，务必确保每条命令都打在你想要的那个集群上。
- **需要时把工作负载留在一个区域内。** 建一个只包含该区域集群的网关。

## 结论

本文介绍了 Amazon SageMaker HyperPod 全局推理网关：一个由 SageMaker 管理的端点，横跨你的 HyperPod 集群，可以是一个区域，也可以是多个。网关依据 KV 缓存余量、队列深度、区域邻近程度和错误率挑选集群，并在客户端无需任何改动的情况下把流量从故障集群挪走。

全局推理网关已在 13 个 AWS 区域可用：US East (N. Virginia)、US East (Ohio)、US West (N. California)、US West (Oregon)、South America (São Paulo)、Europe (Frankfurt)、Europe (Ireland)、Europe (London)、Europe (Stockholm)、Asia Pacific (Tokyo)、Asia Pacific (Mumbai)、Asia Pacific (Singapore) 和 Asia Pacific (Sydney)。

开始使用，请参阅 [AWS 文档](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-model-deployment-global-inference-gateway.html)。

## 关于作者
