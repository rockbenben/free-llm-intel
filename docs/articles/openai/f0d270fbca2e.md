---
vendor: openai
title: 块稀疏 GPU 核函数
original_title: Block-sparse GPU kernels
url: https://openai.com/index/block-sparse-gpu-kernels
date: 2022-09-21
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# 块稀疏 GPU 核函数

我们发布一批高度优化的 GPU 核函数（kernels），面向一类鲜有研究的神经网络架构：权重块稀疏的网络。根据所选稀疏度，这些核函数可以比 cuBLAS 或 cuSPARSE 快几个数量级。我们已用它们在文本情感分析和文本/图像生成建模上取得了当时最先进（state-of-the-art）的结果。

深度学习领域模型架构与算法的发展，在很大程度上受制于基础运算是否有高效的 GPU 实现。其中一个问题一直是稀疏线性运算缺乏高效的 GPU 实现——我们现在发布这一实现，并附上用若干稀疏模式取得的初步结果。这些初步结果有前景但并非定论，我们邀请社区与我们一起，把这些核函数所解锁的架构推向极限。

与稠密权重矩阵不同，稀疏权重矩阵中有大量元素恰好为零。稀疏权重矩阵作为模型构件很有吸引力，因为与稀疏块做矩阵乘法和卷积的计算成本只与非零块的数量成正比。稀疏性使得训练**更宽更深**的神经网络成为可能——在给定参数预算和算力预算下，否则不可能达到这样的规模，例如拥有[数万个隐藏单元](https://openai.com/index/block-sparse-gpu-kernels/#small-world)的 LSTM。（当今训练过的最大 LSTM 也只有数千个隐藏单元。）

## 核函数

这些核函数支持在全连接层和卷积层中高效使用块稀疏权重（见上图）。对卷积层，核函数允许在输入和输出特征维度上稀疏；空间维度上的连接性不受影响。稀疏性以块为单位定义（见上图右侧），并针对 8x8（如本例）、16x16 或 32x32 的块尺寸做了优化。在块级别上，稀疏模式完全可配置。由于核函数跳过值为零的块的计算，计算成本只与非零权重的数量成正比，而与输入/输出特征数量无关。参数存储成本同样只与非零权重数量成正比。

*与 cuBLAS 相比，在不同稀疏度下的加速倍数；测试采用宽状态（12,288 个隐藏单元）、32x32 块尺寸、32 的 mini-batch 尺寸，硬件为 NVIDIA Titan X Pascal GPU、CUDA 8。在所测稀疏度下，与 cuSPARSE 相比加速更为显著。*

## 使用核函数

下面展示在 Tensorflow 中执行稀疏矩阵乘法的一些示例代码。

#### Python

```
1from blocksparse.matmul import BlocksparseMatMul2import tensorflow as tf3import numpy as np45hidden_size = 40966block_size = 327minibatch_size = 6489# Create a (random) sparsity pattern10sparsity = np.random.randint(2, size=(hidden_size//block_size,hidden_size//block_size))1112# Initialize the sparse matrix multiplication object13bsmm = BlocksparseMatMul(sparsity, block_size=block_size)1415# Input to graph16x = tf.placeholder(tf.float32, shape=[None, hidden_size])1718# Initialize block-sparse weights19w = tf.get_variable("w", bsmm.w_shape, dtype=tf.float32)2021# Block-sparse matrix multiplication22y = bsmm(x, w)2324# Run25sess = tf.InteractiveSession()26sess.run(tf.global_variables_initializer())27result = sess.run([y], feed_dict = {x: np.ones((minibatch_size,hidden_size), dtype='float32')})28print(result)
```

## 小世界 LSTM

块稀疏核函数一个特别有趣的用法，是构建小世界神经网络。[小世界图](https://en.wikipedia.org/wiki/Small-world_network)的连通方式使图中任意两个节点之间只需很少几步即可到达——即使图有数十亿节点。我们实现小世界连通性的动机是：尽管稀疏度很高，仍希望信息能快速在网络中传播。大脑[呈现出小世界的连通模式](https://www.ncbi.nlm.nih.gov/pubmed/17079517)，这引出一个问题：同样的性质能否提升 LSTM 的表现？使用小世界稀疏连通，我们高效训练了拥有近两万个隐藏单元的 LSTM——比参数量相当的稠密网络宽 5 倍——并在文本生成建模和半监督情感分类上改善了结果；详见[我们的论文](https://cdn.openai.com/blocksparse/blocksparsepaper.pdf)。

## 情感表示学习

沿用我们在[情感神经元实验](https://openai.com/index/unsupervised-sentiment-neuron/)中的设置，我们训练了参数量大致相当的 LSTM，把稠密权重矩阵模型与块稀疏变体进行对比。稀疏模型在所有情感数据集上都优于稠密模型。我们的稀疏模型把文档级 IMDB 数据集的最先进成绩从 5.91% 错误率（[Miyato 等，2016](https://arxiv.org/abs/1605.07725)）提升到 5.01%。相比我们[此前的结果](https://openai.com/index/unsupervised-sentiment-neuron/)——当时只在较短的句子级数据集上表现最好——这是令人鼓舞的改进。

## 压缩结果

通过使用稀疏且宽的 LSTM，在参数量相同（约 1 亿）的实验中，我们的每字符比特数（bits-per-character）从 1.059 降至 1.048。采用块稀疏线性层的架构也能超越全连接线性层取得的结果。我们对 CIFAR-10 自然图像模型 [PixelCNN++](https://github.com/openai/pixel-cnn) 做了简单改造：用稀疏核函数替换常规 2D 卷积核函数，同时加深网络、其余超参数保持不变，使每维比特数从 2.92 降至 2.90，成为该数据集上新的最先进水平。

## 研究方向

这里列出一些未来研究的建议。

- 神经网络中的大部分权重[可以在训练结束后被剪枝](https://arxiv.org/abs/1710.09282)。把剪枝与这些核函数结合，在推理时能获得多少实际墙钟时间的加速？
- 在生物大脑中，网络的稀疏结构[部分是在发育过程中确定的](https://en.wikipedia.org/wiki/Synaptic_pruning)，而不只是连接强度。我们能否在人工神经网络中做类似的事——用梯度不仅学习连接权重，还学习最优的稀疏结构？近期一篇论文提出了学习[块稀疏 RNN](https://arxiv.org/abs/1711.02782) 的方法；我们最近也提出了神经网络 [L0 正则化](https://arxiv.org/abs/1712.01312) 的算法，可用于这一目标。
- 我们训练了[拥有数万个隐藏单元的 LSTM](https://openai.com/index/block-sparse-gpu-kernels/#small-world-lstms)，得到了更好的文本模型。更一般地说，稀疏层让我们可以训练拥有巨大权重矩阵的模型，而参数量和计算成本与其较小的稠密版本相同。在哪些应用领域，这会对性能带来最大的差异？

**作者**：Scott Gray、Alec Radford、Durk Kingma
