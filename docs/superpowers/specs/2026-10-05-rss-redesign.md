# RSS 订阅源改造（限量 / 双语 / 正文）

**状态**：已批准（4 项待定问题全部锁定，见 §8）。日期 2026-10-05。

## 1. 背景与现状

`write_rss_feeds()` 已经产出：

- `docs/feeds/llm-news-all.xml` — 合并流，`RSS_MERGED_LIMIT = 0` 即**不限量**
- `docs/feeds/llm-news-<vendor>.xml` — 每厂商一个源，**全量归档**
- `docs/feeds/llm-intel-changes.xml` — 变更日志流

每个 `<item>` 只放：`<title>` / `<link>` / `<guid isPermaLink=true>` / `<pubDate>`
/ `<category>` / `<source>` / 可选 `<description>`（超 60 字截断时把完整标题、
英文原标题塞进来）。

**痛点**（实测 2026-10-05）：

- 合并流 3433 条 / 1.9 MB，openai 单厂商 1210 条；主流阅读器（Feedly/Inoreader）
  对 >100 条的 feed 会分页/截断，也会拖慢 fetch
- **正文没进 feed**——但项目已花大代价抓出 `docs/articles/<vendor>/<slug>[.en].md`
  双语正文（3061 中 + 2453 英），完全没被 RSS 消费。用户"看 feed 即读全文"的诉求
  没落地。
- 单语言：中文标题，英文原标题只在 `<description>` 里以文本形式出现，非英语用户
  没有直接可订阅的英文源。

## 2. 目标

三条独立可开的改动：

- **G1 限量**：合并流默认 200 条 / 单厂商流默认 50 条；`--rss-limit` /
  `--rss-vendor-limit` 覆盖。
- **G2 正文**：`<content:encoded>` 从 corpus 里读 `.md` / `.en.md` 转 HTML 塞入。
  抓不到正文（fetch_failed / index_page / 文件缺失）的条目**不写该字段**（不编造）。
- **G3 双语 feed**：每个源出一对文件——`llm-news-all.xml`（中文，走 `title` 或
  `zh_title`）与 `llm-news-all.en.xml`（英文，走 `original_title`）；OPML 并列列出
  两条，用户自选。

不在本次范围：`llm-intel-changes.xml`（配额变更流，条目本就少，不动）；
非 RSS 出口（README / 浏览页）除非受限量/双语改动连带要改文案。

## 3. 设计决策

### 3.1 限量口径

- 合并流默认 **200**（覆盖两周 × 35 厂商 × 每日新增的合理上限）
- 单厂商流默认 **50**（每厂商月产 3-15 条常见，50 条够回看一个季度）
- 两个默认值都用命名常量：`RSS_MERGED_LIMIT = 200` / `RSS_VENDOR_LIMIT = 50`
- CLI：`--rss-limit N`（0 = 不限制，兼容现有语义），新增 `--rss-vendor-limit N`
- 无日期条目仍**只进单厂商源、不进合并流**（现有规则不改），只是单厂商源也限量了
- 未来日期条目仍整条排除（现有规则不改）

### 3.2 正文抽取路径

- 每个 `<item>` 用 `urlhash = sha256(normalize_url(url))[:12]`（与 `fulltext.py` 同
  一身份）在 `bodies.json` 里查条目 → 拿 `en_path` / `zh_path`
- 中文版 feed：读 `zh_path` 指向的 `.md`（若是 native 中文源即 `translator: native`
  的 .md；若是人译 .md 也走这个）
- 英文版 feed：读 `en_path` 指向的 `.en.md`
- Markdown → HTML：新增 stdlib 手写小 helper `_md_to_html(md: str) -> str`，
  覆盖语料里实际出现的构造（ATX 标题 / 段落 / 有序无序列表 / fenced code block /
  粗体斜体 code span / 链接 / 图片 / pipe 表格）。**不引第三方 md 库**（与"不引
  bs4"的自律一致）。helper 输出**已 HTML 转义**（`<>&` 变实体），避免正文里的
  `<html>` 破坏 XML；`<script>` `<iframe>` `<style>` `<link>` 一律剥除防 XSS 面
