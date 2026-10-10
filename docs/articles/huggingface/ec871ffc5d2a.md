---
vendor: huggingface
title: mmBERT：ModernBERT 迈向多语言
original_title: mmBERT: ModernBERT goes Multilingual
url: https://huggingface.co/blog/mmbert
date: 2025-10-07
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: ff51401cb6c8
translator: agent
---

返回文章列表

# mmBERT：ModernBERT 迈向多语言

发布于
					2025 年 9 月 9 日

在 GitHub 上更新



- [![](https://huggingface.co/avatars/0102bcf0db4e822b8bf61ae92305680f.svg)](https://huggingface.co/bitmman-nch)
- [![](https://huggingface.co/avatars/16c289ac2f322e0816d6d5991b618254.svg)](https://huggingface.co/Francois2511)
- [![](https://huggingface.co/avatars/3648c03f5b5f40cd208d46fd3b582739.svg)](https://huggingface.co/bogdanminko)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/tI3V8-PZ8d3CC32fzO31e.png)](https://huggingface.co/Stars321123)
- [![](https://huggingface.co/avatars/6aad4ae2b795578e37fd3723879bff85.svg)](https://huggingface.co/Jyo-K)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/65bd78aeb7db0ab095469e31/jj3kMgx_snMK3AOoJwRwr.jpeg)](https://huggingface.co/Ihssane123)

Marc Marone

mmarone

jhu-clsp

Orion Weller

orionweller

jhu-clsp

William Fleshman

will-fleshman

jhu-clsp

Eugene Yang

eugene-yang

jhu-clsp

Dawn Lawrie

dlawrie

jhu-clsp

Ben Van Durme

vandurme

jhu-clsp

## TL;DR

这篇博客介绍 [mmBERT](https://huggingface.co/collections/jhu-clsp/mmbert-a-modern-multilingual-encoder-68b725831d7c6e3acc435ed4)——一个最先进的（SOTA）大规模多语言编码器模型，在覆盖 1800 多种语言的 3T+ token 文本上训练。它相比此前的多语言模型在性能和速度上都有显著提升，是首个超越 XLM-R 的模型，同时发展出有效学习低资源语言的新策略。mmBERT 建立在 ModernBERT 之上，继承其极速架构，并新增若干组件以实现高效的多语言学习。

如果你想亲自试用模型，[博客末尾](https://huggingface.co/blog/mmbert#usage-examples)提供了示例样板代码！

## 训练数据

图 1：训练数据在整个训练过程中被渐进"退火"，纳入更多语言、采样趋于更均匀。

mmBERT 在一个精心整理、总量超过 3T token 的多语言数据集上训练，分为三个不同阶段。训练数据的底座由三个主要的开源高质量网络爬取数据集构成，兼顾多语言覆盖与数据质量：

**DCLM 与 Filtered DCLM** 提供当前质量最高的英文内容，作为强劲英文性能的骨干（过滤后数据来自 [Dolmino](https://huggingface.co/datasets/allenai/dolmino-mix-1124)）。该数据集代表了最先进的网络数据过滤技术，是关键组成部分。由于其质量很高，我们使用的英文比例显著高于上一代多语言编码器模型（高达 18%）。

**FineWeb2** 提供覆盖 1800 多种语言的广泛[多语言网页内容](https://huggingface.co/datasets/HuggingFaceFW/fineweb-2)。它支撑了我们的大范围多语言覆盖，同时在多样的语系和文字体系中保持合理的质量水准。

**FineWeb2-HQ** 是 [FineWeb2 的过滤子集](https://huggingface.co/datasets/epfml/FineWeb2-HQ)，聚焦 20 种高资源语言。这个过滤版本提供更高质量的多语言内容，在"仅英文过滤数据"与"广泛多语言覆盖"之间架起桥梁。

训练数据还吸收了来自 [Dolma](https://arxiv.org/abs/2402.00159)、[MegaWika v2](https://arxiv.org/abs/2508.03828)、[ProLong](https://arxiv.org/abs/2410.02660) 等的专业语料：代码仓库（StarCoder、ProLong）、学术内容（ArXiv、PeS2o）、参考资料（Wikipedia、教材）和社区讨论（StackExchange），以及指令与数学数据集。

我们数据方法的关键创新是[图 1](https://huggingface.co/blog/mmbert#figure1)展示的**渐进语言纳入策略**。每个阶段我们都从*更平坦*的分布（即更接近均匀分布）中采样，同时加入新语言。也就是说，像俄语这样的高资源语言在训练初期占数据的比例较高（9%），到最后一个训练阶段大约减半。我们在预训练阶段从 60 种高资源语言起步，中期训练扩展到 110 种语言，最后在衰减阶段纳入 FineWeb2 的全部 1833 种语言。这让我们能最大限度发挥有限的低资源语言数据的作用，避免过度重复，同时保持整体数据质量。

## 训练配方与新组件

mmBERT 建立在 [ModernBERT](https://huggingface.co/blog/modernbert) 架构之上，但为多语言学习引入了若干关键创新：

### 架构

我们沿用 ModernBERT-base 的核心架构——22 层、中间维度 1152——但换用 Gemma 2 的分词器以更好地处理多语言文本。base 模型的非嵌入参数为 110M（因词表更大，总参数 307M）；small 变体非嵌入参数 42M（总计 140M）。

### 三阶段训练方案

训练遵循精心设计的三阶段计划：

- **预训练（2.3T token）**：预热加稳定学习率阶段，使用 60 种语言，掩码率 30%
- **中期训练（600B token）**：上下文扩展至 8192 token，数据质量更高，语言扩展到 110 种，掩码率 15%
- **衰减阶段（100B token）**：采用平方根倒数学习率衰减，纳入全部 1833 种语言，掩码率 5%

### 新型训练技术

**反向掩码率调度（Inverse Mask Ratio Schedule）**：我们不用固定掩码率，而是随训练阶段把掩码比例从 30% → 15% → 5% 逐步下调。这让模型早期用较高掩码学习基础表示，后期用较低掩码专注于更细腻的理解。

**退火式语言学习（Annealed Language Learning）**：我们把多语言数据采样的温度从 τ=0.7 → 0.5 → 0.3 动态调整。这形成了从偏向高资源语言到更均匀采样的过渡，让模型先打好多语言基础，再学习低资源语言。

**渐进式语言添加（Progressive Language Addition）**：我们不是一开始就同时训练所有语言，而是在各阶段策略性地添加语言（60 → 110 → 1833）。这避免了在有限的低资源数据上跑过多轮次，最大化学习效率，同时仍取得强劲表现。

**模型融合（Model Merging）**：我们在衰减阶段训练了三个不同变体（英文为主、110 语言、全语言），并用 TIES 融合把它们的优点合并进最终模型。

## 结果

### 自然语言理解（NLU）

表 1：GLUE（英语）上的表现

**英文表现**：在英文 GLUE 基准（[表 1](https://huggingface.co/blog/mmbert#table1)）上，mmBERT base 表现强劲，大幅超越 XLM-R（多语言 RoBERTa）base 和 mGTE base 等其他多语言模型；尽管 mmBERT 训练数据中英文占比不足 25%，仍与仅英文模型不相上下。

表 2：XTREME（多语言）上的表现

**多语言表现**：正如[表 2](https://huggingface.co/blog/mmbert#table2)所示，mmBERT 在 XTREME 基准上相较 XLM-R 有显著提升。亮点包括 XNLI 分类上的强劲表现、TyDiQA 等问答任务的大幅改进，以及在 PAWS-X 和 XCOPA 跨语言理解上的有竞争力结果。

模型在绝大多数类别上都表现良好，例外是 NER、词性标注等结构化预测任务——很可能是分词器差异影响了词边界判断。在这几类上它与上一代大致持平，但可应用的语言更多。

### 检索性能

表 3：MTEB v2 英语上的表现

**英文检索**：尽管 mmBERT 是为大规模多语言场景设计的，在 MTEB v2 英文基准（[表 3](https://huggingface.co/blog/mmbert#table3)）上，mmBERT 相比此前的多语言模型有显著增益，甚至能与 ModernBERT 这样的仅英文模型打平！

表 4：MTEB v2 多语言上的表现

**多语言检索**：在其他模型的多语言对比中，mmBERT 在 MTEB v2 多语言基准上展现出一致的提升（[表 4](https://huggingface.co/blog/mmbert#table4)）。

表 5：CoIR 代码基准上的表现

**代码检索**：得益于现代分词器（基于 Gemma 2），mmBERT 还表现出很强的编码能力（[表 5](https://huggingface.co/blog/mmbert#table5)），使其适用于任何类型的文本数据。唯一超过它的模型是 EuroBERT——它用到了不公开可访问的 Stack v2 数据集。

## 在衰减阶段学习语言

mmBERT 最重要的新特性之一，是证明了低资源语言可以在训练短暂的衰减阶段被有效学会。我们只用最终 100B token 衰减阶段才引入的语言做了测试来验证这一做法。

图 2：在衰减阶段添加 1700 多种语言可以实现快速学习，而这一成果通过模型融合得以保留。

**显著的性能增益**：在 TiQuaD（提格里尼亚语）和 FoQA（法罗语）上的测试显示，把这些语言纳入衰减阶段后取得了大幅改进，如[图 2](https://huggingface.co/blog/mmbert#figure2)所示。结果验证了我们渐进语言学习方法的有效性。

**可与大模型竞争**：尽管只在最后的训练阶段见过这些语言，mmBERT 达到的水平仍超过大得多的模型。在有 LLM 基准数据的法罗语问答上，mmBERT 优于 Google Gemini 2.5 Pro 和 OpenAI o3。

**快速学习的机制**：衰减阶段语言学习之所以成功，在于模型能利用早期阶段建立的强多语言基础。面对新语言时，模型可以迅速调整已有的跨语言表示，而不必从头学起。

**模型融合的收益**：最终的 mmBERT 模型成功保留了衰减阶段的大部分改进，并通过 TIES 融合同时受益于英文为主和高资源语言的两个变体。

## 效率提升

mmBERT 凭借继承自 ModernBERT 的架构改进，相比此前的多语言编码器模型带来了实质性的效率增益：

图 3：mmBERT 比之前的多语言模型高效得多，高达 2-4 倍！

**吞吐性能**：在各种序列长度下，mmBERT 处理文本的速度显著快于现有多语言模型，如[图 3](https://huggingface.co/blog/mmbert#figure3)所示。small 和 base 两种模型都比之前的多语言编码器快很多。

**现代架构的红利**：效率增益来自两项主要技术改进：

- **Flash Attention 2**：优化的注意力计算，显存占用与速度更好
- **去填充（Unpadding）技术**：处理过程中消除不必要的 padding token

**序列长度扩展**：与受限于 512 token 的老模型不同，mmBERT 能高效处理最长 8192 token 的序列并保持高吞吐。这使它适合多语言应用中越来越常见的长文档处理任务。

**能效**：更好的吞吐与现代架构相结合，降低了推理的计算成本，使 mmBERT 在需要大规模多语言支持的生产部署中更实用。

这些效率提升让 mmBERT 不仅比此前的多语言编码器更准，也显著更适合实际使用。

## 使用示例

只需几行代码即可使用这些模型！

```
from transformers import AutoTokenizer, AutoModelForMaskedLM
import torch

tokenizer = AutoTokenizer.from_pretrained("jhu-clsp/mmBERT-base")
model = AutoModelForMaskedLM.from_pretrained("jhu-clsp/mmBERT-base")

def predict_masked_token(text):
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    mask_indices = torch.where(inputs["input_ids"] == tokenizer.mask_token_id)
    predictions = outputs.logits[mask_indices]
    top_tokens, top_indices = torch.topk(predictions, 5, dim=-1)
    return [tokenizer.decode(token) for token in top_indices[0]]

# Works across languages
texts = [
    "The capital of France is <mask>.",
    "La capital de España es <mask>.",
    "Die Hauptstadt von Deutschland ist <mask>.",
]

for text in texts:
    predictions = predict_masked_token(text)
    print(f"Text: {text}")
    print(f"Predictions: {predictions}\n")
```

## 微调示例

### 编码器

点击查看如何用它微调成基于 Sentence Transformers 的稠密嵌入模型

```
import argparse

from datasets import load_dataset
from sentence_transformers import (
    SentenceTransformer,
    SentenceTransformerTrainer,
    SentenceTransformerTrainingArguments,
)
from sentence_transformers.evaluation import TripletEvaluator
from sentence_transformers.losses import CachedMultipleNegativesRankingLoss
from sentence_transformers.training_args import BatchSamplers

def main():
    # parse the lr & model name
    parser = argparse.ArgumentParser()
    parser.add_argument("--lr", type=float, default=8e-5)
    parser.add_argument("--model_name", type=str, default="jhu-clsp/mmBERT-small")
    args = parser.parse_args()
    lr = args.lr
    model_name = args.model_name
    model_shortname = model_name.split("/")[-1]

    # 1. Load a model to finetune
    model = SentenceTransformer(model_name)

    # 2. Load a dataset to finetune on
    dataset = load_dataset(
        "sentence-transformers/msmarco-co-condenser-margin-mse-sym-mnrl-mean-v1",
        "triplet-hard",
        split="train",
    )
    dataset_dict = dataset.train_test_split(test_size=1_000, seed=12)
    train_dataset = dataset_dict["train"].select(range(1_250_000))
    eval_dataset = dataset_dict["test"]

    # 3. Define a loss function
    loss = CachedMultipleNegativesRankingLoss(model, mini_batch_size=16)  # Increase mini_batch_size if you have enough VRAM

    run_name = f"{model_shortname}-DPR-{lr}"
    # 4. (Optional) Specify training arguments
    args = SentenceTransformerTrainingArguments(
        # Required parameter:
        output_dir=f"output/{model_shortname}/{run_name}",
        # Optional training parameters:
        num_train_epochs=1,
        per_device_train_batch_size=512,
        per_device_eval_batch_size=512,
        warmup_ratio=0.05,
        fp16=False,  # Set to False if GPU can't handle FP16
        bf16=True,  # Set to True if GPU supports BF16
        batch_sampler=BatchSamplers.NO_DUPLICATES,  # (Cached)MultipleNegativesRankingLoss benefits from no duplicates
        learning_rate=lr,
        # Optional tracking/debugging parameters:
        save_strategy="steps",
        save_steps=500,
        save_total_limit=2,
        logging_steps=500,
        run_name=run_name,  # Used in `wandb`, `tensorboard`, `neptune`, etc. if installed
    )

    # 5. (Optional) Create an evaluator & evaluate the base model
    dev_evaluator = TripletEvaluator(
        anchors=eval_dataset["query"],
        positives=eval_dataset["positive"],
        negatives=eval_dataset["negative"],
        name="msmarco-co-condenser-dev",
    )
    dev_evaluator(model)

    # 6. Create a trainer & train
    trainer = SentenceTransformerTrainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        loss=loss,
        evaluator=dev_evaluator,
    )
    trainer.train()

    # 7. (Optional) Evaluate the trained model on the evaluator after training
    dev_evaluator(model)

    # 8. Save the model
    model.save_pretrained(f"output/{model_shortname}/{run_name}/final")

    # 9. (Optional) Push it to the Hugging Face Hub
    model.push_to_hub(run_name, private=False)

if __name__ == "__main__":
    main()
```

点击查看如何用它微调成基于 PyLate 的多向量嵌入模型

```
from datasets import load_dataset
from pylate import losses, models, utils
from sentence_transformers import (
    SentenceTransformerTrainer,
    SentenceTransformerTrainingArguments,
)

def main():
    # Load the datasets required for knowledge distillation (train, queries, documents)
    train = load_dataset(
        path="lightonai/ms-marco-en-bge",
        name="train",
    )

    queries = load_dataset(
        path="lightonai/ms-marco-en-bge",
        name="queries",
    )

    documents = load_dataset(
        path="lightonai/ms-marco-en-bge",
        name="documents",
    )

    # Set the transformation to load the documents/queries texts using the corresponding ids on the fly
    train.set_transform(
        utils.KDProcessing(queries=queries, documents=documents).transform,
    )

    # Define the base model, training parameters, and output directory
    num_train_epochs = 1
    lr = 8e-5
    batch_size = 16
    accum_steps = 1
    model_name = "jhu-clsp/mmBERT-small"
    model_shortname = model_name.split("/")[-1]

    # Set the run name for logging and output directory
    run_name = f"{model_shortname}-colbert-KD-{lr}"
    output_dir = f"output/{model_shortname}/{run_name}"

    # Initialize the ColBERT model from the base model
    model = models.ColBERT(model_name_or_path=model_name)

    # Configure the training arguments (e.g., epochs, batch size, learning rate)
    args = SentenceTransformerTrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_train_epochs,
        per_device_train_batch_size=batch_size,
        fp16=False,  # Set to False if you get an error that your GPU can't run on FP16
        bf16=True,  # Set to True if you have a GPU that supports BF16
        run_name=run_name,
        logging_steps=10,
        learning_rate=lr,
        gradient_accumulation_steps=accum_steps,
        warmup_ratio=0.05,
    )

    # Use the Distillation loss function for training
    train_loss = losses.Distillation(model=model)

    # Initialize the trainer
    trainer = SentenceTransformerTrainer(
        model=model,
        args=args,
        train_dataset=train,
        loss=train_loss,
        data_collator=utils.ColBERTCollator(tokenize_fn=model.tokenize),
    )

    # Start the training process
    trainer.train()

    model.save_pretrained(f"{output_dir}/final")

if __name__ == "__main__":
    main()
```

点击查看如何用它微调成基于 Sentence Transformers 的稀疏检索模型

```
import logging

from datasets import load_dataset

from sentence_transformers import (
    SparseEncoder,
    SparseEncoderModelCardData,
    SparseEncoderTrainer,
    SparseEncoderTrainingArguments,
)
from sentence_transformers.sparse_encoder.evaluation import SparseNanoBEIREvaluator
from sentence_transformers.sparse_encoder.losses import SparseMultipleNegativesRankingLoss, SpladeLoss
from sentence_transformers.training_args import BatchSamplers

logging.basicConfig(format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO)

# 1. Load a model to finetune with 2. (Optional) model card data
model = SparseEncoder(
    "jhu-clsp/mmBERT-small",
    model_card_data=SparseEncoderModelCardData(
        language="en",
        license="apache-2.0",
    )
)

# 3. Load a dataset to finetune on
full_dataset = load_dataset("sentence-transformers/natural-questions", split="train").select(range(100_000))
dataset_dict = full_dataset.train_test_split(test_size=1_000, seed=12)
train_dataset = dataset_dict["train"]
eval_dataset = dataset_dict["test"]

# 4. Define a loss function
loss = SpladeLoss(
    model=model,
    loss=SparseMultipleNegativesRankingLoss(model=model),
    query_regularizer_weight=5e-5,
    document_regularizer_weight=3e-5,
)

# 5. (Optional) Specify training arguments
run_name = "splade-distilbert-base-uncased-nq"
args = SparseEncoderTrainingArguments(
    # Required parameter:
    output_dir=f"models/{run_name}",
    # Optional training parameters:
    num_train_epochs=1,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    learning_rate=2e-5,
    warmup_ratio=0.1,
    fp16=True,  # Set to False if you get an error that your GPU can't run on FP16
    bf16=False,  # Set to True if you have a GPU that supports BF16
    batch_sampler=BatchSamplers.NO_DUPLICATES,  # MultipleNegativesRankingLoss benefits from no duplicate samples in a batch
    # Optional tracking/debugging parameters:
    eval_strategy="steps",
    eval_steps=1000,
    save_strategy="steps",
    save_steps=1000,
    save_total_limit=2,
    logging_steps=200,
    run_name=run_name,  # Will be used in W&B if `wandb` is installed
)

# 6. (Optional) Create an evaluator & evaluate the base model
dev_evaluator = SparseNanoBEIREvaluator(dataset_names=["msmarco", "nfcorpus", "nq"], batch_size=16)

# 7. Create a trainer & train
trainer = SparseEncoderTrainer(
    model=model,
    args=args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    loss=loss,
    evaluator=dev_evaluator,
)
trainer.train()

# 8. Evaluate the model performance again after training
dev_evaluator(model)

# 9. Save the trained model
model.save_pretrained(f"models/{run_name}/final")

# 10. (Optional) Push it to the Hugging Face Hub
model.push_to_hub(run_name)
```

点击查看如何用它微调成基于 Sentence Transformers 的重排器模型

```
import logging
import traceback

import torch
from datasets import load_dataset

from sentence_transformers import SentenceTransformer
from sentence_transformers.cross_encoder import (
    CrossEncoder,
    CrossEncoderModelCardData,
    CrossEncoderTrainer,
    CrossEncoderTrainingArguments,
)
from sentence_transformers.cross_encoder.evaluation import (
    CrossEncoderNanoBEIREvaluator,
    CrossEncoderRerankingEvaluator,
)
from sentence_transformers.cross_encoder.losses import BinaryCrossEntropyLoss
from sentence_transformers.evaluation import SequentialEvaluator
from sentence_transformers.util import mine_hard_negatives

# Set the log level to INFO to get more information
logging.basicConfig(format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO)


def main():
    model_name = "jhu-clsp/mmBERT-small"

    train_batch_size = 64
    num_epochs = 1
    num_hard_negatives = 5  # How many hard negatives should be mined for each question-answer pair

    # 1a. Load a model to finetune with 1b. (Optional) model card data
    model = CrossEncoder(
        model_name,
        model_card_data=CrossEncoderModelCardData(
            language="en",
            license="apache-2.0",
        ),
    )
    print("Model max length:", model.max_length)
    print("Model num labels:", model.num_labels)

    # 2a. Load the GooAQ dataset: https://huggingface.co/datasets/sentence-transformers/gooaq
    logging.info("Read the gooaq training dataset")
    full_dataset = load_dataset("sentence-transformers/gooaq", split="train").select(range(100_000))
    dataset_dict = full_dataset.train_test_split(test_size=1_000, seed=12)
    train_dataset = dataset_dict["train"]
    eval_dataset = dataset_dict["test"]
    logging.info(train_dataset)
    logging.info(eval_dataset)

    # 2b. Modify our training dataset to include hard negatives using a very efficient embedding model
    embedding_model = SentenceTransformer("sentence-transformers/static-retrieval-mrl-en-v1", device="cpu")
    hard_train_dataset = mine_hard_negatives(
        train_dataset,
        embedding_model,
        num_negatives=num_hard_negatives,  # How many negatives per question-answer pair
        margin=0,  # Similarity between query and negative samples should be x lower than query-positive similarity
        range_min=0,  # Skip the x most similar samples
        range_max=100,  # Consider only the x most similar samples
        sampling_strategy="top",  # Sample the top negatives from the range
        batch_size=4096,  # Use a batch size of 4096 for the embedding model
        output_format="labeled-pair",  # The output format is (query, passage, label), as required by BinaryCrossEntropyLoss
        use_faiss=True,
    )
    logging.info(hard_train_dataset)

    # 2c. (Optionally) Save the hard training dataset to disk
    # hard_train_dataset.save_to_disk("gooaq-hard-train")
    # Load again with:
    # hard_train_dataset = load_from_disk("gooaq-hard-train")

    # 3. Define our training loss.
    # pos_weight is recommended to be set as the ratio between positives to negatives, a.k.a. `num_hard_negatives`
    loss = BinaryCrossEntropyLoss(model=model, pos_weight=torch.tensor(num_hard_negatives))

    # 4a. Define evaluators. We use the CrossEncoderNanoBEIREvaluator, which is a light-weight evaluator for English reranking
    nano_beir_evaluator = CrossEncoderNanoBEIREvaluator(
        dataset_names=["msmarco", "nfcorpus", "nq"],
        batch_size=train_batch_size,
    )

    # 4b. Define a reranking evaluator by mining hard negatives given query-answer pairs
    # We include the positive answer in the list of negatives, so the evaluator can use the performance of the
    # embedding model as a baseline.
    hard_eval_dataset = mine_hard_negatives(
        eval_dataset,
        embedding_model,
        corpus=full_dataset["answer"],  # Use the full dataset as the corpus
        num_negatives=30,  # How many documents to rerank
        batch_size=4096,
        include_positives=True,
        output_format="n-tuple",
        use_faiss=True,
    )
    logging.info(hard_eval_dataset)
    reranking_evaluator = CrossEncoderRerankingEvaluator(
        samples=[
            {
                "query": sample["question"],
                "positive": [sample["answer"]],
                "documents": [sample[column_name] for column_name in hard_eval_dataset.column_names[2:]],
            }
            for sample in hard_eval_dataset
        ],
        batch_size=train_batch_size,
        name="gooaq-dev",
        # Realistic setting: only rerank the positives that the retriever found
        # Set to True to rerank *all* positives
        always_rerank_positives=False,
    )

    # 4c. Combine the evaluators & run the base model on them
    evaluator = SequentialEvaluator([reranking_evaluator, nano_beir_evaluator])
    evaluator(model)

    # 5. Define the training arguments
    short_model_name = model_name if "/" not in model_name else model_name.split("/")[-1]
    run_name = f"reranker-{short_model_name}-gooaq-bce"
    args = CrossEncoderTrainingArguments(
        # Required parameter:
        output_dir=f"models/{run_name}",
        # Optional training parameters:
        num_train_epochs=num_epochs,
        per_device_train_batch_size=train_batch_size,
        per_device_eval_batch_size=train_batch_size,
        learning_rate=2e-5,
        warmup_ratio=0.1,
        fp16=False,  # Set to False if you get an error that your GPU can't run on FP16
        bf16=True,  # Set to True if you have a GPU that supports BF16
        dataloader_num_workers=4,
        load_best_model_at_end=True,
        metric_for_best_model="eval_gooaq-dev_ndcg@10",
        # Optional tracking/debugging parameters:
        eval_strategy="steps",
        eval_steps=1000,
        save_strategy="steps",
        save_steps=1000,
        save_total_limit=2,
        logging_steps=200,
        logging_first_step=True,
        run_name=run_name,  # Will be used in W&B if `wandb` is installed
        seed=12,
    )

    # 6. Create the trainer & start training
    trainer = CrossEncoderTrainer(
        model=model,
        args=args,
        train_dataset=hard_train_dataset,
        loss=loss,
        evaluator=evaluator,
    )
    trainer.train()

    # 7. Evaluate the final model, useful to include these in the model card
    evaluator(model)

    # 8. Save the final model
    final_output_dir = f"models/{run_name}/final"
    model.save_pretrained(final_output_dir)

    # 9. (Optional) save the model to the Hugging Face Hub!
    # It is recommended to run `huggingface-cli login` to log into your Hugging Face account first
    try:
        model.push_to_hub(run_name)
    except Exception:
        logging.error(
            f"Error uploading model to the Hugging Face Hub:\n{traceback.format_exc()}To upload it manually, you can run "
            f"`huggingface-cli login`, followed by loading the model using `model = CrossEncoder({final_output_dir!r})` "
            f"and saving it using `model.push_to_hub('{run_name}')`."
        )


if __name__ == "__main__":
    main()
```

## 模型家族与链接

**标准模型：**

- [mmBERT-small](https://huggingface.co/jhu-clsp/mmBERT-small)（总参数 140M，非嵌入参数 42M）
- [mmBERT-base](https://huggingface.co/jhu-clsp/mmBERT-base)（总参数 307M，非嵌入参数 110M）

**研究资源：**

- [🤗 mmBERT 模型集合](https://huggingface.co/collections/jhu-clsp/mmbert-a-modern-multilingual-encoder-68b725831d7c6e3acc435ed4)
- [📝 论文](https://arxiv.org/abs/2509.06888)
- [🗂️ 训练数据](https://huggingface.co/datasets/jhu-clsp/mmbert-pretrain-p1-fineweb2-langs)（3T+ token，完全开放）
- [💻 GitHub 仓库](https://github.com/jhu-clsp/mmBERT)
- [📊 训练 checkpoint](https://huggingface.co/jhu-clsp/mmBERT-checkpoints)，供研究训练过程或继续预训练

## 文中提到的模型 3

## 文中提到的数据集 4

## 文中提到的 Collections 1

我们博客的更多文章

llm

nlp

community

## Ettin Suite: SoTA Paired Encoders and Decoders

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6362d9712691058b19de1ba4/Hdqj5aGrFJJbF7oUSzoIh.jpeg)
- ![](https://huggingface.co/avatars/253dcce19a22cb745038a879f480baaf.svg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/63e410e88083f19a218be964/8gqsYilSTSCt8E3JmajP-.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1620819560688-609bbe2f4932693ca2009d6a.jpeg)
- +2

83

2025 年 7 月 16 日

llm

nlp

reasoning

Hot

## SmolLM3: smol, multilingual, long-context reasoner

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/651e96991b97c9f33d26bde6/-Bqs6qrmz0yCfwtB2e-6q.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6375a7603eabfeba1a28f03f/7pN7IWqhD8GbDu6wLDoE8.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1613655355830-noauth.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1644220542819-noauth.jpeg)
- +19

799

2025 年 7 月 8 日

### 社区

StephennFernandes

2025 年 9 月 12 日

有人能指个路吗：我想把 mmBERT 模型用在 BERTscore（一个翻译评估指标）上该怎么用？

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6362d9712691058b19de1ba4/Hdqj5aGrFJJbF7oUSzoIh.jpeg)](https://huggingface.co/orionweller)


orionweller

本文作者

2025 年 9 月 17 日

Hi [@StephennFernandes](https://huggingface.co/StephennFernandes) ！距离我上次用 BERTScore 已经过了挺久了，但凡是看到写着其他 BERT 模型（或 XLM-R 之类）的地方，直接把模型名替换成 mmBERT 就行。建议看看 [https://github.com/Tiiiger/bert_score](https://github.com/Tiiiger/bert_score) 了解更多细节，如果还有不清楚的地方，可以在那里提个 issue。

deleted

2025 年 10 月 31 日


此评论已被隐藏

将文件拖入文本输入框、粘贴，或

点击此处

，即可上传图像、音频和视频。

点击或粘贴此处上传图片

· [注册](https://huggingface.co/join?next=%2Fblog%2Fmmbert)或[登录](https://huggingface.co/login?next=%2Fblog%2Fmmbert)发表评论



- [![](https://huggingface.co/avatars/0102bcf0db4e822b8bf61ae92305680f.svg)](https://huggingface.co/bitmman-nch)
- [![](https://huggingface.co/avatars/16c289ac2f322e0816d6d5991b618254.svg)](https://huggingface.co/Francois2511)
- [![](https://huggingface.co/avatars/3648c03f5b5f40cd208d46fd3b582739.svg)](https://huggingface.co/bogdanminko)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/tI3V8-PZ8d3CC32fzO31e.png)](https://huggingface.co/Stars321123)
- [![](https://huggingface.co/avatars/6aad4ae2b795578e37fd3723879bff85.svg)](https://huggingface.co/Jyo-K)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/65bd78aeb7db0ab095469e31/jj3kMgx_snMK3AOoJwRwr.jpeg)](https://huggingface.co/Ihssane123)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6317233cc92fd6fee317e030/cJHSvvimr1kqgQfHOjO5n.png)](https://huggingface.co/tomaarsen)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/64b999a40b24527e9c25583a/xFHCewJdf5EGn8qDPypqy.jpeg)](https://huggingface.co/DavidGF)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/60f2fc91b92afccb7c34b8ed/W2-Nay12Ef4Ltyaf8EKE9.jpeg)](https://huggingface.co/gabrielmbmb)
- [![](https://huggingface.co/avatars/7a4067accdd1005f78c3c4adad3ee0a5.svg)](https://huggingface.co/Samoed)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/R4llnPAHwhLW99wL9AL_M.png)](https://huggingface.co/zl369)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/646264832538819c729e32ba/MVxNj8FCQzyDEcBuUvivo.jpeg)](https://huggingface.co/adaamko)

## 文中提到的模型 3

## 文中提到的数据集 4

## 文中提到的 Collections 1
