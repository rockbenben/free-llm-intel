---
vendor: huggingface
title: NeoMME：一个高效的多模态原生多语言编码器
original_title: NeoMME: an efficient Multimodal-native and Multilingual Encoder
url: https://huggingface.co/blog/Hcompany/neomme
date: 2026-09-10
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

[![Hugging Face](https://img.shields.io/badge/Collection-FFD21E?style=for-the-badge&logo=huggingface&logoColor=000)](https://hf.co/collections/Hcompany/neomme) [![Hugging Face Paper](https://img.shields.io/badge/HF_Paper-FFD21E?style=for-the-badge&logo=huggingface&logoColor=000)](https://huggingface.co/papers/2609.01657) [![arXiv](https://img.shields.io/badge/arXiv-2609.01657-b31b1b.svg?style=for-the-badge)](https://arxiv.org/abs/2609.01657)

![NeoMME logo](https://github.com/tonywu71/colpali-cookbooks/blob/6ef1332da6bcb48c7ef1f19b25bfa555be7031a8/assets/neomme/neomme_logo.webp?raw=true)

## TL;DR

我们推出 ***NeoMME***——一个 260M 与 800M 的多语言多模态编码器家族。与许多生成式视觉语言模型不同，*NeoMME* 不使用单独预训练的视觉塔，也不使用因果语言模型。单个双向 Transformer 同时处理文本 token 和原始图像 patch，整个模型以 masked discrete-diffusion 目标从头训练。

我们用 ColPali 的页面图像方法对 *NeoMME* 做了视觉文档检索微调。*NeoMME*-Retriever 一次前向传播即可同时返回 dense 和 late-interaction 嵌入。在 nDCG@10 与模型尺寸的维度上，两个尺寸都位于 ViDoRe v3 的 Pareto 前沿。在 NVIDIA L40S GPU 上以匹配的 2048×2048 图像输入尺寸，260M 模型每秒编码约 51 页，约为 ColModernVBERT 吞吐的两倍。层级 token 池化与非对称量化把 late-interaction 索引的存储从每页约 1.5 MB 压到 6 kB（缩小 255 倍），同时保留基线 nDCG@10 的 95% 以上。

*NeoMME* 已可在 Hugging Face Transformers 中使用。我们以 Apache 2.0 许可证发布全部模型 checkpoints。

- 🤗 [*NeoMME* 合集](https://hf.co/collections/Hcompany/neomme)
- 📄 [技术报告](https://huggingface.co/papers/2609.01657)
- 🔎 [Visual RAG demo](https://huggingface.co/spaces/tonywu71/neomme-retriever-demo)

## 为什么又需要一个多模态编码器？

许多近期的视觉文档检索器都是从预训练的生成式视觉语言模型改造而来。一个独立预训练的视觉编码器产出视觉特征，由一个 projector 映射进语言模型的输入空间，随后一个因果 decoder 处理合并后的图像与文本表征。检索、分类和 token 标注并不自回归地生成文本，因此不需要因果 decoder，也不需要这种架构带来的参数与计算开销。

[ModernBERT](https://huggingface.co/blog/modernbert) 把高效的架构与训练改进带给了双向编码器。就视觉文档检索而言，[ModernVBERT](https://huggingface.co/blog/paultltc/modernvbert) 采用双向的 ModernBERT 风格文本编码器，同时保留了独立的预训练 SigLIP2 视觉塔。我们想把这件事推得更远：设计并训练一个多模态编码器，而不必背负 VLM 的参数与计算开销。

***NeoMME***（读作 "nee-oh-me"，IPA /ˈniː.oʊ.mi/）是一个多语言、多模态基础编码器，用单个 Transformer 编码器为输入文本和/或图像生成向量表征。它不基于任何已有的预训练视觉塔、文本编码器或文本解码器。

不同于双塔和 VLM 编码器，NeoMME 在单个双向 Transformer 中处理图像 patch 与文本 token，没有预训练视觉塔，也没有预训练文本编码器或解码器。

图像与文本使用同一计算路径，因此 *NeoMME* 可以更轻松地跨两种模态支持预训练、微调、并行化与服务。

## *NeoMME* 编码器骨干

### 图像与文本共用一个 Transformer

*NeoMME* 有两个尺寸：[260M](https://huggingface.co/Hcompany/NeoMME-260M) 和 [800M](https://huggingface.co/Hcompany/NeoMME-800M)。两者共享同一架构：

- **原生多模态输入**：文本输入使用因子化 token embedding；图像被切成 32×32 不重叠 patch 的网格，用一个小 MLP 投影。两者进入同一个 Transformer 编码器。
- **动态图像分辨率**：图像保持其宽高比和尺寸。这让模型可以对一张高分辨率、信息密集的文档页使用比内容较少的小图像更多的 token。
- **长双向上下文**：两个模型的上下文长度都是 16,384 token（足以容纳至多两张标准 3840×2160 的 4K UHD 图像）。多数层使用对称滑动窗口注意力，而每第六层和最后一层使用全局注意力。
- **现代化的编码器栈**：*NeoMME* 使用了近期编码器改进，如 grouped-query attention、query-key 归一化、gated attention、2D 旋转位置编码、squared-ReLU MLP 等。
- **多语言文本**：我们从零用多语言文本、代码、数学和机器生成的图像转录文本训练了一个 13.1 万词表的 BPE tokenizer。

NeoMME 编码器栈中滑动窗口层与全局注意力层交替排布。

### 通过掩码文本从图像中学习

我们从头预训练 *NeoMME*，把它当作离散 masked-diffusion 文本去噪器。对每个纯文本样本，我们在 0 到 1 之间均匀采样一个破坏率，然后每个符合条件的文本 token 以该速率独立地被 mask。

多模态样本的破坏率在 0.3 到 1 之间。当 *NeoMME* 重建被 mask 的文本时，图像 patch 保持可见。轻度 mask 时，模型常常只靠周边文本就能还原缺失的词。例如，即便没有图像，"cat" 也是 "The [MASK] sat on the mat" 的合理补全。但高强度 mask 迫使模型在几乎没有来自未 mask 文本 token 信号的情况下，学习扎根于图像的描述。

更高的文本破坏率移除了「只靠语言」的捷径，促使 NeoMME 利用可见的图像证据。

预训练混合了多语言文本、代码、数学、自然图像和文档图像。每个模型处理约 5,240 亿打包输入 token，其中 2,900 亿来自纯文本样本。相比 ModernBERT 2 万亿的训练 token 预算，这份文本预算相对较小。因此我们选择 NorMuon 优化器来提升训练期间的数据效率。

## *NeoMME*-Retriever

为了让骨干在下游有有意义的评估，我们用 [ColPali](https://huggingface.co/blog/manu/colpali) 提出的页面图像方法，对 *NeoMME* 做视觉文档检索微调。传统基于文本的检索是检索文本块，而 *NeoMME*-Retriever 直接对文档页面截图排名，绕开了从 PDF 提取文本所需的全部 OCR 预处理步骤。把页面当作图像，保留了布局、图表、表格、字体类型与大小等即使完美的 OCR 模型也无法捕捉的视觉线索。

### 面向 dense 与 late-interaction 检索的双头设计

*NeoMME*-Retriever 复用 *NeoMME* 骨干，但在其上为检索增加两个联合训练的头：

- dense 头把骨干的 hidden state 向量平均成一个归一化向量（mean pooling）。dense 嵌入是当今最常见的：它们紧凑，并且天然配合近似最近邻（ANN）技术做快速检索。
- late-interaction 头把骨干输出 hidden states 中的每个文本 token 或图像 patch 投影为 128 维的归一化向量。相比 dense 嵌入，更细的粒度保留了单个查询 token 与图像区域之间的局部匹配。

两个 *NeoMME* 尺寸的 late-interaction 与 dense 检索头。

> 在 ColBERT 中提出 late-interaction 的 Omar Khattab 解释了为什么这个词比 "multi-vector" 更精确：它描述的是打分函数的粒度与可学习性，而不只是存储向量的数量。
> 想更多了解 late-interaction，我们推荐 Amélie Chatelain 的这篇速成教程。

一次 *NeoMME*-Retriever 前向传播同时返回两种表征，让你无论什么用例和基础设施都有灵活选择。一般情况下我们推荐使用 late-interaction 嵌入，因为它们更强大，并且可以方便地配合 [NextPlaid](https://github.com/lightonai/next-plaid) 这类开源库。不过，如果你有非常大的语料库，可以用 *NeoMME*-Retriever 跑一次前向传播得到 dense 嵌入、通过 ANN 索引检索少量文档，再用 late-interaction 对检索到的候选重排。

### 紧凑模型尺寸下的有竞争力检索

我们报告 ViDoRe v3 上的 nDCG@10。*NeoMME*-Retriever-260M 达到 0.523，是评测模型中严格小于 800M 参数里的最高分，比 ColQwen2.5 只差 0.002 nDCG@10，而参数量约为其 1/14。*NeoMME*-Retriever-800M 达到 0.556，与同尺寸的 [Vultron Retriever Flash (0.8B)](https://huggingface.co/vultr/VultronRetrieverFlash-Qwen3.5-0.8B) 相差 0.009 nDCG@10。两个 *NeoMME*-Retriever 模型都位于模型尺寸 Pareto 前沿上。

ViDoRe v3 nDCG@10 对比模型尺寸。

ViDoRe v1 和 v2 使用 nDCG@5。在两个基准上，*NeoMME*-Retriever-260M 都超过 ColModernVBERT 和大它一倍的 ColSmol-500M。*NeoMME*-Retriever-800M 超过 ColPali v1.3，而参数量少 3.6 倍。

| 模型详情 | ViDoRe (nDCG@*k*) |  |  |  |
| --- | --- | --- | --- | --- |
| 模型 | 参数量 | v3 (@10) | v2 (@5) | v1 (@5) |
| <300M |  |  |  |  |
| [ColModernVBERT](https://huggingface.co/ModernVBERT/colmodernvbert) | 250M | 0.261† | 0.407‡ | 0.806‡ |
| [ColSmol-256M](https://huggingface.co/vidore/colSmol-256M)† | 256M | 0.207 | 0.348 | 0.797 |
| [*NeoMME*-260M](https://huggingface.co/Hcompany/NeoMME-260M-Retriever)‡ | 260M | **0.523** | **0.522** | **0.860** |
| 300M 到 1B |  |  |  |  |
| [ColSmol-500M](https://huggingface.co/vidore/colSmol-500M) | 500M | 0.340‡ | 0.455† | 0.825† |
| [Vultron Flash](https://huggingface.co/vultr/VultronRetrieverFlash-Qwen3.5-0.8B)† | 850M | **0.565** | **0.604** | **0.882** |
| [*NeoMME*-800M](https://huggingface.co/Hcompany/NeoMME-800M-Retriever)‡ | 800M | 0.556 | 0.559 | 0.874 |
| >1B |  |  |  |  |
| [ColQwen2.5-v0.2](https://huggingface.co/vidore/colqwen2.5-v0.2)† | 3.75B | **0.524** | **0.601** | **0.895** |
| [ColPali v1.3](https://huggingface.co/vidore/colpali-v1.3)† | 2.92B | 0.430 | 0.547 | 0.848 |

† 分数来自 MTEB。‡ 我们自己的评测结果。

### 让高分辨率的 late-interaction 检索切实可行

late-interaction 的存储随输出嵌入中向量数量线性增长。更高分辨率的图像包含更多 patch，因此产出更大的嵌入。例如一张 2048×2048 的方形页面，用 *NeoMME*-Retriever 会产出包含 4,200 个向量的嵌入，float32 下约 2.1 MB。在 ViDoRe v3 基准上，实测平均约每文档 1.5 MB。

为压缩 late-interaction 索引的存储足迹，我们结合两种互补的压缩方法：

- [层级 token 池化（Hierarchical token pooling）](https://www.answer.ai/posts/colbert-pooling.html)在给定多向量嵌入中聚类相似的文档向量，用每簇的均值替代该簇，从而减少每页存储的向量数。
- [非对称量化（Asymmetric quantization）](https://www.mixedbread.com/blog/asymmetric-quant)把文档嵌入量化为 int8 或二值。由于查询嵌入不被存储、只是即时生成，它们可以保持更高精度。

我们在 ViDoRe v3 上测试了这个配置。池化因子 10、查询与文档均为 int8 时，存储从每页约 1.5 MB 降到 39 kB，压缩 39 倍，同时保留基线 nDCG@10 的 99% 以上。更激进的配置用池化因子 8、int8 查询、二值文档：每页 6 kB（缩小 255 倍），并保留原始检索质量的 95% 以上。

NeoMME-260M 在 ViDoRe v3 上 late-interaction 索引的质量-存储前沿。标签显示池化因子、保留质量、压缩率与存储。

用户可以基于存储预算和所需检索质量，从该前沿上选择一个压缩档位。

#### 快速推理，更便宜的多模态语料索引

在能搜索语料之前，检索模型必须先把你的文档转成嵌入，存进 Qdrant、Weaviate 或 Milvus 这样的向量库。编码更快意味着构建索引和添加新文档更快，从而降低所需的 GPU 在线时长和计算成本。

于是我们测量了 *NeoMME*-Retriever 与其他多模态文档检索器的图像编码速度。我们使用预处理后的图像张量，并为每个模型、每种图像尺寸分别校准 batch size。在一块 NVIDIA L40S 上、以匹配的 2048×2048 输入尺寸，*NeoMME*-Retriever-260M 每秒编码约 51 页，接近 ColModernVBERT 26 页/秒的两倍。在较小的输入图像上，260M 和 800M 两个 *NeoMME*-Retriever 模型也都快于其他对比模型。

一块 NVIDIA L40S 上按检索器与输入分辨率统计的文档编码吞吐。

### 亲自试试 *NeoMME*-Retriever！

*NeoMME*-Retriever（[260M](https://huggingface.co/Hcompany/NeoMME-260M-Retriever) 和 [800M](https://huggingface.co/Hcompany/NeoMME-800M-Retriever)）会一并返回 dense 与多向量嵌入。下面的例子用 MeanMaxSim late interaction 和 dense 余弦相似度，把两条文本查询对两张文档页面图像打分。

点击展开完整的 🤗 transformers 示例片段

```
# accelerate is an optional dependency needed only when using device_map="auto".
pip install -U accelerate "transformers @ git+https://github.com/huggingface/transformers.git@main" "sentence-transformers>=6.0.0"
```

```
from typing import Any, Literal

import requests
import torch
from PIL import Image
from sentence_transformers.util import cos_sim, mean_maxsim

from transformers import BatchFeature, NeoMMEForRetrieval, NeoMMEProcessor


def encode(
    messages: list[list[dict[str, Any]]],
    task: Literal["query", "document"],
) -> BatchFeature:
    return processor.apply_chat_template(
        messages,
        task=task,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
        processor_kwargs={"padding": "longest"},
    )


model_name = "Hcompany/NeoMME-260M-Retriever"
processor = NeoMMEProcessor.from_pretrained(model_name)
model = NeoMMEForRetrieval.from_pretrained(model_name, device_map="auto")

# Document images (our corpus)
image_urls = [
    "https://github.com/tonywu71/colpali-cookbooks/blob/6ef1332da6bcb48c7ef1f19b25bfa555be7031a8/examples/data/shift_kazakhstan.jpg?raw=true",
    "https://github.com/tonywu71/colpali-cookbooks/blob/6ef1332da6bcb48c7ef1f19b25bfa555be7031a8/examples/data/energy_electricity_generation.jpg?raw=true",
]
documents = [Image.open(requests.get(url, stream=True).raw) for url in image_urls]

# Queries
queries = [
    "Quelle partie de la production pétrolière du Kazakhstan provient de champs en mer ?",
    "Which hour of the day had the highest overall electricity generation in 2019?",
]

document_messages = [
    [{"role": "user", "content": [{"type": "image", "image": document}]}] for document in documents
]
query_messages = [[{"role": "user", "content": query}] for query in queries]

inputs_documents = encode(document_messages, "document").to(model.device)
inputs_text = encode(query_messages, "query").to(model.device)

with torch.inference_mode():
    document_outputs = model(**inputs_documents)
    query_outputs = model(**inputs_text)

late_scores = mean_maxsim(
    query_outputs.embeddings,
    document_outputs.embeddings,
    a_mask=inputs_text["attention_mask"],
    b_mask=inputs_documents["attention_mask"],
)
dense_scores = cos_sim(query_outputs.dense_embeddings, document_outputs.dense_embeddings)

# Expected: late_scores[0, 0] > late_scores[0, 1] and late_scores[1, 1] > late_scores[1, 0].
print(late_scores, dense_scores)
```

### 用 Sentence Transformers 微调

我们提供了独立的 [dense](https://huggingface.co/Hcompany/NeoMME-260M-Retriever-ST-dense) 与 [late-interaction](https://huggingface.co/Hcompany/NeoMME-260M-Retriever-ST-late) checkpoints，用于在 [Sentence Transformers v6](https://huggingface.co/blog/multi-vector-encoder) 中微调。遵循 ModernBERT 等文本编码器的相同模式，Sentence Transformers 通过 [`NeoMMEModel`](https://huggingface.co/docs/transformers/main/en/model_doc/neomme#transformers.NeoMMEModel) 加载骨干，而不是双头的 [`NeoMMEForRetrieval`](https://huggingface.co/docs/transformers/main/en/model_doc/neomme#transformers.NeoMMEForRetrieval) 类。Sentence Transformers 目前每个模型只支持一个检索头，所以每个 checkpoint 让你独立微调 dense 或 late-interaction 头。要一起训练两个头，请用 `NeoMMEForRetrieval` 配合自定义 `Trainer`。

### 从检索到 Visual RAG

视觉文档检索可以作为视觉检索增强生成（RAG）系统的第一阶段。文本 RAG 检索的是提取出的文本块，而视觉 RAG 检索原始页面图像并把它们发给视觉语言模型。模型因此可以利用表格、图形、示意图和页面布局——这些在文本提取时可能被压平或丢弃。视觉 RAG 的工作原理：

- 索引：把每个 PDF 页面转成图像，用检索模型生成嵌入，并把嵌入存入向量库。
- 检索：用同一模型为用户查询生成嵌入，检索 top-k 最相关页面。
- 生成：在聊天消息中把图像追加在查询之后（*e.g.*，`{query}{img_1}{img_2}...{img_k}`），发给 VLM 生成答案。

你可以在我们的 HF Space 中直接用 *NeoMME*-Retriever 体验视觉 RAG：🤗 [tonywu71/neomme-retriever-demo](https://huggingface.co/spaces/tonywu71/neomme-retriever-demo)。

## 结论

*NeoMME* 用一个长上下文双向 Transformer 取代了分离的预训练图像与文本编码器。我们从零训练它同时处理多语言文本 token 和原始 32×32 图像 patch。

*NeoMME*-Retriever 是 *NeoMME* 面向视觉文档检索的微调版本。一次前向传播产出 dense 与 late-interaction 两种表征。260M 模型超过所有评测的严格小于 800M 参数的模型，并且在匹配的 2048×2048 输入尺寸下，以约 ColModernVBERT 2 倍的吞吐编码页面。为了削减高分辨率文档下 late-interaction 嵌入庞大的存储足迹，我们试验了层级 token 池化与非对称量化，成功把 late-interaction 嵌入从每页约 1.5 MB 压到 6 kB（255 倍压缩），同时保留基线 nDCG@10 的 95% 以上。

我们发布全部 *NeoMME* 模型 checkpoints 和 day-zero 的 Hugging Face Transformers 实现，让从业者能在我们的成果之上构建高效的多模态、多语言表征模型。

## 致谢

*NeoMME* 始于两个好朋友之间的一次「支线任务」。我们在时间与算力都有限的条件下完成，并决定分享结果，让社区可以在其上继续构建。感谢 H Company 对这项工作的支持，并提供训练 *NeoMME* 所用的算力。

## 引用

```
@misc{lac2026neommesingletowermultimodalnativemultilingual,
      title={NeoMME: A Single-Tower Multimodal-Native Multilingual Foundation Encoder for Efficient Fine-Tuning and Inference},
      author={Aurélien Lac and Tony Wu},
      year={2026},
      eprint={2609.01657},
      archivePrefix={arXiv},
      primaryClass={cs.IR},
      url={https://arxiv.org/abs/2609.01657},
}
```
