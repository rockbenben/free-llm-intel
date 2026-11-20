"""Regression coverage for source coverage and corpus publication."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import crawler_llm_intel as crawler
import fulltext
import provider_profiles


class TestSourceCoverage(unittest.TestCase):
    def test_registered_feed_only_replaces_html_that_declares_it(self):
        feed = "https://example.org/company.rss"
        blog = crawler.PageResult("https://example.org/blog", "blog", ok=True)
        related = crawler.PageResult("https://example.org/news", "news", ok=True, feeds=[feed])
        empty_feed = "https://example.org/empty.rss"
        updates = crawler.PageResult("https://example.org/updates", "updates", ok=True, feeds=[empty_feed])
        rss = crawler.PageResult(feed, "feed", ok=True, raw=(
            "<rss><channel><item><title>Company news</title>"
            "<link>https://example.org/company/post</link></item></channel></rss>"))
        intel = crawler.VendorIntel("demo", "Demo", "", [], news_pages=[rss, blog, related, updates])
        extract = Mock(side_effect=lambda page, **kw: [
            crawler.Article(title="Independent article", url=page.url + "/post")
        ])
        with patch.object(crawler, "extract_articles_from_page", extract), \
             patch.object(crawler, "fetch_feed_articles", return_value=[]) as fetch:
            crawler.collect_news_articles(intel, crawler.build_session())
        fetch.assert_called_once()
        self.assertEqual(fetch.call_args.args[1], empty_feed)
        self.assertEqual([c.args[0] for c in extract.call_args_list], [blog, updates])
        self.assertEqual({a.url for a in intel.all_news_articles}, {
            "https://example.org/company/post", blog.url + "/post", updates.url + "/post",
        })

    def test_english_source_uses_declared_language(self):
        url = "https://example.org/blog"
        browser = Mock(enabled=True)
        browser.render.return_value = ("<html><main>Official news</main></html>", url, 200)
        session = Mock()
        session.get.return_value = Mock(status_code=403, url=url)
        with patch.object(crawler, "extract_evidence", return_value={k: [1] for k, _, _ in crawler.KEYWORD_GROUPS}):
            crawler.crawl_vendor({"id": "demo"}, [{"type": "blog", "url": url, "lang": "en"}],
                                 session, delay=0, browser=browser)
        self.assertTrue(session.get.call_args.kwargs["headers"]["Accept-Language"].startswith("en"))
        self.assertEqual(browser.render.call_args.args[:2], (url, "en"))


class TestCorpusCompletion(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.feeds = self.root / "docs/feeds"
        self.feeds.mkdir(parents=True)
        mode = patch.object(crawler, "_repo_root", return_value=self.root)
        mode.start()
        self.addCleanup(mode.stop)

    def test_fetch_limit_counts_attempts_and_preserves_later_sibling_titles(self):
        page = "https://example.org/updates"
        urls = [f"{page}#{entry}" for entry in ("done", "deferred", "next", "later")]
        titles = ["旧条目", "退避条目", "新条目", "后续条目"]
        rows = [{"vendor": "demo", "url": url, "title": title} for url, title in zip(urls, titles)]
        key = fulltext.bodies_key("demo", urls[0])
        en_path = "docs/articles/demo/done.en.md"
        fulltext.write_body_doc(self.root / en_path, {}, "Existing English article. " * 30)
        bodies = {key: {"en_status": "ok", "en_path": en_path, "src_lang": "en"}}
        fulltext.save_bodies(self.feeds / "bodies.json", bodies)
        (self.root / crawler.BODY_RETRY_LEDGER_NAME).write_text(
            json.dumps({urls[1]: {"next": "9999-01-01"}}), encoding="utf-8")
        html = "<article><p>" + "Source article paragraph. " * 30 + "</p></article>"
        result = crawler.PageResult(urls[2], "news", ok=True, raw=html, final_url=urls[2])
        with patch.object(fulltext, "iter_article_rows", return_value=rows), \
             patch.object(crawler, "fetch_url", return_value=result) as fetch, \
             patch.object(fulltext, "_slice_anchor_section", return_value="Article section. " * 20) as split:
            self.assertEqual(crawler.main(["--fetch-bodies", "--fetch-limit", "1"]), 0)
        fetch.assert_called_once()
        self.assertEqual(fetch.call_args.args[1], urls[2])
        self.assertIn(titles[3], split.call_args.args[3])

    def test_cleaned_empty_translation_keeps_existing_file_and_ledger(self):
        url = "https://example.org/post"
        key = fulltext.bodies_key("demo", url)
        ledger = self.feeds / "bodies.json"
        bodies = {key: {"slug": "abc"}}
        fulltext.mark_translated(self.root, bodies, key=key, zh_body_md="已有译文。",
                                 translator="agent", today="2026-01-01")
        path = self.root / bodies[key]["zh_path"]
        before = path.read_bytes()
        fulltext.save_bodies(ledger, bodies)
        ledger_before = ledger.read_bytes()
        zh = self.root / "input.md"
        zh.write_text("联系销售", encoding="utf-8")
        self.assertNotEqual(crawler.main(["--mark-translated", key, "--zh-file", str(zh)]), 0)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(ledger.read_bytes(), ledger_before)
        fulltext.write_body_doc(path, {"status": "translated"}, "")
        self.assertTrue(fulltext.validate_bodies(self.root, bodies))

    def test_partial_machine_translation_stays_pending(self):
        key = fulltext.bodies_key("demo", "https://example.org/post")
        en_path = "docs/articles/demo/demo.en.md"
        fulltext.write_body_doc(self.root / en_path, {}, "First paragraph.\n\n```\ncode()\n```\n\nLast paragraph.")
        ledger = self.feeds / "bodies.json"
        fulltext.save_bodies(ledger, {key: {"slug": "demo", "en_status": "ok", "en_path": en_path}})
        for failed in (None, "   "):
            with self.subTest(failed=failed), patch.object(
                provider_profiles, "_gtx_translate",
                side_effect=["这段译文足够长，确保即使后半段仍为英文也会通过文章级语言比例验证。" * 4, failed],
            ) as gtx:
                self.assertEqual(crawler.main(["--mt-bodies"]), 0)
                self.assertEqual(gtx.call_count, 2)
                self.assertEqual(fulltext.pending_translation_keys(fulltext.load_bodies(ledger)), [key])
                self.assertFalse((self.root / "docs/articles/demo/demo.md").exists())

    def test_reclassify_does_not_register_furniture_as_native_body(self):
        url = "https://example.org/post"
        key = fulltext.bodies_key("demo", url)
        en_path = "docs/articles/demo/demo.en.md"
        fulltext.write_body_doc(self.root / en_path, {"url": url}, "联系销售")
        bodies = {key: {"slug": "demo", "en_status": "ok", "en_path": en_path}}
        self.assertEqual(fulltext.reclassify_bodies(self.root, bodies), 1)
        self.assertEqual(bodies[key]["en_status"], "fetch_failed")
        self.assertNotIn("zh_path", bodies[key])
        self.assertEqual(fulltext.validate_bodies(self.root, bodies), [])
