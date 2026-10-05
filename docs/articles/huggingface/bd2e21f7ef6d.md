---
vendor: huggingface
title: SAIR：用 AI 驱动的结构智能加速制药研发
original_title: SAIR: Accelerating Pharma R&D with AI-Powered Structural Intelligence
url: https://huggingface.co/blog/SandboxAQ/sair-data-accelerating-drug-discovery-with-ai
date: 2026-04-07
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

今年夏天，SandboxAQ 发布了 **Structurally Augmented IC50 Repository（结构增强型 IC50 库，**[**SAIR**](https://huggingface.co/datasets/SandboxAQ/SAIR)**）**——最大的「蛋白质-配体 3D 共折叠结构 + 实验测得 IC₅₀ 标签」配对数据集，把分子结构直接链接到药物效力，克服了训练数据长期稀缺的问题。这个数据集现已在 Hugging Face 上发布。研究者第一次可以开放访问超过 **500 万**个由 AI 生成、高精度的蛋白质-配体 3D 结构，每一个都配有经过验证的实测结合效力数据。

[![image/png](https://cdn-uploads.huggingface.co/production/uploads/680ff4388f704be391757780/KOXzLW72JLyU3rtMrb3yn.png)](https://cdn-uploads.huggingface.co/production/uploads/680ff4388f704be391757780/KOXzLW72JLyU3rtMrb3yn.png)

**SAIR 是一个开源数据集**，在宽松的 CC BY 4.0 许可证下免费公开，可立即用于商业与非商业研发管线。SAIR 不只是一个数据集，更是弥合 AI 药物设计长期数据缺口的**战略资产**。它赋能让制药、生物科技和 tech-bio 领域的领导者加速研发、扩大靶点视野、为 AI 模型强力充能——把更多昂贵、冗长的药物设计与优化环节从湿实验搬到 *in silico*（计算机模拟）。这意味着更短的命中-到-先导（hit-to-lead）周期、更高效的先导化合物优化、更少的死胡同项目，以及从最初想法到临床候选物更可预测的路径。

# 跨越既有 AI 成就

AI 与计算机辅助设计在大幅加速新药开发方面潜力巨大。几十年来，科学家一直梦想着这样的 AI：只需一个描述疾病通路的提示，就能识别或设计出强效、无毒、有效的化合物，把数年的药物研发实际压缩到电脑上的几分钟。然而，这一愿景受制于 AI 仅凭分子结构预测关键药物属性（如效力、毒性等）的能力。

此外，传统的基于结构的发现常常在早期就被「确定可靠的 3D 结构」拖慢。三维分子结构决定了分子的功能、动力学和相互作用——当潜在药物候选物预计要与人蛋白靶点结合时，这一点尤其重要。

实验方法，如 X 射线晶体学和冷冻电镜（cryo-EM），需要大量时间与投入，而许多有前景的疾病靶点仍缺乏实验验证的结构信息。计算机模拟 helped 降低了获取 3D 结构和预测结合亲和力的门槛。然而，早一代的蛋白质折叠与对接算法（如 AlphaFold 和 Vina）只能预测分子和蛋白质的静态快照——而现实中它们本质上是动态、随形状变化的。

SAIR 解决了这一制约：它汇编了超过 **100 万个唯一的计算共折叠蛋白质-配体对**，最终产出 **524 万**个不同的 3D 复合物（每对五个不同的共折叠结构）。每个结构都配有来自 [ChEMBL](https://www.ebi.ac.uk/chembl/) 或 [BindingDB](https://www.bindingdb.org/rwd/bind/index.jsp) 的精编 IC₅₀ 测量值，第一次在高质 3D 结构与药物效力之间建立了可扩展的链接，弥合了阻碍 AI 驱动发现的历史数据鸿沟。在类似数据上训练的深度学习亲和力模型，如 Boltz-2，[已被证明](https://www.rxrx.ai/boltz-2)相比传统第一性原理方法可带来高达 1,000 倍的提速。

# 为前沿计算而优化

创造 SAIR 是一次高性能 AI 计算的重大工程。用共折叠 AI 模型 Boltz1，在 760 颗 NVIDIA H100 处理器组成的集群上、经由 Google Cloud Platform 调用 NVIDIA DGX Cloud，计算 SAIR 数据集耗费了超过 130,000 GPU 小时。

采集高度细粒度的节点、算子、调度器与 GPU 指标，加上在基础设施和负载优化上的紧密协作，帮助 NVIDIA AI Accelerator 与 SandboxAQ 工程团队定位瓶颈、优化配置，取得最高的负载吞吐量。

最终，两个团队在生成 SAIR 数据集时实现了 >95% 的 GPU 计算利用率。让我们在三周内做出 SAIR——而最初的估计是三个月（提速超过 4 倍）——并沉淀出一套高度优化、GPU 原生的计算工作流，可无缝对接当今最先进的企业计算环境。

# 空前的规模、准确率与能力

生成如此庞大的数据量只是故事的一半。同样重要的是对其质量的信心——这就是为什么每个预测复合物都经过 [**PoseBusters**](https://pubs.rsc.org/en/content/articlelanding/2024/sc/d3sc04185a) 的严格验证。这是药物发现领域结构相关 AI 基准测试的行业标准开源工具，检查化学合理性与物理可行性。

**最终结果是 97%** 的 SAIR 结构通过了全部检查。除 PoseBusters 验证外，我们还在 SAIR 的合成结构与实验 IC₅₀ 值上对领先的亲和力预测方法做了基准，包括经验打分函数、3D CNN 和图神经网络。这些研究的详细结果见我们[发在 bioRxiv 上的科学论文](https://www.biorxiv.org/content/10.1101/2025.06.17.660168v1)。

SAIR 数据是新模型基准测试以及下游建模、筛选与设计的可靠基础。

# 把「暗」靶点亮起来

药物发现的一个长期挑战是「暗蛋白质组」（dark proteome）——那些根本不存在实验结构的疾病相关蛋白。SAIR 通过在实验数据稀缺之处提供可信的 AI 预测复合物，照亮了这些未知区域。例如，SAIR 数据集中超过 40% 的蛋白在 Protein Data Bank（PDB）里完全没有结构——不管带不带配体。SAIR 解决了现有 AI 模型最大的挑战之一：因数据稀缺导致的低泛化能力。有了 SAIR，科学家现在可以探索过去被认为不可成药的靶点，并带着结构假设去指导虚拟筛选和先导优化，辅以可信的模型预测。

此外，SAIR 的跨靶点广度能揭示多药理学（polypharmacology）模式，阐明单个分子如何与多个蛋白相互作用。利用这幅丰富的相互作用图谱，你可以训练 AI 模型预测脱靶效应或发现新的老药新用机会，让组织在任何实验开始之前就对化合物画像有更深入的理解。

## 访问 SAIR

SAIR 在 [Hugging Face](https://huggingface.co/datasets/SandboxAQ/SAIR) 上免费可得。下面是一份快速指南：从 Hugging Face 拉取 SAIR、浏览主表，并（可选）下载若干结构压缩包。

### 1. 安装 essentials

我们用 Hub 拉取文件，用 pandas+pyarrow 读取 Parquet。

```
pip install huggingface_hub pandas pyarrow
```

### 2. 认证

登录 Hugging Face：

```
import huggingface_hub
huggingface_hub.login(token="your_auth_token")
```

### 3. 加载主表（`sair.parquet`）

从 Hub 获取文件并加载为 DataFrame。

```
from huggingface_hub import hf_hub_download
import pandas as pd

parquet_path = hf_hub_download(
    repo_id="SandboxAQ/SAIR",
    filename="sair.parquet",
    repo_type="dataset"
)

df = pd.read_parquet(parquet_path)
df.head()
```

### 4.（可选）列出可得的结构压缩包

结构文件以大量 `.tar.gz` 归档存放于 `structures_compressed/` 下。列出来，按需选择。

```
from huggingface_hub import list_repo_files

files = [f.split("/")[-1] for f in list_repo_files("SandboxAQ/SAIR", repo_type="dataset")
         if f.startswith("structures_compressed/") and f.endswith(".tar.gz")]
files[:5]
```

### 5.（可选）下载并解压结构

每个归档可能很大（约 10 GB）。只下载你需要的，在本地解压。

```
import os, tarfile
from huggingface_hub import hf_hub_download

dest = "sair_structures"
os.makedirs(dest, exist_ok=True)

to_get = [
    "sair_structures_1006049_to_1016517.tar.gz",
    "sair_structures_100623_to_111511.tar.gz",
]

for name in to_get:
    tar_path = hf_hub_download(
        repo_id="SandboxAQ/SAIR",
        filename=f"structures_compressed/{name}",
        repo_type="dataset",
        local_dir=dest,
        local_dir_use_symlinks=False,
    )
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(dest)
    os.remove(tar_path)  # free disk space
```

该脚本的完整版本（含更健壮的日志与校验）见 [README](https://huggingface.co/datasets/SandboxAQ/SAIR/blob/main/README.md) 文件。更多细节请访问 [SAIR 主页](https://www.sandboxaq.com/sair)，阅读我们[发在 bioRxiv 上的论文](https://www.biorxiv.org/content/10.1101/2025.06.17.660168v1)，或观看我们与 [NVIDIA 联合直播的 25 分钟 webinar](https://www.youtube.com/watch?v=y96t8vu9nfg)——我们演示 SAIR 并解释其中数据的组织方式。详尽的文档、教程和示例基准都已备好，以便使用并加速内部采纳。

药物发现的未来由数据驱动、AI 加速，并扎根于可扩展、高质量的结构性洞见。虽然我们还没有「一个提示就能设计有效药物疗法」的 AI，SAIR 正用新的数据与洞见让研究者离那个目标越来越近——它甚至可能从 AI 加速的研发管线中再省掉数年时间。

我们迫不及待想看研究者用 SAIR 做出什么，SandboxAQ 的专家团队也将全程支持他们走完发现之旅。

### 问题？

请联系作者，或在 SAIR 数据集讨论页发帖。

作者：[Arman Zaribafiyan](mailto:arman.zaribafiyan@sandboxquantum.com)、[Georgia Channing](mailto:georgia@huggingface.co)、[Zane Beckwith](mailto:zane.beckwith@sandboxquantum.com) 和 [Rudi Plesch](mailto:rudi.plesch@sandboxquantum.com)
