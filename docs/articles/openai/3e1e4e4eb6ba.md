---
vendor: openai
title: AI 与效率
original_title: AI and efficiency
url: https://openai.com/index/ai-and-efficiency
date: 2022-06-09
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# AI 与效率

阅读论文（在新窗口打开）。

我们发布的一项分析显示，自 2012 年以来，在 ImageNet 分类上训练一个达到相同性能的神经网络所需的算力，每 16 个月减少一半（factor of 2）。与 2012 年相比，如今把一个神经网络训练到 AlexNet 水平所需的算力少了 44 倍（作为对比，同期摩尔定律只会带来 11 倍的成本改善）。我们的结果表明：对于近期高投入的 AI 任务，算法进步带来的收益已超过经典硬件效率的提升。

*引言参考：ImageNet[1](https://openai.com/index/ai-and-efficiency/#citation-bottom-1)、AlexNet[2](https://openai.com/index/ai-and-efficiency/#citation-bottom-2)、摩尔定律[3](https://openai.com/index/ai-and-efficiency/#citation-bottom-3)*

算法改进是推动 AI 进步的关键因素。尽管度量算法总体进步比度量算力趋势更难，寻找能照亮它的指标仍然重要。[4](https://openai.com/index/ai-and-efficiency/#citation-bottom-4)

训练到 AlexNet 水平性能所用的总算力（以 teraflops/s-days 计）。任意时点的最低算力点以蓝色显示，所有测量点以灰色显示。[2](https://openai.com/index/ai-and-efficiency/#citation-bottom-2:2) [5](https://openai.com/index/ai-and-efficiency/#citation-bottom-5) [6](https://openai.com/index/ai-and-efficiency/#citation-bottom-6) [7](https://openai.com/index/ai-and-efficiency/#citation-bottom-7) [8](https://openai.com/index/ai-and-efficiency/#citation-bottom-8) [9](https://openai.com/index/ai-and-efficiency/#citation-bottom-9) [10](https://openai.com/index/ai-and-efficiency/#citation-bottom-10) [11](https://openai.com/index/ai-and-efficiency/#citation-bottom-11) [12](https://openai.com/index/ai-and-efficiency/#citation-bottom-12) [13](https://openai.com/index/ai-and-efficiency/#citation-bottom-13) [14](https://openai.com/index/ai-and-efficiency/#citation-bottom-14) [15](https://openai.com/index/ai-and-efficiency/#citation-bottom-15) [16](https://openai.com/index/ai-and-efficiency/#citation-bottom-16)

## 度量效率

算法效率可以定义为：训练出某一特定能力所需算力的降低。在排序这类经典计算机科学问题上，效率是我们衡量算法进展的首要方式。传统问题（如排序）上的效率收益比 ML 更容易度量，因为任务难度有更清晰的度量。[A](https://openai.com/index/ai-and-efficiency/#citation-bottom-A) 不过，我们可以通过固定性能，把效率视角应用到机器学习中。效率趋势可以在不同领域间比较，比如 DNA 测序[17](https://openai.com/index/ai-and-efficiency/#citation-bottom-17)（10 个月翻倍）、太阳能[18](https://openai.com/index/ai-and-efficiency/#citation-bottom-18)（6 年翻倍）和晶体管密度[3](https://openai.com/index/ai-and-efficiency/#citation-bottom-3:2)（2 年翻倍）。

在我们的分析中，主要利用开源重实现[19](https://openai.com/index/ai-and-efficiency/#citation-bottom-19) [20](https://openai.com/index/ai-and-efficiency/#citation-bottom-20) [21](https://openai.com/index/ai-and-efficiency/#citation-bottom-21)，在长时间跨度上度量达到 AlexNet 水平性能的进展。我们在 ImageNet 上 ResNet-50 水平性能也看到了类似速率的训练效率提升（17 个月翻倍）。[7](https://openai.com/index/ai-and-efficiency/#citation-bottom-7:2) [16](https://openai.com/index/ai-and-efficiency/#citation-bottom-16:2) 在更短的时间尺度上，翻译、围棋和 Dota 2 中的提升速率更快：

- 在翻译领域，Transformer[22](https://openai.com/index/ai-and-efficiency/#citation-bottom-22) 三年后以少 61 倍的训练算力超越了 seq2seq[23](https://openai.com/index/ai-and-efficiency/#citation-bottom-23) 在 WMT'14 英法翻译上的性能。
- 我们估计 AlphaZero[24](https://openai.com/index/ai-and-efficiency/#citation-bottom-24) 一年后用少 8 倍的算力达到了 AlphaGoZero[25](https://openai.com/index/ai-and-efficiency/#citation-bottom-25) 水平的性能。
- OpenAI Five Rerun 用少 5 倍的训练算力，在此后 3 个月超越了 OpenAI Five[26](https://openai.com/index/ai-and-efficiency/#citation-bottom-26)（后者击败了世界冠军战队 [OG⁠（在新窗口打开）](https://liquipedia.net/dota2/OG)）。

把 2012 年的算力与 2019 年的算力看作不等价是有帮助的，就像美元需要按通胀调整一样。同样一份算力，2019 年能比 2012 年完成更多的事。一种理解方式是：某些类型的 AI 研究进展分两个阶段，类似于半导体领域的“tick-tock”开发模式；新能力（“tick”）通常需要大量算力投入才能获得，随后这些能力的精炼版本（“tock”）因工艺改进而部署效率大幅提升。

算法效率的提升让研究者在给定的时间和资金内能做更多感兴趣的实验。除了作为总体进步的度量，算法效率收益还会以某种类似“拥有更多算力”的方式加速未来的 AI 研究。

## AI 进步的其他度量

除效率之外，还有许多指标可以照亮 AI 的总体算法进步。以美元计的训练成本[28](https://openai.com/index/ai-and-efficiency/#citation-bottom-28)与之相关，但对算法进步的聚焦不如效率窄，因为它还受底层硬件改进、硬件利用率和云基础设施的影响。样本效率在低数据量场景中是关键——许多感兴趣的任务正是如此。更快训练模型的能力[29](https://openai.com/index/ai-and-efficiency/#citation-bottom-29)同样能加速研究，可以视为所关注学习能力的可并行化程度[30](https://openai.com/index/ai-and-efficiency/#citation-bottom-30)的一种度量。我们也认为以下口径的推理效率提升是有意义的——GPU 时间[31](https://openai.com/index/ai-and-efficiency/#citation-bottom-31)、参数量[16](https://openai.com/index/ai-and-efficiency/#citation-bottom-16:3)和 FLOPs——但主要缘于其经济含义[B](https://openai.com/index/ai-and-efficiency/#citation-bottom-B)，而非对未来研究进步的影响。Shufflenet[13](https://openai.com/index/ai-and-efficiency/#citation-bottom-13:2) 在 5 年内以 18 倍的推理效率提升达到 AlexNet 水平性能（15 个月翻倍），这提示训练效率与推理效率可能以相近的速率改进。数据集/环境/基准的创建，是让特定 AI 能力更可控量的有力方法。

## 主要局限

- 我们只有少量任务上的少量算法效率数据点。我们观察到的效率趋势在多大程度上能泛化到其他 AI 任务尚不清楚。系统化的度量可以澄清 AI 领域是否存在算法版的“摩尔定律”[C](https://openai.com/index/ai-and-efficiency/#citation-bottom-C)，若存在，其性质如何。我们认为这是一个非常有趣的开放问题。我们猜测，在相似任务上更可能观察到相似速率的效率进步。所谓相似任务，指 AI 这些子领域内的任务——业界认同我们在这些领域已见实质进步，且投入（算力和/或研究员时间）水平相当。
- 尽管我们相信 AlexNet 代表了巨大的进步，本分析并不试图量化该进步。更一般地，一个能力首次被创造出来时，算法突破可能把所需资源从完全不可行[D](https://openai.com/index/ai-and-efficiency/#citation-bottom-D)降到只是很高。我们认为，新能力通常比此处展示的这类效率提升，占总体概念进步更大的份额。
- 本分析聚焦优化后模型的最终训练运行成本，而非总开发成本。一些算法改进让模型更易于训练——使能稳定训练并取得良好最终表现的超参数空间大得多。另一方面，架构搜索会拉大最终训练运行成本与总训练成本之间的差距。
- 我们不推测效率趋势外推到未来的程度[E](https://openai.com/index/ai-and-efficiency/#citation-bottom-E)，只是呈现结果并讨论若趋势持续的含义。

## 度量与 AI 政策

我们相信[32](https://openai.com/index/ai-and-efficiency/#citation-bottom-32)，更加重视对 AI 系统的度量与评估——无论是技术属性还是社会影响——会改善 AI 相关政策制定。我们认为这类度量计划能照亮政策中的重要问题；我们的《AI 与算力》[4](https://openai.com/index/ai-and-efficiency/#citation-bottom-4:2)分析建议决策者增加对学术界算力资源的资助，使学术研究能够复现、验证并扩展工业研究。本效率分析则提示：决策者可以通过更密切地评估 AI 系统效率改进的速率，形成关于部署 AI 能力成本——以及这些成本将如何随时间改变——的准确直觉。

## 未来对效率的跟踪

如果大规模算力对取得语言、游戏等领域总体 SOTA 仍然重要，那么就有必要下功夫度量以更少算力取得的显著进步（这些贡献往往来自学术机构）。在有意义的能力上取得训练效率 SOTA 的模型，是扩展规模、进而可能取得总体顶尖表现的有希望的候选。另外，弄清楚算法效率改进是直接的[F](https://openai.com/index/ai-and-efficiency/#citation-bottom-F)，因为它们不过是所有实验都产生的学习曲线中一个特别有意义的切片。

我们还认为，度量效率 SOTA 的长期趋势将有助于为总体算法进步描绘定量图景。我们观察到硬件与算法效率收益是相乘的，并且在有意义的时间跨度上可以达到相似的量级——这表明一个好的 AI 进步模型应当整合两者的度量。

我们的结果表明，对于高投入（研究员时间和/或算力）的 AI 任务，算法效率可能超过硬件效率（摩尔定律）的收益。摩尔定律提出于 1965 年，当时集成电路只有 64 个晶体管（6 次翻倍），而天真地外推它预言了个人电脑和智能手机（iPhone 11 有 85 亿个晶体管）。如果我们观察到 AI 算法效率数十年的指数改进，它会把我们带向什么？我们不确定。这些结果让我们提出这个问题，对我们而言是一个温和的信号，指向一个拥有强大 AI 服务与技术的未来。

基于以上所有原因，我们将开始公开跟踪效率 SOTA。我们从视觉和翻译效率基准（ImageNet[G](https://openai.com/index/ai-and-efficiency/#citation-bottom-G) 和 WMT14）开始，未来会考虑增加更多基准。我们相信这些基准上存在我们尚不了解的效率 SOTA，鼓励研究社区[在此提交⁠（在新窗口打开）](https://github.com/openai/ai-and-efficiency)（我们会为原作者与合作者署名）。

行业领导者、政策制定者、经济学家和潜在的研究者都在努力更好地理解 AI 进步，并决定应当投入多少关注、投向何处。度量工作可以帮助这些决策落到实处。如果你对这类工作感兴趣，[考虑申请⁠](https://openai.com/careers/) OpenAI Foresight 或 Policy 团队的工作！

## 脚注

- A 在排序的例子中，问题的“难度”是列表的长度。常用算法快速排序的成本用 Big O 记号表示：O(n log n)。
- B 对于成功部署的系统，推理成本主导总成本。推理成本随系统使用量增长，而训练成本只需支付一次。
- C 全文中，我们把摩尔定律指长期观察到的、稳定的美元/FLOP 每 2 年翻倍。也可以把摩尔定律解读为美元/FLOP 的趋势——它近年已放缓。
- D 例如，算法进步可能把某些任务的复杂度类别从指数级成本变为多项式级成本。这类对重要能力的效率收益难以直接观察，尽管可以通过渐近分析或外推经验得到的缩放定律来观察。
- E 对这些主题做出可信预测是一项庞大的工作，我们宁愿在此回避，也不愿草率处理。
- F 事实上，这项工作主要通过训练 PyTorch 示例模型完成，并对早期学习做了改进性的调整。
- G ImageNet 是视觉基准唯一允许的训练数据来源。不允许人工标注、其他图像或其他数据。自动数据增强是允许的。

## 参考文献

- 1 Deng, J., Dong, W., Socher, R., Li, L.-J., Li, K., & Fei-Fei, L. (2009). “[ImageNet: A Large-Scale Hierarchical Image Database⁠（在新窗口打开）](http://www.image-net.org/papers/imagenet_cvpr09.pdf).” In CVPR09.
- 2 Krizhevsky, A., Sutskever, I., & Hinton, G. E. (2012). “[Imagenet classification with deep convolutional neural networks⁠（在新窗口打开）](https://papers.nips.cc/paper/4824-imagenet-classification-with-deep-convolutional-neural-networks.pdf).” In F. Pereira, C. J. C. Burges, L. Bottou, & K. Q. Weinberger (Eds.), Advances in Neural Information Processing Systems 25 (pp. 1097–1105). Curran Associates, Inc.
- 3 Moore, G. E. (1965). “[Cramming more components onto integrated circuits⁠（在新窗口打开）](https://newsroom.intel.com/wp-content/uploads/sites/11/2018/05/moores-law-electronics.pdf).” Electronics 38(8).
- 4 Amodei, D. & Hernandez, D. (2018). “[AI and Compute⁠](https://openai.com/index/ai-and-compute/).”
- 5 Szegedy, C., Liu, W., Jia, Y., Sermanet, P., Reed, S., Anguelov, D., Erhan, D., Vanhoucke, V., & Rabinovich, A. (2014). “[Going deeper with convolutions⁠（在新窗口打开）](https://arxiv.org/abs/1409.4842).”
- 6 Simonyan, K. & Zisserman, A. (2014). “[Very deep convolutional networks for large-scale image recognition⁠（在新窗口打开）](https://arxiv.org/abs/1409.1556).”
- 7 He, K., Zhang, X., Ren, S., & Sun, J. (2015). “[Deep residual learning for image recognition⁠（在新窗口打开）](https://arxiv.org/abs/1512.03385).”
- 8 Iandola, F. N., Han, S., Moskewicz, M. W., Ashraf, K., Dally, W. J., & Keutzer, K. (2016). “[Squeezenet: Alexnet-level accuracy with 50x fewer parameters and <0.5mb model size⁠（在新窗口打开）](https://arxiv.org/abs/1602.07360).”
- 9 Zagoruyko, S. & Komodakis, N. (2016). “[Wide residual networks⁠（在新窗口打开）](https://arxiv.org/abs/1605.07146).”
- 10 Xie, S., Girshick, R., Dollár, P., Tu, Z., & He, K. (2016). “[Aggregated residual transformations for deep neural networks⁠（在新窗口打开）](https://arxiv.org/abs/1611.05431).”
- 11 Huang, G., Liu, Z., van der Maaten, L., & Weinberger, K. Q. (2016). “[Densely connected convolutional networks⁠（在新窗口打开）](https://arxiv.org/abs/1608.06993).”
- 12 Howard, A. G., Zhu, M., Chen, B., Kalenichenko, D., Wang, W., Weyand, T., Andreetto, M., & Adam, H. (2017). “[Mobilenets: Efficient convolutional neural networks for mobile vision applications⁠（在新窗口打开）](https://arxiv.org/pdf/1704.04861.pdf).”
- 13 Zhang, X., Zhou, X., Lin, M., & Sun, J. (2017). “[Shufflenet: An extremely efficient convolutional neural network for mobile devices⁠（在新窗口打开）](https://arxiv.org/abs/1707.01083).”
- 14 Sandler, M., Howard, A., Zhu, M., Zhmoginov, A., & Chen, L.-C. (2018). “[Mobilenetv2: Inverted residuals and linear bottlenecks⁠（在新窗口打开）](https://arxiv.org/abs/1801.04381).”
- 15 Ma, N., Zhang, X., Zheng, H.-T., & Sun, J. (2018). “[Practical guidelines for efficient cnn architecture design⁠（在新窗口打开）](https://arxiv.org/abs/1807.11164).”
- 16 Tan, M. & Le, Q. V. (2019). “[Efficientnet: Rethinking model scaling for convolutional neural networks⁠（在新窗口打开）](https://arxiv.org/abs/1905.11946).”
- 17 Sawyer, Eric (2011). “[High Throughput Sequencing and Cost Trends⁠（在新窗口打开）](https://www.nature.com/scitable/blog/bio2.0/high_throughput_sequencing_and_cost/).”
- 18 Roberts, David (2019). “[Getting to 100% renewables requires cheap energy storage. But how cheap?⁠（在新窗口打开）](https://www.vox.com/energy-and-environment/2019/8/9/20767886/renewable-energy-storage-cost-electricity).”
- 19 Paszke, A., Gross, S., Chintala, S., Chanan, G., Yang, E., DeVito, Z., Lin, Z., Desmaison, A., Antiga, L., & Lerer, A. (2017). “[Automatic differentiation in PyTorch. In NIPS Autodiff Workshop⁠（在新窗口打开）](https://openreview.net/pdf?id=BJJsrmfCZ).”
- 20 Huang, J. (2017). “[Shufflenet in pytorch⁠（在新窗口打开）](https://github.com/jaxony/shufflenet).”
- 21 Xiao, H. (2017). “[Pytorch mobilenet implementation of “mobilenets: Efficient convolutional neural networks for mobile vision applications”⁠（在新窗口打开）](https://github.com/marvis/pytorch-mobilenet.).”
- 22 Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., & Polosukhin, I. (2017). “[Attention is all you need. CoRR, abs/1706.03762⁠（在新窗口打开）](https://arxiv.org/abs/1706.03762).”
- 23 Sutskever, I., Vinyals, O., & Le, Q. V. (2014). “[Sequence to sequence learning with neural networks. CoRR, abs/1409.3215⁠（在新窗口打开）](https://arxiv.org/abs/1409.3215).”
- 24 Silver, D., Hubert, T., Schrittwieser, J., Antonoglou, I., Lai, M., Guez, A., Lanctot, M., Sifre, L., Kumaran, D., Graepel, T., Lillicrap, T., Simonyan, K., & Hassabis, D. (2018). “[A general reinforcement learning algorithm that masters chess, shogi, and go through self-play. Science, 362(6419), 1140–1144⁠（在新窗口打开）](https://arxiv.org/abs/1712.01815).”
- 25 Silver, D., Schrittwieser, J., Simonyan, K., Antonoglou, I., Huang, A., Guez, A., Hubert, T., Baker, L., Lai, M., Bolton, A., Chen, Y., Lillicrap, T., Hui, F., Sifre, L., van den Driessche, G., Graepel, T., & Hassabis, D. (2017). “[Mastering the game of go without human knowledge. Nature, 550, 354–⁠（在新窗口打开）](https://www.nature.com/articles/nature24270).”
- 26 OpenAI et. al., :, Berner, C., Brockman, G., Chan, B., Cheung, V., Łoski, P., Dennison, C., Farhi, D., Fischer, Q., Hashme, S., Hesse, C., Józefowicz, R., Gray, S., Olsson, C., Pachocki, J., Petrov, M., de Oliveira Pinto, H. P., Raiman, J., Salimans, T., Schlatter, J., Schneider, J., Sidor, S., Sutskever, I., Tang, J., Wolski, F., & Zhang, S. (2019). “[Dota 2 with Large Scale Deep Reinforcement Learning⁠（在新窗口打开）](https://cdn.openai.com/dota-2.pdf).”
- 27 Coleman, C. A., Narayanan, D., Kang, D., Zhao, T., Zhang, J., Nardi, L., Bailis, P., Olukotun, K., Ré, C., & Zaharia, M. (2017). “[The Dawn of AI: Performance Analysis and Cost Modeling of Machine Learning Algorithms⁠（在新窗口打开）](https://dawn.cs.stanford.edu/benchmark/papers/nips17-dawnbench.pdf).”
- 28 Paszke, A., Gross, S., Chintala, S., Chanan, G., Yang, E., DeVito, Z., Lin, Z., Desmaison, A., Antiga, L., & Lerer, A. (2017). “[DAWNBench: An End-to-End Deep Learning Benchmark and Competition. NIPS ML SYSTEMS WORKSHOP, 2017⁠（在新窗口打开）](https://openreview.net/pdf?id=BJJsrmfCZ).”
- 29 Raymond Perrault, Yoav Shoham 等 (2019). “[The AI Index 2019 Annual Report”. Technical report, AI Index Steering Committee, Human-Centered AI Institute, Stanford University, Stanford, CA⁠（在新窗口打开）](https://hai.stanford.edu/sites/default/files/ai_index_2019_report.pdf).”
- 30 McCandlish, S., Kaplan, J., Amodei, D., & Team, O. D. (2018). “[An empirical model of large-batch training”⁠（在新窗口打开）](https://arxiv.org/pdf/1812.06162.pdf).”
- 31 van den Oord, A., Li, Y., Babuschkin, I., Simonyan, K., Vinyals, O., Kavukcuoglu, K., van den Driessche, G., Lockhart, E., Cobo, L. C., Stimberg, F., Casagrande, N., Grewe, D., Noury, S., Dieleman, S., Elsen, E., Kalchbrenner, N., Zen, H., Graves, A., King, H., Walters, T., Belov, D., & Hassabis, D. (2017). “[Parallel wavenet: Fast high-fidelity speech synthesis.⁠（在新窗口打开）](https://arxiv.org/abs/1711.10433).”
- 32 Jack Clark (2019). “[Written Testimony of Jack Clark, Policy Director at OpenAI. Hearing on “Artificial Intelligence: Societal and Ethical Implications” before the House Committee on Science, Space, & Technology⁠（在新窗口打开）](https://science.house.gov/imo/media/doc/Clark%20Testimony.pdf).”

## 作者

Danny Hernandez, Tom Brown

## 致谢

感谢以下人士就本文进行的有益讨论和/或反馈：Dario Amodei、Jack Clark、Alec Radford、Paul Christiano、Sam McCandlish、Ilya Sutskever、Jacob Steinhardt、Jared Kaplan、Amanda Askell、John Schulman、Jacob Hilton、Asya Bergal、Katja Grace、Ryan Carey、Nicholas Joseph、Geoffrey Irving、Jeff Clune 和 Ashley Pilipiszyn。

感谢 Justin Jay Wang 负责设计。

感谢 Niki Parmar 提供原始 [transformer⁠（在新窗口打开）](https://arxiv.org/abs/1706.03762)学习曲线的相关数据点。

也感谢 Mingxing Tan 提供 [EfficientNet⁠（在新窗口打开）](https://arxiv.org/abs/1905.11946)学习曲线的相关数据点，并运行了一个减少 warmup 的实验。
