---
vendor: jina_ai
title: jina-embeddings-v5-omni：面向文本、图像、音频与视频的 embedding
original_title: 
url: https://jina.ai/news/jina-embeddings-v5-omni-multimodal-embeddings-for-text-image-audio-and-video
date: 2026-05-12
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# jina-embeddings-v5-omni：面向文本、图像、音频与视频的 embedding

一个模型，四种模态：文本、图像、音频、视频。1.6B 和 0.9B 两个规模，提供同类最佳的 omni embeddings。

Jina AI · 7 分钟阅读

jina-embeddings-v5-omni — jinaai 的一个模型合集（Collection）

与 jina-embeddings-v5-text-* 对齐的多模态（文本 + 图像 + 视频 + 音频）embedding 模型。两种规模，每种四个任务变体。

jina-embeddings-v5-omni: Text-Geometry-Preserving Multimodal Embeddings via Frozen-Tower Composition

在本工作中，我们提出冻结编码器模型组合（frozen-encoder model composition），一种面向多模态 embedding 模型的新方法。我们建立在 VLM 风格的架构之上：非文本编码器经过适配，为语言模型产出输入，而语言模型进而为各种输入生成 embedding。我们给出成果：jina-embeddings-v5-omni 系列，一对把文本、图像、音频和视频输入编码到单一语义 embedding 空间的模型。我们的做法是扩展两个 Jina Embeddings v5 Text 模型，通过加入图像和音频编码器来支持更多媒体。作为骨干的文本 embedding 模型和新加入的非文本媒体编码器都保持冻结。我们只训练连接各部分的组件，占联合模型总权重的 0.35%。因此训练远比全参数重训高效。此外，语言模型实际上未被改动，对文本输入产出的 embedding 与 Jina Embeddings v5 Text 模型完全一致。我们的评估表明，这一方法产出的结果足以与最先进水平竞争，性能与更大的多模态 embedding 模型几乎相当。

Florian Hönicke

