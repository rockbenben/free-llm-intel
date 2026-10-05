---
vendor: openrouter
title: OpenRouter Video Generation API: A Code-First Guide
original_title: OpenRouter Video Generation API: A Code-First Guide
url: https://openrouter.ai/blog/tutorials/video-generation-api
date: 2026-08-25
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: b4f7b6436181
---

# OpenRouter Video Generation API: A Code-First Guide

OpenRouter ·8/25/2026 · Updated 9/24/2026

Adding video generation to an application is straightforward when you’re testing one model. The complexity shows up when you want to try another. Each provider can have its own endpoint, request parameters, job statuses, polling logic, and output format. That turns a simple model change into another integration to build and maintain.

We put that workflow behind [one asynchronous video API](https://openrouter.ai/docs/guides/overview/multimodal/video-generation). You submit a prompt to `POST /api/v1/videos`, receive a job ID, poll until generation completes, and then download the finished video.

In this guide, we’ll build that flow from start to finish. We’ll submit a job with Seedance, poll it safely, save the MP4, and then run the same integration with Veo and Wan.

## Tl;dr

- One endpoint, multiple video models. Generate with Seedance, Veo, Wan, and other supported models through `POST /api/v1/videos`.
- The workflow is asynchronous. Submit the job, poll its status, then download the completed video.
- Switch models by changing the model identifier. Some model-specific settings, such as duration and aspect ratio, still need adjusting per model, more on that in Step 4, but the endpoint, auth, polling loop, and download logic never change.

## Why an async API works better than the alternatives

Video generation takes longer than a typical API response. A model has to generate and coordinate many frames, maintain visual consistency across them, and sometimes produce matching audio. Depending on the model and requested settings, that process can take from several seconds to a few minutes.

Keeping the original HTTP request open for that entire period is fragile. A browser session can close, a serverless function can reach its execution limit, or a proxy can time out before the video is ready.

An asynchronous API separates submission from completion:

- Submit the generation request.
- Receive a job ID immediately.
- Check the job’s status separately.
- Download the video when generation completes.

Your application can keep running while the model works in the background. It can also recover a job after a restart because generation is attached to a persistent job ID rather than a long-lived connection.

### Integrating directly with one provider

A direct provider integration can work well when you already know which model you want and don’t expect that to change. You use the provider’s authentication, request format, job statuses, polling endpoint, and output response.

The additional work becomes visible when you want to compare another model. The new provider may use different field names for duration and resolution, or return a different job object with different terminal statuses. It may also require another method for downloading the finished asset. Your application then needs a second client, another set of environment variables, and more provider-specific error handling.

There’s nothing inherently wrong with that approach. It just means switching models is an integration change instead of a configuration change, which makes experimentation slower and raises the maintenance cost as your model list grows.

### Running video models locally

Local generation gives you the most control. You can choose the model weights, customize the workflow, keep assets within your own environment, and avoid paying a hosted provider for every generation.

That control comes with infrastructure responsibilities. You need suitable GPU capacity and the right Python and CUDA dependencies. You also need enough storage and a working environment for each model family. Higher resolutions and longer videos increase memory and processing requirements, and adding another model may mean downloading more weights or maintaining another workflow.

This can be worthwhile for teams that already operate GPU infrastructure or require local processing. It’s a heavier starting point when your goal is to add video generation quickly and test several models. The hosted OpenRouter path removes most of that setup, which is what the rest of this guide covers.

### Using one hosted API through OpenRouter

We keep the generation lifecycle consistent across supported video models. The application uses the same API key, `POST /api/v1/videos` endpoint, job-status flow, and output-retrieval process whether the selected model is Seedance, Veo, Wan, or another model in the catalog.

The models still have different capabilities. One may support longer durations, while another offers additional aspect ratios, higher resolutions, audio generation, or provider-specific controls. We expose those differences through the video-model endpoint rather than forcing every model into an identical feature set.

That gives you a stable integration without hiding what makes each model different. Your application can query the current capabilities, build a valid request, and change models without replacing the surrounding job infrastructure.

## Prerequisites and setup

You only need an OpenRouter API key and a tool that can send HTTP requests. The examples here use Python with `requests` and TypeScript with the built-in `fetch` API, but the workflow works from any language that can make an HTTP request.

Start by creating an API key from your OpenRouter account, then store it in an environment variable instead of adding it directly to your source code:

```
export OPENROUTER_API_KEY="sk-or-..."
```

For the Python examples, install `requests` if you don’t already have it:

```
pip install requests
```

OpenRouter authenticates API requests with a bearer token. In Python, we’ll define the shared values once and reuse them throughout the guide:

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

Before submitting a job, you can also [query the video-model endpoint](https://openrouter.ai/docs/guides/overview/multimodal/video-generation#via-the-video-models-api) to see which models are currently available and what each one supports:

```
curl "https://openrouter.ai/api/v1/videos/models" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

The response includes each model’s supported durations, resolutions, aspect ratios, frame-image support, audio capabilities, pricing SKUs, and provider-specific parameters. This is more reliable than assuming that settings accepted by one video model will also work with another.

## Step 1: Submit a video-generation job

Send a POST request to `/api/v1/videos` with the video model. Include a prompt that describes what you want to generate.

`model` is required on every request, and `prompt` is required for text-to-video. Models that support generating a video from image input alone can omit it. You can also provide optional settings such as duration, resolution, aspect ratio, audio generation, reference images, and a seed when the selected model supports them.

We’ll use the same prompt throughout the guide:

```
PROMPT = (
    "A paper boat drifting down a rain-slicked gutter at night, "
    "neon reflections, slow tracking shot, cinematic lighting"
)
```

The following function submits the job using Seedance 2.0:

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

The equivalent cURL request is:

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

A successful request returns HTTP 202 Accepted. The response represents a background job, not the finished video:

```
{
  "id": "job-abc123",
  "status": "pending",
  "polling_url": "https://openrouter.ai/api/v1/videos/job-abc123"
}
```

Store the returned job ID before continuing. If your process restarts, you should be able to resume tracking the existing job instead of submitting and paying for another generation.

## Step 2: Poll the job until it finishes

The `polling_url` returned in Step 1 points to the same job resource you’d reach at `GET /api/v1/videos/{id}`, they’re the same endpoint. A video job can move through the following statuses:

| Status | Meaning |
| --- | --- |
| `pending` | The job has been accepted and is waiting to run |
| `in_progress` | The provider is generating the video |
| `completed` | The video is ready to download |
| `failed` | Generation failed |
| `cancelled` | The job was cancelled |
| `expired` | The job exceeded its allowed lifetime |

Your polling loop should return on `completed` and stop with an error on `failed`, `cancelled`, or `expired`. Otherwise, the application could keep checking a job that will never produce a video.

Documented responses return `polling_url` as a complete URL. The `urljoin` call below is defensive coding that also handles a relative path, so the loop works either way:

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

This loop includes two safeguards that quick examples often omit. First, it handles every documented terminal state instead of waiting only for `completed`. Second, it sets a one-hour timeout so a job can’t leave the process running indefinitely. One edge case worth knowing: because the deadline is checked before each sleep rather than after, a job can run up to one poll interval past the nominal timeout in the worst case before the loop catches it. That’s a fine trade-off for a background job. If you need a hard ceiling, check the deadline again immediately after waking from sleep too.

Our current guidance uses a [30-second polling interval](https://openrouter.ai/docs/guides/overview/multimodal/video-generation). Video jobs usually take from around 30 seconds to several minutes, and checking every second doesn’t make the provider finish sooner. That interval and the timeout ceiling above are both operational guidance, not a documented contract from the endpoint itself, so tune them to your own workload.

The same polling flow in TypeScript:

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

Treat a failed status *request* differently from a failed video *job*. A temporary timeout while polling doesn’t prove the generation itself failed. Retry the status request for the same job ID rather than submitting a new job.

## Step 3: Retrieve and save the video

When the status becomes `completed`, the job response includes a populated `unsigned_urls` array. Each entry points at the job’s authenticated content endpoint:

```
GET /api/v1/videos/{jobId}/content?index=0
```

The index defaults to 0. It only needs to change when a model returns multiple video outputs. Despite the field name, these URLs are not presigned, so send your API key in the Authorization header just as you did while polling.

The helper below uses the first unsigned URL when one is present and reconstructs the content URL from the job ID on the rare chance it isn’t.

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

Streaming the response in chunks avoids loading the entire MP4 into memory before writing it to disk.

Here’s the TypeScript equivalent. Note that this version buffers the download into memory rather than streaming it to disk, which is fine for short clips but worth swapping for a piped stream if you’re routinely downloading long or high-resolution video:

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

At this point, you have a generated MP4 on disk. Move completed videos to storage you control instead of treating the generation endpoint as permanent file hosting. The completed job may also include a `usage` object containing the final cost, which is part of the response body regardless of which language you’re using:

```
usage = completed_job.get("usage") or {}

print("Generation cost:", usage.get("cost"))
print("Used BYOK:", usage.get("is_byok"))
```

Store that value with your internal job record so you can track the actual cost of each generation.

## Step 4: Switch models with one line

The submission, polling, and download functions aren’t tied to Seedance. To use another supported video model, change the model identifier:

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

The endpoint, authentication, response shape, status handling, and download logic stay the same across all three. What doesn’t automatically carry over is every optional setting. Model switching is a one-line change to the code, but it isn’t a guarantee that any given duration, resolution, or aspect ratio combination will validate on the new model. This configuration happens to be portable across all three models covered in this guide:

```
{
  "duration": 4,
  "resolution": "720p",
  "aspect_ratio": "16:9",
  "generate_audio": false
}
```

At the time of writing, the live model endpoint shows Seedance 2.0, Veo 3.1, and Wan 2.7 all supporting that specific combination: four seconds, 720p, 16:9. That’s a shared configuration across these three examples, not a claim that every setting works identically on every model. Move outside it and the differences show up quickly:

- Veo 3.1 currently shows support for four-, six-, and eight-second durations.
- Seedance 2.0 currently shows support for four- to 15-second durations and additional aspect ratios.
- Wan 2.7 currently shows support for two- to 10-second durations and 720p or 1080p resolutions.

A five-second request would validate against Seedance and Wan but fail on Veo. That’s why your application should query `/api/v1/videos/models` before submitting a request rather than assuming that settings accepted by one model will work on another. The numbers above are worth re-checking against that live endpoint before you rely on them, since model capabilities do change.

The same endpoint also exposes `allowed_passthrough_parameters` for model-specific features. These are the keys you’re permitted to send inside the request’s `provider.options` object, which is keyed by provider slug, such as `provider.options["google-vertex"].parameters`. Only the options for the provider that serves your request are forwarded, and unrecognized keys are dropped. Veo, for example, currently lists controls such as `negativePrompt` and `enhancePrompt`, while Wan exposes options including `negative_prompt` and `prompt_extend`.

## A few things worth knowing before this goes to production

The code above is enough to generate and download one video. Once this is running in production, the questions change: you need to control cost, separate job failures from network failures, avoid duplicate processing, and keep tracking jobs after the submitting process exits.

### Check the cost before you scale

Video-generation pricing varies by model and configuration. Duration, resolution, audio generation, and the provider’s billing method can all affect the final cost. Local generation shifts that cost structure entirely, with no per-clip fee but real upfront hardware and maintenance cost instead. A hosted API keeps that cost variable and tied to usage, which is cheaper or more expensive depending on your volume and whether you already own the hardware.

Don’t build one universal cost formula into your application. Query `/api/v1/videos/models` and read the selected model’s `pricing_skus` before displaying an estimate or submitting a large batch. When the job completes, the response can include a `usage` object with the actual cost of that generation:

```
{
  "usage": {
    "cost": 0.5,
    "is_byok": false
  }
}
```

Before running a large batch, estimate the cost using the current model data, then compare the estimate with the actual `usage.cost` values returned by completed jobs. This also helps you spot unexpected changes caused by a higher resolution, longer duration, generated audio, or a different model.

### Handle failures without creating duplicate jobs

A failed polling *request* isn’t the same as a failed video-generation *job*. Your application may lose its connection while checking status even though the provider is still generating the video. If you submit the prompt again immediately, both jobs may complete, leaving you with two videos and two charges for one user request.

Persist the OpenRouter job ID as soon as submission succeeds. A useful job record might contain fields like these:

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

When a status request fails because of a timeout, connection error, or temporary server response, retry the status request using the existing job ID. Only create a new generation after the job itself reaches `failed`, `cancelled`, or `expired`, and only if your application’s retry policy allows another attempt.

Keep job retries separate from polling retries. A polling retry checks the same job again, while a generation retry creates a new paid job. Cap generation retries and retain every job ID created for the same internal request, so you have a complete record when you need to investigate duplicate outputs, provider failures, or unexpected costs.

### Use webhooks when polling stops scaling

[Polling](https://openrouter.ai/docs/guides/overview/multimodal/video-generation#poll-response) is a good default for scripts, prototypes, and small numbers of jobs. It becomes less efficient when your application may have hundreds of generations running at once.

To receive the result automatically, include an [HTTPS callback_url when submitting the job](https://openrouter.ai/docs/guides/overview/multimodal/video-generation#webhooks):

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

You can set the callback for an individual request or configure a default callback for the workspace. The request-level value takes precedence over the workspace default.

We send the webhook when the job reaches a terminal state. Each delivery includes an `X-OpenRouter-Idempotency-Key`, such as:

```
job-abc123-completed
```

Store that value before processing the event. If the webhook is delivered again, your handler can recognize that the job’s already been handled instead of downloading the video or starting the next workflow twice.

When a webhook signing secret is configured, the request also includes an `X-OpenRouter-Signature`. Verify the signature against the raw request body before parsing or re-serializing it. A production handler should then save the new job state, return a fast success response, and move downloading, transcoding, or storage work to a background worker.

### Track concurrent jobs in durable storage

Submitting and waiting are separate operations, so your application can have multiple video jobs running at the same time. Don’t start an unlimited polling loop for every job. Use a bounded worker pool or job queue, and control how many status requests and downloads can run concurrently.

In Python, you could process a limited number of jobs with a thread pool or an asynchronous worker queue. In TypeScript, a concurrency-controlled queue is safer than passing thousands of polling promises directly to `Promise.all()`.

The exact implementation matters less than these rules:

- Save each job ID before beginning to poll.
- Limit the number of active polling and download operations.
- Resume unfinished jobs after a worker restart.
- Don’t resubmit jobs simply because the application restarted.
- Move completed videos to your own storage promptly.

The job ID is the durable link between your application and the generation already in progress. Treat it as part of your application state, not as a value that exists only inside one running process.

## Putting it all together

We’ve covered four steps, and they don’t change no matter which model you’re pointing at. All you do is submit with `POST /api/v1/videos`, poll `GET /api/v1/videos/{id}` while watching for all four terminal states, download the result, and change one string when you want a different model.

Once the async lifecycle is right, the model becomes a setting instead of an architecture decision, whether you’re using the three models covered here or any model added later.

If you’re picking a starting point, [browse the video model catalog](https://openrouter.ai/collections/video-models) to see pricing and capabilities side by side before committing to one.

## Frequently asked questions

### Does OpenRouter support video generation?

Yes, through a dedicated asynchronous API. You submit a prompt to `POST /api/v1/videos`, poll `GET /api/v1/videos/{id}` until the status is `completed`, and download the result. Supported models include Seedance, Veo, Wan, and others, all through the same endpoint.

### How do I generate a video from text with an API?

Send a POST request to `/api/v1/videos` with a model and a prompt. You get back a job ID and a `polling_url`, not the video itself. Poll until the status reaches `completed`, then download from `unsigned_urls` or the `/content` endpoint.

### How do I poll an async video generation job?

Call `GET /api/v1/videos/{id}` on an interval, around 30 seconds is reasonable, until the status reaches a terminal state: `completed`, `failed`, `cancelled`, or `expired`. Set a timeout ceiling so a stuck job can’t hang your process forever.

### Which video models does OpenRouter support?

The catalog includes Seedance, Veo, Wan, and others, and it keeps growing. Query `GET /api/v1/videos/models` for the current list along with each model’s supported resolutions, durations, aspect ratios, and pass-through parameters.

### Can I switch video models without rewriting my code?

Yes. The request shape, authentication, and polling loop are identical across models, only the `model` field changes. Model-specific parameters still reach the provider through the `provider.options` pass-through object.

### Is it cheaper to generate AI video locally or through an API?

Local generation has no per-clip fee once you’ve paid for the hardware, but it requires a capable GPU, dependency management, and a separate setup per model family. A hosted API charges per generation but skips the GPU and setup entirely. Which one is cheaper for you depends on your volume and whether you already own the hardware.

### How long does AI video generation take?

Usually somewhere between thirty seconds and a few minutes, depending on the model, resolution, and clip length. That’s the reason the API is asynchronous instead of a normal blocking call.

### Is video generation eligible for Zero Data Retention?

No. The async retrieval step requires the generated output to be briefly retained so it can be downloaded, so requests with ZDR enforced aren’t routed to video generation.
