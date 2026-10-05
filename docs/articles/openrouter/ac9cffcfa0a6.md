---
vendor: openrouter
title: GPT 5.6 折扣与杰文斯悖论
original_title: GPT 5.6 Discounts & Jevons Paradox
url: https://openrouter.ai/blog/insights/gpt-5-6-discounts-jevons-paradox
date: 2026-08-25
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

OpenAI 在 7 月 27 日至 8 月 14 日为其新的 Terra 和 Luna 模型提供了大幅折扣。这些折扣对 token 用量、总支出和竞争格局产生了什么影响？

## 要点

- **Token 用量激增：** 折扣窗口期内，Terra 的日 token 用量上涨 5.6 倍，Luna 的日 token 用量飙升 13.8 倍。而保持列表价的 Sol 模型同期仅温和上涨 1.1 倍。
- **份额被重新配置：** OpenAI 折扣抢来的份额大部分来自其他实验室，而非 OpenAI 模型家族内部的自相蚕食。
- **用户留下来了：** 折扣期内尝试过折扣 OpenAI 模型的用户中，近三分之一在折扣结束后仍在继续使用。

## 折扣对 token 用量的影响

![Indexed daily token usage by model group, showing Terra and Luna spiking during the discount window while Sol and other groups stay near their pre-period levels](https://openrouter.ai/blog/images/gpt-5-6-discounts-token-index.png)

GPT 5.6 折扣生效的那一刻，token 量爆发式增长。

把活动期内的 token 用量与前期日均对比，效果一目了然：Terra token 上涨 5.6 倍，Luna 上涨 13.8 倍。未打折的 Sol 模型只微涨 1.11 倍，而其他 OpenAI 模型的 token 用量反而略有下降。OpenAI 家族之外，其他模型只是温和上涨。

## 竞争替代

![Stacked daily token share by model group, with the Terra and Luna band expanding and the pooled competitor band shrinking during the discount window](https://openrouter.ai/blog/images/gpt-5-6-discounts-token-share.png)

从前期到活动期，Terra/Luna 占 OpenRouter 全部 token 的比例从 0.7% 升至 7.8%，增加了 7.1 个百分点。所有竞争对手被归并到浅灰色段，每个颜色堆叠上方的标签是 OpenAI 家族的合计份额（Terra + Luna + Sol + 其他 OpenAI）。

同样的对比中，竞争对手让出了 5.3 个百分点，其他 OpenAI 模型让出了 1.9 个百分点——因此约四分之三的增长来自 OpenAI 之外。就整个 OpenAI 家族而言，token 份额从 7.1% 增长到 12.4%，在折扣期间的个别日子甚至一度越过 15%。

![Daily tokens by model author, with OpenAI volume roughly doubling and holding after the program while Anthropic declines](https://openrouter.ai/blog/images/gpt-5-6-discounts-tokens-by-author.png)

主要模型作者的 token 大多在上涨，但 Anthropic 在这一时间段没有。OpenAI 的 token 量平均接近翻倍，并在折扣活动结束后保持了这一更高水平。

## 用户留存

![Retention of customers who used Terra or Luna during the program, split between those with any post-program usage and those running at or above their program pace](https://openrouter.ai/blog/images/gpt-5-6-discounts-retention.png)

显然折扣在活动期内推高了 token 用量，但折扣结束后这些用户留下了吗？

在活动期有 Terra/Luna 用量的 10 万+ 客户中，约 32% 在随后几天里保留了一些用量，18% 的用量达到或超过活动期水平。需要说明，这是按客户数计，未按 token 加权。当然，活动后时间窗比整个折扣期短得多（目前 6 天 vs 19 天的活动期），随着更多数据进来，结论可能变化。

如果改看每日 Terra/Luna token 量，活动后期间平均是折扣期间的 1.38 倍——这意味着留下的账户远大于活动期的中位用户。

![Daily Sol token volume staying flat through the Terra and Luna program, then jumping when Sol receives its own 50% discount on August 17](https://openrouter.ai/blog/images/gpt-5-6-discounts-sol-daily.png)

Sol 在 Terra/Luna 活动期间的日均为 791 亿 token，前期为 712 亿/天——基本持平，是很好的对照组。

但上图从 8 月 17 日起的阴影区域是 Sol 自己的 50% 折扣。Sol 应声跳涨，重演了 Terra/Luna 的模式。

## 方法与说明

数据细节

- 前期：7 月 8 日至 7 月 26 日 | 活动期：7 月 27 日至 8 月 14 日 | 后期：8 月 15 日至 8 月 20 日
- 7 月 30 日：OpenAI 在 50% 折扣之外又下调了自己的列表价（Luna 80%、Terra 20%）。因此 7 月 30 日起的实际折扣为 Luna 90%、Terra 60%。
- 备注：Terra、Luna 和 Sol 均于 7 月 9 日发布。在 8 月 17 日 Sol 获得自己的 50% 折扣之前，Sol 是有用的对照。

方法论

- 排除项：被封禁、已删除、管理员、已申请数据删除、内部及流失账户均被剔除。
- 8 月 20 日是窗口最后一天，可能不完整。
- Sol 仅在 8 月 16 日之前是有效对照。后期窗口为 6 天。
