---
vendor: huggingface
title: FastRTC：面向 Python 的实时通信库
original_title: FastRTC: The Real-Time Communication Library for Python
url: https://huggingface.co/blog/fastrtc
date: 2025-01-12
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: 095ead981d3e
---

# FastRTC：面向 Python 的实时通信库

Freddy Boulton（freddyaboulton）、Abubakar Abid（abidlabs）

过去几个月里，涌现了许多新的实时语音模型，围绕开源和闭源模型甚至成立了整整一批公司。举几个里程碑：

- OpenAI 和 Google 发布了它们面向 ChatGPT 和 Gemini 的实时多模态 API。OpenAI 甚至放出了一个 1-800-ChatGPT 的电话号码！
- Kyutai 发布了 [Moshi](https://huggingface.co/kyutai)，一个完全开源的音频到音频 LLM。Alibaba 发布了 [Qwen2-Audio](https://huggingface.co/Qwen/Qwen2-Audio-7B-Instruct)，Fixie.ai 发布了 [Ultravox](https://huggingface.co/fixie-ai/ultravox-v0_5-llama-3_3-70b)——两个原生理解音频的开源 LLM。
- ElevenLabs 在 Series C 中[融资 1.8 亿美元](https://elevenlabs.io/blog/series-c)。

尽管模型和融资这一侧爆发式增长，构建能流式传输音频和视频的实时 AI 应用仍然很难，尤其是在 Python 里。

- 机器学习工程师可能不具备构建实时应用所需的技术经验，例如 WebRTC。
- 即便是 Cursor 和 Copilot 这样的代码助手工具，也很难写出支持实时音视频应用的 Python 代码。我可是亲身领教过！

这就是为什么我们很高兴宣布 `FastRTC`——面向 Python 的实时通信库。这个库的设计目标，是让用纯 Python 构建实时音视频 AI 应用变得极其简单！

在这篇博客中，我们会通过构建实时音频应用来讲 `FastRTC` 的基础。读完你会理解 `FastRTC` 的核心特性：

- 🗣️ 内置自动语音检测与话轮切换，你只需操心回应用户的逻辑。
- 💻 自动 UI——内置支持 WebRTC 的 Gradio UI，用于测试（或直接部署到生产！）。
- 📞 电话接入——用 fastphone() 可获得一个免费电话号码来拨打进入你的音频流（需要 HF Token，PRO 账号有更高额度）。
- ⚡️ 支持 WebRTC 和 Websocket。
- 💪 可定制——你可以把流挂载到任意 FastAPI app 上，从而提供自定义 UI 或在 Gradio 之外部署。
- 🧰 大量文本转语音、语音转文本、停用词检测的工具，帮你快速上手。

开始吧。

## 快速上手

我们先构建实时音频界的"hello world"：把用户说的话原样回传。在 `FastRTC` 里，这简单到：

```
from fastrtc import Stream, ReplyOnPause
import numpy as np

def echo(audio: tuple[int, np.ndarray]) -> tuple[int, np.ndarray]:
    yield audio

stream = Stream(ReplyOnPause(echo), modality="audio", mode="send-receive")
stream.ui.launch()
```

拆解一下：

- `ReplyOnPause` 会替你处理语音检测和话轮切换。你只需要操心回应用户的逻辑。任何返回一个音频元组（表示为 `(sample_rate, audio_data)`）的生成器都能用。
- `Stream` 类会为你构建一个 Gradio UI，方便快速测试你的流。原型做完之后，你可以用一行代码把 Stream 部署为可用于生产的 FastAPI app——`stream.mount(app)`，其中 `app` 是一个 FastAPI app。

运行效果如下：

## 进阶：LLM 语音聊天

再上一层是用 LLM 来响应用户。`FastRTC` 内置语音转文本和文本转语音能力，所以和 LLM 配合非常容易。我们相应地改一下 `echo` 函数：

```
import os

from fastrtc import (ReplyOnPause, Stream, get_stt_model, get_tts_model)
from openai import OpenAI

sambanova_client = OpenAI(
    api_key=os.getenv("SAMBANOVA_API_KEY"), base_url="https://api.sambanova.ai/v1"
)
stt_model = get_stt_model()
tts_model = get_tts_model()

def echo(audio):
    prompt = stt_model.stt(audio)
    response = sambanova_client.chat.completions.create(
        model="Meta-Llama-3.2-3B-Instruct",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
    )
    prompt = response.choices[0].message.content
    for audio_chunk in tts_model.stream_tts_sync(prompt):
        yield audio_chunk

stream = Stream(ReplyOnPause(echo), modality="audio", mode="send-receive")
stream.ui.launch()
```

我们这里用 SambaNova API，因为它快。`get_stt_model()` 会拉取 [Moonshine Base](https://huggingface.co/UsefulSensors/moonshine-base)，`get_tts_model()` 会从 Hub 拉取 [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M)，两者都为设备端 CPU 推理做了进一步优化。但你也可以用任何 LLM/文本转语音/语音转文本 API，甚至语音到语音的模型。带上你趁手的工具就行——`FastRTC` 只负责实时通信这一层。

## 附赠：电话接入

如果你不调用 `stream.ui.launch()` 而改调 `stream.fastphone()`，你会得到一个免费号码来拨打进入你的流。注意，需要一个 Hugging Face token，PRO 账号有更高额度。

你会在终端里看到类似这样的内容：

```
INFO:	  Your FastPhone is now live! Call +1 877-713-4471 and use code 530574 to connect to your stream.
INFO:	  You have 30:00 minutes remaining in your quota (Resetting on 2025-03-23)
```

然后你拨打这个号码，它就能把你接入你的流！

## 下一步

- 阅读[文档](https://fastrtc.org/)了解更多 `FastRTC` 基础。
- 最好的上手方式是看 [cookbook](https://fastrtc.org/cookbook)。你会了解如何与流行的 LLM 提供商集成（包括 OpenAI 和 Gemini 的实时 API）、如何把你的流与 FastAPI app 集成并做自定义部署、如何从你的 handler 返回额外数据、如何做视频处理，等等！
- ⭐️ 给 [repo](https://github.com/freddyaboulton/fastrtc) 加星，并提交 bug 和需求 issue！
- 关注 HuggingFace 上的 [FastRTC Org](https://huggingface.co/fastrtc) 获取更新，并查看已部署的示例！

感谢你来了解 `FastRTC`！
