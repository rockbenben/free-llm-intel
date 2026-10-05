---
vendor: huggingface
title: 用机器学习为客户服务赋能
original_title: Supercharged Customer Service with Machine Learning
url: https://huggingface.co/blog/supercharge-customer-service-with-machine-learning
date: 2022-09-22
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: ea110daab1b1
---

# 用机器学习为客户服务赋能

Patrick von Platen（patrickvonplaten）

在这篇博客里，我们会模拟一个真实世界的客户服务场景，并用 Hugging Face 生态里的机器学习工具来解决它。

我们强烈推荐把这个 Notebook 当作模板/示例，去解决**你自己的**真实场景。

## 定义任务、数据集与模型

在真正开始写代码之前，先把你想要自动化（或部分自动化）的场景定义清楚很重要。场景定义清晰，才能为你的用例找到最合适的任务、数据集和模型。

### 定义你的 NLP 任务

好，来看一个我们想用自然语言处理模型解决的假想问题。假设我们在卖一款产品，客服团队每天收到成千上万条消息，包括反馈、投诉和问题，理想情况下这些都应该被回复。

很快就会发现，客服根本不可能回复每一条消息。于是我们决定只回复最不满意的客户，并目标是把这 100% 的消息都回复到位——因为相比中性与正面消息，这些多半是最紧急的。

假设 a）非常不满意的客户消息只占全部消息的一小部分，且 b）我们能用自动化的方式把这些不满意的消息筛出来，那客服就应该能达成这个目标。

要自动化地筛出不满意的消息，我们打算用上自然语言处理技术。

第一步是把我们的场景——*筛出不满意的客户消息*——映射到一个机器学习任务上。

