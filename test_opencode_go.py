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


class TestOpenCodeGo(unittest.TestCase):
    def setUp(self):
        env = {"OPENCODE_GO_ENABLED": "true", "OPENCODE_GO_API_KEY": "go-key",
               "OPENCODE_GO_UNTIL": "2099-01-01T00:00:00+08:00",
               "GEMINI_API_KEY": "gemini-key", "AI_REVIEW_MODEL": "gemini-custom"}
        patcher = mock.patch.dict(os.environ, env, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)
        patcher = mock.patch.object(ai, "_go_disabled", False)
        patcher.start()
        self.addCleanup(patcher.stop)

    def response(self, content='{"changed": false}', finish="stop", status=200):
        return SimpleNamespace(status_code=status, json=lambda: {
            "choices": [{"message": {"content": content}, "finish_reason": finish}]})

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
            with self.subTest(status=status), mock.patch.object(ai, "_go_disabled", False), \
                    mock.patch.object(ai.requests, "post", return_value=self.response(status=status)) as post, \
                    mock.patch.object(ai, "call_llm_gemini", return_value="fallback") as gemini:
                self.assertEqual(ai.call_llm("p", api_key="go-key", backend=ai.BACKEND_GO), "fallback")
                ai.call_llm("next", api_key="go-key", backend=ai.BACKEND_GO)
                post.assert_called_once()
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
        with mock.patch.object(ai.requests, "post", side_effect=requests.Timeout), \
                mock.patch.object(ai, "call_llm_gemini", return_value="ok") as gemini:
            ai.call_llm_text("p", system="polish", max_tokens=321, timeout=17)
        self.assertEqual(gemini.call_args.kwargs["system"], "polish")
        self.assertEqual(gemini.call_args.kwargs["max_tokens"], 321)
        self.assertEqual(gemini.call_args.kwargs["response_mime_type"], "text/plain")

    def test_body_failure_never_calls_gemini(self):
        with mock.patch.object(ai.requests, "post", return_value=self.response(status=429)) as post, \
                mock.patch.object(ai, "call_llm_gemini") as gemini:
            translate = crawler.make_llm_body_translator(ai.BACKEND_GO, "ignored")
            for _ in range(2):
                with self.assertRaises(ai.AiReviewError):
                    translate("title", "body")
            post.assert_called_once()
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
