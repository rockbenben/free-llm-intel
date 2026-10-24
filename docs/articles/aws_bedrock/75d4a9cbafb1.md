---
vendor: aws_bedrock
title: 使用 AWS CDK 协调 SageMaker AI 端点自动扩展
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/orchestrating-sagemaker-ai-endpoint-auto-scaling-with-aws-cdk
date: 2026-10-23
lang: zh
captured: 2026-10-24
extractor: readability-v1
translator: mt
status: translated
body_sha: 1ac32ce219f6
---

## [人工智能](https://aws.amazon.com/blogs/machine-learning/)

# 使用 AWS CDK 编排 SageMaker AI 端点自动扩展

更新 Amazon Sagemaker AI 实时终端节点配置（更改实例类型、实例计数或环境变量）会导致通过 AWS CloudFormation 或 AWS 云开发工具包 (AWS CDK) 进行的部署失败。 SageMaker AI 要求您在更新终端节点之前取消注册可扩展目标，但取消注册后，CloudFormation 无法跟踪 AWS Application Auto Scaling 资源。

在本文中，我们将向您展示如何将可重用 CDK 构造与 AWS CloudFormation 自定义资源结合使用，以在终端节点更新期间自动协调取消注册和注册自动扩展。您可以在单个部署中更新端点配置和自动扩展参数，而无需手动干预。

## 为什么会出现这个问题

当您使用本机 CloudFormation 自动扩展资源部署 SageMaker AI 端点，然后更改端点配置并重新部署时，会出现多种故障模式。具体的失败取决于您所做的更改以及解决该问题的方式。

### 更改已注册的自动缩放的端点配置

CloudFormation 尝试在可扩展目标仍处于注册状态时更新端点。 SageMaker AI 拒绝更新并出现以下错误：
```
The variant(s) "[AllTraffic]" must be deregistered as scalable targets with Application Auto Scaling before they can be removed or have their instance type updated.
```
在 CloudFormation 达到自动扩展资源之前，SageMaker AI 会阻止端点更新。

### 手动取消注册自动缩放，然后仅更改端点配置

如果您通过 AWS 命令行界面 (AWS CLI) 取消注册可扩展目标并仅通过终端节点配置更改进行重新部署，则部署会成功。但是，CloudFormation 不会注册自动缩放，即使它位于 CloudFormation 模板中。由于CloudFormation模板中的自动缩放参数没有更改，因此CloudFormation不会注册可缩放目标或重新应用缩放策略。端点现在正在运行，没有自动缩放，并且没有错误表明出现任何问题。

### 手动注销自动伸缩，然后更改自动伸缩参数

如果您通过 AWS CLI 取消注册可扩展目标并通过自动扩展参数更改重新部署，CloudFormation 会尝试更新不再存在的 ScalableTarget 资源：
```
Resource of type 'AWS::ApplicationAutoScaling::ScalableTarget' with identifier 'endpoint/<name>/variant/AllTraffic|sagemaker:variant:DesiredInstanceCount|sagemaker' was not found.
```
此故障值得注意，因为回滚也会失败 (UPDATE_ROLLBACK_FAILED)，使堆栈处于损坏状态，需要在 CloudFormation 控制台中进行手动干预才能恢复。

## 解决方案概述

您可以使用此 CDK 构造将原生“AWS::ApplicationAutoScaling::ScalableTarget”和“AWS::ApplicationAutoScaling::ScalingPolicy”CloudFormation 资源替换为三个自定义资源。这些自定义资源通过显式依赖顺序取消注册并注册围绕端点更新的自动缩放，由 CDK 中的“node.add_dependency”调用强制执行。完整的顺序是：

- **取消注册**（自定义资源）：在端点更新开始之前删除可扩展目标。首次部署时，尚不存在可扩展目标，因此处理程序会优雅地处理错误并继续。
- **端点更新**（CDK 管理）：CDK 正常更新端点资源，交换到新的端点配置。
- **注册可扩展目标**（自定义资源）：等待端点达到“InService”状态，然后注册可扩展目标。
- **附加扩展策略**（自定义资源）：等待可扩展目标可查询，然后应用目标跟踪策略。

