# 产出层（render）与源层分离设计

日期：2026-10-15
状态：待审
相关：`.github/workflows/refresh-intel.yml`、`crawler_llm_intel.py`、`docs/superpowers/specs/2026-10-05-rss-redesign.md`

## 1. 问题

展示层产物（`docs/feeds/articles.json`、RSS/Atom XML、`llm-news-feeds.md/.opml`、
`model-releases.json`、`intel-changes.json`）是**派生物**：它们完全由源
（`llm-news/*.md` 归档 + `docs/articles/**/*.md` 语料 + `llm-intel.yaml`/`profile_overrides.json`）
决定。但今天的管线里，派生物只在「巡检那一次、且在正文步骤之前」生成，于是出现三类滞后：

1. **正文必然晚一天**（结构性，每天发生）。CI 顺序是
   crawler(:144) → fetch-bodies(:163) → mt-bodies(:175) → Verify(:188) → Commit(:211)；
   RSS 由 crawler 生成，而当天新文章的 `.md` 在它之后两步才落盘。workflow 注释自己写明
   「今天新文章的正文今天进 reader，但 RSS 的 `content:encoded` 要到次日那次巡检重排 feed 时才带上全文」。
2. **本地改源不会重排产物**（每次本地精译都复现）。2026-10-15 实测：13 篇精译 + 37 条标题分流 +
   19 条标题修正都已进 main，但线上 `articles.json` 仍是 04:27 的旧快照——34 条已汉化的标题在页面上
   显示英文，Higgsfield 那条在合并流里只有 title/link/guid（456 字节，无 `content:encoded`）。
   本地手动跑一次 `--rebuild-only` 后两者都恢复。
3. **没有任何检查能发现"产物比源旧"**。当天门禁 512 绿，展示层滞后照样绿。

顺带发现的一处职责混淆：`--rebuild-only` 名义上是「从磁盘产物重建」，实际**同时改写归档**
（2026-10-15 实测改写了 5 个 `llm-news/*.md`，其中 deepseek 因影子折叠 46 → 42 行）。
所以「重排产物」这个动作现在会写源，每次都要人工判断那几行 diff 是折叠还是丢数据。

## 2. 目标 / 非目标

**目标**
- 产出层可随时、独立、幂等地从源复算，且**复算过程绝不写源**。
- 正文当天进 feed：CI 在正文步骤之后再渲染一次。
- 「忘记重排」会被闸拦下，而不是静默上线旧标题/旧正文。

**非目标**
- 不把产出层拆成独立模块（那是方案 B，本次明确不做）。
- 不改抓取、翻译、折叠、标题冻结等既有判据。
- 不修源数据质量缺陷：77 条「日期晚于今天」被排除在订阅流外、9 条把 API 参数名当标题
  （`width` / `fast_pretreatment` / `last_frame_image`）——这两类是提取层问题，另行立项。

## 3. 架构：两层职责

**源层**（只有抓取路径可写）
`llm-news/*.md` 归档、`docs/articles/**/*.md` 语料、`docs/feeds/bodies.json` 台账、
`llm-intel-state.json` 快照、`README.md`（情报区需要实抓页面）。

**产出层**（可由源随时复算）
`docs/feeds/*.xml`、`docs/feeds/articles.json`、`vendors.json`、`model-releases.json`、
`intel-changes.json`、`quotas.json`、`llm-news-feeds.md`、`llm-news-feeds.opml`。

分界线一句话：**归档与语料是事实，其余都是视图**。视图不得反向修改事实。

影子折叠（`_dedup_same_title`）留在源层的 `write_news_archives` 里——它决定归档长什么样，
判据与代价已由 `TestArchiveShadowFold` 钉住。产出层只读归档结果，因此渲染永远不会改变归档条目集合。

## 4. 组件与接口

新增一个函数 + 一个旗标，复用既有实现，不复制第二套判据：

```python
def render_outputs(root: Path, intel_list: list[VendorIntel], *, feeds_base: str,
                   rss_limit: int = 0, rss_vendor_limit: int = 0) -> dict:
    """只写产出层：从 intel_list（可由 rebuild_intel_from_disk 得到）重排全部视图文件。

    契约：**不得**写 llm-news/*.md、docs/articles/**、docs/feeds/bodies.json、
    llm-intel-state.json、README.md。返回值含 {files, items, rewritten, future_excluded}，
    供 CLI 打印与测试断言。
    """
```

- CLI 新增 `--render-only`：`rebuild_intel_from_disk(...)` → `render_outputs(...)`，不联网、
  不写快照、不渲染 README。
- `--rebuild-only` 保留，改为 `render_outputs(...)` + `write_news_archives(...)` 的组合调用
  （实现只有一份，避免两套产出逻辑漂移）。
- 巡检主路径（非 rebuild）末尾同样调 `render_outputs(...)`，把 crawler 现有的内联产出写出收进同一函数。

## 5. 数据流

**CI 新时序**（只加一步、只挪一处）

```
backfill-orig → crawler(抓取 + 写归档) → fetch-bodies(写语料 .en.md)
             → mt-bodies(写语料 .md) → render-only(产出层重排) → Verify(含同步守卫) → Commit
```

