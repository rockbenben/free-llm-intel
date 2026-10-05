---
vendor: jina_ai
title: jina-embeddings-v5-omni: Embeddings for Text, Image, Audio and Video
original_title: 
url: https://jina.ai/news/jina-embeddings-v5-omni-multimodal-embeddings-for-text-image-audio-and-video
date: 2026-05-12
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: e3ad8c157db1
---

star

Featured

Press release

May 12, 2026

# jina-embeddings-v5-omni: Embeddings for Text, Image, Audio and Video

One model, four modalities: text, image, audio, video. Best-in-class omni embeddings in 1.6B and 0.9B.

Jina AI • 7 minutes read

jina-embeddings-v5-omni - a jinaai Collection

Multimodal (text + image + video + audio) embedding models aligned with jina-embeddings-v5-text-*. Two sizes, four task variants each.

a jinaai Collection

jina-embeddings-v5-omni: Text-Geometry-Preserving Multimodal Embeddings via Frozen-Tower Composition

In this work, we introduce frozen-encoder model composition, a novel approach to multimodal embedding models. We build on the VLM-style architecture, in which non-text encoders are adapted to produce input for a language model, which in turn generates embeddings for all varieties of input. We present the result: the jina-embeddings-v5-omni suite, a pair of models that encode text, image, audio, and video input into a single semantic embedding space. Our method is to extend the two Jina Embeddings v5 Text models to support additional media by adding encoders for images and audio. The backbone text embedding models and the added non-text media encoders remain frozen. We only trained the connecting components, representing 0.35% of the total weights of the joint model. Training is therefore much more efficient than full-parameter retraining. Additionally, the language model remains effectively unaltered, producing exactly the same embeddings for text inputs as the Jina Embeddings v5 Text models. Our evaluations show that this approach produces results that are competitive with the state-of-the-art, yielding nearly equal performance to larger multimodal embedding models.

arXiv.org

Florian Hönicke

