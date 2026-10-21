# 情报变更日志

> **产物**（逐日追加，超上限裁最旧日块）：AI 核查每日采纳的免费额度事实变化，带前值 → 后值，最新在前。
> 保留最近约 150 条厂商-天记录；人工修订请直接改本文件（格式合法的改动会随重写保留，被裁掉的旧日块不会回来）。

## 2026-10-21
### Cloudflare Workers AI（`cloudflare_workers_ai`）
- 摘要：付费前沿模型名单新增 @cf/deepseek-ai/deepseek-v4.1-flash-1017，该模型不享受免费额度，需付费订阅或预付额度才能访问
- `free_models`：目录内可免费使用的模型共享 **每日 10,000 Neurons 免费额度**（官方定价页原文 “use a total of 10,000 Neurons per day at no charge”），UTC 0 点刷新；代表模型 `@cf/meta/llama-4-scout-17b`、`llama-3.3-7… → 目录内可免费使用的模型共享 **每日 10,000 Neurons 免费额度**（官方定价页原文 “use a total of 10,000 Neurons per day at no charge”），UTC 0 点刷新；代表模型 `@cf/meta/llama-4-scout-17b`、`llama-3.3-7…
- `tier_caveats`：免费额度是账号级 **每日 10,000 Neurons 共享总额度**（不是每模型各 1 万），所有限额每日 00:00 UTC 重置；超额按 $0.011 / 1,000 Neurons 计费，需开通 Workers Paid、kimi-k2.6/k2.7-code、glm-5.2/5.3/5.3-flash、d… → 免费额度是账号级 **每日 10,000 Neurons 共享总额度**（不是每模型各 1 万），所有限额每日 00:00 UTC 重置；超额按 $0.011 / 1,000 Neurons 计费，需开通 Workers Paid、kimi-k2.6/k2.7-code、glm-5.2/5.3/5.3-flash、d…

