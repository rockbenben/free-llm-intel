# -*- coding: utf-8 -*-
"""
test_workflow_and_review.py —— 自动化工作流与核心模块单测
"""

import ast
import contextlib
import io
import json
import os
import re
import tempfile
import types
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

import yaml

import ai_review
import crawler_llm_intel
import provider_profiles


def build_records():
    """按 README 展示顺序构造 (序号, VendorIntel, profile) 三元组（无真实抓取）。"""
    root = Path(__file__).resolve().parent
    vendors, _sources = crawler_llm_intel.parse_yaml(root / "llm-intel.yaml")
    records = []
    for i, v in enumerate(vendors, 1):
        prof = provider_profiles.get_provider_profile(
            v["id"], v.get("name", ""), v.get("homepage", ""))
        intel = crawler_llm_intel.VendorIntel(
            vendor_id=v["id"], brand=v.get("name", ""),
            homepage=v.get("homepage", ""), products=[])
        records.append((i, intel, prof))
    return records


class TestWorkflowYaml(unittest.TestCase):
    """测试 GitHub Actions 工作流配置文件 refresh-intel.yml"""

    def setUp(self):
        self.root = Path(__file__).resolve().parent
        self.workflow_path = self.root / ".github" / "workflows" / "refresh-intel.yml"

    def test_workflow_exists_and_valid_yaml(self):
        self.assertTrue(self.workflow_path.exists(), "refresh-intel.yml 必须存在")
        with open(self.workflow_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        self.assertIsInstance(data, dict)
        self.assertEqual(data.get("name"), "refresh-intel")
        on_trigger = data.get("on") or data.get(True, {})
        self.assertIn("schedule", on_trigger)
        self.assertIn("workflow_dispatch", on_trigger)

    def test_workflow_permissions_and_concurrency(self):
        with open(self.workflow_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        perms = data.get("permissions", {})
        self.assertEqual(perms.get("contents"), "write")
        self.assertEqual(perms.get("pull-requests"), "write")

        concurrency = data.get("concurrency", {})
        self.assertEqual(concurrency.get("group"), "refresh-intel")
        self.assertFalse(concurrency.get("cancel-in-progress", True))

    def test_workflow_steps_structure(self):
        with open(self.workflow_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        jobs = data.get("jobs", {})
        crawl_job = jobs.get("crawl", {})
        steps = crawl_job.get("steps", [])

        step_names = [s.get("name", "") for s in steps]
        # 验证核心步骤必须存在
        self.assertIn("Checkout", step_names)
        self.assertIn("Setup Python", step_names)
        self.assertIn("Install dependencies", step_names)
        self.assertIn("Cache Playwright browsers", step_names)
        self.assertIn("Install Playwright Chromium", step_names,
                      "CI must install Chromium: without it ~1/3 of pages are JS "
                      "shells and the README live-evidence rows lose quality "
                      "(snapshot hashes are requests-stage-only by design)")
        self.assertIn("Sync existing AI PR overrides", step_names, "必须包含拉取并累加未合并 PR overrides 的步骤")
        self.assertIn("Restore translate cache", step_names)
        self.assertIn("Run intel crawler", step_names)
        self.assertIn("Decide commit path", step_names)
        self.assertIn("Open PR for AI-reviewed profile updates", step_names)
        self.assertIn("Commit snapshots and news after PR", step_names)
        self.assertIn("Commit all updates (direct mode)", step_names)

        # 检查 checkout 是否配置了 fetch-depth: 0
        checkout_step = next(s for s in steps if s.get("name") == "Checkout")
        self.assertEqual(checkout_step.get("with", {}).get("fetch-depth"), 0)

        # 检查 create-pull-request 是否配置了 delete-branch: true
        crawl_step = next(s for s in steps if s.get("name") == "Run intel crawler")
        self.assertNotIn("--no-browser", crawl_step.get("run", ""),
                         "CI crawler run must keep the browser fallback enabled")
        self.assertIn("--ai-review", crawl_step.get("run", ""))

        pr_step = next(s for s in steps if s.get("name") == "Open PR for AI-reviewed profile updates")
        self.assertTrue(pr_step.get("with", {}).get("delete-branch"), "PR 步骤必须启用 delete-branch: true")

        # 检查步骤顺序：Open PR 步骤必须在 Commit snapshots and news after PR 步骤之前
        pr_idx = step_names.index("Open PR for AI-reviewed profile updates")
        commit_idx = step_names.index("Commit snapshots and news after PR")
        self.assertLess(pr_idx, commit_idx, "Open PR 必须在 Commit snapshots 之前执行，保证 PR 失败时不污染 main 快照")


    def test_pending_pr_overrides_cannot_reach_main_via_direct_mode(self):
        """Pending-PR overrides only land via the PR branch: direct mode must
        restore them to main HEAD first.

        Regression: the sync step pulls the unmerged ai/intel-update
        profile_overrides.json into the worktree and the crawler renders README
        with those overrides; if that run takes direct mode (no new change /
        changed=false / no key), the old workflow committed both straight to
        main and bypassed human PR review.
        """
        with open(self.workflow_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        steps = data["jobs"]["crawl"]["steps"]
        by_name = {s.get("name", ""): s for s in steps}

        sync = by_name["Sync existing AI PR overrides"]
        self.assertEqual(sync.get("id"), "prsync")
        self.assertIn('echo "synced=true"', sync.get("run", ""))

        direct = by_name["Commit all updates (direct mode)"]["run"]
        self.assertIn("steps.prsync.outputs.synced", direct)
        add_pos = direct.index("git add")
        guard = direct[:add_pos]
        self.assertIn("git checkout HEAD -- README.md profile_overrides.json", guard)

        pr_commit = by_name["Commit snapshots and news after PR"]["run"]
        self.assertNotIn("profile_overrides.json", pr_commit)
        self.assertNotIn("README.md", pr_commit)

    def test_workflow_commits_self_hosted_feeds(self):
        """docs/feeds 是 GitHub Pages 的发布目录：两条提交路径都必须带上它。

        Regression: 只改脚本不改 git add，Pages 上的订阅源就永远是初始那一版，
        而本地产物看起来完全正常（新增文章全在仓库里，只是没人订阅得到）。
        """
        with open(self.workflow_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        by_name = {s.get("name", ""): s for s in data["jobs"]["crawl"]["steps"]}
        for step in ("Commit snapshots and news after PR", "Commit all updates (direct mode)"):
            self.assertIn("docs/feeds", by_name[step]["run"],
                          f"{step} 必须提交自建 RSS 产物，否则 Pages 上的订阅源不会更新")

    def test_ci_verifies_with_ci_safe_suite(self):
        """CI 的校验步骤必须跑「全部 − 白名单」，且不得把 TestCrawlerCleanup 带进去。

        Regression: 该步骤曾只跑 TestNewsSectionCountConsistency 一个类，于是订阅源
        文件名漂移、OPML 分组、归档日期完整性、README 链接失效等守卫全都不在 CI 里，
        得等提交之后才发现；而反过来无脑跑全量（`unittest discover`）又会因为
        TestCrawlerCleanup 删掉 .ai-changed 而踩坏 PR 路由。
        """
        with open(self.workflow_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        steps = data["jobs"]["crawl"]["steps"]
        step = next((s for s in steps
                     if str(s.get("name", "")).startswith("Verify generated artifacts")), None)
        self.assertIsNotNone(step, "必须保留产物校验步骤")
        run = step.get("run", "")
        self.assertIn("ci_suite()", run, "校验步骤必须用 ci_suite() 取测试集")
        self.assertNotIn("discover", run,
                         "不得用 unittest discover 全量跑 —— 会带上 TestCrawlerCleanup")
        self.assertNotIn("TestCrawlerCleanup", run)


class TestAiReviewApplyPatches(unittest.TestCase):
    """测试 ai_review.apply_patches 补丁叠加与证据保留"""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.overlay_path = Path(self.temp_dir.name) / "profile_overrides.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_apply_patches_accumulates_vendors(self):
        # 第一次给 vendor_a 打补丁
        patch_a = {
            "changed": True,
            "summary": "更新 vendor_a 免费额度",
            "fields": {"free_quota": "每月 100 万 tokens"},
            "evidence": ["每月 100 万 tokens 免费"],
        }
        ai_review.apply_patches(self.overlay_path, {"vendor_a": patch_a})

        saved_1 = json.loads(self.overlay_path.read_text(encoding="utf-8"))
        self.assertIn("vendor_a", saved_1)
        self.assertEqual(saved_1["vendor_a"]["free_quota"], "每月 100 万 tokens")
        self.assertEqual(saved_1["vendor_a"]["_evidence"], ["每月 100 万 tokens 免费"])

        # 第二次给 vendor_b 打补丁，不能覆盖掉 vendor_a
        patch_b = {
            "changed": True,
            "summary": "更新 vendor_b 免费额度",
            "fields": {"free_quota": "注册赠送 $5"},
            "evidence": ["注册赠送 $5 代金券"],
        }
        ai_review.apply_patches(self.overlay_path, {"vendor_b": patch_b})

        saved_2 = json.loads(self.overlay_path.read_text(encoding="utf-8"))
        self.assertIn("vendor_a", saved_2, "vendor_a 必须被保留，不能丢失")
        self.assertIn("vendor_b", saved_2, "vendor_b 必须被追加")
        self.assertEqual(saved_2["vendor_a"]["free_quota"], "每月 100 万 tokens")
        self.assertEqual(saved_2["vendor_b"]["free_quota"], "注册赠送 $5")

    def test_apply_patches_evidence_cap(self):
        # 测试证据条目最多保留 20 条
        evidences = [f"证据第 {i} 条" for i in range(25)]
        patch = {
            "changed": True,
            "summary": "批量证据",
            "fields": {"free_quota": "test"},
            "evidence": evidences,
        }
        ai_review.apply_patches(self.overlay_path, {"vendor_c": patch})
        saved = json.loads(self.overlay_path.read_text(encoding="utf-8"))
        stored_ev = saved["vendor_c"]["_evidence"]
        self.assertEqual(len(stored_ev), 20)
        self.assertEqual(stored_ev[-1], "证据第 24 条")


class TestAiReviewValidatePatch(unittest.TestCase):
    """测试 ai_review.validate_patch 的防幻觉逐字证据闸门与字段校验"""

    def setUp(self):
        self.corpus = "智谱 AI 开放平台面向新用户赠送 2000 万 tokens 资源包，Flash 全家桶永久 0 元免费。"

    def test_valid_patch_passes(self):
        patch = {
            "changed": True,
            "summary": "更新智谱额度",
            "fields": {"free_quota": "2000 万 tokens 资源包"},
            "evidence": [{"quote": "新用户赠送 2000 万 tokens 资源包", "url": "https://bigmodel.cn"}],
            "guide_meta": {"tiers": ["permanent"], "signup": "email", "scenarios": ["code"]},
        }
        res = ai_review.validate_patch(patch, self.corpus)
        self.assertTrue(res["changed"])
        self.assertEqual(res["summary"], "更新智谱额度")
        self.assertEqual(res["fields"]["free_quota"], "2000 万 tokens 资源包")

    def test_unchanged_patch_returns_unchanged(self):
        res = ai_review.validate_patch({"changed": False}, self.corpus)
        self.assertFalse(res["changed"])

    def test_hallucinated_evidence_rejected(self):
        fake_patch = {
            "changed": True,
            "summary": "虚假免费",
            "fields": {"free_quota": "1 亿 tokens"},
            "evidence": [{"quote": "完全由 AI 捏造不存在于页面的证据句子", "url": "https://fake.com"}],
        }
        with self.assertRaises(ai_review.AiReviewError) as ctx:
            ai_review.validate_patch(fake_patch, self.corpus)
        self.assertIn("逐字定位", str(ctx.exception))

    def test_invalid_field_name_rejected(self):
        invalid_field_patch = {
            "changed": True,
            "summary": "非法字段",
            "fields": {"invalid_random_field": "test"},
            "evidence": [{"quote": "Flash 全家桶永久 0 元免费", "url": "https://bigmodel.cn"}],
        }
        with self.assertRaises(ai_review.AiReviewError) as ctx:
            ai_review.validate_patch(invalid_field_patch, self.corpus)
        self.assertIn("非法字段", str(ctx.exception))


class TestTimestampMasking(unittest.TestCase):
    """测试 _mask_ts 时间戳防抖逻辑"""

    def test_mask_ts_masks_datetime(self):
        text = "> 最近一次巡检：**2026-09-10 13:08:16**；本地手动运行..."
        masked = crawler_llm_intel._mask_ts(text)
        self.assertIn("__TS__", masked)
        self.assertNotIn("2026-09-10 13:08:16", masked)

    def test_mask_ts_equality_when_only_time_differs(self):
        text1 = "> 最近一次巡检：**2026-09-10 10:00:00**；正文相同"
        text2 = "> 最近一次巡检：**2026-09-10 18:30:45**；正文相同"
        self.assertEqual(
            crawler_llm_intel._mask_ts(text1),
            crawler_llm_intel._mask_ts(text2),
            "仅时间戳不同时，屏蔽后应判定为完全一致"
        )


class TestSnapshotState(unittest.TestCase):
    """测试快照状态管理与 AI 失败指数退避"""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_baseline_and_commit(self):
        state = crawler_llm_intel.SnapshotState(self.root)
        self.assertTrue(state.baseline)

        # 模拟厂商与页面
        vendor = crawler_llm_intel.VendorIntel(
            vendor_id="v1", brand="Brand1", homepage="https://example.com", products=[]
        )
        page = crawler_llm_intel.PageResult(
            url="https://example.com/pricing",
            stype="pricing",
            ok=True,
            snapshot_ok=True,
            snapshot_text="Free tier 100k tokens",
        )
        vendor.intel_pages.append(page)

        # baseline 运行时 stage_vendor 不产生 changed
        changed = state.stage_vendor("v1", vendor, ai_enabled=True)
        self.assertEqual(changed, [])

        state.commit_vendor("v1")
        state.save({"v1"}, full_run=True)

        # 第二次载入（非 baseline）
        state2 = crawler_llm_intel.SnapshotState(self.root)
        self.assertFalse(state2.baseline)

        # 文本未变时
        changed2 = state2.stage_vendor("v1", vendor, ai_enabled=True)
        self.assertEqual(changed2, [])

        # 文本变化时
        page_modified = crawler_llm_intel.PageResult(
            url="https://example.com/pricing",
            stype="pricing",
            ok=True,
            snapshot_ok=True,
            snapshot_text="Free tier 500k tokens (updated)",
        )
        vendor.intel_pages = [page_modified]
        changed3 = state2.stage_vendor("v1", vendor, ai_enabled=True)
        self.assertEqual(len(changed3), 1)

    def test_rollback_vendor_exponential_backoff(self):
        state = crawler_llm_intel.SnapshotState(self.root)
        vendor = crawler_llm_intel.VendorIntel(
            vendor_id="v_err", brand="BrandErr", homepage="https://example.com", products=[]
        )
        page = crawler_llm_intel.PageResult(
            url="https://example.com/pricing",
            stype="pricing",
            ok=True,
            snapshot_ok=True,
            snapshot_text="免费额度 100 万 tokens 每月",
        )
        vendor.intel_pages = [page]
        state.stage_vendor("v_err", vendor)
        state.commit_vendor("v_err")
        state.save({"v_err"}, full_run=True)

        # 文本改变（包含事实关键词）
        state2 = crawler_llm_intel.SnapshotState(self.root)
        page_mod = crawler_llm_intel.PageResult(
            url="https://example.com/pricing",
            stype="pricing",
            ok=True,
            snapshot_ok=True,
            snapshot_text="免费额度 500 万 tokens 每月",
        )
        vendor.intel_pages = [page_mod]
        changed = state2.stage_vendor("v_err", vendor, ai_enabled=True)
        self.assertEqual(len(changed), 1)

        # 模拟 AI 失败，触发 rollback_vendor(bump=True)
        state2.rollback_vendor("v_err", bump=True, error="API timeout")
        state2.save({"v_err"}, full_run=True)

        # 检查持久化数据中的 ai_retry_after 和 ai_attempts
        state_file = self.root / crawler_llm_intel.SNAPSHOT_STATE
        data = json.loads(state_file.read_text(encoding="utf-8"))
        key = crawler_llm_intel._snapshot_key("v_err", page)
        entry = data["sources"][key]
        self.assertEqual(entry.get("ai_attempts"), 1)
        self.assertIn("ai_retry_after", entry)
        expected_retry = (date.today() + timedelta(days=1)).isoformat()
        self.assertEqual(entry["ai_retry_after"], expected_retry)

        # 下次巡检在冷却期内应被跳过
        state3 = crawler_llm_intel.SnapshotState(self.root)
        changed_cooldown = state3.stage_vendor("v_err", vendor, ai_enabled=True)
        self.assertEqual(changed_cooldown, [], "处于冷却期内的变化不应触发 AI")
        self.assertIn("v_err", state3.cooldown)


class TestCrawlerCleanup(unittest.TestCase):
    """测试爬虫启动时对旧残留标记的清理"""

    def test_stale_ai_changed_cleaned_up(self):
        root = Path(crawler_llm_intel.__file__).resolve().parent
        stale_marker = root / ".ai-changed"
        stale_marker.write_text("stale: update", encoding="utf-8")
        self.assertTrue(stale_marker.exists())

        # 调用 main 传入不存在的 yaml 触发早期退出，同时验证清理执行
        import io
        from contextlib import redirect_stderr
        try:
            with redirect_stderr(io.StringIO()):
                crawler_llm_intel.main(["--yaml", "non_existent_yaml.yaml"])
        except SystemExit:
            pass
        self.assertFalse(stale_marker.exists(), "爬虫启动时必须清理历史残留的 .ai-changed 标记")


class TestOnlyFlagSafeguard(unittest.TestCase):
    """测试局部运行 --only 时对全局归档文件的保护机制"""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.news_dir = Path(self.temp_dir.name) / "llm-news"
        self.news_dir.mkdir(parents=True)
        # 预建两个厂商归档
        (self.news_dir / "vendor_a.md").write_text("a", encoding="utf-8")
        (self.news_dir / "vendor_b.md").write_text("b", encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_clean_removed_false_preserves_other_archives(self):
        # 模拟 --only 只巡检 vendor_a
        vendor_a = crawler_llm_intel.VendorIntel(
            vendor_id="vendor_a", brand="Vendor A", homepage="https://a.com", products=[]
        )
        crawler_llm_intel.write_news_archives(self.news_dir, [vendor_a], clean_removed=False)
        self.assertTrue((self.news_dir / "vendor_b.md").exists(), "clean_removed=False 时不得删除其他厂商归档")

    def test_clean_removed_true_removes_stale_archives(self):
        # 模拟全量巡检时下线了 vendor_b
        vendor_a = crawler_llm_intel.VendorIntel(
            vendor_id="vendor_a", brand="Vendor A", homepage="https://a.com", products=[]
        )
        vendor_a.all_news_articles = [crawler_llm_intel.Article(title="New A", url="https://a.com/new")]
        crawler_llm_intel.write_news_archives(self.news_dir, [vendor_a], clean_removed=True)
        self.assertFalse((self.news_dir / "vendor_b.md").exists(), "clean_removed=True 时应清理已下线厂商归档")

    def test_archive_incremental_merge_preserves_old_articles(self):
        # 验证历史文章增量合并，旧文章不被冲掉
        arch_path = self.news_dir / "vendor_a.md"
        arch_path.write_text("1. [旧文章标题](https://a.com/old)（2025-01-01）\n", encoding="utf-8")
        vendor_a = crawler_llm_intel.VendorIntel(
            vendor_id="vendor_a", brand="Vendor A", homepage="https://a.com", products=[]
        )
        vendor_a.all_news_articles = [crawler_llm_intel.Article(title="新文章标题", url="https://a.com/new", date="2026-01-01")]
        crawler_llm_intel.write_news_archives(self.news_dir, [vendor_a], clean_removed=False)
        content = arch_path.read_text(encoding="utf-8")
        self.assertIn("https://a.com/old", content, "历史文章 URL 必须保留")
        self.assertIn("https://a.com/new", content, "新抓取文章 URL 必须加入")

    def test_archive_roundtrip_title_with_brackets(self):
        """标题里含方括号的条目必须能读回。

        回归：归档条目正则原本用 `[^\\]]+` 匹配标题，遇到
        "Director of Machine Learning Insights [Part 4]" 会停在第一个 `]` 上导致**整行失配**。
        后果不只是 RSS 少 3 条 —— `write_news_archives` 正是靠这个正则读回旧归档做增量
        合并，读不回来的条目一旦本次没抓到就会从归档里消失，破坏「只增不减」的保证。
        """
        arch_path = self.news_dir / "vendor_a.md"
        line = ("713. [Director of Machine Learning Insights [Part 4]]"
                "(https://a.com/insights-4)（2022-11-23）")
        arch_path.write_text(f"## 全部文章（共 1 篇）\n\n{line}\n", encoding="utf-8")

        arts = crawler_llm_intel.parse_archived_articles(arch_path)
        self.assertEqual(len(arts), 1, "标题含方括号的条目不得被漏掉")
        self.assertEqual(arts[0].title, "Director of Machine Learning Insights [Part 4]")
        self.assertEqual(arts[0].url, "https://a.com/insights-4")
        self.assertEqual(arts[0].date, "2022-11-23")

        vendor_a = crawler_llm_intel.VendorIntel(
            vendor_id="vendor_a", brand="Vendor A", homepage="https://a.com", products=[])
        vendor_a.all_news_articles = [crawler_llm_intel.Article(
            title="新文章", url="https://a.com/new", date="2026-01-01")]
        crawler_llm_intel.write_news_archives(self.news_dir, [vendor_a], clean_removed=False)
        self.assertIn("https://a.com/insights-4", arch_path.read_text(encoding="utf-8"),
                      "读不回旧归档会让历史文章在本次没抓到时被静默丢弃")


class TestNewsSectionCountConsistency(unittest.TestCase):
    """总表「共 N 篇」必须取自**归档合并后**的全量列表，而不是本次抓取结果。

    归档刻意保留页面已不再链接的历史文章（永不丢失），所以合并后的数量常大于本次
    抓取数。main() 里若把 render_news_section 排在 write_news_archives 之前，总表
    就会用合并前的计数，比归档文件少 —— 线上实测 anthropic 52/54、ppio 51/55、
    cohere 28/29、moonshot_kimi 14/15。
    """

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.news_dir = Path(self.temp_dir.name) / "llm-news"
        self.news_dir.mkdir(parents=True)
        # 隔离网络：标题汉化在测试里恒等返回
        self._orig_translate = crawler_llm_intel.translate_to_zh
        crawler_llm_intel.translate_to_zh = lambda text: text

    def tearDown(self):
        crawler_llm_intel.translate_to_zh = self._orig_translate
        self.temp_dir.cleanup()

    @staticmethod
    def _vendor():
        vendor = crawler_llm_intel.VendorIntel(
            vendor_id="cohere", brand="Cohere", homepage="https://cohere.com", products=[]
        )
        vendor.news_pages = [crawler_llm_intel.PageResult(
            url="https://cohere.com/blog", stype="blog", ok=True)]
        # 本次只抓到 1 篇（模拟页面改版后旧文章不再出现在列表里）
        vendor.news_articles = [crawler_llm_intel.Article(
            title="New post", url="https://cohere.com/blog/new", date="2026-09-01")]
        vendor.all_news_articles = list(vendor.news_articles)
        return vendor

    def test_section_count_matches_archive_after_merge(self):
        rows = ["1. [新文章](https://cohere.com/blog/new)（2026-09-01）"]
        for i in range(1, 6):  # 5 篇历史文章，页面已不再链接
            rows.append(f"{i + 1}. [旧文章{i}](https://cohere.com/blog/old-{i})（2025-0{i}-01）")
        (self.news_dir / "cohere.md").write_text("\n".join(rows) + "\n", encoding="utf-8")

        vendor = self._vendor()
        # main() 中的正确顺序：先合并归档（回写 intel.all_news_articles），再渲染总表
        crawler_llm_intel.write_news_archives(self.news_dir, [vendor], clean_removed=True)
        section = crawler_llm_intel.render_news_section([vendor])

        arch = (self.news_dir / "cohere.md").read_text(encoding="utf-8")
        self.assertIn("共 6 篇", arch, "归档应保留 1 篇新抓取 + 5 篇历史")
        self.assertIn("完整文章归档（共 6 篇）", section,
                      "总表计数必须与归档文件一致（先合并归档、再渲染总表）")

    def test_main_merges_archives_before_rendering_section(self):
        """main() 里 write_news_archives 必须排在 render_news_section 之前。

        用 AST 取调用行号，而不是匹配源码文本 —— 文本匹配会因为一次格式化（把调用拆成
        多行）就误报，而那次改动与它要守的顺序毫无关系（实测踩过）。
        """
        tree = ast.parse(Path(crawler_llm_intel.__file__).read_text(encoding="utf-8"))
        main_fn = next(n for n in tree.body
                       if isinstance(n, ast.FunctionDef) and n.name == "main")
        calls = [(n.lineno, n.func.id) for n in ast.walk(main_fn)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
        write_lines = [ln for ln, name in calls if name == "write_news_archives"]
        render_lines = [ln for ln, name in calls if name == "render_news_section"]
        self.assertTrue(write_lines, "main 必须调用 write_news_archives")
        self.assertTrue(render_lines, "main 必须调用 render_news_section")
        self.assertLess(max(write_lines), min(render_lines),
                        "write_news_archives 必须排在 render_news_section 之前，"
                        "否则总表「共 N 篇」会用合并前计数、比归档少")

    def test_committed_news_md_counts_match_archives(self):
        """守卫已提交的产物：总表每个「共 N 篇」都必须等于对应归档文件里的篇数。

        纯文件读取、不联网，因此能作为 CI 里最后一道一致性闸门。
        """
        root = Path(crawler_llm_intel.__file__).resolve().parent
        md = (root / "llm-news-feeds.md").read_text(encoding="utf-8")
        link_re = re.compile(r"完整文章归档（共 (\d+) 篇）：\[([\w\-]+)\.md\]")
        checked = 0
        for md_count, vendor_id in link_re.findall(md):
            arch = root / "llm-news" / f"{vendor_id}.md"
            self.assertTrue(arch.exists(), f"总表链接了不存在的归档 {arch.name}")
            m = re.search(r"共 (\d+) 篇", arch.read_text(encoding="utf-8"))
            self.assertIsNotNone(m, f"{arch.name} 缺少「共 N 篇」标题")
            self.assertEqual(
                int(md_count), int(m.group(1)),
                f"{vendor_id}：总表写「共 {md_count} 篇」，归档实际「共 {m.group(1)} 篇」"
                "（归档合并必须发生在总表渲染之前）")
            checked += 1
        self.assertGreater(checked, 5, "至少应校验到 5 个厂商的归档计数，疑似正则失配")


class TestSelfHostedRss(unittest.TestCase):
    """自建 RSS 订阅源：日期规则、标题清洗、确定性与旧源清理。"""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.out_dir = Path(self.temp_dir.name) / "feeds"
        # 仓库根：浏览页 docs/index.html 与输入 llm-intel.yaml 都在这里（页面守卫测试要用）
        self.repo_root = Path(crawler_llm_intel.__file__).resolve().parent
        # 隔离网络：标题汉化在测试里恒等返回（线上走 .translate_cache.json 缓存）
        self._orig_translate = crawler_llm_intel.translate_to_zh
        crawler_llm_intel.translate_to_zh = lambda text: text

    def tearDown(self):
        crawler_llm_intel.translate_to_zh = self._orig_translate
        self.temp_dir.cleanup()

    @staticmethod
    def _vendor(vendor_id: str, brand: str, articles: list) -> "crawler_llm_intel.VendorIntel":
        intel = crawler_llm_intel.VendorIntel(
            vendor_id=vendor_id, brand=brand, homepage="", products=[])
        intel.all_news_articles = articles
        return intel

    def _read(self, name: str) -> str:
        return (self.out_dir / name).read_text(encoding="utf-8")

    def test_generates_merged_and_per_vendor_feeds(self):
        a = self._vendor("vendor_a", "Vendor A", [
            crawler_llm_intel.Article(title="A 新文章", url="https://a.com/1", date="2026-01-02")])
        b = self._vendor("vendor_b", "Vendor B", [
            crawler_llm_intel.Article(title="B 新文章", url="https://b.com/1", date="2026-03-01")])
        files, items, changed, skipped = crawler_llm_intel.write_rss_feeds(
            self.out_dir, [a, b], base_url="https://example.github.io/repo/feeds")
        # 3 个 feed：合并流 + 2 个单厂商源；4 条条目：合并流 2 条 + 单源各 1 条；
        # changed 多 1 是 vendors.json 厂商索引
        self.assertEqual((files, items, changed, skipped), (3, 4, 4, 0))
        merged = self._read("llm-news-all.xml")
        self.assertIn('<rss version="2.0"', merged)
        self.assertIn('rel="self" type="application/rss+xml"', merged)
        self.assertIn('href="https://example.github.io/repo/feeds/llm-news-all.xml"', merged)
        # 合并流按日期倒序（B 更新），并带厂商前缀与 category 供阅读器过滤
        self.assertLess(merged.index("B 新文章"), merged.index("A 新文章"))
        self.assertIn("[Vendor B] B 新文章", merged)
        self.assertIn("<category>Vendor B</category>", merged)
        # 合并流用 <source url> 自描述「这条来自哪个厂商的单源」，浏览页据此生成订阅链接
        self.assertIn(
            '<source url="https://example.github.io/repo/feeds/llm-news-vendor_b.xml">'
            'Vendor B</source>', merged)
        # 单厂商源不带前缀，也不需要 <source>（它本身就是那个源）
        single = self._read("llm-news-vendor_a.xml")
        self.assertIn("<title>A 新文章</title>", single)
        self.assertNotIn("<source ", single)

    def test_vendors_index_lists_every_vendor_even_without_dates(self):
        """厂商索引必须列出**全部**厂商，包括文章全无日期、因而进不了聚合流的那几家。

        回归：只从聚合流推导厂商清单会漏掉 3/15（google_gemini / meta_llama 全无日期，
        groq 文章都偏旧排不进前 200 条），而它们恰恰是"官方没有原生 RSS"最需要被订到的。
        """
        dated = self._vendor("vendor_a", "Vendor A", [
            crawler_llm_intel.Article(title="有日期", url="https://a.com/1", date="2026-01-01")])
        undated = self._vendor("vendor_b", "Vendor B", [
            crawler_llm_intel.Article(title="无日期", url="https://b.com/1")])
        crawler_llm_intel.write_rss_feeds(
            self.out_dir, [dated, undated], base_url="https://example.github.io/repo/feeds")
        index = json.loads(self._read("vendors.json"))
        ids = [v["id"] for v in index["vendors"]]
        self.assertEqual(ids, ["vendor_a", "vendor_b"], "索引必须覆盖全部厂商且保持顺序")
        self.assertIn("llm-news-vendor_b.xml", index["vendors"][1]["feed"])
        self.assertEqual(index["vendors"][1]["articles"], 1)
        self.assertEqual(index["vendors"][1]["latest"], "", "全无日期时 latest 为空串")
        # 反面对照：无日期厂商确实不在聚合流里 —— 所以索引不是冗余的
        self.assertNotIn("https://b.com/1", self._read("llm-news-all.xml"))

    def test_vendors_index_no_rewrite_when_unchanged(self):
        a = self._vendor("vendor_a", "Vendor A", [
            crawler_llm_intel.Article(title="新文章", url="https://a.com/1", date="2026-01-01")])
        crawler_llm_intel.write_rss_feeds(self.out_dir, [a])
        target = self.out_dir / "vendors.json"
        before = target.stat().st_mtime_ns
        crawler_llm_intel.write_rss_feeds(self.out_dir, [a])
        self.assertEqual(target.stat().st_mtime_ns, before, "内容不变不得重写索引（避免无变化日刷 diff）")

    def test_future_dated_article_excluded_from_all_feeds(self):
        a = self._vendor("vendor_a", "Vendor A", [
            crawler_llm_intel.Article(title="日期写错了", url="https://a.com/f", date="2099-12-10"),
            crawler_llm_intel.Article(title="正常日期", url="https://a.com/n", date="2026-01-01")])
        _, _, _, skipped = crawler_llm_intel.write_rss_feeds(self.out_dir, [a])
        self.assertEqual(skipped, 1, "晚于今天的日期必然来自源页面错误，必须排除")
        self.assertNotIn("https://a.com/f", self._read("llm-news-vendor_a.xml"))
        self.assertNotIn("https://a.com/f", self._read("llm-news-all.xml"))

    def test_undated_article_kept_in_vendor_feed_only(self):
        a = self._vendor("vendor_a", "Vendor A", [
            crawler_llm_intel.Article(title="无日期", url="https://a.com/u"),
            crawler_llm_intel.Article(title="有日期", url="https://a.com/d", date="2026-01-01")])
        crawler_llm_intel.write_rss_feeds(self.out_dir, [a])
        self.assertIn("https://a.com/u", self._read("llm-news-vendor_a.xml"),
                      "无日期是常态，丢掉会让 Google Gemini / Meta Llama 这类整源消失")
        self.assertNotIn("https://a.com/u", self._read("llm-news-all.xml"),
                         "合并流是时间排序的流，无日期条目无法参与排序")

    def test_long_title_truncated_and_full_text_kept_in_description(self):
        long_title = "标题" * 60
        a = self._vendor("vendor_a", "Vendor A", [
            crawler_llm_intel.Article(title=long_title, url="https://a.com/l", date="2026-01-01")])
        crawler_llm_intel.write_rss_feeds(self.out_dir, [a])
        xml = self._read("llm-news-vendor_a.xml")
        self.assertIn("…</title>", xml, "超长标题必须截断，否则会撑爆阅读器列表")
        self.assertIn(f"完整标题：{long_title}", xml, "完整文本不得丢失")

    def test_stale_vendor_feed_removed(self):
        self.out_dir.mkdir(parents=True)
        (self.out_dir / "llm-news-gone.xml").write_text("<rss/>", encoding="utf-8")
        a = self._vendor("vendor_a", "Vendor A", [
            crawler_llm_intel.Article(title="新文章", url="https://a.com/1", date="2026-01-01")])
        crawler_llm_intel.write_rss_feeds(self.out_dir, [a], clean_removed=True)
        self.assertFalse((self.out_dir / "llm-news-gone.xml").exists(), "已下线厂商的旧订阅源必须清理")
        self.assertTrue((self.out_dir / "llm-news-all.xml").exists())

    def test_no_rewrite_when_content_unchanged(self):
        a = self._vendor("vendor_a", "Vendor A", [
            crawler_llm_intel.Article(title="新文章", url="https://a.com/1", date="2026-01-01")])
        crawler_llm_intel.write_rss_feeds(self.out_dir, [a])
        target = self.out_dir / "llm-news-all.xml"
        before = target.stat().st_mtime_ns
        _, _, changed, _ = crawler_llm_intel.write_rss_feeds(self.out_dir, [a])
        self.assertEqual(changed, 0, "内容无变化时不得改写文件（避免无变化日产生 diff）")
        self.assertEqual(target.stat().st_mtime_ns, before)

    def test_browse_page_references_real_artifact_names(self):
        """浏览页 docs/index.html 引用的产物名必须与爬虫真实产出的一致。

        Regression: 页面把 feed 与索引的文件名写死在 JS 常量里（`FEED` / `INDEX`），
        产物一旦改名，页面不会报错、只会永远停在"加载失败"——属于静默失效。
        这里两侧对齐：先真跑一次 write_rss_feeds 拿到真实文件名，再断言页面引用的是同名文件。
        """
        a = self._vendor("vendor_a", "Vendor A", [
            crawler_llm_intel.Article(title="新文章", url="https://a.com/1", date="2026-01-01")])
        crawler_llm_intel.write_rss_feeds(self.out_dir, [a])
        produced = {p.name for p in self.out_dir.iterdir()}
        self.assertIn("llm-news-all.xml", produced, "合并流文件名变了 —— 页面常量也要跟着改")
        self.assertIn("vendors.json", produced, "厂商索引文件名变了 —— 页面常量也要跟着改")

        page = (self.repo_root / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertIn("feeds/llm-news-all.xml", page, "页面必须引用真实的合并流文件名")
        self.assertIn("feeds/vendors.json", page, "页面必须引用真实的厂商索引文件名")

    def test_browse_page_does_not_hardcode_vendors(self):
        """浏览页的厂商清单只能来自 vendors.json，不得硬编码厂商 id。

        硬编码的厂商列表会随厂商增删而漂移（列出已下线的厂商、漏掉新增的），
        而这种漂移不会报任何错。用 llm-intel.yaml 的真实 id 反查页面正文。
        """
        page = (self.repo_root / "docs" / "index.html").read_text(encoding="utf-8")
        yaml_text = (self.repo_root / "llm-intel.yaml").read_text(encoding="utf-8")
        ids = re.findall(r"^\s*-\s*id:\s*([A-Za-z0-9_]+)", yaml_text, re.M)
        self.assertTrue(ids, "没解析到厂商 id —— 解析正则失配，先修测试本身")
        hits = sorted(i for i in ids if i in page)
        self.assertEqual(
            hits, [], f"浏览页硬编码了厂商 id {hits}；厂商清单应取自 feeds/vendors.json")


class TestOpmlAndNewsDocCoverage(unittest.TestCase):
    """OPML 与新闻总文档必须覆盖**自建源**，而不只是厂商官网自带的原生源。

    实测官网有原生 RSS 的只有 3/15，另外 12 家官方页面根本没有 feed —— 而这正是本仓库
    自建订阅源存在的理由。旧版两处产物只提原生源：OPML 只列 3 条，文档对另外 12 家写
    「未发现 RSS/Atom 链接」且只字不提自建源，读者据此会以为这些厂商订不了。
    """

    BASE = "https://example.github.io/repo/feeds"

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.out_dir = Path(self.temp_dir.name)
        self._orig_translate = crawler_llm_intel.translate_to_zh
        crawler_llm_intel.translate_to_zh = lambda text: text

    def tearDown(self):
        crawler_llm_intel.translate_to_zh = self._orig_translate
        self.temp_dir.cleanup()

    @staticmethod
    def _vendor(vendor_id, brand, *, native_feed="", articles=None):
        """native_feed 非空 → 该厂商官网自带 feed（stype=feed 的源页）。"""
        intel = crawler_llm_intel.VendorIntel(
            vendor_id=vendor_id, brand=brand, homepage="", products=[])
        if native_feed:
            intel.news_pages = [crawler_llm_intel.PageResult(
                url=native_feed, stype="feed", ok=True, final_url=native_feed)]
        else:
            intel.news_pages = [crawler_llm_intel.PageResult(
                url=f"https://{vendor_id}.example/blog", stype="blog", ok=True)]
        arts = articles if articles is not None else [
            crawler_llm_intel.Article(title="一篇文章", url=f"https://{vendor_id}.example/1",
                                      date="2026-01-01")]
        intel.news_articles = arts
        intel.all_news_articles = arts
        return intel

    def _intel_list(self):
        return [
            self._vendor("native_a", "Native A", native_feed="https://a.example/rss.xml"),
            self._vendor("selfhost_b", "SelfHost B"),
        ]

    def test_opml_adds_self_hosted_group_for_vendors_without_native_rss(self):
        path = self.out_dir / "llm-news-feeds.opml"
        crawler_llm_intel.write_opml(path, self._intel_list(), self.BASE)
        opml = path.read_text(encoding="utf-8")
        # 自建源必须收录；有原生源的厂商不得重复收录（自建源与其原生源内容重叠）
        self.assertIn(f"{self.BASE}/llm-news-selfhost_b.xml", opml)
        self.assertNotIn(f"{self.BASE}/llm-news-native_a.xml", opml,
                         "有原生源的厂商不该再出自建源条目 —— 会与原生源重复")
        self.assertIn("官方原生源", opml)
        self.assertIn("自建源", opml)
        # 聚合流单独成组，便于读者只勾一个
        self.assertIn(f"{self.BASE}/llm-news-all.xml", opml)

    def test_opml_stays_native_only_without_feeds_base(self):
        """本地运行推不出 Pages 前缀：不能凭空编地址，只能维持原生源清单。"""
        path = self.out_dir / "llm-news-feeds.opml"
        crawler_llm_intel.write_opml(path, self._intel_list(), "")
        opml = path.read_text(encoding="utf-8")
        self.assertIn("https://a.example/rss.xml", opml)
        self.assertNotIn("llm-news-selfhost_b.xml", opml)
        self.assertNotIn("llm-news-all.xml", opml)

    def test_opml_no_rewrite_when_unchanged(self):
        path = self.out_dir / "llm-news-feeds.opml"
        crawler_llm_intel.write_opml(path, self._intel_list(), self.BASE)
        before = path.stat().st_mtime_ns
        crawler_llm_intel.write_opml(path, self._intel_list(), self.BASE)
        self.assertEqual(path.stat().st_mtime_ns, before,
                         "内容不变不得重写（dateCreated 已屏蔽），否则无变化日会刷 diff")

    def test_news_doc_points_to_self_hosted_feed_for_vendors_without_native_rss(self):
        md = crawler_llm_intel.render_news_section(self._intel_list(), self.BASE)
        # 逐厂商那条自建源指引（文首的总述另有「本仓库自建 RSS」，故按整行匹配）
        marker = "- 📡 **本仓库自建源**（官方没有原生 RSS，标题已汉化）："
        self.assertIn(marker, md)
        self.assertIn(f"{self.BASE}/llm-news-selfhost_b.xml", md)
        # 只给缺原生源的那一家标；有原生源的厂商不该出现自建源链接
        self.assertNotIn(f"{self.BASE}/llm-news-native_a.xml", md)
        self.assertEqual(md.count(marker), 1, "有原生源的厂商不得再标自建源")
        # 浏览页入口也要出现在文首，否则读者不知道还能按厂商筛
        self.assertIn("https://example.github.io/repo/", md)

    def test_news_doc_omits_self_hosted_markers_without_feeds_base(self):
        md = crawler_llm_intel.render_news_section(self._intel_list(), "")
        self.assertNotIn("本仓库自建源", md)
        self.assertNotIn("llm-news-all.xml", md)

    def test_feeds_site_base_derives_page_url(self):
        self.assertEqual(crawler_llm_intel._feeds_site_base(self.BASE),
                         "https://example.github.io/repo/")
        self.assertEqual(crawler_llm_intel._feeds_site_base(""), "",
                         "推不出前缀时必须返回空串，不能猜域名")

    def test_self_hosted_annotation_matches_feed_generation(self):
        """标注「本仓库自建源」的判据必须与真正出源的判据一致。

        Regression: 标注只看「有文章」，而出源还要求「有日期不晚于今天的文章」。
        于是当某厂商的文章日期全被源页面误写成未来时，文档/OPML 会给出一个**并不存在**
        的订阅地址（死链），而两边各自看都「对」。
        """
        future = [crawler_llm_intel.Article(title="日期写错了", url="https://c.example/1",
                                           date="2099-01-01")]
        normal = [crawler_llm_intel.Article(title="正常", url="https://d.example/1",
                                           date="2026-01-01")]
        intel = [
            self._vendor("selfhost_b", "SelfHost B", articles=normal),
            self._vendor("all_future_c", "AllFuture C", articles=future),
        ]
        # 真正出源：只有 B 会被写出来
        crawler_llm_intel.write_rss_feeds(self.out_dir, intel, base_url=self.BASE)
        self.assertTrue((self.out_dir / "llm-news-selfhost_b.xml").exists())
        self.assertFalse((self.out_dir / "llm-news-all_future_c.xml").exists(),
                         "整源日期都在未来时不会出源")

        # 文档与 OPML 必须与之一致：不得给 C 标注/列出订阅地址
        md = crawler_llm_intel.render_news_section(intel, self.BASE)
        self.assertNotIn(f"{self.BASE}/llm-news-all_future_c.xml", md,
                         "不得标注不存在的订阅源（死链）")
        self.assertIn(f"{self.BASE}/llm-news-selfhost_b.xml", md)
        opml_path = self.out_dir / "llm-news-feeds.opml"
        crawler_llm_intel.write_opml(opml_path, intel, self.BASE)
        opml = opml_path.read_text(encoding="utf-8")
        self.assertNotIn("llm-news-all_future_c.xml", opml, "OPML 不得列出不存在的源")
        self.assertIn("llm-news-selfhost_b.xml", opml)

    def test_opml_and_news_doc_use_the_actual_merged_limit(self):
        """条目文案里的「最近 N 条」必须跟着实际上限走。

        Regression: 文案写死了常量，而 `--rss-limit` 可以覆盖它 —— 于是用
        `--rss-limit 500` 跑出来的清单会写着「最近 200 条」。
        """
        intel = self._intel_list()
        opml_path = self.out_dir / "llm-news-feeds.opml"
        crawler_llm_intel.write_opml(opml_path, intel, self.BASE, merged_limit=7)
        self.assertIn("最近 7 条", opml_path.read_text(encoding="utf-8"))
        md = crawler_llm_intel.render_news_section(intel, self.BASE, merged_limit=7)
        self.assertIn("最近 7 条", md)


class TestDateIntegrity(unittest.TestCase):
    """日期正确性：归档按 URL 增量合并、不会自我纠正，错误日期一旦写入就永久留存。

    真实案例：cohere 一篇 2026-07-10 的文章，博客卡片上印的是 "Dec 10, 2026"，
    于是它被当成未来日期、长期钉在归档与 README 第一条，并被 RSS 排除。
    """

    def setUp(self):
        self._quiet = contextlib.redirect_stderr(io.StringIO())
        self._quiet.__enter__()

    def tearDown(self):
        self._quiet.__exit__(None, None, None)

    def test_drop_future_date(self):
        self.assertEqual(crawler_llm_intel._drop_future_date("2099-12-10"), "")
        self.assertEqual(crawler_llm_intel._drop_future_date(""), "")
        today = date.today().strftime("%Y-%m-%d")
        self.assertEqual(crawler_llm_intel._drop_future_date(today), today,
                         "今天不算未来日期")
        self.assertEqual(crawler_llm_intel._drop_future_date("2020-01-01"), "2020-01-01")

    def test_archive_read_drops_future_date(self):
        """老归档里的未来日期必须在读取时就地丢弃，否则会被合并逻辑一路带下去。"""
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "vendor_a.md"
            p.write_text("1. [未来日期文章](https://a.com/f)（2099-12-10）\n"
                         "2. [正常文章](https://a.com/n)（2026-01-01）\n", encoding="utf-8")
            arts = crawler_llm_intel.parse_archived_articles(p)
            self.assertEqual(arts[0].date, "")
            self.assertEqual(arts[1].date, "2026-01-01")

    def test_page_extraction_backfills_date_from_duplicate_card(self):
        """同一 URL 在一页里出现两次时，用后来卡片上的日期补全先出现的那条。

        Regression: 只按 URL 去重会让先出现的首屏 hero 卡片（无日期）胜出，
        把下方列表卡片上本可拿到的日期丢掉 —— 实测 cohere 博客页有 2 条因此退化成无日期。
        """
        page = crawler_llm_intel.PageResult(
            url="https://a.com/blog", stype="blog", ok=True,
            links=[
                ("https://a.com/blog/hero-post", "Hero post title here"),
                ("https://a.com/blog/hero-post",
                 "Hero post title here Sep 13, 2026 15 min read"),
            ])
        arts = crawler_llm_intel.extract_articles_from_page(page, max_items=10)
        self.assertEqual(len(arts), 1, "同一 URL 只保留一条")
        self.assertEqual(arts[0].title, "Hero post title here", "标题保留先出现的（更干净）")
        self.assertEqual(arts[0].date, "2026-09-13", "日期必须从后来的卡片补上")

    def test_archive_merge_keeps_existing_date(self):
        """本次抓取没拿到日期时，必须沿用归档里已有的日期，不能把它抹掉。"""
        with tempfile.TemporaryDirectory() as d:
            news_dir = Path(d) / "llm-news"
            news_dir.mkdir(parents=True)
            arch = news_dir / "vendor_a.md"
            arch.write_text("1. [老文章](https://a.com/x)（2026-05-01）\n", encoding="utf-8")
            intel = crawler_llm_intel.VendorIntel(
                vendor_id="vendor_a", brand="Vendor A", homepage="", products=[])
            intel.all_news_articles = [crawler_llm_intel.Article(
                title="老文章", url="https://a.com/x")]  # 本次页面没给出日期
            crawler_llm_intel.write_news_archives(news_dir, [intel], clean_removed=False)
            self.assertIn("（2026-05-01）", arch.read_text(encoding="utf-8"),
                          "本次无日期时不得抹掉归档里已有的日期")


class TestFeedsBaseDerivation(unittest.TestCase):
    """订阅源对外前缀按 Actions 注入的 GITHUB_REPOSITORY 推导，fork 后无需改代码。"""

    def setUp(self):
        self._orig = os.environ.get("GITHUB_REPOSITORY")

    def tearDown(self):
        if self._orig is None:
            os.environ.pop("GITHUB_REPOSITORY", None)
        else:
            os.environ["GITHUB_REPOSITORY"] = self._orig

    def test_project_page_and_user_page(self):
        os.environ["GITHUB_REPOSITORY"] = "someone/free-llm-intel"
        self.assertEqual(crawler_llm_intel.default_feeds_base(),
                         "https://someone.github.io/free-llm-intel/feeds")
        os.environ["GITHUB_REPOSITORY"] = "someone/someone.github.io"
        self.assertEqual(crawler_llm_intel.default_feeds_base(),
                         "https://someone.github.io/feeds")

    def test_local_run_without_env_yields_empty_base(self):
        os.environ.pop("GITHUB_REPOSITORY", None)
        self.assertEqual(crawler_llm_intel.default_feeds_base(), "",
                         "本地运行时省略 rel=self 即可，不得猜一个域名出来")


class TestReadmeIntegrity(unittest.TestCase):
    """测试 README.md 完整性与本地链接有效性"""

    def setUp(self):
        self.root = Path(__file__).resolve().parent
        self.readme_path = self.root / "README.md"

    def test_readme_blocks_exist(self):
        self.assertTrue(self.readme_path.exists(), "README.md 必须存在")
        content = self.readme_path.read_text(encoding="utf-8")
        self.assertIn("<!-- LLM-GUIDE:BEGIN", content)
        self.assertIn("<!-- LLM-GUIDE:END -->", content)
        self.assertIn("<!-- LLM-INTEL:BEGIN", content)
        self.assertIn("<!-- LLM-INTEL:END -->", content)

    def test_readme_local_links_valid(self):
        import re
        content = self.readme_path.read_text(encoding="utf-8")
        links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
        for text, target in links:
            if target.startswith("http") or target.startswith("#"):
                continue
            clean_path = target.split("#")[0].strip("`")
            target_path = self.root / clean_path
            self.assertTrue(
                target_path.exists(),
                f"README.md 中的本地文件链接失效: [{text}]({target}) -> {target_path}"
            )

    def test_readme_internal_anchors_valid(self):
        import re
        import urllib.parse
        content = self.readme_path.read_text(encoding="utf-8")

        # 收集 HTML 显式 id/name 锚点
        explicit_ids = set(re.findall(r'id=["\']([^"\']+)["\']', content))
        explicit_ids |= set(re.findall(r'name=["\']([^"\']+)["\']', content))

        # 收集 Markdown 标题对应的 GitHub 风格 slug
        headings = re.findall(r"^(#{1,6})\s+(.+)$", content, re.MULTILINE)
        heading_slugs = {crawler_llm_intel._gh_slug(h[1]) for h in headings}
        valid_targets = explicit_ids | heading_slugs

        links = re.findall(r"\[([^\]]+)\]\(#([^)]+)\)", content)
        self.assertGreater(len(links), 50, "README 中应包含大量内部锚点跳转链接")
        for text, anchor in links:
            decoded = urllib.parse.unquote(anchor)
            self.assertIn(
                decoded,
                valid_targets,
                f"README.md 中存在失效的内部锚点跳转: [{text}](#{anchor}) 未找到对应标题或 id 锚点"
            )

    def test_yaml_and_profiles_vendor_sync(self):
        yaml_path = self.root / "llm-intel.yaml"
        self.assertTrue(yaml_path.exists(), "llm-intel.yaml 必须存在")
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        yaml_vendors = {v["id"] for v in data.get("vendors", [])}
        profile_vendors = set(provider_profiles.PROVIDER_PROFILES.keys())

        missing_in_profiles = yaml_vendors - profile_vendors
        missing_in_yaml = profile_vendors - yaml_vendors
        self.assertEqual(
            missing_in_profiles,
            set(),
            f"YAML 中存在但在 provider_profiles.py 中缺失的厂商: {missing_in_profiles}"
        )
        self.assertEqual(
            missing_in_yaml,
            set(),
            f"provider_profiles.py 中存在但在 YAML 中缺失的厂商: {missing_in_yaml}"
        )
        self.assertEqual(len(yaml_vendors), 62, "应覆盖正好 62 家厂商")


class TestGuideRendering(unittest.TestCase):
    """白嫖攻略：过期促销自动过滤、懒人首选块渲染。"""

    def test_guide_meta_keys_are_real_vendors(self):
        """GUIDE_META 的 key 必须是真实厂商 id。

        攻略是按 GUIDE_META 过滤渲染的：key 打错（拼写 / 厂商改名后没跟着改）**不会报错**，
        只是那家厂商从攻略里静默消失 —— 而攻略自称「与下方厂商总表同源」。
        2026-09-18 就是靠人工比对才发现 4 家「有免费能力却不在攻略里」。
        """
        root = Path(__file__).resolve().parent
        vendors, _sources = crawler_llm_intel.parse_yaml(root / "llm-intel.yaml")
        ids = {v["id"] for v in vendors}
        self.assertTrue(ids, "没解析到厂商 id —— 解析失配，先修测试本身")
        unknown = sorted(set(provider_profiles.GUIDE_META) - ids)
        self.assertEqual(unknown, [],
                         f"GUIDE_META 里有不属于任何厂商的 key（写错了？）: {unknown}")
        self.assertEqual(sorted(set(provider_profiles.GUIDE_META) - set(provider_profiles.PROVIDER_PROFILES)), [],
                         "GUIDE_META 的 key 必须在 PROVIDER_PROFILES 里有对应档案")

    def test_promo_fragment_expired(self):
        f = crawler_llm_intel._promo_fragment_expired
        today = date(2026, 9, 12)
        # 写明截止/结束日期且已过 -> 过期剔除
        self.assertTrue(f("GLM-5.3-Flash 限时五折活动（官方标注截止 2026-09-09 24:00）", today))
        self.assertTrue(f("“邀请奖励”活动已于 2025-11-30 结束", today))
        # 日期在未来 -> 保留
        self.assertFalse(f("限时活动截止 2026-12-31，先到先得", today))
        # 无明确日期（限量/未公布截止日）-> 保留，交人工复核
        self.assertFalse(f("免费试用 30 天，每日限量 100 名", today))
        self.assertFalse(f("代码模型限时免费（官方未公布截止日）", today))

    def test_guide_section_picks_and_expiry(self):
        import re
        records = build_records()
        text = "\n".join(crawler_llm_intel.render_guide_section(records))

        self.assertIn("### 0. 懒人首选", text)
        picks_block = text.split("### 1.")[0]
        pick_ids = [vid for vid, meta in provider_profiles.GUIDE_META.items() if meta.get("pick")]
        self.assertEqual(
            len(re.findall(r"^\d+\. \[", picks_block, re.M)), len(pick_ids),
            f"懒人首选数量应与 GUIDE_META 中带 pick 的厂商一致（应为 {len(pick_ids)} 家）")
        for vid in ("zhipu_glm", "siliconflow", "google_gemini"):
            pick = provider_profiles.get_guide_meta(vid)["pick"]
            self.assertIn(pick[:14], text, f"{vid} 的首选推荐语应出现在攻略中")
        # 实名不算门槛：首选清单不得再用「需手机号+实名」给平台贴摩擦标签
        self.assertNotIn("需手机号+实名", text)
        # 四家分级（实名/邮箱同属无条件），不再有「需实名」独立等级
        self.assertIn("先认清四类", text)
        self.assertNotIn("先认清五类", text)
        # 已过期的限时五折不得出现在任何攻略片段中
        self.assertNotIn("限时五折", text)

    def test_tier_rows_value_ordered_not_realname_segmented(self):
        """实名不算门槛：国内永久层进 A，国内一次性进 B；只有绑卡才单列 C。"""
        records = build_records()
        text = "\n".join(crawler_llm_intel.render_guide_section(records))
        rows = {ln.split("|")[1].strip().strip("*"): ln for ln in text.splitlines()
                if ln.startswith("| **")}

        def in_row(label, vid):
            prof = provider_profiles.get_provider_profile(vid)
            dname = prof["display_name"]
            head = dname.split(" (")[0].split("(")[0]
            return head in rows[label]

        # A. 无条件长期：国内永久层（智谱、商汤、硅基流动）与海外免卡永久层并列
        for vid in ("zhipu_glm", "sensetime_sensenova", "siliconflow",
                    "google_gemini", "groq", "openrouter"):
            self.assertTrue(in_row("A. 无条件 · 长期可用", vid), f"{vid} 应在 A 类")
        # B. 无条件限时：国内实名的一次性赠送（阿里、Kimi）与海外免卡一次性并列
        for vid in ("aliyun_qwen", "moonshot_kimi", "inception_labs"):
            self.assertTrue(in_row("B. 无条件 · 一次性限时", vid), f"{vid} 应在 B 类")
        # C 只装绑卡平台；国内实名平台一律不得进 C
        for vid in ("zhipu_glm", "aliyun_qwen", "siliconflow", "moonshot_kimi"):
            self.assertFalse(in_row("C. 需绑卡 · 大额云试用金", vid), f"{vid} 不应因实名进绑卡类")
        for vid in ("cerebras", "aws_bedrock", "azure_openai"):
            self.assertTrue(in_row("C. 需绑卡 · 大额云试用金", vid), f"{vid} 应在 C 类")
        # Inference.net 免费档实为观测额度（tiers 为空），不出现在任何分级里
        for label in ("A. 无条件 · 长期可用", "B. 无条件 · 一次性限时",
                      "C. 需绑卡 · 大额云试用金"):
            self.assertNotIn("Inference.net", rows[label])


class TestTierCaveats(unittest.TestCase):
    """A 类（无条件长期免费）厂商必须写清免费层的真实边界。

    「全家桶永久免费」式的笼统说法会盖住版本代差、限速与商用限制，
    强制每家提供 tier_caveats 才能进永久/周期层。
    """

    def test_all_permanent_vendors_have_caveats(self):
        # A 类（长期）与 B 类（一次性限时）都属「无条件免费」，限制必须写清
        missing, empty = [], []
        for vid, meta in provider_profiles.GUIDE_META.items():
            tiers = set(meta.get("tiers") or [])
            if not tiers or meta.get("signup") == "card":
                continue
            if not ({"permanent", "recurring", "onetime"} & tiers):
                continue
            prof = provider_profiles.PROVIDER_PROFILES.get(vid, {})
            caveats = prof.get("tier_caveats")
            if caveats is None:
                missing.append(vid)
            elif not isinstance(caveats, list) or not all(
                    isinstance(x, str) and x.strip() for x in caveats):
                empty.append(vid)
        self.assertEqual(missing, [],
                         f"无条件免费（A/B 类）厂商缺少 tier_caveats（免费额度限制未写清）: {missing}")
        self.assertEqual(empty, [],
                         f"tier_caveats 必须是非空字符串列表: {empty}")

    def test_caveats_render_as_table_row(self):
        intel = crawler_llm_intel.VendorIntel(
            vendor_id="zhipu_glm", brand="智谱", homepage="", products=[])
        prof = provider_profiles.get_provider_profile("zhipu_glm")
        table = "\n".join(provider_profiles.render_freellm_table(intel, prof, 1))
        self.assertIn("免费层限制 / 注意事项", table)
        # 关键限制必须出现在渲染产物里：版本代差
        self.assertIn("5.x", table)


class TestTextSanitization(unittest.TestCase):
    """控制字符清洗：抓到的 \x00 不得进入 Markdown 产物（会让 git/grep 判为二进制）。"""

    def setUp(self):
        self.readme_path = Path(__file__).resolve().parent / "README.md"

    def test_sanitize_text_strips_control_chars(self):
        s = crawler_llm_intel.sanitize_text
        self.assertEqual(s("请参考\x00限速与隔离。"), "请参考限速与隔离。")
        self.assertEqual(s("\x00\x08\x0b\x0c\x0e\x7f"), "")
        # \t \n \r 必须保留（块级换行与制表符是文本结构的一部分）
        self.assertEqual(s("a\tb\nc\rd"), "a\tb\nc\rd")
        self.assertEqual(s(""), "")
        self.assertEqual(s(None), "")

    def test_article_construction_sanitizes_all_fields(self):
        a = crawler_llm_intel.Article(title="标题\x00", url="https://x.io/a\x00",
                                      date="2026-09-13", source="RSS\x7f")
        self.assertEqual(a.title, "标题")
        self.assertEqual(a.url, "https://x.io/a")
        self.assertEqual(a.source, "RSS")

    def test_readme_is_pure_text(self):
        """生成的 README 不得含任何控制字符——曾有一次巡检把 \x00 写进 DeepSeek 档案。"""
        content = self.readme_path.read_text(encoding="utf-8")
        bad = {hex(ord(ch)) for ch in content
               if ord(ch) < 0x20 and ch not in "\t\n\r"}
        self.assertEqual(bad, set(), f"README.md 含控制字符: {sorted(bad)}")


class TestEvidenceKeyContract(unittest.TestCase):
    """巡检证据分组键契约：展示顺序里的键必须真实存在于 KEYWORD_GROUPS。

    历史 bug：render_freellm_table 曾读取 trial_bonus / monthly_sub / promotions /
    constraints 四个不存在的分组名，导致免费额度表只剩 free_tier 一类证据。
    """

    def test_display_order_keys_exist_in_keyword_groups(self):
        group_keys = {key for key, _label, _kw in crawler_llm_intel.KEYWORD_GROUPS}
        missing = [k for k in provider_profiles.EVIDENCE_DISPLAY_ORDER
                   if k not in group_keys]
        self.assertEqual(missing, [], f"证据展示键在 KEYWORD_GROUPS 中不存在: {missing}")

    def test_render_reads_evidence_keys_via_order_constant(self):
        """证据分组只能经 EVIDENCE_DISPLAY_ORDER 读取，禁止再硬编码分组名列表。"""
        src = Path(provider_profiles.__file__).read_text(encoding="utf-8")
        self.assertIn("for key in EVIDENCE_DISPLAY_ORDER:", src)
        # 旧写法是 for key in ["free_tier", "trial_bonus", ...] 这样的字面量列表
        self.assertNotIn('for key in [', src)


class TestEndpointTable(unittest.TestCase):
    """一键接入速查表：表体由 provider_profiles.openai_compat 驱动，不再硬编码。"""

    def test_endpoint_table_rows_match_profiles(self):
        records = build_records()
        text = "\n".join(crawler_llm_intel.render_guide_section(records))

        self.assertIn("| 平台名称 | 免费额度简述 |", text)
        table = text.split("| 平台名称 | 免费额度简述 |")[1].split("\n## ")[0]
        rows = [ln for ln in table.splitlines() if ln.startswith("| **")]

        expected = []
        for _idx, _intel, prof in records:
            oc = prof.get("openai_compat")
            if isinstance(oc, dict) and oc.get("base_url"):
                expected.append(oc["base_url"])
        self.assertGreaterEqual(len(expected), 9, "应有至少 9 家 OpenAI 兼容厂商")
        self.assertEqual(len(rows), len(expected),
                         "表体行数必须等于带 openai_compat.base_url 的厂商数")

        # 每个 base_url 都必须在表里出现，且不得在渲染代码里硬编码
        for base in expected:
            self.assertIn(base, table, f"{base} 未出现在一键接入表")
        crawler_src = Path(crawler_llm_intel.__file__).read_text(encoding="utf-8")
        self.assertNotIn("open.bigmodel.cn/api/paas/v4 |", crawler_src,
                         "端点表不应在 crawler 里硬编码厂商行")

    def test_endpoint_field_shape(self):
        """openai_compat 字段必须齐全：缺字段会渲染出空链接。"""
        required = {"base_url", "api_key_url", "models"}
        bad = []
        for _idx, _intel, prof in build_records():
            oc = prof.get("openai_compat")
            if not isinstance(oc, dict):
                continue
            miss = required - set(oc)
            if miss:
                bad.append(f"{prof.get('display_name')} 缺 {sorted(miss)}")
        self.assertEqual(bad, [], f"openai_compat 字段不完整: {bad}")


def _gemini_resp(status, message="", details=None):
    """构造 Gemini generateContent 的假响应：200 带候选文本，其余带 error 体。"""
    if status == 200:
        payload = {"candidates": [{"content": {"parts": [{"text": "{}"}]},
                                   "finishReason": "STOP"}]}
    else:
        payload = {"error": {"code": status, "message": message,
                             "details": details or []}}
    # 429/5xx 附带 Retry-After，保证退避等待被封顶在 1s（配合 setUp 里的 sleep 打桩）
    headers = {} if status == 200 else {"retry-after": "1"}
    return types.SimpleNamespace(status_code=status, text=json.dumps(payload),
                                 json=lambda: payload, headers=headers)


class TestGeminiFallbackChain(unittest.TestCase):
    """ai_review 免费层备选链：模型可用性、限流分流、故障判定与墙钟预算"""

    def setUp(self):
        self.orig_sleep = ai_review.time.sleep
        self.orig_fallback = ai_review.GEMINI_FALLBACK_MODELS
        ai_review.time.sleep = lambda seconds: None
        self.requests = []      # 实际请求到的模型（按序）
        self.script = []        # 预置响应序列，用尽后默认返回 200

    def tearDown(self):
        ai_review.time.sleep = self.orig_sleep
        ai_review.GEMINI_FALLBACK_MODELS = self.orig_fallback

    def _fake_post(self, url, headers=None, json=None, timeout=None):
        self.requests.append(url.rsplit("/", 1)[1].replace(":generateContent", ""))
        if self.script:
            status, message = self.script.pop(0)
            return _gemini_resp(status, message)
        return _gemini_resp(200)

    def _run(self, fallback=None, preferred=""):
        """跑一次 call_llm_gemini；fallback 用于把备选链收窄以聚焦断言。"""
        if fallback is not None:
            ai_review.GEMINI_FALLBACK_MODELS = list(fallback)
        patcher = mock.patch.object(ai_review.requests, "post", self._fake_post)
        patcher.start()
        self.addCleanup(patcher.stop)
        return ai_review.call_llm_gemini("prompt", api_key="test-key", model=preferred)

    # -- 备选链结构 -------------------------------------------------------

    def test_fallback_chain_is_stable_free_tier_models_only(self):
        """不纳入 preview 模型；完整 Flash 系在前按新到旧，Lite 系垫底。"""
        chain = ai_review.gemini_candidate_models("")
        self.assertEqual(chain[0], ai_review.GEMINI_DEFAULT_MODEL)
        for m in chain:
            self.assertNotIn("preview", m, "preview 模型仅约两周弃用通知，不适合长期兜底")
            self.assertTrue(m.startswith("gemini-"), m)

        full = [m for m in chain if not m.endswith("-lite")]
        lite = [m for m in chain if m.endswith("-lite")]
        self.assertGreater(len(lite), 0, "备选链应包含 Lite 模型作为最后兜底")
        self.assertLess(max(chain.index(m) for m in full),
                        min(chain.index(m) for m in lite),
                        "完整 Flash 系应排在 Lite 系之前")

        def version(m):
            num = m[len("gemini-"):].split("-")[0]
            return tuple(int(x) for x in num.split("."))

        self.assertEqual(full, sorted(full, key=version, reverse=True),
                         "完整 Flash 系应按版本新到旧排列")
        self.assertEqual(lite, sorted(lite, key=version, reverse=True),
                         "Lite 系应按版本新到旧排列")

    def test_candidate_models_pins_preferred_first_and_dedups(self):
        self.assertEqual(ai_review.gemini_candidate_models(""),
                         [ai_review.GEMINI_DEFAULT_MODEL,
                          *ai_review.GEMINI_FALLBACK_MODELS])
        cands = ai_review.gemini_candidate_models("gemini-3.6-flash")
        self.assertEqual(cands[0], "gemini-3.6-flash", "AI_REVIEW_MODEL 应钉死首选")
        self.assertEqual(len(cands), len(set(cands)), "备选链不应重复请求同一模型")

    def test_fallback_chain_documented_in_readme_and_contributing(self):
        """备选链改动必须同步 README / CONTRIBUTING，防止文档与代码漂移。"""
        root = Path(__file__).resolve().parent
        chain = ai_review.gemini_candidate_models("")
        for name in ("README.md", "CONTRIBUTING.md"):
            text = (root / name).read_text(encoding="utf-8")
            for m in chain:
                self.assertIn(m, text, f"{name} 未列出备选模型 {m}")

    # -- 限流分流 ---------------------------------------------------------

    def test_sustained_rpm_limit_falls_through_to_next_model(self):
        """RPM/TPM 按模型独立计量：退避不缓解应换模型，而不是放弃整批。"""
        self.script = [(429, "Too many requests per minute")] * (
            ai_review.MAX_RATE_RETRIES + 1) + [(200, "")]
        out = self._run(fallback=["gemini-2.5-flash"])
        self.assertEqual(json.loads(out), {})
        self.assertEqual(self.requests[0], ai_review.GEMINI_DEFAULT_MODEL)
        self.assertEqual(self.requests[-1], "gemini-2.5-flash")
        self.assertEqual(len(self.requests), ai_review.MAX_RATE_RETRIES + 2,
                         "首选退避耗尽后应切到备选，而非直接终止")

    def test_daily_rpd_limit_aborts_without_fallback(self):
        """RPD 按项目共享：换模型无意义，必须立即终止且不消耗其他模型调用。"""
        self.script = [(429, "Resource has been exhausted (quota) per day for requests.")]
        with self.assertRaises(ai_review.AiQuotaExhausted):
            self._run(fallback=["gemini-2.5-flash"])
        self.assertEqual(self.requests, [ai_review.GEMINI_DEFAULT_MODEL])

    def test_all_models_rate_limited_is_reported_as_quota(self):
        """备选链全部限流 → 按额度耗尽整批终止（不是笼统的模型不可用）。"""
        self.script = [(429, "Too many requests per minute")] * 20
        with self.assertRaises(ai_review.AiQuotaExhausted):
            self._run(fallback=["gemini-3.7-flash", "gemini-2.5-flash-lite"])
        self.assertEqual(len(self.requests),
                         (ai_review.MAX_RATE_RETRIES + 1) * 3,
                         "3 个候选 × 每个退避耗尽")

    def test_model_missing_falls_through_but_config_error_is_fatal(self):
        self.script = [(404, "models/gemini-3.8-flash was not found or not valid"),
                       (401, "API key not valid. Please pass a valid API key.")]
        with self.assertRaises(ai_review.AiReviewError) as ctx:
            self._run(fallback=["gemini-2.5-flash"])
        self.assertEqual(self.requests, [ai_review.GEMINI_DEFAULT_MODEL, "gemini-2.5-flash"])
        self.assertIn("401", str(ctx.exception), "401 应立即报错，不应继续换模型")

    # -- 故障判定与预算 ---------------------------------------------------

    def test_two_consecutive_5xx_is_reported_as_outage(self):
        """连续两个模型都 5xx：疑似 Google 侧整体故障，换厂商也会失败。"""
        self.script = [(503, "upstream unavailable")] * 6
        with self.assertRaises(ai_review.AiServiceOutage):
            self._run(fallback=["gemini-3.7-flash", "gemini-2.5-flash"])
        self.assertEqual(len(self.requests), ai_review.MAX_TRANSIENT_RETRIES + 2)

    def test_wall_clock_budget_stops_a_slow_review(self):
        """备选链变长后，超时重试叠加不能拖垮整轮巡检。"""
        ai_review.MAX_REVIEW_WALL_SECONDS = 30
        orig_monotonic = ai_review.time.monotonic
        ticks = iter([1000, 1200, 5000])
        ai_review.time.monotonic = lambda: next(ticks)
        self.addCleanup(setattr, ai_review.time, "monotonic", orig_monotonic)
        with self.assertRaises(ai_review.AiReviewError) as ctx:
            self._run(fallback=["gemini-2.5-flash"])
        self.assertIn("墙钟预算", str(ctx.exception))
        self.assertEqual(self.requests, [], "超预算不应发出任何请求")


class TestEvidenceQualityGuards(unittest.TestCase):
    """证据提取的反污染：链接发现排除营销页，事实行过滤样板 / 示例提示词文本"""

    def test_discovery_blocks_singular_case_study_path(self):
        # 回归：HARD_BAD_PATH 曾写作 case-studies?，只匹配复数，
        # /resources/case-study/<slug>（含 cost 字样）漏网后营销文案被当成证据
        bad = [
            "https://www.anyscale.com/resources/case-study/slug-with-cost",
            "https://example.com/case-studies/a",
            "https://example.com/events/ai-night",
            "https://example.com/whitepaper/gpu",
            "https://example.com/careers/engineer",
        ]
        good = [
            "https://example.com/pricing",
            "https://example.com/free-tier",
            "https://docs.example.com/billing/pricing",
        ]
        for url in bad:
            self.assertEqual(crawler_llm_intel.score_links(
                [(url, "x")], "https://example.com/"), [], url)
        scored = {u for _, u, _ in crawler_llm_intel.score_links(
            list((u, "x") for u in good), "https://example.com/")}
        self.assertEqual(scored, set(good))

    def test_fact_line_rejects_boilerplate_and_demo_prompts(self):
        reject = [
            "-上下文：我想推广公司的新产品。我的公司名为：智谱，"
            "新产品名为：ChatGLM 大模型，是一款面向大众的 AI 产品。",
            "此 cookie 对于在网站上进行信用卡交易是必需的。该服务由 Stripe.com 提供。",
            "你是一个专业的文案助手，请帮我写一段推广语。",
        ]
        accept = [
            "开始使用 25 个免费积分。在您的帐户页面上检查您的积分余额并购买额外的积分。",
            "免费套餐的运行有速率限制，大多数型号每分钟最多 40 个请求 (RPM)。",
            "停止新用户注册及充值服务，保留账号登录、账单查询和调用明细查询。",
            "邀请好友注册认证，狂得 2 亿最新模型 Tokens！",
        ]
        for line in reject:
            self.assertFalse(crawler_llm_intel._is_fact_line(line), line[:30])
        for line in accept:
            self.assertTrue(crawler_llm_intel._is_fact_line(line), line[:30])


# CI 里必须排除的测试类。只有「会破坏 CI 自身状态」的类才配进这个白名单：
# `TestCrawlerCleanup` 会删除仓库根目录的 `.ai-changed`，而它正是 workflow
# 「Decide commit path」判定走 PR 还是直提的判据 —— 在 CI 里跑会把 PR 路由踩坏。
# 其余用例都不碰仓库文件（实测：跑完标记存活、`git status` 干净），因此 CI 用
# 「全部用例 − 本白名单」的方式取测试集，而不是手写一份要维护的类清单。
CI_EXCLUDED_CLASSES = ("TestCrawlerCleanup",)


def ci_suite() -> unittest.TestSuite:
    """CI 用测试集 = 全部用例 − `CI_EXCLUDED_CLASSES`。

    刻意**从全量推导**而不是写死类名：以后新增测试类会自动进 CI，不需要谁记得回来
    改 workflow —— 手写清单的下一步就是漂移（新加的守卫静默地不在 CI 里跑，
    而这正是本函数要防的那类问题）。
    """
    def walk(suite):
        out = unittest.TestSuite()
        for item in suite:
            if isinstance(item, unittest.TestSuite):
                out.addTest(walk(item))
            elif type(item).__name__ not in CI_EXCLUDED_CLASSES:
                out.addTest(item)
        return out

    return walk(unittest.TestLoader().loadTestsFromName(__name__))


class TestCiSuite(unittest.TestCase):
    """`ci_suite()` 的取集规则：全部用例减去会破坏 CI 自身状态的那一类。

    取集若失配，后果是**静默**的 —— 少跑一批守卫不会有任何提示，直到某天回归
    溜到提交之后才被发现。所以规则本身也要有守卫。
    """

    @staticmethod
    def _ids(suite) -> list[str]:
        out: list[str] = []
        for item in suite:
            if isinstance(item, unittest.TestSuite):
                out.extend(TestCiSuite._ids(item))
            else:
                out.append(item.id())
        return out

    def test_excludes_only_repo_mutating_cleanup_class(self):
        ids = self._ids(ci_suite())
        self.assertTrue(ids, "ci_suite 不能为空 —— 取集失配会让 CI 静默跳过全部测试")
        self.assertEqual([i for i in ids if "TestCrawlerCleanup" in i], [],
                         "TestCrawlerCleanup 会删掉 .ai-changed，绝不能进 CI")
        # 覆盖面：除白名单外的每个测试类都必须被取到。
        # 用 globals() 而非 `import 本模块` —— 本模块没有（也不该有）自引用。
        defined = {
            name for name, obj in globals().items()
            if isinstance(obj, type) and issubclass(obj, unittest.TestCase)
            and obj is not unittest.TestCase
            and obj.__module__ == __name__
        }
        self.assertTrue(defined, "没解析到测试类 —— 解析失配，先修测试本身")
        covered = {i.split(".")[1] for i in ids}
        self.assertEqual(defined - covered, set(CI_EXCLUDED_CLASSES),
                         "CI 测试集必须覆盖除白名单外的全部测试类")


if __name__ == "__main__":
    unittest.main()
