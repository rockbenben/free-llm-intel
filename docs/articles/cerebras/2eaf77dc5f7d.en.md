---
vendor: cerebras
title: MoE at Scale: Making Sparse Models Fast on Real Hardware
original_title: 
url: https://www.cerebras.ai/blog/moe-guide-scale
date: 
lang: en
captured: 2026-10-14
extractor: readability-v1
status: ok
body_sha: 7d1c5d58da2b
---

Oct 06 2026

# MoE at Scale: Making Sparse Models Fast on Real Hardware

[Daria Soboleva](https://www.cerebras.ai/author/dariasoboleva)[Quentin Anthony](https://www.cerebras.ai/author/quentin-anthony)

[MoE Fundamentals](https://www.cerebras.ai/blog/moe-guide-why-moe) | [Router Wars](https://www.cerebras.ai/blog/moe-guide-router) | [Debugging Dead MoE Models](https://www.cerebras.ai/blog/moe-guide-debug) | [MoE at Scale ](https://www.cerebras.ai/blog/moe-guide-scale)| [MoE Math Demystified](https://www.cerebras.ai/blog/moe-guide-calculator)

In this video we discuss scaling MoE models on modern hardware and address key optimization challenges. If you can’t open the video displayed above, please use this link to open it on YouTube: [https://youtu.be/MXo9LEYzwkg](https://youtu.be/MXo9LEYzwkg)

Mixture-of-Experts (MoE) models allow you to increase total parameter count without proportional increase in compute, letting you train bigger and better models efficiently (Soboleva, 2025a). You might wonder if extracting theoretical benefits from MoE models requires significant engineering work. After all, your part 3 implementation (Soboleva and Tiwari, 2025) trained perfectly fine on a small acceleration node (and even your laptop). An important point here is that you used only 4 experts and 124M backbone parameters, but production systems like DeepSeek-V3, Qwen3-30B-A3B, etc., use hundreds of experts and huge backbones. Try scaling to their sizes with our previous implementation on the GPU, and you will quickly hit your device’s memory limit.

Let’s understand why this happens. Remember the code on Figure 1 that we implemented in part 3? There we warned you that it isn’t efficient and we only used it for pedagogy. Why? On Figure 1, you can see that there is a sequential loop over all experts, even though we only need the experts that were selected for a given token. You might wonder, why so wasteful? You already know that the industry standard routing is not deterministic (Soboleva, 2025b), and thus it is impossible to predict which expert will be activated for a given token in advance. This means that we have to load all experts into memory just in case we might need them later (moving expert weights to the GPU memory on the fly for each token would be too slow given memory-bandwidth and latency limits). Because of that, we have a linear growth in memory requirements as you add more experts, and super quickly it becomes impossible to train on a single GPU (even a dozen of experts won’t fit with our previous implementation).

The rest of this guide covers solutions to this scaling challenge. First, we will talk about GPU solution and its limitations, second, we’ll cover how Cerebras Wafer Scale Engine (WSE) solves this problem, and finally how to combine both to maximize the benefits.

Figure 1: Expert mixing for batch processing (see train [train_gpt moe.pyL208-L225](https://github.com/cat-state/modded-nanogpt-moe/blob/blogpost-version/train_gpt_moe.py##L208-L225)).

### GPU Solution and Its Problems

When your MoE exceeds a single GPU’s memory capacity, the most popular solution is to use some sort of model parallelism, an example of which is expert parallelism, or EP in short (Lepikhin et al., 2020; DeepSeek-AI et al., 2024). With EP, we typically assign an equal number of experts to each GPU, while all other layers (attention, router, etc.) are replicated on each device. In this workflow, the router predicts which tokens should be routed to which experts, then an all-to-all communication operation shuffles tokens to the correct devices based on the router assignments, executes each expert in parallel and then shuffles results back to tokens’ original devices to perform expert mixing.

To make EP efficient, your experts have to be load-balanced across all layers in the network. This creates a tension between model quality and infrastructure efficiency. ML researchers optimizing for the best possible model quality often prefer routing strategies that allow experts to specialize heavily (Soboleva, 2025b), even if this creates load imbalance. Meanwhile, infrastructure teams need predictable, balanced workloads to achieve optimal hardware utilization, and minimize training costs. Both goals are critical, but they pull in different directions. Aggressive load balancing can hurt the model’s quality by forcing tokens to suboptimal experts (like the case we’ve seen with hash routing). But imbalanced experts create expensive infrastructure bottlenecks, where some GPUs sit idle, while others are overloaded, significantly decreasing overall hardware utilization.

Additionally, EP introduces communication overheads that worsen as we increase number of experts. Modern MoE architectures activate many small experts per token rather than fewer but larger ones for better compute efficiency (Krajewski et al., 2024). However, in this setup, intensive load balancing is required to parallelize with EP, which impacts model quality. If you can’t trade off quality for speed with aggressive load balancing, EP’s communication/computation ratio worsens, as we spend most of the time moving tokens around, rather than experts performing useful operations with them. Overall, training MoE models on GPUs remains challenging, as EP alone is typically not enough to generate sufficient parallelism.

### Cerebras WSE vs GPU (Architectural Differences)

GPUs running large MoE models typically need multiple parallelism strategies in addition to expert parallelism. For example, DeepSeek-V3 used a combination of pipeline, expert, and data parallelism (DeepSeek-AI et al., 2024). This creates a complex 3D parallel implementation that you must carefully tune, and that you must re-tune when either your model or the cluster changes. With Cerebras WSE, distributed computing is not required. We utilize data parallelism to train and scale our models. What makes this possible? We have about 900 times more on-chip memory (SRAM) than a latest single GPU, which allows us to store much bigger models on the chip directly. When scaling to larger models, we employ a technique called weight streaming (Hall et al., 2023) that disaggregates memory and compute on WSE. With weight streaming, we remove model parameters (those heavy tensors) from the wafer entirely. They now live in the external memory units, and we stream them to the wafer during training to compute gradients. The wafer streams gradients back to the memory units to update the weights. This technique allows us to train today’s trillion parameter MoE models (Kimi Team, 2025) on just a single device.

### Memory Problem Solved, Now Compute

We’ve established that Cerebras WSE can fit large MoE models on the chip directly with weight streaming and no model parallelism required. But just because you can train a trillion-parameter MoE doesn’t mean it is efficient. As models get more sparse (more experts, lower *top_k*), we now hit a different issue, which is compute utilization. Remember that promised 62% reduction in FLOPs (Floating Point Operations) with 32 experts in the part 1 of this series? There we noted that it would result in MoE model training 3x faster than the dense baselines to achieve the same loss. But this is not what we see in practice. What happens is that we fail to transfer these FLOP reductions into the actual wall-clock speedups. It becomes inefficient to train MoE models at scale.

Why does it happen? With a sparse MoE model, our routing subdivides the batch size across many experts. It results in most experts only seeing a tiny portion of the original batch. Small batches mean most of your experts sit idle, not computing useful operations. You’re loading big expert networks’ matrices, but barely using them (you become I/O bound in these layers). At the same time, attention layers can’t handle larger batches because they are activation memory-bound (Anthony et al., 2023; Korthikanti et al., 2022). This means that they must store large intermediate tensors like attention scores that scale quadratically with sequence length [1]. Thus we have this persistent utilization gap between expert and attention layers. Expert networks are starving and waiting until more data comes in for them to process, and attention layers struggling to efficiently process larger bulks of tokens, preventing us from moving data quicker to the expert networks.

### Batch Tiling on Attention

To solve this problem, on Cerebras WSE we decouple batch size requirements between the attention and expert networks. We call this technique Batch Tiling on Attention (BTA). With BTA, we split attention’s input batch size into G tiles of size B, processing each tile independently, then concatenating the results back together for a large batch size of G × B that we feed into the expert networks (Figure 2).

Figure 2: Batch Tiling on Attention (BTA) architecture. The input batch is split into G tiles, each processed through attention with small batch size B. Outputs are concatenated to form a large batch G × B for expert processing, decoupling batch size constraints between attention and expert layers.

Similarly to how FlashAttention (Dao et al., 2022) tiles along the sequence dimension to reduce memory usage, BTA tiles along the batch dimension to improve imbalanced utilization between expert and attention networks. BTA’s dual batch strategy directly targets MoE’s compute requirements. We use smaller batches for attention layers, reducing their activation memory, and larger batches for expert networks, improving their compute utilization.

Let’s stress-test our BTA technique on one of the recent MoE models called Qwen3-30B-A3B with 3B active parameters (Yang et al., 2025) on a single CS-3 machine. Originally this model uses learned routing with 128 experts and *top_k* = 8 activated ones per each token. We are going to vary *top_k* and the number of experts, thereby varying the sparsity of the model, and observe the effect of sparsity on throughput both with and without BTA.

First, we’ll keep *top_k* fixed at 8 and vary the number of experts from 16 to 128, measuring throughput degradation compared to the dense model with the same number of active parameters. Figure 3a shows that “red” line throughput (conventional batching without BTA) degrades severely, reaching up to 53% (2x slowdown!) with 128 experts. The “blue” line (with BTA and G values tuned to achieve the best speed) shows that throughput stays high, close to the dense model, across all expert counts. In the second experiment, let’s fix number of experts to 128 and vary number of activated experts *top_k* from 1 to 8. In this experiment, we also maintain a fixed number of active parameters by adjusting expert network sizes with a change of *top_k* accordingly. Figure 3b shows that conventional batching demonstrates even larger degradation in throughput as we increase levels of sparsity in the network (lower *top_k*), reaching up to 86% worse speed (7x slowdown!) than our dense model. BTA again maintains high throughput regardless of *top_k* that we used.

Figure 3: BTA prevents throughput degradation as MoE models become sparser. Conventional batching (“red” line) shows severe throughput drops (up to 53% with more experts, 86% with smaller *top_k*), while BTA (“blue” line) maintains stable and high throughput comparable to the dense model across all configurations.

### Show Me the Math

In the sections above, we claimed that EP on GPUs creates communication bottlenecks, whereas on the Cerebras WSE we see compute utilization challenges. We then saw how BTA solves the WSE utilization problem.

Let’s now dig deeper by creating a mathematical model, formalizing these claims using the model, and derive predictions of efficiency from it. We build upon computational frameworks established in (Anthony et al.; Korthikanti et al., 2022), extending their analysis to our MoE setting. If not mentioned otherwise, we assume mixed precision training (fp16/bf16 for the low precision param copy, and fp32 for the high-precision param copy and optimizer states). We omit bias terms from the following equations as they are negligible. Below are the notations needed for our analysis:

- : sequence length
- : batch size
- : hidden size
- : number of query heads in attention
- : number of tiles (in BTA, tiling on the batch)
- : number of activated experts per token
- : FFN multiplier (in MoE layer, filter size / hidden size)
- : number of layers
- : number of experts
- : storage requirement per model parameter (in bytes)

### GPU

Let’s do our analysis on the Qwen3-30B-A3B model (, , , , ,  with SwiGLU nonlinearity) that was used for the experimental section above. First thing we should understand is whether this model can fit on a single GPU. Let’s assume that we have an H100 GPU with 80GB of memory. Let’s calculate the amount of storage we need for just a single MoE layer weights:

With mixed precision we need  bytes per parameter. Accounting for at least model weights and their gradients across all  layers this gives us approximately 116GB of memory needed. Thus, we cannot fit this model on a single H100 GPU and will need to enable some version of model parallelism. While several parallelism schemes exist, we focus on EP for our analysis.

When training an MoE model on a GPU, the memory requirement for a particular layer includes weights, gradients, optimizer states, and activations. The combined weights, gradients, and optimizer states require  bytes of storage per weight. Accounting for all MoE layers in the network we obtain 464GB of storage needed. Following Korthikanti et al. (2022), the amount of activation memory per MoE layer can be computed as:

For our Qwen3-30B-A3B configuration with batch size  using  bytes of storage, this yields approximately 8GB of activation memory across all layers , bringing the memory requirement to roughly 472GB. Now you can see that we need at least 8 H100 GPUs to train this model, and we can place  experts on each GPU with EP. All other layers such as attention layers (K, Q, V matrices), routers and other non-MoE components are replicated on each GPU.

In the sections above, we claimed that EP suffers from communication overhead. Let’s quantify exactly how bad it is in our setup. For that, we will calculate the compute-to-communication time ratio in MoE layers to see what dominates.

With 8 H100 GPUs providing roughly 800 peak TFLOPs/s per GPU (Bekman, 2023-2024). Assuming that we achieve around 500 TFLOPs/s per GPU during the expert MLP GEMMs (which we believe to be representative of realistic GEMM shapes within common MoE models today), expert networks will finish processing data in **0.08 ms**. For communication cost, we account for 2 phases of calling all-to-all operations:

At NVLink’s 350GB/s bandwidth (see Appendix for measurement details), and assuming each token consumes 2 bytes of storage, this data movement takes approximately **0.77 ms**. Put differently, communication consumes 91% of the total MoE layer processing time.The situation gets worse as we increase the number of active experts (resulting in additional communication overheads) and making each expert smaller (reducing useful compute parallelism).

### Cerebras WSE

On Cerebras WSE, we never store model weights on the chip directly. Thus, increasing total number of experts does not require us to employ EP or any other type of model parallelism.

But we hit a different problem. Earlier we showed that MoE model throughput degrades as we introduce more sparsity in the network. This happens because sparse MoE models subdivide the batch size, reducing the amount of useful work per expert while still loading all weights into memory. To quantify this effect, let’s calculate arithmetic intensity (AI) for our Qwen3-30B-A3B model at various sparsity levels:

Arithmetic intensity measures how many floating point operations we get per byte of memory we need to move around. Lower arithmetic intensity means that compute units spend more time idle, waiting for memory transfers.

Plugging in our Qwen3-30B-A3B model configuration and simplifying, we get . Each expert subdivides the batch size and will process on average  sequences. When inducing the minimum level of sparsity ( , analogous to dense network processing), each expert will process the same batch size of , where  is the batch size used elsewhere in the network. However, when using the maximum level of sparsity (, activating only 1 expert per given token), each expert will process on average  sequences, only a tiny portion of the original batch. With a reasonable batch size of  sequences, maximum sparsity results in almost **88%** lower arithmetic intensity compared to minimum sparsity. This means that sparser MoE networks become more I/O bound and severely underutilize their allocated resources. This explains why we see such a big throughput degradation between MoE models and dense networks when training on Cerebras hardware (“red” curve in Figure 3). BTA fixes this issue. We simply make the experts’ batch size a function of the number of experts: . Consider our most sparse case with , where we observed the greatest arithmetic intensity degradation. Instead of each expert processing only  sequences, we now have  sequences per expert. With  and , each expert will process entire batch , which completely restores arithmetic intensity of the MoE layer to match that of minimum sparsity.

For various sparsity levels, we can find the best  to ensure that sparsity has minimal effect on arithmetic intensity and thus throughput of MoE layers and the overall network. However, let’s discuss one more consideration. If we continue growing batch size by G to benefit sparse MoE layers, this creates a problem for attention layers that are activation memory bound [2]. Following Korthikanti et al. (2022), the activation memory per attention layer can be computed as:

The quadratic  [3] term means that scaling batch size by  can quickly exhaust available memory. With BTA, we address this too. As we grow expert networks’ batch size to improve their arithmetic intensity, we also tile the batch size in the attention networks across  groups. We never realize activation memory for attention for all  groups simultaneously and thus reduce their storage requirement, making them less activation memory bound.

To summarize, our analysis confirms exactly what we’ve claimed. EP on the GPUs creates severe communication overheads that dwarf actual computation. On Cerebras WSE, we avoid model parallelism entirely but face a different challenge. As sparsity increases, experts receive subdivided batch sizes that severely underutilize resources, making them I/O bound. With BTA, we fix the problem on Cerebras WSE by decoupling the batch size requirements across expert and attention layers, addressing their unique computational bottlenecks. As demonstrated in Figure 3 (“blue” curve), BTA allows us to train MoE models at the speed of dense networks on Cerebras hardware.

### Bringing It All Together

MoE models are hard to train efficiently. Especially when we go to higher levels of sparsity. Highly sparse MoE models have many more parameters than dense models. With only a few dozen experts, they can hit memory limits on GPUs (a very tiny number given that production MoE models use hundreds of experts nowadays). With larger number of experts GPUs require certain model parallelization techniques implemented to load all experts into the memory. You need to utilize expert parallelism to distribute expert networks across devices and make sure that experts stay load balanced.

Given that memory constraint is less critical on Cerebras hardware, we looked at compute inefficiencies that sparser networks experience. We talked about how techniques like BTA can be employed, significantly improving compute utilization of MoE models on the wafer. It’s worth mentioning that BTA is not a silver bullet. It is one optimization technique in the broader optimization toolkit. The expert parallelism that we discussed for GPU clusters can be applied equally well on the Cerebras hardware. You can distribute experts across multiple WSE devices while using BTA on each device to maintain high compute utilization.

That’s it. You now have the complete picture of MoE training at scale. You understand the fundamental concepts from part 1, know how to choose the right routing method from part 2, can debug MoE training issues with part 3, and have seen how to solve memory management and compute utilization problems on modern hardware (whether you’re training on GPUs with EP or on Cerebras WSE with BTA). In the next part [MoE Math Demystified: What Does 8x7B Actually Mean?](https://www.cerebras.ai/blog/moe-guide-calculator), we’ll shift focus from training to deployment. We will provide you with practical tools to make informed decisions whether to deploy an MoE model or stick to the dense architectures, depending on your constraints.

### Citation

Questions? Find me at: [https://soboleva-daria.github.io/](https://soboleva-daria.github.io/)

### Footnotes

[1] On Cerebras hardware, we don’t use FlashAttention and offload activation tensors into the memory units whenever they are not being used.

[2] Usually, all layers in the network use a batch size of , except for MoE layers that subdivide it.

[3] Qwen3-30B-A3B uses grouped-query attention (GQA), which shares key and value projections across groups of query heads. We keep the multi-head form of equation (6) for simplicity, since GQA does not change the quadratic dependence on  that we use in our analysis.

### References

Anthony, Q., Biderman, S., & Schoelkopf, H. (2023). Transformer Math 101. *Eleuther AI Blog*. [https://blog.eleuther.ai/transformer-math/](https://blog.eleuther.ai/transformer-math/)

Bekman, S. (2023-2024). Machine Learning Engineering Open Book. GitHub repository. [https://github.com/stas00/ml-engineering](https://github.com/stas00/ml-engineering)

Cerebras Systems (2023). Training giant neural networks using weight streaming. *White Paper*. [https://www.cerebras.ai](https://www.cerebras.ai/)

Dao, T., Fu, D. Y., Ermon, S., Rudra, A., & Ré, C. (2022). FlashAttention: Fast and memory-efficient exact attention with IO-awareness. *arXiv preprint arXiv:2205.14135*. [https://doi.org/10.48550/arXiv.2205.14135](https://doi.org/10.48550/arXiv.2205.14135)

DeepSeek-AI (2024). DeepSeek-V3 technical report. *arXiv preprint arXiv:2412.19437*. [https://doi.org/10.48550/arXiv.2412.19437](https://doi.org/10.48550/arXiv.2412.19437)

Kimi Team (2025). Kimi K2: Open agentic intelligence. *arXiv preprint arXiv:2507.20534*. [https://doi.org/10.48550/arXiv.2507.20534](https://doi.org/10.48550/arXiv.2507.20534)

Korthikanti, V., Casper, J., Lym, S., McAfee, L., Andersch, M., Shoeybi, M., & Catanzaro, B. (2022). Reducing activation recomputation in large transformer models. *arXiv preprint arXiv:2205.05198*. [https://doi.org/10.48550/arXiv.2205.05198](https://doi.org/10.48550/arXiv.2205.05198)

Krajewski, J., Ludziejewski, J., Adamczewski, K., et al. (2024). Scaling laws for fine-grained mixture of experts. *arXiv preprint arXiv:2402.07871*. [https://doi.org/10.48550/arXiv.2402.07871](https://doi.org/10.48550/arXiv.2402.07871)

Lepikhin, D., Lee, H., Xu, Y., Chen, D., Firat, O., Huang, Y., Krikun, M., Shazeer, N., & Chen, Z. (2020). GShard: Scaling giant models with conditional computation and automatic sharding. *arXiv preprint arXiv:2006.16668*. [https://doi.org/10.48550/arXiv.2006.16668](https://doi.org/10.48550/arXiv.2006.16668)

Qwen Team (2025). Qwen3-30B-A3B technical report. *arXiv preprint arXiv:2505.09388*. [https://doi.org/10.48550/arXiv.2505.09388](https://doi.org/10.48550/arXiv.2505.09388)

Soboleva, D. (2025). Debugging dead MoE models: A step-by-step guide. *Cerebras Blog*. [https://www.cerebras.ai/blog/moe-guide-debug](https://www.cerebras.ai/blog/moe-guide-debug)

Soboleva, D. (2025). MoE fundamentals: Sparse models are the future. *Cerebras Blog*. [https://www.cerebras.ai/blog/moe-guide-why-moe](https://www.cerebras.ai/blog/moe-guide-why-moe)

Soboleva, D. (2025). Router wars: Which MoE routing strategy actually works. *Cerebras Blog*. [https://www.cerebras.ai/blog/moe-guide-router](https://www.cerebras.ai/blog/moe-guide-router)

### Appendix

Table 1: NCCL all-to-all bus bandwidth results on an 8×H100 SXM5 node. Results show bandwidth converging to 350 GB/s at larger message sizes. The [nvcr.io/nvidia/pytorch:24.10-py3](https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-24-10.html) docker container was used for the software environment, and the benchmark under test is nccl-tests all-to-all bandwidth.

### The MoE 101 Guide

Page

### MoE Fundamentals: Sparse Models Are the Future

Blog

### Router Wars: Which MoE Routing Strategy Actually Works

Blog

### Debugging Dead MoE Models: A Step-by-Step Guide

Blog

### MoE Math Demystified: What Does 8x7B Actually Mean?

Blog
