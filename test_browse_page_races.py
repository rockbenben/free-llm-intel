"""Browser regressions for out-of-order index and reader responses."""

import unittest
from pathlib import Path

try:
    from playwright.sync_api import expect, sync_playwright
except ImportError as exc:
    raise unittest.SkipTest("需要 Playwright 才能验证页面请求时序") from exc


HTML = Path(__file__).resolve().parent / "docs/index.html"
ORIGIN = "https://fixture.test"
ARTICLES_PATH = "/feeds/articles.json"
VENDORS_PATH = "/feeds/vendors.json"
DEMO_FEED = ORIGIN + "/feeds/llm-news-demo.xml"
VENDORS = {"vendors": [
    {"id": "demo", "brand": "Demo AI", "feed": DEMO_FEED, "rank": 0},
    {"id": "other", "brand": "Other AI", "feed": ORIGIN + "/feeds/other.xml", "rank": 1},
]}


class TestBrowsePageRaces(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        playwright = sync_playwright().start()
        cls.addClassCleanup(playwright.stop)
        if not Path(playwright.chromium.executable_path).is_file():
            raise unittest.SkipTest("需要 Playwright Chromium 才能验证页面请求时序")
        cls.browser = playwright.chromium.launch()
        cls.addClassCleanup(cls.browser.close)

    def setUp(self):
        self.page = self.browser.new_page()
        self.addCleanup(self.page.close)
        self.page.set_default_timeout(5000)
        html = HTML.read_text(encoding="utf-8")
        self.page.route(f"{ORIGIN}/**", lambda route: route.fulfill(
            content_type="text/html; charset=utf-8", body=html,
        ) if route.request.is_navigation_request() else route.abort())
        self.page.add_init_script("""
            const pending = new Map();
            const seen = [];
            window.fetch = (url, options = {}) => new Promise(resolve => {
              const key = (options.method || 'GET') + ' ' + new URL(url, location.href).pathname;
              seen.push(key);
              pending.set(key, resolve);
            });
            window.fixture = { pending, seen, async resolve(key, value, status) {
              const resolve = pending.get(key);
              if (!resolve) throw new Error('Unexpected response: ' + key);
              pending.delete(key);
              resolve({ ok: status < 400, status, json: async () => value, text: async () => value });
              await new Promise(done => setTimeout(done, 0));
            }};
        """)
        self.page.goto(ORIGIN + "/")

    def respond(self, path, value="", *, method="GET", status=200):
        key = f"{method} {path}"
        self.page.wait_for_function("key => fixture.pending.has(key)", arg=key)
        self.page.evaluate("args => fixture.resolve(...args)", [key, value, status])

    def article_index(self, *, first_langs="both"):
        return {"articles": [
            ["文章甲", ORIGIN + "/a", "demo", "2026-11-19", "", "first", "1", first_langs],
            ["文章乙", ORIGIN + "/b", "other", "2026-11-18", "", "second", "1", "both"],
        ]}

    def open_article(self, title):
        self.page.get_by_role("button", name=f"读全文：{title}", exact=True).click()

    def test_late_vendor_index_updates_an_active_filter_and_subscription(self):
        self.respond(ARTICLES_PATH, self.article_index())
        self.page.locator(".item button.vendor").get_by_text("demo", exact=True).click()
        expect(self.page.locator("#items .item")).to_have_count(1)
        self.respond(VENDORS_PATH, VENDORS)
        expect(self.page.locator(".item button.vendor")).to_have_text("Demo AI")
        expect(self.page.locator("#chips button[aria-pressed=true]")).to_contain_text("Demo AI")
        expect(self.page.locator("#subscribe-link")).to_have_attribute("href", DEMO_FEED)
        expect(self.page.locator("#items .item")).to_have_count(1)

    def test_vendor_index_first_still_offers_the_single_vendor_feed(self):
        self.respond(VENDORS_PATH, VENDORS)
        self.respond(ARTICLES_PATH, self.article_index())
        self.page.locator("#chips button").filter(has_text="Demo AI").click()
        expect(self.page.locator("#subscribe-link")).to_have_attribute("href", DEMO_FEED)

    def test_merged_feed_fallback_can_still_select_a_vendor_by_name(self):
        self.respond(ARTICLES_PATH, status=404)
        self.respond("/feeds/llm-news-all.xml", (
            '<rss><channel><item><title>[Demo AI] 动态</title>'
            f'<link>{ORIGIN}/a</link><source url="{DEMO_FEED}">Demo AI</source>'
            '</item></channel></rss>'
        ))
        self.respond(VENDORS_PATH, VENDORS)
        self.page.locator("#chips button").filter(has_text="Demo AI").click()
        expect(self.page.locator("#subscribe-link")).to_have_attribute("href", DEMO_FEED)
        expect(self.page.locator("#items .item")).to_have_count(1)

    def test_late_chinese_body_cannot_overwrite_english_selection(self):
        self.respond(ARTICLES_PATH, self.article_index())
        self.open_article("文章甲")
        self.page.locator("#reader-lang-en").click()
        self.respond("/articles/demo/first.en.md", "Selected English body.")
        self.respond("/articles/demo/first.md", "迟到的中文正文。")
        expect(self.page.locator("#reader-body")).to_have_text("Selected English body.")
        expect(self.page.locator("#reader-lang-en")).to_have_attribute("aria-pressed", "true")
        self.assertEqual(self.page.evaluate("new URL(location.href).searchParams.get('lang')"), "en")

    def close_article(self):
        self.page.locator("#reader-close").click()
        self.page.wait_for_function("!new URL(location.href).searchParams.has('read')")

    def test_stale_failed_request_cannot_fall_back_into_another_article(self):
        self.respond(ARTICLES_PATH, self.article_index())
        self.open_article("文章甲")
        self.close_article()
        self.open_article("文章乙")
        self.respond("/articles/other/second.md", "当前正文。")
        self.respond("/articles/demo/first.md", status=404)
        expect(self.page.locator("#reader-body")).to_have_text("当前正文。")
        self.assertNotIn("GET /articles/other/second.en.md", self.page.evaluate("fixture.seen"))

    def test_stale_language_probe_cannot_disable_another_articles_language(self):
        self.respond(ARTICLES_PATH, self.article_index(first_langs=""))
        self.open_article("文章甲")
        self.respond("/articles/demo/first.md", "第一篇正文。")
        self.close_article()
        self.open_article("文章乙")
        self.respond("/articles/other/second.md", "第二篇正文。")
        self.respond("/articles/demo/first.en.md", method="HEAD", status=404)
        expect(self.page.locator("#reader-lang-en")).to_be_enabled()
        expect(self.page.locator("#reader-body")).to_have_text("第二篇正文。")

    def test_popstate_switches_article_title_and_discards_previous_body(self):
        self.respond(ARTICLES_PATH, self.article_index())
        self.open_article("文章甲")
        self.page.evaluate("""() => {
            history.pushState({ fliPushed: true }, '', '?read=other/second&lang=zh');
            window.dispatchEvent(new PopStateEvent('popstate'));
        }""")
        self.respond("/articles/other/second.md", "第二篇正文。")
        self.respond("/articles/demo/first.md", "第一篇正文。")
        expect(self.page.locator("#reader-title-text")).to_have_text("文章乙")
        expect(self.page.locator("#reader-body")).to_have_text("第二篇正文。")
