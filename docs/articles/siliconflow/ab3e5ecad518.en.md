---
vendor: siliconflow
title: Release notes
original_title: 
url: https://docs.siliconflow.cn/docs/release-notes/overview
date: 2026-06-11
lang: en
captured: 2026-10-08
extractor: readability-v1
status: ok
body_sha: 6fa3784ccead
---

# Release notes

SiliconFlow platform release notes covering model updates, service adjustments, pricing changes, and new features.

2026.09.28

### [[Model Service Adjustment] ERNIE-Image-Turbo to Be Discontinued](https://docs.siliconflow.cn/docs/release-notes/overview#model-service-adjustment-ernie-image-turbo-to-be-discontinued)

To further optimize resource allocation and provide more advanced and high-quality technical services, the platform will discontinue the following model on **2026-09-30**:

- baidu/ERNIE-Image-Turbo

If you are currently using this model, it is recommended that you switch to alternative models as soon as possible to avoid service disruptions. For a complete list of available models, please visit [Models](https://cloud.siliconflow.cn/models).

2026.09.09

### [[API Service Adjustment] Chat Models Will Ignore the repetition_penalty Parameter](https://docs.siliconflow.cn/docs/release-notes/overview#api-service-adjustment-chat-models-will-ignore-the-repetition_penalty-parameter)

Starting from **2026-09-15**, the `repetition_penalty` parameter passed in requests to chat models (`/v1/chat/completions`, `/v1/messages`) will be ignored, and the server will process it as a fixed value of `1` (i.e., repetition penalty disabled).

This adjustment does not affect other sampling parameters (such as `temperature`, `top_p`, and `top_k`). If your business previously relied on `repetition_penalty` to tune generation results, please evaluate the impact in advance.

2026.09.09

### [[API Service Adjustment] Image Generation API: batch_size Removal and Default Watermark](https://docs.siliconflow.cn/docs/release-notes/overview#api-service-adjustment-image-generation-api-batch_size-removal-and-default-watermark)

To continuously optimize platform services, the `/v1/images/generations` image generation API will undergo the following adjustments on **2026-09-30**:

- **`batch_size` field removal**: The `batch_size` field will no longer be supported in the request body. If you previously relied on this field to generate multiple images in a single request, please make multiple requests instead.
- **Explicit 'AI-generated' watermark enabled by default for image generation API**: This change applies to image generation requests made via the API. An explicit 'AI-generated' watermark will be added to API-generated images by default, while the implicit watermark is always added. If and only if the developer needs to perform further downstream processing on the generated images should they explicitly pass `X-Enable-Watermark: 0` to opt out of the explicit watermark; in that case, the developer is legally obligated to add the relevant explicit watermark to their final output images themselves.

If you are using the image generation API, please review how these changes may affect your business.

2026.09.03

### [[Model Service Adjustment] Nex-N2-Pro, Qwen3.5-397B-A17B, MiniMax-M2.5, and Other Models to Be Discontinued](https://docs.siliconflow.cn/docs/release-notes/overview#model-service-adjustment-nex-n2-pro-qwen35-397b-a17b-minimax-m25-and-other-models-to-be-discontinued)

To further optimize resource allocation and provide more advanced and high-quality technical services, the platform will discontinue the following models on 2026-09-11:

- nex-agi/Nex-N2-Pro
- Qwen/Qwen3.5-397B-A17B
- MiniMaxAI/MiniMax-M2.5
- Pro/MiniMaxAI/MiniMax-M2.5

If you are currently using any of the above models, it is recommended that you switch to alternative models as soon as possible to avoid service disruptions.

2026.08.25

### [[Pricing Adjustment] Time-Based Pricing for DeepSeek-V4-Flash](https://docs.siliconflow.cn/docs/release-notes/overview#pricing-adjustment-time-based-pricing-for-deepseek-v4-flash)

Starting from **September 1, 2026**, the `deepseek-ai/DeepSeek-V4-Flash` model will adopt time-based pricing, with different rates applying to different time periods.

| Billing Period | Cache Hit | Cache Miss (Input) | Output |
| --- | --- | --- | --- |
| 2:00 AM – 8:00 AM (Beijing Time) daily | ¥0.15 / M Tokens | ¥1.5 / M Tokens | ¥4.5 / M Tokens |
| All other hours | ¥0.3 / M Tokens | ¥3 / M Tokens | ¥9 / M Tokens |

If you are using the above model, please monitor your billing statements. Note: Prices are subject to change. Please refer to the real-time prices displayed on the platform.

2026.08.11

### [[API Service Adjustment] /user/info Endpoint Deprecation](https://docs.siliconflow.cn/docs/release-notes/overview#api-service-adjustment-userinfo-endpoint-deprecation)

Due to ongoing system upgrades, the `/user/info` endpoint can no longer align with the platform's account framework. This API will be officially retired on **August 14, 2026 (Friday)** and will no longer be available thereafter.

Going forward, the platform will introduce account-level replacement APIs in due course to help you access the account information you need more conveniently. New endpoints will be announced on this page upon release.

If you are still using the `/user/info` endpoint, please plan to remove the related calls as soon as possible. Thank you for your understanding and cooperation.

2026.07.29

### [[Pricing Adjustment] Cache Hit Input Token Price Adjustment for DeepSeek-V4-Pro](https://docs.siliconflow.cn/docs/release-notes/overview#pricing-adjustment-cache-hit-input-token-price-adjustment-for-deepseek-v4-pro)

- Starting from **2026-08-03**, the cache hit input token price for the `deepseek-ai/DeepSeek-V4-Pro` model will be adjusted as follows:  Cache Hit: ¥1 / M Tokens

If you are using the above model, please monitor your billing statements. Note: Prices are subject to change. Please refer to the real-time prices displayed on the platform.

2026.06.25

### [[Pricing Adjustment] Pricing Adjusted for Nex-N2-Pro, DeepSeek-V4-Pro, DeepSeek-V3.2, and Qwen3.6 Models](https://docs.siliconflow.cn/docs/release-notes/overview#pricing-adjustment-pricing-adjusted-for-nex-n2-pro-deepseek-v4-pro-deepseek-v32-and-qwen36-models)

- The free trial for the `nex-agi/Nex-N2-Pro` model is about to end. Starting from **2026-06-26**, the platform will begin charging:  Input: ¥1.75 / M Tokens Output: ¥7 / M Tokens Cache Hit: ¥0.175 / M Tokens
- The limited-time discount for the `deepseek-ai/DeepSeek-V4-Pro` model will end on **2026-06-30**, after which the original pricing will be restored:  Input: ¥12 / M Tokens Output: ¥24 / M Tokens Cache Hit: ¥0.1 / M Tokens
- Pricing for `Pro/deepseek-ai/DeepSeek-V3.2` and `deepseek-ai/DeepSeek-V3.2` will be adjusted on **2026-06-30**:  Input: ¥4 / M Tokens Output: ¥6 / M Tokens Cache Hit: ¥0.4 / M Tokens
- Pricing for the `Qwen/Qwen3.6-27B` model will be adjusted on **2026-06-30** and will no longer differentiate input length tiers:  Input: ¥3 / M Tokens Output: ¥18 / M Tokens
- Pricing for the `Qwen/Qwen3.6-35B-A3B` model will be adjusted on **2026-06-30** and will no longer differentiate input length tiers:  Input: ¥1.8 / M Tokens Output: ¥10.8 / M Tokens

If you are using any of the above models, please monitor your billing statements. Note: Prices are subject to change. Please refer to the real-time prices displayed on the platform.

2026.06.05

### [[Model Service Adjustment] GLM-4.7, Kimi-K2.5, and Other Models to Be Discontinued](https://docs.siliconflow.cn/docs/release-notes/overview#model-service-adjustment-glm-47-kimi-k25-and-other-models-to-be-discontinued)

To further optimize resource allocation and provide more advanced and high-quality technical services, the platform will discontinue the following models on 2026-06-11:

- Pro/moonshotai/Kimi-K2.5 (requests will be redirected to K2.6)
- Pro/zai-org/GLM-5 (requests will be redirected to GLM-5.1)
- Pro/zai-org/GLM-4.7
- netease-youdao/bce-embedding-base_v1
- netease-youdao/bce-reranker-base_v1

After `Pro/moonshotai/Kimi-K2.5` and `Pro/zai-org/GLM-5` are discontinued, requests will be redirected to `Pro/moonshotai/Kimi-K2.6` and `Pro/zai-org/GLM-5.1` respectively, and billed according to the corresponding model metering standards.

If you are currently using any of the above models, it is recommended that you switch to alternative models as soon as possible to avoid service disruptions.

2026.05.08

### [[Model Service Adjustment] Kimi-K2, GLM-4.6, and Other Models to Be Discontinued](https://docs.siliconflow.cn/docs/release-notes/overview#model-service-adjustment-kimi-k2-glm-46-and-other-models-to-be-discontinued)

To further optimize resource allocation and provide more advanced and high-quality technical services, the platform will discontinue the following models on 2026-05-15:

- moonshotai/Kimi-K2-Thinking
- moonshotai/Kimi-K2-Instruct-0905
- Pro/moonshotai/Kimi-K2-Instruct-0905
- Pro/moonshotai/Kimi-K2-Thinking
- zai-org/GLM-4.6
- zai-org/GLM-4.6V
- THUDM/GLM-Z1-32B-0414
- THUDM/GLM-4.1V-9B-Thinking
- inclusionAI/Ring-flash-2.0
- Qwen/Qwen3-30B-A3B-Thinking-2507
- Qwen/Qwen3-235B-A22B-Instruct-2507

If you are currently using any of the above models, it is recommended that you switch to alternative models as soon as possible to avoid service disruptions.

2026.05.07

### [[Account Security] Unverified Accounts Will Be Restricted from Platform Functions Starting May 15, 2026](https://docs.siliconflow.cn/docs/release-notes/overview#account-security-unverified-accounts-will-be-restricted-from-platform-functions-starting-may-15-2026)

- To further protect the security of your account and platform rights, and to enhance service safety and reliability, accounts that have not completed real-name verification will be unable to use platform functions starting from May 15, 2026. The restriction will be lifted only after verification is completed.

2026.04.22

### [[Model Service Adjustment] KAT-Dev, PaddleOCR-VL, and Other Models to Be Discontinued](https://docs.siliconflow.cn/docs/release-notes/overview#model-service-adjustment-kat-dev-paddleocr-vl-and-other-models-to-be-discontinued)

To further optimize resource allocation and provide more advanced and high-quality technical services, the platform will discontinue the following models on 2026-04-29:

- Kwaipilot/KAT-Dev
- PaddlePaddle/PaddleOCR-VL
- Qwen/QwQ-32B
- Qwen/Qwen2.5-VL-32B-Instruct
- Qwen/Qwen2.5-VL-72B-Instruct
- deepseek-ai/DeepSeek-R1-Distill-Qwen-32B
- deepseek-ai/DeepSeek-R1-Distill-Qwen-14B
- deepseek-ai/DeepSeek-R1-Distill-Qwen-7B
- Qwen/Qwen2.5-Coder-32B-Instruct
- Qwen/Qwen2-VL-72B-Instruct
- internlm/internlm2_5-7b-chat
- IndexTeam/IndexTTS-2

If you are currently using any of the above models, it is recommended that you switch to alternative models as soon as possible to avoid service disruptions.

2026.04.15

### [[Model Service Adjustment] Qwen3-Coder, ERNIE-4.5, and Other Models to Be Discontinued](https://docs.siliconflow.cn/docs/release-notes/overview#model-service-adjustment-qwen3-coder-ernie-45-and-other-models-to-be-discontinued)

To further optimize resource allocation and provide more advanced and high-quality technical services, the platform will discontinue the following models on 2026-04-22:

- Qwen/Qwen3-Coder-480B-A35B-Instruct
- Qwen/Qwen3-235B-A22B-Thinking-2507
- Qwen/Qwen3-VL-235B-A22B-Thinking
- Qwen/Qwen3-VL-235B-A22B-Instruct
- deepseek-ai/DeepSeek-V2.5
- baidu/ERNIE-4.5-300B-A47B
- ascend-tribe/pangu-pro-moe

If you are currently using any of the above models, it is recommended that you switch to alternative models as soon as possible to avoid service disruptions.

2026.03.10

### [[Model Service Adjustment] MiniMax-M2.1, Qwen2, and Other Models to Be Discontinued](https://docs.siliconflow.cn/docs/release-notes/overview#model-service-adjustment-minimax-m21-qwen2-and-other-models-to-be-discontinued)

To further optimize resource allocation and provide more advanced and high-quality technical services, the platform will discontinue the following models on 2026-03-17:

- Pro/MiniMaxAI/MiniMax-M2.1
- Pro/Qwen/Qwen2-7B-Instruct
- Qwen/Qwen2-7B-Instruct
- Pro/THUDM/glm-4-9b-chat
- THUDM/glm-4-9b-chat
- deepseek-ai/deepseek-vl2
- Pro/Qwen/Qwen2.5-VL-7B-Instruct
- Qwen/Qwen3-Next-80B-A3B-Thinking
- Qwen/Qwen3-Next-80B-A3B-Instruct
- Qwen/Qwen2.5-Coder-7B-Instruct
- Pro/Qwen/Qwen2.5-Coder-7B-Instruct

If you are currently using any of the above models, it is recommended that you switch to alternative models as soon as possible to avoid service disruptions.

2026.03.09

### [[Pricing Adjustment] Pricing Adjusted for Qwen3.5-397B-A17B Model](https://docs.siliconflow.cn/docs/release-notes/overview#pricing-adjustment-pricing-adjusted-for-qwen35-397b-a17b-model)

To ensure the rationality and consistency of the platform's model pricing system, the platform has adjusted the pricing for the Qwen/Qwen3.5-397B-A17B model. For details, please visit ["Model Square"](https://cloud.siliconflow.cn/me/models).

Thank you for your support and understanding!

2026.02.02

### [[Model Service Adjustment] MiniMax-M2, Kimi-Dev-72B, and Other Models to Be Discontinued](https://docs.siliconflow.cn/docs/release-notes/overview#model-service-adjustment-minimax-m2-kimi-dev-72b-and-other-models-to-be-discontinued)

To further optimize resource allocation and provide more advanced and high-quality technical services, the platform will discontinue the following models on 2026-02-09:

- MiniMaxAI/MiniMax-M2
- MiniMaxAI/MiniMax-M1-80k
- moonshotai/Kimi-Dev-72B
- Pro/THUDM/GLM-4.1V-9B-Thinking
- Tongyi-Zhiwen/QwenLong-L1-32B
- Qwen/QVQ-72B-Preview
- THUDM/GLM-Z1-Rumination-32B-0414
- Pro/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B
- Qwen/Qwen3-30B-A3B
- stepfun-ai/step3

If you are currently using any of the above models, it is recommended that you switch to alternative models as soon as possible to avoid service disruptions.

2025.12.24

### [[Model Service Adjustment] GLM-4.5, Qwen3-235B, and Other Models to Be Discontinued](https://docs.siliconflow.cn/docs/release-notes/overview#model-service-adjustment-glm-45-qwen3-235b-and-other-models-to-be-discontinued)

To further optimize resource allocation and provide more advanced and high-quality technical services, the platform will discontinue the following models on 2025-12-31:

- zai-org/GLM-4.5
- Qwen/Qwen3-235B-A22B

If you are currently using any of the above models, it is recommended that you switch to alternative models as soon as possible to avoid service disruptions.

2025.12.17

### [[Service Adjustment] Platform Credit Balance Display Format Updated](https://docs.siliconflow.cn/docs/release-notes/overview#service-adjustment-platform-credit-balance-display-format-updated)

To better protect your platform rights and improve resource usage efficiency, the platform has made the following adjustments to the display format of the **Credit Balance** service:

- **Credit balance used before November 30, 2025** will be uniformly converted into a used-up voucher:  The **total amount and used amount** of this voucher are equal to your historically accumulated consumed credit balance; The **remaining available amount of this voucher is currently 0**. It is solely for recording historical entitlements and will not affect subsequent transactions.
- **Credit balance obtained before November 30, 2025, but not yet used** will be converted into an available voucher:  The total amount of this voucher is consistent with the remaining credit balance as of November 30; Currently, the applicable scope of this voucher remains the same as the previous credit balance and can be used normally for deductions. Any future adjustments to the applicable scope will be based on the voucher's description; - This voucher is valid until 23:59:59 on December 31, 2099.
- **After November 30, 2025, platform incentives will be issued in the form of vouchers.**

You can go to 【Balance Top-up > Vouchers】, click on the voucher count to view the voucher list and details.

2025.12.04

### [[Model Upgrade] DeepSeek-V3.2-Exp Upgraded to V3.2](https://docs.siliconflow.cn/docs/release-notes/overview#model-upgrade-deepseek-v32-exp-upgraded-to-v32)

To further optimize the model service quality, the platform will gradually update the `Deepseek-V3.2-Exp` model to the `Deepseek-V3.2` version over the next two days. Requests to `Pro/deepseek-ai/DeepSeek-V3.2-Exp` and `deepseek-ai/DeepSeek-V3.2-Exp` will be redirected to `Pro/deepseek-ai/DeepSeek-V3.2` and `deepseek-ai/DeepSeek-V3.2`, respectively.

2025.11.17

### [[Model Service Adjustment] Ling-1T, Ring-1T, and Other Models to Be Discontinued](https://docs.siliconflow.cn/docs/release-notes/overview#model-service-adjustment-ling-1t-ring-1t-and-other-models-to-be-discontinued)

To further optimize resource allocation and provide more advanced and high-quality technical services, the platform will discontinue the following models on `2025-11-20`:

- inclusionAI/Ling-1T
- inclusionAI/Ring-1T

If you are currently using any of the above models, it is recommended that you switch to an alternative model as soon as possible to avoid any impact on your services.

2025.11.11

### [[Service Adjustment] Rate Limits Adjusted for DeepSeek-R1/V3 and Other Models](https://docs.siliconflow.cn/docs/release-notes/overview#service-adjustment-rate-limits-adjusted-for-deepseek-r1v3-and-other-models)

To further optimize resource allocation and provide more efficient and stable computing power services, the platform will adjust the Rate Limits for certain models starting from `November 11, 2025`.

The models affected by this adjustment are: `Pro/deepseek-ai/DeepSeek-R1`, `Pro/deepseek-ai/DeepSeek-V3`, `Pro/deepseek-ai/DeepSeek-V3.1-Terminus`, `zai-org/GLM-4.6`,`inclusionAI/Ling-1T`，`inclusionAI/Ring-1T`,`MiniMaxAI/MiniMax-M2`;

If your business has specific requirements for high concurrency or large-scale throughput, please contact us to apply for a higher quota.

Thank you for your understanding and support.

2025.11.06

### [[Service Adjustment] Usage Tier Purchase Entry Closed](https://docs.siliconflow.cn/docs/release-notes/overview#service-adjustment-usage-tier-purchase-entry-closed)

To further optimize resource allocation and provide more efficient and stable computing services, the platform will close the purchase entry for Usage Tiers starting from November 7, 2025.

This adjustment only affects the availability of new purchase entries. Your existing Usage Tiers, current usage level, and the platform's automatic upgrade/downgrade mechanism based on consumption amount will remain unaffected.

If you have a need to quickly increase your usage tier or raise your Rate Limits, please contact us.

Thank you for your understanding and support.

2025.09.29

### [[Model Service Adjustment] DeepSeek-V3.1 Models to Be Discontinued](https://docs.siliconflow.cn/docs/release-notes/overview#model-service-adjustment-deepseek-v31-models-to-be-discontinued)

To further optimize resource allocation and provide more advanced and high-quality technical services, the platform will discontinue the following models on 2025-10-09:

- deepseek-ai/DeepSeek-V3.1
- Pro/deepseek-ai/DeepSeek-V3.1

If you are using any of the above models, it is recommended that you switch to V3.1 Terminus as soon as possible to avoid any disruption in service.

2025.09.16

### [[Model Update] Kimi-K2-Instruct Upgraded to 0905 Version](https://docs.siliconflow.cn/docs/release-notes/overview#model-update-kimi-k2-instruct-upgraded-to-0905-version)

To further optimize the quality of model services, the platform updated the moonshotai/Kimi-K2-Instruct and Pro/moonshotai/Kimi-K2-Instruct models to the latest 0905 version on September 15. The previous 0711 version will no longer be available.

The moonshotai/Kimi-K2-Instruct and Pro/moonshotai/Kimi-K2-Instruct models have been removed from the Model Plaza. All corresponding model requests will now be directed to moonshotai/Kimi-K2-Instruct-0905 and Pro/moonshotai/Kimi-K2-Instruct-0905, respectively.

2025.08.22

### [[Model Service Adjustment] HunyuanVideo-HD and Other Video Models to Be Discontinued](https://docs.siliconflow.cn/docs/release-notes/overview#model-service-adjustment-hunyuanvideo-hd-and-other-video-models-to-be-discontinued)

To further optimize resource allocation and provide more advanced and high-quality technical services, the platform will take the following models offline on September 4, 2025:

- tencent/HunyuanVideo-HD
- Wan-AI/Wan2.1-I2V-14B-720P-Turbo
- Wan-AI/Wan2.1-I2V-14B-720P
- Wan-AI/Wan2.1-T2V-14B-Turbo
- Wan-AI/Wan2.1-T2V-14B

If you are currently using any of the above models, it is recommended that you switch to other models as soon as possible to avoid any impact on your services.

2025.06.23

### [[Model Service Adjustment] DeepSeek-R1-0120 and Other Models to Be Discontinued](https://docs.siliconflow.cn/docs/release-notes/overview#model-service-adjustment-deepseek-r1-0120-and-other-models-to-be-discontinued)

To further optimize resource allocation and provide more advanced and high-quality technical services, the platform will take the following models offline on July 3, 2025:

- Pro/deepseek-ai/DeepSeek-R1-0120
- Pro/deepseek-ai/DeepSeek-V3-1226
- Qwen/QwQ-32B-Preview

If you are currently using any of the above models, it is recommended that you switch to other models as soon as possible to avoid any impact on your services.

2025.06.06

### [[Platform Maintenance] Scheduled Maintenance on June 10, 2025](https://docs.siliconflow.cn/docs/release-notes/overview#platform-maintenance-scheduled-maintenance-on-june-10-2025)

To provide more rich, advanced, and high-quality services, the platform will undergo maintenance from 23:00 on June 10, 2025 to 08:00 on June 11, 2025.

Affected by the system maintenance:

- The following functions on cloud.siliconflow.cn will be suspended: registration, login, and other interface operations, including but not limited to the ones listed below.  Online model experience, fine-tuning, and batch inference; Viewing model lists and details on the official website model marketplace; Online top-up, purchasing tiered packages, checking bills, and issuing invoices, etc.;
- The `/user/info` API will be adjusted, and the fields `name`\ `image`\ `and` email will no longer be returned, with a fixed output of an empty string.

The platform's API services will not be affected by the maintenance and can be continuously used. We recommend that you check your account balance in advance to avoid service restrictions due to insufficient balance.

2025.05.29

### [[Model Update] DeepSeek-R1 Upgraded to 0528 Version](https://docs.siliconflow.cn/docs/release-notes/overview#model-update-deepseek-r1-upgraded-to-0528-version)

SiliconFlow will initiate the `DeepSeek R1` model update.

For the `deepseek-ai/DeepSeek-R1` and `Pro/deepseek-ai/DeepSeek-R1` models, an "incremental" update to the latest `0528` version will be carried out. After the update is completed, both models will be upgraded to the `0528` version. If needed, you can still use the older version of the model via `Pro/deepseek-ai/DeepSeek-R1-0120` until `June 28, 2025`, to achieve a smoother transition for your business.

2025.05.23

### [[Model Service Adjustment] Qwen2-1.5B and Other Models to Be Discontinued](https://docs.siliconflow.cn/docs/release-notes/overview#model-service-adjustment-qwen2-15b-and-other-models-to-be-discontinued)

To further optimize resource allocation and provide more advanced and high-quality technical services, the platform will take the following models offline on June 5, 2025:

- Qwen/Qwen2-1.5B-Instruct
- Pro/Qwen/Qwen2-1.5B-Instruct
- Pro/Qwen/Qwen2-VL-7B-Instruct
- THUDM/chatglm3-6b
- internlm/internlm2_5-20b-chat
- deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B
- Pro/deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B

If you are currently using any of the above models, it is recommended that you switch to another model as soon as possible to avoid any impact on your service.

2025.04.17

### [[Model Service Adjustment] HunyuanVideo (non-HD) Model to Be Discontinued](https://docs.siliconflow.cn/docs/release-notes/overview#model-service-adjustment-hunyuanvideo-non-hd-model-to-be-discontinued)

To further optimize resource allocation and deliver more advanced and high-quality technical services, the platform will retire the HunyuanVideo model (non-HunyuanVideo-HD) on April 29, 2025.

If you are currently using this model, we strongly recommend switching to alternative models as soon as possible to avoid service disruptions.

2025.03.26

### [[Model Update] DeepSeek-V3 Upgraded to 0324 Version](https://docs.siliconflow.cn/docs/release-notes/overview#model-update-deepseek-v3-upgraded-to-0324-version)

As of now, the `Pro/deepseek-ai/DeepSeek-V3` and `deepseek-ai/DeepSeek-V3` model has been updated to the latest 0324 version. You can still use the older model via `Pro/deepseek-ai/DeepSeek-V3-1226` to facilitate a smoother transition of your business.

2025.03.25

### [[Model Update] DeepSeek-V3 to Be Upgraded to 0324 Version](https://docs.siliconflow.cn/docs/release-notes/overview#model-update-deepseek-v3-to-be-upgraded-to-0324-version)

SiliconFlow will initiate the update of the DeepSeek V3 model.

For the `deepseek-ai/DeepSeek-V3` and `Pro/deepseek-ai/DeepSeek-V3` models, they will be "progressively" updated to the latest 0324 version.

After the update, both models will be at the 0324 version. If needed, you can still use the old version of the model via `deepseek-ai/DeepSeek-V3-1226` until April 30, 2025, to facilitate a smoother business transition.

2025.03.11

### [[Service Adjustment] api.siliconflow.com Endpoint to Be Phased Out](https://docs.siliconflow.cn/docs/release-notes/overview#service-adjustment-apisiliconflowcom-endpoint-to-be-phased-out)

To better serve global developer users, SiliconFlow will soon launch an international site and gradually open multiple service regions.

Due to this adjustment, the existing api.siliconflow.com API endpoint will be phased out at an appropriate time. Please switch to api.siliconflow.cn as soon as possible to continue using the service.

We have already configured Global Traffic Manager (GTM) for the .cn endpoint to provide the same global access experience as the current .com endpoint. You only need to change the base URL of your API requests to api.siliconflow.cn.

We recommend that you complete the migration by the end of this month (March 31). If you have any questions, please contact us at any time.

2025.03.07

### [[Service Adjustment] RPH and RPD Limits Removed for DeepSeek-R1/V3](https://docs.siliconflow.cn/docs/release-notes/overview#service-adjustment-rph-and-rpd-limits-removed-for-deepseek-r1v3)

To continuously improve user experience, the Rate Limits policy is being adjusted as follows:

Remove the RPH and RPD rate limits for deepseek-ai/DeepSeek-R1 and deepseek-ai/DeepSeek-V3.

As traffic and load change, the policy may be adjusted at any time, and Silicic Flow reserves the right to interpret.

2025.02.27

### [[Model Service Adjustment] Marco-o1, FLUX.1, and Other Models to Be Discontinued](https://docs.siliconflow.cn/docs/release-notes/overview#model-service-adjustment-marco-o1-flux1-and-other-models-to-be-discontinued)

**1. Model Offline notice** To further optimize resource allocation and provide more advanced, high-quality, and compliant technical services, the platform will shut down certain models on March 6, 2025. The specific list of models involved is as follows:

- Chat models:  AIDC-AI/Marco-o1 meta-llama/Meta-Llama-3.1-8B-Instruct Pro/meta-llama/Meta-Llama-3.1-8B-Instruct meta-llama/Meta-Llama-3.1-70B-Instruct meta-llama/Meta-Llama-3.1-405B-Instruct meta-llama/Llama-3.3-70B-Instruct
- Image generation models:  black-forest-labs/FLUX.1-schnell Pro/black-forest-labs/FLUX.1-schnell black-forest-labs/FLUX.1-dev black-forest-labs/FLUX.1-pro stabilityai/stable-diffusion-xl-base-1.0 stabilityai/stable-diffusion-3-5-large stabilityai/stable-diffusion-3-5-large-turbo stabilityai/stable-diffusion-2-1 deepseek-ai/Janus-Pro-7B
- Voice models:  fishaudio/fish-speech-1.5 FunAudioLLM/SenseVoiceSmall FunAudioLLM/CosyVoice2-0.5B fishaudio/fish-speech-1.4 RVC-Boss/GPT-SoVITS
- Video models:  Lightricks/LTX-Video genmo/mochi-1-preview

2025.02.22

### [[Service Adjustment] New RPH/RPD Rate Limits for DeepSeek-R1/V3](https://docs.siliconflow.cn/docs/release-notes/overview#service-adjustment-new-rphrpd-rate-limits-for-deepseek-r1v3)

To ensure the quality of platform services and the rational allocation of resources, the following adjustments to Rate Limits policies are now in effect:

- Adjustments

New RPH Limit (Requests Per Hour, Per Hour Requests)

- Model Scope:deepseek-ai/DeepSeek-R1, deepseek-ai/DeepSeek-V3
- Applicable Users: All users
- Limit Standard: 30 requests/hour

2.New RPD Limit (Requests Per Day, Per Day Requests)

- Model Scope: deepseek-ai/DeepSeek-R1, deepseek-ai/DeepSeek-V3
- Applicable Users: Users who have not completed real-name authentication
- Limit Standard: 100 requests/day

Please note that these policies may be adjusted at any time based on traffic and load changes. Silicon Flowing Reserves the right to interpret these policies.

2025.02.13

### [[Model Service Adjustment] Yi-1.5, SD-3-medium, and Other Models to Be Discontinued](https://docs.siliconflow.cn/docs/release-notes/overview#model-service-adjustment-yi-15-sd-3-medium-and-other-models-to-be-discontinued)

**1. Model Offline notice** To provide more stable, high-quality, and sustainable services, the following models will be offline on **February 27, 2025**:

- 01-ai/Yi-1.5-34B-Chat-16K
- 01-ai/Yi-1.5-6B-Chat
- 01-ai/Yi-1.5-9B-Chat-16K
- stabilityai/stable-diffusion-3-medium
- google/gemma-2-27b-it
- google/gemma-2-9b-it
- Pro/google/gemma-2-9b-it

If you are using any of these models, it is recommended to migrate to other models available on the platform as soon as possible.

2025.02.09

### [[Pricing Adjustment] DeepSeek-V3 Prices Restored to Original Rates](https://docs.siliconflow.cn/docs/release-notes/overview#pricing-adjustment-deepseek-v3-prices-restored-to-original-rates)

**DeepSeek-V3 model prices have been restored to the original price starting from Beijing time February 9, 2025, at 00:00.** Specific prices:

- Input: ¥2/M Tokens
- Output: ¥8/M Tokens

2025.02.03

### [[Feature Update] Reasoning Model reasoning_content Field Separated](https://docs.siliconflow.cn/docs/release-notes/overview#feature-update-reasoning-model-reasoning_content-field-separated)

The display of the reasoning chain in the inference model will be separated into a separate reasoning_content field from the content field. This change is compatible with the OpenAI and DeepSeek API specifications, making it easier for various frameworks and upper-layer applications to trim the conversation in multi-round dialogues. For more details, see the Inference Model [(DeepSeek-R1) Usage](https://docs.siliconflow.cn/docs/userguide/capabilities/reasoning).

2025.02.01

### [[New Model Launch] DeepSeek-R1 and DeepSeek-V3 Now Available](https://docs.siliconflow.cn/docs/release-notes/overview#new-model-launch-deepseek-r1-and-deepseek-v3-now-available)

**Support for deepseek-ai/DeepSeek-R1 and deepseek-ai/DeepSeek-V3 Models** The specific pricing is as follows:

- `deepseek-ai/DeepSeek-R1` Input:￥4/ M Tokens Output: ￥16/ M Tokens
- `deepseek-ai/DeepSeek-V3`  From February 1, 2025, to February 8, 2025, 24:00 Beijing Time, enjoy a limited-time discount price：Input：¥2￥1/ M Tokens Output：¥8￥2/ M Tokens，The original price will be restored from February 9, 2025, 00:00.

2024.12.27

### [[Service Adjustment] Image and Video URL Validity Period Adjusted to 1 Hour](https://docs.siliconflow.cn/docs/release-notes/overview#service-adjustment-image-and-video-url-validity-period-adjusted-to-1-hour)

**Image and Video URL Validity Period Adjusted to 1 Hour** To continue providing you with more advanced and high-quality services, the validity period of image and video URLs generated by large models will be adjusted to 1 hour starting from January 20, 2025.

If you are currently using the image and video generation service, please make sure to back up the files in time to avoid any business disruptions due to URL expiration.

2024.12.24

### [[Pricing Adjustment] LTX-Video Model Will Start Charging](https://docs.siliconflow.cn/docs/release-notes/overview#pricing-adjustment-ltx-video-model-will-start-charging)

**LTX-Video Model Will Start Charging** To continue providing you with more advanced and high-quality services, the platform will start charging for video generation requests using the Lightricks/LTX-Video model starting from January 6, 2025, at a rate of 0.14 yuan per video.

2024.12.13

### [[Model Service Adjustment] DeepSeek-V2-Chat and Other Models to Be Discontinued](https://docs.siliconflow.cn/docs/release-notes/overview#model-service-adjustment-deepseek-v2-chat-and-other-models-to-be-discontinued)

**1. Model Offline notice** To provide more stable, high-quality, and sustainable services, the following models will be offline on December 19, 2024:

- deepseek-ai/DeepSeek-V2-Chat
- Qwen/Qwen2-72B-Instruct
- Vendor-A/Qwen/Qwen2-72B-Instruct
- OpenGVLab/InternVL2-Llama3-76B

If you are using any of these models, it is recommended to migrate to other models available on the platform as soon as possible.

2024.12.5

### [[Model Service Adjustment] Qwen2.5-Math, Hunyuan-A52B, and Other Models to Be Discontinued](https://docs.siliconflow.cn/docs/release-notes/overview#model-service-adjustment-qwen25-math-hunyuan-a52b-and-other-models-to-be-discontinued)

#### [1. Model offline notice](https://docs.siliconflow.cn/docs/release-notes/overview#1-model-offline-notice)

To provide more stable, high-quality, and sustainable services, the following models will be offline on December 13, 2024:

- Qwen/Qwen2.5-Math-72B-Instruct
- Tencent/Hunyuan-A52B-Instruct

If you are using any of these models, it is recommended to migrate to other models available on the platform as soon as possible.

2024.11.14

### [[Model Service Adjustment] Multiple Models to Be Discontinued and Related Service Updates](https://docs.siliconflow.cn/docs/release-notes/overview#model-service-adjustment-multiple-models-to-be-discontinued-and-related-service-updates)

#### [1. Model offline notice](https://docs.siliconflow.cn/docs/release-notes/overview#1-model-offline-notice-1)

To provide more stable, high-quality, and sustainable services, the following models will be offline on November 22, 2024:

- deepseek-ai/DeepSeek-Coder-V2-Instruct
- Qwen/Qwen2-57B-A14B-Instruct
- Pro/internlm/internlm2_5-7b-chat
- Pro/THUDM/chatglm3-6b
- Pro/01-ai/Yi-1.5-9B-Chat-16K
- Pro/01-ai/Yi-1.5-6B-Chat

If you are using any of these models, it is recommended to migrate to other models available on the platform as soon as possible.

**2.Email login method update** To further enhance service experience, the platform will update the login method starting from November 22, 2024: from the original "email account + password" method to an "email account + verification code" method.

**3. New Overseas API Endpoint** A new endpoint for overseas users has been added: [https://api-st.siliconflow.cn](https://api-st.siliconflow.cn). If you encounter network connection issues while using the original endpoint [https://api.siliconflow.cn](https://api.siliconflow.cn), it is recommended to switch to the new endpoint.

2024.10.09

### [[Pricing Adjustment] Vendor-A/Qwen2-72B Model Will Start Charging](https://docs.siliconflow.cn/docs/release-notes/overview#pricing-adjustment-vendor-aqwen2-72b-model-will-start-charging)

To provide more stable, high-quality, and sustainable services, the Vendor-A/Qwen/Qwen2-72B-Instruct model, which was previously offered for free, will start charging from October 17, 2024. The pricing details are as follows:

- Limited-time discount price：¥ 1.00 / M tokens
- Original price：¥ 4.13 / M tokens（the original price will be restored at a later date）

Third-Party Information Sharing List and Third-Party SDK Directory

Update Date: June 25, 2026

### On this page

[Model Service Adjustment] ERNIE-Image-Turbo to Be Discontinued

[API Service Adjustment] Chat Models Will Ignore the repetition_penalty Parameter

[API Service Adjustment] Image Generation API: batch_size Removal and Default Watermark

[Model Service Adjustment] Nex-N2-Pro, Qwen3.5-397B-A17B, MiniMax-M2.5, and Other Models to Be Discontinued

[Pricing Adjustment] Time-Based Pricing for DeepSeek-V4-Flash

[API Service Adjustment] /user/info Endpoint Deprecation

[Pricing Adjustment] Cache Hit Input Token Price Adjustment for DeepSeek-V4-Pro

[Pricing Adjustment] Pricing Adjusted for Nex-N2-Pro, DeepSeek-V4-Pro, DeepSeek-V3.2, and Qwen3.6 Models

[Model Service Adjustment] GLM-4.7, Kimi-K2.5, and Other Models to Be Discontinued

[Model Service Adjustment] Kimi-K2, GLM-4.6, and Other Models to Be Discontinued

[Account Security] Unverified Accounts Will Be Restricted from Platform Functions Starting May 15, 2026

[Model Service Adjustment] KAT-Dev, PaddleOCR-VL, and Other Models to Be Discontinued

[Model Service Adjustment] Qwen3-Coder, ERNIE-4.5, and Other Models to Be Discontinued

[Model Service Adjustment] MiniMax-M2.1, Qwen2, and Other Models to Be Discontinued

[Pricing Adjustment] Pricing Adjusted for Qwen3.5-397B-A17B Model

[Model Service Adjustment] MiniMax-M2, Kimi-Dev-72B, and Other Models to Be Discontinued

[Model Service Adjustment] GLM-4.5, Qwen3-235B, and Other Models to Be Discontinued

[Service Adjustment] Platform Credit Balance Display Format Updated

[Model Upgrade] DeepSeek-V3.2-Exp Upgraded to V3.2

[Model Service Adjustment] Ling-1T, Ring-1T, and Other Models to Be Discontinued

[Service Adjustment] Rate Limits Adjusted for DeepSeek-R1/V3 and Other Models

[Service Adjustment] Usage Tier Purchase Entry Closed

[Model Service Adjustment] DeepSeek-V3.1 Models to Be Discontinued

[Model Update] Kimi-K2-Instruct Upgraded to 0905 Version

[Model Service Adjustment] HunyuanVideo-HD and Other Video Models to Be Discontinued

[Model Service Adjustment] DeepSeek-R1-0120 and Other Models to Be Discontinued

[Platform Maintenance] Scheduled Maintenance on June 10, 2025

[Model Update] DeepSeek-R1 Upgraded to 0528 Version

[Model Service Adjustment] Qwen2-1.5B and Other Models to Be Discontinued

[Model Service Adjustment] HunyuanVideo (non-HD) Model to Be Discontinued

[Model Update] DeepSeek-V3 Upgraded to 0324 Version

[Model Update] DeepSeek-V3 to Be Upgraded to 0324 Version

[Service Adjustment] api.siliconflow.com Endpoint to Be Phased Out

[Service Adjustment] RPH and RPD Limits Removed for DeepSeek-R1/V3

[Model Service Adjustment] Marco-o1, FLUX.1, and Other Models to Be Discontinued

[Service Adjustment] New RPH/RPD Rate Limits for DeepSeek-R1/V3

[Model Service Adjustment] Yi-1.5, SD-3-medium, and Other Models to Be Discontinued

[Pricing Adjustment] DeepSeek-V3 Prices Restored to Original Rates

[Feature Update] Reasoning Model reasoning_content Field Separated

[New Model Launch] DeepSeek-R1 and DeepSeek-V3 Now Available

[Service Adjustment] Image and Video URL Validity Period Adjusted to 1 Hour

[Pricing Adjustment] LTX-Video Model Will Start Charging

[Model Service Adjustment] DeepSeek-V2-Chat and Other Models to Be Discontinued

[Model Service Adjustment] Qwen2.5-Math, Hunyuan-A52B, and Other Models to Be Discontinued

1. Model offline notice

[Model Service Adjustment] Multiple Models to Be Discontinued and Related Service Updates

1. Model offline notice

[Pricing Adjustment] Vendor-A/Qwen2-72B Model Will Start Charging
