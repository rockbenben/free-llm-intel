---
vendor: deepinfra
title: DeepSeek V4.1 Flash API：速度、延迟与成本
original_title: DeepSeek V4.1 Flash API: Speed, Latency & Cost
url: https://deepinfra.com/blog/deepseek-v4-1-flash-api-benchmarks
date: 2026-09-30
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# DeepSeek V4.1 Flash API：速度、延迟与成本

## **DeepSeek V4.1 Flash（Reasoning, Max Effort）API 评测摘要**

| 指标 | 数值 | 背景 |
| --- | --- | --- |
| 智能 | 40（Artificial Analysis Intelligence Index） | 远高于同规模开放权重模型中位数（18） |
| 速度 | 211.5–545.6 输出 tokens/秒 | 明显很快；中位数：68.9 t/s |
| 延迟（TTFT） | 1.19s–5.28s（因提供方而异） | 有竞争力；中位数：2.32s |
| 价格（DeepSeek API） | 峰值输入 $0.30/1M、输出 $1.20/1M | 缓存折扣：98% |
| 每个 Intelligence Index 任务的成本 | $0.27 | |
| 冗长度 | 评测期间输出 2.5 亿 token | 偏高；中位数：1.4 亿 |
| 上下文窗口 | 1M tokens | 约 1,500 页 A4 |
| 模态 | 文本 + 图像输入；文本输出 | |
| 开放权重 / 许可证 | 开放权重，MIT 许可证 | 允许商用 |
| 模型规模 | 总参数 552B，激活 8–16B（MoE） | |
| 发布 | 2026 年 9 月 10 日 | |
| 跑完 Intelligence Index 评测的总成本 | $476.89 | |

开放权重 AI 版图在 2026 年 9 月 10 日迎来新的里程碑：DeepSeek 发布了 V4.1 Flash——一款挑战"前沿级智能必须依赖专有基础设施"这一假设的模型。这家中国 AI 公司在 2025 年初凭其低成本推理模型一鸣惊人，如今又发布了 DeepSeek-V4.1 Flash，自称更聪明、更快、更高效。

多方的测试都显示 V4.1-Flash 在性能、成本、速度与总运行时间上领先 V4-Pro。DeepSeek 正在逐步下线 V4-Pro。本指南为开发者和企业架构师拆解需要了解的一切：从架构与基准分数，到 API 提供方对比与部署考量。

## **模型概览**

