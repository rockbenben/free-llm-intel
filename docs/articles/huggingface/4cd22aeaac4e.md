---
vendor: huggingface
title: Sentence Transformers 加入 Hugging Face！
original_title: Sentence Transformers is joining Hugging Face!
url: https://huggingface.co/blog/sentence-transformers-joins-hf
date: 2025-10-22
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

今天，我们宣布 Sentence Transformers 正从 Iryna Gurevych 领导的达姆施塔特工业大学[通用知识处理（UKP）实验室](https://www.informatik.tu-darmstadt.de/ukp/ukp_home/index.en.jsp)移交至 Hugging Face。Hugging Face 的 [Tom Aarsen](https://huggingface.co/tomaarsen) 自 2023 年底起就已在维护该库，并将继续领导这个项目。在新的归属地，Sentence Transformers 将受益于 Hugging Face 稳健的基础设施——包括持续集成与测试——确保它紧跟信息检索与自然语言处理的最新进展。

[Sentence Transformers](https://sbert.net/)（又名 SentenceBERT 或 SBERT）是一个流行的开源库，用于生成捕捉语义的高质量 embedding。自 2019 年由 Nils Reimers 创建以来，Sentence Transformers 已被研究人员和从业者广泛用于各类自然语言处理（NLP）任务，包括语义搜索、语义文本相似度、聚类与复述挖掘。经过多年由社区、为社区的开发与打磨，[Hugging Face Hub 上公开可用的 Sentence Transformers 模型超过 16,000 个](https://huggingface.co/models?library=sentence-transformers)，每月服务超过一百万独立用户。

*"Sentence Transformers 是一个巨大的成功故事，也是我们实验室围绕全语义相似度计算长期研究的集大成者。Nils Reimers 做出了一个非常及时的发现，产出的不仅是杰出的研究成果，还有一个高度可用的工具。它持续影响着自然语言处理与 AI 领域一代又一代的学生和从业者。我还要感谢所有用户，尤其是贡献者们——没有他们，这个项目就不会是今天的样子。最后，感谢 Tom 和 Hugging Face 把这个项目带向未来。"*

- **Iryna Gurevych 教授**，达姆施塔特工业大学通用知识处理实验室主任

*"我们非常高兴正式欢迎 Sentence Transformers 加入 Hugging Face 家族！过去两年，看到这个项目在 UKP 实验室出色基础和精彩社区的托举下成长为全球大规模采用的成果，令人振奋。这只是开始：我们将持续加倍支持它的成长与创新，同时坚守让它茁壮成长的开放、协作精神。"*

- **Clem Delangue**，Hugging Face 联合创始人兼 CEO

Sentence Transformers 将继续是一个**社区驱动**的**开源**项目，采用与之前相同的**开源许可证（Apache 2.0）**。欢迎并鼓励研究者、开发者与爱好者贡献。项目将继续把透明、协作与广泛可及性放在首位。

## 项目历史

[Sentence Transformers 库](https://github.com/UKPLab/sentence-transformers)由达姆施塔特工业大学通用知识处理（UKP）实验室的 Nils Reimers 博士于 2019 年发布，导师为 Iryna Gurevych 教授。鉴于标准 BERT embeddings 在句子级语义任务中的局限，[Sentence-BERT](https://arxiv.org/abs/1908.10084) 采用孪生网络（Siamese network）架构，产出可用余弦相似度高效比较的、语义有意义的句子嵌入。得益于模块化、开源的设计，以及在语义文本相似度、聚类、信息检索等任务上的强劲实证表现，该库迅速成为 NLP 研究工具箱的标配，衍生出一系列依赖高质量句子表征的后续研究与真实应用。

2020 年，库中加入多语言支持，把句子嵌入扩展到**400 多种语言**。2021 年，在 Nandan Thakur 与 Johannes Daxenberger 博士的贡献下，库扩展支持用 Cross Encoder 与 Sentence Transformer 模型做句对打分。Sentence Transformers 还与 Hugging Face Hub 集成（v2.0）。四年多时间里，UKP 实验室团队作为社区驱动的开源项目维护该库，并持续提供研究驱动的革新。在此期间，项目开发得益于德国研究基金会（DFG）、德国联邦教育与研究部（BMBF）、黑森州高等教育研究艺术部（HMWK）给予 Gurevych 教授的资助。

2023 年底，来自 Hugging Face 的 Tom Aarsen 接手了库的维护，为 Sentence Transformer 模型引入现代化训练（[v3.0](https://huggingface.co/blog/train-sentence-transformers)），并改进了 Cross Encoder（[v4.0](https://huggingface.co/blog/train-reranker)）与 Sparse Encoder（[v5.0](https://huggingface.co/blog/train-sparse-encoder)）模型。

## 致谢

由 Iryna Gurevych 教授领导的达姆施塔特工业大学通用知识处理（UKP）实验室，在自然语言处理（NLP）与机器学习研究方面享有国际声誉。实验室在表征学习、大语言模型与信息检索领域有大量开创性工作记录，在顶级会议与期刊发表了众多论文。除 Sentence Transformers 外，UKP 实验室还开发了诸多被广泛使用的数据集、基准与开源工具，同时支撑学术研究与真实应用。

Hugging Face 要感谢 UKP 实验室以及所有历任贡献者，特别是 Nils Reimers 博士与 Iryna Gurevych 教授——感谢他们对项目的付出，以及把维护乃至管理托付给我们。我们也感谢由研究者、开发者与从业者组成的社区：他们通过贡献模型、报告 bug、提出功能请求、改进文档和实际落地应用，成就了该库的成功。我们很高兴能在 UKP 实验室奠定的坚实基础上继续建设，与社区一起进一步推动 Sentence Transformers 的能力边界。

## 快速开始

给刚接触 Sentence Transformers、或想探索其能力的朋友：

- **文档**：[https://sbert.net](https://sbert.net)
- **GitHub 仓库**：[https://github.com/huggingface/sentence-transformers](https://github.com/huggingface/sentence-transformers)
- **Hugging Face Hub 上的模型**：[https://huggingface.co/models?library=sentence-transformers](https://huggingface.co/models?library=sentence-transformers)
- **快速上手教程**：[https://sbert.net/docs/quickstart.html](https://sbert.net/docs/quickstart.html)

## 最近的 Sentence Transformers 博文

自 Hugging Face 接手维护以来最重要的更新，按时间顺序：

- [Training and Finetuning Embedding Models with Sentence Transformers](https://huggingface.co/blog/train-sentence-transformers)：稠密 embedding 模型的现代训练 API。
- [Training and Finetuning Reranker Models with Sentence Transformers](https://huggingface.co/blog/train-reranker)：Cross Encoder（重排器）模型对应的训练 API。
- [Training and Finetuning Sparse Embedding Models with Sentence Transformers](https://huggingface.co/blog/train-sparse-encoder)：稀疏编码器（SPLADE）模型对应的训练 API。
- [Multimodal Embedding & Reranker Models with Sentence Transformers](https://huggingface.co/blog/multimodal-sentence-transformers)：用同一套 API 支持文本、图像、音频与视频模型。
- [Training and Finetuning Multimodal Embedding & Reranker Models with Sentence Transformers](https://huggingface.co/blog/train-multimodal-sentence-transformers)：多模态推理博文配套的训练文章。

相关技术主题文章：

- [🪆 Introduction to Matryoshka Embedding Models](https://huggingface.co/blog/matryoshka)：可截断的 embeddings。
- [Train 400x faster Static Embedding Models with Sentence Transformers](https://huggingface.co/blog/static-embeddings)：无注意力、对 CPU 友好的模型。
- [Binary and Scalar Embedding Quantization for Significantly Faster & Cheaper Retrieval](https://huggingface.co/blog/embedding-quantization)：训练后的 embedding 向量压缩。
