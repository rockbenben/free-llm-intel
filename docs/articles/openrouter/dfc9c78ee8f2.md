---
vendor: openrouter
title: Nano Banana API：在代码中使用 Gemini 编辑图像
original_title: Nano Banana API: Edit Images with Gemini in Code
url: https://openrouter.ai/blog/tutorials/nano-banana
date: 2026-09-09
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 5a14fe6952bb
translator: agent
---

# Nano Banana API：在代码中使用 Gemini 编辑图像

OpenRouter ·9/9/2026 · 更新于 9/24/2026

本指南演示如何在代码里用文本提示词编辑图像：把源图和一条编辑指令通过 OpenRouter API 发给 `google/gemini-3.1-flash-image`，编辑后的图片在响应里回来。"Nano Banana"是 Google Gemini 图像模型的绰号，这个 slug 是 Nano Banana 2——该家族默认的快速模型。因为你是通过[一个 API](https://openrouter.ai/blog/announcements/image-api/)访问它，以后想换别的编辑模型，改一个字段就行。

图像编辑是修改已有图片，图像生成是从文本创建新图。本指南讲编辑，所以这里的每个请求都带一张源图。从文本创建图片请看[图像生成文档](https://openrouter.ai/docs/guides/overview/multimodal/image-generation)或[图像生成教程](https://openrouter.ai/blog/tutorials/image-generation/)。

![自然语言图像编辑的前后对比：一张人像照片，提示词 "Add a red wool scarf around the person's neck. Keep everything else the same."，以及编辑后的结果——围巾加上去了，其余保持原样](https://openrouter.ai/blog/images/nano-banana-before-after.png)

## 太长不看

- 编辑只需一个请求：源图放 `input_references`，指令放 `prompt`，从 `data[0].b64_json` 读出编辑后的图、解码存盘。
- `google/gemini-3.1-flash-image` 就是 Nano Banana 2，Gemini 图像的默认快速模型。用之前确认模型接受图像输入——编辑支持因模型而异。
- 本地或私密文件用 base64 data URL 发送；托管图片用普通 HTTP(S) URL。
- 小步编辑：每次把返回的图再发回来当下一步的源图，一次调用一个指令，让改动可叠加。
- 换编辑模型就是改一个字段。

## 前置条件

三样东西：

- 从 [keys 页面](https://openrouter.ai/keys)拿的 OpenRouter API key，和 base URL `https://openrouter.ai/api/v1`。
- 一个 HTTP 客户端。示例用 Python `requests` 和 TypeScript `fetch`。也可以用 curl 或 OpenRouter SDK——任何能发带 Authorization 头的 JSON POST 的客户端都行。
- 一张源图：本地文件或公开 URL。

### 用哪个模型

本指南默认 `google/gemini-3.1-flash-image`，即 Nano Banana 2。它接受图像输入、返回编辑后的图像。Nano Banana 家族目前有四个成员：Nano Banana 2（`google/gemini-3.1-flash-image`，本指南默认）、Nano Banana 2 Lite（`google/gemini-3.1-flash-lite-image`，最便宜最快）、Nano Banana Pro（`google/gemini-3-pro-image`，更慢但质量更高），以及最初的 Nano Banana（`google/gemini-2.5-flash-image`，这个绰号当年就是从它开始的）。

图像目录变化很快：模型不断上架、弃用、改价，今天钉住的 slug 以后可能下架。基于某个模型动工之前，先确认它接受图像输入并支持你要的编辑特性。可编辑模型可以在[图像模型合集](https://openrouter.ai/collections/image-models)浏览，目录走查见[图像生成模型](https://openrouter.ai/blog/tutorials/image-generation-models/)。

下面的示例都用请求里显示的 slug，可以照原样跑、以后再换模型。key 请放环境变量，不要写进代码：

```
export OPENROUTER_API_KEY="sk-or-..."
```

## 第一次图像编辑

编辑图像，就是在单个请求里发出源图和一条文本指令，编辑结果在响应里回来。这是一个能跑的 Python 请求，编码本地文件：

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

TypeScript 版同一请求：

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

两种语言的请求体相同：参考图放 `input_references`，指令放 `prompt`，请求就这么多。

### 输入图的编码方式：base64 还是 URL

`input_references` 接受 base64 data URL 或 HTTP(S) URL。上面的例子编码了本地文件。图片已公开托管的话，直接传链接、跳过编码：

```
"input_references": [
  {"type": "image_url", "image_url": {"url": "https://example.com/portrait.jpg"}}
]
```

图片是公开托管的用 URL，请求体更小；本地或私密文件用 base64。Gemini 接受 `image/png`、`image/jpeg`、`image/webp`、`image/heic` 和 `image/heif` 输入。支持格式因模型而异，发送前先查模型页。

### 从响应里取回编辑后的图像

API 在 `data` 数组里以 base64 返回编辑后的图。解码 `b64_json` 值、写到文件：

```
data = resp.json()["data"][0]
with open("edited.png", "wb") as out:
    out.write(base64.b64decode(data["b64_json"]))
```

TypeScript 版：

```
import { writeFileSync } from "node:fs";

const { data } = await resp.json();
writeFileSync("edited.png", Buffer.from(data[0].b64_json, "base64"));
```

打开 `edited.png` 看结果。不想要裸 HTTP、想用类型化客户端的话，OpenRouter SDK 有个 images 资源，调的是同一个端点：

```
from openrouter import OpenRouter

client = OpenRouter(api_key=api_key)
result = client.images.generate(
    model="google/gemini-3.1-flash-image",
    prompt="Add a red wool scarf around the person's neck. Keep everything else the same.",
    input_references=[{"type": "image_url", "image_url": {"url": source}}],
)
```

用 `pip install openrouter` 安装 SDK。它复用前面定义的 `api_key`，没有额外配置。

## 写编辑提示词

生成提示词描述一整张新图；编辑提示词说什么该变、什么别动。先说改动，再点名哪些必须保持不变：

- 换物体："Replace the coffee mug with a glass of orange juice. Keep the hand position and background unchanged."
- 换背景："Change the background to a snowy street at night. Keep the subject exactly as is."
- 风格迁移："Render this photo as a watercolor painting. Preserve the composition and the subject's pose."
- 修文字："Change the sign text to read 'OPEN'. Match the original font and color."

也可以把提示词写成一小段 JSON 文本：

```
"prompt": "{\"edit\": \"add sunglasses\", \"preserve\": [\"face\", \"hair\", \"lighting\"], \"style\": \"photorealistic\"}"
```

API 把它当普通文本，这不是什么特殊模式。这个结构能帮模型分清"变的"和"留的"。在你的图上把句子版和 JSON 版都试一遍，留效果好的那个。

## 对结果再编辑

一次编辑未必到位。要再来一遍，把返回的图作为下一个源图发回去：取响应里的 `b64_json` 值、转成 data URL、传进下一次 `input_references`：

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

每次调用编辑的是上一个结果，之前的改动会保留下来。一次调用只给一条指令。小步编辑好检查，错了也好回炉。模型不记得你之前的提示词，所以每条新提示词里都要重复它该保持不动的部分。

## 更换编辑模型

同一编辑请求发给别的模型，改 `model` 字段即可。源图、提示词和处理响应的代码都不动：

```
json={
    "model": "openai/gpt-5-image",  # was google/gemini-3.1-flash-image
    "prompt": "Add a red wool scarf. Keep everything else the same.",
    "input_references": [
        {"type": "image_url", "image_url": {"url": source}}
    ],
},
```

`google/gemini-3.1-flash-image` 当快速默认；要最低价用 `google/gemini-3.1-flash-lite-image`；要更高质量、能接受更多延迟，用 `google/gemini-3-pro-image`。最初的 `google/gemini-2.5-flash-image` 用同样的请求形态仍然能跑，但上面这些更新的模型是更好的默认。想在你自己的图上[比较质量、成本或速度](https://openrouter.ai/blog/announcements/image-benchmarks/)，可以换其他提供商的模型，例如 `openai/gpt-5-image`。这一字段改动只对接受图像输入且支持相同 `input_references` 形态的模型有效，切换前先确认该模型有编辑能力。

想按环境而不是按代码设定模型及其选项，用 OpenRouter [Presets](https://openrouter.ai/docs/guides/features/presets)。

## 错误与成本

以下几种失败常见到值得提前规划：

- 输入不受支持。模型可能拒绝它不支持的图片格式，也可能拒绝它访问不了的 URL。发送前先查文件类型和 URL。
- 图片过大。大文件可能超时或失败。先缩小——多数编辑并不需要 4,000 万像素的源图。
- 返回文本而不是图片。像 "what's in this photo?" 这种提问会让模型用文字回答而不产出图片。API 会以 `400` 错误返回（例如 `Gemini could not generate an image (STOP)`），而不是空响应。把提问改成指令，解码之前先检查 HTTP 状态。

有 usage 数据时，响应会以美元报告每个请求的成本。记下来跟踪支出：

```
usage = resp.json().get("usage")
if usage:
    print(f"This edit cost ${usage['cost']}")
```

批处理任务要控制在[速率限制](https://openrouter.ai/docs/api_reference/limits)内。429 和 5xx 用递增间隔重试，并限制同时进行的编辑数。每张返回的图先落盘再开始它的下一次编辑，一次失败不致丢掉已完成的工作。

## 下一步

复制第一个请求、换成你自己的图、跑一次编辑。想从文本创建图片，看[图像生成文档](https://openrouter.ai/docs/guides/overview/multimodal/image-generation)。找当前的可编辑模型，浏览[图像模型合集](https://openrouter.ai/collections/image-models)。

## 常见问题

### 能用 Gemini API 编辑图像吗？

能。通过 OpenRouter API 向 `google/gemini-3.1-flash-image` 发一个请求，带源图和文本指令，编辑后的图以 base64 在响应中返回。这个模型就是 Nano Banana 2。整个请求一屏放得下，Python、TypeScript 或 curl 都能跑。

### 图像生成和图像编辑有什么区别？

图像编辑修改已有图片，图像生成从文本创建新图。每个编辑请求都在 `input_references` 里带一张源图，指令说什么该变、什么该留。请求没有源图、只靠文本提示词工作，那就是生成。

### 图怎么发给 API：URL 还是 base64？

`input_references` 字段接受本地或私密文件的 base64 data URL，也接受公开托管图片的 HTTP(S) URL。图已经在线就用 URL 形态保持请求小巧，文件在本机就用 base64。Gemini 接受 png、jpeg、webp、heic、heif 输入（`image/png`、`image/jpeg`、`image/webp`、`image/heic`、`image/heif`）。支持格式因模型而异，发送前查模型页。

### 能用非 Gemini 的模型编辑图像吗？

能。改 `model` 字段，其余不动。先查[图像模型合集](https://openrouter.ai/collections/image-models)——编辑支持、价格和速度因模型而异。

### 怎么提示 AI 模型编辑图像？

先描述改动，再点名要保留什么，例如 "Change the background to a snowy street at night. Keep the subject exactly as is."。一个请求一条指令效果最好。要精准结果，就小步编辑，把每张返回的图作为下一个提示词的源图再发回去。

## 参考资料

- [OpenRouter API keys](https://openrouter.ai/keys)：创建管理每个请求用到的 key。
- [图像模型合集](https://openrouter.ai/collections/image-models)：可编辑模型的完整清单及其输入支持。
- [图像生成文档](https://openrouter.ai/docs/guides/overview/multimodal/image-generation)：从文本创建图片的姊妹指南。
- [Presets 指南](https://openrouter.ai/docs/guides/features/presets)：按环境而非代码钉住模型及其选项。
