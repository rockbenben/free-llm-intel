# 情报变更日志

> **产物**（逐日追加，超上限裁最旧日块）：AI 核查每日采纳的免费额度事实变化，带前值 → 后值，最新在前。
> 保留最近约 150 条厂商-天记录；人工修订请直接改本文件（格式合法的改动会随重写保留，被裁掉的旧日块不会回来）。

## 2026-09-28
### Anthropic Claude（`anthropic`）
- 摘要：最新模型更新为 Sonnet 5.5，Sonnet 5 已移入 Legacy models；网页端免费版明确支持 Sonnet 与 Haiku（不支持 Opus 与 Fable）。
- `free_models`：**API 无免费模型层**：当前代际 `Claude Fable 5.1`、`Claude Opus 5.5`、`Claude Sonnet 5`、`Claude Haiku 4.5`（上下文最高 1M，随模型而异）均按量付费，`Opus 5`/`Fable 5` 已移入 legacy models；新用户少量测试… → **API 无免费模型层**：当前代际 `Claude Fable 5.1`、`Claude Opus 5.5`、`Claude Sonnet 5.5`、`Claude Haiku 4.5`（上下文最高 1M，随模型而异）均按量付费，`Sonnet 5`/`Opus 5`/`Fable 5` 等已移入 legacy …

