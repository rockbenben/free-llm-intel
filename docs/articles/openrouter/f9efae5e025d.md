---
vendor: openrouter
title: 为什么要用 OpenRouter 接入 DeepSeek
original_title: Why Use OpenRouter for DeepSeek
url: https://openrouter.ai/blog/insights/why-openrouter-for-deepseek
date: 2026-07-13
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 5306fdaa9933
translator: agent
---

# 为什么要用 OpenRouter 接入 DeepSeek

OpenRouter ·7/13/2026

DeepSeek 是 OpenRouter 上被使用最多的模型作者。截至 2026 年 7 月 13 日，它在实时[排行榜](https://openrouter.ai/rankings)上按 token 份额排名第一。所以开发者们在 Reddit 上反复问的那个问题是合理的：DeepSeek 走 OpenRouter 路由，还是直连 DeepSeek 的 API？

"DeepSeek"是一个由 16 家公司分别服务的模型：按实时 [V4 Pro 提供商页面](https://openrouter.ai/deepseek/deepseek-v4-pro)，价格相差约 4 倍，吞吐从每秒 4 到 57 token 不等。OpenRouter 的路由层就是为把这片混乱的提供商田野变成单一 slug 而建的——保持在线、保持便宜、保持快，同时在你想把请求钉在某家提供商上时，给你伸手可及的控制项。直连有时是正确选择，我们会明确告诉你什么时候是。

## 太长不看

- DeepSeek 领跑 OpenRouter 用量：实时[排行榜](https://openrouter.ai/rankings)上按 token 份额的第一作者（2026 年 7 月 13 日核查），总量榜前十里占两席、工具调用榜前十里占两席。
- 单个 DeepSeek 模型同时在很多提供商上运行。按实时 [V4 Pro 页面](https://openrouter.ai/deepseek/deepseek-v4-pro)，输入价在提供商之间拉开约 4 倍，吞吐从每秒 4 到 57 token。
- 我们不给提供商价格加价。目录价就是你付的价，所以这个价差是真实的提供商经济学，不是我们的利润。
- 默认负载均衡会把过去 30 秒内发生过显著宕机的提供商降权，并按价格平方倒数向更便宜的提供商倾斜。你可以用 provider 对象上的 `sort`、`max_price` 和 `order`/`only`/`ignore` 字段按速度或价格排序、封顶支出、纳入或排除提供商。
- 粘性路由让多轮对话不在各家托管方之间弹跳，回退保护长时间的工具调用循环，[Fusion](https://openrouter.ai/docs/guides/routing/routers/fusion-router) 在"答错的代价高于额外 token"的难题上提升可靠性。
- 这一切的成本是按量付费上 5.5% 的平台费。对稳定的单提供商流量，直连可能略占上风。路由换来的是故障转移、提供商钉定，以及改一个字符串就能切换版本。

## DeepSeek 是 OpenRouter 上被使用最多的模型

先说规模，因为它解释了后面的一切。DeepSeek 是 OpenRouter 上最大的 token 来源：按 token 份额的第一模型作者，两个模型进入总榜前十。当一个模型承载这么多生产流量时，好提供商和差提供商之间的差距会很快现形——通常出现在错误日志里，通常在你不方便的时候。

DeepSeek 是一个为计算效率打造的开放权重混合专家（MoE）模型家族，推理和工具调用能力很强。较新的 V4 系列增加了混合注意力系统，让上下文窗口扩展到 1M token 时推理依然高效。OpenRouter 上的阵容覆盖 chat/V3 系列、R1 推理系列、一批蒸馏小模型和较新的 V 系列。当前的旗舰换得够勤，我们不想在这里钉版本号；请查实时 [DeepSeek hub](https://openrouter.ai/deepseek)，别信某篇博客上个月提到的版本。此刻 hub 上列着 22 个 DeepSeek 模型。

截至 2026 年 7 月 13 日，实时[排行榜](https://openrouter.ai/rankings)上的拆解如下：

| 用量维度 | DeepSeek 的位置 |
| --- | --- |
| 作者 token 份额 | 全部作者中第 1，占 16.7% 的 token |
| 用量前十模型 | V4 Flash 第 3，V4 Pro 第 6 |
| 工具调用 | 前十中有 2 个 DeepSeek 模型：V4 Flash 第 3，V4 Pro 第 6 |

## "DeepSeek"是一个模型、多家提供商

在 OpenRouter 上调用 DeepSeek 模型时，可能为你服务的是 16 家不同的公司，而它们彼此不能互换。截至 2026 年 7 月 13 日，DeepSeek V4 Pro 通过 OpenRouter 跑在 16 家提供商上，各有各的价格、在线率和速度。这些取舍并不整齐地对齐：眼下最便宜的提供商恰好在线率最好，最慢的提供商收费仍是最低价 3 倍多。你落在表的哪一行，就是"直连还是走路由"这个问题的答案大半。

![一个 DeepSeek V4 Pro 模型由 16 家提供商服务的示意图，展示 4 张提供商卡片及各自的输入价、在线率和吞吐](https://openrouter.ai/blog/images/deepseek-v4-providers.png)

这是实时 [V4 Pro 提供商表](https://openrouter.ai/deepseek/deepseek-v4-pro)，只截取高低两端。价格一直在动，基于它们做任何设计之前请点进去看当前数字。

| 提供商 | 输入价 /M | 在线率 | 吞吐 |
| --- | --- | --- | --- |
| DeepSeek（输入最便宜、在线率最高） | $0.435/M | 99.92% | 45 tps |
| Baseten（输入最贵、最快） | $1.74/M | 99.45% | 57 tps |
| Together（在线率最低） | $1.74/M | 97.44% | 46 tps |
| DigitalOcean（最慢） | $1.392/M | 99.64% | 4 tps |

同样的模型权重，输入价从约 $0.44/M 到 $1.74/M，吞吐从每秒 4 到 57 token，在线率从约 97% 到接近 100%。直连某一家 DeepSeek 提供商，就是挑定表中一行然后与它过日子，好坏都是它。经 OpenRouter 路由，则是在所有这些行之间用一个 slug 做选择。

这价差乍看像加价，其实不是。我们不给提供商定价加成分：你看到的目录价就是你要付的。4 倍的输入价差是这些提供商运行同一份权重的真实收费差异。这也是"直连 DeepSeek 更便宜吗"没有统一答案的原因——完全取决于你在和哪家提供商比较。

## OpenRouter 把多家提供商变成一个可靠端点

默认情况下，我们的路由层把过去 30 秒内发生过显著宕机的提供商降权，对稳定的提供商按价格平方倒数加权，其余留作回退（完整机制见[提供商选择文档](https://openrouter.ai/docs/guides/routing/provider-selection)）。某家 DeepSeek 提供商退化时，你的请求会在你无感的情况下改路由到另一家。

提供商在请求中途失败时有两件独立的事发生：路由通过回退提供商重试；[Zero Completion Insurance](https://openrouter.ai/docs/guides/features/zero-completion-insurance)（零补全保险）意味着响应报错或零输出 token 返回时不向你收费。

### 对 DeepSeek 提供商排序、封顶和钉定

需要更紧的控制时，`provider` 对象让你在一次调用里调节速度、成本和主机选择：

| 控制项 | 在 DeepSeek 调用上的作用 |
| --- | --- |
| `sort: 'throughput'` / `:nitro` | 路由到最快的提供商。治"DeepSeek 太慢"。 |
| `sort: 'price'` / `:floor` | 路由到该模型最便宜的提供商。 |
| `max_price` | 硬性成本上限。宁可请求失败也不超支。 |
| `order` / `only` / `ignore` | 强制、限定或排除特定的 DeepSeek 提供商。 |
| `quantizations` | 过滤掉量化差的端点。治质量抱怨。 |

下面这个 DeepSeek 调用要速度，但拒绝为速度多付钱。`max_price` 的值当占位符对待；上线前从实时模型页取当前数字。

```
from openrouter import OpenRouter

client = OpenRouter()

res = client.chat.send(
    model="deepseek/deepseek-v4-pro",
    messages=[{"role": "user", "content": "Write a SQL query to find duplicate rows."}],
    provider={"sort": "throughput", "max_price": {"prompt": 1, "completion": 2}},
)
```

```
import { OpenRouter } from '@openrouter/sdk';

const openRouter = new OpenRouter({ apiKey: process.env.OPENROUTER_API_KEY });

const res = await openRouter.chat.send({
  model: 'deepseek/deepseek-v4-pro',
  messages: [{ role: 'user', content: 'Write a SQL query to find duplicate rows.' }],
  provider: { sort: 'throughput', max_price: { prompt: 1, completion: 2 } },
});
```

这个请求会从当前最快的可用提供商拿 DeepSeek V4 Pro，但如果每 token 价格超过你设的上限，它根本不会跑。`order`、`only`、`ignore` 和 `quantizations` 是同样的模式，例如 `provider: { only: ['baidu'], quantizations: ['fp8'] }` 把提供商钉定到某家运行特定量化的。我们的[用路由拿最低成本推理](https://openrouter.ai/blog/tutorials/how-to-get-the-lowest-cost-llm-inference-on-openrouter/)指南更细地讲成本控制字段。

## 粘性路由、回退和 Fusion 把单个模型再抬一层

排序、封顶、钉定解决大多数单请求问题。多轮 agent 还需要更多。三个可叠加的层覆盖这些场景：粘性路由、回退和 Fusion。它们层层叠加，每种都在工作负载真需要时才加。

![可靠性分层示意图：默认负载均衡，之上是排序/封顶/钉定旋钮、粘性路由、回退和 Fusion](https://openrouter.ai/blog/images/deepseek-routing-layers.png)

### 面向多轮 agent 的粘性路由

粘性路由把一个对话的服务提供商钉住，DeepSeek agent 就不会在会话中途在托管方之间弹跳。不带 `session_id` 时，我们用对话开头消息的哈希作为会话键，并在检测到缓存命中后激活钉定。传入 `session_id`（请求体顶层字段或 `x-session-id` 头）时，钉定在第一个成功请求就激活。若被钉定的提供商不可用，请求回退到次优提供商（完整机制见[粘性路由文档](https://openrouter.ai/docs/guides/best-practices/prompt-caching#provider-sticky-routing)）。

一个编码 agent 在 V4 Pro 上跑大型重构时，可以从第一轮钉到会话结束。而工具调用循环若在轮次之间从快提供商跳到慢提供商，你会得到不一致的延迟，更糟的是逐轮不一致的行为。我们的[路由器指南](https://openrouter.ai/blog/insights/model-routing/)讲了 OpenRouter 所有路由器上的粘性。

### 为长工具调用循环准备的回退

回退数组保护一个长的 DeepSeek 对话不被单一提供商的中途失败击穿。想象一个客服机器人跑 5 步工具循环：查客户、查订单、草拟回复、跑政策检查、发送。如果服务该对话的提供商在第 3 步丢了一个响应，整个循环就断了。这正是我们在 r/openrouter 上见过的抱怨形状：经某一家提供商的大体积工具调用对话持续 400。

两个不同的字段管这件事。`models` 是模型 slug 的有序数组，主力模型完全不可用时 OpenRouter 落到下一个模型。`provider.order` 配合 `allow_fallbacks: true` 管单个模型内部的提供商级回退。

```
const res = await openRouter.chat.send({
  models: ['deepseek/deepseek-v4-pro', 'deepseek/deepseek-v4-flash'],
  messages: [{ role: 'user', content: 'Continue the agent loop.' }],
});
```

这个调用先试 DeepSeek V4 Pro，主路径失败时回退到 V4 Flash，一家提供商状态不好不会终结你的运行。

### 答错很贵时用 Fusion

[Fusion](https://openrouter.ai/docs/guides/routing/routers/fusion-router) 跑一个模型评审团加一个裁判，用更严格的审视处理更难的问题。按默认 3 模型评审团，成本约是单次补全的 4 到 5 倍，所以它是例外而不是默认。聊天回复或摘要端点通常用不上。做研究、批评，或一个高风险对比任务——你想要 DeepSeek 的成本画像、但要在难题上更有信心时——一个把 DeepSeek 和裁判放在一起的评审团可能值这个倍数。把它限定在真正难的子任务上。

## 什么时候直连 DeepSeek、什么时候走路由

社区在 Reddit 上的真实抱怨值得真实的回答。有开发者因为延迟和成本发过"别通过 OpenRouter 用 DeepSeek"，也有人直接问 DeepSeek 的价格是不是更低。两个问题都合理。如果你的流量稳定、单提供商、对延迟不敏感，直连更简单——多一跳网络加 5.5% 的按量付费手续费，确实可能让直连成为更干净的选择。

| 该直连 DeepSeek 的情况 | 该经 OpenRouter 路由的情况 |
| --- | --- |
| 你以稳定量级只打一家提供商、想要地板价 | 你想要一个 slug 背后多家提供商的故障转移 |
| 你的流量简单、单轮、延迟不敏感 | 你跑不能断的 agent 或长工具调用对话 |
| 你不需要切换模型或版本 | 你想改一个字符串就换 DeepSeek 版本、或退到别的模型 |
| 你想避免任何平台费 | 提供商质量参差、你想钉定一个验证过的托管方 |

每条抱怨都能对上一个具体修法。"太慢"是路由默认值的问题，不是天花板：设 `sort: 'throughput'` 或加 `:nitro` 后缀。"质量参差"是真的，通常原因是量化：用 `quantizations` 字段过滤，或用 `order`/`only` 钉住你测过的提供商。"长时间运行报 400"通常指向某一家出问题的提供商：加一个回退数组，别吊死在单台主机上。

路由的成本：无加价提供商价之上，5.5% 的按量付费平台费。换来的是跨所有 DeepSeek 提供商的故障转移、只为成功付费的计费、提供商钉定，以及不改集成就切换 DeepSeek 版本的能力。对稳定的单提供商流量，这 5.5% 可能赚不回本。对 agent 类的、或真不能宕机的任何东西，通常能。

## 把 DeepSeek 模型匹配到工作

先按系列选：V4 用于通用 agentic 工作，R1 用于显式分步推理，成本比深度重要时上蒸馏小模型。然后到实时 [DeepSeek hub](https://openrouter.ai/deepseek) 确认当前 slug，别信博客里的模型名——包括本文——因为旗舰在动，钉死的推荐几周就过期。

| 系列 | 用途 | 示例 slug（当前版本以 hub 为准） |
| --- | --- | --- |
| Chat / V3 系列 | 通用聊天与生成 | `deepseek/deepseek-chat`、`deepseek/deepseek-chat-v3-0324` |
| V3.1 / V3.2 系列 | 混合推理 + 工具调用，效率调校 | `deepseek/deepseek-chat-v3.1`、`deepseek/deepseek-v3.2` |
| R1 推理系列 | 显式分步推理 | `deepseek/deepseek-r1`、`deepseek/deepseek-r1-0528` |
| 蒸馏小模型 | 便宜、快、适配小预算 | `deepseek/deepseek-r1-distill-llama-70b` |
| V4 系列 | 最新的大 MoE，1M token 上下文 | `deepseek/deepseek-v4-pro`、`deepseek/deepseek-v4-flash` |

有一个能力值得记住（但请以模型页确认仍然成立）：截至本文撰写，V3.2 和 V4 模型暴露了一个可选的推理开关。传 `reasoning: { enabled: true }` 打开思考模式、把推理步骤包含在输出里；不开就是同一个 slug 上更快更便宜的非推理响应。V4 模型还接受最高 `xhigh` 的 `reasoning_effort` 以获得最大推理量。

## 5 分钟经 OpenRouter 调用 DeepSeek

还没有 OpenRouter 账户的话，注册并在控制台创建一个 API key。OpenRouter API 说你已经熟悉的 OpenAI Chat Completions 格式（见[快速上手](https://openrouter.ai/docs/quickstart)），如果你的技术栈更近 Anthropic 或 OpenAI Responses，也支持 Messages 和 Responses API 格式。

```
from openrouter import OpenRouter

client = OpenRouter()

res = client.chat.send(
    model="deepseek/deepseek-v4-pro",
    messages=[{"role": "user", "content": "Explain MoE routing in two sentences."}],
)
```

```
import { OpenRouter } from '@openrouter/sdk';

const openRouter = new OpenRouter({ apiKey: process.env.OPENROUTER_API_KEY });

const res = await openRouter.chat.send({
  model: 'deepseek/deepseek-v4-pro',
  messages: [{ role: 'user', content: 'Explain MoE routing in two sentences.' }],
});
```

这已经是一个可用的 DeepSeek 调用，默认负载均衡已生效——你还没加任何路由字段就已经有了提供商故障转移。把 slug 换成 [hub](https://openrouter.ai/deepseek) 上的任何模型即可。如果你的目标是免费用 DeepSeek 而不是生产流量，免费档路线在我们的 [免费 LLM API](https://openrouter.ai/blog/tutorials/free-llm-apis-compared/) 指南里。

## 常见问题

### 直连 DeepSeek 和经 OpenRouter 哪个更便宜？

取决于你拿哪家提供商和我们比，因为我们不加价。目录价就是你要付的，另加按量付费上 5.5% 的平台费。路由换来的是跨所有 DeepSeek 提供商的故障转移、版本切换和只为成功付费的计费——对 agentic 或对在线率敏感的工作负载，这份韧性通常盖得过手续费。

### DeepSeek 该走 OpenRouter 还是直连？

除非你的流量永远只打一家稳定的、延迟不敏感的提供商（那种情况下直连更简单、每 token 可能更便宜），否则走 OpenRouter。当你想要跨提供商在线率、质量参差时钉定提供商、为长工具调用循环配回退、或不重写集成就切换 DeepSeek 版本时，就该走 OpenRouter。

### DeepSeek 在各提供商之间的质量一致吗？

质量因提供商而异，主要原因就是各托管方的量化差异会改变模型的回答。用 `quantizations` 过滤量化差的端点，用 `order` 或 `only` 钉住验证过的提供商，承诺之前用[模型页面](https://openrouter.ai/deepseek/deepseek-v4-pro)上的逐提供商基准做对比。

### 怎么让 DeepSeek 在 OpenRouter 上更可靠？

默认负载均衡已经在给过去 30 秒有显著宕机的提供商降权。在此基础上：加一个回退数组，用 `order` 钉住一个口碑已验证的提供商，为粘性多轮对话传 `session_id`（见[粘性路由文档](https://openrouter.ai/docs/guides/best-practices/prompt-caching#provider-sticky-routing)）。

### DeepSeek 在 OpenRouter 上为什么慢或报错？

两个不同的问题，两个不同的修法。慢通常指向提供商选择而不是模型本身：先试 `sort: 'throughput'` 或 `:nitro` 后缀。长工具调用循环上的报错是另一回事：加回退数组，让请求能转去另一家提供商，而不是停死在刚失败的那家。

### DeepSeek 在 OpenRouter 上免费吗？

免费，但有前提："免费"指 DeepSeek 阵容里特定的免费模型——通常 slug 带 `:free` 后缀——以限速形式提供，不是所有 DeepSeek 模型随便用。完整免费清单和当前限制见[免费 LLM API](https://openrouter.ai/blog/tutorials/free-llm-apis-compared/)。

### 我该用哪个 DeepSeek 版本？

先按系列选：chat/V3 通用，R1 推理，蒸馏版看成本，V 系列看长上下文。版本号的变更比系列快。然后按上下文窗口、价格和新鲜度从实时 [DeepSeek hub](https://openrouter.ai/deepseek) 挑当前的具体 slug，再用[排行榜](https://openrouter.ai/rankings)看大家在各领域实际在用哪个版本。
