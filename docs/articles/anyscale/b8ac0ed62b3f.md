---
vendor: anyscale
title: 使用 Ray 进行大规模并行代理模拟
original_title: 
url: https://anyscale.com/blog/massively-parallel-agentic-simulations-with-ray
date: 2025-09-10
lang: zh
captured: 2026-11-05
extractor: readability-v1
translator: mt
status: translated
body_sha: d1354358f30a
---

[主页](https://www.anyscale.com/)[博客](https://www.anyscale.com/blog)博客详细信息

# 使用 Ray 进行大规模并行代理模拟

作者：[Philipp Moritz](https://www.anyscale.com/blog?author=philipp-moritz)、[Sumanth Hegde](https://www.anyscale.com/blog?author=sumanth-hegde)、[Tyler Griggs](https://www.anyscale.com/blog?author=tyler-griggs) 和 [Eric Tang](https://www.anyscale.com/blog?author=eric-tang) | 2025 年 9 月 10 日

![使用 Ray 进行大规模并行代理模拟图片](https://images.ctfassets.net/xjan103pcp94/7JUCwEieiRvbaHqx1VYRIu/ca861e91b802a5ba8e2919144885bc8f/Screenshot_2025-09-10_at_10.42.26â__AM.png?w=1200)

虽然在笔记本电脑上针对托管模型端点（例如 ChatGPT、Claude、Gemini 或 OSS 模型的模型提供商之一）运行单个代理很容易，但在集群上并行运行数千个代理却是一个重大挑战。这也是许多非常有用的LLM和代理用例的重要要求，包括：

- **运行评估：**代理评估用于代理应用程序开发的内循环。它们对于帮助构建更好的LLM、为LLM编写更好的提示或改进代理循环本身至关重要。
- **迭代数据集：**构建代理取决于问题陈述的数据集和验证解决方案的技术。代理模拟使我们能够迭代这些数据集，过滤和改进它们，并收集解决方案轨迹以进行监督微调。
- **运行 RL 训练：** 代理模拟是 RL 训练循环的重要组成部分。它们用于收集轨迹和奖励，用于通过 RL 更新策略。

当您从在笔记本电脑上运行单个代理扩展到并行运行大量代理时，您可能会遇到以下挑战：

- **隔离代理：** 代理需要隔离，以便它们不会相互干扰以及系统的其余部分，并保持在合理的资源限制内。此外，代理需要在定义明确的环境（例如容器）中运行。
- **扩展模型推理和工具使用：** 如果您并行运行大量代理，模型提供者的速率限制通常是不够的，因此您需要弄清楚如何扩展推理。您还可以使用常见工具，例如 MCP 服务器，这些工具也需要通过代理进行扩展。
- **使用自定义模型：** 如果您正在构建自定义代理，您可能还会训练或微调需要部署的自定义模型。

大多数此类设置都涉及大量样板代码和复杂的基础设施。

Ray 允许您使用简单的 Python API 运行大规模并行代理模拟，从而直接解决这些挑战。它处理混合 CPU 和 GPU（或其他加速器）工作负载，并支持推理服务器（例如 vLLM 或 SGLang）等有状态服务。这使得推理能够在与模拟相同的集群上运行，从而能够对模型和代理进行快速联合实验，并进行联合扩展以避免模型的速率限制。 Ray 方便的 Pythonic 开发人员体验使实验设置的迭代变得容易，并无缝扩展到非常大的运行。此外，Ray 的容错功能可以通过使用竞价实例来节省成本。

以下是您通过阅读博客文章将了解到的内容：

- 您将学习如何通过灵活的隔离来运行多个沙盒环境，因此沙盒可以在任何环境（非特权、容器中的容器）中运行，而无需设置单独的沙盒环境。
- 您将了解如何在单个 Ray 集群上运行推理和代理执行，以实现代理和 LLM 设置的快速迭代，而不会遇到速率限制，并且可以轻松扩展并行代理的数量。
- 您将看到上述所有三个用例（运行评估、迭代数据集、运行 RL 训练）的具体示例，以及有关如何提高它们的效率和更容易迭代的一些技巧。

我们将在软件工程的背景下演示这些关键点。为此，我们还开源了一个新数据集，其中包含从 [cpython 存储库](https://github.com/python/cpython) 中抓取的 5500 个测试用例，并展示了如何并行评估它们。我们展示的技术是通用的，也适用于其他领域，包括通用计算机使用、数据工程或科学研究。

## Link隔离并行代理模拟

执行许多并行代理模拟时的一个核心问题是如何将它们彼此隔离并与系统环境隔离。有不同的选择：

- **使用具有完整文件系统隔离的容器：**Docker 是许多软件工程师熟悉的标准，容器非常适合在非对抗性设置中隔离工作负载。这使得 docker 成为一种非常流行的运行代理的方式。使用 docker 也有一些缺点：容器镜像的构建、推送、拉取和存储成本可能很高，而且速率限制可能很烦人。此外，在超级计算机等非特权环境中或在另一个容器内运行可能具有挑战性。其中一些问题可以通过使用不同的容器运行时（例如 podman 或 apptainer）来解决（我们将在下面展示如何执行此操作）。
- **将进程与 cgroup 和 chroot 一起使用：**运行代理的一种不太重量级的方法是通过可以使用 Linux cgroup 和 chroot 隔离的进程。在底层，这也是容器的实现方式，但是直接使用原语可以更好地控制隔离如何发生，例如大多数主机文件系统和包都可以在此设置中重用，因此可以在不拉动和推送容器映像的情况下运行代理，但仍然使用良好的隔离。虽然从头开始实现这一点非常复杂，但有一些方便的命令行实用程序，例如 [bubblewrap](https://github.com/containers/bubblewrap)，可以使这变得简单（我们再次在下面展示如何执行此操作）。
- **使用虚拟机或远程执行：**在某些场景中，需要更重的隔离机制。例如，您可能想在 Mac 上运行 Linux 应用程序，或者在 ARM 上运行 x86_64 应用程序，在这种情况下您需要 VM。在极少数情况下，您需要比容器或 cgroup 提供的更多隔离，在这种情况下，VM 或微型 VM 可能是一个不错的选择。或者您可能希望使用单独的 K8s 集群来执行代理，或使用单独的云提供商。与一些更简单的隔离方法（例如额外的错误处理和通信机制）相比，这些选项通常需要在基础设施级别上进行更多工作。

容器是最常见、应用最广泛的隔离机制，并且与生态系统融合得很好，因此在很多情况下应该是首选。具有附加机制（例如气泡包装）的过程可能尚未得到充分探索以进行隔离。它们非常轻量级且非常易于迭代，并且可以与 uv 等包管理器、本机 Linux 发行版包管理器或 [NixOS](https://nixos.org/) 或 [Guix](https://guix.gnu.org/) 等技术结合使用，以灵活定义代理运行的环境。为了能够针对每种情况使用最适合的隔离原语，我们的设置应该在其环境支持方面灵活。

## 用于代理模拟的 LinkAgent 支架

代理脚手架实现了LLM周围的结构，这使得它可以有效地解决特定领域的问题，在我们的软件工程案例中。脚手架由以下部分组成：

- 向 LLM 提供的提示，通常以模板的形式出现，其中包含占位符，例如 github 问题描述或有关如何在给定软件存储库中操作的具体说明，
- LLM 可用于解决方案的工具，例如 shell 命令、文件编辑工具、Python 解释器、用于收集有关问题和解决方案的更多信息的搜索工具以及可能以 MCP 服务器形式提供的任何其他任意工具，
- 代理循环重复查询LLM并执行LLM的操作。它还可以与用户进行交互检查，并允许他们修改LLM提议的行动方案。

虽然我们在本博客中重点关注软件工程，但该方案非常通用，也适用于任意计算机使用或更专业的领域，例如数据科学工作负载或科学研究。

一些脚手架支持LLM的操作的各种形式的沙箱​​。有些支架是为最终用户解决特定问题而设计的，有些支架是为了运行大规模实验而优化的（例如用于评估或强化学习训练）。虽然这些用例需要不同的解决方案，但理想情况下它们共享相同的提示和工具调用，因此在实验数据集上进行的任何实验都将直接代表用户体验。以下是我们所知的软件工程代理支架列表：

- 最终用户通常以交互方式使用的支架，包括 [Claude Code](https://github.com/anthropics/claude-code)、[Gemini CLI](https://github.com/google-gemini/gemini-cli)、[Qwen Code](https://github.com/QwenLM/qwen-code) 和 [Aider](https://github.com/Aider-AI/aider)。它们一次支持一个会话，通常不提供沙箱，但它们可以与实际工作负载环境一起在容器内运行。其中一些还可以用作评估或强化学习设置的一部分。
- [OpenHands](https://github.com/All-Hands-AI/OpenHands) 是一种流行的全功能代理运行时，旨在供最终用户使用以及用于评估和 RL 设置（它带有评估工具）。 OpenHands 主要基于 docker，并且[可用](https://novasky-ai.notion.site/skyrl-v0) 提供基于远程 k8s 的运行时。它对 MCP 服务器、浏览器和自定义工具等不同工具提供非常通用的支持。
- [SWE-agent](https://github.com/SWE-agent/SWE-agent) 是 SWE-bench 作者的一个代理，可用于解决软件工程问题。它还有一个最小版本，[mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent)，它在隔离方面最灵活，代码非常简单且可修改，因此很容易适应广泛的工作负载。它仅使用 bash 命令即可在软件工程任务中表现良好。
- [Terminal-bench](https://github.com/laude-institute/terminal-bench) 是针对终端使用任务的代理的基准，它附带一个用于适应其他基准（包括 SWE-Bench）的评估工具和一个名为 Terminus 的内置代理支架。所有任务都打包为 Docker 映像，并且该工具为每个任务启动一个容器化环境。
- [R2E-Gym](https://github.com/R2E-Gym/R2E-Gym) 提供了一个类似于健身房的环境界面以及围绕它的代理包装器，但针对模拟和 RL 工作负载进行了更优化。它支持文件编辑器、bash 和文件搜索等工具。
- [Smolagents](https://github.com/huggingface/smolagents?tab=readme-ov-file) 是一个 Huggingface 库，它也注重简约，但也有更多的集成，支持不同的工具调用，并支持通过 Docker 或 E2B 在沙盒环境中执行。

In this blog post we adopted mini-swe-agent because it is extremely simple and hackable and also gives good performance on software engineering problems without extra complexity, but the same approaches demonstrated below are also applicable to other scaffolds.

##链接cpython问题数据集

在这篇博文中，我们使用一个非常简单的数据集，该数据集是从 [cpython](https://github.com/python/cpython) 存储库生成的。可以为许多不同的存储库生成类似的数据集。该格式是一种简化的 swebench 格式，针对运行完整测试套件进行验证进行了优化。 We scraped about 5500 issues from the repository, found the associated PRs and extracted the `base_commit`, which is the parent commit of the PR as well as merge_commit, which is the commit that contains the code of the PR. The dataset is available [here](https://huggingface.co/datasets/pcmoritz/cpython_dataset) and the code that was used to scrape the dataset is available [here](https://gist.github.com/pcmoritz/fa911ee735a5a8f5329ea7a7c8adc47d).

![使用 Ray Img 进行大规模并行代理模拟 1](https://images.ctfassets.net/xjan103pcp94/1UmeTbGXQTiMaAhWXTyNPO/91d3b6aee67d7c308b1c5c255ed99a3c/Screenshot_2025-09-09_at_3.58.33â__PM.png)

使用 Ray Img 1 进行大规模并行代理模拟

给定 LLM 生成的补丁，可以按如下方式验证：

- 查看 `base_commit` 处的 [cpython](https://github.com/python/cpython) 存储库
- 应用LLM生成的补丁，除了`Lib/test/*`中的更改（既避免下一步中的冲突，也避免LLM删除或“修复”测试）
- 应用“Lib/test/*”中原始 PR 差异“base_commit..merge_commit”的更改（这些是 PR 添加的回归测试）
- 现在通过“./configure && make test”运行完整的测试套件。在实践中，为了使这项工作可靠，我们必须排除一些经常失败的测试。幸运的是，cpython 有一个名为“EXTRATESTOPTS”的环境变量，它允许将额外的参数传递给测试套件。我们使用此机制通过“--ignore”标志排除失败的测试。

在下一节中，我们将展示如何并行化补丁的生成以及使用 Ray 的验证。

## 链接使用 mini-swe-agent

在这篇博文的其余部分中，我们将使用 [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) 作为 AI 代理，因为它非常小，易于修改并支持不同的沙箱环境来执行代理操作。由于它的简单性，它也可以轻松地研究和适应软件工程之外的不同问题领域。 “mini-swe-agent”做出的一项设计决策使很多事情变得更容易，即代理的每个操作都是一个简单的“bash”命令，并且不需要[持久 shell 会话](https://mini-swe-agent.com/latest/faq/#why-no-shell-session)。此外，“mini-swe-agents”支持各种不同的隔离[环境]（https://github.com/SWE-agent/mini-swe-agent/tree/main/src/minisweagent/environments）：

- 本地执行，仅执行“bash”命令中的每个命令，无需特殊隔离。在没有用户交互的情况下运行命令的设置中不建议这样做，但可以用于本地交互式使用，其中每个命令在执行之前都由用户检查。
- 通过 [docker](https://www.docker.com/)、[podman](https://podman.io/) 或 [apptainer](https://apptainer.org/) 在容器环境中执行。如果我们想使用容器进行隔离，我们通常会选择podman，因为它不需要守护进程，并且可以配置为在各种环境中运行（包括容器内部以及非特权环境）。 Apptainer 可以成为在超级计算机上运行的良好环境。
- 在由 [bubblewrap](https://github.com/containers/bubblewrap) 隔离的进程中执行，这允许在隔离的环境中运行，而无需设置和维护容器映像的开销。它通过[此环境]（https://github.com/SWE-agent/mini-swe-agent/blob/main/src/minisweagent/environments/extra/bubblewrap.py）支持。例如，我们将在下面使用它来运行 cpython 环境，并与[启动命令](https://github.com/SWE-agent/mini-swe-agent/pull/490) 结合使用，它可以用于设置更复杂的环境，例如使用 uv 的 Python 虚拟环境，用于在 Python 代码库上工作的软件工程代理。

要使用 podman 运行“mini-swe-agent”，您可以通过以下方式安装 podman：
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
然后在签出 [https://github.com/SWE-agent/mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) 的目录中，您可以运行
```
1uv run --extra full mini-extra swebench --model openai/gpt-5-nano --subset verified --split test --workers 128 --output <output directory>
```
要成功运行此特定基准测试，您应该在 `swebench.yaml` 中设置以下参数：在 `environment` 下，添加 `executable: "podman"` 以及 `timeout: 3600` 和 `pull_timeout: 1200`。

对于此类需要拉取大量容器映像的工作负载，还建议使用具有本地 NVMe 磁盘的计算机。如果您在 Anyscale 上的 AWS 上运行，这些将自动配置为 RAID 阵列，以获得最佳性能。

## Link使用 Ray 运行并行 SWE 模拟

在本节中，我们将向您展示如何使用 Ray 和 [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) 运行多个并行模拟。我们将重点关注上面介绍的“cpython”问题数据集上的 SWE-bench 风格的软件工程任务，但这些想法广泛适用于许多不同的模拟环境。

### Link从代理生成数据

在本节中，我们将介绍一个简单而有效的代码示例，用于从代理生成推出数据。使用名为“Engine”的参与者，我们在集群中的每个节点上启动一个“vllm”或“sglang”服务器，并使用 Ray 任务“generate_rollout”（每个问题陈述一个任务）对其运行许多并行模拟。每个任务都使用 [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) 中的“swebench-single”脚本来执行部署。这种设置使推理设置变得简单，因为我们可以直接使用 vllm 和 `sglang` 的 CLI 来启动推理引擎。或者，也可以运行 llm 引擎的集中部署，例如使用 [Ray Serve LLM](https://docs.ray.io/en/latest/serve/llm/index.html) 并将模型公开到所有代理连接到的全局端点，或将 `sglang` 与 [sglang router](https://docs.sglang.ai/advanced_features/router.html) 一起使用。
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
对于此实验，我们将环境类设置为 [bubblewrap](https://github.com/SWE-agent/mini-swe-agent/blob/main/src/minisweagent/environments/extra/bubblewrap.py)。这将确保同一台计算机上运行的所有代理彼此隔离并与系统环境隔离。我们还将结果写入共享 NFS 卷，以便我们可以在下一步中进行进一步的后处理和过滤。一般来说，将轨迹文件和其他输出文件（如日志）写入 NFS 是一种有用的模式，它还允许我们检查部分运行，并在重新执行生成脚本时从中断处恢复。

上述设置中有很多参数可以调整：一是vLLM引擎参数，包括各种形式的并行度，参见[vLLM优化指南](https://docs.vllm.ai/en/latest/configuration/optimization.html)。最佳设置通常取决于您的硬件以及您正在使用的模型架构。另一个需要调整的参数是每个引擎的代理数量。可以通过增加“generate_rollout”装饰器中的“num_cpus”参数来减少。在实践中，我们发现每个引擎 64 到 128 个代理效果良好。每个引擎的最佳代理数量取决于在环境中花费的时间（CPU 工作）和评估 LLM 所花费的时间（GPU 工作）的比率。该比率越高，需要的代理就越多，因此有足够大的批量大小以使推理引擎饱和。

### Link对数据运行过滤和后处理

在本节中，我们将介绍如何使用 Ray 来过滤和后处理数据集以评估轨迹的质量，例如通过分配奖励。一般来说，每个问题实例运行一个 Ray 任务效果很好。如果使用单独的奖励模型，则可以按照与部署代理 LLM 类似的方式进行部署。对于更复杂的设置，使用 [Ray Data](https://docs.ray.io/en/latest/data/data.html) 和 [Ray Data LLM](https://docs.ray.io/en/latest/data/working-with-llms.html) 进行数据集准备可能是有意义的，因为评分和过滤是批量数据处理工作负载。

作为示例，我们将实现“cpython 问题数据集”部分中描述的验证过程。代理轨迹在上一步中生成并写入 NFS。在此步骤中，对于每个问题实例，我们提取代理生成的补丁，并针对完整的 cpython 测试套件进行测试，包括由人类在修复问题的“黄金 PR”中进行的回归测试（原始代理除非作弊，否则看不到）。如果修补后的代码通过了所有测试，则获得奖励 1，否则奖励为 0。根据设置，将验证作为部署过程的一部分或单独运行可能是有意义的。在博客文章的最后一部分中，我们将展示如何将部署和验证过程集成到 RL 框架中。

这是我们刚刚描述的验证过程的代码：
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
我们发现运行模拟时有用的一些技巧：

- 将模拟的日志和输出写入 NFS 等分布式文件系统，以便可以检查部分进度，并且如果整个作业被抢占，则可以恢复进度（类似于传统数据处理中的行级检查点）。
- 为模拟设置适当的内存限制，这样一个流氓特工就不会拖垮其他特工。如果使用基于轻量级进程的隔离，则可以通过将进程包装在“prlimit --as=<以字节为单位的内存限制> <命令>”中来完成。
- 为了避免代理修改共享文件或系统文件，您可以使用容器映像或 bubblewrap 之类的命令，就像我们上面为代理模拟所做的那样。在我们的例子中，这对于评估来说不是必需的，因为“cpython”测试套件的多个实例可以同时运行而不会互相干扰。

要设置软件工程依赖项（例如，在本示例中用于编译“python3”），您可以使用包含以下命令的容器文件：
```
1RUN sudo sed -i 's/# deb-src/deb-src/' /etc/apt/sources.list
2RUN sudo apt update
3RUN sudo apt build-dep -y python3
```
- 我们发现以 Huggingface 数据集的形式标准化初始问题陈述的数据集非常有用，然后为每个问题实例在 NFS 上创建一个文件夹，当我们经历不同的处理阶段时，额外的输出会写入其中，在我们的例子中生成和评分推出。

Anyscale 的任务仪表板为您提供了一种监控代理执行情况的便捷方法：

![任意规模仪表板](https://images.ctfassets.net/xjan103pcp94/BLyVfRozKV2VlNrQrHJNo/9d5cdea359205b0fe2e048feb26cef05/Screenshot_2025-08-19_at_12.14.46â__PM.png)

任意规模的仪表板

使用仪表板的指标页面，您还可以确定哪些资源是执行的瓶颈（例如磁盘吞吐量、网络吞吐量、CPU 或 GPU 内存容量、CPU 或 GPU 计算吞吐量），并选择最适合您的特定工作负载的实例，或超额订阅某些资源（如 CPU）。

我们现在介绍我们的评估结果。我们首先通过评估每个“base_commit”的完整测试套件来评估测试通过率的上限。这产生了测试通过率，无需LLM建议的任何补丁。请注意，可以通过更细粒度地排除测试或改进测试环境来提高上限。然后，我们运行两个模型：Qwen3 Coder 30B 和 Qwen3 235B，并记录每个模型生成的补丁针对完整测试套件（包括每个 PR 的黄金回归测试）的通过率。如果模型对每个问题实例进行 3 次尝试并且仅计算最成功的尝试，我们还会记录通过率。这些运行的轨迹可用于监督微调，为更多运行和进一步微调生成更好的基线。

在接下来的实验中，我们使用了 0.7 的温度，因为它对于 qwen3 来说比 `mini-swe-agent` 使用的默认温度 0.0 更有效。

| **型号** | **通过率** | **3 次推出的通过率** |
| ---| ---| ---|
|测试通过率上限| 64.3% | — |
| Qwen/Qwen3-235B-A22B-Instruct-2507-FP8 | 46.0% | 50.8% |
| Qwen/Qwen3-Coder-30B-A3B-指令 | 36.1% | 49.9% |

正如您所看到的，虽然模型在解决这些任务方面相当有效，但仍然有改进的机会。

我们还展示了系统性能扩展数字——我们使用 c7a.32xlarge 节点来评估完整的 cpython 数据集。正如您所看到的，执行时间与 CPU 数量呈线性关系：

| **节点数量（CPU 数量）** | **执行时间** |
| ---| ---|
| 8 个节点（1024 个 CPU）| 2小时31分钟 |
| 4 个节点（512 个 CPU）| 5小时9米|
| 2 个节点（256 个 CPU）| 10 小时 21 分钟 |

### Link使用 SkyRL 运行端到端强化学习

在本节中，我们将举例说明如何将此方法与 Ray 上运行的现有 RL 库集成。此类 RL 库有[许多选项](https://www.anyscale.com/blog/open-source-rl-libraries-for-llms)。我们选择 SkyRL 来展示集成，因为它对自定义生成器有很好的支持。

Mini-SWE-Agent 与 SkyRL 的集成可以在[此处](https://github.com/NovaSky-AI/SkyRL/pull/222)找到。使用 SkyRL，训练堆栈以模块化方式设计，具有两个主要组件：[训练器和生成器](https://skyrl.readthedocs.io/en/latest/getting-started/overview.html)。在本例中，我们自定义生成器以使用 Mini-SWE-Agent 来生成 SWE-Bench 任务的轨迹。

在高层次上，我们使用自定义的“generate”方法实现“MiniSweAgentGenerator”来生成一批轨迹：
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
在“generate_trajectory”中，我们启动 Ray 任务来生成轨迹并针对给定实例对其进行评估。更具体地说，这包括以下内容：

- 生成：为实例初始化沙箱/环境，使用 Mini-SWE-Agent 在此环境中生成轨迹。为了进行推理，我们将 Mini-SWE-Agent 配置为使用 SkyRL 提供的 HTTP 端点。生成完成后存储生成的 git 补丁。
- 评估：使用给定后端为给定实例初始化一个新环境。将模型的 git 补丁应用到环境中的工作目录。运行实例的评估脚本。如果脚本成功运行，则认为实例已解析，否则视为未解析。

通过将此工作流程作为 Ray 任务运行，我们还能够在 Ray 集群中的所有节点上扩展生成。

从较高层次来看，代码如下所示：
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
请注意，完整的实现有一些用于配置和错误处理的附加逻辑，可以在[此处](https://github.com/NovaSky-AI/SkyRL/pull/222)找到。

有关更多信息，请参阅[此处的文档](https://skyrl.readthedocs.io/en/latest/examples/mini_swe_agent.html)。

## 链接结论

在这篇博文中，我们展示了如何使用 Ray 大规模运行代理模拟，以生成轨迹、评估和训练代理。 Ray 的灵活性使我们能够在单个集群中运行所有相关工作负载（数据处理、模型服务和训练），这简化了开发和实验设置，并允许我们扩展到大量问题实例。简单高效的沙箱可以轻松大规模运行各种代理工作负载。

博客文章中显示的所有示例都可以在 [Anyscale](https://www.anyscale.com/) 中开箱即用。由于 Ray 的分布式特性，使用 [MCP 服务器](https://console.anyscale.com/template-preview/mcp-ray-serve) 等多个组件来部署和评估代理来解决给定问题也很容易。

本博文中的技术既可以作为管道的单独步骤独立运行，也可以作为不同 [RL 库](https://www.anyscale.com/blog/open-source-rl-libraries-for-llms) 的一部分进行集成。 [SkyRL](https://github.com/NovaSky-AI/SkyRL) 由于其灵活的生成器框架而使这变得容易，我们在博客文章中提供了一个示例。

＃＃＃＃ 目录

- [隔离并行代理模拟](https://www.anyscale.com/blog/massively-parallel-agentic-simulations-with-ray#isolated-parallel-agentic-simulations)
- [用于代理模拟的代理支架](https://www.anyscale.com/blog/massively-parallel-agentic-simulations-with-ray#agent-scaffolds-for-agentic-simulations)
- [cpython 问题数据集](https://www.anyscale.com/blog/massively-parallel-agentic-simulations-with-ray#the-cpython-issues-dataset)
- [使用 mini-swe-agent](https://www.anyscale.com/blog/massively-parallel-agentic-simulations-with-ray#using-mini-swe-agent)
- [使用 Ray 运行并行 SWE 模拟](https://www.anyscale.com/blog/massively-parallel-agentic-simulations-with-ray#running-parallel-swe-simulations-with-ray)
- [从代理生成数据](https://www.anyscale.com/blog/massively-parallel-agentic-simulations-with-ray#generate-data-from-agents)
- [对数据运行过滤和后处理](https://www.anyscale.com/blog/massively-parallel-agentic-simulations-with-ray#running-filtering-and-post-processing-on-the-data)
- [使用 SkyRL 运行端到端强化学习](https://www.anyscale.com/blog/massively-parallel-agentic-simulations-with-ray#running-end-to-end-rl-with-skyrl)
- [结论](https://www.anyscale.com/blog/massively-parallel-agentic-simulations-with-ray#conclusion)

####分享

####标签

#### 注册产品更新

####推荐内容

![LLM Graph 的开源 RL 库](https://images.ctfassets.net/xjan103pcp94/3DTHR8PtMcYFYkFUnZVjTH/8aa576362b47aedbce2859583737dca6/image1.png?w=140)强化学习 (RL) 库的架构分为两个主要组成部分：生成和训练。在生成阶段，LLM 引擎在环境中执行多轮部署以生成数据和奖励信号。然后将该输出输入训练阶段以更新模型的参数。这个过程形成了一个反馈循环，其中逐步改进的模型生成下一次数据迭代以进行持续细化。

#### LLM的开源强化学习库

![kuberay-products-best-practices-field](https://images.ctfassets.net/xjan103pcp94/3uRWLXRJv2sisfuH1UpkBg/7ffa981a092ba41c591b03ef933976bf/kuberay-products-best-practices-field.png?w=140)

#### 生产中的 KubeRay：现场最佳实践

![宣布 Ray 在 Google TPU 上支持 PyTorch](https://images.ctfassets.net/xjan103pcp94/5odqs3bDXHHrUGye7EReO6/12a5fb11fc7d119b1ce905d420821160/ExternalRayTorchTPUblog.png?w=140)

#### 宣布 Ray 在 Google TPU 上支持 PyTorch

## 立即探索 Anyscale

使用专为生产 AI 构建的多云平台，在 Ray 上构建、运行和扩展任何 AI 工作负载。

[免费开始](https://authkit.anyscale.com/?utm_source=anyscale&utm_content=exploreblock&utm_medium=website&utm_campaign=cta)[与专家交谈](https://www.anyscale.com/book/demo?utm_source=anyscale&utm_content=exploreblock&utm_medium=website&utm_campaign=cta)
