---
vendor: deepinfra
title: 9 个最佳开源编程模型（2026 年 11 月）
original_title: 
url: https://deepinfra.com/blog/best-open-source-models-for-coding
date: 2026-11-17
lang: zh
captured: 2026-11-17
extractor: readability-v1
translator: mt
status: translated
body_sha: e273a3818828
---

# 9 个最佳开源编码模型（2026 年 11 月）

DeepInfra 发布于 2026.11.17

![9 个最佳编码开源模型（2026 年 11 月）](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/11/best-open-source-models-for-coding-header.png)

现代人工智能 (AI) 编码工具现在可以分析存储库、修复错误、编辑多个文件、运行测试并执行自主开发循环。这些代理工作流程通过连续的模型调用生成数百万个输入和输出令牌，这使得专有 API 的大规模成本高昂。

开源编码模型提供了一种经济高效的替代方案。您可以在私有基础设施上运行它们、选择服务硬件、固定特定模型版本、调整推理设置并减少对单个 API 提供商的依赖。 [DeepInfra](https://deepinfra.com/) 等托管推理服务还允许您使用这些模型，而无需自行管理 GPU，对于本指南中得分最高的模型，每个代币的价格低于每百万输入代币 0.10 美元。

在本指南中，我们比较了截至 2026 年 11 月的领先开源编码模型。我们根据编码基准、上下文窗口大小、许可条款和 API 成本对它们进行评估，并在最后介绍了自托管选项。分数和价格截至 2026 年 11 月 17 日。

## 如何评估编码模型：重要的基准

观察以下基准来判断模型在您计划自动化的任务上的执行情况。

- [**HumanEval**](https://github.com/openai/ human-eval) **和 [MBPP（主要是基本的 Python 问题）](https://huggingface.co/datasets/Muennighoff/mbpp)** 衡量函数级代码生成。模型收到一个简短的自然语言问题，并且必须生成通过单元测试的 Python 代码。它们提供了对基本编程能力的快速衡量，但它们不测试存储库导航、工具使用或多文件更改，并且当前模型已在很大程度上饱和了它们。
- [**SWE-bench Verified**](https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified) **和 [SWE-bench Pro](https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro)** 评估模型在代理编码工作流程中解决实际 GitHub 问题的效果。该模型必须遍历整个代码库，找到错误的来源，跨多个文件编写补丁，并通过执行测试。
- **DeepSWE** 是今年大多数模型卡报告的长期软件工程基准。由于 DeepSeek、Moonshot、MiniMax、小米、Z.ai 和 Qwen 都发布了 DeepSWE v1.1 分数，因此它是最接近跨供应商的通用标准的东西，但需要注意的是每个供应商都运行自己的工具。
- [**Terminal-Bench**](https://www.tbench.ai/) 比较与 shell 命令、命令行界面 (CLI) 和 DevOps 相关的任务的模型性能。供应商现在报告版本 2.1 和 4.0，结果随着所使用的代理线束发生很大变化，因此仅在同一型号卡内比较分数。
- [**LiveBench**](https://livebench.ai/) 是独立的并定期刷新以限制训练数据污染。 LiveBench 于 2026 年 11 月 6 日升级到 2.0 版本。新版本对长期工作（错误修复、运行数小时的应用程序、研究报告）进行评分，其分数与该日期之前发布的 LiveBench 数据无法比较。

除了排行榜之外，还请检查上下文窗口和许可证。在功能级别完成上看起来不错的模型对于整个存储库重构或私人本地使用来说仍然是一个糟糕的选择。

- **上下文窗口**定义模型可以在单个请求中处理多少代码、文档、终端输出和对话历史记录。更大的上下文窗口有助于存储库分析和长时间运行的代理会话。
- **许可证**决定您是否可以在商业上使用权重、修改权重、重新分发模型或通过托管服务提供模型。 “开源”在这个领域被广泛使用。下面的几种型号在具有商业条件的定制许可证下运输开放重量，我们对每一种都进行了注明。我们的[开放权重模型许可证](https://deepinfra.com/blog/open-weight-model-licenses)指南涵盖了要检查的内容。

## 前 9 个开源编码模型：比较

以下是当前顶级开源编码模型在大小、许可证、上下文窗口以及它们最擅长的方面的比较：

|型号|开发商 |参数（总计/活动）|许可证|上下文窗口 |最适合 |
| --- | --- | --- | --- | --- | --- |
| **DeepSeek V4.1 闪存 (1017)** |深度搜索 |共 763B |麻省理工学院 | 1M |每美元最佳编码得分 |
| **Mistral大 4** |Mistral人工智能 | 1T/49B | Mistral 生态系统开放权重许可证 | 1M |欧洲出身的多面手，编码成绩接近顶尖 |
| **GLM-5.3** | Z.ai |共 753B | GLM-5.3 许可证（定制）| 1M |长期编码和安全工作|
| **Qwen3.8-27B** |阿里巴巴Qwen | 27B密|阿帕奇2.0 | 262K |小型部署和本地使用 |
| **MiniMax M3.1 闪光灯** |最小最大 | 428B/23B| MiniMax 社区许可证 | 1M |具有图像和视频输入的代理编码|
| **基米K3.1 Pro** |登月人工智能 | 2.8T/104B| Kimi K3.1-Pro 许可证（定制）| 1M |最艰巨的长期代理任务|
| **MiMo-V2.6-Pro** |小米| 1.02T/42B|麻省理工学院 | 1M | MIT 许可证上的长时间工具使用会话 |
| **DeepSeek V4 Pro (0813)** |深度搜索 |总重1.65吨 |麻省理工学院 | 1M |大型代码库的深度推理 |
| **缪斯微光30B** |元 | 29.6B密|阿帕奇2.0 | 131K|消费类硬件上的本地编码代理 |

### 1.DeepSeek V4.1 闪存 (1017)

[DeepSeek V4.1 Flash-1017](https://deepinfra.com/deepseek-ai/DeepSeek-V4.1-Flash-1017)是DeepSeek Flash系列的10月更新，是目前独立排行榜上最强的开放权重模型。在 [LiveBench 2.0](https://livebench.ai/) 上，它在编码类别中得分为 80.4，是所有开放权重模型中最高的，并且领先于几个专有模型。

DeepSeek 自己的模型卡在 DeepSWE v1.1 上报告为 77.0，在 Terminal-Bench 4.0 上报告为 42.3，均高于原始 V4.1 Flash（74.2 和 31.2）。此更新还减少了任务执行时间和输出长度，这对于按输出令牌付费的代理很重要。该模型是 MIT 许可的、多模式的，并支持 1M 令牌上下文窗口。

它也是本指南中最便宜的严肃编码模型。在 DeepInfra 上，在 51% 启动促销期间，其定价为每百万输入代币 0.098 美元，每百万输出代币 0.294 美元（标价 0.20 美元和 0.60 美元），并且它支持 0.8× 的 Flex 层，用于可以等待的工作。

### 2. Mistral大型 4

[Mistral Large 4](https://huggingface.co/mistralai/Mistral-Large-4-1T-A52B) 是 Mistral AI 最大的模型：约 1 万亿个参数，每个令牌有 490 亿个活跃值，原生多模式，具有 1M 令牌上下文窗口。 Mistral 于 2026 年 10 月 29 日发布了权重，并表示该模型是在其位于欧洲的数据中心进行训练的。它取代 Devstral 作为 Mistral 模型来考虑进行编码。

在 LiveBench 2.0 上，它的编码得分为 79.4，落后 DeepSeek V4.1 Flash-1017 一分，远远领先于其他开放权重领域。其长期代理得分为 24.7，在无人值守工作方面处于中游水平。 （LiveBench 列出了两个 Mistral Large 4 条目；这些数字是 10 月 29 日条目的数据，与开放重量版本相匹配。早期条目的编码得分为 44.4。）

Mistral 生态系统开放权重许可证是经过修改的 MIT 许可证，允许商业和内部使用，但有一个条件：运营模型即服务业务的公司需要获得 Mistral 的单独商业许可证。在撰写本文时，DeepInfra 不为 Mistral Large 4 提供服务，因此路由是 Mistral 自己的 API 或自托管，在这种规模下意味着多 GPU 集群。

### 3.GLM-5.3

[GLM-5.3](https://deepinfra.com/zai-org/GLM-5.3) 使用与 GLM-5.2 相同的基础模型，所有收益都来自训练后。 Z.ai 的[模型卡](https://huggingface.co/zai-org/GLM-5.3) 报告了长期工作的大幅跃升：DeepSWE v1.1 从 46.2 上升到 66.9，Terminal-Bench 2.1 从 81.0 上升到 88.2，SWE-Marathon v1.1 从 19.4 上升到 42.5。它还报告了其比较中最高的 Cyber​​Gym 分数 (84.5)，这使其成为安全审查代理的候选者。

完整的 GLM-5.3 尚未在 LiveBench 2.0 上列出。它的较小兄弟 [GLM-5.3-Flash](https://deepinfra.com/zai-org/GLM-5.3-Flash) 是，编码得分为 70.9，在开放权重模型中排名第三。

在使用许可证构建产品之前，请先检查许可证。 GLM-5.3 遵循定制的 GLM-5.3 许可证，其内容类似于 MIT，但附加了一个条件：年收入超过 100 亿美元的模型即服务业务的公司必须在商业使用之前通过 Z.ai 安全审查。 GLM-5.3-Flash 是普通的 MIT。在 DeepInfra 上，GLM-5.3 每百万代币的投入成本为 0.563 美元，产出成本为 2.50 美元，促销率为 38%（列表为 0.90 美元和 4.00 美元），并提供 Flex。

### 4.Qwen3.8-27B

[Qwen3.8-27B](https://deepinfra.com/Qwen/Qwen3.8-27B) 是 Apache 2.0 下的一个密集的 270 亿参数模型，它是要击败的小模型。其混合架构将门控 DeltaNet 线性注意力模块与门控注意力层相结合，原生支持 262K 令牌上下文，并包含视觉编码器。

在 LiveBench 2.0 上，它的编码得分为 69.3，尽管尺寸只有 GLM-5.3-Flash 的一小部分，但与 GLM-5.3-Flash 相差仅两分。 Qwen 的模型卡在 SWE-bench Pro 上报告为 61.7，在 Terminal-Bench 2.1 上报告为 73.0，在 LiveCodeBench v6 上报告为 90.3。其 DeepSWE v1.1 得分为 42.2，远低于本指南中的大型模型，这是 27B 模型的真实写照：在包含任务上很强，在多小时任务上较弱。 LiveBench 也显示出同样的情况，长期代理得分为 15.9。

在 DeepInfra 上，每百万代币的投入成本为 0.15 美元，产出成本为 1.875 美元，促销率为 25%（分别为 0.20 美元和 2.50 美元），具有 Flex 和优先级。

### 5.MiniMax M3.1 闪光灯

[MiniMax M3.1 Flash](https://huggingface.co/MiniMaxAI/MiniMax-M3.1-Flash) 是一种原生多模式专家混合模型，适用于编码、代理工作流程和计算机使用。它拥有约 4280 亿个总参数，每个令牌有 230 亿个活跃参数，接受文本、图像和视频，并支持多达 100 万个上下文令牌。它在 LiveBench 2.0 编码中得分为 68.8。

MiniMax 在 DeepSWE v1.1 上报告 73.7，在 Terminal-Bench 4.0 上报告 38.1，在 NL2Repo-Bench 上报告 61.2。该卡还公布了 DeepSeek V4.1 Flash-1017 的数据以及自己的数据，而 DeepSeek 在这三项数据上均处于领先地位。

有两件事需要知道。首先，MiniMax 社区许可证默认授予非商业用途；商业用途需要显示“Built with MiniMax M3.1-Flash”，通知MiniMax，并在产品年收入超过2000万美元后获得书面授权。其次，在撰写本文时，DeepInfra 不支持 M3.1 Flash。它使用 Flex 以每百万代币 0.28 美元的输入和 1.10 美元的输出为早期的 [MiniMax-M3](https://deepinfra.com/MiniMaxAI/MiniMax-M3) 提供服务。

### 6.基米K3.1 Pro

[Kimi K3.1 Pro](https://deepinfra.com/moonshotai/Kimi-K3.1-Pro) 是这里最大的模型：总参数 2.8 万亿个，活跃参数 1040 亿个。它是通过大规模强化学习从 Kimi K3 进行后训练的，并用稀疏注意力取代了 K3 的全注意力层，以实现更高效的长上下文工作。

它的外形与 Qwen 的相反。在 LiveBench 2.0 上，它在编码方面得分为 67.8，中等水平，但在长期代理类别中得分为 38.7，与开放权重领域顶级的 DeepSeek V4.1 Flash-1017 持平。 Moonshot 的卡在 DeepSWE v1.1 上报告 75.5，在 Terminal-Bench 4.0 上报告 65.7，在 SWE Marathon v1.1 上报告 51.7。它在 LiveBench 编码中比 Kimi K3 提高了近 15 分（67.8 对 53.1）。

它也是最昂贵的开放权重选项：DeepInfra 上每百万代币 1.90 美元的输入和 9.50 美元的输出（比 2.00 美元和 10.00 美元的标价低 5%），Flex 为 0.8 倍。 Kimi K3.1-Pro 许可证是 MIT 风格的，附带条件：年收入超过 2000 万美元的模型即服务运营商需要与 Moonshot 签订单独协议，并且非常大的消费产品必须显示模型名称。内部使用以及通过 Moonshot 的认证推理合作伙伴使用不受限制。

### 7.MiMo-V2.6-Pro

[MiMo-V2.6-Pro](https://deepinfra.com/XiaomiMiMo/MiMo-V2.6-Pro)是小米的万亿参数推理模型：总参数1.02万亿，活跃数420亿，1M令牌上下文窗口，以及文本、图像、视频和音频输入。它带有简单的 MIT 许可证，这使其成为本指南中商业采用的最简单的大型模型。

本指南中与上一版本的跳跃是最大的。小米卡报告 DeepSWE v1.1 在 MiMo-V2.5 Pro 上从 19.0 上升到 71.9，Terminal-Bench 2.1 从 65.2 上升到 89.9。在 LiveBench 2.0 上，它在编码方面得分为 64.5，在长期代理工作方面得分为 36.4，在后者的开放权重模型中排名第三。

在 DeepInfra 上，每百万代币的输入成本为 0.387 美元，输出成本为 0.783 美元（比标价 0.43 美元和 0.87 美元优惠 10%）。较低的产出价格非常引人注目：对于在代理工作中与 Kimi K3.1 Pro 接近的型号来说，它的价格还不到 Kimi K3.1 Pro 的十分之一。

### 8.DeepSeek V4 Pro (0813)

[DeepSeek V4 Pro-0813](https://deepinfra.com/deepseek-ai/DeepSeek-V4-Pro-0813) 是 DeepSeek 旗舰产品 8 月份的生产版本，拥有 1.65 万亿个参数，具有 1M 代币上下文窗口和 MIT 许可证。它尚未在 LiveBench 2.0 上列出，因此这里的证据是供应商报告的。

DeepSeek 的卡片显示了它与预览版的差距：Terminal-Bench 2.1 从 72.1 到 87.9，DeepSWE 从 12.8 到 62.7，NL2Repo 从 38.5 到 61.5。请注意，更新且便宜得多的 V4.1 Flash-1017 报告了更高的 DeepSWE v1.1 分数 (77.0)。当您需要更大的模型对困难的单次问题进行推理时，请选择 V4 Pro，而对于代理循环，请选择 V4.1 Flash。

在 DeepInfra 上，每百万代币的输入成本为 1.30 美元，缓存输入为 0.10 美元，输出成本为 2.60 美元，Flex 的成本为 1.04 美元和 2.08 美元。对于编码代理来说，缓存输入率值得关注，编码代理在每个步骤中都会重新发送相同的存储库上下文。

### 9. 缪斯微光 30B

[Muse Glimmer 30B](https://deepinfra.com/meta-models/Muse-Glimmer-30B) 是 Meta 的开放模型，适用于在本地或消费者硬件上运行的代理。它是 Apache 2.0 下的一个密集的 296 亿参数模型，于 2026 年 8 月发布，具有图像输入和 131K 令牌上下文窗口。

Meta 在 SWE-bench Verified 上报告 76.0，在 SWE-bench Pro 上报告 51.2，在 Terminal-Bench 2.1 上报告 51.7。它的与众不同之处在于包装。 Meta 推出了两个大约 4 位的变体，分别针对 32GB 和 24GB VRAM，报告平均性能下降 0.2% 和 1.0%，此外还有一个推测性解码起草器，据说可以将 RTX 5090 上的生成速度从每秒 74.9 个令牌提升到 233.4 个令牌。 Qwen3.8-27B 在 Qwen 自己的卡上发布了更高的编码分数（在 SWE-bench Pro 上为 61.7，而在 SWE-bench Pro 上为 51.2），因此当本地速度和现成的量化构建比最后几点更重要时，Glimmer 是首选。

如果您不想自己运行它，DeepInfra 会以每百万代币 0.30 美元的输入和 1.20 美元的输出提供服务。

## 开源编码模型与专有模型的对比

为了设置上下文，有必要了解[开源相对于专有选项的立场](https://deepinfra.com/blog/open-source-vs-lated-source-ai-models-price-gap)。

专有模型提供可靠的工具调用、完善的 IDE 集成、托管基础架构以及跨编码任务的一致性能。权衡是控制：基于使用的定价可能是不可预测的，并且封闭的 API 限制了您对数据处理和服务基础设施的选择。

开放权重模型为您在部署、微调和提供商选择方面提供了更大的灵活性。权衡是，自托管可能需要更多的基础设施和工程工作来优化、监控和维护模型。

以下是 2026 年 11 月 6 日发布的 [LiveBench 2.0](https://livebench.ai/) 列出的开放权重模型的结果。 GLM-5.3、DeepSeek V4 Pro-0813 和 Muse Glimmer 30B 尚未出现在排行榜上，因此没有出现。每个类别中最高的专有分数都作为参考线包含在内。

### LiveBench 2.0 编码

|型号|组织|类型 |编码 |
| --- | --- | --- | --- |
| Gemini 4 Carbon（参考）|谷歌 |专有| 91.0 |
| **DeepSeek V4.1 Flash-1017** |深度搜索 |开放式举重| **80.4** |
| **Mistral大 4** |Mistral人工智能 |开放式举重| 79.4 | 79.4
| **GLM-5.3-闪存** | Z.ai |开放式举重| 70.9 | 70.9
| **Qwen3.8-27B** |阿里巴巴 |开放式举重| 69.3 | 69.3
| **MiniMax M3.1 闪光灯** |最小最大 |开放式举重| 68.8 |
| **基米K3.1 Pro** |登月人工智能 |开放式举重| 67.8 | 67.8
| **MiMo-V2.6-Pro** |小米|开放式举重| 64.5 | 64.5
| **Muse Spark 开放** |元 |开放式举重| 55.1 | 55.1
| **Nemotron 3.5 Super VL** |英伟达 |开放式举重| 54.1 | 54.1
| **基米K3** |登月人工智能 |开放式举重| 53.1 | 53.1

### LiveBench 2.0 长期代理

|型号|组织|类型 |长期代理|
| --- | --- | --- | --- |
|Claude寓言5.2（参考）|Anthropic |专有| 82.9 | 82.9
| **DeepSeek V4.1 Flash-1017** |深度搜索 |开放式举重| **38.8** |
| **基米K3.1 Pro** |登月人工智能 |开放式举重| 38.7 | 38.7
| **MiMo-V2.6-Pro** |小米|开放式举重| 36.4 | 36.4
| **基米K3** |登月人工智能 |开放式举重| 36.0 |
| **MiniMax M3.1 闪光灯** |最小最大 |开放式举重| 25.7 | 25.7
| **Mistral大 4** |Mistral人工智能 |开放式举重| 24.7 | 24.7
| **GLM-5.3-闪存** | Z.ai |开放式举重| 20.7 | 20.7
| **Qwen3.8-27B** |阿里巴巴 |开放式举重| 15.9 | 15.9
| **Muse Spark 开放** |元 |开放式举重| 12.1 | 12.1
| **Nemotron 3.5 Super VL** |英伟达 |开放式举重| 12.0 |

两张桌子讲述着不同的故事。在编码方面，最好的开放权重模型比最好的专有模型落后大约十个百分点。在长期代理工作中，即无人值守数小时的工作中，差距超过四十个百分点。实际阅读：开放权重模型已准备好进行大量编码工作，包括错误修复、重构、测试编写和监督代理循环。对于完全自主的多小时任务，专有模型仍然物有所值，常见的设置是[在两者之间路由](https://deepinfra.com/blog/two-tier-agent-two-models)。

## 开源编码模型真的免费吗？

免费获取模型权重并不意味着零成本。您仍然需要 GPU、存储、网络、推理软件、监控、安全控制、升级和工程时间。大型[混合专家模型](https://deepinfra.com/blog/mixture-of-experts-llm-economics-price-drop)可能只为每个代币激活一小部分参数，但服务系统仍然需要内存中的全套权重。

开放式举重还附带许可条款。 MIT 和 Apache 2.0 授予广泛的使用、修改和重新分发的权利。这里的九个型号中有四个使用具有商业条件的自定义许可证：Mistral Large 4、GLM-5.3、Kimi K3.1 Pro 和 MiniMax M3.1 Flash。

当您具有稳定、高使用率、严格的源代码隐私要求、现有 GPU 容量或使硬件保持繁忙的可预测工作负载时，自托管通常很经济。当使用情况不确定，或者您想在提交基础设施之前测试多个模型时，托管的开放模型 API 通常更有意义。

您可以通过简单的计算来比较这两个选项：

- 每月托管成本 = 输入令牌成本 + 输出令牌成本，减去任何缓存输入和 Flex 节省
- 自托管每月成本=GPU小时数+存储+网络+监控+工程运营

## 开源编码模型在哪里提供最大价值？

开源编码模型在不同场景中提供了多种操作优势。

- **私有代码库：** 当源代码、凭据、客户数据或内部文档无法离开您的环境时，您可以在受控基础设施内运行模型。
- **大容量代理工作流程：** 自托管或低成本开放模型 API 为重复存储库分析、测试执行、调试和工具调用提供了更可预测的成本。
- **模型定制：**您可以微调模型、调整其推理设置、添加特定于领域的工具或训练内部框架和编程语言的适配器。
- **部署控制：** 您的团队可以固定经过测试的模型版本、选择硬件、控制延迟并决定何时应用升级。托管模型 ID 仍然会停用，因此无论哪种方式[计划弃用](https://deepinfra.com/blog/model-deprecation-llm-apps)。
- **特定于硬件的工作负载：** 您可以根据可用 VRAM、吞吐量目标、量化支持和预期上下文长度选择密集或 MoE 架构。
- **减少提供商依赖性：** 开放权重使得在托管 API、私有端点和自我管理基础设施之间移动变得更加容易，而无需重建编码应用程序。

## 在本地或自托管运行开源编码模型

一些服务框架支持开放编码模型：

- **vLLM** 专注于高吞吐量 GPU 服务和生产 API。
- **SGLang** 提供高效的结构化生成和面向代理的服务。我们的[vLLM 与 SGLang 比较](https://deepinfra.com/blog/vllm-vs-sglang) 介绍了如何在两者之间进行选择。
- **llama.cpp** 跨 CPU、消费级 GPU 和 Apple Silicon 运行量化模型。
- **Ollama** 简化了本地模型安装和 API 访问。
- **LM Studio** 提供桌面界面和本地 OpenAI 兼容服务器。

在本地运行模型时，请考虑其大小、精度和上下文窗口。本指南中的两个型号均适合其尺寸。 Muse Glimmer 30B 附带量化版本，Meta 目标为 24GB 和 32GB VRAM。 Qwen3.8-27B 是一个 27B 密集模型，因此四位构建仅用于权重就需要大约 14GB，一旦添加运行时开销和上下文，24GB GPU 就是一个实用的起点。

这里的其他一切都是数据中心模型。其他七个（DeepSeek V4.1 Flash、Mistral Large 4、GLM-5.3、MiniMax M3.1 Flash、MiMo-V2.6-Pro、DeepSeek V4 Pro、Kimi K3.1 Pro）运行 4280 亿到 2.8 万亿个参数，需要多 GPU 服务器。

这些模型是本地或托管的，可连接到任何接受 OpenAI 兼容端点的编码工具，包括 [OpenCode](https://deepinfra.com/blog/claude-code-alternative) 等开放代理。

## 在 DeepInfra 上运行这些模型

如果您想要模型而不需要自己构建服务层，最简单的方法是 DeepInfra 的 [OpenAI 兼容 API](https://docs.deepinfra.com/chat/overview)：与 OpenAI API 相同的请求格式和客户端，并按名称选择模型。上述九种型号中有七种可供选择，价格按代币计算，没有最低价格。

|型号|输入（$/1M）|产出（$/1M）|柔性层 (0.8×) |预计。每月费用* |
| --- | --- | --- | --- | --- |
| DeepSeek V4.1 Flash-1017 | 0.098 美元 | 0.294 美元 |是的 | 15.68 美元 |
| Qwen3.8-27B | 0.15 美元 | 1.875 美元 |是的 | 52.50 美元 |
|缪斯微光 30B | 0.30 美元 | 1.20 美元 |没有 | 54.00 美元 |
| MiMo-V2.6-Pro | 0.387 美元 | 0.783 美元 |没有 | 54.36 美元 |
| GLM-5.3 | 0.563 美元 | 2.50 美元 |是的 | 106.30 美元 |
| DeepSeek V4 Pro-0813 | 1.30 美元 | 2.60 美元 |是的 | 182.00 美元 |
|基米K3.1 Pro | 1.90 美元 | 9.50 美元 |是的 | $380.00 |

**在缓存输入节省之前，估计标准层每月 100M 个输入令牌和 20M 个输出令牌。价格来自 DeepInfra 2026 年 11 月 17 日的型号页面。DeepSeek V4.1 Flash-1017、Qwen3.8-27B、MiMo-V2.6-Pro、GLM-5.3 和 Kimi K3.1 Pro 为促销价格；上面每个型号的部分给出了标价。 MiniMax M3.1 Flash 和 Mistral Large 4 不提供服务；早期的 MiniMax-M3 价格为 0.28 美元和 1.10 美元。*

传播是重点。相同的工作负载在 LiveBench 编码得分最高的模型上花费 15.68 美元，在最大的模型上花费 380 美元，相差 24 倍。三种设置可以进一步降低费用：

- **Flex 层。** 带有 Flex 标签的型号以标准价格的 0.8 倍运行，以换取较慢的响应速度和偶尔的不可用。这适合批量重构、测试生成和隔夜代理运行。上述 DeepSeek V4.1 Flash-1017 的预估值降至 12.54 美元左右。
- **缓存输入。** 编码代理在每个步骤中重新发送相同的系统提示、工具定义和存储库上下文。这些重复的代币按缓存输入费率计费：例如，在 DeepSeek V4 Pro-0813 上，每百万美元 0.10 美元，而不是 1.30 美元。我们的[提示卫生](https://deepinfra.com/blog/prompt-hygiene-cheaper-faster-llm-calls)指南介绍了如何构建提示以便缓存命中。
- **推理工作。** 其中一些模型接受 `reasoning_effort` 设置。 GLM-5.3 默认为“max”；日常编辑时降低到“高”或“低”会减少输出标记。

对于围绕编码代理的大量支持工作，例如读取构建日志或通过屏幕截图对问题进行分类，[Nemotron 3.5 Super VL](https://deepinfra.com/nvidia/NVIDIA-Nemotron-3.5-Super-VL) 是一种低成本多模式选项，每百万代币输入 0.15 美元，输出 0.50 美元。它在 LiveBench 2.0 编码中的得分为 54.1，因此可以使用它来执行简单的步骤。

如果响应速度是产品，就像内联自动完成一样，那么测试提供程序也建立在速度专用硬件上。对于代理、批量工作以及按数量计费的任何事物，每个代币的差距都会加剧。

以下是如何使用 Python 客户端调用这些模型之一：
```
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPINFRA_API_KEY"],
    base_url="https://api.deepinfra.com/v1/openai",
)

response = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V4.1-Flash-1017",
    messages=[
        {"role": "system", "content": "You are a coding assistant. Return only the refactored code."},
        {"role": "user", "content": "Refactor this function for readability:\n\ndef f(a,b):\n    return [x for x in a if x not in b]"},
    ],
    temperature=0.2,
)

print(response.choices[0].message.content)copy
```
要尝试不同的模型，请更改模型名称。

## 底线

最佳的开源编码模型取决于工作。

对于大多数团队来说，从 DeepSeek V4.1 Flash-1017 开始：它在开放权重模型中具有最高的独立编码分数、MIT 许可证以及本指南中最低的价格。如果您的代理运行长时间、无人值守的任务，请对其进行测试 Kimi K3.1 Pro 和 MiMo-V2.6-Pro；他们在长期工作上的得分接近它，而 MiMo 是在麻省理工学院的许可下以较低的产出价格做到这一点的。对于具有安全角度的长视野编码，在许可允许的情况下，GLM-5.3 是可以评估的。如果您需要一个可以自己运行的小型模型，请选择 Qwen3.8-27B 进行乐谱，或选择 Muse Glimmer 30B 进行现成的本地构建。 Mistral Large 4 在编码方面几乎与 DeepSeek 相匹配，如果欧洲构建的模型对您很重要，只要您可以使用 Mistral 的 API 或自己托管万亿参数模型，那么 Mistral Large 4 就是您的选择。

无论您入围哪一个，请在提交之前在您自己的存储库中对其进行衡量。供应商基准测试使用不同的工具，独立排行榜尚未涵盖此处的所有型号。

访问 [DeepInfra 模型页面](https://deepinfra.com/models) 来比较跨上下文窗口和定价的开源模型。如有任何问题或反馈，请通过 [feedback@deepinfra.com](mailto:feedback@deepinfra.com) 与我们联系。您还可以在 [Discord](https://discord.gg/deepinfra) 上加入社区，或者在 X 上的 [@DeepInfra](https://x.com/DeepInfra) 上找到我们。

相关文章

[![Kimi K2.5 的最佳 API：为什么 DeepInfra 在速度、TTFT 和可扩展性方面领先](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/02/Best-API-for-Kimi_sized.jpg)](https://deepinfra.com/blog/best-api-for-kimi-k2-5-deepinfra)[最佳 API Kimi K2.5：为什么 DeepInfra 在速度、TTFT 和可扩展性方面领先](https://deepinfra.com/blog/best-api-for-kimi-k2-5-deepinfra)<p>更新于 2026 年 11 月。Kimi K2.5 被定位为 Moonshot AI 针对现代产品工作流程的“全能”模型：原生多模态（文本 + 视觉/视频）、即时模式与思考模式以及对代理/多代理（“群”）执行模式。然而，在实际应用中，模型功能只是故事的一半。提供商的推理堆栈决定了您的用户实际的事物 [...]</p>

[![从搜索结果到证据：DeepInfra 上的 NVIDIA Nemotron 3.5 嵌入和重新排名](https://deepinfra.com/blog/nvidia-nemotron-3.5-embed-rerank-release.png)](https://deepinfra.com/blog/nvidia-nemotron-3.5-embed-rerank-release)[从搜索结果到证据：NVIDIA Nemotron 3.5 嵌入DeepInfra 上的重新排序](https://deepinfra.com/blog/nvidia-nemotron-3.5-embed-rerank-release)NVIDIA Nemotron 3.5 Embed 和 Rerank 从第 0 天开始在 DeepInfra 上可用。通过 DeepInfra API 调用 Embed 1B、Embed 8B 和 Rerank 8B，无需部署设置和按代币付费定价。

[![介绍提示缓存保留：让您的环境保持温暖 5 分钟或一个小时](https://deepinfra.com/blog/prompt-cache-retention.jpg)](https://deepinfra.com/blog/prompt-cache-retention)[介绍提示缓存保留：让您的环境保持温暖 5 分钟或一个小时小时](https://deepinfra.com/blog/prompt-cache-retention)将提示的 KV 缓存保留 5 分钟或一个小时 - 重用会跳过预填充，以更快地获得第一个令牌，并以折扣缓存读取速率计费。请求中的一个字段。

[查看全部](https://deepinfra.com/blog)
