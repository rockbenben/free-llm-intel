# 产出层（render）与源层分离 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让展示层产物（RSS / articles.json / OPML / feeds.md）可由源随时幂等复算、复算绝不写源，并把「忘了重排」变成红灯。

**Architecture:** 在 `crawler_llm_intel.py` 内新增产出层函数 `render_outputs()`，把 main() 里内联的视图写出收进去；新增 `--render-only` 旗标（只渲染、不写归档），`--rebuild-only` 改为「写归档 + 调 render_outputs」的组合；CI 在 `fetch-bodies` / `mt-bodies` 之后、Verify 之前加一步 render；六条不变量（G1–G6）各配夹具级 + 实产物级守卫。

**Tech Stack:** Python 3.14（本机）、stdlib only（`unittest`、`pathlib`、`hashlib`、`json`、`re`）、GitHub Actions（`refresh-intel.yml`）。

**Spec:** `docs/superpowers/specs/2026-10-15-render-layer-design.md`

> **勘误（2026-10-15，任务已全部执行完毕）**：Task 4 的代码片段里那句
> `[warn] {n_rss_skipped} 条因发布日期晚于今天被排除…建议核查` 和返回键
> `rss_future_excluded = n_rss_skipped` 都是假账——`n_rss_skipped` 混合了合成锚点剔除与
> 同标题折叠，实测当日真未来日期为 0。现已按 `rss_future_excluded` / `rss_other_excluded`
> 分开计数，只有日期问题才提示核查。照本计划重跑的人请以 `main` 上的实现为准。

## Global Constraints

- 测试框架是仓库自带的 `test_workflow_and_review.py`（`unittest`，512 条基线），门禁命令固定为 `python test_workflow_and_review.py`，全绿才算完成。
- 语料/归档写盘一律走既有函数（`fulltext.write_body_doc`、`write_news_archives`），不新造第二套写入口。
- 产物确定性：不得引入构建时间戳；`llm-news-feeds.opml` 的 `dateCreated` 与 RSS 的 `lastBuildDate` 已有屏蔽机制，重构必须保留。
- 不新增第三方依赖。
- 提交信息用中文、写实质不写过程词、不带署名；**push 前必须先问用户**。
- 每个任务结束时工作区必须干净（`git status --porcelain` 为空），临时脚本用完即删。
- Windows 控制台是 GBK：任何含中文/emoji 的诊断输出**落盘再用 Read 看**，不要 print 到 stdout 后靠肉眼读。

---

## File Structure

| 文件 | 责任 | 本次动作 |
|---|---|---|
| `crawler_llm_intel.py` | 源层 + 产出层实现 | 新增 `render_outputs()`、`--render-only` 旗标、`verify_index_matches_archives()`、`verify_feed_bodies()`；main() 的 12 处 `args.rebuild_only` 判据按表改成 `disk_only` |
| `test_workflow_and_review.py` | 全部门禁 | 新增 4 个测试类：`TestRenderOutputs`、`TestRenderDoesNotTouchSources`、`TestIndexMatchesArchives`、`TestFeedCarriesTranslatedBodies`；扩 `TestWorkflowYaml` |
| `.github/workflows/refresh-intel.yml` | CI 时序 | 在 `Translate new bodies (machine)` 之后、`Verify generated artifacts and invariants` 之前插入 `Render outputs` 步骤 |
| `AGENTS.md` | agent 硬规矩 | 加一条：改了 `llm-news/` 或 `docs/articles/` 必须同轮跑 `--render-only` 并提交产物 |
| `docs/superpowers/specs/2026-10-15-render-layer-design.md` | 设计正本 | 已提交，不改 |

---

### Task 1: 抽出 `render_outputs()`（纯重构，产物零变化）

**Files:**
- Modify: `crawler_llm_intel.py`（把 main() 里 `else:` 分支中 `update_news_md(...)` 到 `quotas.json` 写出那一段整体搬进新函数；新函数放在 `write_rss_feeds` 之后、`write_model_releases` 之前的产出层函数群里）
- Test: `test_workflow_and_review.py`（新增 `TestRenderOutputs`）

**Interfaces:**
- Consumes: `update_news_md`、`render_news_section`、`write_rss_feeds`、`extract_model_releases`、`write_model_releases`、`build_quotas_payload`、`write_intel_changes_feed`、`write_opml`、`_write_json`、常量 `CHANGELOG_MD`、`INTEL_CHANGES_FEED`（均为既有）
- Produces:
```python
def render_outputs(root: Path, intel_list: list[VendorIntel], *, feeds_base: str,
                   all_vendors: list[dict], reviews: dict,
                   news_md_path: Path | None = None, opml_path: Path | None = None,
                   feeds_dir: Path | None = None, changelog_path: Path | None = None,
                   rss_limit: int = 0, rss_vendor_limit: int = 0) -> dict
```
返回 dict 的键（后续任务与 CLI 打印都依赖这些名字）：
`{"news_md_changed": bool, "rss_files": int, "rss_items": int, "rss_changed": int,
"rss_future_excluded": int, "releases": int, "releases_changed": bool,
"changes": int, "opml_feeds": int, "quotas_count": int, "quotas_changed": bool}`

- [ ] **Step 1: 先记录重构前基线（幂等前提）**

Run:
```bash
python crawler_llm_intel.py --rebuild-only > /dev/null 2>&1
git status --porcelain | wc -l
```
Expected: `0`（当前树已同步，rebuild 是空操作；2026-10-15 实测为 0）。若不是 0，先提交或还原到干净树再继续——否则后面无法用「零 diff」当验收。

- [ ] **Step 2: 写失败测试（函数还不存在）**

先补 import：`test_workflow_and_review.py` 顶部**没有** `hashlib`（2026-10-15 核对：现有为
ast/contextlib/io/json/os/re/shutil/subprocess/tempfile/types/unittest + datetime/pathlib/mock
+ requests/yaml/ai_review/crawler_llm_intel/provider_profiles/fulltext as ft）。
在 `import contextlib` 之后加一行 `import hashlib`，保持字母序。

然后在 `test_workflow_and_review.py` 末尾追加：

