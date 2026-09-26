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
| ❓ 未考察 | 只从第三方清单见过，尚未访问官方页 |
| ✅ 已收录 | 已进 `llm-intel.yaml` 与 `provider_profiles.py` |

---

## 一、已复核（结论如实记录）

| 厂商 | 线索 | 复核结论 |
|---|---|---|
| **Qoder（国际版）** | 用户点名收录 | ✅ **已收录（Part 4 工具类）** — `docs.qoder.com/account/pricing` 原文：Free 方案基础模型（消息数受限）、新用户 2 周 Pro 试用 300 Credits、用尽自动降级不断供；`events/100credits` 原文：2026-09-18 起个人用户（免费+付费）桌面端每日**手动领** 100 Credits、不结转。证据走 Mintlify `.md` 端点，静态可抓 |
| **腾讯云 CodeBuddy / WorkBuddy** | 用户点名收录 | ✅ **已收录（Part 4 工具类）** — `codebuddy.cn/pricing`（浏览器渲染）：体验版 ¥0，每月 500 积分 + Auto 全模型限免 + 补全限免无限次；`tencentcloud.com/techpedia/144275`：国际版新用户赠试用积分（两周）、免费用户每日基础积分重置。⚠️ 定价页 SPA，静态抓取只拿到壳页，靠巡检浏览器兜底 |
| **InceptionLabs** | 「1000 万 tokens 免费计划」 | ✅ **已收录** — 官方文档 `docs.inceptionlabs.ai/get-started` 原文：新账号 **1 亿 free tokens**、**no payment details required**。第三方少记一个数量级。**免费额度藏在文档站**，根站 `/pricing` 是 404 |
| **Inference.net** | 「$1/月重置额度」 | ✅ **已收录** — 官方 `inference.net/pricing/` 有 **$0 免费档**：100 万 Gateway 请求、30 req/min、1 seat；ToS 明确免费档不需信用卡。传闻的「$1/月」无依据，$50 开户赠金属 $250/月的 Growth 档。**额度列表在 `/pricing/`（带尾斜杠），根路径不列** |
| **Anyscale** | $100 注册额度 | ✅ **已收录** — `pricing` 页原文 "Get started with $100 credit" 复核通过；需工作邮箱；**2026-07-30 公告已签被 Nscale 收购的最终协议**，稳定性待观察 |
| **DigitalOcean Inference Engine** | 「$200 / 60 天」 | ⚠️ **已收录但降级** — 官方文档实际为 **$5 / 90 天**通用云试用金且**必须绑卡**，**不属于 LLM 免费层**；产品已从 GenAI Inference 改名 Inference Engine |
| 01.AI 零一万物 | 注册送体验金，约 1 个月 | ⚠️ **待核实** — CDP 读到官方首页 2026-08-03 关停公告、API 2026-09-03 停止；但静态复核与 Web 搜索均无法确认（站点为 SPA）。已收录但标注为待核实 |
| 昆仑万维 天工 | 新人体验额度 | ❌ **已排除** — `model-platform.tiangong.cn` 302 跳至消费端主站，`api.tiangong.cn` 返回 503。已收录仅作跟踪 |
| NCompass | $100 免费额度 | ❌ **已排除** — 业务已转型为 "GPU performance engineering for opencode"，不再是 LLM 推理平台 |
| Mara | $5 / 30 天 | ❌ **疑似虚构条目** — `www.mara.com` 是比特币矿企 MARA Holdings；`mara.ai` 是 GoDaddy 停放域名（标价 $142 万）；`getmara.ai` 是 HR 招聘 ATS；Wayback 从未归档 LLM 内容。保留作反例留痕 |
| SambaNova Cloud | 「$5 免费额度 + 永久免费层」 | ❌ **已排除** — `cloud.sambanova.ai/pricing` 只列付费单价，无免费层与 $5 赠金记载 |
| 阶步星辰 StepFun | 「繁星计划」 | ⚠️ **待复核** — `platform.stepfun.com` 仅见 Startup / Builder Program；2026-09-26 用真实浏览器（Playwright）渲染 `docs/pricing/details` 与 `docs/quickstart/*` 仍返回 **404**（文档路径已变更），首页正文无任何免费/赠金额度字样。「Step Plan · Credit 月池」疑有额度但**官方页取不到实证**，按「宁缺毋滥」不予收录，留待路径明确后复查 |
| Black Forest Labs (FLUX) | FLUX.2 图像模型热度 | ❌ **已排除（无免费层）** — `bfl.ai/pricing` 与 `docs.bfl.ai/` 复核：纯按量计费，FLUX 每 megapixel 收 $0.015–0.07，"1 credit = $0.01 USD"，无新用户赠金 / free tier 记载。模型虽热，但不符合本站「白嫖」判据 |
| Perplexity (Sonar) | 「$0 起」线索 | ❌ **已排除（无免费层）** — `docs.perplexity.ai/getting-started/pricing` 复核：按次/按 token 计费（web_search $5/1k、Search API 按档位），页内 "$0.0025" 等为**单次调用单价**非免费层，未见注册赠金或永久免费档 |
| **AI 编程工具扩充（7 家）** | 用户追问「其他的呢」 | ✅ **已收录（Part 4 工具类，2026-09-26）** — 均经 requests 直读官方定价页逐字取证：Trae 中国版（`trae.cn/pricing` 免费版每月 500 积分、所有功能均可免费使用）、通义灵码/Qoder CN（`help.aliyun.com` 计费说明：个人体验版免费含 2 周试用 + 300 Credits）、文心快码（`cloud.baidu.com` 定价文档：个人标准版补全免费 + 首次赠 ¥10 请求券）、GitHub Copilot（pricing FAQ 原文 2000 completions + 50 chat/月）、Cursor（Hobby "Limited Agent requests"，官方不公布数字、照原文收录）、Kiro（"perpetual Kiro Free tier … 50 credits"）、Zed（"$0 forever … 2,000 accepted edit predictions"）。⚠️ vendor id 用 `cursor_ide`：`cursor` 与浏览页 CSS 属性撞词，会被「浏览页不硬编码厂商 id」守卫拦下。⚠️ 2026-09-26 CI 首巡：**trae.cn 对机房 IP 一律 403、codebuddy.ai 访问超时**，两家的巡检源都改挂可达页面（trae 走国际版、codebuddy 保留国内站），证据以档案 links + 国内复核为准。原句：⚠️ 2026-09-26 CI 首巡：**trae.cn 对机房 IP 一律 403**（本地国内网络 200），巡检源已改挂国际版 `trae.ai/pricing`（SPA、浏览器兜底可巡）；中国版证据保留、页面级复核需国内网络。⚠️ 国际版当日实测：可见定价卡从 Lite $3 起、**无 Free 卡**，但页面描述仍写 "Get started for Free"、内嵌数据带 Free 方案配额（advanced 1,000/月、补全 5,000、premium 快 10 + 慢 50）——两处矛盾，按可见口径**暂不采信国际版有免费层**，待复查 |
| Windsurf / Codeium | AI IDE 免费层线索 | ❌ **已排除（品牌归属不明）** — `windsurf.com/pricing` 308 永久重定向至 `devin.ai/pricing`，页面标题 "Plans and Pricing \| Devin"、全页 0 次出现 "Windsurf"；Free 卡（unlimited tab completions 等）无法在官方页确证归属，待品牌澄清后复查 |
| Augment Code | AI IDE 免费层线索 | ❌ **已排除（无免费层）** — `augmentcode.com/pricing` 全页无 "free" 字样，仅 Standard/Business/Enterprise；"Standard includes $20 of usage every month" 是**付费随附额度**非免费层 |
| 讯飞 iFlyCode / 星火飞码 | 编程助手免费线索 | ❌ **已排除（站点失联）** — `iflycode.xfyun.cn` DNS 无法解析，`code.iflytek.com` 与搜索仅命中第三方导航站，无任何可复核官方页；疑似产品下线或并入讯飞星火主站 |
| iFlow CLI | 曾经的「免费用 Kimi/Qwen/DeepSeek」 | ❌ **已停服** — `cli.iflow.cn` 首页横幅原文：「iFlow CLI 将于 2026 年 4 月 17 日（北京时间）正式停止服务，请大家迁移至 Qoder」。仅作历史注记；其用户被导流至已收录的 Qoder |
| 华为云码道（CodeArts 代码智能体） | 个人体验版免费线索 | ⚠️ **待复核** — `support.huaweicloud.com` 计费公告确认存在「个人体验版（套餐积分 + 每日签到积分）」，但**免费积分数值未在该页公示**（需登录控制台），按「额度数字必须官方页可引」暂不收录；2026-09-04 起刚切积分制，政策未稳 |
| **小米 MiMo** | 线索入口 `platform.xiaomimimo.com` | ✅ **已收录** — 官方定价页（更新 2026-09-22）原文：**TTS 系列 `mimo-v2.5-tts` / `-voiceclone` / `-voicedesign` 限时免费**、缓存写入限时免费；语言模型（`mimo-v2.6-pro` ¥0.025/¥3/¥6 每百万 tokens 等）与 ASR **按量计费、无免费层**。新用户注册赠金 **40 天有效**（官方促销 FAQ 原文：bonus credit 可经注册或 Refer & Earn 获得），仅抵按量计费 API、不可抵 Token Plan。⚠️ 控制台前端 bundle 仍留「限时免费中，充值功能暂未开放」旧文案，与官方功能日志「2026-01-26 计费功能已上线」冲突 —— 按定价页与 Token Plan 售卖页判定为**已计费** |

