---
vendor: huggingface
title: 嵌入入门
original_title: Getting Started With Embeddings
url: https://huggingface.co/blog/getting-started-with-embeddings
date: 2026-06-01
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: ed1bdd5e465f
---

# 嵌入入门

配套 Notebook 教程点这里：[ ![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg) ](https://colab.research.google.com/github/huggingface/blog/blob/main/notebooks/80_getting_started_with_embeddings.ipynb)

## 理解嵌入

嵌入（embedding）是一段信息的数值化表示，这段信息可以是文本、文档、图像、音频等。这个表示 captures 被嵌入内容的语义，因此能胜任大量工业应用。

对于文本 "What is the main benefit of voting?"，这句话的嵌入可以在向量空间里用一个 384 位的列表表示（例如 [0.84, 0.42, ..., 0.02]）。既然这个列表捕捉了含义，我们就能做很多有意思的事——比如计算不同嵌入之间的距离，判断两句话的语义匹配程度。

嵌入并不限于文本！你也可以为一张图像创建嵌入（例如一个 384 位的列表），再拿它和文本嵌入比较，判断某句话是否在描述这张图。这正是一些强大的图像搜索、分类、描述系统背后的概念！

嵌入是怎么生成的？一个叫 [Sentence Transformers](https://www.sbert.net/index.html) 的开源库让你免费为图像和文本创建最先进（SoTA）的嵌入。本文就用这个库做示例。

## 嵌入有什么用？

> "[...] 一旦你理解了这件 ML 多面手（嵌入），你就能构建从搜索引擎、推荐系统到聊天机器人在内的各种应用。你不必是懂 ML 的数据科学家，也不需要海量标注数据集。" —— Dale Markowitz，Google Cloud

一旦信息（一个句子、一份文档、一张图）被嵌入，创造力就开始了；不少有趣的工业应用都在用嵌入。例如，Google 搜索用嵌入来[做文本对文本、文本对图像的匹配](https://cloud.google.com/blog/topics/developers-practitioners/meet-ais-multitool-vector-embeddings)；Snapchat 用它们来"[把对的广告在合适的时间投给合适的用户](https://eng.snap.com/machine-learning-snap-ad-ranking)"；Meta（Facebook）则把它们用于[社交搜索](https://research.facebook.com/publications/embedding-based-retrieval-in-facebook-search/)。

这些公司能从嵌入获得智能之前，得先把自己的信息嵌入进去。被嵌入的数据集能让算法快速搜索、排序、分组等等。不过这件事可能既贵又在技术上复杂。在这篇文章里，我们用简单的开源工具演示嵌入和分析数据集可以有多容易。

## 开始上手嵌入

我们来做一个小的常见问题（FAQ）引擎：接收用户查询，找出最相似的 FAQ。我们使用[美国社会保障署 Medicare 常见问题](https://faq.ssa.gov/en-US/topic/?id=CAT-01092)。

但第一步要先把数据集嵌入（其他文章里 encode 和 embed 常混用）。Hugging Face Inference API 让我们一个简短的 POST 调用就能嵌入数据集。

由于嵌入捕捉了问题的语义，我们可以比较不同嵌入、看它们彼此有多不同或多相似。得益于此，你可以找到与某个查询最接近的嵌入——等价于找出最相似的 FAQ。更详细解释这个机制请看我们的[语义搜索教程](https://huggingface.co/spaces/sentence-transformers/embeddings-semantic-search)。

简单说，我们要：

- 用 Inference API 嵌入 Medicare 的 FAQ
- 把嵌入后的问题上传到 Hub 免费托管
- 把客户查询与嵌入数据集比较，找出最相似的 FAQ

## 1. 嵌入数据集

第一步是选一个现成的预训练模型来生成嵌入。我们可以从 [Sentence Transformers 库](https://huggingface.co/sentence-transformers)里挑。这里选用 ["sentence-transformers/all-MiniLM-L6-v2"](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)，它小而强。后续文章我们会分析其他模型及其取舍。

登录 Hub。你需要在[账号设置](http://hf.co/settings/tokens)里创建一个 write token。我们把 write token 存进 `hf_token`。

```
model_id = "sentence-transformers/all-MiniLM-L6-v2"
hf_token = "get your token in http://hf.co/settings/tokens"
```

要生成嵌入，可以用 `https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}` 端点，配上 header `{"Authorization": f"Bearer {hf_token}"}`。下面这个函数接收一个含文本的字典，返回一个嵌入列表。

```
import requests

api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
headers = {"Authorization": f"Bearer {hf_token}"}
```

第一次生成嵌入时，API 返回可能要一会儿（约 20 秒）。我们用 `retry` 装饰器（`pip install retry` 安装），如果第一次 `output = query(dict(inputs = texts))` 不成功，等 10 秒再重试三次。之所以这样，是因为第一次请求时模型需要被下载并安装到服务器上，但之后的调用会快得多。

```
def query(texts):
    response = requests.post(api_url, headers=headers, json={"inputs": texts, "options":{"wait_for_model":True}})
    return response.json()
```

当前 API 并不强制执行严格的速率限制，而是由 Hugging Face 在所有可用资源间均衡负载，偏爱平稳的请求流。如果你需要嵌入大量文本或图像，[Hugging Face Accelerated Inference API](https://huggingface.co/docs/api-inference/index) 能加速推理，还能让你在 CPU 与 GPU 之间选择。

```
texts = ["How do I get a replacement Medicare card?",
        "What is the monthly premium for Medicare Part B?",
        "How do I terminate my Medicare Part B (medical insurance)?",
        "How do I sign up for Medicare?",
        "Can I sign up for Medicare Part B if I am working and have health insurance through an employer?",
        "How do I sign up for Medicare Part B if I already have Part A?",
        "What are Medicare late enrollment penalties?",
        "What is Medicare and who can get it?",
        "How can I get help with my Medicare Part A and Part B premiums?",
        "What are the different parts of Medicare?",
        "Will my Medicare premiums be higher because of my higher income?",
        "What is TRICARE ?",
        "Should I sign up for Medicare Part B if I have Veterans' Benefits?"]

output = query(texts)
```

你会收到一个列表的列表作为响应，每个列表包含一条 FAQ 的嵌入。模型 ["sentence-transformers/all-MiniLM-L6-v2"](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) 把输入问题编码成了 13 个各自 384 维的嵌入。我们把列表转成形状 (13x384) 的 Pandas `DataFrame`。

```
import pandas as pd
embeddings = pd.DataFrame(output)
```

它看起来接近这样一个矩阵：

```
[[-0.02388945  0.05525852 -0.01165488 ...  0.00577787  0.03409787  -0.0068891 ]
 [-0.0126876   0.04687412 -0.01050217 ... -0.02310316 -0.00278466   0.01047371]
 [ 0.00049438  0.11941205  0.00522949 ...  0.01687654 -0.02386115   0.00526433]
 ...
 [-0.03900796 -0.01060951 -0.00738271 ... -0.08390449  0.03768405   0.00231361]
 [-0.09598278 -0.06301168 -0.11690582 ...  0.00549841  0.1528919   0.02472013]
 [-0.01162949  0.05961934  0.01650903 ... -0.02821241 -0.00116556   0.0010672 ]]
```

## 2. 在 Hugging Face Hub 上免费托管嵌入

🤗 Datasets 是一个快速访问和共享数据集的库。我们用用户界面（UI）把嵌入数据集托管到 Hub 上，之后任何人都能一行代码加载它。你也可以用终端共享数据集，步骤见[文档](https://huggingface.co/docs/datasets/share#share)。本文的[配套 notebook](https://colab.research.google.com/github/huggingface/blog/blob/main/notebooks/80_getting_started_with_embeddings.ipynb) 里会用终端来共享数据集。想跳过本节，可以直接看已嵌入 FAQ 的 [`ITESM/embedded_faqs_medicare` 仓库](https://huggingface.co/datasets/ITESM/embedded_faqs_medicare)。

首先把嵌入从 Pandas `DataFrame` 导出为 CSV。你也可以用任何你喜欢的方式保存数据集，例如 zip 或 pickle——不一定要用 Pandas 或 CSV。由于我们的嵌入文件不大，存成 CSV 即可，它很容易被下一节要用的 `datasets.load_dataset()` 函数自动推断（见 [Datasets 文档](https://huggingface.co/docs/datasets/about_dataset_load#build-and-load)），也就是说我们不需要写加载脚本。文件名保存为 `embeddings.csv`。

```
embeddings.to_csv("embeddings.csv", index=False)
```

按以下步骤把 `embeddings.csv` 托管到 Hub。

- 在 [Hub UI](https://huggingface.co/) 右上角点击你的用户名。
- 用 "New dataset" 创建一个数据集。

[![](https://huggingface.co/blog/assets/80_getting_started_with_embeddings/SelectDataset.png)](https://huggingface.co/blog/assets/80_getting_started_with_embeddings/SelectDataset.png)

- 选择 Owner（组织或个人）、名称和数据集许可证，选择私有还是公开。创建数据集。

[![](https://huggingface.co/blog/assets/80_getting_started_with_embeddings/createDataset.png)](https://huggingface.co/blog/assets/80_getting_started_with_embeddings/createDataset.png)

- 进入 "Files" 标签（见下图），点击 "Add file"，再点 "Upload file"。

[![](https://huggingface.co/blog/assets/80_getting_started_with_embeddings/AddFile.png)](https://huggingface.co/blog/assets/80_getting_started_with_embeddings/AddFile.png)

- 最后，拖拽或上传数据集，提交变更。

[![](https://huggingface.co/blog/assets/80_getting_started_with_embeddings/UploadFile.png)](https://huggingface.co/blog/assets/80_getting_started_with_embeddings/UploadFile.png)

现在数据集已免费托管在 Hub 上。你（或你愿意分享嵌入的任何人）可以很快把它加载出来。下面来看怎么做。

## 3. 获取与查询最相似的常见问题

假设一位 Medicare 客户问："How can Medicare help me?"。我们要**找出**我们的 FAQ 中哪条最能回答这个查询。方法是为查询生成一个能代表其语义的嵌入，再把它与 FAQ 数据集中的每个嵌入比较，找出向量空间中离查询最近的那个。

用 `pip install datasets` 安装 🤗 Datasets 库。然后从 Hub 加载嵌入数据集并转成 PyTorch `FloatTensor`。注意这不是操作 `Dataset` 的唯一方式——例如也可以用 NumPy、Tensorflow 或 SciPy（参见[文档](https://huggingface.co/docs/datasets/loading)）。想拿真实数据集练手，[`ITESM/embedded_faqs_medicare`](https://huggingface.co/datasets/ITESM/embedded_faqs_medicare) 仓库里有嵌入好的 FAQ，或者用本文的[配套 notebook](https://colab.research.google.com/github/huggingface/blog/blob/main/notebooks/80_getting_started_with_embeddings.ipynb)。

```
import torch
from datasets import load_dataset

faqs_embeddings = load_dataset('namespace/repo_name')
dataset_embeddings = torch.from_numpy(faqs_embeddings["train"].to_pandas().to_numpy()).to(torch.float)
```

用前面定义的 query 函数嵌入客户的问题，并转成 PyTorch `FloatTensor` 以便高效运算。注意，嵌入数据集加载后，也可以用 [faiss 库](https://github.com/facebookresearch/faiss)调用 `Dataset` 的 `add_faiss_index` 和 `search` 方法来找出与嵌入查询最近的 FAQ。[这里有一份替代方案的不错教程](https://huggingface.co/docs/datasets/faiss_es)。

```
question = ["How can Medicare help me?"]
output = query(question)

query_embeddings = torch.FloatTensor(output)
```

可以用 Sentence Transformers 库里的 `util.semantic_search` 函数找出哪些 FAQ 离用户查询最近（最相似）。该函数默认用余弦相似度衡量嵌入间的接近程度。不过也可以用其他度量向量空间中两点距离的函数，例如点积。

用 `pip install -U sentence-transformers` 安装 `sentence-transformers`，然后查找与查询最相似的前 5 条 FAQ。

```
from sentence_transformers.util import semantic_search

hits = semantic_search(query_embeddings, dataset_embeddings, top_k=5)
```

`util.semantic_search` 计算 13 条 FAQ 各自与客户查询的接近程度，返回一个字典列表，包含排名靠前的 `top_k` 条 FAQ。`hits` 长这样：

```
[{'corpus_id': 8, 'score': 0.75653076171875},
 {'corpus_id': 7, 'score': 0.7418993711471558},
 {'corpus_id': 3, 'score': 0.7252674102783203},
 {'corpus_id': 9, 'score': 0.6735571622848511},
 {'corpus_id': 10, 'score': 0.6505177617073059}]
```

`corpus_id` 的值让我们可以索引第一部分定义的 `texts` 列表，取出最相似的前 5 条 FAQ：

```
print([texts[hits[0][i]['corpus_id']] for i in range(len(hits[0]))])
```

以下 5 条 FAQ 离客户查询最近：

```
['How can I get help with my Medicare Part A and Part B premiums?',
 'What is Medicare and who can get it?',
 'How do I sign up for Medicare?',
 'What are the different parts of Medicare?',
 'Will my Medicare premiums be higher because of my higher income?']
```

这份列表就是离客户查询最近的 5 条 FAQ。不错！这里我们把 PyTorch 和 Sentence Transformers 当作主要的数值工具。当然，也可以用 NumPy、SciPy 之类的工具自己定义余弦相似度和排序函数。

## 继续学习的额外资源

想更了解 Sentence Transformers 库：

- [Hub 组织页](https://huggingface.co/sentence-transformers)，有新模型和模型下载说明。
- [Nils Reimers 的推文](https://twitter.com/Nils_Reimers/status/1487014195568775173)对比了 Sentence Transformer 模型与 GPT-3 Embeddings。剧透：Sentence Transformers 很能打！
- [Sentence Transformers 文档](https://www.sbert.net/)
- [Nima 的线程](https://twitter.com/NimaBoscarino/status/1535331680805801984)介绍最新研究。

### 训练与进阶技术

用熟了嵌入模型后，你可能想训练或微调自己的模型，或探索相关技术：

- [用 Sentence Transformers 训练与微调嵌入模型](https://huggingface.co/blog/train-sentence-transformers)：用现行训练 API 训练或微调 Sentence Transformer 模型
- [用 Sentence Transformers 训练与微调重排序模型](https://huggingface.co/blog/train-reranker)：为"检索-重排"流水线的第二阶段训练 Cross Encoder（重排序器）模型
- [用 Sentence Transformers 训练与微调稀疏嵌入模型](https://huggingface.co/blog/train-sparse-encoder)：训练 SPLADE 等稀疏嵌入模型
- [Sentence Transformers 的多模态嵌入与重排序模型](https://huggingface.co/blog/multimodal-sentence-transformers)：用同一套 API 处理文本、图像、音频、视频模型
- [用 Sentence Transformers 训练与微调多模态嵌入与重排序模型](https://huggingface.co/blog/train-multimodal-sentence-transformers)：训练或微调多模态模型，例如用于视觉文档检索
- [🪆 俄罗斯套娃（Matryoshka）嵌入模型入门](https://huggingface.co/blog/matryoshka)：可以把嵌入截断到更小维度而质量损失极小
- [用 Sentence Transformers 训练快 400 倍的静态嵌入模型](https://huggingface.co/blog/static-embeddings)：不依赖注意力、对 CPU 友好的嵌入模型
- [二值与标量嵌入量化：显著更快更省的检索](https://huggingface.co/blog/embedding-quantization)：训练后压缩嵌入以削减存储、加速搜索

感谢阅读！
