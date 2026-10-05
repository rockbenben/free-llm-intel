---
vendor: huggingface
title: Docmatix——面向文档视觉问答的超大规模数据集
original_title: Docmatix
url: https://huggingface.co/blog/docmatix
date: 2025-12-10
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Docmatix——面向文档视觉问答的超大规模数据集

本文由 Andres Marafioti（andito）与 Hugo Laurençon（HugoLaurencon）撰写。

在本博客中，我们发布了 [Docmatix——一个面向文档视觉问答（Document Visual Question Answering, DocVQA）的超大规模数据集](https://huggingface.co/datasets/HuggingFaceM4/Docmatix)，其规模比此前可用的数据集大数百倍。我们用该数据集对 Florence-2 进行微调的消融实验显示，DocVQA 上的性能提升了 20%。

![Example from the dataset](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/docmatix_example.png)
 *数据集中的一条示例*

我们最初萌生创建 Docmatix 的念头，是在开发 [The Cauldron](https://huggingface.co/datasets/HuggingFaceM4/the_cauldron)（一个包含 50 个数据集、用于视觉语言模型（VLM）微调的大型集合）以及 [Idefics2](https://huggingface.co/blog/idefics2) 的过程中。在这一过程中，我们发现了大规模文档视觉问答（DocVQA）数据集在可用性上的显著缺口。我们在 Idefics2 中所依赖的主要数据集是 DocVQA，它包含 10,000 张图像和 39,000 个问答（Q/A）对。即便在该数据集及其他数据集上微调，开源模型与闭源模型之间仍存在较大的性能差距。为解决这一局限，我们很高兴推出 Docmatix——一个包含 240 万张图像、950 万个 Q/A 对的 DocVQA 数据集，这些内容来自 130 万份 PDF 文档。相比以往数据集，规模扩大了 **240 倍**。

![Comparing Docmatix to other DocVQA datasets](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/docmatix_dataset_comp.png)
 *将 Docmatix 与其他 DocVQA 数据集对比*

在这里你可以亲自探索该数据集，看看 Docmatix 中包含的文档类型和问答对。

Docmatix 由 [PDFA 生成——这是一个包含 210 万份 PDF 的大型 OCR 数据集](https://huggingface.co/datasets/pixparse/pdfa-eng-wds)。我们提取 PDFA 的转录文本，并用 [Phi-3-small](https://huggingface.co/microsoft/Phi-3-small-8k-instruct) 模型生成 Q/A 对。为确保数据集质量，我们对生成结果进行了过滤，丢弃了被识别为幻觉的 15% 的 Q/A 对。为此，我们使用正则表达式检测代码，并移除了包含关键词"unanswerable"（无法回答）的答案。数据集为每份 PDF 保留一行。我们将 PDF 以 150 dpi 的分辨率转换为图像，并把处理后的图像上传到 Hugging Face Hub 以便访问。Docmatix 中所有原始 PDF 都能追溯回原始的 PDFA 数据集，从而保证了透明性与可靠性。尽管如此，出于便利我们仍上传了处理后的图像，因为把大量 PDF 转成图像可能是资源密集型的。

![Processing for Docmatix](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/docmatix_processing.png)
 *生成 Docmatix 的处理流水线*

在处理完数据集的第一个小批量后，我们进行了若干消融研究以优化提示词。我们的目标是每页大约生成四对 Q/A。过多的对数意味着它们之间高度重叠，而过少则意味着细节不足。此外，我们力求让答案更像人类的表达，避免过短或过长的回答。我们还优先考虑问题的多样性，确保尽量不重复。有趣的是，当我们引导 [Phi-3 模型](https://huggingface.co/docs/transformers/main/en/model_doc/phi3)基于文档中的具体信息来提问（例如"John Doe 的职位头衔有哪些？"）时，问题的重复率非常低。下图给出了我们分析中的一些关键统计数据：

![Prompt analysis Docmatix](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/docmatix_prompt_analysis.png)
 *按提示词对 Docmatix 的分析*

为评估 Docmatix 的性能，我们用 Florence-2 模型进行了消融研究。我们训练了两个版本的模型用于对比。第一个版本在 DocVQA 数据集上训练了多个 epoch。第二个版本先在 Docmatix 上训练一个 epoch（20% 的图像和 4% 的 Q/A 对），随后在 DocVQA 上再训练一个 epoch，以确保模型能为 DocVQA 评测输出正确的格式。结果十分显著：仅在这一小部分 Docmatix 上训练，就带来了近 20% 的相对提升。此外，0.7B 的 Florence-2 模型表现只比在混合数据集上训练、规模大得多的 8B Idefics2 模型差 5%。

| Dataset | ANSL on DocVQA | model size |
| --- | --- | --- |
| Florence 2 fine-tuned on DocVQA | 60.1 | 700M |
| Florence 2 fine-tuned on Docmatix | 71,4 | 700M |
| Idefics2 | 74,0 | 8B |

## 结论

在本文中，我们介绍了 Docmatix——一个面向 DocVQA 的超大规模数据集。我们展示了借助 Docmatix，在对 Florence-2 微调时可实现 DocVQA 性能 20% 的提升。该数据集应有助于缩小专有 VLM 与开源 VLM 之间的差距。我们鼓励开源社区善用 Docmatix，训练出崭新的、出色的 DocVQA 模型！我们迫不及待想在 🤗 Hub 上看到你的模型！

## 有用资源

- [Docmatix 用于微调 Florence-2 的演示](https://huggingface.co/spaces/HuggingFaceM4/Docmatix-Florence-2)
- [微调 Florence-2 博客](https://huggingface.co/blog/finetune-florence2)
- [微调 Florence-2 Github 仓库](https://github.com/andimarafioti/florence2-finetuning)
- [视觉语言模型详解](https://huggingface.co/blog/vlms)

感谢 merve 和 leo 对本文的审阅以及为本博客制作的缩略图。
