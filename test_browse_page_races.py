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
        expect(self.page.locator(".reader-prose")).to_have_attribute("lang", "en")
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

    def test_reader_is_modal_and_escape_restores_focus_and_history(self):
        self.respond(ARTICLES_PATH, self.article_index())
        trigger = self.page.get_by_role("button", name="读全文：文章甲", exact=True)
        trigger.press("Enter")
        dialog = self.page.locator("#reader-drawer:modal")
        expect(dialog).to_be_visible()
        expect(self.page.locator("#reader-close")).to_be_focused()
        self.page.locator("#q").focus()
        expect(self.page.locator("#reader-close")).to_be_focused()
        self.respond("/articles/demo/first.md", "第一篇正文。")
        self.page.keyboard.press("Escape")
        self.page.wait_for_function("!new URL(location.href).searchParams.has('read')")
        expect(dialog).to_have_count(0)
        expect(trigger).to_be_focused()
        self.page.go_forward()
        expect(dialog).to_be_visible()
        self.page.mouse.click(10, 100)
        self.page.wait_for_function("!new URL(location.href).searchParams.has('read')")
        expect(trigger).to_be_focused()

    def test_filter_and_load_more_keep_keyboard_position(self):
        rows = [[f"文章 {i}", f"{ORIGIN}/{i}", "demo", "2026-11-19"] for i in range(201)]
        self.respond(ARTICLES_PATH, {"articles": rows})
        vendor = self.page.locator('#chips button[data-vendor="demo"]')
        vendor.press("Enter")
        expect(vendor).to_be_focused()
        self.respond(VENDORS_PATH, VENDORS)
        expect(vendor).to_be_focused()
        self.page.locator("#more-btn").press("Enter")
        expect(self.page.get_by_role("link", name="文章 200", exact=True)).to_be_focused()

        self.page.locator("#tab-quotas").press("Enter")
        self.respond("/feeds/quotas.json", {"vendors": [{"id": "demo", "name": "Demo AI", "part": 1}]})
        part = self.page.locator('#q-parts button[data-part="1"]')
        part.press("Enter")
        expect(part).to_be_focused()
        self.page.locator("#q-reset").press("Enter")
        expect(self.page.locator("#qq")).to_be_focused()

    def test_theme_override_persists_and_can_return_to_system(self):
        self.page.emulate_media(color_scheme="light")
        scheme = self.page.locator('meta[name="color-scheme"]')
        button = self.page.locator("#theme-btn")
        expect(scheme).to_have_attribute("content", "light dark")
        button.click()
        expect(scheme).to_have_attribute("content", "dark")
        expect(self.page.locator("html")).to_have_css("color-scheme", "dark")
        expect(self.page.locator("body")).to_have_css("background-color", "rgb(14, 19, 25)")
        self.page.reload()
        expect(scheme).to_have_attribute("content", "dark")
        self.page.emulate_media(color_scheme="dark")
        expect(scheme).to_have_attribute("content", "dark")
        self.page.emulate_media(color_scheme="light")
        button.click()
        expect(scheme).to_have_attribute("content", "light dark")
        self.assertIsNone(self.page.evaluate("localStorage.getItem('fli-theme')"))
        self.page.emulate_media(color_scheme="dark")
        expect(self.page.locator("body")).to_have_css("background-color", "rgb(14, 19, 25)")

    def test_switching_tabs_does_not_restart_pending_feed_loads(self):
        for name, path, payload in (
            ("changes", "/feeds/intel-changes.json", {"items": []}),
            ("quotas", "/feeds/quotas.json", {"vendors": []}),
        ):
            with self.subTest(tab=name):
                tab = self.page.locator(f"#tab-{name}")
                tab.click()
                self.page.locator("#tab-news").click()
                tab.click()
                self.assertEqual(self.page.evaluate("fixture.seen").count(f"GET {path}"), 1)
                self.respond(path, payload)
