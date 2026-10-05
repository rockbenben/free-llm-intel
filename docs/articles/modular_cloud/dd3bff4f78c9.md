---
vendor: modular_cloud
title: Day Zero：MiniMax M3 开放权重登陆 Modular Cloud
original_title: "Modular: Day Zero: MiniMax M3 Open Weights on Modular Cloud"
url: https://www.modular.com/blog/day-zero-minimax-m3-open-weights-on-modular-cloud
date: 2026-06-11
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Day Zero：MiniMax M3 开放权重登陆 Modular Cloud

💡

今天，MiniMax 以开放权重形式发布了 MiniMax M3 模型。Modular 很荣幸成为 Day Zero 首发合作伙伴。

[MiniMax M3](https://www.minimax.io/blog/minimax-m3) 是 [MiniMax](https://www.minimax.io/) 最新的开放权重模型，针对编码、智能体工作以及原生多模态做了优化。让它跻身前沿模型的几点特质：

- **1M token 上下文窗口**（保底 512K），为长时间运行的 agent 任务、大规模编码工作负载和长视频理解而构建。
- **原生多模态。**M3 在文本和图像上同时训练，多模态是其设计使然。
- **MiniMax Sparse Attention (MSA)。**这是让注意力在上下文增长时依然高效的关键。

MiniMax M3 精度基准测试

跨评估数据集的表现。

# 深入 **MiniMax 的稀疏注意力**

M3 背后是一种全新的 MiniMax Sparse Attention（[MSA](https://github.com/MiniMax-AI/MSA/blob/main/docs/MiniMaxSparseAttention.pdf)）操作。MSA 使 1M 上下文的服务成为可能，同时也是 M3 难以运行良好的重要原因。但如果优化到位，MSA 的设计可以把每 token 的注意力计算削减到全注意力前身的约 1/20，带来 prefill 约 9.7 倍、decode 约 15.6 倍的加速，同时在绝大多数工作负载上与全注意力效果持平。

MSA 把每个注意力层拆成两部分：看*哪些* KV，以及*如何*对它们做注意力。前者通过引入一个索引层解决。对每个 query，indexer 给候选 KV block 打分并选出 top-k 个 block。indexer 还维护一个索引键缓存，只有一个共享头（head）和很小的头维度。通过只关注得分最高的 KV cache block，MSA 只需计算 KV cache 中相关 128 个 token 的注意力，而非整个 block。

mojo

```
# One MSA layer, conceptually
s = (Q_idx @ K_idx.T) * idx_scale      # single shared index head, tiny d_idx -- nearly free
S = block_max_pool(s, B=128)           # token scores -> 128-token block scores
S[:, :init_blocks]  = INF             # force-select the attention-sink blocks
S[:, local_window:] = INF - eps       # force-select the recent window
I = topk_per_kv_group(S, k)            # ONE selection, shared by every head in the GQA group
O = softmax_attention(Q, K[I], V[I])   # ordinary GQA over the REAL K/V of the selected blocks
```

模型以*查询主序（query-major）*形式产出选择结果：对每个 query 给出一个 top-k block ID 列表。kernel 的自然写法遵循这个形态——遍历 queries，收集它们选中的 KV block，然后做注意力。按查询主序执行意味着每个 query 独立收集其选中的 block，同一个 KV block 可能被反复从 HBM 取（效率不高）。

mojo

```
# Query-major: the natural schedule
for q_tile in queries:                    # parallel across threadblocks
    for blk in I[q_tile]:                 # this tile's top-k blocks
        K_blk, V_blk = load_block(blk)    # hot blocks re-fetched by EVERY threadblock that picked them
        online_softmax_update(q_tile, K_blk, V_blk)
```

为避免重复加载，MSA 反转了映射：按 query 所选的 KV block 对 queries 分组，也就是以 key-block-major 形式执行——即 MiniMax 所称的"KV outer gather Q"。这样一来，block 只需加载一次，随后为所有这些 query 计算部分注意力、再合并部分结果，从而提升算术强度。

mojo

```
# Once per step: transpose the selection (a sparse-matrix transpose into CSR)
k2q  = invert(I)                  # row = (seq, kv_block); entries = queries that selected it
work = chunk_rows(k2q, q_budget)  # split hot rows for load balance (more below)

# Block-major forward: one threadblock per work item -- each KV byte leaves HBM once
blk, q_list = work[work_id]
K_blk, V_blk = bulk_load(blk)              # ONE contiguous load; resident for the threadblock's lifetime
for q_tile in tiles(q_list, BM):           # stream the selecting queries through it
    Q_t = gather_rows(Q, q_tile)           # gather the queries (scattered rows)
    O_p, lse = attend_one_block(Q_t, K_blk, V_blk)   # single-tile softmax -- next section
    O_partial[q_tile, slot(q_tile, blk)]   = O_p     # per-(query, block) partials,
    LSE_partial[q_tile, slot(q_tile, blk)] = lse     # merged by a separate combine pass
```

这个结构还有个额外好处：简化了 online softmax 计算。记住，在查询主序的注意力中需要执行 online softmax。而在 block 主序格式下，一个线程块对每个 query 组只看*一个* KV block。于是 softmax 可以在单个 tile 上完成，无需在线修正。这与 flash decoding 中的 split-kv reduction 步骤非常相似。

## MiniMax M3 今日上线 Modular Cloud

MiniMax M3 带来了需要全栈优化——从 kernel 到云——才能发挥的新创新。这只有在 Modular 平台上才可能实现。MiniMax M3 现已面向企业客户在 Modular Cloud 上提供。联系我们的 AI 工程师，[今天申请访问](https://console.modular.com/signup?utm_source=M3blog)。
