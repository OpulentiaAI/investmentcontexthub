"""Exercise urllib's real response types without external network calls."""

import io
import os
import unittest
from http.client import HTTPMessage
from unittest.mock import Mock, patch
from urllib.error import HTTPError
from urllib.request import Request

from adapters.contextdev import ContextAnswers
from adapters.contextdev import client as contextdev
from adapters.deepline import client as deepline


class ProviderHttpTransportTests(unittest.TestCase):
    def test_real_http_headers_reach_context_answer(self):
        headers = HTTPMessage()
        headers.add_header("X-Credits-Used", "10")
        response = Mock(status=200, headers=headers)
        response.read.return_value = b'{"json_content":{"price":null},"sources":[]}'
        opener = Mock()
        opener.open.return_value.__enter__ = Mock(return_value=response)
        opener.open.return_value.__exit__ = Mock(return_value=False)
        with patch.dict(os.environ, {"CONFIRM": "send", "CONTEXT_DEV_API_KEY": "test-placeholder"}):
            with patch.object(contextdev, "build_opener", return_value=opener) as build:
                answer = ContextAnswers().answer("Public pricing for example.com", live=True)
        self.assertEqual(answer.credits_used_header, 10)
        self.assertEqual(answer.json_content, {"price": None})
        response.read.assert_called_once_with(contextdev.MAX_RESPONSE_BYTES + 1)
        self.assertIsInstance(build.call_args.args[0], contextdev._NoRedirect)
        opener.open.assert_called_once()

    def test_context_http_failure_does_not_read_private_body(self):
        headers = HTTPMessage()
        headers.add_header("Retry-After", "10")
        body = io.BytesIO(b"private error details")
        error = HTTPError(contextdev.ENDPOINT, 429, "rate limited", headers, body)
        opener = Mock()
        opener.open.side_effect = error
        with patch.object(contextdev, "build_opener", return_value=opener):
            result = contextdev.urllib_transport(Request(contextdev.ENDPOINT), 10)
        self.assertEqual(result, (429, {"Retry-After": "10"}, b""))
        self.assertTrue(body.closed)
        opener.open.assert_called_once()

    def test_deepline_transport_bounds_response_read(self):
        response = Mock(status=200)
        response.read.return_value = b"{}"
        opener = Mock()
        opener.open.return_value.__enter__ = Mock(return_value=response)
        opener.open.return_value.__exit__ = Mock(return_value=False)
        with patch.object(deepline, "build_opener", return_value=opener):
            self.assertEqual(deepline.urllib_transport(Request(deepline.BASE_URL), 2), (200, b"{}"))
        response.read.assert_called_once_with(deepline.MAX_RESPONSE_BYTES + 1)
        self.assertEqual(opener.open.call_args.kwargs["timeout"], 2)


if __name__ == "__main__":
    unittest.main()
