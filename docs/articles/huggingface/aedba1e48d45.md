---
vendor: huggingface
title: Transformers.js v3：WebGPU 支持、新模型与任务，以及更多…
original_title: Transformers.js v3: WebGPU Support, New Models & Tasks, and More…
url: https://huggingface.co/blog/transformersjs-v3
date: 2024-10-22
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: ee11d219cb31
---

# Transformers.js v3：WebGPU 支持、新模型与任务，以及更多…

经过一年多的开发，我们很高兴宣布 🤗 Transformers.js v3 发布！

亮点包括：

- [WebGPU 支持（比 WASM 最快可快 100 倍！）](https://huggingface.co/blog/transformersjs-v3#webgpu-support)
- [新量化格式（dtypes）](https://huggingface.co/blog/transformersjs-v3#new-quantization-formats-dtypes)
- [总共 120 种支持的架构](https://huggingface.co/blog/transformersjs-v3#120-supported-architectures)
- [25 个新示例项目和模板](https://huggingface.co/blog/transformersjs-v3#example-projects-and-templates)
- [Hugging Face Hub 上超过 1200 个预转换模型](https://huggingface.co/blog/transformersjs-v3#over-1200-pre-converted-models)
- [Node.js（ESM + CJS）、Deno 和 Bun 兼容](https://huggingface.co/blog/transformersjs-v3#nodejs-esm--cjs-deno-and-bun-compatibility)
- [在 GitHub 和 NPM 上的新家](https://huggingface.co/blog/transformersjs-v3#a-new-home-on-npm-and-github)

## 安装

从 [NPM](https://www.npmjs.com/package/@huggingface/transformers) 安装 Transformers.js v3 即可开始：

```
npm i @huggingface/transformers
```

然后引入库：

```
import { pipeline } from "@huggingface/transformers";
```

或者通过 CDN：

```
import { pipeline } from "https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.0.0";
```

更多信息请看[文档](https://hf.co/docs/transformers.js)。

## WebGPU 支持

WebGPU 是图形与计算的新一代 Web 标准。这个 [API](https://developer.mozilla.org/en-US/docs/Web/API/WebGPU_API) 让 Web 开发者直接使用底层系统的 GPU 在浏览器里完成高性能计算。WebGPU 是 [WebGL](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API) 的继任者，性能强得多，因为它允许与现代 GPU 更直接的交互。最后，它还支持通用 GPU 计算——用来做机器学习再合适不过！

> 截至 2024 年 10 月，WebGPU 全球支持率约 70%（据 caniuse.com），部分用户可能还用不了这个 API。
> 如果下面的 demo 在你的浏览器里跑不起来，可能需要用特性开关启用：
> Firefox：设置 dom.webgpu.enabled 标志（见这里）。
> Safari：开启 WebGPU feature flag（见这里）。
> 较旧的 Chromium 浏览器（Windows、macOS、Linux）：设置 enable-unsafe-webgpu 标志（见这里）。

### 在 Transformers.js v3 中使用

得益于我们与 [ONNX Runtime Web](https://www.npmjs.com/package/onnxruntime-web) 的合作，开启 WebGPU 加速只需要在加载模型时设置 `device: 'webgpu'`。看几个例子！

**示例：** 在 WebGPU 上计算文本嵌入（[demo](https://v2.scrimba.com/s06a2smeej)）

```
import { pipeline } from "@huggingface/transformers";

// Create a feature-extraction pipeline
const extractor = await pipeline(
  "feature-extraction",
  "mixedbread-ai/mxbai-embed-xsmall-v1",
  { device: "webgpu" },
);

// Compute embeddings
const texts = ["Hello world!", "This is an example sentence."];
const embeddings = await extractor(texts, { pooling: "mean", normalize: true });
console.log(embeddings.tolist());
// [
//   [-0.016986183822155, 0.03228696808218956, -0.0013630966423079371, ... ],
//   [0.09050482511520386, 0.07207386940717697, 0.05762749910354614, ... ],
// ]
```

**示例：** 在 WebGPU 上用 OpenAI Whisper 做自动语音识别（[demo](https://v2.scrimba.com/s0oi76h82g)）

```
import { pipeline } from "@huggingface/transformers";

// Create automatic speech recognition pipeline
const transcriber = await pipeline(
  "automatic-speech-recognition",
  "onnx-community/whisper-tiny.en",
  { device: "webgpu" },
);

// Transcribe audio from a URL
const url = "https://huggingface.co/datasets/Xenova/transformers.js-docs/resolve/main/jfk.wav";
const output = await transcriber(url);
console.log(output);
// { text: ' And so my fellow Americans ask not what your country can do for you, ask what you can do for your country.' }
```

**示例：** 在 WebGPU 上用 MobileNetV4 做图像分类（[demo](https://v2.scrimba.com/s0fv2uab1t)）

```
import { pipeline } from "@huggingface/transformers";

// Create image classification pipeline
const classifier = await pipeline(
  "image-classification",
  "onnx-community/mobilenetv4_conv_small.e2400_r224_in1k",
  { device: "webgpu" },
);

// Classify an image from a URL
const url = "https://huggingface.co/datasets/Xenova/transformers.js-docs/resolve/main/tiger.jpg";
const output = await classifier(url);
console.log(output);
// [
//   { label: 'tiger, Panthera tigris', score: 0.6149784922599792 },
//   { label: 'tiger cat', score: 0.30281734466552734 },
//   { label: 'tabby, tabby cat', score: 0.0019135422771796584 },
//   { label: 'lynx, catamount', score: 0.0012161266058683395 },
//   { label: 'Egyptian cat', score: 0.0011465961579233408 }
// ]
```

## 新量化格式（dtypes）

在 Transformers.js v3 之前，我们用 `quantized` 选项来选择量化（q8）或全精度（fp32）模型，分别设 `quantized` 为 `true` 或 `false`。现在我们通过 `dtype` 参数支持多得多的选择。

可用的量化选项取决于模型，常见的有：全精度（`"fp32"`）、半精度（`"fp16"`）、8-bit（`"q8"`、`"int8"`、`"uint8"`）和 4-bit（`"q4"`、`"bnb4"`、`"q4f16"`）。

![Available dtypes for mixedbread-ai/mxbai-embed-xsmall-v1](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/transformersjs-v3/dtypes-dark.jpg)  [（例如 mixedbread-ai/mxbai-embed-xsmall-v1）](https://huggingface.co/mixedbread-ai/mxbai-embed-xsmall-v1/tree/main/onnx)

### 基本用法

**示例：** 以 4-bit 量化运行 Qwen2.5-0.5B-Instruct（[demo](https://v2.scrimba.com/s0dlcpv0ci)）

```
import { pipeline } from "@huggingface/transformers";

// Create a text generation pipeline
const generator = await pipeline(
  "text-generation",
  "onnx-community/Qwen2.5-0.5B-Instruct",
  { dtype: "q4", device: "webgpu" },
);

// Define the list of messages
const messages = [
  { role: "system", content: "You are a helpful assistant." },
  { role: "user", content: "Tell me a funny joke." },
];

// Generate a response
const output = await generator(messages, { max_new_tokens: 128 });
console.log(output[0].generated_text.at(-1).content);
```

### 逐模块 dtype

Whisper、Florence-2 这类编码器-解码器模型对量化设置极其敏感，尤其是编码器。为此我们新增了按模块选择 dtype 的能力——提供一个"模块名 → dtype"的映射即可。

**示例：** 在 WebGPU 上运行 Florence-2（[demo](https://v2.scrimba.com/s0pdm485fo)）

```
import { Florence2ForConditionalGeneration } from "@huggingface/transformers";

const model = await Florence2ForConditionalGeneration.from_pretrained(
  "onnx-community/Florence-2-base-ft",
  {
    dtype: {
      embed_tokens: "fp16",
      vision_encoder: "fp16",
      encoder_model: "q4",
      decoder_model_merged: "q4",
    },
    device: "webgpu",
  },
);
```

![Florence-2 running on WebGPU](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/transformersjs-v3/florence-2-webgpu.gif)

See full code example

```
import {
  Florence2ForConditionalGeneration,
  AutoProcessor,
  AutoTokenizer,
  RawImage,
} from "@huggingface/transformers";

// Load model, processor, and tokenizer
const model_id = "onnx-community/Florence-2-base-ft";
const model = await Florence2ForConditionalGeneration.from_pretrained(
  model_id,
  {
    dtype: {
      embed_tokens: "fp16",
      vision_encoder: "fp16",
      encoder_model: "q4",
      decoder_model_merged: "q4",
    },
    device: "webgpu",
  },
);
const processor = await AutoProcessor.from_pretrained(model_id);
const tokenizer = await AutoTokenizer.from_pretrained(model_id);

// Load image and prepare vision inputs
const url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/transformers/tasks/car.jpg";
const image = await RawImage.fromURL(url);
const vision_inputs = await processor(image);

// Specify task and prepare text inputs
const task = "<MORE_DETAILED_CAPTION>";
const prompts = processor.construct_prompts(task);
const text_inputs = tokenizer(prompts);

// Generate text
const generated_ids = await model.generate({
  ...text_inputs,
  ...vision_inputs,
  max_new_tokens: 100,
});

// Decode generated text
const generated_text = tokenizer.batch_decode(generated_ids, {
  skip_special_tokens: false,
})[0];

// Post-process the generated text
const result = processor.post_process_generation(
  generated_text,
  task,
  image.size,
);
console.log(result);
// { '<MORE_DETAILED_CAPTION>': 'A green car is parked in front of a tan building. The building has a brown door and two brown windows. The car is a two door and the door is closed. The green car has black tires.' }
```

## 120 种支持的架构

本次发布把支持的架构总数提升到 120 种（见[完整列表](https://huggingface.co/docs/transformers.js/index#models)），覆盖广泛的输入模态和任务。值得关注的新名字：Phi-3、Gemma 与 Gemma 2、LLaVa、Moondream、Florence-2、MusicGen、Sapiens、Depth Pro、PyAnnote 和 RT-DETR。

![Bubble diagram of new architectures in Transformers.js v3](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/transformersjs-v3/architectures.png)

List of new models

- **[Cohere](https://huggingface.co/docs/transformers/main/model_doc/cohere)**（来自 Cohere），随论文 [Command-R: Retrieval Augmented Generation at Production Scale](https://txt.cohere.com/command-r/) 发布，作者 Cohere。
- **[Decision Transformer](https://huggingface.co/docs/transformers/model_doc/decision_transformer)**（来自 Berkeley/Facebook/Google），随论文 [Decision Transformer: Reinforcement Learning via Sequence Modeling](https://arxiv.org/abs/2106.01345) 发布，作者 Lili Chen, Kevin Lu, Aravind Rajeswaran, Kimin Lee, Aditya Grover, Michael Laskin, Pieter Abbeel, Aravind Srinivas, Igor Mordatch。
- **Depth Pro**（来自 Apple），随论文 [Depth Pro: Sharp Monocular Metric Depth in Less Than a Second](https://arxiv.org/abs/2410.02073) 发布，作者 Aleksei Bochkovskii, Amaël Delaunoy, Hugo Germain, Marcel Santos, Yichao Zhou, Stephan R. Richter, Vladlen Koltun。
- **Florence2**（来自 Microsoft），随论文 [Florence-2: Advancing a Unified Representation for a Variety of Vision Tasks](https://arxiv.org/abs/2311.06242) 发布，作者 Bin Xiao, Haiping Wu, Weijian Xu, Xiyang Dai, Houdong Hu, Yumao Lu, Michael Zeng, Ce Liu, Lu Yuan。
- **[Gemma](https://huggingface.co/docs/transformers/main/model_doc/gemma)**（来自 Google），随论文 [Gemma: Open Models Based on Gemini Technology and Research](https://blog.google/technology/developers/gemma-open-models/) 发布，作者 Gemma Google 团队。
- **[Gemma2](https://huggingface.co/docs/transformers/main/model_doc/gemma2)**（来自 Google），随论文 [Gemma2: Open Models Based on Gemini Technology and Research](https://blog.google/technology/developers/google-gemma-2/) 发布，作者 Gemma Google 团队。
- **[Granite](https://huggingface.co/docs/transformers/main/model_doc/granite)**（来自 IBM），随论文 [Power Scheduler: A Batch Size and Token Number Agnostic Learning Rate Scheduler](https://arxiv.org/abs/2408.13359) 发布，作者 Yikang Shen, Matthew Stallone, Mayank Mishra, Gaoyuan Zhang, Shawn Tan, Aditya Prasad, Adriana Meza Soria, David D. Cox, Rameswar Panda。
- **[GroupViT](https://huggingface.co/docs/transformers/model_doc/groupvit)**（来自 UCSD、NVIDIA），随论文 [GroupViT: Semantic Segmentation Emerges from Text Supervision](https://arxiv.org/abs/2202.11094) 发布，作者 Jiarui Xu, Shalini De Mello, Sifei Liu, Wonmin Byeon, Thomas Breuel, Jan Kautz, Xiaolong Wang。
- **[Hiera](https://huggingface.co/docs/transformers/model_doc/hiera)**（来自 Meta），随论文 [Hiera: A Hierarchical Vision Transformer without the Bells-and-Whistles](https://arxiv.org/pdf/2306.00989) 发布，作者 Chaitanya Ryali, Yuan-Ting Hu, Daniel Bolya, Chen Wei, Haoqi Fan, Po-Yao Huang, Vaibhav Aggarwal, Arkabandhu Chowdhury, Omid Poursaeed, Judy Hoffman, Jitendra Malik, Yanghao Li, Christoph Feichtenhofer。
- **JAIS**（来自 Core42），随论文 [Jais and Jais-chat: Arabic-Centric Foundation and Instruction-Tuned Open Generative Large Language Models](https://arxiv.org/pdf/2308.16149) 发布，作者 Neha Sengupta, Sunil Kumar Sahu, Bokang Jia, Satheesh Katipomu, Haonan Li, Fajri Koto, William Marshall, Gurpreet Gosal, Cynthia Liu, Zhiming Chen, Osama Mohammed Afzal, Samta Kamboj, Onkar Pandit, Rahul Pal, Lalit Pradhan, Zain Muhammad Mujahid, Massa Baali, Xudong Han, Sondos Mahmoud Bsharat, Alham Fikri Aji, Zhiqiang Shen, Zhengzhong Liu, Natalia Vassilieva, Joel Hestness, Andy Hock, Andrew Feldman, Jonathan Lee, Andrew Jackson, Hector Xuguang Ren, Preslav Nakov, Timothy Baldwin, Eric Xing。
- **[LLaVa](https://huggingface.co/docs/transformers/model_doc/llava)**（来自 Microsoft Research & University of Wisconsin-Madison），随论文 [Visual Instruction Tuning](https://arxiv.org/abs/2304.08485) 发布，作者 Haotian Liu, Chunyuan Li, Yuheng Li and Yong Jae Lee。
- **[MaskFormer](https://huggingface.co/docs/transformers/model_doc/maskformer)**（来自 Meta 和 UIUC），随论文 [Per-Pixel Classification is Not All You Need for Semantic Segmentation](https://arxiv.org/abs/2107.06278) 发布，作者 Bowen Cheng, Alexander G. Schwing, Alexander Kirillov。
- **[MusicGen](https://huggingface.co/docs/transformers/model_doc/musicgen)**（来自 Meta），随论文 [Simple and Controllable Music Generation](https://arxiv.org/abs/2306.05284) 发布，作者 Jade Copet, Felix Kreuk, Itai Gat, Tal Remez, David Kant, Gabriel Synnaeve, Yossi Adi and Alexandre Défossez。
- **MobileCLIP**（来自 Apple），随论文 [MobileCLIP: Fast Image-Text Models through Multi-Modal Reinforced Training](https://arxiv.org/abs/2311.17049) 发布，作者 Pavan Kumar Anasosalu Vasu, Hadi Pouransari, Fartash Faghri, Raviteja Vemulapalli, Oncel Tuzel。
- **[MobileNetV1](https://huggingface.co/docs/transformers/model_doc/mobilenet_v1)**（来自 Google Inc.），随论文 [MobileNets: Efficient Convolutional Neural Networks for Mobile Vision Applications](https://arxiv.org/abs/1704.04861) 发布，作者 Andrew G. Howard, Menglong Zhu, Bo Chen, Dmitry Kalenichenko, Weijun Wang, Tobias Weyand, Marco Andreetto, Hartwig Adam。
- **[MobileNetV2](https://huggingface.co/docs/transformers/model_doc/mobilenet_v2)**（来自 Google Inc.），随论文 [MobileNetV2: Inverted Residuals and Linear Bottlenecks](https://arxiv.org/abs/1801.04381) 发布，作者 Mark Sandler, Andrew Howard, Menglong Zhu, Andrey Zhmoginov, Liang-Chieh Chen。
- **MobileNetV3**（来自 Google Inc.），随论文 [Searching for MobileNetV3](https://arxiv.org/abs/1905.02244) 发布，作者 Andrew Howard, Mark Sandler, Grace Chu, Liang-Chieh Chen, Bo Chen, Mingxing Tan, Weijun Wang, Yukun Zhu, Ruoming Pang, Vijay Vasudevan, Quoc V. Le, Hartwig Adam。
- **MobileNetV4**（来自 Google Inc.），随论文 [MobileNetV4 - Universal Models for the Mobile Ecosystem](https://arxiv.org/abs/2404.10518) 发布，作者 Danfeng Qin, Chas Leichner, Manolis Delakis, Marco Fornoni, Shixin Luo, Fan Yang, Weijun Wang, Colby Banbury, Chengxi Ye, Berkin Akin, Vaibhav Aggarwal, Tenghui Zhu, Daniele Moro, Andrew Howard。
- **Moondream1**，发布于 vikhyat 的 [moondream](https://github.com/vikhyat/moondream) 仓库。
- **OpenELM**（来自 Apple），随论文 [OpenELM: An Efficient Language Model Family with Open-source Training and Inference Framework](https://arxiv.org/abs/2404.14619) 发布，作者 Sachin Mehta, Mohammad Hossein Sekhavat, Qingqing Cao, Maxwell Horton, Yanzi Jin, Chenfan Sun, Iman Mirzadeh, Mahyar Najibi, Dmitry Belenko, Peter Zatloukal, Mohammad Rastegari。
- **[Phi3](https://huggingface.co/docs/transformers/main/model_doc/phi3)**（来自 Microsoft），随论文 [Phi-3 Technical Report: A Highly Capable Language Model Locally on Your Phone](https://arxiv.org/abs/2404.14219) 发布，作者 Marah Abdin 等。
- **[PVT](https://huggingface.co/docs/transformers/main/model_doc/pvt)**（来自南京大学、港大等），随论文 [Pyramid Vision Transformer: A Versatile Backbone for Dense Prediction without Convolutions](https://arxiv.org/pdf/2102.12122.pdf) 发布，作者 Wenhai Wang, Enze Xie, Xiang Li, Deng-Ping Fan, Kaitao Song, Ding Liang, Tong Lu, Ping Luo, Ling Shao。
- **PyAnnote**，发布于 Hervé Bredin 的 [pyannote/pyannote-audio](https://github.com/pyannote/pyannote-audio) 仓库。
- **[RT-DETR](https://huggingface.co/docs/transformers/model_doc/rt_detr)**（来自 Baidu），随论文 [DETRs Beat YOLOs on Real-time Object Detection](https://arxiv.org/abs/2304.08069) 发布，作者 Yian Zhao, Wenyu Lv, Shangliang Xu, Jinman Wei, Guanzhong Wang, Qingqing Dang, Yi Liu, Jie Chen。
- **Sapiens**（来自 Meta AI），随论文 [Sapiens: Foundation for Human Vision Models](https://arxiv.org/pdf/2408.12569) 发布，作者 Rawal Khirodkar, Timur Bagautdinov, Julieta Martinez, Su Zhaoen, Austin James, Peter Selednik, Stuart Anderson, Shunsuke Saito。
- **[ViTMAE](https://huggingface.co/docs/transformers/model_doc/vit_mae)**（来自 Meta AI），随论文 [Masked Autoencoders Are Scalable Vision Learners](https://arxiv.org/abs/2111.06377) 发布，作者 Kaiming He, Xinlei Chen, Saining Xie, Yanghao Li, Piotr Dollár, Ross Girshick。
- **[ViTMSN](https://huggingface.co/docs/transformers/model_doc/vit_msn)**（来自 Meta AI），随论文 [Masked Siamese Networks for Label-Efficient Learning](https://arxiv.org/abs/2204.07141) 发布，作者 Mahmoud Assran, Mathilde Caron, Ishan Misra, Piotr Bojanowski, Florian Bordes, Pascal Vincent, Armand Joulin, Michael Rabbat, Nicolas Ballas。

## 示例项目与模板

随本次发布，我们上线了 25 个新示例项目和模板，主要用来展示 WebGPU 支持！包括 [Phi-3.5 WebGPU](https://github.com/huggingface/transformers.js-examples/tree/main/phi-3.5-webgpu) 和 [Whisper WebGPU](https://github.com/xenova/whisper-web/tree/experimental-webgpu) 等 demo，见下方动图。

> 我们正在把所有示例项目和 demo 迁移到 https://github.com/huggingface/transformers.js-examples ，敬请期待后续更新！

| ![Phi-3.5 running on WebGPU](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/transformersjs-v3/phi-3.5-webgpu.gif) | ![Whisper Turbo running on WebGPU](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/transformersjs-v3/whisper-turbo-webgpu.gif) |
| --- | --- |

## 超过 1200 个预转换模型

截至本次发布，社区已经把超过 1200 个模型转换成兼容 Transformers.js 的版本！可用模型完整列表见[这里](https://hf.co/models?library=transformers.js)。

想转换自己的模型或微调成果，可以用我们的[转换脚本](https://github.com/huggingface/transformers.js/blob/main/scripts/convert.py)：

```
python -m scripts.convert --quantize --model_id <model_name_or_path>
```

把生成的文件上传到 Hugging Face Hub 后，记得加上 `transformers.js` 标签，方便别人找到并使用你的模型！

![Available Transformers.js models](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/transformersjs-v3/models-dark.jpg)

## Node.js（ESM + CJS）、Deno 和 Bun 兼容

Transformers.js v3 现已兼容三大最流行的服务端 JavaScript 运行时：

| 运行时 | 说明 | 示例 |
| --- | --- | --- |
| [Node.js](https://nodejs.org/) | 基于 Chrome V8 的广泛使用的 JS 运行时，生态庞大，支持大量库和框架。 | [ESM 示例](https://github.com/huggingface/transformers.js-examples/tree/main/node-esm) / [CJS 示例](https://github.com/huggingface/transformers.js-examples/tree/main/node-cjs) |
| [Deno](https://deno.com/) | 默认安全的现代 JavaScript/TypeScript 运行时，使用 ES 模块，甚至带实验性 WebGPU 支持。 | [Deno 示例](https://github.com/huggingface/transformers.js-examples/tree/main/deno-embed) |
| [Bun](https://bun.sh/) | 为性能深度优化的快速 JS 运行时，内置打包器、转译器和包管理器。 | [Bun 示例](https://github.com/huggingface/transformers.js-examples/tree/main/bun) |

## NPM 和 GitHub 上的新家

最后，我们高兴地宣布 Transformers.js 现在以 Hugging Face 官方组织的名义在 NPM 发布为 [`@huggingface/transformers`](https://www.npmjs.com/package/@huggingface/transformers)（取代 v1、v2 使用的 [`@xenova/transformers`](https://www.npmjs.com/package/@xenova/transformers)）。

同时仓库也迁移到 Hugging Face 官方 GitHub 组织（[https://github.com/huggingface/transformers.js](https://github.com/huggingface/transformers.js)），这就是我们的新家——来打个招呼吧！我们期待你的反馈、回复你的 issue、审阅你的 PR！

这是一个重要的里程碑，非常感谢社区帮助我们达成这个长期目标！没有你们，这一切都不可能实现……谢谢！🤗
