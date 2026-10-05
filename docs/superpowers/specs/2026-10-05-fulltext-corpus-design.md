# 全文语料库设计（Full-Text Article Corpus）

日期：2026-10-05 · 状态：待用户评审（v2：CI 接管增量） · 方案：A（分层解耦）

## 1. 目标与非目标

**目标**
- 把订阅流里每篇文章（现有 3548 篇，跨 35 厂商）的**正文**逐篇抓成 Markdown「本地副本」，存进 repo，作为后续加工的信息源。
- 双语双文件：中文为主展示，英文原档并存，便于对照与回溯源文。
- 浏览页（`free-llm-intel.aishort.top`，Pages 源 = `/docs`）点开某篇即**就地渲染**其正文，默认中文、可切英文；无正文/抓取失败则回落原外链。
- **首轮回充在本地**（agent 抓+agent 译），**此后增量由 CI 自动接管**（每日爬完链后抓新正文 + LLM 自动译）。

**翻译通道分层（避免与「译稿归我」默认冲突的隐藏矛盾）**
- **回充（3548 篇一次性）**：agent（我）逐篇人译 —— 沿用标题那轮的口径与偏好。
- **增量（CI 每日新文章）**：走仓库既有 LLM 通道（与 `--ai-titles` 同源）自动译。
- 每篇 frontmatter 记 `translator: agent | llm`，使**任何 LLM 译文日后都可被 agent 复核升级**——增量自动译是「先有可用中文」，不是「放弃质量口径」。这是你在「CI 自动译」上的明确取舍对默认纪律的一次有意偏离，特此标注。

**非目标**
- 不改现有「链接级」情报爬虫、quotas、README、RSS/OPML 的产出语义。
- 不下载图片到本地：正文里图片**保留远程 URL**。
- 不做全文站内搜索（本轮只到「逐篇就地读」；检索另议）。
- CI 的**回充**不在范围（首轮本地一次性做完；CI 只处理之后的新增/变更）。

## 2. 关键约束（已定，勿在实现时翻案）

- **范围**：全部文章，一篇不落。抓不到的正文如实标 `fetch_failed`，**绝不编造**。
- **正文来源**：一律**逐 URL 抓取 + readability 式抽取**（不采「只用 feed 自带 content」的偷懒路径）。
- **抓取环境差异**：本地回充可用**无头浏览器兜底** SPA/动态页；**CI 无浏览器**（`--no-browser`），故 CI 侧纯 `requests` —— SPA/反爬类新文章在 CI 会系统性 `fetch_failed`（见 §10，可事后本地补抓回捞）。
- **存储**：双语双文件。
- **落点**：`docs/articles/`（Pages 根在 `/docs`，页面才能 `fetch` 到；顺带满足「在 repo 里」）。
- **CI 边界**：CI 负责**增量**（只补 `bodies.json` 里缺失/过期的条目），**不得清空/重写已有正文文件**；正文这层的清理策略独立于 `llm-news/*.md`。

## 3. 数据契约

### 3.1 正文文件
- 路径：`docs/articles/<vendor_id>/<urlhash>.md`（中文）与 `<urlhash>.en.md`（英文）。
- `urlhash = sha256(normalize_url(url)).hexdigest()[:12]`。`normalize_url`：去 fragment、去已知跟踪参数（`utm_*` 等）、host 小写、无尾斜杠。**确定性**：同一 URL 多次运行得同一 slug，即便标题变化。
- 一个 URL 对应一篇文章（按 URL 天然去重）。同一 URL 多来源重复条目在抓取时折叠为一条。

