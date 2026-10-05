---
vendor: together_ai
title: 部署并推理 HuggingFace 上的任何模型
original_title: "Deploy and inference any model from HuggingFace"
url: https://www.together.ai/blog/deploy-and-inference-any-model-from-huggingface
date: 2026-05-08
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# 部署并推理 HuggingFace 上的任何模型

Agents、Skills 加 Together Dedicated Container Inference，让"试任何模型"成为可能。

开发者工作方式中正发生一些真实的变化。Agents 打开了过去我们多数人无从下手的工作——不是技术上做不到，而是需要我们没有的小众专业知识。容器化、推理服务器配置、模型专属环境搭建：这类任务过去要么需要深厚专门知识，要么得先花几小时自学才能上路。Agents 提供了一种优雅的方式弥合这些先验知识缺口。你描述想要什么，agent 补上知识空白。

这就是解锁点。不是速度，是*可达性*。

## Netflix 发布新模型的那天

Netflix 最近在 Hugging Face 上发布了 [void-model](https://huggingface.co/netflix/void-model)。发布当天，我的本能和往常一样：我想试试。但"想试一个新模型"和"真的把它跑起来"是两回事。把它弄进一个可用环境、搞定推理服务器配置、弄明白容器设置、把所有东西正确接起来——这一段通常会在"这东西看起来很棒"和"好，我真的在用"之间插入一两天的延迟。

这一次，这个延迟基本为零。

用 [Goose](https://goose-docs.ai/)（一个 CLI agent 运行器）配合 Together 的 [dedicated containers skill](https://github.com/togethercomputer/skills/tree/main/skills/together-dedicated-containers)，我在一次会话里就从"Netflix 刚发了个模型"走到"我有了它的运行中容器"。Agent 产出了把 void-model 部署到 Together Dedicated Container Inference（DCI）基础设施所需的全部代码——基本上就在发布当天。

产出在这里：[github.com/blainekasten/together-void-model-container](https://github.com/blainekasten/together-void-model-container)

## 我具体做了什么

整个设置只有三步。

**第 1 步：安装 Together dedicated containers skill。**

`npx skills add togethercomputer/skills`

这会拉入 [together-dedicated-containers skill](https://github.com/togethercomputer/skills/tree/main/skills/together-dedicated-containers)，它赋予 Goose 使用 Together 基础设施所需的具体知识：如何配置推理服务器、容器规格应该长什么样、给定模型如何把所有东西接起来。

**第 2 步：启动一个 Goose 会话，跑一条 prompt。**

`I want to deploy this model on togethers dedicated containers https://huggingface.co/netflix/void-model`

就这些。一句话。

**第 3 步：坐着看它干活。**

之后，agent 从 Hugging Face 拉取模型详情、为模型架构确定正确的推理服务器配置、生成容器配置文件，产出一个完整可运行的设置——全程不需要我查任何东西，也不需要我逐步指导。

结果就是：[blainekasten/together-void-model-container](https://github.com/blainekasten/together-void-model-container)，一个干净、可用的 repo，任何人都能拿它在 Together 基础设施上跑 void-model。

**第 4 步：用你的模型！**

Agent 部署好你的应用后，你就可以开始对它跑推理。[Together CLI](http://docs.together.ai/reference/cli) 有便捷命令来测试推理。

```
    
tg beta jig submit --watch --payload '{
    "video_url": "https://github.com/Netflix/void-model/raw/refs/heads/main/sample/lime/input_video.mp4",
    "quadmask_url": "https://github.com/Netflix/void-model/raw/refs/heads/main/sample/lime/quadmask_0.mp4",
    "prompt": "Empty park bench with fallen leaves on the ground",
    "use_pass2": false
  }'

    
```

这个模型能把物体从视频中移除，连同它们对场景造成的一切交互——不只是阴影、反射这类次级效应，还包括物体移除后人倒下这类物理交互。

我们这个模型的推理调用是异步的。因此这个请求的响应会返回一个可供轮询的标识符。响应长这样：

```
    
{
  "model": "void-byoc",
  "request_id": "019dc0f3-3c73-7a3f-b4b6-87ad06091180",
  "status": "running",
  "claimed_at": "2026-04-24T19:24:19.447457Z",
  "created_at": "2026-04-24T19:24:19.444567Z",
  "done_at": null,
  "info": null,
  "inputs": {
    "prompt": "Empty park bench with fallen leaves on the ground",
    "quadmask_url": "https://github.com/Netflix/void-model/raw/refs/heads/main/sample/lime/quadmask_0.mp4",
    "use_pass2": false,
    "video_url": "https://github.com/Netflix/void-model/raw/refs/heads/main/sample/lime/input_video.mp4"
  },
  "outputs": null,
  "priority": 1,
  "retries": null,
  "warnings": null
}

    
```

推理完成后，outputs 会包含一个托管视频的 URL。我们可以用 cURL 加上 Together API key 下载它：

```
    
curl -L -O \
  https://api.together.ai/v1/storage/019dc0f3-3c73-7a3f-b4b6-87ad06091180-tmpddmhtvar.mp4 \
  --header "Authorization: Bearer $TOGETHER_API_KEY"

    
```

注意：-L 用于跟随 storage URL 中的 http 重定向，-O 会把输出写入本地文件。

## 为什么选 Together Dedicated Container Inference

这个故事之所以成立，是因为 Together 的 Dedicated Container Inference（DCI）确实是运行这类模型的好地方，值得说明原因。

DCI 给你一个私有的、GPU 支撑的环境，运行你选择的模型，完全由 Together 托管。你不用争抢共享资源，不用配置自己的集群，也不会被锁死在一份固定模型菜单里。你带模型，Together 管基础设施。

对想快速行动的团队，这是大事。当 Netflix、某个研究实验室或开源社区发布新模型时，你可以几乎立刻让它在生产级环境中跑起来。不用自己开 GPU 虚拟机，不用和推理服务器依赖搏斗，不用等谁在托管 endpoint 里加上对它的支持。DCI 生来灵活：模型存在，你就能部署。

成本模型也让实验很轻松。你按用量付费，容器属于你，还没有管理底层算力的开销。这样的设置让你能对"测试新模型"说不犹豫，而不是把它归档到"等我有空"。

如果你想了解 Together 的 DCI，[联系我们](https://www.together.ai/contact-sales?dci=true)开通。
