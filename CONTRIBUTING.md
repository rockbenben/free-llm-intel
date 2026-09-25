# 贡献指南

感谢关注本仓库。所有变更都围绕一个原则：**只收录官方页面能核实的信息**。第三方博客的数字、无法复核的"历史额度"不要写进档案，宁可留空并在 `notes` 注明"无法复核，不予采信"。

## 提交 Issue

- 额度变化 / 模型下架 / 活动到期：请附上**官方链接**（定价页、文档、公告），有截图更好。
- 抓取异常：附上运行命令与终端输出（注意脱敏，不要贴 API Key）。

## 新增 / 修改一个厂商

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
| `tier_caveats` | **列表**，免费层的真实边界：①只免旧版/特定模型时写清版本代差（哪一代收费）；②限速数值（RPM/RPD/TPM，文档无公开数字就明说"以控制台为准"）；③商用限制、数据隐私；④公测/限时等失效风险。**禁止"全家桶永久免费"式笼统表述**；只要归在永久/周期层（tiers 含 permanent/recurring 且免卡），该字段必填（有测试强制） |
| `preconditions` | 手机号、实名、信用卡、企业认证等门槛。注意：实名/邮箱不算门槛，只有「需要付款方式」才单列 |
| `promotions` | 限时折扣、订阅档位等活动，标注截止日与来源 |
| `invite_reward` | （可选）邀请返利 / 拉新奖励。只填官方页可核实的规则；无官方页就写明死链并写"不予采信"。**不填则不出这一行** |
| `student_benefit` | （可选）学生 / 高校师生扶持。同上，无官方页即写明"不予采信"。**不填则不出这一行** |
| `openai_compat` | （可选）字典，有则自动进「一键接入」速查表。键：`summary`（额度简述）、`api_key_label`、`api_key_url`、`base_url`、`models`（推荐填的 model id）。缺 `base_url` 不出表 |
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

- **测试集有两个，别搞混**：本地用 `unittest discover`（全部）；CI 用
  `test_workflow_and_review.ci_suite()`（全部 − `CI_EXCLUDED_CLASSES`，排除集是否为空以该常量为准，
  空集即 CI 跑全部用例）。白名单机制保留着，是为了以后真有「会破坏 CI 自身状态」的用例时有地方写，
  而不是临时去改 workflow。历史上唯一进过白名单的是 `TestCrawlerCleanup`：它会删除仓库根目录的
  `.ai-changed`（workflow「Decide commit path」的判据），后来把仓库根改成可注入的
  `crawler_llm_intel._repo_root()`、该测试改在临时目录里跑，就不再需要排除。
  取集是**从全量推导**的，新增测试类会自动进 CI。
- **新用例不要依赖真实仓库根**：要读写仓库文件时，把落点做成可注入（照 `_repo_root()` 的样子），
  测试里 patch 到临时目录 —— 否则这个用例只能被排除在 CI 之外，等于 CI 里零覆盖。
- **新增产物或新增守卫时，顺手确认它在 CI 里真的会跑**（`ci_suite()` 取到即可）——
  「测试写了但 CI 不跑」和「没写测试」在故障面前是一回事。