### 3.2 frontmatter（中英两文件都带，YAML）
```
---
vendor: <vendor_id>
title: <展示标题；中文文件用 zh 标题，英文文件用原文标题>
original_title: <英文原标题>
url: <canonical 原文链接>
date: <YYYY-MM-DD，无法解析则空>
lang: zh | en
captured: <YYYY-MM-DD 正文抓取日>
extractor: readability-v1
translator: agent | llm        # 仅中文文件；标译者，供后续升级
status: ok | fetch_failed | paywall | translated | pending
body_sha: <正文（去 frontmatter）的 sha256[:12]，用于脏检测/幂等>
---
<正文 Markdown>
```
- 英文文件 `status ∈ {ok, fetch_failed, paywall}`；`fetch_failed/paywall` 时正文段留空。
- 中文文件仅在有译文时存在，`status: translated`；未译 = 文件不存在，队列即由 `bodies.json` 的 `zh_status` 表达。

### 3.3 独立索引 `docs/feeds/bodies.json`
- 键：`f"{vendor_id}\t{canonical_url}"`。
- 值：`{slug, en_path, zh_path|null, en_status, zh_status, translator|null, title, date, captured}`。
- **不扩 articles.json**（避开「原文列易回归」老坑）；页面把 `articles.json`（链接行）与 `bodies.json`（哪些有正文、走哪条路径）联起来用。
- 确定性：JSON 内**不含构建时间戳**（避免每日无谓 diff）；每值的 `captured` 是该篇正文的抓取日（抓到即定，重抓不变），非全局构建时刻；序列化按 key 排序固定序。

### 3.4 schema 不变量（有守卫）
- `bodies.json` 里每条 `en_status=ok` 的行，磁盘上必存在对应 `.en.md` 且其 frontmatter `status=ok`。
- `zh_status=translated` 的行，`.md` 必存在；反之文件存在但 ledger 未标 = 报错。
- `en_status ∈ {fetch_failed, paywall}` 的行，其 `.en.md` 正文段必须为空（**防编造**）。

## 4. 组件与边界（各自可独立理解/独立测）

### C1 `extract_article_markdown(html: str, base_url: str) -> dict`
- 纯函数，标准库 `HTMLParser`（无 bs4），沿用项目既有解析风格。
- 输入原始 HTML，输出 `{title, byline, date, markdown}`；markdown 保留标题层级/段落/列表/代码块/链接(绝对化)/图片(绝对化，远程 URL)/引用。
- 剥离：nav/header/footer/aside/script/style/社交/订阅框。启发式取「最大文本密度正文块」。
- 明确失败返回 `markdown=""` + `reason`（`empty`/`scaffold`(SPA 壳)/`blocked`(反爬)/`paywall`），供上层映射状态。**抓不到不猜。**

### C2 `fetch_bodies(...) · 子命令 --fetch-bodies [--only-missing | --refresh] [--allow-browser]`
- 入参源：`articles.json` 行（`url/vendor/date/title/original_title`）。
- 默认**只补 `bodies.json` 缺失或 `body_sha` 过期**的条目（CI 每日走这条，保证增量、有界）。`--refresh` 全量重抓（本地回充用）。
- 逐条：`requests` 取页 → 命中 SPA 壳/空正文/反爬 →（**仅 `--allow-browser`**，即本地）无头浏览器兜底；否则按 C1 的 `reason` 落 `fetch_failed/paywall`。→ 写 `.en.md`（原子 rename）→ upsert `bodies.json` en 侧。
- 幂等：已存在且 `body_sha` 未变则跳过。
- **批量韧性**：增量落盘、可按 `--vendor`/`--limit` 切单元、线程本地 session、失败单条记账不拖垮队列。
- 本地回充：`--fetch-bodies --refresh --allow-browser`。CI：`--fetch-bodies`（继承 workflow 的 `--no-browser` 环境，纯 requests）。

