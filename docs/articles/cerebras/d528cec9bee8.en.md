---
vendor: cerebras
title: Jais 2: A Blueprint for Sovereign AI
original_title: Jais 2: A Blueprint for Sovereign AI
url: https://www.cerebras.ai/blog/jais2
date: 
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 5bef68098ae6
---

Dec 09 2025

# Jais 2: A Blueprint for Sovereign AI

James Wang

Natalia Vassilieva

Avraham Sheinin

Arabic is spoken by more than 400 million people, yet Arabic-centric Large Language Models (LLMs)still lag behind English-optimized frontier models. Building on the experience gained with the original Jais models, G42’s Inception, the Institute of Foundation Models at MBZUAI and Cerebras Systems introduce Jais-2—a new family of Arabic-centric LLMs, that represent the most capable and culturally aligned Arabic LLMs to date. Jais 2 models were trained end-to-end and deployed for production grade inference on Cerebras wafer-scale clusters, bringing frontier-level capability to models purpose-built for Arabic speaking nations. The Jais 2 chat application runs at 2,000 tokens per second, making it one of the fastest LLMs in the world. Jais 2 serves as a blueprint for sovereign AI, showing how nations can develop highly capable, culturally aligned models at lower cost, higher speed, and without the complexity of large GPU clusters.

Large Western-trained frontier models deliver impressive general intelligence, but they are not contextually grounded in Arabic language, culture, law, or social norms, and much of their capacity is devoted to domains unnecessary for many regional uses. This lack of grounding is most visible in areas such as dialect variation, politeness and deference norms, religious and ethical reasoning – areas where global models routinely misinterpret intent or produce answers that feel unnatural or inappropriate to local users. Existing Arabic-specific models, meanwhile, tend to be too small to retain broad knowledge and robust multilingual capabilities. Jais-2 bridges this gap: a model that combines frontier-level intelligence with deep Arabic linguistic and cultural grounding.

Jais 2 builds on the progress established with the original Arabic–English Jais model family that demonstrated the viability of a dedicated bilingual approach and set early benchmarks for Arabic LLMs. Jais 2 demonstrates significantly higher quality with new 8B and 70B models, compared to the original Jais family, due to a redesigned architecture, a larger and higher-quality Arabic corpus, and a more rigorous fine-tuning and alignment pipeline. Jais 2 70B establishes new state-of-the-art performance for Arabic models on a key Arabic leaderboard, AraGen. It also leads in general tasks such as translation, summarization, and financial analysis, and excels is domains deeply rooted in Arab life, such as poetry, religion, cuisine, and dream interpretation. The combination of model scale, data curation, and efficient training recipe makes Jais-2 the strongest open Arabic LLM available today.

The figure below plots training FLOPs against performance on a leading Arabic benchmark, AraGen, for several Arabic-centric models (Falcon, Fanar) and widely used English-centric or multilingual models (Llama, Qwen). Jais 2 8B model outperforms all other Arabic-centric models of comparable size while being trained on far less data, and hence being much cheaper to train. Jais-2 70B achieves the highest Arabic score while also requiring significantly less training compute than other models of similar size. These results highlight the training efficiency enabled by Cerebras wafer-scale hardware and the optimized Jais-2 training recipe.

