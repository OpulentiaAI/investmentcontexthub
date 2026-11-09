"""Offline contract tests for the Context.dev Answers adapter."""

from __future__ import annotations

import json
import os
import unittest
from unittest.mock import patch
from urllib.error import URLError

from adapters.contextdev import AnswersError, AnswersResponseError, ContextAnswers, build_request
from adapters.contextdev.client import ENDPOINT, MAX_RESPONSE_BYTES, _NoRedirect


class CaptureTransport:
    def __init__(self, status=200, headers=None, body=None):
        self.status = status
        self.headers = headers if headers is not None else {}
        self.body = body if body is not None else b'{"json_content": {}, "sources": []}'
        self.calls = []

    def __call__(self, request, timeout):
        self.calls.append((request, timeout))
        return self.status, self.headers, self.body


class RequestTests(unittest.TestCase):
    def test_offline_builder_explicit_default_and_example_shape(self):
        with patch.dict(os.environ, {"CONTEXT_DEV_API_KEY": "do-not-read"}):
            self.assertEqual(build_request("x"), {"task": "x", "mode": "fast"})
        example = {"known": False, "cost": 0, "unknown": None, "nested": [{"name": ""}]}
        self.assertEqual(build_request("x" * 2000, json_format=example, mode="ultra"),
                         {"task": "x" * 2000, "mode": "ultra", "json_format": example})
        self.assertNotIn("$schema", json.dumps(example))

    def test_task_mode_and_example_invalid_inputs(self):
        for task in ("", " \n ", "x" * 2001, None, 7):
            with self.subTest(task=str(task)[:10]), self.assertRaises(ValueError):
                build_request(task)
        for mode in ("", "standard", "FAST", None, True):
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                build_request("x", mode=mode)
        for example in ([], "{}", {1: "value"}, {"bad": float("nan")},
                        {"bad": float("inf")}, {"bad": object()}, {"bad": True, "other": {1: "x"}}):
            with self.subTest(example=str(example)), self.assertRaises(ValueError):
                build_request("x", json_format=example)

    def test_example_depth_value_and_character_bounds(self):
        def nested(levels):
            value = 0
            for _ in range(levels - 1):
                value = {"x": value}
            return value

        build_request("x", json_format=nested(8))
        with self.assertRaises(ValueError):
            build_request("x", json_format=nested(9))
        build_request("x", json_format={"list": [0] * 498})
        with self.assertRaises(ValueError):
            build_request("x", json_format={"list": [0] * 499})
        build_request("x", json_format={"text": "x" * 15988})
        with self.assertRaises(ValueError):
            build_request("x", json_format={"text": "x" * 16000})
        cycle = {}
        cycle["self"] = cycle
        with self.assertRaises(ValueError):
            build_request("x", json_format=cycle)
        example = {"nested": [{"cost": 0, "unknown": None}]}
        payload = build_request("x", json_format=example)
        example["nested"][0]["cost"] = 10
        self.assertEqual(payload["json_format"]["nested"][0], {"cost": 0, "unknown": None})

    def test_timeout_bounds_and_behavior(self):
        for mode in ("fast", "ultra"):
            for behavior in ("fail", "return-partial"):
                for ms in (1000, 300000):
                    with self.subTest(mode=mode, behavior=behavior, ms=ms):
                        self.assertEqual(build_request("x", mode=mode, timeout_opts={
                            "milliseconds": ms, "behavior": behavior,
                        })["timeoutOpts"], {"milliseconds": ms, "behavior": behavior})
        self.assertEqual(build_request("x", timeout_opts={"milliseconds": 1000})["timeoutOpts"],
                         {"milliseconds": 1000, "behavior": "fail"})
        for opts in ({}, {"milliseconds": 999}, {"milliseconds": 300001},
                     {"milliseconds": 1.5}, {"milliseconds": float("inf")},
                     {"milliseconds": float("nan")}, {"milliseconds": True},
                     {"milliseconds": "30000"}, {"milliseconds": 1000, "behavior": "other"},
                     {"milliseconds": 1000, "behavior": True},
                     {"milliseconds": 1000, "other": "x"}, []):
            with self.subTest(opts=opts), self.assertRaises(ValueError):
                build_request("x", timeout_opts=opts)


class LiveTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {"CONTEXT_DEV_API_KEY": "sensitive-key"}, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def test_both_live_and_current_confirm_required_before_transport(self):
        transport = CaptureTransport()
        client = ContextAnswers(transport=transport)
        for live, confirm in ((False, "send"), (True, None), (True, "SEND"),
                              (True, "send "), (1, "send")):
            with self.subTest(live=live, confirm=confirm):
                with patch.dict(os.environ, {"CONFIRM": confirm} if confirm else {}, clear=False):
                    if confirm is None:
                        os.environ.pop("CONFIRM", None)
                    with self.assertRaises(AnswersError):
                        client.answer("x", live=live)
        self.assertEqual(transport.calls, [])

    def test_missing_or_malformed_key_refuses_transport(self):
        transport = CaptureTransport()
        with patch.dict(os.environ, {"CONFIRM": "send"}):
            for key in (None, "", "bad\nkey", "bad\rkey", "bad key", "bad\x7fkey"):
                with self.subTest(key=key):
                    os.environ.pop("CONTEXT_DEV_API_KEY", None)
                    if key is not None:
                        os.environ["CONTEXT_DEV_API_KEY"] = key
                    with self.assertRaises(AnswersError):
                        ContextAnswers(transport=transport).answer("x", live=True)
        self.assertEqual(transport.calls, [])

    def test_fixed_envelope_and_timeout_exceeds_research_deadline(self):
        transport = CaptureTransport()
        with patch.dict(os.environ, {"CONFIRM": "send"}):
            client = ContextAnswers(transport=transport)
            client.answer("find plans", json_format={"plans": [{"name": ""}]}, live=True)
            client.answer("compare", mode="ultra", timeout_opts={"milliseconds": 2000}, live=True)
            client.answer("compare", mode="ultra", timeout_opts={"milliseconds": 300000}, live=True)
        self.assertEqual([timeout for _, timeout in transport.calls], [45, 17, 65])
        request = transport.calls[0][0]
        self.assertEqual(request.full_url, ENDPOINT)
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("Authorization"), "Bearer sensitive-key")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertEqual(json.loads(request.data), {
            "task": "find plans", "mode": "fast", "json_format": {"plans": [{"name": ""}]},
        })

    def test_values_partial_sources_and_credits_are_not_inferred(self):
        content = {"unknown": None, "available": False, "price": 0}
        body = json.dumps({"json_content": content, "sources": ["https://example.org/a"],
                           "partial": True,
                           "key_metadata": {"credits_consumed": 0, "credits_remaining": 42}}).encode()
        transport = CaptureTransport(headers={"x-Credits-Used": "10"}, body=body)
        with patch.dict(os.environ, {"CONFIRM": "send"}):
            answer = ContextAnswers(transport=transport).answer("x", live=True)
        self.assertEqual(answer.json_content, content)
        self.assertEqual(answer.sources, ["https://example.org/a"])
        self.assertIs(answer.partial, True)
        self.assertEqual(answer.credits_consumed, 0)
        self.assertEqual(answer.credits_remaining, 42)
        self.assertEqual(answer.credits_used_header, 10)
        with patch.dict(os.environ, {"CONFIRM": "send"}):
            absent = ContextAnswers(transport=CaptureTransport()).answer("x", live=True)
            explicit_false = ContextAnswers(transport=CaptureTransport(body=b'{"json_content": {}, "sources": [], "partial": false}')).answer("x", live=True)
        self.assertIsNone(absent.partial)
        self.assertIs(explicit_false.partial, False)
        self.assertIsNone(absent.credits_consumed)
        self.assertIsNone(absent.credits_remaining)
        self.assertIsNone(absent.credits_used_header)

    def test_malformed_success_envelopes_fail_closed(self):
        bad_envelopes = (b'not json', b'[]', b'{}', b'{"json_content": null, "sources": []}',
                         b'{"json_content": {}}', b'{"json_content": {}, "sources": null}',
                         b'{"json_content": {}, "sources": [2]}',
                         b'{"json_content": {}, "sources": ["javascript:alert(1)"]}',
                         b'{"json_content": {}, "sources": ["https://user:pass@example.org/"]}',
                         b'{"json_content": {}, "sources": ["https://example.org:abc/"]}',
                         b'{"json_content": {}, "sources": ["http://[invalid/"]}',
                         b'{"json_content": {}, "sources": ["https://example.org/a b"]}',
                         b'{"json_content": {}, "sources": [], "partial": "true"}',
                         b'{"json_content": {}, "sources": [], "partial": null}',
                         b'{"json_content": {}, "sources": [], "key_metadata": []}',
                         b'{"json_content": {}, "sources": [], "key_metadata": null}',
                         b'{"json_content": {}, "sources": [], "key_metadata": {"credits_consumed": true}}',
                         b'{"json_content": {}, "sources": [], "key_metadata": {"credits_remaining": -1}}',
                         b'{"json_content": {"price": NaN}, "sources": []}',
                         b'{"json_content": {"price": 1e999}, "sources": []}')
        with patch.dict(os.environ, {"CONFIRM": "send"}):
            for body in bad_envelopes:
                with self.subTest(body=body), self.assertRaises(AnswersResponseError):
                    ContextAnswers(transport=CaptureTransport(body=body)).answer("x", live=True)
            for header in ("NaN", "-1", "1.5", "9" * 21, "١"):
                with self.subTest(header=header), self.assertRaises(AnswersResponseError):
                    ContextAnswers(transport=CaptureTransport(headers={"X-Credits-Used": header})).answer("x", live=True)
            for headers in ([], {4: "bad"}):
                with self.subTest(headers=headers), self.assertRaises(AnswersResponseError):
                    ContextAnswers(transport=CaptureTransport(headers=headers)).answer("x", live=True)
            with self.assertRaises(AnswersResponseError):
                ContextAnswers(transport=CaptureTransport(body=b"x" * (MAX_RESPONSE_BYTES + 1))).answer("x", live=True)

    def test_http_failures_and_uncertain_transport_do_not_retry_or_leak(self):
        secret = "sensitive-key"
        class FailingTransport:
            def __init__(self, outcome):
                self.outcome = outcome
                self.calls = 0

            def __call__(self, request, timeout):
                self.calls += 1
                if isinstance(self.outcome, Exception):
                    raise self.outcome
                return self.outcome, {}, (secret + " private provider body").encode()

        with patch.dict(os.environ, {"CONFIRM": "send"}):
            for outcome in (400, 408, 429, 500, 502, 504, 302, URLError(secret),
                            TimeoutError(secret)):
                with self.subTest(outcome=outcome):
                    transport = FailingTransport(outcome)
                    with self.assertRaises(AnswersError) as raised:
                        ContextAnswers(transport=transport).answer("x", live=True)
                    self.assertEqual(transport.calls, 1)
                    self.assertNotIn(secret, str(raised.exception))
                    self.assertNotIn("private provider body", str(raised.exception))

    def test_redirect_handler_never_carries_auth_to_another_host(self):
        from urllib.request import Request
        request = Request(ENDPOINT, headers={"Authorization": "Bearer sensitive-key"}, method="POST")
        self.assertIsNone(_NoRedirect().redirect_request(
            request, None, 302, "redirect", {}, "https://another.example/collect"))


if __name__ == "__main__":
    unittest.main()