```python
class TestRenderOutputs(unittest.TestCase):
    """产出层：render_outputs 只写视图、可重复跑、不碰源。"""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "llm-news").mkdir(parents=True)
        (self.root / "docs" / "feeds").mkdir(parents=True)
        (self.root / "docs" / "articles" / "vendor_a").mkdir(parents=True)
        self.addCleanup(self.temp_dir.cleanup)

    def _fixture_tree(self):
        """1 厂商 3 条归档：1 条有中文译文、1 条待译、1 条无日期。"""
        (self.root / "llm-news" / "vendor_a.md").write_text(
            "# Vendor A 文章归档\n\n"
            "> 由 `crawler_llm_intel.py` 自动整理，抓取于 **2026-10-15**。\n\n"
            "## 全部文章（共 3 篇，按日期倒序；无日期条目列于最后）\n\n"
            "1. [第一篇中文标题](https://a.com/one)（2026-10-14） <!--orig:First post-->\n"
            "2. [Second post](https://a.com/two)（2026-10-13） <!--orig:Second post-->\n"
            "3. [无日期条目](https://a.com/three)\n",
            encoding="utf-8")
        zh = ("---\nvendor: vendor_a\ntitle: 第一篇中文标题\noriginal_title: First post\n"
              "url: https://a.com/one\ndate: 2026-10-14\nlang: zh\ncaptured: 2026-10-15\n"
              "extractor: readability-v1\ntranslator: agent\nstatus: translated\n"
              "body_sha: 000000000000\n---\n\n# 第一篇中文标题\n\n这是中文正文，够长以便断言。\n")
        (self.root / "docs" / "articles" / "vendor_a" / "one.md").write_text(zh, encoding="utf-8")
        en = ("---\nvendor: vendor_a\ntitle: First post\noriginal_title: First post\n"
              "url: https://a.com/one\ndate: 2026-10-14\nlang: en\ncaptured: 2026-10-15\n"
              "extractor: readability-v1\nstatus: ok\nbody_sha: 111111111111\n---\n\n# First post\n\nEnglish body.\n")
        (self.root / "docs" / "articles" / "vendor_a" / "one.en.md").write_text(en, encoding="utf-8")
        bodies = {"vendor_a\thttps://a.com/one": {
            "slug": "aaa111", "en_path": "docs/articles/vendor_a/one.en.md",
            "zh_path": "docs/articles/vendor_a/one.md", "en_status": "ok",
            "zh_status": "translated", "translator": "agent", "title": "第一篇中文标题",
            "date": "2026-10-14", "captured": "2026-10-15", "body_sha": "111111111111",
            "src_lang": "en"}}
        (self.root / "docs" / "feeds" / "bodies.json").write_text(
            json.dumps({"count": 1, "bodies": bodies}, ensure_ascii=False, indent=2),
            encoding="utf-8")

    def _intel(self):
        arts = crawler_llm_intel.parse_archived_articles(
            self.root / "llm-news" / "vendor_a.md")
        intel = crawler_llm_intel.VendorIntel(
            vendor_id="vendor_a", brand="Vendor A", homepage="https://a.com",
            products=[], all_news_articles=arts)
        return [intel]

    def test_writes_views_and_returns_counts(self):
        self._fixture_tree()
        out = crawler_llm_intel.render_outputs(
            self.root, self._intel(), feeds_base="https://x.test/feeds",
            all_vendors=[{"id": "vendor_a", "brand": "Vendor A"}], reviews={})
        self.assertIsInstance(out, dict)
        for k in ("news_md_changed", "rss_files", "rss_items", "rss_changed",
                  "rss_future_excluded", "releases", "releases_changed",
                  "changes", "opml_feeds", "quotas_count", "quotas_changed"):
            self.assertIn(k, out, f"返回契约缺键 {k}")
        self.assertTrue((self.root / "docs" / "feeds" / "articles.json").exists())
        self.assertTrue((self.root / "llm-news-feeds.opml").exists())
        self.assertGreater(out["rss_items"], 0, "夹具应产出条目，否则后面的断言都是空集蒙绿")

    def test_idempotent_second_run_changes_nothing(self):
        self._fixture_tree()
        kwargs = dict(feeds_base="https://x.test/feeds",
                      all_vendors=[{"id": "vendor_a", "brand": "Vendor A"}], reviews={})
        crawler_llm_intel.render_outputs(self.root, self._intel(), **kwargs)
        before = {p.relative_to(self.root).as_posix():
                  hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in self.root.rglob("*") if p.is_file()}
        crawler_llm_intel.render_outputs(self.root, self._intel(), **kwargs)
        after = {p.relative_to(self.root).as_posix():
                 hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after, "G5 幂等：第二次渲染不得改写任何文件")
```

- [ ] **Step 3: 跑测试确认失败**

Run: `python -m unittest test_workflow_and_review.TestRenderOutputs -v`
Expected: FAIL / ERROR，`AttributeError: module 'crawler_llm_intel' has no attribute 'render_outputs'`

- [ ] **Step 4: 实现 `render_outputs()`**

在 `crawler_llm_intel.py` 的产出层函数群中新增（函数体就是 main() 里那段搬过来，`args.*` 换成参数）：

