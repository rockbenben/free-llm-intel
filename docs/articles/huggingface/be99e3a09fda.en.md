---
vendor: huggingface
title: Deploy Hugging Face models easily with Amazon SageMaker 🏎
original_title: Deploy Hugging Face models easily with Amazon SageMaker
url: https://huggingface.co/blog/deploy-hugging-face-models-easily-with-amazon-sagemaker
date: 2021-07-08
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 2ba02e07e87f
---


# **Deploy Hugging Face models easily with Amazon SageMaker 🏎**

					July 8, 2021

Update on GitHub


2

- [![](https://huggingface.co/avatars/5727a1c624ff64329939684ed62f5293.svg)](https://huggingface.co/SalahAbdoNLP)
- [![](https://huggingface.co/avatars/129d1e86bbaf764b507501f4feb177db.svg)](https://huggingface.co/Aanuoluwapo65)

Philipp Schmid

philschmid

Earlier this year[ we announced a strategic collaboration with Amazon](https://huggingface.co/blog/the-partnership-amazon-sagemaker-and-hugging-face) to make it easier for companies to use Hugging Face in Amazon SageMaker, and ship cutting-edge Machine Learning features faster. We introduced new Hugging Face Deep Learning Containers (DLCs) to[ train Hugging Face Transformer models in Amazon SageMaker](https://huggingface.co/transformers/sagemaker.html#getting-started-train-a-transformers-model).

Today, we are excited to share a new inference solution with you that makes it easier than ever to deploy Hugging Face Transformers with Amazon SageMaker! With the new Hugging Face Inference DLCs, you can deploy your trained models for inference with just one more line of code, or select any of the 10,000+ publicly available models from the[ Model Hub](https://huggingface.co/models), and deploy them with Amazon SageMaker.

Deploying models in SageMaker provides you with production-ready endpoints that scale easily within your AWS environment, with built-in monitoring and a ton of enterprise features. It's been an amazing collaboration and we hope you will take advantage of it!

Here's how to use the new[ SageMaker Hugging Face Inference Toolkit](https://github.com/aws/sagemaker-huggingface-inference-toolkit) to deploy Transformers-based models:

```
from sagemaker.huggingface import HuggingFaceModel

# create Hugging Face Model Class and deploy it as SageMaker Endpoint
huggingface_model = HuggingFaceModel(...).deploy()
```

That's it! 🚀

To learn more about accessing and using the new Hugging Face DLCs with the Amazon SageMaker Python SDK, check out the guides and resources below.

## **Resources, Documentation & Samples 📄**

Below you can find all the important resources for deploying your models to Amazon SageMaker.

### **Blog/Video**

- [Video: Deploy a Hugging Face Transformers Model from S3 to Amazon SageMaker](https://youtu.be/pfBGgSGnYLs)
- [Video: Deploy a Hugging Face Transformers Model from the Model Hub to Amazon SageMaker](https://youtu.be/l9QZuazbzWM)

### **Samples/Documentation**

- [Hugging Face documentation for Amazon SageMaker](https://huggingface.co/docs/sagemaker/main)
- [Deploy models to Amazon SageMaker](https://huggingface.co/docs/sagemaker/inference)
- [Amazon SageMaker documentation for Hugging Face](https://docs.aws.amazon.com/sagemaker/latest/dg/hugging-face.html)
- [Python SDK SageMaker documentation for Hugging Face](https://sagemaker.readthedocs.io/en/stable/frameworks/huggingface/index.html)
- [Deep Learning Container](https://github.com/aws/deep-learning-containers/blob/master/available_images.md#huggingface-training-containers)
- [Notebook: Deploy one of the 10 000+ Hugging Face Transformers to Amazon SageMaker for Inference](https://github.com/huggingface/notebooks/blob/master/sagemaker/11_deploy_model_from_hf_hub/deploy_transformer_model_from_hf_hub.ipynb)
- [Notebook: Deploy a Hugging Face Transformer model from S3 to SageMaker for inference](https://github.com/huggingface/notebooks/blob/master/sagemaker/10_deploy_model_from_s3/deploy_transformer_model_from_s3.ipynb)

## **SageMaker Hugging Face Inference Toolkit ⚙️**

In addition to the Hugging Face Transformers-optimized Deep Learning Containers for inference, we have created a new[ Inference Toolkit](https://github.com/aws/sagemaker-huggingface-inference-toolkit) for Amazon SageMaker. This new Inference Toolkit leverages the `pipelines` from the `transformers` library to allow zero-code deployments of models without writing any code for pre- or post-processing. In the "Getting Started" section below you find two examples of how to deploy your models to Amazon SageMaker.

In addition to the zero-code deployment, the Inference Toolkit supports "bring your own code" methods, where you can override the default methods. You can learn more about "bring your own code" in the documentation[ here](https://github.com/aws/sagemaker-huggingface-inference-toolkit#-user-defined-codemodules) or you can check out the sample notebook "deploy custom inference code to Amazon SageMaker".

### **API - Inference Toolkit Description**

Using the` transformers pipelines`, we designed an API, which makes it easy for you to benefit from all `pipelines` features. The API has a similar interface than the[ 🤗 Accelerated Inference API](https://api-inference.huggingface.co/docs/python/html/detailed_parameters.html), meaning your inputs need to be defined in the `inputs` key and if you want additional supported `pipelines` parameters you can add them in the `parameters` key. Below you can find examples for requests.

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

## **Getting started 🧭**

In this guide we will use the new Hugging Face Inference DLCs and Amazon SageMaker Python SDK to deploy two transformer models for inference.

In the first example, we deploy for inference a Hugging Face Transformer model trained in Amazon SageMaker.

In the second example, we directly deploy one of the 10,000+ publicly available Hugging Face Transformers models from the[ Model Hub](https://huggingface.co/models) to Amazon SageMaker for Inference.

### **Setting up the environment**

We will use an Amazon SageMaker Notebook Instance for the example. You can learn[ here how to set up a Notebook Instance.](https://docs.aws.amazon.com/sagemaker/latest/dg/nbi.html) To get started, jump into your Jupyter Notebook or JupyterLab and create a new Notebook with the `conda_pytorch_p36` kernel.

***Note: The use of Jupyter is optional: We could also launch SageMaker API calls from anywhere we have an SDK installed, connectivity to the cloud, and appropriate permissions, such as a Laptop, another IDE, or a task scheduler like Airflow or AWS Step Functions.***

After that we can install the required dependencies.

```
pip install "sagemaker>=2.48.0" --upgrade
```

To deploy a model on SageMaker, we need to create a `sagemaker` Session and provide an IAM role with the right permission. The `get_execution_role` method is provided by the SageMaker SDK as an optional convenience. You can also specify the role by writing the specific role ARN you want your endpoint to use. This IAM role will be later attached to the Endpoint, e.g. download the model from Amazon S3.

```
import sagemaker

sess = sagemaker.Session()
role = sagemaker.get_execution_role()
```

### **Deploy a trained Hugging Face Transformer model to SageMaker for inference**

There are two ways to deploy your SageMaker trained Hugging Face model. You can either deploy it after your training is finished, or you can deploy it later, using the `model_data` pointing to your saved model on Amazon S3. In addition to the two below-mentioned options, you can also instantiate Hugging Face endpoints with lower-level SDK such as `boto3` and `AWS CLI`, `Terraform` and with CloudFormation templates.

#### **Deploy the model directly after training with the Estimator class**

If you deploy your model directly after training, you need to ensure that all required model artifacts are saved in your training script, including the tokenizer and the model. A benefit of deploying directly after training is that SageMaker model container metadata will contain the source training job, providing lineage from training job to deployed model.

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

After we run our request we can delete the endpoint again with.

```
# delete endpoint
predictor.delete_endpoint()
```

#### **Deploy the model from pre-trained checkpoints using the `HuggingFaceModel` class**

If you've already trained your model and want to deploy it at some later time, you can use the `model_data` argument to specify the location of your tokenizer and model weights.

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

After we run our request, we can delete the endpoint again with:

```
# delete endpoint
predictor.delete_endpoint()
```

### **Deploy one of the 10,000+ Hugging Face Transformers to Amazon SageMaker for Inference**

To deploy a model directly from the Hugging Face Model Hub to Amazon SageMaker, we need to define two environment variables when creating the `HuggingFaceModel`. We need to define:

- HF_MODEL_ID: defines the model id, which will be automatically loaded from[ huggingface.co/models](http://huggingface.co/models) when creating or SageMaker Endpoint. The 🤗 Hub provides 10,000+ models all available through this environment variable.
- HF_TASK: defines the task for the used 🤗 Transformers pipeline. A full list of tasks can be found[ here](https://huggingface.co/transformers/main_classes/pipelines.html).

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

After we run our request we can delete the endpoint again with.

```
# delete endpoint
predictor.delete_endpoint()
```

## **FAQ 🎯**

You can find the complete [Frequently Asked Questions](https://huggingface.co/docs/sagemaker/faq) in the [documentation](https://huggingface.co/docs/sagemaker/faq).

*Q: Which models can I deploy for Inference?*

A: You can deploy:

- any 🤗 Transformers model trained in Amazon SageMaker, or other compatible platforms and that can accommodate the SageMaker Hosting design
- any of the 10,000+ publicly available Transformer models from the Hugging Face[ Model Hub](https://huggingface.co/models), or
- your private models hosted in your Hugging Face premium account!

*Q: Which pipelines, tasks are supported by the Inference Toolkit?*

A: The Inference Toolkit and DLC support any of the `transformers` `pipelines`. You can find the full list [here](https://huggingface.co/transformers/main_classes/pipelines.html)

*Q: Do I have to use the `transformers pipelines` when hosting SageMaker endpoints?*

A: No, you can also write your custom inference code to serve your own models and logic, documented [here](https://huggingface.co/docs/sagemaker/inference#user-defined-codemodules).

*Q: Do I have to use the SageMaker Python SDK to use the Hugging Face Deep Learning Containers (DLCs)?*

A: You can use the Hugging Face DLC without the SageMaker Python SDK and deploy your models to SageMaker with other SDKs, such as the [AWS CLI](https://docs.aws.amazon.com/cli/latest/reference/sagemaker/create-training-job.html), [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker.html#SageMaker.Client.create_training_job) or [Cloudformation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sagemaker-endpoint.html). The DLCs are also available through Amazon ECR and can be pulled and used in any environment of choice.

*Q: Why should I use the Hugging Face Deep Learning Containers?*

A: The DLCs are fully tested, maintained, optimized deep learning environments that require no installation, configuration, or maintenance. In particular, our inference DLC comes with a pre-written serving stack, which drastically lowers the technical bar of DL serving.

*Q: How is my data and code secured by Amazon SageMaker?*

A: Amazon SageMaker provides numerous security mechanisms including **[encryption at rest](https://docs.aws.amazon.com/sagemaker/latest/dg/encryption-at-rest-nbi.html)** and **[in transit](https://docs.aws.amazon.com/sagemaker/latest/dg/encryption-in-transit.html)**, **[Virtual Private Cloud (VPC) connectivity](https://docs.aws.amazon.com/sagemaker/latest/dg/interface-vpc-endpoint.html),** and **[Identity and Access Management (IAM)](https://docs.aws.amazon.com/sagemaker/latest/dg/security_iam_service-with-iam.html)**. To learn more about security in the AWS cloud and with Amazon SageMaker, you can visit **[Security in Amazon SageMaker](https://docs.aws.amazon.com/sagemaker/latest/dg/security_iam_service-with-iam.html)** and **[AWS Cloud Security](https://docs.aws.amazon.com/sagemaker/latest/dg/security_iam_service-with-iam.html)**.

*Q: Is this available in my region?*

A: For a list of the supported regions, please visit the **[AWS region table](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/)** for all AWS global infrastructure.

*Q: Do you offer premium support or support SLAs for this solution?*

A: AWS Technical Support tiers are available from AWS and cover development and production issues for AWS products and services - please refer to AWS Support for specifics and scope.

If you have questions which the Hugging Face community can help answer and/or benefit from, please **[post them in the Hugging Face forum](https://discuss.huggingface.co/c/sagemaker/17)**.

If you need premium support from the Hugging Face team to accelerate your NLP roadmap, our[ Expert Acceleration Program](https://huggingface.co/support) offers direct guidance from our open-source, science, and ML Engineering teams.

More Articles from our Blog

guide

announcement

partnerships

## Subscribe to Enterprise Hub with your AWS Account

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1638698875017-noauth.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1608146735109-5fcfb7c407408029ba3577e2.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1605114051380-noauth.jpeg)

9

May 9, 2024

guide

partnerships

aws

## Hugging Face Text Generation Inference available for AWS Inferentia2

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1624629516652-5ff5d596f244529b3ec0fb89.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/647995564be04c76ce4547b3/-tlmMQgr-CTm5TCIjGApB.jpeg)

5

February 1, 2024

### Community

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fdeploy-hugging-face-models-easily-with-amazon-sagemaker) or [log in](https://huggingface.co/login?next=%2Fblog%2Fdeploy-hugging-face-models-easily-with-amazon-sagemaker) to comment


2

- [![](https://huggingface.co/avatars/5727a1c624ff64329939684ed62f5293.svg)](https://huggingface.co/SalahAbdoNLP)
- [![](https://huggingface.co/avatars/129d1e86bbaf764b507501f4feb177db.svg)](https://huggingface.co/Aanuoluwapo65)