### C3 `translate_bodies`：两条译道，共用一套写盘/ledger
- 队列 = `bodies.json` 中 `en_status=ok 且 zh_status≠translated` 的行。
- **agent 回充**（子命令不译，只是我按队列逐篇人译）：读 `.en.md` → 我译 → 原子写 `.md`（frontmatter `translator: agent`）→ `--mark-translated <key>` 更新 ledger。
- **CI 增量**：子命令 `--ai-bodies`（与 `--ai-titles` 同一 LLM 通道，正文版提示词）：取 pending 的英文正文 → LLM 译 → 写 `.md`（`translator: llm`）→ 更新 ledger。失败/超长截断则留 pending，**不产半成品**。
  - 通道即 workflow 里 `--ai-review --ai-titles` 用的 **Gemini**（secret `GEMINI_API_KEY` + var `AI_REVIEW_MODEL`），实测已在 CI 配好，`--ai-bodies` 复用同一 client，不新建。
- `--mark-translated` 只改 ledger，不含翻译逻辑；`--ai-bodies` 只译缺失项，已 `translated` 的不动（幂等、增量）。
- 术语/口径沿用「AI 标题优化」那轮：中文自然、专名保留、标点按 CJK 规范。

### C4 浏览页 reader（`docs/index.html` + `window.FLI`）
- 文章行若 `bodies.json[ key ].en_status=ok`：加「全文」控件；点击 → `fetch('/articles/<vendor>/<slug>.md')` → 客户端极简单文件 md→HTML 渲染（项目零构建，内置小渲染器；与既有 `fli-core` 内联内核同处）。
- 「EN」切换：改拉 `<slug>.en.md`。
- 无正文 / `fetch_failed` / 缺 `bodies.json` 条目 → 保持今天的「外链条目」行为，不报错。
- 渲染逻辑写成 `FLI` 纯函数（如 `bodyHrefFor(entry, lang)`、`renderMarkdown(mdText)` 的纯字符串变换部分），行为测走既有 node `--test` 桥。

## 5. 数据流 & 首轮本地回充 → CI 增量接管

**首轮（本地，agent，一次性）**
1. `--fetch-bodies --refresh --allow-browser` 抓全 3548 篇英文正文 → `.en.md` + `bodies.json`。
2. agent 按厂商分批人译 → `.md`（`translator: agent`）+ ledger。
3. 提交 `docs/articles/**` 与 `docs/feeds/bodies.json`。

**此后每日 CI（增量自动）**
1. 现有链接级爬照旧产出 `articles.json` / 归档 / OPML / README / quotas。
2. `--fetch-bodies`（只补缺失/过期，纯 requests）→ 新文章英文正文（SPA/反爬类记 `fetch_failed`，页面回落外链）。
3. `--ai-bodies`（LLM 通道）→ 新文章中文译文（`translator: llm`）。
4. 原子提交增量 `docs/articles/**` + `bodies.json`（只 add/改新条目，绝不删已有正文）。

**回捞机制**：CI 侧 `fetch_failed`（SPA/无浏览器）的条目，可由本地周期性 `--fetch-bodies --only-missing --allow-browser` 补齐；`translator: llm` 的译文可按需 agent 复核升级为 `agent`。二者都不阻塞每日 CI。

## 6. CI 侧不变量（活守卫）

- **增量有界**：CI 步骤用 `--fetch-bodies`（默认 `--only-missing`），不得触发全量重抓；断言其跳过已 ok 且未变条目（否则 CI 时长/成本失控）。
- **requests-only**：CI 继承 `--no-browser`；断言 `--fetch-bodies` 在无浏览器环境下对 SPA 页返回 `fetch_failed`（走 C1 reason），**不崩、不编**。
- **非覆盖**：`--rebuild-only`/全量爬的清理（`write_news_archives` 的 `clean_removed` 只删 `llm-news/*.md`）**必须不触碰** `docs/articles/**`；CI 提交只做 add/改，**不清空** `bodies.json`。
- **防编造**：CI 产出的 `fetch_failed/paywall` 行正文必空（同 §3.4）。

## 7. 体量与仓库策略

