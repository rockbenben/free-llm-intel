---
vendor: huggingface
title: DeepMath：基于 smolagents 的轻量级数学推理智能体
original_title: DeepMath: A lightweight math reasoning Agent with smolagents
url: https://huggingface.co/blog/intel-deepmath
date: 2025-12-08
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 2a1f75fa2519
translator: agent
---

返回文章列表

# DeepMath：基于 smolagents 的轻量级数学推理智能体

发布于
					2025 年 12 月 4 日

在 GitHub 上更新

点赞

42

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/tI3V8-PZ8d3CC32fzO31e.png)](https://huggingface.co/Stars321123)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/PuIDZB9XDShHohKhYmdmp.png)](https://huggingface.co/YellowjacketGames)
- [![](https://huggingface.co/avatars/cca1f35838af8dbfcc9efe58a769a13e.svg)](https://huggingface.co/theLittleHump)
- [![](https://huggingface.co/avatars/9469599b176034548042922c0afa7051.svg)](https://huggingface.co/dark-pen)
- [![](https://huggingface.co/avatars/f1c0e2ac8395e4648b8a93c1a8254017.svg)](https://huggingface.co/boapps)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6055ae5d25cd24537dd59dc5/eswozkCirLrnyhufN8_-f.jpeg)](https://huggingface.co/danielkorat)

Daniel Fleischer

danf

Intel

Moshe Berchansky

mber

Intel

Moshe Wasserblat

moshew

Intel

![An LLM is using a calculator to answer questions.](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/intel-deepmath/deepmath-figure.jpg)

*作者：Intel AI Software Group*

[DeepMath](https://huggingface.co/Intel/deepmath-v1) 是一个对齐过的数学推理智能体，基于 **[Qwen3-4B Thinking](https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507)** 构建，并用 **GRPO（Group Relative Policy Optimization，组相对策略优化）** 微调。模型不再输出冗长的文字，而是为中间步骤生成**短小的 Python 代码片段**，在安全沙箱中执行，再把结果折叠回推理过程，从而降低错误率、缩短输出长度。该智能体用 **[smolagents 库](https://github.com/huggingface/smolagents)** 实现。

我们在四份数学数据集上评测 DeepMath：**[MATH500](https://huggingface.co/datasets/HuggingFaceH4/MATH-500)、[AIME](https://huggingface.co/datasets/opencompass/AIME2025)、[HMMT](https://huggingface.co/datasets/MathArena/hmmt_feb_2025) 和 [HLE](https://huggingface.co/datasets/cais/hle)**，结果显示：

- 🤖 仅智能体本身就能把输出长度最多降低 66%，同时准确率常常还有所提升。
- ⚡ GRPO 训练在几乎所有基准上进一步提升智能体表现。

👉 代码与评测脚本：[https://github.com/IntelLabs/DeepMath](https://github.com/IntelLabs/DeepMath) 
👉 模型：[https://huggingface.co/Intel/deepmath-v1](https://huggingface.co/Intel/deepmath-v1)

## 为什么做 DeepMath？

大语言模型（LLM）已具备很强的推理能力，但数学解题仍然困难：思维链（chain-of-thought）轨迹往往很长，且容易出算术错误。近期工作[^1][^2]证明小模型也能达到强劲表现，另有研究[^3]考察用工具调用来提高可靠性。这些论文普遍没有强调的一点是：压缩轨迹的冗长性，或显式训练模型偏好"短、以计算为中心"的轨迹——并在受约束、可审计的环境中执行它们。

我们聚焦两个目标：

- **把确定性计算卸载**给安全的执行器。
- **训练模型偏好简洁、以计算为中心的轨迹**，而非冗长文字。

**DeepMath** 的做法是把一个小型 Python 执行器与微调后的 LLM 结合，实现简洁的计算驱动推理。模型学会生成短 Python 片段，片段在沙箱中执行后再重新并入上下文。GRPO 微调通过奖励正确性、鼓励更短输出来强化这一行为。

## 工作原理

- 基座模型：[Qwen3-4B Thinking](https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507)。
- 执行器约束：沙箱环境、允许导入模块的白名单、逐片段超时限制。
- 推理：基于 [smolagents](https://github.com/huggingface/smolagents/) 创建了数学智能体，推理引擎使用 [vLLM](https://github.com/vllm-project/vLLM)。
- 训练：基于 [TRL](https://github.com/huggingface/trl) 的 GRPO trainer，我们修改了 TRL 的 vLLM 客户端与服务端，让 GRPO 的候选补全由我们的 DeepMath 智能体生成。

![Changes to vLLM client and server in TRL library.](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/intel-deepmath/trl-grpo-vllm-deepmath.png)
 *图 1：修改了 vLLM 客户端与服务端，在使用 vLLM 后端生成候选时调用 DeepMath 智能体。*

- **智能体接口：** 推理时，模型可以输出普通 token，也可以输出包含 Python 片段的特殊智能体调用。
- **执行：** 片段在带有严格安全约束的沙箱中运行（无文件 I/O、无网络、有超时）。
- **设计目标：** **简洁性：**用简短聚焦的代码片段替代多行文字计算。 **确定性与安全性：**强制执行限制。 **可解释性：**代码片段可读、可审计。

![Output example: it contains a short python snippet as well as its output which is used in the reasoning process.](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/intel-deepmath/output-example.png)
 *图 2：输出示例——生成 Python 代码、执行求值，答案被插入推理轨迹并用作上下文。*

## 用 GRPO 训练

我们用 **GRPO** 微调模型——这是一种奖励驱动的优化，平衡以下几项：

- **准确率奖励：**答对 +1。
- **使用代码片段：**生成了代码片段 +1，与准确率奖励按 10:1 加权。
- **长度压缩：**把 GRPO 候选补全限制在 5k token 以内，以此鼓励更短输出。
- **温度调度：**实现了线性温度调度（T=1.2 → T=0.7），在训练中平衡探索与稳定性。这一做法意在训练初期增强试错探索，随后随着技能熟练度提高逐步降温。
- **上下文学习（In-context Learning）：**包含 4 个已解答示例，其轨迹中含智能体调用和执行器输出，让模型学习语法与调用/响应模式。
- **数据集：**使用了 [OpenMathReasoning](https://huggingface.co/datasets/nvidia/OpenMathReasoning) 数据集中的 Tool-Integrated Reasoning（TIR）子集。注意 GRPO 只用数据中的题目，不用解答。选择该数据集是为了确保题目确实能从外部工具中获益。

## 评测

我们在四个数据集上把 DeepMath 与基线做了基准对比。指标包括：

- **majority@16：**跨样本的稳健度，为此前数学推理工作所采用，见参考文献。
- **平均输出长度：**简洁度。

![Main results table.](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/intel-deepmath/main-results.png)

- 我们把基线配置（[Qwen3-4B-Thinking-2507](https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507)，无智能体化）与 DeepMath 模型对比。作为消融，我们评估了自研智能体框架在未训练 Qwen3 模型上的运行，记作 **+Agent**；另外检验面向智能体用途的 GRPO 训练能否改善非智能体推理，记作 **+GRPO**。因此这两个消融项相互独立，不能叠加。
- 我们观察到智能体推理缩短了输出长度，准确率结果有好有坏。DeepMath 模型既经过 GRPO 训练、又以智能体模式运行，在轨迹变短的同时取得最高准确率。我们的结论是：**GRPO 训练和智能体推理二者缺一不可**，才能得到最佳结果。

**关键洞见：** DeepMath 把输出长度最多降低 **66%**，同时在高难度数据集上提升了准确率。

## 意义何在

- **准确率：**计算卸载减少了算术错误。
- **效率：**输出更短意味着推理更快、更易解释。
- **安全性：**沙箱执行降低了运行任意代码的风险。

## 结论

DeepMath 展示了一条务实而轻量的路径：把小型执行器与 LLM 结合，并训练模型偏好简短的、计算驱动的轨迹。卸载确定性计算能减少算术与数值误差、缩短轨迹；GRPO 微调进一步鼓励简洁且正确的答案。最终得到一个更准、更可解释的数学解题智能体——不需要超大模型，也不需要重量级外部工具。

## 亲自试试

欢迎查看 [GitHub 仓库](https://github.com/IntelLabs/DeepMath)并分享反馈！欢迎贡献。🚀

## 引用

如果你在研究中使用 DeepMath，请引用：

```
@software{deepmath2025,
  author = {Fleischer, Daniel and Berchansky, Moshe and Wasserblat, Moshe},
  title = {DeepMath: A Lightweight Math Reasoning Agent for LLMs},
  year = {2025},
  publisher = {Intel AI Labs},
  url = {https://github.com/IntelLabs/DeepMath}
}
```

## 局限与未来工作

- **范围**：我们聚焦小模型和数学推理。
- **泛化**：评测对象是竞赛类数学；结论未必能迁移到开放式数学创造或形式化证明。
- 执行生成的代码本身有风险。DeepMath 使用了严格沙箱和资源限制，但任何部署都应审慎管理攻击面并实施限流。

## 参考文献

[1] Luo, Michael, Sijun Tan, Justin Wong, et al. 2025. “DeepScaleR: Surpassing O1-Preview with a 1.5B Model by Scaling RL.” [https://pretty-radio-b75.notion.site/DeepScaleR-Surpassing-O1-Preview-with-a-1-5B-Model-by-Scaling-RL-19681902c1468005bed8ca303013a4e2](https://pretty-radio-b75.notion.site/DeepScaleR-Surpassing-O1-Preview-with-a-1-5B-Model-by-Scaling-RL-19681902c1468005bed8ca303013a4e2)

[2] Liu, Mingjie, Shizhe Diao, Ximing Lu, et al. 2025. “ProRL: Prolonged Reinforcement Learning Expands Reasoning Boundaries in Large Language Models.” arXiv:2505.24864. Preprint, arXiv, May 30. [https://doi.org/10.48550/arXiv.2505.24864](https://doi.org/10.48550/arXiv.2505.24864)

[3] Moshkov, Ivan, Darragh Hanley, Ivan Sorokin, et al. 2025. “AIMO-2 Winning Solution: Building State-of-the-Art Mathematical Reasoning Models with OpenMathReasoning Dataset.” arXiv:2504.16891. Preprint, arXiv, April 23. [https://doi.org/10.48550/arXiv.2504.16891](https://doi.org/10.48550/arXiv.2504.16891)

## 文中提到的模型 2

## 文中提到的数据集 5

我们博客的更多文章

llm

moe

long-context

## DeepSeek-V4: a million-token context that agents can actually use

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/62d648291fa3e4e7ae3fa6e8/oatOwf8Xqe5eDbCSuYqCd.png)

60

2026 年 4 月 24 日

cybersecurity

open-source

community

## AI and the Future of Cybersecurity: Why Openness Matters

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1626214544196-60c757ea5f9a76ab3f844f12.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1594144055859-5ee3a7cd2a3eae3cbdad1305.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1583857146757-5e67bdd61009063689407479.jpeg)

52

2026 年 4 月 21 日

### 社区

InstructorOnline

1 月 18 日

·

1 月 18 日编辑

可以用 LLM 来学习和研究数学话题吗？生成的输出每次不一样，步骤可能对也可能错吧？？

deleted

5 月 7 日

·

此评论已被隐藏

将文件拖入文本输入框、粘贴，或

点击此处

，即可上传图像、音频和视频。

点击或粘贴此处上传图片

· [注册](https://huggingface.co/join?next=%2Fblog%2Fintel-deepmath)或[登录](https://huggingface.co/login?next=%2Fblog%2Fintel-deepmath)发表评论

点赞

42

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/tI3V8-PZ8d3CC32fzO31e.png)](https://huggingface.co/Stars321123)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/PuIDZB9XDShHohKhYmdmp.png)](https://huggingface.co/YellowjacketGames)
- [![](https://huggingface.co/avatars/cca1f35838af8dbfcc9efe58a769a13e.svg)](https://huggingface.co/theLittleHump)
- [![](https://huggingface.co/avatars/9469599b176034548042922c0afa7051.svg)](https://huggingface.co/dark-pen)
- [![](https://huggingface.co/avatars/f1c0e2ac8395e4648b8a93c1a8254017.svg)](https://huggingface.co/boapps)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6055ae5d25cd24537dd59dc5/eswozkCirLrnyhufN8_-f.jpeg)](https://huggingface.co/danielkorat)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1664643955283-60570320cbe9c7542f3501e3.jpeg)](https://huggingface.co/orenpereg)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/63e0c8875c6964861ebb0c49/yzkhPSxgXtJCM62iMBOOK.jpeg)](https://huggingface.co/mber)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/606d6349f1259f30578520ad/72_XrFfgQ6p9tgJj5Bc5U.png)](https://huggingface.co/jmamou)
- [![](https://huggingface.co/avatars/d5adafb8958f422f363d2b1ecde12ba4.svg)](https://huggingface.co/sguskin)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/1616423186722-5f8907c65d083370c711f284.jpeg)](https://huggingface.co/ofirzaf)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/62d93cd728f9c86a4031562e/ix_LD-wjW8vCltosCVUmV.jpeg)](https://huggingface.co/danf)

## 文中提到的模型 2

## 文中提到的数据集 5
