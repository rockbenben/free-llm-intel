---
vendor: openai
title: Agents SDK 的全新演进
original_title: 
url: https://openai.com/index/the-next-evolution-of-the-agents-sdk
date: 2026-10-02
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: native
status: translated
body_sha: a27a18eaaf35
---

OpenAI

2026年4月15日


# Agents SDK 的全新演进

新版 Agents SDK 助力开发者打造更具行动力的智能体。这些智能体能够在受控的沙箱环境中执行文件审查、运行指令、编辑代码，并能够胜任长周期、跨阶段的复杂任务


我们正在为 Agents SDK 引入全新功能，旨在为开发者提供一套标准化且易上手的底层架构。这套架构专为 OpenAI 模型量身打造，包含一个模型原生运行框架 (model-native harness)，支持智能体在计算机上跨文件、跨工具作业；同时，它还配套了原生沙箱执行环境，以确保各类任务的运行安全性。

例如，开发者可以为智能体分配一个受控的工作空间、明确的指令集，以及审查证据所需的必要工具：

#### Python

```
1# pip install "openai-agents>=0.14.0"23import asyncio4import tempfile5from pathlib import Path67from agents import Runner8from agents.run import RunConfig9from agents.sandbox import Manifest, SandboxAgent, SandboxRunConfig10from agents.sandbox.entries import LocalDir11from agents.sandbox.sandboxes import UnixLocalSandboxClient121314async def main() -> None:15    with tempfile.TemporaryDirectory() as tmp:16        dataroom = Path(tmp) / "dataroom"17        dataroom.mkdir()18        (dataroom / "metrics.md").write_text(19            """# Annual metrics2021| Year | Revenue | Operating income | Operating cash flow |22| --- | ---: | ---: | ---: |23| FY2025 | $124.3M | $18.6M | $24.1M |24| FY2024 | $98.7M | $12.4M | $17.9M |25""",26            encoding="utf-8",27        )2829        agent = SandboxAgent(30            name="Dataroom Analyst",31            model="gpt-5.4",32            instructions="Answer using only files in data/. Cite source filenames.",33            default_manifest=Manifest(entries={"data": LocalDir(src=dataroom)}),34        )3536        result = await Runner.run(37            agent,38            "Compare FY2025 revenue, operating income, and operating cash flow with FY2024.",39            run_config=RunConfig(40                sandbox=SandboxRunConfig(client=UnixLocalSandboxClient()),41            ),42        )43        print(result.final_output)444546if __name__ == "__main__":47    asyncio.run(main())48
```

开发者若想打造真正实用的智能体，仅凭顶尖模型远不足够。他们还需要一套完备的系统，来支撑智能体执行文件审查、运行指令、编写代码以及跨步骤的长效协作。

然而，现有的系统在从原型开发迈向生产环境的过程中，往往面临各种权衡：模型无关框架虽然灵活，但无法充分释放前沿模型的性能潜力；模型厂商提供的 SDK 虽然与模型契合度更高，但通常对运行框架 (harness) 内部的可见性不足；而托管型智能体 API 虽能简化了部署，却限制了智能体的运行环境及对敏感数据的访问权限。

以下是部分参与新 SDK 测试的客户反馈：

## 性能更强劲的智能体循环运行框架

随着今日版本的发布，Agents SDK 运行框架 (harness) 为处理文档、文件和系统的智能体提供了更强的能力。该运行框架目前已集成可配置记忆模块、沙箱感知编排功能、类 Codex 的文件系统工具，以及针对前沿智能体系统常用原语 (primitive) 的标准化集成。

