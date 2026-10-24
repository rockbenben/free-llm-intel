---
vendor: aws_bedrock
title: Orchestrating SageMaker AI endpoint auto scaling with AWS CDK
original_title: Orchestrating SageMaker AI endpoint auto scaling with AWS CDK
url: https://aws.amazon.com/blogs/machine-learning/orchestrating-sagemaker-ai-endpoint-auto-scaling-with-aws-cdk
date: 2026-10-23
lang: en
captured: 2026-10-24
extractor: readability-v1
status: ok
body_sha: 42c0ece35504
---

## [Artificial Intelligence](https://aws.amazon.com/blogs/machine-learning/)

# Orchestrating SageMaker AI endpoint auto scaling with AWS CDK

Updating the Amazon Sagemaker AI real-time endpoint configuration (changing the instance type, instance count, or environment variables) causes deployments through AWS CloudFormation or the AWS Cloud Development Kit (AWS CDK) to fail. SageMaker AI requires you to deregister the scalable target before updating the endpoint, but when you deregister it, CloudFormation can’t track the AWS Application Auto Scaling resources.

In this post, we show you how to use a reusable CDK construct with AWS CloudFormation custom resources to orchestrate deregister and register auto scaling automatically during endpoint updates. You can update your endpoint configuration and auto scaling parameters in a single deployment without manual intervention.

## Why this problem occurs

When you deploy a SageMaker AI endpoint with native CloudFormation auto scaling resources, then change the endpoint configuration and redeploy, several failure modes emerge. The specific failure depends on what you change and how you work around the issue.

### Changing the endpoint configuration with auto scaling registered

CloudFormation tries to update the endpoint while the scalable target is still registered. SageMaker AI rejects the update with the following error:

```
The variant(s) "[AllTraffic]" must be deregistered as scalable targets with Application Auto Scaling before they can be removed or have their instance type updated.
```

SageMaker AI blocks the endpoint update before CloudFormation reaches the auto scaling resources.

### Manually deregistering auto scaling, then changing only the endpoint configuration

If you deregister the scalable target through the AWS Command Line Interface (AWS CLI) and redeploy with only an endpoint configuration change, the deployment succeeds. However, CloudFormation doesn’t register auto scaling even though it is in the CloudFormation template. Because the auto scaling parameters in the CloudFormation template haven’t changed, CloudFormation doesn’t register the scalable target or re-apply the scaling policy. The endpoint is now running without auto scaling, and there is no error to indicate anything went wrong.

### Manually deregistering auto scaling, then changing auto scaling parameters

If you deregister the scalable target through the AWS CLI and redeploy with auto scaling parameter changes, CloudFormation tries to update the ScalableTarget resource that no longer exists:

```
Resource of type 'AWS::ApplicationAutoScaling::ScalableTarget' with identifier 'endpoint/<name>/variant/AllTraffic|sagemaker:variant:DesiredInstanceCount|sagemaker' was not found.
```

This failure is notable because the rollback also fails (UPDATE_ROLLBACK_FAILED), leaving the stack in a broken state that requires manual intervention in the CloudFormation console to recover.

## Solution overview

You can use this CDK construct to replace the native `AWS::ApplicationAutoScaling::ScalableTarget` and `AWS::ApplicationAutoScaling::ScalingPolicy` CloudFormation resources with three custom resources. These custom resources deregister and register auto scaling around the endpoint update with explicit dependency ordering, enforced by `node.add_dependency` calls in CDK. The full sequence is:

- **Deregister** (custom resource): Removes the scalable target before the endpoint update begins. On first deploy, no scalable target exists yet, so the handler handles the error gracefully and continues.
- **Endpoint update** (CDK-managed): CDK updates the endpoint resource normally, swapping to the new endpoint configuration.
- **Register Scalable Target** (custom resource): Waits for the endpoint to reach `InService` status, then registers the scalable target.
- **Attach Scaling Policy** (custom resource): Waits for the scalable target to be queryable, then applies the target tracking policy.

![Four-step orchestration the construct runs during an endpoint update: deregister the scalable target, update the endpoint, register the scalable target, and attach the scaling policy](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/19/ML-20841-1.png)

Figure 1: Custom resource orchestration of SageMaker AI endpoint auto scaling around a CDK-managed endpoint update.

Register Scalable Target and Attach Scaling Policy use the CDK provider’s asynchronous completion pattern. Each custom resource has an `on_event` handler that returns immediately and an `is_complete` handler. The provider’s waiter re-invokes the `is_complete` handler on an interval (every 30 seconds) until its readiness check passes. The provider’s `total_timeout` (1 hour for Register Scalable Target, 15 minutes for Attach Scaling Policy) bounds the wait, so it isn’t limited by the timeout of any single Lambda invocation.

A `ConfigHash` property on each custom resource forces CloudFormation to re-invoke the Lambda functions whenever a configuration value changes. The endpoint configuration and auto scaling parameters are defined together because a single `ConfigHash` drives the auto scaling orchestration.

While the construct defines three custom resources, the deployed stack contains more than three Lambda functions. Each custom resource is backed by a CDK `cr.Provider`, and the provider framework generates its own helper Lambda functions. A synchronous provider (Deregister) adds one framework function. An asynchronous provider (Register Scalable Target and Attach Scaling Policy) adds three (`onEvent`, `isComplete`, and `onTimeout`) plus an AWS Step Functions state machine that drives the waiter. As a result, the deployed stack contains three custom resources, two Step Functions state machines, and twelve Lambda functions. Five of the resources hold the construct’s own handler code (one for Deregister, and an `on_event` and `is_complete` pair for each asynchronous resource), with the remaining seven generated by the provider framework. You don’t write or maintain the framework-generated functions, but they are present in the stack and worth accounting for when you review the deployed resources.