我们正在发布 **jina-embeddings-v5-omni**，把我们的 v5-text embedding 模型扩展到图像、音频和视频。两个模型都与 v5-text 共享同一个冻结的文本主干，也就是说文本 embedding **完全一致**——无需重建索引。[jina-embeddings-v5-omni-small](https://jina.ai/?sui&model=jina-embeddings-v5-omni-small) 在四种模态上的平均得分 **53.93**，追平 LCO-7B（54.43），而参数**少 5.7 倍**；[jina-embeddings-v5-omni-nano](https://jina.ai/?sui&model=jina-embeddings-v5-omni-nano) 仅用 0.95B 参数就带来了有竞争力的文档检索。

所有开源权重 omni embedding 模型（支持文本、图像、音频和视频）的帕累托前沿。

jina-embeddings-v5-omni-small（1.57B）追平了 LCO-7B（8.93B）的平均得分，而参数少 5.7 倍。

jina-embeddings-v5-omni-nano（0.95B）比 LanguageBind（1.14B）高 8.9 分。基线：LanguageBind、Omni-Embed-Nemotron-3B、LCO-Embedding-Omni-3B、LCO-Embedding-Omni-7B。

按模态拆分的表现：文本（MMTEB）、图像（MIEB）、视频（MMEB-Video）和音频（MAEB）。

jina-embeddings-v5-omni-small 在文本上以 67.0 领先所有 omni 模型，完整继承了 jina-embeddings-v5-text-small 的质量。在图像上（56.05），它擅长分类（68.55）和聚类（84.57，为所有模型中最佳）。音频（51.46）接近 LCO-7B（52.37），并拥有最佳的音频分类得分（55.89）。视频（41.20）是相对 LCO-7B（47.41）目前存在的差距，因为时序推理更受益于端到端训练。

13 种任务类型上的分任务表现。金色星号标出 jina-embeddings-v5-omni-small 超过最佳开源权重基线（后者体积大 3-9 倍）的任务。胜项：图像分类（68.55 对 64.30）、图像聚类（84.57 对 83.24）、音频分类（55.89 对 53.39）。主要差距：视频检索（27.82 对 58.73）和组合式/视觉问答（44.23 对 53.40）。

文档检索（ViDoRe-in-MIEB）。

jina-embeddings-v5-omni-small 在文本+图像上仅 0.92B 激活参数，得分 79.08，超过 LCO-3B（4.07B 参数，78.24）。

jina-embeddings-v5-omni-nano 仅用 0.31B 激活参数就得到 70.05，远高于 LanguageBind（37.33）。Nemotron-3B 以 85.64 领先，但参数多 5.1 倍。

## [*tag*](https://jina.ai/news/jina-embeddings-v5-omni-multimodal-embeddings-for-text-image-audio-and-video/#architecture)架构

v5-omni 把 v5-text 主干完全冻结，并加入预训练的视觉和音频编码器，通过小型可训练的投影层（projector）连接：

- **视觉**：Qwen3.5 视觉编码器（由 SigLIP2 适配而来），采用 2x2 空间合并（token 减少 4 倍）。除了最后的投影层（`fc_vision_2`）外，其余全部冻结；我们把该层替换为一个随机初始化的层，映射到文本主干的隐藏维度。
- **音频**：Qwen2.5-Omni 编码器（由 Whisper-large-v3 适配而来）。一个随机初始化的 `fc_audio` 层把 1280 维输出投影进文本主干。
- **视频**：作为一串视觉帧来处理，可选地在其前面接上一段抽取出的音频。

该模型继承了 v5-text 的四个任务专用 LoRA adapter（retrieval、text-matching、classification、clustering），并为每个任务变体训练各自独立的投影层权重。架构完全模块化：纯文本部署不加载任何视觉或音频权重（与 v5-text 占用完全相同），仅图像部署跳过音频，完整 omni 则加载全部。

v5-omni 架构。冻结的视觉和音频编码器把可训练的投影层喂给冻结的文本主干。只有投影层（占总权重 0.35%）被训练。任务专用 LoRA adapter 负责检索、分类、聚类和文本匹配。

| 特性 | [jina-embeddings-v5-omni-small](https://jina.ai/?sui&model=jina-embeddings-v5-omni-small) | [jina-embeddings-v5-omni-nano](https://jina.ai/?sui&model=jina-embeddings-v5-omni-nano) |
| --- | --- | --- |
| 基础文本模型 | [jina-embeddings-v5-text-small](https://jina.ai/?sui&model=jina-embeddings-v5-text-small)（Qwen3-0.6B） | [jina-embeddings-v5-text-nano](https://jina.ai/?sui&model=jina-embeddings-v5-text-nano)（EuroBERT-210m） |
| 总参数 | ~1.56B | ~1.04B |
| 模态 | 文本、图像、音频、视频、PDF | 文本、图像、音频、视频、PDF |
| Embedding 维度 | 1024 | 768 |
| Matryoshka 维度 | 32, 64, 128, 256, 512, 768, 1024 | 32, 64, 128, 256, 512, 768 |
| 最大序列长度 | 32768 token | 8192 token |
| 视觉编码器 | Qwen3.5-2B ViT（SigLIP2） | SigLIP2 Base |
| 音频编码器 | Whisper-large-v3 | Whisper-large-v3 |
| 任务 | retrieval、text-matching、classification、clustering | retrieval、text-matching、classification、clustering |
| 文本兼容性 | 与 [jina-embeddings-v5-text-small](https://jina.ai/?sui&model=jina-embeddings-v5-text-small) 完全一致 | 与 [jina-embeddings-v5-text-nano](https://jina.ai/?sui&model=jina-embeddings-v5-text-nano) 完全一致 |
| 可训练参数 | 约 18M 投影层（0.35%） | 约 7M 投影层（0.35%） |
| 池化 | Last-token | Last-token |
| 许可证 | CC BY-NC 4.0 | CC BY-NC 4.0 |

## [*tag*](https://jina.ai/news/jina-embeddings-v5-omni-multimodal-embeddings-for-text-image-audio-and-video/#getting-started)快速上手

### [*tag*](https://jina.ai/news/jina-embeddings-v5-omni-multimodal-embeddings-for-text-image-audio-and-video/#elasticsearch-elastic-inference-service)Elasticsearch（Elastic Inference Service）

如果你已经在 Elasticsearch 中使用 `jina-embeddings-v5-text`，那么现有的文本索引可以直接用于 v5-omni。omni 模型对文本输入产出的 **embedding 与 v5-text 完全一致**——相同输入、相同向量，逐字节相同。你不需要重新嵌入或重建任何文本索引。要在现有文本数据旁边开始检索图像、音频和视频，只需用 v5-omni 新建一个索引，再把多模态内容写入其中即可。

以 v5-omni 作为推理端点，创建一个 `semantic_text` 索引。EIS 会自动为索引和检索选择正确的 LoRA adapter：

```
PUT multimodal-semantic-index
{
  "mappings": {
    "properties": {
      "content": {
        "type": "semantic_text",
        "inference_id": ".jina-embeddings-v5-omni-small"
      }
    }
  }
}
```

把文本、图像（以 base64 data URI 形式）、音频和视频写入同一个字段、同一个索引：

```
// Ingest text
POST multimodal-semantic-index/_doc
{
  "content": "'Kraft Dinner' is what Canadians call macaroni and cheese when prepared from a kit."
}

// Ingest an image (base64)
POST multimodal-semantic-index/_doc
{
  "content": "data:image/png;base64,iVBORw0KGgoAAAAN..."
}
```

用一条文本查询跨所有模态检索：

```
GET multimodal-semantic-index/_search
{
  "query": {
    "semantic": {
      "field": "content",
      "query": "Was bedeutet 'Kraft Dinner' für Kanadier?"
    }
  }
}
```

### [*tag*](https://jina.ai/news/jina-embeddings-v5-omni-multimodal-embeddings-for-text-image-audio-and-video/#jina-embedding-api)Jina Embedding API

```
curl https://api.jina.ai/v1/embeddings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "jina-embeddings-v5-omni-small",
    "task": "retrieval.query",
    "dimensions": 1024,
    "input": ["What does this image show?"],
    "images": ["data:image/png;base64,..."]
  }'
```

### [*tag*](https://jina.ai/news/jina-embeddings-v5-omni-multimodal-embeddings-for-text-image-audio-and-video/#hugging-face)Hugging Face

```
from sentence_transformers import SentenceTransformer
import torch

model = SentenceTransformer(
    "jinaai/jina-embeddings-v5-omni-small-retrieval",
    model_kwargs={"dtype": torch.bfloat16},
)

# Text embedding (identical to v5-text)
text_emb = model.encode("What is knowledge distillation?", prompt_name="query")

# Image embedding
from PIL import Image
img = Image.open("photo.jpg")
img_emb = model.encode(img)

# Cross-modal similarity
similarity = model.similarity(text_emb, img_emb)
```

## [*tag*](https://jina.ai/news/jina-embeddings-v5-omni-multimodal-embeddings-for-text-image-audio-and-video/#training)训练

核心思想是*冻结编码器模型组合*：取一个强大的文本 embedding 模型，加入预训练的视觉和音频编码器，用小型可训练的投影层把它们连接起来，然后除这些投影层外全部冻结。只有总权重的 0.35% 被训练，这带来三个特性：（1）文本一致性保持——主干未被改动，相同输入产出相同输出；（2）训练高效——仅训练投影层比全量训练快 1.8-3.9 倍，GPU 显存少用 42-64%；（3）模块化——各塔（tower）可独立加载。

仅投影层训练与完整训练的对比，在 4x H100 GPU 上进行（batch size 256，15K 步）。音频投影层训练尤其高效：small 快 3.2 倍（154 分钟对 497 分钟），nano 快 3.9 倍（112 分钟对 441 分钟）。显存节省 42-64% 来自不再为冻结编码器存储梯度和优化器状态。

v5-omni 从 v5-text 继承了 Matryoshka 维度支持。图像和音频 embedding 在截断后仍能保持大部分质量，而视频在小维度下退化较多。

小结：v5-omni 相对最强基线的各模态画像。

jina-embeddings-v5-omni-small 以 1.57B 规模在文本、图像和音频上都具备竞争力，视频则是尚待弥合的差距。

## [*tag*](https://jina.ai/news/jina-embeddings-v5-omni-multimodal-embeddings-for-text-image-audio-and-video/#conclusion)结论

通常的观念认为，多模态 embedding 需要端到端地训练整个模型。我们不同意。v5-omni 冻结文本主干、只训练 0.35% 的权重，却能追平体积是它 5-7 倍的模型。教训是：组合胜过重训。强大的文本编码器是最难的部分——一旦你有了它，通过轻量投影层挂上视觉和音频几乎是不花成本的。

这对生产环境意义重大。你现有的 v5-text 索引不受影响。相同查询、相同向量，逐字节相同。你没有重新嵌入任何一篇文档，就获得了图像、音频和视频检索。这才是真正的解锁：把多模态检索当作即插即用的升级，而不是一个迁移项目。

[jina-embeddings-v5-omni-small](https://jina.ai/?sui&model=jina-embeddings-v5-omni-small) 是 2B 参数以下表现最佳的开源权重 omni embedding 模型。[jina-embeddings-v5-omni-nano](https://jina.ai/?sui&model=jina-embeddings-v5-omni-nano) 则在 0.9B 规模上做到了这一点。两者现已上线 [Hugging Face](https://huggingface.co/collections/jinaai/jina-embeddings-v5-omni-69f336b985c156b1d757029e)、[Jina Search Foundation API](https://jina.ai/embeddings)，并作为原生推理端点提供于 Elasticsearch。