这些原语包括：通过 [MCP⁠（在新窗口中打开）](https://modelcontextprotocol.io) 实现的工具使用、通过[技能 (skill) ⁠（在新窗口中打开）](https://agentskills.io)实现的渐进式功能披露、通过 [AGENTS.md⁠（在新窗口中打开）](https://agents.md) 实现的自定义指令，以及利用 [shell⁠（在新窗口中打开）](https://developers.openai.com/api/docs/guides/tools-shell) 工具执行代码和通过 [apply patch⁠（在新窗口中打开）](https://developers.openai.com/api/docs/guides/tools-apply-patch) 工具编辑文件等。该运行框架将持续吸纳新的智能体模式与原语，旨在让开发者从繁琐的核心架构维护中解脱出来，将精力集中在决定智能体实用性的领域特定逻辑上。

此外，该运行框架通过将执行方式与前沿模型的最佳性能模式对齐，帮助开发者进一步释放模型潜力。这种设计使智能体能更贴合模型的“自然运行模式”，从而在执行复杂任务时 — 尤其是那些需要跨多种工具系统协作的工作或长周期任务 — 表现出更卓越的可靠性与性能。

同时，我们深知每款产品都各具特色，很难用统一的模板涵盖。因此，Agents SDK 在设计之初就充分考虑了多样性需求。它为开发者提供了一个既能开箱即用又具备高度灵活性的运行框架，支持开发者根据自身的技术栈轻松定制工具调用、记忆模块及沙箱环境。

## 原生沙箱执行环境

升级后的 Agents SDK 现已原生支持沙箱执行。这意味着智能体可以在受控的计算机环境中运行，并配备任务所需的全部文件、工具及依赖项。

对于许多实用的智能体而言，一个能够安全读写文件、安装依赖、运行代码及调用工具的工作空间至关重要。原生沙箱支持为开发者直接提供了这一执行层，无需再费力自行搭建。

开发者既可以接入自有的沙箱，也能直接使用 SDK 支持的第三方平台，包括 Blaxel、Cloudflare、Daytona、E2B、Modal、Runloop 以及 Vercel。

为了确保环境在不同服务商之间具备可移植性，SDK 还引入了 Manifest 抽象层来定义智能体的工作空间。开发者可以挂载本地文件、定义输出目录，并从 AWS S3、Google Cloud Storage、Azure Blob Storage 及 Cloudflare R2 等存储服务商处导入数据。

这套方案为开发者提供了一种标准化的方式，助力智能体从本地原型平滑过渡到生产部署。同时，它也为模型提供了一个可预测的工作空间：明确输入来源、输出位置，并确保在长周期任务中始终保持作业的井然有序。

## 实现运行框架与算力的解耦，确保安全性、持久性与可扩展性

在设计智能体系统时，必须预先考虑到提示注入 (prompt-injection) 和数据外泄 (exfiltration) 的潜在风险。通过将运行框架与算力环境解耦，可以有效确保凭据等敏感信息不会泄露至执行模型生成代码的环境中。

此外，这种架构还能实现持久化执行。由于智能体的状态已被外部化，即使沙箱容器发生宕机，也不会导致整个任务运行失败。凭借内置的快照 (snapshotting) 与重构 (rehydration) 机制，Agents SDK 可以在原环境失效或过期时，在全新的容器中精准恢复智能体状态，并从最后一个检查点继续运行。

最后，这一设计极大地提升了智能体的可扩展性。在执行任务时，智能体可以灵活调用一个或多个沙箱，仅在必要时激活环境，将子智能体 (sub-agent) 路由至隔离环境中，并通过跨容器的并行作业来显著提升执行效率。

## 定价与可用性

Agents SDK 的这些全新功能现已面向所有 API 用户开放。定价方案沿用标准 API 计费模式，根据 Token 使用量及工具调用次数进行结算。

## 未来展望

在 Agents SDK 的持续迭代中，我们将不断拓宽其应用边界，助力开发者以更轻量化的基础设施，将性能更强的智能体投入生产。与此同时，我们将始终保障开发者所需的灵活性与掌控力，确保智能体能够完美契合各类自定义环境。

目前，全新的运行框架与沙箱功能已率先在 Python 版本中上线，TypeScript 支持也已列入发布计划。此外，我们正致力于将包括代码模式和子智能体在内的更多智能体功能引入这两个语言版本。

展望未来，我们希望进一步推动智能体生态的深度融合：通过支持更多的沙箱服务商、提供更丰富的集成方案，以及探索更多元化的接入方式，让开发者能够将 SDK 无缝嵌入其现有的工具链与系统之中。

- [2026 年](https://openai.com/news/?tags=2026)
- [API 平台](https://openai.com/news/?tags=api-platform)

## 作者

OpenAI








