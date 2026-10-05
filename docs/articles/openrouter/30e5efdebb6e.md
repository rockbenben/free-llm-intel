---
vendor: openrouter
title: OpenRouter 视频生成 API：代码优先指南
original_title: OpenRouter Video Generation API: A Code-First Guide
url: https://openrouter.ai/blog/tutorials/video-generation-api
date: 2026-08-25
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: b4f7b6436181
translator: agent
---

# OpenRouter 视频生成 API：代码优先指南

OpenRouter · 2026/8/25 · 更新于 2026/9/24

只测试一个模型时，给应用加视频生成功能很简单。复杂之处在于你想换另一个模型试试。每家供应商都可能有自己的端点、请求参数、任务状态、轮询逻辑和输出格式。于是一次简单的模型更换，就变成了又一次需要构建和维护的集成。

我们把这套工作流收进了[一个异步视频 API](https://openrouter.ai/docs/guides/overview/multimodal/video-generation)。你向 `POST /api/v1/videos` 提交提示词，拿到一个任务 ID，轮询直到生成完成，然后下载成品视频。

本指南将从头到尾搭建这个流程：用 Seedance 提交一个任务、安全地轮询它、保存 MP4 文件，然后用同一套集成分别跑通 Veo 和 Wan。

## Tl;dr

- 一个端点，多个视频模型。通过 `POST /api/v1/videos` 用 Seedance、Veo、Wan 及其他受支持模型进行生成。
- 工作流是异步的：提交任务、轮询状态、然后下载完成的视频。
- 换模型只需改模型标识符。某些模型专属设置（如时长和宽高比）仍需按模型调整（详见第 4 步），但端点、鉴权、轮询循环和下载逻辑完全不变。

## 为什么异步 API 比其他方案更好

视频生成耗时比一般的 API 响应长得多。模型需要生成并协调大量帧、在帧之间保持视觉一致性，有时还要生成匹配的音频。根据模型和所请求的设置，这个过程短则几秒，长则几分钟。

让原始 HTTP 请求在整个生成期间保持打开是很脆弱的。浏览器会话可能关闭、Serverless 函数可能到达执行上限、代理也可能在视频就绪前就超时。

异步 API 把提交和完成分离开来：

- 提交生成请求。
- 立即收到一个任务 ID。
- 另行查询任务状态。
- 生成完成后下载视频。

模型在后台工作时，你的应用可以继续运行。而且即使进程重启，也能恢复跟踪任务——因为生成挂在一个持久化的任务 ID 上，而不是挂在一条长期连接上。

### 直接集成单一供应商

当你已经确定要哪个模型、而且不预期会改变时，直接集成供应商体验可能不错。你用那家供应商的鉴权、请求格式、任务状态、轮询端点和输出响应即可。

但当你想对比另一个模型时，额外的成本就浮现了。新供应商可能给时长和分辨率用不同的字段名，或返回一个终止状态都不同的任务对象，还可能要求另一种下载成品的方式。于是你的应用需要第二个客户端、另一套环境变量，以及更多供应商专属的错误处理。

这种做法本身没什么错。只是换模型变成了改集成而不是改配置——实验因此变慢，而且随着模型列表增长，维护成本也在上升。

### 在本地运行视频模型

本地生成给你最大的控制权。你可以挑选模型权重、定制工作流、把素材留在自己的环境内，也不必为每次生成向托管供应商付费。

但这种控制权伴随着基础设施责任。你需要合适的 GPU 容量、正确的 Python 和 CUDA 依赖，还要为每个模型族准备足够的存储和可用的环境。更高分辨率、更长视频会抬高内存和算力要求；再加一个模型，可能意味着再下载一批权重或再维护一套工作流。

对于已经在运营 GPU 基础设施或必须本地处理的团队，这可能是值得的。但如果你的目标是快速加上视频生成并测试几个模型，这就是一个沉重的起点。托管的 OpenRouter 路径免掉了其中大部分搭建工作，这也是本指南余下部分要讲的内容。

### 通过 OpenRouter 使用一个托管 API

我们在所有受支持的视频模型上保持统一的生成生命周期。无论选的是 Seedance、Veo、Wan 还是目录里的其他模型，应用用的都是同一个 API key、同一个 `POST /api/v1/videos` 端点、同一套任务状态流程和同一个输出获取流程。

模型之间的能力依然各不相同。有的支持更长的时长，有的提供更多宽高比、更高分辨率、音频生成或供应商专属控制项。我们把这些差异通过 video-model 端点暴露出来，而不是强行让所有模型拥有一样的功能集。

这样你既得到稳定的集成，也不必掩盖每个模型的独特之处。你的应用可以查询当前的能力、构建合法的请求，并在不替换周边任务基础设施的情况下更换模型。

## 前置条件与设置

你只需要一个 OpenRouter API key 和一个能发 HTTP 请求的工具。本文示例用 Python 的 `requests` 和 TypeScript 内置的 `fetch` API，但任何能发 HTTP 请求的语言都能走通这个流程。

先从你的 OpenRouter 账户创建一个 API key，然后把它存在环境变量里，而不是直接写进源码：

```
export OPENROUTER_API_KEY="sk-or-..."
```

对于 Python 示例，如果你还没有 `requests`，先安装：

```
pip install requests
```

OpenRouter 用 bearer token 对 API 请求做鉴权。在 Python 里，我们把共享的值定义一次，然后在全文复用：

```
import os
import requests

API_KEY = os.environ["OPENROUTER_API_KEY"]
BASE_URL = "https://openrouter.ai/api/v1"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}
```

在提交任务之前，你还可以[查询 video-model 端点](https://openrouter.ai/docs/guides/overview/multimodal/video-generation#via-the-video-models-api)，看看当前有哪些模型可用、各自支持什么：

```
curl "https://openrouter.ai/api/v1/videos/models" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

响应里包含每个模型支持的时长、分辨率、宽高比、帧图支持、音频能力、价格 SKU 以及供应商专属参数。这比假设某个视频模型接受的设置换个模型也照样能用要可靠得多。

## 第 1 步：提交一个视频生成任务

向 `/api/v1/videos` 发送 POST 请求，带上视频模型，并在请求中包含描述你想要内容的提示词。

`model` 在每个请求里都是必填的，`prompt` 对文生视频是必填的。支持仅用图像输入生成视频的模型可以省略它。当所选模型支持时，你还可以提供可选设置，如时长、分辨率、宽高比、音频生成、参考图像和种子。

整个指南中我们会用同一个提示词：

```
PROMPT = (
    "A paper boat drifting down a rain-slicked gutter at night, "
    "neon reflections, slow tracking shot, cinematic lighting"
)
```

下面的函数用 Seedance 2.0 提交任务：

```
def submit_video(model: str, prompt: str) -> dict:
    response = requests.post(
        f"{BASE_URL}/videos",
        headers=HEADERS,
        json={
            "model": model,
            "prompt": prompt,
            "duration": 4,
            "resolution": "720p",
            "aspect_ratio": "16:9",
            "generate_audio": False,
        },
        timeout=60,
    )

    response.raise_for_status()
    return response.json()


job = submit_video(
    model="bytedance/seedance-2.0",
    prompt=PROMPT,
)

print("Job ID:", job["id"])
print("Status:", job["status"])
print("Polling URL:", job["polling_url"])
```

等价的 cURL 请求是：

```
curl "https://openrouter.ai/api/v1/videos" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bytedance/seedance-2.0",
    "prompt": "A paper boat drifting down a rain-slicked gutter at night, neon reflections, slow tracking shot, cinematic lighting",
    "duration": 4,
    "resolution": "720p",
    "aspect_ratio": "16:9",
    "generate_audio": false
  }'
```

成功的请求返回 HTTP 202 Accepted。响应代表的是一个后台任务，而不是成品视频：

```
{
  "id": "job-abc123",
  "status": "pending",
  "polling_url": "https://openrouter.ai/api/v1/videos/job-abc123"
}
```

继续往下之前，请保存返回的任务 ID。如果进程重启，你应该能够恢复跟踪已有任务，而不是重新提交、再付一次生成的钱。

## 第 2 步：轮询任务直到结束

第 1 步返回的 `polling_url` 指向的就是你在 `GET /api/v1/videos/{id}` 能访问的同一个任务资源——它们是同一个端点。视频任务可能经过以下几种状态：

| 状态 | 含义 |
| --- | --- |
| `pending` | 任务已被接受，正在排队等待运行 |
| `in_progress` | 供应商正在生成视频 |
| `completed` | 视频已可下载 |
| `failed` | 生成失败 |
| `cancelled` | 任务被取消 |
| `expired` | 任务超出允许的生命周期 |

你的轮询循环应在 `completed` 时返回，并在 `failed`、`cancelled` 或 `expired` 时报错停止。否则应用可能一直查询一个永远不会有视频的任务。

文档中的响应会把 `polling_url` 返回为完整 URL。下面代码里的 `urljoin` 调用是防御性写法，也能处理相对路径，因此两种情况下循环都能工作：

```
import time
from urllib.parse import urljoin

TERMINAL_ERROR_STATES = {
    "failed",
    "cancelled",
    "expired",
}


def poll_video(
    initial_job: dict,
    interval: float = 30.0,
    timeout: float = 3600.0,
) -> dict:
    """Poll until the video completes or reaches an error state."""

    polling_url = urljoin(
        "https://openrouter.ai",
        initial_job["polling_url"],
    )

    deadline = time.monotonic() + timeout
    job = initial_job

    while True:
        status = job["status"]
        print("Status:", status)

        if status == "completed":
            return job

        if status in TERMINAL_ERROR_STATES:
            error = job.get("error") or "No error details were returned."
            raise RuntimeError(
                f"Video generation ended with status '{status}': {error}"
            )

        if status not in {"pending", "in_progress"}:
            raise RuntimeError(
                f"Received unexpected job status: {status}"
            )

        if time.monotonic() >= deadline:
            raise TimeoutError(
                f"Job {job['id']} did not complete within "
                f"{timeout} seconds."
            )

        time.sleep(interval)

        response = requests.get(
            polling_url,
            headers={
                "Authorization": f"Bearer {API_KEY}",
            },
            timeout=30,
        )

        response.raise_for_status()
        job = response.json()


completed_job = poll_video(job)
```

这个循环包含两个常被快速示例省略的保障。其一，它处理所有文档记录的终止状态，而不是只等 `completed`。其二，它设了一小时的超时上限，任务不能让进程无限运行下去。有一个值得了解的边界情况：由于截止时间是在每次 sleep 之前检查而非之后，最坏情况下任务可以超出名义超时值一个轮询间隔才被发现。对后台任务来说这是可以接受的权衡。如果你需要一个硬上限，请在 sleep 醒来后立刻再检查一次截止时间。

我们当前的建议是使用 [30 秒的轮询间隔](https://openrouter.ai/docs/guides/overview/multimodal/video-generation)。视频任务通常需要约 30 秒到几分钟，每秒查一次并不会让供应商更快完成。上述这个间隔和超时上限都属于运维建议，而不是端点本身承诺的契约，请根据自己的负载调整。

TypeScript 版本的同一套轮询流程：

```
type VideoJobStatus =
  | "pending"
  | "in_progress"
  | "completed"
  | "failed"
  | "cancelled"
  | "expired";

type VideoJob = {
  id: string;
  polling_url: string;
  status: VideoJobStatus;
  error?: string;
  unsigned_urls?: string[];
};

const apiKey = process.env.OPENROUTER_API_KEY;

if (!apiKey) {
  throw new Error("OPENROUTER_API_KEY is not set");
}

const terminalErrorStates = new Set<VideoJobStatus>([
  "failed",
  "cancelled",
  "expired",
]);

async function pollVideo(
  initialJob: VideoJob,
  intervalMs = 30_000,
  timeoutMs = 3_600_000,
): Promise<VideoJob> {
  const pollingUrl = new URL(
    initialJob.polling_url,
    "https://openrouter.ai",
  );

  const deadline = Date.now() + timeoutMs;
  let job = initialJob;

  while (true) {
    console.log(`Status: ${job.status}`);

    if (job.status === "completed") {
      return job;
    }

    if (terminalErrorStates.has(job.status)) {
      throw new Error(
        job.error ?? `Video generation ${job.status}`,
      );
    }

    if (Date.now() >= deadline) {
      throw new Error(
        `Video job ${job.id} did not complete before the timeout`,
      );
    }

    await new Promise((resolve) =>
      setTimeout(resolve, intervalMs),
    );

    const response = await fetch(pollingUrl, {
      headers: {
        Authorization: `Bearer ${apiKey}`,
      },
    });

    if (!response.ok) {
      throw new Error(
        `Polling failed: ${response.status} ${await response.text()}`,
      );
    }

    job = (await response.json()) as VideoJob;
  }
}
```

请把失败的轮询*请求*和失败的视频*任务*区别对待。轮询时的一次临时超时，并不能证明生成本身失败了。请对同一个任务 ID 重试状态请求，而不是提交新任务。

## 第 3 步：获取并保存视频

当状态变为 `completed` 时，任务响应里会带一个已填充的 `unsigned_urls` 数组。每个条目指向该任务的带鉴权内容端点：

```
GET /api/v1/videos/{jobId}/content?index=0
```

index 默认为 0。只有当模型返回多个视频输出时才需要改变它。尽管字段名叫 unsigned，这些 URL 并不是预签名链接，所以请像轮询时一样在 Authorization 头里发送你的 API key。

下面的辅助函数在有值时使用第一个 unsigned URL；万一没有，则根据任务 ID 重建内容 URL。

```
def download_video(
    job: dict,
    output_path: str = "out.mp4",
    index: int = 0,
) -> None:
    unsigned_urls = job.get("unsigned_urls") or []

    download_url = (
        unsigned_urls[index]
        if len(unsigned_urls) > index
        else (
            f"{BASE_URL}/videos/"
            f"{job['id']}/content?index={index}"
        )
    )

    with requests.get(
        download_url,
        headers={
            "Authorization": f"Bearer {API_KEY}",
        },
        stream=True,
        timeout=180,
    ) as response:
        response.raise_for_status()

        with open(output_path, "wb") as output_file:
            for chunk in response.iter_content(
                chunk_size=1024 * 1024
            ):
                if chunk:
                    output_file.write(chunk)

    print(f"Saved {output_path}")


download_video(completed_job)
```

分块流式读取响应，可以避免在写盘之前把整个 MP4 加载进内存。

下面是 TypeScript 的等价实现。注意这一版会把下载内容先缓冲到内存而不是流式写盘——对短片没问题，但如果你经常下载长视频或高分辨率视频，值得换成分管流（piped stream）：

```
import { writeFile } from "node:fs/promises";

async function downloadVideo(
  job: VideoJob,
  outputPath = "out.mp4",
  index = 0,
): Promise<void> {
  const downloadUrl =
    job.unsigned_urls?.[index] ??
    `https://openrouter.ai/api/v1/videos/` +
      `${job.id}/content?index=${index}`;

  const response = await fetch(downloadUrl, {
    headers: {
      Authorization: `Bearer ${apiKey}`,
    },
  });

  if (!response.ok) {
    throw new Error(
      `Download failed: ${response.status} ` +
      `${await response.text()}`,
    );
  }

  const videoBuffer = Buffer.from(
    await response.arrayBuffer(),
  );

  await writeFile(outputPath, videoBuffer);
  console.log(`Saved ${outputPath}`);
}
```

到这里，磁盘上已经有一个生成的 MP4 了。请把完成的视频转移到你掌控的存储里，而不是把生成端点当永久文件托管。已完成的任务还可能包含一个带最终成本的 `usage` 对象——无论你用哪种语言，它都是响应体的一部分：

```
usage = completed_job.get("usage") or {}

print("Generation cost:", usage.get("cost"))
print("Used BYOK:", usage.get("is_byok"))
```

把这个值与你内部的任务记录存在一起，以便跟踪每次生成的实际成本。

## 第 4 步：一行代码切换模型

提交、轮询、下载这几个函数并不绑定 Seedance。要用另一个受支持的视频模型，只需改模型标识符：

```
# Seedance
MODEL = "bytedance/seedance-2.0"

# Veo
# MODEL = "google/veo-3.1"

# Wan
# MODEL = "alibaba/wan-2.7"

job = submit_video(
    model=MODEL,
    prompt=PROMPT,
)

completed_job = poll_video(job)
download_video(completed_job)
```

三种模型下，端点、鉴权、响应结构、状态处理和下载逻辑全部一致。不会自动带过去的是那些可选设置。换模型是改一行代码，但这并不保证任一时长、分辨率或宽高比组合都能在新模型上通过校验。恰好下面这组配置在本指南覆盖的三个模型上都可移植：

```
{
  "duration": 4,
  "resolution": "720p",
  "aspect_ratio": "16:9",
  "generate_audio": false
}
```

截至本文撰写时，实时的 model 端点显示 Seedance 2.0、Veo 3.1 和 Wan 2.7 都支持这个特定组合：四秒、720p、16:9。这只是这三个示例的共享配置，不是说每个设置在每个模型上表现一致。一旦超出它，差异很快就会显现：

- Veo 3.1 目前显示支持四秒、六秒和八秒时长。
- Seedance 2.0 目前显示支持四到十五秒时长以及更多宽高比。
- Wan 2.7 目前显示支持两到十秒时长，以及 720p 或 1080p 分辨率。

一个五秒的请求能在 Seedance 和 Wan 上通过校验，但在 Veo 上会失败。这就是为什么你的应用应该在提交请求前查询 `/api/v1/videos/models`，而不是假设某个模型接受的设置换个模型也能用。上面的数字在你依赖它们之前值得再对着那个实时端点复核一遍，因为模型能力确实会变。

同一个端点还暴露模型专属功能的 `allowed_passthrough_parameters`。这些是你允许放进请求 `provider.options` 对象里的键；`provider.options` 以供应商 slug 为键，例如 `provider.options["google-vertex"].parameters`。只有实际服务你请求的那家供应商的 options 会被转发，无法识别的键会被丢弃。例如 Veo 目前列出了 `negativePrompt`、`enhancePrompt` 这类控制项，而 Wan 暴露了 `negative_prompt`、`prompt_extend` 等选项。

## 上生产之前值得了解的几件事

上面的代码足够生成并下载一个视频了。但一旦跑在生产环境，问题就变了：你要控制成本、区分任务失败和网络失败、避免重复处理，还要在提交进程退出后继续跟踪任务。

### 扩容前先检查成本

视频生成的定价因模型和配置而异。时长、分辨率、音频生成以及供应商的计费方式都可能影响最终成本。本地生成则彻底换了一套成本结构：没有单条费用，但前置的硬件和维护开销是实打实的。托管 API 让成本保持可变并与用量挂钩——取决于你的量级和是否已有硬件，它可能更便宜也可能更贵。

不要在应用里写死一个万能成本公式。在展示预估或提交大批量之前，先查询 `/api/v1/videos/models` 并读取所选模型的 `pricing_skus`。任务完成时，响应可能带一个 `usage` 对象，报告该次生成的实际成本：

```
{
  "usage": {
    "cost": 0.5,
    "is_byok": false
  }
}
```

在跑大批量之前，先用当前的模型数据估算成本，然后把估算和已完成任务返回的实际 `usage.cost` 做对比。这也有助于你发现由更高分辨率、更长时长、生成音频或不同模型引起的意外变化。

### 处理失败但不制造重复任务

一次失败的轮询*请求*不等于一次失败的视频生成*任务*。你的应用可能在查询状态时断线，而供应商其实还在生成视频。如果你立刻重新提交提示词，两个任务可能都完成——一个用户需求产出两个视频、两笔扣费。

提交成功后请立刻持久化 OpenRouter 任务 ID。一条有用的任务记录可能包含这些字段：

```
{
  "internal_request_id": "req_9f21",
  "openrouter_job_id": "job-abc123",
  "model": "bytedance/seedance-2.0",
  "status": "pending",
  "attempt_number": 1,
  "submitted_at": "2026-07-27T12:00:00Z",
  "output_location": null,
  "cost": null,
  "error": null
}
```

当状态请求因超时、连接错误或临时服务端响应而失败时，用已有任务 ID 重试状态请求。只有当任务本身到达 `failed`、`cancelled` 或 `expired`，并且你的应用重试策略允许再一次尝试时，才创建新的生成。

请把任务重试和轮询重试分开。轮询重试是再查同一个任务，生成重试则是创建一个新的付费任务。请对生成重试设上限，并保留同一内部请求创建的所有任务 ID，这样在排查重复输出、供应商故障或意外成本时你有完整记录。

### 轮询撑不住时使用 Webhook

对脚本、原型和少量任务来说，[轮询](https://openrouter.ai/docs/guides/overview/multimodal/video-generation#poll-response)是很好的默认方案。但当你的应用可能同时跑几百个生成任务时，它的效率就下降了。

要自动接收结果，请在[提交任务时带上一个 HTTPS 的 callback_url](https://openrouter.ai/docs/guides/overview/multimodal/video-generation#webhooks)：

```
{
  "model": "bytedance/seedance-2.0",
  "prompt": "A paper boat drifting through neon reflections",
  "duration": 4,
  "resolution": "720p",
  "aspect_ratio": "16:9",
  "callback_url": "https://example.com/webhooks/openrouter-video"
}
```

你可以为单个请求设置回调，也可以为工作区配置默认回调。请求级的值优先于工作区默认值。

当任务到达终止状态时我们会发送 webhook。每次投递都带一个 `X-OpenRouter-Idempotency-Key`，例如：

```
job-abc123-completed
```

请在处理事件之前保存这个值。如果 webhook 再次投递，你的处理函数可以识别出该任务已经被处理过，而不会把视频下载两次或把下一个工作流启动两次。

当配置了 webhook 签名密钥时，请求还会带上 `X-OpenRouter-Signature`。请在解析或重新序列化之前，对原始请求体验证签名。一个生产级的处理函数应当保存新的任务状态、快速返回成功响应，并把下载、转码或存储工作交给后台 worker。

### 用持久化存储跟踪并发任务

提交和等待是两个独立操作，所以你的应用可以同时有多个视频任务在跑。不要为每个任务开一个无上限的轮询循环。请使用有界的 worker 池或任务队列，并控制可以同时运行的状态请求与下载数量。

在 Python 里，你可以用线程池或异步 worker 队列处理有限数量的任务。在 TypeScript 里，带并发控制的队列比把成千上万个轮询 promise 直接丢给 `Promise.all()` 更安全。

具体实现怎么写并不重要，重要的是这几条规则：

- 每个任务 ID 在开始轮询之前就要保存。
- 限制活跃的轮询与下载操作数量。
- worker 重启后恢复未完成任务。
- 不要因为应用重启就重新提交任务。
- 完成的视频要尽快转移到你自己的存储。

任务 ID 是你的应用与已在进行的生成之间持久的纽带。把它当作应用状态的一部分，而不是只存在于某一个运行中进程里的值。

## 总结

我们已经走完四个步骤，而无论你指向哪个模型，它们都不变：用 `POST /api/v1/videos` 提交，用 `GET /api/v1/videos/{id}` 轮询并留意全部四个终止状态，下载结果；想换模型时改一个字符串即可。

一旦这套异步生命周期理顺了，模型就变成了一个配置项，而不是架构决策——无论你用的是本文覆盖的三个模型还是以后新增的任何模型。

如果你在选起点，可以[浏览视频模型目录](https://openrouter.ai/collections/video-models)，在锁定一家之前并排看看各家定价与能力。

## 常见问题

### OpenRouter 支持视频生成吗？

支持，通过一个专用的异步 API。你把提示词提交到 `POST /api/v1/videos`，轮询 `GET /api/v1/videos/{id}` 直到状态为 `completed`，然后下载结果。受支持的模型包括 Seedance、Veo、Wan 及其他，全部走同一个端点。

### 如何用 API 从文本生成视频？

向 `/api/v1/videos` 发送一个带模型和提示词的 POST 请求。你拿回的是任务 ID 和一个 `polling_url`，而不是视频本身。轮询直到状态到达 `completed`，然后从 `unsigned_urls` 或 `/content` 端点下载。

### 如何轮询异步视频生成任务？

按固定间隔调用 `GET /api/v1/videos/{id}`（大约 30 秒比较合理），直到状态到达终止状态：`completed`、`failed`、`cancelled` 或 `expired`。请设置超时上限，卡住的任务不能让你的进程永远挂着。

### OpenRouter 支持哪些视频模型？

目录包含 Seedance、Veo、Wan 及其他，而且还在增长。查询 `GET /api/v1/videos/models` 可获得当前列表，以及每个模型支持的分辨率、时长、宽高比和透传参数。

### 不换代码能换视频模型吗？

能。请求结构、鉴权和轮询循环在所有模型上完全相同，只有 `model` 字段会变。模型专属参数仍然通过 `provider.options` 透传对象送达供应商。

### 本地生成 AI 视频和通过 API 生成，哪个更便宜？

本地生成在付清硬件后没有单条费用，但需要够用的 GPU、依赖管理，以及每个模型族一套独立环境。托管 API 按生成次数收费，但完全省掉 GPU 和环境搭建。哪个对你更便宜，取决于你的量级以及你是否已有硬件。

### AI 视频生成要多久？

通常在三十秒到几分钟之间，取决于模型、分辨率和片段长度。正因为如此，API 才设计为异步而不是普通阻塞调用。

### 视频生成适用于零数据保留（ZDR）吗？

不适用。异步获取这一步要求生成结果被短暂保留，以便能够下载，因此强制 ZDR 的请求不会被路由到视频生成。