[Hugging Face Hub 的任务页](https://huggingface.co/tasks)是不错的起点，可以看哪个任务最贴合你的场景。每个任务都有详细说明和潜在用例。

"找出最不满意客户的消息"这个任务可以建模为文本分类：把一条消息分到以下 5 个类别之一：*非常不满意*、*不满意*、*中性*、*满意*、**或** *非常满意*。

### 找到合适的数据集

定了任务，下一步是找模型要用的训练数据。对你的场景而言，数据通常比选对模型架构更影响性能。记住：模型**最多只能好到它训练数据的质量**。所以挑选和整理数据集时要格外小心。

既然我们的假想场景是*筛出不满意的客户消息*，就来看看有哪些可用数据集。

在你的真实场景里，**很可能**你手里有内部数据，它们最能代表你的 NLP 系统实际要处理的数据。那就应该用这些内部数据来训练。同时混入一些公开数据也有帮助，能提升模型的泛化能力。

来看看 [Hugging Face Hub](https://huggingface.co/datasets) 上所有可用的数据集。左侧可以按 *Task Categories*（任务类别）和更细的 *Tasks*（任务）过滤。我们的场景对应 *Text Classification* -> *Sentiment Analysis*，所以选中[这些过滤条件](https://huggingface.co/datasets?task_categories=task_categories:text-classification&task_ids=task_ids:sentiment-classification&sort=downloads)。写这个 Notebook 的时候，剩下大约 80 个数据集。挑数据集要看两点：

- **质量**：数据集质量高吗？具体说：数据和你场景中预期要处理的数据一致吗？数据足够多样、没有偏见吗……？
- **规模**：数据集有多大？通常可以放心地说，越大越好。

高效评估数据集质量相当棘手，判断数据集是否有偏见、偏见在哪更难。看下载量是个简单有效的质量启发式：下载越多、使用越多，数据集质量高的可能性越大。规模则好评估，通常扫一眼数据集卡片就知道了。来看看下载量最大的几个数据集：

- [Glue](https://huggingface.co/datasets/glue)
- [Amazon polarity](https://huggingface.co/datasets/amazon_polarity)
- [Tweet eval](https://huggingface.co/datasets/tweet_eval)
- [Yelp review full](https://huggingface.co/datasets/yelp_review_full)
- [Amazon reviews multi](https://huggingface.co/datasets/amazon_reviews_multi)

接下来读数据集卡片（理想情况下卡片应包含所有相关信息）来更细致地检查这些数据集。此外，[dataset viewer](https://huggingface.co/datasets/glue/viewer/cola/test) 是判断数据是否适合你场景的强力工具。

快速过一遍上面这些数据集的卡片：

- *GLUE* 是一堆小数据集的合集，主要给研究者比较新模型架构用。这些数据集太小，也跟我们的场景不够贴合。
- *Amazon polarity* 规模大，而且因为数据本身就是商品评论，很适合客户反馈场景。但它的标签只有二分类（正/负），而我们要的情感分类需要更细的粒度。
- *Tweet eval* 用各种 emoji 当标签，很难映射到"不满意到满意"的量表上。
- *Amazon reviews multi* 看起来是这里最合适的。它的评论情感标签是 1-5，对应 Amazon 的 1-5 星，这些标签可以映射到*非常不满意、中性、满意、非常满意*。我们在 [dataset viewer](https://huggingface.co/datasets/amazon_reviews_multi/viewer/en/train) 上抽查了一些例子，确认这些评论和真实客户反馈很像，所以这是个很好的数据集。另外每条评论还带 `product_category` 标签，我们甚至可以把数据限定在和自己产品对应的类别上。这个数据集是多语言的，但我们目前只需要英文版。
- *Yelp review full* 看起来也很合适：规模大，含商品评论和 1-5 的情感标签。可惜这个数据集的 viewer 打不开，卡片也相对简陋，需要花更多时间检查。这时应该去读原始论文，但鉴于本篇博客的时间预算，我们选 *Amazon reviews multi*。结论：我们就用 [*Amazon reviews multi*](https://huggingface.co/datasets/amazon_reviews_multi) 数据集，并且考虑全部训练样本。

最后提一句：即使处理私有数据，我们也推荐使用 Hub 的数据集功能。Hugging Face Hub、Transformers 和 Datasets 的集成非常顺滑，组合使用来训练模型毫无阻力。

此外 Hugging Face Hub 还提供：

- [每个数据集都有 dataset viewer](https://huggingface.co/datasets/amazon_reviews_multi)
- [用 widget 轻松给任意模型做演示](https://huggingface.co/docs/hub/models-widgets)
- [私有与公开模型](https://huggingface.co/docs/hub/repositories-settings)
- [仓库的 Git 版本控制](https://huggingface.co/docs/hub/repositories-getting-started)
- [最高等级的安全机制](https://huggingface.co/docs/hub/security)

### 找到合适的模型

任务和最能描述场景的数据集都定了，现在来选要用的模型。

你多半需要在自己的场景上微调一个预训练模型，但先看看 Hub 上是否已有合适的微调模型也值得一做。如果有，在它基础上继续用你的数据集微调，往往能达到更高性能。

来看看所有在 Amazon Reviews Multi 上微调过的模型。在数据集页面右下角点击 *Browse models trained on this dataset*，就能拿到[公开数据上所有在该数据集微调过的模型列表](https://huggingface.co/models?dataset=dataset:amazon_reviews_multi)。注意我们只关心数据集的英文版本，因为客户反馈只有英文。下载量最大的那批模型多数是在多语言版本上训练的，而少数看起来非多语言的又信息很少或性能很差。所以到这里，与其用上面链接里已微调过的模型，不如直接微调一个纯预训练模型更合理。

好，下一步是找到用于微调的合适预训练模型。考虑到 [Hugging Face Hub](https://huggingface.co/models) 上海量的预训练与微调模型，这一步其实比看起来难。通常最好的办法是多试几个不同的模型，看谁表现最好。在 Hugging Face 我们还没找到比较不同模型 checkpoint 的完美方式，但有一些资源值得参考：

- [模型总览（model summary）](https://huggingface.co/docs/transformers/model_summary)简要介绍了各种模型架构。
- 在 Hugging Face Hub 上做任务搜索，*例如*[搜文本分类模型](https://huggingface.co/models)，能看到下载量最高的 checkpoint，这也在一定程度上反映了它们的性能。

不过这两个资源目前都不够理想。模型总览不总是被作者及时更新；新架构发布、旧架构过时的速度，让"所有架构的最新总览"几乎不可能做到。同理，下载量最高的 checkpoint 也不一定最好，比如 [`bert-base-cased`](https://huggingface.co/bert-base-uncased) 是下载量最高的 checkpoint 之一，但已不是性能最好的。

最佳做法是：多试几种模型架构、关注领域专家以跟进新架构、并查看知名排行榜。

对文本分类，值得看的基准是 [GLUE](https://gluebenchmark.com/leaderboard) 和 [SuperGLUE](https://super.gluebenchmark.com/leaderboard)。这两个基准在多种文本分类任务上评估预训练模型——语法正确性、自然语言推理、是非问答等等——和我们的情感分类任务相当接近。因此从这些榜单的头部模型里挑一个用于我们的任务是合理的。

写本篇博客时，表现最好的模型都是参数量超 100 亿的巨型模型，且多数没有开源，*例如* *ST-MoE-32B*、*Turing NLR v5*、*ERNIE 3.0*。头部模型里容易获取的是 [DeBERTa](https://huggingface.co/docs/transformers/model_doc/deberta)。所以我们就来试 DeBERTa 最新的 base 版本——即 [`microsoft/deberta-v3-base`](https://huggingface.co/microsoft/deberta-v3-base)。

## 用 🤗 Transformers 和 🤗 Datasets 训练 / 微调模型

接下来进入技术细节：如何端到端地微调一个模型，让它能自动筛出"非常满意不足"的客户反馈消息。

好！先安装所有需要的 pip 包、配好代码环境，然后处理数据集的预处理，最后开始训练模型。

下面的 Notebook 可以在 Google Colab Pro 上开启 GPU 运行时直接跑。

### 安装所有必需的包

先来安装 [`git-lfs`](https://git-lfs.github.com/)，这样训练过程中就能自动把训练好的 checkpoint 上传到 Hub。

```
apt install git-lfs
```

同时安装本 Notebook 要用到的 🤗 Transformers 和 🤗 Datasets 库。因为本篇博客会用 [DeBERTa](https://huggingface.co/docs/transformers/model_doc/deberta-v2#debertav2)，还需要安装 [`sentencepiece`](https://github.com/google/sentencepiece) 库供它的分词器使用。

```
pip install datasets transformers[sentencepiece]
```

然后登录我们的 [Hugging Face 账号](https://huggingface.co/join)，让模型上传到正确的用户名下。

```
from huggingface_hub import notebook_login

notebook_login()
```

**输出：**

```
    Login successful
    Your token has been saved to /root/.huggingface/token
    Authenticated through git-credential store but this isn't the helper defined on your machine.
    You might have to re-authenticate when pushing to the Hugging Face Hub. Run the following command in your terminal in case you want to set this credential helper as the default

    git config --global credential.helper store
```

### 预处理数据集

开始训练前，要把数据集转成模型能理解的格式。

好在 🤗 Datasets 库让这件事变得极其简单，从下面几行就能看到。

`load_dataset` 函数会加载数据集、整齐地整理进预定义字段（如 `review_body` 和 `stars`），并把整理后的数据以 [arrow 格式](https://arrow.apache.org/#:~:text=Format,data%20access%20without%20serialization%20overhead.)存到磁盘。arrow 格式支持快速且省内存的数据读写。

来加载 `amazon_reviews_multi` 数据集的英文版本。

```
from datasets import load_dataset

amazon_review = load_dataset("amazon_reviews_multi", "en")
```

**输出：**

```
    Downloading and preparing dataset amazon_reviews_multi/en (download: 82.11 MiB, generated: 58.69 MiB, post-processed: Unknown size, total: 140.79 MiB) to /root/.cache/huggingface/datasets/amazon_reviews_multi/en/1.0.0/724e94f4b0c6c405ce7e476a6c5ef4f87db30799ad49f765094cf9770e0f7609...

    Dataset amazon_reviews_multi downloaded and prepared to /root/.cache/huggingface/datasets/amazon_reviews_multi/en/1.0.0/724e94f4b0c6c405ce7e476a6c5ef4f87db30799ad49f765094cf9770e0f7609. Subsequent calls will reuse this data.
```

快得飞起 🔥。来看看数据集的结构。

```
print(amazon_review)
```

**输出：**

```
{.output .execute_result execution_count="5"}
    DatasetDict({
        train: Dataset({
            features: ['review_id', 'product_id', 'reviewer_id', 'stars', 'review_body', 'review_title', 'language', 'product_category'],
            num_rows: 200000
        })
        validation: Dataset({
            features: ['review_id', 'product_id', 'reviewer_id', 'stars', 'review_body', 'review_title', 'language', 'product_category'],
            num_rows: 5000
        })
        test: Dataset({
            features: ['review_id', 'product_id', 'reviewer_id', 'stars', 'review_body', 'review_title', 'language', 'product_category'],
            num_rows: 5000
        })
    })
```

我们有 20 万条训练样本，以及各 5000 条验证与测试样本。对训练来说很合理！我们真正关心的只有输入 `"review_body"` 列和目标 `"stars"` 列。

随机看一条。

```
random_id = 34

print("Stars:", amazon_review["train"][random_id]["stars"])
print("Review:", amazon_review["train"][random_id]["review_body"])
```

**输出：**

```
    Stars: 1
    Review: This product caused severe burning of my skin. I have used other brands with no problems
```

数据集是人类可读格式，但现在需要把它变成"机器可读"格式。先定义模型仓库，它包含预处理和微调我们选定的 checkpoint 所需的全部工具。

```
model_repository = "microsoft/deberta-v3-base"
```

然后加载模型仓库的分词器，也就是 [DeBERTa 的 Tokenizer](https://huggingface.co/docs/transformers/model_doc/deberta-v2#transformers.DebertaV2Tokenizer)。

```
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(model_repository)
```

如前所述，我们用 `"review_body"` 作为模型输入、`"stars"` 作为模型目标。接下来用分词器把输入转成模型能理解的 token id 序列。分词器干的正是这件事，还能帮你把输入长度控制在一定范围内以避免内存问题。这里我们把最大长度限制为 128 个 token；对 DeBERTa 来说大约对应 100 个词，也就是约 5-7 句话。再看一眼 [dataset viewer](https://huggingface.co/datasets/amazon_reviews_multi/viewer/en/test)，可以发现这基本覆盖了全部训练样本。**重要**：这并不意味着模型处理不了更长的输入序列，只是训练时用 128 的最大长度就够了，因为它已覆盖 99% 的训练数据，我们不想浪费显存。Transformer 模型在训练后被证明很擅长向更长序列泛化。

想更全面了解分词，可以看 [Tokenizers 文档](https://huggingface.co/course/chapter6/1?fw=pt)。

标签的转换很简单，原始标签本来就是数字，即 1 到 5。我们只需把标签整体挪到 0 到 4，因为索引通常从 0 开始。

好，把想法落成代码。我们定义一个 `preprocess_function`，对每条数据样本应用它。

```
def preprocess_function(example):
    output_dict = tokenizer(example["review_body"], max_length=128, truncation=True)
    output_dict["labels"] = [e - 1 for e in example["stars"]]
    return output_dict
```

要把这个函数应用到数据集的全部样本，我们用之前创建的 `amazon_review` 对象的 [`map`](https://huggingface.co/docs/datasets/master/en/package_reference/main_classes#datasets.Dataset.map) 方法。它会对 `amazon_review` 所有划分中的每个元素执行该函数，所以训练、验证、测试数据一条命令就全部预处理完。我们使用 `batched=True` 模式加速，同时删掉所有不再需要的列。

```
tokenized_datasets = amazon_review.map(preprocess_function, batched=True, remove_columns=amazon_review["train"].column_names)
```

看看新的结构。

```
tokenized_datasets
```

**输出：**

```
    DatasetDict({
        train: Dataset({
            features: ['input_ids', 'token_type_ids', 'attention_mask', 'labels'],
            num_rows: 200000
        })
        validation: Dataset({
            features: ['input_ids', 'token_type_ids', 'attention_mask', 'labels'],
            num_rows: 5000
        })
        test: Dataset({
            features: ['input_ids', 'token_type_ids', 'attention_mask', 'labels'],
            num_rows: 5000
        })
    })
```

可以看到外层结构没变，只是列名变了。再来看之前那条随机样本——这次它是预处理过的。

```
print("Input IDS:", tokenized_datasets["train"][random_id]["input_ids"])
print("Labels:", tokenized_datasets["train"][random_id]["labels"])
```

**输出：**

```
    Input IDS: [1, 329, 714, 2044, 3567, 5127, 265, 312, 1158, 260, 273, 286, 427, 340, 3006, 275, 363, 947, 2]
    Labels: 0
```

好，输入文本变成了整数序列，模型可以把它们转成词嵌入；标签索引也简单地整体减了 1。

### 微调模型

数据集预处理完毕，下面微调模型。我们会用到流行的 [Hugging Face Trainer](https://huggingface.co/docs/transformers/main/en/main_classes/trainer)，几行代码就能开始训练。`Trainer` 基本适用于 PyTorch 的所有任务，它处理了训练所需的大量样板代码，用起来非常省事。

先用方便的 [`AutoModelForSequenceClassification`](https://huggingface.co/docs/transformers/main/en/model_doc/auto#transformers.AutoModelForSequenceClassification) 加载模型 checkpoint。由于模型仓库里的 checkpoint 只是预训练 checkpoint，需要通过 `num_lables=5` 指定分类头的尺寸（因为我们有 5 个情感类别）。

```
from transformers import AutoModelForSequenceClassification

model = AutoModelForSequenceClassification.from_pretrained(model_repository, num_labels=5)
```

```
    Some weights of the model checkpoint at microsoft/deberta-v3-base were not used when initializing DebertaV2ForSequenceClassification: ['mask_predictions.classifier.bias', 'mask_predictions.LayerNorm.bias', 'mask_predictions.dense.weight', 'mask_predictions.dense.bias', 'mask_predictions.LayerNorm.weight', 'lm_predictions.lm_head.dense.bias', 'lm_predictions.lm_head.bias', 'lm_predictions.lm_head.LayerNorm.weight', 'lm_predictions.lm_head.dense.weight', 'lm_predictions.lm_head.LayerNorm.bias', 'mask_predictions.classifier.weight']
    - This IS expected if you are initializing DebertaV2ForSequenceClassification from the checkpoint of a model trained on another task or with another architecture (e.g. initializing a BertForSequenceClassification model from a BertForPreTraining model).
    - This IS NOT expected if you are initializing DebertaV2ForSequenceClassification from the checkpoint of a model that you expect to be exactly identical (initializing a BertForSequenceClassification model from a BertForSequenceClassification model).
    Some weights of DebertaV2ForSequenceClassification were not initialized from the model checkpoint at microsoft/deberta-v3-base and are newly initialized: ['pooler.dense.bias', 'classifier.weight', 'classifier.bias', 'pooler.dense.weight']
    You should probably TRAIN this model on a down-stream task to be able to use it for predictions and inference.
```

接着加载一个数据整理器（data collator）。[data collator](https://huggingface.co/docs/transformers/main_classes/data_collator) 负责保证每个 batch 在训练时被正确 padding——由于训练样本在每个 epoch 前都会重新打乱，padding 需要是动态的。

```
from transformers import DataCollatorWithPadding

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
```

训练期间，监控模型在保留验证集上的表现很重要。为此要给 `Trainer` 传一个 `compute_metrics` 函数，训练中的每个验证步骤都会调用它。

文本分类最简单的指标是*准确率（accuracy）*，就是被正确分类的样本占比。不过当验证或测试数据非常不均衡时，用*准确率*会有问题。我们快速统计各标签的出现次数，确认这里不是这种情况。

```
from collections import Counter

print("Validation:", Counter(tokenized_datasets["validation"]["labels"]))
print("Test:", Counter(tokenized_datasets["test"]["labels"]))
```

**输出：**

```
    Validation: Counter({0: 1000, 1: 1000, 2: 1000, 3: 1000, 4: 1000})
    Test: Counter({0: 1000, 1: 1000, 2: 1000, 3: 1000, 4: 1000})
```

验证集和测试集均衡得不能再均衡了，所以这里可以放心用准确率！

通过 datasets 库加载[准确率指标](https://huggingface.co/metrics/accuracy)。

```
from datasets import load_metric

accuracy = load_metric("accuracy")
```

然后定义 `compute_metrics`：它作用于模型的预测输出——类型为 [`EvalPrediction`](https://huggingface.co/docs/transformers/main/en/internal/trainer_utils#transformers.EvalPrediction)，同时暴露模型预测和真实标签。我们先对模型预测取 `argmax` 得到预测类别，再连同真实标签一起传给准确率指标。

```
import numpy as np

def compute_metrics(pred):
    pred_logits = pred.predictions
    pred_classes = np.argmax(pred_logits, axis=-1)
    labels = np.asarray(pred.label_ids)

    acc = accuracy.compute(predictions=pred_classes, references=labels)

    return {"accuracy": acc["accuracy"]}
```

好，训练所需的组件全部就绪，剩下的只是定义 `Trainer` 的超参数。我们要确保训练过程中模型 checkpoint 会上传到 Hugging Face Hub。设置 `push_to_hub=True` 后，每个 `save_steps` 都会通过方便的 [`push_to_hub`](https://huggingface.co/docs/transformers/main/en/main_classes/trainer#transformers.Trainer.push_to_hub) 方法自动上传。

此外我们还定义一些标准超参数：学习率、warmup 步数、训练轮数。每 500 步记录一次 loss，每 5000 步跑一次评估。

```
from transformers import TrainingArguments

training_args = TrainingArguments(
    output_dir="deberta_amazon_reviews_v1",
    num_train_epochs=2, 
    learning_rate=2e-5,
    warmup_steps=200,
    logging_steps=500,
    save_steps=5000,
    eval_steps=5000,
    push_to_hub=True,
    evaluation_strategy="steps",
)
```

全部拼起来，终于能实例化 Trainer 并传入所有必需组件。训练期间的保留数据集用 `"validation"` 划分。

```
from transformers import Trainer

trainer = Trainer(
    args=training_args,
    compute_metrics=compute_metrics,
    model=model,
    tokenizer=tokenizer,
    data_collator=data_collator,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["validation"]
)
```

Trainer 蓄势待发 🚀 调用 `trainer.train()` 即可开始训练。

```
train_metrics = trainer.train().metrics
trainer.save_metrics("train", train_metrics)
```

**输出：**

```
    ***** Running training *****
      Num examples = 200000
      Num Epochs = 2
      Instantaneous batch size per device = 8
      Total train batch size (w. parallel, distributed & accumulation) = 8
      Gradient Accumulation steps = 1
      Total optimization steps = 50000
```

**输出：**

| Step | Training Loss | Validation Loss | Accuracy |
| --- | --- | --- | --- |
| 5000 | 0.931200 | 0.979602 | 0.585600 |
| 10000 | 0.931600 | 0.933607 | 0.597400 |
| 15000 | 0.907600 | 0.917062 | 0.602600 |
| 20000 | 0.902400 | 0.919414 | 0.604600 |
| 25000 | 0.879400 | 0.910928 | 0.608400 |
| 30000 | 0.806700 | 0.933923 | 0.609200 |
| 35000 | 0.826800 | 0.907260 | 0.616200 |
| 40000 | 0.820500 | 0.904160 | 0.615800 |
| 45000 | 0.795000 | 0.918947 | 0.616800 |
| 50000 | 0.783600 | 0.907572 | 0.618400 |

**输出：**

```
    ***** Running Evaluation *****
      Num examples = 5000
      Batch size = 8
    Saving model checkpoint to deberta_amazon_reviews_v1/checkpoint-50000
    Configuration saved in deberta_amazon_reviews_v1/checkpoint-50000/config.json
    Model weights saved in deberta_amazon_reviews_v1/checkpoint-50000/pytorch_model.bin
    tokenizer config file saved in deberta_amazon_reviews_v1/checkpoint-50000/tokenizer_config.json
    Special tokens file saved in deberta_amazon_reviews_v1/checkpoint-50000/special_tokens_map.json
    added tokens file saved in deberta_amazon_reviews_v1/checkpoint-50000/added_tokens.json


    Training completed. Do not forget to share your model on huggingface.co/models =)
```

不错，模型确实学到了东西！训练损失和验证损失都在下降，准确率也远高于随机水平（20%）。有趣的是，仅 5000 步后准确率就达到约 **58.6%**，之后再提升就不大了。换个更大的模型或多训一会儿也许能更好，但对我们的假想场景够用了！

好，最后把模型 checkpoint 上传到 Hub。

```
trainer.push_to_hub()
```

**输出：**

```
    Saving model checkpoint to deberta_amazon_reviews_v1
    Configuration saved in deberta_amazon_reviews_v1/config.json
    Model weights saved in deberta_amazon_reviews_v1/pytorch_model.bin
    tokenizer config file saved in deberta_amazon_reviews_v1/tokenizer_config.json
    Special tokens file saved in deberta_amazon_reviews_v1/special_tokens_map.json
    added tokens file saved in deberta_amazon_reviews_v1/added_tokens.json
    Several commits (2) will be pushed upstream.
    The progress bars may be unreliable.
```

### 评估 / 分析模型

微调完成后，要认真分析模型的表现。注意：像*准确率*这样的标准指标有助于了解模型表现的大致情况，但可能不足以评估模型在你真实场景上的表现。更好的做法是找到一个最贴合模型实际用途的指标，并在训练中和训练后专门度量它。

开始评估模型 🤿。

训练结束后模型已被上传到 Hub，名为 [`deberta_v3_amazon_reviews`](https://huggingface.co/patrickvonplaten/deberta_v3_amazon_reviews)，所以第一步先从那里把它下载回来。

```
from transformers import AutoModelForSequenceClassification

model = AutoModelForSequenceClassification.from_pretrained("patrickvonplaten/deberta_v3_amazon_reviews")
```

Trainer 不仅是训练模型的优秀类，也是评估模型的好帮手。用与之前相同的实例和函数重新实例化 Trainer，只是这次不需要传训练数据集。

```
trainer = Trainer(
    args=training_args,
    compute_metrics=compute_metrics,
    model=model,
    tokenizer=tokenizer,
    data_collator=data_collator,
)
```

用 Trainer 的 [`predict`](https://huggingface.co/docs/transformers/main/en/main_classes/trainer#transformers.Trainer.predict) 函数在测试集上按同一指标评估模型。

```
prediction_metrics = trainer.predict(tokenized_datasets["test"]).metrics
prediction_metrics
```

**输出：**

```
    ***** Running Prediction *****
      Num examples = 5000
      Batch size = 8
```

**输出：**

```
    {'test_accuracy': 0.608,
     'test_loss': 0.9637690186500549,
     'test_runtime': 21.9574,
     'test_samples_per_second': 227.714,
     'test_steps_per_second': 28.464}
```

结果与验证集上的表现非常接近，这通常是个好信号，说明模型没有过拟合测试集。

不过 5 类分类问题下 60% 的准确率离完美还差得远——但我们需要每个类都高精度的准确率吗？

由于我们最关心的是非常负面的客户反馈，那就只看模型对最不满意客户评论的分类表现。我们还可以"帮"模型一把——凡是分至**非常不满意**或**不满意**的反馈都由我们来处理——目标是抓住接近 99% 的**非常不满意**消息。同时，这也能衡量这样处理能回复到多少**不满意**消息，以及我们为中性、满意、非常满意的客户多做了多少无用功。

好，写一个新的 `compute_metrics` 函数。

```
import numpy as np

def compute_metrics(pred):
    pred_logits = pred.predictions
    pred_classes = np.argmax(pred_logits, axis=-1)
    labels = np.asarray(pred.label_ids)

    # First let's compute % of very unsatisfied messages we can catch
    very_unsatisfied_label_idx = (labels == 0)
    very_unsatisfied_pred = pred_classes[very_unsatisfied_label_idx]

    # Now both 0 and 1 labels are 0 labels the rest is > 0
    very_unsatisfied_pred = very_unsatisfied_pred * (very_unsatisfied_pred - 1)
    
    # Let's count how many labels are 0 -> that's the "very unsatisfied"-accuracy
    true_positives = sum(very_unsatisfied_pred == 0) / len(very_unsatisfied_pred)

    # Second let's compute how many satisfied messages we unnecessarily reply to
    satisfied_label_idx = (labels > 1)
    satisfied_pred = pred_classes[satisfied_label_idx]

    # how many predictions are labeled as unsatisfied over all satisfied messages?
    false_positives = sum(satisfied_pred <= 1) / len(satisfied_pred)

    return {"%_unsatisfied_replied": round(true_positives, 2), "%_satisfied_incorrectly_labels": round(false_positives, 2)}
```

再次实例化 `Trainer` 以方便跑评估。

```
trainer = Trainer(
    args=training_args,
    compute_metrics=compute_metrics,
    model=model,
    tokenizer=tokenizer,
    data_collator=data_collator,
)
```

用这个更适合我们场景的新指标再跑一次评估。

```
prediction_metrics = trainer.predict(tokenized_datasets["test"]).metrics
prediction_metrics
```

**输出：**

```
    ***** Running Prediction *****
      Num examples = 5000
      Batch size = 8
```

**输出：**

```
    {'test_%_satisfied_incorrectly_labels': 0.11733333333333333,
     'test_%_unsatisfied_replied': 0.949,
     'test_loss': 0.9637690186500549,
     'test_runtime': 22.8964,
     'test_samples_per_second': 218.375,
     'test_steps_per_second': 27.297}
```

漂亮！图景已经很清晰：我们能自动接住约 95% 的**非常不满意**客户，代价是在约 10% 的满意消息上浪费功夫。

快速算笔账。假设每天收到 1 万条消息，其中预计约 500 条是非常负面的。不用回复全部 1 万条，经过这个自动过滤，我们只需查看 500 + 0.12 * 10,000 = 1700 条，并回复其中 475 条，同时会漏掉 5% 的消息。相当不错——人力节省 83%，只漏掉 5% 的**非常不满意**客户！

显然这些数字不代表真实场景中获得的价值，但只要用足够多高质量的真实示例数据，就能接近这个效果！

保存结果

```
trainer.save_metrics("prediction", prediction_metrics)
```

然后再上传一次到 Hub。

```
trainer.push_to_hub()
```

**输出：**

```
    Saving model checkpoint to deberta_amazon_reviews_v1
    Configuration saved in deberta_amazon_reviews_v1/config.json
    Model weights saved in deberta_amazon_reviews_v1/pytorch_model.bin
    tokenizer config file saved in deberta_amazon_reviews_v1/tokenizer_config.json
    Special tokens file saved in deberta_amazon_reviews_v1/special_tokens_map.json
    added tokens file saved in deberta_amazon_reviews_v1/added_tokens.json
    To https://huggingface.co/patrickvonplaten/deberta_amazon_reviews_v1
       599b891..ad77e6d  main -> main

    Dropping the following result as it does not have all the necessary fields:
    {'task': {'name': 'Text Classification', 'type': 'text-classification'}}
    To https://huggingface.co/patrickvonplaten/deberta_amazon_reviews_v1
       ad77e6d..13e5ddd  main -> main
```

结果数据保存在[这里](https://huggingface.co/patrickvonplaten/deberta_amazon_reviews_v1/blob/main/prediction_results.json)。

今天就到这里 😎。最后一步，拿真实世界的数据实测模型也很有意义。可以直接在[模型卡](https://huggingface.co/patrickvonplaten/deberta_amazon_reviews_v1)的推理 widget 上试：

[![example.png](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/classification_widget.png)](https://raw.githubusercontent.com/patrickvonplaten/scientific_images/master/classification_widget.png)

看起来在真实数据上泛化得相当好 🔥

## 优化

一旦你认为模型表现足够上生产，接下来就是让模型尽可能省内存、尽可能快。

一些显而易见的方案：选最合适的加速硬件（*例如*更好的 GPU）、确保前向传播时不计算梯度、或降低精度（*例如*到 float16）。

更高级的优化方法包括使用开源加速库，如 [ONNX Runtime](https://onnxruntime.ai/index.html)、[量化（quantization）](https://pytorch.org/docs/stable/quantization.html)，以及 [Triton](https://developer.nvidia.com/nvidia-triton-inference-server) 这类推理服务器。

在 Hugging Face，我们做了大量工作来降低模型优化门槛，尤其是开源的 [Optimum 库](https://huggingface.co/hardware)。Optimum 让优化大多数 🤗 Transformers 模型变得极其简单。

如果你在找**高度优化**且完全不需要技术知识的方案，可以关注 [Inference API](https://huggingface.co/inference-api)——一个即插即用的生产级服务方案，覆盖包括情感分析在内的多种机器学习任务。

此外，如果你在找**针对自定义用例的支持**，Hugging Face 的专家团队可以帮你加速 ML 项目！从研究到生产的机器学习之旅中，团队会按需答疑并寻找解决方案。访问 [hf.co/support](https://huggingface.co/support) 了解更多并申请报价。
