---
vendor: huggingface
title: 在 Transformers 中用对比搜索生成媲美人类的文本
original_title: Generating Human-level Text with Contrastive Search in Transformers 🤗
url: https://huggingface.co/blog/introducing-csearch
date: 2022-11-08
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: 35bf0a83c312
---

# 在 Transformers 中用对比搜索生成媲美人类的文本 🤗

Tian Lan

GMFTBY

本文也有中文版本 [简体中文](https://huggingface.co/blog/zh/introducing-csearch)。

### 1. 引言：

自然语言生成（即文本生成）是自然语言处理（NLP）的核心任务之一。在这篇博客中，我们介绍当前最先进的解码方法——***对比搜索（Contrastive Search）***，用于神经文本生成。对比搜索最初在 NeurIPS 2022 的论文 *"A Contrastive Framework for Neural Text Generation"* [[1]](https://huggingface.co/blog/introducing-csearch#references)（[[论文](https://arxiv.org/abs/2202.06417)][[官方实现](https://github.com/yxuansu/SimCTG)]）中提出。在其后续工作 *"Contrastive Search Is What You Need For Neural Text Generation"* [[2]](https://huggingface.co/blog/introducing-csearch#references)（[[论文](https://arxiv.org/abs/2210.14140) [[官方实现](https://github.com/yxuansu/Contrastive_Search_Is_What_You_Need)]）中，作者进一步证明：对比搜索可以用**现成的**语言模型跨 **16** 种语言生成媲美人类的文本。

**[备注]** 不熟悉文本生成的用户，请参阅[这篇博客](https://huggingface.co/blog/how-to-generate)了解更多细节。

### 2. Hugging Face 🤗 对比搜索 Demo：

Contrastive Search 现已进入 🤗 `transformers`，PyTorch 和 TensorFlow 都支持。你可以用自选框架在[这个 Colab notebook](https://colab.research.google.com/github/huggingface/blog/blob/main/notebooks/115_introducing_contrastive_search.ipynb)（链接在顶部）中交互体验本文示例。我们还做了一个很棒的 [demo](https://huggingface.co/spaces/joaogante/contrastive_search_generation)，直接对比对比搜索与其他流行解码方法（如 beam search、top-k sampling [[3]](https://huggingface.co/blog/introducing-csearch#references) 和 nucleus sampling [[4]](https://huggingface.co/blog/introducing-csearch#references)）。

### 3. 环境安装：

在运行后续章节的实验前，请按如下方式安装最新版本的 `transformers`

```
pip install torch
pip install "transformers==4.24.0"
```

### 4. 现有解码方法的问题：

解码方法可以分为两类：(i) 确定性方法和 (ii) 随机方法。我们分别来看！

#### 4.1. 确定性方法：

确定性方法（如贪心搜索和 beam search）通过选择语言模型度量下似然最高的文本延续来生成文本。然而，正如已有研究广泛讨论的 [[3]](https://huggingface.co/blog/introducing-csearch#references)[[4]](https://huggingface.co/blog/introducing-csearch#references)，确定性方法常导致*模型退化（model degeneration）*问题，即生成的文本不自然、含有不想要的重复。

下面看一个用 GPT-2 模型贪心搜索生成文本的示例。

```
from transformers import AutoTokenizer, GPT2LMHeadModel

tokenizer = AutoTokenizer.from_pretrained('gpt2-large')
input_ids = tokenizer('DeepMind Company is', return_tensors='pt').input_ids
model = GPT2LMHeadModel.from_pretrained('gpt2-large')

output = model.generate(input_ids, max_length=128)
print("Output:\n" + 100 * '-')
print(tokenizer.decode(output[0], skip_special_tokens=True))
print("" + 100 * '-')
```

模型输出：

```
Output:
----------------------------------------------------------------------------------------------------
DeepMind Company is a leading AI research company, with a focus on deep learning and deep
learning-based systems.

The company's research is focused on the development of deep learning-based systems that
can learn from large amounts of data, and that can be used to solve real-world problems.

DeepMind's research is also used by the UK government to develop new technologies for the
UK's National Health Service.

DeepMind's research is also used by the UK government to develop new technologies for the
UK's National Health Service.

DeepMind's research is also used by the UK government to develop new technologies
----------------------------------------------------------------------------------------------------
```

**[备注]** 从贪心搜索生成的结果中，我们可以看到明显的重复模式。

#### 4.2. 随机方法：

为了解决确定性方法的问题，随机方法在解码过程中引入随机性来生成文本。两种广泛使用的随机方法是 (i) top-k sampling [[3]](https://huggingface.co/blog/introducing-csearch#references) 和 (ii) nucleus sampling（也叫 top-p sampling）[[4]](https://huggingface.co/blog/introducing-csearch#references)。

下面展示用 GPT-2 模型做 nucleus sampling（p=0.95）生成文本的示例。

```
import torch
from transformers import AutoTokenizer, GPT2LMHeadModel

tokenizer = AutoTokenizer.from_pretrained('gpt2-large')
input_ids = tokenizer('DeepMind Company is', return_tensors='pt').input_ids
model = GPT2LMHeadModel.from_pretrained('gpt2-large')

torch.manual_seed(0.)
output = model.generate(input_ids, do_sample=True, max_length=128, top_p=0.95, top_k=0)
print("Output:\n" + 100 * '-')
print(tokenizer.decode(output[0], skip_special_tokens=True))
print("" + 100 * '-')
```

模型输出：

```
Output:
----------------------------------------------------------------------------------------------------
DeepMind Company is a leading provider of AI-based research, development, and delivery of
AI solutions for security, infrastructure, machine learning, communications, and so on."

'AI is not journalism'

Worse still was the message its researchers hoped would reach the world's media — that it
was not really research, but rather a get-rich-quick scheme to profit from living forces'
ignorance.

"The thing is, we know that people don't consciously assess the value of the others'
information. They understand they will get the same on their own."

One example? Given the details of today
----------------------------------------------------------------------------------------------------
```

**[备注]** 虽然 nucleus sampling 能生成没有重复的文本，但生成文本的语义连贯性保持得不好。例如生成短语 *'AI is not journalism'* 与给定前缀 *'DeepMind Company'* 并不连贯。

我们注意到，这个语义不一致的问题可以靠调低温度部分缓解。然而，降低温度会让 nucleus sampling 更接近贪心搜索，相当于在贪心搜索与 nucleus sampling 之间做权衡。一般来说，很难找到一个与 prompt 和模型都无关的温度，能同时避开贪心搜索和 nucleus sampling 两个坑。

### 5. 对比搜索：

本节详细介绍一种新的解码方法 ***对比搜索***。

#### 5.1. 解码目标：

给定前文文本 x<tx_{< t}x<t​，输出 token xtx_{t}xt​ 的选择遵循

其中 V(k)V^{(k)}V(k) 是语言模型概率分布 pθ(v∣x<t)p_{\theta}(v|x_{< t})pθ​(v∣x<t​) 的 top-k 预测集合。第一项即*模型置信度*，是语言模型预测的候选 token vvv 的概率。第二项*退化惩罚*衡量 vvv 相对于前文上下文 x<t x_{< t}x<t​ 的区分度，函数 s(⋅,⋅)s(\cdot, \cdot)s(⋅,⋅) 计算 token 表示之间的余弦相似度。更具体地说，退化惩罚定义为 vvv 的 token 表示 hvh_{v}hv​ 与上下文 x<tx_{< t}x<t​ 中所有 token 表示之间余弦相似度的最大值。这里，候选表示 hvh_{v}hv​ 是语言模型在 x<tx_{< t}x<t​ 与 vvv 拼接后给出的表示。直观来看，vvv 的退化惩罚越大，说明它在表示空间中与上下文越相似，因此越可能导致模型退化问题。超参数 α\alphaα 调节这两个成分的重要性。当 α=0\alpha=0α=0 时，对比搜索退化为原始的贪心搜索。

**[备注]** 生成输出时，对比搜索同时考虑 (i) 语言模型预测的概率，以保持生成文本与前文之间的语义连贯；以及 (ii) 与先前上下文的相似度，以避免模型退化。

#### 5.2. 用对比搜索生成文本：

下面使用与 [4.1](https://huggingface.co/blog/introducing-csearch#deterministic_methods) 和 [4.2](https://huggingface.co/blog/introducing-csearch#stochastic_methods) 节相同的前文（即 *"DeepMind Company is"*），用对比搜索（k=4、α=0.6\alpha=0.6α=0.6）生成文本。为了充分展示对比搜索的卓越能力，我们让语言模型生成一篇**较长**的、含 **512** 个 token 的文档

```
from transformers import GPT2Tokenizer, GPT2LMHeadModel

model_name = 'gpt2-large'
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name, pad_token_id=tokenizer.eos_token_id)
model.eval()

# prepare the prefix
prefix_text = r'DeepMind Company is'
input_ids = tokenizer(prefix_text, return_tensors='pt').input_ids

# generate the result with contrastive search
output = model.generate(input_ids, penalty_alpha=0.6, top_k=4, max_length=512)
print("Output:\n" + 100 * '-')
print(tokenizer.decode(output[0], skip_special_tokens=True))
print("" + 100 * '-')
```

参数说明如下：

- `--top_k`：对比搜索中的超参数 kkk。
- `--penalty_alpha`：对比搜索中的超参数 α\alphaα。

模型输出：

```
Output:
----------------------------------------------------------------------------------------------------
DeepMind Company is a leader in artificial intelligence (AI). We have a long history of working
with companies such as Google, Facebook, Amazon, and Microsoft to build products that improve
people's lives, and today we are excited to announce that DeepMind's AlphaGo program has won the
game of Go, becoming the first program to defeat a professional Go player.

The victory is a testament to the power of deep learning, and to the incredible work of our
research team, which has been at the forefront of AI research for the past five years. AlphaGo
is one of the most advanced Go programs ever created, and its performance is an important step
towards the goal of human-level AI.

"This is the culmination of a decade of hard work," said Andy Ng, co-founder and CTO of DeepMind.
"We are thrilled to have achieved this milestone and look forward to continuing to develop AI that
can be used in a wide range of applications and to help people live better lives."

DeepMind's work on Go began in 2010, when it began to train a neural network to play Go using
millions of games played by top Go players around the world. Since then, the team has refined the
algorithm, adding more and more layers of reinforcement learning to make it better at recognizing
patterns and making decisions based on those patterns. In the past year and a half, the team has
made significant progress in the game, winning a record-tying 13 games in a row to move into the
top four of the world rankings.

"The game of Go is a complex game in which players have to be very careful not to overextend their
territory, and this is something that we have been able to improve over and over again," said
Dr. Demis Hassabis, co-founder and Chief Scientific Officer of DeepMind. "We are very proud of our
team's work, and we hope that it will inspire others to take the next step in their research and
apply the same techniques to other problems."

In addition to the win in Go, DeepMind has also developed an AI system that can learn to play a
number of different games, including poker, Go, and chess. This AI system, called Tarsier, was
developed in partnership with Carnegie Mellon University and the University of California,
Berkeley, and is being used to teach computer vision and machine learning to identify objects in
images and recognize speech in natural language. Tarsier has been trained to play the game of Go
and other games on a
----------------------------------------------------------------------------------------------------
```

**[备注]** 可以看到生成的文本质量极高：整篇文档语法流畅、语义连贯。同时生成文本也很好地保持了事实正确性，例如在第一段中它把 *"AlphaGo"* 展开描述为 *"第一个击败职业围棋选手的程序"*。

#### 5.3. 对比搜索的可视化演示：

为了更好地理解对比搜索如何工作，我们把贪心搜索（[4.1 节](https://huggingface.co/blog/introducing-csearch#deterministic_methods)）与对比搜索做可视化对比。具体地，我们分别可视化贪心搜索和对比搜索生成文本的 token 相似度矩阵。两个 token 之间的相似度定义为它们 token 表示（即最后一个 transformer 层的隐藏状态）之间的余弦相似度。贪心搜索（上）与对比搜索（下）的结果如下图。

**[备注]** 从贪心搜索的结果可以看到，非对角位置出现高相似度分数，清楚表明贪心搜索生成了重复。相反，对比搜索的结果中高相似度分数基本只出现在对角位置，验证了退化问题被成功解决。对比搜索这一出色特性来自解码过程中引入的退化惩罚（见 [5.1 节](https://huggingface.co/blog/introducing-csearch#contrastive_objective)）。

### 6. 更多生成示例：

本节提供更多生成示例，比较不同解码方法。

#### 6.1. 示例一 —— GPT-2：

这部分用 GPT-2 生成文本，前文取自当年发布 GPT-2 的 [OpenAI 博客](https://openai.com/blog/better-language-models/)原文：

> In a shocking finding, scientist discovered a herd of unicorns living in a remote, previously unexplored valley, in the Andes Mountains. Even more surprising to the researchers was the fact that the unicorns spoke perfect English.

加载语言模型并准备前文：

```
import torch
from transformers import AutoTokenizer, GPT2LMHeadModel

tokenizer = AutoTokenizer.from_pretrained('gpt2-large')
model = GPT2LMHeadModel.from_pretrained('gpt2-large')

prefix_text = r"In a shocking finding, scientist discovered a herd of unicorns living in a remote, previously unexplored valley, in the Andes Mountains. Even more surprising to the researchers was the fact that the unicorns spoke perfect English."
input_ids = tokenizer(prefix_text, return_tensors='pt').input_ids
```

##### 6.1.1. 用贪心搜索生成文本：

代码：[点击展开]

```
output = model.generate(input_ids, max_length=512)
print("Output:\n" + 100 * '-')
print(tokenizer.decode(output[0], skip_special_tokens=True))
print("" + 100 * '-')
```

模型输出：[点击展开]

```
Output:
----------------------------------------------------------------------------------------------------
In a shocking finding, scientist discovered a herd of unicorns living in a remote, previously
unexplored valley, in the Andes Mountains. Even more surprising to the researchers was the fact
that the unicorns spoke perfect English.

The researchers, led by Dr. David R. Williams of the University of California, Santa Cruz,
discovered the unicorns in the Andes Mountains of Peru. The area is known for its unique geology
and is home to a number of rare species of animals.

The researchers found the unicorns in the Andes Mountains of Peru.

"We were surprised to find that the unicorns were able to communicate with each other," Williams
said. "We were also surprised to find that they were able to communicate in English."

The researchers believe that the unicorns are descendants of the ancient Incas, who lived in the
area around 2,000 years ago.

"The Incas were the first people to use the Andes Mountains as a refuge from the harsh climate of
the Andes," Williams said. "They were also the first people to use the Andes Mountains as a place
to hunt and gather food."

The researchers believe that the unicorns are descendants of the ancient Incas, who lived in the
area around 2,000 years ago.

"The Incas were the first people to use the Andes Mountains as a refuge from the harsh climate of
the Andes," Williams said. "They were also the first people to use the Andes Mountains as a place
to hunt and gather food."

The researchers believe that the unicorns are descendants of the ancient Incas, who lived in the
area around 2,000 years ago.

"The Incas were the first people to use the Andes Mountains as a refuge from the harsh climate of
the Andes," Williams said. "They were also the first people to use the Andes Mountains as a place
to hunt and gather food."

The researchers believe that the unicorns are descendants of the ancient Incas, who lived in the
area around 2,000 years ago.

"The Incas were the first people to use the Andes Mountains as a refuge from the harsh climate of
the Andes," Williams said. "They were also the first people to use the Andes Mountains as a place
to hunt and gather food."

The researchers believe that the unicorns are descendants of the ancient Incas, who lived in the
area around 2,000 years ago
----------------------------------------------------------------------------------------------------
```

##### 6.1.2. 用 Nucleus Sampling 生成文本：

代码：[点击展开]

```
torch.manual_seed(0.)
output = model.generate(input_ids, do_sample=True, max_length=512, top_p=0.95, top_k=0)
print("Output:\n" + 100 * '-')
print(tokenizer.decode(output[0], skip_special_tokens=True))
print("" + 100 * '-')
```

模型输出：[点击展开]

```
Output:
----------------------------------------------------------------------------------------------------
In a shocking finding, scientist discovered a herd of unicorns living in a remote, previously
unexplored valley, in the Andes Mountains. Even more surprising to the researchers was the fact
that the unicorns spoke perfect English. The study was published in the Journal of Zoology in
March 2016.

Polygynous mammals such as unicorns have remained largely unknown to science. Professor Gustavo
Giacota, from the University of Oxford who led the study, said that they had been documented as
far as Eastern Siberia in Russia, but had only been seen a handful of times in the Gobi Desert.

Tiny animals with pale and shiny coats live in the presence of human beings and are hardly likely
to be victims of any cruelty. However, there is some evidence of the condition occurring in both
humans and animals in remote regions, which might have similarities to "black moles" that coexist
on the skin.

It is thought that Unicorns could be inside themselves, that they have different scents depending
on their current environment, or just fall out and there are plenty of legends of how they have
survived. Experts speculate that the moths and other animals could be remnants of the Yezidi Isis
and Charon, which literally is both the word which means great bird, and the Greek word for sound.
It is said that the Isis and Charon taught their young the use of voice in the form of calling out
to others.

The scientists think that it could be ancient folklore that has survived and is no longer attributed
to a real entity
----------------------------------------------------------------------------------------------------
```

##### 6.1.3. 用对比搜索生成文本：

代码：

```
output = model.generate(input_ids, max_length=512, penalty_alpha=0.6, top_k=4)
print("Output:\n" + 100 * '-')
print(tokenizer.decode(output[0], skip_special_tokens=True))
print("" + 100 * '-')
```

模型输出：

```
Output:
----------------------------------------------------------------------------------------------------
In a shocking finding, scientist discovered a herd of unicorns living in a remote, previously unexplored
valley, in the Andes Mountains. Even more surprising to the researchers was the fact that the unicorns
spoke perfect English.

According to the BBC, a team of scientists led by Dr David MacKay, from the University of Bristol, spent
two years searching for the unicorn herd, which they discovered during a survey of the area.

"It's a very rare find," MacKay told the BBC. "There are a few in the Himalayas, but this is the first
time we've been able to find one in such a remote area."

The team was surprised to find a herd of unicorns living in a region that has been known to be a hotbed
of poaching, with many of the animals poached for their horns, which are used in traditional Chinese
medicine to treat everything from rheumatism to cancer.

"We knew that the area was rich in rhino horn, but we had no idea how many there were, or what they were
doing there," MacKay said. "This is an area of high poaching pressure, and we wanted to find out what was
going on."

In order to do so, the team used GPS collars to track the animals as they moved around the mountain and
the surrounding area. The GPS data was then compared with information gathered from local villagers, who
had a wealth of information about the animals' movements, including where they were eating, what they were
doing at night, and how much time they spent in the mountains each day.

After analyzing the data, the team determined that the herd consisted of at least three species of unicorns,
including a male and two females. One of the females was the mother of the male, and the other two were her
daughters. All three had the same horn color, which is believed to be a sign of purity in the animal kingdom.

While the discovery is exciting, it's not the first time scientists have discovered an animal that speaks
English. Last year, scientists discovered a species of porcupine that can be heard by humans, and has been
dubbed "Porcupine Man" for his ability to converse with the human race.
----------------------------------------------------------------------------------------------------
```

#### 6.2. 示例二 —— OPT：

这部分使用 Meta 近期发布的 OPT 模型 [[5]](https://huggingface.co/blog/introducing-csearch#references)，取著名 ResNet 论文 [[6]](https://huggingface.co/blog/introducing-csearch#references) 摘要的前两句作为前文生成文本。

> Deeper neural networks are more difficult to train. We present a residual learning framework to ease the training of networks that are substantially deeper than those used previously.

加载语言模型并准备前文：

```
import torch
from transformers import AutoTokenizer, OPTForCausalLM
model_name = r'facebook/opt-1.3b'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = OPTForCausalLM.from_pretrained(model_name)

prefix_text = r"Deeper neural networks are more difficult to train. We present a residual learning framework to ease the training of networks that are substantially deeper than those used previously."
input_ids = tokenizer(prefix_text, return_tensors='pt').input_ids
```

##### 6.2.1. 用贪心搜索生成文本：

代码：[点击展开]

```
output = model.generate(input_ids, max_length=256)
print("Output:\n" + 100 * '-')
print(tokenizer.decode(output[0], skip_special_tokens=True))
print("" + 100 * '-')
```

模型输出：[点击展开]

```
Output:
----------------------------------------------------------------------------------------------------
Deeper neural networks are more difficult to train. We present a residual learning framework to ease
the training of networks that are substantially deeper than those used previously. We show that the
residual learning framework can be used to train deep neural networks that are significantly more
difficult to train than those used previously. We also show that the residual learning framework can
be used to train deep neural networks that are significantly more difficult to train than those used
previously.

The paper presents a new residual learning framework for deep neural networks that is based on the
concept of residuals. The residuals are the residuals of the network that are not used in the training
process. The residuals are computed by taking the residuals of the network that are used in the training
process and subtracting the residuals of the network that are not used in the training process. The
residuals are then used to train the network. The residuals are computed by taking the residuals of
the network that are used in the training process and subtracting the residuals of the network that
are not used in the training process. The residuals are then used to train the network. The residuals
are computed by taking the residuals of the network that are used in the training process and
subtracting the residuals of the
----------------------------------------------------------------------------------------------------
```

##### 6.2.2. 用 Nucleus Sampling 生成文本：

代码：[点击展开]

```
torch.manual_seed(0.)
output = model.generate(input_ids, do_sample=True, max_length=256, top_p=0.95, top_k=0)
print("Output:\n" + 100 * '-')
print(tokenizer.decode(output[0], skip_special_tokens=True))
print("" + 100 * '-')
```

模型输出：[点击展开]

```
Output:
----------------------------------------------------------------------------------------------------
Deeper neural networks are more difficult to train. We present a residual learning framework to ease the
training of networks that are substantially deeper than those used previously. The theory focuses on
several aspects of learning, including the dynamics of replicative and non-replicative aspects of learning.
This framework emphasizes learning by entropy. New randomized algorithms enable training networks with
residual learning, so that deep networks can be deployed as reliably and as efficiently as their more
conventional counterparts.
----------------------------------------------------------------------------------------------------
```

##### 6.2.3. 用对比搜索生成文本：

代码：

```
output = model.generate(input_ids, max_length=256, penalty_alpha=0.6, top_k=6)
print("Output:\n" + 100 * '-')
print(tokenizer.decode(output[0], skip_special_tokens=True))
print("" + 100 * '-')
```

模型输出：

```
Output:
----------------------------------------------------------------------------------------------------
Deeper neural networks are more difficult to train. We present a residual learning framework to ease
the training of networks that are substantially deeper than those used previously.

In this paper, we propose a model-based residual learning (MBRL) framework that is based on neural
networks trained on data that is sparse in terms of dimensionality (e.g., 1, 2, 3, etc.). The network
parameters are chosen such that there is a high probability of convergence, i.e., the number of
iterations is large enough to minimize the variance of the residuals. This is achieved by training
the network on a set of training data, in which the data is sparse in terms of dimensionality, and
then discarding the nonparametric part of the data after training is complete.

We show that MBRL outperforms other methods for deep reinforcement learning (RL) and deep convolutional
neural networks (CNNs) by a factor of at least 2. In addition, we show that, compared to CNNs, MBRL
performs better in two-dimensional (2D) and three-dimensional (3D) cases.
----------------------------------------------------------------------------------------------------
```

### 7. 资源：

想了解对比搜索的更多细节，请查阅我们的论文和代码

- **A Contrastive Framework for Neural Text Generation**：(1) [论文](https://arxiv.org/abs/2202.06417) 和 (2) [官方实现](https://github.com/yxuansu/SimCTG)。
- **Contrastive Search Is What You Need For Neural Text Generation**：(1) [论文](https://arxiv.org/abs/2210.14140) 和 (2) [官方实现](https://github.com/yxuansu/Contrastive_Search_Is_What_You_Need)。

### 8. 引用：

```
@inproceedings{su2022a,
   title={A Contrastive Framework for Neural Text Generation},
   author={Yixuan Su and Tian Lan and Yan Wang and Dani Yogatama and Lingpeng Kong and Nigel Collier},
   booktitle={Advances in Neural Information Processing Systems},
   editor={Alice H. Oh and Alekh Agarwal and Danielle Belgrave and Kyunghyun Cho},
   year={2022},
   url={https://openreview.net/forum?id=V88BafmH9Pj}
}

@article{su2022contrastiveiswhatyouneed,
  title={Contrastive Search Is What You Need For Neural Text Generation},
  author={Su, Yixuan and Collier, Nigel},
  journal={arXiv preprint arXiv:2210.14140},
  year={2022}
}
```

## 参考文献：

> [1] Su et al., 2022 "A Contrastive Framework for Neural Text Generation", NeurIPS 2022

> [2] Su and Collier, 2022 "Contrastive Search Is What You Need For Neural Text Generation", Arxiv 2022

> [3] Fan et al., 2018 "Hierarchical Neural Story Generation", ACL 2018

> [4] Holtzman et al., 2020 "The Curious Case of Neural Text Degeneration", ICLR 2020

> [5] Zhang et al., 2022 "OPT: Open Pre-trained Transformer Language Models", Arxiv 2022

> [6] He et al., 2016 "Deep Residual Learning for Image Recognition", CVPR 2016

*- 作者：Yixuan Su 和 Tian Lan*

## 致谢：

感谢 Joao Gante（[@joaogante](https://huggingface.co/joaogante)）、Patrick von Platen（[@patrickvonplaten](https://huggingface.co/patrickvonplaten)）和 Sylvain Gugger（[@sgugger](https://github.com/sgugger)）在把本文提到的对比搜索加入 `transformers` 库的过程中给予的帮助和指导。
