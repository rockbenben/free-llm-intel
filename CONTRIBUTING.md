# 贡献指南

感谢关注本仓库。所有变更都围绕一个原则：**只收录官方页面能核实的信息**。第三方博客的数字、无法复核的"历史额度"不要写进档案，宁可留空并在 `notes` 注明"无法复核，不予采信"。

## 提交 Issue

- 额度变化 / 模型下架 / 活动到期：请附上**官方链接**（定价页、文档、公告），有截图更好。
- 抓取异常：附上运行命令与终端输出（注意脱敏，不要贴 API Key）。

## 新增 / 修改一个厂商

### 0. 先过背景关：排除「中小型中转站」

收录对象是模型厂商官方平台、有真实主体与自有/租用推理算力设施（GPU、RDU 等专用加速器）的推理平台（含官方合作聚合），以及不转售模型 API 的工具平台。以下不收：

- 无自研模型、无自有/租用推理算力设施，转售上游模型 API（尤其 Claude / GPT / Gemini 等闭源模型）；
- 典型信号：匿名主体或新注册账号、远低于官方的价格、空投 / 签到 / 轮盘等羊毛机制、白标分销（reseller storefront）。

推广渠道不作判据——同一信息源也可能介绍正规平台，判的是主体与业务模式。按此判据已拒绝的例子：APInex（PR #4）、DMXAPI、数眼智能（数言 AI）。正规聚合平台（如 OpenRouter、硅基流动）有公司主体与自有设施，不属此列。

**收录资格与免费攻略推荐分开判断**：符合主体与业务模式要求的平台可以收录，但只有官方可核实的免费权益才进入攻略。计划名称为 Free、页面脚本中的赠金配置或未渲染的模板文案，都不能单独证明实际免费权益；无法核实的金额、有效期与免卡条件不予采信。

改动涉及**两个输入文件**，爬虫本身通常不用动：

### 1. `llm-intel.yaml`

- 在 `vendors:` 下加一条：`id`（snake_case，全站唯一）、`brand`、`products`、`homepage`；
- 在 `sources:` 下加待巡检页面，每条为 `{vendor_id, type, url}`。常用 `type`：
  `pricing`（定价页）、`free_quota` / `free_tier`（免费额度说明）、`billing` / `billing_docs`（计费文档）、
  `rate_limits`（限速）、`activities`（活动页）、`api_docs`（API 文档）、
  `referral`（邀请返利 / 拉新活动页）、`student_program`（学生 / 高校扶持计划页）、
  `blog` / `news` / `changelog` / `feed`（博客动态；`feed` 仅用于真正的 RSS/Atom XML，**不要填 sitemap.xml**）。
- **判定「无免费层」之前**，至少试过这三个位置再下结论：`docs.` 子域、带与不带尾部斜杠的 pricing 路径、文档站的 `llms.txt` 索引。免费额度经常只写在文档站里，根站首页与 `/pricing` 可能都是 404。

### 2. `provider_profiles.py`

在 `PROVIDER_PROFILES` 中以同一 `id` 为键加档案：

| 字段 | 内容 |
|---|---|
| `category` | `domestic` / `international` / `cloud` |
| `display_name` | README 中展示的厂商名 |
| `free_models` | **列表**，每个元素是一条 bullet：模型名 + **内联的免费额度 / 限速**（模型与额度不要分开写）；无免费层时写"**无免费模型层**"并说明在架付费模型 |
| `free_quota` | 仅写**账户级注册赠送**（代金券、token 资源包）；模型层免费额度写进 `free_models`，不要重复 |
| `validity` | 额度有效期；滚动重置 / N 天 / 永久免费等 |
| `tier_caveats` | **列表**，免费层的真实边界：①只免旧版/特定模型时写清版本代差（哪一代收费）；②限速数值（RPM/RPD/TPM，文档无公开数字就明说"以控制台为准"）；③商用限制、数据隐私；④公测/限时等失效风险。**禁止"全家桶永久免费"式笼统表述**；只要归在无条件免费层（tiers 含 permanent/recurring/onetime 且免卡，即 `signup` 非 card），该字段必填（`TestTierCaveats` 强制） |
| `preconditions` | 手机号、实名、信用卡、企业认证等门槛。注意：实名/邮箱不算门槛，只有「需要付款方式」才单列 |
| `promotions` | 限时折扣、订阅档位等活动，标注截止日与来源 |
| `invite_reward` | （可选）邀请返利 / 拉新奖励。只填官方页可核实的规则；无官方页就写明死链并写"不予采信"。**不填则不出这一行** |
| `student_benefit` | （可选）学生 / 高校师生扶持。同上，无官方页即写明"不予采信"。**不填则不出这一行** |
| `openai_compat` | （可选）字典，有则自动进「一键接入」速查表。键：`summary`（额度简述）、`api_key_label`、`api_key_url`、`base_url`、`models`（推荐填的 model id）。缺 `base_url` 不出表；填了字典就必须写全 `base_url`/`api_key_url`/`models`，缺任一会被测试拦下（`TestEndpointTable`） |
| `notes` | 已作废的旧说法、品牌变迁等；查不到的旧额度写"无法复核，不予采信" |
| `links` | 元组列表 `(标签, URL)`，至少一条官方定价 / 免费额度页 |

### 3. 本地验证后提交

```bash
# 1. 只跑新增厂商，快速验证抓取与解析（调试模式，不覆盖全局文档）
python crawler_llm_intel.py --only <vendor_id> --no-browser

# 2. 确认抓取无误后，执行全量巡检生成完整 README 与博客总表（建议加 --no-news 快速生成）
python crawler_llm_intel.py --no-browser --no-news

# 3. 运行本地自动化测试套件（全部用例；TestCrawlerCleanup 已改在临时目录里跑，
#    不会碰仓库根的 .ai-changed）
python -m unittest discover

# 4. 确认 README 表格与相应归档文件正常后再提交
git diff README.md
```

