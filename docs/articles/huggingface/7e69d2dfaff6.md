---
vendor: huggingface
title: 用 Hugging Face Inference Endpoints 实现强力 ASR + 说话人分离 + 推测解码
original_title: Powerful ASR + diarization + speculative decoding with Hugging Face Inference Endpoints
url: https://huggingface.co/blog/asr-diarization
date: 2024-08-12
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# 用 Hugging Face Inference Endpoints 实现强力 ASR + 说话人分离 + 推测解码

本文由 Sergei Petrov（sergeipetrov）、Vaibhav Srivastav（reach-vb）、Pedro Cuenca（pcuenq）与 Philipp Schmid（philschmid）撰写。

Whisper 是最好的开源语音识别模型之一，也绝对是被最广泛使用的模型。Hugging Face [Inference Endpoints](https://huggingface.co/inference-endpoints/dedicated) 让部署任何 Whisper 模型开箱即用、非常容易。不过，如果你想引入额外功能——比如识别说话人的说话人分离（diarization）流水线，或用于推测解码的辅助生成——事情就会变得棘手。原因在于你需要把 Whisper 与额外模型组合起来，同时仍然对外只暴露一个 API 端点。

我们将用[自定义推理 handler](https://huggingface.co/docs/inference-endpoints/guides/custom_handler)来解决这个挑战，它将在 Inference Endpoints 上实现自动语音识别（ASR）与说话人分离流水线，并支持推测解码。说话人分离流水线的实现借鉴了著名的 [Insanely Fast Whisper](https://github.com/Vaibhavs10/insanely-fast-whisper#insanely-fast-whisper)，并使用 [Pyannote](https://github.com/pyannote/pyannote-audio) 模型做说话人分离。

这同时也是一次展示 Inference Endpoints 有多灵活的示范——你几乎可以在上面托管任何东西。[这里](https://huggingface.co/sergeipetrov/asrdiarization-handler/)是可以跟着做的代码。注意，在端点初始化时，整个仓库会被挂载，因此你的 `handler.py` 可以引用仓库中的其他文件，如果你不愿把所有逻辑塞进单个文件的话。这次我们选择把内容拆分到几个文件以保持整洁：

- `handler.py` 包含初始化与推理代码
- `diarization_utils.py` 包含所有与说话人分离相关的预处理与后处理
- `config.py` 包含 `ModelSettings` 与 `InferenceConfig`。`ModelSettings` 定义流水线将使用哪些模型（不必全部使用），`InferenceConfig` 定义默认的推理参数

***从 [PyTorch 2.2](https://pytorch.org/blog/pytorch2-2/) 开始，SDPA 开箱即用支持 Flash Attention 2，因此我们会用该版本以获得更快的推理。***

## 主要模块

下面是端点内部结构的高层示意图：

[![pipeline_schema](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/asr-diarization/pipeline_schema.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/asr-diarization/pipeline_schema.png)

ASR 与说话人分离流水线的实现是模块化的，以服务更广的用例——说话人分离流水线工作在 ASR 输出之上，如果不需要说话人分离，你可以只用 ASR 部分。对于说话人分离，我们建议使用 [Pyannote 模型](https://huggingface.co/pyannote/speaker-diarization-3.1)，它是目前 SOTA 的开源实现。

我们还会加入推测解码来加速推理。加速的方式是用一个更小更快的模型提出候选生成结果，由更大的模型来验证。关于它如何具体配合 Whisper 工作，推荐阅读[这篇出色的博客](https://huggingface.co/blog/whisper-speculative-decoding)。

推测解码有一些限制：

- 辅助模型（assistant model）至少其解码器部分应与主模型架构相同
- batch size 必须为 1

请务必把以上因素纳入考虑。根据你的生产用例，支持更大的 batch 可能比推测解码更快。如果你不想用辅助模型，只需把配置中的 `assistant_model` 保持为 `None`。

如果你确实要用辅助模型，对 Whisper 而言很好的选择是其[蒸馏版本](https://huggingface.co/distil-whisper)。

## 搭建你自己的端点

最简单的起步方式是用 [repo duplicator](https://huggingface.co/spaces/huggingface-projects/repo_duplicator) 克隆这个[自定义 handler](https://huggingface.co/sergeipetrov/asrdiarization-handler/blob/main/handler.py)仓库。

这是 `handler.py` 中模型加载的部分：

```
from pyannote.audio import Pipeline
from transformers import pipeline, AutoModelForCausalLM

...

self.asr_pipeline = pipeline(
      "automatic-speech-recognition",
      model=model_settings.asr_model,
      torch_dtype=torch_dtype,
      device=device
  )

  self.assistant_model = AutoModelForCausalLM.from_pretrained(
      model_settings.assistant_model,
      torch_dtype=torch_dtype,
      low_cpu_mem_usage=True,
      use_safetensors=True
  ) 
  
  ...

  self.diarization_pipeline = Pipeline.from_pretrained(
      checkpoint_path=model_settings.diarization_model,
      use_auth_token=model_settings.hf_token,
  ) 
  
  ...
```

你可以根据需要定制流水线。`config.py` 文件中的 `ModelSettings` 保存初始化所用参数，定义推理时使用的模型：

```
class ModelSettings(BaseSettings):
    asr_model: str
    assistant_model: Optional[str] = None
    diarization_model: Optional[str] = None
    hf_token: Optional[str] = None
```

这些参数可以通过传入对应名称的环境变量来调整——这对自定义容器和 inference handler 都适用。这是 [Pydantic 的特性](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)。要在构建容器时传入环境变量，你需要通过 API 调用（而非界面）创建端点。

你也可以把模型名硬编码而不通过环境变量传入，但*请注意，说话人分离流水线要求显式传入一个 token（`hf_token`）*。出于安全原因你不被允许硬编码你的 token，这意味着要使用说话人分离模型，你就必须通过 API 调用来创建端点。

提醒一下，所有与说话人分离相关的预处理/后处理工具都在 `diarization_utils.py` 中。

唯一必需的组件是 ASR 模型。可选地，可以指定一个辅助模型用于推测解码，以及一个说话人分离模型用于按说话人切分转写结果。

### 部署到 Inference Endpoints

如果你只需要 ASR 部分，可以在 `config.py` 中指定 `asr_model`/`assistant_model`，然后一键部署：

[![deploy_oneclick](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/asr-diarization/deploy_oneclick.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/asr-diarization/deploy_oneclick.png)

要往托管在 Inference Endpoints 上的容器传环境变量，你需要用[提供的 API](https://api.endpoints.huggingface.cloud/#post-/v2/endpoint/-namespace-)以编程方式创建端点。下面是一个示例调用：

```
body = {
    "compute": {
        "accelerator": "gpu",
        "instanceSize": "medium",
        "instanceType": "g5.2xlarge",
        "scaling": {
            "maxReplica": 1,
            "minReplica": 0
        }
    },
    "model": {
        "framework": "pytorch",
        "image": {
            # a default container
            "huggingface": {
                "env": {
            # this is where a Hub model gets mounted
                    "HF_MODEL_DIR": "/repository", 
                    "DIARIZATION_MODEL": "pyannote/speaker-diarization-3.1",
                    "HF_TOKEN": "<your_token>",
                    "ASR_MODEL": "openai/whisper-large-v3",
                    "ASSISTANT_MODEL": "distil-whisper/distil-large-v3"
                }
            }
        },
        # a model repository on the Hub
        "repository": "sergeipetrov/asrdiarization-handler",
        "task": "custom"
    },
    # the endpoint name
    "name": "asr-diarization-1",
    "provider": {
        "region": "us-east-1",
        "vendor": "aws"
    },
    "type": "private"
}
```

### 何时使用辅助模型

为了让大家更清楚何时使用辅助模型有收益，这里给出用 [k6](https://k6.io/docs/) 做的一次基准测试：

```
# Setup:
# GPU: A10
ASR_MODEL=openai/whisper-large-v3
ASSISTANT_MODEL=distil-whisper/distil-large-v3

# long: 60s audio; short: 8s audio
long_assisted..................: avg=4.15s    min=3.84s    med=3.95s    max=6.88s    p(90)=4.03s    p(95)=4.89s   
long_not_assisted..............: avg=3.48s    min=3.42s    med=3.46s    max=3.71s    p(90)=3.56s    p(95)=3.61s   
short_assisted.................: avg=326.96ms min=313.01ms med=319.41ms max=960.75ms p(90)=325.55ms p(95)=326.07ms
short_not_assisted.............: avg=784.35ms min=736.55ms med=747.67ms max=2s       p(90)=772.9ms  p(95)=774.1ms
```

如你所见，当音频较短时（batch size 为 1），辅助生成带来显著的性能提升。如果音频较长，推理会自动把它切分成多个 batch，而由于我们先前讨论的限制，推测解码反而可能拖慢推理时间。

### 推理参数

所有推理参数都在 `config.py` 中：

```
class InferenceConfig(BaseModel):
    task: Literal["transcribe", "translate"] = "transcribe"
    batch_size: int = 24
    assisted: bool = False
    chunk_length_s: int = 30
    sampling_rate: int = 16000
    language: Optional[str] = None
    num_speakers: Optional[int] = None
    min_speakers: Optional[int] = None
    max_speakers: Optional[int] = None
```

当然，你可以按需增删参数。与说话人数相关的参数会传给说话人分离流水线，其余主要用于 ASR 流水线。`sampling_rate` 指明待处理音频的采样率，用于预处理；`assisted` 标志告诉流水线是否使用推测解码。记住，辅助生成时 `batch_size` 必须设为 1。

### 请求负载

部署完成后，按如下方式把你的音频连同推理参数一起发送给推理端点（Python）：

```
import base64
import requests

API_URL = "<your endpoint URL>"
filepath = "/path/to/audio"

with open(filepath, "rb") as f:
    audio_encoded = base64.b64encode(f.read()).decode("utf-8")

data = {
    "inputs": audio_encoded,
    "parameters": {
        "batch_size": 24
    }
}

resp = requests.post(API_URL, json=data, headers={"Authorization": "Bearer <your token>"})
print(resp.json())
```

这里的 **"parameters"** 字段是一个字典，包含你想相对 `InferenceConfig` 默认值调整的所有参数。注意，未在 `InferenceConfig` 中声明的参数会被忽略。

或者用 [InferenceClient](https://huggingface.co/docs/huggingface_hub/en/package_reference/inference_client#huggingface_hub.InferenceClient)（也有[异步版本](https://huggingface.co/docs/huggingface_hub/en/package_reference/inference_client#huggingface_hub.AsyncInferenceClient)）：

```
from huggingface_hub import InferenceClient

client = InferenceClient(model = "<your endpoint URL>", token="<your token>")

with open("/path/to/audio", "rb") as f:
    audio_encoded = base64.b64encode(f.read()).decode("utf-8")
data = {
    "inputs": audio_encoded,
    "parameters": {
        "batch_size": 24
    }
}

res = client.post(json=data)
```

## 回顾

在这篇博客中，我们讨论了如何用 Hugging Face Inference Endpoints 搭建一个模块化的 ASR + 说话人分离 + 推测解码流水线。我们尽力让它易于配置、可按需调整流水线，而在 Inference Endpoints 上部署向来讲究轻松！很幸运社区公开可用这些优秀的模型与工具，我们在实现中用到了：

- OpenAI 的 [Whisper](https://huggingface.co/openai/whisper-large-v3) 模型家族
- Pyannote 的[说话人分离模型](https://huggingface.co/pyannote/speaker-diarization-3.1)
- [Insanely Fast Whisper 仓库](https://github.com/Vaibhavs10/insanely-fast-whisper/tree/main)，它是主要的灵感来源

还有一个[仓库](https://github.com/plaggy/fast-whisper-server)实现了同样的流水线并带服务端部分（FastAPI+Uvicorn）。如果你想进一步定制或托管到别处，它可能派上用场。
