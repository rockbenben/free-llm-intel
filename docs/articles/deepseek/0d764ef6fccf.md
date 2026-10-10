---
vendor: deepseek
title: DeepSeek V4.1 Flash：更强、更快、更普惠
original_title: 
url: https://api-docs.deepseek.com/zh-cn/news/news260910
date: 2026-09-10
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: native
status: translated
body_sha: d8569a8dc0a1
---

# DeepSeek V4.1 Flash：更强、更快、更普惠

今天，我们正式发布 DeepSeek V4.1 Flash 模型。这是我们全新模型结构系列中的最小尺寸的模型，具备原生多模态视觉理解能力。新模型结构的设计初衷是：能力上限更高、推理速度更快、吞吐更大、可扩展到更大参数模型。

## 非对称模型结构，小成本大智能

DeepSeek V4.1 Flash 为 552B 参数的 MoE 模型，采用了全新的 Causal-Encoder-Decoder 结构，输入和输出不对称，输入激活只有 8B，输出激活 16B，成本显著低于已知的同尺寸模型。同时，V4.1 Flash 还采用了新的预训练方式、经过了更大规模的强化学习后训练，在基准测试中，成功超越了包括 DeepSeek V4 Pro 在内的一众旗舰模型的智能水平。

DeepSeek-V4.1-Flash 与主流前沿模型在 Agentic Benchmark 上的性能对比

## 更少缓存，更省成本

新一代模型大幅减少了 KV Cache 缓存的大小，与上一代模型相比，对 HBM 的需求减少到 1/4，对 SSD 的需求减少到 1/8。在 Agent 使用场景中，缓存命中的费用往往占比较高，对 KV Cache 的压缩大幅降低了 Agent 类任务的使用成本。

如图展示了 DeepSeek 在减少上下文存储方面的持续进展。相对于初代模型，KV Cache 已经缩小了 437 倍。

## API 支持

DeepSeek V4.1 Flash 已同步上线 DeepSeek API，原生支持多模态，将模型名称更改为 `deepseek-flash` 即可调用最新的 V4.1 Flash 模型。旧版本模型 V4 Flash 与 V4 Flash Vision Exp 现已下线，出于兼容考虑，模型名 `deepseek-v4-flash`、`deepseek-v4-flash-vision-exp` 将被暂时路由到 V4.1 Flash。

同时，经多方测试，V4.1 Flash 在性能、费用、速度、总用时等各项指标上已全面超越 V4 Pro，因此我们计划有序下线 V4 Pro 模型。北京时间 2026 年 9 月 14 日 12:00 之后，至未来 V4.1 Pro 上线之前，用户访问 `deepseek-v4-pro` 的请求将全部路由到 V4.1 Flash，并按 V4.1 Flash 单价计费。

**腾讯（WorkBuddy、CodeBuddy）和 OpenCode 作为官方合作伙伴，现已全量接入 DeepSeek V4.1 Flash，欢迎使用！**

## API 定价调整

得益于模型架构的创新，DeepSeek V4.1 Flash 能够以更低的成本服务更多的用户，因此我们相应下调了 V4.1 Flash 的定价。同时，为了更合理地调配资源，我们仍然采用峰谷定价，闲时价格为高峰时段价格的一半，鼓励用户根据实际使用情况调整任务时间。新价格于 2026 年 9 月 10 日 12:00 开始生效。

## 模型开源

我们将会全力支持开源社区进行新模型的推理适配，并尝试通过各种方式扩大部署的范围。如果您有大规模部署的需求且具备相应的资源（2k 卡 GPU、有存储集群），欢迎与我们联系。

模型开源链接：

[https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash)

论文链接：

[https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/blob/main/DeepSeek_V41_Tech_Report.pdf](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/blob/main/DeepSeek_V41_Tech_Report.pdf)

- [非对称模型结构，小成本大智能](https://api-docs.deepseek.com/zh-cn/news/news260910/#非对称模型结构小成本大智能)
- [更少缓存，更省成本](https://api-docs.deepseek.com/zh-cn/news/news260910/#更少缓存更省成本)
- [API 支持](https://api-docs.deepseek.com/zh-cn/news/news260910/#api-支持)
- [API 定价调整](https://api-docs.deepseek.com/zh-cn/news/news260910/#api-定价调整)
- [模型开源](https://api-docs.deepseek.com/zh-cn/news/news260910/#模型开源)