- **本地复现 CI** 用 `python -m unittest -v test_workflow_and_review.ci_suite`。它从仓库根按
  `unittest discover` 发现测试，再排除 `CI_EXCLUDED_CLASSES`（当前为空）。安装 Node.js
  后，这条命令也会运行 `docs/app.test.mjs` 的浏览页测试。
- 面向 `main` 的 PR 和常规推送由 [CI](.github/workflows/ci.yml) 以只读权限校验提交中的产物。
  [每日巡检](.github/workflows/refresh-intel.yml) 在同一个工作目录内依次更新归档、正文和视图，
  运行同一套测试后一次提交。若推送因 `main` 在巡检期间前进而被拒绝，请在 Actions 的
  **Run workflow** 选择最新 `main` 发起新一轮。
- **新用例不要依赖真实仓库根**：要读写仓库文件时，把落点做成可注入（照 `_repo_root()` 的样子），
  测试里 patch 到临时目录 —— 否则这个用例只能被排除在 CI 之外，等于 CI 里零覆盖。
- **新增产物或新增守卫时，顺手确认它在 CI 里真的会跑**（`ci_suite()` 取到即可）——
  「测试写了但 CI 不跑」和「没写测试」在故障面前是一回事。
- **失败源冷却**：单个情报源连续抓取失败达 `SOURCE_SKIP_FAILS` 次后进入 `SOURCE_RETRY_DAYS` 天的跳过窗口（日志 `[source-skip]`，计数存在 `llm-intel-state.json` 的 `failures`），到期自动放行重试一次、成功即清零；确要强制抓取用 `--force-sources`。别把它和上面 AI 核查的 `[ai-cooldown]` 混淆：前者管抓取失败，后者管核查失败。

- **不要手工编辑 README 的两个自动生成区块**：`LLM-GUIDE:BEGIN/END`（项目介绍后的白嫖攻略）与 `LLM-INTEL:BEGIN/END`（「快速开始」之后的厂商总表），也不要手工编辑 `llm-news-feeds.md` / `llm-news-feeds.opml` / `llm-news/` / `docs/feeds/` 的生成内容——它们在完整运行时会被自动重新渲染。`llm-intel-changelog.md`（AI 采纳变更日志）同样只由脚本追加、CI 随巡检提交，不要手改；首次 AI 采纳之前它不存在是常态。标记块之外（含文末的开发者章节与 365 页脚）人工维护，巡检会**原样保留**（旧版「END 之后一律丢弃」的行为已移除）。
- `llm-news-feeds.opml` 的自建源分组需要可用的订阅前缀。本地渲染同样会读取 `docs/CNAME`。厂商官网自带 RSS 的判断（`_native_feed_vendors`）由 OPML 与 `llm-news-feeds.md` 共用。
- `docs/feeds/*.xml` 与 `docs/feeds/vendors.json`、`docs/feeds/articles.json`、`docs/feeds/model-releases.json`、`docs/feeds/quotas.json`、`docs/feeds/intel-changes.json` 是自建 RSS 订阅源、厂商索引、**全量文章索引**、模型发布雷达（从归档标题抽取「日期+厂商+模型」事件）、「免费额度与活动一览」的机读镜像与变化流伴生 JSON（GitHub Pages 从这里发布），**只由脚本生成**。注意 `--no-news` 会跳过整条新闻链路（发布雷达也在内），因此也不会刷新它们；改动了归档相关的抓取 / 排序 / 清洗逻辑时，请跑一次**不带 `--no-news`** 的巡检确认产物。新增厂商后订阅源会自动多一个 `llm-news-<vendor_id>.xml`、各机读索引随之同步增减，已下线厂商的旧源会被清理。
- `docs/index.html` 是自建 RSS 的**浏览页**（读 `docs/feeds/articles.json` 列出**全部**条目，可筛选、可搜索；选中某厂商时订阅地址自动切成该家单源），**人工维护、不参与巡检**，改它不会与脚本产物冲突。页面里的厂商清单来自 `feeds/vendors.json`，**不要在页面里硬编码厂商列表**（会随厂商增删而漂移）；`docs/.nojekyll` 关闭 Jekyll，不要删除。
- **合并流默认不限制**（`RSS_MERGED_LIMIT = 0`，收录全部有日期的条目）。曾经限 200 条，理由是「全量约 1.2 MB 会让阅读器吃力」—— **那个理由站不住**：GitHub Pages 用 gzip 传输，当初决策时线上实测过 `Content-Encoding: gzip`，那份全量 XML 压缩后只剩约八分之一（历史观测值，不代表现状体积）。当时的判断看的是未压缩体积，别再照它把上限加回来。要限流可用 `--rss-limit N`。
- **页面为什么还读 `articles.json` 而不是合并流**：体积明显更小（不带描述）、免去 XML 解析，而且**标题不截断、还带原文标题**（feed 里截到 60 字是为了列表可读）。别顺手把页面「简化」成读合并流。
- `.translate_cache.json` 是本地缓存，不要提交。
- commit message 只描述变更内容本身。

## AI 自动核查是怎么工作的

1. 每次巡检把各官方页正文做哈希快照（`llm-intel-state.json`），与上次比对；快照条目除 `sha256` 外还存一份 `fact`（经 `FACT_TEXT_LIMIT` 截断的事实行），页面变化时新旧 fact 相减得到「变化行」，供 diff 导向核查把注意力聚焦到实际改动上；
2. 快照变化的厂商进入 LLM 核查队列（`ai_review.py`），输入 = 该厂商全部情报页正文 + 当前生效档案；此外默认还有 `--stale-review-days` 例行复查：超期未被核查的厂商即使页面未变也入队（每轮至多 `STALE_REVIEW_PER_RUN` 家，分批轮完存量），设 `0` 关闭；
3. LLM 只输出严格 JSON：变化字段、攻略元数据、以及**页面原文逐字证据**。证据不能在页面正文中逐字定位的补丁会被整条拒绝（防幻觉）；
4. 通过校验的补丁写入 `profile_overrides.json`（AI 永远不直接改 `provider_profiles.py`），在 CI 中**与快照 / 新闻一起原子提交到 main**（2026-09-22 起不再开 PR 等人工审核，理由见下）；LLM 调用失败或未配置 API Key 时保留旧快照，下次巡检自动重试。

