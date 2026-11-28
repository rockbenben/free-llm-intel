---
vendor: together_ai
title: Qwen3 TTS is now available on Together AI
original_title: 
url: https://www.together.ai/blog/qwen3-tts
date: 2026-11-20
lang: zh
captured: 2026-11-21
extractor: readability-v1
translator: agent
status: translated
body_sha: 159e5cc43539
---


模型库

发布于 11/20/2026

# Qwen3 TTS 现已在 Together AI 上线

在整个产品里沿用同一个声音，用一句自然语言指令改变它的语气，还能在 10 种语言之间切换，首个音频最快 97ms 返回。

- 作者：Anthony Ji、Charles Duong、Sebastien Beurnier、Sahil Yadav、Sonny Khan
- 本文中的链接[在 VoiceFinder 中对比声音](https://voicefinder.together.ai/)[Qwen3 TTS 模型页](https://www.together.ai/models/qwen3-tts-12hz-1-7b)[文本转语音文档](https://docs.together.ai/docs/text-to-speech)[Qwen 在 Hugging Face 上的 model card](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice)

摘要

- **Qwen3 TTS on Together AI：** Qwen 的开源文本转语音模型，可在 Together Serverless Inference 和专用 endpoint 上使用，每 1M 字符收费 \$20。
- **一个声音，多种表达：** 九个预设声音，可用一句自然语言指令——比如 "excited and upbeat"——改变语气和情绪。
- **每个声音都能说 10 种语言：** 每个预设都能讲中文、英语、日语、韩语、德语、法语、俄语、葡萄牙语、西班牙语和意大利语。
- **为实时语音而设计：** 首个音频最快 97ms 返回，支持 HTTP 流式传输，并为分段到达的文本提供 WebSocket API。

从今天起，开发者可以在 Together AI 上运行 [Qwen3 TTS](https://www.together.ai/models/qwen3-tts-12hz-1-7b)，首个音频最快 97ms 返回。

Qwen3 TTS 是一个开源的文本转语音模型，它把"谁在说"和"怎么说"分开。你从九个预设声音里挑一个，这个声音本身保持不变，只靠一句自然语言指令（比如 "excited and upbeat"）改变它的表达方式，或者让它换到 10 种语言中的任意一种。

Together AI 的推理团队针对 Qwen3 TTS 调优了服务栈，使语音能以足够快的速度开始流式输出，撑得住实时对话。该模型现已在 Together Serverless Inference 和专用 endpoint 上提供。

## 告诉它这句话该怎么念

同一句话，念法不同，听起来可能是好消息也可能是坏消息；用 Qwen3 TTS，你只要用几个词描述表达方式就能决定是哪一种。下面 `aiden` 把同一句话读了三遍，各段音频之间声音和文字都不变，变的只有指令。

aiden · 兴奋而轻快


0:02

"好吧，这一下全变了。"

aiden · 愤怒而不耐烦


0:02

"好吧，这一下全变了。"

aiden · 难过而失望


0:02

"好吧，这一下全变了。"

指令控制的是念法，声音始终是你选定的那一个。换语言时也可以沿用同一个声音。

## 一个声音走遍 10 种语言

每个预设声音都能说全部 10 种受支持的语言：中文、英语、日语、韩语、德语、法语、俄语、葡萄牙语、西班牙语和意大利语。这样产品进入新市场时，可以继续用同一个声音。下面 `aiden` 这个英语声音，用四种语言读同一条订单更新。

aiden · 英语（en）


0:03

"您的订单已发货，预计周四送达。"

aiden · 西班牙语（es）


0:03

"Tu pedido ha sido enviado y debería llegar el jueves."

aiden · 德语（de）


0:04

"Ihre Bestellung wurde versandt und sollte am Donnerstag ankommen."

aiden · 日语（ja）


0:05

"ご注文の商品は発送済みで、木曜日に到着する予定です。"

文本要用你所选的语言提供；上面四段音频的文本分别是翻译过的。每个声音还有一个母语，Qwen 建议在母语下使用以获得最佳质量，因此在定下某个预设之前，先听听你的应用所需要的那几种语言。

## 在 VoiceFinder 中挑选声音

挑预设最快的办法，是听每个声音念你自己写的句子。[VoiceFinder](https://voicefinder.together.ai/) 列出了 Qwen3 TTS 的全部声音，可逐个试听样例，也能用它任意一个声音读出你输入的文本。

- 打开 [voicefinder.together.ai](https://voicefinder.together.ai/)，在模型菜单中选择 `Qwen/Qwen3-TTS-12Hz-1.7B`，然后点 **Find voices**。
- 点 **Preview** 试听某个声音的样例。
- 点 **Try custom text**，输入最多 500 个字符，再点 **Generate**，就能听到该声音朗读你的文本。换一个声音重复一次，即可用同一段文本做对比。
- 点 **Show code**，可获得该声音在 Python、TypeScript 或 cURL 下的请求代码。

九个预设声音，以及各自的母语和 Qwen 的描述：

| 声音 | 母语 | 描述 |
| --- | --- | --- |
| aiden | 英语 | 阳光的美式男声，中频清晰 |
| ryan | 英语 | 富有动感的男声，节奏驱动力强 |
| vivian | 中文 | 明亮、略带锋芒的年轻女声 |
| serena | 中文 | 温暖柔和的年轻女声 |
| uncle_fu | 中文 | 老练的男声，低沉稳厚的音色 |
| dylan | 中文、北京话 | 年轻的北京男声，音色清晰自然 |
| eric | 中文、四川话 | 活泼的成都男声，略带沙哑的明亮感 |
| ono_anna | 日语 | 俏皮的日语女声，音色轻盈灵动 |
| sohee | 韩语 | 温暖的韩语女声，情感丰沛 |

## 生成语音

你需要 Together Python SDK（`pip install together`）和一个 `TOGETHER_API_KEY`。下面这个请求把声音、语言和指令一起设好，产出的就是前文那句话的兴奋版读法。

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

Python SDK 通过 `extra_body` 传递 `instructions`。如果某条指令看起来没改变念法，先检查字段名是否拼作 `instructions`——拼错的字段会被静默跳过，不会报错。

该模型的参数：

| 参数 | 该传什么 |
| --- | --- |
| voice | 九个声音名之一，小写 |
| instructions | 对念法的简短描述，例如 excited and upbeat。可选 |
| language | 输入文本的 ISO 639-1 代码，例如 en、zh、ja、ko |
| response_format | wav、mp3、raw 或 mulaw。不支持 opus、aac 和 flac |
| sample_rate | 24000（默认）或 8000 |

Qwen3 TTS 不支持 word timestamps（`alignment=word`）。

## 为语音 agent 流式输出音频

在语音 agent 里，语音必须在整段回复合成完之前就开始播放。在 Together AI 上，Qwen3 TTS 首个音频最快 97ms 返回，并有两种流式方式；用哪种取决于你发起请求时是否已经拿到全文。

### 已有全文：走 HTTP 流式

设置 `stream=True` 和 `response_format="raw"` 后，语音 API 会在生成音频的同时返回 server-sent events，每个 `conversation.item.audio_output.delta` 事件携带一段 base64 编码的音频。下面的脚本接收这个流，解码每个分片并写入文件。

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

输出是 24 kHz 的 16 位单声道 PCM；指令对流式请求的作用方式与对完整请求一样。若想边收边播，把每个解码后的分片直接送到音频输出，而不是写入文件。

### 文本还在生成：用 WebSocket

如果文本来自语言模型、是一个 token 一个 token 产生的，WebSocket endpoint 允许你分片发送。你打开一条连接，文本可用时就追加，输入完成后 commit，服务端拿到整句后便对该句做合成。下面的脚本分两段发送一条订单更新，并保存返回的音频。它需要 `websockets` 包，版本 14 或更高（`pip install websockets`）。

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

连接 URL 里带着模型、声音、语言和音频设置（WebSocket endpoint 把裸 PCM 称作 `pcm`），音频以与 HTTP 流相同的 base64 事件到达。[WebSocket 指南](https://docs.together.ai/docs/inference/text-to-speech/websocket) 列出了全部消息类型。

## 开始使用

- 在 [VoiceFinder](https://voicefinder.together.ai/) 中对比这些声音
- 阅读[文本转语音文档](https://docs.together.ai/docs/text-to-speech)、[流式指南](https://docs.together.ai/docs/inference/text-to-speech/streaming) 和 [WebSocket 指南](https://docs.together.ai/docs/inference/text-to-speech/websocket)
- 查看 [Qwen3 TTS 模型页](https://www.together.ai/models/qwen3-tts-12hz-1-7b)
- 阅读 Qwen 在 Hugging Face 上的 [model card](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice)

现已可用

在 Together AI 上运行 Qwen3 TTS

九个预设声音 · 10 种语言 · 每 1M 字符 \$20

对比这些声音

## 常见问题

### Qwen3 TTS 在 Together AI 上怎么收费？

Qwen3 TTS 在 Together Serverless Inference 上每 1M 字符收费 \$20。该模型在专用 endpoint 上也可用。

### Qwen3 TTS 在 Together AI 上有多快？

在 Together AI 上做流式返回时，Qwen3 TTS 首个音频最快 97ms 返回，所用服务栈由我们的推理团队为实时语音调优。

### 怎么控制 Qwen3 TTS 声音的语气？

在语音请求的 `instructions` 字段里用自然语言描述念法，例如 `excited and upbeat`；在 Python SDK 中通过 `extra_body` 传入。指令会改变声音的情绪和语气，但不改变它听起来像谁。

### 一个 Qwen3 TTS 声音能说多种语言吗？

能。九个 Qwen3 TTS 预设声音每一个都能说全部 10 种受支持语言。把 `voice` 设为声音名、`language` 设为文本的语言，并以该语言发送文本。Qwen 建议在母语下使用各声音以获得最佳质量。

### Qwen3 TTS 在 Together AI 上支持流式吗？

支持，有两种方式。HTTP 上把 `stream` 设为 `true`、`response_format` 设为 `raw`，即可收到携带 base64 编码 PCM 音频的 server-sent events。WebSocket 上分片发送文本，边生成边接收音频。

### Qwen3 TTS 返回哪些音频格式？

在 Together AI 上，Qwen3 TTS 返回 `wav`、`mp3`、`raw`（PCM）或 `mulaw` 音频，采样率为 24000（默认）或 8000。它不返回 `opus`、`aac` 或 `flac`。

### 选定之前怎么对比 Qwen3 TTS 的各个声音？

打开 [VoiceFinder](https://voicefinder.together.ai/)，在模型菜单中选择 `Qwen/Qwen3-TTS-12Hz-1.7B`。你可以预览每个声音，并用它生成最多 500 个字符的自定义文本。

### Qwen3 TTS 是开源的吗？

是。Qwen 以 Apache 2.0 许可发布了 Qwen3 TTS 12Hz 1.7B，权重在 Hugging Face 上。

## 相关文章
