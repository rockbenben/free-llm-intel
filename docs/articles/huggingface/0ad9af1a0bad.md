---
vendor: huggingface
title: 使用 Hugging Face Transformers 和 AWS Inferentia 加速 BERT 推理
original_title: Accelerate BERT inference with Hugging Face Transformers and AWS Inferentia
url: https://huggingface.co/blog/bert-inferentia-sagemaker
date: 2022-03-16
lang: zh
captured: 2026-10-06
extractor: readability-v1
translator: agent
status: translated
---

# 使用 Hugging Face Transformers 和 AWS Inferentia 加速 BERT 推理

配套 notebook：[sagemaker/18_inferentia_inference](https://github.com/huggingface/notebooks/blob/master/sagemaker/18_inferentia_inference/sagemaker-notebook.ipynb)

[BERT](https://huggingface.co/blog/bert-101) 和 [Transformers](https://huggingface.co/docs/transformers/index) 的采用度还在持续增长。基于 Transformer 的模型如今不仅在自然语言处理上拿到最先进（state-of-the-art）的效果，在[计算机视觉](https://arxiv.org/abs/2010.11929)、[语音](https://arxiv.org/abs/2006.11477)和[时间序列](https://arxiv.org/abs/2002.06103)上同样如此。💬 🖼 🎤 ⏳

各公司正在慢慢从实验和研究阶段走向生产阶段，好把 Transformer 模型用在大规模工作负载上。但默认情况下，与传统机器学习算法相比，BERT 和它的同类算是相当慢、相当大、也相当复杂的模型。如何为 Transformers 和 BERT 提速，是今后一项值得解决的有趣挑战——而且会越来越重要。

AWS 给出的答案是自研一款面向推理工作负载优化的定制机器学习芯片，也就是 [AWS Inferentia](https://aws.amazon.com/machine-learning/inferentia/?nc1=h_ls)。AWS 的说法是，AWS Inferentia *“与同代基于 GPU 的 Amazon EC2 实例相比，单次推理成本最多低 80%，吞吐最多高 2.3 倍。”*

AWS Inferentia 实例相比 GPU 的真正价值，来自每颗设备上可用的多个 Neuron Core。Neuron Core 是 AWS Inferentia 内部的定制加速器，每颗 Inferentia 芯片配有 4 个 Neuron Core。这让你既可以每个核心各加载 1 个模型（追求高吞吐），也可以把 1 个模型铺到全部核心上（追求更低延迟）。

## 教程

在这篇端到端教程里，你将学会如何用 Hugging Face Transformers、Amazon SageMaker 和 AWS Inferentia 为文本分类场景下的 BERT 推理提速。

notebook 在这里：[sagemaker/18_inferentia_inference](https://github.com/huggingface/notebooks/blob/master/sagemaker/18_inferentia_inference/sagemaker-notebook.ipynb)

你将学会：

- [1. 把你的 Hugging Face Transformer 转换为 AWS Neuron](https://huggingface.co/blog/bert-inferentia-sagemaker#1-convert-your-hugging-face-transformer-to-aws-neuron)
- [2. 为 `text-classification` 编写自定义 `inference.py` 脚本](https://huggingface.co/blog/bert-inferentia-sagemaker#2-create-a-custom-inferencepy-script-for-text-classification)
- [3. 创建 neuron 模型并把模型与推理脚本上传到 Amazon S3](https://huggingface.co/blog/bert-inferentia-sagemaker#3-create-and-upload-the-neuron-model-and-inference-script-to-amazon-s3)
- [4. 在 Amazon SageMaker 上部署实时推理 Endpoint](https://huggingface.co/blog/bert-inferentia-sagemaker#4-deploy-a-real-time-inference-endpoint-on-amazon-sagemaker)
- [5. 在 Inferentia 上运行并评估 BERT 的推理性能](https://huggingface.co/blog/bert-inferentia-sagemaker#5-run-and-evaluate-inference-performance-of-bert-on-inferentia)

开始吧！🚀

*如果你要在本地环境里使用 SageMaker（而不是 SageMaker Studio 或 Notebook Instances），就需要一个具备 SageMaker 所需权限的 IAM Role。可以在[这里](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-roles.html)了解更多。*

## 1. 把你的 Hugging Face Transformer 转换为 AWS Neuron

我们会用到 [AWS Inferentia 的 AWS Neuron SDK](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/index.html)。Neuron SDK 包含一个深度学习编译器、一个运行时，以及把 PyTorch 和 TensorFlow 模型转换、编译为 neuron 兼容模型的工具，编译出的模型可以运行在 [EC2 Inf1 实例](https://aws.amazon.com/ec2/instance-types/inf1/)上。

第一步，需要安装 [Neuron SDK](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/neuron-intro/neuron-install-guide.html) 和所需的依赖包。

*提示：如果你用的是 Amazon SageMaker Notebook Instances 或 Studio，可以直接选 `conda_python3` 这个 conda kernel。*

```
# Set Pip repository to point to the Neuron repository
!pip config set global.extra-index-url https://pip.repos.neuron.amazonaws.com

# Install Neuron PyTorch
!pip install torch-neuron==1.9.1.* neuron-cc[tensorflow] sagemaker>=2.79.0 transformers==4.12.3 --upgrade
```

装好 Neuron SDK 后，就可以加载并转换模型了。Neuron 模型是用 `torch_neuron` 的 `trace` 方法来转换的，用法与 `torchscript` 类似。更多信息见我们的[文档](https://huggingface.co/docs/transformers/serialization#torchscript)。

要转换模型，得先从 [hf.co/models](http://hf.co/models) 里选出我们要用在文本分类 pipeline 上的模型。这个例子我们用 [distilbert-base-uncased-finetuned-sst-2-english](https://huggingface.co/distilbert-base-uncased-finetuned-sst-2-english)，换成其他 BERT 类模型也很容易调整。

```
model_id = "distilbert-base-uncased-finetuned-sst-2-english"
```

截至本文写作时，[AWS Neuron SDK 还不支持动态 shape](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/neuron-guide/models/models-inferentia.html#dynamic-shapes)，也就是说编译和推理时的输入尺寸必须是固定的。

说白了，这意味着如果模型是按 batch size 为 1、sequence length 为 16 的输入编译出来的，那它就只能对同样形状的输入做推理。

*在 `t2.medium` 实例上，编译大约需要 3 分钟*

```
import os
import tensorflow  # to workaround a protobuf version conflict issue
import torch
import torch.neuron
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSequenceClassification.from_pretrained(model_id, torchscript=True)

# create dummy input for max length 128
dummy_input = "dummy input which will be padded later"
max_length = 128
embeddings = tokenizer(dummy_input, max_length=max_length, padding="max_length",return_tensors="pt")
neuron_inputs = tuple(embeddings.values())

# compile model with torch.neuron.trace and update config
model_neuron = torch.neuron.trace(model, neuron_inputs)
model.config.update({"traced_sequence_length": max_length})

# save tokenizer, neuron model and config for later use
save_dir="tmp"
os.makedirs("tmp",exist_ok=True)
model_neuron.save(os.path.join(save_dir,"neuron_model.pt"))
tokenizer.save_pretrained(save_dir)
model.config.save_pretrained(save_dir)
```

## 2. 为 `text-classification` 编写自定义 `inference.py` 脚本

[Hugging Face Inference Toolkit](https://github.com/aws/sagemaker-huggingface-inference-toolkit) 在 🤗 Transformers 的 [pipeline 能力](https://huggingface.co/transformers/main_classes/pipelines.html)之上支持零代码部署。这让用户可以在不写推理脚本的情况下部署 Hugging Face transformers（[[示例](https://github.com/huggingface/notebooks/blob/master/sagemaker/11_deploy_model_from_hf_hub/deploy_transformer_model_from_hf_hub.ipynb)]）。

但目前 AWS Inferentia 还不支持这个能力，因此我们需要自己提供一个 `inference.py` 脚本来跑推理。

*如果你希望 Inferentia 也支持零代码部署，请到[论坛](https://discuss.huggingface.co/c/sagemaker/17)上告诉我们。*

要用推理脚本，得先创建 `inference.py`。在我们的例子里，会覆盖 `model_fn` 来加载 neuron 模型，并覆盖 `predict_fn` 来搭建文本分类 pipeline。

想更深入了解 `inference.py` 脚本，可以看看这个[示例](https://github.com/huggingface/notebooks/blob/master/sagemaker/17_custom_inference_script/sagemaker-notebook.ipynb)。它除其他内容之外，也解释了 `model_fn` 和 `predict_fn` 分别是什么。

```
!mkdir code
```

我们设置 `NEURON_RT_NUM_CORES=1`，确保每个 HTTP worker 只用 1 个 Neuron core，以最大化吞吐。

```
%%writefile code/inference.py

import os
from transformers import AutoConfig, AutoTokenizer
import torch
import torch.neuron

# To use one neuron core per worker
os.environ["NEURON_RT_NUM_CORES"] = "1"

# saved weights name
AWS_NEURON_TRACED_WEIGHTS_NAME = "neuron_model.pt"

def model_fn(model_dir):
    # load tokenizer and neuron model from model_dir
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = torch.jit.load(os.path.join(model_dir, AWS_NEURON_TRACED_WEIGHTS_NAME))
    model_config = AutoConfig.from_pretrained(model_dir)

    return model, tokenizer, model_config

def predict_fn(data, model_tokenizer_model_config):
    # destruct model, tokenizer and model config
    model, tokenizer, model_config = model_tokenizer_model_config

    # create embeddings for inputs
    inputs = data.pop("inputs", data)
    embeddings = tokenizer(
        inputs,
        return_tensors="pt",
        max_length=model_config.traced_sequence_length,
        padding="max_length",
        truncation=True,
    )
    # convert to tuple for neuron model
    neuron_inputs = tuple(embeddings.values())

    # run prediciton
    with torch.no_grad():
        predictions = model(*neuron_inputs)[0]
        scores = torch.nn.Softmax(dim=1)(predictions)

    # return dictonary, which will be json serializable
    return [{"label": model_config.id2label[item.argmax().item()], "score": item.max().item()} for item in scores]
```

## 3. 创建 neuron 模型并把模型与推理脚本上传到 Amazon S3

在把 neuron 模型部署到 Amazon SageMaker 之前，需要先用保存到 `tmp/` 里的全部模型产物（比如 `neuron_model.pt`）打一个 `model.tar.gz` 压缩包，并把它上传到 Amazon S3。

为此需要先把权限配置好。

```
import sagemaker
import boto3
sess = sagemaker.Session()
# sagemaker session bucket -> used for uploading data, models and logs
# sagemaker will automatically create this bucket if it not exists
sagemaker_session_bucket=None
if sagemaker_session_bucket is None and sess is not None:
    # set to default bucket if a bucket name is not given
    sagemaker_session_bucket = sess.default_bucket()

try:
    role = sagemaker.get_execution_role()
except ValueError:
    iam = boto3.client('iam')
    role = iam.get_role(RoleName='sagemaker_execution_role')['Role']['Arn']

sess = sagemaker.Session(default_bucket=sagemaker_session_bucket)

print(f"sagemaker role arn: {role}")
print(f"sagemaker bucket: {sess.default_bucket()}")
print(f"sagemaker session region: {sess.boto_region_name}")
```

接下来生成我们的 `model.tar.gz`。`inference.py` 脚本会被放进 `code/` 目录。

```
# copy inference.py into the code/ directory of the model directory.
!cp -r code/ tmp/code/
# create a model.tar.gz archive with all the model artifacts and the inference.py script.
%cd tmp
!tar zcvf model.tar.gz *
%cd ..
```

现在就可以用 `sagemaker` 把 `model.tar.gz` 上传到会话的 S3 bucket。

```
from sagemaker.s3 import S3Uploader

# create s3 uri
s3_model_path = f"s3://{sess.default_bucket()}/{model_id}"

# upload model.tar.gz
s3_model_uri = S3Uploader.upload(local_path="tmp/model.tar.gz",desired_s3_uri=s3_model_path)
print(f"model artifcats uploaded to {s3_model_uri}")
```

## 4. 在 Amazon SageMaker 上部署实时推理 Endpoint

`model.tar.gz` 上传到 Amazon S3 之后，就可以创建一个自定义的 `HuggingfaceModel`。这个类用来在 Amazon SageMaker 上创建并部署我们的实时推理 endpoint。

```
from sagemaker.huggingface.model import HuggingFaceModel

# create Hugging Face Model Class
huggingface_model = HuggingFaceModel(
   model_data=s3_model_uri,       # path to your model and script
   role=role,                    # iam role with permissions to create an Endpoint
   transformers_version="4.12",  # transformers version used
   pytorch_version="1.9",        # pytorch version used
   py_version='py37',            # python version used
)

# Let SageMaker know that we've already compiled the model via neuron-cc
huggingface_model._is_compiled_model = True

# deploy the endpoint endpoint
predictor = huggingface_model.deploy(
    initial_instance_count=1,      # number of instances
    instance_type="ml.inf1.xlarge" # AWS Inferentia Instance
)
```

## 5. 在 Inferentia 上运行并评估 BERT 的推理性能

`.deploy()` 会返回一个 `HuggingFacePredictor` 对象，可以用它来发起推理请求。

```
data = {
  "inputs": "the mesmerizing performances of the leads keep the film grounded and keep the audience riveted .",
}

res = predictor.predict(data=data)
res
```

我们已经把 neuron 编译后的 BERT 部署到了 Amazon SageMaker 上的 AWS Inferentia。现在来测一下它的性能。作为一次简单的压测，我们循环向 endpoint 发送 10,000 个同步请求。

```
# send 10000 requests
for i in range(10000):
    resp = predictor.predict(
        data={"inputs": "it 's a charming and often affecting journey ."}
    )
```

到 CloudWatch 里看看性能表现。

```
print(f"https://console.aws.amazon.com/cloudwatch/home?region={sess.boto_region_name}#metricsV2:graph=~(metrics~(~(~'AWS*2fSageMaker~'ModelLatency~'EndpointName~'{predictor.endpoint_name}~'VariantName~'AllTraffic))~view~'timeSeries~stacked~false~region~'{sess.boto_region_name}~start~'-PT5M~end~'P0D~stat~'Average~period~30);query=~'*7bAWS*2fSageMaker*2cEndpointName*2cVariantName*7d*20{predictor.endpoint_name}")
```

在 sequence length 为 128 时，我们的 BERT 模型平均延迟是 `5-6ms`。

图 1. 模型延迟

### 删除模型和 endpoint

为了清理资源，我们可以把模型和 endpoint 都删掉。

```
predictor.delete_model()
predictor.delete_endpoint()
```

## 结论

我们成功把一个原始的 Hugging Face Transformers 模型编译成了兼容 AWS Inferentia 的 Neuron 模型，随后用全新的 Hugging Face Inference DLC 把 Neuron 模型部署到了 Amazon SageMaker。在每个 neuron core 上我们做到了 `5-6ms` 的延迟：论延迟比 CPU 更快，又因为我们并行跑了 4 个模型，吞吐也比 GPU 更高。

如果你或你的公司目前正把 BERT 类 Transformer 用在 encoder 任务上（text-classification、token-classification、question-answering 等），并且延迟能满足要求，那就该考虑切换到 AWS Inferentia。这不仅能省下成本，还能提升模型的效率和性能。

我们计划今后再做一份关于 transformers 成本效益的更详细案例研究，敬请期待！

另外，想进一步了解如何为 transformers 提速，也推荐看看 Hugging Face 的 [optimum](https://github.com/huggingface/optimum)。

感谢阅读！如果有任何问题，欢迎通过 [Github](https://github.com/huggingface/transformers) 或[论坛](https://discuss.huggingface.co/c/sagemaker/17) 联系我。你也可以在 [Twitter](https://twitter.com/_philschmid) 或 [LinkedIn](https://www.linkedin.com/in/philipp-schmid-a6a2bb196/) 上找到我。
