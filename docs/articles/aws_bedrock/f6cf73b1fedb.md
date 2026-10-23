---
vendor: aws_bedrock
title: 在 Amazon SageMaker AI 上使用 Kokoro TTS 流式传输来自 AI 代理的低延迟语音
original_title: 
url: https://aws.amazon.com/blogs/machine-learning/stream-low-latency-speech-from-ai-agents-using-kokoro-tts-on-amazon-sagemaker-ai
date: 2026-10-22
lang: zh
captured: 2026-10-23
extractor: readability-v1
translator: mt
status: translated
body_sha: 02531f9113c7
---

## [人工智能](https://aws.amazon.com/blogs/machine-learning/)

# 在 Amazon SageMaker AI 上使用 Kokoro TTS 流式传输来自 AI 代理的低延迟语音

客户向人工智能语音代理询问问题并等待。客服人员已经有了答案，正在生成长长的多段回复，但客户在五秒钟内什么也没听到。当得到答复时，客户会感到沮丧、困惑，并且不再关注。

文本到语音的集成正是造成了这种差距。一句话响应可能会在 600 毫秒内生成，但完整响应需要 5 秒，并且集成会在综合开始之前等待所有响应。

这篇文章展示了如何缩小这一差距。一旦代理生成每个句子，我们就会将其传输到 [Amazon SageMaker AI](https://aws.amazon.com/sagemaker/) 上托管的 Kokoro-82M 文本转语音 (TTS) 模型，因此合成从第一个句子开始，而不是从完成的响应开始。将音频返回到浏览器也需要自己的解决方案，因此我们还介绍了执行此操作的两种传输方式以及每种传输方式的实际成本。

## 解决方案概述

该解决方案通过在生成的同时进行流式合成而不是等待其完成来缩小差距。当代理生成每个句子时，该句子会立即传输到托管的 Kokoro-82M 文本转语音模型，因此可以在代理说出完整响应之前开始音频播放。 Kokoro-82M 仅包含 8200 万个参数，足够小，可以在单个中层 GPU 实例上廉价运行。对于处理真实流量的语音代理来说，这可以降低延迟和推理成本。

Kokoro-82M 在 SageMaker AI 实时端点上的“ml.g5.xlarge”GPU 实例上的自定义容器中运行。该容器公开两条路由：“POST /incalls”，它流式传输一个完整输入的响应，以及“WS /incalls-bidirection-stream”，它使一个连接在两个方向上的多个消息之间保持打开状态。

下图展示了从客户端到模型的请求路径：

![客户端通过 InvokeEndpointWithBi DirectionStream 连接到 ml.g5.xlarge 上的 Amazon SageMaker AI 实时终端节点。 Starlette ASGI 应用程序公开了 GET /ping、POST /incalls 和 WS /incalls-bi Direction-stream，将 WebSocket 路由到运行 Kokoro-82M 的 KPipeline，该 KPipeline 在同一管道上返回音频和控制帧连接。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/19/ML-21706-1.png)

图 1：通过双向流从客户端到 SageMaker AI 实时端点的请求路径

## 先决条件

在开始之前，您需要：

- 有权创建 SageMaker AI 端点的 AWS 账户； AgentCore 运行时，Amazon Bedrock AgentCore 的一项功能； AWS 身份和访问管理 (IAM) 角色；以及 Amazon Elastic Container Registry (Amazon ECR) 存储库，至少包括 `sagemaker:CreateEndpoint`、`sagemaker:CreateEndpointConfig`、`sagemaker:CreateModel`、`sagemaker:InvokeEndpointWithBi DirectionStream` 和 `bedrock:InvokeModelWithResponseStream` 操作。
- 示例容器将旧版 PyTorch 与已知建议（“PYSEC-2026-2286”，已在 torch 2.10.0 中修复）固定在一起。在进行任何非价值证明使用之前，请检查并升级密码。
- [AWS 云开发工具包 (AWS CDK) v2](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html)，在您的目标账户和 AWS 区域中安装并引导。
- 从声明“com.amazonaws.sagemaker.capability.bidirect-streaming=true”Docker 标签的容器部署的 SageMaker AI 实时端点。
- Python 3.12 或更高版本、[uv](https://docs.astral.sh/uv/) 和 Docker 来构建容器映像（底层 HTTP/2 客户端仅为 Python 3.12 及更高版本提供预构建的轮子）。
- 适用于 Python 的 AWS 开发工具包 (Boto3)，支持“invoke_endpoint_with_bi Direction_stream”。
- 熟悉 WebSockets 和 Starlette 或类似的 ASGI 框架。
- 本文引用的 [GitHub 存储库](https://github.com/aws-samples/sample-kokoro-tts-for-ai-agents) 中的部署代码。

## 演练

本演练首先部署端点和代理，然后完成客户端更改，使增量流式传输端到端地工作。

### 部署端点和代理

Kokoro-82M 终端节点和代理运行时通过两个 CLI 工具进行部署，每个工具都包装自己的 AWS CDK 堆栈：
```
uv run speech-infra deploy kokoro-82m
uv run agent-infra deploy --bedrock-model-id <your-bedrock-model-id>
```
“语音基础设施部署”提供 Kokoro-82M 端点。这包括基础堆栈和模型缓存堆栈，用于创建底层 IAM 角色并将模型的权重同步到 Amazon Simple Storage Service (Amazon S3) 中。然后，端点堆栈构建容器映像并创建 SageMaker AI 模型、端点配置和端点。 “agent-infra deploy”配置托管 Strands 代理的 Amazon Bedrock AgentCore 运行时，该代理调用您刚刚部署的终端节点，因此首先部署终端节点。

### 步骤 1：处理 SageMaker AI 实际发送的 WebSocket 帧类型

SageMaker AI 使用的双向传输将客户端消息的每一条作为二进制 WebSocket 帧传递到容器。编写 Starlette WebSocket 处理程序的常见方法是调用 `receive_text()`，它读取 `message["text"]` 并在该密钥不存在时引发 `KeyError`。由于此客户端发送的每条消息均以二进制形式到达，因此该处理程序在每次请求时都会失败。

这种故障通常会被误诊。将“str(e)”转发到客户端的通用异常处理程序将“KeyError('text')”转换为读取“text”的错误帧，这看起来像是丢失的字段，而不是帧问题。端点本身始终报告“InService”，因为它接受连接并响应每条消息，每次都会出现错误。

明确接受任一帧类型，而不是假设会出现：
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
当不存在文本字段时，这会将字节解码为 UTF-8，而不是假设一种帧类型。通过发送二进制帧来测试它，因为这种故障​​模式会产生格式良好的错误帧和健康的端点状态，而不是明显的崩溃。

### 步骤 2：在消息之间保持会话打开

容器完成一条消息的音频合成后，本能地会关闭会话，这是 HTTP 循环结束的方式。这里是错误的。发送消息的音频和“synthesis_complete”控制帧后，容器循环应返回等待“receive()”，以等待同一仍打开的会话上的下一条消息。仅当客户端发送显式的 `{"type": "close"}` 消息时才关闭连接。

下图显示了一个会话按顺序携带两个句子，仅在最后结束：

![一个双向会话发送两个句子，每个句子后面跟着thesis_start、PCM 音频和synthesis_complete 帧，以显式关闭结束消息。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/20/ml-21706-edit-1.png)

图 2：一个双向会话按顺序携带两个句子，仅在最后关闭

这样，您就可以在一个持久会话中一个接一个地发送多个句子，而它们之间没有重新连接成本。在一个响应后急切地关闭将迫使每个句子建立一个新的连接，从而消除大部分延迟优势。

### 步骤 3：在代理生成句子时流式传输句子

会话行为到位后，延迟问题的客户端修复是一个类，该类可以规范化以两种形式到达的文本：预先已知的完整字符串或实时令牌流。无论哪种方式，它都会产生相同的输出：完整的句子，一旦每个句子完成就准备发送。
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
每个文本片段到达时调用一次“feed()”。它返回所有新完成的句子，保留尾随文本。在输入结束时调用一次“flush()”，以释放剩余的任何部分文本，即使没有尾随标点符号。这可以防止在句点到达之前结束的流丢失最后一句话。

这不是并发合成。每个双向处理程序都是一个严格的顺序循环：接收消息，合成其音频，发送该音频，发送“synthesis_complete”，然后接收下一条消息。当句子一仍在传输时，句子二的音频不会生成。增量发送所带来的范围更窄：第一个句子的综合在它存在的那一刻就开始，而不是等待完整的响应。对于在第一个句子和最后一个句子之间具有实际生成时间的多句子响应，这就是整个延迟的胜利。

我们针对在一个会话中发送三句话输入的实时端点验证了这一点。所有三个块都带有与每个块发送的文本相匹配的音频：

| **块** | **文字** | **音频字节** | **持续时间** |
| --- | --- | --- | --- |
| 1 | “你好呀。” | 73,200 | 1.525 | 1.525
| 2 | “这是部署后检查。” | 108,000 | 2.250 | 2.250
| 3 | “它有三句话。” | 98,400 | 98,400 2.050 | 2.050

### 步骤 4：选择将音频返回客户端的传输方式

将文本增量地流式传输到模型中可以解决一半的问题。另一半是将生成的音频输出到渲染它的任何地方，通常是浏览器。大多数代理和聊天前端已经通过服务器发送事件 (SSE) 传输文本：单向，并且大多数浏览器本机支持。 SSE 是一种文本协议，不是为了承载原始二进制有效负载而构建的。向现有 SSE 管道添加语音的团队自然会采用已有的模式：对音频进行 Base64 编码并将其包装在 JSON 事件中。

我们在 24 个剪辑中测量了该方法的成本，通过 Amazon Transcribe 确认不同编码的质量没有差异，并将 MP3 与 AAC 进行了比较：

| **候选人** | **原始字节** | **Base64 字节** | **比特率** |
| --- | --- | --- | --- |
|原始 PCM | 2,396,400 | 2,396,400 3,195,200 | 3,195,200 384 kbps |
| MP3 48k | 308,304 | 411,072 | 49.5 kbps | 49.5 kbps
| AAC 32k fMP4 | 258,039 | 258,039 344,084 | 41.6 kbps | 41.6 kbps

Base64 将每个有效负载夸大了接近预期的 33%。更微妙的成本是框架对齐。 SSE 事件由空行分隔，但内部音频被分隔为 MP3 帧。这两种方案不一定与传输数据块的方式一致。在一项测量的响应中，四个逻辑 MP3 帧作为六个传输块到达，其中两个在中间帧结束。将每个交付块视为一个完整单元的消费者在普通、健康的流量上失败了。该修复缓冲传入字节，并且仅在找到分隔符后才起作用：
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
今天用于面向模型的腿的替代方案完全跳过了 Base64 和 SSE 框架。它在已经携带增量文本输入的同一双向会话上多路复用原始二进制音频和 JSON 控制帧，并用一条规则区分它们。
```
import json


def _decode_control_frame(chunk: bytes) -> dict | None:
    try:
        decoded = json.loads(chunk.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return decoded if isinstance(decoded, dict) else None
```
无法解码为 JSON 对象的块是音频，按接收时转发，路径中的任何位置都没有编码步骤。一种边缘情况很重要：原始 PCM 音频可以合法地以字节“0x7b”、ASCII 字符“{”开始，与打开 JSON 对象的字符相同。此规则可避免对音频进行错误分类，因为它需要将整个块解析为有效的 JSON，而不是单独解析第一个字节，而 PCM 帧基本上永远不会这样做。

> 注意：如果您的前端已经有一个可用的文本 SSE 管道，则 SSE 事件内的 Base64 编码音频是务实的选择。它花费了大约 33% 的额外有效负载以及缓冲和重新组装步骤，但可以重复使用您已经运行的基础设施。如果您正在构建全新的语音路径，或者优先考虑延迟，那么统一的二进制和 JSON 方法可以避免这两种成本，并重用已经承载文本的连接。

### 步骤 5：将其放在真实代理中

更完整的端到端案例是一个实时的生成代理，每次只编写一个标记，在第一个句子存在之前无法知道第四个句子。此示例作为 Strands 代理运行，由 Amazon Bedrock 支持，部署到 Amazon Bedrock AgentCore 运行时，使用步骤 4 中的模式调用 Kokoro 终端节点。此设计中连接了三个通信支路：面向浏览器的支路将服务器发送的事件传回调用者、代理对 Amazon Bedrock 的流式调用以生成文本，以及代理与 Kokoro 终端节点的双向会话以进行合成。

下图显示了这三个通信分支，以及生成和综合之间发生重叠的位置：

![调用者通过分支 1、POST /调用、SSE 形状和 Base64 音频向使用 BedrockAgentCoreApp 构建的代理容器发送请求。容器通过支线 2 调用 Amazon Bedrock，这是对文本增量的流式反向调用，并通过支线 3（不带 Base64 的原始 PCM）打开到 Kokoro 终端节点的双向会话，将两个流作为服务器发送合并回调用方事件。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/19/ML-21706-3.png)

图 3：连接调用者、Amazon Bedrock 和 Kokoro 终端节点的三个通信线路

请求有效负载携带一个“mode”字段，可以是“bidi”或“batch”，分派到同一入口点函数内的两个代码路径。它们之间的基准仅改变一个变量：综合何时开始。在“run_bidi”中，两个任务同时运行。其中之一会排出基岩文本流并将完整的句子输入到分块器中。另一个耗尽 Kokoro 会话并在音频块到达时发出它们。两者都推入同一个共享队列，因此使用者会按照真正的到达顺序生成事件：早期句子的音频可以到达调用者，而 Bedrock 仍会生成较晚的句子。 “run_batch”是故意相反的：它在一次综合调用之前等待完整的响应，保留作为公平的基线。

从另一个方向来看，从代理容器返回调用者的路径确实使用了 base64，其原因与步骤 4 中描述的不同。 `BedrockAgentCoreApp` 的入口点必须生成简单的 JSON 可序列化字典，其 SDK 会自动将其转换为 `data: {json}\n\n` 帧。没有办法给它一个原始的二进制帧。这是 JSON 本机托管运行时的结果，而不是第 4 步测量并放弃的选择。 “run_bidi”和“run_batch”在这条腿上都付出了相同的成本，因此它们之间的测量差异纯粹是时间上的：当发出第一个音频块时。

## 测试和验证

我们通过两种方式发送相同的 267 个字符、四句文本块：作为一条消息（批量）和仅作为其第一句（增量），从而隔离了 TTS 传输本身对第一个音频时间的贡献。我们分别针对实时端点进行了五次试验。

正如之前测量的那样，仅发送第一个句子将第一个音频字节的平均时间从 329.3 毫秒缩短到 156.7 毫秒，相对提高了 52.4%（与 TTS 传输本身无关）。

然后，我们使用生成文本的真实语言模型来测量更完整的端到端案例，通过“run_bidi”和“run_batch”针对相同的实时基岩模型和端点运行相同的提示，因此唯一的变量是合成开始的时间。

使用相同的方法，在本地容器中，双向模式的首个音频时间比批处理模式快 2.4 倍，而在部署的 AgentCore 运行时则快 3.5 倍。

下图显示了两种环境之间的差距：

![条形图比较批处理和 Bidi 模式下本地和部署的 Amazon Bedrock AgentCore 运行时与第一个音频的相对时间。批次标准化为 1.0x。本地比迪烟测量速度提高了 0.42 倍（快 2.4 倍）。部署的 Bidi 测量值提高了 0.29 倍（速度提高了 3.5 倍）。](https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/10/19/ML-21706-4.png)

图 4：本地和部署的运行时上批处理和双向模式的首个音频的相对时间

一旦添加了实际的网络跃点，对于已部署的情况，差距就会扩大而不是缩小。 “run_bidi”吸收了它已经在生成和合成之间利用的重叠部分中的跳跃。 “run_batch”没有等效的重叠来隐藏该成本，因为它一次只做一件事，因此每增加一毫秒的网络开销都会直接落在其串行等待上。

要针对您自己的部署重现此比较，请运行代理容器公开的相同 bidi-vs-batch 测试：
```
uv run agent-infra demo --endpoint-url <your-endpoint-url> --prompt "<your prompt>"
```
这会通过两种模式发送提示，并根据每种模式的“agent_start”报告第一个“audio_chunk”事件的时间戳。如果您看到错误，请检查步骤 1 中的“KeyError: 'text'”症状。每个请求失败时报告“InService”的端点表示该错误，而不是部署问题。

## 清理

为了避免持续产生费用，请按照相反的部署顺序拆除本演练创建的资源，首先是代理，然后是端点：
```
uv run agent-infra destroy --bedrock-model-id <your-bedrock-model-id>
uv run speech-infra destroy kokoro-82m
```
`agent-infra destroy` 会删除 Amazon Bedrock AgentCore 运行时资源。 `speech-infra destroy` 会删除 SageMaker AI 模型、端点配置和端点。两者都不会清空缓存模型权重的 Amazon S3 存储桶，也不会删除保存容器映像的 Amazon ECR 存储库，因为两者都可以跨模型共享。如果您不再需要它们，请清空并删除 Amazon S3 存储桶，并手动删除 Amazon ECR 存储库，因为存储的模型检查点和容器映像在删除之前会继续产生少量存储费用。

## 结论

我们展示了如何消除语音代理中可避免的延迟的一个来源，在开始语音合成之前等待代理的完整响应，以及如何量化第二个更安静的成本：SSE 内的 Base64 编码音频会使有效负载增加约三分之一，并且如果不对其进行缓冲，可能会与 MP3 帧边界错位。代理生成每个句子后，立即将每个句子流式传输到 SageMaker AI 双向端点，将孤立的第一个音频的时间缩短一半以上，在部署的代理中缩短 2.4 至 3.5 倍。在该会话上复用二进制音频和 JSON 控制帧，而不是将音频编码为文本，消除了简单的 SSE 中继所需的大小膨胀和帧重新对齐工作。

如果您要向已通过 SSE 传输文本的代理添加语音，请从步骤 4 中的 base64 方法开始，并在延迟成为优先事项后重新访问统一传输。要了解更多信息，请参阅 [Amazon SageMaker AI 实时推理文档](https://docs.aws.amazon.com/sagemaker/) 和 [Amazon Bedrock AgentCore 文档](https://docs.aws.amazon.com/bedrock/)。如果您需要帮助将此模式应用到您自己的架构中，请联系您的 AWS 客户团队。

## 关于作者
