---
vendor: huggingface
title: FastRTC: The Real-Time Communication Library for Python
original_title: FastRTC: The Real-Time Communication Library for Python
url: https://huggingface.co/blog/fastrtc
date: 2025-01-12
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 3142192fcf12
---


# FastRTC: The Real-Time Communication Library for Python

					February 25, 2025

Update on GitHub


176

- [![](https://huggingface.co/avatars/6d9c5b56418518844089a90bdd39eacd.svg)](https://huggingface.co/fronkar)
- [![](https://huggingface.co/avatars/3c29d862b02a196c8a53ff09a2c91f09.svg)](https://huggingface.co/Tahahah)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6672b7b12f70d803182f9855/cvFnQl1UODN7hXq6JJLpy.jpeg)](https://huggingface.co/ramanbansal)
- [![](https://huggingface.co/avatars/750b1b70c99f407050c41824422f5800.svg)](https://huggingface.co/basah)
- [![](https://huggingface.co/avatars/84e286313264af1461389fedef8b030d.svg)](https://huggingface.co/PlayAI)
- [![](https://huggingface.co/avatars/25414fa5790345c4b5772e551e6f5008.svg)](https://huggingface.co/Pussinsilicon)

Freddy Boulton

freddyaboulton

Abubakar Abid

abidlabs

In the last few months, many new real-time speech models have been released and entire companies have been founded around both open and closed source models. To name a few milestones:

- OpenAI and Google released their live multimodal APIs for ChatGPT and Gemini. OpenAI even went so far as to release a 1-800-ChatGPT phone number!
- Kyutai released [Moshi](https://huggingface.co/kyutai), a fully open-source audio-to-audio LLM. Alibaba released [Qwen2-Audio](https://huggingface.co/Qwen/Qwen2-Audio-7B-Instruct) and Fixie.ai released [Ultravox](https://huggingface.co/fixie-ai/ultravox-v0_5-llama-3_3-70b) - two open-source LLMs that natively understand audio.
- ElevenLabs [raised $180m](https://elevenlabs.io/blog/series-c) in their Series C.

Despite the explosion on the model and funding side, it's still difficult to build real-time AI applications that stream audio and video, especially in Python.

- ML engineers may not have experience with the technologies needed to build real-time applications, such as WebRTC.
- Even code assistant tools like Cursor and Copilot struggle to write Python code that supports real-time audio/video applications. I know from experience!

That's why we're excited to announce `FastRTC`, the real-time communication library for Python. The library is designed to make it super easy to build real-time audio and video AI applications entirely in Python!

In this blog post, we'll walk through the basics of `FastRTC` by building real-time audio applications. At the end, you'll understand the core features of `FastRTC`:

- 🗣️ Automatic Voice Detection and Turn Taking built-in, so you only need to worry about the logic for responding to the user.
- 💻 Automatic UI - Built-in WebRTC-enabled Gradio UI for testing (or deploying to production!).
- 📞 Call via Phone - Use fastphone() to get a FREE phone number to call into your audio stream (HF Token required. Increased limits for PRO accounts).
- ⚡️ WebRTC and Websocket support.
- 💪 Customizable - You can mount the stream to any FastAPI app so you can serve a custom UI or deploy beyond Gradio.
- 🧰 Lots of utilities for text-to-speech, speech-to-text, stop word detection to get you started.

Let's dive in.

## Getting Started

We'll start by building the "hello world" of real-time audio: echoing back what the user says. In `FastRTC`, this is as simple as:

```
from fastrtc import Stream, ReplyOnPause
import numpy as np

def echo(audio: tuple[int, np.ndarray]) -> tuple[int, np.ndarray]:
    yield audio

stream = Stream(ReplyOnPause(echo), modality="audio", mode="send-receive")
stream.ui.launch()
```

Let's break it down:

- The `ReplyOnPause` will handle the voice detection and turn taking for you. You just have to worry about the logic for responding to the user. Any generator that returns a tuple of audio, (represented as `(sample_rate, audio_data)`) will work.
- The `Stream` class will build a Gradio UI for you to quickly test out your stream. Once you have finished prototyping, you can deploy your Stream as a production-ready FastAPI app in a single line of code - `stream.mount(app)`. Where `app` is a FastAPI app.

Here it is in action:

## Leveling-Up: LLM Voice Chat

The next level is to use an LLM to respond to the user. `FastRTC` comes with built-in speech-to-text and text-to-speech capabilities, so working with LLMs is really easy. Let's change our `echo` function accordingly:

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

We're using the SambaNova API since it's fast. The `get_stt_model()` will fetch [Moonshine Base](https://huggingface.co/UsefulSensors/moonshine-base) and `get_tts_model()` will fetch [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M) from the Hub, both of which have been further optimized for on-device CPU inference. But you can use any LLM/text-to-speech/speech-to-text API or even a speech-to-speech model. Bring the tools you love - `FastRTC` just handles the real-time communication layer.

## Bonus: Call via Phone

If instead of `stream.ui.launch()`, you call `stream.fastphone()`, you'll get a free phone number to call into your stream. Note, a Hugging Face token is required. Increased limits for PRO accounts.

You'll see something like this in your terminal:

```
INFO:	  Your FastPhone is now live! Call +1 877-713-4471 and use code 530574 to connect to your stream.
INFO:	  You have 30:00 minutes remaining in your quota (Resetting on 2025-03-23)
```

You can then call the number and it will connect you to your stream!

## Next Steps

- Read the [docs](https://fastrtc.org/) to learn more about the basics of `FastRTC`.
- The best way to start building is by checking out the [cookbook](https://fastrtc.org/cookbook). Find out how to integrate with popular LLM providers (including OpenAI and Gemini's real-time APIs), integrate your stream with a FastAPI app and do a custom deployment, return additional data from your handler, do video processing, and more!
- ⭐️ Star the [repo](https://github.com/freddyaboulton/fastrtc) and file bug and issue requests!
- Follow the [FastRTC Org](https://huggingface.co/fastrtc) on HuggingFace for updates and check out deployed examples!

Thank you for checking out `FastRTC`!

## Models mentioned in this article 3

More Articles from our Blog

real-time

audio

video

## Hugging Face and Cloudflare Partner to Make Real-Time Speech and Video Seamless with FastRTC

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1654278567459-626a9bfa03e2e2796f24ca11.jpeg)

30

April 9, 2025

audio

vision

llm

## Gemma 3n fully available in the open-source ecosystem!

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/608aabf24955d2bfc3cd99c6/-YxmtpzEmf3NKOTktODRP.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/61929226ded356549e20c5da/ONUjP2S5fUWd07BiFXm0i.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1655385361868-61b85ce86eb1f2c5e6233736.jpeg)
- +4

123

June 26, 2025

### Community

fmurimi

Feb 25, 2025

Wow.

Omkarp2403

Feb 26, 2025


edited Feb 26, 2025

Can fastphone() accept an Indian phone number?

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1654278567459-626a9bfa03e2e2796f24ca11.jpeg)](https://huggingface.co/freddyaboulton)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/Ia-l1eHicmbnb34uSaW4i.jpeg)](https://huggingface.co/Omkarp2403)
- [![](https://huggingface.co/avatars/ae7bb70d43d939a8d84cd4058333d1e9.svg)](https://huggingface.co/WearWitty)


freddyaboulton

Article author

Feb 26, 2025

We're working on getting a whatsapp number

hamishfromatech

Feb 26, 2025

This is amazing!

ngxson

Feb 26, 2025

📻 🎙️ Hey, I generated an **AI podcast** about this blog post, check it out!

*This podcast is generated via [ngxson/kokoro-podcast-generator](https://huggingface.co/spaces/ngxson/kokoro-podcast-generator), using [DeepSeek-R1](https://huggingface.co/deepseek-ai/DeepSeek-R1) and [Kokoro-TTS](https://huggingface.co/hexgrad/Kokoro-82M).*

MRU4913

Feb 27, 2025


edited Feb 28, 2025

Thx to all all. Great work!!!

I have a question for concurrency when use tts_model and stt_model. How does each type of model handle multiple requests at the same time. (e.g. batching technique ? cpu-only threading ....) [@freddyaboulton](https://huggingface.co/freddyaboulton)

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1654278567459-626a9bfa03e2e2796f24ca11.jpeg)](https://huggingface.co/freddyaboulton)
- [![](https://huggingface.co/avatars/ce0de9e4ceb51f2aa4a5db12d17a6128.svg)](https://huggingface.co/MRU4913)


freddyaboulton

Article author

Mar 2, 2025

Hi [@MRU4913](https://huggingface.co/MRU4913)  ! Each stream is an independent event in the event loop. But you can limit how many streams run concurrently very easily. There is a parameter in the Stream class

Nirav-Madhani

Feb 28, 2025


edited Feb 28, 2025

`Taking a while to connect. Are you on a VPN?` Anyone else stuck with this error (I am not using VPN)? This only happens on Gemini examples

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1654278567459-626a9bfa03e2e2796f24ca11.jpeg)](https://huggingface.co/freddyaboulton)


freddyaboulton

Article author

Mar 2, 2025

Hi [@Nirav-Madhani](https://huggingface.co/Nirav-Madhani)  - I am not sure. Let me see. Feel free to clone and run locally in the meantime.

MechanicCoder

Mar 3, 2025

Would be very cool if you can also add a example with Azure OpenAI-API

freddyaboulton

Article author

Mar 3, 2025

Hi [@MechanicCoder](https://huggingface.co/MechanicCoder)  - please feel free to add an example here if you’d like. It should be straightforward- take the example in this blog post and replace the LLM with the api call for the LLM on Azure you like.

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/tfIjlL4vkq_x78kaJqAr1.png)](https://huggingface.co/MechanicCoder)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1654278567459-626a9bfa03e2e2796f24ca11.jpeg)](https://huggingface.co/freddyaboulton)


MechanicCoder

Mar 13, 2025

Hey, have a working example...should I send you a repo link?

monkeyin92

Mar 10, 2025

Can I connect something like FreeSWITCH and have its RTC directly parsed by fastRTC?

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1654278567459-626a9bfa03e2e2796f24ca11.jpeg)](https://huggingface.co/freddyaboulton)


freddyaboulton

Article author

Mar 10, 2025


edited Mar 10, 2025

I have not tried this myself but I think so. The FastRTC server is completely open so you can integrate with any telephony/webrtc client.

Please open a PR to add a guide on how to do this: [https://github.com/freddyaboulton/fastrtc/blob/main/docs/userguide/audio.md](https://github.com/freddyaboulton/fastrtc/blob/main/docs/userguide/audio.md)

Also feel free to join the HF discord and ask questions in the fastrtc-channels: [https://discord.gg/TSWU7HyaYu](https://discord.gg/TSWU7HyaYu)

JuanRoyo

Apr 10, 2025

Hi, I'm new to WebRTC applications, and one of my main questions is: how does the process of capturing audio work? I mean, in demos, you always take the audio directly from the microphone, but I'd like to know if it's possible to get the input audio from a specific port (for example, a listening port where RTP packets are arriving). I guess I need to better understand how WebRTC communications work...Thank you!

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1654278567459-626a9bfa03e2e2796f24ca11.jpeg)](https://huggingface.co/freddyaboulton)
- [![](https://huggingface.co/avatars/f05c5d434402067273f41237d28e4ae7.svg)](https://huggingface.co/JuanRoyo)


freddyaboulton

Article author

Apr 10, 2025

Can you tell me a bit more about the use case [@JuanRoyo](https://huggingface.co/JuanRoyo)  ? WebRTC requires a "handshake" to happen between the two clients. This handshake is taken care of by the `webrtc/offer` route of the FastRTC server. So you can just send a post request there. See this `js` code snippet:

[https://fastrtc.org/userguide/api/](https://fastrtc.org/userguide/api/)

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Ffastrtc) or [log in](https://huggingface.co/login?next=%2Fblog%2Ffastrtc) to comment


176

- [![](https://huggingface.co/avatars/6d9c5b56418518844089a90bdd39eacd.svg)](https://huggingface.co/fronkar)
- [![](https://huggingface.co/avatars/3c29d862b02a196c8a53ff09a2c91f09.svg)](https://huggingface.co/Tahahah)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6672b7b12f70d803182f9855/cvFnQl1UODN7hXq6JJLpy.jpeg)](https://huggingface.co/ramanbansal)
- [![](https://huggingface.co/avatars/750b1b70c99f407050c41824422f5800.svg)](https://huggingface.co/basah)
- [![](https://huggingface.co/avatars/84e286313264af1461389fedef8b030d.svg)](https://huggingface.co/PlayAI)
- [![](https://huggingface.co/avatars/25414fa5790345c4b5772e551e6f5008.svg)](https://huggingface.co/Pussinsilicon)
- [![](https://huggingface.co/avatars/a7760013f6920774127080c673d426e0.svg)](https://huggingface.co/Twelve2five)
- [![](https://huggingface.co/avatars/451f8c40db7c8a10ff6ee42ab42c8170.svg)](https://huggingface.co/AyaKhaled)
- [![](https://huggingface.co/avatars/6fa016e0a86aab520d7c8fb936cff244.svg)](https://huggingface.co/alyahya)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/KUdsH8Mnh736sOt-kABHG.png)](https://huggingface.co/abdouuu)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64db92c723557cdce314432d/Z7qpaVZW8hGJIjCLtDs66.jpeg)](https://huggingface.co/geradeluxer)
- [![](https://huggingface.co/avatars/2e2bb347bf994bf22c258d39b6f88392.svg)](https://huggingface.co/kashyapkp)

## Models mentioned in this article 3
