---
vendor: huggingface
title: ToyBlocks：用于机器人学习与评估的受控世界
original_title: ToyBlocks: A controlled world for robot learning and evaluation
url: https://huggingface.co/blog/allenai/toyblocks
date: 2026-11-06
lang: zh
captured: 2026-11-07
extractor: readability-v1
translator: agent
status: translated
body_sha: 8e7188d109e5
---

[ 返回文章](https://huggingface.co/blog)

# ToyBlocks：用于机器人学习与评估的受控世界

Enterprise  Article

发布于 2026 年 11 月 6 日


5

- [![](https://huggingface.co/avatars/ab7fc92bae0354165d3f9890ac7f5b0b.svg)](https://huggingface.co/wookute221)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/XcLxZc6CL6VO7tOlh0T0g.jpeg)](https://huggingface.co/SmokeyPete)
- [![](https://huggingface.co/avatars/35af30f8a3713e3eda81ac4b9be515f5.svg)](https://huggingface.co/arahul2k2)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/DPzSLPCg9RvVBvkD3Mcys.png)](https://huggingface.co/rapidum)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/67953e11098348e24ae7f316/ZNT-1c2NOyhugYrzK5Vyf.png)](https://huggingface.co/sebast242)

[![Kyle Wiggers 的头像](https://huggingface.co/avatars/9c2a0976ea68fe021a4191d3d4c5454b.svg)](https://huggingface.co/Ai2Comms)

Kyle Wiggers

Ai2Comms

[![Ai2 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/652db071b62cf1f8463221e2/CxxwFiaomTa1MCX_B7-pT.png)](https://huggingface.co/allenai) [allenai](https://huggingface.co/allenai)

💻 [代码](https://github.com/allenai/ToyBlocks) | 📊 [数据](https://huggingface.co/datasets/allenai/toyblocks-data) | 🤖 [模型](https://huggingface.co/collections/allenai/toyblocks) | 📖 [文档](https://allenai.github.io/ToyBlocks/docs/user_guide/index.html)

[![ToyBlocks 等轴测机器人插图](https://www.datocms-assets.com/64837/1793826687-david-thumbnail-download-1.jpg)](https://www.datocms-assets.com/64837/1793826687-david-thumbnail-download-1.jpg)

机器人正在学会叠衣服、分拣零件以及抓取不熟悉的物体。然而，这些演示通常局限在非常狭窄的场景中，无法解释机器人究竟学到了什么，也无法说明它为何会失败。

为了研究复杂系统，科学家通常从培养皿或玻璃饲养箱这类小巧、受控的环境入手，在其中改变条件并观察效果。机器人学同样需要能够支持此类探索的环境——研究人员应当能够调整训练数据或模型设计、重复测试，并精准追溯失败的原因。

今天，我们推出了一个用于构建此类环境的框架，我们称之为 FoundationWorlds。每个 FoundationWorld 都将一个旨在特定环境中研究机器人学的受控仿真世界，与用于自动生成任务和训练演示的工具，以及用于长期度量机器人行为的指标体系结合在一起。它们共同构成了一个研究平台，可用于探究诸多关键问题，例如模型如何随着训练数据的增加而提升，以及如何最有效地将高层推理与精准的物理控制结合起来。

我们的首个基础世界是 [ToyBlocks](https://github.com/allenai/ToyBlocks)：一个围绕机械臂与桌面积木构建的开放仿真框架。场景设置有意保持极简，但机器人在推动、翻转和堆叠积木时，仍然必须对积木之间的相互作用以及如何排列它们进行推理。

ToyBlocks 能够自动生成演示数据（即机器人在仿真中完成任务的录像），无需耗费大量时间进行人工遥操作（teleoperation，即由人远程控制机器人）。研究人员可以轻松变换这些训练体验。例如，团队可以生成更多的推动或翻转演示，然后评估模型在未参与训练的任务上的表现。

以 ToyBlocks 作为我们的第一个 FoundationWorld 为起点，我们的目标是将这种方法扩展到越来越复杂的环境中。

## ToyBlocks 的工作原理

基于我们在开放机器人学习领域的早期工作（包括 [MolmoAct 2](https://allenai.org/blog/molmoact2)、[MolmoBot](https://allenai.org/blog/molmobot-robot-manipulation) 与 [MolmoSpaces](https://allenai.org/blog/molmospaces)），ToyBlocks 为研究人员提供了一种在受控约束领域中研究机器人学问题的方法。

作为一个 FoundationWorld，ToyBlocks 围绕四项核心要求设计：(1) 真实的物理特性与外观，(2) 大规模自动生成任务与演示，(3) 结合高层推理与灵巧操作的挑战，以及 (4) 对特定领域内可能任务的广泛覆盖。

开放式领域需要对极其多样的物体和交互建模，从而难以同时满足所有这些要求。相比之下，ToyBlocks 专注的聚焦范围使其能够全面满足上述标准。

在 ToyBlocks 较小的场景中，研究人员可以系统研究机器人如何学会执行任何合理任务，同时确信仿真中的机械臂和积木的行为与其物理实体高度一致。

[![Physical robot gripper above wooden blocks in the ToyBlocks setup](https://cdn-uploads.huggingface.co/production/uploads/638e39b249de7ae552d977b5/ov2i4rZoAkJw4z9FBaGfm.jpeg)](https://cdn-uploads.huggingface.co/production/uploads/638e39b249de7ae552d977b5/ov2i4rZoAkJw4z9FBaGfm.jpeg)

*ToyBlocks 设置中位于木块上方的物理机器人夹爪。*

ToyBlocks 绝不仅仅关乎抓取和堆叠积木：积木各表面上的图案和字母支持搜索、分类和排列任务。机器人在决定积木摆放位置前，可能需要先翻转积木以查看隐藏的表面。领域随机化（Domain randomization）——在不同场景间改变积木大小、桌面高度及其他物理属性——能够测试模型在几何结构变化时的泛化能力。

[![ToyBlocks framework architecture](https://www.datocms-assets.com/64837/1793917318-toyblocks-framework-current.png)](https://www.datocms-assets.com/64837/1793917318-toyblocks-framework-current.png)

*ToyBlocks 自动生成技能（针对短程任务的行为动作）和任务演示，可用于训练模型或通过追加训练（微调）调整先前训练好的模型。高层推理模型决定要做什么；底层动作模型控制机器人的运动。该框架还可用于轻松设计实验并验证假设。*

ToyBlocks 利用强化学习（RL）和用于计算机器人运动路径的运动规划（motion planning），为涉及简短动作序列的短时程（short-horizon）任务生成技能。技能训练在 Isaac Lab（Nvidia 用于仿真机器人学习的开源框架）中进行。通过试错，这些策略（policy，即选择机器人动作的模型）学会了非抓握式技能（non-prehensile skills），例如在桌面上推积木或在不抓取的情况下将其翻转到另一面。技能生成可以利用特权信息（privileged information，即仿真器可以直接提供但在真实机器人上无法直接获取的值，如积木的精确位置与朝向），而无需从相机图像中估计。这使得自动生成在现实世界中本需要人工遥操作的技能成为可能。

为了生成演示数据，任务与运动规划器（Task-And-Motion Planner, TAMP）自动选择并编排解决任务所需的各项技能，并规划技能之间的机器人动作。在仿真中运行每个规划，便可生成包含记录演示以及描述机器人所执行任务或技能标签的数据集。ToyBlocks 通过在单个图形处理器（GPU）上并行生成并执行数百个此类规划来扩展数据生成规模，性能可达实时速度的 24 倍。

依据传感器观测执行动作引入了感知难题：模型必须估计积木的位姿（pose，即其位置和朝向），而在仿真中这一数据原本可以直接提供。为了反映真实世界的环境条件，ToyBlocks 训练直接将原始传感器观测映射到动作的模型。

*在 ToyBlocks 中训练的 Molmo 2（高层模型）和 ManiFlow（底层模型）的执行过程。Molmo 2 选择旋转和翻转等技能，通过指向界面标明相关积木，而 ManiFlow 控制仿真臂执行所指挥的技能。*

ToyBlocks 可控的数据生成器让用户可以构建着重强调特定技能或填补现有数据集空白的训练混合数据。研究人员可以研究模型需要多少数据，以及哪些经验有助于其泛化到未见任务。例如，他们可以测试增加旋转和拾取放置演示是否能改善翻转能力，或者调节定义工作空间区域内外样本的平衡，进而在未参与训练的任务上评估这些选择。重要的是，对训练后模型的评估不仅能生成成功率指标，还能提供执行速度、施加在物体上的力量，以及通过规划模块所用相同规范度量的任务进度等丰富信息。

网页界面允许用户连接 Claude 或其他前沿模型，并使用自然语言向机器人下达指令或尝试任务，为用户提供了一种无需机器人学专业知识即可探索模型如何规划与行动的途径。

## 基于 ToyBlocks 的研究工作

以下评估使用 ToyBlocks 研究训练数据和方法如何影响性能、空间推理、对新字母和积木外观的泛化、多步规划、向物理机器人的迁移，以及通过工具执行动作的前沿模型。用户可以轻松设计自己的任务和评估指标来探索其他问题——例如，模型是通过指针选择物体还是通过发出诸如“拿起黄色积木”之类的文本指令表现更好。

### 底层动作模型：VLA 空间泛化

底层动作模型（例如视觉-语言-动作模型，VLA）将语言指令和视觉观测映射为机器人的动作。

VLA 的前提是，通过在大规模数据集上进行预训练，它们能够迅速泛化到不同的场景或特定工作空间。然而，关于这些动作模型泛化效果的证据仍然存在分歧。一些研究报告称，这些动作模型对输入的变化（如不同的物体布局和光照条件）非常脆弱；而另一些研究则表明 VLA 具有良好的泛化能力。我们认为，这些研究往往依赖于在空间变化灵活性上非常有限的真实世界数据集。ToyBlocks 使我们能够在一个简单、易复现且具有显著任务空间多样性的环境中，测试动作模型的泛化效果。

我们设计的泛化测试改变了完成指令所需的技能序列、积木上的字母或颜色，以及场景中的积木数量。一项堆叠研究可以在训练中排除四层积木的堆叠，然后测试模型能否组合熟悉的动作用于构建它们。工作空间研究将训练区域内新位置的表现与超出其边界（模型必须进行外推预测）的表现区分开来。我们在下方展示了该研究的设计与发现。

*我们考虑了四项任务：Stack（堆叠）、Unstack（拆解）、Flip（翻转）与 Rotate（旋转）。针对这些任务，我们研究了内插（训练范围内的全新配置）与外推（超出该范围的配置）。例如，我们在物体仅生成在左侧区域（绿色）的场景中进行训练，并在右侧区域（橙色）中测试泛化能力；或者使用 2 块和 5 块积木高度进行训练，并在 3 块和 4 块高度上测试。*

[![Spatial generalization results](https://www.datocms-assets.com/64837/1793904303-toyblocks-visual-08-ai2.png)](https://www.datocms-assets.com/64837/1793904303-toyblocks-visual-08-ai2.png)

*VLA 模型的空间泛化研究（结果基于 [ManiFlow](https://arxiv.org/abs/2509.01819)、[π0.5](https://arxiv.org/abs/2504.16054) 与 MolmoAct 2）。尽管进行了大规模预训练，这些主流动作模型在初始结果中的泛化表现依然较差。我们提升了泛化性能，并分析了各项技术的贡献。图表中的 LoRA 标签代表低秩适应（low-rank adaptation），这是一种通过少量可训练权重更新来微调模型的方法。我们认为动作模型的泛化能力远未得到解决；ToyBlocks 为系统探索泛化技术提供了一个极具价值的试验台。*

### 高层推理：视觉-语言模型

需要多个步骤的长时程任务使我们能够度量模型规划一系列动作以解决问题的能力。我们的框架允许我们创建此类长时程任务，并在高层与底层同时构建 oracle（提供正确规划或动作的基准参考组件）。这使我们能够在模型任务失败时，精确定位是高层规划失败还是底层执行失败。一个典型的长时程任务示例是用积木堆叠拼出“Ai2”；由于字母可能无法立即看到，agent 必须首先选择能够揭示信息的动作，随后规划并执行一系列动作来完成堆叠。

我们评估了具有明确高层规划与底层执行模型的分层模型。在此案例中，我们选择视觉-语言模型（VLM）Molmo 2 作为高层规划器，ManiFlow 作为底层策略。Molmo 2 选择要执行的技能以及对哪块积木执行，而底层模型负责执行该指令。我们训练诸如 ManiFlow 这样的底层模型在完成执行后暂停，并向高层模型请求下一条指令。我们在难度递增的三种场景下评估模型的规划能力。最简单的场景在初始状态下每个字符均正立且面向相机；中等难度的场景中字符可能未正立；最困难的场景中字符在任务开始时完全不可见。

[![Molmo 2 and ManiFlow block spelling results](https://www.datocms-assets.com/64837/1793904303-toyblocks-visual-09-ai2.png)](https://www.datocms-assets.com/64837/1793904303-toyblocks-visual-09-ai2.png)

*使用 Molmo 2 作为高层推理模型，并配合 ManiFlow 或运动规划器进行底层操作，在三字母积木拼写任务上的成功率。示例任务为“Stack Ai2”。Molmo 2 和 ManiFlow 均在 ToyBlocks 上训练，并在三种难度设置和两种泛化条件下进行评估。*

### 高层推理：Agent 系统

我们针对 agent 系统的实验测试了前沿模型如何通过工具调用进行规划与行动。我们使用 Claude Opus 5.5 研究了三种设置。在“搜索与拼写”（search-and-spell）设置中，我们通过 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro)（一种用于将 AI 应用连接到工具的标准协议）公开 ToyBlocks 技能。agent 通过相机图像观察场景，通过指向特定像素来调用拾取、翻转或旋转等技能，并自主决定何时搜索、何时搭建，或者何时宣布任务已完成或无法完成。相同的 MCP 工具既可以执行生成 ToyBlocks 演示数据的脚本化技能（基于运动规划的拾取和放置，以及基于强化学习的旋转和翻转），也可以执行学习得到的 ManiFlow 技能。ToyBlocks 包含了支撑这些实验的底层框架，该框架同样为前文提到的自然语言网页界面提供支持。

*前沿模型（Claude Fable 5.1）在 ToyBlocks 世界中控制机器人搜索积木并将其堆叠成拼出“Ai2”的塔。在此过程中，agent 思考道：“我需要搞清楚拾取放置是否会自动调正朝向，还是需要我手动纠正……我还剩下 63 次调用机会，足够进行一次受控测试”(0:06)。随后 agent 提出假设：“……也许夹爪的偏航角（yaw）呈径向——即从机器人底座指向积木方向”(0:15)，并最终证实了这一假设(0:26)，随后搭建了三块积木的塔，但其中的‘A’摆成了横向(1:11)。令人惊讶的是，当前的前沿模型尽管具备出色的规划、空间推理和搜索能力，却经常出现类似的感知错误（见下图）。*

在经典规划方面，该 agent（使用 Claude Opus 5.5 进行规划和动作选择的系统）利用文本描述，成功解决了全部 30 个积木堆叠任务，而前沿模型在[几年前](https://proceedings.neurips.cc/paper_files/paper/2023/hash/7a92bcdede88c7afd108072faf5485c8-Abstract-Datasets_and_Benchmarks.html)面对类似任务时曾十分吃力。此外，在闭环中反复观察相机图像并选择下一步动作时，它同样取得了 30 个任务全部成功的战绩（30/30）。

在搜索与拼写设置中，agent 必须生成拼出三个字母单词的积木堆叠。它必须在场景中多达八块积木里找到带有对应字母的积木。值得注意的是，50% 的场景并没有凑齐所需全部字母的积木，使得任务不可行。在这种情况下，我们要求 agent 明确声明该任务不可行。我们发现，在该实验中，agent 能够成功解决或正确声明不可行的任务占 63%。错误主要是由于 agent 将字母与外形相似的字母混淆（13%），或在堆叠中为字母选择了错误的朝向（15%）。

我们的结果还表明，当积木具有语义规律或图案模式时，agent 能够更高效地解决任务，利用这些规律来推理被遮挡的面。例如，在大多数不可行的场景中，当积木没有图案规律时，agent 在声明不可行之前会老老实实检查所有积木的每个面；而当积木具备语义图案时，它能够显著更快地声明不可行。

我们的第三个实验设置探讨 agent 是否能像科学家一样通过实验来理解其技能的行为规律。当某项技能的行为出乎意料时，agent 会形成假设、设计小型测试，并根据测试结果修正自身认知。我们在这一构想上进一步拓展，让 agent 自主运行实验，并[根据其发现编写自身的技能描述](https://openreview.net/forum?id=gxEC7M0oZj)。这些自主学习得到的描述将成功率从默认描述下的 24% 提升至 63%，超越了由人类专家编写描述所取得的 36%。

[![Search and Spell outcomes and exposed faces](https://www.datocms-assets.com/64837/1793911236-toyblocks-visual-10a-corrected.png)](https://www.datocms-assets.com/64837/1793911236-toyblocks-visual-10a-corrected.png)

*在每个“搜索与拼写”回合结束时，agent 所暴露的字母积木面的比例（柱状图为 20 个回合的平均值；每个标记代表一个回合，按结果区分样式）。在可行任务中，三字母目标单词的每个字母均存在；在不可行任务中，缺少一个字母，agent 应当如实说明。每块带图案的积木均印有某个字母的大写和小写形式，以及以此字母开头的图像（例如 A 积木：苹果 apple、蚂蚁 ant、A、1、飞机 airplane、a）；无图案积木的六个面则是随机且无关的。Correct（正确）：积木塔拼出了单词，或者对于不可行任务，agent 正确声明了任务不可能完成。Letter rotated or look-alike（字母倒置或混淆）：agent 搭建了塔，但字母被转偏或使用了相似字母替代，包括在缺失字母位置使用相似字母声明完成的五个不可行任务。Block fell out of reach; reported（积木掉落超出范围并汇报）：所需积木被推到了机械臂够不到的地方，因此 agent 汇报其任务已变得不可能。No report（未汇报）：agent 用尽了动作技能配额并在未声明任何结果的情况下停止。对于带图案的积木，agent 在看到较少表面后即可完成任务，因为它可以推断隐藏表面必定展示的内容，而无需检查每一个面。*

### 作为仿真器的动作条件世界模型

动作条件世界模型（Action-conditioned world models）经过训练，能够预测场景如何根据机器人的动作发生改变。将它们作为基于模型的仿真器的替代方案来训练和评估机器人策略，是当前的一个活跃研究领域。它们实现这一目标的效果取决于其对物理交互预测的准确程度，而在不知道场景真实状态的情况下，这很难度量。ToyBlocks 提供了这一基准真值（ground truth，即实际仿真的场景状态），从而支持对近期开发的世界模型在底层物体操作中的表现进行高度受控的测试。在这里，机械臂的末端执行器是其夹爪。

具体而言，我们测试了动作条件世界模型在基于示例执行数据训练后，是否能够预测积木的运动或技能执行的结果。为此，我们选择了四种不同的技能（拾取与放置、翻转、旋转以及混合任务），并为每种技能生成了 900 条轨迹（随时间推移的机器人状态与动作序列）。其中 50% 的轨迹是该技能的成功演示，另外 50% 则由于空间配置的微小变动而失败。在成功和失败执行次数均等的情况下，总是预测成功的模型准确率只有一半。模型在这些演示上进行微调，随后测试它们预测相同技能动作序列结果的能力。

[![World model comparison](https://www.datocms-assets.com/64837/1793904303-toyblocks-visual-11-ai2.png)](https://www.datocms-assets.com/64837/1793904303-toyblocks-visual-11-ai2.png)

*我们发现 Wan 2.2 在预测积木运动和任务结果方面最为准确。Astra 能很好地追踪夹爪，但难以模拟接触过程。LeWM 速度很快且在短交互片段上更准确，但在完整轨迹上会出现漂移。在补充实验中，我们还表明在位姿和成功预测上得分更高的模型也能生成更高质量的训练数据：加入来自最佳视频生成模型的 100 条模型生成轨迹（rollout），可使策略在未见区域的成功率从 19% 提升至 78%。*

我们测试了三类模型：一个拥有 50 亿参数的视频预测模型（[Wan 2.2](https://arxiv.org/abs/2503.20314)）、[一个创建自身物理仿真器并调优以匹配演示数据的 agent 模型 (Astra)](https://openai.com/index/gpt-6-astra/)，以及[一个隐空间世界模型 (LeWM)](https://arxiv.org/abs/2603.19312)。在测试过程中，每个训练好的模型必须基于初始图像和动作序列，分别预测未来的图像、仿真器状态或隐状态（学习到的内部表示）。对于完整轨迹，模型将初始图像作为唯一的观测图像，并结合动作序列进行预测。对于短交互片段（单次拾取、放置、翻转或旋转），模型从紧接该交互之前的真实图像开始。完整轨迹展示了误差如何在长时程中累积，而交互片段则隔离出单次交互（例如夹爪接触积木），并展示模型对其预测的效果。为了公平对比各个模型，我们探测各模型的预测结果，读取出它预期积木和夹爪在轨迹不同点所在的位置，以及它是否预期任务最终能够成功。

### 结合高层与底层模型的真实世界实验

Sim-to-real（仿真向实物迁移）评估在执行积木操作任务的物理机器人上测试仿真中训练的策略。通过对比仿真与真实世界的执行过程，我们评估在仿真中观察到的行为和失败模式能否为真实世界性能提供有意义的参考。例如，研究人员可以评估单个技能及其在更长时程任务中的组合，以找出失败发生的位置以及这些模式是否会延续到物理部署中。

我们测试了完全在 ToyBlocks 仿真数据集上训练的模型能否在零样本（zero-shot）下直接部署到真实世界，而无需在真实世界样本上进行训练。我们分别对 ManiFlow 及其各个底层技能（拾取、放置、翻转和旋转）进行了评估。我们测试了分层系统（Molmo 2 + ManiFlow）能否完成需要这些动作序列的长时程三积木拼写任务。真实世界实验在 30 种场景配置下使用配备 Robotiq 夹爪的 Franka FR3 机械臂。每个场景包含 4–10 块在训练中见过的积木。仅当相关积木被移动到目标位姿且无碰撞时，该回合才被视为成功。如果在回合中操作人员因不安全动作介入停止机器人，则记为失败。

ManiFlow 的原子技能成功率在仿真和真实世界中非常接近（分别为 80.0% 和 81.1%）。分层 Molmo 2 + ManiFlow 系统在 55.5% 的仿真回合 (111/200) 和 50.0% 的真实世界回合 (15/30) 中取得了成功；需要进一步的试验来建立跨任务的统计置信度。

[![Simulation and real-world success rates](https://www.datocms-assets.com/64837/1793919269-toyblocks-visual-12a-30-trials.png)](https://www.datocms-assets.com/64837/1793919269-toyblocks-visual-12a-30-trials.png)

*ManiFlow 底层模型和分层 Molmo 2–ManiFlow 系统在仿真与真实世界中的成功率。对于 ManiFlow，总数代表单个技能执行次数（拾取、放置、翻转和旋转），而对于 Molmo 2–ManiFlow，它代表积木拼写任务回合数。Molmo 2–ManiFlow 评估使用仿真评估中定义的最简单场景配置，其中积木字符可见且正立。*

*使用相同的高层规划器并排展示的真实世界与仿真积木堆叠执行对比。粉色圆环标出了规划器针对每项技能的目标点。各场景使用了不同的积木标签，且仿真的回放经过重新定时，以将抓取和释放动作与真实机器人对齐。*

为了将完全在 ToyBlocks 数据上训练的 Molmo 2 和 ManiFlow 迁移到物理机器人上，我们分三个阶段解决了仿真与现实之间的差距。

在数据生成之前，我们通过调整仿真机器人的参数（包括关节摩擦力和反映在关节处的电机及齿轮箱转动惯量 armature）来进行系统辨识（system identification），以匹配真实机器人的运动轨迹。在数据生成过程中，我们对物理属性（物体尺寸、摩擦力和桌面高度）以及视觉属性（光照、背景、材质和相机参数）进行随机化。在推理阶段，使用前置 ZED 相机和手腕上搭载的 ZED Mini 捕获观测数据。对于使用深度图像的策略，我们利用 [FastFoundationStereo](https://arxiv.org/abs/2512.11130) 从成对的红绿蓝 (RGB) 相机图像中生成干净的深度图（估算每个像素的距离），而不是依赖带噪声的物理深度传感器测量值。

[![The physical ToyBlocks setup with a robot arm, wooden blocks, and a camera](https://www.datocms-assets.com/64837/1793811059-image2.jpg?ts=ae95e598)](https://www.datocms-assets.com/64837/1793811059-image2.jpg?ts=ae95e598)

*物理 ToyBlocks 设置：机械臂、木质积木与相机。*

## 开放工具以推动后续研究

ToyBlocks 将数据生成、训练与评估整合在一个统一的受控环境中，使研究人员能够探究机器人如何随着时间推移进行学习，并测试模型或其训练数据的变化如何影响机器人的行为。我们正在开源仿真资产、程序化任务与演示生成器、自动生成的演示数据、两个展示该框架能力的已训练模型（一个基于 [Molmo 2](https://huggingface.co/allenai/Molmo2-4B-tb)，另一个基于 [ManiFlow](https://huggingface.co/allenai/maniflow-tb)）、训练代码以及评估代码和验证集。这使得其他团队能够构建自己的训练混合数据，并探索超出我们初始实验范围的故障模式。

我们最初发布的数据集是一个概念验证成果，包含 85,336 条长时程演示，根据集合不同，每条演示包含约 6–12 个技能动作演示。初始数据集涵盖了近 1,600 小时的机器人执行数据和 1.44 亿帧画面。在几周内，我们的目标是推出第二版发布，包含更大规模的数据集、更多技能以及更全面的基准评测。我们还将加入当前软件包中尚未包含的完全集成的强化学习训练功能。

ToyBlocks 的其他拓展方向包括配备力和触觉传感器的双臂操作与灵巧手，用于研究涉及频繁物理接触的运动和任务。我们还在探索与非结构化积木堆的交互，将其作为收集数据和研究新行为及任务如何通过交互涌现的一种手段。

*未来方向：基于强化学习的积木堆操作。*

*未来方向：双臂积木操作。*

通过 ToyBlocks，我们希望推动机器人学习科学向前发展，迈向机器人能够可靠地将所学知识应用到陌生任务和环境的未来。我们鼓励研究界探索 ToyBlocks 用于自己的科学研究，甚至以此为基础构建属于自己的 FoundationWorlds。

## 本文提及的模型 2

## 本文提及的数据集 1

## 本文提及的集合 1

该作者的更多文章

## StateBench: Testing how language models track state changes over long documents

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/652db071b62cf1f8463221e2/CxxwFiaomTa1MCX_B7-pT.png)

18

2026 年 11 月 3 日

## Can we trust LLMs to judge whether a research idea is novel?

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/652db071b62cf1f8463221e2/CxxwFiaomTa1MCX_B7-pT.png)

18

2026 年 10 月 27 日

### 社区讨论

![](https://huggingface.co/avatars/26fa040c7f334785b26ae42de24ab4dc.svg)

Entmarch

约 10 小时前

我很喜欢这个概念，我很想看看实际应用，我们如何将 AI 整合到 PLC 和 OBD 系统中，改造现有应用以获得利基收益

![](https://huggingface.co/avatars/ab7fc92bae0354165d3f9890ac7f5b0b.svg)

wookute221

约 7 小时前

selona 我很喜欢这个概念，我很想看看实际应用，我们如何将 AI 整合到 PLC 和 OBD 系统中，改造现有应用以获得利基收益

通过拖拽到文本输入框、粘贴或点击此处上传图像、音频和视频。

点击或粘贴此处上传图像

· [注册](https://huggingface.co/join?next=%2Fblog%2Fallenai%2Ftoyblocks) 或 [登录](https://huggingface.co/login?next=%2Fblog%2Fallenai%2Ftoyblocks) 发表评论


5

- [![](https://huggingface.co/avatars/ab7fc92bae0354165d3f9890ac7f5b0b.svg)](https://huggingface.co/wookute221)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/XcLxZc6CL6VO7tOlh0T0g.jpeg)](https://huggingface.co/SmokeyPete)
- [![](https://huggingface.co/avatars/35af30f8a3713e3eda81ac4b9be515f5.svg)](https://huggingface.co/arahul2k2)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/noauth/DPzSLPCg9RvVBvkD3Mcys.png)](https://huggingface.co/rapidum)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/67953e11098348e24ae7f316/ZNT-1c2NOyhugYrzK5Vyf.png)](https://huggingface.co/sebast242)

## 本文提及的模型 2

## 本文提及的数据集 1

## 本文提及的集合 1
