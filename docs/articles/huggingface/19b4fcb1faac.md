---
vendor: huggingface
title: BotPsy：具有数十亿参数代理语言模型的设备上个人助理
original_title: 
url: https://huggingface.co/blog/qvac/botpsy
date: 2026-11-11
lang: zh
captured: 2026-11-11
extractor: readability-v1
translator: mt
status: translated
body_sha: 6ef13329f6e5
---

[返回文章](https://huggingface.co/blog)

# BotPsy：具有数十亿参数代理语言模型的设备上个人助理

团队文章

Published November 11, 2026

2

- [![](https://huggingface.co/avatars/0532faec32a12d143b5329642a709b0f.svg)](https://huggingface.co/joooon)
- [![](https://huggingface.co/avatars/30ff51594b6454a1eced9a0d472d2ec1.svg)](https://huggingface.co/milangritta)

[![Milan Gritta 的头像](https://huggingface.co/avatars/30ff51594b6454a1eced9a0d472d2ec1.svg)](https://huggingface.co/milangritta)

米兰·格里塔

米兰格利塔

[![QVAC 的头像](https://cdn-avatars.huggingface.co/v1/product/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)](https://huggingface.co/qvac) [qvac](https://huggingface.co/qvac)

[![Jihye Back 的头像](https://cdn-avatars.huggingface.co/v1/product/uploads/61a623353aff6ad7c083e882/biFOfePqURZW0snJHfy_Y.jpeg)](https://huggingface.co/happy-jihye)

智惠回来

快乐智惠

[![QVAC 的头像](https://cdn-avatars.huggingface.co/v1/product/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)](https://huggingface.co/qvac) [qvac](https://huggingface.co/qvac)

[![JinUk, Cho 的头像](https://huggingface.co/avatars/1299f5cd3558e75571711d544f4a6d29.svg)](https://huggingface.co/jucho2725)

曹镇旭

朱乔2725

[![QVAC 的头像](https://cdn-avatars.huggingface.co/v1/product/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)](https://huggingface.co/qvac) [qvac](https://huggingface.co/qvac)

[![Ohjoon Kwon 的头像](https://huggingface.co/avatars/0532faec32a12d143b5329642a709b0f.svg)](https://huggingface.co/joooon)

权五俊

珠云

[![QVAC 的头像](https://cdn-avatars.huggingface.co/v1/product/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)](https://huggingface.co/qvac) [qvac](https://huggingface.co/qvac)

[！[帕特里克·兰伯特头像](https://cdn-avatars.huggingface.co/v1/product/uploads/no-auth/Pmar3VJzQzgT4gdO8dpwt.png)](https://huggingface.co/patrik-lambert)

帕特里克·兰伯特

帕特里克-兰伯特

[![QVAC 的头像](https://cdn-avatars.huggingface.co/v1/product/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)](https://huggingface.co/qvac) [qvac](https://huggingface.co/qvac)

[![Mathias Buus 的头像](https://huggingface.co/avatars/04b3527ef6ff1d6feebcad80e5c0e5c6.svg)](https://huggingface.co/mafintosh)

马蒂亚斯·布什

马芬托什

[![QVAC 的头像](https://cdn-avatars.huggingface.co/v1/product/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)](https://huggingface.co/qvac) [qvac](https://huggingface.co/qvac)

[![Amril Nurman 的头像](https://huggingface.co/avatars/321662b676b3141ce8410614e581e2c.svg)](https://huggingface.co/Nurman)

阿姆里尔·努曼

努曼

[![QVAC 的头像](https://cdn-avatars.huggingface.co/v1/product/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)](https://huggingface.co/qvac) [qvac](https://huggingface.co/qvac)

前沿云LLM的运营成本可能会出现意外波动，而且依赖此类第三方模型会带来漏洞，因为提供商可以随时修改、拒绝或废弃访问。此外，专有模型为特定工作流程提供有限的定制，同时给隐私、数据控制和透明度带来风险。此外，并非每项任务都需要前沿级别的智能：小型、专业的代理同样能够完成特定任务，而且运行成本显着降低，因为许多常规或较小的工作负载可以在设备上高效处理。随着每个参数的智能不断快速提高，我们的目标是站在向高性能、注重隐私的自托管模型转变的最前沿。

Tether AI Research 推出 **BotPsy**，这是一个 0.8B 参数模型 介绍 **BotPsy**，这是一个专为函数调用和代理工作流程而设计的 0.8B 参数模型，构建于 Qwen3.5-0.8B 之上，适合设备上部署。 BotPsy 是一款“个人助理”，它使用工具为用户执行各种简单的任务，涉及的领域包括网络搜索和研究、旅行和生活方式、商业和金融、企业和客户运营、设备和车辆控制、文件和文档、日历以及电子邮件和消息传递。由于其参数数量较少，它最适合低到中等难度的任务。 BotPsy 在其规模内实现了最先进 (SOTA) 的工具使用和代理性能，优于我们测试的每个参数高达 1.2B 的模型（图 1 和 2）。它专为安全的设备上工作流程而设计，提供卓越的指令遵循可靠性和效率，同时保持用户数据的私密性。作为一个小模型，BotPsy 仍然会犯错误，并且不适合高风险使用；请阅读[预期用途和限制](https://huggingface.co/blog/qvac/botpsy#intended-use-and-limitations) 了解更多信息。

🤗 [模型（安全张量）](https://huggingface.co/qvac/BotPsy-0.8B) | 📦 [GGUF（bf16、Q8、Q4）](https://huggingface.co/qvac/BotPsy-0.8B-GGUFs)

**图 1：** BotPsy-0.8B 显着优于其基本模型，并在六个工具使用和代理基准测试中领先于五个，包括相对于 Qwen3.5-2B-Think（其大小的 2.5 倍）；仅在 Claw-Eval 上，Qwen3.5-2B-Think 才领先。

**图 2：** *知识：* 与类似大小的模型相比，工具使用训练保留并改进了 BotPsy 的一般知识，尽管整体知识仍然主要随参数计数而变化。 *指令遵循：* BotPsy 擅长遵循显式指令和多轮任务，但其性能会随着指令的积累而下降，并且在资源较低的语言中会出现滞后。

### 版权投诉

我们将针对侵犯版权的通知采取适当的行动。如果您认为您的作品被以侵犯您知识产权的方式使用或复制，请发送电子邮件至 [data-apps@tether.io](mailto:data-apps@tether.io)，识别并描述受版权保护的作品和涉嫌侵权的内容，以提交侵权通知。

## 主要亮点

### 基准测试结果

- **其基本模型的性能提高了一倍：** BotPsy 在关键基准上将 Qwen3.5-0.8B-Think 的代理能力大致提高了一倍：BFCL v4 从 23.4 升至 44.0，ACEBench 从 30.1 升至 58.7，τ-bench 从 23.2 升至 51.5（零售、电信和银行子集的平均值）。
- **同类中最佳智能体：** BotPsy 在所有六个工具使用和智能体基准测试中均优于 ≤1.2B 参数权重等级（Qwen3.5-0.8B-Think、LFM2.5-1.2B-Think、MiniCPM5-1B-Think）的领先模型：BFCL v4、ACEBench、τ-bench、ToolSandbox、Claw-Eval 和BrowseComp-Plus。
- **优于其较大的兄弟：** BotPsy 在六个基准测试中的五个上测试的所有模型中得分最高，在 BFCL v4（44.0 vs 37.7）、ACEBench（58.7 vs 55.4）、τ-bench（51.5 vs 46.5）、ToolSandbox（64.6）上击败了 Qwen3.5-2B-Think（一个 2.5 倍大小的模型）与 41.2）和 BrowseComp-Plus（4.5 与 2.8）。仅在 Claw-Eval 上，Qwen3.5-2B-Think 领先（48.9 vs 46.5）。

### 模型能力

- **在多轮工作流程中更可靠：** 在 τ²-bench 上，代理必须与客户进行长时间对话，遵循严格的策略并代表客户行事，它在电信方面的得分为 82.5，领先于 Qwen3.5-2B-Think (69.3)。在 BFCL v4 的多回合任务中，它比基准值从 7.5 上升到 46.1，几乎是 Qwen3.5-2B-Think (23.8) 的两倍。按应用程序分组，其多步分数领先于商业和服务领域（58.3 vs 47.4，次之，Qwen3.5-2B-Think）以及设备和系统管理领域（46.1 vs 31.9）的所有模型。
- **知道何时（不）调用工具：** 行动的代理也必须知道何时不行动。在 BFCL v4 的幻觉测试中，BotPsy 的得分为 86.1，是所有测试模型中最高的，该测试检查模型在不存在适当工具时是否会下降。在 ACEBench 的特殊情况下，即请求不完整、包含错误参数或给定工具无法提供服务的情况下，它的得分为 51.3，高于其基本模型的 13.7。
- **遵循说明，同时保留知识：** BotPsy 专注于工具使用，同时保留一般技能。指令跟随能力大幅提升，IFEval 从 59.7 升至 90.8，IFBench 从 22.0 升至 55.9，是所有测试模型中 IFBench 得分最高的。常识也有所提高，GPQA Diamond 从 33.2 升至 38.1，MMLU-Pro 从 41.6 升至 48.9。在所有四个基准测试中，BotPsy 都优于我们测试的所有其他 1.2B 参数或更少的模型。

### 安全、效率和部署

- **比同类中的领先模型更安全：** 在跨越六个危害类别的自动红队中，BotPsy 在 21% 的时间内产生不安全响应，而其基本模型的这一比例为 36%。这是所有参数高达 1.2B 的模型中比率最低的（LFM2.5-1.2B-Think：35%；MiniCPM5-1B-Think：47%）。对于读取不受信任工具输出的代理来说最重要的提示注入攻击，不安全率从其基本模型的 46% 下降到 31%。
- **更高效的推理和更少的循环：** 对于所有五个模型均正确回答的问题，BotPsy 得出答案的推理标记比 GPQA Diamond 上的基本模型少约 3 倍（3,690 vs 11,563），在 MMLU-Pro 上则少 2.7 倍（1,912 vs 5,105）。在所有 IFBench 尝试中，陷入重复推理循环的比率从 22.9% 下降到 1.4%，达到 32k 代币限制的运行率从 28.3% 下降到 0.2%。更短、更果断的推理应该可以减少设备上的延迟。
- **开源且随时可用：** BotPsy 将在 Apache 2.0 许可证下以开放权重发布，用于研究和教育用途。它将提供三种精度（bf16、Q8、Q4）、Hugging Face 安全张量以及 QVAC SDK 和 llama.cpp 的 GGUF 文件。

## 更广阔的视野

在 BotPsy 的基础上，Tether Data, S.A. de C.V. 的未来开发将在 BotPsy 的基础上进行。 （“Tether AI Research”、“我们”、“我们的”）将专注于扩展设备上的代理功能，以与更广泛的硬件和本地服务无缝集成。 Tether 的 Hypersearch 将发展为支持更强大的去中心化点对点 (P2P) 查询，进一步确保绕过企业跟踪器的私密、加密的网络搜索。 QVAC Fabric 本地微调机制将得到优化，以更深入地适应个人用户偏好、工作流程和专用工具环境。未来的迭代将允许智能手机界面在离线到在线转换期间顺利地将繁重的计算任务委托给家庭 PC 或可信的安全 P2P 节点。隐私协议将不断加强，以保证所有个人数据、凭证和决策严格保留在本地硬件上。将引入协作功能，以允许跨受信任的本地网络进行安全的代理间通信，而不会损害用户的机密性。最终，这些进步将巩固 BotPsy 作为一个完全自主、功能强大的个人人工智能生态系统，让用户完全掌控自己的数字生活。

## 方法论

BotPsy 基于 Qwen3.5-0.8B，并经过四个连续阶段的后训练：监督微调（SFT）、多教师按策略蒸馏（MOPD）和两轮强化学习（RL）。每个阶段都使用前一阶段的最佳检查点作为起点，并受益于不同的学习信号：参考轨迹的模仿、更大教师模型的令牌分布以及基于规则的工具调用奖励（见图 3）。

**图 3：** BotPsy 训练配方。学生经历四个阶段。三名 Qwen3.5-4B 专业教师（每人都接受过一项技能的 RL 培训）在蒸馏阶段进行指导。

### 训练过程：四个阶段，三种反馈

我们的方法采用四个阶段的培训，从三种类型的信号中学习：演示、专业教师和可验证的奖励。

**从演示中学习 (SFT)**

我们首先对工具使用对话进行全参数监督微调。其中包括来自模拟环境的多轮代理轨迹、重放的单步、并行和多步调用，以及不应调用工具的情况。

**向老师学习（MOPD）**

接下来，学生接受在策略蒸馏（OPD）的训练：它生成自己的响应，并且专业教师使用每个令牌的反向 KL 散度作为训练信号提供每个令牌的反馈。为了培养教师，我们首先对三个 Qwen3.5-4B 模型进行强化学习训练，专门用于工具使用、一般推理和指令遵循。在培训期间，每个提示都会发送给其中一位老师。该阶段主要旨在恢复在 SFT 阶段退化的知识和指令遵循，尽管工具使用指标也有所增加（见图 4）。

**图 4：** 每个训练阶段后每个能力组的平均得分。 SFT 促进了工具的使用，但将知识和指令推到了基础模型以下；蒸馏使两者都回到基础之上，RL 阶段进一步增加了这三者的收益。

**从规则和环境中学习（强化学习阶段）**

最后，该模型使用 DAPO [1] 进行强化学习训练，仅从规则和验证者计算的奖励中学习。第一轮侧重于工具调用，并伴有指令跟随和 STEM 选择题。与 Tool-N1 [2] 一样，工具调用奖励首先检查推理和工具调用格式。然而，它不是 Tool-N1 的二元正确性奖励，而是本着 ToolRL [3] 的精神提供细粒度的部分信用，将预测的工具名称、参数名称和参数值与基本事实进行匹配。

第二轮将培训组合扩大到一般领域可验证的​​任务：数学、代码、知识（多项选择）问题、指令遵循、结构化输出以及在模拟工作环境中使用多步骤工具。虽然这种组合不包含多轮对话，但它进一步改进了多轮函数调用。

### 数据构成

训练的每个阶段都使用不同的数据混合（图 5）。 SFT阶段主要关注工具的使用，为后续阶段做好准备。 MOPD 混合物结合了工具使用、知识和指令跟踪数据，既可以进一步改进函数调用，又可以从 SFT 阶段恢复通用域回归。第一个强化学习阶段同样主要关注工具的使用，而第二个强化学习阶段则将平衡转向通用领域数据（指令跟踪、知识、数学和代码），保持工具使用的较小份额。

**图 5：** 每个阶段的近似训练数据组成，按功能分组。

## 结果

### 工具使用和代理

BotPsy 的工具使用性能大约是其 Qwen3.5-0.8B 基础的两倍，并且在六个代理基准中的五个上是五个模型中最强的：BFCL v4（44.0 vs 23.4）、ACEBench（58.7 vs 30.1）、τ-bench（51.5 vs 23.2）、BrowseComp-Plus（4.5 vs 1.9）和 ToolSandbox （64.6 比 30.5）。在所有五个方面，它还领先于 Qwen3.5-2B-Think，后者是其尺寸的 2.5 倍（分别为 37.7、55.4、46.5、2.8 和 41.2；参见表 1）。在 Claw-Eval 上，Qwen3.5-2B-Think 领先（48.9 vs 46.5）。

|基准| **BotPsy-0.8B** 我们的 | Qwen3.5-0.8B-思考底座·1× | Qwen3.5-2B-Think 2.5× | LFM2.5-1.2B-思考1.5× | MiniCPM5-1B-Think 1.25× |
| --- | --- | --- | --- | --- | --- |
| BFCL v4 | | BFCL v4 **44.0** | 23.4 | 23.4 37.7 | 37.7 28.1 | 28.1 22.8 | 22.8
| ACEBench² | **58.7** | 30.1 | 30.1 55.4 | 55.4 39.4 | 39.4 24.5 | 24.5
| τ-长凳³ | **51.5** | 23.2 | 23.2 46.5 | 46.5 6.5 | 6.5 28.8 | 28.8
|爪评估⁴ | 46.5 | 46.5 39.3 | 39.3 **48.9** | 31.6 | 31.6 31.0 | 31.0
| BrowseComp-Plus⁵ | **4.5** | 1.9 | 1.9 2.8 | 2.8 0.2 | 0.2 0.8 | 0.8
|工具沙箱⁶ | **64.6** | 30.5 | 30.5 41.2 | 41.2 45.7 | 45.7 28.1 | 28.1
| *平均* | ***45.0*** | *24.7* | *38.8* | *25.3* | *22.7* |

**表 1：** 工具使用和代理基准（0-100，越高越好）。每行的最佳得分**粗体**，第二好的下划线；乘数给出相对于 BotPsy-0.8B 的参数计数。平均值是六个基准的未加权平均值。有关评估设置的详细信息，请参阅[评估脚注](https://huggingface.co/blog/qvac/botpsy#evaluation-footnotes)。

＃＃＃ 知识

工具使用培训不需要常识：GPQA Diamond 从 33.2 上升到 38.1，MMLU-Pro 从 41.6 上升到 48.9，是 1.2B 参数或以下参数下最好的模型（LFM2.5-1.2B-Think：35.0 和 39.4；MiniCPM5-1B-Think：15.8 和 40.0）。知识仍然主要与参数数量相关，Qwen3.5-2B-Think 得分远高于（59.9 和 65.5）。因此，BotPsy 旨在为它不知道的事实调用工具，而不是充当知识模型。

|基准| **BotPsy-0.8B** 我们的 | Qwen3.5-0.8B-思考底座·1× | Qwen3.5-2B-Think 2.5× | LFM2.5-1.2B-思考1.5× | MiniCPM5-1B-Think 1.25× |
| --- | --- | --- | --- | --- | --- |
| GPQA 钻石⁷ | 38.1 | 38.1 33.2 | 33.2 **59.9** | 35.0 | 35.0 15.8 | 15.8
| MMLU-Pro⁸ | 48.9 | 48.9 41.6 | 41.6 **65.5** | 39.4 | 39.4 40.0 | 40.0

**表 2：** 一般知识基准（0-100，越高越好）。每行的最佳得分以 ** 粗体 ** 表示，第二好的得分用下划线表示。有关评估设置的详细信息，请参阅[评估脚注](https://huggingface.co/blog/qvac/botpsy#evaluation-footnotes)。

### 遵循说明

BotPsy 在以下明确指令方面是五种中最好的：IFEval 90.8（base 59.7；Qwen3.5-2B-Think 80.0）和 IFBench 55.9（base 22.0；Qwen3.5-2B-Think 40.9）。 Multi-IF 以八种语言测试了三轮以上的指令，得分为 67.2，与 Qwen3.5-2B-Think (66.9) 和 LFM2.5-1.2B-Think (68.2) 持平。它一开始最强（第 1 回合为 84.3，五个模型中最高），但随着指令的累积下降得更快（第 3 回合为 51.0，这两个模型为 56.5 和 56.2）。资源较少的语言仍然是一个弱点：印地语 (24.5) 和俄语 (57.6) 远远低于英语、中文、法语、西班牙语、意大利语和葡萄牙语的 72-80 分。

|基准| **BotPsy-0.8B** 我们的 | Qwen3.5-0.8B-思考底座·1× | Qwen3.5-2B-Think 2.5× | LFM2.5-1.2B-思考1.5× | MiniCPM5-1B-Think 1.25× |
| --- | --- | --- | --- | --- | --- |
| IFEval⁹ | **90.8** | 59.7 | 59.7 80.0 | 85.6 | 85.6 78.4 | 78.4
| IFBench⁹ | **55.9** | 22.0 | 22.0 40.9 | 40.9 33.9 | 33.9 40.6 | 40.6
|多中频 1⁰ | 67.2 | 67.2 43.2 | 43.2 66.9 | 66.9 **68.2** | 53.4 | 53.4

**表 3：** 指令遵循基准（0-100，越高越好）。每行的最佳得分以 ** 粗体 ** 表示，第二好的得分用下划线表示。有关评估设置的详细信息，请参阅[评估脚注](https://huggingface.co/blog/qvac/botpsy#evaluation-footnotes)。

### 多轮对话

最大的相对收益来自多轮、有状态交互，其中 BotPsy 领先五个多轮基准中的四个（图 6）。在 BFCL v4 多圈上，它从 7.5 上升到 46.1，几乎是 Qwen3.5-2B-Think (23.8) 的两倍，在 ACEBench Agent 上从 7.9 上升到 28.3（Qwen3.5-2B-Think：16.2）。在 τ²-bench 上，它在零售领域的基数翻了一番（67.8 vs 33.9，以微弱优势领先于 Qwen3.5-2B-Think（65.5）），并在电信领域达到 82.5，在电信领域，代理必须指导用户进行多次故障排除（MiniCPM5-1B-Think：74.0；Qwen3.5-2B-Think：69.3）。在单次调用（BFCL 非实时：83.0）和在不合适时不调用工具（BFCL 幻觉：86.1）方面，它也是五种工具中最可靠的。

**图 6：** 多轮代理任务：BFCL v4 多轮、ACEBench Agent、τ²-bench（零售、电信）和 τ³-bench（银行）。 BotPsy 在五个基准测试中领先四个；在 τ³-banking 上，每个模型都保持在 5 以下。

### 弱点

BotPsy 的弱点是开放式搜索以及 Qwen3.5-2B-Think 仍然领先的一些领域。 BotPsy 的 BrowseComp-Plus 得分为 4.5，是五个中最好的，但绝对值较低，并且在 BFCL 网络搜索 (14.0) 和内存 (16.3) 上它落后于 Qwen3.5-2B-Think（19.8 和 26.1）。在 Claw-Eval 上，BotPsy 在其基础上有明显改善（46.5 vs 39.3），但仍略低于 Qwen3.5-2B-Think（48.9）。在 ACEBench 的特殊情况（不完整或错误的请求）上，Qwen3.5-2B-Think 也领先（58.0 vs 51.3），尽管 BotPsy 远远高于其基础（13.7）。 τ³-banking 是 BotPsy 不领先的一个多轮基准：没有模型超过 5（BotPsy 4.1，与其基础没有变化；Qwen3.5-2B-Think 4.8）。

## 作用所在：应用程序级性能细分

BotPsy 可以处理各种用例和场景。图 7 按应用程序组细分了基准测试场景，将简单场景（单轮、一个工具调用）与复杂场景（多轮或多工具）分开。本节引用的总分是所有场景的平均分；图 7 的底行是七组的未加权平均值，因此其数字有所不同。

### 单一工具调用在任何地方都可以正常工作

简单场景在每个具有有意义样本的应用组中得分为 70-79（通信和社交只有 6）。总体而言，BotPsy 得分为 75，比其基本模型 (54) 高出约 21 分，略高于 Qwen3.5-2B-Think (70)。

**图 7：** 按应用程序组划分的每个场景的平均得分（0-100，越高越好），适用于简单（左）和复杂（右）场景。 n给出每组中简单/复杂场景的数量；底行是七组的未加权平均值。

### 最大的收获是多步骤任务

在复杂场景中，BotPsy 的总体得分为 39.5，而其基础得分为 17.9，Qwen3.5-2B-Think 得分为 30.8。涨幅最大的是通信和社交（基础 61 比 13）、商业和服务（58 比 27）以及设备和系统管理（46 比 15）。 Qwen3.5-2B-Think 仅在个人生产力和工作方面领先（64 vs 58，38 个场景，主要是 Claw-Eval），而 MiniCPM5-1B-Think 在沟通和社交方面略有领先（61.5 vs 60.5）。多步骤任务的得分仍然低于单次调用，这仍然是较难任务的主要限制。

### 多步骤信息检索是弱点

复杂信息检索和研究场景得分 15（单次调用：79）。大多数是 BrowseComp-Plus 深度研究问题，对于该尺寸范围内的每个模型来说都很难（基数：9；Qwen3.5-2B-Think：14）。

## 推理效率

BotPsy 比它的基础推理要少得多，并且在多轮代理任务上轮次更少，才能得出正确的答案。这与我们在整个训练过程中明确关注推理效率是一致的。下面的所有比较都是针对相同的问题或任务（所有五个模型都正确回答或解决的问题或任务）进行的，因此难度差异不会影响数字。推理标记是使用每个模型自己的标记生成器进行计数的。

**图 8：** GPQA Diamond、MMLU-Pro、IFEval 和 IFBench 上每个正确答案的推理标记的准确性。令牌是根据所有五个模型都正确回答的问题来衡量的；准确性高于所有问题。左上角更好；虚线是帕累托边界。

**推理更短，准确度更高。** 与其基础相比，BotPsy 在 GPQA Diamond（3,690 vs 11,563）、MMLU-Pro（1,912 vs 5,105）、IFEval（3,148 vs 4,433）和 IFBench（4,204 vs 11,576），同时在所有四项上得分都更高（图 8）。它并不是所有地方都是最短的模型：LFM2.5-1.2B-Think 在 MMLU-Pro、IFEval 和 IFBench 上编写较短的推理，而 MiniCPM5-1B-Think 在 IFEval 和 IFBench 上编写，但精度低于 BotPsy。

**图 9：** τ² 基准零售和电信中每个已解决任务的助理轮次通过率。轮流是根据所有五个模型解决的任务来测量的；通过率高于所有任务。左上角更好；虚线是帕累托边界。

**在多轮代理任务中，轮数比基础轮数少。** 在所有五个模型都解决的 τ² 工作台任务中，BotPsy 需要的辅助轮数比其基础轮数少（图 9）：

- τ²-零售：10.7 回合，而基础版为 11.7 回合（减少 9%），Qwen3.5-2B-Think 为 10.6 回合。
- τ²-电信：13.1 回合，而基础版为 17.6 回合（减少 26%），Qwen3.5-2B-Think 为 13.8 回合（减少 5%）。

它同时传递的任务数量是基础的 2.0 倍（零售）和 2.6 倍（电信）。 MiniCPM5-1B-Think 在零售上使用较少的回合 (8.7)，但仅通过了 9.9% 的零售任务。

## 预期用途和限制

BotPsy 的开发是为了推进最先进的技术并支持研究和教育用途。基于我们的工作开发的模型可能适用于设备和系统管理（设置、文件和文档、时钟和闹钟）、个人生产力和工作（日历和任务、电子邮件、协作工具）、通信（消息传递）、信息检索和研究（网络搜索、天气、新闻）、媒体和生活方式（视频、音乐、食谱和健身、照片）以及商业和服务（地图和旅行、金融、购物和交付）等领域的任务。由于其参数数量较少，它**最适合低到中等难度的任务**。

BotPsy 主要使用英语进行训练和测试，这是推荐的语言。它还在 Multi-IF 上进行了评估，其中涵盖了另外七种语言（中文、法语、印地语、意大利语、葡萄牙语、俄语和西班牙语）：它在大多数语言中表现良好，但在印地语和俄语中得分低得多。 BotPsy 是一个小型语言模型，它会犯错误。它不适用于安全关键或高风险的自动化决策，也不适用于涉及金钱、个人信息、健康和其他敏感主题的应用。

## 引文
```
@misc{botpsy2026,
  title  = {BotPsy: On-Device Personal Assistant with a Sub-Billion-Parameter Agentic Language Model},
  author = {{Tether Data, S.A. de C.V. d.b.a. Tether AI Research}},
  year   = {2026},
  note   = {Hugging Face blog}
}
```
## 参考文献

[1] 于其英, 等. “DAPO：大规模开源LLM强化学习系统。” *神经信息处理系统的进展* 38 (2025): 113222–113244。

[2] 张少坤，等． “Nemotron-Research-Tool-N1：通过强化推理探索工具使用语言模型。” *学习表征国际会议*（2026 年）。

[3] 钱程，等。 “ToolRL：奖励是所有工具学习需求。” *神经信息处理系统的进展* 38 (2025)。

## 评估脚注

- 所有分数均为百分比（越高越好）。
- 所有模型均以思维（推理）模式进行评估。
- 所有使用外部 API 的基准测试均于 **2026 年 11 月 3 日**运行。
- 1 BFCL v4：使用官方加权公式（40% Agentic、30% Multi-Turn、10% Live、10% Non-Live 和 10% Hallucination）计算的总分，3 次运行的平均值。
- ² ACEBench：总体准确度。所有模型均在函数调用（FC）模式下进行评估； 2 次运行的平均值。
- ³ τ-bench：τ²-bench（零售、电信）和 τ³-bench（银行）的平均值，不包括航空公司； 3 次运行的平均值。
- ⁴ Claw-Eval：官方平均任务得分，其中每个任务得分安全性×（0.8×完成度+0.2×鲁棒性）； 3 次运行的平均值。
- ⁵ BrowseComp-Plus：准确性，所有模型最多 30 个步骤。
- ⁶ ToolSandbox：8 个设置的平均相似度得分。
- ⁷ GPQA 钻石级：所有 198 个问题的准确性，3 次运行的平均值，启用思考。
- ⁸ MMLU-Pro：准确性。
- ⁹ IFEval、IFBench：提示级严格精度。
- 1⁰ 多重 IF：3 次运行的平均值。

该作者的更多内容

## QVAC TranscribePsy：最先进的设备上多语言语音识别

- ![](https://cdn-avatars.huggingface.co/v1/product/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)

8

2026 年 10 月 14 日

## QVAC Genesis III：大规模、高质量的开放式合成STEM语料库，用于高效语言模型预训练

- ![](https://cdn-avatars.huggingface.co/v1/product/uploads/68d540a9b913fd49b5e41e0b/ooEaWBPmchmGPmfjyAXEr.png)

2026 年 9 月 23 日

### 社区

通过拖入文本输入、粘贴或单击此处来上传图像、音频和视频。

点击或粘贴此处上传图像

· [注册](https://huggingface.co/join?next=%2Fblog%2Fqvac%2Fbotpsy) 或 [登录](https://huggingface.co/login?next=%2Fblog%2Fqvac%2Fbotpsy) 发表评论

2

- [![](https://huggingface.co/avatars/0532faec32a12d143b5329642a709b0f.svg)](https://huggingface.co/joooon)
- [![](https://huggingface.co/avatars/30ff51594b6454a1eced9a0d472d2ec1.svg)](https://huggingface.co/milangritta)
