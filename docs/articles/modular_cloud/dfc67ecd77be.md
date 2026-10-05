---
vendor: modular_cloud
title: Paged Attention 与 Prefix Caching 现已登陆 MAX Serve
original_title: "Modular: Paged Attention & Prefix Caching Now Available in MAX Serve"
url: https://www.modular.com/blog/paged-attention-prefix-caching-now-available-in-max-serve
date: 2025-02-06
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Paged Attention 与 Prefix Caching 现已登陆 MAX Serve

我们很高兴宣布 [MAX Serve](https://docs.modular.com/max/serve) 现已支持 **Paged Attention** 和 **Prefix Caching**，带来业界领先的 LLM 推理优化。这两个特性可在 [MAX nightly](https://github.com/modular/max/commit/b1b540c6d699cbecab0b50b47c17bf40cdbdd8fd) 和 [MAX Serve nightly Docker 镜像](https://hub.docker.com/layers/modular/max-openai-api/25.1.0.dev2025020205/images/sha256-ca59f45568b326c5aa175b8d94b8e77aa81f0604c3d07e2c6b21245fa25176a4)中使用。

## **立即试用**

开始前请确保已安装 `magic` CLI

Bash

curl -ssL https://magic.modular.com/ | bash

或者通过以下命令更新

Bash

magic self-update

现在用一条命令安装 `max-pipelines` 包

Bash

magic global install max-pipelines

启用优化进行服务

Bash

max-pipelines serve \
    --huggingface-repo-id modularai/llama-3.1 \
    --cache-strategy paged \ 
    --enable-prefix-caching

`‍
`查看可用选项

Bash

max-pipelines serve --help

这些特性适用于[Modular 官方支持的模型](https://github.com/modular/max/tree/main/pipelines/python)，并充分利用了高度优化的 [MAX Graph API](https://docs.modular.com/max/api/python/graph/)。

## **Paged Attention 和 Prefix Caching 为什么重要？**

[Multi-Head Attention](https://arxiv.org/pdf/1706.03762)（MHA）是现代 LLM 的核心构件，但在推理时可能计算量巨大。MHA 的计算复杂度随序列长度呈平方级增长 **O(n²)**、随批大小呈线性增长，对长序列或大批次尤其吃力。[KV Cache](https://huggingface.co/blog/not-lain/kv-caching) 通过存储先前计算的 **Key** 和 **Value** 投影来优化这一点，避免自回归生成期间的重复计算。然而，传统 KV caching 在长序列下面临内存管理难题。

PagedAttention 和 Prefix Caching 正是为了解决这些挑战。

### **Paged Attention：内存高效的 KV Cache 管理**

由 vLLM 提出的 paged attention，以以下方式革新了 LLM 中注意力计算的处理：

- **基于块的内存管理**：把 KV cache 组织为固定大小的内存块（页）；每个块通常包含 16 或 32 个 token；实现高效的内存分配与释放
- **关键收益**：**连续内存保证**：无内存碎片**动态序列管理**：高效处理变长序列**内存池化**：在多个请求间共享内存**GPU 显存节省**：内存占用最多降低 40%

深入了解 paged attention：[vLLM: Easy, Fast, and Cheap LLM Serving with PagedAttention](https://arxiv.org/pdf/2309.06180)**‍**

### **Prefix Caching：优化相似提示**

**‍**由 SGLang 提出的 prefix caching，为结构化 LLM 程序提供了强大的优化：

- **核心概念**：识别并缓存文本提示中的公共前缀模式；利用程序结构实现最优缓存复用；在前缀树上实现智能缓存管理
- **关键优势**：**智能前缀检测**：自动识别可复用的提示片段**程序感知缓存**：针对 LLM 应用中的常见模式优化**吞吐量提升**：结构化工作流最高可加速 3 倍**资源优化**：通过结构化共享实现高效内存利用

深入了解 prefix caching：[SGLang: Efficient Execution of Structured Language Model Programs](https://arxiv.org/pdf/2312.07104)

## [‍](https://arxiv.org/pdf/2312.07104)接下来？

这些改进最多可将 GPU 内存优化 40%，吞吐量提升至 3 倍。以下是一些帮你上手的资源：

- ‍[**MAX 入门**](https://docs.modular.com/max/get-started)
- 探索 [**MAX Serve**](https://docs.modular.com/max/serve) 和 [**MAX Container**](https://docs.modular.com/max/container/)
- 查看教程：[如何用 MAX Serve 在 GPU 上部署 Llama 3](https://docs.modular.com/max/tutorials/max-serve-local-to-cloud)
- 查看[**相关概念页**](https://docs.modular.com/max/serve/prefix-caching)
- 加入我们的 [**Discord**](https://discord.gg/modular) 和 [**Modular 论坛**](https://forum.modular.com/)

我们很期待看到你会用 MAX 构建什么！在社交媒体上用 **#ModularAI** 分享你的项目和体验。
