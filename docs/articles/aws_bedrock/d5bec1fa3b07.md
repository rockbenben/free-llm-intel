---
vendor: aws_bedrock
title: Amazon SageMaker HyperPod Global Inference Gateway 简介：跨区域和集群的一个终端节点
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/introducing-amazon-sagemaker-hyperpod-global-inference-gateway-one-endpoint-across-regions-and-clusters
date: 2026-11-20
lang: zh
captured: 2026-11-21
extractor: readability-v1
translator: llm
status: translated
body_sha: 2e2d89da63a6
---

## [人工智能](https://aws.amazon.com/blogs/machine-learning/)

# 推出 Amazon SageMaker HyperPod 全局推理网关：跨区域和集群的单一端点

在流量高峰期间，请求可能积压在已饱和的 HyperPod 集群队列中，而另一个集群（有时位于另一个 AWS 区域）上的 GPU 却闲置。你已经为那部分容量付费，但你的请求无法到达它。

在[推出 Amazon SageMaker HyperPod 推理网关](https://aws.amazon.com/blogs/machine-learning/introducing-amazon-sagemaker-hyperpod-inference-gateway/)一文中，我们展示了推理网关如何为每个 Amazon SageMaker HyperPod 集群提供一个单一的、GPU 感知的端点。它会读取键值（KV）缓存利用率和队列深度等实时信号，将每个请求放置到最合适的 pod 上。这解决了单个集群内的路由问题，但没有解决跨集群的路由问题。

今天，SageMaker HyperPod 推出全局推理网关。它是一个由 SageMaker 管理的网关，可跨你注册的每个集群进行路由，无论这些集群位于一个区域还是跨多个区域。该网关选择集群，并通过 AWS 骨干网承载请求，借助 AWS Signature Version 4（SigV4）和 AWS Identity and Access Management（IAM）实现自动故障转移和身份验证。在每个集群内部，推理网关仍像以前一样继续选择 pod。全局推理网关是我们在第 1 部分中描述的架构的第二层。

## 挑战：容量分散在多个集群和区域

模型正变得越来越大，而用于服务它们的 GPU 容量也越来越难获得。为了获得足够容量，你将其分散到更多集群和更多区域。

设想一个团队在两个区域的五个 HyperPod 集群上服务四个模型。如果没有推理网关，客户端需要跟踪 20 个端点：每个集群上的每个模型各一个。推理网关将其减少到五个，每个集群一个。但每个客户端仍然需要自己选择集群。

这种选择会带来成本：

- **负载不均。** 在高峰期，请求在一个区域排队，而另一个区域的 GPU 却闲置。
- **手动故障转移。** 当集群发生故障时，工程师需要更改配置以将流量移走。
- **自定义基础设施。** 跨区域分散流量意味着你需要自行构建和维护负载均衡器、DNS 和跨区域网络。

该团队需要一个端点，将每个请求发送到最合适的集群，并在集群发生故障时自行将流量移走。

## 主要优势

全局推理网关帮助你更充分地利用已有的 GPU 容量，同时减少运维工作。

- **让闲置 GPU 投入工作。** 在高峰期，请求会溢出到同一区域或另一个区域中有可用容量的集群，而不是在已饱和的集群上排队。
- **自动故障转移。** 当集群发生故障时，网关将其流量转移到次优集群。客户端无需做任何更改。
- **所有场景使用一个端点。** 客户端调用一个由 SageMaker 管理的端点，而不是跟踪每个集群或每个模型一个端点。
- **无需自定义网络。** 你不需要构建或维护负载均衡器、DNS 或跨区域网络。
- **默认保持私有。** 每个请求都使用 SigV4 和 IAM 进行身份验证，并且仅通过 AWS PrivateLink 到达你的集群。

## 客户反馈

> “在 Bagelcode，我们在 AWS 上运行自己的 LLM 推理服务，帮助公司内各团队（包括我们的游戏团队）利用 AI 改进工作方式。在我们的 beta 测试中，Amazon SageMaker HyperPod 的全局推理网关通过单一端点跨两个 AWS 区域路由请求，并在一个集群无法再服务该模型时继续服务这些请求。这让我们小型平台团队获得了跨区域故障转移能力，而无需构建或维护自己的路由层。”

— Jinhyung Park，Bagelcode 副总裁（AI 平台）

## 工作原理

设置网关需要做两个决定：开放哪些集群用于路由，以及将其中哪些集群归组到一个网关之后。

- **发布集群。** 每个集群执行一次。你在集群现有的 `InferenceGatewayConfig` 中开启 `spec.globalRouting` 块。随后，HyperPod Inference 控制器从你自己的账户中私有地发布该集群。
- **创建网关。** 每个网关执行一次。你调用 `CreateGlobalInferenceGateway` 并传入要跨其路由的集群，SageMaker 返回一个端点。

集群只有在发布后才可访问。发布集群时，控制器会在集群的推理网关前创建一个 Network Load Balancer，在其上发布一个虚拟私有云（VPC）端点服务，并将监听器证书上传到你的 TLS 存储桶。这些资源位于你的账户中。如果你在发布集群之前将其列在网关中，调用会失败并给出提示，告诉你需要修复什么。

### 请求如何流转

图 1 展示了每个请求的路径：（1）你的客户端使用 SigV4 对请求签名，并将其发送到网关的区域端点。（2）网关对调用方进行身份验证并选择最佳集群。（3）AWS PrivateLink 将请求承载到该集群，无论在同一区域还是另一个区域；（4）该集群的推理网关将请求路由到模型 pod，与当前行为一致。

![图 1：全局推理网关架构](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/11/20/ML-22376-1-1.png)

图 1：全局推理网关在一个区域端点接收每个请求，并通过 AWS PrivateLink 将其转发到最佳 HyperPod 集群，该集群的推理网关再将其路由到模型 pod。每个集群都会将其负载发布回网关。

### AWS 负责运营什么

你决定发布哪些集群、将哪些集群归组到一个网关之后，以及如何设置路由权重。其余由 AWS 运营：

- **路由服务集群组。** SageMaker 预置并运营该集群组，它负责终止 TLS、对调用方进行身份验证、为集群评分并转发每个请求。
- **私有连接。** SageMaker 为每个集群创建一个私有端点，并在 AWS 骨干网上承载流量，包括区域内和跨区域。
- **证书和验证。** 使用你创建的执行角色，服务会读取每个集群的 VPC 端点服务名称、证书和区域，因此你无需手动复制它们。在路由流量之前，它会检查这些信息。
- **健康和故障转移。** 网关会对每个集群进行健康检查，并自动将流量从故障集群移走。有关详细信息，请参阅操作网关部分。
- **身份验证和速率限制。** 网关会检查 SigV4 签名、IAM 权限和速率限制，并在任何集群看到请求之前拒绝不通过的请求。

在每个集群上，一个由服务管理、拥有自己的 IAM 角色的指标发布器会将集群的负载发送到网关。

## 网关如何选择集群

对于每个请求，网关根据四个信号为每个健康集群评分，并将请求发送到评分最高的集群。每个集群的指标发布器提供负载信号。

你可以通过路由权重控制每个信号的影响程度。每个权重是 0.0 到 1.0 之间的值，权重为 0 会关闭该信号。如果设置权重，就必须设置全部四个，并且它们必须加起来等于 1.0。如果省略，则适用下表中的默认值。

| **权重** | **评分依据** | **默认值** |
| --- | --- | --- |
| `KVHeadroom` | 集群上可用的 KV 缓存和 GPU 内存 | 0.20 |
| `QueueDepth` | 集群的积压程度 | 0.25 |
| `RegionProximity` | 集群与网关所在区域之间的距离 | 0.40 |
| `ErrorRate` | 集群上最近的失败请求 | 0.15 |

默认权重偏向靠近网关区域的集群，同时仍会将流量导向有可用容量的集群，并远离正在发生故障的集群。如果你的工作负载更看重韧性而非邻近性，请提高 `ErrorRate` 并降低 `RegionProximity`。例如，以下路由配置块将近期错误的权重设为 0.7：

```
{"Weights": {"KVHeadroom": 0.1, "QueueDepth": 0.1, "RegionProximity": 0.1, "ErrorRate": 0.7}}
```

你在 `CreateGlobalInferenceGateway` 的 `Routing` 参数中传入权重，之后可以通过 `UpdateGlobalInferenceGateway` 更改它们。

## 选择你的起点

你的路径取决于你当前运行的内容。如果你从单个集群提供服务，请继续使用该集群的推理网关端点。当你添加第二个集群时，再迁移到全局推理网关。

| **起点** | **你要做什么** | **结果** |
| --- | --- | --- |
| 每个集群上都运行推理网关，例如在 us-east-1 和 us-west-2 的五个集群上运行四个模型 | 更新附加组件，发布每个集群，并创建网关 | 所有集群使用一个端点。在你迁移客户端期间，按集群的端点会继续提供服务。 |
| HyperPod Inference 附加组件在推理网关关闭的情况下运行 | 通过一次附加组件更新和每个集群一个 `InferenceGatewayConfig` 来开启推理网关，为每个模型添加一个调度器，然后按照第一行的步骤操作 | 按模型的端点合并为一个 |
| 两个区域都有 GPU 容量，但尚未设置 HyperPod Inference | 在每个区域使用 HyperPod Inference 附加组件创建 HyperPod 集群，部署你的模型，开启推理网关，然后按照第一行的步骤操作 | 从第一天起就有一个端点，其流量路由可以微调，并且如果某个区域出现问题仍能继续服务 |

## 开始使用

要设置全局推理网关，你需要准备每个集群、创建执行角色，并调用 `CreateGlobalInferenceGateway`。然后向网关端点发送使用 SigV4 签名的 OpenAI 兼容请求。有关分步说明（包括 IAM 角色和策略），请参阅 [AWS 文档](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-model-deployment-global-inference-gateway.html)。

## 安全与访问

对网关的每个请求都使用 SigV4 签名并通过 IAM 授权。调用方需要拥有调用网关的权限，流式传输有自己的操作：

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

将此策略附加到每个发送请求的 IAM 身份上。要允许账户中的每个网关，请使用 `global-inference-gateway/*` 作为资源。

执行角色遵循最小权限。它只能描述你列出的集群，只能访问这些集群的 Amazon Elastic Kubernetes Service（Amazon EKS）API，并且只能读取你 TLS 存储桶中 `gig/` 前缀下、标记为由 HyperPod Inference 创建的路由证书。

**身份令牌。** 如果你的集群检查 JSON Web Tokens（JWT），请使用 `--customer-identity-token`（即 `X-Amzn-SageMaker-Customer-Identity-Token` 标头）传入 token，不带 `Bearer` 前缀。该 token 位于 SigV4 签名内传输，因此未签名的 token 会被拒绝并返回 403，重复的 token 会被拒绝并返回 400。在每一个提供模型服务的集群上开启 JWT 检查，或者全部都不开启，以免请求在一个集群上成功而在另一个集群上失败。

如图 1 所示，请求仅通过 AWS PrivateLink 到达你的集群。网关不会记录或存储提示词或补全内容。

## 操作网关

以下是配置网关的步骤。

### 添加集群

按照文档所述，准备新集群并在其上创建执行角色的 EKS 访问条目。还要将新集群添加到执行角色权限策略的 `Resource` 列表中。然后在网关所在区域调用 `AddInferenceGateway`，即使新集群位于另一个区域：

```
aws sagemaker add-inference-gateway \
  --identifier <gateway-name> \
  --region <region> \
  --cluster-arn arn:aws:sagemaker:<region-3>:<account-id>:cluster/<cluster-id-3> \
  --name <gateway-config-name-3> \
  --namespace inference-gateway
```

网关会验证集群，并在集群健康后开始向其路由。端点、其他集群和客户端不受影响。

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

网关停止向该集群发送新请求，让进行中的请求完成，并删除私有端点。一个网关始终至少保留一个集群。要完全撤回该集群，请在其 `InferenceGatewayConfig` 中设置 `globalRouting.enabled: false` 并重新应用。

### 删除网关

调用 `DeleteGlobalInferenceGateway`：

```
aws sagemaker delete-global-inference-gateway \
  --identifier <gateway-name> --region <region>
```

网关端点停止服务，而按集群的端点继续服务。删除网关后，使用 `globalRouting.enabled: false` 撤回每个集群，然后删除执行角色以及你为全局路由添加的 IAM 权限。

下表总结了常见事件和变更如何影响流量。

| **事件** | **会发生什么** | **你要做什么** |
| --- | --- | --- |
| 网关创建失败 | 网关进入 `FAILED` 状态，`FailureReason` 会说明失败原因，例如证书名称不匹配 | 修复原因。要查看每个集群的状态，请调用 `ListInferenceGateways`。 |
| 集群发生故障 | 流量转移到次优集群，集群恢复后会逐步回归。失败的请求会在另一个集群上重试一次，除非它已经开始流式传输。如果没有剩余的健康集群，网关会返回 503。 | 无需操作。客户端不做任何更改。 |
| 更改路由权重 | 新请求使用新权重，进行中的请求按旧权重完成。不会重新预置任何资源。 | 调用 `UpdateGlobalInferenceGateway` |
| 添加集群 | 集群健康后开始路由。其他内容不变。 | 参见添加集群 |
| 分离集群 | 新请求停止，进行中的请求完成 | 参见分离集群 |
| 删除网关 | 网关端点停止服务，而按集群的端点继续服务 | 参见删除网关 |

如需任何故障排除帮助，请参阅[故障排除指南](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-model-deployment-ts-global-inference-gateway.html)。

## 最佳实践和注意事项

- **发布前规划好分组。** 决定哪些集群位于每个网关之后，并在每个要共享某个模型流量的集群上使用相同的 `modelName`。如果你希望高峰流量跨区域溢出，请为两个区域中的集群留出余量。
- **只发布你添加到网关的集群。** 已发布但不在任何网关中的集群不会收到流量，但其 Network Load Balancer 仍会运行并计费。
- **覆盖每个模型。** `InferenceGatewayConfig` 中的每个调度器都会将模型名称映射到为其提供服务的 pod。未出现在任何调度器中的模型无法通过网关访问，对其的请求会返回 404 错误。
- **保持附加组件配置完整。** 使用 `--resolve-conflicts OVERWRITE` 时，不完整的配置可能会重置你的负载均衡器或 TLS 设置。每次都应从当前配置开始。
- **在每条 `kubectl` 命令中传入 `--context`。** 你会跨多个集群工作，因此请确保每条命令都针对你想要操作的集群运行。
- **需要时，将工作负载保留在一个区域内。** 创建一个仅包含该区域内集群的网关。

## 结论

在本文中，我们介绍了 Amazon SageMaker HyperPod 全局推理网关：一个由 SageMaker 管理的端点，跨你的 HyperPod 集群，可位于一个或多个区域。网关根据 KV 缓存余量、队列深度、区域邻近性和错误率选择集群，并在客户端无需更改的情况下将流量从故障集群移走。

全局推理网关在 13 个 AWS 区域可用：US East (N. Virginia)、US East (Ohio)、US West (N. California)、US West (Oregon)、South America (São Paulo)、Europe (Frankfurt)、Europe (Ireland)、Europe (London)、Europe (Stockholm)、Asia Pacific (Tokyo)、Asia Pacific (Mumbai)、Asia Pacific (Singapore) 以及 Asia Pacific (Sydney)。

要开始使用，请参阅 [AWS 文档](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-model-deployment-global-inference-gateway.html)。

## 关于作者