![构造在端点更新期间运行的四步编排：取消注册可扩展目标、更新端点、注册可扩展目标并附加扩展政策](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/19/ML-20841-1.png)

图 1：围绕 CDK 管理的端点更新进行 SageMaker AI 端点自动扩展的自定义资源编排。

注册可扩展目标和附加扩展策略使用 CDK 提供程序的异步完成模式。每个自定义资源都有一个立即返回的“on_event”处理程序和一个“is_complete”处理程序。提供者的服务员每隔一段时间（每 30 秒）重新调用“is_complete”处理程序，直到其准备就绪检查通过。提供程序的“total_timeout”（注册可扩展目标为 1 小时，附加扩展策略为 15 分钟）限制了等待时间，因此它不受任何单个 Lambda 调用超时的限制。

每当配置值发生更改时，每个自定义资源上的“ConfigHash”属性都会强制 CloudFormation 重新调用 Lambda 函数。端点配置和自动扩展参数是一起定义的，因为单个“ConfigHash”驱动自动扩展编排。

虽然该构造定义了三个自定义资源，但部署的堆栈包含三个以上的 Lambda 函数。每个自定义资源都由 CDK“cr.Provider”支持，并且提供程序框架生成自己的辅助 Lambda 函数。同步提供者（Deregister）添加一个框架功能。异步提供程序（注册可扩展目标和附加扩展策略）添加了三个（“onEvent”、“isComplete”和“onTimeout”）以及一个驱动等待程序的 AWS Step Functions 状态机。因此，部署的堆栈包含三个自定义资源、两个 Step Functions 状态机和十二个 Lambda 函数。其中五个资源包含构造自己的处理程序代码（一个用于取消注册，每个异步资源都有一对“on_event”和“is_complete”），其余七个由提供程序框架生成。您不编写或维护框架生成的函数，但它们存在于堆栈中，并且在您查看已部署的资源时值得考虑。

## 演练

在本演练中，您将使用提供的示例堆栈部署具有自动扩展功能的 SageMaker AI 端点，然后验证配置更新是否正常工作。

该演练包括以下步骤：

- 克隆存储库并安装依赖项。
- 配置您的端点和自动缩放设置。
- 部署并验证。
- 测试更新。

