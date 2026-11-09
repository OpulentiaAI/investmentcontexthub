import io
import json
import os
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request

from adapters.deepline import (
    DeeplineClient,
    DeeplineError,
    PreparedPlay,
    ResponseFormatError,
    RunLimitError,
    prepare_play,
)
from adapters.deepline.client import MAX_RESPONSE_BYTES, _NoRedirect, urllib_transport


RUN_ID = "play/prebuilt/example/run/20260829t123456-789-a1b2c3d4"


def package(status="running", run_id=RUN_ID, **other):
    return {"schemaVersion": 1, "kind": "play_run", "run": {"id": run_id, "status": status}, **other}


def encoded(value):
    return json.dumps(value).encode()


class Transport:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, request, timeout):
        self.calls.append((request, timeout))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class Clock:
    def __init__(self):
        self.time = 0.0
        self.sleeps = []

    def __call__(self):
        return self.time

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.time += seconds


class DeeplineTests(unittest.TestCase):
    def client(self, transport, **kwargs):
        return DeeplineClient(api_key="test-placeholder", transport=transport, **kwargs)

    def test_prepare_is_offline_and_matches_play_envelope(self):
        with patch.dict(os.environ, {"DEEPLINE_API_KEY": "", "CONFIRM": ""}):
            prepared = prepare_play("prebuilt/example", {"nested": [1, True, None]})
        self.assertEqual(prepared.name, "prebuilt/example")
        self.assertEqual(json.loads(prepared.body), {"name": "prebuilt/example", "input": {"nested": [1, True, None]}})

    def test_metadata_request_is_read_only_and_path_encoded(self):
        transport = Transport((200, encoded({"inputSchema": {"type": "object"}, "pricing": {"unit": "request"}})))
        metadata = self.client(transport).inspect_tool("group/id?x=1")
        self.assertEqual(metadata["pricing"], {"unit": "request"})
        request, timeout = transport.calls[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(request.full_url, "https://code.deepline.com/api/v2/integrations/group%2Fid%3Fx%3D1/get")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-placeholder")
        self.assertEqual(timeout, 10.0)

    def test_metadata_requires_schema(self):
        transport = Transport((200, encoded({"name": "example"})))
        with self.assertRaises(ResponseFormatError):
            self.client(transport).inspect_tool("example")

    def test_paid_play_requires_both_current_guards_and_posts_once(self):
        prepared = prepare_play("prebuilt/example", {"row": 1})
        transport = Transport((200, encoded(package())))
        client = self.client(transport)
        with patch.dict(os.environ, {"CONFIRM": "send"}):
            with self.assertRaises(DeeplineError):
                client.run_play(prepared)
        with patch.dict(os.environ, {"CONFIRM": ""}):
            with self.assertRaises(DeeplineError):
                client.run_play(prepared, live=True)
        self.assertEqual(transport.calls, [])
        with patch.dict(os.environ, {"CONFIRM": "send"}):
            result = client.run_play(prepared, live=True)
        self.assertEqual(result["run"]["id"], RUN_ID)
        self.assertEqual(len(transport.calls), 1)
        request, _ = transport.calls[0]
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.full_url, "https://code.deepline.com/api/v2/plays/run")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertEqual(json.loads(request.data), {"name": "prebuilt/example", "input": {"row": 1}})

    def test_tampered_prepared_request_never_posts(self):
        transport = Transport()
        with patch.dict(os.environ, {"CONFIRM": "send"}):
            for body in (b'{"name":"other","input":{}}', b'{"name":"prebuilt/example","input":{},"extra":1}', b"invalid"):
                with self.subTest(body=body), self.assertRaises(ValueError):
                    self.client(transport).run_play(PreparedPlay("prebuilt/example", body), live=True)
        self.assertEqual(transport.calls, [])

    def test_ambiguous_paid_post_is_never_retried(self):
        prepared = prepare_play("prebuilt/example", {"row": 1})
        for failure in (TimeoutError("secret-provider-detail"), (503, b"secret-provider-detail")):
            with self.subTest(failure=failure):
                transport = Transport(failure)
                with patch.dict(os.environ, {"CONFIRM": "send"}):
                    with self.assertRaises(DeeplineError) as caught:
                        self.client(transport).run_play(prepared, live=True)
                self.assertEqual(len(transport.calls), 1)
                self.assertNotIn("secret-provider-detail", str(caught.exception))

    def test_get_encodes_entire_id_and_retains_package(self):
        run_id = "play/a?x=1#frag%2F/run"
        result = package("completed", run_id, outputs={"unreviewed": [1, 2]})
        transport = Transport((200, encoded(result)))
        self.assertEqual(self.client(transport).get_run(run_id), result)
        request, _ = transport.calls[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(request.full_url, "https://code.deepline.com/api/v2/runs/play%2Fa%3Fx%3D1%23frag%252F%2Frun?full=true")

    def test_legacy_and_malformed_packages_fail_closed(self):
        invalid = [
            {"workflowId": RUN_ID, "status": "completed"},
            {"schemaVersion": 2, "kind": "play_run", "run": {"id": RUN_ID, "status": "completed"}},
            package("mystery"),
            package("completed", "different"),
            {"schemaVersion": True, "kind": "play_run", "run": {"id": RUN_ID, "status": "completed"}},
            {"schemaVersion": 1, "kind": "play_run", "run": {"id": RUN_ID, "status": None}},
        ]
        for item in invalid:
            with self.subTest(item=item):
                with self.assertRaises(ResponseFormatError):
                    self.client(Transport((200, encoded(item)))).get_run(RUN_ID)

    def test_terminal_statuses_return_without_claiming_usable_output(self):
        for status in ("completed", "failed", "cancelled"):
            with self.subTest(status=status):
                transport = Transport((200, encoded(package(status))))
                self.assertEqual(self.client(transport).poll_run(RUN_ID, max_polls=3)["run"]["status"], status)
                self.assertEqual(len(transport.calls), 1)

    def test_waiting_is_nonterminal_and_poll_count_caps_calls(self):
        transport = Transport(*[(200, encoded(package(status))) for status in ("queued", "running", "waiting")])
        clock = Clock()
        with self.assertRaises(RunLimitError):
            self.client(transport, clock=clock, sleep=clock.sleep).poll_run(RUN_ID, max_polls=3)
        self.assertEqual(len(transport.calls), 3)
        self.assertEqual(clock.sleeps, [1.0, 1.0])

    def test_poll_deadline_caps_sleep_and_request_timeout(self):
        transport = Transport((200, encoded(package("waiting"))), (200, encoded(package("completed"))))
        clock = Clock()
        client = self.client(transport, clock=clock, sleep=clock.sleep, timeout_seconds=10)
        with self.assertRaises(RunLimitError):
            client.poll_run(RUN_ID, max_polls=5, deadline_seconds=0.25)
        self.assertEqual(len(transport.calls), 1)
        self.assertEqual(transport.calls[0][1], 0.25)
        self.assertEqual(clock.sleeps, [0.25])

    def test_elapsed_request_deadline_discards_even_terminal_package(self):
        clock = Clock()

        def transport(request, timeout):
            clock.time += timeout
            return 200, encoded(package("completed"))

        with self.assertRaises(RunLimitError):
            self.client(transport, clock=clock, sleep=clock.sleep).poll_run(RUN_ID, deadline_seconds=0.5)

    def test_bad_inputs_fail_before_transport(self):
        transport = Transport()
        client = self.client(transport)
        for value in ("", "a\r\nAuthorization: token", " spaced ", 42):
            with self.subTest(value=value), self.assertRaises(ValueError):
                client.get_run(value)
        for kwargs in ({"max_polls": 0}, {"max_polls": 21}, {"deadline_seconds": 121}, {"deadline_seconds": float("nan")}, {"interval_seconds": -1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                client.poll_run(RUN_ID, **kwargs)
        for name, input in (("", {}), ("name", []), ("name", {"x": float("nan")}), ("name", {"x": object()}), ("name", {"x": "z" * (1024 * 1024)})):
            with self.subTest(name=name, input_type=type(input)), self.assertRaises(ValueError):
                prepare_play(name, input)
        self.assertEqual(transport.calls, [])

    def test_missing_key_never_contacts_transport(self):
        transport = Transport()
        with patch.dict(os.environ, {"DEEPLINE_API_KEY": ""}):
            with self.assertRaises(DeeplineError):
                DeeplineClient(transport=transport).get_run(RUN_ID)
        self.assertEqual(transport.calls, [])

    def test_provider_and_transport_failures_redact_secrets_and_body(self):
        secret = "private-test-key"
        body = b"provider-secret-body"
        for response in ((401, body), (302, body), (500, body), RuntimeError("private-transport-secret")):
            with self.subTest(response=response):
                transport = Transport(response)
                with self.assertRaises(DeeplineError) as caught:
                    DeeplineClient(api_key=secret, transport=transport).get_run(RUN_ID)
                self.assertNotIn(secret, str(caught.exception))
                self.assertNotIn(body.decode(), str(caught.exception))
                self.assertNotIn("private-transport-secret", str(caught.exception))
                self.assertEqual(len(transport.calls), 1)

    def test_response_limits_and_invalid_json(self):
        for response in (b"not JSON", b"[]", b"{" + b" " * MAX_RESPONSE_BYTES + b"}", b"{\"x\": NaN}"):
            with self.subTest(size=len(response)):
                with self.assertRaises(ResponseFormatError):
                    self.client(Transport((200, response))).get_run(RUN_ID)

    def test_urllib_transport_disallows_redirect_following(self):
        self.assertIsNone(_NoRedirect().redirect_request(Request("https://code.deepline.com/"), None, 302, "redirect", {}, "https://other.example/"))
        error = HTTPError("https://code.deepline.com/", 302, "redirect", {}, io.BytesIO(b"private-body"))
        opener = unittest.mock.Mock()
        opener.open.side_effect = error
        with patch("adapters.deepline.client.build_opener", return_value=opener) as build:
            status, body = urllib_transport(Request("https://code.deepline.com/"), 1)
        self.assertEqual((status, body), (302, b""))
        self.assertEqual(build.call_args.args[0], _NoRedirect)


if __name__ == "__main__":
    unittest.main()
