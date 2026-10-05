---
vendor: huggingface
title: Transformers.js v3: WebGPU Support, New Models & Tasks, and More…
original_title: Transformers.js v3: WebGPU Support, New Models & Tasks, and More…
url: https://huggingface.co/blog/transformersjs-v3
date: 2024-10-22
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: ee11d219cb31
---

Back to Articles

# Transformers.js v3: WebGPU Support, New Models & Tasks, and More…

Published
					October 22, 2024

Update on GitHub

Upvote

85

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6317233cc92fd6fee317e030/cJHSvvimr1kqgQfHOjO5n.png)](https://huggingface.co/tomaarsen)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/5e3aec01f55e2b62848a5217/PMKS0NNB4MJQlTSFzh918.jpeg)](https://huggingface.co/lysandre)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64371b564aacf7bf786fb530/HZl_fPo7YclFEuuLSme3K.png)](https://huggingface.co/Nymbo)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1594214747713-5e9ecfc04957053f60648a3e.png)](https://huggingface.co/lhoestq)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)](https://huggingface.co/pcuenq)
- [![](https://huggingface.co/avatars/973db41f23cd375c588e7828c5efe5ce.svg)](https://huggingface.co/pierrci)

Joshua

Xenova

After more than a year of development, we're excited to announce the release of 🤗 Transformers.js v3!

Highlights include:

- [WebGPU support (up to 100x faster than WASM!)](https://huggingface.co/blog/transformersjs-v3#webgpu-support)
- [New quantization formats (dtypes)](https://huggingface.co/blog/transformersjs-v3#new-quantization-formats-dtypes)
- [A total of 120 supported architectures](https://huggingface.co/blog/transformersjs-v3#120-supported-architectures)
- [25 new example projects and templates](https://huggingface.co/blog/transformersjs-v3#example-projects-and-templates)
- [Over 1200 pre-converted models on the Hugging Face Hub](https://huggingface.co/blog/transformersjs-v3#over-1200-pre-converted-models)
- [Node.js (ESM + CJS), Deno, and Bun compatibility](https://huggingface.co/blog/transformersjs-v3#nodejs-esm--cjs-deno-and-bun-compatibility)
- [A new home on GitHub and NPM](https://huggingface.co/blog/transformersjs-v3#a-new-home-on-npm-and-github)

## Installation

You can get started by installing Transformers.js v3 from [NPM](https://www.npmjs.com/package/@huggingface/transformers) using:

```
npm i @huggingface/transformers
```

Then, importing the library with

```
import { pipeline } from "@huggingface/transformers";
```

or, via a CDN

```
import { pipeline } from "https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.0.0";
```

For more information, check out the [documentation](https://hf.co/docs/transformers.js).

## WebGPU support

WebGPU is a new web standard for accelerated graphics and compute. The [API](https://developer.mozilla.org/en-US/docs/Web/API/WebGPU_API) enables web developers to use the underlying system's GPU to carry out high-performance computations directly in the browser. WebGPU is the successor to [WebGL](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API) and provides significantly better performance, because it allows for more direct interaction with modern GPUs. Lastly, it supports general-purpose GPU computations, which makes it just perfect for machine learning!

> As of October 2024, global WebGPU support is around 70% (according to caniuse.com), meaning some users may not be able to use the API.
> If the following demos do not work in your browser, you may need to enable it using a feature flag:
> 
> Firefox: with the dom.webgpu.enabled flag (see here).
> Safari: with the WebGPU feature flag (see here).
> Older Chromium browsers (on Windows, macOS, Linux): with the enable-unsafe-webgpu flag (see here).

### Usage in Transformers.js v3

Thanks to our collaboration with [ONNX Runtime Web](https://www.npmjs.com/package/onnxruntime-web), enabling WebGPU acceleration is as simple as setting `device: 'webgpu'` when loading a model. Let's see some examples!

**Example:** Compute text embeddings on WebGPU ([demo](https://v2.scrimba.com/s06a2smeej))

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

**Example:** Perform automatic speech recognition with OpenAI whisper on WebGPU ([demo](https://v2.scrimba.com/s0oi76h82g))

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

**Example:** Perform image classification with MobileNetV4 on WebGPU ([demo](https://v2.scrimba.com/s0fv2uab1t))

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

## New quantization formats (dtypes)

Before Transformers.js v3, we used the `quantized` option to specify whether to use a quantized (q8) or full-precision (fp32) variant of the model by setting `quantized` to `true` or `false`, respectively. Now, we've added the ability to select from a much larger list with the `dtype` parameter.

The list of available quantizations depends on the model, but some common ones are: full-precision (`"fp32"`), half-precision (`"fp16"`), 8-bit (`"q8"`, `"int8"`, `"uint8"`), and 4-bit (`"q4"`, `"bnb4"`, `"q4f16"`).

![Available dtypes for mixedbread-ai/mxbai-embed-xsmall-v1](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/transformersjs-v3/dtypes-dark.jpg)  [(e.g., mixedbread-ai/mxbai-embed-xsmall-v1)](https://huggingface.co/mixedbread-ai/mxbai-embed-xsmall-v1/tree/main/onnx)

### Basic usage

**Example:** Run Qwen2.5-0.5B-Instruct in 4-bit quantization ([demo](https://v2.scrimba.com/s0dlcpv0ci))

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

### Per-module dtypes

Some encoder-decoder models, like Whisper or Florence-2, are extremely sensitive to quantization settings: especially of the encoder. For this reason, we added the ability to select per-module dtypes, which can be done by providing a mapping from module name to dtype.

**Example:** Run Florence-2 on WebGPU ([demo](https://v2.scrimba.com/s0pdm485fo))

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

## 120 supported architectures

This release increases the total number of supported architectures to 120 (see [full list](https://huggingface.co/docs/transformers.js/index#models)), spanning a wide range of input modalities and tasks. Notable new names include: Phi-3, Gemma & Gemma 2, LLaVa, Moondream, Florence-2, MusicGen, Sapiens, Depth Pro, PyAnnote, and RT-DETR.

![Bubble diagram of new architectures in Transformers.js v3](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/transformersjs-v3/architectures.png)

List of new models

- **[Cohere](https://huggingface.co/docs/transformers/main/model_doc/cohere)** (from Cohere) released with the paper [Command-R: Retrieval Augmented Generation at Production Scale](https://txt.cohere.com/command-r/) by Cohere.
- **[Decision Transformer](https://huggingface.co/docs/transformers/model_doc/decision_transformer)** (from Berkeley/Facebook/Google) released with the paper [Decision Transformer: Reinforcement Learning via Sequence Modeling](https://arxiv.org/abs/2106.01345) by Lili Chen, Kevin Lu, Aravind Rajeswaran, Kimin Lee, Aditya Grover, Michael Laskin, Pieter Abbeel, Aravind Srinivas, Igor Mordatch.
- **Depth Pro** (from Apple) released with the paper [Depth Pro: Sharp Monocular Metric Depth in Less Than a Second](https://arxiv.org/abs/2410.02073) by Aleksei Bochkovskii, Amaël Delaunoy, Hugo Germain, Marcel Santos, Yichao Zhou, Stephan R. Richter, Vladlen Koltun.
- **Florence2** (from Microsoft) released with the paper [Florence-2: Advancing a Unified Representation for a Variety of Vision Tasks](https://arxiv.org/abs/2311.06242) by Bin Xiao, Haiping Wu, Weijian Xu, Xiyang Dai, Houdong Hu, Yumao Lu, Michael Zeng, Ce Liu, Lu Yuan.
- **[Gemma](https://huggingface.co/docs/transformers/main/model_doc/gemma)** (from Google) released with the paper [Gemma: Open Models Based on Gemini Technology and Research](https://blog.google/technology/developers/gemma-open-models/) by the Gemma Google team.
- **[Gemma2](https://huggingface.co/docs/transformers/main/model_doc/gemma2)** (from Google) released with the paper [Gemma2: Open Models Based on Gemini Technology and Research](https://blog.google/technology/developers/google-gemma-2/) by the Gemma Google team.
- **[Granite](https://huggingface.co/docs/transformers/main/model_doc/granite)** (from IBM) released with the paper [Power Scheduler: A Batch Size and Token Number Agnostic Learning Rate Scheduler](https://arxiv.org/abs/2408.13359) by Yikang Shen, Matthew Stallone, Mayank Mishra, Gaoyuan Zhang, Shawn Tan, Aditya Prasad, Adriana Meza Soria, David D. Cox, Rameswar Panda.
- **[GroupViT](https://huggingface.co/docs/transformers/model_doc/groupvit)** (from UCSD, NVIDIA) released with the paper [GroupViT: Semantic Segmentation Emerges from Text Supervision](https://arxiv.org/abs/2202.11094) by Jiarui Xu, Shalini De Mello, Sifei Liu, Wonmin Byeon, Thomas Breuel, Jan Kautz, Xiaolong Wang.
- **[Hiera](https://huggingface.co/docs/transformers/model_doc/hiera)** (from Meta) released with the paper [Hiera: A Hierarchical Vision Transformer without the Bells-and-Whistles](https://arxiv.org/pdf/2306.00989) by Chaitanya Ryali, Yuan-Ting Hu, Daniel Bolya, Chen Wei, Haoqi Fan, Po-Yao Huang, Vaibhav Aggarwal, Arkabandhu Chowdhury, Omid Poursaeed, Judy Hoffman, Jitendra Malik, Yanghao Li, Christoph Feichtenhofer.
- **JAIS** (from Core42) released with the paper [Jais and Jais-chat: Arabic-Centric Foundation and Instruction-Tuned Open Generative Large Language Models](https://arxiv.org/pdf/2308.16149) by Neha Sengupta, Sunil Kumar Sahu, Bokang Jia, Satheesh Katipomu, Haonan Li, Fajri Koto, William Marshall, Gurpreet Gosal, Cynthia Liu, Zhiming Chen, Osama Mohammed Afzal, Samta Kamboj, Onkar Pandit, Rahul Pal, Lalit Pradhan, Zain Muhammad Mujahid, Massa Baali, Xudong Han, Sondos Mahmoud Bsharat, Alham Fikri Aji, Zhiqiang Shen, Zhengzhong Liu, Natalia Vassilieva, Joel Hestness, Andy Hock, Andrew Feldman, Jonathan Lee, Andrew Jackson, Hector Xuguang Ren, Preslav Nakov, Timothy Baldwin, Eric Xing.
- **[LLaVa](https://huggingface.co/docs/transformers/model_doc/llava)** (from Microsoft Research & University of Wisconsin-Madison) released with the paper [Visual Instruction Tuning](https://arxiv.org/abs/2304.08485) by Haotian Liu, Chunyuan Li, Yuheng Li and Yong Jae Lee.
- **[MaskFormer](https://huggingface.co/docs/transformers/model_doc/maskformer)** (from Meta and UIUC) released with the paper [Per-Pixel Classification is Not All You Need for Semantic Segmentation](https://arxiv.org/abs/2107.06278) by Bowen Cheng, Alexander G. Schwing, Alexander Kirillov.
- **[MusicGen](https://huggingface.co/docs/transformers/model_doc/musicgen)** (from Meta) released with the paper [Simple and Controllable Music Generation](https://arxiv.org/abs/2306.05284) by Jade Copet, Felix Kreuk, Itai Gat, Tal Remez, David Kant, Gabriel Synnaeve, Yossi Adi and Alexandre Défossez.
- **MobileCLIP** (from Apple) released with the paper [MobileCLIP: Fast Image-Text Models through Multi-Modal Reinforced Training](https://arxiv.org/abs/2311.17049) by Pavan Kumar Anasosalu Vasu, Hadi Pouransari, Fartash Faghri, Raviteja Vemulapalli, Oncel Tuzel.
- **[MobileNetV1](https://huggingface.co/docs/transformers/model_doc/mobilenet_v1)** (from Google Inc.) released with the paper [MobileNets: Efficient Convolutional Neural Networks for Mobile Vision Applications](https://arxiv.org/abs/1704.04861) by Andrew G. Howard, Menglong Zhu, Bo Chen, Dmitry Kalenichenko, Weijun Wang, Tobias Weyand, Marco Andreetto, Hartwig Adam.
- **[MobileNetV2](https://huggingface.co/docs/transformers/model_doc/mobilenet_v2)** (from Google Inc.) released with the paper [MobileNetV2: Inverted Residuals and Linear Bottlenecks](https://arxiv.org/abs/1801.04381) by Mark Sandler, Andrew Howard, Menglong Zhu, Andrey Zhmoginov, Liang-Chieh Chen.
- **MobileNetV3** (from Google Inc.) released with the paper [Searching for MobileNetV3](https://arxiv.org/abs/1905.02244) by Andrew Howard, Mark Sandler, Grace Chu, Liang-Chieh Chen, Bo Chen, Mingxing Tan, Weijun Wang, Yukun Zhu, Ruoming Pang, Vijay Vasudevan, Quoc V. Le, Hartwig Adam.
- **MobileNetV4** (from Google Inc.) released with the paper [MobileNetV4 - Universal Models for the Mobile Ecosystem](https://arxiv.org/abs/2404.10518) by Danfeng Qin, Chas Leichner, Manolis Delakis, Marco Fornoni, Shixin Luo, Fan Yang, Weijun Wang, Colby Banbury, Chengxi Ye, Berkin Akin, Vaibhav Aggarwal, Tenghui Zhu, Daniele Moro, Andrew Howard.
- **Moondream1** released in the repository [moondream](https://github.com/vikhyat/moondream) by vikhyat.
- **OpenELM** (from Apple) released with the paper [OpenELM: An Efficient Language Model Family with Open-source Training and Inference Framework](https://arxiv.org/abs/2404.14619) by Sachin Mehta, Mohammad Hossein Sekhavat, Qingqing Cao, Maxwell Horton, Yanzi Jin, Chenfan Sun, Iman Mirzadeh, Mahyar Najibi, Dmitry Belenko, Peter Zatloukal, Mohammad Rastegari.
- **[Phi3](https://huggingface.co/docs/transformers/main/model_doc/phi3)** (from Microsoft) released with the paper [Phi-3 Technical Report: A Highly Capable Language Model Locally on Your Phone](https://arxiv.org/abs/2404.14219) by Marah Abdin, Sam Ade Jacobs, Ammar Ahmad Awan, Jyoti Aneja, Ahmed Awadallah, Hany Awadalla, Nguyen Bach, Amit Bahree, Arash Bakhtiari, Harkirat Behl, Alon Benhaim, Misha Bilenko, Johan Bjorck, Sébastien Bubeck, Martin Cai, Caio César Teodoro Mendes, Weizhu Chen, Vishrav Chaudhary, Parul Chopra, Allie Del Giorno, Gustavo de Rosa, Matthew Dixon, Ronen Eldan, Dan Iter, Amit Garg, Abhishek Goswami, Suriya Gunasekar, Emman Haider, Junheng Hao, Russell J. Hewett, Jamie Huynh, Mojan Javaheripi, Xin Jin, Piero Kauffmann, Nikos Karampatziakis, Dongwoo Kim, Mahoud Khademi, Lev Kurilenko, James R. Lee, Yin Tat Lee, Yuanzhi Li, Chen Liang, Weishung Liu, Eric Lin, Zeqi Lin, Piyush Madan, Arindam Mitra, Hardik Modi, Anh Nguyen, Brandon Norick, Barun Patra, Daniel Perez-Becker, Thomas Portet, Reid Pryzant, Heyang Qin, Marko Radmilac, Corby Rosset, Sambudha Roy, Olatunji Ruwase, Olli Saarikivi, Amin Saied, Adil Salim, Michael Santacroce, Shital Shah, Ning Shang, Hiteshi Sharma, Xia Song, Masahiro Tanaka, Xin Wang, Rachel Ward, Guanhua Wang, Philipp Witte, Michael Wyatt, Can Xu, Jiahang Xu, Sonali Yadav, Fan Yang, Ziyi Yang, Donghan Yu, Chengruidong Zhang, Cyril Zhang, Jianwen Zhang, Li Lyna Zhang, Yi Zhang, Yue Zhang, Yunan Zhang, Xiren Zhou.
- **[PVT](https://huggingface.co/docs/transformers/main/model_doc/pvt)** (from Nanjing University, The University of Hong Kong etc.) released with the paper [Pyramid Vision Transformer: A Versatile Backbone for Dense Prediction without Convolutions](https://arxiv.org/pdf/2102.12122.pdf) by Wenhai Wang, Enze Xie, Xiang Li, Deng-Ping Fan, Kaitao Song, Ding Liang, Tong Lu, Ping Luo, Ling Shao.
- **PyAnnote** released in the repository [pyannote/pyannote-audio](https://github.com/pyannote/pyannote-audio) by Hervé Bredin.
- **[RT-DETR](https://huggingface.co/docs/transformers/model_doc/rt_detr)** (from Baidu), released together with the paper [DETRs Beat YOLOs on Real-time Object Detection](https://arxiv.org/abs/2304.08069) by Yian Zhao, Wenyu Lv, Shangliang Xu, Jinman Wei, Guanzhong Wang, Qingqing Dang, Yi Liu, Jie Chen.
- **Sapiens** (from Meta AI) released with the paper [Sapiens: Foundation for Human Vision Models](https://arxiv.org/pdf/2408.12569) by Rawal Khirodkar, Timur Bagautdinov, Julieta Martinez, Su Zhaoen, Austin James, Peter Selednik, Stuart Anderson, Shunsuke Saito.
- **[ViTMAE](https://huggingface.co/docs/transformers/model_doc/vit_mae)** (from Meta AI) released with the paper [Masked Autoencoders Are Scalable Vision Learners](https://arxiv.org/abs/2111.06377) by Kaiming He, Xinlei Chen, Saining Xie, Yanghao Li, Piotr Dollár, Ross Girshick.
- **[ViTMSN](https://huggingface.co/docs/transformers/model_doc/vit_msn)** (from Meta AI) released with the paper [Masked Siamese Networks for Label-Efficient Learning](https://arxiv.org/abs/2204.07141) by Mahmoud Assran, Mathilde Caron, Ishan Misra, Piotr Bojanowski, Florian Bordes, Pascal Vincent, Armand Joulin, Michael Rabbat, Nicolas Ballas.

## Example projects and templates

As part of the release, we've published 25 new example projects and templates, primarily focused on showcasing WebGPU support! This includes demos like [Phi-3.5 WebGPU](https://github.com/huggingface/transformers.js-examples/tree/main/phi-3.5-webgpu) and [Whisper WebGPU](https://github.com/xenova/whisper-web/tree/experimental-webgpu), as shown below.

> We're in the process of moving all our example projects and demos to https://github.com/huggingface/transformers.js-examples, so stay tuned for updates on this!

| ![Phi-3.5 running on WebGPU](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/transformersjs-v3/phi-3.5-webgpu.gif) | ![Whisper Turbo running on WebGPU](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/transformersjs-v3/whisper-turbo-webgpu.gif) |
| --- | --- |

## Over 1200 pre-converted models

As of today's release, the community has converted over 1200 models to be compatible with Transformers.js! You can find the full list of available models [here](https://hf.co/models?library=transformers.js).

If you'd like to convert your own models or fine-tunes, you can use our [conversion script](https://github.com/huggingface/transformers.js/blob/main/scripts/convert.py) as follows:

```
python -m scripts.convert --quantize --model_id <model_name_or_path>
```

After uploading the generated files to the Hugging Face Hub, remember to add the `transformers.js` tag so others can easily find and use your model!

![Available Transformers.js models](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/transformersjs-v3/models-dark.jpg)

## Node.js (ESM + CJS), Deno, and Bun compatibility

Transformers.js v3 is now compatible with the three most popular server-side JavaScript runtimes:

| Runtime | Description | Examples |
| --- | --- | --- |
| [Node.js](https://nodejs.org/) | A widely-used JavaScript runtime built on Chrome's V8. It has a large ecosystem and supports a wide range of libraries and frameworks. | [ESM Example](https://github.com/huggingface/transformers.js-examples/tree/main/node-esm) / [CJS Example](https://github.com/huggingface/transformers.js-examples/tree/main/node-cjs) |
| [Deno](https://deno.com/) | A modern runtime for JavaScript and TypeScript that is secure by default. It uses ES modules and even features experimental WebGPU support. | [Deno Example](https://github.com/huggingface/transformers.js-examples/tree/main/deno-embed) |
| [Bun](https://bun.sh/) | A fast JavaScript runtime optimized for performance. It features a built-in bundler, transpiler, and package manager. | [Bun Example](https://github.com/huggingface/transformers.js-examples/tree/main/bun) |

## A new home on NPM and GitHub

Finally, we're delighted to announce that Transformers.js will now be published under the official Hugging Face organization on NPM as [`@huggingface/transformers`](https://www.npmjs.com/package/@huggingface/transformers) (instead of [`@xenova/transformers`](https://www.npmjs.com/package/@xenova/transformers), which was used for v1 and v2).

We've also moved the repository to the official Hugging Face organization on GitHub ([https://github.com/huggingface/transformers.js](https://github.com/huggingface/transformers.js)), which will be our new home — come say hi! We look forward to hearing your feedback, responding to your issues, and reviewing your PRs!

This is a significant milestone and we're extremely grateful to the community for helping us achieve this long-term goal! None of this would be possible without all of you… thank you! 🤗

More Articles from our Blog

announcement

transformers.js

transformers

## Transformers.js v4: Now Available on NPM!

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/61b253b7ac5ecaae3d1efe0c/hwiQ0uvz3t-L5a-NtBIO6.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6468b720b2321e47d32683da/aWAEJJ03I9Z5syqDxHObT.jpeg)

98

February 9, 2026

cross-origin-storage

cos

announcement

## Experimenting with the proposed Cross-Origin Storage API in Transformers.js

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/qCHAzPfN19g2BtO9jJDNv.jpeg)

8

June 23, 2026

### Community

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Ftransformersjs-v3) or [log in](https://huggingface.co/login?next=%2Fblog%2Ftransformersjs-v3) to comment

Upvote

85

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6317233cc92fd6fee317e030/cJHSvvimr1kqgQfHOjO5n.png)](https://huggingface.co/tomaarsen)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/5e3aec01f55e2b62848a5217/PMKS0NNB4MJQlTSFzh918.jpeg)](https://huggingface.co/lysandre)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64371b564aacf7bf786fb530/HZl_fPo7YclFEuuLSme3K.png)](https://huggingface.co/Nymbo)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1594214747713-5e9ecfc04957053f60648a3e.png)](https://huggingface.co/lhoestq)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1617264212503-603d25b75f9d390ab190b777.jpeg)](https://huggingface.co/pcuenq)
- [![](https://huggingface.co/avatars/973db41f23cd375c588e7828c5efe5ce.svg)](https://huggingface.co/pierrci)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6340651b388c3fa40f9a5bc0/vM3rB17pUNT11MUhYqfFY.png)](https://huggingface.co/adamm-hf)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6643cc9a9d42d1d77c1c830f/QYvjWqiiXvyeidYhNm9M5.jpeg)](https://huggingface.co/elliesleightholm)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/Qz1WRFYfs6ZSnRz88wEZt.jpeg)](https://huggingface.co/denizaybey)
- [![](https://huggingface.co/avatars/9302038f3922be4f8f3e6c2c04d18edf.svg)](https://huggingface.co/eduard26)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/648a374f00f7a3374ee64b99/YPwSOrronoozwHbJchPn3.jpeg)](https://huggingface.co/cfahlgren1)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6192895f3b8aa351a46fadfd/gsGa2PvHTKAv7MNbyLH8y.jpeg)](https://huggingface.co/celinah)
