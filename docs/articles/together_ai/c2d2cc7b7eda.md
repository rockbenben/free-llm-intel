---
vendor: together_ai
title: Distilling Kimi-K3.1-Pro into Qwen3.8-27B: Teaching a model a new language
original_title: 
url: https://www.together.ai/blog/distilling-kimi-into-qwen
date: 2026-11-26
lang: zh
captured: 2026-11-27
extractor: readability-v1
translator: mt
status: translated
body_sha: 8e5e219651fc
---

所有博客文章

模型塑造

发表于 11/26/2026

# 将 Kimi-K3.1-Pro 提炼为 Qwen3.8-27B：教授模型一种新语言

当我们询问老挝语时，Qwen3.8-27B 用泰语回答。我们通过Together Post-Training将Kimi-K3.1-Pro的老挝语翻译提炼出来，达到了老师评分的93%，泰语完好无损。

- 作者扎因·哈桑 (Zain Hasan)、桑尼·汗 (Sonny Khan)
- 目录[40+ 型号选择用于生产...40+ 型号选择用于生产...40+ 型号选择用于生产...](https://www.together.ai/blog/distilling-kimi-into-qwen)
- 本文中的链接[GitHub 上的蒸馏食谱](https://github.com/togethercomputer/post-training-cookbook/tree/main/post_training_cookbook/distillation)[一起训练后](https://www.together.ai/post-training)[Qwen3.8-27B](https://www.together.ai/models/qwen3-8-27b)[Kimi-K3.1-Pro](https://www.together.ai/models/kimi-k3-1-pro)

总结

- **差距：** 当被问及老挝语时，Qwen3.8-27B 用泰语回答，得分为 5.5 chrF++，而 Kimi-K3.1-Pro 在同一测试中得分为 47.5。
- **修复：** 我们使用 Together Post-Training 在大约 3,800 个 Kimi-K3.1-Pro 的翻译上训练了一个 LoRA 适配器。
- **结果：** 学生在每个测试句子上都写上了老挝语，得分为 44.3，是老师得分的 93%，并且保留了泰语。
- **成本：** 所有实验总共花费 260 美元，代码位于训练后食谱中。

在进行一些实验时，我们发现最流行的小语言模型 (SLM) 之一的 [Qwen3.8-27B](https://www.together.ai/models/qwen3-8-27b) 无法书写老挝语，这是一种西南泰语，也是老挝的官方语言。如果你要求它把一个英语句子翻译成老挝语，它会用泰语回答，泰语是老挝语的近亲，它使用完全不同的文字。在 [FLORES-200](https://huggingface.co/datasets/Muennighoff/flores200) 老挝语测试集上，该模型得分为 5.5 chrF++，即翻译与人类参考的匹配程度为 0 到 100 分，并且其输出中只有 11% 采用老挝文字。 [Kimi-K3.1-Pro](https://www.together.ai/models/kimi-k3-1-pro) 在同一测试中得分 47.5。

诚然，这是一个小众用例，但这种模式很常见：小型语言模型显示参差不齐的智能，在您关心的狭窄任务上表现不佳，而更大、更昂贵的模型则可以轻松处理它。为了解决这个问题，我们使用 Kimi-K3.1-Pro 作为教师，并使用 Together Post-Training 将其老挝语翻译能力提炼为 Qwen3.8-27B。

在对 Kimi-K3.1-Pro 的约 3,800 个翻译进行训练后，27B 学生对每个测试句子都用老挝语作答，得分为 44.3，是老师得分的 93%。它还保留了泰语翻译能力，有趣的是，这是最难的部分。我们的第一次尝试在 25 个训练步骤内修复了老挝语，但也随之失去了泰语翻译能力。

这篇文章将介绍我们如何发现差距以及最终的效果。代码、设置和成本在后半部分。所有实验总共花费 260 美元。

![基础学生、精炼学生和 Kimi-K3.1-Pro 教师的老挝语和泰语 chrF++ 条形图。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b0765fc996c2110eb55182f_kimi-qwen-distillation-headline.png)

学生从写泰语到写老挝语，达到了老师分数的 93%，并且没有失去泰语能力。

## 寻找差距

![Kimi-K3.1-Pro 和 Qwen3.8-27B 11 种语言的 chrF++ 条形图，老挝语差距最大。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b0766387f6debb78af8c6fe_kimi-qwen-distillation-screen.png)

Kimi-K3.1-Pro 在所有 11 种语言上都击败了 Qwen3.8-27B。老挝目前差距最大（49.0 比 7.2）。

我们使用的指标是 chrF++，它对字符和单词与人工参考翻译的重叠进行评分，从 0 到 100。要了解 Qwen 老挝语分数较低的重要一点是，对于 chrF++，泰语答案与老挝语参考几乎没有任何共同点。当要求翻译成老挝语时，学生的输出 50 个句子中有 45 个包含泰语文字，而仅 6 个句子包含老挝语：

> 中文：“我们现在有 4 个月大的老鼠，它们以前患有糖尿病，但现在没有患糖尿病，”他补充道。 Qwen3.8-27B（基础）：“我们现在有 4 个月大的小鼠，它们以前患有糖尿病，但现在没有糖尿病，”他补充道。

基本模型的泰语是一个合理的翻译，只是语言错误。我们将在结果中再次讨论这一点。

关于数字的一点说明：在这 50 个句子中，Qwen3.8-27B 的 Lao 得分为 7.2，Kimi-K3.1-Pro 的得分为 49.0，而在完整的 1,012 个句子测试集上，老挝得分为 5.5 和 47.5。测试集列在“我们如何构建它”下。

## 计划：离策略蒸馏

蒸馏训练一个小模型（学生）在给定领域表现得像一个大模型（老师）。有两种方法可以做到这一点。

**按策略蒸馏 (OPD)**，在 Thinking Machines 的[关于该主题的帖子](https://thinkingmachines.ai/blog/on-policy-distillation/) 中进行了描述，让学生生成文本，教师对每个标记进行评分。它需要教师对学生标记的对数概率，这实际上意味着两个模型必须共享标记生成器。由于我们将 Kimi 提炼成 Qwen 并且它们不共享标记器，所以我们走了另一个方向。

**离策略蒸馏**让教师生成文本并训练学生通过监督微调 (SFT) 来模仿它。最简单的形式只需要老师的课文。

我们使用了离策略蒸馏。它使教师端相当便宜：每个教师呼叫都是普通的无服务器聊天请求，而 Kimi-K3.1-Pro 是一个相当大的模型，从不需要自己的训练资源。

![从英语句子到经过训练的 LoRA 适配器的蒸馏管道图。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b0766643280c184bf4a8f03_kimi-qwen-distillation-pipeline.png)

端到端管道：英语句子进入 Kimi-K3.1-Pro，经过过滤，并成为 Together Post-Training 模型资源上 Qwen3.8-27B LoRA 会话的 SFT 行。

步骤：

- 收集英语源句子。
- 让 Kimi-K3.1-Pro 翻译它们，关闭思维。
- 删除主要不在目标脚本中的任何翻译。
- 以翻译为目标，在 Qwen3.8-27B 上微调 LoRA 适配器，在训练时评估保留的测试句子。
- 将适配器保存到模型注册表中。

我们对学生进行了“共同后期培训”培训。一种模型资源既可以训练 LoRA 适配器，也可以训练其中的样本，因此我们可以在模型训练时对其进行评分。我们根据四个指标对每个评估进行评分：

- chrF++ 与 FLORES-200 开发测试中的人类参考相比：每次运行开始和结束时的所有 1,012 个句子，每 25 个步骤 300 个句子（两次最长运行中的每 50 或 100 个句子）。
- 老挝文字率：字母主要为老挝文字的输出所占的比例。这直接抓住了泰国问题。
- 泰语保留：对 300 个英语到泰语的测试句子进行 chrF++，以检查模型是否丢失了已有的语言。
- 往返充分性：Kimi-K3.1-Pro 将每个系统的老挝语翻译回英语，我们根据原始英语进行评分。这可以独立于参考风格来检查含义。

保留泰语的同时获得老挝语翻译能力最终成为最棘手的部分。

## 泰国的惊喜

一次运行是一个对照：它以老挝人类参考资料为基础进行训练，其中 945 个来自 FLORES 开发人员，没有老师参与。 Lao 在 25 步内从 6.7 跃升至 43.3。

然后我们看泰语。它从 46.7 下降到 11.7，到运行结束时为 5.3，其中 0% 的泰语输出采用泰文。该模型学会了“在要求翻译时写老挝语”，而不是“写您被要求翻译的语言”。问题已经改变方向了。

![英语到泰语 chrF++ 与每次运行的训练步骤的折线图。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b07668c58205941917537cb_kimi-qwen-distillation-thai-chrf.png)

英语到泰语 chrF++ 300 个测试句子。仅对老挝人进行训练就可以让泰语崩溃；混合运行保留它。

如果我们单独评估老挝，这次比赛看起来会是胜利者。它在这篇文章中的所有学生中获得了最高的老挝语分数。

## 修复泰语

仅限老挝的蒸馏运行在 Kimi-K3.1-Pro 的相同句子翻译上进行训练，以代替人类翻译。这大大减缓了损害，但并没有阻止它。泰语保持了两个时期，然后在第三个时期滑落至 44.3，300 个泰语答案中有 17 个是用老挝语写的。

在训练数据中添加大约 1,000 个 Kimi-K3.1-Pro 泰语翻译修复了这个问题。 Thai 在两次混合运行中的得分分别为 47.4 和 47.8，高于基本模型，并且在任何评估中从未低于 47.3。

![图表比较每种训练组合在询问老挝语和泰语时所写的语言。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b0766965800a95e7276e19d_kimi-qwen-distillation-forgetting.png)

当您要求老挝语和泰语时，每种培训组合会做什么。

这是关于持续学习的一个重要观点：当你教一个模型一些新的东西时，混合数据来保护它已经做得很好的东西，这样你就不会在你关心的事情上出现回归。这是泰语，最容易与老挝语混淆的语言。

## 缩小老挝的其余差距

泰国是安全的，但老挝仍然短缺。每个老挝语示例约有 950 个，接受人类参考训练的学生得分为 44.7，两名精炼学生得分为 41.8 和 41.9。

其中一部分是预期的。人类参考在人类参考指标上做得更好：FLORES dev 和 devtest 是通过相同的人工流程进行翻译的，因此对 dev 的培训会教授 devtest 的参考风格。精炼的学生反而学习了老师的风格。根据 Kimi-K3.1-Pro 自己的翻译进行评分，经过蒸馏的学生从 8 分上升到 58 chrF++，而接受人类参考训练的学生则达到 47 分。

另一个区别是供应。 FLORES dev 拥有 997 条人类参考文献，仅此而已，而 Kimi-K3.1-Pro 可以翻译您拥有的任何英文文本。添加 3,000 个维基百科句子的翻译后，老挝语训练集的示例数量从 965 个增加到 3,834 个，并将老挝语得分从 41.9 提高到 44.3。这与人类参考运行相差不到半点，泰语完好无损。

更多数据也击败了更多传递：4× 数据的一个 epoch 在 300 个测试句子上达到了 43.2，而较小的 Lao + Thai 集的 3 个 epoch 后达到了 41.3。

![四次训练运行中英语到老挝语 chrF++ 与 SFT 步骤的折线图，教师为虚线。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b0766a1cea7d11c54618f09_kimi-qwen-distillation-lao-chrf.png)

英语到老挝语 chrF++，针对四次训练运行的 300 个测试句子，针对 SFT 步骤。虚线就是老师。

＃＃ 结果

|运行|训练数据|老挝chrF++ |老挝文字 |泰语 chrF++ |
| ---| ---| ---| ---| ---|
|基地学生|无 | 5.5 | 5.5 11% | 46.7 | 46.7
| SFT 人类参考文献 | 945 人工老挝语翻译 | 44.7 | 44.7 100% | 5.3 |
|仅限老挝蒸馏 | 965 Kimi-K3.1-Pro 老挝语 翻译 | 41.8 | 41.8 100% | 44.3 | 44.3
|老挝+泰国蒸馏酒| 965 老挝语 + 989 泰语，来自 Kimi-K3.1-Pro | 41.9 | 41.9 100% | 47.4 | 47.4
|蒸馏，老挝+泰语，4×老挝数据| 3,834 老挝语 + 989 泰语，来自 Kimi-K3.1-Pro | 44.3 | 44.3 100% | 47.8 | 47.8
| Kimi-K3.1-Pro老师| - | 47.5 | 47.5 100% | 49.9 | 49.9

老挝数字使用了全部1012个测试句子，泰语使用了300个。最好的成绩达到了老师分数的93%。从基础模型开始的地方开始衡量，它缩小了老挝语 92% 的基础与教师差距：

$$\text{间隙闭合} = \frac{s_{\text{学生}} - s_{\text{base}}}{s_{\text{老师}} - s_{\text{base}}} = \frac{44.3 - 5.5}{47.5 - 5.5} = 0.92$$

**基本模型主要有含义；它只是写了错误的语言。** 记住老鼠的例子。在往返充分性方面，基本模型的泰语输出得分为 64.6，略高于人类老挝参考值 (64.0)。这位蒸馏生的成绩为65.7，并在100%的测试句子上写出了老挝语。所以主要的差距是语言同一性，这就是为什么每次运行都通过第一次评估（25 或 50 个步骤）来修复脚本。

![根据训练步骤用老挝文字编写的老挝语答案所占比例的折线图。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b0766acfba479086057a0a8_kimi-qwen-distillation-lao-script.png)

分享用老挝文字写的老挝答案。每次运行都会通过第一次评估来修复脚本。

损失曲线、代币计数和每次运行的详细信息可以在附录中找到。

## 五种语言培训

为了检查这是否不是老挝特有的，我们用老挝语、北索托语和祖鲁语（三个最大的差距）以及约鲁巴语（两种模型中得分最低的拉丁文字语言）训练了一个适配器，并用泰语进行保留：总共 8,871 个 Kimi-K3.1-Pro 翻译，每种语言约 2,000 个，泰语约 1,000 个，超过 831 个步骤。

![基础学生、蒸馏适配器和 Kimi-K3.1-Pro 五种语言的 chrF++ 条形图。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b0766d45a7d2ce6e9d023e3_kimi-qwen-distillation-multilingual.png)

一款经过精炼的适配器可改进老挝语、北索托语、约鲁巴语和祖鲁语，并保持泰语性能。

|语言 |基地学生|蒸馏| Kimi-K3.1-Pro |差距已缩小|
| ---| ---| ---| ---| ---|
|老挝 | 5.5 | 5.5 41.8 | 41.8 47.5 | 47.5 87% |
|北索托 | 32.7 | 32.7 48.0 | 48.0 50.7 | 50.7 85% |
|约鲁巴语 | 20.7 | 20.7 25.7 | 25.7 27.7 | 27.7 71% |
|祖鲁语 | 37.7 | 37.7 39.2 | 39.2 50.3 | 50.3 12% |
|泰语 | 46.7 | 46.7 48.0 | 48.0 49.9 | 49.9改进|

Lao 出现在全部 1,012 个测试句子中；其余的人用300分，老师对同样的句子打分。每种语言都有进步。 Zulu 改进最少：在训练期间，其输出的 1% 到 2% 陷入重复循环，因此更多 Zulu 数据或重复惩罚是我们首先尝试的事情。

## 如果你有这样的差距

这是我们再次要做的事情：

- 首先筛选。每种语言五十句就足以看出老师遥遥领先的地方。
- 在训练之前看看基础模型出了什么问题。这里的意思就在那里，但语言是错误的，这就是为什么脚本被修复在前 25 到 50 个步骤内。
- 当学生达到稳定水平时，在添加纪元之前生成更多教师数据。
- 混合您想要保留的附近技能的数据，并在训练期间对其进行评分。仅针对老挝的评估会选择打破泰国的比赛为最佳比赛。

## 我们如何构建它

这篇文章的其余部分是操作方法：教师数据、训练循环、设置、测试集和成本。

### 使用无服务器 Kimi-K3.1-Pro 生成教师数据

每一次老师的通话都是一次普通的聊天完成，思维被关闭。翻译不需要长推理：经过思考，Kimi-K3.1-Pro 在 300 个老挝语测试句子上得分较低（43.5 对 47.3），并且使用了大约 8 倍的标记。关闭此选项后，老挝语答案平均约为 175 个输出标记。

```
from together import Together

client = Together()
resp = client.chat.completions.create(
    model="moonshotai/Kimi-K3.1-Pro",
    messages=[{"role": "user", "content": (
        "Translate the following English text into Lao. "
        "Output only the Lao translation, with no explanation.\n\n" + english
    )}],
    max_tokens=1024,
    temperature=0.0,
    chat_template_kwargs={"thinking": False},
)
lao = resp.choices[0].message.content
```

源文本是 FLORES-200 **dev** 的 997 个句子，加上英语维基百科的 4,000 个句子（老挝语 3,000 个，泰语 1,000 个）。

关于数据，有两件事值得了解：

- 从老师那里生成数据很便宜。 Kimi-K3.1-Pro 无服务器成本为每百万输入代币 2 美元，每百万输出代币 10 美元。所有 4,000 份老挝语翻译总共花费 7.46 美元。
- 训练前过滤。只有当至少 70% 的字母符合目标脚本并且不是英语的回声时，我们才会保留翻译。过滤器去除了 Kimi-K3.1-Pro 的 4% 的老挝。

每个幸存的翻译都会成为一个聊天格式的训练行：

```
{"messages": [
  {"role": "user", "content": "Translate the following English text into Lao. Output only the Lao translation, with no explanation.\n\n<English sentence>"},
  {"role": "assistant", "content": "<Kimi-K3.1-Pro's Lao translation>"}
]}
```

### 对学生进行培训后的 Together 培训

训练后一起在代码和 GPU 之间分割训练运行。 **模型资源**是一组加载了基本模型的 GPU（此处为 B200）。它有一个运行 `forward_backward` 和 `optim_step` 的 **trainer**，以及一个可选的 **generator**，用于从中间检查点采样文本。 **会话** 是针对该资源的一次 LoRA 适配器培训。

![笔记本电脑和模型资源之间的一个训练步骤图。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b0766deb889746147db68c7_kimi-qwen-distillation-step.png)

一个训练步骤：笔记本电脑构建样本并发送它们；模型资源计算损失、应用优化器步骤和用于评估的样本。

我们将食谱用于三件事：

- `get_codec("Qwen/Qwen3.8-27B", enable_thinking=False)` 使用 Qwen 自己的模板呈现每个聊天。
- `build_conversation_samples` 屏蔽提示（损失权重 0）并仅训练助手的翻译（权重 1），包括回合结束标记，以便模型学习何时停止。
- `build_cross_entropy_sample` 将令牌转移到 API 期望的下一个令牌目标。

```
from together import Together
from together.post_training import (AdamParams, LoraConfig, LossConfig,
                                    ModelResourcesClient, SamplingParams)
from post_training_cookbook.codecs import get_codec
from post_training_cookbook.samples import make_prompt
from post_training_cookbook.sft.train import TRAIN_ON_LAST, build_conversation_samples

codec = get_codec("Qwen/Qwen3.8-27B", enable_thinking=False)
samples = [s for row in rows for s in build_conversation_samples(
    row["messages"], codec=codec, train_on_what=TRAIN_ON_LAST, max_length=2048)]

# One resource with one generator replica: train and evaluate on the same resource.
raw = Together().post_training.model_resources.create(
    base_model="Qwen/Qwen3.8-27B", lora_enabled=True,
    compute_config={"gpu_type": "B200-SXM", "num_generator_replicas": 1},
    extra_body={"inactive_timeout": 1200})
record_in_ledger(raw.id)            # before waiting, so a crash can't leak it
wait_until_ready(raw.id)            # about 4 to 5 minutes for us
resources = ModelResourcesClient.attach(model_resources_id=raw.id)
session = resources.create_session(lora_config=LoraConfig(rank=64, alpha=128))

for step in range(total_steps):
    batch = next_batch(samples, size=16)
    session.trainer.forward_backward(samples=batch,
                                     loss=LossConfig(type="LOSS_TYPE_CROSS_ENTROPY"))
    session.trainer.optim_step(adam_params=AdamParams(learning_rate=lr_at(step)))

    if (step + 1) % 25 == 0:
        session.trainer.weights_sync()              # publish new weights to the generator
        outs = session.generator.sample_batch(
            [make_prompt(codec.encode_messages(m, add_generation_prompt=True)) for m in test_prompts],
            num_samples=1, sampling_params=SamplingParams(max_tokens=1024, temperature=0.0))
        score(outs)

checkpoint = session.create_inference_checkpoint()  # registers the adapter (ml_...)
```

`record_in_ledger`、`wait_until_ready`、`next_batch`、`lr_at` 和 `score` 是我们的小帮手。

设置为：

- LoRA 排名 64（Qwen3.8-27B 的最大值）和 alpha 128
- 峰值学习率 1e-4，5% 预热和余弦衰减至峰值的十分之一
- 批量大小 16

因为资源有一个生成器，所以我们不需要部署单独的端点来评估。

### 测试集

您会看到同一模型在不同地方的得分略有不同，因为我们对三组 FLORES-200 句子进行了评分：

|切片|用于 |老挝基地|劳老师|
| ---| ---| ---| ---|
|每种语言 50 个句子 | 11 种语言屏幕 | 7.2 | 49.0 | 49.0
| 300 条开发测试句子 |培训期间的评估，泰语| 6.7 | 6.7 47.3 | 47.3
|所有 1,012 个开发测试句子 |每次运行的开始和结束，以及标题结果 | 5.5 | 5.5 47.5 | 47.5

FLORES-200 **开发测试**从未用于训练。我们始终将其作为测试集。

### 时间和成本

假设在 B200 上进行训练，本文中的所有实验总共花费 260 美元。教师数据是最便宜的部分：所有 4,000 份老挝语翻译的价格为 7.46 美元。

至于时间，每次跑步的第一步需要2.5到3分钟。此后，第 16 批中的一个步骤平均需要 2.6 到 3.2 秒，在生成器上评估 300 个测试句子大约需要 20 秒。最好的老挝跑步保持了 46 分钟的资源：33.7 分钟的训练步骤，7.1 分钟的 30 次评估通过，剩下的时间是开始训练、保存适配器和关闭。

## 自己尝试一下

这篇文章的代码位于[训练后食谱](https://github.com/togethercomputer/post-training-cookbook/tree/main/post_training_cookbook/distillation)中：

- `recipes/distillation/screen_languages.py` 衡量师生差距。
- `recipes/distillation/lao_from_kimi_k31_pro.py` 生成教师数据、过滤数据、培训和评估老挝学生。
- `recipes/distillation/multilingual_from_kimi_k31_pro.py` 训练五种语言适配器。

要在训练后为适配器提供服务，请参阅[部署检查点](https://docs.together.ai/docs/post-training/deployment)。

训练后一起

将较大的模型提炼为您自己的模型

从本文中的方法开始，训练 LoRA 适配器并在同一模型资源上对其进行评估。

## 附录：培训是什么样的

![五次运行的训练损失与历元的折线图。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b0766e907f81923fd625cad_kimi-qwen-distillation-training-loss.png)

五次运行的训练损失，根据时期绘制，以便不同长度的运行对齐。

![最佳老挝跑步的学习率与训练步骤的折线图。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b0766f49a29d9fa6265f1f3_kimi-qwen-distillation-learning-rate.png)

最佳老挝跑步的学习率计划：30 个热身步骤，然后余弦衰减到峰值的十分之一。

|运行|步骤|时代| Trained tokens |损失，前 10 步 |失败，最后 25 步 |
| ---| ---| ---| ---| ---| ---|
| SFT 人类参考文献 | 177 | 177 3 | 0.37M | 0.54 | 0.16 | 0.16
|仅限老挝蒸馏 | 180 | 180 3 | 0.38M | 0.36 | 0.36 0.06 | 0.06
|老挝+泰国蒸馏酒| 366 | 366 3 | 0.49M | 0.43 | 0.43 0.06 | 0.06
|蒸馏，老挝+泰语，4×老挝数据| 602 | 602 2 | 111 万 | 0.43 | 0.43 0.13 | 0.13
|五种语言，一种适配器 | 831 | 831 1.5 | 1.5 104万 | 0.82 | 0.82 0.30 | 0.30

损失是每个训练令牌的交叉熵（以 nats 为单位）。经过训练的标记仅计算助手的翻译标记（带有损失的标记），而不计算提示。五种语言运行是“五种语言培训”中的一种。

Three observations from these runs:

- Kimi-K3.1-Pro 的老挝语比人类老挝语更容易让学生学习。人工参考运行和仅限老挝的蒸馏运行翻译相同的 FLORES 开发句子，但学生在人工翻译上每个标记的成本为 0.54 纳特，在 Kimi-K3.1-Pro 上的每个标记为 0.36 纳特，最后以 0.16 纳特与 0.06 纳特的价格结束。 Our guess is that one model's translations are more consistent than a team of human translators', so the student has less to fit.
- The loss drops at every epoch boundary, and held-out quality doesn't follow it. Each drop is the model meeting rows it has already seen.在四次 Lao 运行中，训练损失在第一个 epoch 之后下降了一半以上，而 Lao chrF++ 在 300 个测试句子上的移动量在 -1 到 +3 点之间。更多的数据击败了更多的传递：这些句子的 4× 数据的一个 epoch 达到了 43.2，而较小的 Lao + Thai 数据集的 3 个 epoch 后达到了 41.3。
- The five-language run has the highest loss through its first epoch. Four of its five languages started well below the teacher, against one of two in the Lao runs.

## Related articles
