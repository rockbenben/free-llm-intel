---
vendor: openrouter
title: How to Build a Voice AI Agent
original_title: How to Build a Voice AI Agent
url: https://openrouter.ai/blog/tutorials/build-voice-ai-agent
date: 2026-11-10
lang: en
captured: 2026-11-11
extractor: readability-v1
status: ok
body_sha: 5194417ae133
---

# How to Build a Voice AI Agent

OpenRouter ·11/10/2026

![How to Build a Voice AI Agent](https://openrouter.ai/blog/images/build-voice-ai-agent.png)![How to Build a Voice AI Agent](https://openrouter.ai/blog/images/build-voice-ai-agent-dark.png)

A voice agent needs to do more than generate a good answer. It must understand what someone said, decide what to do, call any needed tools, and start speaking again before the pause gets awkward.

In this tutorial, we’ll build that full loop in Python. Our example is a restaurant booking agent that transcribes a caller, checks table availability with tools, and turns the response back into speech. Speech-to-text, the LLM, and text-to-speech all run through one [OpenRouter API key](https://openrouter.ai/docs/api_reference/authentication), and we stream each completed sentence to TTS instead of waiting for the entire reply.

Across all 12 turns in three test conversations, the overall median server-side time to first audio was 1.9 seconds, while a four-turn conversation cost about $0.013 per minute of processed speech at the promotional prices available during our October 8 test.

## TL;DR

- Text-to-speech accounted for roughly 90% of the measured model cost, making spoken response length an important cost factor for this agent.
- Server-side time to first audio was an estimated 1.4 seconds for plain turns and 2.4 seconds for tool turns in our test, counting one LLM request per turn. The example code makes extra LLM requests, and network and playback add time.
- Names were harder to transcribe than phone numbers. Have callers confirm important details before taking action.
- Sending completed sentences to text-to-speech (TTS) can reduce the wait for spoken output, but real-time playback and interruptions need additional orchestration.

## How a voice AI agent turn works

A voice agent takes a caller’s speech, converts it into text, passes it to an LLM to decide what to do, and turns the response back into speech. Here’s how the process works:

![Diagram of one voice AI agent turn: caller audio goes to speech-to-text, then the LLM, a sentence splitter, text-to-speech and agent audio. The LLM can call the booking tools check_availability and book_table and continue with the tool result.](https://openrouter.ai/blog/images/build-voice-ai-agent-1.png)

For example, when someone calls our restaurant to book a table, the LLM may need to call check_availability before responding. Your application executes the function, sends the available times back to the model, and waits for it to generate a response. This extra round trip adds to the caller’s wait time.

To reduce that wait, we can start generating speech before the LLM finishes its entire response. Instead of waiting for the full text, we’ll stream the response, split it into sentences, and send each completed sentence to TTS while the model continues generating the rest.

For this build, we’ll use our [speech-to-text API](https://openrouter.ai/docs/guides/overview/multimodal/stt) to transcribe the caller, [Chat Completions with tool calling](https://openrouter.ai/docs/guides/features/tool-calling) to handle the conversation and bookings, and our [text-to-speech API](https://openrouter.ai/docs/guides/overview/multimodal/tts) to generate the spoken response.

The transcription API returns text as JSON, while the speech API returns audio bytes. Our Python example will save the generated audio as WAV files, and later we’ll use LiveKit to handle live audio and interruptions.

## Build the voice agent in Python

Let’s build the restaurant booking agent using three models: elevenlabs/scribe-v2 for transcription, openai/gpt-6-luna for the conversation and tool calls, and elevenlabs/eleven-flash-v2.5 for speech generation.

You’ll need Python 3.10 or later and an [OpenRouter API key](https://openrouter.ai/settings/keys). Install the requests library and set your API key as an environment variable:

```
python -m pip install requests
export OPENROUTER_API_KEY="your-api-key"
```

To make the example easy to reproduce, we’ll use a second TTS voice to simulate four caller turns rather than connecting a microphone. We’ll also use mock booking data so the agent can check availability and return reservation details without a real booking system.

Save the following code as voice_agent.py:

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

The script connects the three APIs through run_turn(), which transcribes each caller message, passes the transcript to the LLM, and processes the response. If the LLM requests a tool, the function executes it, adds the result to the conversation history, and makes another request so the model can continue.

Look at how stream_reply() handles tool calls. The model streams function names and arguments in fragments, so we assemble them before executing the tool. For spoken replies, we send completed sentences to TTS through a thread pool, allowing speech generation to overlap with the remaining LLM output.

We then combine the audio in sentence order and save it as a WAV file. We’ll handle actual playback and interruptions when we introduce LiveKit.

You can run the script with this command:

```
python voice_agent.py
```

It should create four audio files, agent_1.wav through agent_4.wav, and print the conversation. Here’s an excerpt from one of our test runs. The caller lines show the transcribed audio, so the numbers may differ from how they were spoken.

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

The example shows the agent checking availability before offering another time, then calling book_table after the caller accepts. It also refuses to promise a text confirmation because we haven’t provided a tool for sending one.

## Why this design works, and what breaks it

A response can look perfectly fine in a chat window but sound strange when read aloud. Times, phone numbers, and markdown are good examples. That’s why our system prompt asks the LLM to keep responses short, avoid formatting, and write times as spoken words, such as “eight fifteen” instead of 8:15.

The same issue can happen in reverse. In our test, speech-to-text converted “eight fifteen” into 815, but the LLM correctly understood the caller’s response because it had the earlier conversation for context. We maintain that history in messages and send it with each request, since Chat Completions doesn’t automatically retain previous turns. As a result, the prompt grew from approximately 290 tokens on the first turn to 490 on the fourth.

Another important consideration is making sure the agent only confirms actions that have actually happened. In an earlier version without book_table, the agent could tell callers their reservation was confirmed even though the application hadn’t created one.

This is why the booking tool needs to do more than return a response. When connected to a real reservation system, it should verify availability, save the booking, and return a confirmation only when the operation succeeds.

## How fast is a voice AI agent?

Across all 12 turns, the median server-side time to first audio was 1.9 seconds. By turn type, the median was 1.4 seconds without tools and 2.4 seconds when the agent needed to call a tool.

We measured three complete conversations covering 12 turns, using our [generation metadata](https://openrouter.ai/docs/api/api-reference/generations/get-generation) to estimate the server-side latency at each stage. This let us separate model processing time from additional network overhead in our test environment.

Here’s how the results compared:

| **Stage** | **With a tool call** | **Without a tool** |
| --- | --- | --- |
| Speech-to-text (Scribe v2) | 549 ms | 391 ms |
| LLM selects tool | 736 ms | — |
| LLM answer, first token | 685 ms | 706 ms |
| Text-to-speech, first byte | 262 ms | 208 ms |
| **Estimated time to first audio** | **2.4 s** | **1.4 s** |

The extra LLM request accounts for much of the difference. When the agent needs to check availability, it must wait for the tool result before generating its answer.

These figures reflect server-side processing rather than the full time a caller experiences. Network delivery, detecting when the caller has finished speaking, and audio playback introduce additional delays. The individual stage medians also won’t necessarily add up to the overall median. The estimates also count one LLM request per turn. The example code below makes two on every turn, a non-streaming request that checks for tool calls and then a streaming request for the reply, and tool turns make another after the tool runs, so expect it to take longer than these figures.

The model comparisons below use separate test runs and inputs, so their reported latencies differ from the full-conversation measurements shown here.

## How much does a voice AI agent cost?

Across five runs, our four-turn restaurant conversation cost between **$0.0069 and $0.0087**. Each call contained approximately 38 seconds of speech, giving us an estimated cost of **$0.013 per minute of processed speech** at the prices available on October 8, 2026.

Most of that cost came from generating the agent’s voice.

| **Stage** | **Share of total cost** | **Price during the test** |
| --- | --- | --- |
| Text-to-speech (Eleven Flash v2.5) | 90% | $20 / million characters |
| Speech-to-text (Scribe v2) | 6% | $0.11 / audio hour |
| LLM (GPT-6 Luna) | 4% | $0.10 / $0.50 per million input/output tokens |

The ElevenLabs prices above included a 50% launch discount that ended on October 19, 2026. At the regular listed rates, [Eleven Flash v2.5](https://openrouter.ai/elevenlabs/eleven-flash-v2.5) costs $40 per million characters, while [Scribe v2](https://openrouter.ai/elevenlabs/scribe-v2) costs approximately $0.22 per audio hour. Assuming the same usage, our conversation would cost roughly $0.025 per minute of processed speech. This is a calculation based on our October 8 measurements, not a separate billing test.

The cost breakdown is still useful. In this conversation, TTS accounted for about 90% of our spending, so keeping the agent’s spoken responses short would have a greater impact on cost than making small reductions to LLM token usage.

You can also track what individual requests actually cost. Transcription responses include usage.cost, while speech responses provide an X-Generation-Id header that you can use to retrieve the cost through our [generation metadata API](https://openrouter.ai/docs/api/api-reference/generations/get-generation).

## Which speech-to-text model should you use?

For a restaurant booking agent, transcription accuracy matters most when the caller mentions details the agent needs to act on, such as names, dates, phone numbers, and reservation times.

To compare models, we generated nine caller lines using three synthetic voices, then created clean and phone-quality versions of each recording. That gave us 54 audio clips, with 90 facts scored per model across the test.

We evaluated ten STT models. The table below shows five that illustrate the range of accuracy and latency we observed.

| **Model** | **Facts kept (of 90)** | **Median server latency** | **Test-date cost/hour** |
| --- | --- | --- | --- |
| microsoft/mai-transcribe-2 | 89 | 1,740 ms | $0.11 |
| elevenlabs/scribe-v2 | 88 | 379 ms | $0.11 |
| openai/whisper-large-v3 | 88 | 517 ms | $0.17 |
| x-ai/grok-stt-1.0 | 86 | 264 ms | $0.10 |
| deepgram/nova-3 | 83 | 83 ms | $0.26 |

MAI-Transcribe 2 retained the most facts, but Scribe v2 was considerably faster while retaining just one fewer. Whisper Large V3 matched Scribe’s score but took longer to respond. For our booking agent, Scribe v2 offered a good balance of accuracy and speed, so we chose it for the Python implementation.

Every recognizer made mistakes with uncommon names, even when it preserved the phone number correctly. For example, “Siobhan Okafor” appeared in the transcripts as “Shioban Okafor”, “Siobhan O’Keefe”, and “Siobhan Akhefer”.

Rather than assuming the transcribed name is correct, have the agent confirm it with the caller or ask them to spell it before completing the reservation.

Keep in mind that these results came from synthetic English recordings, not actual customer calls across different accents and environments. You can explore the [available transcription models](https://openrouter.ai/models?output_modalities=transcription), but it’s worth testing your shortlisted models with audio that reflects your own use case.

## Which LLM and text-to-speech model should you use?

For the LLM, we looked at tool-calling accuracy, response time, and how naturally the generated text could be spoken.

Every LLM in our comparison requested the expected booking tool in all five runs. The differences came down to response speed and answer formatting.

| **Model** | **Wrote times as digits** | **Time to first answer token (median)** | **Cost per turn** |
| --- | --- | --- | --- |
| DeepSeek V4.1 Flash | 0/5 | 1.9 s (1.4 s without reasoning) | $0.00017 |
| GPT-6 Luna | 0/5 | 2.3 s (1.6 s without reasoning) | $0.00008 |
| Claude Haiku 5.5 | 5/5 | 2.6 s | $0.00026 |
| Gemini 3.8 Flash | 0/5 | 4.0 s | $0.00129 |
| MiMo V2.6 Flash | 2/5 | 6.4 s | $0.00006 |

One difference was how the models handled spoken times. Claude Haiku 5.5 wrote 7:30 in every run rather than the requested spoken form, and in one configuration it also included its date calculation in the visible response. Both behaviors matter when the response is going straight to TTS.

These results come from a separate five-run model comparison, rather than the complete conversation measurements above. They measure the time to the first answer token under the tested model settings.

Reasoning also affected latency. In our GPT-6 Luna comparison, disabling reasoning reduced the time to the first answer token from 2.3 seconds to 1.6 seconds on the tested tool turn. That’s useful for a relatively constrained booking task, provided the model continues to make the right tool calls.

### Choosing a text-to-speech model

For TTS, we focused on how quickly each model began returning audio. We sent the same 101-character response to twelve models, repeating the request five times per model.

Six representative results are shown below:

| **Model** | **Median server time to first byte** | **Test-date cost/million characters** |
| --- | --- | --- |
| Grok Voice TTS 1.0 | 80 ms | $15 |
| Kokoro 82M | 98 ms | $0.62 |
| Deepgram Aura-2 | 236 ms | $30 |
| Eleven Flash v2.5 | 275 ms | $20 promotional |
| Eleven v4 Turbo | 1,245 ms | $20 promotional |
| Gemini 3.8 Flash TTS | 2,561 ms | Not directly comparable (token-priced) |

Gemini’s pricing uses a different billing unit, so we’ve left it out of the per-character cost comparison rather than treating an estimated conversion as a quoted rate.

Grok Voice and Kokoro returned their first audio bytes fastest on server-side measurements, while Eleven Flash v2.5 also performed well.

However, the server-reported time didn’t always match what our application experienced. Kokoro recorded a median server latency below 100 milliseconds, but its audio took between three and eight seconds to reach our test environment.

That’s why you should measure latency in your own application, especially when building something conversational. You’ll also want to listen to the generated speech and check pronunciation before choosing a model based on speed alone.

For this implementation, we used Eleven Flash v2.5. You can browse the [available speech models](https://openrouter.ai/models?output_modalities=speech) and replace it with another option using the model slug.

## Run the same agent with LiveKit Agents

Our Python script handles transcription, tool calls, and speech generation, but it doesn’t support a live conversation with the agent. To do that, we also need to handle microphone input, detect when the caller has finished speaking, and manage interruptions.

We can use [LiveKit Agents](https://docs.livekit.io/agents/start/voice-ai/) for this. It handles the real-time audio connection and conversation flow while letting us continue using the same three models through OpenRouter.

First, install LiveKit Agents with the OpenAI plugin:

```
python -m pip install "livekit-agents[openai]~=1.8"
```

You’ll also need LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET from your LiveKit project, along with the OPENROUTER_API_KEY we configured earlier. Follow the [LiveKit quickstart](https://docs.livekit.io/agents/start/voice-ai/) if you haven’t set up a project.

Save the following as livekit_agent.py alongside voice_agent.py. We’ll reuse the restaurant instructions and booking functions from the previous example.

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

The AgentSession connects the three models, while Silero voice activity detection (VAD) helps identify when the caller has stopped speaking so LiveKit can send the audio for transcription. LiveKit also manages speech playback and interruptions.

Notice that the booking functions haven’t changed. LiveKit’s @function_tool decorator makes them available to the LLM, and each function passes the caller’s details to the same mock booking service.

You can test the agent locally using your microphone:

```
python livekit_agent.py console
```

To connect it to your LiveKit project for testing through the Agent Console, run:

```
python livekit_agent.py dev
```

Try asking for a table for six at seven thirty, then accept eight fifteen. In our earlier text-driven LiveKit test, this produced the following tool calls:

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

This setup connects the booking tools to a LiveKit audio session, so you can test the same conversation using your microphone. You can also use our [LiveKit integration guide](https://openrouter.ai/docs/guides/community/livekit) to explore model fallbacks and provider routing.

## Errors you’re likely to hit

During testing, we encountered a few errors caused by missing parameters or unsupported model settings. All three returned HTTP 400 responses:

| **Problem** | **API response** | **How to fix it** |
| --- | --- | --- |
| Omitted voice for an ElevenLabs TTS model | An explicit voice is required for this TTS provider. | Specify a supported voice, such as sarah. |
| Sent a data:audio/wav;base64,… URI to STT | Provider could not process the audio input (unsupported or malformed audio). | Send raw base64 data with the correct audio format. |
| Disabled reasoning where it was mandatory | Reasoning is mandatory for this endpoint and cannot be disabled. | Remove the unsupported reasoning setting. |

Our [speech-to-text API](https://openrouter.ai/docs/guides/overview/multimodal/stt) expects the audio bytes encoded as base64 in input_audio.data, without the data:audio/…;base64, prefix. You must also specify the audio format, such as wav or mp3.

Voice names also vary by provider. For example, an OpenAI voice such as alloy won’t automatically work with ElevenLabs. You can check each model’s supported voices in our [text-to-speech documentation](https://openrouter.ai/docs/guides/overview/multimodal/tts) or through the models API.

One other issue we encountered was that an empty TTS input returned a short audio clip. It’s worth filtering out empty strings before making speech requests.

## Do you need a speech-to-speech model?

Not for this example. The separate speech-to-text, LLM, and text-to-speech pipeline we’ve built is enough to handle our restaurant booking workflow.

We also tested sending the caller’s audio directly to four audio-capable LLMs: Gemini 3.8 Flash, Qwen3.8 Omni Flash, MiMo V2.6 Flash, and GPT Audio Mini. They selected the expected booking tools in all 12 test runs.

That shows these models could handle the tool-calling part of our example without a separate transcription request. However, we didn’t measure a complete speech-to-speech conversation, so those results don’t tell us whether the approach would be faster or produce better spoken responses.

With the three-stage approach, we can inspect the transcript, identify where errors occur, and change the transcription, language, or speech model independently. A model that handles audio input and output directly may simplify the pipeline, but it’s worth comparing the full response time, audio quality, and interruption handling before choosing one.

## Conclusion

Our Python example is a starting point. Before connecting the agent to real callers, replace the mock booking functions with your own backend and test it with actual speech. Only the system prompt makes the agent wait for the caller to agree before it calls book_table, so have your backend confirm the booking before it writes it. Measure the complete response time, including network delivery and playback, rather than relying only on server-side latency.

If you need live audio and interruption handling, use LiveKit while keeping the same models through OpenRouter.

## Frequently asked questions

### How do I connect a voice AI agent to a real phone number?

You can connect a voice AI agent to a phone number using LiveKit’s telephony integration. LiveKit supports inbound calls through its phone-number service or a SIP provider. Configure the required trunk and dispatch rule to route incoming calls to a LiveKit room, where your agent can join the conversation. See the [LiveKit telephony documentation](https://docs.livekit.io/telephony/accepting-calls/) for the setup steps.

### Can a voice AI agent handle interruptions?

Yes. A framework like LiveKit can detect when someone starts speaking while the agent is responding, pause the agent’s speech, and continue the conversation with the new input.

Keep in mind that interrupting speech doesn’t automatically cancel a tool that’s already running. For operations such as reservations or payments, your application should handle cancellation and confirmation carefully.

### Can I use my own voice for an AI voice agent?

Yes, if you choose a text-to-speech model that supports voice cloning. Some models on OpenRouter accept reference audio through the input_references parameter and generate speech using that voice without requiring a separate voice-training process.

Voice cloning support varies by model and provider endpoint, so check the [TTS documentation](https://openrouter.ai/docs/guides/overview/multimodal/tts) before choosing a model. Only use recordings you have permission to reproduce.

### Can I connect the voice agent to a real booking system or other APIs?

Yes. The check_availability and book_table functions in our example use mock data, but you can replace their implementations with requests to your reservation API or database.

The LLM still decides when to call each function, while your application handles the actual operation and returns the result. For actions such as booking a table or sending a confirmation, make sure the operation succeeds before telling the caller it’s complete.
