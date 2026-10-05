---
vendor: huggingface
title: Hugging Face 中的 Patch Time Series Transformer
original_title: Patch Time Series Transformer in Hugging Face
url: https://huggingface.co/blog/patchtst
date: 2022-11-27
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: 71fbe43992a8
---

# Hugging Face 中的 Patch Time Series Transformer——入门

Nam Nguyen（namctin）、Wesley M. Gifford（wmgifford）、Arindam Jati（ajati）、Vijay Ekambaram（vijaye12）、Kashif Rasul（kashif）

在这篇博客里，我们给出如何上手 PatchTST 的示例。我们先在 Electricity 数据上演示 `PatchTST` 的预测能力。然后我们用先前训练好的模型，通过它在 electrical transformer (ETTh1) 数据集上做零样本预测，来演示 `PatchTST` 的迁移学习能力。零样本预测性能表示模型在 `target` 域上的 `test` 性能，而在目标域上不做任何训练。随后，我们会在目标数据的 `train` 部分对预训练模型做线性探测（linear probing）以及（之后的）微调，并在目标数据的 `test` 部分上验证预测性能。

`PatchTST` 模型由 Yuqi Nie、Nam H. Nguyen、Phanwadee Sinthong、Jayant Kalagnanam 在论文 [A Time Series is Worth 64 Words: Long-term Forecasting with Transformers](https://huggingface.co/papers/2211.14730) 中提出，并在 ICLR 2023 上发表。

## PatchTST 概览

从高层看，模型把批次里的单条时间序列向量化为给定大小的 patch，再通过一个 Transformer 编码得到的向量序列，最后由一个合适的 head 输出预测长度的预报。

该模型基于两个关键组件：

- 把时间序列分割为子序列级别的 patch，作为 Transformer 的输入 token；
- 通道独立（channel-independence），每个通道包含一条单变量时间序列，所有序列共享相同的嵌入和 Transformer 权重，即一个[全局](https://doi.org/10.1016/j.ijforecast.2021.03.004)单变量模型。

patch 设计天然带来三方面好处：

- 嵌入中保留了局部语义信息；
- 借助 patch 之间的步长，在相同回看窗口下注意力图的计算与内存用量二次方地减少；
- 通过在 patch 长度（输入向量大小）与上下文长度（序列数）之间做权衡，模型可以关注更长的历史。

此外，PatchTST 采用模块化设计，无缝支持掩码时间序列预训练以及直接的时间序列预测。

| [![PatchTST model schematics](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/patchtst/patchtst-arch.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/patchtst/patchtst-arch.png) |
| --- |
| (a) PatchTST 模型概览：一批 M 条长度为 L 的时间序列各自独立处理（通过 reshape 到 batch 维度）经由 Transformer 主干，再把得到的 batch reshape 回 M 条长度为 T 的预测序列。每条*单变量*序列既可以用有监督方式处理 (b)，其中 patch 化的向量集用于输出完整预测长度；也可以用自监督方式 (c)，预测被掩码的 patch。 |

## 安装

本 demo 需要 Hugging Face [`Transformers`](https://github.com/huggingface/transformers) 作为模型，以及 IBM `tsfm` 包用于辅助数据预处理。我们可以克隆 `tsfm` 仓库并按以下步骤同时安装两者。

- 克隆公开的 IBM Time Series Foundation Model 仓库 [`tsfm`](https://github.com/ibm/tsfm)。`pip install git+https://github.com/IBM/tsfm.git `
- 安装 Hugging Face [`Transformers`](https://github.com/huggingface/transformers#installation)`pip install transformers `
- 在 `python` 终端里用以下命令测试。`from transformers import PatchTSTConfig from tsfm_public.toolkit.dataset import ForecastDFDataset `

## 第一部分：在 Electricity 数据集上预测

这里我们直接在 Electricity 数据集（来自 [https://github.com/zhouhaoyi/Informer2020](https://github.com/zhouhaoyi/Informer2020)）上训练一个 PatchTST 模型，并评估其性能。

```
# Standard
import os

# Third Party
from transformers import (
    EarlyStoppingCallback,
    PatchTSTConfig,
    PatchTSTForPrediction,
    Trainer,
    TrainingArguments,
)
import numpy as np
import pandas as pd

# First Party
from tsfm_public.toolkit.dataset import ForecastDFDataset
from tsfm_public.toolkit.time_series_preprocessor import TimeSeriesPreprocessor
from tsfm_public.toolkit.util import select_by_index
```

### 设置随机种子

```
from transformers import set_seed

set_seed(2023)
```

### 加载并准备数据集

在下一个单元格里，请调整以下参数以适配你的应用：

- `dataset_path`：本地 .csv 文件路径，或目标数据的 csv 文件网页地址。数据用 pandas 加载，`pd.read_csv` 支持的一切都支持：([https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html))。
- `timestamp_column`：含时间戳信息的列名，若没有此列则用 `None`。
- `id_columns`：指定各时间序列 ID 的列名列表。若不存在 ID 列，用 `[]`。
- `forecast_columns`：要建模的列列表
- `context_length`：作为模型输入所用的历史数据量。从输入 dataframe 中提取长度等于 `context_length` 的输入时间序列数据窗口。对多时间序列数据集，上下文窗口的创建会保证它们落在单条时间序列内（即单个 ID）。
- `forecast_horizon`：要预测的未来时间戳数。
- `train_start_index`、`train_end_index`：加载数据中界定训练数据的起止索引。
- `valid_start_index`、`eval_end_index`：加载数据中界定验证数据的起止索引。
- `test_start_index`、`eval_end_index`：加载数据中界定测试数据的起止索引。
- `patch_length`：`PatchTST` 模型的 patch 长度。建议选一个能整除 `context_length` 的值。
- `num_workers`：PyTorch dataloader 中的 CPU worker 数。
- `batch_size`：批大小。

数据先被加载进一个 Pandas dataframe，并划分为训练、验证和测试部分。随后把 Pandas dataframe 转换为训练所需的合适 PyTorch 数据集。

```
# The ECL data is available from https://github.com/zhouhaoyi/Informer2020?tab=readme-ov-file#data
dataset_path = "~/data/ECL.csv"
timestamp_column = "date"
id_columns = []

context_length = 512
forecast_horizon = 96
patch_length = 16
num_workers = 16  # Reduce this if you have low number of CPU cores
batch_size = 64  # Adjust according to GPU memory
```

```
data = pd.read_csv(
    dataset_path,
    parse_dates=[timestamp_column],
)
forecast_columns = list(data.columns[1:])

# get split
num_train = int(len(data) * 0.7)
num_test = int(len(data) * 0.2)
num_valid = len(data) - num_train - num_test
border1s = [
    0,
    num_train - context_length,
    len(data) - num_test - context_length,
]
border2s = [num_train, num_train + num_valid, len(data)]

train_start_index = border1s[0]  # None indicates beginning of dataset
train_end_index = border2s[0]

# we shift the start of the evaluation period back by context length so that
# the first evaluation timestamp is immediately following the training data
valid_start_index = border1s[1]
valid_end_index = border2s[1]

test_start_index = border1s[2]
test_end_index = border2s[2]

train_data = select_by_index(
    data,
    id_columns=id_columns,
    start_index=train_start_index,
    end_index=train_end_index,
)
valid_data = select_by_index(
    data,
    id_columns=id_columns,
    start_index=valid_start_index,
    end_index=valid_end_index,
)
test_data = select_by_index(
    data,
    id_columns=id_columns,
    start_index=test_start_index,
    end_index=test_end_index,
)

time_series_preprocessor = TimeSeriesPreprocessor(
    timestamp_column=timestamp_column,
    id_columns=id_columns,
    input_columns=forecast_columns,
    output_columns=forecast_columns,
    scaling=True,
)
time_series_preprocessor = time_series_preprocessor.train(train_data)
```

```
train_dataset = ForecastDFDataset(
    time_series_preprocessor.preprocess(train_data),
    id_columns=id_columns,
    timestamp_column="date",
    input_columns=forecast_columns,
    output_columns=forecast_columns,
    context_length=context_length,
    prediction_length=forecast_horizon,
)
valid_dataset = ForecastDFDataset(
    time_series_preprocessor.preprocess(valid_data),
    id_columns=id_columns,
    timestamp_column="date",
    input_columns=forecast_columns,
    output_columns=forecast_columns,
    context_length=context_length,
    prediction_length=forecast_horizon,
)
test_dataset = ForecastDFDataset(
    time_series_preprocessor.preprocess(test_data),
    id_columns=id_columns,
    timestamp_column="date",
    input_columns=forecast_columns,
    output_columns=forecast_columns,
    context_length=context_length,
    prediction_length=forecast_horizon,
)
```

### 配置 PatchTST 模型

接下来，我们用一个配置实例化一个随机初始化的 `PatchTST` 模型。下面的设置控制与架构相关的各个超参数。

- `num_input_channels`：时间序列数据中输入通道（或维度）的数量。它自动设为预测列的数量。
- `context_length`：如上所述，作为模型输入所用的历史数据量。
- `patch_length`：从上下文窗口（长度为 `context_length`）中提取的 patch 长度。
- `patch_stride`：从上下文窗口提取 patch 时使用的步长。
- `random_mask_ratio`：为预训练模型而被完全掩码的输入 patch 比例。
- `d_model`：transformer 层的维度。
- `num_attention_heads`：Transformer 编码器中每个注意力层的注意力头数。
- `num_hidden_layers`：编码器层数。
- `ffn_dim`：编码器中中间层（常称前馈层）的维度。
- `dropout`：编码器中所有全连接层的 dropout 概率。
- `head_dropout`：模型 head 中使用的 dropout 概率。
- `pooling_type`：嵌入的池化。支持 `"mean"`、`"max"` 和 `None`。
- `channel_attention`：激活 Transformer 中的通道注意力块，让通道彼此关注。
- `scaling`：是否通过 "mean" 缩放器、"std" 缩放器缩放输入目标，若为 `None` 则不缩放。若为 `True`，缩放器设为 `"mean"`。
- `loss`：模型对应 `distribution_output` head 的损失函数。对参数化分布是负对数似然（`"nll"`），对点估计是均方误差 `"mse"`。
- `pre_norm`：若 pre_norm 设为 `True`，归一化在自注意力之前应用。否则归一化在残差块之后。
- `norm_type`：每个 Transformer 层的归一化。可以是 `"BatchNorm"` 或 `"LayerNorm"`。

关于参数的完整细节，请参考[文档](https://huggingface.co/docs/transformers/main/en/model_doc/patchtst#transformers.PatchTSTConfig)。

```
config = PatchTSTConfig(
    num_input_channels=len(forecast_columns),
    context_length=context_length,
    patch_length=patch_length,
    patch_stride=patch_length,
    prediction_length=forecast_horizon,
    random_mask_ratio=0.4,
    d_model=128,
    num_attention_heads=16,
    num_hidden_layers=3,
    ffn_dim=256,
    dropout=0.2,
    head_dropout=0.2,
    pooling_type=None,
    channel_attention=False,
    scaling="std",
    loss="mse",
    pre_norm=True,
    norm_type="batchnorm",
)
model = PatchTSTForPrediction(config)
```

### 训练模型

接下来，我们可以借助 Hugging Face 的 [Trainer](https://huggingface.co/docs/transformers/main_classes/trainer) 类，基于直接预测策略训练模型。我们先定义 [TrainingArguments](https://huggingface.co/docs/transformers/main_classes/trainer#transformers.TrainingArguments)，它列出训练相关的各种超参数，比如 epoch 数、学习率等等。

```
training_args = TrainingArguments(
    output_dir="./checkpoint/patchtst/electricity/pretrain/output/",
    overwrite_output_dir=True,
    # learning_rate=0.001,
    num_train_epochs=100,
    do_eval=True,
    evaluation_strategy="epoch",
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=batch_size,
    dataloader_num_workers=num_workers,
    save_strategy="epoch",
    logging_strategy="epoch",
    save_total_limit=3,
    logging_dir="./checkpoint/patchtst/electricity/pretrain/logs/",  # Make sure to specify a logging directory
    load_best_model_at_end=True,  # Load the best model when training ends
    metric_for_best_model="eval_loss",  # Metric to monitor for early stopping
    greater_is_better=False,  # For loss
    label_names=["future_values"],
)

# Create the early stopping callback
early_stopping_callback = EarlyStoppingCallback(
    early_stopping_patience=10,  # Number of epochs with no improvement after which to stop
    early_stopping_threshold=0.0001,  # Minimum improvement required to consider as improvement
)

# define trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=valid_dataset,
    callbacks=[early_stopping_callback],
    # compute_metrics=compute_metrics,
)

# pretrain
trainer.train()
```

| Epoch | Training Loss | Validation Loss |
| --- | --- | --- |
| 1 | 0.455400 | 0.215057 |
| 2 | 0.241000 | 0.179336 |
| 3 | 0.209000 | 0.158522 |
| ... | ... | ... |
| 83 | 0.128000 | 0.111213 |

### 在源域的测试集上评估模型

接下来，我们可以借助 `trainer.evaluate()` 来计算测试指标。虽然这不是本任务要评判的目标指标，但它提供了一个合理的检查，确认预训练模型已正确训练。注意 PatchTST 的训练和评估损失是均方误差（MSE）损失。因此我们在后续的评估实验中不再单独计算 MSE 指标。

```
results = trainer.evaluate(test_dataset)
print("Test result:")
print(results)

>>> Test result:
    {'eval_loss': 0.1316315233707428, 'eval_runtime': 5.8077, 'eval_samples_per_second': 889.332, 'eval_steps_per_second': 3.616, 'epoch': 83.0}
```

`0.131` 的 MSE 非常接近原始 PatchTST 论文在 Electricity 数据集上报告的值。

### 保存模型

```
save_dir = "patchtst/electricity/model/pretrain/"
os.makedirs(save_dir, exist_ok=True)
trainer.save_model(save_dir)
```

## 第二部分：从 Electricity 到 ETTh1 的迁移学习

本节我们演示 `PatchTST` 模型的迁移学习能力。我们用之前在 Electricity 数据集上预训练的模型，在 ETTh1 数据集上做零样本预测。

所谓迁移学习，指我们先在 `source` 数据集上为一个预测任务预训练模型（上面我们在 `Electricity` 数据集上做了这件事）。然后我们用预训练模型在 `target` 数据集上做零样本预测。所谓零样本，指不在 `target` 域上做额外训练就直接测性能。我们希望模型从预训练中获取了足够的知识，能迁移到不同的数据集。随后我们会在目标数据的 `train` split 上对预训练模型做线性探测（以及之后的）微调，并在目标数据的 `test` split 上验证预测性能。在这个例子里，源数据集是 `Electricity` 数据集，目标数据集是 ETTh1。

### 在 ETTh1 数据上做迁移学习。

所有评估都在 `ETTh1` 数据的 `test` 部分进行。

步骤 1：直接评估 electricity 预训练模型。这是零样本性能。

步骤 2：做完线性探测后再评估。

步骤 3：做完完整微调后再评估。

### 加载 ETTh 数据集

下面我们把 `ETTh1` 数据集作为 Pandas dataframe 加载。然后创建训练、验证、测试三个 split。接着我们用 `TimeSeriesPreprocessor` 类为模型准备每个 split。

```
dataset = "ETTh1"
```

```
print(f"Loading target dataset: {dataset}")
dataset_path = f"https://raw.githubusercontent.com/zhouhaoyi/ETDataset/main/ETT-small/{dataset}.csv"
timestamp_column = "date"
id_columns = []
forecast_columns = ["HUFL", "HULL", "MUFL", "MULL", "LUFL", "LULL", "OT"]
train_start_index = None  # None indicates beginning of dataset
train_end_index = 12 * 30 * 24

# we shift the start of the evaluation period back by context length so that
# the first evaluation timestamp is immediately following the training data
valid_start_index = 12 * 30 * 24 - context_length
valid_end_index = 12 * 30 * 24 + 4 * 30 * 24

test_start_index = 12 * 30 * 24 + 4 * 30 * 24 - context_length
test_end_index = 12 * 30 * 24 + 8 * 30 * 24

>>> Loading target dataset: ETTh1
```

```
data = pd.read_csv(
    dataset_path,
    parse_dates=[timestamp_column],
)

train_data = select_by_index(
    data,
    id_columns=id_columns,
    start_index=train_start_index,
    end_index=train_end_index,
)
valid_data = select_by_index(
    data,
    id_columns=id_columns,
    start_index=valid_start_index,
    end_index=valid_end_index,
)
test_data = select_by_index(
    data,
    id_columns=id_columns,
    start_index=test_start_index,
    end_index=test_end_index,
)

time_series_preprocessor = TimeSeriesPreprocessor(
    timestamp_column=timestamp_column,
    id_columns=id_columns,
    input_columns=forecast_columns,
    output_columns=forecast_columns,
    scaling=True,
)
time_series_preprocessor = time_series_preprocessor.train(train_data)
```

```
train_dataset = ForecastDFDataset(
    time_series_preprocessor.preprocess(train_data),
    id_columns=id_columns,
    input_columns=forecast_columns,
    output_columns=forecast_columns,
    context_length=context_length,
    prediction_length=forecast_horizon,
)
valid_dataset = ForecastDFDataset(
    time_series_preprocessor.preprocess(valid_data),
    id_columns=id_columns,
    input_columns=forecast_columns,
    output_columns=forecast_columns,
    context_length=context_length,
    prediction_length=forecast_horizon,
)
test_dataset = ForecastDFDataset(
    time_series_preprocessor.preprocess(test_data),
    id_columns=id_columns,
    input_columns=forecast_columns,
    output_columns=forecast_columns,
    context_length=context_length,
    prediction_length=forecast_horizon,
)
```

### 在 ETTH 上做零样本预测

由于我们要开箱测试预测性能，我们加载上面预训练好的模型。

```
finetune_forecast_model = PatchTSTForPrediction.from_pretrained(
    "patchtst/electricity/model/pretrain/",
    num_input_channels=len(forecast_columns),
    head_dropout=0.7,
)
```

```
finetune_forecast_args = TrainingArguments(
    output_dir="./checkpoint/patchtst/transfer/finetune/output/",
    overwrite_output_dir=True,
    learning_rate=0.0001,
    num_train_epochs=100,
    do_eval=True,
    evaluation_strategy="epoch",
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=batch_size,
    dataloader_num_workers=num_workers,
    report_to="tensorboard",
    save_strategy="epoch",
    logging_strategy="epoch",
    save_total_limit=3,
    logging_dir="./checkpoint/patchtst/transfer/finetune/logs/",  # Make sure to specify a logging directory
    load_best_model_at_end=True,  # Load the best model when training ends
    metric_for_best_model="eval_loss",  # Metric to monitor for early stopping
    greater_is_better=False,  # For loss
    label_names=["future_values"],
)

# Create a new early stopping callback with faster convergence properties
early_stopping_callback = EarlyStoppingCallback(
    early_stopping_patience=10,  # Number of epochs with no improvement after which to stop
    early_stopping_threshold=0.001,  # Minimum improvement required to consider as improvement
)

finetune_forecast_trainer = Trainer(
    model=finetune_forecast_model,
    args=finetune_forecast_args,
    train_dataset=train_dataset,
    eval_dataset=valid_dataset,
    callbacks=[early_stopping_callback],
)

print("\n\nDoing zero-shot forecasting on target data")
result = finetune_forecast_trainer.evaluate(test_dataset)
print("Target data zero-shot forecasting result:")
print(result)

>>> Doing zero-shot forecasting on target data

    Target data zero-shot forecasting result:
    {'eval_loss': 0.3728715181350708, 'eval_runtime': 0.95, 'eval_samples_per_second': 2931.527, 'eval_steps_per_second': 11.579}
```

可以看到，用零样本预测方法我们得到 0.370 的 MSE，接近原始 PatchTST 论文里最先进结果。

接下来看看做线性探测会怎样——线性探测指在冻结的预训练模型之上训练一个线性层。线性探测常用来测试预训练模型的特征性能。

### 在 ETTh1 上做线性探测

我们可以在目标数据的 `train` 部分做一个快速的线性探测，看能否提升 `test` 性能。

```
# Freeze the backbone of the model
for param in finetune_forecast_trainer.model.model.parameters():
    param.requires_grad = False

print("\n\nLinear probing on the target data")
finetune_forecast_trainer.train()
print("Evaluating")
result = finetune_forecast_trainer.evaluate(test_dataset)
print("Target data head/linear probing result:")
print(result)

>>> Linear probing on the target data
```

| Epoch | Training Loss | Validation Loss |
| --- | --- | --- |
| 1 | 0.384600 | 0.688319 |
| 2 | 0.374200 | 0.678159 |
| 3 | 0.368400 | 0.667633 |
| ... | ... | ... |

```
>>> Evaluating

    Target data head/linear probing result:
    {'eval_loss': 0.35652095079421997, 'eval_runtime': 1.1537, 'eval_samples_per_second': 2413.986, 'eval_steps_per_second': 9.535, 'epoch': 18.0}
```

可以看到，仅在一个冻结主干之上训练一个简单的线性层，MSE 就从 0.370 降到 0.357，超过了原始报告的结果！

```
save_dir = f"patchtst/electricity/model/transfer/{dataset}/model/linear_probe/"
os.makedirs(save_dir, exist_ok=True)
finetune_forecast_trainer.save_model(save_dir)

save_dir = f"patchtst/electricity/model/transfer/{dataset}/preprocessor/"
os.makedirs(save_dir, exist_ok=True)
time_series_preprocessor = time_series_preprocessor.save_pretrained(save_dir)
```

最后，看看做完整微调能否进一步取得提升。

### 在 ETTh1 上做完整微调

我们可以在目标数据的 `train` 部分做完整模型微调（而非像上面那样探测最后的线性层），看能否提升 `test` 性能。代码与上面的线性探测任务类似，只是我们不冻结任何参数。

```
# Reload the model
finetune_forecast_model = PatchTSTForPrediction.from_pretrained(
    "patchtst/electricity/model/pretrain/",
    num_input_channels=len(forecast_columns),
    dropout=0.7,
    head_dropout=0.7,
)
finetune_forecast_trainer = Trainer(
    model=finetune_forecast_model,
    args=finetune_forecast_args,
    train_dataset=train_dataset,
    eval_dataset=valid_dataset,
    callbacks=[early_stopping_callback],
)
print("\n\nFinetuning on the target data")
finetune_forecast_trainer.train()
print("Evaluating")
result = finetune_forecast_trainer.evaluate(test_dataset)
print("Target data full finetune result:")
print(result)

>>> Finetuning on the target data
```

| Epoch | Training Loss | Validation Loss |
| --- | --- | --- |
| 1 | 0.348600 | 0.709915 |
| 2 | 0.328800 | 0.706537 |
| 3 | 0.319700 | 0.741892 |
| ... | ... | ... |

```
>>> Evaluating

    Target data full finetune result:
    {'eval_loss': 0.354232519865036, 'eval_runtime': 1.0715, 'eval_samples_per_second': 2599.18, 'eval_steps_per_second': 10.266, 'epoch': 12.0}
```

在这种情形下，用完整微调在 ETTh1 数据集上只有小幅提升。对其他数据集可能有更显著的提升。无论如何，我们把模型保存下来。

```
save_dir = f"patchtst/electricity/model/transfer/{dataset}/model/fine_tuning/"
os.makedirs(save_dir, exist_ok=True)
finetune_forecast_trainer.save_model(save_dir)
```

## 总结

在这篇博客里，我们给出了训练 PatchTST 完成预测与迁移学习相关任务的逐步指南，演示了多种微调方式。我们希望便于把 PatchTST HF 模型轻松集成到你的预测用例中，也希望这份内容能成为有用资源，加速 PatchTST 的采用。感谢阅读我们的博客，希望这些信息对你的项目有所帮助。
