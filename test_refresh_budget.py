"""Regression coverage for the daily refresh work deadline."""

import contextlib
import io
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import yaml

import refresh_budget


class TestRefreshBudget(unittest.TestCase):
    deadline = 60 * 60 - 180

    def run_step(self, mode, elapsed, limit="900"):
        with patch.dict(refresh_budget.os.environ, {
            "REFRESH_WORK_DEADLINE": str(self.deadline),
            "AI_BODIES_BUDGET_SECONDS": limit,
        }), patch.object(refresh_budget.time, "time", return_value=elapsed), \
             patch.object(refresh_budget.subprocess, "run",
                          return_value=SimpleNamespace(returncode=0)) as launch, \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = refresh_budget.main([mode, "python", "crawler_llm_intel.py"])
        return code, launch

    def test_slow_core_leaves_shared_time_for_go_and_skips_mt_at_cutoff(self):
        code, launch = self.run_step("translate", 52 * 60)
        self.assertEqual(code, 0)
        hard, soft = launch.call_args.args[0][2], launch.call_args.args[0][-1]
        self.assertGreater(float(soft), 0)
        self.assertLess(float(soft), int(hard.removesuffix("s")))
        self.assertLessEqual(int(hard.removesuffix("s")) + 5, 5 * 60)
        code, launch = self.run_step("translate", 55 * 60)
        self.assertEqual(code, 0)
        self.assertEqual(float(launch.call_args.args[0][-1]), 105)
        code, launch = self.run_step("translate", self.deadline)
        self.assertEqual(code, 0)
        launch.assert_not_called()

    def test_zero_setting_still_honors_work_deadline(self):
        code, launch = self.run_step("translate", self.deadline - 60, limit="0")
        self.assertEqual(code, 0)
        self.assertTrue(0 < float(launch.call_args.args[0][-1]) < 60)

    def test_positive_step_setting_applies_if_smaller_than_remaining(self):
        code, launch = self.run_step("translate", 120, limit="75")
        self.assertEqual(code, 0)
        self.assertEqual(launch.call_args.args[0][-2:], ["--ai-bodies-budget-seconds", "75"])

    def test_required_stage_fails_if_no_work_time_remains(self):
        code, launch = self.run_step("required", self.deadline + 1)
        self.assertNotEqual(code, 0)
        launch.assert_not_called()

    def test_malformed_translation_limit_does_not_stop_the_core_crawler(self):
        code, launch = self.run_step("required", 120, limit="invalid")
        self.assertEqual(code, 0)
        launch.assert_called_once()

    def test_workflow_keeps_publish_steps_outside_work_deadline(self):
        workflow = Path(__file__).resolve().parent / ".github/workflows/refresh-intel.yml"
        crawl = yaml.safe_load(workflow.read_text(encoding="utf-8"))["jobs"]["crawl"]
        self.assertEqual(int(crawl["env"]["REFRESH_JOB_TIMEOUT_MINUTES"]), crawl["timeout-minutes"])
        steps = {step.get("name"): step for step in crawl["steps"]}
        names = list(steps)
        self.assertLess(names.index("Set refresh work deadline"), names.index("Checkout"))
        self.assertIn("GITHUB_ENV", steps["Set refresh work deadline"]["run"])
        for name in ("Run intel crawler", "Fetch article bodies (incremental)"):
            self.assertIn("refresh_budget.py required", steps[name]["run"])
        for name in ("Translate new bodies (Go)", "Translate new bodies (machine)"):
            self.assertIn("refresh_budget.py translate", steps[name]["run"])
            self.assertLess(names.index(name), names.index("Render outputs"))
        for name in ("Render outputs", "Verify generated artifacts and invariants", "Commit all updates"):
            self.assertNotIn("refresh_budget.py", steps[name]["run"])
            self.assertNotIn("continue-on-error", steps[name])
