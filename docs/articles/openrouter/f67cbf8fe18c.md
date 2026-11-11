---
vendor: openrouter
title: 如何构建语音 AI 代理
original_title: 
url: https://openrouter.ai/blog/tutorials/build-voice-ai-agent
date: 2026-11-10
lang: zh
captured: 2026-11-11
extractor: readability-v1
translator: mt
status: translated
body_sha: 2bf82ba24f86
---

# 如何构建语音 AI 代理

开放路由器 ·11/10/2026

![如何构建语音 AI 代理](https://openrouter.ai/blog/images/build-voice-ai-agent.png)![如何构建语音 AI 代理](https://openrouter.ai/blog/images/build-voice-ai-agent-dark.png)

语音代理需要做的不仅仅是生成一个好的答案。它必须理解某人所说的内容，决定要做什么，调用任何需要的工具，并在停顿变得尴尬之前再次开始说话。

在本教程中，我们将在 Python 中构建完整的循环。我们的示例是餐厅预订代理，它会转录呼叫者的内容，使用工具检查餐桌可用性，然后将响应转回语音。语音转文本、LLM 和文本转语音都通过一个 [OpenRouter API 密钥](https://openrouter.ai/docs/api_reference/authentication) 运行，我们将每个完整的句子流式传输到 TTS，而不是等待整个回复。

在 3 个测试对话的所有 12 个回合中，服务器端首次发出音频的总体中位时间为 1.9 秒，而按 10 月 8 日测试期间提供的促销价格计算，四回合对话每分钟处理语音的成本约为 0.013 美元。

## 长篇大论；博士

- 文本到语音转换约占测量模型成本的 90%，这使得语音响应长度成为该代理的重要成本因素。
- 在我们的测试中，按每轮一个 LLM 请求计算，服务器端发出第一个音频的时间估计为普通转弯为 1.4 秒，工具转弯为 2.4 秒。示例代码会发出额外的 LLM 请求，并且网络和播放会增加时间。
- 姓名比电话号码更难转录。让来电者在采取行动之前确认重要细节。
- 将完整的句子发送到文本转语音 (TTS) 可以减少语音输出的等待，但实时播放和中断需要额外的编排。

## 语音 AI 代理的工作原理

语音代理接收呼叫者的语音，将其转换为文本，将其传递给LLM决定要做什么，然后将响应转回语音。该过程的工作原理如下：

![一个语音 AI 代理轮流图：呼叫者音频进入语音转文本，然后是 LLM、句子分割器、文本转语音和代理音频。 LLM 可以调用预订工具 check_availability 和 book_table 并继续使用工具结果。](https://openrouter.ai/blog/images/build-voice-ai-agent-1.png)

例如，当有人打电话给我们的餐厅预订餐桌时，LLM可能需要在回复之前调用 check_availability。您的应用程序执行该函数，将可用时间发送回模型，并等待它生成响应。这种额外的往返会增加呼叫者的等待时间。

为了减少等待时间，我们可以在 LLM 完成其整个响应之前开始生成语音。我们不会等待全文，而是会传输响应，将其分割成句子，并将每个完整的句子发送到 TTS，同时模型继续生成其余句子。

对于此构建，我们将使用我们的[语音转文本 API](https://openrouter.ai/docs/guides/overview/multimodal/stt) 来转录呼叫者，[使用工具调用完成聊天](https://openrouter.ai/docs/guides/features/tool-calling) 来处理对话和预订，以及我们的[文本转语音] API](https://openrouter.ai/docs/guides/overview/multimodal/tts) 生成语音响应。

转录 API 以 JSON 形式返回文本，而语音 API 返回音频字节。我们的 Python 示例将生成的音频保存为 WAV 文件，稍后我们将使用 LiveKit 来处理实时音频和中断。

## 用 Python 构建语音代理

让我们使用三个模型构建餐厅预订代理：用于转录的 elevenlabs/scribe-v2、用于对话和工具调用的 openai/gpt-6-luna 以及用于生成语音的 elevenlabs/eleven-flash-v2.5。

您需要 Python 3.10 或更高版本以及 [OpenRouter API 密钥](https://openrouter.ai/settings/keys)。安装 requests 库并将 API 密钥设置为环境变量：
```
python -m pip install requests
export OPENROUTER_API_KEY="your-api-key"
```
为了使示例易于重现，我们将使用第二个 TTS 语音来模拟四个呼叫者回合，而不是连接麦克风。我们还将使用模拟预订数据，以便代理可以在没有真正的预订系统的情况下检查可用性并返回预订详细信息。

将以下代码保存为voice_agent.py：
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
该脚本通过 run_turn() 连接三个 API，它会转录每个调用者消息，将转录文本传递给 LLM，并处理响应。如果 LLM 请求一个工具，该函数会执行该工具，将结果添加到对话历史记录中，并发出另一个请求，以便模型可以继续。

看看stream_reply()如何处理工具调用。模型以片段形式传输函数名称和参数，因此我们在执行工具之前将它们组装起来。对于口头回复，我们通过线程池将完整的句子发送到 TTS，从而允许语音生成与剩余的 LLM 输出重叠。

然后，我们按句子顺序组合音频并将其保存为 WAV 文件。当我们引入 LiveKit 时，我们将处理实际的播放和中断。

您可以使用以下命令运行该脚本：
```
python voice_agent.py
```
它应该创建四个音频文件（agent_1.wav 到 agent_4.wav），并打印对话。这是我们的一次测试的摘录。呼叫者线路显示转录的音频，因此数字可能与所说的不同。
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
该示例显示代理在提供另一个时间之前检查可用性，然后在调用者接受后调用 book_table。它还拒绝承诺短信确认，因为我们没有提供发送短信的工具。

## 为什么这个设计有效，以及它的失败之处

回复在聊天窗口中看起来非常好，但在大声朗读时听起来很奇怪。时间、电话号码和降价就是很好的例子。这就是为什么我们的系统提示要求LLM保持简短的回答，避免格式化，并将时间写成口语，例如“八点十五分”而不是 8:15。

同样的问题也可能反过来发生。在我们的测试中，语音转文本将“八点十五分”转换为 815，但LLM正确理解了呼叫者的响应，因为它有之前的对话作为上下文。我们在消息中维护该历史记录并随每个请求一起发送，因为聊天完成不会自动保留之前的回合。结果，提示从第一轮的大约 290 个令牌增加到第四轮的 490 个令牌。

另一个重要的考虑因素是确保代理仅确认实际发生的操作。在没有 book_table 的早期版本中，代理可以告诉呼叫者他们的预订已确认，即使应用程序尚未创建预订。

这就是为什么预订工具需要做的不仅仅是返回响应。当连接到真实的预订系统时，它应该验证可用性，保存预订，并仅在操作成功时返回确认。

## 语音 AI 代理的速度有多快？

在所有 12 个回合中，服务器端发出第一个音频的时间中位数为 1.9 秒。按回合类型计算，在没有工具的情况下，中位时间为 1.4 秒，而在代理需要调用工具时，中位时间为 2.4 秒。

我们测量了三个完整的对话，涵盖 12 个回合，使用我们的[生成元数据](https://openrouter.ai/docs/api/api-reference/ Generations/get- Generation) 来估计每个阶段的服务器端延迟。这使我们能够将模型处理时间与测试环境中的额外网络开销分开。

结果比较如下：

| **舞台** | **通过工具调用** | **无需工具** |
| --- | --- | --- |
|语音转文本 (Scribe v2) | 549 毫秒 | 391 毫秒 |
| LLM选择工具| 736 毫秒 | — |
| LLM 答案，第一个令牌 | 685 毫秒 | 706 毫秒 |
|文本转语音，第一个字节 | 262 毫秒 | 208 毫秒 |
| **首次播放音频的预计时间** | **2.4 秒** | **1.4 秒** |

额外的LLM申请是造成这一差异的主要原因。当代理需要检查可用性时，它必须等待工具结果才能生成答案。

这些数字反映了服务器端处理，而不是呼叫者经历的全部时间。网络传输、检测呼叫者何时结束讲话以及音频播放会带来额外的延迟。各个阶段的中位数也不一定等于总体中位数。该估计还计算了每轮一个LLM请求。下面的示例代码每次都会生成两个，一个检查工具调用的非流式请求，然后是一个用于回复的流式请求，工具运行后会生成另一个，因此预计它需要比这些数字更长的时间。

下面的模型比较使用单独的测试运行和输入，因此它们报告的延迟与此处显示的完整对话测量结果不同。

## 语音 AI 代理要多少钱？

在五次运行中，我们四轮餐厅对话的成本在 **0.0069 美元到 0.0087 美元**之间。每个通话包含大约 38 秒的语音，按照 2026 年 10 月 8 日的可用价格，我们估计每分钟处理语音的成本为 **0.013 美元**。

大部分成本来自生成代理的声音。

| **舞台** | **占总成本的份额** | **测试期间的价格** |
| --- | --- | --- |
|文字转语音（十一Flash v2.5）| 90% | 20 美元/百万字符 |
|语音转文本 (Scribe v2) | 6% | 0.11 美元/音频小时 |
|LLM (GPT-6 Luna) | 4% |每百万输入/输出代币 0.10 美元 / 0.50 美元 |

上述 ElevenLabs 价格包括截至 2026 年 10 月 19 日的 50% 发布折扣。按照常规列出的价格，[Eleven Flash v2.5](https://openrouter.ai/elevenlabs/eleven-flash-v2.5) 的价格为每百万字符 40 美元，而 [Scribe v2](https://openrouter.ai/elevenlabs/scribe-v2) 的价格约为每音频小时 0.22 美元。假设使用相同的情况，我们的对话每分钟处理语音的成本约为 0.025 美元。这是根据我们 10 月 8 日的测量结果进行的计算，而不是单独的计费测试。

成本明细还是有用的。在本次对话中，TTS 约占我们支出的 90%，因此保持代理的口头响应简短会对成本产生比小幅减少 LLM 代币使用量更大的影响。

您还可以跟踪各个请求的实际成本。转录响应包括 use.cost，而语音响应提供 X-Generation-Id 标头，您可以使用该标头通过我们的[生成元数据 API](https://openrouter.ai/docs/api/api-reference/ Generations/get- Generation) 检索成本。

## 您应该使用哪种语音到文本模型？

对于餐厅预订代理来说，当呼叫者提及代理需要采取行动的详细信息（例如姓名、日期、电话号码和预订时间）时，转录准确性最为重要。

为了比较模型，我们使用三种合成声音生成了九条呼叫线路，然后为每个录音创建了清晰的电话质量版本。这为我们提供了 54 个音频剪辑，在整个测试中每个模型得分为 90 个事实。

我们评估了十个 STT 模型。下表显示了五个，说明了我们观察到的准确性和延迟的范围。

| **型号** | **保留的事实（共 90 条）** | **服务器延迟中值** | **测试日期每小时成本** |
| --- | --- | --- | --- |
|微软/mai-transcribe-2 | 89 | 89 1,740 毫秒 | 0.11 美元 |
|十一实验室/ scribe-v2 | 88 | 88 379 毫秒 | 0.11 美元 |
| openai/whisper-large-v3 | openai/whisper-large-v3 | 88 | 88 517 毫秒 | 0.17 美元 |
| x-ai/grok-stt-1.0 | 86 | 86 264 毫秒 | 0.10 美元 |
| Deepgram/nova-3 | 83 | 83 83 毫秒 | 0.26 美元 |

MAI-Transcribe 2 保留了最多的事实，但 Scribe v2 的速度要快得多，但仅保留了较少的事实。 Whisper Large V3 与 Scribe 的得分相当，但响应时间较长。对于我们的预订代理来说，Scribe v2 提供了准确性和速度的良好平衡，因此我们选择它来进行 Python 实现。

每个识别器都会在不常见的名字上犯错误，即使它正确地保存了电话号码。例如，“Siobhan Okafor”在成绩单中出现为“Shioban Okafor”、“Siobhan O’Keefe”和“Siobhan Akhefer”。

不要假设转录的姓名是正确的，而是让代理与来电者确认或要求他们在完成预订之前拼写该姓名。

请记住，这些结果来自合成英语录音，而不是不同口音和环境下的实际客户通话。您可以探索[可用的转录模型](https://openrouter.ai/models?output_modalities=transcription)，但值得使用反映您自己的用例的音频来测试您入围的模型。

## 您应该使用哪种 LLM 和文本转语音模型？

对于LLM，我们研究了工具调用的准确性、响应时间以及生成的文本的发音是否自然。

我们比较中的每个LLM在所有五次运行中都要求使用预期的预订工具。差异归结于响应速度和答案格式。

| **型号** | **将时间写成数字** | **首次回答令牌的时间（中位数）** | **每转成本** |
| --- | --- | --- | --- |
| DeepSeek V4.1 闪存 | 0/5 | 1.9 秒（1.4 秒，无推理）| 0.00017 美元 |
| GPT-6 露娜 | 0/5 | 2.3 秒（1.6 秒，无推理）| 0.00008 美元 |
|Claude Haiku 5.5 | 5/5 | 2.6 秒 | 0.00026 美元 |
|Gemini3.8闪存| 0/5 | 4.0 秒 | $0.00129 | $0.00129
| MiMo V2.6 闪存 | 2/5 | 2/5 6.4 秒 | 0.00006 美元 |

一个区别是模型处理说话时间的方式。 Claude Haiku 5.5 在每次运行中都写了 7:30，而不是要求的口头形式，并且在一种配置中，它还在可见响应中包含了日期计算。当响应直接进入 TTS 时，这两种行为都很重要。

这些结果来自单独的五次运行模型比较，而不是上面完整的对话测量。他们测量在测试的模型设置下到达第一个答案标记的时间。

推理也会影响延迟。在我们的 GPT-6 Luna 比较中，禁用推理将测试工具转动中第一个答案标记的时间从 2.3 秒减少到 1.6 秒。如果模型继续调用正确的工具，这对于相对受限的预订任务很有用。

### 选择文本转语音模型

对于 TTS，我们重点关注每个模型开始返回音频的速度。我们向 12 个模型发送了相同的 101 个字符的响应，每个模型重复该请求五次。

六种有代表性的结果如下所示：

| **型号** | **第一个字节的平均服务器时间** | **测试日期成本/百万字符** |
| --- | --- | --- |
| Grok 语音 TTS 1.0 | 80 毫秒 | 15 美元 |
|心82M | 98 毫秒 | 0.62 美元 |
| Deepgram Aura-2 | 236 毫秒 | 30 美元 |
|十一闪客 v2.5 | 275 毫秒 | 20 美元促销 |
| 11 v4 涡轮 | 1,245 毫秒 | 20 美元促销 |
|Gemini 3.8 Flash TTS | 2,561 毫秒 |不可直接比较（代币定价）|

Gemini 的定价使用不同的计费单位，因此我们将其排除在每个字符的成本比较之外，而不是将估计转化视为报价费率。

Grok Voice 和 Kokoro 在服务器端测量中返回第一个音频字节的速度最快，而 Eleven Flash v2.5 也表现良好。

然而，服务器报告的时间并不总是与我们的应用程序经历的时间相符。 Kokoro 记录的平均服务器延迟低于 100 毫秒，但其音频需要三到八秒才能到达我们的测试环境。

这就是为什么您应该测量自己的应用程序中的延迟，尤其是在构建会话式应用程序时。在选择仅基于速度的模型之前，您还需要聆听生成的语音并检查发音。

对于此实现，我们使用了 Eleven Flash v2.5。您可以浏览[可用的语音模型](https://openrouter.ai/models?output_modalities=speech)，并使用模型 slug 将其替换为其他选项。

## 使用 LiveKit Agents 运行相同的代理

我们的 Python 脚本处理转录、工具调用和语音生成，但它不支持与代理的实时对话。为此，我们还需要处理麦克风输入、检测呼叫者何时结束讲话以及管理中断。

为此，我们可以使用[LiveKit Agents](https://docs.livekit.io/agents/start/voice-ai/)。它处理实时音频连接和对话流，同时让我们通过 OpenRouter 继续使用相同的三个模型。

首先，使用 OpenAI 插件安装 LiveKit Agents：
```
python -m pip install "livekit-agents[openai]~=1.8"
```
您还需要 LiveKit 项目中的 LIVEKIT_URL、LIVEKIT_API_KEY 和 LIVEKIT_API_SECRET，以及我们之前配置的 OPENROUTER_API_KEY。如果您尚未设置项目，请按照 [LiveKit 快速入门](https://docs.livekit.io/agents/start/voice-ai/) 进行操作。

将以下内容与 voice_agent.py 一起保存为 livekit_agent.py。我们将重用上一个示例中的餐厅说明和预订功能。
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
AgentSession 连接三个模型，而 Silero 语音活动检测 (VAD) 有助于识别呼叫者何时停止说话，以便 LiveKit 可以发送音频进行转录。 LiveKit 还管理语音播放和中断。

请注意，预订功能没有改变。 LiveKit 的 @function_tool 装饰器使它们可供 LLM 使用，并且每个函数将调用者的详细信息传递给同一个模拟预订服务。

您可以使用麦克风在本地测试代理：
```
python livekit_agent.py console
```
要将其连接到 LiveKit 项目以通过代理控制台进行测试，请运行：
```
python livekit_agent.py dev
```
尝试在七点三十分预订一张六人桌，然后在八点十五分接受。在我们之前的文本驱动的 LiveKit 测试中，这产生了以下工具调用：
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
此设置将预订工具连接到 LiveKit 音频会话，因此您可以使用麦克风测试相同的对话。您还可以使用我们的[LiveKit集成指南](https://openrouter.ai/docs/guides/community/livekit)来探索模型回退和提供者路由。

## 你可能会遇到的错误

在测试过程中，我们遇到了一些由于缺少参数或不受支持的模型设置而导致的错误。所有三个都返回 HTTP 400 响应：

| **问题** | **API 响应** | **如何修复它** |
| --- | --- | --- |
| ElevenLabs TTS 模型省略了语音 |此 TTS 提供商需要明确的语音。 |指定支持的语音，例如 sarah。 |
|发送数据：audio/wav;base64,... URI 到 STT |提供程序无法处理音频输入（不受支持或格式错误的音频）。 |使用正确的音频格式发送原始 Base64 数据。 |
|在强制推理的情况下禁用推理 |推理对于该端点是强制性的，并且不能被禁用。 |删除不支持的推理设置。 |

我们的 [speech-to-text API](https://openrouter.ai/docs/guides/overview/multimodal/stt) 期望在 input_audio.data 中将音频字节编码为 base64，而不带 data:audio/…;base64, 前缀。您还必须指定音频格式，例如 wav 或 mp3。

语音名称也因提供商而异。例如，合金等 OpenAI 语音不会自动与 ElevenLabs 配合使用。您可以在我们的[文本转语音文档](https://openrouter.ai/docs/guides/overview/multimodal/tts) 或通过模型 API 检查每个模型支持的语音。

我们遇到的另一个问题是空的 TTS 输入返回了一个简短的音频剪辑。在发出语音请求之前过滤掉空字符串是值得的。

## 您需要语音到语音模型吗？

不适用于本示例。我们构建的单独的语音到文本、LLM 和文本到语音管道足以处理我们的餐厅预订工作流程。

我们还测试了将呼叫者的音频直接发送到四个支持音频的 LLM：Gemini 3.8 Flash、Qwen3.8 Omni Flash、MiMo V2.6 Flash 和 GPT Audio Mini。他们在所有 12 次测试中都选择了预期的预订工具。

这表明这些模型可以处理我们示例中的工具调用部分，而无需单独的转录请求。然而，我们没有测量完整的语音到语音对话，因此这些结果并不能告诉我们该方法是否会更快或产生更好的口头响应。

通过三阶段方法，我们可以检查转录，识别发生错误的位置，并独立更改转录、语言或语音模型。直接处理音频输入和输出的模型可以简化管道，但在选择模型之前值得比较完整的响应时间、音频质量和中断处理。

## 结论

我们的 Python 示例是一个起点。在将代理连接到真正的呼叫者之前，用您自己的后端替换模拟预订功能，并用实际语音进行测试。只有系统提示才会让代理等待调用者同意才调用 book_table，所以让你的后端在写入之前确认预订。测量完整的响应时间，包括网络传输和播放，而不是仅依赖服务器端延迟。

如果您需要实时音频和中断处理，请使用 LiveKit，同时通过 OpenRouter 保持相同的模型。

## 常见问题

### 如何将语音 AI 代理连接到真实的电话号码？

您可以使用 LiveKit 的电话集成将语音 AI 代理连接到电话号码。 LiveKit 通过其电话号码服务或 SIP 提供商支持入站呼叫。配置所需的中继和调度规则，将传入呼叫路由到 LiveKit 房间，您的客服人员可以在其中加入对话。有关设置步骤，请参阅 [LiveKit 电话文档](https://docs.livekit.io/telephony/accepting-calls/)。

### 语音人工智能代理可以处理中断吗？

是的。像 LiveKit 这样的框架可以检测到有人在代理响应时开始说话，暂停代理的语音，并使用新的输入继续对话。

请记住，打断语音不会自动取消已经运行的工具。对于预订或支付等操作，您的应用程序应谨慎处理取消和确认。

### 我可以使用自己的声音作为人工智能语音代理吗？

是的，如果您选择支持语音克隆的文本转语音模型。 OpenRouter 上的某些模型通过 input_references 参数接受参考音频，并使用该语音生成语音，而不需要单独的语音训练过程。

语音克隆支持因模型和提供商端点而异，因此在选择模型之前请检查 [TTS 文档](https://openrouter.ai/docs/guides/overview/multimodal/tts)。仅使用您有权复制的录音。

### 我可以将语音代理连接到真实的预订系统或其他 API 吗？

是的。我们示例中的 check_availability 和 book_table 函数使用模拟数据，但您可以将它们的实现替换为对预订 API 或数据库的请求。

LLM 仍然决定何时调用每个函数，而您的应用程序则处理实际操作并返回结果。对于预订餐桌或发送确认等操作，请确保操作成功，然后再告诉呼叫者操作已完成。
