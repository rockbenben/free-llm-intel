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
        # 2026-09-22 起巡检不再开 PR（档案更新改为与快照/新闻一起直接提交），
        # 所以不再需要 pull-requests 写权限 —— 最小权限原则。
        self.assertNotIn("pull-requests", perms,
                         "不再开 PR 就不该申请 pull-requests 写权限")

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
        self.assertNotIn("Sync existing AI PR overrides", step_names,
                         "旧 PR 流程的遗留分支同步步骤已退役：新流程不再产生 ai/intel-update 分支，"
                         "留着它反而会把过期补丁灌回 main（2026-09-26 手动清理遗留分支后移除）")
        self.assertIn("Restore translate cache", step_names)
        self.assertIn("Run intel crawler", step_names)
        self.assertIn("Decide commit path", step_names)
        # 2026-09-22：不再开 PR 等人工审核 —— 档案更新与快照 / 新闻走同一条提交路径
        self.assertIn("Commit all updates", step_names)
        self.assertNotIn("Open PR for AI-reviewed profile updates", step_names,
                         "档案更新已改为自动采纳，不应再有开 PR 的步骤")

        # 检查 checkout 是否配置了 fetch-depth: 0
        checkout_step = next(s for s in steps if s.get("name") == "Checkout")
        self.assertEqual(checkout_step.get("with", {}).get("fetch-depth"), 0)

        crawl_step = next(s for s in steps if s.get("name") == "Run intel crawler")
        self.assertNotIn("--no-browser", crawl_step.get("run", ""),
                         "CI crawler run must keep the browser fallback enabled")
        self.assertIn("--ai-review", crawl_step.get("run", ""))
        self.assertIn("--ai-titles", crawl_step.get("run", ""),
                      "新增标题的 AI 润色必须随巡检开启，否则机翻味标题要等人工发起")

        # 2026-09-22：不再有 create-pull-request 步骤（档案更新改为与快照/新闻一起直提），
        # 原「Open PR 必须早于 Commit snapshots」的顺序约束随之取消。
        self.assertNotIn("peter-evans/create-pull-request", yaml.dump(data),
                         "不再开 PR 就不该再引用 create-pull-request action")


    def test_crawler_step_passes_feeds_base_from_repo_variable(self):
        """订阅源前缀必须能通过 repository variable 覆盖（配了自定义域名的仓库需要）。

        Regression: 前缀只按 `GITHUB_REPOSITORY` 推导时，配了自定义域名的仓库里 feed 自己
        声明的 `rel=self` / `<source url>` 会指向 github.io，而浏览页顶部显示的是自定义域名
        —— 两者不一致，且每个订阅多一跳 301。
        """
        with open(self.workflow_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        by_name = {s.get("name", ""): s for s in data["jobs"]["crawl"]["steps"]}
        step = by_name["Run intel crawler"]
        self.assertIn("--feeds-base", step.get("run", ""),
                      "爬虫步骤必须传 --feeds-base，否则自定义域名不生效")
        self.assertIn("vars.FEEDS_BASE", step.get("env", {}).get("FEEDS_BASE", ""),
                      "FEEDS_BASE 必须取自 repository variable —— 留空即退回自动推导，"
                      "fork 后无需配置")

    def test_ai_profile_updates_commit_directly(self):
        """AI 采纳的档案更新走直提：提交清单必须带上 overrides 与 README。

        2026-09-22 起不再有「待审 PR」；2026-09-26 起连遗留分支同步步骤也退役
        （见 test 里对它的 NotIn 守卫），事实字段的唯一入库路径就是证据闸门 + 直提。
        """
        with open(self.workflow_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        by_name = {s.get("name", ""): s for s in data["jobs"]["crawl"]["steps"]}

        commit = by_name["Commit all updates"]["run"]
        self.assertIn("profile_overrides.json", commit,
                      "AI 采纳的档案补丁必须随巡检提交进 main")
        self.assertIn("README.md", commit, "README 按新档案重渲染，也要一起提交")
        self.assertNotIn("git checkout HEAD --", commit,
                         "不应再有把档案补丁还原回 main 的旧流程残留")
        self.assertNotIn("ai/intel-update", commit,
                         "提交流程不应再引用旧 PR 分支")

    def test_workflow_commits_self_hosted_feeds(self):
        """docs/feeds 是 GitHub Pages 的发布目录：提交路径必须带上它。

        Regression: 只改脚本不改 git add，Pages 上的订阅源就永远是初始那一版，
        而本地产物看起来完全正常（新增文章全在仓库里，只是没人订阅得到）。
        """
        with open(self.workflow_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        by_name = {s.get("name", ""): s for s in data["jobs"]["crawl"]["steps"]}
        # 2026-09-22 起只有一条提交路径（档案更新与快照 / 新闻一起原子提交）
        self.assertIn("docs/feeds", by_name["Commit all updates"]["run"],
                      "Commit all updates 必须提交自建 RSS 产物，否则 Pages 上的订阅源不会更新")

    def test_workflow_changelog_add_is_conditional(self):
        """llm-intel-changelog.md 要等第一次 AI 采纳档案更新才落盘，git add 必须判存在。

        Regression: 2026-09-25 巡检把尚不存在的它写进无条件 add 清单，
        `fatal: pathspec ... did not match any files` 直接 exit 128，整次巡检产物没推上去。
        """
        with open(self.workflow_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        by_name = {s.get("name", ""): s for s in data["jobs"]["crawl"]["steps"]}
        commit = by_name["Commit all updates"]["run"]
        add_lines = [line.strip() for line in commit.splitlines()
                     if "git add" in line and "llm-intel-changelog.md" in line]
        self.assertEqual(len(add_lines), 1,
                         "变更日志应恰好被 add 一次")
        self.assertRegex(add_lines[0], r"^if \[ -f ",
                         "变更日志的 git add 必须是 `[ -f ... ]` 条件式，"
                         "仓库初始化（首次 AI 档案更新前）时该文件不存在")

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
    """爬虫启动时清理历史残留的 `.ai-changed` 标记。

    在**临时目录**里跑（把 `_repo_root` patch 过去），因此不会碰真实仓库根的标记 ——
    那是 workflow「Decide commit path」判定走 PR 还是直提的判据，CI 里删掉它会把 PR 路由
    踩坏（本类此前因此只能被排除在 CI 之外）。改注入后，同一个代码路径可以在 CI 里跑。
    """

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.fake_root = Path(self.temp_dir.name)
        self._orig_root = crawler_llm_intel._repo_root
        crawler_llm_intel._repo_root = lambda: self.fake_root

    def tearDown(self):
        crawler_llm_intel._repo_root = self._orig_root
        self.temp_dir.cleanup()

    @staticmethod
    def _run_main():
        with contextlib.redirect_stderr(io.StringIO()):
            return crawler_llm_intel.main(["--yaml", "non_existent_yaml.yaml"])

    def test_stale_ai_changed_cleaned_up(self):
        stale_marker = self.fake_root / ".ai-changed"
        stale_marker.write_text("stale: update", encoding="utf-8")
        self.assertTrue(stale_marker.exists())

        # 传入不存在的 yaml 触发早期退出，同时验证清理已执行
        self.assertEqual(self._run_main(), 1, "yaml 不存在时应以 1 退出")
        self.assertFalse(stale_marker.exists(), "爬虫启动时必须清理历史残留的 .ai-changed 标记")

    def test_repo_root_is_redirected_to_temp(self):
        """守卫：本类的 setUp 必须把 `_repo_root` 指到临时目录。

        否则 `main()` 会去删**真实仓库根**的 `.ai-changed` —— 那是 workflow「Decide commit
        path」判定走 PR 还是直提的判据，CI 里删掉它会把 PR 路由踩坏（本类此前正因此被排除
        在 CI 之外）。这里**只读不写**，绝不去碰真实文件。
        """
        resolved = crawler_llm_intel._repo_root()
        self.assertEqual(resolved, self.fake_root,
                         "setUp 必须替换 _repo_root，否则会动到真实仓库根")
        real_root = Path(crawler_llm_intel.__file__).resolve().parent
        self.assertNotEqual(resolved, real_root, "_repo_root 不得指向真实仓库根")


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


class TestArchiveTitleRetention(unittest.TestCase):
    """重抓回来的英文标题必须沿用归档里已有的中文标题。

    归档合并取的是**本次抓到的** Article（英文原标题），翻译走 translate_to_zh；
    CI 端 .translate_cache.json 不随仓库走，AI 手工重译过的标题第二天就会被
    Google 机翻冲掉（实测：「GPT-6 的提示缓存全面升级」→「更好的 GPT-6 提示缓存」）。
    """

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.news_dir = Path(self.temp_dir.name) / "llm-news"
        self.news_dir.mkdir(parents=True)
        self.feeds_dir = Path(self.temp_dir.name) / "feeds"

    def tearDown(self):
        self.temp_dir.cleanup()

    def _intel(self, articles):
        return crawler_llm_intel.VendorIntel(
            vendor_id="vendor_a", brand="Vendor A", homepage="https://a.com",
            products=[], all_news_articles=articles)

    def test_refetched_english_title_keeps_archived_chinese(self):
        arch_path = self.news_dir / "vendor_a.md"
        arch_path.write_text(
            "## 全部文章（共 1 篇）\n\n"
            "1. [GPT-6 的提示缓存全面升级](https://a.com/x)（2026-09-22）\n",
            encoding="utf-8")
        fresh = crawler_llm_intel.Article(
            title="Better prompt caching for GPT-6",
            url="https://a.com/x", date="2026-09-22")
        intel = self._intel([fresh])
        with mock.patch.object(
                crawler_llm_intel, "translate_to_zh",
                side_effect=AssertionError("沿用归档中文标题时不应再发起翻译")):
            crawler_llm_intel.write_news_archives(self.news_dir, [intel],
                                                  clean_removed=False)
        content = arch_path.read_text(encoding="utf-8")
        self.assertIn("GPT-6 的提示缓存全面升级", content,
                      "归档已有的中文标题不得被重抓的英文原标题冲掉")
        self.assertNotIn("Better prompt caching", content)

    def test_rss_feed_uses_retained_title(self):
        fresh = crawler_llm_intel.Article(
            title="Better prompt caching for GPT-6",
            url="https://a.com/x", date="2026-09-22")
        fresh.zh_title = "GPT-6 的提示缓存全面升级"  # 模拟 write_news_archives 合并结果
        intel = self._intel([fresh])
        with mock.patch.object(
                crawler_llm_intel, "translate_to_zh",
                side_effect=AssertionError("zh_title 已给出时不应再翻译")):
            crawler_llm_intel.write_rss_feeds(self.feeds_dir, [intel],
                                              clean_removed=False)
        xml = (self.feeds_dir / "llm-news-vendor_a.xml").read_text(encoding="utf-8")
        self.assertIn("<title>GPT-6 的提示缓存全面升级</title>", xml)
        # <description> 里的「原文标题」是刻意保留的英文副标题，不该被算作回退
        self.assertIn("原文标题：Better prompt caching", xml)

    def test_english_only_archive_title_still_translated(self):
        """归档标题本身是英文（未汉化）时，照常走翻译，不阻断汉化。"""
        arch_path = self.news_dir / "vendor_a.md"
        arch_path.write_text(
            "## 全部文章（共 1 篇）\n\n"
            "1. [Old English Title](https://a.com/x)（2026-09-22）\n",
            encoding="utf-8")
        fresh = crawler_llm_intel.Article(
            title="Old English Title", url="https://a.com/x", date="2026-09-22")
        intel = self._intel([fresh])
        with mock.patch.object(
                crawler_llm_intel, "translate_to_zh",
                return_value="旧英文标题"):
            crawler_llm_intel.write_news_archives(self.news_dir, [intel],
                                                  clean_removed=False)
        self.assertIn("旧英文标题", arch_path.read_text(encoding="utf-8"))


class TestAiTitlePolish(unittest.TestCase):
    """--ai-titles：本轮新增标题交给 LLM 润色一次，失败回落 Google 机翻。"""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.news_dir = Path(self.temp_dir.name) / "llm-news"
        self.news_dir.mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parse_polish_response(self):
        expected = ["Alpha release", "Beta release"]
        out = crawler_llm_intel.parse_polish_response(
            "1\t甲发布\n"      # 制表分隔
            "2.乙发布\n"        # 点号分隔也要认
            "3\t越界编号\n"      # 越界 → 丢
            "废话行\n"           # 无编号 → 丢
            "1\t重复取首个",
            expected)
        self.assertEqual(out["Alpha release"], "甲发布")
        self.assertEqual(out["Beta release"], "乙发布")
        self.assertNotIn("重复", "".join(out.values()))

    def test_parse_polish_rejects_untranslated_and_runon(self):
        expected = ["Some headline"]
        out = crawler_llm_intel.parse_polish_response(
            "1\tSome headline still English without any Chinese", expected)
        self.assertEqual(out, {})
        long_zh = "好" * 300
        self.assertEqual(crawler_llm_intel.parse_polish_response(
            f"1\t{long_zh}", expected), {}, "超长疑似续写解释应丢弃")

    def test_polish_applied_to_new_english_items_only(self):
        # 归档已有中文标题的旧文章 + 本轮新增一篇英文文章
        arch_path = self.news_dir / "vendor_a.md"
        arch_path.write_text(
            "## 全部文章（共 1 篇）\n\n"
            "1. [既有中文标题](https://a.com/old)（2026-09-01）\n", encoding="utf-8")
        old_fresh = crawler_llm_intel.Article(
            title="Existing headline", url="https://a.com/old", date="2026-09-01")
        new_fresh = crawler_llm_intel.Article(
            title="Brand new headline", url="https://a.com/new", date="2026-09-25")
        vendor = crawler_llm_intel.VendorIntel(
            vendor_id="vendor_a", brand="Vendor A", homepage="https://a.com",
            products=[], all_news_articles=[old_fresh, new_fresh])
        seen: list[list[str]] = []

        def polish(brand, titles):
            seen.append(list(titles))
            return {t: f"译文{t}" for t in titles}

        crawler_llm_intel.write_news_archives(self.news_dir, [vendor],
                                              clean_removed=False, title_polish=polish)
        self.assertEqual(seen, [["Brand new headline"]],
                         "只应把**新增**且仍是英文的标题送润色")
        content = arch_path.read_text(encoding="utf-8")
        self.assertIn("译文Brand new headline", content)
        self.assertIn("既有中文标题", content, "旧条目的归档译文不受影响")

    def test_polish_failure_falls_back_to_translate(self):
        vendor = crawler_llm_intel.VendorIntel(
            vendor_id="vendor_a", brand="Vendor A", homepage="https://a.com",
            products=[], all_news_articles=[crawler_llm_intel.Article(
                title="Failing headline", url="https://a.com/x", date="2026-09-25")])

        def boom(brand, titles):
            raise RuntimeError("quota 炸了")

        with mock.patch.object(crawler_llm_intel, "translate_to_zh",
                               return_value="机翻兜底"):
            crawler_llm_intel.write_news_archives(self.news_dir, [vendor],
                                                  clean_removed=False,
                                                  title_polish=boom)
        self.assertIn("机翻兜底",
                      (self.news_dir / "vendor_a.md").read_text(encoding="utf-8"))

    def test_polisher_batches_and_respects_budget(self):
        titles = [f"Headline number {i}" for i in range(95)]
        calls: list[int] = []

        def fake_call_llm(prompt, **kw):
            n = prompt.count("\t")
            calls.append(n)
            idxs = re.findall(r"(?m)^(\d+)\t", prompt)
            return "\n".join(f"{i}\t标题{i}" for i in idxs)

        with mock.patch.object(ai_review, "call_llm", side_effect=fake_call_llm):
            polish = crawler_llm_intel.make_llm_title_polisher(budget=50, batch=40)
            out = polish("Brand", titles)
        self.assertEqual(calls, [40, 10], "应按 batch 切分且总预算封顶 50")
        self.assertEqual(len(out), 50)


class TestModelReleaseRadar(unittest.TestCase):
    """模型发布雷达：从归档标题抽 (厂商,模型,日期)，宁可漏不可错。"""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _intel(self, articles, vid="vendor_a", brand="Vendor A"):
        return crawler_llm_intel.VendorIntel(
            vendor_id=vid, brand=brand, homepage=f"https://{vid}.com",
            products=[], all_news_articles=articles)

    def test_structured_model_id_from_changelog(self):
        arts = [crawler_llm_intel.Article(
            title="qwen3.8-omni-flash：支持实时音视频交互",
            url="https://a.com/x", date="2026-09-17")]
        ev = crawler_llm_intel.extract_model_releases([self._intel(arts, "aliyun_qwen")])
        self.assertEqual([e["model"] for e in ev], ["qwen3.8-omni-flash"])

    def test_english_intro_word_stripped(self):
        ev = crawler_llm_intel.extract_model_releases([self._intel(
            [crawler_llm_intel.Article(title="Introducing GPT-5.5",
                                       url="https://a.com/y", date="2026-04-23")])])
        self.assertEqual([e["model"] for e in ev], ["GPT-5.5"],
                         "发布引导词不能落在型号开头")

    def test_year_and_head_noise_rejected(self):
        # 「ModCon 2026」只有裸年份 → 丢弃；GLM-ASR-2512 的 2512 是版本 → 保留
        arts = [crawler_llm_intel.Article(title="ModCon 2026 大会上线", url="u1", date="2026-01-01"),
                crawler_llm_intel.Article(title="GLM-ASR-2512 语音识别模型上线", url="u2", date="2025-12-10")]
        models = [e["model"] for e in crawler_llm_intel.extract_model_releases([self._intel(arts)])]
        self.assertNotIn("ModCon 2026", models)
        self.assertIn("GLM-ASR-2512", models)

    def test_dedup_by_vendor_and_model(self):
        arts = [crawler_llm_intel.Article(title="GLM-5.2：专为长周期任务打造", url="a", date="2026-06-17"),
                crawler_llm_intel.Article(title="GLM-5.2 新版上线", url="b", date="2026-06-18")]
        ev = crawler_llm_intel.extract_model_releases([self._intel(arts)])
        self.assertEqual(len(ev), 1, "同厂商同型号只保留一条（首次出现）")

    def test_undated_and_no_verb_ignored(self):
        arts = [crawler_llm_intel.Article(title="我们为什么重构了推理栈", url="a", date="2026-05-01"),
                crawler_llm_intel.Article(title="GPT-9 发布", url="b", date="")]
        self.assertEqual(crawler_llm_intel.extract_model_releases([self._intel(arts)]), [])

    def test_write_model_releases_idempotent(self):
        arts = [crawler_llm_intel.Article(title="Kimi K3 发布", url="https://k/3", date="2026-07-01")]
        ev = crawler_llm_intel.extract_model_releases([self._intel(arts, "moonshot_kimi", "Kimi")])
        p = self.root / "model-releases.json"
        self.assertTrue(crawler_llm_intel.write_model_releases(p, ev))
        self.assertFalse(crawler_llm_intel.write_model_releases(p, ev),
                         "内容不变不得重写（无时间戳）")
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(data["fields"][0], "date")
        self.assertEqual(data["releases"][0][1], "moonshot_kimi")


class TestDateBackfill(unittest.TestCase):
    """--backfill-dates 的解析器与回填写行逻辑（网络以注入的 fetch 替身）。"""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.news = Path(self.temp_dir.name) / "llm-news"
        self.news.mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_resolver_priority_and_noise(self):
        self.assertEqual(
            crawler_llm_intel.resolve_article_date(
                '<script>{"datePublished":"2026-09-24T00:00:00Z"}</script>'), "2026-09-24")
        self.assertEqual(
            crawler_llm_intel.resolve_article_date(
                '<meta property="article:published_time" content="Sep 15, 2026">'), "2026-09-15")
        self.assertEqual(
            crawler_llm_intel.resolve_article_date('<time datetime="2026-08-01">x</time>'), "2026-08-01")
        self.assertEqual(crawler_llm_intel.resolve_article_date(
            '{"datePublished":"0001-01-01"}'), "", "占位年份视为噪声")
        self.assertEqual(crawler_llm_intel.resolve_article_date("<p>无日期</p>"), "")

    def test_backfill_fills_only_missing_and_rewrites_suffix(self):
        (self.news / "v.md").write_text(
            "## 全部文章（共 2 篇）\n\n"
            "1. [有日期文章](https://x.com/a)（2026-09-01）\n"
            "2. [缺日期文章](https://x.com/b)\n", encoding="utf-8")
        calls = []

        def fetch(url):
            calls.append(url)
            return '{"datePublished":"2026-07-19T08:00:00Z"}'

        visited, filled = crawler_llm_intel.backfill_archive_dates(
            self.news, fetch, delay=0)
        self.assertEqual(calls, ["https://x.com/b"], "只访问缺日期的条目")
        self.assertEqual((visited, filled), (1, 1))
        content = (self.news / "v.md").read_text(encoding="utf-8")
        self.assertIn("2. [缺日期文章](https://x.com/b)（2026-07-19）", content)
        self.assertIn("1. [有日期文章](https://x.com/a)（2026-09-01）", content,
                      "已有日期行不得被改写")

    def test_backfill_respects_limit_and_swallows_errors(self):
        lines = [f"{i+1}. [t{i}](https://x.com/{i})" for i in range(5)]
        (self.news / "v.md").write_text(
            "## 全部文章\n\n" + "\n".join(lines) + "\n", encoding="utf-8")

        def fetch(url):
            if url.endswith("1"):
                raise RuntimeError("网络炸了")
            return '<time datetime="2026-05-05">'

        visited, filled = crawler_llm_intel.backfill_archive_dates(
            self.news, fetch, limit=3, delay=0)
        self.assertEqual(visited, 3, "不得超过单次访问上限")
        self.assertEqual(filled, 2, "抓取失败按解不出处理，不写日期")


class TestIntelChangelogAndStaleReview(unittest.TestCase):
    """情报变更日志的追加/置顶/裁剪，与例行复查的超期判定。"""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _entry(self, vid="vendor_a", brand="Vendor A", summary="额度翻倍",
               diffs=(("free_quota", "旧额度", "新额度"),)):
        return {"vendor_id": vid, "brand": brand, "summary": summary,
                "diffs": list(diffs)}

    def test_fmt_compacts_and_truncates(self):
        self.assertEqual(crawler_llm_intel._changelog_fmt(None), "（原无此项）")
        self.assertEqual(crawler_llm_intel._changelog_fmt(["a", "b"]), "a、b")
        long = crawler_llm_intel._changelog_fmt("字" * 400)
        self.assertTrue(long.endswith("…") and len(long) <= 160)

    def test_append_creates_then_merges_same_day_and_prepends_new_day(self):
        p = self.root / crawler_llm_intel.CHANGELOG_MD
        crawler_llm_intel.append_intel_changelog(p, "2026-09-25", [self._entry()])
        crawler_llm_intel.append_intel_changelog(p, "2026-09-25", [
            self._entry(vid="vendor_b", brand="Vendor B", summary="下线旧模型",
                        diffs=[("free_models", "a、b", "a")])])
        content = p.read_text(encoding="utf-8")
        self.assertEqual(content.count("## 2026-09-25"), 1, "同日必须并入一个日块")
        self.assertIn("`free_models`：a、b → a", content)
        crawler_llm_intel.append_intel_changelog(p, "2026-09-26", [
            self._entry(vid="vendor_c", brand="Vendor C", summary="新活动")])
        content = p.read_text(encoding="utf-8")
        self.assertLess(content.find("## 2026-09-26"), content.find("## 2026-09-25"),
                        "新日块置顶（最新在前）")

    def test_append_trims_oldest_days_over_budget(self):
        p = self.root / crawler_llm_intel.CHANGELOG_MD
        for d in range(1, 13):
            crawler_llm_intel.append_intel_changelog(
                p, f"2026-08-{d:02d}",
                [self._entry(vid=f"v{i}", brand=f"V{i}") for i in range(20)])
        content = p.read_text(encoding="utf-8")
        n_vendors = content.count("### ")
        self.assertLessEqual(n_vendors, crawler_llm_intel.CHANGELOG_MAX_VENDORS)
        self.assertNotIn("## 2026-08-01", content, "超预算的最旧日块应整块裁掉")
        self.assertIn("## 2026-08-12", content)

    def test_stale_vendors_orders_oldest_first_and_covers_never_reviewed(self):
        snaps = crawler_llm_intel.SnapshotState(self.root)
        snaps.reviews = {"a": "2026-08-01", "b": "2026-09-20", "c": "2026-09-01"}
        stale = snaps.stale_vendors(["a", "b", "c", "d"], days=45, today="2026-09-25")
        # cutoff = 2026-08-11：b/c 未超期；a 超期；d 从未核查（视为最久）
        self.assertEqual(stale, ["d", "a"])

    def test_mark_reviewed_persists_in_save(self):
        snaps = crawler_llm_intel.SnapshotState(self.root)
        snaps.mark_reviewed("a", when="2026-09-25")
        snaps.save({"a"}, full_run=True)
        reloaded = crawler_llm_intel.SnapshotState(self.root)
        self.assertEqual(reloaded.reviews.get("a"), "2026-09-25")

    def test_legacy_state_without_reviews_loads(self):
        (self.root / crawler_llm_intel.SNAPSHOT_STATE).write_text(
            json.dumps({"sources": {"a|x|u": {"sha256": "h"}}}), encoding="utf-8")
        snaps = crawler_llm_intel.SnapshotState(self.root)
        self.assertEqual(snaps.reviews, {})
        self.assertIn("a|x|u", snaps.entries)


class TestMdChangelogExtraction(unittest.TestCase):
    """Mintlify `.md` 变更日志抽取（groq console changelog.md 实测格式）。"""

    MD = """---
description: Track the latest updates.
title: Changelog - GroqDocs
---

# Changelog

[RSS](https://github.com/groq/groq-changelog/commits/main.atom)[Get Email Updates](https://groq.com/x)

---

Apr 18

### Added[MiniMax M2.5 and Qwen3-VL 32B Instruct (Enterprise)](#minimax-m25)

`minimaxai/minimax-m2.5` and `qwen/qwen3-vl-32b-instruct` are now available.

### Changed[Python SDK v1.2.0](#python-sdk-v120)

Details here.

---

Dec 1, 2025

### Added[MCP Connectors (Beta)](#mcp-connectors-beta)

Some text.

#### NotADate[Kept only if heading level varies](#x)
"""

    def _page(self, raw):
        return crawler_llm_intel.PageResult(
            url="https://console.groq.com/docs/changelog.md",
            stype="changelog", ok=True, raw=raw)

    def test_entries_titles_anchors_dates(self):
        arts = crawler_llm_intel.extract_md_changelog(
            self.MD, "https://console.groq.com/docs/changelog.md", today="2026-09-26")
        titles = [a.title for a in arts]
        self.assertIn("MiniMax M2.5 and Qwen3-VL 32B Instruct (Enterprise)", titles)
        self.assertIn("MCP Connectors (Beta)", titles)
        got = {a.title: a for a in arts}
        # 无年份的 `Apr 18` → 今年（不晚于今天）
        self.assertEqual(got["MiniMax M2.5 and Qwen3-VL 32B Instruct (Enterprise)"].date,
                         "2026-04-18")
        self.assertEqual(got["MCP Connectors (Beta)"].date, "2025-12-01")
        self.assertTrue(got["MCP Connectors (Beta)"].url.endswith("#mcp-connectors-beta"))
        # 分类前缀（Added/Changed）不得留在标题里
        self.assertTrue(all(not t.startswith(("Added", "Changed")) for t in titles))

    def test_too_few_entries_not_trusted(self):
        md = "# Changelog\n\n---\n\nApr 18\n\n### Added[Solo Item](#solo)\n"
        self.assertEqual(crawler_llm_intel.extract_articles_from_page(self._page(md), max_items=100), [])

    def test_html_page_skips_md_branch(self):
        html = "<html><body><h2>2026-01-01</h2></body></html>"
        page = crawler_llm_intel.PageResult(url="https://x.com/blog", stype="blog", ok=True, raw=html)
        arts = crawler_llm_intel.extract_articles_from_page(page)
        self.assertTrue(all(a.url.startswith("http") for a in arts))


class TestRebuildOnly(unittest.TestCase):
    """--rebuild-only：不触网，从磁盘产物重建动态类产物。

    场景固化：开发者改了 llm-news/*.md 里的归档标题，本地一条命令刷新
    RSS/索引/总表，不必等 CI、也不用手工对齐产物 diff。
    """

    YAML = """
vendors:
  - id: vendor_a
    brand: Vendor A
    homepage: https://a.com
    products: []
  - id: vendor_b
    brand: Vendor B
    homepage: https://b.com
    products: []
sources:
  - vendor_id: vendor_a
    type: blog
    url: https://a.com/blog
  - vendor_id: vendor_a
    type: pricing
    url: https://a.com/pricing
  - vendor_id: vendor_b
    type: feed
    url: https://b.com/rss.xml
"""

    NEWS_MD = """# 动态总览

### Vendor A (vendor_a)
- 页面：[官方博客](https://a.com/blog)
  - 📡 RSS/Atom：https://a.com/blog/rss.xml
- 📰 **最新文章**（官方源抓取于 2026-09-25，标题自动汉化）：
  1. [甲文章标题](https://a.com/1)（2026-09-01）
  - 📄 完整文章归档（共 1 篇）：[vendor_a.md](llm-news/vendor_a.md)

### Vendor B (vendor_b)
- 📡 [RSS/Atom 订阅源](https://b.com/rss.xml)：`https://b.com/feed`
- 📰 **最新文章**（官方源抓取于 2026-09-25，标题自动汉化）：
  1. [乙条目标题](https://b.com/1)（2026-09-02）

---
共整理 2 个厂商的动态入口
"""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self._orig_root = crawler_llm_intel._repo_root
        crawler_llm_intel._repo_root = lambda: self.root
        (self.root / "llm-news").mkdir()
        (self.root / "intel.yaml").write_text(self.YAML, encoding="utf-8")
        (self.root / "news.md").write_text(self.NEWS_MD, encoding="utf-8")
        (self.root / "llm-news" / "vendor_a.md").write_text(
            "# Vendor A 文章归档\n\n## 全部文章（共 1 篇）\n\n"
            "1. [甲文章标题](https://a.com/1)（2026-09-01）\n", encoding="utf-8")
        (self.root / "llm-news" / "vendor_b.md").write_text(
            "# Vendor B 文章归档\n\n## 全部文章（共 1 篇）\n\n"
            "1. [乙条目标题](https://b.com/1)（2026-09-02）\n", encoding="utf-8")

    def tearDown(self):
        crawler_llm_intel._repo_root = self._orig_root
        self.temp_dir.cleanup()

    def test_parse_page_states_recovers_feeds_and_flags(self):
        states = crawler_llm_intel._parse_news_md_page_states(self.NEWS_MD)
        a = states["vendor_a"]
        self.assertEqual(a[0]["url"], "https://a.com/blog")
        self.assertEqual(a[0]["feeds"], ["https://a.com/blog/rss.xml"])
        self.assertTrue(a[0]["ok"])
        b = states["vendor_b"]
        self.assertEqual(b[0]["url"], "https://b.com/rss.xml")
        self.assertEqual(b[0]["final_url"], "https://b.com/feed")

    def test_rebuild_intel_uses_yaml_stype_and_archives(self):
        vendors, sources = crawler_llm_intel.parse_yaml(self.root / "intel.yaml")
        grouped = crawler_llm_intel.group_sources_by_vendor(sources)
        states = crawler_llm_intel._parse_news_md_page_states(self.NEWS_MD)
        intel_list = crawler_llm_intel.rebuild_intel_from_disk(
            vendors, grouped, states, self.root / "llm-news")
        self.assertEqual([v.vendor_id for v in intel_list], ["vendor_a", "vendor_b"])
        va = intel_list[0]
        # stype 来自 yaml（非反查 label），feed 检测状态来自产物
        self.assertEqual(va.news_pages[0].stype, "blog")
        self.assertEqual(va.news_pages[0].feeds, ["https://a.com/blog/rss.xml"])
        self.assertEqual([a.url for a in va.all_news_articles], ["https://a.com/1"])
        self.assertEqual(va.news_articles[0].title, "甲文章标题")
        # feed 型源重建后仍被判为原生源厂商
        self.assertIn("vendor_b", crawler_llm_intel._native_feed_vendors(intel_list))

    def test_rebuild_skips_yaml_removed_pages(self):
        """产物里残留、yaml 已删除的入口不得被重建复活。"""
        vendors, sources = crawler_llm_intel.parse_yaml(self.root / "intel.yaml")
        sources = [s for s in sources if s["url"] != "https://a.com/blog"]
        grouped = crawler_llm_intel.group_sources_by_vendor(sources)
        states = crawler_llm_intel._parse_news_md_page_states(self.NEWS_MD)
        intel_list = crawler_llm_intel.rebuild_intel_from_disk(
            vendors, grouped, states, self.root / "llm-news")
        va = next(v for v in intel_list if v.vendor_id == "vendor_a")
        self.assertEqual(va.news_pages, [])

    def test_rebuild_attaches_original_titles(self):
        """英文原文从 articles.json 回填到 art.title，中文归档标题落成 zh_title。

        归档 .md 只有中文显示标题；没有回填的话，RSS 的「原文标题」与索引
        第 5 列会在 rebuild 后静默丢失。
        """
        feeds = self.root / "docs" / "feeds"
        feeds.mkdir(parents=True)
        (feeds / "articles.json").write_text(json.dumps({
            "fields": ["title", "url", "vendor", "date", "original_title"],
            "count": 1,
            "articles": [["甲文章标题", "https://a.com/1", "vendor_a",
                          "2026-09-01", "Original English Headline"]],
        }, ensure_ascii=False), encoding="utf-8")
        vendors, sources = crawler_llm_intel.parse_yaml(self.root / "intel.yaml")
        grouped = crawler_llm_intel.group_sources_by_vendor(sources)
        states = crawler_llm_intel._parse_news_md_page_states(self.NEWS_MD)
        orig = crawler_llm_intel.load_original_titles(feeds / "articles.json")
        intel_list = crawler_llm_intel.rebuild_intel_from_disk(
            vendors, grouped, states, self.root / "llm-news", orig)
        art = intel_list[0].all_news_articles[0]
        self.assertEqual(art.zh_title, "甲文章标题")
        self.assertEqual(art.title, "Original English Headline")

    def test_rebuild_matches_md_endpoint_switch(self):
        """换源到 `.md` 端点（groq 实测）：产物记旧 URL，归一后缀仍能富化检测到的 feed。"""
        vendors, sources = crawler_llm_intel.parse_yaml(self.root / "intel.yaml")
        sources = [s for s in sources if s["url"] != "https://a.com/blog"]
        sources.append({"vendor_id": "vendor_a", "type": "blog", "url": "https://a.com/blog.md"})
        (self.root / "intel.yaml").write_text(
            self.YAML.replace(
                "  - vendor_id: vendor_a\n    type: blog\n    url: https://a.com/blog\n",
                "  - vendor_id: vendor_a\n    type: blog\n    url: https://a.com/blog.md\n"),
            encoding="utf-8")
        grouped = crawler_llm_intel.group_sources_by_vendor(sources)
        states = crawler_llm_intel._parse_news_md_page_states(self.NEWS_MD)
        intel_list = crawler_llm_intel.rebuild_intel_from_disk(
            vendors, grouped, states, self.root / "llm-news")
        va = next(v for v in intel_list if v.vendor_id == "vendor_a")
        self.assertEqual(va.news_pages[0].url, "https://a.com/blog.md")
        self.assertEqual(va.news_pages[0].feeds, ["https://a.com/blog/rss.xml"],
                         "切换 .md 端点后不得丢失已发现的原生 feed")

    def test_rebuild_includes_yaml_only_new_sources(self):
        """yaml 新增、产物里从没有过的源：首轮即按声明建页，不必等实抓补 feeds.md。"""
        vendors, sources = crawler_llm_intel.parse_yaml(self.root / "intel.yaml")
        sources.append({"vendor_id": "vendor_a", "type": "news", "url": "https://a.com/press"})
        grouped = crawler_llm_intel.group_sources_by_vendor(sources)
        intel_list = crawler_llm_intel.rebuild_intel_from_disk(
            vendors, grouped, {}, self.root / "llm-news")
        va = next(v for v in intel_list if v.vendor_id == "vendor_a")
        urls = [p.url for p in va.news_pages]
        self.assertEqual(urls, ["https://a.com/blog", "https://a.com/press"])

    def test_main_rebuild_only_touches_no_network(self):
        """端到端守卫：rebuild 全流程不得调用抓取 / 浏览器 / 翻译接口。"""
        with (
            mock.patch.object(crawler_llm_intel, "crawl_vendor",
                              side_effect=AssertionError("rebuild 不得抓取")),
            mock.patch.object(crawler_llm_intel, "BrowserSession",
                              side_effect=AssertionError("rebuild 不得开浏览器")),
            mock.patch.object(crawler_llm_intel, "translate_to_zh",
                              side_effect=AssertionError("归档中文标题不该触发翻译")),
        ):
            rc = crawler_llm_intel.main([
                "--rebuild-only", "--yaml", "intel.yaml", "--news-md", "news.md",
                "--news-opml", "news.opml"])
        self.assertEqual(rc, 0)
        xml = (self.root / "docs" / "feeds" / "llm-news-vendor_a.xml").read_text(
            encoding="utf-8")
        self.assertIn("甲文章标题", xml)
        index = json.loads((self.root / "docs" / "feeds" / "articles.json").read_text(
            encoding="utf-8"))
        self.assertEqual({r[2] for r in index["articles"]}, {"vendor_a", "vendor_b"})
        # 快照状态与 README 都不许被 rebuild 触碰
        self.assertFalse((self.root / "llm-intel-state.json").exists())
        self.assertFalse((self.root / "README.md").exists())

    def test_rebuild_only_rejects_only_and_no_news(self):
        rc = crawler_llm_intel.main(["--rebuild-only", "--no-news",
                                     "--yaml", "intel.yaml"])
        self.assertEqual(rc, 2)


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
        # 4 个产物：合并流 + 2 个单厂商源 + 全量文章索引（articles.json）；
        # 4 条 feed 条目：合并流 2 条 + 单源各 1 条；
        # changed 多 2 是 vendors.json 厂商索引与 articles.json 全量索引
        self.assertEqual((files, items, changed, skipped), (4, 4, 5, 0))
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


class TestCardAnchorTitleExtraction(unittest.TestCase):
    """卡片式列表页：`<a>` 把标题与整段描述一起包住时，标题要取**锚内标题元素**。

    Regression: 锚文本被拍平后是「标题 + 整段描述」粘成的长串（解析器在 `<a>` 内不插
    块级分隔）。实测通义更新日志 **100%**、x.ai/news 37%、MiniMax 30% 的条目如此 ——
    那些条目的「标题」是一整段正文，订阅后根本没法扫读。
    """

    CARD_HTML = """
    <html><body>
      <div class="card"><a href="/news/grok-4-6-microsoft-foundry">
        <h3>Microsoft Foundry 上的 Grok 4.6</h3>
        <p>Grok 4.6 现已通过 Microsoft Foundry 提供。</p>
      </a></div>
      <div class="card"><a href="/news/plain-item-without-heading">
        Plain item without any heading element, long enough to pass the length gate
      </a></div>
      <div class="card"><a href="/news/short-heading-item">
        <h3>Grok 4.6</h3>
        <p>这是一段很长的描述文本，用来确认标题元素过短时会退回锚文本而不是把条目丢掉。</p>
      </a></div>
    </body></html>
    """

    def _parse(self):
        return crawler_llm_intel.parse_html(self.CARD_HTML, "https://x.ai/news")

    def _page(self):
        text, title, feeds, links, headings = self._parse()
        return crawler_llm_intel.PageResult(
            url="https://x.ai/news", stype="news", ok=True,
            final_url="https://x.ai/news", links=links, link_headings=headings)

    def test_link_headings_align_with_links(self):
        _t, _ti, _f, links, headings = self._parse()
        self.assertEqual(len(headings), len(links),
                         "link_headings 必须与 links 逐项对齐（按下标取用）")
        by_url = {u: h for (u, _a), h in zip(links, headings)}
        self.assertEqual(by_url["https://x.ai/news/grok-4-6-microsoft-foundry"],
                         "Microsoft Foundry 上的 Grok 4.6")
        self.assertEqual(by_url["https://x.ai/news/plain-item-without-heading"], "",
                         "锚内没有标题元素时该位置必须是空串，而不是 None")

    def test_extraction_prefers_inner_heading(self):
        arts = crawler_llm_intel.extract_articles_from_page(self._page())
        got = {a.url.rsplit("/", 1)[-1]: a.title for a in arts}
        self.assertEqual(
            got.get("grok-4-6-microsoft-foundry"), "Microsoft Foundry 上的 Grok 4.6",
            "卡片条目必须取锚内标题，而不是拍平后的「标题+正文」长串")
        self.assertIn("plain-item-without-heading", got,
                      "锚内没有标题元素的条目仍要能提取出来（退回锚文本）")
        self.assertIn("short-heading-item", got,
                      "标题元素过短时不得把条目丢掉 —— 应退回锚文本，而不是被长度下限滤掉")


    def test_misaligned_headings_are_ignored(self):
        """两个列表长度不一致时**整体忽略**标题列表、退回锚文本。

        宁可少修几条，也不要错位取到别人的标题 —— 错位是静默的，没人会发现。
        """
        page = self._page()
        page.link_headings = []          # 模拟未来有人只改了 links 的赋值处
        arts = crawler_llm_intel.extract_articles_from_page(page)
        got = {a.url.rsplit("/", 1)[-1]: a.title for a in arts}
        self.assertIn("grok-4-6-microsoft-foundry", got, "失配时仍要能提取条目")
        self.assertTrue(
            got["grok-4-6-microsoft-foundry"].startswith("Microsoft Foundry 上的 Grok 4.6"),
            "失配时应退回锚文本（标题+正文粘成一串），而不是崩溃或错位")

    CONTEXT_DATE_HTML = """
    <html><body>
      <div class="card"><time datetime="2026-09-22">Sep 22, 2026</time>
        <h3><a href="/news/dated-item">A dated item with a long enough title</a></h3></div>
      <div class="card"><span class="date">2026.08.01</span>
        <h3><a href="/news/another-dated-item">Another dated item, also long enough</a></h3></div>
      <div class="card"><h3><a href="/news/undated-item">An item with no date anywhere near it</a></h3></div>
    </body></html>
    """

    def test_link_context_dates_from_html_structure(self):
        """日期只存在于 HTML 结构里（`<time datetime>` / 独立日期元素）时也要取到。

        Regression: `x.ai/news` 用 `<time dateTime="2026-09-22">`、poolside 用
        `<time datetime="2026-05-11">`、cohere 用 `<p>Sep 10, 2026</p>` —— 锚文本与
        锚内标题元素里**都没有**日期，只从标题找日期的旧逻辑在这些页面 8 条里
        0 条带日期，条目因此进不了合并流（无日期只进单厂商源，见 write_rss_feeds）。
        """
        _t, _ti, _f, links, headings = crawler_llm_intel.parse_html(
            self.CONTEXT_DATE_HTML, "https://example.com/news")
        page = crawler_llm_intel.PageResult(
            url="https://example.com/news", stype="news", ok=True,
            final_url="https://example.com/news", raw=self.CONTEXT_DATE_HTML,
            links=links, link_headings=headings)
        arts = crawler_llm_intel.extract_articles_from_page(page)
        got = {a.url.rsplit("/", 1)[-1]: a.date for a in arts}
        self.assertEqual(got.get("dated-item"), "2026-09-22", "`<time datetime>` 里的日期要认")
        self.assertEqual(got.get("another-dated-item"), "2026-08-01", "独立日期元素里的日期也要认")
        self.assertEqual(got.get("undated-item"), "", "附近确实没有日期时保持空，不得张冠李戴")

    def test_context_dates_abandoned_when_anchor_count_mismatches(self):
        """`<a>` 数量与 links 对不上时**整体放弃**，不得错位。

        错位会把上一条的日期安到这一条上，而且完全静默 —— 宁可少修几条。
        """
        html = '<a href="/x">one long enough</a><a href="/y">two long enough</a>'
        self.assertEqual(crawler_llm_intel._link_context_dates(html, 3), ["", "", ""])
        self.assertEqual(crawler_llm_intel._link_context_dates("", 2), ["", ""])


class TestTableAndAdjacentHeadingExtraction(unittest.TestCase):
    """表格行式 / 「日期 + 相邻标题」式发布记录（腾讯混元、快手、商汤）。

    Regression: 这三家的更新日志此前要么提取 **0 条**、要么只产出「更新时间」
    这种零信息标题 —— 结构 3 要求表格行内有 `<code>` 模型 ID（阿里云百炼那种），
    结构 2 会把表格表头当正文首行，结构 4 要求子标题层级**更深**，三家都不满足。
    """

    TABLE_HTML = """
    <html><body>
      <h3 id="1_发布时间：2026年8月">发布时间：2026年8月</h3>
      <table><tr><th>更新时间</th><th>功能模块</th><th>功能说明</th></tr>
        <tr><td>8月14日</td><td>数据分析</td>
            <td>【新增】数据分析任务完成后可将结果下载至本地，便于进一步处理。</td></tr>
        <tr><td>8月2日</td><td>模型部署</td>
            <td>【新增】新增 GLM-5.2-FP8 模型部署能力，支持预付费与后付费模式。</td></tr>
        <tr><td>8月1日</td><td>开发机</td>
            <td>【新增】开发机支持通过 IP 和 Port 进行 SSH 登录及 SCP 文件传输。</td></tr>
      </table>
    </body></html>
    """

    ADJACENT_HTML = """
    <html><body>
      <h3 id="release-202507">release-202507</h3>
      <p><code>2025.07.23</code></p>
      <h2 id="m1"><strong>【模型更新】发布最新版本日日新-融合模态模型 V6.5</strong></h2>
      <h3 id="release-202506">release-202506</h3>
      <p><code>2025.06.03</code></p>
      <h2 id="m2"><strong>【模型更新】发布最新版本日日新-语音大模型合成</strong></h2>
      <h3 id="release-202504">release-202504</h3>
      <p><code>2025.04.09</code></p>
      <h2 id="m3"><strong>【功能更新】OpenAPI 全面支持通过 API Key 调用</strong></h2>
    </body></html>
    """

    def _extract(self, html, url):
        text, _t, _f, links, lh = crawler_llm_intel.parse_html(html, url)
        page = crawler_llm_intel.PageResult(
            url=url, stype="updates", ok=True, final_url=url, raw=html,
            text=text, links=links, link_headings=lh)
        return crawler_llm_intel.extract_articles_from_page(page)

    def test_table_rows_take_year_from_month_section(self):
        """表格行式：日期只写「8月14日」，年份从月份分节标题取（快手式）。"""
        arts = self._extract(self.TABLE_HTML, "https://www.streamlake.com/document/x")
        self.assertGreaterEqual(len(arts), 3, "表格行要能提取出来")
        self.assertIn("2026-08-14", {a.date for a in arts}, "年份必须从月份分节标题取到")
        self.assertNotIn("更新时间", {a.title for a in arts}, "表格表头不得变成条目")
        self.assertTrue(all(a.date for a in arts), "每一行都要有日期")

    def test_adjacent_heading_after_date(self):
        """「日期 + 其后相邻标题」（商汤式：h2 出现在 h3 分节之后，层级是倒的）。"""
        arts = self._extract(self.ADJACENT_HTML, "https://www.sensecore.cn/help/x")
        self.assertGreaterEqual(len(arts), 3)
        got = {a.date: a.title for a in arts}
        self.assertEqual(got.get("2025-07-23"), "【模型更新】发布最新版本日日新-融合模态模型 V6.5")
        self.assertNotIn("release-202507", {a.title for a in arts},
                         "分节标题（release-YYYYMM）不得变成条目名")


class TestChineseDateFormat(unittest.TestCase):
    """「2026 年 7 月 31 日」这种**单位两侧都有空格**的写法，所有日期解析处都要认。

    Regression: 6 处日期正则里只有 `_PROMO_DATE_PAT` 写成 `\\s*[-/年.]\\s*`，其余写成
    `[-/年.]\\s?`（只容忍单位**后**的空格），于是带前导空格的写法在别处全部漏判 ——
    MiniMax 发布说明的目录锚点（`<a href="#2026-年-7-月-31-日">2026 年 7 月 31 日</a>`）
    因此没被「标题就是日期」的守卫拦住，**每次巡检都往归档里加 8 条日期标题的垃圾**。
    """

    SAMPLES = ("2026 年 7 月 31 日", "2026年7月31日", "2026-07-31", "2026/7/31", "2026.7.31")

    def test_inline_date_re_accepts_spaced_chinese(self):
        for s in self.SAMPLES:
            self.assertTrue(crawler_llm_intel._INLINE_DATE_RE.search(s), f"未识别: {s}")

    def test_normalize_feed_date_accepts_spaced_chinese(self):
        for s in self.SAMPLES:
            self.assertEqual(crawler_llm_intel.normalize_feed_date(s), "2026-07-31",
                             f"未归一化: {s}")

    def test_promo_date_pattern_accepts_spaced_chinese(self):
        """促销到期判定用的是同一套写法，不能只有它一个认。"""
        for s in self.SAMPLES:
            self.assertTrue(crawler_llm_intel._PROMO_DATE_PAT.search(s), f"未识别: {s}")

    def _extract(self, anchors):
        rows = "".join(
            f'<a href="https://x.example/docs/release-notes/models#{u}">{t}</a>'
            for t, u in anchors)
        html = f"<html><body>{rows}</body></html>"
        _t, _ti, _f, links, headings = crawler_llm_intel.parse_html(
            html, "https://x.example/docs/release-notes/models")
        page = crawler_llm_intel.PageResult(
            url="https://x.example/docs/release-notes/models", stype="changelog",
            ok=True, final_url="https://x.example/docs/release-notes/models",
            links=links, link_headings=headings)
        return crawler_llm_intel.extract_articles_from_page(page)

    def test_date_only_titles_are_dropped(self):
        """整条标题就是日期的（含只写年月的）不得成为条目。"""
        arts = self._extract([
            ("2026 年 7 月 31 日", "d1"),
            ("2026 年 4 月", "d2"),
            ("2026-07-31", "d3"),
            ("MiniMax H3 正式发布，支持多模态视频生成", "real"),
        ])
        titles = [a.title for a in arts]
        self.assertEqual(len(arts), 1, f"只应留下真实标题，实际: {titles}")
        self.assertIn("MiniMax H3", titles[0])

    def test_date_prefix_is_stripped_and_kept_as_article_date(self):
        """日期粘在标题前面时：日期归到条目上，标题剥干净。"""
        arts = self._extract([("2026 年 7 月 31 日 MiniMax H3 正式发布", "d")])
        self.assertEqual(len(arts), 1)
        self.assertEqual(arts[0].date, "2026-07-31")
        self.assertNotIn("2026", arts[0].title)


class TestSinglePageAnchorIdentity(unittest.TestCase):
    """单页文档站的条目是「同页不同 `#锚点`」，**fragment 才是它们的身份**。

    Regression: 归档增量合并与合并流去重都用了 `_norm_url`（去掉 fragment）做键，于是同一页的
    N 条折叠成一个键 —— 归档会把历史条目误判成「本次已抓到」而**丢弃**（实测 3 条只重抓到 1 条时
    归档从 3 条掉到 1 条，违反「归档只增不减」），合并流也会把同页条目吃掉（通义 100 条只剩 1 条）。
    `extract_articles_from_page` 与 `collect_news_articles` 早就按 fragment 处理，唯独这两处漏了。
    """

    def test_article_key_keeps_fragment(self):
        self.assertEqual(crawler_llm_intel._article_key("https://x.example/docs#a"),
                         "https://x.example/docs#a")
        self.assertNotEqual(crawler_llm_intel._article_key("https://x.example/docs#a"),
                            crawler_llm_intel._article_key("https://x.example/docs#b"),
                            "同页不同锚点必须是不同的身份键")
        # 仍然做常规规范化：host 小写、去末尾斜线
        self.assertEqual(crawler_llm_intel._article_key("https://X.example/docs/#a"),
                         "https://x.example/docs#a")

    def test_archive_merge_keeps_same_page_anchors(self):
        with tempfile.TemporaryDirectory() as tmp:
            news_dir = Path(tmp) / "llm-news"
            news_dir.mkdir(parents=True)
            (news_dir / "vendor_a.md").write_text(
                "# t\n\n## 全部文章（共 3 篇，按日期倒序；无日期条目列于最后）\n\n"
                "1. [第一篇](https://x.example/docs#a)（2026-01-03）\n"
                "2. [第二篇](https://x.example/docs#b)（2026-01-02）\n"
                "3. [第三篇](https://x.example/docs#c)（2026-01-01）\n", encoding="utf-8")
            v = crawler_llm_intel.VendorIntel(
                vendor_id="vendor_a", brand="A", homepage="", products=[])
            # 本次只重抓到 1 条（页面改版只剩一条）
            v.all_news_articles = [crawler_llm_intel.Article(
                title="第一篇", url="https://x.example/docs#a", date="2026-01-03")]
            v.news_articles = v.all_news_articles
            _n, total, _c = crawler_llm_intel.write_news_archives(
                news_dir, [v], clean_removed=False)
            self.assertEqual(total, 3,
                             "同页锚点的历史条目被当成「已抓到」丢掉了 —— 归档必须只增不减")

    def test_merged_feed_keeps_same_page_anchors(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "feeds"
            v = crawler_llm_intel.VendorIntel(
                vendor_id="vendor_b", brand="B", homepage="", products=[])
            v.all_news_articles = [
                crawler_llm_intel.Article(title="第一篇", url="https://y.example/docs#a",
                                          date="2026-01-03"),
                crawler_llm_intel.Article(title="第二篇", url="https://y.example/docs#b",
                                          date="2026-01-02"),
                crawler_llm_intel.Article(title="第三篇", url="https://y.example/docs#c",
                                          date="2026-01-01"),
            ]
            crawler_llm_intel.write_rss_feeds(out, [v])
            merged = (out / "llm-news-all.xml").read_text(encoding="utf-8")
            self.assertEqual(merged.count("<item>"), 3,
                             "合并流把同页不同锚点的条目去重成一条了")


class TestChangelogTitleIsNameOnly(unittest.TestCase):
    """更新日志条目的标题**只取名称**，不把卡片正文拼进来。

    两种结构都构造过 `名称：描述` 的长标题（阿里云百炼 100/100、MiniMax 9/30 的条目如此），
    中位 145 字 —— 订阅列表里根本没法扫读。正文点进链接就能看到，不必塞进标题。
    """

    def test_structure2_card_title_only(self):
        """结构 2：日期 id 的 h2 + Mintlify 卡片（card-title / card-content）。"""
        html = """
        <html><body>
        <h2 id="2026-07-31">2026 年 7 月 31 日</h2>
        <div data-component-part="card">
          <h3 data-component-part="card-title">MiniMax H3</h3>
          <div data-component-part="card-content">新一代开放通用多模态视频模型，面向由文本、图像、
          视频与声音共同构成的多模态上下文，统一理解创作意图。</div>
        </div>
        </body></html>"""
        page = crawler_llm_intel.PageResult(
            url="https://p.example/docs/release-notes/models", stype="changelog", ok=True,
            final_url="https://p.example/docs/release-notes/models", raw=html)
        arts = crawler_llm_intel.extract_changelog_sections(page)
        self.assertEqual(len(arts), 1)
        self.assertEqual(arts[0].title, "MiniMax H3", "标题不得拼上卡片正文")
        self.assertEqual(arts[0].date, "2026-07-31")

    def test_structure3_table_id_only(self):
        """结构 3：帮助中心表格行（类型 | 时间 | <code>模型ID</code> | 功能说明）。"""
        rows = "".join(
            f'<tr><td><p>文本生成</p></td><td><p>2026-09-1{i}</p></td>'
            f'<td><p><code>model-{i}</code></p></td>'
            f'<td><p>这是第 {i} 个模型的详细功能说明，长度足够通过校验。</p></td></tr>'
            for i in range(1, 5))
        html = f'<html><body><table><tbody>{rows}</tbody></table></body></html>'
        page = crawler_llm_intel.PageResult(
            url="https://q.example/zh/docs/newly-released-models", stype="updates", ok=True,
            final_url="https://q.example/zh/docs/newly-released-models", raw=html)
        arts = crawler_llm_intel.extract_changelog_sections(page)
        self.assertEqual(len(arts), 4)
        for i, a in enumerate(arts, 1):
            # 只写模型 ID（`qwen3.8-max-0902`）在订阅列表里零信息量 —— 2026-09-22
            # 数据审计实测线上 43 条这样。改为「模型 ID + 说明首句」：既保留可检索的
            # ID，又能看出这是什么模型；但不能把整段说明拼进来（中位 145 字），故取首句。
            self.assertEqual(
                a.title, f"model-{i}：这是第 {i} 个模型的详细功能说明，长度足够通过校验")
            self.assertEqual(a.date, f"2026-09-1{i}")
            self.assertTrue(a.url.endswith(f"#model-{i}"), "URL 仍用模型 ID 做锚点")


class TestNewsIntelFilter(unittest.TestCase):
    """动态条目的「情报过滤」—— 2026-09-22 数据审计后**按厂商规则化**。

    背景：线上 3376 条里 77% 来自公司博客 / 社区技术博客（`openai.com/index/*` 的
    客户案例、融资、政策、教程；`huggingface.co/blog` 的社区技术文章），
    其中 228 条根本不是一篇文章。

    判据按**信号组**组织，因为同一个词在不同厂商的源里含义不同：
    `fine-tuning` / `embedding` 在 openai 的 news 里是 API 变更信号，
    在 huggingface 的 blog 里却是技术教程的标题词。
    """

    def test_unlisted_vendor_is_never_filtered(self):
        """未列入规则的厂商（变更日志型源）不过滤。"""
        for t in ("Cooley 如何利用 ChatGPT 加速 IPO 工作",
                  "How X uses ChatGPT to cut costs"):
            self.assertTrue(crawler_llm_intel.is_intel_news("baseten", t), t)

    def test_model_release_and_api_change_kept(self):
        for t in ("Introducing GPT-5.5",
                  "GPT-6 Astra: A new generation of intelligence",
                  "GLM-5.2: Built for Long-Horizon Tasks",
                  "Retiring GPT-4o, GPT-4.1, GPT-4.1 mini, and OpenAI o4-mini in ChatGPT",
                  "New usage analytics and updated spend controls for enterprises",
                  "Advancing voice intelligence with new models in the API"):
            self.assertTrue(crawler_llm_intel.is_intel_news("openai", t), t)

    def test_customer_story_dropped_even_with_release_word(self):
        """客户案例优先于发布信号 —— `cuts launch hours` 里的 launch 是名词。"""
        self.assertFalse(crawler_llm_intel.is_intel_news(
            "openai", "Stampli cuts launch hours by 68% using ChatGPT Work"))
        self.assertFalse(crawler_llm_intel.is_intel_news(
            "openai", "How Cooley is accelerating IPO work with ChatGPT"))

    def test_company_news_and_marketing_dropped(self):
        for t in ("OpenAI appoints Dali Rajic as Chief Revenue Officer",
                  "Introducing the Intelligence Age",
                  "Reimagining advertising with AI",
                  "Expanding AI access and cyber defense for federal, state, and local governments"):
            self.assertFalse(crawler_llm_intel.is_intel_news("openai", t), t)

    def test_huggingface_uses_release_wide_not_strong(self):
        """HF 的 blog 里 `fine-tuning` 是技术教程的标题词，不该当情报。"""
        self.assertFalse(crawler_llm_intel.is_intel_news(
            "huggingface",
            "Fine-tuning a 350M Model for Better Structured Outputs in 100 GRPO Steps"))
        self.assertTrue(crawler_llm_intel.is_intel_news(
            "huggingface", "Welcome Llama 4 Maverick & Scout on Hugging Face"))
        self.assertTrue(crawler_llm_intel.is_intel_news(
            "huggingface", "Introducing Storage Buckets on the Hugging Face Hub"))

    def test_model_listing_on_platform_kept(self):
        """「某模型 now available on 平台」是上架情报，不要求命中产品名词表。"""
        self.assertTrue(crawler_llm_intel.is_intel_news(
            "modal", "Qwen3.8-2.4T-A95B now available on Modal"))
        self.assertTrue(crawler_llm_intel.is_intel_news(
            "modal", "Product updates: VM sandboxes, low-latency routing, RBAC, and more"))

    def test_collect_news_articles_applies_filter(self):
        """过滤在 collect_news_articles 里生效，且判据用的是**原文标题**。"""
        xml = ('<?xml version="1.0"?><rss version="2.0"><channel>'
               '<item><title>Introducing GPT-5.5</title>'
               '<link>https://x.example/a</link>'
               '<pubDate>Mon, 01 Sep 2026 00:00:00 +0000</pubDate></item>'
               '<item><title>How Cooley is accelerating IPO work with ChatGPT</title>'
               '<link>https://x.example/b</link>'
               '<pubDate>Tue, 02 Sep 2026 00:00:00 +0000</pubDate></item>'
               '</channel></rss>')
        page = crawler_llm_intel.PageResult(
            url="https://x.example/feed.xml", stype="feed", ok=True,
            final_url="https://x.example/feed.xml", raw=xml)
        intel = crawler_llm_intel.VendorIntel(
            vendor_id="openai", brand="OpenAI", homepage="", products=[])
        intel.news_pages = [page]
        crawler_llm_intel.collect_news_articles(intel, session=None)
        self.assertEqual([a.title for a in intel.all_news_articles],
                         ["Introducing GPT-5.5"])
        self.assertEqual(intel.news_filtered, 1)


class TestRetiredNewsSource(unittest.TestCase):
    """已废弃新闻源的历史条目要收口。

    归档是「增量合并、只增不减」的 —— 从 yaml 删掉一个源之后，它的历史条目会一直留在
    `llm-news/*.md` 与单厂商 feed 里。实例：`cloud.google.com/blog/products/`
    （Google Cloud 通用 AI 博客：Gartner 魔力象限、印度板球转播、I/O 大会速览）
    于 2026-09-18 从 yaml 移除，但归档里仍有 11 条残留。
    """

    def test_retired_url_recognised(self):
        self.assertTrue(crawler_llm_intel._is_retired_news_url(
            "https://cloud.google.com/blog/products/ai-machine-learning/the-new-gemini"))
        self.assertFalse(crawler_llm_intel._is_retired_news_url(
            "https://ai.google.dev/gemini-api/docs/changelog#09-17-2026"))

    def test_archived_articles_from_retired_source_are_dropped(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            (out / "v.md").write_text(
                "# V 文章归档\n\n> 由脚本整理\n\n"
                "## 全部文章（共 2 篇，按日期倒序；无日期条目列于最后）\n\n"
                "1. [真条目](https://ai.google.dev/gemini-api/docs/changelog#a)（2026-09-17）\n"
                "2. [云博客残留](https://cloud.google.com/blog/products/ai-machine-learning/x)\n",
                encoding="utf-8")
            intel = crawler_llm_intel.VendorIntel(
                vendor_id="v", brand="V", homepage="", products=[])
            with mock.patch.object(crawler_llm_intel, "translate_to_zh", lambda t: t):
                # clean_removed=False：本用例的 intel 没有新抓条目，
                # 传 True 会把整个归档当「已下线厂商」删掉（那是另一条逻辑）
                crawler_llm_intel.write_news_archives(out, [intel], clean_removed=False)
            text = (out / "v.md").read_text(encoding="utf-8")
            self.assertIn("真条目", text, "对口的条目必须保留")
            self.assertNotIn("云博客残留", text, "已废弃源的历史条目应被清理")


class TestNewsTitleQuality(unittest.TestCase):
    """抓取条目的标题质量 —— 2026-09-22 数据审计发现的问题逐类冻结。

    审计线上 3376 条，其中 228 条「根本不是一篇文章」：digitalocean 100 条标题=日期、
    ppio/aliyun 88 条标题=模型 ID、groq 4 条标题=GitHub PR 号、其余为导航文案。
    这里为每一类修好后的行为加守卫，避免以后静默退化。
    """

    def test_feed_date_meta_title_uses_description(self):
        """RSS 标题是「日期 + 栏目」时（DigitalOcean 发布记录），改用 description 首句。"""
        xml = (
            '<?xml version="1.0"?><rss version="2.0"><channel><item>'
            '<title>17 September 2026 (postgresql, mysql)</title>'
            '<link>https://docs.example/notes/2026/dbaas-advanced-edition-ga/</link>'
            '<pubDate>Thu, 17 Sep 2026 00:00:00 +0000</pubDate>'
            '<description>PostgreSQL Advanced Edition and MySQL Advanced Edition '
            'managed database clusters are now generally available. To create a '
            'cluster, see the docs.</description>'
            '</item></channel></rss>')
        arts = crawler_llm_intel.parse_feed_xml(
            xml, "https://docs.example/release-notes/index.xml")
        self.assertEqual(len(arts), 1)
        self.assertEqual(
            arts[0].title,
            "PostgreSQL Advanced Edition and MySQL Advanced Edition managed "
            "database clusters are now generally available")
        self.assertEqual(arts[0].date, "2026-09-17")

    def test_feed_date_title_without_description_is_dropped(self):
        """拿不到真标题、只剩日期时丢弃 —— 产出纯日期条目等于什么都没说。"""
        xml = ('<?xml version="1.0"?><rss version="2.0"><channel><item>'
               '<title>2026 年 9 月 17 日</title>'
               '<link>https://docs.example/notes/2026/x/</link>'
               '</item></channel></rss>')
        self.assertEqual(
            crawler_llm_intel.parse_feed_xml(xml, "https://docs.example/f.xml"), [])

    def test_commit_feed_title_cleaned(self):
        """GitHub 提交式 feed（Groq 的 changelog 仓库）标题是 commit message。"""
        xml = (
            '<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">'
            '<entry><title>Add prompt caching (#14)</title>'
            '<link rel="alternate" href="https://github.com/groq/groq-changelog/commit/aaa"/>'
            '<updated>2025-08-20T00:00:00Z</updated></entry>'
            '<entry><title>chore: GitHub Terraform: Create/Update workflows (#20)</title>'
            '<link rel="alternate" href="https://github.com/groq/groq-changelog/commit/bbb"/>'
            '<updated>2025-08-21T00:00:00Z</updated></entry>'
            '<entry><title>yay first ever groq changelog entry (#1)</title>'
            '<link rel="alternate" href="https://github.com/groq/groq-changelog/commit/ccc"/>'
            '<updated>2025-08-22T00:00:00Z</updated></entry>'
            '</feed>')
        arts = crawler_llm_intel.parse_feed_xml(
            xml, "https://github.com/groq/groq-changelog/commits/main.atom")
        # 去 PR 号、去 conventional 前缀；纯维护性提交丢弃
        self.assertEqual([a.title for a in arts], ["Add prompt caching"])

    def test_model_id_anchor_dropped(self):
        """纯 `vendor/model` 形态的锚点（PPIO 模型清单页）是目录条目，丢弃。"""
        base = "https://p.example/docs/announcement/changelog-llm"
        links = [
            (base + "#qwen/qwen3-14b", "qwen/qwen3-14b"),
            (base + "#kat-coder", "kat-coder"),
            (base + "#a1", "部分多模态模型计划下线：Qwen-Image 等模型将下线"),
        ]
        page = crawler_llm_intel.PageResult(
            url=base, stype="updates", ok=True, final_url=base,
            raw="<html><body>x</body></html>", text="", links=links,
            link_headings=["", "", ""])
        arts = crawler_llm_intel.extract_articles_from_page(page, max_items=10)
        titles = [a.title for a in arts]
        self.assertNotIn("qwen/qwen3-14b", titles, "纯模型 ID 锚点应被丢弃")
        self.assertTrue(any("部分多模态模型计划下线" in t for t in titles), "真公告保留")

    def test_list_item_sub_bullets_dropped(self):
        """结构 5 里，公告的子要点（纯中文短词 + strong 后紧跟分隔符）不是条目。

        PPIO 线上实测：「Playground 支持 Function Call」那条公告之下还有
        「智能交互 ：在对话页面…」「三大优势 ： ⚡ 更强时效性」等 li，
        被当成独立条目后会产出 4 条营销短语。
        """
        html = """
        <html><body>
          <h2 id="2025年7月14日-7月18日">2025年7月14日-7月18日</h2>
          <ul>
            <li><strong>Playground 支持 Function Call</strong> 为了更好地满足用户需求，
                我们在 Playground 中正式推出 Function Call 功能。</li>
            <li><strong>Kimi K2 模型上线</strong> 新增模型。</li>
            <li><strong>计费规则调整</strong> 按量计费说明更新。</li>
            <li><strong>智能交互</strong> ：在对话页面输入与主题相关的问题。</li>
            <li><strong>三大优势</strong> ： ⚡ 更强时效性 - 实时获取最新信息。</li>
            <li><strong>更低幻觉率</strong> - 基于真实数据源，减少错误信息。</li>
          </ul>
        </body></html>"""
        page = crawler_llm_intel.PageResult(
            url="https://p.example/docs/announcement/changelog-llm", stype="updates",
            ok=True, final_url="https://p.example/docs/announcement/changelog-llm",
            raw=html)
        titles = [a.title for a in crawler_llm_intel.extract_changelog_sections(page)]
        for keep in ("Playground 支持 Function Call", "Kimi K2 模型上线", "计费规则调整"):
            self.assertIn(keep, titles, f"{keep} 是真条目，必须保留")
        for noise in ("智能交互", "三大优势", "更低幻觉率"):
            self.assertNotIn(noise, titles, f"{noise} 是子要点，不是条目")


class TestFeedLimitedPageFull(unittest.TestCase):
    """合并流**默认不限制**；页面仍读更省的全量索引。

    合并流曾经限 200 条，理由是「全量约 1.2 MB 会让阅读器吃力」—— **那个理由站不住**：
    GitHub Pages 用 gzip 传输（线上实测 `Content-Encoding: gzip`），全量 2575 条
    （XML 1124 KB）压缩后只有 131 KB。当时的判断看的是未压缩体积。
    现在 `RSS_MERGED_LIMIT = 0` = 不限制，订阅者一次就能拿到全部历史。

    页面仍读 `articles.json` 而不是合并流，但理由换了：**体积只有一半**（520 KB vs 1124 KB）、
    免去 XML 解析，而且**标题不截断、还带原文标题**（feed 里为了列表可读截到 60 字）。
    """

    def _intel(self, n):
        v = crawler_llm_intel.VendorIntel(vendor_id="v", brand="V", homepage="", products=[])
        v.all_news_articles = [
            crawler_llm_intel.Article(title=f"标题{i}", url=f"https://v.example/news/{i}",
                                      date=f"2026-01-{i:02d}")
            for i in range(1, n + 1)
        ]
        return v

    def test_merged_feed_is_unlimited_by_default(self):
        """默认（RSS_MERGED_LIMIT = 0）应收录全部有日期的条目。"""
        self.assertEqual(crawler_llm_intel.RSS_MERGED_LIMIT, 0,
                         "合并流默认不限制；要限流请显式传 merged_limit")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "feeds"
            crawler_llm_intel.write_rss_feeds(out, [self._intel(5)])
            merged = (out / "llm-news-all.xml").read_text(encoding="utf-8")
            self.assertEqual(merged.count("<item>"), 5, "默认不得截断")
            # 文案也要跟着上限走，别写死「最近 N 条」
            self.assertIn("收录全部有日期的条目",
                          crawler_llm_intel.merged_scope_text(
                              crawler_llm_intel.RSS_MERGED_LIMIT))

    def test_explicit_limit_still_works(self):
        """显式给上限时仍生效（`--rss-limit` 与全量索引不受影响）。"""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "feeds"
            crawler_llm_intel.write_rss_feeds(out, [self._intel(5)], merged_limit=2)
            merged = (out / "llm-news-all.xml").read_text(encoding="utf-8")
            self.assertEqual(merged.count("<item>"), 2, "显式上限应生效")
            data = json.loads((out / "articles.json").read_text(encoding="utf-8"))
            self.assertEqual(data["count"], 5, "全量索引不受合并流上限约束")
            self.assertEqual(len(data["articles"]), 5)
            self.assertEqual(data["fields"][:4], ["title", "url", "vendor", "date"])
            dates = [r[3] for r in data["articles"]]
            self.assertEqual(dates, sorted(dates, reverse=True), "有日期的应按日期倒序排在前")

    def test_page_reads_the_full_index(self):
        """页面读 articles.json（体积只有合并流一半、标题不截断、带原文标题）。"""
        page = (Path(__file__).resolve().parent / "docs" / "index.html").read_text(
            encoding="utf-8")
        self.assertIn("feeds/articles.json", page,
                      "浏览页要读全量索引（更小、标题完整、带原文标题）")
        self.assertIn("feeds/llm-news-all.xml", page,
                      "合并流仍是订阅地址与索引缺失时的兜底，不能删")


class TestTranslationSkipsIdentifiers(unittest.TestCase):
    """模型 id 这类标识符不该送去翻译。

    Regression: Google 把 `qwen/qwen3-coder-30b-a3b-instruct：—` 译成
    `qwen/qwen3-coder-30b-a3b-指令：—` —— **模型名被改掉**，比不翻更糟。
    已发布产物里没坏，只是因为那次翻译恰好失败（回退原文），属于侥幸。
    """

    SAMPLES = (
        "qwen/qwen3-coder-30b-a3b-instruct：—",
        "qwen/qwen3-next-80b-a3b-instruct：—",
        "gpt-4.1-mini",
        "claude-sonnet-5",
    )

    # 含**型号**（字母紧邻数字）的标题：宁可留英文，也不翻坏品牌名。
    # 实测 `MiniMax H3` → `迷你最大H3`、`qwen3.8-omni-flash` → `qwen3.8-全向闪存`。
    SAMPLES_WITH_MODEL_NUMBER = (
        "MiniMax H3",
        "qwen3.8-omni-flash",
        "Announcing v2 of our platform",
    )

    def test_identifier_like_text_is_returned_unchanged(self):
        for s in self.SAMPLES:
            self.assertEqual(provider_profiles.translate_to_zh(s), s,
                             f"标识符被改写了: {s}")

    def test_titles_with_model_number_are_returned_unchanged(self):
        for s in self.SAMPLES_WITH_MODEL_NUMBER:
            self.assertEqual(provider_profiles.translate_to_zh(s), s,
                             f"含型号的标题被翻译了（品牌名有被改写风险）: {s}")

    # 纯专名短标题：Mistral 线上实测 `Magistral` → 「公路」、`Pixtral Large`
    # → 「像素大号」、`Le Chat` → 「猫」、`Codestral` → 「共纹」。
    SAMPLES_PROPER_NOUN = (
        "Magistral",
        "Pixtral Large",
        "Le Chat",
        "Codestral",
        "Mistral NeMo",
        "Au Large",
    )

    def test_proper_noun_titles_are_returned_unchanged(self):
        for s in self.SAMPLES_PROPER_NOUN:
            self.assertEqual(provider_profiles.translate_to_zh(s), s,
                             f"品牌 / 产品名被汉化了: {s}")

    def test_sentence_like_short_titles_are_not_treated_as_proper_nouns(self):
        """首词是常见英文词说明是句子（`Introducing Mistral`），不能当专名放过。"""
        for s in ("Introducing Mistral", "Large Enough", "New models", "Cheaper, Better"):
            self.assertFalse(provider_profiles._is_proper_noun_title(s), s)


class TestDateOnlyTitleIsNotATitle(unittest.TestCase):
    """整条标题就是日期 / 数字的（含**只写年月**的 `2026年9月`）不是标题。

    Regression: 这类标题来自日期分节与目录锚点。判据原先在两处各写一遍且**都漏了
    「只写年月」的形态**，于是 Kimi 平台发布记录抓到的 24 条全是「2026年9月」这种月份名
    —— 看着像动态、实际一条内容都没有。抽成 `_is_date_only_title` 后三处共用。
    """

    def test_recognises_date_only_forms(self):
        for s in ("2026 年 7 月 31 日", "2026年9月", "2026-07-31", "2026 年 4 月", "2026"):
            self.assertTrue(crawler_llm_intel._is_date_only_title(s), s)

    def test_real_titles_are_not_dates(self):
        for s in ("GLM-5.3 新一代旗舰模型上线", "MiniMax H3", "2026 年发布计划：模型上下线", ""):
            self.assertFalse(crawler_llm_intel._is_date_only_title(s), s)

    def test_update_container_uses_next_line_when_first_line_is_a_month(self):
        """Kimi 式 update-container：第一行是月份，真标题在下一行。"""
        html = """
        <html><body>
          <div class="x update-container" id="2026年9月">
            <p>2026年9月</p>
            <p>🤖 Kimi 托管智能体（Hosted Agents）Beta 上线</p>
            <p>在模型推理 API 之上，我们封装了 Kimi Durable Harness。</p>
          </div>
          <div class="x update-container" id="2026年8月">
            <p>2026年8月</p>
            <p>kimi-k2.5 与 moonshot-v1 全系列模型上线</p>
          </div>
          <div class="x update-container" id="2026年7月">
            <p>2026年7月</p>
            <p>Kimi K3 上线开放平台 API</p>
          </div>
        </body></html>"""
        page = crawler_llm_intel.PageResult(
            url="https://k.example/docs/changelog", stype="changelog", ok=True,
            final_url="https://k.example/docs/changelog", raw=html)
        arts = crawler_llm_intel.extract_changelog_sections(page)
        self.assertEqual(len(arts), 3)
        titles = [a.title for a in arts]
        self.assertNotIn("2026年9月", titles, "月份名不得当标题")
        self.assertTrue(any("Kimi 托管智能体" in t for t in titles), titles)
        self.assertEqual([a.date for a in arts], ["2026-09-01", "2026-08-01", "2026-07-01"])


    def test_date_section_with_child_headings(self):
        """结构 4：日期分节 + 更深的子标题条目（分节标题本身不是条目）。"""
        html = """
        <html><body>
          <h2 id="2026年9月">2026年9月</h2>
          <h3 id="a">条目 A：新模型上线</h3><p>说明一</p>
          <h3 id="b">条目 B：计费调整</h3><p>说明二</p>
          <h3 id="c">条目 C：SDK 更新</h3><p>说明三</p>
          <h2 id="2026年8月">2026年8月</h2>
          <h3 id="d">条目 D：更早的一条</h3><p>说明四</p>
        </body></html>"""
        page = crawler_llm_intel.PageResult(
            url="https://s.example/docs/changelog", stype="changelog", ok=True,
            final_url="https://s.example/docs/changelog", raw=html)
        arts = crawler_llm_intel.extract_changelog_sections(page)
        self.assertEqual([a.title for a in arts],
                         ["条目 A：新模型上线", "条目 B：计费调整", "条目 C：SDK 更新",
                          "条目 D：更早的一条"])
        self.assertEqual([a.date for a in arts],
                         ["2026-09-01", "2026-09-01", "2026-09-01", "2026-08-01"])


    def test_date_section_with_list_items(self):
        """结构 5：日期分节 + 列表项条目（PPIO 发版记录：`li` 的首个 `<strong>` 才是标题）。

        只取分节标题旁的栏目名（「模型调整 🔧」）等于把内容丢了。
        """
        html = """
        <html><body>
          <h2 id="2026年9月1日-9月4日">2026年9月1日-9月4日</h2>
          <span><strong>模型调整</strong> 🔧</span>
          <ul>
            <li><span><strong>部分多模态模型计划下线</strong></span>
                <span>Qwen-Image、Wan 2.5 等将于 2026 年 9 月 30 日下线。</span></li>
            <li><span><strong>新模型上架</strong></span><span>新增若干模型。</span></li>
          </ul>
          <h2 id="2026年8月25日-8月29日">2026年8月25日-8月29日</h2>
          <span><strong>功能优化</strong> 🔧</span>
          <ul>
            <li><span><strong>控制台改版</strong></span><span>说明。</span></li>
          </ul>
        </body></html>"""
        page = crawler_llm_intel.PageResult(
            url="https://p.example/docs/announcement/changelog", stype="updates", ok=True,
            final_url="https://p.example/docs/announcement/changelog", raw=html)
        arts = crawler_llm_intel.extract_changelog_sections(page)
        self.assertEqual([a.title for a in arts],
                         ["部分多模态模型计划下线", "新模型上架", "控制台改版"])
        self.assertEqual([a.date for a in arts], ["2026-09-01", "2026-09-01", "2026-08-25"])
        self.assertNotIn("模型调整", [a.title for a in arts], "栏目名不得当标题")
        self.assertEqual(len({a.url for a in arts}), 3, "每个 li 要有各自稳定的 URL")


class TestChangelogDateIdFormats(unittest.TestCase):
    """日期标题的 id 有 `YYYY-MM-DD` 与 `MM-DD-YYYY` 两种写法，都要认。

    Regression: 只认前者时，Mintlify 系文档站（如 Gemini API changelog 的
    `id="09-17-2026"`）解析不出日期 → 结构 2 的 `if not norm_date: continue` 把
    **整页 113 条全部丢弃**，看起来像「这页没有内容 / 是 JS 渲染」，其实是日期格式没认。
    """

    def _extract(self, heading_id, title):
        html = (f'<html><body><h2 id="{heading_id}">{title}</h2>'
                f'<ul><li><p>这是这一条变更的说明，长度足够通过校验。</p></li></ul>'
                f'</body></html>')
        page = crawler_llm_intel.PageResult(
            url="https://x.example/docs/changelog", stype="changelog", ok=True,
            final_url="https://x.example/docs/changelog", raw=html)
        return crawler_llm_intel.extract_changelog_sections(page)

    def test_year_first_id(self):
        arts = self._extract("2026-09-17", "2026-09-17")
        self.assertEqual(len(arts), 1)
        self.assertEqual(arts[0].date, "2026-09-17")

    def test_month_first_id(self):
        """Gemini API changelog 的形态：id="09-17-2026"。"""
        arts = self._extract("09-17-2026", "September 17, 2026")
        self.assertEqual(len(arts), 1, "MM-DD-YYYY 的 id 不得被整条丢弃")
        self.assertEqual(arts[0].date, "2026-09-17")

    def test_month_first_id_rejects_impossible_dates(self):
        """月份/日做范围校验：`model-25-99-2026` 这种不该被当日期。"""
        arts = self._extract("25-99-2026", "not a date")
        self.assertEqual(arts, [])


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

    def test_readme_links_into_docs_use_absolute_urls(self):
        """README 里指向 `docs/` 的**链接**必须是绝对地址，不能用相对路径。

        Regression: 相对路径在 github.com 上打开的是**源码视图** —— `docs/index.html`
        显示 HTML 源码、`docs/feeds/*.xml` 显示 XML 源码（而 `raw.githubusercontent.com`
        返回 `text/plain`，根本不能当订阅源）。读者点「网页浏览 / 一键订阅」看到的是一堆
        源码，而不是能用的页面。
        **图片不受影响**（GitHub 会正常渲染相对路径的图片），所以只校验链接、不校验 `![]()`。
        """
        content = self.readme_path.read_text(encoding="utf-8")
        without_images = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", content)
        bad = [target for _text, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", without_images)
               if target.split("#")[0].strip().startswith("docs/")]
        self.assertEqual(
            bad, [],
            f"这些 README 链接用了相对路径，在 GitHub 上只会打开源码视图: {bad}")

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
        self.assertGreaterEqual(
            len(yaml_vendors), 60,
            "厂商总数跌破 60：疑似误删（本阈值是防误删下限，不钉死精确值——"
            "精确家数由 yaml 与上方双向集合校验共同保证一致）")


class TestGuideRendering(unittest.TestCase):
    """白嫖攻略：过期促销自动过滤、懒人首选块渲染。"""

    def test_vendors_without_guide_meta_are_known_deliberate_omissions(self):
        """没有 GUIDE_META 的厂商会被攻略**静默跳过** —— 名单冻结，新增厂商必须显式决定。

        攻略按 `GUIDE_META` 过滤：没条目的厂商直接 `continue`，**不会报错**。于是
        「新增一家有免费额度的厂商、忘了写 GUIDE_META」＝ 它从攻略里消失，而攻略自称
        「与下方厂商总表同源」。这类静默漏项只能靠守卫拦（2026-09-18 就是靠人工比对
        才发现 4 家有免费能力却不在攻略里）。

        名单里每家都是**有意不进攻略**的，理由见注释。要新增厂商时：该进攻略就补
        `GUIDE_META`（+ 档案的 `tier_caveats`），不该进就把 id 加进来并写明原因。
        """
        KNOWN_OMITTED = {
            # 官方明确「无免费额度 / 无赠送」（档案里有一手原文）
            "openai", "xai_grok", "deepseek", "minimax", "together_ai", "deepinfra",
            # 存疑或已停服：条目保留用于跟踪，但不应作为可用免费额度来源（README 已如实标注）
            "lingyiwanwu_01ai", "kunlun_tiangong", "ncompass", "mara",
            # 免费权益无法从官方公开页核实（宁缺毋假）
            "china_mobile_moma", "zhinao_360", "dmxapi",
            # 官方称「新用户有少量免费测试额度」但**金额不公开**，暂不列（待定，见项目记忆）
            "anthropic",
        }
        root = Path(__file__).resolve().parent
        vendors, _sources = crawler_llm_intel.parse_yaml(root / "llm-intel.yaml")
        self.assertTrue(vendors, "没解析到厂商 —— 解析失配，先修测试本身")
        missing = {v["id"] for v in vendors} - set(provider_profiles.GUIDE_META)
        new = sorted(missing - KNOWN_OMITTED)
        self.assertEqual(
            new, [],
            f"这些厂商没有 GUIDE_META，会被攻略静默跳过。该进攻略就补 GUIDE_META，"
            f"不该进就加进 KNOWN_OMITTED 并写明原因: {new}")
        stale = sorted(KNOWN_OMITTED & set(provider_profiles.GUIDE_META))
        self.assertEqual(
            stale, [],
            f"这些厂商已经有 GUIDE_META 了，该从 KNOWN_OMITTED 移除（名单过时了）: {stale}")

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

    def test_vendor_rank_covers_all_vendors(self):
        """热度排序表 `VENDOR_RANK` 必须**双向**对齐真实厂商 id。

        浏览页的厂商标签与订阅列表都按这张表排序。表里打错一个 id 不会报任何错 ——
        那家厂商的 rank 静默变成「未登记」，被排到列表最末，而页面看起来完全正常；
        漏项同理。所以拼写与漏项两个方向都要卡住，新增厂商时必须显式登记。
        """
        root = Path(__file__).resolve().parent
        vendors, _sources = crawler_llm_intel.parse_yaml(root / "llm-intel.yaml")
        ids = {v["id"] for v in vendors}
        self.assertTrue(ids, "没解析到厂商 id —— 解析失配，先修测试本身")
        rank = list(provider_profiles.VENDOR_RANK)
        unknown = sorted(set(rank) - ids)
        self.assertEqual(unknown, [],
                         f"VENDOR_RANK 里有不属于任何厂商的 id（拼写错了？）: {unknown}")
        missing = sorted(ids - set(rank))
        self.assertEqual(missing, [],
                         f"这些厂商没登记进 VENDOR_RANK，会被静默排到列表最后: {missing}")
        self.assertEqual(len(rank), len(set(rank)), "VENDOR_RANK 里有重复的 id")

    def test_vendor_rank_index_falls_back_to_tail(self):
        """未登记厂商的 rank 必须是「排在所有已登记厂商之后」，而不是 0。"""
        tail = provider_profiles.vendor_rank_index("__not_a_real_vendor__")
        self.assertEqual(tail, len(provider_profiles.VENDOR_RANK))
        self.assertGreater(tail, provider_profiles.vendor_rank_index("anthropic"))

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


# CI 里必须排除的测试类。**只有「会破坏 CI 自身状态」的类才配进这个白名单**，目前为空：
# `TestCrawlerCleanup` 曾经在此（它会删掉仓库根的 `.ai-changed`，而那是 workflow
# 「Decide commit path」判定走 PR 还是直提的判据）—— 后来把仓库根改成可注入的
# `crawler_llm_intel._repo_root()`，该测试改在临时目录里跑，就不再需要排除了。
# 保留这个机制是为了以后真有必须排除的用例时有地方写，而不是临时改 workflow。
CI_EXCLUDED_CLASSES: tuple[str, ...] = ()


def ci_suite() -> unittest.TestSuite:
    """CI 用测试集 = 全部用例 − `CI_EXCLUDED_CLASSES`（现为空集，即全部用例都进 CI）。

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

    def test_covers_every_test_class(self):
        """`ci_suite()` 必须覆盖除白名单外的每个测试类（白名单现为空 = 全覆盖）。

        取集失配是**静默**的：少跑一批守卫不会有任何提示，直到某天回归溜到提交之后才发现。
        """
        ids = self._ids(ci_suite())
        self.assertTrue(ids, "ci_suite 不能为空 —— 取集失配会让 CI 静默跳过全部测试")
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

    def test_cleanup_test_is_ci_safe(self):
        """`TestCrawlerCleanup` 不该再被排除 —— 它已改为在临时目录里跑。

        Regression: 该测试曾在**真实仓库根**建 / 删 `.ai-changed`（workflow「Decide commit
        path」判定走 PR 还是直提的判据），于是只能被排除在 CI 之外，那段清理逻辑在 CI 里
        零覆盖。改成注入 `_repo_root()` 后不再需要排除；行为层面的守卫见
        `TestCrawlerCleanup.test_real_repo_marker_is_not_touched`。
        """
        self.assertNotIn("TestCrawlerCleanup", CI_EXCLUDED_CLASSES,
                         "该测试已改为在临时目录里跑，不该再被排除")
        ids = self._ids(ci_suite())
        self.assertTrue(any("TestCrawlerCleanup" in i for i in ids),
                        "TestCrawlerCleanup 必须真的在 CI 测试集里，否则这段清理逻辑零覆盖")


if __name__ == "__main__":
    unittest.main()
