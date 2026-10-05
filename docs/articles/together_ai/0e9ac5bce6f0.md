---
vendor: together_ai
title: Kimi K3：完整开发者指南
original_title: "Kimi K3: the complete developer guide"
url: https://www.together.ai/blog/kimi-k3-guide
date: 2026-08-01
lang: zh
captured: 2026-10-05
extractor: readability-v1
translator: agent
status: translated
---

# Kimi K3：完整开发者指南

在 Together AI API 上运行 Moonshot AI 的 2.8T 开放权重模型所需的一切：基准、定价与可复制粘贴的代码。

## 你将学到

- Kimi K3 是什么，它有何不同？
- 底层构造：KDA、Attention Residuals 与 Stable LatentMoE 架构
- 如何使用推理强度、流式、工具、视觉与 1M 上下文？
- 如何从第一个 API 调用走向生产？
- Kimi K3 在编码与 agentic 基准上与前沿相比如何？
- Kimi K3 在 Together AI 上多少钱？

Kimi K3 是 Moonshot AI 迄今最强的模型：一个 2.8 万亿参数的模型，也是全球首个 3 万亿参数级的开放源模型。它为前沿智能工作而设计——长程编码、端到端知识工作、深度推理。它也是第一个在 GPT 5.6 Sol 和 Claude Fable 5 层级上竞争的开放权重模型，Together AI 正与 Moonshot 团队直接合作为其提供服务。

## 已发布的最大开放权重模型

Kimi 团队对 scaling 有着深刻的执念，成绩也说明了这一点：从 2025 年 7 月到 2026 年 7 月的十二个月中，有九个月 Kimi 模型设定了开放模型规模的天花板。K3 以 2.8 万亿参数成为迄今发布的最大开放权重模型。

现已可用

在 Together AI 上运行 Kimi K3

完整 1M 上下文、自动前缀缓存、OpenAI 兼容 API、由美国基础设施提供服务。

打开 playground

## 底层构造

两项架构更新构成 K3 的骨干，都旨在让信息更容易流过更长的序列、更深的网络：

- **Kimi Delta Attention（KDA）：** 一种混合线性注意力机制，为在超长上下文中扩展注意力提供高效基础。这是首个支持 1M 上下文长度的 Kimi 模型。
- **Attention Residuals（AttnRes）：** 跨模型深度选择性地检索表示，而不是均匀地累加。

来源：Kimi K3

在此基础上，Moonshot 用 Stable LatentMoE 框架进一步推进 Mixture-of-Experts 稀疏性，高效激活 896 个专家中的 16 个。在这种稀疏度下——每个 token 大约激活 2% 的专家——路由与优化成为一阶挑战，因此若干配套技术支撑了 2.8T 规模的稳定训练：

- **Quantile Balancing：** 直接从 router-score 的分位数推导专家分配，消除启发式更新和一个敏感的平衡超参数。
- **Per-Head Muon：** 将 Muon 优化器扩展为独立优化每个 attention 头，在规模上实现更自适应的学习。
- **Sigmoid Tanh Unit（SiTU）：** 改进激活控制。
- **Gated MLA：** 改进注意力选择性。

## 如何在 Together AI 上使用 Kimi K3

API 兼容 OpenAI。以下代码片段面向 Together AI，使用官方 Together Python SDK。

```
python3 -m pip install --upgrade 'together>=2.0.0'
```

```
import os
from together import Together

MODEL = "moonshotai/Kimi-K3"

client = Together(
    api_key=os.environ["TOGETHER_API_KEY"],
)

completion = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "Introduce Kimi K3 in one sentence."}],
    max_tokens=130_000,
)
print(completion.choices[0].message.content)
```

### 思考强度

K3 可通过顶层 reasoning_effort 字段配置。支持三档：low、high、max，默认为 max。在 Together 上，也可以通过标准的 reasoning={"enabled": False} 开关关闭思考。

```
# 调整深度："low" | "high" | "max"
completion = client.chat.completions.create(
    model=MODEL,
    reasoning_effort="max",
    messages=[{"role": "user", "content": "Prove that the square root of 2 is irrational."}],
    max_tokens=8192,
)

# 即时模式，完全不产生思考 token 计费
fast = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "What is the capital of France?"}],
    reasoning={"enabled": False},
    max_tokens=256,
)
```

### 流式

流式响应分别交付 reasoning_content（思维 trace）与最终答案的 content 增量。

