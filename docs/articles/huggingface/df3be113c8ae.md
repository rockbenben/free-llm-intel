---
vendor: huggingface
title: 在单台 RTX PRO 6000 上爬山调优 Inkling 2 Mini 推理
original_title: 
url: https://huggingface.co/blog/inkling-2-mini-inference-hillclimb
date: 2026-11-25
lang: zh
captured: 2026-11-26
extractor: readability-v1
translator: agent
status: translated
body_sha: 729868c1c303
---

# 在单台 RTX PRO 6000 上爬山调优 Inkling 2 Mini 推理

[![Niels Rogge's avatar](https://cdn-avatars.huggingface.co/v1/production/uploads/1608042047613-5f1158120c833276f61f1a84.jpeg)](https://huggingface.co/nielsr)

Niels Rogge

nielsr

[Inkling 2 Mini](https://huggingface.co/blog/inkling2mini) 上周发布，为本地 AI 和更小的开源模型树立了新的 SOTA。它总参数约 26B（每 token 激活 3B），支持多模态输入，上下文窗口达 1M token，在 [Artificial Analysis Intelligence Index v5](https://artificialanalysis.ai/models/open-source) 上领先同重量级，并在 48 项基准中的 32 项上胜过 Gemma 4 31B、Qwen3.8-27B 等模型，因此对于在普通硬件上做编码、工具调用和推理来说，它是一个很强的开放选项。我们写了一篇详尽的博客文章，介绍如何在 Hugging Face 生态中使用它，见[此处](https://huggingface.co/blog/inkling2mini)。

Inkling 2 Mini 有一个有意思的地方，或许能解释它出色的表现：它采用了不寻常的架构。Inkling 2 Mini 是一个循环式的 [Mixture-of-Experts (MoE)](https://huggingface.co/blog/moe) 模型，有 24 个物理层，其中中间 12 层会运行三次，因此每个 token 都要经过 48 层。它的 checkpoint 以 NVFP4 与 MXFP8 混合格式发布，并内置一个用于投机解码的 DSpark drafter。LLM 推理的两个常用框架 vLLM 和 SGLang 都在 nightly 构建中支持它，不过已发布的服务配置针对的是 NVIDIA B200 和 GB300 GPU（`sm100`），遗漏了 NVIDIA RTX PRO 6000 这类 `sm120` 显卡——在后者上内核兼容性可能不同。

我们想知道，在单张 NVIDIA RTX PRO 6000 96 GB 上（也就是 `nvidia-rtx-pro-6000` [Inference Endpoint](https://huggingface.co/docs/inference-endpoints) 所用的那块 GPU），它最快能跑到多快。我们没有手工逐个调参数，而是把一个 [`inference-optimisation`](https://github.com/sybil-solutions/inference-optimisation-skill) skill、`hf` CLI 以及对 [Hugging Face Jobs](https://huggingface.co/docs/hub/jobs-overview) 的访问权限交给一个 coding agent，让它跑了一个下午的实验。

在 46 次有效的基准测试中，单用户解码从 **136 tok/s 提升到 190.6 tok/s（+40%）**（超过同一 GPU 上 [LocalMaxxing 社区 SGLang + DSpark 的 167.7 tok/s 基准成绩](https://www.localmaxxing.com/en/inference-benchmarks/cmwqfbexc089gmi01hd6hiqhn)），使用 vLLM nightly 配合 DSpark 投机解码时，8 用户聚合吞吐从 **约 570 tok/s 提升到 716 tok/s（+26%）**。无论是否启用投机，贪婪解码的输出都逐字节相同；长上下文大海捞针检索在最高 250K token 时 3/3 通过；最终胜出的配置现在正以 Inference Endpoint 的形式、基于固定的镜像 digest 运行。所有日志、脚本和原始测量数据都在 [`NielsRogge/inkling-2-mini-hillclimb`](https://github.com/NielsRogge/inkling-2-mini-hillclimb) 中。

## 环境搭建

`inference-optimisation` skill 给 agent 提供一套固定的实验协议，以及一个小巧、与引擎无关的基准脚本（[`bench.py`](https://github.com/sybil-solutions/inference-optimisation-skill/blob/main/skills/inference-optimisation/scripts/bench.py)）：

- 在调优之前测量硬件，并估算理论上的性能上限。
- 一次只改一个变量，把每个候选项夹在两次对照运行之间（`control → candidate → control`）。只有当某项改动胜过两次对照、且其他指标没有退化时才保留它。
- 把每次运行都记录到 `PLAN.md`，包括退步和死胡同。
- 在宣布胜出方案之前，先通过长上下文、并发和贪婪等价性检查。

`bench.py` 测量单用户解码、并发度为 N 时的聚合解码、若干长度下的冷 prefill，以及 TTFT，其中的 token 数直接取自服务器的 usage 响应。所有运行都使用固定的六条 prompt 面板（一段代码、一段解释、一个故事、一个对比表格、一个 bash 脚本和一段历史综述），temperature 为 1.0（模型默认值），开启 thinking，输出 512 个 token；只要启用了投机解码，就重复 12 次。

这个 skill 原本是为本地 GPU 写的，所以我们把它适配到了 Hugging Face 的基础设施上：

- 计算用 **HF Jobs**。`rtx-pro-6000` 这个 Job 规格用的是与 `nvidia-rtx-pro-6000` Inference Endpoint 相同的 GPU（两者都是 $2.75/小时），因此 Job 上的数字可以直接迁移。一个约 150 行的驱动脚本（`jobs/driver.py`）接收一组服务器配置，逐个启动、跑一次不计入测量的预热、原样调用 `bench.py`、关闭服务器，并为每次运行打印一行台账记录。由于 Job 跑在不同的机器上，agent 可以并行扫 SGLang（`lmsysorg/sglang:inkling-2-mini`）和 vLLM nightly（`vllm/vllm-openai:nightly`）。
- **用 CPU Jobs 读引擎源码。** 遇到没有文档的参数时，agent 会起一个便宜的 `cpu-upgrade` Job，在容器里 grep 已安装的 Python 包。SGLang 的 `SGLANG_OPT_*` 环境变量和 vLLM 的 `speculative-config` 字段就是这么找到的。
- 部署用 **Inference Endpoints**，通过 `hf endpoints deploy` 创建，使用通过验证的那个确切镜像 digest 和参数。

基线是我们组织现有的 endpoint 配置：SGLang 加 `--attention-backend fa4`，不启用投机解码。

## 结果

[![Inkling 2 Mini 在单台 RTX PRO 6000 上四种配置的单用户解码速度](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/inkling-2-mini-inference-hillclimb/results.png)](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/blog/inkling-2-mini-inference-hillclimb/results.png)

*单用户解码速度（12 次请求的中位数）。按其测得的接受率，vLLM + DSpark 达到内存带宽上限的约 95%。*

| 配置（1× RTX PRO 6000） | 单用户解码（tok/s） | 8 用户聚合（tok/s） | Prefill 4K / 32K（tok/s） | TTFT |
| --- | --- | --- | --- | --- |
| SGLang，无投机（基线） | 134–139 | 543–598 | 18.7–19.1K / 16.9–19.1K | 41–114 ms |
| vLLM，无投机 | 157.0 | 638 | 20.7K / 20.7K | 33 ms |
| SGLang + DSpark（8 个 draft） | 166.6 | — ¹ | 18.0–19.5K / 18.9–19.1K | 38–51 ms |
| **vLLM + DSpark（7 个 draft）** | **190.6** | **716** | 20.7K / 20.6K | 40 ms |
| 已部署的 endpoint（经互联网访问） | 194.9 | 673 | 11.7K / 19.2K ² | 198 ms ² |

¹ SGLang 的 RTX PRO 6000 DSpark 配方把 `--max-running-requests` 上限设为 4。把它提到 8 可以到 660 tok/s，仍然落后于 vLLM。² 包含约 160 ms 的客户端到 endpoint 网络往返。

全部提速来自三件事：换到 vLLM nightly（相比无投机的 SGLang 提升 15%，136 → 157 tok/s）；启用带 7 个 draft 和概率式 draft 采样的 DSpark（在此基础上再提升 21%，四次运行 157 → 190.6 tok/s，分别为 189.3、190.4、191.1 和 190.7）；以及加上两个显存参数，让 vLLM 的 DSpark 配置能在 96 GB 上真正启动：

```
vllm serve thinkingmachines/Inkling-2-Mini \
  --tool-call-parser inkling \
  --enable-auto-tool-choice \
  --reasoning-parser inkling \
  --max-model-len 262144 \
  --gpu-memory-utilization 0.85 \
  --speculative-config '{"method":"dspark","num_speculative_tokens":7,"draft_sample_method":"probabilistic"}'
```

`num_speculative_tokens: 7` 和 `draft_sample_method: "probabilistic"` 都经过了直接验证：更短的 draft 数（比如 5）会在启动时被拒绝，因为两个引擎都会强制 checkpoint 的固定 block size；而改用 `greedy` draft 采样会让 vLLM 在 temperature 1.0 下的解码速度下降 11%（见[哪些没奏效](https://huggingface.co/blog/inkling-2-mini-inference-hillclimb#what-didnt-work)）。

### 为什么它停在 190 tok/s 左右

调优之前，agent 在 Job 里探测了这块 RTX PRO 6000（**1,469 GB/s** 拷贝带宽、**416 TFLOPS** BF16、**792 TFLOPS** FP8），并从 safetensors 头部读出了各张量的大小。由于每个 token 都要访问 48 层，朴素解码会重复读取约 2.7 GB 的注意力与稠密权重、约 2 GB 的 routed experts（每层 128 个里取 8 个），以及约 0.9 GB 的 LM head。按 1,469 GB/s 计算，单用户的带宽上限是**约 256 tok/s**。不启用投机时，157 tok/s 的 vLLM 达到了该上限的 61%，主要受限于 48 层访问带来的内核启动延迟。

投机解码改变了 MoE 上的显存算术。一次验证 8 个位置，会激活它们 routed experts 的并集，使得每层 expert 的读取量约为 40%，而不是 6%。在 temperature 1.0 下，我们实测的接受率约为每步 2.3 个 token（每个位置的接受率从第一个 draft 的 0.6 降到 0.33 和 0.19），此时带宽上限降到**约 201 tok/s**。190.6 tok/s 的 vLLM + DSpark 已经达到**硬件带宽的约 95%**，继续调参数几乎没有空间了。要突破 190 tok/s，需要一个在 temperature 1.0 下接受率更高的 drafter，或者一条每层触及 expert 更少的验证路径。

## 哪些没奏效

大多数候选参数要么不被支持，要么噪声太大，要么更慢：

### vLLM

| 手段 | 结果 |
| --- | --- |
| 更短的 draft 长度（3–6） | 启动时被拒绝；要求 `num_speculative_tokens = 7`（checkpoint block size − 1）。 |
| `draft_sample_method: "greedy"` | temperature 1.0 下 −11%（168.6 对约 190.4 tok/s）。 |
| `rejection_sample_method: "block"` | 190.1，对照组为 190.3–190.5；没有影响。 |
| `enable_adaptive_verification` | Inkling 2 的 drafter 在启动时触发断言错误。 |
| `draft_lm_head_quantization: "fp8"` | 仅支持 DeepSeek 的 DSpark drafter。 |

我们还有意跳过了 `rejection_sample_method: "fly"` 和 `"synthetic"`，因为它们会改变输出分布，而我们要的是严格无损的提速。

### SGLang

| 手段 | 结果 |
| --- | --- |
| 更短的 draft 长度（3–6） | 启动时被拒绝；要求 `--speculative-num-draft-tokens 8`（对内置 drafter 来说是 `gamma + 1`）。 |
| `SGLANG_ENABLE_NV_MEGA_RUNTIME_OPTIMIZATION=1` | 一次 +4%，但在新的对照组上无法复现。 |
| `SGLANG_OPT_USE_FUSED_DRAFT_SAMPLE=1` | +2%，在运行间噪声范围内。 |
| `SGLANG_OPT_MOE_QUANT_ONCE=1` | +1%，在运行间噪声范围内。 |
| `SGLANG_DSPARK_USE_GREEDY_DRAFT=1` | temperature 1.0 下 −9%（156.8 对约 172 tok/s）。 |

## 基准测试的坑

过程中有几个测量问题坑了我们：

- **计时 prefill 期间发生 Triton JIT。** vLLM 第一次 4K prefill 返回的是 202 tok/s，而不是 20K，因为 Triton 在被计时的那个请求期间还在编译内核。跨 prompt 长度与并发度跑一次不计入测量的预热之后，4K prefill 的问题解决了；不过每个 Job 的首次运行仍会低报 32K prefill，原因是最后一个 chunk 的形状不同（已在台账中标注）。
- **遗留的服务器占着显存。** 最初的驱动脚本通过 `setsid … &` 保存的 PID 去停服务器，而这个 PID 并不保证等于进程组 ID。上一个服务器一直在 8000 端口上活着，破坏了下一次启动，还变成了仍能通过 `kill -0` 检查的僵尸进程。改用 `subprocess.Popen(start_new_session=True)` 管理进程，并等到显存和 8000 端口都释放后再继续，问题就解决了。
- **vLLM 日志里被藏起来的 OOM 报错。** vLLM + DSpark 有两次在日志末尾以 `"Engine core initialization failed"` 死掉，而真正的原因躺在往上 200 行的位置。第一次，默认的 1M token KV cache 需要 52.6 GiB，而和 drafter 并存时只空着 48.1 GiB（用 `--max-model-len 262144` 解决）。第二次，由于 vLLM v0.34.0 把默认的 `--gpu-memory-utilization` 从 `0.92` 提高到 `1.0`，KV cache 占用了剩余显存，导致 drafter 那 5 GiB 的分配 OOM（用 `--gpu-memory-utilization 0.85` 解决）。现在驱动脚本会打印服务器日志里的每一行错误，而不只是末尾几行。
- **引擎波动。** 在启用投机的相同运行之间，vLLM 的波动保持在 0.4% 以内，而 SGLang 摆动了 ±4.5%。这个幅度足以让 `SGLANG_ENABLE_NV_MEGA_RUNTIME_OPTIMIZATION=1` 在第一次运行时看起来像是 +4% 的收益，后来被重复对照排除了。

## 验证与部署

部署之前，我们锁定了确切的 vLLM nightly digest（`vllm/vllm-openai@sha256:eaa63fd6…`，构建号 `0.34.0rc1.dev1235+gf2f9edcac`），并在一个 Job 里跑了验收门禁：

| 检查项 | 结果 |
| --- | --- |
| 约 50% 上下文处的 needle 检索（126,537 token） | 3/3，TTFT 12.5 s |
| 约 95% 上下文处的 needle 检索（249,970 token） | 3/3，TTFT 28.7 s |
| 并发浸泡（4 个约 58K token 的请求） | 4/4 成功，每个 3/3 检索命中 |
| 贪婪等价性：DSpark 与不启用投机（6 条 prompt，temp 0） | 6/6 逐字节相同 |
| 固定镜像上的单用户解码 | 189.9 / 190.2 tok/s |

这些通过之后，我们用一条 `hf endpoints deploy` 命令部署了 endpoint，同时固定镜像 digest 和模型 revision（认证访问，空闲 60 分钟后缩容到零）：

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

对线上 endpoint 运行 `bench.py` 得到单用户 194.9 tok/s，计入网络延迟后与 Job 中的结果一致。

这次运行的全部内容（`PLAN.md`、`THEORY.md`、`jobs/driver.py`、`submit.sh`、`deploy.sh`，以及原始的 `ledger-*.jsonl` 文件）都在 [`NielsRogge/inkling-2-mini-hillclimb`](https://github.com/NielsRogge/inkling-2-mini-hillclimb) 中。想在另一个模型上复用这套循环，就把你的候选与对照服务器命令写进一个 `configs/plan-*.json` 文件，然后提交到与目标 endpoint 匹配的任意 HF Jobs GPU 规格上。