## 2026-09-27
### Anthropic Claude（`anthropic`）
- 摘要：官方定价页当前代际已变为 Opus 5.5（Opus 5 与 Fable 5 移入 legacy models），档案所列当前代际模型与“官方建议从 Opus 5 起步”的表述已过时
- `free_models`：**API 无免费模型层**：当前代际 `Claude Fable 5.1`（`claude-fable-5-1`）、`Claude Opus 5`（`claude-opus-5`）、`Claude Sonnet 5`（`claude-sonnet-5`）、`Claude Haiku 4.5`（`claude-hai… → **API 无免费模型层**：当前代际 `Claude Fable 5.1`、`Claude Opus 5.5`、`Claude Sonnet 5`、`Claude Haiku 4.5`（上下文最高 1M，随模型而异）均按量付费，`Opus 5`/`Fable 5` 已移入 legacy models；新用户少量测试…
- `notes`：官方建议多数工作负载从 Opus 5 起步，Fable 5.1 面向复杂推理与长程智能体任务。 → 官方页将 Opus 5.5 定位为日常智能体编码与企业工作的“Daily driver”，Fable 5.1 面向复杂推理与长程智能体任务（“Next generation intelligence for long-running agents”）；另有 Opus 5.5 fast mode（2 倍标准价、最快 2…
### Amazon Bedrock（`aws_bedrock`）
- 摘要：AWS 免费套餐抵扣金为开户立得 $100、最高再得 $100，6 个月内合计最高 $200，档案与攻略中“$100+最高 $200/合计 $300”的数字与官方页不符
- `free_quota`：注册即得 **$100** 额度 + 最高 **$200**（6 个月内分期）探索额度（官方免费套餐页，需绑信用卡）；**AWS Activate** 初创计划最高可申请 **$200,000** 抵扣 → 新 AWS 免费套餐账户开户即得 **$100** 服务抵扣金，探索关键服务最多再得 **$100**，6 个月内合计最高 **$200**（需绑信用卡；账户在开户 6 个月后或抵扣金用完时自行关闭，以先到者为准）；**AWS Activate** 初创计划最高可申请 **$200,000** 抵扣
### 中国电信 天翼云/息壤智算（`china_telecom_tianyi`）
- 摘要：天翼云大模型专项页当前显示 Token Plan 畅享版 29.9 元/月对应 4000 万 Tokens，档案“2500 万 tokens 对应 29.9 元畅享版”与页面数字不符，且页面新增编程 Token Plan 付费系列
- `free_models`：星辰大模型专区托管 GLM、DeepSeek V4/V3.2、Qwen 系列 —— 专区设有 **50 万免费 tokens** 领取入口（以体验中心实际到账为准）、电信自研 `TeleChat3`（TeleChat3-36B-Thinking、TeleChat3-Coder-36B 等）由 Tele-AI 发布并开… → 星辰大模型专区托管 GLM、DeepSeek V4/V3.2、Qwen 系列 —— 专区设有 **50 万免费 tokens** 领取入口（以体验中心实际到账为准）、电信自研 `TeleChat3`（TeleChat3-36B-Thinking、TeleChat3-Coder-36B 等）由 Tele-AI 发布并开…
- `tier_caveats`：「最高 2000 元」是试用中心**多档活动的上限、不是注册即得全额**，实际到账金额与有效期以试用中心规则为准、星辰大模型专区另有 50 万 tokens 领取入口；注意 2500 万 tokens 对应的是 **29.9 元/月付费套餐**，不是免费额度 → 「最高 2000 元」是试用中心**多档活动的上限、不是注册即得全额**，实际到账金额与有效期以试用中心规则为准、星辰大模型专区另有 50 万 tokens 领取入口；注意 **4000 万 tokens 对应的是 29.9 元/月付费畅享版**，不是免费额度
- `notes`：旧档案“2500 万 tokens 免费包”有误：2500 万对应的是 29 元/月付费套餐，非免费额度。 → 旧档案“2500 万 tokens”说法有误：现行官方页畅享版 29.9 元/月对应 4000 万 tokens（2500 万已不在页面出现），均为付费套餐而非免费额度；免费入口仅 50 万 tokens 领取与试用中心体验金。
### Cloudflare Workers AI（`cloudflare_workers_ai`）
- 摘要：官方定价页明确 kimi-k2.6/k2.7-code、glm-5.2/5.3/5.3-flash、deepseek-v4-flash-0731/v4-pro-0813 等模型需付费计费方式（Workers Paid 或预付 AI Gateway credits），不在每日 10,000 Neurons 免费层内，且这些付费模型限速仅 20/50 次每分钟，档案将其列为免费额度覆盖模型有误。
- `free_models`：全目录 **86 个模型**共享免费额度：代表 `@cf/meta/llama-4-scout-17b`、`llama-3.3-70b-fp8`、`@cf/openai/gpt-oss-120b/20b`、`deepseek-v4-flash-0731/v4-pro-0813`、`gemma-4-26b`、`glm-… → 目录内可免费使用的模型共享 **每日 10,000 Neurons 免费额度**（官方定价页原文 “use a total of 10,000 Neurons per day at no charge”），UTC 0 点刷新；代表模型 `@cf/meta/llama-4-scout-17b`、`llama-3.3-7…
- `tier_caveats`：86 个模型**共享每日 10,000 Neurons** 总额度（不是每模型各 1 万），按太平洋时间午夜重置；超额按 $0.011 / 1,000 Neurons 计费，需开 Workers Paid、免费层主要面向 Workers 平台内调用；Neurons 换算随模型不同 → 免费额度是账号级 **每日 10,000 Neurons 共享总额度**（不是每模型各 1 万），所有限额每日 00:00 UTC 重置；超额按 $0.011 / 1,000 Neurons 计费，需开通 Workers Paid、kimi-k2.6/k2.7-code、glm-5.2/5.3/5.3-flash、d…
### Morph Labs（`morph_labs`）
- 摘要：官方定价页显示免费层仅为“每月 200 次请求”，$10 是付费充值起步价、新用户首次充值额外送 $5，并无随 WarpGrep/Glance 工具附带的“每月 $10 免费算力额度”。
- `free_quota`：免费层 **每月 200 次请求** + WarpGrep/Glance 等工具附带 **每月 $10 算力额度**（官方定价页），邮箱注册取 Key，按月重置 → 免费层 **每月 200 次请求**（官方定价页 “200 req free every month”），邮箱注册取 Key、按月重置；付费为按量充值 **$10 起**（From $10），新用户 **首次充值额外送 $5**（First top-up +$5 free）——并无随工具附带的每月 $10 免费算力额度
- `free_models`：OpenAI 兼容端点（api.morphllm.com/v1）：`morph-v3-fast`、`morph-v3-large` 及托管 Qwen 3.5 397B、MiniMax M2.7、DeepSeek V4 Flash 等 —— 免费层 **每月 200 次请求**、WarpGrep/Glance 等工具 … → OpenAI 兼容端点（api.morphllm.com/v1）：`morph-v3-fast`、`morph-v3-large` 及托管 Kimi K3、GLM-5.3、DeepSeek V4/V4.1 Flash、Qwen、MiniMax 等开源模型 —— 免费层 **每月 200 次请求**（200 req f…
- `tier_caveats`：免费层 **每月仅 200 次请求**（按月重置），批量 / 高频使用不够；另有随 WarpGrep / Glance 等工具附带的 $10/月算力额度，不开工具拿不到 → 免费层 **每月仅 200 次请求**（按月重置），批量 / 高频使用不够、$10 是**付费充值的起步价**（From $10），仅新用户**首次充值额外送 $5**（First top-up +$5 free）；旧“随 WarpGrep/Glance 工具附带每月 $10 免费算力额度”的说法与官方定价页不符
- `promotions`：面向 AI 编程与智能体场景优化推理延迟；兼容 OpenAI SDK。 → 面向 AI 编程与智能体场景优化推理延迟，兼容 OpenAI SDK；新用户首次充值送 $5（First top-up +$5 free）；另有面向初创公司的 **Startup Credits**（Up to $5K in API credits for startups）。
### Nebius（`nebius`）
- 摘要：档案记 H200 按需 $4.55/时与官方价目表现价 $4.50/时矛盾，且页面新增 2026-10-01 生效的调价列（B300 $9.50、B200 $8.50、H200 $5.40）；免费额度事实（$25 首付转余额、promo code 送金）不变。
- `free_models`：**无免费模型层**：Nebius Token Factory（原 AI Studio，studio.nebius.ai 已 301 跳转 tokenfactory.nebius.com）模型目录以后台为准，需账户余额；GPU 云 B300 $7.85/h、B200 $7.15/h、H200 $4.55/h 等 → **无免费模型层**：Nebius Token Factory（原 AI Studio，studio.nebius.ai 已 301 跳转 tokenfactory.nebius.com）模型目录以后台为准，需账户余额；GPU 云按需 B300 $7.85/h、B200 $7.15/h、H200 $4.50/h 等，…
### Together AI（`together_ai`）
- 摘要：Together AI 官方价目表中 Ternary Bonsai 27B 输入/输出均为 $0.00/1M tokens，与档案“无免费模型层、均需充值后按量调用”的免费/付费属性判断矛盾（平台仍要求最低 $5 充值、无免费试用）。
- `free_models`：**无免费模型层**，serverless 代表模型 Kimi K3、DeepSeek V4 Pro 0813 / V4 Flash 0731、GLM-5.2、MiniMax M3、Qwen3.8 2.4T A95B、GPT OSS 120B，图像 GPT Image 2、Nano Banana 2、FLUX.2 均… → **无免费试用，但存在 $0 定价模型**：官方价目表中 Ternary Bonsai 27B 输入/输出均为 $0.00/1M tokens（Batch API 表同列 $0.00），调用前平台访问仍需最低 $5 充值；其余代表模型 Kimi K3、DeepSeek V4 Pro 0813 / V4 Flash 0…
### 云知声 Token Hub（`unisound_shanhai`）
- 摘要：实名认证认证礼包在原有 U2/U2-Med/U1-OCR/ASR/TTS 之外新增 U2 Flash、U1-OCR-Med 各 500 万 tokens 与 U2-TTS-Clone、U2-TTS-Design 各 2 万字，且官方页首标注 U2 Flash 全新上线（注册即领 1 亿 Token 活动），免费模型清单需扩充。
- `free_models`：`Unisound U2`（通用）、`U2-Med`（医疗）、`U1-OCR` —— 实名认证即送**各 500 万 tokens**、`U2-ASR`（语音识别）—— 赠送 **5 小时**；`U2-TTS`（语音合成）—— 赠送 **5 万字**、另有 `U2-RadiMed`（放射医疗）等在架模型 → `Unisound U2`（通用）、`U2-Med`（医疗）、`U1-OCR`、`U1-OCR-Med`（医疗 OCR）、`U2 Flash`、`U2-RadiMed`（放射医疗）—— 完成实名认证即送**各 500 万 tokens**、`U2-ASR`（语音识别）—— 赠送 **5 小时**；`U2-TTS`（语…
- `tier_caveats`：额度**按模型/服务分散发放**，不是统一 token 池：U2 / U2-Med / U1-OCR 各 500 万、ASR 5 小时、TTS 5 万字，互不通兑、有效期官方文档未标注，以账户内资源包为准 → 额度**按模型/服务分散发放**，不是统一 token 池：U2 / U2-Med / U1-OCR / U1-OCR-Med / U2 Flash / U2-RadiMed 各 500 万 tokens、ASR 5 小时、TTS 5 万字、TTS-Clone / TTS-Design 各 2 万字，互不通兑、有效期…
- `promotions`：平台聚焦语音与医疗场景，提供语音识别/合成与 OCR 全栈接口。 → 平台聚焦语音与医疗场景，提供语音识别/合成与 OCR 全栈接口；官方页首横幅标注 `U2 Flash` 全新上线，并挂「注册即领 1 亿 Token」活动（查看详情，具体以活动页为准）。
### 通义千问 Qwen（`aliyun_qwen`）
- 摘要：更新为千问AI平台最新规则：文本模型免费额度累计超 7000 万 Token，新上线模型自发布起另享 90 天独立额度，明确区分未认证与已认证用户的用尽即停策略。
- `free_quota`：**无独立注册赠金 / 代金券**；免费额度即按模型发放的 tokens（见左栏，官方免费额度文档 help.aliyun.com/zh/model-studio/new-free-quota） → 大部分模型自动获得独立免费额度（通常每模型 100 万 Token），文本类模型累计超 7000 万 Token；账号开通后新上线的模型亦会自动发放额度
- `validity`：**90 天**（自额度发放起） → **90 天**（开通时已有模型自账号开通起算；新上线模型自发布起算）
- `free_models`：自研旗舰 `qwen3.8-max` 及 Qwen3 系列、Qwen-Coder 系列 —— 新用户**每个模型 100 万 tokens** 免费额度，**有效期 90 天**，**仅限北京区域**（开通模型后自动生效，无需领取）、托管第三方模型（DeepSeek-V4、GLM 等）—— 同样按**每模型 100 … → `qwen-max` / `qwen3.7-max` 等大语言模型、多模态、向量、语音、视觉模型 —— 大部分模型**独立享有 100 万 Token** 免费额度，**有效期 90 天**，快照版本与最新版本额度独立计算，仅抵扣实时推理
- `tier_caveats`：**额度按模型独立发放，不是账号总额**：每个模型各 100 万 tokens / 90 天，几十个模型各领各的；过期或用完即止，不可结转、**仅限北京区域**：跨区域调用不扣免费额度、会直接按后付费计费、开通模型时务必勾选「免费额度用完即停」，否则超额自动转付费；无独立注册代金券 → **额度按模型独立计算，不可合并或跨模型转移**：用完后系统不会自动切换模型，需手动修改 model 参数、**快照版本独立**：带日期后缀版本（如 `qwen-max-2026-05-17`）与主版本独立享有额度、**适用范围受限**：仅抵扣模型实时推理，不可抵扣批量调用、内置工具（联网搜索/图片搜索等）、微调与部…
- `preconditions`：注册阿里云账号；免费额度按官方文档规则在百炼平台开通模型后即可使用 → 注册千问AI平台账号；如提示安全保障需前往权益页面完成认证后自动发放
- `notes`：建议在控制台开启“免费额度用完即停”避免超额扣费；跨区域调用不扣免费额度。 → 账户欠费时即使其他模型有剩余免费额度也无法调用；工作台额度显示存在分钟级延迟。
### 豆包大模型（`volcengine_doubao`）
- 摘要：火山方舟定价页明确说明豆包大语言模型分别提供 50 万 tokens 免费推理额度
- `free_quota`：**无新用户注册赠金 / 文本 token 免费额度表**（官方免费额度文档现行版本）；唯一可确认的免费项为下方 Managed Agents 时长包 → 豆包模型分别提供 **50 万 tokens** 免费推理额度；另提供 Managed Agents 免费运行时长包
- `free_models`：**Managed Agents（Agent 编排）** —— 赠送 **30 小时运行时长 + 500 次 web_search 工具调用，有效期 2 年**（官方免费额度文档）、文本/多模态大模型**无统一免费 token 额度**：当前在线旗舰 `doubao-seed-evolving`（持续进化版）、See… → **豆包系列大语言模型（Doubao-Seed 等）** —— 分别提供 **50 万 tokens** 免费推理额度、**Managed Agents（Agent 编排）** —— 赠送 **30 小时运行时长 + 500 次 web_search 工具调用，有效期 2 年**