默认后端是 **Google AI Studio 的 Gemini API**（`generativelanguage.googleapis.com`，免费层 Key 在 [aistudio.google.com/apikey](https://aistudio.google.com/apikey) 申请）：

- 环境变量 `GEMINI_API_KEY`（兼容 `GOOGLE_API_KEY`），默认模型 `gemini-3.8-flash`，可用 `AI_REVIEW_MODEL` 覆盖；
- `AI_REVIEW_BACKEND=auto|opencode-go|gemini|anthropic` 控制后端；`auto`（默认）优先用有效 Go 配置，否则沿用 Gemini → Anthropic 的 Key 选择顺序；
- CI 配置指南：
  1. 在 **Settings → Secrets and variables → Actions** 配置 `GEMINI_API_KEY` Secret；
  2. 在 **Settings → Actions → General → Workflow permissions** 选择 **Read and write permissions**（**不再需要**勾选 Allow GitHub Actions to create and approve pull requests —— 2026-09-22 起巡检不再开 PR）；
  3. 若 `main` 分支开启了 Branch Protection，需将 `github-actions[bot]` 加为允许直推或 bypass 的用户；
  4. 未配置 Key 时新闻更新仍直接原子性提交 main，事实变化保留旧快照等待重试。

- 自建 RSS 的订阅前缀由 `default_feeds_base()` 先读 `docs/CNAME`，缺省时再按
  `GITHUB_REPOSITORY` 推导 Pages 地址。需要覆盖这两项时，在 Actions 仓库变量中设置
  `FEEDS_BASE`（形如 `https://<你的域名>/feeds`），下一次巡检和同轮渲染都会使用它。

人工基线在 `provider_profiles.py`，AI 补丁在 `profile_overrides.json`（同名字段整体覆盖，`_evidence` 累积保留最近 20 条证据）。

### OpenCode Go 临时接管 CI

在 Actions 的 Secrets 添加 `OPENCODE_GO_API_KEY`，Variables 设置：

- `OPENCODE_GO_ENABLED=true`：显式启用；留空或 false 即恢复旧流程。
- `OPENCODE_GO_UNTIL`：可选的订阅截止时刻。不设置或留空时持续优先使用 Go，订阅失效或接口不可用时自动回退旧流程；填写时必须带时区，如 `2026-12-16T18:00:00+08:00`（仅格式示例，按实际到期时间填写），格式错误或到期均跳过 Go。
- `OPENCODE_GO_MODEL`：可省略，默认 `deepseek-v4.1-flash`；`AI_REVIEW_MODEL` 仍只用于原有后端，回退 Gemini 时不会混用 Go 的模型名或 Key。
- `AI_BODIES_LIMIT`：可选的正文篇数上限，默认 0（不限）；已有译文不重译。
- `AI_BODIES_BUDGET_SECONDS`：CI **每个正文翻译步骤**的墙钟预算上限，默认 900 秒。
  每日任务从第一步起计算同一个工作截止时间，为渲染、校验和提交预留最后 180 秒。
  Go 和机翻启动时各自取「当前剩余时间」与单步上限的较小值。设 0 取消单步上限，整轮截止仍生效。
  时间不足时跳过翻译，待译篇目留在 pending。Go 的请求与退避共用步骤截止，机翻逐块按剩余时间
  限制请求超时，晚于截止的整篇译文留待重试。本地 Gemini 等后端仍在两篇之间检查预算。
  若主巡检超时，或正文抓取中断导致产物校验失败，本轮保留上次已发布结果。

Go 有效时优先完成档案核查、新标题润色和待译正文。接口**瞬时错误**（429/5xx/网络抖动）先按 `Retry-After`（缺省 5s，封顶 30s）**重试一次**，仍失败才熔断；400/401/403 这类配置错误不重试。熔断时日志带原因（HTTP 状态 / `finish_reason` / 异常类型），每次请求计入的 `usage.opencode.allowance` 也逐条打印（AI 核查段与正文步骤收尾各汇总一次），据此可区分短期限流、额度用尽与服务故障。熔断后：核查和标题立即用 Gemini 重试当前任务，后续任务沿用旧通道；正文留 pending，交给随后保留的 `--mt-bodies` 机翻步骤，**正文不回退 Gemini**。核查与正文是两个独立进程，各至多探测失败一次。语义证据校验不过仍拒绝补丁，不绕过证据闸门。

CI 正文用 `--ai-bodies --ai-bodies-go-only`，成功写入 `translator=llm`。Go 优先整篇译，
每次请求上限为 32,768 输出 token。按 1.5 个源文字符约对应 1 个输出 token 粗估，超过
49,152 字符或整篇返回 `finish_reason=length` 时，按 Markdown 段落和围栏边界分段。
分段请求每块至多 24,576 字符、每篇至多 8 块，纯代码等无需翻译的块原样保留，其余逐块
检查中文、长度、围栏内容和行内结构。整篇截断只影响该篇，切不动或任一块验收失败时整篇
留 pending。Gemini 正文仍采用 12,000 字符与 8,192 输出 token 上限，供本地可选使用。
未启用 Go 时该步骤直接退出。`--render-only` 在两种正文翻译后统一更新视图。

机翻正文（`--mt-bodies`）走 Google gtx，**代码块、行内代码、链接/图片目标、HTML 标签与裸 URL
都不进翻译接口**（占位后逐字还原）：实测 gtx 会把 URL 路径里的英文词一起翻掉
（`/engineering/managed-agents` → `/management-agents`，链接 404），2026-11-17 那批 37 篇
机翻有 10 篇因此被翻译 QC 判 HARD。占位被译文吞掉时整块回退英文原文，绝不把机器痕迹写进正文。
这一步同样吃 `AI_BODIES_BUDGET_SECONDS` 墙钟（不传时默认 900 秒）：gtx 没有额度墙，
但也不该无限跑，到点剩余留 pending 给下一轮。

接口与使用范围见 [Go 官方文档](https://opencode.ai/docs/console/go/)。请求使用项目自己的 User-Agent 和会话标识；需在 Go 控制台允许 DeepSeek 所需的 Global 区域。建议关闭 Extra Usage，避免超额转按量扣款；这里的截止开关不代替取消订阅自动续费。

本地维护仍以 agent 精译为交付标准；此配置用于 CI 增量处理，不在本地批量调用模型或机翻来替代 agent 精译。

### 免费层限流 / 模型下线的自动回退（主要使用方式）

免费层具体限额 Google 不在公开文档公布（只在 AI Studio 控制台显示，RPD 太平洋时间午夜重置，限额按项目而非 Key 计数）。`ai_review.py` 对此的保护：

1. **模型回退链**：首选模型 404 / 免费层未开放（400 模型类错误）→ 依次尝试
   `gemini-3.8-flash → gemini-3.7-flash → gemini-3.6-flash → gemini-3.5-flash
   → gemini-2.5-flash → gemini-3.5-flash-lite → gemini-3.1-flash-lite
   → gemini-2.5-flash-lite`（均经 [pricing 页](https://ai.google.dev/pricing) 核实免费层
   "Free of charge"，2026-09-15）；完整 Flash 系按新到旧排列（能力优先，严格 JSON +
   逐字证据的核查任务对能力最敏感），Lite 系垫底（更弱但免费层限额更宽松，更可能还余有
   额度），不纳入 preview 模型（官方仅约两周弃用通知，不适合长期兜底）；
   `AI_REVIEW_MODEL=<id>` 会把该模型插到链首，其余仍有回退兜底；
2. **429 短期限流**（RPM/TPM，按模型独立计量）：尊重响应头 `Retry-After`，否则按
   5 / 10 / 20 / 40 秒指数退避，最多重试 4 次；退避仍不缓解则换下一个备选模型
   （其额度桶可能仍有余量），直到备选链全部限流才按额度耗尽整批终止；
3. **429 当日额度（RPD）耗尽**：错误体含 `PerDay` / `per day` / `RPD` 等特征时立即抛 `AiQuotaExhausted`，**只调一次、不重试、不消耗后续厂商**——crawler 随即终止本次 AI 环节，所有变化厂商保留旧快照，新闻 / 渲染照常完成；多个模型连续 5xx 时抛 `AiServiceOutage` 做同样处理；
4. **熔断**：非额度类错误（Key 无效、网络）连续 3 个厂商失败即停止，同样全部保留旧快照；
5. **失败冷却**：单个厂商核查持续失败（如证据闸门不过）时按 **1 / 2 / 4 / 7 天**指数退避，冷却期内该变化不触发任何调用，状态记在 `llm-intel-state.json` 条目的 `ai_attempts / ai_retry_after / ai_last_error`，成功核查或人工不带 `--ai-review` 跑一次即清除；
6. 5xx / 网络抖动：同模型短重试后再走模型回退；400/401/403 配置错误立即报错，不做无意义的换模重试；
7. **墙钟预算**：单厂商核查受 `MAX_REVIEW_WALL_SECONDS`（默认 900s）约束。备选链变长后，
   超时重试（单次请求 `timeout=180s`）与限流退避叠加可能吃光整轮巡检时间，超预算即放弃该厂商、
   保留旧快照，下次巡检重试；CI 侧 `timeout-minutes: 60` 是第二道保险。

日志标记：`[warn]` 回退 / 退避提示、`[ai-quota]` 日额度终止、`[ai-outage]` 服务故障终止、`[ai-abort]` 连续失败终止、`[ai-cooldown]` 冷却跳过、`[ai-error]` 单厂商失败（保留旧快照并计入冷却）。

**CI 的档案更新为自动采纳**（`.github/workflows/refresh-intel.yml`，2026-09-22 改）：
- 旧的「同步遗留 `ai/intel-update` 分支」机制已于 2026-09-26 退役（最后一条遗留分支清理完毕）：**不要再建这个分支**——巡检不再读它，测试里有守卫防止该步骤复活；
- 档案更新（`profile_overrides.json` + 重渲染的 README）、快照、新闻**一次原子提交**，不再分「先开 PR、再推快照」两段（两段之间失败会静默丢失事实变更）；
- **为什么不需要人工审核**：补丁必须带**页面原文逐字证据**，无法在页面正文中逐字定位的会被整条拒绝（防幻觉）；每条改动还留 `_evidence` + `_summary`，事后可追溯，改错 `revert` 即可；
- 页面快照随巡检同步更新到 main：同一批页面文本不会在第二天再次触发 AI，页面发生新的真实变化才会重新核查。

### 人工回退手段（怎么撤销 AI 的动作）

| 情况 | 操作 |
|---|---|
| 不认可某次 AI 更新 | **`git revert` 那次巡检提交**（提交信息以 `chore(ai):` 开头，一眼可辨）；AI 从未触碰 `provider_profiles.py` |
| 已合并但发现有误 | 编辑或删除 `profile_overrides.json` 中对应厂商的键，重跑 `python crawler_llm_intel.py --no-browser --no-news` 重新渲染，即恢复人工基线 |
| 想把某厂商打回重查 | 删除 `llm-intel-state.json` 中该厂商的快照条目，下次 `--ai-review` 强制重新核查 |
| 想临时彻底关掉 AI | 本地运行不带 `--ai-review`（仅更新快照）；CI 关闭 `OPENCODE_GO_ENABLED` 并移除 Gemini / Anthropic Key（事实变化只标记、新闻照更；正文仍可机翻） |

本地复现 AI 核查：

```bash
export GEMINI_API_KEY=AIza...          # Windows: set GEMINI_API_KEY=AIza...
python crawler_llm_intel.py --only <vendor_id> --ai-review --no-browser
# 可选：AI_REVIEW_MODEL 钉死首选模型（仍有免费层回退链兜底）
#       AI_REVIEW_BACKEND=anthropic 改用 ANTHROPIC_API_KEY
```

## 维护「白嫖攻略」

README 项目介绍之后的「白嫖攻略」**不是手写 Markdown**，由爬虫写入独立的 `LLM-GUIDE:BEGIN/END` 生成块（在快速开始之前），依据 `provider_profiles.py` 顶部的 **`GUIDE_META`** 自动渲染（AI 核查可通过补丁里的 `guide_meta` 更新归类）：

- `tiers`：免费类型（`permanent` 永久免费层 / `onetime` 注册赠送 / `recurring` 周期重置 / `selfhost` 开源权重自托管）；
- `signup`：注册通道 / 门槛枚举，三值 + 空串：`email`（邮箱 / OAuth 为主，或邮箱与手机号并列可选、无硬性通道要求；免信用卡）、`phone`（中国大陆账号体系以手机号为**必需 / 主**注册通道：`+86` 短信验证码，常伴随实名；邮箱即便出现也只是可选绑定或海外入口，三方 OAuth 登录不改变本值）、`card`（需绑卡验证）；空串表示该厂商不在白嫖攻略里、暂不标注。**只有 `card` 是攻略里的真门槛**：`phone` 与 `email` 同属免卡常规注册，A/B 类分级按 `signup != "card"` 判定。
  改 `phone` 必须有注册页 / 官方文档的**一手证据**（issue #9），不许按「国内平台都用手机号」批量推断；`docs/index.html` 浏览页已加「手机号注册」分支。改完跑 `python crawler_llm_intel.py --render-only` 同步 `docs/feeds/quotas.json`（守卫 `test_committed_quotas_signup_matches_guide_meta` 会拦下忘跑的情况）。
- `scenarios`：`code` / `flagship` / `longctx` / `multimodal`（图片/视频理解与实时音视频交互）/ `image` / `embed` / `deploy` / `credit` / `referral` / `student`；
- `short`：一句话额度摘要；`tip`：防扣费提示；`pick`：懒人首选推荐语（仅给首推厂商配置，渲染为攻略第 0 节，按厂商编号排序）。

#### signup 取值证据（issue #9，2026-11-15 一手核实）

下表是 `phone` / `email` 判定的证据链。注册页均用无头浏览器实际渲染取字（JS 壳不算证据）；改值前请回访这些官方页复核，链接失效就在同轮更新。

| 厂商 | signup | 一手证据（原文 / 表单字段） | 官方页 |
|---|---|---|---|
| `modelscope` | `phone` | 注册 iframe 字段「账号名 / 手机号码 / +86 / 验证码 / 登录密码」，无邮箱注册入口 | https://modelscope.cn/register ；https://www.modelscope.cn/docs/accounts/registration.md |
| `aliyun_qwen` | `phone` | 注册 iframe 输入框「输入登录名 / 输入登录密码 / 输入手机号 / 请输入校验码」+「+86 / 发送」；帮助文档「通过手机号码注册」 | https://account.aliyun.com/register/register.htm ；https://help.aliyun.com/zh/account/user-guide/ali-cloud-account-registration-process |
| `xiaomi_mimo` | `phone` | 中国站注册页「+86 / 手机号 / 请输入验证码 / 获取验证码」（input name=phone）；官方 FAQ「中国大陆用户注册方式 - 手机号注册」，海外另有邮箱注册 | https://cn.account.xiaomi.com/fe/service/register ；https://mimo.mi.com/docs/quick-start/faq/ |
| `iflytek_spark` | `phone` | 注册页「微信扫码注册 / 手机号注册 / +86 / *请使用您本人的手机号进行注册 / 获取验证码」，输入框「请输入手机号 / 请输入手机验证码」 | https://passport.xfyun.cn/register |
| `streamlake` | `phone` | 隐私政策「您需要提供您的手机号码……我们将通过向您的手机号码发送短信验证码来验证您的身份是否有效，帮助您完成账号注册和登录」 | https://www.streamlake.com/document/POL/me16yzjnvq2ssojcjz |
| `trae` | `phone` | 登录页「+86 / 获取验证码」+ 输入框「输入手机号 / 输入验证码」；用户协议「你可以通过移动电话号码……注册账号」，另有抖音 / Apple 三方登录 | https://www.trae.cn/login ；https://www.trae.cn/terms-of-service |
| `tongyi_lingma` | `phone` | 官方 FAQ「Qoder CN（原灵码）：使用阿里云账号登录」「两套账号通过手机号验证码登录已打通」；阿里云账号注册需手机号 + 实名 | https://help.aliyun.com/zh/lingma/faq |
| `comate` | `phone` | 隐私协议「您可以通过手机号创建百度通用账号……您需向我们提供您的手机号码」，绑定邮箱仅可选，三方登录也要补绑手机号 | https://comate.baidu.com/docs/隐私协议/隐私协议.html |
| `codebuddy_workbuddy` | `email`（不改） | 官方文档「支持选择微信、手机号、邮箱或者 SSO 等登录方式」——并列可选、无硬性通道，按枚举定义归 `email` | https://cloud.tencent.com/document/product/1831/134347 |

边界：`phone` 说的是「手机号为必需 / 主通道」，不是「页面上只有手机号一个入口」——可选绑定邮箱、海外邮箱入口、三方 OAuth 登录都不改变取值；真正并列可选（谁都不是必需）时记 `email`。

README 顶部的「懒人首选速览」是 **`docs/images/top-picks.svg`**，同样由 `render_picks_svg()` 从 `GUIDE_META` 生成、随 `--render-only` / `--guide-render` 重写——**不要再手绘 PNG**：手绘图的维护点是「改一次名单就要重做一张图」，实测最容易漏（正文改了、图还停在旧名单）。SVG 是纯文本，可 diff、可校验；测试 `test_picks_svg_matches_guide_meta` 会直接对撞磁盘文件与现渲染结果，改完 `pick` 不跑渲染就会红。

本地（含 coding agent）更新推荐的固定流水线：

```bash
python crawler_llm_intel.py --picks-audit    # ① 联网：只抓首选厂商的官方页
python crawler_llm_intel.py --guide-render   # ② 离线：重排攻略块 + 速览图
python crawler_llm_intel.py --render-only    # ③ 离线：档案也改过时同步 quotas/订阅源视图
python test_workflow_and_review.py           # ④ 门禁
```

① 的输出里：`ok` = 抓到了；`sparse` = 页面是 JS 渲染壳（静态抓不到事实，要点进官方页或用浏览器兜底）；`FAIL` = 抓取失败；`快照：一致 / 已变化 / 无记录` = 与上次巡检相比该页有没有变；`（请求的 … 被重定向）` = 官方页搬家（实测 `groq.com/pricing` 跳首页、Gemini 文档迁去 `aistudio.google.com`）——这时先把 `llm-intel.yaml` 里的源地址改准，再谈额度数字。审计**只读**，不写快照，所以可以随便跑。
② 只重排 README 的攻略块与 SVG，不联网、不碰其他产物；同一份源连跑两次零改写（测试 `test_guide_render_mode_rewrites_only_the_guide_block` 钉着）。`--render-only` 按契约不碰 README，缺的就是这一格。

「限时 / 易变信息」一节与厂商表的三列时效字段（`promotions`「邀请 / 特惠活动」、`free_quota`「注册福利」、`validity`「额度有效期」）都无需手工维护——爬虫按两类判据识别已经翻篇的时效片段：写明截止/结束日期（`YYYY-MM-DD`、`YYYY年M月D日` 等）且已过当天，或把免费期的终点写成收费的起点（「将于 X 起按次收取调用费用」，这类片段一个截止字样都没有）且该日已过。命中即从展示层摘掉（README 与 `docs/feeds/quotas.json` 同步，浏览页读的就是它），**前端不复述过期活动**；档案字段与 `_evidence` 保留原句，AI 核查与证据链照旧看得见它，所以到期活动不必急着从档案里删。
修改元数据后可用 `python crawler_llm_intel.py --only <vendor_id> --no-browser` 验证单厂商逻辑；提交前运行全量巡检生成完整攻略区块。攻略区块不含时间戳，无内容变化时产物不会被改写。

## 订阅源显示名（FEED_ALIASES）

RSS 频道标题、OPML 条目、`llm-news-feeds.md` 标题、`vendors.json` 四处用的是**同一个名字**：默认取 `display_name` 去掉末尾括号限定（`通义千问 (阿里云)` → `通义千问`），例外才查 `provider_profiles.FEED_ALIASES`。

- **默认不动名字**：`Anthropic Claude`、`Cloudflare Workers AI`、`Meta Llama`、`Groq Cloud` 这类本身已经清楚的完整名保持原样——去掉公司名 / 平台名反而丢信息（2026-11-04 试过批量改，被判定过度简化后回滚）。
- 只在「回落名对普通读者不友好」时加一条别名，目前只有：`StreamLake` → `快手万擎`（英文品牌，中文读者更认产品名）。
- 别名**不带括号限定**（阅读器侧栏会截断）；只能是**有动态源**的厂商（守卫 `test_feed_aliases_cover_only_news_vendors`）。
- 合并流不再叫「合并流」：频道名 / OPML 分别是「全部厂商 · 官方动态」「All Vendors · Official News」「全部厂商 · 一条订完」——读者一眼知道这是「所有厂商的总列表」。
- 改完跑 `python crawler_llm_intel.py --render-only` 重排四处产物；feed **文件名**（`llm-news-<vendor_id>.xml`）是订阅地址，**不要跟着改名**，否则现有订阅者会断流。

## 标题汉化与 AI 优化

巡检产出的中文标题按「来源」分两层，规则不同：

- **每次巡检新抓到、尚未进归档的文章**：标题走 `translate_to_zh`（Google 公开接口 + `.translate_cache.json` 磁盘缓存；纯模型 id / 含型号 / 纯专名标题不翻，保留英文）。CI 端缓存不随仓库走，靠 GitHub Actions cache 续命，缓存被逐出后译文可能变化。
- **已进归档 `llm-news/<vendor>.md` 的文章**：只要归档里该 URL 的标题已是中文，后续巡检**原样沿用**（`Article.zh_title`），不再重新翻译——每日重抓不会把译文冲掉。沿用前先过品牌复原（`_restore_brand_names`：原文确实写着该英文品牌时才把音译换回英文拼写，历史冻结的坏译文在此自愈），另有守卫测试扫描全部产物、禁止品牌音译残留。
- **归档行的三种状态**（决定次日巡检会不会再动它）：可见标题含汉字 → 冻结译文，不再翻译；`<!--orig:X-->` 与可见标题**完全相同** → 冻结「看过原文、判定该留英文」这个决定（产品名如 `Grok Imagine API`），同样不再翻译，注释丢了就退化成「还没汉化」，实测会被机翻改成「Grok 想象 API」写回来；可见标题是英文而**没有**注释 → 机翻失败留下的，下一轮继续试。第三种状态刻意与第二种区分：机翻失败时不写注释（写入条件是译文≠原文），所以「相同」是无歧义的**冻结**信号——但冻结不等于有人做过决定：`llm-news/minimax.md` 的 `width` / `fast_pretreatment` / `last_frame_image`（单页 changelog 把列表项里的参数名当成了标题）与 `llm-news/deepseek.md` 的 `deepseek-chat` / `-reasoner` / `-coder`（它自己 API changelog 给日期段起的名字）也是这个形态，属抽取 artifact；放开会它们被机翻成「宽度」写回来，所以照旧冻结，但别当成人判过留英文。读取归档时会 `html.unescape` 标题与注释（实抓路径经 HTMLParser 已解码，`--rebuild-only` 直读 `.md`，不补这一步就会把 `&amp;` 漏进产物）。
- **归档合并时的「同篇双入口」折叠**（`_dedup_same_title`）：标题+日期完全相同、或一条是锚点卡（`/blog#…`）一条是直链的同名条目，视为同一篇文章收过两次，锚点卡折叠进直链（保留优先级：直链 > 锚点，其次 URL 更短）；两条都是直链且日期不同则不动——那是真同名文章。

因此想优化某篇文章的标题（人工润色，或让 AI 对照英文原文批量重译），**唯一编辑点是 `llm-news/<vendor>.md` 里那一行**；`docs/feeds/*.xml`、`docs/feeds/articles.json`、`llm-news-feeds.md`、README 总表都是每日巡检从归档重建的产物，直接改它们等于白改。`articles.json` 的第 5 列 `original_title` 保留英文原文，是重译时的对照素材。

改完归档想**本地立即刷新产物**（不等 CI、不跑全量抓取）：

```bash
python crawler_llm_intel.py --render-only
```

`--render-only` 只重排**视图**（`docs/feeds/*.xml` 与各类 JSON、`llm-news-feeds.md`、OPML），
**不写归档、不写语料、不写台账、不写快照、不渲染 README**，零网络请求，且幂等（同一份源
连跑第二次零改写），所以任何时候都可以安全重跑。订阅前缀 `feeds_base` 默认从 `docs/CNAME`
推导（自定义域名就是它），需要覆盖时再传 `--feeds-base`。

要连**归档本身**一起重排（改了排序、标题折叠、汉化沿用这类抓取路径逻辑）才用
`--rebuild-only`：它同样零网络请求，但会按抓取路径的规则重写 `llm-news/*.md`——其中包括
按「同标题 + 一条锚点一条直链」折掉影子行（实测 deepseek 归档 46→42）。这类 diff 要逐条
判断是不是预期的折叠，不要默认接受。个别历史上「只改了 XML 没同步归档」的条目会被拉齐成
归档现状——那正是下次 CI 的产出，属修正而非漂移。

归档条目若缺发布日期（源页面把日期放在 JS 里、或文章已滚出列表页），跑维护命令 `python crawler_llm_intel.py --backfill-dates`：它只访问**缺日期**条目对应的文章页，从 JSON-LD `datePublished` / `article:published_time` / `<time datetime>` 元数据回填（分批礼貌抓取，单次访问数有上限，见 `DATE_BACKFETCH_LIMIT`；解不出就保留空白，绝不猜日期）。日期决定归档排序与是否进合并流，回填后同样用 `--rebuild-only` 刷新产物。

### 本地精译前先回捞失败正文

本地精译、正文补齐等维护流程须先检查本轮范围内的 `fetch_failed`：英文 `.en.md`
中的字段是 `status`，`docs/feeds/bodies.json` 中对应 `en_status`。这些条目不在
`pending_translation_keys` 中，所以待译队列清零并不代表失败正文已经处理。

```bash
python crawler_llm_intel.py --fetch-bodies --allow-browser --fetch-vendor <vendor_id>
```

默认就会重试 `fetch_failed`，无需 `--refresh`；可按厂商分批。自动回捞仍失败的，
由本地 agent 逐篇打开官方原文核实，取得真实正文后补回英文语料，再逐段精译并登记
`translator: agent`。仍不可读的保留失败状态与空正文，在交付中列明未恢复项及原因。
不得凭标题或摘要编正文，也不得把失败项直接加入待译队列；已有真实中文译文不重抓。

**抓不到的行会退避，而不是每天重打一遍**（`.body_retry_ledger.json`，与翻译缓存同类：
不进 git、CI 走 Actions cache 续命，删掉即恢复每天重试）。退避长度按**失败性质**分三档：

| 失败性质 | 判据 | 下次再试 |
|---|---|---|
| 页面没了 | `404 / 410` | 180 天后 |
| 临时故障 | 没拿到响应 / `429` / `5xx` | 1/2/4/7/14/30 天阶梯 |
| 确定性失败 | 拿到 200 却没有正文、`403` 反爬 | **一次就退 30 天**，不按天重打 |

抓成功即清账。要立刻把窗口内的行全部重试一遍用 `--ignore-body-retry`
（`--refresh`、`--retry-unreadable` 同样绕过退避）。「连续失败」记的是同一 URL 在**同一环境**
里连续抓不到的次数——本地与 CI 各存各的台账，因为出口 IP 与浏览器能力不同，
本地 403 不等于 CI 403，两边的观察不能互相覆盖。

**核实过的失败要落成状态，而不是只靠缓存**：退避台账按机器存，换台机器或缓存被逐出
就重新试；而「这条我们已经确认取不到」是**结论**，该写进语料。

```bash
python crawler_llm_intel.py --mark-unreachable <slug> \
    --unreachable-note "Cloudflare + 客户端渲染：requests 200 仅 JS 外壳，无头 Edge 为 403"
```

`unreachable` 的语义是「**已核实**：这条在我们这条管线里取不到正文」（反爬 / 客户端渲染 /
已下线 / 非文章页面）：正文清空、退出每日重试、并清掉它的退避账；`--retry-unreadable`
可重看。它和 `index_page`（「这不是文章」）是两件事，别拿后者当「别抓了」的开关——
那会让 reader 以为这篇是目录页，连本地 `--allow-browser` 回捞也会一起跳过。
退避只改「下次什么时候再试」，**不改任何判据**：`fetch_failed` 仍是「这篇正文我们没拿到」，
`index_page` 仍是「这不是文章」。别拿 `index_page` 当「别抓了」的开关 —— 它会让 reader 与
后来维护者误判，连本地 `--allow-browser` 回捞也会一起跳过。
正文有变更后同轮执行 `--render-only` 并运行门禁，产物随源一起提交。

### 翻译批次 QC（`--translation-qc`）

本地精译一批正文后，先跑只读 QC，再 reconcile / 提交：

```bash
python crawler_llm_intel.py --translation-qc          # 默认检查 git 改动/未跟踪的 docs/articles/*.md
python crawler_llm_intel.py --translation-qc --qc-path docs/articles/openai/xxx.md
```

- **硬问题（退出码 1）**：代码块与英文源不一致 / 数量不同、译文多出英文源没有的链接、品牌音译、U+FFFD 替换字符。
- **提示（不阻断）**：英文源有链接未出现在译文。目录、作者栏、追踪串等页面结构差异也会落在这里，需要人工判断，别把 WARN 当泄漏。
- **链接差异只是信号，不是链接真值**：英文源同样是抓取快照，站方可能已把链接迁到新地址（实测 vLLM 旧域名 → `vllm.ai/blog/...`）。修 URL 前先打开目标核对，别直接把英文源那个 URL 抄回去。
- 链接身份复用 `normalize_url`，并额外把 www / 自链接 / `__hs*`、`_gl` 追踪参数折成同一形态；命令只读，不写任何文件。

### 英文原文回填（`--backfill-orig`）

`<!--orig:…-->` 注释是 AI 重译标题时的对照素材，也是 `articles.json` 第 5 列 `original_title` 的来源。`--backfill-orig` 逐篇访问「可见标题已汉化、但归档没存原文」的条目，只补注释、不动可见标题/顺序/日期。三条规则值得知道：

- **锚点行不发请求**：URL 带 `#` 的行是单页列表的合成锚点，没有独立文章页，访问它取回的是列表页自己的标题，写进去就是假原文。
- **台账 `.backfill_orig_ledger.json`**（与 `.translate_cache.json` 同类，不进 git、CI 侧走 actions/cache）：记「这一页给不出英文原文」（`none`）和站方的**稳定**拒绝（`http-403/404/410` 这类 4xx），下轮不再重打。限流与临时故障——`408/425/429`、5xx、超时、连接失败——**不记账**，下轮再试（判据与 `_fetch_with_requests` 的可重试集合一致；实测把 429 当永久失败烧进台账，一次误操作就判死了一家厂商）。台账每 25 条增量落盘，中断的一轮也留得住已判过的账。台账是缓存不是判决——删掉文件（或缓存被逐出）就重新开始尝试。
- **别同时跑两轮**：回填没有跨进程互斥，两个进程并发打同一家会互相触发限流（实测 335 条 429），还会在同一份归档上竞争写。
- **`--only` 可分批**：`python crawler_llm_intel.py --backfill-orig --only huggingface` 只处理那一家，用来绕开「整批 403 的厂商卡在字母序中途烧光配额」。

CI 在爬虫**之前**跑这一步（当天回填的原文当轮就进产物），失败不阻断巡检（`continue-on-error`）。

巡检启用 `--ai-titles` 时，首次收录的英文标题按预算分批润色，模型以编号文本返回译文，写进归档后冻结。事实核查已熔断，或标题润色遇到整批限流、服务故障时，本轮剩余标题直接回落 Google 机翻。已经成功的批次保留译文。

两个已知取舍：官方日后改文章标题，我们停在旧译文（改归档那一行即可跟进）；Google 刚机翻出来的新标题同样会被冻结——不过 CI 的 `--ai-titles` 已在冻结前先润色一轮，只有 LLM 不可用的日子才需要人工补。

### 本地 AI 核查（无 API Key 的正式通道）

CI 的 Gemini 免费层 RPD 会耗尽、或你希望由本地 agent 亲自核查时：

```bash
python crawler_llm_intel.py --review-export          # 组卷：待核查厂商 → .ai-review/packets/<vid>.prompt.md（指纹登记在 .ai-review/manifest.json）
# 让本地 AI 阅读核查包（与远端模型所见 prompt 完全一致），
# 按包尾「输出格式」写 .ai-review/packets/<vid>.json；无事实变化填 {"changed": false}
python crawler_llm_intel.py --review-apply           # 过同一道逐字证据闸门后入库并前进快照
```

`--review-apply` 只重抓有待应用补丁的厂商情报页，按证据的 URL 对照**当次页面**原文。`--only` 可进一步限定厂商。manifest 指纹记录导包时的本地状态，供追溯。给本地 agent 的标准指令是「处理 .ai-review/packets/ 下所有 prompt.md，按包尾输出格式填同名 json」。

证据失效的补丁保留原文件和旧快照。`changed: false` 仅在当次核查材料及实抓快照与导包时一致时采纳；若收到 `[local-reject]` 提示材料已变，重新导包核查。补丁采纳成功后才改名为 `.json.applied` 并推进快照。导包本身不推进待核查变化的快照。`.ai-review/` 已 gitignore，核查产物（overlay / changelog / 快照）与远端通道使用同一套校验规则。