- 3548×双语 ≈ 数千文件、repo 估 +数十 MB（首轮一次性入库，之后每日只增少量）。默认 `.md` 与 `.en.md` **都入库**。
- `.gitattributes`：`docs/articles/** linguist-generated`、`docs/feeds/bodies.json linguist-generated`，使语言统计/PR 高亮不被语料淹没。
- Pages 总量远未触限。若后续 repo 过重，可议把 `.en.md` 转 gitignore（本轮不做，需单独批准）。

## 8. 测试与自检（镜像项目纪律）

- 单元：`urlhash`/`normalize_url` 确定性与去重；C1 **golden fixtures**（≥4：长文厂商、博客厂商、自建页厂商、SPA 失败页），冻结改前副本；`bodies.json` 构建与 §3.4 schema 不变量；页面 reader 纯逻辑（node `--test`）。
- 守卫：§6 四条；「`fetch_failed/paywall` 行正文必空」的防编造差集断言。
- 纪律：每条不变量测**故意破坏一次**证明会咬；差集/基线对比证「不吞内容」；CI 步骤用「只补缺失」夹具证幂等与有界。

## 9. 分阶段与里程碑

> **当前进度**：M0（脚手架）+ M1（本地端到端切片）+ 全量回充（原 M3）已随代码、测试与快照落地；M2（CI 增量接管 + 守卫）待接入 workflow。

- **M0（脚手架）**：`normalize_url`+`urlhash`、C1 抽取器（golden 测）、`bodies.json` schema+构建+§3.4 守卫、`--fetch-bodies` 幂等/只补缺失骨架。
- **M1（端到端打通，小切片，本地）**：1 个厂商（建议 `anthropic`）跑 `--fetch-bodies --allow-browser` + 我人译前 N 篇 + 页面 reader 上线 → 证「抓→存双语→译→页面就地读」整链。
- **M2（CI 增量接管 + 守卫，待接入）**：workflow 加 `--fetch-bodies` + `--ai-bodies` 两步；`--ai-bodies` 复用 `--ai-titles` 同源的 LLM 通道；§6 四条守卫齐 + 变异验证；跑一次 CI 实测只增不改、SPA 项 `fetch_failed` 不崩。
- **M3（回充全量，本地运维）**：按 `articles.json` 计数降序分批 `--fetch-bodies` + agent 人译，每批提交；`openai`/`huggingface` 体量大、跨会话续跑（ledger 记进度）。

## 10. 风险与对策

- **抓不到正文真实存在**（SPA/付费墙/地区墙/反爬，openai/huggingface 老帖尤甚）→ 标 `fetch_failed`、页面回落外链；不追求 100%，追求「拿到的都真」。
- **CI 无浏览器 → 动态页新文章在 CI 系统性抓不到正文** → 记 `fetch_failed`；本地周期性 `--only-missing --allow-browser` 回捞补上（CI 不因此报错）。
- **CI 时长/成本** → `--fetch-bodies` 只补缺失（每日新增量小）；`--ai-bodies` 只译缺失项；正文长文比标题更贵，设单篇字数上限+截断留 pending，不产半成品。
- **LLM 增量译文质量低于 agent 口径** → `translator: llm` 显式标注，支持后续 agent 复核升级为 `agent`；这是「自动兜底」不是「终态」。
- **agent 回充跨多会话** → ledger 驱动、每篇原子落盘、按厂商分批，任何中断都可续。
- **repo 变重 / CI 误删这层** → `linguist-generated` + §6 非覆盖/增量守卫。
- **规范漂移**（urlhash/状态机/schema/双译道多处不一致）→ 单点纯函数 + schema 守卫 + 统一写盘 helper，先测后码。

## 11. 明确「不做」清单

- 不在 CI 做**回充**（3548 篇一次性本地做；CI 只增量）。
- 不下载图片。
- 不扩 articles.json 结构。
- 不做全文检索/相关性排序。
- 不改现有 quotas/README/RSS/OPML 的产出语义。
- 不引入 bs4 等新依赖（抽取器走标准库）。
