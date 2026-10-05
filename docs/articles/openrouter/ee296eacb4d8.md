---
vendor: openrouter
title: Seedance 2.5 评测：它最擅长什么、何时使用
original_title: Seedance 2.5 Review: What It's Best At and When to Use It
url: https://openrouter.ai/blog/insights/seedance-2-5-review
date: 2026-09-09
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 7516385b775b
translator: agent
---

# Seedance 2.5 评测：它最擅长什么、何时使用

OpenRouter ·9/9/2026 · 更新于 9/24/2026

Seedance 2.5 自 2026 年 8 月 7 日起在我们的视频 API 上线。截至 2026 年 9 月 3 日，[模型页面](https://openrouter.ai/bytedance/seedance-2.5)列出的价格是每生成一秒视频 $0.1028 起，也就是 480p 折算出来的秒价。这个每秒价格是推导值，不是固定价。计费按视频 token，token 数随输出像素和时长一起缩放，所以同一模型一秒 720p 大约是一秒 480p 的两倍出头。

这个模型的形态也和 Seedance 2.0 不同：时长做到 30 秒而不是 15 秒，分辨率停在 720p 而不是 4K。下面讲的是它擅长什么、各分辨率下一条片段花多少钱、它与我们自己目录数据下的 Seedance 2.0、Wan 3.0 和 Veo 3.1 怎么比，以及我们建议改用其他模型的情形。

## 太长不看

- 最擅长长单镜头，以及从已有素材出发的工作。片段最长 30 秒，`input_references` 接受图像、视频和音频素材，已有片段可以被编辑或延展，而不是重新生成。
- 截至 2026 年 9 月 3 日的在线规格：4 到 30 秒片段，480p 或 720p，六种画幅比，首尾帧控制，音频在同一次生成中产出。
- 成本约 480p 每秒 $0.103、720p 每秒 $0.231，由计费公式推导：24 fps 下（宽 x 高 x fps x 时长）/ 1024 个视频 token，每 token $0.0000107。
- 带视频参考的请求按每 token $0.0000064 计费，比基础价低约 40%，这让编辑和延展的每秒成本比从零生成更便宜。
- 音频不加钱：`generate_audio` 开或关我们都按同一价计费。Veo 3.1 和 Seedance 1.5 Pro 不是这样，两者静音输出都更便宜。
- 需要 1080p 或 4K、需要同片段长度下最低秒价、或需要逐帧可复现时，请换模型。
- slug 是 `bytedance/seedance-2.5`。更高分辨率属于 `bytedance/seedance-2.0`；`bytedance/seedance-2.0-fast` 和 `bytedance/seedance-2.0-mini` 是更便宜的草稿 slug。

## Seedance 2.5 是什么

Seedance 2.5 是 ByteDance（字节跳动）的视频生成模型，能把多种输入合成一路视频输出。你可以纯文本提示词生成，可以用图像钉住镜头的首帧或尾帧，也可以用参考素材引导结果而不锁定具体帧。我们的模型页把它描述为适合长镜头叙事、参考生成、视频编辑和视频延展，这四件事基本覆盖了它的用途。

下面是来自我们[视频模型端点](https://openrouter.ai/api/v1/videos/models)的当前规格快照，方便你看到这些能力在实际中到哪儿为止。

| **字段** | **值** |
| --- | --- |
| Slug | `bytedance/seedance-2.5` |
| 发布日期 | 2026 年 8 月 7 日 |
| 片段长度 | 4 到 30 秒 |
| 分辨率 | 480p、720p |
| 画幅比 | 16:9、4:3、1:1、3:4、9:16、21:9 |
| 帧控制 | `frame_images` 接受 `first_frame` 和 `last_frame` |
| 参考 | `input_references` 接受图像、视频和音频素材 |
| 音频 | `generate_audio`，默认为 true |
| Seed | 接受，但不保证确定性 |
| 提供商透传键 | `watermark`、`req_key`、`output_format` |
| 价格 | 每视频 token $0.0000107；带视频参考时 $0.0000064 |

*最后核验于 2026 年 9 月 3 日，来源为视频模型端点。*

端点还列出了精确输出尺寸。当你更愿意发 `size` 而不是"分辨率+画幅比"时这很有用：480p 有 854x480、752x560、640x640、560x752、480x854、992x432；720p 有 1280x720、1112x834、960x960、834x1112、720x1280、1470x630。

### 五个 Seedance slug，你要的是哪一个

模型名是给人看的标签（ByteDance: Seedance 2.5），slug 是你填进 model 字段的字符串（`bytedance/seedance-2.5`）。我们上架了五个，它们不能互换。Seedance 2.5 最新也最长。[Seedance 2.0](https://openrouter.ai/bytedance/seedance-2.0) 是高分辨率担当：4 到 15 秒、480p 到 4K，480p 和 720p 按每视频 token $0.000007。[Seedance 2.0 Fast](https://openrouter.ai/bytedance/seedance-2.0-fast) 和 [Seedance 2.0 Mini](https://openrouter.ai/bytedance/seedance-2.0-mini) 最长 15 秒、封顶 720p，每 token $0.0000042 和 $0.0000035，是草稿用的两个 slug。[Seedance 1.5 Pro](https://openrouter.ai/bytedance/seedance-1-5-pro) 是老一代，单趟同时生成视频和音频，封顶 1080p 和 12 秒，带音频每 token $0.0000024，不带音频减半。

### 它不做什么

Seedance 2.5 没有列 1080p，也没有 4K 输出。需要其中之一，请找同家族的 Seedance 2.0，或家族之外的 Veo 3.1。这是新版比旧版规格更窄的唯一一项，围绕 2.5 做设计之前，请先对照你的交付格式检查这条。

## 它最擅长什么

4 到 30 秒的时长窗口和参考输入描述的是模型"接受什么"。选择它而不是家族里其他成员的理由更窄：它是家族里为长度、为已有素材而生的那个 Seedance。

![Seedance 2.5 的四个可选请求控制叠加成层级的示意图：纯文本提示词、钉住首尾帧的 frame images、接受图像视频音频素材的 input references、以及收窄波动的 seed 加提供商透传](https://openrouter.ai/blog/images/seedance-2-5-review-controls.png)

*四个可选控制，每个都减少模型能自行改变的程度。帧图与参考素材选择的是不同模式而非叠加使用，两者都发送时帧图优先。*

### 一次生成 30 秒

30 秒是我们平台上最长的单次生成，只有 [Wan 3.0](https://openrouter.ai/alibaba/wan-3.0) 和 [Wan 3.0 Prime](https://openrouter.ai/alibaba/wan-3.0-prime) 持平。其他所有公布时长范围的模型都止步 20 秒或更短。这一点重要，因为长镜头的替代品就是拼接短镜头，而拼接正是连续性崩掉的地方。如果你的交付物是一条 30 秒广告或一个连续场景，这是最短路径。

### 三种模态的参考

从生成代际 2 开始（含 2.5），[`input_references`](https://openrouter.ai/docs/cookbook/video-generation/reference-to-video) 接受图像、音频和视频素材。图像参考带入一张脸、一个产品或一种风格；视频参考给模型一段可编辑或可延展的现成素材；音频参考给它一条可依循的音轨。我们的模型页列了每次请求最多 50 个参考素材——这是模型页的数字，不是我们端点公布的限制，请把确切上限当作"报告值"而非"实测值"。

视频和音频参考适用于代际 2 起的所有 Seedance 模型，所以在家族内这不是 2.5 独有的。它独有于家族对目录其余部分：Wan 3.0、Veo 3.1 和 Kling v3.0 Pro 都只接受图像参考。

### 编辑和延展按更低费率计费

带视频参考且不带帧图的请求按每视频 token $0.0000064 而不是 $0.0000107 计费，便宜约 40%。720p 下就是每秒 $0.138 而不是 $0.231。所以从这个模型拿 30 秒 720p 内容最便宜的方式，是延展你已有的素材，而不是冷启动生成。

### 镜头的两端都能钉，不只是开头

[`frame_images`](https://openrouter.ai/docs/cookbook/video-generation/image-to-video) 接受 `first_frame` 和 `last_frame` 两种类型，你可以钉住一个镜头从哪里开始、在哪里结束，让模型补中间的运动。另一个 30 秒模型 Wan 3.0 只列了 `first_frame`。如果请求同时带帧图和参考素材，帧图优先，任务按图生视频处理——参考不会有可见效果，请求按基础价计费。

### 音频同趟生成、不加钱

`generate_audio` 默认为 true，而我们的视频 token 单价与音频开关无关，静音并不会省钱。Veo 3.1 带音频 $0.40/秒、不带 $0.20；Seedance 1.5 Pro 对静音输出直接把自己减半。模型页还列了多语言视听生成，所以非英文的台词值得先在这里试一把，再决定要不要为配音单独留预算。

## 它的用武之地（附可直接粘贴的提示词）

长度、参考、附带音频，指向一类具体的活：一个连续场景，或改动一段已有素材。三种情况非常贴合。

### 一个长镜头

这是最强的适配。30 秒够演一整场戏，模型也不需要你剪。按顺序写好节拍，每个节拍给镜头一条指令。

```
A single continuous 30-second take in a working bakery at dawn.

Beats, in order: flour dust in low window light; a baker scoring a loaf;
the loaf sliding into the oven; a wide of the shop as the lights come up
and the first customer opens the door.

Camera: slow handheld follow, no cuts, 35mm, natural light only.
Audio: room tone, oven fan, one door chime at the end.
```

### 延展或编辑已有素材

把片段作为视频参考发过来，只描述该变什么或接下来是什么。这就是按更低的视频输入费率计费的那种请求。

```
Video reference: the last 4 seconds of the bakery clip.

Continue the same shot for 10 more seconds. The baker turns toward the
counter and starts wiping it down. Keep the same lighting, lens, grain,
and camera motion. Do not change the room or the wardrobe.
```

### 对话与口播镜头

短句比长句对口型更稳，但 30 秒让你在一个镜头里放两三句，而不是一代际一句。

```
Reference image: a portrait of the speaker.

The speaker sits at a desk in soft office light and says: "We tried it on
one team first. It took a week. Then we rolled it out everywhere."
Natural lip movement synced to the lines, a short pause between sentences,
medium close-up, subtle hand gesture on the last word. Room tone and light
keyboard ambiance underneath.
```

### 可迁移的提示词模式

- 节拍按顺序排、标好时间。30 秒的提示词更像分镜表而不像描写文。
- 点名哪些东西必须保持不变。脸、服装、产品比例、镜头、灯光都值得明说，别指望参考自动带上。
- 点名运镜和镜头。推近、手持、35mm、浅景深，都是模型会执行的指令。
- 480p 打草稿，720p 出成品。两档价格差了两倍多，但提示词的写法没有区别。

## 在你自己的代码里调用

上面那些提示词是进请求体的，不是聊天消息——视频生成不走 `/chat/completions`。它有一个[专用异步端点](https://openrouter.ai/blog/tutorials/video-generation-api/)：向 `POST /api/v1/videos` 提交任务，轮询我们返回的 `polling_url` 直到状态变为 `completed`，然后用 API key 下载结果。生成通常要 30 秒到几分钟，30 秒轮询间隔是合理默认。视频模型也不出现在普通模型列表里，请用 `/api/v1/videos/models` 或[视频模型合集](https://openrouter.ai/collections/video-models)找它们。

最小的文生视频调用就是"提交 + 轮询"。

**cURL**

```
curl -X POST "https://openrouter.ai/api/v1/videos" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bytedance/seedance-2.5",
    "prompt": "A chef plates a bowl of ramen in a narrow shop at night, neon reflections moving across the window. Slow push-in, shallow depth of field.",
    "duration": 12,
    "resolution": "720p",
    "aspect_ratio": "16:9"
  }'

# The 202 response carries { id, polling_url, status }. Poll that URL
# every 30 seconds until status is "completed". A status of "failed",
# "cancelled", or "expired" is terminal, with the reason in .error.
curl "https://openrouter.ai/api/v1/videos/JOB_ID/content?index=0" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  --output shot-01.mp4
```

**TypeScript**

```
const key = process.env.OPENROUTER_API_KEY;
const headers = { Authorization: `Bearer ${key}`, "Content-Type": "application/json" };

const submit = await fetch("https://openrouter.ai/api/v1/videos", {
  method: "POST",
  headers,
  body: JSON.stringify({
    model: "bytedance/seedance-2.5",
    prompt: "A chef plates a bowl of ramen in a narrow shop at night, neon " +
      "reflections moving across the window. Slow push-in.",
    duration: 12,
    resolution: "720p",
    aspect_ratio: "16:9",
  }),
});

const job = await submit.json();
let status = job;

while (status.status === "pending" || status.status === "in_progress") {
  await new Promise((r) => setTimeout(r, 30_000));
  status = await (await fetch(job.polling_url, { headers })).json();
}

if (status.status === "completed") {
  console.log(status.unsigned_urls[0]);
} else {
  // failed, cancelled, or expired are all terminal. The reason is in status.error.
  console.error(status.status, status.error);
}
```

**Python**

```
import os
import time
import requests

headers = {
    "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
    "Content-Type": "application/json",
}

job = requests.post(
    "https://openrouter.ai/api/v1/videos",
    headers=headers,
    json={
        "model": "bytedance/seedance-2.5",
        "prompt": "A chef plates a bowl of ramen in a narrow shop at night, "
        "neon reflections moving across the window. Slow push-in.",
        "duration": 12,
        "resolution": "720p",
        "aspect_ratio": "16:9",
    },
).json()

status = job
while status["status"] in ("pending", "in_progress"):
    time.sleep(30)
    status = requests.get(job["polling_url"], headers=headers).json()

if status["status"] == "completed":
    video = requests.get(status["unsigned_urls"][0], headers=headers)
    with open("shot-01.mp4", "wb") as f:
        f.write(video.content)
else:
    # failed, cancelled, or expired are all terminal. The reason is in "error".
    raise RuntimeError(f"{status['status']}: {status.get('error')}")
```

加上参考，就把上面的调用变成了编辑或延展工作流。下面的例子延展一条已有片段——正是按更低视频输入费率计费的那种请求。分辨率、时长、画幅比都是可选的，seed 值只是占位而不是必填。

**cURL**

```
# A video reference asks the model to edit or extend existing footage.
# frame_images pins exact frames instead, takes priority if you send both,
# and bills at the base rate rather than the video-input rate.
curl -X POST "https://openrouter.ai/api/v1/videos" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bytedance/seedance-2.5",
    "prompt": "Continue the same shot. The chef looks up from the counter, a flicker of recognition. Keep the lighting, lens, and camera motion.",
    "input_references": [
      { "type": "video_url", "video_url": { "url": "https://example.com/ramen-shop.mp4" } },
      { "type": "image_url", "image_url": { "url": "https://example.com/chef.png" } }
    ],
    "duration": 10,
    "resolution": "720p",
    "aspect_ratio": "16:9",
    "generate_audio": true,
    "seed": 42
  }'
```

**TypeScript**

```
const body = {
  model: "bytedance/seedance-2.5",
  prompt: "Continue the same shot. The chef looks up from the counter, a " +
    "flicker of recognition. Keep the lighting, lens, and camera motion.",
  // A video reference asks the model to edit or extend existing footage.
  // frame_images pins exact frames instead, takes priority if you send both,
  // and bills at the base rate rather than the video-input rate.
  input_references: [
    { type: "video_url", video_url: { url: "https://example.com/ramen-shop.mp4" } },
    { type: "image_url", image_url: { url: "https://example.com/chef.png" } },
  ],
  duration: 10,
  resolution: "720p",
  aspect_ratio: "16:9",
  generate_audio: true,
  seed: 42,
};

const res = await fetch("https://openrouter.ai/api/v1/videos", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${process.env.OPENROUTER_API_KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify(body),
});

const job = await res.json(); // { id, polling_url, status: "pending" }
console.log(job.id, job.polling_url);
```

**Python**

```
import os
import requests

body = {
    "model": "bytedance/seedance-2.5",
    "prompt": "Continue the same shot. The chef looks up from the counter, "
    "a flicker of recognition. Keep the lighting, lens, and camera motion.",
    # A video reference asks the model to edit or extend existing footage.
    # frame_images pins exact frames instead, takes priority if you send
    # both, and bills at the base rate rather than the video-input rate.
    "input_references": [
        {"type": "video_url",
         "video_url": {"url": "https://example.com/ramen-shop.mp4"}},
        {"type": "image_url",
         "image_url": {"url": "https://example.com/chef.png"}},
    ],
    "duration": 10,
    "resolution": "720p",
    "aspect_ratio": "16:9",
    "generate_audio": True,
    "seed": 42,
}

job = requests.post(
    "https://openrouter.ai/api/v1/videos",
    headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
    json=body,
).json()

print(job["id"], job["polling_url"])
```

Seedance 2.5 接受 seed，但并非每个提供商都保证确定性。构建依赖可复现输出的工作流之前，请先看[视频生成文档](https://openrouter.ai/docs/guides/overview/multimodal/video-generation)。[提供商专属选项](https://openrouter.ai/docs/cookbook/video-generation/provider-specific-video-options)走 `provider.options.<slug>.parameters`，其中 `<slug>` 是提供商 slug。Seedance 只跑在一家提供商上：`seed`，其允许的透传键是 `watermark`、`req_key` 和 `output_format`。

## 一条片段实际花多少钱

这些请求按公式而不是固定秒价计费，这是上量之前最值得搞懂的一件事。token 数是 24 fps 下的（宽 x 高 x fps x 时长）/ 1024，每个 token 按 $0.0000107 计费，带视频参考时 $0.0000064。所以变量只有像素、秒数、以及你是否供了素材——任何片段在跑之前就能算出价来。

| **分辨率** | **每秒视频 token** | **每秒** | **10 秒片段** | **30 秒片段** | **带视频参考的每秒** |
| --- | --- | --- | --- | --- | --- |
| 480p (854x480) | 约 9,600 | $0.103 | $1.03 | $3.08 | $0.062 |
| 720p (1280x720) | 21,600 | $0.231 | $2.31 | $6.93 | $0.138 |

*最后核验于 2026 年 9 月 3 日。数字由 token 公式和视频模型端点上的单价计算得出。竖屏在像素数相同时与横屏等价，720x1280 的价格与 1280x720 相同。*

把其中一行从头算一遍：16:9 的 10 秒 720p 片段是 (1280 x 720 x 24 x 10) / 1024 = 216,000 个视频 token，216,000 x $0.0000107 = $2.31。每秒那一列就是这个数除以时长、保留三位小数。

对账之前有两个细节值得知道。我们的事前估算用每个分辨率档的标准尺寸，所以 720p 的 21:9 片段会按 1280x720 估，最终扣款以任务完成时提供商上报的 token 数为准。带视频参考的请求预先授权固定 $2 而不是按公式，因为 token 数取决于你输入素材的长度，任务跑起来之前无从得知。这类请求的最终扣款仍按上报 token 数以视频输入费率结算。

拿 Veo 3.1 带音频 $0.40/秒作对照：Seedance 2.5 在 480p 大约便宜四倍，720p 大约便宜 1.7 倍。拿 Wan 3.0 的 480p $0.05/秒、720p $0.10/秒作对照：Seedance 2.5 两档都大约贵一倍。它不是最便宜的视频生成方式，它是最便宜的"30 秒 + 尾帧控制/视频参考/音频参考"生成方式。

## Seedance 2.5 对阵 Seedance 2.0、Wan 3.0 和 Veo 3.1

会算一条片段的钱之后，对比就归结为[哪个需求先撞上你](https://openrouter.ai/docs/cookbook/video-generation/choose-video-model)。下面四个模型都在我们目录里，所有数字来自同一天同一个端点。

![能力矩阵：创作者对 Seedance 2.5 检验的五个类别，长片段、多模态参考、编辑与延展为文档记载，音频为文档记载且有质量反馈，运动真实感仅创作者反馈](https://openrouter.ai/blog/images/seedance-2-5-review-capability-matrix.png)

*创作者会检验的五个类别，对照我们自己的来源对每一项的记载。*

|  | **Seedance 2.5** | **Seedance 2.0** | **Wan 3.0** | **Veo 3.1** |
| --- | --- | --- | --- | --- |
| Slug | `bytedance/seedance-2.5` | `bytedance/seedance-2.0` | `alibaba/wan-3.0` | `google/veo-3.1` |
| 片段长度 | 4 到 30 秒 | 4 到 15 秒 | 2 到 30 秒 | 4、6 或 8 秒 |
| 分辨率 | 480p、720p | 480p 到 4K | 480p 到 1080p | 720p 到 4K |
| 画幅比数量 | 6 | 7 | 5 | 2 |
| 首帧 | 有 | 有 | 有 | 有 |
| 尾帧 | 有 | 有 | 未列出 | 有 |
| 图像参考 | 有 | 有 | 有 | 有 |
| 视频与音频参考 | 有 | 有 | 未列出 | 未列出 |
| 接受 seed | 有 | 有 | 有 | 有 |
| 480p 带音频，每秒 | $0.103 | $0.067 | $0.05 | 无此档 |
| 720p 带音频，每秒 | $0.231 | $0.151 | $0.10 | $0.40 |
| 1080p 带音频，每秒 | 无此档 | $0.374 | $0.20 | $0.40 |
| 4K 带音频，每秒 | 无此档 | $0.778 | 无此档 | $0.60 |

*最后核验于 2026 年 9 月 3 日，来源为视频模型端点。Seedance 的每秒数字由 token 公式推导，而 Wan 3.0 和 Veo 3.1 在同一端点上公布的是固定每秒 SKU——数字可比，但来路不同。*

Seedance 2.5 同时赢在输入广度和时长上。它是这里唯一在一个请求里同时收 30 秒、两种帧控制、视频和音频参考的模型。要 1080p 和 4K 请用 Seedance 2.0，而且两者共有的每个分辨率上它每秒都更便宜。Wan 3.0 用一半的价格做到 30 秒上限并能到 1080p，但只列了首帧控制、没有视频或音频参考——做长的文生视频它是更好的默认，做编辑它更差。Veo 3.1 是固定长度选项，4K 每秒 $0.60；想更便宜地上 4K，还有每秒 $0.30 生成 4K 的 Veo 3.1 Fast。

四个模型都在同一个 `POST /api/v1/videos` 调用和同一个 key 后面，自己跑对比是改一个字段，不是订四份服务。[视频模型合集](https://openrouter.ai/collections/video-models)列了我们上架的全部视频模型，模态筛选已替你做好。

对比也不一定要写代码。我们的[视频基准页面](https://openrouter.ai/benchmarks/media/videos)把同一个提示词跑遍我们上架的每个视频模型，包括 Seedance 2.5、Seedance 2.0、Wan 3.0 和 Veo 3.1，每条产出旁边就是它的成本和生成耗时。看片子，按成本或耗时排序，再挑模型去聊天里试。买任何单之前，先用它核验本文的这些说法。

## 结论

当片段长度、已有素材或附带音频比分辨率更重要时，Seedance 2.5 是对的选择。一次生成 30 秒、图像/视频/音频三种参考、两种帧控制、带视频参考的请求更低价——这个组合在我们目录里没有第二家。需要 1080p 或 4K 用 Seedance 2.0；想用更少的钱拿 30 秒文生视频用 Wan 3.0；交付物是固定 4/6/8 秒的 4K 片段用 Veo 3.1。需要可复现、可送审产出的团队，请把它现在的结果当待审素材而不是成片。

## 常见问题

### Seedance 2.5 真的适合做视频吗？

适合——对更长的单镜头和从已有素材出发的工作。Seedance 2.5 生成 4 到 30 秒片段，接受图像、视频和音频参考，支持首尾帧控制，音频同趟生成且不加价。当你需要 1080p 或 4K 输出、最低每秒价格或逐帧可复现时，它是更弱的选择。

### Seedance 2.5 能做什么？

Seedance 2.5 可以从文本提示词生成视频，从钉住首帧或尾帧的图像生成，或从把主体、风格、已有素材带进新片段的参考素材生成。截至 2026 年 9 月 3 日，它产出 4 到 30 秒、480p 或 720p、六种画幅比，默认带音频，并有一个 seed 参数收窄运行间波动。[模型页面](https://openrouter.ai/bytedance/seedance-2.5)还列了视频编辑、视频延展和每次请求最多 50 个参考素材。

### Seedance 2.5 每条视频多少钱？

Seedance 2.5 按视频 token 计费，token 数是 24 fps 下的（宽 x 高 x fps x 时长）/ 1024，价格随像素和秒数一起缩放。单价每 token $0.0000107，折算约 480p 每秒 $0.103、720p 每秒 $0.231，10 秒 720p 片段大约 $2.31。音频按同价包含在内。带视频参考的请求改按每 token $0.0000064，便宜约 40%。

### 哪个 AI 视频模型最好？

没有唯一最好的视频模型，正确答案取决于哪个需求先撞上你。要 30 秒片段且需要尾帧控制或视频/音频参考，选 Seedance 2.5；要 1080p 和 4K，选 Seedance 2.0；Wan 3.0 也能到 30 秒、每秒更便宜、能到 1080p，但只列了首帧控制；Veo 3.1 适合固定 4/6/8 秒的 4K 片段。它们都走同一个异步视频端点，改一个字段就能用你自己的提示词对比。完整清单见[视频模型合集](https://openrouter.ai/collections/video-models)。

### 我怎么访问 Seedance 2.5 API？

向 `https://openrouter.ai/api/v1/videos` 发 POST 请求，model 字段填 `bytedance/seedance-2.5`，`prompt` 填提示词；然后轮询响应里的 `polling_url` 直到状态 `completed`，用 API key 下载结果。生成是异步的，通常 30 秒到几分钟。完整请求 schema 包括 [webhooks](https://openrouter.ai/docs/cookbook/video-generation/video-generation-webhooks)，见[视频生成页面](https://openrouter.ai/docs/guides/overview/multimodal/video-generation)。

### Seedance 2.5 做音频吗？

做。音频与视频同趟生成，`generate_audio` 默认 true。开不开音频每 token 单价都一样，没有省钱理由去关掉。Veo 3.1 和 Seedance 1.5 Pro 不是这样，两者静音输出都更便宜。模型页还列了多语言视听生成，值得用你的目标语言台词测一把。

### Seedance 2.5 和 Seedance 2.0 有什么区别？

2.5 时长翻倍、分辨率封顶更低。它生成 4 到 30 秒的 480p/720p 片段，接受图像、视频和音频参考，每视频 token $0.0000107。[Seedance 2.0](https://openrouter.ai/bytedance/seedance-2.0) 生成 4 到 15 秒、480p 到 4K，480p/720p 每 token $0.000007，每秒更便宜，也是两者中唯一能到 1080p 或 4K 的。要长度、要编辑已有素材选 2.5，要分辨率选 2.0。

## 参考资料

- [ByteDance: Seedance 2.5 模型页面](https://openrouter.ai/bytedance/seedance-2.5)。入门价、发布日期、每秒费率、参考素材数量和特性描述。
- [视频模型端点 (/api/v1/videos/models)](https://openrouter.ai/api/v1/videos/models)。本文引用的每个视频模型的支持时长、分辨率、画幅比、输出尺寸、帧图类型、seed 支持、透传键和定价 SKU。
- [视频生成文档](https://openrouter.ai/docs/guides/overview/multimodal/video-generation)。请求 schema、异步任务生命周期、提供商透传、webhooks 和零数据保留排除条款。
- [Announcing Video Generation](https://openrouter.ai/blog/announcements/video-generation/)。视频端点的发布范围和第一天支持的模型。
- [视频模型合集](https://openrouter.ai/collections/video-models)。按视频输出筛选的目录，本文对比集的来源。
- [视频基准](https://openrouter.ai/benchmarks/media/videos)。同一提示词下所有视频模型的并排产出，含每个模型的成本和生成时间。
- [ByteDance: Seedance 2.0 模型页面](https://openrouter.ai/bytedance/seedance-2.0)。家族里高分辨率担当的分辨率范围、时长上限和每 token 费率。
- [Alibaba: Wan 3.0 模型页面](https://openrouter.ai/alibaba/wan-3.0)。另一个 30 秒模型的时长上限、分辨率、帧控制和每秒定价。
- [Google: Veo 3.1 模型页面](https://openrouter.ai/google/veo-3.1)。固定片段长度，以及带/不带音频的每秒定价。

以上所有产品来源最后核验于 2026 年 9 月 3 日。创作者报道仅作定位引用，不作为规格或价格来源。
