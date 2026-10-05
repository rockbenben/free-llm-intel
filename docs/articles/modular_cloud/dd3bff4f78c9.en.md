---
vendor: modular_cloud
title: Day Zero: MiniMax M3 Open Weights on Modular Cloud
original_title: Modular: Day Zero: MiniMax M3 Open Weights on Modular Cloud
url: https://www.modular.com/blog/day-zero-minimax-m3-open-weights-on-modular-cloud
date: 2026-06-11
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 2d114d1f7493
---

June 11, 2026

# Day Zero: MiniMax M3 Open Weights on Modular Cloud

Modular Team

Company

💡

Today, MiniMax released the MiniMax M3 model as open weights. Modular is proud to be a Day Zero launch partner.

[MiniMax M3](https://www.minimax.io/blog/minimax-m3) is the newest open-weights model that has been optimized for coding, agentic work, and native multimodality for [MiniMax](https://www.minimax.io/). A few things that make this a frontier model are:

- **A 1M-token context window** (with a guaranteed minimum of 512K), built for long-running agent tasks, large coding workloads, and long-video understanding.
- **Native multimodality.** M3 is trained on both text and images, so it is multi-modal by design.
- **MiniMax Sparse Attention (MSA).** This is the key that keeps attention efficient as context grows.

MiniMax M3 accuracy benchmarks

across evaluation dataset.

# A look into **MiniMax’s Sparse Attention**

Behind M3 is a new MiniMax Sparse Attention ([MSA](https://github.com/MiniMax-AI/MSA/blob/main/docs/MiniMaxSparseAttention.pdf)) operation. MSA is what enables a 1M context to be served, and a big part of what makes M3 demanding to run well. But, if optimized, MSA’s design allows it to cut the per-token attention compute to roughly 1/20th of its full-attention predecessor. This results in around 9.7× speedup on prefill and 15.6× speedup on decode, while matching full attention across the vast majority of workloads.

MSA splits every attention layer into two parts: *which* KV to look at, and *how* to attend to it. The first is solved by introducing an indexing layer. For each query, the indexer scores candidate KV blocks and chooses the top-k blocks. The indexer also maintains a cache of index keys with a single shared head and a small head dimension. By focusing only on top scoring KV cache blocks, MSA only computes the attention of the relevant 128 tokens in the KV caches rather than the full block.

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

The model produces selection in *query-major* form: for each query, a list of top-k block IDs. The natural kernel follows that shape — loop over queries, gather their selected KV blocks, and then attend. Executing in query-major order would mean each query independently gathers its selected blocks, the same KV block may be fetched from HBM many times (which is not very efficient).

mojo

```
# Query-major: the natural schedule
for q_tile in queries:                    # parallel across threadblocks
    for blk in I[q_tile]:                 # this tile's top-k blocks
        K_blk, V_blk = load_block(blk)    # hot blocks re-fetched by EVERY threadblock that picked them
        online_softmax_update(q_tile, K_blk, V_blk)
```

To avoid the repeated loads, MSA inverts the mapping by grouping the queries by the KV block they selected; i.e. executing in key-block-major form and what MiniMax calls “KV outer gather Q”. As a result, we can improve the arithmetic intensity since the blocks are loaded once, before computing partial attention for all of those queries, and then merging the partial results.

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

This structure has an added benefit of simplifying the online softmax computation. Remember that in query-major attention one needs to perform online softmax. But in the block-major format, a thread block only ever sees *one* KV block per query group. Thus the softmax can be performed on a single tile without the need for an online correction. This is very much similar to the split-kv reduction step in flash decoding.

## Minimax M3 available today on Modular Cloud

The MiniMax M3 model bring novel innovations that require whole stack optimizations - from kernels to cloud. This is only possible in the Modular platform. MiniMax M3 is available on Modular Cloud today for enterprise customers. Talk to our AI engineers to [request access](https://console.modular.com/signup?utm_source=M3blog) today.

Discover what Modular can do for you

Request a demo

## Read more from Modular

View all blogs

Modular 26.6: Open compiler contributions, audio generation, and expanded model support

September 17, 2026

Mojo🔥 is now open source!

August 18, 2026

ModCon 2026: Open source, open cloud, open silicon

August 18, 2026

Build the future of AI with Modular

Get started - FREE

View Editions

- ![Person with blonde hair using a laptop with an Apple logo.](https://cdn.prod.website-files.com/68c9c3107effc2ea46e1a81f/68cc733ff9050921bab7782c_emoji-dev.png)Sign up todaySignup to our Cloud Platform today to get started easily.[Sign Up](https://docs.modular.com/max/get-started)
- ![Magnifying glass emoji with black handle and round clear lens.](https://cdn.prod.website-files.com/68c9c3107effc2ea46e1a81f/68cc733fb111718bbd49ca31_emoji-zoom.png)Browse open modelsBrowse our model catalog, or deploy your own custom model[Browse models](https://www.modular.com/models)

## Sign up for our newsletter

Get all our latest news, announcements and updates delivered directly to your inbox. Unsubscribe at anytime.

Thanks for signing up to our newsletter! 🚀

Thank you,

Modular Sales Team

Oops! Something went wrong while submitting the form.
