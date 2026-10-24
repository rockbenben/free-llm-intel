---
vendor: huggingface
title: 使用 IBM Granite 时间序列模型进行集合预测
original_title: Ensemble forecasting with IBM Granite time-series models
url: https://huggingface.co/blog/ibm-research/granite-timeseries-ensemble-r1
date: 2026-10-22
lang: zh
captured: 2026-10-24
extractor: readability-v1
translator: agent
status: translated
body_sha: 06a33f258d18
---

[ 返回文章](https://huggingface.co/blog)

# 使用 IBM Granite 时间序列模型进行集合预测

企业  文章

发布于 2026 年 10 月 22 日


14

- [![](https://huggingface.co/avatars/8ff9f76420b50f8d733495fcf9bd0ea9.svg)](https://huggingface.co/Fearghal)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/WSgVWqeGen77Vh5GzTL-O.png)](https://huggingface.co/Jake893)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/kyVdmjyfIsLZqFKhaIRF9.png)](https://huggingface.co/okoyelisbon)
- [![](https://huggingface.co/avatars/63644064768d8ba22487d7b5ffeab88d.svg)](https://huggingface.co/ElPanaBru)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/66d6ee839fcb6b494fcc2cbc/AFMksMD6oOy4ec52PUdnL.png)](https://huggingface.co/Bangla84PL)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6747d1af433d60be7006cf02/YrCokyziqIX41i1NhW6vN.png)](https://huggingface.co/Babysworld)

[![Fearghal O'Donncha 的头像](https://huggingface.co/avatars/8ff9f76420b50f8d733495fcf9bd0ea9.svg)](https://huggingface.co/Fearghal)

Fearghal O'Donncha

Fearghal

[![IBM Research 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Chandramouli Kamanchi 的头像](https://huggingface.co/avatars/317e008622f276f00309f81af04b3d3b.svg)](https://huggingface.co/rry003)

Chandramouli Kamanchi

rry003

[![IBM Research 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Guruprasad 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/64ca639d7a4f23635701313e/ZaCrxHOn4feQ39vtBAID2.jpeg)](https://huggingface.co/Ranjini)

Guruprasad

Ranjini

[![IBM Research 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Wesley M. Gifford 的头像](https://huggingface.co/avatars/8833ff37c5ccc477f1593cd8ad5a1208.svg)](https://huggingface.co/wmgifford)

Wesley M. Gifford

wmgifford

[![IBM Research 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Natalia Martinez Gil 的头像](https://huggingface.co/avatars/9041e569f6eb98b79ec3c9e7bcfd302c.svg)](https://huggingface.co/natalialmg91)

Natalia Martinez Gil

natalialmg91

[![IBM Research 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Bradley Eck 的头像](https://huggingface.co/avatars/3ee5aa141090176f0c981322072fce25.svg)](https://huggingface.co/bradleyjeck)

Bradley Eck

bradleyjeck

[![IBM Research 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Pankaj Dayama 的头像](https://huggingface.co/avatars/ed8ccd6d4fbc0e68ce03930eae039c4b.svg)](https://huggingface.co/pankajdayama)

Pankaj Dayama

pankajdayama

[![IBM Research 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Roman Vaculin 的头像](https://huggingface.co/avatars/c9d15c05751f0841bc0c431da3262d50.svg)](https://huggingface.co/vaculin)

Roman Vaculin

vaculin

[![IBM Research 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Ayhan Sebin 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/64e8143f6de557454220921e/aNouKBrKm1dnN9pI1JXlp.jpeg)](https://huggingface.co/ayhansebin)

Ayhan Sebin

ayhansebin

[![IBM Research 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

*四个开放的 Granite 模型、一个可扩展的预测接口，以及更少的“到底该用哪个模型”的猜测。*

预训练的时间序列模型无需在你的数据集上训练就能做预测，但你仍然得挑一个。擅长处理平滑工业信号的模型，可能难以应付噪声很大的零售需求，或者很长的季节性视野，而最佳选择取决于序列本身和任务。

Granite Timeseries Ensemble 把这种选择简化为一个合理的默认值。一套配方组合了四个互补的 Granite 架构，返回中位数与分位数预测，无需重新训练，也没有拟合出来的集合权重。可以先从 Probabilistic Ensemble（均匀概率池化）起步，再对比自适应的 Inter Quartile Range（IQR）Ensemble，并用兼容的预测器扩展同一套接口。集合配方及其默认的 Granite 成员都采用宽松许可（permissive license）。

这个思路在天气预报里并不陌生。[集合预报](https://www.ecmwf.int/en/about/media-centre/focus/2017/fact-sheet-ensemble-weather-forecasting) 会探索一系列可能的结果，而 [North American Multi-Model Ensemble](https://www.cpc.ncep.noaa.gov/products/NMME/NMME_description.html) 这类系统则把不同的模型组合起来做季节预测。时间序列预测以类似的方式受益：互补的模型提供了关于“接下来会发生什么”的不同视角，而集合把这些视角合并成一个预测。

## 试用 Granite Timeseries Ensemble

安装 Granite TSFM，并直接从 Hugging Face 加载推荐的四模型配方：

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

该配方保存的是集合配置，而不是合并后的模型权重。它会在运行时下载四个成员的 checkpoint，因此首次运行要预留额外时间。完整的配置、成员 checkpoint、评估细节与局限性，见[模型卡](https://huggingface.co/ibm-granite/granite-timeseries-ensemble-r1)。

`result.prediction_outputs` 包含点预测，而 `result.quantile_outputs` 包含分位数预测，默认范围是 0.1 到 0.9。应用可以把点值当作中心预测，并选用若干分位数来表达预测区间。例如，0.1 与 0.9 分位数定义了一个名义覆盖率为 80% 的中心预测区间。

## 集合成员

默认配方组合了四个架构不同的预训练 Granite 模型：

| 模型 | 架构 |
| --- | --- |
| [Granite PatchTST-FM-r1](https://huggingface.co/ibm-granite/granite-timeseries-patchtst-fm-r1) | 分块 Transformer |
| [Granite PatchTST-FM-r2](https://huggingface.co/ibm-granite/granite-timeseries-patchtst-fm-r2) | 分块 Conformer |
| [Granite FlowState-r1.1](https://huggingface.co/ibm-granite/granite-timeseries-flowstate-r1) | 状态空间模型 |
| [Granite TTM-r3](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r3) | Tiny Time Mixers（MLP 混合器） |

背景资料见 [PatchTST-FM-r1 论文](https://arxiv.org/abs/2602.06909)、[PatchTST-FM-r2 架构概览](https://huggingface.co/blog/ibm-research/ibm-releases-sota-granite-time-series)、[FlowState 论文](https://arxiv.org/abs/2508.05287) 以及 [Tiny Time Mixers 论文](https://arxiv.org/abs/2401.03955)。

这些架构以不同方式刻画趋势、季节性与局部变化，因此它们的误差不一定同时出现。[一份长达 50 年的预测组合综述](https://arxiv.org/abs/2205.04216) 描述了组合预测如何降低选错单一模型的风险，同时强调成员的质量与多样性依然重要。

[![四个 Granite 预测模型接入统一的 quantile 接口，再由两种聚合方法之一合成预测。](https://huggingface.co/buckets/rry003/blogcomponents/resolve/ensemble_overview.svg?download=true)](https://huggingface.co/buckets/rry003/blogcomponents/resolve/ensemble_overview.svg?download=true)

## 组合预测的两种方式

每个成员都返回分位数预测。两套主要配方使用不同的规则，把这些预测合成一个预测分布及其中位数。

### Probabilistic Ensemble：推荐的默认选择

Probabilistic Ensemble（均匀概率池化）给每个成员相等的影响力，在概率空间中对它们的预测做池化，再从合并后的取值中提取所需的分位数。由于权重固定，新序列既不需要拟合步骤，也没有需要调优的加权超参数。

[预测组合之谜](https://onlinelibrary.wiley.com/doi/10.1111/j.1468-0084.2008.00541.x) 提供了有用的动机：在点预测中，简单的等权组合常常能与用估计权重的方法相抗衡。这套配方把同样的等影响力思路用于概率预测。它也是上面示例中默认加载的方案。

### IQR Ensemble：一种自适应替代方案

IQR Ensemble 按各成员的预测离散程度加权，区间越窄的成员影响力越大。它用 25 分位与 75 分位附近最接近的可用分位数来近似每个成员的四分位距。权重随样本、目标和预测步长而变化，并且和 Probabilistic Ensemble 一样，不从历史预测误差中拟合任何东西。等渗回归（isotonic regression）确保合并后的分位数不会交叉。

区间更窄并不必然意味着更准确或校准更好的预测，而且 IQR 加权可能偏爱过度自信的成员。如果想做实验，配方暴露了一个温度设置（取值越高，权重越趋向均匀）以及一个可选的单成员权重上限。

只改子文件夹，即可加载经过评估的 IQR 配方：

```
ensemble = QuantileEnsembleForecaster.from_pretrained(
    "ibm-granite/granite-timeseries-ensemble-r1",
    subfolder="recipes/granite-iqr",
)
```

## 我该用哪种方法？

| 你的目标 | 从何处入手 | 原因 |
| --- | --- | --- |
| 一个简单的默认方案 | Probabilistic Ensemble | 影响力均等，没有拟合权重 |
| 基于预测离散度的自适应加权 | IQR Ensemble | 影响力随每个成员预测的离散度变化 |

先从 Probabilistic Ensemble 开始。如果预测离散度对你的应用有信息量，就在有代表性的数据上把 IQR Ensemble 与它对比，因为准确性和校准都取决于序列与预测视野。

## 集合相比其成员有提升吗？

我们在 97 个 GIFT-Eval 数据集配置上评估了两套配方。模型不做微调直接预测，测试目标也没有用于选择或拟合聚合方法。这里把官方集合提交的结果与四个组成模型作对比，使用的是 2026 年 10 月 20 日抓取的已发布排行榜分数与排名。

GIFT-Eval 对点预测报告 *MASE*，对概率预测报告 *CRPS/MWQL*（即该基准的 `mean_weighted_sum_quantile_loss` 指标）。分数以 Seasonal Naive 为基准归一化，并在各配置间做几何平均。越低越好。

| 预测 | MASE ↓ | MASE 排名 ↓ | CRPS / MWQL ↓ | CRPS 排名 ↓ |
| --- | --- | --- | --- | --- |
| Granite Ensemble R1 — Prob | **0.683**★ | **47.175**★ | 0.471 | 50.948 |
| Granite Ensemble R1 — IQR | 0.684 | 48.773 | 0.471 | **47.619**★ |
| Granite PatchTST-FM-r2 | 0.685 | 51.371 | **0.467**★ | 48.918 |
| Granite FlowState-r1.1 | 0.701 | 66.474 | 0.490 | 69.485 |
| Granite PatchTST-FM-r1 | 0.717 | 74.794 | 0.488 | 68.134 |
| Granite TTM-r3 | 0.724 | 83.062 | 0.520 | 88.959 |

★ 表示表中所列预测里的最佳值。越低越好。

排名列是把每个配置的排名与完整的 GIFT-Eval 参考排行榜比较后取平均，而不只是在这六个预测之间排序，因此随着新条目加入排行榜，排名数值会发生变化。

两个集合在总体 MASE 与平均 MASE 排名上都优于全部四个单独成员。Probabilistic Ensemble 在这六个预测中取得最低的 MASE：0.683，而 PatchTST-FM-r2 为 0.685。更低的平均 MASE 排名意味着在 GIFT-Eval 多样化的数据集配置上相对更强的点预测表现。综合来看，这些结果支持把集合当作一个实用的起点，开发者无需事先挑出最强的单一架构。相对最佳单成员，MASE 的优势很小，所以主要好处是稳健性：在事先并不知道哪种架构更适合你的数据时，也能得到相当或更好的总体准确率。

PatchTST-FM-r2 仍保持最低的总体 CRPS/MWQL 分数。IQR Ensemble 在这六个预测中取得最低的平均 CRPS 排名，而 Probabilistic Ensemble 在该指标上排在 PatchTST-FM-r2 之后。因此，总体误差与平均排名会偏向不同的选择。

在 2026 年 10 月 20 日的对比中，集合方法在合格系统中按 MASE 排名和 CRPS 排名均列第 3。下图展示了这两套配方，以及每个指标下十个最佳合格参考系统。有些系统——包括因微调或非宽松许可被排除的条目——得分优于这两套配方中的任何一个，所以集合的价值不在于登顶排行榜，而在于一个默认设置就能在许多序列上给出强而一致的结果，无需你去挑选某个成员。

[![GIFT-Eval 平均排名对比：两个 Granite 集合与合格参考系统。越低越好。](https://huggingface.co/buckets/rry003/blogcomponents/resolve/gift_eval_ranks_granite.png?download=true)](https://huggingface.co/buckets/rry003/blogcomponents/resolve/gift_eval_ranks_granite.png?download=true)

*图：2026 年 10 月 20 日的 GIFT-Eval 平均排名榜单，展示了两个 Granite 集合以及每个指标下十个最佳合格参考系统。合格系统需具备复现代码且未声明使用测试数据泄漏；微调条目以及已知为非宽松许可或依赖特定成员的系统被排除。排名数值直接取自已发布的总体排行榜快照；筛选只改变显示哪些系统，不改变它们的排名数值。*

## 把配方扩展到其他预测器

默认配方使用四个 Granite 模型，但通用的 `Forecaster` 接口也接受兼容的外部模型。你可以更换成员组合或聚合方法，同时保留下游相同的预测格式，无需合并或重新训练成员 checkpoint。这让你更容易把集合嵌入已有的预测栈，并在需求演进时加入适合你所在领域的预测器。

仓库还包含扩展配方，加入了 IBM Research 的 checkpoint。这些模型带有单独的许可条款，包括非商业和仅限研究用途的限制，使用前请查阅每个成员的模型卡。

对任何新组合，都要检查预测兼容性、准确性、校准、延迟与许可。

## 针对你的应用评估该配方

GIFT-Eval 是一个覆盖很广的基准，但总体提升并不意味着每个序列都受益，平均排名也不能确立校准的好坏。想知道这些配方在你的应用上表现如何，办法是在有代表性的数据上做回测：

- **贴合你的用例**。使用能反映每个预测起点当时可用数据的历史预测窗口、你需要的预测视野，以及你预期要服务的序列。
- **同类对比**。在相同的窗口上运行 Probabilistic Ensemble、IQR Ensemble，以及一个强的单独成员（例如 PatchTST-FM-r2）。
- **不要只看点误差**。除了 MASE，还要评估 quantile loss，并检查 0.1 到 0.9 区间的经验覆盖率是否达到其名义上的 80%。
- **衡量成本**。记录运行时间与内存占用，判断组合四个模型带来的收益对你的工作负载是否值得。

请记住两个局限。当前配方独立预测多变量通道，没有利用跨通道信息；并且它会加载四个成员 checkpoint，相比单个成员增加了推理时间与内存占用。各成员的上下文上限、预测视野、预处理与缺失值处理也不相同，而且两种聚合方法都不保证在分布偏移下仍然校准或稳健，所以部署后要继续监控预测。

## 在你的数据上试试

推荐的起点是默认的四模型配方：

- [Hugging Face 上的 Granite Timeseries Ensemble](https://huggingface.co/ibm-granite/granite-timeseries-ensemble-r1)
- [入门 notebook](https://github.com/ibm-granite/granite-tsfm/blob/main/notebooks/hfdemo/probabilistic_ensemble_getting_started.ipynb)
- [Granite TSFM 仓库](https://github.com/ibm-granite/granite-tsfm)
- [GIFT-Eval 基准](https://huggingface.co/spaces/Salesforce/GIFT-Eval)

加载默认配方，一次调用即可得到四个 Granite 架构的中位数与分位数预测；随着需求变化，再调整配方。

## 参考文献

- [ECMWF：集合天气预报](https://www.ecmwf.int/en/about/media-centre/focus/2017/fact-sheet-ensemble-weather-forecasting)
- [NOAA：North American Multi-Model Ensemble](https://www.cpc.ncep.noaa.gov/products/NMME/NMME_description.html)
- [FlowState：采样率等变的时间序列预测](https://arxiv.org/abs/2508.05287)
- [Tiny Time Mixers（TTMs）：用于增强多变量时间序列零样本/少样本预测的快速预训练模型](https://arxiv.org/abs/2401.03955)
- [重新审视通用 Transformer：拆解时间序列基础模型的强基线](https://arxiv.org/html/2602.06909v1)
- [预测组合：一份超过 50 年的综述](https://arxiv.org/abs/2205.04216)
- [Smith 与 Wallis（2009），预测组合之谜的简单解释](https://doi.org/10.1111/j.1468-0084.2008.00541.x)

## 本文提到的模型 5

## 本文提到的 Space 1

更多来自该作者

## ALTK-Evolve：学习到的记忆如何在无需前沿模型的情况下登顶客户服务任务的 τ²-bench 排行榜

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)

25

2026 年 10 月 20 日

## 你的 Agent 圆满完成了任务。它还能再来一次吗？

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)

122

2026 年 9 月 15 日

### 社区

把图片、音频和视频拖进文本输入框，或粘贴、或点击此处即可上传。

点击或粘贴此处上传图片

· [注册](https://huggingface.co/join?next=%2Fblog%2Fibm-research%2Fgranite-timeseries-ensemble-r1) 或 [登录](https://huggingface.co/login?next=%2Fblog%2Fibm-research%2Fgranite-timeseries-ensemble-r1) 后发表评论


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

## 本文提到的模型 5

## 本文提到的 Space 1
