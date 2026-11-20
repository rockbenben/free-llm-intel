"""Evidence validation across remote and local review."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import ai_review
import crawler_llm_intel as crawler


PRICING = "https://example.org/pricing"
TERMS = "https://example.org/terms"
QUOTE = "Free accounts receive 100 monthly tokens."


def response(url=PRICING, quote=QUOTE, **extra):
    return {
        "changed": True,
        "fields": {"free_quota": "每月 100 tokens"},
        "evidence": [{"url": url, "quote": quote}],
        **extra,
    }


class TestReviewEvidence(unittest.TestCase):
    def review(self, data):
        pages = [{"url": PRICING, "stype": "pricing", "text": QUOTE},
                 {"url": TERMS, "stype": "terms", "text": "Noncommercial use only."}]
        with patch.object(ai_review, "call_llm", return_value=json.dumps(data)):
            return ai_review.review_vendor("demo", "Demo", {}, {}, pages, backend="gemini")

    def test_remote_requires_explicit_boolean(self):
        for data in ({}, {"changed": 0}, {"changed": "false"}, {"changed": None}):
            with self.subTest(data=data), self.assertRaises(ai_review.AiReviewError):
                self.review(data)
        self.assertEqual(self.review({"changed": False}), {"changed": False})

    def test_remote_checks_quote_against_its_own_page(self):
        for data in (response(TERMS), response(""), response(quote="      "),
                     response(quote=100), response(quote=PRICING)):
            with self.subTest(data=data), self.assertRaises(ai_review.AiReviewError):
                self.review(data)
        self.assertTrue(self.review(response())["changed"])

    def test_rejected_local_patch_preserves_snapshot_and_review_date(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vendor = crawler.VendorIntel("demo", "Demo", "", [], intel_pages=[
                crawler.PageResult(PRICING, "pricing", text=QUOTE, ok=True,
                                   snapshot_text=QUOTE, snapshot_ok=True),
                crawler.PageResult(TERMS, "terms", text="Noncommercial use only.", ok=True),
            ])
            packet = root / crawler.REVIEW_PACKET_DIR / "packets" / "demo.json"
            packet.parent.mkdir(parents=True)
            old = {"sha256": "old"}
            key = f"demo|pricing|{PRICING}"
            for data in (response(TERMS), {}):
                with self.subTest(data=data):
                    snapshots = crawler.SnapshotState(root)
                    snapshots.entries[key] = old.copy()
                    snapshots.reviews["demo"] = "2026-01-01"
                    snapshots.stage_vendor("demo", vendor)
                    packet.write_text(json.dumps(data), encoding="utf-8")
                    self.assertEqual(crawler.run_local_review(root, {"demo": []},
                                                               {"demo": vendor}, snapshots), {})
                    self.assertEqual(snapshots.entries[key], old)
                    self.assertEqual(snapshots.reviews["demo"], "2026-01-01")
                    self.assertTrue(packet.is_file())
                    self.assertFalse(packet.with_suffix(".json.applied").exists())

    def test_partial_guide_updates_preserve_other_overrides(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "profile_overrides.json"
            for guide in ({"tiers": ["recurring"], "signup": "card"}, {"short": "新文案"}):
                ai_review.apply_patches(path, {"demo": self.review(response(guide_meta=guide))})
            saved = json.loads(path.read_text(encoding="utf-8"))["demo"]
            self.assertEqual(saved["guide_meta"],
                             {"tiers": ["recurring"], "signup": "card", "short": "新文案"})

    def test_local_adoption_failure_leaves_packet_and_review_pending(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            vendor = crawler.VendorIntel("demo", "Demo", "", [], intel_pages=[
                crawler.PageResult(PRICING, "pricing", text=QUOTE, ok=True,
                                   snapshot_text=QUOTE, snapshot_ok=True),
            ])
            snapshots = crawler.SnapshotState(root)
            key = f"demo|pricing|{PRICING}"
            snapshots.entries[key] = {"sha256": "old"}
            snapshots.stage_vendor("demo", vendor)
            packet = root / crawler.REVIEW_PACKET_DIR / "packets" / "demo.json"
            packet.parent.mkdir(parents=True)
            packet.write_text(json.dumps(response()), encoding="utf-8")
            with patch.object(crawler, "adopt_patches", side_effect=OSError("write failed")):
                with self.assertRaises(OSError):
                    crawler.run_local_review(root, {"demo": []}, {"demo": vendor}, snapshots)
            self.assertEqual(snapshots.entries[key], {"sha256": "old"})
            self.assertEqual(snapshots.reviews, {})
            self.assertTrue(packet.is_file())
            self.assertFalse(packet.with_suffix(".json.applied").exists())

    def test_remote_rejection_preserves_saved_snapshot_and_review_date(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "llm-intel.yaml").write_text(
                "vendors: [{id: demo}]\nsources: []\n", encoding="utf-8")
            key = f"demo|pricing|{PRICING}"
            old = {"sha256": "old"}
            state = crawler.SnapshotState(root)
            state.entries[key] = old.copy()
            state.reviews["demo"] = "2026-01-01"
            state.save({"demo"}, full_run=False)
            vendor = crawler.VendorIntel("demo", "Demo", "", [], intel_pages=[
                crawler.PageResult(PRICING, "pricing", ok=True, text=QUOTE,
                                   snapshot_ok=True, snapshot_text=QUOTE),
            ])
            with patch.object(crawler, "_repo_root", return_value=root), \
                 patch.object(crawler, "crawl_vendor", return_value=vendor), \
                 patch.object(ai_review, "backend_api_key", return_value="fixture-key"), \
                 patch.object(ai_review, "backend_config_error", return_value=""), \
                 patch.object(ai_review, "resolve_backend", return_value="gemini"), \
                 patch.object(ai_review, "call_llm", return_value="{}") as model:
                self.assertEqual(crawler.main(["--ai-review", "--no-news", "--no-browser", "--only", "demo"]), 0)
            model.assert_called_once()
            saved = crawler.SnapshotState(root)
            self.assertEqual(saved.entries[key]["sha256"], "old")
            self.assertEqual(saved.reviews["demo"], "2026-01-01")
            self.assertFalse((root / "profile_overrides.json").exists())
