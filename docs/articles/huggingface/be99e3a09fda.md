---
vendor: huggingface
title: 用 Amazon SageMaker 轻松部署 Hugging Face 模型 🏎
original_title: Deploy Hugging Face models easily with Amazon SageMaker 🏎
url: https://huggingface.co/blog/deploy-hugging-face-models-easily-with-amazon-sagemaker
date: 2021-07-08
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: 2d34d34551b7
---

# **用 Amazon SageMaker 轻松部署 Hugging Face 模型 🏎**

今年早些时候，[我们宣布了与 Amazon 的战略合作](https://huggingface.co/blog/the-partnership-amazon-sagemaker-and-hugging-face)，让企业更容易在 Amazon SageMaker 中使用 Hugging Face，更快交付前沿的机器学习能力。我们推出了新的 Hugging Face Deep Learning Containers（DLC），用于[在 Amazon SageMaker 中训练 Hugging Face Transformer 模型](https://huggingface.co/transformers/sagemaker.html#getting-started-train-a-transformers-model)。

今天，我们很高兴分享一个新的推理方案，让用 Amazon SageMaker 部署 Hugging Face Transformers 比以往任何时候都简单！借助新的 Hugging Face Inference DLC，你可以只再多写一行代码就把训练好的模型部署为推理服务；也可以从 [Model Hub](https://huggingface.co/models) 上 10,000+ 个公开模型中任选其一，用 Amazon SageMaker 部署。

在 SageMaker 上部署模型，你得到的是生产就绪的端点：在 AWS 环境内轻松扩缩、内置监控、海量企业级特性。这是一次出色的合作，希望大家都能用起来！

下面是用新的 [SageMaker Hugging Face Inference Toolkit](https://github.com/aws/sagemaker-huggingface-inference-toolkit) 部署基于 Transformers 模型的方法：

```
from sagemaker.huggingface import HuggingFaceModel

# create Hugging Face Model Class and deploy it as SageMaker Endpoint
huggingface_model = HuggingFaceModel(...).deploy()
```

就这么简单！🚀

想深入了解如何用 Amazon SageMaker Python SDK 访问和使用新的 Hugging Face DLC，请看后文的指南和资源。

## **资源、文档与示例 📄**

以下是把模型部署到 Amazon SageMaker 所需的全部重要资源。

### **博客/视频**

- [视频：把 S3 上的 Hugging Face Transformers 模型部署到 Amazon SageMaker](https://youtu.be/pfBGgSGnYLs)
- [视频：把 Model Hub 上的 Hugging Face Transformers 模型部署到 Amazon SageMaker](https://youtu.be/l9QZuazbzWM)

### **示例/文档**

- [Hugging Face 的 Amazon SageMaker 文档](https://huggingface.co/docs/sagemaker/main)
- [部署模型到 Amazon SageMaker](https://huggingface.co/docs/sagemaker/inference)
- [Amazon SageMaker 的 Hugging Face 文档](https://docs.aws.amazon.com/sagemaker/latest/dg/hugging-face.html)
- [SageMaker Python SDK 的 Hugging Face 文档](https://sagemaker.readthedocs.io/en/stable/frameworks/huggingface/index.html)
- [Deep Learning Container](https://github.com/aws/deep-learning-containers/blob/master/available_images.md#huggingface-training-containers)
- [Notebook：把 10,000+ Hugging Face Transformers 之一部署到 Amazon SageMaker 做推理](https://github.com/huggingface/notebooks/blob/master/sagemaker/11_deploy_model_from_hf_hub/deploy_transformer_model_from_hf_hub.ipynb)
- [Notebook：把 S3 上的 Hugging Face Transformer 模型部署到 SageMaker 做推理](https://github.com/huggingface/notebooks/blob/master/sagemaker/10_deploy_model_from_s3/deploy_transformer_model_from_s3.ipynb)

## **SageMaker Hugging Face Inference Toolkit ⚙️**

除了为推理优化的 Hugging Face Transformers Deep Learning Container，我们还为 Amazon SageMaker 打造了一个新的 [Inference Toolkit](https://github.com/aws/sagemaker-huggingface-inference-toolkit)。这个 Toolkit 利用 `transformers` 库的 `pipelines`，支持零代码部署模型——无需为预处理/后处理编写任何代码。下面「快速上手」一节提供两个把模型部署到 Amazon SageMaker 的示例。

除了零代码部署，Inference Toolkit 还支持「自带代码（bring your own code）」方式，你可以覆写默认方法。关于「自带代码」的更多信息见[文档](https://github.com/aws/sagemaker-huggingface-inference-toolkit#-user-defined-codemodules)，或查看示例 notebook「deploy custom inference code to Amazon SageMaker」。

### **API - Inference Toolkit 说明**

基于 `transformers pipelines`，我们设计了一套 API，让你轻松享受 `pipelines` 的全部能力。这个 API 的接口与 [🤗 Accelerated Inference API](https://api-inference.huggingface.co/docs/python/html/detailed_parameters.html) 相似：输入需要放在 `inputs` 键里；如果想要额外的受支持 `pipelines` 参数，可以放进 `parameters` 键。下面是请求示例。

```
# text-classification request body
{
    "inputs": "Camera - You are awarded a SiPix Digital Camera! call 09061221066 fromm landline. Delivery within 28 days."
}
# question-answering request body
{
    "inputs": {
        "question": "What is used for inference?",
        "context": "My Name is Philipp and I live in Nuremberg. This model is used with sagemaker for inference."
    }
}
# zero-shot classification request body
{
    "inputs": "Hi, I recently bought a device from your company but it is not working as advertised and I would like to get reimbursed!",
    "parameters": {
        "candidate_labels": [
            "refund",
            "legal",
            "faq"
        ]
    }
}
```

## **快速上手 🧭**

本指南将使用新的 Hugging Face Inference DLC 和 Amazon SageMaker Python SDK，部署两个 transformer 模型做推理。

第一个例子：部署在 Amazon SageMaker 上训练好的 Hugging Face Transformer 模型。

第二个例子：直接从 [Model Hub](https://huggingface.co/models) 上的 10,000+ 公开 Hugging Face Transformers 模型中选一个，部署到 Amazon SageMaker 做推理。

### **搭建环境**

示例中我们使用 Amazon SageMaker Notebook Instance。[如何创建 Notebook Instance 见这里](https://docs.aws.amazon.com/sagemaker/latest/dg/nbi.html)。开始之前，进入你的 Jupyter Notebook 或 JupyterLab，用 `conda_pytorch_p36` 内核新建一个 Notebook。

***注：使用 Jupyter 是可选的：只要装好 SDK、能连通云端且有相应权限，我们在任何地方都能发起 SageMaker API 调用——比如笔记本电脑、其他 IDE，或 Airflow、AWS Step Functions 这类任务调度器。***

然后安装所需依赖。

```
pip install "sagemaker>=2.48.0" --upgrade
```

要在 SageMaker 上部署模型，需要创建一个 `sagemaker` Session，并提供有合适权限的 IAM role。`get_execution_role` 方法是 SageMaker SDK 提供的便利选项；你也可以直接写出希望端点使用的 role ARN。这个 IAM role 之后会挂到 Endpoint 上，例如用于从 Amazon S3 下载模型。

```
import sagemaker

sess = sagemaker.Session()
role = sagemaker.get_execution_role()
```

### **把训练好的 Hugging Face Transformer 模型部署到 SageMaker 做推理**

部署在 SageMaker 上训练好的 Hugging Face 模型有两种方式：训练结束后立即部署；或者稍后部署，用 `model_data` 指向保存在 Amazon S3 上的模型。除了下面两种写法，你还可以用更底层的 SDK（如 `boto3`、`AWS CLI`）、`Terraform` 以及 CloudFormation 模板来实例化 Hugging Face 端点。

#### **用 Estimator 类在训练结束后直接部署模型**

如果训练完直接部署，需要确保训练脚本保存了所有必需的模型工件，包括 tokenizer 和模型。训练后直接部署的好处是：SageMaker 模型容器的元数据会包含源训练任务，提供从训练任务到已部署模型的完整血缘。

```
from sagemaker.huggingface import HuggingFace

############ pseudo code start ############

# create HuggingFace estimator for running training
huggingface_estimator = HuggingFace(....)

# starting the train job with our uploaded datasets as input
huggingface_estimator.fit(...)

############ pseudo code end ############

# deploy model to SageMaker Inference
predictor = hf_estimator.deploy(initial_instance_count=1, instance_type="ml.m5.xlarge")

# example request, you always need to define "inputs"
data = {
   "inputs": "Camera - You are awarded a SiPix Digital Camera! call 09061221066 fromm landline. Delivery within 28 days."
}
# request
predictor.predict(data)
```

发出请求后，可以再删除端点。

```
# delete endpoint
predictor.delete_endpoint()
```

#### **用 `HuggingFaceModel` 类从预训练 checkpoint 部署模型**

如果模型早已训练好、只想以后某个时刻部署，可以用 `model_data` 参数指定 tokenizer 和模型权重的位置。

```
from sagemaker.huggingface.model import HuggingFaceModel

# create Hugging Face Model Class
huggingface_model = HuggingFaceModel(
   model_data="s3://models/my-bert-model/model.tar.gz",  # path to your trained sagemaker model
   role=role, # iam role with permissions to create an Endpoint
   transformers_version="4.6", # transformers version used
   pytorch_version="1.7", # pytorch version used
)
# deploy model to SageMaker Inference
predictor = huggingface_model.deploy(
   initial_instance_count=1, 
   instance_type="ml.m5.xlarge"
)

# example request, you always need to define "inputs"
data = {
   "inputs": "Camera - You are awarded a SiPix Digital Camera! call 09061221066 fromm landline. Delivery within 28 days."
}

# request
predictor.predict(data)
```

发出请求后，可以再删除端点：

```
# delete endpoint
predictor.delete_endpoint()
```

### **把 10,000+ Hugging Face Transformers 之一部署到 Amazon SageMaker 做推理**

要从 Hugging Face Model Hub 直接把模型部署到 Amazon SageMaker，需要在创建 `HuggingFaceModel` 时定义两个环境变量：

- HF_MODEL_ID：定义模型 id，创建 SageMaker Endpoint 时会自动从 [huggingface.co/models](http://huggingface.co/models) 加载。🤗 Hub 上 10,000+ 模型都可以通过这个环境变量使用。
- HF_TASK：定义所用 🤗 Transformers pipeline 的任务。完整任务列表见[这里](https://huggingface.co/transformers/main_classes/pipelines.html)。

```
from sagemaker.huggingface.model import HuggingFaceModel

# Hub Model configuration. <https://huggingface.co/models>
hub = {
  'HF_MODEL_ID':'distilbert-base-uncased-distilled-squad', # model_id from hf.co/models
  'HF_TASK':'question-answering' # NLP task you want to use for predictions
}

# create Hugging Face Model Class
huggingface_model = HuggingFaceModel(
   env=hub, # configuration for loading model from Hub
   role=role, # iam role with permissions to create an Endpoint
   transformers_version="4.6", # transformers version used
   pytorch_version="1.7", # pytorch version used
)

# deploy model to SageMaker Inference
predictor = huggingface_model.deploy(
   initial_instance_count=1,
   instance_type="ml.m5.xlarge"
)

# example request, you always need to define "inputs"
data = {
"inputs": {
    "question": "What is used for inference?",
    "context": "My Name is Philipp and I live in Nuremberg. This model is used with sagemaker for inference."
    }
}

# request
predictor.predict(data)
```

发出请求后，可以再删除端点。

```
# delete endpoint
predictor.delete_endpoint()
```

## **FAQ 🎯**

完整的[常见问题](https://huggingface.co/docs/sagemaker/faq)见[文档](https://huggingface.co/docs/sagemaker/faq)。

*问：哪些模型可以部署做推理？*

答：你可以部署：

- 任何在 Amazon SageMaker（或其他兼容平台）训练的 🤗 Transformers 模型，只要能适配 SageMaker Hosting 的设计；
- Hugging Face [Model Hub](https://huggingface.co/models) 上 10,000+ 公开 Transformer 模型中的任何一个；或
- 托管在你 Hugging Face 付费账号里的私有模型！

*问：Inference Toolkit 支持哪些 pipelines、哪些任务？*

答：Inference Toolkit 和 DLC 支持任何 `transformers` `pipelines`。完整列表见[这里](https://huggingface.co/transformers/main_classes/pipelines.html)。

*问：托管 SageMaker 端点时必须用 `transformers pipelines` 吗？*

答：不必。你也可以编写自定义推理代码来服务自己的模型和逻辑，[文档在这里](https://huggingface.co/docs/sagemaker/inference#user-defined-codemodules)。

*问：必须使用 SageMaker Python SDK 才能用 Hugging Face Deep Learning Containers（DLC）吗？*

答：可以不用 SageMaker Python SDK，直接用 Hugging Face DLC，通过其他 SDK 把模型部署到 SageMaker，如 [AWS CLI](https://docs.aws.amazon.com/cli/latest/reference/sagemaker/create-training-job.html)、[boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker.html#SageMaker.Client.create_training_job) 或 [CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpoint.html)。DLC 也发布在 Amazon ECR，可以在任何你选择的环境中拉取使用。

*问：为什么要用 Hugging Face Deep Learning Containers？*

答：DLC 是充分测试、持续维护、经过优化的深度学习环境，无需安装、配置和维护。特别是，我们的推理 DLC 自带写好的 serving 栈，大幅降低了深度学习部署的技术门槛。

*问：Amazon SageMaker 如何保护我的数据和代码？*

答：Amazon SageMaker 提供了大量安全机制，包括**[静态加密](https://docs.aws.amazon.com/sagemaker/latest/dg/encryption-at-rest-nbi.html)**和**[传输加密](https://docs.aws.amazon.com/sagemaker/latest/dg/encryption-in-transit.html)**、**[Virtual Private Cloud（VPC）连接](https://docs.aws.amazon.com/sagemaker/latest/dg/interface-vpc-endpoint.html)**，以及**[身份与访问管理（IAM）](https://docs.aws.amazon.com/sagemaker/latest/dg/security_iam_service-with-iam.html)**。想更多了解 AWS 云端和 Amazon SageMaker 的安全，请访问 **[Amazon SageMaker 安全](https://docs.aws.amazon.com/sagemaker/latest/dg/security_iam_service-with-iam.html)** 和 **[AWS 云安全](https://docs.aws.amazon.com/sagemaker/latest/dg/security_iam_service-with-iam.html)**。

*问：我的区域可用吗？*

答：支持区域列表请看 **[AWS 区域表](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/)**（涵盖全部 AWS 全球基础设施）。

*问：这个方案提供付费支持或支持 SLA 吗？*

答：AWS 可向客户提供 AWS Technical Support 服务等级，覆盖 AWS 产品和服务的开发与生产问题——具体范围和细节请参考 AWS Support 官方说明。

如果你的问题适合由 Hugging Face 社区解答或对大家都有好处，请**发到 Hugging Face 论坛**（[https://discuss.huggingface.co/c/sagemaker/17](https://discuss.huggingface.co/c/sagemaker/17)）。

如果你需要 Hugging Face 团队的付费支持来加速你的 NLP 路线图，我们的 [Expert Acceleration Program](https://huggingface.co/support) 由开源、科学和机器学习工程团队提供直接指导。