```
stream = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "Explain why the sky is blue."}],
    max_tokens=4096,
    stream=True,
)

in_answer = False
for chunk in stream:
    if not chunk.choices:
        continue
    delta = chunk.choices[0].delta
    thinking = getattr(delta, "reasoning_content", None) or getattr(delta, "reasoning", None)
    if thinking:
        print(thinking, end="", flush=True)
    if delta.content:
        if not in_answer:
            print("\n--- answer ---")
            in_answer = True
        print(delta.content, end="", flush=True)
```

### 视觉输入

可以提供多张图像作为输入。Moonshot 还发布了视觉推理基准 [Perception Bench](https://www.kimi.com/blog/perception-bench)。

```
import base64
from pathlib import Path

# 选项 A：以 URL 传图
IMAGE_URL = "https://raw.githubusercontent.com/pytorch/pytorch/main/docs/source/_static/img/pytorch-logo-dark.png"
image_content = {"type": "image_url", "image_url": {"url": IMAGE_URL}}

# 选项 B：以 base64 传本地图片（需要时取消注释）
# image_data = base64.b64encode(Path("image.png").read_bytes()).decode()
# image_content = {"type": "image_url",
#                  "image_url": {"url": f"data:image/png;base64,{image_data}"}}

completion = client.chat.completions.create(
    model=MODEL,
    max_tokens=2048,
    messages=[{
        "role": "user",
        "content": [
            image_content,
            {"type": "text", "text": "Describe this image."},
        ],
    }],
)
```

**视觉限制：**

- 图像数量没有限制，但整个请求体必须小于 100 MB。
- 推荐上限：图像 4K（4096x2160）。更高分辨率只会消耗处理时间与 token，不提升理解。
- Token 成本随分辨率增长。

### 结构化输出

使用 response_format 配 json_schema 和 strict: true 来约束最终的 message.content。

```
import json

completion = client.chat.completions.create(
    model=MODEL,
    max_tokens=4096,
    messages=[{"role": "user", "content": "Ada Lovelace was 36 years old."}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "person",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
                "required": ["name", "age"],
                "additionalProperties": False,
            },
        },
    },
)

person = json.loads(completion.choices[0].message.content)
# -> {'name': 'Ada Lovelace', 'age': 36}
```

较宽松的 {"type": "json_object"} 模式在只需要语法合法的 JSON 时同样可在 Together 上使用。无论哪种，max_tokens 请保持宽裕：整个思维 trace 在第一个受 schema 约束的 token 发出之前就已消耗，所以太紧的上限会截断 JSON，而不是截断推理。

### 工具与 tool_choice

K3 保留标准的 tool-choice 约束。标准循环是：在 tools 中声明函数；当模型返回 tool_calls 时，把完整的 assistant 消息追加进历史，再为每个调用追加一条带匹配 tool_call_id 的 tool 消息，然后再次调用。在第一轮使用 tool_choice="required" 强制至少一次工具调用，之后切回 "auto"。更改 tool_choice 不会使前缀缓存失效。

```
import json

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name, e.g. Paris"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["city"],
            "additionalProperties": False,
        },
    },
}]

def get_weather(city, unit="celsius"):
    return {"city": city, "temperature": 21, "unit": unit, "conditions": "sunny"}

messages = [{"role": "user", "content": "What's the weather in Paris?"}]
choice_mode = "required"          # 第一轮强制工具调用

for _ in range(5):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice=choice_mode,
        max_tokens=8192,
    )
    choice = response.choices[0]
    message = choice.message

    # 追加 COMPLETE 的 assistant 消息，包含 thinking trace。
    messages.append(message.model_dump(exclude_none=True))

    if choice.finish_reason != "tool_calls" or not message.tool_calls:
        print(message.content)
        break

    for call in message.tool_calls:
        try:
            args = json.loads(call.function.arguments)
        except json.JSONDecodeError:
            args = {}
        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "content": json.dumps(get_weather(**args)),
        })

    choice_mode = "auto"          # 强制轮之后把控制权交还
```

### 动态工具加载

你可以把完整的工具定义（完整名称、描述和参数）放在一条携带 tools 字段、没有 content 的 system 消息中。该工具从这条消息的位置起变为可用。

关键规则：

- 动态声明与顶层 tools 字段使用完全相同的格式。
- 它们按请求生效、不被服务器保留，所以后续请求历史要由你自己保存这条消息。保留它既维持工具的可用性也维持缓存前缀；丢掉它意味着模型不再能调用该工具，且变化的前缀可能错过缓存。
- 在 messages 末尾追加动态声明不影响缓存前缀；移除或修改靠前的声明可能损害变化点之后的缓存命中。

大工具 catalog 的推荐模式：

- **对话开始：** 只声明一个 search_tools 函数（由你的后端实现）加几个核心工具，并在 system prompt 中告知可检索的领域标签。
- **第一轮：** 设置 tool_choice: "required"，强制在回答前先检索。
- **按需注入：** 依据检索结果，通过 system 消息插入匹配工具的完整定义。
- **直接调用：** 模型在后续生成中使用已加载的工具。
- **成本权衡：** 在对话开始前决定 reasoning_effort。

代码示例：

```
CATALOG = {
    "convert_currency": {
        "type": "function",
        "function": {
            "name": "convert_currency",
            "description": "Convert an amount from one currency to another.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "from_currency": {"type": "string"},
                    "to_currency": {"type": "string"},
                },
                "required": ["amount", "from_currency", "to_currency"],
                "additionalProperties": False,
            },
        },
    },
}

search_tools = {
    "type": "function",
    "function": {
        "name": "search_tools",
        "description": "Search the tool catalog. Tags: finance, travel, files.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}

messages = [{"role": "user", "content": "Convert 100 USD to EUR."}]

# 1. 回答前强制检索。
first = client.chat.completions.create(
    model=MODEL, messages=messages, tools=[search_tools],
    tool_choice="required", max_tokens=8192,
)
call = first.choices[0].message.tool_calls[0]
messages.append(first.choices[0].message.model_dump(exclude_none=True))
messages.append({"role": "tool", "tool_call_id": call.id,
                 "content": json.dumps(list(CATALOG))})

# 2. 在 TAIL 注入匹配的定义。`tools` 字段，无 content。
messages.append({"role": "system", "tools": [CATALOG["convert_currency"]]})

# 3. 模型直接调用刚加载的工具。
second = client.chat.completions.create(
    model=MODEL, messages=messages, tools=[search_tools],
    tool_choice="auto", max_tokens=8192,
)
print(second.choices[0].message.tool_calls)
# -> convert_currency({"amount":100,"from_currency":"USD","to_currency":"EUR"})
```

### 1M 上下文与自动缓存

Together 支持完整的 1M 上下文长度，上下文缓存是自动的。让你的长前缀（system prompt、知识库、repo 转储）在各请求之间保持字节级稳定，后续调用才能命中缓存。Moonshot 建议把固定的大块上下文（知识文档）放在 messages 数组的最开头、system 消息之前，然后再追加问题与回复。

```
def _get(obj, key, default=None):
    if obj is None:
        return default
    return obj.get(key, default) if isinstance(obj, dict) else getattr(obj, key, default)

usage = completion.usage
reasoning_tokens = _get(_get(usage, "completion_tokens_details"), "reasoning_tokens", 0)
cached_tokens = _get(_get(usage, "prompt_tokens_details"), "cached_tokens",
                     _get(usage, "cached_tokens", 0))

print(f"prompt={usage.prompt_tokens} cached={cached_tokens} "
      f"completion={usage.completion_tokens} thinking={reasoning_tokens}")
# -> prompt=86 cached=64 completion=133 thinking=111
```

### 采样参数

采样参数是固定的，请求时应省略。模型就是用这些参数训练的，不支持设置替代值：

- temperature = 1.0
- top_p = 0.95
- n = 1
- presence_penalty = 0
- frequency_penalty = 0

### 保留思考

K3 是在保留思考历史（preserved thinking history）模式下训练的，因此 trace 就是下一轮所依赖的状态。用下面的方法保留上一轮的 thinking token 并转发给后续轮次。

```
SECRET = "48213"
TRACE  = "For the session codeword I will use 48213. Committing to 48213 as the codeword."

messages = [
    {"role": "user", "content": "Pick a 5-digit codeword for our session and remember it. "
                                "Reply with exactly: OK"},
    # trace 随 assistant 轮一起走，无需额外标志。
    {"role": "assistant", "content": "OK", "reasoning_content": TRACE},
    {"role": "user", "content": "What codeword did you pick? Reply with just the number."},
]

completion = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    max_tokens=4000,
    chat_template_kwargs={"preserve_thinking": True}
)
print(completion.choices[0].message.content)   # -> 48213
```

删掉 reasoning_content 这一行，同样的调用每次都会回答一个现编的不同数字。真实代码里你不会手写 trace；你回放模型产出的内容，也就是工具循环里的那一行：

```
# 第 1 轮 —— 让 K3 思考。
first = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": "Pick a random 5-digit number and commit to it. "
                                          "Do not tell me. Reply with exactly: OK"}],
    max_tokens=4000,
)

# 完整地回放 assistant 轮。model_dump 会把 reasoning_content 连同 content 一起保留。
history = [
    {"role": "user", "content": "Pick a random 5-digit number and commit to it. "
                                "Do not tell me. Reply with exactly: OK"},
    first.choices[0].message.model_dump(exclude_none=True),
    {"role": "user", "content": "What number did you pick? Reply with just the number."},
]

second = client.chat.completions.create(model=MODEL, messages=history, max_tokens=4000)
print(second.choices[0].message.content)
```

## Kimi K3 定价

Kimi K3 按 token 计价，设有奖励稳定前缀的缓存命中输入档：

Kimi K3 定价

| 档位 | 每 100 万 token 价格 |
| --- | --- |
| 输入（缓存命中） | \$0.30 |
| 输入（缓存未命中） | \$3.00 |
| 输出 | \$15.00 |

上下文窗口：1,048,576 token（1M）。Thinking token 按输出计费。

两个要内化的成本要点：

- **缓存是你的杠杆。** 编码负载下命中率 >90% 时，有效输入成本趋近 \$0.30 的地板价——前提是你保持前缀稳定。重构靠前的消息或工具声明会破坏它。
- **推理按输出计费，而且可以调档。** 思考 token 是按 \$15/M 计费的输出 token，思考无法被完全禁用，但 reasoning_effort 现在有三档。max 仍是默认——所以一个从不设置该字段的流水线，在每次调用（包括琐碎调用）上都在支付最高的推理账单。

## Kimi K3 基准

在整个评估套件上，Kimi K3 交出前沿水平的数字。它在若干编码与 agentic 基准（SWE Marathon、BrowseComp、DeepSearchQA、AutomationBench、OmniDocBench）上领先全场，并在其他基准上与最强的专有模型保持竞争，同时明显超过被测的另一个开放模型 GLM-5.2。在少数基准上它落后于 Claude Fable 5 和 GPT 5.6 Sol，这与 Moonshot 自己对模型的定位一致。

以下所有 Kimi K3 结果均使用 reasoning effort = max。

Kimi K3 基准

Reasoning effort: max

| 基准 | Kimi K3   max | Claude Fable 5   max, 含 fallback | GPT 5.6 Sol   max | Claude Opus 4.8   max | GLM-5.2   max |
| --- | --- | --- | --- | --- | --- |
| 编码 |  |  |  |  |  |
| DeepSWE | 67.5 | 70.0 | 73.0 | 59.0 | 46.2 |
| Program Bench | 77.8 | 76.8 | 77.6 | 71.9 | 63.7 |
| Terminal Bench 2.1 | 88.3 | 84.6 | 88.8 | 84.6 | 82.7 |
| FrontierSWE | 81.2 | 86.6 | 71.3 | 66.7 | 67.3 |
| SWE Marathon | 42.0 | 35.0 | 39.0 | 40.0 | 13.0 |
| PostTrain Bench | 36.6 | 41.4 | 34.6 | 34.1 | 34.3 |
| MLS Bench | 48.3 | 49.9 | 46.2 | 42.8 | 40.4 |
| Kimi Code Bench 2.0（内部） | 72.9 | 76.9 | 64.8 | 71.7 | 64.2 |
| Agentic |  |  |  |  |  |
| GDPval-AA v2 (Elo) | 1668 | 1760 | 1748 | 1600 | 1514 |
| BrowseComp | 91.2 | 88.0 | 90.4 | 84.3 | N/A |
| DeepSearchQA (F1) | 95.0 | 94.2 | N/A | 93.1 | N/A |
| Toolathlon-Verified | 73.2 | 77.9 | 74.9 | 76.2 | 59.9 |
| MCP Atlas | 84.2 | 84.7 | 83.6 | 83.6 | 82.6 |
| Automation Bench | 30.8 | 29.1 | 29.7 | 27.2 | 12.9 |
| Job Bench | 52.9 | 57.4 | 46.5 | 48.4 | 43.4 |
| AA-Briefcase (Elo) | 1548 | 1583 | 1495 | 1354 | 1260 |
| APEX-Agents | 41.0 | 43.3 | 39.9 | 39.4 | 35.6 |
| Office QA Pro | 63.3 | 69.9* | 63.2* | 63.9* | 41.4 |
| SpreadsheetBench 2 | 34.8 | 34.7* | 32.4* | 31.6* | 28.1 |
| DECK-Bench（内部） | 73.5 | 73.0 | 74.7 | 66.9 | 68.6 |
| 推理与知识 |  |  |  |  |  |
| GPQA-Diamond | 93.5 | 92.6 | 94.1 | 91.0 | 91.2 |
| HLE-Full | 43.5 | 53.3 | 44.5 | 49.8* | N/A |
| HLE-Full 带工具 | 56.0 | 63.0 | 58.0 | 57.9* | N/A |
| 视觉 |  |  |  |  |  |
| MMMU-Pro | 81.6 | 81.2 | 83.0 | 78.9 | N/A |
| MMMU-Pro 带 python | 83.4 | 86.5 | 84.6 | 82.7 | N/A |
| CharXiv (RQ) | 84.8 | 88.9 | 84.6 | 80.5 | N/A |
| CharXiv (RQ) 带 python | 91.3 | 93.5 | 89.1 | 89.9 | N/A |
| MathVision | 94.3 | 94.8 | 95.8 | 86.7 | N/A |
| MathVision 带 python | 97.8 | 98.6 | 97.8 | 97.1 | N/A |
| BabyVision 带 python | 85.7 | 90.5 | 88.9 | 81.2 | N/A |
| ZeroBench_main (pass@5) | 23.0 | 23.0 | 17.0 | 17.0 | N/A |
| ZeroBench_main 带 python (pass@5) | 41.0 | 46.0 | 35.0 | 34.0 | N/A |
| WorldVQA ForceAnswer | 51.0 | 56.7 | 41.8 | 39.1 | N/A |
| OmniDocBench | 91.1 | 89.8 | 85.8 | 87.9 | N/A |
| PerceptionBench | 58.5 | 57.2 | 59.7 | 47.2 | N/A |

所有 Kimi K3 结果使用 reasoning effort = max。带星号（*）的数值是在与基础运行不同的条件下报告的——例如引自外部来源或不同的 harness。N/A 表示没有公开分数。阴影单元格标记该行的领先结果。各基准的确切方法学见来源报告。来源：Kimi K3。

## Kimi K3 与前沿的对比

聚合基准表只能说明一部分。为了在成本、编码质量与路由行为上得到直接的判断，我们在 DeepSWE 上让 Kimi K3 对阵领先的专有模型：

- [Kimi K3 vs GPT 5.6 Sol on DeepSWE: cost, coding, and routing](https://www.together.ai/blog/kimi-k3-vs-gpt-5-6-sol-on-deepswe-cost-coding-and-routing)
- [Kimi K3 vs Claude Fable 5 on DeepSWE: cost and coding](https://www.together.ai/blog/kimi-k3-vs-claude-fable-5-on-deepswe-cost-and-coding)

## 常见问题

**Kimi K3 是什么？** Kimi K3 是 Moonshot AI 的旗舰 2.8 万亿参数模型，也是 3 万亿参数级首个开放源模型，为长程编码、知识工作和推理而生。

### **Kimi K3 是开源的吗？**

是。它作为开放权重模型发布，Together AI 与 Moonshot 团队直接合作为其提供服务。

### **Kimi K3 的上下文窗口多大？**

1M token（1,048,576），在 Together AI 上完整支持并带自动上下文缓存。

### **Kimi K3 在 Together AI 上多少钱？**

每 100 万缓存命中输入 token \$0.30，每 100 万缓存未命中输入 token \$3.00，每 100 万输出 token \$15.00。

### **可以关掉 Kimi K3 的思考吗？**

在 Together AI 上，你可以用 reasoning={"enabled": False} 禁用思考，或用 reasoning_effort 设为 low、high、max 调节推理深度。

### **Kimi K3 支持视觉吗？**

支持。它有原生视觉能力，每个请求可接受多张图像，只要整个请求体保持在 100 MB 以内。

## Kimi K3 已在 Together AI 上线。跑起来，交付到生产。

让 K3 归你所有，从一个 API 调用开始。

- 运行 Kimi K3 推理：[Kimi K3 API on Together AI](https://www.together.ai/models/kimi-k3)
- 开始用 API 构建：[阅读文档](https://docs.together.ai/docs/quickstart)
