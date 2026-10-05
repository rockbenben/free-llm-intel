---
vendor: modular_cloud
title: Modular 26.3：Mojo 1.0 Beta、MAX 视频生成等
original_title: "Modular: Modular 26.3: Mojo 1.0 Beta, MAX Video Gen, and more"
url: https://www.modular.com/blog/modular-26-3-mojo-1-0-beta-max-video-gen-and-more
date: 2026-05-07
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Modular 26.3：Mojo 1.0 Beta、MAX 视频生成等

惊喜：Mojo 1.0 正式进入 beta！Modular 的 26.3 版本包含新特性与新模态，但头条是 Mojo 1.0 正式进入 beta，并有在未来几个月定稿 Mojo 1.0 的清晰计划。详情见下文，同时还有 26.3 版本的其他重要发布，包括 MAX 中基于 Wan 2.2 的视频生成以及 MAX 框架更新。

### Mojo 1.0：现已进入 beta！🔥🔥🔥

Mojo 是我们在 Modular 所做一切的基础——从推进 kernel 性能的业界前沿，到运行在新的、新颖的加速器硬件上。12 月，我们为 Mojo 语言[提供了通往 1.0 的路线图](https://www.modular.com/blog/the-path-to-mojo-1-0)，今天我们很高兴宣布 Mojo 1.0 的 beta 版今日可用！

Mojo 1.0 将于今年晚些时候定稿，同时开放编译器并提供语言稳定性。这标志着这门语言新纪元的开始。你现在可以基于已知版本的 Mojo 构建项目，它们明天不会突然崩掉。这个 beta 提供了我们认为"功能完备"的 Mojo 1.0 语言，但离最终发布仍有许多要打磨的地方。

1.0 beta 带来我们长期推进的若干特性，包括：

- 采用全新捕获语法的安全闭包。
- 对 trait 的条件式遵循（conditional conformance）。
- variadics 的重大改进。

我们还引入 LayoutTensor 的继任者 TileTensor，让编写高性能 kernel 更加轻松。TileTensor 把内存布局变成张量自身的编译期属性，因此 GPU kernel 所需的 swizzle、stride 和索引都由类型系统检查，而非手工维护。我们已为这个漂亮的新类型[开启了专门的博客系列](https://www.modular.com/blog/tiletensor-part-1-safer-more-efficient-gpu-kernels)，它也支撑了我们在[持续更新的系列文章](https://www.modular.com/blog/structured-mojo-kernels-part-1-peak-performance-half-the-code)中谈到的结构化 kernel 新范式。

但这还不是全部！我们觉得，既然 Mojo 已走到这么远，是时候给它一个像样的新家。

### 介绍 mojolang.org

没错，Mojo 现在有了自己的网站：[mojolang.org](https://mojolang.org/)！

与 Mojo 1.0 beta 发布一同上线的这个网站，标志着一个重要里程碑；Mojo 几乎已准备好被广泛采用。[Mojolang.org](http://mojolang.org/) 是向世界敞开 Mojo、完成 1.0 正式发布的重要一步，我们目标在秋季完成。

无论你是 Mojo 新人还是资深贡献者，现在去哪里获取所需的一切，比以往任何时候都更清晰。

随着所有 Mojo 文档搬入独立站点，[docs.modular.com](http://docs.modular.com/) 现在专注于用 MAX 构建和服务模型所需的内容。只有在扩展或编写自定义 kernel 时你才需要在 MAX 中使用 Mojo，这也是为什么 MAX AI kernel 库仍留在 docs.modular.com。想全面了解伴随 beta 的所有 Mojo 更新，请看 [mojolang.org changelog](https://mojolang.org/releases/v1.0.0b1/)。

### MAX 中的视频生成

有大更新的不只是 Mojo。我们正在统一的 Modular 平台上添加新模态：视频生成。

我们从文本起步，扩展到音频，加入图像生成/编辑，而如今加上视频生成——如果你的应用需要从静态图像走到鲜活场景，你不再需要跳出 Modular Platform 去做这件事。

今天的发布带来对 [Wan 2.2](https://wan.video/) 的支持——领先的开放视频生成模型之一，更多模型很快到来，同时附带多项改进。MAX 的视频生成现已可用，并即将登陆 [Modular Cloud](https://console.modular.com/signup?utm_source=26_3&utm_source=blog)。如果你正在把工作流中加入视频能力、想探讨这对你基础设施的意义，联系我们。

## MAX 框架

### 统一的、分布式感知的张量

真实世界的模型如今常态化地横跨多块 GPU。在 26.3 中，我们扩展了 `max.experimental` 的多 GPU 支持：一个分布式感知的 `Tensor` 类型、多设备编译，以及张量并行代码所需的集合通信 ops。

PyTorch 的 `DTensor` 确立了把放置元数据挂在张量上是推理分布式问题的正确抽象。JAX 的 `jax.Array` 展示了单一张量类型加上具名 mesh 轴可以多么易读。MAX 借鉴两者，并添加了它们都没有的东西：同一个 `.to(...)` 调用既接受 `NamedMapping`（JAX 风格"这个张量轴映射到那个 mesh 轴"），也接受 `PlacementMapping`（DTensor 风格的 `Replicated` / `Sharded` / `Partial`）。你按问题选合适的写法；两者会下降到同一表示。

实际效果：`Tensor` 无论驻留在单设备上还是在 mesh 上分片，都是同一类型。分片是元数据，不是另一条代码路径。

### 其他亮点

- MAX 的快速 eager 解释器实现 eager 模式 100% 算子覆盖：此前，MAX 中的图必须先经过完整编译器才能运行，我们用 `max.experimental` 中的 MO graph 解释器改变这一点——一条快 10-20 倍的 eager 执行路径。在 26.3，我们完成了剩余的算子覆盖：gather/scatter（embedding 查表、稀疏更新）、卷积与池化（`ConvOp`、`MaxPoolOp`、`AvgPoolOp`）、arg/search 类算子（`ArgMaxOp`、`ArgMinOp`、`TopKOp`）、数据重排（`SplitOp`、`TileOp`），以及此前缺失的其余所有处理器。我们会在 26.4 继续改进。
- NVFP4 grouped matmul kernels 已在所有测试形状上调优；`layer_norm`、`topk`、`argsort`、`concat` 和 `pad_constant` 的 GPU kernel 已完成调优；[《Programming Massively Parallel Processors》](https://www.amazon.com/dp/0443439001?ref=cm_sw_r_ffobk_cp_ud_dp_GRH8M6AK2GESW4JDCE89&social_share=cm_sw_r_ffobk_cp_ud_dp_GRH8M6AK2GESW4JDCE89&bestFormat=true)（PMPP）[教材例题](https://github.com/modular/modular/tree/main/max/kernels/examples/pmpp)的 Mojo 实现现已随包发布。
- `max benchmark` 新增扫描模式（并发 x 请求速率，JSON 输出），KV connector 标志迁移至 `-kv-connector-config`，`-model-override` 支持混合量化的扩散流水线，`Float8Config` 更名为 `QuantConfig`（FP8 + NVFP4 + MXFP4）。

*完整变更列表见 *[*MAX*](https://docs.modular.com/max/changelog/#v263-2026-05-07)* 和 *[*Mojo*](https://mojolang.org/releases/v1.0.0b1/)* changelog*

## 开始使用 26.3

Modular 26.3 现已可用：发布 Mojo 1.0 Beta、为 MAX 带来高性能视频生成、改善 MAX 的开发者体验，并简化 Mojo 的闭包与内存 tiling 语法。安装或升级，几分钟内上手：

shell

```
uv pip install --upgrade modular
```

想更深入地了解本版本包含的一切，请查看：

- [MAX changelog](https://docs.modular.com/max/changelog/#v263-2026-05-07)
- [Mojo changelog](https://mojolang.org/releases/v1.0.0b1/)（现在在 mojolang.org 上！）

如果你在用 Modular 构建，欢迎加入我们：

- [Modular 论坛](https://forum.modular.com/)
- [GitHub](https://github.com/modularml/modular)

我们很期待听到你用 26.3 和 Mojo beta 构建了什么。

分享你对 Mojo 1.0 beta 的反馈：

- 在 GitHub Issues 中用 [the "Mojo 1.0" label](https://github.com/modular/modular/issues?q=state%3Aopen%20label%3A%22Mojo%201.0%22) 提交功能请求和 bug 报告。
- 在社区论坛的 [Mojo 1.0 Beta 子分类](https://forum.modular.com/c/mojo/mojo-1-0-beta/32) 中发起 Mojo 1.0 相关讨论。
