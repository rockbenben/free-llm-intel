---
vendor: huggingface
title: 搭建一个 AI 网络电视台
original_title: Building an AI WebTV
url: https://huggingface.co/blog/ai-webtv
date: 2022-03-02
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# 搭建一个 AI 网络电视台

AI WebTV 是一个实验性演示，用于展示视频与音乐自动合成领域的最新进展。

👉 前往 [AI WebTV Space](https://huggingface.co/spaces/jbilcke-hf/AI-WebTV) 即可观看直播。

如果你使用移动设备，也可以通过 [Twitch 镜像](https://www.twitch.tv/ai_webtv)观看直播流。

[![thumbnail.gif](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/156_ai_webtv/thumbnail.gif)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/156_ai_webtv/thumbnail.gif)

## 概念

AI WebTV 的动机是以一种有趣且易于接近的方式，演示用开源[文生视频模型](https://huggingface.co/tasks/text-to-video)（如 Zeroscope 和 MusicGen）生成的视频。

你可以在 Hugging Face hub 上找到这些开源模型：

- 视频：[zeroscope_v2_576](https://huggingface.co/cerspense/zeroscope_v2_576w) 和 [zeroscope_v2_XL](https://huggingface.co/cerspense/zeroscope_v2_XL)
- 音乐：[musicgen-melody](https://huggingface.co/facebook/musicgen-melody)

单个视频片段刻意做得很短，也就是说，这个 WebTV 应被视为一个技术演示/作品秀（showreel），而不是一档真正的节目（有艺术指导或节目编排）。

## 架构

AI WebTV 的工作方式是：取一串[镜头（video shot）](https://en.wikipedia.org/wiki/Shot_(filmmaking)) prompt，把它们交给[文生视频模型](https://huggingface.co/tasks/text-to-video)，生成一串[条（takes）](https://en.wikipedia.org/wiki/Take)。

此外，一个基础主题和创意（由人撰写）会先经过一个 LLM（这里是 ChatGPT），为每个视频片段生成多样化的独立 prompt。

下面是 AI WebTV 当前架构图：

[![diagram.jpg](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/156_ai_webtv/diagram.jpg)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/156_ai_webtv/diagram.jpg)

## 实现流水线

WebTV 用 NodeJS 和 TypeScript 实现，并使用了托管在 Hugging Face 上的多个服务。

### 文生视频模型

核心视频模型是 Zeroscope V2，它基于 [ModelScope](https://huggingface.co/damo-vilab/modelscope-damo-text-to-video-synthesis)。

Zeroscope 由两个可以串联起来的部分组成：

- 第一遍用 [zeroscope_v2_576](https://huggingface.co/cerspense/zeroscope_v2_576w)，生成 576x320 的视频片段
- 可选的第二遍用 [zeroscope_v2_XL](https://huggingface.co/cerspense/zeroscope_v2_XL)，把视频放大到 1024x576

👉 生成和放大两遍必须使用同一个 prompt。

### 调用视频链

为了快速做原型，WebTV 从两个复制出来的、运行 [Gradio](https://github.com/gradio-app/gradio/) 的 Hugging Face Spaces 上运行 Zeroscope，通过 [@gradio/client](https://www.npmjs.com/package/@gradio/client) NPM 包调用它们。原始 Space 在这里：

- @hysts 的 [zeroscope-v2](https://huggingface.co/spaces/hysts/zeroscope-v2/tree/main)
- @fffiloni 的 [Zeroscope XL](https://huggingface.co/spaces/fffiloni/zeroscope-XL)

如果你[在 Hub 上搜索 Zeroscope](https://huggingface.co/spaces?search=zeroscope)，还能找到社区部署的其他 Space。

👉 公共 Space 随时可能人满或被暂停。如果你打算部署自己的系统，请复制这些 Space，在你自己的账户下运行。

### 使用托管在 Space 上的模型

使用 Gradio 的 Space 可以[暴露 REST API](https://www.gradio.app/guides/sharing-your-app#api-page)，随后就能在 Node 中通过 [@gradio/client](https://www.npmjs.com/package/@gradio/client) 模块调用。

示例如下：

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

### 后处理

单条 take（视频片段）放大之后，会被交给 FILM（Frame Interpolation for Large Motion，大运动帧插值）——一种帧插值算法：

- 原始链接：[网站](https://film-net.github.io/)、[源码](https://github.com/google-research/frame-interpolation)
- Hugging Face 上的模型：[/frame-interpolation-film-style](https://huggingface.co/akhaliq/frame-interpolation-film-style)
- 你可以复制的 Hugging Face Space：@fffiloni 的 [video_frame_interpolation](https://huggingface.co/spaces/fffiloni/video_frame_interpolation/blob/main/app.py)

在后处理阶段，我们还会叠加用 MusicGen 生成的音乐：

- 原始链接：[网站](https://ai.honu.io/papers/musicgen/)、[源码](https://github.com/facebookresearch/audiocraft)
- 你可以复制的 Hugging Face Space：[MusicGen](https://huggingface.co/spaces/facebook/MusicGen)

### 广播直播流

注意：创建视频流可以使用多种工具。AI WebTV 目前用 [FFmpeg](https://ffmpeg.org/documentation.html) 读取一个由 mp4 视频文件和 m4a 音频文件组成的播放列表。

下面是创建这类播放列表的示例：

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

这会生成如下播放列表内容：

```
ffconcat version 1.0
file 'video1.mp4'
file 'video2.mp4'
...
```

然后再次使用 FFmpeg 读取该播放列表，把 [FLV 流](https://en.wikipedia.org/wiki/Flash_Video)发送到 [RTMP 服务器](https://en.wikipedia.org/wiki/Real-Time_Messaging_Protocol)。FLV 是一种老格式，但因为低延迟，在实时流媒体世界里依然流行。

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

FFmpeg 有大量不同的配置选项，更多信息见[官方文档](http://trac.ffmpeg.org/wiki/StreamingGuide)。

至于 RTMP 服务器，你可以在 [GitHub 上找到开源实现](https://github.com/topics/rtmp-server)，例如 [NGINX-RTMP 模块](https://github.com/arut/nginx-rtmp-module)。

AI WebTV 本身使用的是 [node-media-server](https://github.com/illuspas/Node-Media-Server)。

💡 你也可以直接流式推送到 [Twitch 的某个 RTMP 入口](https://help.twitch.tv/s/twitch-ingest-recommendation?language=en_US)。详情见 Twitch 文档。

## 观察与示例

以下是一些生成内容的示例。

我们注意到的第一点是：应用 Zeroscope XL 的第二遍显著改善了图像质量。帧插值的影响也清晰可见。

### 角色与场景构图

Prompt：

```
Photorealistic movie of a llama acting as a programmer, wearing glasses and a hoodie, intensely staring at a screen with lines of code, in a cozy, dimly lit room, Canon EOS, ambient lighting, high details, cinematic, trending on artstation
```

Prompt：

```
3D rendered animation showing a group of food characters forming a pyramid, with a banana standing triumphantly on top. In a city with cotton candy clouds and chocolate road, Pixar's style, CGI, ambient lighting, direct sunlight, rich color scheme, ultra realistic, cinematic, photorealistic.
```

Prompt：

```
Intimate close-up of a red fox, gazing into the camera with sharp eyes, ambient lighting creating a high contrast silhouette, IMAX camera, high detail, cinematic effect, golden hour, film grain.
```

### 动态场景的模拟

文生视频模型真正迷人的地方在于，它们能够仿照自己训练时见过的现实世界现象。

我们在大语言模型身上已经见过这一点——它们能合成以假乱真、模仿人类回答的内容——但把这件事应用到视频上，是把它带入了一个全新的维度。

视频模型预测场景的后续帧，其中可能包含运动中的物体：流体、人、动物或车辆。今天这种仿照还不完美，但评估未来模型（在更大或更专门的数据集上训练，例如动物运动数据集）复现物理现象的精度，以及模拟智能体行为的能力，会是一件很有意思的事。

Prompt：

```
Cinematic movie shot of bees energetically buzzing around a flower, sun rays illuminating the scene, captured in 4k IMAX with a soft bokeh background.
```

Prompt：

```
Dynamic footage of a grizzly bear catching a salmon in a rushing river, ambient lighting highlighting the splashing water, low angle, IMAX camera, 4K movie quality, golden hour, film grain.
```

Prompt：

```
Aerial footage of a quiet morning at the coast of California, with waves gently crashing against the rocky shore. A startling sunrise illuminates the coast with vibrant colors, captured beautifully with a DJI Phantom 4 Pro. Colors and textures of the landscape come alive under the soft morning light. Film grain, cinematic, imax, movie
```

💡 未来这些能力值得更深入的探索，例如用覆盖更多现象的更大规模视频数据集来训练视频模型。

### 风格与特效

Prompt：

```
3D rendered video of a friendly broccoli character wearing a hat, walking in a candy-filled city street with gingerbread houses, under a bright sun and blue skies, Pixar's style, cinematic, photorealistic, movie, ambient lighting, natural lighting, CGI, wide-angle view, daytime, ultra realistic.
```

Prompt：

```
Cinematic movie, shot of an astronaut and a llama at dawn, the mountain landscape bathed in soft muted colors, early morning fog, dew glistening on fur, craggy peaks, vintage NASA suit, Canon EOS, high detailed skin, epic composition, high quality, 4K, trending on artstation, beautiful
```

Prompt：

```
Panda and black cat navigating down the flowing river in a small boat, Studio Ghibli style > Cinematic, beautiful composition > IMAX camera panning following the boat > High quality, cinematic, movie, mist effect, film grain, trending on Artstation
```

### 失败案例

**方向错误**：模型有时在运动和方向上会出问题。例如下面这段看起来像是倒放。此外修饰关键词 ***green*** 也没有被采纳。

Prompt：

```
Movie showing a green pumpkin falling into a bed of nails, slow-mo explosion with chunks flying all over, ambient fog adding to the dramatic lighting, filmed with IMAX camera, 8k ultra high definition, high quality, trending on artstation.
```

**写实场景上的渲染错误**：有时会出现移动竖线或波纹之类的伪影。成因尚不明确，可能与所用关键词的组合有关。

Prompt：

```
Film shot of a captivating flight above the Grand Canyon, ledges and plateaus etched in orange and red. Deep shadows contrast with the fiery landscape under the midday sun, shot with DJI Phantom 4 Pro. The camera rotates to capture the vastness, textures and colors, in imax quality. Film grain, cinematic, movie.
```

**文字或物体被插入画面**：模型有时会把 prompt 中的词注入场景，比如 "IMAX"。在 prompt 中提到 "Canon EOS" 或 "Drone footage" 也可能让这些物体出现在视频里。

在下一个例子中，我们发现 "llama" 一词不仅插入了一只羊驼，还插入了两处燃烧着的 llama 单词。

Prompt：

```
Movie scene of a llama acting as a firefighter, in firefighter uniform, dramatically spraying water at roaring flames, amidst a chaotic urban scene, Canon EOS, ambient lighting, high quality, award winning, highly detailed fur, cinematic, trending on artstation.
```

## 建议

基于以上观察，可以给出一些初步建议：

### 使用视频专属的 prompt 关键词

你可能已经知道，如果用 Stable Diffusion 时不对图像的特定方面做 prompt，衣服的颜⾊或一天中的时间之类就可能变成随机值，或被赋一个中性正午光线这样的通用值。

视频模型也是如此：你需要对各种细节做出明确说明。例如摄像机和角色的运动、它们的朝向、速度和方向。你可以出于创作目的（点子生成）不写这些，但这不一定总能得到你想要的结果（例如实体被倒着动画）。

### 保持场景之间的一致性

如果你打算创建多个视频组成的序列，每个 prompt 都要尽可能加入更多细节，否则一个片段到下一个片段可能会丢失重要细节，比如颜色。

💡 这同时也会提高图像质量，因为 Zeroscope XL 的放大环节也要用到同一个 prompt。

### 善用帧插值

帧插值是一个强大的工具，可以修复小的渲染错误，并把许多缺陷变成特性，尤其在动画量大或可以接受卡通效果的场景中。[FILM 算法](https://film-net.github.io/)会把一帧的元素与片段中前一帧和后一帧的事件平滑衔接。

这对摄像机平移或旋转时移动背景非常有效，还能给你创作自由，例如在生成完成后控制帧数，做慢动作效果。

## 未来工作

希望你喜欢观看 AI WebTV 的直播，并受此启发在这个领域做出更多东西。

由于这是第一次尝试，很多并不是这个技术演示的重点：生成更长、更多样的序列，加入音频（音效、对白），生成并编排复杂剧本，或者让一个语言模型代理对流水线有更多控制权。

这些想法中的一些可能会进入 AI WebTV 的未来版本，但我们也迫不及待想看到研究者、工程师和建造者社区会玩出什么新花样！