## Walkthrough

In this walkthrough, you deploy a SageMaker AI endpoint with auto scaling using the provided example stack, then verify that configuration updates work correctly.

The walkthrough includes the following steps:

- Clone the repository and install dependencies.
- Configure your endpoint and auto scaling settings.
- Deploy and verify.
- Test an update.

The source code is available in the [linked GitHub repository](https://github.com/aws-samples/sample-sagemaker-endpoint-autoscaling).

### Prerequisites

For this walkthrough, you need the following:

- An AWS account with permissions for Amazon SageMaker AI, AWS Lambda, AWS Identity and Access Management (IAM), Application Auto Scaling, and Amazon CloudWatch.
- [AWS CDK v2](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html) installed.
- [Python 3.12](https://www.python.org/downloads/) or later.
- [uv](https://docs.astral.sh/uv/getting-started/installation/) for Python dependency management.
- A SageMaker AI model artifact in Amazon Simple Storage Service (Amazon S3) and a container image in Amazon Elastic Container Registry (Amazon ECR), or a SageMaker AI built-in algorithm container.

### Clone the repository and install dependencies

- Clone the repository:  `git clone https://github.com/aws-samples/sample-sagemaker-endpoint-autoscaling.git cd sample-sagemaker-endpoint-autoscaling`
- Install dependencies:  `uv sync`

### Configure your endpoint and auto scaling settings

The endpoint and auto scaling settings are defined together in config/`config.yaml` because a single `config_hash` drives the auto scaling orchestration. A change to either section triggers the full sequence.

Edit config/`config.yaml` with your values:

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

The endpoint parameters map to the SageMaker AI `CreateModel` and `CreateEndpointConfig` APIs. The auto scaling parameters map to the Application Auto Scaling `RegisterScalableTarget` and `PutScalingPolicy` APIs.

### Deploy and verify

- Bootstrap your AWS environment if you haven’t already:  `uv run cdk bootstrap`
- Deploy the stack:  `uv run cdk deploy InferenceStack`

CloudFormation creates the SageMaker AI model, endpoint configuration, and endpoint, then runs the three custom resources in sequence to register auto scaling.

- Verify that the deployment registered the scalable target:  `aws application-autoscaling describe-scalable-targets --service-namespace sagemaker --resource-ids endpoint/my-model-endpoint/variant/AllTraffic`
- Verify that the deployment applied the scaling policy:  `aws application-autoscaling describe-scaling-policies --service-namespace sagemaker --resource-id endpoint/my-model-endpoint/variant/AllTraffic`

### Test an update

Change a value in config/`config.yaml`, for example, update the instance type from `ml.m5.large` to `ml.m5.xlarge`, and redeploy:

```
uv run cdk deploy InferenceStack
```

After the deployment completes, verify that auto scaling is still registered and has the updated values:

```
aws application-autoscaling describe-scalable-targets
--service-namespace sagemaker
--resource-ids endpoint/my-model-endpoint/variant/AllTraffic
```

### Integrating with an existing stack

Use the example stack if you’re starting fresh or want a reference implementation. Use the construct directly if you already have a CDK stack with SageMaker AI resources.

To integrate with an existing stack, copy the `sagemaker_autoscaling/constructs/` directory into your project and add the construct alongside your endpoint resources:

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

## How the construct works

This section walks through the key implementation details of `SagemakerAutoscalingConstruct`.

### Deregister

The Deregister custom resource calls `deregister_scalable_target` before the endpoint update. It handles `ObjectNotFoundException` for first deployments where no scalable target exists:

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

The dependency is established in CDK:

```
props.endpoint.node.add_dependency(deregister)
```

### Register Scalable Target

Even though CloudFormation treats the endpoint resource as complete once the update is accepted, the scalable target can only be registered after the endpoint reaches `InService`. Rather than block a single Lambda invocation on that wait, Register Scalable Target uses the provider’s asynchronous completion pattern. The `on_event` handler returns immediately, and the provider’s waiter re-invokes the `is_complete` handler on `query_interval` until the endpoint is `InService`. The provider’s `total_timeout` (1 hour) bounds the wait, not the timeout of any single Lambda invocation:

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

On stack deletion, the `on_event` handler deregisters the scalable target to clean up.

### Attach Scaling Policy

There is a brief window after `RegisterScalableTarget` returns where the target isn’t yet queryable. Attach Scaling Policy uses the same asynchronous completion pattern: the `on_event` handler returns immediately, and the `is_complete` handler reports completion only once the scalable target is queryable, at which point it applies the policy. The provider’s `total_timeout` (15 minutes) bounds the wait:

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

On stack deletion, the `on_event` handler deletes the scaling policy to clean up.

### Cleaning up

To avoid incurring future charges, delete the resources:

```
uv run cdk destroy InferenceStack
```

This removes the SageMaker AI endpoint, endpoint configuration, model, Lambda functions, IAM roles, Amazon CloudWatch alarms created by the target tracking scaling policy, and deregisters the scalable target.

## Conclusion

In this post, we showed you how to use a reusable CDK construct to deregister and register auto scaling automatically to orchestrate SageMaker AI endpoint updates. The construct uses three CloudFormation custom resources with explicit dependency ordering and a `ConfigHash` property to keep auto scaling intact across deployments.

To get started, clone the `sample-sagemaker-endpoint-autoscaling` repository and follow the setup instructions. The repository includes an example stack you can deploy directly, or you can integrate the construct into your existing CDK stack.

For more information about Application Auto Scaling for SageMaker AI, see [Automatically scale Amazon SageMaker AI models](https://docs.aws.amazon.com/sagemaker/latest/dg/endpoint-auto-scaling.html). For more information about CloudFormation custom resources, see Custom resources in the [AWS CloudFormation User Guide](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html).

## About the author
