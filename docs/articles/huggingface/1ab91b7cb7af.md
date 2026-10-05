---
vendor: huggingface
title: Swift Transformers 达到 1.0 并展望未来
original_title: Swift Transformers Reaches 1.0
url: https://huggingface.co/blog/swift-transformers
date: 2025-09-26
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: ok
body_sha: d2eaeb5f2773
---

# Swift Transformers 达到 1.0 并展望未来

两年前（！）我们发布了 [`swift-transformers`](https://github.com/huggingface/swift-transformers)，目标是支持 Apple 开发者、帮助他们把本地 LLM 集成进自己的应用。这两年变化很大（那时 MLX 和聊天模板还不存在！），我们也看清了社区实际怎么用这个库。

我们想在最能惠及社区的场景上加倍投入，为未来打下地基。剧透：这次发布之后，我们会重点押注 MLX 与智能体（agentic）场景 🚀

## `swift-transformers` 是什么

`swift-transformers` 是一个 Swift 库，[旨在降低](https://huggingface.co/blog/swift-coreml-llm)在 Apple Silicon 平台（包括 iPhone）上使用本地模型的开发摩擦。它补上了 Core ML 或 MLX 不提供、但本地推理又必需的那几块拼图，包含以下组件：

- `Tokenizers`。为语言模型准备输入比想象中复杂得多。我们在 Python 和 Rust 的 `tokenizers` 库上积累了大量经验——它们是 AI 生态的基石。我们想把同样高性能、顺手的使用体验带到 Swift。Swift 版 `Tokenizers` 应该替你搞定一切，包括聊天模板和智能体场景！
- `Hub`。这是通往 [Hugging Face Hub](https://huggingface.co) 的接口——所有开放模型都在这里。它支持从 Hub 下载模型并本地缓存，支持后台断点续传、模型更新、离线模式。它提供 [Python](https://huggingface.co/docs/huggingface_hub/en/index) 和 [JavaScript](https://huggingface.co/docs/huggingface.js/en/hub/README) 库功能的子集，聚焦 Apple 开发者最需要的任务（例如不支持上传）。
- `Models` 与 `Generation`。这是为转换到 Core ML 格式的 LLM 准备的封装。模型转换不在库的职责范围内（但[我们写了一些指南](https://huggingface.co/blog/mistral-coreml)）。转换完成后，这些模块让推理跑起来非常轻松。

mlx-swift-examples 的测试应用：SmolVLM2 正在讲解视频里的动作。

## 社区怎么用它

多数时候大家用的是 `Tokenizers` 或 `Hub` 模块，而且经常两个都用。一些依赖 `swift-transformers` 的知名项目：

- [`mlx-swift-examples`](https://github.com/ml-explore/mlx-swift-examples)，Apple 出品。它其实不只是示例合集，更是一套可以用 MLX 运行各类模型（包括 LLM 和 VLM 视觉语言模型）的库。可以理解为 MLX 版的 `Models` 和 `Generation`——而且支持的模型类型多得多，比如嵌入模型、Stable Diffusion。
- [WhisperKit](https://github.com/argmaxinc/WhisperKit/)，[argmax](https://www.argmaxinc.com) 出品。开源 ASR（语音识别）框架，为 Apple Silicon 深度优化。它依赖我们的 `Hub` 和 `Tokenizers` 模块。
- [FastVLM](https://github.com/apple/ml-fastvlm/tree/main/app)，Apple 出品；还有大量其他应用演示，比如我们自己的 [SmolVLM2 原生应用](https://huggingface.co/blog/smolvlm2)。

## v1.0 改变了什么

1.0 版本标志着包的稳定。开发者正在基于 swift-transformers 构建应用，这个首个大版本承认了这些真实用途，让版本号与现实相符。它也为接下来和社区一起打造新功能奠定了基础。我们最得意的更新包括：

- **`Tokenizers` 和 `Hub`** 现在是[一等公民的顶层模块](https://github.com/huggingface/swift-transformers/pull/269)。1.0 之前你必须依赖并导入整个包，现在可以只挑 `Tokenizers` 用。
- 说到 Jinja，我们无比自豪地宣布：我们与 [John Mai](https://huggingface.co/JohnMai)（[X](https://x.com/JohnMai_Dev)）合作打造了他那款出色 Swift Jinja 库的**新版本**。John 的工作对社区至关重要：他单枪匹马扛起大梁，提供了一个能随聊天模板愈发复杂而成长的坚实模板库。新版本快了大约两个数量级（不开玩笑），现在以 [`swift-jinja`](https://github.com/huggingface/swift-jinja) 安家。
- 为降低对下游用户的负担，我们**移除了示例 CLI 目标和 `swift-argument-parser` 依赖**——这同时也避免了已使用该库的项目发生版本冲突。
- 感谢 Apple 的贡献，我们[采用了**现代 Core ML API**](https://github.com/huggingface/swift-transformers/pull/257)，支持有状态模型（KV 缓存更省心）和表达力丰富的 `MLTensor` API——删掉了数千行自定义张量运算和数学代码。
- 大量**杂物清理与 [API 面收窄](https://github.com/huggingface/swift-transformers/pull/250)**，降低认知负担、加快迭代。
- **测试**变得[更好、更快、更强](https://github.com/huggingface/swift-transformers/pull/229)。
- 为[公共 API](https://github.com/huggingface/swift-transformers/pull/268)补充了**文档注释**。
- 完整支持 **Swift 6**（[PR](https://github.com/huggingface/swift-transformers/pull/264)）。

1.0 包含破坏性 API 变更。不过，如果你只用 `Tokenizers` 或 `Hub`，我们预计不会遇到大问题。如果你使用库中的 Core ML 组件，请[联系我们](https://github.com/huggingface/swift-transformers/issues/new)，我们会在迁移期提供支持。我们会准备迁移指南并放进文档。

## 用法示例

下面演示如何用 `Tokenizers` 为 LLM 组织工具调用（tool calling）输入：

```
import Tokenizers

let tokenizer = try await AutoTokenizer.from(pretrained: "mlx-community/Qwen2.5-7B-Instruct-4bit")

let weatherTool = [
    "type": "function",
    "function": [
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": [
            "type": "object",
            "properties": ["location": ["type": "string", "description": "City and state"]],
            "required": ["location"]
        ]
    ]
]

let tokens = try tokenizer.applyChatTemplate(
    messages: [["role": "user", "content": "What's the weather in Paris?"]],
    tools: [weatherTool]
)
```

更多示例请看 [README 的这一节](https://github.com/huggingface/swift-transformers?#examples)和 [Examples 目录](https://github.com/huggingface/swift-transformers/tree/main/Examples)。

## 接下来做什么

说实话，我们也不知道。但我们确信对探索 MLX 兴趣浓厚——那通常是开发者在原生应用里上手 ML 的首选路线，我们想把这份体验做到尽可能顺滑。我们的思路包括与 `mlx-swift-examples` 在 LLM 和 VLM 上做得更紧密，比如处理开发者最常遇到的预处理与后处理环节。

我们对智能体场景——特别是 MCP——同样兴奋不已。我们觉得，把系统资源开放给本地工作流，那将非常 🚀。

想跟着这段旅程、或者想分享你的想法，请通过社交媒体或[仓库 issue](https://github.com/huggingface/swift-transformers/issues/new) 联系我们。

## 没有你们就没有这一切 🫵

深深感谢所有贡献者和用户给予的帮助与反馈。爱你们所有人，迫不及待继续与你们一起塑造端侧生成的未来！❤️
