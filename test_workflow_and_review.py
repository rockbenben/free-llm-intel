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
import shutil
import subprocess
import tempfile
import types
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path
from unittest import mock

import requests
import yaml

import ai_review
import crawler_llm_intel
import provider_profiles
import fulltext as ft


def build_records():
    """按 README 展示顺序构造 (序号, VendorIntel, profile) 三元组（无真实抓取）。"""
    root = Path(__file__).resolve().parent
    vendors, _sources = crawler_llm_intel.parse_yaml(root / "llm-intel.yaml")
    records = []
    for i, v in enumerate(vendors, 1):
        # yaml 厂商键是 brand（曾误用 name → 全部空品牌，品牌回退路径从未被测到）
        prof = provider_profiles.get_provider_profile(
            v["id"], v.get("brand", ""), v.get("homepage", ""))
        intel = crawler_llm_intel.VendorIntel(
            vendor_id=v["id"], brand=v.get("brand", ""),
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
                      "CI must install Chromium: without it ~1/3 of pages were JS "
                      "shells at the time we measured, and the README live-evidence "
                      "rows lose quality (snapshot hashes are requests-stage-only by design)")
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

    def test_workflow_backfills_originals_before_crawling(self):
        """英文原文回填是 AI 重译标题的前提，必须接进入口，且排在爬虫之前。

        爬虫把归档当合并基底读：注释在这一轮写进去，当天的 RSS / articles.json
        才带得上 original_title；排在爬虫之后产物要晚一天。
        """
        with open(self.workflow_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        names = [s.get("name", "") for s in data["jobs"]["crawl"]["steps"]]
        self.assertIn("Backfill article originals", names)
        self.assertIn("Restore backfill ledger", names,
                      "台账必须被缓存，否则每天重打同一批取不到原文的 URL")
        self.assertLess(names.index("Backfill article originals"),
                        names.index("Run intel crawler"),
                        "回填要排在爬虫之前，当天产物才能带上原文")
        step = next(s for s in data["jobs"]["crawl"]["steps"]
                    if s.get("name") == "Backfill article originals")
        self.assertIn("--backfill-orig", step.get("run", ""))
        self.assertTrue(step.get("continue-on-error"),
                        "回填是增强项：失败不该挡掉当天的巡检产物提交")
        # 台账与翻译缓存同类：不进 git，靠 Actions cache 续命
        self.assertIn("backfill-ledger-",
                      next(s for s in data["jobs"]["crawl"]["steps"]
                           if s.get("name") == "Restore backfill ledger")["with"]["restore-keys"])
        gitignore = (self.root / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(crawler_llm_intel.BACKFILL_LEDGER_NAME, gitignore,
                      "台账文件必须被忽略，否则每天产生一份 churn 提交")

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


class TestDiffFocusedReviewAndSourceCooldown(unittest.TestCase):
    """diff 导向核查（快照存事实行 + prompt 聚焦变化行）与连续失败源冷却。"""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _page(self, text):
        return crawler_llm_intel.PageResult(
            url="https://example.com/pricing", stype="pricing",
            ok=True, snapshot_ok=True, snapshot_text=text,
            title="", text=text)

    def _vendor(self, page):
        v = crawler_llm_intel.VendorIntel(
            vendor_id="fv1", brand="FocusV", homepage="https://example.com",
            products=[])
        v.intel_pages = [page]
        return v

    def test_stage_records_fact_and_focus_diff(self):
        s1 = crawler_llm_intel.SnapshotState(self.root)
        s1.stage_vendor("fv1", self._vendor(self._page(
            "每月 100 万 tokens\n长期有效\n旧限速说明")))
        s1.commit_vendor("fv1")
        s1.save({"fv1"}, full_run=True)

        s2 = crawler_llm_intel.SnapshotState(self.root)
        key = crawler_llm_intel._snapshot_key("fv1", self._page(""))
        self.assertIn("每月 100 万 tokens",
                      s2.entries[key]["fact"], "条目应携带事实文本")

        changed = s2.stage_vendor("fv1", self._vendor(
            self._page("每月 100 万 tokens\n长期有效\n新限速说明")))
        self.assertEqual(len(changed), 1)
        focus = s2.focus.get("fv1")
        self.assertTrue(focus)
        self.assertEqual(focus[0]["removed"], ["旧限速说明"])
        self.assertEqual(focus[0]["added"], ["新限速说明"])

    def test_focus_prompt_section_and_halved_budget(self):
        page = self._page("Free tier: 100k tokens monthly. " * 4000)
        it = self._vendor(page)
        focus = [{"url": page.url, "stype": "pricing",
                  "removed": ["old rate 10 RPM"], "added": ["new rate 30 RPM"]}]
        p_focus = crawler_llm_intel.build_review_prompt(it, focus)
        p_plain = crawler_llm_intel.build_review_prompt(it)
        self.assertIn("【本次页面变化行】", p_focus)
        self.assertIn("- old rate 10 RPM", p_focus)
        self.assertIn("+ new rate 30 RPM", p_focus)
        self.assertNotIn("【本次页面变化行】", p_plain)
        self.assertLess(len(p_focus), len(p_plain),
                        "focus 时整页预算应减半（证据引文仍在原文区内即不伤闸门）")
        self.assertIn("Free tier: 100k tokens monthly.", p_focus,
                      "变化行证据必须仍能在语料中逐字定位")

    def test_source_failure_cooldown_persist_and_reopen(self):
        today = date.today()
        key = "fv1|pricing|https://example.com/pricing"
        s = crawler_llm_intel.SnapshotState(self.root)
        for _ in range(crawler_llm_intel.SOURCE_SKIP_FAILS - 1):
            s.record_failure(key, today.isoformat())
        self.assertFalse(s.should_skip_source(key, today.isoformat()),
                         "未达阈值不跳过")
        s.record_failure(key, today.isoformat())
        self.assertTrue(s.should_skip_source(key, today.isoformat()))
        s.save({"fv1"}, full_run=True)

        s2 = crawler_llm_intel.SnapshotState(self.root)
        self.assertTrue(s2.should_skip_source(key, today.isoformat()),
                        "冷却状态应随 llm-intel-state.json 持久化")
        reopen = (today + timedelta(days=crawler_llm_intel.SOURCE_RETRY_DAYS))
        self.assertFalse(s2.should_skip_source(key, reopen.isoformat()),
                         "冷却到期自动放行重试")
        s2.clear_failure(key)
        self.assertFalse(s2.should_skip_source(key, today.isoformat()),
                         "抓取成功清零后不再跳过")


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

    def test_kept_english_title_is_not_retranslated(self):
        """`<!--orig:X-->` 与可见标题相同 = 有意保留英文，必须原样留在归档里。

        机翻失败留下的英文行**不写注释**，所以「相同」是唯一的有意保留信号；
        少了这层冻结，产品名标题每轮都会被改写成译名（实测 `Grok Imagine API`
        → 「Grok 想象 API」、`Grok Voice Agent API` → 「Grok 语音代理 API」）。
        """
        arch_path = self.news_dir / "vendor_a.md"
        arch_path.write_text(
            "## 全部文章（共 3 篇）\n\n"
            "1. [Grok Imagine API](https://a.com/keep)（2026-09-22） "
            "<!--orig:Grok Imagine API-->\n"
            "2. [Introducing Grok Voice](https://a.com/todo)（2026-09-21）\n"
            "3. [Grok Bot 现已包含在更多计划中](https://a.com/old)（2026-08-26）\n",
            encoding="utf-8")
        arts = crawler_llm_intel.parse_archived_articles(arch_path)
        keep = next(a for a in arts if a.url.endswith("/keep"))
        todo = next(a for a in arts if a.url.endswith("/todo"))
        self.assertEqual(keep.zh_title, "Grok Imagine API",
                         "与原文同名的可见标题要冻结成 zh_title，否则等于没做过决定")
        self.assertEqual(todo.zh_title, "",
                         "机翻失败留下的英文行必须仍未冻结，下一轮继续试")

        intel = self._intel(list(arts))
        with mock.patch.object(
                crawler_llm_intel, "translate_to_zh",
                side_effect=lambda t: ("Grok 想象 API" if "Imagine" in t
                                       else f"中文 · {t}")):
            crawler_llm_intel.write_news_archives(self.news_dir, [intel],
                                                  clean_removed=False)
        content = arch_path.read_text(encoding="utf-8")
        self.assertIn("[Grok Imagine API](https://a.com/keep)", content,
                      "判定保留英文的那条不得被改写成译名")
        self.assertIn("<!--orig:Grok Imagine API-->", content,
                      "注释必须写回归档，丢了它下一轮就退化成「未汉化」")
        self.assertIn("中文 · Introducing Grok Voice", content,
                      "没有标记的英文行照常送去翻译")
        # 老行（无注释、可见标题即中文译文）是第三种情况：既没保留英文，也没判定过原文。
        # 它 title == zh_title == 中文，若emit 条件只看「相同就写注释」，就会被钉上
        # `<!--orig:中文…-->`，产出层的原文列随即掺进译文（实测 xai_grok 26 行中招）。
        self.assertIn("[Grok Bot 现已包含在更多计划中](https://a.com/old)", content,
                      "老中文行的可见标题必须原样保留")
        for payload in re.findall(r"<!--orig:(.*?)-->", content):
            self.assertFalse(crawler_llm_intel._CJK_CHAR_RE.search(payload),
                             f"注释只能装英文原文，不能装中文译文：{payload}")

    def test_html_entities_in_archived_titles_get_decoded(self):
        """归档里的 `&amp;` 必须在读取时解码，否则实体被写进产物。

        实抓路径经 HTMLParser 已解码，`--rebuild-only` 是直接读 .md 的，少这一步
        产出层就会显示「发布 &amp; 全新推出」（实测 longcat 条目在
        model-releases.json / intel-changes.json 里这样回归过一次）。
        """
        arch_path = self.news_dir / "vendor_a.md"
        arch_path.write_text(
            "## 全部文章（共 2 篇）\n\n"
            "1. [LongCat-2.0 发布 &amp; 全新推出计费服务](https://a.com/lc)（2026-06-30）\n"
            "2. [成本与速度对比](https://a.com/cs)（2026-06-20） <!--orig:Cost &amp; speed--> \n",
            encoding="utf-8")
        arts = crawler_llm_intel.parse_archived_articles(arch_path)
        lc = next(a for a in arts if a.url.endswith("/lc"))
        cs = next(a for a in arts if a.url.endswith("/cs"))
        self.assertEqual(lc.title, "LongCat-2.0 发布 & 全新推出计费服务")
        self.assertEqual(lc.zh_title, "LongCat-2.0 发布 & 全新推出计费服务")
        self.assertEqual(cs.title, "Cost & speed",
                         "注释里的原文同样要解码，它是 articles.json 原文列的来源")
        self.assertEqual(cs.zh_title, "成本与速度对比")

        intel = self._intel(list(arts))
        crawler_llm_intel.write_news_archives(self.news_dir, [intel],
                                              clean_removed=False)
        content = arch_path.read_text(encoding="utf-8")
        self.assertNotIn("&amp;", content, "写回的归档不该把实体再抬一遍")
        self.assertIn("<!--orig:Cost & speed-->", content)

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
        # 英文原文现在是**刻意**保留的（冻结进 `<!--orig:…-->` 注释，供 articles.json
        # 原文列），但它只能待在注释里：可见的列表标题必须仍是中文。
        self.assertIn("<!--orig:Better prompt caching for GPT-6-->", content,
                      "英文原文应被冻结进注释，供产出层稳定恢复 original_title")
        self.assertNotIn("[Better prompt caching", content,
                         "英文原文不得成为可见的列表标题")

    def test_orig_comment_recovers_english_original(self):
        """归档行里的 `<!--orig:…-->` 注释要还原成 title=英文 / zh_title=中文这对形态。"""
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "v.md"
            p.write_text(
                "## 全部文章（共 1 篇）\n\n"
                "1. [中文译文标题](https://a.com/x)（2026-01-01） "
                "<!--orig:English Original Title-->\n", encoding="utf-8")
            arts = crawler_llm_intel.parse_archived_articles(p)
            self.assertEqual(len(arts), 1)
            self.assertEqual(arts[0].title, "English Original Title",
                             "注释里的英文原文要还原为 title，供原文列使用")
            self.assertEqual(arts[0].zh_title, "中文译文标题",
                             "可见中文标题要还原为 zh_title")
            self.assertEqual(crawler_llm_intel.article_title_zh(arts[0]), "中文译文标题",
                             "显示标题仍取冻结的中文，不回退机翻")

    def test_frozen_calque_self_heals_on_carry_over(self):
        """守卫装好前冻结进归档的音译/直译标题，沿用时要借英文原文自愈。

        CI 侧实测：坏译文被 Actions 翻译缓存复活 → 写进归档 → 靠沿用机制永生，
        三道各自正确的机制合谋让产物扫描天天红。沿用点复原是最后一道闸。
        """
        arch_path = self.news_dir / "vendor_a.md"
        arch_path.write_text(
            "## 全部文章（共 1 篇）\n\n"
            "1. [Hugging Face中的贴片时间序列Transformer](https://a.com/patchtst)（2024-02-01）\n",
            encoding="utf-8")
        fresh = crawler_llm_intel.Article(
            title="Patch Time Series Transformer in Hugging Face",
            url="https://a.com/patchtst", date="2024-02-01")
        intel = self._intel([fresh])
        crawler_llm_intel.write_news_archives(self.news_dir, [intel],
                                              clean_removed=False)
        content = arch_path.read_text(encoding="utf-8")
        self.assertIn("Hugging Face中的Patch Time Series Transformer", content,
                      "英文产品名应复原、中文连接词保持原样")
        self.assertNotIn("贴片时间序列", content)

    def test_archive_only_row_is_not_retranslated(self):
        """只在归档里、本次没抓到的条目，同样不许回炉重翻。

        CI 每日红：2024 年的 patchtst 早掉出博客页首屏，合并时按「历史条目只增
        不减」被追加回来，但 parse_archived_articles 把冻结的中文标题放进 title、
        zh_title 留空 → article_title_zh 又把它送回机翻。Google 对已经是中文的串
        再翻一次，就把里面原样保留的英文产品名直译了
        （「Patch Time Series」→「贴片时间序列」），守卫报的正是这条。
        """
        arch_path = self.news_dir / "vendor_a.md"
        arch_path.write_text(
            "## 全部文章（共 1 篇）\n\n"
            "1. [Hugging Face 中的 Patch Time Series Transformer]"
            "(https://a.com/patchtst)（2024-02-01）\n",
            encoding="utf-8")
        fresh = crawler_llm_intel.Article(
            title="A newer post", url="https://a.com/new", date="2026-09-27")
        intel = self._intel([fresh])

        def mangle(text):
            # 模拟 Google 拿到中文标题时的真实行为：英文词被直译、空格被吃掉
            return ("Hugging Face中的贴片时间序列Transformer"
                    if "Patch" in text else text)

        with mock.patch.object(crawler_llm_intel, "translate_to_zh",
                               side_effect=mangle):
            crawler_llm_intel.write_news_archives(self.news_dir, [intel],
                                                  clean_removed=False)
        content = arch_path.read_text(encoding="utf-8")
        self.assertIn("Hugging Face 中的 Patch Time Series Transformer", content,
                      "归档冻结的中文标题必须原样写回")
        self.assertNotIn("贴片", content)

    def test_no_cjk_title_ever_reaches_the_translator(self):
        """不变量：翻译器只该收到非中文标题——含汉字的输入一律是回炉。"""
        arch_path = self.news_dir / "vendor_a.md"
        arch_path.write_text(
            "## 全部文章（共 2 篇）\n\n"
            "1. [用开源 LLM 实现 Constitutional AI](https://a.com/cai)（2024-02-02）\n"
            "2. [Old English Title](https://a.com/en)（2024-02-01）\n",
            encoding="utf-8")
        fresh = crawler_llm_intel.Article(
            title="A newer post", url="https://a.com/new", date="2026-09-27")
        intel = self._intel([fresh])
        seen: list[str] = []

        def spy(text):
            seen.append(text)
            return text

        with mock.patch.object(crawler_llm_intel, "translate_to_zh", side_effect=spy):
            crawler_llm_intel.write_news_archives(self.news_dir, [intel],
                                                  clean_removed=False)
        self.assertEqual([t for t in seen if crawler_llm_intel._CJK_CHAR_RE.search(t)],
                         [], "含汉字的标题被送回机翻，等于让 Google 改自己的归档")
        self.assertIn("Old English Title", seen, "未汉化的英文标题仍应送去翻译")

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

    def test_resolve_article_original_english_vs_native(self):
        self.assertEqual(
            crawler_llm_intel.resolve_article_original(
                "<title>Grok 4.6 is here | xAI</title>", "https://x.ai/news/grok-4-6"),
            "Grok 4.6 is here", "取 <title> 并去站点名后缀")
        self.assertEqual(
            crawler_llm_intel.resolve_article_original(
                "<title>硅基流动发布说明</title>", "https://x.cn/y"), "",
            "中文原生页没有英文原文，不得把中文当原文")

    def test_backfill_orig_writes_comment_and_skips(self):
        """只给「可见标题已汉化、且尚无 orig 注释」的条目访问并回填；已注释/英文可见标题跳过。"""
        (self.news / "v.md").write_text(
            "## 全部文章（共 3 篇）\n\n"
            "1. [已存原文的文章](https://x.com/a)（2026-01-01） <!--orig:Already here-->\n"
            "2. [Grok 4.6 已发布](https://x.ai/news/grok-4-6)（2026-01-02）\n"
            "3. [English visible title](https://x.com/c)（2026-01-03）\n",
            encoding="utf-8")

        def fetch(url):
            return "<title>Grok 4.6 is here | xAI</title>"

        visited, filled, recorded = crawler_llm_intel.backfill_archive_originals(
            self.news, fetch, delay=0)
        self.assertEqual((visited, filled, recorded), (1, 1, 0),
                         "只访问第 2 条（已汉化且无注释）；已注释的、英文可见标题的都不访问")
        content = (self.news / "v.md").read_text(encoding="utf-8")
        self.assertIn("2. [Grok 4.6 已发布](https://x.ai/news/grok-4-6)（2026-01-02） "
                      "<!--orig:Grok 4.6 is here-->", content)
        self.assertIn("1. [已存原文的文章](https://x.com/a)（2026-01-01） "
                      "<!--orig:Already here-->", content, "已有注释的行原样保留")
        self.assertIn("3. [English visible title](https://x.com/c)（2026-01-03）", content)

    # ---- 回填台账：失败/取不到的行不能每轮重打 ----

    LEDGER_ARCHIVE = (
        "## 全部文章（共 4 篇）\n\n"
        "1. [锚点行标题](https://x.ai/news#d-2026-01-01-0)（2026-01-01）\n"
        "2. [吃 403 的文章](https://x.ai/news/blocked)（2026-01-02）\n"
        "3. [中文原生页](https://x.ai/news/chinese)（2026-01-03）\n"
        "4. [能取到原文的文章](https://x.ai/news/good)（2026-01-04）\n")

    def _ledger_case(self, fetch, tmp: Path):
        (tmp / "v.md").write_text(self.LEDGER_ARCHIVE, encoding="utf-8")
        ledger = tmp / crawler_llm_intel.BACKFILL_LEDGER_NAME
        calls: list[str] = []

        def spy(url):
            calls.append(url)
            return fetch(url)
        return spy, calls, ledger

    @staticmethod
    def _http_error(code: int) -> requests.HTTPError:
        err = requests.HTTPError(f"{code} Error")
        err.response = mock.Mock(status_code=code)
        return err

    def test_anchor_rows_are_never_fetched(self):
        """列表页锚点没有独立文章页，访问它取回的是**列表页**标题，写进去就是假原文。"""
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            spy, calls, ledger = self._ledger_case(
                lambda u: "<title>News | xAI</title>", tmp)
            visited, filled, recorded = crawler_llm_intel.backfill_archive_originals(
                tmp, spy, delay=0, ledger_path=ledger)
        self.assertNotIn("https://x.ai/news#d-2026-01-01-0", calls,
                         "锚点行一次都不该被访问")
        self.assertNotIn("https://x.ai/news", [u.split("#")[0] for u in calls])

    def test_permanent_and_unusable_outcomes_are_ledgered(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)

            def fetch(url):
                if "blocked" in url:
                    raise self._http_error(403)
                if "chinese" in url:
                    return "<title>发布说明 | xAI</title>"      # 取到了页，但没有英文原文
                return "<title>Grok lands everywhere | xAI</title>"

            spy, calls, ledger = self._ledger_case(fetch, tmp)
            v1, f1, r1 = crawler_llm_intel.backfill_archive_originals(
                tmp, spy, delay=0, ledger_path=ledger)
            self.assertEqual(sorted(calls), [
                "https://x.ai/news/blocked", "https://x.ai/news/chinese",
                "https://x.ai/news/good"], "首轮把三条直链都试一遍，锚点跳过")
            self.assertEqual(f1, 1)
            data = json.loads(ledger.read_text(encoding="utf-8"))
            self.assertEqual(data["https://x.ai/news/blocked"], "http-403")
            self.assertEqual(data["https://x.ai/news/chinese"], "none")
            self.assertNotIn("https://x.ai/news/good", data, "成功回填的不记账")

            # 第二轮：已记账的两条不再打，只剩成功那条（已带注释）→ 0 访问
            calls2: list[str] = []
            v2, f2, r2 = crawler_llm_intel.backfill_archive_originals(
                tmp, lambda u: calls2.append(u) or "", delay=0, ledger_path=ledger)
            self.assertEqual((v2, f2, r2, calls2), (0, 0, 0, []),
                             "台账生效后不再重打同一批失败项")

    def test_transient_failures_are_retried_next_run(self):
        """超时 / 5xx 不记账：那是服务端临时故障，下一轮还得再试。"""
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)

            def fetch(url):
                if "good" in url:
                    raise requests.Timeout("slow")
                if "blocked" in url:
                    raise self._http_error(503)
                return "<title>发布说明 | xAI</title>"     # 取到页面，但没有英文原文

            spy, calls, ledger = self._ledger_case(fetch, tmp)
            crawler_llm_intel.backfill_archive_originals(tmp, spy, delay=0, ledger_path=ledger)
            data = json.loads(ledger.read_text(encoding="utf-8"))
            self.assertNotIn("https://x.ai/news/good", data, "超时不该被当成永久取不到")
            self.assertNotIn("https://x.ai/news/blocked", data, "5xx 是临时的")
            self.assertEqual(data["https://x.ai/news/chinese"], "none")

    def test_vendors_filter_bounds_the_batch(self):
        """`--only` 必须能圈定回填范围：字母序靠前的厂商吃光配额，后面的就永远轮不到。"""
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            for name, marker in (("aardvark.md", "aa"), ("zebra.md", "zz")):
                (tmp / name).write_text(
                    "## 全部文章（共 1 篇）\n\n"
                    f"1. [文章 {marker}](https://x.ai/news/{marker})（2026-01-01）\n",
                    encoding="utf-8")
            seen: list[str] = []

            def fetch(url):
                seen.append(url)
                return f"<title>Post {url.rsplit('/', 1)[-1]} | xAI</title>"

            crawler_llm_intel.backfill_archive_originals(
                tmp, fetch, limit=10, delay=0, vendors={"zebra"})
            self.assertEqual(seen, ["https://x.ai/news/zz"], "只碰被圈定的那一家")
            text = (tmp / "zebra.md").read_text(encoding="utf-8")
            self.assertIn("<!--orig:Post zz-->", text)
            self.assertNotIn("<!--orig:", (tmp / "aardvark.md").read_text(encoding="utf-8"),
                             "没被圈定的厂商不得改动")

            seen.clear()
            crawler_llm_intel.backfill_archive_originals(tmp, fetch, limit=10, delay=0)
            self.assertEqual(seen, ["https://x.ai/news/aa"], "不传 vendors = 全部处理")

    def test_rate_limit_is_not_a_verdict(self):
        """429 / 408 / 425 是「慢点再来」，不能当成「这页没有原文」永久烧进台账。

        实测踩过：两轮并发打 huggingface 触发限流，335 条链接被记成 `http-429`，
        此后永远不再尝试——一次我自己的操作失误就把整家厂商的原文恢复判了死刑。
        """
        for code in (429, 408, 425, 500, 503):
            exc = self._http_error(code)
            self.assertEqual(crawler_llm_intel._failure_tag(exc), "",
                             f"{code} 属于可重试，不该记账")
        for code in (403, 404, 410):
            self.assertEqual(crawler_llm_intel._failure_tag(self._http_error(code)),
                             f"http-{code}", f"{code} 是站方的稳定答复，应当记账")

    def test_shared_shell_title_is_not_written(self):
        """SPA 外壳页把站点名当 <title> 交回来（实测小米 MiMo 15 条同一个
        `Xiaomi MiMo Home`）：同一份原文挂到第二条**不同的非锚点 URL** 上就是假原文。

        锚点行不参与这条判据——「锚点 + 直链」共用同一原文是同一篇文章的两个入口
        （xai_grok / anthropic 各有一批那样的真重复），一刀切会误删合法原文。
        """
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            (tmp / "v.md").write_text(
                "## 全部文章（共 4 篇）\n\n"
                "1. [第一篇的中文标题](https://mimo.mi.com/news/a)（2026-01-01）\n"
                "2. [第二篇的中文标题](https://mimo.mi.com/news/b)（2026-01-02）\n"
                "3. [真正有标题的一篇](https://mimo.mi.com/news/c)（2026-01-03）\n"
                "4. [同一篇的锚点入口](https://mimo.mi.com/news#d-2026-01-03-9)"
                "（2026-01-03）\n",
                encoding="utf-8")
            ledger = tmp / crawler_llm_intel.BACKFILL_LEDGER_NAME

            def fetch(url):
                if "/news/c" in url:
                    return "<title>MiMo-V2 launches | Xiaomi</title>"
                return "<title>Xiaomi MiMo Home</title>"

            visited, filled, recorded = crawler_llm_intel.backfill_archive_originals(
                tmp, fetch, delay=0, ledger_path=ledger)
            text = (tmp / "v.md").read_text(encoding="utf-8")
            self.assertEqual(filled, 1, "只有第一条能写；第二条共用同一站点名，被判假原文")
            self.assertIn("<!--orig:MiMo-V2 launches-->", text)
            self.assertNotIn("Xiaomi MiMo Home", text)
            data = json.loads(ledger.read_text(encoding="utf-8"))
            self.assertEqual(data["https://mimo.mi.com/news/a"], "shell",
                             "共用外壳标题的两条都不写、都记账（第一条也不能幸免）")
            self.assertEqual(data["https://mimo.mi.com/news/b"], "shell")
            self.assertNotIn("https://mimo.mi.com/news/c", data, "真拿到原文的那条不记账")

    def test_ledger_flushes_during_the_run_not_only_at_the_end(self):
        """中断的一轮也必须留住已判过的账，否则几百个请求全白打。"""
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            rows = "\n".join(
                f"{i}. [文章 {i}](https://x.ai/news/p{i})（2026-01-01）" for i in range(1, 91))
            (tmp / "v.md").write_text(f"## 全部文章（共 90 篇）\n\n{rows}\n", encoding="utf-8")
            ledger = tmp / crawler_llm_intel.BACKFILL_LEDGER_NAME
            seen: list[str] = []
            interrupt_at = 2 * crawler_llm_intel.LEDGER_FLUSH_EVERY + 10

            def fetch(url):
                if len(seen) >= interrupt_at:
                    raise KeyboardInterrupt("巡检被取消")
                seen.append(url)
                return "<title>发布说明 | xAI</title>"      # 每条都判为 none

            with self.assertRaises(KeyboardInterrupt):
                crawler_llm_intel.backfill_archive_originals(
                    tmp, fetch, limit=200, delay=0, ledger_path=ledger)
            self.assertEqual(len(seen), interrupt_at, "夹具前提：确实在跑完前被打断")
            self.assertTrue(ledger.exists(), "中途被中断也要有落盘，不能只在结尾写一次")
            data = json.loads(ledger.read_text(encoding="utf-8"))
            self.assertGreaterEqual(len(data), crawler_llm_intel.LEDGER_FLUSH_EVERY,
                                    "已判过的账必须已写入")
            self.assertLess(len(data), len(seen), "只该留住已 flush 的批次，没 flush 的随中断丢掉")

    def test_clearing_the_ledger_resumes_the_retry(self):
        """台账是缓存不是判决：删掉文件就重新尝试（站点日后改版能取到原文）。"""
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            spy, _calls, ledger = self._ledger_case(
                lambda u: "<title>发布说明 | xAI</title>", tmp)
            crawler_llm_intel.backfill_archive_originals(tmp, spy, delay=0, ledger_path=ledger)
            self.assertEqual(json.loads(ledger.read_text(encoding="utf-8"))[
                "https://x.ai/news/good"], "none")

            def fetch_ok(url):
                if url.endswith("/good"):
                    return "<title>Grok 4.7 is here | xAI</title>"
                return "<title>发布说明 | xAI</title>"
            fixed_calls: list[str] = []
            v, f, r = crawler_llm_intel.backfill_archive_originals(
                tmp, lambda u: (fixed_calls.append(u), fetch_ok(u))[1],
                delay=0, ledger_path=None)     # 无台账 = 每次都试
            self.assertEqual(f, 1, "站点改版给出英文标题后应能补上")
            self.assertIn("<!--orig:Grok 4.7 is here-->",
                          (tmp / "v.md").read_text(encoding="utf-8"))


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

    def test_snapshot_original_titles_are_decoded_before_reuse(self):
        """上一版 articles.json 里的 HTML 实体要先还原，否则每轮自我复制。

        `&amp;` 曾在解码之前被写进索引；不做这步，长列表回填会把它当「另一个标题」
        重新冻进归档注释与 JSON（实测 longcat 的 `&amp;`、腾讯混元的 `&nbsp;`
        就这样在产物里活了每一轮），而还原后与显示标题相等说明它根本不是原文。
        """
        rows = {
            "fields": ["title", "url", "vendor", "date", "original_title"],
            "count": 2,
            "articles": [
                ["发布 & 计费服务", "https://a.com/ent", "vendor_a", "2026-06-30",
                 "发布 &amp; 计费服务"],
                ["Cost & speed", "https://a.com/real", "vendor_a", "2026-06-01",
                 "Cost &amp; speed report"],
            ],
        }
        feeds = self.root / "docs" / "feeds"
        feeds.mkdir(parents=True)
        (feeds / "articles.json").write_text(json.dumps(rows, ensure_ascii=False),
                                             encoding="utf-8")
        orig = crawler_llm_intel.load_original_titles(feeds / "articles.json")
        self.assertNotIn(("vendor_a", "https://a.com/ent"), orig,
                         "实体形态与显示标题同串，不该再当原文回填")
        self.assertEqual(orig[("vendor_a", "https://a.com/real")], "Cost & speed report",
                         "真原文里的实体要还原成 &")

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

    def test_main_fast_replay_skips_readme(self):
        """本地核查快进轮：intel_list 由磁盘重建、没有实抓情报页，不得渲染 README。

        Regression: 快进与 --rebuild-only 同源（rebuild_intel_from_disk 只填动态页），
        渲染 README 会把厂商档案区写成空白、冲掉上一轮实抓成果。补丁已 adopt 进
        profile_overrides.json，留待下一次完整巡检渲染。
        """
        # 状态文件存在 → 非基线，快进守卫（line 5189）才会生效
        (self.root / "llm-intel-state.json").write_text(
            json.dumps({"sources": {}, "reviews": {}, "failures": {}}),
            encoding="utf-8")
        vendors, sources = crawler_llm_intel.parse_yaml(self.root / "intel.yaml")
        grouped = crawler_llm_intel.group_sources_by_vendor(sources)
        states = crawler_llm_intel._parse_news_md_page_states(self.NEWS_MD)
        rebuilt = crawler_llm_intel.rebuild_intel_from_disk(
            vendors, grouped, states, self.root / "llm-news")
        with (
            mock.patch.object(crawler_llm_intel, "try_packet_fast_replay",
                              return_value=(rebuilt, True, {"vendor_a"})),
            mock.patch.object(crawler_llm_intel, "crawl_vendor",
                              side_effect=AssertionError("快进不得实抓")),
            mock.patch.object(crawler_llm_intel, "update_readme",
                              side_effect=AssertionError("快进轮不得渲染 README")),
        ):
            rc = crawler_llm_intel.main([
                "--review-apply", "--yaml", "intel.yaml", "--news-md", "news.md",
                "--news-opml", "news.opml"])
        self.assertEqual(rc, 0)
        self.assertFalse((self.root / "README.md").exists(),
                         "快进轮不得写 README（情报区需要实抓页面）")

    def test_rebuild_only_keeps_every_vendor_in_quotas(self):
        """rebuild 的重建集只有「有动态归档的厂商」，一览必须仍是全集。

        2026-09 回归：quotas.json 跟着 intel_list 出，本地一次 rebuild 就把线上
        一览砍掉一半，Part 1 的几家国内平台和整条 Part 4 工具线静默消失。
        """
        # vendor_c 只有情报源：既没登记动态页，也没归档 → rebuild 不会重建它
        (self.root / "intel.yaml").write_text("""
vendors:
  - id: vendor_a
    brand: Vendor A
    homepage: https://a.com
    products: []
  - id: vendor_b
    brand: Vendor B
    homepage: https://b.com
    products: []
  - id: vendor_c
    brand: Vendor C
    homepage: https://c.com
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
  - vendor_id: vendor_c
    type: pricing
    url: https://c.com/pricing
""", encoding="utf-8")
        with mock.patch.object(crawler_llm_intel, "crawl_vendor",
                               side_effect=AssertionError("rebuild 不得抓取")):
            crawler_llm_intel.main(["--rebuild-only", "--yaml", "intel.yaml",
                                    "--news-md", "news.md", "--news-opml", "news.opml"])
        feeds = self.root / "docs" / "feeds"
        payload = json.loads((feeds / "quotas.json").read_text(encoding="utf-8"))
        indexed = json.loads((feeds / "articles.json").read_text(encoding="utf-8"))
        self.assertEqual({r[2] for r in indexed["articles"]}, {"vendor_a", "vendor_b"},
                         "夹具前提：动态类产物确实只重建出两家")
        self.assertEqual([r["id"] for r in payload["vendors"]],
                         ["vendor_a", "vendor_b", "vendor_c"],
                         "一览不得因为少重建一家而缩水")
        self.assertEqual([r["rank"] for r in payload["vendors"]], [1, 2, 3],
                         "rank 连续，档案锚点才不会串号")

    def test_rebuild_only_rejects_only_and_no_news(self):
        rc = crawler_llm_intel.main(["--rebuild-only", "--no-news",
                                     "--yaml", "intel.yaml"])
        self.assertEqual(rc, 2)


class TestNewsSectionCountConsistency(unittest.TestCase):
    """总表「共 N 篇」必须取自**归档合并后**的全量列表，而不是本次抓取结果。

    归档刻意保留页面已不再链接的历史文章（永不丢失），所以合并后的数量常大于本次
    抓取数。main() 里若把 render_news_section 排在 write_news_archives 之前，总表
    就会用合并前的计数，比归档文件少 —— 排查当时线上实测 anthropic 52/54、ppio 51/55、
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


class TestDeclaredSourceLanguage(unittest.TestCase):
    """动态源的**语言是声明**，不是事后判断：它决定发什么 Accept-Language、出不出英文镜像。"""

    TABLE = {"openai.com/news": "zh", "groq.com": "en",
             "minimax.io/blog": "en", "minimax.cn/blog": "zh"}

    def test_declared_chinese_source_has_no_chinese_in_original_slot(self):
        """源声明中文 → 原文槽里不许装着中文（那等于给中文文章编了个英文原文）。

        回归的是 21 行：`translator=agent` 的中文稿同时躺在 `.en.md`（原文槽）与
        `.md`，两份内容逐字相同，ledger 还记着 `src_lang=en`。对中文源来说那是
        「原文」，对读者却是同一篇中文被展示两遍。
        """
        repo = Path(__file__).resolve().parent
        idx = json.loads((repo / "docs/feeds/articles.json").read_text(encoding="utf-8"))
        entries = json.loads((repo / "docs/feeds/bodies.json").read_text(encoding="utf-8"))["bodies"]
        f = {k: i for i, k in enumerate(idx["fields"])}
        langs = crawler_llm_intel.news_lang_table(repo / "llm-intel.yaml")
        bad = []
        for row in idx["articles"]:
            v, s, url = row[f["vendor"]], row[f["slug"]], row[f["url"]]
            rec = entries.get(ft.bodies_key(v, url)) or {}
            rel = rec.get("en_path")
            if not rel or not (repo / rel).is_file():
                continue
            body = (ft.read_body_doc(repo / rel)[1] or "").strip()
            if len(body) < 40:
                continue
            # 判据与写入器同一个函数：两条路各设一个中文占比阈值，边界上必然互相打架
            if ft.detect_source_lang(body) != "zh":
                continue
            declared = (langs.get(crawler_llm_intel._lang_match_key(url))
                        or crawler_llm_intel.declared_source_lang(url, langs))
            if declared == "zh":
                bad.append(f"{v}/{s}")
        self.assertEqual(bad, [], "这些行的源声明为中文，原文槽里却装着中文正文：%s" % bad[:8])

    def test_every_shipped_news_source_declares_a_language(self):
        root = Path(__file__).resolve().parent
        data = yaml.safe_load((root / "llm-intel.yaml").read_text(encoding="utf-8"))
        news = [s for s in data["sources"]
                if (s.get("type") or "") in crawler_llm_intel.NEWS_TYPES]
        bad = [s["vendor_id"] for s in news if (s.get("lang") or "") not in ("en", "zh")]
        self.assertEqual(bad, [], "这些动态源没声明 lang：%s" % bad[:6])
        self.assertGreater(len(news), 40, "源清单不该空到认不出语言")

    def test_declaration_beats_title_shape_and_body_state(self):
        """中文源就算标题全是英文、正文也留着英文，也不出英文镜像。"""
        art = crawler_llm_intel.Article(title="GLM-5.3 Flash Now Available",
                                        url="https://openai.com/index/some-post")
        table = {"openai.com/index": "zh", "openai.com/news": "zh"}
        self.assertFalse(crawler_llm_intel._english_eligible(art, {}, "openai", table),
                         "旧判据（标题含 ≥4 拉丁 / en_status=ok）会把这条塞进英文镜像")
        en = crawler_llm_intel.Article(title="New model release",
                                       url="https://console.groq.com/docs/changelog")
        self.assertTrue(crawler_llm_intel._english_eligible(en, {}, "groq",
                                                            {"console.groq.com": "en"}))

    def test_host_level_fallback_only_when_unambiguous(self):
        """同 host 上声明了两种语言时，路径匹配不上就不给语言 —— 宁缺不猜。"""
        self.assertEqual(crawler_llm_intel.declared_source_lang(
            "https://groq.com/blog/post-1", {"groq.com": "en"}), "en")
        self.assertEqual(crawler_llm_intel.declared_source_lang(
            "https://example.com/other", {"example.com/a": "en", "example.com/b": "zh"}), "",
            "同 host 两种语言、路径又匹配不上时不能任选一种")

    def test_mixed_language_vendor_is_legal(self):
        """一家厂商同时有中英文动态源是正常配置，两种语言都要留住。"""
        srcs = [{"vendor_id": "vmix", "type": "blog", "url": "https://vmix.io/blog", "lang": "en"},
                {"vendor_id": "vmix", "type": "updates", "url": "https://vmix.cn/news", "lang": "zh"}]
        table = crawler_llm_intel.news_source_langs(srcs)
        self.assertEqual(table, {"vmix.io/blog": "en", "vmix.cn/news": "zh"},
                         "不许因为『一家只能一种语言』把声明丢掉")
        self.assertEqual(crawler_llm_intel.declared_source_lang(
            "https://vmix.cn/news/release-1", table), "zh")
        self.assertEqual(crawler_llm_intel.declared_source_lang(
            "https://vmix.io/blog/post", table), "en")

    def test_browser_fallback_uses_declared_language(self):
        """浏览器兜底通路也要按源声明发语言头，不许跟 requests 通路各说各话。"""
        seen = {}

        class _Page:
            def set_extra_http_headers(self, headers):
                seen.update(headers)

        bs = crawler_llm_intel.BrowserSession(enabled=False)
        bs._page = _Page()
        bs._ensure = lambda: False        # 不真起浏览器，只验头是否在 goto 前被覆盖
        bs.render("https://openai.com/zh-Hans-CN/news/", lang="zh")
        self.assertEqual(seen, {}, "_ensure 失败时不该碰页面")

        bs._ensure = lambda: True
        bs._render_once = lambda url: ("<html></html>", url, 200)
        bs.render("https://openai.com/zh-Hans-CN/news/", lang="zh")
        self.assertTrue(seen.get("Accept-Language", "").startswith("zh"), seen)
        seen.clear()
        bs.render("https://console.groq.com/docs/changelog", lang="en")
        self.assertTrue(seen.get("Accept-Language", "").startswith("en"),
                        "英文源走浏览器兜底也必须发英文优先头")

    def test_fetch_sends_declared_language(self):
        """抓源时按声明发 Accept-Language：en 源不许拿中文头去抓。"""
        seen = {}

        class _Resp:
            status_code = 200
            url = "https://groq.com/docs"
            text = "<html><body>" + ("English prose here. " * 40) + "</body></html>"
            content = text.encode()
            headers = {"Content-Type": "text/html"}

            def raise_for_status(self):
                pass

        class _Session:
            headers = {}

            def get(self, url, timeout=None, allow_redirects=True, headers=None):
                seen["al"] = (headers or {}).get("Accept-Language", "")
                return _Resp()

        crawler_llm_intel._fetch_with_requests(_Session(), "https://groq.com/docs",
                                               "changelog", (5.0, 5.0), 0, lang="en")
        self.assertTrue(seen["al"].startswith("en"), "en 源必须发 en 优先头：%s" % seen["al"])
        crawler_llm_intel._fetch_with_requests(_Session(), "https://groq.com/docs",
                                               "changelog", (5.0, 5.0), 0, lang="zh")
        self.assertTrue(seen["al"].startswith("zh"), "zh 源发中文头：%s" % seen["al"])
        crawler_llm_intel._fetch_with_requests(_Session(), "https://groq.com/docs",
                                               "changelog", (5.0, 5.0), 0)
        self.assertEqual(seen["al"], "", "没声明就不该覆盖会话默认头")


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

    def test_same_title_entries_collapse_preferring_canonical_url(self):
        """单页新闻列表的同标题重复条目必须在产出层折叠成一条，且保留规范直链。

        实测 x.ai：列表页锚点 `news#d-2026-07-16-28` 与真实文章 `news/grok-x` 是同一篇，
        锚点那条日期还更新（列表页按分节取日期）。不折叠的话浏览页会出现两行同标题；
        折叠时若按「日期最新」会错留锚点，故规范直链优先。
        """
        arts = [
            crawler_llm_intel.Article(
                title="Grok X", url="https://x.ai/news#d-2026-07-16-28", date="2026-07-16"),
            crawler_llm_intel.Article(
                title="Grok X", url="https://x.ai/news/grok-x", date="2026-07-15"),
            crawler_llm_intel.Article(
                title="另一篇公告", url="https://x.ai/news/other", date="2026-07-10"),
        ]
        v = self._vendor("xai_grok", "xAI", arts)
        crawler_llm_intel.write_rss_feeds(self.out_dir, [v], base_url="")
        index = json.loads((self.out_dir / "articles.json").read_text(encoding="utf-8"))
        rows = {r[0]: r[1] for r in index["articles"]}
        self.assertEqual(set(rows), {"Grok X", "另一篇公告"},
                         "同标题应折叠成一条，不同标题必须各自保留")
        self.assertEqual(rows["Grok X"], "https://x.ai/news/grok-x",
                         "应保留规范直链，而不是列表页锚点")
        # 输入不被改写：归档仍应持有全部原始条目
        self.assertEqual(len(v.all_news_articles), 3)

    def test_same_title_anchor_only_keeps_most_recent(self):
        """白名单外的单页站：同标题、只有锚点（无规范直链）时，按日期最新折叠成一条。"""
        arts = [
            crawler_llm_intel.Article(
                title="某功能预览版", url="https://docs.demo.cn/changelog#a", date="2024-09-05"),
            crawler_llm_intel.Article(
                title="某功能预览版", url="https://docs.demo.cn/changelog#b", date="2026-04-24"),
        ]
        kept = crawler_llm_intel._rss_articles(
            self._vendor("demo_spa", "Demo", arts), "2099-12-31")
        self.assertEqual(len(kept), 1)
        self.assertEqual(kept[0].date, "2026-04-24", "同锚点形态下保留日期更新的一条")

    def test_title_collapse_is_case_and_space_insensitive(self):
        arts = [
            crawler_llm_intel.Article(title="New  Model", url="https://a.com/1", date="2026-01-01"),
            crawler_llm_intel.Article(title="new model", url="https://a.com/2", date="2026-01-02"),
        ]
        kept = crawler_llm_intel._rss_articles(
            self._vendor("v", "V", arts), "2099-12-31")
        self.assertEqual(len(kept), 1, "大小写/空白差异的同一标题也应折叠")

    def test_canonical_only_vendors_drop_synthetic_anchors(self):
        """deepseek/x.ai/claude 的合成 `#锚点` 条目必须被丢掉，只留规范直链。

        这三家每条新闻都有独立文章页，动态页又是单页列表，变更日志提取器会另造
        `#d-<日期>-<n>` 锚点条目（同一篇的第二份拷贝、标题常重复），读者看到就是重复。
        """
        arts = [
            crawler_llm_intel.Article(
                title="Grok 4.6", url="https://x.ai/news/grok-4-6", date="2026-08-14"),
            crawler_llm_intel.Article(
                title="Grok 4.6 分节", url="https://x.ai/news#d-2026-08-19-13", date="2026-08-19"),
        ]
        v = self._vendor("xai_grok", "xAI", arts)
        crawler_llm_intel.write_rss_feeds(self.out_dir, [v], base_url="")
        urls = [r[1] for r in json.loads(
            (self.out_dir / "articles.json").read_text(encoding="utf-8"))["articles"]]
        self.assertEqual(urls, ["https://x.ai/news/grok-4-6"],
                         "锚点条目应被丢弃，只保留规范直链")

    def test_fragment_identity_vendors_keep_anchors(self):
        """白名单外的单页站（锚点即条目身份、无独立直链页）不受影响。"""
        arts = [
            crawler_llm_intel.Article(title="更新 A", url="https://x.cn/docs#a", date="2026-01-01"),
            crawler_llm_intel.Article(title="更新 B", url="https://x.cn/docs#b", date="2026-01-02"),
        ]
        kept = crawler_llm_intel._rss_articles(
            self._vendor("aliyun_qwen", "Q", arts), "2099-12-31")
        self.assertEqual({a.url for a in kept},
                         {"https://x.cn/docs#a", "https://x.cn/docs#b"},
                         "非白名单厂商的同页锚点必须各自保留")

    def test_original_title_surfaces_in_index(self):
        """带英文原文（title=英文 / zh_title=中文）的条目：索引显示中文、原文列填英文。"""
        arts = [crawler_llm_intel.Article(
            title="Grok 4.6 is here", url="https://x.ai/news/grok-4-6",
            date="2026-08-14", zh_title="Grok 4.6 已发布")]
        v = self._vendor("xai_grok", "xAI", arts)
        crawler_llm_intel.write_rss_feeds(self.out_dir, [v], base_url="")
        row = json.loads((self.out_dir / "articles.json").read_text(
            encoding="utf-8"))["articles"][0]
        self.assertEqual(row[0], "Grok 4.6 已发布", "显示标题用冻结的中文")
        self.assertEqual(row[4], "Grok 4.6 is here", "original_title 用英文原文")

    def test_vendors_index_lists_every_vendor_even_without_dates(self):
        """厂商索引必须列出**全部**厂商，包括文章全无日期、因而进不了聚合流的那几家。

        回归：当时只从聚合流推导厂商清单会漏掉 3/15 家（google_gemini / meta_llama 全无日期，
        groq 文章都偏旧，排不进当时聚合流的旧 200 条上限），而它们恰恰是"官方没有原生 RSS"最需要被订到的。
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

    def test_stale_english_feed_removed_when_vendor_goes_english_less(self):
        """厂商还在、但本轮再也产不出英文镜像时，旧那份 `.en.xml` 必须收掉。

        回归：英文正文被判定为整页复制并清空后，vendors.json 已不再引用该厂商的
        `.en.xml`，而 `write_opml` 是**按文件在不在**决定列不列英文镜像源的 —— 于是
        一份永远不再更新的旧快照会以「活的英文订阅源」挂在 OPML 上给读者。
        """
        self.out_dir.mkdir(parents=True)
        stale = self.out_dir / "llm-news-vendor_e.en.xml"
        stale.write_text("<rss>上一轮的英文镜像旧快照</rss>", encoding="utf-8")
        # 纯中文标题 + 台账里这条已是 index_page：英文侧一条都不合格
        (self.out_dir / "bodies.json").write_text(json.dumps({
            "bodies": {"vendor_e\thttps://e.test/1": {"slug": "x", "en_status": "index_page"}}},
            ensure_ascii=False), encoding="utf-8")
        e = self._vendor("vendor_e", "Vendor E", [
            crawler_llm_intel.Article(title="全新中文动态说明", url="https://e.test/1",
                                      date="2026-01-02")])
        crawler_llm_intel.write_rss_feeds(self.out_dir, [e], clean_removed=True)
        self.assertFalse(stale.exists(), "本轮没出英文镜像，就不许留着上一轮那份")
        self.assertTrue((self.out_dir / "llm-news-vendor_e.xml").is_file(),
                        "中文源与英文侧互不影响")

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

        匹配要求 id 是独立词元：前后都不能是单词字符或连字符。裸子串匹配会被
        `aria-modal="true"` 撞车（modal 是真实厂商 id，drawer 的无障碍属性名里
        恰好含这个词），但那是 ARIA 属性名，不是硬编码厂商列表；JS 里
        `["openai","anthropic"]` 这类字面量前后是引号/方括号，仍会被抓。
        """
        page = (self.repo_root / "docs" / "index.html").read_text(encoding="utf-8")
        yaml_text = (self.repo_root / "llm-intel.yaml").read_text(encoding="utf-8")
        ids = re.findall(r"^\s*-\s*id:\s*([A-Za-z0-9_]+)", yaml_text, re.M)
        self.assertTrue(ids, "没解析到厂商 id —— 解析正则失配，先修测试本身")
        hits = sorted(i for i in ids
                      if re.search(rf"(?<![-\w]){re.escape(i)}(?![\w-])", page))
        self.assertEqual(
            hits, [], f"浏览页硬编码了厂商 id {hits}；厂商清单应取自 feeds/vendors.json")


class TestOpmlAndNewsDocCoverage(unittest.TestCase):
    """OPML 与新闻总文档必须覆盖**自建源**，而不只是厂商官网自带的原生源。

    当时实测：官网有原生 RSS 的只有 3 家（分母是当时全部厂商），其余各家官方页面根本没有
    feed —— 而这正是本仓库自建订阅源存在的理由。旧版两处产物只提原生源：OPML 只列 3 条，
    文档对其余厂商写「未发现 RSS/Atom 链接」且只字不提自建源，读者据此会以为这些厂商订不了。
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

    # 真实厂商 id：用于钉「订阅文档也按 VENDOR_RANK 排、用 display_name」
    _RANK_SCRAMBLE_IDS = ["moonshot_kimi", "openai", "siliconflow",
                          "anthropic", "sensetime_sensenova", "aliyun_qwen"]

    def _scramble_intel(self):
        """故意打乱顺序 + 用旧 brand（不是 display_name）构造，看渲染会不会纠正。"""
        return [self._vendor(vid, f"brand-{vid}",
                              native_feed=f"https://{vid}.example/rss.xml")
                for vid in self._RANK_SCRAMBLE_IDS]

    def test_news_doc_orders_by_vendor_rank(self):
        """回归：`llm-news-feeds.md` 曾沿用 yaml 抓取序，与 README/quotas/浏览页的
        VENDOR_RANK 序不一致（Anthropic 排在 OpenAI 之后、被下调的硅基流动仍压在
        自研厂商之前）。订阅文档必须与其余出口同一顺序。"""
        import re as _re
        md = crawler_llm_intel.render_news_section(self._scramble_intel(), self.BASE)
        ids = _re.findall(r"^### .* \((\w+)\)$", md, _re.M)
        self.assertEqual(ids, sorted(self._RANK_SCRAMBLE_IDS,
                                     key=provider_profiles.vendor_rank_index),
                         "厂商章节顺序必须按 VENDOR_RANK 单调不减")
        # 具体锚点：知名度最高的两家相对顺序、以及「自研>聚合」在订阅文档里同样成立
        self.assertLess(ids.index("anthropic"), ids.index("openai"))
        self.assertLess(ids.index("sensetime_sensenova"), ids.index("siliconflow"))

    def test_news_doc_uses_display_name_not_yaml_brand(self):
        """订阅文档的读者可见名 = display_name（与一览/README 同一展示名），不是 yaml brand。"""
        md = crawler_llm_intel.render_news_section(self._scramble_intel(), self.BASE)
        self.assertIn("### 通义千问 (阿里云) (aliyun_qwen)", md,
                      "aliyun_qwen 章节头应显示 display_name")
        self.assertNotIn("### brand-aliyun_qwen", md, "不得退回 yaml brand")

    def test_opml_orders_by_vendor_rank(self):
        """OPML 是读者真正导入的清单，组内顺序同样要按 VENDOR_RANK。"""
        path = self.out_dir / "llm-news-feeds.opml"
        crawler_llm_intel.write_opml(path, self._scramble_intel(), self.BASE)
        opml = path.read_text(encoding="utf-8")
        pos = {vid: opml.index(f"https://{vid}.example/rss.xml")
               for vid in self._RANK_SCRAMBLE_IDS}
        order = sorted(self._RANK_SCRAMBLE_IDS, key=lambda v: pos[v])
        self.assertEqual(order, sorted(self._RANK_SCRAMBLE_IDS,
                                       key=provider_profiles.vendor_rank_index),
                         "OPML 原生源分组必须按 VENDOR_RANK 排")

    def test_opml_uses_display_name(self):
        path = self.out_dir / "llm-news-feeds.opml"
        crawler_llm_intel.write_opml(path, self._scramble_intel(), self.BASE)
        opml = path.read_text(encoding="utf-8")
        self.assertIn("通义千问 (阿里云)", opml, "OPML 标题须用 display_name")
        self.assertNotIn("brand-aliyun_qwen", opml)

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


class TestNewsIntelFilterRemoved(unittest.TestCase):
    """动态条目**不再做「情报过滤」** —— 用户 2026-10-10 定。

    此前按标题词表剔除客户案例 / 公司新闻 / 营销 / 教程 / 研究论文，只留「看起来像
    模型发布或 API 变更」的条目。那是编辑口味而不是正确性判断，且按措辞判断本来就不稳：
    实测把 Gemini 版本说明 40 条里的 27 条判成非情报，含「Gemini Robotics ER 2 公开预览版」、
    「Antigravity Agent 09-2026」、「文件搜索」这些正是本仓库该收录的东西。

    这里钉的是**新口径**：厂商官方发布的内容一律收录。真正的「不是一篇文章」由别处的
    正确性判据守着（日期当标题、栏目名当标题、通用锚文本、表格表头、已废弃源前缀）。
    """

    def test_filter_is_gone_rather_than_neutered(self):
        """整段移除，而不是留个永远返回 True 的空壳。

        留空壳的话，下一个读代码的人会分不清哪套口径在生效 —— 而这套口径恰恰是
        按措辞猜的，最需要有人能一眼看出它已经不成立了。
        """
        src = (Path(__file__).resolve().parent / "crawler_llm_intel.py").read_text(
            encoding="utf-8")
        for gone in ("def is_intel_news", "NEWS_INTEL_SIGNALS", "NEWS_NOISE_PATTERNS",
                     "NEWS_SIGNAL_STRONG", "news_filtered"):
            self.assertNotIn(gone, src, "%s 应已整段移除" % gone)
        self.assertFalse(hasattr(crawler_llm_intel.VendorIntel, "news_filtered"))

    def test_collect_news_articles_keeps_everything(self):
        """旧判据下会被剔的三类标题，现在必须全部留下，且保持日期倒序。"""
        xml = ('<?xml version="1.0"?><rss version="2.0"><channel>'
               '<item><title>Introducing GPT-5.5</title>'
               '<link>https://x.example/a</link>'
               '<pubDate>Mon, 01 Sep 2026 00:00:00 +0000</pubDate></item>'
               '<item><title>How Cooley is accelerating IPO work with ChatGPT</title>'
               '<link>https://x.example/b</link>'
               '<pubDate>Tue, 02 Sep 2026 00:00:00 +0000</pubDate></item>'
               '<item><title>Fine-tuning a 350M Model for Better Structured Outputs</title>'
               '<link>https://x.example/c</link>'
               '<pubDate>Wed, 03 Sep 2026 00:00:00 +0000</pubDate></item>'
               '</channel></rss>')
        page = crawler_llm_intel.PageResult(
            url="https://x.example/feed.xml", stype="feed", ok=True,
            final_url="https://x.example/feed.xml", raw=xml)
        intel = crawler_llm_intel.VendorIntel(
            vendor_id="openai", brand="OpenAI", homepage="", products=[])
        intel.news_pages = [page]
        crawler_llm_intel.collect_news_articles(intel, session=None)
        self.assertEqual([a.title for a in intel.all_news_articles],
                         ["Fine-tuning a 350M Model for Better Structured Outputs",
                          "How Cooley is accelerating IPO work with ChatGPT",
                          "Introducing GPT-5.5"],
                         "客户案例与教程现在都要收录，且保持日期倒序")
        self.assertEqual(len(intel.news_articles), 3,
                         "主文档展示最新 5 篇；这里总共就 3 条")



class TestRetiredNewsSource(unittest.TestCase):
    """已废弃新闻源的历史条目要收口。

    归档是「增量合并、只增不减」的 —— 从 yaml 删掉一个源之后，它的历史条目会一直留在
    `llm-news/*.md` 与单厂商 feed 里。实例：`cloud.google.com/blog/products/`
    （Google Cloud 通用 AI 博客：Gartner 魔力象限、印度板球转播、I/O 大会速览）
    于 2026-09-18 从 yaml 移除，当时归档里仍有 11 条残留（收口过滤器装上后已清零），故需本过滤器。
    """

    def test_retired_url_recognised(self):
        self.assertTrue(crawler_llm_intel._is_retired_news_url(
            "https://cloud.google.com/blog/products/ai-machine-learning/the-new-gemini"))
        self.assertFalse(crawler_llm_intel._is_retired_news_url(
            "https://ai.google.dev/gemini-api/docs/changelog#09-17-2026"))

    def test_content_reviewed_nonarticles_blocked(self):
        """内容复核确认「不是文章」的个别条目：栏目卡片 / 表单页。只挡这两条，
        不误伤同厂商真帖子/真文章。"""
        r = crawler_llm_intel._is_retired_news_url
        self.assertTrue(r("https://poolside.ai/blog#d-2025-07-17-17"), "poolside 栏目卡片")
        self.assertTrue(r("https://openai.com/form/stargate-infrastructure"), "openai 表单页")
        # 同厂商真实文章不得被挡
        self.assertFalse(r("https://poolside.ai/blog#d-2026-07-21-19"), "poolside 真帖子卡片")
        self.assertFalse(r("https://openai.com/index/introducing-gpt-5-5"), "openai 真文章")

    def test_bailian_changelog_retired_without_hitting_sibling_docs(self):
        """阿里云百炼「新发布模型」变更日志（2026-09-30 换成千问官方动态接口）。

        同一条判据：聚合第三方模型的平台不汇聚 —— 实测 109 条里 68 条是第三方模型上架，
        含「免费/限免」「下线」「价格/计费」的各 0 条。同厂商的 first_call_docs 源
        （`first-api-call-to-qwen`，情报页）路径不同，不得被误伤。
        """
        self.assertTrue(crawler_llm_intel._is_retired_news_url(
            "https://help.aliyun.com/zh/model-studio/newly-released-models"))
        # 归档里的历史条目带日期锚点，前缀匹配要连锚点一起挡住
        self.assertTrue(crawler_llm_intel._is_retired_news_url(
            "https://help.aliyun.com/zh/model-studio/newly-released-models#2026-09-01"))
        self.assertFalse(crawler_llm_intel._is_retired_news_url(
            "https://help.aliyun.com/zh/model-studio/first-api-call-to-qwen"),
            "同厂商的情报页源不受影响")
        self.assertFalse(crawler_llm_intel._is_retired_news_url(
            "https://qwen.ai/blog?id=qwen3-max"), "新源的条目当然不能挡")
        # yaml 侧：百炼源已删、千问接口源已登记（换源两半都要在）
        root = Path(__file__).resolve().parent
        _vendors, sources = crawler_llm_intel.parse_yaml(root / "llm-intel.yaml")
        urls = [s.get("url") or "" for s in sources]
        self.assertFalse(any("newly-released-models" in u for u in urls),
                         "百炼变更日志源应从 yaml 移除")
        self.assertTrue(any("qwen.ai/api/v2/article/retrieval" in u for u in urls),
                        "千问官方动态接口应已登记")

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
    """合并流默认 **50 条**（2026-10-06 定）；页面仍读全量 articles.json 索引。

    历史：200（全文进 feed 后定）→ 30 → 50。全文单条 ~18 KB，200 条 ≈ 3.3 MB 实测
    大陆 ~14 KB/s × 45s 订不动。策略「保全文、砍数量」而非「摘要化」（用户要全文）。
    50 条 ≈ 900 KB 未压缩，靠 gzip（→~320 KB）或 EdgeOne 边缘加速订得动；30 条是
    GitHub Pages 未压缩下的保守值。想拉更多：`--rss-limit N` 或订单厂商源；
    页面读不受限的索引，reader 读全文 .md。见 rss-redesign spec §3.1。
    """

    def _intel(self, n):
        v = crawler_llm_intel.VendorIntel(vendor_id="v", brand="V", homepage="", products=[])
        v.all_news_articles = [
            crawler_llm_intel.Article(title=f"标题{i}", url=f"https://v.example/news/{i}",
                                      date=f"2026-01-{i:02d}")
            for i in range(1, n + 1)
        ]
        return v

    def test_merged_feed_default_limit_is_50(self):
        """默认（RSS_MERGED_LIMIT = 50）截到最近 50 条。"""
        self.assertEqual(crawler_llm_intel.RSS_MERGED_LIMIT, 50,
                         "合并流默认 50 条；要放开请显式传 merged_limit=0")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "feeds"
            crawler_llm_intel.write_rss_feeds(out, [self._intel(80)])
            merged = (out / "llm-news-all.xml").read_text(encoding="utf-8")
            self.assertEqual(merged.count("<item>"), 50, "默认 50 条上限应生效")
            self.assertIn("最近 50 条",
                          crawler_llm_intel.merged_scope_text(
                              crawler_llm_intel.RSS_MERGED_LIMIT))

    def test_merged_limit_zero_still_unlimited(self):
        """显式 merged_limit=0 走"不限制"分支（`--rss-limit 0` 逃生阀仍有效）。"""
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "feeds"
            crawler_llm_intel.write_rss_feeds(out, [self._intel(60)], merged_limit=0)
            merged = (out / "llm-news-all.xml").read_text(encoding="utf-8")
            self.assertEqual(merged.count("<item>"), 60,
                             "merged_limit=0 时不截；文案改口'收录全部有日期的条目'")
            self.assertIn("收录全部有日期的条目",
                          crawler_llm_intel.merged_scope_text(0))

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

    # `Grok 4.1` 实测被 Google 音译成「格罗克4.1」：型号守卫（字母紧邻数字）
    # 被中间的空格隔开拦不住，需要「品牌 + 版本号」整标题守卫。
    SAMPLES_BRAND_VERSION = (
        "Grok 4.1",
        "Grok 4 Fast",
        "Codestral 25.01",
    )

    def test_brand_version_titles_are_returned_unchanged(self):
        for s in self.SAMPLES_BRAND_VERSION:
            self.assertTrue(provider_profiles._is_brand_version_title(s), s)
            self.assertEqual(provider_profiles.translate_to_zh(s), s,
                             f"品牌+版本号标题被音译风险拦截失败: {s}")
        # 真句子不受该守卫影响（存在小写散文词即照常翻译）
        for s in ("New release 1.2 for everyone", "version 2 is out"):
            self.assertFalse(provider_profiles._is_brand_version_title(s), s)

    def test_transliterated_brands_are_restored_in_translations(self):
        r = provider_profiles._restore_brand_names
        self.assertEqual(
            r("介绍克劳德寓言 5.1 和克劳德神话 5.1",
              "Introducing Claude Fable 5.1 and Claude Mythos 5.1"),
            "介绍Claude寓言 5.1 和Claude神话 5.1")
        self.assertEqual(r("PowerPoint 版 格洛克", "PowerPoint 版 Grok"),
                         "PowerPoint 版 Grok")
        # CI 实测音译过的新族：Laguna → 拉古纳（证据行「开始使用拉古纳」）
        self.assertEqual(r("开始使用拉古纳。限时免费使用。",
                           "Start using Laguna. Free to use for a limited time."),
                         "开始使用Laguna。限时免费使用。")
        # Falcon 家族：Google 把 "Falcon-Emirati" 意译成「猎鹰阿联酋」、把 "Falcon"
        # 意译成「猎鹰」——模型名一旦意译就查不到。复合名先整串复原，再兜通用 Falcon。
        self.assertEqual(
            r("猎鹰阿联酋：当LLM学习方言、文化和细微差别时",
              "Falcon-Emirati: When an LLM Learns the Dialect, the Culture, and the Nuance"),
            "Falcon-Emirati：当LLM学习方言、文化和细微差别时")
        self.assertEqual(r("欢迎使用猎鹰 3 系列开源模型",
                           "Welcome to the Falcon 3 Family of Open Models"),
                         "欢迎使用Falcon 3 系列开源模型")
        # 原文里没有该英文品牌时不能乱动（官方中文名/巧合词）
        self.assertEqual(r("克劳德是一名常见译名", "没有英文品牌的中文句子"),
                         "克劳德是一名常见译名")
        # 整串就是音译词：保守不动
        self.assertEqual(r("克劳德", "Claude"), "克劳德")

    def test_published_artifacts_have_no_transliterated_brands(self):
        """已发布产物里不允许残留品牌音译/直译（防线装好前的历史数据回归守卫）。

        扫描范围是**标题与摘要**——feed 的 `<content:encoded>` 整段正文不在守卫内：
        正文里"搜索拉取"（索+拉相邻）与人名音译（Solaiman → 索拉曼）都会误命中
        "索拉"，而正文质量走 agent 逐篇翻译 + 抽查，不靠这个字符串守卫。
        """
        root = Path(__file__).resolve().parent
        pat = re.compile(r"克劳德|格罗克|格洛克|共纹|拥抱人脸|拥抱脸部|拥抱脸|抱脸|拥抱面"
                         r"|法学硕士|双子座|稳定扩散|变压器|扩散器|米斯特拉尔|迷你最大"
                         r"|索拉|反重力|变形金刚|活生生|拉古纳|元人工|公共人工智能|猎鹰"
                         r"|贴片时间序列|双子座3")
        # provider_profiles.py 自身是音译对照表（守卫定义），排除
        files = [root / "README.md", root / "llm-news-feeds.md"]
        files += sorted((root / "llm-news").glob("*.md"))
        files += sorted((root / "docs" / "feeds").glob("*.xml"))
        bad = []
        CDATA_OPEN = "<content:encoded>"
        CDATA_CLOSE = "</content:encoded>"
        for f in files:
            if not f.exists():
                continue
            text = f.read_text(encoding="utf-8")
            if f.suffix == ".xml":
                # 剥掉 <content:encoded>...</content:encoded> 段，只扫标题/description
                text = re.sub(re.escape(CDATA_OPEN) + r".*?" + re.escape(CDATA_CLOSE),
                              "", text, flags=re.DOTALL)
            for i, line in enumerate(text.splitlines(), 1):
                if pat.search(line):
                    bad.append(f"{f.name}:{i}: {line[:60]}")
        self.assertEqual(bad, [], "产物里残留了被音译的品牌名:\n" + "\n".join(bad))


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


class TestArchivePollutionGuards(unittest.TestCase):
    """归档污染三源的守卫：非法日期、结构 4 日期渗漏、索引原文列丢失。

    归档按 URL 增量合并、不会自我纠正 —— 这三类污染一旦写入就永久留存。
    """

    def setUp(self):
        self._quiet = contextlib.redirect_stderr(io.StringIO())
        self._quiet.__enter__()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.feeds_dir = Path(self.temp_dir.name) / "feeds"
        self._saved_orig = dict(crawler_llm_intel._LAST_ORIG_INDEX)

    def tearDown(self):
        crawler_llm_intel._LAST_ORIG_INDEX.clear()
        crawler_llm_intel._LAST_ORIG_INDEX.update(self._saved_orig)
        self.temp_dir.cleanup()
        self._quiet.__exit__(None, None, None)

    def test_illegal_dates_dropped(self):
        """`2025-13-01` 这类日历上不存在的日期：字符串比较防不住（它 < 今天），
        必须按日历校验后丢弃，否则永不自纠。"""
        self.assertEqual(crawler_llm_intel._drop_future_date("2025-13-01"), "")
        self.assertEqual(crawler_llm_intel._drop_future_date("2026-02-30"), "")
        self.assertEqual(crawler_llm_intel._drop_future_date("2026-00-10"), "")
        self.assertEqual(crawler_llm_intel._drop_future_date("2026-09-17"), "2026-09-17")

    def test_normalize_feed_date_rejects_illegal(self):
        self.assertEqual(crawler_llm_intel.normalize_feed_date("2026年13月1日"), "")
        self.assertEqual(crawler_llm_intel.normalize_feed_date("Feb 30, 2026"), "")
        self.assertEqual(crawler_llm_intel.normalize_feed_date("2026-02-28"), "2026-02-28")

    def test_tz_tomorrow_allowed_far_future_dropped(self):
        """东九区源站凌晨发布而管线跑在 UTC 时，源日期是「本地明天」：放行一天。"""
        tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        day_after = (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")
        self.assertEqual(crawler_llm_intel._drop_future_date(tomorrow), tomorrow,
                         "时区偏差最多 26h，明天必须放行")
        self.assertEqual(crawler_llm_intel._drop_future_date(day_after), "")

    def test_structure4_date_does_not_seep_into_undated_section(self):
        """结构 4：日期分节结束后，后面**无日期分节**的子标题不得继承上一个日期。

        Regression: 原判据把「与分节同级的非日期标题」只是跳过、不清 sec_date，
        于是日期渗进后续无日期分节，抓出「2026-09-01｜产品概览子条目」这类
        日期与内容错配的归档条目。
        """
        html = """
        <html><body>
          <h2 id="2026年9月">2026年9月</h2>
          <h3 id="a">条目 A：新模型上线</h3><p>说明一</p>
          <h3 id="b">条目 B：计费调整</h3><p>说明二</p>
          <h3 id="c">条目 C：SDK 更新</h3><p>说明三</p>
          <h2 id="overview">产品概览</h2>
          <h3 id="d">概览子页 D</h3><p>不是动态</p>
          <h3 id="e">概览子页 E</h3><p>不是动态</p>
        </body></html>"""
        page = crawler_llm_intel.PageResult(
            url="https://s.example/docs/changelog", stype="changelog", ok=True,
            final_url="https://s.example/docs/changelog", raw=html)
        arts = crawler_llm_intel.extract_changelog_sections(page)
        self.assertEqual([a.title for a in arts],
                         ["条目 A：新模型上线", "条目 B：计费调整", "条目 C：SDK 更新"],
                         "无日期分节下的子标题不得带着上一分节的日期混进归档")
        self.assertTrue(all(a.date == "2026-09-01" for a in arts))

    def test_index_orig_recovers_from_previous_for_archive_titles(self):
        """纯归档来源的文章（内存里标题已是汉化归档标题，orig == t）：
        写全量索引时必须回退上一版索引的英文原文。

        Regression: 原回退条件是 `orig != t and 无英文` —— 纯归档文章恰恰
        orig == t，永远进不了回退分支；一旦某轮实抓丢了原文列（实测 2769 条
        为空），后续所有轮次都拿不回来。
        """
        self.feeds_dir.mkdir(parents=True)
        (self.feeds_dir / "articles.json").write_text(json.dumps({
            "fields": ["title", "url", "vendor", "date", "original_title"],
            "count": 1,
            "articles": [["甲文章标题", "https://a.com/1", "vendor_a",
                          "2026-09-01", "Original English Headline"]],
        }, ensure_ascii=False), encoding="utf-8")
        crawler_llm_intel._LAST_ORIG_INDEX.clear()
        crawler_llm_intel.load_original_titles(self.feeds_dir / "articles.json")
        art = crawler_llm_intel.Article(
            title="甲文章标题", url="https://a.com/1", date="2026-09-01")
        art.zh_title = "甲文章标题"  # 归档合并后 title 已被冻结成中文
        intel = crawler_llm_intel.VendorIntel(
            vendor_id="vendor_a", brand="Vendor A", homepage="https://a.com",
            products=[], all_news_articles=[art])
        with mock.patch.object(
                crawler_llm_intel, "translate_to_zh",
                side_effect=AssertionError("zh_title 已给出时不应再翻译")):
            crawler_llm_intel.write_rss_feeds(self.feeds_dir, [intel],
                                              clean_removed=False)
        data = json.loads((self.feeds_dir / "articles.json").read_text(encoding="utf-8"))
        self.assertEqual(data["articles"][0][4], "Original English Headline",
                         "上一版索引里的英文原文必须回填，不得静默置空")

    def test_index_orig_not_invented_when_previous_empty(self):
        """上一版索引也没有原文时保持为空，不得把中文标题自己填进原文列。"""
        self.feeds_dir.mkdir(parents=True)
        crawler_llm_intel._LAST_ORIG_INDEX.clear()
        art = crawler_llm_intel.Article(
            title="甲文章标题", url="https://a.com/1", date="2026-09-01")
        art.zh_title = "甲文章标题"
        intel = crawler_llm_intel.VendorIntel(
            vendor_id="vendor_a", brand="Vendor A", homepage="https://a.com",
            products=[], all_news_articles=[art])
        crawler_llm_intel.write_rss_feeds(self.feeds_dir, [intel],
                                          clean_removed=False)
        data = json.loads((self.feeds_dir / "articles.json").read_text(encoding="utf-8"))
        self.assertEqual(data["articles"][0][4], "")


class TestPartialRoundGuardrails(unittest.TestCase):
    """部分数据轮护栏：临时抓不到 ≠ 厂商下线，绝不能因此抹掉历史产物。

    一次源站抖动 / runner 出口被墙，会让在册厂商本轮 all_news_articles 为空。
    原判据把「本轮没抓到」当成「厂商下线」，clean_removed 直接删归档与订阅源 ——
    归档是只增不减的历史记录，删一次永久丢失；订阅者还会读到 404。
    """

    def setUp(self):
        self._quiet = contextlib.redirect_stderr(io.StringIO())
        self._quiet.__enter__()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.news_dir = Path(self.temp_dir.name) / "llm-news"
        self.news_dir.mkdir(parents=True)
        self.feeds_dir = Path(self.temp_dir.name) / "feeds"
        self._saved_orig = dict(crawler_llm_intel._LAST_ORIG_INDEX)

    def tearDown(self):
        crawler_llm_intel._LAST_ORIG_INDEX.clear()
        crawler_llm_intel._LAST_ORIG_INDEX.update(self._saved_orig)
        self.temp_dir.cleanup()
        self._quiet.__exit__(None, None, None)

    def _intel(self, vid, articles):
        return crawler_llm_intel.VendorIntel(
            vendor_id=vid, brand=vid.upper(), homepage=f"https://{vid}.com",
            products=[], all_news_articles=articles)

    def test_intel_failure_abort_threshold(self):
        """纯函数：多数失败才中止；健康巡检（近零失败）与小样本都不触发。"""
        abort = crawler_llm_intel.intel_failure_abort
        self.assertFalse(abort(100, 100), "全成功")
        self.assertFalse(abort(100, 95), "偶发单源失败（5%）远够不着阈值")
        self.assertFalse(abort(100, 51), "49% 失败仍低于多数线")
        self.assertTrue(abort(100, 50), "恰好 50% 失败达阈值")
        self.assertTrue(abort(100, 10), "90% 失败：系统性故障")
        self.assertFalse(abort(4, 0), "小样本（< MIN_TOTAL）不套用比例阈值")

    def test_clean_removed_keeps_transient_failure_archive(self):
        """在册厂商本轮文章为空（临时抓不到）：历史归档必须原样保留。"""
        arch = self.news_dir / "vendor_a.md"
        arch.write_text("## 全部文章（共 1 篇）\n\n"
                        "1. [历史文章](https://a.com/old)（2025-01-01）\n",
                        encoding="utf-8")
        vendor_a = self._intel("vendor_a", [])  # 本轮动态页全失败，文章为空
        crawler_llm_intel.write_news_archives(self.news_dir, [vendor_a],
                                              clean_removed=True)
        self.assertTrue(arch.exists(), "在册厂商的归档不得因一轮抓取失败被删")
        self.assertIn("https://a.com/old", arch.read_text(encoding="utf-8"),
                      "历史文章必须保留（只增不减）")

    def test_clean_removed_removes_vendor_absent_from_list(self):
        """确认下线（从 yaml 移除 → 不在本轮清单）：归档照删不误。"""
        (self.news_dir / "vendor_gone.md").write_text("old", encoding="utf-8")
        vendor_a = self._intel(
            "vendor_a",
            [crawler_llm_intel.Article(title="New A", url="https://a.com/new")])
        crawler_llm_intel.write_news_archives(self.news_dir, [vendor_a],
                                              clean_removed=True)
        self.assertFalse((self.news_dir / "vendor_gone.md").exists(),
                         "已从清单消失的厂商归档应被清理")

    def test_rss_clean_removed_keeps_transient_failure_feed(self):
        """在册厂商本轮无可收录条目：旧订阅源文件保留，避免订阅者读到 404。"""
        self.feeds_dir.mkdir(parents=True)
        (self.feeds_dir / "llm-news-vendor_a.xml").write_text("<rss/>", encoding="utf-8")
        (self.feeds_dir / "llm-news-vendor_gone.xml").write_text("<rss/>", encoding="utf-8")
        vendor_a = self._intel("vendor_a", [])  # 本轮抓不到，arts 为空
        crawler_llm_intel.write_rss_feeds(self.feeds_dir, [vendor_a],
                                          clean_removed=True)
        self.assertTrue((self.feeds_dir / "llm-news-vendor_a.xml").exists(),
                        "在册厂商的订阅源不得因一轮抓取失败被删")
        self.assertFalse((self.feeds_dir / "llm-news-vendor_gone.xml").exists(),
                         "已下线厂商的订阅源应被清理")


class TestFeedsBaseDerivation(unittest.TestCase):
    """订阅源对外前缀：优先 docs/CNAME（自定义域名），其次按 Actions 注入的
    GITHUB_REPOSITORY 推导（fork 后无需改代码）。

    `_repo_root` 注入到临时目录：真实仓库带有 docs/CNAME，不注入的话
    GITHUB_REPOSITORY 分支永远测不到（CNAME 会先命中）。
    """

    def setUp(self):
        self._orig = os.environ.get("GITHUB_REPOSITORY")
        self.temp_dir = tempfile.TemporaryDirectory()
        self.fake_root = Path(self.temp_dir.name)
        self._orig_root = crawler_llm_intel._repo_root
        crawler_llm_intel._repo_root = lambda: self.fake_root

    def tearDown(self):
        crawler_llm_intel._repo_root = self._orig_root
        self.temp_dir.cleanup()
        if self._orig is None:
            os.environ.pop("GITHUB_REPOSITORY", None)
        else:
            os.environ["GITHUB_REPOSITORY"] = self._orig

    def _write_cname(self, text: str):
        docs = self.fake_root / "docs"
        docs.mkdir(exist_ok=True)
        (docs / "CNAME").write_text(text, encoding="utf-8")

    def test_cname_wins_over_github_repository(self):
        """配了自定义域名后 github.io 会 301 跳转，rel=self 必须直接给规范地址。"""
        self._write_cname("free-llm-intel.aishort.top\n")
        os.environ["GITHUB_REPOSITORY"] = "someone/free-llm-intel"
        self.assertEqual(crawler_llm_intel.default_feeds_base(),
                         "https://free-llm-intel.aishort.top/feeds")

    def test_cname_tolerates_url_form_and_extra_lines(self):
        # Pages 只写裸域名，但有人手工填成 URL / 带注释行——取首行、剥协议、去尾斜线
        self._write_cname("https://example.com/\n# old domain\n")
        self.assertEqual(crawler_llm_intel.default_feeds_base(),
                         "https://example.com/feeds")

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


class TestNetworkLayerPassthrough(unittest.TestCase):
    """网络层参数透传与 URL 规范化语义。

    三组回归：
    1) `_norm_url` 曾把整条 URL 小写并丢掉 query —— path/query 大小写敏感
       （`/Docs/Page` 与 `/docs/page` 可以是两个资源；`?Id=x` 与 `?id=x` 同理），
       只有 scheme/host 可以小写；丢 query 会把带参数的文章链接折叠错。
    2) `fetch_url` 曾让 feed 走浏览器兜底 —— 浏览器渲染 XML 得到 HTML 树，
       parse_html 会覆盖 result.raw，而 parse_feed_xml 消费的正是 raw（item 整批丢）；
       短 XML 被判 sparse 误入兜底同样把好源弄坏；失败时兜底把「失败」翻成「ok 但空」。
    3) `collect_news_articles` 的步骤 2（发现的 feed）与步骤 3（详情页补标题）
       曾硬编码默认值，--delay / --timeout 传不进去：对同一站点连续请求不设间隔
       容易触发限流。
    """

    # ---- 1) _norm_url ----

    def test_norm_url_keeps_path_and_query_case(self):
        self.assertEqual(
            crawler_llm_intel._norm_url("HTTPS://X.example/Docs/Page?Id=AbC"),
            "https://x.example/Docs/Page?Id=AbC")

    def test_norm_url_keeps_query_and_drops_fragment(self):
        self.assertEqual(
            crawler_llm_intel._norm_url("https://x.example/p?a=1#sec"),
            "https://x.example/p?a=1")
        # 无 query 时不追加 "?"
        self.assertEqual(
            crawler_llm_intel._norm_url("https://x.example/p/"),
            "https://x.example/p")

    def test_article_key_still_keeps_fragment_after_norm_fix(self):
        self.assertEqual(
            crawler_llm_intel._article_key("https://x.example/Docs#aB"),
            "https://x.example/Docs#ab")

    # ---- 2) feed 不进浏览器兜底 ----

    def _fake_browser(self):
        browser = mock.Mock()
        browser.enabled = True
        # render 成功时返回 (html, final_url, status_code) 三元组；必须让它「成功」，
        # 否则守卫被拆掉时兜底也只是空转，断不出回归
        browser.render.return_value = (
            "<html><body>%s</body></html>" % ("x" * 300),
            "https://x.example/f.xml", 200)
        return browser

    def test_fetch_url_feed_skips_browser_fallback(self):
        browser = self._fake_browser()
        cases = {
            "ok+raw（正常源）": crawler_llm_intel.PageResult(
                url="https://x.example/f.xml", stype="feed", ok=True,
                final_url="https://x.example/f.xml", raw="<rss/>", status_code=200),
            "sparse（短 XML 误判）": crawler_llm_intel.PageResult(
                url="https://x.example/f.xml", stype="feed", ok=True,
                final_url="https://x.example/f.xml", raw="<rss/>",
                sparse=True, status_code=200),
            "403（失败不得被兜底翻成 ok 但空）": crawler_llm_intel.PageResult(
                url="https://x.example/f.xml", stype="feed", ok=False,
                final_url="https://x.example/f.xml", status_code=403),
        }
        for label, pr in cases.items():
            browser.render.reset_mock()
            with mock.patch.object(crawler_llm_intel, "_fetch_with_requests",
                                   return_value=pr):
                out = crawler_llm_intel.fetch_url(
                    None, "https://x.example/f.xml", "feed", browser=browser)
            self.assertIs(out, pr, label)
            browser.render.assert_not_called()
        # 守卫的另一半意义：raw 不被浏览器渲染的 HTML 覆盖（parse_feed_xml 消费 raw）
        self.assertEqual(cases["ok+raw（正常源）"].raw, "<rss/>")
        self.assertFalse(cases["403（失败不得被兜底翻成 ok 但空）"].ok)

    def test_fetch_url_html_still_uses_browser_fallback(self):
        """对照组：同判据下 HTML 页必须仍走浏览器兜底（守卫只豁免 feed）。"""
        browser = self._fake_browser()
        # render 成功时返回 (html, final_url, status_code) 三元组
        browser.render.return_value = (
            "<html><body>%s</body></html>" % ("x" * 300),
            "https://x.example/p", 200)
        pr = crawler_llm_intel.PageResult(
            url="https://x.example/p", stype="news", ok=False,
            final_url="https://x.example/p", status_code=403)
        with mock.patch.object(crawler_llm_intel, "_fetch_with_requests",
                               return_value=pr):
            crawler_llm_intel.fetch_url(None, "https://x.example/p", "news",
                                        browser=browser)
        browser.render.assert_called_once()

    # ---- 3) delay / timeout 透传 ----

    def test_collect_news_passes_timeout_to_discovered_feeds(self):
        page = crawler_llm_intel.PageResult(
            url="https://x.example/blog", stype="news", ok=True,
            final_url="https://x.example/blog",
            feeds=["https://x.example/feed.xml"], text="y" * 300)
        intel = crawler_llm_intel.VendorIntel(
            vendor_id="openai", brand="OpenAI", homepage="", products=[])
        intel.news_pages = [page]
        timeout = (3.0, 9.0)
        with mock.patch.object(crawler_llm_intel, "fetch_feed_articles",
                               return_value=[]) as m_feed, \
                mock.patch.object(crawler_llm_intel.time, "sleep") as m_sleep:
            crawler_llm_intel.collect_news_articles(
                intel, session=None, delay=0.7, timeout=timeout)
        m_feed.assert_called_once_with(None, "https://x.example/feed.xml",
                                       stype="news", timeout=timeout)
        m_sleep.assert_any_call(0.7)

    def test_collect_news_passes_timeout_to_detail_pages(self):
        page = crawler_llm_intel.PageResult(
            url="https://x.example/blog", stype="news", ok=True,
            final_url="https://x.example/blog", text="y" * 300)
        intel = crawler_llm_intel.VendorIntel(
            vendor_id="openai", brand="OpenAI", homepage="", products=[])
        intel.news_pages = [page]
        art = crawler_llm_intel.Article(title="查看详情",
                                        url="https://x.example/a")
        resp = mock.Mock(status_code=200, text="<html><title>Introducing GPT-5.5 deep dive</title></html>",
                         url="https://x.example/a", encoding="utf-8")
        session = mock.Mock()
        session.get.return_value = resp
        timeout = (4.0, 11.0)
        with mock.patch.object(crawler_llm_intel, "extract_articles_from_page",
                               return_value=[art]), \
                mock.patch.object(crawler_llm_intel.time, "sleep") as m_sleep:
            crawler_llm_intel.collect_news_articles(
                intel, session=session, delay=0.5, timeout=timeout)
        session.get.assert_called_once_with("https://x.example/a",
                                            timeout=timeout,
                                            allow_redirects=True)
        m_sleep.assert_any_call(0.5)


class TestLowSeverityFixes(unittest.TestCase):
    """低危批量修复的回归守卫。

    1) update_news_md 曾把 section 直接当 re.sub 替换串：标题里一旦含反斜杠
       （Windows 路径 / LaTeX / 正则示例的文章标题），`\\1`、`\\g` 会被当转义序列
       解释——文档被静默改写甚至直接报错。
    2) append_intel_changelog 同日重跑会把同一批变化再追加一遍（重复厂商块 →
       变化流重复 guid → 阅读器把同一件事推两次）。
    3) OPML 的「情报变化」组曾无条件列出：该流「两类事件都没有就不产出文件」，
       新 fork 首轮导入 OPML 会订到一个 404。
    4) _fetch_with_requests 曾对一切 >=400 重试：404/405 是源站的明确答复，
       重试只是白等 1 秒、多打一次人家的服务器。
    5) parse_archived_articles 曾把读文件失败吞成空列表：增量合并会**静默丢掉**
       该归档的全部历史条目（违反「只增不减」），日志里毫无痕迹。
    6) translate_to_zh 曾静默吞掉一切异常：翻译端点整轮不可用时全部标题安静地
       回退英文，CI 日志里没有任何线索。
    """

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    # ---- 1) re.sub 替换串 ----

    def test_update_news_md_section_with_backslashes_is_literal(self):
        path = self.root / "news.md"
        # 必须先落一份带标记的旧文档：文件不存在时走的是**字符串拼接**分支，
        # 只有旧文档里已有 NEWS_BEGIN/END 才会走 pattern.sub —— 那才是替换串
        # 被 re.sub 解释转义的地方（首版测试没铺旧文档，sabotage 拆掉 lambda
        # 也照样绿，等于什么都没测到）。
        path.write_text(crawler_llm_intel.NEWS_BEGIN + "\n旧内容\n"
                        + crawler_llm_intel.NEWS_END + "\n", encoding="utf-8")
        section = (crawler_llm_intel.NEWS_BEGIN + "\n"
                   r"- [C:\Users\docs 与 \1 与 \g<x> 的标题](https://x.example/a)"
                   "\n" + crawler_llm_intel.NEWS_END + "\n")
        crawler_llm_intel.update_news_md(path, section)
        self.assertIn(r"C:\Users\docs 与 \1 与 \g<x>",
                      path.read_text(encoding="utf-8"),
                      "替换串里的反斜杠必须原样落盘，不得被 re.sub 解释")

    # ---- 2) 变更日志同日去重 ----

    @staticmethod
    def _entry(vid="vendor_a", brand="Vendor A", summary="额度翻倍",
               diffs=(("free_quota", "旧额度", "新额度"),)):
        return {"vendor_id": vid, "brand": brand, "summary": summary,
                "diffs": list(diffs)}

    def test_changelog_same_day_rerun_does_not_duplicate(self):
        p = self.root / crawler_llm_intel.CHANGELOG_MD
        crawler_llm_intel.append_intel_changelog(p, "2026-09-27", [self._entry()])
        crawler_llm_intel.append_intel_changelog(p, "2026-09-27", [self._entry()])
        content = p.read_text(encoding="utf-8")
        self.assertEqual(content.count("### Vendor A"), 1,
                         "同日重跑重放同一批变化不得产生重复厂商块")

    def test_changelog_same_day_new_value_still_appends(self):
        p = self.root / crawler_llm_intel.CHANGELOG_MD
        crawler_llm_intel.append_intel_changelog(p, "2026-09-27", [self._entry()])
        crawler_llm_intel.append_intel_changelog(p, "2026-09-27", [
            self._entry(diffs=[("free_quota", "新额度", "再翻倍")])])
        content = p.read_text(encoding="utf-8")
        self.assertEqual(content.count("### Vendor A"), 2,
                         "同日对同一厂商的再次真实变更（后值不同）照常追加")

    def test_changelog_rerun_mixed_batch_only_appends_new(self):
        p = self.root / crawler_llm_intel.CHANGELOG_MD
        crawler_llm_intel.append_intel_changelog(p, "2026-09-27", [self._entry()])
        crawler_llm_intel.append_intel_changelog(p, "2026-09-27", [
            self._entry(),
            self._entry(vid="vendor_b", brand="Vendor B", summary="新活动")])
        content = p.read_text(encoding="utf-8")
        self.assertEqual(content.count("### Vendor A"), 1)
        self.assertEqual(content.count("### Vendor B"), 1)

    # ---- 3) OPML 情报变化组 ----

    def test_opml_changes_group_follows_feed_existence(self):
        out = self.root / "feeds.opml"
        crawler_llm_intel.write_opml(out, [], feeds_base="https://x/feeds",
                                     changes_feed=False)
        self.assertNotIn("llm-intel-changes.xml", out.read_text(encoding="utf-8"),
                         "变化流未产出时 OPML 不得列出它（导入即 404）")
        crawler_llm_intel.write_opml(out, [], feeds_base="https://x/feeds",
                                     changes_feed=True)
        self.assertIn("llm-intel-changes.xml", out.read_text(encoding="utf-8"))

    # ---- 4) 4xx 不重试 ----

    @staticmethod
    def _resp(code):
        resp = mock.Mock(status_code=code, url="https://x.example/p")
        resp.headers = {}
        resp.encoding = "utf-8"
        resp.text = ""
        return resp

    def _fetch_once(self, session):
        with mock.patch.object(crawler_llm_intel.time, "sleep"):
            return crawler_llm_intel._fetch_with_requests(
                session, "https://x.example/p", "news", (1.0, 2.0), retries=1)

    def test_404_is_not_retried(self):
        session = mock.Mock()
        session.get.return_value = self._resp(404)
        result = self._fetch_once(session)
        self.assertEqual(session.get.call_count, 1,
                         "404 是源站的明确答复，重试只是白等和多打人家服务器")
        self.assertFalse(result.ok)
        self.assertEqual(result.error, "HTTP 404")

    def test_500_is_retried(self):
        session = mock.Mock()
        session.get.return_value = self._resp(500)
        result = self._fetch_once(session)
        self.assertEqual(session.get.call_count, 2, "5xx 是临时故障，照旧重试")
        self.assertFalse(result.ok)

    def test_429_is_retried(self):
        session = mock.Mock()
        session.get.return_value = self._resp(429)
        self._fetch_once(session)
        self.assertEqual(session.get.call_count, 2)

    def test_429_retry_preserves_is_login(self):
        """首抓已判定登录跳转、重试拿到失败壳时，is_login 不得静默丢失。"""
        first = crawler_llm_intel.PageResult(
            url="https://x.example/p", stype="news", ok=False, status_code=429,
            final_url="https://passport.x.example/login?redirect=1", is_login=True)
        second = crawler_llm_intel.PageResult(
            url="https://x.example/p", stype="news", ok=False, status_code=429,
            final_url="https://x.example/p", error="HTTP 429")
        with mock.patch.object(crawler_llm_intel, "_fetch_with_requests",
                               side_effect=[first, second]), \
                mock.patch.object(crawler_llm_intel.time, "sleep"):
            out = crawler_llm_intel.fetch_url(None, "https://x.example/p", "news")
        self.assertIs(out, second)
        self.assertTrue(out.is_login,
                        "重试结果是失败壳时首抓的登录判定必须保留")

    # ---- 5) 归档读取失败必须出声 ----

    def test_parse_archived_articles_warns_on_read_failure(self):
        arch = self.root / "vendor_a.md"
        arch.write_text("- [标题](https://x.example/a)\n", encoding="utf-8")
        err = io.StringIO()
        with mock.patch.object(Path, "read_text",
                               side_effect=OSError("disk on fire")):
            with contextlib.redirect_stderr(err):
                out = crawler_llm_intel.parse_archived_articles(arch)
        self.assertEqual(out, [])
        self.assertIn("warn", err.getvalue(),
                      "读不到归档必须报警：静默空列表会让增量合并丢掉全部历史条目")

    # ---- 6) 翻译失败必须出声（每类异常只报一次） ----

    def test_translate_failure_warns_once_per_exception_type(self):
        saved_failed = set(provider_profiles._TRANS_FAILED)
        saved_warned = set(provider_profiles._TRANS_WARNED)
        provider_profiles._TRANS_FAILED.discard("Some english sentence title")
        provider_profiles._TRANS_WARNED.clear()
        try:
            err = io.StringIO()
            with mock.patch.object(provider_profiles.requests, "get",
                                   side_effect=ConnectionError("boom")):
                with contextlib.redirect_stderr(err):
                    out1 = provider_profiles.translate_to_zh(
                        "Some english sentence title")
                    out2 = provider_profiles.translate_to_zh(
                        "Another english sentence title")
            self.assertEqual(out1, "Some english sentence title")
            self.assertEqual(out2, "Another english sentence title")
            warned = err.getvalue()
            self.assertIn("warn", warned, "翻译系统性故障不得静默")
            self.assertEqual(warned.count("ConnectionError"), 1,
                             "同类异常每轮只报一次，批量翻译不得刷屏")
        finally:
            provider_profiles._TRANS_FAILED.clear()
            provider_profiles._TRANS_FAILED.update(saved_failed)
            provider_profiles._TRANS_WARNED.clear()
            provider_profiles._TRANS_WARNED.update(saved_warned)


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

        explicit_ids = set(re.findall(r'id=["\']([^"\']+)["\']', content))
        explicit_ids |= set(re.findall(r'name=["\']([^"\']+)["\']', content))

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
            # 存疑：不应作为可用免费额度来源（README 已如实标注）
            "ncompass", "mara",
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

    def test_cn_tool_vendors_bucket_as_domestic_in_guide(self):
        """Part 4 工具类的国内产品在攻略表格里必须进「国内：」行。

        Regression: 工具类不属于 domestic/international 任何 category，早期
        全部落到「海外：」，Trae 中国版 / 通义灵码 / 文心快码 被标成海外产品。
        现在看 GUIDE_META["region"]=="cn"。
        """
        meta = provider_profiles.GUIDE_META
        for vid in ("trae", "tongyi_lingma", "comate", "codebuddy_workbuddy"):
            self.assertEqual(meta[vid].get("region"), "cn",
                             f"{vid} 是国内工具，攻略归类需要 region=cn")
        for vid in ("cursor_ide", "kiro", "zed", "github_copilot", "qoder"):
            self.assertIsNone(meta[vid].get("region"),
                              f"{vid} 是海外产品，不应标 region")
        intel_list = [crawler_llm_intel.VendorIntel(
            vendor_id=v, brand=v, homepage="", products=[])
            for v in provider_profiles.PROVIDER_PROFILES]
        block = crawler_llm_intel.render_guide_block(
            crawler_llm_intel.order_vendor_records(intel_list))
        row_a = next(l for l in block.splitlines() if l.startswith("| **A."))
        dom, ovs = row_a.split("国内：")[1].split("<br>海外：")
        for name in ("Trae", "通义灵码", "文心快码", "CodeBuddy"):
            self.assertIn(name, dom)
            self.assertNotIn(name, ovs)
        for name in ("Cursor", "Kiro", "Zed", "Copilot"):
            self.assertIn(name, ovs)

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

    def test_display_names_are_reader_facing_not_platform_clutter(self):
        """厂商展示名用读者认识的模型/品牌名，不堆内部平台名（2026-10-05 定）。

        display_name 会进 README 章节标题与 quotas.json 名/锚点，是读者看到的名字。
        「百炼」只是阿里云平台旧名（真身是通义千问）；「开放平台 / 大模型平台 /
        人工智能平台 / MaaS / 大装置 / 长猫」这类是国内厂商的内部平台/服务名，
        读者搜不到、也不该在一览页替模型名当家。URL 里保留真实控制台地址不受此约束。
        （境外 Modal 的「Serverless AI 云平台」是给中文读者的解释性注解，非内部平台名，不在此列。）
        """
        banned = ("百炼", "开放平台", "大模型平台", "人工智能平台", "MaaS",
                  "大装置", "长猫开放平台")
        for vid, prof in provider_profiles.PROVIDER_PROFILES.items():
            dn = prof.get("display_name", "")
            hit = [b for b in banned if b in dn]
            self.assertFalse(hit, f"{vid} 的 display_name 含平台堆叠 {hit}: {dn}")
        # 正例锚定：改过的这几家现名必须落在模型/品牌名上
        for vid, want in (("aliyun_qwen", "通义"), ("baidu_qianfan", "文心"),
                          ("zhipu_glm", "智谱"), ("xiaomi_mimo", "MiMo")):
            self.assertIn(want, provider_profiles.PROVIDER_PROFILES[vid]["display_name"])

    def test_readme_buckets_sort_within_part_by_vendor_rank(self):
        """README 指南 / quotas.json 的每个 Part 桶内必须按 VENDOR_RANK（模型知名度）排。

        回归：`bucket_by_readme_order` 曾只按 category 分桶、桶内沿用 yaml 定义序，
        于是自研旗舰厂商小米 MiMo（VENDOR_RANK 第 15）在一览页掉到 Part 1 的第 22 位，
        与厂商胶囊 / 页脚 / vendors.json 的知名度排序打架——同一份情报在浏览页不同
        视图给出两种顺序。修法：桶内按 vendor_rank_index 排。
        """
        ids = list(provider_profiles.PROVIDER_PROFILES)
        intel_list = [crawler_llm_intel.VendorIntel(
            vendor_id=v, brand=v, homepage="", products=[]) for v in ids]
        ordered = [intel.vendor_id for _i, intel, _p
                   in crawler_llm_intel.order_vendor_records(intel_list)]
        # 每个 Part（category）内部，vendor_rank_index 必须单调不减
        by_cat = {}
        for vid in ordered:
            cat = crawler_llm_intel.get_provider_profile(vid, "", "").get("category", "domestic")
            by_cat.setdefault(cat, []).append(provider_profiles.vendor_rank_index(vid))
        for cat, ranks in by_cat.items():
            self.assertEqual(ranks, sorted(ranks),
                             f"Part[{cat}] 桶内没按 VENDOR_RANK 排：{ranks}")
        # 具体证人：小米（自研 MiMo，rank 靠前）必须排在国内的百度千帆之前
        self.assertLess(ordered.index("xiaomi_mimo"), ordered.index("baidu_qianfan"),
                        "小米 MiMo 应凭模型知名度排在百度千帆前，不该掉到 Part 1 末尾")

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


class TestCallLlmTextChannel(unittest.TestCase):
    """正文翻译的纯文本通路：与 call_llm 共用后端，但不套 JSON 模式、换 system、放宽 max_tokens。"""

    def _capture_post(self, text_out="正文译文"):
        """打桩 requests.post，记录请求体并返回带纯文本的 Gemini 响应。"""
        import json as _json
        captured = {}

        def fake_post(url, headers=None, json=None, timeout=None):
            captured["url"] = url
            captured["body"] = json
            payload = {"candidates": [{"content": {"parts": [{"text": text_out}]},
                                       "finishReason": "STOP"}]}
            return types.SimpleNamespace(status_code=200, text=_json.dumps(payload),
                                         json=lambda: payload, headers={})
        patcher = mock.patch.object(ai_review.requests, "post", fake_post)
        patcher.start()
        self.addCleanup(patcher.stop)
        return captured

    def test_text_mode_uses_plain_mime_custom_system_and_bigger_tokens(self):
        captured = self._capture_post()
        out = ai_review.call_llm_text("原文", system="你是译者", api_key="k",
                                      backend="gemini")
        self.assertEqual(out, "正文译文")
        gen = captured["body"]["generationConfig"]
        self.assertEqual(gen["responseMimeType"], "text/plain",
                         "正文要原样 markdown，不能被强制成 JSON")
        self.assertEqual(gen["maxOutputTokens"], ai_review.BODY_MAX_TOKENS)
        self.assertEqual(captured["body"]["systemInstruction"]["parts"][0]["text"],
                         "你是译者", "system 必须是调用方给的译者提示，而非情报核查员")

    def test_json_channel_still_forces_json_and_reviewer_system(self):
        """反向维持：call_llm（标题/档案）仍是 JSON + 核查 system，别被文本通路带偏。"""
        captured = self._capture_post(text_out='{"ok": true}')
        ai_review.call_llm("prompt", api_key="k", backend="gemini")
        gen = captured["body"]["generationConfig"]
        self.assertEqual(gen["responseMimeType"], "application/json")
        self.assertEqual(gen["maxOutputTokens"], ai_review.MAX_TOKENS)
        self.assertEqual(captured["body"]["systemInstruction"]["parts"][0]["text"],
                         ai_review.SYSTEM_PROMPT)


class TestAiBodiesCli(unittest.TestCase):
    """crawler main(["--ai-bodies"]) 维护子命令：LLM 通道接线、缺 key 不崩、译量有界。"""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self._orig_root = crawler_llm_intel._repo_root
        crawler_llm_intel._repo_root = lambda: self.root
        self._orig_key = os.environ.get("GEMINI_API_KEY")
        self.slug = "ab12cd34ef56"
        (self.root / "docs/feeds").mkdir(parents=True)
        (self.root / "docs/articles/openai").mkdir(parents=True)
        en_rel = f"docs/articles/openai/{self.slug}.en.md"
        ft.write_body_doc(self.root / en_rel,
                          {"status": "ok", "url": "https://a/p", "title": "Eng"},
                          "This is an English article body with enough words.")
        bodies = {f"openai\thttps://a/p": {"slug": self.slug, "en_path": en_rel,
                  "en_status": "ok", "zh_path": "", "zh_status": "", "translator": "",
                  "title": "中文标题", "date": "", "captured": ""}}
        ft.save_bodies(self.root / "docs/feeds/bodies.json", bodies)

    def tearDown(self):
        crawler_llm_intel._repo_root = self._orig_root
        if self._orig_key is None:
            os.environ.pop("GEMINI_API_KEY", None)
        else:
            os.environ["GEMINI_API_KEY"] = self._orig_key
        self.temp.cleanup()

    def _run(self):
        return crawler_llm_intel.main(["--ai-bodies"])

    def test_translates_pending_and_marks_llm(self):
        os.environ["GEMINI_API_KEY"] = "test-key"
        with mock.patch.object(ai_review, "call_llm_text",
                               return_value="这是一篇中文正文的完整翻译内容。"):
            rc = self._run()
        self.assertEqual(rc, 0)
        saved = ft.load_bodies(self.root / "docs/feeds/bodies.json")
        e = saved[f"openai\thttps://a/p"]
        self.assertEqual(e["zh_status"], "translated")
        self.assertEqual(e["translator"], "llm")
        self.assertTrue((self.root / e["zh_path"]).exists())

    def test_no_key_disables_without_crash(self):
        os.environ.pop("GEMINI_API_KEY", None)
        os.environ.pop("ANTHROPIC_API_KEY", None)
        rc = self._run()   # 缺 key：打印禁用、返回 0，不抛异常、不动 ledger
        self.assertEqual(rc, 0)
        saved = ft.load_bodies(self.root / "docs/feeds/bodies.json")
        self.assertEqual(saved[f"openai\thttps://a/p"]["zh_status"], "")

    def test_limit_bounds_translation(self):
        # 再塞 4 篇 pending，limit=1 只译一篇
        bodies = ft.load_bodies(self.root / "docs/feeds/bodies.json")
        for i in range(4):
            slug = f"l{i:011d}"
            rel = f"docs/articles/openai/{slug}.en.md"
            ft.write_body_doc(self.root / rel, {"status": "ok", "url": f"https://a/{i}"},
                              "English body words here plenty.")
            bodies[f"openai\thttps://a/{i}"] = {"slug": slug, "en_path": rel,
                "en_status": "ok", "zh_path": "", "zh_status": "", "translator": "",
                "title": "T", "date": "", "captured": ""}
        ft.save_bodies(self.root / "docs/feeds/bodies.json", bodies)
        os.environ["GEMINI_API_KEY"] = "test-key"
        with mock.patch.object(ai_review, "call_llm_text",
                               return_value="这是一段足够长的中文翻译正文内容。"):
            rc = crawler_llm_intel.main(["--ai-bodies", "--ai-bodies-limit", "1"])
        self.assertEqual(rc, 0)
        saved = ft.load_bodies(self.root / "docs/feeds/bodies.json")
        translated = [k for k, e in saved.items() if e["zh_status"] == "translated"]
        self.assertEqual(len(translated), 1, "--ai-bodies-limit 必须封顶单日译量")


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
        `TestCrawlerCleanup.test_repo_root_is_redirected_to_temp`。
        """
        self.assertNotIn("TestCrawlerCleanup", CI_EXCLUDED_CLASSES,
                         "该测试已改为在临时目录里跑，不该再被排除")
        ids = self._ids(ci_suite())
        self.assertTrue(any("TestCrawlerCleanup" in i for i in ids),
                        "TestCrawlerCleanup 必须真的在 CI 测试集里，否则这段清理逻辑零覆盖")


class TestSpaShellDetection(unittest.TestCase):
    """SPA 外壳判定不得误伤「挂载点里有服务端渲染内容」的页面。

    Regression: trae.cn 定价页是完整 SSR、中文密集（可见正文 ~1.5k 字），
    旧规则只要 HTML 里出现 id="root" 字样就判外壳 sparse，导致它进不了快照、
    本地 --no-browser 巡检报「内容过少」。
    """

    def test_nonempty_mount_is_not_shell(self):
        html = ('<html><body><div id="root"><!--$-->'
                '<div class="container">免费 Free ¥0 每月 500 积分</div>'
                '</body></html>')
        self.assertIsNone(crawler_llm_intel.SPA_EMPTY_MOUNT.search(html))
        self.assertIsNone(crawler_llm_intel.SPA_HTML_MOUNT.search(html))

    def test_empty_mount_with_noscript_is_shell(self):
        html = ('<html><body><div id="root">  <noscript>You need JS</noscript>'
                '<script src="/a.js"></script></div></body></html>')
        self.assertIsNotNone(crawler_llm_intel.SPA_EMPTY_MOUNT.search(html))

    def test_html_level_mount_id_is_shell(self):
        """build.nvidia.com 形态：挂载 id 直接挂在 <html> 上。"""
        html = '<html class="nv-dark" id="app" lang="en"><head></head></html>'
        self.assertIsNotNone(crawler_llm_intel.SPA_HTML_MOUNT.search(html))


class TestQuotasIndex(unittest.TestCase):
    """「免费额度与活动一览」的机读镜像 quotas.json。"""

    def _yaml_vendors(self):
        root = Path(__file__).resolve().parent
        vendors, _sources = crawler_llm_intel.parse_yaml(root / "llm-intel.yaml")
        return vendors

    def test_payload_fields_and_part_mapping(self):
        vendors = [{"id": "trae", "brand": "Trae", "homepage": "https://www.trae.cn/"}]
        payload = crawler_llm_intel.build_quotas_payload(vendors, {})
        row = payload["vendors"][0]
        self.assertEqual(payload["count"], 1)
        self.assertEqual(row["part"], 4, "tools 必须是 Part 4")
        self.assertEqual(row["anchor"], crawler_llm_intel.vendor_anchor(
            1, provider_profiles.get_provider_profile("trae")))
        self.assertEqual(row["homepage"], "https://www.trae.cn/")
        self.assertIn("promotions", row)
        self.assertIsNone(row["openai_compat"])

    def test_reviewed_date_carried(self):
        payload = crawler_llm_intel.build_quotas_payload(
            [{"id": "trae", "brand": "Trae", "homepage": "https://www.trae.cn/"}],
            {"trae": "2026-09-20"})
        self.assertEqual(payload["vendors"][0]["reviewed"], "2026-09-20")

    def test_every_vendor_part_matches_readme_ordering(self):
        """part 编号必须与 README 章节一致：桶序 domestic→international→cloud→tools。"""
        payload = crawler_llm_intel.build_quotas_payload(self._yaml_vendors(), {})
        parts = [r["part"] for r in payload["vendors"]]
        self.assertEqual(parts, sorted(parts),
                         "quotas.json 的 part 必须单调不减（README 章节同序）")
        self.assertEqual(max(parts), 4)

    def test_covers_every_yaml_vendor(self):
        """一览必须是全集：漏一家 = 页面上查无此厂商，且没有任何报错。

        2026-09 的回归：quotas.json 曾跟着 intel_list 出，而 intel_list 在
        --rebuild-only / 核查包快进下只含有博客归档的那部分厂商，线上一度少掉一半，
        国内平台若干家与整条 Part 4 工具线静默消失。
        """
        vendors = self._yaml_vendors()
        payload = crawler_llm_intel.build_quotas_payload(vendors, {})
        self.assertEqual(payload["count"], len(vendors))
        self.assertEqual({r["id"] for r in payload["vendors"]},
                         {v["id"] for v in vendors})
        self.assertEqual([r["rank"] for r in payload["vendors"]],
                         list(range(1, len(vendors) + 1)), "rank 必须连续，锚点才不串号")

    def test_anchors_match_readme_headings(self):
        """rank/anchor 要能真的跳到 README 里那一家的章节。"""
        root = Path(__file__).resolve().parent
        readme = (root / "README.md").read_text(encoding="utf-8")
        payload = crawler_llm_intel.build_quotas_payload(self._yaml_vendors(), {})
        headings = {crawler_llm_intel._gh_slug(m.group(0))
                    for m in re.finditer(r"^### \d+\. .+$", readme, re.M)}
        self.assertTrue(headings, "README 里没解析到厂商章节，先修测试本身")
        for row in payload["vendors"]:
            self.assertIn(row["anchor"], headings,
                          f"{row['id']} 的锚点 {row['anchor']} 在 README 里不存在")


class TestBrowsePageDesignContract(unittest.TestCase):
    """docs/index.html 的设计契约守卫；DESIGN.md 是同一份契约的文字版。

    2026-09-28 Design QA 查出的四类问题都会静默复发（页面没有构建、没有组件库，
    坏了不报错）：页签与面板的 ARIA 关联、字号标度、常驻 chrome、空结果文案。
    """

    @classmethod
    def setUpClass(cls):
        page = (Path(__file__).resolve().parent / "docs" / "index.html").read_text(
            encoding="utf-8")
        cls.page = page
        cls.style = re.search(r"<style>(.*?)</style>", page, re.S).group(1)

    def _rule(self, selector):
        m = re.search(r"\n\s*" + re.escape(selector) + r"[^{]*\{([^}]*)\}", self.style)
        self.assertIsNotNone(m, f"CSS 里找不到 {selector} 规则")
        return m.group(1)

    def test_free_models_string_does_not_break_search(self):
        """`free_models` 的上游（provider 档案 / overrides 手写）允许是字符串。

        字符串没有 `.join`，异常会打断整个 filter 回调 —— 表现是「一搜索整个
        一览变空」，且页面没有构建、坏了不报错。守卫：拼接前必须归一成数组。
        """
        self.assertIn("Array.isArray(fm)", self.page,
                      "free_models 拼接必须先归一成数组（手写档案可能是字符串）")

    def test_tab_panel_aria_wiring(self):
        """每个页签都要指向一个真实存在、且反向标注自己的 tabpanel。"""
        tabs = re.findall(r"<button[^>]*role=\"tab\"[^>]*>", self.page)
        self.assertEqual(len(tabs), 3, "页签数量变了？同步改这条守卫")
        for tag in tabs:
            tid = re.search(r'id="([^"]+)"', tag).group(1)
            ctl = re.search(r'aria-controls="([^"]+)"', tag)
            self.assertIsNotNone(ctl, f"{tid} 缺 aria-controls，读屏无法跳到面板")
            panel = re.search(r'<div class="pane" id="%s"[^>]*>' % ctl.group(1), self.page)
            self.assertIsNotNone(panel,
                                 f"{tid} 的 aria-controls 指向不存在的 {ctl.group(1)}")
            self.assertIn('role="tabpanel"', panel.group(0))
            self.assertIn('aria-labelledby="%s"' % tid, panel.group(0),
                          "面板要能报出自己属于哪个页签")

    def test_single_main_landmark_wrapping_the_panes(self):
        self.assertEqual(len(re.findall(r"<main\b", self.page)), 1,
                         "读屏的「跳到主内容」依赖唯一 main")
        body = self.page[self.page.index("<main"):self.page.index("</main>")]
        for pid in ("pane-news", "pane-changes", "pane-quotas"):
            self.assertIn('id="%s"' % pid, body, f"{pid} 落在了 main 之外")

    def test_font_sizes_stay_on_the_scale(self):
        """字号一律走 --fs-*；半像素值（11.5/12.5/13.5）已清过一轮，不许回来。"""
        off_scale = [ln.strip() for ln in self.style.splitlines()
                     if "font-size:" in ln and "var(--fs-" not in ln]
        self.assertEqual(off_scale, [], "这些字号没落在标度 token 上")
        self.assertFalse(re.search(r"font-size:\s*\d+\.\d+px", self.style),
                         "又引入半像素字号了")
        self.assertGreaterEqual(len(re.findall(r"--fs-\w+:", self.style)), 5,
                                "标度档位定义被删了？")

    def test_only_the_tab_bar_is_sticky(self):
        """筛选块（搜索 + 厂商胶囊 + 提示）一旦 sticky，手机上就没有正文可看了。

        实测：360x740 下它高 289px = 39% 视口，而页签栏反而滚走。
        """
        self.assertNotIn("sticky", self._rule(".controls"),
                         "筛选块不许常驻置顶")
        self.assertIn("position: sticky", self._rule(".tabs"),
                      "页签栏必须常驻，换视图不能靠滚回顶部")

    def test_focus_ring_follows_the_contract(self):
        """DESIGN.md 状态口径表：focus-visible = 2px --accent 外描边。

        曾经只有搜索框实现了这条，其余控件全用浏览器默认环——两套并存。
        钉形状不钉措辞：全局 :focus-visible 必须给 accent 描边，
        且不许出现把 outline 抹掉的声明。
        """
        self.assertRegex(self.style,
                         r":focus-visible\s*\{[^}]*outline:\s*2px solid var\(--accent\)")
        self.assertNotIn("outline: none", self.style)
        self.assertNotIn("outline:none", self.style)

    def test_every_css_var_is_defined(self):
        """引用一个不存在的 --token 不会报错，只会让那条声明静默失效。

        写这条的理由是现成的：间距收进 var(--sp-*) 时我引用了未定义的 --sp-1，
        margin-top 直接变成 0，页面看起来"正常"，只有对比像素才会发现。
        """
        defined = set(re.findall(r"(--[\w-]+)\s*:", self.style))
        used = set(re.findall(r"var\((--[\w-]+)\)", self.style))
        self.assertEqual(sorted(used - defined), [],
                         "这些 var() 引用没有对应的 token 定义")

    def test_spacing_and_radius_stay_on_tokens(self):
        """margin/padding/gap/圆角一律走 token；裸 px 只允许出现在 :root 定义里。

        逐条声明检查，不是逐行——一行里常混着 `border: 1px` 与 `letter-spacing`，
        那些本来就不属于间距标度。0 与 1px 放行：前者是清零，后者是发丝内边距。
        """
        body = re.sub(r":root\s*\{.*?\}", "", self.style, flags=re.S)
        offenders = []
        for decl in re.findall(r"([-a-z]+)\s*:\s*([^;{}]+)", body):
            prop, value = decl
            if not re.match(r"^(margin|padding|gap|row-gap|column-gap|border-radius)", prop):
                continue
            for num in re.findall(r"(\d+(?:\.\d+)?)px", value):
                if num not in ("0", "1"):
                    offenders.append("%s: %s" % (prop, value.strip()))
                    break
        self.assertEqual(offenders, [],
                         "又写回裸 px 了，新增间距请从 --sp-* / --rd-* 取")

    def test_capsule_base_is_not_reimplemented(self):
        """胶囊基元只允许 .pill 一处；新胶囊挂 .pill + 角色类，别再抄第五遍。

        去重前 .chip/.vendor/.kind/.qpart/.qp-tag 各写了一遍同一套
        display/圆角/描边/底色/文字色，共 38 条声明。
        """
        owners = []
        for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", self.style):
            if "var(--rd-pill)" in body:
                owners.append(sel.strip().splitlines()[-1].strip())
        self.assertEqual(owners, [".pill"],
                         f"圆角胶囊被重复定义了：{owners}")

    def test_text_is_never_dimmed_with_opacity(self):
        """opacity 压暗文字会在深色底上直接跌破对比度线（.chip .n 就是这么翻车的）。"""
        self.assertNotIn("opacity", self.style,
                         "层级请用 --muted / --chip-fg 表达，不要用透明度")

    def test_every_pane_has_its_own_empty_state_copy(self):
        """空结果不能沿用「加载中…」——读者只会以为页面卡住了。"""
        empties = re.findall(
            r"paintMsg\([^,]+,\s*rows\.length,\s*(?:[^']*?\?\s*)?'([^']+)'", self.page)
        self.assertEqual(len(empties), 3, "三个页签各需一句自己的空结果文案")
        loading = re.findall(r'data-loading="([^"]+)"', self.page)
        self.assertEqual(len(loading), 3, "每个提示行都要带 loading 文案")
        for text in empties:
            self.assertNotIn(text, loading)
            self.assertNotIn("加载", text, "空结果文案里不许出现「加载」字样")
        # 三个面板都要分「没搜到」与「还没到货」两态：用户没输过关键词时不许怪关键词
        noquery = re.findall(r"'(还没有[^']+)'", self.page)
        self.assertEqual(len(noquery), 3,
                         f"每个面板都要有自己的无查询空态文案，实得 {noquery}")

    def test_read_full_button_sits_in_the_meta_row_not_the_title(self):
        """「读全文」必须在 `.meta` 行里、且靠右对齐，不许塞回标题行。

        回归：它原先是 `.title` 里的 `display:inline-block`，跟在标题文字后面流动 ——
        按钮的横坐标随标题长度逐行漂移（实测头 20 行出现 14 个不同的 x），整列右缘参差，
        标题也被这个控件截短。挪到 meta 行 + `margin-left:auto` 后右缘才是一条齐的竖线。
        页面没有构建、坏了不报错，所以钉死它。
        """
        row = self.page[self.page.index("function rowNode"):]
        row = row[:row.index("function appendRows")]
        meta_at = row.index("meta.appendChild(rb)")
        self.assertIn("note.className = 'note orig'", row,
                      "新闻条目的原文标题要带 .orig（只有它可截断）")
        self.assertNotIn("t.appendChild(rb)", row,
                         "读全文按钮不许回到标题行里")
        self.assertLess(row.index("meta.className = 'meta'"), meta_at,
                        "按钮要挂在 meta 上")
        self.assertRegex(self._rule(".read-btn"), r"margin-left:\s*auto",
                         "读全文靠 meta 的 auto 外边距钉到行尾")
        # 「原文」截断只在 .orig 上：额度变化页的 .note 是「前值→后值」的实质内容。
        # 这里要精确取「选择器就是 .note」那条规则 —— _rule(".note") 会先撞上 .note.orig。
        bare = re.search(r"\n\s*\.note\s*\{([^}]*)\}", self.style)
        self.assertIsNotNone(bare, "CSS 里找不到 .note 基元规则")
        self.assertNotIn("text-overflow", bare.group(1),
                         "裸 .note 不得截断——额度变化页的正文靠它")

    def test_long_original_title_is_truncated_in_one_line(self):
        """长英文原文要能截成一行，否则一个长标题就把条目折成三四行、行高被拉散。

        关键是 `flex: 1 1 0`：可换行的 flex 容器在**收缩之前**就按假设尺寸决定换行，
        只写 min-width:0 的话长原文会被整体推到独立行、永远触发不了省略号。
        """
        rule = self._rule(".note.orig")
        self.assertRegex(rule, r"flex:\s*1 1 0")
        self.assertRegex(rule, r"min-width:\s*0")
        self.assertRegex(rule, r"text-overflow:\s*ellipsis")

    def test_footer_falls_back_when_index_missing(self):
        """vendors.json 404 时页脚不能是空块（回归：renderVendorFeeds 只在
        applyVendors 里调用，索引缺席走 else 分支就没人建列表）。"""
        body = re.search(r"function render\(\)\s*\{(.*?)\n  \}", self.page, re.S)
        self.assertTrue(body and "renderVendorFeeds" in body.group(1),
                        "render() 必须在 vendor 索引缺席时兜底调用 renderVendorFeeds")
        self.assertIn("state.vendorIndexApplied", self.page,
                      "需要一个索引到位标志来驱动页脚兜底")

    def test_news_search_is_debounced(self):
        """搜索全量过滤 3535 条 + 重建 200 行，宽查询单次 50ms（移动 4x 档 140ms），
        逐键渲染会卡。input 处理器要同步更新 state.q、把 renderItems 交给 setTimeout 防抖。"""
        handler = self.page[self.page.index("el.q.addEventListener"):]
        handler = handler[:handler.index("});") + 3]
        self.assertIn("state.q = el.q.value.trim();", handler,
                      "state.q 要同步更新，别的渲染路径才读得到最新查询")
        self.assertRegex(handler, r"setTimeout\([\s\S]*?renderItems\(\)",
                         "renderItems 要在 setTimeout 里防抖，不能每键同步跑")

    def test_copy_success_is_announced_to_screen_readers(self):
        """「已复制」只改按钮文案，读屏用户点完得不到任何反馈——必须有 live region。"""
        self.assertRegex(self.page,
                         r'id="copy-status"[^>]*role="status"[^>]*aria-live="polite"',
                         "复制确认要挂在一个 polite status 区上")
        handler = self.page[self.page.index("el.copy.addEventListener"):]
        self.assertIn("copy-status", handler, "复制处理器要写入 live region")
        self.assertRegex(handler, r"status\.textContent\s*=\s*''",
                         "回弹时要清空 status，否则连续两次复制不会重新播报")

    def test_tab_switch_resets_scroll_into_new_view(self):
        """深滚后切页签要把新视图滚回开头（回归：切换不动滚动位，
        从 3535 条的长列表切走会停在另一份列表的半路，只剩页脚/空白）。"""
        show = re.search(r"function showTab\([^)]*\)\s*\{(.*?)\n  \}", self.page, re.S)
        body = show.group(1) if show else ""
        # 「是否深滚」必须在隐藏旧 pane 之前判断（一隐藏长列表，scrollY 立刻被夹到新文档高度）
        self.assertIn("var wasDeep = window.scrollY > tabsDocTop()", body,
                      "showTab 要在切 pane 前捕获是否已深滚")
        self.assertLess(body.index("wasDeep ="), body.index("hidden ="),
                        "wasDeep 判断要早于 pane 的 hidden 赋值")
        self.assertRegex(body, r"if \(wasDeep\)[\s\S]*?scrollTo\(0, tabsDocTop\(\)\)",
                         "深滚时要在 rAF 里把页签栏滚回视口顶")
        # 阈值不能读 sticky 的 .tabs（滚过后 offsetTop/rect.top 都变成贴顶位置），
        # 必须从非 sticky 的 header 底边反推
        self.assertNotIn("offsetTop", self.page[self.page.index("function tabsDocTop"):self.page.index("function showTab")],
                         "tabsDocTop 不能走 offsetTop——sticky 元素滚过后它等于 scrollY")
        self.assertRegex(self.page,
                         r"function tabsDocTop\(\)\s*\{[\s\S]*?header[\s\S]*?getBoundingClientRect\(\)\.bottom \+ window\.scrollY",
                         "tabsDocTop 要用非 sticky 的 header 底边 + scrollY 反推页签栏文档流位置")


class TestBrowsePagePureLogic(unittest.TestCase):
    """浏览页纯逻辑（index.html 内联 <script id="fli-core"> 块）的行为测试经 node 跑。

    页面保持单文件（DESIGN.md 契约），纯逻辑内联、无 DOM 依赖；docs/app.test.mjs 从
    index.html 抽出该块 eval 后真调函数断言返回值，替掉「正则扫源码字符串形状」。
    node 缺失时 skip（本地与 ubuntu CI runner 都自带 node）。经 ci_suite() 的
    「全部−白名单」自动进 CI，无需改 workflow。
    """

    ROOT = Path(__file__).resolve().parent

    @unittest.skipUnless(shutil.which("node"), "需要 node 才能跑核心块行为测试")
    def test_browse_page_core_behavior_passes(self):
        proc = subprocess.run(
            ["node", "--test", "docs/app.test.mjs"],
            cwd=str(self.ROOT), capture_output=True, text=True, encoding="utf-8",
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        # 只看 returncode 会把「一条用例都没匹配到」当通过——必须确认真跑了足够用例。
        m = re.search(r"\bpass (\d+)", out)
        self.assertIsNotNone(m, "node --test 没输出 pass 计数（测试文件没被跑到？）")
        self.assertGreaterEqual(int(m.group(1)), 10,
                                f"核心块行为用例应至少 10 条，实得 {m.group(1)}")
        self.assertEqual(proc.returncode, 0, f"核心块行为测试未通过：\n{out}")


class TestIntelChangesFeed(unittest.TestCase):
    """额度/活动变化流：变更日志解析、只出额度事件、README 人工尾部保留。"""

    CHANGELOG = (
        "# 情报变更日志\n\n> 头\n\n"
        "## 2026-09-26\n\n"
        "### Groq Cloud（`groq`）\n"
        "- 摘要：免费层模型换代\n"
        "- `free_models`：A → B\n"
        "- `validity`：C → D\n\n"
        "## 2026-09-20\n\n"
        "### Cohere（`cohere`）\n"
        "- 摘要：试用限速调整\n"
        "- `free_quota`：E → F\n")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_parse_changelog_blocks(self):
        entries = crawler_llm_intel.parse_intel_changelog(self.CHANGELOG)
        self.assertEqual([e["date"] for e in entries], ["2026-09-26", "2026-09-20"])
        self.assertEqual(entries[0]["vendor_id"], "groq")
        self.assertEqual(entries[0]["summary"], "免费层模型换代")
        self.assertEqual(entries[0]["diffs"], [("free_models", "A → B"),
                                               ("validity", "C → D")])

    def test_feed_is_quota_only(self):
        n = crawler_llm_intel.write_intel_changes_feed(
            self.root, self.CHANGELOG, "https://x/feeds")
        self.assertEqual(n, 2, "变化流只收额度/活动变化，不再有模型发布")
        xml = (self.root / crawler_llm_intel.INTEL_CHANGES_FEED).read_text(encoding="utf-8")
        import xml.etree.ElementTree as ET
        items = ET.fromstring(xml).findall("./channel/item")
        # 日期倒序：09-26 Groq、09-20 Cohere，两条都是额度变化
        self.assertIn("额度变化 · Groq", items[0].findtext("title"))
        self.assertIn("额度变化 · Cohere", items[1].findtext("title"))
        self.assertNotIn("新模型", xml, "模型发布不再进变化流（已移到 model-releases.json）")
        self.assertIn("A → B", items[0].findtext("description"))
        guids = [it.findtext("guid") for it in items]
        self.assertEqual(len(set(guids)), 2, "guid 必须稳定且唯一")

    def test_quota_items_link_to_readme_anchor(self):
        n = crawler_llm_intel.write_intel_changes_feed(
            self.root, self.CHANGELOG, "",
            anchors={"groq": "38-groq-cloud-lpu", "cohere": "40-cohere"})
        self.assertEqual(n, 2)
        xml = (self.root / crawler_llm_intel.INTEL_CHANGES_FEED).read_text(encoding="utf-8")
        self.assertIn("#38-groq-cloud-lpu", xml, "额度变化条目应直达 README 厂商档案")
        js = json.loads((self.root / "intel-changes.json").read_text(encoding="utf-8"))
        self.assertEqual(js["items"][0][1], "quota", "伴生 JSON 供浏览页消费，kind 标记类别")

    def test_feed_without_changelog_produces_nothing(self):
        # 首次 AI 采纳前 changelog 不存在：变化流不产出（雷达已移到 model-releases.json）
        n = crawler_llm_intel.write_intel_changes_feed(self.root, "", "")
        self.assertEqual(n, 0)
        self.assertFalse((self.root / crawler_llm_intel.INTEL_CHANGES_FEED).exists(),
                         "无额度条目就不该写空的变化流文件（OPML 据此决定列不列它）")

    def test_opml_lists_changes_feed(self):
        out = self.root / "x.opml"
        crawler_llm_intel.write_opml(out, [], feeds_base="https://x/feeds")
        text = out.read_text(encoding="utf-8")
        self.assertIn("llm-intel-changes.xml", text,
                      "OPML 必须带上「情报变化」组，导入即订到额度变化流")
        # 本地（无 feeds_base）不列 Pages 绝对地址
        out2 = self.root / "y.opml"
        crawler_llm_intel.write_opml(out2, [], feeds_base="")
        self.assertNotIn("llm-intel-changes.xml", out2.read_text(encoding="utf-8"))

    def test_update_readme_preserves_manual_tail(self):
        """END 之后的人工尾部（开发者章节 + 365 页脚）必须在刷新时原样保留。

        旧行为是「END 之后全丢」——布局调整后总表不再是文末，丢尾部会把
        仓库结构 / 更新机制 / 页脚整段吃掉。
        """
        path = self.root / "README.md"
        tail = "\n\n## 仓库结构\n\n表\n\n## 关于 365 开源计划\n\n页脚文本\n"
        path.write_text(
            "头部\n\n" + crawler_llm_intel.README_BEGIN + "\n旧表\n"
            + crawler_llm_intel.README_END + tail, encoding="utf-8")
        wrote = crawler_llm_intel.update_readme(
            path, crawler_llm_intel.README_BEGIN + "\n新表\n"
            + crawler_llm_intel.README_END + "\n", guide_section="")
        self.assertTrue(wrote)
        new = path.read_text(encoding="utf-8")
        self.assertIn("新表", new)
        self.assertNotIn("旧表", new)
        self.assertTrue(new.endswith(tail.lstrip("\n")), "人工尾部必须原样保留")


class TestLocalReviewChannel(unittest.TestCase):
    """本地 AI 核查通道（--review-export / --review-apply）：与远端共用证据闸门。"""

    PAGE = "免费额度政策：注册即送 每月 100 万 tokens，长期有效，仅限非商用。"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        page = crawler_llm_intel.PageResult(
            url="https://p.example/pricing", stype="pricing", ok=True,
            final_url="https://p.example/pricing", text=self.PAGE,
            title="Pricing")
        self.intel = crawler_llm_intel.VendorIntel(
            vendor_id="demo_vid", brand="Demo", homepage="https://p.example",
            products=[], intel_pages=[page])
        self.intel_by_id = {"demo_vid": self.intel}
        self.snaps = crawler_llm_intel.SnapshotState(self.root)
        self.snaps.changed_pages = {"demo_vid": []}

    def tearDown(self):
        self.tmp.cleanup()

    def _packet_dir(self):
        d = self.root / crawler_llm_intel.REVIEW_PACKET_DIR / "packets"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def test_export_writes_prompt_packet(self):
        prompt = crawler_llm_intel.build_review_prompt(self.intel)
        self.assertIn("每月 100 万 tokens", prompt)
        n = crawler_llm_intel.export_review_packets(self.root, {"demo_vid": prompt})
        self.assertEqual(n, 1)
        self.assertTrue((self._packet_dir() / "demo_vid.prompt.md").exists())

    def test_apply_validates_good_and_fabricated(self):
        import json as _json
        d = self._packet_dir()
        # 缺补丁：继续排队（changed_pages 保留）
        snaps = crawler_llm_intel.SnapshotState(self.root)
        snaps.changed_pages = {"demo_vid": []}
        out = crawler_llm_intel.run_local_review(
            self.root, {"demo_vid": []}, self.intel_by_id, snaps)
        self.assertEqual(out, {})
        self.assertEqual(snaps.changed_pages, {},
                         "缺包：哈希不前进（排队靠下次重抓，本地不 commit 即保留旧哈希）")
        # 臆造证据：拒绝并保持排队
        (d / "demo_vid.json").write_text(_json.dumps({
            "changed": True, "summary": "s",
            "fields": {"free_quota": "每月 200 万 tokens"},
            "evidence": [{"url": "https://p.example/pricing",
                          "quote": "每月 200 万 tokens 永久免费"}],
            }, ensure_ascii=False), encoding="utf-8", newline="\n")
        snaps = crawler_llm_intel.SnapshotState(self.root)
        snaps.changed_pages = {"demo_vid": []}
        out = crawler_llm_intel.run_local_review(
            self.root, {"demo_vid": []}, self.intel_by_id, snaps)
        self.assertEqual(out, {}, "证据无法逐字命中必须被闸门拒绝")
        # 逐字真证据：通过并改名 .applied
        (d / "demo_vid.json").write_text(_json.dumps({
            "changed": True, "summary": "补充限速说明",
            "fields": {"free_quota": "每月 100 万 tokens，仅限非商用"},
            "evidence": [{"url": "https://p.example/pricing",
                          "quote": "长期有效，仅限非商用"}],
            }, ensure_ascii=False), encoding="utf-8", newline="\n")
        snaps = crawler_llm_intel.SnapshotState(self.root)
        snaps.changed_pages = {"demo_vid": []}
        out = crawler_llm_intel.run_local_review(
            self.root, {"demo_vid": []}, self.intel_by_id, snaps)
        self.assertIn("free_quota", out["demo_vid"]["fields"])
        self.assertTrue((d / "demo_vid.json.applied").exists(),
                        "已应用的补丁必须改名，防止重复入库")

    def test_adopt_writes_overlay_and_changelog(self):
        import ai_review
        (self.root / "profile_overrides.json").write_text("{}", encoding="utf-8")
        patch = ai_review.validate_patch(
            {"changed": True, "summary": "额度调整",
             "fields": {"free_quota": "每月 100 万 tokens"},
             "evidence": [{"url": "https://p.example/pricing",
                           "quote": "长期有效，仅限非商用"}]},
            self.PAGE)
        n = crawler_llm_intel.adopt_patches(
            self.root, {"demo_vid": patch}, self.intel_by_id)
        self.assertGreaterEqual(n, 1)
        overlay = json.loads((self.root / "profile_overrides.json")
                             .read_text(encoding="utf-8"))
        self.assertEqual(overlay["demo_vid"]["free_quota"], "每月 100 万 tokens")
        self.assertTrue((self.root / crawler_llm_intel.CHANGELOG_MD).exists())
        self.assertTrue((self.root / ".ai-changed").exists())


class TestPacketFastReplay(unittest.TestCase):
    """本地核查快进：指纹一致 → 免重抓复用包内语料；不一致 → 回退完整巡检。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "profile_overrides.json").write_text("{}", encoding="utf-8")
        page = crawler_llm_intel.PageResult(
            url="https://p.example/pricing", stype="pricing", ok=True,
            final_url="https://p.example/pricing",
            text=TestLocalReviewChannel.PAGE, title="Pricing",
            # 快照资格只认 requests 阶段的这两个字段：不填的话厂商压根没有
            # 快照条目，指纹退化成恒定的空摘要，「一致」证明不了任何事。
            snapshot_text=TestLocalReviewChannel.PAGE, snapshot_ok=True)
        self.snaps = crawler_llm_intel.SnapshotState(self.root)
        intel = crawler_llm_intel.VendorIntel(
            vendor_id="demo_vid", brand="Demo", homepage="https://p.example",
            products=[], intel_pages=[page])
        self.snaps.stage_vendor("demo_vid", intel)
        self.snaps.commit_vendor("demo_vid")
        self.digest = crawler_llm_intel.vendor_snapshot_digest(
            self.snaps.entries, "demo_vid")
        self.vendors = [{"id": "demo_vid", "name": "Demo",
                         "homepage": "https://p.example"}]
        self.grouped = {"demo_vid": [
            {"vendor": "demo_vid", "type": "pricing",
             "url": "https://p.example/pricing"}]}
        # 包与 manifest 一律由 export 产出 —— 页头必须由代码写。
        # 早先的 fixture 自己补了页头，把「真实包没有页头 → 快进永不生效」
        # 这个断裂盖掉了，测试全绿而通道在真实数据上 100% 被拒。
        d = self.root / crawler_llm_intel.REVIEW_PACKET_DIR / "packets"
        d.mkdir(parents=True)
        crawler_llm_intel.export_review_packets(
            self.root,
            {"demo_vid": "【当前生效档案】\n{}\n【官方页面原文】\n"
                         + TestLocalReviewChannel.PAGE}, self.snaps)
        (d / "demo_vid.json").write_text(json.dumps({
            "changed": True, "summary": "补充限速说明",
            "fields": {"free_quota": "每月 100 万 tokens，仅限非商用"},
            "evidence": [{"url": "https://p.example/pricing",
                          "quote": "长期有效，仅限非商用"}],
        }, ensure_ascii=False), encoding="utf-8", newline="\n")

    def tearDown(self):
        self.tmp.cleanup()

    def _replay(self, digest, exported=None):
        mpath = (self.root / crawler_llm_intel.REVIEW_PACKET_DIR
                 / crawler_llm_intel.REVIEW_MANIFEST)
        # 在 export 写出的真实 manifest 上改指纹/日期：保留 staged 等其余字段，
        # exported 默认昨天（固定日期会随时间推移撞上超龄回退，测试变定时炸弹）。
        manifest = json.loads(mpath.read_text(encoding="utf-8"))
        manifest["demo_vid"]["digest"] = digest
        manifest["demo_vid"]["exported"] = exported or (
            date.today() - timedelta(days=1)).isoformat()
        mpath.write_text(json.dumps(manifest), encoding="utf-8", newline="\n")
        return crawler_llm_intel.try_packet_fast_replay(
            self.root, self.snaps, self.vendors, self.grouped,
            self.root / "llm-news-feeds.md", self.root / "docs" / "feeds")

    def test_matching_digest_applies_without_crawl(self):
        self.assertNotEqual(
            self.digest, crawler_llm_intel.vendor_snapshot_digest({}, ""),
            "fixture 里厂商必须有真实情报页快照，否则指纹恒空、快进断言变成空转")
        intel_list, applied, vids = self._replay(self.digest)
        self.assertEqual(vids, {"demo_vid"})
        self.assertTrue(applied, "指纹一致必须走快进")
        self.assertTrue(intel_list, "快进要交回磁盘重建的 intel 供渲染")
        overlay = json.loads((self.root / "profile_overrides.json")
                             .read_text(encoding="utf-8"))
        self.assertIn("demo_vid", overlay, "补丁应过闸入库")
        d = self.root / crawler_llm_intel.REVIEW_PACKET_DIR / "packets"
        self.assertTrue((d / "demo_vid.json.applied").exists())
        self.assertFalse((d / "demo_vid.json").exists())
        self.assertEqual(
            crawler_llm_intel.read_packet_manifest(self.root), {},
            "已过闸的登记应注销，不留陈旧条目")

    def test_fast_replay_save_keeps_outside_vendors(self):
        # 快进只处理 in-scope 厂商：清单外厂商的哈希条目一条都不能掉
        other = crawler_llm_intel.SnapshotState(self.root)
        key = "other_vid|pricing|https://o.example/p"
        demo_key = "demo_vid|pricing|https://p.example/pricing"
        other.entries[key] = {"sha256": "x" * 64, "fact": ""}
        other.entries[demo_key] = {"sha256": "y" * 64, "fact": ""}
        other.save({"demo_vid"}, full_run=True, crawl_scope={"demo_vid"})
        data = json.loads(other.path.read_text(encoding="utf-8"))
        self.assertIn(key, data["sources"],
                      "限定范围落盘不得清理本轮没实抓的其余厂商")
        self.assertIn(demo_key, data["sources"])
        # 对照组：整跑语义（无范围）仍会清掉不在本轮清单里的条目
        other.save({"demo_vid"}, full_run=True)
        data3 = json.loads(other.path.read_text(encoding="utf-8"))
        self.assertNotIn(key, data3["sources"])

    def test_stale_digest_falls_back(self):
        intel_list, applied, vids = self._replay("0" * 64)
        self.assertEqual(vids, set())
        self.assertFalse(applied, "页面变了必须回退完整巡检重验")
        self.assertEqual(intel_list, [])
        self.assertEqual((self.root / "profile_overrides.json")
                         .read_text(encoding="utf-8"), "{}")
        d = self.root / crawler_llm_intel.REVIEW_PACKET_DIR / "packets"
        self.assertTrue((d / "demo_vid.json").exists(),
                        "回退路径不得消费补丁——留给完整巡检")

    def test_empty_snapshot_digest_falls_back(self):
        """厂商没有任何情报页快照时指纹恒定为空摘要：一致也证明不了页面没变。"""
        empty = crawler_llm_intel.SnapshotState(self.root)
        digest = crawler_llm_intel.vendor_snapshot_digest(empty.entries, "demo_vid")
        self.assertEqual(digest, crawler_llm_intel.vendor_snapshot_digest({}, ""))
        (self.root / crawler_llm_intel.REVIEW_PACKET_DIR
         / crawler_llm_intel.REVIEW_MANIFEST).write_text(
            json.dumps({"demo_vid": {"digest": digest,
                                     "exported": (date.today()
                                                  - timedelta(days=1)).isoformat()}}),
            encoding="utf-8", newline="\n")
        _il, applied, vids = crawler_llm_intel.try_packet_fast_replay(
            self.root, empty, self.vendors, self.grouped,
            self.root / "llm-news-feeds.md", self.root / "docs" / "feeds")
        self.assertFalse(applied, "空快照厂商必须回退实抓")
        self.assertEqual(vids, set())

    def test_export_registers_manifest(self):
        m = crawler_llm_intel.read_packet_manifest(self.root)
        self.assertEqual(m["demo_vid"]["digest"], self.digest,
                         "登记指纹必须与当前情报页快照一致（新闻页不进指纹）")

    def test_export_writes_packet_header(self):
        """页头由 export 写：真实包若缺页头，快进通道会 100% 拒收（曾踩过）。"""
        pkt = (self.root / crawler_llm_intel.REVIEW_PACKET_DIR / "packets"
               / "demo_vid.prompt.md").read_text(encoding="utf-8")
        self.assertTrue(pkt.startswith(crawler_llm_intel.PACKET_HEADER),
                        "导出的包必须以核查包页头开头")
        self.assertIn("【官方页面原文】", pkt)

    def test_headerless_packet_is_rejected(self):
        """手工/截断的无页头包不能当语料用，且必须回退而非原地空转。"""
        d = self.root / crawler_llm_intel.REVIEW_PACKET_DIR / "packets"
        (d / "demo_vid.prompt.md").write_text(
            "【官方页面原文】\n" + TestLocalReviewChannel.PAGE, encoding="utf-8")
        _il, applied, vids = self._replay(self.digest)
        self.assertFalse(applied, "有包没过闸就要回退完整巡检，否则下轮重演同一次拒绝")
        self.assertEqual(vids, set())
        self.assertTrue((d / "demo_vid.json").exists(),
                        "被拒的补丁必须原样留着，等完整巡检重验")
        self.assertEqual((self.root / "profile_overrides.json")
                         .read_text(encoding="utf-8"), "{}")


class TestReviewChannelHardening(unittest.TestCase):
    """本地核查通道加固的回归护栏：哈希前进 / 状态原子性与损坏处理 / 闸门语料 / 字段集对齐。"""

    OLD_TEXT = "免费额度政策：注册即送 每月 100 万 tokens，长期有效，仅限非商用。"
    NEW_TEXT = "免费额度政策：注册即送 每月 200 万 tokens，长期有效，仅限非商用。"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "profile_overrides.json").write_text("{}", encoding="utf-8")
        self.vendors = [{"id": "demo_vid", "brand": "Demo",
                         "homepage": "https://p.example"}]
        self.grouped = {"demo_vid": [
            {"vendor": "demo_vid", "type": "pricing",
             "url": "https://p.example/pricing"}]}

    def tearDown(self):
        self.tmp.cleanup()

    def _intel(self, text):
        page = crawler_llm_intel.PageResult(
            url="https://p.example/pricing", stype="pricing", ok=True,
            final_url="https://p.example/pricing", text=text, title="Pricing",
            snapshot_text=text, snapshot_ok=True)
        return crawler_llm_intel.VendorIntel(
            vendor_id="demo_vid", brand="Demo", homepage="https://p.example",
            products=[], intel_pages=[page])

    def test_fast_replay_advances_snapshot_hash(self):
        """完整本地周期：export→填包→apply 快进后哈希必须前进，不再每轮重复排队。"""
        vid = "demo_vid"
        # 第一轮：基线建档（旧页面）
        snaps = crawler_llm_intel.SnapshotState(self.root)
        snaps.stage_vendor(vid, self._intel(self.OLD_TEXT))
        snaps.save({vid}, full_run=True)
        # 第二轮：页面变化 → 导包 → rollback（与 main 的 export 分支一致）
        snaps = crawler_llm_intel.SnapshotState(self.root)
        changed = snaps.stage_vendor(vid, self._intel(self.NEW_TEXT))
        self.assertTrue(changed, "页面文本变化必须被检出")
        prompt = ("【当前生效档案】\n{}\n【官方页面原文】\n" + self.NEW_TEXT)
        crawler_llm_intel.export_review_packets(self.root, {vid: prompt}, snaps)
        snaps.rollback_vendor(vid)
        snaps.save({vid}, full_run=True)
        self.assertEqual(snaps.changed_pages, {}, "rollback 后变化队列应清空")
        # 填包：证据逐字出自新页面原文
        d = self.root / crawler_llm_intel.REVIEW_PACKET_DIR / "packets"
        (d / f"{vid}.json").write_text(json.dumps({
            "changed": True, "summary": "额度翻倍",
            "fields": {"free_quota": "每月 200 万 tokens"},
            "evidence": [{"url": "https://p.example/pricing",
                          "quote": "每月 200 万 tokens，长期有效"}],
        }, ensure_ascii=False), encoding="utf-8", newline="\n")
        # apply：快进过闸
        snaps = crawler_llm_intel.SnapshotState(self.root)
        _il, applied, vids = crawler_llm_intel.try_packet_fast_replay(
            self.root, snaps, self.vendors, self.grouped,
            self.root / "llm-news-feeds.md", self.root / "docs" / "feeds")
        self.assertTrue(applied)
        snaps.save(vids, full_run=False, crawl_scope=vids)
        # 关键断言：快照已前进到新页面哈希 —— 再抓同一页面不再报变化
        snaps = crawler_llm_intel.SnapshotState(self.root)
        self.assertEqual(snaps.stage_vendor(vid, self._intel(self.NEW_TEXT)), [],
                         "采纳后哈希不前进 → 同一变化每轮重新检出（死循环回归）")
        overlay = json.loads((self.root / "profile_overrides.json")
                             .read_text(encoding="utf-8"))
        self.assertEqual(overlay[vid]["free_quota"], "每月 200 万 tokens")

    def test_second_apply_over_existing_applied_file(self):
        """Windows 上 rename 撞已存在的 .applied 会崩；replace 必须静默覆盖。"""
        vid = "demo_vid"
        snaps = crawler_llm_intel.SnapshotState(self.root)
        snaps.stage_vendor(vid, self._intel(self.OLD_TEXT))
        snaps.save({vid}, full_run=True)
        snaps = crawler_llm_intel.SnapshotState(self.root)
        snaps.stage_vendor(vid, self._intel(self.NEW_TEXT))
        prompt = ("【当前生效档案】\n{}\n【官方页面原文】\n" + self.NEW_TEXT)
        crawler_llm_intel.export_review_packets(self.root, {vid: prompt}, snaps)
        d = self.root / crawler_llm_intel.REVIEW_PACKET_DIR / "packets"
        # 上一轮采纳的残留：第二次过闸时目标文件已存在
        (d / f"{vid}.json.applied").write_text('{"changed": false}',
                                               encoding="utf-8")
        (d / f"{vid}.json").write_text(json.dumps({
            "changed": True, "summary": "额度翻倍",
            "fields": {"free_quota": "每月 200 万 tokens"},
            "evidence": [{"url": "https://p.example/pricing",
                          "quote": "每月 200 万 tokens，长期有效"}],
        }, ensure_ascii=False), encoding="utf-8", newline="\n")
        intel_by_id = {vid: self._intel(self.NEW_TEXT)}
        out = crawler_llm_intel.run_local_review(
            self.root, {vid: []}, intel_by_id, snaps)
        self.assertIn(vid, out, "已有 .applied 残留时二次采纳必须成功")

    def test_corrupt_state_backs_up_and_rebaselines(self):
        """损坏的 state 不得静默清空成「全厂商变化」：备份 + 按基线重建。"""
        path = self.root / crawler_llm_intel.SNAPSHOT_STATE
        path.write_text('{"sources": {{{ 半截 JSON', encoding="utf-8")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            snaps = crawler_llm_intel.SnapshotState(self.root)
        self.assertTrue(snaps.baseline, "损坏后必须按基线建档，不报变化")
        self.assertEqual(snaps.entries, {})
        backups = list(self.root.glob("*.corrupt-*"))
        self.assertEqual(len(backups), 1, "损坏文件必须存档留证")
        self.assertIn("基线", err.getvalue())

    def test_digest_ignores_backoff_bookkeeping(self):
        """ai_attempts 等退避字段不进指纹：bump 一次不得被误判「页面又变」。"""
        snaps = crawler_llm_intel.SnapshotState(self.root)
        snaps.stage_vendor("demo_vid", self._intel(self.OLD_TEXT))
        snaps.commit_vendor("demo_vid")
        before = crawler_llm_intel.vendor_snapshot_digest(
            snaps.entries, "demo_vid")
        for entry in snaps.entries.values():
            entry["ai_attempts"] = 3
            entry["ai_retry_after"] = "2026-10-01"
            entry["ai_last_error"] = "quota"
        after = crawler_llm_intel.vendor_snapshot_digest(
            snaps.entries, "demo_vid")
        self.assertEqual(before, after)

    def test_aged_packet_falls_back_to_crawl(self):
        """导包超过 PACKET_MAX_AGE_DAYS：指纹一致也不再快进，回退实抓。"""
        vid = "demo_vid"
        snaps = crawler_llm_intel.SnapshotState(self.root)
        snaps.stage_vendor(vid, self._intel(self.OLD_TEXT))
        snaps.commit_vendor(vid)
        crawler_llm_intel.export_review_packets(
            self.root, {vid: "【官方页面原文】\n" + self.OLD_TEXT}, snaps)
        d = self.root / crawler_llm_intel.REVIEW_PACKET_DIR / "packets"
        (d / f"{vid}.json").write_text('{"changed": false}', encoding="utf-8")
        mpath = self.root / crawler_llm_intel.REVIEW_PACKET_DIR / "manifest.json"
        manifest = json.loads(mpath.read_text(encoding="utf-8"))
        manifest[vid]["exported"] = (
            date.today()
            - timedelta(days=crawler_llm_intel.PACKET_MAX_AGE_DAYS + 1)
        ).isoformat()
        mpath.write_text(json.dumps(manifest), encoding="utf-8", newline="\n")
        _il, applied, vids = crawler_llm_intel.try_packet_fast_replay(
            self.root, snaps, self.vendors, self.grouped,
            self.root / "llm-news-feeds.md", self.root / "docs" / "feeds")
        self.assertFalse(applied, "超龄包必须回退实抓重验")
        self.assertEqual(vids, set())

    def test_evidence_corpus_excludes_profile_and_removed_lines(self):
        """闸门语料 = 原文区 + 变化行新增侧：旧档案值与删除行不得给幻觉补丁放行。"""
        profile = {"free_quota": "旧额度 OLDQUOTA 每月 1 分"}
        pages = [{"url": "u", "stype": "pricing", "title": "t",
                  "text": "页面原文包含 全新事实 NEWFACT，足够长的正文内容。"}]
        focus = [{"url": "u", "stype": "pricing",
                  "removed": ["旧文本 OLDQUOTA 已删除"],
                  "added": ["全新事实 NEWFACT 已上线"]}]
        prompt = ai_review.build_user_prompt(
            "v", "B", profile, {}, pages, focus=focus)
        corpus = ai_review.evidence_corpus(prompt)
        self.assertIn("NEWFACT", corpus)
        self.assertNotIn("OLDQUOTA", corpus,
                         "旧档案值/删除行混进语料会放过引用旧值的幻觉补丁")
        base = {"changed": True, "summary": "s",
                "fields": {"free_quota": "每月 2 分"}}
        with self.assertRaises(ai_review.AiReviewError):
            ai_review.validate_patch(
                {**base, "evidence": [{"url": "u", "quote": "旧额度 OLDQUOTA"}]},
                ai_review.evidence_corpus(prompt))
        ok = ai_review.validate_patch(
            {**base, "evidence": [{"url": "u", "quote": "全新事实 NEWFACT 已上线"}]},
            ai_review.evidence_corpus(prompt))
        self.assertTrue(ok["changed"])
        # 无分区标记的语料原样返回（兼容直接构造 corpus 的调用方）
        self.assertEqual(ai_review.evidence_corpus("裸语料"), "裸语料")

    def test_field_types_align_with_overlay_fields(self):
        """FIELD_TYPES 与 _OVERLAY_FIELDS 必须同集：漂移会让合法补丁整个被拒。"""
        self.assertEqual(set(ai_review.FIELD_TYPES),
                         provider_profiles._OVERLAY_FIELDS)

    def test_openai_compat_dict_patch_validation(self):
        base = {"changed": True, "summary": "s",
                "evidence": [{"url": "u", "quote": "base_url 见页面原文"}]}
        ok = ai_review.validate_patch(
            {**base, "fields": {"openai_compat": {
                "base_url": "https://api.example/v1",
                "api_key_url": "https://example/key",
                "models": "m1"}}},
            "base_url 见页面原文")
        self.assertEqual(ok["fields"]["openai_compat"]["base_url"],
                         "https://api.example/v1")
        with self.assertRaises(ai_review.AiReviewError):
            ai_review.validate_patch(
                {**base, "fields": {"openai_compat": {"base_url": 42}}},
                "base_url 见页面原文")
        with self.assertRaises(ai_review.AiReviewError):
            ai_review.validate_patch(
                {**base, "fields": {"openai_compat": {}}},
                "base_url 见页面原文")

    def test_apply_patches_backs_up_corrupt_overlay(self):
        p = self.root / "profile_overrides.json"
        p.write_text("{ 损坏的 JSON", encoding="utf-8")
        patch = ai_review.validate_patch(
            {"changed": True, "summary": "s",
             "fields": {"free_quota": "每月 100 万 tokens"},
             "evidence": [{"url": "u", "quote": "长期有效，仅限非商用"}]},
            TestLocalReviewChannel.PAGE)
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            ai_review.apply_patches(p, {"demo_vid": patch})
        overlay = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(overlay["demo_vid"]["free_quota"], "每月 100 万 tokens")
        backups = [q for q in self.root.glob("profile_overrides.json.corrupt-*")]
        self.assertEqual(len(backups), 1, "损坏覆写必须存档留证，不得无痕覆盖")
        self.assertNotIn("损坏", p.read_text(encoding="utf-8"))

    def test_load_overrides_corrupt_keeps_file_and_warns(self):
        p = self.root / "profile_overrides.json"
        p.write_text("{ 损坏的 JSON", encoding="utf-8")
        err = io.StringIO()
        with mock.patch.object(provider_profiles, "_OVERLAY_PATH", p), \
                contextlib.redirect_stderr(err):
            out = provider_profiles._load_overrides()
        self.assertEqual(out, {})
        self.assertIn("解析失败", err.getvalue())
        self.assertEqual(p.read_text(encoding="utf-8"), "{ 损坏的 JSON",
                         "加载器不得改动原文件（备份是副本）")
        self.assertTrue(list(self.root.glob("profile_overrides.json.corrupt-*")))

    def test_state_save_is_atomic_no_tmp_leftover(self):
        snaps = crawler_llm_intel.SnapshotState(self.root)
        snaps.stage_vendor("demo_vid", self._intel(self.OLD_TEXT))
        snaps.save({"demo_vid"}, full_run=True)
        self.assertEqual(list(self.root.glob("*.tmp")), [],
                         "原子写不得残留 .tmp 半成品")
        data = json.loads((self.root / crawler_llm_intel.SNAPSHOT_STATE)
                          .read_text(encoding="utf-8"))
        self.assertIn("sources", data)


class TestArchiveDedup(unittest.TestCase):
    """归档合并折叠「同一篇文章的两个入口」，但真同名文章必须保住。"""

    A = crawler_llm_intel.Article
    ANCHOR = "https://blog.example/post-x"
    DIRECT = "https://blog.example/posts/grok-4-7"

    def test_anchor_card_collapses_into_direct_link(self):
        anchor = self.A(title="Introducing Grok 4.7", zh_title="介绍 Grok 4.7",
                        url=self.ANCHOR + "#d-2026-09-21-0", date="2026-09-21")
        direct = self.A(title="Introducing Grok 4.7",
                        url=self.DIRECT, date="2026-09-21")
        out = crawler_llm_intel._dedup_same_title([anchor, direct])
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].url, self.DIRECT, "保留的必须是详情页直链")

    def test_rss_english_and_archive_chinese_group_together(self):
        """一条带 zh_title（title 英文）、一条只有中文标题：按显示标题归组。"""
        rss = self.A(title="Claude in Chrome is generally available",
                     zh_title="Claude in Chrome 正式全面可用",
                     url="https://blog.example#d-1", date="2026-09-15")
        arch = self.A(title="Claude in Chrome 正式全面可用",
                      url="https://blog.example/chrome-ga", date="2026-08-26")
        out = crawler_llm_intel._dedup_same_title([rss, arch])
        self.assertEqual(len(out), 1, "锚点卡与直链是同一篇的两个入口")

    def test_same_title_same_date_duplicates_collapse(self):
        a = self.A(title="版本更新", url="https://docs.example/changelog#v1", date="2026-09-25")
        b = self.A(title="版本更新", url="https://docs.example/changelog#v1-1", date="2026-09-25")
        self.assertEqual(len(crawler_llm_intel._dedup_same_title([a, b])), 1)

    def test_distinct_same_title_articles_are_kept(self):
        """openai 实测：2016/2017 三篇都叫「团队近况」，都是直链不同日期 → 全保。"""
        arts = [self.A(title="Team update", url=f"https://openai.example/index/u{i}",
                       date=f"201{i}-0{4-i}-10") for i in (7, 6, 5)]
        self.assertEqual(len(crawler_llm_intel._dedup_same_title(arts)), 3)

    def test_order_after_dedup_follows_input(self):
        arts = [self.A(title="B", url="https://x/b", date="2026-09-02"),
                self.A(title="A", url="https://x/a#card", date="2026-09-01"),
                self.A(title="A", url="https://x/a/page", date="2026-08-01")]
        out = crawler_llm_intel._dedup_same_title(arts)
        self.assertEqual([a.url for a in out], ["https://x/b", "https://x/a/page"],
                         "折叠不能打乱日期倒序")


class TestJsonApiNewsSource(unittest.TestCase):
    """数据接口型动态源：页面纯前端渲染、官方又没有 RSS 时的唯一通路。

    实例是千问 qwen.ai/research（2026-09-30 换源，替代阿里云百炼「新发布模型」变更日志）。
    为什么只能走接口——CSR 页面渲染后整页 0 个 `<a>`、详情正链 path 是 `/blog` 会被
    `_SECTION_ROOT` 判成栏目根、全站无 RSS——见 llm-intel.yaml 的 research 源注释。
    """

    API = "https://qwen.ai/api/v2/article/retrieval?type=qwen_ai&language=zh-CN"
    HUMAN = "https://qwen.ai/research"

    # ---- 夹具 ----

    @staticmethod
    def _articles_payload():
        return [
            # content 是站点返回的 HTML 富文本 —— 里面的日期与 <h3> 正是 HTML 提取器
            # 会误当成「变更日志条目」的东西（见 test_html_fallback_skips_api_body）
            {"title": "Qwen3-Max 正式发布", "path": "qwen3-max",
             "extra": {"date": "2026-09-20", "tags": ["release"]},
             "content": "<h3>Qwen3-Max 的核心能力</h3><p>2026-09-20 上线，支持 256K 上下文，"
                        "覆盖文本、图像与代码三类任务的统一推理。</p>"},
            # 日期带时间与时区后缀：只取前 10 位
            {"title": "Qwen-Image 编辑能力升级", "path": "qwen-image-edit",
             "extra": {"date": "2026-09-10T08:00:00.000Z"},
             "content": "<h3>局部重绘的使用方式</h3><p>2026-09-10 起支持蒙版重绘，"
                        "并保留原图的构图与光照。</p>"},
            {"title": "Qwen3-Coder 上下文扩容", "path": "qwen3-coder",
             "extra": {"date": "2026-08-28"},
             "content": "<h3>仓库级理解能力的改动</h3><p>2026-08-28 起上下文窗口扩到 1M，"
                        "并调整了工具调用的返回结构。</p>"},
            {"title": "太短", "path": "x"},              # 丢：标题 < 4 字符
            {"title": "缺少 slug 的条目", "path": ""},     # 丢：拼不出正链
            {"title": "没有日期的条目", "path": "no-date", "extra": {}},
            {"title": "日期在未来的条目", "path": "future",
             "extra": {"date": "2099-01-01"}},           # 保条目、丢日期
            "不是字典的条目",
        ]

    def _body(self, articles=None):
        return json.dumps(
            {"code": 200, "data": {"articles": articles if articles is not None
                                   else self._articles_payload()}},
            ensure_ascii=False)

    def _page(self, *, raw=None, text="", stype="research", ok=True, url=API,
              display_url=HUMAN):
        return crawler_llm_intel.PageResult(
            url=url, stype=stype, ok=ok, final_url=url, raw=raw if raw is not None
            else self._body(), text=text, display_url=display_url)

    def _intel(self, pages):
        intel = crawler_llm_intel.VendorIntel(
            vendor_id="aliyun_qwen", brand="通义千问 Qwen", homepage="", products=[])
        intel.news_pages = pages
        return intel

    # ---- 1) 适配器解析 ----

    def test_adapter_parses_official_shape(self):
        arts = crawler_llm_intel.extract_articles_from_json(self._page())
        by_url = {a.url: a for a in arts}
        self.assertIn("https://qwen.ai/blog?id=qwen3-max", by_url,
                      "正链必须是站点自己的规范地址 <origin>/blog?id=<slug>")
        a = by_url["https://qwen.ai/blog?id=qwen3-max"]
        self.assertEqual(a.title, "Qwen3-Max 正式发布")
        self.assertEqual(a.date, "2026-09-20")
        self.assertEqual(a.source, "官方 JSON 接口")
        self.assertEqual(a.stype, "research")
        # extra.date 带时间/时区后缀时只取日期部分
        self.assertEqual(by_url["https://qwen.ai/blog?id=qwen-image-edit"].date,
                         "2026-09-10")

    def test_adapter_drops_junk_and_future_dates_but_keeps_entries(self):
        arts = crawler_llm_intel.extract_articles_from_json(self._page())
        slugs = [u.split("id=")[-1] for u in (a.url for a in arts)]
        self.assertNotIn("x", slugs, "标题 < 4 字符的不是文章")
        self.assertNotIn("", slugs, "没有 slug 拼不出正链")
        by_slug = dict(zip(slugs, arts))
        self.assertEqual(by_slug["no-date"].date, "", "没有日期只是排到末尾，条目要留")
        self.assertEqual(by_slug["future"].date, "",
                         "远未来日期必须在入口丢掉：归档只增不减，错日期会永久留存")
        self.assertNotIn("不是字典的条目", [a.title for a in arts])

    def test_adapter_respects_max_items(self):
        many = [{"title": f"第 {i} 篇发布说明", "path": f"p{i}",
                 "extra": {"date": "2026-09-01"}} for i in range(300)]
        arts = crawler_llm_intel.extract_articles_from_json(
            self._page(raw=self._body(many)), max_items=5)
        self.assertEqual(len(arts), 5, "接口一次可能给几百条，必须有上限")

    def test_adapter_returns_empty_for_unusable_bodies(self):
        cases = {
            "HTML 页": "<html><body>前端渲染的空壳</body></html>",
            "坏 JSON": '{"data": {"articles": [',
            "缺 articles": '{"data": {"total": 40}}',
            "articles 不是列表": '{"data": {"articles": {"a": 1}}}',
            "空正文": "",
        }
        for label, body in cases.items():
            self.assertEqual(
                crawler_llm_intel.extract_articles_from_json(self._page(raw=body)),
                [], label)

    def test_adapter_origin_comes_from_url_not_hardcoded(self):
        page = self._page(url="https://mirror.example/api/list", raw=self._body())
        arts = crawler_llm_intel.extract_articles_from_json(page)
        self.assertTrue(all(a.url.startswith("https://mirror.example/blog?id=")
                            for a in arts), "域名要从接口 URL 推，不能写死")

    # ---- 2) 截断守卫：接口响应体是兆级 ----

    def test_json_body_prefers_raw_over_truncated_text(self):
        """`text` 在非 HTML 分支被截到 20000 字符，日期全在 extra 里 → 只能读 `raw`。

        Regression: 只改 yaml 换源、不动抓取层时，实测 4.9MB 响应截断后前 20000 字符里
        `"date"` 出现 **0** 次，整源 0 条目，而产物上看不出任何异常。
        """
        padded = self._body([
            {"title": "开头的一篇", "path": "first", "content": "填充正文" * 8000},
            {"title": "Qwen3-Max 正式发布", "path": "qwen3-max",
             "extra": {"date": "2026-09-20"}},
        ])
        truncated = padded[:20000]
        self.assertNotIn('"date"', truncated, "夹具前提：截断后确实拿不到日期")
        page = self._page(raw=padded, text=truncated)
        arts = {a.url: a for a in crawler_llm_intel.extract_articles_from_json(page)}
        self.assertIn("https://qwen.ai/blog?id=qwen3-max", arts,
                      "必须从 raw 拿到完整响应体：截断后连条目本身都不在里面")
        self.assertEqual(arts["https://qwen.ai/blog?id=qwen3-max"].date, "2026-09-20")
        self.assertTrue(crawler_llm_intel.json_api_body(page))

    def test_json_api_body_detection(self):
        self.assertEqual(crawler_llm_intel.json_api_body(
            self._page(raw="<html></html>")), "", "HTML 页不是数据接口")
        for body in ('{"a": 1}', '[{"a": 1}]', '  {"a": 1}'):
            self.assertEqual(crawler_llm_intel.json_api_body(self._page(raw=body)),
                             body.lstrip())
        # 只有 text 时也要认得出来（--rebuild-only 之外的兜底路径）
        self.assertTrue(crawler_llm_intel.json_api_body(
            self._page(raw="", text='{"a": 1}')))

    def test_fetch_keeps_full_body_for_news_types(self):
        """抓取层：非 HTML 响应体对动态类源必须留全文（`text` 的 20000 字符上限不够）。

        Regression: 只改 yaml 换源、不动抓取层时，千问接口实测响应 4.9MB，
        前 20000 字符里 `"date"` 出现 **0** 次，配好源跑下来是 0 条目。
        """
        body = self._body([
            {"title": "开头的一篇", "path": "first",
             "content": "填充正文" * 8000},          # 把日期挤到 20000 字符之后
            {"title": "后面的一篇", "path": "second",
             "extra": {"date": "2026-09-20"}},
        ])
        self.assertGreater(len(body), 20000, "夹具前提：响应体要超过旧的截断上限")
        resp = mock.Mock(status_code=200, url=self.API, text=body,
                         headers={"Content-Type": "application/json"},
                         encoding="utf-8")
        session = mock.Mock()
        session.get.return_value = resp
        page = crawler_llm_intel._fetch_with_requests(
            session, self.API, "research", (1.0, 2.0), retries=0)
        self.assertTrue(page.ok)
        self.assertNotIn('"date"', page.text[:20000])
        urls = [a.url for a in crawler_llm_intel.extract_articles_from_json(page)]
        self.assertIn("https://qwen.ai/blog?id=second", urls,
                      "全文留在 raw 里才提得出 20000 字符之后的条目")

    def test_fetch_still_truncates_non_news_body(self):
        """对照组：情报页（非 NEWS_TYPES）仍按 20000 字符截断，不把兆级正文常驻内存。"""
        body = '{"quota": "' + "x" * 60000 + '"}'
        resp = mock.Mock(status_code=200, url="https://q.example/api/quota",
                         text=body, headers={"Content-Type": "application/json"},
                         encoding="utf-8")
        session = mock.Mock()
        session.get.return_value = resp
        page = crawler_llm_intel._fetch_with_requests(
            session, "https://q.example/api/quota", "free_quota", (1.0, 2.0),
            retries=0)
        self.assertEqual(len(page.text), 20000)
        self.assertEqual(page.raw, "", "情报页不需要全文")

    # ---- 3) collect_news_articles 的步骤编排 ----

    def test_html_fallback_skips_api_body(self):
        """步骤 3 不得把接口响应体喂给 HTML 提取器。

        Regression: 实测千问接口经 `extract_changelog_sections` 凭空造出 **53** 条，
        URL 全是「接口地址 + 合成 `#d-<日期>-<n>` 锚点」（点进去是 4.9MB 的 JSON），
        标题里还混着文章正文的小标题。
        """
        page = self._page()
        junk = crawler_llm_intel.extract_articles_from_page(page, max_items=100)
        self.assertTrue(any("#d-" in a.url or a.url == self.API for a in junk),
                        "夹具前提：HTML 提取器对这个响应体确实会产出伪条目")

        intel = self._intel([page])
        with mock.patch.object(crawler_llm_intel, "extract_articles_from_page",
                              wraps=crawler_llm_intel.extract_articles_from_page) as spy:
            crawler_llm_intel.collect_news_articles(intel, session=None)
        spy.assert_not_called()
        urls = [a.url for a in intel.all_news_articles]
        self.assertTrue(urls, "接口条目本身要进归档")
        self.assertTrue(all(u.startswith("https://qwen.ai/blog?id=") for u in urls),
                        f"不得出现伪锚点条目：{urls}")

    def test_api_step_runs_after_html_fallback(self):
        """接口条目若先进 `articles`，步骤 3 的 `if not articles` 会把同厂商的 HTML
        动态页永久挡掉 —— 而归档只增不减，这种「静默停更」在产物上完全看不出来。"""
        html_page = crawler_llm_intel.PageResult(
            url="https://qwen.ai/updates", stype="updates", ok=True,
            final_url="https://qwen.ai/updates", text="y" * 300)
        html_art = crawler_llm_intel.Article(
            title="来自 HTML 动态页的条目", url="https://qwen.ai/updates/one",
            date="2026-09-18")
        intel = self._intel([self._page(), html_page])
        with mock.patch.object(crawler_llm_intel, "extract_articles_from_page",
                              return_value=[html_art]):
            crawler_llm_intel.collect_news_articles(intel, session=None)
        urls = [a.url for a in intel.all_news_articles]
        self.assertIn("https://qwen.ai/updates/one", urls, "HTML 动态页不得被接口条目挡掉")
        self.assertIn("https://qwen.ai/blog?id=qwen3-max", urls)

    def test_failed_api_page_yields_nothing(self):
        """抓取失败的接口页不得产出条目 —— 响应体可能仍在（503 也常带 JSON 错误体）。"""
        page = self._page(ok=False)
        self.assertTrue(crawler_llm_intel.json_api_body(page),
                        "夹具前提：失败页仍带着可解析的响应体")
        intel = self._intel([page])
        crawler_llm_intel.collect_news_articles(intel, session=None)
        self.assertEqual(intel.all_news_articles, [])

    # ---- 4) 产物渲染：印给人看的地址 ----

    def test_feeds_md_prints_human_url_and_api_hint(self):
        intel = self._intel([self._page()])
        intel.news_articles = intel.all_news_articles = [
            crawler_llm_intel.Article(title="Qwen3-Max 正式发布",
                                      url="https://qwen.ai/blog?id=qwen3-max",
                                      date="2026-09-20")]
        md = crawler_llm_intel.render_news_section([intel], "https://x.example/feeds")
        self.assertIn(f"- 页面：[研究页]({self.HUMAN})", md)
        self.assertNotIn("article/retrieval", md,
                         "订阅入口不得印接口长串（读者点进去是 4.9MB 的 JSON）")
        self.assertIn("🔌 官方未提供 RSS/Atom 订阅源，条目取自官方数据接口", md)
        self.assertNotIn("未发现 RSS/Atom 链接", md,
                         "接口源本来就没有 HTML 页面可发现，这句是错话")

    def test_feeds_md_api_hint_survives_rebuild(self):
        """重建出的页没有响应体，`json_api_body` 判不出来 —— 靠 display_url 兜住。

        否则同一份产物在实抓与 --rebuild-only 之间来回翻这一行。
        """
        page = crawler_llm_intel.PageResult(
            url=self.API, stype="research", ok=True, final_url=self.API,
            display_url=self.HUMAN)
        intel = self._intel([page])
        intel.news_articles = intel.all_news_articles = [
            crawler_llm_intel.Article(title="Qwen3-Max 正式发布",
                                      url="https://qwen.ai/blog?id=qwen3-max",
                                      date="2026-09-20")]
        md = crawler_llm_intel.render_news_section([intel], "https://x.example/feeds")
        self.assertIn("🔌 官方未提供 RSS/Atom", md)
        self.assertNotIn("未发现 RSS/Atom 链接", md)

    def test_archive_subscription_entry_prints_human_url(self):
        intel = self._intel([self._page()])
        intel.news_articles = intel.all_news_articles = [
            crawler_llm_intel.Article(title="Qwen3-Max 正式发布",
                                      url="https://qwen.ai/blog?id=qwen3-max",
                                      date="2026-09-20")]
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            with mock.patch.object(crawler_llm_intel, "translate_to_zh", lambda t: t):
                crawler_llm_intel.write_news_archives(out, [intel], clean_removed=False)
            text = (out / "aliyun_qwen.md").read_text(encoding="utf-8")
        self.assertIn(f"- 页面：[研究页]({self.HUMAN})", text)
        self.assertNotIn("article/retrieval", text)

    # ---- 5) --rebuild-only 的状态回填 ----

    YAML = f"""
vendors:
  - id: aliyun_qwen
    brand: 通义千问 Qwen
    homepage: https://qwen.ai
    products: []
sources:
  - vendor_id: aliyun_qwen
    type: research
    url: "{API}"
    page: {HUMAN}
"""

    def test_rebuild_restores_display_url_and_page_state(self):
        """产物里印的是 display_url，状态也只能按它找回来。

        Regression: 只按 yaml `url` 匹配时状态匹配不上，「上一轮接口抓取失败」的 ❌
        标记被丢掉，重建出来的产物于是宣称这个源是健康的。
        """
        news_md = (
            "# 动态总览\n\n"
            "### 通义千问 Qwen (aliyun_qwen)\n"
            f"- 页面：[研究页]({self.HUMAN})\n"
            "  - ❌ 抓取失败：HTTP 503（可直接访问页面查看）\n"
        )
        states = crawler_llm_intel._parse_news_md_page_states(news_md)
        self.assertFalse(states["aliyun_qwen"][0]["ok"], "夹具前提：❌ 行要被解析出来")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "llm-news").mkdir()
            (root / "intel.yaml").write_text(self.YAML, encoding="utf-8")
            vendors, sources = crawler_llm_intel.parse_yaml(root / "intel.yaml")
            grouped = crawler_llm_intel.group_sources_by_vendor(sources)
            intel_list = crawler_llm_intel.rebuild_intel_from_disk(
                vendors, grouped, states, root / "llm-news")
        self.assertEqual(len(intel_list), 1)
        page = intel_list[0].news_pages[0]
        self.assertEqual(page.display_url, self.HUMAN)
        self.assertEqual(page.url, self.API)
        self.assertFalse(page.ok, "接口抓取失败的 ❌ 标记不得在重建中丢失")
        self.assertEqual(page.stype, "research")

    def test_yaml_declares_page_for_api_source(self):
        """yaml 侧的契约：接口源必须带 `page`，否则产物会把接口长串印给读者。"""
        root = Path(__file__).resolve().parent
        _vendors, sources = crawler_llm_intel.parse_yaml(root / "llm-intel.yaml")
        api_sources = [s for s in sources
                       if any(k in (s.get("url") or "") for k in ("/api/", "wp-json"))
                       and (s.get("type") or "") in crawler_llm_intel.NEWS_TYPES]
        self.assertEqual(len(api_sources), 2,
                         "夹具前提：目前应有千问接口与 AI21 wp-json 两个动态接口源")
        for s in api_sources:
            self.assertTrue(s.get("page"), f"数据接口源缺 page：{s}")
            self.assertNotIn("/api/", s["page"], "page 必须是给人看的地址")
            self.assertNotIn("wp-json", s["page"])


class TestWordpressNewsSource(unittest.TestCase):
    """WordPress `wp-json` 作为动态源（AI21）—— 第二个 JSON 消费者，形状完全不同。

    换源动因是实测出来的缺陷：AI21 归档 13 条**全是** `blog/#d-<日期>-<n>` 合成锚点，
    一条都打不开（与 deepseek / x.ai / claude 那个缺陷同源，见
    NEWS_CANONICAL_ONLY_VENDORS）。站上没有 RSS：/feed、/blog/feed、/rss.xml 实测全部
    落到首页 HTML 或 404，只有 wp-json 给规范直链与精确发布时间。
    """

    ENDPOINT = ("https://www.ai21.com/wp-json/wp/v2/posts?per_page=100"
                "&orderby=date&order=desc&_fields=date,link,title")
    HUMAN = "https://www.ai21.com/blog"

    @staticmethod
    def _day(offset_days: int) -> str:
        """相对抓取日的日期，测试不随时间腐烂。"""
        return (date.today() - timedelta(days=offset_days)).isoformat()

    def _body(self, items=None):
        return json.dumps(items if items is not None else [
            # title 是 `{"rendered": ...}` 且带 HTML 实体，link 带尾斜杠
            {"date": f"{self._day(10)}T14:25:38",
             "link": "https://www.ai21.com/blog/you-need-a-verifier/",
             "title": {"rendered": "You don&#8217;t need a frontier model. "
                                   "You need a verifier."}},
            {"date": f"{self._day(400)}T09:00:00",
             "link": "https://www.ai21.com/blog/older-post/",
             "title": {"rendered": "Better and cheaper together"}},
            {"date": f"{self._day(900)}T09:00:00",          # 超出两年窗口
             "link": "https://www.ai21.com/blog/ancient-post/",
             "title": {"rendered": "2023 年的旧帖不该灌进浏览页"}},
            {"date": "", "link": "https://www.ai21.com/blog/no-date/",
             "title": {"rendered": "没有日期的条目照收，只是排到最后"}},
            {"date": (date.today() + timedelta(days=30)).isoformat() + "T00:00:00",
             "link": "https://www.ai21.com/blog/from-the-future/",
             "title": {"rendered": "日期写在未来的条目"}},
            {"date": self._day(20), "link": "",             # 丢：没有 link 打不开
             "title": {"rendered": "缺 link 的条目"}},
            {"date": self._day(20), "link": "https://www.ai21.com/blog/x/",
             "title": {"rendered": "太短"}},                # 丢：标题 < 4 字符
            "不是字典的一行",
        ], ensure_ascii=False)

    def _page(self, body=None, stype="blog"):
        return crawler_llm_intel.PageResult(
            url=self.ENDPOINT, stype=stype, ok=True, final_url=self.ENDPOINT,
            raw=body if body is not None else self._body(), display_url=self.HUMAN)

    def _intel(self, pages, vendor_id="ai21_labs", brand="AI21 Labs"):
        intel = crawler_llm_intel.VendorIntel(
            vendor_id=vendor_id, brand=brand, homepage="", products=[])
        intel.news_pages = pages
        return intel

    # ---- 解析 ----

    def test_wordpress_adapter_decodes_title_and_trims_date(self):
        arts = {a.url: a for a in crawler_llm_intel.extract_articles_from_wordpress(
            self._page())}
        url = "https://www.ai21.com/blog/you-need-a-verifier/"
        self.assertIn(url, arts, "link 就是站方给的规范地址，原样保留")
        self.assertEqual(arts[url].title,
                         "You don\u2019t need a frontier model. You need a verifier.",
                         "`&#8217;` 这类实体要解码，否则进归档就是 `&#8217;` 字面量")
        self.assertEqual(arts[url].date, self._day(10), "date 带时间后缀，只取前 10 位")
        self.assertEqual(arts[url].source, "官方内容接口")
        self.assertEqual(arts[url].stype, "blog")

    def test_wordpress_window_drops_aged_posts(self):
        urls = {a.url for a in crawler_llm_intel.extract_articles_from_wordpress(
            self._page())}
        self.assertIn("https://www.ai21.com/blog/older-post/", urls, "窗口内的要留")
        self.assertNotIn("https://www.ai21.com/blog/ancient-post/", urls,
                         "超过两年的旧帖不收：浏览页不是历史存档")

    def test_wordpress_window_is_rolling_not_fixed(self):
        """窗口按「抓取日减天数」算，不是写死日期 —— 写死会随时间越放越宽。"""
        items = [{"date": f"{self._day(cut)}T00:00:00",
                  "link": f"https://www.ai21.com/blog/p{cut}/",
                  "title": {"rendered": f"第 {cut} 天前的一篇帖子"}}
                 for cut in (729, 731)]
        urls = {a.url.rsplit("/p", 1)[-1].strip("/") for a in
                crawler_llm_intel.extract_articles_from_wordpress(self._page(self._body(items)))}
        self.assertEqual(urls, {"729"}, "窗口边界外一天的必须被挡掉")
        # 同一个夹具把窗口放宽就都在 —— 证明挡住它的是窗口，不是别的判据
        wide = crawler_llm_intel.extract_articles_from_wordpress(
            self._page(self._body(items)), window_days=5 * 365)
        self.assertEqual(len(wide), 2)

    def test_wordpress_window_rolls_with_the_clock(self):
        """把抓取日推到三年后，同一批帖子的去留必须跟着变。

        写死一个 cutoff 基准日（哪怕算法同样是「减 730 天」）在这里就会露馅：
        老帖会被永久放行，窗口随着时间越放越宽。
        """
        future = datetime(2029, 1, 1)
        ref = (future - timedelta(days=crawler_llm_intel.JSON_NEWS_WINDOW_DAYS)).date()
        items = [{"date": f"{(ref + timedelta(days=1)).isoformat()}T00:00:00",
                  "link": "https://www.ai21.com/blog/inside/",
                  "title": {"rendered": "窗口内的一条帖子"}},
                 {"date": f"{(ref - timedelta(days=1)).isoformat()}T00:00:00",
                  "link": "https://www.ai21.com/blog/outside/",
                  "title": {"rendered": "窗口外的一条帖子"}}]
        clock = mock.Mock()
        clock.now.return_value = future
        page = self._page(self._body(items))
        with mock.patch.object(crawler_llm_intel, "datetime", clock):
            urls = {a.url.rsplit("/", 2)[-2] for a in
                    crawler_llm_intel.extract_articles_from_wordpress(page)}
        self.assertEqual(urls, {"inside"},
                         "以 2029-01-01 为抓取日时，边界应按 window 天数整体前移")

    def test_wordpress_keeps_undated_and_defuses_future_dates(self):
        arts = {a.url: a for a in crawler_llm_intel.extract_articles_from_wordpress(
            self._page())}
        self.assertIn("https://www.ai21.com/blog/no-date/", arts,
                      "没有日期只是排到末尾，条目本身不该消失")
        future = arts.get("https://www.ai21.com/blog/from-the-future/")
        self.assertIsNotNone(future)
        self.assertEqual(future.date, "", "远未来日期要在入口丢掉（归档只增不减）")

    def test_wordpress_drops_unusable_rows(self):
        urls = [a.url for a in crawler_llm_intel.extract_articles_from_wordpress(
            self._page())]
        self.assertNotIn("", urls, "没有 link 的条目打不开")
        self.assertNotIn("https://www.ai21.com/blog/x/", urls, "标题过短不是文章")
        self.assertNotIn("不是字典的一行", urls)

    def test_wordpress_respects_max_items(self):
        items = [{"date": self._day(1), "link": f"https://www.ai21.com/blog/p{i}/",
                  "title": {"rendered": f"第 {i} 篇帖子"}} for i in range(300)]
        arts = crawler_llm_intel.extract_articles_from_wordpress(
            self._page(self._body(items)), max_items=5)
        self.assertEqual(len(arts), 5)

    def test_shapes_do_not_cross(self):
        """两种接口形状互不认领：认错了会把 0 条当成「源停更」。"""
        wp_page = self._page()
        qwen_shape = json.dumps({"data": {"articles": [
            {"title": "Qwen3-Max 正式发布", "path": "qwen3-max",
             "extra": {"date": self._day(5)}}]}}, ensure_ascii=False)
        self.assertEqual(crawler_llm_intel.extract_articles_from_json(wp_page), [],
                         "千问适配器不该认 WP 的裸数组")
        self.assertEqual(
            crawler_llm_intel.extract_articles_from_wordpress(
                crawler_llm_intel.PageResult(url="https://qwen.ai/api/x", stype="research",
                                             ok=True, raw=qwen_shape)),
            [], "WP 适配器不该认千问的 data.articles")

    # ---- 步骤 3.5 分派 ----

    def test_collect_news_dispatches_to_wordpress_adapter(self):
        intel = self._intel([self._page()])
        with mock.patch.object(crawler_llm_intel, "extract_articles_from_page",
                              wraps=crawler_llm_intel.extract_articles_from_page) as spy:
            crawler_llm_intel.collect_news_articles(intel, session=None)
        spy.assert_not_called()
        urls = [a.url for a in intel.all_news_articles]
        self.assertTrue(urls and all("#d-" not in u for u in urls),
                        f"接口源不得产出合成锚点：{urls}")
        self.assertIn("https://www.ai21.com/blog/you-need-a-verifier/", urls)

    def test_feeds_md_hint_does_not_claim_client_rendering(self):
        """两家的接口源共用一行提示，措辞只能陈述共同事实。

        AI21 是 WordPress **服务端**渲染，弃用 HTML 是因为列表页只给合成锚点且官方
        没留 RSS；提示里写「页面为前端渲染」对它就是一句假话（千问那句才是）。
        """
        intel = self._intel([self._page()])
        intel.news_articles = intel.all_news_articles = []
        md = crawler_llm_intel.render_news_section([intel], "https://x.example/feeds")
        self.assertIn("🔌 官方未提供 RSS/Atom 订阅源，条目取自官方数据接口", md)
        self.assertNotIn("前端渲染", md)
        self.assertNotIn("wp-json", md, "订阅入口印 yaml `page` 的人类地址，不印接口长串")

    # ---- 老锚点收口（换源的直接动因） ----

    def _anchored_intel(self):
        intel = self._intel([self._page()])
        intel.all_news_articles = [
            crawler_llm_intel.Article(title="合成锚点老条目",
                                      url="https://www.ai21.com/blog/#d-2026-08-19-0",
                                      date="2026-08-19"),
            crawler_llm_intel.Article(title="有直链的新条目",
                                      url="https://www.ai21.com/blog/new-post",
                                      date="2026-09-20"),
        ]
        intel.news_articles = intel.all_news_articles
        return intel

    def test_ai21_is_canonical_only_so_anchors_stop_shipping(self):
        self.assertIn("ai21_labs", crawler_llm_intel.NEWS_CANONICAL_ONLY_VENDORS,
                      "换源前那批 blog/#d-… 锚点全是死链，产出层必须挡掉")
        urls = [a.url for a in crawler_llm_intel._rss_articles(
            self._anchored_intel(), date.today().isoformat())]
        self.assertEqual(urls, ["https://www.ai21.com/blog/new-post"],
                         "只留规范直链；归档 .md 仍全量留档")

    def test_anchor_filter_does_not_spill_to_other_vendors(self):
        """对照组：没进白名单的厂商，锚点就是它的条目身份，不能跟着挡。"""
        intel = self._anchored_intel()
        intel.vendor_id = "minimax"
        urls = [a.url for a in crawler_llm_intel._rss_articles(
            intel, date.today().isoformat())]
        self.assertIn("https://www.ai21.com/blog/#d-2026-08-19-0", urls,
                      "白名单外的厂商维持原状")

    # ---- yaml 契约 ----

    def test_yaml_ai21_source_shape(self):
        root = Path(__file__).resolve().parent
        _vendors, sources = crawler_llm_intel.parse_yaml(root / "llm-intel.yaml")
        src = next(s for s in sources if s.get("vendor_id") == "ai21_labs"
                   and "wp-json" in (s.get("url") or ""))
        self.assertEqual(src.get("page"), "https://www.ai21.com/blog")
        self.assertEqual(src.get("type"), "blog")
        # 窗口必须在爬虫侧，URL 里不许出现固定日期
        self.assertNotIn("after=", src["url"],
                         "写死 after= 日期会随时间越放越宽，等于没有窗口")
        self.assertIn("_fields=", src["url"], "不裁字段会把整篇正文拉回来")
        listing = [s for s in sources if (s.get("url") or "") == "https://www.ai21.com/blog"]
        self.assertEqual(listing, [], "列表页源已换掉")


class TestBackfillOriginalEncoding(unittest.TestCase):
    """`--backfill-orig` 的字符编码：乱码绝不能被当成「英文原文」写进归档。

    实测事故（2026-09-30）：DeepSeek 文章页发 `Content-Type: text/html` 不带 charset，
    requests 按 RFC 回落 ISO-8859-1，UTF-8 中文标题被解成
    `DeepSeek-V4-Pro æ\xad£å¼\x8fç\x99\x88...` 这类拉丁扩展乱码；它既含真拉丁（模型名）
    又不含 CJK，于是过了 resolve_article_original 的判据，26 条乱码进了归档注释。
    """

    # 事故里的真实乱码原文（UTF-8 字节被按 latin-1 解出来的形态）
    MOJI = "DeepSeek-V4-Pro æ\xad£å¼\x8fç\x99\x88ä¸\x8açº¿ | DeepSeek"

    def _html(self, title: str) -> str:
        return f"<html><head><title>{title}</title></head><body>正文</body></html>"

    def test_mojibake_title_is_rejected(self):
        self.assertEqual(
            crawler_llm_intel.resolve_article_original(
                self._html(self.MOJI), "https://api.deepseek.com/news/"),
            "", "乱码不是英文原文：写进归档就是永久污染，产出层 original_title 会跟着坏")

    def test_chinese_native_page_is_rejected(self):
        self.assertEqual(
            crawler_llm_intel.resolve_article_original(
                self._html("DeepSeek-V4-Pro 正式版上线 | DeepSeek"),
                "https://api.deepseek.com/news/"),
            "", "中文原生页本就没有英文原文")

    def test_english_title_still_recovers(self):
        """守卫不能误伤正常回填（那才是这条命令的用途）。"""
        self.assertEqual(
            crawler_llm_intel.resolve_article_original(
                self._html("Introducing Grok 4.7 - xAI"), "https://x.ai/news/grok-4-7"),
            "Introducing Grok 4.7")

    def test_accented_legitimate_title_survives(self):
        """真带重音的英文标题（人名、西语品牌）不能被当成乱码打掉。"""
        self.assertEqual(
            crawler_llm_intel.resolve_article_original(
                self._html("Tino Cuéllar joins as Chief Global Affairs Officer | Anthropic"),
                "https://www.anthropic.com/news/tino-cuellar"),
            "Tino Cuéllar joins as Chief Global Affairs Officer")

    def test_response_text_applies_charset_fallback(self):
        """根因修复：无 charset 的响应要按 apparent_encoding 重解。

        抓取主路径 `_fetch_with_requests` 一直有这个兜底，独立入口（回填）以前没有。
        """
        raw = self._html("DeepSeek-V4-Pro 正式版上线 | DeepSeek").encode("utf-8")

        class Resp:
            encoding = "ISO-8859-1"      # requests 对无 charset 的默认回落
            apparent_encoding = "utf-8"

            @property
            def text(self):
                return raw.decode(self.encoding or "latin-1")

        resp = Resp()
        out = crawler_llm_intel.response_text(resp)
        self.assertEqual(resp.encoding, "utf-8")
        self.assertIn("正式版上线", out, "兜底后应拿到正常中文，而不是拉丁扩展乱码")
        self.assertNotIn("æ", out)


class TestFulltextUrlIdentity(unittest.TestCase):
    """全文语料层：URL 规范化 + 稳定 slug（`fulltext` 模块）。"""

    def test_normalize_strips_fragment_and_tracking_lowercases_host(self):
        self.assertEqual(
            ft.normalize_url("https://OpenAI.com/Blog/Post/?utm_source=x&ref=1#sec"),
            "https://openai.com/Blog/Post?ref=1",
        )

    def test_normalize_removes_trailing_slash_but_keeps_root(self):
        self.assertEqual(ft.normalize_url("https://a.com/x/"), "https://a.com/x")
        self.assertEqual(ft.normalize_url("https://a.com/"), "https://a.com/")
        self.assertEqual(ft.normalize_url("https://a.com"), "https://a.com/")

    def test_path_locale_stripped_only_on_the_whitelisted_host(self):
        """openai 的中文新闻页混着两种链接写法，同一篇文章必须只有一个身份。

        白名单之外不许剥：deepseek 的 `/zh-cn/updates/` 就是它中文版页面本身，
        剥掉会跟不存在的英文版撞成一个身份，也把源声明的语言骗成英文。
        """
        self.assertEqual(ft.normalize_url("https://openai.com/zh-Hans-CN/index/gpt-6/"),
                         "https://openai.com/index/gpt-6")
        self.assertEqual(ft.normalize_url("https://openai.com/index/gpt-6/"),
                         "https://openai.com/index/gpt-6")
        self.assertEqual(ft.url_hash("https://openai.com/zh-Hans-CN/index/gpt-6"),
                         ft.url_hash("https://openai.com/index/gpt-6"),
                         "两种写法必须归一到同一个语料文件名")
        self.assertEqual(ft.normalize_url("https://openai.com/zh-Hans-CN/news/"),
                         "https://openai.com/news",
                         "源自身的 locale 段也剥（canonical 与列表页同一身份）")
        kept = ft.normalize_url("https://api-docs.deepseek.com/zh-cn/updates/")
        self.assertEqual(kept, "https://api-docs.deepseek.com/zh-cn/updates")
        self.assertEqual(ft.normalize_url("https://mimo.mi.com/docs/zh-CN/updates/model"),
                         "https://mimo.mi.com/docs/zh-CN/updates/model")

    def test_url_hash_deterministic_and_fragment_sensitive(self):
        """slug 必须**认** fragment —— 这条口径 2026-10-08 从「忽略」翻了过来。

        单页变更日志的每条条目都是「同页不同 #锚点」（MiniMax 发布说明、Kimi 发布记录、
        poolside / inference.net 的博客卡片）。fragment 不参与身份时，N 条条目会塌成
        一个 slug、共用一份「整页」正文：实测 MiniMax 35 条条目只有 2 个正文文件，
        21 条挤在同一个文件里，点开任一条看到的都是整页目录。
        """
        h = ft.url_hash("https://a.com/post")
        self.assertEqual(h, ft.url_hash("https://a.com/post"), "无 fragment 必须稳定")
        self.assertEqual(len(h), 12)
        self.assertTrue(all(c in "0123456789abcdef" for c in h))
        # 同一个页面的不同锚点 = 不同条目 = 不同 slug
        self.assertNotEqual(ft.url_hash("https://a.com/post#one"),
                            ft.url_hash("https://a.com/post#two"))
        self.assertNotEqual(h, ft.url_hash("https://a.com/post#frag"))
        # 跟踪参数照旧不参与身份
        self.assertEqual(ft.url_hash("https://a.com/post?utm_source=n"),
                         ft.url_hash("https://a.com/post"))

    def test_bodies_key_uses_normalized_url(self):
        """ledger 键同样认 fragment，且仍剥跟踪参数。

        fragment 不进键时，同页第二条锚点条目会被判成「已有正文」直接跳过，
        正文也就永远只有整页那一份。
        """
        self.assertEqual(
            ft.bodies_key("openai", "https://a.com/p?utm_source=n"),
            ft.bodies_key("openai", "https://a.com/p"))
        self.assertEqual(ft.bodies_key("openai", "https://a.com/p"),
                         "openai\thttps://a.com/p")
        self.assertNotEqual(ft.bodies_key("openai", "https://a.com/p#x"),
                            ft.bodies_key("openai", "https://a.com/p#y"))
        # fragment 大小写不敏感（避免 #Sec 与 #sec 各算一条）
        self.assertEqual(ft.bodies_key("openai", "https://a.com/p#Sec"),
                         ft.bodies_key("openai", "https://a.com/p#sec"))

    def test_anchor_fragment_is_decoded(self):
        self.assertEqual(ft.anchor_fragment(
            "https://a.com/p#2026-%E5%B9%B4-7-%E6%9C%88"), "2026-年-7-月")
        self.assertEqual(ft.anchor_fragment("https://a.com/p"), "")


class TestAnchorSectionSlicing(unittest.TestCase):
    """单页变更日志的正文切片（`fulltext._slice_anchor_section`）。

    回归：MiniMax 发布说明是一个页面装 21 条条目，抓回来的正文永远是整页，
    21 条条目共用一份 3461 字符的整页正文 —— 点「MiniMax M3」看到的是从 H3 到
    01-系列的全表。切片后每条只拿到自己那节。
    """

    PAGE = (
        "## [\u21a9](https://x.cn/docs#2026-\u5e74-7-\u6708-31-\u65e5)2026 \u5e74 7 \u6708 31 \u65e5\n"
        "\n"
        "## MiniMax H3\n"
        "\n"
        "\u65b0\u4e00\u4ee3\u5f00\u653e\u901a\u7528\u591a\u6a21\u6001\u89c6\u9891\u6a21\u578b\uff0c\u9762\u5411\u6587\u672c\u3002\n"
        "\n"
        "## [\u21a9](https://x.cn/docs#2026-\u5e74-7-\u6708-16-\u65e5)2026 \u5e74 7 \u6708 16 \u65e5\n"
        "\n"
        "## Music-3.0\n"
        "\n"
        "\u5c1a\u672a\u63a8\u51fa\uff0c\u4ec5\u4fdd\u7559\u7a0b\u5e8f\u516c\u544a\u3002\n"
    )

    def test_slices_only_the_anchored_entry(self):
        sec = ft._slice_anchor_section(self.PAGE, "2026-年7-月16-日")
        self.assertIn("Music-3.0", sec)
        self.assertIn("尚未推出", sec)
        self.assertNotIn("MiniMax H3", sec,
                         "切片不得带上相邻条目的内容")
        self.assertNotIn("新一代开放通用多模态", sec)

    def test_keeps_the_entries_own_title_heading(self):
        """条目标题（`## MiniMax H3`）与日期标题**同级**，按同级切会把正文整段丢掉。"""
        sec = ft._slice_anchor_section(self.PAGE, "2026-年7-月31-日")
        self.assertIn("MiniMax H3", sec)
        self.assertIn("新一代开放通用多模态", sec)
        self.assertNotIn("Music-3.0", sec)

    def test_slug_style_fragment_matches_page_anchor_style(self):
        """URL 里的锚点与标题回链是两种写法，必须归一后仍能匹配上。

        真实 URL 是 `#2026-年7-月31-日`，页面回链是 `#2026-年7-31-日`；
        原样比对匹配不上就会静默退回整页 —— 也就是「切片看着没生效」。
        """
        sec = ft._slice_anchor_section(self.PAGE, "2026-年7-月31-日")
        self.assertIn("MiniMax H3", sec)
        self.assertLess(len(sec), len(self.PAGE))

    def test_unknown_anchor_returns_whole_page_never_empty(self):
        """宁可给整页也不给空 —— 空正文会被 detect_index_page 判掉，正文直接留空。"""
        out = ft._slice_anchor_section(self.PAGE, "2099-年1-月1-日")
        self.assertTrue(out.strip())
        self.assertGreaterEqual(len(out), len(self.PAGE) - 2)

    def test_no_fragment_is_a_no_op(self):
        self.assertEqual(ft._slice_anchor_section(self.PAGE, ""), self.PAGE)

    #: groq changelog 形状：条目标题自带指向本页锚点的链接，正文里有粗体小标题与 bullet。
    GROQ = (
        "### Added[MCP Connectors (Beta)](#mcp-connectors-beta)\n"
        "\n"
        "MCP Connectors give you Gmail, Calendar and Drive without custom servers.\n"
        "\n"
        "**Key Changes:**\n"
        "\n"
        "* Gmail reads your inbox\n"
        "* Drive returns files\n"
        "\n"
        "Key changes shipped this week\n"
        "\n"
        "**Docs:** more here\n"
        "\n"
        "### Changed[Python SDK v0.30.0](#python-sdk-v0300)\n"
        "\n"
        "The Python SDK has been updated to v0.30.0, adding these models:\n"
        "\n"
        "* DeepSeek V4 supports tool calling\n"
        "* Qwen3.6 supports vision inputs\n"
        "\n"
        "---\n"
        "\n"
        "Jul 15, 2025\n"
        "\n"
        "### Added[Third Entry](#third-entry)\n"
        "\n"
        "Third entry body.\n"
    )

    def test_heading_with_inline_anchor_link_slices_exact(self):
        """行内 `](#锚点)` 精确命中 —— 英文 slug 过日期键会退化成纯数字，必须走这一档。

        回归：判据只留「数字+汉字」时，`mcp-connectors-beta` 的键是空串，切片静默
        退回整页（实测 7 条 groq 条目共用 42208 字符的整页目录）。
        """
        sec = ft._slice_anchor_section(self.GROQ, "mcp-connectors-beta")
        self.assertIn("without custom servers", sec)
        self.assertIn("Gmail reads your inbox", sec)
        # 「紧跟的行是粗体标签（`**Docs:**`）而不是真 bullet」不能把这里判成下一条起点
        self.assertIn("more here", sec)
        self.assertNotIn("Python SDK", sec)

    def test_body_sentence_is_not_an_entry_start(self):
        """正文首句不得被当成下一条的开头 —— 否则切片在第一句处就收口。

        这一条专门给「句末标点」守卫当证人：这里的正文以 `:` 收尾、后面**就是真
        bullet**，「bullet 要带空格」那条拦不住它。回归实测：少了标点守卫时
        `Python SDK v0.30.0` 那条只剩 95 字符的标题行，正文整段被切丢。
        """
        sec = ft._slice_anchor_section(self.GROQ, "python-sdk-v0300")
        self.assertIn("DeepSeek V4 supports tool calling", sec)
        self.assertIn("adding these models", sec)
        self.assertNotIn("MCP Connectors give you", sec)

    def test_next_entry_date_label_is_not_left_in_tail(self):
        """切片尾部不许挂着**下一条**的日期标签 —— groq 页用 `---` + 日期分隔条目。

        回归：不剥收尾时实测 13 条 groq 切片末尾带着 `---` 和下一条的 `Oct 29, 2025`，
        读者会误认这条就是那个日期。
        """
        sec = ft._slice_anchor_section(self.GROQ, "python-sdk-v0300")
        self.assertNotIn("Jul 15, 2025", sec)
        self.assertNotIn("Third entry body", sec)
        self.assertIn("Qwen3.6 supports vision inputs", sec)

    #: Cloudflare Workers AI changelog 形状：日期标题下没有条目小标题，
    #: 条目就是一行裸标题 + 紧跟的 bullet 清单，同一日期下可并列多条。
    CF = (
        "## 2026-06-16\n"
        "\n"
        "GLM-5.2 now available on Workers AI\n"
        "\n"
        "- `@cf/zai-org/glm-5.2` is now available with a 262,144 token context window.\n"
        "- Read the changelog to get started.\n"
        "\n"
        "Moonshot AI Kimi K2.6 now available on Workers AI\n"
        "\n"
        "- `@cf/moonshotai/kimi-k2.6` supports tool calling and vision inputs.\n"
    )

    def test_plain_title_entry_headings_slice_per_entry(self):
        """条目没有标题行时，按「裸标题 + bullet 清单」定位，同日期下两条各归各。"""
        a = ft._slice_anchor_section(self.CF, "glm-52-now-available-on-workers-ai")
        b = ft._slice_anchor_section(self.CF, "moonshot-ai-kimi-k26-now-available-on-workers-ai")
        self.assertIn("262,144 token", a)
        self.assertNotIn("kimi-k2.6", a)
        self.assertIn("tool calling and vision", b)
        self.assertNotIn("GLM-5.2", b)

    def test_fence_interior_lines_are_not_starts(self):
        """代码栅栏内的短行不是条目标题 —— 且屏蔽判定本身要有证人。

        回归：本模块的栅栏正则一度与「剥译文包裹」的同名常量撞车，被静默覆盖，
        于是块内 `curl` 这类行重新参与定位。断言 `_visible_lines` 的形状就是那道证人。
        """
        self.assertEqual(ft._visible_lines(["a", "```", "b", "```", "c"]),
                         [True, False, False, False, True])
        page = ("## 2026-06-16\n\nReal entry title\n\n- a bullet\n\n"
                "```\ncurl\n\nnot a title\n```\n\nnext line of the same entry\n")
        sec = ft._slice_anchor_section(page, "real-entry-title")
        self.assertIn("not a title", sec)
        self.assertIn("next line of the same entry", sec)
        self.assertLess(len(sec), len(page))


    #: 腾讯混元更新日志形状：`## 2025年6月` 小节下面是一张四列表，
    #: **一条更新就是表格里的一行**；锚点 `t<日期>-<序号>` 是抽取时合成的，
    #: 页面上没有任何标题与它对得上 —— 实测 80 行因此只有整页可读。
    TX = (
        "## 2025年6月\n"
        "\n"
        "| **动态名称** | **动态描述** | **发布时间** | **相关文档** |\n"
        "| --- | --- | --- | --- |\n"
        "| hunyuan-t1-vision-20250619 上线 | 特性A：图生文快思考 | 2025-06-19 | [文档](https://t.cn/a) |\n"
        "| hunyuan-turbos-vision-20250619 上线 | 特性B：加速版图生文 | 2025-06-19 | [文档](https://t.cn/b) |\n"
        "\n"
        "## 2025年5月\n"
        "\n"
        "| **动态名称** | **动态描述** | **发布时间** | **相关文档** |\n"
        "| --- | --- | --- | --- |\n"
        "| hunyuan-lite 下线 | 特性C：旧版本停止服务 | 2025-05-09 | [文档](https://t.cn/c) |\n"
    )

    def test_table_row_entry_slices_by_date_and_title(self):
        """条目在表格行里：合成锚点给日期，标题选中那一行，切片带上表头与所属小节。"""
        sec = ft._slice_anchor_section(self.TX, "t2025-06-19-12", "hunyuan-t1-vision-20250619 上线")
        self.assertIn("特性A", sec)
        self.assertNotIn("特性B", sec, "同日期另一行不得混进来")
        self.assertNotIn("特性C", sec)
        self.assertIn("**动态名称**", sec, "没有表头，读者看不懂这一行各列是什么")
        self.assertIn("## 2025年6月", sec)
        self.assertLess(len(sec), len(self.TX))

    def test_ambiguous_or_unmatched_title_refuses_table_slice(self):
        """标题选不中、或同日期几行都合它 —— 一律退回整页，宁缺不错。"""
        whole = ft._slice_anchor_section(self.TX, "t2025-06-19-12", "上线")
        self.assertEqual(whole.strip(), self.TX.strip(), "两行都含「上线」时不许猜一行")
        none = ft._slice_anchor_section(self.TX, "t2025-06-19-12", "根本不存在的一条")
        self.assertEqual(none.strip(), self.TX.strip())

    def test_synthetic_anchor_only_parses_unambiguous_iso_dates(self):
        """合成锚点只认 ISO 日期；月日顺序有歧义的写法一律不认。

        Gemini 版本说明的锚点 `04-09-2025-2` 实测是**美式 MM-DD-YYYY**（该行 date 列
        是 2025-04-09，页面标题是「2025 年 4 月 9 日」）。按 DD-MM 读会指到另一天，
        日期错则正文错 —— 所以这里钉的是「返回 None」，不是某个猜出来的日期。
        """
        self.assertEqual(ft._syn_date_ordinal("t2025-06-19-12"), ("2025-06-19", 12))
        self.assertEqual(ft._syn_date_ordinal("d-2026-06-25-46"), ("2026-06-25", 46))
        self.assertIsNone(ft._syn_date_ordinal("04-09-2025-2"))

    # 智谱更新日志形状：条目名是**普通一行**，下面紧跟 emoji、型号名，再是 bullet。
    # 页面里没有标题语法，也没有能对上锚点的链接 —— 前三种判据全落空。
    ZP = (
        "GLM-5.3-Flash 原生多模态模型上线\n"
        "\n"
        "\U0001f440\n"
        "\n"
        "GLM-5.3-Flash\n"
        "\n"
        "- 原生融入视觉能力，实现代码、浏览器与图形界面的协同闭环。\n"
        "- 极致高效混合架构：总参 320B，激活 18B。\n"
        "\n"
        "GLM-5.3 新一代旗舰模型上线\n"
        "\n"
        "\U0001f4ac\n"
        "\n"
        "GLM-5.3\n"
        "\n"
        "- 更强的编程能力：内部基准较 GLM-5.2 提升 50%。\n"
    )
    ZP_TITLES = ["GLM-5.3-Flash 原生多模态模型上线", "GLM-5.3 新一代旗舰模型上线"]

    def test_sibling_titles_slice_entries_that_are_not_headings(self):
        """分界只认「同页其他条目的标题」，不猜哪行像标题。"""
        a = ft._slice_anchor_section(self.ZP, "2026-08-26", self.ZP_TITLES[0], self.ZP_TITLES)
        b = ft._slice_anchor_section(self.ZP, "2026-08-19", self.ZP_TITLES[1], self.ZP_TITLES)
        self.assertIn("协同闭环", a, "第一条要拿到自己的正文")
        self.assertNotIn("新一代旗舰", a, "第一条不许带上第二条的标题")
        self.assertNotIn("提升 50%", a, "第一条不许带上第二条的正文")
        self.assertIn("提升 50%", b, "第二条（末条）拿到页尾")
        self.assertNotIn("协同闭环", b)
        self.assertLess(len(a), len(self.ZP.strip()), "切完必须比整页短")

    def test_sibling_titles_refuse_ambiguous_or_unmatched(self):
        """标题命中 0 行 / 多行 / 切不出正文，都维持整页，不猜。"""
        dup = self.ZP + "\nGLM-5.3 新一代旗舰模型上线\n\n再来一次。\n"
        got = ft._slice_anchor_section(dup, "x", self.ZP_TITLES[1], self.ZP_TITLES)
        self.assertEqual(got.strip(), dup.strip(), "同一标题命中两行时不许任选一行")
        miss = ft._slice_anchor_section(self.ZP, "x", "页面里根本没有的一条", self.ZP_TITLES)
        self.assertEqual(miss.strip(), self.ZP.strip())
        # 只有标题一行、后面紧跟另一条标题：切出来是空的，维持整页
        tight = "甲上线\n\n乙上线\n\n乙的正文。\n"
        self.assertEqual(ft._slice_anchor_section(tight, "x", "甲上线", ["甲上线", "乙上线"]).strip(),
                         tight.strip(), "切完只剩标题本身就不算切出「这一条」")

    def test_real_anchor_wins_over_sibling_titles(self):
        """页面自己有锚点标题时仍走锚点判据，新判据只兜底。"""
        page = ("## [跳](https://x.cn/docs#a)2026 年 7 月 31 日\n\n"
                "## MiniMax H3\n\n新一代开放通用多模态视频模型，面向文本与视频的统一生成。\n\n"
                "- 支持 1080p 输出与更长的片段时长。\n"
                "- 定价与上一代持平，不额外收费。\n\n"
                "## [跳](https://x.cn/docs#b)2026 年 7 月 16 日\n\nMusic-3.0\n\n尚未推出，仅保留程序公告。\n")
        got = ft._slice_anchor_section(page, "a", "MiniMax H3", ["MiniMax H3", "Music-3.0"])
        self.assertIn("统一生成", got)
        self.assertNotIn("尚未推出", got, "锚点起点切到下一条锚点标题为止")
        self.assertLess(len(got), len(page.strip()))

        self.assertIsNone(ft._syn_date_ordinal("04-09-2025-2"))
        self.assertIsNone(ft._syn_date_ordinal("mcp-connectors-beta"))

    # Gemini API 版本说明形状：`## <日期>` 分节之下是一组 `- **条目名**：说明…`。
    # 条目不是标题行、行内也没有锚点（`#10-08-2026-3` 那个 id 在 HTML 上，readability
    # 抽完就没了）—— 前三种判据全落空，整页 44,439 字符被 42 条共用，正文全部留空。
    GEM = (
        "# 版本说明\n\n本页面记录了 Gemini API 的更新。\n\n"
        "## 2026 年 10 月 8 日\n\n"
        "- **Gemini 3.7 Flash 弃用**：`gemini-3.7-flash` 已弃用，并已由 "
        "`gemini-3.8-flash` 取代。所有请求会自动路由到新模型。\n\n"
        "- **Deep Research 智能体 `deep-research-pro-preview-12-2025` 弃用**："
        "该智能体已弃用，并将于 2026 年 10 月 23 日关停。请将 `interactions.create` "
        "请求中的 `agent` 参数迁移到 `deep-research-preview-04-2026`。\n\n"
        "## 2026 年 10 月 6 日\n\n"
        "- **Gemini Omni Flash 正式版 (GA)**：现已发布于 `gemini-omni-1.1-flash`，"
        "并新增 **视频扩展** 与 **分辨率控制** 两项能力。\n"
    )
    GEM_TITLES = ["Gemini 3.7 Flash 弃用",
                  "Deep Research 智能体 `deep-research-pro-preview-12-2025` 弃用",
                  "Gemini Omni Flash 正式版 (GA)"]

    def test_dated_bullet_entries_slice_by_date_and_title(self):
        """日期分节 + 列表项：日期圈分节、标题选中那一项，切出真正文。"""
        got = ft._slice_anchor_section(
            self.GEM, "10-08-2026-2", self.GEM_TITLES[1], self.GEM_TITLES, "2026-10-08")
        self.assertIn("关停", got)
        self.assertIn("deep-research-preview-04-2026", got)
        self.assertNotIn("已弃用，并已由", got, "同分节的另一条不得混进来")
        self.assertNotIn("视频扩展", got, "别的日期分节也不得混进来")
        self.assertLess(len(got), len(self.GEM.strip()), "切完必须比整页短")

    def test_same_day_entries_never_share_one_body(self):
        """同一天的多条各归各：共用日期标题可以，正文绝不合并。

        分界是「下一个**同级或更浅**的列表项」，所以同一天相邻的两条各自只拿自己那条
        bullet（更深缩进的子要点留在父条目里）。反过来，同名撞车时一律不切 ——
        宁可退回整页被 index_page 拒收，也不让两条共用一份正文。
        """
        first = ft._slice_anchor_section(
            self.GEM, "10-08-2026-1", self.GEM_TITLES[0], self.GEM_TITLES, "2026-10-08")
        second = ft._slice_anchor_section(
            self.GEM, "10-08-2026-2", self.GEM_TITLES[1], self.GEM_TITLES, "2026-10-08")
        self.assertIn("gemini-3.8-flash", first)
        self.assertNotIn("关停", first, "第一条不许带上第二条的正文")
        self.assertIn("关停", second)
        self.assertNotIn("gemini-3.8-flash", second, "第二条不许带上第一条的正文")
        self.assertNotEqual(first, second, "同一天两条不得切出同一份正文")
        # 两份可以共用日期标题行（那是分节抬头，不是正文），但正文部分必须不同
        self.assertEqual(first.splitlines()[0], second.splitlines()[0])
        dup = ("## 2026 年 5 月 19 日\n\n- **弃用公告**：甲的正文在这里。\n\n"
               "- **弃用公告**：乙的正文在这里。\n")
        got = ft._slice_anchor_section(dup, "05-19-2026-1", "弃用公告", ["弃用公告"], "2026-05-19")
        self.assertEqual(got.strip(), dup.strip(), "同分节重名时退回整页，不许任选一条")

    def test_short_entry_below_the_length_floor_is_not_sliced(self):
        """只剩一行条目名、没有说明的 bullet 不算切出「这一条」，返回空串。

        直接测 `_slice_dated_bullets`（而不是 `_slice_anchor_section`）：这种形状会被更早的
        `_slice_by_sibling_titles` 兜住，测上层就测不到这道长度闸门了。
        """
        page = ("## 2026 年 5 月 19 日\n\n- **弃用公告**\n\n"
                "- **别的条目**：有说明的正文，长度要过那道下限，否则两条都会被挡掉、测不出差别。\n")
        self.assertEqual(ft._slice_dated_bullets(page, "弃用公告", "2026-05-19"), "")
        self.assertIn("有说明的正文",
                      ft._slice_dated_bullets(page, "别的条目", "2026-05-19"))

    # Gemini 2025-04-09 的真实形状：`<ul>` 里套 `<ul>`，子条目是**独立的 <li>**。
    # readability 把嵌套压平成父条目里的一串行内粗体，markdown 路径认不出子条目。
    GEM_HTML = (
        '<h2 id="04-09-2025">2025 年 4 月 9 日</h2>\n'
        '<ul>\n'
        '<li>发布了 <code>veo-2.0-generate-001</code>，一款正式版 (GA) 的文本到视频模型。</li>\n'
        '<li><p>发布了 <code>gemini-2.0-flash-live-001</code>，这是启用结算功能的模型。</p>\n'
        '<ul>\n'
        '<li><p><strong>增强的会话管理和可靠性</strong></p>\n'
        '<ul>\n'
        '<li><strong>会话恢复</strong>：在临时网络中断期间保持会话有效。</li>\n'
        '</ul></li>\n'
        '<li><p><strong>可配置的中断处理</strong>：决定用户输入是否应中断模型的回答。</p></li>\n'
        '</ul></li>\n'
        '</ul>\n')

    def test_html_tree_recovers_entries_nested_lists_destroyed(self):
        """嵌套 `<li>` 是独立条目，markdown 丢了层级就回 HTML 取。

        回归：`分辨率控制`、`Gemini 3.8 Live 扩展思考` 在页面里都是独立 `<li>`，只看
        markdown 会把它们当成别的条目的行内子项而丢弃 —— 那不是「子项冒名」，是真条目。
        """
        got = ft._slice_changelog_html(self.GEM_HTML, "可配置的中断处理", "2025-04-09")
        self.assertIn("决定用户输入是否应中断模型的回答", got)
        self.assertNotIn("veo-2.0-generate-001", got, "同分节的别的条目不得混进来")
        self.assertNotIn("会话恢复", got, "更深的孙条目也不该混进来")
        deep = ft._slice_changelog_html(self.GEM_HTML, "会话恢复", "2025-04-09")
        self.assertIn("保持会话有效", deep)
        self.assertNotIn("中断处理", deep, "孙条目不许带上父条目的标题")

    def test_html_tree_refuses_bare_labels_and_unknown_titles(self):
        """只有条目名没有说明的（页面本来就没有正文）、或标题对不上 → 不切。"""
        self.assertEqual(ft._slice_changelog_html(self.GEM_HTML, "增强的会话管理和可靠性",
                                                  "2025-04-09"), "",
                         "只有条目名、下面挂的是子条目 → 本条自己没有正文")
        self.assertEqual(ft._slice_changelog_html(self.GEM_HTML, "页面上根本没有的一条",
                                                  "2025-04-09"), "")
        self.assertEqual(ft._slice_changelog_html(self.GEM_HTML, "可配置的中断处理",
                                                  "2025-01-01"), "",
                         "日期圈错分节就不给，不跨节乱取")
        self.assertEqual(ft._slice_changelog_html(self.GEM_HTML, "可配置的中断处理", ""), "")

    def test_html_tree_keeps_links_and_code_as_markdown(self):
        """切片是给读者看的正文，链接与 `<code>` 要转成 markdown，不能剩裸标签。"""
        html = ('<h2 id="05-19-2026">2026 年 5 月 19 日</h2><ul>'
                '<li><p><strong>文件搜索</strong>：请参阅 '
                '<a href="https://x.cn/fs">文件搜索文档</a>，并使用 '
                '<code>gemini-embedding-2</code> 模型。</p></li></ul>')
        got = ft._slice_changelog_html(html, "文件搜索", "2026-05-19")
        self.assertIn("[文件搜索文档](https://x.cn/fs)", got)
        self.assertIn("`gemini-embedding-2`", got)
        self.assertNotIn("<a ", got)
        self.assertNotIn("<code>", got)

    def test_html_tree_never_leaks_script_or_style(self):
        """`<script>` / `<style>` 的内容一个字都不许进正文。

        回归：HTMLParser 会把脚本正文当普通 data 回调，不挡的话 `var x=1` 和整段 CSS
        会跟着条目一起落进 `docs/articles/` 给读者看。
        """
        for junk, tag in (('var leak="SCRIPTLEAK";', "script"), ('.x{color:red}', "style")):
            html = ('<h2 id="05-19-2026">2026 年 5 月 19 日</h2><ul>'
                    '<li><p><strong>文件搜索</strong>：更新了文件搜索以支持多模态搜索。'
                    '<{t}>{j}</{t}></li></ul>').format(t=tag, j=junk)
            got = ft._slice_changelog_html(html, "文件搜索", "2026-05-19")
            self.assertIn("支持多模态搜索", got)
            self.assertNotIn(junk, got, "<%s> 内容漏进正文了" % tag)

    def test_html_tree_handles_b_tags_and_unclosed_li(self):
        """`<b>` 与 `<strong>` 同等；漏写 `</li>` 不许让整页条目消失。

        回归：开始标签只认 `strong` 而结束标签认 `("strong","b")`，`<b>条目名</b>` 的
        条目名取不到（该条永远匹配不上），还会在正文里留下一对没配平的 `**`。而
        HTMLParser 不做隐式闭合，`<li>a<li>b</ul>` 会让**后面每一条**都压在栈里、
        一个都不收。
        """
        h2 = '<h2 id="05-19-2026">2026 年 5 月 19 日</h2><ul>'
        got = ft._slice_changelog_html(
            h2 + '<li><b>文件搜索</b>：更新了文件搜索以支持多模态搜索。</li></ul>',
            "文件搜索", "2026-05-19")
        self.assertIn("支持多模态搜索", got)
        self.assertTrue(got.startswith("**文件搜索**："), "``<b>`` 应转成配平的 **，实际 %r" % got[:30])

        second = ft._slice_changelog_html(
            h2 + '<li><strong>甲号条目上线</strong>：甲的正文内容在这里有足够长的一段说明文字。'
                 '<li><strong>乙号条目上线</strong>：乙的正文内容也在这里有足够长的一段说明文字。</ul>',
            "乙号条目上线", "2026-05-19")
        self.assertIn("乙的正文内容", second, "漏写 </li> 不该把后面的条目全丢掉")
        self.assertNotIn("甲的正文内容", second)

    def test_dated_bullets_ignore_fenced_code_samples(self):
        """代码块里的 `- xxx` 是 YAML/JSON 示例行，不是条目。

        回归：`_slice_dated_bullets` 原来不查 `_visible_lines()`（同族的
        `_slice_anchor_section` 却一路传着 `visible` 掩码），于是文档站示例代码里的
        一行会当条目名被切出来，读者点开看到的是一段配置片段。
        """
        page = ("## 2026 年 5 月 19 日\n\n```yaml\n"
                "- 假条目名：这段文字在代码块里，是示例配置不是条目。\n```\n")
        self.assertEqual(ft._slice_dated_bullets(page, "假条目名", "2026-05-19"), "")

    def test_native_translation_must_actually_contain_chinese(self):
        """`translator: native` ⟹ 正文里真的有汉字。

        回归：中文页上整条是**纯英文**公告时，判中文的兜底（整页是中文）会把它登记成
        已完成的汉化；而 `zh_status=translated` 让它此后被 `fetch_bodies` 永久跳过、
        `reclassify_bodies` 又只查 `en_status == "ok"` 的行 —— 没有这道闸就再也回不来。
        """
        with tempfile.TemporaryDirectory() as d:
            slug = "cccc0000dddd"
            rel = "docs/articles/google_gemini/%s.md" % slug
            p = Path(d) / rel
            p.parent.mkdir(parents=True)
            ft.write_body_doc(p, {"vendor": "google_gemini", "title": "T",
                                  "status": "translated", "translator": "native"},
                             "This announcement is entirely in English, no CJK at all.")
            bodies = {"google_gemini\thttps://x/p": {
                "slug": slug, "en_path": "", "en_status": "", "zh_path": rel,
                "zh_status": "translated", "translator": "native", "title": "T",
                "date": "", "captured": "", "body_sha": "x", "src_lang": "zh"}}
            errs = ft.validate_bodies(Path(d), bodies)
            self.assertTrue(any("没有汉字" in e for e in errs),
                            "纯英文正文登记成 native 必须报错，实际：%r" % errs)

    def test_html_tree_dates_sections_by_heading_text_not_by_ambiguous_id(self):
        """分节靠**标题文字**认日期，不靠 `id`。

        回归：`id="10-08-2026"` 是月日顺序有歧义的写法，按两种顺序都认会把
        **另一天**的分节当成本条 —— 实测 ledger date=2026-10-08 会切到 `08-10-2026`
        那节去，「唯一命中」这道守卫救不了（错的那节恰好只有它匹配）。
        标题文字 `2026 年 8 月 10 日` 年月在前、无歧义，且 ledger 的 date 本就从它解析。
        """
        html = ('<h2 id="08-10-2026">2026 年 8 月 10 日</h2><ul>'
                '<li><strong>八月条目</strong>：这是八月那条的正文内容，足够长了吧。</li></ul>'
                '<h2 id="10-08-2026">2026 年 10 月 8 日</h2><ul>'
                '<li><strong>十月条目</strong>：这是十月那条的正文内容，也足够长。</li></ul>')
        self.assertEqual(ft._slice_changelog_html(html, "八月条目", "2026-10-08"), "",
                         "date=2026-10-08 不许取到 8 月 10 日那节的内容")
        self.assertIn("十月那条", ft._slice_changelog_html(html, "十月条目", "2026-10-08"))
        self.assertIn("八月那条", ft._slice_changelog_html(html, "八月条目", "2026-08-10"))

    def test_dated_bullets_refuse_subitem_and_lookalike_titles(self):
        """子项与形近标题一律不切：宁缺不错，不给张冠李戴的正文。

        「分辨率控制」是 Gemini Omni Flash 那条的**说明里的子项**，不是独立条目；
        「Antigravity 09-2026」与条目名「Antigravity Agent 09-2026」只差中间一个词。
        两者都不得命中那条的正文。
        """
        for title in ("分辨率控制", "视频扩展"):
            got = ft._slice_anchor_section(self.GEM, "10-06-2026-1", title, self.GEM_TITLES, "2026-10-06")
            self.assertEqual(got.strip(), self.GEM.strip(), "子项 %r 不得冒名顶替整个条目" % title)
        lookalike = self.GEM + "\n## 2026 年 5 月 19 日\n\n- **Antigravity Agent**：受管代理已发布。\n"
        got = ft._slice_anchor_section(lookalike, "05-19-2026-1", "Antigravity",
                                      self.GEM_TITLES + ["Antigravity"], "2026-05-19")
        self.assertIn("受管代理", got, "条目名以标题开头时应当命中")
        got2 = ft._slice_anchor_section(lookalike, "05-19-2026-1", "Antigravity 09-2026",
                                       self.GEM_TITLES + ["Antigravity 09-2026"], "2026-05-19")
        self.assertEqual(got2.strip(), lookalike.strip(), "词中间不同的标题不得命中")

    def test_dated_bullets_ignore_the_anchor_ordinal(self):
        """锚点里的序号会位移，**只认标题**。

        Gemini 2026-10-08 分节昨天只有 1 条（Deep Research = `-1`），今天有 3 条，
        `-1` 已经变成「Gemini 3.7 Flash 弃用」。若按序号取，这条标题会被挂上别的条目正文。
        """
        stale = ft._slice_anchor_section(
            self.GEM, "10-08-2026-1", self.GEM_TITLES[1], self.GEM_TITLES, "2026-10-08")
        self.assertIn("deep-research-preview-04-2026", stale, "序号过期时仍按标题取到自己的正文")
        self.assertNotIn("已弃用，并已由", stale, "不许按序号取到 Gemini 3.7 Flash 那条")

    def test_dated_bullets_need_a_date_and_a_real_title(self):
        """没有 date（调用方没给）或标题太短，都维持整页。"""
        got = ft._slice_anchor_section(self.GEM, "10-08-2026-2", self.GEM_TITLES[1], self.GEM_TITLES)
        self.assertEqual(got.strip(), self.GEM.strip(), "没有 date 就不猜")
        for bad in ("弃用", "", "   "):
            out = ft._slice_anchor_section(self.GEM, "10-08-2026-2", bad, self.GEM_TITLES, "2026-10-08")
            self.assertEqual(out.strip(), self.GEM.strip(), "标题 %r 不够定位，维持整页" % bad)

    def test_heading_date_keys_accept_the_writings_changelogs_use(self):
        """分节标题的日期写法各页不同，都要收敛到同一个 ISO。"""
        self.assertEqual(ft._heading_date_keys("2026 年 10 月 8 日"), {"2026-10-08"})
        self.assertEqual(ft._heading_date_keys("2026年10月8日"), {"2026-10-08"})
        self.assertEqual(ft._heading_date_keys("October 8, 2026"), {"2026-10-08"})
        self.assertEqual(ft._heading_date_keys("Oct 8, 2026"), {"2026-10-08"})
        self.assertEqual(ft._heading_date_keys("版本说明"), set(), "非日期标题认不出就返回空集")
        self.assertEqual(ft._heading_date_keys("model-2025-rc1"), set(), "版本号不当日期")

class TestIdentityAndLinkAreSeparate(unittest.TestCase):
    """**身份（url）与展示链接（link）必须是两个东西**。

    起因：单页变更日志里 `<li>` 没有自己的锚点，索引侧用「分节 id + 序号」合成
    `#10-06-2026-1` 当身份 —— 但页面上根本没有这个 id，点开停在版本说明页顶（实测
    Gemini 158 行 / 5 个厂商全是这种假锚点）。修法是链接改用实读的分节锚点
    `#10-06-2026`，身份原样保留。

    身份不能改：`--rebuild-only` 从归档 markdown 的链接反推 url 与 slug，一旦把
    可见链接换成真锚点，同一分节的十几条会塌成同一个 slug，正文互相覆盖。
    """

    SECTIONS = (
        '<h2 id="10-06-2026">2026 年 10 月 6 日</h2><ul>'
        '<li><strong>甲条目正式发布了</strong>：甲条目的正文说明，足够长的一段文字。</li>'
        '<li><strong>乙条目弃用公告发布</strong>：乙条目的正文说明，也足够长的一段文字。</li>'
        '</ul>'
        '<h2 id="10-07-2026">2026 年 10 月 7 日</h2><ul>'
        '<li><strong>丙条目更新说明上线</strong>：丙条目的正文说明，同样足够长的一段。</li>'
        '</ul>')

    def _arts(self):
        page = crawler_llm_intel.PageResult(
            url="https://x.test/changelog?hl=zh-cn",
            final_url="https://x.test/changelog?hl=zh-cn",
            text="", raw=self.SECTIONS, stype="changelog")
        return crawler_llm_intel.extract_changelog_sections(page, max_items=50)

    def test_synthesised_ordinal_is_identity_and_section_anchor_is_link(self):
        arts = self._arts()
        self.assertEqual(len(arts), 3)
        by_title = {a.title: a for a in arts}
        deep = by_title["甲条目正式发布了"]
        self.assertTrue(deep.url.endswith("#10-06-2026-1"),
                        "身份仍是合成分节 id + 序号，实得 %r" % deep.url)
        self.assertEqual(deep.link, "https://x.test/changelog?hl=zh-cn#10-06-2026",
                         "展示链接必须是页面上真有的分节锚点")
        second = by_title["乙条目弃用公告发布"]
        self.assertTrue(second.url.endswith("#10-06-2026-2"))
        self.assertEqual(second.link, deep.link, "同一分节的两条共用展示链接")
        self.assertNotEqual(deep.url, second.url, "身份必须各不相同")

    def test_archive_round_trip_keeps_identity_and_link_apart(self):
        """归档写出真链接 + `<!--url:身份-->`，读回来必须还原成同一对值。"""
        arts = self._arts()
        ident = {a.title: a.url for a in arts}
        link = {a.title: a.link for a in arts}
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "google_gemini.md"
            lines = ["# 归档", ""]
            for i, a in enumerate(arts, 1):
                lines.append(f"{i}. [{a.title}]({a.link})（{a.date}） <!--url:{a.url}-->")
            p.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
            back = crawler_llm_intel.parse_archived_articles(p)
            self.assertEqual(len(back), len(arts))
            for a in back:
                self.assertEqual(a.url, ident[a.title], "身份没还原")
                self.assertEqual(a.link, link[a.title], "展示链接没还原")
            slugs = {ft.url_hash(a.url) for a in back}
            self.assertEqual(len(slugs), len(arts),
                             "身份塌成同一个 slug 会让同一分节的正文互相覆盖")

    def test_legacy_archive_line_without_comment_is_its_own_identity(self):
        """旧归档行没有 `<!--url:-->` 注释：可见链接就是身份，两者相同。"""
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "v.md"
            p.write_text("1. [旧条目标题](https://x.test/c#10-06-2026-1)（2026-10-06）\n",
                         encoding="utf-8", newline="\n")
            a = crawler_llm_intel.parse_archived_articles(p)[0]
            self.assertEqual(a.url, "https://x.test/c#10-06-2026-1")
            self.assertEqual(a.link, a.url)

    def test_rss_link_is_displayable_but_guid_stays_identity(self):
        """阅读器点 `<link>` 要能跳；`<guid>` 必须是身份，否则同分节十几条会被当新条目重推。"""
        art = crawler_llm_intel.Article(
            title="Gemini 3.7 Flash deprecation", url="https://x.test/c#10-06-2026-1",
            link="https://x.test/c#10-06-2026", date="2026-10-06")
        item = crawler_llm_intel._rss_item(art, "Gemini 3.7 Flash 弃用")
        self.assertIn("<link>https://x.test/c#10-06-2026</link>", item)
        self.assertIn("https://x.test/c#10-06-2026-1</guid>", item)
        self.assertNotIn("<link>https://x.test/c#10-06-2026-1</link>", item)

    def test_index_column_and_page_prefer_link(self):
        with tempfile.TemporaryDirectory() as d:
            v = crawler_llm_intel.VendorIntel(vendor_id="v", brand="V", homepage="", products=[])
            v.all_news_articles = [
                crawler_llm_intel.Article(title="T", url="https://v.test/c#10-06-2026-1",
                                          link="https://v.test/c#10-06-2026", date="2026-10-06")]
            feeds = Path(d) / "feeds"
            crawler_llm_intel.write_rss_feeds(feeds, [v], "")
            data = json.loads((feeds / "articles.json").read_text(encoding="utf-8"))
            row = data["articles"][0]
            self.assertEqual(row[1], "https://v.test/c#10-06-2026-1", "url 列仍是身份")
            self.assertEqual(row[data["fields"].index("link")], "https://v.test/c#10-06-2026")
            self.assertEqual(row[5], ft.url_hash(row[1]), "slug 仍由身份算出")
        page = (Path(__file__).resolve().parent / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertIn("link: r[8] || r[1] || ''", page,
                      "页面必须优先用 link 列，老索引（无第 9 列）退回 url")


    def test_backfill_links_only_repairs_rows_whose_section_anchor_really_exists(self):
            """回填只修「去掉序号确实是页面上真锚点」的行，其余原样不动。

            B 类源站（腾讯混元 `t-…`、streamlake、siliconflow、poolside）压根没给锚点 ——
            连去掉序号的前缀在页面上都不存在。给它们编一个「看起来能跳」的链接是**造假**，
            必须原样留着。
            """
            html = '<h2 id="10-06-2026">2026 年 10 月 6 日</h2>'   # 只有这一个真 id
            page = ("<h2 id=\"10-08-2026\">2026 年 10 月 8 日</h2>"
                    "<h2 id=\"10-06-2026\">2026 年 10 月 6 日</h2>")
            with tempfile.TemporaryDirectory() as d:
                nd = Path(d)
                (nd / "google_gemini.md").write_text(
                    "1. [甲条目正式发布了](https://x.test/c#10-06-2026-1)（2026-10-06）\n"
                    "2. [乙条目弃用公告发布](https://x.test/c#10-09-2026-1)（2026-10-09）\n"
                    "3. [丙条目更新说明上线](https://x.test/c#t2026-08-14-0)（2026-08-14）\n"
                    "4. [丁条目已是真链接](https://x.test/c#10-06-2026)（2026-10-06）\n",
                    encoding="utf-8", newline="\n")
                calls = []

                def fetch(u):
                    calls.append(u)
                    return page

                visited, fixed = crawler_llm_intel.backfill_archive_links(
                    nd, fetch, delay=0)
                self.assertEqual(visited, 1, "同一个分节页只该抓一次，实得 %d 次" % visited)
                self.assertEqual(fixed, 1, "只有甲那条能修")
                text = (nd / "google_gemini.md").read_text(encoding="utf-8")
                lines = text.splitlines()
                self.assertIn("(https://x.test/c#10-06-2026)（2026-10-06） "
                              "<!--url:https://x.test/c#10-06-2026-1-->", lines[0],
                              "甲：可见链接换成真锚点、身份进注释")
                self.assertIn("#10-09-2026-1", lines[1], "乙：页面没这个 id，原样不动")
                self.assertIn("#t2026-08-14-0", lines[2], "丙：源站无锚点，原样不动")
                self.assertIn("#10-06-2026)", lines[3], "丁：本来就是真链接，不动")
                self.assertNotIn("<!--url:", lines[1] + lines[2] + lines[3])
                # 回填后再跑一次不应再改任何行（幂等）。可能仍会为「已经是真链接」的
                # 那行抓一次页去核对 —— 每个分节页只抓一次，代价有界。
                again = crawler_llm_intel.backfill_archive_links(nd, fetch, delay=0)
                self.assertEqual(again[1], 0, "已修过的行不该被重复改写")
                self.assertEqual((nd / "google_gemini.md").read_text(encoding="utf-8"), text,
                                 "第二次跑不应产生任何 diff")


class TestListedMeansReadable(unittest.TestCase):
    """不变量：进了 articles.json 的每一行，要么磁盘上有正文文件，要么台账写明读不到。

    回归的是读者报的那个现象：「标题在列表里，点开却说没进语料」。根因链是单页变更日志
    的 N 条条目共用一份整页正文（旧身份不认 fragment）→ 整页被判目录页 → 正文留空，
    可 N 行标题照样发布；`readable` 的 '' 态（「还没轮到正文抓取」）于是变成「按钮亮着、
    点进去 404」。'' 一旦进了提交产物就是骗点击，所以这里要求它为 0。
    """

    def _payload(self, rows):
        return {"fields": ["title", "url", "vendor", "date", "original_title", "slug", "readable"],
                "count": len(rows), "articles": rows}

    def _row(self, vendor, slug, url, title="t"):
        return [title, url, vendor, "2026-01-02", "", slug, ""]

    def test_committed_artifacts_have_no_undocumented_rows(self):
        repo = Path(__file__).resolve().parent
        idx = json.loads((repo / "docs/feeds/articles.json").read_text(encoding="utf-8"))
        entries = json.loads((repo / "docs/feeds/bodies.json").read_text(encoding="utf-8"))["bodies"]
        gaps = crawler_llm_intel.corpus_gaps(idx, entries, repo)
        self.assertEqual(
            gaps, [],
            "这些行既没有 docs/articles 下的正文文件，台账也没记不可读原因："
            "%s —— 读者点开只会看到「还没落到语料里」" % gaps[:5])

    def test_gap_detection_needs_file_or_documented_reason(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            v = "demo"
            (root / "docs/articles" / v).mkdir(parents=True)
            (root / "docs/articles" / v / "havefile01.en.md").write_text("x", encoding="utf-8")
            url_ok = "https://demo.test/blog/a#1"
            url_doc = "https://demo.test/blog/b#2"
            url_bad = "https://demo.test/blog/c#3"
            rows = [self._row(v, "havefile01", url_ok),
                    self._row(v, "docreason1", url_doc),
                    self._row(v, "nothing001", url_bad)]
            entries = {
                ft.bodies_key(v, url_doc): {"slug": "docreason1", "en_status": "index_page"},
                ft.bodies_key(v, url_bad): {"slug": "nothing001", "en_status": "ok"},
            }
            gaps = crawler_llm_intel.corpus_gaps(self._payload(rows), entries, root)
            self.assertEqual([g[1] for g in gaps], ["nothing001"],
                             "有文件 / 记了 index_page 的都算有说法；只标 ok 却没文件才是缺口")

    def test_unreadable_status_list_is_the_whole_vocabulary(self):
        """台账里能算「有说法」的状态是封闭集合，别让人新造一个混过守卫。"""
        self.assertEqual(set(crawler_llm_intel.UNREADABLE_STATUSES),
                         {"fetch_failed", "index_page", "paywall"})

    def test_empty_body_file_is_not_readable(self):
        """文件在但正文空 ≠ 有可读的东西。

        回归：`reclassify_bodies` 判成目录页时清空正文**却留着文件**，只看文件在不在
        的话，29 行空正文会一边报 `readable=1`（读者点开是空的）一边让缺口检查报绿。
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            v = "demo"
            (root / "docs/articles" / v).mkdir(parents=True)
            ft.write_body_doc(root / "docs/articles" / v / "emptbody01.en.md",
                              {"status": "index_page", "url": "https://demo.test/x"}, "")
            ft.write_body_doc(root / "docs/articles" / v / "hasbod001.md",
                              {"status": "translated", "url": "https://demo.test/y"}, "有正文")
            ft.write_body_doc(root / "docs/articles" / v / "blankline.en.md",
                              {"status": "ok", "url": "https://demo.test/z"}, "   \n\n  ")
            self.assertFalse(crawler_llm_intel.has_readable_body(root, v, "emptbody01"),
                             "frontmatter 之后没字 = 读不出东西")
            self.assertTrue(crawler_llm_intel.has_readable_body(root, v, "hasbod001"))
            self.assertFalse(crawler_llm_intel.has_readable_body(root, v, "blankline"),
                             "只有一堆空白行也算读不出")
            self.assertFalse(crawler_llm_intel.has_readable_body(root, v, "nosuchslug"),
                             "厂商目录都没有 = 读不出")
            # 缺口侧：台账只标 ok 却没有真正文 → 仍然是缺口（不能因为空文件躺在盘上就放过）
            url = "https://demo.test/x#9"
            rows = [self._row(v, "emptbody01", url)]
            gaps = crawler_llm_intel.corpus_gaps(
                self._payload(rows), {ft.bodies_key(v, url): {"slug": "emptbody01",
                                                              "en_status": "ok"}}, root)
            self.assertEqual([g[1] for g in gaps], ["emptbody01"],
                             "空正文文件不许冒充「已经有正文」")
            # 但记了不可读原因时空文件只是占位，不该算缺口
            gaps2 = crawler_llm_intel.corpus_gaps(
                self._payload(rows), {ft.bodies_key(v, url): {"slug": "emptbody01",
                                                              "en_status": "index_page"}}, root)
            self.assertEqual(gaps2, [], "标了 index_page 的行按钮本就不亮，占位文件无害")

    def test_body_langs_names_which_languages_are_on_disk(self):
        """langs 列分清「有哪门正文」，页面据此决定 EN 页签亮不亮、要不要发探测请求。

        回归：页面原先只能靠**先发一个注定 404 的请求**去猜另一种语言在不在，而那个
        404 会在语言回退里抢赢正文请求，只有单语正文的行点开是空白或假报错。
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            v = "demo"
            (root / "docs/articles" / v).mkdir(parents=True)
            cases = {
                "bothlang01": ("both", "中文", "English"),
                "zhonly0001": ("zh", "只有中文", None),        # 中文原生页
                "enonly0001": ("en", None, "English only"),    # 还没译的英文页
                "nonehere001": ("", None, None),
            }
            for slug, (want, zh, en) in cases.items():
                if zh is not None:
                    ft.write_body_doc(root / "docs/articles" / v / f"{slug}.md",
                                      {"url": f"https://demo.test/{slug}"}, zh)
                if en is not None:
                    ft.write_body_doc(root / "docs/articles" / v / f"{slug}.en.md",
                                      {"url": f"https://demo.test/{slug}"}, en)
                self.assertEqual(crawler_llm_intel.body_langs(root, v, slug), want,
                                 f"{slug} 应该是 {want}")
            # 空正文的 .en.md 不算「有英文」——否则 EN 页签亮着，点进去是空的
            ft.write_body_doc(root / "docs/articles" / v / "emptzh001.md",
                              {"url": "https://demo.test/w"}, "有正文")
            ft.write_body_doc(root / "docs/articles" / v / "emptzh001.en.md",
                              {"url": "https://demo.test/w"}, "")
            self.assertEqual(crawler_llm_intel.body_langs(root, v, "emptzh001"), "zh")

    def test_committed_artifacts_have_no_empty_body_claiming_readable(self):
        """已提交索引里不许有 `readable=1` 却读不出正文的行——判据得在真产物上成立。

        这条是上一条在**产物**上的落地：把「文件在」换成「正文在」之前，盘上有 29 行
        满足「文件在、正文空、readable=1」。
        """
        repo = Path(__file__).resolve().parent
        idx = json.loads((repo / "docs/feeds/articles.json").read_text(encoding="utf-8"))
        f = {k: i for i, k in enumerate(idx["fields"])}
        empty = [r[f["vendor"]] + "/" + r[f["slug"]]
                 for r in idx["articles"]
                 if r[f["slug"]] and r[f["readable"]] == "1"
                 and not crawler_llm_intel.has_readable_body(repo, r[f["vendor"]], r[f["slug"]])]
        self.assertEqual(empty, [], "这些行声明可读却读不出东西：%s" % empty[:10])

    def test_committed_bodies_are_all_ledgered(self):
        """盘上有正文文件的索引行，台账里必须有对应键。

        回归：3 行在身份改认 fragment 后文件落了新名、台账键没跟上，于是对所有
        「按台账扫正文」的检查隐身——它们一直把整页变更日志当正文发给读者。
        """
        repo = Path(__file__).resolve().parent
        idx = json.loads((repo / "docs/feeds/articles.json").read_text(encoding="utf-8"))
        entries = json.loads((repo / "docs/feeds/bodies.json").read_text(encoding="utf-8"))["bodies"]
        ghost = crawler_llm_intel.unledgered_body_files(idx, entries, repo)
        self.assertEqual(ghost, [], "这些行有正文却不在台账里，任何台账扫描都看不见它们：%s" % ghost[:8])

    def test_unledgered_detection_needs_a_real_body(self):
        """判据本身：只有「真读得出正文」的行才算，缺口行由 corpus_gaps 管。"""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "docs/articles/demo").mkdir(parents=True)
            ft.write_body_doc(root / "docs/articles/demo/aaaa00000009.md",
                              {"status": "translated"}, "正文" * 40)
            rows = [self._row("demo", "aaaa00000009", "https://demo.test/log#9"),
                    self._row("demo", "bbbb00000001", "https://demo.test/log#8")]
            self.assertEqual(crawler_llm_intel.unledgered_body_files(self._payload(rows), {}, root),
                             ["demo/aaaa00000009"],
                             "有文件没台账键的才算；什么都没的交给缺口检查")
            self.assertEqual(crawler_llm_intel.unledgered_body_files(
                self._payload(rows), {ft.bodies_key("demo", rows[0][1]): {"slug": "aaaa00000009"}},
                root), [], "台账里有键就不算幽灵行")

    def test_no_two_rows_share_one_whole_page_body(self):
        """已提交语料里不许有两行条目共用同一份正文。

        回归：单页变更日志重键后，N 条条目各自存了一份**整页**副本（实测 12 组
        129 行、约 2.5 MB），读者点任何一条都是同一张全表。
        """
        repo = Path(__file__).resolve().parent
        idx = json.loads((repo / "docs/feeds/articles.json").read_text(encoding="utf-8"))
        groups = crawler_llm_intel.duplicate_body_groups(idx, repo)
        self.assertEqual(groups, [],
                         "这些行共用同一份正文（整页被复制成 N 篇）：%s" % groups[:5])

    def test_duplicate_body_group_detection_shape(self):
        """判据本身：跨行同正文要抓到；同一行原文=中文不算；短正文不算。

        文件按 `vendor/slug` 直取，**不看台账有没有这一行**：实测有 3 行丢了台账键、
        盘上却还装着整页正文，只查台账的写法对它们完全隐身。
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "docs/articles/demo").mkdir(parents=True)
            long = "长正文" * 120
            ft.write_body_doc(root / "docs/articles/demo/aaaa00000001.en.md",
                              {"status": "ok"}, long)
            ft.write_body_doc(root / "docs/articles/demo/aaaa00000002.en.md",
                              {"status": "ok"}, long)          # 另一行，同一份
            own = "另一份长正文" * 100
            ft.write_body_doc(root / "docs/articles/demo/aaaa00000003.en.md",
                              {"status": "ok"}, own)
            ft.write_body_doc(root / "docs/articles/demo/aaaa00000003.md",
                              {"status": "translated"}, own)   # 同一行的中文侧
            short = "短句" * 20
            ft.write_body_doc(root / "docs/articles/demo/aaaa00000004.en.md",
                              {"status": "ok"}, short)
            ft.write_body_doc(root / "docs/articles/demo/aaaa00000005.en.md",
                              {"status": "ok"}, short)
            rows = []
            for slug, url in (("aaaa00000001", "https://demo.test/log#1"),
                              ("aaaa00000002", "https://demo.test/log#2"),
                              ("aaaa00000003", "https://demo.test/log#3"),
                              ("aaaa00000004", "https://demo.test/log#4"),
                              ("aaaa00000005", "https://demo.test/log#5")):
                rows.append(self._row("demo", slug, url))
            got = crawler_llm_intel.duplicate_body_groups(self._payload(rows), root)
            self.assertEqual(got, [["demo/aaaa00000001", "demo/aaaa00000002"]],
                             "只该报跨行的整页复制；同一行两侧相同与短正文撞车都不算")

    def test_missing_slug_column_does_not_panic(self):
        self.assertEqual(crawler_llm_intel.corpus_gaps({"fields": ["title"], "articles": [["t"]]}, {}, Path(__file__).resolve().parent), [])

    def test_fetch_vendor_selects_all_listed_vendors(self):
        """`--fetch-vendor` 可重复，多家一起跑。

        回归：这个参数曾是单值，`--fetch-vendor a --fetch-vendor b` 只有最后一个生效，
        实测一整轮只跑了最后一家还以为都跑完了。
        """
        rows = [{"vendor": v, "url": "https://%s.test/x" % v} for v in ("groq", "anyscale", "groq")]
        got = crawler_llm_intel.select_body_rows(rows, ["groq", "anyscale"])
        self.assertEqual([r["vendor"] for r in got], ["groq", "anyscale", "groq"],
                         "传两家就得两家的行都留下")
        self.assertEqual(len(crawler_llm_intel.select_body_rows(rows, [])), 3, "空 = 不限厂商")
        self.assertEqual([r["vendor"] for r in crawler_llm_intel.select_body_rows(rows, ["anyscale"], 1)],
                         ["anyscale"], "limit 必须在厂商筛选之后生效（先截后筛就会漏掉目标厂商）")
        with tempfile.TemporaryDirectory() as d:
            argv = ["--fetch-bodies", "--fetch-vendor", "groq", "--fetch-vendor", "anyscale"]
            ns = crawler_llm_intel.build_arg_parser().parse_args(argv)
            self.assertEqual(ns.fetch_vendor, ["groq", "anyscale"],
                             "argparse 必须是 action=append，否则只剩最后一家")
        # 逃生阀要从命令行真的传到 fetch_bodies 的闸门参数上
        ns = crawler_llm_intel.build_arg_parser().parse_args(
            ["--fetch-bodies", "--retry-unreadable"])
        self.assertTrue(ns.retry_unreadable, "--retry-unreadable 必须存在并落到 args")
        self.assertFalse(crawler_llm_intel.build_arg_parser().parse_args(
            ["--fetch-bodies"]).retry_unreadable, "默认不重抓已判定读不到的行（CI 每日走默认）")


class TestReadFullButtonHonesty(unittest.TestCase):
    """「读全文」按钮不许给读者一个已知点不开的入口。

    回归：按钮只看「有没有 slug」，而 slug 在文章**刚被收录**时就发下来了，于是每篇
    都亮。正文要等 CI 后续的 --fetch-bodies / --mt-bodies 才落盘，中间必然有一段
    点了报「这篇正文还没落到语料里」的窗口；另有 27 条 `fetch_failed`、15 条
    `index_page` 则是**永远**读不出来。读者最爱点的恰好是最新那批。

    三态判据（articles.json 的 readable 列）：'0' 已判定抓不到 → 不亮；
    '1' 磁盘已有正文 → 亮；'' 还没轮到正文步骤 → 照旧亮（不提前藏掉新文章）。
    """

    @classmethod
    def setUpClass(cls):
        cls.page = (Path(__file__).resolve().parent / "docs" / "index.html").read_text(
            encoding="utf-8")

    def test_index_carries_the_readable_column(self):
        import json
        idx = json.loads((Path(__file__).resolve().parent
                          / "docs/feeds/articles.json").read_text(encoding="utf-8"))
        self.assertIn("readable", idx["fields"],
                      "articles.json 少一列 readable，按钮就退回「只看 slug」")
        width = len(idx["fields"])
        self.assertTrue(all(len(r) == width for r in idx["articles"]),
                        "有行宽度对不上 readable 列，页面按位置取列会整体错位")

    def test_button_is_hidden_only_when_known_unreadable(self):
        row = self.page[self.page.index("function rowNode"):]
        row = row[:row.index("function appendRows")]
        self.assertIn("it.slug && it.readable !== '0'", row,
                      "按钮判据必须是 slug 且非「已判定抓不到」")
        self.assertNotIn("if (it.slug) {", row,
                         "只看 slug 的旧判据会让每篇都亮按钮")

    def test_reader_falls_back_to_the_other_language(self):
        """中文原生页只有 .md、英文页可能中文还没译 —— 都不该把读者挡在门外。

        决议本身是 `FLI.loadBody`（docs/app.test.mjs 有时序行为用例），页面只负责调用；
        这里钉的是**不许退回旧的 Promise.race**：两个请求赛跑时，另一语言那个注定 404
        的响应常常先落地，「没有另一种语言」就被当成「这篇没有正文」，抽屉渲染成空白。
        """
        load = re.search(r"function readerLoad\([^)]*\)\s*\{(.*?)\n  \}",
                         self.page, re.S)
        self.assertIsNotNone(load)
        body = load.group(1)
        self.assertIn("FLI.loadBody(", body, "正文语言决议要走 FLI.loadBody")
        self.assertNotIn("Promise.race", self.page,
                         "reader 不许再用 Promise.race 让 404 与正文赛跑")
        self.assertIn("readerMdPath(reader.vendor, reader.slug, lang)", body)


class TestFulltextBodyDoc(unittest.TestCase):
    """frontmatter 扁平读写 + 原子落盘。"""

    def test_body_doc_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.md"
            fm = {"vendor": "openai", "title": "GPT: 发布: 新版", "url": "https://a.com/p"}
            ft.write_body_doc(p, fm, "正文\n第二行")
            got_fm, got_body = ft.read_body_doc(p)
            self.assertEqual(got_fm, fm)
            self.assertEqual(got_body, "正文\n第二行")

    def test_body_doc_atomic_write_leaves_no_tmp(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "y.md"
            ft.write_body_doc(p, {"a": "1"}, "body")
            self.assertEqual(list(Path(d).glob("*.tmp")), [])

    def test_read_body_doc_without_frontmatter_raises(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "z.md"
            p.write_text("no frontmatter here", encoding="utf-8")
            self.assertRaises(ValueError, ft.read_body_doc, p)


class TestFulltextExtractor(unittest.TestCase):
    """正文抽取（密度选主块 + markdown 化 + 硬失败判定），golden fixtures 冻结输入。"""

    FIX = Path("tests/fixtures/articles")

    def _read(self, name):
        return (self.FIX / name).read_text(encoding="utf-8")

    def test_longform_golden(self):
        r = ft.extract_article_markdown(self._read("longform.html"), "https://vendor.example/p")
        self.assertEqual(r["reason"], "")
        self.assertEqual(r["title"], "发布 GPT-6")
        expected = (self.FIX / "longform.expected.md").read_text(encoding="utf-8").strip()
        self.assertEqual(r["markdown"].strip(), expected)

    def test_keeps_headings_links_and_drops_nav_footer(self):
        r = ft.extract_article_markdown(self._read("blog.html"), "https://vendor.example/b")
        md = r["markdown"]
        self.assertEqual(r["reason"], "")
        self.assertIn("## 本周更新", md)
        self.assertIn("[技术报告](https://vendor.example/target)", md)   # 相对链接绝对化
        self.assertNotIn("版权", md)
        self.assertNotIn("Docs", md)

    def test_list_items_grouped_and_code_and_image(self):
        r = ft.extract_article_markdown(self._read("longform.html"), "https://vendor.example/p")
        md = r["markdown"]
        self.assertIn("- 通过 API 立即开放\n- 面向企业版提供更高吞吐", md)   # 同组单块
        self.assertIn("```\nresp =", md)
        self.assertIn("![示意图](https://vendor.example/img/a.png)", md)

    def test_selfhosted_section_main(self):
        r = ft.extract_article_markdown(self._read("selfhosted.html"), "https://vendor.example/r")
        self.assertEqual(r["reason"], "")
        self.assertEqual(r["title"], "稀疏注意力实测")
        self.assertGreater(len(r["markdown"]), 200)

    def test_spa_shell_reports_scaffold_no_body(self):
        r = ft.extract_article_markdown(self._read("spa_shell.html"), "https://vendor.example/app")
        self.assertEqual(r["reason"], "scaffold")
        self.assertEqual(r["markdown"], "")

    def test_blocked_html_reports_blocked(self):
        html = "<html><body>We noticed something unusual. You have been blocked.</body></html>"
        self.assertEqual(ft.extract_article_markdown(html, "https://x/y")["reason"], "blocked")

    def test_status_for_reason_mapping(self):
        self.assertEqual(ft.status_for_reason(""), "ok")
        self.assertEqual(ft.status_for_reason("paywall"), "paywall")
        self.assertEqual(ft.status_for_reason("scaffold"), "fetch_failed")
        self.assertEqual(ft.status_for_reason("blocked"), "fetch_failed")
        self.assertEqual(ft.status_for_reason("empty"), "fetch_failed")

    def test_table_rendered_as_markdown_pipe(self):
        body = ("<article><p>" + "正文内容很丰富。" * 40 + "</p>"
                "<table><tr><th>模型</th><th>VQA</th></tr>"
                "<tr><td>jina-vlm</td><td>72.3</td></tr></table></article>")
        md = ft.extract_article_markdown("<html><body>" + body + "</body></html>",
                                         "https://x/y")["markdown"]
        self.assertIn("| 模型 | VQA |", md)
        self.assertIn("| --- | --- |", md)
        self.assertIn("| jina-vlm | 72.3 |", md)


class TestFulltextLang(unittest.TestCase):
    """源语言判定与「中文原生页不进 .en.md」的重分类。"""

    ZH_HTML = ("<article><h1>通义千问发布新版</h1><p>" + "这是一段中文正文内容。" * 40
               + "</p></article>")
    EN_HTML = ("<article><h1>New Release</h1><p>" + "This is English body text. " * 40
               + "</p></article>")

    def test_captured_stays_put_when_the_body_did_not_change(self):
        """正文逐字没变就**别动 `captured`**。

        回归：`captured` 记的是「这篇正文是哪天抓到的」。重抓一遍拿到相同内容却把
        日期改成今天，信息量是零，却让每次 `--retry-unreadable` 都产出一批只差一行的
        无意义改动（实测 moonshot / siliconflow / streamlake 三家 62 个文件只动了这个
        字段），把真改动淹没在噪声里。空正文的墓碑文件尤其如此。
        """
        rows = [{"vendor": "aliyun_qwen", "url": "https://x/p", "title": "T", "date": "",
                 "original_title": "T"}]
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bodies = {}
            # 第一轮：抓出正文，captured 落在当天
            ft.fetch_bodies(root, rows, bodies, fetch=lambda u: (self.EN_HTML, True, 200, u),
                            today="2026-10-01")
            e = bodies[ft.bodies_key("aliyun_qwen", "https://x/p")]
            self.assertEqual(e["captured"], "2026-10-01")
            body_sha = e["body_sha"]

            # 第二轮：同样的内容、换了「今天」，captured 不许跟着跳
            ft.fetch_bodies(root, rows, bodies, fetch=lambda u: (self.EN_HTML, True, 200, u),
                            today="2026-10-10", only_missing=False)
            e2 = bodies[ft.bodies_key("aliyun_qwen", "https://x/p")]
            self.assertEqual(e2["captured"], "2026-10-01", "内容没变却改了 captured")
            self.assertEqual(e2["body_sha"], body_sha)
            fm, _ = ft.read_body_doc(root / e2["en_path"])
            self.assertEqual(fm.get("captured"), "2026-10-01", "frontmatter 也要一致")

            # 第三轮：正文真的变了，captured 才更新
            changed = ("<article><h1>New Release</h1><p>" + "Body text changed here. " * 40
                       + "</p></article>")
            ft.fetch_bodies(root, rows, bodies, fetch=lambda u: (changed, True, 200, u),
                            today="2026-10-10", only_missing=False)
            self.assertEqual(bodies[ft.bodies_key("aliyun_qwen", "https://x/p")]["captured"],
                             "2026-10-10", "内容变了，captured 必须更新")

    def test_detect_source_lang(self):
        self.assertEqual(ft.detect_source_lang(
            ft.extract_article_markdown(self.ZH_HTML, "https://x/p")["markdown"]), "zh")
        self.assertEqual(ft.detect_source_lang(
            ft.extract_article_markdown(self.EN_HTML, "https://x/p")["markdown"]), "en")

    def test_fetch_chinese_native_goes_to_zh_not_en(self):
        with tempfile.TemporaryDirectory() as d:
            rows = [{"vendor": "aliyun_qwen", "url": "https://x/p", "title": "T", "date": "",
                     "original_title": "T"}]
            bodies = {}

            def fetch(u):
                return (self.ZH_HTML, True, 200, "https://x/p")
            ft.fetch_bodies(Path(d), rows, bodies, fetch=fetch, today="2026-10-05")
            e = bodies[ft.bodies_key("aliyun_qwen", "https://x/p")]
            self.assertEqual(e["src_lang"], "zh")
            self.assertEqual(e["zh_status"], "translated")
            self.assertEqual(e["translator"], "native")
            self.assertEqual(e["en_status"], "")
            self.assertTrue((Path(d) / e["zh_path"]).exists())
            self.assertFalse((Path(d) / "docs/articles/aliyun_qwen" / (e["slug"] + ".en.md")).exists())
            self.assertEqual(ft.pending_translation_keys(bodies), [])

    def test_chinese_changelog_slice_inherits_the_pages_language(self):
        """单页变更日志的一条正文以整页语言为准，别让模型名把中文切片判成英文源。

        Gemini 那条弃用公告整段都是 `deep-research-pro-preview-12-2025` 这类模型名：
        778 字里 425 个拉丁字符、CJK 只占 18%，单看切片过不了 0.4 的中文阈值。若照旧判成
        英文源，已经是中文的正文会被存成 `.en.md` 并排进待译队列，让 CI 再机翻一遍。
        """
        page = ("# 版本说明\n\n本页面记录了 Gemini API 的更新。\n\n"
                "## 2026 年 10 月 8 日\n\n"
                "- **Gemini 3.7 Flash 弃用**：`gemini-3.7-flash` 已弃用并由 "
                "`gemini-3.8-flash` 取代，所有请求会自动路由到新模型上，无需改动。\n\n"
                "- **Deep Research 智能体 `deep-research-pro-preview-12-2025` 弃用**："
                "`deep-research-pro-preview-12-2025` 智能体已弃用，并将于 **2026 年 10 月 23 日**"
                "关停。请将 `interactions.create` 请求中的 `agent` 参数从 "
                "`deep-research-pro-preview-12-2025` 迁移到 `deep-research-preview-04-2026`，"
                "或迁移到 `deep-research-max-preview-04-2026` 以获得最大全面性。\n\n"
                "## 2026 年 10 月 6 日\n\n"
                "- **Gemini Nano Banana 2.1 正式版 (GA)**：发布了最新的高效率图片生成和"
                "对话式智能修图模型，可用于生产环境。该版本在主体一致性上有明显提升，"
                "并支持更高的分辨率输出与更自然的指令跟随能力。\n\n"
                "- **弃用公告**：`gemini-3.1-flash-image` 已被弃用，迁移到 "
                "`gemini-nano-banana-2.1`。请注意在迁移后调整请求中的模型名称。\n")
        cut = ft._slice_anchor_section(
            page, "10-08-2026-2", "Deep Research 智能体 `deep-research-pro-preview-12-2025` 弃用",
            ["Gemini 3.7 Flash 弃用"], "2026-10-08")
        self.assertIn("关停", cut)
        self.assertEqual(ft.detect_source_lang(page), "zh")
        self.assertNotEqual(ft.detect_source_lang(cut), "zh",
                            "这条切片单看确实判不出中文（回归的前提，别把测试改松了）")
        with tempfile.TemporaryDirectory() as d:
            rows = [{"vendor": "google_gemini",
                     "url": "https://ai.google.dev/gemini-api/docs/changelog?hl=zh-cn#10-08-2026-2",
                     "title": "Deep Research 智能体 `deep-research-pro-preview-12-2025` 弃用",
                     "date": "2026-10-08", "original_title": ""}]
            bodies = {}
            ft.fetch_bodies(Path(d), rows, bodies,
                            fetch=lambda u: (page, True, 200, u), today="2026-10-10")
            e = bodies[ft.bodies_key("google_gemini", rows[0]["url"])]
            self.assertEqual(e["src_lang"], "zh")
            self.assertEqual(e["translator"], "native")
            self.assertEqual(e["en_status"], "", "中文原生不该留英文侧")
            self.assertEqual(ft.pending_translation_keys(bodies), [], "中文原生不进待译队列")

    def test_reclassify_moves_cached_chinese_out_of_en(self):
        with tempfile.TemporaryDirectory() as d:
            slug = "aaaa0000bbbb"
            (Path(d) / "docs/articles/aliyun_qwen").mkdir(parents=True)
            zh_md = "这是一段中文正文内容。" * 40
            ft.write_body_doc(Path(d) / f"docs/articles/aliyun_qwen/{slug}.en.md",
                              {"vendor": "aliyun_qwen", "url": "https://x/p", "title": "T",
                               "status": "ok"}, zh_md)
            bodies = {f"aliyun_qwen\thttps://x/p": {"slug": slug,
                "en_path": f"docs/articles/aliyun_qwen/{slug}.en.md", "en_status": "ok",
                "zh_path": "", "zh_status": "", "translator": "", "title": "T", "date": "",
                "captured": "", "src_lang": ""}}
            self.assertEqual(ft.reclassify_bodies(Path(d), bodies), 1)
            e = bodies["aliyun_qwen\thttps://x/p"]
            self.assertEqual(e["src_lang"], "zh")
            self.assertEqual(e["zh_status"], "translated")
            self.assertFalse((Path(d) / "docs/articles/aliyun_qwen" / (slug + ".en.md")).exists())
            self.assertTrue((Path(d) / e["zh_path"]).exists())
            self.assertEqual(ft.reclassify_bodies(Path(d), bodies), 0)   # 幂等
            self.assertEqual(ft.validate_bodies(Path(d), bodies), [])

    def test_reclassify_leaves_english(self):
        with tempfile.TemporaryDirectory() as d:
            slug = "cccc1111dddd"
            (Path(d) / "docs/articles/openai").mkdir(parents=True)
            ft.write_body_doc(Path(d) / f"docs/articles/openai/{slug}.en.md",
                              {"vendor": "openai", "url": "https://x/p", "status": "ok"},
                              "English body " * 40)
            bodies = {f"openai\thttps://x/p": {"slug": slug,
                "en_path": f"docs/articles/openai/{slug}.en.md", "en_status": "ok", "src_lang": "",
                "zh_path": "", "zh_status": "", "translator": "", "title": "T", "date": "",
                "captured": ""}}
            self.assertEqual(ft.reclassify_bodies(Path(d), bodies), 1)   # 补 src_lang=en
            self.assertEqual(bodies["openai\thttps://x/p"]["src_lang"], "en")
            self.assertTrue((Path(d) / f"docs/articles/openai/{slug}.en.md").exists())


class TestFulltextIndexPage(unittest.TestCase):
    """链接目录页（blog index）判定 + 抓取时排除，不占待译队列。"""

    INDEX_MD = "\n".join(
        f"- [→ Post title number {i} with a fairly long descriptive sentence about the topic]({{url}}{i})"
        for i in range(30)).replace("{url}", "https://poolside.ai/blog/")
    ARTICLE_MD = ("Some intro paragraph of real prose that carries the argument. " * 6 +
                  " See [a link](https://x/y) inline, then " + "many more words of body text. " * 20)

    def test_detect_index_page(self):
        self.assertTrue(ft.detect_index_page(self.INDEX_MD))

    def test_real_article_not_flagged(self):
        self.assertFalse(ft.detect_index_page(self.ARTICLE_MD))

    def test_short_body_not_flagged(self):
        self.assertFalse(ft.detect_index_page("[a](u) [b](u) [c](u)"))  # < 200 字符

    def test_fetch_marks_index_page_empty_and_unqueued(self):
        with tempfile.TemporaryDirectory() as d:
            rows = [{"vendor": "poolside", "url": "https://x/blog", "title": "T", "date": "",
                     "original_title": "T"}]
            bodies = {}
            html = "<html><body><ul>" + "".join(
                f"<li><a href='https://x/blog/{i}'>Post {i} with a long descriptive sentence here</a></li>"
                for i in range(40)) + "</ul></body></html>"

            def fetch(u):
                return (html, True, 200, "https://x/blog")
            ft.fetch_bodies(Path(d), rows, bodies, fetch=fetch, today="2026-10-05")
            e = bodies[ft.bodies_key("poolside", "https://x/blog")]
            self.assertEqual(e["en_status"], "index_page")
            _fm, body = ft.read_body_doc(Path(d) / e["en_path"])
            self.assertEqual(body.strip(), "")
            self.assertEqual(ft.pending_translation_keys(bodies), [])
            self.assertEqual(ft.validate_bodies(Path(d), bodies), [])


class TestRssDualFeeds(unittest.TestCase):
    """双语 feed 发射（R1b）：中/英各一，guid 用 ?li=1 后缀区分，native 中文源
    在英文 feed 里整体跳过；单厂商源受 RSS_VENDOR_LIMIT 约束。"""

    BASE = "https://example.test/feeds"

    def _intel(self, vid: str, brand: str, n: int, title_prefix: str = "Post") -> crawler_llm_intel.VendorIntel:
        v = crawler_llm_intel.VendorIntel(vendor_id=vid, brand=brand, homepage="", products=[])
        v.all_news_articles = [
            crawler_llm_intel.Article(
                title=f"{title_prefix} {i}",
                url=f"https://{vid}.test/blog/{i}",
                date=f"2026-01-{i:02d}",
            )
            for i in range(1, n + 1)
        ]
        return v

    def _write_bodies(self, feeds_dir: Path, entries: dict) -> None:
        """entries: {(vendor, url, en_status)}；构造 bodies.json + 空 .en.md 文件。"""
        bodies = {}
        for vendor, url, en_status in entries:
            key = ft.bodies_key(vendor, url)
            slug = ft.url_hash(url)
            en_rel = f"docs/articles/{vendor}/{slug}.en.md"
            en_path = feeds_dir.parent / en_rel
            en_path.parent.mkdir(parents=True, exist_ok=True)
            fm = {"vendor": vendor, "title": "x", "url": ft.normalize_url(url),
                  "status": en_status, "lang": "en"}
            ft.write_body_doc(en_path, fm, "body" if en_status == "ok" else "")
            bodies[key] = {"slug": slug, "en_path": en_rel, "en_status": en_status,
                           "zh_path": "", "zh_status": "", "translator": "",
                           "title": "", "date": "", "captured": "",
                           "body_sha": "", "src_lang": "en" if en_status == "ok" else ""}
        ft.save_bodies(feeds_dir / "bodies.json", bodies)

    def test_dual_feed_files_emitted(self):
        with tempfile.TemporaryDirectory() as d:
            feeds = Path(d) / "feeds"
            feeds.mkdir()
            self._write_bodies(feeds, [("openai", "https://openai.test/blog/1", "ok")])
            crawler_llm_intel.write_rss_feeds(feeds, [self._intel("openai", "OpenAI", 3)], self.BASE, lang_table={"openai.test": "en"})
            self.assertTrue((feeds / "llm-news-all.xml").exists())
            self.assertTrue((feeds / "llm-news-all.en.xml").exists())
            self.assertTrue((feeds / "llm-news-openai.xml").exists())
            self.assertTrue((feeds / "llm-news-openai.en.xml").exists())

    def test_english_feed_guid_has_li_suffix(self):
        with tempfile.TemporaryDirectory() as d:
            feeds = Path(d) / "feeds"
            feeds.mkdir()
            url = "https://openai.test/blog/1"
            self._write_bodies(feeds, [("openai", url, "ok")])
            crawler_llm_intel.write_rss_feeds(feeds, [self._intel("openai", "OpenAI", 1)], self.BASE, lang_table={"openai.test": "en"})
            zh = (feeds / "llm-news-openai.xml").read_text(encoding="utf-8")
            en = (feeds / "llm-news-openai.en.xml").read_text(encoding="utf-8")
            # 硬编码 ?li=1 而非引用常量，否则改坏常量测试一起漂——真正的不变量是
            # "中英 guid 必须不同、英文带 query 后缀"
            self.assertIn(f'<guid isPermaLink="true">{url}</guid>', zh)
            self.assertIn(f'<guid isPermaLink="true">{url}?li=1</guid>', en)
            # <link> 两边都保持原 URL，不带后缀
            self.assertIn(f"<link>{url}</link>", en)
            self.assertIn(f"<link>{url}</link>", zh)

    def test_native_chinese_source_skipped_in_en_feed(self):
        """源声明为中文（或未声明）→ 英文镜像里整体不出现。

        千问是中文源：`lang: zh` 写在源上，不靠 `en_status` 或标题里有没有拉丁字母。
        """
        with tempfile.TemporaryDirectory() as d:
            feeds = Path(d) / "feeds"
            feeds.mkdir()
            v = self._intel("aliyun_qwen", "通义千问", 2, title_prefix="通义千问更新")
            # 中文原生标题（无拉丁字母）→ _english_eligible 回退判据也排除
            self._write_bodies(feeds, [
                ("aliyun_qwen", "https://aliyun_qwen.test/blog/1", ""),
                ("aliyun_qwen", "https://aliyun_qwen.test/blog/2", ""),
            ])
            crawler_llm_intel.write_rss_feeds(feeds, [v], self.BASE)
            self.assertTrue((feeds / "llm-news-aliyun_qwen.xml").exists(),
                            "中文 feed 仍要出")
            self.assertFalse((feeds / "llm-news-aliyun_qwen.en.xml").exists(),
                             "该厂商全无英文正文，不出 .en.xml")

    def test_vendor_limit_applied(self):
        """单厂商流截到 RSS_VENDOR_LIMIT 条；合并流截 merged_limit。"""
        with tempfile.TemporaryDirectory() as d:
            feeds = Path(d) / "feeds"
            feeds.mkdir()
            entries = [("v", f"https://v.test/blog/{i}", "ok") for i in range(1, 25)]
            self._write_bodies(feeds, entries)
            crawler_llm_intel.write_rss_feeds(
                feeds, [self._intel("v", "V", 24)], self.BASE,
                merged_limit=100, vendor_limit=10, lang_table={"v.test": "en"})
            zh = (feeds / "llm-news-v.xml").read_text(encoding="utf-8")
            en = (feeds / "llm-news-v.en.xml").read_text(encoding="utf-8")
            self.assertEqual(zh.count("<item>"), 10)
            self.assertEqual(en.count("<item>"), 10)

    def test_english_feed_body_absent_when_fetch_failed(self):
        """源声明是英文 → 条目照进英文镜像；但抓不到正文的那条**不许带正文**。

        改前的判据是「en_status 不是 ok 就不进英文 feed」，可那量的是我们的抓取
        状态、不是源的语言：整页复制被判成 index_page 时，条目会凭空从订阅者的镜像里
        消失。现在镜像成员由源声明决定，正文有没有由语料决定，两件事分开。
        """
        with tempfile.TemporaryDirectory() as d:
            feeds = Path(d) / "feeds"
            feeds.mkdir()
            url_ok = "https://v.test/blog/1"
            url_bad = "https://v.test/blog/2"
            self._write_bodies(feeds, [
                ("v", url_ok, "ok"),
                ("v", url_bad, "fetch_failed"),
            ])
            v = self._intel("v", "V", 2)
            crawler_llm_intel.write_rss_feeds(feeds, [v], self.BASE, lang_table={"v.test": "en"})
            en = (feeds / "llm-news-v.en.xml").read_text(encoding="utf-8")
            zh = (feeds / "llm-news-v.xml").read_text(encoding="utf-8")
            items = {i.split("<link>")[1].split("</link>")[0]: i
                     for i in en.split("<item>")[1:]}
            self.assertIn(url_ok, items)
            self.assertIn(url_bad, items, "英文源的条目不该因我们抓不到就消失")
            self.assertNotIn("<content:encoded>", items[url_bad],
                             "抓不到正文的条目只给标题与链接，不许编一段出来"
                             "（正文注入本身由 test_write_rss_feeds_injects_body 钉）")
            self.assertIn("blog/1", zh)
            self.assertIn("blog/2", zh)


class TestMdHtmlDualRun(unittest.TestCase):
    """md→html 的 Python 与 JS 实现必须产出**同一 tag 序列**（reader 抽屉与 RSS
    `content:encoded` 共用一份内容语义，两份源不能漂移，见 corpus spec §12.4）。

    结构等价而非字节等价：只比 `(tag, text)` 序列；忽略空白与属性顺序差异。
    """

    FIXTURES = [
        ("heading_para", "# Title\n\nHello world.\n"),
        ("bold_code_link", "See [docs](https://x.test/a) with **bold** and `code`.\n"),
        ("image", "![alt](https://x.test/p.png)\n"),
        ("list", "- a\n- b\n"),
        ("olist", "1. one\n2. two\n"),
        ("code", "```python\nprint(1)\n```\n"),
        ("table", "| Model | Score |\n|---|---|\n| A | 1 |\n"),
        ("blockquote", "> quoted\n"),
        ("raw_html_escaped", "Type `<div>` here.\n"),
    ]

    def _js_html(self, md: str) -> str:
        # 从 index.html 抠 <script id="fli-core">，eval 后调 mdToHtml；
        # 用 stdin 传 md 避免 shell 转义。node 不在时退回 skip。
        import subprocess, shutil
        if not shutil.which("node"):
            self.skipTest("node 不在 PATH")
        script = (
            "const fs=require('fs');"
            "const html=fs.readFileSync('docs/index.html','utf8');"
            "const m=html.match(/<script id=\"fli-core\">([\\s\\S]*?)<\\/script>/);"
            "if(!m){console.error('no fli-core');process.exit(2);}"
            "const FLI=new Function(m[1]+'\\n;return FLI;')();"
            "let s='';process.stdin.on('data',d=>s+=d);"
            "process.stdin.on('end',()=>{process.stdout.write(FLI.mdToHtml(s));});"
        )
        r = subprocess.run(["node", "-e", script], input=md.encode("utf-8"),
                           capture_output=True, cwd=str(Path(__file__).resolve().parent))
        if r.returncode != 0:
            self.fail(f"node 报错：{r.stderr.decode('utf-8', errors='replace')}")
        return r.stdout.decode("utf-8")

    @staticmethod
    def _tokens(html: str) -> list:
        """(tag, inner_text) 序列。attr 与空白差异忽略。"""
        import html as h_mod
        out = []
        i = 0
        while i < len(html):
            lt = html.find("<", i)
            if lt < 0:
                break
            gt = html.find(">", lt)
            if gt < 0:
                break
            tag_full = html[lt:gt + 1]
            m = re.match(r"</?\s*([a-zA-Z][a-zA-Z0-9]*)", tag_full)
            if m:
                tag = m.group(1).lower()
                closing = tag_full.startswith("</")
                selfclose = tag_full.endswith("/>") or tag in ("img", "br", "input", "hr")
                if not closing and not selfclose:
                    # 抓 inner text 直到匹配的下一个开/闭标签
                    close = html.find("<", gt + 1)
                    inner = html[gt + 1:close if close >= 0 else len(html)]
                    inner = re.sub(r"<[^>]+>", "", inner).strip()
                    out.append((tag, h_mod.unescape(inner)))
                else:
                    out.append((tag + ("/" if selfclose and not closing else ""), ""))
            i = gt + 1
        return out

    def test_python_and_js_agree(self):
        import crawler_llm_intel as c
        for name, md in self.FIXTURES:
            with self.subTest(name):
                py = c._md_to_html(md)
                js = self._js_html(md)
                self.assertEqual(self._tokens(py), self._tokens(js),
                                 f"Python/JS tag sequence 不一致\npy={py!r}\njs={js!r}")


class TestIndexHasSlug(unittest.TestCase):
    """articles.json 每行末尾加 slug（reader 抽屉拼 md 路径的数据前置，见 corpus spec §12）。

    守卫的是：字段名列表含 slug、readable 与 langs；每行 row[5] == fulltext.url_hash(row[1])；
    row[6]/row[7] 各只取自己的那组值（且同源于一次磁盘探测）。
    变异：把 crawler 里 url_hash 换成硬编码 "deadbeef0000"、删掉某一列，或让
    readable 与 langs 走两次不同的探测，本类断言变红。
    """

    def _intel(self, n=3):
        v = crawler_llm_intel.VendorIntel(vendor_id="v", brand="V", homepage="", products=[])
        v.all_news_articles = [
            crawler_llm_intel.Article(
                title=f"post {i}", url=f"https://v.test/blog/{i}", date=f"2026-01-{i:02d}")
            for i in range(1, n + 1)
        ]
        return v

    def test_articles_json_has_slug_column(self):
        with tempfile.TemporaryDirectory() as d:
            feeds = Path(d) / "feeds"
            crawler_llm_intel.write_rss_feeds(feeds, [self._intel(3)], "")
            data = json.loads((feeds / "articles.json").read_text(encoding="utf-8"))
            self.assertEqual(
                data["fields"],
                ["title", "url", "vendor", "date", "original_title", "slug",
                 "readable", "langs", "link"])
            for row in data["articles"]:
                self.assertEqual(len(row), 9)
                # row[1]=url, row[5]=slug；slug 由 fulltext.url_hash 决定
                self.assertEqual(row[5], ft.url_hash(row[1]),
                                 "slug 必须等于 fulltext.url_hash(url)，与 bodies.json 里的 slug 一致")
                self.assertRegex(row[5], r"^[0-9a-f]{12}$")
                # row[6]=readable 三态：磁盘有正文 '1' / 已判定抓不到 '0' / 还没轮到 ''
                self.assertIn(row[6], ("", "0", "1"),
                              "readable 只允许三态，页面按位置取这一列决定「读全文」按钮")
                # row[7]=langs：盘上有哪门语言的正文。'' = 建索引时还没有（正文晚索引
                # 一步落盘），页面据此退回网络探测，不许据此禁用页签。
                self.assertIn(row[7], ("", "zh", "en", "both"),
                              "langs 只允许这四值，页面按 langFlags 认这三种 + ''")
                self.assertEqual(row[6] == "1", row[7] != "",
                                 "readable 与 langs 必须同源于一次磁盘探测：'1'  ⟺ 至少一门有正文")

    def test_slug_survives_prev_index_without_slug(self):
        """上一版 articles.json 是 5 字段（无 slug），load_original_titles 只按
        字段名读 original_title，不受列数变化的影响。"""
        with tempfile.TemporaryDirectory() as d:
            feeds = Path(d) / "feeds"
            feeds.mkdir(parents=True)
            (feeds / "articles.json").write_text(json.dumps({
                "fields": ["title", "url", "vendor", "date", "original_title"],
                "count": 1,
                "articles": [["中文标题", "https://a.test/x", "v", "2026-01-01",
                              "English Headline"]],
            }, ensure_ascii=False), encoding="utf-8")
            out = crawler_llm_intel.load_original_titles(feeds / "articles.json")
            self.assertEqual(out[("v", "https://a.test/x")], "English Headline")


class TestRssSizeCapDegrade(unittest.TestCase):
    """R3：合并流产物超 RSS_SOFT_CAP 自动降级为首段摘要 + 回源链接。"""

    def test_summarize_short_passthrough(self):
        html = "<p>short</p>"
        self.assertEqual(crawler_llm_intel._summarize_html(html, "https://x.test/a"), html)

    def test_summarize_truncates_and_adds_link(self):
        html = "<p>" + ("x" * 800) + "</p>"
        out = crawler_llm_intel._summarize_html(html, "https://x.test/a", limit=200)
        self.assertLess(len(out), 400)
        self.assertIn("<a href=\"https://x.test/a\">", out)
        self.assertIn("阅读完整文章", out)

    def test_summarize_does_not_split_open_tag(self):
        # 截半路 <a href="... 未闭合 → 尾段丢弃
        html = "<p>hi</p><a href=\"https://x.test/a\">link</a>"
        out = crawler_llm_intel._summarize_html(html, "https://x.test/a", limit=15)
        # 15 字大概到 `<p>hi</p><a href=` 附近，末尾的半个 `<a href=` 要剥掉
        self.assertFalse(out.rstrip().endswith("<a"))
        self.assertNotIn("<a href=", out.split("<a href=\"https://x.test/a\">阅读完整文章")[0])

    def test_merged_feed_degrades_over_cap(self):
        """注入超大正文，write_rss_feeds 走降级路径：产物含"降级"字样 + 摘要 + 回源链接。"""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            feeds = root / "docs" / "feeds"
            feeds.mkdir(parents=True)
            old_cap = crawler_llm_intel.RSS_SOFT_CAP
            try:
                crawler_llm_intel.RSS_SOFT_CAP = 2000  # 极小阈值触发降级
                bodies = {}
                v = crawler_llm_intel.VendorIntel(vendor_id="v", brand="V",
                                                  homepage="", products=[])
                arts = []
                for i in range(1, 5):
                    url = f"https://v.test/blog/{i}"
                    slug = ft.url_hash(url)
                    rel = f"docs/articles/v/{slug}.md"
                    (root / "docs/articles/v").mkdir(parents=True, exist_ok=True)
                    ft.write_body_doc(root / rel,
                                      {"vendor": "v", "title": f"post {i}",
                                       "url": url, "lang": "zh", "status": "translated"},
                                      "x" * 3000)
                    bodies[ft.bodies_key("v", url)] = {
                        "slug": slug, "en_path": "", "zh_path": rel,
                        "en_status": "", "zh_status": "translated",
                        "translator": "native", "title": "", "date": "",
                        "captured": "", "body_sha": "", "src_lang": "zh"}
                    arts.append(crawler_llm_intel.Article(
                        title=f"post {i}", url=url, date=f"2026-01-0{i}",
                        zh_title=f"文章 {i}"))
                v.all_news_articles = arts
                ft.save_bodies(feeds / "bodies.json", bodies)
                crawler_llm_intel.write_rss_feeds(feeds, [v], "https://x.test/feeds",
                                                  merged_limit=100)
                text = (feeds / "llm-news-all.xml").read_text(encoding="utf-8")
                self.assertIn("正文降级为首段摘要", text)
                self.assertIn("阅读完整文章", text)
                # 4 条 * 3000 字 ≈ 12 KB >> 2 KB 阈值 → 应真的降级
                self.assertLess(len(text.encode("utf-8")), 6000)
            finally:
                crawler_llm_intel.RSS_SOFT_CAP = old_cap

    def _emit_vendor_feed(self, root, feeds, n_articles, body_size, cap):
        """给单厂商 v 造 n_articles 篇、每篇 body_size 字的中文正文，跑 write_rss_feeds，
        返回 (单厂商流文本, 合并流文本)。cap 用于触发/不触发降级。"""
        old_cap = crawler_llm_intel.RSS_SOFT_CAP
        try:
            crawler_llm_intel.RSS_SOFT_CAP = cap
            bodies = {}
            v = crawler_llm_intel.VendorIntel(vendor_id="v", brand="V", homepage="", products=[])
            arts = []
            (root / "docs/articles/v").mkdir(parents=True, exist_ok=True)
            for i in range(1, n_articles + 1):
                url = f"https://v.test/blog/{i}"
                slug = ft.url_hash(url)
                rel = f"docs/articles/v/{slug}.md"
                ft.write_body_doc(root / rel,
                                  {"vendor": "v", "title": f"post {i}", "url": url,
                                   "lang": "zh", "status": "translated"}, "正文" * body_size)
                bodies[ft.bodies_key("v", url)] = {
                    "slug": slug, "en_path": "", "zh_path": rel, "en_status": "",
                    "zh_status": "translated", "translator": "native", "title": "",
                    "date": "", "captured": "", "body_sha": "", "src_lang": "zh"}
                arts.append(crawler_llm_intel.Article(
                    title=f"post {i}", url=url, date=f"2026-01-{i:02d}", zh_title=f"文章 {i}"))
            v.all_news_articles = arts
            ft.save_bodies(feeds / "bodies.json", bodies)
            crawler_llm_intel.write_rss_feeds(feeds, [v], "https://x.test/feeds",
                                              merged_limit=100, vendor_limit=50)
            return ((feeds / "llm-news-v.xml").read_text(encoding="utf-8"),
                    (feeds / "llm-news-all.xml").read_text(encoding="utf-8"))
        finally:
            crawler_llm_intel.RSS_SOFT_CAP = old_cap

    def test_vendor_feed_degrades_over_cap(self):
        """新行为：单厂商流超 RSS_SOFT_CAP 也降级（旧版写死「单厂商不降级」→ 大厂商流长到 MB 订不动）。"""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); feeds = root / "docs" / "feeds"; feeds.mkdir(parents=True)
            vtext, _ = self._emit_vendor_feed(root, feeds, n_articles=20, body_size=800, cap=5000)
            self.assertIn("正文降级为首段摘要", vtext, "超大单厂商流必须降级")
            self.assertIn("阅读完整文章", vtext)

    def test_small_vendor_feed_keeps_full_text(self):
        """反向：小单厂商流不越线 → 保留全文，不降级（全文体验仍在，只是不塞爆合并流）。"""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); feeds = root / "docs" / "feeds"; feeds.mkdir(parents=True)
            vtext, _ = self._emit_vendor_feed(root, feeds, n_articles=2, body_size=10, cap=500000)
            self.assertNotIn("正文降级为首段摘要", vtext)
            self.assertIn("<content:encoded>", vtext, "小流仍带全文 content")


class TestRssContentEncoded(unittest.TestCase):
    """R2：md→html helper + content:encoded 注入。

    - _md_to_html 覆盖 ATX 标题 / 段落 / 有序 / 无序 / 代码栅栏 / 表格 /
      链接 / 图片 / 粗体 / 斜体 / inline code
    - 危险标签 <script>/<iframe>/<style> 一律剥除
    - _rss_cdata 处理内部 `]]>` 拆分
    - write_rss_feeds 从 bodies.json 定位 .md/.en.md → 塞 content:encoded；
      文件缺失或正文为空则不塞该字段
    """

    def test_md_heading_para_list_code(self):
        md = "# Title\n\nHello **world**, meet `code`.\n\n- a\n- b\n\n1. one\n2. two\n\n```\nprint(1)\n```\n"
        html = crawler_llm_intel._md_to_html(md)
        self.assertIn("<h1>Title</h1>", html)
        self.assertIn("<strong>world</strong>", html)
        self.assertIn("<code>code</code>", html)
        self.assertIn("<ul><li>a</li><li>b</li></ul>", html)
        self.assertIn("<ol><li>one</li><li>two</li></ol>", html)
        self.assertIn("<pre><code>print(1)</code></pre>", html)

    def test_md_table(self):
        md = "| Model | Score |\n|---|---|\n| A | 1 |\n| B | 2 |\n"
        html = crawler_llm_intel._md_to_html(md)
        self.assertIn("<thead>", html)
        self.assertIn("<th>Model</th>", html)
        self.assertIn("<td>A</td>", html)
        self.assertEqual(html.count("<tr>"), 3)

    def test_md_link_image(self):
        md = "See [docs](https://x.test/a) and ![alt](https://x.test/p.png).\n"
        html = crawler_llm_intel._md_to_html(md)
        self.assertIn('<a href="https://x.test/a">docs</a>', html)
        self.assertIn('<img src="https://x.test/p.png" alt="alt">', html)

    def test_md_strips_unsafe_tags(self):
        """语料正文里的 <script> 原文要**变成转义文本**（读者看见字面量、浏览器不当标签执行）。"""
        html = crawler_llm_intel._md_to_html("Type `<script>alert(1)</script>` in your config.\n")
        # 关键：不能出现**未转义**的 <script> 标签
        self.assertNotIn("<script>", html)
        # 转义后是字面量，浏览器不会当标签解析——alert(1) 作为文本无害
        self.assertIn("&lt;script&gt;", html)
        # 段落形态直接扔 raw HTML 也一样被 escape
        raw = "before\n\n<script>alert(1)</script>\n\nafter\n"
        out = crawler_llm_intel._md_to_html(raw)
        self.assertNotIn("<script>", out)

    def test_md_escapes_angle_brackets(self):
        # 正文里 "<div>" 不该被当标签解读
        html = crawler_llm_intel._md_to_html("Type `<div>` to open a container.\n")
        self.assertIn("&lt;div&gt;", html)
        self.assertNotIn("<div>", html)

    def test_rss_cdata_splits_embedded_close(self):
        wrapped = crawler_llm_intel._rss_cdata("abc]]>def")
        self.assertTrue(wrapped.startswith("<![CDATA["))
        self.assertTrue(wrapped.endswith("]]>"))
        # 内部 `]]>` 被拆成 `]]` + `]>` 转义
        self.assertIn("]]]]><![CDATA[>", wrapped)
        # 反过来拼接应还原字面量
        self.assertEqual(wrapped.replace("<![CDATA[", "").replace("]]>", "").replace("]]]]>", "]]"), "abc]]>def")

    def test_write_rss_feeds_injects_body(self):
        """给定 corpus 里真实一份 .en.md，write_rss_feeds 把它塞进 content:encoded。

        语料布局：feeds_dir = <root>/docs/feeds，正文 = <root>/docs/articles/<vendor>/<slug>.md。
        _body_html_for 从 entries 的相对路径 + feeds_dir.parent.parent 拼出绝对路径。
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            feeds = root / "docs" / "feeds"
            feeds.mkdir(parents=True)
            url = "https://openai.test/blog/1"
            slug = ft.url_hash(url)
            zh_rel = f"docs/articles/openai/{slug}.md"
            en_rel = f"docs/articles/openai/{slug}.en.md"
            (root / "docs/articles/openai").mkdir(parents=True)
            ft.write_body_doc(root / en_rel,
                              {"vendor": "openai", "title": "Hello", "url": url,
                               "lang": "en", "status": "ok"},
                              "# Hello\n\nBody **world**.\n")
            ft.write_body_doc(root / zh_rel,
                              {"vendor": "openai", "title": "你好", "url": url,
                               "lang": "zh", "status": "translated"},
                              "# 你好\n\n正文 **世界**.\n")
            bodies = {ft.bodies_key("openai", url): {
                "slug": slug, "en_path": en_rel, "zh_path": zh_rel,
                "en_status": "ok", "zh_status": "translated",
                "translator": "agent", "title": "", "date": "", "captured": "",
                "body_sha": "", "src_lang": "en"}}
            ft.save_bodies(feeds / "bodies.json", bodies)
            v = crawler_llm_intel.VendorIntel(vendor_id="openai", brand="OpenAI",
                                              homepage="", products=[])
            v.all_news_articles = [crawler_llm_intel.Article(
                title="Hello", url=url, date="2026-01-01", zh_title="你好")]
            crawler_llm_intel.write_rss_feeds(feeds, [v], "https://x.test/feeds", lang_table={"openai.test": "en", "x.test": "en"})
            zh_xml = (feeds / "llm-news-openai.xml").read_text(encoding="utf-8")
            en_xml = (feeds / "llm-news-openai.en.xml").read_text(encoding="utf-8")
            self.assertIn("<content:encoded>", zh_xml)
            self.assertIn("正文", zh_xml)
            self.assertIn("<strong>世界</strong>", zh_xml)
            self.assertIn("<content:encoded>", en_xml)
            self.assertIn("<strong>world</strong>", en_xml)

    def test_write_rss_feeds_no_content_when_missing_file(self):
        """缺正文文件 → 该 item 不写 content:encoded（不编造、不塞空字段）。"""
        with tempfile.TemporaryDirectory() as d:
            feeds = Path(d) / "feeds"
            feeds.mkdir()
            url = "https://openai.test/blog/gone"
            slug = ft.url_hash(url)
            en_rel = f"docs/articles/openai/{slug}.en.md"
            # ledger 说 en_status=ok 但磁盘没文件
            bodies = {ft.bodies_key("openai", url): {
                "slug": slug, "en_path": en_rel, "zh_path": "",
                "en_status": "ok", "zh_status": "", "translator": "",
                "title": "", "date": "", "captured": "",
                "body_sha": "", "src_lang": "en"}}
            ft.save_bodies(feeds / "bodies.json", bodies)
            v = crawler_llm_intel.VendorIntel(vendor_id="openai", brand="OpenAI",
                                              homepage="", products=[])
            v.all_news_articles = [crawler_llm_intel.Article(
                title="Gone", url=url, date="2026-01-01")]
            crawler_llm_intel.write_rss_feeds(feeds, [v], "https://x.test/feeds")
            zh_xml = (feeds / "llm-news-openai.xml").read_text(encoding="utf-8")
            self.assertNotIn("<content:encoded>", zh_xml)

    def test_rss_root_declares_content_ns(self):
        """xmlns:content 必须在 <rss> 根声明，否则 <content:encoded> 是非法 XML。"""
        with tempfile.TemporaryDirectory() as d:
            feeds = Path(d) / "feeds"
            feeds.mkdir()
            v = crawler_llm_intel.VendorIntel(vendor_id="v", brand="V", homepage="", products=[])
            v.all_news_articles = [crawler_llm_intel.Article(
                title="Hi", url="https://v.test/1", date="2026-01-01")]
            crawler_llm_intel.write_rss_feeds(feeds, [v], "https://x.test/feeds")
            zh = (feeds / "llm-news-v.xml").read_text(encoding="utf-8")
            self.assertIn('xmlns:content="http://purl.org/rss/1.0/modules/content/"', zh)


class TestFulltextLedgerFetch(unittest.TestCase):
    """bodies.json ledger + fetch_bodies（注入 fetch，无网络）+ 翻译队列/mark。"""

    def _stub_fetch(self, mapping, default=("<body>checking your browser</body>", False, 403, "")):
        def fetch(url):
            return mapping.get(ft.normalize_url(url), default)
        return fetch

    def _long_body(self):
        return "<article><h1>T</h1><p>" + "This is substantial English body text. " * 40 + "</p></article>"

    def test_save_bodies_is_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bodies.json"
            b = {"b\thttps://x": {"slug": "2"}, "a\thttps://y": {"slug": "1"}}
            ft.save_bodies(p, b)
            first = p.read_bytes()
            ft.save_bodies(p, dict(reversed(list(b.items()))))
            self.assertEqual(p.read_bytes(), first)

    def test_validate_flags_en_ok_without_file(self):
        with tempfile.TemporaryDirectory() as d:
            b = {"openai\thttps://a/p": {"slug": "deadbeef1234",
                "en_path": "docs/articles/openai/deadbeef1234.en.md", "en_status": "ok"}}
            errs = ft.validate_bodies(Path(d), b)
            self.assertTrue(any("deadbeef1234.en.md" in e for e in errs))

    def test_validate_flags_fetch_failed_with_body(self):
        with tempfile.TemporaryDirectory() as d:
            slug = "aaaa1111bbbb"
            f = Path(d) / "docs/articles/openai"
            f.mkdir(parents=True)
            ft.write_body_doc(f / f"{slug}.en.md",
                              {"vendor": "openai", "status": "fetch_failed", "url": "https://a/p"}, "编造的正文")
            b = {f"openai\thttps://a/p": {"slug": slug, "en_path": f"docs/articles/openai/{slug}.en.md",
                "en_status": "fetch_failed"}}
            self.assertTrue(any("编造" in e or "非空" in e for e in ft.validate_bodies(Path(d), b)))

    def test_refuses_body_already_held_by_another_row(self):
        """不同 URL 抓回同一份内容（首页/空壳回退）→ 第二行不许再存一遍。

        回归：modular.com 三篇博客重抓后都落到「Inference reimagined…」营销首页，
        17,209 字逐字相同，产物侧的 duplicate_body_groups 当场报红。写入侧要有同一句话。
        """
        page = ("<article><h1>Inference reimagined</h1><p>"
                + "One unified stack for AI across GPUs and CPUs. " * 20 + "</p></article>")

        def fetch(u, *a, **kw):
            return (page, True, 200, u)

        rows = [{"vendor": "modular", "url": "https://m.test/blog/a", "title": "A",
                 "date": "", "original_title": "A"},
                {"vendor": "modular", "url": "https://m.test/blog/b", "title": "B",
                 "date": "", "original_title": "B"}]
        with tempfile.TemporaryDirectory() as d:
            bodies = {}
            ft.fetch_bodies(Path(d), rows, bodies, fetch=fetch, today="2026-10-09")
            a = bodies[ft.bodies_key("modular", rows[0]["url"])]
            b = bodies[ft.bodies_key("modular", rows[1]["url"])]
            self.assertEqual(a["en_status"], "ok", "第一行按正常文章收")
            self.assertEqual(b["en_status"], "index_page",
                             "同一份内容已经属于另一条了，这条就没有正文")
            rel = b.get("en_path")
            self.assertFalse(rel and (Path(d) / rel).is_file()
                             and (ft.read_body_doc(Path(d) / rel)[1] or "").strip(),
                             "被拒收的行不许留着非空正文")

    def test_refuses_whole_page_on_shared_changelog_page(self):
        """带 fragment 的条目 + 同页还有其他条目 + 切不出「这一条」→ 记 index_page。

        回归的是重抓那次实测：streamlake 3 行各存了同一份 7,100 字整页，把上一轮的
        清理原地撤销。产物侧的守卫（`duplicate_body_groups`）只能事后报红，写入侧
        必须自己拒收。
        """
        page = ("<article><h1>Release notes</h1><p>"
                + "The changelog page describing everything. " * 30 + "</p></article>")

        def fetch(u, *a, **kw):
            return (page, True, 200, u)

        rows = [{"vendor": "openai", "url": "https://a.test/log#e1", "title": "Entry one",
                 "date": "", "original_title": "Entry one"},
                {"vendor": "openai", "url": "https://a.test/log#e2", "title": "Entry two",
                 "date": "", "original_title": "Entry two"}]
        with tempfile.TemporaryDirectory() as d:
            bodies = {}
            ft.fetch_bodies(Path(d), rows, bodies, fetch=fetch, today="2026-10-09")
            for r in rows:
                e = bodies[ft.bodies_key("openai", r["url"])]
                self.assertEqual(e["en_status"], "index_page",
                                 "切不出「这一条」就不许把整页当正文写下来")
                rel = e.get("en_path")
                if rel:
                    self.assertFalse((Path(d) / rel).is_file()
                                     and (ft.read_body_doc(Path(d) / rel)[1] or "").strip(),
                                     "index_page 的行不许留着非空正文")

        # 反面对照：这一页只有这一个条目时，整页**就是**这一条，照旧收
        with tempfile.TemporaryDirectory() as d:
            bodies = {}
            ft.fetch_bodies(Path(d), rows[:1], bodies, fetch=fetch, today="2026-10-09")
            e = bodies[ft.bodies_key("openai", rows[0]["url"])]
            self.assertEqual(e["en_status"], "ok", "单条页不该被这条规则误伤")
            self.assertTrue((Path(d) / e["en_path"]).is_file())

    def test_fetch_bodies_writes_ok_and_updates_ledger(self):
        with tempfile.TemporaryDirectory() as d:
            rows = [{"vendor": "openai", "url": "https://a.com/p", "title": "T",
                     "date": "2026-01-01", "original_title": "T"}]
            bodies = {}
            n = ft.fetch_bodies(Path(d), rows, bodies,
                                fetch=self._stub_fetch({"https://a.com/p": (self._long_body(), True, 200, "https://a.com/p")}),
                                today="2026-10-05")
            self.assertEqual(n, 1)
            e = bodies[ft.bodies_key("openai", "https://a.com/p")]
            self.assertEqual(e["en_status"], "ok")
            self.assertTrue((Path(d) / e["en_path"]).exists())

    def test_fetch_bodies_records_fetch_failed_no_body(self):
        with tempfile.TemporaryDirectory() as d:
            rows = [{"vendor": "x", "url": "https://spa/app", "title": "T", "date": "", "original_title": "T"}]
            bodies = {}
            ft.fetch_bodies(Path(d), rows, bodies, fetch=self._stub_fetch({}), today="2026-10-05")
            e = bodies[ft.bodies_key("x", "https://spa/app")]
            self.assertEqual(e["en_status"], "fetch_failed")
            _fm, body = ft.read_body_doc(Path(d) / e["en_path"])
            self.assertEqual(body.strip(), "")

    def test_fetch_bodies_only_missing_skips_existing(self):
        with tempfile.TemporaryDirectory() as d:
            rows = [{"vendor": "openai", "url": "https://a.com/p", "title": "T", "date": "", "original_title": "T"}]
            fetch = self._stub_fetch({"https://a.com/p": (self._long_body(), True, 200, "https://a.com/p")})
            bodies = {}
            ft.fetch_bodies(Path(d), rows, bodies, fetch=fetch, today="2026-10-05")
            self.assertEqual(ft.fetch_bodies(Path(d), rows, bodies, fetch=fetch, today="2026-10-06"), 0)

    def test_retry_unreadable_retries_only_judged_unreadable(self):
        """`index_page` 是判定不是事实：只有显式重试才重抓，且有译文的行永远不碰。

        回归的是「标了就永远翻不回来」：CI 每日巡检走 only_missing，标过 index_page
        的行再也不会被看一眼。源站改版、或当初判错，都需要一个比 `--refresh`
        （连好正文一起重抓）窄得多的出口。
        """
        with tempfile.TemporaryDirectory() as d:
            url = "https://a.com/log#entry-2"
            key = ft.bodies_key("openai", url)
            rows = [{"vendor": "openai", "url": url, "title": "T",
                     "date": "", "original_title": "T"}]
            calls = []

            def fetch(u, *a, **kw):
                calls.append(u)
                return (self._long_body(), True, 200, u)

            def judged(status):
                return {key: {"slug": "aaaa1111bbbb", "en_path": "", "en_status": status,
                              "zh_path": "", "zh_status": "", "translator": ""}}

            for status, retriable_by_default in (("index_page", False), ("paywall", True),
                                                 ("fetch_failed", True)):
                calls.clear()
                bodies = judged(status)
                ft.fetch_bodies(Path(d), rows, bodies, fetch=fetch, today="2026-10-05")
                self.assertEqual(calls, [url] * int(retriable_by_default),
                                 "%s 默认%s" % (status, "每天重抓" if retriable_by_default
                                                else "不再被看一眼"))
                calls.clear()
                bodies = judged(status)
                n = ft.fetch_bodies(Path(d), rows, bodies, fetch=fetch, today="2026-10-06",
                                    retry_unreadable=True)
                self.assertEqual(calls, [url], f"{status} 行带 retry_unreadable 应重抓")
                self.assertEqual(n, 1)
            # 已有真实中文译文的行：连重试都不碰（重抓会把精译冲掉）
            calls.clear()
            bodies = judged("index_page")
            bodies[key].update({"zh_status": "translated", "zh_path": "docs/articles/openai/x.md",
                                "translator": "agent"})
            ft.fetch_bodies(Path(d), rows, bodies, fetch=fetch, today="2026-10-07",
                            retry_unreadable=True)
            self.assertEqual(calls, [], "zh=translated 的行不许被重抓冲掉")
            # 已有英文正文的行照旧跳过（重试不是重抓）
            calls.clear()
            bodies = judged("ok")
            ft.fetch_bodies(Path(d), rows, bodies, fetch=fetch, today="2026-10-08",
                            retry_unreadable=True)
            self.assertEqual(calls, [], "en=ok 的行仍应跳过")

    def test_pending_and_mark_translated(self):
        with tempfile.TemporaryDirectory() as d:
            slug = "abcd1234ef56"
            (Path(d) / "docs/articles/openai").mkdir(parents=True)
            ft.write_body_doc(Path(d) / f"docs/articles/openai/{slug}.en.md",
                              {"status": "ok", "url": "https://a/p"}, "English body")
            bodies = {f"openai\thttps://a/p": {"slug": slug, "en_path": f"docs/articles/openai/{slug}.en.md",
                "en_status": "ok", "zh_status": "", "translator": "", "title": "T", "date": "", "captured": ""}}
            self.assertEqual(ft.pending_translation_keys(bodies), ["openai\thttps://a/p"])
            ft.mark_translated(Path(d), bodies, key="openai\thttps://a/p",
                               zh_body_md="中文正文。", translator="agent", today="2026-10-05")
            e = bodies["openai\thttps://a/p"]
            self.assertEqual(e["zh_status"], "translated")
            self.assertEqual(e["translator"], "agent")
            fm, body = ft.read_body_doc(Path(d) / e["zh_path"])
            self.assertEqual(fm["translator"], "agent")
            self.assertEqual(body, "中文正文。")
            self.assertEqual(ft.pending_translation_keys(bodies), [])

    def test_reconcile_absorbs_on_disk_translations(self):
        # 子代理只写 .md、控制者单点 reconcile：磁盘有非空译文即标 translated
        with tempfile.TemporaryDirectory() as d:
            slug = "eeee2222ffff"
            (Path(d) / "docs/articles/groq").mkdir(parents=True)
            ft.write_body_doc(Path(d) / f"docs/articles/groq/{slug}.en.md",
                              {"status": "ok", "url": "https://g/x"}, "English")
            ft.write_body_doc(Path(d) / f"docs/articles/groq/{slug}.md",
                              {"lang": "zh", "translator": "agent", "status": "translated"}, "中文译文。")
            bodies = {f"groq\thttps://g/x": {"slug": slug,
                "en_path": f"docs/articles/groq/{slug}.en.md", "en_status": "ok",
                "zh_path": "", "zh_status": "", "translator": "", "title": "T", "date": "", "captured": ""}}
            self.assertEqual(ft.reconcile_translations(Path(d), bodies), 1)
            e = bodies["groq\thttps://g/x"]
            self.assertEqual(e["zh_status"], "translated")
            self.assertEqual(e["translator"], "agent")
            self.assertEqual(ft.reconcile_translations(Path(d), bodies), 0)  # 幂等

    def test_iter_article_rows(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "articles.json"
            p.write_text(json.dumps({"fields": ["title", "url", "vendor", "date", "original_title"],
                "articles": [["T", "https://a/p", "openai", "2026-01-01", "T"]]}), encoding="utf-8")
            rows = ft.iter_article_rows(p)
            self.assertEqual(rows, [{"vendor": "openai", "url": "https://a/p", "title": "T",
                                     "date": "2026-01-01", "original_title": "T"}])


class TestTranslateBodiesLlm(unittest.TestCase):
    """--ai-bodies 核心：pending 英文正文 → LLM 中文 → .md（translator=llm），不产半成品。"""

    def _seed(self, d, slug, en_body, *, zh_status="", translator="", vendor="openai"):
        (Path(d) / f"docs/articles/{vendor}").mkdir(parents=True, exist_ok=True)
        en_rel = f"docs/articles/{vendor}/{slug}.en.md"
        ft.write_body_doc(Path(d) / en_rel, {"status": "ok", "url": "https://a/p",
                                             "title": "Eng Title"}, en_body)
        key = f"{vendor}\thttps://a/p"
        bodies = {key: {"slug": slug, "en_path": en_rel, "en_status": "ok",
                        "zh_path": "", "zh_status": zh_status, "translator": translator,
                        "title": "中文标题", "date": "", "captured": ""}}
        return key, bodies

    def test_happy_path_writes_llm_translation(self):
        with tempfile.TemporaryDirectory() as d:
            key, bodies = self._seed(d, "aaaa00001111", "English article body here.")
            n = ft.translate_bodies_llm(Path(d), bodies,
                                        lambda t, b: "这是一篇中文正文的翻译内容。",
                                        today="2026-10-06")
            self.assertEqual(n, 1)
            e = bodies[key]
            self.assertEqual(e["zh_status"], "translated")
            self.assertEqual(e["translator"], "llm")
            fm, zh = ft.read_body_doc(Path(d) / e["zh_path"])
            self.assertEqual(fm["translator"], "llm")
            self.assertEqual(fm["lang"], "zh")
            self.assertEqual(zh, "这是一篇中文正文的翻译内容。")
            self.assertEqual(ft.pending_translation_keys(bodies), [])

    def test_idempotent_skips_already_translated(self):
        with tempfile.TemporaryDirectory() as d:
            _key, bodies = self._seed(d, "bbbb00002222", "English body.",
                                      zh_status="translated", translator="agent")
            calls = []
            n = ft.translate_bodies_llm(Path(d), bodies,
                                        lambda t, b: calls.append(1) or "中文",
                                        today="2026-10-06")
            self.assertEqual(n, 0)
            self.assertEqual(calls, [], "已 translated 的绝不重译（幂等）")

    def test_over_char_cap_left_pending(self):
        with tempfile.TemporaryDirectory() as d:
            key, bodies = self._seed(d, "cccc00003333", "x" * 500)
            calls = []
            n = ft.translate_bodies_llm(Path(d), bodies,
                                        lambda t, b: calls.append(1) or "中文翻译内容",
                                        today="2026-10-06", char_cap=200)
            self.assertEqual(n, 0)
            self.assertEqual(calls, [], "超长篇不送翻译，避免截断产半成品")
            self.assertEqual(bodies[key]["zh_status"], "")
            self.assertEqual(ft.pending_translation_keys(bodies), [key])

    def test_refusal_output_not_written(self):
        with tempfile.TemporaryDirectory() as d:
            key, bodies = self._seed(d, "dddd00004444", "English body.")
            # 模型吐回英文（没翻）→ 校验不过 → 留 pending、不写 .md
            n = ft.translate_bodies_llm(Path(d), bodies,
                                        lambda t, b: "English body.", today="2026-10-06")
            self.assertEqual(n, 0)
            self.assertEqual(bodies[key]["zh_status"], "")
            self.assertFalse((Path(d) / f"docs/articles/openai/{'dddd00004444'}.md").exists())

    def test_exception_leaves_pending(self):
        with tempfile.TemporaryDirectory() as d:
            key, bodies = self._seed(d, "eeee00005555", "English body.")

            def boom(t, b):
                raise RuntimeError("quota exhausted")
            n = ft.translate_bodies_llm(Path(d), bodies, boom, today="2026-10-06")
            self.assertEqual(n, 0)
            self.assertEqual(ft.pending_translation_keys(bodies), [key],
                             "调用异常留 pending，下次再试，不崩整批")

    def test_strips_fence_and_label(self):
        with tempfile.TemporaryDirectory() as d:
            key, bodies = self._seed(d, "ffff00006666", "English body.")
            ft.translate_bodies_llm(Path(d), bodies,
                                    lambda t, b: "```markdown\n译文：这是一段中文正文。\n```",
                                    today="2026-10-06")
            _fm, zh = ft.read_body_doc(Path(d) / bodies[key]["zh_path"])
            self.assertEqual(zh, "这是一段中文正文。")

    def test_limit_caps_batch(self):
        with tempfile.TemporaryDirectory() as d:
            bodies = {}
            for i in range(5):
                slug = f"l{i:011d}"
                (Path(d) / "docs/articles/openai").mkdir(parents=True, exist_ok=True)
                rel = f"docs/articles/openai/{slug}.en.md"
                ft.write_body_doc(Path(d) / rel, {"status": "ok", "url": f"https://a/{i}"}, "body")
                bodies[f"openai\thttps://a/{i}"] = {"slug": slug, "en_path": rel,
                    "en_status": "ok", "zh_status": "", "translator": "", "title": "T",
                    "date": "", "captured": ""}
            n = ft.translate_bodies_llm(Path(d), bodies,
                                        lambda t, b: "这是一段中文正文内容。",
                                        today="2026-10-06", limit=2)
            self.assertEqual(n, 2, "limit 封顶本次译量，控 CI 成本")

    def test_incremental_flush(self):
        with tempfile.TemporaryDirectory() as d:
            bodies = {}
            (Path(d) / "docs/articles/openai").mkdir(parents=True)
            for i in range(3):
                slug = f"f{i:011d}"
                rel = f"docs/articles/openai/{slug}.en.md"
                ft.write_body_doc(Path(d) / rel, {"status": "ok", "url": f"https://a/{i}"}, "body")
                bodies[f"openai\thttps://a/{i}"] = {"slug": slug, "en_path": rel,
                    "en_status": "ok", "zh_status": "", "translator": "", "title": "T",
                    "date": "", "captured": ""}
            saves = []
            ft.translate_bodies_llm(Path(d), bodies, lambda t, b: "中文翻译的正文内容。",
                                    today="2026-10-06", save=lambda b: saves.append(len(b)),
                                    flush_every=1)
            self.assertEqual(len(saves), 3, "每译一篇即落一次 ledger，中断也保住已完成项")

    def test_limit_caps_calls_not_scan(self):
        """limit 封的是「实际调用次数」：超长项不占预算，排在长文后面的短文照样轮到。

        回归：旧实现先 keys[:limit] 再过滤，若前 limit 条恰好都超长，则本轮译 0，
        短文永远排在长文后面饿死。这里把 3 篇超长排在 3 篇短文前面，limit=2 →
        应译成 2（短文）、over_cap=3、deferred=1，而不是被超长项吃光预算译 0。
        """
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "docs/articles/openai").mkdir(parents=True)
            bodies = {}
            ordered = [("cap_a", "y" * 300), ("cap_b", "y" * 300), ("cap_c", "y" * 300),
                       ("short_a", "short english"), ("short_b", "short english"),
                       ("short_c", "short english")]
            for slug, eb in ordered:
                rel = f"docs/articles/openai/{slug}.en.md"
                ft.write_body_doc(Path(d) / rel, {"status": "ok", "url": f"https://a/{slug}"}, eb)
                bodies[f"openai\thttps://a/{slug}"] = {"slug": slug, "en_path": rel,
                    "en_status": "ok", "zh_status": "", "translator": "", "title": slug,
                    "date": "", "captured": ""}
            stats = {}
            n = ft.translate_bodies_llm(Path(d), bodies,
                                        lambda t, b: "这是一段合格的中文正文翻译。",
                                        today="2026-10-06", limit=2, char_cap=100, stats=stats)
            self.assertEqual(n, 2)
            self.assertEqual(stats["over_cap"], 3)
            self.assertEqual(stats["deferred"], 1)
            self.assertEqual(stats["translated"], 2)

    def test_stats_categorizes_every_skip(self):
        """stats 把每篇归类摊开——专治「批量译了 0 篇却看不出为什么」。"""
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "docs/articles/openai").mkdir(parents=True)
            b2 = {}
            # 四篇各走一条出口：正常译 / 超长 / 调用抛错 / 输出校验不过
            for slug, eb in [("t_ok", "normal english prose"),
                             ("t_cap", "x" * 300),
                             ("t_err", "boom body"),
                             ("t_rej", "english echo")]:
                rel = f"docs/articles/openai/{slug}.en.md"
                ft.write_body_doc(Path(d) / rel, {"status": "ok", "url": f"https://a/{slug}"}, eb)
                b2[f"openai\thttps://a/{slug}"] = {"slug": slug, "en_path": rel,
                    "en_status": "ok", "zh_status": "", "translator": "", "title": slug,
                    "date": "", "captured": ""}
            def translate2(title, en_body):
                if en_body == "boom body":
                    raise RuntimeError("HTTP 400 maxOutputTokens exceeded")
                if en_body == "english echo":
                    return "english echo"               # 原样吐回 = 没翻，校验不过
                return "这是一段合格的中文正文翻译。"
            stats = {}
            ft.translate_bodies_llm(Path(d), b2, translate2, today="2026-10-06",
                                    char_cap=100, stats=stats)
            self.assertEqual(stats["translated"], 1)
            self.assertEqual(stats["over_cap"], 1)
            self.assertEqual(stats["errored"], 1)
            self.assertEqual(stats["rejected"], 1)
            self.assertTrue(stats["errors"] and "400" in stats["errors"][0],
                            "异常样本要带出来，否则又是静默 0")


class TestFulltextCiInvariants(unittest.TestCase):
    """corpus spec §6 四条 CI 活守卫：增量有界 / requests-only / 非覆盖 / 防编造。

    每条都在临时根里跑真实函数（注入 fetch，无网络），并配一次「故意破坏证明会咬」
    （见提交说明）——这是每日 CI 抓正文/译正文不失控、不吞语料、不编正文的底线。
    """

    def _long_body(self):
        return "<article><h1>T</h1><p>" + "Substantial English body prose. " * 40 + "</p></article>"

    # -- 守卫 1：增量有界 --------------------------------------------------
    def test_only_missing_makes_no_fetch_for_done_entries(self):
        """已 ok 的条目在 only_missing 下必须一次网络都不发（否则 CI 时长/成本失控）。"""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            slug = "bound0000001"
            (root / "docs/articles/openai").mkdir(parents=True)
            en_rel = f"docs/articles/openai/{slug}.en.md"
            ft.write_body_doc(root / en_rel, {"status": "ok", "url": "https://a/1"}, "已有英文正文")
            bodies = {ft.bodies_key("openai", "https://a/1"): {
                "slug": slug, "en_path": en_rel, "en_status": "ok", "zh_status": "translated"}}
            rows = [{"vendor": "openai", "url": "https://a/1", "title": "T", "date": "", "original_title": "T"}]
            calls = []
            def fetch(url):
                calls.append(url)
                return (self._long_body(), True, 200, url)
            n = ft.fetch_bodies(root, rows, bodies, fetch=fetch, today="2026-10-06",
                                only_missing=True)
            self.assertEqual(n, 0)
            self.assertEqual(calls, [], "增量有界：已 ok 且未变条目不得重抓")

    # -- 守卫 2：requests-only，SPA 不崩不编 ------------------------------
    def test_spa_page_without_browser_yields_empty_failed(self):
        """无浏览器环境抓到反爬/SPA 空壳 → fetch_failed、正文留空、绝不抛异常。"""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rows = [{"vendor": "x", "url": "https://spa/app", "title": "T", "date": "", "original_title": "T"}]
            bodies = {}
            blocked = ("<html><title>Just a moment</title><body>Checking your browser"
                       " before you access</body></html>")
            n = ft.fetch_bodies(root, rows, bodies,
                                fetch=lambda u: (blocked, False, 403, u), today="2026-10-06")
            e = bodies[ft.bodies_key("x", "https://spa/app")]
            self.assertEqual(e["en_status"], "fetch_failed")
            _fm, body = ft.read_body_doc(root / e["en_path"])
            self.assertEqual(body.strip(), "", "抓不到就留空，绝不把空壳/JS 壳当正文")
            self.assertEqual(ft.validate_bodies(root, bodies), [])

    # -- 守卫 3：非覆盖，清理不碰语料 --------------------------------------
    def test_archive_cleanup_does_not_touch_corpus(self):
        """write_news_archives 的 clean_removed 只清 llm-news/*.md，不得碰 docs/articles/**。"""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            news_dir = root / "llm-news"
            news_dir.mkdir()
            (news_dir / "gone_vendor.md").write_text("# 旧归档\n", encoding="utf-8")
            # 语料层：与 llm-news 完全不同的目录，清理逻辑不该越界删它
            art = root / "docs/articles/openai"
            art.mkdir(parents=True)
            (art / "keep.md").write_text("正文语料", encoding="utf-8")
            (art / "keep.en.md").write_text("corpus", encoding="utf-8")
            ledger = root / "docs/feeds"
            ledger.mkdir(parents=True)
            ft.save_bodies(ledger / "bodies.json", {"openai\thttps://a/1": {"slug": "keep"}})
            crawler_llm_intel.write_news_archives(news_dir, [], clean_removed=True)
            self.assertFalse((news_dir / "gone_vendor.md").exists(), "下线厂商归档应被清掉")
            self.assertTrue((art / "keep.md").exists(), "非覆盖：清理不得删 docs/articles/**")
            self.assertTrue((art / "keep.en.md").exists())
            self.assertEqual(list(ft.load_bodies(ledger / "bodies.json").keys()),
                             ["openai\thttps://a/1"], "非覆盖：清理不得清空 bodies.json")

    # -- 守卫 4：防编造，失败项正文必空 ------------------------------------
    def test_failed_rows_never_carry_body(self):
        """抓到内容但 fetch 判为失败（ok=False）时，正文文件必须留空——不得把
        半页 / 未确认来源的抽取结果当正文冻进语料（这才是「不编」真正要挡的）。"""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rows = [
                {"vendor": "v", "url": "https://v/ok", "title": "T", "date": "", "original_title": "T"},
                {"vendor": "v", "url": "https://v/softfail", "title": "T", "date": "", "original_title": "T"},
            ]
            bodies = {}
            def fetch(u):
                # 两页都能抽出正文，但 softfail 那页 HTTP 层判失败（5xx / 软封锁）
                if u.endswith("/ok"):
                    return (self._long_body(), True, 200, u)
                return (self._long_body(), False, 500, u)
            ft.fetch_bodies(root, rows, bodies, fetch=fetch, today="2026-10-06")
            bad = [k for k, e in bodies.items()
                   if e.get("en_status") in ("fetch_failed", "paywall", "index_page")]
            self.assertTrue(bad, "夹具应含失败项")
            for k in bad:
                _fm, body = ft.read_body_doc(root / bodies[k]["en_path"])
                self.assertEqual(body.strip(), "", f"防编造：{k} 状态 {bodies[k]['en_status']} 却带正文")


    # -- 守卫 5（CI 实产物兜底）：已提交语料整体过 schema ------------------
    def test_committed_corpus_passes_schema(self):
        """真实 docs/feeds/bodies.json + docs/articles/** 必须过 validate_bodies。

        这是 §6 四条在 CI 里的落点：fetch-bodies / ai-bodies 步骤排在 Verify 之前，
        它们写坏任何一个 .md 或 ledger（缺文件、失败项带正文、translated 无译文）
        都会在这里被拦下、挡住当天提交——把「fixture 级守卫」升级成「对真实产物生效」。
        """
        repo = Path(crawler_llm_intel.__file__).resolve().parent
        ledger = repo / "docs/feeds/bodies.json"
        if not ledger.exists():          # 精简检出 / fork 无语料时不硬失败
            self.skipTest("仓库无 bodies.json，跳过实产物校验")
        bodies = ft.load_bodies(ledger)
        errs = ft.validate_bodies(repo, bodies)
        self.assertEqual(errs, [], f"已提交语料违反 §3.4/§6 schema：{errs[:5]}")


class TestTranslateBodyMt(unittest.TestCase):
    """正文机器翻译：按块处理、代码块原样保留、失败块留原文、结构不塌。"""

    def _patch_gtx(self, fn):
        patcher = mock.patch.object(provider_profiles, "_gtx_translate", fn)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_code_block_preserved_verbatim(self):
        self._patch_gtx(lambda t, timeout=8.0: "【" + t + "】")
        md = "Intro para.\n\n```python\nprint('keep')  # 别译\n```\n\nTail para."
        out = provider_profiles.translate_body_to_zh(md)
        self.assertIn("print('keep')  # 别译", out)
        self.assertNotIn("【print", out, "代码块内容不得被翻译")
        self.assertIn("【Intro para.", out, "散文块应被送去翻译")

    def test_failed_chunk_keeps_original(self):
        # 两块散文被中间的代码块分开 → 各自独立成块；gtx 只对含 B 的块失败 → 该块留原文
        def gtx(t, timeout=8.0):
            return None if "Bad B" in t else "中" + t
        self._patch_gtx(gtx)
        out = provider_profiles.translate_body_to_zh("Good A here\n\n```\ncode\n```\n\nBad B here")
        self.assertIn("中Good A here", out, "成功块被翻译")
        self.assertIn("Bad B here", out, "失败块留原文，绝不吞")
        self.assertNotIn("中Bad B", out)
        self.assertIn("```\ncode\n```", out, "中间代码块原样")

    def test_blank_lines_between_blocks_not_collapsed(self):
        self._patch_gtx(lambda t, timeout=8.0: "T:" + t)
        md = "para one\n\n```\ncode\n```\n\npara two"
        out = provider_profiles.translate_body_to_zh(md)
        self.assertIn("```\ncode\n```", out, "代码块前后空行/围栏不能被吞掉")

    def test_empty_input_passthrough(self):
        self.assertEqual(provider_profiles.translate_body_to_zh(""), "")
        self.assertEqual(provider_profiles.translate_body_to_zh("   "), "   ")


class TestMtBodiesCli(unittest.TestCase):
    """crawler main(["--mt-bodies"])：走机翻回调、标 translator=mt、无 key 也能跑。"""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self._orig_root = crawler_llm_intel._repo_root
        crawler_llm_intel._repo_root = lambda: self.root
        self.slug = "mt12ab34cd56"
        (self.root / "docs/feeds").mkdir(parents=True)
        (self.root / "docs/articles/openai").mkdir(parents=True)
        en_rel = f"docs/articles/openai/{self.slug}.en.md"
        ft.write_body_doc(self.root / en_rel, {"status": "ok", "url": "https://a/p", "title": "Eng"},
                          "This is an English article body with plenty of words here.")
        bodies = {f"openai\thttps://a/p": {"slug": self.slug, "en_path": en_rel,
                  "en_status": "ok", "zh_path": "", "zh_status": "", "translator": "",
                  "title": "中文标题", "date": "", "captured": ""}}
        ft.save_bodies(self.root / "docs/feeds/bodies.json", bodies)

    def tearDown(self):
        crawler_llm_intel._repo_root = self._orig_root
        self.temp.cleanup()

    def test_writes_mt_translation_and_marks_mt(self):
        # MT 用 gtx，无需任何 key；这里 mock translate_body_to_zh 返回中文
        with mock.patch.object(provider_profiles, "translate_body_to_zh",
                               return_value="这是一篇中文正文的完整机翻内容。"):
            rc = crawler_llm_intel.main(["--mt-bodies"])
        self.assertEqual(rc, 0)
        saved = ft.load_bodies(self.root / "docs/feeds/bodies.json")
        e = saved["openai\thttps://a/p"]
        self.assertEqual(e["zh_status"], "translated")
        self.assertEqual(e["translator"], "mt")
        fm, zh = ft.read_body_doc(self.root / e["zh_path"])
        self.assertEqual(fm["translator"], "mt")
        self.assertEqual(zh, "这是一篇中文正文的完整机翻内容。")

    def test_gtx_failure_leaves_pending_no_crash(self):
        # translate_body_to_zh 原样退回（gtx 全失败）→ 校验不过 → 留 pending、不崩、不写坏
        with mock.patch.object(provider_profiles, "translate_body_to_zh",
                               side_effect=lambda b: b):   # 返回英文原文 = 没翻
            rc = crawler_llm_intel.main(["--mt-bodies"])
        self.assertEqual(rc, 0)
        saved = ft.load_bodies(self.root / "docs/feeds/bodies.json")
        self.assertEqual(saved["openai\thttps://a/p"]["zh_status"], "")
        self.assertEqual(ft.pending_translation_keys(saved), ["openai\thttps://a/p"])


class TestPageFurnitureStrip(unittest.TestCase):
    """中文正文落盘口的页面家具清洗：只删站件，不删正文。

    证人按「该红的红在该处」验：删家具的规则、留文献清单的规则、栅栏内部的豁免，
    各自有独立的断言，放宽任何一条都会有一格变红。
    """

    def test_labels_cta_and_tag_values_gone_prose_untouched(self):
        body = "\n".join([
            "# 推出 Meta VR Glasses",
            "",
            "我们把影院装进了一副 100 克的眼镜里。",
            "",
            "分类",
            "",
            ":",
            "",
            "Meta",
            "",
            "产品新闻",
            "",
            "标签：",
            "",
            "AI",
            "",
            "下载全部图片",
            "",
            "分享本文",
            "",
            "联系销售",
        ])
        out = ft.strip_page_furniture(body)
        self.assertIn("我们把影院装进了一副 100 克的眼镜里。", out)
        self.assertIn("# 推出 Meta VR Glasses", out)
        for gone in ("分类", "标签：", "下载全部图片", "分享本文", "联系销售", "产品新闻"):
            self.assertNotIn(gone, out, f"{gone} 是站件，该删")
        self.assertNotIn("\nAI\n", out, "标签值也该随标签一起走")

    def test_code_fence_interior_never_touched(self):
        body = "\n".join([
            "# 指南",
            "",
            "```text",
            "联系销售",
            "## 继续阅读",
            "分类",
            "```",
        ])
        self.assertEqual(ft.strip_page_furniture(body), body,
                         "代码块里的同样的字串是内容，动一个字都不行")

    def test_bibliography_under_further_reading_survives(self):
        # 同一个「延伸阅读」标题：文献清单（没有卡片日期）不是推荐区
        body = "\n".join([
            "# 文章",
            "",
            "正文段落，讲清了方法。",
            "",
            "### 延伸阅读",
            "",
            "- Rolnick et al. (2019) - Tidy RLHF",
            "- Strubell et al. (2019) - Energy and Policy",
        ])
        out = ft.strip_page_furniture(body)
        self.assertIn("### 延伸阅读", out)
        self.assertIn("Rolnick et al.", out)

    def test_related_cards_block_removed_only_with_card_fingerprint(self):
        with_cards = "\n".join([
            "# 公告",
            "",
            "正文。",
            "",
            "## 继续阅读",
            "",
            "GPT-6 开发实用指南",
            "产品2026年10月2日",
            "DevDay 2026 回顾",
            "公司2026年9月29日",
        ])
        out = ft.strip_page_furniture(with_cards)
        self.assertNotIn("## 继续阅读", out)
        self.assertNotIn("DevDay 2026 回顾", out, "推荐区的卡片标题是站件")
        self.assertIn("正文。", out)
        # 没有「类别+日期」指纹的同名标题，不认作推荐区
        no_fingerprint = "\n".join([
            "# 公告",
            "",
            "## 继续阅读",
            "",
            "我们把这套方法写成了一篇文章，欢迎接着读。",
        ])
        self.assertIn("## 继续阅读", ft.strip_page_furniture(no_fingerprint),
                      "没指纹就不该整块吞掉")

    def test_nav_word_only_before_first_heading(self):
        body = "\n".join(["产品", "# 隆重推出 AgentKit", "", "我们把产品交付给你。", "", "产品"])
        out = ft.strip_page_furniture(body)
        self.assertEqual(out.split("\n")[0].strip(), "# 隆重推出 AgentKit",
                         "标题之前的导航词该删")
        self.assertIn("产品", out.split("\n")[-1], "正文里出现的同一个词不许删")

    def test_strip_is_idempotent(self):
        body = "\n".join(["# 标题", "正文。", "", "分类", "", ":", "", "Meta", "", "联系销售"])
        once = ft.strip_page_furniture(body)
        self.assertEqual(ft.strip_page_furniture(once), once)

    def test_mark_translated_strips_before_sha(self):
        # 落盘口洗过一次：body_sha 必须对得上**洗后**的正文，不然 sha 就成了假账
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            key = "openai\thttps://openai.com/x"
            bodies = {key: {"slug": "abc123", "en_status": "ok", "en_path": "",
                           "zh_status": "", "zh_path": ""}}
            ft.mark_translated(root, bodies, key=key,
                                     zh_body_md="# 标题\n\n正文。\n\n联系销售\n",
                                     translator="agent", today="2026-10-10")
            p = root / "docs/articles/openai/abc123.md"
            fm, body = ft.read_body_doc(p)
            self.assertNotIn("联系销售", body)
            import hashlib
            self.assertEqual(fm["body_sha"],
                             hashlib.sha256(body.strip().encode("utf-8")).hexdigest()[:12])


if __name__ == "__main__":
    unittest.main()
