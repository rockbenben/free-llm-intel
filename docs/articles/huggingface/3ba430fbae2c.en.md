---
vendor: huggingface
title: Building an AI WebTV
original_title: Building an AI WebTV
url: https://huggingface.co/blog/ai-webtv
date: 2022-03-02
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 9f3da2d5c76f
---

Back to Articles

# Building an AI WebTV

Published
					July 17, 2023

Update on GitHub

Upvote

2

- [![](https://huggingface.co/avatars/0d04d6b1d64b08eadbbd8ed7d7e16505.svg)](https://huggingface.co/pxlpshr)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/XOz5jE5ru4Ifusaihcabl.jpeg)](https://huggingface.co/JMArts)

ARCHIVED ACCOUNT

jbilcke-hf

The AI WebTV is an experimental demo to showcase the latest advancements in automatic video and music synthesis.

👉 Watch the stream now by going to the [AI WebTV Space](https://huggingface.co/spaces/jbilcke-hf/AI-WebTV).

If you are using a mobile device, you can view the stream from the [Twitch mirror](https://www.twitch.tv/ai_webtv).

[![thumbnail.gif](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/156_ai_webtv/thumbnail.gif)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/156_ai_webtv/thumbnail.gif)

## Concept

The motivation for the AI WebTV is to demo videos generated with open-source [text-to-video models](https://huggingface.co/tasks/text-to-video) such as Zeroscope and MusicGen, in an entertaining and accessible way.

You can find those open-source models on the Hugging Face hub:

- For video: [zeroscope_v2_576](https://huggingface.co/cerspense/zeroscope_v2_576w) and [zeroscope_v2_XL](https://huggingface.co/cerspense/zeroscope_v2_XL)
- For music: [musicgen-melody](https://huggingface.co/facebook/musicgen-melody)

The individual video sequences are purposely made to be short, meaning the WebTV should be seen as a tech demo/showreel rather than an actual show (with an art direction or programming).

## Architecture

The AI WebTV works by taking a sequence of [video shot](https://en.wikipedia.org/wiki/Shot_(filmmaking)) prompts and passing them to a [text-to-video model](https://huggingface.co/tasks/text-to-video) to generate a sequence of [takes](https://en.wikipedia.org/wiki/Take).

Additionally, a base theme and idea (written by a human) are passed through a LLM (in this case, ChatGPT), in order to generate a variety of individual prompts for each video clip.

Here's a diagram of the current architecture of the AI WebTV:

[![diagram.jpg](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/156_ai_webtv/diagram.jpg)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/156_ai_webtv/diagram.jpg)

## Implementing the pipeline

The WebTV is implemented in NodeJS and TypeScript, and uses various services hosted on Hugging Face.

### The text-to-video model

The central video model is Zeroscope V2, a model based on [ModelScope](https://huggingface.co/damo-vilab/modelscope-damo-text-to-video-synthesis).

Zeroscope is comprised of two parts that can be chained together:

- A first pass with [zeroscope_v2_576](https://huggingface.co/cerspense/zeroscope_v2_576w), to generate a 576x320 video clip
- An optional second pass with [zeroscope_v2_XL](https://huggingface.co/cerspense/zeroscope_v2_XL) to upscale the video to 1024x576

👉 You will need to use the same prompt for both the generation and upscaling.

### Calling the video chain

To make a quick prototype, the WebTV runs Zeroscope from two duplicated Hugging Face Spaces running [Gradio](https://github.com/gradio-app/gradio/), which are called using the [@gradio/client](https://www.npmjs.com/package/@gradio/client) NPM package. You can find the original spaces here:

- [zeroscope-v2](https://huggingface.co/spaces/hysts/zeroscope-v2/tree/main) by @hysts
- [Zeroscope XL](https://huggingface.co/spaces/fffiloni/zeroscope-XL) by @fffiloni

Other spaces deployed by the community can also be found if you [search for Zeroscope on the Hub](https://huggingface.co/spaces?search=zeroscope).

👉 Public Spaces may become overcrowded and paused at any time. If you intend to deploy your own system, please duplicate those Spaces and run them under your own account.

### Using a model hosted on a Space

Spaces using Gradio have the ability to [expose a REST API](https://www.gradio.app/guides/sharing-your-app#api-page), which can then be called from Node using the [@gradio/client](https://www.npmjs.com/package/@gradio/client) module.

Here is an example:

```
import { client } from "@gradio/client"

export const generateVideo = async (prompt: string) => {
  const api = await client("*** URL OF THE SPACE ***")

  // call the "run()" function with an array of parameters
  const { data } = await api.predict("/run", [		
    prompt,
    42,	// seed	
    24, // nbFrames
    35 // nbSteps
  ])
  
  const { orig_name } = data[0][0]

  const remoteUrl = `${instance}/file=${orig_name}`

  // the file can then be downloaded and stored locally
}
```

### Post-processing

Once an individual take (a video clip) is upscaled, it is then passed to FILM (Frame Interpolation for Large Motion), a frame interpolation algorithm:

- Original links: [website](https://film-net.github.io/), [source code](https://github.com/google-research/frame-interpolation)
- Model on Hugging Face: [/frame-interpolation-film-style](https://huggingface.co/akhaliq/frame-interpolation-film-style)
- A Hugging Face Space you can duplicate: [video_frame_interpolation](https://huggingface.co/spaces/fffiloni/video_frame_interpolation/blob/main/app.py) by @fffiloni

During post-processing, we also add music generated with MusicGen:

- Original links: [website](https://ai.honu.io/papers/musicgen/), [source code](https://github.com/facebookresearch/audiocraft)
- Hugging Face Space you can duplicate: [MusicGen](https://huggingface.co/spaces/facebook/MusicGen)

### Broadcasting the stream

Note: there are multiple tools you can use to create a video stream. The AI WebTV currently uses [FFmpeg](https://ffmpeg.org/documentation.html) to read a playlist made of mp4 videos files and m4a audio files.

Here is an example of creating such a playlist:

```
import { promises as fs } from "fs"
import path from "path"

const allFiles = await fs.readdir("** PATH TO VIDEO FOLDER **")
const allVideos = allFiles
  .map(file => path.join(dir, file))
  .filter(filePath => filePath.endsWith('.mp4'))

let playlist = 'ffconcat version 1.0\n'
allFilePaths.forEach(filePath => {
  playlist += `file '${filePath}'\n`
})
await fs.promises.writeFile("playlist.txt", playlist)
```

This will generate the following playlist content:

```
ffconcat version 1.0
file 'video1.mp4'
file 'video2.mp4'
...
```

FFmpeg is then used again to read this playlist and send a [FLV stream](https://en.wikipedia.org/wiki/Flash_Video) to a [RTMP server](https://en.wikipedia.org/wiki/Real-Time_Messaging_Protocol). FLV is an old format but still popular in the world of real-time streaming due to its low latency.

```
ffmpeg -y -nostdin \
  -re \
  -f concat \
  -safe 0 -i channel_random.txt -stream_loop -1 \
  -loglevel error \
  -c:v libx264 -preset veryfast -tune zerolatency \
  -shortest \
  -f flv rtmp://<SERVER>
```

There are many different configuration options for FFmpeg, for more information in the [official documentation](http://trac.ffmpeg.org/wiki/StreamingGuide).

For the RTMP server, you can find [open-source implementations on GitHub](https://github.com/topics/rtmp-server), such as the [NGINX-RTMP module](https://github.com/arut/nginx-rtmp-module).

The AI WebTV itself uses [node-media-server](https://github.com/illuspas/Node-Media-Server).

💡 You can also directly stream to [one of the Twitch RTMP entrypoints](https://help.twitch.tv/s/twitch-ingest-recommendation?language=en_US). Check out the Twitch documentation for more details.

## Observations and examples

Here are some examples of the generated content.

The first thing we notice is that applying the second pass of Zeroscope XL significantly improves the quality of the image. The impact of frame interpolation is also clearly visible.

### Characters and scene composition

Prompt:

Photorealistic movie of a

llama acting as a programmer, wearing glasses and a hoodie

, intensely

staring at a screen

with lines of code, in a cozy,

dimly lit room

, Canon EOS, ambient lighting, high details, cinematic, trending on artstation

Prompt:

3D rendered animation showing a group of food characters

forming a pyramid

, with a

banana

standing triumphantly on top. In a city with

cotton candy clouds

and

chocolate road

, Pixar's style, CGI, ambient lighting, direct sunlight, rich color scheme, ultra realistic, cinematic, photorealistic.

Prompt:

Intimate

close-up of a red fox, gazing into the camera with sharp eyes

, ambient lighting creating a high contrast silhouette, IMAX camera,

high detail

,

cinematic effect

, golden hour, film grain.

### Simulation of dynamic scenes

Something truly fascinating about text-to-video models is their ability to emulate real-life phenomena they have been trained on.

We've seen it with large language models and their ability to synthesize convincing content that mimics human responses, but this takes things to a whole new dimension when applied to video.

A video model predicts the next frames of a scene, which might include objects in motion such as fluids, people, animals, or vehicles. Today, this emulation isn't perfect, but it will be interesting to evaluate future models (trained on larger or specialized datasets, such as animal locomotion) for their accuracy when reproducing physical phenomena, and also their ability to simulate the behavior of agents.

Prompt:

Cinematic movie shot of

bees energetically buzzing around a flower

, sun rays illuminating the scene, captured in 4k IMAX with a soft bokeh background.

Prompt:

Dynamic footage of a grizzly bear catching a salmon in a rushing river

, ambient lighting highlighting the splashing water, low angle, IMAX camera, 4K movie quality, golden hour, film grain.

Prompt:

Aerial footage of a quiet morning at the coast of California, with

waves gently crashing against the rocky shore

. A startling sunrise illuminates the coast with vibrant colors, captured beautifully with a DJI Phantom 4 Pro. Colors and textures of the landscape come alive under the soft morning light. Film grain, cinematic, imax, movie

💡 It will be interesting to see these capabilities explored more in the future, for instance by training video models on larger video datasets covering more phenomena.

### Styling and effects

Prompt:

3D rendered video

of a friendly broccoli character wearing a hat, walking in a candy-filled city street with gingerbread houses, under a

bright sun and blue skies

,

Pixar's style

, cinematic, photorealistic, movie,

ambient lighting

, natural lighting,

CGI

, wide-angle view, daytime, ultra realistic.

Prompt:

Cinematic movie

, shot of an astronaut and a llama at dawn, the mountain landscape bathed in

soft muted colors

, early morning fog, dew glistening on fur, craggy peaks, vintage NASA suit, Canon EOS, high detailed skin, epic composition, high quality, 4K, trending on artstation, beautiful

Prompt:

Panda and black cat

navigating down the flowing river

in a small boat, Studio Ghibli style > Cinematic, beautiful composition > IMAX

camera panning following the boat

> High quality, cinematic, movie, mist effect, film grain, trending on Artstation

### Failure cases

**Wrong direction:** the model sometimes has trouble with movement and direction. For instance, here the clip seems to be played in reverse. Also the modifier keyword ***green*** was not taken into account.

Prompt:

Movie showing a

green pumpkin

falling into a bed of nails, slow-mo explosion with chunks flying all over, ambient fog adding to the dramatic lighting, filmed with IMAX camera, 8k ultra high definition, high quality, trending on artstation.

**Rendering errors on realistic scenes:** sometimes we can see artifacts such as moving vertical lines or waves. It is unclear what causes this, but it may be due to the combination of keywords used.

Prompt:

Film shot of a captivating flight above the Grand Canyon, ledges and plateaus etched in orange and red.

Deep shadows contrast

with the fiery landscape under the midday sun, shot with DJI Phantom 4 Pro. The camera rotates to capture the vastness,

textures

and colors, in imax quality. Film

grain

, cinematic, movie.

**Text or objects inserted into the image:** the model sometimes injects words from the prompt into the scene, such as "IMAX". Mentioning "Canon EOS" or "Drone footage" in the prompt can also make those objects appear in the video.

In the following example, we notice the word "llama" inserts a llama but also two occurrences of the word llama in flames.

Prompt:

Movie scene of a

llama

acting as a firefighter, in firefighter uniform, dramatically spraying water at

roaring flames

, amidst a chaotic urban scene, Canon EOS, ambient lighting, high quality, award winning, highly detailed fur, cinematic, trending on artstation.

## Recommendations

Here are some early recommendations that can be made from the previous observations:

### Using video-specific prompt keywords

You may already know that if you don’t prompt a specific aspect of the image with Stable Diffusion, things like the color of clothes or the time of the day might become random, or be assigned a generic value such as a neutral mid-day light.

The same is true for video models: you will want to be specific about things. Examples include camera and character movement, their orientation, speed and direction. You can leave it unspecified for creative purposes (idea generation), but this might not always give you the results you want (e.g., entities animated in reverse).

### Maintaining consistency between scenes

If you plan to create sequences of multiple videos, you will want to make sure you add as many details as possible in each prompt, otherwise you may lose important details from one sequence to another, such as the color.

💡 This will also improve the quality of the image since the prompt is used for the upscaling part with Zeroscope XL.

### Leverage frame interpolation

Frame interpolation is a powerful tool which can repair small rendering errors and turn many defects into features, especially in scenes with a lot of animation, or where a cartoon effect is acceptable. The [FILM algorithm](https://film-net.github.io/) will smoothen out elements of a frame with previous and following events in the video clip.

This works great to displace the background when the camera is panning or rotating, and will also give you creative freedom, such as control over the number of frames after the generation, to make slow-motion effects.

## Future work

We hope you enjoyed watching the AI WebTV stream and that it will inspire you to build more in this space.

As this was a first trial, a lot of things were not the focus of the tech demo: generating longer and more varied sequences, adding audio (sound effects, dialogue), generating and orchestrating complex scenarios, or letting a language model agent have more control over the pipeline.

Some of these ideas may make their way into future updates to the AI WebTV, but we also can’t wait to see what the community of researchers, engineers and builders will come up with!

## Models mentioned in this article 4

## Spaces mentioned in this article 5

More Articles from our Blog

open-source

diffusers

generative

## Introducing Modular Diffusers - Composable Building Blocks for Diffusion Pipelines

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1677857909367-624ef9ba9d608e459387b34e.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/63df091910678851bb0cd0e0/FUXFt0C-rUFSppIAu5ZDN.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1630334896986-6126e46848005fa9ca5c578c.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1649681653581-5f7fbd813e94f16a85448745.jpeg)

55

March 5, 2026

ethics

text-generation

guide

## Visible Watermarking with Gradio

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1626214544196-60c757ea5f9a76ab3f844f12.png)

21

September 15, 2025

### Community

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fai-webtv) or [log in](https://huggingface.co/login?next=%2Fblog%2Fai-webtv) to comment

Upvote

2

- [![](https://huggingface.co/avatars/0d04d6b1d64b08eadbbd8ed7d7e16505.svg)](https://huggingface.co/pxlpshr)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/XOz5jE5ru4Ifusaihcabl.jpeg)](https://huggingface.co/JMArts)

## Models mentioned in this article 4

## Spaces mentioned in this article 5