We are releasing **jina-embeddings-v5-omni**, extending our v5-text embedding models to images, audio, and video. Both models share the same frozen text backbone as v5-text, meaning text embeddings are **identical** - no index rebuild needed. [jina-embeddings-v5-omni-small](https://jina.ai/?sui&model=jina-embeddings-v5-omni-small) scores **53.93** on average across four modalities, matching LCO-7B (54.43) at **5.7x fewer parameters**, while [jina-embeddings-v5-omni-nano](https://jina.ai/?sui&model=jina-embeddings-v5-omni-nano) delivers competitive document retrieval at just 0.95B parameters.

Pareto frontier of all open-weight omni embedding models (supporting text, image, audio, and video).

jina-embeddings-v5-omni-small

(1.57B) matches the average score of LCO-7B (8.93B) while using 5.7x fewer parameters.

jina-embeddings-v5-omni-nano

(0.95B) outperforms LanguageBind (1.14B) by +8.9 points. Baselines: LanguageBind, Omni-Embed-Nemotron-3B, LCO-Embedding-Omni-3B, LCO-Embedding-Omni-7B.

Per-modality breakdown across Text (MMTEB), Image (MIEB), Video (MMEB-Video), and Audio (MAEB).

jina-embeddings-v5-omni-small

leads all omni models on text with 67.0, inheriting

jina-embeddings-v5-text-small

's full quality. On image (56.05), it excels at classification (68.55) and clustering (84.57, best among all models). Audio (51.46) is close to LCO-7B (52.37), with the best audio classification score (55.89). Video (41.20) is the current gap vs LCO-7B (47.41), as temporal reasoning benefits more from end-to-end training.

Per-task performance across 13 task types. Gold stars mark tasks where

jina-embeddings-v5-omni-small

beats the best open-weight baseline (3-9x larger). Wins: image classification (68.55 vs 64.30), image clustering (84.57 vs 83.24), audio classification (55.89 vs 53.39). Main gaps: video retrieval (27.82 vs 58.73) and compositional/VQA (44.23 vs 53.40).

Document retrieval (ViDoRe-in-MIEB).

jina-embeddings-v5-omni-small

at 0.92B active text+image parameters scores 79.08, outperforming LCO-3B (78.24 at 4.07B).

jina-embeddings-v5-omni-nano

scores 70.05 with just 0.31B active parameters, far above LanguageBind (37.33). Nemotron-3B leads at 85.64 but uses 5.1x more parameters.

## [*tag*](https://jina.ai/news/jina-embeddings-v5-omni-multimodal-embeddings-for-text-image-audio-and-video/#architecture)Architecture

v5-omni keeps the v5-text backbone completely frozen and adds pretrained vision and audio encoders connected through small trainable projectors:

- **Vision**: Qwen3.5 vision encoders (adapted from SigLIP2) with 2x2 spatial merge (4x token reduction). We freeze everything except the final projection layer (`fc_vision_2`), which we replace with a randomly initialized layer mapping into the text backbone's hidden dimension.
- **Audio**: Qwen2.5-Omni encoder (adapted from Whisper-large-v3). A single randomly initialized `fc_audio` layer projects the 1280-dimensional output into the text backbone.
- **Video**: Handled as a sequence of visual frames, optionally preceded by an extracted audio segment.

The model inherits v5-text's four task-specific LoRA adapters (retrieval, text-matching, classification, clustering) and trains separate projector weights for each task variant. The architecture is fully modular: text-only deployment loads no vision or audio weights (identical to v5-text footprint), image-only skips audio, full omni loads everything.

v5-omni architecture. Frozen vision and audio encoders feed trainable projectors into the frozen text backbone. Only the projectors (0.35% of total weights) are trained. Task-specific LoRA adapters handle retrieval, classification, clustering, and text-matching.

| Feature | [jina-embeddings-v5-omni-small](https://jina.ai/?sui&model=jina-embeddings-v5-omni-small) | [jina-embeddings-v5-omni-nano](https://jina.ai/?sui&model=jina-embeddings-v5-omni-nano) |
| --- | --- | --- |
| Base Text Model | [jina-embeddings-v5-text-small](https://jina.ai/?sui&model=jina-embeddings-v5-text-small) (Qwen3-0.6B) | [jina-embeddings-v5-text-nano](https://jina.ai/?sui&model=jina-embeddings-v5-text-nano) (EuroBERT-210m) |
| Total Parameters | ~1.56B | ~1.04B |
| Modalities | Text, Image, Audio, Video, PDF | Text, Image, Audio, Video, PDF |
| Embedding Dimensions | 1024 | 768 |
| Matryoshka Dimensions | 32, 64, 128, 256, 512, 768, 1024 | 32, 64, 128, 256, 512, 768 |
| Max Sequence Length | 32768 tokens | 8192 tokens |
| Vision Encoder | Qwen3.5-2B ViT (SigLIP2) | SigLIP2 Base |
| Audio Encoder | Whisper-large-v3 | Whisper-large-v3 |
| Tasks | retrieval, text-matching, classification, clustering | retrieval, text-matching, classification, clustering |
| Text Compatibility | Identical to [jina-embeddings-v5-text-small](https://jina.ai/?sui&model=jina-embeddings-v5-text-small) | Identical to [jina-embeddings-v5-text-nano](https://jina.ai/?sui&model=jina-embeddings-v5-text-nano) |
| Trainable Parameters | ~18M projectors (0.35%) | ~7M projectors (0.35%) |
| Pooling | Last-token | Last-token |
| License | CC BY-NC 4.0 | CC BY-NC 4.0 |

## [*tag*](https://jina.ai/news/jina-embeddings-v5-omni-multimodal-embeddings-for-text-image-audio-and-video/#getting-started)Getting Started

### [*tag*](https://jina.ai/news/jina-embeddings-v5-omni-multimodal-embeddings-for-text-image-audio-and-video/#elasticsearch-elastic-inference-service)Elasticsearch (Elastic Inference Service)

If you are already using `jina-embeddings-v5-text` in Elasticsearch, your existing text indexes work with v5-omni out of the box. The omni models produce **identical embeddings for text inputs** as v5-text - same input, same vector, byte-for-byte. You do not need to re-embed or rebuild any text index. To start searching images, audio, and video alongside your existing text data, simply create a new index with v5-omni and ingest your multimodal content into it.

Create a `semantic_text` index with v5-omni as the inference endpoint. EIS automatically selects the correct LoRA adapter for indexing and retrieval:

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

Ingest text, images (as base64 data URIs), audio, and video into the same field, the same index:

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

Search across all modalities with a single text query:

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

## [*tag*](https://jina.ai/news/jina-embeddings-v5-omni-multimodal-embeddings-for-text-image-audio-and-video/#training)Training

The core idea is *frozen-encoder model composition*: take a strong text embedding model, add pretrained vision and audio encoders, connect them with small trainable projectors, and freeze everything except those projectors. Only 0.35% of total weights are trained, which gives us three properties: (1) text identity preservation - the backbone is unmodified, same input produces identical output; (2) training efficiency - projector-only training is 1.8-3.9x faster with 42-64% less GPU memory; (3) modularity - towers can be loaded independently.

Projector-only training vs full training on 4x H100 GPUs (batch size 256, 15K steps). Audio projector training is particularly efficient: 3.2x faster for small (154 min vs 497 min) and 3.9x faster for nano (112 min vs 441 min). Memory savings of 42-64% come from not storing gradients and optimizer states for frozen encoders.

v5-omni inherits Matryoshka dimension support from v5-text. Image and audio embeddings preserve most quality under truncation, while video degrades more at small dimensions.

Summary: per-modality profile of v5-omni vs the strongest baselines.

jina-embeddings-v5-omni-small

at 1.57B covers text, image, and audio competitively, with video as the remaining gap to close.

## [*tag*](https://jina.ai/news/jina-embeddings-v5-omni-multimodal-embeddings-for-text-image-audio-and-video/#conclusion)Conclusion

The conventional wisdom says multimodal embeddings require training the entire model end-to-end. We disagree. v5-omni freezes the text backbone, trains 0.35% of weights, and matches models 5-7x its size. The lesson: composition beats retraining. A strong text encoder is the hardest part â€“ once you have it, bolting on vision and audio via lightweight projectors is almost free.

This matters for production. Your existing v5-text indexes is untouched. Same query, same vector, byte-for-byte. You just gained image, audio, and video search without re-embedding a single document. That is the real unlock multimodal retrieval as a drop-in upgrade, not a migration project.

[jina-embeddings-v5-omni-small](https://jina.ai/?sui&model=jina-embeddings-v5-omni-small) is the best-performing open-weight omni embedding model under 2B parameters. [jina-embeddings-v5-omni-nano](https://jina.ai/?sui&model=jina-embeddings-v5-omni-nano) does it at 0.9B. Both available now on [Hugging Face](https://huggingface.co/collections/jinaai/jina-embeddings-v5-omni-69f336b985c156b1d757029e), [Jina Search Foundation API](https://jina.ai/embeddings), and as a native inference endpoint in Elasticsearch.

Categories:

star

Featured

Press release

rss_feed

Read more

September 14, 2026 • 9 minutes read

jina-ocr-v1: Faster Document Parsing on Low-Budget GPUs

August 03, 2026 • 11 minutes read

jina-reranker-v3.5: Faster Listwise Reranking with Hybrid Attention and Self-Distillation

February 19, 2026 • 7 minutes read

jina-embeddings-v5-text: New SOTA Small Multilingual Embeddings