- **不要手工编辑 README 的两个自动生成区块**：`LLM-GUIDE:BEGIN/END`（项目介绍后的白嫖攻略）与 `LLM-INTEL:BEGIN/END`（文末厂商总表），也不要手工编辑 `llm-news-feeds.md` / `llm-news-feeds.opml` / `llm-news/` / `docs/feeds/` 的生成内容——它们在完整运行时会被自动重新渲染。人工说明可放在区块之外。
- `llm-news-feeds.opml` 的**自建源**分组只在能推导出 Pages 前缀时（CI 注入 `GITHUB_REPOSITORY`）才会写；本地跑推不出前缀，只写「官方原生源」一组——别把本地生成的 OPML 当成线上形态。厂商**官网自带** RSS 的判断（`_native_feed_vendors`）被 OPML 与 `llm-news-feeds.md` 共用，改一处即可，不要在两处各写一遍判断。
- `docs/feeds/*.xml` 与 `docs/feeds/vendors.json`、`docs/feeds/articles.json` 是自建 RSS 订阅源、厂商索引与**全量文章索引**（GitHub Pages 从这里发布），**只由脚本生成**。注意 `--no-news` 会跳过整条新闻链路，因此也不会刷新它们；改动了归档相关的抓取 / 排序 / 清洗逻辑时，请跑一次**不带 `--no-news`** 的巡检确认产物。新增厂商后订阅源会自动多一个 `llm-news-<vendor_id>.xml`、两个索引自动多一条，已下线厂商的旧源会被清理。
- `docs/index.html` 是自建 RSS 的**浏览页**（读 `docs/feeds/articles.json` 列出**全部**条目，可筛选、可搜索；选中某厂商时订阅地址自动切成该家单源），**人工维护、不参与巡检**，改它不会与脚本产物冲突。页面里的厂商清单来自 `feeds/vendors.json`，**不要在页面里硬编码厂商列表**（会随厂商增删而漂移）；`docs/.nojekyll` 关闭 Jekyll，不要删除。
- **合并流默认不限制**（`RSS_MERGED_LIMIT = 0`，收录全部有日期的条目）。曾经限 200 条，理由是「全量约 1.2 MB 会让阅读器吃力」—— **那个理由站不住**：GitHub Pages 用 gzip 传输（线上实测 `Content-Encoding: gzip`），当年那份 1124 KB 的全量 XML 压缩后只剩 131 KB。当时的判断看的是未压缩体积，别再照它把上限加回来。要限流可用 `--rss-limit N`。
- **页面为什么还读 `articles.json` 而不是合并流**：体积明显更小（不带描述）、免去 XML 解析，而且**标题不截断、还带原文标题**（feed 里截到 60 字是为了列表可读）。别顺手把页面「简化」成读合并流。
- `.translate_cache.json` 是本地缓存，不要提交。
- commit message 只描述变更内容本身。

## AI 自动核查是怎么工作的

1. 每次巡检把各官方页正文做哈希快照（`llm-intel-state.json`），与上次比对；
2. 仅快照变化的厂商才调用 LLM（`ai_review.py`），输入 = 该厂商全部情报页正文 + 当前生效档案；
3. LLM 只输出严格 JSON：变化字段、攻略元数据、以及**页面原文逐字证据**。证据不能在页面正文中逐字定位的补丁会被整条拒绝（防幻觉）；
4. 通过校验的补丁写入 `profile_overrides.json`（AI 永远不直接改 `provider_profiles.py`），在 CI 中**与快照 / 新闻一起原子提交到 main**（2026-09-22 起不再开 PR 等人工审核，理由见下）；LLM 调用失败或未配置 API Key 时保留旧快照，下次巡检自动重试。

