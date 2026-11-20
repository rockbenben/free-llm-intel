"""Regression coverage for the write scope of local maintenance commands."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import crawler_llm_intel as crawler
import fulltext


class TestMaintenanceScope(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.feeds = self.root / "docs/feeds"
        self.feeds.mkdir(parents=True)
        repo_root = patch.object(crawler, "_repo_root", return_value=self.root)
        repo_root.start()
        self.addCleanup(repo_root.stop)

    def test_custom_news_md_does_not_enable_global_writes(self):
        (self.root / "llm-intel.yaml").write_text(
            "vendors: [{id: vendor_a}, {id: vendor_b}]\nsources: []\n", encoding="utf-8"
        )
        archive_dir = self.root / "llm-news"
        archive_dir.mkdir()
        originals = {
            archive_dir / "vendor_b.md": b"Other vendor archive",
            self.feeds / "llm-news-vendor_b.xml": b"Other vendor RSS",
            self.feeds / "articles.json": b'{"fields":[],"articles":[]}',
            self.root / "llm-news-feeds.opml": b"Global OPML",
        }
        for path, content in originals.items():
            path.write_bytes(content)
        intel = crawler.VendorIntel("vendor_a", "A", "", [])
        intel.all_news_articles = [
            crawler.Article(title="新动态", url="https://example.org/news/demo", date="2026-01-01")
        ]
        with patch.object(crawler, "crawl_vendor", return_value=intel), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(crawler.main(["--only", "vendor_a", "--news-md", "preview.md", "--no-browser"]), 0)
        self.assertTrue((archive_dir / "vendor_a.md").is_file())
        for path, content in originals.items():
            with self.subTest(path=path):
                self.assertEqual(path.read_bytes(), content)

    def test_fully_isolated_preview_renders_without_cleaning_other_feeds(self):
        (self.root / "llm-intel.yaml").write_text(
            "vendors: [{id: vendor_a}, {id: vendor_b}]\nsources: []\n", encoding="utf-8"
        )
        preview = self.root / "preview"
        preview_feeds = preview / "feeds"
        preview_feeds.mkdir(parents=True)
        other_feed = preview_feeds / "llm-news-vendor_b.xml"
        other_feed.write_bytes(b"Other vendor RSS")
        intel = crawler.VendorIntel("vendor_a", "A", "", [])
        intel.all_news_articles = [
            crawler.Article(title="新动态", url="https://example.org/news/demo", date="2026-01-01")
        ]
        with patch.object(crawler, "crawl_vendor", return_value=intel), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(crawler.main([
                "--only", "vendor_a", "--no-browser",
                "--news-md", "preview/news.md", "--news-opml", "preview/news.opml",
                "--feeds-dir", "preview/feeds",
            ]), 0)
        self.assertTrue((preview / "news.md").is_file())
        self.assertTrue((preview / "news.opml").is_file())
        self.assertTrue((preview_feeds / "llm-news-vendor_a.xml").is_file())
        self.assertEqual(other_feed.read_bytes(), b"Other vendor RSS")
        self.assertFalse((self.root / crawler.TOP_PICKS_SVG).exists())
        self.assertEqual(list(self.feeds.iterdir()), [])

    def test_scoped_body_maintenance_protects_translations_and_other_vendors(self):
        bodies = {}
        originals = {}
        rows = []
        for vendor, article in (("vendor_a", "translated"), ("vendor_a", "pending"), ("vendor_b", "outside")):
            url = f"https://example.org/{article}"
            key = fulltext.bodies_key(vendor, url)
            slug = fulltext.url_hash(url)
            en = f"docs/articles/{vendor}/{slug}.en.md"
            fulltext.write_body_doc(self.root / en, {"url": url, "status": "ok"}, "中文原生正文。" * 60)
            bodies[key] = {"slug": slug, "en_path": en, "en_status": "ok"}
            if article == "translated":
                fulltext.mark_translated(self.root, bodies, key=key, zh_body_md="已有精译。",
                                         translator="agent", today="2026-01-01")
                originals[self.root / bodies[key]["zh_path"]] = (self.root / bodies[key]["zh_path"]).read_bytes()
            if article != "pending":
                originals[self.root / en] = (self.root / en).read_bytes()
            rows.append([vendor, url, article])
        ledger = self.feeds / "bodies.json"
        fulltext.save_bodies(ledger, bodies)
        before = fulltext.load_bodies(ledger)
        with patch.object(fulltext, "iter_article_rows", return_value=[
            dict(zip(("vendor", "url", "title"), row)) for row in rows
        ]), patch.object(crawler, "fetch_url") as fetch, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(crawler.main(["--fetch-bodies", "--fetch-vendor", "vendor_a", "--refresh"]), 0)
        fetch.assert_not_called()
        after = fulltext.load_bodies(ledger)
        for url, vendor in (("translated", "vendor_a"), ("outside", "vendor_b")):
            key = fulltext.bodies_key(vendor, f"https://example.org/{url}")
            self.assertEqual(after[key], before[key])
        self.assertEqual(after[fulltext.bodies_key("vendor_a", "https://example.org/pending")]["translator"], "native")
        for path, content in originals.items():
            self.assertEqual(path.read_bytes(), content)

    def test_refresh_skips_an_existing_translation_before_fetch(self):
        url = "https://example.org/translated"
        key = fulltext.bodies_key("vendor_a", url)
        bodies = {key: {"zh_status": "translated"}}
        with patch.object(fulltext, "extract_article_markdown") as extract:
            fetch = Mock(return_value=("", False, 404, url))
            self.assertEqual(fulltext.fetch_bodies(
                self.root, [{"url": url, "vendor": "vendor_a"}], bodies,
                fetch=fetch, today="2026-01-01", only_missing=False,
            ), 0)
        fetch.assert_not_called()
        extract.assert_not_called()
