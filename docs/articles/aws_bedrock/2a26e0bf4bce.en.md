---
vendor: aws_bedrock
title: Deploying real-time personalized speech with Qwen3-TTS on Amazon SageMaker AI
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/deploying-real-time-personalized-speech-with-qwen3-tts-on-amazon-sagemaker-ai
date: 2026-09-25
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: db45012c1083
---

## [Artificial Intelligence](https://aws.amazon.com/blogs/machine-learning/)

# Deploying real-time personalized speech with Qwen3-TTS on Amazon SageMaker AI

With voice cloning, you can generate new speech in a target speaker’s voice from a short reference recording, without retraining a model. You can now deploy the publicly available [Qwen3-TTS-12Hz-1.7B-Base](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base) text-to-speech model from [Amazon SageMaker JumpStart](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-jumpstart.html) to a fully managed, real-time inference endpoint.

Voice cloning reproduces the vocal identity of a specific speaker. Start with a short recording of the speaker and its transcript. Then supply the new text to synthesize. The model speaks that text in the reference speaker’s voice, without retraining. Media teams, educators, and application developers can use this capability to create personalized voice experiences and localize multilingual content. They can also support accessible communication and preserve a speaker’s identity across languages.

With a self-hosted, publicly available voice cloning model, you control cost and keep audio data within your AWS environment. You can also adapt the model to your domain. With [Amazon SageMaker AI](https://aws.amazon.com/sagemaker/ai/), you can run the model on a fully managed real-time endpoint and handle infrastructure provisioning, health monitoring, and automatic scaling. You don’t manage the underlying GPU servers.

This post shows how to deploy Qwen3-TTS-12Hz-1.7B-Base from Amazon SageMaker JumpStart using the [Amazon SageMaker Python SDK](https://github.com/aws/sagemaker-python-sdk), and how to invoke the resulting endpoint to clone a voice from a reference clip. It also covers the configuration settings that make this deployment work in practice, along with the Amazon CloudWatch metrics you can use to monitor and right-size the endpoint.

## What is Qwen3-TTS

Qwen3-TTS is a publicly available text-to-speech model family developed by the Qwen team at Alibaba Cloud. It covers 10 languages: Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, and Italian. The models use the Qwen3-TTS-Tokenizer-12Hz speech tokenizer and support streaming generation for low-latency, interactive scenarios.

This post uses the Base variant, [Qwen3-TTS-12Hz-1.7B-Base](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base). It performs voice cloning from only a few seconds of user audio. It can also serve as a base for fine-tuning. For voice cloning, the model takes a reference audio clip and its transcript. It captures the speaker’s vocal characteristics, such as timbre, pitch, and cadence, and applies them to new text. This differs from the [CustomVoice](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice) variant, which generates speech from a fixed set of predefined speakers rather than a user-supplied reference.

The model also supports cross-lingual cloning: You can capture a voice from a reference in one language and generate speech in another while preserving the speaker’s vocal identity.

Qwen3-TTS-12Hz-1.7B-Base is available in Amazon SageMaker JumpStart alongside Qwen3-TTS-12Hz-1.7B-CustomVoice and Qwen3-ASR-1.7B. With these JumpStart options, you can use the streamlined deployment shown in this post.

## Voice cloning

With voice cloning, applications can reproduce the vocal identity of a chosen speaker from a reference recording, rather than being limited to a fixed set of predefined voices. This supports a range of use cases across media, customer engagement, education, and conversational AI.

### Benefits

Key benefits of this deployment approach include:

- **Personalization at scale:** You can produce speech in a target voice from a short sample, without collecting large training datasets.
- **Multilingual reach:** You can use a voice captured in one language to generate speech in another while preserving identity.
- **Cost efficiency:** Deployments align cost with compute usage instead of per-character API pricing.
- **Data control:** Data stays within your AWS account and the Amazon SageMaker endpoint you manage.

### Application use cases

Common applications for voice cloning include:

- **Content localization:** You can translate content into multiple languages while preserving the original speaker’s voice.
- **Customer experience:** Contact-center and virtual-assistant responses can use a consistent brand voice.
- **E-learning and audiobooks:** You can present long-form content in a specific instructor’s or author’s voice.
- **Creative prototyping:** You can test dialogue and voiceovers before studio production.
- **Real-time conversational AI:** Streaming speech recognition and low-latency synthesis can support interactive voice agents.

## Solution overview

This solution deploys Qwen3-TTS-12Hz-1.7B-Base from Amazon SageMaker JumpStart to a real-time endpoint. JumpStart provides the model artifacts and a pre-built serving container, so you don’t write a custom inference handler. You construct a `JumpStartModel` object, call its `deploy` method, and invoke the resulting endpoint with the Amazon SageMaker runtime client.

The JumpStart container serves the model to generate 24 kHz audio output from text input. This stage design affects how you size GPU memory, as the following section explains.

### Architecture

The following diagram shows the real-time inference architecture for the deployment.

Figure 1: Real-time voice cloning architecture on Amazon SageMaker AI

The deployment follows the standard Amazon SageMaker AI real-time inference pattern:

- The client sends an HTTP request to the Amazon SageMaker AI endpoint. The request body contains the target text, the base64-encoded reference audio, and the reference audio’s transcript.
- Amazon SageMaker AI routes the request to the vLLM-Omni serving container running on a GPU instance.
- The talker stage generates speech tokens from the text and reference voice. The code2wav stage renders them into a waveform.
- The response returns to the client as audio in the requested format (this post uses WAV).

### Prerequisites

Before you begin, confirm that you have the following resources and permissions:

- An AWS account with access to [Amazon SageMaker AI](https://docs.aws.amazon.com/sagemaker/) and [Amazon Simple Storage Service (Amazon S3)](https://aws.amazon.com/s3/).
- An [AWS Identity and Access Management (IAM)](https://docs.aws.amazon.com/iam/) identity with permissions to create Amazon SageMaker models, endpoint configurations, and endpoints, and to invoke the endpoint.
- An [Amazon SageMaker Studio](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-updated.html) environment, a notebook instance, or a local environment with the [Amazon SageMaker Python SDK](https://sagemaker.readthedocs.io/) installed.
- Sufficient service quota for a supported GPU instance. This walkthrough uses `ml.g6.4xlarge` (1x NVIDIA L4 GPU, 24 GB), which is sufficient for the 1.7B model.
- A short reference audio clip of the target speaker (a few seconds is sufficient) and a transcript of the words spoken in it.

### Step 1: Deploy the model from JumpStart

Construct a `JumpStartModel` with the model ID and deploy it. The GPU memory override is the most important setting for this deployment. The following section explains how to configure it. Before running the following code, replace `<sagemaker-execution-role-arn>` with the ARN of the IAM execution role that Amazon SageMaker AI uses to deploy the model.

```
from sagemaker.jumpstart.model import JumpStartModel

model = JumpStartModel(
    model_id="huggingface-ttsvoiceclone-qwen3-tts-12hz-1-7b-base",
    model_version="1.0.1", # pin for reproducibility
    instance_type="ml.g6.4xlarge", # 24 GB L4
    role="<sagemaker-execution-role-arn>",
    env={"SM_VLLM_GPU_MEMORY_UTILIZATION": "0.45"}, # required (see the following section)
)

predictor = model.deploy(
    endpoint_name="qwen3-tts-voice-clone",
    accept_eula=True,
)
```

The endpoint takes several minutes to reach the `InService` status while the container loads the model onto the GPU. You can monitor the endpoint status in the Amazon SageMaker AI console or by calling the `describe_endpoint` API.

### Step 2: Size GPU memory correctly

As described earlier, the model runs as two stages (talker and code2wav) on the same GPU. vLLM reserves GPU memory up front based on `gpu_memory_utilization`, the fraction of GPU memory a stage can claim. Both stages share one GPU. To avoid out-of-memory errors during startup, keep their combined reservation within the GPU’s capacity.

Set the value so the two stages together fit comfortably. With one shared setting applied equally to both stages, `0.45` works well (0.45 + 0.45 = 0.90, leaving a approximately 10 percent buffer):

```
env={"SM_VLLM_GPU_MEMORY_UTILIZATION": "0.45"}
```

At container startup, each stage logs its memory use to the endpoint’s log group in Amazon CloudWatch Logs. The following values confirm the model fits well within a 24 GB GPU:

| **What it measures** | **Value** | **Example** |
| --- | --- | --- |
| **Talker model weights** | 3.66 GiB | Model loading took 3.66 GiB memory and 0.81 seconds |
| **code2wav model weights** | 0.45 GiB | Model loading took 0.45 GiB memory and 4.73 seconds |
| **Talker KV cache reserved** | 6.08 GiB | Available KV cache memory: 6.08 GiB |
| **Talker KV cache token budget** | 56,928 tokens | GPU KV cache size: 56,928 tokens |

The model weights are small (3.66 GiB for the talker and 0.45 GiB for code2wav). Most of the remaining memory each stage is allowed becomes KV cache, the working memory that holds tokens for in-flight requests. At a utilization of `0.45` on a 24 GB GPU (about 22 GiB usable), each stage can use up to roughly 10 GiB. Together, the two stages fit within the GPU with headroom to spare. This is why a 24 GB GPU is well suited to the 1.7B model, and a larger GPU is not required.

### Step 3: Test the endpoint

With the endpoint `InService`, test voice cloning. Two details are specific to this JumpStart container and are essential to get a response:

- **Route selection:** An Amazon SageMaker endpoint exposes a single `/invocations` path, which this container routes to its completions handler by default. To reach the text-to-speech handler, you must pass the custom attribute `route=/v1/audio/speech`. Without it, the request is rejected.
- **Payload shape:** Use the OpenAI speech schema with `task_type` set to `"Base"` for voice cloning, and include the reference clip URI and its transcript.

**Audio formats.** Provide the reference clip as a base64-encoded `data:audio/wav;base64,...` URI. Converting the reference to 24 kHz mono WAV before encoding is the recommended input form. The endpoint returns audio in the format you request through `response_format`. This post uses `"wav"`, and the model generates 24 kHz mono audio.

The following code converts the reference clip and base64-encodes it:

```
import base64, io, json, subprocess
import boto3, soundfile as sf, imageio_ffmpeg

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ffmpeg, "-y", "-i", "reference.m4a",
    "-ar", "24000", "-ac", "1", "reference.wav"], check=True)

data, sr = sf.read("reference.wav", dtype="float32")
buf = io.BytesIO(); sf.write(buf, data, sr, format='WAV'); buf.seek(0)
ref_uri = "data:audio/wav;base64," + base64.b64encode(buf.read()).decode()

REF_TEXT = "Transcript of the words spoken in the reference clip."
```

### Clone a voice for a single sentence

Invoke the endpoint with the target text in `input` and the reference clip in `ref_audio`. Note the `CustomAttributes` routing argument, which is required to reach the text-to-speech handler:

```
runtime = boto3.client("sagemaker-runtime")

payload = {
    "model": "/opt/ml/model",
    "input": "This is a demonstration of real-time voice cloning using Qwen TTS on Amazon SageMaker AI.",
    "task_type": "Base",
    "ref_audio": ref_uri,
    "ref_text": REF_TEXT,
    "language": "English",
    "response_format": "wav",
}

resp = runtime.invoke_endpoint(
    EndpointName="qwen3-tts-voice-clone",
    ContentType="application/json",
    CustomAttributes="route=/v1/audio/speech", # required to reach the TTS handler
    Body=json.dumps(payload),
)
open("clone.wav", "wb").write(resp["Body"].read())
```

The preceding request is the most basic case: one sentence of text returned as speech in the cloned voice. The following patterns build on it, using the same `ref_audio`, `ref_text`, and `route` custom attribute.

Sample audio for this example (open the files provided with this post):

**Reference input:** `reference_original_input.wav`

**Generated output:** `cloned_output.wav`

A single request works well for one sentence or a short passage. For longer content, such as an article or a multi-line script, split it and send one request per sentence or paragraph so the voice stays consistent throughout.

### Generate speech in another language (cross-lingual cloning)

To produce speech in a different language while keeping the same voice, use the same reference clip and set `"language"` to another supported language. The following example uses the English reference to generate Chinese speech, preserving the speaker’s vocal identity across languages.

```
payload = {
    "model": "/opt/ml/model",
    "input": "你好，这是一个语音克隆的测试。",
    "task_type": "Base",
    "ref_audio": ref_uri, # same English reference
    "ref_text": REF_TEXT,
    "language": "Chinese",
    "response_format": "wav",
}
resp = runtime.invoke_endpoint(
    EndpointName="qwen3-tts-voice-clone",
    ContentType="application/json",
    CustomAttributes="route=/v1/audio/speech",
    Body=json.dumps(payload),
)
open("clone_chinese.wav", "wb").write(resp["Body"].read())
```

**Generated output:** `cross_lingual_cloning.wav`

### Choosing an instance and scaling for your traffic

Choose an instance in three steps. First, confirm that JumpStart supports it. Then, check your [service quota](https://docs.aws.amazon.com/general/latest/gr/sagemaker.html) and confirm that its GPU memory fits the model. For a 1.7B model, a 24 GB GPU (the g6 family, NVIDIA L4) is well matched and cost effective.

To estimate concurrent request capacity, check the KV cache token budget in the endpoint’s log group in Amazon CloudWatch Logs. The log group path is `/aws/sagemaker/Endpoints/<endpoint-name>`. At container startup, you see a line such as:

```
GPU KV cache size: 56,928 tokens
```

This value is the total KV cache capacity, measured in tokens. It represents the combined token count that the reserved cache can hold across concurrent requests. Divide this budget by the average request size to estimate concurrent capacity. Because TTS requests are typically short, one instance can accommodate multiple simultaneous requests.

For higher traffic, add endpoint instances or select an instance type with more GPU capacity. Amazon SageMaker AI automatic scaling can adjust the instance count based on demand.

## Monitoring the endpoint with Amazon CloudWatch

Amazon SageMaker AI publishes endpoint metrics to Amazon CloudWatch automatically. They fall into two groups: instance-level hardware metrics and invocation-level request metrics. Use them to right-size the instance, tune concurrency, and set alarms.

### Instance (hardware) metrics

Namespace `/aws/sagemaker/Endpoints`, with dimensions `EndpointName` and `VariantName`:

| **Metric** | **Description** |
| --- | --- |
| **GPUUtilization** | The percentage of GPU compute units used by the instances. |
| **GPUMemoryUtilization** | The percentage of GPU memory used by the instances. |
| **CPUUtilization** | The percentage of CPU units used by the instances. |
| **MemoryUtilization** | The percentage of system memory used by the instances. |
| **DiskUtilization** | The percentage of disk space used by the instances. |

### Invocation (request) metrics

Namespace `AWS/SageMaker`, same dimensions:

View `Invocations` with the Sum statistic to see the total request count over a period.

| **Metric** | **Description** |
| --- | --- |
| **Invocations** | The number of requests sent to the endpoint. |
| **InvocationsPerInstance** | The number of requests sent to each instance behind the endpoint. |
| **ConcurrentRequestsPerModel** | The number of requests being processed concurrently. |
| **ModelLatency** | The time the model takes to respond, as viewed from SageMaker AI, in microseconds. |
| **OverheadLatency** | The time added by SageMaker AI overhead, in microseconds. |
| **Invocation4XXErrors** | The number of requests that returned a 4XX HTTP response code. |
| **Invocation5XXErrors** | The number of requests that returned a 5XX HTTP response code. |
| **InvocationModelErrors** | The number of requests that did not result in a valid model response. |

## Clean up

To avoid ongoing charges, delete the endpoint, endpoint configuration, and model when you are finished:

```
predictor.delete_endpoint() # deletes endpoint and endpoint config
predictor.delete_model()
```

## Conclusion

This post showed how to deploy the publicly available Qwen3-TTS-12Hz-1.7B-Base model to an Amazon SageMaker AI real-time endpoint using Amazon SageMaker JumpStart. It also showed how to invoke the endpoint to clone a voice from a short reference clip and transcript. With a managed real-time endpoint, you control your data and align cost with the compute you use, without managing the underlying infrastructure.

To get started, use the [Amazon SageMaker JumpStart guide](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-jumpstart.html) to open JumpStart in Amazon SageMaker Studio. Search for “Qwen3-TTS-12Hz-1.7B-Base” and deploy the model by using the configuration in this post. For model details, see the [Qwen3-TTS model card](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base).

## About the authors
