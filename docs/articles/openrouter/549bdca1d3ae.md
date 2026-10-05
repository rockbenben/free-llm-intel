---
vendor: openrouter
title: 如何将 SillyTavern 连接到 OpenRouter（2026 指南）
original_title: How to Connect SillyTavern to OpenRouter (2026 Guide)
url: https://openrouter.ai/blog/tutorials/sillytavern-openrouter
date: 2026-06-18
lang: zh
captured: 2026-10-05
extractor: readability-v1
status: ok
body_sha: 5f40d74cdae9
translator: agent
---

# 如何将 SillyTavern 连接到 OpenRouter（2026 指南）

OpenRouter ·6/18/2026 · 更新于 9/24/2026

想在 SillyTavern 里用多个 AI 模型，通常意味着分别注册 Anthropic、Google、Mistral 等好几家，每家一个账户，往往还有每月 $20 的订阅。一个 OpenRouter key 把这些换成一份额度余额，外加 SillyTavern 一个下拉框里的 70 多家提供商的 [300 多个模型](https://openrouter.ai/models)。很多可以免费开始，五分钟左右就能开聊。

本指南讲连接步骤、值得一试的角色扮演模型、真正要紧的设置，以及 SillyTavern 用户最常撞到的错误的修法。同一个 key 在编码 agent 和编辑器里也通用，见[如何把 OpenRouter 接入任意编码 agent](https://openrouter.ai/blog/tutorials/any-coding-agent/)。

## 五步把 SillyTavern 连上 OpenRouter

操作都在 SillyTavern 的 API Connections 面板里。目标是让 SillyTavern 指向 OpenRouter、验证 key、选模型，并在长聊之前先发一条测试消息。

- 打开 API Connections 面板（顶栏的插头图标），把 **API Type** 设为 Chat Completion。
- 把 **Chat Completion Source** 设为 OpenRouter。
- 点 **Authorize** 通过 OAuth 流程创建 key，或在 [openrouter.ai/settings/keys](https://openrouter.ai/settings/keys) 生成一个、粘贴进 API key 输入框。
- 点 **Connect**，等 SillyTavern 验证 key。
- 从下拉框选一个模型，点 **Test Message**。

承诺长时间会话之前先把这条测试消息发了。Connect 成功只证明 SillyTavern 能验证你的 key。模型不可用、路由到的提供商服务不了该请求、slug 错了、账户无权访问那个模型、或提示词超出模型上下文窗口时，生成照样会失败。

几乎每个配置都用 Chat Completion。图像内联和工具调用只在 Chat Completion 下可用，这也符合当前 OpenRouter 模型对提示词的期望方式。Text Completion 给高级用户更细的原始提示词格式控制，但不是起步该走的路。如果你那个版本的 OpenRouter 只出现在 Chat Completion 源下面，那是预期行为。完整配置细节在 [SillyTavern 的 OpenRouter 文档](https://docs.sillytavern.app/usage/api-connections/openrouter/)。

## 免费模型与 $10 额度规则

打了 `:free` 标签的模型每 token $0，但请求限制照常在——这一点常让人栽跟头。

| 账户状态 | :free 每日上限 | 每分钟上限 |
| --- | --- | --- |
| 额度不足 $10 | 每天 50 次请求 | 每分钟 20 次 |
| 额度 $10 及以上 | 每天 1,000 次请求 | 每分钟 20 次 |

$10 是一次性的额度购买，不是订阅，且这笔额度在付费模型上照常可用。OpenRouter 对提供商定价[不加价](https://openrouter.ai/pricing)，目录价就是你要付的钱，失败请求不计费。已经直接付钱给某家提供商、想保留那份合同的，改用[自带 key](https://openrouter.ai/docs/guides/overview/auth/byok)。

"免费"模型上出现扣费，几乎总是没注意每 token 计费和请求限制被绕过了：检查你实际选的是不是付费模型、是否启用了付费回退路由、或用的 slug 结尾没有 `:free`。撞到免费模型上限是限制问题，不是免费模型在收你的钱。

## 值得一试的角色扮演模型

DeepSeek V3.2 是长场景便宜可靠的默认。想要更放得开、少些过滤的文字，试 Euryale 系微调模型。角色卡带着复杂指令、模型必须照做时，Hermes 4 405B 比多数模型处理得好。

| 模型 slug | 上下文 | 输入/输出 每 1M | 免费变体 | 适合 |
| --- | --- | --- | --- | --- |
| `deepseek/deepseek-v3.2` | 131K | $0.23 / $0.34 | 无 | 长会话的便宜、连贯默认 |
| `deepseek/deepseek-r1-0528` | 164K | $0.50 / $2.15 | 无 | 重推理的场景与规划 |
| `sao10k/l3.3-euryale-70b` | 131K | $0.65 / $0.75 | 无 | 有性格的 RP 文风加长窗口 |
| `gryphe/mythomax-l2-13b` | 4K | $0.06 / $0.06 | 无 | 经典廉价主力，上下文极小 |
| `aion-labs/aion-rp-llama-3.1-8b` | 32K | $0.80 / $1.60 | 无 | 专为角色扮演调校，轻量 |
| `nousresearch/hermes-4-405b` | 131K | $1.00 / $3.00 | 无 | 复杂角色卡、严格指令遵循 |
| `z-ai/glm-4.6` | 203K | $0.43 / $1.74 | 无 | 强劲通用模型 |
| `mistralai/mistral-large-2512` | 262K | $0.50 / $1.50 | 无 | 精致的付费选择，较少过滤 |

*价格与上下文窗口于 2026-06-16 对照 OpenRouter 目录核实。每 token 费率会变，长会话前请在模型页面确认。*

免费变体会在模型本体不变的情况下来了又走，且上下文窗口经常比付费版小——角色卡开场中途"失忆"通常就是这个原因。围绕任何免费模型搭配置之前，先到 [openrouter.ai/models?q=free](https://openrouter.ai/models?q=free) 确认那个 `:free` slug 还活着。

## 真正要紧的设置与路由

先用保稳定性的设置起步，连接可靠之后再调优。

- 打开流式输出，回复随模型生成逐字出现。
- 把上下文长度滑杆设为上表中模型的真实窗口。免费变体更小，请以目录页为准，别信第三方教程。
- 保留回退提供商开启以保可靠性。只有当你要精确控制请求由哪家提供商服务时才关。
- 长生命周期角色——大系统提示词或重复的 lorebook 上下文——用[提示词缓存](https://openrouter.ai/docs/guides/best-practices/prompt-caching)。它不会让请求免费，但把跨轮重复输入的成本砍下来。

两个路由后缀写在模型 slug 结尾：`:nitro` 排到最快的提供商，`:floor` 排到最便宜的。两者都对应 OpenRouter 的[提供商路由](https://openrouter.ai/docs/guides/routing/provider-selection)排序项。固定角色卡的长会话，`:floor` 加提示词缓存能实打实地降成本。时间敏感的生成则用 `:nitro`。

流式有一个计费提醒：中止流只对支持取消的提供商停止处理和计费。好几家不支持，包括 AWS Bedrock、Groq、Google、Google AI Studio、Minimax 和 Mistral。在这些提供商上——以及非流式请求中——模型会跑完整个生成并全额计费。

## 让角色扮演对话保持私密

OpenRouter 的隐私看两层：OpenRouter 存什么，以及服务你请求的提供商存什么。除非你主动开启日志，OpenRouter 不存提示词或响应，但会保留 token 数、延迟这类用量元数据。下游提供商有自己的保留政策——这就是路由控制重要的原因。

开启[零数据保留](https://openrouter.ai/docs/guides/routing/provider-selection)，按请求或全账户只路由到不存提示词和响应的提供商。OpenRouter 可能对同意记录提示词与补全提供小额折扣；多数角色扮演用户最好保持关闭，别把角色卡和聊天历史暴露进日志。

OpenRouter 自己不过滤内容，但它路由到的提供商各自执行政策——所以说这套配置"无审查"是言过其实。某个模型总是拒绝或砍场景时，那是提供商的审核。换一个过滤更少模型或提供商。具体见[信任中心](https://trust.openrouter.ai)。

## 修最常见的错误

多数 SillyTavern 加 OpenRouter 的问题落进几个模式。从确切的错误信息出发，套用对应的修法。

**"Could not verify OpenRouter token."** 常见错误，且信息有误导性。key 几乎总是好的；真正原因是 DNS 或网络问题挡住了 SillyTavern 访问 openrouter.ai，请求没走到验证那步。到[你的 keys 页面](https://openrouter.ai/settings/keys)确认 key 有效，去掉尾部空格重新粘贴一次，OAuth 的话重新 Authorize，然后重启。仍失败就把 DNS 解析器换到 8.8.8.8 或 1.1.1.1 再重启。多数时候修 DNS 就好。

**401 错误**：OpenRouter 拒绝了 SillyTavern 发来的 key。重新生成、去掉尾部空格再贴一次；调付费模型时确认账户有额度。

**源列表里没有 OpenRouter**：先把 API Type 设为 Chat Completion——其他类型下它不会出现。升级并重启 SillyTavern。只有老版本或特殊安装才动 `config.yaml`，那里的 `show_openrouter_api: true` 是权宜开关，不是默认。改动之前先看[相关的 SillyTavern issue](https://github.com/SillyTavern/SillyTavern/issues/3796)。

**模型下拉框是空的**：账户通常没问题，是 SillyTavern 拉列表失败。刷新连接并重启。还不行就按模型页上的确切 slug 手动输入。

**Connect 成功但生成失败**：Connect 只证明 key 有效。换另一个模型测一次；付费模型确认账户有额度；检查 slug；大型角色卡、lorebook 或历史记录把窗口撑爆时，把上下文长度调低。

## 常见问题

### 怎么把 OpenRouter 连到 SillyTavern？

打开 API Connections 面板，API Type 设 Chat Completion，源选 OpenRouter，点 Authorize 拿 OAuth key 或从 [openrouter.ai/settings/keys](https://openrouter.ai/settings/keys) 粘贴一个，点 Connect，选模型，发一条测试消息。

### OpenRouter 对 SillyTavern 真的免费吗？

对打了 `:free` 标签的模型，是免费的——带限制。免费模型每天 50 次、每分钟 20 次。一次性购买 $10 额度后日上限升到 1,000 次，分钟上限不变。不是订阅，这笔额度在付费模型上照用。

### SillyTavern 角色扮演最好的免费模型是哪个？

`meta-llama/llama-3.3-70b-instruct:free` 是强选择，可用时有 131K 上下文。免费模型的可用性经常变，围绕它搭配置前，先到 [openrouter.ai/models?q=free](https://openrouter.ai/models?q=free) 确认那个 `:free` slug 还在线。

### 怎么修 "could not verify OpenRouter token"？

通常是 DNS 或网络问题，不是 key 坏了。DNS 换 8.8.8.8（Google）或 1.1.1.1（Cloudflare），确认 key 有效，去掉尾部空格重贴，重启 SillyTavern。

### 为什么我的生成提前停止？

先看响应的 finish reason——同一症状有多种原因：提供商审核、max-tokens 限制、上下文长度问题或流式行为。某家提供商总把场景截短，就换模型或提供商试试；只是回答太快结束的话，再调高最大输出设置。

### SillyTavern 用 OpenRouter 还是单提供商 key？

只用一家提供商、要最简计费，用直连 key。想要一套配置接多个模型、提供商路由、某条线路宕机时的回退、可试的免费模型和一个统一的额度池，用 OpenRouter。
