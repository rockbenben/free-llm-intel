---
vendor: openai
title: AI and efficiency
original_title: AI and efficiency
url: https://openai.com/index/ai-and-efficiency
date: 2022-06-09
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: b1a1b30c8a1b
---

OpenAI

May 5, 2020

Publication

# AI and efficiency

Read paper

(opens in a new window)

Loading…

We’re releasing an analysis showing that since 2012 the amount of compute needed to train a neural net to the same performance on ImageNet classification has been decreasing by a factor of 2 every 16 months. Compared to 2012, it now takes 44 times less compute to train a neural network to the level of AlexNet (by contrast, Moore’s Law would yield an 11x cost improvement over this period). Our results suggest that for AI tasks with high levels of recent investment, algorithmic progress has yielded more gains than classical hardware efficiency.

*Intro references: Imagenet[1](https://openai.com/index/ai-and-efficiency/#citation-bottom-1), AlexNet[2](https://openai.com/index/ai-and-efficiency/#citation-bottom-2), Moore’s Law[3](https://openai.com/index/ai-and-efficiency/#citation-bottom-3)*

Algorithmic improvement is a key factor driving the advance of AI. It’s important to search for measures that shed light on overall algorithmic progress, even though it’s harder than measuring such trends in compute.[4](https://openai.com/index/ai-and-efficiency/#citation-bottom-4)

Loading...

Total amount of compute in teraflops/s-days used to train to AlexNet level performance. Lowest compute points at any given time shown in blue, all points measured shown in gray.[2](https://openai.com/index/ai-and-efficiency/#citation-bottom-2:2), [5](https://openai.com/index/ai-and-efficiency/#citation-bottom-5), [6](https://openai.com/index/ai-and-efficiency/#citation-bottom-6), [7](https://openai.com/index/ai-and-efficiency/#citation-bottom-7), [8](https://openai.com/index/ai-and-efficiency/#citation-bottom-8), [9](https://openai.com/index/ai-and-efficiency/#citation-bottom-9), [10](https://openai.com/index/ai-and-efficiency/#citation-bottom-10), [11](https://openai.com/index/ai-and-efficiency/#citation-bottom-11), [12](https://openai.com/index/ai-and-efficiency/#citation-bottom-12), [13](https://openai.com/index/ai-and-efficiency/#citation-bottom-13), [14](https://openai.com/index/ai-and-efficiency/#citation-bottom-14), [15](https://openai.com/index/ai-and-efficiency/#citation-bottom-15), [16](https://openai.com/index/ai-and-efficiency/#citation-bottom-16)

## Measuring efficiency

Algorithmic efficiency can be defined as reducing the compute needed to train a specific capability. Efﬁciency is the primary way we measure algorithmic progress on classic computer science problems like sorting. Efficiency gains on traditional problems like sorting are more straightforward to measure than in ML because they have a clearer measure of task difficulty.[A](https://openai.com/index/ai-and-efficiency/#citation-bottom-A) However, we can apply the efficiency lens to machine learning by holding performance constant. Efficiency trends can be compared across domains like DNA sequencing[17](https://openai.com/index/ai-and-efficiency/#citation-bottom-17) (10-month doubling), solar energy[18](https://openai.com/index/ai-and-efficiency/#citation-bottom-18) (6-year doubling), and transistor density[3](https://openai.com/index/ai-and-efficiency/#citation-bottom-3:2) (2-year doubling).

For our analysis, we primarily leveraged open-source re-implementations[19](https://openai.com/index/ai-and-efficiency/#citation-bottom-19), [20](https://openai.com/index/ai-and-efficiency/#citation-bottom-20), [21](https://openai.com/index/ai-and-efficiency/#citation-bottom-21) to measure progress on AlexNet level performance over a long horizon. We saw a similar rate of training efficiency improvement for ResNet-50 level performance on ImageNet (17-month doubling time).[7](https://openai.com/index/ai-and-efficiency/#citation-bottom-7:2), [16](https://openai.com/index/ai-and-efficiency/#citation-bottom-16:2) We saw faster rates of improvement over shorter timescales in Translation, Go, and Dota 2:

- Within translation, the Transformer[22](https://openai.com/index/ai-and-efficiency/#citation-bottom-22) surpassed seq2seq[23](https://openai.com/index/ai-and-efficiency/#citation-bottom-23) performance on English to French translation on WMT’14 with 61x less training compute 3 years later.
- We estimate AlphaZero[24](https://openai.com/index/ai-and-efficiency/#citation-bottom-24) took 8x less compute to get to AlphaGoZero[25](https://openai.com/index/ai-and-efficiency/#citation-bottom-25) level performance 1 year later.
- OpenAI Five Rerun required 5x less training compute to surpass OpenAI Five[26](https://openai.com/index/ai-and-efficiency/#citation-bottom-26) (which beat the world champions, [OG⁠(opens in a new window)](https://liquipedia.net/dota2/OG)) 3 months later.

It can be helpful to think of compute in 2012 not being equal to compute in 2019 in a similar way that dollars need to be inflation-adjusted over time. A fixed amount of compute could accomplish more in 2019 than in 2012. One way to think about this is that some types of AI research progress in two stages, similar to the “tick tock” model of development seen in semiconductors; new capabilities (the “tick”) typically require a significant amount of compute expenditure to obtain, then refined versions of those capabilities (the “tock”) become much more efficient to deploy due to process improvements.

Increases in algorithmic efficiency allow researchers to do more experiments of interest in a given amount of time and money. In addition to being a measure of overall progress, algorithmic efficiency gains speed up future AI research in a way that’s somewhat analogous to having more compute.

## Other measures of AI progress

In addition to efficiency, many other measures shed light on overall algorithmic progress in AI. Training cost in dollars[28](https://openai.com/index/ai-and-efficiency/#citation-bottom-28) is related, but less narrowly focused on algorithmic progress because it’s also affected by improvement in the underlying hardware, hardware utilization, and cloud infrastructure. Sample efficiency is key when we’re in a low data regime, which is the case for many tasks of interest. The ability to train models faster[29](https://openai.com/index/ai-and-efficiency/#citation-bottom-29) also speeds up research and can be thought of as a measure of the parallelizability[30](https://openai.com/index/ai-and-efficiency/#citation-bottom-30) of learning capabilities of interest. We also find increases in inference efficiency in terms of GPU time[31](https://openai.com/index/ai-and-efficiency/#citation-bottom-31), parameters[16](https://openai.com/index/ai-and-efficiency/#citation-bottom-16:3), and flops meaningful, but mostly as a result of their economic implications[B](https://openai.com/index/ai-and-efficiency/#citation-bottom-B) rather than their effect on future research progress. Shufflenet[13](https://openai.com/index/ai-and-efficiency/#citation-bottom-13:2) achieved AlexNet-level performance with an 18x inference efficiency increase in 5 years (15-month doubling time), which suggests that training efficiency and inference efficiency might improve at similar rates. The creation of datasets/​environments/​benchmarks is a powerful method of making specific AI capabilities of interest more measurable.

## Primary limitations

- We have only a small number of algorithmic efficiency data points on a few tasks. It’s unclear the degree to which the efficiency trends we’ve observed generalize to other AI tasks. Systematic measurement could make it clear whether an algorithmic equivalent to Moore’s Law[C](https://openai.com/index/ai-and-efficiency/#citation-bottom-C) in the domain of AI exists, and if it exists, clarify its nature. We consider this a highly interesting open question. We suspect we’re more likely to observe similar rates of efficiency progress on similar tasks. By similar tasks, we mean tasks within these sub-domains of AI, on which the field agrees we’ve seen substantial progress, and that have comparable levels of investment (compute and/or researcher time).
- Even though we believe AlexNet represented a lot of progress, this analysis doesn’t attempt to quantify that progress. More generally, the first time a capability is created, algorithmic breakthroughs may have reduced the resources required from totally infeasible[D](https://openai.com/index/ai-and-efficiency/#citation-bottom-D) to merely high. We think new capabilities generally represent a larger share of overall conceptual progress than observed efficiency increases of the type shown here.
- This analysis focuses on the final training run cost for an optimized model rather than total development costs. Some algorithmic improvements make it easier to train a model by making the space of hyperparameters that will train stably and get good final performance much larger. On the other hand, architecture searches increase the gap between the final training run cost and total training costs.
- We don’t speculate[E](https://openai.com/index/ai-and-efficiency/#citation-bottom-E) on the degree to which we expect efficiency trends will extrapolate in time, we merely present our results and discuss the implications if the trends persist.

## Measurement and AI policy

We believe[32](https://openai.com/index/ai-and-efficiency/#citation-bottom-32) that policymaking related to AI will be improved by a greater focus on the measurement and assessment of AI systems, both in terms of technical attributes and societal impact. We think such measurement initiatives can shed light on important questions in policy; our AI and Compute[4](https://openai.com/index/ai-and-efficiency/#citation-bottom-4:2) analysis suggests policymakers should increase funding for compute resources for academia, so that academic research can replicate, reproduce, and extend industry research. This efficiency analysis suggests that policymakers could develop accurate intuitions about the cost of deploying AI capabilities—and how these costs are going to alter over time—by more closely assessing the rate of improvements in efficiency for AI systems.

## Tracking efficiency going forward

If large scale compute continues to be important to achieving state of the art (SOTA) overall performance in domains like language and games then it’s important to put effort into measuring notable progress achieved with smaller amounts of compute (contributions often made by academic institutions). Models that achieve training efficiency state of the arts on meaningful capabilities are promising candidates for scaling up and potentially achieving overall top performance. Additionally, figuring out the algorithmic efficiency improvements are straightforward[F](https://openai.com/index/ai-and-efficiency/#citation-bottom-F) since they are just a particularly meaningful slice of the learning curves that all experiments generate.

We also think that measuring long run trends in efficiency SOTAs will help paint a quantitative picture of overall algorithmic progress. We observe that hardware and algorithmic efficiency gains are multiplicative and can be on a similar scale over meaningful horizons, which suggests that a good model of AI progress should integrate measures from both.

Our results suggest that for AI tasks with high levels of investment (researcher time and/or compute) algorithmic efficiency might outpace gains from hardware efficiency (Moore’s Law). Moore’s Law was coined in 1965 when integrated circuits had a mere 64 transistors (6 doublings) and naively extrapolating it out predicted personal computers and smartphones (an iPhone 11 has 8.5 billion transistors). If we observe decades of exponential improvement in the algorithmic efficiency of AI, what might it lead to? We’re not sure. That these results make us ask this question is a modest update for us towards a future with powerful AI services and technology.

For all these reasons, we’re going to start tracking efficiency SOTAs publicly. We’ll start with vision and translation efficiency benchmarks (ImageNet[G](https://openai.com/index/ai-and-efficiency/#citation-bottom-G) and WMT14), and we’ll consider adding more benchmarks over time. We believe there are efficiency SOTAs on these benchmarks we’re unaware of and encourage the research community to [submit them here⁠(opens in a new window)](https://github.com/openai/ai-and-efficiency) (we’ll give credit to original authors and collaborators).

Industry leaders, policymakers, economists, and potential researchers are all trying to better understand AI progress and decide how much attention they should invest and where to direct it. Measurement efforts can help ground such decisions. If you’re interested in this type of work, [consider applying⁠](https://openai.com/careers/) to work at OpenAI’s Foresight or Policy team!

Loading...

- [Compute Scaling](https://openai.com/research/index/?tags=compute-scaling)

## Footnotes

- AIn the sorting example, the “difficulty” of the problem is the length of the list. The cost for quicksort, a commonly used algorithm is denoted in Big O notation: O(nlog⁡n) O(n\log{}n) O(nlogn)
- BInference costs dominate total costs for successful deployed systems. Inference costs scale with usage of the system, whereas training costs only need to be paid once.
- CThroughout this post we refer to Moore’s Law as the consistent, long-observed 2-year doubling time of dollars/flop. One could also interpret Moore’s Law as the trend in dollars/flop, that has recently slowed down.
- DFor instance algorithmic progress could change the complexity class on some task from exponential to polynomial cost. Such efficiency gains on capabilities of interest are intractable to directly observe, though they may be observable through asymptotic analysis or extrapolating empirically derived scaling laws.
- EMaking credible forecasts on such topics is a substantial enterprise, we’d rather avoid here than give insufficient treatment.
- FIn fact, this work was primarily done by training PyTorch examples models, with tweaks to improve early learning.
- GImageNet is the only training data source allowed for the vision benchmark. No human captioning, other images, or other data is allowed. Automated augmentation is ok.

## References

- 1Deng, J., Dong, W., Socher, R., Li, L.-J., Li, K., & Fei-Fei, L. (2009). “[ImageNet: A Large-Scale Hierarchical Image Database⁠(opens in a new window)](http://www.image-net.org/papers/imagenet_cvpr09.pdf).” In CVPR09.
- 2Krizhevsky, A., Sutskever, I., & Hinton, G. E. (2012). “[Imagenet classification with deep convolutional neural networks⁠(opens in a new window)](https://papers.nips.cc/paper/4824-imagenet-classification-with-deep-convolutional-neural-networks.pdf).” In F. Pereira, C. J. C. Burges, L. Bottou, & K. Q. Weinberger (Eds.), Advances in Neural Information Processing Systems 25 (pp. 1097–1105). Curran Associates, Inc.
- 3Moore, G. E. (1965). “[Cramming more components onto integrated circuits⁠(opens in a new window)](https://newsroom.intel.com/wp-content/uploads/sites/11/2018/05/moores-law-electronics.pdf).” Electronics 38(8).
- 4Amodei, D. & Hernandez, D. (2018). “[AI and Compute⁠](https://openai.com/index/ai-and-compute/).”
- 5Szegedy, C., Liu, W., Jia, Y., Sermanet, P., Reed, S., Anguelov, D., Erhan, D., Vanhoucke, V., & Rabinovich, A. (2014). “[Going deeper with convolutions⁠(opens in a new window)](https://arxiv.org/abs/1409.4842).”
- 6Simonyan, K. & Zisserman, A. (2014). “[Very deep convolutional networks for large-scale image recognition⁠(opens in a new window)](https://arxiv.org/abs/1409.1556).”
- 7He, K., Zhang, X., Ren, S., & Sun, J. (2015). “[Deep residual learning for image recognition⁠(opens in a new window)](https://arxiv.org/abs/1512.03385) .”
- 8Iandola, F. N., Han, S., Moskewicz, M. W., Ashraf, K., Dally, W. J., & Keutzer, K. (2016). “[Squeezenet: Alexnet-level accuracy with 50x fewer parameters and <0.5mb model size⁠(opens in a new window)](https://arxiv.org/abs/1602.07360).”
- 9Zagoruyko, S. & Komodakis, N. (2016). “[Wide residual networks⁠(opens in a new window)](https://arxiv.org/abs/1605.07146).”
- Xie, S., Girshick, R., Dollár, P., Tu, Z., & He, K. (2016). “

[Aggregated residual transforma- tions for deep neural networks⁠(opens in a new window)](https://arxiv.org/abs/1611.05431).”

- 11Huang,G.,Liu,Z.,vanderMaaten,L.,&Weinberger,K.Q.(2016). “[Densely connected convolutional networks⁠(opens in a new window)](https://arxiv.org/abs/1608.06993).”
- 12Howard, A. G., Zhu, M., Chen, B., Kalenichenko, D., Wang, W., Weyand, T., An- dreetto, M., & Adam, H. (2017). “[Mobilenets: Efficient convolutional neural networks for mobile vision applications⁠(opens in a new window)](https://arxiv.org/pdf/1704.04861.pdf).”
- 13Zhang, X., Zhou, X., Lin, M., & Sun, J. (2017). “[Shufflenet: An extremely efficient convolutional neural network for mobile devices⁠(opens in a new window)](https://arxiv.org/abs/1707.01083).”
- 14Sandler, M., Howard, A., Zhu, M., Zhmoginov, A., & Chen, L.-C. (2018). “[Mobilenetv2: Inverted residuals and linear bottlenecks⁠(opens in a new window)](https://arxiv.org/abs/1801.04381).”
- 15Ma, N., Zhang, X., Zheng, H.-T., & Sun, J. (2018). “[Practical guidelines for efficient cnn architecture design⁠(opens in a new window)](https://arxiv.org/abs/1807.11164).”
- 16Tan, M. & Le, Q. V. (2019). “[Efficientnet: Rethinking model scaling for convolutional neural networks⁠(opens in a new window)](https://arxiv.org/abs/1905.11946).”
- 17Sawyer, Eric (2011). “[High Throughput Sequencing and Cost Trends⁠(opens in a new window)](https://www.nature.com/scitable/blog/bio2.0/high_throughput_sequencing_and_cost/).”
- 18Roberts, David (2019). “[Getting to 100% renewables requires cheap energy storage. But how cheap?⁠(opens in a new window)](https://www.vox.com/energy-and-environment/2019/8/9/20767886/renewable-energy-storage-cost-electricity).”
- 19Paszke, A., Gross, S., Chintala, S., Chanan, G., Yang, E., DeVito, Z., Lin, Z., Desmai- son, A., Antiga, L., & Lerer, A. (2017). “[Automatic differentiation in PyTorch. In NIPS Autodiff Workshop⁠(opens in a new window)](https://openreview.net/pdf?id=BJJsrmfCZ).”
- 20Huang, J. (2017). “[Shufflenet in pytorch⁠(opens in a new window)](https://github.com/jaxony/shufflenet).”
- 21Xiao, H. (2017). “[Pytorch mobilenet implementation of “mobilenets: Efficient convolutional neural networks for mobile vision applications”⁠(opens in a new window)](https://github.com/marvis/pytorch-mobilenet.).”
- 22Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., & Polosukhin, I. (2017). “[Attention is all you need. CoRR, abs/1706.03762⁠(opens in a new window)](https://arxiv.org/abs/1706.03762).”
- 23Sutskever, I., Vinyals, O., & Le, Q. V. (2014). “[Sequence to sequence learning with neural networks. CoRR, abs/1409.3215⁠(opens in a new window)](https://arxiv.org/abs/1409.3215).”
- 24Silver, D., Hubert, T., Schrittwieser, J., Antonoglou, I., Lai, M., Guez, A., Lanctot, M., Sifre, L., Kumaran, D., Graepel, T., Lillicrap, T., Simonyan, K., & Hassabis, D. (2018). “[A general reinforcement learning algorithm that masters chess, shogi, and go through self-play. Science, 362(6419), 1140–1144⁠(opens in a new window)](https://arxiv.org/abs/1712.01815).”
- 25Silver, D., Schrittwieser, J., Simonyan, K., Antonoglou, I., Huang, A., Guez, A., Hubert, T., Baker, L., Lai, M., Bolton, A., Chen, Y., Lillicrap, T., Hui, F., Sifre, L., van den Driessche, G., Graepel, T., & Hassabis, D. (2017). “[Mastering the game of go without human knowledge. Nature, 550, 354–⁠(opens in a new window)](https://www.nature.com/articles/nature24270).”
- OpenAI et. al, :, Berner, C., Brockman, G., Chan, B., Cheung, V., De ̨biak, P., Dennison, C., Farhi, D., Fischer, Q., Hashme, S., Hesse, C., Józefowicz, R., Gray, S., Olsson, C., Pachocki, J., Petrov, M., de Oliveira Pinto, H. P., Raiman, J., Salimans, T., Schlatter, J., Schneider, J., Sidor, S., Sutskever, I., Tang, J., Wolski, F., & Zhang, S. (2019). “

[Dota 2 with Large Scale Deep Reinforcement Learning⁠(opens in a new window)](https://cdn.openai.com/dota-2.pdf).”

- Cody A. Coleman, Deepak Narayanan, Daniel Kang, Tian Zhao, Jian Zhang, Luigi Nardi, Peter Bailis, Kunle Olukotun, Chris Ré, and Matei Zaharia (2017). “

[High Throughput Sequencing and Cost Trends⁠(opens in a new window)](https://dawn.cs.stanford.edu/benchmark/papers/nips17-dawnbench.pdf).”

- 28Paszke, A., Gross, S., Chintala, S., Chanan, G., Yang, E., DeVito, Z., Lin, Z., Desmai- son, A., Antiga, L., & Lerer, A. (2017). “[DAWNBench: An End-to-End Deep Learning Benchmark and Competition. NIPS ML SYSTEMS WORKSHOP, 2017⁠(opens in a new window)](https://openreview.net/pdf?id=BJJsrmfCZ).”
- 29Raymond Perrault, Yoav Shoham, E. B. J. C. J. E. B. G. T. L. J. M. S. M. & Niebles, J. C. (2019). “[The AI Index 2019 Annual Report”. Technical report, AI Index Steering Committee, Human-Centered AI Institute, Stanford University, Stanford, CA⁠(opens in a new window)](https://hai.stanford.edu/sites/default/files/ai_index_2019_report.pdf).”
- 30McCandlish, S., Kaplan, J., Amodei, D., & Team, O. D. (2018). “[An empirical model of large-batch training”⁠(opens in a new window)](https://arxiv.org/pdf/1812.06162.pdf).”
- 31van den Oord, A., Li, Y., Babuschkin, I., Simonyan, K., Vinyals, O., Kavukcuoglu, K., van den Driessche, G., Lockhart, E., Cobo, L. C., Stimberg, F., Casagrande, N., Grewe, D., Noury, S., Dieleman, S., Elsen, E., Kalchbrenner, N., Zen, H., Graves, A., King, H., Walters, T., Belov, D., & Hassabis, D. (2017). “[Parallel wavenet: Fast high-fidelity speech synthesis.⁠(opens in a new window)](https://arxiv.org/abs/1711.10433).”
- 32Jack Clark (2019). “[Written Testimony of Jack Clark, Policy Director at OpenAI. Hearing on “Artificial Intelligence: Societal and Ethical Implications” before the House Committee on Science, Space, & Technology⁠(opens in a new window)](https://science.house.gov/imo/media/doc/Clark%20Testimony.pdf).”

## Authors

Danny Hernandez, Tom Brown

## Acknowledgments

We’d like to thank the following people helpful conversations and/or feedback on this post: Dario Amodei, Jack Clark, Alec Radford, Paul Christiano, Sam McCandlish, Ilya Sutskever, Jacob Steinhardt, Jared Kaplan, Amanda Askell, John Schulman, Jacob Hilton, Asya Bergal, Katja Grace, Ryan Carey, Nicholas Joseph, Geoffrey Irving, Jeff Clune, and Ashley Pilipiszyn.

Thanks to Justin Jay Wang for design.

Thanks to Niki Parmar for providing the relevant points from the original [transformer⁠(opens in a new window)](https://arxiv.org/abs/1706.03762) learning curves.

Also thanks to Mingxing Tan for providing the relevant points from [EfficientNet⁠(opens in a new window)](https://arxiv.org/abs/1905.11946) learning curves and running an experiment with reduced warmup.

## Related articles

View all

Techniques for training large neural networks

PublicationJun 9, 2022

Introducing Triton: Open-source GPU programming for neural networks

ReleaseJul 28, 2021

Scaling Kubernetes to 7,500 nodes

ConclusionJan 25, 2021
