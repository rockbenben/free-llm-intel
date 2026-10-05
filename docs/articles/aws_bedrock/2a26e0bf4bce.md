---
vendor: aws_bedrock
title: 在 Amazon SageMaker AI 上部署实时个性化语音（Qwen3-TTS）
original_title: Deploying real-time personalized speech with Qwen3-TTS on Amazon SageMaker AI
url: https://aws.amazon.com/blogs/machine-learning/deploying-real-time-personalized-speech-with-qwen3-tts-on-amazon-sagemaker-ai
date: 2026-09-25
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

借助语音克隆（voice cloning），你可以从一段简短的参考录音生成目标说话人声音的新语音，而无需重新训练模型。你现在可以[从 Amazon SageMaker JumpStart](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-jumpstart.html) 部署公开可用的 [Qwen3-TTS-12Hz-1.7B-Base](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base) 文本转语音模型，到一个完全托管的实时推理端点。

语音克隆复现特定说话人的声音身份。从一段该说话人的短录音及其转录文本开始，然后提供要合成的新文本。模型用参考说话人的声音说出那段文本，而无需重新训练。媒体团队、教育者应用开发者可以用这一能力创造个性化的语音体验、为多语言内容做本地化。他们还能支持无障碍沟通，并在跨语言时保留说话人的身份。

