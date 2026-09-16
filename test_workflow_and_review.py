# -*- coding: utf-8 -*-
"""
test_workflow_and_review.py —— 自动化工作流与核心模块单测
"""

import json
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


if __name__ == "__main__":
    unittest.main()
