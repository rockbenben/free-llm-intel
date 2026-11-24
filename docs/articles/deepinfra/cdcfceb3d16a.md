---
vendor: deepinfra
title: 9 个最佳开源编程模型（2026 年 11 月）
original_title: 
url: https://deepinfra.com/blog/best-open-source-models-for-coding
date: 2026-11-17
lang: zh
captured: 2026-11-17
extractor: readability-v1
translator: agent
status: translated
body_sha: 97645ce6153c
---

# 9 个最佳开源编程模型（2026 年 11 月）

DeepInfra 发布于 2026.11.17

![9 个最佳开源编程模型（2026 年 11 月）](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/11/best-open-source-models-for-coding-header.png)

现代 AI 编程工具如今能分析代码仓库、修复 bug、编辑多个文件、运行测试，并执行自主开发循环。这些 agentic 工作流通过持续不断的模型调用产生数以百万计的输入和输出 token，这让专有 API 在规模化时变得昂贵。

开源编程模型提供了一种更具成本效益的替代方案。你可以在私有基础设施上运行它们，自选服务硬件，锁定某个特定模型版本，调整 inference 设置，并减少对单一 API 提供商的依赖。像 [DeepInfra](https://deepinfra.com/) 这样的托管推理服务还让你无需自己管理 GPU 就能使用这些模型，按 token 计价；本指南中得分最高的模型，每百万输入 token 的价格低于 $0.10。

在本指南中，我们对比截至 2026 年 11 月的领先开源编程模型。我们从编程 benchmark、context window 大小、许可证条款和 API 成本几个维度评估它们，并在文末介绍自托管方案。分数和价格截至 2026 年 11 月 17 日。

## 如何评估编程模型：真正重要的 benchmark

关注下面这些 benchmark，可以判断一个模型在你计划自动化的任务上表现如何。

- [**HumanEval**](https://github.com/openai/human-eval) **和 [MBPP（Mostly Basic Python Problems）](https://huggingface.co/datasets/Muennighoff/mbpp)** 衡量函数级代码生成能力。模型会收到一段简短的自然语言问题，必须产出能通过单元测试的 Python 代码。它们能快速衡量基础编程能力，但不检验仓库导航、工具使用或多文件改动，而且当前模型大多已经把这两项刷满。
- [**SWE-bench Verified**](https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified) **和 [SWE-bench Pro](https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro)** 评估模型在 agentic 编程工作流中解决真实 GitHub issue 的能力。模型必须通读整个代码库、定位 bug 源头、跨多个文件写出 patch，并通过执行测试。
- **DeepSWE** 是今年大多数 model card 都会报告的长周期软件工程 benchmark。由于 DeepSeek、Moonshot、MiniMax、Xiaomi、Z.ai 和 Qwen 都公布了 DeepSWE v1.1 分数，它最接近一个跨厂商的共同标尺——前提是每家厂商都跑自己的 harness。
- [**Terminal-Bench**](https://www.tbench.ai/) 对比模型在 shell 命令、command-line interface（CLI）和 DevOps 相关任务上的表现。厂商现在报告 2.1 和 4.0 两个版本，而且结果会随所用的 agent harness 大幅变化，所以只在同一份 model card 内比较分数。
- [**LiveBench**](https://livebench.ai/) 是独立评测，并定期刷新，以限制训练数据污染。LiveBench 于 2026 年 11 月 6 日切换到 2.0 版本。新版本评估长周期工作（bug 修复、连续运行数小时的应用、研究报告），其分数与 2026 年 11 月 6 日之前发布的 LiveBench 数据不可直接比较。

除了排行榜，还要看 context window 和许可证。一个在函数级补全上看着不错的模型，用于整仓库重构或私有本地部署时仍可能是糟糕的选择。

- **Context window** 决定模型在单次请求中能处理多少代码、文档、终端输出和对话历史。更大的 context window 有助于仓库分析和长时间运行的 agent 会话。
- **许可证**决定你能否将权重用于商业用途、修改它们、再分发模型，或通过托管服务提供该模型。“开源”在这个领域是个被宽松使用的词。下面有几个模型以带商业条件的定制许可证发布 open weights，我们会逐一注明。我们关于 [open-weight 模型许可证](https://deepinfra.com/blog/open-weight-model-licenses) 的指南介绍了需要核查什么。

## 九大开源编程模型横评

以下是当前顶尖开源编程模型在规模、许可证、context window 以及各自最擅长领域上的对比：

| 模型 | 开发者 | 参数（总计 / 激活） | 许可证 | Context window | 最擅长 |
| --- | --- | --- | --- | --- | --- |
| **DeepSeek V4.1 Flash (1017)** | DeepSeek | 总计 763B | MIT | 1M | 每美元最高编程分数 |
| **Mistral Large 4** | Mistral AI | 1T / 49B | Mistral Ecosystem Open-Weight License | 1M | 欧洲打造、编程分数接近顶尖的通用模型 |
| **GLM-5.3** | Z.ai | 总计 753B | GLM-5.3 License (custom) | 1M | 长周期编程与安全工作 |
| **Qwen3.8-27B** | Alibaba Qwen | 27B dense | Apache 2.0 | 262K | 小型部署与本地使用 |
| **MiniMax M3.1 Flash** | MiniMax | 428B / 23B | MiniMax Community License | 1M | 支持图像和视频输入的 agentic 编程 |
| **Kimi K3.1 Pro** | Moonshot AI | 2.8T / 104B | Kimi K3.1-Pro License (custom) | 1M | 最难的长周期 agent 任务 |
| **MiMo-V2.6-Pro** | Xiaomi | 1.02T / 42B | MIT | 1M | MIT 许可证下的长工具调用会话 |
| **DeepSeek V4 Pro (0813)** | DeepSeek | 总计 1.65T | MIT | 1M | 大型代码库上的深度推理 |
| **Muse Glimmer 30B** | Meta | 29.6B dense | Apache 2.0 | 131K | 消费级硬件上的本地编程 agents |

### 1. DeepSeek V4.1 Flash (1017)

[DeepSeek V4.1 Flash-1017](https://deepinfra.com/deepseek-ai/DeepSeek-V4.1-Flash-1017) 是 DeepSeek Flash 系列的 10 月更新，也是当前独立排行榜上最强的 open-weight 模型。在 [LiveBench 2.0](https://livebench.ai/) 上，它的 coding 类别得分 80.4，是所有 open-weight 模型中最高的，并领先于若干专有模型。

DeepSeek 自己的 model card 报告 DeepSWE v1.1 为 77.0、Terminal-Bench 4.0 为 42.3，均高于最初的 V4.1 Flash（74.2 和 31.2）。这次更新还缩短了任务执行时间和输出长度，这对按输出 token 付费的 agents 很重要。该模型采用 MIT 许可证，是多模态模型，支持 1M token 的 context window。

它也是本指南中最便宜的、真正能打的编程模型。在 DeepInfra 上，51% 上线促销期间每百万输入 token 定价 $0.098、每百万输出 token $0.294（目录价 $0.20 和 $0.60），并且支持 Flex 档位，以 0.8× 的价格处理可以等待的工作。

### 2. Mistral Large 4

[Mistral Large 4](https://huggingface.co/mistralai/Mistral-Large-4-1T-A52B) 是 Mistral AI 最大的模型：约 1 万亿参数，每个 token 激活 490 亿，原生多模态，context window 为 1M token。Mistral 于 2026 年 10 月 29 日发布了权重，并表示该模型在其位于欧洲的自有数据中心训练。它取代 Devstral，成为考虑用于编程的 Mistral 模型。

在 LiveBench 2.0 上，它的 coding 得分是 79.4，比 DeepSeek V4.1 Flash-1017 低 1 分，明显领先 open-weight 阵营的其余模型。它的长周期 agentic 得分是 24.7，在无人值守工作上处于中游。（LiveBench 列出了两个 Mistral Large 4 条目；这里的数字对应 10 月 29 日的条目，与 open-weight 发布一致。较早那个条目的 coding 得分是 44.4。）

Mistral Ecosystem Open-Weight License 是一份修改过的 MIT 许可证，允许商业和内部使用，但有一个条件：经营 model-as-a-service 业务的公司需要从 Mistral 获得单独的商用许可。截至撰写本文时，DeepInfra 并未提供 Mistral Large 4，所以途径只有 Mistral 自家的 API 或自托管——以这个规模而言，就意味着一个多 GPU 集群。

### 3. GLM-5.3

[GLM-5.3](https://deepinfra.com/zai-org/GLM-5.3) 使用与 GLM-5.2 相同的基础模型，全部提升都来自 post-training。Z.ai 的 [model card](https://huggingface.co/zai-org/GLM-5.3) 报告了长周期工作上的大幅跃升：DeepSWE v1.1 从 46.2 升到 66.9，Terminal-Bench 2.1 从 81.0 升到 88.2，SWE-Marathon v1.1 从 19.4 升到 42.5。它还报告了其对比中的最高 CyberGym 分数（84.5），这让它成为安全审查 agents 的候选。

完整的 GLM-5.3 尚未出现在 LiveBench 2.0 上。它更小的兄弟版本 [GLM-5.3-Flash](https://deepinfra.com/zai-org/GLM-5.3-Flash) 已在榜上，coding 得分 70.9，在 open-weight 模型中排第三。

基于它构建产品之前，先检查许可证。GLM-5.3 以定制的 GLM-5.3 License 发布，读起来像 MIT，但多了一个条件：年收入超过 100 亿美元且经营 model-as-a-service 业务的公司，必须在商业使用前通过 Z.ai 的安全审查。GLM-5.3-Flash 是纯 MIT。在 DeepInfra 上，GLM-5.3 在 38% 促销下每百万 token 输入 $0.563、输出 $2.50（目录价 $0.90 和 $4.00），并提供 Flex。

### 4. Qwen3.8-27B

[Qwen3.8-27B](https://deepinfra.com/Qwen/Qwen3.8-27B) 是一个采用 Apache 2.0 的 dense 270 亿参数模型，也是小模型中要被追赶的那个。它的混合架构把 Gated DeltaNet 线性注意力块与 Gated Attention 层结合起来，原生支持 262K token 的 context，并包含一个视觉编码器。

在 LiveBench 2.0 上，它的 coding 得分是 69.3，与 GLM-5.3-Flash 相差不到 2 分，而规模只是后者的零头。Qwen 的 model card 报告 SWE-bench Pro 为 61.7、Terminal-Bench 2.1 为 73.0、LiveCodeBench v6 为 90.3。它的 DeepSWE v1.1 得分是 42.2，远低于本指南中的大模型——这正是 27B 模型的真实写照：在有边界的任务上强，在多小时任务上弱。LiveBench 也显示了同样的情况：长周期 agentic 得分 15.9。

在 DeepInfra 上，25% 促销下每百万 token 输入 $0.15、输出 $1.875（目录价 $0.20 和 $2.50），并提供 Flex 和 Priority 档位。

### 5. MiniMax M3.1 Flash

[MiniMax M3.1 Flash](https://huggingface.co/MiniMaxAI/MiniMax-M3.1-Flash) 是一个原生多模态的 mixture-of-experts 模型，面向编程、agentic 工作流和计算机操作。它总参数约 4280 亿，每个 token 激活 230 亿，接受文本、图像和视频输入，最高支持 1M token 的 context。它在 LiveBench 2.0 coding 中得分 68.8。

MiniMax 报告 DeepSWE v1.1 为 73.7、Terminal-Bench 4.0 为 38.1、NL2Repo-Bench 为 61.2。它的 model card 还把自己的数字和 DeepSeek V4.1 Flash-1017 并排列出，而 DeepSeek 在这三项上全部领先。

有两点需要知道。第一，MiniMax Community License 默认只授予非商业使用权；商业使用需要展示“Built with MiniMax M3.1-Flash”、通知 MiniMax，并在产品年收入超过 2000 万美元后获得书面授权。第二，截至撰写本文时，DeepInfra 并未提供 M3.1 Flash，而是提供更早的 [MiniMax-M3](https://deepinfra.com/MiniMaxAI/MiniMax-M3)，每百万 token 输入 $0.28、输出 $1.10，并提供 Flex。

### 6. Kimi K3.1 Pro

[Kimi K3.1 Pro](https://deepinfra.com/moonshotai/Kimi-K3.1-Pro) 是本指南中最大的模型：总参数 2.8 万亿，激活 1040 亿。它基于 Kimi K3 通过大规模强化学习做 post-training，并用稀疏注意力替换了 K3 的 full-attention 层，以便更高效地处理长上下文工作。

它的画像与 Qwen 正好相反。在 LiveBench 2.0 上，它的 coding 得分是 67.8，处于中游，但长周期 agentic 类别得分为 38.7，与 DeepSeek V4.1 Flash-1017 并列 open-weight 阵营榜首。Moonshot 的 model card 报告 DeepSWE v1.1 为 75.5、Terminal-Bench 4.0 为 65.7、SWE Marathon v1.1 为 51.7。它在 LiveBench coding 上比 Kimi K3 提升了近 15 分（67.8 对 53.1）。

它也是最贵的 open-weight 选项：在 DeepInfra 上每百万 token 输入 $1.90、输出 $9.50（相当于 $2.00 和 $10.00 目录价的 5% 折扣），Flex 档位为 0.8×。Kimi K3.1-Pro License 是 MIT 风格但带有条件：年收入超过 2000 万美元的 model-as-a-service 运营方需要与 Moonshot 单独签约，超大型消费级产品必须展示模型名称。内部使用，以及通过 Moonshot 认证推理伙伴的使用，不受此限。

### 7. MiMo-V2.6-Pro

[MiMo-V2.6-Pro](https://deepinfra.com/XiaomiMiMo/MiMo-V2.6-Pro) 是小米的万亿参数推理模型：总参数 1.02 万亿，激活 420 亿，context window 为 1M token，接受文本、图像、视频和音频输入。它采用纯 MIT 许可证，是本指南中最容易在商业上采用的大模型。

相比上一版本的跃升是本指南中最大的。小米的 model card 报告 DeepSWE v1.1 从 MiMo-V2.5 Pro 的 19.0 升至 71.9，Terminal-Bench 2.1 从 65.2 升至 89.9。在 LiveBench 2.0 上，它的 coding 得分 64.5，长周期 agentic 工作得分 36.4，后者在 open-weight 模型中排第三。

在 DeepInfra 上，每百万 token 输入 $0.387、输出 $0.783（相对 $0.43 和 $0.87 的目录价有 10% 折扣）。输出价格之低很突出：对 agentic 工作表现接近 Kimi K3.1 Pro 的模型来说，这个价格不到后者的十分之一。

### 8. DeepSeek V4 Pro (0813)

[DeepSeek V4 Pro-0813](https://deepinfra.com/deepseek-ai/DeepSeek-V4-Pro-0813) 是 DeepSeek 旗舰模型 8 月的生产发布版本，参数 1.65 万亿，context window 为 1M token，采用 MIT 许可证。它尚未出现在 LiveBench 2.0 上，因此这里的证据来自厂商自报。

DeepSeek 的 model card 展示了它相比预览版走了多远：Terminal-Bench 2.1 从 72.1 升到 87.9，DeepSWE 从 12.8 升到 62.7，NL2Repo 从 38.5 升到 61.5。注意，更新也更便宜的 V4.1 Flash-1017 报告的 DeepSWE v1.1 分数更高（77.0）。当你需要大模型在困难的单次问题上做推理时，选 V4 Pro；用于 agent 循环时，选 V4.1 Flash。

在 DeepInfra 上，每百万 token 输入 $1.30、缓存输入 $0.10、输出 $2.60，Flex 档位为 $1.04 和 $2.08。缓存输入价格值得编程 agents 关注，因为它们每一步都会重发同样的仓库上下文。

### 9. Muse Glimmer 30B

[Muse Glimmer 30B](https://deepinfra.com/meta-models/Muse-Glimmer-30B) 是 Meta 面向在本地或消费级硬件上运行的 agents 推出的开放模型。它是一个采用 Apache 2.0 的 dense 296 亿参数模型，于 2026 年 8 月发布，支持图像输入，context window 为 131K token。

Meta 报告 SWE-bench Verified 为 76.0、SWE-bench Pro 为 51.2、Terminal-Bench 2.1 为 51.7。真正让它与众不同的是封装。Meta 提供了两个约 4-bit 的变体，分别面向 32GB 和 24GB 显存，报告平均性能损失为 0.2% 和 1.0%；还附带一个 speculative decoding drafter，据称能把 RTX 5090 上的生成速度从每秒 74.9 token 提升到 233.4 token。Qwen3.8-27B 在 Qwen 自己的 model card 上给出了更高的编程分数（SWE-bench Pro 为 61.7 对 51.2），所以当本地速度和开箱即用的量化构建比最后那几分更重要时，Glimmer 就是选择。

如果你不想自己运行，DeepInfra 提供该模型，每百万 token 输入 $0.30、输出 $1.20。

## 开源编程模型与专有模型相比处于什么位置

为了建立背景，值得先弄清楚[开源模型相对专有选项处于什么位置](https://deepinfra.com/blog/open-source-vs-closed-source-ai-models-price-gap)。

专有模型提供可靠的工具调用、精致的 IDE 集成、托管基础设施，以及在各类编程任务上稳定的表现。代价是控制权：按用量计费可能难以预测，封闭 API 也限制你在数据处理和服务基础设施上的选择。

open-weight 模型在部署、微调和供应商选择上给你更大的灵活性。代价是自托管可能需要更多基础设施和工程投入，用来优化、监控和维护模型。

以下是 [LiveBench 2.0](https://livebench.ai/) 在 2026 年 11 月 6 日发布版本中，针对其列出的 open-weight 模型的结果。GLM-5.3、DeepSeek V4 Pro-0813 和 Muse Glimmer 30B 尚未上榜，因此没有出现。每个类别的最高专有模型分数作为参考行一并列出。

### LiveBench 2.0 编程

| 模型 | 组织 | 类型 | 编程 |
| --- | --- | --- | --- |
| Gemini 4 Carbon（参考） | Google | 专有 | 91.0 |
| **DeepSeek V4.1 Flash-1017** | DeepSeek | open weights | **80.4** |
| **Mistral Large 4** | Mistral AI | open weights | 79.4 |
| **GLM-5.3-Flash** | Z.ai | open weights | 70.9 |
| **Qwen3.8-27B** | Alibaba | open weights | 69.3 |
| **MiniMax M3.1 Flash** | MiniMax | open weights | 68.8 |
| **Kimi K3.1 Pro** | Moonshot AI | open weights | 67.8 |
| **MiMo-V2.6-Pro** | Xiaomi | open weights | 64.5 |
| **Muse Spark Open** | Meta | open weights | 55.1 |
| **Nemotron 3.5 Super VL** | NVIDIA | open weights | 54.1 |
| **Kimi K3** | Moonshot AI | open weights | 53.1 |

### LiveBench 2.0 长周期 agentic

| 模型 | 组织 | 类型 | 长周期 agentic |
| --- | --- | --- | --- |
| Claude Fable 5.2（参考） | Anthropic | 专有 | 82.9 |
| **DeepSeek V4.1 Flash-1017** | DeepSeek | open weights | **38.8** |
| **Kimi K3.1 Pro** | Moonshot AI | open weights | 38.7 |
| **MiMo-V2.6-Pro** | Xiaomi | open weights | 36.4 |
| **Kimi K3** | Moonshot AI | open weights | 36.0 |
| **MiniMax M3.1 Flash** | MiniMax | open weights | 25.7 |
| **Mistral Large 4** | Mistral AI | open weights | 24.7 |
| **GLM-5.3-Flash** | Z.ai | open weights | 20.7 |
| **Qwen3.8-27B** | Alibaba | open weights | 15.9 |
| **Muse Spark Open** | Meta | open weights | 12.1 |
| **Nemotron 3.5 Super VL** | NVIDIA | open weights | 12.0 |

这两张表讲述了不同的故事。在编程上，最好的 open-weight 模型比最好的专有模型落后约 10 分。在长周期 agentic 工作——也就是那种无人值守跑上数小时的工作——差距超过 40 分。实际解读是：open-weight 模型已经能承担大部分编程工作，包括 bug 修复、重构、编写测试和有监督的 agent 循环。对于完全自主的多小时任务，专有模型仍然值那个价，而常见做法是[在两者之间路由](https://deepinfra.com/blog/two-tier-agent-two-models)。

## 开源编程模型真的免费吗？

免费获得模型权重并不意味着零成本。你仍然需要 GPU、存储、网络、推理软件、监控、安全控制、升级和工程时间。大型 [mixture-of-experts 模型](https://deepinfra.com/blog/mixture-of-experts-llm-economics-price-drop) 每个 token 可能只激活一小部分参数，但服务系统仍然需要把完整的权重集放在内存里。

open weights 还附带许可证条款。MIT 和 Apache 2.0 授予广泛的使用、修改和再分发权利。这里 9 个模型中有 4 个使用带商业条件的定制许可证：Mistral Large 4、GLM-5.3、Kimi K3.1 Pro 和 MiniMax M3.1 Flash。

自托管通常在经济上划算的情形是：你用量稳定且很高、有严格的源代码隐私要求、已有 GPU 容量，或者工作负载可预测、能让硬件保持忙碌。当用量仍不确定，或者你想在投入基础设施之前先试几个模型时，托管的开源模型 API 往往更合适。

你可以用一个简单计算来比较两种方案：

- 托管月成本 = 输入 token 成本 + 输出 token 成本，减去缓存输入和 Flex 带来的节省
- 自托管月成本 = GPU 小时 + 存储 + 网络 + 监控 + 工程运维

## 开源编程模型在哪些场景价值最大？

开源编程模型在不同场景下提供了若干运营优势。

- **私有代码库：**当源代码、凭据、客户数据或内部文档不能离开你的环境时，你可以在受控基础设施里运行模型。
- **高用量 agentic 工作流：**自托管或低成本的 open-model API 能为反复的仓库分析、测试执行、调试和工具调用提供更可预测的成本。
- **模型定制：**你可以微调模型、调整 inference 设置、加入领域专用工具，或为内部框架和编程语言训练 adapter。
- **部署控制权：**你的团队可以锁定经过测试的模型版本、选择硬件、控制延迟，并决定何时应用升级。托管的 model ID 终究会被退役，所以无论走哪条路都要[为弃用做好规划](https://deepinfra.com/blog/model-deprecation-llm-apps)。
- **面向特定硬件的工作负载：**你可以根据可用的显存、吞吐目标、量化支持和预期上下文长度，选择 dense 或 MoE 架构。
- **降低供应商依赖：**open weights 让你更容易在托管 API、私有 endpoint 和自管基础设施之间迁移，而不必重建编程应用。

## 在本地或自托管运行开源编程模型

有多个 serving 框架支持开源编程模型：

- **vLLM** 专注于高吞吐的 GPU 服务和生产 API。
- **SGLang** 提供高效的结构化生成和面向 agent 的服务。我们的 [vLLM 与 SGLang 对比](https://deepinfra.com/blog/vllm-vs-sglang) 介绍了如何在这两者之间做选择。
- **llama.cpp** 在 CPU、消费级 GPU 和 Apple Silicon 上运行量化模型。
- **Ollama** 简化了本地模型的安装和 API 访问。
- **LM Studio** 提供桌面界面和一个本地 OpenAI 兼容服务端。

在本地运行模型时，要考虑它的规模、精度和 context window。本指南中有两个模型适合本地运行。Muse Glimmer 30B 提供量化构建，Meta 将其目标定在 24GB 和 32GB 显存。Qwen3.8-27B 是一个 27B 的 dense 模型，4-bit 构建仅权重就需要大约 14GB，加上运行时开销和上下文之后，24GB 显卡是一个实用的起点。

其余的模型都是数据中心级模型。另外七个（DeepSeek V4.1 Flash、Mistral Large 4、GLM-5.3、MiniMax M3.1 Flash、MiMo-V2.6-Pro、DeepSeek V4 Pro、Kimi K3.1 Pro）参数规模从 4280 亿到 2.8 万亿不等，需要多 GPU 服务器。

无论本地还是托管，这些模型都能接入任何接受 OpenAI 兼容 endpoint 的编程工具，包括 [OpenCode](https://deepinfra.com/blog/claude-code-alternative) 这样的开放 agents。

## 在 DeepInfra 上运行这些模型

如果你不想自己搭建服务层，最简便的方式是使用 DeepInfra 的 [OpenAI 兼容 API](https://docs.deepinfra.com/chat/overview)：请求格式和 client 与 OpenAI API 相同，通过名称选择模型。上面九个模型中有七个可用，按 token 计价，没有最低消费。

| 模型 | 输入（$/1M） | 输出（$/1M） | Flex 档位（0.8×） | 估算月成本* |
| --- | --- | --- | --- | --- |
| DeepSeek V4.1 Flash-1017 | $0.098 | $0.294 | 是 | $15.68 |
| Qwen3.8-27B | $0.15 | $1.875 | 是 | $52.50 |
| Muse Glimmer 30B | $0.30 | $1.20 | 否 | $54.00 |
| MiMo-V2.6-Pro | $0.387 | $0.783 | 否 | $54.36 |
| GLM-5.3 | $0.563 | $2.50 | 是 | $106.30 |
| DeepSeek V4 Pro-0813 | $1.30 | $2.60 | 是 | $182.00 |
| Kimi K3.1 Pro | $1.90 | $9.50 | 是 | $380.00 |

**估算基于每月 1 亿输入 token 和 2000 万输出 token、按标准档位计算，未计入缓存输入带来的节省。价格取自 2026 年 11 月 17 日 DeepInfra 的模型页面。DeepSeek V4.1 Flash-1017、Qwen3.8-27B、MiMo-V2.6-Pro、GLM-5.3 和 Kimi K3.1 Pro 为促销价；目录价见上文各模型章节。MiniMax M3.1 Flash 与 Mistral Large 4 未提供服务；更早的 MiniMax-M3 可提供，价格为 $0.28 和 $1.10。*

价差本身就是重点。同样的工作负载，用在 LiveBench coding 分数最高的模型上花 $15.68，用在最大的模型上花 $380，相差 24 倍。三种设置可以进一步压低账单：

- **Flex 档位。**带 Flex 标记的模型按标准价格的 0.8× 运行，代价是响应更慢、偶尔不可用。这适合批量重构、测试生成和过夜 agent 运行。上面 DeepSeek V4.1 Flash-1017 的估算会降到约 $12.54。
- **缓存输入。**编程 agents 每一步都会重发相同的 system prompt、工具定义和仓库上下文。这些重复的 token 按缓存输入费率计费：例如在 DeepSeek V4 Pro-0813 上，每百万 token 为 $0.10 而不是 $1.30。我们关于 [prompt hygiene](https://deepinfra.com/blog/prompt-hygiene-cheaper-faster-llm-calls) 的指南介绍了如何组织 prompt 以命中缓存。
- **推理强度。**这些模型中有几个接受 `reasoning_effort` 设置。GLM-5.3 默认为 `max`；对日常编辑降到 `high` 或 `low` 可以减少输出 token。

对于编程 agent 周围的大量辅助工作，比如读取构建日志或用截图初步研判 issue，[Nemotron 3.5 Super VL](https://deepinfra.com/nvidia/NVIDIA-Nemotron-3.5-Super-VL) 是一个低成本的多模态选项，每百万 token 输入 $0.15、输出 $0.50。它在 LiveBench 2.0 coding 中得分 54.1，所以适合用在简单步骤上。

如果响应速度本身就是产品，比如行内自动补全，也要测试建立在速度专用硬件上的提供商。对于 agents、批处理，以及任何按量计费的场景，按 token 的差价会不断累积。

下面是使用 Python client 调用其中一个模型的示例：

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

想试其他模型，改一下模型名即可。

## 结论

最佳的开源编程模型取决于具体工作。

对大多数团队来说，从 DeepSeek V4.1 Flash-1017 开始：它在 open-weight 模型中拥有最高的独立 coding 分数、MIT 许可证，以及本指南中最低的价格。如果你的 agents 要跑长时间、无人值守的任务，可以拿 Kimi K3.1 Pro 和 MiMo-V2.6-Pro 与它对比测试；这两者在长周期工作上得分接近，而 MiMo 是在 MIT 许可证下、以较低的输出价格做到的。若需要带安全视角的长周期编程，GLM-5.3 值得评估——前提是许可证允许。如果你需要能自己运行的小模型，想要分数就选 Qwen3.8-27B，想要开箱即用的本地构建就选 Muse Glimmer 30B。Mistral Large 4 在编程上与 DeepSeek 几乎持平，如果“欧洲打造的模型”对你重要，它就是选择——前提是你能用 Mistral 的 API 或自己托管一个万亿参数模型。

无论你把哪些列入候选，在最终决定前都要在你自己仓库上实测。厂商 benchmark 使用不同的 harness，而独立排行榜尚未覆盖这里的每一个模型。

访问 [DeepInfra 模型页面](https://deepinfra.com/models)，对比各开源模型的 context window 和定价。如有任何问题或反馈，请通过 [feedback@deepinfra.com](mailto:feedback@deepinfra.com) 联系我们。你也可以加入 [Discord](https://discord.gg/deepinfra) 社区，或在 X 上找到 [@DeepInfra](https://x.com/DeepInfra)。

相关文章

[![Kimi K2.5 最佳 API：为什么 DeepInfra 在速度、TTFT 和可扩展性上领先](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/02/Best-API-for-Kimi_sized.jpg)](https://deepinfra.com/blog/best-api-for-kimi-k2-5-deepinfra)[Kimi K2.5 最佳 API：为什么 DeepInfra 在速度、TTFT 和可扩展性上领先](https://deepinfra.com/blog/best-api-for-kimi-k2-5-deepinfra)<p>更新于 2026 年 11 月。Kimi K2.5 被定位为 Moonshot AI 面向现代产品工作流的“全能”模型：原生多模态（文本 + 视觉/视频）、Instant 与 Thinking 两种模式，并支持 agentic / multi-agent（“swarm”）执行模式。不过在实际应用中，模型能力只是一半的故事。提供方的推理栈决定了你的用户真正 [&hellip;]</p>

[![从搜索结果到证据：NVIDIA Nemotron 3.5 Embed 与 Rerank 登陆 DeepInfra](https://deepinfra.com/blog/nvidia-nemotron-3.5-embed-rerank-release.png)](https://deepinfra.com/blog/nvidia-nemotron-3.5-embed-rerank-release)[从搜索结果到证据：NVIDIA Nemotron 3.5 Embed 与 Rerank 登陆 DeepInfra](https://deepinfra.com/blog/nvidia-nemotron-3.5-embed-rerank-release)NVIDIA Nemotron 3.5 Embed 和 Rerank 自发布首日起就已在 DeepInfra 上提供。通过 DeepInfra API 调用 Embed 1B、Embed 8B 和 Rerank 8B，无需任何部署配置，按 token 计价。

[![推出 Prompt Cache Retention：让上下文保温 5 分钟或 1 小时](https://deepinfra.com/blog/prompt-cache-retention.jpg)](https://deepinfra.com/blog/prompt-cache-retention)[推出 Prompt Cache Retention：让上下文保温 5 分钟或 1 小时](https://deepinfra.com/blog/prompt-cache-retention)将 prompt 的 KV cache 保留 5 分钟或 1 小时——复用时跳过 prefill，从而更快返回首个 token，并按折扣后的缓存读取费率计费。请求里只需一个字段。

[查看全部](https://deepinfra.com/blog)
