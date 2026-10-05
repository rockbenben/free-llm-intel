---
vendor: huggingface
title: 将 Hub 从 Git LFS 迁移到 Xet
original_title: Migrating the Hub from Git LFS to Xet
url: https://huggingface.co/blog/migrating-the-hub-to-xet
date: 2025-07-15
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: ae8c19eeb2d5
---

# 将 Hub 从 Git LFS 迁移到 Xet

Jared Sulzdorf

jsulz

xet-team

Joseph Godlewski

jgodlewski

xet-team

Sam Horradarn

sirahd

xet-team

今年一月，Hugging Face 的 [Xet 团队](https://huggingface.co/xet-team)上线了新的存储后端，很快就把 [Hub 上约 6% 的下载流量切到了这套基础设施](https://huggingface.co/blog/xet-on-the-hub)上。这是个重要里程碑，但只是开始。6 个月内，50 万个仓库、共 20 PB 数据加入了迁移 Xet 的行列——随着 Git LFS 不再够用，Hub 正在转向一个能与 AI 建设者负载共同扩展的存储系统。

今天，Hub 上已有超过 100 万人在使用 Xet。五月，Xet 成为[新用户和新组织的默认选项](https://huggingface.co/changelog/xet-default-for-new-users)。GitHub issue、论坛帖子和 Discord 消息加起来只有几十条——这也许是同等规模中最安静的一次迁移。

怎么做到的？一方面，团队有备而来：多年打磨的内容寻址存储（CAS）和作为系统基石的 [Rust 客户端](https://github.com/huggingface/xet-core)，是他们撑起了这一切。没有这些，Git LFS 可能仍是 Hub 的"未来"。但这次迁移背后真正无名英雄是：

- 一个内部称为 Git LFS Bridge 的关键基础设施
- 全天候运行的后台内容迁移

有了这两个组件，我们可以在几天内激进地迁移 PB 级数据，而无需担心对 Hub 和社区的影响。它们也给了我们底气，在未来几周和几个月里迈得更快（直接[跳到最后](https://huggingface.co/blog/migrating-the-hub-to-xet#xet-for-everyone) 👇 看接下来的计划）。

## 桥接与向后兼容

早在规划 Xet 迁移之初，我们做了几个关键设计决策：

- 不搞 Git LFS 到 Xet 的"硬切换"
- 启用了 Xet 的仓库应该可以同时包含 Xet 文件和 LFS 文件
- 仓库从 LFS 迁移到 Xet 不需要"锁"：也就是说，可以在后台运行，不干扰任何上传下载

这些看似朴素的决策，源于我们对社区的承诺，影响却很深远。最重要的一条是：我们不认为用户和团队必须立刻改变工作流、或为了对接启用 Xet 的仓库去下载新客户端。

如果你有支持 Xet 的客户端（例如 `hf-xet`，即 `huggingface_hub` 的 Xet 集成），上传下载会走完整的 Xet 技术栈。上传时，客户端[用内容定义分块（content defined chunking）把文件切成块](https://huggingface.co/blog/from-files-to-chunks)；下载时，客户端请求文件的重建信息。上传的[块被送到 CAS 并存入 S3](https://huggingface.co/blog/rearchitecting-uploads-and-downloads)。下载时，[CAS 告诉客户端需要从 S3 请求哪些块区间](https://huggingface.co/blog/rearchitecting-uploads-and-downloads#a-custom-protocol-for-uploads-and-downloads)，客户端在本地重建文件。

对于旧版 `huggingface_hub` 或 [huggingface.js](https://github.com/huggingface/huggingface.js)——它们不支持基于块的文件传输——你依然可以在 Xet 仓库上传和下载，只是字节走的路线不同。当客户端通过 `resolve` 端点请求一个 Xet 存储的文件时，Git LFS Bridge 会构造并返回一个 [presigned URL](https://docs.aws.amazon.com/AmazonS3/latest/userguide/ShareObjectPreSignedURL.html)，模仿 LFS 协议。Bridge 负责从 S3 中的内容重建文件并返回给请求方。

Git LFS Bridge 的高度简化视图——实际上这条路径还包含更多 API 调用和组件，比如挡在 Bridge 前面的 CDN、存文件元数据的 DynamoDB，以及 S3 本身。

想看实际效果，右键点击上方图片在新标签页打开：URL 会从 `https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/migrating-the-hub-to-xet/bridge.png` 重定向到以 `https://cas-bridge.xethub.hf.co/xet-bridge-us/...` 开头的地址。也可以用 `curl -vL` 访问同一个 URL，在终端里观察重定向。

同时，当不支持 Xet 的客户端上传文件时，文件先进入 LFS 存储，再被迁移到 Xet。这个"后台迁移流程"——[文档里只简要提过](https://huggingface.co/docs/hub/en/storage-backends#backward-compatibility-with-lfs)——既支撑着向 Xet 的迁移，也支撑着上传的向后兼容。它已经迁移了十几 PB 的模型和数据集，让 50 万个仓库与 Xet 存储保持同步，而且从未掉链子。

每次有文件需要从 LFS 迁移到 Xet，就会触发一个 webhook，把事件推到分布式队列里，由编排器（orchestrator）处理。编排器会：

- 如果事件需要，先在仓库上启用 Xet
- 为仓库里每个 LFS 文件获取其全部 LFS 版本列表
- 按大小或文件数把文件打包成任务：先满足哪个算哪个——1000 个文件或 500MB
- 把这些任务放到另一个队列，交给迁移 worker pod 处理

迁移 worker 领取任务后，每个 pod：

- 下载批次中列出的 LFS 文件
- 用 [xet-core](https://github.com/huggingface/xet-core) 把这些 LFS 文件上传到 Xet 的内容寻址存储

由 webhook 事件触发的迁移流程；为简洁起见，从编排器开始画。

## 扩展迁移规模

四月，我们联系到 [bartowski](https://huggingface.co/bartowski)，问他们愿不愿意试用 Xet，借此测试这套系统的极限。bartowski 名下近 500 TB、2,000 个仓库，这次迁移暴露了几个薄弱环节：

- 用于全局去重的临时[分片（shard）文件](https://huggingface.co/blog/from-chunks-to-blocks#scaling-deduplication-with-aggregation)先写到 `/tmp`，再移动到分片缓存。但在我们的 worker pod 上，`/tmp` 和 [Xet 缓存](https://huggingface.co/docs/huggingface_hub/guides/manage-cache#chunk-based-caching-xet)位于不同的挂载点，移动失败，分片文件从未被清理。最终磁盘被写满，引发一波 **`No space left on device`** 错误。
- 在支撑完 [Llama 4 发布](https://huggingface.co/blog/llama4-release)之后，我们曾为突发下载给 CAS 扩容，但这次迁移 worker 反了过来：几百个 GB 级的并发上传把 CAS 压到了资源上限之外。
- 理论上迁移 worker 的吞吐远不止报告值；对 pod 做 profiling 后发现瓶颈在网络和 [EBS](https://aws.amazon.com/ebs/) I/O。

要治这个三头怪，得每一层都动：给 xet-core 打补丁、给 CAS 扩容、上调 worker 节点规格。幸运的是，[bartowski](https://huggingface.co/bartowski) 愿意陪我们一起折腾，直到每个仓库都迁到 Xet。这些教训随后直接用在 Hub 上最大的存储用户身上，如 [RichardErkhov](https://huggingface.co/RichardErkhov)（1.7PB、25,000 个仓库）和 [mradermacher](https://huggingface.co/mradermacher)（6.1PB、42,000 个仓库 🤯）。

同期，CAS 吞吐在第一次和最近一次大规模迁移之间增长了一个数量级：

- **bartowski 迁移：** CAS 持续承载约 35 Gb/s，其中约 5 Gb/s 来自常规 Hub 流量。
- **mradermacher 和 RichardErkhov 迁移：** CAS 峰值约 300 Gb/s，同时还在服务约 40 Gb/s 的日常负载。

CAS 吞吐量：每个尖峰对应一次重要迁移，而基线吞吐稳步上升，截至 2025 年 7 月已接近 100 Gb/s。

## 零摩擦，更快的传输

开始替换 LFS 时，我们有两个目标：

- 不造成伤害（do no harm）
- 尽快把影响力做到最大

在最初这些约束和目标的指引下设计，我们得以：

- 先把 `hf-xet` 引入并打磨成熟，再把它作为必需依赖并入 `huggingface_hub`
- 在社区仍在用各自现有方式向启用 Xet 的仓库上传下载时，让基础设施把剩下的事接管下来
- 从渐进式迁移 Hub 的过程中学到宝贵经验——从规模问题到客户端在分布式文件系统上的行为

我们不必等所有上传路径都支持 Xet，不必硬切换，也不必逼社区采纳特定工作流，就能立即着手把 Hub 迁移到 Xet，且对用户影响极小。一句话：让团队保持自己的工作流，自然地过渡到 Xet，由基础设施支撑"统一存储系统"这个长期目标。

## 人人都能用 Xet

一二月，我们邀请重度用户入驻，收集反馈并对基础设施做压力测试。为了听取社区意见，我们上线了[Xet 仓库预览等待名单](https://huggingface.co/join/xet)。很快，Xet 就成为 Hub 新用户的默认选项。

现在我们在为 Hub 上最大的发布者（[Meta Llama](https://huggingface.co/meta-llama)、[Google](https://huggingface.co/google)、[OpenAI](https://huggingface.co/openai) 和 [Qwen](https://huggingface.co/Qwen)）提供支持，而社区照常运转、毫无被打扰。

接下来是什么？

从本月开始，我们把 Xet 开放给所有人。留意即将发出的开通邮件；拿到权限后，更新到最新版 `huggingface_hub`（`pip install -U huggingface_hub`），立刻享受更快的传输。这也意味着：

- 你的所有现有仓库都会从 LFS 迁移到 Xet
- 所有新建仓库默认启用 Xet

如果你用浏览器或 Git 在 Hub 上传下载，也没问题。这两者的基于块的支持很快就来。在那之前，继续用你现在的工作流即可，没有任何限制。

下一步：开源 Xet 协议和整套基础设施栈。能随 AI 负载扩展的字节存储与传输方式在 Hub 上，而我们正把它带给每一个人。

有任何问题，欢迎在评论区留言 👇，或在 [**Xet 团队**](https://huggingface.co/xet-team)页面[**发起讨论**](https://huggingface.co/spaces/xet-team/README/discussions/new)。