- 空 body / 无对应文件的条目：**不写 `<content:encoded>`**（不塞空字符串，避免
  阅读器显示"空正文"）

### 3.3 双语 feed 与 guid

- 两条 feed 的 `<guid>` 若都用文章原 URL，多数阅读器会按 guid 去重，用户同订两条
  只看到一份——这不是我们要的效果（用户想同订看中英）。
- **决策**：guid 用 query 后缀区分。中文版 `guid` = 原 URL（保向后兼容，旧订阅者不
  重下）；英文版 `guid` = 原 URL + `?li=1`。选 query 而非 fragment 的原因：`#frag`
  会被部分阅读器剥掉、`?li=1` 保留稳定
- `<link>` 两个版本都指向原 URL（跳回原文）
- `<description>` 里的"原文标题：xxx"在中文版保留（帮中英混排读者对齐），英文版
  省掉（title 就是英文，无须再列）

### 3.4 OPML 与文档

- OPML 并列列出双版：每个厂商两条 outline（中文 → `llm-news-<vid>.xml`，英文 →
  `llm-news-<vid>.en.xml`），display_name 后缀标 `EN`
- 合并流同样两条
- `llm-news-feeds.md` 章节文案改："每条源都有中/英两版，读者任选一版；若两版都订
  会看到重复条目（guid 不同，阅读器不去重）。"
- **英文 feed 只列英文正文可给的条目**：`bodies.json` 里 `en_status ≠ "ok"`（含
  native 中文、fetch_failed、index_page）的条目在英文 feed 中**整体跳过**，不进
  `<item>`。中文原生源（aliyun_qwen / moonshot_kimi 等）在英文 feed 里可能整源为空
  ——那就不生成该 `.en.xml` 文件，OPML 里也不列它的英文 outline
- 浏览页 `docs/index.html` 的"按厂商订阅"链接默认跳中文版；如需英文可在 UI 上加
  语言切换（**不在本次范围**）

### 3.5 幂等与增量

- `clean_removed` 现在只按 vendor_id 判断旧 feed 是否要删。双语改造后，删除条件要
  同时覆盖 `llm-news-<vid>.en.xml`，且当某厂商从"有英文正文"退化为"全 fetch_failed"
  时英文 feed 也不能变空文件——保留上次的（现有对中文 feed 的行为一致）
- CI 每日一次全量重生成 feed 文件，不做增量

## 4. 落地位置（实施记录）

代码全部在 `crawler_llm_intel.py` 与 `test_workflow_and_review.py`。核心入口：
`write_rss_feeds()` / `_rss_item()` / `_md_to_html()` / `_body_html_for()` /
`_english_eligible()` / `_summarize_html()` / `_emit_merged()`。常量：
`RSS_MERGED_LIMIT` / `RSS_VENDOR_LIMIT` / `RSS_EN_GUID_SUFFIX` / `RSS_SOFT_CAP` /
`RSS_SUMMARY_CHARS`。CLI：`--rss-limit` / `--rss-vendor-limit`。OPML 与
`llm-news-feeds.md` 双列分别在 `write_opml()` / `render_news_section()`。
具体 commit 见 `git log --oneline`。

## 5. 测试与不变量（实施记录）

三个测试类覆盖：
- `TestRssDualFeeds` — 双文件发射 / guid `?li=1` / native 中文源英文侧跳过 /
  `vendor_limit` 生效 / `fetch_failed` 排除
- `TestRssContentEncoded` — `_md_to_html` 各构造、raw HTML 转义、CDATA 拆分、
  `xmlns:content` 声明、`_body_html_for` 端到端注入、缺文件不塞字段
- `TestRssSizeCapDegrade` — `_summarize_html` 截断与不切半开标签、合并流产物
  超阈值自动降级

**变异守卫**（都验证过）：
- 把 `RSS_EN_GUID_SUFFIX = ""` → guid 测试变红（测试硬编码 `?li=1` 字面量、不引常量）
- 把 `RSS_SOFT_CAP` 乘 10000（关闭判定）→ 降级测试变红

## 6. 迁移与回滚

- **上线即全量重跑**：CI 下一次定时巡检产出新形态的 feed；旧阅读器订阅 URL
  `llm-news-all.xml` 不变，会自动收到中文版 + 200 条版
