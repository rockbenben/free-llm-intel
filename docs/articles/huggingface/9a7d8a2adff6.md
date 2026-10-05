---
vendor: huggingface
title: SetFitABSA：使用 SetFit 的少样本方面级情感分析
original_title: SetFitABSA: Few-Shot Aspect Based Sentiment Analysis using SetFit
url: https://huggingface.co/blog/setfit-absa
date: 2023-09-12
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: b1cf8206e9a9
---

本文亦有[简体中文](https://huggingface.co/blog/zh/setfit-absa)版本。

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/setfit-absa/method.png)

*SetFitABSA 是一种高效的技术，用于检测文本中对特定方面（aspect）的情感。*

方面级情感分析（Aspect-Based Sentiment Analysis, ABSA）是检测文本中对特定方面情感的任务。例如在句子 "This phone has a great screen, but its battery is too small" 中，*方面*词是 "screen" 和 "battery"，对应它们的情感极性分别是正面和负面。

ABSA 被组织广泛采用，通过分析客户对各个领域产品或服务的各方面的反馈来提取有价值的洞察。然而，为 ABSA 标注训练数据是一件苦差事，因为要在训练样本中标识的方面粒度非常细（词元级）。

Intel Labs 和 Hugging Face 很高兴推出 SetFitABSA——一个用于少样本训练领域专用 ABSA 模型的框架；SetFitABSA 在少样本场景下具有竞争力，甚至胜过 Llama2、T5 这类生成式模型。

与基于 LLM 的方法相比，SetFitABSA 有两大独特优势：

🗣 **不需要提示词：** 用 LLM 做少样本上下文学习需要手工打磨提示词，这让结果变得脆弱、对措辞敏感、并且依赖使用者的经验。SetFitABSA 干脆抛弃提示词，直接从一个小的标注文本样本集生成丰富的嵌入。

🏎 **训练快：** SetFitABSA 只需要少量标注训练样本；此外，它使用简单的训练数据格式，无需专门的标注工具。这让数据标注过程又快又轻松。

在这篇博客中，我们将解释 SetFitABSA 的原理，以及如何用 [SetFit 库](https://github.com/huggingface/setfit)训练你自己的模型。开始吧！

## 它是如何工作的？

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/setfit-absa/method.png)

*SetFitABSA 的三阶段训练过程*

SetFitABSA 由三个步骤组成。第一步从文本中抽取方面候选，第二步把方面候选分类为方面或非方面从而得出方面，最后一步为每个抽出的方面关联一个情感极性。第二步和第三步都基于 SetFit 模型。

### 训练

**1. 方面候选抽取**

