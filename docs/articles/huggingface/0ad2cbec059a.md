---
vendor: huggingface
title: Hugging Face Text Generation Inference 现已支持 AWS Inferentia2
original_title: Hugging Face Text Generation Inference available for AWS Inferentia2
url: https://huggingface.co/blog/text-generation-inference-on-inferentia2
date: 2024-10-16
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: 29d9aac7e8d9
---

# Hugging Face Text Generation Inference 现已支持 AWS Inferentia2

我们很高兴地宣布，Hugging Face Text Generation Inference（TGI）在 AWS Inferentia2 和 Amazon SageMaker 上正式可用（general availability）。

**[Text Generation Inference (TGI)](https://github.com/huggingface/text-generation-inference)** 是专为大规模部署和服务大语言模型（LLM）生产负载而构建的方案。TGI 使用张量并行（Tensor Parallelism）和连续批处理（continuous batching），为 Llama、Mistral 等最流行的开放 LLM 提供高性能文本生成。Grammarly、Uber、Deutsche Telekom 等众多公司都在生产中使用 Text Generation Inference。

TGI 与 Amazon SageMaker、AWS Inferentia2 的结合，为构建生产级 LLM 应用提供了一个强有力的方案，也是 GPU 的可行替代。这一无缝集成带来简单轻松的模型部署与维护，让 LLM 在广泛的生产用例中更易用、更可扩展。

借助 SageMaker 上全新的 TGI for AWS Inferentia2，AWS 客户可以享受到与 [HuggingChat](https://hf.co/chat)、[OpenAssistant](https://open-assistant.io/) 以及 Hugging Face Hub 上 LLM Serverless Endpoints 同款的、高并发低延迟技术。

## 在 Amazon SageMaker 上用 AWS Inferentia2 部署 Zephyr 7B

本教程展示用 Amazon SageMaker 在 AWS Inferentia2 上部署最先进 LLM（如 Zephyr 7B）有多简单。Zephyr 是 [mistralai/Mistral-7B-v0.1](https://huggingface.co/mistralai/Mistral-7B-v0.1) 的 7B 微调版本，按照[技术报告](https://arxiv.org/abs/2310.16944)的详述，用[直接偏好优化（DPO）](https://arxiv.org/abs/2305.18290)在公开数据与合成数据的混合集上训练。模型以 Apache 2.0 许可证发布，保证广泛可用。

我们将演示如何：

- 搭建开发环境
- 获取 TGI Neuronx 镜像
- 把 Zephyr 7B 部署到 Amazon SageMaker
- 运行推理并与模型对话

开始吧。

### 1. 搭建开发环境

我们将使用 `sagemaker` Python SDK 把 Zephyr 部署到 Amazon SageMaker，因此需要先配置好 AWS 账号并安装 `sagemaker` Python SDK。

```
!pip install transformers "sagemaker>=2.206.0" --upgrade --quiet
```

如果你要在本地环境使用 SageMaker，需要一个具备 SageMaker 所需权限的 IAM Role。更多说明见[这里](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-roles.html)。

```
import sagemaker
import boto3
sess = sagemaker.Session()
# sagemaker session bucket -> used for uploading data, models and logs
# sagemaker will automatically create this bucket if it doesn't exist
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
print(f"sagemaker session region: {sess.boto_region_name}")
```

### 2. 获取 TGI Neuronx 镜像

全新的 Hugging Face TGI Neuronx DLC 可以在 AWS Inferentia2 上运行推理。你可以用 `sagemaker` SDK 的 `get_huggingface_llm_image_uri` 方法，根据你想要的 `backend`、`session`、`region` 和 `version` 获取对应的 Hugging Face TGI Neuronx DLC URI。所有可用版本见[这里](https://github.com/aws/deep-learning-containers/releases?q=tgi+AND+neuronx&expanded=true)。

*注：写这篇博客时，最新版 Hugging Face LLM DLC 还不能通过 `get_huggingface_llm_image_uri` 方法获取。这里直接使用容器原始 URI。*

```
from sagemaker.huggingface import get_huggingface_llm_image_uri

# retrieve the llm image uri
llm_image = get_huggingface_llm_image_uri(
  "huggingface-neuronx",
  version="0.0.20"
)

# print ecr image uri
print(f"llm image uri: {llm_image}")
```

### 4. 把 Zephyr 7B 部署到 Amazon SageMaker

Inferentia2 上的 Text Generation Inference（TGI）支持包括 Llama、Mistral 在内的流行开放 LLM。完整的受支持模型列表（文本生成）见[这里](https://huggingface.co/docs/optimum-neuron/package_reference/export#supported-architectures)。

**为 Inferentia2 编译 LLM**

写作本文时，[AWS Inferentia2 尚不支持推理时的动态 shape](https://awsdocs-neuron.readthedocs-hosted.com/en/v2.6.0/general/arch/neuron-features/dynamic-shapes.html#neuron-dynamic-shapes)，也就是说我们必须提前指定序列长度和批大小。为了让客户更轻松地发挥 Inferentia2 的全部实力，我们创建了 [neuron 模型缓存](https://huggingface.co/docs/optimum-neuron/guides/cache_system)，内含最流行 LLM 的预编译配置。一个缓存配置由模型架构（Mistral）、模型规模（7B）、neuron 版本（2.16）、Inferentia 核心数（2）、批大小（2）和序列长度（2048）共同定义。

这意味着我们不必自己编译模型，直接用缓存里的预编译版本即可。例如 [mistralai/Mistral-7B-v0.1](https://huggingface.co/mistralai/Mistral-7B-v0.1) 和 [HuggingFaceH4/zephyr-7b-beta](https://huggingface.co/HuggingFaceH4/zephyr-7b-beta)。已编译/缓存的配置可以在 [Hugging Face Hub](https://huggingface.co/aws-neuron/optimum-neuron-cache/tree/main/inference-cache-config) 上找到。如果你想要的配置还没缓存，可以自己用 [Optimum CLI](https://huggingface.co/docs/optimum-neuron/cli/compile) 编译，或者在[缓存仓库](https://huggingface.co/aws-neuron/optimum-neuron-cache/discussions)提请求。

本文中我们在 `inf2.8xlarge` 实例上用以下命令和参数重新编译了 `HuggingFaceH4/zephyr-7b-beta`，并推送到 Hub 的 [aws-neuron/zephyr-7b-seqlen-2048-bs-4-cores-2](https://huggingface.co/aws-neuron/zephyr-7b-seqlen-2048-bs-4-cores-2)。

```
# compile model with optimum for batch size 4 and sequence length 2048
optimum-cli export neuron -m HuggingFaceH4/zephyr-7b-beta --batch_size 4 --sequence_length 2048 --num_cores 2 --auto_cast_type bf16 ./zephyr-7b-beta-neuron
# push model to hub [repo_id] [local_path] [path_in_repo]
huggingface-cli upload  aws-neuron/zephyr-7b-seqlen-2048-bs-4 ./zephyr-7b-beta-neuron ./ --exclude "checkpoint/**"
# Move tokenizer to neuron model repository
python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('HuggingFaceH4/zephyr-7b-beta').push_to_hub('aws-neuron/zephyr-7b-seqlen-2048-bs-4')"
```

如果你要编译的 LLM 配置尚未缓存，可能需要花到 45 分钟。

**部署 TGI Neuronx Endpoint**

在把模型部署到 Amazon SageMaker 之前，要先定义 TGI Neuronx 端点配置，确保定义了以下额外参数：

- `HF_NUM_CORES`：编译时使用的 Neuron 核心数。
- `HF_BATCH_SIZE`：编译模型时使用的批大小。
- `HF_SEQUENCE_LENGTH`：编译模型时使用的序列长度。
- `HF_AUTO_CAST_TYPE`：编译模型时使用的自动转换类型。

还需要定义传统的 TGI 参数：

- `HF_MODEL_ID`：Hugging Face 模型 ID。
- `HF_TOKEN`：访问 gated 模型用的 Hugging Face API token。
- `MAX_BATCH_SIZE`：模型能处理的最大批大小，等于编译时使用的批大小。
- `MAX_INPUT_LENGTH`：模型能处理的最大输入长度。
- `MAX_TOTAL_TOKENS`：模型能生成的 token 总量上限，等于编译时使用的序列长度。

```
import json
from sagemaker.huggingface import HuggingFaceModel

# sagemaker config & model config
instance_type = "ml.inf2.8xlarge"
health_check_timeout = 1800

# Define Model and Endpoint configuration parameter
config = {
    "HF_MODEL_ID": "HuggingFaceH4/zephyr-7b-beta",
    "HF_NUM_CORES": "2",
    "HF_BATCH_SIZE": "4",
    "HF_SEQUENCE_LENGTH": "2048",
    "HF_AUTO_CAST_TYPE": "bf16",  
    "MAX_BATCH_SIZE": "4",
    "MAX_INPUT_LENGTH": "1512",
    "MAX_TOTAL_TOKENS": "2048",
}

# create HuggingFaceModel with the image uri
llm_model = HuggingFaceModel(
  role=role,
  image_uri=llm_image,
  env=config
)
```

创建好 `HuggingFaceModel` 之后，用 `deploy` 方法把它部署到 Amazon SageMaker。我们将以 `ml.inf2.8xlarge` 实例类型部署。

```
# Deploy model to an endpoint
llm = llm_model.deploy(
  initial_instance_count=1,
  instance_type=instance_type,
  container_startup_health_check_timeout=health_check_timeout,
)
```

SageMaker 会创建端点并把模型部署上去，可能需要 10-15 分钟。

### 5. 运行推理并与模型对话

端点部署完成后，用 `predictor` 的 `predict` 方法对它做推理。你可以把不同参数放进 payload 的 `parameters` 属性来影响生成。支持的参数见[这里](https://www.philschmid.de/sagemaker-llama-llm#5-run-inference-and-chat-with-the-model)，或 TGI 在 [swagger 文档](https://huggingface.github.io/text-generation-inference/)中的开放 API 规范。

`HuggingFaceH4/zephyr-7b-beta` 是一个对话模型，意味着我们可以用如下提示词结构与它对话：

```
<|system|>\nYou are a friendly.</s>\n<|user|>\nInstruction</s>\n<|assistant|>\n
```

手动拼提示词容易出错，所以可以用 tokenizer 的 `apply_chat_template` 方法来帮忙。它接受大家熟悉的 OpenAI 格式的 `messages` 字典，转换成模型正确的格式。我们看看 Zephyr 是否知道一些 AWS 的趣事。

```
from transformers import AutoTokenizer

# load the tokenizer
tokenizer = AutoTokenizer.from_pretrained("aws-neuron/zephyr-7b-seqlen-2048-bs-4-cores-2")

# Prompt to generate
messages = [
    {"role": "system", "content": "You are the AWS expert"},
    {"role": "user", "content": "Can you tell me an interesting fact about AWS?"},
]
prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

# Generation arguments
payload = {
    "do_sample": True,
    "top_p": 0.6,
    "temperature": 0.9,
    "top_k": 50,
    "max_new_tokens": 256,
    "repetition_penalty": 1.03,
    "return_full_text": False,
    "stop": ["</s>"]
}
chat = llm.predict({"inputs":prompt, "parameters":payload})

print(chat[0]["generated_text"][len(prompt):])
# Sure, here's an interesting fact about AWS: As of 2021, AWS has more than 200 services in its portfolio, ranging from compute power and storage to databases,
```

太好了，我们成功把 Zephyr 部署到了 Inferentia2 的 Amazon SageMaker 上，还和它聊上了。

### 6. 清理

清理时删除模型和端点即可。

```
llm.delete_model()
llm.delete_endpoint()
```

## 总结

Hugging Face Text Generation Inference（TGI）与 AWS Inferentia2、Amazon SageMaker 的集成，为部署大语言模型（LLM）提供了高性价比的替代方案。

我们正在积极支持更多模型、简化编译流程、打磨缓存系统。

感谢阅读！如有问题，欢迎通过 [Twitter](https://twitter.com/_philschmid) 或 [LinkedIn](https://www.linkedin.com/in/philipp-schmid-a6a2bb196/) 联系我。
