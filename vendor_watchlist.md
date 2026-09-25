# Vendor Watchlist · 待考察厂商池

> ⚠️ **本文件不是免费额度情报**：这里列的是「听说过但尚未在官方页复核」的厂商线索，**不构成任何免费额度的证据**。
> 来源以第三方汇总仓库（[FreeLLM-API-KeyHub](https://github.com/guihuashaoxiang/FreeLLM-API-KeyHub) 的 `LLM_API_Providers_All.md`）为主，加上巡检中遇到的入口。
> 晋升到 `llm-intel.yaml` 的条件见文末。

---

## 复核状态说明

| 标记 | 含义 |
|---|---|
| ❌ 已排除 | 官方页复核过，无免费层 / 站点已失效 / 路径 404 |
| ⚠️ 待复核 | 页面存在但为前端渲染，静态巡检取不到正文，需浏览器抓取 |
| ❓ 未考察 | 只从第三方清单见过，本轮未访问官方页 |
| ✅ 已收录 | 已进 `llm-intel.yaml` 与 `provider_profiles.py` |

---

## 一、本轮已复核（结论如实记录）

| 厂商 | 线索 | 复核结论 |
|---|---|---|
| **InceptionLabs** | 「1000 万 tokens 免费计划」 | ✅ **已收录** — 官方文档 `docs.inceptionlabs.ai/get-started` 原文：新账号 **1 亿 free tokens**、**no payment details required**。第三方少记一个数量级。**免费额度藏在文档站**，根站 `/pricing` 是 404 |
| **Inference.net** | 「$1/月重置额度」 | ✅ **已收录** — 官方 `inference.net/pricing/` 有 **$0 免费档**：100 万 Gateway 请求、30 req/min、1 seat；ToS 明确免费档不需信用卡。传闻的「$1/月」无依据，$50 开户赠金属 $250/月的 Growth 档。**额度列表在 `/pricing/`（带尾斜杠），根路径不列** |
| **Anyscale** | $100 注册额度 | ✅ **已收录** — `pricing` 页原文 "Get started with $100 credit" 复核通过；需工作邮箱；**2026-07-30 公告已签被 Nscale 收购的最终协议**，稳定性待观察 |
| **DigitalOcean Inference Engine** | 「$200 / 60 天」 | ⚠️ **已收录但降级** — 官方文档实际为 **$5 / 90 天**通用云试用金且**必须绑卡**，**不属于 LLM 免费层**；产品已从 GenAI Inference 改名 Inference Engine |
| 01.AI 零一万物 | 注册送体验金，约 1 个月 | ⚠️ **待核实** — CDP 读到官方首页 2026-08-03 关停公告、API 2026-09-03 停止；但静态复核与 Web 搜索均无法确认（站点为 SPA）。已收录但标注为待核实 |
| 昆仑万维 天工 | 新人体验额度 | ❌ **已排除** — `model-platform.tiangong.cn` 302 跳至消费端主站，`api.tiangong.cn` 返回 503。已收录仅作跟踪 |
| NCompass | $100 免费额度 | ❌ **已排除** — 业务已转型为 "GPU performance engineering for opencode"，不再是 LLM 推理平台 |
| Mara | $5 / 30 天 | ❌ **疑似虚构条目** — `www.mara.com` 是比特币矿企 MARA Holdings；`mara.ai` 是 GoDaddy 停放域名（标价 $142 万）；`getmara.ai` 是 HR 招聘 ATS；Wayback 从未归档 LLM 内容。保留作反例留痕 |
| SambaNova Cloud | 「$5 免费额度 + 永久免费层」 | ❌ **已排除** — `cloud.sambanova.ai/pricing` 只列付费单价，无免费层与 $5 赠金记载 |
| 阶步星辰 StepFun | 「繁星计划」 | ⚠️ **待复核** — `platform.stepfun.com` 仅见 Startup / Builder Program；定价文档为前端渲染取不到正文（页面自述「Step Plan 上线 · Credit 月池」，疑似有额度但无法静态确认） |
| **小米 MiMo** | 线索入口 `platform.xiaomimimo.com` | ✅ **已收录** — 官方定价页（更新 2026-09-22）原文：**TTS 系列 `mimo-v2.5-tts` / `-voiceclone` / `-voicedesign` 限时免费**、缓存写入限时免费；语言模型（`mimo-v2.6-pro` ¥0.025/¥3/¥6 每百万 tokens 等）与 ASR **按量计费、无免费层**。新用户注册赠金 **40 天有效**（官方促销 FAQ 原文：bonus credit 可经注册或 Refer & Earn 获得），仅抵按量计费 API、不可抵 Token Plan。⚠️ 控制台前端 bundle 仍留「限时免费中，充值功能暂未开放」旧文案，与官方功能日志「2026-01-26 计费功能已上线」冲突 —— 按定价页与 Token Plan 售卖页判定为**已计费** |

---

## 二、国内原始模型厂商（❓ 未考察）

| 厂商 | 第三方清单给出的平台入口 |
|---|---|
| 华为云 盘古 | `huaweicloud.com/product/pangu.html` |
| 百川智能 | `platform.baichuan-ai.com` |
| 阶步星辰 StepFun | `platform.stepfun.com` |
| 面壁智能 MiniCPM | `modelbest.cn` |
| 出门问问 | `openapi.mobvoi.com` |
| 京东 言犀 | `console.jdcloud.com` |
| vivo 蓝心 BlueLM | `dev.vivo.com.cn` |
| OPPO 安第斯 AndesGPT | `open.oppomobile.com` |
| 第四范式 式说 | `4paradigm.com` |
| 紫东太初（中科院自动化所） | `taichu-web.ia.ac.cn` |
| 浪潮信息 源 Yuan | `yuan.inspur.com` |
| 达观数据 曹植 | `datagrand.com` |
| 云从科技 从容 | `cloudwalk.com` |
| 快手 可图 / 意间 | `klingai.kuaishou.com` |
| 知乎 知海图 AI | `zhihai.zhihu.com` |
| 猎户星空 | `ainirobot.com` |

## 三、国内聚合 / 算力平台（❓ 未考察）

| 厂商 | 第三方清单给出的平台入口 |
|---|---|
| 白山云 AI | `ai.baishan.com` |
| AiHubMix | `aihubmix.com` |
| 中国联通 元景 | `maas.ai-yuanjing.com` |
| 非线智能 NoneLinear | `nonelinear.com` |
| 网易有道 ThinkFlow | `ai.youdao.com` |

## 四、海外原始模型厂商（❓ 未考察）

| 厂商 | 第三方清单给出的平台入口 |
|---|---|
| Upstage Solar | `console.upstage.ai` |
| Reka AI | `api.reka.ai` |
| Perplexity Sonar | `docs.perplexity.ai` |
| Writer AI Palmyra | `dev.writer.com` |
| Aleph Alpha | `aleph-alpha.com` |
| Inflection AI | `inflection.ai` |
| Databricks Mosaic AI | `databricks.com` |
| Clarifai | `clarifai.com` |
| Black Forest Labs (FLUX) | `bfl.ai` |
| Liquid AI | `liquid.ai` |
| Salesforce Einstein | `developer.salesforce.com` |
| Snowflake Cortex | `snowflake.com` |

## 五、海外云 / 聚合平台（❓ 未考察）

| 厂商 | 第三方清单给出的平台入口 |
|---|---|
| Replicate | `replicate.com` |
| Lepton AI（现 NVIDIA DGX Cloud Lepton） | `lepton.ai` |
| Novita AI | `novita.ai` |
| Lambda Labs | `lambda.ai` |
| OVHcloud AI Endpoints | `endpoints.ai.cloud.ovh.net` |
| RunPod | `runpod.io` |
| Hyperbolic | `hyperbolic.xyz` |
| kluster.ai | `kluster.ai` |
| ShareAI | `shareai.now` |
| AkashML | `akash.network` |
| AtlasCloud | `atlascloud.ai` |
| Avian | `avian.io` |
| Chutes | `chutes.ai` |
| Cirrascale | `cirrascale.com` |
| Crusoe | `crusoe.ai` |
| DekaLLM | `cloudeka.id` |
| Featherless | `featherless.ai` |
| FriendliAI | `friendli.ai` |
| GMICloud | `gmicloud.ai` |
| Inceptron | `inceptron.io` |
| Infermatic | `infermatic.ai` |
| Ionstream | `ionstream.ai` |
| ModelRun | `modelrun.org` |
| Parasail | `parasail.io` |
| Perceptron | `perceptron.inc` |
| Phala Network | `phala.network` |
| Sourceful | `sourceful.com` |
| Venice | `venice.ai` |
| Weights & Biases | `wandb.ai` |
| Z.AI | `chat.z.ai` |
| OctoAI | `octoai.cloud` |

---

## 六、晋升条件

一条线索要进 `llm-intel.yaml`，需要同时满足：

1. **官方一手 URL 可访问**（厂商自家域名，`curl` 能拿到 200；前端渲染也算，但要能被巡检的浏览器兜底抓到正文）；
2. **免费额度数字能在官方页原文中找到**（不是第三方转述、不是控制台登录后可见的浮层）；
3. **写成带出处的字段**（`free_quota` / `validity` / `preconditions`），而不是笼统的"有免费额度"；
4. 查不到就如实写"未见公示 / 不予采信"——**本仓库宁可少一条情报，也不要一条假的**。

参考：本轮复核里，第三方清单的 8 家「免费额度平台」有 **3 家**（InceptionLabs、Inference.net、Anyscale）经官方页确认真有免费额度，但**8 个数字里 6 个是错的**（InceptionLabs 少记一个数量级、DigitalOcean 从 $5 记成 $200、其余 4 个数字无官方页支撑）。第三方汇总仓库适合作**线索池**，不适合作**数据源**。

**一个踩过的坑**：只查厂商官网首页会漏判。InceptionLabs 的免费额度写在 `docs.` 子域，`inference.net` 的额度列表在带尾斜杠的 `/pricing/`，DigitalOcean 的 signup credit 在 `docs.digitalocean.com`。判定「无免费层」之前，至少要试过 `docs.` 子域、带/不带尾斜杠的 pricing 路径、以及文档站的 `llms.txt` 索引。

---

*本文件为人工维护的线索清单，不参与巡检脚本的抓取。*