Jais 2 is publicly accessible through the [web](https://www.jaischat.ai/jaischat) as well as dedicated mobile applications for both iOS and Android, making the system easily available to users across the region. For developers and researchers, the team has released open-weight 70B and 8B variants on [HuggingFace](https://huggingface.co/collections/inceptionai/jais-2-family), to facilitate integration, experimentation and further research. We encourage the community to evaluate the models and appand share feedback to help guide future improvements.

This work represents a multi-institution effort completed over months of coordinated engineering, data curation, and large-scale training across Inception,MBZUAI, and Cerebras. In the following section, we outline the five key stages of development—from early model design and scaling-law exploration to pretraining, supervised fine-tuning, and alignment. For full details, see the complete Jais 2 technical report.

### Frontier Model Development Pipeline

Systematic experimentation at small and medium scales is essential for building high-quality large models. It enables disciplined architecture search, efficient hyperparameter tuning, and, critically, the ability to derive scaling laws that guide decisions for large scale training. Cerebras infrastructure makes it easy to switch between different model and cluster sizes, dramatically simplifying this critical phase.

Following this approach and to ensure the most efficient model architecture and training recipe, the team ran a comprehensive suite of low-cost experiments to validate model depth/width ratios, FFN expansion, ReLU² stability, high RoPE base frequency, learning-rate schedules, and tokenizer behavior at low cost. Running these experiments quickly on Cerebras systems—without designing parallelism strategies—made it possible to test many architectural and hyperparameter configurations and verify scaling-law behavior cleanly. Maximal Update Parameterization (µP) ensured that learning rates and optimization settings identified at small scale can be transferred reliably to the 8B and 70B models in a zero-shot manner. This experimentation and architecture search defined the model blueprint and laid the foundation for stable pretraining and efficient fine-tuning.

- Pretraining –Jais-2 was pretrained from scratch on 2.6 trillion curated Arabic, English, and code tokens - about one-seventh the dataset size used for Llama-3 70B - establishing the model’s core linguistic and reasoning capabilities. Despite significantly lower token training budget, the resulting model achieves state-of-the-art performance in Arabic and is competitive in English with similar-sized models. Jais-2 followed a two-stage pretraining regimen: Stage-1 broad pretraining, which consumed over 90% of the total compute, followed by Stage-2 targeted refinement using the remaining 5–10% to strengthen domain-specific and Arabic-specific performance.
- Supervised Fine-Tuning (SFT) - More than twenty million instruction–response pairs were used to teach bilingual instruction following, structured reasoning, and controllable conversational behavior. Arabic SFT included MSA, dialects, poetry, religious reasoning, sentiment analysis, and domain-specific tasks.
- Direct Preference Optimization (DPO) - DPO used large batches of human preference comparisons across Arabic and English to refine helpfulness, safety, tone, politeness, refusals, and cultural appropriateness.
- GRPO - A final GRPO phase improved multi-turn coherence, reduced conversational drift, and stabilized step-by-step reasoning, completing the alignment stack.

### Training on Condor Galaxy: Unified Memory for Efficient Training

Jais 2 models were trained on Condor Galaxy 1 and Condor Galaxy 2 clusters, each containing sixty-four Cerebras CS-2 systems connected to a unified MemoryX and SwarmX fabric. Instead of stitching together hundreds of GPUs, weight streaming places all model parameters in a single, terabyte-scale block of memory inside MemoryX. Each CS-2 streams weights from this monolithic memory pool, eliminating duplication and removing the need for tensor parallelism, pipeline parallelism, or ZeRO partitioning. This design allows the entire cluster to behave like one chip with one block of memory. The cluster provides near-linear performance scaling from one to sixty-four systems—dramatically simplifying the training workflow.

### Inference on Condor Galaxy: 20× Faster Than ChatGPT

Once training was complete, we deployed the larger of the two models, Jais 2 70B, on a Cerebras CS-3 cluster for inference. In inference mode, MemoryX is bypassed entirely: all model weights are loaded directly into on-wafer SRAM spread across the interconnected CS-3 systems. Our SRAM architecture delivers petabyte-per-second bandwidth—orders of magnitude greater than the latest HBM memory used by GPUs, enabling dramatically faster inference output than the latest GPUs.

In addition, Cerebras’ inference team developed a high-fidelity draft model for Jais 2 and paired it with our in-house speculative decoding stack. The combined result of our SRAM architecture and spec decode is output speed of 2,000 tokens per second for Jais 2 70B, more than 20× faster than frontier models like GPT-5 and Claude on real workloads. High speed inference unlocks powerful new applications like instant document summarization, realtime code iteration, and low latency voice agents. These capabilities have helped Cerebras customers such as Cognition, Notion, and Mistral achieve strong differentiation in the market.

### A Blueprint for Sovereign AI

Jais 2 establishes a new state of the art for Arabic language models and sets a benchmark for how a regional, culturally grounded frontier model should perform. It is available as open weights and through public interfaces across the UAE and wider Arabic-speaking world—bringing advanced AI capability to institutions, developers, and governments across the region.

This project also demonstrates the full potential of the Cerebras wafer-scale architecture for sovereign AI development. Its unified, terabyte-scale MemoryX training environment avoids the complexity of GPU-based distributed memory management, while inference uses on-wafer SRAM to achieve world-leading generation speed at 70B scale. The UAE is the first country to deploy this complete training-to-inference workflow on Cerebras hardware for the benefit of an entire region, proving that national-scale AI capability can be built without reliance on GPU megaclusters. As other nations pursue their own sovereign AI strategies, we look forward to partnering with them to build powerful and efficient frontier models.