在这项工作中我们假设：方面通常是产品或服务的特征，多半是名词或名词复合词（连续名词组成的字符串）。我们用 [spaCy](https://spacy.io/) 对（少样本）训练集中的句子做分词，并抽取名词/名词复合词。由于并非所有抽出的名词/名词复合词都是方面，我们称它们为方面候选。

**2. 方面/非方面分类**

有了方面候选，我们需要训练一个模型来区分作为方面的名词和不作为方面的名词。为此需要带"是方面/不是方面"标签的训练样本。做法是：把训练集中标注的方面视为 `True` 方面，而其他不重叠的候选方面视为非方面，标记为 `False`：

- **训练句子：** "Waiters aren't friendly but the cream pasta is out of this world."
- **分词：** [Waiters, are, n't, friendly, but, the, cream, pasta, is, out, of, this, world, .]
- **抽出的方面候选：** [**Waiters**, are, n't, friendly, but, the, **cream**, **pasta**, is, out, of, this, **world**, .]
- **训练集金标签（[BIO 格式](https://en.wikipedia.org/wiki/Inside%E2%80%93outside%E2%80%93beginning_(tagging))）：** [B-ASP, O, O, O, O, O, B-ASP, I-ASP, O, O, O, O, O, .]
- **生成的方面/非方面标签：** [**Waiters**, are, n't, friendly, but, the, **cream**, **pasta**, is, out, of, this, **world**, .]

现在所有方面候选都有了标签，如何用它来训练候选方面分类器呢？换句话说，如何让 SetFit 这个句子分类框架去分类单个词元？这就是技巧所在：把每个方面候选与整个训练句子拼接，用下面的模板创建训练实例：

```
aspect_candidate:training_sentence
```

对上面的例子套用模板会生成 3 个训练实例——两个带 `True` 标签的方面实例，一个带 `False` 标签的非方面实例：

| 文本 | 标签 |
| --- | --- |
| Waiters:Waiters aren't friendly but the cream pasta is out of this world. | 1 |
| cream pasta:Waiters aren't friendly but the cream pasta is out of this world. | 1 |
| world:Waiters aren't friendly but the cream pasta is out of this world. | 0 |
| ... | ... |

生成训练实例后，我们就可以发挥 SetFit 的威力，训练一个少样本、领域专用的二分类器，从输入文本评论中抽取方面。这就是我们第一个微调后的 SetFit 模型。

**3. 情感极性分类**

系统从文本中抽取出方面后，需要为每个方面关联一个情感极性（如正面、负面或中性）。为此我们使用第二个 SetFit 模型，训练方式与方面抽取模型类似，如下例所示：

- **训练句子：** "Waiters aren't friendly but the cream pasta is out of this world."
- **分词：** [Waiters, are, n't, friendly, but, the, cream, pasta, is, out, of, this, world, .]
- **训练集金标签：** [NEG, O, O, O, O, O, POS, POS, O, O, O, O, O, .]

| 文本 | 标签 |
| --- | --- |
| Waiters:Waiters aren't friendly but the cream pasta is out of this world. | NEG |
| cream pasta:Waiters aren't friendly but the cream pasta is out of this world. | POS |
| ... | ... |

注意，与方面抽取模型不同，这个训练集不包含非方面，因为目标是分类真实方面上的情感极性。

## 运行推理

在推理时，测试句子先经过 spaCy 方面候选抽取阶段，按 `aspect_candidate:test_sentence` 模板生成测试实例。接着，方面/非方面分类器过滤掉非方面。最后，抽出的方面被送入情感极性分类器，为每个方面预测情感极性。

实际上，这意味着模型可以接收普通文本作为输入，输出方面及其情感：

**模型输入：**

```
"their dinner specials are fantastic."
```

**模型输出：**

```
[{'span': 'dinner specials', 'polarity': 'positive'}]
```

## 基准测试

SetFitABSA 的对比基线是 [AWS AI Labs](https://arxiv.org/pdf/2210.06629.pdf) 和 [Salesforce AI Research](https://arxiv.org/pdf/2204.05356.pdf) 近期的最先进工作——他们用提示词微调 T5 和 GPT2。为了更完整的图景，我们还在上下文学习下对比了 Llama-2-chat 模型。我们使用 Semantic Evaluation Challenge 2014（[SemEval14](https://aclanthology.org/S14-2004.pdf)）中广受欢迎的 Laptop14 和 Restaurant14 ABSA [数据集](https://huggingface.co/datasets/alexcadillon/SemEval2014Task4)。SetFitABSA 在中间任务——方面词抽取（SB1）——以及完整的 ABSA 任务——方面抽取连同情感极性预测（SB1+SB2）——上都做了评估。

### 模型规模对比

| 模型 | 规模（参数） |
| --- | --- |
| Llama-2-chat | 7B |
| T5-base | 220M |
| GPT2-base | 124M |
| GPT2-medium | 355M |
| **SetFit (MPNet)** | 2x 110M |

注意，SB1 任务的 SetFitABSA 为 110M 参数，SB2 为 110M 参数，SB1+SB2 的 SetFitABSA 共 220M 参数。

### 性能对比

可以看到，当训练实例数量很少时，SetFitABSA 有明显优势——尽管它的体积是 T5 的一半、GPT2-medium 的三分之一。即使与体积大 64 倍的 Llama 2 相比，性能也持平或更好。

**SetFitABSA vs GPT2**

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/setfit-absa/SetFitABSA_vs_GPT2.png)

**SetFitABSA vs T5**

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/setfit-absa/SetFitABSA_vs_T5.png)

注意，为了公平比较，我们与 SetFitABSA 对比时严格使用各基线（GPT2、T5 等）所使用的数据集划分。

**SetFitABSA vs Llama2**

![](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/setfit-absa/SetFitABSA_vs_Llama2.png)

我们发现，增加 Llama2 的上下文学习样本数量并没有带来性能提升。这种现象此前在 ChatGPT 上也被展示过，我们认为值得进一步研究。

## 训练你自己的模型

SetFitABSA 是 SetFit 框架的一部分。要训练 ABSA 模型，先安装启用了 `absa` 选项的 `setfit`：

```
python -m pip install -U "setfit[absa]"
```

另外，必须安装 `en_core_web_lg` spaCy 模型：

```
python -m spacy download en_core_web_lg
```

接着准备训练集。训练集的格式是一个带 `text`、`span`、`label`、`ordinal` 列的 `Dataset`：

- **text**：包含方面的完整句子或文本。
- **span**：完整句子中的一个方面，可以由多个词组成。例如 "food"。
- **label**：与该方面 span 对应的（极性）标签。例如 "positive"。标签名可以在标注收集的训练数据时任意选择。
- **ordinal**：如果该方面 span 在文本中出现多次，这个 ordinal 表示这些出现的序号。通常它就是 0，因为每个方面一般只在输入文本中出现一次。

例如，训练文本 "Restaurant with wonderful food but worst service I ever seen" 包含两个方面，所以训练集表中会增加两行：

| 文本 | Span | 标签 | Ordinal |
| --- | --- | --- | --- |
| Restaurant with wonderful food but worst service I ever seen | food | positive | 0 |
| Restaurant with wonderful food but worst service I ever seen | service | negative | 0 |
| ... | ... | ... | ... |

训练数据集就绪后，就可以创建 ABSA trainer 并执行训练。SetFit 模型的训练本身相当高效，但 SetFitABSA 涉及两个依次训练的模型，因此建议使用 GPU 训练以保持较短的训练时间。例如，下面的训练脚本在免费的 Google Colab T4 GPU 上约 10 分钟就能训练出一个完整的 SetFitABSA 模型。

```
from datasets import load_dataset
from setfit import AbsaTrainer, AbsaModel

# Create a training dataset as above
# For convenience we will use an already prepared dataset here
train_dataset = load_dataset("tomaarsen/setfit-absa-semeval-restaurants", split="train[:128]")

# Create a model with a chosen sentence transformer from the Hub
model = AbsaModel.from_pretrained("sentence-transformers/paraphrase-mpnet-base-v2")

# Create a trainer:
trainer = AbsaTrainer(model, train_dataset=train_dataset)
# Execute training:
trainer.train()
```

就这样！我们训练出了一个领域专用的 ABSA 模型。我们可以把训练好的模型保存到磁盘或上传到 Hugging Face Hub。注意模型包含两个子模型，所以要分别给定各自的路径：

```
model.save_pretrained(
    "models/setfit-absa-model-aspect", 
    "models/setfit-absa-model-polarity"
)
# or
model.push_to_hub(
    "tomaarsen/setfit-absa-paraphrase-mpnet-base-v2-restaurants-aspect",
    "tomaarsen/setfit-absa-paraphrase-mpnet-base-v2-restaurants-polarity"
)
```

现在可以让训练好的模型投入推理了。先加载模型：

```
from setfit import AbsaModel

model = AbsaModel.from_pretrained(
    "tomaarsen/setfit-absa-paraphrase-mpnet-base-v2-restaurants-aspect",
    "tomaarsen/setfit-absa-paraphrase-mpnet-base-v2-restaurants-polarity"
)
```

然后使用 predict API 运行推理。输入是字符串列表，每个字符串是一段文本评论：

```
preds = model.predict([
    "Best pizza outside of Italy and really tasty.",
    "The food variations are great and the prices are absolutely fair.",
    "Unfortunately, you have to expect some waiting time and get a note with a waiting number if it should be very full."
])

print(preds)
# [
#     [{'span': 'pizza', 'polarity': 'positive'}],
#     [{'span': 'food variations', 'polarity': 'positive'}, {'span': 'prices', 'polarity': 'positive'}],
#     [{'span': 'waiting time', 'polarity': 'neutral'}, {'span': 'waiting number', 'polarity': 'neutral'}]
# ]
```

更多训练选项、模型保存与加载、推理的细节，请参阅 SetFit [文档](https://huggingface.co/docs/setfit/how_to/absa)。

## 参考资料

- Maria Pontiki, Dimitris Galanis, John Pavlopoulos, Harris Papageorgiou, Ion Androutsopoulos, and Suresh Manandhar. 2014. SemEval-2014 task 4: Aspect based sentiment analysis. In Proceedings of the 8th International Workshop on Semantic Evaluation (SemEval 2014), pages 27–35.
- Siddharth Varia, Shuai Wang, Kishaloy Halder, Robert Vacareanu, Miguel Ballesteros, Yassine Benajiba, Neha Anna John, Rishita Anubhai, Smaranda Muresan, Dan Roth, 2023 "Instruction Tuning for Few-Shot Aspect-Based Sentiment Analysis". [https://arxiv.org/abs/2210.06629](https://arxiv.org/abs/2210.06629)
- Ehsan Hosseini-Asl, Wenhao Liu, Caiming Xiong, 2022. "A Generative Language Model for Few-shot Aspect-Based Sentiment Analysis". [https://arxiv.org/abs/2204.05356](https://arxiv.org/abs/2204.05356)
- Lewis Tunstall, Nils Reimers, Unso Eun Seo Jo, Luke Bates, Daniel Korat, Moshe Wasserblat, Oren Pereg, 2022. "Efficient Few-Shot Learning Without Prompts". [https://arxiv.org/abs/2209.11055](https://arxiv.org/abs/2209.11055)