`render-only` 步骤**不加 `continue-on-error`**：它失败时当天不提交，与既有
`INTEL_FAIL_ABORT_RATIO`「宁可不提交当天产物，也不提交不一致的产物」同一取向。
正文步骤仍是 `continue-on-error`（增强层挂了不该挡当天巡检）。

**本地流程**（写进 AGENTS.md 一句话）
改了 `llm-news/` 或 `docs/articles/` 就必须同轮跑 `python crawler_llm_intel.py --render-only`，
并把产物一起提交。忘了跑 → 同步守卫在本地门禁就会红。

## 6. 不变量与守卫

| 编号 | 不变量 | 判据来源 | 备注 |
|---|---|---|---|
| G1 | `articles.json` 的 title 列 == 归档解析出的显示标题（`zh_title or title`） | `parse_archived_articles` | 抓「改了归档没重排」 |
| G2 | `articles.json` 的 date 列 == 归档行日期 | 同上 | 日期是排序与 pubDate 的根据 |
| G3 | 归档里**该被收录**的行都出现在 `articles.json`：测试内独立实现一份收录口径（有日期 → 进合并流；无日期 → 只进单厂商；`NEWS_CANONICAL_ONLY_VENDORS` 丢合成锚点；`RSS_MERGED_LIMIT`/`RSS_VENDOR_LIMIT` 截窗），与 `articles.json` 的行集合对账 | 测试自己的 ~20 行实现，**不调用 render** | 用实现验证实现等于没验证；差异要能指名到具体 URL |
| G4 | 出现在 feed 里的条目，若台账 `zh_status=translated` 且 `zh_path` 存在，则该 item 必须带 `<content:encoded>` | `_body_html_for` | **例外**：整源触发 `RSS_SOFT_CAP` 降级为摘要时合法缺失，判据按降级标志放行 |
| G5 | `render_outputs` 幂等：同一份源连跑两次，产物逐字节相同 | 现有「内容未变不改写」机制（`dateCreated` / `lastBuildDate` 屏蔽） | 让「随时重排」成为安全操作 |
| G6 | `render_outputs` 不写源：调用前后 `llm-news/*.md` 与 `docs/articles/**` 的哈希集合不变 | — | 本次架构的核心边界 |

G1–G4、G6 各配两格测试：**夹具级**（小树上种一个已知违规，断言变红）+ **实产物级**
（跑在仓库真产物上，沿用 Guard 5/6/7 的形状：无 `bodies.json` 时 `skipTest`，
并带「形状证人」断言确实扫到了足量条目，防空集蒙绿）。G5 用夹具跑两遍比字节。

## 7. 错误处理与失败模式

- `render_outputs` 内部单个源写出失败 → 抛出，不吞（当天不提交优于提交半成品）。
- 归档解析异常（实体、方括号标题）沿用既有守卫，不在本次改动。
- 源缺失（精简检出 / fork 无语料）→ 实产物级守卫 `skipTest`，夹具级守卫照常跑。
- 已知不等价边界要如实披露：render 与完整巡检的产物**不保证逐字节相同**
  （OPML 的重定向解析、`--backfill-orig` 的注释回填都只在联网路径发生）。
  CI 里 render 排在 crawl 之后，当天产物以 render 为准，差异会体现在当天 diff。

## 8. 测试策略

1. 夹具：造 1 厂商 / 3 条归档（1 条有 zh 正文、1 条 pending、1 条无日期）+ 对应 `.md`，
   跑 `render_outputs`，断言 G1/G2/G3/G4/G6 与幂等 G5。
2. 破坏验证（每一格都要红一次，记录在提交信息里）：
   - 改归档标题不重跑 render → G1 红；
   - 删掉一条 item 的 `content:encoded` 而台账仍 translated → G4 红；
   - 让 `render_outputs` 顺手写一个归档文件 → G6 红；
   - 让 render 写入当前时间戳 → G5 红。
3. 实产物级：G1/G2/G3/G4/G6 跑在仓库真产物上（当前状态应全绿——今天已手动 rebuild 过）。
4. 回归：`python test_workflow_and_review.py` 全绿（基线 512）。

## 9. 迁移与回滚

- 迁移一步到位：加函数 + 旗标 + CI 一步 + 守卫；`--rebuild-only` 行为对外不变（仍写归档）。
- 回滚：删掉 CI 的 render 步骤与 `--render-only` 旗标即回到今天的行为，
  因为 render 只是既有 rebuild 的子集，不留兼容垫片。
- 首次上线前先在本地跑一次 `--render-only`，确认「已同步状态下再跑一次 = 0 文件改写」（幂等证据），
  避免 CI 第一次就产出一大坨无关 diff。

## 10. 验收

- CI 当天：新文章的 feed item 带 `<content:encoded>`（不再是次日）。
- 本地：改归档/语料后不跑 render，门禁红；跑了就绿。
- `--render-only` 连跑两次，第二次 `git status` 干净。
- 归档条目集合在 render 前后不变（G6），影子折叠仍只发生在抓取路径。
