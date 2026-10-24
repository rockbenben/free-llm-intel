---
vendor: huggingface
title: 使用 IBM Granite 时间序列模型进行集合预测
original_title: 
url: https://huggingface.co/blog/ibm-research/granite-timeseries-ensemble-r1
date: 2026-10-22
lang: zh
captured: 2026-10-23
extractor: readability-v1
translator: mt
status: translated
body_sha: 4c63a353d675
---

[返回文章](https://huggingface.co/blog)

# 使用 IBM Granite 时间序列模型进行集合预测

企业文章

发布于 2026 年 10 月 22 日

14

- [![](https://huggingface.co/avatars/8ff9f76420b50f8d733495fcf9bd0ea9.svg)](https://huggingface.co/Fearghal)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/WSgVWqeGen77Vh5GzTL-O.png)](https://huggingface.co/Jake893)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/kyVdmjyfIsLZqFKhaIRF9.png)](https://huggingface.co/okoyelisbon)
- [![](https://huggingface.co/avatars/63644064768d8ba22487d7b5ffeab88d.svg)](https://huggingface.co/ElPanaBru)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/66d6ee839fcb6b494fcc2cbc/AFMksMD6oOy4ec52PUdnL.png)](https://huggingface.co/Bangla84PL)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6747d1af433d60be7006cf02/YrCokyziqIX41i1NhW6vN.png)](https://huggingface.co/Babysworld)

[![Fearghal O'Donncha 的头像](https://huggingface.co/avatars/8ff9f76420b50f8d733495fcf9bd0ea9.svg)](https://huggingface.co/Fearghal)

菲尔格尔·奥唐查

菲尔格尔

[![IBM Research 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Chandramouli Kamanchi 的头像](https://huggingface.co/avatars/317e008622f276f00309f81af04b3d3b.svg)](https://huggingface.co/rry003)

钱德拉穆利·卡曼奇

ry003

[![IBM Research 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Guruprasad 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/64ca639d7a4f23635701313e/ZaCrxHOn4feQ39vtBAID2.jpeg)](https://huggingface.co/Ranjini)

古鲁普拉萨德

兰吉尼

[![IBM Research 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Wesley M. Gifford 的头像](https://huggingface.co/avatars/8833ff37c5ccc477f1593cd8ad5a1208.svg)](https://huggingface.co/wmgifford)

韦斯利·M·吉福德

威姆吉福德

[![IBM Research 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Natalia Martinez Gil 的头像](https://huggingface.co/avatars/9041e569f6eb98b79ec3c9e7bcfd302c.svg)](https://huggingface.co/natalmg91)

娜塔莉亚·马丁内斯·吉尔

出生mg91

[![IBM Research 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Bradley Eck 的头像](https://huggingface.co/avatars/3ee5aa141090176f0c981322072fce25.svg)](https://huggingface.co/bradleyjeck)

布拉德利·艾克

布拉德利杰克

[![IBM Research 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Pankaj Dayama 的头像](https://huggingface.co/avatars/ed8ccd6d4fbc0e68ce03930eae039c4b.svg)](https://huggingface.co/pankajdayama)

潘卡吉·达亚玛

潘卡吉达亚马

[![IBM Research 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Roman Vaculin 的头像](https://huggingface.co/avatars/c9d15c05751f0841bc0c431da3262d50.svg)](https://huggingface.co/vaculin)

罗曼·瓦库林

真空蛋白

[![IBM Research 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Ayhan Sebin 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/64e8143f6de557454220921e/aNouKBrKm1dnN9pI1JXlp.jpeg)](https://huggingface.co/ayhansebin)

艾汉·塞宾

艾汉瑟宾

[![IBM Research 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

*四个开放的 Granite 模型，一个可扩展的预测界面，减少对使用哪个模型的猜测。*

预训练的时间序列模型无需对数据集进行训练即可进行预测，但您仍然必须选择一个。能够很好地处理平滑工业信号的模型可能会难以应对嘈杂的零售需求或较长的季节性范围，最佳选择取决于系列和任务。

Granite Timeseries Ensemble 将这种选择简化为合理的默认值。一种配方结合了四种互补的 Granite 架构，并返回中值和分位数预测，无需重新训练，也无需拟合整体权重。从概率集成（统一概率池）开始，比较自适应四分位距 (IQR) 集成，并使用兼容的预测器扩展相同的接口。合奏配方及其默认 Granite 成员均获得许可。

这个想法在天气预报中很常见。 [集合预报](https://www.ecmwf.int/en/about/media-centre/focus/2017/fact-sheet-ensemble-weather-forecasting) 探索一系列可能的结果，而[北美多模型集合](https://www.cpc.ncep.noaa.gov/products/NMME/NMME_description.html) 等系统结合了不同的模型进行季节预测。时间序列预测以类似的方式受益：互补模型提供了对接下来发生的事情的不同观点，并且集合将这些观点合并为一个预测。

## 尝试 Granite Timeseries Ensemble

安装 Granite TSFM 并直接从 Hugging Face 加载推荐的四模型配方：
```
pip install "granite-tsfm>=0.3.11"
```

```
import pandas as pd

from tsfm_public.models.ensemble.modeling_ensemble import QuantileEnsembleForecaster

df = pd.read_csv(
    "https://raw.githubusercontent.com/zhouhaoyi/ETDataset/main/ETT-small/ETTh1.csv",
    parse_dates=["date"],
)

ensemble = QuantileEnsembleForecaster.from_pretrained(
    "ibm-granite/granite-timeseries-ensemble-r1",
)

result = ensemble(
    df.tail(1024),
    timestamp_column="date",
    target_columns=["OT"],
    context_length=1024,
    prediction_length=24,
)

print(result.prediction_outputs) # point forecast
print(result.quantile_outputs)   # quantiles
```
该配方存储整体配置而不是合并的模型权重。它在运行时下载四个成员检查点，因此为第一次运行留出额外的时间。有关完整配置、成员检查点、评估详细信息和限制，请参阅[模型卡](https://huggingface.co/ibm-granite/granite-timeseries-ensemble-r1)。

`result.prediction_outputs` 包含点预测，而 `result.quantile_outputs` 包含分位数预测，默认范围为 0.1 到 0.9。应用程序可以使用点值作为中心预测并使用选定的分位数来表示预测范围。例如，0.1 和 0.9 分位数定义了名义覆盖率 80% 的中心预测区间。

## 乐团成员

默认配方结合了四个具有不同架构的预先训练的 Granite 模型：

|型号|建筑|
| --- | --- |
| [Granite PatchTST-FM-r1](https://huggingface.co/ibm-granite/granite-timeseries-patchtst-fm-r1) |修补变压器|
| [Granite PatchTST-FM-r2](https://huggingface.co/ibm-granite/granite-timeseries-patchtst-fm-r2) |修补Conformer |
| [Granite FlowState-r1.1](https://huggingface.co/ibm-granite/granite-timeseries-flowstate-r1) |状态空间模型|
| [Granite TTM-r3](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r3) | Tiny Time Mixers（MLP 混合器）|

有关背景信息，请参阅 [PatchTST-FM-r1 论文](https://arxiv.org/abs/2602.06909)、[PatchTST-FM-r2 架构概述](https://huggingface.co/blog/ibm-research/ibm-releases-sota-granite-time-series)、[FlowState论文](https://arxiv.org/abs/2508.05287)，以及[Tiny Time Mixers 论文](https://arxiv.org/abs/2401.03955)。

这些架构以不同的方式捕捉趋势、季节性和局部变化，因此它们的错误不必重合。 [预测组合的 50 年回顾](https://arxiv.org/abs/2205.04216) 描述了组合预测如何降低选择错误单一模型的风险，同时强调成员质量和多样性仍然很重要。

[![四个 Granite 预测模型提供通用分位数接口和两种聚合方法之一。](https://huggingface.co/buckets/rry003/blogcomponents/resolve/ensemble_overview.svg?download=true)](https://huggingface.co/buckets/rry003/blogcomponents/resolve/ensemble_overview.svg?download=true)

## 两种结合预测的方法

每个成员返回分位数预测。两种主要方法使用不同的规则将这些预测转化为一种预测分布及其中位数。

### 概率集成：推荐的默认值

概率集成（统一概率池）赋予每个成员同等的影响力，将其分位数预测汇集到概率空间中，并从组合值中提取所需的分位数。由于权重是固定的，因此没有拟合步骤，也没有权重超参数来调整新系列。

[预测组合难题](https://onlinelibrary.wiley.com/doi/10.1111/j.1468-0084.2008.00541.x) 提供了有用的动机：在点预测中，简单的等权重组合通常比估计权重的方法表现得更好。这个秘诀将相同的等影响思想应用于概率预测。这是上面示例中默认加载的。

### IQR Ensemble：自适应替代方案

IQR Ensemble 根据成员的预测差额对成员进行加权，使较小的区间具有更大的影响力。它从第 25 个百分位和第 75 个百分位周围最接近的可用分位数估算出每个成员的四分位数范围。权重因样本、目标和水平步长而异，并且与概率集成一样，历史预测误差不会拟合任何内容。等渗回归可防止组合分位数交叉。

更窄的区间并不一定意味着更准确或更好校准的预测，IQR 加权可能有利于过度自信的成员。如果您想进行实验，配方会公开温度设置（较高的值使体重趋于均匀）以及对任何单个成员体重的可选上限。

通过仅更改子文件夹来加载评估的 IQR 配方：
```
ensemble = QuantileEnsembleForecaster.from_pretrained(
    "ibm-granite/granite-timeseries-ensemble-r1",
    subfolder="recipes/granite-iqr",
)
```
## 我应该使用哪种方法？

|您的目标|以 | 开头为什么 |
| --- | --- | --- |
|一个简单的默认 |概率系综|同等影响力，无需安装权重 |
|基于预测价差的自适应加权| IQR 合奏 |影响力随每个成员的预测传播而变化 |

从概率系综开始。如果预测价差看起来对您的应用有帮助，请在代表性数据上将 IQR 集成与它进行比较，因为准确性和校准取决于系列和范围。

## 乐团的成员有进步吗？

我们在 97 个 GIFT-Eval 数据集配置上评估了这两种食谱。模型预测没有进行微调，并且没有使用测试目标来选择或拟合聚合方法。在这里，我们使用 2026 年 10 月 20 日发布的排行榜分数和排名，将官方集成提交结果与四个组成模型进行比较。

GIFT-Eval 报告点预测的 *MASE* 和概率预测的 *CRPS/MWQL*（基准的“mean_weighted_sum_quantile_loss”指标）。分数被归一化为季节性朴素，并在配置之间进行几何平均。越低越好。

|预测|梅斯 ↓ | MASE 排名 ↓ | CRPS / MWQL ↓ | CRPS 排名 ↓ |
| --- | --- | --- | --- | --- |
|花岗岩整体 R1 — 问题 | **0.683**★ | **47.175**★ | 0.471 | 0.471 50.948 |
|花岗岩整体 R1 — IQR | 0.684 | 0.684 48.773 | 48.773 0.471 | 0.471 **47.619**★ |
|花岗岩补丁TST-FM-r2 | 0.685 | 0.685 51.371 | **0.467**★ | 48.918 | 48.918
|花岗岩 FlowState-r1.1 | 0.701 | 0.701 66.474 | 66.474 0.490 | 0.490 69.485 | 69.485
|花岗岩补丁TST-FM-r1 | 0.717 | 0.717 74.794 | 74.794 0.488 | 0.488 68.134 | 68.134
|花岗岩 TTM-r3 | 0.724 | 0.724 83.062 | 0.520 | 88.959 | 88.959

★ 显示的预测中的最佳值。越低越好。

排名列根据完整 GIFT-Eval 参考排行榜（而不仅仅是这六个预测）计算每个配置的平均排名，因此排名值可能会随着条目添加到排行榜而发生变化。

两个组合在总体 MASE 和平均 MASE 排名方面均优于所有四个单独成员。概率集成在这六个预测中实现了最低的 MASE：0.683，而 PatchTST-FM-r2 的 MASE 为 0.685。较低的平均 MASE Rank 表明 GIFT-Eval 的不同数据集配置的相对点预测性能更强。总之，这些结果支持将整体作为一个实用的起点，而不需要开发人员提前选择最强的单独架构。 MASE 相对于最佳单个成员的优势很小，因此主要好处是稳健性：您无需事先知道哪种架构适合您的数据，即可获得可比较或更好的聚合准确性。

PatchTST-FM-r2 保留最低的 CRPS/MWQL 总分。在这六种预测中，IQR 集成的平均 CRPS 排名最低，而概率集成在该指标上排名落后于 PatchTST-FM-r2。因此，聚合误差和平均排名有利于不同的选择。

在 2026 年 10 月 20 日的比较中，集成方法在 MASE Rank 和 CRPS Rank 的合格系统中排名第三。下图显示了这两种方法以及每个指标的十个最佳合格参考系统。一些系统，包括被排除为微调或非许可许可的条目，得分比这两种方法都好，因此整体的价值并不在于它在排行榜上名列前茅。单一默认值可以在多个系列中提供强大、一致的结果，而无需您选择成员。

[![Granite 整体和合格参考系统的 GIFT-Eval 平均排名比较。越低越好。](https://huggingface.co/buckets/rry003/blogcomponents/resolve/gift_eval_ranks_granite.png?download=true)](https://huggingface.co/buckets/rry003/blogcomponents/resolve/gift_eval_ranks_granite.png?download=true)

*图：2026 年 10 月 20 日的 GIFT-Eval 平均排名排名，显示了两个 Granite 整体以及每个指标的十个最佳合格参考系统。合格的系统具有复制代码并且没有声明的测试数据泄漏；排除具有已知非许可许可证或成员依赖性的微调条目和系统。排名值直接取自已发布的总体排行榜快照；过滤更改显示的系统，而不是其排名值。*

## 将方法扩展到其他预测者

默认配方使用四个 Granite 模型，但常见的“Forecaster”接口也接受兼容的外部模型。您可以更改成员组合或聚合方法并保持相同的下游预测格式，而无需合并或重新训练成员检查点。这使得您可以更轻松地将整体集成到现有的预测堆栈中，并根据您的需求的变化添加适合您领域的预测器。

该存储库还包括添加 IBM 研究检查点的扩展配方。这些带有单独的许可条款，包括非商业和研究使用限制，因此在使用它们之前请检查每个会员的模型卡。

对于任何新组合，请检查预测兼容性、准确性、校准、延迟和许可。

## 评估适合您的应用的配方

GIFT-Eval 是一个广泛的基准，但总收益并不意味着每个系列都受益，平均排名也无法建立校准。了解配方在您的应用程序中的行为方式的方法是对代表性数据进行回溯测试：

- **匹配您的用例**。使用历史预测窗口来反映每个预测源的可用数据、您需要的时间范围以及您期望提供的系列。
- **同类比较**。在同一窗口上运行概率集成、IQR 集成和强大的单个成员（例如 PatchTST-FM-r2）。
- **超越点错误**。与 MASE 一起评估分位数损失，并对照其名义 80% 检查 0.1 至 0.9 区间的经验覆盖范围。
- **衡量成本**。记录运行时间和内存使用情况，以判断组合四个模型的好处是否适合您的工作负载。

请记住两个限制。当前的配方独立预测多变量通道，不使用跨通道信息，并且加载四个成员检查点，这增加了相对于单个成员的推理时间和内存。成员上下文限制、范围、预处理和缺失值处理也不同，并且两种聚合方法都不能保证分布变化下的校准或鲁棒性，因此在部署后继续监视预测。

## 在你的数据上尝试一下

推荐的起点是默认的四模型配方：

- [Hugging Face 上的 Granite Timeseries Ensemble](https://huggingface.co/ibm-granite/granite-timeseries-ensemble-r1)
- [入门笔记本](https://github.com/ibm-granite/granite-tsfm/blob/main/notebooks/hfdemo/probabilistic_ensemble_getting_started.ipynb)
- [Granite TSFM 存储库](https://github.com/ibm-granite/granite-tsfm)
- [GIFT-Eval 基准](https://huggingface.co/spaces/Salesforce/GIFT-Eval)

加载默认配方，一次调用即可从所有四种 Granite 架构中获取中值和分位数预测，并根据您的需求的变化调整配方。

## 参考文献

- [ECMWF：集合天气预报](https://www.ecmwf.int/en/about/media-centre/focus/2017/fact-sheet-ensemble-weather-forecasting)
- [NOAA：北美多模型集合](https://www.cpc.ncep.noaa.gov/products/NMME/NMME_description.html)
- [FlowState：采样率等变时间序列预测](https://arxiv.org/abs/2508.05287)
- [微型时间混合器 (TTM)：用于增强多元时间序列零/少样本预测的快速预训练模型](https://arxiv.org/abs/2401.03955)
- [重温通用 Transformer：解构时间序列基础模型的强大基线](https://arxiv.org/html/2602.06909v1)
- [预测组合：超过 50 年的回顾](https://arxiv.org/abs/2205.04216)
- [Smith 和 Wallis (2009)，预测组合难题的简单解释](https://doi.org/10.1111/j.1468-0084.2008.00541.x)

## 本文提到的型号 5

## 本文提到的空间1

该作者的更多内容

## ALTK-Evolve：学习记忆如何在没有前沿模型的情况下在客户服务任务的 τ² 基准排行榜上名列前茅

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)

25

2026 年 10 月 20 日

## 您的代理完成了任务。它会再次这样做吗？

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)

122

2026 年 9 月 15 日

### 社区

通过拖入文本输入、粘贴或单击此处来上传图像、音频和视频。

点击或粘贴此处上传图像

· [注册](https://huggingface.co/join?next=%2Fblog%2Fibm-research%2Fgranite-timeseries-ensemble-r1) 或 [登录](https://huggingface.co/login?next=%2Fblog%2Fibm-research%2Fgranite-timeseries-ensemble-r1) 发表评论

14

- [![](https://huggingface.co/avatars/8ff9f76420b50f8d733495fcf9bd0ea9.svg)](https://huggingface.co/Fearghal)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/WSgVWqeGen77Vh5GzTL-O.png)](https://huggingface.co/Jake893)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/kyVdmjyfIsLZqFKhaIRF9.png)](https://huggingface.co/okoyelisbon)
- [![](https://huggingface.co/avatars/63644064768d8ba22487d7b5ffeab88d.svg)](https://huggingface.co/ElPanaBru)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/66d6ee839fcb6b494fcc2cbc/AFMksMD6oOy4ec52PUdnL.png)](https://huggingface.co/Bangla84PL)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6747d1af433d60be7006cf02/YrCokyziqIX41i1NhW6vN.png)](https://huggingface.co/Babysworld)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/wLxC26FpMurJTtMGlo2xM.png)](https://huggingface.co/wasifff)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/yu32gPCVLqnpeQd_MMZ74.png)](https://huggingface.co/darrowoflykos)
- [![](https://huggingface.co/avatars/c9d15c05751f0841bc0c431da3262d50.svg)](https://huggingface.co/vaculin)
- [![](https://huggingface.co/avatars/ed8ccd6d4fbc0e68ce03930eae039c4b.svg)](https://huggingface.co/pankajdayama)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/c_JwpKUXjG0LeKGknmQDk.png)](https://huggingface.co/heatmynuts)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/XM-JnSrJZF_tHU4WbhI-D.png)](https://huggingface.co/zensaintlaurent)

## 本文提到的型号 5

## 本文提到的空间1
