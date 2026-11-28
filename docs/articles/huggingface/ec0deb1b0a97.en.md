---
vendor: huggingface
title: DeepMath: A lightweight math reasoning Agent with smolagents
original_title: DeepMath: A lightweight math reasoning Agent with smolagents
url: https://huggingface.co/blog/intel-deepmath
date: 2025-12-08
lang: en
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: a13dd888d128
---

# DeepMath: A lightweight math reasoning Agent with smolagents

					December 4, 2025














![An LLM is using a calculator to answer questions.](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/intel-deepmath/deepmath-figure.jpg)

*By Intel AI Software Group*

[DeepMath](https://huggingface.co/Intel/deepmath-v1) is an aligned math reasoning agent built on **[Qwen3-4B Thinking](https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507)** and fine-tuned with **GRPO (Group Relative Policy Optimization)**. Instead of verbose text, the model emits **tiny Python snippets** for intermediate steps, runs them in a secure sandbox, and folds the results back into its reasoning, reducing errors and output length. The agent is implemented using the **[smolagents library](https://github.com/huggingface/smolagents)**.

We evaluate DeepMath on four math datasets: **[MATH500](https://huggingface.co/datasets/HuggingFaceH4/MATH-500), [AIME](https://huggingface.co/datasets/opencompass/AIME2025), [HMMT](https://huggingface.co/datasets/MathArena/hmmt_feb_2025), and [HLE](https://huggingface.co/datasets/cais/hle),** and show that:

- 🤖 The math agent alone reduces output lengths by up to 66%, while often improving accuracy.
- ⚡ GRPO training improves the agent performance even further, in almost all benchmarks.

👉 Code and evaluation scripts: [https://github.com/IntelLabs/DeepMath](https://github.com/IntelLabs/DeepMath) 
👉 Model: [https://huggingface.co/Intel/deepmath-v1](https://huggingface.co/Intel/deepmath-v1)

## Why DeepMath?

Large language models (LLMs) have advanced reasoning capabilities, but mathematical problem-solving remains challenging; chain-of-thought traces can be lengthy and prone to arithmetic mistakes. Recent works[^1][^2] demonstrate that small models can reach strong performance, and other studies[^3] investigate tool use to improve reliability. What those papers generally do not emphasize is reducing trace verbosity or explicitly training models to prefer short, computation-oriented traces executed in a constrained, auditable environment.

We focused on two goals:

- **Offload deterministic computation** to a safe executor.
- **Train models to prefer concise, computation-oriented traces** over verbose text.

**DeepMath** tackles this by combining a small Python executor with a fine-tuned LLM, enabling concise, computation-driven reasoning. The model learns to generate short Python snippets, which are executed in a sandbox and reintegrated into the context. GRPO fine-tuning encourages this behavior by rewarding correctness and encouraging shorter outputs.

## How It Works

- Base model: [Qwen3-4B Thinking](https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507).
- Executor constraints: sandboxed environment, allow-list of imported modules, per-snippet timeout.
- Inference: based on [smolagents](https://github.com/huggingface/smolagents/), a math agent was created. [vLLM](https://github.com/vllm-project/vLLM) is used as the inference engine.
- Training: based on the GRPO trainer in [TRL](https://github.com/huggingface/trl), we modified TRL's vLLM client and server to generate GRPO completions using our DeepMath agent.

![Changes to vLLM client and server in TRL library.](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/intel-deepmath/trl-grpo-vllm-deepmath.png)
 *Figure 1: The vLLM client and server were modified to use the DeepMath agent in generating the candidates, while using the vLLM backend.*

- **Agent Interface:** During inference, the model can output normal tokens or special agent calls containing Python snippets.
- **Execution:** Snippets run in a sandboxed environment with strict safety constraints (no file I/O, no network, timeouts).
- **Design Goals:**  **Concision:** Replace multi-line textual calculations with short, focused snippets.  **Determinism & Safety:** Enforce strict execution limits.  **Interpretability:** Snippets are readable and auditable.

![Output example: it contains a short python snippet as well as its output which is used in the reasoning process.](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/intel-deepmath/output-example.png)
 *Figure 2: Output example where python code is generated, evaluated and the answer is inserted into the trace and used for context.*

## Training with GRPO

We fine-tune the model using **GRPO**, a reward-based optimization that balances:

- **Accuracy Reward:** +1 for correct answers.
- **Using code snippets:** +1 for generating code snippets, weighted 10:1 vs. the accuracy reward.
- **Length reduction:** shorter lengths are encouraged by limiting the GRPO completion candidates to 5k tokens.
- **Temperature Scheduling:** We implemented linear temperature scheduling (T=1.2 → T=0.7) to balance exploration and stability during training. This approach aims to enhance experimentation during the initial training phases, subsequently reducing the temperature as we refine our proficiency in the skill.
- **In-context Learning**: we include 4 solved examples where the trace contains agent calls and executor outputs, so the model learns the syntax and the call/response pattern.
- **Dataset**: we used the Tool-Integrated Reasoning (TIR) subset of the [OpenMathReasoning](https://huggingface.co/datasets/nvidia/OpenMathReasoning) dataset. Note that GRPO only uses the problem, not the solution in the data. This dataset was chosen to ensure the problems benefit from the external tool.

## Evaluation

We benchmarked DeepMath against baselines on four datasets. Metrics include:

- **majority@16**: robustness across samples, as used in previous math reasoning works, see references.
- **Mean output length**: brevity.

![Main results table.](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/intel-deepmath/main-results.png)

- We compare a baseline configuration ([Qwen3-4B-Thinking-2507](https://huggingface.co/Qwen/Qwen3-4B-Thinking-2507), no agenting) with our DeepMath model. As ablation, we evaluate the agentic framework we developed running with the untrained Qwen3 model, denoted by **+Agent**. Additionally, we examine whether the GRPO training (for agentic use) improves non-agentic inference, denoted by **+GRPO**. Thus the two ablations are independent, not additive.
- We observe the agentic inference reduces output lengths, with mixed accuracy results. The DeepMath model is both GRPO-trained and run in agentic mode, and shows the highest accuracy with shortened traces. We conclude **both GRPO training and agentic inference are needed** for best results.

**Key Insight:** DeepMath reduces output length by up to **66%** while improving accuracy on challenging datasets.

## Why It Matters

- **Accuracy:** Offloading computation reduces arithmetic errors.
- **Efficiency:** Shorter outputs mean faster inference and easier interpretability.
- **Safety:** Sandbox execution mitigates risks of running arbitrary code.

## Conclusion

DeepMath demonstrates a practical and lightweight way to combine a small executor with an LLM and to train the model to prefer short, computation-driven traces. Offloading deterministic computation reduces arithmetic and numerical errors and shortens traces, and GRPO fine-tuning further encourages concise, correct answers. The result is a more accurate and more interpretable math-solving agent without requiring a massive model or heavyweight external tools.

## Try It Yourself

Check out the [GitHub repo](https://github.com/IntelLabs/DeepMath) and share your feedback! Contributions welcome. 🚀

## Citation

If you use DeepMath in your research, please cite:

```
@software{deepmath2025,
  author = {Fleischer, Daniel and Berchansky, Moshe and Wasserblat, Moshe},
  title = {DeepMath: A Lightweight Math Reasoning Agent for LLMs},
  year = {2025},
  publisher = {Intel AI Labs},
  url = {https://github.com/IntelLabs/DeepMath}
}
```

## Limitations & Future Work

- **Scope**: we focused on a small model and on mathematical reasoning.
- **Generalization**: evaluated on contest-style math; results may not transfer to open-ended mathematical creativity or formal proofs.
- Executing generated code is inherently risky. DeepMath uses strict sandboxing and resource limits, but any deployment should carefully manage attack surfaces and enforce rate limits.

## References

[1] Luo, Michael, Sijun Tan, Justin Wong, et al. 2025. “DeepScaleR: Surpassing O1-Preview with a 1.5B Model by Scaling RL.” [https://pretty-radio-b75.notion.site/DeepScaleR-Surpassing-O1-Preview-with-a-1-5B-Model-by-Scaling-RL-19681902c1468005bed8ca303013a4e2](https://pretty-radio-b75.notion.site/DeepScaleR-Surpassing-O1-Preview-with-a-1-5B-Model-by-Scaling-RL-19681902c1468005bed8ca303013a4e2)

[2] Liu, Mingjie, Shizhe Diao, Ximing Lu, et al. 2025. “ProRL: Prolonged Reinforcement Learning Expands Reasoning Boundaries in Large Language Models.” arXiv:2505.24864. Preprint, arXiv, May 30. [https://doi.org/10.48550/arXiv.2505.24864](https://doi.org/10.48550/arXiv.2505.24864)

[3] Moshkov, Ivan, Darragh Hanley, Ivan Sorokin, et al. 2025. “AIMO-2 Winning Solution: Building State-of-the-Art Mathematical Reasoning Models with OpenMathReasoning Dataset.” arXiv:2504.16891. Preprint, arXiv, April 23. [https://doi.org/10.48550/arXiv.2504.16891](https://doi.org/10.48550/arXiv.2504.16891)

## Models mentioned in this article 2

## Datasets mentioned in this article 5

More Articles from our Blog

llm

moe

long-context

## DeepSeek-V4: a million-token context that agents can actually use

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/62d648291fa3e4e7ae3fa6e8/oatOwf8Xqe5eDbCSuYqCd.png)

60

April 24, 2026

cybersecurity

open-source

community

## AI and the Future of Cybersecurity: Why Openness Matters

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1626214544196-60c757ea5f9a76ab3f844f12.png)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1594144055859-5ee3a7cd2a3eae3cbdad1305.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1583857146757-5e67bdd61009063689407479.jpeg)

52

April 21, 2026

### Community

InstructorOnline

Jan 18


edited Jan 18

Is it possible to use LLM to study and research math topics? All of the steps could be correct or incorrect depending on the variation of the generated output ??

deleted

May 7


This comment has been hidden

Upload images, audio, and videos by dragging in the text input, pasting, or

clicking here

.






## Models mentioned in this article 2

## Datasets mentioned in this article 5