用一个自托管、公开可用的语音克隆模型，你控制成本并把音频数据留在你的 AWS 环境内。你还可以把模型适配到你的领域。借助 [Amazon SageMaker AI](https://aws.amazon.com/sagemaker/ai/)，你可以在一个完全托管的实时端点上运行模型，并处理基础设施配置、健康监控和自动伸缩。你无需管理底层 GPU 服务器。

本文演示如何用 [Amazon SageMaker Python SDK](https://github.com/aws/sagemaker-python-sdk) 从 Amazon SageMaker JumpStart 部署 Qwen3-TTS-12Hz-1.7B-Base，以及如何调用生成的端点从一段参考音频克隆声音。它还涵盖让这一部署在实践中奏效的配置设置，以及你用于监控并按需调整端点的 Amazon CloudWatch 指标。

## 什么是 Qwen3-TTS

Qwen3-TTS 是由阿里云 Qwen 团队开发的一个公开可用的文本转语音模型家族。它覆盖 10 种语言：中文、英文、日文、韩文、德文、法文、俄文、葡萄牙文、西班牙文和意大利文。这些模型使用 Qwen3-TTS-Tokenizer-12Hz 语音分词器，并支持流式生成以用于低延迟交互场景。

本文使用 Base 变体 [Qwen3-TTS-12Hz-1.7B-Base](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base)。它仅用几秒用户音频就能执行语音克隆，也可以作为微调的基础。对于语音克隆，模型接收一段参考音频及其转录文本，捕捉说话人的声音特征（如音色、音高和节奏）并应用到新文本上。这不同于 [CustomVoice](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice) 变体——后者从一组固定的预定义说话人而非用户提供的参考来生成语音。

该模型还支持跨语言克隆：你可以从一个语言的参考中捕捉声音，并在另一种语言中生成语音，同时保留说话人的声音身份。

Qwen3-TTS-12Hz-1.7B-Base 与 Qwen3-TTS-12Hz-1.7B-CustomVoice 和 Qwen3-ASR-1.7B 一起在 Amazon SageMaker JumpStart 中提供。有了这些 JumpStart 选项，你可以使用本文展示的精简部署。

## 语音克隆

借助语音克隆，应用可以从一段参考录音复现所选说话人的声音身份，而不受限于一组固定的预定义声音。这支持媒体、客户互动、教育和对话式 AI 各领域的一系列用例。

### 收益

这一部署方式的关键收益包括：

- **规模化个性化：** 你可以从一小段样本生成目标声音的语音，而无需收集大型训练数据集。
- **多语言覆盖：** 你可以用在一个语言中捕捉的声音，在保留身份的同时生成另一种语言的语音。
- **成本效率：** 部署把成本与计算用量对齐，而非按字符 API 计价。
- **数据控制：** 数据留在你的 AWS 账户和你管理的 Amazon SageMaker 端点内。

### 应用用例

语音克隆的常见应用包括：

- **内容本地化：** 你可以在保留原说话人声音的同时，把内容翻译成多种语言。
- **客户体验：** 联络中心和虚拟助手的响应可以使用一致的品牌声音。
- **在线学习和有声书：** 你可以用某位讲师或作者的特定声音呈现长内容。
- **创意原型：** 你可以在录音室制作前测试对白和配音。
- **实时对话式 AI：** 流式语音识别和低延迟合成可支持交互式语音智能体。

## 方案概览

这一方案把 Qwen3-TTS-12Hz-1.7B-Base 从 Amazon SageMaker JumpStart 部署到一个实时端点。JumpStart 提供模型产物和一个预构建的服务容器，因此你无需编写自定义推理 handler。你构造一个 `JumpStartModel` 对象、调用它的 `deploy` 方法，并用 Amazon SageMaker runtime 客户端调用生成的端点。

JumpStart 容器服务该模型，从文本输入生成 24 kHz 音频输出。这一阶段式设计影响你如何确定 GPU 显存大小，下一节会解释。

### 架构

下图展示了部署的实时推理架构。

图 1：Amazon SageMaker AI 上的实时语音克隆架构

该部署遵循标准的 Amazon SageMaker AI 实时推理模式：

- 客户端向 Amazon SageMaker AI 端点发送一个 HTTP 请求。请求体包含目标文本、base64 编码的参考音频，以及参考音频的转录文本。
- Amazon SageMaker AI 把请求路由到运行在 GPU 实例上的 vLLM-Omni 服务容器。
- talker 阶段从文本和参考声音生成语音 token，code2wav 阶段把它们渲染成波形。
- 响应以所请求格式的音频（本文用 WAV）返回给客户端。

### 前提条件

开始前，确认你拥有以下资源和权限：

- 一个 AWS 账户，可访问 [Amazon SageMaker AI](https://docs.aws.amazon.com/sagemaker/) 和 [Amazon Simple Storage Service (Amazon S3)](https://aws.amazon.com/s3/)。
- 一个 [AWS Identity and Access Management (IAM)](https://docs.aws.amazon.com/iam/) 身份，具备创建 Amazon SageMaker 模型、端点配置和端点，以及调用端点的权限。
- 一个 [Amazon SageMaker Studio](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-updated.html) 环境、一个 notebook 实例，或一个安装了 [Amazon SageMaker Python SDK](https://sagemaker.readthedocs.io/) 的本地环境。
- 一种受支持 GPU 实例的足够服务配额。本演练使用 `ml.g6.4xlarge`（1x NVIDIA L4 GPU，24 GB），对 1.7B 模型足够。
- 一段目标说话人的短参考音频（几秒钟足够），以及其中所说文字的转录。

### 步骤 1：从 JumpStart 部署模型

用一个 model ID 构造 `JumpStartModel` 并部署它。GPU 显存覆盖是这一部署最重要的设置。下一节解释如何配置它。在运行下面代码之前，把 `<sagemaker-execution-role-arn>` 替换为 Amazon SageMaker AI 用于部署模型的 IAM execution 角色的 ARN。

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

在容器把模型加载到 GPU 期间，端点需要几分钟达到 `InService` 状态。你可以在 Amazon SageMaker AI 控制台监控端点状态，或调用 `describe_endpoint` API。

### 步骤 2：正确确定 GPU 显存大小

如前所述，模型作为两个阶段（talker 和 code2wav）运行在同一块 GPU 上。vLLM 基于 `gpu_memory_utilization`（一个阶段可占用的 GPU 显存比例）预先保留 GPU 显存。两个阶段共享一块 GPU。为避免启动期间的内存不足错误，让它们的合计保留处于 GPU 容量之内。

把该值设为使两个阶段合计能舒适容纳。用一个同等应用于两个阶段的共享设置，`0.45` 效果很好（0.45 + 0.45 = 0.90，留下约 10% 的缓冲）：

```
env={"SM_VLLM_GPU_MEMORY_UTILIZATION": "0.45"}
```

在容器启动时，每个阶段会把它使用的内存记录到端点在 Amazon CloudWatch Logs 中的日志组。下列数值确认该模型能舒适地落入一块 24 GB GPU 之内：

| **测量内容** | **数值** | **示例** |
| --- | --- | --- |
| **talker 模型权重** | 3.66 GiB | Model loading took 3.66 GiB memory and 0.81 seconds |
| **code2wav 模型权重** | 0.45 GiB | Model loading took 0.45 GiB memory and 4.73 seconds |
| **talker KV 缓存保留** | 6.08 GiB | Available KV cache memory: 6.08 GiB |
| **talker KV 缓存 token 预算** | 56,928 tokens | GPU KV cache size: 56,928 tokens |

模型权重很小（talker 3.66 GiB，code2wav 0.45 GiB）。每个阶段被允许的剩余内存大多变成了 KV 缓存——那个为在途请求持有 token 的工作内存。在 24 GB GPU（约 22 GiB 可用）上以 `0.45` 利用率，每个阶段最多可用约 10 GiB。两阶段合起来落在 GPU 之内且余量充裕。这就是为什么 24 GB GPU 很适合 1.7B 模型，而不需要更大的 GPU。

### 步骤 3：测试端点

端点达到 `InService` 后，测试语音克隆。有两个细节是这个 JumpStart 容器特有的，且对得到响应至关重要：

- **路由选择：** 一个 Amazon SageMaker 端点暴露单个 `/invocations` 路径，该容器默认把它路由到其 completions handler。要到达文本转语音 handler，你必须传递自定义属性 `route=/v1/audio/speech`。没有它，请求会被拒绝。
- **载荷形态：** 使用 OpenAI speech schema，把 `task_type` 设为用于语音克隆的 `"Base"`，并包含参考音频 URI 及其转录文本。

**音频格式。** 以 base64 编码的 `data:audio/wav;base64,...` URI 提供参考音频。把参考音频转成 24 kHz 单声道 WAV 再编码是推荐的输入形式。端点以你通过 `response_format` 请求的格式返回音频。本文使用 `"wav"`，模型生成 24 kHz 单声道音频。

下面的代码转换参考音频并做 base64 编码：

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

### 为一句话克隆声音

用 `input` 中的目标文本和 `ref_audio` 中的参考音频调用端点。注意 `CustomAttributes` 路由参数，它是到达文本转语音 handler 所必需的：

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

上面的请求是最基本的例子：一句文本，以克隆声音的语音返回。下面的模式在其之上构建，使用同样的 `ref_audio`、`ref_text` 和 `route` 自定义属性。

本示例的示例音频（打开本文随附提供的文件）：

**参考输入：** `reference_original_input.wav`

**生成输出：** `cloned_output.wav`

单个请求很适合一句话或一小段。对于更长的内容，如一篇文章或多行脚本，把它拆分并按每句或每段发一个请求，使声音自始至终保持一致。

### 用另一种语言生成语音（跨语言克隆）

要在保持同一声音的同时以不同语言生成语音，使用同一段参考音频，并把 `"language"` 设为另一个受支持的语言。下面的例子用英文参考生成中文语音，在跨语言时保留说话人的声音身份。

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

**生成输出：** `cross_lingual_cloning.wav`

### 为你的流量选择实例并伸缩

分三步选择一个实例。首先确认 JumpStart 支持它。然后检查你的[服务配额](https://docs.aws.amazon.com/general/latest/gr/sagemaker.html)并确认它的 GPU 显存容纳得下模型。对于 1.7B 模型，一块 24 GB GPU（g6 家族，NVIDIA L4）匹配良好且经济。

要估算并发请求容量，查看端点在 Amazon CloudWatch Logs 中的日志组里的 KV 缓存 token 预算。日志组路径是 `/aws/sagemaker/Endpoints/<endpoint-name>`。在容器启动时，你会看到一行类似：

```
GPU KV cache size: 56,928 tokens
```

这个值是 KV 缓存总容量，以 token 计。它表示预留缓存在并发请求间可持有的合计 token 数。把这一预算除以平均请求大小以估算并发容量。因为 TTS 请求通常很短，一个实例可以容纳多个同时请求。

对于更高的流量，增加端点实例或选择一个有更多 GPU 容量的实例类型。Amazon SageMaker AI 自动伸缩可以根据需求调整实例数。

## 用 Amazon CloudWatch 监控端点

Amazon SageMaker AI 自动把端点指标发布到 Amazon CloudWatch。它们分两组：实例级硬件指标和调用级请求指标。用它们来确定实例大小、调优并发和设置告警。

### 实例（硬件）指标

命名空间 `/aws/sagemaker/Endpoints`，维度为 `EndpointName` 和 `VariantName`：

| **指标** | **描述** |
| --- | --- |
| **GPUUtilization** | 实例使用的 GPU 计算单元百分比。 |
| **GPUMemoryUtilization** | 实例使用的 GPU 显存百分比。 |
| **CPUUtilization** | 实例使用的 CPU 单元百分比。 |
| **MemoryUtilization** | 实例使用的系统内存百分比。 |
| **DiskUtilization** | 实例使用的磁盘空间百分比。 |

### 调用（请求）指标

命名空间 `AWS/SageMaker`，同样的维度：

用 Sum 统计查看 `Invocations` 以看到一段时间内的总请求数。

| **指标** | **描述** |
| --- | --- |
| **Invocations** | 发送到端点的请求数。 |
| **InvocationsPerInstance** | 发送到端点后每台实例的请求数。 |
| **ConcurrentRequestsPerModel** | 正被并发处理的请求数。 |
| **ModelLatency** | 模型响应所需时间（从 SageMaker AI 视角看），以微秒计。 |
| **OverheadLatency** | SageMaker AI 开销增加的时间，以微秒计。 |
| **Invocation4XXErrors** | 返回 4XX HTTP 响应码的请求数。 |
| **Invocation5XXErrors** | 返回 5XX HTTP 响应码的请求数。 |
| **InvocationModelErrors** | 未得到有效模型响应的请求数。 |

## 清理

为避免持续产生费用，完成后删除端点、端点配置和模型：

```
predictor.delete_endpoint() # deletes endpoint and endpoint config
predictor.delete_model()
```

## 结论

本文演示了如何用 Amazon SageMaker JumpStart 把公开可用的 Qwen3-TTS-12Hz-1.7B-Base 模型部署到一个 Amazon SageMaker AI 实时端点，还演示了如何调用端点从一段简短的参考音频和转录文本克隆声音。用一个托管的实时端点，你控制自己的数据并把成本与你使用的计算对齐，而无需管理底层基础设施。

要开始上手，用 [Amazon SageMaker JumpStart 指南](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-jumpstart.html)在 Amazon SageMaker Studio 中打开 JumpStart。搜索“Qwen3-TTS-12Hz-1.7B-Base”并用本文的配置部署模型。模型细节参见 [Qwen3-TTS 模型卡](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base)。
