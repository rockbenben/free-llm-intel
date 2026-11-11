---
vendor: huggingface
title: BotPsy：基于十亿参数以下 agentic 语言模型的端侧个人助理
original_title: 
url: https://huggingface.co/blog/qvac/botpsy
date: 2026-11-11
lang: zh
captured: 2026-11-11
extractor: readability-v1
translator: agent
status: translated
body_sha: 34d5b5445b70
---

[ 返回文章](https://huggingface.co/blog)

# BotPsy：基于十亿参数以下 agentic 语言模型的端侧个人助理

团队文章

发布于 November 11, 2026


2

- [![](https://huggingface.co/avatars/0532faec32a12d143b5329642a709b0f.svg)](https://huggingface.co/joooon)
- [![](https://huggingface.co/avatars/30ff51594b6454a1eced9a0d472d2ec1.svg)](https://huggingface.co/milangritta)

[![Milan Gritta 的头像](https://huggingface.co/avatars/30ff51594b6454a1eced9a0d472d2ec1.svg)](https://huggingface.co/milangritta)

Milan Gritta

milangritta

[![QVAC 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)](https://huggingface.co/qvac) [qvac](https://huggingface.co/qvac)

[![Jihye Back 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/61a623353aff6ad7c083e882/biFOfePqURZW0snJHfy_Y.jpeg)](https://huggingface.co/happy-jihye)

Jihye Back

happy-jihye

[![QVAC 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)](https://huggingface.co/qvac) [qvac](https://huggingface.co/qvac)

[![JinUk, Cho 的头像](https://huggingface.co/avatars/1299f5cd3558e75571711d544f4a6d29.svg)](https://huggingface.co/jucho2725)

JinUk, Cho

jucho2725

[![QVAC 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)](https://huggingface.co/qvac) [qvac](https://huggingface.co/qvac)

[![ohjoon kwon 的头像](https://huggingface.co/avatars/0532faec32a12d143b5329642a709b0f.svg)](https://huggingface.co/joooon)

ohjoon kwon

joooon

[![QVAC 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)](https://huggingface.co/qvac) [qvac](https://huggingface.co/qvac)

[![Patrik Lambert 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/Pmar3VJzQzgT4gdO8dpwt.png)](https://huggingface.co/patrik-lambert)

Patrik Lambert

patrik-lambert

[![QVAC 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)](https://huggingface.co/qvac) [qvac](https://huggingface.co/qvac)

[![Mathias Buus 的头像](https://huggingface.co/avatars/04b3527ef6ff1d6feebcad80e5c0e5c6.svg)](https://huggingface.co/mafintosh)

Mathias Buus

mafintosh

[![QVAC 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)](https://huggingface.co/qvac) [qvac](https://huggingface.co/qvac)

[![Amril Nurman 的头像](https://huggingface.co/avatars/321662b676eb3141ce8410614e581e2c.svg)](https://huggingface.co/Nurman)

Amril Nurman

Nurman

[![QVAC 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)](https://huggingface.co/qvac) [qvac](https://huggingface.co/qvac)

前沿云端 LLM 的运营成本很高，且可能意外波动；依赖这类第三方模型还会带来隐患，因为提供方随时可能修改、拒绝或停用访问权限。此外，专有模型对特定工作流的定制空间有限，同时给隐私、数据掌控和透明度带来风险。再说，并非每项任务都需要前沿级别的智能：小型专用 agent 在特定任务上同样能胜任，运行成本却低得多，因为许多常规或较小的负载都能在端侧高效处理。随着单位参数的智能水平持续快速提升，我们希望站在这一转向的前沿——迈向高性能、注重隐私、可自托管的模型。

Tether AI Research 推出 **BotPsy**，这是一个 0.8B 参数模型 介绍 **BotPsy**，这是一个专为函数调用和 agentic 工作流设计的 0.8B 参数模型，构建于 Qwen3.5-0.8B 之上，适合端侧部署。 BotPsy 是一款“个人助理”，它使用工具为用户执行各种简单的任务，涉及的领域包括网页搜索与研究、旅行与生活方式、商业与金融、企业与客户运营、设备与车辆控制、文件与文档、日历，以及邮件与消息。由于其参数量小，它最适合低到中等难度的任务。 BotPsy 在其规模内实现了最先进（SOTA）的工具使用和 agentic 性能，优于我们测试过的所有参数量不超过 1.2B 的模型（图 1 和图 2）。它专为安全的端侧工作流设计，在保持用户数据私密的同时，提供出色的指令遵循可靠性与效率。作为小模型，BotPsy 仍会出错，不适合高风险场景；更多信息请阅读[预期用途与限制](https://huggingface.co/blog/qvac/botpsy#intended-use-and-limitations)。

🤗 [模型（safetensors）](https://huggingface.co/qvac/BotPsy-0.8B) | 📦 [GGUF（bf16、Q8、Q4）](https://huggingface.co/qvac/BotPsy-0.8B-GGUFs)

**图 1：** BotPsy-0.8B 显著优于其基础模型，在六项工具使用与 agentic 基准中有五项领先，包括领先于 Qwen3.5-2B-Think（规模为其 2.5 倍）；只有在 Claw-Eval 上 Qwen3.5-2B-Think 略胜一筹。

**图 2：** *知识：* 与规模相近的模型相比，工具使用训练保留并提升了 BotPsy 的通用知识，不过整体知识水平仍主要取决于参数量。*指令遵循：* BotPsy 擅长遵循显式指令和多轮任务，但表现会随指令累积而下降，在资源较少的语言上也相对落后。

### 版权投诉

对于版权侵权通知，我们会采取适当措施。如果您认为自己的作品被以侵犯知识产权的方式使用或复制，请发送邮件至 [data-apps@tether.io](mailto:data-apps@tether.io)，注明并描述受版权保护的作品及涉嫌侵权的内容，以提交侵权通知。

## 主要亮点

### 基准测试结果

- **基础模型性能翻倍：** 在关键基准上，BotPsy 把 Qwen3.5-0.8B-Think 的 agentic 能力大致提升了一倍：BFCL v4 从 23.4 升至 44.0，ACEBench 从 30.1 升至 58.7，τ-bench 从 23.2 升至 51.5（零售、电信和银行子集的平均值）。
- **同级别最佳 agent：** 在 ≤1.2B 参数这一量级中，BotPsy 在全部六项工具使用与 agentic 基准上均优于领先模型（Qwen3.5-0.8B-Think、LFM2.5-1.2B-Think、MiniCPM5-1B-Think）：BFCL v4、ACEBench、τ-bench、ToolSandbox、Claw-Eval 和 BrowseComp-Plus。
- **超越更大的同类模型：** 在六项基准中的五项上，BotPsy 在所有受测模型中得分最高，在 BFCL v4（44.0 对 37.7）、ACEBench（58.7 对 55.4）、τ-bench（51.5 对 46.5）、ToolSandbox（64.6 对 41.2）和 BrowseComp-Plus（4.5 对 2.8）上击败了规模为其 2.5 倍的 Qwen3.5-2B-Think。只有在 Claw-Eval 上 Qwen3.5-2B-Think 领先（48.9 对 46.5）。

### 模型能力

- **多轮工作流中更可靠：** 在 τ²-bench 上，agent 必须与客户进行长时间对话、遵循严格的策略并代表客户行事，它在电信场景得 82.5 分，领先于 Qwen3.5-2B-Think（69.3）。在 BFCL v4 的多轮任务上，它相对基础模型从 7.5 升至 46.1，接近 Qwen3.5-2B-Think（23.8）的两倍。按应用分组，其多步得分在商业与服务（58.3 对 47.4，次优为 Qwen3.5-2B-Think）以及设备与系统管理（46.1 对 31.9）上领先所有受测模型。
- **知道何时（不）调用工具：** 会行动的 agent 也必须知道何时不行动。BFCL v4 的幻觉测试检查模型在没有合适工具时是否会拒绝作答，BotPsy 在此得 86.1 分，为所有受测模型中最高。ACEBench 的特殊情况指请求不完整、包含错误参数，或给定工具无法满足请求，BotPsy 在此得 51.3 分，高于其基础模型的 13.7。
- **遵循指令同时保留知识：** BotPsy 专攻工具使用，同时保留通用能力。指令遵循显著提升，IFEval 从 59.7 升至 90.8，IFBench 从 22.0 升至 55.9，后者为所有受测模型中的最高 IFBench 得分。通用知识同样提升，GPQA Diamond 从 33.2 升至 38.1，MMLU-Pro 从 41.6 升至 48.9。在这四项基准上，BotPsy 均优于我们测试过的所有其他参数量 1.2B 及以下的模型。

### 安全、效率与部署

- **比同级别领先模型更安全：** 在覆盖六类危害的自动化红队测试中，BotPsy 有 21% 的时候给出不安全回答，其基础模型为 36%。这是所有参数量不超过 1.2B 的模型中最低的比例（LFM2.5-1.2B-Think：35%；MiniCPM5-1B-Think：47%）。在 prompt 注入攻击下（这对读取不可信工具输出的 agent 最为关键），不安全率从基础模型的 46% 降至 31%。
- **推理更高效、更少兜圈：** 在五个模型都答对的问题上，BotPsy 在 GPQA Diamond 上得出答案所用的推理 token 比基础模型少约 3 倍（3,690 对 11,563），在 MMLU-Pro 上少 2.7 倍（1,912 对 5,105）。在所有 IFBench 尝试中，陷入重复推理循环的比例从 22.9% 降至 1.4%，触及 32k token 上限的运行从 28.3% 降至 0.2%。更短、更果断的推理应当能降低端侧延迟。
- **开源且开箱即用：** BotPsy 将以开放权重形式发布，采用 Apache 2.0 许可，供研究和教育用途使用。它将提供三种精度（bf16、Q8、Q4），既有 Hugging Face safetensors 格式，也有供 QVAC SDK 和 llama.cpp 使用的 GGUF 文件。

## 更长远的愿景

在 BotPsy 的基础上，Tether Data, S.A. de C.V.（“Tether AI Research”、“我们”、“我们的”）后续的开发将着力扩展端侧 agentic 能力，使其与更广泛的硬件和本地服务无缝集成。Tether 的 Hypersearch 将演进为支持更稳健的去中心化点对点（P2P）查询，进一步保障私密、加密、绕开企业追踪器的网页搜索。QVAC Fabric 的本地 fine-tuning 机制将得到优化，以更深入地适配个体用户的偏好、工作流和专用工具环境。未来的迭代将让智能手机界面在离线与在线切换期间，把繁重的计算任务顺畅地委托给家用 PC 或可信的安全 P2P 节点。隐私协议会持续加强，以保证所有个人数据、凭据和决策都严格留在本地硬件上。我们还将引入协作功能，在可信的本地网络中实现安全的 agent 间通信，同时不损害用户机密性。最终，这些进展将把 BotPsy 夯实为一个完全自主、能力强大的个人 AI 生态，让用户完全掌控自己的数字生活。

## 方法论

BotPsy 基于 Qwen3.5-0.8B，经四个连续阶段进行后训练：监督微调（SFT）、多教师同策略蒸馏（MOPD）以及两轮强化学习（RL）。每个阶段都以前一阶段的最佳检查点为起点，并从不同的学习信号中获益：对参考轨迹的模仿、规模大得多的教师模型的 token 分布，以及基于规则的工具调用奖励（见图 3）。

**图 3：** BotPsy 的训练配方。学生模型历经四个阶段。三位 Qwen3.5-4B 专业教师模型各自针对一项技能做过 RL 训练，在蒸馏阶段提供指导。

### 训练流程：四个阶段、三类反馈

我们的方法采用四个训练阶段，从三类信号中学习：演示、专业教师和可验证的奖励。

**从演示中学习（SFT）**

我们首先在工具使用对话上做全参数监督微调。这些对话包括来自模拟环境的多轮 agent 轨迹、重放的单次、并行和多步调用，以及不应调用工具的情形。

**向教师学习（MOPD）**

接下来，用同策略蒸馏（OPD）训练学生模型：它自己生成回答，由专业教师对每个 token 给出反馈，以逐 token 的反向 KL 散度作为训练信号。为构建这些教师，我们先用 RL 训练了三个 Qwen3.5-4B 模型，分别专攻工具使用、通用推理和指令遵循。训练时，每个 prompt 会被路由到其中一位教师。这一阶段主要为了恢复在 SFT 阶段有所退化的知识与指令遵循能力，不过工具使用指标也会提升（见图 4）。

**图 4：** 每个训练阶段后各能力组的平均分。SFT 提升了工具使用，却把知识和指令遵循压到基础模型之下；蒸馏让两者回到基础模型之上，RL 阶段又在三者上带来进一步增益。

**从规则与环境中学习（RL 阶段）**

最后，用 DAPO [1] 对模型做强化学习训练，只从规则和验证器计算出的奖励中学习。第一轮聚焦工具调用，并辅以指令遵循和 STEM 选择题。与 Tool-N1 [2] 一样，工具调用奖励先检查推理和工具调用格式。不过它不用 Tool-N1 的二元正确性奖励，而是沿用 ToolRL [3] 的思路给出细粒度的部分得分，把预测的工具名、参数名和参数值与真值逐一比对。

第二轮把训练组合扩展到通用领域的可验证任务：数学、代码、知识（选择题）题、指令遵循、结构化输出，以及在模拟工作场所环境中的多步工具使用。尽管这个组合不含多轮对话，它仍进一步改善了多轮函数调用。

### 数据构成

每个训练阶段使用不同的数据配比（图 5）。SFT 阶段主要聚焦工具使用，为后续阶段打基础。MOPD 的配比混合了工具使用、知识和指令遵循数据，既为进一步提升函数调用，也为弥补 SFT 阶段在通用领域上的退化。第一轮 RL 同样主要聚焦工具使用，第二轮 RL 则把重心转向通用领域数据（指令遵循、知识、数学和代码），只保留较小比例的工具使用数据。

**图 5：** 各阶段训练数据的大致构成，按能力分组。

## 结果

### 工具使用与 agent

BotPsy 把 Qwen3.5-0.8B 基础模型的工具使用性能大致提升了一倍，并在六项 agentic 基准中的五项上为五个模型里最强：BFCL v4（44.0 对 23.4）、ACEBench（58.7 对 30.1）、τ-bench（51.5 对 23.2）、BrowseComp-Plus（4.5 对 1.9）和 ToolSandbox（64.6 对 30.5）。这五项上它也领先于规模为其 2.5 倍的 Qwen3.5-2B-Think（分别为 37.7、55.4、46.5、2.8 和 41.2；见表 1）。在 Claw-Eval 上，Qwen3.5-2B-Think 领先（48.9 对 46.5）。

| 基准 | **BotPsy-0.8B** 我们的 | Qwen3.5-0.8B-Think 基础模型 · 1× | Qwen3.5-2B-Think 2.5× | LFM2.5-1.2B-Think 1.5× | MiniCPM5-1B-Think 1.25× |
| --- | --- | --- | --- | --- | --- |
| BFCL v4¹ | **44.0** | 23.4 | 37.7 | 28.1 | 22.8 |
| ACEBench² | **58.7** | 30.1 | 55.4 | 39.4 | 24.5 |
| τ-bench³ | **51.5** | 23.2 | 46.5 | 6.5 | 28.8 |
| Claw-Eval⁴ | 46.5 | 39.3 | **48.9** | 31.6 | 31.0 |
| BrowseComp-Plus⁵ | **4.5** | 1.9 | 2.8 | 0.2 | 0.8 |
| ToolSandbox⁶ | **64.6** | 30.5 | 41.2 | 45.7 | 28.1 |
| *平均* | ***45.0*** | *24.7* | *38.8* | *25.3* | *22.7* |

**表 1：** 工具使用与 agentic 基准（0–100，越高越好）。每行最佳得分以**粗体**标出，次佳加下划线；倍数为相对 BotPsy-0.8B 的参数量。平均值为六项基准的未加权平均。评估设置的细节见[评估脚注](https://huggingface.co/blog/qvac/botpsy#evaluation-footnotes)。

### 知识

工具使用训练并未牺牲通用知识：GPQA Diamond 从 33.2 升至 38.1，MMLU-Pro 从 41.6 升至 48.9，是参数量 1.2B 及以下模型中最好的（LFM2.5-1.2B-Think：35.0 和 39.4；MiniCPM5-1B-Think：15.8 和 40.0）。知识水平仍主要取决于参数量，Qwen3.5-2B-Think 的得分明显更高（59.9 和 65.5）。因此，BotPsy 的设计定位是：对自己不知道的事实去调用工具，而不是充当知识模型。

| 基准 | **BotPsy-0.8B** 我们的 | Qwen3.5-0.8B-Think 基础模型 · 1× | Qwen3.5-2B-Think 2.5× | LFM2.5-1.2B-Think 1.5× | MiniCPM5-1B-Think 1.25× |
| --- | --- | --- | --- | --- | --- |
| GPQA Diamond⁷ | 38.1 | 33.2 | **59.9** | 35.0 | 15.8 |
| MMLU-Pro⁸ | 48.9 | 41.6 | **65.5** | 39.4 | 40.0 |

**表 2：** 通用知识基准（0–100，越高越好）。每行最佳得分以**粗体**标出，次佳加下划线。评估设置的细节见[评估脚注](https://huggingface.co/blog/qvac/botpsy#evaluation-footnotes)。

### 指令遵循

在遵循显式指令方面，BotPsy 是五个模型中最好的：IFEval 90.8（基础模型 59.7；Qwen3.5-2B-Think 80.0），IFBench 55.9（基础模型 22.0；Qwen3.5-2B-Think 40.9）。Multi-IF 考察八种语言、三轮对话中的指令遵循，BotPsy 得 67.2，与 Qwen3.5-2B-Think（66.9）和 LFM2.5-1.2B-Think（68.2）持平。它起步最强（第 1 轮 84.3，五个模型中最高），但随指令累积下降更快（第 3 轮 51.0，那两个模型分别为 56.5 和 56.2）。资源较少的语言仍是弱项：印地语（24.5）和俄语（57.6）远低于英语、中文、法语、西班牙语、意大利语和葡萄牙语达到的 72–80。

| 基准 | **BotPsy-0.8B** 我们的 | Qwen3.5-0.8B-Think 基础模型 · 1× | Qwen3.5-2B-Think 2.5× | LFM2.5-1.2B-Think 1.5× | MiniCPM5-1B-Think 1.25× |
| --- | --- | --- | --- | --- | --- |
| IFEval⁹ | **90.8** | 59.7 | 80.0 | 85.6 | 78.4 |
| IFBench⁹ | **55.9** | 22.0 | 40.9 | 33.9 | 40.6 |
| Multi-IF¹⁰ | 67.2 | 43.2 | 66.9 | **68.2** | 53.4 |

**表 3：** 指令遵循基准（0–100，越高越好）。每行最佳得分以**粗体**标出，次佳加下划线。评估设置的细节见[评估脚注](https://huggingface.co/blog/qvac/botpsy#evaluation-footnotes)。

### 多轮对话

最大的相对增益出现在多轮、有状态的交互中，BotPsy 在五项多轮基准里领先四项（图 6）。在 BFCL v4 多轮上，它从 7.5 升至 46.1，接近 Qwen3.5-2B-Think（23.8）的两倍；在 ACEBench Agent 上从 7.9 升至 28.3（Qwen3.5-2B-Think：16.2）。在 τ²-bench 上，它在零售场景把基础模型的得分翻倍（67.8 对 33.9，以微弱优势领先于 Qwen3.5-2B-Think 的 65.5），在电信场景达到 82.5——该场景中 agent 要在多轮里引导用户完成故障排查（MiniCPM5-1B-Think：74.0；Qwen3.5-2B-Think：69.3）。在单次调用（BFCL non-live：83.0）以及没有合适工具时不调用工具（BFCL hallucination：86.1）这两方面，它也是五个模型中最可靠的。

**图 6：** 多轮 agentic 任务：BFCL v4 多轮、ACEBench Agent、τ²-bench（零售、电信）和 τ³-bench（银行）。BotPsy 在五项基准中领先四项；在 τ³-banking 上，所有模型都低于 5。

### 薄弱之处

BotPsy 的弱项是开放式搜索，以及 Qwen3.5-2B-Think 仍然领先的少数几个方面。BotPsy 的 BrowseComp-Plus 得分 4.5 是五个模型中最好的，但绝对值偏低；在 BFCL 网页搜索（14.0）和记忆（16.3）上，它落后于 Qwen3.5-2B-Think（19.8 和 26.1）。在 Claw-Eval 上，BotPsy 相比基础模型有明显提升（46.5 对 39.3），但仍略低于 Qwen3.5-2B-Think（48.9）。在 ACEBench 的特殊情况（不完整或错误的请求）上，Qwen3.5-2B-Think 同样领先（58.0 对 51.3），不过 BotPsy 在此远高于其基础模型（13.7）。τ³-banking 是 BotPsy 唯一不领先的多轮基准：没有模型超过 5（BotPsy 4.1，与基础模型持平；Qwen3.5-2B-Think 4.8）。

## 适用场景：应用级性能拆解

BotPsy 能应对多种用例和场景。图 7 按应用组拆解基准场景，把简单场景（单轮、一次工具调用）与复杂场景（多轮或多工具）分开。本节引用的总分是对所有场景取平均；图 7 最下面一行是七个组的未加权平均，因此数值有所不同。

### 单次工具调用在各处都表现良好

在样本量有意义的每个应用组里，简单场景得分都在 70–79（Communication & Social 只有 6 个）。总体上 BotPsy 得 75 分，比基础模型（54）高约 21 分，也略高于 Qwen3.5-2B-Think（70）。

**图 7：** 按应用组划分的每个场景平均得分（0–100，越高越好），左侧为简单场景、右侧为复杂场景。n 表示每组中简单 / 复杂场景的数量；最下面一行是七个组的未加权平均。

### 增益最大的是多步任务

在复杂场景上，BotPsy 总体得 39.5 分，其基础模型为 17.9，Qwen3.5-2B-Think 为 30.8。增益最大的是 Communication & Social（61 对基础模型的 13）、Commerce & Services（58 对 27）和 Device & System Management（46 对 15）。Qwen3.5-2B-Think 只在 Personal Productivity & Work 上领先（64 对 58，38 个场景，多数来自 Claw-Eval），MiniCPM5-1B-Think 在 Communication & Social 上略领先（61.5 对 60.5）。多步任务的得分仍低于单次调用，这仍是应对更难任务时的主要限制。

### 多步信息检索是弱项

复杂的 Information Retrieval & Research 场景得 15 分（单次调用：79）。其中多数是 BrowseComp-Plus 的深度研究题，对该规模区间的每个模型都很难（基础模型：9；Qwen3.5-2B-Think：14）。

## 推理效率

BotPsy 得出正确答案所需的推理远少于其基础模型，在多轮 agent 任务上所需的轮数也更少。这与我们在整个训练过程中对推理效率的明确侧重一致。下面的所有比较都基于相同的问题或任务（五个模型都答对或解决过的那些），因此难度差异不会左右这些数字。推理 token 用各模型自己的 tokenizer 计数。

**图 8：** GPQA Diamond、MMLU-Pro、IFEval 和 IFBench 上每个正确答案的准确率与推理 token 的关系。token 在五个模型都答对的问题上统计；准确率为所有问题上的结果。越靠左上越好；虚线是 Pareto 前沿。

**推理更短，准确率更高。** 与基础模型相比，BotPsy 在 GPQA Diamond（3,690 对 11,563）、MMLU-Pro（1,912 对 5,105）、IFEval（3,148 对 4,433）和 IFBench（4,204 对 11,576）上，每个正确答案所用的推理 token 少了 1.4–3.1 倍，同时在四项上得分都更高（图 8）。它并非在所有地方都是推理最短的模型：LFM2.5-1.2B-Think 在 MMLU-Pro、IFEval 和 IFBench 上写出的推理更短，MiniCPM5-1B-Think 在 IFEval 和 IFBench 上也是如此，但两者在各项上的准确率都低于 BotPsy。

**图 9：** τ²-bench 零售与电信场景上每个已解决任务的通过率与 assistant 轮数的关系。轮数在五个模型都解决的任务上统计；通过率为所有任务上的结果。越靠左上越好；虚线是 Pareto 前沿。

**多轮 agent 任务所需轮数少于基础模型。** 在五个模型都解决的 τ²-bench 任务上，BotPsy 所需的 assistant 轮数少于其基础模型（图 9）：

- τ²-retail：10.7 轮，基础模型为 11.7 轮（少 9%），Qwen3.5-2B-Think 为 10.6 轮。
- τ²-telecom：13.1 轮，基础模型为 17.6 轮（少 26%），Qwen3.5-2B-Think 为 13.8 轮（少 5%）。

与此同时，它通过的任务数是基础模型的 2.0 倍（零售）和 2.6 倍（电信）。MiniCPM5-1B-Think 在零售上用的轮数更少（8.7），但只通过了 9.9% 的零售任务。

## 预期用途与限制

BotPsy 的开发旨在推进技术前沿，并支持研究与教育用途。基于我们工作开发的模型可能适用于以下领域的任务：设备与系统管理（设置、文件与文档、时钟与闹钟）、个人生产力与工作（日历与任务、邮件、协作工具）、通信（消息）、信息检索与研究（网页搜索、天气、新闻）、媒体与生活方式（视频、音乐、食谱与健身、照片），以及商业与服务（地图与旅行、金融、购物与配送）。由于参数量小，它**最适合低到中等难度的任务**。

BotPsy 主要用英语训练和测试，这也是推荐使用的语言。它还在 Multi-IF 上做过评估，该基准覆盖另外七种语言（中文、法语、印地语、意大利语、葡萄牙语、俄语和西班牙语）：在大多数语言上表现良好，但在印地语和俄语上得分低得多。BotPsy 是一个小型语言模型，会出错。它不适用于安全攸关或高风险的自动化决策，也不适用于涉及金钱、个人信息、健康及其他敏感主题的应用。

## 引用

```
@misc{botpsy2026,
  title  = {BotPsy: On-Device Personal Assistant with a Sub-Billion-Parameter Agentic Language Model},
  author = {{Tether Data, S.A. de C.V. d.b.a. Tether AI Research}},
  year   = {2026},
  note   = {Hugging Face blog}
}
```

## 参考文献

[1] Yu, Qiying, et al. "DAPO: An Open-Source LLM Reinforcement Learning System at Scale." *Advances in Neural Information Processing Systems* 38 (2025): 113222–113244.

[2] Zhang, Shaokun, et al. "Nemotron-Research-Tool-N1: Exploring Tool-Using Language Models with Reinforced Reasoning." *International Conference on Learning Representations* (2026).

[3] Qian, Cheng, et al. "ToolRL: Reward is All Tool Learning Needs." *Advances in Neural Information Processing Systems* 38 (2025).

## 评估脚注

- 所有分数均为百分比（越高越好）。
- 所有模型都在 thinking（推理）模式下评估。
- 所有使用外部 API 的基准都在 **November 3, 2026** 运行。
- ¹ BFCL v4：总分按官方加权公式计算（40% Agentic、30% Multi-Turn、10% Live、10% Non-Live 和 10% Hallucination），取 3 次运行的平均。
- ² ACEBench：总体准确率。所有模型均在函数调用（FC）模式下评估；取 2 次运行的平均。
- ³ τ-bench：τ²-bench（零售、电信）和 τ³-bench（银行）的平均值，不含 airline；取 3 次运行的平均。
- ⁴ Claw-Eval：官方平均任务得分，每个任务按 安全性 ×（0.8 × 完成度 + 0.2 × 鲁棒性）计分；取 3 次运行的平均。
- ⁵ BrowseComp-Plus：准确率，所有模型最多 30 步。
- ⁶ ToolSandbox：8 个设置上的平均相似度得分。
- ⁷ GPQA Diamond：全部 198 道题上的准确率，取 3 次运行的平均，启用 thinking。
- ⁸ MMLU-Pro：准确率。
- ⁹ IFEval、IFBench：prompt 级严格准确率。
- ¹⁰ Multi-IF：取 3 次运行的平均。

该作者的更多文章

## QVAC TranscribePsy：最先进的端侧多语言语音识别

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)

8

October 14, 2026

## QVAC Genesis III：用于高效语言模型预训练的大规模、高质量开放合成 STEM 语料库

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)

September 23, 2026

### 社区

把图片、音频和视频拖进文本输入框、粘贴，或点击此处即可上传。

点按或粘贴到此处上传图片

· [注册](https://huggingface.co/join?next=%2Fblog%2Fqvac%2Fbotpsy) 或 [登录](https://huggingface.co/login?next=%2Fblog%2Fqvac%2Fbotpsy) 后发表评论


2

- [![](https://huggingface.co/avatars/0532faec32a12d143b5329642a709b0f.svg)](https://huggingface.co/joooon)
- [![](https://huggingface.co/avatars/30ff51594b6454a1eced9a0d472d2ec1.svg)](https://huggingface.co/milangritta)