- **旧订阅者**（期望"全量归档"）：可用 `--rss-limit 0` 手动触发一次或写死该
  参数；本次默认从"全量"改"200 条"，是**破坏性变更**——需要在 README 或
  CHANGELOG 说明
- **回滚**：把 `RSS_MERGED_LIMIT` / `RSS_VENDOR_LIMIT` 改回 0 即可（feed 内容
  不变，只条数变化）；`<content:encoded>` 字段阅读器自动忽略不认识的字段，无风险

## 7. 风险

- **体积**：合并流 200 条 × 中英 × 平均正文 8 KB → 约 3.2 MB（HTML 化后比 markdown
  再胀 20%）。GitHub Pages 单文件软上限 25 MB，安全。若真某天 openai 长文密集导致
  超阈值，见 §7.1 降级策略
- **XSS**：正文里 `<script>` `<iframe>` `<style>` `<link>` 一律在 md→html 前**剥
  除**（§3.2）；输出走 CDATA 包 HTML 转义后的字符串
- **HTML 转义**：`content:encoded` 用 CDATA：`<content:encoded><![CDATA[ ...
  ]]></content:encoded>`；CDATA 里的 `]]>` 序列需拆分为 `]]]]><![CDATA[>`

### 7.1 超阈值降级

- CI 生成合并流时（`write_rss_feeds` 内），若产物 > `RSS_SOFT_CAP`（新常量，建议
  **5 MB**，留 5× headroom 到 Pages 单文件 25 MB 上限），**自动降级**：中文合并流
  保留 `<content:encoded>` 但截正文到前 500 字 + `[阅读完整文章 →](link)`；英文同规则
- 单厂商流不降级（每厂商 feed 独立，读者按需要订阅，可控）
- 降级时 `llm-news-feeds.md` 附一行说明当前状态（可选，取决于产物大小趋势）

## 8. 已决问题

- **Q1 合并流塑不塑全文**：塑。超 5 MB 自动降级为首段摘要 + 回源链接（§7.1）
- **Q2 内容形态**：走**手写 stdlib md→html helper**（§3.2），覆盖语料实际出现的
  构造，剥危险标签、HTML 转义、CDATA 包裹
- **Q3 guid 后缀**：`?li=1`；中文 guid = 原 URL（向后兼容），英文 guid = 原 URL
  `?li=1`
- **Q4 中文原生正文**：英文 feed **整体跳过** `en_status ≠ ok` 的条目；某厂商若
  全是 native 中文，则不出该厂商 `.en.xml`，OPML 也不列

## 9. 里程碑

**当前进度**（2026-10-05）：R1a / R1b / R2 / R3 全部落地，377 测试通过、guid 与降级两条变异守卫都跑过。

- **R1a** 常量：`RSS_MERGED_LIMIT 0→200`、`RSS_VENDOR_LIMIT = 50`、`RSS_EN_GUID_SUFFIX = "?li=1"`
- **R1b** 双语发射：`_rss_item`/`_rss_channel` 加 `lang`、`write_rss_feeds` 出 `.en.xml`、
  `clean_removed` 处理孤儿、`vendors.json` 加 `feed_en`、OPML / `llm-news-feeds.md` 双列、
  `--rss-vendor-limit` CLI
- **R2** 正文注入：`_md_to_html` + `_rss_cdata` + `_body_html_for`；`_rss_item` 消费
  `content_html`；`xmlns:content` 声明；native 中文源不出英文 feed
- **R3** 降级：`RSS_SOFT_CAP` 5 MB 阈值 + `_summarize_html` 首段摘要 + 回源链接

**未做**（下一轮 / 独立特性）：
- **R4 可选（部分）**：`docs/index.html` 顶部 `<link rel=alternate>` 加英文版让浏览器/
  阅读器扩展识别订阅发现——本轮已顺带做了。订阅按钮的**语言切换 UI**仍待。
- **M1 浏览页 reader**（corpus spec §9）：点开条目就地读全文——语料 md 已在 repo、
  RSS `content:encoded` 也塞了，index.html 现在还是跳回原文。属独立特性，不在本轮 RSS 改造范围。
