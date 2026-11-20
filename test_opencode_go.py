"""Go routing and fallback contracts; no live API calls or corpus writes."""
import os
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import requests
import yaml
import ai_review as ai
import crawler_llm_intel as crawler
import fulltext as ft


class TestOpenCodeGo(unittest.TestCase):
    def setUp(self):
        env = {"OPENCODE_GO_ENABLED": "true", "OPENCODE_GO_API_KEY": "go-key",
               "OPENCODE_GO_UNTIL": "2099-01-01T00:00:00+08:00",
               "GEMINI_API_KEY": "gemini-key", "AI_REVIEW_MODEL": "gemini-custom"}
        patcher = mock.patch.dict(os.environ, env, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)
        # Go 的一次调用会写模块级状态（熔断 / 计数 / 额度 / 最后失败原因），逐项重置，
        # 否则前一个用例失败后的熔断会污染后一个用例。
        for name, value in {"_go_disabled": False, "_go_requests": 0,
                            "_go_allowance_total": 0.0, "_go_allowance_calls": 0,
                            "_go_last_failure": ""}.items():
            patcher = mock.patch.object(ai, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def response(self, content='{"changed": false}', finish="stop", status=200,
                 allowance=None, headers=None):
        payload = {"choices": [{"message": {"content": content}, "finish_reason": finish}]}
        if allowance is not None:
            payload["usage"] = {"opencode": {"allowance": allowance, "cost": 0}}
        return SimpleNamespace(status_code=status, headers=headers or {}, text="",
                               json=lambda: payload)

    def test_explicit_enable_key_and_valid_optional_deadline(self):
        self.assertEqual(ai.resolve_backend(), ai.BACKEND_GO)
        for field, values in {
            "OPENCODE_GO_ENABLED": ["", "false"], "OPENCODE_GO_API_KEY": [""],
            "OPENCODE_GO_UNTIL": ["bad", "2099-01-01", "2000-01-01T00:00:00Z"],
        }.items():
            for value in values:
                with self.subTest(field=field, value=value), mock.patch.dict(os.environ, {field: value}):
                    self.assertEqual(ai.resolve_backend(), ai.BACKEND_GEMINI)

    def test_missing_or_blank_deadline_keeps_go_priority(self):
        for value in (None, "", "  "):
            with self.subTest(value=value), mock.patch.dict(os.environ):
                if value is None:
                    os.environ.pop("OPENCODE_GO_UNTIL", None)
                else:
                    os.environ["OPENCODE_GO_UNTIL"] = value
                self.assertEqual(ai.resolve_backend(), ai.BACKEND_GO)
                with mock.patch.object(ai.requests, "post", return_value=self.response()) as post:
                    ai.call_llm("facts")
                    post.assert_called_once()

    def test_no_deadline_subscription_failure_still_restores_old_routes(self):
        with mock.patch.dict(os.environ, {"OPENCODE_GO_UNTIL": ""}), \
                mock.patch.object(ai.requests, "post", return_value=self.response(status=402)) as post, \
                mock.patch.object(ai, "call_llm_gemini", return_value="fallback") as gemini:
            self.assertEqual(ai.call_llm("facts"), "fallback")
            self.assertEqual(ai.resolve_backend(), ai.BACKEND_GEMINI)
            self.assertEqual(crawler.main(["--ai-bodies", "--ai-bodies-go-only"]), 0)
            post.assert_called_once()
            gemini.assert_called_once()

    def test_explicit_backend_still_wins(self):
        self.assertEqual(ai.resolve_backend("gemini"), "gemini")
        with mock.patch.dict(os.environ, {"AI_REVIEW_BACKEND": "anthropic"}):
            self.assertEqual(ai.resolve_backend(), "anthropic")

    def test_review_request_and_models_are_isolated(self):
        with mock.patch.object(ai.requests, "post", return_value=self.response()) as post:
            self.assertEqual(ai.call_llm("facts", model="gemini-custom"), '{"changed": false}')
        args, kw = post.call_args
        self.assertEqual(args[0], ai.GO_API_URL)
        self.assertEqual(kw["json"]["model"], "deepseek-v4.1-flash")
        self.assertEqual(kw["headers"]["Authorization"], "Bearer go-key")
        self.assertTrue(kw["headers"]["x-opencode-session"])
        self.assertEqual(kw["json"]["response_format"], {"type": "json_object"})

    def test_title_and_body_use_text_with_their_own_systems(self):
        with mock.patch.object(ai.requests, "post", return_value=self.response("中文")) as post:
            ai.call_llm_text("title", system="polish", max_tokens=100)
            kw = post.call_args.kwargs["json"]
            self.assertNotIn("response_format", kw)
            self.assertEqual(kw["messages"][0]["content"], "polish")
            self.assertEqual(kw["max_tokens"], 100)
            crawler.make_llm_body_translator(ai.BACKEND_GO, "ignored")("title", "body")
            self.assertEqual(post.call_args.kwargs["json"]["messages"][0]["content"],
                             crawler.BODY_TRANSLATE_SYSTEM)

    def test_http_failures_fallback_current_task_and_open_circuit(self):
        for status in (400, 401, 402, 403, 404, 429, 500, 503):
            # 瞬时错误（429/5xx）先重试一次；永久错误（4xx）不重试
            expected_posts = 2 if status in ai.GO_TRANSIENT_STATUSES else 1
            with self.subTest(status=status), mock.patch.object(ai, "_go_disabled", False), \
                    mock.patch.object(ai.requests, "post", return_value=self.response(status=status)) as post, \
                    mock.patch.object(ai.time, "sleep") as sleep, \
                    mock.patch.object(ai, "call_llm_gemini", return_value="fallback") as gemini:
                self.assertEqual(ai.call_llm("p", api_key="go-key", backend=ai.BACKEND_GO), "fallback")
                ai.call_llm("next", api_key="go-key", backend=ai.BACKEND_GO)
                self.assertEqual(post.call_count, expected_posts)
                if expected_posts == 1:
                    sleep.assert_not_called()
                self.assertEqual(gemini.call_args.kwargs["api_key"], "gemini-key")
                self.assertEqual(gemini.call_args.kwargs["model"], "gemini-custom")
                self.assertEqual(ai.resolve_backend(), "gemini")

    def test_bad_or_truncated_outputs_fallback(self):
        for response in (self.response(""), self.response("partial", "length"),
                         self.response("invalid json"), SimpleNamespace(status_code=200, json=lambda: [])):
            with self.subTest(response=response), mock.patch.object(ai, "_go_disabled", False), \
                    mock.patch.object(ai.requests, "post", return_value=response), \
                    mock.patch.object(ai, "call_llm_gemini", return_value="ok") as gemini:
                self.assertEqual(ai.call_llm("p"), "ok")
                gemini.assert_called_once()

    def test_network_failure_preserves_text_parameters(self):
        with mock.patch.object(ai.requests, "post", side_effect=requests.Timeout) as post, \
                mock.patch.object(ai.time, "sleep"), \
                mock.patch.object(ai, "call_llm_gemini", return_value="ok") as gemini:
            ai.call_llm_text("p", system="polish", max_tokens=321, timeout=17)
        self.assertEqual(post.call_count, 2, "网络异常先重试一次再回落 Gemini")
        self.assertEqual(gemini.call_args.kwargs["system"], "polish")
        self.assertEqual(gemini.call_args.kwargs["max_tokens"], 321)
        self.assertEqual(gemini.call_args.kwargs["response_mime_type"], "text/plain")

    def test_body_failure_never_calls_gemini(self):
        with mock.patch.object(ai.requests, "post", return_value=self.response(status=429)) as post, \
                mock.patch.object(ai.time, "sleep"), \
                mock.patch.object(ai, "call_llm_gemini") as gemini:
            translate = crawler.make_llm_body_translator(ai.BACKEND_GO, "ignored")
            for _ in range(2):
                with self.assertRaises(ai.AiReviewError):
                    translate("title", "body")
            # 第 1 次：429 → 重试一次仍 429 → 熔断（2 次请求）；第 2 次：已熔断，不再发请求
            self.assertEqual(post.call_count, 2)
            gemini.assert_not_called()

    def test_body_cli_without_go_never_loads_or_writes_corpus(self):
        with mock.patch.dict(os.environ, {"OPENCODE_GO_ENABLED": "false"}), \
                mock.patch.object(ai, "call_llm_gemini") as gemini, \
                mock.patch("fulltext.load_bodies") as load:
            self.assertEqual(crawler.main(["--ai-bodies", "--ai-bodies-go-only"]), 0)
            gemini.assert_not_called()
            load.assert_not_called()

    def test_existing_evidence_gate_still_rejects_go_fabrication(self):
        reply = '{"changed":true,"fields":{"free_quota":"999"},"evidence":["invented"]}'
        with mock.patch.object(ai.requests, "post", return_value=self.response(reply)):
            with self.assertRaises(ai.AiReviewError):
                ai.review_vendor("v", "Vendor", {}, {}, [{"url": "https://example.com", "stype": "pricing", "text": "real facts"}])

    def test_expiry_during_run_uses_gemini_key_even_with_cached_go_backend(self):
        with mock.patch.dict(os.environ, {"OPENCODE_GO_UNTIL": "2000-01-01T00:00:00Z"}), \
                mock.patch.object(ai.requests, "post") as post, \
                mock.patch.object(ai, "call_llm_gemini", return_value="ok") as gemini:
            ai.call_llm("p", api_key="go-key", model="deepseek-v4.1-flash", backend=ai.BACKEND_GO)
            post.assert_not_called()
            self.assertEqual(gemini.call_args.kwargs["api_key"], "gemini-key")
            self.assertEqual(gemini.call_args.kwargs["model"], "gemini-custom")

    def test_gemini_abort_signal_is_not_swallowed(self):
        with mock.patch.object(ai.requests, "post", return_value=self.response(status=402)), \
                mock.patch.object(ai, "call_llm_gemini", side_effect=ai.AiQuotaExhausted("quota")):
            with self.assertRaises(ai.AiQuotaExhausted):
                ai.call_llm("p")

    def test_transient_error_retried_then_recovers(self):
        responses = [self.response(status=503), self.response('{"changed": false}')]
        with mock.patch.object(ai.requests, "post", side_effect=responses) as post, \
                mock.patch.object(ai.time, "sleep") as sleep, \
                mock.patch.object(ai, "call_llm_gemini") as gemini:
            self.assertEqual(ai.call_llm("p"), '{"changed": false}')
        self.assertEqual(post.call_count, 2, "503 应重试一次后成功")
        sleep.assert_called_once()
        gemini.assert_not_called()
        self.assertTrue(ai.go_available(), "重试成功不得熔断")
        self.assertEqual(ai.go_usage_snapshot()["requests"], 2)

    def test_retry_after_header_is_respected(self):
        responses = [self.response(status=429, headers={"retry-after": "7"}),
                     self.response("ok")]
        with mock.patch.object(ai.requests, "post", side_effect=responses), \
                mock.patch.object(ai.time, "sleep") as sleep:
            self.assertEqual(ai.call_llm_text("p", system="s", max_tokens=10), "ok")
        sleep.assert_called_once_with(7)

    def test_retry_exhausted_fuses_with_reason(self):
        with mock.patch.object(ai.requests, "post",
                               return_value=self.response(status=429)) as post, \
                mock.patch.object(ai.time, "sleep"):
            translate = crawler.make_llm_body_translator(ai.BACKEND_GO, "ignored")
            with self.assertRaises(ai.AiReviewError) as ctx:
                translate("title", "body")
        self.assertEqual(post.call_count, 2)
        self.assertIn("HTTP 429", str(ctx.exception))
        self.assertIn("已重试 1 次仍失败", str(ctx.exception))
        self.assertFalse(ai.go_available())
        self.assertIn("HTTP 429", ai.go_usage_snapshot()["last_failure"])

    def test_permanent_error_not_retried(self):
        with mock.patch.object(ai.requests, "post",
                               return_value=self.response(status=400)) as post, \
                mock.patch.object(ai.time, "sleep") as sleep, \
                mock.patch.object(ai, "call_llm_gemini", return_value="fallback"):
            self.assertEqual(ai.call_llm("p"), "fallback")
        self.assertEqual(post.call_count, 1, "400/401 这类配置错误重试无意义")
        sleep.assert_not_called()

    def test_truncated_output_not_retried_but_reason_visible(self):
        with mock.patch.object(ai.requests, "post",
                               return_value=self.response("partial", finish="length")) as post, \
                mock.patch.object(ai.time, "sleep") as sleep:
            translate = crawler.make_llm_body_translator(ai.BACKEND_GO, "ignored")
            with self.assertRaises(ai.GoBodyTruncated) as ctx:
                translate("t", "body")
        self.assertEqual(post.call_count, 1, "输出截断重试无意义")
        sleep.assert_not_called()
        self.assertIn("finish_reason=length", str(ctx.exception))
        self.assertTrue(ai.go_available())

    def test_body_budget_bounds_each_request_and_retry_wait(self):
        clock = [100.0]
        responses = [self.response(status=503), self.response("translated")]
        with mock.patch.object(ai.requests, "post", side_effect=responses) as post, \
                mock.patch.object(ai.time, "monotonic", side_effect=lambda: clock[0]), \
                mock.patch.object(ai.time, "sleep", side_effect=lambda seconds: clock.__setitem__(
                    0, clock[0] + seconds)) as sleep:
            translate = crawler.make_llm_body_translator(ai.BACKEND_GO, "ignored")
            self.assertEqual(translate("t", "body", deadline=112), "translated")
            self.assertEqual([call.kwargs["timeout"] for call in post.call_args_list], [12, 7])
            sleep.assert_called_once_with(5)
        with mock.patch.object(ai.requests, "post",
                               return_value=self.response(status=429, headers={"retry-after": "7"})) as post, \
                mock.patch.object(ai.time, "monotonic", return_value=100), \
                mock.patch.object(ai.time, "sleep") as sleep:
            with self.assertRaises(ai.GoBodyBudgetExpired):
                translate("t", "body", deadline=103)
            post.assert_called_once()
            self.assertEqual(post.call_args.kwargs["timeout"], 3)
            sleep.assert_not_called()
        self.assertTrue(ai.go_available())

    def test_body_budget_stops_waiting_for_an_in_flight_request(self):
        from threading import Event

        release = Event()

        def blocked_post(*args, **kwargs):
            release.wait(5)
            return self.response("late")

        with mock.patch.object(ai.requests, "post", side_effect=blocked_post), \
                mock.patch.object(ai.time, "sleep") as sleep:
            translate = crawler.make_llm_body_translator(ai.BACKEND_GO, "ignored")
            try:
                with self.assertRaises(ai.GoBodyBudgetExpired):
                    translate("t", "body", deadline=ai.time.monotonic() + 0.1)
            finally:
                release.set()
            sleep.assert_not_called()
        self.assertTrue(ai.go_available())

    def test_allowance_accumulates_and_formats(self):
        responses = [self.response("ok1", allowance=0.0012),
                     self.response("ok2", allowance=0.0008)]
        with mock.patch.object(ai.requests, "post", side_effect=responses):
            ai.call_llm_text("a", system="s", max_tokens=10)
            ai.call_llm_text("b", system="s", max_tokens=10)
        snap = ai.go_usage_snapshot()
        self.assertEqual(snap["requests"], 2)
        self.assertAlmostEqual(snap["allowance"], 0.002)
        self.assertEqual(snap["allowance_calls"], 2)
        self.assertEqual(snap["allowance_text"], "$0.002")

    def test_ai_bodies_prints_go_usage_summary(self):
        import contextlib
        import io
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "docs/feeds").mkdir(parents=True)
            (root / "docs/articles/openai").mkdir(parents=True)
            en_rel = "docs/articles/openai/go1234567890.en.md"
            ft.write_body_doc(root / en_rel,
                              {"status": "ok", "url": "https://a/p", "title": "Eng"},
                              "English article body with enough words here.")
            ft.save_bodies(root / "docs/feeds/bodies.json", {
                "openai\thttps://a/p": {"slug": "go1234567890", "en_path": en_rel,
                                        "en_status": "ok", "zh_path": "", "zh_status": "",
                                        "translator": "", "title": "中文标题",
                                        "date": "", "captured": ""}})
            resp = self.response("这是一篇中文正文的完整翻译内容，足够长。", allowance=0.004)
            buf = io.StringIO()
            with mock.patch.object(crawler, "_repo_root", lambda: root), \
                    mock.patch.object(ai.requests, "post", return_value=resp), \
                    contextlib.redirect_stdout(buf):
                rc = crawler.main(["--ai-bodies", "--ai-bodies-go-only"])
        self.assertEqual(rc, 0)
        out = buf.getvalue()
        self.assertIn("Go 请求 1 次", out)
        self.assertIn("$0.004", out)

    def test_ai_bodies_go_prefers_whole_and_chunks_only_when_needed(self):
        import contextlib
        import io
        import tempfile

        for mode in ("whole", "truncated", "estimated", "chunk_truncated"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                paragraph = "This is an English paragraph with enough words to be translated. " * 20
                body = "\n\n".join(paragraph for _ in range(45 if mode == "estimated" else 10))
                following = "This independent article should reach Go after the first article."
                ledger = {}
                for slug, url, source in (("gochunk00001", "https://a/p", body),
                                          ("gochunk00002", "https://a/q", following)):
                    rel = f"docs/articles/openai/{slug}.en.md"
                    ft.write_body_doc(root / rel, {"status": "ok", "url": url, "title": "Eng"}, source)
                    ledger[f"openai\t{url}"] = {"slug": slug, "en_path": rel, "en_status": "ok"}
                ledger_path = root / "docs/feeds/bodies.json"
                ft.save_bodies(ledger_path, ledger)
                sent = []

                def reply(*args, **kwargs):
                    payload = kwargs["json"]
                    self.assertEqual(payload["max_tokens"], 32_768)
                    source = payload["messages"][-1]["content"].split("\n\n", 2)[-1]
                    sent.append(source)
                    if (mode in {"truncated", "chunk_truncated"} and len(sent) == 1
                            or mode == "chunk_truncated" and len(sent) == 2):
                        return self.response("partial", finish="length")
                    return self.response("这是一段完整的中文译文。" * max(1, len(source) // 30)
                                         + "最后保留原文结论。")

                buf = io.StringIO()
                with mock.patch.object(crawler, "_repo_root", lambda: root), \
                        mock.patch.object(ai.requests, "post", side_effect=reply), \
                        contextlib.redirect_stdout(buf):
                    self.assertEqual(crawler.main(["--ai-bodies", "--ai-bodies-go-only"]), 0)
                self.assertEqual(sent[-1], following)
                saved = ft.load_bodies(ledger_path)
                self.assertEqual(saved["openai\thttps://a/q"]["translator"], "llm")
                self.assertIn("最后保留原文结论。",
                              ft.read_body_doc(root / saved["openai\thttps://a/q"]["zh_path"])[1])
                if mode == "whole":
                    self.assertEqual(sent, [body, following])
                elif mode == "estimated":
                    self.assertEqual("\n\n".join(sent[:-1]), body)
                    self.assertGreater(len(sent), 2)
                elif mode == "truncated":
                    self.assertEqual(sent[0], body)
                    self.assertEqual("\n\n".join(sent[1:-1]), body)
                else:
                    self.assertEqual(saved["openai\thttps://a/p"]["zh_status"], "")
                    self.assertEqual(len(sent), 3)
                    continue
                self.assertEqual(saved["openai\thttps://a/p"]["translator"], "llm")
                self.assertIn(f"分块成稿 {int(mode != 'whole')}", buf.getvalue())

    def test_workflow_go_precedes_machine_and_render(self):
        workflow = yaml.safe_load((Path(__file__).parent / ".github/workflows/refresh-intel.yml").read_text(encoding="utf-8"))
        job = workflow["jobs"]["crawl"]
        steps = {s["name"]: s for s in job["steps"]}
        names = list(steps)
        order = ["Fetch article bodies (incremental)", "Translate new bodies (Go)",
                 "Translate new bodies (machine)", "Render outputs"]
        self.assertEqual(sorted(order, key=names.index), order)
        self.assertIn("--ai-bodies-go-only", steps[order[1]]["run"])
        self.assertEqual(steps[order[1]]["env"]["AI_BODIES_LIMIT"], "${{ vars.AI_BODIES_LIMIT || '0' }}")
        for name in ("Run intel crawler", order[1]):
            self.assertIn("OPENCODE_GO_API_KEY", steps[name]["env"])
        self.assertNotIn("GEMINI_API_KEY", steps[order[1]]["env"])


if __name__ == "__main__":
    unittest.main()
