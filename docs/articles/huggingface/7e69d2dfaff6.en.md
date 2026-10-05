---
vendor: huggingface
title: Powerful ASR + diarization + speculative decoding with Hugging Face Inference Endpoints
original_title: Powerful ASR + diarization + speculative decoding with Hugging Face Inference Endpoints
url: https://huggingface.co/blog/asr-diarization
date: 2024-08-12
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 27e361a12c39
---

Back to Articles

# Powerful ASR + diarization + speculative decoding with Hugging Face Inference Endpoints

Published
					May 1, 2024

Update on GitHub

Upvote

83

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/62990c4743898d5a4f7eacb4/gIRotoJl4rHBVC0lU1n18.png)](https://huggingface.co/ugurcanvurgun)
- [![](https://huggingface.co/avatars/b2725bb163fa15d6c5856121780d52eb.svg)](https://huggingface.co/Csplk)
- [![](https://huggingface.co/avatars/253086bb97bfb344eef07076c103c0fb.svg)](https://huggingface.co/blaklion)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63107b18e87051f3e3e0f598/R9onir4Y0MZuq1jEWCZ2-.jpeg)](https://huggingface.co/ucyang)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1655385361868-61b85ce86eb1f2c5e6233736.jpeg)](https://huggingface.co/reach-vb)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/62fd2359085065dcf869c657/TXavf9PzwzQFg33rrwxeL.png)](https://huggingface.co/charlescai2016)

Sergei Petrov

sergeipetrov

Vaibhav Srivastav

reach-vb

Pedro Cuenca

pcuenq

Philipp Schmid

philschmid

This article is also available in Chinese [简体中文](https://huggingface.co/blog/zh/asr-diarization).

Whisper is one of the best open source speech recognition models and definitely the one most widely used. Hugging Face [Inference Endpoints](https://huggingface.co/inference-endpoints/dedicated) make it very easy to deploy any Whisper model out of the box. However, if you’d like to introduce additional features, like a diarization pipeline to identify speakers, or assisted generation for speculative decoding, things get trickier. The reason is that you need to combine Whisper with additional models, while still exposing a single API endpoint.

We'll solve this challenge using a [custom inference handler](https://huggingface.co/docs/inference-endpoints/guides/custom_handler), which will implement the Automatic Speech Recognition (ASR) and Diarization pipeline on Inference Endpoints, as well as supporting speculative decoding. The implementation of the diarization pipeline is inspired by the famous [Insanely Fast Whisper](https://github.com/Vaibhavs10/insanely-fast-whisper#insanely-fast-whisper), and it uses a [Pyannote](https://github.com/pyannote/pyannote-audio) model for diarization.

This will also be a demonstration of how flexible Inference Endpoints are and that you can host pretty much anything there. [Here](https://huggingface.co/sergeipetrov/asrdiarization-handler/) is the code to follow along. Note that during initialization of the endpoint, the whole repository gets mounted, so your `handler.py` can refer to other files in your repository if you prefer not to have all the logic in a single file. In this case, we decided to separate things into several files to keep things clean:

- `handler.py` contains initialization and inference code
- `diarization_utils.py` has all the diarization-related pre- and post-processing
- `config.py` has `ModelSettings` and `InferenceConfig`. `ModelSettings` define which models will be utilized in the pipeline (you don't have to use all of them), and `InferenceConfig` defines the default inference parameters

***Starting with [Pytorch 2.2](https://pytorch.org/blog/pytorch2-2/), SDPA supports Flash Attention 2 out-of-the-box, so we'll use that version for faster inference.***

## The main modules

This is a high-level diagram of what the endpoint looks like under the hood:

[![pipeline_schema](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/asr-diarization/pipeline_schema.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/asr-diarization/pipeline_schema.png)

The implementation of ASR and diarization pipelines is modularized to cater to a wider range of use cases - the diarization pipeline operates on top of ASR outputs, and you can use only the ASR part if diarization is not needed. For diarization, we propose using the [Pyannote model](https://huggingface.co/pyannote/speaker-diarization-3.1), currently a SOTA open source implementation.

We’ll also add speculative decoding as a way to speed up inference. The speedup is achieved by using a smaller and faster model to suggest generations that are validated by the larger model. Learn more about how it works with Whisper specifically in [this great blog post](https://huggingface.co/blog/whisper-speculative-decoding).

Speculative decoding comes with restrictions:

- at least the decoder part of an assistant model should have the same architecture as that of the main model
- the batch size much be 1

Make sure to take the above into account. Depending on your production use case, supporting larger batches can be faster than speculative decoding. If you don't want to use an assistant model, just keep the `assistant_model` in the configuration as `None`.

If you do use an assistant model, a great choice for Whisper is a [distilled version](https://huggingface.co/distil-whisper).

## Set up your own endpoint

The easiest way to start is to clone the [custom handler](https://huggingface.co/sergeipetrov/asrdiarization-handler/blob/main/handler.py) repository using the [repo duplicator](https://huggingface.co/spaces/huggingface-projects/repo_duplicator).

Here is the model loading piece from the `handler.py`:

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

You can customize the pipeline based on your needs. `ModelSettings`, in the `config.py` file, holds the parameters used for initialization, defining the models to use during inference:

```
class ModelSettings(BaseSettings):
    asr_model: str
    assistant_model: Optional[str] = None
    diarization_model: Optional[str] = None
    hf_token: Optional[str] = None
```

The parameters can be adjusted by passing environment variables with corresponding names - this works both with a custom container and an inference handler. It’s a [Pydantic feature](https://docs.pydantic.dev/latest/concepts/pydantic_settings/). To pass environment variables to a container during build time you’ll have to create an endpoint via an API call (not via the interface).

You could hardcode model names instead of passing them as environment variables, but *note that the diarization pipeline requires a token to be passed explicitly (`hf_token`).* You are not allowed to hardcode your token for security reasons, which means you will have to create an endpoint via an API call in order to use a diarization model.

As a reminder, all the diarization-related pre- and postprocessing utils are in `diarization_utils.py`

The only required component is an ASR model. Optionally, an assistant model can be specified to be used for speculative decoding, and a diarization model can be used to partition a transcription by speakers.

### Deploy on Inference Endpoints

If you only need the ASR part you could specify `asr_model`/`assistant_model` in the `config.py` and deploy with a click of a button:

[![deploy_oneclick](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/asr-diarization/deploy_oneclick.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/asr-diarization/deploy_oneclick.png)

To pass environment variables to containers hosted on Inference Endpoints you’ll need to create an endpoint programmatically using the [provided API](https://api.endpoints.huggingface.cloud/#post-/v2/endpoint/-namespace-). Below is an example call:

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

### When to use an assistant model

To give a better idea on when using an assistant model is beneficial, here's a benchmark performed with [k6](https://k6.io/docs/):

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

As you can see, assisted generation gives dramatic performance gains when an audio is short (batch size is 1). If an audio is long, inference will automatically chunk it into batches, and speculative decoding may hurt inference time because of the limitations we discussed before.

### Inference parameters

All the inference parameters are in `config.py`:

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

Of course, you can add or remove parameters as needed. The parameters related to the number of speakers are passed to a diarization pipeline, while all the others are mostly for the ASR pipeline. `sampling_rate` indicates the sampling rate of the audio to process and is used for preprocessing; the `assisted` flag tells the pipeline whether to use speculative decoding. Remember that for assisted generation the `batch_size` must be set to 1.

### Payload

Once deployed, send your audio along with the inference parameters to your inference endpoint, like this (in Python):

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

Here the **"parameters"** field is a dictionary that contains all the parameters you'd like to adjust from the `InferenceConfig`. Note that parameters not specified in the `InferenceConfig` will be ignored.

Or with [InferenceClient](https://huggingface.co/docs/huggingface_hub/en/package_reference/inference_client#huggingface_hub.InferenceClient) (there is also an [async version](https://huggingface.co/docs/huggingface_hub/en/package_reference/inference_client#huggingface_hub.AsyncInferenceClient)):

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

## Recap

In this blog, we discussed how to set up a modularized ASR + diarization + speculative decoding pipeline with Hugging Face Inference Endpoints. We did our best to make it easy to configure and adjust the pipeline as needed, and deployment with Inference Endpoints is always a piece of cake! We are lucky to have great models and tools openly available to the community that we used in the implementation:

- A family of [Whisper](https://huggingface.co/openai/whisper-large-v3) models by OpenAI
- A [diarization model](https://huggingface.co/pyannote/speaker-diarization-3.1) by Pyannote
- The [Insanely Fast Whisper repository](https://github.com/Vaibhavs10/insanely-fast-whisper/tree/main), which was the main source of inspiration

There is a [repo](https://github.com/plaggy/fast-whisper-server) that implements the same pipeline along with the server part (FastAPI+Uvicorn). It may come in handy if you'd like to customize it even further or host somewhere else.

## Models mentioned in this article 3

## Spaces mentioned in this article 1

More Articles from our Blog

guide

cloud

inference

## Blazingly fast whisper transcriptions with Inference Endpoints

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1583858935715-5e67c47c100906368940747e.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1654278567459-626a9bfa03e2e2796f24ca11.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/654bcb6fae75d15300d48205/T4L1RZUgCZgdik4ZhEWCq.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1655385361868-61b85ce86eb1f2c5e6233736.jpeg)
- +2

83

May 13, 2025

audio

speech-to-speech

inference

## Deploying Speech-to-Speech on Hugging Face

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/65d66b494bbd0d92b641cdbb/6-7dm7B-JxcoS1QlCPdMN.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/638eb5f949de7ae552dd6211/mJkQJGpn9tXV37N2VLFCh.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/YARBj-PT4QW3Mys2UzGco.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/660bc459d81d6112496f30f8/jMrpAckFyg-_iHMI7sn2h.jpeg)

46

October 22, 2024

### Community

NAVEENRAJ007

Apr 25, 2025

hi naveen how are you

tetttssts

Apr 27, 2025

Hello

tetttssts

Apr 27, 2025

Tffg

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fasr-diarization) or [log in](https://huggingface.co/login?next=%2Fblog%2Fasr-diarization) to comment

Upvote

83

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/62990c4743898d5a4f7eacb4/gIRotoJl4rHBVC0lU1n18.png)](https://huggingface.co/ugurcanvurgun)
- [![](https://huggingface.co/avatars/b2725bb163fa15d6c5856121780d52eb.svg)](https://huggingface.co/Csplk)
- [![](https://huggingface.co/avatars/253086bb97bfb344eef07076c103c0fb.svg)](https://huggingface.co/blaklion)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63107b18e87051f3e3e0f598/R9onir4Y0MZuq1jEWCZ2-.jpeg)](https://huggingface.co/ucyang)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1655385361868-61b85ce86eb1f2c5e6233736.jpeg)](https://huggingface.co/reach-vb)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/62fd2359085065dcf869c657/TXavf9PzwzQFg33rrwxeL.png)](https://huggingface.co/charlescai2016)
- [![](https://huggingface.co/avatars/86194456844c7b2b5389de36cb258472.svg)](https://huggingface.co/RichardForests)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1639773384591-5f353bb37e58354338621655.jpeg)](https://huggingface.co/nbroad)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64c1c77c245c55a21c6f5a13/d9zlSksf3TxWpBbb-r0fd.jpeg)](https://huggingface.co/Reza2kn)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/5f17f0a0925b9863e28ad517/78BR8GuQiX9a8wbbRlSAC.webp)](https://huggingface.co/victor)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63c1c9d0c58fcfeac189c527/0RDPL8XCqlo164CHsuBT8.jpeg)](https://huggingface.co/simonweniger)
- [![](https://huggingface.co/avatars/f02b5b457f818e87b3ab8c1341b12062.svg)](https://huggingface.co/ClayFace)

## Models mentioned in this article 3

## Spaces mentioned in this article 1