```python
def render_outputs(root: Path, intel_list: list[VendorIntel], *, feeds_base: str,
                   all_vendors: list[dict], reviews: dict,
                   news_md_path: Path | None = None, opml_path: Path | None = None,
                   feeds_dir: Path | None = None, changelog_path: Path | None = None,
                   rss_limit: int = 0, rss_vendor_limit: int = 0) -> dict:
    """产出层：从 `intel_list` 重排全部**视图**文件。

    契约（spec §3）：**只写视图，绝不写源** —— `llm-news/*.md`、`docs/articles/**`、
    `docs/feeds/bodies.json`、`llm-intel-state.json`、`README.md` 一律不碰。
    G6 守卫按调用前后的哈希集合钉住这条；G5 要求同一份源连跑两次零改写。

    `intel_list` 的来源不限：完整巡检的实抓结果，或 `rebuild_intel_from_disk` 从归档
    重建的结果——两者对产出层是同一个输入契约。
    """
    news_md_path = news_md_path or (root / "llm-news-feeds.md")
    opml_path = opml_path or (root / "llm-news-feeds.opml")
    feeds_dir = feeds_dir or (root / "docs" / "feeds")
    changelog_path = changelog_path or (root / CHANGELOG_MD)

    news_changed = update_news_md(
        news_md_path,
        render_news_section(intel_list, feeds_base, merged_limit=rss_limit,
                            vendor_limit=rss_vendor_limit))
    print(f"      {news_md_path.name} {'已刷新' if news_changed else '无内容变化，未改写'}")

    n_rss, n_rss_items, n_rss_changed, n_rss_skipped = write_rss_feeds(
        feeds_dir, intel_list, feeds_base, merged_limit=rss_limit,
        vendor_limit=rss_vendor_limit)
    print(f"      {feeds_dir.name} 自建 RSS {n_rss} 个源、{n_rss_items} 条"
          f"（本次实际改写 {n_rss_changed} 个文件）")
    if n_rss_skipped:
        print(f"      [warn] {n_rss_skipped} 条因发布日期晚于今天被排除在订阅流之外"
              "（归档 .md 中仍保留）——多为源页面日期提取有误，建议核查。")

    releases = extract_model_releases(intel_list)
    wrote_rel = write_model_releases(feeds_dir / "model-releases.json", releases)
    print(f"      模型发布雷达 {len(releases)} 个事件"
          f"（{('已刷新 model-releases.json') if wrote_rel else '无内容变化，未改写'}）")

    changelog_text = (changelog_path.read_text(encoding="utf-8")
                      if changelog_path.exists() else "")
    quotas = build_quotas_payload(all_vendors, reviews)
    anchors = {row["id"]: row["anchor"] for row in quotas["vendors"]}
    n_changes = write_intel_changes_feed(feeds_dir, changelog_text, feeds_base, anchors)
    if n_changes:
        print(f"      额度/活动变化流 {n_changes} 条（{INTEL_CHANGES_FEED} + intel-changes.json）")

    n_feeds = write_opml(opml_path, intel_list, feeds_base, merged_limit=rss_limit,
                         changes_feed=bool(n_changes)
                         or (feeds_dir / INTEL_CHANGES_FEED).exists(),
                         feeds_dir=feeds_dir)
    print(f"      {opml_path.name}（{n_feeds} 个订阅源）")

    wrote_q = _write_json(feeds_dir / "quotas.json", quotas)
    print(f"      额度快照 quotas.json {quotas['count']} 家"
          f"（{'已刷新' if wrote_q else '无内容变化，未改写'}）")

    return {"news_md_changed": bool(news_changed), "rss_files": n_rss,
            "rss_items": n_rss_items, "rss_changed": n_rss_changed,
            "rss_future_excluded": n_rss_skipped, "releases": len(releases),
            "releases_changed": bool(wrote_rel), "changes": n_changes,
            "opml_feeds": n_feeds, "quotas_count": quotas["count"],
            "quotas_changed": bool(wrote_q)}
```

然后把 main() 里 `else:` 分支（`write_news_archives(...)` 之后到 `quotas.json` 打印为止）替换为：

```python
        news_dir = news_md_path.parent / "llm-news"
        n_arch, n_arch_arts, n_arch_changed = write_news_archives(
            news_dir, intel_list, clean_removed=True, title_polish=title_polish)
        print(f"      llm-news/ 归档 {n_arch} 个厂商文件、共 {n_arch_arts} 篇文章"
              f"（本次实际改写 {n_arch_changed} 个文件）")
        render_outputs(root, intel_list, feeds_base=feeds_base,
                       all_vendors=all_vendors, reviews=snapshots.reviews,
                       news_md_path=news_md_path, opml_path=opml_path,
                       feeds_dir=feeds_dir, changelog_path=root / CHANGELOG_MD,
                       rss_limit=args.rss_limit, rss_vendor_limit=args.rss_vendor_limit)
```

注意：`write_news_archives` 必须仍在 `render_outputs` **之前**（它把合并结果写回
`intel.all_news_articles`，总表计数与 RSS 都取这份合并后列表——原注释里的顺序约束不变）。

- [ ] **Step 5: 跑新测试**

Run: `python -m unittest test_workflow_and_review.TestRenderOutputs -v`
Expected: PASS（2 条）

- [ ] **Step 6: 验收「产物零变化」（这一步是本任务的真判据）**

Run:
```bash
python crawler_llm_intel.py --rebuild-only > /dev/null 2>&1
git status --porcelain
```
Expected: 输出为空。若有 diff，逐个核对是不是重构引入的行为变化（日志文案变化可接受，产物字节变化不可接受），修到零 diff 为止。

- [ ] **Step 7: 跑全量门禁**

Run: `python test_workflow_and_review.py`
Expected: `Ran 514 tests ... OK`（512 基线 + 本任务 2 条）

- [ ] **Step 8: Commit**

```bash
git add crawler_llm_intel.py test_workflow_and_review.py
git commit -m "refactor(feeds): 抽出产出层 render_outputs，巡检路径行为零变化"
```

---

### Task 2: `--render-only` 旗标（只渲染、绝不写归档）

**Files:**
- Modify: `crawler_llm_intel.py`（`build_arg_parser()` 加旗标；main() 里 12 处 `args.rebuild_only` 判据按下表改；产出层分支加 render-only 路径）
- Test: `test_workflow_and_review.py`（扩 `TestRenderOutputs`）

**Interfaces:**
- Consumes: Task 1 的 `render_outputs(...)`、既有 `rebuild_intel_from_disk(vendors, grouped, page_states, news_dir, orig_by_key)`、`_parse_news_md_page_states(text)`、`load_original_titles(path)`
- Produces: CLI `--render-only`；main() 内局部变量 `disk_only: bool`

`args.rebuild_only` 的 12 处判据改成什么（行号为 2026-10-15 的 HEAD，实施时以 grep 结果为准）：

| 行 | 原判据 | 改成 | 理由 |
|---|---|---|---|
| 6591 | `if not args.rebuild_only:`（清 `.ai-changed`） | `if not disk_only:` | render 也不做核查 |
| 6802 | `--rebuild-only` 与 `--only/--no-news` 互斥 | `disk_only` 且报错文案同时提两个旗标 | 同为全局重建 |
| 6810 | 与 `--review-export` 互斥 | `disk_only` | 同上 |
| 6814 | 与 `--review-apply` 互斥 | `disk_only` | 同上 |
| 6822 | playwright 提示 | `disk_only` | 不联网 |
| 6827 | 基线建档提示 | `disk_only` | 不写快照 |
| 6837 | 快进重放条件里的排除项 | `disk_only` | 不走快进 |
| 6844 | `elif args.rebuild_only:` 从磁盘重建 intel_list | `elif disk_only:`，打印文案按旗标分别写 | 两种模式都要 intel_list |
| 6928 | 陈旧复查候选的排除项 | `disk_only` | 不联网 |
| 7080 | `if not args.rebuild_only:` → `snapshots.save(...)` | `if not disk_only:` | **render 绝不写 llm-intel-state.json** |
| 7090 | 跳过 README 渲染的分支 | `disk_only` | README 情报区需要实抓页面 |
| 7207 | 灾难性失败护栏的排除项 | `disk_only` | 没有实抓 |

归档写出（main() 的 `else:` 分支里那次 `write_news_archives(..., clean_removed=True)`）保持**只在非 render-only 时执行**：

```python
        if not args.render_only:
            n_arch, n_arch_arts, n_arch_changed = write_news_archives(
                news_dir, intel_list, clean_removed=True, title_polish=title_polish)
            print(f"      llm-news/ 归档 {n_arch} 个厂商文件、共 {n_arch_arts} 篇文章"
                  f"（本次实际改写 {n_arch_changed} 个文件）")
        render_outputs(...)
```

- [ ] **Step 1: 写失败测试**

在 `TestRenderOutputs` 里追加。**注意：不要在测试里真跑 `--render-only` 子进程**——它会重写
真仓库的 `docs/feeds/*`，把测试变成会弄脏工作区的操作。旗标接线用 `build_arg_parser()` 验，
「真跑一次不动源」放在下面的手工步骤（Step 5）里验：

```python
    def test_render_only_flag_is_wired(self):
        args = crawler_llm_intel.build_arg_parser().parse_args(["--render-only"])
        self.assertTrue(args.render_only)
        self.assertFalse(args.rebuild_only, "两个旗标各自独立，不得互相隐含")

    def test_render_only_is_mutually_exclusive_with_crawl_flags(self):
        """render 不联网，与 --only/--no-news/核查导包互斥；返回 2 且不做任何写入。"""
        repo = Path(crawler_llm_intel.__file__).resolve().parent
        for extra in (["--only", "openai"], ["--no-news"],
                      ["--review-export", "x.json"], ["--review-apply", "x.json"]):
            with self.subTest(extra=extra):
                rc = crawler_llm_intel.main(["--render-only"] + extra)
                self.assertEqual(rc, 2, f"--render-only 与 {extra} 应互斥")
        self.assertTrue(repo.exists())   # 仅为可读性；真判据是上面 rc==2 时早已 return
```

（`main()` 在这些互斥校验里是**先打印 fatal 再 return 2**，不会走到任何写盘分支，
所以这条测试无副作用。若实施时发现某条组合会先写盘再校验，把校验前移，别改测试。）

- [ ] **Step 2: 跑测试确认失败**

Run: `python -m unittest test_workflow_and_review.TestRenderOutputs.test_render_only_flag_does_not_touch_sources -v`
Expected: ERROR，`SystemExit: 2`（argparse 报 `unrecognized arguments: --render-only`）

- [ ] **Step 3: 加旗标与 `disk_only`**

`build_arg_parser()` 里紧跟 `--rebuild-only` 之后：

```python
    parser.add_argument("--render-only", action="store_true",
                        help="维护模式（不联网）：只从磁盘源（llm-news/ 归档 + docs/articles/ 语料）"
                             "重排产出层（docs/feeds/*.xml、articles.json、vendors.json、"
                             "model-releases.json、intel-changes.json、quotas.json、"
                             "llm-news-feeds.md/.opml）。与 --rebuild-only 的差别是**绝不写归档**，"
                             "因此可以在改完语料/归档后随时安全重跑。")
```

main() 里 `args = parser.parse_args(argv)` 之后立刻：

```python
    disk_only = args.rebuild_only or args.render_only
```

再按上表逐处替换，并把 `elif args.rebuild_only:` 那段改成：

```python
    elif disk_only:
        mode = "--rebuild-only" if args.rebuild_only else "--render-only"
        print(f"[2/4] {mode}：跳过抓取，从磁盘产物重建 ...")
        news_text = news_md_path.read_text(encoding="utf-8") if news_md_path.exists() else ""
        intel_list = rebuild_intel_from_disk(
            vendors, grouped, _parse_news_md_page_states(news_text),
            news_md_path.parent / "llm-news",
            load_original_titles(feeds_dir / "articles.json"))
        n_arts = sum(len(v.all_news_articles) for v in intel_list)
        print(f"      重建 {len(intel_list)} 个厂商、{n_arts} 篇归档文章（未发起网络请求）。")
```

- [ ] **Step 4: 跑测试确认通过**

Run: `python -m unittest test_workflow_and_review.TestRenderOutputs -v`
Expected: PASS（4 条）

- [ ] **Step 5: 手工验两条模式的行为差**

Run:
```bash
python crawler_llm_intel.py --render-only > /dev/null 2>&1 && git status --porcelain | wc -l
python crawler_llm_intel.py --rebuild-only > /dev/null 2>&1 && git status --porcelain | wc -l
```
Expected: 两次都是 `0`（当前树已同步，两种模式都应是空操作）。

- [ ] **Step 6: 全量门禁 + Commit**

Run: `python test_workflow_and_review.py` → Expected `Ran 516 tests ... OK`（514 + 本任务 2 条）

```bash
git add crawler_llm_intel.py test_workflow_and_review.py
git commit -m "feat(feeds): 加 --render-only，产出层可独立重排且绝不写归档"
```

---

### Task 3: G1 + G2 守卫（索引标题/日期必须等于归档）

**Files:**
- Modify: `crawler_llm_intel.py`（新增 `verify_index_matches_archives`，放在 `find_title_drift` 之后）
- Test: `test_workflow_and_review.py`（新增 `TestIndexMatchesArchives`）

**Interfaces:**
- Consumes: `parse_archived_articles`、`_ARCHIVE_ARTICLE_RE`、`_article_key`
- Produces: `def verify_index_matches_archives(root: Path) -> list`（返回违规描述列表，空=合规）

- [ ] **Step 1: 写失败测试**

```python
class TestIndexMatchesArchives(unittest.TestCase):
    """G1/G2：docs/feeds/articles.json 是归档的视图，标题与日期不得滞后。

    这条闸抓的就是 2026-10-15 那次事故：34 条已汉化的标题在归档里是中文、
    索引里还是英文，页面与 feed 因此显示旧文案，而门禁 512 全绿。
    """

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "llm-news").mkdir(parents=True)
        (self.root / "docs" / "feeds").mkdir(parents=True)
        self.addCleanup(self.temp_dir.cleanup)

    def _write(self, arch_title, idx_title, date="2026-10-14"):
        (self.root / "llm-news" / "vendor_a.md").write_text(
            "## 全部文章（共 1 篇）\n\n"
            f"1. [{arch_title}](https://a.com/one)（{date}） <!--orig:First post-->\n",
            encoding="utf-8")
        (self.root / "docs" / "feeds" / "articles.json").write_text(json.dumps({
            "fields": ["title", "url", "vendor", "date", "original_title",
                       "slug", "readable", "langs", "link"],
            "articles": [[idx_title, "https://a.com/one", "vendor_a", date,
                          "First post", "aaa111", "1", "both", ""]],
        }, ensure_ascii=False), encoding="utf-8")

    def test_matches_when_in_sync(self):
        self._write("第一篇中文标题", "第一篇中文标题")
        self.assertEqual(crawler_llm_intel.verify_index_matches_archives(self.root), [])

    def test_stale_title_is_caught(self):
        self._write("第一篇中文标题", "First post")
        errs = crawler_llm_intel.verify_index_matches_archives(self.root)
        self.assertEqual(len(errs), 1, errs)
        self.assertIn("First post", errs[0])

    def test_stale_date_is_caught(self):
        self._write("第一篇中文标题", "第一篇中文标题", date="2026-10-14")
        p = self.root / "docs" / "feeds" / "articles.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        d["articles"][0][3] = "2026-10-01"
        p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        errs = crawler_llm_intel.verify_index_matches_archives(self.root)
        self.assertEqual(len(errs), 1, errs)
        self.assertIn("date", errs[0])

    def test_committed_index_matches_committed_archives(self):
        repo = Path(crawler_llm_intel.__file__).resolve().parent
        if not (repo / "docs/feeds/articles.json").exists():
            self.skipTest("仓库无 articles.json，跳过实产物校验")
        errs = crawler_llm_intel.verify_index_matches_archives(repo)
        self.assertEqual(errs, [], f"索引与归档不同步（忘了 --render-only？）：{errs[:5]}")
        rows = json.loads((repo / "docs/feeds/articles.json")
                          .read_text(encoding="utf-8"))["articles"]
        self.assertGreater(len(rows), 3000, "实产物扫描没覆盖到语料规模，形状证人失败")
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python -m unittest test_workflow_and_review.TestIndexMatchesArchives -v`
Expected: ERROR，`AttributeError: ... has no attribute 'verify_index_matches_archives'`

- [ ] **Step 3: 实现**

```python
def verify_index_matches_archives(root: Path) -> list:
    """G1/G2：`docs/feeds/articles.json` 的 title / date 必须等于归档行的显示标题与日期。

    索引是归档的视图。视图滞后不会让任何 schema 校验变红（2026-10-15 实测：34 条已汉化
    标题在页面上仍显示英文，门禁 512 全绿），所以要用「源 → 视图」逐条对账来钉。
    只比对**归档里有、索引里也有**的行：收录口径（合并流截窗、canonical-only 厂商、
    折叠）由 G3 单独管，这里不重复实现，避免两条闸互相掩盖。
    """
    idx_path = root / "docs/feeds/articles.json"
    if not idx_path.exists():
        return []
    try:
        data = json.loads(idx_path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        return [f"articles.json 解析失败：{exc}"]
    fields = data.get("fields", [])
    if "url" not in fields or "title" not in fields:
        return ["articles.json 缺 url/title 列"]
    i_url, i_title = fields.index("url"), fields.index("title")
    i_date = fields.index("date") if "date" in fields else None
    index = {}
    for row in data.get("articles", []):
        index[_article_key(row[i_url])] = row
    errs = []
    for arch in sorted((root / "llm-news").glob("*.md")):
        for art in parse_archived_articles(arch):
            row = index.get(_article_key(art.url))
            if row is None:
                continue                      # 收录口径归 G3 管
            want = art.zh_title or art.title
            if row[i_title] != want:
                errs.append(f"{arch.stem}: 索引标题 {row[i_title]!r} != 归档 {want!r}（{art.url}）")
            if i_date is not None and art.date and row[i_date] != art.date:
                errs.append(f"{arch.stem}: 索引 date {row[i_date]!r} != 归档 {art.date!r}（{art.url}）")
    return errs
```

- [ ] **Step 4: 跑测试确认通过**

Run: `python -m unittest test_workflow_and_review.TestIndexMatchesArchives -v`
Expected: PASS（4 条）。若实产物那条红了，说明当前树索引与归档不同步 → 跑 `--render-only` 后重测（**不要**为了让测试绿而放宽判据）。

- [ ] **Step 5: 破坏验证（必须红一次）**

Run:
```bash
python - <<'PY'
import json, pathlib
p = pathlib.Path('docs/feeds/articles.json')
d = json.loads(p.read_text(encoding='utf-8'))
d['articles'][0][0] = 'ZZZ 故意改坏的标题'
p.write_text(json.dumps(d, ensure_ascii=False), encoding='utf-8')
PY
python -m unittest test_workflow_and_review.TestIndexMatchesArchives.test_committed_index_matches_committed_archives
git checkout -- docs/feeds/articles.json
```
Expected: 该测试 FAIL（证明实产物级守卫会咬），随后 `git status --porcelain` 为空。

- [ ] **Step 6: 全量门禁 + Commit**

Run: `python test_workflow_and_review.py` → Expected `Ran 520 tests ... OK`

```bash
git add crawler_llm_intel.py test_workflow_and_review.py
git commit -m "test(feeds): 索引标题/日期必须等于归档，忘记重排即红"
```

---

### Task 4: G4 守卫（有译文的条目必须带全文）

**Files:**
- Modify: `crawler_llm_intel.py`（新增 `verify_feed_bodies`，紧跟 `verify_index_matches_archives`）
- Test: `test_workflow_and_review.py`（新增 `TestFeedCarriesTranslatedBodies`）

**Interfaces:**
- Consumes: `fulltext.load_bodies`、`fulltext.bodies_key`、常量 `RSS_SOFT_CAP`
- Produces: `def verify_feed_bodies(root: Path) -> list`

判据（spec §6 G4）：feed item 的 `<link>` 能在台账里找到 `zh_status == "translated"` 且 `zh_path` 非空的行时，该 item 必须含 `<content:encoded>`。**例外**：整源降级——同一个 feed 文件里**所有** item 都没有 `<content:encoded>` 时视为触发 `RSS_SOFT_CAP` 的摘要版，跳过该文件（降级是既有设计，用户要全文但 2 MB 兜底优先保证可订阅）。

- [ ] **Step 1: 写失败测试**

```python
class TestFeedCarriesTranslatedBodies(unittest.TestCase):
    """G4：台账说「已有中文正文」的条目，feed 里就必须带全文。

    2026-10-15 实测的反例：Higgsfield 那条在合并流里只有 title/link/guid（456 字节），
    因为 feed 生成早于正文步骤。CI 把 render 挪到 mt-bodies 之后 + 这条闸，
    「正文晚一天」才不会再静默发生。
    """

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "docs" / "feeds").mkdir(parents=True)
        self.addCleanup(self.temp_dir.cleanup)

    def _write(self, item_xml):
        (self.root / "docs" / "feeds" / "llm-news-vendor_a.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0">'
            f"<channel>{item_xml}</channel></rss>", encoding="utf-8")
        (self.root / "docs" / "feeds" / "bodies.json").write_text(json.dumps({
            "count": 1,
            "bodies": {"vendor_a\thttps://a.com/one": {
                "slug": "aaa111", "en_path": "", "zh_path": "docs/articles/vendor_a/one.md",
                "en_status": "", "zh_status": "translated", "translator": "agent",
                "title": "第一篇", "date": "2026-10-14", "captured": "2026-10-15",
                "body_sha": "", "src_lang": "zh"}},
        }, ensure_ascii=False), encoding="utf-8")

    def test_item_with_translation_must_carry_full_text(self):
        self._write("<item><title>First post</title><link>https://a.com/one</link></item>")
        errs = crawler_llm_intel.verify_feed_bodies(self.root)
        self.assertEqual(len(errs), 1, errs)
        self.assertIn("content:encoded", errs[0])

    def test_item_with_content_passes(self):
        self._write("<item><title>第一篇</title><link>https://a.com/one</link>"
                    "<content:encoded><![CDATA[<p>正文</p>]]></content:encoded></item>")
        self.assertEqual(crawler_llm_intel.verify_feed_bodies(self.root), [])

    def test_whole_source_degraded_to_summary_is_exempt(self):
        """整源摘要化是 RSS_SOFT_CAP 的既有兜底，不该被这条闸当成缺正文。"""
        self._write("<item><title>A</title><link>https://a.com/one</link></item>"
                    "<item><title>B</title><link>https://a.com/two</link></item>")
        self.assertEqual(crawler_llm_intel.verify_feed_bodies(self.root), [])

    def test_committed_feeds_carry_translated_bodies(self):
        repo = Path(crawler_llm_intel.__file__).resolve().parent
        if not (repo / "docs/feeds/bodies.json").exists():
            self.skipTest("仓库无语料台账，跳过实产物校验")
        errs = crawler_llm_intel.verify_feed_bodies(repo)
        self.assertEqual(errs, [], f"feed 缺全文（正文步骤之后没重排？）：{errs[:5]}")
        xmls = list((repo / "docs/feeds").glob("llm-news-*.xml"))
        self.assertGreater(len(xmls), 20, "实产物扫描没覆盖到 feed 规模，形状证人失败")
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python -m unittest test_workflow_and_review.TestFeedCarriesTranslatedBodies -v`
Expected: ERROR，`AttributeError: ... has no attribute 'verify_feed_bodies'`

- [ ] **Step 3: 实现**

```python
def verify_feed_bodies(root: Path) -> list:
    """G4：台账里 `zh_status=translated` 的条目，出现在 feed 里就必须带 `<content:encoded>`。

    例外：整源降级。`write_rss_feeds` 在单源超过 `RSS_SOFT_CAP` 时会把**整个源**重建成
    「首段摘要 + 回源链接」，此时该文件所有 item 都没有 content:encoded —— 那是既有兜底，
    不是本闸要抓的滞后。判据用「整源零全文」而不是逐条放行，避免把真滞后也豁免掉。
    """
    import fulltext as _ft
    ledger_path = root / "docs/feeds/bodies.json"
    if not ledger_path.exists():
        return []
    bodies = _ft.load_bodies(ledger_path)
    translated = {}
    for key, e in bodies.items():
        if e.get("zh_status") == "translated" and e.get("zh_path"):
            vendor, _, url = key.partition("\t")
            translated[(vendor, _article_key(url))] = e
    errs = []
    for xml in sorted((root / "docs/feeds").glob("llm-news-*.xml")):
        text = xml.read_text(encoding="utf-8", errors="replace")
        items = re.findall(r"<item>[\s\S]*?</item>", text)
        if not items:
            continue
        with_body = sum(1 for it in items if "<content:encoded>" in it)
        if with_body == 0:
            continue                       # 整源摘要化（RSS_SOFT_CAP 兜底）
        for it in items:
            if "<content:encoded>" in it:
                continue
            m = re.search(r"<link>([^<]+)</link>", it)
            if not m:
                continue
            url = m.group(1).strip()
            vendor = xml.stem[len("llm-news-"):]
            if vendor == "all":            # 合并流的厂商要从 <category> 或 source 反查
                cat = re.search(r"<category>([^<]+)</category>", it)
                vendor = ""
                for (v, _k) in translated:
                    if cat and _k == _article_key(url):
                        vendor = v
                        break
            if (vendor, _article_key(url)) in translated:
                errs.append(f"{xml.name}: 已有中文正文却缺 <content:encoded>（{url}）")
    return errs
```

注：合并流（`llm-news-all.xml`）的 vendor 归属用台账反查（上面 `for (v, _k) in translated`
那段）。若实测这段太慢（台账 3700+ 行 × item 数），改成先建
`{_article_key(url): vendor}` 的反向字典再查——**先量再改**，不要一上来就优化。

- [ ] **Step 4: 跑测试确认通过**

Run: `python -m unittest test_workflow_and_review.TestFeedCarriesTranslatedBodies -v`
Expected: PASS（4 条）。实产物那条若红，先跑 `--render-only` 再测；仍红就逐条看是不是
真滞后（例如今天新译的 13 篇），不要放宽判据。

- [ ] **Step 5: 破坏验证**

Run:
```bash
python - <<'PY'
import pathlib, re
p = pathlib.Path('docs/feeds/llm-news-openai.xml')
t = p.read_text(encoding='utf-8')
i = t.find('<content:encoded>')
j = t.find('</content:encoded>', i) + len('</content:encoded>')
p.write_text(t[:i] + t[j:], encoding='utf-8', newline='\n')
PY
python -m unittest test_workflow_and_review.TestFeedCarriesTranslatedBodies.test_committed_feeds_carry_translated_bodies
git checkout -- docs/feeds/llm-news-openai.xml
```
Expected: FAIL（守卫会咬），随后 `git status --porcelain` 为空。

- [ ] **Step 6: 全量门禁 + Commit**

Run: `python test_workflow_and_review.py` → Expected `Ran 524 tests ... OK`

```bash
git add crawler_llm_intel.py test_workflow_and_review.py
git commit -m "test(feeds): 有译文的条目必须带全文，整源摘要化除外"
```

---

### Task 5: G3 守卫（收录口径由测试独立实现一份）

**Files:**
- Test: `test_workflow_and_review.py`（新增 `TestIndexCoverageIndependent`）

**Interfaces:**
- Consumes: `parse_archived_articles`、`_article_key`、常量 `RSS_MERGED_LIMIT`、`NEWS_CANONICAL_ONLY_VENDORS`
- Produces: 无新生产代码（这条闸只在测试里，**故意不复用产出层实现**）

- [ ] **Step 1: 写测试（独立实现收录口径）**

```python
class TestIndexCoverageIndependent(unittest.TestCase):
    """G3：归档里该收录的行必须都在 articles.json 里。

    口径在测试里**独立实现一份**（约 20 行），不调用 render/产出层代码——
    用实现验证实现等于没验证。差异要能指名到具体 URL，不能只报个数。
    """

    def _expected_urls(self, repo):
        want = set()
        for arch in sorted((repo / "llm-news").glob("*.md")):
            vid = arch.stem
            canonical_only = vid in crawler_llm_intel.NEWS_CANONICAL_ONLY_VENDORS
            for art in crawler_llm_intel.parse_archived_articles(arch):
                if "#" in art.url and canonical_only:
                    continue                      # 合成锚点在这几家不进索引
                want.add(crawler_llm_intel._article_key(art.url))
        return want

    def test_committed_index_covers_archives(self):
        repo = Path(crawler_llm_intel.__file__).resolve().parent
        idx = repo / "docs/feeds/articles.json"
        if not idx.exists():
            self.skipTest("仓库无 articles.json，跳过实产物校验")
        data = json.loads(idx.read_text(encoding="utf-8"))
        fields = data["fields"]
        i_url = fields.index("url")
        have = {crawler_llm_intel._article_key(r[i_url]) for r in data["articles"]}
        want = self._expected_urls(repo)
        self.assertGreater(len(want), 3000, "形状证人：归档解析没读到量")
        missing = sorted(want - have)
        self.assertEqual(missing, [],
                         f"{len(missing)} 条归档行没进索引（前 5：{missing[:5]}）")

    def test_bites_when_a_row_is_dropped_from_index(self):
        """破坏验证：从索引里删一行，这条闸必须红。"""
        repo = Path(crawler_llm_intel.__file__).resolve().parent
        idx = repo / "docs/feeds/articles.json"
        if not idx.exists():
            self.skipTest("仓库无 articles.json")
        data = json.loads(idx.read_text(encoding="utf-8"))
        rows = data["articles"]
        self.assertGreater(len(rows), 10)
        data["articles"] = rows[:-1]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "docs" / "feeds").mkdir(parents=True)
            (root / "docs" / "feeds" / "articles.json").write_text(
                json.dumps(data, ensure_ascii=False), encoding="utf-8")
            for p in (repo / "llm-news").glob("*.md"):
                (root / "llm-news").mkdir(exist_ok=True)
                (root / "llm-news" / p.name).write_text(p.read_text(encoding="utf-8"),
                                                       encoding="utf-8")
            have = {crawler_llm_intel._article_key(r[data["fields"].index("url")])
                    for r in data["articles"]}
            missing = self._expected_urls(root) - have
            self.assertTrue(missing, "删掉一行后必须能查出缺失，否则这条闸是空的")
```

- [ ] **Step 2: 跑测试**

Run: `python -m unittest test_workflow_and_review.TestIndexCoverageIndependent -v`
Expected: 两条都 PASS。**若第一条红了**，说明当前索引与归档口径不符（可能是真漏收，也可能是我的独立口径写错了）——逐条看 missing 的 URL 属于哪一类，先判「是口径还是数据」，再决定改测试口径还是跑 `--render-only`。不要为了让它绿而加豁免。

- [ ] **Step 3: 全量门禁 + Commit**

Run: `python test_workflow_and_review.py` → Expected `Ran 526 tests ... OK`

```bash
git add test_workflow_and_review.py
git commit -m "test(feeds): 索引收录口径由测试独立复算，漏收即红"
```

---

### Task 6: G6 守卫（render 绝不写源）

**Files:**
- Test: `test_workflow_and_review.py`（扩 `TestRenderOutputs`）

**Interfaces:**
- Consumes: Task 1 的 `render_outputs(...)`
- Produces: 无新生产代码

- [ ] **Step 1: 写测试**

```python
    def test_render_never_writes_sources(self):
        """G6：渲染前后，源层文件的哈希集合必须完全不变。"""
        self._fixture_tree()
        def snap():
            return {p.relative_to(self.root).as_posix():
                    hashlib.sha256(p.read_bytes()).hexdigest()
                    for d in ("llm-news", "docs/articles")
                    for p in (self.root / d).rglob("*") if p.is_file()} | {
                    "docs/feeds/bodies.json":
                    hashlib.sha256((self.root / "docs/feeds/bodies.json").read_bytes()).hexdigest()}
        before = snap()
        self.assertTrue(before, "夹具必须真有源文件")
        crawler_llm_intel.render_outputs(
            self.root, self._intel(), feeds_base="https://x.test/feeds",
            all_vendors=[{"id": "vendor_a", "brand": "Vendor A"}], reviews={})
        self.assertEqual(snap(), before, "render_outputs 写了源层文件")
```

- [ ] **Step 2: 跑测试确认通过**

Run: `python -m unittest test_workflow_and_review.TestRenderOutputs.test_render_never_writes_sources -v`
Expected: PASS（Task 1 的实现本来就不写源；这条闸的价值在于**以后**有人往 render 里加一行归档写出就会红）

- [ ] **Step 3: 破坏验证（必须红一次）**

临时在 `render_outputs()` 函数体第一行插入：

```python
    (root / "llm-news" / "__g6_probe.md").write_text("probe\n", encoding="utf-8")
```

Run: `python -m unittest test_workflow_and_review.TestRenderOutputs.test_render_never_writes_sources -v`
Expected: FAIL。然后**删掉这行探针**，重跑确认 PASS，并确认 `git status --porcelain` 里没有 `__g6_probe.md` 残留。

- [ ] **Step 4: 全量门禁 + Commit**

Run: `python test_workflow_and_review.py` → Expected `Ran 527 tests ... OK`

```bash
git add test_workflow_and_review.py
git commit -m "test(feeds): 产出层不得写源，哈希集合前后必须相同"
```

---

### Task 7: CI 加 render 步骤（正文当天进 feed）

**Files:**
- Modify: `.github/workflows/refresh-intel.yml`（在 `Translate new bodies (machine)` 之后、`Verify generated artifacts and invariants` 之前插入）
- Test: `test_workflow_and_review.py`（扩 `TestWorkflowYaml`）

**Interfaces:**
- Consumes: Task 2 的 `--render-only`
- Produces: CI step `Render outputs`

- [ ] **Step 1: 写失败测试**

在 `TestWorkflowYaml` 里追加：

```python
    def test_render_step_sits_after_bodies_and_before_verify(self):
        """正文步骤之后必须重排产出层，否则 content:encoded 又要晚一天。

        这一步**不加 continue-on-error**：render 失败时当天不提交，
        与 INTEL_FAIL_ABORT_RATIO「宁可不提交也不提交不一致产物」同取向。
        """
        with open(self.workflow_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        steps = data["jobs"]["crawl"]["steps"]
        names = [s.get("name", "") for s in steps]
        for need in ("Run intel crawler", "Fetch article bodies (incremental)",
                     "Translate new bodies (machine)", "Render outputs",
                     "Verify generated artifacts and invariants"):
            self.assertIn(need, names, f"缺步骤 {need}")
        i_bodies = names.index("Translate new bodies (machine)")
        i_render = names.index("Render outputs")
        i_verify = names.index("Verify generated artifacts and invariants")
        self.assertLess(i_bodies, i_render, "render 必须排在正文步骤之后")
        self.assertLess(i_render, i_verify, "render 必须排在 Verify 之前，否则守卫查的是旧产物")
        step = steps[i_render]
        self.assertNotIn("continue-on-error", step,
                         "render 失败要挡住当天提交，不能 continue-on-error")
        self.assertIn("--render-only", step["run"])
        self.assertIn("FEEDS_BASE", step.get("env", {}),
                      "render 要用与 crawler 同一个订阅前缀")
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python -m unittest test_workflow_and_review.TestWorkflowYaml.test_render_step_sits_after_bodies_and_before_verify -v`
Expected: FAIL，`AssertionError: 'Render outputs' not found in [...]`

- [ ] **Step 3: 改 workflow**

在 `Translate new bodies (machine)` 步骤之后插入：

```yaml
      # 产出层重排：正文步骤之后必须再渲染一次，否则今天新译的正文进不了 feed
      # （crawler 生成 RSS 时 .md 还不存在，`content:encoded` 要等次日才带上——
      # 2026-10-15 实测 Higgsfield 那条只有 456 字节、无正文）。
      # 只写视图、绝不写归档（G6 守卫钉住），因此可安全重跑。
      # 不加 continue-on-error：render 挂了当天不提交，宁缺勿错。
      - name: Render outputs
        env:
          PYTHONIOENCODING: utf-8
          FEEDS_BASE: ${{ vars.FEEDS_BASE }}
        run: python crawler_llm_intel.py --render-only --feeds-base "$FEEDS_BASE"
```

同时把 `Run intel crawler` 步骤上方那段注释里「滞后边界：…要到**次日**那次巡检重排 feed 时才带上全文」改成指向新步骤的说明（注释与代码同批改，别留替不存在的实现说话的注释）。

- [ ] **Step 4: 跑测试确认通过**

Run: `python -m unittest test_workflow_and_review.TestWorkflowYaml -v`
Expected: PASS（含新一条）

- [ ] **Step 5: 全量门禁 + Commit**

Run: `python test_workflow_and_review.py` → Expected `Ran 528 tests ... OK`

```bash
git add .github/workflows/refresh-intel.yml test_workflow_and_review.py
git commit -m "ci: 正文步骤之后重排产出层，新译文当天进 feed"
```

---

### Task 8: 文档与本地纪律

**Files:**
- Modify: `AGENTS.md`（「其它硬规矩」段加一条）
- Modify: `CONTRIBUTING.md`（若其中有描述产物生成时机的段落，同步一句）

**Interfaces:** 无代码接口。

- [ ] **Step 1: 写 AGENTS.md 那条规矩**

在 `## 其它硬规矩` 列表末尾加：

```markdown
- **改了 `llm-news/` 归档或 `docs/articles/` 语料，必须同轮跑
  `python crawler_llm_intel.py --render-only` 并把产物一起提交**：展示层
  （`docs/feeds/articles.json`、RSS、OPML、`llm-news-feeds.md`）是归档与语料的视图，
  不重排就会停留在旧快照（2026-10-15 实测 34 条已汉化标题在线上仍显示英文）。
  `--render-only` 只写视图、绝不写归档，可安全重跑；跑两次第二次必须是零 diff。
  忘了跑，门禁里 G1/G2/G4 会红。
```

- [ ] **Step 2: 核对 CONTRIBUTING 里是否有时机描述需要改**

Run: `grep -n "次日\|rebuild-only\|articles.json" CONTRIBUTING.md | head -20`
逐条判断：凡是说「产物由每日巡检生成」的地方，补一句「本地改源后用 `--render-only` 重排」。
没有相关段落就不改（不要为了对称硬加）。

- [ ] **Step 3: 全量门禁 + Commit**

Run: `python test_workflow_and_review.py` → Expected `Ran 528 tests ... OK`

```bash
git add AGENTS.md CONTRIBUTING.md
git commit -m "docs: 改归档或语料后必须同轮 --render-only 重排产物"
```

- [ ] **Step 4: 收尾核验（本计划的总验收）**

Run:
```bash
python crawler_llm_intel.py --render-only > /dev/null 2>&1; git status --porcelain | wc -l
python test_workflow_and_review.py 2>&1 | tail -3
```
Expected: 第一条 `0`（已同步状态下 render 是空操作）；第二条 `OK`。
然后**问用户是否 push**（本仓库规矩：push 前先问）。

---

## Self-Review

**Spec 覆盖对照**

| Spec 条目 | 落在哪个任务 |
|---|---|
| §4 `render_outputs()` + `--render-only` + `--rebuild-only` 组合调用 | Task 1、Task 2 |
| §5 CI 新时序（render 排在正文步骤后、Verify 前，不加 continue-on-error） | Task 7 |
| §5 本地流程写进 AGENTS.md | Task 8 |
| §6 G1 标题对账 / G2 日期对账 | Task 3 |
| §6 G3 收录口径独立实现 | Task 5 |
| §6 G4 有译文必须带全文（软降级除外） | Task 4 |
| §6 G5 幂等 | Task 1 Step 2（`test_idempotent_second_run_changes_nothing`）+ Task 2 Step 5 |
| §6 G6 渲染不写源 | Task 6 + Task 2 Step 1（CLI 级） |
| §7 失败模式：render 抛出不吞 | Task 7 Step 3（不加 continue-on-error）|
| §8 破坏验证每格红一次 | Task 3 Step 5、Task 4 Step 5、Task 6 Step 3、Task 5 第二条测试 |
| §9 回滚 = 删旗标 + 删 CI 步骤 | 无代码任务；Task 7 的步骤是自包含 YAML 块，删除即回滚 |
| §2 非目标（不拆模块、不修提取层缺陷） | 计划里没有对应任务，符合 |

**已知留白（有意，不是 TBD）**
- Task 4 实现里合并流的 vendor 归属用台账反查，注明「先量再改」——若实测慢，改反向字典，判据不变。
- Task 5 的独立口径若与产出层不一致，要求先判「口径错还是数据错」再动手，不预设答案。

**类型/命名一致性检查**：`render_outputs` 的返回键在 Task 1 定义、Task 2/6 只按名取用；
`verify_index_matches_archives` / `verify_feed_bodies` 的名字在 Task 3/4 的定义与调用一致；
`disk_only` 只在 main() 内使用，不跨任务。