## 2026-10-20
### Together AI（`together_ai`）
- 摘要：Muse Spark Open 限时免费活动已结束，恢复为正常收费模型（输入 $1.25/1M tokens，输出 $4.25/1M tokens）
- `free_models`：`Ternary Bonsai 27B` —— 输入与输出均定价为 **$0.00/1M tokens**（需充值门槛）、`Muse Spark Open (Free for limited time)` —— **限时免费活动**，输入与输出均定价为 **$0.00**（活动有效期至 2026/10/18；需充值门… → `Ternary Bonsai 27B` —— 输入与输出均定价为 **$0.00/1M tokens**（需充值门槛）、`Tev1 4B Experimental` —— 输出免费（Free），输入收取 **$0.04/1M tokens**（需充值门槛）、**平台调用限制**：官方计费文档明确平台不提供免费试用，…
- `promotions`：限时活动：Muse Spark Open (Free for limited time) 提供 $0.00 输入/输出优惠，有效期至 2026 年 10 月 18 日（Promotion valid until 10/18/2026）。 → 无
### InceptionLabs（`inception_labs`）
- 摘要：官方主推模型升级为 Mercury 3（文档快速入门已切为 mercury-3），并上线 launch 50% 折扣定价，涵盖 Mercury 3、Mercury Voice 与 Mercury Decide。
- `free_models`：`mercury-2.5`（diffusion-based LLM，官方文档唯一具名的免费调用模型）；另含 Mercury Voice、Mercury Router、付费定价：Mercury 2.5 输入 $0.20 / 百万 tokens、输出 $0.75 / 百万 tokens；Mercury Voice 输入 … → `mercury-3` —— 官方文档 Quick Start 具名调用的最新 diffusion LLM 模型，共享新用户 **1 亿 free tokens**、`Mercury Voice`、`Mercury Decide` —— 官方产品线模型（超出免费额度后适用 Launch 50% 优惠价：Mercury…
- `tier_caveats`：1 亿 tokens 的**有效期官方文档未载明**，也未说明是否按月重置，按一次性到账规划用量、免费额度对应 Mercury 系列模型；超出后按量计费（Mercury 2.5 输入 $0.20 / 输出 $0.75 每百万 tokens），需到 Billing 添加付款方式 → 1 亿 tokens 的**有效期官方文档未载明**，也未说明是否按月重置，按一次性到账规划用量、免费额度对应 Mercury 系列模型；超出后需到 Billing 添加付款方式按量计费（Mercury 3 上线 50% 折扣价：输入 $0.10 / 输出 $0.35 每百万 tokens）
- `promotions`：无其他活动记载。 → Mercury 3 上线促销（50% off at launch），Mercury 3、Mercury Voice、Mercury Decide 提供半价定价优惠。
- `openai_compat`：{"summary": "新号 1 亿 free tokens，免信用卡", "api_key_label": "Dashboard 申请", "api_key_url": "https://platform.inceptionlabs.ai/dashboard/api-keys", "base_url": "htt… → {"summary": "新号 1 亿 free tokens，免信用卡", "api_key_label": "Dashboard 申请", "api_key_url": "https://platform.inceptionlabs.ai/dashboard/api-keys", "base_url": "htt…
### Mancer（`mancer`）
- 摘要：更正免费模型范围：官方模型列表中仅 MythoLite 标注为 FREE（上下文 2560、输出上限 150），MythoMax 及 Magnum 72B 均为付费模型；且官方说明账户积分负额度下仍可使用免费模型。
- `free_models`：官方模型页标注 **FREE** 的模型（如 `MythoLite`，及 MythoMax、Magnum 72B v4 等角色扮演向模型）—— **0 元免费调用**（清单以 mancer.tech/models 页面 FREE 标签为准）、付费另有 DeepSeek V4 Flash 284B、GLM 4.7 35… → `MythoLite` (LLaMA 2 13B) —— **0 元免费调用**（上下文 2560 tokens，单次输出上限 150 tokens）、其余模型按 Token 计费 —— 包括 `MythoMax`、`Magnum 72B v4`、`Qwen3.8 27B`、`DeepSeek V4 Flash`、`…
- `tier_caveats`：只有模型页标 **FREE** 的角色扮演向模型 0 元（如 MythoLite 等），其余模型按 token 计费；FREE 清单随页面调整、免费模型同样限速，具体 RPM 以模型页标注为准 → 当前模型列表中仅 `MythoLite` 标注为 **FREE**，其余角色扮演及通用模型（如 MythoMax、Magnum 72B 等）均需消耗积分计费、若退款导致账户积分变为负数，官方明确仍可继续调用免费模型
### 科大讯飞星火（`iflytek_spark`）
- 摘要：星火API新增 Spark-X2.5-1.7B 免费及 Spark-X2.5-4B 限时免费领取，均支持在产品页免费领取。
- `free_quota`：**无独立注册赠金**；唯一免费项为星火 Lite（额度需在星火产品页领取，规则以领取页为准）；进阶版本无公开赠送额度记载 → **无独立注册赠金**；Spark-X2.5-1.7B 标明“免费”，Spark-X2.5-4B 标明“限时免费”，Spark Lite 等模型在产品页支持“免费领取”
- `free_models`：**星火 Lite** —— 官方 HTTP 调用文档原文“具有更高的响应速度，**支持免费使用**”，免费额度在星火产品页领取（QPS/限速以领取页规则为准）、付费版本：Pro、Pro-128K、Max、Max-32K、**4.0 Ultra**（已升级至 X1.5 快思考模式），另有深度推理 **X2** 产品线… → **Spark-X2.5-1.7B** —— 官方定价标明“免费”，1.7B级端侧通用语言Dense模型（1M上下文），需在产品页点击“免费领取”、**Spark-X2.5-4B** —— 官方定价标明“限时免费”，4B级端侧通用语言Dense模型（1M上下文），需在产品页点击“免费领取”、**Spark Lite*…
- `tier_caveats`：免费的只有**星火 Lite 一个模型**，且额度**必须先到星火产品页手动领取**（不是注册自动到账）；QPS / 限速以领取页规则为准、进阶版本（Pro/Max/4.0 Ultra 等）无公开免费额度 → 免费额度需在产品页手动点击“免费领取”后使用，非注册自动到账、Spark-X2.5-4B 标注为“限时免费”，存在活动到期转收费风险、旗舰模型 Spark-X2.5、Spark X2 及 Spark-X2-Flash 为付费调用
### NVIDIA NIM（`nvidia_nim`）
- 摘要：官网首页代表性免费模型更新，展示了 Nemotron 3.5 Super VL、Nemotron 3.5 Lightning、DeepSeek V4.1 Flash 等最新模型。
- `free_models`：API 目录代表模型 `nvidia/nemotron-3-ultra-550b-a55b`、`nemotron-3.5-lightning-30b`、`nemotron-3-super-120b`、`deepseek-v4-pro/flash`、`kimi-k3`、`gpt-oss-120b/20b`、`glm-5… → 官网首页代表模型 `nvidia/nemotron-3-ultra-550b-a55b`、`nvidia/nemotron-3.5-super-vl-120b-a12b`、`nvidia/nemotron-3.5-lightning-30b-a3b`、`deepseek-ai/deepseek-v4.1-flash`…

## 2026-10-18
### DeepSeek（`deepseek`）
- 摘要：deepseek-flash 底层版本更新为 DeepSeek-V4.1-Flash-1017；DeepSeek Harness/Claude Code/Codex 中访问 Search/Fetch 接口目前未计费，明确将于 2026 年 11 月 1 日起开始收费
- `free_models`：**无免费模型层**，全量模型按量计费：`deepseek-flash`（DeepSeek-V4.1-Flash，支持图像理解与思考模式）、`deepseek-v4-pro`（DeepSeek-V4-Pro-0813）；上下文 1M（最大输出 384K）、峰谷定价（元/百万 tokens，高峰为工作日 9:00–12… → **无免费模型层**，全量模型按量计费：`deepseek-flash`（DeepSeek-V4.1-Flash-1017，支持图像理解与思考模式）、`deepseek-v4-pro`（DeepSeek-V4-Pro-0813）；上下文 1M（最大输出 384K）、峰谷定价（元/百万 tokens，高峰为工作日 9:…
- `promotions`：实行**峰谷定价**（元/百万 tokens，高峰为工作日 9:00–12:00、14:00–18:00，空闲时段半价）：deepseek-flash 输出 8.0（高峰）/4.0（空闲），缓存命中 0.04/0.02；deepseek-v4-pro 输出 27.0/13.5，缓存命中 0.30/0.15。**限时活… → 实行**峰谷定价**（元/百万 tokens，高峰为工作日 9:00–12:00、14:00–18:00，空闲时段半价）：deepseek-flash 输出 8.0（高峰）/4.0（空闲），缓存命中 0.04/0.02；deepseek-v4-pro 输出 27.0/13.5，缓存命中 0.30/0.15。**限时免…
### Together AI（`together_ai`）
- 摘要：官方定价页新增 Muse Spark Open 限时免费活动（输入/输出均为 $0.00，有效期至 2026 年 10 月 18 日），但调用仍受平台最低 $15 充值门槛约束。
- `free_models`：**无免费试用，但存在 $0 / 输出免费定价模型**：官方价目表中 Ternary Bonsai 27B 输入/输出均为 $0.00/1M tokens；Tev1 4B Experimental 输出免费（Free），输入收取 $0.04/1M tokens。调用前平台访问仍需首次最低 $15 充值；其余模型均需充… → `Ternary Bonsai 27B` —— 输入与输出均定价为 **$0.00/1M tokens**（需充值门槛）、`Muse Spark Open (Free for limited time)` —— **限时免费活动**，输入与输出均定价为 **$0.00**（活动有效期至 2026/10/18；需充值门…
- `promotions`：Serverless 按量计费 + 专用 GPU 集群；支持 OpenAI SDK 兼容调用。 → 限时活动：Muse Spark Open (Free for limited time) 提供 $0.00 输入/输出优惠，有效期至 2026 年 10 月 18 日（Promotion valid until 10/18/2026）。

## 2026-10-17
### xAI Grok（`xai_grok`）
- 摘要：新增最新旗舰模型 grok-4.7 及 grok-build-0.1，API 全线模型依然需充值使用，无免费层
- `free_models`：**API 无免费模型层**：`grok-4.6`（编码模型 Grok Build）、grok-4.5、grok-4.3、grok-4.20 系列（reasoning / non-reasoning / multi-agent，上下文最高 1M）均需充值；旧 `grok-2`/`grok-beta` 已退役 → **API 无免费模型层**：最新旗舰 `grok-4.7`（支持 Grok Build 智能体编码）、`grok-build-0.1`、`grok-4.6`、`grok-4.5`、`grok-4.3`、`grok-4.20` 系列（上下文最高 1M）均按 Token 计费需充值；旧 `grok-2`/`grok-b…
### DeepSeek（`deepseek`）
- 摘要：新增网页搜索与抓取（Search & Fetch）API 定价，并上线 Claude Code 与 Codex 网页搜索两周限时免费活动
- `promotions`：实行**峰谷定价**（元/百万 tokens，高峰为工作日 9:00–12:00、14:00–18:00，空闲时段半价）：deepseek-flash 输出 8.0（高峰）/4.0（空闲），缓存命中 0.04/0.02；deepseek-v4-pro 输出 27.0/13.5，缓存命中 0.30/0.15。 → 实行**峰谷定价**（元/百万 tokens，高峰为工作日 9:00–12:00、14:00–18:00，空闲时段半价）：deepseek-flash 输出 8.0（高峰）/4.0（空闲），缓存命中 0.04/0.02；deepseek-v4-pro 输出 27.0/13.5，缓存命中 0.30/0.15。**限时活…
### Hugging Face（`huggingface`）
- 摘要：Hugging Face 取消了免费用户每月 $0.10 的 Inference Providers 免费额度，免费用户需充值或升级 PRO 才能使用 API。
- `free_quota`：Inference Providers 免费用户**每月 $0.10** 额度（官方定价文档原文，标注 “subject to change”），注册生成 Access Token 即可、免信用卡；PRO 会员 **$9/月**含每月 **$2** 通用推理额度 → 免费用户**无免费额度**（已取消原每月 $0.10 免费试用额度），需购买额度或升级为 PRO 用户；PRO 会员 **$9/月**含每月 **$2** 通用推理额度
- `validity`：免费额度**按月发放** → PRO 会员额度**按月发放**；免费用户无额度
- `free_models`：经 18 家 provider（Cerebras/Together/Fireworks/Groq/Novita 等）路由的开源模型：`openai/gpt-oss-120b`、`deepseek-ai/DeepSeek-V3/R1`、`FLUX.1-dev` 等 —— 共享免费用户 **$0.10/月** 额度（原 … → 无免费模型 —— 官方已取消 Free Users 的每月免费额度，调用 Inference Providers 需充值或开通 PRO
- `tier_caveats`：免费用户每月仅 **$0.10** 推理额度（官方标注 “subject to change”），只够极低频测试，不是长期主力额度、原 Serverless 社区免费集群 2025 年 7 月起已改为 hf-inference provider 且主要提供 CPU 推理；PRO $9/月也只含 $2 额度 → 官方已正式取消免费用户的每月 $0.10 额度，未付费免费账号无法免费调用 Inference Providers API、PRO 用户每月含 $2 通用额度，可用于 Inference Providers、Inference Endpoints、Spaces 硬件等
### OpenRouter（`openrouter`）
- 摘要：官方定价 FAQ 明确免费模型数量为 25+ 款（4 家供应商），并补充失败请求同样计入每日额度上限、账户负余额会阻断免费模型调用等规则。
- `free_models`：**`:free` 后缀模型**（实时目录约 16 个）—— **限速 20 RPM**；每日请求上限 **50 次**（累计购买不足 10 credits）或 **1,000 次**（购满 10 credits），官方 limits 文档常量 FREE_MODEL_RATE_LIMIT_RPM=20 / FREE_… → **`:free` 后缀模型**（官方标称 25+ 款免费模型，4 家免费提供商）—— **限速 20 RPM**；每日请求上限 **50 次**（未购满 $10）或 **1,000 次**（账户累计购买至少 $10 credits），失败请求同样计入每日上限、当前 :free 实例：`google/gemma-4-…
- `tier_caveats`：**只有带 `:free` 后缀的模型免费**，同名付费模型照常扣费；免费实例约 16 个且随上游厂商变动（旧 llama-3.3-70b / gemma-2 / deepseek-r1 等 :free ID 已下架）、限速 20 RPM；每日 50 次（累计充值不足 $10）或 1,000 次（购满 $10 cre… → **只有带 `:free` 后缀的模型免费**，同名付费模型照常扣费；官方提供 25+ 款免费模型，随上游变动、限速 20 RPM；每日 50 次（未购满 $10）或 1,000 次（购满 $10 credits 后），**失败请求同样计入每日上限**、若账户存在负余额（negative balance），将封锁免费…
### Fireworks AI（`fireworks_ai`）
- 摘要：Muse Glimmer 30B SFT 限时免费微调活动的截止日期从 10/31 延长至 11/30。
- `free_quota`：官方已下线新号 $1 免费额度表述，全面转向预付费充值（需绑定支付方式购买点数）；当前仅存限时免费项目：Muse Glimmer 30B SFT 微调截至 10/31 完全免费且免绑定信用卡 → 官方已下线新号 $1 免费额度表述，全面转向预付费充值（需绑定支付方式购买点数）；当前仅存限时免费项目：Muse Glimmer 30B SFT 微调截至 11/30 完全免费且免绑定信用卡
- `validity`：限时活动至 10/31 截止 → 限时活动至 11/30 截止
- `free_models`：`Muse Glimmer 30B` —— SFT 监督微调限时免费，支持 UI 与 Serverless Training API（至 10/31 截止，无需信用卡） → `Muse Glimmer 30B` —— SFT 监督微调限时免费，支持 UI 与 Serverless Training API（至 11/30 截止，无需信用卡）
- `tier_caveats`：原新用户 $1 试用额度已取消，常规 Serverless 推理需添加支付方式充值购买积分（pre-paid）后方可调用、免费微调活动仅限 Muse Glimmer 30B SFT，且截至 10/31 → 原新用户 $1 试用额度已取消，常规 Serverless 推理需添加支付方式充值购买积分（pre-paid）后方可调用、免费微调活动仅限 Muse Glimmer 30B SFT，且截至 11/30
- `promotions`：Muse Glimmer 30B SFT 限时免费（至 10/31，免信用卡）；Batch 批处理推理按 Serverless 定价的 5 折计费（50% of serverless pricing）。 → Muse Glimmer 30B SFT 限时免费（至 11/30，免信用卡）；Batch 批处理推理按 Serverless 定价的 5 折计费（50% of serverless pricing）。

## 2026-10-14
### Google Gemini（`google_gemini`）
- 摘要：Google 上线新旗舰推理模型 Gemini 4 Argon，官方明确注明其不适用于免费层级
- `free_models`：`Gemini 3.8 / 3.7 / 3.6 Flash`、Gemini 3.5 Flash/Flash-Lite、Gemini 3.1 Flash-Lite、Gemini 3 Flash Preview、`Gemini 2.5 Pro/Flash/Flash-Lite`、`Gemma 4`、Gemini Embe… → `Gemini 3.8 / 3.7 / 3.6 Flash`、Gemini 3.5 Flash/Flash-Lite、Gemini 3.1 Flash-Lite、Gemini 3 Flash Preview、`Gemini 2.5 Pro/Flash/Flash-Lite`、`Gemma 4`、Gemini Embe…
- `tier_caveats`：**不是所有模型都有免费层**：3.x Flash / Gemma 4 / Embedding 系列可用；`Gemini 3.1 Pro Preview`、Nano Banana 图像系列**无免费层**，调错模型会直接付费、**隐私代价**：免费层输入/输出数据可能被用于改进 Google 产品；敏感数据不要走免费… → **不是所有模型都有免费层**：3.x Flash / Gemma 4 / Embedding 系列可用；`Gemini 4 Argon`、`Gemini 3.1 Pro Preview`、Nano Banana 图像系列**无免费层**，调错模型会直接付费、**隐私代价**：免费层输入/输出数据可能被用于改进 Go…
### MiniMax（`minimax`）
- 摘要：订阅体系由 Token Plan 更新为 M Plan（Go/Explore/Build 档位）；上线 M3.1 Flash Preview 文本模型并发布 M2.5/M2.7 系列模型下线通知；Free 档不支持 API Key 接入，无免费 API 额度。
- `free_models`：**无免费模型层**：当前旗舰 `MiniMax-M3`（官方原文：全新 MSA 注意力架构、1M 上下文、原生多模态 Coding/Agentic 模型）、`MiniMax-M2.7`/M2.7-highspeed，以及视频 `H3`、`speech-2.8`、`music-3.0` 均为付费（Token Plan… → **无免费 API 模型层**：Free 档不支持 API Key 接入（仅限 MiniMax Code 客户端与网页端有限可用 `M3.1 Flash Preview` 及图像声音模型）、**API 付费与下线动态**：API 调用需订阅 M Plan（Go/Explore/Build）或购买积分包，支持文本模型 …
- `promotions`：**Token Plan 订阅**（官方定价文档）：Plus ¥49/月、Max ¥119/月、Ultra ¥469/月，覆盖 M3/M2.7/图像/语音（Max/Ultra 支持 Hailuo2.3 视频生成，H3 视频、音色设计等特殊模型除外）；预付积分包固定为入门版 ¥30（4,489 积分）、进阶版 ¥150… → **M Plan 订阅**：个人 AI 订阅方案，提供 Go（年付 ¥490/年）、Explore（Go 的 3 倍用量，年付 ¥1,190/年）、Build（Go 的 12 倍用量，年付 ¥4,690/年），支持通过 API Key 接入编程与 Agent 工具；**积分包**：入门版 ¥30（4,489 积分）、…
- `openai_compat`：{"summary": "新用户 Token Plan 订阅/体验", "api_key_label": "控制台申请", "api_key_url": "https://platform.minimax.cn/console/access?tab=api-keys", "base_url": "https://ap… → {"summary": "M Plan 订阅或积分包通过 API Key 接入", "api_key_label": "控制台申请", "api_key_url": "https://platform.minimax.cn/console/access?tab=api-keys", "base_url": "http…
### Fireworks AI（`fireworks_ai`）
- 摘要：官方页面移除了新账号 $1 免费额度并转为预付费充值模式，同时新增 Muse Glimmer 30B SFT 限时免信用卡免费训练活动
- `free_quota`：新账号送 **$1 免费额度**（官方定价页原文 “Get started with $1 in free credits.”），邮箱注册自助开通，用完即止 → 官方已下线新号 $1 免费额度表述，全面转向预付费充值（需绑定支付方式购买点数）；当前仅存限时免费项目：Muse Glimmer 30B SFT 微调截至 10/31 完全免费且免绑定信用卡
- `validity`：用完即止 → 限时活动至 10/31 截止
- `free_models`：serverless 模型可用 $1 赠金抵扣：`Kimi K3`（$3/$15）、Kimi K2.7 Code、`DeepSeek V4 Pro 0813`（$1.32/$3.96）、`DeepSeek V4 Flash 0731`（$0.22/$0.66）、Qwen 3.8 Max / 3.7 Plus 等 → `Muse Glimmer 30B` —— SFT 监督微调限时免费，支持 UI 与 Serverless Training API（至 10/31 截止，无需信用卡）
- `tier_caveats`：**$1 额度极小**，只够几十次测试调用，用完即止、不重置、现行 serverless 价目已无 Llama 聊天模型单列（未列名模型按尺寸档位计费） → 原新用户 $1 试用额度已取消，常规 Serverless 推理需添加支付方式充值购买积分（pre-paid）后方可调用、免费微调活动仅限 Muse Glimmer 30B SFT，且截至 10/31
- `preconditions`：邮箱注册即可自助开通（self-serve） → 参与限时微调无需信用卡（No credit card required）；常规推理需要绑定支付方式购买积分
- `promotions`：Batch 5 折；支持 Function Calling 与 JSON Schema 结构化输出。 → Muse Glimmer 30B SFT 限时免费（至 10/31，免信用卡）；Batch 批处理推理按 Serverless 定价的 5 折计费（50% of serverless pricing）。

## 2026-10-13
### Cursor（`cursor_ide`）
- 摘要：定价体系全面调整，免费层包含有限智能体与 Grok 聊天/Imagine 用量且额度每周重置，付费档改为 Plus ($8/月) 至 Ultra ($200/月)
- `free_quota`：**Hobby 档长期免费**：官方定价页原文 “Free … ✓ No credit card required ✓ Limited Agent requests ✓ Access to Composer”——免信用卡、Agent 请求受限、可用 Composer；**具体条数定价页未公布** → **免费层长期免费**：官方定价显示 $0/月，包含有限 AI 用量（智能体请求次数有限、聊天请求次数有限；Grok 聊天、图像生成 Imagine 与 Grok 构建有限）；用量池额度每周重置
- `validity`：免费档不限时；Pro $20/月 起为「Extended limits on Agent」的付费升级 → 免费档不限时，用量每周重置；付费升级档位调整为 Plus ($8/月)、高级版 ($30/月)、Super ($100/月)、Ultra ($200/月)
- `free_models`：Agent —— Hobby 档限量请求（Limited Agent requests）、Composer —— 免费档即可访问 → Cursor 智能体 —— 免费档请求次数有限、Grok 聊天 —— 免费档请求次数有限、Grok 图像生成 (Imagine) —— 免费档用量有限、Grok 构建 —— 免费档用量有限
- `promotions`：Pro / Pro+ / Ultra 分档；Grok 等模型按档解锁 → 套餐重构为 Plus ($8/月)、高级版 ($30/月)、Super ($100/月)、Ultra ($200/月)；高级版及以上方提供云端智能体与按 API 标价的第三方模型
### DMXAPI（`dmxapi`）
- 摘要：价格表显示小米 MiMO 系列 3 款 TTS 及音色模型当前限时免费（固定价格 ￥0/次），另有万相/Tripo 等异步结果获取接口免费，其余 500+ 模型仍为按量计费。
- `free_models`：**无公开免费模型层**：第三方聚合转发，模型清单随上游更新，当前文档列出 GPT-5.x、Claude 4.5、Gemini 3、DeepSeek 等系列（以文档站模型列表为准） → `mimo-v2.5-tts` —— 小米精品音色 TTS，限时免费（固定价格 ￥0 / 次，上下文 8k）、`mimo-v2.5-tts-voiceclone` —— 小米音色克隆，限时免费（固定价格 ￥0 / 次，上下文 8k）、`mimo-v2.5-tts-voicedesign` —— 小米音色设计，限时免费…

## 2026-10-12
### SiliconFlow 硅基流动（`siliconflow`）
- 摘要：定价页新增 0 元对话模型 Xing4.0-29B 与 bge-large 系列向量模型，并明确语音仅 ASR/GSR 与 SenseVoiceSmall 免费（TTS 合成收费）
- `free_models`：文本 `PaddleOCR-VL-1.5`、`Hunyuan-MT-7B` —— 定价页标注「免费」，**0 元调用**（限速以官方文档为准）、向量 `bge-m3`、重排 `bge-reranker-v2-m3` —— **0 元免费**、图像 `Kolors`、语音 ASR/TTS 系列 —— **0 元免费**… → 对话 `Xing4.0-29B`、`PaddleOCR-VL-1.5`、`Hunyuan-MT-7B` —— 定价页标注「免费」，**0 元调用**、向量 `bge-m3`、`bge-large-zh-v1.5`、`bge-large-en-v1.5` 与重排 `bge-reranker-v2-m3` —— **0 …
- `tier_caveats`：**0 元只覆盖小模型 / 向量 / 重排 / 画图 / 语音**（PaddleOCR-VL、Hunyuan-MT、bge、Kolors 等）；DeepSeek-V4、GLM-5.x、Kimi-K2.7 等旗舰全部按量计费，只能用 14 元代金券抵扣、免费模型清单随定价页「免费」标签调整，接入前以 pricing 页… → **0 元只覆盖指定开源模型 / 向量 / 重排 / 画图 / 识别语音**（Xing4.0-29B、PaddleOCR-VL、Hunyuan-MT、bge 系列、Kolors、SenseVoice 等）；DeepSeek-V4、GLM-5.x、Kimi-K2.7 等旗舰全部按量计费，需使用 14 元代金券抵扣、免费…
- `openai_compat`：{"summary": "众多 0 元模型 + 注册送 14 元券", "api_key_label": "控制台申请", "api_key_url": "https://cloud.siliconflow.cn/account/ak", "base_url": "https://api.siliconflow.cn… → {"summary": "众多 0 元模型 + 注册送 14 元券", "api_key_label": "控制台申请", "api_key_url": "https://cloud.siliconflow.cn/account/ak", "base_url": "https://api.siliconflow.cn…
### Nebius（`nebius`）
- 摘要：官网移除了旧按需单价及 2026 年远期生效价标注，GPU 云按需价格调整为 B300 $9.50/h、B200 $8.50/h、H200 $5.40/h 等
- `free_models`：**无免费模型层**：Nebius Token Factory（原 AI Studio，studio.nebius.ai 已 301 跳转 tokenfactory.nebius.com）模型目录以后台为准，需账户余额；GPU 云按需 B300 $7.85/h、B200 $7.15/h、H200 $4.50/h 等，… → **无免费模型层**：Nebius Token Factory（原 AI Studio，studio.nebius.ai 已 301 跳转 tokenfactory.nebius.com）模型目录以后台为准，需账户余额；GPU 云按需 B300 $9.50/h、B200 $8.50/h、H200 $5.40/h、H1…

## 2026-10-11
### Qoder（`qoder`）
- 摘要：Qwen3.8-Flash 限免活动已延长超过 9 月 30 日，具体截止日期改为待公布
- `free_models`：基础模型 —— Free 方案长期可用，消息条数受限（Free 列还含有限补全/NES 与 BYOK）、高级（premium）模型 —— 每日领 100 Credits（2026-09-18 起，官方未公布截止）+ Pro 试用 300 Credits 抵扣、限时免费活动 —— `Qwen3.8-Flash` 限免*… → 基础模型 —— Free 方案长期可用，消息条数受限（Free 列还含有限补全/NES 与 BYOK）、高级（premium）模型 —— 每日领 100 Credits（2026-09-18 起，官方未公布截止）+ Pro 试用 300 Credits 抵扣、限时免费活动 —— `Qwen3.8-Flash` 限免已…
### 文心快码 Comate（`comate`）
- 摘要：个人标准版首次赠送额度由「¥10 智能体请求券」调整为「7 天有效期 5000 积分」
- `free_quota`：**个人标准版单价免费**：官方定价文档原文「智能补全 免费」+ 模型额度「赠智能体请求券¥10（首次）」；付费档额度耗尽后可自动切换「免费Auto-Free模式」（专业版 150k tokens/h、旗舰版 500k tokens/h） → **个人标准版单价免费**：官方定价文档原文「智能补全 免费」+ 模型额度「赠7天有效期5000积分（首次）」；付费档额度耗尽后可自动切换「免费Auto-Free模式」（专业版 150k tokens/h、旗舰版 500k tokens/h）
- `validity`：智能补全长期免费；¥10 智能体请求券为首次赠送，按订阅周期刷新、不可提前预支 → 智能补全长期免费；首次赠送的 5000 积分有效期为 7 天
- `free_models`：智能补全 —— 个人标准版免费不限次、智能体请求 —— 首次赠 ¥10 请求券；Auto-Free 模式在额度用尽后兜底（限付费档） → 智能补全 —— 个人标准版免费不限次、模型额度 —— 首次赠 5000 积分（7天有效期）；Auto-Free 模式在额度用尽后兜底（限付费档）
### Zed（`zed`）
- 摘要：Pro 14 天免费试用包含的托管模型由 GPT-5.6 Luna 调整为 GPT-6 Luna
- `validity`：免费档不限时；Pro 试用为 14 天或 $5 GPT-5.6 Luna 用量耗尽即止（“The trial ends when you use the $5 balance or 14 days pass”） → 免费档不限时；Pro 试用为 14 天或 $5 GPT-6 Luna 用量耗尽即止（“The trial ends when you use the $5 balance or 14 days pass”）
- `notes`：「Free forever」指标题档定价长期 $0，非全部 AI 功能免费；试用条款里的 GPT-5.6 Luna 为当前托管模型名 → 「Free forever」指标题档定价长期 $0，非全部 AI 功能免费；试用条款里的 GPT-6 Luna 为当前托管模型名
### 百度智能云千帆（`baidu_qianfan`）
- 摘要：纠正 17 个免费模型的具体清单（实为 ERNIE 4.5 系列、DeepSeek、Kimi-K2、Qwen3 等，非 ERNIE 5.0/5.1），并补充仅支持在线推理、不支持批量推理的限制条件。
- `free_models`：**17 个模型**（含 `ERNIE 5.1`、`ERNIE 5.0`、`ERNIE X1.1`、`ERNIE 4.5-Turbo` 等）—— 新用户**每个模型赠送 100 万 tokens，有效期 3 个月**、旧 ERNIE-Speed/Lite/Tiny 永久免费模型**已下架**，平台当前无永久免费模型 → **17 个指定预置模型**（含 `ERNIE-4.5-Turbo` 系列、`ERNIE-X1-Turbo-32K`、`DeepSeek-R1/V3/V3.1`、`Kimi-K2-Instruct`、`Qwen3/Qwen3-Coder`、`bge-large` 等） —— 首次开通自动发放，**每个模型赠送 100…
- `tier_caveats`：**17 个模型各 100 万 tokens / 3 个月**，额度按模型独立计算；另送的 20 元代金券只有 **1 个月**有效期、旧 ERNIE-Speed / Lite / Tiny **永久免费模型已下架**，平台当前无永久免费层，额度用尽需开通付费 → **17 个模型各 100 万 tokens / 3 个月**，额度按模型独立计算；仅支持抵扣预置模型服务在线推理，不支持批量推理、旧 ERNIE-Speed / Lite / Tiny **永久免费模型已下架**，平台当前无永久免费层，额度用尽需开通付费
- `openai_compat`：{"summary": "17 个模型各 100 万 / 3 个月", "api_key_label": "控制台申请", "api_key_url": "https://console.bce.baidu.com/qianfan/overview", "base_url": "https://qianfan.bai… → {"summary": "17 个模型各 100 万 / 3 个月", "api_key_label": "控制台申请", "api_key_url": "https://console.bce.baidu.com/qianfan/overview", "base_url": "https://qianfan.bai…
### 腾讯混元（`tencent_hunyuan`）
- 摘要：免费额度范围不仅限于 Hunyuan-a13b，而是包含 Hunyuan-a13b、Hunyuan-role-latest、多模态视觉与翻译等 8 款模型共享 100 万 tokens，且嵌入模型独享 100 万 tokens；接口默认 5 并发且耗尽不自动转后付费。
- `free_quota`：**无额外注册赠金**；免费资源即左栏两款模型的 tokens（官方免费额度文档 /document/product/1729/97731） → 首次开通免费赠送生文/多模态 **共 100 万 tokens**（8 款模型共享消耗）+ 文本嵌入模型 **100 万 tokens**，有效期均 **1 年**；默认资源包耗尽后不自动转入后付费
- `free_models`：`Hunyuan-a13b`（共享版）—— 首次开通赠送 **100 万 tokens，有效期 1 年**、文本嵌入模型 —— 赠送 **100 万 tokens，有效期 1 年**、付费旗舰：混元 `Hy4` 预览版（2026-08-28 发布）、`Hy-MT2-Pro`（翻译）、`Hy-Role-Latest`（… → `Hunyuan-a13b` / `Hunyuan-role-latest` / `Hunyuan-translation` / `Hunyuan-translation-lite` / `Tencent HY Vision 1.5 Instruct` / `Hunyuan-turbos-vision` / `Hun…
- `tier_caveats`：**只有两款模型免费**：Hunyuan-a13b 共享版、文本嵌入模型各 100 万 tokens、有效期 1 年；旗舰 Hy4、Hy-Image、角色扮演等按 token 后付费、旧 Hunyuan-Lite / Standard 已下线——流传的「Hunyuan-lite 完全免费」已失效 → 免费额度分两类：8 款生文/视觉/翻译模型**合并共享** 100 万 tokens，以及 `Hunyuan-embedding` 独立 100 万 tokens，有效期均为 1 年、默认情况下，免费资源包耗尽或到期后**不会自动转入后付费**，未主动开通后付费将报错中断、混元生文接口默认限制 **5 个并发**，由…
- `notes`：免费额度限 a13b 共享版与嵌入模型；旗舰 Hy4 等按 token 后付费。 → 赠送额度包含 a13b、角色扮演、翻译和视觉等多款模型（共享 100 万）以及 embedding（独立 100 万）；默认不自动转后付费。

## 2026-10-10
### Anthropic Claude（`anthropic`）
- 摘要：Claude Max 订阅新增每月 $100 至 $200 API 额度，Team 订阅新增最高 $500/月共享 API 额度。
- `promotions`：Pro 订阅 $20/月（年付 $17/月）含 Claude Code；Max 从 $100/月起；Batch 5 折、提示缓存读低至 0.1x。 → Pro 订阅 $20/月（年付 $17/月）含 Claude Code；Max 从 $100/月起，含每月 $100 至 $200 的 Claude Platform API 额度；Team 计划含最高 $500/月池化 API 额度；Batch 5 折、提示缓存读低至 0.1x。
### Together AI（`together_ai`）
- 摘要：平台使用门槛调整：组织首次充值最低金额由 $5 提升至 $15（后续充值最低 $5）；仍然没有免费试用赠额。
- `free_quota`：**无免费试用 / 无赠送**：官方计费文档原文 “Together AI does not currently offer free trials. Access to the Together platform requires a minimum $5 credit purchase.”——$5 是最低充值额而… → **无免费试用 / 无赠送**：官方计费文档原文 “Together AI does not currently offer free trials. Access to the Together platform requires a minimum $15 credit purchase.”——首次充值最低额为 …
- `free_models`：**无免费试用，但存在 $0 / 输出免费定价模型**：官方价目表中 Ternary Bonsai 27B 输入/输出均为 $0.00/1M tokens；Tev1 4B Experimental 输出免费（Free），输入收取 $0.04/1M tokens。调用前平台访问仍需最低 $5 充值；其余模型均需充值后按… → **无免费试用，但存在 $0 / 输出免费定价模型**：官方价目表中 Ternary Bonsai 27B 输入/输出均为 $0.00/1M tokens；Tev1 4B Experimental 输出免费（Free），输入收取 $0.04/1M tokens。调用前平台访问仍需首次最低 $15 充值；其余模型均需充…
- `preconditions`：注册账号并至少充值 $5 → 注册账号并完成组织首次最低 $15 充值（后续充值最低 $5）
### 云知声 Token Hub（`unisound_shanhai`）
- 摘要：官方页首活动更新为 U2 Flash 限时免费无限量调用（2026.09.30-2026.10.31），社群活动变更为扫码入群领 5 亿 Token
- `promotions`：平台聚焦语音与医疗场景，提供语音识别/合成与 OCR 全栈接口；官方页首横幅标注 `U2 Flash` 全新上线，并挂「注册即领 1 亿 Token」活动（查看详情，具体以活动页为准）。 → 平台聚焦语音与医疗场景，提供语音识别/合成与 OCR 全栈接口；官方页首横幅标注 `U2 Flash` 全新上线并限时免费无限量调用（2026.09.30-2026.10.31）；弹窗标注扫码加入交流群领取 5 亿 token。
### InceptionLabs（`inception_labs`）
- 摘要：官网更新模型定价，Mercury 2.5 输入价格由 $0.25 降至 $0.20/1M tokens，并列出 Mercury Voice 等新模型定价
- `free_models`：`mercury-2.5`（diffusion-based LLM，官方文档唯一具名的免费可用模型）；模型列表另含 Mercury 2 / Mercury Edit、付费定价：输入 $0.25 / 百万 tokens、输出 $0.75 / 百万 tokens（免费额度用完后适用） → `mercury-2.5`（diffusion-based LLM，官方文档唯一具名的免费调用模型）；另含 Mercury Voice、Mercury Router、付费定价：Mercury 2.5 输入 $0.20 / 百万 tokens、输出 $0.75 / 百万 tokens；Mercury Voice 输入 …
- `tier_caveats`：1 亿 tokens 的**有效期官方文档未载明**，也未说明是否按月重置，按一次性到账规划用量、免费额度对应 mercury 系列模型；超出后输入 $0.25 / 输出 $0.75 每百万 tokens，需到 Billing 加付款方式 → 1 亿 tokens 的**有效期官方文档未载明**，也未说明是否按月重置，按一次性到账规划用量、免费额度对应 Mercury 系列模型；超出后按量计费（Mercury 2.5 输入 $0.20 / 输出 $0.75 每百万 tokens），需到 Billing 添加付款方式

## 2026-10-08
### Mistral AI（`mistral`）
- 摘要：付费订阅 Vibe Pro 附带的 API credits 调整为 $25.5/月，免费 API 端点与无新用户赠金政策保持不变
- `free_quota`：**无新用户赠金 / 免费实验层**（现行 API 定价页未提及；旧“€5 赠金 / 1 RPS 免费层”无据）；Le Chat 套餐含 $10/月 API credits 属订阅权益 → **无新用户赠金 / 免费实验层**（现行 API 定价页未提及；旧“€5 赠金 / 1 RPS 免费层”无据）；Vibe Pro 订阅套餐含 $25.5/月 API credits 属付费订阅权益

## 2026-10-04
### Together AI（`together_ai`）
- 摘要：官方价目表新增 Tev1 4B Experimental 模型，其输出 token 标为 Free（输入仍收取 $0.04/1M tokens），平台仍需最低充值 $5 方可调用。
- `free_models`：**无免费试用，但存在 $0 定价模型**：官方价目表中 Ternary Bonsai 27B 输入/输出均为 $0.00/1M tokens（Batch API 表同列 $0.00），调用前平台访问仍需最低 $5 充值；其余代表模型 Kimi K3、DeepSeek V4 Pro 0813 / V4 Flash 0… → **无免费试用，但存在 $0 / 输出免费定价模型**：官方价目表中 Ternary Bonsai 27B 输入/输出均为 $0.00/1M tokens；Tev1 4B Experimental 输出免费（Free），输入收取 $0.04/1M tokens。调用前平台访问仍需最低 $5 充值；其余模型均需充值后按…

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
