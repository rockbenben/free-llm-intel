---
vendor: openrouter
title: Nano Banana API: Edit Images with Gemini in Code
original_title: Nano Banana API: Edit Images with Gemini in Code
url: https://openrouter.ai/blog/tutorials/nano-banana
date: 2026-09-09
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 5a14fe6952bb
---

# Nano Banana API: Edit Images with Gemini in Code

OpenRouter ·9/9/2026 · Updated 9/24/2026

This guide shows how to edit an image with a text prompt in code. You send the source image and an edit prompt to `google/gemini-3.1-flash-image` through the OpenRouter API, and the edited image comes back in the response. “Nano Banana” is the nickname for Google’s Gemini image models. This slug is Nano Banana 2, the default fast model in that family. Because you reach it through [one API](https://openrouter.ai/blog/announcements/image-api/), you can use a different editing model later by changing one field.

Image editing changes an existing image. Image generation creates a new image from text. This guide covers editing, so every request here includes a source image. For creating images from text, see the [image generation docs](https://openrouter.ai/docs/guides/overview/multimodal/image-generation) or the [image generation tutorial](https://openrouter.ai/blog/tutorials/image-generation/).

![Before-and-after example of a natural-language image edit: a portrait photo, the prompt "Add a red wool scarf around the person's neck. Keep everything else the same.", and the edited result with the scarf added and everything else intact](https://openrouter.ai/blog/images/nano-banana-before-after.png)

## Tl;dr

- Editing takes one request. Put the source image in `input_references` and the instruction in `prompt`, then read the edited image from `data[0].b64_json` and decode it to disk.
- `google/gemini-3.1-flash-image` is Nano Banana 2, the default fast Gemini image model. Check that a model accepts image input before you use it, because editing support varies.
- Send the input as a base64 data URL for local or private files, or a plain HTTP(S) URL for a hosted image.
- Edit in small steps. Send each returned image back in as the next source, one instruction per call, so changes stack.
- Change the editing model by editing one field.

## Prerequisites

You need three things:

- An OpenRouter API key from the [keys page](https://openrouter.ai/keys) and the base URL `https://openrouter.ai/api/v1`.
- An HTTP client. The samples use Python `requests` and TypeScript `fetch`. You can also use curl or the OpenRouter SDK. Any client that sends a JSON POST with an Authorization header works.
- A source image, either a local file or a public URL.

### Which model to use

The default in this guide is `google/gemini-3.1-flash-image`, Nano Banana 2. It takes an image as input and returns an edited image. The Nano Banana family has four current members: Nano Banana 2 (`google/gemini-3.1-flash-image`) is the default in this guide, Nano Banana 2 Lite (`google/gemini-3.1-flash-lite-image`) is the cheapest and fastest, Nano Banana Pro (`google/gemini-3-pro-image`) is slower and higher quality, and the original Nano Banana (`google/gemini-2.5-flash-image`) is the older model the nickname started with.

The image catalog changes often. Models are added, deprecated, and repriced, so a slug you pin today may be retired later. Before you build on a model, check that it accepts image input and supports the editing features you need. You can browse the editing-capable models in the [image model collection](https://openrouter.ai/collections/image-models). For a walkthrough of the catalog, see [image generation models](https://openrouter.ai/blog/tutorials/image-generation-models/).

The samples below use the slug shown in each request, so you can run them as written and change the model later. Keep your key in an environment variable, not in your code:

```
export OPENROUTER_API_KEY="sk-or-..."
```

## Your first image edit

To edit an image, send the source image and a text instruction in a single request. The edited image comes back in the response. Here is a working request in Python that encodes a local file:

```
import base64, os, requests

api_key = os.environ["OPENROUTER_API_KEY"]

# Encode a local source image as a base64 data URL.
with open("portrait.jpg", "rb") as f:
    encoded = base64.b64encode(f.read()).decode()
source = f"data:image/jpeg;base64,{encoded}"

resp = requests.post(
    "https://openrouter.ai/api/v1/images",
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "model": "google/gemini-3.1-flash-image",
        "prompt": "Add a red wool scarf around the person's neck. Keep everything else the same.",
        "input_references": [
            {"type": "image_url", "image_url": {"url": source}}
        ],
    },
)
resp.raise_for_status()
```

The same request in TypeScript:

```
import { readFileSync } from "node:fs";

const apiKey = process.env.OPENROUTER_API_KEY!;
const encoded = readFileSync("portrait.jpg").toString("base64");
const source = `data:image/jpeg;base64,${encoded}`;

const resp = await fetch("https://openrouter.ai/api/v1/images", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${apiKey}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: "google/gemini-3.1-flash-image",
    prompt: "Add a red wool scarf around the person's neck. Keep everything else the same.",
    input_references: [{ type: "image_url", image_url: { url: source } }],
  }),
});
```

The request body is the same in both languages. Put the reference image in `input_references` and the instruction in `prompt`. That is the whole request.

### Encoding the input image: base64 or URL

The `input_references` field takes either a base64 data URL or an HTTP(S) URL. The examples above encode a local file. If your image is already hosted publicly, pass the link directly and skip the encoding:

```
"input_references": [
  {"type": "image_url", "image_url": {"url": "https://example.com/portrait.jpg"}}
]
```

Use a URL when the image is public and hosted, because it keeps the request body small. Use base64 for local or private files. Gemini accepts `image/png`, `image/jpeg`, `image/webp`, `image/heic`, and `image/heif` inputs. Supported formats vary by model, so check the model page before you send.

### Retrieving the edited image from the response

The API returns the edited image as base64 data in the `data` array. Decode the `b64_json` value and write it to a file:

```
data = resp.json()["data"][0]
with open("edited.png", "wb") as out:
    out.write(base64.b64decode(data["b64_json"]))
```

The TypeScript version:

```
import { writeFileSync } from "node:fs";

const { data } = await resp.json();
writeFileSync("edited.png", Buffer.from(data[0].b64_json, "base64"));
```

Open `edited.png` to see the result. If you want a typed client instead of raw HTTP, the OpenRouter SDK has an images resource that calls the same endpoint:

```
from openrouter import OpenRouter

client = OpenRouter(api_key=api_key)
result = client.images.generate(
    model="google/gemini-3.1-flash-image",
    prompt="Add a red wool scarf around the person's neck. Keep everything else the same.",
    input_references=[{"type": "image_url", "image_url": {"url": source}}],
)
```

Install the SDK with `pip install openrouter`. It reuses the `api_key` defined earlier, so no extra setup is needed.

## Writing edit prompts

A generation prompt describes a whole new image. An edit prompt says what to change and what to leave alone. State the change first, then name what must stay the same:

- Object swap: “Replace the coffee mug with a glass of orange juice. Keep the hand position and background unchanged.”
- Background change: “Change the background to a snowy street at night. Keep the subject exactly as is.”
- Style transfer: “Render this photo as a watercolor painting. Preserve the composition and the subject’s pose.”
- Text fix: “Change the sign text to read ‘OPEN’. Match the original font and color.”

You can also write the prompt as a small block of JSON text:

```
"prompt": "{\"edit\": \"add sunglasses\", \"preserve\": [\"face\", \"hair\", \"lighting\"], \"style\": \"photorealistic\"}"
```

The API treats this as plain text, so it is not a special mode. The structure can help the model separate what changes from what stays. Try both the sentence form and the JSON form on your own images and keep whichever works better.

## Editing the result again

One edit will not always give you what you want. To run another pass, send the returned image back in as the next source. Take the `b64_json` value from the response, turn it into a data URL, and pass it in the next `input_references`:

```
def edit(source_data_url, prompt):
    resp = requests.post(
        "https://openrouter.ai/api/v1/images",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "google/gemini-3.1-flash-image",
            "prompt": prompt,
            "input_references": [
                {"type": "image_url", "image_url": {"url": source_data_url}}
            ],
        },
    )
    resp.raise_for_status()
    item = resp.json()["data"][0]
    media_type = item.get("media_type", "image/png")
    return f"data:{media_type};base64,{item['b64_json']}"

step1 = edit(source, "Add a red wool scarf. Keep everything else the same.")
step2 = edit(step1, "Now make the scarf navy blue instead of red.")
step3 = edit(step2, "Add soft morning light coming from the left.")
```

Each call edits the last result, so earlier changes carry forward. Give one instruction per call. Small edits are easier to check and easier to redo when they come back wrong. The model does not remember your earlier prompts, so repeat the parts it should leave alone in each new prompt.

## Changing the editing model

To send the same edit request to a different model, change the `model` field. The source image, the prompt, and the response-handling code stay the same:

```
json={
    "model": "openai/gpt-5-image",  # was google/gemini-3.1-flash-image
    "prompt": "Add a red wool scarf. Keep everything else the same.",
    "input_references": [
        {"type": "image_url", "image_url": {"url": source}}
    ],
},
```

Use `google/gemini-3.1-flash-image` as a fast default. Use `google/gemini-3.1-flash-lite-image` when you want the lowest price. Use `google/gemini-3-pro-image` when you want higher quality and can accept more latency. The original `google/gemini-2.5-flash-image` still works with the same request shape, but the newer models above are the better default. Use a model from another provider, such as `openai/gpt-5-image`, when you want to [compare quality, cost, or speed](https://openrouter.ai/blog/announcements/image-benchmarks/) on your own images. This one-field change only works for models that accept image input and support the same `input_references` shape, so check that a model is editing-capable before you switch to it.

To set a model and its options per environment instead of in code, use OpenRouter [Presets](https://openrouter.ai/docs/guides/features/presets).

## Errors and cost

These failures are common enough to plan for:

- Unsupported input. A model may reject an image format it does not support, and it may reject a URL it cannot reach. Check the file type and the URL before you send.
- Oversized images. Large files can time out or fail. Shrink the image first, because most edits do not need a 40-megapixel source.
- Text instead of an image. A question like “what’s in this photo?” can make the model answer in text instead of producing an image. The API returns this as a `400` error, such as `Gemini could not generate an image (STOP)`, not as an empty response. Write an instruction instead of a question, and check the HTTP status before you decode.

The response reports the cost of each request in USD when usage data is available. Log it to track spend:

```
usage = resp.json().get("usage")
if usage:
    print(f"This edit cost ${usage['cost']}")
```

For batch jobs, stay within [rate limits](https://openrouter.ai/docs/api_reference/limits). Retry 429 and 5xx responses with growing delays between tries, and limit how many edits run at once. Save each returned image before starting its next edit, so one failure does not lose finished work.

## Next steps

Copy the first request, use your own image, and run an edit. To create images from text instead, see the [image generation docs](https://openrouter.ai/docs/guides/overview/multimodal/image-generation). To find current editing-capable models, browse the [image model collection](https://openrouter.ai/collections/image-models).

## Frequently asked questions

### Can I edit an image with the Gemini API?

Yes. Send the source image and a text instruction in one request to `google/gemini-3.1-flash-image` through the OpenRouter API, and the edited image comes back as base64 in the response. That model is Nano Banana 2. The full request fits on one screen, and you can run it in Python, TypeScript, or curl.

### What’s the difference between image generation and image editing?

Image editing changes an existing image. Image generation creates a new image from text. Every editing request includes a source image in `input_references` and an instruction that says what to change and what to keep. If your request has no source image and works from a text prompt alone, that is generation.

### How do I send an image to the API, URL or base64?

The `input_references` field takes a base64 data URL for a local or private file, or a plain HTTP(S) URL for a public hosted image. Use the URL form to keep the request small when the image is already online, and the base64 form when the file is on your machine. Gemini accepts png, jpeg, webp, heic, and heif inputs (`image/png`, `image/jpeg`, `image/webp`, `image/heic`, `image/heif`). Supported formats vary by model, so check the model page before you send.

### Can I use a model other than Gemini to edit images?

Yes. Change the `model` field and keep the rest of the request the same. Check the [image model collection](https://openrouter.ai/collections/image-models) first, because editing support, price, and speed vary by model.

### How do I prompt an AI model to edit an image?

Describe the change first, then name what to preserve, for example “Change the background to a snowy street at night. Keep the subject exactly as is.” One instruction per request works best. For precise results, edit in small steps and send each returned image back in as the source for the next prompt.

## References

- [OpenRouter API keys](https://openrouter.ai/keys): Create and manage the key used in every request.
- [Image model collection](https://openrouter.ai/collections/image-models): The full set of editing-capable models and their input support.
- [Image generation docs](https://openrouter.ai/docs/guides/overview/multimodal/image-generation): The sibling guide for creating images from text.
- [Presets guide](https://openrouter.ai/docs/guides/features/presets): Pin a model and its options per environment instead of setting them in code.
