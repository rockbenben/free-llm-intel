---
vendor: together_ai
title: 把 Kimi-K3.1-Pro 蒸馏进 Qwen3.8-27B：教模型一门新语言
original_title: 
url: https://www.together.ai/blog/distilling-kimi-into-qwen
date: 2026-11-26
lang: zh
captured: 2026-11-27
extractor: readability-v1
translator: agent
status: translated
body_sha: 6604035b90cb
---

# 把 Kimi-K3.1-Pro 蒸馏进 Qwen3.8-27B：教模型一门新语言

Qwen3.8-27B 被要求输出 Lao 时，用 Thai 作答了。我们用 Together Post-Training 把 Kimi-K3.1-Pro 的 Lao 译文蒸馏进它，达到了 teacher 得分的 93%，而 Thai 完好无损。

- 作者：Zain Hasan、Sonny Khan
- 本文链接：[GitHub 上的 distillation cookbook](https://github.com/togethercomputer/post-training-cookbook/tree/main/post_training_cookbook/distillation)[Together Post-Training](https://www.together.ai/post-training)[Qwen3.8-27B](https://www.together.ai/models/qwen3-8-27b)[Kimi-K3.1-Pro](https://www.together.ai/models/kimi-k3-1-pro)

摘要

- **差距：** Qwen3.8-27B 在被要求输出 Lao 时用 Thai 作答，chrF++ 得分 5.5，而 Kimi-K3.1-Pro 在同一测试上得 47.5。
- **修复办法：** 我们用 Together Post-Training，在约 3,800 条 Kimi-K3.1-Pro 的译文上训练了一个 LoRA adapter。
- **结果：** student 在每一句测试句上都用 Lao 作答，得分 44.3，是 teacher 得分的 93%，并且保住了它的 Thai。
- **成本：** 全部实验加起来花费 \$260，代码在 post-training cookbook 里。

在做一些实验时我们发现，[Qwen3.8-27B](https://www.together.ai/models/qwen3-8-27b)——最受欢迎的小语言模型（SLM）之一——不会写 Lao。Lao 是西南部 Tai 语支的一门语言，也是老挝的官方语言。如果你让它把一句英文翻译成 Lao，它会用 Thai 回答：Thai 是 Lao 最接近的亲属语言，用的却是完全不同的文字。在 [FLORES-200](https://huggingface.co/datasets/Muennighoff/flores200) 的 Lao 测试集上，这个模型的 chrF++ 得分是 5.5——chrF++ 是 0 到 100 的分数，衡量译文与人工参考译文的接近程度——而且它只有 11% 的输出使用 Lao 文字。[Kimi-K3.1-Pro](https://www.together.ai/models/kimi-k3-1-pro) 在同一测试上的得分是 47.5。

平心而论，这是个很窄的场景，但这种模式相当常见：一个小语言模型表现出“锯齿状的智能”，在你关心的某个狭窄任务上一败涂地，而一个更大、更贵的模型却能轻松处理。为了补上这一点，我们把 Kimi-K3.1-Pro 当作 teacher，用 Together Post-Training 把它的 Lao 翻译能力蒸馏进 Qwen3.8-27B。

在约 3,800 条 Kimi-K3.1-Pro 的译文上训练之后，这个 27B 的 student 在每一句测试句上都用 Lao 作答，得分 44.3，是 teacher 得分的 93%。它还保住了自己的 Thai 翻译能力——有意思的是，这最后成了最难的部分。我们的第一次尝试在 25 个训练 step 内就修好了 Lao，但也把 Thai 的翻译能力一并弄丢了。

本文会走一遍我们是怎么发现这个差距的、以及最后什么办法奏效。代码、设置和成本在后半部分。所有实验加起来花费 \$260。

![基础 student、蒸馏后的 student 与 Kimi-K3.1-Pro teacher 的 Lao 与 Thai chrF++ 柱状图。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b0765fc996c2110eb55182f_kimi-qwen-distillation-headline.png)

student 从写 Thai 变成写 Lao，达到 teacher 得分的 93%，同时没有丢掉 Thai 能力。

## 找到差距

![Kimi-K3.1-Pro 与 Qwen3.8-27B 在 11 门语言上的 chrF++ 柱状图，差距最大的是 Lao。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b0766387f6debb78af8c6fe_kimi-qwen-distillation-screen.png)

Kimi-K3.1-Pro 在全部 11 门语言上都胜过 Qwen3.8-27B。Lao 上的差距远远最大（49.0 对 7.2）。

我们用的指标是 chrF++，它衡量译文与人工参考译文在字符和词层面的重叠度，取值 0 到 100。关于 Qwen 的 Lao 得分为什么这么低，有一点很重要：在 chrF++ 看来，一个 Thai 答案和一个 Lao 参考译文几乎没有共同之处。当要求翻译成 Lao 时，这个 student 的 50 句输出里有 45 句含 Thai 文字，只有 6 句含 Lao 文字：

> English: "We now have 4-month-old mice that are non-diabetic that used to be diabetic," he added.Qwen3.8-27B (base): “ปัจจุบันเรามีหนูอายุ 4 เดือนที่ไม่เป็นโรคเบาหวาน ซึ่งเคยเป็นโรคเบาหวานมาก่อน” เขากล่าวเสริมKimi-K3.1-Pro: "ພວກເຮົາຕອນນີ້ມີໜູອາຍຸ 4 ເດືອນ ທີ່ບໍ່ເປັນໂຣກເບົາຫວານ ເຊິ່ງເຄີຍເປັນໂຣກເບົາຫວານມາກ່ອນ," ລາວກ່າວຕື່ມ.

基础模型这段 Thai 是一份说得过去的翻译，只是用错了语言。我们会在结果部分回到这一点。

关于这些数字还有一点说明：在这 50 句上，Qwen3.8-27B 的 Lao 得分是 7.2，Kimi-K3.1-Pro 是 49.0；而在完整的 1,012 句测试集上，两者分别是 5.5 和 47.5。测试集列在“我们是怎么做的”一节。

## 方案：off-policy distillation

蒸馏是训练一个小模型（student），让它在某个给定领域里表现得像一个大模型（teacher）。做法有两种。

**On-policy distillation（OPD）**，Thinking Machines 在[这个主题的文章](https://thinkingmachines.ai/blog/on-policy-distillation/)里描述过：让 student 生成文本，teacher 给每一个 token 打分。它需要 teacher 在 student 的 token 上的 log-probabilities，实际就意味着两个模型必须共用同一个 tokenizer。这里我们要把 Kimi 蒸馏进 Qwen，两者不共用 tokenizer，所以我们走了另一个方向。

**Off-policy distillation** 让 teacher 生成文本，再用监督式 fine-tuning（SFT）训练 student 去模仿。最简单的形式下，它只需要 teacher 生成的文本。

我们用的是 off-policy distillation。它让 teacher 这一侧的开销相当低：每次调用 teacher 都是一次普通的 serverless chat 请求，而 Kimi-K3.1-Pro 虽然是个相当大的模型，却从来不需要自己的训练资源。

![从英文句子到一个训练好的 LoRA adapter 的蒸馏流水线示意图。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b0766643280c184bf4a8f03_kimi-qwen-distillation-pipeline.png)

端到端流水线：英文句子送进 Kimi-K3.1-Pro，经过过滤，成为 SFT 数据行，供 Together Post-Training 一个 model resource 上的 Qwen3.8-27B LoRA session 使用。

步骤如下：

- 收集英文源句。
- 让 Kimi-K3.1-Pro 把它们翻译出来，关闭 thinking。
- 丢弃任何大部分字母不属于目标文字（script）的译文。
- 以这些译文为目标，在 Qwen3.8-27B 上 fine-tune 一个 LoRA adapter，并在训练过程中用留出的测试句做评估。
- 把 adapter 保存到 model registry。

我们在 Together Post-Training 上训练这个 student。同一个 model resource 既用于训练 LoRA adapter，也用于从它采样，所以我们能在训练的同时给模型打分。每次评估我们打四个指标：

- 在 FLORES-200 devtest 上对人工参考译文的 chrF++：每次 run 开始和结束时测全部 1,012 句，每 25 个 step 测 300 句（两个最长的 run 里是每 50 或 100 个 step）。
- Lao 文字比例：字母大部分是 Lao 的输出所占的比例。这个指标能直接抓到 Thai 的问题。
- Thai 保持度：在 300 句英译 Thai 测试句上的 chrF++，用来检查模型没有丢掉它原本就会的一门语言。
- 往返充分性：让 Kimi-K3.1-Pro 把各个系统的 Lao 译文回译成英文，我们再把回译结果与原始英文比对打分。这样可以在不依赖参考译文风格的情况下检查语义。

在获得 Lao 翻译能力的同时保住 Thai，最终成了最棘手的部分。

## Thai 带来的意外

其中一次 run 是对照组：用人工的 Lao 参考译文训练，945 条，来自 FLORES dev，完全没有 teacher 参与。Lao 在 25 个 step 内就从 6.7 跳到 43.3。

然后我们去看 Thai。它已经从 46.7 掉到 11.7，到这次 run 结束时只剩 5.3，Thai 输出中落在 Thai 文字里的比例是 0%。模型学到的是“被要求翻译时就写 Lao”，而不是“写你被要求的那门语言”。问题换了个方向。

![各次 run 的英译 Thai chrF++ 随训练 step 变化的折线图。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b07668c58205941917537cb_kimi-qwen-distillation-thai-chrf.png)

300 句测试句上的英译 Thai chrF++。只用人工 Lao 训练会让 Thai 崩掉；混合数据的几次 run 保住了它。

如果我们只评估 Lao，这次 run 看起来会是赢家。它是本文所有 student 里 Lao 得分最高的。

## 修好 Thai

只用 Lao 的那次蒸馏 run，用 Kimi-K3.1-Pro 对同一批句子的译文替代人工译文来训练。这大大减缓了损害，但没有止住。Thai 撑过了两个 epoch，到第三个 epoch 滑到 44.3，300 个 Thai 回答里有 17 个写成了 Lao。

往训练数据里加入约 1,000 条 Kimi-K3.1-Pro 的 Thai 译文就解决了。两次混合 run 的 Thai 最终分别是 47.4 和 47.8，高于基础模型，而且在任何一次评估中都没有低于 47.3。

![对比每种训练配比在被要求输出 Lao 与 Thai 时实际写出何种语言的示意图。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b0766965800a95e7276e19d_kimi-qwen-distillation-forgetting.png)

每种训练数据配比在被要求 Lao 和被要求 Thai 时分别的表现。

这正是关于持续学习（continual learning）的一个好例子：当你教模型一样新东西时，要掺入能保护它已经做得好的那些能力的数据，这样你在意的东西才不会退步。在这里，那就是 Thai——最容易和 Lao 混淆的语言。

## 补齐 Lao 剩余的差距

Thai 保住了，但 Lao 还差一截。在各自约 950 条 Lao 样本的情况下，用人工参考译文训练的 student 得分 44.7，两个蒸馏出来的 student 分别是 41.8 和 41.9。

其中一部分是意料之中的。人工参考译文在“人工参考”这一指标上本来就更占便宜：FLORES dev 和 devtest 是经由同一套人工流程翻译的，所以在 dev 上训练等于在教 devtest 的参考风格。蒸馏出来的 student 学到的则是 teacher 的风格。如果拿 Kimi-K3.1-Pro 自己的译文当参考来打分，蒸馏 student 的 chrF++ 从 8 升到 58，而用人工参考训练的 student 达到 47。

另一个差别是供给。FLORES dev 只有 997 条人工参考译文，不可能再多；而 Kimi-K3.1-Pro 能翻译你手上的任何英文文本。把它对 3,000 句 Wikipedia 的译文加进来，Lao 训练集就从 965 条扩到 3,834 条，Lao 从 41.9 升到 44.3。这距离用人工参考那一次不到半个点，而且 Thai 完好。

更多数据也胜过更多轮训练：4× 数据跑一个 epoch 就在那 300 句测试句上达到 43.2，而较小的 Lao + Thai 集跑三个 epoch 后是 41.3。

![四次训练 run 的英译 Lao chrF++ 随 SFT step 变化的折线图，teacher 以虚线表示。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b0766a1cea7d11c54618f09_kimi-qwen-distillation-lao-chrf.png)

四次训练 run 在 300 句测试句上的英译 Lao chrF++，横轴为 SFT step。虚线是 teacher。

## 结果

| 实验 | 训练数据 | Lao chrF++ | Lao 文字占比 | Thai chrF++ |
| --- | --- | --- | --- | --- |
| 基础 student | 无 | 5.5 | 11% | 46.7 |
| 用人工参考做 SFT | 945 条人工 Lao 译文 | 44.7 | 100% | 5.3 |
| 蒸馏，仅 Lao | 965 条 Kimi-K3.1-Pro 的 Lao 译文 | 41.8 | 100% | 44.3 |
| 蒸馏，Lao + Thai | 来自 Kimi-K3.1-Pro 的 965 条 Lao + 989 条 Thai | 41.9 | 100% | 47.4 |
| 蒸馏，Lao + Thai，Lao 数据 4× | 来自 Kimi-K3.1-Pro 的 3,834 条 Lao + 989 条 Thai | 44.3 | 100% | 47.8 |
| Kimi-K3.1-Pro teacher | - | 47.5 | 100% | 49.9 |

Lao 的数字用全部 1,012 句测试句，Thai 用 300 句。最好的一次 run 达到 teacher 得分的 93%。如果以基础模型的起点来量，它在 Lao 上补上了 base 到 teacher 之间 92% 的差距：

$$\text{gap closed} = \frac{s_{\text{student}} - s_{\text{base}}}{s_{\text{teacher}} - s_{\text{base}}} = \frac{44.3 - 5.5}{47.5 - 5.5} = 0.92$$

**基础模型大体上是抓到了意思的，只是写错了语言。** 回想一下那个老鼠的例子。在往返充分性上，基础模型那段 Thai 输出得分 64.6，略高于人工 Lao 参考译文（64.0）。蒸馏后的 student 得分 65.7，并且在 100% 的测试句上写出 Lao。所以主要的差距是“语言身份”，这也是为什么每一次 run 在第一次评估（第 25 或第 50 个 step）时就已经把文字修好了。

![Lao 回答中写成 Lao 文字的比例随训练 step 变化的折线图。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b0766acfba479086057a0a8_kimi-qwen-distillation-lao-script.png)

Lao 回答中写成 Lao 文字的比例。每一次 run 在第一次评估时就已经把文字修好了。

loss 曲线、token 数量和每次 run 的细节可以在附录里找到。

## 在五门语言上训练

为了确认这不是 Lao 特有的情况，我们训练了一个 adapter，涵盖 Lao、Northern Sotho 和 Zulu（差距最大的三个）加上 Yoruba——两个模型在所有拉丁字母语言里得分最低的那门——再加上用于保持能力的 Thai：总共 8,871 条 Kimi-K3.1-Pro 译文，每门语言约 2,000 条，Thai 1,000 条，跑了 831 个 step。

![基础 student、蒸馏后的 adapter 与 Kimi-K3.1-Pro 在五门语言上的 chrF++ 柱状图。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b0766d45a7d2ce6e9d023e3_kimi-qwen-distillation-multilingual.png)

一个蒸馏出来的 adapter 同时提升了 Lao、Northern Sotho、Yoruba 和 Zulu，并保住了 Thai 的表现。

| 语言 | 基础 student | 蒸馏后 | Kimi-K3.1-Pro | 已补差距 |
| --- | --- | --- | --- | --- |
| Lao | 5.5 | 41.8 | 47.5 | 87% |
| Northern Sotho | 32.7 | 48.0 | 50.7 | 85% |
| Yoruba | 20.7 | 25.7 | 27.7 | 71% |
| Zulu | 37.7 | 39.2 | 50.3 | 12% |
| Thai | 46.7 | 48.0 | 49.9 | 有所提升 |

Lao 用全部 1,012 句测试句；其余语言用 300 句，teacher 也在同样的句子上打分。每门语言都有提升。Zulu 提升最少：训练中它有 1% 到 2% 的输出陷入重复循环，所以多给 Zulu 数据、或者加一个 repetition penalty，是我们会最先试的两件事。

## 如果你也遇到这样的差距

如果重来，我们还会这么做：

- 先做筛查。每门语言 50 句就足够看出 teacher 在哪里遥遥领先。
- 训练之前先看清基础模型错在哪里。这次是意思有了、语言错了，所以文字在头 25 到 50 个 step 内就修好了。
- 当 student 进入平台期时，先去生成更多 teacher 数据，而不是加 epoch。
- 掺入你想保住的相邻技能的数据，并在训练中给它打分。只看 Lao 的评估会把那次搞坏 Thai 的 run 选成最优。

## 我们是怎么做的

本文剩下的部分都是做法：teacher 数据、训练循环、各项设置、测试集和成本。

### 用 serverless 的 Kimi-K3.1-Pro 生成 teacher 数据

每次调用 teacher 都是一次普通的 chat completion，并且关闭 thinking。翻译不需要长推理：打开 thinking 时，Kimi-K3.1-Pro 在 300 句 Lao 测试句上的得分反而更低（43.5 对 47.3），而且用了大约 8 倍的 token。关掉之后，一个 Lao 回答平均约 175 个 output token。

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

源文本是 FLORES-200 **dev** 的 997 句，加上 4,000 句来自英文 Wikipedia 的句子（Lao 3,000 句，Thai 1,000 句）。

关于这些数据，有两点值得知道：

- 用 teacher 生成数据很便宜。Kimi-K3.1-Pro 的 serverless 价格是每百万 input token \$2、每百万 output token \$10。全部 4,000 条 Lao 译文加起来花费 \$7.46。
- 训练前先过滤。只有当一条译文里至少 70% 的字母属于目标文字、并且它不是英文的复读时，我们才保留它。这个过滤器删掉了 Kimi-K3.1-Pro 的 4% Lao 译文。

每一条保留下来的译文变成一行 chat 格式的训练数据：

```
{"messages": [
  {"role": "user", "content": "Translate the following English text into Lao. Output only the Lao translation, with no explanation.\n\n<English sentence>"},
  {"role": "assistant", "content": "<Kimi-K3.1-Pro's Lao translation>"}
]}
```

### 在 Together Post-Training 上训练 student

Together Post-Training 把一次训练 run 拆给你的代码和 GPU 两侧。**model resource** 是一组 GPU（这里是 B200），上面加载了基础模型。它有一个 **trainer**，负责执行 `forward_backward` 和 `optim_step`，还可以有一个可选的 **generator**，从中间的 checkpoint 采样文本。**session** 则是在这个 resource 上训练的一个 LoRA adapter。

![笔记本与 model resource 之间一个训练 step 的示意图。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b0766deb889746147db68c7_kimi-qwen-distillation-step.png)

一个训练 step：笔记本构建样本并发出去；model resource 计算 loss、执行 optimizer step，并为评估做采样。

我们用 cookbook 做了三件事：

- `get_codec("Qwen/Qwen3.8-27B", enable_thinking=False)` 用 Qwen 自己的模板渲染每段对话。
- `build_conversation_samples` 把 prompt 遮起来（loss 权重 0），只训练 assistant 的译文（权重 1），并且包含回合结束的 token，这样模型能学会什么时候停。
- `build_cross_entropy_sample` 把 token 平移成 API 期望的 next-token 目标。

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

`record_in_ledger`、`wait_until_ready`、`next_batch`、`lr_at` 和 `score` 是我们自己写的小 helper。

设置是：

- LoRA rank 64（Qwen3.8-27B 的最大值），alpha 128
- 峰值学习率 1e-4，前 5% 做 warmup，然后用 cosine 衰减到峰值的十分之一
- batch size 16

因为 resource 带 generator，我们不需要为了评估单独部署一个 endpoint。

### 测试集

同一个模型在不同地方会看到略有出入的分数，因为我们在三套 FLORES-200 句子集上打过分数：

| 句子集 | 用途 | 基础模型 Lao | Teacher Lao |
| --- | --- | --- | --- |
| 每门语言 50 句 | 11 门语言的筛查 | 7.2 | 49.0 |
| 300 句 devtest | 训练中的评估，以及 Thai | 6.7 | 47.3 |
| 全部 1,012 句 devtest | 每次 run 的开始与结束，以及主要结果 | 5.5 | 47.5 |

FLORES-200 **devtest** 从未用于训练。我们全程把它留作测试集。

### 时间与成本

按在 B200 上训练来算，本文所有实验加起来花费 \$260。teacher 数据是便宜的那部分：全部 4,000 条 Lao 译文花了 \$7.46。

至于时间，每次 run 的第一个 step 要 2.5 到 3 分钟。之后在 batch 16 下，一个 step 的中位数是 2.6 到 3.2 秒，在 generator 上评估 300 句测试句大约 20 秒。最好的那次 Lao run 占用了它的 resource 46 分钟：训练 step 33.7 分钟，30 轮评估共 7.1 分钟，其余时间花在启动 session、保存 adapter 和关停上。

## 自己动手试试

本文的代码在 [post-training cookbook](https://github.com/togethercomputer/post-training-cookbook/tree/main/post_training_cookbook/distillation) 里：

- `recipes/distillation/screen_languages.py` 测量 teacher 与 student 之间的差距。
- `recipes/distillation/lao_from_kimi_k31_pro.py` 生成 teacher 数据、过滤、训练并评估 Lao student。
- `recipes/distillation/multilingual_from_kimi_k31_pro.py` 训练那个五语言 adapter。

训练之后要部署这个 adapter，见 [Deploy a checkpoint](https://docs.together.ai/docs/post-training/deployment)。

Together Post-Training

将更大的模型蒸馏进你自己的模型

在同一份 model resource 上训练并评估一个 LoRA adapter，从本文的 recipe 起步。

## 附录：训练过程长什么样

![五次 run 的训练 loss 随 epoch 变化的折线图。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b0766e907f81923fd625cad_kimi-qwen-distillation-training-loss.png)

五次 run 的训练 loss，横轴用 epoch，这样长度不同的 run 才能对齐比较。

![最好那次 Lao run 的学习率随训练 step 变化的折线图。](https://cdn.prod.website-files.com/69654e88dce9154b5f12070c/6b0766f49a29d9fa6265f1f3_kimi-qwen-distillation-learning-rate.png)

最好那次 Lao run 的学习率调度：30 个 warmup step，然后用 cosine 衰减到峰值的十分之一。

| 实验 | step 数 | epoch 数 | 训练 token 数 | 前 10 个 step 的 loss | 最后 25 个 step 的 loss |
| --- | --- | --- | --- | --- | --- |
| 用人工参考做 SFT | 177 | 3 | 0.37M | 0.54 | 0.16 |
| 蒸馏，仅 Lao | 180 | 3 | 0.38M | 0.36 | 0.06 |
| 蒸馏，Lao + Thai | 366 | 3 | 0.49M | 0.43 | 0.06 |
| 蒸馏，Lao + Thai，Lao 数据 4× | 602 | 2 | 1.11M | 0.43 | 0.13 |
| 五门语言，一个 adapter | 831 | 1.5 | 1.04M | 0.82 | 0.30 |

loss 是交叉熵，单位是每个被训练 token 的 nat。训练 token 数只计 assistant 译文的 token，也就是承担 loss 的那些，不含 prompt。五门语言那次 run 就是“在五门语言上训练”一节里的那次。

从这些 run 里能看到三点：

- 对 student 来说，Kimi-K3.1-Pro 的 Lao 比人工 Lao 更好学。用人工参考的那次 run 和只用 Lao 的蒸馏 run 翻译的是同一批 FLORES dev 句子，但 student 在人工译文上的起点是每个 token 0.54 nat，在 Kimi-K3.1-Pro 的译文上是 0.36，结束时分别是 0.16 和 0.06。我们的猜测是：一个模型的译文比一组人工译者的译文更一致，所以 student 要拟合的东西更少。
- 每个 epoch 边界 loss 都会下降，而留出集上的质量并不跟着走。每次下降都是模型又见到了它已经见过的数据行。在四次 Lao run 里，第一个 epoch 之后训练 loss 掉了一半以上，而那 300 句测试句上的 Lao chrF++ 只变动了 −1 到 +3 个点。更多数据胜过多跑几轮：4× 数据跑一个 epoch 就在这些句子上达到 43.2，而较小的 Lao + Thai 集跑三个 epoch 后是 41.3。
- 五门语言那次 run 在第一个 epoch 里的 loss 是最高的。它五门语言里有四门的起点远低于 teacher，而 Lao 那几次 run 里是两门中的一门。
