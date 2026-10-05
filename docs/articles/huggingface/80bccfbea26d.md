---
vendor: huggingface
title: 异步机器人推理：解耦动作预测与执行
original_title: Asynchronous Robot Inference: Decoupling Action Prediction and Execution
url: https://huggingface.co/blog/async-robot-inference
date: 2023-04-23
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: 1b24a25c91f1
---

# 异步机器人推理：解耦动作预测与执行

**TL;DR** 机器人策略（policy）正变得越来越庞大，并且预测的是一整块未来动作，而不是单个下一步动作。这导致机器人在等待新动作时可执行时却空闲，执行中出现明显延迟、响应不足。异步推理收紧了控制回路，消除了运行时的滞后，通过解耦动作预测与动作执行实现更自适应的控制。本篇博客介绍异步推理的基本原理，以及它如何在真实世界中提升机器人策略的性能。

## 目录

- [入门](https://huggingface.co/blog/async-robot-inference#getting-started)
- [异步推理：深入剖析](https://huggingface.co/blog/async-robot-inference#async-inference-a-deep-dive)
- [1. 为什么顺序推理不够好](https://huggingface.co/blog/async-robot-inference#1-why-sequential-inference-falls-short)
- [2. 异步推理，一句话概括](https://huggingface.co/blog/async-robot-inference#2-asynchronous-inference-in-a-nutshell)
- [3. 系统架构](https://huggingface.co/blog/async-robot-inference#3-system-architecture) [机器人客户端](https://huggingface.co/blog/async-robot-inference#robot-client) [策略服务器](https://huggingface.co/blog/async-robot-inference#policy-server)
- [4. 分析异步推理](https://huggingface.co/blog/async-robot-inference#4-analyzing-async-inference)
- [5. 在你的环境中使用异步推理](https://huggingface.co/blog/async-robot-inference#5-using-async-in-your-setup)
- [总结](https://huggingface.co/blog/async-robot-inference#conclusions)

## 入门

想上手异步推理，请跟随[我们的教程](https://huggingface.co/docs/lerobot/en/async)。

*顺序推理（第一个视频）对比异步推理（第二个视频）*。异步推理允许重新规划、收紧控制回路，带来：(1) 失败后的恢复尝试，(2) 任务完成时间约 2 倍加速。顺序推理在抓取物体失败后仍会继续演完当前的动作块，而异步推理可以重新规划并执行新的动作块。两种设置用的是同一个策略！

## 异步推理：深入剖析

异步推理把动作执行与动作预测解耦。考虑到当前流行的模型——[[ACT](https://huggingface.co/papers/2304.13705)]、[[OpenVLA](https://huggingface.co/papers/2406.09246)]、[[PI0](https://huggingface.co/papers/2410.24164)]、[[SmolVLA](https://huggingface.co/papers/2506.01844)]——都倾向于输出动作块 `a_{t:t+H}` 而非给定观测 `o_t` 时的单个动作 `a_t`，这一点尤其重要。你可以用 [LeRobot](https://huggingface.co/lerobot) 跑一遍这些模型亲自验证。

按顺序消费动作块会带来：(1) 运行时延迟，影响任务执行时间；(2) 因长时间开环执行而响应不足。异步推理通过**解耦动作预测与动作执行**同时缓解这两个限制。我们在 SmolVLA 中引入了异步推理，发现任务完成时间约加速 2 倍，任务成功率相当。

具体而言，我们设计了一个双组件系统，策略推理与动作执行在两个不同进程（也可能在网络连接的两台不同机器）中进行：

- **`PolicyServer`**：部署在加速硬件上，能用比真实机器人上分配到的更多算力来跑推理。
- **`RobotClient`**：把收到的动作入队并执行，同时下一块动作正在计算。

`PolicyServer` 与 `RobotClient` 之间的通信基于 **gRPC**，性能约比同类 REST API 快 5×。最终效果是一台*永远*不为推理等待的机器人。

![异步推理示意图](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/async-inference/async_scheme.png)

*异步推理*，注意：(1) 客户端发送第一个观测用于推理，很快收到第一个动作块；(2) 客户端在当前块尚未用完时就发送下一个观测进行处理；(3) 客户端收到更新后的动作块，并与此前正在执行的块的剩余部分做聚合。

## 1. 为什么顺序推理不够好

假设策略 π 把当前观测 `o_t` 映射为未来 H 个动作的序列。形式化写：π: O ↦ A，`A_t = (a_t, a_{t+1}, …, a_{t+H}) = π(o_t)`。

传统控制回路因此包含以下步骤：

- 采集 `o_t`。
- 运行 `π(o_t)` 得到 `A_t = π(o_t)`。
- 将 `A_t` 入队，开始执行——从队列弹出动作。
- 若队列为空，等待 `A_{t+H}`；否则重复第 3 步。

第 2 步期间机器人是**空闲**的。延迟随模型规模增长（而模型只会越来越大），并可能迅速超过交互时间（通常为 1/`fps` 左右），下面这段视频（来自我们的 [Discord 社区](https://discord.com/invite/ttk5CV6tUw) 🤗）展示了这一点：

这直接导致：(1) 任务完成时间上的性能下降——机器人必须等下一个动作块算完；(2) 响应能力下降——(2.1) 队列有动作时长时间开环执行，(2.2) 等待下一块时完全空闲。

*(左)*顺序推理*，高亮标出空闲期。（右）*选择动作的耗时*，在本地队列耗尽触发推理时出现尖峰（在 2021 款 MacBook Pro 上用 ACT 模型，推理延迟约 100ms——30fps 下约 3 帧）。*

## 2. 异步推理，一句话概括

我们的系统通过让计算与执行重叠来消除空闲期：

- `RobotClient` 把最新观测流式发送给 `PolicyServer`。
- 服务器执行推理的同时，客户端继续执行**当前队列**中的动作。
- 新动作到达后并入队列，循环继续。

关键思想在于：机器人已经知道接下来几步该做什么，所以可以在服务器计算新动作的同时保持运动。

![异步推理流程图](https://github.com/user-attachments/assets/6f323660-52b4-4537-8bde-f9b70b7f1bc0)

*异步推理*通过解耦这两个过程，让当前动作块的执行与下一块的计算在时间上重叠——两者甚至可以在通过网络连接的不同机器上运行。*

结果是控制回路更紧、机器人从不为推理等待。由此带来任务完成时间约 2 倍加速、成功率相当，并且更紧的回路带来更自适应的控制（见下方视频）。

## 3. 系统架构

| 组件 | 职责 | 技术 |
| --- | --- | --- |
| **RobotClient** | 机载运行，流式发送观测，维护**动作队列**，执行动作 | Python、gRPC |
| **PolicyServer** | 托管策略，执行批量推理，回传动作块 | Python、gRPC，通常在加速硬件（GPU/TPU）上 |

gRPC 基于 HTTP/2 并使用 protocol buffers，开箱即得低延迟二进制消息与双向流，这帮助我们维持更紧的控制回路和低于 100ms 的往返延迟（在我们的本地网络、SmolVLA 托管于 NVIDIA RTX 4090 的环境下实测）。

`RobotClient` 机载运行，通过 gRPC 向 `PolicyServer` 流式发送观测。`PolicyServer` 对收到的观测做推理准备，并把一个动作块发回给 `RobotClient`。

### 机器人客户端

![从客户端视角看](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/async-inference/from_client_perspective.png)

*从客户端视角*，观测按本地队列状态流向服务器；进来的块在与当前动作队列重叠的部分做聚合。

`RobotClient` 维护本地动作队列，遵循一条简单却有效的策略：**当队列长度低于一个可配置阈值时发送新观测**（SmolVLA 论文中记作 \(g\)，代码里是 `chunk_size_threshold`）。这个阈值以最大块长的分数表示，是平衡计算负载与响应速度的触发条件。

![客户端到服务器](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/async-inference/client_to_server.png)

*客户端按本地队列状态向服务器流式发送观测。*

从客户端视角，流程如下展开：

- **队列监控**：客户端持续将自己的动作队列长度与**chunk size threshold** 参数比较。队列低于该阈值，即意味着应发送新的观测去处理。
- **观测流式发送**：阈值条件满足后，客户端采集当前观测并通过 gRPC 流向 `PolicyServer`。关键点是，**观测以流（stream）而非一元（unary）RPC 发送**，因为它们通常超过 4MB 的最大消息尺寸（多路高分辨率相机采集会达到这个量级）。
- **动作块聚合**：当服务器返回新的动作块时，客户端把它与当前队列中的剩余动作在重叠部分合并。这就是**自定义聚合器（aggregator）**发挥作用的地方——对当前块与新进块的重叠区段做不同处理。目前我们支持通过指定自定义函数 `aggregate_fn(chunk1: torch.Tensor, chunk2: torch.Tensor) -> torch.Tensor` 灵活地聚合块，该函数在每个重叠时间步被调用，用户可以自行提供。重叠部分（图中浅蓝色区域）需要小心处理。可以设计不同的聚合策略：**Replace**：直接用新的预测替换重叠动作；**Weighted blend**：用时间权重合并重叠动作（越近的动作权重越高）。

这套系统高度可配置：chunk size threshold 可根据网络延迟、模型推理时间和期望的响应速度调节。阈值越低更新越频繁（计算成本也越高），阈值越高通信开销越低、但可能造成队列饿死。最后，我们通常在一个线程里接收来自 `PolicyServer` 的动作，在另一个线程里执行。这让客户端在一个独立线程里持续监听新块，不阻塞执行，并且在新块完全可用之前始终消费当前块。

### 策略服务器

`PolicyServer` 从 `RobotClient` 收到观测后，会做必要的观测清洗，让收到的观测满足推理输入要求。该过程如下图所示：

![服务器流水线](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/async-inference/server_pipeline.png)

*观测清洗流水线*在服务器上运行，三个主要步骤：(1) 键匹配 (2) 预处理 (3) 推理准备。*

观测准备就绪后，会与上次用于推理的观测进行比较。这避免陷入这样的循环：非常相似的观测被反复处理，触发不必要的推理、执行相似动作（进而又产生非常相似的观测）。我们用关节空间相似度来比较观测，这是一种近似且快速的度量机器人变化的方式。显然，这个指标不能适应环境的动态变化（物体位置改变、受到扰动等），但我们发现它在多数情况下是很好的折中，能有效避免不必要的推理和状态塌缩。重要的是，`RobotClient` 保留对某个观测是否必须处理的控制权，以避免死锁。客户端发送且标记 `must_go=True` 的观测无论相似度如何都会被处理。

![策略工作流](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/async-inference/policy_workflow.png)

*策略工作流*：进来的观测与上次用于推理的观测比较，只有差异足够大或被标记 must_go 时才处理。*

最后，为确保 `PolicyServer` 始终处理最新可用的观测，在前一个观测成功处理完成之前，我们会阻塞新进来的观测。为此我们利用 `PolicyServer` 上的队列，确保进来的观测在服务器准备好处理之前不入队（见下图）。

![客户端 ping 服务器](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/async-inference/client_pings_server.png)

*客户端每 1/fps 秒 ping 一次服务器*，但观测在前一个成功处理之前不会入队等待处理。*

## 4. 分析异步推理

实际应用中，异步推理有两个关键时间尺度：

- **环境步长** `environment_dt = 1/fps`：表示机器人执行一个动作有多快。
- **推理延迟** `inference_time`：前向传播 + 网络往返。通常可以认为网络往返相对策略推理时间可忽略，但并非每个环境都如此。

重要的是，比值 `c = environment_dt / inference_time` 会带来不同行为：

- `c ≪ 1`：环境演化快于推理。此时队列很快见底，我们退化回顺序控制。
- `c ≥ 1`：服务器跟得上。队列始终（几乎）是满的。

关键点是 `c` 影响任意时刻队列中可用的动作数量。要避免上述的顺序控制退化，可以：

- **给策略服务器更多算力**：把服务器部署在 GPU 上，通过分配更多计算资源来降低 `inference_time`。
- **更高频地发送观测给服务器**：当队列长度 `k` 低于其最大尺寸的某个**分数** `g = k/H` 时就发送新观测。`g=0` 等价于顺序推理（队列空，等待）；`g=1` 每个时间步都发观测（最大算力、最小延迟）。

实验（见下方图表）显示，当发送的观测不被过滤（全部 must-go）时，`g≈0.7` 是一个不错的折中。我们建议先设 `g=0.5`，并按[我们的文档](https://huggingface.co/docs/lerobot/en/async)调参以满足你的具体需求。

![队列](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/async-inference/queues.png)

*任意时刻队列中可用的动作数量*随 g 的变化。g 值越大更新越频繁、计算成本越高；g 接近 0 则重现顺序推理（队列空，等待）。实验中我们发现 g~0.7 是较好的折中。*

## 5. 在你的环境中使用异步推理

异步推理简单但有效，是提升机器人策略性能的好办法。在我们用 SmolVLA 的实验中，异步推理带来任务完成时间约 2 倍加速、成功率相当，更紧的回路也让控制更自适应。

要用异步推理运行你的策略，只需跟随我们的[教程](https://huggingface.co/docs/lerobot/en/async)，换成你自己的参数（如策略路径或 chunk size threshold）。异步推理原生支持输出动作块的策略！

## 总结

我们介绍了异步推理——一种简单但有效的机器人策略性能提升手段。在我们用 SmolVLA 的实验中，异步推理带来任务完成时间约 2 倍加速、成功率相当，更紧的回路也让控制更自适应。

我们很高兴把这项工作分享给社区，期待看到它如何被用于提升机器人策略的表现。欢迎向 [`huggingface/lerobot`](https://huggingface.co/lerobot) 提交 PR 改进和扩展异步推理框架，也欢迎在我们的 [Discord 社区](https://discord.com/invite/ttk5CV6tUw)继续讨论 🤗。
