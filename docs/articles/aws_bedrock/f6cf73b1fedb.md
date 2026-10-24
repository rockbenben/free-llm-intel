---
vendor: aws_bedrock
title: 在 Amazon SageMaker AI 上使用 Kokoro TTS 流式传输 AI 智能体的低延迟语音
original_title: Stream low-latency speech from AI agents using Kokoro TTS on Amazon SageMaker AI
url: https://aws.amazon.com/blogs/machine-learning/stream-low-latency-speech-from-ai-agents-using-kokoro-tts-on-amazon-sagemaker-ai
date: 2026-10-22
lang: zh
captured: 2026-10-24
extractor: readability-v1
translator: agent
status: translated
body_sha: 6e3aa85baef0
---

## [Artificial Intelligence](https://aws.amazon.com/blogs/machine-learning/)

# 在 Amazon SageMaker AI 上使用 Kokoro TTS 流式传输 AI 智能体的低延迟语音

客户向 AI 语音智能体提出一个问题，然后等待。智能体其实已经有答案，并且正生成到一段较长的多段落回复的中途，但客户有五秒钟什么都听不到。等答案真正到达时，客户已经沮丧、困惑，而且早就不再关注了。

文本转语音集成恰恰制造了这个空档。一句回复也许 600 毫秒就能生成完，但完整回复要花五秒，而集成会等全部生成完才开始合成。

