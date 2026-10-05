---
vendor: openrouter
title: 在 OpenRouter 上设置团队 AI 支出控制
original_title: Set Up Team AI Spend Controls on OpenRouter
url: https://openrouter.ai/blog/tutorials/team-spend-controls-setup
date: 2026-08-07
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: a0691a176887
translator: agent
---

# 在 OpenRouter 上设置团队 AI 支出控制

OpenRouter ·8/7/2026

团队在 OpenRouter 上成长后，越来越多的 API key 和越来越宽的模型访问让"谁在花什么钱"难以看清。五个控制项解决这件事：组织让所有人共享一份额度池；preset 按工作负载限定模型；按 key 限额封顶单个 key 的支出；guardrails 按成员执行预算和模型白名单；Activity 面板展示钱去了哪。

本指南按顺序全部配一遍：组织、preset、key 限额、guardrails，最后在 Activity 里核对。还在决定要哪些控制的，先读[治理团队 AI 支出](https://openrouter.ai/blog/insights/governing-team-ai-spend/)指南；本文讲配置本身。

![OpenRouter 支出控制按配置顺序的示意图：治理（共享额度池的组织加管理员与成员角色，然后 preset）、用量控制（按日/周/月重置的 key 限额，然后是带成员预算和模型白名单的 guardrails）、可视性（按创建者、API key 或模型看支出、支持 CSV 和 PDF 导出的 Activity 面板）](https://openrouter.ai/blog/images/team-spend-controls-setup-order.png)

## 开始之前

先确认以下条件就位：

- 使用邮箱已验证的账户（创建组织要求验证邮箱）。
- 以组织管理员身份完成配置——你需要管理计费、API key、成员访问和 guardrails。
- 提前规划成员名单。组织默认支持最多 10 名成员，更高上限可联系支持。
- 和团队过一遍定价。按量付费无最低消费，标准按量账户的 5.5% 平台费发生在购买额度时，不是每次请求。见[定价](https://openrouter.ai/pricing)。

## 第 1 步：创建组织并汇入额度

到 [Settings > Preferences](https://openrouter.ai/settings/preferences)，打开 **Organization** 区，点 **Create Organization**。填好组织信息后邀请团队成员，并用应用顶部的组织切换器切进组织上下文。

继续之前确认切换器显示的是你的组织名。个人账户里，用量、API key 和额度属于你个人；组织上下文里，它们属于共享的组织账户。组织切换器是用量归属错误的高发来源。

计费权限取决于邀请时给用户分配的角色：

- **管理员（Admin）**可以购买额度、查看计费信息。
- **成员（Member）**可以使用组织资源、创建 API key，但不能购买额度、不能看计费明细。

### 给共享额度池充值

在组织上下文里，从[计费页面](https://openrouter.ai/settings/credits)购买额度。额度进入一个所有组织 API key 共用的池子——在中心给团队充一次，而不是挨个给工程师补额度。

需要把现有个人额度搬进组织，用[额度页面](https://openrouter.ai/settings/credits)的转移选项。转移有资格规则（账户开启双因素认证、账户与成员身份时长、近期购买的额度、两次转移间的冷却期），暂时不能转移时页面会说明原因。按发票计费的组织不能接收转移。

## 第 2 步：用 Preset 限定模型和提供商

[Preset](https://openrouter.ai/docs/guides/features/presets)是可复用的配置，钉住某个工作负载用哪个模型、哪些提供商。组织账户的 preset 全成员共享。

### 创建 preset

到 [Presets 设置](https://openrouter.ai/settings/presets)，按工作负载路径建 preset，例如 `support-bot`、`internal-search`、`eval-runner`。

每个 preset：

- 选一个模型或一个回退模型数组。
- 用 `sort` 配提供商路由偏好。
- 应用提供商纳入/排除规则。
- 可选设置 `system`、`temperature` 和 `top_p`。
- 以稳定的 slug 保存。

Preset 有版本管理：每次保存都被指定为 API 请求解析到的新 active 版本，版本历史保留、可回滚。请求级参数以浅覆盖方式压过 preset 值。

| Preset 控制 | 作用 |
| --- | --- |
| 模型选择 | 让工作负载留在预期的模型家族上 |
| 回退数组 | 提供商或模型故障期间请求继续可用 |
| 提供商路由（sort） | 按你优先的延迟或成本路由 |
| 提供商纳入/排除 | 执行限定在批准的提供商上 |
| 提示词与生成参数 | 保持输出风格和方差一致 |

### 在代码里引用 preset

引用 preset 有三种方式：作为 model 写 `@preset/{slug}`、用独立的 `preset` 字段，或 `model@preset/{slug}`。三种都在服务器端解析，同一个 preset 在任何 SDK 都能用。

```
const resp = await fetch('https://openrouter.ai/api/v1/chat/completions', {
  method: 'POST',
  headers: {
    Authorization: `Bearer ${process.env.OPENROUTER_API_KEY}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    model: '@preset/support-bot',
    messages: [{ role: 'user', content: 'Summarize this ticket.' }],
  }),
});
```

通过 API 创建或更新 preset 时，只有配置字段会被存储——`model`、`temperature`、`top_p`、`provider`、`system`、`tools`。`messages`、`input`、`prompt`、`stream` 这类瞬态字段被忽略。

Preset 只影响显式引用它的请求。需要 key 无法绕开的模型限制，请用第 4 步的 guardrail 模型白名单。

## 第 3 步：用限额与重置周期给每个 key 封顶

每个 API key 都可以设一个额度 `limit` 和一个 `limit_reset`，让每个工作负载在周期开始时拿到新配额。这些 key 通过 Management API key 创建和管理——它只用于 key 管理。

### 创建 Management API key

到 [Management Keys](https://openrouter.ai/settings/management-keys) 点 **Create New Key**。

Management API key 处理管理类操作：`/api/v1/keys` 下的 key 管理和 `/api/v1/guardrails` 下的 guardrail 管理。它调不了补全端点，放在开通系统和自动化流水线里是安全的。用它按服务、环境或工程师各建一个 key，让访问和支出按工作负载隔离。

### 配置限额、重置和生命周期控制

通过 `/api/v1/keys` 创建或更新 key 时，花费封顶和重置方式都在你手里：

| 字段 | 设定什么 |
| --- | --- |
| `limit` | 该 key 的额度上限 |
| `limit_reset` | daily、weekly 或 monthly（daily 在 UTC 午夜重置） |
| `disabled` | `true` 立即停用该 key |
| `include_byok_in_limit` | BYOK 支出是否计入限额 |

创建一个带每日额度上限的 key：

```
const res = await fetch('https://openrouter.ai/api/v1/keys', {
  method: 'POST',
  headers: {
    Authorization: `Bearer ${process.env.OPENROUTER_MANAGEMENT_KEY}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: 'support-bot-prod',
    limit: 25,
    limit_reset: 'daily',
  }),
});
```

更新 key 以收紧上限或更换重置周期：

```
const res = await fetch(`https://openrouter.ai/api/v1/keys/${keyHash}`, {
  method: 'PATCH',
  headers: {
    Authorization: `Bearer ${process.env.OPENROUTER_MANAGEMENT_KEY}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ limit: 15, limit_reset: 'weekly' }),
});
```

立即停用 key，止住支出或切断一个行为异常的负载：

```
await fetch(`https://openrouter.ai/api/v1/keys/${keyHash}`, {
  method: 'PATCH',
  headers: {
    Authorization: `Bearer ${process.env.OPENROUTER_MANAGEMENT_KEY}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ disabled: true }),
});
```

### 监控用量、自动化治理

每个 key 通过 `usage`、`usage_daily`、`usage_weekly`、`usage_monthly`、`limit_remaining` 及其 BYOK 对应字段报告自己的用量。可以用 cron 任务或后台 worker 轮询这些字段，在 key 逼近上限时把它停用。

`limit` 封的是 key，不是人。需要对一个成员名下所有 key 统一执法时，用第 4 步按成员分配的 guardrail。key 轮换与密钥卫生见 [API key 管理指南](https://openrouter.ai/docs/cookbook/administration/api-key-rotation)。

## 第 4 步：用 Guardrail 执行按成员预算和模型白名单

Guardrail 在"人"这个层面执行策略，不管成员创建了多少 API key。它把第 2 步的模型默认和第 3 步的按 key 封顶变成成员绕不过的硬限制。只有组织管理员能创建和管理 guardrails。

### 创建 guardrail

到 [Settings > Privacy](https://openrouter.ai/settings/privacy)，滚到 [Guardrails](https://openrouter.ai/docs/guides/features/guardrails)，点 **New Guardrail**。

配置以下项：

- **预算上限：**设一个美元封顶，按日、周或月重置。超出上限的请求以 403 拒绝。
- **分配范围：**分配给组织成员（覆盖其全部 key 和聊天会话），或分配给特定 API key（再叠一层）。每个用户或 key 直接挂一个 guardrail。
- **模型与提供商白名单：**只有列表内的模型和提供商被允许，其余一律拦截——即使 key 直接请求也一样。留空即全放行。
- **可选安全控制：**按模型组的零数据保留（ZDR）、提示词注入与越狱检测、敏感信息（PII）脱敏或拦截、自定义正则内容过滤器。

分配之前用**资格预览（eligibility preview）**看实际生效的限制。

### 按成员预算如何表现

Guardrail 预算按用户、按 key 各自执行，不在团队内共享。给 3 名成员各设 $50/天，每人各有一份额度：Alice 花到 $50 时她的请求被拦，Bob 和 Carol 各自的 $50 完好。一个成员跨所有 key 的花费累计到该成员的总额上。

当 key 级限额和成员级 guardrail 同时生效时，更低的限制赢。这正是单靠 key 限额给不了的、紧的按成员预算。

### 多个 guardrail 同时生效时策略如何合成

| 层 | 解析方式 |
| --- | --- |
| 模型与提供商白名单 | 交集：所有规则都允许的才允许 |
| 零数据保留（ZDR） | 按模型组取 OR |
| 敏感信息控制 | 拦截优先于脱敏 |
| 预算 | 按用户、按 key 独立计算；更低的限额赢 |

### 以编程方式管理 guardrail

也可以用 Management key 通过 `PATCH /api/v1/guardrails/{id}` 更新 guardrail：

```
curl -X PATCH https://openrouter.ai/api/v1/guardrails/$GUARDRAIL_ID \
  -H "Authorization: Bearer $OPENROUTER_MANAGEMENT_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "limit_usd": 50,
    "reset_interval": "daily",
    "allowed_models": ["anthropic/claude-sonnet-4.6", "openai/gpt-4o-mini"],
    "allowed_providers": ["anthropic", "openai"]
  }'
```

白名单接受精确的模型 slug，不支持通配符——模型策略变化时需要维护。预算耗尽前也没有警告，请求被拦时用户直接吃 403。guardrail 与 key 级限额何时用哪个，见[治理团队 AI 支出](https://openrouter.ai/blog/insights/governing-team-ai-spend/)。

## 第 5 步：在 Activity 面板读团队支出

打开 [Activity](https://openrouter.ai/activity)，看三张指标卡（Spend、Tokens、Requests）。设定时段（1 小时、1 天、1 周、1 月或 1 年），然后分组：

- **Creator** 显示按成员的花费。
- **API Key** 把花费映射到你在第 3 步封顶的那些负载。
- **Model** 显示哪些模型吃预算最多。

组织上下文里，Activity 动态展示所有成员的用量元数据——模型、成本、时间——并可按 API key 过滤。提示词和响应从不存储。也可以在 Options 下拉里选 Export 导出 CSV 或 PDF。

OpenRouter 在三处报告用量，各回答不同的问题：

| 界面 | 用途 | 位置 |
| --- | --- | --- |
| `usage` 对象 | 每个 API 响应的逐响应 token 和成本数据 | API 响应体 |
| `usage_*` key 字段 | 单个 key 的时间窗合计 | `GET /api/v1/key` |
| Activity 面板 | Spend、Tokens、Requests；可分组、可导出 | [openrouter.ai/activity](https://openrouter.ai/activity) |

Activity 里显示的 BYOK 支出按提供商列表价估算，可能和你的协议折扣有差异。

## 验证你的配置

把组织交给团队之前，跑这四项检查：

- 通过 preset（`@preset/{slug}`）发一次调用，确认响应里带 `usage.cost`。每个响应都会自动带 `usage` 对象。
- 通过 `GET /api/v1/key` 确认被封顶的 key 在调用后 `limit_remaining` 减少了。
- 发一个违反 guardrail 的请求（超预算或不在模型白名单内），确认返回 403。
- 打开 Activity、按 Creator 分组，确认花费归属到正确的成员。

白名单之外的请求返回 403、Activity 面板在每个人名下显示其支出时，配置就完成了。

## 常见问题

### 怎么在 OpenRouter 上跟踪整个团队的 AI 支出？

创建组织让所有用量记在同一份共享额度池上；打开 Activity 面板按 Creator 分组，把花费归属到每个成员。组织上下文里，动态展示所有成员的用量元数据（模型、成本、时间）；提示词和响应不会被存储。

### 能给 OpenRouter 的 API key 设支出上限吗？

能。通过 Management API 在 `/api/v1/keys` 创建或更新 key 时，设 `limit`（额度上限）和 `limit_reset`（daily、weekly 或 monthly）。每日限额在 UTC 午夜重置。限额封的是那个 key，不是持有它的人——5 个各 $20 的 key 允许一个工程师一天花 $100。

### OpenRouter 组织能容纳多少人？

组织默认上限 10 名成员，更多请联系支持。只有管理员能购买额度或查看计费，成员创建 key 并使用组织资源。组织 key 的所有用量都从同一份额度池扣。

### 组织成员能互相看到用量吗？

能——看的是用量元数据。组织上下文里 Activity 展示每个成员的模型、成本和时间数据，可以按 API key 过滤或按 Creator 分组归属花费。提示词和响应从不存储，动态里只有花费与用量数据，没有内容。

### 能限制团队使用哪些模型吗？

能，两种方式。Preset 为引用它（`@preset/{slug}`）的流量设默认模型或回退列表，但 key 可以跳过 preset 直接调任何模型。Guardrail 的模型白名单是按成员或按 key 的硬限制，白名单之外的请求一律 403、与 preset 无关。需要的是执法而不只是默认，就用 guardrail。

### 能封顶一个人每天的支出吗？

能。给组织成员分配 guardrail 预算，每人都有自己的日/周/月额度。其所有 key 的合计花费触顶时，请求以 403 被拦。按 key 的限额封的是 key 不是人——真正的人均预算要用按成员分配的 guardrail。

### OpenRouter 必须付费吗？有最低消费吗？

不必。按量付费无最低消费，且有免费档。标准按量账户的平台费是额度购买的 5.5%，我们不给提供商定价加价，目录价就是模型成本。当前档位和费用见[定价](https://openrouter.ai/pricing)。

### 怎么查看我的 OpenRouter 用量？

三处可看。每个 API 响应自带含 token 计数和成本的 `usage` 对象；`GET /api/v1/key` 返回可代码轮询的逐 key 用量字段；[Activity 页面](https://openrouter.ai/activity)展示 Spend、Tokens 和 Requests，支持分组与 CSV/PDF 导出。
