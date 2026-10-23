---
vendor: huggingface
title: Ensemble forecasting with IBM Granite time-series models
original_title: Ensemble forecasting with IBM Granite time-series models
url: https://huggingface.co/blog/ibm-research/granite-timeseries-ensemble-r1
date: 2026-10-22
lang: en
captured: 2026-10-23
extractor: readability-v1
status: ok
body_sha: 8af2051b494a
---

[ Back to Articles](https://huggingface.co/blog)

# Ensemble forecasting with IBM Granite time-series models

Enterprise  Article

Published October 22, 2026


14

- [![](https://huggingface.co/avatars/8ff9f76420b50f8d733495fcf9bd0ea9.svg)](https://huggingface.co/Fearghal)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/WSgVWqeGen77Vh5GzTL-O.png)](https://huggingface.co/Jake893)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/kyVdmjyfIsLZqFKhaIRF9.png)](https://huggingface.co/okoyelisbon)
- [![](https://huggingface.co/avatars/63644064768d8ba22487d7b5ffeab88d.svg)](https://huggingface.co/ElPanaBru)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/66d6ee839fcb6b494fcc2cbc/AFMksMD6oOy4ec52PUdnL.png)](https://huggingface.co/Bangla84PL)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6747d1af433d60be7006cf02/YrCokyziqIX41i1NhW6vN.png)](https://huggingface.co/Babysworld)

[![Fearghal O'Donncha's avatar](https://huggingface.co/avatars/8ff9f76420b50f8d733495fcf9bd0ea9.svg)](https://huggingface.co/Fearghal)

Fearghal O'Donncha

Fearghal

[![IBM Research's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Chandramouli Kamanchi's avatar](https://huggingface.co/avatars/317e008622f276f00309f81af04b3d3b.svg)](https://huggingface.co/rry003)

Chandramouli Kamanchi

rry003

[![IBM Research's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Guruprasad's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/64ca639d7a4f23635701313e/ZaCrxHOn4feQ39vtBAID2.jpeg)](https://huggingface.co/Ranjini)

Guruprasad

Ranjini

[![IBM Research's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Wesley M. Gifford's avatar](https://huggingface.co/avatars/8833ff37c5ccc477f1593cd8ad5a1208.svg)](https://huggingface.co/wmgifford)

Wesley M. Gifford

wmgifford

[![IBM Research's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Natalia Martinez Gil's avatar](https://huggingface.co/avatars/9041e569f6eb98b79ec3c9e7bcfd302c.svg)](https://huggingface.co/natalialmg91)

Natalia Martinez Gil

natalialmg91

[![IBM Research's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Bradley Eck's avatar](https://huggingface.co/avatars/3ee5aa141090176f0c981322072fce25.svg)](https://huggingface.co/bradleyjeck)

Bradley Eck

bradleyjeck

[![IBM Research's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Pankaj Dayama's avatar](https://huggingface.co/avatars/ed8ccd6d4fbc0e68ce03930eae039c4b.svg)](https://huggingface.co/pankajdayama)

Pankaj Dayama

pankajdayama

[![IBM Research's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Roman Vaculin's avatar](https://huggingface.co/avatars/c9d15c05751f0841bc0c431da3262d50.svg)](https://huggingface.co/vaculin)

Roman Vaculin

vaculin

[![IBM Research's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

[![Ayhan Sebin's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/64e8143f6de557454220921e/aNouKBrKm1dnN9pI1JXlp.jpeg)](https://huggingface.co/ayhansebin)

Ayhan Sebin

ayhansebin

[![IBM Research's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)](https://huggingface.co/ibm-research) [ibm-research](https://huggingface.co/ibm-research)

*Four open Granite models, one extensible forecasting interface, and less guesswork about which model to use.*

Pre-trained time-series models can forecast without training on your dataset, but you still have to choose one. A model that handles smooth industrial signals well may struggle with noisy retail demand or a long seasonal horizon, and the best choice depends on the series and the task.

Granite Timeseries Ensemble reduces that choice to a sensible default. One recipe combines four complementary Granite architectures and returns median and quantile forecasts, with no retraining and no fitted ensemble weights. Start with the Probabilistic Ensemble (uniform probability pooling), compare the adaptive Inter Quartile Range (IQR) Ensemble, and extend the same interface with compatible forecasters. The ensemble recipe and its default Granite members are permissively licensed.

The idea will be familiar from weather forecasting. [Ensemble forecasts](https://www.ecmwf.int/en/about/media-centre/focus/2017/fact-sheet-ensemble-weather-forecasting) explore a range of possible outcomes, and systems such as the [North American Multi-Model Ensemble](https://www.cpc.ncep.noaa.gov/products/NMME/NMME_description.html) combine different models for seasonal prediction. Time-series forecasting benefits in a similar way: complementary models offer different views of what comes next, and an ensemble merges those views into one forecast.

## Try Granite Timeseries Ensemble

Install Granite TSFM and load the recommended four-model recipe directly from Hugging Face:

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

The recipe stores the ensemble configuration rather than merged model weights. It downloads the four member checkpoints at runtime, so allow extra time for the first run. For the full configuration, member checkpoints, evaluation details, and limitations, see the [model card](https://huggingface.co/ibm-granite/granite-timeseries-ensemble-r1).

`result.prediction_outputs` contains the point forecast, while `result.quantile_outputs` contains the quantile predictions which by default range from 0.1 to 0.9. Applications can use the point value as a central prediction and selected quantiles to express forecast ranges. For example, the 0.1 and 0.9 quantiles define a central forecast interval with nominal 80% coverage.

## The ensemble members

The default recipe combines four pre-trained Granite models with different architectures:

| Model | Architecture |
| --- | --- |
| [Granite PatchTST-FM-r1](https://huggingface.co/ibm-granite/granite-timeseries-patchtst-fm-r1) | Patched Transformer |
| [Granite PatchTST-FM-r2](https://huggingface.co/ibm-granite/granite-timeseries-patchtst-fm-r2) | Patched Conformer |
| [Granite FlowState-r1.1](https://huggingface.co/ibm-granite/granite-timeseries-flowstate-r1) | State-space model |
| [Granite TTM-r3](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r3) | Tiny Time Mixers (MLP mixer) |

For background, see the [PatchTST-FM-r1 paper](https://arxiv.org/abs/2602.06909), [PatchTST-FM-r2 architecture overview](https://huggingface.co/blog/ibm-research/ibm-releases-sota-granite-time-series), [FlowState paper](https://arxiv.org/abs/2508.05287), and [Tiny Time Mixers paper](https://arxiv.org/abs/2401.03955).

These architectures capture trends, seasonality, and local variation in different ways, so their errors need not coincide. A [50-year review of forecast combinations](https://arxiv.org/abs/2205.04216) describes how combining forecasts can reduce the risk of picking the wrong single model, while stressing that member quality and diversity still matter.

[![Four Granite forecasting models feed a common quantile interface and one of two aggregation methods.](https://huggingface.co/buckets/rry003/blogcomponents/resolve/ensemble_overview.svg?download=true)](https://huggingface.co/buckets/rry003/blogcomponents/resolve/ensemble_overview.svg?download=true)

## Two ways to combine the forecasts

Each member returns quantile forecasts. The two main recipes use different rules to turn those forecasts into one predictive distribution and its median.

### Probabilistic Ensemble: the recommended default

The Probabilistic Ensemble (uniform probability pooling) gives each member equal influence, pools their quantile forecasts in probability space, and extracts the requested quantiles from the combined values. Because the weights are fixed, there is no fitting step and no weighting hyperparameters to tune for a new series.

The [forecast combination puzzle](https://onlinelibrary.wiley.com/doi/10.1111/j.1468-0084.2008.00541.x) offers useful motivation: in point forecasting, simple equal-weight combinations have often held up well against methods with estimated weights. This recipe applies the same equal-influence idea to probabilistic forecasts. It is the default loaded in the example above.

### IQR Ensemble: an adaptive alternative

The IQR Ensemble weights members according to their forecast spread, giving narrower intervals greater influence. It approximates each member’s interquartile range from the closest available quantiles around the 25th and 75th percentiles. Weights vary by sample, target, and horizon step, and like the Probabilistic Ensemble, nothing is fitted from historical forecast errors. Isotonic regression keeps the combined quantiles from crossing.

A narrower interval does not necessarily mean a more accurate or better-calibrated forecast, and IQR weighting can favor an overconfident member. If you want to experiment, the recipe exposes a temperature setting (higher values move the weights toward uniform) and an optional cap on any single member's weight.

Load the evaluated IQR recipe by changing only the subfolder:

```
ensemble = QuantileEnsembleForecaster.from_pretrained(
    "ibm-granite/granite-timeseries-ensemble-r1",
    subfolder="recipes/granite-iqr",
)
```

## Which method should I use?

| Your goal | Start with | Why |
| --- | --- | --- |
| A simple default | Probabilistic Ensemble | Equal influence, no fitted weights |
| Adaptive weighting based on forecast spread | IQR Ensemble | Influence varies with each member's predicted spread |

Start with the Probabilistic Ensemble. If forecast spread looks informative for your application, compare the IQR Ensemble against it on representative data, since accuracy and calibration depend on the series and the horizon.

## Does the ensemble improve on its members?

We evaluated both recipes on 97 GIFT-Eval dataset configurations. The models forecast without fine-tuning, and test targets were not used to select or fit the aggregation method. Here we compare the official ensemble submission results with the four constituent models, using published leaderboard scores and ranks captured on 20 October 2026.

GIFT-Eval reports *MASE* for point forecasts and *CRPS/MWQL* (the benchmark's `mean_weighted_sum_quantile_loss` metric) for probabilistic forecasts. Scores are normalized to Seasonal Naive and geometrically averaged across configurations. Lower is better.

| Forecast | MASE ↓ | MASE Rank ↓ | CRPS / MWQL ↓ | CRPS Rank ↓ |
| --- | --- | --- | --- | --- |
| Granite Ensemble R1 — Prob | **0.683**★ | **47.175**★ | 0.471 | 50.948 |
| Granite Ensemble R1 — IQR | 0.684 | 48.773 | 0.471 | **47.619**★ |
| Granite PatchTST-FM-r2 | 0.685 | 51.371 | **0.467**★ | 48.918 |
| Granite FlowState-r1.1 | 0.701 | 66.474 | 0.490 | 69.485 |
| Granite PatchTST-FM-r1 | 0.717 | 74.794 | 0.488 | 68.134 |
| Granite TTM-r3 | 0.724 | 83.062 | 0.520 | 88.959 |

★ Best value among the forecasts shown. Lower is better.

Rank columns average per-configuration ranks against the full GIFT-Eval reference leaderboard, not just these six forecasts, so rank values can shift as entries are added to the leaderboard.

Both ensembles outperform all four individual members on aggregate MASE and average MASE Rank. The Probabilistic Ensemble achieves the lowest MASE among these six forecasts: 0.683 compared with 0.685 for PatchTST-FM-r2. Lower average MASE Rank indicates stronger relative point-forecast performance across GIFT-Eval’s diverse dataset configurations. Together, these results support the ensemble as a practical starting point, without requiring developers to select the strongest individual architecture in advance. The MASE margin over the best single member is small, so the main benefit is robustness: you get comparable or better aggregate accuracy without knowing in advance which architecture will suit your data.

PatchTST-FM-r2 retains the lowest aggregate CRPS/MWQL score. The IQR Ensemble achieves the lowest average CRPS Rank among these six forecasts, while the Probabilistic Ensemble ranks behind PatchTST-FM-r2 on that measure. Aggregate error and average rank therefore favor different choices.

In the 20 October 2026 comparison, the ensemble approach ranks 3rd among eligible systems on MASE Rank and CRPS Rank. The figure below shows both recipes alongside the ten best eligible reference systems per metric. Some systems, including entries excluded as fine-tuned or non-permissively licensed, score better than either recipe, so the value of the ensemble is not that it tops the leaderboard. It is that a single default delivers strong, consistent results across many series without requiring you to choose a member.

[![GIFT-Eval average rank comparison for both Granite ensembles and eligible reference systems. Lower is better.](https://huggingface.co/buckets/rry003/blogcomponents/resolve/gift_eval_ranks_granite.png?download=true)](https://huggingface.co/buckets/rry003/blogcomponents/resolve/gift_eval_ranks_granite.png?download=true)

*Figure: GIFT-Eval average-rank standings on 20 October 2026, showing both Granite ensembles alongside the ten best eligible reference systems per metric. Eligible systems have replication code and no declared test-data leakage; fine-tuned entries and systems with known non-permissive licenses or member dependencies are excluded. Rank values are taken directly from the published overall leaderboard snapshot; filtering changes which systems are displayed, not their rank values.*

## Extend the recipe to other forecasters

The default recipe uses four Granite models, but the common `Forecaster` interface also accepts compatible external models. You can change the member mix or the aggregation method and keep the same downstream forecast format, with no merging or retraining of member checkpoints. That makes it easier to fit the ensemble into an existing forecasting stack, and to add forecasters suited to your domain as your needs evolve.

The repository also includes expanded recipes that add IBM Research checkpoints. These carry separate license terms, including non-commercial and research-use restrictions, so review each member's model card before using them.

For any new combination, check forecast compatibility, accuracy, calibration, latency, and licensing.

## Evaluate the recipe for your application

GIFT-Eval is a broad benchmark, but aggregate gains don’t mean every series benefits, and average ranks don’t establish calibration. The way to find out how the recipes behave for your application is to backtest them on representative data:

- **Match your use case**. Use historical forecast windows that reflect the data available at each forecast origin, the horizon you need, and the series you expect to serve.
- **Compare like with like**. Run the Probabilistic Ensemble, the IQR Ensemble, and a strong individual member (such as PatchTST-FM-r2) on the same windows.
- **Look beyond point error**. Assess quantile loss alongside MASE, and check the empirical coverage of the 0.1 to 0.9 interval against its nominal 80%.
- **Measure the cost**. Record runtime and memory use to judge whether the benefit of combining four models justifies it for your workload.

Keep two limitations in mind. The current recipe forecasts multivariate channels independently, without using cross-channel information, and it loads four member checkpoints, which increases inference time and memory relative to a single member. Member context limits, horizons, preprocessing, and missing-value handling also differ, and neither aggregation method guarantees calibration or robustness under distribution shift, so keep monitoring forecasts after deployment.

## Try it on your data

The recommended starting point is the default four-model recipe:

- [Granite Timeseries Ensemble on Hugging Face](https://huggingface.co/ibm-granite/granite-timeseries-ensemble-r1)
- [Getting-started notebook](https://github.com/ibm-granite/granite-tsfm/blob/main/notebooks/hfdemo/probabilistic_ensemble_getting_started.ipynb)
- [Granite TSFM repository](https://github.com/ibm-granite/granite-tsfm)
- [GIFT-Eval benchmark](https://huggingface.co/spaces/Salesforce/GIFT-Eval)

Load the default recipe to get median and quantile forecasts from all four Granite architectures in one call, and adapt the recipe as your needs evolve.

## References

- [ECMWF: Ensemble weather forecasting](https://www.ecmwf.int/en/about/media-centre/focus/2017/fact-sheet-ensemble-weather-forecasting)
- [NOAA: North American Multi-Model Ensemble](https://www.cpc.ncep.noaa.gov/products/NMME/NMME_description.html)
- [FlowState: Sampling-Rate-Equivariant Time-Series Forecasting](https://arxiv.org/abs/2508.05287)
- [Tiny Time Mixers (TTMs): Fast Pre-trained Models for Enhanced Zero/Few-Shot Forecasting of Multivariate Time Series](https://arxiv.org/abs/2401.03955)
- [Revisiting the Generic Transformer: Deconstructing a Strong Baseline for Time Series Foundation Models](https://arxiv.org/html/2602.06909v1)
- [Forecast combinations: an over 50-year review](https://arxiv.org/abs/2205.04216)
- [Smith and Wallis (2009), A Simple Explanation of the Forecast Combination Puzzle](https://doi.org/10.1111/j.1468-0084.2008.00541.x)

## Models mentioned in this article 5

## Spaces mentioned in this article 1

More from this author

## ALTK-Evolve: How learned memory tops the τ²-bench leaderboard on customer service tasks without a frontier model

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)

25

October 20, 2026

## Your Agent Aced the Task. Will It Do It Again?

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/637bfdf60dc13843b468ac20/npxapKcW-cXX3J2JBl2vY.png)

122

September 15, 2026

### Community

Upload images, audio, and videos by dragging in the text input, pasting, or clicking here.

Tap or paste here to upload images

· [Sign up](https://huggingface.co/join?next=%2Fblog%2Fibm-research%2Fgranite-timeseries-ensemble-r1) or [log in](https://huggingface.co/login?next=%2Fblog%2Fibm-research%2Fgranite-timeseries-ensemble-r1) to comment


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

## Models mentioned in this article 5

## Spaces mentioned in this article 1
