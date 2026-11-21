---
vendor: together_ai
title: Qwen3 TTS is now available on Together AI
original_title: 
url: https://www.together.ai/blog/qwen3-tts
date: 2026-11-20
lang: zh
captured: 2026-11-21
extractor: readability-v1
translator: mt
status: translated
body_sha: feb8b442e1e3
---

所有博客文章

模型库

发布日期：2026 年 11 月 20 日

# Qwen3 TTS 现已在 Together AI 上提供

在您的产品中保持一种声音，通过简单语言指令改变其语气，并在 10 种语言之间切换，第一个音频只需 97 毫秒。

- 作者Anthony Ji、Charles Duong、Sebastien Beurnier、Sahil Yadav、Sonny Khan
- 目录[40+ 型号选择用于生产...40+ 型号选择用于生产...40+ 型号选择用于生产...](https://www.together.ai/blog/qwen3-tts)
- 本文中的链接[在 VoiceFinder 中比较声音](https://voicefinder.together.ai/)[Qwen3 TTS 模型页面](https://www.together.ai/models/qwen3-tts-12hz-1-7b)[文本转语音文档](https://docs.together.ai/docs/text-to-speech)[Qwen 在 Hugging Face 上的模型卡](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice)

总结

- **Together AI 上的 Qwen3 TTS：** Qwen 的开放式文本转语音模型，基于 Together Serverless Inference 和专用端点，每 100 万个字符 20 美元。
- **一种声音，多种表达：** 九种预设声音，可以根据简单语言指令（例如“兴奋和乐观”）改变语气和情绪。
- **每种语音 10 种语言：** 每个预设都讲中文、英语、日语、韩语、德语、法语、俄语、葡萄牙语、西班牙语和意大利语。
- **专为实时语音而构建：**首个音频只需 97 毫秒，具有 HTTP 流和用于分段到达文本的 WebSocket API。

从今天开始，开发者可以在 Together AI 上运行 [Qwen3 TTS](https://www.together.ai/models/qwen3-tts-12hz-1-7b)，首个音频只需 97 毫秒。

Qwen3 TTS 是一种开放的文本转语音模型，可区分说话者和说话方式。您可以选择九种预设语音中的一种，当您使用简单语言指令（例如“兴奋和乐观”）更改其表达方式或在 10 种语言之间移动时，该语音保持不变。

AI 的推理团队共同调整了 Qwen3 TTS 的服务堆栈，以便语音能够足够快地开始流式传输，以进行实时对话。该模型现已在 Together Serverless Inference 和专用端点上可用。

## 告诉它如何说出这句话

同一句话可能会成为好消息或坏消息，具体取决于它的表达方式，而使用 Qwen3 TTS，您可以通过用几句话描述传递内容来决定是好消息还是坏消息。这里，语音 `aiden` 将一行读三遍。剪辑之间的声音和文字不会改变，只有指令会改变。

艾登 · 兴奋和乐观

0:02

“嗯，这改变了一切。”

艾登 · 愤怒且不耐烦

0:02

“嗯，这改变了一切。”

艾登 · 悲伤和失望

0:02

“嗯，这改变了一切。”

指令控制传送，并且声音保持您选择的声音。当您更改语言时，您也可以保持相同的声音。

## 在 10 种语言中保持同一个声音

每个预设语音均支持所有 10 种语言：中文、英语、日语、韩语、德语、法语、俄语、葡萄牙语、西班牙语和意大利语。这使得产品在进入新市场时可以保持相同的声音。这里 `aiden` 是英语语音，以四种语言读取相同的订单更新。

艾登 · 英语 (en)

0:03

“您的订单已发货，预计周四到达。”

艾登 · 西班牙语 (eng)

0:03

“您的订单已发货，预计周四到达。”

艾登·德语（二）

0:04

“您的订单已发货，应该会在周四到达。”

艾登·日语（是）

0:05

“对不起，对不起，我不知道该怎么办。”

以您选择的语言提供文本；上面的四个剪辑使用单独翻译的文本。每个语音还有一种母语，Qwen 建议使用母语语音以获得最佳质量，因此在选择预设之前先听听您的应用程序需要的语言。

## 在 VoiceFinder 中选择一个声音

选择预设的最快方法是听每个人说出自己的台词。 [VoiceFinder](https://voicefinder.together.ai/) 列出 Qwen3 TTS 语音，播放每个语音的样本并读取您在其中任何语音中输入的文本。

- 打开 [voicefinder.together.ai](https://voicefinder.together.ai/)，在模型菜单中选择 `Qwen/Qwen3-TTS-12Hz-1.7B`，然后选择 **查找声音**。
- 选择**预览**来播放语音样本。
- 选择 **尝试自定义文本**，输入最多 500 个字符，然后选择 **生成** 以听到语音朗读您的文本。用另一个声音重复，以在相同的文本上比较它们。
- 选择 **显示代码** 以使用 Python、TypeScript 或 cURL 获取对该语音的请求。

九种预设语音，以及每种语音的母语和 Qwen 的描述：

|语音|母语 |描述 |
| --- | --- | --- |
|艾登 |英语 |阳光美式男声，中音清晰 |
|瑞安 |英语 |充满活力的男声，节奏感强 |
|维维安 |中文 |明亮、略显前卫的年轻女声 |
|塞雷娜|中文 |温暖温柔的年轻女声|
|叔叔_fu |中文 |经验丰富的男声，音色低沉、圆润|
|迪伦 |汉语，北京话 |年轻的北京男声，音色清晰自然 |
|埃里克 |汉语，四川话 |活泼的成都男声，略带沙哑的亮度|
|小野安娜 |日语 |俏皮的日本女声，音色轻快灵活|
|苏熙 |韩语 |温暖的韩语女声，情感丰富|

## 生成语音

您需要 Together Python SDK (`pip install together`) 和 `TOGETHER_API_KEY`。这个请求将声音、语言和指令结合在一起，并产生了对上面这句话的兴奋的阅读。

```
from together import Together

client = Together()

response = client.audio.speech.create(
    model="Qwen/Qwen3-TTS-12Hz-1.7B",
    input="Well, that changes everything.",
    voice="aiden",  # who speaks
    language="en",  # the language of the text
    extra_body={"instructions": "excited and upbeat"},  # how to say it
    response_format="mp3",
)

response.write_to_file("excited.mp3")
```

Python SDK 通过 `instructions` 传递 `extra_body`。如果指令似乎没有更改交付，请检查该字段是否拼写为 `instructions`，因为拼写错误的字段会被跳过而不会出现错误。

该型号的参数：

|参数|送什么 |
| --- | --- |
|语音|九个声音名称之一，小写|
|说明 |对交付的简短描述，例如兴奋和乐观。可选|
|语言 |输入文本的 ISO 639-1 代码，例如 en、zh、ja 或 ko |
|响应格式 | wav、mp3、raw 或 mulaw。不支持 opus、aac 和 flac |
|采样率| 24000（默认）或 8000 |

Qwen3 TTS 不支持单词时间戳 (`alignment=word`)。

## 为语音代理传输音频

在语音代理中，必须在合成整个回复之前开始语音。在 Together AI 上，Qwen3 TTS 在短短 97 毫秒内返回第一个音频，并以两种方式传输。正确的方法取决于您提出请求时是否拥有全文。

### 当您拥有全文时：通过 HTTP 进行流式传输

对于 `stream=True` 和 `response_format="raw"`，语音 API 在生成音频时返回服务器发送的事件。每个 `conversation.item.audio_output.delta` 事件都携带一个 Base64 编码的音频块。该脚本接收流，解码每个块并将音频保存到文件中。

```
import base64
import json

from together import Together

client = Together()

with client.audio.speech.with_streaming_response.create(
    model="Qwen/Qwen3-TTS-12Hz-1.7B",
    input="Your order has shipped and should arrive on Thursday.",
    voice="aiden",
    language="en",
    extra_body={"instructions": "excited and upbeat"},
    stream=True,
    response_format="raw",
    response_encoding="pcm_s16le",
) as response, open("order-update.pcm", "wb") as audio:
    for line in response.iter_lines():
        if not line.startswith("data: {"):
            continue
        event = json.loads(line[len("data: "):])
        if event.get("type") == "conversation.item.audio_output.delta":
            # Each event carries a base64 chunk of 16-bit PCM at 24 kHz
            audio.write(base64.b64decode(event["delta"]))
```

输出为 24 kHz 的 16 位单声道 PCM，该指令适用于流式请求，就像适用于完整请求一样。要在语音到达时播放语音​​，请将每个解码的块发送到音频输出而不是文件。

### 当文本仍在写入时：WebSocket

如果文本来自语言模型标记，则 WebSocket 端点允许您将其分段发送。您打开一个连接，在文本可用时追加文本，并在输入完成后提交，服务器在获得整个句子后合成每个句子。该脚本分两部分发送订单更新并保存返回的音频。它需要 `websockets` 软件包、版本 14 或更高版本 (`pip install websockets`)。

```
import asyncio
import base64
import json
import os

import websockets

URL = (
    "wss://api.together.ai/v1/audio/speech/websocket"
    "?model=Qwen/Qwen3-TTS-12Hz-1.7B&voice=aiden&language=en"
    "&response_format=pcm&sample_rate=24000"
)


async def main():
    headers = {"Authorization": f"Bearer {os.environ['TOGETHER_API_KEY']}"}
    async with websockets.connect(URL, additional_headers=headers) as ws:
        # Append text as it becomes available, then commit once the input is complete
        await ws.send(json.dumps({"type": "input_text_buffer.append", "text": "Your order has shipped. "}))
        await ws.send(json.dumps({"type": "input_text_buffer.append", "text": "It should arrive on Thursday."}))
        await ws.send(json.dumps({"type": "input_text_buffer.commit"}))

        with open("order-update.pcm", "wb") as audio:
            async for message in ws:
                event = json.loads(message)
                if event["type"] == "conversation.item.audio_output.delta":
                    # Each event carries a base64 chunk of 16-bit PCM at 24 kHz
                    audio.write(base64.b64decode(event["delta"]))
                elif event["type"] == "conversation.item.audio_output.done":
                    break
                elif event["type"] == "conversation.item.tts.failed":
                    raise RuntimeError(event["error"])


asyncio.run(main())
```

连接 URL 携带模型、语音、语言和音频设置（WebSocket 端点名为原始 PCM `pcm`），并且音频以与 HTTP 流相同的 base64 事件到达。 [WebSocket 指南](https://docs.together.ai/docs/inference/text-to-speech/websocket) 列出了每种消息类型。

## 开始吧

- 比较[VoiceFinder](https://voicefinder.together.ai/)中的声音
- 阅读[文本转语音文档](https://docs.together.ai/docs/text-to-speech)、[流媒体指南](https://docs.together.ai/docs/inference/text-to-speech/streaming) 和 [WebSocket 指南](https://docs.together.ai/docs/inference/text-to-speech/websocket)
- 查看[Qwen3 TTS模型页面](https://www.together.ai/models/qwen3-tts-12hz-1-7b)
- 阅读Qwen的[Hugging Face上的模型卡](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice)

现已上市

在 Together AI 上运行 Qwen3 TTS

九种预设语音 · 10 种语言 · 每 100 万字符 20 美元

比较声音

## 常见问题解答

### Together AI 上的 Qwen3 TTS 费用是多少？

Qwen3 TTS 在 Together Serverless Inference 上每 100 万个字符的成本为 20 美元。该模型也可在专用端点上使用。

### Qwen3 TTS 在 Together AI 上的速度有多快？

当您在我们的推理团队针对实时语音进行调整的服务堆栈上流式传输响应时，Qwen3 TTS 在 Together AI 上会在短短 97 毫秒内返回第一个音频。

### 如何控制 Qwen3 TTS 语音的语气？

在语音请求的 `instructions` 字段中发送交付的简单语言描述，例如 `excited and upbeat`。在Python SDK中，通过`extra_body`传递。指令会改变声音的情绪和语气，但不会改变听起来像谁。

### 一个 Qwen3 TTS 语音可以说多种语言吗？

是的，九种 Qwen3 TTS 预设语音中的每一种都可以说所有 10 种支持的语言。将 `voice` 设置为语音名称，将 `language` 设置为文本语言，并以该语言发送文本。 Qwen 建议使用每种声音的母语以获得最佳质量。

### Qwen3 TTS 是否支持 Together AI 上的串流？

是的，Qwen3 TTS 通过两种方式支持 Together AI 上的流式传输。通过 HTTP，将 `stream` 设置为 `true`，将 `response_format` 设置为 `raw`，以接收服务器发送的带有 Base64 编码 PCM 音频的事件。通过 WebSocket，分段发送文本并接收生成的音频。

### Qwen3 TTS 返回哪些音频格式？

Qwen3 TTS 在 Together AI 上以 24000（默认）或 8000 的采样率返回 `wav`、`mp3`、`raw` (PCM) 或 `mulaw` 音频。它不返回 `opus`、`aac` 或 `flac`。

### 在选择之前如何比较 Qwen3 TTS 语音？

打开[VoiceFinder](https://voicefinder.together.ai/)并在型号菜单中选择`Qwen/Qwen3-TTS-12Hz-1.7B`。您可以预览每个语音并用它生成最多 500 个字符的您自己的文本。

### Qwen3 TTS 开源吗？

是的，Qwen 在 Apache 2.0 许可证下发布了 Qwen3 TTS 12Hz 1.7B。重量位于Hugging Face上。

## 相关文章
