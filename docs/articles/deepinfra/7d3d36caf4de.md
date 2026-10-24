---
vendor: deepinfra
title: Granite 4.2 8B: Model Overview & Integration Guide
original_title: 
url: https://deepinfra.com/blog/granite-4-2-8b-model-overview-integration-guide
date: 2026-10-21
lang: zh
captured: 2026-10-23
extractor: readability-v1
translator: mt
status: translated
body_sha: 76266a8874b7
---

# Granite 4.2 8B：模型概述和集成指南

DeepInfra 发布于 2026.10.21

![Granite 4.2 8B：模型概述和集成指南](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/10/Granite-4.2-Model-Integration-Guide.png)

[Granite 4.2 8B](https://deepinfra.com/ibm-granite/granite-4.2-8b)是IBM开发的80亿参数密集变压器推理模型。作为 Granite 4.2 系列的中型成员，它平衡了推理深度和运行效率。

该模型在 Apache 2.0 许可下发布，专为复杂推理、代码生成、工具调用和结构化数据输出而构建。

它的定义特征是本机思维链推理。 Granite 4.2 8B 在产生最终答案之前在 *<think>...</think>* 标签内执行逐步逻辑处理。

这支持需要深层逻辑的应用程序，例如数学问题解决、代理工作流程和软件工程任务。

## **功能和性能**

### **原生推理和灵活的思维模式**

为了让开发人员能够控制延迟和计算深度，该模型支持三种思维模式，可以根据每个查询进行切换：

- **完整思考（默认）：**最大化复杂查询的推理深度并生成全面的思想链标记
- **省力思维：**为更简单的查询提供简要推理，减少获得第一个令牌的时间
- **非思考：**完全禁用推理阶段，以尽可能降低延迟

### **基准**

该模型已经过推理、知识、指令遵循和编码任务的测试：

| **类别** | **基准** | **分数** | **公制** |
| --- | --- | --- | --- |
|推理| AIME 2025 | 86.67 |准确度|
|推理| GPQA | 64.14 |准确度|
|知识 | MMLU-专业版 | 74.04 |准确度|
|遵循说明 | Arena-Hard-V2 | 65.19 | 65.19分数 |
|编码 | SWE-Bench 验证 | 47.67 | 47.67已解决的问题 |

与 Granite 4.2 3B 相比，8B 变体提供了更大的推理深度。与 30B 旗舰产品相比，它仍然具有更高的资源效率，使其成为企业部署的中间选择。

### **上下文窗口和多语言支持**

Granite 4.2 8B 原生支持 128K 令牌上下文窗口，可扩展至 512K 令牌以执行长上下文任务。

这使得它能够分析长文档和大型代码库。

该模型官方支持英语、法语、日语、阿拉伯语、西班牙语、中文等12种语言。

## **API 入门**

Granite 4.2 8B 托管在 DeepInfra 上，具有 OpenAI 兼容接口，可集成到现有工作流程中。

＃＃＃ **验证**

该 API 需要 DeepInfra API 密钥。将其作为不记名令牌包含在 HTTP 授权标头中：

授权：持有者 <YOUR_DEEPINFRA_API_KEY>

内容类型：application/json

### **API 端点基础知识**

- **基本 URL：** https://api.deepinfra.com/v1/openai
- **路径：** /chat/completions
- **型号标识符：** ibm-granite/granite-4.2-8b

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
## **配置和参数**

API 支持以下参数来微调模型行为：

| **参数** | **类型** | **默认** | **描述** |
| --- | --- | --- | --- |
|最大令牌数 |整数 |未设置 |生成的最大新令牌数，由模型的上下文长度限制 |
|温度|浮动| 1 |控制随机性（0 是确定性的，越高越有创意）|
|顶部_p |浮动| 1 |核采样概率截止|
|重复惩罚 |浮动| 1 |阻止重复的文本生成 |
|停止|数组|未设置|停止令牌生成的序列 |
|响应格式 |对象|文字|设置为 json_object 或 json_schema 以获取结构化 JSON 输出 |
|工具/工具选择|数组/字符串 |未设置|定义可调用函数并控制工具调用 |
|提示缓存键 |字符串|未设置|用于跨请求重用缓存的提示状态的显式密钥 |

*tools / tool_choice* 参数使[工具调用](https://deepinfra.com/blog/deepinfra-function-calling-guide)起作用：模型决定调用哪个函数并提供与其模式匹配的参数。

*response_format* 参数是您请求可靠的[结构化数据输出](https://deepinfra.com/blog/json-mode)而不是自由格式文本的方式。

### **响应格式**

由于 Granite 4.2 8B 是一个推理模型，[响应中的内容字段](https://deepinfra.com/blog/deepinfra-json-only-responses) 包括推理步骤和最终答案：
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
## **定价和使用**

DeepInfra 按[每个代币]对 Granite 4.2 8B 进行定价(https://deepinfra.com/blog/inference-economics-ai-costs-at-scale)：

- **输入代币：** 每 100 万个代币 0.06 美元
- **输出代币：** 每 100 万个代币 0.25 美元
- [**提示缓存：**](https://deepinfra.com/blog/pricing-101-token-math-cost-per-completion) 每 100 万个缓存令牌 0.015 美元，这降低了重复系统提示或大型上下文窗口的成本

专用端点部署和专用托管可满足大批量企业需求。

## **技术背景**

Granite 4.2 8B 是使用三级管道从 Granite 4.1 8B Base 进行后训练的。最后阶段使用了组相对策略优化（一种强化学习技术），在 NVIDIA GB200 NVL72 集群上运行。

此训练支持 IBM 所谓的“推理增强工具调用”(https://deepinfra.com/blog/function-calling-feature)，其中模型会推理要使用哪个工具以及为什么它适合任务。

## **DeepInfra 上的相关模型**

Granite 4.2 8B 与 DeepInfra 上的其他高效模型一起处理工具调用和代理工作负载：

- [**Gemma 4 26B A4B IT:**](https://deepinfra.com/google/gemma-4-26B-A4B-it) 一个专家混合模型，总参数为 25.2B，活动参数为 3.8B。它提供了 262,144 个令牌上下文窗口，并支持 JSON 输出、函数调用和多模式输入
- [**Qwen3.6-35B-A3B:**](https://deepinfra.com/Qwen/Qwen3.6-35B-A3B) 一个多模式专家混合模型，具有 35B 总数和 3B 活动参数以及原生 262,144 个令牌上下文窗口
- [**GLM-5.3-Flash:**](https://deepinfra.com/zai-org/GLM-5.3-Flash) 具有 1,048,576 个令牌上下文窗口并支持 JSON 输出和函数调用的本机多模式模型
- [**DeepSeek-V4-Flash-0731:**](https://deepinfra.com/deepseek-ai/DeepSeek-V4-Flash-0731) 具有 1,048,576 个令牌上下文窗口并支持 JSON 输出和函数调用的模型

## **结论**

Granite 4.2 8B 连接轻量级效率和深度逻辑处理。其原生思维链、大上下文窗口和灵活的思维模式使其适合[代理工作流程](https://deepinfra.com/blog/decision-models-ai-agent-infrastructure)和企业编码任务。

要点：

- **推理：** AIME 2025 和 SWE-Bench Verified 上的高分
- **灵活性：** 在完全推理和低延迟模式之间切换
- **成本：** 基于使用情况的定价，并提供及时的缓存折扣

获取 API 密钥并尝试 [DeepInfra 上的 Granite 4.2 8B](https://deepinfra.com/ibm-granite/granite-4.2-8b)。

相关文章

[![DeepSeek V4 Pro：模型概述、功能和性能指南](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/04/deepseek-v4-pro.png)](https://deepinfra.com/blog/deepseek-v4-pro-model-overview)[DeepSeek V4 Pro：模型概述、功能和性能指南](https://deepinfra.com/blog/deepseek-v4-pro-model-overview)<p>DeepSeek V4 Pro 是 DeepSeek 的 1.6 万亿参数 Mixture-of-Experts (MoE) 模型，于 2026 年 4 月 24 日在 MIT 许可下发布。它专为高级推理、复杂的软件工程和长时间运行的代理任务而设计，并与 DeepSeek-V4-Flash 一起推出，这是一种更轻的 284B 参数变体，专为更快、更低成本的推理而设计。 V4 系列是 DeepSeek 的第一个两层阵容 [...]</p>

[![DeepSeek 的 10.29B 美元融资轮解释](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/07/deepseek-1029-round-1024x725.png)](https://deepinfra.com/blog/deepseeks-upcoming-round)[DeepSeek 的 10.29B 美元融资融资轮解释](https://deepinfra.com/blog/deepseeks-upcoming-round)<p>自 2023 年成立以来，DeepSeek 从未接受过外部资金。两年来，它拒绝了每一家来电的风险投资公司和大型科技公司，其研究资金完全来自其母对冲基金浙江汉飞资产管理公司的回报，据报道，该基金 2025 年的回报率为 56.6%。那个时代 […]</p>

[![Wan 3.0 API 基准：速度、延迟和成本](https://deepinfrabldev.wpenginepowered.com/wp-content/uploads/2026/10/api.png)](https://deepinfra.com/blog/wan-3-0-api-benchmarks)[Wan 3.0 API 基准：速度、延迟和成本成本](https://deepinfra.com/blog/wan-3-0-api-benchmarks)<p>关键要点 Wan 是阿里巴巴的视频生成模型系列。早期的 Wan2.2 模型在 Apache 2.0 下作为开放权重提供，而后来的版本（例如 Wan2.6、Wan2.7 和 Wan3.0）则通过托管 API 提供。 Wan 3.0是第一个接受文档和网页作为输入的Wan模型。它还使最大值加倍[...]</p>

[查看全部](https://deepinfra.com/blog)
