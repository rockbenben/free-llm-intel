---
vendor: anyscale
title: 用 Ray 做大规模并行 agent 模拟
original_title: 
url: https://anyscale.com/blog/massively-parallel-agentic-simulations-with-ray
date: 2025-09-10
lang: zh
captured: 2026-11-05
extractor: readability-v1
translator: agent
status: translated
body_sha: ef7a8361c5f4
---

# 用 Ray 做大规模并行 agent 模拟

作者：[Philipp Moritz](https://www.anyscale.com/blog?author=philipp-moritz)、[Sumanth Hegde](https://www.anyscale.com/blog?author=sumanth-hegde)、[Tyler Griggs](https://www.anyscale.com/blog?author=tyler-griggs) 和 [Eric Tang](https://www.anyscale.com/blog?author=eric-tang) | 2025 年 9 月 10 日

![用 Ray 做大规模并行 agent 模拟（题图）](https://images.ctfassets.net/xjan103pcp94/7JUCwEieiRvbaHqx1VYRIu/ca861e91b802a5ba8e2919144885bc8f/Screenshot_2025-09-10_at_10.42.26â__AM.png?w=1200)

在自己的笔记本上跑单个 agent、对接一个托管的 model endpoint（比如 ChatGPT、Claude、Gemini，或者某家开源模型的服务商）很容易，但在一个集群上并行跑上万个 agent 则是一大挑战。而对许多少见却非常有用的 LLM 与 agentic 用例来说，它同时也是一项重要前提，包括：

- **跑评测：** agentic 评测处在 agentic 应用开发的内循环里。无论是想造出更好的 LLM、给 LLM 写出更好的 prompt，还是改进 agent loop 本身，它都至关重要。
- **迭代数据集：** 构建 agent 取决于「问题描述数据集」和「验证解法的技术」。agentic 模拟让我们能在这些数据集上迭代、筛选并改进它们，还能收集解答轨迹用于监督微调。
- **跑 RL 训练：** agentic 模拟是 RL 训练循环中必不可少的一环，用来收集轨迹与奖励，再用 RL 据这些更新策略。

当你从在笔记本上跑单个 agent，扩展到并行跑大量 agent 时，大概率会撞上下面这些挑战：

- **隔离 agent：** agent 需要被隔离，让它们互不干扰、也不干扰系统的其余部分，并且待在合理的资源限制之内。此外，agent 需要运行在一个定义清楚的环境里，比如容器。
- **扩展模型推理与工具使用：** 并行跑大量 agent 时，模型服务商的 rate limit 通常不够用，所以你得想清楚怎么扩展推理。你可能还会用到 MCP server 这类常见工具，它们也得跟着 agent 一起扩上去。
- **使用自定义模型：** 如果你在构建定制化的 agent，很可能你自己也训练或微调了模型，而这些模型还需要被部署起来。

大多数这类方案都要写大量样板代码、搭复杂的基础设施。

Ray 直接回应了这些挑战：它让你用一个简单、Pythonic 的 API 就能跑大规模并行的 agentic 模拟。它能处理 CPU 与 GPU（或其他加速器）混合的负载，也支持像推理服务器（例如 vLLM 或 SGLang）这样的有状态服务。这样一来，推理就能和模拟跑在同一个集群上，既能对模型与 agent 做快速的联合实验，也能联合扩缩以避免撞上模型的 rate limit。Ray 顺手的 Pythonic 开发体验让实验配置的迭代变得容易，也能平滑扩展到非常大的运行规模。此外，Ray 的容错能力让你可以用 spot 实例来节省成本。

读这篇博客你会学到：

- 你会学到如何用灵活的隔离方式运行大量沙箱环境，让沙箱能跑在任何环境里（无特权环境、容器套容器），而不必再单独搭一套沙箱环境。
- 你会学到如何让推理与 agent 执行都跑在同一个 Ray 集群上，从而在不撞 rate limit 的前提下同时快速迭代 agent 与 LLM 的设置，也让并行 agent 的数量更容易往上扩。
- 你会看到上文三种用例（跑评测、迭代数据集、跑 RL 训练）的具体例子，以及许多让它们更高效、更好迭代的技巧。

我们将在软件工程的场景下演示这些要点。为此，我们还开源了一个新数据集，其中包含从 [cpython 仓库](https://github.com/python/cpython)抓取来的 5500 个测试用例，并展示如何并行地评测它们。我们演示的技术是通用的，同样适用于其他领域，包括通用的计算机操作、数据工程或科学研究。

## 隔离并行的 agentic 模拟

做大量并行 agentic 模拟时，一个核心问题是如何把它们彼此隔离、并与系统环境隔离。可选项有几种：

- **用带完整文件系统隔离的容器：** Docker 是许多软件工程师都熟悉的标准，容器很适合在非对抗性场景里隔离负载，这也让 docker 成了跑 agent 的一种非常流行的方式。但用 docker 也有一些缺点：容器镜像的构建、推送、拉取和存储都可能代价高昂，rate limit 也让人烦躁。此外，在超级计算机这类无特权环境里、或在另一个容器内部运行容器都会比较棘手。其中一些问题可以通过换用别的容器运行时（如 podman 或 apptainer）来解决（下面我们会演示怎么做）。
- **用配合 cgroups 与 chroot 的进程：** 一种更轻量的跑 agent 的方式是用进程，靠 Linux cgroups 和 chroot 来隔离。容器底层其实也是这么实现的，但直接使用这些原语能让你更多地掌控隔离是如何发生的。例如在这种设定下，主机上大部分文件系统和包都能复用，于是不必推拉容器镜像也能跑 agent，同时仍然有不错的隔离效果。虽然从零实现这套东西非常复杂，但像 [bubblewrap](https://github.com/containers/bubblewrap) 这样好用的命令行工具能让它变得简单（同样，下面我们会演示）。
- **用虚拟机或远程执行：** 有些场景需要更重的隔离机制。例如你可能想在 mac 上跑一个 linux 应用，或者在 ARM 上跑一个 x86_64 应用，这种情况下你就需要 VM。少数情况下，你需要比容器或 cgroups 所能提供的更强的隔离，这时 VM 或 micro VM 会是个好选择。又或者你想用一个独立的 K8s 集群来执行 agent，或者使用另一家云服务商。与一些更简单的隔离方法相比，这些选项通常需要在基础设施层面做更多工作，比如额外的错误处理和通信机制。

容器是最常见、适用范围也最广的隔离机制，而且与生态集成得很好，所以很多情况下应当是首选。带 bubblewrap 这类额外机制的进程隔离，用来做隔离大概还被低估着：它们极其轻量、迭代起来非常容易，还可以和包管理器（如 uv、Linux 发行版自带的包管理器）或 [NixOS](https://nixos.org/)、[Guix](https://guix.gnu.org/) 这类技术组合，灵活地定义 agent 运行于其中的环境。为了让每种情形都能用上最合适的隔离原语，我们的方案在环境支持上应当保持灵活。

## agentic 模拟的 agent scaffold

agent scaffold 实现的是 LLM 外围的那层结构，让它能在某个特定领域——在我们这里是软件工程——有效地解决问题。scaffold 由以下部分组成：

- 给 LLM 的 prompt，通常是带占位符的模板，比如占位符是一个 github issue 的描述，或是在给定软件仓库里该如何行事的具体指令，
- LLM 在解题时可用的 tools，比如 shell 命令、文件编辑工具、一个 python 解释器、用来收集问题与解法更多信息的搜索工具，以及任何其他以 MCP server 形式提供的工具，
- agent loop，它反复调用 LLM 并执行 LLM 给出的动作；它也可能与用户交互式确认，让用户能修改 LLM 提出的行动方案。

虽然本文聚焦软件工程，但这套结构非常通用，同样适用于任意计算机操作，或数据科学负载、科学研究这类更专门的领域。

一些 scaffold 支持对 LLM 的动作做各种形式的沙箱。一些 scaffold 是为终端用户解决具体问题设计的，一些则为跑大规模实验做了优化（例如用于评测或 RL 训练）。这些用例虽然需要不同的解法，但理想情况下它们共享同样的 prompt 和 tool call，这样在实验数据集上做的任何实验都能直接代表真实用户体验。以下是我们所知的面向软件工程的 agentic scaffold 清单：

- 通常由终端用户使用、多为交互式的 scaffold 包括 [Claude Code](https://github.com/anthropics/claude-code)、[Gemini CLI](https://github.com/google-gemini/gemini-cli)、[Qwen Code](https://github.com/QwenLM/qwen-code) 和 [Aider](https://github.com/Aider-AI/aider)。它们一次只支持一个会话，通常也不提供沙箱，但可以和实际的工作负载环境一起放在容器里运行。其中一些也可以加以改造，用于评测或 RL 场景。
- [OpenHands](https://github.com/All-Hands-AI/OpenHands) 是一个流行的功能完整的 agent 运行时，既可以为终端用户所用，也可以用于评测与 RL 场景（它自带一个评测 harness）。OpenHands 主要以 docker 为基础，另有一个基于远程 k8s 的运行时[可用](https://novasky-ai.notion.site/skyrl-v0)。它对 MCP server、浏览器、自定义工具等各种工具有非常通用的支持。
- [SWE-agent](https://github.com/SWE-agent/SWE-agent) 是 SWE-bench 的作者们做的一个 agent，可以用来解决软件工程问题。它还有一个极简版本 [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent)，在隔离方面最灵活，代码也非常简单、好改，因此很容易适配各种各样的负载。它只用 bash 命令，在软件工程任务上就表现得不错。
- [Terminal-bench](https://github.com/laude-institute/terminal-bench) 是一个针对终端使用类任务的 agent 基准，附带一个可用来适配其他基准（包括 SWE-Bench）的评测 harness，以及一个名为 Terminus 的内置 agent scaffold。所有任务都打包成 Docker 镜像，harness 会为每个任务启动一个容器化环境。
- [R2E-Gym](https://github.com/R2E-Gym/R2E-Gym) 为环境提供类 gym 的接口，并在外面包了一层 agent wrapper，但它更偏向为模拟和 RL 负载做优化。它支持文件编辑器、bash 和文件搜索等工具。
- [Smolagents](https://github.com/huggingface/smolagents?tab=readme-ov-file) 是 huggingface 的一个库，同样主打极简，但还有更多集成、对不同 tool call 的支持，以及通过 Docker 或 E2B 在沙箱环境中执行的支持。

在这篇博客里我们采用了 mini-swe-agent，因为它极其简单、好改，并且在没有额外复杂度的情况下也能在软件工程问题上给出不错的表现；但下面演示的同样思路也适用于其他 scaffold。

## cpython issues 数据集

本文使用一个非常简单的数据集，它由 [cpython](https://github.com/python/cpython) 仓库生成。同样的方法可以为许多不同的仓库生成数据集。格式是一个简化版的 swebench 格式，为「跑完整测试套件来做验证」做了优化。我们从仓库里抓取了约 5500 个 issue，找到与之对应的 PR，并抽取出 `base_commit`（即 PR 的父提交）以及 merge_commit（即包含该 PR 代码的那个提交）。数据集在[这里](https://huggingface.co/datasets/pcmoritz/cpython_dataset)，用来抓取数据集的代码在[这里](https://gist.github.com/pcmoritz/fa911ee735a5a8f5329ea7a7c8adc47d)。

![用 Ray 做大规模并行 agent 模拟 图 1](https://images.ctfassets.net/xjan103pcp94/1UmeTbGXQTiMaAhWXTyNPO/91d3b6aee67d7c308b1c5c255ed99a3c/Screenshot_2025-09-09_at_3.58.33â__PM.png)

用 Ray 做大规模并行 agent 模拟 图 1

给定 LLM 生成的一个 patch，可以按下面这样验证：

- 把 [cpython](https://github.com/python/cpython) 仓库检出到 `base_commit`
- 应用 LLM 生成的 patch，但 `Lib/test/*` 里的改动除外（既是为了避免下一步产生冲突，也是为了避免 LLM 删除或「修好」测试）
- 应用原始 PR diff `base_commit..merge_commit` 中 `Lib/test/*` 的改动（这些就是该 PR 新增的回归测试）
- 然后通过 `./configure && make test` 跑完整测试套件。实践中，为了让它稳定可用，我们不得不排除一些经常失败的测试。好在 cpython 有一个叫 `EXTRATESTOPTS` 的环境变量，允许往测试套件传额外参数。我们就是用这个机制通过 `--ignore` 旗标来排除失败测试的。

下一节我们会展示如何用 Ray 把 patch 的生成和验证都并行化。

## 使用 mini-swe-agent

本文余下的部分我们使用 [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) 作为 AI agent，因为它非常精简、容易修改，并且支持把 agent 动作执行在多种沙箱环境里。也正因为简单，它很容易被研究并改造到软件工程之外的不同问题域。`mini-swe-agent` 有一个让很多事情都变容易的设计决策：agent 的每个动作就是一条简单的 `bash` 命令，不需要[持久的 shell 会话](https://mini-swe-agent.com/latest/faq/#why-no-shell-session)。此外，`mini-swe-agents` 支持多种不同的隔离[环境](https://github.com/SWE-agent/mini-swe-agent/tree/main/src/minisweagent/environments)：

- 本地执行，即每条命令就在一个 `bash` 命令里执行，没有任何特殊隔离。在「命令不经用户确认就执行」的设定下不推荐这么用，但它可以用于本地交互式使用——每条命令在执行前由用户检查一遍。
- 在容器环境里执行，可以通过 [docker](https://www.docker.com/)、[podman](https://podman.io/) 或 [apptainer](https://apptainer.org/)。如果我们想用容器做隔离，通常会选 podman，因为它不需要 daemon，而且可以配置成在各种环境里运行（包括容器内部以及无特权环境）。在超级计算机上运行时，apptainer 会是个不错的选择。
- 在由 [bubblewrap](https://github.com/containers/bubblewrap) 隔离的进程里执行，这样就能在隔离环境中运行，又没有设置和维护容器镜像的开销。它通过[这个环境](https://github.com/SWE-agent/mini-swe-agent/blob/main/src/minisweagent/environments/extra/bubblewrap.py)得到支持。例如下面我们会用它来跑 cpython 环境；再配合一个[启动命令](https://github.com/SWE-agent/mini-swe-agent/pull/490)，它就能用来搭建更复杂的环境，比如为处理 Python 代码库的 agent 准备带 uv 的 Python 虚拟环境。

要在 podman 下运行 `mini-swe-agent`，你可以这样安装 podman：

```
1sudo apt-get -y install podman
2
3# The following is required if you want to run podman inside of a container
4sudo cp /usr/share/containers/containers.conf /etc/containers/containers.conf && sudo sed -i 's/^#cgroup_manager = "systemd"/cgroup_manager = "cgroupfs"/' /etc/containers/containers.conf && sudo sed -i 's/^#events_logger = "journald"/events_logger = "file"/' /etc/containers/containers.conf
5sudo apt-get install containers-storage
6sudo cp /usr/share/containers/storage.conf /etc/containers/storage.conf
7sudo sed -i 's/^#ignore_chown_errors = "false"/ignore_chown_errors = "true"/' /etc/containers/storage.conf
8# Depending on your execution environment (e.g. if some privileges are missing or if you need access to e.g. GPUs), you might also want to add some of the options from https://github.com/containers/podman/issues/20453#issuecomment-1912725982
```

然后在一个检出了 [https://github.com/SWE-agent/mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) 的目录里，你可以运行

```
1uv run --extra full mini-extra swebench --model openai/gpt-5-nano --subset verified --split test --workers 128 --output <output directory>
```

要顺利跑通这个特定基准，你应该在 `swebench.yaml` 里设置下面这些参数：在 `environment` 下加上 `executable: "podman"`，以及 `timeout: 3600` 和 `pull_timeout: 1200`。

对于这类需要拉取大量容器镜像的负载，还建议使用带本地 NVMe 磁盘的机器。如果你在 AWS 上的 Anyscale 运行，这些磁盘会被自动[配置](https://docs.anyscale.com/configuration/compute/aws#nvme-configuration)成 RAID 阵列以获得最佳性能。

## 用 Ray 运行并行的 SWE 模拟

本节展示如何用 Ray 和 [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) 运行大量并行模拟。我们会聚焦 SWE-bench 风格、跑在上面介绍的 `cpython` issues 数据集上的软件工程任务，但这些思路可以广泛适用于许多不同的模拟环境。

### 从 agent 生成数据

本节给出一个简单却有效的代码示例，用于从 agent 生成 rollout 数据。我们用一个名为 `Engine` 的 actor，在集群里每个节点起一个 `vllm` 或 `sglang` 服务器，然后用 Ray 任务 `generate_rollout`——每个问题描述一个任务——并行地对它跑大量模拟。每个任务都使用来自 [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) 的 `swebench-single` 脚本来执行 rollout。这样的设定让推理这一侧保持简单，因为我们直接可以用 vllm 和 `sglang` 的 CLI 来启动推理引擎。另一种做法是用 [Ray Serve LLM](https://docs.ray.io/en/latest/serve/llm/index.html) 中心化地部署 llm engine，把模型暴露成一个所有 agent 都连过去的全局 endpoint；或者用 `sglang` 配 [sglang router](https://docs.sglang.ai/advanced_features/router.html)。

```
1import requests
2import subprocess
3from pathlib import Path
4
5from datasets import load_dataset
6import ray
7
8ENGINE_ADDRESS = "http://127.0.0.1:8000"
9
10@ray.remote(num_gpus=8)
11class Engine:
12
13    def __init__(self, model: str):
14        self.model = model
15        self.engine_process = subprocess.Popen(
16            ["/usr/local/bin/uv", "run", "--with", "vllm",
17             "vllm", "serve", self.model,
18             "--tensor-parallel-size", "8",
19             "--max-model-len", "64000", "--enable-expert-parallel",
20             # You can add --data-parallel-size if you want to use
21             # data parallel replicas in addition to tensor and expert parallel
22             "--enable-auto-tool-choice", "--tool-call-parser", "qwen3_coder"],
23        )
24
25        # If you want to use sglang instead, use the following code:
26        # self.engine_process = subprocess.Popen(
27        #     ["/usr/local/bin/uv", "run", "--with", "sglang[all]",
28        #      "-m", "sglang.launch_server",
29        #      "--model-path", self.model, "--tp-size", "8",
30        #      "--enable-ep-moe", "--host", "0.0.0.0", "--port", "8000"],
31        # )
32
33    def wait_for_engine(self):
34        while True:
35            try:
36                result = requests.get(ENGINE_ADDRESS + "/health", timeout=10)
37            except requests.exceptions.ConnectionError:
38                continue
39            if result.status_code == 200:
40                return
41
42@ray.remote(num_cpus=1, scheduling_strategy="SPREAD")
43def generate_rollout(model: str, dataset_name: str, instance_id: str, target_dir: str):
44    model_path = "hosted_vllm/" + model
45    target_path = Path(target_dir) / instance_id/ f"{instance_id}.traj.json"
46    result = subprocess.run(
47        ["/usr/local/bin/uv", "run", "mini-extra", "swebench-single",
48         "--model", model_path, "--subset", dataset_name,
49         "--split", "train", "--instance", instance_id,
50         "--environment-class", "bubblewrap",
51         "--output", target_path,
52        ],
53        env={
54            "HOSTED_VLLM_API_BASE": ENGINE_ADDRESS + "/v1",
55            "LITELLM_MODEL_REGISTRY_PATH": "/mnt/shared_storage/pcmoritz/model_registry.json",
56        },
57        capture_output=True,
58    )
59    return result
60
61# For this example, we use 5 nodes with 8 GPUs each
62num_shards = 5
63model = "Qwen/Qwen3-235B-A22B-Instruct-2507-FP8"
64dataset_name = "pcmoritz/cpython_dataset"
65dataset = load_dataset(dataset_name, split="train")
66
67executors = [Engine.remote(model) for i in range(num_shards)]
68ray.get([executor.wait_for_engine.remote() for executor in executors])
69
70results = []
71for record in dataset:
72    result = generate_rollout.remote(
73        model,
74        dataset_name,
75        record["instance_id"],
76        "/mnt/shared_storage/pcmoritz/rollouts"
77    )
78    results.append(result)
79
80ray.get(results)
```

在这个实验里，我们把 environment class 设成了 [bubblewrap](https://github.com/SWE-agent/mini-swe-agent/blob/main/src/minisweagent/environments/extra/bubblewrap.py)。这会确保跑在同一台机器上的所有 agent 彼此隔离、也与系统环境隔离。我们还把结果写入一个共享的 NFS 卷，以便下一步做进一步的后处理和筛选。总的来说，把轨迹文件和其他输出文件（比如日志）写到 NFS 是一种有用的模式，它还让我们能对部分运行做 checkpoint，如果生成脚本被重新执行，就能从上次中断的地方接着跑。

上面的设定里有若干参数可以调。其一是 vLLM 引擎参数，包括各种形式的并行，见 [vLLM 优化指南](https://docs.vllm.ai/en/latest/configuration/optimization.html)。最佳设置通常取决于你的硬件以及你所使用的模型架构。另一个要调的参数是每个引擎承载的 agent 数量；把 `generate_rollout` 装饰器里的 `num_cpus` 参数调大就能降低它。实践中我们发现每个引擎 64 到 128 个 agent 效果不错。每个引擎的最优 agent 数，取决于在环境里花费的时间（CPU 工作）与评测 LLM 花费的时间（GPU 工作）之比；这个比值越高，需要的 agent 就越多，这样才有足够大的 batch size 把推理引擎喂饱。

### 对数据做筛选与后处理

本节介绍如何用 Ray 对数据集做筛选与后处理，以评估轨迹的质量，例如给每条轨迹分配一个奖励。一般每个问题实例跑一个 Ray 任务就够用了。如果要用一个独立的奖励模型，可以按部署 agent LLM 的类似方式把它部署起来。在更复杂的设定下，用 [Ray Data](https://docs.ray.io/en/latest/data/data.html) 和 [Ray Data LLM](https://docs.ray.io/en/latest/data/working-with-llms.html) 来做数据准备可能更合适，因为打分和筛选属于批处理式的数据负载。

作为例子，我们会实现「cpython issues 数据集」一节描述的那个验证流程。agent 轨迹已在上一步生成并写到了 NFS 上。在这一步，针对每个问题实例，我们抽出 agent 生成的 patch，并在完整的 cpython 测试套件上测试它，其中包含人类在「修复该 issue 的 golden PR」里提交的回归测试（除非原始 agent 作弊，否则它是看不到这些测试的）。如果打过补丁的代码通过了全部测试，就得到 1 的奖励，否则奖励为 0。视具体设定而定，把验证作为 rollout 流程的一部分、或者把它单独跑，都可能更合适。在本文最后一节，我们会展示如何把 rollout 与验证两个流程都集成进一个 RL 框架。

下面是我们刚描述的验证流程的代码：

```
1import json
2from pathlib import Path
3import re
4import subprocess
5import tempfile
6
7from datasets import load_dataset
8import ray
9
10TEST_CMD = """
11./configure && prlimit --as=34359738368 make test TESTOPTS="\
12    --ignore test.test_embed.InitConfigTests.test_init_setpythonhome \
13    --ignore test.test_os.TestScandir.test_attributes \
14    --ignore test.test_pathlib.test_pathlib.PathSubclassTest.test_is_mount \
15    --ignore test.test_pathlib.test_pathlib.PathSubclassTest.test_stat \
16    --ignore test.test_pathlib.test_pathlib.PathTest.test_is_mount \
17    --ignore test.test_pathlib.test_pathlib.PathTest.test_stat \
18    --ignore test.test_pathlib.test_pathlib.PosixPathTest.test_is_mount \
19    --ignore test.test_pathlib.test_pathlib.PosixPathTest.test_stat \
20    --ignore test.test_pathlib.PathSubclassTest.test_is_mount \
21    --ignore test.test_pathlib.PathSubclassTest.test_stat \
22    --ignore test.test_pathlib.PathTest.test_is_mount \
23    --ignore test.test_pathlib.PathTest.test_stat \
24    --ignore test.test_pathlib.PosixPathTest.test_is_mount \
25    --ignore test.test_pathlib.PosixPathTest.test_stat \
26    --ignore test.test_perf_profiler.* \
27    --ignore test.test_pdb.PdbTestInline.test_quit \
28    --ignore test.test_pdb.PdbTestInline.test_quit_after_interact"
29"""
30
31def safe_subprocess_run(path: Path, command: str | list[str], **kwargs):
32    """Run the command in a subprocess with error handling."""
33    try:
34        result = subprocess.run(
35            command,
36            text=True,
37            **kwargs
38        )
39    except Exception as e:
40        with open(path / "tests.exception", "w") as f:
41            f.write(str(e))
42        return None
43    if result.returncode != 0:
44        if result.stdout:
45            with open(path / "tests.out", "w") as f:
46                f.write(result.stdout)
47        if result.stderr:
48            with open(path / "tests.err", "w") as f:
49                f.write(result.stderr)
50        return None
51    return result
52
53def run_tests(path: Path, instance: dict[str, str], trajectory: dict):
54    with tempfile.TemporaryDirectory() as working_dir:
55        # check out the repository at the base_commit
56        if not safe_subprocess_run(
57            path,
58            f"git init && git remote add origin https://github.com/{instance['repo']} && "
59            f"git fetch --depth 1 origin {instance['merge_commit']} && "
60            f"git fetch --depth 1 origin {instance['base_commit']} && git checkout FETCH_HEAD && cd ..",
61            shell=True,
62            cwd=working_dir,
63            capture_output=True,
64        ):
65            return
66        # apply patch from the submission
67        if trajectory["info"]["submission"]
68            with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
69                f.write(trajectory["info"]["submission"])
70            print(f"wrote submission patch to {f.name}")
71            if not safe_subprocess_run(
72                path,
73                ["git", "apply", "--exclude", "Lib/test/*", f.name],
74                cwd=working_dir,
75                capture_output=True,
76            ):
77                return
78        # apply patches from the PR merge commit (tests only)
79        result = safe_subprocess_run(
80            path,
81            ["git", "diff", instance["base_commit"], instance["merge_commit"]],
82            cwd=working_dir,
83            capture_output=True,
84        )
85        if not result:
86            return
87        if result.stdout != "":
88            with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
89                f.write(result.stdout)
90            print(f"wrote test patch to {f.name}")
91            if not safe_subprocess_run(
92                path,
93                ["git", "apply", "--include", "Lib/test/*", f.name],
94                cwd=working_dir,
95                capture_output=True,
96            ):
97                return
98        # run full test suite
99        with open(path / "tests.log", "w") as f:
100            result = safe_subprocess_run(
101                path,
102                TEST_CMD,
103                shell=True,
104                cwd=working_dir,
105                stdout=f,
106                stderr=subprocess.STDOUT,
107            )
108            if not result:
109                return
110            return {"path": str(path), "exit_code": result.returncode}
111
112@ray.remote(num_cpus=1)
113def run_tests_safe(path: Path, instance: dict[str, str], trajectory: dict):
114    try:
115        # Note: We don't actually use the return values here, instead we
116        # parse the test run log file to determine if the tests passed or not
117        return run_tests(path, instance, trajectory)
118    except Exception:
119        return
120
121instances = load_dataset("pcmoritz/cpython_dataset", split="train")
122results = []
123
124for path in Path('/mnt/shared_storage/pcmoritz/rollouts').iterdir():
125    if path.is_dir():
126        json_file = path / f"{path.name}.traj.json"
127        if not json_file.exists():
128            continue
129        with open(json_file, 'r') as f:
130            trajectory = json.load(f)
131            instance = instances.filter(lambda x: x['instance_id'] == path.name)[0]
132            if trajectory["info"]["submission"] and re.search(r'Binary files .+ and .+ differ', trajectory["info"]["submission"]):
133                print(f"skipping instance {instance}")
134                continue
135            results.append(run_tests_safe.remote(path, instance, trajectory))
136
137ray.get(results)
```

我们发现在跑这些模拟时，有几个技巧很有用：

- 把模拟的日志和输出写到 NFS 这类分布式文件系统里，这样部分进度可以被查看，整个作业被抢占后也能接着跑（类似于传统数据处理里的行级 checkpoint）。
- 给模拟设置合适的内存上限，这样一个失控的 agent 不会把别的 agent 一起带崩。如果用的是轻量的、基于进程的隔离，可以把进程包在 `prlimit --as=<memory limit in bytes> <command>.` 里来实现。
- 要避免共享文件或系统文件被 agent 改掉，你可以用容器镜像，或者像我们上面为 agent 模拟做的那样用 bubblewrap 这类命令。在我们的例子里，评估阶段并不需要这样做，因为 `cpython` 测试套件的多个实例可以同时运行而不互相干扰。

要准备软件工程的依赖（例如本例里编译 `python3` 所需的依赖），你可以用一个 container file，里面写这样的命令：

```
1RUN sudo sed -i 's/# deb-src/deb-src/' /etc/apt/sources.list
2RUN sudo apt update
3RUN sudo apt build-dep -y python3
```

- 我们发现，把初始问题描述用一个 huggingface dataset 的形式标准化非常有用；然后为每个问题实例在 NFS 上建一个文件夹，随着处理推进到不同阶段（在我们的例子里是生成 rollout 与给 rollout 打分），把额外的输出陆续写进去。

Anyscale 的任务 dashboard 为你提供了一种便捷的方式来监控 agent 的执行：

![Anyscale dashboard](https://images.ctfassets.net/xjan103pcp94/BLyVfRozKV2VlNrQrHJNo/9d5cdea359205b0fe2e048feb26cef05/Screenshot_2025-08-19_at_12.14.46â__PM.png)

Anyscale dashboard

借助 dashboard 的 metrics 页面，你还能判断是哪类资源成了执行的瓶颈（例如磁盘吞吐、网络吞吐、CPU 或 GPU 的显存容量、CPU 或 GPU 的计算吞吐），从而为你的具体负载挑选最合适的实例类型，或者对 CPU 这类资源做超额订阅。

下面给出我们评测的结果。我们首先评测测试通过率的天花板：对每个 `base_commit` 跑一遍完整测试套件，得到在没有任何 LLM 提出补丁时的测试通过率。注意这个天花板可以通过更细粒度地排除测试、或改进测试环境来抬高。然后我们跑两个模型，Qwen3 Coder 30B 和 Qwen3 235B，并记录每个模型生成的补丁在完整测试套件（包含每个 PR 的 golden 回归测试）上的通过率。我们还记录了「每个问题实例给模型 3 次机会、只算最成功的那一次」时的通过率。这些运行的轨迹可以用于监督微调，从而生成一个更好的基线，供更多轮运行和进一步微调使用。

在下面的实验中，我们把 temperature 设为 0.7，因为对 qwen3 而言它比 `mini-swe-agent` 默认使用的 0.0 更有效。

| **模型** | **通过率** | **3 次 rollout 的通过率** |
| --- | --- | --- |
| 测试通过率天花板 | 64.3% | — |
| Qwen/Qwen3-235B-A22B-Instruct-2507-FP8 | 46.0% | 50.8% |
| Qwen/Qwen3-Coder-30B-A3B-Instruct | 36.1% | 49.9% |

可以看到，虽然这些模型解决这类任务已经相当有效，但仍有提升的空间。

我们也给出系统性能的扩展数据——评测完整 cpython 数据集时我们用的是 c7a.32xlarge 节点。可以看到执行时间随 CPU 数量线性扩展：

| **节点数（CPU 数）** | **执行时间** |
| --- | --- |
| 8 个节点（1024 个 CPU） | 2 小时 31 分 |
| 4 个节点（512 个 CPU） | 5 小时 9 分 |
| 2 个节点（256 个 CPU） | 10 小时 21 分 |

### 用 SkyRL 跑端到端 RL

本节给出一个例子，说明这套方法如何与运行在 Ray 上的现有 RL 库集成。这样的 RL 库[有很多可选](https://www.anyscale.com/blog/open-source-rl-libraries-for-llms)。我们选 SkyRL 来演示集成，因为它对自定义 generator 的支持很好。

Mini-SWE-Agent 与 SkyRL 的集成可以在[这里](https://github.com/NovaSky-AI/SkyRL/pull/222)找到。在 SkyRL 里，训练栈是模块化设计的，有两个主要组件：[训练器与生成器](https://skyrl.readthedocs.io/en/latest/getting-started/overview.html)。在这个例子里，我们定制 generator，改用 Mini-SWE-Agent 来为 SWE-Bench 任务生成轨迹。

从整体上看，我们实现了一个 `MiniSweAgentGenerator`，用一个自定义的 `generate` 方法来生成一批轨迹：

```
1class MiniSweAgentGenerator(SkyRLGymGenerator):
2	async def generate_trajectory(self, prompt, ...): 
3		...
4	async def generate(self, generator_input: GeneratorInput) -> GeneratorOutput:
5		...
6		prompts = generator_input["prompts"]
7		env_extras = generator_input["env_extras"]
8		tasks = []
9		for i in range(len(prompts)):
10	           tasks.append(
11	               self.generate_trajectory(
12	                  prompts[i],
13	                  env_extras[i],
14	               )
15	           )
16
17	       all_outputs = await asyncio.gather(*tasks)
```

在 `generate_trajectory` 里，我们启动一个 Ray 任务，为给定的实例生成一条轨迹并做评估。更具体地说，它包括以下内容：

- 生成：为该实例初始化一个沙箱 / 环境用 Mini-SWE-Agent 在该环境里生成一条轨迹。推理方面，我们把 Mini-SWE-Agent 配置成使用 SkyRL 提供的 HTTP endpoint。生成完成后保存所生成的 git patch。
- 评估：使用给定的 backend 为该实例初始化一个全新的环境。把模型的 git patch 应用到环境中的工作目录。运行该实例的评估脚本。如果脚本运行成功，就认为该实例已被解决，否则视为未解决。

把这套工作流作为 Ray 任务来跑，也让我们能够把所有节点上的生成能力都扩上去。

从整体上看，代码大致如下：

```
1@ray.remote(num_cpus=0.01)
2def init_and_run(instance: dict, litellm_model_name: str, sweagent_config: dict, data_source):
3    model = get_model(litellm_model_name, sweagent_config.get("model", {}))
4    error = None
5    try:
6        env = get_sb_environment(sweagent_config, instance, data_source)
7        agent = DefaultAgent(model, env, **sweagent_config.get("agent", {}))
8        exit_status, model_patch = agent.run(instance["problem_statement"])
9        eval_result = evaluate_trajectory(instance, model_patch, sweagent_config, data_source)
10    except Exception as e:
11        error = str(e)
12    return agent.messages, eval_result, error
13
14class MiniSweAgentGenerator(SkyRLGymGenerator):
15    async def generate_trajectory(self, prompt, env_extras, ...):
16        messages, eval_result, error = init_and_run.remote(
17            env_extras["instance"], 
18            litellm_model_name, 
19            sweagent_config, 
20            data_source
21        )
22        ...
```

请注意，完整实现还包含一些用于配置和错误处理的额外逻辑，可以在[这里](https://github.com/NovaSky-AI/SkyRL/pull/222)找到。

更多信息请参阅[这里的文档](https://skyrl.readthedocs.io/en/latest/examples/mini_swe_agent.html)。

## 结论

本文展示了如何用 Ray 大规模运行 agentic 模拟，来生成轨迹、评估 agent 并训练 agent。Ray 的灵活性让我们能把所有相关负载（数据处理、模型服务与训练）跑在同一个集群里，这简化了开发与实验的搭建，也让我们能把问题实例的数量扩到非常大的规模。简单高效的沙箱机制，让各种各样的 agentic 负载都能轻松地在规模化环境里运行。

本文展示的所有示例都能在 [Anyscale](https://www.anyscale.com/) 上开箱即用。由于 Ray 的分布式特性，部署和评估由多个组件构成的 agent（例如用 [MCP servers](https://console.anyscale.com/template-preview/mcp-ray-serve) 来解决某个问题）也很容易。

本文的这些技术既可以作为流水线中各自独立的步骤来跑，也可以集成为不同 [RL 库](https://www.anyscale.com/blog/open-source-rl-libraries-for-llms)的一部分。[SkyRL](https://github.com/NovaSky-AI/SkyRL) 凭借其灵活的 generator 框架让这件事变得简单，我们在本文里给出了一个相应的例子。