本文介绍如何弥合这个空档。智能体每产出一句话，我们就把它流式传输到托管在 [Amazon SageMaker AI](https://aws.amazon.com/sagemaker/) 上的 Kokoro-82M 文本转语音（TTS）模型，因此合成从第一句就开始，而不是等整段回复完成。把音频送回浏览器也需要专门的方案，所以我们还会介绍两种实现传输的方式，以及各自在实践中付出的代价。

## 方案概述

该方案通过与生成过程并行进行流式合成，而不是等生成结束，来弥合这个空档。智能体每产出一句话，这句话就立即流式传输到托管的 Kokoro-82M 文本转语音模型，因此音频播放可以在智能体说完整个回复之前就开始。Kokoro-82M 只有 8200 万参数，小到足以在单台中等规格的 GPU 实例上低成本运行。这让处理真实流量的语音智能体同时保持低延迟和低推理成本。

Kokoro-82M 运行在 SageMaker AI 实时端点上的自定义容器中，实例类型为 `ml.g5.xlarge` GPU 实例。该容器暴露两个路由：`POST /invocations`，针对一次完整输入流式返回响应；以及 `WS /invocations-bidirectional-stream`，在双向传输中跨多条消息保持一个连接打开。

下图展示了从客户端到模型的请求路径：

![Client connects to an Amazon SageMaker AI real-time endpoint on ml.g5.xlarge over InvokeEndpointWithBidirectionalStream. A Starlette ASGI app exposing GET /ping, POST /invocations, and WS /invocations-bidirectional-stream routes the WebSocket to a KPipeline running Kokoro-82M, which returns audio and control frames on the same connection.](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/19/ML-21706-1.png)

图 1：客户端经双向流到 SageMaker AI 实时端点的请求路径

## 先决条件

开始之前，你需要：

- 一个 AWS 账户，具备创建以下资源的权限：SageMaker AI 端点；AgentCore runtime（Amazon Bedrock AgentCore 的一项能力）；AWS Identity and Access Management (IAM) 角色；以及 Amazon Elastic Container Registry (Amazon ECR) 仓库。至少需要 `sagemaker:CreateEndpoint`、`sagemaker:CreateEndpointConfig`、`sagemaker:CreateModel`、`sagemaker:InvokeEndpointWithBidirectionalStream` 和 `bedrock:InvokeModelWithResponseStream` 这些操作权限。
- 示例容器固定使用一个较旧的 PyTorch 版本，存在已知安全公告（`PYSEC-2026-2286`，已在 torch 2.10.0 中修复）。在任何非概念验证用途之前，请审查并升级该固定版本。
- [AWS Cloud Development Kit (AWS CDK) v2](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html)，已在目标账户和 AWS 区域中安装并完成 bootstrap。
- 一个从声明了 `com.amazonaws.sagemaker.capabilities.bidirectional-streaming=true` Docker 标签的容器部署的 SageMaker AI 实时端点。
- Python 3.12 或更高版本、[uv](https://docs.astral.sh/uv/)，以及用于构建容器镜像的 Docker（底层 HTTP/2 客户端只为 Python 3.12 及更新版本提供预编译 wheel）。
- 支持 `invoke_endpoint_with_bidirectional_stream` 的 AWS SDK for Python (Boto3)。
- 熟悉 WebSockets 以及 Starlette 或类似的 ASGI 框架。
- 本文引用的 [GitHub 仓库](https://github.com/aws-samples/sample-kokoro-tts-for-ai-agents)中的部署代码。

## 演练

本演练先部署端点和智能体，然后逐步完成让增量流式传输端到端可用的客户端改动。

### 部署端点和智能体

Kokoro-82M 端点和智能体运行时通过两个 CLI 工具部署，每个工具封装各自的 AWS CDK 堆栈：

```
uv run speech-infra deploy kokoro-82m
uv run agent-infra deploy --bedrock-model-id <your-bedrock-model-id>
```

`speech-infra deploy` 负责创建 Kokoro-82M 端点。这包括 foundation 和 model-cache 两个堆栈，它们创建底层的 IAM 角色，并把模型权重同步到 Amazon Simple Storage Service (Amazon S3)。随后 endpoint 堆栈构建容器镜像，并创建 SageMaker AI 模型、端点配置和端点。`agent-infra deploy` 创建承载 Strands 智能体的 Amazon Bedrock AgentCore runtime，该智能体会调用你刚部署的端点，因此请先部署端点。

### 步骤 1：处理 SageMaker AI 实际发送的 WebSocket 帧类型

SageMaker AI 使用的双向传输会把客户端消息的每一个片段都以二进制 WebSocket 帧的形式送到你的容器。编写 Starlette WebSocket 处理程序的一种常见方式是调用 `receive_text()`，它会读取 `message["text"]`，如果该键不存在就抛出 `KeyError`。由于这个客户端发送的每条消息都以二进制形式到达，该处理程序会在每个请求上失败。

这个失败常被误诊。一个把 `str(e)` 转发给客户端的通用异常处理程序会把 `KeyError('text')` 变成一个内容为 `'text'` 的错误帧，看起来像是缺少字段，而不是帧格式问题。端点本身全程报告 `InService`，因为它会接受连接并回应每条消息，只是每次都带一个错误。

请显式接受任一种帧类型，而不是假定只会出现其中一种：

```
from starlette.websockets import WebSocket, WebSocketDisconnect

async def _receive_message(websocket: WebSocket) -> str:
    message = await websocket.receive()
    if message["type"] == "websocket.disconnect":
        raise WebSocketDisconnect(message.get("code", 1000))
    payload = message.get("text")
    if payload is None:
        payload = message.get("bytes", b"").decode("utf-8")
    return payload
```

这段代码在没有 text 字段时把字节按 UTF-8 解码，而不是假定某种帧类型。请用发送二进制帧的方式来测试它，因为这种故障模式会产生格式正确的错误帧和健康的端点状态，而不会出现明显的崩溃。

### 步骤 2：在消息之间保持会话打开

你的容器合成完一条消息的音频后，直觉是关闭会话，就像 HTTP 周期结束那样。在这里这是错的。在发送一条消息的音频和一个 `synthesis_complete` 控制帧之后，容器循环应当回到 `receive()` 上，等待同一个仍然打开的会话中的下一条消息。只有当客户端发送显式的 `{"type": "close"}` 消息时才关闭连接。

下图展示一个会话依次承载两句话，只在最后关闭：

![One bidirectional session sending two sentences, each followed by synthesis_start, PCM audio, and synthesis_complete frames, ending with an explicit close message.](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/20/ml-21706-edit-1.png)

图 2：一个双向会话依次承载两句话，只在最后关闭

这样，你就可以在一个持久会话上依次发送多句话，句子之间没有重连开销。每响应一次就急切关闭，会迫使每句话都新建连接，抵消掉大部分延迟收益。

### 步骤 3：在智能体产出时流式发送句子

会话行为就位之后，客户端侧针对延迟问题的修复是一个类，它把以两种形态到达的文本归一化：一开始就已知的完整字符串，或者实时的 token 流。两种情况下它都产生同样的输出：完整的句子，每句一完成就准备好发送。

```
import re

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


class IncrementalSentenceChunker:
    def __init__(self) -> None:
        self._buffer = ""

    def feed(self, fragment: str) -> list[str]:
        self._buffer += fragment
        parts = _SENTENCE_RE.split(self._buffer)
        if len(parts) == 1:
            return []
        self._buffer = parts[-1]
        return [s.strip() for s in parts[:-1] if s.strip()]

    def flush(self) -> str | None:
        remainder = self._buffer.strip()
        self._buffer = ""
        return remainder or None
```

每当一个文本片段到达时调用一次 `feed()`。它返回任何新完成的句子，并保留尾部的文本。在输入结束时调用一次 `flush()`，以释放即使没有结尾标点也剩余的残缺文本。这样，一个在句号到来之前就结束的流不会丢掉最后一句。

这不是并发合成。每个双向处理程序都是严格顺序的循环：接收一条消息、合成其音频、发送该音频、发送 `synthesis_complete`，然后接收下一条消息。第二句的音频不会在第一句仍在传输时生成。增量发送带来的收益要窄得多：第一句一存在就开始合成，而不是等待完整回复。对于首句与末句之间存在真实生成时间的多句回复，这就是全部的延迟收益。

我们在一个实时端点上对此做了验证，在一个会话上发送三句输入。三个分块都返回了与各自发送文本匹配的音频：

| **分块** | **文本** | **音频字节数** | **时长（秒）** |
| --- | --- | --- | --- |
| 1 | “Hello there.” | 73,200 | 1.525 |
| 2 | “This is a post deployment check.” | 108,000 | 2.250 |
| 3 | “It has three sentences.” | 98,400 | 2.050 |

### 步骤 4：选择把音频送回客户端的传输方式

把文本增量地流进模型解决了问题的一半。另一半是把生成的音频送到任何负责渲染它的地方，通常是浏览器。大多数智能体和聊天前端已经通过 Server-Sent Events (SSE) 流式传输文本：单向，并被大多数浏览器原生支持。SSE 是一种文本协议，并不是为承载原始二进制负载而构建的。为现有 SSE 管道增加语音的团队，自然会沿用已有的模式：把音频做 base64 编码，包进一个 JSON 事件。

我们在 24 个音频片段上测量了这种做法的代价，并用 Amazon Transcribe 确认不同编码之间的质量没有差异，还比较了 MP3 与 AAC：

| **候选方案** | **原始字节** | **Base64 字节** | **码率** |
| --- | --- | --- | --- |
| Raw PCM | 2,396,400 | 3,195,200 | 384 kbps |
| MP3 48k | 308,304 | 411,072 | 49.5 kbps |
| AAC 32k fMP4 | 258,039 | 344,084 | 41.6 kbps |

Base64 会让每个负载膨胀接近预期的 33%。更隐蔽的代价是帧对齐。SSE 事件以空行分隔，但其中的音频是按 MP3 帧分隔的。这两种方案未必与传输层切分数据的方式对齐。在一次实测响应中，四个逻辑 MP3 帧以六个传输分块到达，其中两个在帧中间结束。把每个传输分块当作一个完整单元处理的消费者，在普通、健康的流量上就会出错。修复方式是缓冲传入的字节，只有当找到分隔符时才处理：

```
buffer = b""
for event in resp["Body"]:
    if "PayloadPart" not in event:
        continue
    buffer += event["PayloadPart"]["Bytes"]
    while b"\n\n" in buffer:
        frame, buffer = buffer.split(b"\n\n", 1)
        handle(frame)
```

目前用于面向模型那一段的替代方案完全跳过 base64 和 SSE 分帧。它把原始二进制音频和 JSON 控制帧复用到同一条已经在承载增量文本输入的双向会话上，并用一条规则区分它们。

```
import json


def _decode_control_frame(chunk: bytes) -> dict | None:
    try:
        decoded = json.loads(chunk.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return decoded if isinstance(decoded, dict) else None
```

无法解码为 JSON 对象的分块就是音频，按收到的原样转发，路径中任何地方都没有编码步骤。有一个边缘情况很重要：原始 PCM 音频可以合法地以字节 `0x7b` 开头，也就是 ASCII 字符 `{`，与 JSON 对象的起始字符相同。这条规则之所以避免把该音频误分类，是因为它要求整个分块都能解析为合法 JSON，而不只看第一个字节，而 PCM 帧基本上永远不会满足这一点。

> 注意：如果你的前端已经有一条可用的文本 SSE 管道，那么在 SSE 事件里放 base64 编码的音频是务实的选择。它会带来约 33% 的额外负载和一个缓冲重组的步骤，但复用了你已经在运维的基础设施。如果你是全新构建语音通路，或者延迟是首要考虑，那么统一的二进制加 JSON 方案既避免了这两项代价，又复用了已经在承载文本的连接。

### 步骤 5：在真实智能体中整合起来

更完整的端到端场景是一个实时的生成式智能体，它逐 token 组织回复，在第二句存在之前根本无法知道第四句。这个示例以 Strands 智能体的形式运行，由 Amazon Bedrock 支撑，部署到 Amazon Bedrock AgentCore runtime，并用步骤 4 的模式调用 Kokoro 端点。这个设计中有三段通信连接：面向浏览器、把 Server-Sent Events 送回调用方的那一段；智能体为文本生成对 Amazon Bedrock 的流式调用；以及智能体为合成与 Kokoro 端点建立的双向会话。

下图展示这三段通信连接，以及生成与合成的重叠发生在哪里：

![Caller sends a request to an agent container built with BedrockAgentCoreApp over leg 1, POST /invocations, SSE-shaped with base64 audio. The container calls Amazon Bedrock over leg 2, a streaming converse call for text deltas, and opens a bidirectional session to the Kokoro endpoint over leg 3, raw PCM with no base64, merging both streams back to the caller as Server-Sent Events.](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/19/ML-21706-3.png)

图 3：连接调用方、Amazon Bedrock 和 Kokoro 端点的三段通信连接

请求负载携带一个 `mode` 字段，取值为 `"bidi"` 或 `"batch"`，在同一个入口函数内分派到两条代码路径。两者之间的基准测试只改变一个变量：合成何时开始。在 `run_bidi` 中，两个任务并发运行。一个消费 Bedrock 文本流，把完成的句子送入分句器。另一个消费 Kokoro 会话，在音频块到达时立即发出。两者都推入同一个共享队列，因此消费者按真实到达顺序产出事件：较早句子的音频可以在 Bedrock 仍在生成较晚句子时就到达调用方。`run_batch` 是有意相反的做法：它等待完整回复之后才做一次合成调用，作为公平的基线保留。

反过来，从智能体容器回到调用方的那一段确实使用了 base64，原因与步骤 4 描述的并不相同。`BedrockAgentCoreApp` 的入口必须产出可 JSON 序列化的普通字典，其 SDK 会自动把它们变成 `data: {json}\n\n` 帧。没有办法给它一个原始二进制帧。这是 JSON 原生托管运行时带来的结果，而不是步骤 4 测量并放弃的那个选择。`run_bidi` 和 `run_batch` 在这一段付出完全相同的代价，因此两者之间测得的差异纯粹是时序：第一个音频块何时发出。

## 测试与验证

我们通过两种方式发送同一段 267 字符、四句话的文本，来隔离 TTS 传输本身对首音频时间的贡献：作为一条消息（batch），以及只作为它的第一句（incremental）。我们在实时端点上各运行了五次试验。

如前所述，只发送第一句把首音频字节的平均时间从 329.3 ms 降到 156.7 ms，相对改善 52.4%，且隔离在 TTS 传输本身。

随后我们用真实的语言模型生成文本，测量更完整的端到端场景：把同一个提示分别通过 `run_bidi` 和 `run_batch` 运行在同一个实时 Bedrock 模型和端点上，因此唯一的变量是合成开始的时间。

使用同样的方法，bidi 模式的首音频时间在本地容器上比 batch 模式快 2.4 倍，在已部署的 AgentCore runtime 上快 3.5 倍。

下图展示了两种环境中的这一差距：

![Bar chart comparing relative time to first audio for batch and bidi modes, locally and on a deployed Amazon Bedrock AgentCore runtime. Batch is normalized to 1.0x. Local bidi measures 0.42x (2.4 times faster). Deployed bidi measures 0.29x (3.5 times faster).](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/19/ML-21706-4.png)

图 4：batch 与 bidi 模式在本地和已部署运行时上的相对首音频时间

一旦加入真实的网络跳转，已部署场景的差距会扩大而不是缩小。`run_bidi` 把这一跳吸收进它已经在利用的生成与合成重叠之中。`run_batch` 没有等价的重叠来隐藏这项成本，因为它一次只做一件事，所以每一毫秒新增的网络开销都直接落在它的串行等待上。

要在你自己的部署上复现这个对比，请运行智能体容器暴露的同一个 bidi 与 batch 测试：

```
uv run agent-infra demo --endpoint-url <your-endpoint-url> --prompt "<your prompt>"
```

这会把提示通过两种模式各发送一次，并报告每一次首个 `audio_chunk` 事件相对于 `agent_start` 的时间戳。如果你看到的是错误，请检查步骤 1 中的 `KeyError: 'text'` 症状。端点报告 `InService` 而每个请求都失败，说明的是那个 bug，而不是部署问题。

## 清理

为避免持续计费，请按与部署相反的顺序拆除本演练创建的资源，先智能体，再端点：

```
uv run agent-infra destroy --bedrock-model-id <your-bedrock-model-id>
uv run speech-infra destroy kokoro-82m
```

`agent-infra destroy` 会移除 Amazon Bedrock AgentCore runtime 资源。`speech-infra destroy` 会移除 SageMaker AI 模型、端点配置和端点。两者都不会清空缓存模型权重的 Amazon S3 存储桶，也不会删除存放容器镜像的 Amazon ECR 仓库，因为二者都可能在多个模型之间共享。如果你不再需要它们，请手动清空并删除 Amazon S3 存储桶，并移除 Amazon ECR 仓库，因为存储的模型检查点和容器镜像在被删除之前会持续产生少量存储费用。

## 结论

我们展示了如何从语音智能体中移除一个可避免的延迟来源——在开始语音合成之前等待智能体的完整回复——以及如何量化第二项更隐蔽的代价：SSE 中的 base64 编码音频会让负载膨胀约三分之一，而且如果不做缓冲，就可能与 MP3 帧边界错位。在智能体产出一句话时就把它流式传入 SageMaker AI 双向端点，在隔离测试中把首音频时间缩短了一半以上，在已部署的智能体中缩短了 2.4 到 3.5 倍。在那条会话上复用二进制音频和 JSON 控制帧，而不是把音频编码为文本，消除了朴素 SSE 中继所需的大小膨胀和帧重对齐工作。

如果你要为一个已经通过 SSE 流式传输文本的智能体增加语音，请从步骤 4 的 base64 方案开始，并在延迟成为首要考虑时再回头看统一传输。要了解更多，请参阅 [Amazon SageMaker AI 实时推理文档](https://docs.aws.amazon.com/sagemaker/) 和 [Amazon Bedrock AgentCore 文档](https://docs.aws.amazon.com/bedrock/)。如果你想把这个模式应用到自己的架构中，请联系你的 AWS 客户团队。

## 关于作者
