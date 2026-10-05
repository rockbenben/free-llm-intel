---
vendor: huggingface
title: 更快的训练与推理：Habana Gaudi®2 对比 Nvidia A100 80GB
original_title: Faster Training and Inference: Habana Gaudi®2 vs Nvidia A100 80GB
url: https://huggingface.co/blog/habana-gaudi-2-benchmark
date: 2023-09-07
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: d7874a607b31
---

# 更快的训练与推理：Habana Gaudi®2 对比 Nvidia A100 80GB

本文另有中文版本可用：[简体中文](https://huggingface.co/blog/zh/habana-gaudi-2-benchmark)。

在这篇文章中，你将了解如何使用 [Habana® Gaudi®2](https://habana.ai/training/gaudi2/) 加速模型训练与推理，并用 🤗 [Optimum Habana](https://huggingface.co/docs/optimum/habana/index) 训练更大的模型。随后我们给出一系列基准测试，包括 BERT 预训练、Stable Diffusion 推理和 T5-3B 微调，用来衡量第一代 Gaudi、Gaudi2 与 Nvidia A100 80GB 之间的性能差距。剧透——Gaudi2 无论是训练还是推理都比 Nvidia A100 80GB 快约一倍！

[Gaudi2](https://habana.ai/training/gaudi2/) 是 Habana Labs 设计的第二代 AI 硬件加速器。单台服务器含 8 块加速设备，每块 96GB 内存（第一代 Gaudi 为 32GB，A100 80GB 为 80GB）。Habana 的 SDK [SynapseAI](https://developer.habana.ai/) 对一代 Gaudi 和 Gaudi2 通用。这意味着 🤗 Optimum Habana——它在 🤗 Transformers、🤗 Diffusers 库与 SynapseAI 之间提供了非常友好的接口——**在 Gaudi2 上与一代 Gaudi 的用法完全一致！** 所以如果你已经有一代 Gaudi 的现成训练或推理工作流，我们鼓励你直接在 Gaudi2 上尝试，一行都不用改。

## 如何获得 Gaudi2 的访问权限？

Intel 和 Habana 提供 Gaudi2 的方式中，简单且省钱的一种是 Intel Developer Cloud。要在上面开始使用 Gaudi2，请按以下步骤：

- 前往 [Intel Developer Cloud 着陆页](https://www.intel.com/content/www/us/en/developer/tools/devcloud/services.html)，登录你的账户，没有就先注册。
- 进入 [Intel Developer Cloud 管理控制台](https://scheduler.cloud.intel.com/#/systems)。
- 选择 *Habana Gaudi2 Deep Learning Server featuring eight Gaudi2 HL-225H mezzanine cards and latest Intel® Xeon® Processors*，然后点击右下角的 *Launch Instance*，如下图所示。  ![Cloud Architecture](https://huggingface.co/blog/assets/habana-gaudi-2-benchmark/launch_instance.png)
- 然后你可以提交实例申请：  ![Cloud Architecture](https://huggingface.co/blog/assets/habana-gaudi-2-benchmark/request_instance.png)
- 申请获批后，重做第 3 步并点击 *Add OpenSSH Publickey*，添加一种支付方式（信用卡或促销码）和一个 SSH 公钥——公钥可用 `ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa` 生成。每次添加支付方式或 SSH 公钥后，可能会被重定向回第 3 步。
- 重做第 3 步，然后点击 *Launch Instance*。你需要接受拟议的服务条款，实例才会真正启动。
- 前往 [Intel Developer Cloud 管理控制台](https://scheduler.cloud.intel.com/#/systems)，点击 *View Instances* 标签页。
- 你就可以复制 SSH 命令远程访问你的 Gaudi2 实例了！

> 如果你终止了实例、之后还想再用 Gaudi2，得把整个流程重走一遍。

关于该流程的更多信息见[这里](https://scheduler.cloud.intel.com/public/Intel_Developer_Cloud_Getting_Started.html)。

## 基准测试

我们为评估一代 Gaudi、Gaudi2 和 A100 80GB 在训练与推理上、对不同规模模型的能力，做了若干基准测试。

### 预训练 BERT

几个月前，Hugging Face 的技术负责人 [Philipp Schmid](https://huggingface.co/philschmid) 演示了[如何用 🤗 Optimum Habana 在 Gaudi 上预训练 BERT](https://huggingface.co/blog/pretraining-bert)。那次跑了 65k 训练步，每设备 batch size 为 32 条样本（即 8*32=256 总量），总训练时长 8 小时 53 分钟（这次运行的 TensorBoard 日志见[这里](https://huggingface.co/philschmid/bert-base-uncased-2022-habana-test-6/tensorboard?scroll=1#scalars)）。

我们在 Gaudi2 上用同样的脚本、同样的超参数重跑，得到总训练时长 2 小时 55 分钟（日志见[这里](https://huggingface.co/regisss/bert-pretraining-gaudi-2-batch-size-32/tensorboard?scroll=1#scalars)）。**什么都没改，Gaudi2 就拿到了 3.04 倍加速。**

由于 Gaudi2 每设备内存约为一代 Gaudi 的 3 倍，可以利用更大的容量上更大的 batch。这会让 HPU 有更多活儿可干，也让开发者能尝试一代 Gaudi 够不着的一整段超参范围。用每设备 64 条样本（总计 512）的 batch size，我们 20k 步就达到了与之前 65k 步相似的 loss 收敛，总训练时长 1 小时 33 分钟（日志见[这里](https://huggingface.co/regisss/bert-pretraining-gaudi-2-batch-size-64/tensorboard?scroll=1#scalars)）。这一配置的吞吐高出 1.16 倍，而新 batch size 大幅加速了收敛。**整体而言，与一代 Gaudi 相比，Gaudi2 把总训练时间缩短到 1/5.75、吞吐提升到 3.53 倍**。

**Gaudi2 相对 A100 也有加速**：batch size 32 时 1580.2 samples/s 对 981.6；batch size 64 时 1835.8 samples/s 对 1082.6。这与 Habana 在 BERT 预训练第一阶段、batch size 64 下[宣称的](https://habana.ai/training/gaudi2/) 1.8 倍加速一致。

下表为我们得到的一代 Gaudi、Gaudi2 与 Nvidia A100 80GB 的吞吐：

|  | 一代 Gaudi（BS=32） | Gaudi2（BS=32） | Gaudi2（BS=64） | A100（BS=32） | A100（BS=64） |
| --- | --- | --- | --- | --- | --- |
| 吞吐（samples/s） | 520.2 | 1580.2 | 1835.8 | 981.6 | 1082.6 |
| 加速比 | x1.0 | x3.04 | x3.53 | x1.89 | x2.08 |

*BS* 为每设备 batch size。Gaudi 运行使用混合精度（bf16/fp32），A100 运行使用 fp16。所有运行都是 *8 设备*上的*分布式*运行。

### 用 Stable Diffusion 文生图

🤗 Optimum Habana 1.3 版的主要新特性之一是[对 Stable Diffusion 的支持](https://huggingface.co/docs/optimum/habana/usage_guides/stable_diffusion)。现在在 Gaudi 上从文本生成图像非常容易。与 🤗 Diffusers 在 GPU 上不同，图像是按批次生成的。由于模型编译耗时，前两批会慢于后续迭代。本基准在计算一代 Gaudi 和 Gaudi2 的吞吐时剔除了这两次迭代。

[这个脚本](https://github.com/huggingface/optimum-habana/tree/main/examples/stable-diffusion)以 8 条样本的 batch size 运行，使用 [`Habana/stable-diffusion`](https://huggingface.co/Habana/stable-diffusion) 的 Gaudi 配置。

我们得到的结果如下表所示，与 Habana [公布的数字](https://developer.habana.ai/resources/habana-models-performance/)一致。**Gaudi2 的延迟比一代 Gaudi 快 3.51 倍（3.25s 对 0.925s）、比 Nvidia A100 快 2.84 倍（2.63s 对 0.925s）**，而且能支撑更大的 batch size。

|  | 一代 Gaudi（BS=8） | Gaudi2（BS=8） | A100（BS=1） |
| --- | --- | --- | --- |
| 延迟（s/img） | 3.25 | 0.925 | 2.63 |
| 加速比 | x1.0 | x3.51 | x1.24 |

*更新：随着 SynapseAI 1.10 和 Optimum Habana 1.6 给一代 Gaudi 与 Gaudi2 带来额外加速，上表数字已做更新。*

*BS* 为 batch size。Gaudi 运行使用 *bfloat16* 精度，A100 运行使用 *fp16* 精度（更多信息见[这里](https://huggingface.co/docs/diffusers/optimization/fp16)）。所有运行都是*单设备*运行。

### 微调 T5-3B

凭借每设备 96 GB 内存，Gaudi2 可以跑大得多的模型。例如，我们成功微调了 T5-3B（含 30 亿参数），且只启用了 gradient checkpointing 这一种内存优化。这在一代 Gaudi 上做不到。这次运行的日志见[这里](https://huggingface.co/regisss/t5-3b-summarization-gaudi-2/tensorboard?scroll=1#scalars)——模型用[这个脚本](https://github.com/huggingface/optimum-habana/tree/main/examples/summarization)在 CNN DailyMail 数据集上做文本摘要微调。

我们取得的结果见下表。**Gaudi2 比 A100 80GB 快 2.44 倍。** 我们观察到 Gaudi2 上这里放不下大于 1 的 batch size，原因是运行第一次迭代时累积操作的计算图占用了内存空间。Habana 正在未来版本的 SynapseAI 中优化内存占用。我们期待用更新版本的 Habana SDK 扩展这组基准，并尝试 [DeepSpeed](https://www.deepspeed.ai/)，看看同样的趋势是否成立。

|  | 一代 Gaudi | Gaudi2（BS=1） | A100（BS=16） |
| --- | --- | --- | --- |
| 吞吐（samples/s） | N/A | 19.7 | 8.07 |
| 加速比 | / | x2.44 | x1.0 |

*BS* 为每设备 batch size。Gaudi2 与 A100 运行使用 fp32 并启用 gradient checkpointing。所有运行都是 *8 设备*上的*分布式*运行。

## 结论

这篇文章分享了我们对 Gaudi2 的第一手体验。由于 Habana 的 SDK SynapseAI 对一代 Gaudi 和 Gaudi2 完全兼容，从一代到 Gaudi2 的过渡毫无缝隙——未来版本提出的新优化将同时惠及两者。

你已经看到 Habana Gaudi2 相对一代 Gaudi 大幅提升性能，并在训练和推理上都达到约 Nvidia A100 80GB 两倍的吞吐速度。

你现在也知道如何通过 Intel Developer Zone 配置一台 Gaudi2 实例。去看看[示例](https://github.com/huggingface/optimum-habana/tree/main/examples)，用 🤗 Optimum Habana 在 Gaudi2 上轻松运行。

如果你想用最新的 AI 硬件加速器和软件库来加速你的机器学习训练与推理工作流，看看我们的 [Expert Acceleration Program](https://huggingface.co/support)。想了解更多 Habana 方案，[在这里读我们的合作介绍](https://huggingface.co/hardware/habana)并[联系他们](https://habana.ai/contact-us/)。想了解 Hugging Face 让 AI 硬件加速器更易用的努力，见我们的 [Hardware Partner Program](https://huggingface.co/hardware)。

### 相关话题

- [Getting Started on Transformers with Habana Gaudi](https://huggingface.co/blog/getting-started-habana)
- [Accelerate Transformer Model Training with Hugging Face and Habana Labs](https://developer.habana.ai/events/accelerate-transformer-model-training-with-hugging-face-and-habana-labs/)

感谢阅读！如有任何问题，欢迎通过 [Github](https://github.com/huggingface/optimum-habana) 或[论坛](https://discuss.huggingface.co/c/optimum/59) 联系我，也可以在 [LinkedIn](https://www.linkedin.com/in/regispierrard/) 上找到我。