源代码可在[链接的 GitHub 存储库](https://github.com/aws-samples/sample-sagemaker-endpoint-autoscaling) 中获取。

### 先决条件

对于本演练，您需要以下内容：

- 具有 Amazon SageMaker AI、AWS Lambda、AWS Identity and Access Management (IAM)、Application Auto Scaling 和 Amazon CloudWatch 权限的 AWS 账户。
- 安装了 [AWS CDK v2](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html)。
- [Python 3.12](https://www.python.org/downloads/) 或更高版本。
- [uv](https://docs.astral.sh/uv/getting-started/installation/) 用于 Python 依赖管理。
- Amazon Simple Storage Service (Amazon S3) 中的 SageMaker AI 模型工件和 Amazon Elastic Container Registry (Amazon ECR) 中的容器映像，或 SageMaker AI 内置算法容器。

### 克隆存储库并安装依赖项

- 克隆存储库：`git clone https://github.com/aws-samples/sample-sagemaker-endpoint-autoscaling.git cd Sample-sagemaker-endpoint-autoscaling`
- 安装依赖项：`uvsync`

### 配置您的端点和自动缩放设置

端点和自动缩放设置在 config/`config.yaml` 中一起定义，因为单个“config_hash”驱动自动缩放编排。对任一部分的更改都会触发完整的序列。

使用您的值编辑 config/`config.yaml`：
```
endpoint:
  endpoint_name: "my-model-endpoint"
  image: "123456789012.dkr.ecr.us-east-1.amazonaws.com/my-model:latest"
  model_data_url: "s3://my-bucket/models/model.tar.gz"
  instance_type: "ml.m5.large"
  initial_instance_count: 1
  environment: {}
autoscaling:
  min_capacity: 1
  max_capacity: 10
  target_value: 100
  scale_in_cooldown: 600
  scale_out_cooldown: 120
```
端点参数映射到 SageMaker AI `CreateModel` 和 `CreateEndpointConfig` API。自动缩放参数映射到 Application Auto Scaling `RegisterScalableTarget` 和 `PutScalingPolicy` API。

### 部署并验证

- 如果您还没有启动您的 AWS 环境，请执行以下操作：“uv run cdk bootstrap”
- 部署堆栈：`uv run cdk deploy InferenceStack`

CloudFormation 创建 SageMaker AI 模型、端点配置和端点，然后按顺序运行三个自定义资源以注册自动扩展。

- 验证部署是否注册了可扩展目标：`aws application-autoscaling describe-scalable-targets --service-namespace sagemaker --resource-ids endpoint/my-model-endpoint/variant/AllTraffic`
- 验证部署是否应用了扩展策略：`aws application-autoscaling describe-scaling-policies --service-namespace sagemaker --resource-id endpoint/my-model-endpoint/variant/AllTraffic`

### 测试更新

更改 config/`config.yaml` 中的值，例如将实例类型从 `ml.m5.large` 更新为 `ml.m5.xlarge`，然后重新部署：
```
uv run cdk deploy InferenceStack
```
部署完成后，验证自动扩展是否仍已注册并具有更新的值：
```
aws application-autoscaling describe-scalable-targets
--service-namespace sagemaker
--resource-ids endpoint/my-model-endpoint/variant/AllTraffic
```
### 与现有堆栈集成

如果您是新手或想要参考实现，请使用示例堆栈。如果您已经拥有包含 SageMaker AI 资源的 CDK 堆栈，请直接使用该构造。

要与现有堆栈集成，请将“sagemaker_autoscaling/constructs/”目录复制到您的项目中，并将该构造与端点资源一起添加：
```
import json
from sagemaker_autoscaling.constructs.sagemaker_autoscaling_construct import (
    AutoscalingConfig,
    SagemakerAutoscalingConstruct,
    SagemakerAutoscalingProps,
)

# Both endpoint and auto scaling values must be in config_hash so that
# a change to either triggers the auto scaling orchestration.
config_hash = json.dumps({
    "endpoint": {
        "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/my-model:latest",
        "modelDataUrl": "s3://my-bucket/models/model.tar.gz",
        "instanceType": "ml.m5.large",
        "initialInstanceCount": 1,
    },
    "autoscaling": {
        "minCapacity": 1,
        "maxCapacity": 10,
        "targetValue": 100,
        "scaleInCooldown": 600,
        "scaleOutCooldown": 120,
    },
})

SagemakerAutoscalingConstruct(
    self, "Autoscaling",
    props=SagemakerAutoscalingProps(
        endpoint=your_endpoint,  # your CfnEndpoint
        autoscaling=AutoscalingConfig(
            min_capacity=1,
            max_capacity=10,
            target_value=100,
            scale_in_cooldown=600,
            scale_out_cooldown=120,
        ),
        config_hash=config_hash,
    ),
)
```
## 构造如何工作

本节将介绍“SagemakerAutoscalingConstruct”的关键实现细节。

### 注销

取消注册自定义资源在端点更新之前调用“deregister_scalable_target”。它为不存在可扩展目标的首次部署处理“ObjectNotFoundException”：
```
def handler(event, context):
    resource_id = event["ResourceProperties"]["ResourceId"]
    if event["RequestType"] in ("Create", "Update"):
        try:
            client.deregister_scalable_target(
                ServiceNamespace="sagemaker",
                ResourceId=resource_id,
                ScalableDimension="sagemaker:variant:DesiredInstanceCount",
            )
        except client.exceptions.ObjectNotFoundException:
            pass  # No scalable target on first deploy
    return {"PhysicalResourceId": f"deregister-{resource_id}"}
```
CDK中建立依赖关系：
```
props.endpoint.node.add_dependency(deregister)
```
### 注册可扩展目标

尽管 CloudFormation 在接受更新后将端点资源视为完整，但只有在端点达到“InService”后才能注册可扩展目标。 Register Scalable Target 使用提供程序的异步完成模式，而不是在等待期间阻止单个 Lambda 调用。 `on_event` 处理程序立即返回，并且提供者的服务员在 `query_interval` 上重新调用 `is_complete` 处理程序，直到端点为 `InService`。提供程序的“total_timeout”（1 小时）限制了等待时间，而不是任何单个 Lambda 调用的超时：
```
def handler(event, context):
    props = event["ResourceProperties"]
    resource_id = props["ResourceId"]
    endpoint_name = resource_id.split("/")[1]
    if event["RequestType"] == "Delete":
        return {"IsComplete": True}
    status = sm_client.describe_endpoint(EndpointName=endpoint_name)["EndpointStatus"]
    if status == "Failed":
        raise Exception("Endpoint in Failed state")
    if status != "InService":
        return {"IsComplete": False}
    as_client.register_scalable_target(
        ServiceNamespace="sagemaker",
        ResourceId=resource_id,
        ScalableDimension="sagemaker:variant:DesiredInstanceCount",
        MinCapacity=int(props["MinCapacity"]),
        MaxCapacity=int(props["MaxCapacity"]),
    )
    return {"IsComplete": True}
```
在堆栈删除时，“on_event”处理程序会取消注册可扩展目标以进行清理。

### 附加扩展策略

`RegisterScalableTarget` 返回后有一个短暂的窗口，其中目标尚不可查询。附加扩展策略使用相同的异步完成模式：“on_event”处理程序立即返回，而“is_complete”处理程序仅在可扩展目标可查询时报告完成，此时它应用该策略。提供者的“total_timeout”（15 分钟）限制了等待时间：
```
def handler(event, context):
    props = event["ResourceProperties"]
    resource_id = props["ResourceId"]
    if event["RequestType"] == "Delete":
        return {"IsComplete": True}
    resp = client.describe_scalable_targets(
        ServiceNamespace="sagemaker",
        ResourceIds=[resource_id],
        ScalableDimension="sagemaker:variant:DesiredInstanceCount",
    )
    if not resp.get("ScalableTargets"):
        return {"IsComplete": False}
    client.put_scaling_policy(
        PolicyName=props["PolicyName"],
        ServiceNamespace="sagemaker",
        ResourceId=resource_id,
        ScalableDimension="sagemaker:variant:DesiredInstanceCount",
        PolicyType="TargetTrackingScaling",
        TargetTrackingScalingPolicyConfiguration=json.loads(props["ScalingPolicyConfig"]),
    )
    return {"IsComplete": True}
```
在堆栈删除时，“on_event”处理程序会删除扩展策略以进行清理。

### 清理

为避免将来产生费用，请删除资源：
```
uv run cdk destroy InferenceStack
```
这将删除由目标跟踪扩展策略创建的 SageMaker AI 终端节点、终端节点配置、模型、Lambda 函数、IAM 角色、Amazon CloudWatch 警报，并取消注册可扩展目标。

## 结论

在这篇文章中，我们向您展示了如何使用可重用的 CDK 构造自动取消注册和注册自动扩展，以编排 SageMaker AI 端点更新。该构造使用三个具有显式依赖顺序的 CloudFormation 自定义资源和“ConfigHash”属性，以在部署中保持自动缩放不变。

首先，克隆“sample-sagemaker-endpoint-autoscaling”存储库并按照设置说明进行操作。该存储库包含一个示例堆栈，您可以直接部署，也可以将该构造集成到现有的 CDK 堆栈中。

有关 SageMaker AI 的 Application Auto Scaling 的更多信息，请参阅[自动扩展 Amazon SageMaker AI 模型](https://docs.aws.amazon.com/sagemaker/latest/dg/endpoint-auto-scaling.html)。有关 CloudFormation 自定义资源的更多信息，请参阅 [AWS CloudFormation 用户指南](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html) 中的自定义资源。

## 关于作者
