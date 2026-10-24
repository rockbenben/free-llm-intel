---
vendor: deepinfra
title: Granite 4.2 8B：模型概述与集成指南
original_title: Granite 4.2 8B: Model Overview & Integration Guide
url: https://deepinfra.com/blog/granite-4-2-8b-model-overview-integration-guide
date: 2026-10-21
lang: zh
captured: 2026-10-24
extractor: readability-v1
translator: agent
status: translated
body_sha: 38f20f257e05
---

# Granite 4.2 8B：模型概述与集成指南

发布于 2026.10.21，作者 DeepInfra

![Granite 4.2 8B：模型概述与集成指南](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/10/Granite-4.2-Model-Integration-Guide.png)

[Granite 4.2 8B](https://deepinfra.com/ibm-granite/granite-4.2-8b) 是 IBM 开发的 80 亿参数稠密 Transformer 推理模型。作为 Granite 4.2 系列中的中等规模成员，它在推理深度与运行效率之间取得平衡。

该模型以 Apache 2.0 许可证发布，专为复杂推理、代码生成、工具调用和结构化数据输出而构建。

它最具决定性的特性是原生思维链推理。Granite 4.2 8B 在给出最终答案之前，会在 *<think>…</think>* 标签内逐步进行逻辑处理。

这支撑了需要深度逻辑的应用，例如数学问题求解、agentic 工作流和软件工程任务。

## **能力与性能**

### **原生推理与灵活的思考模式**

为了让开发者掌控延迟与计算深度，该模型支持三种思考模式，可按每次查询单独切换：

- **完整思考（默认）：** 为复杂查询最大化推理深度，并生成完整的思维链 token
- **低耗力思考：** 为较简单的查询提供简短推理，降低首 token 时间
- **非思考：** 完全关闭推理阶段，以获得尽可能低的延迟

### **基准测试**

该模型已在推理、知识、指令遵循和编码任务上接受测试：

| **类别** | **基准** | **分数** | **指标** |
| --- | --- | --- | --- |
| 推理 | AIME 2025 | 86.67 | 准确率 |
| 推理 | GPQA | 64.14 | 准确率 |
| 知识 | MMLU-Pro | 74.04 | 准确率 |
| 指令遵循 | Arena-Hard-V2 | 65.19 | 分数 |
| 编码 | SWE-Bench Verified | 47.67 | 已解决 Issue 数 |

与 Granite 4.2 3B 相比，8B 变体提供更强的推理深度。与 30B 旗舰版本相比，它仍然更节省资源，因此成为企业部署中的中间选项。

### **上下文窗口与多语言支持**

Granite 4.2 8B 原生支持 128K token 上下文窗口，针对长上下文任务可扩展到 512K token。

这使它能够分析长文档和大型代码库。

该模型官方支持 12 种语言，包括英语、法语、日语、阿拉伯语、西班牙语和中文。

## **API 快速上手**

Granite 4.2 8B 托管在 DeepInfra 上，提供兼容 OpenAI 的接口，可集成进现有工作流。

### **身份验证**

API 需要一个 DeepInfra API key。请把它作为 bearer token 放入 HTTP Authorization 请求头：

Authorization: Bearer <YOUR_DEEPINFRA_API_KEY>

Content-Type: application/json

### **API 端点基础**

- **Base URL：** https://api.deepinfra.com/v1/openai
- **路径：** /chat/completions
- **模型标识符：** ibm-granite/granite-4.2-8b

### **cURL 示例**

```
curl -X POST "https://api.deepinfra.com/v1/openai/chat/completions" \

  -H "Authorization: Bearer $DEEPINFRA_API_KEY" \

  -H "Content-Type: application/json" \

  -d '{

    "model": "ibm-granite/granite-4.2-8b",

    "messages": [

      {"role": "user", "content": "Solve: If a store sells 12 pens for $18, how much do 30 pens cost?"}

    ],

    "temperature": 0.7

  }'copy
```

### **Python 示例**

```
import os

import requests

api_key = os.environ.get("DEEPINFRA_API_KEY")

url = "https://api.deepinfra.com/v1/openai/chat/completions"

payload = {

    "model": "ibm-granite/granite-4.2-8b",

    "messages": [

        {"role": "system", "content": "Be a helpful assistant."},

        {"role": "user", "content": "Write a Python function to check if a string is a palindrome."}

    ],

    "temperature": 0.7,

    "max_tokens": 1024

}

response = requests.post(url, headers={"Authorization": f"Bearer {api_key}"}, json=payload)

print(response.json())copy
```

## **配置与参数**

API 支持以下参数来微调模型行为：

| **参数** | **类型** | **默认值** | **描述** |
| --- | --- | --- | --- |
| max_tokens | integer | 未设置 | 要生成的最大新 token 数，受模型上下文长度限制 |
| temperature | float | 1 | 控制随机性（0 为确定性输出，值越高越有创造性） |
| top_p | float | 1 | 核采样（nucleus sampling）概率截断 |
| repetition_penalty | float | 1 | 抑制重复文本生成 |
| stop | array | 未设置 | 使 token 生成停止的序列 |
| response_format | object | text | 设为 json_object 或 json_schema 以输出结构化 JSON |
| tools / tool_choice | array / string | 未设置 | 定义可调用函数并控制工具调用 |
| prompt_cache_key | string | 未设置 | 用于跨请求复用已缓存提示词状态的显式键 |

*tools / tool_choice* 参数让[工具调用](https://deepinfra.com/blog/deepinfra-function-calling-guide)得以工作：模型决定调用哪个函数，并提供符合该函数 schema 的参数。

*response_format* 参数则是你请求可靠的[结构化数据输出](https://deepinfra.com/blog/json-mode)、而非自由格式文本的方式。

### **响应格式**

由于 Granite 4.2 8B 是推理模型，[响应中的 content 字段](https://deepinfra.com/blog/deepinfra-json-only-responses)会先包含推理步骤，再给出最终答案：

```
{

  "choices": [

    {

      "message": {

        "role": "assistant",

        "content": "<think>\n12 pens cost $18, so 1 pen is $1.50. 30 * $1.50 = $45.\n</think>\n30 pens will cost $45."

      }

    }

  ]

}copy
```

## **定价与用量**

DeepInfra 按 [token 计费](https://deepinfra.com/blog/inference-economics-ai-costs-at-scale)为 Granite 4.2 8B 定价：

- **输入 token：** 每 100 万 token 0.06 美元
- **输出 token：** 每 100 万 token 0.25 美元
- [**提示词缓存：**](https://deepinfra.com/blog/pricing-101-token-math-cost-per-completion) 每 100 万缓存 token 0.015 美元，可降低重复系统提示词或大型上下文窗口的成本

私有端点部署和专属托管可用于高流量的企业需求。

## **技术背景**

Granite 4.2 8B 以 Granite 4.1 8B Base 为基础，通过三阶段流水线后训练而成。最后阶段使用了 Group Relative Policy Optimization（一种强化学习技术），运行在 NVIDIA GB200 NVL72 集群上。

这一训练支撑了 IBM 所称的[推理增强型工具调用](https://deepinfra.com/blog/function-calling-feature)：模型会推理该用哪个工具、以及为什么它适合当前任务。

## **DeepInfra 上的相关模型**

Granite 4.2 8B 与 DeepInfra 上其他擅长工具调用和 agentic 工作负载的高效模型并列：

- [**Gemma 4 26B A4B IT:**](https://deepinfra.com/google/gemma-4-26B-A4B-it) 一个 Mixture-of-Experts 模型，总参数 25.2B、激活参数 3.8B。它提供 262,144 token 上下文窗口，支持 JSON 输出、函数调用和多模态输入
- [**Qwen3.6-35B-A3B:**](https://deepinfra.com/Qwen/Qwen3.6-35B-A3B) 一个多模态 Mixture-of-Experts 模型，总参数 35B、激活参数 3B，原生支持 262,144 token 上下文窗口
- [**GLM-5.3-Flash:**](https://deepinfra.com/zai-org/GLM-5.3-Flash) 一个原生多模态模型，上下文窗口 1,048,576 token，支持 JSON 输出和函数调用
- [**DeepSeek-V4-Flash-0731:**](https://deepinfra.com/deepseek-ai/DeepSeek-V4-Flash-0731) 一个上下文窗口 1,048,576 token 的模型，支持 JSON 输出和函数调用

## **结论**

Granite 4.2 8B 在轻量高效与深度逻辑处理之间架起桥梁。原生思维链、大上下文窗口和灵活的思考模式，使它适合 [agentic 工作流](https://deepinfra.com/blog/decision-models-ai-agent-infrastructure)和企业编码任务。

要点：

- **推理：** 在 AIME 2025 和 SWE-Bench Verified 上得分强劲
- **灵活性：** 可在完整推理与低延迟模式之间切换
- **成本：** 按用量计费，并提供提示词缓存折扣

获取 API key，试用 [DeepInfra 上的 Granite 4.2 8B](https://deepinfra.com/ibm-granite/granite-4.2-8b)。

相关文章

[![DeepSeek V4 Pro：模型概述、特性与性能指南](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/04/deepseek-v4-pro.png)](https://deepinfra.com/blog/deepseek-v4-pro-model-overview)[DeepSeek V4 Pro：模型概述、特性与性能指南](https://deepinfra.com/blog/deepseek-v4-pro-model-overview)<p>DeepSeek V4 Pro 是 DeepSeek 的 1.6 万亿参数 Mixture-of-Experts（MoE）模型，于 2026 年 4 月 24 日在 MIT 许可证下发布。它面向高级推理、复杂软件工程和长时间运行的 agentic 任务而设计，并与 DeepSeek-V4-Flash 一同推出——后者是更轻的 284B 参数变体，专为更快、更低成本的推理打造。V4 系列是 DeepSeek 首个双层产品线 [&hellip;]</p>

[![解读 DeepSeek 的 102.9 亿美元融资](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/07/deepseek-1029-round-1024x725.png)](https://deepinfra.com/blog/deepseeks-upcoming-round)[解读 DeepSeek 的 102.9 亿美元融资](https://deepinfra.com/blog/deepseeks-upcoming-round)<p>自 2023 年成立以来，DeepSeek 从未拿过外部资金。两年间，它拒绝了所有登门拜访的风险投资机构和大型科技公司，研究经费完全来自其母公司对冲基金 Zhejiang High-Flyer Asset Management 的收益，据报道该基金 2025 年的回报率为 56.6%。那个时代 [&hellip;]</p>

[![Wan 3.0 API 基准测试：速度、延迟与成本](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/10/api.png)](https://deepinfra.com/blog/wan-3-0-api-benchmarks)[Wan 3.0 API 基准测试：速度、延迟与成本](https://deepinfra.com/blog/wan-3-0-api-benchmarks)<p>关键要点 Wan 是阿里巴巴的视频生成模型系列。较早的 Wan2.2 模型以 Apache 2.0 开放权重形式发布，而 Wan2.6、Wan2.7 和 Wan3.0 等后续版本则通过托管 API 提供。Wan 3.0 是首个接受文档和网页作为输入的 Wan 模型。它还把最大 [&hellip;]</p>

[查看全部](https://deepinfra.com/blog)
