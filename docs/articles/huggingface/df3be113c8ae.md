---
vendor: huggingface
title: 在一台 RTX PRO 6000 上进行爬山 Inkling 2 Mini 推理
original_title: 
url: https://huggingface.co/blog/inkling-2-mini-inference-hillclimb
date: 2026-11-25
lang: zh
captured: 2026-11-26
extractor: readability-v1
translator: llm
status: translated
body_sha: 841eaa4a9f83
---

# 在单张 RTX PRO 6000 上对 Inkling 2 Mini 推理进行爬山调优

发布于 November 25, 2026


[![Niels Rogge 的头像](https://cdn-avatars.huggingface.co/v1/production/uploads/1608042047613-5f1158120c833276f61f1a84.jpeg)](https://huggingface.co/nielsr)

Niels Rogge

nielsr

[Inkling 2 Mini](https://huggingface.co/blog/inkling2mini) 上周发布，为本地 AI 和更小的开源模型树立了新的最先进水平。凭借约 26B 总参数（每 token 激活 3B）、多模态输入和 1M-token 上下文窗口，它在 [Artificial Analysis Intelligence Index v5](https://artificialanalysis.ai/models/open-source) 上、以及在 48 项基准中的 32 项上领先 Gemma 4 31B 和 Qwen3.8-27B 等模型，使其成为在中等硬件上进行编码、工具使用和推理的强开源选项。我们写了一篇详细的博客文章，介绍如何在 Hugging Face 生态中使用它，见[这里](https://huggingface.co/blog/inkling2mini)。

Inkling 2 Mini 一个有趣且可能解释其出色性能的方面是其不同寻常的架构。Inkling 2 Mini 是一个循环式 [Mixture-of-Experts (MoE)](https://huggingface.co/blog/moe) 模型，有 24 个物理层，其中中间 12 层运行三次，因此每个 token 经过 48 层。该 checkpoint 以混合 NVFP4 和 MXFP8 形式发布，并捆绑一个用于投机解码的 DSpark drafter。作为 LLM 推理的首选框架，vLLM 和 SGLang 都在 nightly 构建中支持它，不过已发布的服务 recipe 面向 NVIDIA B200 和 GB300 GPU（`sm100`），遗漏了像 NVIDIA RTX PRO 6000 这样的 `sm120` 卡，在这些卡上内核兼容性可能不同。

我们想看看在单张 NVIDIA RTX PRO 6000 96 GB 上能多快地服务它，这是 `nvidia-rtx-pro-6000` [Inference Endpoint](https://huggingface.co/docs/inference-endpoints) 背后的 GPU。我们没有手动调 flag，而是给一个编码 agent 提供了 [`inference-optimisation`](https://github.com/sybil-solutions/inference-optimisation-skill) 技能、`hf` CLI，以及对 [Hugging Face Jobs](https://huggingface.co/docs/hub/jobs-overview) 的访问权限，让它运行了一个下午的实验。

在 46 次有效基准运行中，单用户解码从 **136 提升到 190.6 tok/s（+40%）**（超过同一 GPU 上 [LocalMaxxing 的 167.7 tok/s 社区 SGLang + DSpark 基准](https://www.localmaxxing.com/en/inference-benchmarks/cmwqfbexc089gmi01hd6hiqhn)），使用 vLLM nightly 和 DSpark 投机解码时，8 用户聚合吞吐从 **约 570 提升到 716 tok/s（+26%）**。无论是否启用投机，贪心输出都逐字节相同，长上下文 needle 检索在最高 250K token 时通过 3/3，获胜配置现在正基于固定镜像 digest 作为 Inference Endpoint 运行。所有日志、脚本和原始测量数据都在 [`NielsRogge/inkling-2-mini-hillclimb`](https://github.com/NielsRogge/inkling-2-mini-hillclimb) 中。

## 设置

`inference-optimisation` 技能给 agent 一个固定的实验协议和一个小的、与引擎无关的基准脚本（[`bench.py`](https://github.com/sybil-solutions/inference-optimisation-skill/blob/main/skills/inference-optimisation/scripts/bench.py)）：

- 在调优前测量硬件并估计理论上限。
- 一次只改变一个变量，并将每个候选配置夹在两次对照运行之间（`control → candidate → control`）。只有当某项变更优于两次对照且未使其他指标回退时才保留。
- 将每次运行记录到 `PLAN.md`，包括回归和死胡同。
- 在宣布获胜者之前通过长上下文、并发和贪心等价性检查。

`bench.py` 测量单用户解码、并发 N 下的聚合解码、若干长度下的冷 prefill 和 TTFT，直接使用服务器 usage 响应中的 token 计数。所有运行都使用固定的一组六个提示（代码、解释、故事、比较表、bash 脚本和历史摘要），temperature 1.0（模型默认值），thinking 开启，512 个输出 token，并在启用投机解码时重复 12 次。

该技能是为本地 GPU 编写的，因此我们将它适配到 Hugging Face 基础设施：

- **HF Jobs** 用于计算。`rtx-pro-6000` Job flavor 使用与 `nvidia-rtx-pro-6000` Inference Endpoint 相同的 GPU（两者均为 $2.75/h），因此 Job 数据可以直接迁移。一个约 150 行的驱动脚本（`jobs/driver.py`）接收服务器配置列表，依次启动每个配置，运行一次不计入测量的预热，原样调用 `bench.py`，关闭服务器，并为每次运行打印一行台账。由于 Job 在独立机器上运行，agent 并行扫描了 SGLang（`lmsysorg/sglang:inkling-2-mini`）和 vLLM nightly（`vllm/vllm-openai:nightly`）。
- **用于阅读引擎源码的 CPU Jobs。** 当某个 flag 没有文档时，agent 会运行一个低成本的 `cpu-upgrade` Job，在容器内 grep 已安装的 Python 包。它就是这样找到 SGLang 的 `SGLANG_OPT_*` 环境变量和 vLLM 的 `speculative-config` 字段的。
- **Inference Endpoints** 用于部署，通过 `hf endpoints deploy` 创建，使用通过验证的精确镜像 digest 和 flags。

基线是我们现有的组织 endpoint 配置：SGLang 使用 `--attention-backend fa4`，且不启用投机解码。

## 结果

[![在单张 RTX PRO 6000 上四种配置下 Inkling 2 Mini 的单用户解码速度](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/inkling-2-mini-inference-hillclimb/results.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/inkling-2-mini-inference-hillclimb/results.png)

*单用户解码速度（12 次请求的中位数）。vLLM + DSpark 在其测得的接受率下达到内存带宽上限的约 95%。*

| 配置（1× RTX PRO 6000） | 单用户解码（tok/s） | 8 用户聚合（tok/s） | Prefill 4K / 32K（tok/s） | TTFT |
| --- | --- | --- | --- | --- |
| SGLang，无投机（基线） | 134–139 | 543–598 | 18.7–19.1K / 16.9–19.1K | 41–114 ms |
| vLLM，无投机 | 157.0 | 638 | 20.7K / 20.7K | 33 ms |
| SGLang + DSpark（8 个 drafts） | 166.6 | — ¹ | 18.0–19.5K / 18.9–19.1K | 38–51 ms |
| **vLLM + DSpark（7 个 drafts）** | **190.6** | **716** | 20.7K / 20.6K | 40 ms |
| 已部署 endpoint（通过互联网） | 194.9 | 673 | 11.7K / 19.2K ² | 198 ms ² |

¹ SGLang 的 RTX PRO 6000 DSpark recipe 将 `--max-running-requests` 上限设为 4。将其提高到 8 后达到 660 tok/s，仍落后于 vLLM。 ² 包含约 160 ms 的客户端到 endpoint 网络往返。

全部加速来自切换到 vLLM nightly（+15%，相较无投机的 SGLang，136 → 157 tok/s）、启用带 7 个 drafts 和概率式 draft 采样的 DSpark（在此基础上再 +21%，四次运行中 157 → 190.6 tok/s：189.3、190.4、191.1 和 190.7），以及添加两个内存 flag，使 vLLM 的 DSpark 设置真正能在 96 GB 上启动：

```
vllm serve thinkingmachines/Inkling-2-Mini \
  --tool-call-parser inkling \
  --enable-auto-tool-choice \
  --reasoning-parser inkling \
  --max-model-len 262144 \
  --gpu-memory-utilization 0.85 \
  --speculative-config '{"method":"dspark","num_speculative_tokens":7,"draft_sample_method":"probabilistic"}'
```

`num_speculative_tokens: 7` 和 `draft_sample_method: "probabilistic"` 都经过直接验证：更短的 draft 数量（例如 5）会在启动时被拒绝，因为两个引擎都会强制执行 checkpoint 的固定 block size；而在 temperature 1.0 下切换到 `greedy` draft 采样会使 vLLM 解码速度下降 11%（见[哪些没有奏效](https://huggingface.co/blog/inkling-2-mini-inference-hillclimb#what-didnt-work)）。

### 为什么停在约 190 tok/s

在调优前，agent 在 Job 内探测了 RTX PRO 6000（**1,469 GB/s** 拷贝带宽、**416 TFLOPS** BF16、**792 TFLOPS** FP8），并从 safetensors 头读取张量大小。因为每个 token 要进行 48 次层访问，普通解码会重新读取约 2.7 GB 的注意力与稠密权重、约 2 GB 的路由专家（每层 128 个中的 8 个），以及约 0.9 GB 的 LM head。在 1,469 GB/s 下，这给出 **约 256 tok/s** 的单用户带宽上限。无投机时，vLLM 的 157 tok/s 达到该上限的 61%，主要受限于跨 48 次访问的内核启动延迟。

投机解码改变了 MoE 上的内存计算。共同验证 8 个位置会激活其路由专家的并集，读取每层专家的约 40%，而不是 6%。在 temperature 1.0 下，我们测得的接受率约为每步 2.3 个 token（每个位置的接受率从第一个 draft 的 0.6 降到 0.33 和 0.19），带宽上限降至 **约 201 tok/s**。在 190.6 tok/s 时，vLLM + DSpark 已经达到**硬件带宽的约 95%**，因此进一步调 flag 几乎没有剩余空间。要越过 190 tok/s，需要具有更高 temperature 1.0 接受率的 drafter，或每层触及更少专家的验证路径。

## 哪些没有奏效

大多数候选 flag 不受支持、噪声大或更慢：

### vLLM

| 调节项 | 结果 |
| --- | --- |
| 更短的 draft 长度（3–6） | 启动时被拒绝；要求 `num_speculative_tokens = 7`（checkpoint block size − 1）。 |
| `draft_sample_method: "greedy"` | 在 temperature 1.0 下 −11%（168.6 对约 190.4 tok/s）。 |
| `rejection_sample_method: "block"` | 190.1 对对照组的 190.3–190.5；无效果。 |
| `enable_adaptive_verification` | Inkling 2 drafter 在启动时出现断言错误。 |
| `draft_lm_head_quantization: "fp8"` | 仅支持 DeepSeek DSpark drafters。 |

我们还特意跳过了 `rejection_sample_method: "fly"` 和 `"synthetic"`，因为它们会改变输出分布，而我们想要严格无损的加速。

### SGLang

| 调节项 | 结果 |
| --- | --- |
| 更短的 draft 长度（3–6） | 启动时被拒绝；要求 `--speculative-num-draft-tokens 8`（捆绑 drafter 的 `gamma + 1`）。 |
| `SGLANG_ENABLE_NV_MEGA_RUNTIME_OPTIMIZATION=1` | 一次 +4%，在全新对照下未能复现。 |
| `SGLANG_OPT_USE_FUSED_DRAFT_SAMPLE=1` | +2%，在运行间噪声范围内。 |
| `SGLANG_OPT_MOE_QUANT_ONCE=1` | +1%，在运行间噪声范围内。 |
| `SGLANG_DSPARK_USE_GREEDY_DRAFT=1` | 在 temperature 1.0 下 −9%（156.8 对约 172 tok/s）。 |

## 基准测试的坑

过程中有几个测量问题让我们踩了坑：

- **计时 prefill 期间的 Triton JIT。** vLLM 的第一次 4K prefill 返回 202 tok/s，而不是 20K，因为 Triton 在计时请求期间编译内核。跨提示长度和并发运行一次不计入测量的预热修复了 4K prefill，不过每个 Job 中的第一次运行仍会低报 32K prefill，原因是最后一个 chunk 的形状差异（已在台账中标记）。
- **占用 GPU 内存的孤儿服务器。** 初始驱动通过从 `setsid … &` 保存的 PID 停止服务器，但该 PID 不保证与进程组 ID 匹配。前一个服务器仍在 8000 端口存活，破坏了下一次启动，并变成仍能通过 `kill -0` 的僵尸进程。使用 `subprocess.Popen(start_new_session=True)` 管理进程，并等待 GPU 内存和 8000 端口都空闲，解决了该问题。
- **vLLM 日志中隐藏的 OOM 错误。** vLLM + DSpark 两次在日志末尾以 `"Engine core initialization failed"` 崩溃，而真正原因在往上 200 行处。首先，默认 1M token 的 KV cache 需要 52.6 GiB，而在 drafter 旁边只有 48.1 GiB 空闲（`--max-model-len 262144` 解决了这个问题）。接着，由于 vLLM v0.34.0 将默认 `--gpu-memory-utilization` 从 `0.92` 提高到 `1.0`，KV cache 占用了剩余 VRAM，并使 drafter 的 5 GiB 分配发生 OOM（`--gpu-memory-utilization 0.85` 解决了这个问题）。驱动现在会打印服务器日志中的每一行错误，而不是只打印末尾。
- **引擎方差。** 在启用投机的相同运行中，vLLM 保持在 0.4% 以内，而 SGLang 波动 ±4.5%。这一波动大到足以让 `SGLANG_ENABLE_NV_MEGA_RUNTIME_OPTIMIZATION=1` 在第一次运行中看起来像 +4% 的胜利，直到重复对照排除了它。

## 验证与部署

部署前，我们固定了确切的 vLLM nightly digest（`vllm/vllm-openai@sha256:eaa63fd6…`，构建 `0.34.0rc1.dev1235+gf2f9edcac`），并在一个 Job 内运行验收门禁：

| 门禁 | 结果 |
| --- | --- |
| 约 50% 上下文（126,537 token）下的 needle 检索 | 3/3，TTFT 12.5 s |
| 约 95% 上下文（249,970 token）下的 needle 检索 | 3/3，TTFT 28.7 s |
| 并发浸泡（4 × 约 58K token 请求） | 4/4 成功，每个 3/3 检索 |
| 贪心等价性，DSpark 对比无投机（6 个提示，temp 0） | 6/6 逐字节相同 |
| 固定镜像上的单用户解码 | 189.9 / 190.2 tok/s |

这些通过后，我们用一个 `hf endpoints deploy` 命令部署了 endpoint，同时固定镜像 digest 和模型 revision（认证访问，空闲 60 分钟后缩容到零）：

```
hf endpoints deploy inkling2mini-tuned-dspark --namespace <your-org> \
  --repo thinkingmachines/Inkling-2-Mini --revision 7a67ae2314b44ef05c87fd1d4d311c58aaeb18f6 \
  --framework custom --custom-image "vllm/vllm-openai@sha256:eaa63fd6ee3aac77f3158e80ed79ec425db3a53f7cd666bf1954e96abfaf19a7" \
  --health-route /health --port 8000 \
  --vendor aws --region us-east-2 --accelerator gpu --instance-type nvidia-rtx-pro-6000 --instance-size x1 \
  --min-replica 0 --max-replica 1 --scale-to-zero-timeout 60 --type authenticated \
  --container-command "vllm serve" \
  --container-args "/repository --served-model-name thinkingmachines/Inkling-2-Mini --host 0.0.0.0 --port 8000 --tool-call-parser inkling --enable-auto-tool-choice --reasoning-parser inkling --max-model-len 262144 --gpu-memory-utilization 0.85 --speculative-config '{\"method\":\"dspark\",\"num_speculative_tokens\":7,\"draft_sample_method\":\"probabilistic\"}'"
```

对在线 endpoint 运行 `bench.py` 得到单用户 194.9 tok/s，在计入网络延迟后与 Job 运行一致。

本次运行的所有内容（`PLAN.md`、`THEORY.md`、`jobs/driver.py`、`submit.sh`、`deploy.sh` 以及原始 `ledger-*.jsonl` 文件）都在 [`NielsRogge/inkling-2-mini-hillclimb`](https://github.com/NielsRogge/inkling-2-mini-hillclimb) 中。要在另一个模型上复用该循环，请将候选与对照服务器命令放入 `configs/plan-*.json` 文件，并提交到与目标 endpoint 匹配的任意 HF Jobs GPU flavor。

博客中的更多文章

guidevllminference

## 用一条命令在 HF Jobs 上运行 vLLM 服务器

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/1677431596830-631ce4b244503b72277fc89f.jpeg)

14

June 26, 2026

transformersmistralvllm

## 欢迎 Le Chonk：Hugging Face 上的 Mistral Large 4

- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6141a88b3a0ec78603c9e784/DJsxSmWV39M33JFheLobC.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/60f0608166e5701b80ed3f02/H9LNnlf0W4fiOJhQMxnbW.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/6123945a0ed258ebc83f3d56/8wMHFQHEV24G_ljl4kPxQ.jpeg)
- ![](https://cdn-avatars.huggingface.co/v1/production/uploads/649a943906690b959319d192/k8ZlmJWF3GNpYLHrdpejY.jpeg)
- +7

93

October 29, 2026

### 社区