[DeepSeek-V4.1-Flash](https://deepinfra.com/deepseek-ai/DeepSeek-V4.1-Flash) 是一款多模态 Mixture-of-Experts（MoE）模型，骨干参数 552B，支持最高一百万 token 的上下文。模型原生处理图像与文本，并以自回归方式生成文本。

DeepSeek-V4.1-Flash 采用 Causal Encoder-Decoder（CED）架构：一个 40 层 Transformer，由 20 层因果编码器加 20 层解码器组成。这一架构创新让模型在处理输入时激活的参数少于生成输出时，大幅提升效率。

### **亮点**

- **前沿级智能，Flash 档定价：** DeepSeek V4.1 Flash（Reasoning, Max Effort）在智能维度属于领先模型之列，与同规模其他开放权重模型相比定价合理。
- **巨量上下文窗口：** 与前代相同的 [1M token 上下文](https://getdeploying.com/llms/deepseek-v4.1-flash)，可处理整个代码库或超长文档。
- **原生多模态支持：** 该模型是其新架构家族中最小的一员，而该家族现已[原生支持视觉理解](https://www.neowin.net/news/deepseek-launches-v41-flash-multimodal-reasoning-model/)。
- **MIT 许可的开放权重：** 允许完整商用。
- **卓越的效率：** DeepSeek-V4.1-Flash 相对 DeepSeek-V4-Flash 和 DeepSeek-V1 分别实现约 4 倍和 437 倍的 KV cache 体积缩减。

## **技术规格**

### **总参数**

它是一个采用全新 encoder-decoder 架构的 [552B 参数 MoE 模型](https://www.yottalabs.ai/post/deepseek-v4-1-flash-pricing-specs-v4-pro-routing-2026)。

### **激活参数**

DeepSeek-V4.1 Flash 采用 5,520 亿参数的 Mixture of Experts 设计，以低成本提供更多智能。它还使用了新的 Causal Encoder-Decoder 架构，这意味着该模型处理输入只激活 80 亿参数，生成输出激活 160 亿参数。

### **模型体积**

DeepSeek V4.1 Flash [在磁盘上占 510 GB](https://www.yottalabs.ai/post/deepseek-v4-1-flash-hardware-requirements-gpu-memory-2026)。checkpoint 共 510 GB，分为 48 个 shard。

DeepSeek V4 Flash 原本是 166.9 GB、两张 H200 就能跑；它的继任者体积是原来的三倍。

### **模型权重**

权重已按 MIT 许可发布在 [Hugging Face](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash) 上，公开可下载，开发者可以在自有硬件上托管、微调和部署该模型。

### **许可证**

权重采用 MIT 许可。这一宽松许可证允许商用、修改、分发与私有使用，不受限制。

### **输入模态**

模型原生处理图像与文本。这种多模态能力无需独立的视觉编码器即可完成视觉-语言任务。

### **输出模态**

输出模态严格为文本。模型基于文本和/或图像输入以自回归方式生成文本。

### **上下文窗口**

1M 上下文，约合 1,500 页 A4 或 750,000 个单词。可以在单个 prompt 中处理整个代码库、冗长法律文档或大量研究论文。

## **推理能力**

### **Reasoning**

DeepSeek-V4.1-Flash 支持从 1 到 100 连续可调的 reasoning effort。下文所有 instruct 结果均使用最大档位（reasoning_effort=100）。

这个连续的"推理旋钮"相比以往的离散模式（Non-think、Think High、Think Max）是显著进步，允许对计算-精度权衡进行细粒度控制。

### **智能**

DeepSeek V4.1 Flash（Reasoning, Max Effort）在 [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/models/deepseek-v4-1-flash) 上得分 40。这一综合基准从推理、知识、数学和编程四个维度评估模型。

### **Intelligence Index 对比**

DeepSeek V4.1 Flash（Reasoning, Max Effort）在 Artificial Analysis Intelligence Index 上得分 40，在可比模型中远高于平均水平（中位数：18）。

DeepSeek 还采用了新的预训练方法和更大规模的强化学习后训练，取得超越 Kimi-K3、GLM-5.3、Claude Opus 5、GPT 5.6-Sol 和 DeepSeek-V4-Pro 等旗舰模型的基准成绩。

### **能力指标**

| 基准 | 得分 |
| --- | --- |
| MMLU | 91% |
| MMLU-Pro | 81.2% |
| HLE（High-Level Expertise） | 36.8% |
| IFEval | 89.5% |
| SimpleQA | 49% |
| AIME 2025 | 87.5% |
| Deep SWE | 74.2% |

DeepSeek V4.1 Flash [在 MMLU 上得分 91%](https://automatio.ai/models/deepseek-v4-1-flash)，在 MMLU Pro 上得分 81.2%。

### **智能构成**

- **语言智能：** 英文与多语言任务掌握出色，指令遵循得分 89.5%。
- **数学智能：** 在 AIME 2025 竞赛级题目上取得 87.5%，表现强劲。
- **编程智能：** DeepSeek V4.1 Flash 在 Deep SWE 上得 74.2 分，与 [GPT-6 Astra、Gemini 3.8 Flash 和 Opus 5 处于同一区间](https://www.mindstudio.ai/blog/deepseek-v4-1-flash-benchmarks)。
- **视觉智能：** 面向视觉-语言任务的原生图像理解。

## **性能指标**

### **速度**

DeepSeek V4.1 Flash（Reasoning, Max Effort）以每秒 214 token 的输出速度表现明显很快。[各提供方速度差异很大](https://artificialanalysis.ai/models/deepseek-v4-1-flash/providers)：输出速度排名靠前的有 Inco (FAST)（545.6 t/s）、LithosAI（402.5 t/s）和 Databricks（338.2 t/s）。

### **延迟**

速度在各提供方之间差异显著，最快与最慢相差 344%。延迟方面，Inco (FAST)（5.28s）、LithosAI（6.00s）和 Databricks（7.17s）提供了最低的首个回答 token 时间。

### **端到端响应时间**

对标准工作负载，端到端响应时间通常在 5–15 秒之间，具体取决于提供方和 reasoning effort 设置。模型较高的输出速度（优质提供方 200+ t/s）意味着一旦开始生成，即使很长的回复也能很快完成。

### **Token 用量**

在评测 Intelligence Index 时，它生成了 2.5 亿 token，相比 1.4 亿的中位数非常啰嗦。

这种冗长度是成本规划时必须考虑的因素：该模型倾向于生成全面、详细的回复，消耗的输出 token 高于平均水平。

## **成本**

### **定价结构**

模型名为 deepseek-flash，非峰谷时段每百万输入 token $0.15、每百万输出 token $0.60，峰值时段价格翻倍，缓存命中为 $0.003。

| 定价档位 | 输入（每 1M tokens） | 输出（每 1M tokens） | 缓存命中 |
| --- | --- | --- | --- |
| 非峰值 | $0.15 | $0.60 | $0.003 |
| 峰值 | $0.30 | $1.20 | $0.006 |

[峰值时段为 UTC 时间 01:00–04:00 与 06:00–10:00](https://techjacksolutions.com/ai-tools/deepseek/deepseek-v4-1-flash/)，周一至周五；其余时段均为非峰值，按峰值费率的一半计费。

### **缓存经济学**

缓存命中折扣极高，按 token 计约为未命中费率的 98% 折扣（峰值时 $0.006 对 $0.30）。

在大量请求间复用的 system prompt 或 tool schema，成本只占同等长度全新 prompt 的一小部分——这对每一步都重发相同脚手架的智能体工作流尤为重要。

### **成本对比**

DeepSeek V4.1 Flash（Reasoning, Max Effort）定价为输入每 1M token $0.30（属于中等价位，中位数：$0.30），输出每 1M token $1.20（略偏贵，中位数：$1.15）。

总计，让 DeepSeek V4.1 Flash（Reasoning, Max Effort）跑完 Intelligence Index 评测花费了 $476.89。

### **开放性**

[于 2026 年 4 月 24 日以 MIT 许可证开源发布](https://apxml.com/models/deepseek-v4-1-flash)。

DeepSeek V4.1 Flash 代表了开放权重 AI 的高水位。MIT 许可证对商用、修改和再分发不设任何限制。开发者可完全获取：

- 模型权重（510 GB checkpoint）
- 架构文档
- 训练方法论细节
- 评测脚本与基准

这种开放性让企业可以本地部署、面向特定领域微调，并放心集成而不必担心供应商锁定。

## **API 提供方**

### **可用提供方**

DeepSeek V4.1 Flash 在 [OpenRouter 上有 19 个提供方](https://openrouter.ai/deepseek/deepseek-v4.1-flash)：Alibaba Cloud Int.、Relace、DeepSeek、Morph、DeepInfra、Fireworks、GMICloud、AtlasCloud 以及另外 11 家。

DeepSeek V4.1 Flash（Reasoning, Max Effort）可通过 8 个 API 提供方获取：DeepSeek、Novita、Fireworks、Parasail、Baseten、Databricks、Inco (FAST) 和 LithosAI。

### **API 提供方基准**

| 提供方 | 输出速度 | TTFT | 混合价格（每 1M） |
| --- | --- | --- | --- |
| Inco (FAST) | 545.6 t/s | 5.28s | N/A |
| LithosAI | 402.5 t/s | 6.00s | $0.09 |
| Databricks | 338.2 t/s | 7.17s | $0.08 |
| Fireworks | ~250 t/s | N/A | $0.11 |
| DeepSeek | 211.5 t/s | 1.19s | $0.06–0.30 |

Inco (FAST) 性能最佳，同时拥有最高速度与最低延迟。

价格方面，Databricks（$0.08）、LithosAI（$0.09）和 Fireworks（$0.11）提供每 1M token 最低的混合价格。各提供方价格差距最高达 4.9 倍。

### **提供方对比表**

| 特性 | DeepSeek（一方） | DeepInfra | Fireworks | Databricks |
| --- | --- | --- | --- | --- |
| 输出速度 | 211.5 t/s | 高 | ~250 t/s | 338.2 t/s |
| TTFT | 1.19s | ~1.11s | N/A | 7.17s |
| 输入成本 | $0.30（峰值） | 有竞争力 | $0.11 混合 | $0.08 混合 |
| 输出成本 | $1.20（峰值） | 有竞争力 | N/A | N/A |
| 缓存折扣 | 98% | 视情况 | N/A | N/A |
| 1M 上下文 | ✓ | ✓ | ✓ | ✓ |
| 图像输入 | ✓ | ✓ | ✓ | ✓ |

对多数生产规模部署而言，DeepInfra 提供了最强的综合组合：低延迟、[两个 V4 变体上均有竞争力的定价](https://deepinfra.com/blog/best-api-providers-for-deepseek-v4)，以及功能完整的 OpenAI 兼容 API。

## **自托管要求**

### **硬件要求**

DeepSeek V4.1 Flash 大约需要 614 GB GPU 显存。

DeepSeek V4.1 Flash 是第一个需要整整一台节点的 Flash 模型。

vLLM、SGLang 和 NVIDIA 的 day-one 服务方案全部从四张 Blackwell 级 GPU 或八张 H200 起步。

### **量化选项**

DeepSeek V4.1 Flash 在 4-bit 量化、32K 上下文下约需 306 GB GPU 显存。

能装下的最便宜租用方案是 8× RTX A6000，约每月 $3,168。这与在 DeepSeek API 上每月消耗约 70 亿 token 的费用相当。低于这个量级，自托管反而更贵。

### **软件支持**

vLLM 0.30.0 及以上，NVIDIA 侧使用打了 deepseekv41-flash-0909 标签的镜像，AMD 侧使用 ROCm nightly。SGLang 的 day-zero 构建已支持，并能从 checkpoint 自动选择 attention 与 MoE 后端。

## **总体建议**

对于追求前沿级智能、又不愿被专有锁定绑住的团队，DeepSeek V4.1 Flash 提供了出色的价值主张。DeepSeek 的宣称是 V4.1 Flash 在"性能、成本、速度和任务完成时间"上全面击败 V4 Pro。

**最适合：**

- 长上下文的智能体与编程工作负载
- 需要处理海量文档的 RAG 流水线
- 图像与文本混合的多模态应用
- token 量大但成本敏感的部署
- 善用缓存折扣的智能体工作流

**如有以下需求请考虑其他方案：**

- 需要消费级硬件的自托管选项
- 用例要求极简的回复长度
- 需要基准与生产表现严格一致（一些实测显示存在差距）

DeepSeek V4.1 Flash 纸面上与 Opus 5 和 GPT-5.6 相当，但实测编程任务暴露出基准分数与真实输出之间的差距。请针对你的具体用例充分评估。

API 访问方面，DeepInfra（deepinfra.com）在性能、定价与开发者体验之间提供了出色平衡——考虑到该模型的冗长输出，这一点尤为重要：提供方层面吞吐与缓存经济学的差异会实质性影响总成本。

## **结论**

DeepSeek V4.1 Flash 是开放权重 AI 发展的重要里程碑。DeepSeek 表示，该模型为更强的能力、更快的推理、更高的吞吐以及向更大规模模型扩展而设计。

凭借 552B 总参数、8–16B 激活参数、1M token 上下文窗口、原生多模态支持与 MIT 许可，它以专有模型成本的一小部分交付前沿级能力。98% 的缓存折扣让它在智能体工作流中格外有吸引力。

V4.1-Flash 让 DeepSeek 能以更低成本服务更多用户，并且他们[把节省让利给用户](https://deepseek.com/en/news/deepseek-v4-1-flash/)。

无论你是在构建生产级 AI 应用、开展研究，还是探索语言模型能力的前沿，DeepSeek V4.1 Flash 都值得认真考虑——可通过 DeepInfra 及众多其他提供方访问，也可依据宽松的 MIT 许可自行托管。

## **常见问题**

### **我能在消费级硬件上运行 DeepSeek V4.1 Flash 吗？**

不能。DeepSeek V4.1 Flash 磁盘占用 510 GB，约需 614 GB GPU 显存。即使量化，你也需要企业级 GPU 基础设施。

### **DeepSeek V4.1 Flash 支持图像输入吗？**

支持。模型原生处理图像与文本。

### **商用免费吗？**

是的。权重采用 MIT 许可。

### **DeepSeek V4 Pro 怎么样了？**

自 2026 年 9 月 14 日 UTC 04:00 起，所有 deepseek-v4-pro 请求都将按 V4.1-Flash 的费率路由到 V4.1-Flash。

### **reasoning effort 旋钮如何工作？**

模型支持连续可调的 reasoning effort 设置（整数 1–100），在推理成本与准确率之间做权衡。

### **为什么模型这么啰嗦？**

它速度很快，但确实非常啰嗦。模型倾向于提供全面、详细的回复。做预算时请按更高的输出 token 消耗来规划。