---

## 二、国内原始模型厂商（❓ 未考察）

| 厂商 | 第三方清单给出的平台入口 |
|---|---|
| 华为云 盘古 | `huaweicloud.com/product/pangu.html` |
| 百川智能 | `platform.baichuan-ai.com` |
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
| Writer AI Palmyra | `dev.writer.com` |
| Aleph Alpha | `aleph-alpha.com` |
| Inflection AI | `inflection.ai` |
| Databricks Mosaic AI | `databricks.com` |
| Clarifai | `clarifai.com` |
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

参考：2026-09 首批复核里，第三方清单的 8 家「免费额度平台」有 **3 家**（InceptionLabs、Inference.net、Anyscale）经官方页确认真有免费额度，但**8 个数字里 6 个是错的**（InceptionLabs 少记一个数量级、DigitalOcean 从 $5 记成 $200、其余 4 个数字无官方页支撑）。第三方汇总仓库适合作**线索池**，不适合作**数据源**。

**一个踩过的坑**：只查厂商官网首页会漏判。InceptionLabs 的免费额度写在 `docs.` 子域，`inference.net` 的额度列表在带尾斜杠的 `/pricing/`，DigitalOcean 的 signup credit 在 `docs.digitalocean.com`。判定「无免费层」之前，至少要试过 `docs.` 子域、带/不带尾斜杠的 pricing 路径、以及文档站的 `llms.txt` 索引。

---

*本文件为人工维护的线索清单，不参与巡检脚本的抓取。*
