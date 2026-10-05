---
vendor: openrouter
title: Seedance 2.5 Review: What It's Best At and When to Use It
original_title: Seedance 2.5 Review: What It's Best At and When to Use It
url: https://openrouter.ai/blog/insights/seedance-2-5-review
date: 2026-09-09
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 7516385b775b
---

# Seedance 2.5 Review: What It's Best At and When to Use It

OpenRouter ·9/9/2026 · Updated 9/24/2026

Seedance 2.5 has been live on our video API since August 7, 2026, and as of September 3, 2026, the [model page](https://openrouter.ai/bytedance/seedance-2.5) lists it from $0.1028 per second of generated video, which is what 480p works out to. That per-second figure is derived, not fixed. Billing is per video token, and the token count scales with output pixels as well as duration, so a second of 720p costs a little over twice a second of 480p from the same model.

The model is also a different shape from Seedance 2.0. It runs to 30 seconds instead of 15, and it stops at 720p instead of 4K. Below is what it does well, what a clip costs at each resolution, how it compares to Seedance 2.0, Wan 3.0, and Veo 3.1 on our own catalog data, and the cases where we’d recommend a different model.

## Tl;dr

- Best at long single takes and at work that starts from existing footage. Clips run to 30 seconds, and `input_references` accepts image, video, and audio assets, so an existing clip can be edited or extended rather than regenerated.
- Live specs as of September 3, 2026: clips of 4 to 30 seconds, 480p or 720p, six aspect ratios, first and last frame control, and audio generated in the same pass.
- Cost runs about $0.103 per second at 480p and $0.231 at 720p, derived from the billing formula of (width x height x fps x duration) / 1024 video tokens at 24 fps, billed at $0.0000107 apiece.
- A request that carries a video reference bills at $0.0000064 per token, about 40% below the base rate, which makes editing and extension cheaper per second than generating from scratch.
- Audio costs nothing extra, since we bill the same rate whether `generate_audio` is on or off. That isn’t true of Veo 3.1 or Seedance 1.5 Pro, which both charge less for silent output.
- Use a different model when you need 1080p or 4K, when you want the lowest price per second at the same clip length, or when you need frame-exact reproducibility.
- The slug is `bytedance/seedance-2.5`. Higher resolutions belong to `bytedance/seedance-2.0`, and `bytedance/seedance-2.0-fast` and `bytedance/seedance-2.0-mini` are the cheaper draft slugs.

## What Seedance 2.5 is

Seedance 2.5 is ByteDance’s video generation model, and it takes several kinds of input into one video output. You can generate from a text prompt alone, from images that fix the first or last frame of a shot, or from reference assets that steer the result without pinning a specific frame. Our model page describes it as suited to long-form storytelling, reference-based generation, video editing, and video extension, and those four jobs cover most of what it’s used for.

Here’s the current spec snapshot from our [video models endpoint](https://openrouter.ai/api/v1/videos/models), so you can see where those capabilities stop in practice.

| **Field** | **Value** |
| --- | --- |
| Slug | `bytedance/seedance-2.5` |
| Released | August 7, 2026 |
| Clip length | 4 to 30 seconds |
| Resolutions | 480p, 720p |
| Aspect ratios | 16:9, 4:3, 1:1, 3:4, 9:16, 21:9 |
| Frame control | `frame_images` accepts `first_frame` and `last_frame` |
| References | `input_references` accepts image, video, and audio assets |
| Audio | `generate_audio`, defaults to true |
| Seed | Accepted, though determinism isn’t guaranteed |
| Provider passthrough keys | `watermark`, `req_key`, `output_format` |
| Price | $0.0000107 per video token, or $0.0000064 with a video reference |

*Last checked September 3, 2026 on the video models endpoint.*

The endpoint also lists the exact output sizes, which is useful when you’d rather send `size` than a resolution and an aspect ratio: 854x480, 752x560, 640x640, 560x752, 480x854, 992x432 at 480p, and 1280x720, 1112x834, 960x960, 834x1112, 720x1280, 1470x630 at 720p.

### Five Seedance slugs, and which one you want

The model name is the human-readable label, ByteDance: Seedance 2.5, while the slug is the string you put in the model field, `bytedance/seedance-2.5`. We carry five, and they aren’t interchangeable. Seedance 2.5 is the newest and the longest. [Seedance 2.0](https://openrouter.ai/bytedance/seedance-2.0) is the higher-resolution model, with clips of 4 to 15 seconds at 480p through 4K for $0.000007 per video token at 480p and 720p. [Seedance 2.0 Fast](https://openrouter.ai/bytedance/seedance-2.0-fast) and [Seedance 2.0 Mini](https://openrouter.ai/bytedance/seedance-2.0-mini) run to 15 seconds at a 720p ceiling for $0.0000042 and $0.0000035 per token, which makes them the draft slugs. [Seedance 1.5 Pro](https://openrouter.ai/bytedance/seedance-1-5-pro) is the older model that generates video and audio in a single pass, stops at 1080p and 12 seconds, and bills $0.0000024 per token with audio or half that without.

### What it doesn’t do

Seedance 2.5 lists no 1080p and no 4K output. If you need either, that’s Seedance 2.0 in the same family, or Veo 3.1 outside it. This is the one spec where the newer version is narrower than the older one, and it’s worth checking against your delivery format before you build around 2.5.

## What it’s best at

The 4-to-30 second window and the reference inputs describe what the model accepts. The reason to choose it over the rest of the family is narrower than that. It’s the Seedance model for length and for footage you already have.

![Diagram of Seedance 2.5's four optional request controls stacked as layers: text prompt only, frame images pinning first and last frames, input references accepting image, video, and audio assets, and seed plus provider passthrough narrowing variance](https://openrouter.ai/blog/images/seedance-2-5-review-controls.png)

*Four optional controls, each reducing how much the model can change on its own. Frame images and reference assets select different modes rather than combining, and frame images take priority if both are sent.*

### Thirty seconds in one generation

Thirty seconds is the longest single generation we carry, matched only by [Wan 3.0](https://openrouter.ai/alibaba/wan-3.0) and [Wan 3.0 Prime](https://openrouter.ai/alibaba/wan-3.0-prime). Every other model that publishes a duration range stops at 20 seconds or less. That matters because the alternative to a long take is stitching short ones, and stitching is where continuity breaks down. If your deliverable is a 30-second spot or a single continuous scene, this is the shortest path to it.

### References in three modalities

[`input_references`](https://openrouter.ai/docs/cookbook/video-generation/reference-to-video) accepts image, audio, and video assets on Seedance generation 2 and newer, which includes 2.5. Image references carry a face, a product, or a style. A video reference gives the model existing footage to edit or extend. An audio reference gives it a track to work against. Our model page lists up to 50 reference assets per request, which is a model page figure rather than a limit our endpoint publishes, so treat the exact ceiling as reported rather than measured.

Video and audio references work on every Seedance model from generation 2 onward, so this isn’t unique to 2.5 inside the family. It does separate the family from the rest of the catalog. Wan 3.0, Veo 3.1, and Kling v3.0 Pro all take image references only.

### Editing and extension bill at a lower rate

A request that carries a video reference and no frame images bills at $0.0000064 per video token instead of $0.0000107, about 40% less. At 720p that’s $0.138 per second instead of $0.231. So the cheapest way to get 30 seconds of 720p out of this model is to extend footage you already have rather than to generate it cold.

### Both ends of a shot, not just the first

[`frame_images`](https://openrouter.ai/docs/cookbook/video-generation/image-to-video) accepts entries typed as `first_frame` and `last_frame`, so you can fix where a shot begins and ends and let the model fill in the motion between them. Wan 3.0, the other 30-second model, lists `first_frame` only. If a request carries both frame images and reference assets, the frame images take priority and the job is treated as image-to-video, so the references will have no visible effect and the request bills at the base rate.

### Audio in the same pass, at no extra charge

`generate_audio` defaults to true, and we price video tokens identically whether audio is on or off, so muting a generation saves nothing. Veo 3.1 charges $0.40 per second with audio against $0.20 without, and Seedance 1.5 Pro halves its own rate for silent output. The model page also lists multilingual audiovisual generation, so a line in a language other than English is worth attempting here before you budget for a separate voice pass.

## Where it fits, with prompts you can paste

Length, references, and included audio fit a specific kind of job: one continuous scene, or a change to footage that already exists. Three cases fit that description well.

### One long take

This is the strongest fit, since 30 seconds is enough for a full scene and the model doesn’t need you to cut. Write the beats in order and give the camera one instruction per beat.

```
A single continuous 30-second take in a working bakery at dawn.

Beats, in order: flour dust in low window light; a baker scoring a loaf;
the loaf sliding into the oven; a wide of the shop as the lights come up
and the first customer opens the door.

Camera: slow handheld follow, no cuts, 35mm, natural light only.
Audio: room tone, oven fan, one door chime at the end.
```

### Extending or editing existing footage

Send the clip as a video reference and describe only what should change or what comes next. This is the request shape that bills at the lower video-input rate.

```
Video reference: the last 4 seconds of the bakery clip.

Continue the same shot for 10 more seconds. The baker turns toward the
counter and starts wiping it down. Keep the same lighting, lens, grain,
and camera motion. Do not change the room or the wardrobe.
```

### Dialogue and talking heads

Short lines sync better than long ones, but 30 seconds gives you room for two or three of them in one take instead of one line per generation.

```
Reference image: a portrait of the speaker.

The speaker sits at a desk in soft office light and says: "We tried it on
one team first. It took a week. Then we rolled it out everywhere."
Natural lip movement synced to the lines, a short pause between sentences,
medium close-up, subtle hand gesture on the last word. Room tone and light
keyboard ambiance underneath.
```

### Prompt patterns that transfer

- Order the beats and time them. A 30-second prompt reads more like a shot list than a description.
- Name what must stay fixed. Face, wardrobe, product proportions, lens, and lighting are all worth stating explicitly rather than assuming a reference carries them.
- Name the camera move and the lens. Push-in, handheld, 35mm, and shallow depth of field are instructions the model acts on.
- Draft at 480p and finish at 720p. The two resolutions differ by more than a factor of two in price, but not in how the prompt is written.

## Calling it from your own code

Those prompts go into a request body rather than a chat message, because video generation doesn’t run on `/chat/completions`. It has a [dedicated asynchronous endpoint](https://openrouter.ai/blog/tutorials/video-generation-api/), so you submit a job to `POST /api/v1/videos`, poll the `polling_url` we return until the status reads `completed`, then download the result with your API key. Generation usually takes from 30 seconds to a few minutes, and a 30-second polling interval is a reasonable default. Video models also don’t appear in the plain models list, so use `/api/v1/videos/models` or the [video model collection](https://openrouter.ai/collections/video-models) to find them.

The minimal text-to-video call is a submit and a poll.

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

Adding references turns that into an editing or extension workflow. The example below extends an existing clip, which is the request shape that bills at the lower video-input rate. Resolution, duration, and aspect ratio are all optional, and the seed value is a placeholder rather than a required value.

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

Seedance 2.5 accepts a seed, but determinism isn’t guaranteed by every provider. Check the [video generation docs](https://openrouter.ai/docs/guides/overview/multimodal/video-generation) before you build a workflow that depends on repeatable output. [Provider-specific options](https://openrouter.ai/docs/cookbook/video-generation/provider-specific-video-options) travel under `provider.options.<slug>.parameters`, where `<slug>` is the provider slug. Seedance runs on one provider, `seed`, and its allowed passthrough keys are `watermark`, `req_key`, and `output_format`.

## What a clip actually costs

Those requests bill on a formula rather than a flat per-second rate, which is the single most useful thing to understand before you scale up. The token count is (width x height x fps x duration) / 1024 at 24 fps, and every token bills at $0.0000107, or $0.0000064 when the request carries a video reference. So the only variables are pixels, seconds, and whether you’re supplying footage, and you can price any clip before you run it.

| **Resolution** | **Video tokens per second** | **Per second** | **10-second clip** | **30-second clip** | **Per second with a video reference** |
| --- | --- | --- | --- | --- | --- |
| 480p (854x480) | about 9,600 | $0.103 | $1.03 | $3.08 | $0.062 |
| 720p (1280x720) | 21,600 | $0.231 | $2.31 | $6.93 | $0.138 |

*Last checked September 3, 2026. Figures are calculated from the token formula and the per-token rates on the video models endpoint. Vertical formats cost the same as landscape at equal pixel counts, so 720x1280 prices match 1280x720.*

Working one row through end to end, a 10-second 720p clip in 16:9 is (1280 x 720 x 24 x 10) / 1024, which comes to 216,000 video tokens, and 216,000 tokens at $0.0000107 is $2.31. The per-second column is that figure divided by duration and rounded to three decimals.

Two details are worth knowing before you reconcile a bill. Our up-front estimate uses the standard dimensions for each resolution tier, so a 21:9 clip at 720p is estimated as if it were 1280x720, and the final charge comes from the token count the provider reports when the job completes. A request that carries a video reference is authorized at a flat $2 instead of the formula, because the token count depends on the length of your input footage, which we don’t know until the job runs. The final charge for those requests still comes from the reported token count at the video-input rate.

Measured against Veo 3.1 with audio at $0.40 per second, Seedance 2.5 at 480p is about four times cheaper and at 720p about 1.7 times cheaper. Measured against Wan 3.0 at $0.05 per second at 480p and $0.10 at 720p, Seedance 2.5 costs about twice as much at both. It isn’t the cheapest way to generate video. It’s the cheapest way to generate a 30-second clip with last-frame control, video references, or audio references.

## Seedance 2.5 against Seedance 2.0, Wan 3.0, and Veo 3.1

Once you can price a clip, the comparison comes down to [which requirement you hit first](https://openrouter.ai/docs/cookbook/video-generation/choose-video-model). All four models below are in our catalog, and every figure comes from the same endpoint on the same day.

![Capability matrix comparing five categories creators test for Seedance 2.5, showing long clips, multimodal references, and editing and extension as documented, audio as documented with quality reports, and motion realism as creator reports only](https://openrouter.ai/blog/images/seedance-2-5-review-capability-matrix.png)

*The five categories creators test, against what our own sources document for each one.*

|  | **Seedance 2.5** | **Seedance 2.0** | **Wan 3.0** | **Veo 3.1** |
| --- | --- | --- | --- | --- |
| Slug | `bytedance/seedance-2.5` | `bytedance/seedance-2.0` | `alibaba/wan-3.0` | `google/veo-3.1` |
| Clip length | 4 to 30 seconds | 4 to 15 seconds | 2 to 30 seconds | 4, 6, or 8 seconds |
| Resolutions | 480p, 720p | 480p to 4K | 480p to 1080p | 720p to 4K |
| Aspect ratios | 6 | 7 | 5 | 2 |
| First frame | Yes | Yes | Yes | Yes |
| Last frame | Yes | Yes | Not listed | Yes |
| Image references | Yes | Yes | Yes | Yes |
| Video and audio references | Yes | Yes | Not listed | Not listed |
| Seed accepted | Yes | Yes | Yes | Yes |
| 480p with audio, per second | $0.103 | $0.067 | $0.05 | Not available |
| 720p with audio, per second | $0.231 | $0.151 | $0.10 | $0.40 |
| 1080p with audio, per second | Not available | $0.374 | $0.20 | $0.40 |
| 4K with audio, per second | Not available | $0.778 | Not available | $0.60 |

*Last checked September 3, 2026 on the video models endpoint. Seedance per-second figures are derived from the token formula, while Wan 3.0 and Veo 3.1 publish flat per-second SKUs on that same endpoint, so the figures are comparable but reached by different routes.*

Seedance 2.5 wins on inputs and on length together. It’s the only model here that takes 30 seconds, both frame types, and video and audio references in the same request. Seedance 2.0 is the one to use for 1080p and 4K, and it’s cheaper per second at every resolution the two share. Wan 3.0 matches the 30-second ceiling at half the price and reaches 1080p, but it lists first-frame control only and no video or audio references, so it’s the better default for long text-to-video and the worse one for editing. Veo 3.1 is the fixed-length option, at $0.60 per second for 4K, and Veo 3.1 Fast generates 4K for $0.30 per second if you want the cheaper route to that resolution.

Because all four sit behind the same `POST /api/v1/videos` call and the same key, running your own comparison is a one-field change rather than four subscriptions. The [video model collection](https://openrouter.ai/collections/video-models) lists everything we carry with the modality filter already applied.

You don’t have to write code to compare them. Our [video benchmarks page](https://openrouter.ai/benchmarks/media/videos) runs the same prompt through every video model we carry, including Seedance 2.5, Seedance 2.0, Wan 3.0, and Veo 3.1, and shows each output next to what it cost and how long it took to generate. Watch the clips, sort by cost or generation time, then pick the models you want to try in chat. Use it to check the claims in this review before you spend anything.

## The verdict

Seedance 2.5 is the right choice when clip length, existing footage, or included audio matter more than resolution. Thirty seconds in one generation, image, video, and audio references, both frame types, and a lower rate for video-referenced requests are a combination nothing else in our catalog offers. Use Seedance 2.0 when you need 1080p or 4K, Wan 3.0 when you want 30 seconds of text-to-video for less, and Veo 3.1 when a fixed 4, 6, or 8-second 4K clip is the deliverable. Teams that need repeatable, approval-ready output should treat its results as material to review rather than as finals.

## FAQ

### Is Seedance 2.5 actually good for videos?

Yes, for longer single takes and for work that starts from existing footage. Seedance 2.5 generates clips of 4 to 30 seconds, accepts image, video, and audio references, supports first- and last-frame control, and generates audio in the same pass at the same rate. It’s a weaker choice when you need 1080p or 4K output, the lowest price per second, or frame-exact reproducibility.

### What can Seedance 2.5 do?

Seedance 2.5 generates video from a text prompt, from images that fix the first or last frame, or from reference assets that carry a subject, a style, or existing footage into a new clip. As of September 3, 2026, it produces clips of 4 to 30 seconds at 480p or 720p, across six aspect ratios, with audio by default and a seed parameter to narrow variance between runs. The [model page](https://openrouter.ai/bytedance/seedance-2.5) also lists video editing and video extension, and up to 50 reference assets per request.

### How much does Seedance 2.5 cost per video?

Seedance 2.5 bills per video token, and tokens are (width x height x fps x duration) / 1024 at 24 fps, so the price scales with both pixels and seconds. The rate is $0.0000107 per token, which works out to about $0.103 per second at 480p and $0.231 at 720p, so a 10-second 720p clip costs roughly $2.31. Audio is included at the same rate. A request that carries a video reference bills at $0.0000064 per token instead, about 40% less.

### Which AI video model is best?

There’s no single best video model, and the right answer depends on which requirement you hit first. Seedance 2.5 is the pick for 30-second clips that need last-frame control or video and audio references. Seedance 2.0 is the pick for 1080p and 4K. Wan 3.0 also runs to 30 seconds, costs less per second, and reaches 1080p, but it lists first-frame control only. Veo 3.1 is the pick for fixed 4, 6, or 8-second clips at 4K. All of them run through the same asynchronous video endpoint, so you can compare them on your own prompt by changing one field. The [video model collection](https://openrouter.ai/collections/video-models) lists the full set.

### How do I access the Seedance 2.5 API?

Send a POST request to `https://openrouter.ai/api/v1/videos` with `bytedance/seedance-2.5` in the model field and your prompt in `prompt`, then poll the `polling_url` from the response until the status is `completed` and download the result with your API key. Generation is asynchronous and usually takes from 30 seconds to a few minutes. The full request schema, including [webhooks](https://openrouter.ai/docs/cookbook/video-generation/video-generation-webhooks), is on the [video generation page](https://openrouter.ai/docs/guides/overview/multimodal/video-generation).

### Does Seedance 2.5 do audio?

Yes. Seedance 2.5 generates audio in the same pass as the video, and `generate_audio` defaults to true. We bill the same per-token rate with audio on or off, so there’s no cost reason to disable it. That isn’t true of Veo 3.1 or Seedance 1.5 Pro, which both charge less for silent output. The model page also lists multilingual audiovisual generation, so it’s worth testing a line in your own target language.

### What’s the difference between Seedance 2.5 and Seedance 2.0?

Seedance 2.5 runs twice as long and stops at a lower resolution. It generates 4 to 30 second clips at 480p or 720p, accepts image, video, and audio references, and bills $0.0000107 per video token. [Seedance 2.0](https://openrouter.ai/bytedance/seedance-2.0) generates 4 to 15 second clips at 480p through 4K and bills $0.000007 per token at 480p and 720p, so it’s cheaper per second and the only one of the two that reaches 1080p or 4K. Pick 2.5 for length and for editing existing footage, and 2.0 for resolution.

## References

- [ByteDance: Seedance 2.5 model page](https://openrouter.ai/bytedance/seedance-2.5). Entry price, release date, per-second rates, reference asset count, and capability description.
- [Video models endpoint (/api/v1/videos/models)](https://openrouter.ai/api/v1/videos/models). Supported durations, resolutions, aspect ratios, output sizes, frame image types, seed support, passthrough keys, and pricing SKUs for every video model cited here.
- [Video generation documentation](https://openrouter.ai/docs/guides/overview/multimodal/video-generation). Request schema, asynchronous job lifecycle, provider passthrough, webhooks, and the Zero Data Retention exclusion.
- [Announcing Video Generation](https://openrouter.ai/blog/announcements/video-generation/). Launch scope for the video endpoint and the models supported on day one.
- [Video model collection](https://openrouter.ai/collections/video-models). The catalog filtered to video output, used for the comparison set.
- [Video benchmarks](https://openrouter.ai/benchmarks/media/videos). Side-by-side outputs from every video model on a shared prompt, with cost and generation time per model.
- [ByteDance: Seedance 2.0 model page](https://openrouter.ai/bytedance/seedance-2.0). Resolution range, clip ceiling, and per-token rates for the higher-resolution model in the family.
- [Alibaba: Wan 3.0 model page](https://openrouter.ai/alibaba/wan-3.0). Clip ceiling, resolutions, frame control, and per-second pricing for one of the other two 30-second models.
- [Google: Veo 3.1 model page](https://openrouter.ai/google/veo-3.1). Fixed clip lengths and per-second pricing with and without audio.

All product sources above were last checked on September 3, 2026. Creator coverage is cited as framing only, not as a source of specs or prices.
