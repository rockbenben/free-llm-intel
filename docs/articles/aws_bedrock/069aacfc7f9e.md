---
vendor: aws_bedrock
title: 新 agent 技能：为你的 coding agent 提供 Amazon SageMaker 优化的生成式 AI 推理
original_title: New agent skill: Amazon SageMaker optimized generative AI inference for your coding agent
url: https://aws.amazon.com/blogs/machine-learning/new-agent-skill-amazon-sagemaker-optimized-generative-ai-inference-for-your-coding-agent
date: 2026-10-05
lang: zh
captured: 2026-10-06
extractor: readability-v1
translator: agent
status: translated
---

# 新 agent 技能：为你的 coding agent 提供 Amazon SageMaker 优化的生成式 AI 推理

工程师们越来越多地使用编码辅助工具来加速开发工作流。今天，[Amazon SageMaker AI 优化的生成式 AI 推理](https://aws.amazon.com/blogs/machine-learning/amazon-sagemaker-ai-now-supports-optimized-generative-ai-inference-recommendations/)推出了 `aws-ai-ml` 技能，可通过 [Agent Toolkit for AWS](https://aws.amazon.com/products/developer-tools/agent-toolkit-for-aws/) 获取。这项技能让 [Kiro](https://kiro.dev/)、Claude Code、Codex 这类 coding agent 具备推理优化与基准测试方面的深度专业知识。安装技能后，你现有的 agent 就能代你对 endpoint 做基准测试、推荐部署配置、比较性能运行结果，并生成可执行的 SageMaker Python SDK v3 代码。`aws-ai-ml` 是一个工具包，可以插入任何支持 Model Context Protocol（MCP）的 coding agent，把它变成一名 SageMaker AI 推理优化专家。

在本文中，我们将梳理这项技能能做什么、如何配置，以及它如何帮助你更快地从模型走向生产。

## 挑战：在意图与基础设施之间搭桥

Amazon SageMaker AI 支持 serverful 托管，覆盖实时、批量和异步三种模式。它提供按需容量和预留容量、异构实例、虚拟私有云（VPC）隔离、自动扩缩容，并与每一条 SageMaker AI 训练路径集成。这套能力面广且深，但大多数工程师并不是先知道哪个实例族或服务容器最适合自己才来的。他们带来的是一个用例：一个想要达到的性能目标、一个需要守住的成本区间，或者一个在投入生产前必须评估的模型。

SageMaker AI 优化生成式 AI 推理的 agentic 体验正是为了弥合这一落差。你告诉 agent 你想完成什么，它就产出可执行的 SageMaker Python SDK v3 代码，你可以审阅、修改并在自己的环境中运行。agent 会提出有针对性的澄清问题，生成基于真实基准测试和实测性能数据的代码，并像解决方案架构师那样贴合你的业务约束。

全程你都在掌控之中。每一步都实时可见，并且呈现为你可以阅读、可以质疑的代码。没有任何事情发生在不透明的 UI 背后。

## 开始使用

你可以通过 [Agent Toolkit for AWS](https://aws.amazon.com/products/developer-tools/agent-toolkit-for-aws/) 在本地机器上安装 `aws-ai-ml` 技能，也可以在 Amazon SageMaker Studio 的 JupyterLab space 中使用它。无论哪种方式，都能从零基础在 10 分钟内进入可用的对话。

### 方式 A：与任意 coding agent 搭配使用（Kiro、Claude Code、Codex 或任何兼容 MCP 的 agent）

**第 1 步：安装 Agent Toolkit for AWS。** 如果还没装，先完成 Agent Toolkit 的设置。这需要 AWS Command Line Interface（AWS CLI）2.35+ 以及安装好的 [uv](https://docs.astral.sh/uv/)。

```
aws configure agent-toolkit
```

该命令会自动检测你的 agent、安装技能并配置 AWS MCP Server。关于针对具体 agent 的设置（插件安装命令、MCP 配置），参见 [Agent Toolkit for AWS 入门指南](https://aws.amazon.com/products/developer-tools/agent-toolkit-for-aws/)。

**第 2 步：安装 `aws-ai-ml` 技能。** 把 SageMaker AI 优化生成式 AI 推理技能添加到你的 agent：

```
npx skills add aws/agent-toolkit-for-aws/skills/aws-ai-ml
```

**第 3 步：确认并开始。** 打开你的 coding agent 的聊天面板并提问："有哪些可用的技能？"你应该能看到 `aws-ai-ml` 列在其中。确认之后，用自然语言描述你的意图。你的 coding agent 现在已经内置了 SageMaker AI 推理优化方面的专业知识。

**前置条件：** 你的 AWS 凭证必须拥有调用 SageMaker AI API 的权限（创建 endpoint、运行基准测试和推荐作业）。该技能生成的代码在你的凭证下运行。技能本身不需要额外的 AWS Identity and Access Management（IAM）配置。

**注意：** 对于 Kiro 和 Claude Code，agent 可以在运行时发现技能。它们可以通过 [AWS MCP Server](https://aws.amazon.com/blogs/aws/the-aws-mcp-server-is-now-generally-available/) 按需搜索并加载技能，完全不需要本地安装。试着问你的 agent："搜索与数据库相关的 AWS 技能。"关于运行时发现技能，参阅 [readme](https://github.com/aws/agent-toolkit-for-aws/tree/main/skills)。

### 方式 B：在 Amazon SageMaker Studio 内使用

如果你更愿意在一个托管的 JupyterLab 环境中工作，可以在 Amazon SageMaker Studio 中配合预配置镜像使用这项技能。

**第 1 步：打开 Amazon SageMaker Studio。** 在目标 AWS 账户和 AWS 区域中进入 Amazon SageMaker Studio，选择你的 Studio domain，并从你的用户配置（user profile）启动 Studio IDE。

**第 2 步：创建一个 JupyterLab space。** 在 Studio 落地页选择 **JupyterLab**，再选择 **Create JupyterLab space**。给 space 起个名字（例如 `my-inference-opt`），并把共享设置保持为 **Private**（技能只在私有 space 中同步）。在 **Image** 菜单下，选择包含 SageMaker AI 优化生成式 AI 推理技能的那个镜像。该镜像出厂时已预配置好 `aws-ai-ml` agent 技能及全部必要依赖。选择 **Run space** 并等待其启动（第一次大约需要 5–10 分钟）。

**注意：** 请使用全新的 space。一个在本地改过技能版本的旧 space 可能不会采用预配置镜像。

**第 3 步：打开 JupyterLab 并启动终端。** space 启动完成后，打开 JupyterLab 并选择 **Terminal**。

**第 4 步：授权你的 coding agent。** 在终端中，使用你的身份提供商（identity provider）完成 coding agent 的认证。例如，使用 Kiro 时：

```
kiro-cli login --license pro --identity-provider <your-IdP-start-URL> --region us-east-1 --use-device-flow
```

**第 5 步：确认并开始。** 打开你的 coding agent 的聊天面板并提问："有哪些可用的技能？"你应该能看到 `aws-ai-ml` 列在其中。确认之后，用自然语言描述你的意图。

> 故障排查：
>         如果 agent 报告没有可用技能，请确认你的 space 设置为 Private。你也可以在终端里检查：

```
ls ~/.kiro/skills/
```

> 如果该目录为空，但 /etc/sagemaker/skills/ 中存在技能文件，请运行 restart-jupyter-server，刷新页面后重试。

## 你能做什么

这套 agentic 体验覆盖推理优化生命周期中的以下能力。你不需要知道该调用哪个能力。描述你的需求，agent 会判断下一步；有任何不清楚的地方，它会向你提问。

### 对现有 endpoint 做基准测试

如果你已经有一个模型部署在 SageMaker AI endpoint 上，可以让 agent 对它做基准测试。告诉 agent 你想测哪个 endpoint，它会生成一个 Python notebook，用 SageMaker Python SDK 的 `Workload.synthetic()` 和 `start_benchmark()` API 跑负载测试。

在运行任何基准测试之前，agent 会先确认你的 endpoint 可以安全地接受压测，因为基准测试会向线上 endpoint 施加真实流量。

基准测试完成后，你会得到一份量化性能报告，包含：

- **吞吐（Throughput）**：每秒请求数、每秒输出 token 数。
- **延迟（Latency）**：p50、p99、首 token 时间（time-to-first-token）、token 间延迟。
- **并发（Concurrency）**：支持的并发请求数。

这些是在真实基础设施上施加真实负载测得的数值，而不是估算。agent 还会推荐提升性能的机制（如 prefill decoding）。

**示例提示：** *"Benchmark my Llama endpoint on SageMaker AI."（对 SageMaker AI 上的 Llama endpoint 做基准测试。）*

### 为你的模型找到合适的实例类型

如果你有一个模型，需要为它在 SageMaker AI 上找到合适的实例类型，告诉你的 agent 即可。模型存放在哪里、如何获得的都不重要：

- **存在 Amazon Simple Storage Service（Amazon S3）里的微调或自定义模型**：你训练或下载了一个模型并存储在 S3 中。提供 S3 URI 和你的优化目标即可。示例提示：*"I want to find the cheapest instance type to deploy my fine-tuned model on SageMaker."（我想为微调模型找到在 SageMaker 上部署成本最低的实例类型。）*
- **来自 [Amazon SageMaker JumpStart](https://aws.amazon.com/sagemaker/jumpstart/) 的公开基础模型**：你想部署 JumpStart 目录中的基础模型（FM），提供模型 ID 即可。示例提示：*"Find the best instance for model huggingface-reasoning-qwen3-8b on SageMaker AI."（在 SageMaker AI 上为模型 huggingface-reasoning-qwen3-8b 找到最佳实例。）*
- **在 [Hugging Face Hub](https://huggingface.co/models) 上的模型**：你想使用托管在 Hugging Face 上的模型，提供模型名称即可。对于受访问限制的模型（gated models，如 Llama 系列），你的 agent 会展示许可条款，请你接受条款并提供你的 Hugging Face token。示例提示：*"I want to deploy a Llama model from Hugging Face Hub. What's the cheapest option?"（我想部署一个来自 Hugging Face Hub 的 Llama 模型。最便宜的方案是什么？）*

在每种情况下，你的 agent 都会生成代码，把模型放到候选实例和配置上评估，然后给出按序排列的部署选项，并附带具体的性能指标：吞吐、延迟分位数、首 token 时间和并发。你根据自己的成本和性能要求做选择。

### 比较基准测试运行

如果你跑了多个基准测试（例如配置变更前后，或在两种实例类型之间），可以让 agent 对它们进行比较。提供两个基准测试作业名，agent 就会生成一份对比，计算关键指标的差值：吞吐、延迟分位数和首 token 时间。

结果以百分比变化呈现，正值代表更好，让你得到一份单一、可读的总结：你的改动究竟提升了性能、恶化了性能，还是没有实质影响。

如果其中一个基准测试运行不存在，agent 会提出先运行它，然后再继续对比。

**示例提示：** *"I have two benchmark runs and I want to compare them. Which one is faster?"（我有两次基准测试结果，想对比一下。哪次更快？）*

## 基准测试结果

下表在同一基准负载（512/256 tokens，并发 4）下比较了两个已部署的模型。Δ% 列展示模型 B（Qwen3-8B）相对模型 A（Qwen3-1.7B）在每个指标上快多少，正值表示模型 B 更好。

| **指标** | **Qwen3-1.7B（模型 A）** | **Qwen3-8B（模型 B）** | **Δ%** |
| --- | --- | --- | --- |
| 输出 token 吞吐 | 188.2 tokens/s | 271.2 tokens/s | +44.1% ✅ |
| 每用户吞吐 | 47.5 tokens/s | 69.4 tokens/s | +45.9% ✅ |
| 请求吞吐 | 0.736 req/s | 1.08 req/s | +46.7% ✅ |
| Token 间延迟 | 20.9 ms | 14 ms | +33.0% ✅ |
| 请求延迟 | 5,382 ms | 3,658 ms | +32.0% ✅ |
| 首 token 时间 | 67.5 ms | 166.3 ms | −146.5% ❌ |

两个模型运行在不同硬件上。Qwen3-8B 使用一块 4-GPU 的 `ml.g5.12xlarge`（4x A10G），而 Qwen3-1.7B 使用单块 L4 GPU（`ml.g6.4xlarge`）。这些差值反映的约有 4 倍的算力差异，而不仅仅是模型本身的差异。

结论是：Qwen3-8B 带来约 44–47% 的更高吞吐和更低的端到端延迟，这主要归功于额外的 GPU 算力。Qwen3-1.7B 只在首 token 时间上占优——这正是更小模型配单 GPU 时预期中的优势。

## 综合来看

你不需要记住各个能力的名称，也不需要知道该请求哪个工作流。下表展示常见请求如何映射到结果。

| **你说** | **你得到** |
| --- | --- |
| "I already deployed a model and want to know how fast it is."（我已经部署了一个模型，想知道它有多快。） | 量化性能报告：来自真实负载的吞吐、延迟分位数和并发指标。 |
| "I have a model in S3 and I don't know what instance to deploy on."（我有一个模型在 S3 里，不知道该部署到什么实例上。） | 按序排列的部署选项，附每个候选配置的成本、吞吐和延迟。 |
| "I want to deploy a JumpStart model and find the cheapest instance. I only have the model ID."（我想部署一个 JumpStart 模型并找到最便宜的实例，我只有模型 ID。） | 按序排列的部署选项，无需 S3 中转（staging）。如需要，会给出受限模型的替代方案。 |
| "I ran a benchmark before and after a change. Which one is faster?"（我在改动前后各跑了一次基准测试，哪次更快？） | 覆盖所有指标的百分比变化，标明提升还是回退。 |
| "I want to optimize a Llama model from Hugging Face Hub."（我想优化一个来自 Hugging Face Hub 的 Llama 模型。） | 展示许可条款，把模型中转（staging）到 S3，然后给出标准推荐结果。 |

如果你的请求横跨多个能力（例如先把 Hugging Face 模型中转到位，再获取部署推荐），agent 会在同一个对话中自然地把它们串起来。

## 对 agent 行为的预期

配备了 `aws-ai-ml` 技能的 agent 遵循几条让体验可预测且安全的行为准则：

- **它会索取所需的信息。** 如果缺少信息（比如 endpoint 名称或 S3 URI），agent 会让你补充，而不是瞎猜。
- **在有影响的行动之前先确认。** 在运行会向线上 endpoint 施加真实流量的基准测试之前，agent 会警告影响并请求明确确认。
- **超出范围时会直说。** 如果你要求 agent 做它做不到的事（比如部署模型），它会解释自己能提供什么替代，例如生成你需要的部署配置。
- **它生成的是 SageMaker Python SDK v3 代码。** 每份输出都是可执行的代码，你可以在自己的环境中检查、修改并运行。

## 清理资源

为避免持续产生费用，请删除你创建的资源：

- [删除 SageMaker AI endpoint](https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints-delete.html)：基准测试或推荐过程中创建的 endpoint。
- [停止或删除你的 JupyterLab space](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-updated-jl-user-guide-shutdown.html)：如果你使用了 SageMaker Studio。
- [移除 S3 对象](https://docs.aws.amazon.com/AmazonS3/latest/userguide/DeletingObjects.html)：基准测试和推荐作业存放在你的 SageMaker AI 默认 bucket 中的对象。

## 结语

面向 Amazon SageMaker AI 优化生成式 AI 推理的 `aws-ai-ml` 技能，把你现有的 coding agent 变成 SageMaker AI 推理优化专家。无论你是要对线上 endpoint 做基准测试、为模型寻找最便宜的实例、比较配置，还是把 Hugging Face 模型中转到位做评估，只需要描述你想要什么，agent 就能交付可度量的结果。

要开始使用，请通过 [Agent Toolkit for AWS](https://aws.amazon.com/products/developer-tools/agent-toolkit-for-aws/) 安装技能并添加到你已在用的 coding agent，或者在 Amazon SageMaker Studio 中启动一个预配置的 JupyterLab space。更多信息参见 [Amazon SageMaker AI 文档](https://docs.aws.amazon.com/sagemaker/latest/dg/whatis.html)。
