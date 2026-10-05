---
vendor: huggingface
title: 度量语音识别中的基准优化
original_title: Measuring benchmark optimization in speech recognition
url: https://huggingface.co/blog/asr-benchmark-optimization
date: 2026-06-10
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# 度量语音识别中的基准优化

公开的 voice AI 基准日益表明模型达到了人类水平。然而这些分数并不总能反映模型在真实世界中的表现。由于公开基准是开放且被广泛使用的，模型也可能针对测试本身被优化。它们的分数提升，可能是因为学到了基准特有的模式，而不是因为底层任务做得更好了。

原因之一是传统基准忽视了许多让语音系统可靠、自然、语境得体、实际有效的条件与品质。这正是我们最近在 [Real World VoiceEQ](https://huggingface.co/spaces/HumeAI/rw-voice-eq)、[Open-ASR Leaderboard](https://huggingface.co/blog/open-asr-leaderboard-private-data) 和 [Far-field ASR Leaderboard](https://huggingface.co/spaces/treble-technologies/ffasr) 中引入保留集（held-out sets）的原因：为了度量真实使用中更重要的方面。

然而，仅仅扩大测量范围并不能解决问题。这一现象有时被称为基准优化（benchmark optimization）或"benchmaxxing"，在机器学习领域常被讨论，但在语音识别中一直难以度量。

我们最新的研究引入三项测试来帮助量化它。我们评估了 11 个广泛使用的开源 ASR 模型，发现若干得分最高的系统会复现 [VoxPopuli](https://huggingface.co/datasets/facebook/voxpopuli) 英文和 [LibriSpeech](https://huggingface.co/datasets/openslr/librispeech_asr)（clean、other）数据集中的基准转写文本——即便音频与之矛盾、相关词已被静音、或音频同等支持两种不同的书写形式。

某些情况下，模型似乎不仅依赖"说了什么"，还依赖暗示它们正在被哪个基准测试的细微声学线索。结果，它们的分数高估了自己泛化转写语音的能力。

## 参考文本分歧（VoxPopuli 案例研究）

VoxPopuli 以含有大量转写错误著称（这也是 Artificial Analysis 发布[清理版](https://huggingface.co/datasets/ArtificialAnalysis/VoxPopuli-Cleaned-AA)的原因）。我们的共识分歧探测（consensus disagreement probe）测试当领先 ASR 模型遇到这些错误时会发生什么：*它们是准确转写音频内容，还是复现基准中错误的参考转写？*

为了规模化测试，我们使用一个由低音素错误率（PER）独立模型组成的集成。PER 衡量书面转写与音频中声音的接近程度，是模型转写忠实度的有用代理指标。集成结果可用于标记模型一致不同意基准参考转写的样本。然后我们把其中一部分标记样本与人工标注比对，以验证修正后的转写。

例如，一段 VoxPopuli 音频清晰包含 "Thank you, Mr. President"，但参考转写省略了 "Thank you"。我们测试的 11 个模型中有 6 个复现了基准的错误转写——给出"预期"答案，尽管它与音频矛盾。在真实音频上，格式也遵循同样模式：省略 "Thank you" 的模型同样复现基准的标点风格，写 "Mr" 不加点；而包含该可听短语的模型倾向写 "Mr." 带点。

当我们用新采集的欧洲议会录音声音或通用声音呈现同样内容时，这一行为往往减弱或消失。在下面的样例中，除一个模型外，所有模型在"新议会录音克隆"上都回归到忠实于音频的转写。这表明模型在响应有助于其识别基准归属的声学线索，从而产出与音频相悖的"预期"转写。

该片段的参考转写是 "Mr President, I have another complaint about this procedure, which is that it is not secret."。下面三段音频实际说的都是同一句话，前面有一个可听的 "Thank you,"——克隆版本是该真实句子的文本转语音演绎，因此三段的礼貌语都可听。绿色高亮加 ✅ 标记包含可听 "Thank you" 的转写；红色高亮加 ❌ 标记复现基准错误省略的转写。所有转写都是模型原始输出、未经任何规范化——大小写和标点完全按生成原样保留，包括某些模型的全小写输出。

**Original VoxPopuli recording**

**Voice clone of the same speaker**

**Clone of a parliament speaker recorded after every model's training cutoff**

| Model | Real clip | Same-speaker clone | ep-fresh clone |
| --- | --- | --- | --- |
| [CohereLabs/cohere-transcribe-03-2026](https://huggingface.co/CohereLabs/cohere-transcribe-03-2026) | ❌ Mr President… | ❌ Mr President… | ✅ Thank you, Mr President… |
| [nvidia/canary-qwen-2.5b](https://huggingface.co/nvidia/canary-qwen-2.5b) | ❌ Mr President… | ❌ Mr President… | ✅ Thank you Mr. President… |
| [ibm-granite/granite-speech-4.1-2b](https://huggingface.co/ibm-granite/granite-speech-4.1-2b) | ❌ mr president… | ❌ mr president… | ✅ thank you mr president… |
| [microsoft/Phi-4-multimodal-instruct](https://huggingface.co/microsoft/Phi-4-multimodal-instruct) | ❌ Mr President… | ❌ Mr President… | ❌ Mr President… |
| [nvidia/parakeet-tdt-0.6b-v2](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2) | ❌ Mr President… | ✅ Thank you, Mr President… | ✅ Thank you, Mr. President… |
| [bosonai/higgs-audio-v3-8b-stt-v2](https://huggingface.co/bosonai/higgs-audio-v3-8b-stt-v2) | ❌ mr president… | ❌ mr president… | ✅ thank you mr president… |
| [Qwen/Qwen3-ASR-0.6B-hf](https://huggingface.co/Qwen/Qwen3-ASR-0.6B-hf) | ✅ Thank you, Mr. President… | ✅ Thank you, Mister President… | ✅ Thank you, Mister President… |
| [mistralai/Voxtral-Mini-3B-2507](https://huggingface.co/mistralai/Voxtral-Mini-3B-2507) | ✅ Thank you, Mr. President… | ✅ Thank you, Mr. President… | ✅ Thank you, Mr. President… |
| [moonshotai/Kimi-Audio-7B-Instruct](https://huggingface.co/moonshotai/Kimi-Audio-7B-Instruct) | ✅ Thank you, mr. President… | ✅ Thank you, Mr. President… | ✅ Thank you, mr. President… |
| [openai/whisper-large-v3](https://huggingface.co/openai/whisper-large-v3) | ✅ Thank you, Mr. President… | ✅ Thank you, Mr. President… | ✅ Thank you, Mr. President… |
| [moonshine-ai/moonshine-streaming-medium](https://huggingface.co/moonshine-ai/moonshine-streaming-medium) | ✅ thank you mr president… | ✅ thank you mr president… | ✅ thank you mr president… |
| **Drops the courtesy (❌) out of 11** | **6** | **5** | **1** |

Parakeet 是唯一一个在真实音频上复现基准、在同说话人克隆上却答对的模型。Phi-4 是唯一在 ep-fresh 克隆上仍丢掉礼貌语的模型。而当我们改用与任何议会录音无关的通用 TTS 声音重新合成该句时，全部 11 个模型都恢复了礼貌语。

结果表明这一问题既普遍又影响显著。我们的方法在我们分析的 40% VoxPopuli 测试片段中标记出潜在的参考错误，影响约 3% 的全部参考词。

表现出基准优化行为的模型有 18-30% 的概率复现错误的参考转写。下方散点图以 VoxPopuli 词错误率（WER）为 x 轴，以每个模型复现基准错误参考而非共识修正的比率为 y 轴。WER 最低——即公开报告成绩最强——的模型，恰恰最可能复现这些错误。

## 被掩实体召回

在共识分歧探测的基础上，我们刻意将测试数据集音频样本中的数字静音，再让模型转写它听到的内容。数字在音频中字面缺失，模型不应输出任何数字，更不用说文本中的那个精确数字。

其中一些数字是半可预测的（虽然模型仍不太可能猜对），另一些则相当意外。以下片段结合两种探测，展示模型如何复现参考转写错误——包括一个错误数字，甚至有一个模型在被静音的情况下自动补全了相对随机的年份（2011）。在下面每个模型的行中：

- 绿色高亮加删除线标记模型正确地未复现的参考转写词（忠实于音频）；
- 绿色高亮加下划线标记用忠实于音频的正确内容替换了参考的错误措辞；
- 红色高亮（普通文本）复现了参考转写中错误、无音频支撑的内容：保留 "Mr President"、在音频说 "one thousand six hundred" 处写 "more than 1 amendments"、补出被静音的年份 "2011"，或以 "plenary" 结尾。

**2011 draft budget (masked numbers)**

| Reference | Mr President, in the Committee on Budgets, we voted on more than 1 amendments to the 2011 draft budget … voted in the plenary. |
| --- | --- |
| What the audio says | In the Committee on Budgets, we voted on more than one thousand six hundred amendments to the ⟨silenced⟩ draft budget … voted in the … |
| [CohereLabs/cohere-transcribe-03-2026](https://huggingface.co/CohereLabs/cohere-transcribe-03-2026) | Mr President, in the Committee on Budgets we voted on more than 1 amendments to the 2011 draft budget … voted in the plenary. |
| [nvidia/canary-qwen-2.5b](https://huggingface.co/nvidia/canary-qwen-2.5b) | Mr President, in the Committee on Budgets we voted on more than one amendments to the 2011 draft budget … voted in the plenary |
| [ibm-granite/granite-speech-4.1-2b](https://huggingface.co/ibm-granite/granite-speech-4.1-2b) | Mr President in the committee on budgets we voted on more than one thousand six hundred amendments to the 2011 draft budget … voted on in the plenary |
| [microsoft/Phi-4-multimodal-instruct](https://huggingface.co/microsoft/Phi-4-multimodal-instruct) | Mr President In the Committee on Budgets we voted on more than 1 amendments to the 2011 draft budget … voted on in the plenary. |
| [nvidia/parakeet-tdt-0.6b-v2](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2) | Mr President In the Committee on Budgets we voted on more than one amendments to the 2011 draft budget … voted in the Protestants. |
| [bosonai/higgs-audio-v3-8b-stt-v2](https://huggingface.co/bosonai/higgs-audio-v3-8b-stt-v2) | Mr President in the committee on budgets we voted on more than one thousand six hundred amendments to the 2011 draft budget … voted in the plenary |
| [Qwen/Qwen3-ASR-0.6B-hf](https://huggingface.co/Qwen/Qwen3-ASR-0.6B-hf) | Mr President In the Committee on Budgets, we voted on more than 1,600 amendments to the 2011 draft budget … voted in the plenary |
| [mistralai/Voxtral-Mini-3B-2507](https://huggingface.co/mistralai/Voxtral-Mini-3B-2507) | Mr President In the Committee on Budgets, we voted on more than 1,600 amendments to the 2011 draft budget … voted in the plenary |
| [moonshotai/Kimi-Audio-7B-Instruct](https://huggingface.co/moonshotai/Kimi-Audio-7B-Instruct) | Mr President Ah in the committee on budgets we voted on more than one thousand six hundred amendments to the 2011 draft budget … voted in the plenary |
| [openai/whisper-large-v3](https://huggingface.co/openai/whisper-large-v3) | Mr President In the Committee on Budgets, we voted on more than 1,600 amendments to the 2011 draft budget … voted in the plenary |
| [moonshine-ai/moonshine-streaming-medium](https://huggingface.co/moonshine-ai/moonshine-streaming-medium) | Mr President in the committee on budgets we voted on more than one thousand six hundred amendments to the 2011 draft budget … voted in the plenary |

恢复率在公开基准上最高，在保留或新采集音频（下文 ep-fresh 与 libri-fresh）上更低。在 LibriSpeech 上，一些基准表现最强的模型在约 30-40% 的样本中复现了被静音的数字——尽管数字本身已被移除。对若干模型而言，该效应在新采集数据上减弱，说明与基准相关联的周边音频（而不只是文本自动补全）帮助模型找回了参考内容。

## 拼写切换

我们的拼写切换探测测试模型是否在音频中无法分辨的情况下，仍复现基准参考转写使用的精确拼写。正字法变体是语义与发音相同、但拼写可以不同的词（1 vs one、Mr. vs mister、John vs Jon、Honor vs Honour 等）。理论上，模型应一致地偏好某一种拼写，或以大致随机的比率交替使用。如果模型系统性地切换到与各基准参考转写一致的拼写，就说明模型察觉到了测试期望哪种拼写。

**Transcription: "I URGED ON THE BOYS THAT WHATEVER HAPPENED WE SHOULD NOT SHOOT ANY ONE" — models using "any one": 6/11, models using "anyone": 5/11**

**Transcription: "CAMOUFLAGE WAS NOT A WORD THE CAPTAIN OR ANYONE ELSE OF HIS TIME YET UNDERSTOOD" — models using "any one": 2/11, models using "anyone": 9/11**

在 LibriSpeech 内部，我们测试一种涉及旧式空格习惯的*数据集内*切换：一些参考转写用 "any one"，另一些用 "anyone"。我们测量针对给定变体的最低准确率，称之为"切换率"。若模型只用一种变体，切换率为 0%；随机选择的模型预期为 50%；能在每个测试样本都选对变体的模型可得 100%。

第二个探测测试*跨数据集切换*：每个基准在其整个测试语料中一致使用不同的拼写习惯。例如，VoxPopuli 用缩写 "Mr."，而 LibriSpeech 拼出 "Mister"。

多个模型超过 50% 的随机基线，有的切换准确率约达 90%。**这表明模型能识别音频样本来自哪个数据集，并选用该基准期望的拼写习惯——尽管两种形式听起来完全相同。**

## 定位切换的来源

为了测试这些行为能否泛化到公开基准之外，我们还从相同来源领域、但在模型训练截止日期之后采集了新数据：VoxPopuli 用近期欧洲议会录音，LibriSpeech 用新活跃的 LibriVox 朗读者。然而，当面对同领域新采集的数据时，许多模型不再匹配参考转写，而是回归更忠实于音频的转写。

其他干预手段也指向同样结论。音频中存在但参考转写遗漏的短语，在要求模型翻译音频、或把其注意力限制到相关帧时可能重新出现。裁掉周边基准上下文，或附加普通会话音频，也能恢复忠实转写。而附加 VoxPopuli 音频则可能产生相反效果，让原本忠实的合成或挖掘样本更倾向匹配基准参考。

**总之，这些结果表明模型能够忠实转写字面的口语内容，但在利用周边声学上下文来决定是跟随音频，还是跟随某个基准特有的转写策略。**

## 结论

我们的发现表明，在两大开源数据集上，一些模型能检测到与数据集关联的声学线索并相应调整转写行为。具体而言，模型可能复现音频中不存在但参考转写中存在的词、以更高比率找回被静音的数字，或利用周边声学上下文选择某个基准期望的书写变体。

对选择模型的人来说，这些发现强调了使用完全保留的评估集（如 RW-Voice-EQ Bench 和 Open ASR Leaderboard 所做的那样）、以及不要只盯着单一公开基准词错误率的重要性。为此，[Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard) 新增了 "Benchmark fitting" 标签页，对所有模型纳入上述两项分析：量化 (1) VoxPopuli 参考错误率，(2) 跨全部公开数据集的拼写切换。相关脚本已在 [GitHub](https://github.com/huggingface/open_asr_leaderboard/tree/main/benchmark_fitting) 开源，[未规范化的模型输出](https://huggingface.co/buckets/hf-audio/asr_leaderboard_h200)亦然。

我们的发现还建议：基准开发者应避免简单的独立同分布测试划分，改用按时间、说话人或其他元数据的分离。对训练数据和模型选择流程做更高透明度，也能帮助研究者理解这些行为如何产生。

公开基准仍然宝贵：透明、可重复、易于运行、且被研究社区充分理解。但只有当我们能区分真实的转写改进与无法泛化到新音频的基准特有增益时，它们才最有价值。

更多信息，推荐阅读我们的[完整报告](https://huggingface.co/papers/2608.19936)。

## 文中提到的模型 10

## 文中提到的数据集 3

## 文中提到的 Spaces 3

## 文中提到的论文 1

我们博客的更多文章

audio

speech

leaderboard

## The Open ASR Leaderboard Adds Its First Global South Language

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6384db7fb2906edaf835a91d/MOTXxaOmjlTZ8wONYifnD.jpeg)
- ![](https://huggingface.co/avatars/82ecee27d4b68fd5df3d3b3506600e7a.svg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/67bc3e2f4b9d3615a6e2c982/8x33LQ0fwbnUtIn9CAwv2.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6673251287330d7378e6b5e3/VVvuAsOUMiAPNgsdoRZjM.png)
- +6

60

2026 年 8 月 28 日

audio

speech

benchmark

## Introducing Real World VoiceEQ: Measuring the human quality of voice AI

- ![](https://huggingface.co/avatars/e5663d6740afc5aa42d6cfb6360ef084.svg)
- ![](https://huggingface.co/avatars/a7a92c5f9e01577dd7bcebe5a345f2f7.svg)
- ![](https://huggingface.co/avatars/5ddb29b461d38a9edc9a985fd15ce534.svg)
- ![](https://huggingface.co/avatars/62e4f62d21f3ad9b314819f9c45161d3.svg)
- +9

34

2026 年 7 月 15 日

### 社区

Abc-123-Xy

Aug 22

nice

CA111AKO111MAP

Aug 22

nice paper

将文件拖入文本输入框、粘贴，或

点击此处

，即可上传图像、音频和视频。

点击或粘贴此处上传图片

· [注册](https://huggingface.co/join?next=%2Fblog%2Fasr-benchmark-optimization)或[登录](https://huggingface.co/login?next=%2Fblog%2Fasr-benchmark-optimization)发表评论

点赞

68

- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6384db7fb2906edaf835a91d/MOTXxaOmjlTZ8wONYifnD.jpeg)](https://huggingface.co/bezzam)
- [![](https://huggingface.co/avatars/a7a92c5f9e01577dd7bcebe5a345f2f7.svg)](https://huggingface.co/aliceebaird)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/r6F20gfbuflBGbpmMZ7e7.png)](https://huggingface.co/sharath25)
- [![](https://huggingface.co/avatars/b920256b1688b73ce1b889ac53594110.svg)](https://huggingface.co/tlebryk02)
- [![](https://huggingface.co/avatars/821e66bd12e82026f786d0a1eef9811d.svg)](https://huggingface.co/aluko26)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/697299e19695fae39c520649/y3-bbcHl-iTO1fwKurxkB.jpeg)](https://huggingface.co/0bserverx)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/AIasly97s2SiP4-4MSPDA.png)](https://huggingface.co/meharpsingh)
- [![](https://huggingface.co/avatars/d0010ed32ae04727528ce0b500a1a8f5.svg)](https://huggingface.co/out51der)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/no-auth/3rZ01yvs5yE0WzxsYFkXP.png)](https://huggingface.co/lalzuai)
- [![](https://huggingface.co/avatars/30c19d48a1c5e20462eed58884908b2b.svg)](https://huggingface.co/myian0211)
- [![](https://cdn-avatars.huggingface.co/v1/production/uploads/6a30495b901a5b1643c876f2/gUbDd5mrUJXM1WLXp9444.jpeg)](https://huggingface.co/Aditya172003)
- [![](https://huggingface.co/avatars/1723bf6d3e639abec11d7361574eca96.svg)](https://huggingface.co/zahrarabiee)

## 文中提到的模型 10

## 文中提到的数据集 3

## 文中提到的 Spaces 3

## 文中提到的论文 1
