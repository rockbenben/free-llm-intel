---
vendor: openrouter
title: 如何构建语音 AI agent
original_title: 
url: https://openrouter.ai/blog/tutorials/build-voice-ai-agent
date: 2026-11-10
lang: zh
captured: 2026-11-11
extractor: readability-v1
translator: agent
status: translated
body_sha: eddba098c66b
---

OpenRouter ·11/10/2026

![如何构建语音 AI agent](https://openrouter.ai/blog/images/build-voice-ai-agent.png)![如何构建语音 AI agent](https://openrouter.ai/blog/images/build-voice-ai-agent-dark.png)

语音 agent 要做的远不止给出一句漂亮回答。它得听懂对方说了什么，决定该做什么，调用需要的工具，还要在停顿变得尴尬之前重新开口。

在本教程里，我们用 Python 把这套完整闭环搭出来。示例是一个餐厅预订 agent：把来电者的话转成文字，用工具查空桌，再把回复变回语音。语音转文本、LLM 和文本转语音都走同一个 [OpenRouter API 密钥](https://openrouter.ai/docs/api_reference/authentication)，而且我们把每个成句流式送给 TTS，不必等整段回复生成完。

在三次测试对话的全部 12 个回合里，服务器端首个音频的总体中位时间是 1.9 秒；按 10 月 8 日测试时的促销价计算，四回合对话每分钟处理语音约需 $0.013。

## TL;DR

- 文本转语音约占实测模型成本的 90%，因此语音回复的长度是这个 agent 一个重要的成本因素。
- 在我们的测试里，按每回合一次 LLM 请求计算，服务器端首个音频的时间估计普通回合为 1.4 秒、工具回合为 2.4 秒。示例代码会多发出几次 LLM 请求，网络传输和播放也会额外耗时。
- 姓名比电话号码更难转录准确。在采取行动之前，让来电者确认重要细节。
- 把成句直接送给文本转语音（TTS）能缩短语音输出的等待，但实时播放和打断还需要额外的编排。

## 语音 AI agent 的一轮如何工作

语音 agent 接住来电者的语音，转成文本，交给 LLM 决定下一步，再把回复变回语音。整个流程是这样的：

![语音 AI agent 一个回合的示意图：来电者音频先到语音转文本，再经过 LLM、句子切分、文本转语音，最后成为 agent 音频。LLM 可以调用预订工具 check_availability 和 book_table，并带着工具结果继续。](https://openrouter.ai/blog/images/build-voice-ai-agent-1.png)

比如有人打电话到餐厅订位时，LLM 可能需要先调用 check_availability 再作答。你的应用执行这个函数，把可订时间回传给模型，等它生成回复。这多出来的一来一回，会拉长来电者的等待。

要缩短这段等待，可以在 LLM 写完整个回复之前就开始生成语音。不必等全文：我们流式读取回复、按句切分，在模型继续生成余下内容的同时，把每个成句送给 TTS。

这次构建里，我们用[语音转文本 API](https://openrouter.ai/docs/guides/overview/multimodal/stt)转录来电者，用[带工具调用的 Chat Completions](https://openrouter.ai/docs/guides/features/tool-calling)处理对话和订位，再用[文本转语音 API](https://openrouter.ai/docs/guides/overview/multimodal/tts)生成语音回复。

转录 API 返回 JSON 文本，语音 API 返回音频字节。我们的 Python 示例会把生成的音频存成 WAV 文件，稍后再用 LiveKit 处理实时音频和打断。

## 用 Python 构建语音 agent

我们用三个模型来搭这个餐厅预订 agent：elevenlabs/scribe-v2 负责转录，openai/gpt-6-luna 负责对话和工具调用，elevenlabs/eleven-flash-v2.5 负责生成语音。

你需要 Python 3.10 或更高版本，以及一个 [OpenRouter API 密钥](https://openrouter.ai/settings/keys)。安装 requests 库，并把 API 密钥设成环境变量：

```
python -m pip install requests
export OPENROUTER_API_KEY="your-api-key"
```

为了让示例容易复现，我们不接麦克风，而是用第二个 TTS 语音模拟四轮来电。预订数据也用模拟的，这样 agent 无需真实预订系统就能查空桌、返回订位详情。

把下面这段代码存为 voice_agent.py：

```
import base64
import io
import json
import os
import re
import wave
from concurrent.futures import ThreadPoolExecutor
from datetime import date

import requests

API = "https://openrouter.ai/api/v1"
AUTH = {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"}

STT = "elevenlabs/scribe-v2"
LLM = "openai/gpt-6-luna"
TTS = "elevenlabs/eleven-flash-v2.5"
PCM_RATE = 24000

def system_prompt():
    today = date.today()  # read per call, so a long-running agent stays on the right day
    return (
        "You are the phone receptionist for Luigi's restaurant. "
        f"Today is {today:%A, %B} {today.day}, {today.year}. Keep answers short and spoken: "
        "no markdown, and say times in words. Check availability before "
        "offering a table. Only book after the caller agrees and provides a name. "
        "Do not claim to send confirmation texts."
    )

def tool(name, description, properties):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": list(properties),
            },
        },
    }

DATE = {"type": "string", "description": "YYYY-MM-DD"}
TIME = {"type": "string", "description": "HH:MM, 24-hour"}
PARTY = {"type": "integer", "minimum": 1}

TOOLS = [
    tool(
        "check_availability",
        "Find open tables near the requested time",
        {"date": DATE, "time": TIME, "party_size": PARTY},
    ),
    tool(
        "book_table",
        "Book only after the caller accepts a time and gives a name",
        {
            "date": DATE,
            "time": TIME,
            "party_size": PARTY,
            "name": {"type": "string"},
        },
    ),
]

def run_tool(name, args):
    # Mock booking service; replace with a real reservation backend.
    if name == "check_availability":
        return {
            "open_times": (
                ["17:45", "20:15"]
                if args["party_size"] >= 5
                else [args["time"]]
            )
        }

    if name == "book_table":
        allowed = (
            ["17:45", "20:15"]
            if args["party_size"] >= 5
            else [args["time"]]
        )
        return (
            {"booked": True, "reference": "XJ47Q"}
            if args["time"] in allowed
            else {"booked": False, "error": "Time unavailable"}
        )

    return {"error": f"Unknown tool: {name}"}

def to_wav(pcm, rate):
    if len(pcm) % 2:
        raise ValueError("PCM audio must contain whole 16-bit samples")
    output = io.BytesIO()
    with wave.open(output, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(pcm)
    return output.getvalue()

def speak(text, voice="sarah"):
    if not text.strip():
        return b"", PCM_RATE

    with requests.post(
        f"{API}/audio/speech",
        headers=AUTH,
        stream=True,
        timeout=60,
        json={
            "model": TTS,
            "input": text,
            "voice": voice,
            "response_format": "pcm",
            "provider": {
                "options": {
                    "elevenlabs": {"output_format": "pcm_24000"}
                }
            },
        },
    ) as response:
        response.raise_for_status()
        if not response.headers.get("Content-Type", "").startswith("audio/pcm"):
            raise ValueError("Expected raw PCM audio from TTS")
        pcm = b"".join(response.iter_content(4096))
        if not pcm:
            raise ValueError("TTS returned no audio")
        return pcm, PCM_RATE

def transcribe(wav):
    response = requests.post(
        f"{API}/audio/transcriptions",
        headers=AUTH,
        timeout=60,
        json={
            "model": STT,
            "language": "en",
            "input_audio": {
                "data": base64.b64encode(wav).decode("ascii"),
                "format": "wav",
            },
        },
    )
    response.raise_for_status()
    return response.json()["text"].strip()

def choose_tool_calls(messages):
    # Resolve possible tools before starting any paid TTS requests.
    response = requests.post(
        f"{API}/chat/completions",
        headers=AUTH,
        timeout=60,
        json={
            "model": LLM,
            "messages": messages,
            "tools": TOOLS,
            "tool_choice": "auto",
            "reasoning": {"effort": "none"},
            "max_tokens": 300,
        },
    )
    response.raise_for_status()
    message = response.json()["choices"][0]["message"]
    return message.get("tool_calls") or []

def stream_reply(messages):
    # This request has no tools, so sentences can safely go to TTS.
    pending, finish = "", None
    with requests.post(
        f"{API}/chat/completions",
        headers=AUTH,
        stream=True,
        timeout=60,
        json={
            "model": LLM,
            "messages": messages,
            "reasoning": {"effort": "none"},
            "max_tokens": 300,
            "stream": True,
        },
    ) as response:
        response.raise_for_status()
        response.encoding = "utf-8"

        for line in response.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: {"):
                continue

            chunk = json.loads(line[6:])
            if chunk.get("error"):  # a provider error mid-stream, after some text may have arrived
                raise RuntimeError(f"stream error: {chunk['error']}")
            choices = chunk.get("choices")
            if not choices:
                continue

            finish = choices[0].get("finish_reason") or finish
            pending += (choices[0].get("delta") or {}).get("content") or ""
            # Wait for whitespace; a buffer ending in "3." may still become "3.14".
            while match := re.search(r"[.!?]\s", pending):
                sentence = pending[:match.end()].strip()
                if sentence:
                    yield sentence
                pending = pending[match.end():]

    if finish == "length":  # hit max_tokens, so don't speak the clipped tail or save the reply as a full answer
        raise RuntimeError("reply cut off at max_tokens")
    if pending.strip():
        yield pending.strip()

def run_turn(caller_wav, messages):
    heard = transcribe(caller_wav)
    messages.append({"role": "user", "content": heard})

    # Tool selection can repeat when the model needs several tool results.
    for _ in range(4):
        calls = choose_tool_calls(messages)
        if not calls:
            break

        messages.append({"role": "assistant", "content": None, "tool_calls": calls})
        for call in calls:
            try:
                args = json.loads(call["function"]["arguments"])
                result = run_tool(call["function"]["name"], args)
            except (ValueError, TypeError, KeyError) as exc:
                result = {"error": str(exc)}
            messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": json.dumps(result),
            })
    else:
        raise RuntimeError("Too many tool calls")

    sentences, jobs = [], []
    with ThreadPoolExecutor(max_workers=3) as pool:
        for sentence in stream_reply(messages):
            sentences.append(sentence)
            jobs.append(pool.submit(speak, sentence))
        audio = [job.result() for job in jobs]

    if not sentences:
        raise RuntimeError("LLM returned no spoken response")

    rates = {rate for _, rate in audio}
    if rates != {PCM_RATE}:
        raise ValueError("Inconsistent TTS sample rates")

    spoken = " ".join(sentences)
    messages.append({"role": "assistant", "content": spoken})
    pcm = b"".join(chunk for chunk, _ in audio)
    return heard, spoken, to_wav(pcm, PCM_RATE)

if __name__ == "__main__":
    caller_lines = [
        "Hi, do you have a table for six this Saturday at seven thirty?",
        "Eight fifteen works. The name is Siobhan Okafor.",
        "Can you text the confirmation to four one five, "
        "five five five, zero one eight two?",
        "No, that's everything. Thanks, bye.",
    ]

    messages = [{"role": "system", "content": system_prompt()}]
    for turn, line in enumerate(caller_lines, 1):
        pcm, rate = speak(line, voice="george")
        heard, said, reply = run_turn(to_wav(pcm, rate), messages)
        with open(f"agent_{turn}.wav", "wb") as file:
            file.write(reply)
        print(f"caller: {heard}\nagent:  {said}\n")
```

脚本通过 run_turn() 把三个 API 串起来：转录每条来电消息，把转录文本交给 LLM，再处理回复。如果 LLM 请求调用工具，这个函数就执行它、把结果加进对话历史，然后再次发起请求让模型接着走。

看看 stream_reply() 怎么处理工具调用。模型把函数名和参数按片段流式吐出，所以要先拼完整再执行工具。至于语音回复，我们通过线程池把成句送给 TTS，让语音生成和 LLM 余下的输出重叠进行。

随后按句子顺序把音频拼起来，存成 WAV 文件。真正的播放和打断，等引入 LiveKit 时再处理。

用这条命令运行脚本：

```
python voice_agent.py
```

它会生成四个音频文件，agent_1.wav 到 agent_4.wav，并打印整段对话。下面是我们某次测试的片段。caller 那几行是转录出来的音频内容，所以数字可能和当时说的不一样。

```
caller: Hi, do you have a table for six this Saturday at 7:30?

agent:  We don't have seven-thirty available for six,
        but I can offer five forty-five or eight fifteen.
        Would either work for you?

caller: 815 works. The name is Siobhan Okafor

agent:  You're booked for six at eight fifteen this
        Saturday under Siobhan Okafor.
        Your reference is XJ47Q.

caller: Can you text the confirmation to 415-555-0182?

agent:  I can't send texts from here, but your
        reservation is confirmed under Siobhan Okafor
        for six at eight fifteen this Saturday,
        reference XJ47Q.
```

这个例子里，agent 先查空桌再报出别的时间，等来电者接受后才调用 book_table。它也不肯承诺发短信确认，因为我们没有提供发短信的工具。

## 这套设计为什么成立，又会在哪里失效

一段回复在聊天窗口里看着挺正常，读出来却可能很别扭，时间、电话号码和 markdown 都是典型。所以我们的 system prompt 要求 LLM 把回复压短、不用格式、把时间写成口语词，比如用 “eight fifteen” 而不用 8:15。

同样的问题也会反过来出现。在我们的测试里，语音转文本把 “eight fifteen” 转成了 815，但 LLM 还是正确理解了来电者的回答，因为它有前面的对话作上下文。我们把这段历史放在 messages 里，随每次请求一起发送——Chat Completions 不会自动保留之前的回合。结果 prompt 从第一回合约 290 个 token 涨到第四回合的 490 个 token。

另一个要点是：确保 agent 只确认真实发生过的操作。早期没有 book_table 的版本里，应用根本没建预订，agent 却会告诉来电者订位已确认。

所以预订工具不能只是返回一个响应。接上真实预订系统后，它应该先核实空桌、保存订位，只有操作成功才返回确认。

## 语音 AI agent 有多快？

全部 12 个回合里，服务器端首个音频的时间中位数是 1.9 秒。按回合类型分开看，不调用工具时中位数 1.4 秒，agent 需要调工具时 2.4 秒。

我们测量了三段完整对话、共 12 个回合，借助[生成元数据](https://openrouter.ai/docs/api/api-reference/generations/get-generation)估算每个阶段的服务器端延迟。这样就能把模型处理时间和测试环境里额外的网络开销分开。

结果对比如下：

| **阶段** | **有工具调用** | **无工具调用** |
| --- | --- | --- |
| 语音转文本 (Scribe v2) | 549 ms | 391 ms |
| LLM 选择工具 | 736 ms | — |
| LLM 回答，首个 token | 685 ms | 706 ms |
| 文本转语音，首个字节 | 262 ms | 208 ms |
| **首个音频的预计时间** | **2.4 s** | **1.4 s** |

多出来的那次 LLM 请求是差距的主要来源。agent 要查空桌时，必须等工具结果回来才能生成回答。

这些数字反映的是服务器端处理，不是来电者感受到的完整耗时。网络传输、判断来电者是否说完、音频播放都会再添延迟；各阶段的中位数也未必能加总出总体中位数。估算还按每回合一次 LLM 请求计算。下面的示例代码每回合会发两次——先一次非流式请求查工具调用，再一次流式请求取回复；工具回合在工具跑完后还会再发一次，所以实际会比这些数字更慢。

下面的模型对比用的是另外的测试运行和输入，因此报告里的延迟与这里整段对话的测量结果不一样。

## 语音 AI agent 要花多少钱？

五次运行里，四回合的餐厅对话成本在 **$0.0069 到 $0.0087** 之间。每通通话约含 38 秒语音，按 2026 年 10 月 8 日的价格估算，成本为 **每分钟处理语音 $0.013**。

这笔成本大头在生成 agent 的语音。

| **阶段** | **占总成本的比例** | **测试期间的价格** |
| --- | --- | --- |
| 文本转语音 (Eleven Flash v2.5) | 90% | $20 / million characters |
| 语音转文本 (Scribe v2) | 6% | $0.11 / audio hour |
| LLM (GPT-6 Luna) | 4% | $0.10 / $0.50 per million input/output tokens |

上面的 ElevenLabs 价格含 50% 首发折扣，折扣已于 2026 年 10 月 19 日结束。按常规标价，[Eleven Flash v2.5](https://openrouter.ai/elevenlabs/eleven-flash-v2.5) 是每百万字符 $40，[Scribe v2](https://openrouter.ai/elevenlabs/scribe-v2) 约为每音频小时 $0.22。按同样的用量算，这段对话每分钟处理语音约需 $0.025。这是依据 10 月 8 日的测量结果推算的，不是另做了一次计费测试。

成本明细依然有用。这段对话里 TTS 占了约 90% 的开销，所以把 agent 的语音回复压短，比小幅削减 LLM 的 token 用量更能省成本。

你也可以查每条请求的实际花费。转录响应里带 usage.cost，语音响应则提供 X-Generation-Id 标头，可以借此通过我们的[生成元数据 API](https://openrouter.ai/docs/api/api-reference/generations/get-generation)取回成本。

## 该用哪款语音转文本模型？

对餐厅预订 agent 来说，来电者报出 agent 要据此行动的细节时，转录准确度最关键，比如姓名、日期、电话号码和预订时间。

为了对比模型，我们用三种合成语音生成了九条来电台词，再给每条录音做出清晰版和电话音质版。这样一共得到 54 段音频，整个测试里每个模型评分 90 条事实。

我们评估了十款 STT 模型。下表列出其中五款，用来展示观察到的准确度和延迟区间。

| **模型** | **保留的事实（共 90 条）** | **服务器延迟中位数** | **测试日每小时成本** |
| --- | --- | --- | --- |
| microsoft/mai-transcribe-2 | 89 | 1,740 ms | $0.11 |
| elevenlabs/scribe-v2 | 88 | 379 ms | $0.11 |
| openai/whisper-large-v3 | 88 | 517 ms | $0.17 |
| x-ai/grok-stt-1.0 | 86 | 264 ms | $0.10 |
| deepgram/nova-3 | 83 | 83 ms | $0.26 |

MAI-Transcribe 2 保住的事实最多，但 Scribe v2 只少一条，速度却快得多。Whisper Large V3 得分和 Scribe 持平，响应却更慢。对我们的预订 agent 来说，Scribe v2 在准确度和速度上平衡得不错，所以 Python 实现选了它。

每款识别器都会在少见姓名上出错，即便电话号码转对了。比如 “Siobhan Okafor” 在转录里变成了 “Shioban Okafor”、“Siobhan O’Keefe” 和 “Siobhan Akhefer”。

别默认转录出来的姓名就是对的，让 agent 跟来电者核对，或者请对方拼一遍，再完成预订。

要记住，这些结果来自合成的英语录音，不是各种口音和环境下的真实客户来电。你可以去翻[可用的转录模型](https://openrouter.ai/models?output_modalities=transcription)，但更值得用贴合自己场景的音频，把候选模型实测一遍。

## 该用哪款 LLM 和文本转语音模型？

挑 LLM 时，我们看的是工具调用准确度、响应时间，以及生成的文字读起来是否自然。

对比里的每款 LLM 在五次运行中都请求了预期的预订工具。差别落在响应速度和答案格式上。

| **模型** | **把时间写成数字** | **首个回答 token 的时间（中位数）** | **每回合成本** |
| --- | --- | --- | --- |
| DeepSeek V4.1 Flash | 0/5 | 1.9 s（无推理时 1.4 s） | $0.00017 |
| GPT-6 Luna | 0/5 | 2.3 s（无推理时 1.6 s） | $0.00008 |
| Claude Haiku 5.5 | 5/5 | 2.6 s | $0.00026 |
| Gemini 3.8 Flash | 0/5 | 4.0 s | $0.00129 |
| MiMo V2.6 Flash | 2/5 | 6.4 s | $0.00006 |

一个差别在于各模型怎么处理口语时间。Claude Haiku 5.5 每次运行都写成 7:30，而不是要求的口语形式；在某种配置下，它还把日期计算写进了可见回复。回复要直接送进 TTS 时，这两种行为都有影响。

这些结果来自另一次五轮模型对比，不是上面整段对话的测量。它们量的是在测试用模型设置下，到首个回答 token 的时间。

推理也会影响延迟。在 GPT-6 Luna 的对比里，关掉推理把测试工具回合上首个回答 token 的时间从 2.3 秒降到 1.6 秒。对订位这种相对受限的任务，这挺有用，前提是模型仍能正确发起工具调用。

### 选择文本转语音模型

挑 TTS 时，我们主要看每款模型多快开始返回音频。把同一段 101 字符的回复发给 12 款模型，每款重复请求五次。

下面列出六款有代表性的结果：

| **模型** | **服务器返回首个字节的时间中位数** | **测试日成本 / 百万字符** |
| --- | --- | --- |
| Grok Voice TTS 1.0 | 80 ms | $15 |
| Kokoro 82M | 98 ms | $0.62 |
| Deepgram Aura-2 | 236 ms | $30 |
| Eleven Flash v2.5 | 275 ms | $20（促销价） |
| Eleven v4 Turbo | 1,245 ms | $20（促销价） |
| Gemini 3.8 Flash TTS | 2,561 ms | 无法直接比较（按 token 计价） |

Gemini 的计价用的是另一种计费单位，所以我们把它排除在按字符计的成本对比之外，没有把估算换算当成报价。

按服务器端测量，Grok Voice 和 Kokoro 返回首个音频字节最快，Eleven Flash v2.5 表现也不错。

不过服务器上报的时间，并不总和我们应用实际感受到的一致。Kokoro 记下的服务器延迟中位数不到 100 毫秒，音频却要三到八秒才抵达我们的测试环境。

所以该在自己的应用里量延迟，做对话式产品时尤其如此。只按速度挑模型之前，也最好先听听生成的语音、检查发音。

这次实现用的是 Eleven Flash v2.5。你可以浏览[可用的语音模型](https://openrouter.ai/models?output_modalities=speech)，用模型 slug 换成别的选项。

## 用 LiveKit Agents 跑同一个 agent

我们的 Python 脚本管转录、工具调用和语音生成，但还撑不起跟 agent 的实时对话。要做到这点，还得处理麦克风输入、判断来电者何时说完，以及管理打断。

这可以交给 [LiveKit Agents](https://docs.livekit.io/agents/start/voice-ai/)。它负责实时音频连接和对话流转，同时让我们继续通过 OpenRouter 用同样这三个模型。

先装上带 OpenAI 插件的 LiveKit Agents：

```
python -m pip install "livekit-agents[openai]~=1.8"
```

你还需要从 LiveKit 项目里拿到 LIVEKIT_URL、LIVEKIT_API_KEY 和 LIVEKIT_API_SECRET，加上前面配好的 OPENROUTER_API_KEY。如果还没建项目，照 [LiveKit 快速入门](https://docs.livekit.io/agents/start/voice-ai/)走一遍。

把下面这段和 voice_agent.py 放在一起，存成 livekit_agent.py。我们会复用上一个例子里的餐厅说明和预订函数。

```
import os

from livekit import agents
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    function_tool,
    inference,
)
from livekit.plugins import openai

from voice_agent import run_tool, system_prompt

API = "https://openrouter.ai/api/v1"
KEY = os.environ["OPENROUTER_API_KEY"]

class Luigis(Agent):
    def __init__(self):
        super().__init__(instructions=system_prompt())

    @function_tool
    async def check_availability(
        self, date: str, time: str, party_size: int
    ) -> dict:
        """Check available tables for a date, time, and party size."""
        return run_tool(
            "check_availability",
            {"date": date, "time": time, "party_size": party_size},
        )

    @function_tool
    async def book_table(
        self, date: str, time: str, party_size: int, name: str
    ) -> dict:
        """Book a table after the caller agrees and gives a name."""
        return run_tool(
            "book_table",
            {
                "date": date,
                "time": time,
                "party_size": party_size,
                "name": name,
            },
        )

server = AgentServer()

@server.rtc_session(agent_name="luigis")
async def luigis_session(ctx: agents.JobContext):
    session = AgentSession(
        vad=inference.VAD(model="silero"),
        stt=openai.STT(
            model="elevenlabs/scribe-v2",
            base_url=API,
            api_key=KEY,
        ),
        llm=openai.LLM.with_openrouter(
            model="openai/gpt-6-luna",
            api_key=KEY,
            reasoning_effort="none",
        ),
        tts=openai.TTS(
            model="elevenlabs/eleven-flash-v2.5",
            voice="sarah",
            response_format="pcm",
            base_url=API,
            api_key=KEY,
        ),
    )

    await session.start(room=ctx.room, agent=Luigis())

if __name__ == "__main__":
    agents.cli.run_app(server)
```

AgentSession 把三个模型接起来，Silero 语音活动检测（VAD）负责判断来电者什么时候停口，好让 LiveKit 把音频送去转录。语音播放和打断也由 LiveKit 管理。

注意预订函数没动。LiveKit 的 @function_tool 装饰器把它们暴露给 LLM，每个函数依旧把来电者的信息传给同一个模拟预订服务。

可以用麦克风在本地测试这个 agent：

```
python livekit_agent.py console
```

要把它接到 LiveKit 项目、通过 Agent Console 测试，运行：

```
python livekit_agent.py dev
```

试着订一张七点半的六人桌，再接受八点十五分。在我们早先那次文本驱动的 LiveKit 测试里，产生了下面这些工具调用：

```
check_availability(
    date="2026-10-10",
    time="19:30",
    party_size=6
)

book_table(
    date="2026-10-10",
    time="20:15",
    party_size=6,
    name="Siobhan Okafor"
)
```

这套配置把预订工具接进了 LiveKit 音频会话，于是你能用麦克风把同一段对话走一遍。也可以看我们的 [LiveKit 集成指南](https://openrouter.ai/docs/guides/community/livekit)，了解模型回退和 provider 路由。

## 你可能会碰到的错误

测试时我们撞上几个由缺参数或模型设置不受支持引起的错误，三者都返回 HTTP 400 响应：

| **问题** | **API 响应** | **修复办法** |
| --- | --- | --- |
| 给 ElevenLabs TTS 模型漏传了 voice | 该 TTS provider 要求显式指定 voice。 | 指定受支持的 voice，比如 sarah。 |
| 把 data:audio/wav;base64,… URI 发给 STT | provider 无法处理该音频输入（音频不受支持或格式有误）。 | 用正确的音频格式发送原始 base64 数据。 |
| 在强制要求推理的地方关掉了推理 | 该 endpoint 强制要求推理，无法关闭。 | 去掉这个不受支持的推理设置。 |

我们的[语音转文本 API](https://openrouter.ai/docs/guides/overview/multimodal/stt)要求把音频字节以 base64 编码放进 input_audio.data，不带 data:audio/…;base64, 前缀。还必须指定音频格式，比如 wav 或 mp3。

voice 名称也因 provider 而异。比如 OpenAI 的 alloy 这类 voice，不会自动能在 ElevenLabs 上用。你可以在我们的[文本转语音文档](https://openrouter.ai/docs/guides/overview/multimodal/tts)里，或通过 models API，查每款模型支持哪些 voice。

还遇到过一个问题：空的 TTS 输入会返回一小段音频。发语音请求前把空字符串过滤掉比较稳妥。

## 你需要语音到语音模型吗？

这个例子不需要。我们搭的语音转文本、LLM、文本转语音分开的三段流水线，足够跑通餐厅预订流程。

我们也试过把来电者音频直接喂给四款支持音频的 LLM：Gemini 3.8 Flash、Qwen3.8 Omni Flash、MiMo V2.6 Flash 和 GPT Audio Mini。12 次测试里，它们都选对了预期的预订工具。

这说明这些模型不单独发转录请求，也能扛下示例里的工具调用环节。不过我们没有测完整的语音到语音对话，所以这些结果说明不了这条路是否更快、语音回复是否更好。

用三段式，我们能检查转录文本、定位错在哪，再单独换转录、语言或语音模型。直接处理音频输入输出的模型也许能简化流水线，但选它之前，值得把完整响应时间、音频质量和打断处理都比一比。

## 结论

我们的 Python 示例只是个起点。把 agent 接到真实来电者之前，先用自己的后端替掉模拟预订函数，拿真实语音测一遍。目前只有 system prompt 让 agent 等来电者同意后才调 book_table，所以要让后端在写入之前确认订位。测完整响应时间，把网络传输和播放算进去，别只盯服务器端延迟。

如果需要实时音频和打断处理，就用 LiveKit，模型仍通过 OpenRouter 保持同一套。

## 常见问题

### 怎么把语音 AI agent 接到真实电话号码？

可以用 LiveKit 的电话集成，把语音 AI agent 接到电话号码上。LiveKit 通过它的电话号码服务或 SIP 提供商支持呼入。配置好所需的 trunk 和 dispatch rule，把呼入路由到 LiveKit 房间，你的 agent 就能加入对话。具体设置步骤见 [LiveKit 电话文档](https://docs.livekit.io/telephony/accepting-calls/)。

### 语音 AI agent 能处理打断吗？

能。像 LiveKit 这样的框架可以检测到有人在 agent 说话时开口，暂停 agent 的语音，再带着新输入把对话接下去。

要注意，打断语音并不会自动取消已经在跑的工具。像订位、支付这类操作，应用得谨慎处理取消和确认。

### 能给 AI 语音 agent 用自己的声音吗？

可以，前提是选支持声音克隆的文本转语音模型。OpenRouter 上有些模型通过 input_references 参数接收参考音频，用那个声音生成语音，不用另做声音训练。

声音克隆的支持情况因模型和 provider endpoint 而异，选模型前先查 [TTS 文档](https://openrouter.ai/docs/guides/overview/multimodal/tts)。只用你有权复制的录音。

### 能把语音 agent 接到真实预订系统或其他 API 吗？

可以。示例里的 check_availability 和 book_table 用的是模拟数据，你可以把它们的实现换成对预订 API 或数据库的请求。

什么时候调哪个函数仍由 LLM 决定，实际操作和结果返回由你的应用负责。像订桌、发确认这类动作，务必先确认操作成功，再告诉来电者已经办妥。