默认后端是 **Google AI Studio 的 Gemini API**（`generativelanguage.googleapis.com`，免费层 Key 在 [aistudio.google.com/apikey](https://aistudio.google.com/apikey) 申请）：

- 环境变量 `GEMINI_API_KEY`（兼容 `GOOGLE_API_KEY`），默认模型 `gemini-3.8-flash`，可用 `AI_REVIEW_MODEL` 覆盖；
- `AI_REVIEW_BACKEND=auto|gemini|anthropic` 控制后端，`auto`（默认）为有 Gemini Key 走 Gemini、否则尝试 `ANTHROPIC_API_KEY` 直连 Anthropic；
- CI 配置指南：
  1. 在 **Settings → Secrets and variables → Actions** 配置 `GEMINI_API_KEY` Secret；
  2. 在 **Settings → Actions → General → Workflow permissions** 选择 **Read and write permissions**（**不再需要**勾选 Allow GitHub Actions to create and approve pull requests —— 2026-09-22 起巡检不再开 PR）；
  3. 若 `main` 分支开启了 Branch Protection，需将 `github-actions[bot]` 加为允许直推或 bypass 的用户；
  4. 未配置 Key 时新闻更新仍直接原子性提交 main，事实变化保留旧快照等待重试。

- **订阅源地址（`FEEDS_BASE`）**：自建 RSS 的对外前缀由 `default_feeds_base()` 按
  `GITHUB_REPOSITORY` 推导为 `https://<owner>.github.io/<repo>/feeds`，**fork 后无需任何配置**。
  但若仓库配了**自定义域名**，GitHub Pages 会把 github.io 上的请求 301 到自定义域名 ——
  于是 feed 自己声明的 `<atom:link rel="self">` 与 `<source url>`（都取这个前缀）会与
  浏览页顶部显示的地址不一致，且每个订阅多一跳。此时在
  **Settings → Secrets and variables → Actions → Variables** 加一个 `FEEDS_BASE`
  （值形如 `https://<你的域名>/feeds`）即可，workflow 会把它传给 `--feeds-base`；
  留空则退回自动推导。改完等下一次巡检生效（产物是生成的，不要手工改 XML）。

人工基线在 `provider_profiles.py`，AI 补丁在 `profile_overrides.json`（同名字段整体覆盖，`_evidence` 累积保留最近 20 条证据）。

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
| 想临时彻底关掉 AI | 本地运行不带 `--ai-review`（仅更新快照）；CI 删除 `GEMINI_API_KEY` Secret（事实变化只标记、新闻照更） |

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
- `signup`：`email`（邮箱 / OAuth 免信用卡）或 `card`（需绑卡验证）；
- `scenarios`：`code` / `flagship` / `longctx` / `image` / `embed` / `deploy` / `credit`；
- `short`：一句话额度摘要；`tip`：防扣费提示；`pick`：懒人首选推荐语（仅给首推厂商配置，渲染为攻略第 0 节，按厂商编号排序）。

「限时 / 易变信息」一节无需手工维护——爬虫自动扫描各档案的 `promotions`、`free_models` 等字段中的「截止 / 限量 / 限时 / limited time」关键词；片段中写明的截止/结束日期（`YYYY-MM-DD`、`YYYY年M月D日` 等）若已过当天，该片段自动剔除，因此到期活动应直接从档案字段中删除或改写为无日期表述。
修改元数据后可用 `python crawler_llm_intel.py --only <vendor_id> --no-browser` 验证单厂商逻辑；提交前运行全量巡检生成完整攻略区块。攻略区块不含时间戳，无内容变化时产物不会被改写。

## 标题汉化与 AI 优化

巡检产出的中文标题按「来源」分两层，规则不同：

- **每次巡检新抓到、尚未进归档的文章**：标题走 `translate_to_zh`（Google 公开接口 + `.translate_cache.json` 磁盘缓存；纯模型 id / 含型号 / 纯专名标题不翻，保留英文）。CI 端缓存不随仓库走，靠 GitHub Actions cache 续命，缓存被逐出后译文可能变化。
- **已进归档 `llm-news/<vendor>.md` 的文章**：只要归档里该 URL 的标题已是中文，后续巡检**原样沿用**（`Article.zh_title`），不再重新翻译——每日重抓不会把译文冲掉。

因此想优化某篇文章的标题（人工润色，或让 AI 对照英文原文批量重译），**唯一编辑点是 `llm-news/<vendor>.md` 里那一行**；`docs/feeds/*.xml`、`docs/feeds/articles.json`、`llm-news-feeds.md`、README 总表都是每日巡检从归档重建的产物，直接改它们等于白改。`articles.json` 的第 5 列 `original_title` 保留英文原文，是重译时的对照素材。

改完归档想**本地立即刷新产物**（不等 CI、不跑全量抓取）：

```bash
python crawler_llm_intel.py --rebuild-only --feeds-base "https://free-llm-intel.aishort.top/feeds"
```

`--rebuild-only` 从 归档 `.md`（中文标题 + 文章）+ `llm-news-feeds.md`（原生 feed 状态）+ `articles.json`（英文原文）重建全部动态类产物，零网络请求；README 情报区与快照需要实抓，不触碰。个别历史上「只改了 XML 没同步归档」的条目会被拉齐成归档现状——这正是下次 CI 的产出，属修正而非漂移。

归档条目若缺发布日期（源页面把日期放在 JS 里、或文章已滚出列表页），跑维护命令 `python crawler_llm_intel.py --backfill-dates`：它只访问**缺日期**条目对应的文章页，从 JSON-LD `datePublished` / `article:published_time` / `<time datetime>` 元数据回填（分批礼貌抓取，单次运行的访问数有上限，见 `DATE_BACKFETCH_LIMIT`；解不出就保留空白，绝不猜日期）。日期决定归档排序与是否进合并流，回填后同样用 `--rebuild-only` 刷新产物。

**新增条目的机翻标题**：巡检带 `--ai-titles`（CI 已默认开启）时，首次收录的文章标题会交给 LLM 按「信达雅」润色一次，结果写进归档后随沿用机制冻结；LLM 失败 / 缺 key 时自动回落 Google 机翻，预算内分批调用。

两个已知取舍：官方日后改文章标题，我们停在旧译文（改归档那一行即可跟进）；Google 刚机翻出来的新标题同样会被冻结——不过 CI 的 `--ai-titles` 已在冻结前先润色一轮，只有 LLM 不可用的日子才需要人工补。
